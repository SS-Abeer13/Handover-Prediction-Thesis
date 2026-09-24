"""Turn the processed tables into model-ready arrays and datasets.

This is the single place where features, labels, masks, splits and windows meet,
so the leakage-safety rules live here and nowhere else:

* the transform is fitted on TRAIN rows only and then applied everywhere;
* degenerate-feature pruning is a TRAIN-only decision;
* QoE thresholds arrive pre-fitted from TRAIN rows;
* window construction never reaches across a drive boundary.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from ..config import Config
from ..data.features import select_blocks
from ..data.labels import horizon_tags
from ..data.splits import Split, row_masks
from ..data.transforms import TabularTransform, drop_degenerate
from ..data.windows import WindowIndex, build_window_index, materialise
from ..models.dataset import SequenceDataset
from ..utils import get_logger

LOG = get_logger("hoproj.assemble")


@dataclass
class Assembled:
    feature_names: list[str]
    transform: TabularTransform
    X: np.ndarray                       # (n_rows, F) scaled
    frame: pd.DataFrame                 # meta rows aligned with X
    Y_ho: np.ndarray                    # (n_rows, H)
    M_ho: np.ndarray
    Y_qoe: np.ndarray | None
    M_qoe: np.ndarray | None
    y_dwell: np.ndarray | None
    m_dwell: np.ndarray | None
    cand: np.ndarray | None             # (n_rows, K, C)
    cand_mask: np.ndarray | None
    y_target: np.ndarray | None
    horizons: list[float]
    row_masks: dict[str, np.ndarray]
    windows: dict[str, WindowIndex]
    window_tensors: dict[str, np.ndarray]

    @property
    def n_features(self) -> int:
        return self.X.shape[1]

    @property
    def d_cand(self) -> int:
        return 0 if self.cand is None else self.cand.shape[2]


def _candidate_tensor(features: pd.DataFrame, k: int) -> tuple[np.ndarray, np.ndarray, list[str]]:
    """(N, K, C) per-candidate attributes, all transferable (no cell identity)."""
    templates = ["nbr{i}_rsrp", "gap_serving_nbr{i}", "gap_serving_nbr{i}_d1"]
    extra = [c for c in features.columns if c.startswith("gap_serving_nbr") and "_mean" in c]
    by_slot: list[list[np.ndarray]] = []
    names: list[str] = []
    for i in range(1, k + 1):
        cols = [t.format(i=i) for t in templates]
        cols += [c for c in extra if c.startswith(f"gap_serving_nbr{i}_mean")]
        present = [c for c in cols if c in features.columns]
        if not present:
            return np.empty((len(features), 0, 0)), np.empty((len(features), 0)), []
        vals = [features[c].to_numpy(float) for c in present]
        vals.append(np.full(len(features), float(i)))                  # slot rank
        vals.append((np.asarray(vals[0]) == np.nanmax(
            np.column_stack([features[f"nbr{j}_rsrp"].to_numpy(float)
                             for j in range(1, k + 1) if f"nbr{j}_rsrp" in features]), axis=1)
        ).astype(float))                                               # is strongest candidate
        by_slot.append(vals)
        if not names:
            names = present + ["slot_rank", "is_best_candidate"]
    C = min(len(v) for v in by_slot)
    cand = np.stack([np.column_stack([np.nan_to_num(v, nan=0.0) for v in slot[:C]])
                     for slot in by_slot], axis=1)
    mask = np.isfinite(np.stack([features[f"nbr{i}_rsrp"].to_numpy(float)
                                 for i in range(1, k + 1)], axis=1))
    return cand.astype(np.float32), mask.astype(np.float32), names[:C]


def _scale_candidates(cand: np.ndarray, train_rows: np.ndarray) -> np.ndarray:
    if cand.size == 0:
        return cand
    flat = cand[train_rows].reshape(-1, cand.shape[2])
    med = np.nanmedian(flat, axis=0)
    q75, q25 = np.nanpercentile(flat, [75, 25], axis=0)
    scale = np.where((q75 - q25) < 1e-9, 1.0, (q75 - q25) / 1.349)
    return np.clip((cand - med) / scale, -8, 8).astype(np.float32)


def assemble(features: pd.DataFrame, labels: pd.DataFrame, cfg: Config, split: Split,
             cache_dir: Path | None = None) -> Assembled:
    from ..data.labels import usable_horizons
    horizons = usable_horizons(cfg)
    tags = horizon_tags(cfg)
    k = int(cfg.get_path("features.neighbour_k", 3))
    blocks = list(cfg.get_path("features.blocks", ["rf", "mobility", "history", "qoe"]))
    if cfg.get_path("features.regime") == "context_rich":
        blocks.append("context")

    frame = features.reset_index(drop=True)
    lab = labels.reset_index(drop=True)
    assert len(frame) == len(lab), "features and labels are not row-aligned"

    masks = row_masks(frame, split, cfg)
    names = select_blocks(frame, blocks)
    names = drop_degenerate(frame[names], masks["train"])

    transform = TabularTransform(cfg.get_path("features.scaler", "robust"),
                                 cfg.get_path("features.impute", "median"),
                                 float(cfg.get_path("features.clip_sigma", 8.0)))
    transform.fit(frame.loc[masks["train"], names])
    X = transform.transform(frame[names])

    Y_ho = np.column_stack([lab[f"y_ho_{t}"].to_numpy(np.float32) for t in tags])
    M_ho = np.column_stack([lab[f"m_ho_{t}"].to_numpy(np.float32) for t in tags])
    Y_qoe = M_qoe = None
    if all(f"y_qoe_{t}" in lab for t in tags) and cfg.get_path("tasks.qoe.enabled", False):
        Y_qoe = np.column_stack([lab[f"y_qoe_{t}"].to_numpy(np.float32) for t in tags])
        M_qoe = np.column_stack([lab[f"m_qoe_{t}"].to_numpy(np.float32) for t in tags])
    y_dwell = m_dwell = None
    if cfg.get_path("tasks.dwell.enabled", False) and "y_dwell_log" in lab:
        y_dwell = lab["y_dwell_log"].to_numpy(np.float32)
        m_dwell = lab["m_dwell"].to_numpy(np.float32)
    cand = cand_mask = y_target = None
    if cfg.get_path("tasks.target.enabled", False):
        cand, cand_mask, cand_names = _candidate_tensor(frame, k)
        if cand.size:
            cand = _scale_candidates(cand, masks["train"])
            y_target = lab["y_target_cand"].to_numpy(np.int64)
            LOG.info("candidate tensor %s from %s", cand.shape, cand_names)
        else:
            cand = cand_mask = None

    interp = frame["is_interpolated"].to_numpy(bool) if "is_interpolated" in frame else None
    period = float(cfg.get_path("data.target_period_s") or 1.0)
    L = max(2, int(round(float(cfg.get_path("windows.length_s", 10.0)) / period)))
    stride = max(1, int(round(float(cfg.get_path("windows.stride_s", 1.0)) / period)))
    # One causal window index over the whole frame; windows never cross a drive
    # boundary, so selecting by the partition of the END row is exact for the
    # grouped conditions and is the intended behaviour for the random-row control.
    wi_all = build_window_index(frame, L, stride,
                                float(cfg.get_path("windows.min_valid_frac", 0.7)), interp)
    windows, tensors = {}, {}
    for part in ("train", "val", "calib", "test"):
        keep = masks[part][wi_all.end_pos]
        wi = WindowIndex(wi_all.end_pos[keep], wi_all.start_pos[keep],
                         wi_all.drive_id[keep], wi_all.route_id[keep], L,
                         wi_all.valid_frac[keep])
        windows[part] = wi
        cache = (cache_dir / f"windows_{split.name}_{part}.npy") if cache_dir else None
        tensors[part] = (materialise(X, wi, cache) if len(wi)
                         else np.empty((0, L, X.shape[1]), dtype=np.float32))
        LOG.info("part=%-6s rows=%6d windows=%6d drives=%3d", part, int(masks[part].sum()),
                 len(wi), len(set(wi.drive_id.tolist())))
    return Assembled(names, transform, X, frame, Y_ho, M_ho, Y_qoe, M_qoe,
                     y_dwell, m_dwell, cand, cand_mask, y_target, horizons,
                     masks, windows, tensors)


def make_dataset(a: Assembled, part: str, tasks: dict | None = None) -> SequenceDataset:
    wi = a.windows[part]
    pos = wi.end_pos
    tasks = tasks or {}
    kw = {}
    if tasks.get("handover", {}).get("enabled", True):
        kw["y_ho"], kw["m_ho"] = a.Y_ho[pos], a.M_ho[pos]
    if a.Y_qoe is not None and tasks.get("qoe", {}).get("enabled", False):
        kw["y_qoe"], kw["m_qoe"] = a.Y_qoe[pos], a.M_qoe[pos]
    if a.y_dwell is not None and tasks.get("dwell", {}).get("enabled", False):
        kw["y_dwell"], kw["m_dwell"] = a.y_dwell[pos], a.m_dwell[pos]
    if a.cand is not None and tasks.get("target", {}).get("enabled", False):
        kw["cand"], kw["cand_mask"], kw["y_target"] = a.cand[pos], a.cand_mask[pos], a.y_target[pos]
    return SequenceDataset(a.window_tensors[part], **kw)


def snapshot_matrix(a: Assembled, part: str) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Last timestep of each window - what the snapshot baselines see."""
    pos = a.windows[part].end_pos
    return a.X[pos], a.Y_ho[pos], a.M_ho[pos]


def window_meta(a: Assembled, part: str) -> pd.DataFrame:
    pos = a.windows[part].end_pos
    cols = [c for c in ("t", "drive_id", "route_id", "direction", "dist_in_drive_m",
                        "serving_cell_name", "serving_pci", "lat", "lon") if c in a.frame]
    return a.frame.loc[pos, cols].reset_index(drop=True)

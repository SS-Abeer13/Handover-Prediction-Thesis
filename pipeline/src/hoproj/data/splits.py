"""Stage R12 - grouped partitioning.

Three evaluation *conditions* are produced from the same data, which is what
makes the leakage study (section 25) an experiment rather than an assertion:

``random_row``     rows shuffled without regard to drive - the conventional, and
                   optimistic, protocol.  Retained ONLY as a leakage control.
``grouped_drive``  whole drives assigned to train / val / calib / test.
``external_route`` the locked route is the test set; no sample, statistic,
                   hyper-parameter or threshold from it is ever seen earlier.

The development domain is further split into train / val / calib.  ``calib`` is
held back from gradient descent *and* from model selection, and is used only for
temperature scaling, conformal calibration and abstention thresholds.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict

import numpy as np
import pandas as pd

from ..config import Config
from ..utils import get_logger

LOG = get_logger("hoproj.splits")

DEV_PARTS = ("train", "val", "calib", "test")


@dataclass
class Split:
    name: str
    condition: str
    train: list[str]
    val: list[str]
    calib: list[str]
    test: list[str]
    note: str = ""

    def as_dict(self) -> dict:
        return asdict(self)


def _stratified_group_assign(drives: pd.DataFrame, fractions: dict, stratify_on: list[str],
                             rng: np.random.Generator) -> dict[str, list[str]]:
    """Assign whole drives to train/val/calib, balancing strata."""
    out = {k: [] for k in DEV_PARTS}
    keys = [c for c in stratify_on if c in drives.columns] or [drives.columns[0]]
    for _, grp in drives.groupby(keys, dropna=False):
        ids = grp["drive_id"].tolist()
        rng.shuffle(ids)
        n = len(ids)
        n_val = max(1, int(round(fractions.get("val", 0.15) * n))) if n >= 3 else 0
        n_cal = max(1, int(round(fractions.get("calib", 0.15) * n))) if n >= 4 else 0
        n_tst = max(1, int(round(fractions.get("test", 0.15) * n))) if n >= 5 else 0
        out["val"] += ids[:n_val]
        out["calib"] += ids[n_val:n_val + n_cal]
        out["test"] += ids[n_val + n_cal:n_val + n_cal + n_tst]
        out["train"] += ids[n_val + n_cal + n_tst:]
    return out


def make_splits(drives: pd.DataFrame, cfg: Config) -> dict[str, Split]:
    rng = np.random.default_rng(int(cfg.get_path("project.seed", 0)))
    external = cfg.get_path("splits.external_route")
    fractions = cfg.get_path("splits.dev_fractions", {"train": 0.65, "val": 0.175, "calib": 0.175})
    stratify = cfg.get_path("splits.stratify_on", ["route_id", "direction"])

    dev = drives[drives["route_id"] != external].copy()
    ext = drives[drives["route_id"] == external].copy()
    if external and ext.empty:
        LOG.warning("external_route %r matches no drive; external condition will be empty", external)

    parts = _stratified_group_assign(dev, fractions, stratify, rng)
    splits: dict[str, Split] = {}

    splits["grouped_drive"] = Split(
        name="grouped_drive", condition="grouped_drive",
        train=parts["train"], val=parts["val"], calib=parts["calib"], test=parts["test"],
        note="Condition B: complete-drive separation inside the development domain; "
             "the test drives are disjoint from the drives used for early stopping.",
    )
    splits["external_route"] = Split(
        name="external_route", condition="external_route",
        train=parts["train"], val=parts["val"], calib=parts["calib"],
        test=ext["drive_id"].tolist(),
        note=f"Condition C: locked external route {external!r}, used only at R15.",
    )
    splits["random_row"] = Split(
        name="random_row", condition="random_row",
        train=dev["drive_id"].tolist(), val=dev["drive_id"].tolist(),
        calib=dev["drive_id"].tolist(), test=dev["drive_id"].tolist(),
        note="Condition A: rows are shuffled at sample level; LEAKAGE CONTROL ONLY.",
    )
    for s in splits.values():
        LOG.info("split %-15s train=%d val=%d calib=%d test=%d drives",
                 s.name, len(s.train), len(s.val), len(s.calib), len(s.test))
    return splits


def row_masks(frame: pd.DataFrame, split: Split, cfg: Config,
              seed: int | None = None) -> dict[str, np.ndarray]:
    """Boolean row masks for a split, honouring the random-row condition."""
    drive = frame["drive_id"].to_numpy()
    if split.condition == "random_row":
        rng = np.random.default_rng(seed if seed is not None else int(cfg.get_path("project.seed", 0)))
        pool = np.isin(drive, np.asarray(split.train, dtype=object))
        idx = np.flatnonzero(pool)
        rng.shuffle(idx)
        fr = cfg.get_path("splits.dev_fractions", {})
        n = len(idx)
        n_val = int(round(fr.get("val", 0.15) * n))
        n_cal = int(round(fr.get("calib", 0.15) * n))
        n_tst = int(round(fr.get("test", 0.15) * n))
        masks = {k: np.zeros(len(frame), dtype=bool) for k in ("train", "val", "calib", "test")}
        masks["val"][idx[:n_val]] = True
        masks["calib"][idx[n_val:n_val + n_cal]] = True
        masks["test"][idx[n_val + n_cal:n_val + n_cal + n_tst]] = True
        masks["train"][idx[n_val + n_cal + n_tst:]] = True
        return masks
    return {part: np.isin(drive, np.asarray(getattr(split, part), dtype=object))
            for part in ("train", "val", "calib", "test")}


def grouped_folds(drives: list[str], n_folds: int, seed: int = 0) -> list[tuple[list[str], list[str]]]:
    """GroupKFold over drive ids, for hyper-parameter search inside the dev domain."""
    rng = np.random.default_rng(seed)
    ids = np.array(sorted(drives), dtype=object)
    rng.shuffle(ids)
    folds = np.array_split(ids, max(2, n_folds))
    out = []
    for i in range(len(folds)):
        va = list(folds[i])
        tr = [d for j, f in enumerate(folds) if j != i for d in f]
        out.append((tr, va))
    return out

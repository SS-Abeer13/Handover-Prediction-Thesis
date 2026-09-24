"""One (model, condition, regime, feature-set) training+evaluation run."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score

from ..config import Config
from ..data.splits import Split
from ..eval import events as EV
from ..eval import metrics as MET
from ..eval import stats as ST
from ..models.registry import build_model, model_kind
from ..utils import get_logger, set_seed
from .assemble import Assembled, assemble, make_dataset, snapshot_matrix, window_meta

LOG = get_logger("hoproj.trainer")


def mean_auprc(Y: np.ndarray, P: np.ndarray, M: np.ndarray) -> float:
    vals = []
    for j in range(Y.shape[1]):
        sel = M[:, j].astype(bool)
        y = Y[sel, j]
        if sel.sum() < 10 or len(np.unique(y)) < 2:
            continue
        vals.append(average_precision_score(y, P[sel, j]))
    return float(np.mean(vals)) if vals else float("nan")


@dataclass
class RunResult:
    model: str
    condition: str
    regime: str
    feature_set: str
    variant: str
    seed: int
    horizon_table: pd.DataFrame
    event_table: pd.DataFrame
    predictions: dict[str, np.ndarray]      # part -> (N, H)
    meta: dict[str, pd.DataFrame]
    footprint: dict = field(default_factory=dict)
    history: dict = field(default_factory=dict)
    extras: dict = field(default_factory=dict)


def train_and_evaluate(cfg: Config, features: pd.DataFrame, labels: pd.DataFrame,
                       ho: pd.DataFrame, split: Split, model_name: str,
                       feature_set: str = "default", variant: str = "base",
                       seed: int | None = None, cache_dir: Path | None = None,
                       assembled: Assembled | None = None,
                       return_model: bool = False) -> RunResult:
    seed = int(cfg.get_path("project.seed", 0)) if seed is None else int(seed)
    set_seed(seed)
    a = assembled or assemble(features, labels, cfg, split, cache_dir)
    kind = model_kind(model_name)
    tasks = cfg.get_path("tasks", {})
    horizons = a.horizons

    preds: dict[str, np.ndarray] = {}
    metas: dict[str, pd.DataFrame] = {}
    footprint, history, extras = {}, {}, {}
    model = None

    if kind in ("rule", "snapshot"):
        Xtr, Ytr, Mtr = snapshot_matrix(a, "train")
        model = build_model(model_name, cfg, a.n_features, len(horizons), seed=seed)
        if kind == "rule":
            frame_tr = a.frame.loc[a.windows["train"].end_pos, a.feature_names]
            model.fit(frame_tr)
            for part in ("train", "val", "calib", "test"):
                pos = a.windows[part].end_pos
                if len(pos) == 0:
                    continue
                preds[part] = model.predict_proba(
                    a.frame.loc[pos, a.feature_names], n_outputs=len(horizons))
        else:
            model.fit(Xtr, Ytr, masks=Mtr)
            for part in ("train", "val", "calib", "test"):
                Xp, _, _ = snapshot_matrix(a, part)
                if len(Xp) == 0:
                    continue
                preds[part] = model.predict_proba(Xp)
            footprint = {"n_parameters": getattr(model, "n_params", 0)}
    else:
        ds = {p: make_dataset(a, p, tasks) for p in ("train", "val", "calib", "test")}
        model = build_model(model_name, cfg, a.n_features, len(horizons),
                            d_cand=a.d_cand, seed=seed)
        model.fit(ds["train"], ds["val"] if len(ds["val"]) else None, metric_fn=mean_auprc)
        history = {k: v for k, v in model.history.__dict__.items()}
        want = ["handover"]
        if a.Y_qoe is not None and tasks.get("qoe", {}).get("enabled"):
            want.append("qoe")
        if a.cand is not None and tasks.get("target", {}).get("enabled"):
            want.append("target")
        if a.y_dwell is not None and tasks.get("dwell", {}).get("enabled"):
            want.append("dwell")
        for part in ("train", "val", "calib", "test"):
            if len(ds[part]) == 0:
                continue
            out = model.predict(ds[part], want=tuple(want) + ("z",))
            preds[part] = out["handover"]
            for extra_key in ("qoe", "target", "dwell", "z"):
                if extra_key in out:
                    extras.setdefault(extra_key, {})[part] = out[extra_key]
        from ..deploy.profile import model_footprint
        footprint = model_footprint(model.model)

    for part in preds:
        metas[part] = window_meta(a, part)

    # ------------------------------------------------------------- metric tables
    pos_test = a.windows["test"].end_pos
    Y, M = a.Y_ho[pos_test], a.M_ho[pos_test]
    P = preds.get("test", np.zeros_like(Y))
    horizon_table = MET.multi_horizon_table(Y, P, M, horizons,
                                            tuple(cfg.get_path("eval.fixed_fpr", [0.01, 0.05, 0.1])))
    horizon_table.insert(0, "model", model_name)
    horizon_table.insert(1, "condition", split.condition)
    horizon_table.insert(2, "regime", cfg.get_path("features.regime"))
    horizon_table.insert(3, "feature_set", feature_set)
    horizon_table.insert(4, "variant", variant)

    # drive-level bootstrap CI on the primary metric
    groups = metas.get("test", pd.DataFrame()).get("drive_id")
    if groups is not None and len(groups):
        boot_rows = []
        for j, h in enumerate(horizons):
            sel = M[:, j].astype(bool)
            if sel.sum() < 50 or len(np.unique(Y[sel, j])) < 2:
                continue
            res = ST.drive_bootstrap(
                lambda yy, pp: average_precision_score(yy, pp) if len(np.unique(yy)) > 1 else np.nan,
                Y[sel, j], P[sel, j], groups.to_numpy()[sel],
                n=int(cfg.get_path("eval.bootstrap.n", 1000)),
                ci=float(cfg.get_path("eval.bootstrap.ci", 0.95)),
                seed=seed)
            boot_rows.append({"horizon_s": h, **{f"auprc_{k}": v for k, v in res.items()}})
        if boot_rows:
            horizon_table = horizon_table.merge(pd.DataFrame(boot_rows), on="horizon_s", how="left")

    # ------------------------------------------------------- event-level metrics
    op_fpr = float(cfg.get_path("eval.event.operating_fpr", 0.05))
    thresholds = []
    pos_val = a.windows["val"].end_pos
    Yv, Mv = a.Y_ho[pos_val], a.M_ho[pos_val]
    Pv = preds.get("val")
    for j in range(len(horizons)):
        thr = 0.5
        if Pv is not None and len(Pv):
            sel = Mv[:, j].astype(bool)
            if sel.sum() > 50 and len(np.unique(Yv[sel, j])) > 1:
                _, thr = MET.recall_at_fpr(Yv[sel, j], Pv[sel, j], op_fpr)
        thresholds.append(float(thr) if np.isfinite(thr) else 0.5)

    event_table = pd.DataFrame()
    if "test" in metas and len(metas["test"]):
        event_table = EV.detection_by_horizon(
            metas["test"], P, M, ho, horizons, thresholds,
            warn_horizon_s=float(cfg.get_path("eval.event.warn_horizon_s", 5.0)))
        if len(event_table):
            event_table.insert(0, "model", model_name)
            event_table.insert(1, "condition", split.condition)
            event_table.insert(2, "regime", cfg.get_path("features.regime"))
            event_table.insert(3, "feature_set", feature_set)
            event_table.insert(4, "variant", variant)

    extras["operating_thresholds"] = thresholds
    # Out-of-fold pooling (stage13) needs the test targets and masks that go
    # with `predictions["test"]`; recomputing them outside means re-deriving the
    # window index, which is where the earlier drive-id collision crept in.
    extras["Y_test"], extras["M_test"] = Y, M
    extras["assembled"] = a if return_model else None
    extras["model"] = model if return_model else None
    return RunResult(model_name, split.condition, cfg.get_path("features.regime"),
                     feature_set, variant, seed, horizon_table, event_table, preds,
                     metas, footprint, history, extras)

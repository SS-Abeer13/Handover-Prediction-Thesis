"""Stage 13 - the benchmark, rerun on the pooled XCAL signalling dataset.

This replaces stage02's single train/val/calib/test partition with grouped
K-fold cross-validation over every drive in the pooled capture. Three reasons:

1. A single 15% test partition of 43 drives leaves 6 drives, and a drive-level
   bootstrap over 6 groups produces confidence intervals that are wide for the
   wrong reason. Rotating the folds puts every drive in the test set exactly
   once, so the pooled out-of-fold predictions are evaluated over all 43.
2. Repeating the whole rotation over several seeds turns every paired model
   comparison from a single number into a distribution. The earlier paired
   tests ran on 4 folds, where a two-sided Wilcoxon cannot return anything
   below p = 0.125 whatever the data says.
3. The leakage study needs the same protocol on both sides, or the comparison
   measures the protocol rather than the leak.

Thresholds, temperature and every scaler are fitted inside the fold. Event
metrics are computed per fold with that fold's own threshold and then pooled by
summing counts, never by averaging rates.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from ..config import Config, deep_merge, load_config, resolve_paths
from ..data.splits import Split
from ..eval import metrics as MET
from ..eval import report as RPT
from ..eval import stats as ST
from ..utils import get_logger, read_json, read_table, timed, write_json
from .stage12_xcal_prepare import HORIZONS, capture_config

LOG = get_logger("hoproj.stage13")

FEATURE_SETS = {"rf": ["rf"], "rf_mob": ["rf", "mobility"],
                "rf_mob_hist": ["rf", "mobility", "history"]}


def load_xcal(paths: dict):
    processed = paths["processed"]
    feats = read_table(processed / "features.parquet")
    meta = read_json(processed / "feature_meta.json")
    feats.attrs["feature_block"] = meta["feature_block"]
    feats.attrs["feature_names"] = meta["feature_names"]
    lab = read_table(processed / "labels.parquet")
    ho = read_table(processed / "handovers.parquet")
    drives = read_table(processed / "drives.parquet")
    for df in (feats, lab, ho):
        if "t" in df:
            df["t"] = pd.to_datetime(df["t"])
    return feats, lab, ho, drives


def make_folds(drives: pd.DataFrame, k: int, seed: int) -> list[Split]:
    """K rotations; each drive is in `test` exactly once.

    Within a rotation the remaining drives are split into train / val / calib,
    where calib is reserved for calibration and thresholds and never trained on.
    Stratification is by capture so no fold is dominated by one day.
    """
    rng = np.random.default_rng(seed)
    assign: dict[str, int] = {}
    for _, grp in drives.groupby("capture", dropna=False):
        ids = grp["drive_id"].tolist()
        rng.shuffle(ids)
        for i, d in enumerate(ids):
            assign[d] = i % k
    folds = []
    for f in range(k):
        test = [d for d, fi in assign.items() if fi == f]
        rest = [d for d, fi in assign.items() if fi != f]
        rng.shuffle(rest)
        n_val = max(1, int(round(0.18 * len(rest))))
        n_cal = max(1, int(round(0.18 * len(rest))))
        folds.append(Split(name=f"fold{f}", condition="grouped_drive",
                           val=rest[:n_val], calib=rest[n_val:n_val + n_cal],
                           train=rest[n_val + n_cal:], test=test,
                           note=f"Grouped {k}-fold rotation, fold {f}."))
    return folds


def random_row_split(drives: pd.DataFrame) -> Split:
    allids = drives["drive_id"].tolist()
    return Split(name="random_row", condition="random_row", train=allids,
                 val=allids, calib=allids, test=allids,
                 note="Rows shuffled at sample level; LEAKAGE CONTROL ONLY.")


def _pool_events(per_fold: list[pd.DataFrame]) -> pd.DataFrame:
    """Sum counts across folds, then recompute rates. Never average rates."""
    if not per_fold:
        return pd.DataFrame()
    ev = pd.concat(per_fold, ignore_index=True)
    cnt = ["n_events", "n_detected", "n_alarm_episodes", "n_false_alarm_episodes",
           "observed_hours", "observed_km"]
    cnt = [c for c in cnt if c in ev.columns]
    out = ev.groupby("horizon_s", as_index=False)[cnt].sum()
    if {"n_detected", "n_events"} <= set(out.columns):
        out["event_detection_rate"] = out["n_detected"] / out["n_events"].replace(0, np.nan)
        out["missed_event_rate"] = 1.0 - out["event_detection_rate"]
    if {"n_false_alarm_episodes", "observed_hours"} <= set(out.columns):
        out["false_alarms_per_hour"] = (out["n_false_alarm_episodes"]
                                        / out["observed_hours"].replace(0, np.nan))
    if {"n_false_alarm_episodes", "observed_km"} <= set(out.columns):
        out["false_alarms_per_km"] = (out["n_false_alarm_episodes"]
                                      / out["observed_km"].replace(0, np.nan))
    if "median_lead_time_s" in ev.columns and "n_detected" in ev.columns:
        w = ev.groupby("horizon_s").apply(
            lambda g: np.average(g["median_lead_time_s"].fillna(0),
                                 weights=g["n_detected"].clip(lower=1e-9))
            if g["n_detected"].sum() > 0 else np.nan, include_groups=False)
        out = out.merge(w.rename("median_lead_time_s").reset_index(), on="horizon_s", how="left")
    return out


def run_model(cfg: Config, feats, lab, ho, folds: list[Split], model_name: str,
              feature_set: str, seed: int, cache: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Fit and evaluate one model over every fold; return pooled OOF metrics."""
    from .trainer import train_and_evaluate

    P_parts, Y_parts, M_parts, g_parts, ev_parts = [], [], [], [], []
    for split in folds:
        with timed(f"{model_name}|{feature_set}|seed{seed}|{split.name}"):
            try:
                res = train_and_evaluate(cfg, feats, lab, ho, split, model_name,
                                         feature_set=feature_set, seed=seed,
                                         cache_dir=cache)
            except Exception as exc:                       # noqa: BLE001
                LOG.exception("%s %s failed: %s", model_name, split.name, exc)
                continue
        meta = res.meta.get("test")
        if meta is None or not len(meta):
            continue
        pos = meta.index.to_numpy() if "row" not in meta else meta["row"].to_numpy()
        P_parts.append(res.predictions["test"])
        Y_parts.append(res.extras["Y_test"])
        M_parts.append(res.extras["M_test"])
        g_parts.append(meta["drive_id"].to_numpy())
        if len(res.event_table):
            ev_parts.append(res.event_table)

    if not P_parts:
        return pd.DataFrame(), pd.DataFrame()

    P = np.vstack(P_parts)
    Y = np.vstack(Y_parts)
    M = np.vstack(M_parts)
    groups = np.concatenate(g_parts)
    horizons = cfg.get_path("labels.horizons_s")

    tbl = MET.multi_horizon_table(Y, P, M, horizons,
                                  tuple(cfg.get_path("eval.fixed_fpr", [0.01, 0.05, 0.1])))
    boot_rows = []
    from sklearn.metrics import average_precision_score
    for j, h in enumerate(horizons):
        sel = M[:, j].astype(bool)
        if sel.sum() < 50 or len(np.unique(Y[sel, j])) < 2:
            continue
        r = ST.drive_bootstrap(
            lambda yy, pp: average_precision_score(yy, pp) if len(np.unique(yy)) > 1 else np.nan,
            Y[sel, j], P[sel, j], groups[sel],
            n=int(cfg.get_path("eval.bootstrap.n", 400)), seed=seed)
        boot_rows.append({"horizon_s": h, "auprc_ci_low": r["ci_low"],
                          "auprc_ci_high": r["ci_high"], "n_drives": r["n_groups"]})
    if boot_rows:
        tbl = tbl.merge(pd.DataFrame(boot_rows), on="horizon_s", how="left")
    tbl.insert(0, "model", model_name)
    tbl.insert(1, "feature_set", feature_set)
    tbl.insert(2, "seed", seed)
    tbl.insert(3, "condition", folds[0].condition)

    ev = _pool_events(ev_parts)
    if len(ev):
        ev.insert(0, "model", model_name)
        ev.insert(1, "feature_set", feature_set)
        ev.insert(2, "seed", seed)
        ev.insert(3, "condition", folds[0].condition)
    return tbl, ev


def main(argv=None):
    ap = argparse.ArgumentParser(description="Stage 13: XCAL benchmark, grouped K-fold")
    ap.add_argument("--root", default=None)
    ap.add_argument("--models", nargs="*",
                    default=["rule", "logreg", "lgbm", "mlp", "gru", "tcn", "transformer"])
    ap.add_argument("--feature-sets", nargs="*", default=["rf_mob_hist"])
    ap.add_argument("--seeds", nargs="*", type=int, default=[1337])
    ap.add_argument("--folds", type=int, default=5)
    ap.add_argument("--epochs", type=int, default=40)
    ap.add_argument("--leakage", action="store_true",
                    help="also run the random-row leakage control")
    ap.add_argument("--tag", default="xcal_main")
    a = ap.parse_args(argv)

    cfg = capture_config("x", "y", HORIZONS)
    cfg = Config(deep_merge(cfg, {
        "project": {"paths": {"processed": "data/processed_xcal",
                              "interim": "data/interim_xcal",
                              "reports": "reports_xcal",
                              "artifacts": "artifacts_xcal"}},
        "train": {"epochs": a.epochs, "early_stop_patience": 8},
        "eval": {"bootstrap": {"n": 400}},
        "tasks": {"qoe": {"enabled": False}, "target": {"enabled": False},
                  "dwell": {"enabled": False}}}))
    paths = resolve_paths(cfg, a.root)
    feats, lab, ho, drives = load_xcal(paths)
    LOG.info("pooled XCAL: %d samples, %d drives, %d handovers, %d features",
             len(feats), drives["drive_id"].nunique(), len(ho),
             len(feats.attrs["feature_names"]))

    cache = paths["interim"] / "window_cache"
    res_rows, ev_rows = [], []
    for seed in a.seeds:
        folds = make_folds(drives, a.folds, seed)
        LOG.info("seed %d: fold test sizes %s", seed, [len(f.test) for f in folds])
        for fs in a.feature_sets:
            run_cfg = Config(deep_merge(cfg, {"features": {"blocks": FEATURE_SETS[fs]}}))
            for model_name in a.models:
                tbl, ev = run_model(run_cfg, feats, lab, ho, folds, model_name, fs, seed, cache)
                if len(tbl):
                    res_rows.append(tbl)
                if len(ev):
                    ev_rows.append(ev)
        if a.leakage:
            rr = [random_row_split(drives)]
            for fs in a.feature_sets:
                run_cfg = Config(deep_merge(cfg, {"features": {"blocks": FEATURE_SETS[fs]}}))
                for model_name in a.models:
                    tbl, ev = run_model(run_cfg, feats, lab, ho, rr, model_name, fs, seed, cache)
                    if len(tbl):
                        res_rows.append(tbl)

    if not res_rows:
        raise RuntimeError("no run completed")
    results = pd.concat(res_rows, ignore_index=True)
    RPT.save_table(results, paths["reports"], a.tag)
    if ev_rows:
        RPT.save_table(pd.concat(ev_rows, ignore_index=True), paths["reports"], f"{a.tag}_events")
    write_json({"models": a.models, "feature_sets": a.feature_sets, "seeds": a.seeds,
                "folds": a.folds, "n_drives": int(drives["drive_id"].nunique()),
                "protocol": "grouped K-fold rotation; every drive tested once; "
                            "thresholds and calibration fitted inside the fold"},
               paths["artifacts"] / f"{a.tag}.json")
    LOG.info("stage 13 complete: %d rows", len(results))
    return results


if __name__ == "__main__":
    main()

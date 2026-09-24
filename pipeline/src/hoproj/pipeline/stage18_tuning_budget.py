"""Stage 18 - equal tuning budget for every model (doc 19, item I).

The objection this answers is the standard one: *"your deep baselines are
untuned"*. In stage 13 every model ran on its coded default parameters, so a
reviewer can argue that LightGBM's margin is an artefact of the defaults
happening to suit gradient boosting.

Protocol
--------
* **Outer**: the stage-13 grouped 5-fold rotation, unchanged, so the tuned and
  default arms are compared on exactly the same test drives.
* **Inner**: ``GroupKFold(3)`` over the *training* drives of that outer fold
  only. Test drives never enter a search.
* **Budget**: the same number of Optuna trials for every model, with the same
  objective - mean AUPRC at the 2 s horizon over the three inner folds. The
  middle horizon is used so nothing is tuned to one extreme.
* Trials are pruned on the inner-fold running mean, so a hopeless trial does
  not cost three fits; every model still gets the same *number of trials*,
  which is the budget being equalised.
* The winning parameters are refit on the whole outer-train and scored once on
  the held-out outer fold. Predictions are pooled out-of-fold over all 43
  drives, exactly as in stage 13.
* The default arm is re-run here rather than copied from stage 13, so both arms
  share fold assignment, seed and code path and the delta is attributable to
  the parameters alone.

Search spaces are deliberately small: with 43 drives a wide space overfits the
inner rotation, which would understate the tuned arm rather than flatter it.
"""
from __future__ import annotations

import argparse
import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

from ..config import Config, deep_merge, resolve_paths
from ..data.splits import Split
from ..eval import metrics as MET
from ..eval import report as RPT
from ..eval import stats as ST
from ..utils import get_logger, timed, write_json
from .stage12_xcal_prepare import HORIZONS, capture_config
from .stage13_xcal_benchmark import FEATURE_SETS, load_xcal, make_folds

LOG = get_logger("hoproj.stage18")

TUNE_HORIZON = 2.0          # middle horizon; avoids tuning to one extreme
N_INNER = 3


# --------------------------------------------------------------- search spaces
def suggest(trial, model: str) -> tuple[dict, dict]:
    """Return (model params, train-config overrides) for one trial."""
    if model == "lgbm":
        return {
            "n_estimators": trial.suggest_int("n_estimators", 200, 1200, step=100),
            "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.15, log=True),
            "num_leaves": trial.suggest_int("num_leaves", 15, 127, log=True),
            "min_child_samples": trial.suggest_int("min_child_samples", 10, 100),
            "subsample": trial.suggest_float("subsample", 0.6, 1.0),
            "subsample_freq": 1,
            "colsample_bytree": trial.suggest_float("colsample_bytree", 0.5, 1.0),
            "reg_lambda": trial.suggest_float("reg_lambda", 0.1, 10.0, log=True),
            "is_unbalance": trial.suggest_categorical("is_unbalance", [True, False]),
        }, {}
    if model == "logreg":
        return {
            "C": trial.suggest_float("C", 1e-3, 1e2, log=True),
            "max_iter": 4000,
            "class_weight": trial.suggest_categorical("class_weight", ["balanced", None]),
        }, {}

    train = {
        "lr": trial.suggest_float("lr", 1e-4, 5e-3, log=True),
        "weight_decay": trial.suggest_float("weight_decay", 1e-6, 1e-2, log=True),
        "batch_size": trial.suggest_categorical("batch_size", [128, 256, 512]),
    }
    if model == "mlp":
        hidden = trial.suggest_categorical(
            "hidden", ["64", "128,64", "256,128", "128,128,64"])
        return {"hidden": [int(x) for x in hidden.split(",")],
                "dropout": trial.suggest_float("dropout", 0.0, 0.4)}, train
    if model == "gru":
        return {"hidden": trial.suggest_categorical("hidden", [32, 64, 96, 128, 192]),
                "layers": trial.suggest_int("layers", 1, 3),
                "dropout": trial.suggest_float("dropout", 0.0, 0.4),
                "bidirectional": trial.suggest_categorical("bidirectional", [True, False])}, train
    if model == "tcn":
        width = trial.suggest_categorical("width", [32, 64, 96])
        depth = trial.suggest_int("depth", 2, 4)
        return {"channels": [width] * depth,
                "kernel_size": trial.suggest_categorical("kernel_size", [2, 3, 5]),
                "dropout": trial.suggest_float("dropout", 0.0, 0.4)}, train
    if model == "transformer":
        d_model = trial.suggest_categorical("d_model", [64, 96, 128])
        nhead = trial.suggest_categorical("nhead", [2, 4, 8])
        while d_model % nhead:                      # keep the head split legal
            nhead //= 2
        return {"d_model": d_model, "nhead": max(1, nhead),
                "layers": trial.suggest_int("layers", 1, 3),
                "ff": d_model * trial.suggest_categorical("ff_mult", [2, 4]),
                "dropout": trial.suggest_float("dropout", 0.0, 0.4)}, train
    raise KeyError(model)


# ------------------------------------------------------------------ inner folds
def inner_folds(train_drives: list[str], k: int, seed: int) -> list[Split]:
    """Grouped K-fold over the outer fold's training drives only."""
    rng = np.random.default_rng(seed)
    ids = list(train_drives)
    rng.shuffle(ids)
    assign = {d: i % k for i, d in enumerate(ids)}
    out = []
    for f in range(k):
        test = [d for d in ids if assign[d] == f]
        rest = [d for d in ids if assign[d] != f]
        n_val = max(1, int(round(0.20 * len(rest))))
        n_cal = max(1, int(round(0.15 * len(rest))))
        out.append(Split(name=f"inner{f}", condition="grouped_drive",
                         val=rest[:n_val], calib=rest[n_val:n_val + n_cal],
                         train=rest[n_val + n_cal:], test=test,
                         note="inner tuning fold"))
    return out


def fit_score(cfg, feats, lab, ho, split, model, seed, cache, horizon) -> float:
    from .trainer import train_and_evaluate
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        res = train_and_evaluate(cfg, feats, lab, ho, split, model,
                                 feature_set="rf_mob_hist", seed=seed, cache_dir=cache)
    row = res.horizon_table.query("horizon_s == @horizon")
    if not len(row) or not np.isfinite(row["auprc"].iloc[0]):
        return float("nan")
    return float(row["auprc"].iloc[0])


def tune_one(base_cfg, feats, lab, ho, outer: Split, model: str, n_trials: int,
             seed: int, cache: Path) -> tuple[dict, dict, float]:
    """Optuna search inside one outer fold. Returns (params, train_over, best)."""
    import optuna
    optuna.logging.set_verbosity(optuna.logging.WARNING)

    pool = list(outer.train) + list(outer.val) + list(outer.calib)
    inner = inner_folds(pool, N_INNER, seed)

    def objective(trial):
        params, train_over = suggest(trial, model)
        cfg = Config(deep_merge(base_cfg, {"model": {"params": params},
                                           "train": train_over}))
        scores = []
        for i, isplit in enumerate(inner):
            try:
                s = fit_score(cfg, feats, lab, ho, isplit, model, seed, cache, TUNE_HORIZON)
            except Exception as exc:                          # noqa: BLE001
                LOG.warning("%s trial %d inner %d failed: %s", model, trial.number, i, exc)
                s = float("nan")
            if np.isfinite(s):
                scores.append(s)
            trial.report(float(np.mean(scores)) if scores else 0.0, i)
            if trial.should_prune():
                raise optuna.TrialPruned()
        if not scores:
            raise optuna.TrialPruned()
        return float(np.mean(scores))

    study = optuna.create_study(
        direction="maximize",
        sampler=optuna.samplers.TPESampler(seed=seed, n_startup_trials=5),
        pruner=optuna.pruners.MedianPruner(n_startup_trials=5, n_warmup_steps=0))
    study.optimize(objective, n_trials=n_trials, catch=(RuntimeError, ValueError))
    params, train_over = suggest(study.best_trial, model)
    return params, train_over, float(study.best_value)


# ------------------------------------------------------------------- outer loop
def evaluate_arm(cfg_for_fold, feats, lab, ho, folds, model, seed, cache):
    """Fit/score a model over the outer folds; pool OOF predictions."""
    from .trainer import train_and_evaluate
    P, Y, M, G = [], [], [], []
    for split, cfg in zip(folds, cfg_for_fold):
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                res = train_and_evaluate(cfg, feats, lab, ho, split, model,
                                         feature_set="rf_mob_hist", seed=seed,
                                         cache_dir=cache)
        except Exception as exc:                              # noqa: BLE001
            LOG.exception("%s %s failed: %s", model, split.name, exc)
            continue
        meta = res.meta.get("test")
        if meta is None or not len(meta):
            continue
        P.append(res.predictions["test"])
        Y.append(res.extras["Y_test"])
        M.append(res.extras["M_test"])
        G.append(meta["drive_id"].to_numpy())
    if not P:
        return pd.DataFrame(), None
    P, Y, M = np.vstack(P), np.vstack(Y), np.vstack(M)
    groups = np.concatenate(G)
    horizons = cfg_for_fold[0].get_path("labels.horizons_s")
    tbl = MET.multi_horizon_table(Y, P, M, horizons, (0.01, 0.05, 0.10))
    return tbl, (Y, P, M, groups)


def paired_delta(a_pack, b_pack, horizons, seed, n_boot=400):
    """Drive-level bootstrap CI on (tuned - default) AUPRC, paired by drive."""
    from sklearn.metrics import average_precision_score
    Ya, Pa, Ma, Ga = a_pack
    Yb, Pb, Mb, Gb = b_pack
    rows = []
    rng = np.random.default_rng(seed)
    drives = np.unique(Ga)
    for j, h in enumerate(horizons):
        sa, sb = Ma[:, j].astype(bool), Mb[:, j].astype(bool)
        if sa.sum() < 50 or sb.sum() < 50:
            continue
        def ap(Y, P, S, keep):
            sel = S & keep
            if sel.sum() < 10 or len(np.unique(Y[sel, j])) < 2:
                return np.nan
            return average_precision_score(Y[sel, j], P[sel, j])
        keep_all = np.ones(len(Ga), dtype=bool)
        point = ap(Ya, Pa, sa, keep_all) - ap(Yb, Pb, sb, keep_all)
        boot = []
        for _ in range(n_boot):
            pick = rng.choice(drives, size=len(drives), replace=True)
            keep = np.isin(Ga, pick)
            d = ap(Ya, Pa, sa, keep) - ap(Yb, Pb, sb, keep)
            if np.isfinite(d):
                boot.append(d)
        lo, hi = (np.nanpercentile(boot, [2.5, 97.5]) if boot else (np.nan, np.nan))
        rows.append({"horizon_s": h, "delta_auprc": point,
                     "ci_low": float(lo), "ci_high": float(hi)})
    return pd.DataFrame(rows)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Stage 18: equal tuning budget")
    ap.add_argument("--root", default=None)
    ap.add_argument("--models", nargs="*",
                    default=["logreg", "lgbm", "mlp", "gru", "tcn", "transformer"])
    ap.add_argument("--trials", type=int, default=20)
    ap.add_argument("--folds", type=int, default=5)
    ap.add_argument("--seed", type=int, default=1337)
    ap.add_argument("--epochs", type=int, default=40)
    ap.add_argument("--tag", default="tuning_budget")
    a = ap.parse_args(argv)

    cfg = capture_config("x", "y", HORIZONS)
    cfg = Config(deep_merge(cfg, {
        "project": {"paths": {"processed": "data/processed_xcal",
                              "interim": "data/interim_xcal",
                              "reports": "reports_xcal",
                              "artifacts": "artifacts_xcal"}},
        "train": {"epochs": a.epochs, "early_stop_patience": 8},
        "eval": {"bootstrap": {"n": 400}},
        "features": {"blocks": FEATURE_SETS["rf_mob_hist"]},
        "tasks": {"qoe": {"enabled": False}, "target": {"enabled": False},
                  "dwell": {"enabled": False}}}))
    paths = resolve_paths(cfg, a.root)
    feats, lab, ho, drives = load_xcal(paths)
    folds = make_folds(drives, a.folds, a.seed)
    cache = paths["interim"] / "window_cache"
    horizons = cfg.get_path("labels.horizons_s")
    LOG.info("stage18: %d models x %d trials x %d inner folds x %d outer folds",
             len(a.models), a.trials, N_INNER, a.folds)

    out_rows, delta_rows, chosen = [], [], {}
    for model in a.models:
        with timed(f"default arm {model}"):
            d_tbl, d_pack = evaluate_arm([cfg] * len(folds), feats, lab, ho, folds,
                                         model, a.seed, cache)
        if len(d_tbl):
            d_tbl.insert(0, "model", model)
            d_tbl.insert(1, "arm", "default")
            out_rows.append(d_tbl)

        per_fold_cfg, fold_params = [], []
        for split in folds:
            with timed(f"tune {model} {split.name}"):
                params, train_over, best = tune_one(cfg, feats, lab, ho, split, model,
                                                    a.trials, a.seed, cache)
            LOG.info("%s %s best inner AUPRC@2s %.4f params=%s train=%s",
                     model, split.name, best, params, train_over)
            per_fold_cfg.append(Config(deep_merge(cfg, {"model": {"params": params},
                                                        "train": train_over})))
            fold_params.append({"fold": split.name, "inner_auprc": best,
                                "params": params, "train": train_over})
        chosen[model] = fold_params

        with timed(f"tuned arm {model}"):
            t_tbl, t_pack = evaluate_arm(per_fold_cfg, feats, lab, ho, folds,
                                         model, a.seed, cache)
        if len(t_tbl):
            t_tbl.insert(0, "model", model)
            t_tbl.insert(1, "arm", "tuned")
            out_rows.append(t_tbl)

        if d_pack and t_pack:
            d = paired_delta(t_pack, d_pack, horizons, a.seed)
            d.insert(0, "model", model)
            delta_rows.append(d)
        # write as we go: a long run should never lose finished models
        if out_rows:
            RPT.save_table(pd.concat(out_rows, ignore_index=True), paths["reports"], a.tag)
        if delta_rows:
            RPT.save_table(pd.concat(delta_rows, ignore_index=True), paths["reports"],
                           f"{a.tag}_delta")
        write_json({"protocol": "nested grouped CV; inner GroupKFold(3) on training "
                                "drives only; equal trial budget; objective mean inner "
                                f"AUPRC at {TUNE_HORIZON}s",
                    "trials": a.trials, "inner_folds": N_INNER, "outer_folds": a.folds,
                    "seed": a.seed, "chosen": chosen},
                   paths["artifacts"] / f"{a.tag}.json")
    LOG.info("stage 18 complete")


if __name__ == "__main__":
    main()

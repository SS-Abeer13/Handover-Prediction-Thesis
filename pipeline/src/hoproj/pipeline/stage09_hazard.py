"""Stage 09 - discrete-time hazard reformulation and self-excitation.

Three questions, one run:

``formulation``  Does estimating a discrete-time hazard beat four independent
                 binary heads at the same horizons, with the same features and
                 the same model class? Monotone horizons are guaranteed by the
                 hazard; the baseline's violation rate measures what the old
                 formulation was getting wrong.
``self-excitation``
                 What is the Hawkes branching ratio of the handover process -
                 the fraction of handovers that exist only because another one
                 just happened - and does feeding that structure to the model
                 as a causal feature improve prediction?
``resolution``   The capture rate is fixed at 1 Hz and cannot be raised, so the
                 grid's own resolution ceiling is measured and reported rather
                 than treated as a defect to be fixed later.

Splits are by whole drive throughout, as everywhere else in this pipeline.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from ..config import Config, deep_merge, load_config, resolve_paths
from ..data import labels as L
from ..data.selfexcite import excitation_features, fit_hawkes
from ..data.features import select_blocks
from ..data.transforms import TabularTransform
from ..eval import metrics as MET
from ..eval import stats as ST
from ..models.hazard import build_long, monotonicity_violations, predict_incidence
from ..models.registry import build_model
from ..utils import get_logger, set_seed, timed, write_json
from .stage07_regime_transfer import build_pool

LOG = get_logger("hoproj.stage09")

EDGES = [1.0, 2.0, 3.0, 5.0]
BLOCKS = ["rf", "mobility", "history"]


# ----------------------------------------------------------------- resolution
def resolution_ceiling(ho: pd.DataFrame, period_s: float = 1.0) -> dict:
    """What a fixed 1 Hz grid can and cannot represent.

    Two handovers closer together than one sample period cannot both be marked
    on the grid, and no model can be credited or penalised for the second. This
    is a property of the instrument, not of the predictor, so it is quantified
    once and carried as a stated ceiling on every event-level metric.
    """
    gaps = (ho.sort_values(["drive_id", "t"])
              .groupby("drive_id")["t"].diff().dt.total_seconds().dropna())
    n = len(ho)
    unresolvable = int((gaps < period_s).sum())
    return {"n_events": n,
            "n_gaps": int(len(gaps)),
            "median_gap_s": float(gaps.median()),
            "frac_gap_under_1_period": float((gaps < period_s).mean()),
            "frac_gap_under_2_periods": float((gaps < 2 * period_s).mean()),
            "frac_gap_under_5s": float((gaps < 5.0).mean()),
            "events_unrepresentable_on_grid": unresolvable,
            "max_representable_event_fraction": float(1 - unresolvable / max(n, 1)),
            "period_s": period_s}


# ------------------------------------------------------------------ modelling
def _lgbm(X: pd.DataFrame, y: np.ndarray, seed: int):
    """Unweighted binary LightGBM.

    ``scale_pos_weight`` is deliberately NOT used. It improves nothing that
    AUPRC measures - the ranking is invariant to a monotone reweighting - and it
    destroys the probability scale. That matters doubly here: the hazard model
    multiplies four per-bin probabilities through the product-limit identity, so
    a per-bin calibration error compounds across horizons. Both arms are fitted
    the same way so the comparison stays fair.
    """
    import lightgbm as lgb
    params = dict(objective="binary", learning_rate=0.05, num_leaves=31,
                  min_data_in_leaf=40, feature_fraction=0.8, bagging_fraction=0.8,
                  bagging_freq=1, lambda_l2=1.0, verbose=-1, seed=seed)
    return lgb.train(params, lgb.Dataset(X, label=y), num_boost_round=400)


def _predict(model, X):
    return model.predict(X)


def run_fold(feats: pd.DataFrame, lab: pd.DataFrame, names: list[str],
             tr: np.ndarray, te: np.ndarray, edges: list[float],
             seed: int) -> dict:
    """Fit the baseline multi-head model and the hazard model on one split."""
    tf = TabularTransform("robust", clip_sigma=8.0)
    tf.fit(feats.loc[tr, names])
    X = pd.DataFrame(tf.transform(feats[names]), columns=names, index=feats.index)

    tags = [L._htag(e) for e in edges]
    Y = np.column_stack([lab[f"y_ho_{t}"].to_numpy(float) for t in tags])
    M = np.column_stack([lab[f"m_ho_{t}"].to_numpy(bool) for t in tags])

    # ---- baseline: four independent binary heads
    P_base = np.zeros_like(Y)
    for k, t in enumerate(tags):
        sel = tr & M[:, k]
        m = _lgbm(X.loc[sel], Y[sel, k], seed)
        P_base[:, k] = _predict(m, X)

    # ---- hazard: one model over (sample x at-risk bin)
    t_next = lab["t_to_next_ho_s"].to_numpy(float)
    t_end = (feats.groupby("drive_id")["t"].transform("max") - feats["t"]
             ).dt.total_seconds().to_numpy(float)
    long = build_long(X, t_next, t_end, edges, valid=tr)
    mh = _lgbm(long.X, long.y, seed)
    P_haz = predict_incidence(mh, X, edges, predict_fn=_predict)

    return {"Y": Y, "M": M, "P_base": P_base, "P_haz": P_haz, "te": te,
            "n_long": len(long.y)}


def evaluate(res: dict, edges: list[float], drives: np.ndarray, label: str) -> pd.DataFrame:
    rows = []
    Y, M, te = res["Y"], res["M"], res["te"]
    for name, P in (("multi-head binary", res["P_base"]), ("discrete-time hazard", res["P_haz"])):
        for k, e in enumerate(edges):
            sel = te & M[:, k]
            if sel.sum() < 50 or len(np.unique(Y[sel, k])) < 2:
                continue
            m = MET.classification_metrics(Y[sel, k], P[sel, k])
            from sklearn.metrics import average_precision_score
            bs = ST.drive_bootstrap(average_precision_score,
                                    Y[sel, k], P[sel, k], drives[sel], n=200)
            lo, hi = bs["ci_low"], bs["ci_high"]
            rows.append({"variant": label, "model": name, "horizon_s": e,
                         "n": m["n"], "positive_rate": m["positive_rate"],
                         "auprc": m["auprc"], "auprc_lift": m.get("auprc_lift"),
                         "auprc_ci_low": lo, "auprc_ci_high": hi,
                         "auroc": m["auroc"], "brier": m["brier"], "ece": m["ece"],
                         "recall_at_fpr0.05": m.get("recall_at_fpr0.05")})
    return pd.DataFrame(rows)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--folds", type=int, default=4)
    ap.add_argument("--seed", type=int, default=1337)
    a = ap.parse_args()
    set_seed(a.seed)

    cfg = Config(deep_merge(load_config("base.yaml", adapter="xcal_signalling"),
                            {"features": {"blocks": BLOCKS}}))
    paths = resolve_paths(cfg)
    out_dir = Path(paths["reports"]) / "tables"
    out_dir.mkdir(parents=True, exist_ok=True)
    art = Path(paths["artifacts"])

    feats, lab, ho = build_pool(cfg)
    feats = feats.reset_index(drop=True)
    lab = lab.reset_index(drop=True)
    drives = feats["drive_id"].to_numpy()

    # ---------------------------------------------------------- 1 Hz ceiling
    ceiling = {"pooled": resolution_ceiling(ho)}
    for cap, g in ho.groupby("capture"):
        ceiling[str(cap)] = resolution_ceiling(g)
    LOG.info("1 Hz resolution ceiling (pooled): %s", ceiling["pooled"])

    # ------------------------------------------------------ Hawkes structure
    hawkes = {}
    try:
        hawkes["pooled"] = fit_hawkes(ho, feats).as_dict()
    except Exception as exc:                                   # pragma: no cover
        LOG.warning("pooled Hawkes fit failed: %s", exc)
    for cap, g in ho.groupby("capture"):
        sub = feats[feats["capture"] == cap] if "capture" in feats else feats
        try:
            hawkes[str(cap)] = fit_hawkes(g, sub).as_dict()
        except Exception as exc:
            LOG.warning("Hawkes fit failed for %s: %s", cap, exc)
    pd.DataFrame(hawkes).T.to_csv(out_dir / "hawkes_selfexcitation.csv")
    (out_dir / "hawkes_selfexcitation.md").write_text(
        pd.DataFrame(hawkes).T.round(4).to_markdown())

    # ------------------------------------------------- self-excitation feats
    with timed("self-excitation features"):
        se = excitation_features(feats, ho)
    feats_se = pd.concat([feats, se], axis=1)
    base_names = [n for n in select_blocks(feats, BLOCKS) if n in feats.columns]
    se_names = base_names + list(se.columns)
    feats_se.attrs = dict(feats.attrs)

    # ------------------------------------------------------- grouped K folds
    rng = np.random.default_rng(a.seed)
    uniq = np.unique(drives)
    rng.shuffle(uniq)
    folds = np.array_split(uniq, a.folds)

    all_rows, mono_rows = [], []
    for fi, hold in enumerate(folds):
        te = np.isin(drives, hold)
        tr = ~te
        if te.sum() < 100 or tr.sum() < 500:
            continue
        for label, F, names in (("rf+mobility+history", feats, base_names),
                                ("+ self-excitation", feats_se, se_names)):
            with timed(f"fold {fi} [{label}]"):
                res = run_fold(F, lab, names, tr, te, EDGES, a.seed + fi)
            df = evaluate(res, EDGES, drives, label)
            df["fold"] = fi
            all_rows.append(df)
            for nm, P in (("multi-head binary", res["P_base"]),
                          ("discrete-time hazard", res["P_haz"])):
                v = monotonicity_violations(P[te])
                mono_rows.append({"fold": fi, "variant": label, "model": nm, **v})

    res = pd.concat(all_rows, ignore_index=True)
    res.to_csv(out_dir / "hazard_vs_multihead_folds.csv", index=False)
    summ = (res.groupby(["variant", "model", "horizon_s"])
              [["positive_rate", "auprc", "auprc_lift", "auroc", "brier", "ece"]]
              .mean().round(4).reset_index())
    summ.to_csv(out_dir / "hazard_vs_multihead.csv", index=False)
    (out_dir / "hazard_vs_multihead.md").write_text(summ.to_markdown(index=False))

    # paired significance: hazard vs multi-head, per horizon, across drives
    pair_rows = []
    for (variant, h), g in res.groupby(["variant", "horizon_s"]):
        a_ = g.loc[g.model == "discrete-time hazard", "auprc"].to_numpy()
        b_ = g.loc[g.model == "multi-head binary", "auprc"].to_numpy()
        n = min(len(a_), len(b_))
        if n >= 3:
            from scipy.stats import wilcoxon
            try:
                pv = float(wilcoxon(a_[:n], b_[:n]).pvalue)
            except Exception:
                pv = float("nan")
        else:
            pv = float("nan")
        pair_rows.append({"variant": variant, "horizon_s": h, "n_folds": n,
                          "auprc_hazard": float(np.mean(a_)), "auprc_multihead": float(np.mean(b_)),
                          "delta": float(np.mean(a_) - np.mean(b_)), "wilcoxon_p": pv})
    pd.DataFrame(pair_rows).round(4).to_csv(out_dir / "hazard_paired_test.csv", index=False)
    (out_dir / "hazard_paired_test.md").write_text(
        pd.DataFrame(pair_rows).round(4).to_markdown(index=False))

    mono = pd.DataFrame(mono_rows)
    mono_s = mono.groupby(["variant", "model"]).mean(numeric_only=True).round(4).reset_index()
    mono_s.to_csv(out_dir / "horizon_monotonicity.csv", index=False)
    (out_dir / "horizon_monotonicity.md").write_text(mono_s.to_markdown(index=False))

    write_json({"resolution_ceiling": ceiling, "hawkes": hawkes}, art / "stage09.json")
    LOG.info("\n%s", summ.to_string(index=False))
    LOG.info("\n%s", mono_s.to_string(index=False))


if __name__ == "__main__":
    main()

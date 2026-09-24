"""Stage 11 - the learned mechanism, and what predicting it could buy.

Two closing pieces, both on data already in hand.

``mechanism``  A monotone-constrained Explainable Boosting Machine estimates
               the same discrete-time hazard. Its shape function for the
               serving-to-neighbour gap is the learned trigger curve, and it can
               be plotted directly against the analytic 3GPP A3 threshold that
               the signalling says the network is running. The monotone
               constraint is a physics prior, not a regulariser of convenience:
               the A3 event fires when Mn + Ofn - Hys > Ms + Ofs + Off, which is
               monotone increasing in the neighbour-minus-serving gap.

``benefit``    The counting upper bound on avoidable ping-pongs, swept over the
               minimum useful lead time and an actuator-efficacy parameter. No
               counterfactual is assumed anywhere; see ``eval/benefit.py``.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from ..config import Config, deep_merge, load_config, resolve_paths
from ..data import labels as L
from ..data.features import select_blocks
from ..data.transforms import TabularTransform
from ..eval.benefit import benefit_envelope
from ..models.hazard import build_long, predict_incidence
from ..utils import get_logger, set_seed, timed, write_json
from .stage07_regime_transfer import build_pool
from .stage09_hazard import BLOCKS, EDGES, _lgbm, _predict

LOG = get_logger("hoproj.stage11")

GAP_FEATURE = "gap_serving_nbr1"


def fit_ebm(X: pd.DataFrame, y: np.ndarray, monotone: dict[str, int], seed: int):
    from interpret.glassbox import ExplainableBoostingClassifier
    cols = list(X.columns)
    mono = [monotone.get(c, 0) for c in cols]
    ebm = ExplainableBoostingClassifier(
        feature_names=cols, monotone_constraints=mono, interactions=0,
        outer_bags=8, inner_bags=0, max_bins=64, random_state=seed)
    ebm.fit(X, y)
    return ebm


def shape_function(ebm, feature: str) -> pd.DataFrame | None:
    """Per-feature contribution on the log-odds scale, as (bin centre, value)."""
    names = list(ebm.term_names_)
    if feature not in names:
        return None
    i = names.index(feature)
    bins = ebm.bins_[i][0]
    scores = np.asarray(ebm.term_scores_[i])[1:-1]      # drop the missing/unseen bins
    edges = np.asarray(bins, dtype=float)
    centres = np.concatenate([[edges[0]], (edges[:-1] + edges[1:]) / 2, [edges[-1]]])
    n = min(len(centres), len(scores))
    return pd.DataFrame({"feature": feature, "bin_centre": centres[:n],
                         "log_odds_contribution": scores[:n]})


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=1337)
    ap.add_argument("--skip-ebm", action="store_true")
    a = ap.parse_args()
    set_seed(a.seed)

    cfg = Config(deep_merge(load_config("base.yaml", adapter="xcal_signalling"),
                            {"features": {"blocks": BLOCKS}}))
    paths = resolve_paths(cfg)
    out = Path(paths["reports"]) / "tables"
    out.mkdir(parents=True, exist_ok=True)

    feats, lab, ho = build_pool(cfg)
    feats = feats.reset_index(drop=True); lab = lab.reset_index(drop=True)
    drives = feats["drive_id"].to_numpy()
    names = [n for n in select_blocks(feats, BLOCKS) if n in feats.columns]

    rng = np.random.default_rng(a.seed)
    uniq = np.unique(drives); rng.shuffle(uniq)
    tr_d = uniq[:int(0.7 * len(uniq))]
    tr = np.isin(drives, tr_d); te = ~tr

    tf = TabularTransform("robust", clip_sigma=8.0)
    tf.fit(feats.loc[tr, names])
    X = pd.DataFrame(tf.transform(feats[names]), columns=names, index=feats.index)

    t_next = lab["t_to_next_ho_s"].to_numpy(float)
    t_end = (feats.groupby("drive_id")["t"].transform("max") - feats["t"]
             ).dt.total_seconds().to_numpy(float)

    # ------------------------------------------------------------- mechanism
    if not a.skip_ebm and GAP_FEATURE in names:
        # unscaled gap, so the shape function is readable in dB against the A3 rule
        Xr = feats[names].copy()
        long_r = build_long(Xr, t_next, t_end, EDGES, valid=tr)
        # gap_serving_nbr1 = serving_rsrp - neighbour_rsrp, so a LARGER gap means
        # the serving cell is further ahead and a handover is LESS likely. The A3
        # event fires when Mn - Ms > Off, i.e. when gap < -Off. The hazard is
        # therefore monotone DECREASING in this feature; constraining it the other
        # way (as a first pass did) forces the model to fit against the physics and
        # costs roughly 0.10 AUPRC.
        mono = {GAP_FEATURE: -1, "gap_serving_best_nbr": -1}
        with timed("monotone EBM"):
            ebm = fit_ebm(long_r.X, long_r.y, mono, a.seed)
        sh = shape_function(ebm, GAP_FEATURE)
        if sh is not None:
            sh.to_csv(out / "ebm_shape_gap.csv", index=False)
            LOG.info("EBM shape function for %s written (%d bins, range %.1f..%.1f dB)",
                     GAP_FEATURE, len(sh), sh.bin_centre.min(), sh.bin_centre.max())
        imp = pd.DataFrame({"term": list(ebm.term_names_),
                            "importance": list(ebm.term_importances())}
                           ).sort_values("importance", ascending=False)
        imp.head(25).to_csv(out / "ebm_term_importance.csv", index=False)
        (out / "ebm_term_importance.md").write_text(imp.head(20).round(4).to_markdown(index=False))

        # does the physics prior cost or buy anything out of domain?
        from sklearn.metrics import average_precision_score, roc_auc_score
        Pe = predict_incidence(ebm, Xr, EDGES,
                               predict_fn=lambda m, x: m.predict_proba(x)[:, 1])
        rows = []
        for k, e in enumerate(EDGES):
            tag = L._htag(e)
            m = te & lab[f"m_ho_{tag}"].to_numpy(bool)
            y = lab[f"y_ho_{tag}"].to_numpy(float)
            if m.sum() < 50 or len(np.unique(y[m])) < 2:
                continue
            rows.append({"model": "monotone EBM", "horizon_s": e,
                         "auprc": float(average_precision_score(y[m], Pe[m, k])),
                         "auroc": float(roc_auc_score(y[m], Pe[m, k]))})
        long_s = build_long(X, t_next, t_end, EDGES, valid=tr)
        mg = _lgbm(long_s.X, long_s.y, a.seed)
        Pl = predict_incidence(mg, X, EDGES, predict_fn=_predict)
        for k, e in enumerate(EDGES):
            tag = L._htag(e)
            m = te & lab[f"m_ho_{tag}"].to_numpy(bool)
            y = lab[f"y_ho_{tag}"].to_numpy(float)
            if m.sum() < 50 or len(np.unique(y[m])) < 2:
                continue
            rows.append({"model": "LightGBM hazard", "horizon_s": e,
                         "auprc": float(average_precision_score(y[m], Pl[m, k])),
                         "auroc": float(roc_auc_score(y[m], Pl[m, k]))})
        cmp = pd.DataFrame(rows).round(4)
        cmp.to_csv(out / "ebm_vs_lgbm_hazard.csv", index=False)
        (out / "ebm_vs_lgbm_hazard.md").write_text(cmp.to_markdown(index=False))
        LOG.info("\n%s", cmp.to_string(index=False))
    else:
        long_s = build_long(X, t_next, t_end, EDGES, valid=tr)
        mg = _lgbm(long_s.X, long_s.y, a.seed)
        Pl = predict_incidence(mg, X, EDGES, predict_fn=_predict)

    # --------------------------------------------------------------- benefit
    k2 = EDGES.index(2.0)
    score = Pl[:, k2]
    te_s = feats.loc[te].copy()
    te_score = score[te]
    ho_te = ho[ho["drive_id"].isin(set(feats.loc[te, "drive_id"]))]
    q = {f"alarm_top_{int(p*100)}pct": float(np.quantile(te_score, 1 - p))
         for p in (0.02, 0.05, 0.10, 0.20, 0.40)}
    env = benefit_envelope(ho_te, te_s, te_score, q, event_col="is_pingpong")
    env.round(4).to_csv(out / "benefit_envelope_pingpong.csv", index=False)
    e1 = env[env.actuator_efficacy == 1.0]
    piv = e1.pivot_table(index=["operating_point", "alarm_rate"],
                         columns="min_lead_time_s", values="max_avoidable_frac").round(3)
    pref = e1.pivot_table(index=["operating_point", "alarm_rate"],
                          columns="min_lead_time_s", values="random_alarm_reference").round(3)
    pexc = e1.pivot_table(index=["operating_point", "alarm_rate"],
                          columns="min_lead_time_s", values="excess_over_random").round(3)
    (out / "benefit_envelope_pingpong.md").write_text(
        "## Upper bound on avoidable ping-pongs (perfect actuator)\n\n"
        + piv.to_markdown()
        + "\n\n## Same-rate random-alarm reference\n\n" + pref.to_markdown()
        + "\n\n## Excess over random - the part the predictor actually earns\n\n"
        + pexc.to_markdown() + "\n")
    LOG.info("\nupper bound (perfect actuator)\n%s\n\nrandom reference\n%s\n\nexcess\n%s",
             piv.to_string(), pref.to_string(), pexc.to_string())

    write_json({"n_test_drives": int(len(np.unique(drives[te]))),
                "n_adverse_events": int(env["n_adverse_events"].iloc[0]) if len(env) else 0,
                "thresholds": q},
               Path(paths["artifacts"]) / "stage11.json")


if __name__ == "__main__":
    main()

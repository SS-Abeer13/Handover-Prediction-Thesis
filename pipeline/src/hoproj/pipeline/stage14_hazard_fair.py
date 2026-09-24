"""Stage 14 - the hazard claim, tested against a baseline that can fight back.

Stage 09 compared a discrete-time hazard model against four independent binary
LightGBM heads and reported better calibration (ECE down 23-35%) and zero
monotonicity violations against the baseline's 25%. Both are true and neither
is interesting, because that baseline was raw and uncalibrated. Nobody deploys
raw multi-head probabilities; they run isotonic calibration, and if they care
about coherence across horizons they project onto the monotone cone. A reviewer
will ask whether those two lines of post-processing close the gap. This stage
answers that before the reviewer asks.

Six arms, identical folds, identical features, identical seeds:

  1. multi-head LGBM                    the stage 09 baseline, unchanged
  2. multi-head LGBM + isotonic         standard post-hoc calibration
  3. multi-head LGBM + isotonic + PAVA  ... and projected monotone
  4. hazard LGBM                        the proposed formulation
  5. multi-head MLP                     same comparison, different learner
  6. hazard MLP                         ... so "formulation" and "LightGBM"
                                        cannot be confused for each other

Two further corrections to stage 09's protocol:

* Five horizons including 0.5 s. Signalling handovers carry millisecond
  timestamps, so the sub-sample-period horizon is labelable.
* Five seeds x four folds = twenty paired observations per comparison. Stage 09
  had four, where a two-sided Wilcoxon cannot report below p = 0.125 no matter
  how large the effect is. Every delta also carries a cluster bootstrap CI.

Isotonic calibrators are fitted on calibration drives held out of training
inside each fold, never on the test drives.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from ..config import Config, deep_merge, resolve_paths
from ..data.features import select_blocks
from ..data.selfexcite import excitation_features
from ..data.transforms import TabularTransform
from ..eval import metrics as MET
from ..eval import stats as ST
from ..models.hazard import build_long, monotonicity_violations, predict_incidence
from ..models.monotone import LogisticHazardMLP, isotonic_per_horizon, pava_rows
from ..utils import get_logger, set_seed, timed, write_json
from .stage12_xcal_prepare import HORIZONS, capture_config
from .stage13_xcal_benchmark import load_xcal

LOG = get_logger("hoproj.stage14")

BLOCKS = ["rf", "mobility", "history"]
EDGES = HORIZONS                      # [0.5, 1, 2, 3, 5]


def _lgbm(X, y, seed: int):
    """Unweighted binary LightGBM; see stage 09 on why there is no pos weight."""
    import lightgbm as lgb
    params = dict(objective="binary", learning_rate=0.05, num_leaves=31,
                  min_data_in_leaf=40, feature_fraction=0.8, bagging_fraction=0.8,
                  bagging_freq=1, lambda_l2=1.0, verbose=-1, seed=seed)
    return lgb.train(params, lgb.Dataset(X, label=y), num_boost_round=400)


def _htags(edges):
    return [f"h{str(e).replace('.', 'p')}" for e in edges]


def run_fold(X: pd.DataFrame, lab: pd.DataFrame, t_end: np.ndarray,
             fit: np.ndarray, cal: np.ndarray, te: np.ndarray,
             edges: list[float], seed: int, with_mlp: bool) -> dict:
    """Fit every arm on one fold. `fit` trains, `cal` calibrates, `te` scores."""
    tags = _htags(edges)
    Y = np.column_stack([lab[f"y_ho_{t}"].to_numpy(float) for t in tags])
    M = np.column_stack([lab[f"m_ho_{t}"].to_numpy(bool) for t in tags])
    t_next = lab["t_to_next_ho_s"].to_numpy(float)
    out: dict[str, np.ndarray] = {}

    # ---- arm 1: four independent binary heads
    P_base = np.zeros_like(Y)
    for k, t in enumerate(tags):
        sel = fit & M[:, k]
        P_base[:, k] = _lgbm(X.loc[sel], Y[sel, k], seed).predict(X)
    out["multi-head LGBM"] = P_base

    # ---- arm 2/3: the same heads, calibrated, then projected monotone
    P_iso = isotonic_per_horizon(P_base[cal], Y[cal], M[cal], P_base)
    out["multi-head LGBM + isotonic"] = P_iso
    out["multi-head LGBM + isotonic + monotone"] = pava_rows(P_iso)

    # ---- arm 4: discrete-time hazard, same learner
    long = build_long(X, t_next, t_end, edges, valid=fit)
    mh = _lgbm(long.X, long.y, seed)
    out["hazard LGBM"] = predict_incidence(mh, X, edges,
                                           predict_fn=lambda m, z: m.predict(z))

    if with_mlp:
        # ---- arm 5: multi-head, neural
        P_mlp = np.zeros_like(Y)
        for k, t in enumerate(tags):
            sel = fit & M[:, k]
            m = LogisticHazardMLP(X.shape[1], seed=seed).fit(X.loc[sel].to_numpy(),
                                                             Y[sel, k])
            P_mlp[:, k] = m.predict(X.to_numpy())
        out["multi-head MLP"] = P_mlp

        # ---- arm 6: hazard, neural - same long format, different function class
        hm = LogisticHazardMLP(long.X.shape[1], seed=seed).fit(long.X.to_numpy(), long.y)
        out["hazard MLP"] = predict_incidence(
            hm, X, edges, predict_fn=lambda m, z: m.predict(np.asarray(z)))

    return {"P": out, "Y": Y, "M": M, "te": te}


def evaluate(res: dict, edges: list[float], drives: np.ndarray,
             variant: str, fold: int, seed: int) -> tuple[pd.DataFrame, list[dict]]:
    rows, mono = [], []
    Y, M, te = res["Y"], res["M"], res["te"]
    for name, P in res["P"].items():
        for k, e in enumerate(edges):
            sel = te & M[:, k]
            if sel.sum() < 50 or len(np.unique(Y[sel, k])) < 2:
                continue
            m = MET.classification_metrics(Y[sel, k], P[sel, k])
            rows.append({"variant": variant, "model": name, "horizon_s": e,
                         "fold": fold, "seed": seed, "n": m["n"],
                         "positive_rate": m["positive_rate"], "auprc": m["auprc"],
                         "auprc_lift": m.get("auprc_lift"), "auroc": m["auroc"],
                         "brier": m["brier"], "ece": m["ece"]})
        mono.append({"variant": variant, "model": name, "fold": fold, "seed": seed,
                     **monotonicity_violations(P[te])})
    return pd.DataFrame(rows), mono


def paired_stats(res: pd.DataFrame, reference: str, out_dir: Path,
                 sfx: str = "") -> pd.DataFrame:
    """Every arm against the hazard model, with a CI on the delta, not just a p."""
    from scipy.stats import wilcoxon

    rows = []
    key = ["variant", "horizon_s", "fold", "seed"]
    ref = res[res.model == reference].set_index(key)
    for name, g in res.groupby("model"):
        if name == reference:
            continue
        gg = g.set_index(key)
        common = ref.index.intersection(gg.index)
        for (variant, h), idx in pd.Series(list(common), index=pd.MultiIndex.from_tuples(
                common, names=key)).groupby(level=["variant", "horizon_s"]):
            keys = list(idx)
            for metric in ("auprc", "ece"):
                a = ref.loc[keys, metric].to_numpy(float)
                b = gg.loc[keys, metric].to_numpy(float)
                d = a - b
                n = len(d)
                if n < 3 or not np.isfinite(d).all():
                    continue
                # bootstrap over the paired observations (fold x seed)
                rng = np.random.default_rng(0)
                bs = np.array([np.mean(rng.choice(d, n, replace=True)) for _ in range(2000)])
                try:
                    pv = float(wilcoxon(a, b).pvalue)
                except Exception:                              # all-zero differences
                    pv = float("nan")
                rows.append({"variant": variant, "horizon_s": h, "metric": metric,
                             "comparator": name, "n_pairs": n,
                             f"{metric}_hazard": float(np.mean(a)),
                             f"{metric}_comparator": float(np.mean(b)),
                             "delta_hazard_minus_comparator": float(np.mean(d)),
                             "delta_ci_low": float(np.quantile(bs, 0.025)),
                             "delta_ci_high": float(np.quantile(bs, 0.975)),
                             "wilcoxon_p": pv})
    tbl = pd.DataFrame(rows).round(4)
    tbl.to_csv(out_dir / f"hazard_paired_fair{sfx}.csv", index=False)
    (out_dir / f"hazard_paired_fair{sfx}.md").write_text(tbl.to_markdown(index=False))
    return tbl


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description="Stage 14: fair hazard comparison")
    ap.add_argument("--root", default=None)
    ap.add_argument("--folds", type=int, default=4)
    ap.add_argument("--seeds", nargs="*", type=int, default=[1337, 1338, 1339, 1340, 1341])
    ap.add_argument("--no-mlp", action="store_true")
    ap.add_argument("--tag", default="",
                    help="suffix for output tables; keeps separate runs apart")
    a = ap.parse_args(argv)

    cfg = Config(deep_merge(capture_config("x", "y", EDGES), {
        "project": {"paths": {"processed": "data/processed_xcal",
                              "interim": "data/interim_xcal",
                              "reports": "reports_xcal",
                              "artifacts": "artifacts_xcal"}}}))
    paths = resolve_paths(cfg, a.root)
    out_dir = Path(paths["reports"]) / "tables"
    out_dir.mkdir(parents=True, exist_ok=True)
    sfx = f"_{a.tag}" if a.tag else ""

    feats, lab, ho, _ = load_xcal(paths)
    feats = feats.reset_index(drop=True)
    lab = lab.reset_index(drop=True)
    drives = feats["drive_id"].to_numpy()
    t_end = (feats.groupby("drive_id")["t"].transform("max") - feats["t"]
             ).dt.total_seconds().to_numpy(float)

    with timed("self-excitation features"):
        se = excitation_features(feats, ho)
    base_names = [n for n in select_blocks(feats, BLOCKS) if n in feats.columns]
    feats_se = pd.concat([feats, se], axis=1)
    feats_se.attrs = dict(feats.attrs)
    se_names = base_names + list(se.columns)

    all_rows, mono_rows = [], []
    for seed in a.seeds:
        set_seed(seed)
        rng = np.random.default_rng(seed)
        uniq = np.unique(drives)
        rng.shuffle(uniq)
        folds = np.array_split(uniq, a.folds)
        for fi, hold in enumerate(folds):
            te = np.isin(drives, hold)
            rest = np.setdiff1d(uniq, hold)
            rng.shuffle(rest)
            n_cal = max(1, int(round(0.2 * len(rest))))
            cal = np.isin(drives, rest[:n_cal])
            fit = np.isin(drives, rest[n_cal:])
            if te.sum() < 100 or fit.sum() < 500 or cal.sum() < 100:
                continue
            for variant, F, names in (("rf+mobility+history", feats, base_names),
                                      ("+ self-excitation", feats_se, se_names)):
                tf = TabularTransform("robust", clip_sigma=8.0)
                tf.fit(F.loc[fit, names])
                X = pd.DataFrame(tf.transform(F[names]), columns=names, index=F.index)
                with timed(f"seed {seed} fold {fi} [{variant}]"):
                    res = run_fold(X, lab, t_end, fit, cal, te, EDGES, seed + fi,
                                   with_mlp=not a.no_mlp)
                df, mono = evaluate(res, EDGES, drives, variant, fi, seed)
                all_rows.append(df)
                mono_rows += mono
            # Checkpoint after every fold. Each (seed, fold) costs minutes on
            # a two-core box, so a run that is interrupted three seeds in
            # should still leave a usable paired test behind.
            pd.concat(all_rows, ignore_index=True).to_csv(
                out_dir / f"hazard_fair_folds{sfx}.csv", index=False)

    res = pd.concat(all_rows, ignore_index=True)
    res.to_csv(out_dir / f"hazard_fair_folds{sfx}.csv", index=False)

    summ = (res.groupby(["variant", "model", "horizon_s"])
              [["positive_rate", "auprc", "auprc_lift", "auroc", "brier", "ece"]]
              .agg(["mean", "std"]).round(4))
    summ.columns = ["_".join(c) for c in summ.columns]
    summ = summ.reset_index()
    summ.to_csv(out_dir / f"hazard_fair_summary{sfx}.csv", index=False)
    (out_dir / f"hazard_fair_summary{sfx}.md").write_text(summ.to_markdown(index=False))

    paired = paired_stats(res, "hazard LGBM", out_dir, sfx)

    mono = pd.DataFrame(mono_rows)
    mono_s = (mono.groupby(["variant", "model"]).mean(numeric_only=True)
              .round(4).reset_index().drop(columns=["fold", "seed"], errors="ignore"))
    mono_s.to_csv(out_dir / f"horizon_monotonicity_fair{sfx}.csv", index=False)
    (out_dir / f"horizon_monotonicity_fair{sfx}.md").write_text(mono_s.to_markdown(index=False))

    write_json({"arms": sorted(res["model"].unique()), "seeds": a.seeds,
                "folds": a.folds, "edges": EDGES,
                "n_paired_observations": int(len(a.seeds) * a.folds),
                "note": "isotonic calibrators fitted on held-out calibration drives "
                        "inside each fold; PAVA is the L2 monotone projection"},
               Path(paths["artifacts"]) / f"stage14{sfx}.json")
    LOG.info("\n%s", summ.to_string(index=False))
    LOG.info("\n%s", mono_s.to_string(index=False))
    LOG.info("\n%s", paired.to_string(index=False))


if __name__ == "__main__":
    main()

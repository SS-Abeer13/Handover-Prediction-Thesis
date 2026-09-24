"""Stage 16 - signalling features, report conversion, and a ping-pong predictor.

Three additions, all on the pooled XCAL dataset, all under the same grouped
K-fold protocol as stage 13.

**1. Does the signalling channel help prediction?**
Until now the models saw only the periodic CSV. This adds a ``signalling``
feature block - the A3 time-to-trigger clock, counts of measurement reports in
strictly earlier bins, and RF slopes - and ablates it against the existing
blocks. The expectation is a gain concentrated at 2-5 s, because a
measurement report leads its handover by up to TTT plus the RRC procedure
time, while dwell should keep dominating at 1 s.

**2. Report conversion as a task in its own right.**
Ghoshal et al. measured that most reported A3 events never become a handover;
stage 11 replicated it at 60.6% on our data. Neither paper *models* it. Given
that a report has been sent, will the network act on it within k seconds? The
positives are the converted reports and the negatives are the three-in-five
that are not. It is a cleanly posed, network-side, previously unmodelled
question, and the data to answer it is already parsed.

**3. A ping-pong predictor, instead of borrowing the handover model.**
The benefit envelope in stage 11 ranked samples by "is a handover imminent"
and then measured how many *ping-pongs* that ranking caught, which is why the
excess over a random alarm went negative above a 10% budget. A predictor
trained on the ping-pong label deserves its own envelope before the
conclusion is drawn.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from ..config import Config, deep_merge, resolve_paths
from ..data.config_regime import annotate_reports, parse_maps
from ..data.features import select_blocks
from ..data.signalling import parse_signalling
from ..data.signalling_features import build_signalling_features
from ..data.transforms import TabularTransform
from ..eval import metrics as MET
from ..eval import stats as ST
from ..eval.benefit import benefit_envelope, warning_coverage
from ..utils import get_logger, read_table, set_seed, timed, write_json, write_parquet
from .stage12_xcal_prepare import CAPTURES, HORIZONS, capture_config
from .stage13_xcal_benchmark import load_xcal
from .stage14_hazard_fair import _htags, _lgbm

LOG = get_logger("hoproj.stage16")

BLOCKS = ["rf", "mobility", "history"]
PINGPONG_WINDOW_S = 15.0                 # literature standard; see pingpong_benchmark.md


# ------------------------------------------------------------------ reports
def all_reports(cache: Path) -> pd.DataFrame:
    """Every annotated measurement report, all captures, cached to parquet."""
    cache.parent.mkdir(parents=True, exist_ok=True)
    if cache.exists():
        df = read_table(cache)
        df["t"] = pd.to_datetime(df["t"])
        return df
    frames = []
    for tag, raw, _csv, sig in CAPTURES:
        p = Path(raw) / sig
        with timed(f"reports {tag}"):
            maps = parse_maps(p)
            log = parse_signalling(p)
            r = annotate_reports(log.measurement_reports, maps)
            r["capture"] = tag
        frames.append(r)
    out = pd.concat(frames, ignore_index=True)
    keep = [c for c in out.columns if out[c].dtype != object or c in
            ("event_id", "capture", "report_config_id", "meas_object_id")]
    out = out[keep]
    write_parquet(out, cache)
    return out


def conversion_dataset(reports: pd.DataFrame, ho: pd.DataFrame, feats: pd.DataFrame,
                       within_s: float = 2.0) -> tuple[pd.DataFrame, np.ndarray, np.ndarray]:
    """One row per A3 report: did a handover follow within `within_s`?

    Features are the sample-frame row in force at the report's time (the last
    sample at or before it), plus the report's own configuration. Reports
    outside any retained drive are dropped, so the task shares the QC and the
    drive grouping of every other table here.
    """
    a3 = reports[reports["event_id"] == "A3"].sort_values("t").reset_index(drop=True)
    rows, y, grp = [], [], []
    for cap, r_cap in a3.groupby("capture"):
        f_cap = feats[feats["capture"] == cap].sort_values("t")
        h_cap = ho[ho["capture"] == cap].sort_values("t")
        if not len(f_cap) or not len(h_cap):
            continue
        merged = pd.merge_asof(r_cap[["t", "a3_offset_db", "hysteresis_db",
                                      "time_to_trigger_ms"]],
                               f_cap, on="t", direction="backward",
                               tolerance=pd.Timedelta(seconds=2.0),
                               suffixes=("_rep", ""))
        ok = merged["drive_id"].notna().to_numpy()
        ht = h_cap["t"].astype("int64").to_numpy() / 1e9
        rt = r_cap["t"].astype("int64").to_numpy() / 1e9
        nxt = np.searchsorted(ht, rt, side="left")
        gap = np.where(nxt < len(ht), ht[np.clip(nxt, 0, len(ht) - 1)] - rt, np.inf)
        rows.append(merged[ok])
        y.append((gap[ok] <= within_s).astype(int))
        grp.append(merged.loc[ok, "drive_id"].to_numpy())
    if not rows:
        return pd.DataFrame(), np.empty(0), np.empty(0)
    X = pd.concat(rows, ignore_index=True)
    return X, np.concatenate(y), np.concatenate(grp)


# --------------------------------------------------------------- ping-pong
def pingpong_labels(feats: pd.DataFrame, ho: pd.DataFrame,
                    window_s: float = PINGPONG_WINDOW_S,
                    lead_s: float = 5.0) -> np.ndarray:
    """1 if the NEXT handover from this sample is a ping-pong within `lead_s`.

    ``is_pingpong`` on the handover table already marks a handover whose return
    to the source cell happens inside the window, so the sample-level target is
    simply "the next handover is one of those, and it is close enough to act
    on".
    """
    y = np.zeros(len(feats), dtype=int)
    col = "is_pingpong" if "is_pingpong" in ho.columns else None
    if col is None:
        return y
    ts = feats["t"].astype("int64").to_numpy() / 1e9
    drives = feats["drive_id"].to_numpy()
    for d, idx in pd.Series(np.arange(len(feats)), index=drives).groupby(level=0):
        h = ho[ho["drive_id"] == d].sort_values("t")
        if not len(h):
            continue
        ht = h["t"].astype("int64").to_numpy() / 1e9
        flag = h[col].to_numpy(bool)
        pos = idx.to_numpy()
        nxt = np.searchsorted(ht, ts[pos], side="left")
        inb = nxt < len(ht)
        j = np.clip(nxt, 0, len(ht) - 1)
        y[pos] = (inb & flag[j] & ((ht[j] - ts[pos]) <= lead_s)).astype(int)
    return y


# -------------------------------------------------------------------- runs
def kfold_oof(X: pd.DataFrame, y: np.ndarray, groups: np.ndarray,
              k: int, seed: int) -> np.ndarray:
    """Out-of-fold predictions from a grouped K-fold rotation."""
    p = np.zeros(len(y), dtype=float)
    rng = np.random.default_rng(seed)
    uniq = np.unique(groups)
    rng.shuffle(uniq)
    for hold in np.array_split(uniq, k):
        te = np.isin(groups, hold)
        tr = ~te
        if tr.sum() < 100 or te.sum() < 20 or len(np.unique(y[tr])) < 2:
            continue
        m = _lgbm(X.loc[tr], y[tr], seed)
        p[te] = m.predict(X.loc[te])
    return p


def scored(y, p, groups, label: str, seed: int) -> dict:
    from sklearn.metrics import average_precision_score
    m = MET.classification_metrics(y, p)
    b = ST.drive_bootstrap(
        lambda yy, pp: average_precision_score(yy, pp) if len(np.unique(yy)) > 1 else np.nan,
        y, p, groups, n=400, seed=seed)
    return {"task": label, "n": m["n"], "positive_rate": m["positive_rate"],
            "auprc": m["auprc"], "auprc_lift": m.get("auprc_lift"),
            "auprc_ci_low": b["ci_low"], "auprc_ci_high": b["ci_high"],
            "auroc": m["auroc"], "brier": m["brier"], "ece": m["ece"],
            "n_drives": b["n_groups"]}


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description="Stage 16: signalling features, "
                                             "report conversion, ping-pong")
    ap.add_argument("--root", default=None)
    ap.add_argument("--folds", type=int, default=5)
    ap.add_argument("--seeds", nargs="*", type=int, default=[1337, 1338, 1339])
    ap.add_argument("--conversion-within", type=float, default=2.0)
    a = ap.parse_args(argv)

    cfg = Config(deep_merge(capture_config("x", "y", HORIZONS), {
        "project": {"paths": {"processed": "data/processed_xcal",
                              "interim": "data/interim_xcal",
                              "reports": "reports_xcal",
                              "artifacts": "artifacts_xcal"}}}))
    paths = resolve_paths(cfg, a.root)
    out_dir = Path(paths["reports"]) / "tables"
    out_dir.mkdir(parents=True, exist_ok=True)
    feats, lab, ho, _ = load_xcal(paths)
    feats = feats.reset_index(drop=True)
    lab = lab.reset_index(drop=True)
    drives = feats["drive_id"].to_numpy()

    reports = all_reports(Path(paths["interim"]) / "reports_all.parquet")
    LOG.info("reports: %d (%d A3)", len(reports), int((reports["event_id"] == "A3").sum()))

    # ------------------------------------------------- 1. signalling ablation
    with timed("signalling features"):
        sig = build_signalling_features(feats, reports)
    base_names = [n for n in select_blocks(feats, BLOCKS) if n in feats.columns]
    F = pd.concat([feats, sig], axis=1)
    sets = {"rf+mob+hist": base_names,
            "+ signalling": base_names + list(sig.columns),
            "signalling only": list(sig.columns)}

    tags = _htags(HORIZONS)
    Y = np.column_stack([lab[f"y_ho_{t}"].to_numpy(float) for t in tags])
    M = np.column_stack([lab[f"m_ho_{t}"].to_numpy(bool) for t in tags])

    rows = []
    for seed in a.seeds:
        set_seed(seed)
        for sname, names in sets.items():
            tf = TabularTransform("robust", clip_sigma=8.0)
            tf.fit(F[names])
            X = pd.DataFrame(tf.transform(F[names]), columns=names, index=F.index)
            for k, h in enumerate(HORIZONS):
                sel = M[:, k].astype(bool)
                p = np.full(len(F), np.nan)
                p[sel] = kfold_oof(X.loc[sel], Y[sel, k].astype(int),
                                   drives[sel], a.folds, seed)
                r = scored(Y[sel, k].astype(int), p[sel], drives[sel],
                           f"handover@{h}s", seed)
                rows.append({"feature_set": sname, "seed": seed, "horizon_s": h, **r})
    abl = pd.DataFrame(rows)
    abl.to_csv(out_dir / "signalling_ablation_folds.csv", index=False)
    summ = (abl.groupby(["feature_set", "horizon_s"])
              [["positive_rate", "auprc", "auprc_lift", "auroc", "ece"]]
              .agg(["mean", "std"]).round(4))
    summ.columns = ["_".join(c) for c in summ.columns]
    summ = summ.reset_index()
    summ.to_csv(out_dir / "signalling_ablation.csv", index=False)
    (out_dir / "signalling_ablation.md").write_text(summ.to_markdown(index=False))
    LOG.info("\n%s", summ.to_string(index=False))

    # -------------------------------------------- 2. report conversion task
    conv_rows = []
    Xc, yc, gc = conversion_dataset(reports, ho, feats, a.conversion_within)
    if len(Xc) > 200:
        num = Xc.select_dtypes(include=[np.number])
        num = num.loc[:, num.notna().mean() > 0.5]
        drop = [c for c in num.columns if c.startswith(("y_", "m_", "t_to_next"))]
        num = num.drop(columns=drop, errors="ignore").fillna(num.median())
        LOG.info("conversion task: %d A3 reports, %.1f%% convert within %.1fs, "
                 "%d features", len(yc), 100 * yc.mean(), a.conversion_within,
                 num.shape[1])
        for seed in a.seeds:
            p = kfold_oof(num, yc, gc, a.folds, seed)
            conv_rows.append({"within_s": a.conversion_within, "seed": seed,
                              **scored(yc, p, gc, "A3 report -> handover", seed)})
        conv = pd.DataFrame(conv_rows)
        conv.to_csv(out_dir / "report_conversion.csv", index=False)
        (out_dir / "report_conversion.md").write_text(conv.round(4).to_markdown(index=False))
        LOG.info("\n%s", conv.round(4).to_string(index=False))

    # ----------------------------------------------- 3. ping-pong predictor
    y_pp = pingpong_labels(feats, ho)
    LOG.info("ping-pong target: %d positives of %d samples (%.2f%%)",
             int(y_pp.sum()), len(y_pp), 100 * y_pp.mean())
    pp_rows, envelopes = [], []
    if y_pp.sum() > 50:
        names = base_names + list(sig.columns)
        tf = TabularTransform("robust", clip_sigma=8.0)
        tf.fit(F[names])
        X = pd.DataFrame(tf.transform(F[names]), columns=names, index=F.index)
        for seed in a.seeds:
            p_pp = kfold_oof(X, y_pp, drives, a.folds, seed)
            pp_rows.append({"seed": seed, **scored(y_pp, p_pp, drives,
                                                   "ping-pong (dedicated)", seed)})
            # generic handover model ranking, for the same envelope
            p_ho = kfold_oof(X, Y[:, 1].astype(int), drives, a.folds, seed)
            for tag, p in (("dedicated ping-pong model", p_pp),
                           ("generic handover model", p_ho)):
                # Same alarm budgets for both rankers, so the comparison is
                # about WHAT is ranked, not how many alarms are allowed.
                thr = {f"alarm_top_{int(q*100)}pct": float(np.quantile(p, 1 - q))
                       for q in (0.02, 0.05, 0.10, 0.20, 0.40)}
                try:
                    env = benefit_envelope(ho, feats, p, thr)
                    env = env.assign(ranker=tag, seed=seed)
                    envelopes.append(env)
                except Exception as exc:                        # noqa: BLE001
                    LOG.warning("envelope failed for %s: %s", tag, exc)
        pp = pd.DataFrame(pp_rows)
        pp.to_csv(out_dir / "pingpong_predictor.csv", index=False)
        (out_dir / "pingpong_predictor.md").write_text(pp.round(4).to_markdown(index=False))
        LOG.info("\n%s", pp.round(4).to_string(index=False))
        if envelopes:
            env = pd.concat(envelopes, ignore_index=True)
            env.to_csv(out_dir / "benefit_envelope_dedicated.csv", index=False)
            (out_dir / "benefit_envelope_dedicated.md").write_text(
                env.round(4).to_markdown(index=False))

    write_json({"signalling_features": list(sig.columns),
                "conversion_within_s": a.conversion_within,
                "pingpong_window_s": PINGPONG_WINDOW_S,
                "seeds": a.seeds, "folds": a.folds},
               Path(paths["artifacts"]) / "stage16.json")


if __name__ == "__main__":
    main()

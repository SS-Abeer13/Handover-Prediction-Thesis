"""Stage 22 - experiments for the revision (review of 17 Sept 2026).

    python -m hoproj.pipeline.stage22_revision --exp all

Every number in the revised manuscript comes from a table this stage writes
to ``reports_rev/tables``. Nothing is transcribed by hand.

Experiments (reviewer concern in brackets)
  audit       row-time alignment of the 1 Hz export, dataset / hazard tables [C9, C4, C1]
  protocols   four splitting protocols x seven learners, fixed hyper-parameters [C1, C2]
  main        LOCO, nested 20-trial tuning, all learners + history baselines [C3, C8, C17]
  coherence   hazard vs independent heads, isotonic, cumulative max, PAV [C11]
  crc         risk-control frontier, 12 train/calib/test capture rotations [C10]
  ablation    feature blocks, lag 0 vs 1, re-establishment censoring [C9, C15, C18]
"""
from __future__ import annotations

import argparse
import json
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

from ..revision import evaluation as EV
from ..revision import models as MD
from ..revision.data import (CAPTURE_NAMES, EDGES, load_revision_data,
                             row_alignment_audit)
from ..utils import get_logger

warnings.filterwarnings("ignore")
LOG = get_logger("hoproj.stage22")

ROOT = Path(".")
PROC = ROOT / "data/processed_xcal"
SIG = ROOT / "data/rev/signalling.pkl"
REP = ROOT / "data/rev/reports_v2.pkl"
OUT = ROOT / "reports_rev/tables"
MAIN_BLOCKS = ["rf", "mobility", "history"]
SEEDS = [0, 1, 2]
N_TRIALS = 20


def save(df: pd.DataFrame, name: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT / f"{name}.csv", index=False)
    (OUT / f"{name}.md").write_text(df.round(4).to_markdown(index=False))
    LOG.info("wrote %s (%d rows)", name, len(df))


def data(lag=1, censor=False):
    return load_revision_data(PROC, SIG, lag=lag, censor_reest=censor, reports_pickle=REP)


# ------------------------------------------------------------------ learners
def learner(name: str, d, seed: int, params: dict | None = None):
    p = params or {}
    cols = list(d.X.columns)
    if name == "lgbm":
        return MD.HazardLGBM(seed=seed, **p)
    if name == "lgbm_indep":
        return MD.IndepLGBM(seed=seed, **p)
    if name == "lr":
        return MD.HazardLR(seed=seed, **p)
    if name == "mlp":
        return MD.HazardMLP(seed=seed, **p)
    if name in ("gru", "tcn", "transformer"):
        return MD.SeqHazard(arch=name, seed=seed, **p)
    if name == "a3":
        return MD.A3Rule(cols={"gap": cols.index("gap_serving_best_nbr"),
                               "streak": cols.index("nbr_better_streak_s"),
                               "off": cols.index("cfg_a3_offset_db"),
                               "hys": cols.index("cfg_hysteresis_db")})
    raise KeyError(name)


SEQ = {"gru", "tcn", "transformer"}
LABEL = {"lgbm": "LightGBM", "lgbm_indep": "LightGBM (independent heads)",
         "lr": "Logistic regression", "mlp": "MLP", "gru": "GRU", "tcn": "TCN",
         "transformer": "Transformer", "a3": "Event A3 rule (deployed parameters)",
         "dwell": "Dwell time only (LightGBM)", "history": "History block only (LightGBM)",
         "hawkes": "Hawkes-kernel intensity (LR)"}


class Design:
    """Feature matrices for one dataset, shared by every learner."""

    def __init__(self, d, blocks):
        self.d = d
        self.names = d.feats(blocks)
        allcols = list(d.X.columns)
        self.X = d.X[self.names].to_numpy(float)
        self.Xall = d.X.to_numpy(float)          # for the A3 rule (needs cfg columns)
        self.t_next = d.frame["t_next_ho_s"].to_numpy(float)
        self.Y = d.Y
        self._W = None
        self.allcols = allcols

    def W(self):
        if self._W is None:
            full = self.d.full
            self._W = MD.make_windows(self.X, self.d.frame, full[self.names].to_numpy(float),
                                      full[["capture", "t"]], L=10)
        return self._W

    def inputs(self, name):
        if name in SEQ:
            return self.W()
        if name == "a3":
            return self.Xall
        return self.X


def fit_predict(name, des: Design, fit, test, seed, params=None):
    m = learner(name, des.d, seed, params)
    Z = des.inputs(name)
    m.fit(Z[fit], des.t_next[fit])
    return m.predict(Z[test])


def tune(name, des: Design, fit, cal, seed) -> dict:
    """20-trial random search, scored on the fold's own calibration block."""
    space = {"lgbm": MD.HazardLGBM.space, "lgbm_indep": MD.HazardLGBM.space,
             "lr": MD.HazardLR.space, "mlp": MD.HazardMLP.space}.get(name, MD.SeqHazard.space)
    if name == "a3":
        return {}
    rng = np.random.default_rng(1000 + seed)
    best, best_p = -np.inf, {}
    from sklearn.metrics import average_precision_score
    for _ in range(N_TRIALS):
        p = MD.sample_params(space, rng)
        try:
            P = fit_predict(name, des, fit, cal, seed, p)
        except Exception as exc:                    # noqa: BLE001
            LOG.warning("trial failed %s %s: %s", name, p, exc)
            continue
        Yc = des.Y[cal]
        s = np.mean([average_precision_score(Yc[:, k], P[:, k]) for k in range(len(EDGES))
                     if len(np.unique(Yc[:, k])) == 2])
        if s > best:
            best, best_p = s, p
    return best_p


def _track_km(g: pd.DataFrame) -> float:
    """Great-circle track length over consecutive 1 Hz rows, not bridging gaps > 2 s."""
    g = g.sort_values("t")
    la, lo = np.radians(g["lat"].to_numpy()), np.radians(g["lon"].to_numpy())
    step = 2 * 6371.0088 * np.arcsin(np.sqrt(
        np.sin(np.diff(la) / 2) ** 2
        + np.cos(la[:-1]) * np.cos(la[1:]) * np.sin(np.diff(lo) / 2) ** 2))
    dt = np.diff(g["t"].to_numpy()) / np.timedelta64(1, "s")
    return float(np.nansum(np.where(dt <= 2, step, 0.0)))


# ------------------------------------------------------------------ experiments
def exp_audit():
    import pickle
    d = data()
    feats = pd.read_parquet(PROC / "features.parquet")
    feats["t"] = pd.to_datetime(feats["t"])
    save(row_alignment_audit(feats, d.events), "c9_row_alignment_audit")
    save(MD.hazard_table(d.frame["t_next_ho_s"].to_numpy()), "c4_hazard_prevalence_reconciled")
    fr = d.frame
    sess = []
    for cap, g in fr.groupby("capture"):
        ev = d.events[d.events.capture == cap]
        raw = feats[feats.capture == cap]
        sess.append({"capture": CAPTURE_NAMES[cap], "sessions": 1,
                     "chunks_180s": raw["drive_id"].nunique(), "rows_qc": len(raw),
                     "rows_usable": len(g), "handovers_all": len(ev),
                     "handovers_in_qc_chunks": int(pd.read_parquet(PROC / "handovers.parquet")
                                                   .query("capture == @cap").shape[0]),
                     "reestablishments": int((d.reest.capture == cap).sum()),
                     "duration_min": round((raw["t"].max() - raw["t"].min()).total_seconds() / 60, 1),
                     # NB: two distances, and the draft quoted them interchangeably (78 km / 95 km).
                     # km_driven is the whole retained recording; km_usable covers only the rows that
                     # survive to the modelling frame, which is 16 % shorter. Always label which.
                     "km_driven": round(_track_km(raw), 1),
                     "km_usable": round(float(g["km_step"].sum()), 1),
                     "mean_speed_kmh": round(float(raw["speed_kmh"].mean()), 1)})
    save(pd.DataFrame(sess), "c1_dataset_sessions")
    save(pd.DataFrame([{"horizon_s": e, "prevalence": v, "constant_negative_accuracy": 1 - v}
                       for e, v in d.info["prevalence"].items()]), "c4_prevalence")
    rc = d.reest.groupby(["capture", "cause"]).size().unstack(fill_value=0).reset_index()
    save(rc, "c15_reestablishment_causes")
    # how close are re-establishments to handover commands?
    rows = []
    for cap, g in d.reest.groupby("capture"):
        et = d.events.loc[d.events.capture == cap, "t"].sort_values().to_numpy()
        for r in g.itertuples():
            j = np.searchsorted(et, np.datetime64(r.t))
            prev = (np.datetime64(r.t) - et[j - 1]) / np.timedelta64(1, "ms") if j > 0 else np.nan
            rows.append({"capture": cap, "cause": r.cause, "ms_since_prev_ho_command": prev})
    x = pd.DataFrame(rows)
    x["within_1s_of_command"] = x["ms_since_prev_ho_command"] <= 1000
    save(x.groupby("cause").agg(n=("capture", "size"),
                                median_ms_since_command=("ms_since_prev_ho_command", "median"),
                                share_within_1s=("within_1s_of_command", "mean")).reset_index(),
         "c15_reestablishment_timing")
    save(pd.DataFrame([{"rows_usable": len(fr), "rows_with_competing_reest_first": int(fr["competing_first"].sum()),
                        "long_format_rows": int(MD.hazard_table(fr["t_next_ho_s"].to_numpy())["at_risk"].sum())}]),
         "c4_long_format_size")


def exp_protocols(learners, lag=1, tag=""):
    d = data(lag=lag)
    des = Design(d, MAIN_BLOCKS)
    rows = []
    for proto, fn in EV.PROTOCOLS.items():
        folds = fn(d.frame)
        for name in learners:
            seeds = [0] if name == "a3" else SEEDS[:2 if name in SEQ else 3]
            for seed in seeds:
                t0 = time.time()
                P = np.full(des.Y.shape, np.nan)
                for f in folds:
                    tr = f.fit | f.calib
                    P[f.test] = fit_predict(name, des, tr, f.test, seed)
                ok = ~np.isnan(P[:, 0])
                hm = EV.horizon_metrics(des.Y[ok], P[ok])
                hm.insert(0, "protocol", proto)
                hm.insert(1, "learner", name)
                hm.insert(2, "seed", seed)
                rows.append(hm)
                LOG.info("%s %s seed %d: AUPRC@1s %.3f (%.0fs)", proto, name, seed,
                         hm.loc[hm.horizon_s == 1.0, "auprc"].iloc[0], time.time() - t0)
            save(pd.concat(rows), f"c2_protocol_ladder_raw{tag}")
    raw = pd.concat(rows)
    summ = raw.groupby(["protocol", "learner", "horizon_s"])[["auprc", "lift", "auroc", "ece"]].mean().reset_index()
    save(summ, f"c2_protocol_ladder{tag}")
    return summ


def inflation_table(summ: pd.DataFrame, tag=""):
    piv = summ.pivot_table(index=["learner", "horizon_s"], columns="protocol", values="auprc").reset_index()
    for ref in ("loco", "blocked_purged"):
        piv[f"inflation_random_vs_{ref}_%"] = 100 * (piv["random_row"] / piv[ref] - 1)
    piv["inflation_chunk_vs_loco_%"] = 100 * (piv["chunk_grouped"] / piv["loco"] - 1)
    for proto in EV.PROTOCOLS:
        piv[f"rank_{proto}"] = piv.groupby("horizon_s")[proto].rank(ascending=False)
    save(piv, f"c2_inflation_by_horizon{tag}")


def exp_main(learners):
    d = data()
    des = Design(d, MAIN_BLOCKS)
    folds = EV.loco(d.frame)
    oof, chosen = {}, []
    extra = {"dwell": ["t_since_prev_ho_s", "has_prev_ho"], "history": d.names["history"]}
    for name in learners + list(extra):
        base = name if name not in extra else "lgbm"
        cols = None if name not in extra else [des.names.index(c) for c in extra[name]]
        seeds = [0] if name == "a3" else SEEDS
        Ps = []
        for seed in seeds:
            P = np.full(des.Y.shape, np.nan)
            for f in folds:
                t0 = time.time()
                if cols is not None:
                    sub = Design(d, MAIN_BLOCKS)
                    sub.X = des.X[:, cols]
                    sub.names = [des.names[i] for i in cols]
                    D = sub
                else:
                    D = des
                params = {} if name in ("a3",) else tune(base, D, f.fit, f.calib, seed)
                chosen.append({"learner": name, "fold": f.name, "seed": seed, "params": json.dumps(params)})
                P[f.test] = fit_predict(base, D, f.fit | f.calib, f.test, seed, params)
                LOG.info("main %s %s seed %d done (%.0fs)", name, f.name, seed, time.time() - t0)
            Ps.append(P)
            np.save(OUT / f"oof_{name}_s{seed}.npy", P)
        oof[name] = np.mean(Ps, axis=0)
        np.save(OUT / f"oof_{name}.npy", oof[name])
        save(pd.DataFrame(chosen), "c17_tuned_params")
    # hawkes-kernel baseline: LR hazard on exponential kernel sums of past commands
    oof["hawkes"] = hawkes_baseline(d, folds)
    np.save(OUT / "oof_hawkes.npy", oof["hawkes"])
    summarise_main(d, oof)


def hawkes_baseline(d, folds):
    fr = d.frame
    feats = np.zeros((len(fr), 3))
    for cap, g in fr.groupby("capture"):
        t0 = g["t"].min() - pd.to_timedelta(g["ts"].min(), unit="s")
        et = ((d.events.loc[d.events.capture == cap, "t"] - t0).dt.total_seconds()).to_numpy()
        ts = g["ts"].to_numpy()
        for j, beta in enumerate((0.1, 0.3, 1.0)):
            s = np.zeros(len(ts))
            for i, t in enumerate(ts):
                past = et[(et < t) & (et > t - 60)]
                s[i] = np.exp(-beta * (t - past)).sum()
            feats[g.index, j] = s
    P = np.full(d.Y.shape, np.nan)
    tn = fr["t_next_ho_s"].to_numpy()
    for f in folds:
        m = MD.HazardLR(C=1.0).fit(feats[f.fit | f.calib], tn[f.fit | f.calib])
        P[f.test] = m.predict(feats[f.test])
    return P


def summarise_main(d, oof: dict):
    fr, Y = d.frame, d.Y
    rows, per_cap, strata = [], [], []
    for name, P in oof.items():
        hm = EV.horizon_metrics(Y, P)
        bs = EV.block_bootstrap(fr, Y, P, n=300)
        hm["auprc_ci_low"] = np.nanquantile(bs, 0.025, axis=0)[: len(hm)]
        hm["auprc_ci_high"] = np.nanquantile(bs, 0.975, axis=0)[: len(hm)]
        hm.insert(0, "learner", LABEL.get(name, name))
        rows.append(hm)
        for cap in sorted(fr["capture"].unique()):
            m = (fr["capture"] == cap).to_numpy()
            h = EV.horizon_metrics(Y, P, m)
            h.insert(0, "learner", LABEL.get(name, name))
            h.insert(1, "held_out_capture", CAPTURE_NAMES[cap])
            per_cap.append(h)
        # C8: burst strata
        for lab, m in (("quiet (no handover in previous 10 s)", ~fr["in_burst"].to_numpy()),
                       ("in burst (handover 2-10 s earlier)", fr["in_burst"].to_numpy())):
            h = EV.horizon_metrics(Y, P, m)
            h.insert(0, "learner", LABEL.get(name, name))
            h.insert(1, "stratum", lab)
            strata.append(h)
    save(pd.concat(rows), "c3_main_loco")
    pc = pd.concat(per_cap)
    save(pc, "c3_main_loco_per_capture")
    save(pd.concat(strata), "c8_burst_strata")
    # paired per-capture deltas vs LightGBM (n = 4 captures; exact sign test)
    from scipy.stats import binomtest
    ref = pc[pc.learner == "LightGBM"].set_index(["held_out_capture", "horizon_s"])
    out = []
    for name, g in pc.groupby("learner"):
        if name == "LightGBM":
            continue
        g = g.set_index(["held_out_capture", "horizon_s"])
        for h in EDGES:
            a = ref.xs(h, level=1)["auprc"]
            b = g.xs(h, level=1)["auprc"].reindex(a.index)
            dlt = (a - b).dropna()
            wins = int((dlt > 0).sum())
            out.append({"comparator": name, "horizon_s": h, "n_captures": len(dlt),
                        "mean_delta_auprc_lgbm_minus_comparator": dlt.mean(),
                        "min_delta": dlt.min(), "max_delta": dlt.max(),
                        "lgbm_wins": wins,
                        "exact_sign_test_p_two_sided": binomtest(wins, len(dlt)).pvalue if len(dlt) else np.nan})
    save(pd.DataFrame(out), "c3_paired_per_capture")
    # event-level metrics at 5 % FPR (threshold from each fold's calibration block)
    P = oof["lgbm"]
    thr_rows = []
    folds = EV.loco(fr)
    ev_parts = []
    for f in folds:
        # threshold from in-fold calibration predictions (refit-free proxy: use OOF of other folds is leaky);
        # recompute calibration predictions with the fold's model
        des = Design(d, MAIN_BLOCKS)
        Pc = fit_predict("lgbm", des, f.fit, f.calib, 0)
        thr = np.array([EV.thr_at_fpr(des.Y[f.calib, k], Pc[:, k], 0.05) for k in range(len(EDGES))])
        thr_rows.append({"fold": f.name, **{f"thr_{e}": t for e, t in zip(EDGES, thr)}})
        em = EV.event_metrics(fr, P, thr, d.events, f.test)
        em.insert(0, "held_out", f.name)
        ev_parts.append(em)
    em = pd.concat(ev_parts)
    pooled = em.groupby("horizon_s").agg(events=("events", "sum"), resolvable=("resolvable_on_grid", "sum"),
                                         detected=("detected", "sum"), fa=("false_alarm_episodes", "sum"),
                                         hours=("hours", "sum"), km=("km", "sum"),
                                         lead_median_s=("lead_median_s", "median")).reset_index()
    pooled["detection_rate"] = pooled["detected"] / pooled["events"]
    pooled["grid_ceiling"] = pooled["resolvable"] / pooled["events"]
    pooled["false_alarms_per_hour"] = pooled["fa"] / pooled["hours"]
    pooled["false_alarms_per_km"] = pooled["fa"] / pooled["km"]
    save(em, "c18_event_metrics_per_capture_fpr5")
    save(pooled, "c18_event_metrics_pooled_fpr5")


def exp_coherence():
    from sklearn.isotonic import IsotonicRegression
    from sklearn.metrics import average_precision_score
    from ..models.monotone import pava_rows
    d = data()
    des = Design(d, MAIN_BLOCKS)
    arms = {k: np.full(des.Y.shape, np.nan) for k in
            ("independent", "independent + cumulative max", "independent + PAV",
             "independent + isotonic", "independent + isotonic + PAV", "hazard")}
    # Two violation rates exist and they answer different questions.  A deployed system is
    # ONE fit, so the per-seed rate is what a practitioner meets; averaging predictions over
    # seeds is an ensemble that smooths violations away.  Both are reported, per arm, and the
    # manuscript quotes the single-fit rate throughout [C11].
    per_seed = {k: [] for k in arms}
    for seed in SEEDS:
        one = {k: np.full(des.Y.shape, np.nan) for k in arms}
        for f in EV.loco(d.frame):
            ind = MD.IndepLGBM(seed=seed).fit(des.X[f.fit], des.t_next[f.fit])
            Pt, Pc = ind.predict(des.X[f.test]), ind.predict(des.X[f.calib])
            iso = np.column_stack([IsotonicRegression(out_of_bounds="clip", y_min=0, y_max=1)
                                   .fit(Pc[:, k], des.Y[f.calib, k]).predict(Pt[:, k])
                                   for k in range(len(EDGES))])
            hz = MD.HazardLGBM(seed=seed).fit(des.X[f.fit], des.t_next[f.fit]).predict(des.X[f.test])
            outs = {"independent": Pt, "independent + cumulative max": np.maximum.accumulate(Pt, axis=1),
                    "independent + PAV": pava_rows(Pt), "independent + isotonic": iso,
                    "independent + isotonic + PAV": pava_rows(iso), "hazard": hz}
            for k, v in outs.items():
                one[k][f.test] = v
                cur = arms[k][f.test]
                arms[k][f.test] = np.where(np.isnan(cur), v / len(SEEDS), cur + v / len(SEEDS))
        for k, P in one.items():
            per_seed[k].append({"arm": k, "seed": seed, **EV.violations(P)})
    # Conclusions in Section 5.4 rest on ECE differences of 0.005-0.035.  Round 3 added a
    # PAIRED bootstrap over 180-second blocks; round 4's reviewers were right that this is
    # pseudo-replication: Section 5.3 of this same thesis proves those blocks are dependent
    # (splitting on them inflates AUPRC by 13 %), so resampling them deflates the standard
    # error and manufactures intervals that "exclude zero".  The block bootstrap is kept as
    # a WITHIN-campaign descriptive interval and is no longer the basis of any claim; the
    # comparison that carries a conclusion is now the four per-campaign paired differences,
    # one per independent unit, reported in full with no test attached.
    rows, vio = [], []
    for k, P in arms.items():
        hm = EV.horizon_metrics(des.Y, P)
        hm.insert(0, "arm", k)
        for stat, tag in ((average_precision_score, "auprc"), (EV.ece, "ece")):
            bs = EV.block_bootstrap(d.frame, des.Y, P, n=300, stat=stat)
            hm[f"{tag}_ci_low"] = np.nanquantile(bs, 0.025, axis=0)[: len(hm)]
            hm[f"{tag}_ci_high"] = np.nanquantile(bs, 0.975, axis=0)[: len(hm)]
        rows.append(hm)
        ps = pd.DataFrame(per_seed[k])
        vio.append({"arm": k,
                    **{f"{c}_single_fit": float(ps[c].mean()) for c in
                       ("rows_violating", "pairs_violating", "mean_violation_if_any",
                        "p95_violation_if_any", "max_violation")},
                    **{f"{c}_seed_mean": v for c, v in EV.violations(P).items()}})
    save(pd.concat(rows), "c11_coherence_metrics")
    save(pd.DataFrame(vio), "c11_coherence_violations")

    # ---- per-campaign metrics for every coherence arm.  Section 5.4 promised these in
    # Appendix A and never printed them, and the per-campaign sign was quoted from the
    # TUNED arm while the pooled number came from this one, which is how the manuscript
    # came to say the hazard arm won pooled and lost 0 of 4.  Same arm, same row set now.
    cap = d.frame["capture"].to_numpy()
    percap = []
    for k, P in arms.items():
        for c in np.unique(cap):
            sel = cap == c
            hm = EV.horizon_metrics(des.Y[sel], P[sel])
            hm.insert(0, "capture", CAPTURE_NAMES.get(c, c))
            hm.insert(0, "arm", k)
            percap.append(hm)
    percap = pd.concat(percap, ignore_index=True)
    save(percap, "c11_coherence_per_capture")

    # ---- paired differences, two ways, clearly separated.
    #  (a) per-campaign: four independent units, reported individually, no test.
    #  (b) within-campaign block bootstrap: descriptive only, retained for continuity.
    pair = []
    caps = list(np.unique(cap))
    for k in arms:
        if k == "hazard":
            continue
        for stat, tag in ((average_precision_score, "auprc"), (EV.ece, "ece")):
            bh = EV.block_bootstrap(d.frame, des.Y, arms["hazard"], n=300, seed=7, stat=stat)
            bk = EV.block_bootstrap(d.frame, des.Y, arms[k], n=300, seed=7, stat=stat)
            dif = bh - bk                                # hazard minus control
            for ki, h in enumerate(EDGES):
                per = []
                for c in caps:
                    sel = cap == c
                    y, ph, pk = des.Y[sel, ki], arms["hazard"][sel, ki], arms[k][sel, ki]
                    if len(np.unique(y)) < 2:
                        per.append(np.nan)
                        continue
                    per.append(float(stat(y, ph) - stat(y, pk)))
                per = np.array(per, float)
                wins = int(np.nansum(per < 0)) if tag == "ece" else int(np.nansum(per > 0))
                pair.append({
                    "arm": k, "metric": tag, "horizon_s": h,
                    "difference": float(np.nanmean(dif[:, ki])),
                    "block_ci_low": float(np.nanquantile(dif[:, ki], 0.025)),
                    "block_ci_high": float(np.nanquantile(dif[:, ki], 0.975)),
                    **{f"campaign_{i + 1}": (None if np.isnan(v) else float(v))
                       for i, v in enumerate(per)},
                    "campaigns_favouring_hazard": wins,
                    "n_campaigns": int(np.isfinite(per).sum()),
                    "sign_consistent": bool(np.isfinite(per).all()
                                            and (np.all(per > 0) or np.all(per < 0))),
                    # a sign test on four paired units cannot go below 0.125, so the best
                    # available statement is "same sign on all four", never "significant".
                    "min_attainable_p": 0.125,
                })
    save(pd.DataFrame(pair), "c11_paired_differences")
    save(pd.concat([pd.DataFrame(v) for v in per_seed.values()], ignore_index=True),
         "c11_violations_single_seed")


def exp_crc(h_idx=(1, 3)):
    d = data()
    des = Design(d, MAIN_BLOCKS)
    fr = d.frame
    caps = sorted(fr["capture"].unique())
    alphas = [0.05, 0.10, 0.15, 0.20, 0.30]
    grid = np.linspace(0, 1, 1001)
    rows = []
    for test in caps:
        for cal in caps:
            if cal == test:
                continue
            tr = ~fr["capture"].isin([test, cal]).to_numpy()
            te = (fr["capture"] == test).to_numpy()
            ca = (fr["capture"] == cal).to_numpy()
            m = MD.HazardLGBM(seed=0).fit(des.X[tr], des.t_next[tr])
            Pc, Pt = m.predict(des.X[ca]), m.predict(des.X[te])
            Pc_full = np.full(des.Y.shape, np.nan)
            Pc_full[ca] = Pc
            Pt_full = np.full(des.Y.shape, np.nan)
            Pt_full[te] = Pt
            for k in h_idx:
                yc, yt = des.Y[ca, k], des.Y[te, k]
                # the event-level loss the abstract and Section 1.3 actually promise: a
                # handover is caught if ANY usable row in its lead window alarms, and an
                # event with no usable row counts as missed [C10, round 3]
                cu_e, cs_e = EV.event_scores(fr, np.where(ca, Pc_full[:, k], np.nan),
                                             d.events, ca, EDGES[k])
                tu_e, ts_e = EV.event_scores(fr, np.where(te, Pt_full[:, k], np.nan),
                                             d.events, te, EDGES[k])
                for a in alphas:
                    thr, n = EV.crc_threshold(fr.loc[ca, "drive_id"].to_numpy(), yc, Pc[:, k], a, grid)
                    alarm = Pt[:, k] >= thr
                    units = fr.loc[te, "drive_id"].to_numpy()
                    losses = [((~alarm) & (yt == 1) & (units == u)).sum() / max(((yt == 1) & (units == u)).sum(), 1)
                              for u in np.unique(units)]
                    thr_e, n_e = EV.crc_threshold(cu_e, np.ones(len(cs_e), int), cs_e, a, grid)
                    feas_e = bool(np.isfinite(thr_e))
                    # An infeasible target is met only by the degenerate "alarm on every
                    # row" threshold, which the row-level table used to report as a loss of
                    # zero.  Report it as missing instead [C10, round 3].
                    if feas_e:
                        miss_e = ts_e < thr_e
                        loss_e = [miss_e[tu_e == u].mean() for u in np.unique(tu_e)]
                        m_e, u_e = float(miss_e.mean()), float(np.mean(loss_e))
                        ar_e = float((Pt[:, k] >= thr_e).mean())
                    else:
                        m_e = u_e = ar_e = np.nan
                    rows.append({"horizon_s": EDGES[k], "alpha": a, "test": CAPTURE_NAMES[test],
                                 "calib": CAPTURE_NAMES[cal], "n_calib_units": n,
                                 "floor_1_over_n_plus_1": 1 / (n + 1), "feasible": np.isfinite(thr),
                                 "threshold": thr, "alarm_rate": alarm.mean(),
                                 "realised_miss_rate_rows": ((~alarm) & (yt == 1)).sum() / max((yt == 1).sum(), 1),
                                 "mean_unit_loss": float(np.mean(losses)),
                                 "units_with_loss_le_alpha": float(np.mean(np.array(losses) <= a)),
                                 "n_events_test": int(len(ts_e)),
                                 "feasible_events": feas_e,
                                 "threshold_events": thr_e,
                                 "alarm_rate_events": ar_e,
                                 "realised_miss_rate_events": m_e,
                                 "mean_unit_loss_events": u_e,
                                 # the floor no threshold can beat: events with no usable
                                 # row in their lead window are missed by construction
                                 "unresolvable_event_share": float((ts_e == -np.inf).mean()),
                                 # expressibility is decided on the CALIBRATION set, the realised
                                 # loss on the test set; the two shares differ by campaign, which is
                                 # precisely the non-exchangeability this section is testing
                                 "unresolvable_event_share_calib": float((cs_e == -np.inf).mean())})
    raw = pd.DataFrame(rows)
    save(raw, "c10_crc_rotations")
    summ = raw.groupby(["horizon_s", "alpha"]).agg(
        rotations=("test", "size"), feasible=("feasible", "mean"),
        alarm_rate_mean=("alarm_rate", "mean"), mean_unit_loss=("mean_unit_loss", "mean"),
        mean_unit_loss_max=("mean_unit_loss", "max"),
        feasible_events=("feasible_events", "mean"),
        alarm_rate_events_mean=("alarm_rate_events", "mean"),
        mean_unit_loss_events=("mean_unit_loss_events", "mean"),
        realised_miss_events=("realised_miss_rate_events", "mean"),
        unresolvable_event_share=("unresolvable_event_share", "mean"),
        unresolvable_event_share_calib=("unresolvable_event_share_calib", "mean"),
        rotations_with_mean_loss_le_alpha=("mean_unit_loss", lambda s: 0),
    ).reset_index()
    summ["rotations_with_mean_loss_le_alpha"] = raw.assign(ok=raw.mean_unit_loss <= raw.alpha) \
        .groupby(["horizon_s", "alpha"])["ok"].mean().to_numpy()
    summ["rotations_with_event_loss_le_alpha"] = \
        raw.assign(ok=raw.mean_unit_loss_events <= raw.alpha) \
        .groupby(["horizon_s", "alpha"])["ok"].mean().to_numpy()
    save(summ, "c10_crc_frontier")
    # exchangeable reference: calibration and test units drawn from the same pool
    rng = np.random.default_rng(0)
    rows = []
    folds = EV.loco(fr)
    P = np.load(OUT / "oof_lgbm.npy") if (OUT / "oof_lgbm.npy").exists() else None
    if P is not None:
        units = fr["drive_id"].to_numpy()
        uu = np.unique(units)
        for rep in range(200):
            perm = rng.permutation(uu)
            cal_u, te_u = perm[: len(uu) // 2], perm[len(uu) // 2:]
            ca, te = np.isin(units, cal_u), np.isin(units, te_u)
            for k in h_idx:
                for a in alphas:
                    thr, n = EV.crc_threshold(units[ca], des.Y[ca, k], P[ca, k], a, grid)
                    alarm = P[te, k] >= thr
                    yt = des.Y[te, k]
                    losses = [((~alarm) & (yt == 1) & (units[te] == u)).sum() /
                              max(((yt == 1) & (units[te] == u)).sum(), 1) for u in te_u]
                    rows.append({"horizon_s": EDGES[k], "alpha": a, "rep": rep, "n_calib_units": n,
                                 "mean_unit_loss": np.mean(losses), "alarm_rate": alarm.mean()})
        ex = pd.DataFrame(rows).groupby(["horizon_s", "alpha"]).agg(
            n_calib_units=("n_calib_units", "first"), mean_unit_loss=("mean_unit_loss", "mean"),
            alarm_rate=("alarm_rate", "mean")).reset_index()
        save(ex, "c10_crc_pooled_chunk_split")


def exp_selective_lag():
    """C9 (round 3): separate the cost of the LEAK from the cost of the REPAIR.

    The v2 repair lags every export feature by one row.  That removes the
    contaminated serving-cell assignment but also discards one second of GPS
    kinematics, which the end-of-second flip cannot contaminate.  Four arms, one
    common row set, identical folds, seeds and learner:

      none         v1 alignment, nothing lagged
      neighbour    only the neighbour/gap columns (and cfg) lagged - the arm a
                   reader assumes when told "lag the cell-identity features"
      assignment   every serving-relative column lagged, GPS kept at row t
      all          v2 as reported everywhere else in this thesis
    """
    from ..revision.data import RevData
    arms = {}
    for scope in ("none", "neighbour", "serving", "assignment", "all"):
        arms[scope] = load_revision_data(PROC, SIG, lag=0 if scope == "none" else 1,
                                         reports_pickle=REP, lag_scope=scope)
    # one common row set, so the four AUPRCs are comparable
    keys = None
    for d in arms.values():
        k = set(map(tuple, d.frame[["capture", "t"]].to_numpy()))
        keys = k if keys is None else (keys & k)
    LOG.info("selective lag: common row set %d (arm sizes %s)", len(keys),
             {k: len(v.frame) for k, v in arms.items()})

    def restrict(d):
        m = np.array([tuple(r) in keys for r in d.frame[["capture", "t"]].to_numpy()])
        return RevData(d.frame[m].reset_index(drop=True), d.X[m].reset_index(drop=True),
                       d.names, d.events, d.reest, dict(d.info), d.full)

    rows = []
    for scope, d0 in arms.items():
        d = restrict(d0)
        des = Design(d, MAIN_BLOCKS)
        n_lag = int(d0.info["n_lagged"])
        for learner in ("lgbm", "a3"):
            for seed in (SEEDS if learner == "lgbm" else [0]):
                P = np.full(des.Y.shape, np.nan)
                for f in EV.loco(d.frame):
                    P[f.test] = fit_predict(learner, des, f.fit | f.calib, f.test, seed)
                hm = EV.horizon_metrics(des.Y, P)
                hm.insert(0, "arm", scope)
                hm.insert(1, "learner", LABEL[learner])
                hm.insert(2, "columns_lagged", n_lag)
                hm.insert(3, "seed", seed)
                rows.append(hm)
        LOG.info("selective lag: %s done (%d of %d columns lagged)", scope, n_lag,
                 int(d0.info["n_export"]))
    raw = pd.concat(rows)
    save(raw, "c9sel_lag_scope_raw")
    agg = (raw.groupby(["arm", "learner", "columns_lagged", "horizon_s"])
           [["n", "prevalence", "auprc", "lift", "auroc"]].mean().round(4).reset_index())
    order = {"none": 0, "neighbour": 1, "serving": 2, "assignment": 3, "all": 4}
    agg = agg.sort_values(["learner", "horizon_s", "arm"],
                          key=lambda c: c.map(order) if c.name == "arm" else c)
    save(agg, "c9sel_lag_scope")

    # the decomposition the manuscript quotes
    lg = agg[agg.learner == LABEL["lgbm"]].set_index(["arm", "horizon_s"])
    dec = []
    for h in (1.0, 5.0):
        a = {k: float(lg.loc[(k, h), "auprc"]) for k in order}
        dec.append({"horizon_s": h,
                    "v1 (nothing lagged)": round(a["none"], 3),
                    "neighbour and gap columns lagged": round(a["neighbour"], 3),
                    "serving-cell radio scalars lagged": round(a["serving"], 3),
                    "all serving-relative lagged (GPS live)": round(a["assignment"], 3),
                    "v2 (everything lagged)": round(a["all"], 3),
                    "share of the v1-v2 drop caused by the neighbour and gap columns alone":
                        round((a["none"] - a["neighbour"]) / (a["none"] - a["all"]), 3),
                    "share caused by the serving-cell radio scalars alone":
                        round((a["none"] - a["serving"]) / (a["none"] - a["all"]), 3),
                    "share attributable to lagging GPS as well":
                        round((a["assignment"] - a["all"]) / (a["none"] - a["all"]), 3)})
    save(pd.DataFrame(dec), "c9sel_lag_decomposition")


def exp_ablation():
    rows = []
    specs = [("rf", ["rf"], 1, False), ("rf+mobility", ["rf", "mobility"], 1, False),
             ("rf+mobility+history (main)", MAIN_BLOCKS, 1, False),
             ("history only", ["history"], 1, False),
             ("signalling only", ["signalling"], 1, False),
             ("rf+mobility+history+signalling", MAIN_BLOCKS + ["signalling"], 1, False),
             ("main, NO lag (v1 alignment)", MAIN_BLOCKS, 0, False),
             ("rf only, NO lag", ["rf"], 0, False),
             ("main, re-establishment censored", MAIN_BLOCKS, 1, True)]
    cache = {}
    for lab, blocks, lag, cens in specs:
        key = (lag, cens)
        if key not in cache:
            cache[key] = data(lag=lag, censor=cens)
        d = cache[key]
        des = Design(d, blocks)
        for seed in SEEDS:
            P = np.full(des.Y.shape, np.nan)
            for f in EV.loco(d.frame):
                P[f.test] = fit_predict("lgbm", des, f.fit | f.calib, f.test, seed)
            hm = EV.horizon_metrics(des.Y, P)
            hm.insert(0, "variant", lab)
            hm.insert(1, "seed", seed)
            rows.append(hm)
        LOG.info("ablation %s done", lab)
    raw = pd.concat(rows)
    save(raw, "c18_ablation_raw")
    save(raw.groupby(["variant", "horizon_s"])[["n", "prevalence", "auprc", "lift", "auroc", "ece"]]
         .agg(["mean", "std"]).round(4).pipe(lambda x: x.set_axis(["_".join(c) for c in x.columns], axis=1))
         .reset_index(), "c18_ablation")
    # single-feature AUROC (lagged, orientation-free) and dwell direction
    d = cache[(1, False)]
    from sklearn.metrics import roc_auc_score
    sf = []
    for c in d.X.columns:
        x = d.X[c].to_numpy(float)
        ok = np.isfinite(x)
        if ok.sum() < 1000 or np.nanstd(x) == 0:
            continue
        a = roc_auc_score(d.Y[ok, 1], x[ok])
        sf.append({"feature": c, "auroc_1s": max(a, 1 - a),
                   "direction": "higher -> more likely" if a >= 0.5 else "lower -> more likely",
                   "coverage": ok.mean()})
    save(pd.DataFrame(sf).sort_values("auroc_1s", ascending=False), "c14_single_feature_auroc")
    fr = d.frame
    bins = [0, 2, 3, 4, 5, 7, 10, 15, 20, 30, 60, 601]
    dd = fr.assign(dwell_bin=pd.cut(fr["t_since_prev_ho_s"], bins, right=False))
    save(dd.groupby("dwell_bin").agg(n=("y_1", "size"), p_ho_1s=("y_1", "mean"),
                                     p_ho_5s=("y_4", "mean")).reset_index().astype({"dwell_bin": str}),
         "c8_dwell_direction")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--exp", nargs="+", default=["all"])
    ap.add_argument("--learners", nargs="*",
                    default=["a3", "lr", "lgbm", "mlp", "gru", "tcn", "transformer"])
    a = ap.parse_args(argv)
    OUT.mkdir(parents=True, exist_ok=True)
    ex = set(a.exp)
    if ex & {"audit", "all"}:
        exp_audit()
    if ex & {"protocols", "all"}:
        inflation_table(exp_protocols(a.learners))
    if ex & {"protocols_lag0"}:
        inflation_table(exp_protocols(["lgbm", "lr", "gru"], lag=0, tag="_lag0"), tag="_lag0")
    if ex & {"main", "all"}:
        exp_main(a.learners)
    if ex & {"coherence", "all"}:
        exp_coherence()
    if ex & {"crc", "all"}:
        exp_crc()
    if ex & {"ablation", "all"}:
        exp_ablation()
    if ex & {"selective_lag", "all"}:
        exp_selective_lag()


if __name__ == "__main__":
    main()

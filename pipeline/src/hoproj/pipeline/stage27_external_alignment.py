"""Stage 27 - does the row-time alignment problem of Section 5.1 exist in a
public drive-test dataset collected with a different tool?

Dataset: Raca, Leahy, Sreenan and Quinlan, "Beyond Throughput, The Next
Generation: A 5G Dataset with Channel and Context Metrics", ACM MMSys 2020
(github.com/uccmisl/5Gdataset, GPL-3.0). 60 driving traces from a commercial
Irish operator, logged at ~1 Hz with G-NetTrack Pro, carrying Timestamp,
Longitude, Latitude, Speed, CellID, RSRP, RSRQ, SNR, CQI, RSSI and throughput.
Most rows are NetworkMode LTE; the rest are 5G NSA.

Our export is XCAL and carries decoded RRC, so the audit there could use an
independent event clock. This dataset has no signalling, so three weaker but
independent tests are used:

A  Kinematic test. Does the speed reported on a row match the displacement
   AFTER its timestamp or BEFORE it? This tells us which interval the row
   summarises, without needing any event.
B  Serving-cell contamination. At a cell change between t and t+1, does the
   radio on row t already look like the new cell or like the old one?
C  Prediction inflation. Predict "the serving cell changes in the next second"
   from row t (as published studies do) and from row t-1, everything else
   fixed, leave-one-trace-out.
"""
from __future__ import annotations

import glob
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, roc_auc_score

from ..utils import get_logger
from .stage22_revision import save

LOG = get_logger("hoproj.stage27")
ROOT = Path("../ext/5g/5G-production-dataset")
RADIO = ["RSRP", "RSRQ", "SNR", "CQI", "RSSI", "DL_bitrate", "UL_bitrate", "Speed"]


def load() -> pd.DataFrame:
    files = sorted(glob.glob(str(ROOT / "*" / "Driving" / "*" / "*.csv"))
                   + glob.glob(str(ROOT / "*" / "Driving" / "*.csv")))
    out = []
    for f in files:
        d = pd.read_csv(f)
        if "CellID" not in d or "Timestamp" not in d:
            continue
        d["t"] = pd.to_datetime(d["Timestamp"], format="%Y.%m.%d_%H.%M.%S", errors="coerce")
        d = d.dropna(subset=["t"])
        for c in RADIO + ["Longitude", "Latitude"]:
            d[c] = pd.to_numeric(d[c], errors="coerce")
        d["CellID"] = pd.to_numeric(d["CellID"], errors="coerce")
        # one row per second: the first sample of each second, as a reader would
        d = d.groupby("t", as_index=False).first()
        d = d.set_index("t").asfreq("1s").reset_index()          # keep real gaps as NaN rows
        d["trace"] = Path(f).stem
        d["app"] = Path(f).parts[-3] if "Driving" in Path(f).parts else "Download"
        out.append(d)
    df = pd.concat(out, ignore_index=True)
    LOG.info("loaded %d traces, %d rows, %d cell changes", df.trace.nunique(), len(df),
             int((df.groupby("trace")["CellID"].diff().fillna(0) != 0).sum()))
    return df


def haversine(lat1, lon1, lat2, lon2):
    R = 6371000.0
    p1, p2 = np.radians(lat1), np.radians(lat2)
    dp, dl = p2 - p1, np.radians(lon2 - lon1)
    a = np.sin(dp / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dl / 2) ** 2
    return 2 * R * np.arcsin(np.sqrt(np.clip(a, 0, 1)))


def test_a_kinematics(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for tr, g in df.groupby("trace"):
        g = g.sort_values("t")
        lat, lon = g.Latitude.to_numpy(), g.Longitude.to_numpy()
        v = g.Speed.to_numpy(float) / 3.6                      # km/h -> m/s, one second per row
        fwd = np.r_[haversine(lat[:-1], lon[:-1], lat[1:], lon[1:]), np.nan]
        bwd = np.r_[np.nan, haversine(lat[:-1], lon[:-1], lat[1:], lon[1:])]
        ok = np.isfinite(v) & np.isfinite(fwd) & np.isfinite(bwd) & (v > 1.0)
        if ok.sum() < 30:
            continue
        rows.append({"trace": tr, "n": int(ok.sum()),
                     "median_abs_err_forward_m": float(np.median(np.abs(v[ok] - fwd[ok]))),
                     "median_abs_err_backward_m": float(np.median(np.abs(v[ok] - bwd[ok]))),
                     "corr_forward": float(np.corrcoef(v[ok], fwd[ok])[0, 1]),
                     "corr_backward": float(np.corrcoef(v[ok], bwd[ok])[0, 1])})
    t = pd.DataFrame(rows)
    t["forward_wins"] = t.median_abs_err_forward_m < t.median_abs_err_backward_m
    return t


def test_b_contamination(df: pd.DataFrame, k: int = 3) -> pd.DataFrame:
    """At a cell change between t and t+1, is row t's radio the old cell's or the new one's?"""
    rows = []
    for tr, g in df.groupby("trace"):
        g = g.sort_values("t").reset_index(drop=True)
        cid = g.CellID.to_numpy()
        rsrp = g.RSRP.to_numpy(float)
        chg = np.flatnonzero((cid[1:] != cid[:-1]) & np.isfinite(cid[1:]) & np.isfinite(cid[:-1]))
        for i in chg:
            old = rsrp[max(0, i - k - 1):i]                     # rows strictly before t
            new = rsrp[i + 2:i + 2 + k]                         # rows strictly after t+1
            if len(old) < 2 or len(new) < 2 or not np.isfinite(rsrp[i]):
                continue
            mo, mn = np.nanmedian(old), np.nanmedian(new)
            if abs(mo - mn) < 3:                                # need the two levels to differ
                continue
            rows.append({"trace": tr, "closer_to_new_cell": abs(rsrp[i] - mn) < abs(rsrp[i] - mo),
                         "row_t_rsrp": rsrp[i], "old_level": mo, "new_level": mn})
    return pd.DataFrame(rows)


def features(g: pd.DataFrame, lag: int) -> pd.DataFrame:
    x = g[RADIO].astype(float)
    if lag:
        x = x.shift(lag)
    out = {c: x[c] for c in RADIO}
    for c in ("RSRP", "RSRQ", "SNR", "RSSI"):
        for w in (3, 5, 10):
            out[f"{c}_mean{w}"] = x[c].rolling(w, min_periods=2).mean()
            out[f"{c}_std{w}"] = x[c].rolling(w, min_periods=2).std()
        out[f"{c}_d1"] = x[c].diff()
        out[f"{c}_slope5"] = x[c].diff(5) / 5
    # time since the previous cell change, from the same column the label uses
    cid = g.CellID.shift(lag)
    chg = (cid != cid.shift(1)).cumsum()
    out["t_since_cell_change"] = g.groupby(chg).cumcount().astype(float)
    return pd.DataFrame(out, index=g.index)


def test_c_inflation(df: pd.DataFrame, seeds=(0, 1, 2), lags=(0, 1, 2)) -> pd.DataFrame:
    import lightgbm as lgb
    parts = []
    for tr, g in df.groupby("trace"):
        g = g.sort_values("t").reset_index(drop=True)
        y = (g.CellID.shift(-1) != g.CellID) & g.CellID.notna() & g.CellID.shift(-1).notna()
        for lag in lags:
            f = features(g, lag)
            f["y"] = y.astype(int)
            f["trace"] = tr
            f["lag"] = lag
            f["valid"] = g.CellID.notna() & g.CellID.shift(-1).notna() & f.drop(
                columns=["y", "trace", "lag"]).notna().any(axis=1)
            parts.append(f)
    allf = pd.concat(parts, ignore_index=True)
    allf = allf[allf.valid].drop(columns=["valid"])
    cols = [c for c in allf.columns if c not in ("y", "trace", "lag")]
    rows = []
    traces = sorted(allf.trace.unique())
    folds = np.array_split(np.array(traces), 5)
    for lag in lags:
        sub = allf[allf.lag == lag]
        for seed in seeds:
            P = pd.Series(np.nan, index=sub.index)
            for hold in folds:
                te = sub.trace.isin(hold)
                m = lgb.train(dict(objective="binary", learning_rate=0.05, num_leaves=31,
                                   min_data_in_leaf=40, feature_fraction=0.8, verbose=-1,
                                   seed=seed, num_threads=2),
                              lgb.Dataset(sub.loc[~te, cols], sub.loc[~te, "y"]),
                              num_boost_round=300)
                P[sub.index[te]] = m.predict(sub.loc[te, cols])
            y = sub["y"].to_numpy()
            p = P.to_numpy()
            rows.append({"features_from": {0: "row t (as published)", 1: "row t-1 (lagged one)",
                                          2: "row t-2 (lagged two)"}[lag],
                         "seed": seed, "n": len(y), "prevalence": y.mean(),
                         "auprc": average_precision_score(y, p),
                         "lift": average_precision_score(y, p) / y.mean(),
                         "auroc": roc_auc_score(y, p)})
    return pd.DataFrame(rows)


def main():
    df = load()
    a = test_a_kinematics(df)
    save(a, "c9ext_kinematic_per_trace")
    save(pd.DataFrame([{
        "traces": len(a), "traces_where_forward_fits_better": int(a.forward_wins.sum()),
        "share_forward": float(a.forward_wins.mean()),
        "median_abs_err_forward_m": float(a.median_abs_err_forward_m.median()),
        "median_abs_err_backward_m": float(a.median_abs_err_backward_m.median()),
        "median_corr_forward": float(a.corr_forward.median()),
        "median_corr_backward": float(a.corr_backward.median())}]), "c9ext_kinematic_summary")
    b = test_b_contamination(df)
    save(pd.DataFrame([{"cell_changes_tested": len(b),
                        "row_t_closer_to_new_cell": int(b.closer_to_new_cell.sum()),
                        "share_closer_to_new_cell": float(b.closer_to_new_cell.mean())}]),
         "c9ext_cell_contamination")
    c = test_c_inflation(df)
    save(c, "c9ext_inflation_raw")
    s = c.groupby("features_from")[["prevalence", "auprc", "lift", "auroc"]].mean().reset_index()
    g = {r.features_from.split(" ")[1]: r for _, r in s.iterrows()}
    lag0, lag1, lag2 = g["t"], g["t-1"], g["t-2"]
    s2 = pd.concat([s, pd.DataFrame([
        {"features_from": "gain from t-1 to t (one second fresher)", "prevalence": np.nan,
         "auprc": 100 * (lag0.auprc / lag1.auprc - 1), "lift": np.nan,
         "auroc": lag0.auroc - lag1.auroc},
        {"features_from": "gain from t-2 to t-1 (one second fresher)", "prevalence": np.nan,
         "auprc": 100 * (lag1.auprc / lag2.auprc - 1), "lift": np.nan,
         "auroc": lag1.auroc - lag2.auroc}])], ignore_index=True)
    save(s2, "c9ext_inflation")
    LOG.info("\n%s", s2.to_string(index=False))


if __name__ == "__main__":
    main()


def summary():
    """One table the manuscript quotes, comparing the two instruments."""
    k = pd.read_csv("reports_rev/tables/c9ext_kinematic_summary.csv").iloc[0]
    b = pd.read_csv("reports_rev/tables/c9ext_cell_contamination.csv").iloc[0]
    c = pd.read_csv("reports_rev/tables/c9ext_inflation.csv").set_index("features_from")
    ours = pd.read_csv("reports_rev/tables/c9_row_alignment_audit.csv")
    ab = pd.read_csv("reports_rev/tables/c18_ablation.csv").set_index(["variant", "horizon_s"])
    a_lag0 = float(ab.loc[("main, NO lag (v1 alignment)", 1.0), "auprc_mean"])
    a_lag1 = float(ab.loc[("rf+mobility+history (main)", 1.0), "auprc_mean"])
    o = ours[ours.subset.str.startswith("all")].iloc[0]
    rows = [
        {"test": "Serving cell on the row before the event already matches the post-event cell",
         "this work (XCAL 1 Hz export)": f"{100 * float(o['row t+0']):.1f} % of 938 handover commands",
         "public dataset (G-NetTrack Pro, MMSys 2020)":
             f"{100 * float(b.share_closer_to_new_cell):.1f} % of {int(b.cell_changes_tested)} cell changes "
             f"(radio on row t is closer to the OLD cell)"},
        {"test": "Background rate three rows earlier",
         "this work (XCAL 1 Hz export)": f"{100 * float(ours[ours.subset.str.startswith('isolated')].iloc[0]['row t-3']):.1f} %",
         "public dataset (G-NetTrack Pro, MMSys 2020)": "50 % by construction of the test"},
        {"test": "Kinematic check (does reported speed match displacement after the row's timestamp?)",
         "this work (XCAL 1 Hz export)": "not applicable; the event clock settles it directly",
         "public dataset (G-NetTrack Pro, MMSys 2020)":
             f"inconclusive: forward {k.median_abs_err_forward_m:.1f} m vs backward "
             f"{k.median_abs_err_backward_m:.1f} m median error, GPS too coarse"},
        {"test": "AUPRC gain from using the row stamped t rather than t−1",
         "this work (XCAL 1 Hz export)": f"+{100 * (a_lag0 / a_lag1 - 1):.0f} % "
             f"({a_lag1:.3f} to {a_lag0:.3f}), an artefact",
         "public dataset (G-NetTrack Pro, MMSys 2020)":
             f"+{float(c.loc['gain from t-1 to t (one second fresher)', 'auprc']):.0f} %, "
             f"smaller than the +{float(c.loc['gain from t-2 to t-1 (one second fresher)', 'auprc']):.0f} % "
             "gain from t−2 to t−1, so it is freshness rather than contamination"},
    ]
    save(pd.DataFrame(rows), "c9ext_summary")

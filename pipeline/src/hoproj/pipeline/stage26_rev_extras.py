"""Stage 26 - remaining revision tables: parser counters, unlagged single-feature
AUROC, the ping-pong definition ladder and the Hawkes fit, all recomputed on the
v2 configuration timeline and the full command stream."""
from __future__ import annotations

import pickle
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

from ..data.config_timeline_v2 import annotate_reports_v2, parse_timeline
from ..data.selfexcite import fit_hawkes
from ..revision.data import CAPTURE_NAMES, load_revision_data
from ..utils import get_logger
from .stage12_xcal_prepare import CAPTURES
from .stage22_revision import PROC, REP, SIG, save

LOG = get_logger("hoproj.stage26")


def timeline_counters():
    sig = pickle.load(open(SIG, "rb"))
    rows = []
    for tag, raw, _, s in CAPTURES:
        tl = parse_timeline(Path(raw) / s)
        a = annotate_reports_v2(sig[tag]["reports"][["t", "meas_id"]], tl)
        v1 = sig[tag]["reports"]["event_id"].fillna("-").to_numpy()
        agree = float((a["event_id"].fillna("-").to_numpy() == v1).mean())
        rows.append({"capture": CAPTURE_NAMES[tag], "config_updates": tl.n_updates,
                     "measid_removals": tl.n_removals, "interfreq_swaps": tl.n_swaps,
                     "config_resets": tl.n_resets, "reports": len(a),
                     "resolved_share": float(a["resolved"].mean()),
                     "a3_share": float((a["event_id"] == "A3").mean()),
                     "agreement_with_v1": agree})
    save(pd.DataFrame(rows), "c_timeline_v2_counters")


def feature_blocks():
    """Single source of truth for every feature count quoted in the manuscript.

    Five different totals appeared across the draft (152 / 112 / 106 / 107 / 120) because
    each was typed by hand at the point of use.  Nothing downstream may hard-code a count
    again: Table 4.3 and Section 4.6 both read this file.
    """
    d = load_revision_data(PROC, SIG, lag=1, reports_pickle=REP)
    n = {k: len(v) for k, v in d.names.items()}
    main = n["rf"] + n["mobility"] + n["history"]
    rows = [
        {"block": "Radio", "count": n["rf"], "in_main_set": True,
         "source": "1 Hz export, lagged one row"},
        {"block": "Mobility", "count": n["mobility"], "in_main_set": True,
         "source": "1 Hz export, lagged one row"},
        {"block": "History", "count": n["history"], "in_main_set": True,
         "source": "decoded signalling, session-level"},
        {"block": "Main feature set", "count": main, "in_main_set": True, "source": ""},
        {"block": "Signalling (ablation only)", "count": n["signalling"], "in_main_set": False,
         "source": "decoded signalling"},
        {"block": "Design matrix as built", "count": len(d.X.columns), "in_main_set": False,
         "source": "main set plus the signalling block"},
    ]
    assert main == 112, main
    assert main + n["signalling"] == len(d.X.columns)
    save(pd.DataFrame(rows), "c0_feature_blocks")


def single_feature_lag0():
    d = load_revision_data(PROC, SIG, lag=0, reports_pickle=REP)
    rows = []
    Y = d.Y
    for c in list(d.X.columns) + ["serving_dwell_s"]:
        x = (d.frame[c] if c == "serving_dwell_s" else d.X[c]).to_numpy(float)
        ok = np.isfinite(x)
        if ok.sum() < 1000 or np.nanstd(x) == 0:
            continue
        a = roc_auc_score(Y[ok, 1], x[ok])
        rows.append({"feature": c, "auroc_1s": max(a, 1 - a)})
    save(pd.DataFrame(rows).sort_values("auroc_1s", ascending=False), "c14_single_feature_auroc_lag0")


def _pp_flags(ev: pd.DataFrame, window: float, by_pci_only: bool,
              any_return: bool) -> np.ndarray:
    """Per-handover ping-pong indicator, aligned to ``ev``'s own row order.

    NB: this must be evaluated once on the FULL command sequence.  "Return to the
    immediately previous cell" is defined relative to the neighbours a handover
    actually has, so filtering the event frame *before* flagging silently redefines
    "previous" within the subset.  That is what made the carrier strata of Table 5.14
    imply 218 ping-pongs while the regime strata implied 252 on the same 957 commands:
    dropping the inter-frequency commands made intra-frequency handovers adjacent that
    were not adjacent in the drive.  Stratify the flags, never re-run the detector on a
    subset.  (Campaign strata were unaffected only because ``groupby("capture")`` below
    already splits the sequence on exactly that boundary.)
    """
    flag = pd.Series(False, index=ev.index)
    for cap, g in ev.groupby("capture"):
        g = g.sort_values("t")
        idx = g.index.to_numpy()
        key = g["target_pci"].astype(str) if by_pci_only else \
            g["target_pci"].astype(str) + "@" + g["target_earfcn"].astype(str)
        t = g["t"].to_numpy()
        k = key.to_numpy()
        for i in range(len(g)):
            j = i + 1
            while j < len(g) and (t[j] - t[i]) / np.timedelta64(1, "s") <= window:
                back = k[j] == k[i - 1] if i > 0 else False
                if any_return:
                    if j > i and k[j] in set(k[max(0, i - 3):i]):
                        flag.loc[idx[i]] = True
                        break
                elif j == i + 1 and back:
                    flag.loc[idx[i]] = True
                    break
                j += 1
    return flag.to_numpy()


def _pp(ev: pd.DataFrame, window: float, by_pci_only: bool, any_return: bool) -> float:
    hits = 0
    for cap, g in ev.groupby("capture"):
        g = g.sort_values("t").reset_index(drop=True)
        key = g["target_pci"].astype(str) if by_pci_only else \
            g["target_pci"].astype(str) + "@" + g["target_earfcn"].astype(str)
        t = g["t"].to_numpy()
        k = key.to_numpy()
        for i in range(len(g)):
            j = i + 1
            while j < len(g) and (t[j] - t[i]) / np.timedelta64(1, "s") <= window:
                back = k[j] == k[i - 1] if i > 0 else False
                if any_return:
                    if j > i and k[j] in set(k[max(0, i - 3):i]):
                        hits += 1
                        break
                elif j == i + 1 and back:
                    hits += 1
                    break
                j += 1
    return hits / len(ev)


def pingpong():
    d = load_revision_data(PROC, SIG, lag=1, reports_pickle=REP)
    ev = d.events
    qc = pd.read_parquet(PROC / "handovers.parquet")
    rows = [
        {"definition": "Return to the immediately previous cell, identified by PCI and carrier, within 15 s",
         "n_handovers": len(ev), "rate": _pp(ev, 15, False, False)},
        {"definition": "The same, with the cell identified by PCI alone",
         "n_handovers": len(ev), "rate": _pp(ev, 15, True, False)},
        {"definition": "Any return within the window, not only to the previous cell",
         "n_handovers": len(ev), "rate": _pp(ev, 15, False, True)},
        {"definition": "Return to the immediately previous cell, restricted to commands inside retained blocks",
         "n_handovers": len(qc), "rate": float(qc["is_pingpong"].mean())},
    ]
    save(pd.DataFrame(rows), "c13_pingpong_definitions")
    grid = []
    for w in (5, 10, 15):
        for lab, (pci, anyr) in {"previous cell, PCI+carrier": (False, False),
                                 "previous cell, PCI only": (True, False),
                                 "any recent cell, PCI+carrier": (False, True)}.items():
            grid.append({"window_s": w, "convention": lab, "rate": _pp(ev, w, pci, anyr)})
    save(pd.DataFrame(grid), "c13_pingpong_grid")
    # where it concentrates
    at = pd.read_csv("reports_rev/tables/c5_handover_attribution_v2_rows.csv", parse_dates=["t"])
    ev2 = ev.copy()
    ev2["relation"] = at["ho_relation"].to_numpy()[: len(ev2)]
    # flag once on the full sequence, then partition the flags — see _pp_flags
    ev2["pp"] = _pp_flags(ev2, 15, False, False)
    strata = []
    for lab, sub in (("intra-frequency handovers", ev2[ev2.relation == "intra-frequency"]),
                     ("inter-frequency handovers", ev2[ev2.relation == "inter-frequency"]),
                     ("highway campaign", ev2[ev2.capture == "XCAL15Sept"]),
                     ("urban campaigns", ev2[ev2.capture != "XCAL15Sept"])):
        strata.append({"stratum": lab, "n_handovers": len(sub),
                       "n_pingpong": int(sub["pp"].sum()), "rate": float(sub["pp"].mean())})
    strata.append({"stratum": "all commands", "n_handovers": len(ev2),
                   "n_pingpong": int(ev2["pp"].sum()), "rate": float(ev2["pp"].mean())})
    save(pd.DataFrame(strata), "c13_pingpong_strata")


def hawkes():
    d = load_revision_data(PROC, SIG, lag=1, reports_pickle=REP)
    rows = []
    for cap, g in d.events.groupby("capture"):
        s = d.frame[d.frame.capture == cap]
        t0 = s["t"].min() - pd.to_timedelta(s["ts"].min(), unit="s")
        ev = pd.DataFrame({"drive_id": cap, "t": g["t"]})
        sm = pd.DataFrame({"drive_id": cap, "t": pd.date_range(t0, s["t"].max(), freq="1s")})
        try:
            f = fit_hawkes(ev, sm)
            rows.append({"stratum": CAPTURE_NAMES[cap], "events": len(g), **f.as_dict()})
        except Exception as exc:                                  # noqa: BLE001
            LOG.warning("hawkes failed for %s: %s", cap, exc)
    ev = pd.DataFrame({"drive_id": d.events["capture"], "t": d.events["t"]})
    sm = pd.DataFrame({"drive_id": d.frame["capture"], "t": d.frame["t"]})
    f = fit_hawkes(ev, sm)
    rows.append({"stratum": "pooled", "events": len(d.events), **f.as_dict()})
    save(pd.DataFrame(rows), "c_hawkes_fit")
    save(ogata_residuals(d, f), "c_hawkes_gof")


def ogata_residuals(d, f) -> pd.DataFrame:
    """Ogata's time-rescaling residual test, with the statistic actually reported.

    Section 5.10 says the exponential kernel is rejected but an earlier draft gave no
    statistic, so a reader could not judge how badly.  Rescaling the time axis by the
    fitted compensator turns the arrivals into a unit-rate Poisson process if the model
    is right, which makes the transformed inter-arrival times Exp(1).
    """
    from scipy import stats
    mu, a, b = f.mu, f.alpha, f.beta
    resid = []
    for cap, g in d.events.groupby("capture"):
        ts = np.sort((g["t"] - g["t"].min()).dt.total_seconds().to_numpy())
        # compensator Lambda(t) = mu*t + (alpha/beta) * sum_i (1 - exp(-beta (t - t_i)))
        lam = [mu * t + (a / b) * np.sum(1 - np.exp(-b * (t - ts[ts < t]))) for t in ts]
        resid.append(np.diff(np.array(lam)))
    r = np.concatenate(resid)
    r = r[np.isfinite(r) & (r >= 0)]
    ks = stats.kstest(r, "expon")
    return pd.DataFrame([{
        "test": "Ogata time-rescaling residuals vs Exp(1)",
        "n_residuals": int(len(r)),
        "ks_statistic_D": float(ks.statistic),
        "p_value": float(ks.pvalue),
        "mean_residual": float(r.mean()),
        "rejects_exponential_kernel_at_0.05": bool(ks.pvalue < 0.05),
    }])


if __name__ == "__main__":
    timeline_counters()
    feature_blocks()
    single_feature_lag0()
    pingpong()
    hawkes()

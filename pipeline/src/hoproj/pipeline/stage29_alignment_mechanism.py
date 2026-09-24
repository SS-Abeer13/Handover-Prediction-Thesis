"""Stage 29 - the mechanism behind the row-time alignment defect [C9].

    python -m hoproj.pipeline.stage29_alignment_mechanism --exp all

Stage 22 (``audit``) established *that* a 1 Hz XCAL row stamped t already shows
the post-handover serving cell.  Stage 27/28 showed the same defect is absent in
G-NetTrack Pro logs and present in a second, independent XCAL corpus (NUWiNS).
This stage asks *why*, and turns the observation into a falsifiable prediction.

Mechanism
---------
A handover command is sent at an arbitrary instant tau inside the second
[t, t+1).  Write

    delta = tau - floor(tau)          position of the command inside the second
    x     = t_complete - tau          execution (interruption) time
    m     = 1 - delta - x             margin by which execution beats t+1

If the exporter writes one row per second and that row carries the serving cell
*as of the end of the second*, then the row stamped t shows the target whenever
m > 0 and the source cell whenever m < 0.  The defect is therefore not a bug in
any particular capture: it is what end-of-second aggregation does to an event
whose execution is two orders of magnitude faster than the grid.

Experiments
  delta      contamination by delta quartile, our four captures
  margin     contamination vs the execution margin m - the falsification test
  synthesis  three-dataset mechanism table for the manuscript (Table A.3)
"""
from __future__ import annotations

import argparse
import pickle
from pathlib import Path

import numpy as np
import pandas as pd

from ..utils import get_logger

LOG = get_logger("hoproj.stage29")

ROOT = Path(".")
PROC = ROOT / "data/processed_xcal"
SIG = ROOT / "data/rev/signalling.pkl"
OUT = ROOT / "reports_rev/tables"
NUWINS_ALIGN = OUT / "c9ext_nuwins_alignment.csv"
NUWINS_SUB = OUT / "c9ext_nuwins_subsecond.csv"
EXT_SUMMARY = OUT / "c9ext_summary.csv"

DELTA_EDGES = [0.0, 0.25, 0.50, 0.75, 1.0]
MARGIN_EDGES = [-0.25, 0.0, 0.05, 0.10, 0.25, 0.50, 0.75, 1.0]


def save(df: pd.DataFrame, name: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT / f"{name}.csv", index=False)
    (OUT / f"{name}.md").write_text(df.round(4).to_markdown(index=False))
    LOG.info("wrote %s (%d rows)", name, len(df))


# ------------------------------------------------------------------ our data
def per_handover() -> pd.DataFrame:
    """One row per completed handover command, with its intra-second geometry."""
    feats = pd.read_parquet(PROC / "features.parquet")
    feats["t"] = pd.to_datetime(feats["t"])
    sig = pickle.load(open(SIG, "rb"))
    rows = []
    for cap, v in sig.items():
        h = v["handovers"]
        h = h[h["completed"]].copy().sort_values("t").reset_index(drop=True)
        s = feats.loc[feats.capture == cap].set_index("t").sort_index()
        prev_gap = h["t"].diff().dt.total_seconds().fillna(9e9).to_numpy()
        next_gap = (-h["t"].diff(-1).dt.total_seconds()).fillna(9e9).to_numpy()
        tgts = h["target_pci"].to_numpy()
        cols = ["t", "target_pci", "interrupt_ms"]
        for i, (tau, tgt, ims) in enumerate(h[cols].itertuples(index=False)):
            t0 = tau.floor("s")
            if t0 not in s.index:
                continue
            get = lambda k: (s.at[t0 + pd.Timedelta(seconds=k), "serving_pci"]  # noqa: E731
                             if (t0 + pd.Timedelta(seconds=k)) in s.index else np.nan)
            delta = (tau - t0).total_seconds()
            x = float(ims) / 1000.0
            rows.append({"capture": cap, "delta": delta, "exec_s": x,
                         "margin": 1.0 - delta - x,
                         "prev_gap_s": prev_gap[i], "next_gap_s": next_gap[i],
                         "target_pci": tgt, "pci_tm2": get(-2), "pci_tm1": get(-1),
                         "pci_t": get(0), "pci_tp1": get(1),
                         "next_target_pci": tgts[i + 1] if i + 1 < len(tgts) else np.nan})
    d = pd.DataFrame(rows)
    for k, c in ((-2, "pci_tm2"), (-1, "pci_tm1"), (0, "pci_t"), (1, "pci_tp1")):
        d[f"hit_{k}"] = (d[c] == d["target_pci"]).astype(float).where(d[c].notna())
    d["isolated"] = d["prev_gap_s"] > 8.0
    d["clean"] = (d["prev_gap_s"] > 2.0) & (d["next_gap_s"] > 2.0)
    return d


def exp_delta(d: pd.DataFrame) -> None:
    """Contamination of row t by where inside the second the command falls."""
    out = []
    for lab, g in (("all handovers", d), ("isolated (previous > 8 s earlier)", d[d.isolated]),
                   ("clean (no other handover within 2 s)", d[d.clean])):
        g = g.copy()
        g["bin"] = pd.cut(g["delta"], DELTA_EDGES, right=False)
        for b, gg in g.groupby("bin", observed=True):
            out.append({"subset": lab,
                        "delta bin (s into the second)": f"[{b.left:.2f}, {b.right:.2f})",
                        "n": int(len(gg)),
                        "row t shows target": round(float(gg["hit_0"].mean()), 3),
                        "row t+1 shows target": round(float(gg["hit_1"].mean()), 3),
                        "median execution (ms)": round(1000 * float(gg["exec_s"].median()), 1)})
        out.append({"subset": lab, "delta bin (s into the second)": "all",
                    "n": int(len(g)),
                    "row t shows target": round(float(g["hit_0"].mean()), 3),
                    "row t+1 shows target": round(float(g["hit_1"].mean()), 3),
                    "median execution (ms)": round(1000 * float(g["exec_s"].median()), 1)})
    save(pd.DataFrame(out), "c9m_delta_bins_ours")


def exp_margin(d: pd.DataFrame) -> None:
    """The falsification test: execution margin m = 1 - delta - x against row t."""
    g = d.copy()
    g["bin"] = pd.cut(g["margin"], MARGIN_EDGES, right=False)
    rows = []
    for b, gg in g.groupby("bin", observed=True):
        rows.append({"execution margin m (s)": f"[{b.left:+.2f}, {b.right:+.2f})",
                     "n": int(len(gg)),
                     "row t shows target": round(float(gg["hit_0"].mean()), 3),
                     "row t-1 shows target": round(float(gg["hit_-1"].mean()), 3)})
    save(pd.DataFrame(rows), "c9m_execution_margin")

    # the prediction as a 2x2 contingency table
    pred = g["margin"] > 0
    obs = g["hit_0"] > 0.5
    tab = pd.DataFrame({
        "prediction": ["execution completes before t+1 (m > 0)",
                       "execution crosses t+1 (m < 0)"],
        "n": [int(pred.sum()), int((~pred).sum())],
        "row t shows target": [round(float(obs[pred].mean()), 3),
                               round(float(obs[~pred].mean()), 3)],
        "row t shows source": [round(float((~obs[pred]).mean()), 3),
                               round(float((~obs[~pred]).mean()), 3)]})
    save(tab, "c9m_mechanism_prediction")

    # where the mechanism over-predicts: is it a one-row exporter lag?
    miss = g[(g["margin"] > 0) & (g["hit_0"] < 0.5)]
    diag = pd.DataFrame([
        {"residual case": "row t predicted to show target but shows source", "n": int(len(miss)),
         "share": round(len(miss) / len(g), 3), "share of": "all handovers"},
        {"residual case": "... of which row t+1 shows the target (one-row exporter lag)",
         "n": int((miss["hit_1"] > 0.5).sum()),
         "share": round(float((miss["hit_1"] > 0.5).mean()), 3), "share of": "residual cases"},
        {"residual case": "... of which row t still equals row t-1 (KPI not yet refreshed)",
         "n": int((miss["pci_t"] == miss["pci_tm1"]).sum()),
         "share": round(float((miss["pci_t"] == miss["pci_tm1"]).mean()), 3),
         "share of": "residual cases"},
        {"residual case": "... of which a further handover lands inside the same second",
         "n": int((miss["next_gap_s"] < (1.0 - miss["delta"])).sum()),
         "share": round(float((miss["next_gap_s"] < (1.0 - miss["delta"])).mean()), 3),
         "share of": "residual cases"}])
    save(diag, "c9m_residual_diagnosis")


def exp_synthesis(d: pd.DataFrame) -> None:
    """Three-dataset mechanism table (manuscript Table A.3)."""
    pct = lambda v, n=1: f"{100 * v:.{n}f} %"  # noqa: E731
    ours = {"n": int(len(d)), "t": float(d["hit_0"].mean()), "tm1": float(d["hit_-1"].mean()),
            "iso_n": int(d.isolated.sum()), "iso_t": float(d.loc[d.isolated, "hit_0"].mean()),
            "p90": 1000 * float(d["exec_s"].quantile(0.9))}

    nw = pd.read_csv(OUT / "c9ext_nuwins_alignment_all.csv")
    pool = nw[nw.dataset == "pooled"].set_index("subset")
    nfs = pd.read_csv(OUT / "c9ext_nuwins_startofsecond_all.csv")
    fpool = nfs[nfs.dataset == "pooled"].set_index("subset")
    nfiles = int(nw[~nw.dataset.isin(["pooled"])
                    & ~nw.dataset.str.endswith("(all files)")]["dataset"].nunique())
    nops = int(nw[nw.dataset.str.endswith("(all files)")]["dataset"].nunique())
    ec = pd.read_csv(OUT / "c9ext_nuwins_execution_cdf.csv")

    ir = pd.read_csv(OUT / "c9ext_cell_contamination.csv").iloc[0] \
        if (OUT / "c9ext_cell_contamination.csv").exists() else None
    ir_share = f"{100 * float(ir['share_closer_to_new_cell']):.1f} % of " \
               f"{int(ir['cell_changes_tested']):,} cell changes" if ir is not None else "--"

    rows = [
        ("Instrument", "XCAL, 1 Hz export produced by the tool",
         "G-NetTrack Pro, ~1 Hz application log",
         "XCAL, native 10 Hz export downsampled here"),
        ("Network and region", "One operator, Dhaka and Gazipur",
         "One operator, Ireland (Raca et al., MMSys 2020)",
         f"{nops} tier-1 operators, two cross-US routes (NUWiNS, PAM 2025)"),
        ("Event clock", "RRC signalling: command and complete",
         "serving-cell identifier changes only", "XCAL handover event column"),
        ("Row semantics", "aggregate over the second, written at its end",
         "instantaneous sample", "set by us: last, or first, sample of the second"),
        ("Handovers audited", f"{ours['n']:,}", ir_share.split(' of ')[-1] if ir is not None else "--",
         f"{int(pool.loc['all handovers', 'n']):,} in {nfiles} files"),
        ("Row t shows the target cell", pct(ours["t"]), ir_share.split(' of ')[0] if ir is not None else "--",
         pct(float(pool.loc["all handovers", "row t+0"]))),
        ("Isolated handovers only", f"{pct(ours['iso_t'])} (n = {ours['iso_n']:,})",
         "not separable (no signalling clock)",
         f"{pct(float(pool.loc[pool.index.str.startswith('isolated')][ 'row t+0'].iloc[0]))} "
         f"(n = {int(pool.loc[pool.index.str.startswith('isolated')]['n'].iloc[0]):,})"),
        ("Row t-1 shows the target cell", pct(ours["tm1"]),
         "no step across the integer boundary",
         pct(float(pool.loc["all handovers", "row t-1"]))),
        ("Same rows, start-of-second rule", "not available (the tool aggregates)",
         "not applicable (rows are samples)",
         pct(float(fpool.loc["all handovers", "row t+0"]))),
        ("Update delay observed", f"p90 {ours['p90']:.0f} ms from RRC complete messages",
         "not observable on a 1 Hz grid",
         f"50-75 ms, recovered from the contamination cliff "
         f"({pct(float(ec.iloc[2]['row t shows target']), 0)} at 75-100 ms left, "
         f"{pct(float(ec.iloc[3]['row t shows target']), 0)} at 50-75 ms, "
         f"{pct(float(ec.iloc[4]['row t shows target']), 0)} below 50 ms)"),
        ("Verdict", "defect present, attenuated by a one-row KPI refresh lag",
         "no defect: sampled rows are not aggregates",
         "defect present under end-of-second, absent under start-of-second"),
    ]
    save(pd.DataFrame(rows, columns=["Property", "This work", "Irish 4G/5G (MMSys 2020)",
                                     "US tier-1 (NUWiNS PAM 2025)"]),
         "c9m_three_dataset_mechanism")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--exp", default="all",
                    choices=["all", "delta", "margin", "synthesis"])
    a = ap.parse_args()
    d = per_handover()
    LOG.info("%d completed handovers with an export row at floor(tau)", len(d))
    if a.exp in ("all", "delta"):
        exp_delta(d)
    if a.exp in ("all", "margin"):
        exp_margin(d)
    if a.exp in ("all", "synthesis"):
        exp_synthesis(d)
    d.to_csv(OUT / "c9m_per_handover_geometry.csv", index=False)


if __name__ == "__main__":
    main()

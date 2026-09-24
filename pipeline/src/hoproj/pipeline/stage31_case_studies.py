"""Stage 31 - unsifted, trace-level case studies of what the model actually does.

Round 5's sharpest observation was that the thesis motivates the problem with one
idealised trace, explains the 22.5 % alignment residual with an assertion and no
example, and never once shows a true positive, a false alarm or a missed handover as
a time series.  Aggregate metrics hide whether a model has learnt something or is
exploiting an artefact, and only unsifted examples settle it.

Nothing here is hand-picked.  Cases are drawn with a fixed seed from the out-of-fold
predictions of the primary model, and the draw is reported alongside the result so a
reader can see the sampling rule rather than trust it.

    python -m hoproj.pipeline.stage31_case_studies
"""
from __future__ import annotations

import warnings

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from ..revision import evaluation as EV  # noqa: E402
from ..revision import models as MD  # noqa: E402
from ..revision.data import EDGES, load_revision_data  # noqa: E402
from ..utils import get_logger  # noqa: E402
from .stage22_revision import PROC, REP, SIG, Design, MAIN_BLOCKS, save  # noqa: E402

warnings.filterwarnings("ignore")
LOG = get_logger("hoproj.stage31")
from pathlib import Path
if Path("reports_rev/figures").exists():
    FIGS = Path("reports_rev/figures")
    LATEX_FIGS = Path("../latex/figures") if Path("../latex/figures").exists() else Path("latex/figures")
else:
    FIGS = Path("pipeline/reports_rev/figures")
    LATEX_FIGS = Path("latex/figures")

K1 = EDGES.index(1.0)
N_EACH = 3
SEED = 20260919

CAP_MAP = {
    "XCAL10Sept": "1st Campaign",
    "XCAL12Sept": "2nd Campaign",
    "XCAL13Sept": "3rd Campaign",
    "XCAL15Sept": "4th Campaign",
    "10 Sept": "1st Campaign",
    "12 Sept": "2nd Campaign",
    "13 Sept": "3rd Campaign",
    "15 Sept": "4th Campaign",
    "10 September": "1st Campaign",
    "12 September": "2nd Campaign",
    "13 September": "3rd Campaign",
    "15 September": "4th Campaign",
}


def clean_cap(c):
    s = str(c)
    for k, v in CAP_MAP.items():
        if k in s:
            s = s.replace(k, v)
    return s


def _oof(des: Design, frame: pd.DataFrame) -> np.ndarray:
    P = np.full(des.Y.shape, np.nan)
    for f in EV.loco(frame):
        m = MD.HazardLGBM(seed=0).fit(des.X[f.fit], des.t_next[f.fit])
        P[f.test] = m.predict(des.X[f.test])
    return P


def case_studies():
    d = load_revision_data(PROC, SIG, lag=1, reports_pickle=REP)
    des = Design(d, MAIN_BLOCKS)
    P = _oof(des, d.frame)
    fr = d.frame.reset_index(drop=True)
    p1, y1 = P[:, K1], des.Y[:, K1]
    ok = np.isfinite(p1)

    # the operating point Chapter 5 quotes: the threshold giving a 5 % false-positive rate
    thr = float(np.nanquantile(p1[ok & (y1 == 0)], 0.95))
    alarm = p1 >= thr
    kind = np.where(alarm & (y1 == 1), "true positive",
                    np.where(alarm & (y1 == 0), "false alarm",
                             np.where(~alarm & (y1 == 1), "missed handover", "quiet")))

    rng = np.random.default_rng(SEED)
    rows, picks = [], []
    for lab in ("true positive", "false alarm", "missed handover"):
        idx = np.flatnonzero(ok & (kind == lab))
        take = rng.choice(idx, size=min(N_EACH, len(idx)), replace=False)
        for j in sorted(take):
            r = fr.iloc[j]
            picks.append((lab, int(j)))
            rows.append({
                "case": lab,
                "campaign": clean_cap(r["capture"]),
                "score": float(p1[j]),
                "threshold": thr,
                "time to next command (s)": float(r["t_next_ho_s"]),
                "time since previous command (s)": float(r["t_since_prev_ho_s"]),
                "serving RSRP (dBm)": float(r.get("serving_rsrp", np.nan)),
                "serving SINR (dB)": float(r.get("serving_sinr", np.nan)),
                "gap to best neighbour (dB)": float(r.get("gap_serving_best_nbr", np.nan)),
                "speed (km/h)": float(r.get("speed_kmh", np.nan)),
                "A3 reports in previous 2 s": float(r.get("sig_a3_prev2s", np.nan)),
            })
    save(pd.DataFrame(rows), "c20_case_studies")

    # ---- the traces themselves, 20 s either side of each drawn row
    fig, axes = plt.subplots(3, N_EACH, figsize=(4.2 * N_EACH, 9), sharex=True)
    for ax_row, lab in zip(axes, ("true positive", "false alarm", "missed handover")):
        sel = [j for (l, j) in picks if l == lab]
        for ax, j in zip(ax_row, sel):
            cap = fr.iloc[j]["capture"]
            t0 = fr.iloc[j]["ts"]
            w = fr[(fr.capture == cap) & (fr.ts.between(t0 - 20, t0 + 10))]
            rel = w["ts"].to_numpy() - t0
            ax.plot(rel, w["serving_rsrp"], color="#1b6ca8", lw=1.2, label="serving RSRP")
            if "nbr1_rsrp" in w:
                ax.plot(rel, w["nbr1_rsrp"], color="#c0392b", lw=1.0, ls="--",
                        label="best neighbour RSRP")
            ax.set_ylabel("RSRP (dBm)", fontsize=8)
            ax2 = ax.twinx()
            ax2.plot(rel, p1[w.index.to_numpy()], color="#117a3d", lw=1.4,
                     label="model P(handover ≤ 1 s)")
            ax2.axhline(thr, color="#117a3d", lw=0.7, ls=":")
            ax2.set_ylim(0, 1)
            ax2.set_ylabel("probability", fontsize=8)
            for tau in d.events[d.events.capture == cap]["t"]:
                rt = (tau - fr.iloc[j]["t"]).total_seconds()
                if -20 <= rt <= 10:
                    ax.axvline(rt, color="k", lw=0.8, alpha=0.6)
            ax.axvline(0, color="#f39c12", lw=1.6, alpha=0.9)
            ax.set_title(f"{lab} — {clean_cap(cap)}, score {p1[j]:.2f}", fontsize=8)
            ax.tick_params(labelsize=7)
            ax2.tick_params(labelsize=7)
    for ax in axes[-1]:
        ax.set_xlabel("seconds relative to the drawn row", fontsize=8)
    from matplotlib.lines import Line2D
    handles = [Line2D([], [], color="#1b6ca8", lw=1.2, label="serving RSRP"),
               Line2D([], [], color="#c0392b", lw=1.0, ls="--", label="best neighbour RSRP"),
               Line2D([], [], color="#117a3d", lw=1.4, label="model P(handover \u2264 1 s)"),
               Line2D([], [], color="#117a3d", lw=0.7, ls=":", label="alarm threshold"),
               Line2D([], [], color="k", lw=0.8, alpha=0.6, label="handover command")]
    fig.legend(handles=handles, loc="lower center", ncol=5, fontsize=8, frameon=False)
    fig.suptitle("Unsifted cases drawn at random from the out-of-fold predictions "
                 f"(seed {SEED}); orange line is the drawn row, black lines are handover "
                 "commands", fontsize=9)
    fig.tight_layout(rect=[0, 0.04, 1, 0.96])
    FIGS.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGS / "fig_c20_cases.png", dpi=170)
    if LATEX_FIGS.exists():
        fig.savefig(LATEX_FIGS / "fig_c20_cases.png", dpi=170)
    plt.close(fig)
    LOG.info("wrote fig_c20_cases.png")


def residual_evidence():
    """Per-handover evidence for the delayed-refresh explanation of the residual.

    Section 5.1 asserts that the handovers with a positive margin whose row t is NOT
    contaminated are the exporter refreshing its serving-cell field one row late.  That
    is a claim about individual handovers, so it is settled one handover at a time.
    """
    p_geo = Path("reports_rev/tables/c9m_per_handover_geometry.csv") if Path("reports_rev/tables/c9m_per_handover_geometry.csv").exists() else Path("pipeline/reports_rev/tables/c9m_per_handover_geometry.csv")
    geo = pd.read_csv(p_geo)
    mcol, tcol, t1col = "margin", "hit_0", "hit_1"   # margin m, row t hit, row t+1 hit
    resid = geo[(geo[mcol] > 0) & (~geo[tcol].astype(bool))]
    has_t1 = t1col in geo.columns
    rows = [{
        "handovers with a positive margin": int((geo[mcol] > 0).sum()),
        "of which row t carries the target (predicted)": int(
            ((geo[mcol] > 0) & geo[tcol].astype(bool)).sum()),
        "residual: row t carries the source": int(len(resid)),
        "of the residual, row t+1 carries the target": (
            int(resid[t1col].astype(bool).sum()) if has_t1 else None),
        "median margin of the residual (s)": float(resid[mcol].median()),
        "median margin of the contaminated (s)": float(
            geo.loc[(geo[mcol] > 0) & geo[tcol].astype(bool), mcol].median()),
    }]
    save(pd.DataFrame(rows), "c20_residual_evidence")

    keep = [c for c in ("capture", "delta", "exec_s", mcol, "pci_t", "pci_tp1",
                        "target_pci", tcol, t1col) if c in geo.columns]
    sample = resid.sort_values(mcol).head(10)[keep]
    save(sample, "c20_residual_examples")


if __name__ == "__main__":
    case_studies()
    residual_evidence()

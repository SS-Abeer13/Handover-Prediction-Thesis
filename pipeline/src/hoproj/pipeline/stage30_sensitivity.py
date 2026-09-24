"""Stage 30 - sensitivity of the results to the four post-hoc windows.

Round 5 raised, correctly, that the 180 s block length, the 60 s purge, the 10 s
burst cutoff and the 2 s post-handover blank were all chosen after the data were in
hand, and that a reader cannot tell whether a conclusion survives a different choice.
Each is varied here over a range that brackets the value used, with everything else
held fixed.  The point is not to find a better setting - it is to show that no
conclusion in Chapter 5 turns on where these were set.

    python -m hoproj.pipeline.stage30_sensitivity
"""
from __future__ import annotations

import warnings

import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score

from ..revision import evaluation as EV
from ..revision import models as MD
from ..revision.data import EDGES, load_revision_data
from ..utils import get_logger
from .stage22_revision import PROC, REP, SEEDS, SIG, Design, MAIN_BLOCKS, save

warnings.filterwarnings("ignore")
LOG = get_logger("hoproj.stage30")
K1 = EDGES.index(1.0)


def _fit_predict(des: Design, folds) -> np.ndarray:
    """Out-of-fold hazard predictions for the primary learner, fixed hyper-parameters."""
    P = np.full(des.Y.shape, np.nan)
    for f in folds:
        m = MD.HazardLGBM(seed=0).fit(des.X[f.fit], des.t_next[f.fit])
        P[f.test] = m.predict(des.X[f.test])
    return P


def _auprc(Y, P, k=K1, sel=None):
    y = Y[:, k] if sel is None else Y[sel, k]
    p = P[:, k] if sel is None else P[sel, k]
    ok = np.isfinite(p)
    return float(average_precision_score(y[ok], p[ok])) if len(np.unique(y[ok])) == 2 else np.nan


def _synthetic_chunks(frame: pd.DataFrame, seconds: float) -> np.ndarray:
    """Chunk ids of a chosen length, rebuilt from timestamps within each capture."""
    out = np.empty(len(frame), object)
    for cap, g in frame.groupby("capture"):
        rel = (g["ts"] - g["ts"].min()).to_numpy() / seconds
        out[g.index.to_numpy()] = [f"{cap}:{int(i)}" for i in np.floor(rel)]
    return out


def block_length():
    """How much does the 'random blocks' protocol inflate at other block lengths?"""
    d = load_revision_data(PROC, SIG, lag=1, reports_pickle=REP)
    des = Design(d, MAIN_BLOCKS)
    base = _auprc(des.Y, _fit_predict(des, EV.loco(d.frame)))
    rows = []
    for L in (60, 120, 180, 240, 300):
        fr = d.frame.copy()
        fr["drive_id"] = _synthetic_chunks(fr, L)
        a = _auprc(des.Y, _fit_predict(des, EV.chunk_grouped(fr)))
        rows.append({"block_length_s": L, "n_blocks": int(pd.Series(fr["drive_id"]).nunique()),
                     "auprc_1s_random_blocks": a, "auprc_1s_loco": base,
                     "inflation_vs_loco_%": 100 * (a / base - 1)})
    save(pd.DataFrame(rows), "c19_sens_block_length")


def purge_length():
    """Does the blocked protocol's verdict depend on the size of the purge?"""
    d = load_revision_data(PROC, SIG, lag=1, reports_pickle=REP)
    des = Design(d, MAIN_BLOCKS)
    base = _auprc(des.Y, _fit_predict(des, EV.loco(d.frame)))
    rows = []
    for g in (0, 30, 60, 90, 120, 180):
        a = _auprc(des.Y, _fit_predict(des, EV.blocked(d.frame, purge=float(g))))
        rows.append({"purge_s": g, "auprc_1s_blocked": a, "auprc_1s_loco": base,
                     "inflation_vs_loco_%": 100 * (a / base - 1)})
    save(pd.DataFrame(rows), "c19_sens_purge")


def burst_cutoff():
    """The quiet-vs-burst split of Section 5.8, at other cutoffs.

    The model is fitted once and the cutoff only re-labels rows, which is the correct
    design: the stratification is a post-hoc view of one set of predictions, not a
    separate experiment.  Burst initiators are reported separately because every burst
    begins on a quiet row, so 'quiet' is not a set of isolated handovers.
    """
    d = load_revision_data(PROC, SIG, lag=1, reports_pickle=REP)
    des = Design(d, MAIN_BLOCKS)
    P = _fit_predict(des, EV.loco(d.frame))
    ts = d.frame["ts"].to_numpy()
    prev = ts - d.frame["t_since_prev_ho_s"].to_numpy()
    rows = []
    for B in (5.0, 10.0, 15.0, 20.0):
        inb = (ts - prev) <= B
        for lab, sel in (("in burst", inb), ("quiet", ~inb)):
            prev_rate = float(des.Y[sel, K1].mean())
            a = _auprc(des.Y, P, sel=sel)
            rows.append({"burst_cutoff_s": B, "stratum": lab, "n_rows": int(sel.sum()),
                         "prevalence": prev_rate, "auprc_1s": a,
                         "lift_1s": a / prev_rate if prev_rate else np.nan})
    save(pd.DataFrame(rows), "c19_sens_burst_cutoff")

    # Is a "quiet" positive row an isolated handover, or the first of a burst?
    nxt = d.frame["t_next_ho_s"].to_numpy()
    init = d.frame["next_is_first_in_burst"].to_numpy(bool)
    pos = (nxt <= 1.0) & np.isfinite(nxt)
    quiet = (ts - prev) > 10.0
    br = []
    for lab, sel in (("quiet rows", quiet & pos), ("in-burst rows", ~quiet & pos)):
        n = int(sel.sum())
        br.append({"positive rows at 1 s": lab, "n": n,
                   "whose handover starts a new burst": int((sel & init).sum()),
                   "share starting a new burst": float((sel & init).sum() / max(n, 1)),
                   "mean score": float(np.nanmean(P[sel, K1]))})
    save(pd.DataFrame(br), "c19_burst_initiators")


def blank_window():
    """The 2 s post-handover blank, varied.  This changes the row set, so the model is
    refitted and the prevalence floor moves with it; the lift is the comparable number."""
    rows = []
    for W in (0.0, 1.0, 2.0, 3.0, 5.0):
        d = load_revision_data(PROC, SIG, lag=1, reports_pickle=REP, blank_s=W)
        des = Design(d, MAIN_BLOCKS)
        P = _fit_predict(des, EV.loco(d.frame))
        prev = float(des.Y[:, K1].mean())
        a = _auprc(des.Y, P)
        rows.append({"blank_s": W, "n_rows": int(len(d.frame)), "prevalence_1s": prev,
                     "auprc_1s": a, "lift_1s": a / prev})
    save(pd.DataFrame(rows), "c19_sens_blank")


if __name__ == "__main__":
    block_length()
    purge_length()
    burst_cutoff()
    blank_window()

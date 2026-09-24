"""Protocols, metrics, event-level scoring and risk control for the revision."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, roc_auc_score

from .data import EDGES

K = len(EDGES)
PURGE_S = 60.0


# ------------------------------------------------------------------ protocols
@dataclass
class Fold:
    name: str
    test: np.ndarray        # bool masks over frame rows
    fit: np.ndarray
    calib: np.ndarray


def _purge(frame: pd.DataFrame, train: np.ndarray, test: np.ndarray, gap: float) -> np.ndarray:
    """Drop training rows within `gap` s of any test row of the same capture."""
    keep = train.copy()
    for cap, g in frame.groupby("capture"):
        te_t = np.sort(g.loc[test[g.index], "ts"].to_numpy())
        if not len(te_t):
            continue
        tr_idx = g.index[train[g.index]]
        tt = frame.loc[tr_idx, "ts"].to_numpy()
        j = np.searchsorted(te_t, tt)
        d_right = np.where(j < len(te_t), te_t[np.clip(j, 0, len(te_t) - 1)] - tt, np.inf)
        d_left = np.where(j > 0, tt - te_t[np.clip(j - 1, 0, None)], np.inf)
        near = np.minimum(np.abs(d_left), np.abs(d_right)) <= gap
        keep[tr_idx[near]] = False
    return keep


def _temporal_calib(frame: pd.DataFrame, train: np.ndarray, frac: float = 0.2):
    """Last `frac` of each training capture (by time) calibrates; purge between."""
    cal = np.zeros(len(frame), bool)
    for cap, g in frame[train].groupby("capture"):
        cut = g["ts"].quantile(1 - frac)
        cal[g.index[g["ts"] >= cut]] = True
    fit = _purge(frame, train & ~cal, cal, PURGE_S)
    return fit, cal


def loco(frame: pd.DataFrame) -> list[Fold]:
    out = []
    for cap in sorted(frame["capture"].unique()):
        te = (frame["capture"] == cap).to_numpy()
        fit, cal = _temporal_calib(frame, ~te)
        out.append(Fold(f"LOCO:{cap}", te, fit, cal))
    return out


def blocked(frame: pd.DataFrame, k: int = 5, purge: float = PURGE_S) -> list[Fold]:
    """Contiguous time blocks within every capture; 60 s purge around the test block."""
    blk = np.zeros(len(frame), int)
    for cap, g in frame.groupby("capture"):
        q = np.floor((g["ts"] - g["ts"].min()) / (g["ts"].max() - g["ts"].min() + 1e-9) * k)
        blk[g.index] = np.clip(q, 0, k - 1)
    out = []
    for f in range(k):
        te = blk == f
        tr = _purge(frame, ~te, te, purge)
        fit, cal = _temporal_calib(frame, tr)
        out.append(Fold(f"blocked:{f}", te, fit, cal))
    return out


def chunk_grouped(frame: pd.DataFrame, k: int = 5, seed: int = 0) -> list[Fold]:
    """The v1 protocol: random 180 s chunks, stratified by capture, no buffer."""
    rng = np.random.default_rng(seed)
    assign = {}
    for cap, g in frame.groupby("capture"):
        ids = g["drive_id"].unique().tolist()
        rng.shuffle(ids)
        assign.update({d: i % k for i, d in enumerate(ids)})
    a = frame["drive_id"].map(assign).to_numpy()
    out = []
    for f in range(k):
        te = a == f
        rest = [d for d, v in assign.items() if v != f]
        rng.shuffle(rest)
        cal_ids = set(rest[: max(1, int(0.2 * len(rest)))])
        cal = frame["drive_id"].isin(cal_ids).to_numpy() & ~te
        out.append(Fold(f"chunk:{f}", te, ~te & ~cal, cal))
    return out


def random_rows(frame: pd.DataFrame, k: int = 5, seed: int = 0) -> list[Fold]:
    rng = np.random.default_rng(seed)
    a = rng.integers(0, k, len(frame))
    out = []
    for f in range(k):
        te = a == f
        rest = ~te
        cal = rest & (rng.random(len(frame)) < 0.2)
        out.append(Fold(f"row:{f}", te, rest & ~cal, cal))
    return out


PROTOCOLS = {"random_row": random_rows, "chunk_grouped": chunk_grouped,
             "blocked_purged": blocked, "loco": loco}
PROTOCOL_LABEL = {"random_row": "Random rows (leaky control)",
                  "chunk_grouped": "Random 180 s chunks (v1 protocol)",
                  "blocked_purged": "Contiguous blocks + 60 s purge",
                  "loco": "Leave one capture out (primary)"}


# ------------------------------------------------------------------ metrics
def ece(y, p, bins: int = 15) -> float:
    order = np.argsort(p)
    parts = np.array_split(order, bins)
    n = len(p)
    return float(sum(len(b) / n * abs(y[b].mean() - p[b].mean()) for b in parts if len(b)))


def horizon_metrics(Y: np.ndarray, P: np.ndarray, mask: np.ndarray | None = None) -> pd.DataFrame:
    rows = []
    for k, e in enumerate(EDGES):
        sel = np.ones(len(Y), bool) if mask is None else mask
        y, p = Y[sel, k], P[sel, k]
        if len(np.unique(y)) < 2:
            continue
        prev = y.mean()
        ap = average_precision_score(y, p)
        rows.append({"horizon_s": e, "n": int(sel.sum()), "prevalence": prev, "auprc": ap,
                     "lift": ap / prev, "auroc": roc_auc_score(y, p), "ece": ece(y, p),
                     "brier": float(np.mean((p - y) ** 2))})
    return pd.DataFrame(rows)


def block_bootstrap(frame: pd.DataFrame, Y, P, n: int = 500, seed: int = 0,
                    stat=average_precision_score, sel: np.ndarray | None = None) -> np.ndarray:
    """(n, K) bootstrap draws; resamples 180 s chunks within each capture.

    Conditional on the four sessions: it does not capture between-day
    variance, which the per-capture (LOCO) spread reports separately.
    """
    rng = np.random.default_rng(seed)
    sel = np.ones(len(frame), bool) if sel is None else sel
    fr = frame[sel]
    groups = {cap: [np.flatnonzero(sel)[np.flatnonzero((fr["drive_id"] == d).to_numpy())]
                    for d in g["drive_id"].unique()]
              for cap, g in fr.groupby("capture")}
    out = np.full((n, K), np.nan)
    for b in range(n):
        idx = np.concatenate([np.concatenate([gl[i] for i in rng.integers(0, len(gl), len(gl))])
                              for gl in groups.values()])
        for k in range(K):
            y = Y[idx, k]
            if len(np.unique(y)) == 2:
                out[b, k] = stat(y, P[idx, k])
    return out


def violations(P: np.ndarray) -> dict:
    d = np.diff(P, axis=1)
    neg = np.maximum(0, -d)
    return {"rows_violating": float((d < -1e-12).any(1).mean()),
            "pairs_violating": float((d < -1e-12).mean()),
            "mean_violation_if_any": float(neg[d < -1e-12].mean()) if (d < -1e-12).any() else 0.0,
            "p95_violation_if_any": float(np.quantile(neg[d < -1e-12], 0.95)) if (d < -1e-12).any() else 0.0,
            "max_violation": float(neg.max())}


# ------------------------------------------------------------------ events
def event_metrics(frame: pd.DataFrame, P: np.ndarray, thr: np.ndarray, events: pd.DataFrame,
                  sel: np.ndarray) -> pd.DataFrame:
    """Event detection, lead time and false-alarm episodes per horizon.

    An event at tau is detected at horizon h if some usable row t with
    tau - h <= t < tau alarms (F_h(t) >= thr_h). Lead time is tau minus the
    first alarming row in that window. A false-alarm episode is a maximal run
    of consecutive alarming rows with no handover in (run start, run end + h].
    """
    fr = frame[sel]
    Ps = P[sel]
    hours = len(fr) / 3600.0
    km = float(fr["km_step"].sum())
    rows = []
    for k, h in enumerate(EDGES):
        alarm = Ps[:, k] >= thr[k]
        n_ev = n_res = n_det = 0
        leads = []
        n_fa = n_ep = 0
        for cap, g in fr.groupby("capture"):
            gi = np.flatnonzero((fr["capture"] == cap).to_numpy())
            ts = fr["ts"].to_numpy()[gi]
            al = alarm[gi]
            t0 = frame.loc[frame.capture == cap, "t"].min() - pd.to_timedelta(
                frame.loc[frame.capture == cap, "ts"].min(), unit="s")
            et = ((events.loc[events.capture == cap, "t"] - t0).dt.total_seconds()).to_numpy()
            et = et[(et >= ts.min()) & (et <= ts.max() + h)]
            order = np.argsort(ts)
            ts, al = ts[order], al[order]
            for tau in et:
                lo, hi = np.searchsorted(ts, tau - h, "left"), np.searchsorted(ts, tau, "left")
                n_ev += 1
                if hi > lo:
                    n_res += 1
                    w = np.flatnonzero(al[lo:hi])
                    if len(w):
                        n_det += 1
                        leads.append(tau - ts[lo + w[0]])
            # alarm episodes
            run_start = None
            for i in range(len(ts) + 1):
                on = i < len(ts) and al[i] and (run_start is None or ts[i] - ts[i - 1] <= 1.0 + 1e-6)
                if on and run_start is None:
                    run_start = i
                elif not on and run_start is not None:
                    s, e_ = ts[run_start], ts[i - 1]
                    n_ep += 1
                    if not ((et > s) & (et <= e_ + h)).any():
                        n_fa += 1
                    run_start = i if (i < len(ts) and al[i]) else None
        rows.append({"horizon_s": h, "events": n_ev, "resolvable_on_grid": n_res,
                     "grid_ceiling": n_res / max(n_ev, 1), "detected": n_det,
                     "detection_rate": n_det / max(n_ev, 1),
                     "alarm_rate_rows": float(alarm.mean()), "alarm_episodes": n_ep,
                     "false_alarm_episodes": n_fa, "false_alarms_per_hour": n_fa / hours,
                     "false_alarms_per_km": n_fa / km if km > 0 else np.nan,
                     "lead_median_s": float(np.median(leads)) if leads else np.nan,
                     "lead_p25_s": float(np.quantile(leads, 0.25)) if leads else np.nan,
                     "lead_p75_s": float(np.quantile(leads, 0.75)) if leads else np.nan,
                     "hours": hours, "km": km})
    return pd.DataFrame(rows)


def thr_at_fpr(y, p, fpr: float) -> float:
    neg = np.sort(p[y == 0])
    if not len(neg):
        return 0.5
    return float(neg[int(np.ceil((1 - fpr) * len(neg))) - 1]) + 1e-12


# ------------------------------------------------------------------ risk control
def event_scores(frame: pd.DataFrame, p: np.ndarray, events: pd.DataFrame,
                 sel: np.ndarray, h: float) -> tuple[np.ndarray, np.ndarray]:
    """Per-handover score and unit, using the detection rule of ``event_metrics``.

    An event at tau scores the maximum model output over the usable rows in
    [tau - h, tau).  An event with no usable row in that window scores -inf, so it
    counts as missed rather than being dropped from the denominator: that is what
    makes an event-level conformal loss comparable with the detection rate of
    Appendix A rather than with the row-level miss rate [C10, round 3].
    """
    fr = frame[sel]
    ps = p[sel]
    ev_unit, ev_score = [], []
    for cap, g in fr.groupby("capture"):
        gi = np.flatnonzero((fr["capture"] == cap).to_numpy())
        ts = fr["ts"].to_numpy()[gi]
        order = np.argsort(ts)
        ts = ts[order]
        sc = ps[gi][order]
        du = fr["drive_id"].to_numpy()[gi][order]
        t0 = frame.loc[frame.capture == cap, "t"].min() - pd.to_timedelta(
            frame.loc[frame.capture == cap, "ts"].min(), unit="s")
        et = ((events.loc[events.capture == cap, "t"] - t0).dt.total_seconds()).to_numpy()
        et = et[(et >= ts.min()) & (et <= ts.max() + h)]
        for tau in et:
            lo, hi = np.searchsorted(ts, tau - h, "left"), np.searchsorted(ts, tau, "left")
            if hi > lo:
                ev_score.append(float(sc[lo:hi].max()))
                ev_unit.append(du[hi - 1])
            else:
                ev_score.append(-np.inf)
                ev_unit.append(du[min(hi, len(du) - 1)])
    return np.asarray(ev_unit), np.asarray(ev_score, dtype=float)


def crc_threshold(unit_ids: np.ndarray, y: np.ndarray, p: np.ndarray, alpha: float,
                  grid: np.ndarray) -> tuple[float, int]:
    """Largest threshold whose CRC-adjusted per-unit miss rate is <= alpha.

    Loss of a unit = fraction of its positive rows scored below the threshold
    (0 for units without positives); B = 1 (Angelopoulos et al., 2024).
    """
    units = np.unique(unit_ids)
    n = len(units)
    pos = y == 1
    # per-unit loss as a function of the threshold
    L = np.zeros((n, len(grid)))
    for i, u in enumerate(units):
        m = (unit_ids == u) & pos
        if m.sum():
            L[i] = (p[m][:, None] < grid[None, :]).mean(0)
    Rhat = L.mean(0)
    ok = (n * Rhat + 1.0) / (n + 1) <= alpha
    if not ok.any():
        return -np.inf, n                       # infeasible: alarm everywhere
    return float(grid[np.flatnonzero(ok).max()]), n

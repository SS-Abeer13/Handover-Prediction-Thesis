"""Event-level evaluation (section 23.2).

A physical handover counts once, however many consecutive samples fire.  For each
real event we ask: was there a warning inside the warning window, and how early
was the *first* one?  Reported alongside false alarms per hour and per kilometre,
because a predictor that warns constantly detects everything and is useless.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from ..utils import get_logger

LOG = get_logger("hoproj.events")


def event_level_metrics(meta: pd.DataFrame, p: np.ndarray, ho: pd.DataFrame,
                        threshold: float, warn_horizon_s: float = 5.0,
                        merge_gap_s: float = 1.0) -> dict:
    """
    meta  : per-prediction rows with columns t, drive_id (aligned with ``p``)
    p     : predicted probability at each row (single horizon, or a fused score)
    ho    : handover event table (drive_id, t)
    """
    meta = meta.reset_index(drop=True).copy()
    meta["p"] = np.asarray(p, float).ravel()
    meta["warn"] = meta["p"] >= threshold

    total_events = 0
    detected = 0
    lead_times: list[float] = []
    alarms_total = 0
    useful_alarms = 0
    obs_seconds = 0.0
    obs_km = 0.0

    for drive_id, grp in meta.groupby("drive_id", sort=False):
        grp = grp.sort_values("t")
        t = grp["t"].to_numpy("datetime64[ns]").astype("int64") / 1e9
        warn = grp["warn"].to_numpy(bool)
        obs_seconds += float(t[-1] - t[0]) if len(t) > 1 else 0.0
        if "dist_in_drive_m" in grp:
            obs_km += float(np.nanmax(grp["dist_in_drive_m"].to_numpy(float))) / 1000.0

        ev_t = ho.loc[ho["drive_id"] == drive_id, "t"]
        ev_t = ev_t.to_numpy("datetime64[ns]").astype("int64") / 1e9 if len(ev_t) else np.empty(0)
        total_events += len(ev_t)

        # alarm episodes: consecutive warning runs merged when closer than merge_gap_s
        episodes = _episodes(t, warn, merge_gap_s)
        alarms_total += len(episodes)
        matched_ep = set()
        for e in ev_t:
            # The label at time t asks about (t, t+h]; the samples that can warn
            # about an event at e are therefore t in [e - h, e), not t <= e.
            window = (t >= e - warn_horizon_s) & (t < e)
            if not window.any():
                continue
            if warn[window].any():
                detected += 1
                first = t[window][np.argmax(warn[window])]
                lead_times.append(float(e - first))
            for k, (a, b) in enumerate(episodes):
                if a <= e and b >= e - warn_horizon_s:
                    matched_ep.add(k)
        useful_alarms += len(matched_ep)

    false_alarms = max(alarms_total - useful_alarms, 0)
    hours = obs_seconds / 3600.0
    return {
        "n_events": int(total_events),
        "n_detected": int(detected),
        "event_detection_rate": detected / total_events if total_events else np.nan,
        "missed_event_rate": 1 - detected / total_events if total_events else np.nan,
        "median_lead_time_s": float(np.median(lead_times)) if lead_times else np.nan,
        "mean_lead_time_s": float(np.mean(lead_times)) if lead_times else np.nan,
        "p25_lead_time_s": float(np.percentile(lead_times, 25)) if lead_times else np.nan,
        "p75_lead_time_s": float(np.percentile(lead_times, 75)) if lead_times else np.nan,
        "n_alarm_episodes": int(alarms_total),
        "n_false_alarm_episodes": int(false_alarms),
        "false_alarms_per_hour": false_alarms / hours if hours > 0 else np.nan,
        "false_alarms_per_km": false_alarms / obs_km if obs_km > 0 else np.nan,
        "observed_hours": hours,
        "observed_km": obs_km,
        "threshold": float(threshold),
    }


def detection_by_horizon(meta: pd.DataFrame, P: np.ndarray, M: np.ndarray, ho: pd.DataFrame,
                         horizons: list[float], thresholds: list[float],
                         warn_horizon_s: float = 5.0) -> pd.DataFrame:
    """Detection rate and lead time per horizon head, at a per-horizon threshold."""
    rows = []
    for j, h in enumerate(horizons):
        sel = M[:, j].astype(bool)
        if sel.sum() == 0:
            continue
        res = event_level_metrics(meta.loc[sel], P[sel, j], ho, thresholds[j],
                                 warn_horizon_s=min(warn_horizon_s, max(h, 1.0)))
        res["horizon_s"] = h
        rows.append(res)
    df = pd.DataFrame(rows)
    return df[["horizon_s"] + [c for c in df.columns if c != "horizon_s"]] if len(df) else df


def _episodes(t: np.ndarray, warn: np.ndarray, merge_gap_s: float) -> list[tuple[float, float]]:
    out: list[list[float]] = []
    for i in np.flatnonzero(warn):
        ts = t[i]
        if out and ts - out[-1][1] <= merge_gap_s:
            out[-1][1] = ts
        else:
            out.append([ts, ts])
    return [(a, b) for a, b in out]

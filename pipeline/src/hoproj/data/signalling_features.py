"""Features the RRC signalling makes available and the model has never seen.

The pipeline parses the signalling log to build ground truth and to attribute
each handover to the A3 profile that fired it, and then throws that channel
away before modelling. Every feature the models use comes from the periodic
CSV: serving RF, GPS, speed, dwell. That is a strange place to stop, because
the signalling carries the two quantities most directly on the causal path
between radio conditions and a handover:

* **How far through the time-to-trigger the UE already is.** The A3 entering
  condition is not a threshold on the instantaneous gap; it is a threshold that
  must hold *continuously* for TTT milliseconds. A sample where the condition
  has held for 300 ms of a 320 ms TTT is a completely different state from one
  where it has just become true, and the gap alone cannot tell them apart.
  This is the mechanism behind the stage 11 finding that the static gap
  discriminates at AUROC 0.566 while dwell reaches 0.865.

* **Whether the UE has recently sent a measurement report.** The network sees
  this in real time. Roughly 39% of reported A3 events convert to a handover,
  so a report is a strong but far from decisive signal - exactly the kind of
  evidence a learned model should weigh rather than a rule should threshold.

Leakage
-------
A measurement report precedes the handover command by ~50-200 ms, which is
inside one 1 Hz sample. Counting reports in the *current* bin would therefore
leak the outcome. Every report feature here is built from strictly earlier
bins: the count over ``(t - k, t - period]``, never ``(t - k, t]``. The unit
test in tests/ asserts this by construction.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from ..utils import get_logger

LOG = get_logger("hoproj.sigfeat")

REPORT_WINDOWS_S = (1.0, 2.0, 3.0, 5.0)
SLOPE_WINDOWS_S = (3.0, 5.0)
SLOPE_FIELDS = ("serving_rsrp", "serving_sinr", "serving_rsrq", "gap_serving_nbr1")


def a3_condition_held(frame: pd.DataFrame) -> pd.Series:
    """Boolean: is the A3 entering condition satisfied at this sample?

    3GPP TS 36.331 clause 5.5.4.4, entering condition A3-1:

        Mn + Ofn + Ocn - Hys > Mp + Ofp + Ocp + Off

    With no per-cell or per-frequency offsets configured in these captures this
    reduces to ``neighbour - serving > Off + Hys``. The pipeline stores
    ``gap_serving_nbr1 = serving - neighbour``, so the condition is

        gap < -(Off + Hys).

    The sign matters: the offsets in these captures are negative as often as
    positive, and plotting the thresholds at raw offset rather than at -offset
    once hid the entire trigger-coverage finding.
    """
    gap = frame.get("gap_serving_nbr1")
    off = frame.get("a3_offset_db")
    hys = frame.get("hysteresis_db")
    if gap is None or off is None:
        return pd.Series(np.zeros(len(frame), dtype=bool), index=frame.index)
    h = hys if hys is not None else pd.Series(np.zeros(len(frame)), index=frame.index)
    return (gap < -(off.astype(float) + h.astype(float).fillna(0.0))).fillna(False)


def _run_length_s(held: np.ndarray, t: np.ndarray, reset: np.ndarray) -> np.ndarray:
    """Seconds for which `held` has been continuously true, reset per group."""
    out = np.zeros(len(held), dtype=float)
    acc = 0.0
    for i in range(len(held)):
        if reset[i] or not held[i]:
            # a new drive, or the condition is not satisfied: the clock is down
            acc = 0.0
        elif held[i - 1]:
            acc += float(t[i] - t[i - 1])
        else:
            # first sample on which the condition holds; it became true somewhere
            # inside the previous inter-sample interval, so credit it with zero
            acc = 0.0
        out[i] = acc
    return out


def ttt_clock(frame: pd.DataFrame) -> pd.DataFrame:
    """How long the A3 condition has held, absolutely and as a fraction of TTT."""
    held = a3_condition_held(frame).to_numpy(bool)
    t = frame["t"].astype("int64").to_numpy() / 1e9
    drive = frame["drive_id"].to_numpy()
    reset = np.r_[True, drive[1:] != drive[:-1]]
    run = _run_length_s(held, t, reset)
    ttt_s = frame.get("time_to_trigger_ms")
    ttt_s = (ttt_s.astype(float) / 1000.0).to_numpy() if ttt_s is not None \
        else np.full(len(frame), np.nan)
    with np.errstate(divide="ignore", invalid="ignore"):
        frac = np.where(ttt_s > 0, run / ttt_s, np.nan)
    return pd.DataFrame({
        "sig_a3_condition_held": held.astype(float),
        "sig_a3_hold_s": run,
        "sig_a3_hold_frac_of_ttt": np.clip(frac, 0, 10),
    }, index=frame.index)


def report_history(frame: pd.DataFrame, reports: pd.DataFrame,
                   period_s: float = 1.0,
                   windows_s: tuple[float, ...] = REPORT_WINDOWS_S) -> pd.DataFrame:
    """Counts of measurement reports in strictly earlier bins.

    The upper edge of every window is ``t - period_s``, not ``t``. A report and
    the handover it triggers are typically 50-200 ms apart, so anything in the
    current bin is contemporaneous with the label rather than predictive of it.
    """
    out = pd.DataFrame(index=frame.index)
    ts = frame["t"].astype("int64").to_numpy() / 1e9
    if not len(reports):
        for w in windows_s:
            out[f"sig_reports_prev{int(w)}s"] = 0.0
            out[f"sig_a3_reports_prev{int(w)}s"] = 0.0
        out["sig_s_since_a3_report"] = np.nan
        return out

    rt_all = np.sort(reports["t"].astype("int64").to_numpy() / 1e9)
    a3 = reports[reports["event_id"] == "A3"]
    rt_a3 = np.sort(a3["t"].astype("int64").to_numpy() / 1e9)

    hi = ts - period_s                       # strictly earlier bins only
    for w in windows_s:
        lo = hi - w
        for tag, arr in (("", rt_all), ("a3_", rt_a3)):
            # half-open (lo, hi]: a report exactly w seconds back belongs to
            # the previous window, not this one, so the windows tile without
            # double-counting a report at a bin boundary
            n = (np.searchsorted(arr, hi, side="right")
                 - np.searchsorted(arr, lo, side="right"))
            out[f"sig_{tag}reports_prev{int(w)}s"] = n.astype(float)

    idx = np.searchsorted(rt_a3, hi, side="right") - 1
    last = np.where(idx >= 0, rt_a3[np.clip(idx, 0, len(rt_a3) - 1)], np.nan)
    out["sig_s_since_a3_report"] = np.clip(hi - last, 0, 120)
    return out


def rf_slopes(frame: pd.DataFrame, period_s: float = 1.0,
              windows_s: tuple[float, ...] = SLOPE_WINDOWS_S,
              fields: tuple[str, ...] = SLOPE_FIELDS) -> pd.DataFrame:
    """Backward-looking rate of change, dB per second, per drive."""
    out = pd.DataFrame(index=frame.index)
    g = frame.groupby("drive_id", sort=False)
    for f in fields:
        if f not in frame.columns:
            continue
        for w in windows_s:
            lag = max(1, int(round(w / period_s)))
            out[f"sig_d{f}_{int(w)}s"] = (g[f].diff(lag) / w).to_numpy()
    return out


def build_signalling_features(frame: pd.DataFrame, reports: pd.DataFrame,
                              period_s: float = 1.0) -> pd.DataFrame:
    """Every signalling-derived feature, aligned to the feature frame's rows."""
    parts = [ttt_clock(frame), report_history(frame, reports, period_s), rf_slopes(frame, period_s)]
    out = pd.concat(parts, axis=1)
    out = out.replace([np.inf, -np.inf], np.nan)
    LOG.info("signalling features: %d columns (%s)", out.shape[1],
             ", ".join(out.columns[:4]) + ", ...")
    return out

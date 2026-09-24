"""The benefit envelope: what a perfect actuator could have bought.

The decision question - "does predicting handovers actually help?" - cannot be
answered by off-policy evaluation on this data. The 3GPP A3 rule is a
deterministic logging policy, so propensities are 0 or 1 and every OPE
estimator collapses to the analyst's own outcome model. Reporting a policy
value here would be the same circularity that appears in the literature, in
better notation.

What *is* identified, by counting alone and with no counterfactual assumption
whatsoever, is an upper bound. For each observed adverse event (a ping-pong, a
re-establishment), ask a purely factual question: did the predictor raise an
alarm at least tau seconds before it? If it did not, no intervention triggered
by this predictor could have prevented that event, whatever the intervention
was. So

    K(tau, lambda) / N

is an upper bound on the fraction of adverse events any downstream action
could have avoided, given this predictor at this operating point.

A real actuator is not perfect. Introducing an efficacy parameter eta in [0, 1]
- the probability that an intervention, given adequate warning, actually
prevents the event - the attainable benefit is eta * K/N. Eta is not estimated
here; it is swept, and the result is reported as a surface over (tau, eta).
That keeps the assumption visible and separate from the measurement.

The cost side is measured the same way: the alarm rate and the false alarms per
hour at the same operating point are what the network pays for that benefit.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from ..utils import get_logger

LOG = get_logger("hoproj.benefit")


def warning_coverage(event_t: np.ndarray, event_drive: np.ndarray,
                     sample_t: np.ndarray, sample_drive: np.ndarray,
                     score: np.ndarray, threshold: float, tau: float,
                     max_lead: float = 10.0) -> np.ndarray:
    """Was an alarm raised in [t_event - max_lead, t_event - tau] on that drive?

    ``tau`` is the minimum lead time an intervention needs to be useful; the
    upper limit keeps an alarm from an unrelated earlier episode from counting.
    """
    flagged = score >= threshold
    out = np.zeros(len(event_t), dtype=bool)
    for d in np.unique(event_drive):
        em = event_drive == d
        sm = sample_drive == d
        st = sample_t[sm]
        sf = flagged[sm]
        if not sm.any():
            continue
        order = np.argsort(st)
        st, sf = st[order], sf[order]
        csum = np.concatenate([[0], np.cumsum(sf.astype(np.int64))])
        for j in np.flatnonzero(em):
            lo = np.searchsorted(st, event_t[j] - max_lead, "left")
            hi = np.searchsorted(st, event_t[j] - tau, "right")
            out[j] = (csum[hi] - csum[lo]) > 0
    return out


def benefit_envelope(events: pd.DataFrame, samples: pd.DataFrame, score: np.ndarray,
                     thresholds: dict[str, float], taus=(0.0, 1.0, 2.0, 3.0, 5.0),
                     etas=(0.25, 0.5, 0.75, 1.0), event_col: str = "is_pingpong",
                     drive_col: str = "drive_id", time_col: str = "t",
                     max_lead: float = 10.0) -> pd.DataFrame:
    """Upper bound on avoidable adverse events, per operating point."""
    st = samples[time_col].to_numpy("datetime64[ns]").astype("int64") / 1e9
    sd = samples[drive_col].to_numpy()
    hours = (samples.groupby(drive_col)[time_col].agg(lambda x: (x.max() - x.min()).total_seconds())
             .sum()) / 3600.0

    sel = events[event_col].to_numpy(bool) if event_col in events else np.ones(len(events), bool)
    ev = events.loc[sel]
    et = ev[time_col].to_numpy("datetime64[ns]").astype("int64") / 1e9
    ed = ev[drive_col].to_numpy()
    N = len(ev)
    if N == 0:
        return pd.DataFrame()

    # A random alarm firing independently at the same rate already covers a
    # surprising fraction of events, because the warning window is several
    # samples wide. Without this reference the envelope flatters itself.
    def _random_reference(p: float, tau: float, period: float = 1.0) -> float:
        w = max(0.0, (max_lead - tau)) / period
        return float(1.0 - (1.0 - p) ** w)

    rows = []
    for name, thr in thresholds.items():
        alarm_rate = float((score >= thr).mean())
        fa_per_h = float((score >= thr).sum()) / max(hours, 1e-9)
        for tau in taus:
            warned = warning_coverage(et, ed, st, sd, score, thr, tau, max_lead)
            K = int(warned.sum())
            ref = _random_reference(alarm_rate, tau)
            for eta in etas:
                rows.append({"operating_point": name, "threshold": thr,
                             "alarm_rate": alarm_rate, "alarms_per_hour": fa_per_h,
                             "min_lead_time_s": tau, "n_adverse_events": N,
                             "n_warned": K, "max_avoidable_frac": K / N,
                             "random_alarm_reference": ref,
                             "lift_over_random": (K / N) / max(ref, 1e-9),
                             "excess_over_random": K / N - ref,
                             "actuator_efficacy": eta,
                             "attainable_benefit_frac": eta * K / N})
    return pd.DataFrame(rows)

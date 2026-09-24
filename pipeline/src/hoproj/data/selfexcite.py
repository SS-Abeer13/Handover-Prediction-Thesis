"""Self-excitation: ping-pong as a Hawkes process rather than a nuisance.

A handover raises the probability of another handover shortly afterwards. The
handover literature treats that as a control problem - tune time-to-trigger,
hysteresis, cell individual offset - and measures it with a ping-pong *rate*,
which is a thresholded count and says nothing about how strongly one event
drives the next.

A self-exciting (Hawkes) process says it directly. With an exponential kernel,

    lambda(t) = mu + alpha * sum_{t_i < t} exp(-beta (t - t_i)),

``mu`` is the background rate driven by geometry and mobility, and the
**branching ratio** ``n = alpha / beta`` is the expected number of offspring
each handover triggers - that is, the fraction of handovers that exist only
because another handover just happened. For a stationary process n < 1, and
1/(1-n) is the mean cluster size.

Each drive is an independent realisation on [0, T_drive]. The log-likelihood
uses Ozaki's recursion, so the cost is linear in the number of events.

References
----------
Hawkes, Biometrika 58(1):83-90 (1971).
Ozaki, Ann. Inst. Statist. Math. 31:145-155 (1979) - the recursive likelihood.
Reinhart, Statistical Science 33(3) (2018) - review of self-exciting processes.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy.optimize import minimize

from ..utils import get_logger

LOG = get_logger("hoproj.selfexcite")


@dataclass
class HawkesFit:
    mu: float
    alpha: float
    beta: float
    loglik: float
    n_events: int
    n_realisations: int
    total_time_s: float

    @property
    def branching_ratio(self) -> float:
        return self.alpha / self.beta

    @property
    def mean_cluster_size(self) -> float:
        n = self.branching_ratio
        return float("inf") if n >= 1 else 1.0 / (1.0 - n)

    @property
    def decay_halflife_s(self) -> float:
        return float(np.log(2.0) / self.beta)

    def as_dict(self) -> dict:
        return {"mu_per_s": self.mu, "alpha": self.alpha, "beta": self.beta,
                "branching_ratio": self.branching_ratio,
                "mean_cluster_size": self.mean_cluster_size,
                "excitation_halflife_s": self.decay_halflife_s,
                "background_share": 1.0 - self.branching_ratio,
                "loglik": self.loglik, "n_events": self.n_events,
                "n_realisations": self.n_realisations,
                "total_time_s": self.total_time_s}


def _nll(theta: np.ndarray, realisations: list[tuple[np.ndarray, float]]) -> float:
    mu, alpha, beta = np.exp(theta)
    total = 0.0
    for ts, T in realisations:
        # compensator
        comp = mu * T
        if ts.size:
            comp += (alpha / beta) * np.sum(1.0 - np.exp(-beta * (T - ts)))
        # log-intensity at events, via Ozaki's recursion
        s = 0.0
        acc = 0.0
        prev = None
        for t in ts:
            if prev is not None:
                acc = np.exp(-beta * (t - prev)) * (1.0 + acc)
            lam = mu + alpha * acc
            if lam <= 0:
                return 1e12
            s += np.log(lam)
            prev = t
        total += s - comp
    return -total


def fit_hawkes(events: pd.DataFrame, samples: pd.DataFrame,
               group: str = "drive_id", time_col: str = "t") -> HawkesFit:
    """Fit a univariate exponential Hawkes process, pooling drives as realisations."""
    spans = samples.groupby(group)[time_col].agg(["min", "max"])
    realisations: list[tuple[np.ndarray, float]] = []
    n_ev = 0
    for g, span in spans.iterrows():
        T = (span["max"] - span["min"]).total_seconds()
        if T <= 0:
            continue
        ev = events.loc[events[group] == g, time_col]
        ts = np.sort((ev - span["min"]).dt.total_seconds().to_numpy()) if len(ev) else np.empty(0)
        ts = ts[(ts >= 0) & (ts <= T)]
        realisations.append((ts, float(T)))
        n_ev += ts.size
    if n_ev < 20:
        raise ValueError(f"too few events to fit a Hawkes process ({n_ev})")

    total_T = sum(T for _, T in realisations)
    rate = n_ev / total_T
    best = None
    # multi-start: the likelihood is not convex and beta is weakly identified
    for b0 in (0.05, 0.2, 0.5, 1.0):
        for frac in (0.2, 0.5, 0.8):
            x0 = np.log([max(rate * (1 - frac), 1e-6), max(b0 * frac, 1e-6), b0])
            r = minimize(_nll, x0, args=(realisations,), method="Nelder-Mead",
                         options={"maxiter": 4000, "xatol": 1e-6, "fatol": 1e-6})
            if best is None or r.fun < best.fun:
                best = r
    mu, alpha, beta = np.exp(best.x)
    fit = HawkesFit(float(mu), float(alpha), float(beta), float(-best.fun),
                    int(n_ev), len(realisations), float(total_T))
    LOG.info("Hawkes fit: mu=%.4f/s alpha=%.4f beta=%.4f -> branching ratio %.3f "
             "(background share %.3f, excitation half-life %.2fs, %d events over %.0fs)",
             fit.mu, fit.alpha, fit.beta, fit.branching_ratio,
             1 - fit.branching_ratio, fit.decay_halflife_s, fit.n_events, fit.total_time_s)
    return fit


def excitation_features(samples: pd.DataFrame, events: pd.DataFrame,
                        betas: tuple[float, ...] = (0.1, 0.3, 1.0),
                        group: str = "drive_id", time_col: str = "t") -> pd.DataFrame:
    """Causal self-excitation terms: sum of exp(-beta (t - t_i)) over PAST events.

    One column per decay rate, so the model can pick its own time constant
    rather than inheriting the single beta of the fitted Hawkes process. Strictly
    causal - an event exactly at ``t`` does not contribute to the value at ``t``.
    """
    out = pd.DataFrame(index=samples.index)
    for b in betas:
        out[f"se_excite_b{str(b).replace('.', 'p')}"] = 0.0
    out["se_n_ho_so_far"] = 0.0
    out["se_t_since_last_ho_s"] = np.nan

    for g, idx in samples.groupby(group).groups.items():
        pos = np.asarray(idx)
        ts = samples.loc[pos, time_col].to_numpy("datetime64[ns]").astype("int64") / 1e9
        ev = events.loc[events[group] == g, time_col]
        if not len(ev):
            out.loc[pos, "se_n_ho_so_far"] = 0.0
            continue
        et = np.sort(ev.to_numpy("datetime64[ns]").astype("int64") / 1e9)
        k = np.searchsorted(et, ts, side="left")          # events strictly before t
        out.loc[pos, "se_n_ho_so_far"] = k.astype(float)
        has = k > 0
        gap = np.full(len(ts), np.nan)
        gap[has] = ts[has] - et[k[has] - 1]
        out.loc[pos, "se_t_since_last_ho_s"] = gap
        for b in betas:
            # cumulative sum trick: sum_j<=k exp(-b(t - e_j)) = exp(-b t) * sum_j exp(b e_j)
            # computed in a shifted frame to avoid overflow
            ref = et[0]
            w = np.concatenate([[0.0], np.cumsum(np.exp(b * (et - ref)))])
            val = np.zeros(len(ts))
            val[has] = np.exp(-b * (ts[has] - ref)) * w[k[has]]
            out.loc[pos, f"se_excite_b{str(b).replace('.', 'p')}"] = val
    return out

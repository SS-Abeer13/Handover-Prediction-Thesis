"""Discrete-time hazard model - the correct formulation of this task.

The pipeline's original target was four independent binary labels ("a handover
occurs within 1 / 2 / 3 / 5 s"). That is a discrete-time survival model with the
survival structure deleted: nothing constrains
``P(T<=1) <= P(T<=2) <= P(T<=3) <= P(T<=5)``, right-censoring at the end of a
drive is handled only by dropping tail rows, and the four heads cannot share
statistical strength.

The hazard formulation fixes all three. Time is partitioned into bins whose
upper edges are exactly the horizons of interest, and the model estimates the
conditional hazard

    h_k(x) = P(T in bin k | T >= start of bin k, x),

from which every horizon follows by the product-limit identity

    F(edge_k | x) = 1 - prod_{j<=k} (1 - h_j(x)).

Monotonicity is then true by construction rather than by luck, and censored
rows contribute to every bin they survived instead of being discarded.

Implementation note: this is deliberately *not* a neural model. The data is
long-format (one row per sample x at-risk bin) with the bin index as a feature,
so a single binary LightGBM estimates all hazards at once. The model that
already wins on this data keeps winning; only the target changes.

References
----------
Gensheimer & Narasimhan, PeerJ 7:e6257 (2019) - discrete-time logistic hazard.
Kvamme & Borgan, Lifetime Data Analysis 27:710-736 (2021) - discretisation
schemes; finds the binning matters more than the architecture.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from ..utils import get_logger

LOG = get_logger("hoproj.hazard")


@dataclass
class HazardData:
    X: pd.DataFrame          # long-format design matrix (features + bin index)
    y: np.ndarray            # hazard indicator
    row_of: np.ndarray       # index of the originating sample row
    bin_of: np.ndarray       # bin index of each long row
    n_rows: int              # number of original sample rows
    edges: list[float]


def build_long(features: pd.DataFrame, t_to_next: np.ndarray, t_to_end: np.ndarray,
               edges: list[float], valid: np.ndarray | None = None) -> HazardData:
    """Expand samples into (sample x at-risk bin) rows.

    ``t_to_next`` is the observed time to the next handover (NaN if none occurs
    before the drive ends) and ``t_to_end`` the time remaining in the drive, so
    ``min(t_to_next, t_to_end)`` is the follow-up time and the observation is
    censored wherever ``t_to_next`` is NaN or exceeds ``t_to_end``.
    """
    n = len(features)
    if valid is None:
        valid = np.ones(n, dtype=bool)
    lo = np.array([0.0] + list(edges[:-1]), dtype=float)
    hi = np.array(edges, dtype=float)

    T = np.where(np.isfinite(t_to_next), t_to_next, np.inf)
    C = np.asarray(t_to_end, dtype=float)
    event = np.isfinite(T) & (T <= C)
    follow = np.minimum(T, C)

    rows, bins, ys = [], [], []
    for k in range(len(edges)):
        # at risk in bin k if follow-up reaches past the bin's lower edge...
        at_risk = valid & (follow > lo[k])
        # ...and, for a censored subject, the whole bin must be observed
        at_risk &= event | (follow >= hi[k])
        hazard = at_risk & event & (follow > lo[k]) & (follow <= hi[k])
        idx = np.flatnonzero(at_risk)
        rows.append(idx)
        bins.append(np.full(idx.size, k, dtype=np.int16))
        ys.append(hazard[idx].astype(np.int8))

    row_of = np.concatenate(rows)
    bin_of = np.concatenate(bins)
    y = np.concatenate(ys)
    X = features.iloc[row_of].reset_index(drop=True)
    X = X.assign(_bin=bin_of.astype(np.int16))
    LOG.info("hazard long format: %d sample rows -> %d at-risk rows, "
             "hazard rate per bin %s", int(valid.sum()), len(y),
             {k: round(float(y[bin_of == k].mean()), 4) for k in range(len(edges))})
    return HazardData(X, y, row_of, bin_of, n, list(edges))


def cumulative_incidence(hazards: np.ndarray) -> np.ndarray:
    """(n, K) per-bin hazards -> (n, K) cumulative incidence, monotone by construction."""
    surv = np.cumprod(1.0 - np.clip(hazards, 1e-9, 1 - 1e-9), axis=1)
    return 1.0 - surv


def predict_incidence(model, features: pd.DataFrame, edges: list[float],
                      predict_fn=None) -> np.ndarray:
    """Score every sample in every bin and convert to cumulative incidence."""
    n = len(features)
    H = np.zeros((n, len(edges)), dtype=float)
    for k in range(len(edges)):
        Xk = features.assign(_bin=np.int16(k))
        p = predict_fn(model, Xk) if predict_fn is not None else model.predict_proba(Xk)[:, 1]
        H[:, k] = np.asarray(p, dtype=float).ravel()
    return cumulative_incidence(H)


def monotonicity_violations(P: np.ndarray) -> dict:
    """How often a set of per-horizon probabilities decreases with the horizon.

    Zero by construction for the hazard model; reported for the independent
    multi-head baseline, where it is a direct measure of the incoherence the
    hazard formulation removes.
    """
    d = np.diff(P, axis=1)
    return {"violating_rows_frac": float((d < 0).any(axis=1).mean()),
            "violating_pairs_frac": float((d < 0).mean()),
            "max_violation": float(np.maximum(0.0, -d).max()) if d.size else 0.0,
            "mean_violation_when_violating": float(np.maximum(0.0, -d)[d < 0].mean())
            if (d < 0).any() else 0.0}

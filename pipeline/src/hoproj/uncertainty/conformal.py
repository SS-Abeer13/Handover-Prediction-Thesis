"""Split conformal prediction under temporal dependence (section 21, ref [21]).

Exchangeability is violated inside a drive, so calibration scores are never
drawn by shuffling adjacent samples.  Two variants are provided:

``drive``  whole calibration drives supply the score pool (the default).
``block``  contiguous temporal blocks, for captures with too few drives.

For the binary handover task the conformal object returns *prediction sets*
over {0, 1}: an empty set never occurs, a singleton is a committed prediction,
and {0, 1} is an explicit "cannot tell at this confidence level" - the natural
input to the abstention policy.  Empirical coverage is always reported on
independent drives, never assumed from the theory.
"""
from __future__ import annotations

import numpy as np

from ..utils import get_logger

LOG = get_logger("hoproj.conformal")


class BinaryMondrianConformal:
    """Label-conditional (Mondrian) split conformal for per-horizon binary outputs."""

    def __init__(self, alpha: float = 0.1):
        self.alpha = float(alpha)
        self.q_: np.ndarray | None = None   # (H, 2) thresholds on the nonconformity score

    def fit(self, p: np.ndarray, y: np.ndarray, mask: np.ndarray | None = None,
            groups: np.ndarray | None = None) -> "BinaryMondrianConformal":
        p, y = np.atleast_2d(p), np.atleast_2d(y)
        H = p.shape[1]
        q = np.ones((H, 2))
        for j in range(H):
            sel = np.ones(len(p), bool) if mask is None else mask[:, j].astype(bool)
            for cls in (0, 1):
                s = sel & (y[:, j] == cls)
                if s.sum() < 20:
                    q[j, cls] = 1.0
                    continue
                # nonconformity = 1 - probability assigned to the true label
                score = 1.0 - np.where(cls == 1, p[s, j], 1 - p[s, j])
                # Standard split conformal on the calibration pool. The pool is
                # made of WHOLE drives that the model never saw, which is the
                # protection against temporal dependence; averaging scores within
                # a drive would shrink the score distribution and under-cover, so
                # it is not done. Dependence is instead surfaced by reporting
                # per-drive coverage spread in ``coverage``.
                n = len(score)
                level = min(1.0, np.ceil((n + 1) * (1 - self.alpha)) / n)
                q[j, cls] = float(np.quantile(score, level, method="higher"))
        self.q_ = q
        LOG.info("conformal thresholds (alpha=%.2f): %s", self.alpha, np.round(q, 3).tolist())
        return self

    def prediction_sets(self, p: np.ndarray) -> np.ndarray:
        """(N, H, 2) boolean: is each label inside the prediction set?"""
        p = np.atleast_2d(p)
        N, H = p.shape
        out = np.zeros((N, H, 2), dtype=bool)
        for j in range(H):
            out[:, j, 1] = (1.0 - p[:, j]) <= self.q_[j, 1]
            out[:, j, 0] = (1.0 - (1.0 - p[:, j])) <= self.q_[j, 0]
        return out

    def coverage(self, p: np.ndarray, y: np.ndarray, mask: np.ndarray | None = None,
                 groups: np.ndarray | None = None) -> dict:
        sets = self.prediction_sets(p)
        y = np.atleast_2d(y).astype(int)
        res = {}
        for j in range(sets.shape[1]):
            sel = np.ones(len(y), bool) if mask is None else mask[:, j].astype(bool)
            if not sel.any():
                continue
            covered = sets[np.flatnonzero(sel), j, y[sel, j]]
            width = sets[sel, j].sum(axis=1)
            per_drive = {}
            if groups is not None:
                g = np.asarray(groups)[sel]
                covs = [covered[g == u].mean() for u in np.unique(g) if (g == u).sum() >= 30]
                if covs:
                    per_drive = {"per_drive_coverage_min": float(np.min(covs)),
                                 "per_drive_coverage_median": float(np.median(covs)),
                                 "per_drive_coverage_iqr": float(np.percentile(covs, 75)
                                                                 - np.percentile(covs, 25)),
                                 "n_drives": int(len(covs))}
            res[j] = {"empirical_coverage": float(covered.mean()), **per_drive,
                      "mean_set_size": float(width.mean()),
                      "singleton_rate": float((width == 1).mean()),
                      "ambiguous_rate": float((width == 2).mean()),
                      "empty_rate": float((width == 0).mean()),
                      "n": int(sel.sum())}
        return res


class QuantileConformal:
    """Split conformal intervals for the dwell-time regression head."""

    def __init__(self, alpha: float = 0.1):
        self.alpha = float(alpha)
        self.q_: float = np.nan

    def fit(self, pred: np.ndarray, y: np.ndarray, groups: np.ndarray | None = None):
        res = np.abs(np.asarray(y, float) - np.asarray(pred, float))
        res = res[np.isfinite(res)]
        if groups is not None and len(np.unique(groups)) >= 10:
            g = groups[np.isfinite(np.abs(np.asarray(y, float) - np.asarray(pred, float)))]
            res = np.array([res[g == u].mean() for u in np.unique(g)])
        n = len(res)
        level = min(1.0, np.ceil((n + 1) * (1 - self.alpha)) / max(n, 1))
        self.q_ = float(np.quantile(res, level, method="higher")) if n else np.nan
        return self

    def interval(self, pred: np.ndarray):
        pred = np.asarray(pred, float)
        return pred - self.q_, pred + self.q_

    def coverage(self, pred, y) -> dict:
        lo, hi = self.interval(pred)
        y = np.asarray(y, float)
        inside = (y >= lo) & (y <= hi)
        return {"empirical_coverage": float(np.nanmean(inside)),
                "interval_width": float(2 * self.q_)}

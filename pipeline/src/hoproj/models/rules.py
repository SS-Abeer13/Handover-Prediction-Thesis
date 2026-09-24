"""Trivial and rule baselines (section 18).

These exist so that every learned number has something honest to beat.  An
AUPRC that only just clears the no-handover persistence baseline is not a result.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


class PersistenceBaseline:
    """Always predicts "no handover". Its AUPRC equals the positive prevalence."""

    name = "persistence"

    def fit(self, *_args, **_kwargs):
        return self

    def predict_proba(self, X: pd.DataFrame | np.ndarray, n_outputs: int = 1) -> np.ndarray:
        n = len(X)
        return np.zeros((n, n_outputs), dtype=float)


class RfGapRule:
    """A3-inspired rule: score rises as the best neighbour overtakes the serving cell.

    score = sigma( (gap_threshold - gap) / 2 + trend_term )

    with ``gap = RSRP_serving - RSRP_best_neighbour`` and a trend term driven by
    the serving-cell RSRP slope.  Monotone in the same quantities a network uses
    for an A3 event, so it is a fair non-learned comparator.  No parameters are
    fitted on the data; the two constants come from config.
    """

    name = "rf_gap_rule"

    def __init__(self, gap_db: float = 2.0, trend_db_per_s: float = -1.0, **_):
        self.gap_db = float(gap_db)
        self.trend_db_per_s = float(trend_db_per_s)
        self.cols_: dict[str, str | None] = {}

    def fit(self, X: pd.DataFrame, *_args, **_kwargs):
        self.cols_ = {
            "gap": _pick(X, ["gap_serving_best_nbr", "gap_serving_nbr1"]),
            "slope": _pick(X, [c for c in X.columns if c.startswith("serving_rsrp_slope")]
                           + ["serving_rsrp_d1"]),
            "streak": _pick(X, ["nbr_better_streak_s"]),
        }
        return self

    def predict_proba(self, X: pd.DataFrame, n_outputs: int = 1) -> np.ndarray:
        gap_col = self.cols_.get("gap")
        gap = X[gap_col].to_numpy(float) if gap_col else np.full(len(X), 10.0)
        slope_col = self.cols_.get("slope")
        slope = X[slope_col].to_numpy(float) if slope_col else np.zeros(len(X))
        streak_col = self.cols_.get("streak")
        streak = X[streak_col].to_numpy(float) if streak_col else np.zeros(len(X))
        z = (self.gap_db - np.nan_to_num(gap, nan=10.0)) / 2.0
        z += np.clip(-np.nan_to_num(slope) / abs(self.trend_db_per_s), -3, 3)
        z += np.clip(np.nan_to_num(streak) / 3.0, 0, 3)
        p = 1.0 / (1.0 + np.exp(-z))
        return np.tile(p[:, None], (1, n_outputs))


def _pick(X: pd.DataFrame, candidates) -> str | None:
    for c in candidates:
        if c in X.columns:
            return c
    return None


RULES = {"persistence": PersistenceBaseline, "rf_gap": RfGapRule}

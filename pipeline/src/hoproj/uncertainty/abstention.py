"""Selective prediction: thresholds, risk-coverage curves, accept/reject (section 22).

The abstention threshold tau is chosen on validation + calibration drives only.
The external route is scored with the frozen tau; its acceptance rate is a
*result*, never an input to the choice of tau.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from ..utils import get_logger

LOG = get_logger("hoproj.abstention")


def select_threshold(score: np.ndarray, target_coverage: float) -> float:
    """tau such that a fraction ``target_coverage`` of in-distribution samples is accepted."""
    score = np.asarray(score, float)
    score = score[np.isfinite(score)]
    if len(score) == 0:
        return np.inf
    return float(np.quantile(score, np.clip(target_coverage, 0.0, 1.0)))


def risk_coverage_curve(y: np.ndarray, p: np.ndarray, score: np.ndarray,
                        thresholds: list[float] | None = None,
                        coverages: list[float] | None = None,
                        decision_threshold: float = 0.5,
                        taus: dict[float, float] | None = None) -> pd.DataFrame:
    """Risk as a function of coverage, where samples with high ``score`` are rejected.

    ``risk``         error rate among accepted samples
    ``fn_risk``      false negatives per accepted positive - the mobility-critical error
    ``auprc``        AUPRC recomputed on the accepted subset
    """
    from sklearn.metrics import average_precision_score

    y = np.asarray(y, float).ravel()
    p = np.asarray(p, float).ravel()
    score = np.asarray(score, float).ravel()
    ok = np.isfinite(y) & np.isfinite(p) & np.isfinite(score)
    y, p, score = y[ok], p[ok], score[ok]
    coverages = coverages or [1.0, 0.95, 0.9, 0.8, 0.7, 0.6, 0.5]
    rows = []
    for cov in coverages:
        tau = (taus or {}).get(cov, select_threshold(score, cov))
        acc = score <= tau
        if acc.sum() < 10:
            continue
        ya, pa = y[acc], p[acc]
        pred = (pa >= decision_threshold).astype(float)
        tp = float(((pred == 1) & (ya == 1)).sum())
        fn = float(((pred == 0) & (ya == 1)).sum())
        fp = float(((pred == 1) & (ya == 0)).sum())
        rows.append({
            "target_coverage": cov,
            "tau": tau,
            "realised_coverage": float(acc.mean()),
            "n_accepted": int(acc.sum()),
            "risk": float((pred != ya).mean()),
            "fn_risk": fn / max(tp + fn, 1.0),
            "fp_rate": fp / max((ya == 0).sum(), 1.0),
            "positive_rate_accepted": float(ya.mean()),
            "auprc": float(average_precision_score(ya, pa)) if len(np.unique(ya)) > 1 else np.nan,
        })
    return pd.DataFrame(rows)


def apply_policy(p: np.ndarray, score: np.ndarray, tau: float,
                 decision_threshold: float = 0.5) -> pd.DataFrame:
    accept = np.asarray(score, float) <= tau
    return pd.DataFrame({
        "accepted": accept,
        "decision": np.where(accept, (np.asarray(p, float) >= decision_threshold).astype(int), -1),
        "p": np.asarray(p, float),
        "ood_score": np.asarray(score, float),
    })


def policy_summary(df: pd.DataFrame, y: np.ndarray) -> dict:
    y = np.asarray(y, float)
    acc = df["accepted"].to_numpy(bool)
    out = {"coverage": float(acc.mean()), "n": int(len(df))}
    if acc.any():
        pred = df.loc[acc, "decision"].to_numpy(float)
        ya = y[acc]
        out.update({
            "accepted_error_rate": float((pred != ya).mean()),
            "accepted_false_negatives": int(((pred == 0) & (ya == 1)).sum()),
            "accepted_false_positives": int(((pred == 1) & (ya == 0)).sum()),
        })
    if (~acc).any():
        out["abstained_positive_rate"] = float(y[~acc].mean())
    return out

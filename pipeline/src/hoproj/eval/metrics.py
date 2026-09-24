"""Sample-level metrics for a heavily imbalanced forecasting problem (section 23.1).

Accuracy is deliberately absent from the primary set. AUPRC is primary; recall at
a fixed false-positive rate is the operationally meaningful secondary, because a
mobility controller has a false-alarm budget, not an accuracy budget.
"""
from __future__ import annotations

import numpy as np
from sklearn.metrics import (average_precision_score, brier_score_loss,
                             precision_recall_curve, roc_auc_score, roc_curve)

from ..uncertainty.calibration import expected_calibration_error


def recall_at_fpr(y: np.ndarray, p: np.ndarray, fpr_target: float) -> tuple[float, float]:
    """Recall achievable at a given FPR, and the threshold that achieves it."""
    y, p = np.asarray(y, float), np.asarray(p, float)
    if len(np.unique(y)) < 2:
        return float("nan"), float("nan")
    fpr, tpr, thr = roc_curve(y, p)
    idx = np.searchsorted(fpr, fpr_target, side="right") - 1
    idx = int(np.clip(idx, 0, len(thr) - 1))
    return float(tpr[idx]), float(thr[idx])


def precision_at_recall(y: np.ndarray, p: np.ndarray, recall_target: float) -> float:
    y, p = np.asarray(y, float), np.asarray(p, float)
    if len(np.unique(y)) < 2:
        return float("nan")
    prec, rec, _ = precision_recall_curve(y, p)
    ok = rec >= recall_target
    return float(prec[ok].max()) if ok.any() else float("nan")


def best_f1(y: np.ndarray, p: np.ndarray) -> tuple[float, float]:
    y, p = np.asarray(y, float), np.asarray(p, float)
    if len(np.unique(y)) < 2:
        return float("nan"), 0.5
    prec, rec, thr = precision_recall_curve(y, p)
    f1 = 2 * prec * rec / np.maximum(prec + rec, 1e-12)
    i = int(np.nanargmax(f1))
    return float(f1[i]), float(thr[min(i, len(thr) - 1)])


def classification_metrics(y: np.ndarray, p: np.ndarray,
                           fixed_fpr=(0.01, 0.05, 0.10)) -> dict:
    y = np.asarray(y, float).ravel()
    p = np.asarray(p, float).ravel()
    ok = np.isfinite(y) & np.isfinite(p)
    y, p = y[ok], p[ok]
    out = {"n": int(len(y)), "positive_rate": float(y.mean()) if len(y) else np.nan}
    if len(y) == 0 or len(np.unique(y)) < 2:
        return {**out, "auprc": np.nan, "auroc": np.nan, "brier": np.nan,
                "nll": np.nan, "ece": np.nan, "f1_best": np.nan}
    out["auprc"] = float(average_precision_score(y, p))
    out["auprc_lift"] = out["auprc"] / max(out["positive_rate"], 1e-12)
    out["auroc"] = float(roc_auc_score(y, p))
    out["brier"] = float(brier_score_loss(y, p))
    q = np.clip(p, 1e-7, 1 - 1e-7)
    out["nll"] = float(-np.mean(y * np.log(q) + (1 - y) * np.log(1 - q)))
    out["ece"] = expected_calibration_error(y, p)
    f1, thr = best_f1(y, p)
    out["f1_best"], out["f1_best_threshold"] = f1, thr
    for f in fixed_fpr:
        r, t = recall_at_fpr(y, p, f)
        out[f"recall_at_fpr{f:g}"] = r
        out[f"threshold_at_fpr{f:g}"] = t
    out["precision_at_recall0.5"] = precision_at_recall(y, p, 0.5)
    out["precision_at_recall0.8"] = precision_at_recall(y, p, 0.8)
    return out


def regression_metrics(y: np.ndarray, pred: np.ndarray, quantile: float | None = None) -> dict:
    y, pred = np.asarray(y, float).ravel(), np.asarray(pred, float).ravel()
    ok = np.isfinite(y) & np.isfinite(pred)
    y, pred = y[ok], pred[ok]
    if len(y) == 0:
        return {"mae": np.nan, "rmse": np.nan, "medae": np.nan, "n": 0}
    err = pred - y
    out = {"n": int(len(y)), "mae": float(np.abs(err).mean()),
           "rmse": float(np.sqrt((err ** 2).mean())),
           "medae": float(np.median(np.abs(err))),
           "bias": float(err.mean())}
    if quantile is not None:
        out[f"quantile_loss_{quantile:g}"] = float(
            np.mean(np.maximum(quantile * -err, (quantile - 1) * -err)))
    return out


def multi_horizon_table(Y: np.ndarray, P: np.ndarray, M: np.ndarray,
                        horizons: list[float], fixed_fpr=(0.01, 0.05, 0.10)) -> "pd.DataFrame":
    import pandas as pd

    rows = []
    for j, h in enumerate(horizons):
        sel = M[:, j].astype(bool)
        met = classification_metrics(Y[sel, j], P[sel, j], fixed_fpr)
        met["horizon_s"] = h
        rows.append(met)
    df = pd.DataFrame(rows)
    return df[["horizon_s"] + [c for c in df.columns if c != "horizon_s"]]

"""Probability calibration on dedicated complete-drive calibration data (section 21).

Temperature scaling fits one scalar per horizon on the calibration drives only.
Those drives are excluded from gradient descent *and* from early stopping, so the
temperature is not chosen on data the model has already optimised against.
"""
from __future__ import annotations

import numpy as np
from scipy.optimize import minimize_scalar

from ..utils import get_logger, read_json, write_json

LOG = get_logger("hoproj.calibration")
EPS = 1e-7


def _logit(p: np.ndarray) -> np.ndarray:
    p = np.clip(p, EPS, 1 - EPS)
    return np.log(p / (1 - p))


class TemperatureScaler:
    """One temperature per output column; T > 1 softens over-confidence."""

    def __init__(self):
        self.T_: np.ndarray | None = None

    def fit(self, p: np.ndarray, y: np.ndarray, mask: np.ndarray | None = None) -> "TemperatureScaler":
        p = np.atleast_2d(p)
        y = np.atleast_2d(y)
        H = p.shape[1]
        T = np.ones(H)
        for j in range(H):
            sel = np.ones(len(p), bool) if mask is None else mask[:, j].astype(bool)
            if sel.sum() < 20 or len(np.unique(y[sel, j])) < 2:
                continue
            z = _logit(p[sel, j])
            yy = y[sel, j].astype(float)

            def nll(t: float) -> float:
                t = max(t, 1e-3)
                q = 1.0 / (1.0 + np.exp(-z / t))
                q = np.clip(q, EPS, 1 - EPS)
                return float(-np.mean(yy * np.log(q) + (1 - yy) * np.log(1 - q)))

            res = minimize_scalar(nll, bounds=(0.05, 20.0), method="bounded")
            T[j] = float(res.x)
        self.T_ = T
        LOG.info("fitted temperatures: %s", np.round(T, 3).tolist())
        return self

    def transform(self, p: np.ndarray) -> np.ndarray:
        if self.T_ is None:
            return p
        z = _logit(np.atleast_2d(p))
        return 1.0 / (1.0 + np.exp(-z / self.T_[None, :]))

    def save(self, path):
        write_json({"T": None if self.T_ is None else self.T_.tolist()}, path)

    @classmethod
    def load(cls, path):
        obj = cls()
        T = read_json(path).get("T")
        obj.T_ = None if T is None else np.asarray(T, float)
        return obj


class IsotonicCalibrator:
    """Per-horizon isotonic regression; more flexible, needs more calibration data."""

    def __init__(self):
        self.models_: list = []

    def fit(self, p, y, mask=None):
        from sklearn.isotonic import IsotonicRegression

        p, y = np.atleast_2d(p), np.atleast_2d(y)
        self.models_ = []
        for j in range(p.shape[1]):
            sel = np.ones(len(p), bool) if mask is None else mask[:, j].astype(bool)
            if sel.sum() < 50 or len(np.unique(y[sel, j])) < 2:
                self.models_.append(None)
                continue
            ir = IsotonicRegression(out_of_bounds="clip", y_min=0.0, y_max=1.0)
            ir.fit(p[sel, j], y[sel, j])
            self.models_.append(ir)
        return self

    def transform(self, p):
        p = np.atleast_2d(p)
        cols = [m.predict(p[:, j]) if m is not None else p[:, j]
                for j, m in enumerate(self.models_)]
        return np.column_stack(cols)


def build_calibrator(kind: str):
    return {"temperature": TemperatureScaler, "isotonic": IsotonicCalibrator}.get(
        kind, TemperatureScaler)()


def expected_calibration_error(y: np.ndarray, p: np.ndarray, n_bins: int = 15) -> float:
    y, p = np.asarray(y, float).ravel(), np.asarray(p, float).ravel()
    ok = np.isfinite(y) & np.isfinite(p)
    y, p = y[ok], p[ok]
    if len(y) == 0:
        return float("nan")
    edges = np.linspace(0, 1, n_bins + 1)
    idx = np.clip(np.digitize(p, edges[1:-1]), 0, n_bins - 1)
    ece = 0.0
    for b in range(n_bins):
        sel = idx == b
        if not sel.any():
            continue
        ece += sel.mean() * abs(y[sel].mean() - p[sel].mean())
    return float(ece)


def reliability_curve(y: np.ndarray, p: np.ndarray, n_bins: int = 15):
    y, p = np.asarray(y, float).ravel(), np.asarray(p, float).ravel()
    edges = np.linspace(0, 1, n_bins + 1)
    idx = np.clip(np.digitize(p, edges[1:-1]), 0, n_bins - 1)
    conf, acc, cnt = [], [], []
    for b in range(n_bins):
        sel = idx == b
        if not sel.any():
            continue
        conf.append(float(p[sel].mean())); acc.append(float(y[sel].mean())); cnt.append(int(sel.sum()))
    return np.array(conf), np.array(acc), np.array(cnt)

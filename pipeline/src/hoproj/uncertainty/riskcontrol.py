"""Conformal risk control: a distribution-free bound on missed handovers.

Split conformal controls *coverage*. Coverage is not the quantity an operator
cares about; the quantity is **how many imminent handovers the alarm misses**.
Conformal risk control generalises conformal prediction from coverage to the
expected value of any monotone loss, so the false-negative rate can be bounded
directly (Angelopoulos, Bates, Fisch, Lei & Schuster, ICLR 2024).

The guarantee. For a threshold parameter ``lambda`` with a loss
``L(lambda)`` that is non-increasing as the alarm becomes more eager, choosing

    lambda_hat = inf { lambda : (n R_hat(lambda) + B) / (n + 1) <= alpha }

gives ``E[L_{n+1}(lambda_hat)] <= alpha`` for a fresh exchangeable unit, where
``R_hat`` is the mean loss over the n calibration units and ``B`` bounds the
loss (here B = 1).

**The exchangeable unit is the drive, not the sample.** Samples one second
apart on the same drive are not exchangeable with samples from another drive -
they share a route, a vehicle, a radio environment and a cell set. Calibrating
per sample would report a guarantee that does not hold. The calibration unit
here is therefore a whole drive: each drive contributes one loss value, and
``n`` is the number of calibration drives. This costs statistical efficiency
(tens of units instead of thousands) and buys a guarantee that is actually
true. See Dunn, Wasserman & Ramdas, JASA 118(544) (2023) on two-layer
hierarchical conformal, and Barber, Candes, Ramdas & Tibshirani, Annals of
Statistics 51(2) (2023) for the non-exchangeable case.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from ..utils import get_logger

LOG = get_logger("hoproj.riskcontrol")


@dataclass
class RiskControlResult:
    alpha: float
    lambda_hat: float
    n_calib_units: int
    calib_risk: float
    test_risk: float
    test_alarm_rate: float
    per_unit_test_risk: np.ndarray
    grid: np.ndarray
    calib_risk_curve: np.ndarray

    def as_dict(self) -> dict:
        r = self.per_unit_test_risk
        r = r[np.isfinite(r)]
        return {"alpha": self.alpha, "lambda_hat": self.lambda_hat,
                "n_calib_drives": self.n_calib_units,
                "calibration_risk": self.calib_risk,
                "test_fnr": self.test_risk,
                "test_alarm_rate": self.test_alarm_rate,
                "per_drive_fnr_median": float(np.median(r)) if r.size else np.nan,
                "per_drive_fnr_p90": float(np.percentile(r, 90)) if r.size else np.nan,
                "per_drive_fnr_max": float(r.max()) if r.size else np.nan,
                "drives_over_alpha_frac": float((r > self.alpha).mean()) if r.size else np.nan}


def _fnr_per_unit(y: np.ndarray, p: np.ndarray, units: np.ndarray,
                  lam: float) -> np.ndarray:
    """Missed-positive fraction within each unit, at alarm threshold ``lam``."""
    out = []
    for u in np.unique(units):
        m = units == u
        pos = y[m] == 1
        if not pos.any():
            out.append(np.nan)            # a drive with no event carries no FNR
            continue
        out.append(float((p[m][pos] < lam).mean()))
    return np.asarray(out, dtype=float)


def conformal_risk_control(y_cal: np.ndarray, p_cal: np.ndarray, u_cal: np.ndarray,
                           y_te: np.ndarray, p_te: np.ndarray, u_te: np.ndarray,
                           alpha: float = 0.10, n_grid: int = 200,
                           loss_bound: float = 1.0) -> RiskControlResult:
    """Pick the alarm threshold that bounds the expected per-drive miss rate."""
    grid = np.unique(np.concatenate([[0.0], np.quantile(p_cal, np.linspace(0, 1, n_grid)), [1.0]]))
    grid = np.sort(grid)[::-1]                       # strict -> eager
    n_units = len(np.unique(u_cal))

    curve = np.empty(len(grid))
    lam_hat = 0.0
    for i, lam in enumerate(grid):
        r = _fnr_per_unit(y_cal, p_cal, u_cal, lam)
        r = r[np.isfinite(r)]
        rhat = float(r.mean()) if r.size else 1.0
        curve[i] = rhat
        n = max(r.size, 1)
        if (n * rhat + loss_bound) / (n + 1) <= alpha:
            lam_hat = float(lam)
            break
    else:
        lam_hat = 0.0                                # alarm always on

    per_unit = _fnr_per_unit(y_te, p_te, u_te, lam_hat)
    finite = per_unit[np.isfinite(per_unit)]
    result = RiskControlResult(
        alpha=alpha, lambda_hat=lam_hat, n_calib_units=n_units,
        calib_risk=float(curve[:len(grid)][min(i, len(curve) - 1)]),
        test_risk=float(finite.mean()) if finite.size else np.nan,
        test_alarm_rate=float((p_te >= lam_hat).mean()),
        per_unit_test_risk=per_unit, grid=grid, calib_risk_curve=curve)
    LOG.info("CRC alpha=%.2f -> lambda=%.4f | calib risk %.3f | test FNR %.3f "
             "| alarm rate %.3f | %d calibration drives",
             alpha, lam_hat, result.calib_risk, result.test_risk,
             result.test_alarm_rate, n_units)
    return result


def naive_sample_threshold(y_cal: np.ndarray, p_cal: np.ndarray, alpha: float) -> float:
    """The tempting shortcut: pick the threshold that hits the target FNR pooled
    over calibration SAMPLES, ignoring drive structure. Reported alongside the
    conformal threshold to show what the exchangeability violation costs."""
    pos = p_cal[y_cal == 1]
    if not pos.size:
        return 0.0
    return float(np.quantile(pos, alpha))

"""Statistical analysis (section 24).

The resampling unit is the *drive*, never the row.  Rows inside a drive are
strongly dependent, so row-level bootstrap confidence intervals on this kind of
data are far too narrow and are not reported.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from ..utils import get_logger

LOG = get_logger("hoproj.stats")


def drive_bootstrap(metric_fn, y: np.ndarray, p: np.ndarray, groups: np.ndarray,
                    n: int = 1000, ci: float = 0.95, seed: int = 0) -> dict:
    """Cluster bootstrap: resample whole drives with replacement."""
    y, p = np.asarray(y, float), np.asarray(p, float)
    groups = np.asarray(groups, dtype=object)
    uniq = np.unique(groups)
    index = {g: np.flatnonzero(groups == g) for g in uniq}
    rng = np.random.default_rng(seed)
    point = metric_fn(y, p)
    draws = np.full(n, np.nan)
    for b in range(n):
        pick = rng.choice(uniq, size=len(uniq), replace=True)
        idx = np.concatenate([index[g] for g in pick])
        try:
            draws[b] = metric_fn(y[idx], p[idx])
        except Exception:
            continue
    lo, hi = np.nanpercentile(draws, [100 * (1 - ci) / 2, 100 * (1 + ci) / 2])
    return {"point": float(point), "ci_low": float(lo), "ci_high": float(hi),
            "n_groups": int(len(uniq)), "n_boot": int(np.isfinite(draws).sum()),
            "bootstrap_se": float(np.nanstd(draws))}


def paired_permutation(metric_fn, y: np.ndarray, p_a: np.ndarray, p_b: np.ndarray,
                       groups: np.ndarray, n: int = 2000, seed: int = 0) -> dict:
    """Swap the two models' predictions within randomly chosen drives."""
    y = np.asarray(y, float)
    p_a, p_b = np.asarray(p_a, float), np.asarray(p_b, float)
    groups = np.asarray(groups, dtype=object)
    uniq = np.unique(groups)
    index = {g: np.flatnonzero(groups == g) for g in uniq}
    observed = metric_fn(y, p_a) - metric_fn(y, p_b)
    rng = np.random.default_rng(seed)
    count = 0
    valid = 0
    for _ in range(n):
        swap = rng.random(len(uniq)) < 0.5
        pa, pb = p_a.copy(), p_b.copy()
        for g, s in zip(uniq, swap):
            if s:
                i = index[g]
                pa[i], pb[i] = p_b[i], p_a[i]
        try:
            diff = metric_fn(y, pa) - metric_fn(y, pb)
        except Exception:
            continue
        valid += 1
        if abs(diff) >= abs(observed) - 1e-12:
            count += 1
    return {"observed_difference": float(observed),
            "p_value": (count + 1) / (valid + 1) if valid else np.nan,
            "n_permutations": valid}


def wilcoxon_per_drive(metric_fn, y: np.ndarray, p_a: np.ndarray, p_b: np.ndarray,
                       groups: np.ndarray) -> dict:
    """Per-drive metric for each model, then a paired signed-rank test."""
    from scipy.stats import wilcoxon

    groups = np.asarray(groups, dtype=object)
    a_vals, b_vals = [], []
    for g in np.unique(groups):
        idx = np.flatnonzero(groups == g)
        if len(np.unique(np.asarray(y)[idx])) < 2:
            continue
        try:
            a_vals.append(metric_fn(y[idx], p_a[idx]))
            b_vals.append(metric_fn(y[idx], p_b[idx]))
        except Exception:
            continue
    if len(a_vals) < 6:
        return {"p_value": np.nan, "n_drives": len(a_vals),
                "note": "too few drives with both classes for a signed-rank test"}
    stat, p = wilcoxon(a_vals, b_vals)
    d = np.array(a_vals) - np.array(b_vals)
    return {"statistic": float(stat), "p_value": float(p), "n_drives": len(a_vals),
            "median_difference": float(np.median(d)),
            "cliffs_delta": float(np.mean(np.sign(d)))}


def holm_correction(pvalues: dict[str, float]) -> pd.DataFrame:
    items = [(k, v) for k, v in pvalues.items() if np.isfinite(v)]
    items.sort(key=lambda kv: kv[1])
    m = len(items)
    rows, running = [], 0.0
    for i, (k, p) in enumerate(items):
        adj = min(1.0, (m - i) * p)
        running = max(running, adj)
        rows.append({"comparison": k, "p_raw": p, "p_holm": running,
                     "significant_0.05": running < 0.05})
    return pd.DataFrame(rows)


def leakage_inflation(table: pd.DataFrame, metric: str = "auprc",
                      condition_col: str = "condition") -> pd.DataFrame:
    """Delta between the random-row condition and the grouped / external conditions."""
    index_cols = [c for c in ("model", "regime", "feature_set", "variant", "horizon_s")
                  if c in table.columns and table[c].nunique() > 1 or c in ("model", "horizon_s")]
    piv = table.pivot_table(index=[c for c in dict.fromkeys(index_cols)],
                            columns=condition_col, values=metric)
    out = piv.copy()
    if "random_row" in piv and "grouped_drive" in piv:
        out["delta_grouped"] = piv["random_row"] - piv["grouped_drive"]
        out["relative_inflation_grouped"] = out["delta_grouped"] / piv["grouped_drive"].replace(0, np.nan)
    if "random_row" in piv and "external_route" in piv:
        out["delta_external"] = piv["random_row"] - piv["external_route"]
        out["relative_inflation_external"] = out["delta_external"] / piv["external_route"].replace(0, np.nan)
    return out.reset_index()

"""Stage R10 - dataset characterisation and distribution-shift description."""
from __future__ import annotations

import numpy as np
import pandas as pd

from ..config import Config
from ..data.labels import horizon_tags
from ..utils import get_logger

LOG = get_logger("hoproj.characterise")


def dataset_summary(samples: pd.DataFrame, drives: pd.DataFrame, ho: pd.DataFrame,
                    labels: pd.DataFrame, cfg: Config) -> dict:
    tags = horizon_tags(cfg)
    per_route = drives.groupby("route_id").agg(
        drives=("drive_id", "nunique"), samples=("n_samples", "sum"),
        hours=("duration_s", lambda s: s.sum() / 3600.0),
        km=("distance_m", lambda s: s.sum() / 1000.0),
        mean_speed=("mean_speed_kmh", "mean"),
    )
    ho_route = ho.merge(drives[["drive_id", "route_id"]], on="drive_id", how="left")
    per_route["handovers"] = ho_route.groupby("route_id").size()
    per_route["pingpong"] = ho_route.groupby("route_id")["is_pingpong"].sum()
    per_route["ho_per_km"] = per_route["handovers"] / per_route["km"].replace(0, np.nan)

    prevalence = {}
    for tag in tags:
        m = labels[f"m_ho_{tag}"].astype(bool)
        prevalence[tag] = {
            "valid_samples": int(m.sum()),
            "positive_rate": float(labels.loc[m, f"y_ho_{tag}"].mean()),
            "imbalance_ratio": float((1 - labels.loc[m, f"y_ho_{tag}"].mean())
                                     / max(labels.loc[m, f"y_ho_{tag}"].mean(), 1e-9)),
        }
        if f"y_qoe_{tag}" in labels:
            prevalence[tag]["qoe_positive_rate"] = float(labels.loc[m, f"y_qoe_{tag}"].mean())

    missing = samples.isna().mean().sort_values(ascending=False)
    cells = samples["serving_cell_name"].dropna().astype(str) if "serving_cell_name" in samples else pd.Series(dtype=str)
    summary = {
        "n_samples": int(len(samples)),
        "n_drives": int(drives["drive_id"].nunique()),
        "n_routes": int(drives["route_id"].nunique()),
        "n_handovers": int(len(ho)),
        "pingpong_frac": float(ho["is_pingpong"].mean()) if len(ho) else 0.0,
        "total_hours": float(drives["duration_s"].sum() / 3600.0),
        "total_km": float(drives["distance_m"].sum() / 1000.0),
        "unique_serving_cells": int(cells.nunique()),
        "dates": sorted(drives["date"].unique().tolist()),
        "per_route": per_route.reset_index().to_dict(orient="records"),
        "label_prevalence": prevalence,
        "top_missing_fields": missing[missing > 0].head(15).round(4).to_dict(),
    }
    return summary


def shift_report(features: pd.DataFrame, feature_names: list[str],
                 dev_mask: np.ndarray, ext_mask: np.ndarray, top_k: int = 20) -> pd.DataFrame:
    """Per-feature standardised mean difference + KS statistic, dev vs external.

    This is the descriptive half of the OOD study: it says *which* variables move
    when the route changes, before any OOD score is trained.
    """
    from scipy import stats

    rows = []
    for col in feature_names:
        a = features.loc[dev_mask, col].to_numpy(float)
        b = features.loc[ext_mask, col].to_numpy(float)
        a = a[np.isfinite(a)]
        b = b[np.isfinite(b)]
        if len(a) < 50 or len(b) < 50:
            continue
        pooled = np.sqrt((a.var() + b.var()) / 2) or 1.0
        ks = stats.ks_2samp(a[:20000], b[:20000], method="asymp")
        rows.append({"feature": col, "smd": float((b.mean() - a.mean()) / pooled),
                     "ks": float(ks.statistic), "ks_p": float(ks.pvalue),
                     "dev_mean": float(a.mean()), "ext_mean": float(b.mean())})
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    out["abs_smd"] = out["smd"].abs()
    return out.sort_values("abs_smd", ascending=False).reset_index(drop=True)


def cell_overlap(samples: pd.DataFrame, dev_mask: np.ndarray, ext_mask: np.ndarray) -> dict:
    """How many external-route cells were never seen in development (RQ6)."""
    key = "serving_cell_name" if "serving_cell_name" in samples else "serving_pci"
    dev = set(samples.loc[dev_mask, key].dropna().astype(str))
    ext = set(samples.loc[ext_mask, key].dropna().astype(str))
    unseen = ext - dev
    return {"dev_cells": len(dev), "external_cells": len(ext),
            "unseen_external_cells": len(unseen),
            "unseen_fraction": len(unseen) / max(len(ext), 1),
            "unseen_examples": sorted(unseen)[:20]}

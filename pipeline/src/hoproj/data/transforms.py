"""Leakage-safe preprocessing: every statistic is fitted on TRAIN rows only."""
from __future__ import annotations

import numpy as np
import pandas as pd

from ..utils import get_logger, read_json, write_json

LOG = get_logger("hoproj.transforms")


class TabularTransform:
    """Impute -> clip -> scale, with all parameters learned from training rows.

    Stored as plain JSON so a fitted transform can be audited and shipped with
    the model artefacts (required for the reproducibility package, R16).
    """

    def __init__(self, scaler: str = "robust", impute: str = "median", clip_sigma: float = 8.0):
        self.scaler = scaler
        self.impute = impute
        self.clip_sigma = float(clip_sigma)
        self.columns: list[str] = []
        self.fill_: dict[str, float] = {}
        self.center_: dict[str, float] = {}
        self.scale_: dict[str, float] = {}

    def fit(self, X: pd.DataFrame) -> "TabularTransform":
        self.columns = list(X.columns)
        arr = X.to_numpy(dtype=float, na_value=np.nan)
        med = np.nanmedian(arr, axis=0)
        med = np.where(np.isfinite(med), med, 0.0)
        self.fill_ = dict(zip(self.columns, med.tolist()))
        filled = np.where(np.isfinite(arr), arr, med)
        if self.scaler == "standard":
            center = filled.mean(axis=0)
            scale = filled.std(axis=0)
        elif self.scaler == "none":
            center = np.zeros(filled.shape[1])
            scale = np.ones(filled.shape[1])
        else:  # robust
            center = np.nanmedian(filled, axis=0)
            q75, q25 = np.nanpercentile(filled, [75, 25], axis=0)
            scale = (q75 - q25) / 1.349
        scale = np.where((~np.isfinite(scale)) | (scale < 1e-9), 1.0, scale)
        self.center_ = dict(zip(self.columns, center.tolist()))
        self.scale_ = dict(zip(self.columns, scale.tolist()))
        LOG.info("fitted %s transform on %d train rows x %d columns",
                 self.scaler, len(X), len(self.columns))
        return self

    def transform(self, X: pd.DataFrame) -> np.ndarray:
        missing = [c for c in self.columns if c not in X.columns]
        if missing:
            X = X.copy()
            for c in missing:
                X[c] = np.nan
        arr = X[self.columns].to_numpy(dtype=float, na_value=np.nan)
        fill = np.array([self.fill_[c] for c in self.columns])
        arr = np.where(np.isfinite(arr), arr, fill)
        center = np.array([self.center_[c] for c in self.columns])
        scale = np.array([self.scale_[c] for c in self.columns])
        out = (arr - center) / scale
        if self.clip_sigma:
            np.clip(out, -self.clip_sigma, self.clip_sigma, out=out)
        return out.astype(np.float32)

    def fit_transform(self, X: pd.DataFrame) -> np.ndarray:
        return self.fit(X).transform(X)

    def save(self, path) -> None:
        write_json({"scaler": self.scaler, "impute": self.impute, "clip_sigma": self.clip_sigma,
                    "columns": self.columns, "fill": self.fill_,
                    "center": self.center_, "scale": self.scale_}, path)

    @classmethod
    def load(cls, path) -> "TabularTransform":
        blob = read_json(path)
        obj = cls(blob["scaler"], blob["impute"], blob["clip_sigma"])
        obj.columns = blob["columns"]
        obj.fill_, obj.center_, obj.scale_ = blob["fill"], blob["center"], blob["scale"]
        return obj


def drop_degenerate(X: pd.DataFrame, train_mask: np.ndarray, min_unique: int = 2,
                    max_nan_frac: float = 0.9) -> list[str]:
    """Columns that are constant or almost entirely missing *in the training rows*."""
    tr = X.loc[train_mask]
    keep = []
    for col in X.columns:
        s = tr[col]
        if s.isna().mean() > max_nan_frac:
            continue
        if s.nunique(dropna=True) < min_unique:
            continue
        keep.append(col)
    dropped = [c for c in X.columns if c not in keep]
    if dropped:
        LOG.info("dropping %d degenerate features (train-only decision): %s%s",
                 len(dropped), dropped[:8], " ..." if len(dropped) > 8 else "")
    return keep

"""Snapshot (single-sample) baselines: logistic regression, LightGBM, compact MLP.

Each wraps a *set* of independent per-horizon binary models behind one
``predict_proba`` returning an (N, H) matrix, so snapshot and temporal models are
interchangeable downstream.
"""
from __future__ import annotations

import numpy as np

from ..utils import get_logger

LOG = get_logger("hoproj.snapshot")


class MultiHorizonWrapper:
    """Fits one binary model per horizon on the same features."""

    def __init__(self, factory, name: str):
        self.factory = factory
        self.name = name
        self.models_: list = []
        self.trivial_: list[float | None] = []

    def fit(self, X, Y, sample_weight=None, masks=None, **kwargs):
        X = np.asarray(X, dtype=np.float32)
        Y = np.asarray(Y)
        self.models_, self.trivial_ = [], []
        for j in range(Y.shape[1]):
            m = np.ones(len(Y), dtype=bool) if masks is None else masks[:, j].astype(bool)
            y = Y[m, j]
            if len(np.unique(y)) < 2:
                self.models_.append(None)
                self.trivial_.append(float(y.mean()) if len(y) else 0.0)
                LOG.warning("%s horizon %d: single-class training target, using constant", self.name, j)
                continue
            mdl = self.factory()
            sw = None if sample_weight is None else np.asarray(sample_weight)[m]
            try:
                mdl.fit(X[m], y, sample_weight=sw)
            except TypeError:
                mdl.fit(X[m], y)
            self.models_.append(mdl)
            self.trivial_.append(None)
        return self

    def predict_proba(self, X, n_outputs: int | None = None) -> np.ndarray:
        X = np.asarray(X, dtype=np.float32)
        cols = []
        for mdl, triv in zip(self.models_, self.trivial_):
            if mdl is None:
                cols.append(np.full(len(X), triv if triv is not None else 0.0))
            else:
                cols.append(mdl.predict_proba(X)[:, 1])
        return np.column_stack(cols)

    @property
    def n_params(self) -> int:
        total = 0
        for m in self.models_:
            if m is None:
                continue
            if hasattr(m, "coef_"):
                total += int(np.size(m.coef_) + np.size(getattr(m, "intercept_", 0)))
            elif hasattr(m, "booster_"):
                total += int(m.booster_.num_trees() * 2 ** 6)
        return total


def make_logreg(params: dict):
    from sklearn.linear_model import LogisticRegression

    def factory():
        return LogisticRegression(
            C=params.get("C", 1.0), max_iter=params.get("max_iter", 2000),
            class_weight=params.get("class_weight", "balanced"), n_jobs=None)

    return MultiHorizonWrapper(factory, "logreg")


def make_lgbm(params: dict):
    import lightgbm as lgb

    def factory():
        return lgb.LGBMClassifier(
            n_estimators=params.get("n_estimators", 600),
            learning_rate=params.get("learning_rate", 0.05),
            num_leaves=params.get("num_leaves", 63),
            min_child_samples=params.get("min_child_samples", 50),
            subsample=params.get("subsample", 0.8),
            subsample_freq=params.get("subsample_freq", 1),
            colsample_bytree=params.get("colsample_bytree", 0.8),
            reg_lambda=params.get("reg_lambda", 1.0),
            is_unbalance=params.get("is_unbalance", True),
            n_jobs=params.get("n_jobs", -1), verbosity=-1)

    return MultiHorizonWrapper(factory, "lgbm")


def make_xgb(params: dict):
    import xgboost as xgb

    def factory():
        return xgb.XGBClassifier(
            n_estimators=params.get("n_estimators", 600),
            learning_rate=params.get("learning_rate", 0.05),
            max_depth=params.get("max_depth", 6),
            subsample=params.get("subsample", 0.8),
            colsample_bytree=params.get("colsample_bytree", 0.8),
            reg_lambda=params.get("reg_lambda", 1.0),
            scale_pos_weight=params.get("scale_pos_weight", 1.0),
            tree_method="hist", n_jobs=-1, eval_metric="aucpr")

    return MultiHorizonWrapper(factory, "xgboost")

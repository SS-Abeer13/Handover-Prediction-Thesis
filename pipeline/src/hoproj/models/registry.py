"""Single entry point for constructing any model in the comparison."""
from __future__ import annotations

from ..config import Config
from ..utils import get_logger
from . import rules, snapshot

LOG = get_logger("hoproj.registry")

SNAPSHOT_MODELS = {"logreg", "lgbm", "xgboost"}
TORCH_MODELS = {"mlp", "gru", "lstm", "tcn", "transformer"}
RULE_MODELS = {"rule", "persistence", "rf_gap"}


def model_kind(name: str) -> str:
    if name in RULE_MODELS:
        return "rule"
    if name in SNAPSHOT_MODELS:
        return "snapshot"
    if name in TORCH_MODELS:
        return "torch"
    raise KeyError(f"unknown model {name!r}")


def build_model(name: str, cfg: Config, n_features: int, n_horizons: int,
                d_cand: int = 0, seed: int = 0, params: dict | None = None):
    params = params if params is not None else (cfg.get_path("model.params", {}) or {})
    kind = model_kind(name)
    if kind == "rule":
        if name in ("rule", "rf_gap"):
            mode = params.get("mode", "rf_gap")
            if mode == "persistence":
                return rules.PersistenceBaseline()
            return rules.RfGapRule(**{k: v for k, v in params.items() if k != "mode"})
        return rules.PersistenceBaseline()
    if kind == "snapshot":
        return {"logreg": snapshot.make_logreg, "lgbm": snapshot.make_lgbm,
                "xgboost": snapshot.make_xgb}[name](params)
    from .wrapper import TorchSeqModel
    return TorchSeqModel(name, n_features, n_horizons,
                         cfg.get_path("tasks", {}), params,
                         cfg.get_path("train", {}), d_cand=d_cand, seed=seed)

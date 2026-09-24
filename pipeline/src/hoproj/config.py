"""Configuration loading: YAML + deep merge + dotted access + provenance hash."""
from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = REPO_ROOT / "configs"


def _read_yaml(path: str | Path) -> dict:
    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def deep_merge(base: dict, override: dict) -> dict:
    out = copy.deepcopy(base)
    for key, val in (override or {}).items():
        if isinstance(val, dict) and isinstance(out.get(key), dict):
            out[key] = deep_merge(out[key], val)
        else:
            out[key] = copy.deepcopy(val)
    return out


class Config(dict):
    """Dict with dotted lookup: cfg.get_path('labels.horizons_s')."""

    def get_path(self, dotted: str, default: Any = None) -> Any:
        node: Any = self
        for part in dotted.split("."):
            if not isinstance(node, dict) or part not in node:
                return default
            node = node[part]
        return node

    def require(self, dotted: str) -> Any:
        sentinel = object()
        val = self.get_path(dotted, sentinel)
        if val is sentinel:
            raise KeyError(f"missing required config key: {dotted}")
        return val

    def set_path(self, dotted: str, value: Any) -> None:
        parts = dotted.split(".")
        node: dict = self
        for part in parts[:-1]:
            node = node.setdefault(part, {})
        node[parts[-1]] = value

    @property
    def fingerprint(self) -> str:
        blob = json.dumps(self, sort_keys=True, default=str).encode()
        return hashlib.sha256(blob).hexdigest()[:12]

    def dump(self, path: str | Path) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            yaml.safe_dump(dict(self), fh, sort_keys=False)


def load_config(
    base: str | Path = "base.yaml",
    adapter: str | None = None,
    model: str | None = None,
    experiment: str | None = None,
    overrides: dict | None = None,
) -> Config:
    """Compose: base <- adapter <- model <- experiment <- CLI overrides.

    The adapter file may carry an ``overrides`` block which is applied *after*
    its own ``adapter`` section, so a capture-specific limitation (for example a
    pilot log with no neighbour measurements) automatically disables the tasks it
    cannot support.
    """
    base_path = Path(base)
    if not base_path.is_absolute() and not base_path.exists():
        base_path = CONFIG_DIR / base_path
    cfg = Config(_read_yaml(base_path))

    adapter = adapter or cfg.get_path("data.adapter")
    if adapter:
        ad = _read_yaml(CONFIG_DIR / "adapters" / f"{adapter}.yaml")
        ad_over = ad.pop("overrides", {})
        cfg = Config(deep_merge(cfg, ad))
        cfg = Config(deep_merge(cfg, ad_over))
        cfg.set_path("data.adapter", adapter)
    if model:
        cfg = Config(deep_merge(cfg, _read_yaml(CONFIG_DIR / "models" / f"{model}.yaml")))
    if experiment:
        cfg = Config(deep_merge(cfg, _read_yaml(CONFIG_DIR / "experiments" / f"{experiment}.yaml")))
    if overrides:
        cfg = Config(deep_merge(cfg, overrides))
    return cfg


def parse_cli_overrides(pairs: list[str]) -> dict:
    """``--set train.epochs=3 features.regime=context_rich`` -> nested dict."""
    out: dict = {}
    for pair in pairs or []:
        if "=" not in pair:
            raise ValueError(f"override must be key=value, got {pair!r}")
        key, raw = pair.split("=", 1)
        try:
            val = yaml.safe_load(raw)
        except Exception:
            val = raw
        node = out
        parts = key.split(".")
        for part in parts[:-1]:
            node = node.setdefault(part, {})
        node[parts[-1]] = val
    return out


def resolve_paths(cfg: Config, root: str | Path | None = None) -> dict[str, Path]:
    root = Path(root or os.environ.get("HOPROJ_ROOT", REPO_ROOT)).resolve()
    paths = {k: (root / v).resolve() for k, v in cfg.require("project.paths").items()}
    for p in paths.values():
        p.mkdir(parents=True, exist_ok=True)
    paths["root"] = root
    return paths

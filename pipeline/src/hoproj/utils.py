"""Shared helpers: logging, seeding, geometry, IO, run manifests."""
from __future__ import annotations

import json
import logging
import os
import platform
import random
import subprocess
import sys
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd

EARTH_R_M = 6_371_008.8
LOG_FMT = "%(asctime)s | %(levelname)-7s | %(name)-22s | %(message)s"


def get_logger(name: str = "hoproj", level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(LOG_FMT, datefmt="%H:%M:%S"))
        logger.addHandler(handler)
    logger.setLevel(level)
    logger.propagate = False
    return logger


LOG = get_logger()


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed % (2**32 - 1))
    os.environ["PYTHONHASHSEED"] = str(seed)
    try:
        import torch

        torch.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
    except Exception:
        pass


@contextmanager
def timed(label: str, logger: logging.Logger | None = None):
    log = logger or LOG
    t0 = time.perf_counter()
    log.info("START %s", label)
    try:
        yield
    finally:
        log.info("DONE  %s (%.2fs)", label, time.perf_counter() - t0)


# ----------------------------------------------------------------- geometry
def haversine_m(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(np.radians, (lat1, lon1, lat2, lon2))
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    return 2 * EARTH_R_M * np.arcsin(np.sqrt(np.clip(a, 0, 1)))


def local_xy(lat, lon, lat0=None, lon0=None):
    """Equirectangular local projection in metres (adequate over a few km)."""
    lat = np.asarray(lat, dtype=float)
    lon = np.asarray(lon, dtype=float)
    lat0 = float(np.nanmean(lat)) if lat0 is None else lat0
    lon0 = float(np.nanmean(lon)) if lon0 is None else lon0
    x = np.radians(lon - lon0) * EARTH_R_M * np.cos(np.radians(lat0))
    y = np.radians(lat - lat0) * EARTH_R_M
    return x, y


def bearing_deg(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(np.radians, (lat1, lon1, lat2, lon2))
    dlon = lon2 - lon1
    x = np.sin(dlon) * np.cos(lat2)
    y = np.cos(lat1) * np.sin(lat2) - np.sin(lat1) * np.cos(lat2) * np.cos(dlon)
    return (np.degrees(np.arctan2(x, y)) + 360.0) % 360.0


def angle_diff_deg(a, b):
    d = (np.asarray(a, float) - np.asarray(b, float) + 180.0) % 360.0 - 180.0
    return d


# ---------------------------------------------------------------------- IO
def write_json(obj: Any, path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=2, default=_json_default)
    return path


def read_json(path: str | Path) -> Any:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _json_default(obj):
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, (np.ndarray,)):
        return obj.tolist()
    if isinstance(obj, (pd.Timestamp,)):
        return obj.isoformat()
    if isinstance(obj, Path):
        return str(obj)
    return str(obj)


def write_parquet(df: pd.DataFrame, path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        df.to_parquet(path, index=False)
    except Exception:       # pyarrow unavailable -> fall back to csv.gz
        path = path.with_suffix(".csv.gz")
        df.to_csv(path, index=False)
    return path


def read_table(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    if path.suffix == ".parquet":
        return pd.read_parquet(path)
    return pd.read_csv(path)


def first_existing(*candidates: str | Path) -> Path | None:
    for cand in candidates:
        if cand and Path(cand).exists():
            return Path(cand)
    return None


def environment_manifest() -> dict:
    def _ver(mod: str) -> str:
        try:
            return __import__(mod).__version__
        except Exception:
            return "absent"

    try:
        git = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, timeout=5
        ).stdout.strip() or None
    except Exception:
        git = None
    return {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "git_commit": git,
        "packages": {m: _ver(m) for m in
                     ["numpy", "pandas", "scipy", "sklearn", "torch", "lightgbm", "pyarrow"]},
    }


def safe_div(num, den, fill=np.nan):
    den = np.asarray(den, float)
    out = np.full(np.shape(num), fill, dtype=float)
    ok = den != 0
    out[ok] = np.asarray(num, float)[ok] / den[ok]
    return out


def chunked(seq: Iterable, size: int):
    buf = []
    for item in seq:
        buf.append(item)
        if len(buf) >= size:
            yield buf
            buf = []
    if buf:
        yield buf

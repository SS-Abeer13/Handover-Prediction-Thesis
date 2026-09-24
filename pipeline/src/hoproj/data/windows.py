"""Sequence windowing: build (N, L, F) tensors without copying the whole table.

A window ending at sample ``i`` uses rows ``i-L+1 .. i`` of the same drive, so a
prediction at ``t`` sees only the past.  Windows are rejected when more than
``1 - min_valid_frac`` of their rows were synthesised on the regular grid, or when
the target mask for the horizon of interest is 0.

Windows are materialised lazily into a float32 memmap on first use, so an
81k-sample capture with a 10 s window and ~200 features stays well inside a
laptop's memory budget.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

from ..utils import get_logger

LOG = get_logger("hoproj.windows")


@dataclass
class WindowIndex:
    """Row positions that end a valid window, plus their provenance."""
    end_pos: np.ndarray            # int index into the feature matrix
    start_pos: np.ndarray
    drive_id: np.ndarray
    route_id: np.ndarray
    length: int
    valid_frac: np.ndarray = field(default_factory=lambda: np.empty(0))

    def __len__(self) -> int:
        return len(self.end_pos)


def build_window_index(frame: pd.DataFrame, length: int, stride: int = 1,
                       min_valid_frac: float = 0.7,
                       interpolated: np.ndarray | None = None) -> WindowIndex:
    ends, starts, drives, routes, fracs = [], [], [], [], []
    pos = np.arange(len(frame))
    for drive_id, idx in frame.groupby("drive_id", sort=False).indices.items():
        idx = np.sort(np.asarray(idx))
        route = frame["route_id"].iloc[idx[0]]
        if len(idx) < length:
            continue
        for j in range(length - 1, len(idx), stride):
            window = idx[j - length + 1: j + 1]
            if interpolated is not None:
                frac = 1.0 - float(interpolated[window].mean())
                if frac < min_valid_frac:
                    continue
            else:
                frac = 1.0
            ends.append(idx[j])
            starts.append(window[0])
            drives.append(drive_id)
            routes.append(route)
            fracs.append(frac)
    wi = WindowIndex(np.asarray(ends, dtype=np.int64), np.asarray(starts, dtype=np.int64),
                     np.asarray(drives, dtype=object), np.asarray(routes, dtype=object),
                     length, np.asarray(fracs, dtype=np.float32))
    LOG.info("window index: %d windows of length %d (stride %d) over %d drives",
             len(wi), length, stride, len(set(wi.drive_id.tolist())))
    return wi


def materialise(X: np.ndarray, wi: WindowIndex, cache_path: str | Path | None = None) -> np.ndarray:
    """Return a (N, L, F) array, memmapped when ``cache_path`` is given."""
    n, L, F = len(wi), wi.length, X.shape[1]
    nbytes = n * L * F * 4
    if cache_path is not None and nbytes > 200 * 1024**2:
        Path(cache_path).parent.mkdir(parents=True, exist_ok=True)
        out = np.lib.format.open_memmap(cache_path, mode="w+", dtype=np.float32, shape=(n, L, F))
    else:
        out = np.empty((n, L, F), dtype=np.float32)
    offsets = np.arange(-L + 1, 1)
    block = max(1, int(2e7 // max(L * F, 1)))
    for a in range(0, n, block):
        b = min(a + block, n)
        rows = wi.end_pos[a:b, None] + offsets[None, :]
        out[a:b] = X[rows]
    LOG.info("materialised windows: shape=%s (%.1f MB)", out.shape, nbytes / 1024**2)
    return out

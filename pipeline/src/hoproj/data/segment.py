"""Stage R7b - split continuous logging sessions into pseudo-drives.

Why this exists
---------------
The proposal's evaluation protocol partitions by *complete drives* and by
*complete routes*.  A capture that records one long continuous session per
corridor gives only one group per corridor, which makes grouped cross-validation
and trip-level bootstrap impossible.  A session on a corridor is in practice a
sequence of traversals (there and back, repeatedly).  We recover those
traversals geometrically:

  1. project the session's GPS onto the corridor's principal axis -> along-track
     coordinate ``s`` (metres);
  2. median-smooth ``s`` to remove GPS jitter;
  3. cut at direction reversals, i.e. local extrema of ``s``;
  4. keep runs that cover at least ``min_traverse_frac`` of the corridor extent
     and last at least ``min_run_duration_s``; shorter runs are merged into the
     neighbour they continue.

Each surviving run is one drive, carrying ``route_id`` and ``direction``
(``fwd``/``rev``).  Drives are the grouping unit for every split, every
bootstrap resample and every calibration set in the rest of the pipeline.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from ..config import Config
from ..utils import get_logger, haversine_m, local_xy

LOG = get_logger("hoproj.segment")


def _along_track(lat: np.ndarray, lon: np.ndarray) -> np.ndarray:
    x, y = local_xy(lat, lon)
    pts = np.column_stack([x, y])
    ok = np.isfinite(pts).all(axis=1)
    s = np.full(len(pts), np.nan)
    if ok.sum() < 10:
        return s
    centred = pts[ok] - pts[ok].mean(axis=0)
    # principal axis of the corridor
    _, _, vt = np.linalg.svd(centred, full_matrices=False)
    axis = vt[0]
    s[ok] = centred @ axis
    return pd.Series(s).interpolate(limit_direction="both").to_numpy()


def _smooth(s: np.ndarray, window: int) -> np.ndarray:
    if window <= 1:
        return s
    return pd.Series(s).rolling(window, center=True, min_periods=1).median().to_numpy()


def _reversal_runs(s: np.ndarray, min_len: int, min_span: float) -> list[tuple[int, int]]:
    """Monotone runs of ``s``, cutting at sustained direction reversals."""
    n = len(s)
    if n < min_len:
        return [(0, n)]
    d = np.sign(np.diff(s, prepend=s[0]))
    d[d == 0] = np.nan
    d = pd.Series(d).ffill().bfill().to_numpy()
    cuts = [0]
    last_dir = d[0]
    last_cut = 0
    for i in range(1, n):
        if d[i] != last_dir:
            span = abs(s[i] - s[last_cut])
            if (i - last_cut) >= min_len and span >= min_span:
                cuts.append(i)
                last_cut = i
            last_dir = d[i]
    cuts.append(n)
    runs = [(a, b) for a, b in zip(cuts[:-1], cuts[1:]) if b > a]
    # merge runs that are too short into the previous one
    merged: list[list[int]] = []
    for a, b in runs:
        if merged and ((b - a) < min_len or abs(s[b - 1] - s[a]) < min_span):
            merged[-1][1] = b
        else:
            merged.append([a, b])
    return [(a, b) for a, b in merged]


def assign_routes(samples: pd.DataFrame, events: pd.DataFrame | None, cfg: Config) -> pd.DataFrame:
    """Attach ``route_id`` to each sample."""
    samples = samples.copy()
    mode = cfg.get_path("segmentation.route_from", "handover_log")
    samples["route_id"] = pd.Series([pd.NA] * len(samples), dtype="object")
    if mode == "handover_log" and events is not None and "route_id" in events:
        for sid, grp in samples.groupby("session_id"):
            lo, hi = grp["t"].min(), grp["t"].max()
            sub = events[(events["t"] >= lo - pd.Timedelta(seconds=60)) &
                         (events["t"] <= hi + pd.Timedelta(seconds=60))]
            if len(sub):
                label = sub["route_id"].value_counts().idxmax()
                samples.loc[grp.index, "route_id"] = label
    fallback = samples["route_id"].isna()
    if fallback.any():
        samples.loc[fallback, "route_id"] = (
            "session_" + samples.loc[fallback, "session_id"].astype(str)
        )
    return samples


def segment_drives(samples: pd.DataFrame, cfg: Config) -> pd.DataFrame:
    """Add ``drive_id``, ``direction``, ``s_along_m``, ``drive_seq`` columns."""
    method = cfg.get_path("segmentation.method", "along_track_runs")
    period = float(cfg.get_path("data.target_period_s") or 1.0)
    smooth_n = max(1, int(round(float(cfg.get_path("segmentation.smooth_window_s", 15)) / period)))
    min_len = max(10, int(round(float(cfg.get_path("segmentation.min_run_duration_s", 120)) / period)))
    min_frac = float(cfg.get_path("segmentation.min_traverse_frac", 0.45))
    fixed_n = max(10, int(round(float(cfg.get_path("segmentation.fixed_duration_s", 600)) / period)))

    samples = samples.copy()
    samples["s_along_m"] = np.nan
    samples["drive_id"] = ""
    samples["direction"] = ""
    rows_out = []
    for (route, sid), grp in samples.groupby(["route_id", "session_id"], sort=True):
        grp = grp.sort_values("t")
        s = _along_track(grp["lat"].to_numpy(float), grp["lon"].to_numpy(float))
        s_sm = _smooth(s, smooth_n)
        extent = float(np.nanmax(s_sm) - np.nanmin(s_sm)) if np.isfinite(s_sm).any() else 0.0
        if method == "session":
            runs = [(0, len(grp))]
        elif method == "fixed_duration":
            runs = [(a, min(a + fixed_n, len(grp))) for a in range(0, len(grp), fixed_n)]
        else:
            runs = _reversal_runs(s_sm, min_len, min_frac * max(extent, 1.0))
        grp = grp.assign(s_along_m=s_sm)
        for k, (a, b) in enumerate(runs):
            idx = grp.index[a:b]
            direction = "fwd" if (s_sm[b - 1] - s_sm[a]) >= 0 else "rev"
            grp.loc[idx, "drive_id"] = f"{route}__s{sid:02d}__d{k:03d}"
            grp.loc[idx, "direction"] = direction
        rows_out.append(grp)
    out = pd.concat(rows_out).sort_values("t")
    out["drive_seq"] = out.groupby("drive_id").cumcount()
    out["t_in_drive_s"] = out.groupby("drive_id")["t"].transform(lambda s: (s - s.min()).dt.total_seconds())
    # cumulative travelled distance per drive
    out["step_m"] = 0.0
    dist = haversine_m(out["lat"].shift(), out["lon"].shift(), out["lat"], out["lon"])
    out["step_m"] = np.where(out["drive_seq"] == 0, 0.0, np.nan_to_num(dist))
    out["dist_in_drive_m"] = out.groupby("drive_id")["step_m"].cumsum()
    n_drives = out["drive_id"].nunique()
    LOG.info("segmented %d drives over %d routes (median %.0fs, median %.2f km)",
             n_drives, out["route_id"].nunique(),
             out.groupby("drive_id")["t_in_drive_s"].max().median(),
             out.groupby("drive_id")["dist_in_drive_m"].max().median() / 1000.0)
    return out.reset_index(drop=True)


def drive_table(samples: pd.DataFrame) -> pd.DataFrame:
    """One row per drive: the manifest used by splits, QC and bootstrap."""
    g = samples.groupby("drive_id")
    tbl = pd.DataFrame({
        "drive_id": list(g.groups.keys()),
        "route_id": g["route_id"].first().values,
        "session_id": g["session_id"].first().values,
        "direction": g["direction"].first().values,
        "t_start": g["t"].min().values,
        "t_end": g["t"].max().values,
        "n_samples": g.size().values,
        "duration_s": g["t_in_drive_s"].max().values,
        "distance_m": g["dist_in_drive_m"].max().values,
        "mean_speed_kmh": g["speed_kmh"].mean().values,
        "interp_frac": g["is_interpolated"].mean().values if "is_interpolated" in samples else 0.0,
    })
    tbl["date"] = pd.to_datetime(tbl["t_start"]).dt.date.astype(str)
    tbl["hour"] = pd.to_datetime(tbl["t_start"]).dt.hour
    tbl["time_period"] = pd.cut(tbl["hour"], [-1, 10, 15, 24],
                                labels=["morning", "midday", "evening"]).astype(str)
    return tbl.sort_values("t_start").reset_index(drop=True)

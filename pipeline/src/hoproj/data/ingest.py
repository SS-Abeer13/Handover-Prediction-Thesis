"""Stage R7a - raw capture -> canonical sample table.

Canonical sample schema (columns absent in a given capture are created as NaN):

    t                  pandas datetime64   immutable raw timestamp
    t_rel_s            float               seconds since session start
    session_id         int                 contiguous logging block
    lat, lon           float
    speed_kmh          float
    serving_pci        float   serving_earfcn float   serving_band  str
    serving_enb        float   plmn           float   serving_cell_name str
    serving_rsrp/rsrq/rssi/sinr/cqi          float
    nbr{1..k}_id, nbr{1..k}_rsrp             float
    phy_dl_kbps, phy_ul_kbps, dl_tp_kbps, ul_tp_kbps, rtt_ms, pkt_loss_pct
    is_interpolated    bool                 row synthesised on the regular grid
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from ..config import Config
from ..utils import get_logger

LOG = get_logger("hoproj.ingest")

CANONICAL_NUMERIC = [
    "lat", "lon", "speed_kmh",
    "serving_pci", "serving_earfcn", "serving_enb", "plmn",
    "serving_rsrp", "serving_rsrq", "serving_rssi", "serving_sinr", "serving_cqi",
    "phy_dl_kbps", "phy_ul_kbps", "dl_tp_kbps", "ul_tp_kbps", "rtt_ms", "pkt_loss_pct",
]
CANONICAL_STR = ["serving_band", "serving_cell_name", "rrc_state"]


def _resolve_source(raw_dir: Path, value: str | Path) -> Path:
    cand = Path(value)
    if cand.is_absolute() and cand.exists():
        return cand
    for base in (raw_dir, raw_dir.parent, Path.cwd()):
        hit = base / cand
        if hit.exists():
            return hit
        matches = sorted(base.glob(f"**/{cand.name}"))
        if matches:
            return matches[0]
    raise FileNotFoundError(f"cannot locate source {value!r} under {raw_dir}")


def _parse_time(series: pd.Series, fmt: str | None) -> pd.Series:
    s = series.astype(str).str.strip()
    if fmt:
        out = pd.to_datetime(s, format=fmt, errors="coerce")
        if out.isna().mean() > 0.5:          # format drifted between exports
            out = pd.to_datetime(s, errors="coerce")
        return out
    return pd.to_datetime(s, errors="coerce")


def load_samples(cfg: Config, raw_dir: Path) -> pd.DataFrame:
    spec = cfg.require("adapter.samples")
    path = _resolve_source(raw_dir, cfg.require("data.sources")[spec.get("path_key", "samples")])
    LOG.info("reading samples from %s", path)
    df = pd.read_csv(path, low_memory=False)
    if cfg.get_path("adapter.strip_column_whitespace", False):
        df.columns = [c.strip() for c in df.columns]
    # de-duplicate repeated XCAL column names (pandas already suffixes .1, .2)
    tcol = spec["time"]["column"]
    t = _parse_time(df[tcol], spec["time"].get("format"))
    rename = {k: v for k, v in spec.get("rename", {}).items() if k in df.columns}
    missing = sorted(set(spec.get("rename", {})) - set(df.columns))
    if missing:
        LOG.warning("adapter columns absent in capture (filled NaN): %s", missing)
    out = df[list(rename)].rename(columns=rename).copy()
    out.insert(0, "t", t)
    for col in CANONICAL_NUMERIC:
        out[col] = pd.to_numeric(out.get(col), errors="coerce")
    for col in CANONICAL_STR:
        out[col] = out.get(col)
        if col in out:
            out[col] = out[col].astype("object")
    k = int(cfg.get_path("features.neighbour_k", 3))
    for i in range(1, k + 1):
        for suffix in ("id", "rsrp", "rsrq"):
            col = f"nbr{i}_{suffix}"
            out[col] = pd.to_numeric(out.get(col), errors="coerce")
    out = out.dropna(subset=["t"]).sort_values("t").reset_index(drop=True)
    LOG.info("samples: %d rows, %s -> %s", len(out), out.t.min(), out.t.max())
    return out


def load_handovers(cfg: Config, raw_dir: Path) -> pd.DataFrame | None:
    spec = cfg.get_path("adapter.handovers")
    if not spec:
        return None
    key = spec.get("path_key", "handovers")
    src = cfg.get_path("data.sources", {}).get(key)
    if not src:
        return None
    path = _resolve_source(raw_dir, src)
    LOG.info("reading handover log from %s", path)
    df = pd.read_csv(path)
    df.columns = [c.strip() for c in df.columns]
    t = _parse_time(df[spec["time"]["column"]], spec["time"].get("format"))
    rename = {k: v for k, v in spec.get("rename", {}).items() if k in df.columns}
    out = df.rename(columns=rename).copy()
    out["t"] = t
    out = out.dropna(subset=["t"]).sort_values("t").reset_index(drop=True)
    LOG.info("handover events: %d (%s)", len(out),
             out["ho_type"].value_counts().to_dict() if "ho_type" in out else "no type column")
    return out


def load_signalling(cfg: Config, raw_dir: Path):
    """Parse the paired RRC signalling export, when the adapter declares one."""
    spec = cfg.get_path("adapter.signalling")
    if not spec:
        return None
    src = cfg.get_path("data.sources", {}).get(spec.get("path_key", "signalling"))
    if not src:
        return None
    from .signalling import parse_signalling

    return parse_signalling(_resolve_source(raw_dir, src))


def merge_signalling(samples: pd.DataFrame, log, cfg: Config) -> pd.DataFrame:
    """Fill the neighbour columns from MeasurementReports projected onto the grid.

    The CSV's own Best_N* columns are empty in these captures, so without this the
    serving-to-neighbour gap - the single most predictive feature - does not exist.
    Reports are event-triggered and therefore sparse; ``mr_age_s`` records how stale
    each projection is and travels with the data so it can be masked or modelled.
    """
    from .signalling import to_sample_grid

    tol = float(cfg.get_path("adapter.signalling.projection_tolerance_s", 3.0))
    k = int(cfg.get_path("features.neighbour_k", 3))
    grid = to_sample_grid(log, pd.DatetimeIndex(samples["t"]), k=k, tolerance_s=tol)
    out = samples.drop(columns=[c for c in grid.columns if c != "t" and c in samples.columns])
    out = out.merge(grid, on="t", how="left")
    cov = out[f"nbr1_rsrp"].notna().mean() if "nbr1_rsrp" in out else 0.0
    LOG.info("signalling merge: %.1f%% of samples carry a neighbour measurement "
             "(median report age %.2fs)", 100 * cov,
             float(out["mr_age_s"].median()) if "mr_age_s" in out else float("nan"))
    return out


def mark_sessions(df: pd.DataFrame, gap_s: float) -> pd.DataFrame:
    dt = df["t"].diff().dt.total_seconds()
    df = df.copy()
    df["session_id"] = (dt.fillna(gap_s + 1) > gap_s).cumsum().astype(int)
    df["t_rel_s"] = df.groupby("session_id")["t"].transform(lambda s: (s - s.min()).dt.total_seconds())
    return df


def regularise_grid(df: pd.DataFrame, period_s: float, max_gap_s: float) -> pd.DataFrame:
    """Put each session on a uniform grid.

    Short holes are linearly interpolated and flagged; holes longer than
    ``max_gap_s`` are left as NaN rows so the window builder can reject them.
    No destructive interpolation of event-derived columns is performed.
    """
    if not period_s:
        df = df.copy()
        df["is_interpolated"] = False
        return df
    out = []
    numeric = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])
               and c not in ("session_id",)]
    carry = [c for c in df.columns if c not in numeric + ["t", "session_id", "t_rel_s"]]
    for sid, grp in df.groupby("session_id", sort=True):
        grp = grp.drop_duplicates(subset="t").set_index("t").sort_index()
        grid = pd.date_range(grp.index.min(), grp.index.max(), freq=f"{int(period_s * 1000)}ms")
        res = grp.reindex(grid)
        native = grp.index
        res["is_interpolated"] = ~res.index.isin(native)
        # gap length at each grid point, measured against native stamps
        pos = np.searchsorted(native.values, res.index.values)
        prev_idx = np.clip(pos - 1, 0, len(native) - 1)
        next_idx = np.clip(pos, 0, len(native) - 1)
        gap = (native.values[next_idx] - native.values[prev_idx]).astype("timedelta64[ms]").astype(float) / 1000.0
        fillable = gap <= max_gap_s
        res[numeric] = res[numeric].interpolate(method="time", limit_direction="both")
        res.loc[~fillable & res["is_interpolated"].values, numeric] = np.nan
        for col in carry:
            res[col] = res[col].ffill()
        res["session_id"] = sid
        res = res.reset_index(names="t")
        out.append(res)
    merged = pd.concat(out, ignore_index=True)
    merged["t_rel_s"] = merged.groupby("session_id")["t"].transform(lambda s: (s - s.min()).dt.total_seconds())
    frac = float(merged["is_interpolated"].mean())
    LOG.info("regularised to %.3fs grid: %d rows (%.2f%% synthesised)", period_s, len(merged), 100 * frac)
    return merged


def ingest(cfg: Config, raw_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame | None]:
    samples = load_samples(cfg, raw_dir)
    samples = mark_sessions(samples, float(cfg.get_path("data.session_gap_s", 5.0)))
    samples = regularise_grid(
        samples,
        cfg.get_path("data.target_period_s"),
        float(cfg.get_path("data.max_interpolate_gap_s", 3.0)),
    )
    log = load_signalling(cfg, raw_dir)
    if log is not None:
        samples = merge_signalling(samples, log, cfg)
    events = load_handovers(cfg, raw_dir)
    if events is None and log is not None and cfg.get_path(
            "adapter.signalling.prefer_signalling_handovers", True):
        from .signalling import handover_table

        events = handover_table(log)
        if len(events):
            LOG.info("using %d signalling-confirmed handovers as the event source", len(events))
    # deliberately not attached to ``samples.attrs``: the frame is written to
    # parquet and a parser object is not serialisable. Callers that need the
    # raw streams call ``load_signalling`` themselves.
    return samples, events

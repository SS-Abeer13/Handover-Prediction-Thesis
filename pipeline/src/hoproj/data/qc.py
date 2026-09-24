"""Stage R7c - per-drive quality control and synchronisation accounting."""
from __future__ import annotations

import numpy as np
import pandas as pd

from ..config import Config
from ..utils import get_logger

LOG = get_logger("hoproj.qc")


def drive_quality(samples: pd.DataFrame, drives: pd.DataFrame, cfg: Config) -> pd.DataFrame:
    core = [c for c in cfg.get_path("qc.core_fields", []) if c in samples.columns]
    period = float(cfg.get_path("data.target_period_s") or 1.0)
    rows = []
    for drive_id, grp in samples.groupby("drive_id"):
        dt = grp["t"].diff().dt.total_seconds().dropna()
        gps_gap = grp["lat"].notna().astype(int)
        rows.append({
            "drive_id": drive_id,
            "missing_core_frac": float(grp[core].isna().mean().mean()) if core else 0.0,
            "missing_gps_frac": float(grp["lat"].isna().mean()),
            "max_dt_s": float(dt.max()) if len(dt) else period,
            "dt_jitter_s": float(dt.std()) if len(dt) else 0.0,
            "interp_frac": float(grp["is_interpolated"].mean()) if "is_interpolated" in grp else 0.0,
            "max_speed_kmh": float(grp["speed_kmh"].max()),
            "nbr_missing_frac": float(grp[[c for c in grp.columns if c.startswith("nbr") and c.endswith("rsrp")]]
                                      .isna().mean().mean()) if any(c.startswith("nbr") for c in grp.columns) else 1.0,
            "qoe_missing_frac": float(grp[[c for c in ("dl_tp_kbps", "rtt_ms", "pkt_loss_pct") if c in grp]]
                                      .isna().mean().mean()) if any(c in grp for c in ("dl_tp_kbps", "rtt_ms", "pkt_loss_pct")) else 1.0,
            "gps_continuity": float(gps_gap.mean()),
        })
    qc = pd.DataFrame(rows).merge(drives, on="drive_id", how="right")

    reasons = []
    keep = np.ones(len(qc), dtype=bool)
    for i, row in qc.iterrows():
        bad = []
        if row["duration_s"] < float(cfg.get_path("qc.min_drive_duration_s", 90)):
            bad.append("too_short_duration")
        if row["n_samples"] < int(cfg.get_path("qc.min_drive_samples", 90)):
            bad.append("too_few_samples")
        if cfg.get_path("qc.require_gps", True) and row["missing_gps_frac"] > 0.2:
            bad.append("gps_missing")
        if row["max_dt_s"] > float(cfg.get_path("qc.max_gps_gap_s", 5.0)):
            bad.append("clock_gap")
        if row["max_speed_kmh"] > float(cfg.get_path("qc.max_speed_kmh", 140)):
            bad.append("implausible_speed")
        if row["missing_core_frac"] > float(cfg.get_path("qc.max_missing_frac_core", 0.25)):
            bad.append("core_rf_missing")
        keep[i] = not bad
        reasons.append(";".join(bad))
    qc["qc_pass"] = keep
    qc["qc_reject_reason"] = reasons
    LOG.info("QC: %d/%d drives pass (%s)", int(keep.sum()), len(qc),
             pd.Series([r for r in reasons if r]).value_counts().to_dict())
    return qc


def apply_qc(samples: pd.DataFrame, qc: pd.DataFrame) -> pd.DataFrame:
    good = set(qc.loc[qc["qc_pass"], "drive_id"])
    before = len(samples)
    out = samples[samples["drive_id"].isin(good)].reset_index(drop=True)
    LOG.info("dropped %d samples from rejected drives", before - len(out))
    return out

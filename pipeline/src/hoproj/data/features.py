"""Stage R9 - feature construction.

Every feature is computed from information available at or before time ``t``
(causal rolling windows, backward differences).  No future value, and no
aggregate computed over the whole drive, ever enters a feature.

Blocks
------
rf        serving RSRP/RSRQ/SINR/RSSI/CQI, neighbour RSRP, serving-to-neighbour
          gaps, neighbour ranks, causal rolling mean/std, 1st and 2nd derivatives,
          short-window variability (a fading proxy).
mobility  speed, acceleration, bearing, bearing change, travelled distance,
          stop duration, mobility-state indicator.
history   time since previous handover, serving-cell dwell, number of handovers
          so far in the drive, previous-cell relationship, return-to-source flag.
qoe       DL/UL throughput, RTT, packet loss plus their causal trends.
context   operator/band/EARFCN/route/time-of-day - ONLY in regime B.

Regimes (section 15 of the proposal)
------------------------------------
``topology_agnostic``  drops absolute GPS, route id, cell identity: the model may
                       only use relative radio, mobility, history and QoE signals.
``context_rich``       adds the deployment-specific context block.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from ..config import Config
from ..utils import angle_diff_deg, bearing_deg, get_logger

LOG = get_logger("hoproj.features")

BLOCK_RF = "rf"
BLOCK_MOB = "mobility"
BLOCK_HIST = "history"
BLOCK_QOE = "qoe"
BLOCK_CTX = "context"


def _causal_roll(g: pd.core.groupby.SeriesGroupBy, win: int, stat: str) -> pd.Series:
    r = g.rolling(win, min_periods=1)
    return getattr(r, stat)().reset_index(level=0, drop=True)


def build_features(samples: pd.DataFrame, labels: pd.DataFrame, cfg: Config) -> pd.DataFrame:
    period = float(cfg.get_path("data.target_period_s") or 1.0)
    wins = [max(2, int(round(w / period))) for w in cfg.get_path("features.rolling_windows_s", [3, 5, 10])]
    k = int(cfg.get_path("features.neighbour_k", 3))
    # Build the SUPERSET of blocks, always. Which blocks a model may see is a
    # selection decision made per run in ``assemble`` (via ``select_blocks``),
    # not a construction decision made once here - otherwise a regime or
    # feature-set ablation silently compares a config against itself.
    blocks = {BLOCK_RF, BLOCK_MOB, BLOCK_HIST, BLOCK_QOE, BLOCK_CTX}
    requested = set(cfg.get_path("features.blocks", [BLOCK_RF, BLOCK_MOB, BLOCK_HIST, BLOCK_QOE]))
    regime = cfg.get_path("features.regime", "topology_agnostic")

    df = samples.sort_values(["drive_id", "t"]).reset_index(drop=True)
    lab = labels.set_index(["drive_id", "t"])
    collected: dict[str, np.ndarray] = {}
    meta = df[["t", "drive_id", "route_id", "direction", "drive_seq", "t_in_drive_s",
               "dist_in_drive_m", "lat", "lon", "serving_pci", "serving_cell_name"]].copy()
    gb = df.groupby("drive_id", sort=False)
    feature_block: dict[str, str] = {}

    def add(name: str, values, block: str) -> None:
        collected[name] = np.asarray(values, dtype=float)
        feature_block[name] = block

    # ------------------------------------------------------------------ RF
    if BLOCK_RF in blocks:
        rf_base = ["serving_rsrp", "serving_rsrq", "serving_sinr", "serving_rssi", "serving_cqi"]
        for col in rf_base:
            if col not in df:
                continue
            add(col, df[col], BLOCK_RF)
            s = gb[col]
            add(f"{col}_d1", s.diff().fillna(0.0) / period, BLOCK_RF)
            add(f"{col}_d2", s.diff().diff().fillna(0.0) / period**2, BLOCK_RF)
            for w in wins:
                add(f"{col}_mean{w}", _causal_roll(s, w, "mean"), BLOCK_RF)
                add(f"{col}_std{w}", _causal_roll(s, w, "std").fillna(0.0), BLOCK_RF)
            # causal slope over the longest window (least squares on a fixed grid)
            w = max(wins)
            add(f"{col}_slope{w}", _causal_slope(df, col, w, period), BLOCK_RF)
            # fading proxy: range within the shortest window
            w0 = min(wins)
            add(f"{col}_range{w0}",
                (_causal_roll(s, w0, "max") - _causal_roll(s, w0, "min")).fillna(0.0), BLOCK_RF)

        nbr_cols = [f"nbr{i}_rsrp" for i in range(1, k + 1) if f"nbr{i}_rsrp" in df]
        for i, col in enumerate(nbr_cols, start=1):
            add(col, df[col], BLOCK_RF)
            add(f"gap_serving_nbr{i}", df["serving_rsrp"] - df[col], BLOCK_RF)
            s = gb[col]
            add(f"{col}_d1", s.diff().fillna(0.0) / period, BLOCK_RF)
            gap = df["serving_rsrp"] - df[col]
            add(f"gap_serving_nbr{i}_d1", gap.groupby(df["drive_id"]).diff().fillna(0.0) / period, BLOCK_RF)
            for w in wins[:2]:
                add(f"gap_serving_nbr{i}_mean{w}",
                    _causal_roll(gap.groupby(df["drive_id"]), w, "mean"), BLOCK_RF)
        if nbr_cols:
            nbr = df[nbr_cols].to_numpy(float)
            all_nan_nbr = np.isnan(nbr).all()
            if all_nan_nbr:
                LOG.warning("neighbour RSRP columns are present but entirely empty in this "
                            "capture; candidate-derived features will be constant/NaN and "
                            "target-cell ranking cannot be trained (XCAL feasibility gate, R0)")
            with np.errstate(invalid="ignore"):
                import warnings as _w
                with _w.catch_warnings():
                    _w.simplefilter("ignore", RuntimeWarning)
                    nbr_max = np.nanmax(nbr, axis=1) if not all_nan_nbr else np.full(len(df), np.nan)
                    nbr_min = np.nanmin(nbr, axis=1) if not all_nan_nbr else np.full(len(df), np.nan)
                    nbr_mean = np.nanmean(nbr, axis=1) if not all_nan_nbr else np.full(len(df), np.nan)
            add("nbr_best_rsrp", nbr_max, BLOCK_RF)
            add("nbr_mean_rsrp", nbr_mean, BLOCK_RF)
            add("nbr_spread_rsrp", nbr_max - nbr_min, BLOCK_RF)
            add("gap_serving_best_nbr", df["serving_rsrp"].to_numpy(float) - nbr_max, BLOCK_RF)
            add("serving_rank_among_cands",
                1 + np.nansum(nbr > df["serving_rsrp"].to_numpy(float)[:, None], axis=1), BLOCK_RF)
            gapbest = pd.Series(df["serving_rsrp"].to_numpy(float) - nbr_max)
            add("gap_serving_best_nbr_d1",
                gapbest.groupby(df["drive_id"]).diff().fillna(0.0).to_numpy() / period, BLOCK_RF)
            for w in wins:
                add(f"gap_serving_best_nbr_mean{w}",
                    _causal_roll(gapbest.groupby(df["drive_id"]), w, "mean"), BLOCK_RF)
            # A3-like margin: how long the best neighbour has already been better
            better = np.nan_to_num(nbr_max > df["serving_rsrp"].to_numpy(float)).astype(float)
            add("nbr_better_streak_s", _streak(pd.Series(better), df["drive_id"]) * period, BLOCK_RF)

    # ------------------------------------------------------------- mobility
    if BLOCK_MOB in blocks:
        add("speed_kmh", df["speed_kmh"], BLOCK_MOB)
        s = gb["speed_kmh"]
        add("accel_kmh_s", s.diff().fillna(0.0) / period, BLOCK_MOB)
        for w in wins:
            add(f"speed_mean{w}", _causal_roll(s, w, "mean"), BLOCK_MOB)
            add(f"speed_std{w}", _causal_roll(s, w, "std").fillna(0.0), BLOCK_MOB)
        brg = bearing_deg(df["lat"].shift(), df["lon"].shift(), df["lat"], df["lon"])
        brg = pd.Series(brg).where(df["drive_seq"] > 0).ffill().fillna(0.0)
        add("bearing_sin", np.sin(np.radians(brg)), BLOCK_MOB)
        add("bearing_cos", np.cos(np.radians(brg)), BLOCK_MOB)
        dbrg = pd.Series(angle_diff_deg(brg, brg.shift().fillna(brg))).fillna(0.0)
        add("bearing_change_deg", dbrg, BLOCK_MOB)
        add("bearing_change_abs_mean", _causal_roll(dbrg.abs().groupby(df["drive_id"]), max(wins), "mean"), BLOCK_MOB)
        add("dist_travelled_m", df["dist_in_drive_m"], BLOCK_MOB)
        stopped = (df["speed_kmh"] < 2.0).astype(float)
        add("stop_duration_s", _streak(stopped, df["drive_id"]) * period, BLOCK_MOB)
        add("is_stopped", stopped, BLOCK_MOB)
        add("mobility_state_fast", (df["speed_kmh"] > 40).astype(float), BLOCK_MOB)
        add("mobility_state_mid", ((df["speed_kmh"] > 15) & (df["speed_kmh"] <= 40)).astype(float), BLOCK_MOB)

    # --------------------------------------------------------------- history
    if BLOCK_HIST in blocks:
        idx = pd.MultiIndex.from_arrays([df["drive_id"], df["t"]])
        tprev = lab["t_since_prev_ho_s"].reindex(idx).to_numpy(float)
        add("t_since_prev_ho_s", np.nan_to_num(tprev, nan=600.0), BLOCK_HIST)
        add("has_prev_ho", np.isfinite(tprev).astype(float), BLOCK_HIST)
        key = "serving_pci" if df["serving_pci"].notna().any() else "serving_cell_name"
        changed = (gb[key].shift() != df[key]) & df[key].notna()
        add("serving_dwell_s", _streak((~changed).astype(float), df["drive_id"], reset_on_zero=True) * period, BLOCK_HIST)
        add("n_ho_so_far", changed.groupby(df["drive_id"]).cumsum().astype(float) - 1.0, BLOCK_HIST)
        prev_cell = df[key].where(changed).groupby(df["drive_id"]).ffill()
        prev_prev = df[key].where(changed).groupby(df["drive_id"]).shift().ffill()
        add("returned_to_source", (df[key] == prev_prev).astype(float), BLOCK_HIST)
        if all(f"nbr{i}_id" in df for i in range(1, k + 1)):
            prev_serving = prev_prev.to_numpy(float)
            cand = df[[f"nbr{i}_id" for i in range(1, k + 1)]].to_numpy(float)
            add("prev_serving_is_candidate",
                (cand == prev_serving[:, None]).any(axis=1).astype(float), BLOCK_HIST)
        add("ho_rate_per_min", np.where(df["t_in_drive_s"] > 0,
                                        (changed.groupby(df["drive_id"]).cumsum().to_numpy(float))
                                        / np.maximum(df["t_in_drive_s"].to_numpy(float), 1.0) * 60.0, 0.0), BLOCK_HIST)

    # ------------------------------------------------------------------- QoE
    if BLOCK_QOE in blocks:
        for col in ["dl_tp_kbps", "ul_tp_kbps", "rtt_ms", "pkt_loss_pct", "phy_dl_kbps", "phy_ul_kbps"]:
            if col not in df or df[col].isna().all():
                continue
            add(col, df[col], BLOCK_QOE)
            s = gb[col]
            add(f"{col}_d1", s.diff().fillna(0.0) / period, BLOCK_QOE)
            for w in wins[:2]:
                add(f"{col}_mean{w}", _causal_roll(s, w, "mean"), BLOCK_QOE)
            w = max(wins)
            add(f"{col}_ratio{w}",
                df[col].to_numpy(float) / np.maximum(_causal_roll(s, w, "mean").to_numpy(float), 1e-6), BLOCK_QOE)
        if "dl_tp_kbps" in df and df["dl_tp_kbps"].notna().any():
            low = (df["dl_tp_kbps"] < df["dl_tp_kbps"].expanding().quantile(0.1).bfill()).astype(float)
            add("dl_low_streak_s", _streak(low, df["drive_id"]) * period, BLOCK_QOE)

    # --------------------------------------------------------------- context
    if BLOCK_CTX in blocks:
        # prefixed so they cannot collide with the meta columns carried alongside
        add("ctx_lat", df["lat"], BLOCK_CTX)
        add("ctx_lon", df["lon"], BLOCK_CTX)
        add("serving_earfcn", df.get("serving_earfcn", np.nan), BLOCK_CTX)
        add("serving_pci_num", df.get("serving_pci", np.nan), BLOCK_CTX)
        add("serving_enb", df.get("serving_enb", np.nan), BLOCK_CTX)
        hour = df["t"].dt.hour + df["t"].dt.minute / 60.0
        add("hour_sin", np.sin(2 * np.pi * hour / 24), BLOCK_CTX)
        add("hour_cos", np.cos(2 * np.pi * hour / 24), BLOCK_CTX)
        for col, prefix in (("serving_band", "band"), ("route_id", "route"), ("direction", "dir")):
            if col in df:
                dummies = pd.get_dummies(df[col].astype(str), prefix=prefix, dtype=float)
                for c in dummies.columns:
                    add(c, dummies[c], BLOCK_CTX)

    # missingness masks
    if cfg.get_path("features.keep_missing_masks", True):
        for col in ["serving_rsrp", "serving_rsrq", "serving_sinr", "dl_tp_kbps", "rtt_ms",
                    "pkt_loss_pct"] + [f"nbr{i}_rsrp" for i in range(1, k + 1)]:
            if col in df:
                add(f"mask_{col}", df[col].isna().astype(float), "mask")

    out = pd.DataFrame(collected, index=df.index).replace([np.inf, -np.inf], np.nan)
    clash = sorted(set(meta.columns) & set(out.columns))
    if clash:
        raise ValueError(f"feature names collide with metadata columns: {clash}")
    result = pd.concat([meta, out], axis=1)
    assert result.columns.is_unique, "duplicate column names in the feature frame"
    LOG.info("built %d features (%s) under regime=%s",
             out.shape[1], {b: sum(1 for v in feature_block.values() if v == b)
                            for b in sorted(set(feature_block.values()))}, regime)
    result.attrs["feature_block"] = feature_block
    result.attrs["feature_names"] = list(out.columns)
    return result


def _causal_slope(df: pd.DataFrame, col: str, win: int, period: float) -> np.ndarray:
    """Least-squares slope of the last ``win`` samples, per drive (causal)."""
    x = np.arange(win, dtype=float) * period
    x = x - x.mean()
    denom = float((x**2).sum()) or 1.0

    def _f(series: pd.Series) -> pd.Series:
        return series.rolling(win, min_periods=2).apply(
            lambda v: float(np.dot(v - v.mean(), x[-len(v):] - x[-len(v):].mean()) / denom), raw=True)

    return df.groupby("drive_id")[col].apply(_f).reset_index(level=0, drop=True).fillna(0.0).to_numpy()


def _streak(flag: pd.Series, group: pd.Series, reset_on_zero: bool = True) -> np.ndarray:
    """Length of the current run of 1s in ``flag``, restarting each group."""
    flag = pd.Series(np.asarray(flag, dtype=float))
    grp = pd.Series(np.asarray(group))
    out = np.zeros(len(flag))
    run = 0
    prev_g = None
    f = flag.to_numpy()
    g = grp.to_numpy()
    for i in range(len(f)):
        if g[i] != prev_g:
            run = 0
            prev_g = g[i]
        run = run + 1 if f[i] > 0 else (0 if reset_on_zero else run)
        out[i] = run
    return out


def select_blocks(features: pd.DataFrame, blocks: list[str]) -> list[str]:
    """Feature names belonging to ``blocks`` (masks always travel with their block)."""
    fb = features.attrs.get("feature_block", {})
    wanted = set(blocks)
    names = [n for n in features.attrs.get("feature_names", []) if fb.get(n) in wanted]
    if "mask" not in wanted:
        keep = []
        for n in features.attrs.get("feature_names", []):
            if fb.get(n) != "mask":
                continue
            base = n[len("mask_"):]
            if any(base in w for w in names):
                keep.append(n)
        names += keep
    return names

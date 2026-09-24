"""Stage R8 - reproducible label construction.

All labels are written once, before any modelling, and every rule below is
declared in ``configs/base.yaml`` so the label set is reproducible from config
alone.

Targets produced per sample ``t``
---------------------------------
``y_ho_h{H}``        1 if a handover occurs in ``(t, t+H]``.
``m_ho_h{H}``        validity mask (0 = sample excluded for that horizon).
``y_pingpong_h{H}``  1 if a handover in ``(t, t+H]`` is a ping-pong event.
``y_qoe_h{H}``       1 if QoE degradation occurs in ``(t, t+H]``.
``y_dwell_s``        time to the next serving-cell transition (censoring flagged).
``y_target_cand``    index of the candidate neighbour that becomes the next
                     serving cell (-1 = no event / target not among candidates).
``cand{i}_is_target`` one-hot form used by the ranking head.

Masking rules
-------------
* ``post_event_blank_s`` after a handover the radio state is still settling and
  the "next" event is trivially predictable, so those samples are masked.
* Samples whose horizon extends past the end of their drive are masked
  (``exclude_trace_tail``), instead of being silently labelled 0.
* Samples inside an un-interpolatable logging hole are masked.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from ..config import Config
from ..utils import get_logger

LOG = get_logger("hoproj.labels")


# --------------------------------------------------------------- HO events
def handover_events(samples: pd.DataFrame, events: pd.DataFrame | None, cfg: Config) -> pd.DataFrame:
    """Canonical per-drive handover event table.

    Columns: drive_id, t, from_pci, to_pci, ho_type, source
    """
    source = cfg.get_path("labels.handover.source", "handover_log")
    tol = pd.Timedelta(seconds=float(cfg.get_path("labels.handover.match_tolerance_s", 1.5)))

    if source in ("handover_log", "signalling") and events is not None:
        ev = events.copy()
        idx = samples[["t", "drive_id", "route_id"]].sort_values("t")
        merged = pd.merge_asof(ev.sort_values("t"), idx, on="t",
                               direction="nearest", tolerance=tol)
        unmatched = merged["drive_id"].isna().sum()
        if unmatched:
            LOG.warning("%d/%d logged handovers fall outside any retained drive", unmatched, len(ev))
        merged = merged.dropna(subset=["drive_id"])
        out = merged[["drive_id", "t"]].copy()
        out["from_pci"] = pd.to_numeric(merged.get("from_pci"), errors="coerce")
        out["to_pci"] = pd.to_numeric(merged.get("to_pci"), errors="coerce")
        out["ho_type"] = merged.get("ho_type", "normal")
        out["source"] = "handover_log"
    else:
        s = samples.sort_values(["drive_id", "t"])
        key = "serving_pci" if s["serving_pci"].notna().any() else "serving_cell_name"
        prev = s.groupby("drive_id")[key].shift()
        changed = prev.notna() & s[key].notna() & (prev != s[key])
        out = pd.DataFrame({
            "drive_id": s.loc[changed, "drive_id"].values,
            "t": s.loc[changed, "t"].values,
            "from_pci": pd.to_numeric(prev[changed], errors="coerce").values,
            "to_pci": pd.to_numeric(s.loc[changed, key], errors="coerce").values,
            "ho_type": "cell_change",
            "source": "serving_cell_change",
        })
    out = out.sort_values(["drive_id", "t"]).reset_index(drop=True)

    # ping-pong / short-stay annotation (temporal definition, fixed in config)
    win = float(cfg.get_path("labels.handover.pingpong_return_window_s", 10.0))
    short = float(cfg.get_path("labels.handover.short_stay_s", 8.0))
    out["dt_next_s"] = out.groupby("drive_id")["t"].diff(-1).dt.total_seconds().abs()
    out["next_to"] = out.groupby("drive_id")["to_pci"].shift(-1)
    out["is_return"] = (out["next_to"] == out["from_pci"]) & (out["dt_next_s"] <= win)
    out["is_short_stay"] = out["dt_next_s"] <= short
    out["is_pingpong"] = out["is_return"].fillna(False)
    if "ho_type" in out:
        out["is_pingpong"] = out["is_pingpong"] | out["ho_type"].astype(str).str.lower().eq("pingpong")
    LOG.info("handover events: %d (%.1f%% ping-pong) from %s",
             len(out), 100 * out["is_pingpong"].mean(), out["source"].iloc[0] if len(out) else "n/a")
    return out


# ------------------------------------------------------------ QoE degradation
def fit_qoe_thresholds(samples: pd.DataFrame, cfg: Config) -> dict:
    """Percentile thresholds fitted on TRAINING samples only."""
    q = cfg.get_path("labels.qoe", {})
    th = {}
    if "dl_tp_kbps" in samples and samples["dl_tp_kbps"].notna().any():
        th["dl_tp_low"] = float(np.nanpercentile(samples["dl_tp_kbps"], q.get("dl_tp_low_pct", 10.0)))
    if "rtt_ms" in samples and samples["rtt_ms"].notna().any():
        th["rtt_high"] = float(np.nanpercentile(samples["rtt_ms"], q.get("rtt_high_pct", 90.0)))
    if "pkt_loss_pct" in samples and samples["pkt_loss_pct"].notna().any():
        th["loss_high"] = float(np.nanpercentile(samples["pkt_loss_pct"], q.get("loss_high_pct", 90.0)))
    th["interruption_dl_kbps"] = float(q.get("interruption_dl_kbps", 50.0))
    th["min_rules"] = int(q.get("min_rules_triggered", 1))
    LOG.info("QoE thresholds (train-only): %s", th)
    return th


def qoe_degraded_instant(samples: pd.DataFrame, th: dict) -> np.ndarray:
    """Boolean per sample: is the service degraded *now*?"""
    rules = []
    if "dl_tp_low" in th and "dl_tp_kbps" in samples:
        rules.append((samples["dl_tp_kbps"] < th["dl_tp_low"]).to_numpy())
    if "rtt_high" in th and "rtt_ms" in samples:
        rules.append((samples["rtt_ms"] > th["rtt_high"]).to_numpy())
    if "loss_high" in th and "pkt_loss_pct" in samples:
        rules.append((samples["pkt_loss_pct"] > th["loss_high"]).to_numpy())
    if "dl_tp_kbps" in samples:
        rules.append((samples["dl_tp_kbps"] < th.get("interruption_dl_kbps", 50.0)).to_numpy())
    if not rules:
        return np.zeros(len(samples), dtype=bool)
    count = np.nansum(np.vstack([r.astype(float) for r in rules]), axis=0)
    return count >= th.get("min_rules", 1)


# ------------------------------------------------------------------- builder
def build_labels(samples: pd.DataFrame, ho: pd.DataFrame, cfg: Config,
                 qoe_thresholds: dict | None = None) -> pd.DataFrame:
    horizons = usable_horizons(cfg)
    blank = float(cfg.get_path("labels.handover.post_event_blank_s", 2.0))
    tail = bool(cfg.get_path("labels.handover.exclude_trace_tail", True))
    k = int(cfg.get_path("features.neighbour_k", 3))

    out = samples[["t", "drive_id", "route_id", "direction"]].copy()
    n = len(samples)
    t_ns = samples["t"].to_numpy("datetime64[ns]").astype("int64")
    drive_codes = pd.factorize(samples["drive_id"])[0]

    # per-drive event times / attributes
    ev_by_drive: dict[str, dict] = {}
    for drive_id, grp in ho.groupby("drive_id"):
        ev_by_drive[drive_id] = {
            "t": grp["t"].to_numpy("datetime64[ns]").astype("int64"),
            "to_pci": grp["to_pci"].to_numpy(float),
            "pingpong": grp["is_pingpong"].to_numpy(bool),
        }
    drive_ids = pd.Series(samples["drive_id"].values)
    drive_end = samples.groupby("drive_id")["t"].transform("max").to_numpy("datetime64[ns]").astype("int64")

    qoe_now = None
    if qoe_thresholds:
        qoe_now = qoe_degraded_instant(samples, qoe_thresholds)
        out["qoe_degraded_now"] = qoe_now

    # time since / until events, per sample
    t_prev = np.full(n, np.nan)
    t_next = np.full(n, np.nan)
    next_to = np.full(n, np.nan)
    for drive_id, idx in drive_ids.groupby(drive_ids).groups.items():
        pos = np.asarray(idx)
        info = ev_by_drive.get(drive_id)
        if info is None or len(info["t"]) == 0:
            continue
        et = info["t"]
        ts = t_ns[pos]
        nxt = np.searchsorted(et, ts, side="right")
        has_next = nxt < len(et)
        t_next[pos[has_next]] = (et[nxt[has_next]] - ts[has_next]) / 1e9
        next_to[pos[has_next]] = info["to_pci"][nxt[has_next]]
        has_prev = nxt > 0
        t_prev[pos[has_prev]] = (ts[has_prev] - et[nxt[has_prev] - 1]) / 1e9

    out["t_since_prev_ho_s"] = t_prev
    out["t_to_next_ho_s"] = t_next
    out["next_target_pci"] = next_to

    # ---- per-horizon binary labels + masks
    horizon_to_end = (drive_end - t_ns) / 1e9
    base_invalid = np.zeros(n, dtype=bool)
    if "is_interpolated" in samples:
        base_invalid |= samples["is_interpolated"].to_numpy(bool) & samples["serving_rsrp"].isna().to_numpy()
    base_invalid |= samples["serving_rsrp"].isna().to_numpy()
    post_blank = np.nan_to_num(t_prev, nan=np.inf) < blank

    for h in horizons:
        tag = _htag(h)
        y = (np.nan_to_num(t_next, nan=np.inf) <= h).astype(np.int8)
        mask = (~base_invalid) & (~post_blank)
        if tail:
            mask &= horizon_to_end >= h
        out[f"y_ho_{tag}"] = y
        out[f"m_ho_{tag}"] = mask.astype(np.int8)

        # ping-pong restricted to horizons where a HO exists
        pp = np.zeros(n, dtype=np.int8)
        for drive_id, idx in drive_ids.groupby(drive_ids).groups.items():
            info = ev_by_drive.get(drive_id)
            if info is None or len(info["t"]) == 0:
                continue
            pos = np.asarray(idx)
            nxt = np.searchsorted(info["t"], t_ns[pos], side="right")
            ok = (nxt < len(info["t"]))
            sel = pos[ok]
            within = (info["t"][nxt[ok]] - t_ns[sel]) / 1e9 <= h
            pp[sel[within]] = info["pingpong"][nxt[ok]][within].astype(np.int8)
        out[f"y_pingpong_{tag}"] = pp

        if qoe_now is not None:
            fut = _future_any(qoe_now, t_ns, drive_codes, h)
            out[f"y_qoe_{tag}"] = fut.astype(np.int8)
            out[f"m_qoe_{tag}"] = mask.astype(np.int8)

    # ---- dwell regression (time to next transition), right-censored flagged
    clip = float(cfg.get_path("labels.dwell.clip_s", 180.0))
    dwell = np.clip(np.nan_to_num(t_next, nan=clip), 0, clip)
    out["y_dwell_s"] = dwell
    out["m_dwell"] = (np.isfinite(t_next) & (~base_invalid)).astype(np.int8)
    if cfg.get_path("labels.dwell.log_transform", True):
        out["y_dwell_log"] = np.log1p(dwell)

    # ---- candidate target-cell label
    cand_ids = np.column_stack([
        pd.to_numeric(samples.get(f"nbr{i}_id"), errors="coerce").to_numpy(float)
        for i in range(1, k + 1)
    ]) if all(f"nbr{i}_id" in samples for i in range(1, k + 1)) else np.full((n, k), np.nan)
    tgt = np.full(n, -1, dtype=np.int8)
    match = cand_ids == next_to[:, None]
    any_match = match.any(axis=1)
    tgt[any_match] = match.argmax(axis=1)[any_match].astype(np.int8)
    out["y_target_cand"] = tgt
    # only meaningful where a handover really is imminent within the longest horizon
    hmax = max(horizons)
    out["m_target"] = ((np.nan_to_num(t_next, nan=np.inf) <= hmax) &
                       (tgt >= 0 if cfg.get_path("labels.target_cell.require_candidate_match", True)
                        else np.ones(n, bool))).astype(np.int8)
    for i in range(k):
        out[f"cand{i+1}_is_target"] = (tgt == i).astype(np.int8)

    _log_prevalence(out, horizons)
    return out


def _future_any(flag: np.ndarray, t_ns: np.ndarray, drive_codes: np.ndarray, h: float) -> np.ndarray:
    """True where ``flag`` is set at any sample in (t, t+h] within the same drive."""
    n = len(flag)
    out = np.zeros(n, dtype=bool)
    order = np.lexsort((t_ns, drive_codes))
    for code in np.unique(drive_codes):
        pos = order[drive_codes[order] == code]
        ts = t_ns[pos]
        fl = flag[pos]
        hi = np.searchsorted(ts, ts + int(h * 1e9), side="right")
        csum = np.concatenate([[0], np.cumsum(fl.astype(np.int64))])
        lo = np.arange(len(ts)) + 1
        out[pos] = (csum[np.clip(hi, 0, len(ts))] - csum[np.clip(lo, 0, len(ts))]) > 0
    return out


def _htag(h: float) -> str:
    return f"h{str(h).replace('.', 'p')}"


def horizon_tags(cfg: Config) -> list[str]:
    return [_htag(float(h)) for h in usable_horizons(cfg)]


def usable_horizons(cfg: Config) -> list[float]:
    """Horizons that the capture's sampling rate can actually label.

    A horizon shorter than one sample period admits no positive label on a
    regular grid, which would silently produce an all-negative target and an
    undefined AUPRC. Such horizons are dropped here, loudly, rather than
    reported as a perfect-or-zero result later.
    """
    period = float(cfg.get_path("data.target_period_s") or 1.0)
    requested = [float(h) for h in cfg.require("labels.horizons_s")]
    # A sub-period horizon is labelable when the EVENT clock is finer than the
    # sample clock. Signalling-confirmed handovers carry millisecond timestamps,
    # so "a handover in the next 0.5 s" is well defined even on a 1 Hz sample
    # grid; only the transition-derived event log, whose events are snapped to
    # the grid, genuinely cannot express it. The flag is opt-in per adapter so
    # the guard still fires by default.
    subperiod_ok = bool(cfg.get_path("labels.allow_subperiod_horizons", False))
    usable = [h for h in requested if subperiod_ok or h >= period - 1e-9]
    dropped = [h for h in requested if h not in usable]
    if dropped:
        LOG.warning("dropping horizons %s: the %.3fs sampling grid cannot label them "
                    "(need >= %.3fs)", dropped, period, period)
    if not usable:
        raise ValueError(f"no horizon in {requested} is labelable at a {period}s sampling period")
    return usable


def _log_prevalence(labels: pd.DataFrame, horizons: list[float]) -> None:
    rows = []
    for h in horizons:
        tag = _htag(h)
        m = labels[f"m_ho_{tag}"].astype(bool)
        rows.append((h, int(m.sum()), float(labels.loc[m, f"y_ho_{tag}"].mean())))
    LOG.info("HO label prevalence: %s",
             ", ".join(f"{h}s={p*100:.2f}% (n={n})" for h, n, p in rows))

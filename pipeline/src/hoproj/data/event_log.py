"""Regenerate a handover event log from a drive-test sample export.

Why this exists
---------------
A supplied event log can fall out of step with the sample export it describes -
a re-export renumbers cells, and the old log then points at a network that is no
longer in the file. The audit detects that (``authenticity.event_sample_pairing``);
this rebuilds the log from the samples so the two are, by construction, the same
capture.

Events are serving-cell transitions. Every derived field is computed from the
sample file alone, so nothing can disagree with it.

Event typing (temporal, declared here and in ``configs/base.yaml``):

``pingpong``  the next transition returns to this event's source cell within
              ``pingpong_return_window_s``.
``short_stay`` the next transition follows within ``short_stay_s`` but goes
              somewhere else.
``stable``    no further transition for at least ``stable_dwell_s``.
``normal``    everything else.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from ..config import Config, load_config, parse_cli_overrides, resolve_paths
from ..utils import get_logger, haversine_m

LOG = get_logger("hoproj.event_log")

COLUMNS = [
    "global_event_id", "corridor", "event_id", "handover_type", "timestamp",
    "from_cell_name", "from_pci", "from_band", "to_cell_name", "to_pci", "to_band",
    "time_since_prev_handover_s", "distance_since_prev_handover_m",
    "avg_speed_prev_segment_kmh", "latitude_at_handover", "longitude_at_handover",
    "serving_rsrp_just_before_dbm", "serving_rsrp_just_after_dbm",
]


def regenerate(samples: pd.DataFrame, cfg: Config,
               corridor_names: dict[int, str] | None = None,
               session_gap_s: float = 5.0) -> pd.DataFrame:
    """Build the event table from ``samples`` (canonical column names)."""
    df = samples.sort_values("t").reset_index(drop=True)
    gap = df["t"].diff().dt.total_seconds().fillna(session_gap_s + 1)
    df["_session"] = (gap > session_gap_s).cumsum()

    key = "serving_pci" if df["serving_pci"].notna().any() else "serving_cell_name"
    prev = df.groupby("_session")[key].shift()
    changed = prev.notna() & df[key].notna() & (prev != df[key])
    idx = np.flatnonzero(changed.to_numpy())
    LOG.info("found %d serving-cell transitions across %d sessions",
             len(idx), df["_session"].nunique())

    ret_win = float(cfg.get_path("labels.handover.pingpong_return_window_s", 10.0))
    short = float(cfg.get_path("labels.handover.short_stay_s", 8.0))
    stable = float(cfg.get_path("labels.handover.stable_dwell_s", 60.0))

    step = haversine_m(df["lat"].shift(), df["lon"].shift(), df["lat"], df["lon"])
    step = pd.Series(np.nan_to_num(step), index=df.index)
    step[df["_session"] != df["_session"].shift()] = 0.0
    cum = step.cumsum()

    rows = []
    for n, i in enumerate(idx):
        b, a = df.iloc[i - 1], df.iloc[i]
        rows.append({
            "timestamp": a["t"],
            "_session": int(a["_session"]),
            "from_cell_name": b.get("serving_cell_name"),
            "from_pci": b.get("serving_pci"),
            "from_band": b.get("serving_band"),
            "to_cell_name": a.get("serving_cell_name"),
            "to_pci": a.get("serving_pci"),
            "to_band": a.get("serving_band"),
            "latitude_at_handover": a.get("lat"),
            "longitude_at_handover": a.get("lon"),
            "serving_rsrp_just_before_dbm": b.get("serving_rsrp"),
            "serving_rsrp_just_after_dbm": a.get("serving_rsrp"),
            "_cum_m": float(cum.iloc[i]),
            "_row": int(i),
        })
    ev = pd.DataFrame(rows)
    if ev.empty:
        return pd.DataFrame(columns=COLUMNS)

    # per-session sequencing
    ev = ev.sort_values(["_session", "timestamp"]).reset_index(drop=True)
    g = ev.groupby("_session")
    ev["time_since_prev_handover_s"] = g["timestamp"].diff().dt.total_seconds()
    ev["distance_since_prev_handover_m"] = g["_cum_m"].diff().round(1)
    ev["avg_speed_prev_segment_kmh"] = (
        ev["distance_since_prev_handover_m"] / ev["time_since_prev_handover_s"] * 3.6).round(1)

    dt_next = -g["timestamp"].diff(-1).dt.total_seconds()
    next_to = g["to_pci"].shift(-1)
    is_return = (next_to == ev["from_pci"]) & (dt_next <= ret_win)
    is_short = (~is_return) & (dt_next <= short)
    is_stable = dt_next.isna() | (dt_next >= stable)
    ev["handover_type"] = np.select(
        [is_return.fillna(False), is_short.fillna(False), is_stable.fillna(False)],
        ["pingpong", "short_stay", "stable"], default="normal")

    # corridor label: one per contiguous logging session
    # map the supplied names onto the sessions in chronological order, whatever
    # integers ``mark_sessions`` happened to assign
    order = {sid: rank for rank, sid in enumerate(sorted(ev["_session"].unique()))}
    names = corridor_names or {}
    ev["corridor"] = ev["_session"].map(
        lambda s: names.get(order[s], f"session_{order[s] + 1:02d}"))
    ev["event_id"] = ev.groupby("corridor").cumcount() + 1
    ev = ev.sort_values("timestamp").reset_index(drop=True)
    ev["global_event_id"] = np.arange(1, len(ev) + 1)
    ev["timestamp"] = ev["timestamp"].dt.strftime("%m/%d/%Y %H:%M:%S.%f").str[:-3]

    out = ev[COLUMNS]
    LOG.info("regenerated event log: %d events | %s",
             len(out), out["handover_type"].value_counts().to_dict())
    LOG.info("per corridor: %s", out.groupby("corridor").size().to_dict())
    return out


def validate(samples: pd.DataFrame, events: pd.DataFrame) -> dict:
    """Confirm the regenerated log actually matches the samples it came from."""
    serv = set(pd.to_numeric(samples["serving_pci"], errors="coerce").dropna().astype(int))
    tgt = set(pd.to_numeric(events["to_pci"], errors="coerce").dropna().astype(int))
    t_ev = pd.to_datetime(events["timestamp"], format="%m/%d/%Y %H:%M:%S.%f")
    s = samples.set_index("t").sort_index()
    match = 0
    for t, to in zip(t_ev, events["to_pci"]):
        try:
            match += int(s.loc[t:].iloc[0]["serving_pci"] == to)
        except Exception:
            pass
    return {
        "events": int(len(events)),
        "targets_seen_as_serving_cell": len(tgt & serv) / max(len(tgt), 1),
        "target_matches_sample_at_event_time": match / max(len(events), 1),
        "median_gap_between_events_s": float(
            pd.to_numeric(events["time_since_prev_handover_s"], errors="coerce").median()),
        # active logging time only - the wall-clock span includes overnight gaps
        "events_per_active_minute": float(
            len(events) / (samples.groupby(
                (samples["t"].diff().dt.total_seconds().fillna(999) > 5).cumsum()
            )["t"].agg(lambda s: (s.max() - s.min()).total_seconds()).sum() / 60)),
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description="Regenerate a handover log from a sample export")
    ap.add_argument("--config", default="base.yaml")
    ap.add_argument("--adapter", default="curated_v1")
    ap.add_argument("--root", default=None)
    ap.add_argument("--out", default="HANDOVER_LOG_REGENERATED.csv")
    ap.add_argument("--corridors", nargs="*", default=[],
                    help="names for each contiguous logging session, in order")
    ap.add_argument("--set", dest="overrides", nargs="*", default=[])
    args = ap.parse_args(argv)

    cfg = load_config(args.config, adapter=args.adapter,
                      overrides=parse_cli_overrides(args.overrides))
    paths = resolve_paths(cfg, args.root)
    from .ingest import load_samples, mark_sessions

    samples = mark_sessions(load_samples(cfg, paths["raw"]),
                            float(cfg.get_path("data.session_gap_s", 5.0)))
    names = {i: n for i, n in enumerate(args.corridors)} if args.corridors else None
    ev = regenerate(samples, cfg, names)
    out = paths["raw"] / args.out
    ev.to_csv(out, index=False)
    LOG.info("wrote %s", out)
    for k, v in validate(samples, ev).items():
        LOG.info("  %-38s %s", k, round(v, 4) if isinstance(v, float) else v)
    return out


if __name__ == "__main__":
    main()

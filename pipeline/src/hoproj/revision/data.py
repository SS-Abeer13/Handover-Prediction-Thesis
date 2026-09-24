"""Revision dataset (review of 17 Sept 2026).

Differences from stage 12/13, each tied to a reviewer concern:

* C9  - export row semantics. A 1 Hz XCAL row stamped t already shows the
        post-handover serving cell for 74 % of handovers whose command is sent
        in (t, t+1) (``row_alignment_audit``). The row therefore summarises the
        window that *ends* near t+1. Every export-derived feature is lagged by
        one row, so the information cut-off of a prediction at t is t.
* C1  - history is computed over the whole session from signalling
        timestamps, not per 180 s chunk (removes left truncation, alfa) and
        not from the export's serving-cell column (which carries the leak).
* C4  - one common row set for every horizon (rows with >= 5 s of follow-up
        and outside the 2 s post-handover blank), so the prevalence table and
        the hazard table are the same numbers seen two ways.
* C15 - re-establishments are carried as a competing event.
"""
from __future__ import annotations

import pickle
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

from ..data.features import select_blocks
from ..utils import get_logger, read_json, read_table

LOG = get_logger("hoproj.rev.data")

EDGES = [0.5, 1.0, 2.0, 3.0, 5.0]
CAPTURE_NAMES = {"XCAL10Sept": "10 Sept (urban arterial)",
                 "XCAL12Sept": "12 Sept (urban loop)",
                 "XCAL13Sept": "13 Sept (dense urban)",
                 "XCAL15Sept": "15 Sept (highway)"}
HIST = ["t_since_prev_ho_s", "has_prev_ho", "t_since_prev2_ho_s",
        "ho_count_30s", "ho_count_60s", "last_ho_was_return"]
BLANK_S = 2.0
BURST_GAP_S = 10.0


@dataclass
class RevData:
    frame: pd.DataFrame                  # one row per usable sample
    X: pd.DataFrame                      # model features (lagged export + session history)
    names: dict[str, list[str]]          # block -> feature names
    events: pd.DataFrame                 # all completed handover commands
    reest: pd.DataFrame                  # re-establishment requests
    info: dict = field(default_factory=dict)
    full: pd.DataFrame | None = None     # every row, incl. masked ones (for windows)

    @property
    def Y(self) -> np.ndarray:
        return np.column_stack([self.frame[f"y_{i}"].to_numpy(int) for i in range(len(EDGES))])

    def feats(self, blocks: list[str]) -> list[str]:
        return [n for b in blocks for n in self.names[b]]


def _prev_times(ev_t: np.ndarray, t: np.ndarray, k: int) -> np.ndarray:
    """Time of the k-th most recent event strictly before t (NaN if none)."""
    i = np.searchsorted(ev_t, t, side="left") - k
    out = np.full(len(t), np.nan)
    ok = i >= 0
    out[ok] = ev_t[i[ok]]
    return out


def row_alignment_audit(feats: pd.DataFrame, events: pd.DataFrame) -> pd.DataFrame:
    """Share of handovers whose target already serves in export rows around the command."""
    rows = []
    for cap, s in feats.groupby("capture"):
        s = s.set_index("t").sort_index()
        ev = events[events.capture == cap].sort_values("t")
        gaps = ev["t"].diff().dt.total_seconds().fillna(99).to_numpy()
        for (tau, tgt), gap in zip(ev[["t", "target_pci"]].itertuples(index=False), gaps):
            t0 = tau.floor("s")
            r = {"capture": cap, "isolated": gap > 8}
            for k in range(-3, 2):
                tt = t0 + pd.Timedelta(seconds=k)
                r[k] = float(s.at[tt, "serving_pci"] == tgt) if tt in s.index else np.nan
            rows.append(r)
    x = pd.DataFrame(rows)
    out = []
    for lab, g in (("all handovers", x), ("isolated (previous > 8 s earlier)", x[x.isolated])):
        out.append({"subset": lab, "n": int(g[0].notna().sum()),
                    **{f"row t{'+' if k >= 0 else ''}{k}": round(float(g[k].mean()), 3)
                       for k in range(-3, 2)}})
    return pd.DataFrame(out)


# ---------------------------------------------------------------- C9 (round 3)
# Which export features does the end-of-second flip actually contaminate?  The
# mechanism of Section 5.1 flips the serving-cell *assignment* inside the second.
# Everything measured relative to that assignment moves with it:
#   * ``serving_*``      - the radio scalars are measured on whichever cell serves,
#                          so after the flip they describe the TARGET, not the source;
#   * ``nbr*``/``gap_*``  - the neighbour list is defined against the serving cell, so
#                          after the flip the old serving cell becomes a neighbour and
#                          the A3 gap inverts;
#   * the cfg columns     - the configuration in force is attached to the serving cell.
# Nothing in the mobility block depends on the assignment: speed, acceleration,
# bearing and distance come from GPS.  ``lag_scope`` selects which of these groups
# is lagged, so the cost of the repair can be separated from the cost of the leak.
LAG_SCOPES = ("all", "assignment", "serving", "neighbour", "none")


def _lag_columns(scope: str, rf: list[str], mob: list[str], cfg: list[str]) -> list[str]:
    if scope == "all":
        return rf + mob + cfg
    if scope == "assignment":                 # every serving-relative column, GPS kept live
        return rf + cfg
    if scope == "serving":                    # only the serving-cell radio scalars
        return [c for c in rf if c.startswith("serving_")]
    if scope == "neighbour":                  # only the neighbour/gap columns and cfg
        keep = [c for c in rf if c.startswith(("nbr", "gap_"))
                or c in ("serving_rank_among_cands",)]
        return keep + cfg
    if scope == "none":
        return []
    raise KeyError(scope)


def load_revision_data(processed: Path, sig_pickle: Path, lag: int = 1,
                       censor_reest: bool = False,
                       reports_pickle: Path | None = None,
                       lag_scope: str = "all",
                       blank_s: float | None = None,
                       burst_gap_s: float | None = None) -> RevData:
    # Both windows are post-hoc choices (2 s and 10 s). They are arguments rather than
    # constants so stage 30 can show the results do not depend on where they were set.
    blank_s = BLANK_S if blank_s is None else blank_s
    burst_gap_s = BURST_GAP_S if burst_gap_s is None else burst_gap_s
    feats = read_table(processed / "features.parquet")
    meta = read_json(processed / "feature_meta.json")
    feats.attrs["feature_block"] = meta["feature_block"]
    feats.attrs["feature_names"] = meta["feature_names"]
    feats["t"] = pd.to_datetime(feats["t"])
    sig = pickle.load(open(sig_pickle, "rb"))
    ev = []
    re_ = []
    for cap, v in sig.items():
        h = v["handovers"]
        h = h[h["completed"]].copy()
        h["capture"] = cap
        ev.append(h[["capture", "t", "target_pci", "target_earfcn"]])
        f = v["failures"].copy()
        f["capture"] = cap
        re_.append(f[["capture", "t", "cause"]])
    events = pd.concat(ev, ignore_index=True).sort_values(["capture", "t"]).reset_index(drop=True)
    reest = pd.concat(re_, ignore_index=True).sort_values(["capture", "t"]).reset_index(drop=True)

    rf = [n for n in select_blocks(feats, ["rf"]) if n in feats.columns]
    mob = [n for n in select_blocks(feats, ["mobility"]) if n in feats.columns]
    cfg_cols = ["a3_offset_db", "hysteresis_db", "time_to_trigger_ms"]
    cfg_present = [c for c in cfg_cols if c in feats.columns]
    export_cols = _lag_columns(lag_scope, rf, mob, cfg_present)
    all_export = rf + mob + cfg_present

    feats = feats.sort_values(["capture", "t"]).reset_index(drop=True)
    parts = []
    for cap, g in feats.groupby("capture", sort=True):
        g = g.copy()
        t0 = g["t"].min()
        g["ts"] = (g["t"] - t0).dt.total_seconds()
        # ---- C9: lag export features by `lag` rows, only across a true 1 s step
        if lag and export_cols:
            lagged = g.set_index("t")[export_cols]
            lagged.index = lagged.index + pd.Timedelta(seconds=lag)
            g[export_cols] = lagged.reindex(g["t"]).to_numpy()
        e = events[events.capture == cap]
        et = ((e["t"] - t0).dt.total_seconds()).to_numpy()
        tgt = e["target_pci"].to_numpy()
        rt = ((reest.loc[reest.capture == cap, "t"] - t0).dt.total_seconds()).to_numpy()
        ts = g["ts"].to_numpy()
        # ---- session-level history from signalling timestamps (strictly < t)
        p1 = _prev_times(et, ts, 1)
        p2 = _prev_times(et, ts, 2)
        g["t_since_prev_ho_s"] = np.nan_to_num(ts - p1, nan=600.0).clip(0, 600)
        g["has_prev_ho"] = np.isfinite(p1).astype(float)
        g["t_since_prev2_ho_s"] = np.nan_to_num(ts - p2, nan=600.0).clip(0, 600)
        n_before = np.searchsorted(et, ts, side="left")
        g["ho_count_30s"] = n_before - np.searchsorted(et, ts - 30, side="left")
        g["ho_count_60s"] = n_before - np.searchsorted(et, ts - 60, side="left")
        ret = np.zeros(len(et))
        ret[2:] = (tgt[2:] == tgt[:-2]).astype(float)
        idx = n_before - 1
        g["last_ho_was_return"] = np.where(idx >= 0, ret[np.clip(idx, 0, None)], 0.0)
        # ---- labels on the event clock
        nxt = np.searchsorted(et, ts, side="right")
        t_next = np.where(nxt < len(et), et[np.clip(nxt, 0, len(et) - 1)] - ts, np.inf)
        rn = np.searchsorted(rt, ts, side="right")
        t_reest = np.where(rn < len(rt), rt[np.clip(rn, 0, max(len(rt) - 1, 0))] - ts, np.inf) \
            if len(rt) else np.full(len(ts), np.inf)
        g["t_next_ho_s"] = t_next
        g["t_next_reest_s"] = t_reest
        g["t_to_session_end_s"] = ts.max() - ts
        g["next_is_first_in_burst"] = False
        has_next = nxt < len(et)
        gap_before_next = np.full(len(ts), np.inf)
        j = nxt[has_next]
        gap_before_next[has_next] = np.where(j > 0, et[j] - et[np.clip(j - 1, 0, None)], np.inf)
        g["next_is_first_in_burst"] = gap_before_next > burst_gap_s
        g["in_burst"] = (ts - p1) <= burst_gap_s
        g["next_event_idx"] = np.where(has_next, nxt, -1)
        parts.append(g)
    df = pd.concat(parts, ignore_index=True)
    t0s = {cap: g["t"].min() for cap, g in df.groupby("capture")}
    if reports_pickle is not None:
        rv2 = {k: v["reports"] for k, v in pickle.load(open(reports_pickle, "rb")).items()}
        df = pd.concat([df, add_signalling_block(df, rv2, t0s)], axis=1)
    else:
        for c in SIG:
            df[c] = np.nan

    for k, e in enumerate(EDGES):
        df[f"y_{k}"] = (df["t_next_ho_s"] <= e).astype(int)
    valid = (df["t_to_session_end_s"] >= EDGES[-1]) & (df["t_since_prev_ho_s"] >= blank_s)
    if lag and export_cols:
        valid &= df[export_cols].notna().any(axis=1)
    df["competing_first"] = (df["t_next_reest_s"] < np.minimum(df["t_next_ho_s"], EDGES[-1]))
    if censor_reest:
        valid &= ~df["competing_first"]
    full = df[["capture", "t"] + rf + mob + HIST + SIG].copy()
    df = df[valid].reset_index(drop=True)
    names = {"rf": rf, "mobility": mob, "history": HIST, "signalling": SIG}
    X = df[rf + mob + HIST + SIG].astype(float)
    df["km_step"] = df["speed_kmh"].fillna(0).to_numpy() / 3600.0
    info = {"lag": lag, "lag_scope": lag_scope, "n_lagged": len(export_cols),
            "n_export": len(all_export), "censor_reest": censor_reest, "n_rows": int(len(df)),
            "n_events_total": int(len(events)), "n_reest_total": int(len(reest)),
            "n_features": len(rf + mob + HIST),
            "prevalence": {e: float(df[f"y_{k}"].mean()) for k, e in enumerate(EDGES)}}
    LOG.info("revision data (lag=%d, censor_reest=%s): %d rows, %d features, prevalence %s",
             lag, censor_reest, len(df), X.shape[1],
             {e: round(v, 4) for e, v in info["prevalence"].items()})
    return RevData(df, X, names, events, reest, info, full)


SIG = ["sig_a3_prev1s", "sig_a3_prev2s", "sig_a3_prev5s", "sig_all_prev2s", "sig_all_prev5s",
       "sig_s_since_a3", "sig_a3_hold_s", "cfg_a3_offset_db", "cfg_hysteresis_db",
       "cfg_ttt_ms"]


def add_signalling_block(df: pd.DataFrame, reports_v2: dict, t0s: dict) -> pd.DataFrame:
    """Signalling features with the information cut-off at the prediction instant t.

    Reports are counted in (t - w, t]; a report sent at t - 50 ms is something
    the network already holds at t. The A3 hold clock runs on the lagged export
    gap and the lagged profile in force (Off, Hys, TTT).
    """
    out = pd.DataFrame(index=df.index, columns=SIG, dtype=float)
    for cap, g in df.groupby("capture"):
        rep = reports_v2[cap]
        t0 = t0s[cap]
        rt = np.sort(((rep["t"] - t0).dt.total_seconds()).to_numpy())
        ra = np.sort(((rep.loc[rep["event_id"] == "A3", "t"] - t0).dt.total_seconds()).to_numpy())
        ts = g["ts"].to_numpy()
        for w in (1, 2, 5):
            out.loc[g.index, f"sig_a3_prev{w}s"] = (np.searchsorted(ra, ts, "left")
                                                    - np.searchsorted(ra, ts - w, "left"))
        for w in (2, 5):
            out.loc[g.index, f"sig_all_prev{w}s"] = (np.searchsorted(rt, ts, "left")
                                                     - np.searchsorted(rt, ts - w, "left"))
        i = np.searchsorted(ra, ts, "left") - 1
        out.loc[g.index, "sig_s_since_a3"] = np.where(i >= 0, ts - ra[np.clip(i, 0, None)], 120.0).clip(0, 120)
        off = g["a3_offset_db"].astype(float)
        hys = g["hysteresis_db"].astype(float).fillna(0)
        held = (g["gap_serving_nbr1"] < -(off + hys)).fillna(False).to_numpy()
        run = np.zeros(len(g))
        for j in range(1, len(g)):
            if held[j] and held[j - 1] and ts[j] - ts[j - 1] <= 1.0 + 1e-6:
                run[j] = run[j - 1] + 1.0
        out.loc[g.index, "sig_a3_hold_s"] = run
        out.loc[g.index, "cfg_a3_offset_db"] = off.to_numpy()
        out.loc[g.index, "cfg_hysteresis_db"] = g["hysteresis_db"].astype(float).to_numpy()
        out.loc[g.index, "cfg_ttt_ms"] = g["time_to_trigger_ms"].astype(float).to_numpy()
    return out.astype(float)

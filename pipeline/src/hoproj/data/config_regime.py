"""Attribute every handover to the network's own handover-control parameters.

The RRC signalling carries a complete chain from a measurement report back to
the rule that triggered it:

    measurementReport.measId
      -> measIdToAddModList:      measId -> measObjectId + reportConfigId
      -> reportConfigToAddModList: reportConfigId -> A3 offset / hysteresis / TTT
      -> measObjectId             -> carrier frequency

So each handover can be labelled with the A3 offset, hysteresis and
time-to-trigger that were active when it fired. That turns the network's
configuration from unobserved context into a measured variable, which is what
makes a controlled configuration-shift experiment possible: several A3 profiles
run concurrently on different carriers inside the same drive, so city, UE,
driver, day and route are all held fixed while the rule varies.

A3 semantics (TS 36.331 clause 5.5.4.4): the offset is signalled in half-dB
steps and may be negative, meaning the network hands over while the neighbour is
still *weaker* than the serving cell. Hysteresis is also in half-dB steps.

**The identifiers are message-scoped, not global.** ``reportConfigId`` and
``measId`` are indices into the UE's current measurement configuration, and the
network rewrites that configuration constantly - typically at every handover. In
one 60-minute capture, 29 of 30 observed reportConfigIds denote a *different
event type* (A1/A2/A3/A4/A5/A6) at different points in the log, and every one of
32 measIds points at many different reportConfigIds over time.

A parser that flattens the whole file into one dictionary therefore lets later
definitions silently overwrite earlier ones and attributes handovers to rules
that were not in force when they fired. This module instead maintains a
**configuration timeline**: each measConfig occurrence updates a running state
(3GPP measConfig is incremental - AddMod inserts or replaces, RemoveList
deletes), and every measurement report is resolved against the state in force at
its own timestamp.

Ghoshal et al. (arXiv:2511.03116) report that the simpler "the last measurement
report triggered the handover" assumption misattributes ~12% of handovers; the
identifier-scoping error corrected here is a distinct and larger one.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from ..utils import get_logger

LOG = get_logger("hoproj.config_regime")

TTT_MS = {
    "ms0": 0, "ms40": 40, "ms64": 64, "ms80": 80, "ms100": 100, "ms128": 128,
    "ms160": 160, "ms256": 256, "ms320": 320, "ms480": 480, "ms512": 512,
    "ms640": 640, "ms1024": 1024, "ms1280": 1280, "ms2560": 2560, "ms5120": 5120,
}

_REPORT_CFG = re.compile(
    r"reportConfigId\s+(\d+)\s*,\s*reportConfig reportConfigEUTRA\s*:(.*?)"
    r"(?=reportConfigId\s+\d+|measIdToAddModList|$)", re.S)
_MEAS_ID = re.compile(
    r"measId\s+(\d+)\s*,\s*measObjectId\s+(\d+)\s*,\s*reportConfigId\s+(\d+)")
_MEAS_OBJ = re.compile(r"measObjectId\s+(\d+)\s*,\s*measObject measObjectEUTRA\s*:\s*"
                       r"carrierFreq\s+(\d+)", re.S)


_PC_TS = re.compile(r"PC Timestamp:\s*\[\s*(\d{4})\s+(\w{3})\s+(\d{1,2})\s+"
                    r"(\d{2}:\d{2}:\d{2}\.\d+)\s*\]")
_RECORD = re.compile(r"\n(?=\d{2}:\d{2}:\d{2}\.\d+\t)")


@dataclass
class RegimeMaps:
    """A configuration TIMELINE, not a flat map.

    ``states`` is ordered by time; each entry is the full configuration in force
    from that timestamp until the next one.
    """
    times: list[pd.Timestamp]
    states: list[dict]                   # {"meas_id": {...}, "report_config": {...}, "carrier": {...}}

    def at(self, t) -> dict:
        i = int(np.searchsorted(np.asarray(self.times, dtype="datetime64[ns]"),
                                np.datetime64(t), side="right")) - 1
        return self.states[i] if i >= 0 else {"meas_id": {}, "report_config": {}, "carrier": {}}

    # convenience for callers that only need the final state
    @property
    def report_config(self) -> dict:
        return self.states[-1]["report_config"] if self.states else {}

    @property
    def meas_id(self) -> dict:
        return self.states[-1]["meas_id"] if self.states else {}

    @property
    def carrier(self) -> dict:
        return self.states[-1]["carrier"] if self.states else {}


def _parse_block(body: str) -> tuple[dict, dict, dict]:
    """reportConfig / measId / measObject definitions inside one measConfig."""
    rc: dict[int, dict] = {}
    for cid, cfg in _REPORT_CFG.findall(body):
        ev = re.search(r"eventId\s+event(\w+)\s*:", cfg)
        entry = {"event": ev.group(1) if ev else None,
                 "a3_offset_db": np.nan, "hysteresis_db": np.nan,
                 "time_to_trigger_ms": np.nan}
        a3 = re.search(r"a3-Offset\s+(-?\d+)", cfg)
        if a3 and entry["event"] == "A3":
            entry["a3_offset_db"] = int(a3.group(1)) * 0.5
        hy = re.search(r"hysteresis\s+(\d+)", cfg)
        if hy:
            entry["hysteresis_db"] = int(hy.group(1)) * 0.5
        tt = re.search(r"timeToTrigger\s+(\w+)", cfg)
        if tt:
            entry["time_to_trigger_ms"] = TTT_MS.get(tt.group(1), np.nan)
        rc[int(cid)] = entry
    mid = {int(m): (int(o), int(c)) for m, o, c in _MEAS_ID.findall(body)}
    car = {int(o): int(f) for o, f in _MEAS_OBJ.findall(body)}
    return rc, mid, car


def parse_maps(path: str | Path) -> RegimeMaps:
    """Build the configuration timeline by replaying every measConfig in order."""
    txt = Path(path).read_text(errors="replace")
    times: list[pd.Timestamp] = []
    states: list[dict] = []
    rc: dict[int, dict] = {}
    mid: dict[int, tuple[int, int]] = {}
    car: dict[int, int] = {}
    n_msg = 0
    for rec in _RECORD.split(txt):
        if "measConfig" not in rec and "reportConfigToAddModList" not in rec:
            continue
        ts = _PC_TS.search(rec)
        if not ts:
            continue
        y, mon, day, clock = ts.groups()
        t = pd.to_datetime(f"{y}-{mon}-{day} {clock}", format="%Y-%b-%d %H:%M:%S.%f")
        d_rc, d_mid, d_car = _parse_block(rec)
        if not (d_rc or d_mid or d_car):
            continue
        # measConfig is incremental: AddMod inserts or replaces
        rc = {**rc, **d_rc}
        mid = {**mid, **d_mid}
        car = {**car, **d_car}
        times.append(t)
        states.append({"report_config": dict(rc), "meas_id": dict(mid), "carrier": dict(car)})
        n_msg += 1
    if not states:
        states = [{"report_config": {}, "meas_id": {}, "carrier": {}}]
        times = [pd.Timestamp("1970-01-01")]
    final = states[-1]
    n_a3 = sum(1 for v in final["report_config"].values() if v.get("event") == "A3")
    LOG.info("config timeline: %d measConfig updates; final state has %d reportConfigs "
             "(%d A3), %d measId links, %d carriers", n_msg,
             len(final["report_config"]), n_a3, len(final["meas_id"]), len(final["carrier"]))
    return RegimeMaps(times, states)


def annotate_reports(reports: pd.DataFrame, maps: RegimeMaps) -> pd.DataFrame:
    """Resolve each MeasurementReport against the configuration in force AT ITS TIME."""
    out = reports.copy()
    rcid, obj, ev = [], [], []
    a3o, hys, ttt, car = [], [], [], []
    for t, m in zip(out["t"], out["meas_id"]):
        st = maps.at(t)
        link = st["meas_id"].get(int(m)) if pd.notna(m) else None
        o, c = link if link else (None, None)
        cfg = st["report_config"].get(c, {}) if c is not None else {}
        rcid.append(c); obj.append(o); ev.append(cfg.get("event"))
        a3o.append(cfg.get("a3_offset_db", np.nan))
        hys.append(cfg.get("hysteresis_db", np.nan))
        ttt.append(cfg.get("time_to_trigger_ms", np.nan))
        car.append(st["carrier"].get(o) if o is not None else np.nan)
    out["report_config_id"] = rcid
    out["meas_object_id"] = obj
    out["event_id"] = ev
    out["a3_offset_db"] = a3o
    out["hysteresis_db"] = hys
    out["time_to_trigger_ms"] = ttt
    out["carrier_earfcn"] = car
    n = len(out)
    if n:
        LOG.info("reports resolved: %.1f%% to a config, of which %.1f%% are A3 "
                 "(event mix: %s)", 100 * float(pd.notna(out["report_config_id"]).mean()),
                 100 * float((out["event_id"] == "A3").mean()),
                 out["event_id"].value_counts(dropna=False).head(6).to_dict())
    return out


def attribute_handovers(handovers: pd.DataFrame, reports: pd.DataFrame,
                        tolerance_s: float = 5.0) -> pd.DataFrame:
    """Label each handover with the A3 profile of the most recent A3 report before it.

    A handover follows the measurement report that triggered it, so the last A3
    report inside ``tolerance_s`` identifies the rule in force.
    """
    a3 = reports[reports["a3_offset_db"].notna()].sort_values("t")
    if not len(a3) or not len(handovers):
        out = handovers.copy()
        for c in ("a3_offset_db", "hysteresis_db", "time_to_trigger_ms", "carrier_earfcn"):
            out[c] = np.nan
        return out
    cols = ["t", "a3_offset_db", "hysteresis_db", "time_to_trigger_ms", "carrier_earfcn",
            "report_config_id"]
    out = pd.merge_asof(handovers.sort_values("t"), a3[[c for c in cols if c in a3]],
                        on="t", direction="backward",
                        tolerance=pd.Timedelta(seconds=tolerance_s))
    out["regime"] = regime_label(out)
    frac = float(out["a3_offset_db"].notna().mean())
    LOG.info("attributed %.0f%% of %d handovers to an A3 profile; regimes: %s",
             100 * frac, len(out),
             out["regime"].value_counts().to_dict())
    return out


def regime_label(df: pd.DataFrame) -> pd.Series:
    """Compact, sortable name for a configuration regime."""
    def _one(r):
        if pd.isna(r.get("a3_offset_db")):
            return "unattributed"
        ttt = r.get("time_to_trigger_ms")
        return (f"A3{r['a3_offset_db']:+.1f}dB"
                f"/TTT{int(ttt) if pd.notna(ttt) else '?'}ms")
    return df.apply(_one, axis=1)


def regime_to_samples(samples: pd.DataFrame, reports: pd.DataFrame,
                      tolerance_s: float = 5.0) -> pd.DataFrame:
    """Project the active A3 parameters onto the sample grid.

    Gives every sample the rule that governs it, so a model can be conditioned on
    the configuration rather than having to infer it.
    """
    a3 = reports[reports["a3_offset_db"].notna()].sort_values("t")
    cols = ["t", "a3_offset_db", "hysteresis_db", "time_to_trigger_ms", "carrier_earfcn"]
    if not len(a3):
        out = samples.copy()
        for c in cols[1:]:
            out[c] = np.nan
        return out
    merged = pd.merge_asof(samples.sort_values("t"), a3[[c for c in cols if c in a3]],
                           on="t", direction="backward",
                           tolerance=pd.Timedelta(seconds=tolerance_s))
    LOG.info("A3 parameters projected onto %.0f%% of samples",
             100 * float(merged["a3_offset_db"].notna().mean()))
    return merged


def regime_table(attributed: pd.DataFrame) -> pd.DataFrame:
    """One row per configuration regime: counts and the behaviour it produces."""
    df = attributed.dropna(subset=["a3_offset_db"]).copy()
    if not len(df):
        return pd.DataFrame()
    df = df.sort_values("t")
    df["gap_s"] = df["t"].diff().dt.total_seconds()
    g = df.groupby(["a3_offset_db", "hysteresis_db", "time_to_trigger_ms"])
    tbl = pd.DataFrame({
        "handovers": g.size(),
        "median_gap_s": g["gap_s"].median(),
        "frac_under_10s": g["gap_s"].apply(lambda s: float((s < 10).mean())),
        "carriers": g["carrier_earfcn"].nunique(),
    })
    if "interrupt_ms" in df:
        tbl["median_interrupt_ms"] = g["interrupt_ms"].median()
    return tbl.reset_index().sort_values("handovers", ascending=False)

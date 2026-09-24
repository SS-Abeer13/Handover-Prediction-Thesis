"""Configuration timeline v2 - VarMeasConfig replay per TS 36.331 section 5.5.2.

Review response (alfa, C14/Contribution 4). The v1 timeline in
``config_regime.py`` accumulated AddMod entries correctly but ignored three
parts of the standard, all of which are present in these logs:

* ``measIdToRemoveList`` / ``reportConfigToRemoveList`` /
  ``measObjectToRemoveList`` (5.5.2.2, 5.5.2.4, 5.5.2.5). Removing a
  reportConfig or a measObject also removes every measId that links to it.
  v1 kept removed bindings alive (2,917 measId removals in the four logs).
* The measId swap on an inter-frequency handover (5.5.6.1): when
  ``mobilityControlInfo`` carries a carrier that differs from the source
  carrier, measIds linked to the source-carrier object are re-linked to the
  target-carrier object and vice versa, before the measConfig carried in the
  same message is applied.
* Release of the whole VarMeasConfig when the UE leaves RRC_CONNECTED
  (``rrcConnectionRelease``) or sets up a fresh connection.

It also records ``reportInterval``, ``reportAmount``, ``reportOnLeave`` and
``hysteresis`` per report configuration, which the report-episode analysis of
the revision needs (bravo, C7).

The identifiers are therefore *not* scoped to the message that carries them
(the v1 manuscript wording): they persist in VarMeasConfig until modified or
removed by later signalling. v1 fixed a union-of-fragments bug; that is a bug
fix, not a contribution, and the revised manuscript says so.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from ..utils import get_logger

LOG = get_logger("hoproj.config_v2")

TTT_MS = {f"ms{v}": v for v in (0, 40, 64, 80, 100, 128, 160, 256, 320, 480, 512,
                                640, 1024, 1280, 2560, 5120)}
RI_MS = {f"ms{v}": v for v in (120, 240, 480, 640, 1024, 2048, 5120, 10240)}
RI_MS.update({"min1": 60000, "min6": 360000, "min12": 720000, "min30": 1800000,
              "min60": 3600000})

_RECORD = re.compile(r"\n(?=\d{2}:\d{2}:\d{2}\.\d+\t)")
_PC_TS = re.compile(r"PC Timestamp:\s*\[\s*(\d{4})\s+(\w{3})\s+(\d{1,2})\s+"
                    r"(\d{2}:\d{2}:\d{2}\.\d+)\s*\]")
_REPORT_CFG = re.compile(
    r"reportConfigId\s+(\d+)\s*,\s*reportConfig reportConfig(EUTRA|InterRAT)\s*:(.*?)"
    r"(?=reportConfigId\s+\d+\s*,\s*reportConfig|measIdToAddModList|measIdToRemoveList|"
    r"quantityConfig|measGapConfig|s-Measure|$)", re.S)
_MEAS_ID = re.compile(r"measId\s+(\d+)\s*,\s*measObjectId\s+(\d+)\s*,\s*reportConfigId\s+(\d+)")
_MEAS_OBJ = re.compile(r"measObjectId\s+(\d+)\s*,\s*measObject measObjectEUTRA\s*:\s*"
                       r"carrierFreq\s+(\d+)", re.S)
_LIST = r"{name}\s*\n((?:\s*\d+\s*,?\s*\n)+)"
_MCI = re.compile(r"mobilityControlInfo.*?targetPhysCellId\s+(\d+)(.*?)t304", re.S)


def _int_list(name: str, body: str) -> list[int]:
    m = re.search(_LIST.format(name=re.escape(name)), body)
    return [int(x) for x in re.findall(r"\d+", m.group(1))] if m else []


def _report_configs(body: str) -> dict[int, dict]:
    out = {}
    for cid, kind, cfg in _REPORT_CFG.findall(body):
        ev = re.search(r"eventId\s+event(A\d|B\d)[\w-]*\s*:", cfg)
        periodic = re.search(r"triggerType\s+periodical", cfg)
        e = {"event": ev.group(1) if ev else ("periodical" if periodic else kind),
             "a3_offset_db": np.nan, "hysteresis_db": np.nan,
             "time_to_trigger_ms": np.nan, "report_interval_ms": np.nan,
             "report_amount": None, "report_on_leave": None,
             "threshold_raw": None}
        a3 = re.search(r"a3-Offset\s+(-?\d+)", cfg)
        if a3:
            e["a3_offset_db"] = int(a3.group(1)) * 0.5
        hy = re.search(r"hysteresis\s+(\d+)", cfg)
        if hy:
            e["hysteresis_db"] = int(hy.group(1)) * 0.5
        tt = re.search(r"timeToTrigger\s+(\w+)", cfg)
        if tt:
            e["time_to_trigger_ms"] = TTT_MS.get(tt.group(1), np.nan)
        ri = re.search(r"reportInterval\s+(\w+)", cfg)
        if ri:
            e["report_interval_ms"] = RI_MS.get(ri.group(1), np.nan)
        ra = re.search(r"reportAmount\s+(\w+)", cfg)
        if ra:
            e["report_amount"] = ra.group(1)
        ro = re.search(r"reportOnLeave\s+(\w+)", cfg)
        if ro:
            e["report_on_leave"] = ro.group(1) == "TRUE"
        th = re.search(r"threshold-RSRP\s+(-?\d+)", cfg)
        if th:
            e["threshold_raw"] = int(th.group(1))
        out[int(cid)] = e
    return out


@dataclass
class TimelineV2:
    times: np.ndarray                  # datetime64[ns], sorted
    states: list[dict]
    serving_carrier: list[int | None]
    n_updates: int
    n_removals: int
    n_swaps: int
    n_resets: int

    def at(self, t) -> dict:
        i = int(np.searchsorted(self.times, np.datetime64(t), side="right")) - 1
        return self.states[i] if i >= 0 else {"rc": {}, "mid": {}, "obj": {}}


def parse_timeline(path: str | Path) -> TimelineV2:
    txt = Path(path).read_text(errors="replace")
    rc: dict[int, dict] = {}
    mid: dict[int, tuple[int, int]] = {}
    obj: dict[int, int] = {}
    serving: int | None = None
    times, states, serv = [], [], []
    n_upd = n_rem = n_swap = n_reset = 0
    for rec in _RECORD.split(txt):
        head = rec.split("\n", 1)[0]
        ts = _PC_TS.search(rec)
        if not ts:
            continue
        y, mon, day, clock = ts.groups()
        t = pd.to_datetime(f"{y}-{mon}-{day} {clock}", format="%Y-%b-%d %H:%M:%S.%f")
        changed = False
        if "rrcConnectionRelease" in head or "rrcConnectionSetup " in head + " ":
            if "rrcConnectionSetupComplete" not in head and (rc or mid or obj):
                rc, mid, obj = {}, {}, {}
                n_reset += 1
                changed = True
        if "rrcConnectionReconfiguration" in head and "Complete" not in head:
            # 1) inter-frequency handover: swap measIds first (5.5.6.1)
            m = _MCI.search(rec)
            if m:
                dl = re.search(r"dl-CarrierFreq\s+(\d+)", m.group(2))
                target = int(dl.group(1)) if dl else serving
                if serving is not None and target is not None and target != serving:
                    src_objs = [o for o, f in obj.items() if f == serving]
                    tgt_objs = [o for o, f in obj.items() if f == target]
                    if src_objs and tgt_objs:
                        so, to = src_objs[0], tgt_objs[0]
                        for k, (o, c) in list(mid.items()):
                            if o == so:
                                mid[k] = (to, c)
                            elif o == to:
                                mid[k] = (so, c)
                        n_swap += 1
                    else:
                        # target carrier not configured: drop source-carrier links
                        for k, (o, c) in list(mid.items()):
                            if o in src_objs:
                                del mid[k]
                serving = target
                changed = True
            # 2) removals, then additions (5.5.2.1 order)
            if "measConfig" in rec:
                for x in _int_list("measIdToRemoveList", rec):
                    if mid.pop(x, None) is not None:
                        n_rem += 1
                for x in _int_list("measObjectToRemoveList", rec):
                    obj.pop(x, None)
                    for k in [k for k, (o, _) in mid.items() if o == x]:
                        del mid[k]
                        n_rem += 1
                for x in _int_list("reportConfigToRemoveList", rec):
                    rc.pop(x, None)
                    for k in [k for k, (_, c) in mid.items() if c == x]:
                        del mid[k]
                        n_rem += 1
                d_rc = _report_configs(rec)
                d_obj = {int(o): int(f) for o, f in _MEAS_OBJ.findall(rec)}
                d_mid = {int(a): (int(b), int(c)) for a, b, c in _MEAS_ID.findall(rec)}
                if d_rc or d_obj or d_mid:
                    rc.update(d_rc)
                    obj.update(d_obj)
                    mid.update(d_mid)
                    n_upd += 1
                changed = True
        if changed:
            times.append(t)
            states.append({"rc": dict(rc), "mid": dict(mid), "obj": dict(obj)})
            serv.append(serving)
    order = np.argsort(np.asarray(times, dtype="datetime64[ns]"), kind="stable")
    tl = TimelineV2(np.asarray(times, dtype="datetime64[ns]")[order],
                    [states[i] for i in order], [serv[i] for i in order],
                    n_upd, n_rem, n_swap, n_reset)
    LOG.info("timeline v2 %s: %d updates, %d measId removals, %d inter-freq swaps, "
             "%d resets", Path(path).name, n_upd, n_rem, n_swap, n_reset)
    return tl


def annotate_reports_v2(reports: pd.DataFrame, tl: TimelineV2) -> pd.DataFrame:
    rows = []
    for r in reports.itertuples(index=False):
        st = tl.at(r.t)
        link = st["mid"].get(int(r.meas_id)) if pd.notna(r.meas_id) else None
        e = {"report_config_id": np.nan, "meas_object_id": np.nan, "event_id": None,
             "a3_offset_db": np.nan, "hysteresis_db": np.nan, "time_to_trigger_ms": np.nan,
             "report_interval_ms": np.nan, "report_amount": None, "carrier_earfcn": np.nan,
             "resolved": link is not None}
        if link is not None:
            o, c = link
            cfg = st["rc"].get(c, {})
            e.update(report_config_id=c, meas_object_id=o, event_id=cfg.get("event"),
                     a3_offset_db=cfg.get("a3_offset_db", np.nan),
                     hysteresis_db=cfg.get("hysteresis_db", np.nan),
                     time_to_trigger_ms=cfg.get("time_to_trigger_ms", np.nan),
                     report_interval_ms=cfg.get("report_interval_ms", np.nan),
                     report_amount=cfg.get("report_amount"),
                     carrier_earfcn=st["obj"].get(o, np.nan))
        rows.append(e)
    ann = pd.DataFrame(rows, index=reports.index)
    base = reports[[c for c in reports.columns if c not in ann.columns]]
    return pd.concat([base, ann], axis=1)

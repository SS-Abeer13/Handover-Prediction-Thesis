"""Parse an XCAL/Accuver RRC signalling text export (R0/R8).

The drive-test CSV gives a regular sample grid but, in the captures seen so far,
leaves the neighbour columns empty. The signalling log carries what the CSV does
not: the UE's own MeasurementReports (neighbour PCI with quantised RSRP/RSRQ),
the network's handover commands, and the A3 parameters that triggered them.

Extracted streams
-----------------
``measurement_reports``  t, meas_id, serving rsrp/rsrq, and one row per reported
                         neighbour (pci, rsrp, rsrq), dequantised to dBm/dB.
``handovers``            t, target_pci, target_earfcn, t304, and the time and
                         latency of the matching ReconfigurationComplete. These
                         are *signalling-confirmed* handovers, not inferred
                         serving-cell changes.
``failures``             RRC re-establishment request/complete pairs - the only
                         defensible basis for an RLF/HOF label.
``meas_config``          a3-offset, hysteresis, time-to-trigger per reportConfig,
                         i.e. the network's actual mobility settings. These make
                         the A3 rule baseline a real comparator rather than a
                         guess, and let the thesis state the operating point it
                         is predicting against.

3GPP quantisation (TS 36.133): RSRP dBm = rsrpResult - 140, in [-140, -44];
RSRQ dB = rsrqResult / 2 - 19.5, in [-19.5, -3].
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

from ..utils import get_logger

LOG = get_logger("hoproj.signalling")

# a record starts with  HH:MM:SS.mmm <tab> seq <tab> dir <tab> channel <tab> rat <tab> name
HEADER = re.compile(
    r"^(?P<time>\d{2}:\d{2}:\d{2}\.\d{1,6})\t"
    r"(?P<seq>\d+)\t"
    r"(?P<dir>[-<>-]+)\t"
    r"(?P<channel>[^\t]*)\t"
    r"(?P<rat>[^\t]*)\t"
    r"(?P<name>.*)$"
)
TTT_MS = {
    "ms0": 0, "ms40": 40, "ms64": 64, "ms80": 80, "ms100": 100, "ms128": 128,
    "ms160": 160, "ms256": 256, "ms320": 320, "ms480": 480, "ms512": 512,
    "ms640": 640, "ms1024": 1024, "ms1280": 1280, "ms2560": 2560, "ms5120": 5120,
}


def rsrp_dbm(v) -> float:
    v = pd.to_numeric(v, errors="coerce")
    return np.where(pd.isna(v), np.nan, np.clip(v - 140.0, -141, -43))


def rsrq_db(v) -> float:
    v = pd.to_numeric(v, errors="coerce")
    return np.where(pd.isna(v), np.nan, np.clip(v / 2.0 - 19.5, -20, -2.5))


@dataclass
class SignallingLog:
    measurement_reports: pd.DataFrame = field(default_factory=pd.DataFrame)
    neighbours: pd.DataFrame = field(default_factory=pd.DataFrame)
    handovers: pd.DataFrame = field(default_factory=pd.DataFrame)
    failures: pd.DataFrame = field(default_factory=pd.DataFrame)
    meas_config: pd.DataFrame = field(default_factory=pd.DataFrame)
    message_counts: pd.Series = field(default_factory=pd.Series)
    date: pd.Timestamp | None = None

    def summary(self) -> dict:
        return {
            "measurement_reports": int(len(self.measurement_reports)),
            "reported_neighbour_rows": int(len(self.neighbours)),
            "unique_neighbour_pcis": int(self.neighbours["pci"].nunique()) if len(self.neighbours) else 0,
            "handover_commands": int(len(self.handovers)),
            "handovers_completed": int(self.handovers["completed"].sum()) if len(self.handovers) else 0,
            "reestablishments": int(len(self.failures)),
            "distinct_a3_offsets": sorted(self.meas_config["a3_offset_db"].dropna().unique().tolist())
                                   if len(self.meas_config) else [],
            "distinct_ttt_ms": sorted(self.meas_config["time_to_trigger_ms"].dropna().unique().tolist())
                               if len(self.meas_config) else [],
        }


def _records(path: Path):
    """Yield (timestamp string, message name, body lines) for every record."""
    cur_head, body = None, []
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            m = HEADER.match(line.rstrip("\n"))
            if m:
                if cur_head is not None:
                    yield cur_head, body
                cur_head, body = m.groupdict(), []
            elif cur_head is not None:
                body.append(line.rstrip("\n"))
    if cur_head is not None:
        yield cur_head, body


_PC_TS = re.compile(r"PC Timestamp:\s*\[\s*(\d{4})\s+(\w{3})\s+(\d{1,2})\s+(\d{2}:\d{2}:\d{2}\.\d+)\s*\]")


def _absolute_time(head: dict, body: list[str], fallback_date) -> pd.Timestamp:
    for line in body[:6]:
        m = _PC_TS.search(line)
        if m:
            year, mon, day, clock = m.groups()
            return pd.to_datetime(f"{year}-{mon}-{day} {clock}", format="%Y-%b-%d %H:%M:%S.%f")
    if fallback_date is None:
        return pd.NaT
    return pd.to_datetime(f"{fallback_date} {head['time']}")


def _parse_measurement_report(text: str) -> dict:
    out: dict = {"neighbours": []}
    m = re.search(r"measId\s+(\d+)", text)
    if m:
        out["meas_id"] = int(m.group(1))
    pcell = re.search(r"measResultPCell\s*.*?rsrpResult\s+(\d+)\s*,\s*rsrqResult\s+(-?\d+)",
                      text, re.S)
    if pcell:
        out["serving_rsrp_idx"] = int(pcell.group(1))
        out["serving_rsrq_idx"] = int(pcell.group(2))
    neigh_block = re.search(r"measResultNeighCells\s+measResultListEUTRA\s*:(.*?)(?:measResultServFreqList|$)",
                            text, re.S)
    if neigh_block:
        for pci, rsrp, rsrq in re.findall(
                r"physCellId\s+(\d+)\s*,\s*measResult\s*.*?rsrpResult\s+(\d+)\s*,\s*rsrqResult\s+(-?\d+)",
                neigh_block.group(1), re.S):
            out["neighbours"].append({"pci": int(pci), "rsrp_idx": int(rsrp), "rsrq_idx": int(rsrq),
                                      "src": "pcell_list"})
    # Carrier-aggregation reports carry a second neighbour source that the block
    # above deliberately stops short of: measResultServFreqList-r10 reports the
    # best neighbour ON THE SCELL CARRIER. It is a real, separately measured
    # candidate on another frequency and was previously discarded outright.
    for sf in re.finditer(
            r"measResultBestNeighCell-r10\s*(?:\n|.)*?physCellId-r10\s+(\d+)\s*,\s*"
            r"rsrpResultNCell-r10\s+(\d+)\s*,\s*rsrqResultNCell-r10\s+(-?\d+)", text):
        pci, rsrp, rsrq = int(sf.group(1)), int(sf.group(2)), int(sf.group(3))
        if not any(n["pci"] == pci for n in out["neighbours"]):
            out["neighbours"].append({"pci": pci, "rsrp_idx": rsrp, "rsrq_idx": rsrq,
                                      "src": "scell_best"})
    return out


def _parse_mobility_control(text: str) -> dict | None:
    m = re.search(r"mobilityControlInfo\s*(.*)", text, re.S)
    if not m:
        return None
    blk = m.group(1)[:4000]
    out: dict = {}
    t = re.search(r"targetPhysCellId\s+(\d+)", blk)
    if not t:
        return None
    out["target_pci"] = int(t.group(1))
    dl = re.search(r"dl-CarrierFreq\s+(\d+)", blk)
    if dl:
        out["target_earfcn"] = int(dl.group(1))
    t304 = re.search(r"t304\s+ms(\d+)", blk)
    if t304:
        out["t304_ms"] = int(t304.group(1))
    return out


def _parse_meas_config(text: str) -> list[dict]:
    rows = []
    for blk in re.findall(r"reportConfigId\s+(\d+)\s*,\s*reportConfig reportConfigEUTRA\s*:(.*?)"
                          r"(?=reportConfigId\s+\d+|measIdToAddModList|$)", text, re.S):
        cfg_id, body = blk
        row = {"report_config_id": int(cfg_id)}
        ev = re.search(r"eventId\s+event(\w+)\s*:", body)
        if ev:
            row["event"] = ev.group(1)
        a3 = re.search(r"a3-Offset\s+(-?\d+)", body)
        if a3:
            row["a3_offset_db"] = int(a3.group(1)) * 0.5   # TS 36.331: 0.5 dB steps
        hy = re.search(r"hysteresis\s+(\d+)", body)
        if hy:
            row["hysteresis_db"] = int(hy.group(1)) * 0.5
        tt = re.search(r"timeToTrigger\s+(\w+)", body)
        if tt:
            row["time_to_trigger_ms"] = TTT_MS.get(tt.group(1))
        thr = re.search(r"threshold(?:1|2)?\s+threshold-RSRP\s*:\s*(\d+)", body)
        if thr:
            row["threshold_rsrp_dbm"] = int(thr.group(1)) - 140
        rows.append(row)
    return rows


def parse_signalling(path: str | Path, date: str | None = None) -> SignallingLog:
    path = Path(path)
    LOG.info("parsing signalling log %s (%.1f MB)", path.name, path.stat().st_size / 1024**2)
    mr_rows, nb_rows, ho_rows, cfg_rows, fail_rows, complete_times, names = [], [], [], [], [], [], []
    fallback_date = date

    for head, body in _records(path):
        name = head["name"].strip()
        names.append(name)
        text = "\n".join(body)
        if fallback_date is None:
            m = _PC_TS.search(text)
            if m:
                fallback_date = f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
        t = _absolute_time(head, body, fallback_date)

        if "measurementReport" in name:
            parsed = _parse_measurement_report(text)
            idx = len(mr_rows)
            mr_rows.append({"t": t, "meas_id": parsed.get("meas_id"),
                            "serving_rsrp": float(rsrp_dbm(parsed.get("serving_rsrp_idx"))),
                            "serving_rsrq": float(rsrq_db(parsed.get("serving_rsrq_idx"))),
                            "n_neighbours": len(parsed["neighbours"])})
            for rank, nb in enumerate(sorted(parsed["neighbours"],
                                             key=lambda d: -d["rsrp_idx"]), start=1):
                nb_rows.append({"t": t, "report_idx": idx, "rank": rank, "pci": nb["pci"],
                                "rsrp": float(rsrp_dbm(nb["rsrp_idx"])),
                                "rsrq": float(rsrq_db(nb["rsrq_idx"]))})
        elif "rrcConnectionReconfigurationComplete" in name:
            complete_times.append(t)
        elif "rrcConnectionReconfiguration" in name:
            mc = _parse_mobility_control(text)
            if mc:
                ho_rows.append({"t": t, **mc})
            if "measConfig" in text:
                for row in _parse_meas_config(text):
                    cfg_rows.append({"t": t, **row})
        elif "rrcConnectionReestablishmentRequest" in name:
            cause = re.search(r"reestablishmentCause\s+(\w+)", text)
            pci = re.search(r"physCellId\s+(\d+)", text)
            fail_rows.append({"t": t, "cause": cause.group(1) if cause else None,
                              "source_pci": int(pci.group(1)) if pci else None})

    mr = pd.DataFrame(mr_rows).sort_values("t").reset_index(drop=True) if mr_rows else pd.DataFrame()
    nb = pd.DataFrame(nb_rows).sort_values("t").reset_index(drop=True) if nb_rows else pd.DataFrame()
    ho = pd.DataFrame(ho_rows).sort_values("t").reset_index(drop=True) if ho_rows else pd.DataFrame()
    cfg = pd.DataFrame(cfg_rows).drop_duplicates(
        subset=[c for c in ("report_config_id", "event", "a3_offset_db", "hysteresis_db",
                            "time_to_trigger_ms") if c in pd.DataFrame(cfg_rows).columns]
    ).reset_index(drop=True) if cfg_rows else pd.DataFrame()
    fail = pd.DataFrame(fail_rows).sort_values("t").reset_index(drop=True) if fail_rows else pd.DataFrame()

    # pair each handover command with the ReconfigurationComplete that follows it
    if len(ho) and complete_times:
        comp = pd.Series(sorted(pd.to_datetime(complete_times)))
        pos = np.searchsorted(comp.values, ho["t"].to_numpy("datetime64[ns]"), side="left")
        ok = pos < len(comp)
        ho["t_complete"] = pd.NaT
        ho.loc[ok, "t_complete"] = comp.to_numpy()[pos[ok]]
        ho["interrupt_ms"] = (pd.to_datetime(ho["t_complete"]) - ho["t"]).dt.total_seconds() * 1000
        # a completion more than t304 away is not this handover's completion
        limit = ho.get("t304_ms", pd.Series(1000, index=ho.index)).fillna(1000)
        ho["completed"] = ho["interrupt_ms"].between(0, limit * 1.5)
        ho.loc[~ho["completed"], ["t_complete", "interrupt_ms"]] = [pd.NaT, np.nan]
    elif len(ho):
        ho["t_complete"], ho["interrupt_ms"], ho["completed"] = pd.NaT, np.nan, False

    log = SignallingLog(mr, nb, ho, fail, cfg,
                        pd.Series(names).value_counts(),
                        pd.to_datetime(fallback_date) if fallback_date else None)
    LOG.info("signalling: %s", log.summary())
    return log


def to_sample_grid(log: SignallingLog, index: pd.DatetimeIndex, k: int = 3,
                   tolerance_s: float = 2.0) -> pd.DataFrame:
    """Project the reported neighbours onto a regular sample grid.

    Each grid point takes the most recent MeasurementReport within ``tolerance_s``.
    Reports are event-triggered and therefore sparse; ``mr_age_s`` records how
    stale the projection is so a model, or a QC rule, can discount it.
    """
    out = pd.DataFrame(index=index)
    for i in range(1, k + 1):
        out[f"nbr{i}_id"] = np.nan
        out[f"nbr{i}_rsrp"] = np.nan
        out[f"nbr{i}_rsrq"] = np.nan
    out["mr_serving_rsrp"] = np.nan
    out["mr_serving_rsrq"] = np.nan
    out["mr_age_s"] = np.nan
    out["nbr_age_s"] = np.nan
    if not len(log.measurement_reports):
        return out.reset_index(names="t")

    wide = []
    for idx, grp in log.neighbours.groupby("report_idx"):
        row = {"report_idx": idx}
        for _, r in grp.nsmallest(k, "rank").iterrows():
            row[f"nbr{int(r['rank'])}_id"] = r["pci"]
            row[f"nbr{int(r['rank'])}_rsrp"] = r["rsrp"]
            row[f"nbr{int(r['rank'])}_rsrq"] = r["rsrq"]
        wide.append(row)
    wide = pd.DataFrame(wide)
    mr = log.measurement_reports.reset_index(names="report_idx")
    mr = mr.merge(wide, on="report_idx", how="left").rename(
        columns={"serving_rsrp": "mr_serving_rsrp", "serving_rsrq": "mr_serving_rsrq"})
    mr = mr.sort_values("t")

    grid = pd.DataFrame({"t": index}).sort_values("t")
    # Serving-cell figures come from the most recent report of ANY kind.
    serving_cols = ["t", "report_idx", "mr_serving_rsrp", "mr_serving_rsrq"]
    merged = pd.merge_asof(grid, mr[[c for c in serving_cols if c in mr]], on="t",
                           direction="backward",
                           tolerance=pd.Timedelta(seconds=tolerance_s))
    # Neighbours come from the most recent report that actually CARRIED one.
    # Roughly 40% of reports are serving-only A1/A2 events; merging both streams
    # together let such a report mask a neighbour reading from a second earlier,
    # which is what held grid coverage near 28% when the logs support ~56%.
    nbr_cols = [f"nbr{i}_{s}" for i in range(1, k + 1) for s in ("id", "rsrp", "rsrq")]
    nbr_cols = [c for c in nbr_cols if c in mr]
    have_nbr = mr[[c for c in nbr_cols if c.endswith("_id")]].notna().any(axis=1)
    mr_n = mr.loc[have_nbr, ["t"] + nbr_cols].rename(columns={"t": "t_nbr"})
    mr_n["t"] = mr_n["t_nbr"]
    merged = pd.merge_asof(merged, mr_n, on="t", direction="backward",
                           tolerance=pd.Timedelta(seconds=tolerance_s))
    merged["mr_age_s"] = np.nan
    have = merged["report_idx"].notna()
    if have.any():
        ref = mr.set_index("report_idx")["t"]
        merged.loc[have, "mr_age_s"] = (
            merged.loc[have, "t"] - merged.loc[have, "report_idx"].map(ref)).dt.total_seconds()
    # Staleness of the NEIGHBOUR reading is a separate quantity and is the one a
    # model should discount on, so it is carried in its own column.
    merged["nbr_age_s"] = (merged["t"] - merged["t_nbr"]).dt.total_seconds()
    cols = ["t", "mr_serving_rsrp", "mr_serving_rsrq", "mr_age_s", "nbr_age_s"] + \
           [f"nbr{i}_{s}" for i in range(1, k + 1) for s in ("id", "rsrp", "rsrq")]
    return merged[[c for c in cols if c in merged]]


def handover_table(log: SignallingLog) -> pd.DataFrame:
    """Signalling-confirmed handover events, in the canonical event schema."""
    if not len(log.handovers):
        return pd.DataFrame(columns=["t", "from_pci", "to_pci", "ho_type", "source"])
    ho = log.handovers.copy()
    ho["to_pci"] = ho["target_pci"].astype(float)
    ho["from_pci"] = ho["to_pci"].shift()
    ho["ho_type"] = np.where(ho.get("completed", False), "signalling_confirmed", "commanded_incomplete")
    ho["source"] = "rrc_mobilityControlInfo"
    keep = ["t", "from_pci", "to_pci", "ho_type", "source", "t_complete", "interrupt_ms",
            "completed", "target_earfcn", "t304_ms"]
    return ho[[c for c in keep if c in ho]]

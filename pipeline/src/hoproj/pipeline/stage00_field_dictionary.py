"""Stage 00 (R0/R4): XCAL feasibility gate - build the field dictionary.

Reads a raw capture and reports, per variable: availability, native sampling
rate, timestamp resolution, missingness and export format.  That is exactly the
table section 10.4 of the proposal requires before any window length,
synchronisation tolerance or horizon is fixed.  It also states plainly which
tasks the capture can and cannot support.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from ..config import load_config, parse_cli_overrides, resolve_paths
from ..data.ingest import load_samples, load_signalling, merge_signalling
from ..eval.report import df_to_md, save_table, write_markdown_report
from ..utils import get_logger

LOG = get_logger("hoproj.stage00")

GROUPS = {
    "serving_rsrp": "RF", "serving_rsrq": "RF", "serving_sinr": "RF",
    "serving_rssi": "RF", "serving_cqi": "RF",
    "nbr1_rsrp": "Neighbour", "nbr2_rsrp": "Neighbour", "nbr3_rsrp": "Neighbour",
    "nbr1_id": "Neighbour", "nbr2_id": "Neighbour", "nbr3_id": "Neighbour",
    "serving_pci": "Cell", "serving_cell_name": "Cell", "serving_earfcn": "Cell",
    "serving_band": "Cell", "serving_enb": "Cell", "plmn": "Cell",
    "lat": "Mobility", "lon": "Mobility", "speed_kmh": "Mobility",
    "rrc_state": "Signalling",
    "dl_tp_kbps": "QoE", "ul_tp_kbps": "QoE", "phy_dl_kbps": "QoE",
    "phy_ul_kbps": "QoE", "rtt_ms": "QoE", "pkt_loss_pct": "QoE",
}

TASK_REQUIREMENTS = {
    "multi-horizon handover forecasting": ["serving_rsrp", "serving_pci"],
    "candidate-neighbour target ranking": ["nbr1_rsrp", "nbr1_id"],
    "QoE degradation prediction": ["dl_tp_kbps"],
    "QoE regression (RTT / loss)": ["rtt_ms", "pkt_loss_pct"],
    "mobility features": ["speed_kmh", "lat", "lon"],
    "signalling-confirmed handover / target cell": ["sig_handover_command", "sig_target_pci"],
    "handover failure / RLF labels": ["sig_reestablishment"],
    "A3 rule baseline with the network's own parameters": ["sig_a3_offset", "sig_time_to_trigger"],
}


def run(cfg, paths: dict) -> pd.DataFrame:
    samples = load_samples(cfg, paths["raw"])
    log = load_signalling(cfg, paths["raw"])
    if log is not None:
        samples = merge_signalling(samples, log, cfg)
    dt = samples["t"].diff().dt.total_seconds().dropna()
    period = float(dt.median()) if len(dt) else np.nan
    ts_res = _timestamp_resolution(samples["t"])

    rows = []
    for col, group in GROUPS.items():
        if col not in samples.columns:
            rows.append({"variable": col, "group": group, "availability": "absent",
                         "native_rate_hz": np.nan, "timestamp_resolution_s": ts_res,
                         "missing_frac": 1.0, "n_present": 0, "n_unique": 0,
                         "example": "", "export_format": "csv"})
            continue
        s = samples[col]
        present = int(s.notna().sum())
        miss = float(s.isna().mean())
        avail = "absent" if present == 0 else ("sparse" if miss > 0.5 else "available")
        rate = (1.0 / period) * (1 - miss) if period and np.isfinite(period) else np.nan
        rows.append({
            "variable": col, "group": group, "availability": avail,
            "native_rate_hz": round(rate, 3) if np.isfinite(rate) else np.nan,
            "timestamp_resolution_s": ts_res,
            "missing_frac": round(miss, 4), "n_present": present,
            "n_unique": int(s.nunique(dropna=True)),
            "example": "" if present == 0 else str(s.dropna().iloc[0])[:24],
            "export_format": "csv",
        })
    # variables that only the signalling log can supply
    if log is not None:
        span_s = max((samples["t"].max() - samples["t"].min()).total_seconds(), 1.0)
        sig = log.summary()
        extra = [
            ("sig_measurement_report", "Signalling", sig["measurement_reports"]),
            ("sig_neighbour_measurement", "Signalling", sig["reported_neighbour_rows"]),
            ("sig_handover_command", "Signalling", sig["handover_commands"]),
            ("sig_target_pci", "Signalling", sig["handover_commands"]),
            ("sig_handover_completed", "Signalling", sig["handovers_completed"]),
            ("sig_reestablishment", "Signalling", sig["reestablishments"]),
            ("sig_a3_offset", "Signalling", len(sig["distinct_a3_offsets"])),
            ("sig_time_to_trigger", "Signalling", len(sig["distinct_ttt_ms"])),
        ]
        for name, group, count in extra:
            rows.append({
                "variable": name, "group": group,
                "availability": "absent" if count == 0 else ("sparse" if count < 10 else "available"),
                "native_rate_hz": round(count / span_s, 4),
                "timestamp_resolution_s": 0.001,
                "missing_frac": 0.0 if count else 1.0,
                "n_present": int(count), "n_unique": int(count),
                "example": "", "export_format": "rrc text log",
            })
    table = pd.DataFrame(rows).sort_values(["group", "variable"]).reset_index(drop=True)

    feas = []
    for task, needed in TASK_REQUIREMENTS.items():
        status = []
        for col in needed:
            row = table.loc[table["variable"] == col]
            status.append(row["availability"].iloc[0] if len(row) else "absent")
        verdict = ("supported" if all(s == "available" for s in status)
                   else "degraded" if any(s in ("available", "sparse") for s in status)
                   else "NOT supported")
        feas.append({"task": task, "requires": ", ".join(needed),
                     "field_status": ", ".join(status), "verdict": verdict})
    feasibility = pd.DataFrame(feas)

    reports = paths["reports"]
    save_table(table, reports, "xcal_field_dictionary")
    save_table(feasibility, reports, "xcal_feasibility_gate")
    write_markdown_report([
        ("Capture", "\n".join([
            f"- rows: {len(samples)}",
            f"- span: {samples['t'].min()} to {samples['t'].max()}",
            f"- median sample period: {period:.3f} s ({1/period:.2f} Hz)" if period else "- irregular",
            f"- timestamp resolution: {ts_res} s",
            f"- shortest labelable horizon at this rate: {period:.3f} s" if period else "",
        ])),
        ("Field dictionary", df_to_md(table, 80)),
        ("Signalling log", "\n".join(f"- **{k}**: {v}" for k, v in log.summary().items())
         if log is not None else "_no signalling export paired with this capture_"),
        ("What this capture can support", df_to_md(feasibility)),
        ("Gate", "Do not finalise window length, synchronisation tolerance or forecast "
                 "horizons until the fields above are confirmed. Any task marked "
                 "'NOT supported' must be dropped from the protocol or the logging "
                 "configuration changed before the main campaign."),
    ], reports / "00_field_dictionary.md", "XCAL field dictionary and feasibility gate (R0)")
    LOG.info("field dictionary written; verdicts: %s",
             feasibility.set_index("task")["verdict"].to_dict())
    return table


def _timestamp_resolution(t: pd.Series) -> float:
    frac = (t.astype("int64") % 1_000_000_000).to_numpy()
    if (frac == 0).all():
        return 1.0
    nz = frac[frac != 0]
    return float(np.gcd.reduce(nz) / 1e9) if len(nz) else 1.0


def main(argv=None):
    ap = argparse.ArgumentParser(description="Stage 00: XCAL field dictionary / feasibility gate")
    ap.add_argument("--config", default="base.yaml")
    ap.add_argument("--adapter", default="xcal_wide")
    ap.add_argument("--root", default=None)
    ap.add_argument("--set", dest="overrides", nargs="*", default=[])
    args = ap.parse_args(argv)
    cfg = load_config(args.config, adapter=args.adapter,
                      overrides=parse_cli_overrides(args.overrides))
    return run(cfg, resolve_paths(cfg, args.root))


if __name__ == "__main__":
    main()

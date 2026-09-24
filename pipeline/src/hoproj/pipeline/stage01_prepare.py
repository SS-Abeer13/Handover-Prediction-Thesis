"""Stage 01 (R7-R10): raw capture -> processed drives, labels, features, characterisation."""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from ..config import Config, load_config, parse_cli_overrides, resolve_paths
from ..data import characterise, ingest, labels as L, qc, segment
from ..data.splits import make_splits
from ..eval.report import df_to_md, save_table, write_markdown_report
from ..utils import (environment_manifest, get_logger, set_seed, timed, write_json,
                     write_parquet)

LOG = get_logger("hoproj.stage01")


def run(cfg: Config, paths: dict) -> dict:
    set_seed(int(cfg.get_path("project.seed", 0)))
    raw, interim, processed = paths["raw"], paths["interim"], paths["processed"]

    with timed("ingest"):
        samples, events = ingest.ingest(cfg, raw)

    with timed("route assignment + drive segmentation"):
        samples = segment.assign_routes(samples, events, cfg)
        samples = segment.segment_drives(samples, cfg)
        drives = segment.drive_table(samples)

    with timed("quality control"):
        qc_tbl = qc.drive_quality(samples, drives, cfg)
        samples = qc.apply_qc(samples, qc_tbl)
        drives = drives[drives["drive_id"].isin(set(samples["drive_id"]))].reset_index(drop=True)

    with timed("handover events + labels"):
        ho = L.handover_events(samples, events, cfg)
        ho = ho[ho["drive_id"].isin(set(samples["drive_id"]))].reset_index(drop=True)
        # QoE thresholds must come from TRAINING drives only -> build the splits first
        splits = make_splits(drives, cfg)
        train_drives = set(splits["grouped_drive"].train)
        qoe_th = L.fit_qoe_thresholds(samples[samples["drive_id"].isin(train_drives)], cfg) \
            if cfg.get_path("tasks.qoe.enabled", False) or "qoe" in cfg.get_path("features.blocks", []) else {}
        lab = L.build_labels(samples, ho, cfg, qoe_th or None)

    with timed("feature construction"):
        feats = features_frame = None
        from ..data.features import build_features
        features_frame = build_features(samples, lab, cfg)
        feats = features_frame

    # align labels to the feature row order (features are sorted by drive then time)
    key = ["drive_id", "t"]
    lab_aligned = (feats[key].merge(lab, on=key, how="left", validate="one_to_one")
                   .reset_index(drop=True))

    with timed("characterisation"):
        summary = characterise.dataset_summary(samples, drives, ho, lab, cfg)
        ext = cfg.get_path("splits.external_route")
        dev_mask = (feats["route_id"] != ext).to_numpy()
        ext_mask = (feats["route_id"] == ext).to_numpy()
        shift = characterise.shift_report(feats, feats.attrs["feature_names"], dev_mask, ext_mask) \
            if ext_mask.any() else pd.DataFrame()
        overlap = characterise.cell_overlap(samples, dev_mask, ext_mask) if ext_mask.any() else {}

    # ------------------------------------------------------------------ persist
    out = {}
    out["samples"] = str(write_parquet(samples, interim / "samples.parquet"))
    out["drives"] = str(write_parquet(drives, processed / "drives.parquet"))
    out["qc"] = str(write_parquet(qc_tbl, processed / "qc_report.parquet"))
    out["handovers"] = str(write_parquet(ho, processed / "handovers.parquet"))
    out["labels"] = str(write_parquet(lab_aligned, processed / "labels.parquet"))
    out["features"] = str(write_parquet(feats, processed / "features.parquet"))
    write_json({"feature_block": feats.attrs["feature_block"],
                "feature_names": feats.attrs["feature_names"]},
               processed / "feature_meta.json")
    write_json({k: v.as_dict() for k, v in splits.items()}, processed / "splits.json")
    write_json({"summary": summary, "cell_overlap": overlap, "qoe_thresholds": qoe_th,
                "config_fingerprint": cfg.fingerprint, "environment": environment_manifest()},
               processed / "dataset_summary.json")
    cfg.dump(processed / "frozen_config.yaml")

    reports = paths["reports"]
    save_table(pd.DataFrame(summary["per_route"]), reports, "dataset_per_route")
    save_table(qc_tbl.drop(columns=[c for c in ("t_start", "t_end") if c in qc_tbl]),
               reports, "qc_per_drive")
    prev = pd.DataFrame([{"horizon": k, **v} for k, v in summary["label_prevalence"].items()])
    save_table(prev, reports, "label_prevalence")
    if len(shift):
        save_table(shift.head(40), reports, "distribution_shift_dev_vs_external")

    write_markdown_report(
        [
            ("Capture summary", "\n".join(
                f"- **{k}**: {v}" for k, v in summary.items()
                if k not in ("per_route", "label_prevalence", "top_missing_fields", "dates"))),
            ("Per route", df_to_md(pd.DataFrame(summary["per_route"]))),
            ("Multi-horizon label prevalence", df_to_md(prev)),
            ("Quality control", df_to_md(
                qc_tbl.groupby(["qc_pass"]).size().rename("drives").reset_index())),
            ("Cell overlap, development vs external route",
             "\n".join(f"- **{k}**: {v}" for k, v in overlap.items()) or "_no external route present_"),
            ("Largest distribution shifts (dev vs external)", df_to_md(shift.head(15))
             if len(shift) else "_no external route present_"),
            ("Missingness (top fields)", "\n".join(
                f"- `{k}`: {v:.3f}" for k, v in summary["top_missing_fields"].items()) or "_none_"),
        ],
        reports / "01_dataset_characterisation.md",
        "Dataset characterisation (R10)")
    LOG.info("stage 01 complete: %s", {k: Path(v).name for k, v in out.items()})
    return out


def main(argv=None) -> dict:
    ap = argparse.ArgumentParser(description="Stage 01: prepare the modelling dataset")
    ap.add_argument("--config", default="base.yaml")
    ap.add_argument("--adapter", default=None)
    ap.add_argument("--root", default=None)
    ap.add_argument("--set", dest="overrides", nargs="*", default=[])
    args = ap.parse_args(argv)
    cfg = load_config(args.config, adapter=args.adapter,
                      overrides=parse_cli_overrides(args.overrides))
    return run(cfg, resolve_paths(cfg, args.root))


if __name__ == "__main__":
    main()

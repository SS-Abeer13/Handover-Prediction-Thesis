"""Stage 12 - materialise the pooled XCAL signalling captures as THE dataset.

Why this stage exists
---------------------
Until now the benchmark tables (stage02: the seven-model comparison, the
leakage study, the feature ablation, the uncertainty tables) were produced on
the curated 6-8 Sept export, whose handover ground truth is *derived* from
serving-cell transitions in the sample grid. Everything published since - the
hazard reformulation, the Hawkes fit, conformal risk control, the benefit
envelope, the A3 mechanism - was computed on the XCAL 10/12/13 Sept captures,
whose handover ground truth comes from RRC signalling and is attributed to the
exact deployed A3 rule.

Two datasets, two label definitions, two sets of numbers for the same model.
This stage removes that split: it writes the pooled XCAL captures into
``data/processed_xcal`` in exactly the layout stage01 produces, so stage02,
stage03 and stage05 run against it unchanged.

What is deliberately different from stage01
-------------------------------------------
* Drive ids are prefixed with the capture tag. Without this, stage06's
  per-capture ``drive_id`` naming collides across captures and grouped splits
  leak (observed once: pooled AUROC 0.994).
* The ``qoe`` feature block is not built. The XCAL exports carry PHY
  throughput but not the application-layer RTT/loss columns the QoE rules
  need, so the feature set is ``rf_mob_hist`` rather than ``rf_mob_hist_qoe``.
* ``labels.allow_subperiod_horizons`` is on: signalling handovers carry
  millisecond timestamps (verified: 100% of events), so the 0.5 s horizon is
  labelable on a 1 Hz sample grid. The event clock, not the sample clock, is
  what bounds the horizon from below.
* There is no locked external route in these captures. External validation is
  carried by stage08 (the independent public Mendeley dataset) instead, and
  the ``external_route`` condition is absent from the emitted splits.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from ..config import Config, deep_merge, load_config, resolve_paths
from ..data import ingest, qc, segment
from ..data import labels as L
from ..data.features import build_features
from ..data.splits import Split
from ..data.config_regime import (annotate_reports, attribute_handovers, parse_maps,
                                  regime_to_samples)
from ..data.signalling import parse_signalling
from ..eval.report import df_to_md, save_table, write_markdown_report
from ..utils import (environment_manifest, get_logger, set_seed, timed, write_json,
                     write_parquet)

LOG = get_logger("hoproj.stage12")

BLOCKS = ["rf", "mobility", "history"]

CAPTURES = [
    ("XCAL10Sept", "sept10/data/raw", "test 10 sept-M1.csv", "test_10_sept_signalling.txt"),
    ("XCAL12Sept", "sept12/data/raw", "test 12 sept.csv", "test 12 sept signalling.txt"),
    ("XCAL13Sept", "sept13/data/raw", "test 13 sept.csv", "test 13 sept signalling.txt"),
    # 15 Sept: Uttara -> Gazipur highway corridor. Added 15 Sept 2026; this is the
    # first capture outside the urban corridor and the first at highway speed.
    ("XCAL15Sept", "sept15/data/raw", "test 15 sept.csv", "test 15 sept signalling.txt"),
]

HORIZONS = [0.5, 1.0, 2.0, 3.0, 5.0]

CONFIG_FEATURES = ["a3_offset_db", "hysteresis_db", "time_to_trigger_ms", "carrier_earfcn"]


def capture_config(csv: str, sig: str, horizons: list[float]) -> Config:
    ov = {
        "data": {"sources": {"samples": csv, "signalling": sig}},
        "features": {"blocks": BLOCKS, "regime": "topology_agnostic"},
        "segmentation": {"method": "fixed_duration", "fixed_duration_s": 180,
                         "route_from": "config"},
        "qc": {"min_drive_duration_s": 60, "min_drive_samples": 60},
        "labels": {"horizons_s": list(horizons), "allow_subperiod_horizons": True},
        "splits": {"external_route": None},
    }
    return Config(deep_merge(load_config("base.yaml", adapter="xcal_signalling"), ov))


def prepare_capture(tag: str, raw: str, csv: str, sig: str, horizons: list[float]) -> dict:
    cfg = capture_config(csv, sig, horizons)
    rawp = Path(raw)
    with timed(f"prepare {tag}"):
        samples, events = ingest.ingest(cfg, rawp)
        maps = parse_maps(rawp / sig)
        log = parse_signalling(rawp / sig)
        reports = annotate_reports(log.measurement_reports, maps)

        samples = regime_to_samples(samples, reports)
        samples = segment.assign_routes(samples, events, cfg)
        samples = segment.segment_drives(samples, cfg)
        # Drive ids must be globally unique or grouped splits silently leak.
        samples["drive_id"] = tag + "__" + samples["drive_id"].astype(str)
        drives = segment.drive_table(samples)
        samples = qc.apply_qc(samples, qc.drive_quality(samples, drives, cfg))
        drives = drives[drives["drive_id"].isin(set(samples["drive_id"]))].reset_index(drop=True)

        ho = L.handover_events(samples, events, cfg)
        ho = ho[ho["drive_id"].isin(set(samples["drive_id"]))].reset_index(drop=True)
        ho = attribute_handovers(ho, reports)
        lab = L.build_labels(samples, ho, cfg)
        feats = build_features(samples, lab, cfg)
        lab = (feats[["drive_id", "t"]].merge(lab, on=["drive_id", "t"], how="left")
               .reset_index(drop=True))
        idx = pd.MultiIndex.from_frame(feats[["drive_id", "t"]])
        src = samples.set_index(["drive_id", "t"])
        for c in CONFIG_FEATURES:
            if c in src.columns:
                feats[c] = src.reindex(idx)[c].to_numpy()
        for frame in (feats, lab, ho, drives):
            frame["capture"] = tag
    LOG.info("%s: %d samples, %d drives, %d handovers", tag, len(feats),
             drives["drive_id"].nunique(), len(ho))
    return {"features": feats, "labels": lab, "ho": ho, "drives": drives, "cfg": cfg}


def pooled_splits(drives: pd.DataFrame, seed: int,
                  fractions: dict) -> dict[str, Split]:
    """Whole-drive partitions, stratified by capture so each split sees all three.

    The external-route condition of stage01 has no counterpart here (these
    captures share one corridor), so only the grouped and the leakage-control
    conditions are emitted.
    """
    rng = np.random.default_rng(seed)
    parts: dict[str, list[str]] = {k: [] for k in ("train", "val", "calib", "test")}
    for _, grp in drives.groupby("capture", dropna=False):
        ids = grp["drive_id"].tolist()
        rng.shuffle(ids)
        n = len(ids)
        n_val = max(1, int(round(fractions["val"] * n)))
        n_cal = max(1, int(round(fractions["calib"] * n)))
        n_tst = max(1, int(round(fractions["test"] * n)))
        parts["val"] += ids[:n_val]
        parts["calib"] += ids[n_val:n_val + n_cal]
        parts["test"] += ids[n_val + n_cal:n_val + n_cal + n_tst]
        parts["train"] += ids[n_val + n_cal + n_tst:]

    allids = drives["drive_id"].tolist()
    return {
        "grouped_drive": Split(name="grouped_drive", condition="grouped_drive",
                               note="Whole XCAL drives, stratified by capture.",
                               **parts),
        "random_row": Split(name="random_row", condition="random_row",
                            train=allids, val=allids, calib=allids, test=allids,
                            note="Rows shuffled at sample level; LEAKAGE CONTROL ONLY."),
    }


def run(root: str | None, horizons: list[float], seed: int) -> dict:
    cfg0 = capture_config(CAPTURES[0][2], CAPTURES[0][3], horizons)
    cfg0.set_path("project.paths.processed", "data/processed_xcal")
    cfg0.set_path("project.paths.interim", "data/interim_xcal")
    cfg0.set_path("project.paths.reports", "reports_xcal")
    cfg0.set_path("project.paths.artifacts", "artifacts_xcal")
    paths = resolve_paths(cfg0, root)
    set_seed(seed)

    prepared = [prepare_capture(tag, raw, csv, sig, horizons)
                for tag, raw, csv, sig in CAPTURES]

    feats = pd.concat([p["features"] for p in prepared], ignore_index=True)
    # pd.concat drops DataFrame.attrs, which carries the feature-block registry
    # every downstream select_blocks call depends on.
    feats.attrs = dict(prepared[0]["features"].attrs)
    lab = pd.concat([p["labels"] for p in prepared], ignore_index=True)
    ho = pd.concat([p["ho"] for p in prepared], ignore_index=True)
    drives = pd.concat([p["drives"] for p in prepared], ignore_index=True)

    order = feats.sort_values(["drive_id", "t"]).index
    feats = feats.loc[order].reset_index(drop=True)
    lab = lab.loc[order].reset_index(drop=True)
    assert (feats["drive_id"].to_numpy() == lab["drive_id"].to_numpy()).all()

    tags = [L._htag(h) for h in horizons]
    prev = pd.DataFrame([{
        "horizon_s": h,
        "n_labelable": int(lab[f"m_ho_{t}"].sum()),
        "positive_rate": float(lab.loc[lab[f"m_ho_{t}"] == 1, f"y_ho_{t}"].mean()),
    } for h, t in zip(horizons, tags)])
    LOG.info("pooled prevalence:\n%s", prev.to_string(index=False))

    fractions = cfg0.get_path("splits.dev_fractions")
    splits = pooled_splits(drives, seed, fractions)
    for s in splits.values():
        LOG.info("split %-14s train=%d val=%d calib=%d test=%d drives", s.name,
                 len(s.train), len(s.val), len(s.calib), len(s.test))

    processed = paths["processed"]
    write_parquet(drives, processed / "drives.parquet")
    write_parquet(ho, processed / "handovers.parquet")
    write_parquet(lab, processed / "labels.parquet")
    write_parquet(feats, processed / "features.parquet")
    write_json({"feature_block": feats.attrs["feature_block"],
                "feature_names": feats.attrs["feature_names"]},
               processed / "feature_meta.json")
    write_json({k: v.as_dict() for k, v in splits.items()}, processed / "splits.json")
    summary = {
        "captures": [c[0] for c in CAPTURES],
        "n_samples": int(len(feats)),
        "n_drives": int(drives["drive_id"].nunique()),
        "n_handovers": int(len(ho)),
        "horizons_s": horizons,
        "feature_block": "rf+mobility+history (no qoe: XCAL carries no RTT/loss columns)",
        "n_features": len(feats.attrs["feature_names"]),
        "label_source": "RRC signalling (handover commands), ms timestamps",
        "per_capture": {p["drives"]["capture"].iloc[0]: {
            "samples": int(len(p["features"])),
            "drives": int(p["drives"]["drive_id"].nunique()),
            "handovers": int(len(p["ho"]))} for p in prepared},
        "prevalence": prev.to_dict("records"),
        "environment": environment_manifest(),
    }
    write_json(summary, processed / "dataset_summary.json")
    cfg0.dump(processed / "frozen_config.yaml")

    save_table(prev, paths["reports"], "xcal_label_prevalence")
    save_table(pd.DataFrame(
        [{"capture": k, **v} for k, v in summary["per_capture"].items()]),
        paths["reports"], "xcal_capture_summary")
    write_markdown_report(
        [("What this dataset is",
          "Pooled XCAL 10/12/13/15 Sept captures with RRC-signalling handover ground "
          "truth. This replaces the curated 6-8 Sept export as the benchmark "
          "dataset so that every table in the manuscript describes one dataset."),
         ("Per capture", df_to_md(pd.DataFrame(
             [{"capture": k, **v} for k, v in summary["per_capture"].items()]))),
         ("Label prevalence", df_to_md(prev)),
         ("Splits", "\n".join(
             f"- **{s.name}**: train {len(s.train)} / val {len(s.val)} / "
             f"calib {len(s.calib)} / test {len(s.test)} drives"
             for s in splits.values()))],
        paths["reports"] / "12_xcal_dataset.md",
        "XCAL pooled dataset (stage 12)")
    return summary


def main(argv=None):
    ap = argparse.ArgumentParser(description="Stage 12: pooled XCAL dataset for stage02")
    ap.add_argument("--root", default=None)
    ap.add_argument("--horizons", nargs="*", type=float, default=HORIZONS)
    ap.add_argument("--seed", type=int, default=1337)
    a = ap.parse_args(argv)
    return run(a.root, list(a.horizons), a.seed)


if __name__ == "__main__":
    main()

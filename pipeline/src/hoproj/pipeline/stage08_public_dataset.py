"""Stage 08 - external validation on the public IUT/Mendeley LTE handover dataset.

`Drive-Test-Based LTE Handover Dataset for Cellular Mobility Studies in Urban
Bangladesh` (Shafi, Istiaque, Sowad, Kawser; Mendeley Data 10.17632/n2pvmtyn2j.1)
was collected on the same operator, in the same city, with the same XCAL-M
licence - but on a different route, by different people, two years earlier. It is
the only independent, publicly citable holdout available to this project.

Why the domain is built from the SIGNALLING rather than the published CSVs:

* the `Parent Dataset` CSVs are event-triggered rows, not a periodic grid
  (0.24 rows/s over 45 min), so they cannot support a fixed-horizon forecast;
* they carry no GPS, no speed and no date - only a time-of-day string - so no
  mobility feature and no absolute timeline can be built from them;
* RSRP/RSRQ are stored as raw 3GPP indices, undocumented in the README;
* the `Processed Dataset` CSVs have Excel-mangled timestamps (`33:33.712`) and
  re-encoded cell IDs.

The `Measurement Reports` text exports, by contrast, are byte-for-byte the same
XCAL RRC format as our own captures, carry absolute `PC Timestamp`s, and yield
signalling-confirmed handovers with target cells. So this stage reconstructs the
sample grid from the signalling itself and evaluates on the RF + cell-history
blocks only - mobility features are unavailable by construction on this dataset,
which is itself the finding worth reporting.
"""
from __future__ import annotations

import argparse
import glob
import os
from pathlib import Path

import numpy as np
import pandas as pd

from ..config import Config, deep_merge, load_config, resolve_paths
from ..data import qc, segment
from ..data import labels as L
from ..data.features import build_features
from ..data.signalling import handover_table, parse_signalling, to_sample_grid
from ..utils import get_logger, timed, write_json
from .stage06_cross_capture import Domain, prepare, run

LOG = get_logger("hoproj.stage08")

BLOCKS = ["rf", "history"]          # no GPS/speed in the public dataset
PERIOD_S = 1.0


def _session_frame(path: str, tolerance_s: float = 3.0) -> tuple[pd.DataFrame, pd.DataFrame]:
    """One capture file -> (regular sample grid, handover events)."""
    log = parse_signalling(Path(path))
    mr = log.measurement_reports
    if not len(mr):
        return pd.DataFrame(), pd.DataFrame()
    t0, t1 = mr["t"].min().floor("s"), mr["t"].max().ceil("s")
    idx = pd.date_range(t0, t1, freq=f"{int(PERIOD_S)}s")
    grid = to_sample_grid(log, idx, tolerance_s=tolerance_s)
    grid = grid.rename(columns={"mr_serving_rsrp": "serving_rsrp",
                                "mr_serving_rsrq": "serving_rsrq"})
    ho = handover_table(log)

    # Serving PCI is not carried in a MeasurementReport, but the handover chain
    # states it exactly from the first command onward: between two commands the
    # serving cell IS the previous target. Rows before the first command get a
    # distinct sentinel rather than a guess.
    grid["serving_pci"] = np.nan
    if len(ho):
        ho = ho.sort_values("t").reset_index(drop=True)
        pci = pd.Series(np.nan, index=grid.index)
        for _, e in ho.iterrows():
            pci[grid["t"] >= e["t"]] = e["to_pci"]
        grid["serving_pci"] = pci
    grid["serving_pci"] = grid["serving_pci"].fillna(-1.0)
    grid["serving_cell_name"] = grid["serving_pci"].astype(int).astype(str)
    for c in ("serving_rssi", "serving_sinr", "serving_cqi", "lat", "lon", "speed_kmh"):
        grid[c] = np.nan
    grid["is_interpolated"] = grid["serving_rsrp"].isna()
    grid["serving_rsrp"] = grid["serving_rsrp"].ffill(limit=5)
    grid["serving_rsrq"] = grid["serving_rsrq"].ffill(limit=5)
    return grid, ho


def build_domain(root: Path, name: str = "public IUT dataset",
                 tolerance_s: float = 3.0, max_gap_s: int = 10,
                 min_run_s: int = 60) -> Domain:
    files = sorted(glob.glob(str(root / "*" / "*.txt")))
    if not files:
        raise SystemExit(f"no measurement-report exports under {root}")
    ov = {"features": {"blocks": BLOCKS, "regime": "topology_agnostic"},
          "labels": {"handover": {"source": "signalling"},
                     "target_cell": {"require_candidate_match": False}},
          "segmentation": {"method": "fixed_duration", "fixed_duration_s": 300,
                           "route_from": "config"},
          # GPS is absent from this dataset by construction, so the GPS gate is
          # switched off here and nowhere else; every other QC rule still applies.
          "qc": {"min_drive_duration_s": 60, "min_drive_samples": 60,
                 "require_gps": False,
                 "core_fields": ["serving_rsrp", "serving_rsrq"]},
          "data": {"target_period_s": PERIOD_S}}
    cfg = Config(deep_merge(load_config("base.yaml", adapter="xcal_signalling"), ov))

    S, E = [], []
    for f in files:
        ds = os.path.basename(os.path.dirname(f)).replace("Measurement Reports_", "") \
                                                 .replace("Measurement Report_", "")
        tag = f"{ds}__{os.path.splitext(os.path.basename(f))[0]}"
        g, ho = _session_frame(f, tolerance_s)
        if not len(g) or len(g) < 60:
            LOG.info("skip %s (too short)", tag)
            continue
        g["_session"] = tag
        ho = ho.assign(_session=tag) if len(ho) else ho
        S.append(g)
        E.append(ho)
    samples = pd.concat(S, ignore_index=True).sort_values(["_session", "t"])
    events = pd.concat([e for e in E if len(e)], ignore_index=True)

    # every file is its own session; segment each into fixed-duration drives
    # Drives cannot be cut geometrically (no GPS) or by wall clock: the UE is in
    # RRC idle for most of these captures, so only 27% of grid seconds carry a
    # radio measurement at all. A drive here is therefore one contiguous
    # RRC-CONNECTED run - measurements no more than `max_gap_s` apart - which is
    # the only interval over which a fixed-horizon forecast is even defined.
    samples["route_id"] = samples["_session"]
    codes = {v: i for i, v in enumerate(sorted(samples["_session"].unique()))}
    samples["session_id"] = samples["_session"].map(codes)
    keep_parts = []
    for sess, g in samples.groupby("_session", sort=True):
        g = g.reset_index(drop=True)
        ok = g["serving_rsrp"].notna().to_numpy()
        idx = np.where(ok)[0]
        if not len(idx):
            continue
        cuts = np.where(np.diff(idx) > max_gap_s)[0]
        for k, part in enumerate(np.split(idx, cuts + 1)):
            lo, hi = part[0], part[-1]
            if hi - lo + 1 < min_run_s:
                continue
            seg = g.iloc[lo:hi + 1].copy()
            seg["drive_id"] = f"PUB__{sess}__r{k:02d}"
            keep_parts.append(seg)
    if not keep_parts:
        raise SystemExit("no RRC-connected run long enough to evaluate")
    samples = pd.concat(keep_parts, ignore_index=True).sort_values(["drive_id", "t"])
    samples["direction"] = "na"
    samples["drive_seq"] = samples.groupby("drive_id").cumcount()
    samples["t_in_drive_s"] = samples.groupby("drive_id")["t"].transform(
        lambda x: (x - x.min()).dt.total_seconds())
    samples["dist_in_drive_m"] = 0.0
    drives = segment.drive_table(samples)
    samples = qc.apply_qc(samples, qc.drive_quality(samples, drives, cfg))
    drives = drives[drives["drive_id"].isin(set(samples["drive_id"]))].reset_index(drop=True)

    ho = L.handover_events(samples, events, cfg)
    ho = ho[ho["drive_id"].isin(set(samples["drive_id"]))].reset_index(drop=True)
    lab = L.build_labels(samples, ho, cfg)
    feats = build_features(samples, lab, cfg)
    lab = (feats[["drive_id", "t"]].merge(lab, on=["drive_id", "t"], how="left")
           .reset_index(drop=True))
    LOG.info("%s: %d samples, %d drives, %d handovers", name,
             len(feats), drives["drive_id"].nunique(), len(ho))
    return Domain(name, feats, lab, ho, drives, L.usable_horizons(cfg), L.horizon_tags(cfg))


CAPTURES = [
    ("XCAL 10 Sept", "sept10/data/raw", "test 10 sept-M1.csv", "test_10_sept_signalling.txt"),
    ("XCAL 12 Sept", "sept12/data/raw", "test 12 sept.csv", "test 12 sept signalling.txt"),
    ("XCAL 13 Sept", "sept13/data/raw", "test 13 sept.csv", "test 13 sept signalling.txt"),
]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--public-root", required=True,
                    help="the 'Measurement Reports' directory of the public dataset")
    ap.add_argument("--models", nargs="+", default=["lgbm"])
    ap.add_argument("--epochs", type=int, default=25)
    ap.add_argument("--direction", default="both",
                    choices=["both", "ours_to_public", "public_to_ours"])
    a = ap.parse_args()

    cfg = Config(deep_merge(load_config("base.yaml", adapter="xcal_signalling"),
                            {"features": {"blocks": BLOCKS, "regime": "topology_agnostic"},
                             "training": {"epochs": a.epochs}}))
    paths = resolve_paths(cfg)

    pub = build_domain(Path(a.public_root))
    ours = [prepare(n, "xcal_signalling", Path(r),
                    {"samples": c, "signalling": s},
                    overrides={"features": {"blocks": BLOCKS}})
            for n, r, c, s in CAPTURES]
    # stage06.prepare names drives per capture, so the three captures produce
    # COLLIDING drive ids. Pooling them without a prefix makes one "drive" span
    # two captures, which puts the same rows on both sides of the grouped split.
    for d in ours:
        tag = d.name.replace(" ", "") + "__"
        for frame in (d.features, d.labels, d.ho, d.drives):
            if "drive_id" in frame:
                frame["drive_id"] = tag + frame["drive_id"].astype(str)

    # one pooled "ours" domain so the comparison is our whole campaign vs theirs.
    # pd.concat drops DataFrame.attrs, which is where the feature-block registry
    # lives, so it is copied back explicitly - without it select_blocks() silently
    # returns an empty feature list.
    pooled_feats = pd.concat([d.features for d in ours], ignore_index=True)
    pooled_feats.attrs = dict(ours[0].features.attrs)
    pooled = Domain("XCAL Sept 10-13 pooled",
                    pooled_feats,
                    pd.concat([d.labels for d in ours], ignore_index=True),
                    pd.concat([d.ho for d in ours], ignore_index=True),
                    pd.concat([d.drives for d in ours], ignore_index=True),
                    ours[0].horizons, ours[0].tags)

    fs = {"rf_history": []}
    pairs = {"ours_to_public": [(pooled, [pub])],
             "public_to_ours": [(pub, [pooled])]}
    pairs["both"] = pairs["ours_to_public"] + pairs["public_to_ours"]
    out = [run(src, tgts, cfg, a.models, fs, paths) for src, tgts in pairs[a.direction]]
    res = pd.concat(out, ignore_index=True)
    RPT_DIR = Path(paths["reports"]) / "tables"
    RPT_DIR.mkdir(parents=True, exist_ok=True)
    stem = f"public_dataset_transfer_{a.direction}"
    res.to_csv(RPT_DIR / f"{stem}.csv", index=False)
    (RPT_DIR / f"{stem}.md").write_text(res.to_markdown(index=False))
    write_json(Path(paths["artifacts"]["dir"] if isinstance(paths["artifacts"], dict) else paths["artifacts"]) / "public_dataset.json",
               {"public_drives": int(pub.drives["drive_id"].nunique()),
                "public_handovers": int(len(pub.ho)),
                "our_drives": int(pooled.drives["drive_id"].nunique()),
                "our_handovers": int(len(pooled.ho))})
    LOG.info("wrote %s", RPT_DIR / "public_dataset_transfer.csv")


if __name__ == "__main__":
    main()

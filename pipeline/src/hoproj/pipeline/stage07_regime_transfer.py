"""Stage 07 - configuration-regime transfer, the controlled shift experiment.

Several A3 profiles run concurrently on different carriers of the same network,
so a single drive contains handovers governed by different rules. Splitting the
data by *regime* rather than by campaign holds city, UE, driver, day, route and
even time-of-day fixed while the handover-control parameters vary. That is a far
cleaner shift experiment than comparing captures or operators.

Three questions:

``difficulty``  Is one regime intrinsically harder to predict than another, at
                matched prevalence? Reported as AUPRC lift, per regime, from a
                model trained on all regimes with drives held out.
``transfer``    Train on one regime, test on another. Grouped by drive on both
                sides, so no window is shared.
``conditioning``Does giving the model the measured A3 parameters as inputs
                recover any of the transfer loss? The same runs, with and
                without four configuration features.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from ..config import Config, deep_merge, load_config, resolve_paths
from ..data import ingest, qc, segment
from ..data import labels as L
from ..data.config_regime import (annotate_reports, attribute_handovers, parse_maps,
                                  regime_to_samples)
from ..data.features import build_features, select_blocks
from ..data.signalling import parse_signalling
from ..data.transforms import TabularTransform
from ..data.windows import build_window_index, materialise
from ..eval import metrics as MET
from ..eval import report as RPT
from ..eval import stats as ST
from ..models.dataset import SequenceDataset
from ..models.registry import build_model, model_kind
from ..utils import get_logger, set_seed, timed, write_json

LOG = get_logger("hoproj.stage07")

BLOCKS = ["rf", "mobility", "history"]
CONFIG_FEATURES = ["a3_offset_db", "hysteresis_db", "time_to_trigger_ms", "carrier_earfcn"]
CAPTURES = [
    ("10 Sept", "sept10/data/raw", "test 10 sept-M1.csv", "test_10_sept_signalling.txt"),
    ("12 Sept", "sept12/data/raw", "test 12 sept.csv", "test 12 sept signalling.txt"),
    ("13 Sept", "sept13/data/raw", "test 13 sept.csv", "test 13 sept signalling.txt"),
]


def build_pool(cfg_base: Config, min_events: int = 60) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """One pooled frame over every real capture, with the A3 regime on each row."""
    feats_all, labels_all, ho_all = [], [], []
    for name, raw, csv, sig in CAPTURES:
        ov = {"data": {"sources": {"samples": csv, "signalling": sig}},
              "features": {"blocks": BLOCKS, "regime": "topology_agnostic"},
              "segmentation": {"method": "fixed_duration", "fixed_duration_s": 180,
                               "route_from": "config"},
              "qc": {"min_drive_duration_s": 60, "min_drive_samples": 60}}
        cfg = Config(deep_merge(load_config("base.yaml", adapter="xcal_signalling"), ov))
        rawp = Path(raw)
        with timed(f"prepare {name}"):
            samples, events = ingest.ingest(cfg, rawp)
            log = parse_signalling(rawp / sig)
            maps = parse_maps(rawp / sig)
            reports = annotate_reports(log.measurement_reports, maps)

            samples = regime_to_samples(samples, reports)
            samples = segment.assign_routes(samples, events, cfg)
            samples = segment.segment_drives(samples, cfg)
            # drive ids must be unique across captures
            samples["drive_id"] = name.replace(" ", "") + "__" + samples["drive_id"].astype(str)
            drives = segment.drive_table(samples)
            samples = qc.apply_qc(samples, qc.drive_quality(samples, drives, cfg))

            ho = L.handover_events(samples, events, cfg)
            ho = ho[ho["drive_id"].isin(set(samples["drive_id"]))].reset_index(drop=True)
            ho = attribute_handovers(ho, reports)
            lab = L.build_labels(samples, ho, cfg)
            feats = build_features(samples, lab, cfg)
            lab = (feats[["drive_id", "t"]].merge(lab, on=["drive_id", "t"], how="left")
                   .reset_index(drop=True))
            # carry the configuration onto the feature frame
            for c in CONFIG_FEATURES:
                feats[c] = samples.set_index(["drive_id", "t"]).reindex(
                    pd.MultiIndex.from_frame(feats[["drive_id", "t"]]))[c].to_numpy()
            feats["capture"] = name
            ho["capture"] = name
        feats_all.append(feats)
        labels_all.append(lab)
        ho_all.append(ho)

    F = pd.concat(feats_all, ignore_index=True)
    Y = pd.concat(labels_all, ignore_index=True)
    H = pd.concat(ho_all, ignore_index=True)
    F.attrs["feature_block"] = feats_all[0].attrs["feature_block"]
    F.attrs["feature_names"] = feats_all[0].attrs["feature_names"]

    F["regime"] = _regime_key(F)
    H["regime"] = _regime_key(H)
    keep = H["regime"].value_counts()
    keep = set(keep[keep >= min_events].index) - {"unattributed"}
    LOG.info("regimes retained (>=%d handovers): %s", min_events, sorted(keep))
    LOG.info("pooled: %d samples, %d drives, %d handovers across %d captures",
             len(F), F["drive_id"].nunique(), len(H), F["capture"].nunique())
    return F, Y, H[H["regime"].isin(keep)].reset_index(drop=True)


def _regime_key(df: pd.DataFrame) -> pd.Series:
    a3, ttt = df.get("a3_offset_db"), df.get("time_to_trigger_ms")
    if a3 is None:
        return pd.Series(["unattributed"] * len(df), index=df.index)
    return pd.Series(np.where(pd.isna(a3), "unattributed",
                              [f"A3{a:+.0f}dB/TTT{int(t)}ms" if pd.notna(a) and pd.notna(t)
                               else "unattributed" for a, t in zip(a3, ttt)]),
                     index=df.index)


def _prep(F, Y, cfg, names, L_win, stride):
    wi = build_window_index(F, L_win, stride, 0.0,
                            F["is_interpolated"].to_numpy(bool) if "is_interpolated" in F else None)
    tags = L.horizon_tags(cfg)
    Ym = np.column_stack([Y[f"y_ho_{t}"].to_numpy(np.float32) for t in tags])
    Mm = np.column_stack([Y[f"m_ho_{t}"].to_numpy(np.float32) for t in tags])
    return wi, Ym, Mm


def run(cfg: Config, paths: dict, models=("lgbm", "gru"), seed: int = 1337) -> pd.DataFrame:
    F, Y, H = build_pool(cfg)
    horizons = L.usable_horizons(cfg)
    period = float(cfg.get_path("data.target_period_s") or 1.0)
    L_win = max(2, int(round(float(cfg.get_path("windows.length_s", 10.0)) / period)))
    stride = max(1, int(round(float(cfg.get_path("windows.stride_s", 1.0)) / period)))

    base_names = [n for n in select_blocks(F, BLOCKS) if n in F.columns]
    regimes = sorted(set(H["regime"]))
    wi, Ym, Mm = _prep(F, Y, cfg, base_names, L_win, stride)
    reg_rows = F["regime"].to_numpy()[wi.end_pos]
    drives_rows = F["drive_id"].to_numpy()[wi.end_pos]

    rows = []
    for use_config in (False, True):
        names = base_names + ([c for c in CONFIG_FEATURES if c in F.columns] if use_config else [])
        cond = "with A3 features" if use_config else "RF/mobility/history only"

        for src in regimes:
            src_rows = reg_rows == src
            if src_rows.sum() < 500:
                continue
            # hold out whole drives inside the source regime for validation
            # Hold out whole drives GLOBALLY, not just within the source regime, so
            # the held-out set can serve every target regime without sharing a drive
            # with training.
            rng = np.random.default_rng(seed)
            all_d = np.unique(drives_rows)
            rng.shuffle(all_d)
            n_val = max(2, int(round(0.30 * len(all_d))))
            val_d = set(all_d[:n_val].tolist())
            tr = src_rows & ~np.isin(drives_rows, list(val_d))
            va = src_rows & np.isin(drives_rows, list(val_d))
            if tr.sum() < 300 or va.sum() < 100:
                continue

            tf = TabularTransform(cfg.get_path("features.scaler", "robust"),
                                  clip_sigma=float(cfg.get_path("features.clip_sigma", 8.0)))
            tf.fit(F.loc[wi.end_pos[tr], names])
            X = tf.transform(F[names])
            T = materialise(X, wi)

            for model_name in models:
                set_seed(seed)
                kind = model_kind(model_name)
                with timed(f"{model_name} | train {src} | {cond}"):
                    mdl = build_model(model_name, cfg, len(names), len(horizons), seed=seed)
                    if kind == "snapshot":
                        mdl.fit(X[wi.end_pos][tr], Ym[wi.end_pos][tr], masks=Mm[wi.end_pos][tr])
                        predict = lambda sel: mdl.predict_proba(X[wi.end_pos][sel])
                    else:
                        mdl.fit(SequenceDataset(T[tr], y_ho=Ym[wi.end_pos][tr],
                                                m_ho=Mm[wi.end_pos][tr]),
                                SequenceDataset(T[va], y_ho=Ym[wi.end_pos][va],
                                                m_ho=Mm[wi.end_pos][va]),
                                metric_fn=__import__(
                                    "hoproj.pipeline.trainer", fromlist=["mean_auprc"]).mean_auprc)
                        predict = lambda sel: mdl.predict(SequenceDataset(T[sel]),
                                                          want=("handover",))["handover"]

                for tgt in regimes:
                    # Regimes co-exist inside a single drive, so a cross-regime test
                    # set drawn without care shares drives with the training set -
                    # exactly the leakage the rest of the pipeline forbids. Every
                    # evaluation therefore uses only drives held out from training,
                    # whether the regime matches or not.
                    sel = (reg_rows == tgt) & np.isin(drives_rows, list(val_d))
                    if sel.sum() < 200:
                        continue
                    P = predict(sel)
                    Yt, Mt = Ym[wi.end_pos][sel], Mm[wi.end_pos][sel]
                    g = drives_rows[sel]
                    for j, h in enumerate(horizons):
                        ok = Mt[:, j].astype(bool)
                        if ok.sum() < 100 or len(np.unique(Yt[ok, j])) < 2:
                            continue
                        m = MET.classification_metrics(Yt[ok, j], P[ok, j])
                        boot = ST.drive_bootstrap(
                            lambda yy, pp: MET.classification_metrics(yy, pp)["auprc"],
                            Yt[ok, j], P[ok, j], g[ok],
                            n=int(cfg.get_path("eval.bootstrap.n", 200)), seed=seed)
                        rows.append({
                            "conditioning": cond, "model": model_name,
                            "train_regime": src, "test_regime": tgt,
                            "same_regime": src == tgt, "horizon_s": h,
                            "n": int(ok.sum()), "n_drives": boot["n_groups"],
                            "positive_rate": m["positive_rate"], "auprc": m["auprc"],
                            "auprc_lift": m["auprc_lift"], "auroc": m["auroc"],
                            "auprc_ci_low": boot["ci_low"], "auprc_ci_high": boot["ci_high"],
                            "ece": m["ece"]})
    res = pd.DataFrame(rows)
    RPT.save_table(res, paths["reports"], "regime_transfer")
    write_json({"regimes": regimes, "captures": [c[0] for c in CAPTURES],
                "config_features": CONFIG_FEATURES,
                "note": "regimes co-exist inside single drives, so city, UE, driver, day "
                        "and route are held fixed while the handover rule varies"},
               paths["artifacts"] / "regime_transfer.json")
    return res


def main(argv=None):
    ap = argparse.ArgumentParser(description="Stage 07: configuration-regime transfer")
    ap.add_argument("--root", default=None)
    ap.add_argument("--models", nargs="*", default=["lgbm", "gru"])
    ap.add_argument("--epochs", type=int, default=25)
    args = ap.parse_args(argv)
    cfg = Config(deep_merge(load_config("base.yaml", adapter="xcal_signalling"),
                            {"train": {"epochs": args.epochs, "early_stop_patience": 6},
                             "eval": {"bootstrap": {"n": 200}},
                             "features": {"blocks": BLOCKS}}))
    return run(cfg, resolve_paths(cfg, args.root), tuple(args.models))


if __name__ == "__main__":
    main()

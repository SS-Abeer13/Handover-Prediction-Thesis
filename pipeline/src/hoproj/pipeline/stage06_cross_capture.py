"""Stage 06 - cross-capture transfer: train on one capture, test on another.

Section 22 of the proposal declares device/operator/service shift as OOD
scenarios. This stage implements the strongest version available here: train on
one measurement campaign and evaluate on a *different capture, on different
days, with different equipment settings*. Nothing is shared between the two -
not the drives, not the routes, not the cells, not the scaler.

That is a harder test than the locked-route holdout, because the locked route at
least came out of the same export. If a model survives this, the claim is about
LTE mobility dynamics rather than about one campaign.

Two feature regimes are reported, because the captures differ in what they log:

``full``    every feature both captures can build (113).
``robust``  drops the 14 neighbour-derived features that are populated in under
            half of the XCAL samples, since those come from event-triggered
            MeasurementReports rather than a periodic column. This is the set a
            deployable model could actually rely on across captures.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from ..config import Config, deep_merge, load_config, resolve_paths
from ..data import ingest, qc, segment
from ..data import labels as L
from ..data.features import build_features, select_blocks
from ..data.transforms import TabularTransform
from ..data.windows import build_window_index, materialise
from ..deploy.profile import model_footprint
from ..eval import events as EV
from ..eval import metrics as MET
from ..eval import report as RPT
from ..eval import stats as ST
from ..models.dataset import SequenceDataset
from ..models.registry import build_model, model_kind
from ..uncertainty.calibration import TemperatureScaler
from ..utils import get_logger, set_seed, timed, write_json

LOG = get_logger("hoproj.stage06")

BLOCKS = ["rf", "mobility", "history"]
SPARSE_NEIGHBOUR = [
    "gap_serving_best_nbr", "gap_serving_nbr1", "gap_serving_nbr2", "gap_serving_nbr3",
    "gap_serving_nbr2_mean3", "gap_serving_nbr2_mean5", "gap_serving_nbr3_mean3",
    "gap_serving_nbr3_mean5", "nbr1_rsrp", "nbr2_rsrp", "nbr3_rsrp",
    "nbr_best_rsrp", "nbr_mean_rsrp", "nbr_spread_rsrp",
]


@dataclass
class Domain:
    name: str
    features: pd.DataFrame
    labels: pd.DataFrame
    ho: pd.DataFrame
    drives: pd.DataFrame
    horizons: list[float]
    tags: list[str]


def prepare(name: str, adapter: str, raw: Path, sources: dict,
            base: str = "base.yaml", overrides: dict | None = None) -> Domain:
    ov = {"data": {"sources": sources}, "features": {"blocks": BLOCKS,
                                                     "regime": "topology_agnostic"}}
    if overrides:
        ov = deep_merge(ov, overrides)
    cfg = Config(deep_merge(load_config(base, adapter=adapter), ov))
    with timed(f"prepare {name}"):
        samples, events = ingest.ingest(cfg, raw)
        samples = segment.assign_routes(samples, events, cfg)
        samples = segment.segment_drives(samples, cfg)
        drives = segment.drive_table(samples)
        qc_tbl = qc.drive_quality(samples, drives, cfg)
        samples = qc.apply_qc(samples, qc_tbl)
        drives = drives[drives["drive_id"].isin(set(samples["drive_id"]))].reset_index(drop=True)
        ho = L.handover_events(samples, events, cfg)
        ho = ho[ho["drive_id"].isin(set(samples["drive_id"]))].reset_index(drop=True)
        lab = L.build_labels(samples, ho, cfg)
        feats = build_features(samples, lab, cfg)
        lab = (feats[["drive_id", "t"]].merge(lab, on=["drive_id", "t"], how="left")
               .reset_index(drop=True))
    LOG.info("%s: %d samples, %d drives, %d handovers, prevalence %s",
             name, len(feats), drives["drive_id"].nunique(), len(ho),
             {t: round(float(lab.loc[lab[f"m_ho_{t}"] == 1, f"y_ho_{t}"].mean()), 4)
              for t in L.horizon_tags(cfg)})
    return Domain(name, feats, lab, ho, drives, L.usable_horizons(cfg), L.horizon_tags(cfg))


def _matrices(dom: Domain, names: list[str], L_win: int, stride: int):
    wi = build_window_index(dom.features, L_win, stride, 0.0,
                            dom.features["is_interpolated"].to_numpy(bool)
                            if "is_interpolated" in dom.features else None)
    Y = np.column_stack([dom.labels[f"y_ho_{t}"].to_numpy(np.float32) for t in dom.tags])
    M = np.column_stack([dom.labels[f"m_ho_{t}"].to_numpy(np.float32) for t in dom.tags])
    return wi, Y, M


def run(source: Domain, targets: list[Domain], cfg: Config, models: list[str],
        feature_sets: dict[str, list[str]], paths: dict, seed: int = 1337) -> pd.DataFrame:
    period = float(cfg.get_path("data.target_period_s") or 1.0)
    L_win = max(2, int(round(float(cfg.get_path("windows.length_s", 10.0)) / period)))
    stride = max(1, int(round(float(cfg.get_path("windows.stride_s", 1.0)) / period)))
    horizons = source.horizons
    rows, ev_rows = [], []

    for fs_name, drop in feature_sets.items():
        names = [n for n in select_blocks(source.features, BLOCKS) if n not in drop]
        names = [n for n in names if n in source.features.columns
                 and all(n in t.features.columns for t in targets)]
        LOG.info("feature set %r: %d features", fs_name, len(names))

        # ---- source split: whole drives, train / val(threshold+calibration)
        rng = np.random.default_rng(seed)
        ids = source.drives["drive_id"].to_numpy()
        rng.shuffle(ids)
        n_val = max(1, int(round(0.25 * len(ids))))
        val_ids, train_ids = set(ids[:n_val]), set(ids[n_val:])
        tr_rows = source.features["drive_id"].isin(train_ids).to_numpy()
        va_rows = source.features["drive_id"].isin(val_ids).to_numpy()

        tf = TabularTransform(cfg.get_path("features.scaler", "robust"),
                              clip_sigma=float(cfg.get_path("features.clip_sigma", 8.0)))
        tf.fit(source.features.loc[tr_rows, names])
        Xs = tf.transform(source.features[names])

        wi_s, Ys, Ms = _matrices(source, names, L_win, stride)
        keep_tr = tr_rows[wi_s.end_pos]
        keep_va = va_rows[wi_s.end_pos]
        Ts = materialise(Xs, wi_s)

        prepared_targets = []
        for tgt in targets:
            Xt = tf.transform(tgt.features[names])          # SOURCE statistics, deliberately
            wi_t, Yt, Mt = _matrices(tgt, names, L_win, stride)
            prepared_targets.append((tgt, materialise(Xt, wi_t), wi_t, Yt, Mt))

        for model_name in models:
            set_seed(seed)
            kind = model_kind(model_name)
            with timed(f"train {model_name} on {source.name} [{fs_name}]"):
                if kind == "snapshot":
                    mdl = build_model(model_name, cfg, len(names), len(horizons), seed=seed)
                    mdl.fit(Xs[wi_s.end_pos][keep_tr], Ys[wi_s.end_pos][keep_tr],
                            masks=Ms[wi_s.end_pos][keep_tr])
                    footprint = {"n_parameters": getattr(mdl, "n_params", 0)}
                else:
                    ds_tr = SequenceDataset(Ts[keep_tr], y_ho=Ys[wi_s.end_pos][keep_tr],
                                            m_ho=Ms[wi_s.end_pos][keep_tr])
                    ds_va = SequenceDataset(Ts[keep_va], y_ho=Ys[wi_s.end_pos][keep_va],
                                            m_ho=Ms[wi_s.end_pos][keep_va])
                    from .trainer import mean_auprc
                    mdl = build_model(model_name, cfg, len(names), len(horizons), seed=seed)
                    mdl.fit(ds_tr, ds_va, metric_fn=mean_auprc)
                    footprint = model_footprint(mdl.model)

            def predict(X_scaled, tensor, wi):
                """Predictions for the rows a window index points at."""
                if kind == "snapshot":
                    return mdl.predict_proba(X_scaled[wi.end_pos])
                return mdl.predict(SequenceDataset(tensor), want=("handover",))["handover"]

            # calibrate on the SOURCE validation drives only
            p_val = (mdl.predict_proba(Xs[wi_s.end_pos][keep_va]) if kind == "snapshot"
                     else mdl.predict(SequenceDataset(Ts[keep_va]),
                                      want=("handover",))["handover"])
            scaler = TemperatureScaler().fit(p_val, Ys[wi_s.end_pos][keep_va],
                                             Ms[wi_s.end_pos][keep_va])
            thr = []
            for j in range(len(horizons)):
                sel = Ms[wi_s.end_pos][keep_va][:, j].astype(bool)
                t_ = 0.5
                if sel.sum() > 50 and len(np.unique(Ys[wi_s.end_pos][keep_va][sel, j])) > 1:
                    _, t_ = MET.recall_at_fpr(Ys[wi_s.end_pos][keep_va][sel, j],
                                              scaler.transform(p_val)[sel, j], 0.05)
                thr.append(float(t_) if np.isfinite(t_) else 0.5)

            evaluations = [("SOURCE held-out drives", source, p_val,
                            Ys[wi_s.end_pos][keep_va], Ms[wi_s.end_pos][keep_va],
                            source.features.loc[wi_s.end_pos[keep_va]])]
            for tgt, Tt, wi_t, Yt, Mt in prepared_targets:
                pt = predict(tf.transform(tgt.features[names]), Tt, wi_t)
                evaluations.append((tgt.name, tgt, pt, Yt[wi_t.end_pos], Mt[wi_t.end_pos],
                                    tgt.features.loc[wi_t.end_pos]))

            for label, dom, P, Y, M, meta in evaluations:
                Pc = scaler.transform(P)
                for j, h in enumerate(horizons):
                    sel = M[:, j].astype(bool)
                    if sel.sum() < 50 or len(np.unique(Y[sel, j])) < 2:
                        continue
                    m = MET.classification_metrics(Y[sel, j], Pc[sel, j])
                    boot = ST.drive_bootstrap(
                        lambda yy, pp: MET.classification_metrics(yy, pp)["auprc"],
                        Y[sel, j], Pc[sel, j], meta["drive_id"].to_numpy()[sel],
                        n=int(cfg.get_path("eval.bootstrap.n", 200)), seed=seed)
                    rows.append({"train_on": source.name, "test_on": label,
                                 "model": model_name, "feature_set": fs_name,
                                 "horizon_s": h, "n": int(sel.sum()),
                                 "positive_rate": m["positive_rate"], "auprc": m["auprc"],
                                 "auprc_lift": m["auprc_lift"],
                                 "auprc_ci_low": boot["ci_low"], "auprc_ci_high": boot["ci_high"],
                                 "auroc": m["auroc"], "recall_at_fpr0.05": m["recall_at_fpr0.05"],
                                 "brier": m["brier"], "ece": m["ece"],
                                 "n_drives": boot["n_groups"]})
                et = EV.detection_by_horizon(meta.reset_index(drop=True), Pc, M, dom.ho,
                                             horizons, thr, warn_horizon_s=5.0)
                if len(et):
                    et.insert(0, "train_on", source.name)
                    et.insert(1, "test_on", label)
                    et["feature_set"] = fs_name
                    et["model"] = model_name
                    ev_rows.append(et)

    res = pd.DataFrame(rows)
    ev = pd.concat(ev_rows, ignore_index=True) if ev_rows else pd.DataFrame()
    tag = f"cross_capture_from_{source.name}"
    RPT.save_table(res, paths["reports"], tag)
    if len(ev):
        RPT.save_table(ev[[c for c in ["train_on", "test_on", "model", "feature_set",
                                       "horizon_s", "n_events", "event_detection_rate",
                                       "median_lead_time_s", "false_alarms_per_hour"]
                           if c in ev]], paths["reports"], f"{tag}_events")
    return res


def main(argv=None):
    ap = argparse.ArgumentParser(description="Stage 06: cross-capture transfer")
    ap.add_argument("--root", default=None)
    ap.add_argument("--models", nargs="*", default=["lgbm", "gru"])
    ap.add_argument("--epochs", type=int, default=25)
    args = ap.parse_args(argv)

    cfg = Config(deep_merge(load_config("base.yaml", adapter="curated_v1"),
                            {"train": {"epochs": args.epochs, "early_stop_patience": 6},
                             "eval": {"bootstrap": {"n": 200}},
                             "features": {"blocks": BLOCKS}}))
    paths = resolve_paths(cfg, args.root)

    curated = prepare("curated 6-8 Sept", "curated_v1", paths["raw"],
                      {"samples": "DRIVETEST_LOGS_1_fixed.csv",
                       "handovers": "HANDOVER_LOG_REGENERATED.csv"})
    xcal_over = {"segmentation": {"method": "fixed_duration", "fixed_duration_s": 180,
                                  "route_from": "config"},
                 "qc": {"min_drive_duration_s": 60, "min_drive_samples": 60}}
    s10 = prepare("XCAL 10 Sept", "xcal_signalling", Path("sept10/data/raw"),
                  {"samples": "test 10 sept-M1.csv",
                   "signalling": "test_10_sept_signalling.txt"}, overrides=xcal_over)
    s12 = prepare("XCAL 12 Sept", "xcal_signalling", Path("sept12/data/raw"),
                  {"samples": "test 12 sept.csv",
                   "signalling": "test 12 sept signalling.txt"}, overrides=xcal_over)
    s13 = prepare("XCAL 13 Sept", "xcal_signalling", Path("sept13/data/raw"),
                  {"samples": "test 13 sept.csv",
                   "signalling": "test 13 sept signalling.txt"}, overrides=xcal_over)

    fsets = {"full": set(), "robust": set(SPARSE_NEIGHBOUR)}
    out = []
    out.append(run(curated, [s10, s12, s13], cfg, args.models, fsets, paths))
    out.append(run(s10, [s12, s13, curated], cfg, args.models, fsets, paths))
    out.append(run(s12, [s10, s13, curated], cfg, args.models, fsets, paths))
    out.append(run(s13, [s10, s12, curated], cfg, args.models, fsets, paths))
    allres = pd.concat(out, ignore_index=True)
    RPT.save_table(allres, paths["reports"], "cross_capture_all")
    write_json({"domains": ["curated 6-8 Sept", "XCAL 10 Sept", "XCAL 12 Sept",
                            "XCAL 13 Sept"],
                "feature_sets": {k: sorted(v) for k, v in fsets.items()},
                "note": "scaler, thresholds and temperature are all fitted on the source "
                        "capture only; the target capture contributes nothing."},
               paths["artifacts"] / "cross_capture.json")
    return allres


if __name__ == "__main__":
    main()

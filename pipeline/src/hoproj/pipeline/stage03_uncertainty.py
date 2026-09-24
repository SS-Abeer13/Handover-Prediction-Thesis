"""Stage 03 (R14): deep ensemble, calibration, conformal, OOD, abstention.

Order matters and is enforced here:

1. train ``ensemble_size`` members on the SAME grouped training drives;
2. fit the temperature on the CALIBRATION drives (never train, never val);
3. fit the conformal thresholds on the same calibration drives, pooled per drive;
4. fit the OOD scorers on TRAIN representations;
5. choose the abstention threshold tau on validation + calibration only;
6. report coverage, risk and OOD separation on the held-out drives.

The external route is evaluated in stage 04 with every one of these frozen.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from ..config import Config, load_config, parse_cli_overrides, resolve_paths
from ..eval import metrics as MET
from ..eval import report as RPT
from ..uncertainty import abstention as AB
from ..uncertainty import ood as OOD
from ..uncertainty.calibration import build_calibrator, reliability_curve
from ..uncertainty.conformal import BinaryMondrianConformal
from ..uncertainty.ensemble import DeepEnsemble
from ..utils import get_logger, timed, write_json, write_parquet
from .assemble import assemble, make_dataset, window_meta
from .stage02_experiment import load_processed

LOG = get_logger("hoproj.stage03")


def train_ensemble(cfg: Config, a, model_name: str, size: int):
    from ..models.registry import build_model

    tasks = cfg.get_path("tasks", {})
    ds = {p: make_dataset(a, p, tasks) for p in ("train", "val", "calib", "test")}
    from .trainer import mean_auprc

    members = []
    for i in range(size):
        seed = int(cfg.get_path("project.seed", 0)) + 101 * i
        m = build_model(model_name, cfg, a.n_features, len(a.horizons),
                        d_cand=a.d_cand, seed=seed)
        with timed(f"ensemble member {i+1}/{size} (seed {seed})"):
            m.fit(ds["train"], ds["val"] if len(ds["val"]) else None, metric_fn=mean_auprc)
        members.append(m)
    return DeepEnsemble(members), ds


def run(cfg: Config, paths: dict, model_name: str = "gru",
        condition: str = "grouped_drive") -> dict:
    feats, labels, ho, splits = load_processed(paths)
    split = splits[condition]
    a = assemble(feats, labels, cfg, split, paths["interim"] / "window_cache")
    size = int(cfg.get_path("uncertainty.ensemble_size", 5))
    ens, ds = train_ensemble(cfg, a, model_name, size)
    ens.save(paths["artifacts"] / f"ensemble_{model_name}_{condition}")

    horizons = a.horizons
    pred = {p: ens.predict(ds[p]) for p in ("train", "val", "calib", "test") if len(ds[p])}
    pos = {p: a.windows[p].end_pos for p in pred}
    Y = {p: a.Y_ho[pos[p]] for p in pred}
    M = {p: a.M_ho[pos[p]] for p in pred}
    meta = {p: window_meta(a, p) for p in pred}

    # ---------------------------------------------------------- 2. calibration
    cal_kind = cfg.get_path("uncertainty.calibration", "temperature")
    calibrator = build_calibrator(cal_kind)
    if "calib" in pred:
        calibrator.fit(pred["calib"]["mean"], Y["calib"], M["calib"])
    cal = {p: calibrator.transform(v["mean"]) for p, v in pred.items()}

    rows, curves = [], {}
    for part in ("val", "test"):
        if part not in pred:
            continue
        for j, h in enumerate(horizons):
            sel = M[part][:, j].astype(bool)
            if sel.sum() < 50 or len(np.unique(Y[part][sel, j])) < 2:
                continue
            raw = MET.classification_metrics(Y[part][sel, j], pred[part]["mean"][sel, j])
            cl = MET.classification_metrics(Y[part][sel, j], cal[part][sel, j])
            rows.append({"part": part, "horizon_s": h, "variant": "ensemble_raw", **raw})
            rows.append({"part": part, "horizon_s": h, "variant": f"ensemble_{cal_kind}", **cl})
            if part == "test":
                curves[f"raw h={h}s"] = reliability_curve(Y[part][sel, j], pred[part]["mean"][sel, j])
                curves[f"cal h={h}s"] = reliability_curve(Y[part][sel, j], cal[part][sel, j])
    calib_table = pd.DataFrame(rows)

    # ------------------------------------------------------------ 3. conformal
    conformal_report = {}
    if cfg.get_path("uncertainty.conformal.enabled", True) and "calib" in pred:
        cp = BinaryMondrianConformal(float(cfg.get_path("uncertainty.conformal.alpha", 0.1)))
        groups = meta["calib"]["drive_id"].to_numpy() \
            if cfg.get_path("uncertainty.conformal.blocks", "drive") == "drive" else None
        cp.fit(cal["calib"], Y["calib"], M["calib"], groups)
        for part in ("val", "test"):
            if part in pred:
                conformal_report[part] = cp.coverage(cal[part], Y[part], M[part],
                                                    meta[part]["drive_id"].to_numpy())
        write_json({"alpha": cp.alpha, "thresholds": cp.q_.tolist(),
                    "coverage": conformal_report}, paths["artifacts"] / "conformal.json")

    # ------------------------------------------------------------------ 4. OOD
    Ztr = ens.embeddings(ds["train"])
    scorers = OOD.build_scorers(cfg)
    fitted = {}
    for name, sc in scorers.items():
        if name in ("mahalanobis", "knn"):
            fitted[name] = sc.fit(Ztr)
        else:
            fitted[name] = sc.fit()
    Z = {p: ens.embeddings(ds[p]) for p in pred}

    def scores_for(part: str) -> dict[str, np.ndarray]:
        out = {}
        for name, sc in fitted.items():
            if name == "ensemble_disagreement":
                out[name] = sc.score(pred[part]["std"])
            elif name == "energy":
                out[name] = sc.score(cal[part])
            else:
                out[name] = sc.score(Z[part])
        return out

    ood_scores = {p: scores_for(p) for p in pred}

    # declared shifts inside the development domain (temporal / mobility)
    drives = pd.read_parquet(paths["processed"] / "drives.parquet") \
        if (paths["processed"] / "drives.parquet").exists() else None
    ood_rows = []
    if drives is not None:
        for kind in ("temporal", "mobility"):
            grp = OOD.declare_shift_groups(drives, kind, split.train + split.val, split.test)
            if not grp:
                continue
            for name, s in ood_scores.get("val", {}).items():
                din = meta["val"]["drive_id"].isin(grp["in"]).to_numpy()
                dout = meta["val"]["drive_id"].isin(grp["out"]).to_numpy()
                if din.sum() < 50 or dout.sum() < 50:
                    continue
                res = OOD.evaluate_ood(s[din], s[dout])
                ood_rows.append({"shift": kind, "score": name, "part": "val", **res})
    ood_table = pd.DataFrame(ood_rows)

    # ------------------------------------------------------------ 5. abstention
    coverages = [float(c) for c in cfg.get_path("uncertainty.abstention.target_coverages",
                                                [1.0, 0.95, 0.9, 0.8, 0.7, 0.6, 0.5])]
    j_ref = min(len(horizons) - 1, max(range(len(horizons)),
                                       key=lambda j: horizons[j] if horizons[j] <= 2.0 else -1))
    primary_score = cfg.get_path("uncertainty.ood.scores", ["ensemble_disagreement"])[0]
    pool_parts = [p for p in ("val", "calib") if p in ood_scores]
    pool = np.concatenate([ood_scores[p][primary_score] for p in pool_parts]) if pool_parts else np.empty(0)
    taus = {c: AB.select_threshold(pool, c) for c in coverages}
    thr_op = _operating_threshold(Y, M, cal, j_ref,
                                  float(cfg.get_path("eval.event.operating_fpr", 0.05)))
    rc_curves = {}
    for part in ("val", "test"):
        if part not in pred:
            continue
        sel = M[part][:, j_ref].astype(bool)
        rc = AB.risk_coverage_curve(Y[part][sel, j_ref], cal[part][sel, j_ref],
                                    ood_scores[part][primary_score][sel],
                                    coverages=coverages, taus=taus,
                                    decision_threshold=thr_op)
        rc["part"] = part
        rc["horizon_s"] = horizons[j_ref]
        rc["ood_score"] = primary_score
        rc_curves[part] = rc

    reports = paths["reports"]
    if len(calib_table):
        RPT.save_table(calib_table, reports, "uncertainty_calibration")
    if len(ood_table):
        RPT.save_table(ood_table, reports, "ood_detection")
    rc_all = pd.concat(rc_curves.values(), ignore_index=True) if rc_curves else pd.DataFrame()
    if len(rc_all):
        RPT.save_table(rc_all, reports, "risk_coverage")
        RPT.plot_risk_coverage(rc_curves, reports)
    RPT.plot_reliability(curves, reports)

    conf_md = "_conformal disabled_"
    if conformal_report:
        conf_md = RPT.df_to_md(pd.DataFrame([
            {"part": part, "horizon_s": horizons[j], **v}
            for part, per_h in conformal_report.items() for j, v in per_h.items()]))

    RPT.write_markdown_report([
        ("Ensemble", f"- model: `{model_name}`\n- members: {ens.size}\n"
                     f"- condition: `{condition}`\n- calibration: `{cal_kind}` "
                     f"fitted on {len(split.calib)} held-back calibration drives"),
        ("Calibration before and after", RPT.df_to_md(
            calib_table[["part", "horizon_s", "variant", "auprc", "brier", "nll", "ece"]]
            if len(calib_table) else pd.DataFrame())),
        ("Conformal coverage (calibrated on whole drives)", conf_md),
        ("OOD detection under declared shifts", RPT.df_to_md(ood_table)),
        ("Risk versus coverage", RPT.df_to_md(rc_all)),
        ("Frozen abstention thresholds",
         "\n".join(f"- coverage {c:.2f} -> tau = {t:.4f}" for c, t in taus.items())),
    ], reports / "03_uncertainty.md", "Uncertainty, OOD and abstention (R14)")

    artefact = {"model": model_name, "condition": condition, "ensemble_size": ens.size,
                "calibration": cal_kind, "primary_ood_score": primary_score,
                "taus": taus, "operating_threshold": thr_op,
                "reference_horizon_s": horizons[j_ref]}
    write_json(artefact, paths["artifacts"] / "uncertainty_policy.json")
    if hasattr(calibrator, "save"):
        calibrator.save(paths["artifacts"] / "calibrator.json")
    LOG.info("stage 03 complete")
    return artefact


def _operating_threshold(Y, M, cal, j, fpr) -> float:
    if "val" not in cal:
        return 0.5
    sel = M["val"][:, j].astype(bool)
    if sel.sum() < 50 or len(np.unique(Y["val"][sel, j])) < 2:
        return 0.5
    _, thr = MET.recall_at_fpr(Y["val"][sel, j], cal["val"][sel, j], fpr)
    return float(thr) if np.isfinite(thr) else 0.5


def main(argv=None):
    ap = argparse.ArgumentParser(description="Stage 03: uncertainty, OOD, abstention")
    ap.add_argument("--config", default="base.yaml")
    ap.add_argument("--adapter", default=None)
    ap.add_argument("--model", default="gru")
    ap.add_argument("--condition", default="grouped_drive")
    ap.add_argument("--root", default=None)
    ap.add_argument("--set", dest="overrides", nargs="*", default=[])
    args = ap.parse_args(argv)
    cfg = load_config(args.config, adapter=args.adapter, model=args.model,
                      overrides=parse_cli_overrides(args.overrides))
    return run(cfg, resolve_paths(cfg, args.root), args.model, args.condition)


if __name__ == "__main__":
    main()

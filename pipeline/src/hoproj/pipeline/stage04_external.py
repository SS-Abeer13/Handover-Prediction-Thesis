"""Stage 04 (R15): locked external-route evaluation.

This stage refuses to run unless a freeze manifest exists.  The manifest records
the config fingerprint, the model choice, the calibration artefacts and the
abstention thresholds that were fixed *before* the external route was touched.
That refusal is the only mechanism that makes "we did not peek" auditable rather
than a claim in a thesis.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from ..config import Config, load_config, parse_cli_overrides, resolve_paths
from ..deploy.profile import export_onnx, model_footprint, profile_torch_model
from ..eval import events as EV
from ..eval import metrics as MET
from ..eval import ranking as RK
from ..eval import report as RPT
from ..eval import stats as ST
from ..uncertainty import abstention as AB
from ..uncertainty import ood as OOD
from ..uncertainty.calibration import TemperatureScaler, reliability_curve
from ..utils import get_logger, read_json, timed, write_json, write_parquet
from .assemble import assemble, make_dataset, window_meta
from .stage02_experiment import load_processed
from .stage03_uncertainty import train_ensemble

LOG = get_logger("hoproj.stage04")

FREEZE_FILE = "freeze_manifest.json"


def write_freeze_manifest(cfg: Config, paths: dict, model: str, notes: str = "") -> Path:
    policy_path = paths["artifacts"] / "uncertainty_policy.json"
    manifest = {
        "config_fingerprint": cfg.fingerprint,
        "frozen_model": model,
        "external_route": cfg.get_path("splits.external_route"),
        "horizons_s": cfg.get_path("labels.horizons_s"),
        "window_length_s": cfg.get_path("windows.length_s"),
        "feature_regime": cfg.get_path("features.regime"),
        "feature_blocks": cfg.get_path("features.blocks"),
        "uncertainty_policy": read_json(policy_path) if policy_path.exists() else None,
        "notes": notes,
    }
    path = paths["artifacts"] / FREEZE_FILE
    write_json(manifest, path)
    LOG.info("wrote freeze manifest to %s", path)
    return path


def run(cfg: Config, paths: dict, model_name: str, require_freeze: bool = True) -> dict:
    freeze_path = paths["artifacts"] / FREEZE_FILE
    if require_freeze and not freeze_path.exists():
        raise RuntimeError(
            "the external route is LOCKED: no freeze manifest found. Run stages 01-03, "
            "then `python -m hoproj.pipeline.stage04_external --freeze --model <name>` to "
            "record the frozen protocol, and only then evaluate.")
    manifest = read_json(freeze_path) if freeze_path.exists() else {}
    if manifest.get("config_fingerprint") and manifest["config_fingerprint"] != cfg.fingerprint:
        LOG.warning("config fingerprint changed since the freeze (%s -> %s); the external "
                    "evaluation is no longer a clean holdout.",
                    manifest["config_fingerprint"], cfg.fingerprint)

    feats, labels, ho, splits = load_processed(paths)
    split = splits["external_route"]
    if not split.test:
        raise RuntimeError("external_route split is empty - check splits.external_route in config")
    a = assemble(feats, labels, cfg, split, paths["interim"] / "window_cache")
    ens, ds = train_ensemble(cfg, a, model_name, int(cfg.get_path("uncertainty.ensemble_size", 5)))

    horizons = a.horizons
    pred = {p: ens.predict(ds[p]) for p in ("val", "calib", "test") if len(ds[p])}
    pos = {p: a.windows[p].end_pos for p in pred}
    Y = {p: a.Y_ho[pos[p]] for p in pred}
    M = {p: a.M_ho[pos[p]] for p in pred}
    meta = {p: window_meta(a, p) for p in pred}

    scaler = TemperatureScaler()
    if "calib" in pred:
        scaler.fit(pred["calib"]["mean"], Y["calib"], M["calib"])
    cal = {p: scaler.transform(v["mean"]) for p, v in pred.items()}

    # ---------------------------------------------------------- primary tables
    table = MET.multi_horizon_table(Y["test"], cal["test"], M["test"], horizons,
                                    tuple(cfg.get_path("eval.fixed_fpr", [0.01, 0.05, 0.1])))
    table.insert(0, "model", model_name)
    table.insert(1, "condition", "external_route")
    boot = []
    from sklearn.metrics import average_precision_score
    for j, h in enumerate(horizons):
        sel = M["test"][:, j].astype(bool)
        if sel.sum() < 50 or len(np.unique(Y["test"][sel, j])) < 2:
            continue
        res = ST.drive_bootstrap(
            lambda yy, pp: average_precision_score(yy, pp) if len(np.unique(yy)) > 1 else np.nan,
            Y["test"][sel, j], cal["test"][sel, j], meta["test"]["drive_id"].to_numpy()[sel],
            n=int(cfg.get_path("eval.bootstrap.n", 1000)), seed=int(cfg.get_path("project.seed", 0)))
        boot.append({"horizon_s": h, **{f"auprc_{k}": v for k, v in res.items()}})
    if boot:
        table = table.merge(pd.DataFrame(boot), on="horizon_s", how="left")

    thresholds = []
    for j in range(len(horizons)):
        thr = 0.5
        if "val" in cal:
            sel = M["val"][:, j].astype(bool)
            if sel.sum() > 50 and len(np.unique(Y["val"][sel, j])) > 1:
                _, thr = MET.recall_at_fpr(Y["val"][sel, j], cal["val"][sel, j],
                                           float(cfg.get_path("eval.event.operating_fpr", 0.05)))
        thresholds.append(float(thr) if np.isfinite(thr) else 0.5)
    event_table = EV.detection_by_horizon(meta["test"], cal["test"], M["test"], ho,
                                          horizons, thresholds,
                                          float(cfg.get_path("eval.event.warn_horizon_s", 5.0)))
    if len(event_table):
        event_table.insert(0, "model", model_name)

    # ----------------------------------------------------------- OOD/abstention
    policy = manifest.get("uncertainty_policy") or {}
    primary = policy.get("primary_ood_score",
                         cfg.get_path("uncertainty.ood.scores", ["ensemble_disagreement"])[0])
    scorers = OOD.build_scorers(cfg)
    Ztr = ens.embeddings(ds["train"]) if "train" in ds else None
    sc = scorers[primary]
    if primary in ("mahalanobis", "knn") and Ztr is not None:
        sc.fit(Ztr)
    else:
        sc.fit()

    def _score(part: str) -> np.ndarray:
        if primary == "ensemble_disagreement":
            return sc.score(pred[part]["std"])
        if primary == "energy":
            return sc.score(cal[part])
        return sc.score(ens.embeddings(ds[part]))

    s_dev = np.concatenate([_score(p) for p in ("val", "calib") if p in pred])
    s_ext = _score("test")
    ood_geo = OOD.evaluate_ood(s_dev, s_ext)

    taus = {float(k): float(v) for k, v in (policy.get("taus") or {}).items()} or \
        {c: AB.select_threshold(s_dev, c) for c in
         cfg.get_path("uncertainty.abstention.target_coverages", [1.0, 0.9, 0.8])}
    j_ref = min(range(len(horizons)), key=lambda j: abs(horizons[j] -
                float(policy.get("reference_horizon_s", 2.0))))
    sel = M["test"][:, j_ref].astype(bool)
    rc = AB.risk_coverage_curve(Y["test"][sel, j_ref], cal["test"][sel, j_ref], s_ext[sel],
                                coverages=sorted(taus), taus=taus,
                                decision_threshold=float(policy.get("operating_threshold", 0.5)))
    rc["part"] = "external_route"
    rc["horizon_s"] = horizons[j_ref]

    # --------------------------------------------------------- unseen-cell RQ6
    ranking_table = pd.DataFrame()
    if a.cand is not None and cfg.get_path("tasks.target.enabled", False):
        scores = ens.members[0].predict(ds["test"], want=("target",)).get("target")
        if scores is not None:
            seen = set(feats.loc[feats["drive_id"].isin(split.train), "serving_cell_name"]
                       .dropna().astype(str))
            tgt_cell = meta["test"].get("serving_cell_name", pd.Series(index=meta["test"].index))
            ranking_table = RK.unseen_cell_breakdown(
                scores, a.y_target[pos["test"]], tgt_cell.astype(str).to_numpy(), seen,
                valid=(a.cand_mask[pos["test"]].sum(axis=1) > 0))

    # ------------------------------------------------------------- deployment
    deploy_rows = []
    period = float(cfg.get_path("data.target_period_s") or 1.0)
    L = max(2, int(round(float(cfg.get_path("windows.length_s", 10.0)) / period)))
    m0 = ens.members[0]
    if hasattr(m0, "model"):
        deploy_rows = profile_torch_model(
            m0.model, L, a.n_features,
            tuple(cfg.get_path("deploy.profile_batch_sizes", [1, 32, 256])),
            int(cfg.get_path("deploy.profile_repeats", 50)))
        fp = model_footprint(m0.model)
        for r in deploy_rows:
            r.update(fp)
            r["model"] = model_name
        if cfg.get_path("deploy.export_onnx", False):
            export_onnx(m0.model, L, a.n_features, paths["artifacts"] / f"{model_name}.onnx")
    deploy_table = pd.DataFrame(deploy_rows)

    reports = paths["reports"]
    RPT.save_table(table, reports, "external_route_results")
    if len(event_table):
        RPT.save_table(event_table, reports, "external_route_events")
    RPT.save_table(rc, reports, "external_route_risk_coverage")
    if len(deploy_table):
        RPT.save_table(deploy_table, reports, "deployment_profile")
    if len(ranking_table):
        RPT.save_table(ranking_table, reports, "external_route_target_ranking")
    curves = {}
    for j, h in enumerate(horizons):
        s = M["test"][:, j].astype(bool)
        if s.sum() > 100 and len(np.unique(Y["test"][s, j])) > 1:
            curves[f"external h={h}s"] = reliability_curve(Y["test"][s, j], cal["test"][s, j])
    RPT.plot_reliability(curves, reports, name="external_reliability")
    RPT.plot_risk_coverage({"external_route": rc}, reports, name="external_risk_coverage")

    RPT.write_markdown_report([
        ("Frozen protocol", "\n".join(f"- **{k}**: {v}" for k, v in manifest.items()
                                      if k != "uncertainty_policy")),
        ("External-route performance (calibrated ensemble)", RPT.df_to_md(table)),
        ("Event-level detection and lead time", RPT.df_to_md(event_table)),
        ("Geographic OOD separation", "\n".join(f"- **{k}**: {v}" for k, v in ood_geo.items())),
        ("Risk versus coverage with frozen thresholds", RPT.df_to_md(rc)),
        ("Target-cell ranking, seen vs unseen cells", RPT.df_to_md(ranking_table)
         if len(ranking_table) else "_target-cell task disabled_"),
        ("Deployment profile", RPT.df_to_md(deploy_table)),
    ], reports / "04_external_route.md", "Locked external-route evaluation (R15)")

    write_json({"ood_geographic": ood_geo, "taus": taus,
                "reference_horizon_s": horizons[j_ref]},
               paths["artifacts"] / "external_summary.json")
    LOG.info("stage 04 complete")
    return {"results": table, "events": event_table, "risk_coverage": rc,
            "ood": ood_geo, "deploy": deploy_table}


def main(argv=None):
    ap = argparse.ArgumentParser(description="Stage 04: locked external-route evaluation")
    ap.add_argument("--config", default="base.yaml")
    ap.add_argument("--adapter", default=None)
    ap.add_argument("--model", default="gru")
    ap.add_argument("--root", default=None)
    ap.add_argument("--freeze", action="store_true",
                    help="write the freeze manifest and exit without touching the external route")
    ap.add_argument("--notes", default="")
    ap.add_argument("--no-require-freeze", action="store_true")
    ap.add_argument("--set", dest="overrides", nargs="*", default=[])
    args = ap.parse_args(argv)
    cfg = load_config(args.config, adapter=args.adapter, model=args.model,
                      overrides=parse_cli_overrides(args.overrides))
    paths = resolve_paths(cfg, args.root)
    if args.freeze:
        return write_freeze_manifest(cfg, paths, args.model, args.notes)
    return run(cfg, paths, args.model, require_freeze=not args.no_require_freeze)


if __name__ == "__main__":
    main()

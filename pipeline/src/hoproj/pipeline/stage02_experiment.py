"""Stage 02 (R11-R13): run the model / regime / feature-set / condition grid."""
from __future__ import annotations

import argparse
import itertools
from pathlib import Path

import numpy as np
import pandas as pd

from ..config import Config, deep_merge, load_config, parse_cli_overrides, resolve_paths
from ..data.splits import Split
from ..eval import report as RPT
from ..eval import stats as ST
from ..utils import get_logger, read_json, read_table, timed, write_json, write_parquet

LOG = get_logger("hoproj.stage02")

FEATURE_SETS = {
    "rf": ["rf"],
    "rf_mob": ["rf", "mobility"],
    "rf_mob_hist": ["rf", "mobility", "history"],
    "rf_mob_hist_qoe": ["rf", "mobility", "history", "qoe"],
    "default": None,
}


def load_processed(paths: dict) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict]:
    processed = paths["processed"]
    feats = read_table(_p(processed, "features"))
    meta = read_json(processed / "feature_meta.json")
    feats.attrs["feature_block"] = meta["feature_block"]
    feats.attrs["feature_names"] = meta["feature_names"]
    labels = read_table(_p(processed, "labels"))
    ho = read_table(_p(processed, "handovers"))
    for df in (feats, labels, ho):
        if "t" in df:
            df["t"] = pd.to_datetime(df["t"])
    splits = {k: Split(**v) for k, v in read_json(processed / "splits.json").items()}
    return feats, labels, ho, splits


def _p(processed: Path, stem: str) -> Path:
    for suffix in (".parquet", ".csv.gz", ".csv"):
        cand = processed / f"{stem}{suffix}"
        if cand.exists():
            return cand
    raise FileNotFoundError(f"{stem} not found in {processed}; run stage01 first")


def run(cfg: Config, paths: dict, allow_external: bool = False) -> pd.DataFrame:
    from .trainer import train_and_evaluate

    feats, labels, ho, splits = load_processed(paths)
    exp = cfg.get_path("experiment", {}) or {}
    models = exp.get("models", ["lgbm", "gru"])
    regimes = exp.get("regimes", [cfg.get_path("features.regime")])
    fsets = exp.get("feature_sets", ["default"])
    conditions = exp.get("conditions", ["grouped_drive"])
    variants = exp.get("variants", {"base": {}})
    fs_map = deep_merge(FEATURE_SETS, cfg.get_path("feature_sets", {}) or {})

    if not allow_external and "external_route" in conditions:
        LOG.warning("external_route requested without --allow-external; it is LOCKED until R15. "
                    "Dropping it from this run.")
        conditions = [c for c in conditions if c != "external_route"]

    horizon_rows, event_rows, artefacts = [], [], {}
    cache = paths["interim"] / "window_cache"
    assembled_cache: dict[tuple, object] = {}   # (condition, regime, feature_set, variant)
    grid = list(itertools.product(conditions, regimes, fsets, variants.items(), models))
    LOG.info("experiment %r: %d runs", exp.get("name", "unnamed"), len(grid))

    for condition, regime, fset, (vname, vover), model_name in grid:
        run_cfg = Config(deep_merge(cfg, {"features": {"regime": regime}}))
        blocks = fs_map.get(fset)
        if blocks:
            run_cfg.set_path("features.blocks", list(blocks))
        if vover:
            run_cfg = Config(deep_merge(run_cfg, vover))
        tag = f"{model_name}|{condition}|{regime}|{fset}|{vname}"
        ckey = (condition, regime, fset, vname)
        if ckey not in assembled_cache:
            from .assemble import assemble
            assembled_cache.clear()             # only one assembly held at a time
            assembled_cache[ckey] = assemble(feats, labels, run_cfg, splits[condition], cache)
        with timed(f"run {tag}"):
            try:
                res = train_and_evaluate(run_cfg, feats, labels, ho, splits[condition],
                                         model_name, feature_set=fset, variant=vname,
                                         cache_dir=cache, assembled=assembled_cache[ckey])
            except Exception as exc:
                LOG.exception("run %s failed: %s", tag, exc)
                continue
        horizon_rows.append(res.horizon_table)
        if len(res.event_table):
            event_rows.append(res.event_table)
        artefacts[tag] = {"footprint": res.footprint,
                          "best_epoch": res.history.get("best_epoch"),
                          "best_val_metric": res.history.get("best_metric")}
        np.save(paths["artifacts"] / f"pred_{_safe(tag)}.npy", res.predictions.get("test", np.empty(0)))
        res.meta.get("test", pd.DataFrame()).to_parquet(
            paths["artifacts"] / f"meta_{_safe(tag)}.parquet", index=False) \
            if "test" in res.meta else None

    if not horizon_rows:
        raise RuntimeError("no run completed successfully")
    results = pd.concat(horizon_rows, ignore_index=True)
    events = pd.concat(event_rows, ignore_index=True) if event_rows else pd.DataFrame()
    name = exp.get("name", "experiment")
    write_parquet(results, paths["artifacts"] / f"results_{name}.parquet")
    if len(events):
        write_parquet(events, paths["artifacts"] / f"events_{name}.parquet")
    write_json(artefacts, paths["artifacts"] / f"runinfo_{name}.json")

    reports = paths["reports"]
    primary = cfg.get_path("eval.primary_metric", "auprc")
    keep = ["model", "condition", "regime", "feature_set", "variant", "horizon_s",
            "n", "positive_rate", "auprc", "auprc_lift", "auroc", "auprc_ci_low",
            "auprc_ci_high", "recall_at_fpr0.05", "brier", "ece"]
    tidy = results[[c for c in keep if c in results.columns]]
    RPT.save_table(tidy, reports, f"{name}_results")
    if len(events):
        ev_keep = ["model", "condition", "regime", "feature_set", "variant", "horizon_s",
                   "n_events", "event_detection_rate", "median_lead_time_s",
                   "false_alarms_per_hour", "false_alarms_per_km", "threshold"]
        RPT.save_table(events[[c for c in ev_keep if c in events.columns]], reports, f"{name}_events")
    RPT.plot_metric_vs_horizon(results[results["condition"] == results["condition"].iloc[0]],
                               reports, primary, name=f"{name}_{primary}_vs_horizon")
    if len(events):
        RPT.plot_lead_time(events[events["condition"] == events["condition"].iloc[0]],
                           reports, name=f"{name}_lead_time")

    sections = [("Runs", RPT.df_to_md(tidy, 80))]
    if len(events):
        sections.append(("Event-level detection and lead time",
                         RPT.df_to_md(events[[c for c in ev_keep if c in events.columns]], 80)))
    if results["condition"].nunique() > 1:
        infl = ST.leakage_inflation(results, primary)
        RPT.save_table(infl, reports, f"{name}_leakage_inflation")
        RPT.plot_leakage(infl, reports, name=f"{name}_leakage", metric=primary)
        sections.append(("Leakage inflation by evaluation protocol", RPT.df_to_md(infl, 60)))
    RPT.write_markdown_report(sections, reports / f"02_{name}.md",
                              f"Experiment: {name}")
    return results


def _safe(tag: str) -> str:
    return tag.replace("|", "__").replace("/", "-")


def main(argv=None):
    ap = argparse.ArgumentParser(description="Stage 02: model comparison grid")
    ap.add_argument("--config", default="base.yaml")
    ap.add_argument("--adapter", default=None)
    ap.add_argument("--experiment", default="main")
    ap.add_argument("--root", default=None)
    ap.add_argument("--allow-external", action="store_true",
                    help="unlock the external route (only at stage R15, after freezing)")
    ap.add_argument("--set", dest="overrides", nargs="*", default=[])
    args = ap.parse_args(argv)
    cfg = load_config(args.config, adapter=args.adapter, experiment=args.experiment,
                      overrides=parse_cli_overrides(args.overrides))
    return run(cfg, resolve_paths(cfg, args.root), allow_external=args.allow_external)


if __name__ == "__main__":
    main()

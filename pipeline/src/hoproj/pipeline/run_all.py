"""End-to-end driver, in protocol order.

Modern XCAL Pipeline (Default):
    python -m hoproj.pipeline.run_all                          # runs stages 12-21 (pooled XCAL)
    python -m hoproj.pipeline.run_all --stage stage12          # prepare pooled captures
    python -m hoproj.pipeline.run_all --stage stage13          # benchmark across models
    python -m hoproj.pipeline.run_all --stage stage14          # hazard evaluation
    python -m hoproj.pipeline.run_all --stage stage15          # Hawkes GoF & CRC frontier
    python -m hoproj.pipeline.run_all --stage stage16          # signalling ablation & ping-pong
    python -m hoproj.pipeline.run_all --stage stage17          # generate publication figures
    python -m hoproj.pipeline.run_all --stage stage18          # equal Bayesian tuning budget
    python -m hoproj.pipeline.run_all --stage stage19          # Astana transfer & UDA CORAL
    python -m hoproj.pipeline.run_all --stage stage20          # Shafi departmental baseline
    python -m hoproj.pipeline.run_all --stage stage21          # LOCO highway transfer

Legacy Pipeline:
    python -m hoproj.pipeline.run_all --pipeline legacy --smoke
    python -m hoproj.pipeline.run_all --pipeline legacy
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from ..config import Config, deep_merge, load_config, parse_cli_overrides, resolve_paths
from ..utils import get_logger, timed

LOG = get_logger("hoproj.run_all")

SMOKE = {
    "train": {"epochs": 3, "batch_size": 128, "early_stop_patience": 2},
    "uncertainty": {"ensemble_size": 2},
    "eval": {"bootstrap": {"n": 100}},
    "deploy": {"profile_repeats": 5, "profile_batch_sizes": [1, 32]},
}


def run_xcal_pipeline(args, over):
    """Run modern XCAL stages 12 to 21."""
    stage = args.stage
    root = args.root

    xcal_stages = [
        ("stage12", "hoproj.pipeline.stage12_xcal_prepare"),
        ("stage13", "hoproj.pipeline.stage13_xcal_benchmark"),
        ("stage14", "hoproj.pipeline.stage14_hazard_fair"),
        ("stage15", "hoproj.pipeline.stage15_gof_frontier"),
        ("stage16", "hoproj.pipeline.stage16_signalling_pingpong"),
        ("stage17", "hoproj.pipeline.stage17_figures"),
        ("stage18", "hoproj.pipeline.stage18_tuning_budget"),
        ("stage19", "hoproj.pipeline.stage19_transfer_adaptation"),
        ("stage20", "hoproj.pipeline.stage20_departmental_baseline"),
        ("stage21", "hoproj.pipeline.stage21_capture_transfer"),
    ]

    selected = []
    if stage in ("all", "xcal", "main"):
        selected = xcal_stages
    else:
        for s_name, mod_path in xcal_stages:
            if stage in (s_name, s_name.replace("stage", "")):
                selected.append((s_name, mod_path))
                break

    if not selected:
        LOG.error("Unknown stage: %s. Available XCAL stages: %s", stage, [s[0] for s in xcal_stages])
        return 1

    LOG.info("Executing XCAL pipeline with %d stages...", len(selected))
    for s_name, mod_path in selected:
        with timed(f"{s_name} ({mod_path})"):
            LOG.info("=== Running %s ===", s_name)
            try:
                mod = __import__(mod_path, fromlist=["main"])
                if hasattr(mod, "main"):
                    mod_argv = []
                    if root:
                        mod_argv.extend(["--root", str(root)])
                    if args.smoke:
                        if s_name == "stage13":
                            mod_argv.extend(["--epochs", "3", "--folds", "2", "--seeds", "1"])
                    mod.main(mod_argv)
                elif hasattr(mod, "run"):
                    mod.run()
                else:
                    LOG.warning("Stage %s has neither main() nor run()", s_name)
            except Exception as e:
                LOG.error("Stage %s failed with exception: %s", s_name, e, exc_info=True)
                if not args.ignore_errors:
                    raise
    LOG.info("XCAL pipeline execution completed successfully.")
    return 0


def run_legacy_pipeline(args, over):
    """Run legacy stages 01 to 05."""
    base = load_config(args.config, adapter=args.adapter, overrides=over)
    paths = resolve_paths(base, args.root)
    stage = args.stage

    from . import stage01_prepare, stage02_experiment, stage03_uncertainty
    from . import stage04_external, stage05_report

    if stage in ("all", "prepare"):
        with timed("stage 01 prepare"):
            stage01_prepare.run(base, paths)
    if stage in ("all", "experiments"):
        for name in args.experiments:
            cfg = load_config(args.config, adapter=args.adapter, experiment=name, overrides=over)
            with timed(f"stage 02 experiment {name}"):
                stage02_experiment.run(cfg, paths, allow_external=False)
    if stage in ("all", "uncertainty"):
        cfg = load_config(args.config, adapter=args.adapter, model=args.model, overrides=over)
        with timed("stage 03 uncertainty"):
            stage03_uncertainty.run(cfg, paths, args.model, "grouped_drive")
    if stage == "external":
        cfg = load_config(args.config, adapter=args.adapter, model=args.model, overrides=over)
        with timed("stage 04 external"):
            stage04_external.run(cfg, paths, args.model)
    if stage in ("all", "report", "external"):
        with timed("stage 05 report"):
            out = stage05_report.run(base, paths)
            LOG.info("consolidated report: %s", out)
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="Run the whole pipeline")
    ap.add_argument("--pipeline", default="xcal", choices=["xcal", "legacy"],
                    help="Pipeline suite to execute: xcal (stages 12-21, default) or legacy (stages 01-05)")
    ap.add_argument("--config", default="base.yaml")
    ap.add_argument("--adapter", default=None)
    ap.add_argument("--root", default=None)
    ap.add_argument("--stage", default="all",
                    help="Stage to run: all, or specific stage name (e.g. stage12, stage13, ..., stage21)")
    ap.add_argument("--experiments", nargs="*",
                    default=["main", "leakage_study", "ablation_features"])
    ap.add_argument("--model", default="gru", help="model used for uncertainty stage")
    ap.add_argument("--smoke", action="store_true", help="tiny run to verify wiring")
    ap.add_argument("--ignore-errors", action="store_true", help="continue pipeline on stage error")
    ap.add_argument("--set", dest="overrides", nargs="*", default=[])
    args = ap.parse_args(argv)

    over = parse_cli_overrides(args.overrides)
    if args.smoke:
        over = deep_merge(SMOKE, over)
        if "experiments" not in [a for a in (argv or [])]:
            args.experiments = ["main"]

    if args.pipeline == "xcal":
        return run_xcal_pipeline(args, over)
    else:
        return run_legacy_pipeline(args, over)


if __name__ == "__main__":
    raise SystemExit(main())

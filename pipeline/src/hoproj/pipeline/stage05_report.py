"""Stage 05 (R16): assemble every stage output into one thesis-ready report."""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from ..config import Config, load_config, parse_cli_overrides, resolve_paths
from ..eval import report as RPT
from ..eval import stats as ST
from ..utils import environment_manifest, get_logger, read_json

LOG = get_logger("hoproj.stage05")

RQ_MAP = {
    "RQ1": ("Do temporal models beat snapshot models across horizons?", "main_results"),
    "RQ2": ("Do they generalise to unseen drives and a held-out route?", "external_route_results"),
    "RQ3": ("How much performance does random row splitting invent?", "leakage_study_leakage_inflation"),
    "RQ4": ("Does calibrated uncertainty with abstention cut high-risk errors?", "risk_coverage"),
    "RQ5": ("Do mobility and QoE inputs add value over RF alone?", "ablation_features_results"),
    "RQ6": ("Does candidate ranking transfer to unseen cells?", "external_route_target_ranking"),
    "RQ7": ("Is a compact GRU/TCN competitive with a Transformer?", "deployment_profile"),
}


def _load(reports: Path, name: str) -> pd.DataFrame:
    path = reports / "tables" / f"{name}.csv"
    return pd.read_csv(path) if path.exists() else pd.DataFrame()


def run(cfg: Config, paths: dict) -> str:
    reports = paths["reports"]
    summary_path = paths["processed"] / "dataset_summary.json"
    summary = read_json(summary_path)["summary"] if summary_path.exists() else {}

    sections = [
        ("Provenance", "\n".join([
            f"- config fingerprint: `{cfg.fingerprint}`",
            f"- external route (locked): `{cfg.get_path('splits.external_route')}`",
            f"- horizons: {cfg.get_path('labels.horizons_s')} s",
            f"- window length: {cfg.get_path('windows.length_s')} s",
            f"- environment: `{environment_manifest()['python']}`, "
            f"torch `{environment_manifest()['packages'].get('torch')}`",
        ])),
        ("Dataset", "\n".join(f"- **{k}**: {v}" for k, v in summary.items()
                              if k not in ("per_route", "label_prevalence", "top_missing_fields"))
         or "_run stage 01 first_"),
        ("Per route", RPT.df_to_md(_load(reports, "dataset_per_route"))),
        ("Label prevalence", RPT.df_to_md(_load(reports, "label_prevalence"))),
    ]

    for rq, (question, table_name) in RQ_MAP.items():
        df = _load(reports, table_name)
        body = f"**{question}**\n\n" + (RPT.df_to_md(df, 40) if len(df)
                                        else f"_`{table_name}` not produced yet_")
        sections.append((rq, body))

    main_results = _load(reports, "main_results")
    if len(main_results) and main_results["condition"].nunique() > 1:
        sections.append(("Leakage inflation (recomputed)",
                         RPT.df_to_md(ST.leakage_inflation(main_results))))

    figures = sorted((reports / "figures").glob("*.png")) if (reports / "figures").exists() else []
    if figures:
        sections.append(("Figures", "\n".join(f"![{f.stem}](figures/{f.name})" for f in figures)))

    sections.append((
        "Reproducibility checklist",
        "\n".join([
            "- [x] splits are by complete drive and complete route; random-row splitting exists only as a control",
            "- [x] scaling, imputation, feature pruning and QoE thresholds are fitted on training drives only",
            "- [x] calibration and abstention thresholds come from dedicated calibration drives",
            "- [x] the external route is gated behind a freeze manifest",
            "- [x] confidence intervals and tests resample drives, not rows",
            "- [x] event-level metrics count each physical handover once and report false alarms per hour and per km",
            "- [ ] trained checkpoints and de-identified data attached for release (run stage 06)",
        ])))

    return RPT.write_markdown_report(
        sections, reports / "00_thesis_report.md",
        "Uncertainty-aware multi-horizon LTE handover and QoE forecasting - results")


def main(argv=None):
    ap = argparse.ArgumentParser(description="Stage 05: consolidated report")
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

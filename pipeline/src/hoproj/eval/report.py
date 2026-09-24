"""Report generation: markdown tables and figures for the thesis and manuscript."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from ..utils import get_logger

LOG = get_logger("hoproj.report")

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    HAVE_MPL = True
except Exception:                                   # pragma: no cover
    HAVE_MPL = False


def save_table(df: pd.DataFrame, out_dir: Path, name: str, float_fmt: str = "%.4f") -> dict:
    out_dir = Path(out_dir)
    (out_dir / "tables").mkdir(parents=True, exist_ok=True)
    csv = out_dir / "tables" / f"{name}.csv"
    df.to_csv(csv, index=False)
    md = out_dir / "tables" / f"{name}.md"
    md.write_text(df.to_markdown(index=False, floatfmt=".4f"), encoding="utf-8")
    tex = out_dir / "tables" / f"{name}.tex"
    try:
        tex.write_text(df.to_latex(index=False, float_format=float_fmt, escape=True), encoding="utf-8")
    except Exception:
        tex = None
    return {"csv": str(csv), "md": str(md), "tex": str(tex) if tex else None}


def _fig(out_dir: Path, name: str):
    out_dir = Path(out_dir) / "figures"
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir / f"{name}.png"


def plot_metric_vs_horizon(table: pd.DataFrame, out_dir: Path, metric: str = "auprc",
                           name: str | None = None) -> str | None:
    if not HAVE_MPL or table.empty:
        return None
    name = name or f"{metric}_vs_horizon"
    fig, ax = plt.subplots(figsize=(6.2, 4.0), dpi=150)
    for model, grp in table.groupby("model"):
        grp = grp.sort_values("horizon_s")
        ax.plot(grp["horizon_s"], grp[metric], marker="o", label=str(model))
    if "positive_rate" in table:
        base = table.groupby("horizon_s")["positive_rate"].mean().sort_index()
        ax.plot(base.index, base.values, "k--", alpha=0.6, label="prevalence (AUPRC floor)")
    ax.set_xlabel("forecast horizon (s)")
    ax.set_ylabel(metric.upper())
    ax.set_title(f"{metric.upper()} vs forecast horizon")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    path = _fig(out_dir, name)
    fig.tight_layout(); fig.savefig(path); plt.close(fig)
    return str(path)


def plot_reliability(curves: dict, out_dir: Path, name: str = "reliability") -> str | None:
    if not HAVE_MPL or not curves:
        return None
    fig, ax = plt.subplots(figsize=(4.6, 4.4), dpi=150)
    ax.plot([0, 1], [0, 1], "k--", alpha=0.5, label="perfect")
    for label, (conf, acc, _cnt) in curves.items():
        ax.plot(conf, acc, marker="o", ms=3, label=label)
    ax.set_xlabel("predicted probability"); ax.set_ylabel("observed frequency")
    ax.set_title("Reliability diagram"); ax.grid(alpha=0.3); ax.legend(fontsize=8)
    path = _fig(out_dir, name)
    fig.tight_layout(); fig.savefig(path); plt.close(fig)
    return str(path)


def plot_risk_coverage(curves: dict[str, pd.DataFrame], out_dir: Path,
                       name: str = "risk_coverage", risk_col: str = "fn_risk") -> str | None:
    if not HAVE_MPL or not curves:
        return None
    fig, ax = plt.subplots(figsize=(6.0, 4.0), dpi=150)
    for label, df in curves.items():
        if df.empty or risk_col not in df:
            continue
        d = df.sort_values("realised_coverage")
        ax.plot(d["realised_coverage"], d[risk_col], marker="o", label=label)
    ax.set_xlabel("coverage (fraction of samples answered)")
    ax.set_ylabel(risk_col)
    ax.set_title("Risk versus coverage under abstention")
    ax.grid(alpha=0.3); ax.legend(fontsize=8)
    path = _fig(out_dir, name)
    fig.tight_layout(); fig.savefig(path); plt.close(fig)
    return str(path)


def plot_lead_time(event_table: pd.DataFrame, out_dir: Path, name: str = "lead_time") -> str | None:
    if not HAVE_MPL or event_table.empty:
        return None
    fig, ax = plt.subplots(figsize=(6.2, 4.0), dpi=150)
    for model, grp in event_table.groupby("model"):
        grp = grp.sort_values("horizon_s")
        ax.plot(grp["horizon_s"], grp["median_lead_time_s"], marker="s", label=f"{model} lead")
    ax.set_xlabel("forecast horizon (s)"); ax.set_ylabel("median first-warning lead time (s)")
    ax.set_title("Usable warning time per horizon"); ax.grid(alpha=0.3); ax.legend(fontsize=8)
    path = _fig(out_dir, name)
    fig.tight_layout(); fig.savefig(path); plt.close(fig)
    return str(path)


def plot_leakage(inflation: pd.DataFrame, out_dir: Path, name: str = "leakage_inflation",
                 metric: str = "auprc") -> str | None:
    if not HAVE_MPL or inflation.empty:
        return None
    cols = [c for c in ("random_row", "grouped_drive", "external_route") if c in inflation]
    if not cols:
        return None
    fig, ax = plt.subplots(figsize=(6.4, 4.0), dpi=150)
    width = 0.8 / len(cols)
    labels = inflation.apply(lambda r: f"{r.get('model','')}\n{r.get('horizon_s','')}s", axis=1)
    x = np.arange(len(inflation))
    for i, c in enumerate(cols):
        ax.bar(x + i * width, inflation[c], width, label=c)
    ax.set_xticks(x + width * (len(cols) - 1) / 2)
    ax.set_xticklabels(labels, fontsize=7)
    ax.set_ylabel(metric.upper()); ax.set_title("Evaluation protocol vs apparent performance")
    ax.grid(alpha=0.3, axis="y"); ax.legend(fontsize=8)
    path = _fig(out_dir, name)
    fig.tight_layout(); fig.savefig(path); plt.close(fig)
    return str(path)


def write_markdown_report(sections: list[tuple[str, str]], out_path: Path, title: str) -> str:
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"# {title}", "",
             f"_Generated by the hoproj pipeline. Every number below is reproducible from "
             f"`configs/` plus the staged raw capture._", ""]
    for heading, body in sections:
        lines += [f"## {heading}", "", body, ""]
    out_path.write_text("\n".join(lines), encoding="utf-8")
    LOG.info("wrote report %s", out_path)
    return str(out_path)


def df_to_md(df: pd.DataFrame, max_rows: int = 40) -> str:
    if df is None or len(df) == 0:
        return "_(no rows)_"
    shown = df.head(max_rows)
    note = "" if len(df) <= max_rows else f"\n\n_({len(df) - max_rows} further rows in the CSV.)_"
    return shown.to_markdown(index=False, floatfmt=".4f") + note

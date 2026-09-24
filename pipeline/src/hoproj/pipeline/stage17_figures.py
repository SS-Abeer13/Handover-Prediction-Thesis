"""Stage 17 - manuscript figures, regenerated from the pooled dataset.

The mechanism figure is the one that went stale: it was drawn by hand before
the configuration-timeline fix and kept showing a 92.5% trigger coverage after
the corrected number turned out to be 25.3%. Putting it behind a stage means
the picture is recomputed whenever the data is, and the numbers it prints come
from the same frames the tables do.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from ..config import Config, deep_merge, resolve_paths
from ..data.features import select_blocks
from ..data.signalling_features import build_signalling_features
from ..eval.figures import mechanism_figure
from ..utils import get_logger, timed, write_json
from .stage12_xcal_prepare import HORIZONS, capture_config
from .stage13_xcal_benchmark import load_xcal
from .stage16_signalling_pingpong import all_reports

LOG = get_logger("hoproj.stage17")

CANDIDATES = ["serving_dwell_s", "serving_sinr", "t_since_prev_ho_s",
              "gap_serving_nbr1", "serving_rsrp", "serving_rsrq",
              "sig_a3_hold_s", "sig_a3_reports_prev3s", "sig_s_since_a3_report"]


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description="Stage 17: manuscript figures")
    ap.add_argument("--root", default=None)
    ap.add_argument("--horizon", type=float, default=1.0)
    a = ap.parse_args(argv)

    cfg = Config(deep_merge(capture_config("x", "y", HORIZONS), {
        "project": {"paths": {"processed": "data/processed_xcal",
                              "interim": "data/interim_xcal",
                              "reports": "reports_xcal",
                              "artifacts": "artifacts_xcal"}}}))
    paths = resolve_paths(cfg, a.root)
    feats, lab, ho, _ = load_xcal(paths)
    feats = feats.reset_index(drop=True)
    lab = lab.reset_index(drop=True)

    reports = all_reports(Path(paths["interim"]) / "reports_all.parquet")
    with timed("signalling features"):
        sig = build_signalling_features(feats, reports)
    F = pd.concat([feats, sig], axis=1)

    tag = f"h{str(a.horizon).replace('.', 'p')}"
    y = lab[f"y_ho_{tag}"].to_numpy(float)
    m = lab[f"m_ho_{tag}"].to_numpy(bool)
    y = np.where(m, y, np.nan)

    out = Path(paths["reports"]) / "figures" / "fig_mechanism_a3.png"
    parts = mechanism_figure(F, y, ho, reports, out, CANDIDATES)

    tables = Path(paths["reports"]) / "tables"
    tables.mkdir(parents=True, exist_ok=True)
    for name, df in parts.items():
        if isinstance(df, pd.DataFrame) and len(df):
            df.round(4).to_csv(tables / f"mechanism_{name}.csv", index=False)
            (tables / f"mechanism_{name}.md").write_text(df.round(4).to_markdown(index=False))

    prof = parts["profiles"]
    summary = {"figure": str(out), "horizon_s": a.horizon,
               "handover_weighted_trigger_coverage":
                   float(prof["weighted_coverage"].sum() / prof["share_of_handovers"].sum())
                   if len(prof) else None,
               "pooled_never_triggers":
                   float(parts["conversion"].query("capture == 'pooled'")
                         ["never_triggers"].iloc[0])}
    write_json(summary, Path(paths["artifacts"]) / "stage17.json")
    LOG.info("%s", summary)
    LOG.info("\n%s", prof.round(4).to_string(index=False))
    LOG.info("\n%s", parts["single_feature_auroc"].round(4).to_string(index=False))


if __name__ == "__main__":
    main()

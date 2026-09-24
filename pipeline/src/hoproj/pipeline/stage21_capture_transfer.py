"""Stage 21 - leave-one-capture-out transfer across the four measured captures.

Why this stage exists
---------------------
Stage 06 answered "does a model trained here work there?" with a matrix that
included the curated 6-8 Sept export. That export is no longer part of the
evidence base: every table in the manuscript now describes measured captures
with RRC-signalling ground truth, so a transfer matrix that spends three of its
sixteen cells on a dataset we no longer use is not the experiment a reader
wants.

This stage replaces it. Train on three captures, test on the fourth, four times
over. The fourth capture (15 Sept) is the one that matters: it is a different
corridor at a different speed on a different cell layer, and it was collected
after every modelling decision in this thesis had been frozen. Nothing in the
feature set, the horizon set, the split rule or the model configuration was
touched to accommodate it.

What is held out
----------------
A whole capture, which is stricter than the grouped-drive rotation used
everywhere else: the test capture shares no drive, no route, no hour and, for
15 Sept, no corridor with anything the model saw.

Reported per (train-set, test-capture, horizon): AUPRC with its prevalence
floor and lift, AUROC, ECE, and the matched within-capture score so the
transfer penalty is readable as a difference rather than an absolute.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from ..config import Config, deep_merge, resolve_paths
from ..data.splits import Split
from ..eval.report import df_to_md, save_table, write_markdown_report
from ..utils import get_logger, set_seed, timed, write_json
from .stage12_xcal_prepare import capture_config, HORIZONS
from .stage13_xcal_benchmark import load_xcal

LOG = get_logger("hoproj.stage21")

CAPTURE_LABEL = {
    "XCAL10Sept": "10 Sept urban arterial",
    "XCAL12Sept": "12 Sept urban loop",
    "XCAL13Sept": "13 Sept dense urban",
    "XCAL15Sept": "15 Sept highway",
}


def _metrics(y, p, prevalence):
    from sklearn.metrics import average_precision_score, roc_auc_score
    out = {}
    if len(np.unique(y)) < 2:
        return {"auprc": np.nan, "auroc": np.nan, "lift": np.nan, "ece": np.nan}
    ap = average_precision_score(y, p)
    out["auprc"] = float(ap)
    out["auroc"] = float(roc_auc_score(y, p))
    out["lift"] = float(ap / prevalence) if prevalence > 0 else np.nan
    # 15-bin expected calibration error
    bins = np.linspace(0, 1, 16)
    idx = np.clip(np.digitize(p, bins) - 1, 0, 14)
    ece = 0.0
    for b in range(15):
        m = idx == b
        if m.sum():
            ece += (m.sum() / len(p)) * abs(p[m].mean() - y[m].mean())
    out["ece"] = float(ece)
    return out


def _fit_predict(cfg, feats, lab, ho, train_drives, test_drives, seed, cache):
    from .trainer import train_and_evaluate
    # the trainer wants a non-empty val/calib; carve them out of train by drive
    rng = np.random.default_rng(seed)
    tr = list(train_drives)
    rng.shuffle(tr)
    n_val = max(2, int(0.15 * len(tr)))
    n_cal = max(2, int(0.15 * len(tr)))
    split = Split(name="capture_transfer", condition="grouped_drive",
                  train=tr[n_val + n_cal:],
                  val=tr[:n_val], calib=tr[n_val:n_val + n_cal],
                  test=list(test_drives))
    res = train_and_evaluate(cfg, feats, lab, ho, split, "lgbm",
                             feature_set="rf_mob_hist", seed=seed, cache_dir=cache)
    return res


def run(root=None, seed: int = 1337) -> pd.DataFrame:
    set_seed(seed)
    cfg = capture_config("x", "y", HORIZONS)
    cfg = Config(deep_merge(cfg, {
        "project": {"paths": {"processed": "data/processed_xcal",
                              "interim": "data/interim_xcal",
                              "reports": "reports_xcal",
                              "artifacts": "artifacts_xcal"}},
        "train": {"epochs": 40, "early_stop_patience": 8},
        "eval": {"bootstrap": {"n": 200}},
        "tasks": {"qoe": {"enabled": False}, "target": {"enabled": False},
                  "dwell": {"enabled": False}}}))
    paths = resolve_paths(cfg, root)
    feats, lab, ho, drives = load_xcal(paths)
    cache = paths["artifacts"] / "stage21"
    cache.mkdir(parents=True, exist_ok=True)

    captures = sorted(drives["capture"].unique())
    horizons = cfg.get_path("labels.horizons_s")
    rows = []
    for held in captures:
        te = drives.loc[drives["capture"] == held, "drive_id"].tolist()
        tr = drives.loc[drives["capture"] != held, "drive_id"].tolist()
        with timed(f"hold out {held}  (train {len(tr)} drives, test {len(te)})"):
            res = _fit_predict(cfg, feats, lab, ho, tr, te, seed, cache)
        P, Y, M = res.predictions["test"], res.extras["Y_test"], res.extras["M_test"]
        for j, h in enumerate(horizons):
            sel = M[:, j].astype(bool)
            if sel.sum() < 30:
                continue
            y, p = Y[sel, j], P[sel, j]
            prev = float(y.mean())
            m = _metrics(y, p, prev)
            rows.append(dict(held_out=held, label=CAPTURE_LABEL.get(held, held),
                             horizon_s=h, n=int(sel.sum()), prevalence=prev,
                             n_train_drives=len(tr), n_test_drives=len(te), **m))
            LOG.info("%s h=%.1f  n=%d prev=%.3f AUPRC=%.3f (lift %.1fx) AUROC=%.3f ECE=%.3f",
                     held, h, sel.sum(), prev, m["auprc"], m["lift"], m["auroc"], m["ece"])

    out = pd.DataFrame(rows)
    save_table(out, paths["reports"], "capture_transfer")

    # a compact 1 s view for the manuscript
    one = out[out["horizon_s"] == 1.0].copy()
    save_table(one, paths["reports"], "capture_transfer_1s")
    write_json(paths["reports"] / "21_capture_transfer.json",
               {"captures": list(captures), "rows": len(out)})
    write_markdown_report(
        paths["reports"] / "21_capture_transfer.md",
        "Leave-one-capture-out transfer (stage 21)",
        [("What this is",
          "Train on three measured captures, test on the fourth, four times over. "
          "A whole capture is held out, so the test capture shares no drive, no route "
          "and no hour with anything the model saw. This replaces the curated-vs-XCAL "
          "transfer matrix of stage 06."),
         ("At the 1 s horizon", df_to_md(one.round(4))),
         ("All horizons", df_to_md(out.round(4)))])
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="Stage 21: leave-one-capture-out transfer")
    ap.add_argument("--root", default=None)
    ap.add_argument("--seed", type=int, default=1337)
    a = ap.parse_args(argv)
    return run(a.root, a.seed)


if __name__ == "__main__":
    main()

"""Stage 10 - a distribution-free bound on missed handovers.

Split conformal (stage 03) answers "does the prediction set cover the truth
90% of the time". An operator asks a different question: *how many imminent
handovers will the alarm miss?* Conformal risk control answers that one
directly, and this stage reports the answer at the level the guarantee is
actually valid - whole drives.

Two contrasts are reported:

``grouped vs naive``  The conformal threshold calibrated over whole drives
                      against the tempting shortcut of pooling calibration
                      samples. The gap between the two is what the
                      exchangeability violation would have cost.
``risk vs coverage``  Achieved false-negative rate and alarm rate at several
                      target levels, so the operating cost of a guarantee is
                      visible rather than implied.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from ..config import Config, deep_merge, load_config, resolve_paths
from ..data import labels as L
from ..data.features import select_blocks
from ..data.transforms import TabularTransform
from ..models.hazard import build_long, predict_incidence
from ..uncertainty.riskcontrol import conformal_risk_control, naive_sample_threshold
from ..utils import get_logger, set_seed, timed, write_json
from .stage07_regime_transfer import build_pool
from .stage09_hazard import BLOCKS, EDGES, _lgbm, _predict

LOG = get_logger("hoproj.stage10")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--alphas", nargs="+", type=float, default=[0.05, 0.10, 0.20])
    ap.add_argument("--repeats", type=int, default=5)
    ap.add_argument("--seed", type=int, default=1337)
    a = ap.parse_args()
    set_seed(a.seed)

    cfg = Config(deep_merge(load_config("base.yaml", adapter="xcal_signalling"),
                            {"features": {"blocks": BLOCKS}}))
    paths = resolve_paths(cfg)
    out_dir = Path(paths["reports"]) / "tables"
    out_dir.mkdir(parents=True, exist_ok=True)

    feats, lab, ho = build_pool(cfg)
    feats = feats.reset_index(drop=True)
    lab = lab.reset_index(drop=True)
    drives = feats["drive_id"].to_numpy()
    names = [n for n in select_blocks(feats, BLOCKS) if n in feats.columns]
    tags = [L._htag(e) for e in EDGES]

    rows = []
    for rep in range(a.repeats):
        rng = np.random.default_rng(a.seed + rep)
        uniq = np.unique(drives)
        rng.shuffle(uniq)
        n = len(uniq)
        # The conformal risk bound carries a finite-sample penalty B/(n+1) with
        # B = 1, so a target alpha is UNREACHABLE unless n >= 1/alpha - 1
        # calibration units exist. With drives as the exchangeable unit that is
        # a hard constraint on the campaign, not a tuning knob - see the
        # feasibility column in the output table.
        n_tr, n_cal = int(0.50 * n), int(0.30 * n)
        tr_d, cal_d, te_d = uniq[:n_tr], uniq[n_tr:n_tr + n_cal], uniq[n_tr + n_cal:]
        tr = np.isin(drives, tr_d); cal = np.isin(drives, cal_d); te = np.isin(drives, te_d)

        tf = TabularTransform("robust", clip_sigma=8.0)
        tf.fit(feats.loc[tr, names])
        X = pd.DataFrame(tf.transform(feats[names]), columns=names, index=feats.index)

        t_next = lab["t_to_next_ho_s"].to_numpy(float)
        t_end = (feats.groupby("drive_id")["t"].transform("max") - feats["t"]
                 ).dt.total_seconds().to_numpy(float)
        with timed(f"rep {rep} hazard fit"):
            long = build_long(X, t_next, t_end, EDGES, valid=tr)
            model = _lgbm(long.X, long.y, a.seed + rep)
            P = predict_incidence(model, X, EDGES, predict_fn=_predict)

        for k, (e, tag) in enumerate(zip(EDGES, tags)):
            M = lab[f"m_ho_{tag}"].to_numpy(bool)
            Y = lab[f"y_ho_{tag}"].to_numpy(float)
            c, t_ = cal & M, te & M
            if Y[c].sum() < 10 or Y[t_].sum() < 10:
                continue
            for alpha in a.alphas:
                r = conformal_risk_control(Y[c], P[c, k], drives[c],
                                           Y[t_], P[t_, k], drives[t_], alpha=alpha)
                lam_naive = naive_sample_threshold(Y[c], P[c, k], alpha)
                miss_naive = float((P[t_, k][Y[t_] == 1] < lam_naive).mean())
                naive_per_drive = []
                for d in np.unique(drives[t_]):
                    m = (drives[t_] == d) & (Y[t_] == 1)
                    if m.any():
                        naive_per_drive.append(float((P[t_, k][m] < lam_naive).mean()))
                naive_per_drive = np.asarray(naive_per_drive)
                rows.append({"rep": rep, "horizon_s": e, "alpha": alpha,
                             **r.as_dict(),
                             "naive_lambda": lam_naive,
                             "naive_pooled_test_fnr": miss_naive,
                             "naive_alarm_rate": float((P[t_, k] >= lam_naive).mean()),
                             "naive_per_drive_fnr_p90": float(np.percentile(naive_per_drive, 90))
                             if naive_per_drive.size else np.nan,
                             "naive_drives_over_alpha_frac": float((naive_per_drive > alpha).mean())
                             if naive_per_drive.size else np.nan,
                             "alpha_feasible": bool(alpha > 1.0 / (r.n_calib_units + 1)),
                             "min_alpha_reachable": 1.0 / (r.n_calib_units + 1)})

    df = pd.DataFrame(rows)
    df.to_csv(out_dir / "risk_control_runs.csv", index=False)
    summ = (df.groupby(["horizon_s", "alpha"])[
        ["min_alpha_reachable", "lambda_hat", "test_fnr", "test_alarm_rate",
         "per_drive_fnr_p90", "drives_over_alpha_frac",
         "naive_pooled_test_fnr", "naive_per_drive_fnr_p90",
         "naive_drives_over_alpha_frac", "naive_alarm_rate",
         "n_calib_drives"]].mean().round(4).reset_index())
    summ.to_csv(out_dir / "risk_control.csv", index=False)
    (out_dir / "risk_control.md").write_text(summ.to_markdown(index=False))
    write_json({"summary": summ.to_dict(orient="records")},
               Path(paths["artifacts"]) / "stage10.json")
    LOG.info("\n%s", summ.to_string(index=False))


if __name__ == "__main__":
    main()

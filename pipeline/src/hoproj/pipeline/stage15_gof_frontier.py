"""Stage 15 - does the Hawkes model fit, and what does the CRC guarantee cost?

Two claims from stage 09 / stage 10 are stated without the evidence a reviewer
needs, and this stage supplies it.

**C2, self-excitation.** A branching ratio of 0.61 is a fitted parameter of an
assumed model. Reporting it without a goodness-of-fit test asserts that
handovers are self-exciting; it does not show it. Three checks:

* *Ogata residuals.* Under the fitted model the compensator
  ``Lambda(t) = int_0^t lambda(s) ds`` rescales event times into a unit-rate
  Poisson process, so the rescaled inter-event times must be Exp(1). A
  Kolmogorov-Smirnov test against Exp(1) is the direct test of fit.
* *Likelihood ratio against homogeneous Poisson.* alpha = 0 is a boundary of the
  parameter space, so the asymptotic null is the 50:50 mixture
  ``0.5 chi2_0 + 0.5 chi2_1`` (Self & Liang 1987), not chi2_2. Using chi2_2
  would make the test conservative, but stating the right null costs nothing.
* *Parametric bootstrap CI.* Simulate from the fitted process over the observed
  drive durations (Ogata thinning), refit, and take the empirical quantiles of
  n = alpha/beta. The stage 09 "+/- 0.04" was the spread across three captures,
  which is a different quantity.

A renewal alternative is also fitted. If a gamma renewal process explains the
clustering as well as self-excitation does, then "self-exciting" is the wrong
word for it and the contribution needs rewording.

**C3, conformal risk control.** The guarantee holds; the question is what it
costs. At alpha = 0.1 the certified threshold alarmed on 59-86% of samples,
which is a valid bound and a useless operating point. This stage sweeps alpha,
reports the alarm rate it buys at every level, and runs the procedure on the
hazard model's incidence - better calibrated than the multi-head predictions it
used before - with calibration drives pooled across all three captures so the
feasibility floor n >= 1/alpha - 1 stops binding so early.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from ..config import Config, deep_merge, resolve_paths
from ..data.features import select_blocks
from ..data.selfexcite import fit_hawkes
from ..data.transforms import TabularTransform
from ..models.hazard import build_long, predict_incidence
from ..uncertainty.riskcontrol import conformal_risk_control, naive_sample_threshold
from ..utils import get_logger, set_seed, timed, write_json
from .stage12_xcal_prepare import HORIZONS, capture_config
from .stage13_xcal_benchmark import load_xcal
from .stage14_hazard_fair import _htags, _lgbm

LOG = get_logger("hoproj.stage15")

BLOCKS = ["rf", "mobility", "history"]
ALPHAS = [0.05, 0.10, 0.15, 0.20, 0.30, 0.40]


# ------------------------------------------------------------------- Hawkes
def _realisations(ho: pd.DataFrame, feats: pd.DataFrame) -> list[tuple[np.ndarray, float]]:
    spans = feats.groupby("drive_id")["t"].agg(["min", "max"])
    out = []
    for g, span in spans.iterrows():
        T = (span["max"] - span["min"]).total_seconds()
        if T <= 0:
            continue
        ev = ho.loc[ho["drive_id"] == g, "t"]
        ts = np.sort((ev - span["min"]).dt.total_seconds().to_numpy()) if len(ev) else np.empty(0)
        out.append((ts[(ts >= 0) & (ts <= T)], float(T)))
    return out


def rescaled_times(ts: np.ndarray, mu: float, alpha: float, beta: float) -> np.ndarray:
    """Ogata's residuals: Lambda(t_i) increments, which are Exp(1) under the model.

    For the exponential kernel the compensator has a closed form,

        Lambda(t) = mu t + (alpha/beta) sum_i [1 - exp(-beta (t - t_i))],

    so the increments between consecutive events need no numerical integration.
    """
    if ts.size < 2:
        return np.empty(0)
    r = alpha / beta

    def Lam(t):
        past = ts[ts < t]
        return mu * t + r * np.sum(1.0 - np.exp(-beta * (t - past)))

    L = np.array([Lam(t) for t in ts])
    return np.diff(L)


def simulate_hawkes(mu: float, alpha: float, beta: float, T: float,
                    rng: np.random.Generator) -> np.ndarray:
    """Ogata thinning. Returns event times on [0, T]."""
    ts: list[float] = []
    t = 0.0
    while t < T:
        lam_bar = mu + alpha * np.sum(np.exp(-beta * (t - np.asarray(ts)))) if ts else mu
        lam_bar = max(lam_bar, 1e-9)
        t = t - np.log(rng.random()) / lam_bar
        if t >= T:
            break
        lam = mu + (alpha * np.sum(np.exp(-beta * (t - np.asarray(ts)))) if ts else 0.0)
        if rng.random() <= lam / lam_bar:
            ts.append(t)
    return np.asarray(ts)


def hawkes_gof(ho: pd.DataFrame, feats: pd.DataFrame, n_boot: int, seed: int) -> dict:
    from scipy import stats

    fit = fit_hawkes(ho, feats)
    mu, alpha, beta = fit.mu, fit.alpha, fit.beta
    reals = _realisations(ho, feats)

    # --- Ogata residuals, pooled across drives
    resid = np.concatenate([rescaled_times(ts, mu, alpha, beta)
                            for ts, _ in reals if ts.size >= 2]) if reals else np.empty(0)
    ks = stats.kstest(resid, "expon") if resid.size > 10 else None

    # --- LR against homogeneous Poisson (alpha = 0). Boundary null.
    total_T = sum(T for _, T in reals)
    n_ev = sum(ts.size for ts, _ in reals)
    rate = n_ev / total_T if total_T else np.nan
    ll_pois = n_ev * np.log(rate) - rate * total_T if rate > 0 else np.nan
    lr = 2.0 * (fit.loglik - ll_pois)
    # 0.5 chi2_0 + 0.5 chi2_1 mixture, so p = 0.5 * P(chi2_1 > lr)
    p_lr = 0.5 * float(stats.chi2.sf(lr, 1)) if np.isfinite(lr) and lr > 0 else 1.0

    # --- gamma renewal alternative on inter-event times
    gaps = np.concatenate([np.diff(ts) for ts, _ in reals if ts.size >= 2])
    renewal = {}
    if gaps.size > 20:
        shape, loc, scale = stats.gamma.fit(gaps, floc=0)
        ll_gamma = float(np.sum(stats.gamma.logpdf(gaps, shape, loc=loc, scale=scale)))
        ll_exp = float(np.sum(stats.expon.logpdf(gaps, loc=0, scale=gaps.mean())))
        renewal = {"gamma_shape": float(shape), "gamma_scale": float(scale),
                   "gamma_loglik": ll_gamma, "exponential_loglik": ll_exp,
                   "gamma_ks_p": float(stats.kstest(gaps, "gamma",
                                                    args=(shape, loc, scale)).pvalue),
                   "note": "shape > 1 = regular, < 1 = clustered inter-event times"}

    # --- parametric bootstrap CI on the branching ratio
    rng = np.random.default_rng(seed)
    ns = []
    for _ in range(n_boot):
        sim = []
        for _, T in reals:
            sim.append((simulate_hawkes(mu, alpha, beta, T, rng), T))
        try:
            from ..data.selfexcite import _nll
            from scipy.optimize import minimize
            x0 = np.log([max(mu, 1e-6), max(alpha, 1e-6), max(beta, 1e-6)])
            r = minimize(_nll, x0, args=(sim,), method="Nelder-Mead",
                         options={"maxiter": 2000, "xatol": 1e-5, "fatol": 1e-5})
            m_, a_, b_ = np.exp(r.x)
            ns.append(a_ / b_)
        except Exception:                                       # noqa: BLE001
            continue
    ci = (float(np.quantile(ns, 0.025)), float(np.quantile(ns, 0.975))) if len(ns) > 20 \
        else (np.nan, np.nan)

    return {**fit.as_dict(),
            "ogata_ks_stat": float(ks.statistic) if ks else np.nan,
            "ogata_ks_p": float(ks.pvalue) if ks else np.nan,
            "n_residuals": int(resid.size),
            "loglik_poisson": float(ll_pois),
            "lr_stat_vs_poisson": float(lr),
            "lr_p_boundary_mixture": p_lr,
            "branching_ci_low": ci[0], "branching_ci_high": ci[1],
            "n_bootstrap": len(ns), **renewal}


# ----------------------------------------------------------- CRC frontier
def hazard_oof(feats: pd.DataFrame, lab: pd.DataFrame, edges: list[float],
               k: int, seed: int) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Out-of-fold hazard incidence over every drive, for honest CRC input."""
    names = [n for n in select_blocks(feats, BLOCKS) if n in feats.columns]
    drives = feats["drive_id"].to_numpy()
    tags = _htags(edges)
    Y = np.column_stack([lab[f"y_ho_{t}"].to_numpy(float) for t in tags])
    M = np.column_stack([lab[f"m_ho_{t}"].to_numpy(bool) for t in tags])
    t_next = lab["t_to_next_ho_s"].to_numpy(float)
    t_end = (feats.groupby("drive_id")["t"].transform("max") - feats["t"]
             ).dt.total_seconds().to_numpy(float)

    P = np.zeros_like(Y)
    rng = np.random.default_rng(seed)
    uniq = np.unique(drives)
    rng.shuffle(uniq)
    for hold in np.array_split(uniq, k):
        te = np.isin(drives, hold)
        tr = ~te
        tf = TabularTransform("robust", clip_sigma=8.0)
        tf.fit(feats.loc[tr, names])
        X = pd.DataFrame(tf.transform(feats[names]), columns=names, index=feats.index)
        long = build_long(X, t_next, t_end, edges, valid=tr)
        m = _lgbm(long.X, long.y, seed)
        Pi = predict_incidence(m, X, edges, predict_fn=lambda mm, z: mm.predict(z))
        P[te] = Pi[te]
    return P, Y, M, drives


def crc_frontier(P, Y, M, drives, edges, alphas, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    uniq = np.unique(drives)
    rng.shuffle(uniq)
    n_cal = int(round(0.5 * len(uniq)))
    cal_ids, te_ids = set(uniq[:n_cal]), set(uniq[n_cal:])
    cal = np.array([d in cal_ids for d in drives])
    te = np.array([d in te_ids for d in drives])

    rows = []
    for k, e in enumerate(edges):
        mk = M[:, k].astype(bool)
        c, t = cal & mk, te & mk
        if c.sum() < 100 or t.sum() < 100:
            continue
        for alpha in alphas:
            r = conformal_risk_control(Y[c, k], P[c, k], drives[c],
                                       Y[t, k], P[t, k], drives[t], alpha=alpha)
            lam_naive = naive_sample_threshold(Y[c, k], P[c, k], alpha)
            alarm_naive = float((P[t, k] >= lam_naive).mean())
            per = r.per_unit_test_risk[np.isfinite(r.per_unit_test_risk)]
            rows.append({
                "horizon_s": e, "alpha": alpha,
                "min_alpha_reachable": 1.0 / (len(np.unique(drives[c])) + 1),
                "lambda_hat": r.lambda_hat, "test_fnr": r.test_risk,
                "test_alarm_rate": r.test_alarm_rate,
                "per_drive_fnr_p90": float(np.quantile(per, 0.9)) if per.size else np.nan,
                "drives_over_alpha_frac": float((per > alpha).mean()) if per.size else np.nan,
                "naive_lambda": lam_naive, "naive_alarm_rate": alarm_naive,
                "n_calib_drives": int(len(np.unique(drives[c]))),
                "n_test_drives": int(len(np.unique(drives[t])))})
    return pd.DataFrame(rows)


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description="Stage 15: Hawkes GOF + CRC frontier")
    ap.add_argument("--root", default=None)
    ap.add_argument("--boot", type=int, default=200)
    ap.add_argument("--folds", type=int, default=4)
    ap.add_argument("--seed", type=int, default=1337)
    ap.add_argument("--skip-gof", action="store_true")
    ap.add_argument("--skip-crc", action="store_true")
    a = ap.parse_args(argv)
    set_seed(a.seed)

    cfg = Config(deep_merge(capture_config("x", "y", HORIZONS), {
        "project": {"paths": {"processed": "data/processed_xcal",
                              "interim": "data/interim_xcal",
                              "reports": "reports_xcal",
                              "artifacts": "artifacts_xcal"}}}))
    paths = resolve_paths(cfg, a.root)
    out_dir = Path(paths["reports"]) / "tables"
    out_dir.mkdir(parents=True, exist_ok=True)
    feats, lab, ho, _ = load_xcal(paths)
    feats = feats.reset_index(drop=True)
    lab = lab.reset_index(drop=True)

    payload = {}
    if not a.skip_gof:
        gof = {}
        with timed("Hawkes GOF pooled"):
            gof["pooled"] = hawkes_gof(ho, feats, a.boot, a.seed)
        for cap, g in ho.groupby("capture"):
            sub = feats[feats["capture"] == cap]
            try:
                with timed(f"Hawkes GOF {cap}"):
                    gof[str(cap)] = hawkes_gof(g, sub, max(a.boot // 2, 50), a.seed)
            except Exception as exc:                            # noqa: BLE001
                LOG.warning("GOF failed for %s: %s", cap, exc)
        tbl = pd.DataFrame(gof).T
        tbl.to_csv(out_dir / "hawkes_goodness_of_fit.csv")
        (out_dir / "hawkes_goodness_of_fit.md").write_text(tbl.round(4).to_markdown())
        payload["hawkes_gof"] = gof
        LOG.info("\n%s", tbl[["branching_ratio", "branching_ci_low", "branching_ci_high",
                              "ogata_ks_p", "lr_p_boundary_mixture"]].round(4).to_string())

    if not a.skip_crc:
        with timed("out-of-fold hazard incidence"):
            P, Y, M, drives = hazard_oof(feats, lab, HORIZONS, a.folds, a.seed)
        front = crc_frontier(P, Y, M, drives, HORIZONS, ALPHAS, a.seed)
        front.round(4).to_csv(out_dir / "risk_control_frontier.csv", index=False)
        (out_dir / "risk_control_frontier.md").write_text(
            front.round(4).to_markdown(index=False))
        payload["crc_rows"] = int(len(front))
        LOG.info("\n%s", front.round(3).to_string(index=False))

    write_json(payload, Path(paths["artifacts"]) / "stage15.json")


if __name__ == "__main__":
    main()

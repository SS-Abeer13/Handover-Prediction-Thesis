"""Stage 19 - zero-cost domain adaptation on every transfer we report (doc 19, item K).

The reviewer question is short: *"you report a transfer loss and then attempt no
domain adaptation at all?"*

Two adaptation methods are tried, both **unsupervised** - they use only the
target domain's *features*, never its labels, and never a fitted model from the
target side. That is what makes them zero-cost: a deployed UE could apply either
one without any target-side ground truth.

``per_drive_z``   Each drive is standardised by its own robust location and
                  scale, on both sides of the transfer. This removes per-device
                  and per-session offsets (antenna gain, receiver calibration,
                  the ambient level of a route) while leaving within-drive
                  dynamics - which is where the predictive signal lives - intact.

``coral``         CORrelation ALignment: the target features are whitened by the
                  target covariance and recoloured by the source covariance, with
                  the means matched. Ten lines, no training, aligns first and
                  second moments of the two feature distributions.

Both are applied *after* the source-fitted scaler, so the ``none`` arm is exactly
the protocol of stages 07 and 08 and the arms differ only by the adaptation.

Two transfer settings are covered, the same two the manuscript reports:

``regime``    within-campaign configuration-regime transfer (stage 07's design):
              city, UE, driver, route and day held fixed, the A3 parameters vary.
``external``  the pooled XCAL captures against the public IUT/Mendeley dataset,
              both directions (stage 08's design): different route, different
              people, two years earlier.
"""
from __future__ import annotations

import argparse
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

from ..config import Config, deep_merge, load_config, resolve_paths
from ..data import labels as L
from ..data.features import select_blocks
from ..data.transforms import TabularTransform
from ..data.windows import build_window_index, materialise
from ..eval import metrics as MET
from ..eval import report as RPT
from ..models.registry import build_model
from ..utils import get_logger, set_seed, timed, write_json

LOG = get_logger("hoproj.stage19")

ADAPTATIONS = ("none", "per_drive_z", "coral")
LGBM_PARAMS = {"n_jobs": 1}          # stage 18 may be running on the other core


# --------------------------------------------------------------- adaptation ops
def per_drive_z(X: np.ndarray, drive_ids: np.ndarray) -> np.ndarray:
    """Robust per-drive standardisation. Uses only that drive's own rows."""
    out = X.astype(np.float32, copy=True)
    for d in np.unique(drive_ids):
        sel = drive_ids == d
        block = out[sel]
        med = np.nanmedian(block, axis=0)
        q1, q3 = np.nanpercentile(block, [25, 75], axis=0)
        scale = (q3 - q1) / 1.349
        scale[~np.isfinite(scale) | (scale < 1e-6)] = 1.0
        med[~np.isfinite(med)] = 0.0
        out[sel] = (block - med) / scale
    return np.nan_to_num(out, nan=0.0, posinf=0.0, neginf=0.0)


def _sqrtm_psd(C: np.ndarray, power: float, eps: float = 1e-5) -> np.ndarray:
    w, V = np.linalg.eigh(C + eps * np.eye(C.shape[0], dtype=C.dtype))
    w = np.clip(w, eps, None) ** power
    return (V * w) @ V.T


def coral(Xs_train: np.ndarray, Xt: np.ndarray) -> np.ndarray:
    """Align the TARGET onto the source: whiten by C_t, recolour by C_s.

    Aligning the target (rather than the source) keeps one trained model per
    source domain, so the comparison across targets is between predictions of
    the same fitted model.
    """
    Xs = np.nan_to_num(Xs_train.astype(np.float64))
    Xt = np.nan_to_num(Xt.astype(np.float64))
    ms, mt = Xs.mean(0), Xt.mean(0)
    Cs = np.cov(Xs - ms, rowvar=False)
    Ct = np.cov(Xt - mt, rowvar=False)
    A = _sqrtm_psd(Ct, -0.5) @ _sqrtm_psd(Cs, 0.5)
    return np.nan_to_num(((Xt - mt) @ A + ms).astype(np.float32))


def adapt(kind: str, X_src_tr: np.ndarray, X_src_all: np.ndarray, X_tgt: np.ndarray,
          src_drives: np.ndarray, tgt_drives: np.ndarray):
    """Return (source matrix for fitting, target matrix for scoring)."""
    if kind == "none":
        return X_src_all, X_tgt
    if kind == "per_drive_z":
        return per_drive_z(X_src_all, src_drives), per_drive_z(X_tgt, tgt_drives)
    if kind == "coral":
        return X_src_all, coral(X_src_tr, X_tgt)
    raise KeyError(kind)


def _fit_lgbm(cfg, X, Y, M, n_horizons, seed):
    set_seed(seed)
    mdl = build_model("lgbm", cfg, X.shape[1], n_horizons, seed=seed, params=LGBM_PARAMS)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        mdl.fit(X, Y, masks=M)
    return mdl


def _score(Y, P, M, horizons) -> pd.DataFrame:
    return MET.multi_horizon_table(Y, P, M, horizons, (0.01, 0.05, 0.10))


# ------------------------------------------------------------- regime transfer
def regime_experiment(cfg: Config, seed: int) -> pd.DataFrame:
    from .stage07_regime_transfer import BLOCKS, build_pool, _regime_key

    F, Y, H = build_pool(cfg)
    # build_pool composes its own capture config (stage 07's), which does not
    # enable sub-period horizons; take the horizons the pooled labels actually
    # carry rather than the ones this stage's config asks for.
    all_h = cfg.get_path("labels.horizons_s")
    pairs = [(h, t) for h, t in zip(all_h, L.horizon_tags(cfg))
             if f"y_ho_{t}" in Y.columns]
    horizons = [h for h, _ in pairs]
    period = float(cfg.get_path("data.target_period_s") or 1.0)
    L_win = max(2, int(round(float(cfg.get_path("windows.length_s", 10.0)) / period)))
    stride = max(1, int(round(float(cfg.get_path("windows.stride_s", 1.0)) / period)))
    names = [n for n in select_blocks(F, BLOCKS) if n in F.columns]

    wi = build_window_index(F, L_win, stride, 0.0,
                            F["is_interpolated"].to_numpy(bool) if "is_interpolated" in F else None)
    tags = [t for _, t in pairs]
    Ym = np.column_stack([Y[f"y_ho_{t}"].to_numpy(np.float32) for t in tags])[wi.end_pos]
    Mm = np.column_stack([Y[f"m_ho_{t}"].to_numpy(np.float32) for t in tags])[wi.end_pos]
    reg_rows = F["regime"].to_numpy()[wi.end_pos]
    drive_rows = F["drive_id"].to_numpy()[wi.end_pos]

    rng = np.random.default_rng(seed)
    all_d = np.unique(drive_rows)
    rng.shuffle(all_d)
    val_d = set(all_d[:max(2, int(round(0.30 * len(all_d))))].tolist())
    held = np.isin(drive_rows, list(val_d))

    regimes = sorted(set(H["regime"]))
    rows = []
    for src in regimes:
        src_tr = (reg_rows == src) & ~held
        if src_tr.sum() < 300:
            continue
        tf = TabularTransform(cfg.get_path("features.scaler", "robust"),
                              clip_sigma=float(cfg.get_path("features.clip_sigma", 8.0)))
        tf.fit(F.loc[wi.end_pos[src_tr], names])
        X = np.asarray(tf.transform(F[names]))[wi.end_pos]

        for a in ADAPTATIONS:
            for tgt in regimes:
                sel = (reg_rows == tgt) & held
                j1 = horizons.index(1.0) if 1.0 in horizons else 0
                if sel.sum() < 200 or len(np.unique(Ym[sel][:, j1])) < 2:
                    continue
                Xs_fit, Xt = adapt(a, X[src_tr], X, X[sel], drive_rows, drive_rows[sel])
                with timed(f"regime {src}->{tgt} [{a}]"):
                    mdl = _fit_lgbm(cfg, Xs_fit[src_tr], Ym[src_tr], Mm[src_tr],
                                    len(horizons), seed)
                    P = mdl.predict_proba(Xt)
                tbl = _score(Ym[sel], P, Mm[sel], horizons)
                tbl.insert(0, "experiment", "regime")
                tbl.insert(1, "adaptation", a)
                tbl.insert(2, "source", src)
                tbl.insert(3, "target", tgt)
                tbl.insert(4, "matched", src == tgt)
                rows.append(tbl)
    return pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()


# ----------------------------------------------------------- external transfer
def external_experiment(cfg: Config, public_root: Path, seed: int) -> pd.DataFrame:
    from .stage06_cross_capture import _matrices, prepare
    from .stage08_public_dataset import CAPTURES, build_domain

    BLOCKS_X = ["rf", "history"]                    # no GPS/speed in the public data
    pub = build_domain(public_root)
    ours = []
    for name, raw, csv, sig in CAPTURES:
        ours.append(prepare(name, "xcal_signalling", Path(raw),
                            {"samples": csv, "signalling": sig},
                            overrides={"features": {"blocks": BLOCKS_X},
                                       "segmentation": {"method": "fixed_duration",
                                                        "fixed_duration_s": 180,
                                                        "route_from": "config"},
                                       "qc": {"min_drive_duration_s": 60,
                                              "min_drive_samples": 60}}))

    # pool our three captures into one domain
    from .stage06_cross_capture import Domain
    mine = Domain("XCAL pooled",
                  pd.concat([d.features for d in ours], ignore_index=True),
                  pd.concat([d.labels for d in ours], ignore_index=True),
                  pd.concat([d.ho for d in ours], ignore_index=True),
                  pd.concat([d.drives for d in ours], ignore_index=True),
                  ours[0].horizons, ours[0].tags)
    mine.features.attrs = dict(ours[0].features.attrs)

    period = float(cfg.get_path("data.target_period_s") or 1.0)
    L_win = max(2, int(round(float(cfg.get_path("windows.length_s", 10.0)) / period)))
    stride = max(1, int(round(float(cfg.get_path("windows.stride_s", 1.0)) / period)))

    rows = []
    for source, target in ((mine, pub), (pub, mine)):
        names = [n for n in select_blocks(source.features, BLOCKS_X)
                 if n in source.features.columns and n in target.features.columns]
        horizons = [h for h in source.horizons if h in target.horizons]
        hidx_s = [source.horizons.index(h) for h in horizons]
        hidx_t = [target.horizons.index(h) for h in horizons]
        LOG.info("external %s -> %s: %d shared features, horizons %s",
                 source.name, target.name, len(names), horizons)

        rng = np.random.default_rng(seed)
        ids = source.drives["drive_id"].to_numpy().copy()
        rng.shuffle(ids)
        train_ids = set(ids[max(1, int(round(0.25 * len(ids)))):])

        tf = TabularTransform(cfg.get_path("features.scaler", "robust"),
                              clip_sigma=float(cfg.get_path("features.clip_sigma", 8.0)))
        tr_mask_rows = source.features["drive_id"].isin(train_ids).to_numpy()
        tf.fit(source.features.loc[tr_mask_rows, names])

        wi_s, Ys, Ms = _matrices(source, names, L_win, stride)
        Xs = np.asarray(tf.transform(source.features[names]))[wi_s.end_pos]
        Ys, Ms = Ys[wi_s.end_pos][:, hidx_s], Ms[wi_s.end_pos][:, hidx_s]
        ds = source.features["drive_id"].to_numpy()[wi_s.end_pos]
        keep_tr = tr_mask_rows[wi_s.end_pos]

        wi_t, Yt, Mt = _matrices(target, names, L_win, stride)
        Xt = np.asarray(tf.transform(target.features[names]))[wi_t.end_pos]
        Yt, Mt = Yt[wi_t.end_pos][:, hidx_t], Mt[wi_t.end_pos][:, hidx_t]
        dt = target.features["drive_id"].to_numpy()[wi_t.end_pos]

        for a in ADAPTATIONS:
            Xs_fit, Xt_use = adapt(a, Xs[keep_tr], Xs, Xt, ds, dt)
            with timed(f"external {source.name}->{target.name} [{a}]"):
                mdl = _fit_lgbm(cfg, Xs_fit[keep_tr], Ys[keep_tr], Ms[keep_tr],
                                len(horizons), seed)
                P_t = mdl.predict_proba(Xt_use)
                P_s = mdl.predict_proba(Xs_fit[~keep_tr])
            for tag, (Yv, Pv, Mv) in (("transfer", (Yt, P_t, Mt)),
                                      ("in_domain_holdout", (Ys[~keep_tr], P_s, Ms[~keep_tr]))):
                tbl = _score(Yv, Pv, Mv, horizons)
                tbl.insert(0, "experiment", "external")
                tbl.insert(1, "adaptation", a)
                tbl.insert(2, "source", source.name)
                tbl.insert(3, "target", target.name if tag == "transfer" else source.name)
                tbl.insert(4, "matched", tag != "transfer")
                rows.append(tbl)
    return pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()


def summarise(df: pd.DataFrame, horizon: float = 1.0) -> pd.DataFrame:
    """Matched vs mismatched AUROC per adaptation, and the transfer gap."""
    d = df[df["horizon_s"] == horizon]
    out = []
    for (exp, a), g in d.groupby(["experiment", "adaptation"]):
        m = g[g["matched"]]["auroc"].mean()
        x = g[~g["matched"]]["auroc"].mean()
        mp = g[g["matched"]]["auprc"].mean()
        xp = g[~g["matched"]]["auprc"].mean()
        out.append({"experiment": exp, "adaptation": a, "horizon_s": horizon,
                    "auroc_matched": m, "auroc_transfer": x, "auroc_gap": m - x,
                    "auprc_matched": mp, "auprc_transfer": xp, "auprc_gap": mp - xp})
    if not out:
        return pd.DataFrame()
    return pd.DataFrame(out).sort_values(["experiment", "adaptation"])


def main(argv=None):
    ap = argparse.ArgumentParser(description="Stage 19: zero-cost transfer adaptation")
    ap.add_argument("--root", default=None)
    ap.add_argument("--public-root", default="public")
    ap.add_argument("--experiments", nargs="*", default=["regime", "external"])
    ap.add_argument("--seed", type=int, default=1337)
    ap.add_argument("--tag", default="transfer_adaptation")
    a = ap.parse_args(argv)

    cfg = Config(deep_merge(load_config("base.yaml", adapter="xcal_signalling"), {
        "project": {"paths": {"processed": "data/processed_xcal",
                              "interim": "data/interim_xcal",
                              "reports": "reports_xcal",
                              "artifacts": "artifacts_xcal"}},
        "labels": {"horizons_s": [0.5, 1.0, 2.0, 3.0, 5.0],
                   "allow_subperiod_horizons": True},
        "segmentation": {"method": "fixed_duration", "fixed_duration_s": 180,
                         "route_from": "config"},
        "qc": {"min_drive_duration_s": 60, "min_drive_samples": 60},
        "tasks": {"qoe": {"enabled": False}, "target": {"enabled": False},
                  "dwell": {"enabled": False}}}))
    paths = resolve_paths(cfg, a.root)

    parts = []
    if "regime" in a.experiments:
        parts.append(regime_experiment(cfg, a.seed))
    if "external" in a.experiments:
        parts.append(external_experiment(cfg, Path(a.public_root), a.seed))
    df = pd.concat([p for p in parts if len(p)], ignore_index=True)
    RPT.save_table(df, paths["reports"], a.tag)
    summ = pd.concat([s for s in (summarise(df, h) for h in (0.5, 1.0, 2.0)) if len(s)],
                     ignore_index=True)
    RPT.save_table(summ, paths["reports"], f"{a.tag}_summary")
    write_json({"adaptations": list(ADAPTATIONS), "model": "lgbm",
                "note": "both adaptations are unsupervised: target labels are never "
                        "used, only target features",
                "experiments": a.experiments, "seed": a.seed},
               paths["artifacts"] / f"{a.tag}.json")
    LOG.info("stage 19 complete: %d rows", len(df))
    print(summ.to_string(index=False))


if __name__ == "__main__":
    main()

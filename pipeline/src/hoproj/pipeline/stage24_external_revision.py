"""Stage 24 - external validation, rebuilt for the revision (C6).

The v1 external check trained on our 1 Hz export features (which carry the
row-time leak, C9) and tested on a grid reconstructed from the public
dataset's L3 signalling. Here BOTH domains are built the same way, from L3
signalling only (``stage08.build_domain``): every feature is a backward
as-of merge on millisecond report timestamps, so the information cut-off is
exact by construction and identical on both sides.

The public dataset (Shafi et al., Mendeley Data 10.17632/n2pvmtyn2j) shares
our operator, city, instrument licence and institution. It is an
independent collection on the same network, not an external network.
"""
from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, roc_auc_score

from ..data.features import select_blocks
from ..revision import evaluation as EV
from ..revision import models as MD
from ..revision.data import EDGES
from ..utils import get_logger
from .stage08_public_dataset import build_domain
from .stage12_xcal_prepare import CAPTURES
from .stage22_revision import save

LOG = get_logger("hoproj.stage24")
PUB = Path("data/public_mr")
OURS = Path("data/ours_mr")


def frame(dom, source):
    f = dom.features.reset_index(drop=True)
    lab = dom.labels.reset_index(drop=True)
    names = [n for n in select_blocks(f, ["rf", "history"]) if n in f.columns]
    tags = [f"h{str(e).replace('.', 'p')}" for e in EDGES]
    m = np.all([lab[f"m_ho_{t}"].to_numpy() == 1 for t in tags if f"m_ho_{t}" in lab], axis=0)
    X = f[names].to_numpy(float)[m]
    tn = lab["t_to_next_ho_s"].fillna(np.inf).to_numpy(float)[m]
    Y = np.column_stack([(tn <= e).astype(int) for e in EDGES])
    g = f["drive_id"].astype(str).to_numpy()[m]
    grp = np.array(["__".join(d.split("__")[1:3]) for d in g])
    return {"X": X, "t": tn, "Y": Y, "run": g, "group": grp, "names": names}


def metrics(Y, P, runs, label):
    rows = []
    rng = np.random.default_rng(0)
    ur = np.unique(runs)
    idx_by = {r: np.flatnonzero(runs == r) for r in ur}
    for k, e in enumerate(EDGES):
        y, p = Y[:, k], P[:, k]
        if len(np.unique(y)) < 2:
            continue
        bs_a, bs_p = [], []
        for _ in range(500):
            ii = np.concatenate([idx_by[r] for r in rng.choice(ur, len(ur))])
            if len(np.unique(y[ii])) == 2:
                bs_a.append(roc_auc_score(y[ii], p[ii]))
                bs_p.append(average_precision_score(y[ii], p[ii]))
        ap = average_precision_score(y, p)
        rows.append({"setting": label, "horizon_s": e, "n": len(y), "runs": len(ur),
                     "prevalence": y.mean(), "auroc": roc_auc_score(y, p),
                     "auroc_ci_low": np.quantile(bs_a, .025), "auroc_ci_high": np.quantile(bs_a, .975),
                     "auprc": ap, "auprc_ci_low": np.quantile(bs_p, .025),
                     "auprc_ci_high": np.quantile(bs_p, .975), "lift": ap / y.mean(),
                     "ece": EV.ece(y, p)})
    return rows


def grouped_oof(D, seed=0):
    P = np.full(D["Y"].shape, np.nan)
    for g in np.unique(D["group"]):
        te = D["group"] == g
        m = MD.HazardLGBM(seed=seed).fit(D["X"][~te], D["t"][~te])
        P[te] = m.predict(D["X"][te])
    return P


def main():
    src = Path("/mnt/user-data/uploads/Handover Thesis/Drivetest Data/"
               "Drive-Test-Based LTE Handover Dataset for Cellular/Handover Dataset (ver 2)/"
               "Measurement Reports")
    PUB.mkdir(parents=True, exist_ok=True)
    for d in src.iterdir():
        dst = PUB / d.name.replace(" ", "_")
        if not dst.exists():
            os.symlink(d, dst)
    (OURS / "XCAL").mkdir(parents=True, exist_ok=True)
    for tag, raw, _, sig in CAPTURES:
        dst = OURS / "XCAL" / f"{tag}.txt"
        if not dst.exists():
            os.symlink(Path(raw).resolve() / sig, dst)
    import pickle
    cache = Path("data/rev/external_domains.pkl")
    if cache.exists():
        dp, do = pickle.load(open(cache, "rb"))
    else:
        dp, do = build_domain(PUB, "public"), build_domain(OURS, "ours")
        pickle.dump((dp, do), open(cache, "wb"))
    pub, ours = frame(dp, "public"), frame(do, "ours")
    assert pub["names"] == ours["names"]
    LOG.info("public: %d rows, %d runs, %d groups; ours: %d rows, %d runs",
             len(pub["Y"]), len(set(pub["run"])), len(set(pub["group"])),
             len(ours["Y"]), len(set(ours["run"])))
    rows = []
    rows += metrics(ours["Y"], grouped_oof(ours), ours["run"], "ours, leave-one-capture-out")
    rows += metrics(pub["Y"], grouped_oof(pub), pub["run"], "public, leave-one-file-out")
    m = MD.HazardLGBM(seed=0).fit(ours["X"], ours["t"])
    rows += metrics(pub["Y"], m.predict(pub["X"]), pub["run"], "ours -> public (no refit)")
    m = MD.HazardLGBM(seed=0).fit(pub["X"], pub["t"])
    rows += metrics(ours["Y"], m.predict(ours["X"]), ours["run"], "public -> ours (no refit)")
    save(pd.DataFrame(rows), "c6_external_signalling_only")
    save(pd.DataFrame([{"domain": k, "rows": len(v["Y"]), "runs": len(set(v["run"])),
                        "files_or_captures": len(set(v["group"])), "features": len(v["names"]),
                        "events_in_rows_5s": int(v["Y"][:, -1].sum())}
                       for k, v in (("public", pub), ("ours", ours))]), "c6_external_domains")
    save(pd.DataFrame({"feature": pub["names"]}), "c6_external_feature_list")


if __name__ == "__main__":
    main()

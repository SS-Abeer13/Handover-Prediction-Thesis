"""Stage 32 - the 9 Oct 2026 operator B capture: a blind, second-operator test.

    python -m hoproj.pipeline.stage32_second_operator            # build + blind + tables
    python -m hoproj.pipeline.stage32_second_operator --skip-build

WHAT THIS CAPTURE IS.  Every campaign in the study (10/12/13/15 Sept) is operator A.  ``oct-9-2026.csv`` / ``oct-9-2026.txt`` are operator B, recorded on 9 Oct 2026 near IUT, Gazipur, with the same XCAL set-up.  It
was recorded after the modelling freeze and after the alignment audit, so it is the
first campaign that is blind with respect to *every* pipeline decision, including the
one-row lag (review concern: "campaign 4 is not blind").

WHAT THIS STAGE DOES - AND DELIBERATELY DOES NOT DO.
* It does NOT add 9 Oct to ``stage12_xcal_prepare.CAPTURES``.  Pooling it into the
  main leave-one-campaign-out table would turn the only blind, cross-operator test into
  one more training campaign.  The headline stays the four operator A campaigns.
* It builds a separate five-campaign dataset under ``second_operator/`` (stage 12's
  unchanged per-capture code path) so the four operator A rows are bit-identical to
  ``data/processed_xcal``.
* Blind test = exactly the 9 Oct fold of LOCO under the frozen stage-22 protocol: fit
  and calibration rows from the four operator A campaigns (temporal calibration
  split), nested 20-trial tuning, seeds 0-2, scored on 9 Oct only.
* Confirmatory tables: the row-alignment audit, ping-pong ladder and carrier strata,
  handover profiles, all per campaign.

Raw files are expected, like the other captures, at ``oct09/data/raw/oct-9-2026.*``
relative to the pipeline root.

Requires the RSRP-only neighbour fix in ``hoproj.data.signalling`` (14 Oct 2026):
operator B reports neighbours with reportQuantity = rsrp, and the old parser dropped
all but 16 of 776 neighbour rows on this log.
"""
from __future__ import annotations

import argparse
import json
import pickle
import time
from pathlib import Path

import numpy as np
import pandas as pd

from ..data.config_regime import annotate_reports, parse_maps
from ..data.config_timeline_v2 import annotate_reports_v2, parse_timeline
from ..data.signalling import parse_signalling
from ..revision import data as RD
from ..revision import evaluation as EV
from ..utils import get_logger
from . import stage12_xcal_prepare as s12
from . import stage22_revision as S
from .stage26_rev_extras import _pp, _pp_flags

LOG = get_logger("hoproj.stage32")

OCT = ("XCAL09Oct", "oct09/data/raw", "oct-9-2026.csv", "oct-9-2026.txt")
OCT_NAME = "9 Oct (operator B, Gazipur)"
ROOT2 = Path("second_operator")
LEARNERS = ["a3", "lr", "lgbm", "dwell", "history", "hawkes", "mlp"]


def build_pickles(caps, out: Path) -> None:
    """data/rev/signalling.pkl and reports_v2.pkl, as stages 22-31 read them."""
    sig, rv2 = {}, {}
    for tag, raw, _, s in caps:
        p = Path(raw) / s
        log = parse_signalling(p)
        sig[tag] = {"handovers": log.handovers, "failures": log.failures,
                    "reports": annotate_reports(log.measurement_reports, parse_maps(p))}
        rv2[tag] = {"reports": annotate_reports_v2(log.measurement_reports, parse_timeline(p))}
    out.mkdir(parents=True, exist_ok=True)
    pickle.dump(sig, open(out / "signalling.pkl", "wb"))
    pickle.dump(rv2, open(out / "reports_v2.pkl", "wb"))


def _register():
    RD.CAPTURE_NAMES.setdefault(OCT[0], OCT_NAME)
    r = ROOT2.resolve()          # absolute: stage 23 below runs from inside ROOT2
    S.PROC, S.SIG, S.REP = (r / "data/processed_xcal", r / "data/rev/signalling.pkl",
                            r / "data/rev/reports_v2.pkl")
    S.OUT = r / "reports/tables"


def build() -> None:
    caps = list(s12.CAPTURES)
    s12.CAPTURES[:] = caps + [OCT]          # only for this call
    try:
        s12.run(str(ROOT2), s12.HORIZONS, 1337)
        build_pickles(s12.CAPTURES, ROOT2 / "data/rev")
    finally:
        s12.CAPTURES[:] = caps


def blind(learners) -> pd.DataFrame:
    d = S.data()
    fr = d.frame
    des = S.Design(d, S.MAIN_BLOCKS)
    te = (fr["capture"] == OCT[0]).to_numpy()
    fit, cal = EV._temporal_calib(fr, ~te)
    extra = {"dwell": ["t_since_prev_ho_s", "has_prev_ho"], "history": d.names["history"]}
    rows, chosen = [], []
    for name in learners:
        t0 = time.time()
        if name == "hawkes":
            P = S.hawkes_baseline(d, [EV.Fold("LOCO:XCAL09Oct", te, fit, cal)])
        else:
            base = name if name not in extra else "lgbm"
            D = des
            if name in extra:
                cols = [des.names.index(c) for c in extra[name]]
                D = S.Design(d, S.MAIN_BLOCKS)
                D.X, D.names = des.X[:, cols], [des.names[i] for i in cols]
            Ps = []
            for seed in ([0] if name == "a3" else S.SEEDS):
                p = {} if name == "a3" else S.tune(base, D, fit, cal, seed)
                chosen.append({"learner": name, "seed": seed, "params": json.dumps(p, default=float)})
                P = np.full(des.Y.shape, np.nan)
                P[te] = S.fit_predict(base, D, fit | cal, te, seed, p)
                Ps.append(P)
            P = np.mean(Ps, axis=0)
        np.save(S.OUT / f"oof_blind_{name}.npy", P)
        h = EV.horizon_metrics(des.Y, P, te)
        h.insert(0, "learner", S.LABEL.get(name, name))
        rows.append(h)
        LOG.info("blind %s done (%.0fs)", name, time.time() - t0)
    out = pd.concat(rows)
    S.save(out, "c32_blind_second_operator")
    S.save(pd.DataFrame(chosen), "c32_blind_tuned_params")
    return out


def per_campaign_tables() -> None:
    d = S.data()
    feats = pd.read_parquet(S.PROC / "features.parquet")
    feats["t"] = pd.to_datetime(feats["t"])
    ev = d.events
    al, pp = [], []
    for cap in sorted(ev["capture"].unique()):
        a = RD.row_alignment_audit(feats[feats.capture == cap], ev[ev.capture == cap])
        a.insert(0, "capture", RD.CAPTURE_NAMES[cap])
        al.append(a)
    S.save(pd.concat(al), "c32_alignment_audit_per_campaign")
    # carrier relation per command, from the stage 23 attribution if present
    at_path = S.OUT / "c5_handover_attribution_v2_rows.csv"
    ev2 = ev.copy()
    if at_path.exists():
        at = pd.read_csv(at_path)
        assert (at["capture"].to_numpy()[: len(ev2)] == ev2["capture"].to_numpy()).all()
        ev2["relation"] = at["ho_relation"].to_numpy()[: len(ev2)]
    else:
        ev2["relation"] = "unknown"
    ev2["pp"] = _pp_flags(ev2, 15, False, False)    # flag on the full sequence, then stratify
    for cap in sorted(ev["capture"].unique()):
        e, g = ev[ev.capture == cap], ev2[ev2.capture == cap]
        pp.append({"capture": RD.CAPTURE_NAMES[cap], "n_handovers": len(e),
                   "prev_cell_pci_carrier_15s": _pp(e, 15, False, False),
                   "prev_cell_pci_only_15s": _pp(e, 15, True, False),
                   "any_return_15s": _pp(e, 15, False, True),
                   "intra_freq_rate": g.loc[g.relation == "intra-frequency", "pp"].mean(),
                   "n_intra": int((g.relation == "intra-frequency").sum()),
                   "inter_freq_rate": g.loc[g.relation == "inter-frequency", "pp"].mean(),
                   "n_inter": int((g.relation == "inter-frequency").sum())})
    S.save(pd.DataFrame(pp), "c32_pingpong_per_campaign")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--skip-build", action="store_true")
    ap.add_argument("--learners", nargs="*", default=LEARNERS)
    a = ap.parse_args(argv)
    _register()
    S.OUT.mkdir(parents=True, exist_ok=True)
    if not a.skip_build:
        build()
    # the descriptive revision tables, on the five-campaign build (reference only)
    S.exp_audit()
    from . import stage23_signalling_revision as s23
    import os
    cwd = os.getcwd()
    os.chdir(ROOT2)                 # stage 23 reads data/... and writes reports_rev/tables
    try:
        s12.CAPTURES.append(OCT)
        s23.main()
    finally:
        s12.CAPTURES.remove(OCT)
        os.chdir(cwd)
    src = ROOT2 / "reports_rev/tables/c5_handover_attribution_v2_rows.csv"
    if src.exists():
        (S.OUT / src.name).write_bytes(src.read_bytes())
    per_campaign_tables()
    blind(a.learners)


if __name__ == "__main__":
    main()

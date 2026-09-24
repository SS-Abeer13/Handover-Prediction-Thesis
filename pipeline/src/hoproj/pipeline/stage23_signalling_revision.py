"""Stage 23 - LTE signalling analyses for the revision (C5, C7, C14).

* Handover attribution under the v2 configuration timeline: each handover
  command is attributed to the most recent measurement report sent in the
  2 s before it, and inherits that report's event, offset, hysteresis, TTT
  and carrier relation (intra- vs inter-frequency).
* The offset sign is reported weighted by handovers, not by configurations.
* Report conversion is computed per *trigger episode*: consecutive reports of
  one measId whose spacing is consistent with reportInterval re-reporting
  (reportAmount > 1) are one episode. Per-report rates are kept alongside to
  show how much the periodic repeats alone change the figure.
"""
from __future__ import annotations

import pickle
from pathlib import Path

import numpy as np
import pandas as pd

from ..revision.data import CAPTURE_NAMES
from ..utils import get_logger
from .stage22_revision import OUT, save

LOG = get_logger("hoproj.stage23")
WINDOW_S = 2.0


def serving_carrier(t: pd.Series, ho: pd.DataFrame, export: pd.DataFrame) -> np.ndarray:
    ht = ho["t"].to_numpy()
    he = ho["target_earfcn"].to_numpy(float)
    i = np.searchsorted(ht, t.to_numpy(), side="right") - 1
    out = np.where(i >= 0, he[np.clip(i, 0, None)], np.nan)
    ex = export.set_index("t")["serving_earfcn"].sort_index()
    fb = ex.reindex(t.dt.floor("s").to_numpy()).to_numpy(float)
    return np.where(np.isnan(out), fb, out)


def episodes(rep: pd.DataFrame) -> pd.Series:
    """Episode id per report (same measId, gap <= 1.5 x reportInterval + 0.3 s)."""
    rep = rep.sort_values("t")
    eid = np.zeros(len(rep), int)
    last: dict = {}
    nxt = 0
    for i, (m, c, t, ri, ra) in enumerate(rep[["meas_id", "report_config_id", "t",
                                               "report_interval_ms", "report_amount"]]
                                          .itertuples(index=False)):
        key = (m, c)
        lim = (1.5 * ri / 1000 + 0.3) if (pd.notna(ri) and ra not in ("r1", None)) else 0.0
        if key in last and (t - last[key][0]).total_seconds() <= lim:
            eid[i] = last[key][1]
        else:
            eid[i] = nxt
            nxt += 1
        last[key] = (t, eid[i])
    return pd.Series(eid, index=rep.index)


def main():
    sig = pickle.load(open("data/rev/signalling.pkl", "rb"))
    rv2 = pickle.load(open("data/rev/reports_v2.pkl", "rb"))
    feats = pd.read_parquet("data/processed_xcal/features.parquet")
    feats["t"] = pd.to_datetime(feats["t"])
    ho_rows, ep_rows, rep_rows = [], [], []
    for cap in sorted(sig):
        ho = sig[cap]["handovers"]
        ho = ho[ho["completed"]].sort_values("t").reset_index(drop=True)
        rep = rv2[cap]["reports"].sort_values("t").reset_index(drop=True)
        rep["serving_earfcn"] = serving_carrier(rep["t"], ho, feats[feats.capture == cap])
        rep["relation"] = np.where(rep["carrier_earfcn"].isna(), "unknown",
                                   np.where(rep["carrier_earfcn"] == rep["serving_earfcn"],
                                            "intra-frequency", "inter-frequency"))
        rep["episode"] = episodes(rep)
        rep["capture"] = cap
        # --- attribute each handover to the latest report in the preceding 2 s
        rt = rep["t"].to_numpy()
        owning_episodes = {}            # episode -> number of commands attributed to it
        for h in ho.itertuples():
            j = np.searchsorted(rt, np.datetime64(h.t), side="left") - 1
            r = rep.iloc[j] if j >= 0 else None
            ok = r is not None and (h.t - r["t"]).total_seconds() <= WINDOW_S
            if ok:
                e = r["episode"]
                owning_episodes[e] = owning_episodes.get(e, 0) + 1
            src = serving_carrier(pd.Series([h.t - pd.Timedelta(milliseconds=1)]), ho,
                                  feats[feats.capture == cap])[0]
            ho_rows.append({
                "capture": cap, "t": h.t, "target_earfcn": h.target_earfcn,
                "ho_relation": "intra-frequency" if h.target_earfcn == src else "inter-frequency",
                "attributed": ok,
                "event": r["event_id"] if ok else "none in 2 s",
                "a3_offset_db": r["a3_offset_db"] if ok else np.nan,
                "hysteresis_db": r["hysteresis_db"] if ok else np.nan,
                "ttt_ms": r["time_to_trigger_ms"] if ok else np.nan,
                "report_relation": r["relation"] if ok else None,
                "ms_report_to_command": (h.t - r["t"]).total_seconds() * 1000 if ok else np.nan})
        # --- conversion: per report and per episode (A3 only, and all types)
        ht = ho["t"].to_numpy()

        def converted(t0, t1):
            i = np.searchsorted(ht, np.datetime64(t0), side="left")
            return i < len(ht) and ht[i] <= np.datetime64(t1 + pd.Timedelta(seconds=WINDOW_S))
        rep["converted_report"] = [converted(t, t) for t in rep["t"]]
        rep_rows.append(rep)
        for eid, g in rep.groupby("episode"):
            ep_rows.append({"capture": cap, "event": g["event_id"].iloc[0],
                            # C7 (round 2): an episode "owns" a command only if that command
                            # is attributed to one of ITS reports by the same latest-report-
                            # within-2 s rule used for Table 3.1.  Each command has exactly one
                            # attributed report, so this matching is one-to-one and the owned
                            # counts sum to the attributed commands rather than exceeding them.
                            "owns_command": bool(owning_episodes.get(eid, 0)),
                            "commands_owned": int(owning_episodes.get(eid, 0)),
                            "a3_offset_db": g["a3_offset_db"].iloc[0],
                            "hysteresis_db": g["hysteresis_db"].iloc[0],
                            "ttt_ms": g["time_to_trigger_ms"].iloc[0],
                            "report_interval_ms": g["report_interval_ms"].iloc[0],
                            "report_amount": g["report_amount"].iloc[0],
                            "relation": g["relation"].iloc[0], "n_reports": len(g),
                            "converted": converted(g["t"].min(), g["t"].max())})
    H = pd.DataFrame(ho_rows)
    E = pd.DataFrame(ep_rows)
    R = pd.concat(rep_rows, ignore_index=True)
    H.to_csv(OUT / "c5_handover_attribution_v2_rows.csv", index=False)

    # C5: offset sign weighted by handovers
    a3 = H[H.event == "A3"]
    prof = (H.assign(profile=np.where(H.event == "A3",
                                      "A3 " + H.a3_offset_db.map(lambda v: f"{v:+g} dB")
                                      + ", Hys " + H.hysteresis_db.map(lambda v: f"{v:g} dB")
                                      + ", TTT " + H.ttt_ms.map(lambda v: f"{v:g} ms"),
                                      H.event.fillna("unresolved")))
            .groupby(["profile", "report_relation"], dropna=False).size().rename("handovers")
            .reset_index().sort_values("handovers", ascending=False))
    prof["share_of_all_handovers"] = prof["handovers"] / len(H)
    save(prof, "c5_handover_profiles_v2")
    sign = pd.DataFrame([{
        "handovers": len(H), "attributed_to_a_report_within_2s": int(H.attributed.sum()),
        "attributed_A3": len(a3),
        "A3_positive_offset": int((a3.a3_offset_db > 0).sum()),
        "A3_zero_offset": int((a3.a3_offset_db == 0).sum()),
        "A3_negative_offset": int((a3.a3_offset_db < 0).sum()),
        "A3_positive_share_of_A3": float((a3.a3_offset_db > 0).mean()),
        "A5": int((H.event == "A5").sum()), "A4": int((H.event == "A4").sum()),
        "A2": int((H.event == "A2").sum()), "A1": int((H.event == "A1").sum()),
        "periodical": int((H.event == "periodical").sum()),
        "median_ms_report_to_command": float(H.ms_report_to_command.median())}])
    save(sign, "c5_offset_sign_handover_weighted")
    save(H.groupby(["capture", "ho_relation"]).size().rename("handovers").reset_index(),
         "c14_intra_inter_handovers")

    # C7: conversion
    def rate(df, key):
        g = df.groupby(key, dropna=False)
        return g.agg(n=("converted", "size"), converted=("converted", "sum")).assign(
            declined_share=lambda x: 1 - x.converted / x.n).reset_index()

    a3e = E[E.event == "A3"]
    a3r = R[R.event_id == "A3"].rename(columns={"converted_report": "converted"})
    a3x = a3e.drop(columns=["converted"]).rename(columns={"owns_command": "converted"})
    tbl = []
    for lab, df in (("per report (v1 unit)", a3r),
                    ("per trigger episode (any command within 2 s)", a3e),
                    ("per trigger episode (one-to-one, owns the command)", a3x)):
        r = rate(df.assign(all="pooled"), "all")
        r.insert(0, "unit", lab)
        tbl.append(r.rename(columns={"all": "stratum"}))
        r = rate(df, "capture").rename(columns={"capture": "stratum"})
        r["stratum"] = r["stratum"].map(CAPTURE_NAMES)
        r.insert(0, "unit", lab)
        tbl.append(r)
        r = rate(df, "relation").rename(columns={"relation": "stratum"})
        r.insert(0, "unit", lab)
        tbl.append(r)
    save(pd.concat(tbl, ignore_index=True), "c7_a3_conversion_by_unit")

    # C7 (round 2): how many episodes were open around each command, i.e. how much of the
    # "any command within 2 s" rate is one command being claimed by several episodes.
    dup = []
    for lab, df in (("A3 episodes", a3e), ("all episodes", E)):
        n_any = int(df["converted"].sum())
        n_own = int(df["owns_command"].sum())
        dup.append({"episode set": lab, "episodes": int(len(df)),
                    "episodes with a command within 2 s": n_any,
                    "episodes owning a command (one-to-one)": n_own,
                    "episodes owning two or more commands": int((df["commands_owned"] > 1).sum()),
                    "commands owned in total": int(df["commands_owned"].sum()),
                    "commands claimed more than once": n_any - n_own,
                    "inflation factor": round(n_any / max(n_own, 1), 2)})
    save(pd.DataFrame(dup), "c7_episode_command_multiplicity")
    pe = a3e.assign(profile=a3e.a3_offset_db.map(lambda v: f"{v:+g} dB") + ", Hys "
                    + a3e.hysteresis_db.map(lambda v: f"{v:g}") + ", TTT " + a3e.ttt_ms.map(lambda v: f"{v:g}")
                    + ", RI " + a3e.report_interval_ms.map(lambda v: f"{v:g}") + " x " + a3e.report_amount.astype(str))
    save(pe.groupby(["profile", "relation"]).agg(episodes=("converted", "size"),
                                                 reports=("n_reports", "sum"),
                                                 converted=("converted", "sum"),
                                                 owns_command=("owns_command", "sum"))
         .assign(declined_share=lambda x: 1 - x.converted / x.episodes,
                 declined_share_one_to_one=lambda x: 1 - x.owns_command / x.episodes)
         .reset_index().sort_values("episodes", ascending=False), "c7_a3_conversion_by_profile")
    save(R.groupby(["capture", "event_id"], dropna=False).size().rename("reports").reset_index(),
         "c7_report_type_counts_v2")

    # C-ground-truth (round 3): does every decoded command actually complete?  A reviewer
    # reading 341 re-establishments against 957 commands can reasonably ask whether the
    # label "command issued" means "handover occurred".  It does: every command in the
    # event set carries a decoded RRCConnectionReconfigurationComplete.
    gt = []
    for cap in sorted(sig):
        h = sig[cap]["handovers"]
        f = sig[cap]["failures"]
        ht = h["t"].to_numpy()
        ft = f["t"].to_numpy()
        near = sum(bool((((ft - t) / np.timedelta64(1, "s") > 0)
                         & ((ft - t) / np.timedelta64(1, "s") <= 5)).any()) for t in ht)
        after = sum(bool((((ht - t) / np.timedelta64(1, "s") >= -2)
                          & ((ht - t) / np.timedelta64(1, "s") <= 0)).any()) for t in ft)
        gt.append({"capture": CAPTURE_NAMES[cap], "commands": int(len(h)),
                   "with a decoded Complete": int(h["completed"].sum()),
                   "completion rate": float(h["completed"].mean()),
                   "median interruption (ms)": float(h["interrupt_ms"].median()),
                   "re-establishments": int(len(f)),
                   "commands followed by one within 5 s": int(near),
                   "re-establishments within 2 s after a command": int(after)})
    g = pd.DataFrame(gt)
    tot = {"capture": "pooled", "commands": int(g["commands"].sum()),
           "with a decoded Complete": int(g["with a decoded Complete"].sum()),
           "completion rate": float(g["with a decoded Complete"].sum() / g["commands"].sum()),
           "median interruption (ms)": float(pd.concat(
               [sig[c]["handovers"]["interrupt_ms"] for c in sig]).median()),
           "re-establishments": int(g["re-establishments"].sum()),
           "commands followed by one within 5 s": int(g["commands followed by one within 5 s"].sum()),
           "re-establishments within 2 s after a command":
               int(g["re-establishments within 2 s after a command"].sum())}
    save(pd.concat([g, pd.DataFrame([tot])], ignore_index=True), "c15_handover_completion")
    save(pd.DataFrame([{"a3_reports": len(a3r), "a3_episodes": len(a3e),
                        "reports_per_episode": len(a3r) / len(a3e),
                        "a3_reports_per_handover": len(a3r) / len(H),
                        "session_seconds": float(sum((sig[c]["handovers"]["t"].max() - sig[c]["handovers"]["t"].min()).total_seconds() for c in sig))}]),
         "c7_episode_summary")


if __name__ == "__main__":
    main()

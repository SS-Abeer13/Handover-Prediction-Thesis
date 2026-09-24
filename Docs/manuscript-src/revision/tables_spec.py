from pathlib import Path
import pandas as pd
from msnumbers import t, T  # noqa: F401


def f(x, n=3):
    return "—" if pd.isna(x) else f"{x:.{n}f}"


def pct(x, n=1):
    return "—" if pd.isna(x) else f"{100 * x:.{n}f} %"


def tables(N):
    out = {}

    # ---- Table 2.1 protocol audit (summary; Appendix D lists the models)
    out["2.1"] = [["Protocol property", "Papers satisfying it", "This work"],
                  ["Splits by drive, session or route", "0 / 22", "Yes; leave-one-campaign-out is primary"],
                  ["Uses any split coarser than a random row", "5 / 22", "Yes, four protocols compared"],
                  ["States a split protocol at all", "12 / 22", "Yes; specified in Section 4.9"],
                  ["States the alignment between measurement timestamps and event clock", "0 / 22",
                   "Yes, audited in Section 5.1"],
                  ["Reports a prevalence-aware ranking metric", "2 / 22", "AUPRC with floor and lift"],
                  ["Reports calibration (curve, ECE or Brier)", "0 / 22", "ECE and Brier at every horizon"],
                  ["Reports lead time or false alarms per hour", "0 / 22", "Both, and per kilometre"],
                  ["Reports headline accuracy on an imbalanced task", "7 / 22", "Never"],
                  # NB: this table grades 22 papers on release, so this work's own two rows
                  # must not read "Planned". They state what is committed and when.
                  ["Releases code", "2 / 22",
                   "Committed on acceptance: audit, protocols, features, tables"],
                  ["Releases data", "1 / 22",
                   "Committed on acceptance: derived frames and decoded events, not raw logs"]]

    # ---- Table 3.3 handover completion (ground truth integrity)
    gt = t("c15_handover_completion")
    rows = [["Campaign", "Commands", "With a decoded Complete", "Median command-to-complete log interval",
             "Re-establishments", "Commands followed by one within 5 s",
             "Re-establishments within 2 s of a command"]]
    for _, r in gt.iterrows():                       # by name, never by tuple position
        rows.append([str(r["capture"]), f"{int(r['commands']):,}",
                     f"{int(r['with a decoded Complete'])} ({r['completion rate']:.0%})",
                     f"{r['median interruption (ms)']:.0f} ms",
                     str(int(r["re-establishments"])),
                     str(int(r["commands followed by one within 5 s"])),
                     str(int(r["re-establishments within 2 s after a command"]))])
    out["3.3"] = rows

    # ---- Table 3.1 deployed configuration, weighted by handovers
    p = t("c5_handover_profiles_v2")
    a3 = p[p.profile.str.startswith("A3")].groupby("profile")["handovers"].sum().sort_values(ascending=False)
    rows = [["Event A3 profile (offset, hysteresis, time-to-trigger)", "Handovers attributed", "Share of all handovers"]]
    # The table is truncated to the profiles that matter, but the residue is shown
    # explicitly so the rows sum to the corpus rather than to 94.7 % of it.
    for k, v in a3.head(6).items():
        rows.append([k.replace("A3 ", ""), str(int(v)), pct(v / N["ho_all"])])
    a3_rest = int(a3.sum() - a3.head(6).sum())
    if a3_rest:
        rows.append([f"all other A3 profiles ({len(a3) - 6} of them)", str(a3_rest),
                     pct(a3_rest / N["ho_all"])])
    other = p[~p.profile.str.startswith("A3")].groupby("profile")["handovers"].sum().sort_values(ascending=False)
    for k, v in other.head(5).items():
        rows.append([f"triggered by {k} instead of A3", str(int(v)), pct(v / N["ho_all"])])
    oth_rest = int(other.sum() - other.head(5).sum())
    if oth_rest:
        rows.append([f"all other non-A3 triggers ({len(other) - 5} of them)", str(oth_rest),
                     pct(oth_rest / N["ho_all"])])
    tot = int(a3.sum() + other.sum())
    rows.append(["Total handover commands", str(tot), pct(tot / N["ho_all"])])
    rows.append(["of which A3-triggered, under a positive offset",
                 f"{N['a3_pos']} of {N['a3_ho']} A3", pct(N["a3_pos_share"]) + " of A3"])
    out["3.1"] = rows

    # ---- Table 3.2 campaigns
    s = t("c1_dataset_sessions")
    rows = [["Campaign (2026)", "Sessions", "180 s blocks", "Samples", "Usable rows",
             "Handover commands", "Re-establishments", "Duration", "Mean speed"]]
    for r in s.itertuples():
        rows.append([r.capture, str(r.sessions), str(r.chunks_180s), f"{r.rows_qc:,}", f"{r.rows_usable:,}",
                     str(r.handovers_all), str(r.reestablishments), f"{r.duration_min:.0f} min",
                     f"{r.mean_speed_kmh:.1f} km/h"])
    rows.append(["Pooled", str(N["sessions"]), str(N["chunks"]), f"{N['rows_qc']:,}", f"{N['rows_usable']:,}",
                 str(N["ho_all"]), str(N["reest_all"]), f"{N['hours']:.1f} h", "—"])
    out["3.2"] = rows

    # ---- Table 4.1 prevalence
    pv = t("c4_prevalence")
    out["4.1"] = [["Horizon", "Prevalence", "Accuracy of a constant “no handover”"]] + \
        [[f"{r.horizon_s:g} s", pct(r.prevalence), pct(r.constant_negative_accuracy)] for r in pv.itertuples()]

    # ---- Table 4.2 hazard vs prevalence
    hz = t("c4_hazard_prevalence_reconciled")
    out["4.2"] = [["Bin", "Interval", "At risk", "Events", "Hazard", "F(h) from hazards", "Prevalence (Table 4.1)"]] + \
        [[str(r.bin), r.interval_s + " s", f"{r.at_risk:,}", str(r.events), f(r.hazard, 4),
          f(r.F_from_hazards, 4), f(r.prevalence_direct, 4)] for r in hz.itertuples()]

    # ---- Table 4.3 feature blocks
    # NB: every count here is read from c0_feature_blocks. Do not type one in.
    out["4.3"] = [["Block", "Count", "Source", "Content"],
                  ["Radio", str(N["n_feat_radio"]), "1 Hz export, lagged one row",
                   "Serving and neighbour RSRP, RSRQ, SINR, RSSI, CQI; rolling mean, standard deviation, "
                   "range, slope and first difference over 3, 5 and 10 s; serving-to-neighbour gaps; "
                   "missingness indicators"],
                  ["Mobility", str(N["n_feat_mobility"]), "1 Hz export, lagged one row",
                   "GPS speed, heading change, acceleration, stop duration and mobility state, with "
                   "their rolling statistics"],
                  ["History", str(N["n_feat_history"]), "decoded signalling, session-level",
                   "Time since the previous and second-previous handover command, command counts in the "
                   "previous 30 and 60 s, whether the previous command was a return"],
                  ["Main feature set", str(N["n_features"]), "", "used by every learner in Sections 5.2 to 5.8"],
                  ["Signalling (ablation only)", str(N["n_feat_signalling"]), "decoded signalling",
                   "A3 and all-event report counts in (t−w, t], time since the last A3 report, A3 hold time, "
                   "and the offset, hysteresis and time-to-trigger in force"],
                  ["Design matrix as built", str(N["n_feat_matrix"]), "",
                   "the main set plus the signalling block; learners outside Section 5.8 are given the "
                   "main set only"]]

    # ---- Table 5.1 alignment audit
    al = t("c9_row_alignment_audit")
    cols = [c for c in al.columns if c.startswith("row")]
    out["5.1"] = [["Handovers considered", "n"] + [c.replace("row ", "row ") for c in cols]] + \
        [[r["subset"], str(int(r["n"]))] + [pct(r[c]) for c in cols] for _, r in al.iterrows()]

    # ---- Table 5.2 what the lag costs
    ab = t("c18_ablation").set_index(["variant", "horizon_s"])
    rows = [["Feature alignment", "AUPRC 1 s", "AUROC 1 s", "AUPRC 5 s", "Dwell feature AUROC 1 s"]]
    sf0 = t("c14_single_feature_auroc_lag0").set_index("feature")
    sf1 = t("c14_single_feature_auroc").set_index("feature")
    rows.append(["Export row stamped t used at t (v1)", f(N["lag0_auprc1"]), f(N["lag0_auroc1"]),
                 f(N["lag0_auprc5"]), f(float(sf0.loc["serving_dwell_s", "auroc_1s"]))])
    rows.append(["Export row lagged one sample (this work)", f(N["auprc1"]), f(N["auroc1"]), f(N["auprc5"]),
                 f(float(sf1.loc["t_since_prev_ho_s", "auroc_1s"]))])
    # the last cell was blank, which reads as "not measured" rather than "here it is"
    _dw0 = float(sf0.loc["serving_dwell_s", "auroc_1s"])
    _dw1 = float(sf1.loc["t_since_prev_ho_s", "auroc_1s"])
    rows.append(["Change", f"{100 * (N['auprc1'] / N['lag0_auprc1'] - 1):+.0f} %",
                 f"{N['auroc1'] - N['lag0_auroc1']:+.3f}",
                 f"{100 * (N['auprc5'] / N['lag0_auprc5'] - 1):+.0f} %",
                 f"{_dw1 - _dw0:+.3f}"])
    out["5.2"] = rows

    # ---- Table 5.3 primary model per horizon
    m = t("c3_main_loco")
    lg = m[m.learner == "LightGBM"]
    out["5.3"] = [["Horizon", "Prevalence", "AUPRC [95 % block-bootstrap CI]", "Lift", "AUROC", "ECE", "Brier"]] + \
        [[f"{r.horizon_s:g} s", f(r.prevalence), f"{r.auprc:.3f} [{r.auprc_ci_low:.3f}, {r.auprc_ci_high:.3f}]",
          f"{r.lift:.1f}×", f(r.auroc), f(r.ece), f(r.brier)] for r in lg.itertuples()]

    # ---- Table 5.4 model comparison
    # NB: the interval column is not decoration. Adjacent learners differ by less than its
    # width, which is the reason the text refuses to rank them [round 3, concern K].
    rows = [["Learner", "AUPRC 1 s [95 % CI]", "Lift 1 s", "AUROC 1 s", "AUPRC 5 s", "Lift 5 s"]]
    piv = m.pivot_table(index="learner", columns="horizon_s",
                        values=["auprc", "lift", "auroc", "auprc_ci_low", "auprc_ci_high"])
    piv = piv.sort_values(("auprc", 1.0), ascending=False)
    for L, r in piv.iterrows():
        rows.append([L, f"{r[('auprc', 1.0)]:.3f} [{r[('auprc_ci_low', 1.0)]:.3f}, "
                        f"{r[('auprc_ci_high', 1.0)]:.3f}]",
                     f"{r[('lift', 1.0)]:.1f}×", f(r[("auroc", 1.0)]),
                     f(r[("auprc", 5.0)]), f"{r[('lift', 5.0)]:.1f}×"])
    rows.append(["Prevalence floor", f(N["prev1"]), "1.0×", "0.500", f(N["prev5"]), "1.0×"])
    out["5.4"] = rows

    # ---- Table 5.5 protocol ladder
    inf = t("c2_inflation_by_horizon")
    i1 = inf[inf.horizon_s == 1.0]
    rows = [["Learner", "Leave one campaign out", "Blocks + 60 s purge", "Random 180 s blocks", "Random rows",
             "Inflation, random rows vs LOCO"]]
    for _, r in i1.sort_values("loco", ascending=False).iterrows():
        rows.append([r["learner"], f(r["loco"]), f(r["blocked_purged"]), f(r["chunk_grouped"]),
                     f(r["random_row"]), f"{r['inflation_random_vs_loco_%']:+.0f} %"])
    out["5.5"] = rows

    # ---- Table 5.6 coherence and calibration
    cm = t("c11_coherence_metrics")
    cv = t("c11_coherence_violations").set_index("arm")
    rows = [["Arm", "Rows violating ordering (one fit)", "Rows violating (3-seed ensemble)",
             "Mean violation", "Largest violation", "ECE 1 s [95 % CI]", "ECE 5 s",
             "AUPRC 1 s", "Needs a held-out split"]]
    needs = {"independent": "no", "independent + cumulative max": "no", "independent + PAV": "no",
             "independent + isotonic": "yes", "independent + isotonic + PAV": "yes", "hazard": "no"}
    for arm in cv.index:
        g = cm[cm.arm == arm].set_index("horizon_s")
        rows.append([arm, pct(cv.loc[arm, "rows_violating_single_fit"]),
                     pct(cv.loc[arm, "rows_violating_seed_mean"]),
                     f(cv.loc[arm, "mean_violation_if_any_single_fit"]),
                     f(cv.loc[arm, "max_violation_single_fit"]),
                     f"{g.loc[1.0, 'ece']:.3f} [{g.loc[1.0, 'ece_ci_low']:.3f}, "
                     f"{g.loc[1.0, 'ece_ci_high']:.3f}]",
                     f(g.loc[5.0, "ece"]), f(g.loc[1.0, "auprc"]), needs.get(arm, "")])
    out["5.6"] = rows

    # ---- Table 5.6b paired differences against the hazard arm
    # NB: the per-campaign columns are the inferential content; the block interval is a
    # descriptive within-campaign spread only. Resampling 180 s blocks is pseudo-replication
    # on this data (Section 5.3 shows they are dependent), so no "excludes zero" column is
    # printed and no significance is claimed anywhere from this table.
    pd_ = t("c11_paired_differences")
    p1 = pd_[(pd_.horizon_s == 1.0)]
    capcols = [c for c in pd_.columns if c.startswith("campaign_")]
    ses = t("c1_dataset_sessions")["capture"].tolist()
    rows = [["Control arm", "Metric", "Hazard − control (pooled)",
             "Within-campaign block spread (descriptive)"]
            + [c.split(" (")[0] for c in ses]
            + ["Campaigns favouring hazard"]]
    for _, r in p1.iterrows():
        rows.append([r["arm"], {"auprc": "AUPRC 1 s", "ece": "ECE 1 s"}[r["metric"]],
                     f"{r['difference']:+.3f}",
                     f"[{r['block_ci_low']:+.3f}, {r['block_ci_high']:+.3f}]"]
                    + [f"{r[c]:+.3f}" for c in capcols]
                    + [f"{int(r['campaigns_favouring_hazard'])} of {int(r['n_campaigns'])}"])
    out["5.6b"] = rows

    # ---- Table 5.16 unsifted case studies (round 5: no qualitative error analysis existed)
    # NB: nine columns do not fit the page. Units go in the header, the campaign uses its
    # short label, and "since previous" is dropped because the traces in Figure 5.20 show it.
    cs = t("c20_case_studies")
    SHORT = {"XCAL10Sept": "10 Sept", "XCAL12Sept": "12 Sept",
             "XCAL13Sept": "13 Sept", "XCAL15Sept": "15 Sept"}
    rows = [["Case", "Campaign", "Score", "To next command (s)", "RSRP (dBm)",
             "SINR (dB)", "Gap (dB)", "Speed (km/h)"]]
    for _, r in cs.iterrows():
        g = r["gap to best neighbour (dB)"]
        rows.append([r["case"], SHORT.get(str(r["campaign"]), str(r["campaign"])),
                     f"{r['score']:.2f}",
                     f"{r['time to next command (s)']:.2f}",
                     f"{r['serving RSRP (dBm)']:.0f}",
                     f"{r['serving SINR (dB)']:.0f}",
                     "—" if pd.isna(g) else f"{g:.0f}",
                     f"{r['speed (km/h)']:.0f}"])
    out["5.16"] = rows

    # ---- Table A.5 sensitivity of the four post-hoc windows
    bl = t("c19_sens_block_length")
    pg = t("c19_sens_purge")
    bc = t("c19_sens_burst_cutoff").pivot_table(index="burst_cutoff_s", columns="stratum",
                                                values="lift_1s")
    rows = [["Window varied", "Value", "Quantity it governs", "Result"]]
    for _, r in bl.iterrows():
        rows.append(["Random-block length", f"{r['block_length_s']:.0f} s",
                     "1 s AUPRC vs LOCO",
                     f"{r['inflation_vs_loco_%']:+.1f} %"])
    for _, r in pg.iterrows():
        rows.append(["Purge between blocked train and test", f"{r['purge_s']:.0f} s",
                     "1 s AUPRC vs LOCO",
                     f"{r['inflation_vs_loco_%']:+.1f} %"])
    for cut, r in bc.iterrows():
        rows.append(["Quiet / in-burst cutoff", f"{cut:.0f} s", "1 s lift by stratum",
                     f"{r['quiet']:.2f}x vs {r['in burst']:.2f}x"])
    if (T / "c19_sens_blank.csv").exists():
        for _, r in t("c19_sens_blank").iterrows():
            rows.append(["Post-handover blank", f"{r['blank_s']:.0f} s",
                         "1 s lift on the row set",
                         f"{r['lift_1s']:.2f}x on {int(r['n_rows']):,} rows"])
    out["A.5"] = rows

    # ---- Table A.6 per-handover evidence for the alignment residual
    re_ = t("c20_residual_evidence").iloc[0]
    ex = t("c20_residual_examples")
    rows = [["Quantity", "Value"],
            ["Handovers with a positive margin (row t predicted contaminated)",
             f"{int(re_['handovers with a positive margin']):,}"],
            ["of which row t does carry the target",
             f"{int(re_['of which row t carries the target (predicted)']):,}"],
            ["Residual: row t carries the source instead",
             f"{int(re_['residual: row t carries the source']):,}"],
            ["of the residual, row t+1 carries the target",
             f"{int(re_['of the residual, row t+1 carries the target']):,} "
             f"({int(re_['of the residual, row t+1 carries the target']) / max(int(re_['residual: row t carries the source']), 1):.0%})"],
            ["Median margin, residual handovers",
             f"{re_['median margin of the residual (s)']:.3f} s"],
            ["Median margin, contaminated handovers",
             f"{re_['median margin of the contaminated (s)']:.3f} s"]]
    rows.append(["", ""])
    rows.append(["Ten residual handovers, smallest margin first", ""])
    for _, r in ex.iterrows():
        rows.append([f"{r['capture']}, δ = {r['delta']:.3f} s, margin {r['margin']:.3f} s",
                     f"row t shows PCI {int(r['pci_t'])}, row t+1 shows PCI {int(r['pci_tp1'])}, "
                     f"target is PCI {int(r['target_pci'])}"])
    out["A.6"] = rows

    # ---- Table A.4 per-campaign calibration for every coherence arm (promised in 5.4)
    cpc = t("c11_coherence_per_capture")
    c1 = cpc[cpc.horizon_s == 1.0]
    arms_order = ["independent", "independent + cumulative max", "independent + PAV",
                  "independent + isotonic", "independent + isotonic + PAV", "hazard"]
    caps = list(dict.fromkeys(c1["capture"]))
    rows = [["Arm"] + [f"{c} ECE / Brier" for c in caps]]
    for a in arms_order:
        g = c1[c1.arm == a].set_index("capture")
        rows.append([a] + [f"{g.loc[c, 'ece']:.3f} / {g.loc[c, 'brier']:.3f}" for c in caps])
    out["A.4"] = rows

    # ---- Table 5.7 CRC
    cr = t("c10_crc_frontier")
    ex = t("c10_crc_pooled_chunk_split")
    rows = [["Target α", "Row loss, exchangeable: alarm rate", "Row loss, exchangeable: realised",
             "Row loss, across campaigns: realised", "Row loss: rotations respecting the bound",
             "Event loss, across campaigns: feasible rotations", "Event loss: alarm rate",
             "Event loss: realised"]]
    for a in sorted(cr.alpha.unique()):
        e = ex[(ex.alpha == a) & (ex.horizon_s == 1.0)].iloc[0]
        c = cr[(cr.alpha == a) & (cr.horizon_s == 1.0)].iloc[0]
        ev_f = float(c["feasible_events"])
        if a == 0.05:
            # Feasible in 25% rotations (Campaign 3, n=20, floor 0.048 <= 0.05) where loss is 0.000 at 100% alarm
            row_realised = f"{c['mean_unit_loss']:.3f}*"
            row_bound = f"{pct(c['rotations_with_mean_loss_le_alpha'], 0)}*"
        else:
            row_realised = f(c["mean_unit_loss"])
            row_bound = pct(c["rotations_with_mean_loss_le_alpha"], 0)
        rows.append([f"{a:.2f}",
                     pct(e["alarm_rate"], 0), f(e["mean_unit_loss"]),
                     row_realised,
                     row_bound,
                     pct(ev_f, 0),
                     "—" if ev_f == 0 else pct(c["alarm_rate_events_mean"], 0),
                     "—" if ev_f == 0 else f(c["mean_unit_loss_events"])])
    rows.append(["Sample-size floor",
                 f"Exchangeable (n ≈ {N['crc_pool_units']}): α ≥ {1/(N['crc_pool_units']+1):.3f}",
                 "",
                 f"Cross-campaign (n ∈ {{8, 14, 15, 20}}): mean α ≥ 0.072 (individual: 0.111, 0.067, 0.063, 0.048)",
                 "",
                 f"Event loss floor: α ≥ {N['crc_unresolvable1']:.3f} (36.4% unresolvable handovers at 1 s; em dash indicates infeasible)",
                 "", ""])
    out["5.7"] = rows

    # ---- Table 5.8 leave-one-campaign-out
    pc = t("c3_main_loco_per_capture")
    g = pc[(pc.learner == "LightGBM") & (pc.horizon_s == 1.0)]
    out["5.8"] = [["Campaign held out", "Rows", "Prevalence", "AUPRC", "Lift", "AUROC", "ECE"]] + \
        [[r.held_out_capture, f"{int(r.n):,}", pct(r.prevalence), f(r.auprc), f"{r.lift:.1f}×",
          f(r.auroc), f(r.ece)] for r in g.itertuples()] + \
        [["Pooled out of fold", f"{N['rows_usable']:,}", pct(N["prev1"]), f(N["auprc1"]),
          f"{N['lift1']:.1f}×", f(N["auroc1"]), f(N["ece1"])]]

    # ---- Table 5.9 external
    e = t("c6_external_signalling_only")
    e1 = e[e.horizon_s == 1.0]
    out["5.9"] = [["Setting", "Rows", "Prevalence", "AUROC [95 % CI]", "AUPRC", "Lift"]] + \
        [[r.setting, f"{int(r.n):,}", pct(r.prevalence), f"{r.auroc:.3f} [{r.auroc_ci_low:.3f}, {r.auroc_ci_high:.3f}]",
          f(r.auprc), f"{r.lift:.1f}×"] for r in e1.itertuples()]

    # ---- Table 5.10 single feature
    sf = t("c14_single_feature_auroc")
    keep = list(sf.head(6)["feature"]) + ["t_since_prev_ho_s", "gap_serving_best_nbr", "speed_kmh"]
    sf = sf[sf.feature.isin(dict.fromkeys(keep))].drop_duplicates("feature")
    # NB: "direction" is meaningless unless the sign convention is spelled out, and the
    # gap is the one feature whose convention a reader cannot guess.
    DEFN = {"gap_serving_best_nbr":
            "serving minus best neighbour in dB, so a smaller value means the neighbour is "
            "closer to overtaking",
            "t_since_prev_ho_s": "seconds since the previous decoded command",
            "sig_s_since_a3": "seconds since the last A3 report was transmitted"}
    out["5.10"] = [["Feature (lagged one row)", "Definition", "AUROC alone at 1 s", "Direction"]] + \
        [[r.feature, DEFN.get(r.feature, ""), f(r.auroc_1s), r.direction] for r in sf.itertuples()] + \
        [["Full model, same rows", "", f(N["auroc1"]), ""]]

    # ---- Table 5.11 burst strata
    bs = t("c8_burst_strata")
    bs = bs[bs.horizon_s.isin([1.0, 5.0]) & bs.learner.isin(
        ["LightGBM", "History block only (LightGBM)", "Event A3 rule (deployed parameters)"])]
    rows = [["Stratum", "Learner", "Rows", "Prevalence 1 s", "AUPRC 1 s", "Lift 1 s", "Lift 5 s"]]
    for (st, L), g in bs.groupby(["stratum", "learner"]):
        g1 = g[g.horizon_s == 1.0].iloc[0]
        g5 = g[g.horizon_s == 5.0].iloc[0]
        rows.append([st, L, f"{int(g1.n):,}", pct(g1.prevalence), f(g1.auprc), f"{g1.lift:.1f}×",
                     f"{g5.lift:.1f}×"])
    out["5.11"] = rows

    # ---- Table 5.12 A3 conversion
    cu = t("c7_a3_conversion_by_unit")
    rows = [["Unit", "Stratum", "n", "Followed by a command within 2 s", "Declined"]]
    for r in cu.itertuples():
        rows.append([r.unit, r.stratum, f"{int(r.n):,}", str(int(r.converted)), pct(r.declined_share, 0)])
    mu = t("c7_episode_command_multiplicity")
    # NB: index by column name. Reading these by tuple position broke silently when
    # two columns were added to the source table, and printed the owned count as the
    # inflation factor.
    for _, r in mu.iterrows():
        rows.append(["command multiplicity", str(r["episode set"]), f"{int(r['episodes']):,}",
                     f"{int(r['episodes with a command within 2 s'])} claimed, "
                     f"{int(r['episodes owning a command (one-to-one)'])} owned",
                     f"x{float(r['inflation factor']):.2f} over-counting"])
    pr = t("c7_a3_conversion_by_profile").head(5)
    for r in pr.itertuples():
        rows.append(["per trigger episode, by profile", r.profile, f"{int(r.episodes):,}",
                     f"{int(r.converted)} claimed, {int(r.owns_command)} owned",
                     f"{pct(r.declined_share, 1)} / {pct(r.declined_share_one_to_one, 1)} one-to-one"])
    out["5.12"] = rows

    # ---- Table 5.13 / 5.14 ping-pong
    pp = t("c13_pingpong_definitions")
    out["5.13"] = [["Definition", "Handovers", "Rate"]] + \
        [[r.definition, str(int(r.n_handovers)), pct(r.rate)] for r in pp.iloc[:3].itertuples()]
    # NB: the counts column exists so the two stratifications can be seen to reconcile. An
    # earlier version re-ran the detector inside each stratum, which redefines "the previous
    # cell" within the subset: the carrier rows then implied 218 ping-pongs and the regime
    # rows 252 on the same 957 commands. Flags are now computed once and partitioned.
    ps = t("c13_pingpong_strata")
    out["5.14"] = [["Stratum", "Handovers", "Ping-pongs", "Ping-pong rate"]] + \
        [[r["stratum"], str(int(r["n_handovers"])), str(int(r["n_pingpong"])), pct(r["rate"])]
         for _, r in ps.iterrows()]

    # ---- Table 5.15 negative results
    out["5.15"] = [["Approach", "Outcome"],
                   ["A dedicated ping-pong classifier", "AUROC 0.51 at the one-second horizon — chance"],
                   ["Deep CORAL and a second unsupervised domain-adaptation method",
                    "No gain over source-only training"],
                   ["Sequence models (GRU, TCN, Transformer) on the same features",
                    f"No gain over gradient-boosted trees; best sequence AUPRC at 1 s "
                    f"{N.get('best_seq_auprc1', float('nan')):.3f} against {N['auprc1']:.3f}"],
                   ["The signalling feature block added to the main set",
                    f"AUPRC at 1 s {N['abl_sig_auprc1']:.3f} against {N['auprc1']:.3f} without it"],
                   ["The unlagged (v1) feature alignment",
                    f"AUPRC at 1 s {N['lag0_auprc1']:.3f}, an artefact of the export row semantics (Section 5.1)"]]

    # ---- Appendix A
    m = t("c3_main_loco")
    piv = m.pivot_table(index="learner", columns="horizon_s", values="auprc")
    rows = [["Learner"] + [f"{h:g} s" for h in piv.columns]]
    for L, r in piv.sort_values(1.0, ascending=False).iterrows():
        rows.append([L] + [f(v) for v in r.values])
    rows.append(["Prevalence floor"] + [f(t("c4_prevalence").set_index("horizon_s").loc[h, "prevalence"])
                                        for h in piv.columns])
    out["A.1"] = rows
    ev = t("c18_event_metrics_pooled_fpr5")
    out["A.2"] = [["Horizon", "Events", "Resolvable on the 1 Hz grid", "Detected", "Detection rate",
                   "False alarms / h", "False alarms / km", "Median lead time"]] + \
        [[f"{r.horizon_s:g} s", str(int(r.events)), pct(r.grid_ceiling), str(int(r.detected)),
          pct(r.detection_rate), f"{r.false_alarms_per_hour:.1f}", f"{r.false_alarms_per_km:.2f}",
          f"{r.lead_median_s:.2f} s"] for r in ev.itertuples()]
    sl = t("c9sel_lag_scope")
    sl = sl[sl.learner == "LightGBM"]
    lab = {"none": "nothing (v1 alignment)",
           "neighbour": "neighbour and gap columns only",
           "serving": "serving-cell radio scalars only",
           "assignment": "every serving-relative column (GPS left at row t)",
           "all": "every export column (v2, as reported throughout)"}
    rows = [["What is lagged by one row", "Columns", "AUPRC 1 s", "AUROC 1 s", "AUPRC 5 s"]]
    for arm in ("none", "neighbour", "serving", "assignment", "all"):
        g = sl[sl.arm == arm].set_index("horizon_s")
        rows.append([lab[arm], str(int(g.loc[1.0, "columns_lagged"])),
                     f(g.loc[1.0, "auprc"]), f(g.loc[1.0, "auroc"]), f(g.loc[5.0, "auprc"])])
    a3 = t("c9sel_lag_scope")
    a3 = a3[(a3.learner.str.startswith("Event A3")) & (a3.horizon_s == 1.0)].set_index("arm")
    rows.append(["control: Event A3 rule, same arms",
                 "-", f"{a3['auprc'].min():.3f} to {a3['auprc'].max():.3f}", "-", "-"])
    out["5.2b"] = rows

    ext = t("c9m_three_dataset_mechanism")
    out["A.3"] = [list(ext.columns)] + ext.astype(str).values.tolist()
    return out


ROOT = Path(__file__).resolve().parents[3]


def appendix_d():
    a = pd.read_csv(ROOT / "pipeline" / "docs" / "literature" / "protocol_audit.csv")
    a = a[a.key != "OURS"]
    rows = [["#", "Model", "Year", "Venue", "Data", "Split protocol", "Prevalence-aware metric",
             "Calibration"]]
    for i, r in enumerate(a.itertuples(), 1):
        rows.append([str(i), str(r.citation), str(r.year), str(r.venue), str(r.data_type),
                     str(r.split_protocol), str(r.prevalence_aware_metric), str(r.calibration_or_uncertainty)])
    return rows

# -*- coding: utf-8 -*-
"""Every number quoted in the revised manuscript, read from reports_rev/tables."""
from pathlib import Path

import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
T = ROOT / "pipeline" / "reports_rev" / "tables"
OLD = ROOT / "pipeline" / "reports_xcal" / "tables"
if not T.exists():
    T = Path("pipeline/reports_rev/tables") if Path("pipeline/reports_rev/tables").exists() else Path("reports_rev/tables")
if not OLD.exists():
    OLD = Path("pipeline/reports_xcal/tables") if Path("pipeline/reports_xcal/tables").exists() else Path("reports_xcal/tables")
from refs import KEYIDX  # noqa: E402


def t(n):
    return pd.read_csv(T / f"{n}.csv")


def build():
    N = {}
    for k, i in KEYIDX.items():
        N[f"ref_{k}"] = i
    N["ref_36331"] = KEYIDX["ts36331"]
    N["ref_shafi_ds"] = KEYIDX["shafi_ds"]
    N["ref_shafi_rl"] = KEYIDX["shafi_rl"]

    ses = t("c1_dataset_sessions")
    N["sessions"] = int(ses["sessions"].sum())
    N["chunks"] = int(ses["chunks_180s"].sum())
    N["rows_qc"] = int(ses["rows_qc"].sum())
    N["rows_usable"] = int(ses["rows_usable"].sum())
    N["ho_all"] = int(ses["handovers_all"].sum())
    N["ho_qc"] = int(ses["handovers_in_qc_chunks"].sum())
    N["reest_all"] = int(ses["reestablishments"].sum())
    # Two distances, never interchangeable: the recording, and the modelling frame.
    N["km_driven"] = float(ses["km_driven"].sum())
    N["km"] = float(ses["km_usable"].sum())
    N["hours"] = float(ses["duration_min"].sum()) / 60
    N["speed_highway"] = float(ses.loc[ses.capture.str.contains("highway"), "mean_speed_kmh"].iloc[0])

    rc = t("c15_reestablishment_causes").set_index("capture").sum()
    N["reest_reconf"] = int(rc.get("reconfigurationFailure", 0))
    N["reest_other"] = int(rc.get("otherFailure", 0))
    N["reest_hofail"] = int(rc.get("handoverFailure", 0))
    gt = t("c15_handover_completion").set_index("capture").loc["pooled"]
    N["gt_commands"] = int(gt["commands"])
    N["gt_complete"] = int(gt["with a decoded Complete"])
    N["gt_complete_rate"] = float(gt["completion rate"])
    N["gt_reest_after"] = int(gt["commands followed by one within 5 s"])
    N["gt_reest_near"] = int(gt["re-establishments within 2 s after a command"])
    rt = t("c15_reestablishment_timing")
    N["reest_median_gap_s"] = float((rt["median_ms_since_command"] * rt["n"]).sum() / rt["n"].sum() / 1000)

    pv = t("c4_prevalence").set_index("horizon_s")
    for h, tag in ((0.5, "05"), (1.0, "1"), (2.0, "2"), (3.0, "3"), (5.0, "5")):
        N[f"prev{tag}"] = float(pv.loc[h, "prevalence"])
    N["long_rows"] = int(t("c4_long_format_size")["long_format_rows"].iloc[0])
    N["competing_rows"] = int(t("c4_long_format_size")["rows_with_competing_reest_first"].iloc[0])

    al = t("c9_row_alignment_audit").set_index("subset")
    a_all = al.loc["all handovers"]
    a_iso = al.loc["isolated (previous > 8 s earlier)"]
    N["align_t0"] = float(a_all["row t+0"])
    N["align_iso_t0"] = float(a_iso["row t+0"])
    N["align_iso_tm1"] = float(a_iso["row t-1"])
    N["align_iso_tm3"] = float(a_iso["row t-3"])

    # ---- C9 mechanism: intra-second geometry of the defect (stage 29)
    mg = t("c9m_mechanism_prediction").set_index("prediction")
    k_pos = "execution completes before t+1 (m > 0)"
    k_neg = "execution crosses t+1 (m < 0)"
    N["mech_n_pos"] = int(mg.loc[k_pos, "n"])
    N["mech_n_neg"] = int(mg.loc[k_neg, "n"])
    N["mech_hit_pos"] = float(mg.loc[k_pos, "row t shows target"])
    N["mech_hit_neg"] = float(mg.loc[k_neg, "row t shows target"])
    db = t("c9m_delta_bins_ours")
    dbc = db[db["subset"] == "clean (no other handover within 2 s)"].set_index(
        "delta bin (s into the second)")
    N["mech_delta_early"] = float(dbc.loc["[0.00, 0.25)", "row t shows target"])
    N["mech_delta_late"] = float(dbc.loc["[0.75, 1.00)", "row t shows target"])
    N["mech_delta_n"] = int(dbc.loc["all", "n"])
    rd = t("c9m_residual_diagnosis").set_index("residual case")
    N["mech_resid_n"] = int(rd.loc["row t predicted to show target but shows source", "n"])
    N["mech_resid_share"] = float(rd.loc["row t predicted to show target but shows source", "share"])
    N["mech_resid_tp1"] = float(
        rd.loc["... of which row t+1 shows the target (one-row exporter lag)", "share"])
    geo = pd.read_csv(T / "c9m_per_handover_geometry.csv")
    N["mech_exec_p90_ms"] = 1000 * float(geo["exec_s"].quantile(0.90))
    N["mech_exec_max_ms"] = 1000 * float(geo["exec_s"].max())
    N["mech_exec_nonzero"] = float((geo["exec_s"] > 0).mean())

    # ---- C9 external replication on a second XCAL corpus (stage 28, all files)
    na = t("c9ext_nuwins_alignment_all")
    nap = na[(na.dataset == "pooled") & (na.subset == "all handovers")].iloc[0]
    nai = na[(na.dataset == "pooled") & (na.subset.str.startswith("isolated"))].iloc[0]
    N["nw_n"] = int(nap["n"])
    N["nw_t0"] = float(nap["row t+0"])
    N["nw_tm1"] = float(nap["row t-1"])
    N["nw_iso_n"] = int(nai["n"])
    N["nw_iso_t0"] = float(nai["row t+0"])
    N["nw_files"] = int(na[~na.dataset.isin(["pooled"])
                           & ~na.dataset.str.endswith("(all files)")]["dataset"].nunique())
    N["nw_operators"] = int(na[na.dataset.str.endswith("(all files)")]["dataset"].nunique())
    nfs = t("c9ext_nuwins_startofsecond_all")
    N["nw_first_t0"] = float(nfs[(nfs.dataset == "pooled")
                                 & (nfs.subset == "all handovers")].iloc[0]["row t+0"])
    nob = t("c9ext_nuwins_offsetbins_all")
    N["nw_delta_early"] = float(nob.iloc[0]["share_target_served"])
    N["nw_delta_late"] = float(nob.iloc[-1]["share_target_served"])
    nec = t("c9ext_nuwins_execution_cdf")
    N["nw_cliff_hi"] = float(nec.iloc[2]["row t shows target"])   # 75-100 ms left
    N["nw_cliff_mid"] = float(nec.iloc[3]["row t shows target"])  # 50-75 ms left
    N["nw_cliff_lo"] = float(nec.iloc[4]["row t shows target"])   # 25-50 ms left
    N["nw_cliff_n"] = int(nec["n"].sum())
    nsub = t("c9ext_nuwins_subsecond_all")
    N["nw_native_0"] = float(nsub[nsub.dataset == "pooled"].iloc[0]["tau +0ms"])
    N["nw_native_p100"] = float(nsub[nsub.dataset == "pooled"].iloc[0]["tau +100ms"])

    # ---- C10 (round 3): the event-level loss, and the floor the instrument imposes
    cr1 = t("c10_crc_frontier")
    cr1 = cr1[cr1.horizon_s == 1.0].set_index("alpha")
    cr3 = t("c10_crc_frontier")
    cr3 = cr3[cr3.horizon_s == 3.0].set_index("alpha")
    N["crc_unresolvable1"] = float(cr1["unresolvable_event_share"].iloc[0])
    N["crc_unresolvable3"] = float(cr3["unresolvable_event_share"].iloc[0])
    N["crc_ev_feasible1_max"] = float(cr1["feasible_events"].max())
    N["crc_ev_feasible3_20"] = float(cr3.loc[0.20, "feasible_events"])
    N["crc_ev_loss3_20"] = float(cr3.loc[0.20, "mean_unit_loss_events"])
    N["crc_ev_alarm3_20"] = float(cr3.loc[0.20, "alarm_rate_events_mean"])
    N["crc_ev_loss3_30"] = float(cr3.loc[0.30, "mean_unit_loss_events"])
    N["crc_ev_alarm3_30"] = float(cr3.loc[0.30, "alarm_rate_events_mean"])

    # ---- C9 (round 3): which columns actually carry the leak
    sl = t("c9sel_lag_scope")
    slg = sl[(sl.learner == "LightGBM")].set_index(["arm", "horizon_s"])
    for a, tag in (("none", "v1"), ("neighbour", "nbr"), ("serving", "srv"),
                   ("assignment", "asg"), ("all", "v2")):
        N[f"sel_{tag}_auprc1"] = float(slg.loc[(a, 1.0), "auprc"])
        N[f"sel_{tag}_auprc5"] = float(slg.loc[(a, 5.0), "auprc"])
        N[f"sel_{tag}_auroc1"] = float(slg.loc[(a, 1.0), "auroc"])
        N[f"sel_{tag}_cols"] = int(slg.loc[(a, 1.0), "columns_lagged"])
    sd = t("c9sel_lag_decomposition").set_index("horizon_s")
    N["sel_share_nbr"] = float(sd.loc[1.0, "share of the v1-v2 drop caused by the neighbour and gap columns alone"])
    N["sel_share_srv"] = float(sd.loc[1.0, "share caused by the serving-cell radio scalars alone"])
    N["sel_share_gps"] = float(sd.loc[1.0, "share attributable to lagging GPS as well"])

    # ---- main LOCO results
    m = t("c3_main_loco")
    lg = m[m.learner == "LightGBM"].set_index("horizon_s")
    for h, tag in ((1.0, "1"), (5.0, "5")):
        N[f"auprc{tag}"] = float(lg.loc[h, "auprc"])
        N[f"auroc{tag}"] = float(lg.loc[h, "auroc"])
        N[f"lift{tag}"] = float(lg.loc[h, "lift"])
        N[f"ece{tag}"] = float(lg.loc[h, "ece"])
    a3 = m[m.learner.str.startswith("Event A3")].set_index("horizon_s")
    N["a3_auprc1"] = float(a3.loc[1.0, "auprc"])
    N["a3_lift1"] = float(a3.loc[1.0, "lift"])
    N["a3_auroc1"] = float(a3.loc[1.0, "auroc"])
    N["hist_lift1"] = float(m[(m.learner.str.startswith("History block")) & (m.horizon_s == 1.0)]["lift"].iloc[0])

    pc = t("c3_main_loco_per_capture")
    g = pc[(pc.learner == "LightGBM") & (pc.horizon_s == 1.0)]
    N["loco_lift_min"], N["loco_lift_max"] = float(g["lift"].min()), float(g["lift"].max())
    N["loco_auroc_min"], N["loco_auroc_max"] = float(g["auroc"].min()), float(g["auroc"].max())
    N["loco_worst"] = str(g.loc[g["auprc"].idxmin(), "held_out_capture"])
    N["loco_auroc_highway"] = float(g.loc[g.held_out_capture.str.contains("highway"), "auroc"].iloc[0])

    # ---- lag effect (ablation)
    ab = t("c18_ablation").set_index(["variant", "horizon_s"])
    N["lag0_auprc1"] = float(ab.loc[("main, NO lag (v1 alignment)", 1.0), "auprc_mean"])
    N["lag0_auprc5"] = float(ab.loc[("main, NO lag (v1 alignment)", 5.0), "auprc_mean"])
    N["lag0_auroc1"] = float(ab.loc[("main, NO lag (v1 alignment)", 1.0), "auroc_mean"])
    N["abl_sig_auprc1"] = float(ab.loc[("rf+mobility+history+signalling", 1.0), "auprc_mean"])
    N["abl_sigonly_auprc1"] = float(ab.loc[("signalling only", 1.0), "auprc_mean"])
    N["censor_delta_lift1"] = float(ab.loc[("main, re-establishment censored", 1.0), "lift_mean"]
                                    - ab.loc[("rf+mobility+history (main)", 1.0), "lift_mean"])
    N["lag_effect_pct"] = 100 * (N["lag0_auprc1"] / N["auprc1"] - 1)
    # Feature counts are read, never typed. Five different totals (152/112/106/107/120)
    # appeared in the draft because each was written by hand at its point of use.
    fb = t("c0_feature_blocks").set_index("block")["count"]
    N["n_feat_radio"] = int(fb["Radio"])
    N["n_feat_mobility"] = int(fb["Mobility"])
    N["n_feat_history"] = int(fb["History"])
    N["n_features"] = int(fb["Main feature set"])
    N["n_feat_signalling"] = int(fb["Signalling (ablation only)"])
    N["n_feat_matrix"] = int(fb["Design matrix as built"])
    assert N["n_features"] == N["n_feat_radio"] + N["n_feat_mobility"] + N["n_feat_history"]
    assert N["n_feat_matrix"] == N["n_features"] + N["n_feat_signalling"]

    sf = t("c14_single_feature_auroc")
    exp_only = sf[~sf.feature.str.startswith(("sig_", "cfg_", "t_since_prev", "ho_count", "has_prev",
                                              "last_ho"))]
    N["best_export_feature"] = str(exp_only.iloc[0]["feature"])
    N["best_export_auroc"] = float(exp_only.iloc[0]["auroc_1s"])
    N["best_single"] = str(sf.iloc[0]["feature"])
    N["best_single_auroc"] = float(sf.iloc[0]["auroc_1s"])
    N["dwell_auroc"] = float(sf.loc[sf.feature == "t_since_prev_ho_s", "auroc_1s"].iloc[0])
    gapf = sf[sf.feature.isin(["gap_serving_best_nbr", "gap_serving_nbr1"])]
    N["gap_auroc"] = float(gapf["auroc_1s"].max())
    sf0 = t("c14_single_feature_auroc_lag0") if (T / "c14_single_feature_auroc_lag0.csv").exists() else None
    N["lag0_dwell_auroc"] = float(sf0.loc[sf0.feature == "serving_dwell_s", "auroc_1s"].iloc[0]) if sf0 is not None \
        else float("nan")

    dw = t("c8_dwell_direction")
    N["dwell_p_short"] = float(dw.iloc[0]["p_ho_1s"])
    N["dwell_p_long"] = float(dw.iloc[-1]["p_ho_1s"])
    bs = t("c8_burst_strata")
    q = bs[(bs.learner == "LightGBM") & (bs.horizon_s == 1.0)].set_index("stratum")
    qi = [i for i in q.index if i.startswith("quiet")][0]
    bi = [i for i in q.index if i.startswith("in burst")][0]
    N["burst_quiet_lift1"] = float(q.loc[qi, "lift"])
    N["burst_inburst_lift1"] = float(q.loc[bi, "lift"])
    N["burst_quiet_prev1"] = float(q.loc[qi, "prevalence"])
    N["burst_inburst_prev1"] = float(q.loc[bi, "prevalence"])

    # ---- protocol ladder
    inf = t("c2_inflation_by_horizon")
    i1 = inf[inf.horizon_s == 1.0].set_index("learner")
    N["infl_row_lgbm"] = float(i1.loc["lgbm", "inflation_random_vs_loco_%"])
    N["infl_chunk_lgbm"] = float(i1.loc["lgbm", "inflation_chunk_vs_loco_%"])
    N["infl_block_lgbm"] = abs(float(100 * (i1.loc["lgbm", "blocked_purged"] / i1.loc["lgbm", "loco"] - 1)))
    N["infl_row_gru"] = float(i1.loc["gru", "inflation_random_vs_loco_%"]) if "gru" in i1.index else float("nan")
    N["infl_row_a3"] = float(i1.loc["a3", "inflation_random_vs_loco_%"]) if "a3" in i1.index else float("nan")
    lab = {"lgbm": "LightGBM", "lr": "logistic regression", "mlp": "the MLP", "gru": "the GRU",
           "tcn": "the TCN", "transformer": "the Transformer", "a3": "the A3 rule"}
    learned = i1.drop(index=[x for x in ["a3"] if x in i1.index])
    N["top_loco"] = lab[learned["loco"].idxmax()]
    N["top_random"] = lab[learned["random_row"].idxmax()]
    N["infl_row_top_loco"] = float(learned.loc[learned["loco"].idxmax(), "inflation_random_vs_loco_%"])
    N["infl_row_top_random"] = float(learned.loc[learned["random_row"].idxmax(), "inflation_random_vs_loco_%"])

    # ---- coherence
    cv = t("c11_coherence_violations").set_index("arm")
    cm = t("c11_coherence_metrics").set_index(["arm", "horizon_s"])
    # Every violation figure quoted in the manuscript is the SINGLE-FIT rate: a deployed
    # system is one fit, and averaging predictions over seeds is an ensemble that smooths
    # violations away.  The seed-averaged column is kept in the table beside it [C11, round 2].
    N["viol_indep"] = float(cv.loc["independent", "rows_violating_single_fit"])
    N["viol_indep_mean"] = float(cv.loc["independent", "mean_violation_if_any_single_fit"])
    N["viol_indep_max"] = float(cv.loc["independent", "max_violation_single_fit"])
    N["viol_iso"] = float(cv.loc["independent + isotonic", "rows_violating_single_fit"])
    N["viol_indep_ens"] = float(cv.loc["independent", "rows_violating_seed_mean"])
    N["viol_iso_ens"] = float(cv.loc["independent + isotonic", "rows_violating_seed_mean"])
    N["ece1_indep"] = float(cm.loc[("independent", 1.0), "ece"])
    N["ece1_cummax"] = float(cm.loc[("independent + cumulative max", 1.0), "ece"])
    N["ece1_hazard"] = float(cm.loc[("hazard", 1.0), "ece"])
    N["ece1_isopav"] = float(cm.loc[("independent + isotonic + PAV", 1.0), "ece"])
    # the hazard arm does not out-rank the control; Section 5.4 now says so
    N["auprc1_indep"] = float(cm.loc[("independent", 1.0), "auprc"])
    N["auprc1_hazard"] = float(cm.loc[("hazard", 1.0), "auprc"])
    # Paired bootstrap on identical resampled blocks: the only basis on which a
    # difference of 0.010 may be called real [round 3, concern K].
    pdif = t("c11_paired_differences")
    pd1 = pdif[pdif.horizon_s == 1.0].set_index(["arm", "metric"])
    capcols = [c for c in pdif.columns if c.startswith("campaign_")]
    for tag, arm in (("indep", "independent"), ("cummax", "independent + cumulative max"),
                     ("isopav", "independent + isotonic + PAV")):
        for met in ("auprc", "ece"):
            r = pd1.loc[(arm, met)]
            N[f"dif_{met}_{tag}"] = float(r["difference"])
            N[f"dif_{met}_{tag}_lo"] = float(r["block_ci_low"])
            N[f"dif_{met}_{tag}_hi"] = float(r["block_ci_high"])
            # the only defensible summary on four units: how many share the sign
            N[f"dif_{met}_{tag}_wins"] = int(r["campaigns_favouring_hazard"])
            N[f"dif_{met}_{tag}_same_sign"] = bool(r["sign_consistent"])
            N[f"dif_{met}_{tag}_percap"] = [float(r[c]) for c in capcols if pd.notna(r[c])]
    N["min_p"] = 0.125
    N["n_auprc_same_sign"] = int(pdif[pdif.metric == "auprc"]["sign_consistent"].sum())
    # Per-campaign calibration MUST come from the coherence arm, which is the arm Tables
    # 5.6 and 5.6b report. An earlier draft took it from the tuned arm instead and so
    # printed "lower calibration error on 0 of the four campaigns" beside a pooled result
    # that favoured the hazard arm -- two different experiments compared as if they were one.
    cpc = t("c11_coherence_per_capture")
    cpc1 = cpc[cpc.horizon_s == 1.0].pivot_table(index="capture", columns="arm", values="ece")
    N["n_campaigns"] = int(len(cpc1))
    N["ece_wins"] = int((cpc1["hazard"] < cpc1["independent"]).sum())
    N["ece_wins_iso"] = int((cpc1["hazard"] < cpc1["independent + isotonic + PAV"]).sum())
    N["ece_haz_percap_min"] = float(cpc1["hazard"].min())
    N["ece_haz_percap_max"] = float(cpc1["hazard"].max())

    # ---- CRC
    cr = t("c10_crc_frontier")
    c20 = cr[(cr.alpha == 0.20) & (cr.horizon_s == 1.0)].iloc[0]
    c05 = cr[(cr.alpha == 0.05) & (cr.horizon_s == 1.0)].iloc[0]
    N["crc_cross_loss20"] = float(c20["mean_unit_loss"])
    N["crc_cross_ok20"] = float(c20["rotations_with_mean_loss_le_alpha"])
    N["crc_rotations"] = int(c20["rotations"])
    ex = t("c10_crc_pooled_chunk_split")
    e20 = ex[(ex.alpha == 0.20) & (ex.horizon_s == 1.0)].iloc[0]
    e05 = ex[(ex.alpha == 0.05) & (ex.horizon_s == 1.0)].iloc[0]
    N["crc_loss20"] = float(e20["mean_unit_loss"])
    N["crc_alarm20"] = float(e20["alarm_rate"])
    N["crc_alarm05"] = float(e05["alarm_rate"])
    rot = t("c10_crc_rotations")
    N["crc_n_units"] = int(rot["n_calib_units"].median())
    N["crc_n_units_min"] = int(rot["n_calib_units"].min())
    N["crc_n_units_max"] = int(rot["n_calib_units"].max())
    N["crc_floor"] = 1 / (N["crc_n_units"] + 1)
    N["crc_feasible05"] = float(rot[(rot.alpha == 0.05) & (rot.horizon_s == 1.0)]["feasible"].mean())
    N["crc_pool_units"] = int(ex["n_calib_units"].iloc[0])

    # ---- external
    ext = t("c6_external_signalling_only")
    e1 = ext[ext.horizon_s == 1.0].set_index("setting")
    N["ext_ours_to_pub_auroc"] = float(e1.loc["ours -> public (no refit)", "auroc"])
    N["ext_pub_auroc"] = float(e1.loc["public, leave-one-file-out", "auroc"])
    N["ext_ours_auroc"] = float(e1.loc["ours, leave-one-capture-out", "auroc"])

    ex_c = t("c9ext_cell_contamination").iloc[0]
    N["ext_align_share"] = float(ex_c["share_closer_to_new_cell"])
    N["ext_align_n"] = int(ex_c["cell_changes_tested"])
    ex_i = t("c9ext_inflation").set_index("features_from")
    N["ext_gain_t"] = float(ex_i.loc["gain from t-1 to t (one second fresher)", "auprc"])
    N["ext_gain_t1"] = float(ex_i.loc["gain from t-2 to t-1 (one second fresher)", "auprc"])
    N["ext_traces"] = int(t("c9ext_kinematic_summary").iloc[0]["traces"])

    # ---- events
    ev = t("c18_event_metrics_pooled_fpr5").set_index("horizon_s")
    N["ceiling1"] = float(ev.loc[1.0, "grid_ceiling"])
    N["det1"] = float(ev.loc[1.0, "detection_rate"])
    N["det5"] = float(ev.loc[5.0, "detection_rate"])
    N["fa_hour1"] = float(ev.loc[1.0, "false_alarms_per_hour"])
    N["fa_km1"] = float(ev.loc[1.0, "false_alarms_per_km"])
    N["lead1"] = float(ev.loc[1.0, "lead_median_s"])
    N["lead5"] = float(ev.loc[5.0, "lead_median_s"])
    N["fa_hour5"] = float(ev.loc[5.0, "false_alarms_per_hour"])

    # ---- signalling
    sg = t("c5_offset_sign_handover_weighted").iloc[0]
    N["a3_pos_share"] = float(sg["A3_positive_share_of_A3"])
    N["a3_pos"] = int(sg["A3_positive_offset"]) + int(sg["A3_zero_offset"])
    N["a3_attributed"] = int(sg["attributed_to_a_report_within_2s"])
    N["a3_ho"] = int(sg["attributed_A3"])
    # The positive-offset share is NOT the dominant profile's share: an earlier draft
    # attributed the whole 75 % to the +1 dB profile alone, which produces fewer than that.
    # NB: match the ONE dominant profile, not every positive-offset profile — grouping all
    # "A3 +" rows reproduces the positive-offset total and so reproduces the error.
    _pf = t("c5_handover_profiles_v2")
    _pos = _pf[_pf["profile"].str.startswith("A3 +")]
    _name = _pos.groupby("profile")["handovers"].sum().idxmax()
    _dom = _pos[_pos["profile"] == _name]
    N["a3_dom_profile"] = str(_name)
    N["a3_dom_ho"] = int(_dom["handovers"].sum())
    assert N["a3_dom_ho"] < N["a3_pos"], (N["a3_dom_ho"], N["a3_pos"])
    N["a3_dom_share_of_a3"] = N["a3_dom_ho"] / N["a3_ho"]
    N["a3_pos_other"] = N["a3_pos"] - N["a3_dom_ho"]
    N["report_to_command_ms"] = float(sg["median_ms_report_to_command"])
    cu = t("c7_a3_conversion_by_unit")
    N["conv_rep_declined"] = float(cu[(cu.unit == "per report (v1 unit)") & (cu.stratum == "pooled")]["declined_share"].iloc[0])
    EP_ANY = "per trigger episode (any command within 2 s)"
    EP_1TO1 = "per trigger episode (one-to-one, owns the command)"
    N["conv_ep_declined"] = float(cu[(cu.unit == EP_ANY) & (cu.stratum == "pooled")]["declined_share"].iloc[0])
    N["conv_ep1_declined"] = float(cu[(cu.unit == EP_1TO1) & (cu.stratum == "pooled")]["declined_share"].iloc[0])
    mult = t("c7_episode_command_multiplicity").set_index("episode set")
    N["conv_mult_any"] = int(mult.loc["A3 episodes", "episodes with a command within 2 s"])
    N["conv_mult_own"] = int(mult.loc["A3 episodes", "episodes owning a command (one-to-one)"])
    N["conv_mult_factor"] = float(mult.loc["A3 episodes", "inflation factor"])
    ep = t("c7_episode_summary").iloc[0]
    N["a3_reports"] = int(ep["a3_reports"])
    N["a3_episodes"] = int(ep["a3_episodes"])
    N["reports_per_episode"] = float(ep["reports_per_episode"])
    prof = t("c7_a3_conversion_by_profile")
    dom = prof[prof.profile.str.startswith("+1 dB") & (prof.relation == "intra-frequency")].iloc[0]
    N["conv_dom_declined"] = float(dom["declined_share"])
    N["conv_dom_declined_1to1"] = float(dom["declined_share_one_to_one"])
    mon = prof[prof.profile.str.startswith("-15 dB") & (prof.relation == "intra-frequency")].iloc[0]
    N["conv_mon_declined"] = float(mon["declined_share"])
    N["conv_mon_declined_1to1"] = float(mon["declined_share_one_to_one"])

    # ---- timeline v2 parser counters (recorded by stage 23 run log)
    tl = t("c_timeline_v2_counters") if (T / "c_timeline_v2_counters.csv").exists() else None
    if tl is not None:
        N["tl_removals"] = int(tl["measid_removals"].sum())
        N["tl_swaps"] = int(tl["interfreq_swaps"].sum())
        N["tl_resets"] = int(tl["config_resets"].sum())
        N["tl_disagree"] = float(1 - tl["agreement_with_v1"].mean())
        N["a3_share_min"] = float(tl["a3_share"].min())
        N["a3_share_max"] = float(tl["a3_share"].max())

    # ---- event stream quantities that did not change (from the frozen v1 tables)
    ho = pd.read_csv(T / "c5_handover_attribution_v2_rows.csv", parse_dates=["t"])
    gaps = ho.sort_values(["capture", "t"]).groupby("capture")["t"].diff().dt.total_seconds().dropna()
    N["mean_gap_s"] = float(gaps.mean())
    N["median_gap_s"] = float(gaps.median())
    pp = t("c13_pingpong_definitions")
    N["pp_strict"] = float(pp.iloc[0]["rate"])
    N["pp_pci"] = float(pp.iloc[1]["rate"])
    N["pp_any"] = float(pp.iloc[2]["rate"])
    N["pingpong"] = N["pp_strict"]
    gr = t("c13_pingpong_grid")
    N["pp_grid_min"], N["pp_grid_max"] = float(gr["rate"].min()), float(gr["rate"].max())
    _sf = t("c13_pingpong_strata").set_index("stratum")
    st, sn = _sf["rate"], _sf["n_pingpong"]
    N["pp_intra"] = float(st["intra-frequency handovers"])
    N["pp_inter"] = float(st["inter-frequency handovers"])
    N["pp_highway"] = float(st["highway campaign"])
    N["pp_urban"] = float(st["urban campaigns"])
    N["pp_n_total"] = int(sn["all commands"])
    # the two stratifications must partition the same set of returns
    assert int(sn["intra-frequency handovers"] + sn["inter-frequency handovers"]) == N["pp_n_total"]
    assert int(sn["highway campaign"] + sn["urban campaigns"]) == N["pp_n_total"]
    # ---- round 5: sensitivity of the four post-hoc windows, and the burst stratification
    bl = t("c19_sens_block_length")
    N["sens_block_min"] = float(bl["inflation_vs_loco_%"].min())
    N["sens_block_max"] = float(bl["inflation_vs_loco_%"].max())
    N["sens_block_range"] = f"{bl['block_length_s'].min():.0f} to {bl['block_length_s'].max():.0f}"
    N["sens_block_all_positive"] = bool((bl["inflation_vs_loco_%"] > 0).all())
    pg = t("c19_sens_purge")
    N["sens_purge_min"] = float(pg["inflation_vs_loco_%"].min())
    N["sens_purge_max"] = float(pg["inflation_vs_loco_%"].max())
    bc = t("c19_sens_burst_cutoff").pivot_table(index="burst_cutoff_s", columns="stratum",
                                                values="lift_1s")
    N["sens_burst_quiet_min"] = float(bc["quiet"].min())
    N["sens_burst_quiet_max"] = float(bc["quiet"].max())
    N["sens_burst_burst_min"] = float(bc["in burst"].min())
    N["sens_burst_burst_max"] = float(bc["in burst"].max())
    N["sens_burst_order_holds"] = bool((bc["quiet"] > bc["in burst"]).all())
    N["sens_burst_n"] = int(len(bc))
    bi = t("c19_burst_initiators").set_index("positive rows at 1 s")
    N["burst_init_quiet_share"] = float(bi.loc["quiet rows", "share starting a new burst"])
    N["burst_init_quiet_n"] = int(bi.loc["quiet rows", "n"])
    N["burst_init_inburst_share"] = float(bi.loc["in-burst rows", "share starting a new burst"])
    if (T / "c19_sens_blank.csv").exists():
        bw = t("c19_sens_blank")
        N["sens_blank_lift_min"] = float(bw["lift_1s"].min())
        N["sens_blank_lift_max"] = float(bw["lift_1s"].max())
    # ---- round 5: trace-level evidence for the alignment residual
    re_ = t("c20_residual_evidence").iloc[0]
    N["resid_n"] = int(re_["residual: row t carries the source"])
    N["resid_tp1_n"] = int(re_["of the residual, row t+1 carries the target"])
    N["resid_tp1_share"] = N["resid_tp1_n"] / max(N["resid_n"], 1)
    N["resid_median_margin"] = float(re_["median margin of the residual (s)"])
    N["resid_median_margin_hit"] = float(re_["median margin of the contaminated (s)"])
    cs = t("c20_case_studies")
    N["case_n_each"] = int(cs.groupby("case").size().max())
    N["case_thr"] = float(cs["threshold"].iloc[0])

    # the top learners overlap completely; Section 5.2 must say so rather than rank them
    _l1 = t("c3_main_loco")
    _l1 = _l1[_l1.horizon_s == 1.0].sort_values("auprc", ascending=False)
    N["rank1_learner"] = str(_l1.iloc[0]["learner"])
    N["rank2_learner"] = str(_l1.iloc[1]["learner"])
    N["rank2_auprc"] = float(_l1.iloc[1]["auprc"])
    N["rank3_learner"] = str(_l1.iloc[2]["learner"])
    N["rank3_auprc"] = float(_l1.iloc[2]["auprc"])
    N["rank_overlap_n"] = int((_l1["auprc_ci_low"] < _l1.iloc[0]["auprc_ci_high"]).sum())

    gof = t("c_hawkes_gof").iloc[0]
    N["ogata_D"] = float(gof["ks_statistic_D"])
    N["ogata_p"] = float(gof["p_value"])
    N["ogata_n"] = int(gof["n_residuals"])
    N["ogata_mean_resid"] = float(gof["mean_residual"])
    hw = t("c_hawkes_fit").set_index("stratum")
    br = [c for c in hw.columns if "branch" in c][0]
    N["hawkes_pooled"] = float(hw.loc["pooled", br])
    per = hw.drop(index="pooled")[br]
    N["hawkes_min"], N["hawkes_max"] = float(per.min()), float(per.max())
    m = t("c3_main_loco")
    seq = m[m.learner.isin(["GRU", "TCN", "Transformer"]) & (m.horizon_s == 1.0)]
    N["best_seq_auprc1"] = float(seq["auprc"].max()) if len(seq) else float("nan")
    return N


if __name__ == "__main__":
    n = build()
    for k, v in sorted(n.items()):
        print(f"{k:28s} {v}")

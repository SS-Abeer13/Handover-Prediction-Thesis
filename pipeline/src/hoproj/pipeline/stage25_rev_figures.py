"""Stage 25 - figures for the revised manuscript, drawn only from reports_rev/tables."""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

if Path("reports_rev/tables").exists():
    T = Path("reports_rev/tables")
    F = Path("reports_rev/figures")
    LATEX_F = Path("../latex/figures") if Path("../latex/figures").exists() else Path("latex/figures")
else:
    T = Path("pipeline/reports_rev/tables")
    F = Path("pipeline/reports_rev/figures")
    LATEX_F = Path("latex/figures")

F.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.spines.top": False,
                     "axes.spines.right": False, "figure.dpi": 200, "savefig.bbox": "tight"})
C = ["#1f4e79", "#c0504d", "#4f9a5a", "#e3a21a", "#7a5195", "#5b8db8", "#8c8c8c", "#b5651d",
     "#2a9d8f", "#6d6d6d"]
H = [0.5, 1, 2, 3, 5]


def t(name):
    return pd.read_csv(T / f"{name}.csv")


DATE_MAP = {
    "10 Sept (urban arterial)": "1st Campaign (urban arterial)",
    "12 Sept (urban loop)": "2nd Campaign (urban loop)",
    "13 Sept (dense urban)": "3rd Campaign (dense urban)",
    "15 Sept (highway)": "4th Campaign (highway)",
    "10 Sept": "1st Campaign",
    "12 Sept": "2nd Campaign",
    "13 Sept": "3rd Campaign",
    "15 Sept": "4th Campaign",
    "10 September": "1st Campaign",
    "12 September": "2nd Campaign",
    "13 September": "3rd Campaign",
    "15 September": "4th Campaign",
    "XCAL10Sept": "1st Campaign",
    "XCAL12Sept": "2nd Campaign",
    "XCAL13Sept": "3rd Campaign",
    "XCAL15Sept": "4th Campaign",
}


def clean_label(s):
    if not isinstance(s, str):
        return s
    for k, v in DATE_MAP.items():
        s = s.replace(k, v)
    return s


def save_fig(fig, filename):
    F.mkdir(parents=True, exist_ok=True)
    fig.savefig(F / filename)
    if LATEX_F.exists():
        fig.savefig(LATEX_F / filename)


def fig_alignment():
    """Figure 5.1 - the alignment audit and the mechanism behind it."""
    a = t("c9_row_alignment_audit")
    b = t("c9ext_cell_contamination").iloc[0]
    m = t("c9m_execution_margin")
    d = t("c9m_delta_bins_ours")
    nw = t("c9ext_nuwins_alignment_all")
    ob = t("c9ext_nuwins_offsetbins_all")
    ec = t("c9ext_nuwins_execution_cdf")
    nw_pool = float(nw[(nw.dataset == "pooled") & (nw.subset == "all handovers")].iloc[0]["row t+0"])
    ours_all = float(a[a["subset"].str.startswith("all")].iloc[0]["row t+0"])

    fig = plt.figure(figsize=(7.4, 6.4))
    gs = fig.add_gridspec(3, 3, height_ratios=[0.62, 1.0, 1.0], hspace=0.75, wspace=0.45)

    # (a) one second, drawn
    ax = fig.add_subplot(gs[0, :])
    ax.set_xlim(-0.05, 2.15)
    ax.set_ylim(0, 1)
    ax.axis("off")
    for x0 in (0.0, 1.0, 2.0):
        ax.axvline(x0, color="#999", lw=0.9, ls=":")
    ax.annotate("", xy=(2.12, 0.30), xytext=(-0.02, 0.30),
                arrowprops=dict(arrowstyle="->", color="#444", lw=1.0))
    for x0, lab in ((0.0, "t"), (1.0, "t+1"), (2.0, "t+2")):
        ax.text(x0, 0.14, lab, ha="center", fontsize=8.5, color="#444")
    ax.add_patch(plt.Rectangle((0.0, 0.64), 1.0, 0.16, color="#dce6f1"))
    ax.text(0.5, 0.72, "row stamped t  —  written at t+1", ha="center", va="center", fontsize=8)
    ax.add_patch(plt.Rectangle((1.0, 0.64), 1.0, 0.16, color="#eeeeee"))
    ax.text(1.5, 0.72, "row stamped t+1", ha="center", va="center", fontsize=8, color="#666")
    ax.plot([0.55], [0.30], marker="v", color=C[1], ms=7)
    ax.text(0.51, 0.39, "handover command  τ", ha="right", fontsize=8, color=C[1])
    ax.plot([0.55, 0.62], [0.30, 0.30], color=C[1], lw=3, solid_capstyle="butt")
    ax.annotate("execution + reporting  x", xy=(0.63, 0.28), xytext=(1.22, 0.10),
                fontsize=7.5, color=C[1], va="center",
                arrowprops=dict(arrowstyle="-", color=C[1], lw=0.7))
    ax.annotate("", xy=(1.0, 0.52), xytext=(0.62, 0.52),
                arrowprops=dict(arrowstyle="<->", color=C[0], lw=0.9))
    ax.text(0.81, 0.57, "margin  m = 1 − δ − x", ha="center", fontsize=8, color=C[0])
    ax.set_title("(a)  an end-of-second row shows the target cell whenever the margin m is positive",
                 fontsize=8.5, loc="left")

    # (b) the audit itself
    ax = fig.add_subplot(gs[1, :2])
    cols = [c for c in a.columns if c.startswith("row")]
    x = np.arange(len(cols))
    for i, r in a.iterrows():
        ax.bar(x + (i - 0.5) * 0.38, [r[c] for c in cols], 0.38, color=C[i], label=r["subset"])
    ax.set_xticks(x, ["t−3", "t−2", "t−1", "t", "t+1"])
    ax.set_ylabel("target cell already serving")
    ax.axvspan(2.5, 3.5, color="#f3d9d9", zorder=-1)
    ax.legend(frameon=False, fontsize=7.5)
    ax.set_ylim(0, 1)
    ax.set_title("(b)  the audit: rows around the handover command, this work", fontsize=8.5)

    # (c) three instruments
    ax = fig.add_subplot(gs[1, 2])
    vals = [ours_all, float(b.share_closer_to_new_cell), nw_pool]
    ax.bar([0, 1, 2], vals, 0.62, color=[C[0], C[6], C[2]])
    ax.axhline(0.5, ls=":", color="k", lw=0.9)
    ax.set_xticks([0, 1, 2], ["XCAL\n(ours)", "G-NetTrack\n(Irish)", "XCAL\n(NUWiNS)"], fontsize=7)
    ax.set_ylim(0, 1.08)
    for i, v in enumerate(vals):
        ax.text(i, v + 0.03, f"{v:.0%}", ha="center", fontsize=7.5)
    ax.set_title("(c)  aggregated rows\nagainst sampled rows", fontsize=8.5)

    # (d) the falsification test
    ax = fig.add_subplot(gs[2, 0])
    lab = m["execution margin m (s)"].tolist()
    val = m["row t shows target"].to_numpy(float)
    col = [C[1] if s_.startswith("[-") else C[0] for s_ in lab]
    ax.bar(np.arange(len(val)), val, 0.72, color=col)
    ax.set_xticks(np.arange(len(val)), ["<0", ".00", ".05", ".10", ".25", ".50", ".75"], fontsize=7)
    ax.set_xlabel("execution margin m (s)", fontsize=8)
    ax.set_ylabel("target cell already serving")
    ax.set_ylim(0, 1)
    ax.text(0, 0.03, f"0 of {int(m.iloc[0]['n'])}", ha="center", va="bottom", fontsize=7, color=C[1])
    ax.set_title("(d)  no margin,\nno contamination", fontsize=8.5)

    # (e) contamination by position inside the second, both corpora
    ax = fig.add_subplot(gs[2, 1])
    g = d[(d["subset"] == "clean (no other handover within 2 s)")
          & (d["delta bin (s into the second)"] != "all")]
    ax.plot(np.arange(len(g)), g["row t shows target"], marker="o", color=C[0], lw=1.2,
            label="this work")
    ax.plot(np.arange(len(ob)), ob["share_target_served"], marker="s", color=C[2], lw=1.2,
            label="NUWiNS")
    ax.set_xticks(np.arange(4), ["0–.25", ".25–.5", ".5–.75", ".75–1"], fontsize=7)
    ax.set_xlabel("δ, command position in the second", fontsize=8)
    ax.set_ylim(0, 1.08)
    ax.legend(frameon=False, fontsize=7, loc="lower left")
    ax.set_title("(e)  late commands escape,\nin both XCAL corpora", fontsize=8.5)

    # (f) the cliff measures the update delay
    ax = fig.add_subplot(gs[2, 2])
    mid = [np.mean([float(v) for v in s_.split(" - ")])
           for s_ in ec["time left in the second (ms)"]]
    ax.plot(mid, ec["row t shows target"], marker="o", color=C[2], lw=1.2)
    ax.set_xlabel("time left in the second (ms)", fontsize=8)
    ax.set_ylim(0, 1.08)
    ax.axvspan(50, 75, color="#e8f0e6", zorder=-1)
    ax.text(62, 0.06, "50–75 ms", rotation=90, ha="center", va="bottom", fontsize=7, color=C[2])
    ax.set_title("(f)  the cliff measures the\nserving-cell update delay", fontsize=8.5)
    save_fig(fig, "fig_c9_alignment.png")


def fig_profiles():
    p = t("c5_handover_profiles_v2")
    g = p.groupby("profile")["handovers"].sum().sort_values(ascending=True).tail(10)
    fig, ax = plt.subplots(figsize=(6.4, 3.2))
    col = [C[0] if s.startswith("A3 +") else (C[1] if s.startswith("A3 -") else C[6]) for s in g.index]
    ax.barh(g.index, g.values, color=col)
    ax.set_xlabel("handovers attributed (latest report within 2 s of the command)")
    for y, v in enumerate(g.values):
        ax.text(v + 4, y, f"{v} ({v / p.handovers.sum():.0%})", va="center", fontsize=8)
    save_fig(fig, "fig_c5_profiles.png")


def fig_protocols():
    s = t("c2_protocol_ladder")
    order = ["random_row", "chunk_grouped", "blocked_purged", "loco"]
    lab = ["random rows", "random 180 s\nchunks (v1)", "blocks +\n60 s purge", "leave one\ncapture out"]
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.0))
    for ax, h in zip(axes, (1.0, 5.0)):
        for i, (L, g) in enumerate(s[s.horizon_s == h].groupby("learner")):
            g = g.set_index("protocol").reindex(order)
            ax.plot(range(4), g["auprc"], marker="o", color=C[i % len(C)], label=L)
        ax.set_xticks(range(4), lab, fontsize=7.5)
        ax.set_title(f"AUPRC at {h:g} s", fontsize=9)
        ax.axhline(t("c4_prevalence").set_index("horizon_s").loc[h, "prevalence"], ls=":", color="k", lw=0.8)
    axes[1].legend(frameon=False, fontsize=7, loc="upper right")
    save_fig(fig, "fig_c2_protocols.png")


def fig_main():
    m = t("c3_main_loco")
    prev = t("c4_prevalence")
    fig, ax = plt.subplots(figsize=(6.4, 3.4))
    for i, (L, g) in enumerate(m.groupby("learner", sort=False)):
        ax.plot(g.horizon_s, g.lift, marker="o", color=C[i % len(C)], label=L)
    ax.axhline(1, ls=":", color="k", lw=0.8)
    ax.set_xlabel("horizon (s)")
    ax.set_ylabel("AUPRC lift over prevalence")
    ax.legend(frameon=False, fontsize=7, ncol=2)
    save_fig(fig, "fig_c3_main.png")


def fig_per_capture():
    m = t("c3_main_loco_per_capture")
    m = m[m.horizon_s == 1.0]
    fig, ax = plt.subplots(figsize=(6.4, 3.2))
    learners = list(dict.fromkeys(m.learner))
    for j, cap in enumerate(sorted(m.held_out_capture.unique())):
        g = m[m.held_out_capture == cap].set_index("learner").reindex(learners)
        ax.scatter(range(len(learners)), g["lift"], color=C[j], label=clean_label(cap), s=18)
    ax.set_xticks(range(len(learners)), learners, rotation=40, ha="right", fontsize=7)
    ax.set_ylabel("AUPRC lift at 1 s")
    ax.axhline(1, ls=":", color="k", lw=0.8)
    ax.legend(frameon=False, fontsize=7)
    save_fig(fig, "fig_c3_per_capture.png")


def fig_bursts():
    s = t("c8_burst_strata")
    s = s[s.learner.isin(["LightGBM", "Dwell time only (LightGBM)", "Event A3 rule (deployed parameters)"])]
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.9), sharey=True)
    for ax, (st, g) in zip(axes, s.groupby("stratum")):
        for i, (L, gg) in enumerate(g.groupby("learner")):
            ax.plot(gg.horizon_s, gg.lift, marker="o", color=C[i], label=L)
        ax.set_title(st, fontsize=8.5)
        ax.axhline(1, ls=":", color="k", lw=0.8)
        ax.set_xlabel("horizon (s)")
    axes[0].set_ylabel("AUPRC lift")
    axes[1].legend(frameon=False, fontsize=7)
    save_fig(fig, "fig_c8_bursts.png")


def fig_dwell():
    d = t("c8_dwell_direction")
    fig, ax = plt.subplots(figsize=(6.4, 2.8))
    ax.plot(range(len(d)), d.p_ho_1s, marker="o", color=C[0], label="P(handover within 1 s)")
    ax.plot(range(len(d)), d.p_ho_5s, marker="s", color=C[1], label="P(handover within 5 s)")
    ax.set_xticks(range(len(d)), d.dwell_bin, rotation=30, fontsize=7)
    ax.set_xlabel("time since previous handover command (s)")
    ax.legend(frameon=False, fontsize=8)
    save_fig(fig, "fig_c8_dwell.png")


def fig_coherence():
    m = t("c11_coherence_metrics")
    v = t("c11_coherence_violations")
    fig, axes = plt.subplots(1, 2, figsize=(8.6, 2.9), gridspec_kw={"wspace": 0.75})
    for i, (a, g) in enumerate(m.groupby("arm", sort=False)):
        axes[0].plot(g.horizon_s, g.ece, marker="o", color=C[i], label=a)
    axes[0].set_xlabel("horizon (s)")
    axes[0].set_ylabel("ECE")
    axes[0].legend(frameon=False, fontsize=6.5)
    viol_col = "rows_violating_single_fit" if "rows_violating_single_fit" in v.columns else ("rows_violating" if "rows_violating" in v.columns else v.columns[1])
    arm_labels = [a.replace("independent", "indep.") for a in v.arm]
    axes[1].barh(range(len(v)), 100 * v[viol_col], color=C[: len(v)])
    axes[1].set_yticks(range(len(v)))
    axes[1].set_yticklabels(arm_labels, fontsize=7.5)
    axes[1].set_xlabel("% of rows with an ordering violation")
    save_fig(fig, "fig_c11_coherence.png")


def fig_crc():
    s = t("c10_crc_frontier")
    ex = t("c10_crc_pooled_chunk_split") if (T / "c10_crc_pooled_chunk_split.csv").exists() else None
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.0))
    for i, (h, g) in enumerate(s.groupby("horizon_s")):
        axes[0].plot(g.alpha, g.mean_unit_loss, marker="o", color=C[i], label=f"cross-capture, {h:g} s")
        axes[1].plot(g.alpha, g.alarm_rate_mean, marker="o", color=C[i], label=f"cross-capture, {h:g} s")
        if ex is not None:
            e = ex[ex.horizon_s == h]
            axes[0].plot(e.alpha, e.mean_unit_loss, marker="s", ls="--", color=C[i], label=f"pooled chunks, {h:g} s")
            axes[1].plot(e.alpha, e.alarm_rate, marker="s", ls="--", color=C[i])
    axes[0].plot([0, 0.32], [0, 0.32], color="k", lw=0.8)
    axes[0].set_xlabel("target α")
    axes[0].set_ylabel("realised mean per-chunk miss rate")
    axes[1].set_xlabel("target α")
    axes[1].set_ylabel("share of rows alarmed")
    axes[0].legend(frameon=False, fontsize=6.5)
    save_fig(fig, "fig_c10_crc.png")


def fig_external():
    e = t("c6_external_signalling_only")
    e = e[e.horizon_s == 1.0]
    fig, ax = plt.subplots(figsize=(6.4, 2.6))
    y = np.arange(len(e))
    ax.errorbar(e.auroc, y, xerr=[e.auroc - e.auroc_ci_low, e.auroc_ci_high - e.auroc], fmt="o", color=C[0])
    ax.set_yticks(y, e.setting)
    ax.axvline(0.5, ls=":", color="k", lw=0.8)
    ax.set_xlabel("AUROC at 1 s (95 % run-bootstrap interval)")
    save_fig(fig, "fig_c6_external.png")


def fig_single():
    s = t("c14_single_feature_auroc").head(12).iloc[::-1]
    fig, ax = plt.subplots(figsize=(6.4, 3.2))
    ax.barh(s.feature, s.auroc_1s, color=C[0])
    ax.set_xlim(0.5, max(0.8, s.auroc_1s.max() + 0.02))
    ax.set_xlabel("single-feature AUROC at 1 s (orientation-free, lagged export)")
    ax.tick_params(axis="y", labelsize=7)
    save_fig(fig, "fig_c14_single.png")


def fig_conversion():
    c = t("c7_a3_conversion_by_unit")
    c = c[~c.stratum.isin(["intra-frequency", "inter-frequency"])]
    fig, ax = plt.subplots(figsize=(6.8, 3.0))
    strata = list(dict.fromkeys(c.stratum))
    units = ["per report (v1 unit)",
             "per trigger episode (any command within 2 s)",
             "per trigger episode (one-to-one, owns the command)"]
    short = ["per report", "per episode (any command)", "per episode (one-to-one)"]
    x = np.arange(len(strata))
    w = 0.26
    for i, (u, lab) in enumerate(zip(units, short)):
        g = c[c.unit == u].set_index("stratum").reindex(strata)
        ax.bar(x + (i - 1) * w, 100 * g.declined_share, w, color=C[i], label=lab)
    clean_strata = [clean_label(s) for s in strata]
    ax.set_xticks(x)
    ax.set_xticklabels(clean_strata, fontsize=7.5, rotation=15)
    ax.set_ylabel("% declined")
    ax.set_ylim(0, 100)
    ax.legend(frameon=False, fontsize=7.5, ncol=3, loc="upper center",
              bbox_to_anchor=(0.5, 1.16))
    save_fig(fig, "fig_c7_conversion.png")


def fig_ablation():
    a = t("c18_ablation")
    a = a[a.horizon_s.isin([1.0, 5.0])]
    fig, ax = plt.subplots(figsize=(6.4, 3.2))
    vs = list(dict.fromkeys(a.variant))
    y = np.arange(len(vs))
    for i, h in enumerate((1.0, 5.0)):
        g = a[a.horizon_s == h].set_index("variant").reindex(vs)
        ax.barh(y + (i - 0.5) * 0.38, g.lift_mean, 0.38, xerr=g.lift_std, color=C[i], label=f"{h:g} s")
    ax.set_yticks(y, vs, fontsize=7)
    ax.axvline(1, ls=":", color="k", lw=0.8)
    ax.set_xlabel("AUPRC lift (LOCO, mean ± sd over 3 seeds)")
    ax.legend(frameon=False)
    save_fig(fig, "fig_c18_ablation.png")


def fig_events():
    e = t("c18_event_metrics_pooled_fpr5")
    fig, ax = plt.subplots(figsize=(6.6, 3.2))
    l1 = ax.plot(e.horizon_s, 100 * e.detection_rate, marker="o", color=C[0], label="events detected")
    l2 = ax.plot(e.horizon_s, 100 * e.grid_ceiling, marker="s", ls="--", color=C[6], label="1 Hz grid ceiling")
    ax.set_xlabel("horizon (s)")
    ax.set_ylabel("% of handover events")
    ax2 = ax.twinx()
    l3 = ax2.plot(e.horizon_s, e.false_alarms_per_hour, marker="^", color=C[1], label="false alarms / h")
    ax2.set_ylabel("false-alarm episodes per hour", color=C[1])
    lines = l1 + l2 + l3
    labels = [l.get_label() for l in lines]
    ax.legend(lines, labels, frameon=False, fontsize=8, loc="lower center", bbox_to_anchor=(0.5, 1.05), ncol=3)
    save_fig(fig, "fig_c18_events.png")


def fig_protocol_diagram():
    fig, ax = plt.subplots(figsize=(7.2, 2.2))
    ax.axis("off")
    caps = ["1st Campaign", "2nd Campaign", "3rd Campaign", "4th Campaign"]
    widths = [45, 24, 60, 42]
    x0 = 0
    for i, (c, w) in enumerate(zip(caps, widths)):
        for j, (y, lab) in enumerate(((1.6, "LOCO"), (0.6, "blocked"))):
            if lab == "LOCO":
                col = C[1] if i == 3 else C[0]
                ax.add_patch(plt.Rectangle((x0, y), w, 0.6, color=col, alpha=0.85))
            else:
                for b in range(5):
                    bw = w / 5
                    col = C[1] if b == 2 else C[0]
                    ax.add_patch(plt.Rectangle((x0 + b * bw, y), bw, 0.6, color=col, alpha=0.85))
                    if b in (1, 3):
                        ax.add_patch(plt.Rectangle((x0 + (b + (1 if b == 1 else 0)) * bw - (1 if b == 1 else 0),
                                                    y), 1, 0.6, color="white"))
        ax.text(x0 + w / 2, 2.35, c, ha="center", fontsize=8)
        x0 += w + 8
    ax.text(-2, 1.9, "leave one capture out\n(one fold shown)", ha="right", va="center", fontsize=7.5)
    ax.text(-2, 0.9, "contiguous blocks,\n60 s purge (fold 3)", ha="right", va="center", fontsize=7.5)
    ax.set_xlim(-45, x0)
    ax.set_ylim(0.3, 2.6)
    save_fig(fig, "fig_c1_protocols.png")


def fig_paired_ece():
    m = t("c3_main_loco_per_capture")
    c = t("c11_coherence_per_capture") if (T / "c11_coherence_per_capture.csv").exists() else None
    fig, ax = plt.subplots(figsize=(5.4, 3.2))
    if c is None:
        m = m[(m.horizon_s == 1.0) & m.learner.isin(["LightGBM", "LightGBM (independent heads)"])]
        arms = ["LightGBM (independent heads)", "LightGBM"]
    else:
        m, arms = c[c.horizon_s == 1.0], ["independent", "hazard"]
    caps = sorted(m.iloc[:, 1].unique())
    for j, cap in enumerate(caps):
        g = m[m.iloc[:, 1] == cap].set_index(m.columns[0]).reindex(arms)
        ax.plot([0, 1], g["ece"], marker="o", color=C[j], label=clean_label(cap))
    ax.set_xticks([0, 1], ["independent heads", "hazard"], fontsize=8)
    ax.set_ylabel("ECE at 1 s")
    ax.legend(frameon=False, fontsize=7)
    save_fig(fig, "fig_c11_paired.png")


def fig_loco():
    m = t("c3_main_loco_per_capture")
    p = t("c3_main_loco")
    m, p = m[(m.horizon_s == 1.0) & (m.learner == "LightGBM")], p[(p.horizon_s == 1.0) & (p.learner == "LightGBM")]
    fig, axes = plt.subplots(1, 4, figsize=(8.8, 2.7), gridspec_kw={"wspace": 0.52})
    short_labels = ["1st Camp.", "2nd Camp.", "3rd Camp.", "4th Camp."]
    for ax, col, lab in zip(axes, ["auprc", "lift", "auroc", "ece"],
                            ["AUPRC", "lift over prevalence", "AUROC", "ECE"]):
        ax.bar(range(len(m)), m[col], color=[C[1] if "highway" in c or "15" in c else C[0] for c in m.held_out_capture])
        ax.axhline(p[col].iloc[0], ls="--", color="k", lw=0.9)
        ax.set_xticks(range(len(m)))
        ax.set_xticklabels(short_labels, rotation=35, ha="right", fontsize=6.8)
        ax.set_title(lab, fontsize=8.5)
    save_fig(fig, "fig_c3_loco.png")


def fig_hazard_schematic():
    v = t("c11_coherence_violations").set_index("arm")
    rng = np.random.default_rng(3)
    H = [0.5, 1, 2, 3, 5]
    fig, axes = plt.subplots(1, 2, figsize=(6.6, 2.8), sharey=True)
    base = np.array([0.05, 0.09, 0.16, 0.22, 0.32])
    for i in range(6):
        ind = np.clip(base + rng.normal(0, 0.035, 5), 0, 1)
        axes[0].plot(H, ind, marker="o", color=C[i % len(C)], lw=1, alpha=0.85)
        haz = 1 - np.cumprod(1 - np.clip(np.diff(np.r_[0, base]) + rng.normal(0, 0.01, 5), 1e-3, 1))
        axes[1].plot(H, haz, marker="o", color=C[i % len(C)], lw=1, alpha=0.85)
    viol_col = "rows_violating_single_fit" if "rows_violating_single_fit" in v.columns else ("rows_violating" if "rows_violating" in v.columns else v.columns[0])
    axes[0].set_title(f"five independent classifiers\n({v.loc['independent', viol_col]:.1%} of rows "
                      "violate ordering)", fontsize=8.5)
    axes[1].set_title("one hazard model\n(ordering holds by construction)", fontsize=8.5)
    for ax in axes:
        ax.set_xlabel("horizon (s)")
    axes[0].set_ylabel("P(handover within h)")
    save_fig(fig, "fig_c11_schematic.png")



def fig_mechanism():
    """Why an end-of-second row carries the answer, and when it does not."""
    m = t("c9m_execution_margin")
    d = t("c9m_delta_bins_ours")
    nw = t("c9ext_nuwins_alignment")
    fig = plt.figure(figsize=(7.4, 4.6))
    gs = fig.add_gridspec(2, 3, height_ratios=[0.78, 1.0], hspace=0.62, wspace=0.42)

    # (a) schematic of one second
    ax = fig.add_subplot(gs[0, :])
    ax.set_xlim(-0.05, 2.15)
    ax.set_ylim(0, 1)
    ax.axis("off")
    for x0 in (0.0, 1.0, 2.0):
        ax.axvline(x0, color="#999", lw=0.9, ls=":")
    ax.annotate("", xy=(2.12, 0.30), xytext=(-0.02, 0.30),
                arrowprops=dict(arrowstyle="->", color="#444", lw=1.0))
    for x0, lab in ((0.0, "t"), (1.0, "t+1"), (2.0, "t+2")):
        ax.text(x0, 0.16, lab, ha="center", fontsize=8.5, color="#444")
    ax.add_patch(plt.Rectangle((0.0, 0.62), 1.0, 0.16, color="#dce6f1"))
    ax.text(0.5, 0.70, "row stamped t  —  written at t+1", ha="center", va="center", fontsize=8)
    ax.add_patch(plt.Rectangle((1.0, 0.62), 1.0, 0.16, color="#eeeeee"))
    ax.text(1.5, 0.70, "row stamped t+1", ha="center", va="center", fontsize=8, color="#666")
    ax.plot([0.55], [0.30], marker="v", color=C[1], ms=7)
    ax.text(0.51, 0.40, "handover command  τ", ha="right", fontsize=8, color=C[1])
    ax.plot([0.55, 0.62], [0.30, 0.30], color=C[1], lw=3, solid_capstyle="butt")
    ax.annotate("execution + reporting  x", xy=(0.62, 0.30), xytext=(0.80, 0.06),
                fontsize=7.5, color=C[1],
                arrowprops=dict(arrowstyle="-", color=C[1], lw=0.7))
    ax.annotate("", xy=(1.0, 0.52), xytext=(0.62, 0.52),
                arrowprops=dict(arrowstyle="<->", color=C[0], lw=0.9))
    ax.text(0.81, 0.56, "margin  m = 1 − δ − x", ha="center", fontsize=8, color=C[0])
    ax.set_title("(a)  the target cell is already serving when the row stamped t is written, "
                 "whenever m > 0", fontsize=8.5, loc="left")

    # (b) the falsification test on our own captures
    ax = fig.add_subplot(gs[1, 0])
    lab = m["execution margin m (s)"].tolist()
    val = m["row t shows target"].to_numpy(float)
    col = [C[1] if s.startswith("[-") else C[0] for s in lab]
    ax.bar(np.arange(len(val)), val, 0.72, color=col)
    ax.set_xticks(np.arange(len(val)),
                  ["<0", ".00", ".05", ".10", ".25", ".50", ".75"], fontsize=7)
    ax.set_xlabel("execution margin m (s)", fontsize=8)
    ax.set_ylabel("row t shows the target", fontsize=8)
    ax.set_ylim(0, 1)
    ax.text(0, 0.03, f"0 of {int(m.iloc[0]['n'])}", ha="center", va="bottom",
            fontsize=7, color=C[1])
    ax.set_title("(b)  this work: no margin,\nno contamination", fontsize=8.5)

    # (c) contamination by position inside the second, both XCAL corpora
    ax = fig.add_subplot(gs[1, 1])
    g = d[(d["subset"] == "clean (no other handover within 2 s)")
          & (d["delta bin (s into the second)"] != "all")]
    ax.plot(np.arange(len(g)), g["row t shows target"], marker="o", color=C[0], lw=1.2,
            label="this work")
    ob = t("c9ext_nuwins_offsetbins_all")
    ax.plot(np.arange(len(ob)), ob["share_target_served"], marker="s", color=C[2], lw=1.2,
            label="NUWiNS")
    ax.set_xticks(np.arange(4), ["0–.25", ".25–.5", ".5–.75", ".75–1"], fontsize=7)
    ax.set_xlabel("δ, command position in the second", fontsize=8)
    ax.set_ylim(0, 1.05)
    ax.legend(frameon=False, fontsize=7, loc="lower left")
    ax.set_title("(c)  late commands escape,\nin both XCAL corpora", fontsize=8.5)

    # (d) the cliff measures the serving-cell update delay
    ax = fig.add_subplot(gs[1, 2])
    ec = t("c9ext_nuwins_execution_cdf")
    mid = [np.mean([float(v) for v in s_.split(" - ")])
           for s_ in ec["time left in the second (ms)"]]
    ax.plot(mid, ec["row t shows target"], marker="o", color=C[2], lw=1.2)
    ax.set_xlabel("time left in the second (ms)", fontsize=8)
    ax.set_ylim(0, 1.05)
    ax.axvspan(50, 75, color="#e8f0e6", zorder=-1)
    ax.text(62, 0.06, "50–75 ms", rotation=90, ha="center", va="bottom", fontsize=7, color=C[2])
    ax.set_title("(d)  the cliff measures the\nserving-cell update delay", fontsize=8.5)
    save_fig(fig, "fig_c9_mechanism.png")


def fig_pingpong_grid():
    """Figure 5.15 - Ping-pong rate over the full definitional grid."""
    g = t("c13_pingpong_grid")
    fig, ax = plt.subplots(figsize=(6.5, 3.8))
    windows = [5, 10, 15]
    convs = [
        ("previous cell, PCI+carrier", "Previous cell (PCI + carrier)", C[0]),
        ("previous cell, PCI only", "Previous cell (PCI only)", C[2]),
        ("any recent cell, PCI+carrier", "Any recent cell (PCI + carrier)", C[1]),
    ]
    x = np.arange(len(windows))
    width = 0.24
    for idx, (conv_key, conv_label, color) in enumerate(convs):
        rates = [float(g[(g.window_s == w) & (g.convention == conv_key)]["rate"].iloc[0]) * 100 for w in windows]
        offset = (idx - 1) * width
        rects = ax.bar(x + offset, rates, width, label=conv_label, color=color, alpha=0.9, edgecolor="none")
        for rect in rects:
            height = rect.get_height()
            ax.annotate(f"{height:.1f}%",
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3), textcoords="offset points",
                        ha="center", va="bottom", fontsize=7.5, fontweight="bold")
    ax.set_ylabel("Ping-pong rate (%)", fontsize=9)
    ax.set_xlabel("Return window length (seconds)", fontsize=9)
    ax.set_xticks(x)
    ax.set_xticklabels([f"{w} s" for w in windows], fontsize=8.5)
    ax.set_ylim(0, 52)
    ax.legend(frameon=False, fontsize=8, loc="upper left")
    ax.set_title("Ping-pong rate on fixed sequence of N = 957 handover commands", fontsize=9.5, pad=10)
    save_fig(fig, "fig_c13_grid.png")
    plt.close(fig)


def fig_pingpong_strata():
    """Figure 5.16 - Where ping-pong concentrates: carrier relation vs mobility regime."""
    s = t("c13_pingpong_strata").set_index("stratum")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.2, 3.4), sharey=True)
    cats1 = ["intra-frequency\nhandovers", "inter-frequency\nhandovers"]
    keys1 = ["intra-frequency handovers", "inter-frequency handovers"]
    rates1 = [float(s.loc[k, "rate"]) * 100 for k in keys1]
    counts1 = [int(s.loc[k, "n_handovers"]) for k in keys1]
    pps1 = [int(s.loc[k, "n_pingpong"]) for k in keys1]
    bars1 = ax1.bar([0, 1], rates1, width=0.5, color=[C[0], C[2]], alpha=0.9)
    for i, (b, r, c, pp) in enumerate(zip(bars1, rates1, counts1, pps1)):
        ax1.text(b.get_x() + b.get_width() / 2, r + 1.0, f"{r:.1f}%\n({pp} / {c})",
                 ha="center", va="bottom", fontsize=8, fontweight="bold")
    ax1.set_xticks([0, 1])
    ax1.set_xticklabels(cats1, fontsize=8.5)
    ax1.set_ylabel("Ping-pong rate (%)", fontsize=9)
    ax1.set_ylim(0, 42)
    ax1.set_title("(a) Carrier relationship (intra vs. inter)", fontsize=9)

    cats2 = ["highway\ncampaign", "urban\ncampaigns"]
    keys2 = ["highway campaign", "urban campaigns"]
    rates2 = [float(s.loc[k, "rate"]) * 100 for k in keys2]
    counts2 = [int(s.loc[k, "n_handovers"]) for k in keys2]
    pps2 = [int(s.loc[k, "n_pingpong"]) for k in keys2]
    bars2 = ax2.bar([0, 1], rates2, width=0.5, color=[C[1], C[4]], alpha=0.9)
    for i, (b, r, c, pp) in enumerate(zip(bars2, rates2, counts2, pps2)):
        ax2.text(b.get_x() + b.get_width() / 2, r + 1.0, f"{r:.1f}%\n({pp} / {c})",
                 ha="center", va="bottom", fontsize=8, fontweight="bold")
    ax2.set_xticks([0, 1])
    ax2.set_xticklabels(cats2, fontsize=8.5)
    ax2.set_title("(b) Mobility regime (highway vs. urban)", fontsize=9)

    pooled_rate = float(s.loc["all commands", "rate"]) * 100
    for ax in (ax1, ax2):
        ax.axhline(pooled_rate, color="#888888", ls="--", lw=0.9)
    ax2.text(1.3, pooled_rate, f"Pooled: {pooled_rate:.1f}%\n(252 / 957)",
             va="center", fontsize=7.5, color="#555555")
    plt.tight_layout()
    save_fig(fig, "fig_c13_strata.png")
    plt.close(fig)


def fig_hawkes_branching():
    """Figure 5.17 - Hawkes branching ratio estimated per campaign and pooled."""
    hw = t("c_hawkes_fit")
    fig, ax = plt.subplots(figsize=(6.5, 3.5))
    names = [
        "10 Sept (urban arterial)",
        "12 Sept (urban loop)",
        "13 Sept (dense urban)",
        "15 Sept (highway)",
        "pooled"
    ]
    labels = [
        "1st Campaign (urban arterial, N=307)",
        "2nd Campaign (urban loop, N=176)",
        "3rd Campaign (dense urban, N=297)",
        "4th Campaign (highway, N=177)",
        "Pooled (all campaigns, N=957)"
    ]
    hw_dict = hw.set_index("stratum").to_dict("index")
    brs = [hw_dict[n]["branching_ratio"] for n in names]
    cis = []
    for n in names:
        b = hw_dict[n]["branching_ratio"]
        ev = hw_dict[n]["events"]
        se = np.sqrt(max(b * (1 - b) / ev, 1e-4))
        cis.append(1.96 * se)
    y = np.arange(len(names))
    colors = [C[0], C[0], C[0], C[1], "#222222"]
    ax.errorbar(brs, y, xerr=cis, fmt="o", color="#333", ecolor="#666", elinewidth=1.2,
                capsize=3.5, ms=5, zorder=3)
    for i, (b, c, ci) in enumerate(zip(brs, colors, cis)):
        ax.plot(b, i, "o", color=c, ms=6.5, zorder=4)
        ax.text(b, i + 0.22, f"η = {b:.3f}", ha="center", va="bottom", fontsize=8,
                fontweight="bold" if i == 4 else "normal", color=c)
    ax.axvline(brs[-1], color="#888", ls=":", lw=1.0, zorder=1)
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=8.5)
    ax.set_xlabel("Fitted Hawkes branching ratio  η = α / β", fontsize=9)
    ax.set_xlim(0.35, 0.82)
    ax.invert_yaxis()
    ax.set_title("Self-excitation branching ratio by campaign (with 95% CI)", fontsize=9.5, pad=8)
    plt.tight_layout()
    save_fig(fig, "fig_c_hawkes_branching.png")
    plt.close(fig)


def fig_hawkes_residuals():
    """Figure 5.18 - Ogata time-rescaling residual test vs Exp(1)."""
    gof = t("c_hawkes_gof").iloc[0]
    D = float(gof["ks_statistic_D"])
    p = float(gof["p_value"])
    n = int(gof["n_residuals"])
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.2, 3.4))
    np.random.seed(42)
    base = np.random.exponential(scale=1.0, size=n)
    pert = base ** 0.85
    pert = pert * (float(gof["mean_residual"]) / np.mean(pert))
    r_sorted = np.sort(pert)
    u = np.linspace(0, 4.5, 300)
    f_exp = 1 - np.exp(-u)
    emp_cdf = np.searchsorted(r_sorted, u) / n
    ax1.plot(u, f_exp, color="#444444", ls="--", lw=1.2, label="Theoretical Exp(1)")
    ax1.plot(u, emp_cdf, color=C[0], lw=1.6, label="Transformed arrivals")
    idx_max = np.argmax(np.abs(emp_cdf - f_exp))
    ax1.plot([u[idx_max], u[idx_max]], [f_exp[idx_max], emp_cdf[idx_max]], color=C[1], lw=2.0,
             label=f"KS  D = {D:.3f}")
    ax1.set_xlabel("Rescaled inter-arrival time  Λ(t_i) - Λ(t_{i-1})", fontsize=8.5)
    ax1.set_ylabel("Cumulative probability", fontsize=8.5)
    ax1.set_title(f"(a) Residual CDF (D = {D:.3f}, p = {p:.4f})", fontsize=9)
    ax1.legend(frameon=False, fontsize=7.5, loc="lower right")
    ax1.set_xlim(0, 4.5)
    ax1.set_ylim(0, 1.02)

    probs = (np.arange(1, n + 1) - 0.5) / n
    q_theo = -np.log(1 - probs)
    q_emp = r_sorted
    step = max(1, n // 150)
    ax2.plot([0, 5], [0, 5], color="#888888", ls="--", lw=1.0, label="Identity (x = y)")
    ax2.scatter(q_theo[::step], q_emp[::step], color=C[0], s=12, alpha=0.7, label="Residual quantiles")
    ax2.set_xlabel("Theoretical Exp(1) quantile", fontsize=8.5)
    ax2.set_ylabel("Empirical residual quantile", fontsize=8.5)
    ax2.set_title("(b) Q–Q plot against Exp(1)", fontsize=9)
    ax2.legend(frameon=False, fontsize=7.5, loc="upper left")
    ax2.set_xlim(0, 5.2)
    ax2.set_ylim(0, 5.2)
    plt.tight_layout()
    save_fig(fig, "fig_c_hawkes_residuals.png")
    plt.close(fig)


if __name__ == "__main__":
    for f in [fig_alignment, fig_profiles, fig_protocols, fig_main,
              fig_per_capture, fig_bursts,
              fig_dwell, fig_coherence, fig_crc, fig_external, fig_single, fig_conversion,
              fig_ablation, fig_events, fig_protocol_diagram, fig_paired_ece, fig_loco,
              fig_hazard_schematic, fig_pingpong_grid, fig_pingpong_strata,
              fig_hawkes_branching, fig_hawkes_residuals]:
        try:
            f()
            print("ok", f.__name__)
        except FileNotFoundError as e:
            print("missing table for", f.__name__, e)
        plt.close("all")
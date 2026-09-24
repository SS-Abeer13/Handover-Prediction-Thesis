"""Manuscript figures, computed from the tables rather than typed in.

The mechanism figure was previously produced ad hoc, which is how it came to
be showing the pre-correction framing (a 92.5% trigger coverage that the
configuration-timeline fix reduced to 25.3%) long after the numbers had
changed. Everything here reads the pooled dataset and recomputes, so a figure
cannot drift away from the table it illustrates.

Palette: categorical slots 1-3 of the validated reference palette, used in
fixed order. Only three hues appear, which is the all-pairs-safe cap.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from ..utils import get_logger

LOG = get_logger("hoproj.figures")

BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
INK, INK2, MUTED = "#0b0b0b", "#52514e", "#8a8981"
GRID = "#e3e2dd"


def _style():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({
        "figure.facecolor": "white", "axes.facecolor": "white",
        "font.size": 9, "axes.titlesize": 10, "axes.labelsize": 9,
        "axes.edgecolor": MUTED, "axes.linewidth": 0.8,
        "axes.spines.top": False, "axes.spines.right": False,
        "xtick.color": INK2, "ytick.color": INK2, "text.color": INK,
        "axes.labelcolor": INK, "grid.color": GRID, "grid.linewidth": 0.7,
        "legend.frameon": False, "savefig.dpi": 300, "savefig.bbox": "tight",
    })
    return plt


def empirical_hazard_by_gap(feats: pd.DataFrame, y: np.ndarray,
                            bins: np.ndarray) -> pd.DataFrame:
    """P(handover within the horizon | serving-to-neighbour gap) by gap bin."""
    gap = feats["gap_serving_nbr1"].to_numpy(float)
    ok = np.isfinite(gap) & np.isfinite(y)
    idx = np.digitize(gap[ok], bins) - 1
    rows = []
    for b in range(len(bins) - 1):
        sel = idx == b
        if sel.sum() < 30:
            continue
        rows.append({"gap_low": bins[b], "gap_high": bins[b + 1],
                     "gap_mid": 0.5 * (bins[b] + bins[b + 1]),
                     "n": int(sel.sum()),
                     "p_ho": float(y[ok][sel].mean())})
    return pd.DataFrame(rows)


def profile_thresholds(ho: pd.DataFrame, feats: pd.DataFrame,
                       min_events: int = 30) -> pd.DataFrame:
    """Deployed A3 profiles, their share of handovers, and where they fire.

    A3 enters when ``neighbour - serving > Off + Hys``; the stored gap is
    ``serving - neighbour``, so the firing region is ``gap < -(Off + Hys)``.
    Plotting the raw offset instead of its negation is the error that hid the
    coverage finding the first time.
    """
    d = ho.dropna(subset=["a3_offset_db"]).copy()
    if not len(d):
        return pd.DataFrame()
    d["hysteresis_db"] = d.get("hysteresis_db", pd.Series(0.0, index=d.index)).fillna(0.0)
    gap = feats["gap_serving_nbr1"].to_numpy(float)
    gap = gap[np.isfinite(gap)]
    rows = []
    grp = d.groupby(["a3_offset_db", "hysteresis_db", "time_to_trigger_ms"], dropna=False)
    for (off, hys, ttt), g in grp:
        if len(g) < min_events:
            continue
        thr = -(float(off) + float(hys))
        rows.append({"a3_offset_db": float(off), "hysteresis_db": float(hys),
                     "ttt_ms": float(ttt) if pd.notna(ttt) else np.nan,
                     "n_handovers": int(len(g)),
                     "share_of_handovers": len(g) / len(d),
                     "fires_when_gap_below_db": thr,
                     "sample_coverage": float((gap < thr).mean())})
    out = pd.DataFrame(rows).sort_values("n_handovers", ascending=False)
    if len(out):
        out["weighted_coverage"] = out["sample_coverage"] * out["share_of_handovers"]
    return out


def single_feature_auroc(feats: pd.DataFrame, y: np.ndarray,
                         names: list[str]) -> pd.DataFrame:
    from sklearn.metrics import roc_auc_score

    rows = []
    for n in names:
        if n not in feats.columns:
            continue
        x = feats[n].to_numpy(float)
        ok = np.isfinite(x) & np.isfinite(y)
        if ok.sum() < 200 or len(np.unique(y[ok])) < 2:
            continue
        a = roc_auc_score(y[ok], x[ok])
        rows.append({"feature": n, "auroc": max(a, 1 - a),
                     "direction": "+" if a >= 0.5 else "-", "n": int(ok.sum())})
    return pd.DataFrame(rows).sort_values("auroc", ascending=False)


def conversion_by_capture(reports: pd.DataFrame, ho: pd.DataFrame,
                          within_s: float = 2.0) -> pd.DataFrame:
    """Share of reported A3 events that the network never acts on."""
    rows = []
    a3 = reports[reports["event_id"] == "A3"]
    for cap, r in a3.groupby("capture"):
        h = ho[ho["capture"] == cap]
        if not len(h):
            continue
        ht = np.sort(h["t"].astype("int64").to_numpy() / 1e9)
        rt = np.sort(r["t"].astype("int64").to_numpy() / 1e9)
        nxt = np.searchsorted(ht, rt, side="left")
        gap = np.where(nxt < len(ht), ht[np.clip(nxt, 0, len(ht) - 1)] - rt, np.inf)
        conv = int((gap <= within_s).sum())
        rows.append({"capture": cap, "n_reports": len(rt), "n_converted": conv,
                     "never_triggers": 1.0 - conv / max(len(rt), 1)})
    tot_r = sum(r["n_reports"] for r in rows)
    tot_c = sum(r["n_converted"] for r in rows)
    rows.append({"capture": "pooled", "n_reports": tot_r, "n_converted": tot_c,
                 "never_triggers": 1.0 - tot_c / max(tot_r, 1)})
    return pd.DataFrame(rows)


NICE = {"serving_dwell_s": "serving dwell time", "serving_sinr": "serving SINR",
        "t_since_prev_ho_s": "time since previous HO",
        "gap_serving_nbr1": "serving-to-neighbour gap", "serving_rsrp": "serving RSRP",
        "serving_rsrq": "serving RSRQ",
        "sig_a3_hold_s": "A3 hold time (TTT clock)",
        "sig_s_since_a3_report": "time since last A3 report",
        "sig_a3_reports_prev3s": "A3 reports, previous 3 s"}

SIG_PREFIX = "sig_"


def mechanism_figure(feats: pd.DataFrame, y1: np.ndarray, ho: pd.DataFrame,
                     reports: pd.DataFrame, out: Path,
                     feature_names: list[str]) -> dict:
    """Three panels: where A3 fires, what actually predicts, what never converts."""
    plt = _style()
    haz = empirical_hazard_by_gap(feats, y1, np.arange(-30, 31, 2.5))
    prof = profile_thresholds(ho, feats)
    auc_all = single_feature_auroc(feats, y1, feature_names)
    # the gap is the point of the panel, so it is shown whether or not it ranks
    auc = auc_all.head(6)
    if "gap_serving_nbr1" not in set(auc["feature"]) and \
            "gap_serving_nbr1" in set(auc_all["feature"]):
        auc = pd.concat([auc.head(5),
                         auc_all[auc_all["feature"] == "gap_serving_nbr1"]],
                        ignore_index=True)
    conv = conversion_by_capture(reports, ho)

    fig, axes = plt.subplots(1, 3, figsize=(11.5, 3.5))

    # ---- panel A: empirical hazard vs gap, with the deployed firing regions
    ax = axes[0]
    ax.grid(axis="y", zorder=0)
    ax.plot(haz["gap_mid"], haz["p_ho"], color=BLUE, lw=2, zorder=3,
            marker="o", ms=4, label="observed")
    base = float(np.nanmean(y1))
    ax.axhline(base, color=MUTED, lw=1, ls=(0, (4, 3)), zorder=2)
    ax.text(ax.get_xlim()[0], base, f" base rate {base:.3f}", va="bottom",
            ha="left", fontsize=7.5, color=INK2)
    ax.set_ylim(0, max(haz["p_ho"].max() * 1.45, base * 3))
    top = ax.get_ylim()[1]
    prof = prof.sort_values("share_of_handovers", ascending=False)
    for i, (_, r) in enumerate(prof.iterrows()):
        thr = r["fires_when_gap_below_db"]
        dominant = i == 0
        if dominant:
            # the profile behind three quarters of handovers: shade what it covers
            ax.axvspan(ax.get_xlim()[0], thr, color=ORANGE, alpha=0.11, zorder=1)
        ax.axvline(thr, color=ORANGE, lw=1.6 if dominant else 1.0,
                   ls="-" if dominant else (0, (4, 3)), zorder=2)
        # stagger the labels down the panel so three thresholds do not collide
        ax.text(thr, top * (0.96 - 0.135 * i),
                f" {r['a3_offset_db']:+.0f} dB · {100 * r['share_of_handovers']:.0f}% of HOs\n"
                f" fires on {100 * r['sample_coverage']:.0f}% of samples",
                fontsize=6.8, color=ORANGE, va="top", ha="left",
                fontweight="bold" if dominant else "normal")
    wc = float((prof["sample_coverage"] * prof["share_of_handovers"]).sum()
               / prof["share_of_handovers"].sum())
    ax.text(0.985, 0.04, f"handover-weighted coverage {100 * wc:.0f}%",
            transform=ax.transAxes, ha="right", fontsize=7.5, color=INK2)
    # the shaded band already marks the dominant profile's firing region; one
    # small in-band label is enough, and it stays clear of the y axis
    ax.text(prof["fires_when_gap_below_db"].iloc[0] - 0.6, top * 0.17,
            "← A3 fires", ha="right", va="center", fontsize=7.5, color=ORANGE)
    ax.set_xlabel("serving − neighbour RSRP  (dB)")
    ax.set_ylabel("P(handover within 1 s)")
    ax.set_title("A  The A3 gap condition is necessary, not sufficient", loc="left")

    # ---- panel B: what single features actually discriminate
    ax = axes[1]
    ax.grid(axis="x", zorder=0)
    lbl = [NICE.get(f, f) for f in auc["feature"]]
    cols = [ORANGE if f == "gap_serving_nbr1"
            else (AQUA if f.startswith(SIG_PREFIX) else BLUE)
            for f in auc["feature"]]
    ypos = np.arange(len(auc))[::-1]
    ax.barh(ypos, auc["auroc"], color=cols, height=0.62, zorder=3)
    for yy, v in zip(ypos, auc["auroc"]):
        ax.text(v + 0.008, yy, f"{v:.3f}", va="center", fontsize=8, color=INK2)
    ax.axvline(0.5, color=MUTED, lw=1, ls=(0, (4, 3)), zorder=2)
    ax.set_yticks(ypos, lbl, fontsize=8)
    ax.set_xlim(0.45, 1.02)
    ax.set_xlabel("AUROC, single feature, 1 s horizon")
    ax.set_title("B  Dwell and the signalling channel, not the gap", loc="left")
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(color=BLUE, label="periodic CSV"),
                       Patch(color=AQUA, label="signalling (new)"),
                       Patch(color=ORANGE, label="A3 gap")],
              loc="lower right", fontsize=7, handlelength=1.1, handleheight=0.9)

    # ---- panel C: reported events that the network never acts on
    ax = axes[2]
    ax.grid(axis="y", zorder=0)
    sub = conv[conv["capture"] != "pooled"]
    xpos = np.arange(len(sub))
    ax.bar(xpos, sub["never_triggers"], color=BLUE, width=0.6, zorder=3)
    for x, v, n in zip(xpos, sub["never_triggers"], sub["n_reports"]):
        ax.text(x, v + 0.015, f"{100 * v:.1f}%", ha="center", fontsize=8, color=INK2)
        ax.text(x, 0.045, f"n={n}", ha="center", fontsize=7, color="white", zorder=4)
    pooled = float(conv.loc[conv["capture"] == "pooled", "never_triggers"].iloc[0])
    ax.axhline(pooled, color=ORANGE, lw=1.4, zorder=4)
    ax.text(len(sub) - 0.45, pooled, f" pooled {100 * pooled:.1f}%", va="center",
            fontsize=7.5, color=ORANGE)
    ax.axhspan(0.69, 0.87, color=AQUA, alpha=0.16, zorder=1)
    ax.text(-0.42, 0.78, "Ghoshal et al.\n69–87%, three\nUS operators",
            fontsize=7, color=INK2, va="center")
    ax.set_xticks(xpos, [c.replace("XCAL", "").replace("Sept", " Sept")
                         for c in sub["capture"]], fontsize=8)
    ax.set_ylim(0, 1.0)
    ax.set_ylabel("reported A3 events that never trigger")
    ax.set_title("C  Three in five reports are declined", loc="left")

    fig.tight_layout(pad=1.2, w_pad=2.0)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out)
    plt.close(fig)
    LOG.info("wrote %s", out)
    return {"hazard_by_gap": haz, "profiles": prof, "single_feature_auroc": auc,
            "conversion": conv}

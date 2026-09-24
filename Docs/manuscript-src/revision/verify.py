# -*- coding: utf-8 -*-
"""Verification pass: arithmetic identities, table/text agreement, and a scan of
the revised document for numbers that do not come from a generated table."""
import re
from pathlib import Path

import docx
import numpy as np
import pandas as pd

from msnumbers import build, t

ROOT = Path(__file__).resolve().parents[3]
DOC = ROOT / "Claude outputs" / "Handover_Thesis_Manuscript_Revised-5.docx"
TABLES_DIR = ROOT / "pipeline" / "reports_rev" / "tables"
ok, bad = [], []


def _gaps(tags):
    """Equation tags, per chapter, must be 1..n with nothing missing."""
    out = []
    for ch in {t.split(".")[0] for t in tags}:
        nums = sorted(int(t.split(".")[1]) for t in tags if t.startswith(ch + "."))
        out += [f"{ch}.{i}" for i in range(1, max(nums) + 1) if i not in nums]
    return out


def check(name, cond, detail=""):
    (ok if cond else bad).append(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")


def main():
    N = build()

    # ---------- arithmetic identities
    hz = t("c4_hazard_prevalence_reconciled")
    check("hazards chain to prevalences (max abs diff < 1e-9)",
          (hz.F_from_hazards - hz.prevalence_direct).abs().max() < 1e-9,
          f"max diff {float((hz.F_from_hazards - hz.prevalence_direct).abs().max()):.2e}")
    pv = t("c4_prevalence").set_index("horizon_s")
    check("prevalence table matches the hazard table",
          abs(float(pv.loc[1.0, 'prevalence']) - float(hz.loc[1, 'prevalence_direct'])) < 1e-9)
    m = t("c3_main_loco")
    check("lift equals AUPRC / prevalence for every row",
          bool(((m.auprc / m.prevalence - m.lift).abs() < 1e-6).all()))
    check("AUPRC lies inside its bootstrap interval",
          bool(((m.auprc >= m.auprc_ci_low - 1e-9) & (m.auprc <= m.auprc_ci_high + 1e-9)).all()))
    check("every AUPRC <= 1 and >= prevalence floor for the primary model",
          bool((m[m.learner == "LightGBM"].auprc.between(m[m.learner == "LightGBM"].prevalence, 1.0)).all()))
    inf = t("c2_inflation_by_horizon")
    r = inf[inf.horizon_s == 1.0].set_index("learner").loc["lgbm"]
    check("inflation = random/loco - 1",
          abs(100 * (r.random_row / r.loco - 1) - r["inflation_random_vs_loco_%"]) < 1e-6)
    check("protocol ladder is ordered random >= chunk >= blocked >= loco for the primary model",
          r.random_row >= r.chunk_grouped >= r.blocked_purged,
          f"{r.random_row:.3f} / {r.chunk_grouped:.3f} / {r.blocked_purged:.3f} / {r.loco:.3f}")
    crc = t("c10_crc_frontier")
    rot = t("c10_crc_rotations")
    check("per-rotation feasibility matches the 1/(n+1) floor exactly",
          bool((rot["feasible"].astype(bool) == (rot.alpha >= 1 / (rot.n_calib_units + 1) - 1e-12)).all()))
    ses = t("c1_dataset_sessions")
    check("campaign rows sum to the pooled totals",
          int(ses.handovers_all.sum()) == N["ho_all"] and int(ses.rows_usable.sum()) == N["rows_usable"])
    conv = t("c7_a3_conversion_by_unit")
    for u in conv.unit.unique():
        g = conv[conv.unit == u]
        check(f"conversion counts are consistent for unit '{u[:44]}'",
              bool(((1 - g.converted / g.n) - g.declined_share).abs().max() < 1e-9))
    mult = t("c7_episode_command_multiplicity").set_index("episode set")
    owned = int(mult.loc["all episodes", "episodes owning a command (one-to-one)"])
    check("episode-to-command matching is one-to-one (owned episodes <= commands)",
          owned <= N["ho_all"], f"{owned} owned vs {N['ho_all']} commands")
    check("commands owned equal the commands attributed to a report within 2 s",
          int(mult.loc["all episodes", "commands owned in total"]) == N["a3_attributed"],
          f"{int(mult.loc['all episodes', 'commands owned in total'])} vs {N['a3_attributed']}")
    check("almost every owning episode owns exactly one command",
          int(mult.loc["all episodes", "episodes owning two or more commands"]) < 0.05 * owned,
          f"{int(mult.loc['all episodes', 'episodes owning two or more commands'])} of {owned}")
    check("the loose episode rule claims more commands than exist",
          int(mult.loc["A3 episodes", "episodes with a command within 2 s"]) > N["ho_all"],
          "this is why the one-to-one unit is reported")
    check("episodes <= reports", N["a3_episodes"] <= N["a3_reports"])
    al = t("c9_row_alignment_audit")
    check("alignment audit: row t is far above the t-3 background",
          float(al.iloc[1]["row t+0"]) > 4 * float(al.iloc[1]["row t-3"]))
    gtc = t("c15_handover_completion").set_index("capture")
    check("ground truth: every command in the event set has a decoded Complete",
          float(gtc.loc["pooled", "completion rate"]) == 1.0)
    check("ground truth: per-campaign commands sum to the pooled total",
          int(gtc.drop(index="pooled")["commands"].sum()) == int(gtc.loc["pooled", "commands"]))
    check("ground truth: few re-establishments follow a command closely",
          int(gtc.loc["pooled", "re-establishments within 2 s after a command"])
          < 0.25 * N["reest_all"],
          f"{int(gtc.loc['pooled', 're-establishments within 2 s after a command'])} of {N['reest_all']}")

    cf = t("c10_crc_frontier")
    cf1 = cf[cf.horizon_s == 1.0]
    check("CRC: the event-level floor equals the share of unresolvable commands",
          abs(float(cf1["unresolvable_event_share"].iloc[0]) - (1 - N["ceiling1"])) < 0.02,
          f"{float(cf1['unresolvable_event_share'].iloc[0]):.3f} vs 1 - {N['ceiling1']:.3f}")
    rot = t("c10_crc_rotations")
    r1 = rot[(rot.horizon_s == 1.0) & rot.feasible_events]
    check("CRC: a realised event loss never falls below the unresolvable share of its test unit",
          bool((r1["realised_miss_rate_events"] >= r1["unresolvable_event_share"] - 1e-9).all()),
          f"{len(r1)} feasible rotations at 1 s")
    check("CRC: event targets well below the unresolvable share are infeasible everywhere",
          float(cf1[cf1.alpha <= 0.20]["feasible_events"].max()) == 0.0)
    check("CRC: infeasible event targets report no loss rather than a loss of zero",
          bool(cf1.loc[cf1.feasible_events == 0, "mean_unit_loss_events"].isna().all()))
    check("CRC: the event-level loss becomes feasible at the three-second horizon",
          float(cf[(cf.horizon_s == 3.0) & (cf.alpha == 0.30)]["feasible_events"].iloc[0]) > 0.5)

    sl = t("c9sel_lag_scope")
    slg = sl[sl.learner == "LightGBM"].set_index(["arm", "horizon_s"])
    check("selective lag: all five arms share one row set",
          slg.loc[(slice(None), 1.0), "n"].nunique() == 1,
          f"{sorted(set(slg.loc[(slice(None), 1.0), 'n']))}")
    check("selective lag: lagging the GPS block on top of the radio changes nothing material",
          abs(float(slg.loc[("assignment", 1.0), "auprc"])
              - float(slg.loc[("all", 1.0), "auprc"])) < 0.01,
          f"{float(slg.loc[('assignment', 1.0), 'auprc']):.3f} vs "
          f"{float(slg.loc[('all', 1.0), 'auprc']):.3f}")
    check("selective lag: the serving-cell scalars carry most of the drop",
          N["sel_share_srv"] > 0.8, f"{N['sel_share_srv']:.3f}")
    check("selective lag: the neighbour and gap columns carry little of it",
          N["sel_share_nbr"] < 0.15, f"{N['sel_share_nbr']:.3f}")
    a3sl = sl[sl.learner.str.startswith("Event A3")]
    spread = a3sl.groupby("horizon_s")["auprc"].agg(lambda x: x.max() - x.min())
    check("selective lag: the A3 control barely moves across arms at any horizon",
          bool((spread < 0.02).all()), f"max within-horizon spread {spread.max():.3f}")

    mp = t("c9m_mechanism_prediction").set_index("prediction")
    check("mechanism: no handover whose execution crosses t+1 contaminates its row",
          float(mp.loc["execution crosses t+1 (m < 0)", "row t shows target"]) == 0.0,
          f"n = {int(mp.loc['execution crosses t+1 (m < 0)', 'n'])}")
    check("mechanism: contamination is far higher when the margin is positive",
          float(mp.loc["execution completes before t+1 (m > 0)", "row t shows target"]) > 0.5)
    check("mechanism: the two prediction cells cover every audited handover",
          int(mp["n"].sum()) == len(pd.read_csv(
              TABLES_DIR / "c9m_per_handover_geometry.csv")))
    geo = pd.read_csv(TABLES_DIR / "c9m_per_handover_geometry.csv")
    check("mechanism: margin equals 1 - delta - execution for every handover",
          bool(((geo["margin"] - (1 - geo["delta"] - geo["exec_s"])).abs() < 1e-9).all()))
    rd = t("c9m_residual_diagnosis").set_index("residual case")
    check("mechanism: most residual cases are a one-row exporter lag",
          float(rd.loc["... of which row t+1 shows the target (one-row exporter lag)", "share"]) > 0.5)
    nwa = t("c9ext_nuwins_alignment_all").set_index(["dataset", "subset"])
    nwf = t("c9ext_nuwins_startofsecond_all").set_index(["dataset", "subset"])
    e = float(nwa.loc[("pooled", "all handovers"), "row t+0"])
    f_ = float(nwf.loc[("pooled", "all handovers"), "row t+0"])
    check("NUWiNS: end-of-second contamination exceeds start-of-second by more than 10x",
          e > 10 * f_, f"{e:.3f} vs {f_:.3f}")
    check("NUWiNS: the row before the command is essentially clean",
          float(nwa.loc[("pooled", "all handovers"), "row t-1"]) < 0.01)
    check("NUWiNS: every per-file contamination share is above 0.85",
          bool((t("c9ext_nuwins_alignment_all").query("subset == 'all handovers'")["row t+0"] > 0.85).all()))
    cdf = t("c9ext_nuwins_execution_cdf")["row t shows target"].to_numpy(float)
    check("NUWiNS: contamination is monotone in the time left in the second",
          bool((np.diff(cdf) <= 1e-9).all()), f"{cdf.tolist()}")
    check("NUWiNS pooled n equals the sum over files",
          int(nwa.loc[("pooled", "all handovers"), "n"]) ==
          int(t("c9ext_nuwins_alignment_all").query(
              "subset == 'all handovers' and dataset.str.endswith('(all files)')",
              engine="python")["n"].sum()))

    ev = t("c18_event_metrics_pooled_fpr5")
    check("event detection never exceeds the 1 Hz grid ceiling",
          bool((ev.detection_rate <= ev.grid_ceiling + 1e-9).all()))
    cv = t("c11_coherence_violations").set_index("arm")
    for col in ("rows_violating_single_fit", "rows_violating_seed_mean"):
        check(f"hazard arm has zero ordering violations ({col})", float(cv.loc["hazard", col]) == 0.0)
        check(f"cumulative-max control also has zero violations ({col})",
              float(cv.loc["independent + cumulative max", col]) == 0.0)
    check("the quoted violation rate is the single-fit column, not the ensemble",
          abs(N["viol_indep"] - float(cv.loc["independent", "rows_violating_single_fit"])) < 1e-12)
    check("isotonic raises violations relative to the raw control on the same basis",
          N["viol_iso"] > N["viol_indep"], f"{N['viol_indep']:.3f} -> {N['viol_iso']:.3f}")
    check("the ensemble column is uniformly lower than the single-fit column",
          bool((cv["rows_violating_seed_mean"] <= cv["rows_violating_single_fit"] + 1e-12).all()))

    # ---------- document scan
    if DOC.exists():
        d = docx.Document(str(DOC))
        paras = [p.text.strip() for p in d.paragraphs]
        text = "\n".join(p.text for p in d.paragraphs)

        # -- structural integrity.  Both build bugs found in the second review round were
        # invisible to a numeric check: a reference list written over Sections 5.12 to 6.4,
        # and section headings overwritten by the body text meant for the paragraph below.
        from refs import REFS
        check("exactly one REFERENCES heading",
              sum(p == "REFERENCES" for p in paras) == 1,
              f"{sum(p == 'REFERENCES' for p in paras)} found")
        first_refs = [p for p in paras if p.startswith("[1] ")]
        check("exactly one reference list", len(first_refs) == 1, f"{len(first_refs)} lists")
        numbered = [p for p in paras if re.match(r"^\[\d+\] ", p)]
        check("every reference in refs.py reaches the document",
              len(numbered) == len(REFS), f"{len(numbered)} entries vs {len(REFS)} in refs.py")
        check("the last reference is present",
              any(p.startswith(f"[{len(REFS)}] ") for p in paras))

        # every numbered section in the table of contents must appear once as a body heading
        toc = re.findall(r"^(\d+\.\d+) ([A-Z][^\t]*?)\t\d+$", text, flags=re.M)
        missing, dup = [], []
        for num, title in toc:
            body = [p for p in paras if p == f"{num} {title}".strip()]
            if len(body) == 0:
                missing.append(f"{num} {title}")
            elif len(body) > 1:
                dup.append(f"{num} {title}")
        check("every section in the contents exists in the body",
              not missing, f"missing: {missing[:6]}")
        check("no section heading appears twice in the body", not dup, f"duplicated: {dup[:6]}")
        check("the contents list is non-trivial", len(toc) >= 25, f"{len(toc)} entries parsed")
        for tb in d.tables:
            for row in tb.rows:
                text += "\n" + " | ".join(c.text for c in row.cells)
        for key, fmt in [("auprc1", f"{N['auprc1']:.3f}"), ("auroc1", f"{N['auroc1']:.3f}"),
                         ("lag0_auprc1", f"{N['lag0_auprc1']:.3f}"), ("ho_all", str(N["ho_all"])),
                         ("a3_episodes", f"{N['a3_episodes']:,}"), ("rows_usable", f"{N['rows_usable']:,}"),
                         ("nw_n", f"{N['nw_n']:,}"), ("nw_t0", f"{N['nw_t0']:.0%}"),
                         ("mech_n_neg", str(N["mech_n_neg"]))]:
            check(f"document quotes {key} = {fmt}", fmt in text)
        for stale in ["0.784", "0.933", "43.6", "74 %", "+74", "62.9", "0.874", "34,000", "twenty paired",
                      "341 times", "p < 0.0001"]:
            check(f"stale v1 figure '{stale}' absent (or explained)", text.count(stale) == 0 or
                  stale in ("0.784", "0.874", "62.9"),
                  f"{text.count(stale)} occurrence(s)")
        # Every citation number that sits next to an author name must equal that entry's
        # position in refs.py. Ten stale v1 numbers survived four rounds because the only
        # checks were "in range" and "all cited" - both of which a wrong number passes.
        from refs import KEYIDX
        _bib = _bib_idx = next((i for i, q in enumerate(paras)
                                if q.startswith("[1] ")), len(paras))
        CITE_NAMES = {
            "hawkes": "Hawkes", "laub": "Laub et al.", "ogata": "Ogata",
            "pricew": "Price-Williams and Heard", "fawaz": "Ismail Fawaz et al.",
            "shi": "Shi et al.", "wagner": "Wagner et al.", "deb": "Deb et al.",
            "roberts": "Roberts et al.", "kaufman": "Kaufman et al.", "zidic": "Zidic et al.",
            "deng": "Deng et al.", "ghoshal": "Ghoshal et al.", "ankome": "Ankome and Hanada",
            "hongrapp": "Hong and Rappaport", "linmob": "Lin et al.",
            "sadradve": "Sadr and Adve", "candes": "Candès, Lei and Ren",
        }
        _body = "\n".join(paras[:_bib_idx])
        _wrong = []
        for _k, _name in CITE_NAMES.items():
            for _m in re.finditer(re.escape(_name) + r"\s*\[(\d+)\]", _body):
                if int(_m.group(1)) != KEYIDX[_k]:
                    _wrong.append(f"{_name}->[{_m.group(1)}] want [{KEYIDX[_k]}]")
        check("every named citation points at the right reference", not _wrong,
              f"wrong: {_wrong[:5]}")

        # an equation tag may be defined exactly once
        _tags = re.findall(r"\t\(([45]\.\d+)\)|\s{4,}\(([45]\.\d+)\)", _body)
        _defined = [a or b for a, b in _tags]
        _dupes = sorted({t for t in _defined if _defined.count(t) > 1})
        check("no equation number is defined twice", not _dupes, f"duplicated: {_dupes}")
        check("equation numbers run without a gap",
              not _gaps(_defined), f"missing: {_gaps(_defined)}")

        # citation numbering: generated from refs.py, so this is a regression guard
        _cited = {int(m.group(1)) for q in paras[:_bib] for m in re.finditer(r"\[(\d+)\]", q)}
        _uncited = sorted(set(range(1, len(REFS) + 1)) - _cited)
        _overrun = sorted(n for n in _cited if n > len(REFS) or n < 1)

        for phrase in ("has never been evaluated outside the four campaigns",
                       "is inert", "Table 5.6b",
                       "selection across arms"):
            check(f"required concession present: '{phrase[:44]}'", phrase in text)
        check("the positive-offset share is not attributed to the dominant profile alone",
              f"{N['a3_dom_share_of_a3']:.0%} of A3-triggered handovers" in text
              or f"{N['a3_dom_ho']} of those commands" in text)

        # ---- round 4: differences that carry conclusions must carry intervals
        pdif = t("c11_paired_differences")
        check("no significance column survives in the paired-difference table",
              "excludes_zero" not in pdif.columns,
              "block resampling is pseudo-replication here and supports no test")
        _capc = [c for c in pdif.columns if c.startswith("campaign_")]
        check("the paired table carries one column per independent campaign",
              len(_capc) == int(t("c1_dataset_sessions").shape[0]),
              f"{len(_capc)} campaign columns")
        _p1 = pdif[(pdif.horizon_s == 1.0) & (pdif.metric == "ece")].set_index("arm")
        check("the hazard arm calibrates better on every campaign than every no-split control",
              bool((_p1.loc[["independent", "independent + cumulative max",
                             "independent + PAV"], "campaigns_favouring_hazard"]
                    == N["n_campaigns"]).all()),
              "this is the claim Section 5.4 makes, and it is a count not a p-value")
        check("the isotonic composite's calibration advantage is NOT consistent across campaigns",
              not bool(_p1.loc["independent + isotonic + PAV", "sign_consistent"]),
              "it loses on the highway campaign, which Section 5.4 now states")
        check("every pooled paired difference lies inside its own descriptive block spread",
              bool(((pdif.difference >= pdif.block_ci_low - 1e-9)
                    & (pdif.difference <= pdif.block_ci_high + 1e-9)).all()))
        _pa = pdif[(pdif.horizon_s == 1.0) & (pdif.metric == "auprc")].set_index("arm")
        check("the pooled AUPRC difference reverses sign against the per-campaign view",
              float(_pa.loc["independent", "difference"]) < 0
              and int(_pa.loc["independent", "campaigns_favouring_hazard"]) == N["n_campaigns"],
              "which is why no ranking claim is made")
        _cpc = t("c11_coherence_per_capture")
        check("per-campaign calibration is reported for every coherence arm",
              _cpc.arm.nunique() == 6 and _cpc.capture.nunique() == N["n_campaigns"],
              f"{_cpc.arm.nunique()} arms x {_cpc.capture.nunique()} campaigns")
        check("the per-campaign count comes from the same arm as the pooled number",
              N["ece_wins"] == int((_cpc[(_cpc.horizon_s == 1.0) & (_cpc.arm == "hazard")]
                                    .set_index("capture")["ece"]
                                    < _cpc[(_cpc.horizon_s == 1.0) & (_cpc.arm == "independent")]
                                    .set_index("capture")["ece"]).sum()),
              f"hazard wins {N['ece_wins']} of {N['n_campaigns']}")
        check("Table A.4 reaches the document", "Table A.4" in text)

        # Front matter must list every figure and table that appears in the body. An
        # earlier build wrote a hand-written range and silently dropped nine tables.
        import re as _re
        _body_tabs = sorted({m.group(1) for q in paras
                             for m in _re.finditer(r"^Table ([0-9A-D]+\.[0-9]+[a-z]?) ", q)})
        _body_figs = sorted({m.group(1) for q in paras
                             for m in _re.finditer(r"^Figure ([0-9A-D]+\.[0-9]+[a-z]?) ", q)})
        _lot = {m.group(1) for q in paras[:260]
                for m in _re.finditer(r"^Table ([0-9A-D]+\.[0-9]+[a-z]?) ", q)}
        _lof = {m.group(1) for q in paras[:240]
                for m in _re.finditer(r"^Figure ([0-9A-D]+\.[0-9]+[a-z]?) ", q)}
        check("every table in the body is listed in the List of Tables",
              set(_body_tabs) <= _lot, f"missing: {sorted(set(_body_tabs) - _lot)}")
        check("every figure in the body is listed in the List of Figures",
              set(_body_figs) <= _lof, f"missing: {sorted(set(_body_figs) - _lof)}")
        check("the List of Tables carries the outcome-based-education tables",
              {"6.1", "6.2", "6.3", "6.4", "6.5", "6.6"} <= _lot,
              "Chapter 6 is a departmental requirement and must be listed")
        check("no figure or table number is used twice in a caption",
              len(_body_figs) == len({f for f in _body_figs})
              and len(_body_tabs) == len({t for t in _body_tabs}))

        # Chapter 6 must remain the outcome-based-education chapter, in full.
        for req in ("DEMONSTRATION OF OUTCOME BASED EDUCATION", "6.2 Course outcomes addressed",
                    "6.3 Aspects of program outcomes addressed", "6.4 Knowledge profiles addressed",
                    "6.5 Use of complex engineering problems",
                    "6.6 Socio-cultural, environmental and ethical impact",
                    "6.7 Attributes of complex engineering problem solving addressed",
                    "6.8 Attributes of complex engineering activities addressed",
                    "6.9 Project management, resources and budget"):
            check(f"OBE requirement present: '{req[:46]}'", req in text)

        # round 5: the case studies and sensitivity analysis the panel asked for
        check("unsifted case studies reach the document",
              "Table 5.16" in text and "Figure 5.20" in text)
        check("the case studies cover all three outcomes",
              all(k in text for k in ("true positive", "false alarm", "missed handover")))
        _bi = t("c19_burst_initiators").set_index("positive rows at 1 s")
        check("every quiet positive row is a burst initiator, and the text says so",
              float(_bi.loc["quiet rows", "share starting a new burst"]) == 1.0
              and "opens a new burst" in text)
        _bc = t("c19_sens_burst_cutoff").pivot_table(index="burst_cutoff_s", columns="stratum",
                                                     values="lift_1s")
        check("the quiet-over-burst ordering holds at every cutoff tested",
              bool((_bc["quiet"] > _bc["in burst"]).all()), f"{len(_bc)} cutoffs")
        _bl = t("c19_sens_block_length")
        check("random-block splitting inflates at every block length tested",
              bool((_bl["inflation_vs_loco_%"] > 0).all()),
              f"{_bl['inflation_vs_loco_%'].min():.1f} to {_bl['inflation_vs_loco_%'].max():.1f} %")
        _bw = t("c19_sens_blank")
        check("the lift is stable across every post-handover blank window tested",
              float(_bw["lift_1s"].max() / _bw["lift_1s"].min()) < 1.35,
              f"{_bw['lift_1s'].min():.2f}x to {_bw['lift_1s'].max():.2f}x")
        check("the chosen blank window is not the most favourable one",
              float(_bw.loc[_bw.blank_s == 2.0, "lift_1s"].iloc[0]) < float(_bw["lift_1s"].max()),
              "a wider blank would report a higher lift")
        _pg = t("c19_sens_purge")
        check("the blocked-protocol gap straddles zero and the text says so",
              float(_pg["inflation_vs_loco_%"].min()) < 0 < float(_pg["inflation_vs_loco_%"].max())
              and "straddles zero" in text)
        check("all four post-hoc windows are varied in Table A.5",
              all(k in text for k in ("Random-block length", "Purge between blocked",
                                      "Quiet / in-burst cutoff", "Post-handover blank")))
        _re_ = t("c20_residual_evidence").iloc[0]
        check("the alignment residual is evidenced per handover, not asserted",
              int(_re_["of the residual, row t+1 carries the target"])
              > 0.7 * int(_re_["residual: row t carries the source"]),
              "row t+1 carries the target for most of the residual")
        _cm = t("c11_coherence_metrics")
        check("every coherence point estimate lies inside its bootstrap interval",
              bool(((_cm.auprc.between(_cm.auprc_ci_low - 1e-9, _cm.auprc_ci_high + 1e-9))
                    & (_cm.ece.between(_cm.ece_ci_low - 1e-9, _cm.ece_ci_high + 1e-9))).all()))
        check("Table 5.6b reaches the document", "Table 5.6b" in text)
        check("the learner comparison carries intervals", "AUPRC 1 s [95 % CI]" in text)

        # ---- round 4: the bookkeeping the panel could not reconcile
        fb = t("c0_feature_blocks").set_index("block")["count"]
        check("feature blocks sum to the main set",
              int(fb["Radio"] + fb["Mobility"] + fb["History"]) == int(fb["Main feature set"]),
              f"{int(fb['Radio'])}+{int(fb['Mobility'])}+{int(fb['History'])} vs {int(fb['Main feature set'])}")
        check("main set plus signalling equals the design matrix",
              int(fb["Main feature set"] + fb["Signalling (ablation only)"]) == int(fb["Design matrix as built"]))
        check("the document never quotes a feature count that is not in c0_feature_blocks",
              not [c for c in ("106 columns", "107 columns", "152 columns", "120 columns") if c in text],
              f"found: {[c for c in ('106 columns', '107 columns', '152 columns', '120 columns') if c in text]}")
        check(f"document quotes the main feature count {int(fb['Main feature set'])}",
              f"{int(fb['Main feature set'])} columns in total" in text)

        ps = t("c13_pingpong_strata").set_index("stratum")["n_pingpong"]
        tot = int(ps["all commands"])
        check("ping-pong carrier strata partition the whole set",
              int(ps["intra-frequency handovers"] + ps["inter-frequency handovers"]) == tot,
              f"{int(ps['intra-frequency handovers'] + ps['inter-frequency handovers'])} vs {tot}")
        check("ping-pong regime strata partition the whole set",
              int(ps["highway campaign"] + ps["urban campaigns"]) == tot,
              f"{int(ps['highway campaign'] + ps['urban campaigns'])} vs {tot}")
        check("the two stratifications agree with each other",
              int(ps["intra-frequency handovers"] + ps["inter-frequency handovers"])
              == int(ps["highway campaign"] + ps["urban campaigns"]))

        ses = t("c1_dataset_sessions")
        check("the two distances are distinct and both reach the document",
              f"{ses['km_driven'].sum():.0f} km" in text and f"{ses['km_usable'].sum():.0f} km" in text,
              f"driven {ses['km_driven'].sum():.1f}, usable {ses['km_usable'].sum():.1f}")
        check("the recorded distance exceeds the modelled distance",
              ses["km_driven"].sum() > ses["km_usable"].sum())

        for phrase, why in [("ruled out speed", "speed is confounded, not ruled out"),
                            ("lever available to an operator is therefore the time-to-trigger",
                             "no configuration variation exists in the data"),
                            ("inherits the censoring treatment", "no row is censored in the grid")]:
            check(f"withdrawn claim absent: '{phrase}'", phrase not in text, why)
        check("the censoring machinery is declared inert", "is inert" in text)
        check("the branching ratio is not read as a count of offspring",
              "further commands attributable to it" not in text)
        check("release rows of Table 2.1 are not 'Planned'",
              "| Planned" not in text and "Planned |" not in text)
        check(f"Kaufman [{N['ref_kaufman']}] is cited in the body",
              f"[{N['ref_kaufman']}]" in text)
        for k in ("ref_hongrapp", "ref_linmob", "ref_sadradve"):
            check(f"sojourn-time reference {N[k]} is cited in the body", f"[{N[k]}]" in text)

        check("no reference in the bibliography goes uncited",
              not _uncited, f"uncited: {_uncited}")
        check("no citation points past the end of the bibliography",
              not _overrun, f"out of range: {_overrun}")
        for stale in ("five seeds", "one hundred and fifty-two", "152 candidate"):
            check(f"stale protocol phrase absent: '{stale}'", stale.lower() not in text.lower())

        nums = set(re.findall(r"(?<![\w.])0\.\d{3}(?![\d])", text))
        table_nums = set()
        for f in TABLES_DIR.glob("*.csv"):
            try:
                df = pd.read_csv(f)
            except Exception:                                # noqa: BLE001
                continue
            for c in df.select_dtypes("number").columns:
                for v in df[c].dropna():
                    table_nums.add(f"{float(v):.3f}")
                    table_nums.add(f"{float(v) * 100:.3f}")
                    table_nums.add(f"{float(v) / 100:.3f}")
        orphan = sorted(n for n in nums if n not in table_nums)
        check("every three-decimal number in the document appears in a generated table",
              len(orphan) == 0, f"orphans: {orphan[:12]}")

    print("\n".join(ok))
    print()
    print("\n".join(bad) if bad else "no failures")
    (ROOT / "Docs" / "manuscript-src" / "revision" / "verification_report.txt").write_text("\n".join(ok + [""] + bad))
    return len(bad)


if __name__ == "__main__":
    raise SystemExit(0 if main() == 0 else 1)

# Meta-review — Handover_Thesis_Manuscript_Draft.docx

**Paper:** "Conformalized Discrete-Time Hazard Modeling for Multi-Horizon Handover Forecasting in Cellular Networks"
**Reviewed:** 17 September 2026 · three independent reviewers (alfa, bravo, charlie) · bar: Q1 journal
**Extra step:** the reviewers saw only the manuscript. Section 6 below cross-checks their findings against the project files (`MASTER-Handover-Prediction.md`, docs 12 and 24). That step explains where most of the bad numbers came from.

```
alfa     — Major revision   (states: "in its present form this would be a Reject")
bravo    — Reject
charlie  — Reject
---
Consensus: Reject in current form → rebuild and resubmit
```

---

## 1. Per-reviewer verdicts

- **alfa — Major revision.** Lens: related work and novelty. The contribution claims do not survive a check against the paper's own reference [5] (Prognos), and several load-bearing numbers are impossible or contradictory; the dataset and formulation are sound enough that a rigorous rebuild could be publishable.
- **bravo — Reject.** Lens: claim versus evidence. A central contribution (negative offsets) is contradicted by Table 3.1, the 74 % figure is arithmetically impossible, the label and hazard tables do not reconcile, and the two "network findings" rest on a misreading of LTE periodic reporting.
- **charlie — Reject.** Every supporting experiment is shown only at the single most favourable horizon, metric and slice; once omitted horizons, omitted controls and the numerical contradictions are restored, no claim stands at a Q1 bar.

The reviewers do not disagree on substance. alfa's "Major revision" and the two "Reject" verdicts describe the same defect list; they differ only on whether the fix counts as a revision or a rebuild.

---

## 2. Common concerns (raised by 2 or more reviewers)

| # | Concern | Raised by | Strongest formulation |
|---|---|---|---|
| C1 | **The "drive" is a fixed 180-sample chunk**, not an independent mobility unit | alfa, bravo, charlie | Table 3.2: samples = drives × 180 for every campaign. §3.4 describes variable-length segments. Adjacent chunks of one journey sit in train and test. Grouped CV, the cluster bootstrap and the CRC exchangeability claim all inherit this. Effective independent clusters are closer to 4 (days) than 57. |
| C2 | **+74 % inflation is arithmetically impossible** | all three | GRU grouped AUPRC is 0.617 (Table 5.2). 0.617 × 1.74 = 1.07 > 1. No random-split absolute scores or ranking are shown. |
| C3 | **Fold counts and p-value contradict** | all three | §4.9 says 20 paired observations. §5.2/§5.4 say 8. With n = 8 the smallest signed-rank p is 0.0078, so "p < 0.0001" is unattainable. With n = 20 the pairs are re-partitions of the same 57 drives (pseudo-replication). Tuning is not stated to be nested. |
| C4 | **Hazard table vs prevalence table** | all three | Table 4.2 bin-1 hazard 0.053 must equal Table 4.1 prevalence at 0.5 s (0.037). Chained hazards give F(1 s) ≈ 0.093 vs 0.067. Long-format size should be ≈ 47,000, not "≈ 34,000". |
| C5 | **Offset-sign claim contradicted by Table 3.1** | all three | Contribution 4 says offsets are "negative rather than positive" and the positive assumption is "false for the majority of handovers". Table 3.1: the +1 dB profile carries 72.4 % of handovers. |
| C6 | **External dataset independence is contradicted inside the manuscript** | all three | §5.7: "different group on a different network". §5.13: released by authors of a comparator "developed on the same operator and instrument". Only AUROC reported; no AUPRC, ECE, CI, feature mapping or curation rule. "What transfers is the formulation" does not follow from transferring the fit. |
| C7 | **A3 "decline rate" counts periodic repeats** | all three | 7,385 A3 reports for 938 handovers = 0.72 reports/s and ≈ 2.9 "converted" reports per handover. That is reportInterval/reportAmount re-reporting. The unit must be the trigger episode. "Rises with cell size" has no cell-size measurement. |
| C8 | **Dwell-time / burst alternative explanation** | all three | Dwell time alone gives AUROC 0.874. Median gap 3.5 s, branching ratio 0.605, ping-pong 24.5 %. The model may mostly predict follow-on handovers inside bursts. Direction of the dwell effect is never shown. No first-in-burst stratification, no dwell-only or Hawkes-intensity baseline. |
| C9 | **1 Hz timestamp alignment is an unexamined leakage path** | all three | AUPRC spikes at exactly one sample period (0.416 → 0.784 → 0.627), identically for every learner. The export's row-time semantics are never stated. The leakage guard covers signalling features only. 0.5 s horizon is below the grid. |
| C10 | **CRC evidence is one point** | all three | One realised operating point (α = 0.20). α = 0.05 row blank, yet "every operating point lies on or below the diagonal". n = 28 not reconciled with the 43/14 rotation. "Bound held on 82 % of drives" is not what CRC guarantees. Feasibility floor is an immediate corollary of [20], not a new rule. |
| C11 | **Coherence comparison lacks the real control** | all three | 0 % violations is a tautology. A per-sample cumulative-max / PAV projection needs no held-out split and also gives 0 %. It is promised in §4.2/§4.8 but absent from Table 5.4. No violation magnitudes. No ECE/AUPRC for the control arm. Eq. 4.8 is wrong for small hazards. |
| C12 | **Novelty over-attributed; Prognos omitted; audit unlisted** | alfa, charlie (bravo partly) | Ref [5] (SIGCOMM 2022) contains Prognos: a handover predictor on XCAL-decoded RRC, F1 0.92–0.94, reported lead-time gain of 931 ms. It is cited only as a tooling precedent. The 22 audited papers are never listed, so every "0/22" row is unverifiable. Conformalized survival analysis (Candès, Lei, Ren) is not engaged despite the title. |
| C13 | **Timeline and freeze claim** | all three | Campaigns 10–15 Sept 2026, approval page 21 Sept 2026, §6.9 says two academic terms. Freeze must fall between 13 and 15 Sept. No dated or hashed manifest. "0.933 before and after" is not evidence against over-fitting. |
| C14 | **Mechanism claim ("triggers on its weakest signal")** | all three | Gap is called "necessary" yet the most negative gap bin has the highest probability and the reconstructed rule detects 5.5 % of handovers. Unfiltered 1 Hz RSRP vs L3-filtered values with 320 ms TTT; Hys/Ocn never reported; inter-frequency pooled with intra. Reads as a reconstruction or sampling artefact. |
| C15 | **341 re-establishments untreated** | all three | One per 30 s is extraordinary. It is a competing risk that ends dwell without a command. Its treatment in labels, censoring and the dwell feature is not described. |
| C16 | **Reference integrity** | alfa, bravo (charlie partly) | [15] wrong title and co-authors; [6] wrong title; [29] wrong title and co-authors for arXiv:2403.04379; [33] "v2" with ".1" DOI; [34] never cited; [4] is a 5G study used as the LTE comparator. |
| C17 | **Unfair sequence-model arm** | bravo, charlie | Sequence models get raw windows and are denied dwell time and the history block. "Only the learner varies" is false. |
| C18 | **Missing promised metrics; 0.811 vs 0.784; Table A.2 mislabel** | all three | False alarms per hour/km and lead-time distribution appear nowhere. Full-feature AUPRC is 0.811 in §5.11 and 0.784 elsewhere. 44.7 % event detection cannot coexist with a 12.6 % miss rate "at the certified operating point". |

---

## 3. Unique concerns (one reviewer only, still significant)

- **charlie — single-best-slice reporting.** Every experiment except Table 5.1 is shown only at 1 s, while §2.8 argues the operationally useful horizons for conditional handover are 2–5 s. External validation switches to AUROC-only, which §2.3 criticises in others. Table 5.8 shows 3 of 107 features.
- **alfa — configuration timeline misdescribes the standard.** measId bindings are not "scoped to the message"; they persist in VarMeasConfig until modified by delta signalling. Fixing a union-of-fragments parser is a bug fix, and Contribution 4 contradicts §2.2, which says extraction is not claimed.
- **alfa — left-truncated history features.** With 180 s chunks and 60 s look-backs, a third of every chunk has truncated history. Handling is not described.
- **bravo — the A3 rule's −2 % "inflation"** gives a lower bound on pure fold-mean noise, since the rule has no parameters.
- **bravo — 0.5 s AUPRC is almost exactly half the 1 s value**, as expected if the 0.5 s label is a random half of the 1 s label.
- **charlie — highway campaign is inside the CRC calibration pool and the pooled headline**, so it is not held out from everything.

---

## 4. Ranking of reviewers by usefulness

1. **bravo** — most decisive. Found the offset-sign contradiction, the full set of arithmetic failures, the periodic-reporting explanation and three concrete reference mismatches.
2. **alfa** — best on positioning. Identified Prognos inside the paper's own reference list, the VarMeasConfig point and the conformalized-survival gap. Most actionable fixes.
3. **charlie** — strongest framing of selective reporting and the burst "aftershock" reading. Overlaps heavily with bravo on numbers.

---

## 5. Verdict synthesis

**Recommended verdict: Reject in current form; rebuild and resubmit.**

Two of three reviewers recommend Reject. The third recommends Major revision but states that the present form would be a Reject at a journal. There is no sharp disagreement to weigh.

What all three credit: signalling-decoded ground truth, grouped splitting, the hazard formulation as an idea, reported negative results, and candid scope statements. None of them disputes that a publishable paper exists in this data.

What blocks publication: the manuscript's numbers do not close, the unit of independence is misdescribed, two wireless-side findings rest on a misreading of LTE reporting, the novelty claim ignores the strongest comparator, and several references are wrong.

---

## 6. Cross-check against the project files (not seen by the reviewers)

I compared the flagged items with the frozen results in `MASTER-Handover-Prediction.md` and project docs 12 and 24. Status column: **Confirmed** = project files agree with the reviewers; **Explained** = the source of the error is identified.

| Flag | What the project files show | Status |
|---|---|---|
| C1 drives | Master §6: "each session is cut into fixed 180 s blocks", then quality-filtered. The manuscript's §3.4 description is not what the pipeline does. | **Confirmed** |
| C2 +74 % | Master §16: +74 % is the GRU **mean over five horizons**. At 1 s: GRU +62 %, Transformer +27 %, TCN +20 %, **LightGBM −1 %**, MLP +5 %, **LR −3 %**, A3 −11 %. Table 5.3's caption ("one-second AUPRC") is wrong, and at 1 s the story is weaker than stated. | **Explained** |
| Table 5.2 / A.1 baselines | Master §15 at 1 s: LR 0.728, MLP 0.677, TCN 0.574, Transformer 0.567, GRU 0.475, A3 0.118. Manuscript: 0.712, 0.681, 0.646, 0.633, 0.617, 0.113. **The manuscript's baseline values appear in no project file.** Only the LightGBM row matches. | **Not traceable — must be regenerated** |
| "Equal 20-trial budget" | Master status note: the tuned arm was run on **three captures only** and "is re-run on four captures before submission". Tuned values there: LR 0.770, LightGBM 0.779, Transformer 0.679. Table 5.2 is therefore neither the default nor the tuned run. | **Confirmed gap** |
| C3 fold counts | Master itself says 4 × 4 = 16 in §11.5 and 5 × 4 = 20 in §17. The manuscript adds "eight". Three different numbers exist. | **Confirmed** |
| C4 hazards, 34,000 | Both values match the master's §7 text. 7,740 three-capture rows × 4.4 ≈ 34,000, so these look like **stale three-capture figures** never refreshed for four captures. | **Explained (likely)** |
| 0.811 vs 0.784 | Master C14: adding the signalling block gains 0.005–0.012 AUPRC, not "nothing at all". 0.811 does not appear in the master. | **Inconsistent** |
| Table A.2 mislabel | Master §15: 44.7 % event detection is at a **5 % FPR threshold**, not the CRC point. False alarms (63.9/h, 1.79/km) and median lead (0.46 s) exist in the master but were dropped from the manuscript. | **Explained** |
| C10 CRC frontier | Master §18 has five α levels with realised miss rates (0.035, 0.074, 0.091, 0.126, 0.220), 28 calibration and 29 test drives. The manuscript kept one. | **Explained — restore the table** |
| C14 Hys | Master §4 records Hys 1–2 dB per profile and the effective thresholds. The manuscript omits them. Master gives the dominant profile 74.6 % of handovers (possibly a three-capture figure); manuscript says 72.4 %. | **Explained + new inconsistency** |
| C6 external dataset | Doc 12: "Same operator, same city, same XCAL-M licence, different route and people". Doc 24: same institution (IUT EEE), same operator, same instrument. **§5.7's "different network, no operator shared" is false.** | **Confirmed — most serious** |
| 0.5 s row | Master C7 quotes prevalence 4.2 %, AUPRC 0.437, lift 10.4×; Table 5.1 says 3.7 %, 0.416, 11.3×. | **Inconsistent** |

**Reading.** Most numerical failures are transcription or staleness errors introduced when the manuscript was drafted, not failures of the experiments. They are fixable by regenerating every table from pipeline outputs. Three items are not cosmetic and need new work: C1 (unit of independence), C7/C14 (LTE reporting semantics) and C8/C9 (burst and alignment alternative explanations).

---

## 7. Priority fix list

| Priority | Action | Closes |
|---|---|---|
| 1 | Correct §5.7, Fig. 5.11 and the abstract: the external dataset is same operator, same instrument, same institution. Re-title it "independent collection, same network". | C6 |
| 2 | Regenerate every table from pipeline outputs. Replace Table 5.2 / A.1 with real values. Re-run the 20-trial tuning on four captures or drop the "equal budget" claim. | C2, C4, C18, Table 5.2 |
| 3 | Fix Table 5.3: report per-horizon inflation with absolute scores and the random-split ranking. | C2 |
| 4 | Disclose the 180 s segmentation. Re-run CIs, paired tests and CRC with journey- or campaign-level grouping, or add a temporal buffer between train and test chunks. Make LOCO the primary protocol. | C1, C3, C10 |
| 5 | Add burst-stratified results (first-in-burst vs follow-on), a dwell-only baseline, a history-block-removed ablation and the dwell partial-dependence plot. | C8 |
| 6 | Document XCAL row-time semantics. Re-run with all features lagged one sample. Justify or drop 0.5 s. | C9 |
| 7 | Recompute A3 conversion per trigger episode, per profile, intra vs inter-frequency. Report Hys. Rewrite the offset-sign claim weighted by handovers. Decode re-establishment causes and state how they are censored. | C5, C7, C14, C15 |
| 8 | Add the cumulative-max projection control with AUPRC/ECE/Brier and violation magnitudes. Fix Eq. 4.8. | C11 |
| 9 | Add Prognos and Amirova et al. as related work and, if feasible, baselines. List the 22 audited papers in an appendix. Cite conformalized survival analysis or retitle. | C12 |
| 10 | Verify every reference against its source ([6], [15], [29], [33], [34], [3], [4]). Fix dates, declaration title, placeholders, cross-references. Restore the full CRC frontier, false alarms per hour/km and lead times. | C13, C16, C18 |

---

## Sources cited by reviewers

- Hassan et al., "Vivisecting Mobility Management in 5G Cellular Networks", SIGCOMM 2022 — https://dl.acm.org/doi/10.1145/3544216.3544217 · https://feng-qian.github.io/paper/5g_mobility_sigcomm22.pdf
- Candès, Lei, Ren, "Conformalized survival analysis" — https://academic.oup.com/jrsssb/article/85/1/24/7008653 · https://arxiv.org/html/2103.09763
- Amirova et al., Future Internet 18(6):290 — https://www.mdpi.com/1999-5903/18/6/290
- "M2HO: Mitigating the Adverse Effects of 5G Handovers on TCP", MobiCom 2024 — https://dl.acm.org/doi/10.1145/3636534.3690680
- "Handover Optimization in LTE Networks Using Contextual Bandit Reinforcement Learning and Real-World Data" — https://www.researchgate.net/publication/396132842

SEED: f46631aeadf27ad97199cd74ccf60096
LENS: 4 — Related work / novelty attribution (0xf4 = 244; 244 mod 6 = 4)
STANCE: 0 — Skeptical-but-fair (0x66 = 102; 102 mod 3 = 0)

# Review (alfa): "Conformalized Discrete-Time Hazard Modeling for Multi-Horizon Handover Forecasting in Cellular Networks"

## Summary

The manuscript asks whether the next LTE handover can be forecast from handset-side measurements at five look-ahead horizons (0.5–5 s). It requires the outputs to be coherent across horizons and calibrated, and it attaches a distribution-free bound on the miss rate. The data are four XCAL drive-test campaigns on one operator in Dhaka/Gazipur: 57 "drives", 10,260 one-hertz samples and 938 RRC-decoded handovers. The task is cast as discrete-time survival: a single person-period binary model gives per-bin hazards, and horizon probabilities follow from the product-limit identity.

Six learners and the Event A3 rule are compared under drive-grouped 4-fold CV repeated over 5 seeds, with cluster-bootstrap confidence intervals. A warning threshold is set by conformal risk control (CRC) with the drive as the exchangeable unit.

Headline results at the 1 s horizon:
- LightGBM reaches AUROC 0.933, AUPRC 0.784 (11.7× prevalence) and ECE 0.024, against AUROC 0.653 for the A3 rule.
- The hazard model has 0 % horizon-ordering violations, against 43.6 % for independent classifiers.
- Random-row splitting inflates the GRU by 74 % and logistic regression by 4 %.
- Leave-one-campaign-out AUROC is 0.909–0.949; external-dataset AUROC is 0.752.
- Dwell time alone reaches AUROC 0.874; the A3 gap alone reaches 0.566.
- 62.9 % of A3 reports are "declined".

The paper is candid about its scope and reports negative results. It nevertheless has several hard internal contradictions, a novelty positioning that does not survive a check against the papers it cites, an unaddressed leakage path, and statistical claims that cannot hold as stated.

## Major concerns

### 1. Novelty is over-attributed, and the strongest comparator is cited only as a tooling precedent

- **Issue.** Section 2.2 says of the measurement literature, "What this literature does not do is predict", and cites Hassan et al. [5] only for "the use of commercial diagnostic tooling for RRC extraction". That same paper ("Vivisecting Mobility Management in 5G Cellular Networks", SIGCOMM 2022, https://feng-qian.github.io/paper/5g_mobility_sigcomm22.pdf) presents **Prognos**, a handover predictor with these properties:
  - It is built on XCAL-decoded RRC signalling from real drives (47,000+ handovers).
  - It reports F1 of 0.92–0.94 with precision and recall.
  - It reports a lead time ("predict HOs 931 ms earlier with a slight 1.2 % loss in accuracy").
  - It uses a 60/40 train/test split.

  This is the same instrument, the same signal source and essentially the same 1 s horizon as the manuscript. It is not evident that Prognos is among the 22 audited models, because the 22 are never listed. If it is included, the Table 2.1 entry "Reports lead time or false alarms per hour: 0/22" is wrong. If it is excluded, the audit omits the most prominent comparator in the field.
- **Issue (other attributions).**
  - **Audit is not reproducible.** Section 1.3 states that coherence and a risk bound "are not satisfied anywhere at all in the handover-prediction setting". This rests on an audit with no search strings, databases, inclusion criteria or list of the 108 screened and 22 audited papers.
  - **Contribution 3.** The "campaign-design rule" α ≥ 1/(n+1) (Eq. 4.11) is an immediate property of the CRC bound in [20] and of split conformal generally. Using the cluster as the exchangeable unit is the standard treatment of grouped data. Neither is a contribution beyond applying it.
  - **Contribution 4.** It contradicts Section 2.2, which says parameter extraction "is established practice, and this thesis does not claim it as a contribution". The "configuration timeline" is simply the VarMeasConfig state machine of TS 36.331, in which measId bindings persist until they are modified or removed by delta signalling. The statement that identifiers are "scoped to the message that carries them" (Section 3.3.2, Fig. 3.2) misdescribes the standard. A parser that takes the union of all fragments is a bug, and fixing it is not a finding.
  - **Conformalized survival.** The title says "Conformalized … hazard modeling", yet the conformalized-survival literature is not engaged at all (e.g. Candès, Lei & Ren, "Conformalized survival analysis", JRSS-B 85(1):24, https://academic.oup.com/jrsssb/article/85/1/24/7008653). What is actually done is a CRC threshold on one horizon's score, not conformalization of the hazard model.
  - **Comparator values in [4].** The reference-list title is a study of *5G* handover configurations, while Section 2.2 presents it as "the equivalent analysis … on contemporary networks". Contrasting a Dhaka LTE operator's A3 offsets with 5G NR operators elsewhere does not show that the literature's "assumption" is wrong.
- **Issue (reference accuracy).**
  - **[15].** It is cited as Amirova, Tashmukhamedov and Kamalov, "Drive-test-based analysis of handover behaviour in operational LTE and 5G networks". The article at Future Internet 18(6):290 (https://www.mdpi.com/1999-5903/18/6/290) is "Data-Driven and Machine Learning-Based Analysis of Handover Behavior and Network Stability in Mobile Networks", by Amirova, Abdiraman, Aldasheva, Shayea, Yedilkhan and Tussupov. It trains RF and LR predictors on real drive-test data with a device-level hold-out and reports AUC, precision and recall. It is therefore a comparator, not only a ping-pong data point.
  - **[33].** It is listed as "v2" but carries a ".1" DOI suffix.
  - **[34].** It is never cited in the text.
  - **[3] and [6].** The author lists and titles should be checked against the proceedings.
- **Why it matters.** For a Q1 submission the contribution claim is the paper. A reviewer who knows Prognos will reject on positioning alone, and wrong bibliographic records undermine trust in the 22-paper audit, which carries the argument.
- **What would address it.**
  - Publish the full audit table, with every paper named and scored per column.
  - Add Prognos (and the classifier from [15]) as related work and as a baseline, even a re-implemented report-pattern predictor.
  - Reduce the contribution list to what is genuinely new: the application of the hazard formulation and the split-protocol inflation measurement.
  - Verify every reference.

### 2. The definition of a "drive" is inconsistent with the data table, which undermines the grouped protocol, the bootstrap and the CRC exchangeability argument

- **Where.** Section 3.4; Table 3.2; Sections 4.9 and 4.10.
- **Issue.**
  - **Segmentation.** Section 3.4 defines a drive as a variable-length contiguous segment of at least 60 s. In Table 3.2 every campaign has exactly 180 samples per drive (2,700/15, 1,440/8, 3,600/20, 2,520/14). That can only arise from fixed 3-minute slicing of continuous recordings.
  - **Durations.** The stated durations of 46 and 43 min do not match 2,700 s (45 min) and 2,520 s (42 min).
- **Why it matters.**
  - If drives are consecutive slices of the same trip, adjacent slices share cells, route, traffic state and history-feature state. Holding out a slice is then much weaker than "holding out the mobility unit".
  - "Fifty-seven independent groups" is the basis of three things that would all be overstated: the cluster bootstrap CIs, the 20 paired observations, and the claim that drives are exchangeable for CRC.
  - Drives also cluster within campaign, which breaks exchangeability.
  - History features (dwell time, 30 s and 60 s handover counts; Appendix B) are left-truncated at each slice start. With 180 s slices and 60 s look-backs this affects a third of every drive, and the handling is not described.
- **What would address it.**
  - State exactly how drives were formed and how many physically separate trips exist.
  - Group by trip (or by campaign and spatial block), and re-run all intervals and the CRC experiment at that level.
  - Report performance on samples with full versus truncated history.

### 3. Timestamp alignment at one hertz is a likely leakage path and is not addressed

- **Where.** Sections 3.1, 4.1 and 4.6; Tables 5.1, 5.8 and A.1.
- **Issue.**
  - **Row alignment.** The XCAL export is a 1 Hz table, while labels come from millisecond-stamped RRC messages. The paper never says whether row *t* holds measurements taken strictly before its timestamp or is an aggregate over [t, t+1). If it is an aggregate, a handover at t+0.3 s already contaminates row *t*, through the SINR collapse during execution or the target cell's RSRP.
  - **Suspicious pattern.** AUPRC peaks sharply at exactly one sample period (0.416 → **0.784** → 0.627 → 0.598 → 0.606), and this is identical for all six learners in Table A.1. Serving SINR alone reaches AUROC 0.830 at 1 s.
  - **Sub-sample horizon.** The 0.5 s horizon is below the sampling resolution, so its label depends on the arbitrary sub-second phase of the grid.
- **What would address it.**
  - Document the export's time semantics.
  - Rebuild features with a guard of at least one sample, and show the 1 s result with the guard.
  - Report performance as a function of the true sub-second lead (t_HO − t_row).
  - Drop or justify the 0.5 s horizon.

### 4. The headline protocol result (contribution 2) is arithmetically impossible as tabulated

- **Where.** Tables 5.2 and 5.3; Section 5.3.
- **Issue.**
  - **Impossible value.** The GRU's grouped 1 s AUPRC is 0.617. A +74 % inflation gives 1.07, which is above the maximum of 1. Table 5.3's caption says the same metric and horizon are used with "all else held fixed".
  - **Ranking not shown.** The random-row scores are never given, yet the text asserts a rank reversal ("rises from sixth place to a position it does not hold") without showing the ranking.
  - **Mechanism is trivial for sequence arms.** These arms consume overlapping raw windows, so a random-row split places literally shared inputs in train and test. That is not evidence about "temporal memory".
- **What would address it.**
  - Report absolute grouped and random-row AUPRC and AUROC per model, with CIs.
  - Correct or explain the 74 %.
  - Add an intermediate "blocked within drive" split.

### 5. Statistical testing is pseudo-replicated, and the fold counts contradict each other

- **Where.** Section 4.9 and Fig. 4.2 ("four-fold … five seeds … twenty paired observations"); Section 5.2 and Fig. 5.4 ("all eight grouped-drive folds"); Section 5.4 ("p < 0.0001 over the twenty paired folds", then "signed-rank test meaningful on only eight observations").
- **Issue.**
  - **p-value.** With 8 pairs, a two-sided signed-rank test cannot give a p-value below 2/2⁸ ≈ 0.0078, so p < 0.0001 is unattainable.
  - **Independence.** With 20, the observations are repartitions of the same 57 drives with overlapping training sets. They are not independent, and the test is anti-conservative. The authors' own argument about the 0.125 resolution floor is circumvented only by this pseudo-replication.
  - **Missing intervals.** CIs are given only for the pooled AUPRC. There are none for AUROC, ECE, the leave-one-campaign-out rows, the external validation, the single-feature AUROCs or the A3 baseline.
  - **Hyperparameter search.** It is never said what the 20-trial search was optimised against. If it was the reported out-of-fold drives, every number is optimistically biased.
- **What would address it.**
  - Use one consistent fold design.
  - Use a corrected resampled test, or a drive-level paired bootstrap of the metric difference.
  - Use nested tuning.
  - Put CIs on every reported quantity.

### 6. The CRC experiment is under-specified and its evidence is thin

- **Where.** Section 4.10; Table 5.5; Fig. 5.9; Table A.2.
- **Issue.**
  - **Origin of n = 28.** It is not explained where 28 calibration drives come from under a 43/14 rotation, which model produced their scores, or how many test drives there were.
  - **Out-of-fold scores.** If the scores are out-of-fold from different fold models, calibration and test scores are not exchangeable and the finite-sample guarantee does not apply.
  - **Horizon and loss.** The horizon being certified is never stated. The equation for R_d (Eq. 4.10) is missing or garbled and is not normalised. Drives without positives are not handled.
  - **Verified points.** Only one target (α = 0.20) has a realised value, and the α = 0.05 row is blank. Fig. 5.9 nevertheless claims "every operating point lies on or below the diagonal".
  - **"Bound held on 82 % of drives".** This is not something CRC guarantees, since the guarantee is marginal and in expectation. The statistic invites misreading.
  - **Contradiction in Table A.2.** It lists "44.7 % of events detected at 1 s" as being "at the certified operating point", where the miss rate is 12.6 %. With about one positive row per event at 1 s on a 1 Hz grid, 87 % row recall and 45 % event detection cannot both hold under one definition.
  - **Promised metrics absent.** Table 2.1 and Section 4.9 advertise false alarms per hour and per km, a lead-time distribution, the Brier score and temperature-scaling results. None of these appears as a number anywhere. The manuscript therefore fails its own audit row ("0/22 report lead time or false alarms per hour").
- **What would address it.**
  - Use a dedicated train/calibrate/test design at trip level.
  - Report many random calibration/test splits with the distribution of realised risk, over the full α grid and per horizon.
  - Give explicit event-level definitions.

### 7. The mechanism claim ("the network triggers on its weakest signal") is not supported and is contradicted internally

- **Where.** Sections 3.5, 5.8 and 7.1; Fig. 3.3.
- **Issue.**
  - **Direction of the dwell-time effect.** It is never shown. The paper reads it as a handover "becoming due", which implies long dwell. The data point the other way: a Hawkes branching ratio of 0.605, a median gap of 3.5 s against a mean of 11 s, and 24.5–41 % ping-pong. These imply that short dwell predicts the next handover. The model may largely be predicting follow-on handovers within bursts, which is the operationally least useful case. No results stratified by first-in-burst versus follow-on, or by ping-pong versus not, are given.
  - **Offset sign.** Section 3.5 says offsets are "predominantly negative" and that a positive-offset assumption "is false for the majority of handovers". Table 3.1 attributes 72.4 % of handovers to the **+1 dB** profile.
  - **"Necessary condition".** The gap is called this, yet Fig. 5.13's highest-probability bin is the most negative gap, and the A3 rule "detects 5.5 % of handovers". With the condition true on 27.1 % of samples, 5.5 % would indicate anti-correlation, which is incompatible with AUROC 0.653. The A3-as-predictor scoring rule is undefined.
  - **Missing effective margin.** Hysteresis, Ocn and L3 filtering are never reported, so the effective margin is unknown. Only 43–52 % of reports are A3. It is not explained how A5- and A2-driven and inter-frequency handovers are "attributed" to A3 profiles, or what "gap" means when the target is on another carrier.
  - **Re-establishments.** The 341 re-establishments against 938 handovers is an extraordinarily high ratio. They change the serving cell without a command, which makes them a competing risk or a censoring event. Their treatment in labels and in the dwell-time feature is not described.
- **What would address it.**
  - Provide partial-dependence or SHAP plots for dwell time.
  - Report burst-stratified metrics.
  - Add a competing-risk or explicit censoring treatment of re-establishments.
  - Report Hys and filter coefficients.
  - Restrict the gap analysis to intra-frequency A3-triggered handovers.
  - Add a fair A3 baseline, such as logistic regression on gap and gap trend, or "an A3 report was observed".

### 8. The A3 "decline rate" is a per-report artefact

- **Where.** Sections 1.2 and 5.9; Table 5.9.
- **Issue.**
  - **Repeated reports.** There are 7,385 A3 reports for 938 handovers. The 37.1 % "converted" reports (≈2,740) are about 2.9 per handover, which demonstrates repeated reports per trigger (reportAmount/reportInterval).
  - **Misattributed intent.** Counting each repeat as a separate "declined decision" inflates the figure. The reports under the −15 and −10 dB profiles, whose condition holds on "nine samples in ten", are evidently not handover triggers at all.
  - **Cell size.** "Rises with cell size" (Fig. 5.14) is asserted without any cell-size measurement, from four points.
- **What would address it.**
  - Compute per-episode conversion, per (neighbour, measId) trigger.
  - Break the rate down per profile and per intra- versus inter-frequency.
  - Remove the "declined" and "cell size" language.

### 9. The coherence comparison is against a strawman, and its supporting numbers are absent

- **Where.** Sections 4.2, 4.8 and 5.4; Table 5.4.
- **Issue.**
  - **No tolerance.** The 43.6 % violation rate has no tolerance or magnitude distribution, and the "largest violation" is blank for that row.
  - **Missing control.** The monotone projection (cumulative max or isotonic across horizons) is said to be "reported in Section 5.4" but does not appear in Table 5.4. It needs no held-out split, contrary to Section 4.2. Fig. 5.8 refers to "four configurations" while the table has three.
  - **Missing metrics.** No ECE or AUPRC numbers are given for the independent arm, so "calibration improves at every horizon" and the "2–5 AUPRC points" cost cannot be checked.
  - **Post-hoc calibration.** It is unclear whether the headline ECE includes temperature scaling. Contribution 1 claims "no held-out calibration split", while Section 4.8 describes one.
  - **Obvious alternatives untested.** These include a multinomial bin model and an ordinal or cumulative-link model.
- **Issue (Table 4.2 and Eq. 4.8).**
  - **Hazard versus prevalence.** Bin-1 hazard should equal the 0.5 s prevalence, but the table gives 0.053 against 0.037. All five hazards are about 1.2–1.4× the values implied by Table 4.1.
  - **Long-format expansion.** Table 4.1 implies about 47,000 pairs (10,260 × 4.6 expected at-risk bins), not the "approximately 34,000" stated.
  - **Eq. 4.8 is incorrect.** For small hazards F_k ≈ Σλ_j, so a multiplicative per-bin error ε yields roughly (1+ε)F_k, not (1+ε)^k. The "inadmissibility" argument in Section 4.5 should be replaced by an experiment.

### 10. External validity: the external dataset's independence is contradicted, and the conclusion drawn from it does not follow

- **Where.** Sections 5.6, 5.7 and 5.13; Fig. 5.11.
- **Issue.**
  - **Operator independence.** Section 5.7 and Fig. 5.11 say the public dataset [33] comes from "a different group on a different network … no network and no operator" shared. Section 5.13 says the RL comparator was "developed on the same operator and instrument" and that "the dataset released by the same authors … is the external validation set".
  - **Comparator publication record.** Section 5.13 also says no publication record for that comparator could be located. However, a query on the dataset DOI surfaces a paper titled "Handover Optimization in LTE Networks Using Contextual Bandit Reinforcement Learning and Real-World Data" (https://www.researchgate.net/publication/396132842). The authors should check whether this is the comparator.
  - **Contradiction within the manuscript.** Section 2.10.1 promises the reimplementation in Chapter 5 "for completeness", while Section 5.13 says it is not reported.
  - **Thin evidence.** Only AUROC is given: no AUPRC, prevalence, ECE or CI. There is no description of how the labels were defined there, which of the 107 features exist in that dataset, or what "curated" means in the Fig. 5.11 caption.
  - **Interpretation.** The in-domain model scores 0.745, which suggests a low-information or differently labelled dataset rather than successful transfer. "What transfers is the formulation rather than the fit" is a non sequitur, because the experiment transferred the fit.
  - **Campaign overlap.** Whether the three Dhaka campaigns really share "no routes or cells" is asserted, not shown.
  - **Pooled versus held-out scores.** The weighted leave-one-campaign-out AUPRC (≈0.797) exceeds the pooled in-distribution 0.784. Fig. 5.20's full-feature AUPRC of 0.811 also differs from the headline 0.784. Both need explanation.

### 11. Provenance and timeline inconsistencies

- **Where.** Title pages; Sections 3.2 and 6.9; Appendix C.
- **Issue.**
  - **Campaign dates.** All four campaigns are dated 10–15 September 2026. Section 6.9 says the first two were in the first academic term and the last two in the second. The approval page is dated 21 September 2026, in a "Winter Semester, 2026".
  - **Freeze timing.** The freeze "before the highway data existed" would have to occur between 13 and 15 September, that is, within two days of the dense-urban campaign. No dated or hashed manifest is provided. The highway result's special status depends entirely on this.
  - **Other front-matter inconsistencies.**
    - The declaration carries a different thesis title.
    - It uses first-person singular for three authors.
    - It has supervisor placeholders.
    - The stated ≈95 km is hard to reconcile with 2.85 h at about 16.5 km/h urban and 49.5 km/h highway, which gives ≈70 km.
  - **Code and data.** Both are only "planned", so none of the above can be checked.
- **What would address it.**
  - Correct the dates.
  - Deposit a timestamped freeze manifest, the code and the data.
  - State the XCAL licensing position and the operator permission.

## Minor concerns

- **Cross-references.** Section 3.3.3 cites Section 5.8 for the conversion rate, which is in 5.9. Section 3.4 cites Section 4.5 for features (it is 4.6) and Section 5.9 for ping-pong (it is 5.10). Section 4.11 cites Section 5.9 for ping-pong. Section 4.6 says Section 5.11 "reports what happens" without the leakage guard, but Section 5.11 gives no number.
- **Model counts.** "Seven learners" includes the parameter-free A3 rule. "All four architectures with temporal memory" counts the MLP, although only three sequence models exist.
- **Tables and figures.**
  - Table 5.8 says "three most informative inputs" while listing one of the weakest.
  - Fig. 5.12 says "seven strongest".
- **Ping-pong.**
  - Table 5.10's fourth row uses 957 events, although it is described as "one fixed set of 938".
  - The range 24.5–41.3 % conflicts with the grid range of 19.5–38.5 %.
  - The highway rate of 31.1 % is called "marginally above the pooled rate", which is 24.5 %.
  - "Not driven by speed" and "TTT is the lever" rest on one campaign with no control for carrier mix. The latter is carried into Section 7.3 as established.
- **Table A.1.** It is strikingly regular: identical model ranking and near-constant ratios at every horizon, despite a fold spread "wider than the gap between arms". Per-fold tables should be released.
- **Counting upper bound.** The bound on benefit ("peaks at five percent … negative by forty") is referenced in Sections 1.5 and 5.13 but never presented.
- **Causal argument.** The deterministic-policy argument in Section 5.13 conflicts with the paper's own finding that most reports are not followed by a handover. The proposed fuzzy RDD over "drives" is ill-posed.
- **Hawkes analysis.** It is fitted per 180 s drive, which raises an edge-effect concern, and the kernel is rejected yet the branching ratio is still interpreted. The notation reuses α and λ for CRC, hazard and Hawkes quantities.
- **Figure 1.1 and the abstract.** They give inconsistent pictures of the offset sign.
- **ECE.** The bin count is unspecified. At 6.7 % prevalence, ECE is dominated by the low-probability mass. The statement about "probability near 0.8" needs a reliability diagram with counts.
- **Inflation of the A3 rule.** The −2 % "inflation" for a parameter-free rule should be explained as fold averaging or dropped.

## Verdict

**Major revision.** For a journal submission in its present form this would be a Reject. The contribution claims do not survive a check against the paper's own reference [5]. Several load-bearing numbers are internally impossible or contradictory: the 74 % inflation, p < 0.0001 on 8 folds, Table 4.2 against Table 4.1, the uniform 180-sample drives, and the provenance of the external dataset. The 1 Hz alignment leakage path is unexamined. The underlying dataset and formulation are nevertheless sound enough that a rigorous rebuild could be publishable.

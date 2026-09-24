SEED: 807f22ae2549758d66721e57bf553130
LENS: 2 — Claim-vs-evidence alignment (0x80 = 128; 128 mod 6 = 2)
STANCE: 1 — Adversarial (0x7f = 127; 127 mod 3 = 1)

# Review (bravo): "Conformalized Discrete-Time Hazard Modeling for Multi-Horizon Handover Forecasting in Cellular Networks"

## Summary

The manuscript asks whether the next LTE handover command can be forecast from handset-side measurements at five look-ahead times (0.5–5 s), with probabilities that are coherent across horizons, calibrated, and accompanied by a distribution-free miss-rate guarantee. The data are four XCAL drive-test campaigns on one operator in Dhaka/Gazipur: 57 "drives", 10,260 one-hertz samples and 938 RRC-decoded handovers. The task is cast as discrete-time survival, with one long-format binary model emitting per-bin hazards. Seven learners are compared under grouped-by-drive 4-fold CV repeated over 5 seeds. A warning threshold is set by conformal risk control (CRC) with the drive as the exchangeable unit.

The headline result is LightGBM at AUROC 0.933, AUPRC 0.784 and ECE 0.024 at 1 s, against AUROC 0.653 for a reconstructed Event A3 rule. Secondary results are:
- zero horizon-ordering violations against 43.6 % for independent classifiers;
- random-row splitting inflating a GRU by 74 % against 4 % for logistic regression;
- leave-one-campaign-out AUROC of 0.909–0.949;
- external transfer at AUROC 0.752 against 0.745;
- a "mechanism" claim that the network triggers on its weakest signal (dwell-time AUROC 0.874 against A3-gap AUROC 0.566);
- 62.9 % of A3 reports "declined";
- a Hawkes and ping-pong characterisation.

The manuscript's rhetoric is that of measured restraint. Its content is not. Several headline claims are contradicted by the manuscript's own tables, several numbers are arithmetically impossible as stated, and the two "network findings" rest on a misreading of LTE measurement reporting.

## Major concerns

**1. Headline claims are contradicted by the manuscript's own evidence (lens: claim-vs-evidence).**
- *Issue / Where:*
  - (a) The abstract, Contribution 4, §3.5 and Table 6.4 (P4) claim the deployed A3 offsets are "negative rather than positive" and that the positive-offset assumption "is false for the majority of handovers". Table 3.1 states that the dominant profile is a **+1 dB** offset carrying **679 of 938 (72.4 %)** handovers. Figure 1.1 and Table 5.11 repeat "+1 dB". So the positive-offset assumption holds for at least 72 % of handovers, and the "opposite in sign" claim is false on the manuscript's own numbers. Three of the five listed offset *values* are negative, but that is a count of configuration values, not of handovers.
  - (b) §5.8 calls the gap "a necessary condition". Yet Figure 5.13 reports that the *most negative* gap bin has the highest handover probability, and the reconstructed A3 rule "detects 5.5 % of handovers" (§5.1). If A3 were the operative trigger and were correctly reconstructed, nearly every A3-triggered handover would be preceded by entry-condition satisfaction. A 5.5 % hit rate says the reconstruction is broken, not that the network "triggers on its weakest signal". Likely causes are 1 Hz unfiltered RSRP against the UE's L3-filtered 40–200 ms samples, a best-neighbour-in-export that is not the target cell, no Hys/Ocn in Table 3.1, and inter-frequency objects pooled with intra-frequency ones.
  - (c) §5.7 concludes that "what transfers is the formulation rather than the fit" from an experiment that transfers *the fit* "without refitting".
  - (d) §5.6 claims "0.933 before and 0.933 after" is "the strongest available evidence" against over-fitting. A three-decimal coincidence on a pooled metric is not evidence of anything.
  - (e) §5.10/§7.3 assert that TTT is "the lever governing ping-pong, having ruled out speed". This is a causal claim from one highway campaign confounded with carrier mix, in a thesis that elsewhere disclaims causal inference.
- *Why it matters:* Contribution 4 and the "mechanism" finding, called "the most compact statement of what the thesis found", are the wireless-side novelty. As written, neither survives a reading of Table 3.1 and §5.1.
- *What would address it:*
  - Report the offset, Hys and TTT distributions weighted by handovers and by measurement object, with intra- and inter-frequency separated.
  - Validate the A3 reconstruction against the logged A3 MeasurementReports: what fraction of actual A3 MRs does the reconstruction reproduce within ±1 s?
  - Compute the gap against the *reported or target* cell.
  - Drop or rewrite the "necessary condition", "weakest signal" and "lever" language.

**2. Several reported numbers are impossible or mutually inconsistent.**
- *Where / Issue:*
  - (a) Table 5.3 gives +74 % AUPRC inflation for the GRU, whose grouped AUPRC is 0.617 (Table 5.2). 0.617 × 1.74 = 1.07, which exceeds 1. The abstract's own headline number cannot be a relative AUPRC gain as the caption states. The inflation metric is never defined, and no random-split absolute scores are given.
  - (b) Table 4.2's hazards imply cumulative incidence of 0.053, 0.093, 0.171, 0.231 and 0.325 by Eq. 4.4. Table 4.1 gives prevalences of 0.037, 0.067, 0.125, 0.175 and 0.259. These cannot both describe the same data. The bin-1 hazard *is* the 0.5 s prevalence, up to a handful of censored rows.
  - (c) §4.4 says the long-format expansion yields "approximately 34,000" pairs. From Table 4.1, the at-risk count is 10,260 × (1 + 0.963 + 0.933 + 0.875 + 0.825) ≈ 47,000. A 28 % shortfall suggests the at-risk set or the censoring is implemented differently from Eq. 4.6.
  - (d) §5.11 and Figure 5.20 give the full-feature 1 s AUPRC as **0.811**. The headline everywhere else is **0.784**.
  - (e) Table A.2 places the 44.7 % event detection at 1 s "at the certified operating point" of α = 0.20. There the realised per-drive miss rate is 12.6 %, i.e. about 87 % of positive samples alarmed. On a 1 Hz grid at the 1 s horizon there is at most one positive sample per event. Sample recall of about 87 % and event detection of 44.7 % are therefore irreconcilable without an unstated definition of "detected". The CRC horizon is also never stated.
  - (f) 938 events on a 1 Hz grid with a 90.5 % "resolvable" ceiling imply about 850 positives at 1 s (8.3 %), not 6.7 %.
  - (g) §5.2 refers twice to "four architectures with temporal memory"; §4.7 lists three.
- *Why it matters:* Appendix C asserts that every table is "regenerated from the stage outputs rather than transcribed". These discrepancies show that either this is not so or the pipeline has bugs in label construction or expansion. A reader cannot trust the 0.933 while the label arithmetic does not close.
- *What would address it:* A reconciliation table covering events, positives per horizon, at-risk rows per bin and censored rows. Absolute scores under both split protocols. A single frozen results file from which every number is drawn.

**3. The statistical protocol overstates its resolution, and "eight folds" contradicts "twenty".**
- *Where / Issue:*
  - §4.9 and Figure 4.2 specify 4 folds × 5 seeds = 20 paired observations. §5.2 and Figures 5.4 and 5.6 speak of "eight grouped-drive folds". §5.4 says the signed-rank test is "meaningful on only eight observations". The same section reports *p* < 0.0001 "over the twenty paired folds". With n = 8 the smallest two-sided signed-rank *p* is 2/2⁸ ≈ 0.008, so *p* < 0.0001 is unattainable.
  - With n = 20 the observations are re-partitions of the same 57 drives and are not independent. The manuscript's own argument that four folds floor *p* at 0.125 shows that seed repetition is being used to manufacture resolution. No corrected resampled test (Nadeau–Bengio or similar) is used.
  - Hyperparameters (20 trials per arm) are tuned on unspecified data. "Fold hygiene" (§4.9) lists the scaler, threshold and calibrator but not the search. If tuning used the same outer folds, every score is optimistically biased.
  - Table 5.2 carries no intervals. The LightGBM–LR gap (0.784 against 0.712) is never tested.
  - The A3 rule has no parameters to fit, yet its score moves by −2 % under re-splitting (Table 5.3). That movement therefore gives a lower bound on the pure noise of the fold-mean metric.
- *What would address it:* State the fold count once. Use nested CV. Report drive-bootstrap CIs on paired *differences*. Use a variance-corrected test.

**4. The "drive" is not an independent or exchangeable unit, which undermines the grouped CV, the bootstrap and the CRC guarantee (Contribution 3).**
- *Where / Issue:*
  - In Table 3.2 every campaign has exactly 180 samples per drive (2,700/15 = 1,440/8 = 3,600/20 = 2,520/14 = 180). §3.4 defines a drive as a variable-length contiguous segment of at least 60 s. The "drives" are evidently fixed 3-minute chunks of one continuous journey per day, and this is undisclosed. The durations also disagree with the sample counts: 46 min against 2,700 s, and 43 min against 2,520 s.
  - Adjacent chunks share cells, traffic, route and serial correlation. Figure 3.1 itself shows that events cluster at junctions revisited across chunks. Drives within a day are not exchangeable, drives across campaigns are not identically distributed, and future deployment drives are neither.
  - Dwell-time and history features are left-truncated at each chunk boundary, since "none crosses a drive boundary".
  - The CRC evidence itself is thin. Table 5.5 contains **one** validated operating point. The α = 0.05 row has "---" for realised risk. Figure 5.9's "every operating point lies on or below the diagonal" is therefore a claim about a single point.
  - n = 28 calibration drives is never reconciled with the 43/14 train/test split of §4.9. "Bound held on 82 % of drives" has no stated denominator.
  - Eq. 4.10 is missing; the risk is written as a set, not a rate.
  - The risk is a sample-level miss fraction, not an event-level one.
  - The "campaign-design rule" α ≥ 1/(n+1) is an immediate, well-known property of the CRC bound with B = 1 in [20]. Presenting it as something that "appears nowhere in the handover literature" inflates it.
- *What would address it:*
  - Disclose the segmentation.
  - Use journey-level or campaign-level blocks, or at least a spatial or temporal buffer between train and test chunks.
  - Report coverage over many random calibration/test splits and at several α and horizons.
  - Discuss CRC under non-exchangeability (weighted or covariate-shift variants).

**5. The A3 "decline rate" and RLF counts reflect a misunderstanding of LTE reporting.**
- *Where / Issue:*
  - §5.9 counts 7,385 A3 reports, of which 37.1 % (about 2,740) are "followed by a handover within 2 s". There are only 938 handovers, so about 2.9 "converted" reports per handover.
  - 7,385 A3 reports in 10,260 s is 0.72 per second. With A3 at 43–52 % of all reports (§3.3.3), this is about 1.5 reports per second in total. This is the signature of event-triggered *periodic* reporting (reportInterval/reportAmount). Repeats under one triggered measId are not independent requests that the network "declines".
  - A profile with a −15 dB offset whose condition "holds on nine samples in ten" (Figure 3.3) behaves as a quasi-periodic measurement and is plausibly an inter-frequency or load-balancing object. §3.5 labels everything "intra-frequency" while Table 5.11 reports inter-carrier handovers.
  - "Decline rate rises with cell size" rests on four points with cell size unmeasured.
  - 341 re-establishments in 2.85 h, one per 30 s against 938 handovers, is extraordinary. It is asserted to be "not pathological", never analysed, and used in the motivation.
  - Re-establishment is a *competing risk*: it ends serving-cell dwell without a handover command. The likelihood in §4.4 treats it as neither event nor censoring.
- *What would address it:* Collapse reports to trigger episodes per (measId, cell). Report conversion per episode and per measurement object. Audit the re-establishment causes. Model or censor the competing events explicitly.

**6. Alternative explanation for the headline: the model forecasts the tail of ping-pong bursts and post-report latency, not handovers in general.**
- *Where / Issue:*
  - The median inter-handover gap is 3.5 s, the Hawkes branching ratio is 0.605, and 24.5–38.5 % of handovers are returns. Dwell time alone gives AUROC 0.874, and the GRU, which sees no history features, scores exactly 0.874 (Tables 5.2 and 5.8).
  - The manuscript interprets dwell as "a handover is becoming due". Self-excitation implies the opposite direction: *short* dwell predicts an imminent handover. The sign is never reported.
  - AUPRC peaks at 1 s and collapses by 2 s (0.784 to 0.627, lift 11.7× to 5.0×). This is consistent with the predictor keying on signals that exist only once the UE has already triggered. The leakage guard (§4.6) still admits reports "at or before *t*", and A3 reports precede the command by only about 50–300 ms. The reported 0.811 = 0.811 ablation does not rule this out, because 1 Hz radio rows stamped at *t* may aggregate over an interval that straddles the command. The export time-stamping convention is never given.
  - The 0.5 s horizon is unidentifiable from 1 Hz inputs. Its AUPRC (0.416) is almost exactly half the 1 s value, as expected if the 0.5 s label is a random half of the 1 s label.
- *What would address it:* Stratify all metrics by time since last handover (for example, more than 15 s against 15 s or less) and by first-in-burst against return. Report the dwell sign and partial dependence. Document the export timestamp semantics. Drop the 0.5 s horizon or collect sub-second data.

**7. Baselines and controls are weak or unfair, and the coherence comparison is against a straw man.**
- *Where / Issue:*
  - Sequence models receive "raw per-second measurements rather than the engineered summary features" (§4.7). They are therefore denied dwell time and history, the strongest block. "The only thing varying between arms is the learner" is false, and the "no temporal model wins" finding is confounded.
  - No trivial baselines are reported: dwell-only, "A3 report in last second", RSRP-slope extrapolation. None of the 22 audited methods is reproduced.
  - The coherence result (43.6 % against 0 %) counts violations of any magnitude. No violation-size distribution is given. Table 5.4 has no ECE column despite its title, omits the monotone-projection row that the text says is "reported", and marks the independent arm's largest violation "---".
  - §4.2's claim that monotone projection "consumes a held-out split" is wrong. A per-sample cumulative-max or PAV projection needs no data and would also give 0 % violations. Ordinal/cumulative-link or multi-output monotone models are not considered.
  - Whether the hazard arm gains or loses discrimination relative to independent fits is never tabulated.
  - Eq. 4.8 is incorrect: for F = 1 − Π(1 − λ) with small λ, a multiplicative hazard error propagates approximately linearly, not as (1 + ε)^k. The reweighting-inadmissibility argument, cited in §6.5 as "deep analytical knowledge", needs redoing.
  - ECE rising to 0.141 at 5 s in the *unweighted* hazard model is unexplained.
  - The gloss that ECE 0.024 means "near 0.8 → ~80 %" (§5.4) does not follow. Equal-mass bins are dominated by near-zero predictions at 6.7 % prevalence. No reliability diagram or high-score bin is shown.
- *What would address it:* Give every learner the same inputs. Add the trivial baselines and at least one reproduced published method. Add the projection, cumulative-max and ordinal controls. Provide reliability diagrams with per-bin counts.

**8. The external validation is under-described and its independence is contradicted.**
- *Where / Issue:*
  - §5.7 and Figure 5.11 call [33] "a different group on a different network… no network and no operator" in common. §5.13 says the dataset was "released by the same authors" as an RL comparator "developed on the same operator and instrument". Both statements cannot be true.
  - Nothing is said about how a 107-feature model transfers "without refitting". It is not stated whether the public set contains RRC signalling, configuration identifiers, neighbours or a 1 Hz grid, or how labels and prevalence were defined there.
  - An in-domain ceiling of 0.745 suggests weak labels or features. A drop from 0.933 to 0.752 is spun as success, with no CI.
  - [33] is cited as "v2" with a ".1" DOI.
  - §5.13 withholds the RL comparator result because "no publication record… could be located". A search on the dataset DOI returns a paper titled "Handover Optimization in LTE Networks Using Contextual Bandit Reinforcement Learning and Real-World Data" (researchgate.net/publication/396132842). If that is the comparator, it must be cited and the comparison reported.

**9. The timeline and "freeze" are not credible as described, and reproducibility is nil.**
- *Where / Issue:*
  - Table 3.2 dates all four campaigns 10–15 September 2026, and the approval page is dated 21 September 2026. §6.9 says the first two campaigns belonged to the first academic term and the last two to the second.
  - The highway "frozen" claim therefore requires that all features, seven tuned models, the DA experiments and the protocol were fixed between 13 and 15 September.
  - The manifest is described but neither shown nor hashed. Code and data are "Planned".
  - The 22-paper audit (Table 2.1), on which every "none of 22" novelty claim rests, never lists the 22 papers, so it is unverifiable.
  - The assertion that survival formulations have "not been applied to mobility events" rests solely on that unlisted audit.

**10. Reference integrity.**
- [6] is cited as Liu, Peng and Tan, "M2HO: Mitigating the negative impact of mobility management on handover performance". The MobiCom 2024 paper is "M2HO: Mitigating the Adverse Effects of 5G Handovers on TCP" (dl.acm.org/doi/10.1145/3636534.3690680). The cited use of it ("read mobilityControlInfo…") should be re-checked.
- [29], arXiv:2403.04379, is "Performance evaluation of conditional handover in 5G systems under fading scenario" by Deb, Rathod, Balamurugan, Ghosh, Singh and Sanyal. The cited title and co-authors (Monogioudis, Calin) do not match.
- [4] is by its own title a *5G* configuration study, yet it is used as the LTE offset comparator in §2.2 and §3.5 without comment.
- [34] is never cited in the text.
- The author initials in [3] and the 2026-dated items [7], [10], [11], [15] should be verified against source.
- This pattern suggests that bibliographic entries were generated rather than transcribed. At a Q1 venue this is disqualifying until fixed.

## Minor concerns

- The Declaration carries a different title ("Uncertainty-Aware Multi-Horizon…") and "[Supervisor Name, Title]" placeholders. It uses first-person singular for three authors, and §6.6 refers to "the author's own handset".
- Cross-references have drifted:
  - §3.3.3 points to the conversion rate in "§5.8" (it is §5.9);
  - §3.4 and §4.11 point to ping-pong in "§5.9" (it is §5.10);
  - §3.4 points to features in "§4.5" (it is §4.6);
  - §5.4 says "all four configurations" where Table 5.4 has three.
- §5.10 says "one fixed set of 938 handovers under four definitions", but the fourth row uses 957 events. §2.4 repeats the 24.5 → 41.3 % range as if on 938. Figure 5.15's grid tops out at 38.5 %.
- §5.10 calls the highway ping-pong rate of 31.1 % "marginally above the pooled rate". The pooled rate is 24.5 %.
- "Approximately 95 km" is not reconciled with the stated speeds. The highway at 49.5 km/h for about 42 min is about 35 km. The urban campaigns at about one third of that speed for about 129 min add about 35 km. That gives about 70 km.
- §5.3 says the GRU rises "to a position it does not hold". The random-split leaderboard is never shown. Random-row splitting of overlapping windows for sequence models is trivially leaky, and this should be framed as known.
- Table A.1 shows an identical model ordering and near-constant inter-model ratios at all five horizons. Per-fold dispersion should be shown.
- Hawkes: the *n* for the KS test is not given, 180 s chunks induce edge effects, and ping-pong is an obvious confound. The analysis "supports the same conclusion" about TTT only rhetorically.
- The "counting upper bound on benefit… peaks at five percent… turns negative by forty" (§5.13) is mentioned but appears in no table or figure.
- Figures 5.1 and 5.2 cannot be assessed. False alarms per hour and per km and the lead-time distributions promised in §4.9 and Table 2.1 appear in no table.
- It is unclear whether the headline ECE is before or after temperature scaling. The abstract says "without post-hoc correction"; Table 2.1 lists temperature scaling.
- Ethics: the operator is anonymised but identifiable from the route and dates. There is no statement on operator or XCAL licence terms for data release.
- Chapter 6 should be removed for journal submission.

## Verdict

**Reject** (in current form; resubmission after a rebuild is conceivable). The hazard-plus-grouped-evaluation idea is sound. However, a central contribution is contradicted by Table 3.1, the abstract's 74 % figure is arithmetically impossible, and the label and hazard tables do not reconcile. In addition, the "exchangeable drive" is an undisclosed 180-second chunk, the A3 "mechanism" and "decline" findings rest on a faulty rule reconstruction and on miscounting periodic reports, and several references are misattributed. These go beyond what a major revision of the existing text can repair.

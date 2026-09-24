SEED: `80660342efdae5d1b47725a3a0d308b0`
AXIS: 0 — Distinguishing-test failure
STANCE: 0 — Skeptical-but-fair

---

# Review — Reviewer bravo

*Note on scope: the supplied text is missing §5.12 (Discussion against objectives), §5.13 (Threats to validity), §6.1–6.4 and §7.3, and the reference list is interleaved into the middle of Chapters 5 and 6. I have not assessed the threats-to-validity section and my concerns should be read with that gap in mind.*

## Summary

The paper asks whether an LTE handover command can be forecast, one to five seconds ahead, from quantities a handset already holds, using ground truth decoded from RRC signalling rather than vendor counters. Four drive-test campaigns on one commercial operator in Dhaka/Gazipur yield 10,260 one-hertz rows and 957 handover commands. The headline methodological claim is an alignment audit: in 75.9% of handovers the export row stamped *before* the command already carries the *post*-handover serving cell, which the authors attribute to end-of-second aggregation; lagging every export feature one row collapses the one-second AUPRC of the same model from 0.600 to 0.179. The task is then posed as discrete-time survival (hazards multiplied via the product-limit identity, so horizon ordering is a theorem), evaluated leave-one-campaign-out, with a conformal risk-control bound whose exchangeable unit is a driving unit. Secondary results: a four-rung splitting ladder (random rows inflate one-second AUPRC by 48%), and two corrected network characterisations (A3 episode conversion 30% vs 63% per report; 75% of A3 handovers under a positive offset).

The honesty of the framing is unusual and genuinely creditable — the paper demolishes its own best prior number and says so repeatedly. My problem is that the honesty is not matched by the evidence, and that the numbers in the tables do not support the sentences in the prose.

## Major concerns

### 1. The aggregation-mechanism claim is supported only by experiments that could not have come out the other way (AXIS)

**Issue.** §5.1 advances a specific causal mechanism — the exporter writes one row per second carrying state as of the *end* of the second, so the row stamped *t* shows the target cell whenever `m = 1 − delta − x > 0`. Three experiments are offered as tests. None is a distinguishing test.

- **The NUWiNS result is entailed by its own construction.** The corpus is native 10 Hz. The authors downsample it themselves, keeping the last sample of each second (93.2% contaminated) or the first (4.1%). That contrast is arithmetic, not evidence: if you build rows by taking the last sample of a second, and the serving-cell register updates ~60 ms after a command, then a command in that second is contaminated with probability ≈ P(delta < 1 − x). No outcome other than "high under last-sample, low under first-sample" was physically possible. It demonstrates the mechanism is *sufficient*; it does not test whether it is what XCAL's own 1 Hz export does.
- **The Raca/G-NetTrack control is confounded four ways at once.** Table A.3 concedes it differs in instrument, operator, country, event clock (serving-cell-identifier changes, *no signalling*), and row semantics. Its 29.4% is therefore uninformative about aggregation specifically. §5.1 even reports that the Raca data shows a *larger* jump at t−2 → t−1 (+57%) than at t−1 → t (+38%) — i.e. the diagnostic signature the authors propose (an anomalous jump at the final step) is present in the dataset they designate as the clean control, just at a different lag. That is a false-positive for their own detector and it is passed over in one sentence.
- **Their own export does not match the mechanism's prediction, and the gap is patched post hoc.** The mechanism predicts ≈93%; the authors measure 75.9%. §5.1 rescues this with an auxiliary hypothesis — "the exporter refreshing the serving-cell field one row late" — and then asserts that "the uncontaminated figure for it is not zero but about 24%". That auxiliary is fitted to the residual and never independently tested.
- **The one genuinely falsifiable test is n = 15.** "Of the 15 handovers whose execution crosses the second boundary, m < 0, not one has the target cell on the row stamped t." This is the best thing in §5.1 and I want to credit it. But with x having p90 = 99 ms and max 105 ms, and 65% of commands recording non-zero interruption, a uniform delta implies roughly 40–60 handovers with m < 0 out of 938, not 15. Either x is systematically under-recorded, or the m < 0 set is not constructed the way the text says. Until that discrepancy is resolved the falsification test is not interpretable.

**Where.** §5.1 (lines 991–1009), Figure 5.1 panels (c)–(f), Appendix Table A.3.

**Why it matters.** The alignment audit is contribution 1 and the paper's principal claim to a journal audience. If the mechanism is right, the recommendation ("lag every export feature by one row") generalises to every XCAL-derived study. If the mechanism is only *consistent* with the data and the true cause is, say, a KPI-refresh pipeline in the tool's writer thread, the correct remedy may be a different lag, or a per-field lag, and the recommendation is wrong in detail while being right in spirit.

**What would address it.** You already possess the one distinguishing experiment and §7.3 names it: re-export your own four captures at native message rate from the same XCAL sessions and *observe* the write rule instead of inferring it. That single experiment would replace the entire three-dataset argument. Absent that: pre-register the predicted contamination rate from the measured `x` distribution and your delta distribution, and report the predicted-vs-observed number with an interval, rather than reporting 75.9% and explaining the shortfall afterwards.

### 2. Three mutually incompatible values for the headline result, in three tables that all claim to hold everything else fixed

**Issue.** The one-second AUPRC of the primary model under leave-one-campaign-out is reported as:

- **0.179** — Table 5.3, Table 5.4, Table A.1, the abstract, contribution 1, §7.1;
- **0.160** — Table 5.5, LOCO column ("with all else held fixed");
- **0.157** — Table 5.6, hazard arm.

Worse, Table 5.4 and Table 5.5 disagree for *every* learner, and they disagree in a way that reverses the paper's own conclusion. Table 5.4 (LOCO): LightGBM 0.179, logistic regression 0.130 — LightGBM wins by 38%. Table 5.5 (LOCO): logistic regression 0.167, LightGBM 0.160 — logistic regression wins. §5.3 then builds contribution 3 on the latter: *"Under leave-one-campaign-out the leading learner at one second is logistic regression; under random-row splitting it is LightGBM… A study using the standard protocol of the comparator literature would therefore report a different winner on the same data."* Table 5.4 and Table A.1 say the winner is LightGBM under LOCO too, so the reordering does not occur.

Only the A3 rule agrees across the two tables (0.116), and it agrees to three decimals across all four protocols, which suggests that column was computed once and copied rather than recomputed per protocol — which would void its role as the control that distinguishes over-fitting from test-set difficulty.

**Where.** Tables 5.3, 5.4, 5.5, 5.6, A.1; prose at §5.2 (1049), §5.3 (1080).

**Why it matters.** Contribution 3 ("the protocol determines the ranking of models and not only their level") is the claim with the widest implication for the field, and it is currently contradicted by the paper's own primary results table. A reader cannot tell which number is the result.

**What would address it.** Regenerate every table from one run of the pipeline (Appendix C claims this is already enforced: *"every table reported in Chapters 4 and 5 is regenerated from the stage outputs rather than transcribed"* — that is demonstrably not true of the submitted draft). State explicitly whether Table 5.5 uses a reduced feature set, a different tuning budget, or single-seed fits, and if the reordering survives only under one of those, say so.

### 3. Coherence and calibration numbers contradict the tables they cite, and the per-campaign record contradicts the pooled claim

**Issue.** §5.4 states the independent-classifier arm *"violates ordering on 40.2% of rows, with a mean violation of 0.025 and a maximum of 0.521."* Table 5.6 says 29.0%, 0.020, 0.377. The abstract, contribution 4, §4.2 and §7.1 all quote 40.2%. The prose then says isotonic calibration makes coherence worse — *"violations rise from 40.2% to 33.4%"* — which is a fall, not a rise, under the quoted number, and a rise only under the table's 29.0%. The stale number has propagated to five places.

Expected calibration error at one second for the primary system is given as **0.012** (Table 5.3), **0.036** (Table 5.6, hazard arm), and **0.024** (§5.4 prose: *"The operational meaning of an expected calibration error of 0.024 at the one-second horizon…"*). The prose then reads 0.024 operationally — *"among the samples on which the system asserts a probability near 0.8, a handover follows within one second on approximately 80% of occasions"* — which, at a 6.8% prevalence and AUROC 0.777, I do not believe a well-populated 0.8 bin even exists to support.

Separately, §5.4 concedes *"the hazard arm has the lower calibration error on 0 of the four held-out campaigns at one second."* The hazard formulation loses on calibration in every single unit, and wins only pooled. That is a textbook aggregation artefact and it is reported in one sentence, immediately followed by an appeal to the sign test's resolution limit. The honest summary of Table 5.6 is: the hazard formulation buys coherence that a two-line cumulative maximum also buys for free, at a calibration cost relative to the isotonic composite, and with a 0-for-4 per-campaign record against its own control.

**Where.** §5.4 (1098–1114), Tables 5.3 and 5.6, §4.2, §7.1, abstract.

**Why it matters.** Contribution 4 is defended explicitly on *"reaching coherence and competitive calibration from one fit"*. "Competitive" is doing heavy lifting for a result that is 0-for-4 per campaign.

**What would address it.** Reconcile every ECE and violation figure to a single source; report per-campaign ECE for all six arms in the main text, not Appendix A; and either defend the pooled-vs-per-campaign discrepancy mechanistically or retire the calibration half of contribution 4 and rest the argument on the (real) data-efficiency point: no held-out calibration split, one fit instead of five.

### 4. The conformal risk-control section reports an operating point its own feasibility floor forbids

**Issue.** §4.10 derives α ≥ 1/(n+1) and states *"With the 14 calibration blocks available in a held-out campaign here, the tightest expressible target is α ≥ 0.067."* Table 5.7 nonetheless reports a full row at **α = 0.05** — alarm rate 86%, realised miss 0.018, "rotations respecting the bound 100%" — and its own footer reads "Feasibility floor with n = 14: α ≥ 0.067". §5.5 then discloses that *"only 25% of the rotations can express α = 0.05 at all"* (3 of 12), so the cross-campaign column at α = 0.05 averages three rotations and the exchangeable column presumably averages something else. Neither n is stated per row. A caption elsewhere refers to *"28 held-out calibration drives"*, a number that appears nowhere else in a dataset of 4 sessions and 57 blocks.

Substantively: in the exchangeable regime the certified threshold alarms on 47% of rows at α = 0.20 and 86% at α = 0.05. An alarm on nearly half of all seconds is not a warning system. In the regime an operator actually faces, the bound fails in 17% of rotations. The section's stated purpose — to report the regime where the assumption fails — is admirable, but the conclusion that follows is that the guarantee is currently vacuous at any deployable alarm rate, and the paper does not say that.

**Where.** §4.10 (936–940), §5.5 (1118–1136), Table 5.7.

**Why it matters.** Contribution 5 is one of two claims the paper says *"are not satisfied anywhere at all in the handover-prediction setting."* A guarantee reported below its own feasibility floor, on an undisclosed and varying n, cannot carry that weight.

**What would address it.** Delete or grey out infeasible rows; report n per row and per column; and state plainly in the abstract what the certified operating point costs (alarm rate), since the abstract currently promises *"a stated operating cost"* and never states one.

### 5. Reproducibility: the paper does not meet the standard it applies to others

**Issue.** Table 2.1 grades 22 prior models on releasing code (2/22) and data (1/22) and enters "Planned" for itself in both rows. A paper whose central contribution is a methodological audit it urges the field to adopt cannot ship with its own artifacts pending. Beyond that, the text cannot be implemented from as given:

- **Feature counts do not converge.** §2.10 Stage 3: "One hundred and fifty-two candidate features". §4.6: "three blocks and 112 columns in total". Table 4.3: 83 + 17 + 6 = **106**, with the total row reading 112. §4.7: "over the 107 features". Appendix B: "The 107 features retained" then lists 83 + 17 + 13 + 7 = **120**, and gives the signalling block 13 features where Table 4.3 gives it 10. Appendix B invokes a "degenerate-feature filter of Section 4.6"; §4.6 describes no such filter.
- **Seeds disagree.** §2.10 Stage 5: "repeated over five seeds". §4.9: "run over three seeds". Figure 5.19 caption: "the spread over three seeds".
- **Two incompatible reference lists.** The in-text list (lines 1321–1381) and the final REFERENCES (1577+) use different numbering from roughly [18] onward and different author lists for the same works (cf. [3] "H. Deng, C. Peng, A. Fida" vs "S. Deng, A. Peng, H. Fida"). Consequences in the body: §2.5 cites [18] for Candès *Conformalized survival analysis* while §2.6 cites [18] for Cohen et al.; §4.9 attributes the point-adjusted-metrics result to "[30]", which is LightGBM in the final list; §4.10 and contribution 5 attribute the conformal risk-control bound to "[21]", which is Hawkes (1971) in the final list. Most seriously, **[37], [38], [39], [40] and [41] — Raca, the Mendeley LTE dataset, the RL comparator, and both NUWiNS references — do not appear in the final reference list at all.** The entire external-evidence base of §5.1 and §5.7 is uncitable from the bibliography. Three references also carry unresolved editorial notes ("[Author list to be completed from the ACM record before submission]", "[Venue to be confirmed]", "[confirm the version DOI before submission]").
- No repository, no software or library versions, no hyperparameter search space, no LightGBM configuration.

**Where.** Table 2.1; §2.10, §4.6, §4.7, §4.9, Appendix B, Appendix C; both reference lists.

**What would address it.** Release the audit script, the four protocol implementations and the table-generation pipeline before review, as §7.3 itself recommends; pick one feature count and one reference list.

### 6. The "independent" external validation is not independent, and the transfer result is more consistent with an easier target set

**Issue.** §5.7 discloses — creditably — that the public dataset [38] was collected *"by a different group of people on a different route two years earlier, using the same operator, the same city and the same XCAL licence, in the same department of the same institution"*, and its author list includes the supervisor of this thesis. Objective O4 promises generalisation *"to an independently collected public dataset"*; what is delivered tests route and date within one operator, city, instrument and lab. That should be stated in the objective and the abstract, not only in §5.7.

More pointedly, the transfer result is read backwards. Table 5.9: `ours → public (no refit)` reaches AUROC 0.760, versus 0.711 for a model trained *on that dataset itself* and 0.730 for the authors' own in-domain result. A model that transfers *better than in-domain training in both directions of comparison* is, in my experience, almost always evidence that the target set is easier (fewer rows, 1,455; different prevalence, 6.3%; leave-one-file-out on files of unstated length), not that the formulation generalises. The paper reads it as *"the formulation and the feature construction transfer to another collection on this network"* and notes only that intervals overlap.

**Where.** §5.7 (1167–1179), Table 5.9, Objective O4 (476).

**What would address it.** A distinguishing test: match prevalence and row count by subsampling; report a scrambled-label control and a source-only-on-shuffled-features control; and report `public → public` and `ours → ours` on identically sized folds. If `ours → public` still beats `public → public` after that, the transfer claim earns its place.

### 7. Dataset accounting does not close, and one causal inference is contradicted by the table beneath it

**Issue.** Several counts do not reconcile:

- **957 vs 938.** Table 3.2 gives 15 + 8 + 20 + 14 = 57 blocks against durations of 45/24/60/42 minutes, i.e. 2700/1440/3600/2520 samples — every block is exactly full and none was dropped by QC. If no block was dropped, all 957 commands lie inside retained blocks, yet §3.4 says QC *"reduce[s] the raw handover count from 957 commands to 938 that fall inside a retained block."* Both cannot hold.
- **§3.4 declares a rule it then breaks.** *"The 957 figure is used only where the raw event stream is the appropriate object, which in this thesis occurs in exactly one place: the ungrouped variant of the ping-pong definition ladder in Section 5.9."* Ping-pong is §5.10, and Table 5.13 uses 957 for three of its four rows, and Table 5.14 uses 957 throughout.
- **The ping-pong range is quoted three ways.** §2.4: "24.5% to 41.3%" on 938. Table 5.13 and §5.10: 26.3% to 43.8% on 957. §7.1: "on one fixed set of 938 handovers moves from 26.3% to 41.3%".
- **Distance.** §3.6: "approximately 78 km of driving". Table 6.6: "Approximately 95 km". The speed×duration product gives ≈96 km, and Table A.2's false-alarms-per-km (5.45 vs 179.0/h ⇒ 32.8 km/h) is consistent with 95 km, so 78 km is wrong.
- **Table 3.1 does not sum.** Rows total 907 of 957 handovers (50 unattributed); the A3 rows sum to 648 while the final row asserts "651 A3 total". The headline 74.8% is 484/647.

Separately, §5.10 concludes *"It is not driven by speed: the highway campaign, at roughly twice the urban mean speed, returns at 32.2% against 25.0% on the urban campaigns"*, and §7.3 hardens this to *"having ruled out speed as the driver."* The table shows ping-pong **higher** on the fast campaign, and a two-proportion test on 177 vs 780 gives z ≈ 1.96, p ≈ 0.05 — a marginal effect in the direction opposite to the one claimed, on an effective sample of one campaign fully confounded with corridor, time of day and traffic. This is exactly the 0.01 < p < 0.05 territory the paper is elsewhere so careful about, and it is used to motivate a proposed intervention (varying the TTT).

**What would address it.** Reconcile the counts; correct §5.10 to "we cannot separate speed from corridor with one highway campaign"; withdraw "ruled out".

### 8. The strongest system in the neighbourhood is named and never compared against

**Issue.** §2.2 states that Prognos, inside Hassan et al. — [Vivisecting mobility management in 5G cellular networks, SIGCOMM 2022](https://dl.acm.org/doi/10.1145/3544216.3544217) ([PDF](https://feng-qian.github.io/paper/5g_mobility_sigcomm22.pdf)) — *"is the closest prior system to the one built here: it predicts handovers from XCAL-decoded RRC state on a live network and reports a lead-time gain of roughly 900 ms"*, and that §2.3 *"therefore positions this thesis against Prognos explicitly."* It does not. §2.3 excludes Prognos from the audit on a definitional technicality (*"a system component rather than a published prediction model with its own protocol"*) and never reports a comparison. The only baseline in Table 5.4 is the deployed A3 rule at 0.116. Prognos's ~900 ms lead-time gain is directly commensurable with this paper's median lead time of 0.47 s at the one-second horizon (Table A.2) and is not put beside it.

Similarly, Table 2.1's flagship row "Splits by drive, session or route: 0/22" is not disposed of for Appendix D row 9 — [Amirova et al., *Data-Driven and Machine Learning-Based Analysis of Handover Behavior and Network Stability in Mobile Networks*, Future Internet 18(6):290](https://www.mdpi.com/1999-5903/18/6/290) — which Appendix D itself records as REAL-MEASURED, **device-level hold-out**, with a PR curve and AUC CIs. §2.3's rebuttal of the five coarser-split papers ("the two most recent additions are regression tasks… the strongest protocol addresses next-day cell-level radio-link failure") covers rows 19, 22 and 13, not row 9. A device-level hold-out on measured radio is a mobility-unit split by most readings, and the 0/22 claim needs that row rebutted by name.

Finally, the alignment finding is framed as unprecedented (*"None of them states how the timestamp of a measurement row relates to the interval it summarises"*), but the underlying failure — a feature whose aggregation window extends past the prediction instant — is the canonical look-ahead/target-leakage bug, catalogued in the Kaufman et al. taxonomy the paper cites as [36] and never uses, and studied quantitatively in recent work such as [*Hidden Leaks in Time Series Forecasting*, arXiv:2512.06932](https://arxiv.org/abs/2512.06932). The contribution is "we found an instance of a known bug class in a widely used instrument's export, and measured what it is worth" — which is a good and useful contribution. Frame it that way rather than as a new phenomenon.

**What would address it.** A row for Prognos (or a reimplementation) in Table 5.4 scored on your rows; a named rebuttal of Appendix D row 9; a sentence attributing the bug class to the leakage literature.

## Minor concerns

- Table 5.2 is titled *"What the one-row lag costs, with everything else held fixed"*, but its Dwell-AUROC column (0.873 → 0.664) is not a lag effect: §4.6 and §5.8 both say 0.664 is dwell recomputed from **signalling timestamps**, i.e. a change of data source. Everything else is not held fixed in that column, and the 0.873 → 0.664 figure appears in the abstract and contribution 1 under the lag framing.
- Table numbering is broken. The List of Tables contains two disjoint blocks with conflicting captions for 5.5–5.12; the conformal table is called Table 5.7 at line 1116 and Table 5.5 at line 1118; Figure 5.8 is captioned once as burst stratification (1112) and referenced at 1104 as the coherence figure.
- "Table A.3" is described in the Appendix A text as covering only A.1 and A.2; A.3 appears without introduction.
- §1.5 caps resolvable events at 90.5%; Table A.2 gives 64.6% at 1 s and 95.3% at 5 s. 90.5% appears nowhere else.
- §4.6 says the history block is 6 features (Table 4.3) but Appendix B says 7 and adds serving dwell time and distinct-cell count.
- Figure 4.1 is introduced twice with identical text on consecutive lines (812–814).
- Equation numbering skips 4.10.
- Chapter 6 (Outcome-Based Education, ~110 lines, 6 tables) has no place in a Q1 journal submission and should be stripped, along with the BSc front matter, declaration and approval pages.
- `sig_s_since_a3` and `serving_sinr` are both given as AUROC 0.723 to three decimals in Table 5.10; report more precision or acknowledge the tie.
- §5.8 reports that adding the signalling block *reduces* one-second AUPRC (0.179 → 0.168). With 20 random-search trials per fold and nested selection, that is more likely a tuning-budget artefact than a real negative; say so.
- Event-level performance (34% detection at 179 false alarms/hour, median lead 0.47 s) is buried in Appendix Table A.2 and never appears in the abstract, §5.2, or §7.1. Given the paper's own criticism that *"none reports how early its warnings arrive or how many false alarms they generate per unit time"*, these belong in the main results.
- §7.1 promises "Six items follow from those limits" and lists seven.

## Belief update

Three things, none of them the headline.

**I updated moderately** on the claim that the row-aggregation rule, not the vendor or the network, controls serving-cell contamination in a 1 Hz export. The 93.2% vs 4.1% contrast on the *same* 4,712 NUWiNS handovers is not a test of the authors' hypothesis, but it is a clean demonstration that the downsampling convention alone moves the number from "almost always contaminated" to "almost never" — and that is a fact I will now check in my own pipelines. I also accept that some real contamination exists in the authors' own export; 75.9% vs an 11.7% background on isolated handovers is not explicable by chance.

**I updated substantially** on the A3 report-conversion correction. Table 5.12 is the cleanest table in the paper: every subtotal reconciles, the 8,136 → 2,361 episode grouping is stated mechanically (reportInterval 240 ms × reportAmount infinity, 3.4 reports/episode), and the per-profile breakdown (+1 dB profile declined on 2.3% of episodes) makes the result interpretable rather than merely reported. "A study using A3 reports as proxy labels must separate the mobility configuration from the rest" is a real finding I had not held.

**I did not update** on handover predictability. I cannot take a number from this paper: the primary one-second AUPRC is 0.179, 0.160 or 0.157 depending on which table I read, and the protocol-reordering claim is contradicted by the paper's own Table 5.4. The ping-pong definitional grid told me something I already believed (definitions dominate reported rates) with a range I cannot pin down, since it is quoted as 24.5–41.3%, 26.3–43.8% and 26.3–41.3% in three places.

The paper's own closing line — *"on drive-test data, the protocol and the timestamp semantics decide the result before the model does"* — is probably true. This draft does not yet demonstrate it.

## Verdict

**Major revision.** The central mechanism claim currently rests on a self-constructed downsampling contrast that could not have failed, a four-way-confounded control, and an n = 15 test whose selection does not reconcile with the reported interruption distribution — and the one distinguishing experiment, a native-rate re-export of the authors' own captures, is available to them and not performed; that, plus tables that report three different values for the headline number, is what stands between this and publication rather than any deficiency in the underlying measurement work. If the Table 5.4 / Table 5.5 contradiction cannot be reconciled on re-run, my recommendation becomes Reject.

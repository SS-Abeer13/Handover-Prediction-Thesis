SEED: `d9b3dd4459a3f88d82428e6ba8a0fae6`
LENS: 1 — Experimental design
STANCE: 2 — Steelman-then-press

---

# Review of *Leakage-Audited Multi-Horizon Handover Forecasting from LTE Drive-Test Signalling*

Reviewer: **charlie**

## Summary

The paper asks whether an imminent LTE handover command can be forecast from handset-observable measurements, at 0.5–5 s horizons, with coherent and calibrated probabilities and a distribution-free bound on the per-drive miss rate. Four drive-test campaigns on one commercial operator in Dhaka/Gazipur (4 continuous sessions, 10,260 one-hertz rows, 957 RRC-decoded handover commands) supply ground truth taken from `RRCConnectionReconfiguration` messages carrying `mobilityControlInfo` rather than vendor counters. The task is posed as discrete-time survival: a single learner estimates per-bin hazards and horizon probabilities follow from the product-limit identity, so ordering holds by construction. The headline empirical claim is negative-then-positive: an alignment audit shows that in 75.9% of handovers the export row stamped before the command already carries the post-handover serving cell (Table 5.1), and lagging every export feature one row collapses the one-second AUPRC from 0.600 to 0.179 (Table 5.2); after that correction LightGBM reaches AUPRC 0.179 at 1 s against a 6.8% floor (2.6×, AUROC 0.777) and 0.475 at 5 s under leave-one-campaign-out, against 0.116 for the deployed Event A3 rule scored as a predictor (Tables 5.3, 5.4). Secondary results are a four-rung splitting ladder (random rows inflate by 48%), a conformal risk-control frontier in and out of the exchangeable regime, and two corrected characterisations of the deployed network (30% of A3 *episodes* declined; 75% of A3-triggered handovers under a positive offset).

I want to say at the outset that the intellectual posture of this manuscript is unusually good. A paper whose central result is the destruction of its own best number, which prints the pre-audit figure beside the post-audit one, which reports that its favoured formulation *loses* to the isotonic composite on calibration, and which states that four units cannot support a significance claim, is doing something the audited literature demonstrably does not do. If the numbers held together, Section 5.1 alone would justify publication. They do not hold together, and that is what the rest of this review is about.

## Major concerns

---

**1. The experimental design supports almost none of the comparative claims built on it, and the uncertainty quantification uses a resampling unit the paper itself proves is invalid.**

*Issue.* Steelmanning first: the authors are right that a campaign is the only defensible independent unit here (Section 3.4), right that leave-one-campaign-out is therefore the correct primary protocol (Section 4.9), and admirably explicit that four paired observations cannot reach a sign-test p below 0.125 (Sections 3.6, 4.9, 5.4). Having established that, the paper proceeds to make a series of between-unit comparative claims anyway — that the protocol reorders the leaderboard (Section 5.3), that the hazard formulation calibrates competitively (Section 5.4), that the result transfers across corridor and speed regime (Section 5.6) — each of which is a contrast estimated from n = 4 confounded units. And the confounding is total: campaign is perfectly aliased with corridor, mean speed, date, duration, time of day, traffic and event density (Table 3.2: 24–60 min, 21.4–50.9 km/h, 5–159 re-establishments). The "held-out" highway campaign differs in *both* corridor and speed by construction (Section 3.2), so a drop in AUPRC there (0.132 against 0.196–0.233, Table 5.8) is uninterpretable — speed, corridor, cell density, and the near-absence of re-establishments (5 versus 64–159) all change together.

Worse, the primary interval estimate contradicts the paper's own central methodological finding. Table 5.3 reports 95% block-bootstrap CIs computed by resampling 180-second blocks *within* campaign. Section 5.3 exists precisely to demonstrate that 180-second blocks of one continuous session are **not** independent — that treating them as exchangeable inflates AUPRC by 13%. The paper therefore uses, as its resampling unit, the unit it has just proven is dependent. The hedge "conditional on these four sessions" addresses between-day variation but not within-session dependence, which is the thing that makes the interval too narrow. The same unit is then reused for the conformal calibration pool (Section 5.5), so the "exchangeable regime" is exchangeable by assertion on units shown to be non-exchangeable one section earlier.

*Where.* Sections 3.2, 3.4, 4.9; Tables 3.2, 5.3, 5.5, 5.8; Section 5.3.

*Why it matters.* Every comparative number in Chapter 5 inherits an interval of unknown but understated width. The AUPRC spread across learners in Table 5.4 (0.130–0.179 at 1 s) is entirely inside the stated CI for the primary model alone (0.159–0.204) — and that CI is itself too narrow. On the paper's own evidence, the manuscript cannot distinguish LightGBM from MLP from TCN, and cannot distinguish any of them from logistic regression with confidence. Yet LightGBM is designated "the primary model" and a leaderboard is printed to three decimals.

*What would address it.* (i) Replace or supplement the within-session block bootstrap with a hierarchical/cluster bootstrap whose top-level unit is the campaign, and state plainly that with four clusters the resulting intervals will be uninformative — that is the honest result. (ii) Report a stationary block bootstrap with the block length chosen from the measured autocorrelation of the per-row scores, not fixed at the 180 s bookkeeping length. (iii) Add a design table making the aliasing explicit (campaign × corridor × speed × date × duration), and demote every between-campaign contrast to "descriptive, n = 4, confounded". (iv) The correct fix is more sessions; Section 7.3's "eight to ten independent sessions" is right, and until it exists the comparative claims should be framed as hypotheses, not findings.

---

**2. The splitting-ladder experiment — the paper's most distinctive claim — is not a controlled experiment as executed, and Table 5.5 contradicts Tables 5.3, 5.4, 5.6 and A.1 on the same quantity.**

*Issue.* The design is right in principle: hold data, features, formulation, hyper-parameters and seeds fixed and vary only the splitting rule. Three things break it.

First, the numbers do not agree. The one-second leave-one-campaign-out AUPRC of LightGBM appears three times with three values: **0.179** (Tables 5.3, 5.4, A.1), **0.160** (Table 5.5), **0.157** (Table 5.6, "hazard" arm). Logistic regression is **0.130** in Tables 5.4/A.1 and **0.167** in Table 5.5. MLP is 0.173 versus 0.152; Transformer 0.152 versus 0.126. These are stated to be the same estimand under the same protocol. The claim in Section 5.3 that "under leave-one-campaign-out the leading learner at one second is logistic regression" is true *only* in Table 5.5 (0.167 > 0.160) and false in Tables 5.4 and A.1 (0.130 < 0.179). The entire "the protocol reorders the leaderboard" contribution (contribution 3, objective O2, Section 5.3, Chapter 7) rests on the one table that disagrees with the primary results table.

Second, the abstract's "48%" is computed against 0.160, not against the abstract's own headline 0.179. Against 0.179 the random-row inflation is +32%. The paper cannot report both numbers as properties of the same model.

Third, the A3 rule is offered as the control that "shows the effect is over-fitting rather than a difference in test-set difficulty" because it moves by +0% across the ladder. But a deterministic parameter-free rule scored on a pooled out-of-fold row set is *identical by construction* across all four protocols — every row appears in exactly one test fold under each rule, so the pooled row set is the same set. The control has zero power to detect a difference in test-set difficulty and cannot support the inference drawn from it.

*Where.* Section 5.3, Table 5.5; against Tables 5.3, 5.4, 5.6, A.1; abstract; contribution 3; Section 7.1.

*Why it matters.* This is the result with "the widest implication for the comparator literature" by the authors' own description, and it is the basis for indicting 22 prior papers. A reordering claim resting on a 0.007 AUPRC gap, inside a CI of width ≥0.045, in a table that contradicts the paper's primary table, cannot carry that weight.

*What would address it.* Reconcile the three tables and state which pipeline produced which — if Table 5.5 is a separate run (different seeds, different tuning, different row set), say so and re-run it against the primary configuration. Report Table 5.5 with per-seed and per-campaign dispersion and CIs. Replace the A3 "control" with a genuine one (e.g. a label-permutation null, or a fixed model scored under each protocol's *train* set held constant). If the ranking reversal does not survive, say so — the level-inflation finding survives on its own and is still worth reporting.

---

**3. The coherence numbers in the prose contradict the coherence table, and the contradicted number is the one that appears in the abstract, the contributions list and the conclusions.**

*Issue.* Table 5.6 reports the independent-classifier arm violating horizon ordering on **29.0%** of rows, with mean violation 0.020 and largest 0.377. The prose in the same section states **40.2%**, mean 0.025, maximum 0.521. The 40.2% figure also appears in the abstract, contribution 4, Section 2.5, Section 4.2 and Section 7.1. It appears in no table. Compounding this, Section 5.4 states that isotonic calibration "makes coherence worse (violations rise from 40.2% to 33.4%)" — 40.2 → 33.4 is a *fall*. The sentence is only arithmetically coherent against the table's 29.0%, which is the number the same sentence has just contradicted.

*Where.* Table 5.6; Section 5.4 prose; abstract; Section 1.6 (contribution 4); Sections 2.5, 4.2; Section 7.1.

*Why it matters.* The violation rate is the sole quantitative justification for preferring the hazard formulation over the obvious baseline, and it is quoted in the abstract. A reader cannot tell whether the defect being repaired affects 29% or 40% of rows, and one of the two numbers is wrong.

*What would address it.* Fix the number everywhere from a single regenerated table (Appendix C claims tables are regenerated rather than transcribed — this pair demonstrates that the claim does not currently hold), and re-check the direction words in every sentence that compares arms.

---

**4. Three mutually inconsistent values are reported for the primary model's one-second ECE, and the per-campaign evidence points the opposite way from the pooled claim.**

*Issue.* The one-second expected calibration error of the primary model is **0.012** (Table 5.3, abstract), **0.036** (Table 5.6, Section 5.4 prose, Section 7.1) and **0.024** (Section 5.4, the paragraph explaining what an ECE "means operationally"). The choice is load-bearing: the comparison against the isotonic-plus-PAV composite (0.016) is a loss at 0.036, a near-tie at 0.024, and a win at 0.012. The manuscript's carefully argued concession — "the hazard formulation does not beat it on calibration" — depends on which of its own three numbers is correct.

Separately, Section 5.4 states that "the hazard arm has the lower calibration error on **0 of the four** held-out campaigns at one second," i.e. it is worse on every single unit. The pooled ECE (0.036 vs 0.047) says it is better. A pooled statistic that reverses a 0-of-4 per-unit direction is a Simpson-type reversal produced by aggregating predictions across folds with offsetting biases; this is also visible in Table 5.8, where the pooled ECE (0.012) is *lower than three of the four* per-campaign values (0.018, 0.021, 0.012, 0.033). Under the paper's own doctrine — that the per-campaign spread is "the honest measure" — the honest reading is that the hazard arm calibrates worse than the control on every unit tested, and the manuscript instead reports the pooled number in the abstract.

*Where.* Tables 5.3, 5.6, 5.8; Section 5.4; abstract; Section 7.1.

*Why it matters.* Calibration is objective O3 and the property the paper says none of the 22 audited models reports. Getting it internally inconsistent, and then quoting the aggregate that reverses the per-unit direction, undermines the paper's strongest methodological claim about itself.

*What would address it.* Report one ECE per (arm, horizon, held-out campaign) in the main text, with the pooled value only as a footnote; state the fold-averaged ECE alongside the pooled one; and rewrite the comparison sentence to match the 0-of-4 count. Also report the bin counts — ECE over 15 equal-mass bins on a fold with 1,131 rows and 8% prevalence is estimated from ~9 positives per bin and is very noisy.

---

**5. The alignment audit — the paper's best contribution — is supported by a null that is not chance, a control dataset that cannot test the hypothesis, and a "replication" the authors generated themselves.**

*Issue.* Steelmanned: the mechanism in Equation (5.1) is elegant, the falsification test is the right instinct, and I would want this audit run on every drive-test prediction paper. But three legs of the evidence are weaker than the text says.

*(a) The null.* The audit declares 75.9% contaminated against a "background rate given by rows three seconds earlier (12.1%)". Row t−3 is not chance. The paper's own Section 5.10 reports a ping-pong rate of 26.3–43.8%: in a substantial fraction of handovers the *target* cell is a cell that was serving shortly before, so "row t−3 carries the target cell" has an elevated probability for reasons that have nothing to do with aggregation. The correct null is a permutation over matched non-handover rows, or a PCI-frequency-matched baseline, not an adjacent lag.

*(b) The control.* The Raca et al. traces are presented as proving the defect is absent in a sampled log. But Table A.3 states the event clock there is "serving-cell identifier changes only" and that isolated handovers are "not separable (no signalling clock)". If the event is *defined* as the row at which the serving-cell identifier changes, then asking whether row t already shows the new cell is close to circular, and the reported 29.4% is not "none" — it is 2.5× the paper's own claimed background. Section 5.1 nonetheless says "the account predicts no contamination, and there is none."

*(c) The "replication".* The NUWiNS result is described in the abstract and in contribution 2 as holding "again across instruments," on "4,712 handovers from 3 operators." But Table A.3 states the row semantics there were "set by us: last, or first, sample of the second." Taking the last 10 Hz sample of each second, given a serving-cell update delay the paper estimates at ~60 ms, mechanically places the post-event state in ~94% of rows. This is a demonstration that end-of-second downsampling produces the artefact — it is not independent evidence that XCAL's native 1 Hz export uses end-of-second aggregation, which is the claim that matters for the authors' own data and which remains inferred rather than observed (Section 7.3 concedes this).

*(d) Sample size and resolution.* The falsification test rests on **15** boundary-crossing handovers; a 0/15 result has an exact upper 95% bound of 0.22, which should be stated. And the 15 is hard to reconcile with the reported interruption distribution (65% of commands non-zero, p90 = 99 ms, max 105 ms): under δ ~ U(0,1) that implies of order 2–4% of 938 commands crossing the boundary, i.e. 20–40, not 15. Finally, the ~60 ms update-delay estimate is said to be "consistent with the native ten-hertz view … where the target is already serving at τ + 100 ms in 100% of handovers" — a 10 Hz grid is consistent with *any* delay below 100 ms and has no power to validate 60 ms.

*Where.* Section 5.1; Tables 5.1, A.3; Figure 5.1(c)–(f); abstract; contribution 2.

*Why it matters.* This is the finding the paper says it most wants the field to adopt, and the one the acknowledgements and Chapter 7 foreground. It deserves an inferential standard the current text does not meet, and it is the claim most likely to be attacked by exactly the measurement community whose corpora are being reanalysed — a community that already runs formal replications of this corpus family (see [*Replication: Performance of Cellular Networks on the Wheels*, IMC 2025](https://dl.acm.org/doi/10.1145/3730567.3764486), a replication of the Ghoshal et al. "on the wheels" drive-test study from which reference [41] is drawn). Positioning Section 5.1 against that replication practice would strengthen it considerably; presenting a self-imposed downsampling rule as cross-instrument replication invites the opposite reception.

*What would address it.* Report a proper null (permutation or frequency-matched) for Table 5.1; drop or heavily qualify the Raca "control" and state that its event clock cannot separate the hypotheses; restate the NUWiNS experiment as *"a controlled demonstration that the aggregation rule alone produces the artefact"* rather than as cross-instrument replication; give the exact CI on 0/15; reconcile the 15 against the interruption distribution; and either obtain the native-rate re-export (Section 7.3's own top recommendation) or state that the write rule for the authors' own tool remains inferred.

---

**6. The event-level operating characteristics do not support the operational claims the paper makes for the warning, and the paper's own cited standards analysis says so.**

*Issue.* Section 1.2 asserts "a warning one second ahead of a handover command is sufficient time for the network to complete target-cell preparation," and Section 6.6 builds a societal-impact argument on it. Table A.2 gives the measured operating point: at 1 s, detection rate **34.0%**, false alarms **179.0 per hour** (5.45/km), **median lead time 0.47 s**. On a stream where handovers occur every 11 s, that is a false alarm roughly every 20 seconds for a third of events detected half a second early. Section 2.8 cites Deb et al. [29] for precisely the proposition that a model identifying the target "two hundred milliseconds before the event buys nothing, because the preparation message must be sent, acknowledged and stored." A 0.47 s median lead is in the same regime. At 5 s the lead improves to 3.31 s but detection is still 42.5% at 69.6 false alarms/hour.

The table is also mislabelled between the List of Tables ("at the certified operating point of Section 5.5") and its own caption ("at the 5% false-positive operating point") — these are different operating points, and the conformal frontier in Table 5.7 shows alarm rates of 36–86%, nowhere near 5% FPR.

*Where.* Section 1.2, Section 6.6, Table A.2, Figure 5.2, Table 5.7, List of Tables.

*Why it matters.* The paper's stated framing is that measured cost should replace asserted benefit — that is the indictment levelled at the comparator literature ("none reports how early its warnings arrive or how many false alarms they generate"). The manuscript reports those numbers, to its credit, and then does not let them revise the motivating claim.

*What would address it.* Rewrite Sections 1.2 and 6.6 against Table A.2: state that at every operating point measured, the warning is not yet operationally usable, and that the contribution is the measurement framework rather than a deployable predictor. Reconcile the two operating-point captions. Report the full lead-time distribution (not just the median) and the detection/false-alarm frontier, since the single 5% point is arbitrary.

---

**7. The conformal risk-control section evaluates the wrong estimand, defines its risk in a form that is not admissible under the cited bound, and reports a row below its own stated feasibility floor.**

*Issue.* Conformal risk control [20] guarantees **E[R(λ̂)] ≤ α** for a fresh exchangeable unit — a statement about an expectation. Table 5.7 evaluates it by the column "rotations respecting the bound" (100%, 92%, 83%, 83%, 67%), i.e. the *frequency with which a realisation falls below α*. That is a coverage statement about a different object; a procedure controlling the mean can fail on many individual rotations and still satisfy its guarantee exactly. The "83% of rotations" number, which Chapter 7 elevates to "the honest measure of what exchangeability across days is worth here," therefore does not measure what it is said to measure.

The risk itself is printed as `R_d(λ) = { t ∈ d : y_t = 1 ∧ p̂_t < λ }` — a set (or a count), not a loss bounded in [0,1], while the procedure is instantiated with B = 1. As written this is not the bounded monotone risk the bound requires; presumably a normalisation by the positives in d is intended, but it must appear. Relatedly, Equation (4.9) takes an infimum over λ while λ is described as "ordered by decreasing strictness" and the miss rate is non-decreasing in a probability threshold — the direction of monotonicity needs to be stated explicitly, not left for the reader to reconstruct.

The α = 0.05 row is reported (86% alarm rate, realised 0.018, 100% of rotations respecting) despite Section 4.10's own feasibility floor α ≥ 1/(n+1) = 0.067 at n = 14, and despite Section 5.5's statement that "only 25% of the rotations can express α = 0.05 at all." An infeasible target should not produce a table row without a marker.

Finally, the unit bookkeeping is unrecoverable: Section 4.10 and Table 5.7 use 180-second blocks (14 in a held-out campaign, 57 total), but the text at the head of the section says the frontier was "obtained … on **28 held-out calibration drives**." The paper insists elsewhere (Section 3.4) that blocks are emphatically *not* drives, and 28 matches neither 14 nor 57. The 12 campaign rotations are also not independent (each campaign appears in six pairs), so percentages over them have no clean interpretation.

*Where.* Section 4.10, Equations (4.9)/(4.11) (Equation 4.10 is missing entirely), Section 5.5 (whose heading is absent from the body), Table 5.7.

*Why it matters.* The distribution-free guarantee is contribution 5 and objective O3, and it is the element the paper claims is absent from the whole comparator literature. As presented it cannot be checked or reproduced.

*What would address it.* State the risk as a normalised, bounded, monotone loss and prove monotonicity in λ; evaluate the guarantee as the *mean* realised risk across rotations with an interval, and report the per-rotation frequency only as a secondary diagnostic with its correct interpretation; mark infeasible α rows; reconcile 14/28/57 and define "drive" once; restore the missing section heading and equation number.

---

**8. The protocol audit that justifies the novelty claim is not reproducible from Appendix D, counts unverified entries as negatives, and excludes the single closest comparator by a definitional move.**

*Issue.* Table 2.1 reports crisp counts out of 22, and Appendix D is offered so "each row of Table 2.1 can be checked." It does not check out. Counting the "Split protocol" column of Table D.1, I find at most 8–9 entries that state a protocol (rows 4, 6, 9, 10, 12, 13, 19, 22, arguably 5), against the claimed **12/22**. Three of the 22 (row 15, a dataset paper with "no models trained"; row 20, an RL paper; row 21, "no learning") train no predictive model at all, yet inflate the denominator of a table about *prediction models*. Several cells read "NOT VERIFIED", "UNVERIFIED", or "nan" (rows 7, 11, 15, 20, 21) — these are counted as failures in Table 2.1's "Papers satisfying it" column, which converts unverifiability into evidence of absence.

More importantly, Prognos — which the paper itself calls "the closest prior system to the one built here," on live-network XCAL-decoded RRC, reporting a ~900 ms lead-time gain ([Hassan et al., SIGCOMM 2022](https://feng-qian.github.io/paper/5g_mobility_sigcomm22.pdf)) — is excluded from the audited set on the grounds that it is "a system component rather than a published prediction model with its own protocol." That exclusion removes the one comparator that would constrain the paper's numbers, and no reimplementation or numeric comparison to it is attempted anywhere. Nor is the promised comparator from Section 2.10.1 delivered: "Chapter 5 reports a reimplementation of that comparator scored as a predictor, for completeness" — no such reimplementation appears in Chapter 5, Table 5.4, or Appendix A.

The screen also appears not to be exhaustive on its own terms: a 2026 predictive-handover system such as [*PreHO: Predictive Handover for LEO Satellite Networks*](https://arxiv.org/html/2603.07987) is neither in Appendix D nor discussed, and the survival grounding cites only a review [16] and one clinical application [17], omitting the canonical methodological references for the exact construction used here (e.g. [Kvamme & Borgan, *Continuous and discrete-time survival prediction with neural networks*, Lifetime Data Analysis](https://link.springer.com/article/10.1007/s10985-021-09532-6) and the standard [discrete-time modelling tutorial](https://link.springer.com/article/10.1186/s12874-022-01679-6)). Since the paper's positioning explicitly depends on locating the formulation correctly ("what is new here is narrower"), the omission matters.

*Where.* Section 2.3, Table 2.1, Appendix D (Table D.1), Section 2.10.1, Sections 1.2 and 1.3 ("None of these five requirements is satisfied jointly anywhere in the audited literature").

*Why it matters.* Every "none of the 22" statement — and there are many, including in the abstract's framing and in Chapter 6's attribute tables — is only as good as this audit. As tabulated, the audit's own counts cannot be reproduced from its own appendix.

*What would address it.* Recount Table 2.1 from Table D.1 and publish the coding sheet with per-paper evidence (quotation or page reference); introduce an explicit "unverifiable" category rather than folding it into "no"; restrict the denominator to papers that actually fit a predictive model; add Prognos to the audit or drop the "closest prior system" framing; and either deliver the promised comparator reimplementation or remove the sentence promising it.

---

**9. Reproducibility: the feature inventory is irreconcilable across four statements, the model descriptions contradict themselves, and the manuscript carries two incompatible reference lists.**

*Issue.* The feature set is described as **152** candidate features (Section 2.10, Stage 3), **112** columns in three blocks (Section 4.6), a Table 4.3 whose blocks sum to 83 + 17 + 6 = **106** under a row labelled "Main feature set | 112", **107** features for logistic regression (Section 4.7) and for the retained set (Appendix B), and an Appendix B inventory that itemises 83 + 17 + 13 + 7 = **120**. Table 4.3 gives the signalling block 10 features and the history block 6; Appendix B gives 13 and 7.

Section 4.7 states in one paragraph that "the sequence models consume windows of the ten most recent feature vectors — the same vectors, lagged the same way — so the only thing that varies between arms is the learner," and two paragraphs later that they consume "a window of raw per-second measurements rather than the engineered summary features." These cannot both be true, and the whole point of that subsection is that the earlier draft's confound was removed.

The manuscript contains two reference lists — one interleaved in the body (lines around the Chapter 5/6 boundary) and one under REFERENCES — with different numbering *and different author lists* for the same works ([3] Deng et al. vs "S. Deng, A. Peng, H. Fida"; [15] Amirova; [18] Candès vs Cohen; [33] Shafi vs Guo). In-text citations are correspondingly unstable: Section 4.9 cites "Wagner et al. [30]" for event-detection metrics while [30] is LightGBM in the final list and Wagner is [28]; Section 4.10 cites conformal risk control as [20] and Section 4.11/contribution 5 cite the same result as [21], which is Hawkes. Three references carry unresolved editorial notes ("[Author list to be completed from the ACM record before submission]", "[Venue to be confirmed]", "[confirm the version DOI before submission]").

Several promised sections are absent: 5.12 (Discussion against the objectives) and 5.13 (Threats to validity) are in the Table of Contents and cross-referenced from Section 5.10, but do not appear; Sections 6.1–6.4 and the heading of 7.3 are likewise missing; Section 5.5's heading is missing though its content is present under 5.4. Table numbers 5.5 through 5.14 are each used for two different tables across the two List-of-Tables blocks and the body.

*Where.* Sections 2.10, 4.6, 4.7; Tables 4.3, D.1; Appendix B; both reference lists; Table of Contents versus body.

*Why it matters.* The paper positions reproducibility as a contribution ("the audit is three lines of code"; Table 2.1 lists code/data release as "Planned"). A manuscript that criticises 20 of 22 papers for not releasing code, while itself listing release as "planned" and reporting four different feature counts, cannot make that argument.

*What would address it.* One regenerated feature manifest (count, names, block, source, lag) as a machine-readable appendix; a single reference list; a citation-integrity pass; the missing sections restored; unique table numbers; and an actual artefact (repository or DOI) with the seeds, hyper-parameter search spaces, library versions and the audit script, before acceptance rather than after.

---

**10. Conflict of interest around the "independent" external validation is disclosed partially and framed misleadingly, and the arithmetic of the two "corrected network characterisations" does not close.**

*Issue (a) — COI.* Section 5.7 states, to the authors' credit, that the public dataset [38] "was produced in the same department as this work." What it does not state is that the thesis supervisor, Dr. M. T. Kawser, is a **co-author of that dataset** ([38]) and of the comparator study [39] — a fact visible only by comparing the approval page with the reference list. Meanwhile the Acknowledgements thank "the authors of the publicly released LTE drive-test dataset used for the independent check" as though they were an unrelated third party, and Section 6.6 lists the same-department provenance as an ethical matter handled. Table 5.9 is then headed "Transfer between our campaigns and an independently collected public dataset."

*Issue (b) — arithmetic of contribution 6.* Table 3.1 does not sum. The listed A3 profiles total 648 handovers, while the same table's summary row states "651 A3 total"; all listed rows (A3 plus A4/A5/A6/A1/none) total 907 of 957 commands and 94.7% of the share column, leaving ~50 handovers and 5.3% unaccounted for and unexplained. The 75% positive-offset claim (472 + 12 = 484 of 648 = 74.7%) is therefore computed on a denominator the table does not reconcile.

Worse, Table 5.12 and Table 3.1 are mutually inconsistent. Table 5.12 reports **1,647** A3 trigger episodes "followed by a command within 2 s" out of 2,361 — but there are only **957** commands in the entire corpus, and Table 3.1 attributes only **472** commands to the +1 dB profile against Table 5.12's **717** converted episodes for that same profile. Multiple episodes must be mapping to the same command (plausible, with several measIds triggering near-simultaneously), but then the "30% declined" rate has a numerator that double-counts commands and a denominator that is not a partition, and it is not comparable to the per-command attribution in Table 3.1. Neither the abstract's "30% of A3 episodes are not followed by a handover within two seconds" nor contribution 6 acknowledges this.

*Where.* Approval page; Acknowledgements; Section 5.7; Section 6.6; references [38], [39]; Tables 3.1, 5.12; contribution 6; abstract; Section 7.1.

*Why it matters.* (a) For a Q1 journal the supervisory relationship to the "independent" validation corpus is a declarable conflict, and the word "independent" in Table 5.9's heading and in the abstract overstates what was disclosed. (b) Contribution 6 is one of six headline contributions and both of its numbers currently rest on tables that do not balance.

*What would address it.* An explicit COI statement naming the shared authorship, and softening "independent collection" to "a separate collection by an overlapping group." For (b): make Table 3.1 sum, account for the ~50 missing commands, and either report the episode-conversion rate on a command-disjoint basis or state clearly that episodes are many-to-one onto commands and give both figures.

---

**11. The ping-pong ladder is reported three different ways, and the causal lever recommended for it is contradicted by the paper's own stratification; the Hawkes analysis interprets a fit its own diagnostic rejects.**

*Issue.* The definitional-instability finding is reported as: 938 handovers moving from **24.5% to 41.3%** (Section 2.4); 957 handovers moving from **26.3% to 43.8%**, with a nine-cell grid spanning **21.0–43.8%** (Section 5.10, Table 5.13); and 938 handovers moving from **26.3% to 41.3%** (Section 7.1). No table contains 24.5% or 41.3%. Section 3.4 further states that the 957 count is used "in exactly one place: the ungrouped variant of the ping-pong definition ladder in Section 5.9" — but Section 5.9 is the report-conversion section, and 957 is used in three of four rows of Table 5.13 and throughout Table 5.14. A paper whose thesis is that authors must state their definitional choices exactly should not print three versions of its own ladder.

Section 5.10 then asserts "It is not driven by speed" and Section 7.3 says the time-to-trigger is the lever "having ruled out speed as the driver." The table immediately above reports ping-pong at **32.2%** on the highway campaign versus **25.0%** urban — higher at double the speed. The inference is drawn from the intra/inter-frequency contrast being larger (27.1% vs 7.2%), which is a statement about relative magnitude, not a ruling-out; and the inter-frequency gap is partly mechanical, since a return across carriers requires a second inter-frequency decision. Regime is also fully confounded with campaign (concern 1), so the 32.2/25.0 contrast is a one-unit comparison.

The Hawkes analysis reports a branching ratio of 0.653 and interprets it ("each handover command is followed on average by roughly 0.7 further commands attributable to it") while simultaneously reporting that the Ogata residual test **rejects** the fitted exponential kernel. Under a rejected kernel, α/β is a functional of a misspecified model and the attribution statement does not follow. No test statistic, p-value or sample size is given for the rejection, and no CI is given for the pooled branching ratio. Pooling four campaigns with different event rates also inflates apparent self-excitation through superposition, and a 26–44% ping-pong rate is an obvious non-Hawkes generator of the clustering.

*Where.* Sections 2.4, 3.4, 5.10, 7.1, 7.3; Tables 5.13, 5.14; Figures 5.15–5.18.

*Why it matters.* The ping-pong result is offered as a methodological correction to the literature; the Hawkes result is offered as convergent evidence for the burst structure and motivates the quiet/burst stratification of Section 5.8.

*What would address it.* One ladder, one denominator, one set of numbers, with the full nine-cell grid in a table rather than only in a figure. Withdraw "not driven by speed" or support it with a within-campaign speed stratification. Either fit a kernel that passes the residual test before quoting a branching ratio, or report the branching ratio explicitly as a descriptive summary of a rejected fit and delete the causal-attribution sentence; report the KS statistic, its p-value and the held-out drives it was computed on; fit per campaign rather than pooled.

## Minor concerns

- **Total driving distance is inconsistent**: Section 3.6 says "approximately 78 km," Table 6.6 says "approximately 95 km," and Table 3.2's durations and mean speeds imply ~96 km. The false-alarms-per-km column of Table A.2 implies ~33 km/h, consistent with ~96 km, so 78 km appears to be the error.
- Table 4.3's "Main feature set | 112" row does not equal the sum of the blocks above it (106).
- Suspicious exact ties invite a check of the regeneration pipeline: AUROC = 0.777 at both 0.5 s and 1 s (Table 5.3); MLP and TCN both at exactly 0.755 (Table 5.4); `sig_s_since_a3` and `serving_sinr` both at exactly 0.723 (Table 5.10).
- "Figure 4.1 illustrates the two formulations side by side." appears twice in succession (Section 4.3), the second time in place of the figure caption.
- An orphan sentence, "Instrument ceiling. The one-hertz export caps event-level detection at 64.6% at one second," sits inside the interleaved reference list with no surrounding section.
- Table A.2's "Events" column varies from 934 to 937 across horizons with no explanation; if rows are dropped for want of follow-up window, say which and why the count changes by horizon.
- Section 7.3 announces "Six items follow from those limits" and then lists seven; the third item is introduced as "the first item because it is the only one that addresses the identification problem."
- Cross-references to Sections 5.9 and 5.10 are repeatedly swapped (Section 3.5 cites 5.9 for the 75% offset result, which is in 3.5; Section 4.11 cites "the ping-pong behaviour of Section 5.9," which is in 5.10).
- Section 4.4 states "no row is censored inside the horizon grid," while Section 5.8 reports "censoring the 93 rows whose next event is a re-establishment" as a competing-risk sensitivity — and Section 3.6 counts 341 re-establishments. The relationship between 341 events and 93 rows is never given.
- The two-second post-handover blank is a label-defined row exclusion that removes the densest burst rows and changes the prevalence; it needs a sensitivity analysis, since it interacts directly with the quiet/burst stratification of Table 5.11 and with the 64.6% resolvability ceiling.
- The deployment vantage point is never fixed. The signalling block is excluded from the main arm because "a handset-side predictor may not have them," but A3 report transmission times are handset-side, the history block already requires decoded RRC, and the motivating use case (target-cell preparation) is network-side. The exclusion also removes the strongest single feature in the paper (`sig_s_since_a3`, AUROC 0.723).
- In Section 5.7, the transferred model (AUROC 0.760) outscores both in-domain models (0.711, 0.730). A transfer result exceeding in-domain performance usually indicates a difference in dataset difficulty or size (1,455 rows, ~92 positives), not transfer quality, and should be read as such rather than as evidence the formulation transfers.
- Chapter 6 (outcome-based education, course/program outcome mapping, BDT budget) is a degree-programme requirement and has no place in a journal submission; it should be removed for the Q1 version.
- The Event A3 rule is scored with AUPRC and AUROC, which requires a ranking, but the rule as specified in Equation (2.1) is a boolean. State exactly what continuous score was used (margin? hold time?), because the rule is the paper's most important baseline.
- "Leave-one-capture-out" (Table 5.9) is used without definition alongside "leave-one-campaign-out" and "leave-one-file-out."
- Section 4.7's "equal tuning budget by construction" — twenty random-search trials per outer fold — equalises trial count, not search difficulty; twenty trials is a thin budget for a Transformer and a generous one for logistic regression, so the learner comparison is confounded with search-space dimensionality.
- References [6], [15] and [38] carry unresolved editorial placeholders that must not survive to submission.

## Verdict

**Major revision.** The alignment audit, the splitting ladder and the refusal to launder a 0.600 AUPRC are genuine contributions and the paper's honesty about its own reversals is better than most of what it criticises — but the primary model's one-second AUPRC appears as three different numbers, its ECE as three, and its coherence baseline as two, and several headline claims (the leaderboard reversal, the calibration comparison, the 30% conversion rate, the operational value of the warning) are contradicted by the manuscript's own tables; none of this is fatal to the underlying work, but all of it must be reconciled, with the uncertainty re-estimated at the campaign level, before the paper can be assessed on its merits.

**Sources consulted**

- [Vivisecting Mobility Management in 5G Cellular Networks (Hassan et al., ACM SIGCOMM 2022)](https://feng-qian.github.io/paper/5g_mobility_sigcomm22.pdf)
- [Replication: Performance of Cellular Networks on the Wheels (ACM IMC 2025)](https://dl.acm.org/doi/10.1145/3730567.3764486)
- [Continuous and discrete-time survival prediction with neural networks (Lifetime Data Analysis)](https://link.springer.com/article/10.1007/s10985-021-09532-6)
- [Survival prediction models: an introduction to discrete-time modeling (BMC Medical Research Methodology)](https://link.springer.com/article/10.1186/s12874-022-01679-6)
- [PreHO: Predictive Handover for LEO Satellite Networks (arXiv)](https://arxiv.org/html/2603.07987)

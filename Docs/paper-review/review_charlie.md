SEED: f168bc5907ba8dfdd8c2d7c115d37af0
AXIS: 1 — Cherry-picked examples (0xf1 = 241; 241 mod 8 = 1)
STANCE: 2 — Steelman-then-press (0x68 = 104; 104 mod 3 = 2)

# Review (charlie): "Conformalized Discrete-Time Hazard Modeling for Multi-Horizon Handover Forecasting in Cellular Networks"

## Summary

The thesis asks whether the next LTE handover command can be forecast 0.5–5 s ahead from UE-side measurements. It wants coherent multi-horizon probabilities, calibration and a distribution-free miss-rate bound. Data are 2.9 h of 1 Hz XCAL drive-test logs from one UE on one Dhaka operator. They comprise 57 "drives", 10,260 samples and 938 RRC-decoded handovers.

A configuration-timeline replay resolves measId bindings. The task is cast as discrete-time survival: one LightGBM fitted on (sample × bin) rows, with horizon probabilities recovered by the product-limit identity. Seven learners are compared under 4-fold grouped-by-drive CV × 5 seeds. Conformal risk control (CRC) is applied with the drive as the exchangeable unit.

- **Headline:** at 1 s, AUROC 0.933 and AUPRC 0.784 (11.7× lift), ECE 0.024, against AUROC 0.653 for the deployed A3 rule scored as a predictor.
- **Coherence:** 0 % horizon-ordering violations vs 43.6 % for independent classifiers.
- **Protocol:** random-row splitting "inflates" a GRU by 74 % and LR by 4 %.
- **Generalisation:** leave-one-campaign-out AUROC 0.909–0.949; external-dataset AUROC 0.752 vs 0.745 in-domain.
- **Mechanism:** dwell time alone gives AUROC 0.874; the A3 gap gives 0.566.

The paper is unusually self-aware about protocol. The signalling-grounded labels, grouped splits and reported negative results are real assets. But the evidence is much thinner, more selectively presented and more internally inconsistent than the confident prose implies.

## Major concerns

### 1. [Evidence — AXIS: cherry-picking] The thesis is reported through its single best slice: best horizon, best metric per experiment, extreme examples

**Issue.** Steelman: the authors do publish a five-horizon table (Table 5.1, Table A.1) and say calibration collapses beyond 2 s. That is more than most handover papers do.

Press: every other experiment is shown only at 1 s, which is the best of five horizons by a wide margin. This covers model comparison (Table 5.2), split inflation (Table 5.3), LOCO (Table 5.6), external validation (Table 5.7), single-feature AUROC (Table 5.8), ablation (Fig. 5.20) and calibration pairing (Fig. 5.6).

- Table 5.1 shows AUROC falling 0.933 → 0.854 → 0.816 → 0.783. Lift falls 11.7× → 2.3× and ECE rises to 0.141.
- Yet §2.8 argues, citing the conditional-handover analysis, that the operationally useful horizons are 2–5 s. The paper headlines the horizon it admits is least useful for CHO. It hides how LOCO, transfer and the protocol result behave where it matters.

Selection recurs at every level:

- **Metric switching.** External validation reports only AUROC, with no AUPRC, prevalence, ECE or CI. §2.3 mocks a railway study for reporting only AUROC, and Table 2.1 promises AUPRC "with floor and lift". The external set is also described as "curated" (Fig. 5.11 caption) with no curation rule given.
- **Extremes as headline.** The abstract quotes the 74 % and 4 % endpoints of Table 5.3. The random-split ranking itself is never shown: "rises from sixth place to a position it does not hold" (§5.3).
- **Selected strata.** Table 5.11 gives intra/inter-carrier, the dominant profile and the highway. It omits the three urban campaigns and the non-dominant profiles. "Not driven by speed" rests on one campaign-level number (31.1 %) with no interval and no within-campaign speed stratification.
- **Selected features.** Table 5.8 is captioned "the three most informative inputs", yet its third row is described in the text as "close to the least informative". That is 3 of 107, hand-picked to make a rhetorical contrast.
- **Selected operating points.** Table 5.5 has two α rows, and only one has a realised miss rate. Yet §5.5 claims "every operating point lies on or below the diagonal".
- **Promised but absent.** Table 2.1 says this work reports lead time and false alarms "per hour… and per kilometre". No such number appears in any table or in the text, nor does a lead-time distribution.

**Where.** Abstract; §5.1–5.8; Tables 5.2–5.8, 5.11; Fig. 5.11 caption; Table 2.1.

**Why it matters.** A reader cannot tell whether protocol, transfer and mechanism claims hold at 2–5 s or only at the grid-adjacent horizon where the task is nearly trivial (see concern 2).

**What would address it.**
- Report every experiment at all five horizons, with drive-level CIs.
- Give full tables for random-split rankings, all single-feature AUROCs, all strata and the entire CRC frontier with realised risk.
- Report external validation on AUPRC, lift and ECE with the curation rule stated.
- Give numerical false alarms per hour and lead-time quantiles.

### 2. [Evidence — alternative explanation] The model may mostly be predicting aftershocks, plus a possible 1 Hz alignment leak

**Issue.** Steelman: dwell time is legitimately UE-observable, and the authors report its strength (AUROC 0.874 alone) rather than hiding it.

Press: that number is the most important result in the thesis, and it undercuts the headline.

- Handovers here are violently bursty: median gap 3.5 s against a mean of 11 s, ping-pong 24.5 %, Hawkes branching ratio 0.605.
- "A handover just happened, so another will follow" is therefore a near-sufficient predictor. One counter gets 0.874; 107 features, a hazard model and conformal machinery add 0.06.
- Predicting the second leg of a ping-pong is operationally very different from warning about the first handover after a long dwell. Only 44.7 % of events are detected at 1 s, and no analysis says which ones.

Separately, the 1 s spike is suspicious: AUPRC 0.416 (0.5 s) → 0.784 (1 s) → 0.627 (2 s). The paper never states how the 1 Hz XCAL export rows are time-aligned to millisecond RRC timestamps. If a row stamped *t* summarises [t, t+1), the last pre-handover row contains post-decision radio state. The leakage guard in §4.6 covers only signalling features.

**Where.** §5.8, Table 5.8, §5.10, §3.1, §4.6.

**Why it matters.** The headline may be a property of burst structure and grid alignment, not of forecastable radio dynamics.

**What would address it.**
- Stratify all metrics by preceding dwell (e.g. >10 s, "first-in-burst", vs follow-ups).
- Add baselines: dwell-only, history-block-only, and the fitted Hawkes intensity used as a predictor.
- Document row/timestamp alignment and re-run with features lagged by one full sample.
- Report the ablation with the history block removed.

### 3. [Evidence — unit construction] The "drive" appears to be a fixed 180-sample chunk, not an independent mobility unit

**Issue.** Steelman: grouping by segment is far better than random rows, and LOCO results close to pooled ones suggest limited route memorisation.

Press: Table 3.2 gives samples = drives × 180 exactly for every campaign (15×180 = 2,700; 8×180 = 1,440; 20×180 = 3,600; 14×180 = 2,520).

- §3.4 defines a drive as a quality-filtered contiguous segment of ≥60 s, which cannot yield identical lengths.
- So "drives" are presumably 3-minute slices of one continuous same-day recording on the same route. Sibling slices share cells, junctions and traffic, and sit in both train and test.
- The "mobility unit is held out" claim, the cluster bootstrap "over drives" and the CRC exchangeability unit all inherit this. Adjacent slices are temporally ordered and dependent. The effective number of independent clusters is closer to 4 (days).

**Where.** Table 3.2, §3.4, §4.9, §4.10.

**Why it matters.** The CIs are too narrow, exchangeability is asserted rather than defended, and contribution 3 ("the exchangeable unit is the drive") is hollow if a drive is an arbitrary window.

**What would address it.**
- State the segmentation rule truthfully.
- Bootstrap and conformalise at route-pass or campaign level, or show that inter-slice dependence is negligible.
- Present LOCO as the primary protocol.

### 4. [Statistical rigour / Presentation] Numbers contradict each other, and some are arithmetically impossible

**Issue.** Steelman: Appendix C says every table is regenerated from stage outputs.

Press: the manuscript's numbers do not survive a pocket calculator.

- **(a) Impossible inflation.** Table 5.3 gives a +74 % inflation of the GRU's 1 s AUPRC. Table 5.2 gives that AUPRC as 0.617, and 0.617 × 1.74 = 1.07 > 1.
- **(b) Fold counts.** §4.9 and Fig. 4.2 say 4 folds × 5 seeds = 20 paired observations. §5.2 and Fig. 5.4 say "eight grouped-drive folds". §5.4 cites "p < 0.0001 over the twenty paired folds" and, two sentences later, a signed-rank test "on only eight observations".
  - With n = 8, the smallest two-sided signed-rank p is 0.0078.
  - With n = 20, the "pairs" are reshuffles of the same 57 drives. That is pseudo-replication, not independence.
- **(c) Hazard vs prevalence.** Table 4.2 gives a bin-1 mean hazard of 0.053. Table 4.1 gives 0.5 s prevalence of 0.037, and these should be the same quantity. Chaining the Table 4.2 hazards gives F(1 s) ≈ 0.093 vs the stated 0.067.
- **(d) Expansion size.** §4.4 says long-format expansion gives "approximately 34,000" pairs. The at-risk arithmetic from Table 4.1 gives ≈ 47,000.
- **(e) Ablation vs headline.** Fig. 5.20 and §5.11 report the full model's 1 s AUPRC as 0.811. The headline is 0.784.
- **(f) Event detection vs miss rate.** Table A.2 says 44.7 % event detection is "at the certified operating point" α = 0.20, where realised sample miss rate is 12.6 %. Catching ~87 % of positive samples while detecting <45 % of events needs an explanation. No event-detection definition is given, and the CRC horizon is never stated.
- **(g) Missing calibration numbers.** Table 5.4 is captioned "coherence and calibration" but contains no calibration numbers. The control arm's ECE and AUPRC appear nowhere. The "monotone projection" control promised in §4.2/§4.8 is absent. Fig. 5.8 refers to "all four configurations" while the table has three.
- **(h) Offset sign.** The abstract and contribution 4 say deployed A3 offsets are "negative rather than positive". Table 3.1 shows the dominant profile is +1 dB, carrying 72.4 % of handovers. Fig. 1.1's caption says +1 dB. §3.5's "false for the majority of handovers" contradicts its own table.
- **(i) External dataset provenance.** §5.7 and Fig. 5.11 say the external dataset shares "no network and no operator". §5.13 says it was released by the authors of a comparator "developed on the same operator and instrument".
- **(j) Comparator reporting.** §2.10.1 says the RL comparator reimplementation is reported in Chapter 5. §5.13 says it is not.
- **(k) Counting bound.** A "counting upper bound" on benefit is invoked (§1.5, §5.13: "peaks at a five-percent alarm budget and turns negative by forty") but never shown.
- **(l) Cross-references off by one.** §3.3.3 points to §5.8 where §5.9 is meant; §3.4 points to §4.5 and §5.9 where §4.6 and §5.10 are meant; §4.11 points to §5.9 where §5.10 is meant. Eq. (4.10) is unnumbered and defines a set, not a rate. λ denotes both hazard and threshold.

**Where.** As cited above.

**Why it matters.** At a Q1 venue, (a), (c), (h) and (i) alone destroy trust in the "regenerated, not transcribed" claim and in the results they touch.

**What would address it.** A full numerical audit with a released results manifest, and one consistent definition each of folds, tests and event detection.

### 5. [Evidence — pre-registration] The "frozen before the data existed" claim is unverifiable and chronologically strained

**Issue.** Steelman: scheduling a campaign after a freeze is excellent practice, and the highway LOCO row (AUROC 0.927) is the best-designed experiment in the paper.

Press:

- Table 3.2 dates the campaigns 10, 12, 13 and 15 September 2026, and the approval page is dated 21 September 2026. The largest campaign (20 drives) was therefore collected two days before the freeze, and the whole thesis was completed six days after the final drive.
- §6.9 says the work spanned two academic terms, with campaigns 1–2 in the first and 3–4 in the second. Both cannot be true.
- The manifest has no hash, timestamp or public registration.
- The highway campaign is included in the pooled headline, in the CRC calibration pool ("pooling… across the four campaigns", §4.10), and in whatever produced the final hyperparameters.
- Twenty-trial tuning is never described as nested, and "fold hygiene" (§4.9) omits hyperparameters.
- "Adding it moved AUROC by nothing (0.933 → 0.933)" is not evidence against overfitting. It is one number to three decimals.
- The network configuration is identical across campaigns (§3.5), so the highway row tests speed and corridor only.

**Where.** §3.2, Table 3.2, §5.6, §6.9, App. C.

**Why it matters.** The only genuinely out-of-sample claim rests on an unauditable assertion.

**What would address it.**
- Correct the dates, publish the timestamped manifest or commit, and use nested tuning.
- Report the highway result from the pre-freeze model object, not a LOCO refit.

### 6. [Baselines / Novelty] The A3 "baseline" is a strawman, and the strongest measured-data predictor is cited but not compared

**Issue.** Steelman: scoring the deployed rule is a reasonable sanity check.

Press: a binary indicator that is reactive by construction, giving AUROC 0.653, is not a baseline for a forecasting task. The appropriate baselines are:

- trend-extrapolated time-to-A3-entry per profile;
- the history-only and Hawkes predictors of concern 2;
- published systems.

Reference [5] is cited only to "legitimise tooling". It presents Prognos, a handover predictor built on RRC-decoded measurement reports and learned carrier policy. It was evaluated on real traces at 0.4 % prevalence, with F1 0.92–0.94, precision/recall, and a reported mean lead-time gain of 931 ms. It was compared against GBDT and stacked-LSTM baselines that scored F1 0.24–0.48.

That directly contradicts three statements in the thesis:

- "measurement-grade ground truth exists, but is not joined to prediction" (§2.9);
- "none reports how early its warnings arrive" (§1.2, §2.3);
- the use of GBDT as the winner here.

The 22 audited papers are never listed, so the audit (Table 2.1) cannot be checked. The "0/22" rows carry the novelty argument.

The title says "Conformalized… Hazard". The method is actually CRC on a threshold. Conformalized survival analysis (Candès, Lei, Ren) is neither cited nor distinguished.

**Where.** §2.2, §2.3, §2.9, §4.7, §5.13.

**Why it matters.** Novelty and superiority are asserted against a field from which the strongest comparator has been omitted.

**What would address it.** List the 22 papers. Re-implement Prognos-style and trend-extrapolation baselines. Relate the work to conformalized survival analysis.

### 7. [Missing ablation] The hazard formulation's benefit is not a distinguishing test

**Issue.** 0 % violations "by construction" is a tautology, not a result.

The meaningful comparison is hazard against independent classifiers plus per-sample isotonic projection or rearrangement. That repair needs no held-out split, contrary to §4.2, and also yields 0 % violations. The comparison should cover AUPRC, ECE and Brier at each horizon. It is absent.

Other gaps:

- §5.2 concedes the fold spread exceeds the gap between the two LightGBM arms.
- Violation magnitudes are not reported. 43.6 % could be 1e-4-scale noise.
- The hazard arm uses temperature scaling "on a held-out partition" (§4.8) while claiming "no held-out calibration split" (§1.6).
- §4.5's claim that reweighting "destroys" the scale ignores that Eq. (4.7) is analytically invertible.

**Where.** §4.2–4.5, §5.4, Table 5.4.

**Why it matters.** Contribution 1 currently shows only that a product of numbers in [0,1] is monotone.

**What would address it.** Run the projection control and report violation-magnitude distributions and per-horizon paired differences at campaign level.

### 8. [Statistical rigour] The CRC section certifies almost nothing

**Issue.** Steelman: the feasibility floor α ≥ 1/(n+1) is correctly stated.

Press: it is an immediate corollary of Angelopoulos et al., not a "campaign-design rule… that appears nowhere".

- The provenance of the n = 28 calibration drives is never reconciled with the 43/14 rotation. It is unclear what was trained, calibrated and tested on what.
- There is one split and one realised point.
- "Bound held on 82 % of drives" is irrelevant to a guarantee in expectation.
- The risk is sample-level, not event-level.
- Exchangeability of 3-minute slices across days and corridors is assumed.
- At α = 0.05 the procedure alarms 61 % of the time. The honest conclusion is that the guarantee is not usable, not that objective O3 is "met".

**What would address it.** Repeated random calibration/test partitions at campaign-respecting granularity, event-level risk, and the full frontier with realised risk distributions.

### 9. [Domain validity] The signalling interpretations are doubtful

**Issue.**

- **(a) Report conversion.** 7,385 A3 reports in 10,260 s is 0.72 reports per second. This almost certainly reflects periodic re-reporting (reportInterval/reportAmount) while the entry condition persists. The 62.9 % figure therefore counts repeats of one event and calls them "declined". The unit should be the A3 episode. The paper never mentions reportAmount or reportInterval. The all-report-types figure (68.7 %) is meaningless because A1/A2 reports are not handover requests.
- **(b) "The network triggers on its weakest signal."** This compares a pooled best-neighbour gap against five profiles with offsets from −15 to +5 dB. It uses unfiltered 1 Hz samples, while the rule operates on L3-filtered values with a 320 ms TTT. The crossing and the command can both fall between two samples. Low single-feature AUROC at 1 s is a sampling artefact, not a mechanism, and "structurally late" does not follow. Hysteresis and Ocn are never reported, so the effective margin is unknown.
- **(c) Re-establishments.** 341 RRC re-establishments against 938 handovers, about 120 per hour, is implausible for a functioning commercial network and suggests a decoding or counting problem. The paper never examines causes, how these events reset dwell time, or how post-RLF samples are labelled.
- **(d) Negative offsets.** Negative A3 offsets for inter-frequency or priority-layer steering are ordinary. Calling this a finding with "disproportionate consequence" overclaims.

**Where.** §1.2, §3.5, §5.8–5.9, Table 3.1.

**What would address it.** Episode-level conversion, per-profile gap analysis on the correct measurement object, re-establishment cause decoding, and reporting of Hys/Ocn.

### 10. [Reproducibility] Nothing is released, and the text is insufficient to replicate

**Issue.**

- Code and data are "planned", which sits badly with Table 2.1's scolding of others.
- The following are all missing: hyperparameter spaces and selected values, the sequence-model window length, neural training details, ECE bin count, bootstrap replicates, event-detection and false-alarm-episode definitions, the external-dataset feature mapping, the transfer procedure and the curation rule. It is unclear whether the external dataset has RRC logs at all, or which of the 107 features survive.
- Drafting errors remain:
  - Reference [33] has a version/DOI mismatch ("v2" vs ".1").
  - Reference [34] is never cited.
  - Placeholders remain ("[Supervisor Name, Title]").
  - The declaration title differs from the thesis title.
  - "My own handset" conflicts with "departmental equipment".
- Several references look mis-transcribed and need checking against sources. Examples are the [3] author initials and title, and the [6] authorship.
- A search on the dataset DOI surfaces a publication titled "Handover Optimization in LTE Networks Using Contextual Bandit Reinforcement Learning and Real-World Data". The authors should reconcile this with §5.13's claim that "no publication record for the comparator could be located".

## Minor concerns

- Seven-model rank order is identical at all five horizons with near-constant ratios (Table A.1) and no CIs. Show per-fold spreads.
- Sequence models consume raw windows while tabular models get engineered features including dwell time. The "temporal memory doesn't help" conclusion is confounded by input set.
- Under random-row splitting, sequence windows overlap across the split. That is input duplication, not "temporal memory", so §5.3's mechanism story is untested.
- Hawkes: the fit is rejected by the authors' own KS test (p = 7×10⁻⁴), yet the branching ratio is still interpreted. Per-campaign intervals overlap, so "lowest on the highway" is noise. Estimation on 3-minute slices truncates history.
- The 0.5 s horizon on a 1 Hz grid is mostly sub-sample phase noise. The "90.5 % ceiling" derivation is not given.
- "TTT is the lever" (§5.10) is a causal claim from one configuration with no variation. The disclaimer does not undo the sentence.
- The proposed fuzzy RD "at the A3 boundary" conflicts with the paper's own statement that the policy is deterministic given state.
- Durations: 2,700 s is 45 min and 2,520 s is 42 min, not 46 and 43. "95 km" is hard to square with the stated speeds.
- Chapter 6 and much of Ch. 1–2 are padded with self-congratulation ("what a careful reviewer checks"). Cut the prose by about 40 %.
- Figures cannot be assessed from captions. Several captions carry claims (Fig. 5.2 "comparable false-alarm rate") with no numbers anywhere.

## Belief update

Two things shifted my beliefs, and only modestly.

- **Bursty handovers.** I now believe handover arrivals on a dense urban LTE network can be so bursty that a dwell-time counter alone yields AUROC ≈ 0.87 for "handover within 1 s". Any future handover-prediction paper must therefore report a history-only baseline and first-in-burst performance.
- **Random-row splitting.** It is modestly reinforced that random-row splitting misleads on 1 Hz drive data. I already believed this. The specific 74 % figure is arithmetically impossible as presented, so I take only the direction.

Nothing of substance shifted on the hazard formulation (a tautology without the projection control), the conformal guarantee (one split, unusable at tight α), transfer (0.75 AUROC, single metric, provenance contradictory), or the "network triggers on its weakest signal" mechanism, which I read as a sampling artefact.

## Verdict

**Reject** (in current form; resubmission after a rebuild is encouraged). The headline and nearly every supporting claim are shown only through the single most favourable horizon, metric and slice, on 2.9 h of data cut into 180-sample "drives". Once the omitted horizons, the omitted controls (history-only, projection, Prognos-style) and the numerical contradictions are put back, the text leaves no claim standing at a Q1 bar.

Sources:
- [Vivisecting Mobility Management in 5G Cellular Networks (SIGCOMM 2022) — ACM DL](https://dl.acm.org/doi/10.1145/3544216.3544217)
- [Vivisecting Mobility Management in 5G Cellular Networks — author PDF (Prognos design and evaluation)](https://feng-qian.github.io/paper/5g_mobility_sigcomm22.pdf)
- [Handover Optimization in LTE Networks Using Contextual Bandit Reinforcement Learning and Real-World Data — ResearchGate record](https://www.researchgate.net/publication/396132842_Handover_Optimization_in_LTE_Networks_Using_Contextual_Bandit_Reinforcement_Learning_and_Real-World_Data)
- [Conformalized Survival Analysis — Candès, Lei, Ren (arXiv 2103.09763)](https://arxiv.org/html/2103.09763)

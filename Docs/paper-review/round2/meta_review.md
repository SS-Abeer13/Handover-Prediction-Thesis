# Meta-review — *Leakage-Audited Multi-Horizon Handover Forecasting from LTE Drive-Test Signalling*

**Panel:** three independent reviewers (alfa, bravo, charlie), no shared context.
**Date:** 18 September 2026.
**Manuscript:** `Handover_Thesis_Manuscript_Revised.docx` (revision of the draft reviewed 17 September 2026).

---

## Per-reviewer verdicts

- **alfa — Major revision.** "The measurement work, the alignment audit and the willingness to report results that damage the authors' own earlier claims are genuinely above the standard of the surrounding literature and are worth publishing — but as submitted the manuscript prints three different values for its headline AUPRC, three for its headline ECE and two for its headline violation rate, builds its protocol contribution on a table that contradicts its primary results table, reports a conversion rate whose numerator exceeds the events available to it, and promises code, data and two cross-referenced sections that do not exist."

- **bravo — Major revision** (explicitly conditional: *"If the Table 5.4 / Table 5.5 contradiction cannot be reconciled on re-run, my recommendation becomes Reject."*). The central mechanism claim rests on "a self-constructed downsampling contrast that could not have failed, a four-way-confounded control, and an n = 15 test whose selection does not reconcile with the reported interruption distribution."

- **charlie — Major revision.** "None of this is fatal to the underlying work, but all of it must be reconciled, with the uncertainty re-estimated at the campaign level, before the paper can be assessed on its merits."

All three open by crediting the paper's honesty — the self-destruction of the 0.600 figure, the reporting of controls that weaken the authors' own formulation, the explicit statement that four units cannot support a significance claim. None of them regards the underlying study as unsound. Every concern below is about what the manuscript *says* relative to what its tables *contain*.

---

## Common concerns — raised by two or more reviewers

### A. One estimand, three published values (3/3) — the panel's dominant complaint

All three independently isolated the same defect: the one-second LOCO AUPRC of the primary model appears as **0.179** (Tables 5.3, 5.4, A.1, abstract), **0.160** (Table 5.5) and **0.157** (Table 5.6). The one-second ECE appears as **0.012**, **0.036** and **0.024**. The ordering-violation rate is **40.2 %** in the abstract, §2.5, §4.2, §5.4 and §7.1, and **29.0 %** in Table 5.6.

Strongest formulation (bravo): *"A reader cannot tell which number is the result."* Sharpest instance (charlie): §5.4 says isotonic calibration makes coherence worse, *"violations rise from 40.2 % to 33.4 %"* — which is a **fall**, and is only arithmetically coherent against the table's 29.0 %.

**Verified against the pipeline.** The three AUPRC values are three genuinely different experimental arms — nested 20-trial tuning over three seeds (0.179), the fixed-hyperparameter protocol ladder (0.160), and the fixed-hyperparameter coherence experiment (0.157). Likewise 40.2 % is the single-seed violation rate and 29.0 % the seed-averaged one. **The numbers are not wrong; the labelling is.** All three tables present themselves as the same quantity under the same conditions, and Table 5.5's caption explicitly says "with all else held fixed". That is a captioning and cross-referencing failure, not a computation failure — but it is fatal to readability and it falsifies Appendix C's claim that regeneration prevents silent disagreement.

### B. The leaderboard-reordering claim survives only in the untuned arm (3/3)

Contribution 3 rests on "under leave-one-campaign-out the leading learner at one second is logistic regression; under random-row splitting it is LightGBM." That holds in Table 5.5 (lr 0.167 > lgbm 0.160). In Table 5.4 the same protocol gives lgbm 0.179 > lr 0.130 — a 0.049 gap in the opposite direction.

**Verified:** the reordering is real *within the fixed-hyperparameter ladder* and disappears once the learners are tuned. The honest statement is therefore narrower than the one printed: *the protocol reorders untuned learners*. charlie adds that a 0.007 gap sits far inside the per-campaign spread (0.132–0.233, Table 5.8), so even within the ladder the reordering is not distinguishable from fold noise.

bravo and charlie both further note that the **A3 rule cannot serve as the control it is used as**: it is deterministic and the pooled out-of-fold row set is identical under all four protocols, so its 0.116 is invariant *by construction* and has zero power to detect a difference in test-set difficulty. This is correct and is a genuine methodological error, not a presentation issue.

### C. The mechanism evidence is not a distinguishing test (bravo, charlie; alfa on the arithmetic)

bravo's central charge, and the most consequential idea in the panel: the NUWiNS experiment downsamples a 10 Hz corpus *by the authors' own rule*, so "93.2 % under last-sample, 4.1 % under first-sample" is entailed by the construction. It shows end-of-second aggregation is **sufficient** to produce the artefact; it does not show that XCAL's native 1 Hz export does that. charlie reaches the same conclusion independently and proposes the same wording fix: call it *"a controlled demonstration that the aggregation rule alone produces the artefact"*, not cross-instrument replication.

Both also fault the Raca control: its event clock is the serving-cell identifier itself, so asking whether row *t* already shows the new cell is close to circular, and its 29.4 % is 2.5× the paper's own claimed background rather than "none". bravo notes a sharper problem — the Raca data shows a *larger* jump at t−2 → t−1 (+57 %) than at t−1 → t (+38 %), which is the paper's own contamination signature appearing in its designated clean control at a different lag, disposed of in one sentence.

All three then converge on the same arithmetic gap in the falsification test (concern D).

### D. The n = 15 falsification test does not reconcile with the reported interruption distribution (3/3)

The paper reports p90(x) = 99 ms, max(x) = 105 ms, and that 65 % of commands record a non-zero interruption. Under δ ~ U(0,1) that implies of order 20–45 boundary-crossing handovers out of 938, not 15. alfa presses further: if ~35 % of commands have x ≈ 0, the "0 % contaminated when less than 50 ms remain" bin should show ~35 % contamination from the zero-x mass alone. charlie adds that a 0/15 result carries an exact upper 95 % bound of 0.22, which should be stated, and that a 10 Hz grid cannot discriminate a 60 ms delay from any other value below 100 ms.

This is the single most important technical finding of the panel, because the falsification test is the strongest evidence in §5.1 and the sub-second-delay recovery is contribution 2. It needs the full distribution of *x*, an explicit statement of what a recorded zero means, and a predicted-versus-observed count.

### E. The A3 "conversion rate" is a co-occurrence rate (alfa, charlie)

Table 5.12 reports 1,647 A3 episodes "followed by a command within 2 s" out of 2,361 — against 957 commands in the entire corpus. The +1 dB profile shows 717 converting episodes against 472 commands attributed to it in Table 3.1.

**Verified against the pipeline:** episodes map many-to-one onto commands. The "30 % declined" figure is therefore not a decline rate, and alfa's inferential point is the damaging one: *a profile that re-reports on several measurement identities simultaneously will show a spuriously low decline rate precisely because it is verbose*, which inverts the paper's reading of the negative-offset profiles as neighbour-monitoring. This is a real defect in contribution 6, and it repeats — at smaller magnitude — exactly the denominator error the paper criticises in the per-report unit.

### F. Two incompatible reference lists, and the external evidence base is uncitable (3/3)

**Verified:** the manuscript contains two complete reference lists — one embedded in the body after Table 5.15, running to **[41]**, and one under REFERENCES, running only to **[34]**. References **[35]–[41]** — which include Raca, the Mendeley dataset, the RL comparator and both NUWiNS papers — appear in no final bibliography. In-text numbering is unstable across the two lists ([18] is Candès in one and Cohen in the other; [21] is Angelopoulos in one and Hawkes in the other; [30] is Wagner in one and LightGBM in the other). Three entries still carry editorial placeholders.

### G. Missing sections that the table of contents promises and the body cites (3/3)

**Verified:** §5.12 (Discussion against the objectives) and §5.13 (Threats to validity) are in the ToC and cross-referenced from §5.10 ("for the reason given in Section 5.13") but do not exist in the body, which runs from Table 5.15 straight into the embedded reference list. §7.3's heading and §6.1–6.4 are likewise absent. bravo's review carries an explicit scope caveat because of this — the threats-to-validity section is the one a reviewer most needs in a paper making this many bounded claims.

### H. Reproducibility asserted, not delivered (3/3)

Table 2.1 grades 22 prior papers on code release (2/22) and data release (1/22) and enters "Planned" for itself. The feature inventory is irreconcilable across four statements — 152 candidates (§2.10), 112 columns (§4.6), Table 4.3's blocks summing to 106 under a total row of 112, 107 features (§4.7 and Appendix B), Appendix B's own itemisation summing to 120. Seeds are five in §2.10 and three in §4.9. §4.7 says the sequence models consume "the same vectors, lagged the same way" and, two paragraphs later, "raw per-second measurements rather than the engineered summary features."

### I. Conformal risk control reported below its own feasibility floor (3/3), and against the wrong estimand (charlie)

All three flag the α = 0.05 row: §4.10 derives α ≥ 1/(n+1) = 0.067 at n = 14, and §5.5 states only 25 % of rotations can express α = 0.05, yet the row is printed without a marker. The calibration-set size is stated as 14 blocks, 28 drives and 57 blocks in three places.

charlie alone identifies the deeper problem: conformal risk control guarantees **E[R] ≤ α**, an expectation, while Table 5.7 evaluates the *frequency* with which individual rotations fall below α — a different object, and the one Chapter 7 elevates to "the honest measure of what exchangeability across days is worth here." charlie also notes the risk is printed as a set/count rather than a loss bounded in [0,1], which is not admissible under the cited bound.

### J. The event-level operating point contradicts the motivation (3/3)

At the 5 % false-positive point the system detects 34.0 % of events with 179 false alarms per hour and a **median lead time of 0.47 s** (Table A.2). §1.2 motivates the work by asserting that one second is enough for target-cell preparation, and §2.8 cites Deb et al. for the proposition that 200 ms of lead "buys nothing." The abstract, §5.2 and §7.1 report only AUPRC, AUROC and lift. In a paper whose indictment of the field is that *"none reports how early its warnings arrive or how many false alarms they generate per unit time"*, burying exactly those numbers in an appendix is the panel's clearest charge of selective emphasis.

### K. The "independent" external validation, and an undeclared conflict (3/3)

§5.7 discloses that the public dataset was produced in the same department. What none of the text states is that the thesis supervisor is a **co-author of reference [38] and of the comparator study [39]**. Table 5.9 is nevertheless headed "an independently collected public dataset", and the Acknowledgements thank its authors as a third party. All three reviewers ask for a formal COI statement and for "independent" to be softened.

All three separately note that the transferred model (AUROC 0.760) outscores both the in-domain model trained on that data (0.711) and the authors' own in-domain result (0.730) — an inversion that normally indicates an easier or shorter target set (1,455 rows), left unexplained. alfa adds that §5.7 evaluates a *different feature set* (signalling-only) from the one all the paper's results use, so it cannot answer objective O4 as stated.

### L. The closest prior system is named and never scored (3/3)

Prognos (Hassan et al., SIGCOMM 2022) is called "the closest prior system to the one built here" and then excluded from the audit as "a system component rather than a published prediction model." Its ~900 ms lead-time gain is directly commensurable with this paper's 0.47 s median lead and is never put beside it. §2.10.1 promises "Chapter 5 reports a reimplementation of that comparator scored as a predictor" — no such row exists anywhere.

All three also press the novelty framing: temporal misalignment and window-aggregation leakage are a catalogued bug class (Kaufman et al., cited as [36] and never used), and hazard/sojourn-time modelling of cell residence is long established in the analytical cellular literature. The correct claim is narrower and still worth making: *the first drive-test instantiation of a known leakage class, with its cost measured.*

### M. Inference from four confounded units (alfa, charlie)

Campaign is perfectly aliased with corridor, speed, date, duration, time of day and event density. charlie's sharpest point: Table 5.3's 95 % intervals are block-bootstrapped over 180-second blocks *within* campaign — the very unit §5.3 proves is dependent — so the primary interval uses the resampling unit the paper itself invalidates one section earlier, and the same unit then defines the conformal "exchangeable regime". The learner spread in Table 5.4 (0.130–0.179) lies entirely inside the primary model's own stated CI (0.159–0.204).

### N. Dataset accounting does not close (3/3)

957 vs 938 handovers against a block table in which no block appears to have been dropped; distance 78 km (§3.6) vs ~95 km (Table 6.6) vs ~96 km implied by speed × duration; Table 3.1 printed rows summing to 907 of 957. **Verified:** the underlying profile table does sum to 957 — the manuscript prints a truncated version without saying so.

### O. Ping-pong and Hawkes (bravo, charlie)

The definitional ladder is quoted as 24.5–41.3 % (§2.4), 26.3–43.8 % (§5.10, Table 5.13) and 26.3–41.3 % (§7.1); no table contains 24.5 % or 41.3 %. §5.10 asserts ping-pong "is not driven by speed" while the table beneath shows 32.2 % on the highway campaign against 25.0 % urban — higher at double the speed, marginal at p ≈ 0.05, on one confounded unit — and §7.3 hardens this to "having ruled out speed as the driver." The Hawkes branching ratio of 0.653 is interpreted quantitatively even though the paper reports that the Ogata residual test **rejects** the fitted kernel; bravo and charlie both call for the causal-attribution sentence to go. alfa separately notes 0.653 is expected *direct* offspring, not total (≈1.9).

---

## Unique concerns — raised by one reviewer only

- **alfa — leave-one-campaign-out does not close spatial leakage.** Three of four campaigns share a Dhaka extent; the paper never reports cell-identity or route overlap between held-out and training campaigns. The one geographically disjoint campaign (highway) is also the weakest (0.132 vs 0.196–0.233), which is precisely the pattern spatial leakage in the other three folds would produce. For a paper titled "Leakage-Audited", asserting campaign independence rather than testing it is a conspicuous gap. Fix is cheap: report PCI-set Jaccard overlap per fold, and add a spatially blocked rung to the ladder.
- **charlie — row *t*−3 is not a chance baseline.** With a ping-pong rate of 26–44 %, the target cell is often a cell that was serving shortly before, so the 12.1 % "background" is inflated for reasons unrelated to aggregation. The audit needs a permutation or PCI-frequency-matched null.
- **charlie — the CRC estimand mismatch** (see I above).
- **bravo — the Raca control exhibits the paper's own contamination signature** at t−2 → t−1, a false positive for the detector being proposed.

---

## Ranking of reviewers

1. **charlie** — the most distinct, verifiable findings, and two that nobody else reached: the conformal risk-control estimand mismatch (a genuine statistical error, not a presentation one) and the row *t*−3 null. Its design critique — that the primary confidence interval is bootstrapped over the unit the paper itself proves is dependent — is the cleanest internal contradiction anyone found.
2. **bravo** — fewer findings, but the single most consequential idea in the panel: that §5.1's evidence is all *consistent-with* and none of it *distinguishing*, and that the one distinguishing experiment (a native-rate re-export of the authors' own captures) is available and not performed. Its belief-update section is unusually informative about which claims actually landed.
3. **alfa** — broadest verification of the arithmetic, and the only reviewer to catch the spatial-leakage gap and to state the conflict of interest in the terms a journal requires. Its A3-conversion finding (shared with charlie) is the most damaging single arithmetic error in the paper.

The gap between the three is narrow; the ordering reflects depth of unique contribution, not quality.

---

## Verdict synthesis

**Major revision — unanimous, and not close to Reject on the science.**

All three reviewers independently judged the underlying study sound and the alignment audit worth publishing. Not one concern attacks the data collection, the RRC decoding, the hazard formulation or the honesty of the reporting. What the panel attacks is the manuscript's internal consistency and the distance between its prose and its tables — and my own check of the pipeline confirms the panel is right about the facts while being wrong about one diagnosis:

- **The three AUPRC values and the two violation rates are three different experimental arms, correctly computed.** The fix is captions, cross-references and one sentence saying which arm each table reports — not a re-run. bravo's conditional escalation to Reject ("if the Table 5.4 / Table 5.5 contradiction cannot be reconciled") is therefore satisfiable, but the reordering claim must be narrowed to *untuned* learners, because that is the only arm in which it holds.
- **Four defects are real and require work, not relabelling:** the A3 episode denominator (many-to-one onto commands, verified); the "violations rise from 40.2 % to 33.4 %" sentence, which mixes two estimands and inverts its own direction; the two reference lists with [35]–[41] missing from the final bibliography; and the missing §5.12/§5.13/§7.3.
- **Three claims must be narrowed rather than defended:** the NUWiNS experiment is a controlled demonstration, not a cross-instrument replication; the Raca dataset is a weak control whose event clock cannot separate the hypotheses; the sub-second update-delay recovery needs the full distribution of *x* before it can stand.
- **Two things should simply be added:** the event-level operating point in the abstract and §5.2, and a conflict-of-interest statement naming the supervisor's co-authorship of [38] and [39].

The paper's own thesis — that on drive-test data the protocol and the timestamp semantics decide the result before the model does — is one all three reviewers believe. The revision's task is to stop the manuscript from being a counterexample to its own standard of bookkeeping.

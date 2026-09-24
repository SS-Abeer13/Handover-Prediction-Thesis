SEED: `189493d0f85ef485a65226b3bb3ff9a3`
AXIS: 0 — Distinguishing-test failure
STANCE: 1 — Adversarial

---

# Review — Reviewer echo

## Summary

The paper asks whether an LTE handover command can be forecast seconds ahead from handset-observable measurements, using four drive-test campaigns (2.9 h, 10,260 1 Hz samples, 957 RRC-decoded handover commands) on one commercial operator in Dhaka/Gazipur. It poses the task as discrete-time survival (per-bin hazards, horizon probabilities via the product-limit identity), evaluates under leave-one-campaign-out (LOCO) with a four-rung splitting ladder, and adds conformal risk control at the drive level. The headline result is negative-flavoured and is the paper's best feature: an audit finds that in 75.9 % of handovers the 1 Hz export row stamped *before* the command already carries the *post*-handover serving cell, and lagging every export feature one row collapses one-second AUPRC from 0.600 to 0.179 (2.6× a 6.8 % floor, AUROC 0.777), against 0.116 for the deployed A3 rule scored as a predictor. Secondary claims: random-row splitting inflates AUPRC 48 %, independent per-horizon heads violate ordering on 40.2 % of rows, and two operator-configuration characterisations (A3 conversion has no unit-free value; 75 % of A3 handovers fire under a positive offset).

## Major concerns

**1. [AXIS] The central mechanistic claim is never subjected to a distinguishing test, and the one intervention that would distinguish it was not run.**

*Issue.* The paper's title, contributions 1 and 2, and its most-quoted number (0.600 → 0.179) all rest on the claim that end-of-second row aggregation leaks the post-handover cell into the row stamped `t`. Every piece of evidence offered is consistent with that account but also consistent with at least one rival account, and the paper never constructs an experiment that separates them.

- The NUWiNS test (§5.1, Appendix A Table A.3) is presented as "the decisive one." It is not a test. Downsampling a 10 Hz log by keeping the *last* sample of each second and then observing that the last sample of a second containing a handover shows the post-handover cell is a tautology of the downsampling rule, not a discovery about XCAL's 1 Hz exporter. The 93.2 % / 4.1 % contrast confirms arithmetic, not a hypothesis about the authors' own instrument — which §5.13 concedes remains inferred ("does not establish the exact semantics of the XCAL row timestamp, which the vendor documentation does not state").
- The falsification test (n = 15 boundary-crossing handovers, "not one contaminates its row") is *the same rows* as the intra-second gradient in panel (e). With x ≈ 60–105 ms, `m < 0` requires δ > ~0.9, so the 15 handovers are by construction the latest-arriving ones, which the δ-gradient already shows are least contaminated. The two "predictions" are one prediction counted twice. Worse, the arithmetic does not reconcile: δ should be near-uniform, 938 commands with 65 % carrying non-zero x and x in the 60–105 ms band should put roughly 40–60 events in the `m < 0` set, not 15. The paper does not address the discrepancy.
- The 22.5 % residual (positive margin, no contamination) is rescued by a second, post-hoc mechanism ("the exporter refreshing the serving-cell field one row late"). Once a free one-row refresh lag is admitted, the account predicts contamination *or* non-contamination for any handover and is unfalsifiable as stated.
- The Irish control (Raca et al., 29.4 %) is adjudicated clean by a post-hoc shape criterion invented in the same paragraph ("a contaminated final row shows up as an anomalous jump at the last step; a clean log shows the smooth decay"). 29.4 % is more than twice the paper's own 12 % background rate; no pre-stated threshold separates "no defect" from "attenuated defect."

*The missing distinguishing experiment.* The repair lags **every** export feature by one row. That confounds two entirely different things: (a) removing leaked serving-cell identity, and (b) discarding one second of legitimately predictive radio information (RSRP/SINR/gap trajectories). The obvious arm — lag only the cell-identity-derived features (serving PCI, dwell, gap-to-*serving*), keep the radio block at its original alignment — is never reported anywhere in the paper, though the authors plainly have the data. Until it is, "0.600 → 0.179 is leakage" is indistinguishable from "0.600 → 0.179 is leakage plus a self-inflicted one-second information handicap," and the title claim is unsupported.

*Where.* §5.1 (lines ~983–1009), Table 5.1, Table 5.2, Table A.3, §5.13 "Residual alignment risk."

*Why it matters.* This is the paper's only genuinely novel finding. If the effect is even 40 % information loss rather than 100 % leakage, then (i) the "236 %" figure in §5.12 is wrong, (ii) the recommendation to the field ("lag every export feature") is the wrong recommendation, and (iii) the corrected 0.179 is an under-estimate of what a correctly aligned predictor achieves — which changes the paper's conclusion about whether handover is predictable at all.

*What would address it.* (i) The selective-lag ablation above, reported at 1 s and 5 s on the same folds. (ii) The native-rate re-export §7.3 already names as the top follow-up — the authors hold the captures; this is a re-export, not a new campaign, and a paper whose thesis is "verify alignment rather than assume it" cannot ship with its own alignment assumed. (iii) Drop "decisive" from the NUWiNS framing and state what it actually establishes.

**2. The primary result table and the protocol-ladder table report different numbers for the same cell, and the contradiction destroys the claim the ladder exists to support.**

*Issue.* Table 5.3, Table 5.4 and Table A.1 all give LOCO 1 s AUPRC of **0.179** for LightGBM and **0.130** for logistic regression. Table 5.5's LOCO column gives **0.160** for lgbm and **0.167** for lr. Table 5.6 gives **0.157** for the hazard arm. Three values for the primary number; LR moves by 28 % between tables and changes rank. The prose in §5.3 then asserts "Under leave-one-campaign-out the leading learner at one second is logistic regression" — true only in Table 5.5, flatly false in Table 5.4 where LR is last of six. The 48 % inflation headline is 0.236/0.160; the abstract attaches it to "the same number," i.e. 0.179, for which the implied random-row value would be 0.265, a number that appears nowhere.

*Where.* Table 5.3, Table 5.4, Table 5.5, Table 5.6, Table A.1; §5.3 ¶4; Abstract; Contribution 3; §5.12 (O2).

*Why it matters.* Contribution 3 — arguably the paper's most transferable claim — is that protocol choice *reorders the leaderboard*. That claim exists only inside Table 5.5's LOCO column, which contradicts every other LOCO table in the paper. As it stands the reordering could be an artefact of two different experiments being spliced into one table.

*What would address it.* Regenerate all five tables from one pipeline run, state which is canonical, and re-derive every percentage quoted in the abstract, contributions and §5.12 from it. Appendix C claims tables are "regenerated from the stage outputs rather than transcribed"; this is direct evidence that they are not.

**3. Expected calibration error takes three different values for the same quantity, and the per-campaign and pooled comparisons point in opposite directions.**

*Issue.* One-second ECE for the primary hazard model is 0.012 (Table 5.3, Table 5.8 pooled), 0.036 (Table 5.6), and 0.024 (§5.4 prose, line ~1114 — a number in no table). Separately, §5.4 states "the hazard arm has the lower calibration error on **0 of the four** held-out campaigns at one second," while Table 5.6 reports pooled hazard ECE 0.036 against independent 0.047. Losing 4–0 per campaign and winning pooled is a Simpson reversal that the paper neither notices nor explains. Table 5.8's pooled ECE (0.012) is also below the minimum of its own four per-campaign values (0.012, 0.018, 0.021, 0.033), which is possible but is the signature of ECE being computed on pooled scores in one place and out-of-fold per campaign in another.

*Where.* Table 5.3, Table 5.6, Table 5.8, §5.4 (lines ~1100–1114).

*Why it matters.* Calibration is objective O3 and one of the paper's four "0/22" novelty claims. The operational gloss in §5.4 ("among samples on which the system asserts a probability near 0.8, a handover follows on approximately 80 % of occasions") is attached to a number the paper cannot hold fixed across three pages, and the 4–0 per-campaign result is the more honest statistic.

*What would address it.* One ECE definition, one binning scheme, one fold aggregation, applied everywhere; report the per-campaign result as primary given n = 4; withdraw or heavily qualify "competitive calibration."

**4. The novelty claim is a four-way conjunction narrowed until it is true, and the nearest comparator is excluded on a procedural technicality and never compared numerically.**

*Issue.* "None of 22 holds out the mobility unit for a per-timestep classification task on measured radio data" survives only because each conjunct eliminates a different paper. Appendix D #9 (Amirova et al.) is real-measured, device-level hold-out, PR curve *and* bootstrap CI on AUC; #12 reports AP alongside AUC on real operator data; #13 uses rolling-origin temporal splits on Turkcell data. The paper's own headline count ("0/22") is then quoted in the abstract and §1.2 without the qualifiers. More seriously, Prognos — which the paper itself calls "the closest prior system to the one built here" and which predicts handovers from XCAL-decoded RRC on a live network with a ~900 ms lead-time gain — is removed from the audited set because it is "a system component rather than a published prediction model with its own protocol." It appears in [ACM SIGCOMM 2022](https://dl.acm.org/doi/10.1145/3544216.3544217) ([PDF](https://feng-qian.github.io/paper/5g_mobility_sigcomm22.pdf)). No number in this paper is ever placed beside a number from it, despite the paper reporting median lead times (0.47 s at 1 s, 3.31 s at 5 s) in exactly comparable units.

Relatedly, the alignment audit is framed as new to the field, but window-aggregation look-ahead bias is a named, documented leakage class — [Leakage (machine learning)](https://en.wikipedia.org/wiki/Leakage_(machine_learning)), [Purged cross-validation](https://en.wikipedia.org/wiki/Purged_cross-validation), and a standardised point-in-time look-ahead benchmark at [arXiv:2601.13770](https://arxiv.org/pdf/2601.13770). The paper's own reference [36] (Kaufman et al., *Leakage in Data Mining*) is in the bibliography and **cited nowhere in the text**. The correct framing is "a known leakage class, previously unaudited in this measurement setting, with a first quantification of its magnitude" — which is still worth publishing and is not what the abstract says.

*Where.* §1.2, §2.3 ¶6, Table 2.1, Appendix D, Abstract; reference [36].

*Why it matters.* An informed reader should update on the *magnitude* (70 % of AUPRC), not on the discovery of leakage per se. Overclaiming the latter invites a referee to discount the former.

*What would address it.* State the conjunction explicitly wherever "0/22" appears; add a numerical row for Prognos in Table 5.4 or explain in one sentence why its F1-on-events cannot be mapped to any metric here; cite [36] where leakage is first discussed.

**5. The "most important baseline" is handicapped by exactly the defect the paper is auditing, and no radio-block ablation isolates what the model adds.**

*Issue.* The Event A3 rule is described as "the most important baseline in the thesis because it is what is presently running in the network," yet it is scored from the *lagged 1 Hz export* (§5.1: "Everything reported after this section uses the lagged features"). The deployed rule runs on the UE's L3-filtered measurements at full rate with a 320 ms TTT; re-deriving its entry condition from a one-second-stale 1 Hz grid is not the deployed rule, it is a degraded reconstruction of it, and the degradation is in the same direction as the paper's headline effect. Secondly, a binary rule has no score to rank with; how a rule that either holds or does not yields AUPRC 0.116 and AUROC 0.689 (rather than a single operating point) is never specified. Thirdly, "History block only (LightGBM)" reaches 0.114 — within noise of the A3 rule — so 6 features of signalling history recover ~64 % of the full model's AUPRC, and the marginal value of the 83-feature radio block is never reported as its own ablation.

*Where.* §4.7, Table 5.4, Table 5.5, Table 5.11, Table A.1.

*Why it matters.* The paper's operational claim is "materially better than the deployed rule." That comparison is 0.179 vs 0.116 — a gap smaller than the gap between the paper's own two LOCO estimates of the numerator (0.179 vs 0.160).

*What would address it.* Score the A3 rule at native measurement-report rate from the signalling log (the authors have it, with millisecond timestamps); state the scoring rule that produces a continuous A3 score; add radio-block-only and radio+mobility ablations to Figure 5.19.

**6. The conformal contribution reports a row below its own stated feasibility floor, and at every operationally usable target the guarantee fails.**

*Issue.* Eq. (4.11) gives α ≥ 1/(n+1) = 0.067 for n = 14, and §5.5 states only 25 % of rotations can express α = 0.05 at all. Table 5.7 nonetheless reports a full α = 0.05 row (alarm 86 %, realised miss 0.018, 100 % of rotations respecting the bound). Either the floor is wrong or the row is. Meanwhile the cross-campaign regime — the one an operator faces — respects the bound in 92 %, 83 %, 83 % and 67 % of rotations at α = 0.10, 0.15, 0.20, 0.30, i.e. the guarantee fails one time in six at the loosest target anyone would deploy, at alarm rates of 36–55 %. §5.5 says the right thing in prose; the abstract and contribution 5 still sell the bound as an achievement.

*Where.* §4.10 Eq. (4.11), Table 5.7, §5.5, Abstract, Contribution 5.

*Why it matters.* A distribution-free guarantee that holds 67 % of the time is not a guarantee, and reporting an infeasible α invites the reader to distrust the rest of the table.

*What would address it.* Delete or footnote the α = 0.05 row; move the cross-campaign failure rate into the abstract; state plainly that with four sessions no deployable conformal target is attainable and reframe contribution 5 as the campaign-design corollary (which is the honest and useful part).

**7. Two of the formulation's stated advantages are vacuous on this dataset, by the paper's own statements.**

*Issue.* §4.1 argues censoring must be modelled ("the last samples of every drive are censored, and discarding them would both waste data and bias the observed event-time distribution"). §4.4 then states "**no row is censored inside the horizon grid**." The censoring-aware likelihood therefore does nothing here, yet "inherits the censoring treatment of Section 4.4" is listed in §5.4 as one of two surviving advantages of the hazard arm, and Figure 5.19 nonetheless reports "censoring ablations." Second, on the paper's own Table 5.6 the hazard arm's AUPRC (0.157) is *below* the raw independent control (0.158) and its ECE (0.036) is worse than isotonic+PAV (0.016); the cumulative-max projection reaches zero violations at zero cost in two lines. §5.4 and §7.1 concede this candidly — to the authors' credit — but the abstract and contribution 4 still lead with "zero ordering violations against 40.2 %," which is the comparison the body of the paper says is the wrong one.

*Where.* §4.1, §4.4, §5.4, §7.1, Figure 5.19, Abstract, Contribution 4.

*Why it matters.* After the paper's own corrections, contribution 4 reduces to "coherence from one fit with no held-out split," which is a convenience argument, not a methodological one. The abstract should say that.

*What would address it.* Delete the censoring advantage or demonstrate a dataset configuration where censoring binds; rewrite the abstract sentence to lead with the cumulative-max comparison rather than the raw independent heads.

**8. Reproducibility: the paper indicts a field for not releasing code and data, then releases neither.**

*Issue.* Table 2.1 scores the comparator literature 2/22 on code and 1/22 on data, against "Planned" for this work. There is no repository, no DOI, no seeds (§4.9 says "three seeds" but does not name them), no library versions, no hyperparameter search ranges (only "twenty random-search trials"), no LightGBM configuration, no definition of the "degenerate-feature filter," and no released audit script — despite §7.3 naming the audit script as "the parts of this work most worth releasing." Feature counts are irreconcilable: Stage 3 says **152** candidate features, §4.6 says **112** columns, Table 4.3's blocks sum to **106** (83+17+6), §4.7 says logistic regression runs "over the **107** features," Appendix B says "**107** retained" and then lists blocks summing to **120** (83+17+13+7), with signalling and history block sizes disagreeing between Table 4.3 (10, 6) and Appendix B (13, 7). Citation numbering is broken from [21] onward: §2.7 cites Hawkes as [21] (list: Angelopoulos), Laub as [22] (list: Bates), Ogata as [23] (list: Hawkes); §2.5 and §2.6 both use [18] for different papers; §4.7 cites LightGBM as [30] (list: Wagner); §4.8 cites temperature scaling as [31] (list: Deb); Wagner is [28] in §2.8 and [30] in §4.9.

*Where.* Table 2.1, §2.10 Stage 3, §4.6, Table 4.3, §4.7, §4.9, Appendix B, Appendix C, References [18]–[36].

*Why it matters.* A competent graduate student cannot rebuild the feature matrix (which count?), cannot resolve half the citations, and cannot re-run the audit. For a paper whose thesis is that the field's results are unreliable because its methods are unstated, this is disqualifying at a Q1 venue.

*What would address it.* An archived repository with the audit script, the four split protocols and the table pipeline; one reconciled feature inventory; a full pass over the bibliography.

## Minor concerns

- **Driving distance contradiction.** §3.6 says "approximately 78 km"; Table 6.6 says "approximately 95 km." Table 3.2's durations × mean speeds give ~96 km, and Table A.2's false-alarms-per-km (5.45 at 179.0/h) implies ~33 km/h, i.e. ~96 km. §3.6 is wrong.
- **"57 drives" vs "not drives."** §1.5 says "57 drives"; §3.4 says the 57 blocks are explicitly *not* a mobility unit. Appendix A and §6.3 call the protocol a "grouped-drive rotation." The paper's central protocol argument is undercut by its own terminology.
- **938 vs 957 usage contradicted within one subsection.** §3.4 says event-level analyses in §5.9 *and* §5.10 use 957, then says 957 is used "in exactly one place: the ungrouped variant of the ping-pong ladder in Section 5.9" — but ping-pong is §5.10, and Table 5.13 mixes n = 957 (rows 1–3) with n = 938 (row 4), breaking the "one unchanging set of handover commands" framing the section is built on.
- **Ping-pong range is stale in §2.4** ("24.5 % to 41.3 % on 938") against §5.10 ("26.3 % to 43.8 %" on 957 and "21.0 % to 43.8 %" across the nine-cell grid).
- **Table 3.1 does not sum.** Profile rows total 907 handovers (94.7 %), not 957; the A3 sub-rows total 648, not the stated 651.
- **Table 5.12 "x650.00 inflation" and "x927.00 inflation"** are table-generation garbage (the figures implied are ~2.6× and ~4.8×).
- **§4.7 self-contradicts on one page**: sequence models "consume windows of the ten most recent feature vectors — the same vectors" and, three paragraphs later, "raw per-second measurements rather than the engineered summary features." Also seven learners are promised; Table 5.4 adds an eighth ("Hawkes-kernel intensity (LR)") never described.
- **Non-monotone event-level detection** in Table A.2: 34.0 % at 1 s falls to 33.6 % at 2 s while the grid ceiling rises from 64.6 % to 74.8 %. Unremarked.
- **Operating point is never characterised honestly in the abstract.** Table A.2's 1 s point is 34.0 % detection at 179 false alarms/hour and 0.47 s median lead — one false alarm every 20 s on a route where handovers occur every 11 s. Neither detection rate, false-alarm rate nor lead time appears in the abstract or the contributions list.
- **Hawkes branching ratio is quoted as a finding (0.653, "roughly 0.7 further commands") from a model the Ogata residual test rejects.** A rejected kernel's branching ratio is not interpretable; the paper reports the rejection and the estimate side by side without resolving them. The Hawkes analysis also feeds nothing downstream except a learner that scores 0.120.
- **External validation isn't external.** §5.7's "independent" dataset is the same operator, city, instrument, department and supervisor, on a different route two years earlier — the paper says so. The transferred model also *beats* the in-domain model (0.760 vs 0.711) and the source-domain model (0.730), which normally indicates an easier target domain or an undertrained 1,455-row target model; the only comment offered is "the intervals overlap."
- **§5.11's "removing the signalling leakage guard raises the apparent score substantially"** gives no number, and contradicts §4.6 (the signalling block is "legitimate") and Table 5.15 (adding it *lowers* AUPRC, 0.168 vs 0.179). Three positions on one feature block.
- **§5.13's counting benefit bound** ("peaks at a five-percent alarm budget and turns negative by forty") has no table, no method and no other mention.
- **Duplicate table and figure numbers.** The List of Tables contains two conflicting blocks (5.5–5.12 each used twice); Figure 5.8 is captioned "Where the model earns its advantage" but referenced in §5.4 as the calibration/violation figure; the Figure 4.1 line is duplicated verbatim; the transfer table ([TABLE 16]) has no in-text caption.
- **Prevalence table cross-check passes**, and Table 4.2 chains exactly to Table 4.1 with at-risk counts summing to the stated 39,435 expansion. That arithmetic is clean and is worth keeping visible.

## Belief update

Two things, one large and one small.

The large one: I now put meaningful probability on 1 Hz drive-test exports from at least one major vendor being end-of-second aggregates rather than instant samples, and on that having contaminated an unknown fraction of the published handover-prediction literature. The NUWiNS start-vs-end downsampling result is tautological as a test of *this* instrument but it does establish the magnitude that end-of-second aggregation would produce if present, and the δ-gradient in the authors' own captures is a pattern I would not have predicted from an information-loss-only account. That is a real, checkable, cheap diagnostic and I will use it.

The small one: the prevalence floors in Table 4.1 (6.8 % at 1 s, 26.1 % at 5 s) and the resulting lifts (2.6×, 1.8×) are a useful calibration on what "handover prediction" can be worth at second granularity. AUROC 0.95+ papers on this task should now be read as protocol reports, not performance reports.

Nothing else moved. I do not accept the 0.600 → 0.179 decomposition as leakage until the selective-lag ablation exists; I do not accept "the protocol reorders the leaderboard" while the two LOCO tables disagree; and the hazard formulation, by the paper's own Table 5.6, is a convenience over `np.maximum.accumulate`, not a contribution. The conformal section persuaded me that four sessions cannot support a distribution-free guarantee, which is the opposite of what it was written to show — and to the authors' credit, they say so in §5.5.

## Verdict

**Major revision.** The alignment finding is worth publishing and the paper's self-correcting posture is genuinely unusual, but the mechanism behind its headline number has never been given a test that could have come out the other way — the NUWiNS arm is tautological, the n = 15 falsification is the δ-gradient counted twice, the 22.5 % residual is patched with a free parameter, and the one ablation that would separate leakage from information loss (lag only the cell-identity features) is absent from a paper that otherwise ablates everything; run it, reconcile the four mutually contradictory LOCO tables, and this becomes a good paper.

Sources consulted:
- [Vivisecting mobility management in 5G cellular networks — ACM SIGCOMM 2022](https://dl.acm.org/doi/10.1145/3544216.3544217) ([PDF](https://feng-qian.github.io/paper/5g_mobility_sigcomm22.pdf))
- [Survival prediction models: an introduction to discrete-time modeling — BMC Medical Research Methodology](https://bmcmedresmethodol.biomedcentral.com/articles/10.1186/s12874-022-01679-6)
- [Leakage (machine learning) — Wikipedia](https://en.wikipedia.org/wiki/Leakage_(machine_learning))
- [Purged cross-validation — Wikipedia](https://en.wikipedia.org/wiki/Purged_cross-validation)
- [A Standardized Benchmark of Look-ahead Bias in Point-in-Time Data — arXiv:2601.13770](https://arxiv.org/pdf/2601.13770)

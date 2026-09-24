# Meta-review — *Leakage-Audited Multi-Horizon Handover Forecasting from LTE Drive-Test Signalling*

**Panel:** three independent reviewers (delta, echo, foxtrot), no shared context, none shown any earlier round.
**Date:** 19 September 2026. **Round:** 3.
**Manuscript:** `Handover_Thesis_Manuscript_Revised.docx` as rebuilt on 18 September.

---

## Per-reviewer verdicts

- **delta — Reject.** "The alignment audit … is a genuine and transferable contribution that deserves publication, but the manuscript in its present state reports its own headline AUPRC as three different numbers, its own leaderboard two contradictory ways, its own calibration error three ways, and arithmetic in Tables 3.1 and 5.12 that cannot be correct; and its novelty framing rests on a literature screen that misses the cell-sojourn-time literature and carves out the closest prior system."

- **echo — Major revision.** "The mechanism behind its headline number has never been given a test that could have come out the other way … the one ablation that would separate leakage from information loss (lag only the cell-identity features) is absent from a paper that otherwise ablates everything; run it, reconcile the four mutually contradictory LOCO tables, and this becomes a good paper."

- **foxtrot — Major revision.** "The two headline LOCO tables contradict each other on every learner, the conformal guarantee certifies a row-level quantity while the text promises an event-level one … no measured operating point supports the target-cell-preparation motivation … and a headline contribution contains arithmetic that cannot be right; none of this is fatal to the underlying work, but all of it must be resolved."

One Reject and two Major revisions. The Reject is not on the science: delta's verdict sentence names bookkeeping, table contradictions and novelty framing, and opens by saying the audit "deserves publication."

---

## Status against the previous round

Round 2's four *action* items were addressed before this round, and the panel confirms three of the four are gone: no reviewer reports a duplicate reference list, missing sections, or a misquoted violation-rate direction. The A3 conversion rewrite is the exception — it fixed the statistical error and introduced two new arithmetic defects (below).

Four round-2 concerns were knowingly **left open** and all three reviewers found them again, independently: the three unlabelled experimental arms, the buried event-level operating point, the same-department "independent" dataset, and the NUWiNS framing. They should not be treated as new information.

What follows separates **(N)** new, **(O)** known and open, and **(R)** regression introduced by the last revision.

---

## Common concerns — raised by two or more reviewers

### A. **(R)** Two arithmetic defects introduced by the A3 rewrite — verified

Both are confirmed against the pipeline and both are mine, not the reviewers' misreadings:

1. Contribution 6 reads "the loose episode rule lets 2,361 episodes claim **1,647 of 957** commands" — a fraction whose numerator exceeds its denominator. It is meant to say that 1,647 *episode claims* fall on a corpus of 957 commands, i.e. the multiplicity statement, and it does not say that. (delta, foxtrot)
2. Table 5.12's multiplicity rows print "**×650.00 inflation**" and "**×927.00 inflation**". The intended values are ×2.59 and ×4.84. Cause confirmed: the table builder reads the inflation factor by tuple position, and two columns were added to the source table between the builder being written and the table being regenerated, so it now prints *commands owned in total*. (delta, echo, foxtrot)

delta's framing is the one that matters: "Section 5.9's thesis is that a rate quoted without its unit is a statement about bookkeeping and not about the network. The section demonstrating that thesis contains four bookkeeping errors."

### B. **(O)** The three experimental arms are still unlabelled (3/3)

0.179 / 0.160 / 0.157 for the same described estimand; logistic regression 0.130 in Table 5.4 and 0.167 in Table 5.5; the reordering claim true only in the latter. This is the single most-repeated finding across rounds 2 and 3 — six of six reviewers — and it is the open item I had queued and not yet done. echo adds a point the round-2 panel missed: the abstract's 48 % is 0.236/0.160, so attaching it to 0.179 implies a random-row value of 0.265 that appears nowhere.

### C. **(O)** Expected calibration error, and the 0–4 per-campaign reversal (3/3)

0.012 / 0.036 / 0.024, and the hazard arm losing on all four campaigns while winning pooled. Unchanged from round 2 and unaddressed. delta adds that the operational gloss ("probability near 0.8 … 80 % of occasions") is unsupported because no reliability-bin counts are shown and it is not established that any row scores near 0.8 at a 6.8 % prevalence.

### D. **(N)** The lag confounds leakage with information loss — the panel's most valuable new finding (echo, foxtrot)

Both reach it independently. The repair lags **every** export feature by one row, but the mechanism in Eq. (5.1) is specific to the *serving-cell identity register*. Nothing shows that RSRP, RSRQ, SINR or speed in row *t* are post-hoc in the same way. So 0.600 → 0.179 measures the cost of a conservative repair, not the cost of the leak, and the paper presents it as the latter in the abstract, contribution 1, §5.1, §5.11 and §7.1.

The missing arm is cheap and decisive: keep row *t*, lag or rebuild only the cell-identity-derived features (serving PCI, dwell, PCI-change indicators), report the three-way comparison. foxtrot: "0.179 is a lower bound on achievable performance and 0.421 is an upper bound on the leak, and the true leakage cost is somewhere between." This changes what the paper concludes about whether handover is predictable at all, and it is the one experiment I would run before anything else.

### E. **(N)** The conformal guarantee certifies a row-level quantity while the text promises an event-level one (foxtrot; echo and delta on the feasibility floor)

foxtrot alone identifies this, and it is the deepest technical finding of the round — distinct from, and more consequential than, round 2's estimand objection. §1.3(iv), contribution 5 and §7.1 all promise "a stated bound on **the fraction of handovers it will miss**." What §4.10 certifies is a set of *rows* per unit. Because only 64.6 % of commands have any usable row in the one-second window, 35.4 % of events cannot enter the loss at all, so a certified row-miss rate of 0.168 is consistent with an event-level miss rate above 35 % — and Table A.2 indeed reports 66 % event-level misses at 1 s. Table 5.7 and Table A.2 are the same system in different units and are never reconciled.

foxtrot also notes the printed loss is an unnormalised cardinality with an unclosed brace, not a bounded risk with B = 1, and that Eq. (4.10) is missing from the numbering — suggesting a deleted normalisation step. All three reviewers separately flag the α = 0.05 row printed below the paper's own feasibility floor with a 100 % compliance figure computed over rotations that cannot express it.

### F. **(O)** No measured operating point supports the stated motivation (3/3)

34.0 % detection, 179 false alarms/hour, 0.47 s median lead at 1 s — against §2.8's own imported criterion (Deb et al.) that 200 ms of lead "buys nothing." foxtrot presses hardest and adds a contradiction I had not seen: Appendix A's prose says Table A.2 reports "the certified operating point of Section 5.5" while the table's own caption says "the 5 % false-positive operating point," and those cannot both be true since §5.5's thresholds alarm on 36–86 % of rows. foxtrot and echo both note the detection rate is non-monotone in horizon (34.0 % at 1 s → 33.6 % at 2 s) while the ceiling rises, which is unexplained.

### G. **(N)** The re-establishment rate threatens the ground truth (delta, foxtrot)

341 re-establishments against 957 commands in 2.9 hours, 321 of them `reconfigurationFailure` — one per 2.8 handover commands. §5.8 then censors "the 93 rows whose next event is a re-establishment," which cannot be reconciled with 341 events. delta's inference is the serious one: if a material share of the 957 reconfigurations were never applied, then "command issued at τ" is not "handover occurred," and the event set underlying every AUPRC, ping-pong rate and conversion rate is of uncertain composition — *and the alignment mechanism itself assumes the handover completes inside the second.* The per-campaign spread (159 in 60 min on 13 Sept, 5 in 42 min on the highway) is unremarked.

This was not raised in round 2 by anyone. It deserves a direct answer: how many of the 957 have a decoded `RRCConnectionReconfigurationComplete`, and does the analysis hold when the others are dropped?

### H. **(O/N)** Novelty framing: the screen misses a literature and carves out the nearest system (3/3)

Round 2 raised the Prognos exclusion and the leakage-class attribution. Round 3 adds something new and harder: delta shows the screen returns **no pre-2020 work at all** and misses the cell-sojourn-time / handover-rate literature that models exactly the survival function this paper estimates. The defensible claim — *learned, covariate-conditional, per-sample* hazards on *measured* mobility data, against analytical marginal distributions — is narrower than "has not been directed at mobility data" and is not what §2.5, §2.9 and contribution 4 currently say.

All three also note that Appendix D row 9 (Amirova et al.) is recorded as real-measured with a device-level hold-out and a PR curve, which contradicts "0/22" on two rows of Table 2.1, and that reference [36] (Kaufman, on leakage) sits in the bibliography uncited in a paper about leakage.

### I. **(O)** Table 3.1 does not sum, and the external validation is not external (3/3, both)

Table 3.1 prints the top 6 A3 profiles and top 5 non-A3 rows of a table that does sum to 957, so the printed rows total 907 and the A3 rows 648 against a stated 651. The truncation is never declared. delta adds that §2.2 and §3.5 attribute the whole 75 % to the +1 dB profile alone, which is 472/651 = 72.5 %.

On external validity, all three repeat round 2's finding and two add that *both* arms of Table 5.9 are signalling-only, so the primary model — the radio and mobility blocks, 100 of 112 features — has never been externally tested at all, and that the promised comparator reimplementation is absent from §5.11 and Table 5.15.

### J. **(O)** Reproducibility: five feature counts, broken citation numbering, nothing released (3/3)

152 / 112 / 106 / 107 / 120. Seeds five or three. Distance 78 km or 95 km (both echo and delta derive ~96 km from the data and conclude §3.6 is wrong). Citation numbering off from [18] onward, with [18] denoting two different works in adjacent sections. "Planned" in both release rows of a table that grades 22 other papers on exactly that.

### K. **(N)** Statistical treatment: differences of 0.005–0.012 carry conclusions, with no interval (delta, foxtrot)

Tables 5.4, 5.5, 5.10, 5.11, 5.15 and A.1 carry no uncertainty at all, yet conclusions rest on differences well inside the per-campaign spread the paper itself reports (0.132–0.233 across campaigns against a quoted bootstrap interval of width 0.045). foxtrot adds that the tuning protocol — 20 trials × 7 learners × 4 protocols × 4 folds × 3 seeds — has no selection accounting, on ~584 positive rows.

### L. **(N)** Two of the formulation's advantages are inert on this data (echo, foxtrot)

§4.1 argues censoring must be modelled; §4.4 states "no row is censored inside the horizon grid." The censoring-aware likelihood therefore does nothing here, yet "inherits the censoring treatment of Section 4.4" is still listed in §5.4 as one of the two surviving advantages. And the hazard arm's own AUPRC (0.157) sits *below* the raw independent control (0.158) in Table 5.6. After the paper's own concessions, contribution 4 reduces to "coherence from one fit with no held-out split" — a convenience argument, which the abstract does not say.

### M. **(N)** The ping-pong "lever" claim is about a parameter the study never varied (delta, foxtrot)

§3.5 establishes the configuration set is stable across all four campaigns — there is no TTT or offset variation anywhere in the data — yet §5.10 concludes the lever is "the time-to-trigger and offset," and §7.3 hardens this to "having ruled out speed as the driver" while the table beneath shows the *fastest* campaign has the *highest* ping-pong rate. foxtrot adds that the Hawkes analysis is offered as corroboration but says nothing about TTT or offset, and that its branching ratio is interpreted physically from a kernel the paper's own Ogata residual test rejects.

delta also finds a new arithmetic problem: Table 5.14's carrier strata imply 218 ping-pongs (22.8 %) while its regime strata imply 252 (26.3 %) on the same fixed command set.

---

## Unique concerns

- **foxtrot — the conformal estimand mismatch** (E above). The single most technically consequential finding of this round.
- **delta — the pre-2020 blind spot and the cell-sojourn-time literature** (H above). Changes what contribution 4 can claim.
- **echo — the n = 15 falsification test is the δ-gradient counted twice.** "With x ≈ 60–105 ms, `m < 0` requires δ > ~0.9, so the 15 handovers are by construction the latest-arriving ones, which the δ-gradient already shows are least contaminated. The two predictions are one prediction counted twice." Round 2 questioned whether 15 was the right *count*; echo questions whether the test is *independent evidence* at all. It is the sharper objection.
- **echo — the A3 baseline is handicapped by the defect being audited.** The deployed rule runs on L3-filtered measurements at full rate with a 320 ms TTT; scoring it from the *lagged 1 Hz export* is a degraded reconstruction, degraded in the same direction as the headline effect. Also: a boolean rule has no ranking, so how AUPRC 0.116 and AUROC 0.689 arise is never specified.
- **delta — Table 3.2's sample counts are exactly 180 × block count for every campaign**, so no block was dropped by quality control, contradicting the 957 → 938 explanation; and the durations are exact multiples of 180 s, which is implausible for continuous field logging.

---

## Ranking of reviewers

1. **foxtrot** — the conformal estimand mismatch is a genuine technical error that two prior panels and I all missed, and the operating-point analysis is the most complete treatment anyone has given it, down to catching that Appendix A and the table caption name two different operating points.
2. **echo** — fewer findings, but the selective-lag ablation is the one experiment that would most change what the paper concludes, and the "one prediction counted twice" reading of the falsification test is the sharpest single sentence in the round. Its belief-update section is unusually candid about what did and did not land.
3. **delta** — the broadest verification and the only reviewer to reach the pre-2020 literature and the re-establishment threat to ground truth. Ranked third only because its verdict leans on defects that are bookkeeping rather than science; its two unique findings are as valuable as anything above.

The spread is narrow.

---

## Verdict synthesis

**Major revision**, with one dissent to Reject that should be taken seriously rather than averaged away.

delta's Reject is reasoned and its grounds are real — but every item in its verdict sentence is either a labelling fix, a truncated table, a generated-cell bug or a framing correction. None requires new data and none touches the measurement work. Two reviewers who found the *same* defects concluded Major revision, and delta's own opening says the audit "deserves publication." Weighing those together, the defensible reading is that the manuscript is not yet assessable rather than not publishable.

What actually changed this round: three of the four repaired items stayed repaired, one repair introduced two new arithmetic errors, and the panel surfaced four substantive findings nobody had reached before — the selective-lag confound, the conformal row-versus-event estimand, the inert censoring machinery, and the re-establishment threat to the event set.

Ordered by what it would cost to be wrong:

1. **Run the selective-lag ablation** (D). Until it exists, the paper's headline number is attributed to the wrong cause, and the field-wide recommendation may be wrong in detail.
2. **Resolve the conformal estimand** (E) — either re-run CRC with an event-level loss, which is what §1.3 promises and is still a bounded monotone loss, or restate §1.3, §1.6 and §7.1 in row-level language and reconcile Table 5.7 with Table A.2. Print the loss as a normalised bounded quantity and restore the missing equation.
3. **Answer the re-establishment question** (G) — how many of the 957 commands completed, and does anything change when the others are dropped.
4. **Fix the two regressions and label the arms** (A, B) — mechanical, and between them they account for most of delta's Reject.
5. **Then the framing corrections** (F, H, I, L, M) — operating point into the abstract, novelty narrowed to the claim the evidence supports, censoring advantage withdrawn, "lever" and "ruled out speed" withdrawn, Table 3.1 either completed or declared truncated.

The paper's own closing line — that on drive-test data the protocol and the timestamp semantics decide the result before the model does — is one every reviewer across three rounds has believed. The work left is to stop the manuscript being a counterexample to its own standard.

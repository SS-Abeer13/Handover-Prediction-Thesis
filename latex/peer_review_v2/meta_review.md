# Meta-Review (v2 — recompiled manuscript, 2026-09-23)

**Paper:** Conformalized Discrete-Time Hazard Modeling for Multi-Horizon Handover Forecasting in Cellular Networks
**Manuscript:** `latex/main.pdf` rebuilt from the .tex sources edited 09:04–09:12 UTC on 2026-09-23 (109 pages; md5 4082fbb9…)
**Reviewers:** alfa, bravo, charlie, delta (4 independent panelists)

## Per-reviewer verdicts

- **alfa** — Major revision: the audit methodology and honest negative results are publishable, but the headline 0.179 AUPRC is not itself shown to be free of residual leakage — Table 5.1's own row t−1 is still 15.6% contaminated overall vs 11.7% on isolated handovers, concentrated in the bursty regime that drives much of the lift.
- **bravo** — Major revision: the leakage-audit and protocol-comparison findings are valuable, but the novelty framing for conformal risk control and the survival formulation overreaches relative to adjacent literatures that were not searched, the "independent" validation is not arm's-length, and n = 4 campaigns cannot support the directional claims as worded.
- **charlie** — Major revision: the only claims to external generalization rest on a single retrospectively-contaminated, factor-confounded campaign and a same-lab "independent" dataset, and the headline risk-control result is framed more positively in the abstract than the body supports.
- **delta** — Major revision: the "held-out" campaign's independence, the O4 generalization claim and the causal mechanism test lean on post-hoc, same-sample or confounded evidence more than the abstract, contributions list and discussion acknowledge.

## Common concerns

1. **Campaign 4 is not a blind held-out test.** The one-row lag correction — the single decision that moves 1 s AUPRC from 0.600 to 0.179 — was derived after all four campaigns were in hand, including the one later reported as held out; the pre-registration freeze covers learner/hyperparameters but not the feature-construction decision with by far the largest effect.
   Raised by: **charlie, delta** (bravo raises the adjacent post-hoc-protocol point, see 5).
   Strongest formulation (charlie): *"The pipeline used to score the 'generalization' campaign was itself calibrated in part on that campaign's own contamination pattern. This is leakage into protocol design, not leakage into model fitting."*

2. **"Independent" external validation is a same-lab replication.** The public dataset [38] and RL comparator [39] share the supervisor, department, city, operator and XCAL instrument; the transfer uses only 6 of 112 features. Disclosed in §6.6, but the abstract, O4 and Chapter 1 still say "independent".
   Raised by: **bravo, charlie, delta** (alfa flags that the COI disclosure sits in Chapter 6, which is stripped for journal mode).
   Strongest formulation (delta): *"The thesis has essentially zero fully external evidence for generalisation beyond one lab's instrumentation and one operator."*

3. **O4 is declared "met" on a single campaign in which corridor and speed are fully confounded.** §5.12 states O4 is met (AUROC 0.769 on the highway) although §5.6/§5.13.2 concede the two factors are collinear; one observation cannot attribute the AUPRC drop (0.132 vs 0.196–0.233) to either.
   Raised by: **charlie, delta**.
   Strongest formulation (delta): *"Declaring the objective 'met' when the experimental design cannot isolate the manipulated factor is an overclaim."*

4. **"k of 4 campaigns" vote-counting reads as confirmatory evidence.** Phrases like "4 of 4 favour hazard" appear throughout Chapter 5 and the abstract while the n = 4 / p ≥ 0.125 caveat is confined to §5.13.4; campaigns are one operator's four author-chosen drives with no repeat-route replicate to estimate session-level noise.
   Raised by: **bravo, charlie, delta**.
   Strongest formulation (bravo): *"Four is not just 'underpowered' but essentially anecdotal for ranking purposes."*

5. **Evaluation thresholds chosen post hoc; git-internal freeze is not verifiable.** Block length 180 s, 60 s purge, 10 s burst cutoff, 2 s blanking and the lag itself were fixed after data collection; the freeze lives only in an internal repository; Table A.5 tests only local ±2× perturbations.
   Raised by: **alfa, bravo, charlie** (delta as part of concern 1).
   Strongest formulation (charlie): *"It is robustness to small perturbations of a data-informed choice, not evidence the choice itself was unbiased."*

6. **The 0/15 boundary-crossing "falsification test" is over-weighted.** n = 15 with a Wilson upper bound of 20.4%, run on the same corpus that generated the hypothesis; the residual 211-case "1-row refresh delay" refinement is validated only in-sample. The cross-instrument replications (4,712 XCAL handovers; NUWiNS start- vs end-of-second) are much stronger and should lead.
   Raised by: **alfa, delta** (bravo as a minor concern).
   Strongest formulation (delta): *"Framing this as evidence that 'falsifies' a competing account overstates what a same-sample, small-n check can show."*

7. **Code and data not available at review time.** Release is deferred to "on acceptance", and raw vendor logs will never be released — for a paper whose core contribution is a pipeline-level discovery, and whose decoding pipeline already had a history-changing bug (flat-union parser misclassifying 99.4% of reports as A3).
   Raised by: **alfa, bravo, charlie, delta** (delta as a minor concern).

## Unique concerns

- **Residual leakage at the corrected row (t−1) is never tested** — Table 5.1 shows 15.6% contamination at t−1 overall vs 11.7% for isolated handovers, concentrated in bursts where Table 5.13 still reports 1.9× lift. Recompute headline AUPRC on isolated handovers only, or run the margin/δ diagnostic on row t−1. *(alfa — the most specific, directly checkable threat to the headline number.)*
- **A3 baseline is a self-admitted weakened proxy** — it cannot see the time-to-trigger state; a TTT-window emulation from the recovered per-configuration TTT values (Table 3.1) is a cheap, stronger baseline. *(alfa)*
- **No second-device/firmware replication** — all campaigns use one XCAL handset; the "property of the aggregation rule, not a vendor" conclusion is untested across devices, and this is absent from §5.13/§7.2. *(alfa)*
- **Conformal novelty claim rests on an unaudited search** — §2.6 gives search strings but no screened/excluded counts (unlike the 108→22 audit in Appendix D); conformal-under-shift / weighted-conformal / adaptive conformal literature is neither cited nor tried as a remedy for the campaign-shift problem the paper presents as a "boundary result". *(bravo; alfa raises the same audit-asymmetry point, charlie the reverse asymmetry as a minor.)*
- **Discrete-time hazard via expanded-bin BCE is textbook in churn / predictive-maintenance / RUL literature**, uncited; §4.3–4.5 present a near-trivial monotonicity proof and a censoring likelihood later admitted "inert" as load-bearing. *(bravo)*
- **Abstract leads with a numeric conformal miss-loss (0.153 at α = 0.20)** before stating that no cross-campaign guarantee holds and that the per-handover estimand is inexpressible at 1 s. *(charlie)*
- **Multiplicity policy inconsistent** — Holm–Bonferroni applied only to the four Hawkes goodness-of-fit tests, nothing else. *(delta, minor)*

## Ranking

1. **alfa** — found the only concern that could move the headline number itself (residual t−1 contamination in bursts), grounded in the paper's own Table 5.1 with a concrete, cheap test, plus a stronger TTT baseline and the missing device-replication limitation.
2. **delta** — sharpest statement of the protocol-design leak into Campaign 4 and of the O4 overclaim, with the most actionable fix (re-run the pipeline on Campaigns 1–3 only and report both protocols).
3. **charlie** — covers the same Campaign 4 / O4 / independence ground as delta and adds the abstract-ordering problem for the conformal result and the local-only sensitivity analysis.
4. **bravo** — useful novelty-attribution critique (conformal-under-shift and discrete-hazard lineage) and the verified Table 3.2 caption error, but its concerns are about framing and positioning rather than validity of the results.

## Verdict synthesis

**Major revision** (unanimous, 4/4). The panel agrees the leakage/alignment audit and its cross-instrument replication are a real, unusually honestly reported contribution, and the revision since this morning has fixed several earlier issues (bootstrap-CI anti-conservatism is now caveated, the 12-rotation pseudoreplication is acknowledged in the abstract, reference TODOs are gone). What remains is a gap between framing and evidence: Campaign 4 is not blind to the pipeline's largest decision, "independent" validation is same-lab, O4 is declared met on one confounded observation, and "k of 4" language does confirmatory work it cannot bear. These are mostly fixable by rewording plus one or two cheap analyses. The one concern that could change the headline number — alfa's residual t−1 contamination in bursts — should be run before submission, because if isolated-handover AUPRC falls noticeably below 0.179 the abstract changes.

## Change vs. this morning's panel (v1, same day, pre-edit PDF)

- **Resolved or largely resolved:** block-bootstrap CI anti-conservatism (now caveated in §5.2/§5.13.4 and deferred to LOCO spread); "83% of 12 rotations" pseudoreplication (abstract now says the rotations "exhibit pseudoreplication across n = 4"); bracketed reference TODOs (none found in the new text).
- **Still open:** Campaign 4 not blind (now raised by 2 reviewers, was 2); same-lab "independent" dataset (now 3/4, was 1); O4 confound; internal-only freeze; Chapter 6 still in the build; count drift (Table 3.2 still captioned "after quality control" but its column sums to the raw 957).
- **New in v2:** residual t−1 contamination (alfa); TTT-emulating baseline; device replication; conformal-under-shift novelty gap; abstract ordering of the conformal result.

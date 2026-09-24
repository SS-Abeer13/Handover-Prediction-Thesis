# Meta-Review

**Paper:** Conformalized Discrete-Time Hazard Modeling for Multi-Horizon Handover Forecasting in Cellular Networks
**Reviewers:** alfa, bravo, charlie, delta (4 independent panelists)

## Per-reviewer verdicts

- **alfa** — Major revision: the alignment-audit contribution is strong, but the primary predictive and risk-control numbers are defended with confidence intervals the paper's own Section 5.3 analysis shows to be anti-conservative when applied to this data's block structure, and that inconsistency must be resolved before the quantitative claims can be taken at face value.
- **bravo** — Major revision: the leakage-audit contribution and the honesty about negative results are genuinely valuable, but the held-out campaign is not actually blind to the pipeline's defining preprocessing decision, key generalisation and risk-control claims rest on confounded or pseudo-replicated evidence from only four independent units, the causal mechanism behind the central correction is unconfirmed on the paper's own instrument, and the manuscript still contains submission-readiness defects.
- **charlie** — Major revision: the core contribution (the alignment audit and the honest, self-correcting statistical posture) is genuine and unusually rigorous for this scale of study, but the inconsistent application of the authors' own uncertainty-quantification standard to the headline result and the pseudoreplication in the cross-campaign conformal evaluation must be fixed before the reported precision of the central claims can be trusted.
- **delta** — Major revision: the underlying leakage/alignment audit is a genuinely valuable and unusually honest methodological contribution, but the statistical treatment of uncertainty is internally inconsistent, and the conformal risk-control result's "83% of 12 rotations" statistic is presented with more inferential weight in the abstract than four independent campaigns can support.

## Common concerns

1. **Block-bootstrap confidence intervals are internally inconsistent with the paper's own findings.** The headline AUPRC/AUROC/ECE intervals in Tables 5.4–5.5 are computed with the same 180-second block-bootstrap procedure that Section 5.3/5.4 independently proves to be anti-conservative on this data (block-splitting itself inflates one-second AUPRC by 13%), and Section 5.4 explicitly withdraws a paired-comparison claim on that basis — but the identical mechanism is left unflagged everywhere it produces the paper's most-cited number.
   Raised by: **alfa, charlie, delta**.
   Strongest formulation (charlie): *"If the block bootstrap is not trustworthy for testing a hazard-vs-control difference, it is not trustworthy for characterizing uncertainty in the headline AUPRC either — the same non-independence applies to both."*

2. **The conformal risk-control "83% of 12 rotations" statistic pseudoreplicates four independent campaigns as if they were twelve.** Because every rotation reuses one of only four campaigns as calibration or test set, the twelve outcomes are correlated through shared campaign identity, so the reported percentage carries a resolution the underlying data cannot support — and does so in the abstract and conclusion, not just deep in Section 5.5.
   Raised by: **alfa, bravo, charlie, delta** (unanimous).
   Strongest formulation (delta): *"'83%' is a descriptive tally over highly dependent outcomes, not evidence of coverage frequency in any statistical sense — it cannot be interpreted as an empirical false-coverage rate the way the abstract's phrasing invites a reader to do."*

3. **The held-out campaign is not a genuinely blind generalization test.** The one-row alignment/lag correction that defines the entire feature pipeline was derived by pooling contamination evidence across all four campaigns — including the campaign later reported as "held out" for the leave-one-campaign-out evaluation — so what survives as a clean test is the model's hyperparameters, not the measurement pipeline that determines what the model sees.
   Raised by: **alfa, bravo**.
   Strongest formulation (bravo): *"A skeptic should ask: would the audit have concluded 'lag by exactly one row' if only Campaigns 1–3 had been available? The paper does not show this."*

4. **Small-subgroup point estimates are reported without uncertainty, at odds with the paper's own cautious standard elsewhere.** Percentages computed on subgroups as small as n=15 (the boundary-crossing falsification test) or n=93–291 (various contamination and feature-block breakdowns) are stated to one decimal place as if exact, while the same thesis explicitly refuses significance testing at n=4 campaigns.
   Raised by: **alfa, charlie**.

5. **Reference list contains unresolved bibliographic placeholders.** Multiple entries carry literal editorial TODOs — incomplete author lists, unconfirmed DOIs/venues/volume-page ranges — inconsistent with a submission-ready manuscript, and one of them ([38]) underlies the Section 5.7 generalization claim.
   Raised by: **alfa, bravo, charlie, delta** (unanimous; flagged as a minor/administrative issue by all four, not a major concern in itself).

6. **Chapter 6 (Outcome-Based Education mapping) is capstone-accreditation boilerplate with no place in a journal submission.** All four reviewers independently flagged this chapter, and the associated appendices, for removal before any journal-track version of the manuscript.
   Raised by: **alfa, bravo, charlie, delta** (unanimous minor concern).

7. **Handover/event counts drift across chapters without consistent flagging.** The raw decoded count (957), the quality-controlled count (938), and further per-horizon counts (934–937) are used somewhat interchangeably across tables and prose.
   Raised by: **alfa, bravo, delta**.

## Unique concerns

- **alfa** — The claim that no prior wireless conformal-prediction study addresses a mobility-management case rests on an unspecified, undocumented literature screen, unlike the transparent 108→22 screen the same thesis uses for the handover-prediction literature in Section 2.3.
- **bravo** — The "freeze" of modelling decisions prior to the held-out campaign is attested only by the authors' own private version history, with no independent or third-party timestamp.
- **bravo** — The generalization claim (Objective O4) confounds corridor and speed regime, since the held-out campaign differs from the others on both axes simultaneously — a confound the thesis itself explicitly acknowledges for a different analysis (ping-pong) but not here.
- **bravo** — The two external-validity checks (the "independent" public dataset and the RL comparator baseline) share supervisor, department, instrument, and operator lineage with the primary study, which sits uneasily with "independent collection" language used in headline text.
- **bravo** — The causal mechanism proposed for the alignment defect (end-of-second export aggregation) is validated only on external, downsampled corpora and never confirmed on a native-rate re-export of the actual campaigns being predicted on.
- **bravo** — A stated 90.5% event-resolvability ceiling is never reconciled with a different, materially lower 64.2% eligible-prediction-window figure used elsewhere for what appears to be the same underlying 1 Hz sampling limitation.
- **charlie** — LightGBM is designated the "primary model" from a seven-learner comparison whose confidence intervals mostly overlap, with no stated pre-registration of that choice, risking winner's-curse-style optimism in the headline effect size.
- **charlie** — The blocked+purge splitting protocol is recommended as a practical leave-one-campaign-out substitute even though the paper's own sensitivity analysis (Table A.5) cannot establish the direction of its bias relative to LOCO.
- **charlie** — No multiplicity correction is applied to the large number of full-dataset comparisons (splitting windows, cutoffs, definitional grids), conflating this with the separate and valid argument that no correction is informative at the n=4-campaign level.
- **delta** — The internal hyperparameter-tuning split is drawn from within the same three training campaigns used for the final fit rather than a fourth independent unit, so tuning may leak training-campaign idiosyncrasies that the leave-one-campaign-out rotation cannot detect.

## Ranking

1. **charlie** — Most systematically exposes internally inconsistent statistical standards across multiple parts of the paper (bootstrap CI misuse, conformal pseudoreplication, post-hoc primary-model selection, unaddressed multiplicity, deferred reproducibility) with precise textual anchors in each case; broadest coverage of concerns that go to the core validity of the headline numbers.
2. **delta** — Independently converges on the same bootstrap and pseudoreplication flaws as charlie via a different reading of the text, and contributes one genuinely new, non-overlapping concern (internal tuning-split leakage) that no other reviewer identified.
3. **bravo** — Raises the single most structurally consequential critique in the panel (the held-out campaign is not blind to the pipeline-defining alignment correction) and layers on five further largely non-overlapping design concerns (freeze provenance, confounded regime, COI-adjacent external validity, unconfirmed causal mechanism, scope-figure mismatch); very high per-concern novelty, somewhat less tightly focused on the statistical core than charlie or delta.
4. **alfa** — Corroborates the two most-repeated concerns in the panel (held-out contamination, bootstrap-CI inconsistency) and adds one genuinely novel point (the undocumented literature-screen claim), but contributes comparatively less new ground once bravo's and charlie/delta's findings are on the table.

## Verdict synthesis

**Major revision.** All four reviewers reached this verdict independently and there is no disagreement to arbitrate. Two systemic issues were found by every reviewer working from the paper text alone and via different routes: the block-bootstrap confidence intervals attached to the headline AUPRC/AUROC/ECE figures use exactly the resampling procedure the thesis's own Section 5.3/5.4 shows to be anti-conservative on this data, and the cross-campaign conformal result ("83% of 12 rotations") pseudoreplicates outcomes from only four independent campaigns while being reported with the rhetorical weight of a validation statistic. Both are fixable without new data collection — by re-expressing uncertainty using the 4-campaign spread the paper already reports honestly elsewhere (e.g., Table 5.10), consistent with the standard the authors apply to themselves when they withdraw the Section 5.4 paired-comparison claim. The next most serious issue, raised independently by two reviewers, is that the leave-one-campaign-out evaluation's "held-out" campaign is not blind to the alignment-audit correction that defines the entire feature pipeline, since that correction was derived from evidence pooled across all four campaigns; this weakens, without invalidating, the paper's generalization claim and should be either reframed or re-tested with the pipeline frozen on three campaigns only. None of the panel disputes that the alignment-audit finding itself — the discovery that a one-hertz export artifact inflates apparent AUPRC by more than 3× — is a genuine, well-corroborated, and independently valuable contribution; the consensus is that the predictive and risk-control claims built on top of it are currently defended with more statistical confidence than the paper's own n=4-campaign evidence base, by the paper's own logic, supports. Administrative issues (unresolved reference placeholders, the accreditation-chapter content) are unanimous but straightforward to fix before any journal submission.

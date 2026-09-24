# Synthesis Meta-Review: Leakage-Audited Multi-Horizon Handover Forecasting from LTE Drive-Test Signalling

## Per-reviewer verdicts
- **alfa** — **Major revision**: The manuscript provides an outstanding methodological audit of temporal leakage and split-induced inflation, but requires substantial revisions to resolve anti-conservative block-bootstrap variance estimation, correct for multiple testing, address conformal risk breakdown under covariate shift, and repair mathematical notation errors.
- **bravo** — **Major revision**: While presenting an exemplary and devastatingly honest audit of data leakage in cellular telemetry, major revisions are necessary to eliminate pseudo-replication in bootstrap uncertainty estimates, reconcile contradictory calibration findings between pooled and per-campaign metrics, restore missing appendix data, correct equation labeling errors, and align contribution claims with the empirical limits of conformal risk control.
- **charlie** — **Major revision**: While the timestamp alignment audit is a triumph of scientific integrity, the manuscript requires major revisions to eliminate its reliance on cherry-picked qualitative examples, replace the administrative OBE checklist in Chapter 6 with genuine trace-level case studies of model successes and false alarms, provide physical evidence for the delayed-refresh residual, and temper claims regarding practical real-time deployability.

## Common concerns

1. **Pseudo-replication and anti-conservative confidence intervals from within-campaign block bootstrapping**
   - *Reviewers*: **alfa**, **bravo**
   - *Description*: Resampling 180-second blocks within continuous campaigns to compute 95% confidence intervals and paired difference tests ignores strong temporal and spatial autocorrelation, deflates standard errors, and generates false claims that intervals 'exclude zero' despite previously proving that 180-second blocks are statistically dependent.
   - *Strongest quote (bravo)*: "In Section 3.4 and Section 5.3, the authors establish that 180-second segments of a single continuous drive session share trajectory, radio environment, and cell sequences, showing that treating them as independent units inflates AUPRC by up to 13% to 48%. Yet, in Section 5.4 (Table 5.6b), the authors construct 95% confidence intervals for paired differences between models ... by resampling these exact 180-second blocks. This is classical pseudo-replication."

2. **Severely underpowered sample size ($N=4$ sessions) and uninformative cross-campaign inference**
   - *Reviewers*: **alfa**, **bravo**, **charlie**
   - *Description*: With only four continuous driving sessions comprising 2.9 hours of driving, formal hypothesis testing across campaigns is impossible (minimum two-sided sign-test p-value is 0.125), and model metrics fluctuate heavily across routes (e.g., a 43% drop from Urban Loop to Highway).
   - *Strongest quote (charlie)*: "While the authors commendably recognize that adjacent 180-second blocks are not independent and enforce leave-one-campaign-out (LOCO) as the only sound unit, having N=4 independent units means the minimum attainable two-sided sign-test p-value is 0.125. ... With only four points, an informed reader cannot determine whether this spread represents random variance across corridors, driver habits, or time of day."

3. **Multiplicity, post-hoc pipeline tuning, and unadjusted multi-hypothesis comparisons**
   - *Reviewers*: **alfa**, **bravo**, **charlie**
   - *Description*: Running 1,680 fits per protocol across 7 learners, 5 horizons, multiple feature subsets, and post-hoc heuristics (180s blocks, 60s purge, 10s burst cutoff) without family-wise error control risks substantial Type I error inflation and overinterprets marginal metric differences.
   - *Strongest quote (bravo)*: "The experimental search space spans 20 trials across 7 learners, 4 folds, and 3 seeds (1,680 fits per protocol) ... Reporting LightGBM as the leading model over MLP and TCN without multiple-comparison adjustment overinterprets differences that lie entirely within mutual confidence bounds. Moreover, Section 3.2 admits that the alignment audit and feature lagging ... were conducted after all four campaigns were collected."

4. **Breakdown of distribution-free conformal risk guarantees under cross-campaign shift and grid discretization**
   - *Reviewers*: **alfa**, **bravo**, **charlie**
   - *Description*: Framing distribution-free conformal risk control as an accomplished primary contribution overstates practical utility, since exchangeability fails across driving corridors (violating nominal bounds in 17%–33% of rotations), and 36.4% of handovers lack valid sample rows due to 1-Hz quantization.
   - *Strongest quote (bravo)*: "Contribution 5 and Objective O3 promise a distribution-free risk guarantee for handover warning. However, as Table 5.7 documents, under cross-campaign deployment ... the empirical miss rate violates the nominal bound in 17% to 33% of rotations because drive-test sessions violate the fundamental exchangeability assumption. More critically, at the 1-second horizon, 36.4% of handover commands lack a valid sample row within their lead window due to 1-Hz sampling grid quantization, rendering finite-sample risk bounds for event-level loss completely inexpressible."

5. **Operational unviability of proactive target-cell preparation under 1-Hz telemetry**
   - *Reviewers*: **bravo**, **charlie**
   - *Description*: The narrative claims advance warning enables proactive target-cell preparation, but at the 5% false-positive operating point the model detects only 34% of handovers while incurring 179 false alarms per hour (one every 20 seconds) with a median lead time of just 0.47 seconds.
   - *Strongest quote (charlie)*: "Section 1.2 claims that 'a warning one second ahead of a handover command is sufficient time for the network to complete target-cell preparation.' However, Figure 5.2 and Table A.2 reveal that at the 5% false-positive rate operating point, the model achieves a detection rate of only 34% at 1 second while generating 179 false-alarm episodes per hour—an alarm every 20 seconds of driving—with a median lead time of just 0.47 seconds."

6. **Survival formulation provides no empirical advantage over simple monotonic projections on independent heads**
   - *Reviewers*: **alfa**, **charlie**
   - *Description*: The discrete-time survival formulation is presented as an essential architectural breakthrough for horizon coherence, yet empirical controls prove that simple cumulative-maximum or PAV post-processing on independent heads achieves identical coherence and AUPRC at zero cost, while the censoring loss term is completely inert.
   - *Strongest quote (charlie)*: "The survival framing (Equations 4.2–4.5) is mathematically elegant, but Table 5.6 demonstrates that a simple two-line cumulative-maximum projection (independent + cumulative max) or Pool Adjacent Violators (independent + PAV) on standard independent binary classifiers also reaches exactly 0.0% ordering violations, identical 1-second AUPRC ... Posing the hazard formulation as a foundational advantage over independent heads overclaims its actual empirical utility."

7. **Duplicated and corrupted equation tags, malformed expressions, and dead cross-references**
   - *Reviewers*: **alfa**, **bravo**, **charlie**
   - *Description*: Chapter 4 duplicates Equations (4.9) and (4.11), contains a dangling unnumbered equation on line 253, and repeatedly references non-existent Section 3.7.
   - *Strongest quote (bravo)*: "In Chapter 4, Equation (4.9) is assigned twice (line 237 and line 243); Equation (4.11) is assigned twice (line 248 and line 260); line 253 contains a dangling, unnumbered expression ... and Chapter 4 (line 21) and Chapter 5 (line 275) both refer to 'the row filter of Section 3.7', but Chapter 3 terminates at Section 3.6."

## Unique concerns

1. **Contradictory calibration error statements between pooled and per-campaign metrics, and missing Appendix A data**
   - *Reviewer*: **bravo**
   - *Description*: Section 5.4 asserts that the hazard arm has lower calibration error on 0 of the 4 individual campaigns, directly contradicting the pooled paired difference in Table 5.6b, while the promised per-campaign calibration breakdown in Appendix A is missing and ECE values (0.012, 0.036, 0.024) conflict across chapters.

2. **Absence of qualitative trace-level error analysis and repurposing of Chapter 6 as an administrative OBE checklist**
   - *Reviewer*: **charlie**
   - *Description*: The paper motivates handover physics with a single idealized trace (Figure 1.1) and provides an unverified assertion for the 22.5% unaligned residual, while Chapter 6 (titled Demonstrative Case Studies) contains zero qualitative case studies of True Positives, False Positives, or False Negatives, having been repurposed entirely as an administrative OBE checklist.

3. **Inconsistent reporting of branching ratio from a rejected, misspecified Hawkes process**
   - *Reviewer*: **bravo**
   - *Description*: The exponential-kernel Hawkes point process is formally rejected by Ogata time-rescaling residual diagnostics, yet the authors continue to cite its branching ratio (0.653) as a quantitative measure of clustering without reporting the Kolmogorov-Smirnov test statistic or p-value.

4. **Proprietary binary XCAL diagnostic logs restrict independent verification of ASN.1 parser timeline**
   - *Reviewer*: **charlie**
   - *Description*: While derived CSV files will be open-sourced, the raw proprietary binary captures (.xdl/.xcap) cannot be shared, preventing independent verification of the ASN.1 decoding timeline and the ~60 ms exporter latency estimation.

5. **Selection bias and base-rate confounding in quiet vs. burst row stratification**
   - *Reviewer*: **alfa**
   - *Description*: Partitioning rows into quiet and burst sets introduces survivor bias because every burst is initiated on a quiet row, and comparing AUPRC lift across strata with differing baseline prevalences (4.3% vs 11.2%) confounds precision-recall geometry with predictive power.

6. **Confounding RF propagation boundaries with intersection kinematics and timer cadence**
   - *Reviewer*: **charlie**
   - *Description*: The strongest features are time-since-last-A3 and serving SINR rather than neighbour overtaking gap, leaving open the alternative hypothesis that the model acts primarily as a timer of network cadence and vehicle deceleration at road junctions rather than forecasting RF propagation boundaries.

## Ranking
1. **bravo** — Provided the highest diagnostic value and deepest technical critique by uncovering an internal contradiction in Section 5.4 where the hazard arm was worse on 0 of 4 individual campaigns despite a pooled advantage, identifying missing Appendix A data, dismantling the rejected Hawkes branching ratio, and locating exact broken cross-references.
2. **charlie** — Provided exceptional adversarial insight by exposing that Chapter 6 was converted into an administrative OBE checklist rather than presenting actual qualitative case studies, demonstrating that simple cumulative-maximum projections match the survival model, and detailing the unviable operating frontier (179 false alarms/hour, 0.47s lead time).
3. **alfa** — Provided rigorous statistical grounding by exposing the anti-conservative block-bootstrap variance estimation, the lack of family-wise error rate corrections, and the survivor bias in quiet vs. burst row stratification.

## Verdict synthesis
The consensus across all three reviewers is an unequivocal **Major revision**. The manuscript's forensic deconstruction of temporal alignment leakage (accounting for 96% of unlagged predictive lift) and data-splitting inflation (+48% under random-row CV) represents an outstanding, highly publishable contribution to cellular communications and machine learning methodology. However, the thesis currently undermines its own rigorous ethos through internal contradictions: it relies on autocorrelated block-bootstrapping to claim statistical significance where $N=4$ clusters lack power; it asserts calibration improvements that reverse at the campaign level; it overclaims proactive warning feasibility despite an operating reality of 179 false alarms per hour and 0.47 s lead time; it frames conformal risk control as a primary contribution despite a 33% empirical failure rate under distribution shift; and it omits true qualitative case studies in Chapter 6. Addressing these issues will transform the thesis into a landmark methodological reference for mobile computing.

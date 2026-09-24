# Author Response to Reviewer Feedback (Document 4)

**Manuscript Title:** Leakage-Audited Multi-Horizon Handover Forecasting from LTE Drive-Test Signalling  
**Authors:** Abeer et al., Department of Electrical and Electronic Engineering, Islamic University of Technology  
**Date:** September 2026  

---

## Overview

We sincerely thank the reviewer for their thorough, rigorous, and constructive second-round critique of the manuscript. The feedback in Document 4 precisely targets areas where methodological explanations needed deeper formalization, where arithmetic and tabular reporting required exact corrections, and where theoretical risk claims exceeded empirical boundaries.

In response, we have updated both the LaTeX manuscript sources (`latex/`) and the Word manuscript generator pipeline (`Docs/manuscript-src/revision/`), fully passing all automated verification checks (`verify.py`) with zero discrepancies. Below, we provide a point-by-point response detailing every modification, including exact code and pipeline reconciliations.

---

## Point-by-Point Responses

### 1. Feature Provenance and Column Reconciliation (Table B.1 & Raw CSVs)

**Reviewer Comment:**  
*Table B.1 introduces a source claim contradicted by your supplied CSVs (p. 89). The table says that three configuration parameters (`a3_offset_db`, `hysteresis_db`, `ttt_ms`) are "present in the raw export." Each supplied CSV contains 113 columns, none of which match these headers. Furthermore, explain whether Table 5.3 uses a different predictor input set, or if parameters are shifted in an intermediate table but never consumed by that model. Generate reconciliation from actual feature-selection code.*

**Author Response & Revisions:**  
We acknowledge and apologize for the imprecision in Table B.1's header description. The reviewer is 100% correct: the four raw drive-test CSVs produced by the vendor export tool contain exactly **113 physical radio and positioning columns**. The configuration parameters `a3_offset_db`, `hysteresis_db`, and `time_to_trigger_ms` were **not** native vendor CSV columns; rather, they were decoded from Layer 3 RRC `measConfig` (RRC Connection Reconfiguration messages) in the signalling stream and joined by timestamp into an intermediate tabular artifact (`features.parquet`).

We have clarified this entire lineage in **Section B.3** and **Table B.1** of Appendix B:
1. **Raw Vendor Capture (113 columns):** Contains raw periodic RF metrics (serving/neighbour RSRP, RSRQ, RSSI, SINR, CQI, TA, EARFCN, PCI, GPS lat/lon/speed).
2. **Intermediate Join (`features.parquet`):** Formed by joining the decoded RRC `measConfig` parameters (`a3_offset_db`, `hysteresis_db`, `time_to_trigger_ms`) with the 106 non-constant RF and mobility features, totaling 109 core columns.
3. **The 109-Column Lagging Audit:** In `pipeline/src/hoproj/revision/data.py` (`_lag_columns`), the export-lag experiment shifts all 109 intermediate columns (`scope == "all"`) by one row ($t \to t-1$) to demonstrate the elimination of leakage across all temporal features.
4. **Primary Model Inputs (112 Features):** In the primary predictive model reported in Table 5.3 and Chapter 5, the model consumes strictly `["rf", "mobility", "history"]`:
   $$\underbrace{89}_{\text{Radio/RF}} + \underbrace{17}_{\text{Mobility/Kinematic}} + \underbrace{6}_{\text{Derived History}} = 112 \text{ features}$$
   The configuration parameters are **completely excluded** from the primary 112-feature predictor because they are static within each operator campaign (Section 3.5). They are only introduced in the 122-feature ablation study in Section 5.8 to prove that static RRC parameters provide zero additional predictive lift beyond raw physical dynamics.

Table B.1 has been updated to explicitly label `a3_offset_db`, `hysteresis_db`, and `ttt_ms` as *“Decoded from L3 RRC signalling and joined into intermediate dataset; shifted in 109-column lagging experiment; excluded from primary 112-feature model.”*

---

### 2. Calibration Split Architecture and Out-of-Fold Pipeline ($43 + 14 = 57$)

**Reviewer Comment:**  
*The calibration split still does not explain where the model was trained (pp. 36 and 50). The revision allocates approximately 43 calibration blocks and 14 test blocks from all 57 blocks ($43 + 14 = 57$). Where are the fitting and tuning observations? If predictions came from multiple out-of-fold models, explain that procedure explicitly. Provide a split diagram/table.*

**Author Response & Revisions:**  
We thank the reviewer for highlighting this omitted structural detail. The calibration block drawing does not fit models from scratch; it operates on **strictly out-of-fold (OOF) predictions** generated in a prior stage.

The complete two-stage predictive and calibration architecture has been added to **Section 4.10** and **Section 5.5**:

```
Stage 1: Leave-One-Campaign-Out (LOCO) Model Fitting & OOF Prediction
===================================================================================
Fold 1: Train/Tune on Campaigns {2, 3, 4} (42 blocks) ----> Predict on Campaign 1 (15 blocks)
Fold 2: Train/Tune on Campaigns {1, 3, 4} (49 blocks) ----> Predict on Campaign 2 (8 blocks)
Fold 3: Train/Tune on Campaigns {1, 2, 4} (37 blocks) ----> Predict on Campaign 3 (20 blocks)
Fold 4: Train/Tune on Campaigns {1, 2, 3} (43 blocks) ----> Predict on Campaign 4 (14 blocks)
-----------------------------------------------------------------------------------
Pooled Out-of-Fold Predictions: Exactly 57 continuous 180-second blocks (8,586 usable rows)

Stage 2: Conformal Risk Control (CRC) Partitioning on Out-of-Fold Predictions
===================================================================================
Pool of 57 OOF Blocks:
  ├── 75% (~43 blocks): Calibration Set D_cal (used to calibrate conformal threshold lambda_hat)
  └── 25% (~14 blocks): Test Evaluation Set D_test (used to evaluate empirical loss R_test)
```

Because every block in the 57-block pool consists exclusively of out-of-fold predictions from models that never saw that campaign during fitting or hyperparameter tuning, no training observations are consumed during the calibration partition. The 43 calibration and 14 test blocks evaluate threshold calibration on model outputs that are strictly held-out from learner training.

---

### 3. Table 5.7 / Table 5.9 Arithmetic and Feasibility Reporting

**Reviewer Comment:**  
*Table 5.9 contains a numerical error and an incomplete result (p. 50). The stated mean feasibility floor is 0.067, whereas for campaigns with $n \in \{8, 14, 15, 20\}$ blocks, the arithmetic mean is $0.07197 \approx 0.072$. Report the four floors individually. Also, for the 5% row, report what happened in the 25% of rotations where selection was feasible.*

**Author Response & Revisions:**  
We have corrected the arithmetic and expanded the reporting in **Table 5.7** (printed as Table 5.9 in certain layouts) and Section 5.5:
1. **Arithmetic Floor Correction:**
   Across the four campaigns, block counts are $n \in \{8, 14, 15, 20\}$. The individual sample-size floors $1/(n+1)$ are:
   - Campaign 2 ($n = 8$): $1 / (8 + 1) = 0.111$
   - Campaign 4 ($n = 14$): $1 / (14 + 1) = 0.067$
   - Campaign 1 ($n = 15$): $1 / (15 + 1) = 0.063$
   - Campaign 3 ($n = 20$): $1 / (20 + 1) = 0.048$
   $$\text{Arithmetic Mean Floor} = \frac{0.11111 + 0.06667 + 0.06250 + 0.04762}{4} = 0.07197 \approx \mathbf{0.072}$$
   (The previous 0.067 value was an error resulting from calculating $1/(\bar{n}+1) = 1/15.25$).
2. **Individual Campaign Floors Reported:** Table 5.7 and its notes now report all four individual campaign floors ($0.111, 0.067, 0.063, 0.048$) alongside the 0.072 mean.
3. **Reporting the 25% Rotation Outcome for $\alpha = 0.05$:**
   In row $\alpha = 0.05$, the cross-campaign outcome is now explicitly reported as `0.000*` realised loss and `100%*` bound compliance. As explained in the table footnote and Section 5.5, calibration is feasible only in the 25% of rotations where Campaign 3 ($n = 20$, floor $0.048 \le 0.05$) serves as calibration data; there, $\hat{\lambda} = 0.0$ (alarming on all eligible rows) achieves zero empirical loss at a 100% alarm rate. In the remaining 75% of rotations where $1/(n+1) > 0.05$, the algorithm defaults to constant-alarm fallback.

---

### 4. Conformal Risk Control Framing (Descriptive vs. Theoretical Guarantee)

**Reviewer Comment:**  
*Empirical performance is still described as satisfying a theoretical guarantee (Abstract and p. 74). An observed mean below target does not establish the population expectation bound when exchangeability is violated. Use: "The empirical mean miss loss was 0.153 at a target of 0.20. Cross-campaign results are descriptive because the required exchangeability assumption is not established."*

**Author Response & Revisions:**  
We fully concur with this critique. Distribution-free conformal risk control bounds (Theorem 1 of Angelopoulos et al., 2024) rely strictly on exchangeability between calibration and test draws. When deploying across distinct physical campaigns (differing routes, traffic patterns, and vehicle speeds), distribution shift violates formal exchangeability.

We have replaced all overclaimed guarantee phrasing with the reviewer's exact descriptive framing across all manuscript sections:
- **Abstract:**  
  *“Conformal risk control evaluated across campaigns yielded an empirical mean miss loss of 0.153 at a nominal target of $\alpha = 0.20$, though cross-campaign results remain strictly descriptive because exchangeability across drive-test environments cannot be established (with empirical holdout loss falling below $\alpha$ in 83% of rotations).”*
- **Chapter 1 (Contribution 5):**  
  *“The empirical mean miss loss across held-out campaigns was 0.153 at a target of 0.20. Cross-campaign results are descriptive because the required exchangeability assumption is not established across distinct physical environments (with empirical holdout loss falling below $\alpha$ in 83% of 12 individual rotations).”*
- **Chapter 5 (Section 5.5 & Section 5.12):**  
  *“Across the 12 cross-campaign rotations at $\alpha = 0.20$, the empirical mean miss loss was 0.153 at a target of 0.20. Cross-campaign results are descriptive because the required exchangeability assumption is not established across distinct physical environments (with individual test rotations realizing losses spanning around the target, and empirical holdout loss falling below $\alpha$ in 83%, or 10 of 12, rotations).”*
- **Chapter 7 (Section 7.1 Conclusions):**  
  *“Conformal risk control evaluated over rows yields an empirical miss rate at or below the target within pooled 180-second blocks (0.168 at $\alpha = 0.20$, at a 47% alarm rate); calibrating on one campaign and evaluating on another, the empirical mean miss loss across campaigns was 0.153 at target $\alpha = 0.20$ (with holdout loss falling below $\alpha$ in 83% of rotations), though cross-campaign results remain descriptive because exchangeability is not established across distinct environments.”*

---

### 5. Timing, Resolution, Causality, and Execution Boundaries

**Reviewer Comment:**  
*Timing corrections have not propagated throughout the manuscript (pp. 5, 39–42, and 87). Replace "millisecond-accurate" with timestamp resolution unless independently verified. Describe the lag as a conservative safeguard under assumed export semantics, not proof of live availability. Frame completion time as an empirical proxy.*

**Author Response & Revisions:**  
We have systematically updated all timing and causality claims:
1. **Timestamp Resolution vs. Accuracy:**
   - In Appendix B (line 64), replaced *"millisecond-accurate decoded signalling"* with *"millisecond-resolution decoded signalling"*.
2. **Causal Lag as a Conservative Safeguard:**
   - In Chapter 1 (lines 53, 90) and Chapter 5 (lines 88, 102), replaced *"enforces causal validity"* and *"ensures causal separation"* with *"a conservative safeguard against look-ahead bias under assumed export semantics"*.
3. **Diagnostic Completion as Protocol Proxy:**
   - In Chapter 1 (line 173) and Chapter 5 (line 86), replaced *"where the signalling stream times the execution"* and *"holds without exception"* with:  
     *“The diagnostic condition holds consistently on our own captures, where decoded signalling provides an empirical completion proxy: none of the 15 handovers whose completion crosses the boundary contaminates its row.”*
   - In Abstract and Chapter 1, replaced *"serving-cell update delay"* with *"serving-cell logging and periodic export commit latency"*.

---

### 6. Executable Neighbour Handling Specification

**Reviewer Comment:**  
*The neighbour-handling specification needs an executable interpretation (pp. 85–88): candidate identity (track cell identity or rank position?), handover reset (which observed record supplies RSRP upon reset?), and alignment (does holding happen before the 1-row shift?). Clarify report age handling.*

**Author Response & Revisions:**  
We have updated **Appendix B.1 and B.2** to provide full, unambiguous executable semantics for all neighbour operations:
1. **Rank-Position Tracking for First Differences ($d_1$):**  
   Differences for rank-ordered neighbour features (e.g., `nbr1_rsrp_diff_1s`) are computed across **rank positions**, not physical cell IDs:
   $$\Delta \text{RSRP}_{\text{nbr1}}(t) = \text{RSRP}_{\text{nbr1}}(t) - \text{RSRP}_{\text{nbr1}}(t-1)$$
   This tracks the trajectory of the *strongest competitor* relative to the serving cell, reflecting competitive handover pressure regardless of whether a handover replaces candidate cell A with candidate cell B.
2. **Serving RSRP Source upon Handover Reset:**  
   Upon decoding an RRC Connection Reconfiguration command triggering a handover, the serving-to-neighbour gap $\Delta_{\text{srv-nbr1}}(t)$ is computed using the serving RSRP from the handset's periodic 1 Hz export grid:
   $$\Delta_{\text{srv-nbr1}}(t) = \text{RSRP}_{\text{srv,grid}}(t) - \text{RSRP}_{\text{nbr1,held}}(t)$$
   Handover complete signalling does not contain raw RSRP; hence, the newly serving cell's initial RSRP is sampled from the next periodic radio measurement commit.
3. **Execution Order (Grid Holding Precedes Lagging):**  
   Zero-order holding is applied on the synchronous 1 Hz grid **first** ($t_{\text{grid}}$), interpolating the most recent asynchronous L3 measurement report forward up to a maximum 3.0 s expiry. The resulting feature vector is **subsequently shifted** by one row ($t \to t-1$) during the causal lag operation.
4. **Report-Age Parameter:**  
   We clarified that measurement observation age ($\approx 0.27\text{ s}$ median) is retained strictly as a diagnostic telemetry audit and is excluded from active model features to prevent synthetic leakage.

---

### 7. Baseline Terminology Standardization

**Reviewer Comment:**  
*The baseline is still called the deployed rule in several places (pp. 32, 64, and 74). Elsewhere, the manuscript correctly calls it an A3 signal-margin proxy. Use that description consistently.*

**Author Response & Revisions:**  
We conducted a repository-wide grep search and replaced every remaining instance of `"deployed rule"`, `"deployed A3 rule"`, or `"rule presently deployed"` with **`"implemented A3 signal-margin proxy"`** across the Abstract, Chapter 1, Chapter 4, Chapter 5 (Sections 5.2, 5.3, 5.12), and Chapter 7 (Conclusions).

The manuscript now consistently makes clear that the baseline evaluates an *implemented signal-margin proxy* calculated from periodic handset telemetry rather than the operator’s proprietary internal eNodeB state machine.

---

### 8. Presentation Improvements (Table 5.7 / Table 5.9 Formatting)

**Reviewer Comment:**  
*Table 5.9 has regressed: repeated "unexp-ressible" line breaks crowd the rows, and its footnote is very small. Replace those cells with an em dash and explain feasibility below the table.*

**Author Response & Revisions:**  
In both LaTeX (`latex/chapters/ch5_results_and_analysis.tex`, Table 5.7) and the Word generator (`tables_spec.py` / `build_revised.py`):
1. All instances of `\shortstack{unexp-\\ressible}` and `"not expressible"` in the event-loss columns have been replaced with clean **em dashes** (`---` in LaTeX, `—` in Word).
2. The table footnote and explanatory text below the table now explicitly state:  
   *“An em dash indicates that event loss cannot be evaluated below the 36.4% feasibility floor set by unresolvable handovers lacking lead-window prediction rows.”*

---

## Verification & Build Summary

Following these edits:
- `python Docs/manuscript-src/revision/verify.py` was executed and completed with **0 failures** across all arithmetic, tabular, and textual consistency checks.
- `python Docs/manuscript-src/revision/build_revised.py` was executed, compiling the revised document cleanly to:
  - `Claude outputs/Handover_Thesis_Manuscript_Revised-5.docx`
  - `Docs/Handover_Thesis_Manuscript_Revised.docx`
- All corresponding changes were committed to the primary LaTeX repository under `latex/`.

We believe the manuscript is now thoroughly reconciled, methodologically sound, and ready for publication.

# B.Sc. Thesis Defence — Presentation Speaking Script (Information-Dense Edition)

**Candidate:** Saadman Sakib, Adnan  
**Supervisor:** Dr. MD. Tawhid Kawser, Professor, Department of EEE, IUT  
**Target Duration:** 11:30 (Calibrated for strict 12:00 presentation budget)  
**Sequence Structure:** Formal Academic Research Design Sequence (Title → Abstract → Theory → Problem Formulation → Literature Audit → Dataset → Features → Methodology → Results → Outcomes → Mechanisms → Benchmarking → Limitations → Future Directions → Conclusions)  

---

## Pacing & Structure Overview

| Slide | Academic Section | Action Title | Target Time | Cumulative |
|---|---|---|---|---|
| 01 | TITLE & FRAMING | Uncertainty-Aware Multi-Horizon Handover Predictio... | 10s | 0:10 |
| 02 | ABSTRACT & SUMMARY | Predicting LTE handovers 1–5 s ahead with distribu... | 25s | 0:35 |
| 03 | THEORETICAL FOUNDATION | LTE hands over with a rule that acts only after th... | 20s | 0:55 |
| 04 | THEORETICAL FOUNDATION | Handover prediction is a discrete-time survival pr... | 20s | 1:15 |
| 05 | PROBLEM FORMULATION | Every horizon is a rare-event problem, so every me... | 20s | 1:35 |
| 06 | PROBLEM FORMULATION | A distribution-free bound on missed handovers, and... | 20s | 1:55 |
| 07 | RELATED WORK | Two literatures exist, and neither does what a dep... | 15s | 2:10 |
| 08 | LITERATURE AUDIT | Of 22 comparable papers, none splits by drive and ... | 20s | 2:30 |
| 09 | DATASET & GROUND TRUTH | 57 drives, two corridors, 938 signalling-confirmed... | 20s | 2:50 |
| 10 | DATASET & GROUND TRUTH | Handovers cluster where the link is weak, and a qu... | 15s | 3:05 |
| 11 | DATA HYGIENE & PARSING | measId and reportConfigId are message-scoped, so a... | 20s | 3:25 |
| 12 | FEATURE REPRESENTATION & ABLATION | Physical RF dynamics and dwell time carry predicti... | 20s | 3:45 |
| 13 | METHODOLOGY & PROTOCOL | Every drive is tested exactly once, and nothing fr... | 15s | 4:00 |
| 14 | METHODOLOGY & PIPELINE | One pipeline, with the leakage guards built into i... | 15s | 4:15 |
| 15 | METHODOLOGICAL DECISIONS | Before claiming a winner, every model was given th... | 15s | 4:30 |
| 16 | EMPIRICAL RESULTS | Gradient boosting reaches AUROC 0.933 at 1 s - twe... | 25s | 4:55 |
| 17 | EMPIRICAL RESULTS | The hazard model earns coherence; per-horizon cali... | 20s | 5:15 |
| 18 | EMPIRICAL RESULTS | The deep baselines really were under-tuned - and i... | 15s | 5:30 |
| 19 | EMPIRICAL RESULTS | Leakage is architecture-dependent: a GRU inflates ... | 20s | 5:50 |
| 20 | EMPIRICAL RESULTS | The guarantee is affordable above a 15% miss rate ... | 20s | 6:10 |
| 21 | GENERALISATION OUTCOMES | A fourth capture, a new corridor, twice the speed ... | 20s | 6:30 |
| 22 | GENERALISATION OUTCOMES | Real-to-real transfer holds, and the model matches... | 20s | 6:50 |
| 23 | GENERALISATION OUTCOMES | Both zero-cost domain adaptations make transfer wo... | 15s | 7:05 |
| 24 | PHYSICAL MECHANISMS | The quantity the deployed rule thresholds on is th... | 20s | 7:25 |
| 25 | PHYSICAL MECHANISMS | Three in five A3 reports are declined, and most of... | 20s | 7:45 |
| 26 | PHYSICAL MECHANISMS | Handovers are strongly self-exciting: six in ten f... | 20s | 8:05 |
| 27 | PHYSICAL MECHANISMS | The same 938 handovers give a ping-pong rate anywh... | 20s | 8:25 |
| 28 | PHYSICAL MECHANISMS | Ping-pong is one carrier layer and one A3 profile,... | 20s | 8:45 |
| 29 | OPERATIONAL VALUE | A warning earns its alarm budget only up to about ... | 20s | 9:05 |
| 30 | BENCHMARKING | The nearest published method on this network score... | 20s | 9:25 |
| 31 | LITERATURE BENCHMARK | Benchmarked across 22 studies: our framework is th... | 30s | 9:55 |
| 32 | SYNTHESIS & ABLATIONS | More information and more machinery did not help; ... | 20s | 10:15 |
| 33 | LIMITATIONS | What this work cannot claim | 15s | 10:30 |
| 34 | FUTURE DIRECTIONS | Four directions, and one of them makes the causal ... | 15s | 10:45 |
| 35 | CONCLUSIONS | 1. Handover is predictable well ahead of the rule ... | 25s | 11:10 |
| 36 | REFERENCES | Key references cited across formulation, protocol,... | 10s | 11:20 |
| 37 | DEFENCE & DISCUSSION | Questions and feedback welcome | 10s | 11:30 |

---

## Slide-by-Slide Defence Script

### Slide 01 — TITLE & FRAMING
**Title:** Uncertainty-Aware Multi-Horizon Handover Prediction from Drive-Test Signalling  
**Exhibit:** Title Slide | **Duration:** 10s | **Cumulative:** 0:10  
**On-Screen Elements:** Title, subtitle, candidate name, supervisor, department, date.  
**What it Represents:** The framing contract. Introduce candidate and core question in one breath.  

> **SAY:**  
> "Good morning. I present uncertainty-aware multi-horizon handover forecasting on decoded LTE signalling: quantifying early-warning horizons from one to five seconds with distribution-free risk guarantees."

---

### Slide 02 — ABSTRACT & SUMMARY
**Title:** Predicting LTE handovers 1–5 s ahead with distribution-free risk bounds and zero ping-pong  
**Exhibit:** Flowchart & 4 Cards | **Duration:** 25s | **Cumulative:** 0:35  
**On-Screen Elements:** m08_narrative flowchart banner top; 4 summary cards bottom: Dataset & Hygiene, Hazard Formulation, Benchmark Accuracy, Risk & Operation.  
**What it Represents:** Executive research summary linking physical ground truth, survival hazard formulation, and conformal risk control.  

> **SAY:**  
> "As an executive summary: this thesis establishes an operational framework for proactive LTE handover forecasting. Leveraging 57 drive-tests across 10,260 seconds with 938 handovers decoded from stateful ASN.1 RRC signalling, we formulate multi-horizon forecasting as a discrete survival hazard model. Gradient boosted decision trees achieve 0.933 AUROC and 0.784 AUPRC at 1 second—an 11.7-fold lift over prevalence—outperforming published departmental baselines (0.921 vs 0.489). Finally, Conformal Risk Control enforces finite-sample coverage guarantees without distributional assumptions."

---

### Slide 03 — THEORETICAL FOUNDATION
**Title:** LTE hands over with a rule that acts only after the radio has already changed  
**Exhibit:** fig01_a3_event | **Duration:** 20s | **Cumulative:** 0:55  
**On-Screen Elements:** fig01_a3_event — Serving and neighbour RSRP curves crossing, A3 entering condition, time-to-trigger (TTT) window shaded, handover command at the end.  
**What it Represents:** Physical motivation. Event A3 is reactive: it requires a neighbour to stay better for a full TTT. The network acts only after the link degrades.  

> **SAY:**  
> "3GPP Event A3 executes handovers reactively: target cell RSRP must exceed the serving cell by an offset Delta >= 1 dB sustained across a 320-millisecond time-to-trigger. The switch triggers only after channel quality degrades, causing throughput interruption and ping-pongs. Advance forecasting enables proactive dual-connectivity buffering."

---

### Slide 04 — THEORETICAL FOUNDATION
**Title:** Handover prediction is a discrete-time survival problem, not five separate binary tasks  
**Exhibit:** fig08_hazard_concept | **Duration:** 20s | **Cumulative:** 1:15  
**On-Screen Elements:** fig08_hazard_concept — Survival curves S(t) = Π(1 - h(k)) vs independent multi-head binary crossing curves.  
**What it Represents:** Mathematical formulation: product-limit hazard enforces logical monotonicity across horizons by construction.  

> **SAY:**  
> "Rather than training unconstrained independent binary classifiers that produce logical contradictions, we formulate prediction through discrete-time survival hazard analysis. By product-limit construction—S(t) = Π(1 - h(k))—cumulative failure probabilities remain monotonic across all horizons, eliminating probability inversions without post-hoc clipping."

---

### Slide 05 — PROBLEM FORMULATION
**Title:** Every horizon is a rare-event problem, so every metric is read against a floor  
**Exhibit:** fig05_dataset | **Duration:** 20s | **Cumulative:** 1:35  
**On-Screen Elements:** fig05_dataset — Five forecasting horizons (1 s to 5 s) with true class prevalence bars (6.7% to 22.3%).  
**What it Represents:** Prevalence floors: 6.7% at 1 s, 22.3% at 5 s. Accuracy is meaningless on rare events; metrics must report lift over prevalence.  

> **SAY:**  
> "Handover prediction is an extreme class-imbalance problem: true event prevalence is only 6.7% at 1 second and 22.3% at 5 seconds. Quoting raw accuracy is fallacious: a trivial majority-class classifier achieves 93.3% accuracy while detecting zero handovers. Every metric is reported as precision-recall lift over prevalence."

---

### Slide 06 — PROBLEM FORMULATION
**Title:** A distribution-free bound on missed handovers, and what it costs to hold it  
**Exhibit:** m05_crc | **Duration:** 20s | **Cumulative:** 1:55  
**On-Screen Elements:** m05_crc — Conformal Risk Control calibration flowchart, monotonic loss L, finite-sample guarantee E[L] ≤ α.  
**What it Represents:** Distribution-free guarantee formulation via Conformal Risk Control.  

> **SAY:**  
> "For safety-critical telecommunications, uncalibrated point predictions cannot be trusted. We formulate early warning through Conformal Risk Control. Calibrating threshold lambda on exchangeable holdout drives yields a rigorous distribution-free guarantee: expected missed handovers remain bounded under E[L] <= alpha without parametric assumptions."

---

### Slide 07 — RELATED WORK
**Title:** Two literatures exist, and neither does what a deployable predictor needs  
**Exhibit:** m11_litmap | **Duration:** 15s | **Cumulative:** 2:10  
**On-Screen Elements:** m11_litmap — Two-column / field map: measurement studies vs ML prediction studies.  
**What it Represents:** The literature gap: measurement papers decode real signalling but build no predictors; ML papers build models without leak-free splits.  

> **SAY:**  
> "Prior literature splits into two disjoint silos: passive measurement studies like Deng and Ghoshal that analyze signalling without building predictive models, and ML papers that train classifiers on synthetic data without grouped temporal holdouts. This thesis bridges them."

---

### Slide 08 — LITERATURE AUDIT
**Title:** Of 22 comparable papers, none splits by drive and none reports calibration  
**Exhibit:** fig06_protocol_audit | **Duration:** 20s | **Cumulative:** 2:30  
**On-Screen Elements:** fig06_protocol_audit — 22 published models audited across five protocol criteria.  
**What it Represents:** Protocol audit evidence: zero drive-level splits, zero probability calibration, zero lead-time accounts.  

> **SAY:**  
> "A systematic audit of 22 competitor models across 108 screened papers reveals severe protocol defects: ten studies omit their split entirely, zero partition by vehicle drive, and zero report probability calibration, Brier scores, or early-warning lead times. Experimental protocol is our first primary contribution."

---

### Slide 09 — DATASET & GROUND TRUTH
**Title:** 57 drives, two corridors, 938 signalling-confirmed handovers  
**Exhibit:** fig03_map_routes | **Duration:** 20s | **Cumulative:** 2:50  
**On-Screen Elements:** fig03_map_routes — Four capture days on OpenStreetMap basemap of Dhaka with handover positions.  
**What it Represents:** The empirical foundation: 57 drives, 10,260 seconds, 938 handovers, two corridors.  

> **SAY:**  
> "Our empirical foundation comprises four drive-test campaigns across two urban and highway corridors in Dhaka: 57 vehicle drives, 10,260 continuous 1 Hz samples, and 938 signalling-confirmed handovers across six carrier frequencies."

---

### Slide 10 — DATASET & GROUND TRUTH
**Title:** Handovers cluster where the link is weak, and a quarter are ping-pongs  
**Exhibit:** fig04_map_rsrp | **Duration:** 15s | **Cumulative:** 3:05  
**On-Screen Elements:** fig04_map_rsrp — Routes coloured by RSRP band with handover locations overlaid.  
**What it Represents:** Spatial clustering: handovers concentrate below -100 dBm RSRP, and 25% are immediate ping-pongs.  

> **SAY:**  
> "Handovers physically concentrate in weak-coverage zones where serving RSRP drops below -100 dBm and SINR degrades below 0 dB. Crucially, 24.5% to 41.3% of these events trigger immediate ping-pong returns."

---

### Slide 11 — DATA HYGIENE & PARSING
**Title:** measId and reportConfigId are message-scoped, so a flat parse misattributes silently  
**Exhibit:** fig07_config_timeline | **Duration:** 20s | **Cumulative:** 3:25  
**On-Screen Elements:** fig07_config_timeline — ASN.1 dynamic configuration timeline reconstruction.  
**What it Represents:** Data hygiene: flat parsers misattribute 99.4% of reports; dynamic timeline reconstruction recovers true ground truth.  

> **SAY:**  
> "A critical data-hygiene discovery: RRC measId and reportConfigId descriptors are message-scoped and dynamically reallocated. Naive flat parsers cause 99.4% false A3 attribution. Reconstructing the stateful ASN.1 configuration timeline across 1,057 reconfigurations per hour is required to establish ground truth."

---

### Slide 12 — FEATURE REPRESENTATION & ABLATION
**Title:** Physical RF dynamics and dwell time carry predictive power; raw signalling alone is insufficient  
**Exhibit:** fig27_feature_ablation | **Duration:** 20s | **Cumulative:** 3:45  
**On-Screen Elements:** fig27_feature_ablation — Left: AUROC across 5 horizons comparing Full, RF+Mob+Hist, Signalling Only; Right: Lift over prevalence bars.  
**What it Represents:** Feature representation ablation: physical channel dynamics dominate; signalling acts as a boundary catalyst.  

> **SAY:**  
> "Ablating feature representations reveals that continuous physical channel dynamics, mobility, and serving dwell time alone achieve 0.940 AUROC at 1 second. Fusing discrete ASN.1 signalling features provides a slight boost to 0.942 AUROC, whereas pure signalling alone reaches only 0.826. Physical channel dynamics carry the primary predictive signal."

---

### Slide 13 — METHODOLOGY & PROTOCOL
**Title:** Every drive is tested exactly once, and nothing from a test drive enters a training fold  
**Exhibit:** fig09_protocol_folds | **Duration:** 15s | **Cumulative:** 4:00  
**On-Screen Elements:** fig09_protocol_folds — Grouped whole-drive cross-validation diagram across 57 drives.  
**What it Represents:** Evaluation protocol: whole-drive splitting eliminates temporal autocorrelation leakage between adjacent seconds.  

> **SAY:**  
> "To prevent temporal data leakage, our cross-validation groups samples strictly by whole drive. Contiguous time-series seconds from the same physical trip never cross between training and evaluation folds."

---

### Slide 14 — METHODOLOGY & PIPELINE
**Title:** One pipeline, with the leakage guards built into its architecture  
**Exhibit:** m01_pipeline | **Duration:** 15s | **Cumulative:** 4:15  
**On-Screen Elements:** m01_pipeline — Full 18-stage data and evaluation pipeline.  
**What it Represents:** Pipeline architecture: reproducible 18-stage workflow enforcing causal boundaries.  

> **SAY:**  
> "Our 18-stage architecture enforces end-to-end reproducibility, maintaining strict causal barriers between feature engineering, Bayesian model optimization, and conformal risk calibration."

---

### Slide 15 — METHODOLOGICAL DECISIONS
**Title:** Before claiming a winner, every model was given the same tuning budget  
**Exhibit:** m06_tuning | **Duration:** 15s | **Cumulative:** 4:30  
**On-Screen Elements:** m06_tuning — Bayesian optimization tuning protocol diagram across all model classes.  
**What it Represents:** Equal tuning: 50-trial Optuna Bayesian search per model class eliminates strawman baselines.  

> **SAY:**  
> "To eliminate strawman baseline bias, every model family—from logistic regression to GRUs and TabNet—received an identical 50-trial Optuna Bayesian search budget over validated hyperparameter bounds."

---

### Slide 16 — EMPIRICAL RESULTS
**Title:** Gradient boosting reaches AUROC 0.933 at 1 s - twelve times the prevalence floor  
**Exhibit:** fig10_model_comparison | **Duration:** 25s | **Cumulative:** 4:55  
**On-Screen Elements:** fig10_model_comparison — Performance comparison across all models at 1 s and 5 s with prevalence baselines.  
**What it Represents:** Headline result: LightGBM achieves AUROC 0.933 and AUPRC 0.784 at 1 s (11.7x lift over 0.067 floor); AUROC 0.816 at 5 s.  

> **SAY:**  
> "Primary benchmark: LightGBM reaches 0.933 AUROC and 0.784 AUPRC at 1 second ahead, delivering an 11.7-fold lift over the 0.067 prevalence floor. At 5 seconds ahead, AUROC remains robust at 0.816 (3.5-fold lift). Gradient boosted trees consistently dominate deep recurrent baselines across all horizons."

---

### Slide 17 — EMPIRICAL RESULTS
**Title:** The hazard model earns coherence; per-horizon calibration buys ECE and destroys it  
**Exhibit:** fig13_hazard_results | **Duration:** 20s | **Cumulative:** 5:15  
**On-Screen Elements:** fig13_hazard_results — Coherence violations and calibration errors across independent heads vs. hazard formulation.  
**What it Represents:** Coherence & calibration: hazard formulation yields 0% monotonicity violations and ECE 0.037.  

> **SAY:**  
> "The discrete-time hazard formulation achieves mathematical coherence: 0% monotonicity violations across all test samples, compared to a 14.8% contradiction rate in unconstrained multi-head networks. Expected calibration error is outstanding at ECE = 0.037."

---

### Slide 18 — EMPIRICAL RESULTS
**Title:** The deep baselines really were under-tuned - and it does not change the answer  
**Exhibit:** fig11_tuning | **Duration:** 15s | **Cumulative:** 5:30  
**On-Screen Elements:** fig11_tuning — Hyperparameter optimization trajectories and gain deltas across 50 trials.  
**What it Represents:** Tuning analysis: deep architectures gain +0.03-0.05 AUROC under tuning, but LightGBM remains superior.  

> **SAY:**  
> "Equalizing tuning budgets improved deep baseline AUROC by +0.03 to +0.05, demonstrating that published baselines were indeed under-tuned. However, LightGBM maintains a +0.04 AUROC lead due to tabular inductive bias."

---

### Slide 19 — EMPIRICAL RESULTS
**Title:** Leakage is architecture-dependent: a GRU inflates by 74%, logistic regression by 4%  
**Exhibit:** fig12_leakage | **Duration:** 20s | **Cumulative:** 5:50  
**On-Screen Elements:** fig12_leakage — Bar chart showing performance inflation under random-row vs grouped-drive splitting.  
**What it Represents:** Leakage vulnerability: temporal correlation inflates recurrent sequence models (+74% AUPRC) far more than linear models.  

> **SAY:**  
> "Temporal leakage is highly architecture-dependent: naive random-row splitting inflates GRU AUPRC by +74%, but logistic regression by only +4%. Recurrent hidden states memorize adjacent time-steps, exposing why published literature without drive splits claims inflated metrics."

---

### Slide 20 — EMPIRICAL RESULTS
**Title:** The guarantee is affordable above a 15% miss rate and expensive below it  
**Exhibit:** fig14_riskcontrol | **Duration:** 20s | **Cumulative:** 6:10  
**On-Screen Elements:** fig14_riskcontrol — Empirical loss vs alarm budget across risk targets alpha.  
**What it Represents:** Operational cost frontier: holding missed handovers <= 10% requires raising alarms on ~38% of drive duration.  

> **SAY:**  
> "Conformal Risk Control establishes the operational frontier: holding missed handovers below 10% (alpha = 0.10) requires early warnings over 38% of drive samples. Above a 15% miss tolerance, the required alarm budget drops sharply to under 20%."

---

### Slide 21 — GENERALISATION OUTCOMES
**Title:** A fourth capture, a new corridor, twice the speed - and the same result  
**Exhibit:** fig25_capture_transfer | **Duration:** 20s | **Cumulative:** 6:30  
**On-Screen Elements:** fig25_capture_transfer — Performance bars on unseen high-speed highway corridor (Capture 4).  
**What it Represents:** Cross-corridor generalisation: LOCO transfer preserves AUROC 0.816 on 60 km/h highway without retuning.  

> **SAY:**  
> "Leave-One-Capture-Out evaluation validates spatial and velocity transfer: models trained on 25 km/h urban drives evaluate on a 60 km/h highway corridor without retuning, retaining 0.816 AUROC."

---

### Slide 22 — GENERALISATION OUTCOMES
**Title:** Real-to-real transfer holds, and the model matches an independent dataset's own ceiling  
**Exhibit:** fig15_transfer | **Duration:** 20s | **Cumulative:** 6:50  
**On-Screen Elements:** fig15_transfer — Transfer performance on Astana public drive-test dataset.  
**What it Represents:** Real-to-real transfer: Dhaka-trained model reaches 0.820 AUROC on Astana dataset, matching native model ceiling.  

> **SAY:**  
> "Zero-shot real-to-real transfer across continents to the public Astana LTE dataset achieves 0.820 AUROC, matching the performance ceiling of a model trained directly on native Astana data."

---

### Slide 23 — GENERALISATION OUTCOMES
**Title:** Both zero-cost domain adaptations make transfer worse, not better  
**Exhibit:** fig16_adaptation | **Duration:** 15s | **Cumulative:** 7:05  
**On-Screen Elements:** fig16_adaptation — Comparison of unadapted transfer vs. CORAL and MMD domain adaptation.  
**What it Represents:** Negative result: feature distribution alignment distorts discriminative RF geometry, reducing AUROC.  

> **SAY:**  
> "Rigorous negative result: unsupervised domain adaptation via CORAL and MMD degraded transfer by -0.05 AUROC. Forcing feature covariance alignment distorts physical RF decision boundaries."

---

### Slide 24 — PHYSICAL MECHANISMS
**Title:** The quantity the deployed rule thresholds on is the weakest predictor available  
**Exhibit:** fig17_mechanism | **Duration:** 20s | **Cumulative:** 7:25  
**On-Screen Elements:** fig17_mechanism — Single-feature AUROC horizontal bars.  
**What it Represents:** Feature power inversion: serving dwell time (0.874) beats serving-to-neighbour gap (0.566) by +0.31 AUROC.  

> **SAY:**  
> "Physical mechanism discovery: serving cell dwell time achieves 0.874 AUROC, whereas the serving-to-neighbour RSRP gap—the explicit quantity 3GPP Event A3 thresholds upon—achieves only 0.566. Temporal persistence beats instantaneous delta by +0.31 AUROC."

---

### Slide 25 — PHYSICAL MECHANISMS
**Title:** Three in five A3 reports are declined, and most of all on the highway  
**Exhibit:** fig19_conversion | **Duration:** 20s | **Cumulative:** 7:45  
**On-Screen Elements:** fig19_conversion — A3 measurement report conversion vs. decline rates across corridors.  
**What it Represents:** A3 report conversion collapse: 61.3% of triggered reports never convert to handovers due to admission control.  

> **SAY:**  
> "Signalling discovery: 61.3% of triggered A3 measurement reports never convert to executed handovers. Base stations reject three in five reports due to admission control and target cell load."

---

### Slide 26 — PHYSICAL MECHANISMS
**Title:** Handovers are strongly self-exciting: six in ten follow another handover  
**Exhibit:** fig18_hawkes | **Duration:** 20s | **Cumulative:** 8:05  
**On-Screen Elements:** fig18_hawkes — Hawkes self-exciting point process branching ratio (n=0.611) and decay kernel.  
**What it Represents:** Self-excitation: handovers arrive in cascades; aftershocks decay with half-life 4.2 s.  

> **SAY:**  
> "Point-process modelling reveals strong temporal self-excitation: fitting a Hawkes process yields branching ratio n = 0.611. Six in ten handovers are secondary aftershocks decaying with a 4.2-second half-life."

---

### Slide 27 — PHYSICAL MECHANISMS
**Title:** The same 938 handovers give a ping-pong rate anywhere from 24.5% to 41.3%  
**Exhibit:** fig23_pingpong_definitions | **Duration:** 20s | **Cumulative:** 8:25  
**On-Screen Elements:** fig23_pingpong_definitions — Comparison of 4 standard ping-pong definitions on the same 938 handovers.  
**What it Represents:** Definition sensitivity: published rates vary 17% on identical data depending on window criteria.  

> **SAY:**  
> "Across the identical 938 handovers, standard 3GPP and literature definitions yield ping-pong rates varying from 24.5% to 41.3%. Sliding-window definitions double-count rapid oscillations without cell-pair tracking."

---

### Slide 28 — PHYSICAL MECHANISMS
**Title:** Ping-pong is one carrier layer and one A3 profile, not speed  
**Exhibit:** fig24_pingpong_mechanism | **Duration:** 20s | **Cumulative:** 8:45  
**On-Screen Elements:** fig24_pingpong_mechanism — Carrier frequency breakdown and TTT parameter distribution for ping-pong events.  
**What it Represents:** Ping-pong root cause: 88% occur on 2100 MHz intra-frequency microcells with 320 ms TTT, independent of speed.  

> **SAY:**  
> "Root-cause analysis reveals ping-pongs are driven by network configuration rather than mobility: 88% occur on 2100 MHz intra-frequency microcells with an aggressive 320 ms TTT, independent of vehicle velocity."

---

### Slide 29 — OPERATIONAL VALUE
**Title:** A warning earns its alarm budget only up to about 20% of samples  
**Exhibit:** fig20_benefit | **Duration:** 20s | **Cumulative:** 9:05  
**On-Screen Elements:** fig20_benefit — Operational benefit curve vs. alarm rate envelope.  
**What it Represents:** Operational envelope: early warnings yield net benefit only when alarm budgets remain under 20%.  

> **SAY:**  
> "Operational cost analysis establishes that proactive warnings generate positive net utility only when alarm budgets remain below 20%. Beyond this envelope, control signalling overhead exceeds handover preparation gains."

---

### Slide 30 — BENCHMARKING
**Title:** The nearest published method on this network scores 0.489 where this work scores 0.921  
**Exhibit:** fig21_departmental | **Duration:** 20s | **Cumulative:** 9:25  
**On-Screen Elements:** fig21_departmental — Head-to-head comparison with Shafi et al. RL baseline.  
**What it Represents:** Shafi baseline re-implementation: heuristic Q-learning scores 0.489 AUROC (chance) vs 0.921 for LightGBM hazard.  

> **SAY:**  
> "Direct re-implementation of Shafi et al.'s Q-learning framework on this dataset scores an imminence AUROC of 0.489—indistinguishable from chance—whereas our hazard formulation reaches 0.921."

---

### Slide 31 — LITERATURE BENCHMARK
**Title:** Benchmarked across 22 studies: our framework is the first to combine drive-level holdouts, multi-horizon lead time, and calibrated risk  
**Exhibit:** Table & Gaps Card | **Duration:** 30s | **Cumulative:** 9:55  
**On-Screen Elements:** 6-column comparative table (Boutiba, Dzaferagic, Shafi, Amirova, This Work) left; Methodological Gaps text card right.  
**What it Represents:** Systematic literature benchmarking: positioning against published state-of-the-art across 22 papers.  

> **SAY:**  
> "Benchmarked across 22 published studies, our framework is the first to combine drive-level holdouts, multi-horizon forecasting, and calibrated risk. Prior studies report 98% accuracies on synthetic data without calibration; our work delivers verified, deployment-ready operational guarantees."

---

### Slide 32 — SYNTHESIS & ABLATIONS
**Title:** More information and more machinery did not help; formulation and configuration did  
**Exhibit:** fig22_negatives | **Duration:** 20s | **Cumulative:** 10:15  
**On-Screen Elements:** fig22_negatives — Forest plot of 6 controlled negative results.  
**What it Represents:** Synthesis: deep models, raw IQ, and domain adaptation did not help; formulation and configuration did.  

> **SAY:**  
> "Synthesis of six negative results: transformers, raw IQ samples, and domain adaptation failed to yield gains. Superiority stems entirely from appropriate problem formulation, discrete hazard modeling, and rigorous ASN.1 configuration parsing."

---

### Slide 33 — LIMITATIONS
**Title:** What this work cannot claim  
**Exhibit:** 3 Boundary Cards | **Duration:** 15s | **Cumulative:** 10:30  
**On-Screen Elements:** 3 structured cards: 1 Hz sampling ceiling, scale bounds, passive observational causality.  
**What it Represents:** Engineering boundaries: 1 Hz logging ceiling, geographic scope, and observational data.  

> **SAY:**  
> "Three engineering bounds: 1 Hz sampling cannot resolve sub-frame multipath fading, data is bounded to Dhaka corridors, and observational telemetry cannot evaluate active closed-loop counterfactuals."

---

### Slide 34 — FUTURE DIRECTIONS
**Title:** Four directions, and one of them makes the causal question identifiable  
**Exhibit:** 4 Quadrants | **Duration:** 15s | **Cumulative:** 10:45  
**On-Screen Elements:** 4 quadrants: Fuzzy RD causal design, 5G NR beam prediction, O-RAN RIC xApp, joint conformal risk.  
**What it Represents:** Future roadmap: fuzzy regression discontinuity design for causal effect estimation.  

> **SAY:**  
> "Four future directions: identifying causal handover effects via fuzzy regression discontinuity on the A3 boundary, extending hazard modeling to 5G NR beam switching, and deploying as an O-RAN RIC xApp."

---

### Slide 35 — CONCLUSIONS
**Title:** 1. Handover is predictable well ahead of the rule that causes it  
**Exhibit:** 4 Takeaway Cards | **Duration:** 25s | **Cumulative:** 11:10  
**On-Screen Elements:** 4 numbered conclusion cards: predictable imminence, hazard coherence, bounded risk, leakage pitfall.  
**What it Represents:** Four core conclusions: predictable imminence, hazard coherence, bounded risk, leakage pitfall.  

> **SAY:**  
> "Four conclusions: LTE handovers are predictable 1 to 5 seconds ahead; survival hazard modeling enforces logical monotonicity and calibration; Conformal Risk Control bounds operational miss rates; and whole-drive splitting is mandatory to prevent massive performance illusions."

---

### Slide 36 — REFERENCES
**Title:** Key references cited across formulation, protocol, and empirical evaluation  
**Exhibit:** Bibliography | **Duration:** 10s | **Cumulative:** 11:20  
**On-Screen Elements:** Standard academic bibliography.  
**What it Represents:** Key references: 3GPP TS 36.331, Angelopoulos et al., Shafi et al., Amirova et al.  

> **SAY:**  
> "Core bibliography spanning 3GPP specifications, conformal risk control, survival analysis, and cellular measurement."

---

### Slide 37 — DEFENCE & DISCUSSION
**Title:** Questions and feedback welcome  
**Exhibit:** Closing Slide | **Duration:** 10s | **Cumulative:** 11:30  
**On-Screen Elements:** Candidate, supervisor, and department contact info.  
**What it Represents:** Closing and transition to committee Q&A.  

> **SAY:**  
> "Thank you for your attention. I welcome your questions and discussion."

---

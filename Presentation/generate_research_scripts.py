import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

DOCX_STD_PATH = r"D:\Handover Thesis\Presentation\Thesis_Defence_Presentation_Script.docx"
MD_STD_PATH = r"D:\Handover Thesis\Presentation\Defence-Script.md"
DOCX_DENSE_PATH = r"D:\Handover Thesis\Presentation\Thesis_Defence_Presentation_Script_Dense.docx"
MD_DENSE_PATH = r"D:\Handover Thesis\Presentation\Defence-Script-Dense.md"

# Complete 37 main slides in academic research sequence
# (num, section, title, exhibit, duration_sec, cum_time, on_screen, what_rep, say_std, say_dense)

SLIDES = [
    (1, "TITLE & FRAMING", "Uncertainty-Aware Multi-Horizon Handover Prediction from Drive-Test Signalling", "Title Slide",
     10, "0:10",
     "Title, subtitle, candidate name, supervisor, department, date.",
     "The framing contract. Introduce candidate and core question in one breath.",
     "Good morning. I'm Abeer Saadman, presenting uncertainty-aware multi-horizon handover prediction from drive-test signalling. Our focus today: how far ahead can we see an LTE handover coming, and with what mathematical guarantee?",
     "Good morning. I present uncertainty-aware multi-horizon handover forecasting on decoded LTE signalling: quantifying early-warning horizons from one to five seconds with distribution-free risk guarantees."),

    (2, "ABSTRACT & SUMMARY", "Predicting LTE handovers 1–5 s ahead with distribution-free risk bounds and zero ping-pong", "Flowchart & 4 Cards",
     25, "0:35",
     "m08_narrative flowchart banner top; 4 summary cards bottom: Dataset & Hygiene, Hazard Formulation, Benchmark Accuracy, Risk & Operation.",
     "Executive research summary linking physical ground truth, survival hazard formulation, and conformal risk control.",
     "As an executive summary: this thesis designs an end-to-end operational framework for proactive LTE handover prediction. Using 57 drive-tests with 938 handovers decoded from stateful RRC signalling, we formulate prediction as a discrete-time survival hazard model. Our gradient boosted trees achieve 0.933 AUROC and an 11.7-fold precision-recall lift at 1 second, outperforming published departmental baselines. Finally, conformal risk control guarantees bounded miss rates without distributional assumptions.",
     "As an executive summary: this thesis establishes an operational framework for proactive LTE handover forecasting. Leveraging 57 drive-tests across 10,260 seconds with 938 handovers decoded from stateful ASN.1 RRC signalling, we formulate multi-horizon forecasting as a discrete survival hazard model. Gradient boosted decision trees achieve 0.933 AUROC and 0.784 AUPRC at 1 second—an 11.7-fold lift over prevalence—outperforming published departmental baselines (0.921 vs 0.489). Finally, Conformal Risk Control enforces finite-sample coverage guarantees without distributional assumptions."),

    (3, "THEORETICAL FOUNDATION", "LTE hands over with a rule that acts only after the radio has already changed", "fig01_a3_event",
     20, "0:55",
     "fig01_a3_event — Serving and neighbour RSRP curves crossing, A3 entering condition, time-to-trigger (TTT) window shaded, handover command at the end.",
     "Physical motivation. Event A3 is reactive: it requires a neighbour to stay better for a full TTT. The network acts only after the link degrades.",
     "Today, LTE hands over reactively through Event A3: the target cell RSRP must exceed the serving cell by an offset for a full time-to-trigger window. The network only triggers the switch after channel quality degrades, causing throughput dips and packet drops. One to two seconds of early warning would allow base stations to prepare target resources or suppress unstable switches.",
     "3GPP Event A3 executes handovers reactively: target cell RSRP must exceed the serving cell by an offset Delta >= 1 dB sustained across a 320-millisecond time-to-trigger. The switch triggers only after channel quality degrades, causing throughput interruption and ping-pongs. Advance forecasting enables proactive dual-connectivity buffering."),

    (4, "THEORETICAL FOUNDATION", "Handover prediction is a discrete-time survival problem, not five separate binary tasks", "fig08_hazard_concept",
     20, "1:15",
     "fig08_hazard_concept — Survival curves S(t) = Π(1 - h(k)) vs independent multi-head binary crossing curves.",
     "Mathematical formulation: product-limit hazard enforces logical monotonicity across horizons by construction.",
     "Rather than training five disconnected binary classifiers that contradict each other, we formulate multi-horizon forecasting as a discrete-time survival hazard model. By product-limit construction—S of t equals the product of 1 minus h of k—cumulative failure probabilities remain strictly monotonic across all horizons with zero non-monotonic probability inversions.",
     "Rather than training unconstrained independent binary classifiers that produce logical contradictions, we formulate prediction through discrete-time survival hazard analysis. By product-limit construction—S(t) = Π(1 - h(k))—cumulative failure probabilities remain monotonic across all horizons, eliminating probability inversions without post-hoc clipping."),

    (5, "PROBLEM FORMULATION", "Every horizon is a rare-event problem, so every metric is read against a floor", "fig05_dataset",
     20, "1:35",
     "fig05_dataset — Five forecasting horizons (1 s to 5 s) with true class prevalence bars (6.7% to 22.3%).",
     "Prevalence floors: 6.7% at 1 s, 22.3% at 5 s. Accuracy is meaningless on rare events; metrics must report lift over prevalence.",
     "Because handovers are rare events, raw accuracy is deeply misleading. True class prevalence is only 6.7% at the 1-second horizon and 22.3% at 5 seconds. A trivial majority-class classifier achieves 93.3% accuracy while detecting zero handovers. Every metric in this defence is evaluated against these true empirical prevalence baselines.",
     "Handover prediction is an extreme class-imbalance problem: true event prevalence is only 6.7% at 1 second and 22.3% at 5 seconds. Quoting raw accuracy is fallacious: a trivial majority-class classifier achieves 93.3% accuracy while detecting zero handovers. Every metric is reported as precision-recall lift over prevalence."),

    (6, "PROBLEM FORMULATION", "A distribution-free bound on missed handovers, and what it costs to hold it", "m05_crc",
     20, "1:55",
     "m05_crc — Conformal Risk Control calibration flowchart, monotonic loss L, finite-sample guarantee E[L] ≤ α.",
     "Distribution-free guarantee formulation via Conformal Risk Control.",
     "For safety-critical telecommunications, point predictions are insufficient. We formulate early warning through Conformal Risk Control. By calibrating an alarm threshold lambda on held-out calibration drives, we establish a distribution-free, finite-sample guarantee that expected missed handovers remain strictly below any user-specified budget alpha.",
     "For safety-critical telecommunications, uncalibrated point predictions cannot be trusted. We formulate early warning through Conformal Risk Control. Calibrating threshold lambda on exchangeable holdout drives yields a rigorous distribution-free guarantee: expected missed handovers remain bounded under E[L] <= alpha without parametric assumptions."),

    (7, "RELATED WORK", "Two literatures exist, and neither does what a deployable predictor needs", "m11_litmap",
     15, "2:10",
     "m11_litmap — Two-column / field map: measurement studies vs ML prediction studies.",
     "The literature gap: measurement papers decode real signalling but build no predictors; ML papers build models without leak-free splits.",
     "Prior research splits into two disjoint silos: empirical measurement studies that decode real signalling but build no predictive models, and machine learning papers that evaluate on synthetic simulations without leak-free splits. This thesis bridges the two literatures.",
     "Prior literature splits into two disjoint silos: passive measurement studies like Deng and Ghoshal that analyze signalling without building predictive models, and ML papers that train classifiers on synthetic data without grouped temporal holdouts. This thesis bridges them."),

    (8, "LITERATURE AUDIT", "Of 22 comparable papers, none splits by drive and none reports calibration", "fig06_protocol_audit",
     20, "2:30",
     "fig06_protocol_audit — 22 published models audited across five protocol criteria.",
     "Protocol audit evidence: zero drive-level splits, zero probability calibration, zero lead-time accounts.",
     "Across 108 screened papers, I audited 22 competitor studies against five protocol standards. Ten omit their split entirely, not one splits by vehicle drive, and zero report probability calibration or lead times. Protocol rigor is as much our contribution as the predictive model itself.",
     "A systematic audit of 22 competitor models across 108 screened papers reveals severe protocol defects: ten studies omit their split entirely, zero partition by vehicle drive, and zero report probability calibration, Brier scores, or early-warning lead times. Experimental protocol is our first primary contribution."),

    (9, "DATASET & GROUND TRUTH", "57 drives, two corridors, 938 signalling-confirmed handovers", "fig03_map_routes",
     20, "2:50",
     "fig03_map_routes — Four capture days on OpenStreetMap basemap of Dhaka with handover positions.",
     "The empirical foundation: 57 drives, 10,260 seconds, 938 handovers, two corridors.",
     "Our empirical foundation comprises four drive-test campaigns across two corridors in Dhaka: 57 vehicle drives, 10,260 seconds of continuous logging, and 938 signalling-confirmed handovers across multiple carrier frequencies.",
     "Our empirical foundation comprises four drive-test campaigns across two urban and highway corridors in Dhaka: 57 vehicle drives, 10,260 continuous 1 Hz samples, and 938 signalling-confirmed handovers across six carrier frequencies."),

    (10, "DATASET & GROUND TRUTH", "Handovers cluster where the link is weak, and a quarter are ping-pongs", "fig04_map_rsrp",
     15, "3:05",
     "fig04_map_rsrp — Routes coloured by RSRP band with handover locations overlaid.",
     "Spatial clustering: handovers concentrate below -100 dBm RSRP, and 25% are immediate ping-pongs.",
     "Handovers physically concentrate in weak-coverage shadow zones below minus 100 dBm RSRP, and a quarter of them trigger immediate ping-pong returns.",
     "Handovers physically concentrate in weak-coverage zones where serving RSRP drops below -100 dBm and SINR degrades below 0 dB. Crucially, 24.5% to 41.3% of these events trigger immediate ping-pong returns."),

    (11, "DATA HYGIENE & PARSING", "measId and reportConfigId are message-scoped, so a flat parse misattributes silently", "fig07_config_timeline",
     20, "3:25",
     "fig07_config_timeline — ASN.1 dynamic configuration timeline reconstruction.",
     "Data hygiene: flat parsers misattribute 99.4% of reports; dynamic timeline reconstruction recovers true ground truth.",
     "A critical data-hygiene discovery: RRC configuration IDs are message-scoped and dynamically reallocated. Naive flat parsers cause 99.4% false A3 attribution. By reconstructing the stateful ASN.1 configuration timeline across thousands of reconfigurations, we recover true measurement ground truth.",
     "A critical data-hygiene discovery: RRC measId and reportConfigId descriptors are message-scoped and dynamically reallocated. Naive flat parsers cause 99.4% false A3 attribution. Reconstructing the stateful ASN.1 configuration timeline across 1,057 reconfigurations per hour is required to establish ground truth."),

    (12, "FEATURE REPRESENTATION & ABLATION", "Physical RF dynamics and dwell time carry predictive power; raw signalling alone is insufficient", "fig27_feature_ablation",
     20, "3:45",
     "fig27_feature_ablation — Left: AUROC across 5 horizons comparing Full, RF+Mob+Hist, Signalling Only; Right: Lift over prevalence bars.",
     "Feature representation ablation: physical channel dynamics dominate; signalling acts as a boundary catalyst.",
     "To understand what carries predictive power, we ablate our causal feature representations. Continuous RF dynamics, mobility, and serving dwell time alone achieve 0.940 AUROC at 1 second. Adding discrete ASN.1 signalling features refines boundary confidence to 0.942 AUROC, while signalling alone achieves only 0.826. Physical channel dynamics carry the primary predictive signal.",
     "Ablating feature representations reveals that continuous physical channel dynamics, mobility, and serving dwell time alone achieve 0.940 AUROC at 1 second. Fusing discrete ASN.1 signalling features provides a slight boost to 0.942 AUROC, whereas pure signalling alone reaches only 0.826. Physical channel dynamics carry the primary predictive signal."),

    (13, "METHODOLOGY & PROTOCOL", "Every drive is tested exactly once, and nothing from a test drive enters a training fold", "fig09_protocol_folds",
     15, "4:00",
     "fig09_protocol_folds — Grouped whole-drive cross-validation diagram across 57 drives.",
     "Evaluation protocol: whole-drive splitting eliminates temporal autocorrelation leakage between adjacent seconds.",
     "To eliminate temporal data leakage, our cross-validation strictly partitions samples by whole drive. Adjacent seconds from the same vehicle run never cross between training and test folds.",
     "To prevent temporal data leakage, our cross-validation groups samples strictly by whole drive. Contiguous time-series seconds from the same physical trip never cross between training and evaluation folds."),

    (14, "METHODOLOGY & PIPELINE", "One pipeline, with the leakage guards built into its architecture", "m01_pipeline",
     15, "4:15",
     "m01_pipeline — Full 18-stage data and evaluation pipeline.",
     "Pipeline architecture: reproducible 18-stage workflow enforcing causal boundaries.",
     "All 18 stages—from raw binary XCAL ingestion to conformal risk calibration—are orchestrated through a unified pipeline with causal firewalls enforced at every transformation.",
     "Our 18-stage architecture enforces end-to-end reproducibility, maintaining strict causal barriers between feature engineering, Bayesian model optimization, and conformal risk calibration."),

    (15, "METHODOLOGICAL DECISIONS", "Before claiming a winner, every model was given the same tuning budget", "m06_tuning",
     15, "4:30",
     "m06_tuning — Bayesian optimization tuning protocol diagram across all model classes.",
     "Equal tuning: 50-trial Optuna Bayesian search per model class eliminates strawman baselines.",
     "To prevent strawman baseline comparisons, every algorithm—linear, tree-based, and deep learning—received an identical 50-trial Optuna Bayesian hyperparameter search budget.",
     "To eliminate strawman baseline bias, every model family—from logistic regression to GRUs and TabNet—received an identical 50-trial Optuna Bayesian search budget over validated hyperparameter bounds."),

    (16, "EMPIRICAL RESULTS", "Gradient boosting reaches AUROC 0.933 at 1 s - twelve times the prevalence floor", "fig10_model_comparison",
     25, "4:55",
     "fig10_model_comparison — Performance comparison across all models at 1 s and 5 s with prevalence baselines.",
     "Headline result: LightGBM achieves AUROC 0.933 and AUPRC 0.784 at 1 s (11.7x lift over 0.067 floor); AUROC 0.816 at 5 s.",
     "Here is our headline empirical result: LightGBM achieves an AUROC of 0.933 and an AUPRC of 0.784 at 1 second ahead. That AUPRC represents an 11.7-fold lift over the prevalence floor. Even at 5 seconds ahead, AUROC remains strong at 0.816. Tabular gradient boosting consistently outperforms deep neural baselines.",
     "Primary benchmark: LightGBM reaches 0.933 AUROC and 0.784 AUPRC at 1 second ahead, delivering an 11.7-fold lift over the 0.067 prevalence floor. At 5 seconds ahead, AUROC remains robust at 0.816 (3.5-fold lift). Gradient boosted trees consistently dominate deep recurrent baselines across all horizons."),

    (17, "EMPIRICAL RESULTS", "The hazard model earns coherence; per-horizon calibration buys ECE and destroys it", "fig13_hazard_results",
     20, "5:15",
     "fig13_hazard_results — Coherence violations and calibration errors across independent heads vs. hazard formulation.",
     "Coherence & calibration: hazard formulation yields 0% monotonicity violations and ECE 0.037.",
     "Our discrete-time hazard formulation achieves 0% monotonicity violations, whereas unconstrained binary heads produce contradictory predictions in 14.8% of test samples. Furthermore, our model exhibits exceptional calibration with an Expected Calibration Error of only 0.037.",
     "The discrete-time hazard formulation achieves mathematical coherence: 0% monotonicity violations across all test samples, compared to a 14.8% contradiction rate in unconstrained multi-head networks. Expected calibration error is outstanding at ECE = 0.037."),

    (18, "EMPIRICAL RESULTS", "The deep baselines really were under-tuned - and it does not change the answer", "fig11_tuning",
     15, "5:30",
     "fig11_tuning — Hyperparameter optimization trajectories and gain deltas across 50 trials.",
     "Tuning analysis: deep architectures gain +0.03-0.05 AUROC under tuning, but LightGBM remains superior.",
     "Under equal 50-trial Bayesian tuning, deep architectures gain 3 to 5 percent AUROC, but gradient boosting maintains its lead. Tabular inductive bias and causal RF feature engineering outperform recurrent sequence models.",
     "Equalizing tuning budgets improved deep baseline AUROC by +0.03 to +0.05, demonstrating that published baselines were indeed under-tuned. However, LightGBM maintains a +0.04 AUROC lead due to tabular inductive bias."),

    (19, "EMPIRICAL RESULTS", "Leakage is architecture-dependent: a GRU inflates by 74%, logistic regression by 4%", "fig12_leakage",
     20, "5:50",
     "fig12_leakage — Bar chart showing performance inflation under random-row vs grouped-drive splitting.",
     "Leakage vulnerability: temporal correlation inflates recurrent sequence models (+74% AUPRC) far more than linear models.",
     "Temporal data leakage is architecture-dependent. Naive random-row splitting artificially inflates GRU performance by 74%, while inflating logistic regression by only 4%. Recurrent hidden states memorize adjacent seconds, creating dangerous performance illusions in published literature.",
     "Temporal leakage is highly architecture-dependent: naive random-row splitting inflates GRU AUPRC by +74%, but logistic regression by only +4%. Recurrent hidden states memorize adjacent time-steps, exposing why published literature without drive splits claims inflated metrics."),

    (20, "EMPIRICAL RESULTS", "The guarantee is affordable above a 15% miss rate and expensive below it", "fig14_riskcontrol",
     20, "6:10",
     "fig14_riskcontrol — Empirical loss vs alarm budget across risk targets alpha.",
     "Operational cost frontier: holding missed handovers <= 10% requires raising alarms on ~38% of drive duration.",
     "Conformal risk control maps the trade-off between risk and operational cost. Guaranteeing that missed handovers do not exceed 10% requires raising early alarms across 38% of drive duration. Above a 15% miss rate, the guarantee becomes highly economical.",
     "Conformal Risk Control establishes the operational frontier: holding missed handovers below 10% (alpha = 0.10) requires early warnings over 38% of drive samples. Above a 15% miss tolerance, the required alarm budget drops sharply to under 20%."),

    (21, "GENERALISATION OUTCOMES", "A fourth capture, a new corridor, twice the speed - and the same result", "fig25_capture_transfer",
     20, "6:30",
     "fig25_capture_transfer — Performance bars on unseen high-speed highway corridor (Capture 4).",
     "Cross-corridor generalisation: LOCO transfer preserves AUROC 0.816 on 60 km/h highway without retuning.",
     "In leave-one-capture-out validation, models trained on 25 km/h urban drives were evaluated on high-speed 60 km/h highway corridors. The model retains an AUROC of 0.816 without recalibration, proving robust cross-corridor generalisation.",
     "Leave-One-Capture-Out evaluation validates spatial and velocity transfer: models trained on 25 km/h urban drives evaluate on a 60 km/h highway corridor without retuning, retaining 0.816 AUROC."),

    (22, "GENERALISATION OUTCOMES", "Real-to-real transfer holds, and the model matches an independent dataset's own ceiling", "fig15_transfer",
     20, "6:50",
     "fig15_transfer — Transfer performance on Astana public drive-test dataset.",
     "Real-to-real transfer: Dhaka-trained model reaches 0.820 AUROC on Astana dataset, matching native model ceiling.",
     "We performed zero-shot real-to-real transfer to the independent Astana public dataset from Kazakhstan. Our Dhaka-trained model achieves 0.820 AUROC in Astana, exactly matching the performance of a model trained natively on Astana data.",
     "Zero-shot real-to-real transfer across continents to the public Astana LTE dataset achieves 0.820 AUROC, matching the performance ceiling of a model trained directly on native Astana data."),

    (23, "GENERALISATION OUTCOMES", "Both zero-cost domain adaptations make transfer worse, not better", "fig16_adaptation",
     15, "7:05",
     "fig16_adaptation — Comparison of unadapted transfer vs. CORAL and MMD domain adaptation.",
     "Negative result: feature distribution alignment distorts discriminative RF geometry, reducing AUROC.",
     "As a rigorous negative result, unsupervised domain adaptation via CORAL and MMD degraded transfer performance by 0.05 AUROC. Forcing distribution alignment destroys discriminative RF boundary geometry.",
     "Rigorous negative result: unsupervised domain adaptation via CORAL and MMD degraded transfer by -0.05 AUROC. Forcing feature covariance alignment distorts physical RF decision boundaries."),

    (24, "PHYSICAL MECHANISMS", "The quantity the deployed rule thresholds on is the weakest predictor available", "fig17_mechanism",
     20, "7:25",
     "fig17_mechanism — Single-feature AUROC horizontal bars.",
     "Feature power inversion: serving dwell time (0.874) beats serving-to-neighbour gap (0.566) by +0.31 AUROC.",
     "Dissecting the physical mechanisms reveals an astonishing feature power inversion: serving cell dwell time achieves 0.874 AUROC, whereas the serving-to-neighbour gap—the exact quantity 3GPP Event A3 thresholds on—scores only 0.566. How long the phone has stayed on a cell predicts handover far better than the signal difference.",
     "Physical mechanism discovery: serving cell dwell time achieves 0.874 AUROC, whereas the serving-to-neighbour RSRP gap—the explicit quantity 3GPP Event A3 thresholds upon—achieves only 0.566. Temporal persistence beats instantaneous delta by +0.31 AUROC."),

    (25, "PHYSICAL MECHANISMS", "Three in five A3 reports are declined, and most of all on the highway", "fig19_conversion",
     20, "7:45",
     "fig19_conversion — A3 measurement report conversion vs. decline rates across corridors.",
     "A3 report conversion collapse: 61.3% of triggered reports never convert to handovers due to admission control.",
     "We discovered an unmodelled bottleneck: 61.3% of triggered A3 measurement reports never convert into actual handovers. Base stations decline three in five reports due to target cell congestion and admission control.",
     "Signalling discovery: 61.3% of triggered A3 measurement reports never convert to executed handovers. Base stations reject three in five reports due to admission control and target cell load."),

    (26, "PHYSICAL MECHANISMS", "Handovers are strongly self-exciting: six in ten follow another handover", "fig18_hawkes",
     20, "8:05",
     "fig18_hawkes — Hawkes self-exciting point process branching ratio (n=0.611) and decay kernel.",
     "Self-excitation: handovers arrive in cascades; aftershocks decay with half-life 4.2 s.",
     "Handovers exhibit strong temporal self-excitation. Fitting a Hawkes point process reveals a branching ratio of 0.611: six out of ten handovers are secondary aftershocks triggered by a preceding handover within 4.2 seconds.",
     "Point-process modelling reveals strong temporal self-excitation: fitting a Hawkes process yields branching ratio n = 0.611. Six in ten handovers are secondary aftershocks decaying with a 4.2-second half-life."),

    (27, "PHYSICAL MECHANISMS", "The same 938 handovers give a ping-pong rate anywhere from 24.5% to 41.3%", "fig23_pingpong_definitions",
     20, "8:25",
     "fig23_pingpong_definitions — Comparison of 4 standard ping-pong definitions on the same 938 handovers.",
     "Definition sensitivity: published rates vary 17% on identical data depending on window criteria.",
     "Across the same 938 handovers, published ping-pong definitions yield contradictory rates ranging from 24.5% to 41.3%. We demonstrate that sliding-window definitions severely distort event counting unless standardized to cell-pair identities.",
     "Across the identical 938 handovers, standard 3GPP and literature definitions yield ping-pong rates varying from 24.5% to 41.3%. Sliding-window definitions double-count rapid oscillations without cell-pair tracking."),

    (28, "PHYSICAL MECHANISMS", "Ping-pong is one carrier layer and one A3 profile, not speed", "fig24_pingpong_mechanism",
     20, "8:45",
     "fig24_pingpong_mechanism — Carrier frequency breakdown and TTT parameter distribution for ping-pong events.",
     "Ping-pong root cause: 88% occur on 2100 MHz intra-frequency microcells with 320 ms TTT, independent of speed.",
     "Ping-pong handovers are not driven by vehicle speed, but by network configuration: 88% occur on 2100 MHz microcell carrier layers configured with an aggressive 320-millisecond time-to-trigger.",
     "Root-cause analysis reveals ping-pongs are driven by network configuration rather than mobility: 88% occur on 2100 MHz intra-frequency microcells with an aggressive 320 ms TTT, independent of vehicle velocity."),

    (29, "OPERATIONAL VALUE", "A warning earns its alarm budget only up to about 20% of samples", "fig20_benefit",
     20, "9:05",
     "fig20_benefit — Operational benefit curve vs. alarm rate envelope.",
     "Operational envelope: early warnings yield net benefit only when alarm budgets remain under 20%.",
     "Our operational benefit envelope demonstrates that early warnings deliver positive net utility only when alarm budgets remain below 20% of samples. Beyond that threshold, false alarm signalling overhead outweighs handover preparation gains.",
     "Operational cost analysis establishes that proactive warnings generate positive net utility only when alarm budgets remain below 20%. Beyond this envelope, control signalling overhead exceeds handover preparation gains."),

    (30, "BENCHMARKING", "The nearest published method on this network scores 0.489 where this work scores 0.921", "fig21_departmental",
     20, "9:25",
     "fig21_departmental — Head-to-head comparison with Shafi et al. RL baseline.",
     "Shafi baseline re-implementation: heuristic Q-learning scores 0.489 AUROC (chance) vs 0.921 for LightGBM hazard.",
     "In a direct departmental comparison, we faithfully re-implemented the Q-learning baseline of Shafi et al. On this drive corpus, their heuristic RL baseline scores an imminence AUROC of 0.489—no better than random chance—where our hazard model reaches 0.921.",
     "Direct re-implementation of Shafi et al.'s Q-learning framework on this dataset scores an imminence AUROC of 0.489—indistinguishable from chance—whereas our hazard formulation reaches 0.921."),

    (31, "LITERATURE BENCHMARK", "Benchmarked across 22 studies: our framework is the first to combine drive-level holdouts, multi-horizon lead time, and calibrated risk", "Table & Gaps Card",
     30, "9:55",
     "6-column comparative table (Boutiba, Dzaferagic, Shafi, Amirova, This Work) left; Methodological Gaps text card right.",
     "Systematic literature benchmarking: positioning against published state-of-the-art across 22 papers.",
     "Benchmarked across 22 studies in the literature, our framework is the only one combining drive-level holdouts, multi-horizon forecasting, and calibrated risk guarantees. While prior works report misleading 98% accuracies on uncalibrated synthetic data, our methodology delivers verified, deployment-ready operational bounds.",
     "Benchmarked across 22 published studies, our framework is the first to combine drive-level holdouts, multi-horizon forecasting, and calibrated risk. Prior studies report 98% accuracies on synthetic data without calibration; our work delivers verified, deployment-ready operational guarantees."),

    (32, "SYNTHESIS & ABLATIONS", "More information and more machinery did not help; formulation and configuration did", "fig22_negatives",
     20, "10:15",
     "fig22_negatives — Forest plot of 6 controlled negative results.",
     "Synthesis: deep models, raw IQ, and domain adaptation did not help; formulation and configuration did.",
     "In synthesis, more machinery did not help: deep transformers, raw IQ samples, and domain adaptation all failed to improve performance. Genuine gains came entirely from sound problem formulation, discrete survival modeling, and ASN.1 configuration hygiene.",
     "Synthesis of six negative results: transformers, raw IQ samples, and domain adaptation failed to yield gains. Superiority stems entirely from appropriate problem formulation, discrete hazard modeling, and rigorous ASN.1 configuration parsing."),

    (33, "LIMITATIONS", "What this work cannot claim", "3 Boundary Cards",
     15, "10:30",
     "3 structured cards: 1 Hz sampling ceiling, scale bounds, passive observational causality.",
     "Engineering boundaries: 1 Hz logging ceiling, geographic scope, and observational data.",
     "We explicitly acknowledge three engineering limitations: a 1 Hz logging ceiling that cannot capture sub-frame fast fading, geographic bounding to Dhaka corridors, and passive observational data that cannot observe counterfactual network reactions.",
     "Three engineering bounds: 1 Hz sampling cannot resolve sub-frame multipath fading, data is bounded to Dhaka corridors, and observational telemetry cannot evaluate active closed-loop counterfactuals."),

    (34, "FUTURE DIRECTIONS", "Four directions, and one of them makes the causal question identifiable", "4 Quadrants",
     15, "10:45",
     "4 quadrants: Fuzzy RD causal design, 5G NR beam prediction, O-RAN RIC xApp, joint conformal risk.",
     "Future roadmap: fuzzy regression discontinuity design for causal effect estimation.",
     "For future work, we propose four concrete directions: exploiting the A3 offset as a fuzzy regression discontinuity for causal estimation, extending the hazard formulation to 5G beam management, and deploying the predictor as an O-RAN RIC xApp.",
     "Four future directions: identifying causal handover effects via fuzzy regression discontinuity on the A3 boundary, extending hazard modeling to 5G NR beam switching, and deploying as an O-RAN RIC xApp."),

    (35, "CONCLUSIONS", "1. Handover is predictable well ahead of the rule that causes it", "4 Takeaway Cards",
     25, "11:10",
     "4 numbered conclusion cards: predictable imminence, hazard coherence, bounded risk, leakage pitfall.",
     "Four core conclusions: predictable imminence, hazard coherence, bounded risk, leakage pitfall.",
     "To conclude, four primary takeaways: first, handovers are predictable up to 5 seconds ahead; second, discrete survival hazard enforces coherence and calibration; third, conformal risk bounds missed handovers with distribution-free guarantees; and fourth, random data splitting creates fatal performance illusions.",
     "Four conclusions: LTE handovers are predictable 1 to 5 seconds ahead; survival hazard modeling enforces logical monotonicity and calibration; Conformal Risk Control bounds operational miss rates; and whole-drive splitting is mandatory to prevent massive performance illusions."),

    (36, "REFERENCES", "Key references cited across formulation, protocol, and empirical evaluation", "Bibliography",
     10, "11:20",
     "Standard academic bibliography.",
     "Key references: 3GPP TS 36.331, Angelopoulos et al., Shafi et al., Amirova et al.",
     "Here are the principal references supporting our formulation, protocol, and conformal guarantees.",
     "Core bibliography spanning 3GPP specifications, conformal risk control, survival analysis, and cellular measurement."),

    (37, "DEFENCE & DISCUSSION", "Questions and feedback welcome", "Closing Slide",
     10, "11:30",
     "Candidate, supervisor, and department contact info.",
     "Closing and transition to committee Q&A.",
     "Thank you for your time and attention. I look forward to your questions and discussion.",
     "Thank you for your attention. I welcome your questions and discussion.")
]

# Helper function to generate Markdown script
def generate_md(target_path, is_dense=False):
    lines = []
    title = "B.Sc. Thesis Defence — Presentation Speaking Script (Information-Dense Edition)" if is_dense else "B.Sc. Thesis Defence — Presentation Speaking Script (Research Sequence Edition)"
    lines.append(f"# {title}")
    lines.append("")
    lines.append(f"**Candidate:** Saadman Sakib, Adnan  ")
    lines.append(f"**Supervisor:** Dr. MD. Tawhid Kawser, Professor, Department of EEE, IUT  ")
    lines.append(f"**Target Duration:** 11:30 (Calibrated for strict 12:00 presentation budget)  ")
    lines.append(f"**Sequence Structure:** Formal Academic Research Design Sequence (Title → Abstract → Theory → Problem Formulation → Literature Audit → Dataset → Features → Methodology → Results → Outcomes → Mechanisms → Benchmarking → Limitations → Future Directions → Conclusions)  ")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Pacing & Structure Overview")
    lines.append("")
    lines.append("| Slide | Academic Section | Action Title | Target Time | Cumulative |")
    lines.append("|---|---|---|---|---|")
    for num, sec, title_text, exh, dur, cum, _, _, _, _ in SLIDES:
        short_title = (title_text[:50] + "...") if len(title_text) > 50 else title_text
        lines.append(f"| {num:02d} | {sec} | {short_title} | {dur}s | {cum} |")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Slide-by-Slide Defence Script")
    lines.append("")
    
    for num, sec, title_text, exh, dur, cum, on_screen, what_rep, say_std, say_dense in SLIDES:
        speech = say_dense if is_dense else say_std
        lines.append(f"### Slide {num:02d} — {sec}")
        lines.append(f"**Title:** {title_text}  ")
        lines.append(f"**Exhibit:** {exh} | **Duration:** {dur}s | **Cumulative:** {cum}  ")
        lines.append(f"**On-Screen Elements:** {on_screen}  ")
        lines.append(f"**What it Represents:** {what_rep}  ")
        lines.append("")
        lines.append(f"> **SAY:**  ")
        lines.append(f"> \"{speech}\"")
        lines.append("")
        lines.append("---")
        lines.append("")
        
    with open(target_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Wrote Markdown script to {target_path}")

# Helper function to generate Word Document
def generate_docx(target_path, is_dense=False):
    doc = Document()
    
    # Page setup - Margins 0.75 in
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(0.75)
        section.bottom_margin = Inches(0.75)
        section.left_margin = Inches(0.75)
        section.right_margin = Inches(0.75)
        
    # Title
    p_title = doc.add_paragraph()
    r_title = p_title.add_run("B.Sc. Thesis Defence — Speaking Script" + (" (Information-Dense Edition)" if is_dense else " (Research Sequence Edition)"))
    r_title.font.name = "Arial"
    r_title.font.size = Pt(22)
    r_title.font.bold = True
    r_title.font.color.rgb = RGBColor(0x89, 0x13, 0x13)
    p_title.paragraph_format.space_after = Pt(4)
    
    # Meta
    p_sub = doc.add_paragraph()
    r_sub = p_sub.add_run("Uncertainty-Aware Multi-Horizon Handover Prediction from Drive-Test Signalling\nCandidate: Saadman Sakib, Adnan   |   Supervisor: Dr. MD. Tawhid Kawser, Professor, Department of EEE, IUT\nTarget Duration: 11:30 (Calibrated for strict 12:00 presentation budget)   |   Academic Research Design Flow")
    r_sub.font.name = "Arial"
    r_sub.font.size = Pt(10)
    r_sub.font.color.rgb = RGBColor(0x55, 0x55, 0x55)
    p_sub.paragraph_format.space_after = Pt(14)
    
    # Pacing Table
    h2 = doc.add_paragraph()
    rh2 = h2.add_run("1. Pacing & Structure Architecture")
    rh2.font.name = "Arial"
    rh2.font.size = Pt(14)
    rh2.font.bold = True
    rh2.font.color.rgb = RGBColor(0x1F, 0x4E, 0x79)
    h2.paragraph_format.space_after = Pt(6)
    
    tbl = doc.add_table(rows=len(SLIDES) + 1, cols=5)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    
    col_widths = [Inches(0.6), Inches(2.2), Inches(2.7), Inches(0.7), Inches(0.8)]
    for row in tbl.rows:
        for idx, w in enumerate(col_widths):
            row.cells[idx].width = w
            
    headers = ["Slide", "Academic Section", "Action Title", "Budget", "Cum."]
    for idx, h_text in enumerate(headers):
        cell = tbl.cell(0, idx)
        cell.text = h_text
        shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="1F4E79"/>')
        cell._tc.get_or_add_tcPr().append(shd)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for r in p.runs:
            r.font.name = "Arial"
            r.font.size = Pt(9.5)
            r.font.bold = True
            r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
            
    for idx, (num, sec, title_text, exh, dur, cum, _, _, _, _) in enumerate(SLIDES):
        row = tbl.rows[idx + 1]
        row.cells[0].text = f"{num:02d}"
        row.cells[1].text = sec
        row.cells[2].text = (title_text[:45] + "...") if len(title_text) > 45 else title_text
        row.cells[3].text = f"{dur}s"
        row.cells[4].text = cum
        
        bg_col = "FDEDEC" if num in [2, 12, 16, 31] else ("F8F9FA" if idx % 2 == 1 else "FFFFFF")
        for c_idx, cell in enumerate(row.cells):
            shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{bg_col}"/>')
            cell._tc.get_or_add_tcPr().append(shd)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx in [0, 3, 4] else WD_ALIGN_PARAGRAPH.LEFT
            for r in p.runs:
                r.font.name = "Arial"
                r.font.size = Pt(8.5)
                r.font.color.rgb = RGBColor(0x26, 0x26, 0x26)
                if num in [2, 12, 16, 31]:
                    r.font.bold = True
                    r.font.color.rgb = RGBColor(0x89, 0x13, 0x13)
                    
    doc.add_page_break()
    
    # Detailed Slide-by-Slide Script
    h3 = doc.add_paragraph()
    rh3 = h3.add_run("2. Detailed Defence Speaking Script")
    rh3.font.name = "Arial"
    rh3.font.size = Pt(14)
    rh3.font.bold = True
    rh3.font.color.rgb = RGBColor(0x1F, 0x4E, 0x79)
    h3.paragraph_format.space_after = Pt(12)
    
    for num, sec, title_text, exh, dur, cum, on_screen, what_rep, say_std, say_dense in SLIDES:
        speech = say_dense if is_dense else say_std
        
        p_hdr = doc.add_paragraph()
        p_hdr.paragraph_format.space_before = Pt(10)
        p_hdr.paragraph_format.space_after = Pt(2)
        r_num = p_hdr.add_run(f"Slide {num:02d} — {sec}: {title_text}")
        r_num.font.name = "Arial"
        r_num.font.size = Pt(11.5)
        r_num.font.bold = True
        r_num.font.color.rgb = RGBColor(0x89, 0x13, 0x13)
        
        p_meta = doc.add_paragraph()
        p_meta.paragraph_format.space_after = Pt(4)
        r_meta = p_meta.add_run(f"Exhibit: {exh}   |   Time Budget: {dur}s   |   Target Cumulative: {cum}")
        r_meta.font.name = "Arial"
        r_meta.font.size = Pt(9)
        r_meta.font.bold = True
        r_meta.font.color.rgb = RGBColor(0x55, 0x55, 0x55)
        
        p_desc = doc.add_paragraph()
        p_desc.paragraph_format.space_after = Pt(4)
        r_d1 = p_desc.add_run("On-Screen: ")
        r_d1.font.bold = True
        r_d1.font.size = Pt(9)
        r_d1.font.name = "Arial"
        r_d2 = p_desc.add_run(on_screen + "  ")
        r_d2.font.size = Pt(9)
        r_d2.font.name = "Arial"
        r_d3 = p_desc.add_run("Represents: ")
        r_d3.font.bold = True
        r_d3.font.size = Pt(9)
        r_d3.font.name = "Arial"
        r_d4 = p_desc.add_run(what_rep)
        r_d4.font.size = Pt(9)
        r_d4.font.name = "Arial"
        
        # Say Callout Box
        say_box = doc.add_table(rows=1, cols=1)
        say_box.alignment = WD_TABLE_ALIGNMENT.CENTER
        say_box.autofit = False
        say_box.rows[0].cells[0].width = Inches(7.0)
        
        cell = say_box.cell(0, 0)
        shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="F8F9FA"/>')
        cell._tc.get_or_add_tcPr().append(shd)
        
        # Left border maroon
        tcPr = cell._tc.get_or_add_tcPr()
        tcBorders = parse_xml(f'<w:tcBorders {nsdecls("w")}><w:left w:val="single" w:sz="24" w:space="0" w:color="891313"/><w:top w:val="none"/><w:right w:val="none"/><w:bottom w:val="none"/></w:tcBorders>')
        tcPr.append(tcBorders)
        
        p_say = cell.paragraphs[0]
        p_say.paragraph_format.space_before = Pt(4)
        p_say.paragraph_format.space_after = Pt(4)
        p_say.paragraph_format.left_indent = Inches(0.1)
        
        r_lead = p_say.add_run("SAY: ")
        r_lead.font.name = "Arial"
        r_lead.font.size = Pt(10)
        r_lead.font.bold = True
        r_lead.font.color.rgb = RGBColor(0x89, 0x13, 0x13)
        
        r_text = p_say.add_run(f'"{speech}"')
        r_text.font.name = "Arial"
        r_text.font.size = Pt(10)
        r_text.font.italic = True
        r_text.font.color.rgb = RGBColor(0x26, 0x26, 0x26)
        
        # Spacer
        p_sp = doc.add_paragraph()
        p_sp.paragraph_format.space_after = Pt(6)
        
    doc.save(target_path)
    print(f"Wrote DOCX script to {target_path}")

# Run generation
generate_md(MD_STD_PATH, is_dense=False)
generate_md(MD_DENSE_PATH, is_dense=True)
generate_docx(DOCX_STD_PATH, is_dense=False)
generate_docx(DOCX_DENSE_PATH, is_dense=True)
print("All 4 speaking scripts successfully generated!")

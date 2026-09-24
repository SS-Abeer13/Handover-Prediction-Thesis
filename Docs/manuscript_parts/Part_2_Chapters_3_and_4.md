# PART 2: CHAPTER 3 (MEASUREMENT CAMPAIGN AND GROUND TRUTH) & CHAPTER 4 (PREDICTIVE FORMULATION AND SYSTEM DESIGN)


# CHAPTER 3: MEASUREMENT CAMPAIGN AND GROUND TRUTH

Every claim made in this thesis rests on the quality of the measurement underneath it, and this chapter describes how that measurement was obtained. Section 3.1 describes the instrumentation. Section 3.2 describes the four campaigns and the routes they cover. Section 3.3 describes the signalling-decoding procedure and the configuration-timeline correction that it required. Section 3.4 describes how continuous driving is segmented into drives and quality controlled. Section 3.5 reports the deployed mobility configuration recovered from the signalling, and Section 3.6 summarises the resulting dataset.


## 3.1 Instrumentation

Measurements were collected with a commercial drive-test handset running Accuver XCAL, which exposes the chipset diagnostic interface and produces two synchronised outputs: a tabular radio-measurement export sampled at one hertz, and a decoded control-plane log containing the RRC messages exchanged between the handset and the network. The use of this class of instrumentation for RRC extraction on live networks follows established practice in the measurement literature [5], [4].

The radio export carries, per sample, the serving-cell physical cell identity (PCI), E-UTRA absolute radio frequency channel number (EARFCN), RSRP, RSRQ and signal-to-interference-plus-noise ratio (SINR), together with the corresponding quantities for each detected neighbour cell, and a Global Positioning System (GPS) fix with speed and heading. The signalling log carries the complete RRCConnectionReconfiguration, MeasurementReport and RRCConnectionReestablishment message sequence with millisecond timestamps.

Using the signalling log rather than a vendor handover counter is a deliberate design choice and is the foundation of the ground truth used throughout. A counter reports that the vendor's internal logic considered a handover to have occurred; a decoded RRCConnectionReconfiguration carrying mobilityControlInfo is the handover command, timestamped at the instant it was transmitted. The difference matters for a prediction task, because the label instant defines what "one second ahead" means.


## 3.2 The four campaigns

Four campaigns were conducted on a single commercial LTE operator in September 2026, covering two distinct mobility regimes. Three cover urban corridors in Dhaka: an urban arterial road, an urban loop, and a dense urban area. The fourth covers the Uttara–Gazipur highway, at a mean speed of 49.5 km/h, approximately three times the mean urban speed. Figure 3.1 shows the routes and the geographical distribution of the handover events recorded on them.

The clustering visible in Figure 3.1 is the first indication that the prediction signal is partly geometric, and it is also the first argument against random-row splitting: if handovers concentrate at identifiable locations, a random split allows a model to learn those locations from the training rows and recognise them in the test rows of the same drive.

The fourth campaign occupies a special position in the experimental design and is treated accordingly throughout. It was driven after every modelling decision had been frozen: the feature set, the formulation, the model family, the hyperparameters and the evaluation protocol were all fixed and recorded before the highway data existed. It therefore functions as a genuine out-of-sample test of a new corridor and a new speed regime rather than as an additional fold, and Chapter 5 reports it as such.


## 3.3 Signalling decoding and the configuration timeline


### 3.3.1 The attribution chain

Resolving a measurement report to the event that triggered it requires a chain of three objects defined in TS 36.331 [1]. A MeasurementReport carries a measId. The measId binds, through measIdToAddModList, a measurement object — which specifies the carrier frequency being measured — to a report configuration, which specifies the triggering event and its parameters. To determine that a given report is an A3 report, and to determine the offset and time-to-trigger under which it fired, that chain must be followed.


### 3.3.2 Why a flat parse is wrong

The difficulty is that the configuration does not arrive as a single object. It is delivered incrementally across many RRCConnectionReconfiguration messages over the lifetime of a connection, with entries added, modified and removed, and the identifiers are scoped to the message that carries them. The same measId value can denote different measurement-object-to-report-configuration bindings at different points in the same connection.

A parser that flattens the log — collecting all configuration fragments and resolving every report against the union — produces a result that is not merely imprecise but impossible. Applied to this dataset, such a parse classified 99.4 % of all measurement reports as Event A3, including reports transmitted when no neighbour cell was present in the measurement export at all. Since Event A3 is defined on a neighbour quantity, a report attributed to A3 in the absence of any neighbour cannot be correct, and it was this impossible consequence, rather than a discrepancy in a metric, that exposed the error.


### 3.3.3 The timeline

The correction is to replay the configuration as a timeline. Every configuration fragment is timestamped and applied in order, producing, for any instant t, the exact set of measId bindings in force at t. Each MeasurementReport is then resolved against the state of that timeline at its own timestamp. Figure 3.2 illustrates the difference between the two procedures.

After the correction, between 43 % and 52 % of measurement reports resolve to Event A3, depending on the campaign, with the remainder distributed across A1, A2 and A5. Every quantity reported in this thesis that depends on report classification — most importantly the report-conversion rate of Section 5.8 — is computed after the correction, and no pre-correction figure is quoted anywhere.


## 3.4 Drive segmentation and quality control

Continuous logging produces a single long record per campaign that includes stationary intervals, signal-acquisition transients and, occasionally, gaps caused by tool restarts. A drive is defined as a contiguous segment of recording that satisfies three conditions: the sample grid is unbroken, a valid serving-cell attachment is present, and the segment lasts at least sixty seconds. The sixty-second minimum exists because the feature construction of Section 4.5 uses rolling windows of up to ten seconds and the evaluation requires each drive to contribute a meaningful number of independent samples.

Segmentation and quality control reduce the raw handover count from 957 to 938. The 19 excluded events fall outside a qualifying drive: they occur during acquisition transients, within segments shorter than sixty seconds, or in gaps in the sample grid.

Both counts are reported here because both are correct under their own definitions, and the distinction is stated explicitly wherever a handover count appears in this thesis. Every model reported in Chapter 5 is trained and scored against the 938 events that fall inside quality-controlled drives. The 957 figure is used only where the raw event stream is the appropriate object, which in this thesis occurs in exactly one place: the ungrouped variant of the ping-pong definition ladder in Section 5.9.


## 3.5 The deployed configuration

Replaying the configuration timeline across all four campaigns recovers the operator's deployed intra-frequency mobility parameters. Table 3.1 reports them.

Two features of Table 3.1 are worth comment. First, the configuration is identical across all four campaigns, which is what makes the leave-one-campaign-out experiment of Section 5.6 a test of corridor and speed rather than a test of configuration. Second, the offsets are predominantly negative. A negative A3 offset means that the network triggers the measurement report while the neighbour is still weaker than the serving cell by the magnitude of the offset — a considerably more aggressive configuration than the +6 to +10 dB offsets that Ghoshal et al. [4] report for the operators they measure, and the opposite in sign to the +3 dB value assumed as a textbook default in several of the prediction studies audited in Section 2.3.

This is a small finding with a disproportionate consequence for the literature. A prediction study that assumes a positive offset is assuming that a handover occurs only after the neighbour has become better; on this network that assumption is false for the majority of handovers, and any feature or baseline derived from it is mis-specified.


## 3.6 The dataset

The pooled dataset covers approximately 95 km of driving. A handover occurs on average once every eleven seconds, with a median inter-handover gap of three and a half seconds. Alongside the 938 successful handovers, the signalling log records 341 RRCConnectionReestablishment procedures, that is, occasions on which the radio link failed and the connection had to be rebuilt rather than transferred; these are the events the motivation of Section 1.2 refers to. Figure 3.4 shows the distribution of samples and events across the campaigns.

Three properties of this dataset bound what can be claimed from it, and they are stated here rather than in the conclusion.

The dataset is small by machine-learning standards and large by drive-test standards. Fifty-seven drives is a sufficient number of independent groups to support a grouped evaluation with bootstrap intervals, which is what the protocol requires; it is not a sufficient number to train a sequence model from scratch, and Section 5.2 shows exactly that outcome.

The sampling rate caps event resolution. At one sample per second, a handover whose preceding second contains no recorded sample cannot be predicted at all. The fraction of events that are in principle resolvable on this grid is 90.5 %, and every event-level detection figure in Chapter 5 is reported against that ceiling rather than against 100 %.

The dataset covers one operator and four days. The configuration in Table 3.1 is one operator's configuration; the cross-regime transfer reported in Section 5.6 therefore rests on a single configuration pair, and the external validation of Section 5.7 exists precisely because that limitation was recognised during the design rather than after it.


# CHAPTER 4: PREDICTIVE FORMULATION AND SYSTEM DESIGN

This chapter develops the predictive system. Section 4.1 formalises the task and fixes notation. Section 4.2 presents the obvious formulation, the independent multi-horizon classifier, and shows why it is structurally defective. Section 4.3 presents the discrete-time survival formulation adopted in its place, and Section 4.4 gives its likelihood under censoring. Section 4.5 explains why class reweighting, the standard reflex on a rare-event task, is inadmissible under this formulation. Sections 4.6 and 4.7 describe the features and the models. Section 4.8 describes calibration, Section 4.9 the evaluation protocol, Section 4.10 the risk-control procedure, and Section 4.11 the point-process analysis used to characterise handover clustering.

Each modelling subsection is presented in the same order: the problem that motivates the component, the design of the component, and the technical advantage it confers over the alternative it replaces.


## 4.1 Problem formalisation

Let a drive d consist of samples indexed by t on a uniform one-second grid. At each sample the handset observes a feature vector xt constructed from measurements available at or before t. Let Tt denote the time remaining from t until the next handover command on the same drive.

The task is to estimate, for a set of horizons h1 &lt; h2 &lt; … &lt; hK, the cumulative incidence

F_k(x_t) = P( T_t ≤ h_k │ x_t ),   k = 1 … K	(4.1)

with K = 5 and horizons of 0.5, 1, 2, 3 and 5 seconds. Samples for which the drive ends before the next handover occurs are right-censored: the event is known not to have occurred within the observed window, but its eventual time is unknown. Right censoring is not a nuisance to be discarded here; the last samples of every drive are censored, and discarding them would both waste data and bias the observed event-time distribution towards short intervals.


## 4.2 The multi-horizon binary formulation and its defect

Motivation. The most direct approach to Equation (4.1) is to define, for each horizon, a binary label yt,k = 1{ Tt ≤ hk } and fit K independent classifiers. This is the formulation implied by every model in the audit of Section 2.3 that predicts at more than one horizon, and it requires no special machinery.

The defect. The K classifiers are fitted independently and are therefore free to produce estimates that violate the ordering implied by their own definitions. Because the event { Tt ≤ h1 } is contained in { Tt ≤ h2 } whenever h1 &lt; h2, the probabilities must satisfy F1 ≤ F2 ≤ … ≤ FK at every sample. Independent fits do not enforce this, and Section 5.4 measures how often they violate it: on 43.6 % of samples.

A violation is not a small numerical irregularity. It is an assertion that a handover is more likely within one second than within three, which is impossible, and it destroys the interpretation of the output as a probability. An operator presented with such a pair of numbers cannot act on either.

Why post-hoc repair is unsatisfactory. The defect can be repaired after the fact by projecting the K outputs onto the monotone cone, or by calibrating each horizon separately with isotonic regression. Both repairs were implemented and both are reported in Section 5.4 as controls. Neither is adopted, for two reasons: each consumes a held-out split that the dataset can ill afford, and per-horizon isotonic calibration measurably worsens coherence rather than improving it.


## 4.3 The discrete-time survival formulation

Motivation. The ordering constraint is a consequence of the definition of cumulative incidence, so the natural remedy is to estimate a quantity from which ordering follows automatically, rather than to estimate the ordered quantities directly and repair them.

Design. Partition the time axis into K bins whose upper edges are exactly the horizons of interest:

B_1 = (0, h_1],  B_2 = (h_1, h_2],  …,  B_K = (h_{K−1}, h_K]

and define the discrete-time hazard as the probability that the event falls in bin k given that it has not occurred by the start of that bin:

λ_k(x) = P( T ∈ B_k │ T > h_{k−1}, x )	(4.2)

The survival function is the product of per-bin survivals,

S_k(x) = Π_{j=1..k} ( 1 − λ_j(x) ) = P( T > h_k │ x )	(4.3)

and the cumulative incidence required by Equation (4.1) is its complement, which is the product-limit identity:

F_k(x) = P( T ≤ h_k │ x ) = 1 − Π_{j=1..k} ( 1 − λ_j(x) )	(4.4)

Technical advantage. Monotonicity is now a theorem rather than a hope. Since λj ∈ [0,1], every factor (1 − λj) lies in [0,1], so

S_{k+1} = S_k · ( 1 − λ_{k+1} ) ≤ S_k   ⟹   F_{k+1} ≥ F_k	(4.5)

The argument uses no property of the learner beyond the range of its output. Any model that emits a value in [0,1] per bin produces a coherent set of horizon probabilities under Equation (4.4). This is why the coherence result reported in Section 5.4 is learner-independent while the calibration result is not, and it is the single most important structural property of the system developed here.


## 4.4 The likelihood under censoring

Let kt be the bin in which the event occurs for sample t, and let ct be the last bin fully survived before censoring. Define the at-risk set Rt = {1 … min(kt, ct)} — the bins the sample actually entered — and the per-bin indicator zt,k = 1{ k = kt }. The discrete-time survival log-likelihood then collapses into a single expression covering both the censored and uncensored cases:

ℓ = Σ_t Σ_{k ∈ R_t} [ z_{t,k} log λ_k(x_t) + (1 − z_{t,k}) log(1 − λ_k(x_t)) ]	(4.6)

Equation (4.6) is exactly a binary cross-entropy over the expanded set of (sample × at-risk bin) pairs. The practical consequence is that fitting a discrete-time survival model requires no specialised software: the data are expanded from wide to long format, the bin index k is appended as a feature so that the model can learn the shape of the baseline hazard, and a single binary classifier is fitted. A censored sample contributes a (1 − λk) term for every bin it survived rather than being discarded.

On this dataset the expansion takes 10,260 rows to approximately 34,000 (sample, bin) pairs. The measured per-bin hazard rates, pooled over folds, are reported in Table 4.2.


## 4.5 Why class reweighting is inadmissible here

The standard response to a rare-event task is to reweight the positive class, for example through the scale_pos_weight parameter of a gradient-boosting implementation. That response must not be used in the hazard arm, for a reason specific to Equation (4.4).

Reweighting the positive class by a factor w transforms the fitted probability monotonically,

λ̃ = w λ / ( w λ + (1 − λ) )	(4.7)

Ranking metrics are invariant under this transformation, since AUPRC and AUROC depend only on the order of scores. The probability scale, however, is destroyed — and Equation (4.4) multiplies K of those probabilities together. A per-bin multiplicative calibration error ε therefore compounds across the horizon axis as

F̂_k / F_k ~ ( 1 + ε )^k	(4.8)

so the distortion grows with the horizon, precisely where calibration is already weakest. Both the hazard arm and the independent-classifier control arm are consequently fitted unweighted, which has the additional benefit of keeping the comparison between them fair.


## 4.6 Feature construction

Motivation. The system must predict from quantities a handset actually possesses at the instant of prediction. Two constraints follow: no feature may use information from the future, and no feature may use information from a different drive.

Design. One hundred and fifty-two candidate columns are constructed and 107 survive a degenerate-feature filter that removes columns with zero variance or more than 50 % missing values on the training rows. They fall into four blocks, summarised in Table 4.3.

Every rolling window is strictly backward-looking and closes at the prediction instant t, and window computation is performed per drive so that no window spans a drive boundary. Features are standardised using statistics computed on the training partition only; a scaler fitted on the pooled dataset is itself a leak, and although a small one, it is among the first things a careful reviewer checks.

The signalling block requires an explicit leakage guard. A measurement report is a causal antecedent of the handover it triggers, and it is also, in the log, nearly simultaneous with it. A naive "time since last A3 report" feature therefore carries information about the very handover being predicted. The guard applied here excludes any report falling inside the prediction window itself, so that a signalling feature evaluated at t for horizon h may only reference reports transmitted at or before t. Section 5.11 reports what happens when the guard is removed.


## 4.7 Models compared

Seven learners are compared under identical folds, identical seeds and the identical hazard formulation. The comparison is designed so that the only thing varying between arms is the learner.

The Event A3 rule. The deployed rule is scored as if it were a predictor, using the recovered configuration of Table 3.1 to determine when the entry condition of Equation (2.1) holds. This is the most important baseline in the thesis because it is what is presently running in the network.

Logistic regression. A regularised linear model over the 107 features, included as the simplest learner that can use the full feature set.

Gradient-boosted trees. LightGBM [30] is the primary model. It is chosen for a tabular task with heterogeneous, partly missing features of mixed scale, where axis-aligned splits and native missing-value handling are well matched to the data.

Multi-layer perceptron. A feed-forward network over the same tabular features, included to separate the contribution of non-linearity from that of temporal memory.

Sequence models. A temporal convolutional network, a Transformer encoder and a gated recurrent unit, each consuming a window of raw per-second measurements rather than the engineered summary features. These arms test whether a model that learns its own temporal representation outperforms one given hand-constructed rolling statistics.

Every neural arm receives an equal hyperparameter budget of twenty trials; the tree and linear arms receive the same budget. Section 5.2 reports the outcome, which is that no arm with temporal memory overtakes the tabular arms on a dataset of this size.


## 4.8 Calibration

Ranking quality is insufficient for the task stated in Section 1.3, which requires the asserted probability to correspond to an empirical frequency. Three calibration treatments are evaluated.

Temperature scaling [31] fits a single scalar on a held-out partition, dividing the logits before the sigmoid. It is the least expressive treatment and cannot alter the ranking.

Isotonic regression [32] fits a non-decreasing step function per horizon. It is more expressive and can correct a wider class of miscalibration, but it consumes a held-out split and, applied per horizon, is free to reorder the horizons relative to one another.

The monotone projection repairs an incoherent set of horizon outputs by projecting them onto the monotone cone. It is implemented for the control arm only, since the hazard formulation makes it unnecessary.

Calibration quality is reported as the expected calibration error, computed as the weighted mean absolute difference between confidence and empirical frequency across equal-mass bins, with the Brier score reported alongside it.


## 4.9 Evaluation protocol

Motivation. The protocol is the component most likely to invalidate a result on data of this kind, because adjacent one-second samples within a drive are near-duplicates of one another. Section 5.3 measures the consequence.

Design. The evaluation protocol has five elements.

Grouping. The unit of splitting is the whole drive. A drive appears either in training or in test on a given fold, never in both. Figure 4.2 illustrates the rotation.

Rotation. A four-fold rotation over the 57 drives ensures that every drive is tested exactly once per seed, with approximately 14 drives held out against 43 in training on each fold.

Repetition. The rotation is repeated with five random seeds, producing twenty paired observations per comparison. The reason is not cosmetic. With four folds alone, a paired test over four observations cannot attain a p-value below 0.125 regardless of the size of the effect, so the test would report its own resolution limit rather than a property of the data.

Interval estimation. Confidence intervals are obtained by a cluster bootstrap that resamples whole drives with replacement, because samples within a drive are not independent.

Fold hygiene. The feature scaler, the decision threshold and the probability calibrator are fitted inside the training partition of each fold only.

Metrics. Four families are reported. Ranking quality is reported as AUPRC, always accompanied by the prevalence floor and the lift over it, together with AUROC. Calibration is reported as expected calibration error and Brier score. Coherence is reported as the fraction of samples on which the horizon ordering is violated. Event-level cost is reported as the fraction of handover events detected, the number of false alarms per hour and per kilometre, and the distribution of lead times. Reporting all four families is deliberate: Wagner et al. [28] show that no single aggregate metric for event detection satisfies all desirable properties, so the event-level figures are reported alongside the row-level ones rather than instead of them.


## 4.10 Distribution-free risk control

Motivation. A probability is not yet an operating point. Converting the model output into a warning requires a threshold, and an operator is entitled to know what that threshold guarantees on drives it has not seen.

Design. Let λ ∈ Λ index a family of alarm thresholds ordered by decreasing strictness and let R(λ) be a bounded, non-increasing risk. Conformal risk control [20] selects

λ̂ = inf { λ : ( n·R̂(λ) + B ) / ( n + 1 ) ≤ α }	(4.9)

where R̂(λ) is the empirical risk over n exchangeable calibration units and B bounds the loss, here B = 1. The guarantee is that E[Rn+1(λ̂)] ≤ α for a fresh exchangeable unit, distribution-free, with no assumption on the model or on the data-generating process beyond exchangeability.

The exchangeable unit is the drive. This is the choice that makes the guarantee meaningful, and it is the contribution of this section. Samples within a drive are not exchangeable with samples from a different drive: they share a cell sequence, a traffic condition and a trajectory. The risk is therefore defined as the per-drive miss rate

R_d(λ) = 	{ t ∈ d : y_t = 1 ∧ p̂_t < λ }

and R̂(λ) averages over calibration drives rather than over samples.

Technical advantage, and a design rule that follows from it. Equation (4.9) can be satisfied only if its left-hand side can reach α at all. At the most permissive threshold R̂ = 0, so the smallest attainable value is B/(n+1), giving the feasibility floor

α ≥ 1/(n+1)   ⟺   n ≥ 1/α − 1	(4.11)

Equation (4.11) is a campaign-design rule: a study that wishes to promise a 5 % miss rate requires at least 19 calibration drives, and one promising 2 % requires 49, independently of how good the model is. Pooling calibration drives across the four campaigns here gives n = 28 and therefore α ≥ 0.034. This rule appears nowhere in the handover literature, and it determines how much driving a study must do before its guarantee is even expressible.


## 4.11 Point-process analysis of handover arrivals

Motivation. The ping-pong behaviour of Section 5.9 suggests that handovers do not arrive independently. Quantifying that clustering requires a model of the arrival process itself rather than of the per-sample probability.

Design. The handover arrival stream on each drive is modelled as a self-exciting Hawkes process [21], [22] with conditional intensity

μ(t) = μ_0 + Σ_{t_i < t} α · exp( −β ( t − t_i ) )	(4.12)

in which each arrival raises the intensity of subsequent arrivals by α and the excitation decays at rate β. The branching ratio α/β is the expected number of direct offspring per event and summarises the strength of the clustering.

Validation. A fit alone is not evidence of self-excitation. Following the networking precedent of Price-Williams and Heard [24], the fit is validated by the residual analysis of Ogata [23]: the time axis is rescaled by the fitted compensator, and the transformed inter-arrival times are tested against a unit-rate exponential distribution by a Kolmogorov–Smirnov test on held-out drives. Section 5.10 reports both the branching ratio and the outcome of that test, including the respect in which the test rejects the fitted kernel.

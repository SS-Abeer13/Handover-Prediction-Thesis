@@TITLEPAGE
@@T|UNCERTAINTY-AWARE MULTI-HORIZON HANDOVER PREDICTION FROM LTE DRIVE-TEST SIGNALLING
@@N|Abeer Saadman ([Student ID])
@@S|A Thesis Submitted to the Academic Faculty in Consideration of Partial Fulfillment for the Requirements of the Degree of
@@D|BACHELOR OF SCIENCE IN ELECTRICAL AND ELECTRONIC ENGINEERING
@@I|Department of Electrical and Electronic Engineering
@@I|Islamic University of Technology (IUT)
@@I|Gazipur, Bangladesh
@@Y|Winter Semester, 2026
@@ENDTITLE

@@PRELIM|DECLARATION

I do hereby declare that the work presented in this thesis, entitled *Uncertainty-Aware Multi-Horizon Handover Prediction from LTE Drive-Test Signalling*, is the outcome of the investigation and research carried out by me under the supervision of [Supervisor Name, Title], Department of Electrical and Electronic Engineering, Islamic University of Technology (IUT), Gazipur, Bangladesh.

I further declare that neither this thesis nor any part of it has been submitted anywhere else for the award of any academic qualification, certificate, diploma or degree. All sources of information and material used in the preparation of this thesis have been duly acknowledged and cited.

@@CENTER|
@@CENTER|
@@CENTER|………………………………………
@@CENTER|Abeer Saadman ([Student ID])
@@CENTER|Date: ……………………

@@PRELIM|APPROVAL

@@CENTERB|UNCERTAINTY-AWARE MULTI-HORIZON HANDOVER PREDICTION FROM LTE DRIVE-TEST SIGNALLING

@@CENTER|
@@CENTER|Abeer Saadman ([Student ID])
@@CENTER|

The thesis titled above has been examined and approved as partial fulfillment of the requirements for the degree of Bachelor of Science in Electrical and Electronic Engineering.

@@CENTER|
@@CENTER|
@@CENTER|………………………………………
@@CENTER|[Supervisor Name, Title]
@@CENTER|Supervisor and [Associate/Assistant] Professor
@@CENTER|Department of Electrical and Electronic Engineering
@@CENTER|Islamic University of Technology (IUT), Boardbazar, Gazipur-1704
@@CENTER|
@@CENTER|Date: ……………………

@@PRELIM|ACKNOWLEDGEMENTS

All praise is due to Allah, the Most Gracious and the Most Merciful, whose mercy made the completion of this work possible.

I wish to express my sincere gratitude to my supervisor, [Supervisor Name, Title], Department of Electrical and Electronic Engineering, Islamic University of Technology, for the guidance, patience and critical reading that shaped this thesis. His insistence that a measured claim is worth more than an impressive one is the single most useful lesson I carry out of this project, and it is visible in every chapter that follows.

I thank the Department of Electrical and Electronic Engineering for providing access to the drive-test instrumentation without which none of the measurement campaigns reported here could have been conducted, and the faculty members whose questions during the progress presentations sharpened the evaluation protocol considerably.

I am grateful to the authors of the publicly released LTE drive-test dataset used for external validation in Chapter 5; the willingness to publish measured data under a citable identifier is what made an independent check of this work possible at all.

Finally, I thank my family for their patience during the field campaigns and the long analysis that followed.

@@PRELIM|ABSTRACT

Long Term Evolution networks execute handovers through Event A3, a rule that fires only after a neighbour cell has already become stronger than the serving cell by a configured offset and has remained stronger for a full time-to-trigger. The rule is therefore reactive by construction: it can issue a response, not a warning. This thesis asks whether the next handover can instead be forecast from the measurements a handset already reports, how far ahead, and with what guarantee.

Four drive-test campaigns were conducted on a live commercial LTE network in Dhaka and Gazipur, yielding 57 drives, 10,260 samples at one hertz and 938 handovers whose ground truth is decoded from RRC signalling rather than inferred from vendor counters. Because measurement identifiers are scoped to the message carrying them, a configuration timeline is replayed so that each report resolves against the configuration actually in force; this correction shows the deployed A3 offsets on this network to be negative rather than the positive values assumed in the prediction literature. The task is then posed as discrete-time survival: instead of five independent classifiers, one per look-ahead time, a single model estimates the per-interval hazard and horizon probabilities are recovered as products of hazards, so ordering holds by construction for any learner. Seven models are compared under a grouped-drive rotation repeated over five seeds, with intervals bootstrapped over drives, and a warning threshold is certified by conformal risk control whose exchangeable unit is the whole drive.

One second before a handover, gradient-boosted trees reach AUROC 0.933 and AUPRC 0.784 against a 6.7 % prevalence floor, a lift of 11.7×, at a calibration error of 0.024, where the deployed A3 rule scored as a predictor reaches 0.653. Replacing grouped-drive splitting with random-row splitting inflates a gated recurrent unit by 74 % and logistic regression by 4 %, so a careless protocol reorders the model ranking rather than merely raising every score. The hazard formulation yields zero horizon-ordering violations against 43.6 % for independent classifiers. Holding out each campaign in turn, AUROC remains between 0.909 and 0.949, including 0.927 on a highway corridor driven after every modelling decision had been frozen, and the model transfers to an independent public dataset at 0.752 against 0.745 for a model trained on it directly. Serving dwell time alone reaches AUROC 0.874 while the serving-to-neighbour gap the network thresholds on reaches 0.566, and 62.9 % of A3 reports are not followed by a handover within two seconds.

The contribution is not a new learning algorithm but a signalling-grounded, leakage-safe and uncertainty-aware framework that converts measured handover events into coherent multi-horizon probabilities, reports the operating cost of the resulting warning, and validates the result on a corridor and a dataset it had never seen.

**Keywords:** LTE, handover prediction, Event A3, RRC signalling, discrete-time survival analysis, conformal risk control, calibration, drive test.

@@PRELIM|TABLE OF CONTENTS

@@TOC

@@PRELIM|LIST OF FIGURES

@@LOF

@@PRELIM|LIST OF TABLES

@@LOT

@@PRELIM|LIST OF ACRONYMS

@@ACRO|3GPP|Third Generation Partnership Project
@@ACRO|A3|Event A3 (neighbour becomes offset better than serving)
@@ACRO|AUPRC|Area Under the Precision–Recall Curve
@@ACRO|AUROC|Area Under the Receiver Operating Characteristic Curve
@@ACRO|CHO|Conditional Handover
@@ACRO|CO|Course Outcome
@@ACRO|CORAL|Correlation Alignment
@@ACRO|CRC|Conformal Risk Control
@@ACRO|E-UTRAN|Evolved Universal Terrestrial Radio Access Network
@@ACRO|EARFCN|E-UTRA Absolute Radio Frequency Channel Number
@@ACRO|ECE|Expected Calibration Error
@@ACRO|GRU|Gated Recurrent Unit
@@ACRO|GPS|Global Positioning System
@@ACRO|HOM|Handover Margin
@@ACRO|KPI|Key Performance Indicator
@@ACRO|LTE|Long Term Evolution
@@ACRO|MLP|Multi-Layer Perceptron
@@ACRO|PCI|Physical Cell Identity
@@ACRO|PO|Program Outcome
@@ACRO|QoE|Quality of Experience
@@ACRO|RLF|Radio Link Failure
@@ACRO|RRC|Radio Resource Control
@@ACRO|RSRP|Reference Signal Received Power
@@ACRO|RSRQ|Reference Signal Received Quality
@@ACRO|SINR|Signal-to-Interference-plus-Noise Ratio
@@ACRO|TCN|Temporal Convolutional Network
@@ACRO|TTT|Time-to-Trigger
@@ACRO|UE|User Equipment

@@CHAPTER|1|INTRODUCTION

Mobility is the property that distinguishes a cellular network from every other access technology, and the handover is the mechanism that delivers it. Each time a user equipment moves beyond the useful coverage of its serving cell, the network must transfer the connection to a neighbour without interrupting the service carried on it. On a dense urban network this happens constantly: across the measurement campaigns reported in this thesis, a handover occurred on average once every eleven seconds of driving. Every one of those events is a brief window in which throughput drops, latency rises and, occasionally, the radio link fails outright.

This chapter states the problem the thesis addresses, the reason it is worth addressing, and the objectives against which the work should be judged. Section 1.1 describes how handover is triggered in Long Term Evolution (LTE) and why the triggering rule is structurally incapable of providing advance warning. Section 1.2 quantifies the cost of that limitation on measured data. Section 1.3 states the problem formally, Section 1.4 lists the objectives, Section 1.5 bounds the scope, Section 1.6 summarises the contributions, and Section 1.7 describes the organisation of the remainder of the report.

## 1.1 Background

In an LTE network the user equipment (UE) continuously measures the Reference Signal Received Power (RSRP) and Reference Signal Received Quality (RSRQ) of its serving cell and of the neighbour cells it can detect, and reports those measurements to the network when a condition configured by the network is satisfied [1]. The dominant condition governing intra-frequency mobility is Event A3, which is defined in 3GPP TS 36.331 as the condition that a neighbour cell becomes better than the serving cell by a configured offset, and that this relation persists for a configured time-to-trigger (TTT) before the report is sent [1].

Two properties of that definition matter for this thesis. First, the condition is written on a comparison that must already hold: the neighbour must have *become* better before anything happens. Second, the TTT imposes an additional delay whose purpose is to suppress spurious triggering caused by fast fading. Together they guarantee that by the time a measurement report leaves the handset, the radio environment has already changed. The network then evaluates the report and, if it decides to proceed, issues an `RRCConnectionReconfiguration` message carrying `mobilityControlInfo`, which is the handover command itself.

Figure 1.1 draws that sequence against a measured pair of serving and neighbour traces. Event A3 is therefore a reaction rule and not a prediction rule, and this is not a deficiency of the standard. The rule was designed to decide reliably, not early, and it performs that function well. What the standard does not provide, and what an increasingly latency-sensitive service mix increasingly wants, is advance notice: an indication, one or two seconds before the fact, that a handover is imminent, so that the target cell can be prepared, the transmission schedule adjusted, or an unnecessary transfer suppressed.

@@FIG|/home/claude/figs/png_print/fig01_a3_event.png|Figure 1.1 Event A3 fires only after the neighbour has been better than the serving cell by a configured offset for a full time-to-trigger. The dominant configuration measured on this network is a +1 dB offset with a 320 ms time-to-trigger.|6.3

## 1.2 Motivation

The cost of reacting rather than anticipating is measurable, and it was measured on the data collected for this thesis rather than assumed from the literature. Across four campaigns totalling 2.9 hours of driving, 938 signalling-confirmed handovers were observed, a mean interval of eleven seconds with a median gap of three and a half seconds between consecutive events. Of those handovers, 24.5 % returned to the cell just vacated within fifteen seconds; each such pair represents two signalling exchanges and two service interruptions that produced no net change in serving cell. The radio link failed and required re-establishment 341 times. Of 7,385 Event A3 reports transmitted by the handset, 62.9 % were not followed by a handover command within two seconds, indicating that the majority of the control-plane traffic the rule generates does not result in mobility at all.

These are not pathological numbers for a dense urban deployment; they are what the deployed configuration produces. They do, however, establish that even a short prediction horizon has something to act on. A warning one second ahead of a handover command is sufficient time for the network to complete target-cell preparation, and a warning that a handover is likely to be reversed within fifteen seconds is sufficient information to consider not performing it.

The natural question is whether such a predictor already exists. A screening of 108 publications, of which 22 were audited in detail in Chapter 2, indicates that it does not exist in a form an operator could act upon. Of those 22 models, none holds out the mobility unit — a whole drive or a whole device session — when evaluating a per-timestep classification task on measured radio data; none reports a calibration curve, an expected calibration error or a Brier score; and none reports how early its warnings arrive or how many false alarms they generate per unit time. Seven report headline accuracy on tasks whose positive-class prevalence lies between 0.86 % and 11 %, where a constant negative prediction already scores between 89 % and 99 %.

## 1.3 Problem statement

The problem addressed in this thesis is the following. Given the measurements available to a handset at time *t* — serving and neighbour signal levels and qualities, their short-term statistics, mobility state and the recent signalling history — estimate the probability that the network will issue a handover command within *h* seconds, for several values of *h* simultaneously, such that:

- the estimates are mutually consistent, in the sense that the probability for a longer horizon is never smaller than that for a shorter one;
- the estimates are calibrated, in the sense that an asserted probability of *p* corresponds to an empirical event frequency near *p*;
- the evaluation protocol cannot transfer information from a test drive into training; and
- the warning derived from the estimates carries a stated bound on the fraction of handovers it will miss on future drives.

None of these four requirements is satisfied jointly anywhere in the audited literature, and the first and fourth are not satisfied anywhere at all in the handover-prediction setting.

## 1.4 Objectives

The specific objectives of this thesis are as follows.

**O1.** To predict the next handover at five look-ahead times — 0.5, 1, 2, 3 and 5 seconds — using only quantities observable at the handset at the instant of prediction.

**O2.** To establish an evaluation protocol that cannot leak information between training and test, by grouping every split at the level of the whole drive, and to measure how much that protocol is worth relative to the random-row splitting that is standard in the comparator literature.

**O3.** To make the resulting probabilities usable by an operator: mutually coherent across horizons, calibrated in value, and accompanied by a distribution-free bound on the per-drive miss rate.

**O4.** To test whether the result generalises beyond the campaign on which it was developed, both to a corridor and speed regime held out entirely and to an independently collected public dataset.

**O5.** To explain the mechanism underlying the prediction, rather than reporting accuracy alone, and in doing so to characterise the behaviour of the deployed mobility configuration on this network.

## 1.5 Scope and limitations

The scope of this work is deliberately bounded, and the bounds are stated here rather than deferred to the conclusion.

The study covers one commercial LTE operator, four measurement days, two mobility regimes and 57 drives. It does not claim that the numerical results transfer to another operator or another radio access technology, although Chapter 5 reports an external validation that bears on that question. The measurement export is sampled at one hertz, which caps the fraction of handover events that can in principle be resolved at 90.5 %; this is a property of the instrument and not of the models.

The system developed here is an offline predictor evaluated on recorded data. It is not integrated into a network, and no claim is made that deploying it would improve any network key performance indicator. In particular, no causal claim is made about the benefit of acting on the warning, for the reason given in Chapter 5: the logging policy is deterministic, so the propensities required for off-policy evaluation are zero or one and the causal estimand is not identified on observational data of this kind. Only a counting upper bound is reported.

Finally, the thesis makes no claim relating to human health. No human subjects were involved, no exposure measurements were taken, and the impact analysis in Chapter 6 is confined to what the measurements support.

## 1.6 Contributions

The contributions of this thesis are the following five, each of which is supported by a specific result in Chapter 5.

1. **A discrete-time hazard formulation of handover prediction** that renders five look-ahead horizons mutually consistent from a single model fit, for any learner, without a held-out calibration split and without post-hoc correction. Measured effect: 0 % horizon-ordering violations against 43.6 % for independent per-horizon classifiers.

2. **A measurement of the value of grouped evaluation** on drive-test radio data, showing that the inflation caused by random-row splitting is architecture-dependent — 74 % for a gated recurrent unit against 4 % for logistic regression — and therefore reorders the model ranking rather than merely raising it.

3. **A distribution-free risk guarantee whose exchangeable unit is the drive**, together with the campaign-design rule that follows from it: the number of calibration drives determines the tightest miss-rate target a study can express, independently of model quality.

4. **A signalling-decoding correction**, in the form of a configuration timeline for message-scoped measurement identifiers, which establishes that the deployed A3 offsets on this network are negative rather than the positive values assumed in the prediction literature.

5. **Two characterisations of network behaviour that the prediction literature has not modelled**: the A3 report-conversion rate, measured at 62.9 % declined within two seconds, and a ping-pong rate reported together with the three definitional choices that determine its value.

## 1.7 Organisation of the report

The remainder of this report is organised as follows. Chapter 2 reviews the four literatures that bear on this problem — cellular measurement studies, handover prediction, survival analysis and distribution-free uncertainty quantification — presents a protocol audit of the 22 most comparable prediction models, and sets out the methodology adopted, including the approaches that were considered and rejected. Chapter 3 describes the measurement campaign, the signalling-decoding procedure and the construction of the dataset. Chapter 4 develops the predictive formulation, the feature construction, the models compared, the evaluation protocol and the risk-control procedure. Chapter 5 reports and discusses the results against the objectives of Section 1.4. Chapter 6 demonstrates how the work addresses the course outcomes, program outcomes, knowledge profiles and complex engineering problem and activity attributes required of a capstone project. Chapter 7 concludes and identifies the work that follows from the limits of the present study.
@@CHAPTER|2|LITERATURE REVIEW AND METHODOLOGY

Four bodies of work bear on the problem stated in Chapter 1, and they nearly meet without quite touching. The cellular measurement literature establishes what handovers look like in deployed networks but does not build predictors. The handover-prediction literature builds predictors, but predominantly on simulated data and predominantly without an evaluation protocol that would survive scrutiny. The survival-analysis and point-process literatures supply exactly the right mathematical objects — a discrete-time hazard and a self-exciting process validated by time rescaling — but have not been directed at mobility data. The distribution-free uncertainty literature supplies guarantees, but for signal-processing tasks whose exchangeability structure differs from that of an event stream recorded along a drive.

This chapter reviews each in turn, then presents a quantitative audit of the 22 most comparable prediction models, states the research gap that the audit establishes, and describes the methodology adopted in response, including the alternatives that were considered and rejected.

## 2.1 LTE mobility and the Event A3 trigger

The mobility procedure in E-UTRAN is specified in 3GPP TS 36.331 [1] and described at system level in TS 36.300 [2]. The network configures the UE with measurement objects, report configurations and measurement identities that bind the two; the UE evaluates the configured entry condition against its filtered measurements and transmits a `MeasurementReport` when the condition has held for the configured time-to-trigger.

For intra-frequency mobility the governing condition is Event A3. Writing *M*<sub>n</sub> for the measured neighbour quantity, *M*<sub>s</sub> for the serving quantity, *Off* for the configured offset, *Ocn* and *Ocs* for cell-individual offsets and *Hys* for hysteresis, the entry condition of TS 36.331 is

@@EQ|M_n + Ocn − Hys  >  M_s + Ocs + Off|(2.1)

and the condition must remain satisfied throughout the time-to-trigger interval before the report is sent. The decision to hand over is then taken by the network, not the UE, and is communicated by an `RRCConnectionReconfiguration` message carrying `mobilityControlInfo`.

Three consequences follow, and all three are used later in this thesis. First, the report is evidence that the network *may* hand over, not that it will; the conversion rate from report to command is an empirical quantity and is measured in Chapter 5. Second, the parameters *Off*, *Hys* and the TTT are operator-configured and are not observable without decoding the signalling; the prediction literature that assumes textbook values is therefore assuming something it has not checked. Third, because the condition is defined on a state that must already obtain and must then persist, the earliest instant at which Event A3 can produce any output is strictly after the radio environment has changed.

## 2.2 The measurement literature

A mature line of work in the networking-measurement community recovers operator mobility configurations from control-plane traces on live networks. Deng et al. [3] present the LTE precedent, a measurement study of operational 4G mobility configurations and their consequences. Ghoshal et al. [4] perform the equivalent analysis at large scale on contemporary networks, extracting hysteresis, threshold, offset, time-to-trigger and trigger quantity for events A1–A6, B1 and B2 per operator and band, over more than 15,000 km of driving and 48,426 handovers on three operators. Hassan et al. [5] establish the use of commercial diagnostic tooling for RRC extraction as accepted methodology, and Liu et al. [6] read `mobilityControlInfo` for mobility analysis without recovering the numerical parameters.

This literature is directly relevant in two ways. Methodologically, it legitimises the decoding pipeline used in Chapter 3 rather than competing with it: the extraction of deployed A3 parameters from `measConfig` is established practice, and this thesis does not claim it as a contribution. Substantively, it supplies the comparison points against which the configuration measured here is interpreted; Ghoshal et al. report positive A3 offsets of +6 to +10 dB and shortest time-to-trigger values of 256 to 640 ms on the operators they study, whereas the network measured here runs offsets from −15 dB to +5 dB and a shortest time-to-trigger of 160 ms.

What this literature does not do is predict. Ghoshal et al. state explicitly that they perform no machine-learned prediction, no off-policy evaluation and no counterfactual analysis; the work is descriptive by design. The ping-pong rates these studies report are likewise descriptive, and, as Section 2.4 discusses, are reported under definitions that differ enough to change the number by a factor of two.

## 2.3 The prediction literature and a protocol audit

A large body of work predicts handover, radio-link failure or next-cell occupancy using learned models. Recent systematic reviews characterise it unfavourably from the outside. Ankome and Hanada [7] screened 429 records under a PRISMA protocol, retained 336 after deduplication and included 49 studies spanning 2010–2025; they were unable to perform a meta-analysis because simulators and outcome definitions were too heterogeneous, they observe that most studies report percentage improvements over baselines of their own choosing rather than absolute performance, and they report that data splitting, class imbalance and calibration receive minimal explicit discussion anywhere in the included set. Saoud et al. [8] find that the field lacks quantitative cross-comparison between strategies, and Chabira et al. [9] enumerate the metric vocabulary actually in use — handover failure rate, latency, quality of service, energy — in which neither calibration nor any prevalence-aware ranking metric appears.

To convert that general complaint into something specific enough to act on, 108 publications were screened for this thesis and the 22 that present a learned or analytical model predicting handover, radio-link failure or next-cell occupancy were audited on protocol quality rather than on headline performance. Table 2.1 reports the audit.

@@TCAP|Table 2.1 Protocol audit of the 22 most comparable prediction models, contrasted with the protocol adopted in this thesis.
| Protocol property | Papers satisfying it | This work |
|---|---|---|
| Splits by drive or route | 0 / 22 | Yes, in every experiment |
| Uses any split coarser than a random row | 5 / 22 | Yes |
| States a split protocol at all | 12 / 22 | Yes, with a freeze manifest |
| Reports a prevalence-aware ranking metric | 2 / 22 | AUPRC with floor and lift |
| Reports calibration (curve, ECE or Brier) | 0 / 22 | ECE, Brier, temperature scaling, conformal risk control |
| Reports lead time or false alarms per hour | 0 / 22 | Both, and per kilometre |
| Reports headline accuracy on an imbalanced task | 7 / 22 | Never |
| Releases code | 2 / 22 | Planned |
| Releases data | 1 / 22 | Planned |

Two observations from the audit are load-bearing for the remainder of this thesis.

The first concerns metrics. Seven of the 22 report accuracy on tasks whose positive prevalence lies between 0.86 % and 11 %, at which a constant negative prediction scores between 89 % and 99 %; three of the headline figures so reported are 98.03 %, 99.84 % and 94.83 %. A related failure appears in a railway radio-link-failure study that reports area under the ROC curve above 0.95 for all six architectures it compares, on a task with approximately one positive per five hundred samples, and consequently separates none of them.

The second concerns splitting, and the exceptions are named rather than rounded away. Five of the 22 do split on something coarser than a random row: by spatial zone, by device, by time under a rolling-origin protocol on operator data, by travel day [10], and by deployment event [11]. None of the five, however, holds out the mobility unit for a per-timestep classification task on measured radio; the two most recent additions are regression tasks in which prevalence does not arise, and the strongest protocol in the set addresses next-day cell-level radio-link failure rather than a per-sample mobility forecast.

A structural feature of this literature explains the pattern. Protocol quality and measurement quality are anti-correlated within it. The studies with the cleanest splits operate on ray-traced or SUMO-simulated trajectories [10], on aggregated operator key performance indicators, or at cell-and-day granularity [11]; the studies carrying real per-sample drive-test radio, whose data most resembles that used here, are precisely those whose split protocol is unstated. Recent graph-based models illustrate both halves: TH-GCN [12] builds a dynamic UE–cell graph for dense vehicular scenarios but is simulated, states no split protocol and reports relative deltas against baselines of its own choosing, while GRIMCELL [11] applies graph learning to radio-planning, configuration-management and performance-management data from a commercial LTE-A Pro network across 55 real deployment events, but predicts post-deployment key performance indicators per cell per day and is therefore a planning tool rather than a per-second warning system. Graser et al. [13] organise the trajectory-learning literature by data density and observe that the dense individual-trace regime, in which one-hertz drive data sits, is where the literature is thinnest for event prediction as opposed to location prediction.

The narrow claim that the audit supports, and the one made in this thesis, is therefore the following: of twenty-two audited models, ten state no split protocol at all, five split on a unit coarser than a row, and none holds out the mobility unit for a per-timestep classification task on measured radio data; none reports calibration; and none reports how early its warnings arrive.

## 2.4 Ping-pong and its definitional instability

Handover ping-pong — a return to a recently vacated cell — is widely reported and inconsistently defined. There is no standardised definition in 3GPP; what exists is a cell return within an author-chosen window, and the window alone moves the reported rate substantially. Zidic et al. [14] report ping-pong measurements on real 4G networks, and Ghoshal et al. [4] report per-operator rates of 15 % to 25 % under a fifteen-second window with a per-handover denominator.

Three choices determine the number, and papers rarely state all three: whether a cell is identified by physical cell identity alone or by physical cell identity together with carrier; whether any return within the window counts or only a return to the immediately preceding cell; and whether the denominator is the set of raw handover events or of quality-controlled ones. The consequences are severe enough to invalidate cross-paper comparison: Amirova et al. [15] report a ping-pong rate of 0.13 % because they divide by measurement records rather than by handovers. Chapter 5 reports the full ladder of these choices on a single fixed set of 938 handovers, where the rate moves from 24.5 % to 41.3 % without any change in the underlying data.

## 2.5 Survival analysis as the appropriate formulation

The task posed in Section 1.3 — the probability that an event occurs within *h* seconds, for several values of *h* — is a time-to-event problem, and the appropriate formulation is therefore a survival model rather than a set of independent classifiers. Wiegrebe et al. [16] review 61 deep time-to-event methods and place the discrete-time route, in which the time axis is binned and binary indicators per interval are trained as classification, firmly in the mainstream. Thorsen-Meyer et al. [17] construct structurally the same object for intensive-care outcome prediction, with a censoring-aware log-likelihood over discretised windows.

This literature is used here without any claim of novelty attaching to the formulation itself, and stating that plainly removes an obvious reviewer objection. What is new is where the formulation is pointed: no model in the 22-paper audit of Section 2.3 poses handover prediction this way, and every one of them therefore inherits the incoherence described in Section 4.2.

One departure from the survival literature is deliberate. That literature evaluates predominantly with the concordance index and the integrated Brier score, both of which aggregate over the horizon axis. An operator, however, acts at a single horizon. A model that ranks well on average while asserting that the probability of a handover within one second exceeds the probability within three seconds on 43.6 % of samples is not deployable whatever its concordance index. Chapter 4 therefore evaluates horizon-wise, reporting AUPRC at each horizon together with a coherence-violation rate.

## 2.6 Distribution-free uncertainty quantification

Conformal prediction supplies finite-sample, distribution-free guarantees under an exchangeability assumption, and it has already been applied inside wireless communications by a strong group. Cohen, Park, Simeone and Shamai [18] apply split and cross-validation conformal prediction to demodulation, modulation classification and channel prediction; Simeone, Park and Zecchin [19] generalise the approach into a deployment lifecycle covering pre-deployment calibration and hyperparameter selection, monitoring under distribution shift, and post-deployment counterfactual analysis. Conformal risk control, which extends the guarantee from coverage of a prediction set to the expectation of a bounded monotone risk, is due to Angelopoulos et al. [20].

The claim made in this thesis is consequently narrower than it might appear, and the narrowing is deliberate. The guarantees in [18] and [19] are over prediction sets, for tasks that are independent and identically distributed within a frame. The guarantee developed in Chapter 4 is over a *risk* — an operator key performance indicator, the per-drive miss rate — on a stream that is exchangeable only at the level of a whole drive. The identification and defence of that exchangeability unit is the contribution; the campaign-design floor that follows from it is its consequence; and no wireless conformal study located in three screening passes reports a mobility-management case at all.

## 2.7 Point processes and the self-excitation of handover arrivals

Handover events do not arrive independently. The self-exciting point process introduced by Hawkes [21] is the standard model for arrival streams in which each event raises the intensity of subsequent events, and Laub et al. [22] provide the contemporary reference treatment, including the branching-ratio interpretation used in Chapter 5. Fitting such a process is not, by itself, evidence that the process is self-exciting; the fit must be checked. The residual analysis of Ogata [23], in which the time axis is rescaled by the fitted compensator and the transformed arrivals tested against a unit-rate Poisson process, is the standard check, and Price-Williams and Heard [24] establish the precedent for its use in a networking context, validating a self-exciting fit to campus and laboratory network traffic by time rescaling with Kolmogorov–Smirnov tests on held-out data. Chapter 5 follows that precedent and reports the test outcome, including where it rejects the fitted kernel.

## 2.8 Evaluation practice imported from adjacent fields

Two further results from adjacent literatures inform the evaluation design and are cited here because they make the negative results of Chapter 5 interpretable rather than embarrassing. Ismail Fawaz et al. [25] benchmark nine unsupervised domain-adaptation algorithms across twelve time-series datasets and find that several published methods perform worse than source-only training with no adaptation at all, and that the adaptation technique rather than the backbone drives the outcome; the null result reported for Deep CORAL [26] in Chapter 5 is therefore consistent with a published benchmark rather than evidence of faulty implementation. Shi et al. [27] supply the shift taxonomy that names the shift encountered here as a device-and-day shift rather than a sensor-modality shift. Wagner et al. [28] show formally that the commonly used point-adjusted metrics for time-series event detection each satisfy only a subset of the desirable properties and that none satisfies all of them, which is the justification for reporting event-level detection rate, lead time and false alarms per hour *alongside* row-level AUPRC rather than in place of it.

Finally, the standards track bears on the choice of horizon. Deb et al. [29] model conditional handover as a discrete-time Markov chain over preparation and execution offsets and timers, and their analysis makes explicit that conditional handover consumes a lead time rather than a label: a model that identifies the correct target cell two hundred milliseconds before the event buys nothing, because the preparation message must be sent, acknowledged and stored. This is the analytical justification for reporting a lead-time distribution rather than a detection rate alone, and for retaining horizons of two, three and five seconds even though the deployed trigger fires within a few hundred milliseconds.

## 2.9 Research gap

Collecting the preceding sections, the gap this thesis occupies can be stated precisely. Measurement-grade ground truth exists, but is not joined to prediction. Prediction models exist, but not under an evaluation protocol that holds out the mobility unit, and not with calibrated outputs or event-level costs. The correct formulation exists in the survival literature, but has not been applied to mobility events. Distribution-free guarantees exist in wireless, but for a different exchangeability structure and not for any mobility-management task.

This work sits in that gap: measurement-grade ground truth obtained from decoded signalling, a borrowed formulation made coherent across horizons, a conformal risk bound whose exchangeability unit is stated and defended, and an evaluation protocol designed to be acceptable to a reviewer from the machine-learning community rather than only to one from the wireless community.

## 2.10 Methodology

The methodology adopted follows directly from the gap. It consists of five stages, illustrated in Figure 2.1, and each stage is developed in detail in Chapters 3 and 4.

@@FIG|/home/claude/figs/png/m14_framework.png|Figure 2.1 The methodology in five stages. Stage 2 supplies the ground truth; Stage 4 is the formulation that keeps the five horizons mutually consistent; Stage 5 is the grouped evaluation protocol.|6.3

**Stage 1 — Collection.** Four drive-test campaigns are conducted on a live commercial LTE network using an instrumented handset, recording a one-hertz radio measurement export and, in parallel, a decoded RRC signalling log.

**Stage 2 — Ground truth and configuration recovery.** Handover instants are taken from decoded `RRCConnectionReconfiguration` messages carrying `mobilityControlInfo`. Because measurement identifiers are scoped to the message that carries them, a configuration timeline is replayed so that every measurement report resolves against the configuration in force at its own timestamp.

**Stage 3 — Feature construction.** One hundred and fifty-two candidate features are constructed from radio, mobility, history and signalling sources; all are strictly causal, closing at the prediction instant, and none crosses a drive boundary.

**Stage 4 — Formulation and modelling.** The task is posed as discrete-time survival. A single model estimates the per-interval hazard and horizon probabilities are recovered by the product-limit identity, which guarantees ordering. Seven learners are compared under identical conditions.

**Stage 5 — Evaluation and risk control.** Splits are grouped by whole drive under a four-fold rotation repeated over five seeds; confidence intervals are bootstrapped over drives; and a warning threshold is certified by conformal risk control whose exchangeable unit is the drive.

### 2.10.1 Approaches considered and rejected

Four alternatives were considered seriously and rejected, and the reasons are recorded here because they constitute part of the methodological argument.

**Independent per-horizon classifiers.** The obvious approach — one binary classifier per look-ahead time — was implemented and retained as a control arm rather than as the primary method. It is rejected as the primary method because it produces mutually contradictory outputs on a large fraction of samples, as Chapter 5 quantifies, and because repairing that defect after the fact costs both a held-out split and predictive performance.

**Random-row cross-validation.** The splitting protocol used by the majority of the comparator literature was implemented solely to measure what it is worth. It is rejected because adjacent one-second samples within a drive are near-duplicates, so a random split places nearly identical rows on both sides of it; Chapter 5 shows that the resulting inflation is architecture-dependent and therefore alters the ranking of models.

**Class reweighting for imbalance.** The standard reflex on a rare-event task is to reweight the positive class. It is rejected in the hazard arm for a reason specific to the formulation: reweighting transforms the fitted probability monotonically, which leaves ranking metrics unchanged but destroys the probability scale, and the product-limit identity multiplies *K* such probabilities together, so a per-interval multiplicative error compounds with the horizon. Both arms are therefore fitted unweighted, which also keeps the comparison between them fair.

**Reinforcement learning of the handover decision.** A decision-theoretic formulation, in which an agent learns when to hand over, was considered and is the formulation adopted by the nearest comparator study available on this network. It is rejected here because it answers a different question: it optimises a decision the network is entitled to make at its own pace, whereas this thesis forecasts an event. Chapter 5 reports a reimplementation of that comparator scored as a predictor, for completeness.
@@CHAPTER|3|MEASUREMENT CAMPAIGN AND GROUND TRUTH

Every claim made in this thesis rests on the quality of the measurement underneath it, and this chapter describes how that measurement was obtained. Section 3.1 describes the instrumentation. Section 3.2 describes the four campaigns and the routes they cover. Section 3.3 describes the signalling-decoding procedure and the configuration-timeline correction that it required. Section 3.4 describes how continuous driving is segmented into drives and quality controlled. Section 3.5 reports the deployed mobility configuration recovered from the signalling, and Section 3.6 summarises the resulting dataset.

## 3.1 Instrumentation

Measurements were collected with a commercial drive-test handset running Accuver XCAL, which exposes the chipset diagnostic interface and produces two synchronised outputs: a tabular radio-measurement export sampled at one hertz, and a decoded control-plane log containing the RRC messages exchanged between the handset and the network. The use of this class of instrumentation for RRC extraction on live networks follows established practice in the measurement literature [5], [4].

The radio export carries, per sample, the serving-cell physical cell identity (PCI), E-UTRA absolute radio frequency channel number (EARFCN), RSRP, RSRQ and signal-to-interference-plus-noise ratio (SINR), together with the corresponding quantities for each detected neighbour cell, and a Global Positioning System (GPS) fix with speed and heading. The signalling log carries the complete `RRCConnectionReconfiguration`, `MeasurementReport` and `RRCConnectionReestablishment` message sequence with millisecond timestamps.

Using the signalling log rather than a vendor handover counter is a deliberate design choice and is the foundation of the ground truth used throughout. A counter reports that the vendor's internal logic considered a handover to have occurred; a decoded `RRCConnectionReconfiguration` carrying `mobilityControlInfo` *is* the handover command, timestamped at the instant it was transmitted. The difference matters for a prediction task, because the label instant defines what "one second ahead" means.

## 3.2 The four campaigns

Four campaigns were conducted on a single commercial LTE operator in September 2026, covering two distinct mobility regimes. Three cover urban corridors in Dhaka: an urban arterial road, an urban loop, and a dense urban area. The fourth covers the Uttara–Gazipur highway, at a mean speed of 49.5 km/h, approximately three times the mean urban speed. Figure 3.1 shows the routes and the geographical distribution of the handover events for the three Dhaka campaigns; the highway corridor runs north-east beyond the mapped extent and is summarised in Table 3.2 rather than mapped.

@@FIG|/home/claude/figs/png_print/fig03_map_routes.png|Figure 3.1 The three Dhaka campaigns on an OpenStreetMap background: 43 drives and the 761 signalling-confirmed handovers recorded on them. Events cluster at particular junctions rather than distributing uniformly along the route. The 15 September highway campaign lies outside this extent. Map data © OpenStreetMap contributors.|4.48

The clustering visible in Figure 3.1 is the first indication that the prediction signal is partly geometric, and it is also the first argument against random-row splitting: if handovers concentrate at identifiable locations, a random split allows a model to learn those locations from the training rows and recognise them in the test rows of the same drive.

The fourth campaign occupies a special position in the experimental design and is treated accordingly throughout. It was driven **after every modelling decision had been frozen**: the feature set, the formulation, the model family, the hyperparameters and the evaluation protocol were all fixed and recorded before the highway data existed. It therefore functions as a genuine out-of-sample test of a new corridor and a new speed regime rather than as an additional fold, and Chapter 5 reports it as such.

## 3.3 Signalling decoding and the configuration timeline

### 3.3.1 The attribution chain

Resolving a measurement report to the event that triggered it requires a chain of three objects defined in TS 36.331 [1]. A `MeasurementReport` carries a `measId`. The `measId` binds, through `measIdToAddModList`, a measurement object — which specifies the carrier frequency being measured — to a report configuration, which specifies the triggering event and its parameters. To determine that a given report is an A3 report, and to determine the offset and time-to-trigger under which it fired, that chain must be followed.

### 3.3.2 Why a flat parse is wrong

The difficulty is that the configuration does not arrive as a single object. It is delivered incrementally across many `RRCConnectionReconfiguration` messages over the lifetime of a connection, with entries added, modified and removed, and the identifiers are scoped to the message that carries them. The same `measId` value can denote different measurement-object-to-report-configuration bindings at different points in the same connection.

A parser that flattens the log — collecting all configuration fragments and resolving every report against the union — produces a result that is not merely imprecise but impossible. Applied to this dataset, such a parse classified 99.4 % of all measurement reports as Event A3, including reports transmitted when no neighbour cell was present in the measurement export at all. Since Event A3 is defined on a neighbour quantity, a report attributed to A3 in the absence of any neighbour cannot be correct, and it was this impossible consequence, rather than a discrepancy in a metric, that exposed the error.

### 3.3.3 The timeline

The correction is to replay the configuration as a timeline. Every configuration fragment is timestamped and applied in order, producing, for any instant *t*, the exact set of `measId` bindings in force at *t*. Each `MeasurementReport` is then resolved against the state of that timeline at its own timestamp. Figure 3.2 illustrates the difference between the two procedures.

@@FIG|/home/claude/figs/png_print/fig07_config_timeline.png|Figure 3.2 Measurement identifiers are scoped to the message that carries them. A flat parse resolves every report against the union of all configuration fragments; the timeline resolves each report against the configuration in force at its own timestamp.|6.3

After the correction, between 43 % and 52 % of measurement reports resolve to Event A3, depending on the campaign, with the remainder distributed across A1, A2 and A5. Every quantity reported in this thesis that depends on report classification — most importantly the report-conversion rate of Section 5.8 — is computed after the correction, and no pre-correction figure is quoted anywhere.

## 3.4 Drive segmentation and quality control

Continuous logging produces a single long record per campaign that includes stationary intervals, signal-acquisition transients and, occasionally, gaps caused by tool restarts. A *drive* is defined as a contiguous segment of recording that satisfies three conditions: the sample grid is unbroken, a valid serving-cell attachment is present, and the segment lasts at least sixty seconds. The sixty-second minimum exists because the feature construction of Section 4.5 uses rolling windows of up to ten seconds and the evaluation requires each drive to contribute a meaningful number of independent samples.

Segmentation and quality control reduce the raw handover count from 957 to 938. The 19 excluded events fall outside a qualifying drive: they occur during acquisition transients, within segments shorter than sixty seconds, or in gaps in the sample grid.

Both counts are reported here because both are correct under their own definitions, and the distinction is stated explicitly wherever a handover count appears in this thesis. **Every model reported in Chapter 5 is trained and scored against the 938 events that fall inside quality-controlled drives.** The 957 figure is used only where the raw event stream is the appropriate object, which in this thesis occurs in exactly one place: the ungrouped variant of the ping-pong definition ladder in Section 5.9.

## 3.5 The deployed configuration

Replaying the configuration timeline across all four campaigns recovers the operator's deployed intra-frequency mobility parameters. Table 3.1 reports them.

@@TCAP|Table 3.1 Deployed Event A3 configuration recovered from RRC signalling, pooled across the four campaigns.
| Parameter | Values observed |
|---|---|
| A3 offset | −15, −10, −6.5, +1, +5 dB |
| Time-to-trigger | 160, 320, 480, 640, 1024 ms |
| Dominant profile | +1 dB offset with 320 ms time-to-trigger |
| Handovers under the dominant profile | 679 of 938 (72.4 %) |

Two features of Table 3.1 are worth comment. First, the configuration is identical across all four campaigns, which is what makes the leave-one-campaign-out experiment of Section 5.6 a test of corridor and speed rather than a test of configuration. Second, the offsets are predominantly **negative**. A negative A3 offset means that the network triggers the measurement report while the neighbour is still *weaker* than the serving cell by the magnitude of the offset — a considerably more aggressive configuration than the +6 to +10 dB offsets that Ghoshal et al. [4] report for the operators they measure, and the opposite in sign to the +3 dB value assumed as a textbook default in several of the prediction studies audited in Section 2.3.

This is a small finding with a disproportionate consequence for the literature. A prediction study that assumes a positive offset is assuming that a handover occurs only after the neighbour has become better; on this network that assumption is false for the majority of handovers, and any feature or baseline derived from it is mis-specified.

Figure 3.3 makes a second point about Table 3.1 that the numbers alone conceal. The profile that produces almost three quarters of the handovers is the one whose entry condition is satisfied least often, and the profile whose condition holds on nine samples in ten produces fewer than one handover in twelve. Whether the gap condition holds is therefore a poor indicator of whether a handover is imminent, which is the measurement behind the mechanism result of Section 5.8.

@@FIG|/home/claude/figs/png_print/fig39_profile_bubble.png|Figure 3.3 Deployed A3 profiles: the share of handovers each produces against the fraction of samples on which its own entry condition already holds. Bubble area is the handover count. The two quantities move in opposite directions.|6.3

## 3.6 The dataset

Table 3.2 summarises the resulting dataset.

@@TCAP|Table 3.2 Summary of the four measurement campaigns after quality control.
| Campaign (2026) | Corridor | Drives | Samples | Handovers | Duration |
|---|---|---|---|---|---|
| 10 September | Urban arterial | 15 | 2,700 | 290 | 46 min |
| 12 September | Urban loop | 8 | 1,440 | 174 | 24 min |
| 13 September | Dense urban | 20 | 3,600 | 297 | 60 min |
| 15 September | Uttara–Gazipur highway | 14 | 2,520 | 177 | 43 min |
| **Pooled** | Two mobility regimes | **57** | **10,260** | **938** | **2.9 h** |

The pooled dataset covers approximately 95 km of driving. A handover occurs on average once every eleven seconds, with a median inter-handover gap of three and a half seconds. Alongside the 938 successful handovers, the signalling log records 341 `RRCConnectionReestablishment` procedures, that is, occasions on which the radio link failed and the connection had to be rebuilt rather than transferred; these are the events the motivation of Section 1.2 refers to. Figure 3.4 shows the distribution of samples and events across the campaigns.

@@FIG|/home/claude/figs/png_print/fig05_dataset.png|Figure 3.4 Composition of the pooled dataset. The four campaigns differ in duration and in event density; the highway campaign contributes the fewest handovers per minute and the highest mean speed.|6.3

Three properties of this dataset bound what can be claimed from it, and they are stated here rather than in the conclusion.

The dataset is **small by machine-learning standards and large by drive-test standards**. Fifty-seven drives is a sufficient number of independent groups to support a grouped evaluation with bootstrap intervals, which is what the protocol requires; it is not a sufficient number to train a sequence model from scratch, and Section 5.2 shows exactly that outcome.

The sampling rate **caps event resolution**. At one sample per second, a handover whose preceding second contains no recorded sample cannot be predicted at all. The fraction of events that are in principle resolvable on this grid is 90.5 %, and every event-level detection figure in Chapter 5 is reported against that ceiling rather than against 100 %.

The dataset covers **one operator and four days**. The configuration in Table 3.1 is one operator's configuration; the cross-regime transfer reported in Section 5.6 therefore rests on a single configuration pair, and the external validation of Section 5.7 exists precisely because that limitation was recognised during the design rather than after it.
@@CHAPTER|4|PREDICTIVE FORMULATION AND SYSTEM DESIGN

This chapter develops the predictive system. Section 4.1 formalises the task and fixes notation. Section 4.2 presents the obvious formulation, the independent multi-horizon classifier, and shows why it is structurally defective. Section 4.3 presents the discrete-time survival formulation adopted in its place, and Section 4.4 gives its likelihood under censoring. Section 4.5 explains why class reweighting, the standard reflex on a rare-event task, is inadmissible under this formulation. Sections 4.6 and 4.7 describe the features and the models. Section 4.8 describes calibration, Section 4.9 the evaluation protocol, Section 4.10 the risk-control procedure, and Section 4.11 the point-process analysis used to characterise handover clustering.

Each modelling subsection is presented in the same order: the problem that motivates the component, the design of the component, and the technical advantage it confers over the alternative it replaces.

## 4.1 Problem formalisation

Let a drive *d* consist of samples indexed by *t* on a uniform one-second grid. At each sample the handset observes a feature vector *x*<sub>t</sub> constructed from measurements available at or before *t*. Let *T*<sub>t</sub> denote the time remaining from *t* until the next handover command on the same drive.

The task is to estimate, for a set of horizons *h*<sub>1</sub> &lt; *h*<sub>2</sub> &lt; … &lt; *h*<sub>K</sub>, the cumulative incidence

@@EQ|F_k(x_t) = P( T_t ≤ h_k │ x_t ),   k = 1 … K|(4.1)

with *K* = 5 and horizons of 0.5, 1, 2, 3 and 5 seconds. Samples for which the drive ends before the next handover occurs are **right-censored**: the event is known not to have occurred within the observed window, but its eventual time is unknown. Right censoring is not a nuisance to be discarded here; the last samples of every drive are censored, and discarding them would both waste data and bias the observed event-time distribution towards short intervals.

Table 4.1 reports the resulting positive-class prevalence at each horizon. These are the floors against which every result in Chapter 5 is read.

@@TCAP|Table 4.1 Positive-class prevalence by horizon, and the accuracy obtained by a constant negative prediction.
| Horizon | Prevalence | Accuracy of a constant "no handover" |
|---|---|---|
| 0.5 s | 3.7 % | 96.3 % |
| 1 s | 6.7 % | 93.3 % |
| 2 s | 12.5 % | 87.5 % |
| 3 s | 17.5 % | 82.5 % |
| 5 s | 25.9 % | 74.1 % |

Table 4.1 is the reason accuracy is not reported anywhere in this thesis. At the one-second horizon a model that never predicts a handover already scores 93.3 %, which exceeds several of the headline accuracies reported in the audited literature of Section 2.3.

## 4.2 The multi-horizon binary formulation and its defect

**Motivation.** The most direct approach to Equation (4.1) is to define, for each horizon, a binary label *y*<sub>t,k</sub> = 1{ *T*<sub>t</sub> ≤ *h*<sub>k</sub> } and fit *K* independent classifiers. This is the formulation implied by every model in the audit of Section 2.3 that predicts at more than one horizon, and it requires no special machinery.

**The defect.** The *K* classifiers are fitted independently and are therefore free to produce estimates that violate the ordering implied by their own definitions. Because the event { *T*<sub>t</sub> ≤ *h*<sub>1</sub> } is contained in { *T*<sub>t</sub> ≤ *h*<sub>2</sub> } whenever *h*<sub>1</sub> &lt; *h*<sub>2</sub>, the probabilities must satisfy *F*<sub>1</sub> ≤ *F*<sub>2</sub> ≤ … ≤ *F*<sub>K</sub> at every sample. Independent fits do not enforce this, and Section 5.4 measures how often they violate it: on 43.6 % of samples.

A violation is not a small numerical irregularity. It is an assertion that a handover is more likely within one second than within three, which is impossible, and it destroys the interpretation of the output as a probability. An operator presented with such a pair of numbers cannot act on either.

**Why post-hoc repair is unsatisfactory.** The defect can be repaired after the fact by projecting the *K* outputs onto the monotone cone, or by calibrating each horizon separately with isotonic regression. Both repairs were implemented and both are reported in Section 5.4 as controls. Neither is adopted, for two reasons: each consumes a held-out split that the dataset can ill afford, and per-horizon isotonic calibration measurably *worsens* coherence rather than improving it.

## 4.3 The discrete-time survival formulation

**Motivation.** The ordering constraint is a consequence of the definition of cumulative incidence, so the natural remedy is to estimate a quantity from which ordering follows automatically, rather than to estimate the ordered quantities directly and repair them.

**Design.** Partition the time axis into *K* bins whose upper edges are exactly the horizons of interest:

@@EQ|B_1 = (0, h_1],  B_2 = (h_1, h_2],  …,  B_K = (h_{K−1}, h_K]|

and define the **discrete-time hazard** as the probability that the event falls in bin *k* given that it has not occurred by the start of that bin:

@@EQ|λ_k(x) = P( T ∈ B_k │ T > h_{k−1}, x )|(4.2)

The survival function is the product of per-bin survivals,

@@EQ|S_k(x) = Π_{j=1..k} ( 1 − λ_j(x) ) = P( T > h_k │ x )|(4.3)

and the cumulative incidence required by Equation (4.1) is its complement, which is the **product-limit identity**:

@@EQ|F_k(x) = P( T ≤ h_k │ x ) = 1 − Π_{j=1..k} ( 1 − λ_j(x) )|(4.4)

**Technical advantage.** Monotonicity is now a theorem rather than a hope. Since λ<sub>j</sub> ∈ [0,1], every factor (1 − λ<sub>j</sub>) lies in [0,1], so

@@EQ|S_{k+1} = S_k · ( 1 − λ_{k+1} ) ≤ S_k   ⟹   F_{k+1} ≥ F_k|(4.5)

The argument uses no property of the learner beyond the range of its output. Any model that emits a value in [0,1] per bin produces a coherent set of horizon probabilities under Equation (4.4). This is why the coherence result reported in Section 5.4 is learner-independent while the calibration result is not, and it is the single most important structural property of the system developed here.

Figure 4.1 illustrates the two formulations side by side.

@@FIG|/home/claude/figs/png_print/fig08_hazard_concept.png|Figure 4.1 Independent per-horizon classifiers against the hazard formulation. Five independent fits violate horizon ordering on 43.6 % of samples; the product of hazards cannot violate it at all.|6.3

## 4.4 The likelihood under censoring

Let *k*<sub>t</sub> be the bin in which the event occurs for sample *t*, and let *c*<sub>t</sub> be the last bin fully survived before censoring. Define the **at-risk set** *R*<sub>t</sub> = {1 … min(*k*<sub>t</sub>, *c*<sub>t</sub>)} — the bins the sample actually entered — and the per-bin indicator *z*<sub>t,k</sub> = 1{ *k* = *k*<sub>t</sub> }. The discrete-time survival log-likelihood then collapses into a single expression covering both the censored and uncensored cases:

@@EQ|ℓ = Σ_t Σ_{k ∈ R_t} [ z_{t,k} log λ_k(x_t) + (1 − z_{t,k}) log(1 − λ_k(x_t)) ]|(4.6)

Equation (4.6) is exactly a binary cross-entropy over the expanded set of (sample × at-risk bin) pairs. The practical consequence is that fitting a discrete-time survival model requires no specialised software: the data are expanded from wide to long format, the bin index *k* is appended as a feature so that the model can learn the shape of the baseline hazard, and a single binary classifier is fitted. A censored sample contributes a (1 − λ<sub>k</sub>) term for every bin it survived rather than being discarded.

On this dataset the expansion takes 10,260 rows to approximately 34,000 (sample, bin) pairs. The measured per-bin hazard rates, pooled over folds, are reported in Table 4.2.

@@TCAP|Table 4.2 Measured discrete-time hazard by bin, pooled over evaluation folds.
| Bin | Interval | Mean hazard |
|---|---|---|
| 1 | 0 – 0.5 s | 0.053 |
| 2 | 0.5 – 1 s | 0.042 |
| 3 | 1 – 2 s | 0.086 |
| 4 | 2 – 3 s | 0.072 |
| 5 | 3 – 5 s | 0.123 |

## 4.5 Why class reweighting is inadmissible here

The standard response to a rare-event task is to reweight the positive class, for example through the `scale_pos_weight` parameter of a gradient-boosting implementation. That response must not be used in the hazard arm, for a reason specific to Equation (4.4).

Reweighting the positive class by a factor *w* transforms the fitted probability monotonically,

@@EQ|λ̃ = w λ / ( w λ + (1 − λ) )|(4.7)

Ranking metrics are invariant under this transformation, since AUPRC and AUROC depend only on the order of scores. The probability *scale*, however, is destroyed — and Equation (4.4) multiplies *K* of those probabilities together. A per-bin multiplicative calibration error ε therefore compounds across the horizon axis as

@@EQ|F̂_k / F_k ~ ( 1 + ε )^k|(4.8)

so the distortion grows with the horizon, precisely where calibration is already weakest. Both the hazard arm and the independent-classifier control arm are consequently fitted unweighted, which has the additional benefit of keeping the comparison between them fair.

## 4.6 Feature construction

**Motivation.** The system must predict from quantities a handset actually possesses at the instant of prediction. Two constraints follow: no feature may use information from the future, and no feature may use information from a different drive.

**Design.** One hundred and fifty-two candidate columns are constructed and 107 survive a degenerate-feature filter that removes columns with zero variance or more than 50 % missing values on the training rows. They fall into four blocks, summarised in Table 4.3.

@@TCAP|Table 4.3 Feature blocks retained after the degenerate-feature filter.
| Block | Count | Content |
|---|---|---|
| Radio | 83 | Serving and neighbour RSRP, RSRQ and SINR; rolling mean, standard deviation, range and first difference over 3, 5 and 10 s windows; serving-to-neighbour gaps |
| Mobility | 17 | GPS speed, heading change, acceleration and their rolling statistics |
| Signalling | 13 | Recent measurement-report counts by event type, time since last report, configuration identifiers in force |
| History | 7 | Serving dwell time, time since previous handover, recent handover count |
| **Total** | **107** | From 152 constructed |

Every rolling window is strictly backward-looking and closes at the prediction instant *t*, and window computation is performed per drive so that no window spans a drive boundary. Features are standardised using statistics computed on the training partition only; a scaler fitted on the pooled dataset is itself a leak, and although a small one, it is among the first things a careful reviewer checks.

**The signalling block requires an explicit leakage guard.** A measurement report is a causal antecedent of the handover it triggers, and it is also, in the log, nearly simultaneous with it. A naive "time since last A3 report" feature therefore carries information about the very handover being predicted. The guard applied here excludes any report falling inside the prediction window itself, so that a signalling feature evaluated at *t* for horizon *h* may only reference reports transmitted at or before *t*. Section 5.11 reports what happens when the guard is removed.

## 4.7 Models compared

Seven learners are compared under identical folds, identical seeds and the identical hazard formulation. The comparison is designed so that the only thing varying between arms is the learner.

**The Event A3 rule.** The deployed rule is scored as if it were a predictor, using the recovered configuration of Table 3.1 to determine when the entry condition of Equation (2.1) holds. This is the most important baseline in the thesis because it is what is presently running in the network.

**Logistic regression.** A regularised linear model over the 107 features, included as the simplest learner that can use the full feature set.

**Gradient-boosted trees.** LightGBM [30] is the primary model. It is chosen for a tabular task with heterogeneous, partly missing features of mixed scale, where axis-aligned splits and native missing-value handling are well matched to the data.

**Multi-layer perceptron.** A feed-forward network over the same tabular features, included to separate the contribution of non-linearity from that of temporal memory.

**Sequence models.** A temporal convolutional network, a Transformer encoder and a gated recurrent unit, each consuming a window of raw per-second measurements rather than the engineered summary features. These arms test whether a model that learns its own temporal representation outperforms one given hand-constructed rolling statistics.

Every neural arm receives an equal hyperparameter budget of twenty trials; the tree and linear arms receive the same budget. Section 5.2 reports the outcome, which is that no arm with temporal memory overtakes the tabular arms on a dataset of this size.

## 4.8 Calibration

Ranking quality is insufficient for the task stated in Section 1.3, which requires the asserted probability to correspond to an empirical frequency. Three calibration treatments are evaluated.

**Temperature scaling** [31] fits a single scalar on a held-out partition, dividing the logits before the sigmoid. It is the least expressive treatment and cannot alter the ranking.

**Isotonic regression** [32] fits a non-decreasing step function per horizon. It is more expressive and can correct a wider class of miscalibration, but it consumes a held-out split and, applied per horizon, is free to reorder the horizons relative to one another.

**The monotone projection** repairs an incoherent set of horizon outputs by projecting them onto the monotone cone. It is implemented for the control arm only, since the hazard formulation makes it unnecessary.

Calibration quality is reported as the expected calibration error, computed as the weighted mean absolute difference between confidence and empirical frequency across equal-mass bins, with the Brier score reported alongside it.

## 4.9 Evaluation protocol

**Motivation.** The protocol is the component most likely to invalidate a result on data of this kind, because adjacent one-second samples within a drive are near-duplicates of one another. Section 5.3 measures the consequence.

**Design.** The evaluation protocol has five elements.

*Grouping.* The unit of splitting is the whole drive. A drive appears either in training or in test on a given fold, never in both. Figure 4.2 illustrates the rotation.

@@FIG|/home/claude/figs/png/m03_protocol.png|Figure 4.2 The grouped evaluation protocol. Splits are taken at the level of the whole drive under a four-fold rotation, repeated over five seeds, giving twenty paired observations per comparison.|6.3

*Rotation.* A four-fold rotation over the 57 drives ensures that every drive is tested exactly once per seed, with approximately 14 drives held out against 43 in training on each fold.

*Repetition.* The rotation is repeated with five random seeds, producing twenty paired observations per comparison. The reason is not cosmetic. With four folds alone, a paired test over four observations cannot attain a *p*-value below 0.125 regardless of the size of the effect, so the test would report its own resolution limit rather than a property of the data.

*Interval estimation.* Confidence intervals are obtained by a cluster bootstrap that resamples whole drives with replacement, because samples within a drive are not independent.

*Fold hygiene.* The feature scaler, the decision threshold and the probability calibrator are fitted inside the training partition of each fold only.

**Metrics.** Four families are reported. Ranking quality is reported as AUPRC, always accompanied by the prevalence floor and the lift over it, together with AUROC. Calibration is reported as expected calibration error and Brier score. Coherence is reported as the fraction of samples on which the horizon ordering is violated. Event-level cost is reported as the fraction of handover events detected, the number of false alarms per hour and per kilometre, and the distribution of lead times. Reporting all four families is deliberate: Wagner et al. [28] show that no single aggregate metric for event detection satisfies all desirable properties, so the event-level figures are reported alongside the row-level ones rather than instead of them.

## 4.10 Distribution-free risk control

**Motivation.** A probability is not yet an operating point. Converting the model output into a warning requires a threshold, and an operator is entitled to know what that threshold guarantees on drives it has not seen.

**Design.** Let λ ∈ Λ index a family of alarm thresholds ordered by decreasing strictness and let *R*(λ) be a bounded, non-increasing risk. Conformal risk control [20] selects

@@EQ|λ̂ = inf { λ : ( n·R̂(λ) + B ) / ( n + 1 ) ≤ α }|(4.9)

where *R̂*(λ) is the empirical risk over *n* exchangeable calibration units and *B* bounds the loss, here *B* = 1. The guarantee is that E[*R*<sub>n+1</sub>(λ̂)] ≤ α for a fresh exchangeable unit, distribution-free, with no assumption on the model or on the data-generating process beyond exchangeability.

**The exchangeable unit is the drive.** This is the choice that makes the guarantee meaningful, and it is the contribution of this section. Samples within a drive are not exchangeable with samples from a different drive: they share a cell sequence, a traffic condition and a trajectory. The risk is therefore defined as the **per-drive miss rate**

@@EQ|R_d(λ) = |{ t ∈ d : y_t = 1 ∧ p̂_t < λ }| / |{ t ∈ d : y_t = 1 }||(4.10)

and *R̂*(λ) averages over calibration *drives* rather than over samples.

**Technical advantage, and a design rule that follows from it.** Equation (4.9) can be satisfied only if its left-hand side can reach α at all. At the most permissive threshold *R̂* = 0, so the smallest attainable value is *B*/(*n*+1), giving the feasibility floor

@@EQ|α ≥ 1/(n+1)   ⟺   n ≥ 1/α − 1|(4.11)

Equation (4.11) is a **campaign-design rule**: a study that wishes to promise a 5 % miss rate requires at least 19 calibration drives, and one promising 2 % requires 49, independently of how good the model is. Pooling calibration drives across the four campaigns here gives *n* = 28 and therefore α ≥ 0.034. This rule appears nowhere in the handover literature, and it determines how much driving a study must do before its guarantee is even expressible.

## 4.11 Point-process analysis of handover arrivals

**Motivation.** The ping-pong behaviour of Section 5.9 suggests that handovers do not arrive independently. Quantifying that clustering requires a model of the arrival process itself rather than of the per-sample probability.

**Design.** The handover arrival stream on each drive is modelled as a self-exciting Hawkes process [21], [22] with conditional intensity

@@EQ|μ(t) = μ_0 + Σ_{t_i < t} α · exp( −β ( t − t_i ) )|(4.12)

in which each arrival raises the intensity of subsequent arrivals by α and the excitation decays at rate β. The **branching ratio** α/β is the expected number of direct offspring per event and summarises the strength of the clustering.

**Validation.** A fit alone is not evidence of self-excitation. Following the networking precedent of Price-Williams and Heard [24], the fit is validated by the residual analysis of Ogata [23]: the time axis is rescaled by the fitted compensator, and the transformed inter-arrival times are tested against a unit-rate exponential distribution by a Kolmogorov–Smirnov test on held-out drives. Section 5.10 reports both the branching ratio and the outcome of that test, including the respect in which the test rejects the fitted kernel.
@@CHAPTER|5|RESULTS AND DISCUSSION

This chapter reports what the system of Chapter 4 achieves on the data of Chapter 3, and discusses each result against the objectives stated in Section 1.4. Section 5.1 reports the primary prediction result. Sections 5.2 to 5.5 report the four results that concern the method rather than the score: model ranking under an equal budget, the measured cost of a careless evaluation protocol, coherence and calibration, and the risk-control frontier. Sections 5.6 and 5.7 report generalisation within and beyond the campaign. Sections 5.8 to 5.10 report the mechanism and the two network findings. Section 5.11 reports the negative results, Section 5.12 discusses the outcome against the objectives, and Section 5.13 states the threats to validity.

All figures in this chapter are computed out of fold under the grouped-drive rotation of Section 4.9 unless stated otherwise.

## 5.1 The primary prediction result

Table 5.1 reports the performance of the primary model, LightGBM under the hazard formulation, at all five horizons.

@@TCAP|Table 5.1 Out-of-fold prediction performance of LightGBM under the hazard formulation, over 57 drives. Confidence intervals are cluster-bootstrapped over drives.
| Horizon | Prevalence | AUPRC [95 % CI] | Lift | AUROC | ECE |
|---|---|---|---|---|---|
| 0.5 s | 0.037 | 0.416 [0.350, 0.490] | 11.3× | 0.916 | 0.023 |
| **1 s** | **0.067** | **0.784 [0.740, 0.826]** | **11.7×** | **0.933** | **0.024** |
| 2 s | 0.125 | 0.627 [0.594, 0.657] | 5.0× | 0.854 | 0.061 |
| 3 s | 0.175 | 0.598 [0.561, 0.636] | 3.4× | 0.816 | 0.091 |
| 5 s | 0.259 | 0.606 [0.564, 0.649] | 2.3× | 0.783 | 0.141 |

One second before a handover command, the model reaches AUROC 0.933 and AUPRC 0.784 against a prevalence floor of 6.7 %, a lift of 11.7×, at an expected calibration error of 0.024. This is the headline result of the thesis and it answers objective O1.

Two features of Table 5.1 require comment because they are easy to misread. First, the AUPRC value at two seconds (0.627) is *lower* than at one second (0.784) while the prevalence is higher; the correct comparison is the lift column, where 11.7× at one second falls to 5.0× at two. Reading AUPRC across rows without the floor is precisely the error that Section 2.3 documents in the comparator literature. Second, the calibration error rises monotonically with the horizon, from 0.023 at half a second to 0.141 at five. The model is well calibrated where the task is sharp and poorly calibrated where it is diffuse, and this is reported rather than concealed because it bounds the horizon at which the output can be used as a probability rather than as a ranking.

The comparison that matters operationally is against the rule presently deployed. Scored on the same data as a predictor, Event A3 reaches AUROC 0.653 and detects 5.5 % of handovers one second ahead.

At the event level rather than the sample level, 44.7 % of handover events are detected one second in advance and 65.1 % at five seconds, against a ceiling of 90.5 % imposed by the one-hertz sampling grid described in Section 3.6. The ceiling is a property of the instrument; the gap between 44.7 % and 90.5 % is the property of the model.

Two views of that result are worth separating, because they answer different questions. Figure 5.1 reports where the model sits on the receiver-operating and precision-recall planes at each horizon, restricted to the low-false-positive region an operator would actually use. Figure 5.2 leaves the sample level entirely and plots the quantity an operator pays: the fraction of handover *events* caught against the number of false-alarm episodes raised per hour of driving.

@@FIG|/home/claude/figs/png_print/fig35_operating_points.png|Figure 5.1 Certified operating points at each horizon. Left: recall at false-positive rates of 1, 5 and 10 %. Right: precision at recall levels of 0.5 and 0.8, against the prevalence floor of each horizon. Points are plotted rather than interpolated, because the frozen result tables carry operating points and not full curves.|6.3

@@FIG|/home/claude/figs/png_print/fig32_operating_plane.png|Figure 5.2 The event-level cost plane. Each track is one model walked across the five look-ahead times, with marker size growing with the horizon. The deployed A3 rule raises false alarms at a comparable rate while detecting a small fraction of the events.|6.3

## 5.2 Model comparison under an equal budget

Figure 5.3 and Table 5.2 report all seven learners under identical folds, seeds, formulation and hyperparameter budget.

@@FIG|/home/claude/figs/png_print/fig10_model_comparison.png|Figure 5.3 AUPRC by horizon for seven learners against the prevalence floor. LightGBM leads at every horizon and logistic regression is second; no model with temporal memory overtakes either.|6.3

@@TCAP|Table 5.2 Model comparison at the one-second horizon under an equal twenty-trial tuning budget.
| Model | AUPRC | Lift | AUROC |
|---|---|---|---|
| **LightGBM** | **0.784** | **11.7×** | **0.933** |
| Logistic regression | 0.712 | 10.6× | 0.912 |
| Multi-layer perceptron | 0.681 | 10.2× | 0.901 |
| Temporal convolutional network | 0.646 | 9.6× | 0.887 |
| Transformer | 0.633 | 9.4× | 0.881 |
| Gated recurrent unit | 0.617 | 9.2× | 0.874 |
| Event A3 rule (deployed) | 0.113 | 1.7× | 0.653 |

The ordering is itself a finding. LightGBM leads at every horizon and logistic regression is second, ahead of all four architectures with temporal memory. This is not an argument that sequence models are unsuitable for the task in general; it is a statement about a dataset of 57 drives. With 10,260 samples and 938 events, there is insufficient data for a sequence model to learn a temporal representation that improves on the rolling statistics constructed by hand in Section 4.6, and each of the four was given the same twenty-trial budget in which to try.

The deployed A3 rule sits at the bottom of the table by a wide margin, which is the expected result and not a criticism of the rule: Event A3 is a decision procedure that the standard designed to be reliable rather than early, and Section 5.8 shows the mechanistic reason why the quantity it thresholds on carries little predictive signal.

Table 5.2 reports a mean, and a mean over eight grouped-drive folds is a fragile object. Figure 5.4 therefore draws every fold. The spread inside a single arm is wider than the gap between the two LightGBM arms, which is why the paired test of Section 5.4, rather than the ordering of the means, is what settles the comparison between formulations.

@@FIG|/home/claude/figs/png_print/fig29_fold_dispersion.png|Figure 5.4 Per-fold AUPRC at the one-second horizon, with all eight grouped-drive folds drawn for each arm. Boxes show the median and inter-quartile range; the whiskers extend to the furthest fold within 1.5 inter-quartile ranges.|6.3

## 5.3 The evaluation protocol is worth more than the model

The result in this section concerns the protocol rather than the predictor, and it is the one with the widest implication for the comparator literature.

The experiment is a controlled substitution. Everything is held fixed — the data, the features, the formulation, the hyperparameters, the seeds — and only the splitting rule is changed, from grouping by whole drive to splitting rows at random. Table 5.3 reports the resulting inflation.

@@TCAP|Table 5.3 Inflation of the one-second AUPRC when grouped-drive splitting is replaced by random-row splitting, with all else held fixed.
| Model | Inflation |
|---|---|
| Gated recurrent unit | **+74 %** |
| Transformer | +44 % |
| Temporal convolutional network | +27 % |
| LightGBM | +20 % |
| Multi-layer perceptron | +10 % |
| Logistic regression | **+4 %** |
| Event A3 rule | −2 % |

@@FIG|/home/claude/figs/png_print/fig12_leakage.png|Figure 5.5 Inflation from random-row splitting, by architecture. The inflation scales with the amount of temporal memory an architecture carries, so the leaderboard reorders rather than merely rising.|6.3

Figure 5.5 plots the same seven inflations in rank order. The mechanism is straightforward once stated. Two samples one second apart on the same drive are near-duplicates: the serving cell is the same, the neighbour set is the same, and the rolling features overlap in nine of their ten seconds. A random split therefore places almost the same row on both sides of it, and the more temporal memory an architecture carries, the more it profits from encountering its own near-neighbour during training. The parameter-free A3 rule has nothing to over-fit with, and its score moves slightly in the opposite direction.

The consequence is sharper than the familiar statement that a leaky protocol raises scores. Because the inflation is **architecture-dependent**, it reorders the ranking. Under random-row splitting on this data the gated recurrent unit rises from sixth place to a position it does not hold under grouped splitting, which is to say that a study using the standard protocol of the comparator literature could conclude that a sequence model wins on data where it does not. This answers objective O2, and it is why the protocol is presented in this thesis as a contribution rather than as housekeeping.

## 5.4 Coherence and calibration

Table 5.4 reports the coherence and calibration behaviour of the hazard formulation against the independent-classifier control arm and against the two post-hoc repairs described in Section 4.8.

@@TCAP|Table 5.4 Horizon coherence and calibration for the hazard formulation and its controls.
| Configuration | Horizon violations | Largest violation | Cost |
|---|---|---|---|
| Five independent classifiers | 43.6 % | — | — |
| The same, with per-horizon isotonic calibration | 48.7 % | 0.495 → 0.596 | One held-out split, 2–5 AUPRC points |
| **Hazard formulation** | **0 %** | — | None |

The hazard formulation produces no horizon-ordering violations, which follows from Equation (4.5) and requires no verification beyond confirming that the implementation matches the equation. The independent-classifier arm violates ordering on 43.6 % of samples.

The isotonic control deserves its own sentence because it is the obvious objection to the whole formulation. If per-horizon calibration can repair the outputs of independent classifiers, the hazard formulation buys nothing that a post-processing step could not. The measurement shows the opposite: applying isotonic regression per horizon makes coherence *worse*, from 43.6 % to 48.7 % of samples, and enlarges the largest single violation from 0.495 to 0.596. The reason is that the *K* isotonic maps are fitted independently and are therefore free to reorder the horizons relative to one another. The control can win on calibration error considered alone — it is a more expressive calibrator than temperature scaling — but it cannot win on calibration and coherence together, and it costs a held-out split and two to five AUPRC points to try.

Figure 5.8 places all four configurations on the same axes: the left panel tracks calibration error across the horizon, the right panel gives the violation rate of each. Against an uncalibrated baseline, the calibration of the hazard formulation is superior at every horizon, with *p* < 0.0001 over the twenty paired folds of Section 4.9.

Because the folds are paired, the appropriate picture is a paired one. Figure 5.6 draws one line per fold between the two formulations: the calibration error falls on every fold without exception, which is what makes the signed-rank test meaningful on only eight observations. Figure 5.7 then follows the same comparison along the horizon axis, and adds the result that bounds the usable range of the output: both formulations degrade steeply beyond two seconds, so the five-second probability should be read as a ranking rather than as a probability.

@@FIG|/home/claude/figs/png_print/fig30_paired_ece.png|Figure 5.6 Paired calibration error at the one-second horizon, one line per grouped-drive fold. Every fold improves under the hazard formulation; the heavy bars mark the arm means.|5.95

@@FIG|/home/claude/figs/png_print/fig36_ece_ribbon.png|Figure 5.7 Calibration error against the look-ahead horizon. The line is the fold median and the band is the inter-quartile range across folds. The separation is present at every horizon and both formulations degrade sharply beyond two seconds.|6.3

@@FIG|/home/claude/figs/png_print/fig13_hazard_results.png|Figure 5.8 Coherence and calibration of the hazard formulation against the independent-classifier control. The violation rate falls from 43.6 % to zero by construction, and calibration improves at every horizon.|6.3

The operational meaning of an expected calibration error of 0.024 at the one-second horizon is worth stating plainly, because a calibration figure is easy to report and easy to ignore. It means that among the samples on which the system asserts a probability near 0.8, a handover follows within one second on approximately 80 % of occasions. That is what permits the output to enter a decision rule rather than merely to sort samples, and it is what none of the 22 audited models in Section 2.3 reports. Together with Section 5.5 this answers objective O3.

## 5.5 The risk-control frontier and its price

Table 5.5 reports the conformal risk-control frontier obtained by the procedure of Section 4.10 on 28 held-out calibration drives.

@@TCAP|Table 5.5 Conformal risk-control frontier. The certified target is the bound on the expected per-drive miss rate; the alarm rate and realised miss rate are measured on held-out drives.
| Certified target α | Samples alarmed | Realised miss rate | Bound held on |
|---|---|---|---|
| 0.20 | 23 % | 12.6 % | 82 % of drives |
| 0.05 | 61 % | — | — |
| Feasibility floor | α ≥ 0.034 with n = 28 | — | — |

Three observations follow.

First, the guarantee is real and it is cheap at a loose target. At α = 0.20 the certified threshold alarms on 23 % of samples and realises a miss rate of 12.6 %, comfortably inside the promise, and the per-drive bound held on 82 % of held-out drives.

Second, the guarantee becomes expensive quickly. At α = 0.05 the alarm rate rises to 61 % of samples, which is not an operating point any operator would deploy. Reporting the whole frontier rather than a single flattering point is a deliberate choice, and it is the honest form of a claim about guaranteed performance: the guarantee is not free, and its price is the alarm rate.

Third, and most consequentially, the number of calibration drives binds independently of model quality. With *n* = 28, Equation (4.11) gives a feasibility floor of α ≥ 0.034: no target tighter than approximately 3.4 % can be expressed at all, however good the predictor becomes. A study that wishes to promise 2 % needs at least 49 calibration drives. This converts a modelling question into a campaign-design question, and it is the practical form of the contribution claimed in Section 1.6.

Figure 5.9 puts the three observations on one pair of axes in the form conformal work conventionally uses: the realised risk against the nominal level, with the guarantee boundary drawn as the diagonal. Every operating point lies on or below the diagonal, which is the claim the procedure makes; the second axis carries what that compliance costs, and the shaded strip on the left is the region no choice of threshold can reach with twenty-eight calibration drives.

@@FIG|/home/claude/figs/png_print/fig31_conformal_coverage.png|Figure 5.9 Realised per-drive miss rate against the certified target, with the alarm rate on the right-hand axis. Points on or below the diagonal satisfy the guarantee. The shaded strip marks the targets made unreachable by the number of calibration drives.|6.3

## 5.6 Generalisation across corridors and speed regimes

Objective O4 asks whether the result survives outside the data on which it was developed. Two experiments address it, at increasing distance from the training distribution.

The first holds out each campaign in its entirety, training on the remaining three. Table 5.6 reports the outcome.

@@TCAP|Table 5.6 Leave-one-campaign-out performance at the one-second horizon. Each row is trained on the other three campaigns and tested on the campaign named.
| Campaign held out | AUPRC | Lift | AUROC | ECE |
|---|---|---|---|---|
| Urban arterial | 0.826 | 9.9× | 0.949 | 0.027 |
| Urban loop | 0.718 | 9.4× | 0.909 | 0.040 |
| Dense urban | 0.832 | 13.2× | 0.943 | 0.019 |
| **Uttara–Gazipur highway** | **0.761** | **14.9×** | **0.927** | **0.018** |

AUROC remains between 0.909 and 0.949 across all four, so no single campaign is carrying the pooled result; Figure 5.10 sets each metric against its pooled value. The weakest row is the urban loop, and the reason is size rather than difficulty: at eight drives, 174 handovers and 24 minutes it is the smallest campaign, so it both contributes least to the training partitions of the other rows and produces the least certain test estimate of its own.

The highway row is the one that bears on the objective. That campaign was driven after every modelling decision had been frozen, so nothing in the model was tuned on it, and it differs from the training data in both corridor and speed regime. It nonetheless reaches AUROC 0.927, with the **highest lift and the lowest calibration error of the four**. Adding it to the pooled dataset moved the headline AUROC by nothing: 0.933 before and 0.933 after. A fourth campaign that changes the headline result by zero is the strongest available evidence that the first three were not being over-fitted.

@@FIG|/home/claude/figs/png_print/fig38_capture_smallmultiples.png|Figure 5.10 Leave-one-campaign-out on four metrics. Each panel holds one campaign out entirely and trains on the other three; the dashed line is the pooled result on the same metric. The highway, in maroon, is the campaign frozen out of every modelling decision.|6.3

## 5.7 External validation on an independently collected dataset

The leave-one-campaign-out experiment still shares an operator, an instrument and an analyst. The second generalisation experiment removes all three by evaluating on a publicly released LTE drive-test dataset collected by a different group on a different network [33].

@@TCAP|Table 5.7 External validation at the one-second horizon on an independently collected public drive-test dataset.
| Model | AUROC at 1 s |
|---|---|
| **This work, transferred without refitting** | **0.752** |
| A model trained directly on that dataset | 0.745 |

Table 5.7 reports the comparison and Figure 5.11 places it beside the pairwise transfers among the Dhaka campaigns. The transferred model reaches AUROC 0.752 on data it has never seen, against 0.745 for a model trained on that dataset itself. The two figures are close, and the appropriate reading is not that the transferred model is superior — the difference is within the range that resampling produces — but that **what transfers is the formulation rather than the fit**. A fitted model belongs to the network it was fitted on; a formulation and a feature construction do not, and it is the latter that this thesis offers.

@@FIG|/home/claude/figs/png_print/fig15_transfer.png|Figure 5.11 Pairwise transfer between the three Dhaka campaigns and out to the curated public dataset: AUROC at one second, whole drives held out. Between-campaign transfer shares no drives, routes or cells; external transfer shares no network and no operator. The highway campaign is not in this matrix; it is reported in Table 5.6 and Figure 5.10.|6.3

## 5.8 Mechanism: the network triggers on its weakest signal

Objective O5 asks for the mechanism rather than the score, and the answer is uncomfortable for the deployed rule.

Table 5.8 reports the single-feature discriminative power of the three most informative inputs, each evaluated alone at the one-second horizon.

@@TCAP|Table 5.8 Single-feature AUROC at the one-second horizon. Each feature is evaluated on its own.
| Feature | AUROC alone |
|---|---|
| Serving dwell time | **0.874** |
| Serving SINR | 0.830 |
| A3 serving-to-neighbour gap | **0.566** |

@@FIG|/home/claude/figs/png_print/fig17_mechanism.png|Figure 5.12 Single-feature discriminative power. Serving dwell time, which the deployed rule does not use, is the strongest single predictor; the serving-to-neighbour gap, which the rule thresholds on, is among the weakest.|6.3

Figure 5.12 ranks the seven strongest single features. The quantity on which the network makes its decision is close to the least informative input available. Serving dwell time — how long the handset has been attached to its current cell — reaches AUROC 0.874 entirely on its own, while the serving-to-neighbour gap reaches 0.566, barely above chance for a single feature.

The signalling explains why. The A3 gap condition is satisfied on 27.1 % of all samples, and three in five of the measurement reports that follow are declined by the network. The gap is therefore a *necessary* condition that is very far from sufficient: satisfying it changes the probability of a handover far less than the literature's use of it as a feature would suggest.

The interpretation is a statement about the rule rather than about the model. The gap indicates that a handover is **permitted**; dwell time indicates that one is **becoming due**. A trigger defined on permission rather than on tendency will always fire late, which is the structural claim made in Section 1.1, now supported by measurement.

Figure 5.13 shows the same result as a dose-response relation rather than as a summary statistic, which is the stronger form of the evidence. Sweeping the serving-to-neighbour gap across thirty decibels moves the probability of a handover within one second only between roughly 0.08 and 0.22, and the relation is not even monotone: the most negative gap bin carries the highest handover probability of all. A quantity that behaves this way cannot, on its own, order samples by imminence.

@@FIG|/home/claude/figs/png_print/fig33_dose_response.png|Figure 5.13 Probability of a handover within one second against the serving-to-neighbour gap, in 2.5 dB bins, with Wilson binomial intervals. The lower panel gives the sample count in each bin, so a wide interval is visibly a small-sample interval.|6.29

## 5.9 The A3 report-conversion rate

The first of the two network findings concerns what happens to a measurement report after it is sent. Table 5.9 reports the fraction of Event A3 reports that are *not* followed by a handover command within two seconds.

@@TCAP|Table 5.9 Event A3 report-conversion rate by campaign. The figure reported is the fraction of A3 reports not followed by a handover command within two seconds.
| Campaign | Declined within 2 s |
|---|---|
| Urban arterial | 57.2 % |
| Urban loop | 60.1 % |
| Dense urban | 63.3 % |
| Highway | 71.9 % |
| **Pooled (7,385 reports)** | **62.9 %** |

@@FIG|/home/claude/figs/png_print/fig19_conversion.png|Figure 5.14 A3 report conversion by campaign. The decline rate rises with cell size, reaching 71.9 % on the highway where cells are largest.|6.3

Figure 5.14 draws the same four campaigns against the pooled rate. Two qualifiers travel with this number wherever it is quoted, and both are stated here because omitting either changes the figure materially. The measurement counts **Event A3 reports only**; taken over all measurement report types together the decline rate is 68.7 %. And it uses a **two-second conversion window**; a different window produces a different number. Both qualifiers are computable only after the configuration-timeline correction of Section 3.3, without which report type cannot be determined reliably.

The finding itself is that a measurement report is not a handover decision. Nearly two thirds of the A3 reports this network receives are declined, and the decline rate rises with cell size. Any model that treats an A3 report as a proxy label for a handover is therefore training on a label that is wrong most of the time.

## 5.10 Ping-pong: definitional instability and its actual source

The second network finding concerns ping-pong, and it has two parts: how much the reported rate depends on unstated definitional choices, and where the phenomenon actually concentrates.

Table 5.10 reports the same fixed set of 938 handovers under four definitions that differ only in choices the literature routinely leaves unstated, and the figure that follows extends that ladder to the full grid.

@@TCAP|Table 5.10 The ping-pong rate on one fixed set of handovers under four definitions.
| Definition | Rate |
|---|---|
| Return to the immediately previous cell, identified by PCI and carrier, within 15 s | **24.5 %** |
| The same, with the cell identified by PCI alone | 29.0 % |
| Any return within the window, not only to the previous cell | 38.5 % |
| Ungrouped, over the 957 raw events | 41.3 % |

The rate moves by more than sixteen percentage points without a single change to the underlying measurement. This is the quantitative form of the observation in Section 2.4, and it is the reason this thesis quotes the strictest of the four and states all three choices alongside it. It also explains how Amirova et al. [15] arrive at 0.13 % on comparable data: dividing by measurement records rather than by handovers changes the denominator by two orders of magnitude.

The window length is a fourth choice, and Figure 5.15 reports the full grid rather than the single row of Table 5.10. Across three window lengths and four identity-and-return conventions the same 938 handovers yield twelve defensible ping-pong rates between 19.5 % and 38.5 %. No cell in that grid is wrong; what is wrong is publishing one of them without saying which.

@@FIG|/home/claude/figs/png_print/fig37_pingpong_heatmap.png|Figure 5.15 The ping-pong rate over the full definitional grid: three return windows against four combinations of cell identity and return rule, computed on one unchanging set of 938 handovers. The outlined cell is the definition quoted throughout this thesis.|6.3

Table 5.11 reports where the phenomenon concentrates.

@@TCAP|Table 5.11 Ping-pong rate by carrier relationship, configuration profile and mobility regime.
| Stratum | Ping-pong rate |
|---|---|
| Intra-carrier handovers | 31.0 % |
| Inter-carrier handovers | 6.5 % |
| Dominant profile (+1 dB, 320 ms), 72 % of all handovers | 29.2 % |
| Highway campaign, mean speed 49.5 km/h | 31.1 % |

@@FIG|/home/claude/figs/png_print/fig24_pingpong_mechanism.png|Figure 5.16 Where ping-pong concentrates. The dominant axis is the carrier relationship, not the mobility regime; the highway returns as often as the urban corridors despite three times the mean speed.|6.3

Figure 5.16 separates the three strata. Two results follow. Ping-pong is concentrated almost entirely in intra-carrier handovers, at 31.0 % against 6.5 % across carriers, a factor of nearly five. And it is **not driven by speed**, which is the intuitive explanation: the highway campaign, at three times the urban mean speed, returns at 31.1 %, marginally *above* the pooled rate. The lever available to an operator is therefore the time-to-trigger of the dominant configuration profile rather than any speed-dependent adaptation. This thesis stops short of claiming a causal effect for such a change, for the reason given in Section 5.13.

Modelling the arrival stream as a self-exciting process supports the same conclusion from a different direction. The fitted Hawkes branching ratio is 0.605 with a 95 % interval of [0.524, 0.673], so each handover triggers on average approximately 0.6 further handovers; per campaign the value runs 0.649, 0.609, 0.567 and 0.513, lowest on the highway. The Ogata residual test of Section 4.11 rejects the exponential kernel (*D* = 0.074, *p* = 7 × 10⁻⁴), which is reported rather than suppressed: the clustering is real, but its temporal shape is not the exponential decay that the standard Hawkes kernel assumes. Figure 5.17 gives the per-campaign estimates with their intervals and Figure 5.18 illustrates the fitted intensity against the arrival stream itself.

@@FIG|/home/claude/figs/png_print/fig34_forest_hawkes.png|Figure 5.17 Hawkes branching ratio estimated on each campaign separately and on the pooled stream, with bootstrap intervals. The pooled estimate is drawn as a diamond in the usual convention. The per-campaign intervals overlap, so the campaigns differ in point estimate but not detectably in clustering strength.|6.3

@@FIG|/home/claude/figs/png_print/fig18_hawkes.png|Figure 5.18 Self-excitation in the handover arrival stream. The fitted branching ratio is 0.605; the Ogata residual test rejects the exponential kernel, so the clustering is real but not exponentially shaped.|6.3

## 5.11 Negative results

Four approaches were implemented in good faith, measured, and did not help. They are reported because a claim that the formulation and the protocol are what matter is credible only if the alternatives were actually tried.

@@TCAP|Table 5.12 Approaches implemented and measured that produced no improvement.
| Approach | Outcome |
|---|---|
| A dedicated ping-pong classifier | AUROC 0.51 at the one-second horizon — chance |
| Additional neighbour-cell features | No gain over the retained feature set |
| Explicit cell-clustering features | No gain over the retained feature set |
| Deep CORAL and a second unsupervised domain adaptation method | No gain over source-only training |

@@FIG|/home/claude/figs/png_print/fig22_negatives.png|Figure 5.19 Approaches that did not improve on the retained configuration. The dedicated ping-pong classifier is indistinguishable from chance.|6.3

Table 5.12 lists them and Figure 5.19 sets each against the configuration that was retained. The dedicated ping-pong classifier is the most informative of the four. Ping-pong is highly structured at the population level, as Section 5.10 shows, and yet it is not predictable at the level of the individual handover from these inputs: whether a particular transfer will be reversed appears to depend on the state of the target cell, which the handset does not observe.

The domain-adaptation null is consistent with published benchmarking rather than indicative of a faulty implementation. Ismail Fawaz et al. [25] benchmark nine unsupervised domain-adaptation algorithms over twelve time-series datasets and find several published methods performing worse than source-only training, with the adaptation technique rather than the backbone driving the outcome; the result here has the same shape.

One further ablation deserves its own figure, because its result is easy to state backwards. Figure 5.20 shows that adding the thirteen signalling features to the radio, mobility and history block changes the one-second AUPRC by nothing at all — 0.811 against 0.811 — while signalling features on their own still reach 0.370, roughly five times the prevalence floor. The signalling block therefore carries genuine information about imminence; the radio features simply carry it already.

@@FIG|/home/claude/figs/png_print/fig40_signalling_ablation.png|Figure 5.20 Feature-block ablation at the one-second horizon, one marker per seed. Signalling features are informative on their own and redundant once the radio, mobility and history block is present.|6.3

Finally, removing the signalling leakage guard of Section 4.6 raises the apparent score substantially, which is the expected behaviour of a leak and is the reason the guard exists. That configuration is not reported as a result anywhere in this thesis.

## 5.12 Discussion against the objectives

Objective O1 is met: the next handover is predicted one second ahead at AUROC 0.933 and AUPRC 0.784, 11.7× the prevalence floor, from quantities a handset already observes, against AUROC 0.653 for the rule presently deployed.

Objective O2 is met, and the answer is larger than anticipated. Grouped evaluation is worth between 4 % and 74 % depending on architecture, and because the dependence is on architecture, the protocol determines which model appears to win rather than merely how well every model appears to do.

Objective O3 is met on both its parts. Coherence is exact by construction, against 43.6 % violations for the obvious alternative, and the guarantee is reported together with the alarm rate it costs and the feasibility floor set by the number of calibration drives.

Objective O4 is met at two distances: AUROC 0.927 on a corridor and speed regime frozen out of every modelling decision, and AUROC 0.752 on an independently collected public dataset against 0.745 for a model trained on it directly.

Objective O5 is met, and produced the most interpretable finding in the thesis: the quantity the network thresholds on is nearly the weakest predictor available, while the strongest is a quantity the rule does not use at all.

## 5.13 Threats to validity

Four threats bear on the results above and are stated here rather than deferred.

**Scale and coverage.** The evidence is 57 drives on one operator over four days. The cross-regime transfer of Section 5.6 rests on a single configuration pair, because the deployed configuration is identical across all four campaigns. A second operator would test what a second corridor cannot.

**Instrument ceiling.** The one-hertz export caps event-level detection at 90.5 %. This does not affect the row-level results, which are defined on the grid itself, but it bounds every event-level figure reported in Section 5.1.

**Causal identification.** No causal claim is made about the benefit of acting on a warning, and this is a matter of identification rather than of effort. The logging policy is deterministic: given the radio state and the configuration, Event A3 either fires or it does not, so the propensity of the observed action is zero or one and the inverse-propensity weights required for off-policy evaluation are undefined. Only a counting upper bound on benefit is therefore reported, and it peaks at a five-percent alarm budget and turns negative by forty. Section 7.3 identifies the design that would make the causal question answerable on data already held.

**Comparator availability.** The nearest comparator method available on this network — a reinforcement-learning formulation of the handover *decision* developed on the same operator and instrument — was reimplemented from its method description and scored as a predictor on this data, where it proved close to uninformative. That comparison is not reported as a headline result here, because at the time of writing no publication record for the comparator could be located and a comparison against a reference a reader cannot retrieve is of limited value. The dataset released by the same authors is, however, published under a citable identifier and is the external validation set used in Section 5.7.
@@CHAPTER|6|DEMONSTRATION OF OUTCOME BASED EDUCATION

This chapter demonstrates how the work reported in Chapters 1 to 5 addresses the course outcomes, program outcomes, knowledge profiles and complex engineering problem and activity attributes required of a capstone project in EEE 4700/4800. Each claim made here refers to a specific section of the thesis rather than asserting an attribute in the abstract, and attributes that the work does not genuinely address are marked as such rather than claimed.

## 6.1 Introduction

Outcome Based Education requires that a capstone project be assessed against what the student is able to do at its conclusion rather than against the volume of work performed. The sections that follow map the activities of this project onto the defined outcomes, in the order set out in the departmental thesis format: course outcomes in Section 6.2, aspects of program outcomes in Section 6.3, knowledge profiles in Section 6.4, the use of complex engineering problems in Section 6.5, the socio-cultural, environmental and ethical impact in Section 6.6, and the attributes of complex engineering problem solving and complex engineering activities in Sections 6.7 and 6.8.

## 6.2 Course outcomes addressed

Table 6.1 lists the course outcomes defined for EEE 4700 and indicates those addressed by this project.

@@TCAP|Table 6.1 Course outcomes addressed in this project.
| CO | CO statement | PO | Addressed |
|---|---|---|---|
| CO1 | Apply knowledge of electrical and electronic engineering to the solution of complex engineering problems | PO1 | √ |
| CO2 | Identify a contemporary real-life problem related to electrical and electronic engineering by reviewing and analysing existing research works | PO2 | √ |
| CO3 | Determine functional requirements of the problem considering feasibility and efficiency through analysis and synthesis of information | PO4 | √ |
| CO4 | Select a suitable solution and determine its method considering professional ethics, codes and standards | PO8 | √ |
| CO5 | Adopt modern engineering resources and tools for the solution of the problem | PO5 | √ |
| CO6 | Prepare management plan and budgetary implications for the solution of the problem | PO11 | √ |
| CO7 | Analyse the impact of the proposed solution on health, safety, culture and society | PO6 | √ |
| CO8 | Analyse the impact of the proposed solution on environment and sustainability | PO7 | √ |
| CO9 | Develop a viable solution considering health, safety, cultural, societal and environmental aspects | PO3 | √ |
| CO10 | Work effectively as an individual and as a team member for the accomplishment of the solution | PO9 | √ |
| CO11 | Prepare various technical reports, design documentation, and deliver effective presentations for demonstration of the solution | PO10 | √ |
| CO12 | Recognise the need for continuing education and participation in professional societies and meetings | PO12 | √ |

## 6.3 Aspects of program outcomes addressed

Table 6.2 identifies the specific aspects of the relevant program outcomes that the project addresses, and states where each is evidenced.

@@TCAP|Table 6.2 Aspects of program outcomes addressed, with the evidencing section.
| PO | Aspect | Addressed | Evidence |
|---|---|---|---|
| PO3 | Public health | — | No health claim is made; see Section 6.6 |
| PO3 | Safety | √ | Connection continuity and radio-link failure, Section 1.2 |
| PO3 | Societal | √ | Section 6.6 |
| PO3 | Environmental | √ | Measured unnecessary signalling, Section 5.10 |
| PO4 | Design of experiments | √ | Grouped-drive rotation and seed repetition, Section 4.9 |
| PO4 | Analysis and interpretation of data | √ | Chapter 5 in its entirety |
| PO4 | Synthesis of information | √ | Protocol audit of 22 models, Section 2.3 |
| PO5 | Modern tool usage | √ | Drive-test instrumentation and analysis stack, Section 6.4 |
| PO6 | Societal | √ | Section 6.6 |
| PO6 | Legal | √ | Data handling and operator anonymity, Section 6.6 |
| PO7 | Societal and environmental | √ | Section 6.6 |
| PO8 | Professional ethics and responsibilities | √ | Reporting of negative results, Section 5.11 |
| PO8 | Norms | √ | Conformance to 3GPP TS 36.331 terminology throughout |
| PO10 | Comprehend and write effective reports | √ | This report |
| PO10 | Design documentation | √ | Chapters 3 and 4 |
| PO10 | Make effective presentations | √ | Progress and defence presentations |
| PO11 | Engineering management principles | √ | Section 6.9 |
| PO11 | Economic decision-making | √ | Section 6.9 |

## 6.4 Knowledge profiles addressed

Table 6.3 identifies the knowledge profiles K3 to K8 and justifies each against the content of this thesis. No profile is claimed without a corresponding section.

@@TCAP|Table 6.3 Knowledge profiles addressed, with justification.
| K | Justification |
|---|---|
| K3 | A systematic, theory-based formulation of engineering fundamentals: the discrete-time survival formulation of Section 4.3, including the product-limit identity and its monotonicity proof, and the censoring-aware likelihood of Section 4.4 |
| K4 | Specialist knowledge at the forefront of the discipline: the decoding of RRC measurement configuration under message-scoped identifiers, Section 3.3, and the recovery of deployed Event A3 parameters, Section 3.5 |
| K5 | Knowledge supporting engineering design in a practice area: the feature construction, model selection and calibration design of Sections 4.6 to 4.8, each chosen against a stated alternative |
| K6 | Knowledge of engineering practice and technology: the conduct of four drive-test campaigns with commercial diagnostic instrumentation on a live operator network, Chapter 3 |
| K7 | Comprehension of the role of engineering in society: the impact analysis of Section 6.6, including the explicit refusal to make a health claim the measurements do not support |
| K8 | Engagement with research literature: the screening of 108 publications and the protocol audit of 22 comparable models in Section 2.3, together with the methodological provenance recorded in Sections 2.5 to 2.8 |

## 6.5 Use of complex engineering problems

The problem addressed here satisfies the defining characteristics of a complex engineering problem in several independent respects.

It cannot be resolved without deep, analytically based knowledge: the incoherence of independent multi-horizon classifiers is not visible without the survival formulation of Section 4.3, and the inadmissibility of class reweighting under that formulation, Section 4.5, follows from a compounding argument that no amount of empirical tuning would reveal.

It involves conflicting technical requirements whose trade-offs must be resolved quantitatively rather than asserted. The clearest is the warning trade-off of Section 5.5: an earlier and more sensitive warning is more useful to the network and also more expensive, and the frontier from a 20 % certified miss rate at a 23 % alarm rate to a 5 % target at a 61 % alarm rate is measured rather than assumed.

It is not amenable to a standard procedure. The evaluation protocol that the comparator literature treats as standard, random-row cross-validation, is demonstrably wrong on this data, and Section 5.3 measures by how much and in which direction.

It spans several sub-disciplines: the LTE control plane, radio propagation, statistical survival analysis, distribution-free inference, point-process modelling and software engineering, and no single one of them is sufficient.

## 6.6 Socio-cultural, environmental and ethical impact

**Societal.** Bangladesh, and Dhaka in particular, sustains one of the densest populations of mobile subscribers in the world, and on the routes measured here a handover occurs every eleven seconds. Mobile connectivity in this setting is not a convenience but an infrastructure on which financial services, transport and emergency communication depend. A warning one to two seconds ahead of a handover gives the network the opportunity to prepare the target cell before an interruption occurs rather than to recover after it, which bears directly on the continuity of those services.

**Environmental and sustainability.** The environmental argument made here is confined to what was measured. Section 5.10 shows that 24.5 % of the handovers observed returned to the cell just vacated within fifteen seconds, and that the phenomenon is concentrated in intra-carrier transfers under one dominant configuration profile. Each such pair is signalling work, radio resource occupancy and processing load expended for no change in serving cell. Identifying that fraction is a precondition for reducing it. This thesis does **not** claim a measured energy saving, because no such measurement was made, and Section 5.13 states why a causal benefit claim is not identified on data of this kind.

**Health.** No health claim of any kind is made. This project involved no human subjects, took no exposure measurements and conducted no experiment bearing on health. Stating that plainly is itself the ethical position: the temptation in a thesis that touches radio transmission is to assert a health benefit on the grounds that fewer transmissions must be better, and that assertion would not be supported by anything in Chapters 3 to 5.

**Ethical and legal.** Three ethical considerations arose and were handled explicitly. Measurements were collected from the author's own handset and subscription, so no third-party user data was recorded; no subscriber identifiers appear anywhere in the dataset. The operator is not named in this report, because the findings of Section 3.5 characterise a deployed configuration and the purpose of reporting them is scientific rather than comparative. And negative results were reported rather than omitted: Section 5.11 records four approaches that were implemented and did not work, including one, the ping-pong classifier, that would have been an attractive additional contribution had it succeeded.

**Cultural.** The measurement campaigns were conducted on public roads under ordinary traffic conditions, and the driving itself conformed to local traffic regulation. No aspect of the work required access to private premises or to restricted infrastructure.

## 6.7 Attributes of complex engineering problem solving addressed

Table 6.4 maps the attributes P1 to P7 onto the work.

@@TCAP|Table 6.4 Attributes of complex engineering problem solving addressed.
| P | Attribute | Addressed | How |
|---|---|---|---|
| P1 | Depth of knowledge required | √ | Survival formulation and its monotonicity proof, Section 4.3; conformal risk control, Section 4.10 |
| P2 | Range of conflicting requirements | √ | The warning frontier of Section 5.5: lead time against false-alarm cost, measured across the whole curve |
| P3 | Depth of analysis required | √ | No standard procedure applies; the standard evaluation protocol is shown to be invalid here, Section 5.3 |
| P4 | Familiarity of issues | √ | The deployed configuration was unknown before decoding, Section 3.5, and differs in sign from the literature's assumption |
| P5 | Extent of applicable codes | √ | 3GPP TS 36.331 and TS 36.300 govern the signalling interpretation throughout Chapter 3 |
| P6 | Extent of stakeholder involvement | √ | Operator, subscriber and regulator interests differ; Section 6.6 states which are and are not addressed |
| P7 | Interdependence | √ | Six sub-problems — decoding, labelling, feature design, formulation, evaluation and risk control — each of which constrains the others |

## 6.8 Attributes of complex engineering activities addressed

Table 6.5 maps the attributes A1 to A5 onto the work.

@@TCAP|Table 6.5 Attributes of complex engineering activities addressed.
| A | Attribute | Addressed | How |
|---|---|---|---|
| A1 | Range of resources | √ | Commercial drive-test instrumentation, decoded control-plane logs, a gradient-boosting and deep-learning software stack, and 108 screened publications |
| A2 | Level of interaction | √ | Resolution of conflicting requirements between prediction horizon, calibration quality and alarm cost, Sections 5.4 and 5.5 |
| A3 | Innovation | √ | The application of a discrete-time hazard formulation and a drive-level conformal risk bound to mobility prediction, neither of which appears in the audited literature |
| A4 | Consequences for society and the environment | √ | Section 6.6, bounded to what was measured |
| A5 | Familiarity | √ | The problem falls outside standards-governed practice: no 3GPP procedure specifies handover *prediction*, and no standard definition of ping-pong exists, as Section 5.10 demonstrates quantitatively |

## 6.9 Project management, resources and budget

The project was conducted over two academic terms. The first term covered problem identification, the literature screening of Section 2.3, the first two measurement campaigns and the construction of the decoding pipeline. The second term covered the formulation and modelling of Chapter 4, the third and fourth campaigns, the evaluation of Chapter 5 and the preparation of this report. The fourth campaign was scheduled deliberately after the freeze of all modelling decisions, which is a scheduling choice with a methodological purpose: the out-of-sample status of the highway result in Section 5.6 depends on it.

@@TCAP|Table 6.6 Resource and cost summary for the project.
| Item | Justification | Cost (BDT) |
|---|---|---|
| Drive-test instrumentation | Departmental equipment, used under supervision | Nil (departmental) |
| Mobile data and subscription | Four measurement campaigns on a live network | 3,000 |
| Vehicle fuel and hire | Approximately 95 km across four campaigns, including the highway run | 9,000 |
| Computation | Model training and evaluation on personal and departmental hardware | Nil |
| Report production and binding | Three hard-bound copies as required | 3,000 |
| **Total** | | **15,000** |

Table 6.6 itemises the cost. The budget falls within the departmental allocation of BDT 15,000 per group. The dominant cost is field data collection rather than computation, which is characteristic of measurement-driven work and is the reason the feasibility floor of Section 5.5 is an economic constraint as much as a statistical one: buying a tighter guarantee means buying more driving.
@@CHAPTER|7|CONCLUSIONS

## 7.1 Summary of findings

This thesis set out to determine whether the next LTE handover can be forecast from the measurements a handset already reports, how far in advance, and with what guarantee. On four drive-test campaigns conducted on a live commercial network in Dhaka and Gazipur — 57 drives, 10,260 samples and 938 handovers whose ground truth is decoded from RRC signalling — the answer is that it can, and the five principal findings are the following.

**The next handover is predictable one second in advance.** Gradient-boosted trees under a discrete-time hazard formulation reach AUROC 0.933 and AUPRC 0.784 against a 6.7 % prevalence floor, a lift of 11.7×, at an expected calibration error of 0.024, using only quantities a handset observes at the instant of prediction. The deployed Event A3 rule, scored on the same data as a predictor, reaches AUROC 0.653 and detects 5.5 % of handovers one second ahead.

**A single hazard model makes the five horizons mutually consistent.** Because horizon probabilities are recovered as products of per-interval hazards, ordering holds by construction for any learner whose output lies in the unit interval. The measured consequence is 0 % horizon-ordering violations against 43.6 % for the five independent classifiers that the comparator literature implies, achieved from one fit, with no held-out calibration split and no post-hoc repair. The obvious alternative repair, per-horizon isotonic calibration, was implemented and makes coherence worse rather than better.

**The evaluation protocol determines which model appears to win.** Replacing grouped-drive splitting with the random-row splitting standard in the comparator literature inflates the one-second AUPRC by 74 % for a gated recurrent unit and by 4 % for logistic regression. Because the inflation scales with the temporal memory an architecture carries, a careless protocol reorders the leaderboard rather than merely raising it. This is a result about the field's evidence base, not only about the models compared here.

**The result generalises beyond the data it was developed on.** Holding out each campaign entirely, AUROC remains between 0.909 and 0.949. The highway campaign, driven after every modelling decision had been frozen, reaches AUROC 0.927 with the highest lift and the lowest calibration error of the four, and adding it to the pool moved the headline figure by nothing. On an independently collected public drive-test dataset the transferred model reaches AUROC 0.752 against 0.745 for a model trained on that dataset directly, indicating that what transfers is the formulation rather than the fit.

**The warning carries a stated guarantee, and a stated price.** Conformal risk control certified on 28 held-out drives, with the whole drive as the exchangeable unit, holds the expected per-drive miss rate below a chosen target: a 20 % target costs a 23 % alarm rate and realises 12.6 % misses, while a 5 % target costs 61 %. The number of calibration drives sets a feasibility floor of α ≥ 1/(*n*+1), here 0.034, that no improvement in the model can move.

Alongside these, two properties of the deployed network were characterised that the prediction literature has not modelled. The A3 report-conversion rate is 62.9 % declined within two seconds across 7,385 reports, rising with cell size, so a measurement report is a poor proxy label for a handover. And the ping-pong rate on one fixed set of 938 handovers moves from 24.5 % to 41.3 % depending on three definitional choices that published work routinely leaves unstated; where it concentrates is the carrier relationship, at 31.0 % intra-carrier against 6.5 % inter-carrier, and not the mobility regime, since the highway at three times the urban mean speed returns at 31.1 %.

Underlying all of these is the mechanistic finding of Section 5.8, which is the most compact statement of what the thesis found: **the network triggers on its weakest available signal.** Serving dwell time alone reaches AUROC 0.874 while the serving-to-neighbour gap that Event A3 thresholds on reaches 0.566. The gap indicates that a handover is permitted; dwell time indicates that one is becoming due; and a rule defined on permission rather than on tendency is structurally late.

## 7.2 Limitations

The limits of the present study are restated here because they determine what follows from it.

The evidence base is 57 drives, one operator, four days and one radio access technology. The deployed configuration is identical across all four campaigns, so the cross-regime transfer of Section 5.6 rests on a single configuration pair; a second operator would test what a second corridor cannot. The one-hertz measurement export caps event-level detection at 90.5 %, which bounds every event-level figure reported.

No causal claim is made about the benefit of acting on the warning. The logging policy is deterministic — given the radio state and the configuration, Event A3 either fires or it does not — so the propensities required for off-policy evaluation take the values zero and one and the causal estimand is not identified. Only a counting upper bound was reported.

Finally, the system is an offline predictor evaluated on recorded data. It has not been integrated into a network and no network key performance indicator has been measured with it in the loop.

## 7.3 Recommendations for future work

Five items follow from those limits, in the order that the limits dictate.

**A fuzzy regression-discontinuity design at the A3 boundary.** This is the first item because it is the only one that addresses the identification problem, and because it is executable on data already collected. Event A3 imposes a sharp threshold on an observable running variable; drives that fall just either side of that threshold differ locally in treatment but not systematically in anything else. A fuzzy regression-discontinuity design at the boundary would make the local causal effect of the handover decision identifiable without requiring an experimental intervention on a live network.

**A second corridor and a second operator.** Four days on one network is sufficient for a careful study and insufficient to claim generality. A second operator would additionally break the single-configuration-pair limitation, since the negative A3 offsets reported in Section 3.5 are one operator's choice rather than a property of LTE.

**Linking the warning to a measured service outcome.** The benefit reported here is a counting bound. Connecting the warning to a measured throughput or interruption effect — ideally in a testbed where the action taken on the warning can be varied — would convert that bound into an estimate.

**An experimental test of the time-to-trigger.** Section 5.10 identifies the time-to-trigger of the dominant configuration profile as the lever governing ping-pong, having ruled out speed as the driver. Varying that parameter under controlled conditions and measuring the resulting return rate is the direct test of that inference, and it would also supply the treatment variation that the causal design above requires.

**Release of code and data.** The protocol argument of Section 5.3 is a claim about how results in this field should be produced, and such a claim is only worth making if others can reproduce and contest it. Of the 22 models audited in Section 2.3, two release code and one releases data; releasing both is the minimum consistent with the argument this thesis makes.

## 7.4 Concluding remark

The contribution of this work is not a new learning algorithm, and it is worth closing by saying so directly. Gradient boosting, discrete-time survival analysis and conformal risk control are all established methods, and the thesis is explicit throughout about where each came from. What is new is the combination and the discipline imposed on it: measurement-grade ground truth decoded from signalling rather than inferred from counters, a formulation that makes multi-horizon outputs coherent by construction rather than by correction, an evaluation protocol that holds out the mobility unit and whose value is measured rather than asserted, a guarantee whose exchangeability unit is identified and defended, and a set of results tested on a corridor and a dataset the model had never seen. On the evidence of the protocol audit in Section 2.3, that combination has not previously been assembled for this problem, and the parts of it that are least novel — the grouped split, the calibration curve, the reported false-alarm rate — are the parts the field most consistently omits.

@@REFSTART

[1] 3GPP, "Evolved Universal Terrestrial Radio Access (E-UTRA); Radio Resource Control (RRC); Protocol specification," *3GPP TS 36.331*, Release 17, 2022.

[2] 3GPP, "Evolved Universal Terrestrial Radio Access (E-UTRA) and Evolved Universal Terrestrial Radio Access Network (E-UTRAN); Overall description; Stage 2," *3GPP TS 36.300*, Release 17, 2022.

[3] S. Deng, A. Peng, H. Fida, J. Meng, and Y. C. Hu, "A large-scale measurement study of mobility support in operational cellular networks," in *Proceedings of the ACM Internet Measurement Conference (IMC)*, pp. 216–230, 2018.

[4] M. Ghoshal, Z. J. Kong, Q. Xu, Y. C. Hu, and D. Koutsonikolas, "A measurement study of handover configurations in operational 5G networks," *arXiv preprint arXiv:2511.03116*, 2025.

[5] A. Hassan, A. Narayanan, A. Zhang, W. Ye, R. Zhu, S. Jin, J. Carpenter, Z. M. Mao, F. Qian, and Z.-L. Zhang, "Vivisecting mobility management in 5G cellular networks," in *Proceedings of the ACM SIGCOMM Conference*, pp. 86–100, 2022.

[6] Y. Liu, C. Peng, and Z. Tan, "M2HO: Mitigating the negative impact of mobility management on handover performance," in *Proceedings of the ACM International Conference on Mobile Computing and Networking (MobiCom)*, 2024.

[7] S. Ankome and T. Hanada, "A systematic review of machine learning approaches to handover management in mobile networks," *Machine Learning and Knowledge Extraction*, vol. 8, no. 5, article 133, 2026.

[8] A. Saoud, M. Bouchakour, and N. Boukhatem, "Handover management strategies in heterogeneous networks: a review," *Technologies*, vol. 13, no. 8, article 352, 2025.

[9] A. Chabira, S. Belkacem, and Y. Bouzid, "Performance metrics for handover evaluation in next-generation mobile networks," *Technologies*, vol. 13, no. 7, article 276, 2025.

[10] T. Dinh, P. Fazio, and M. Voznak, "Joint prediction of next-cell sequence and resource block demand from vehicular trajectories," *PLOS ONE*, vol. 21, no. 8, article e0355372, 2026.

[11] J. Sánchez-Martín, A. Fernández, and R. García, "GRIMCELL: graph learning for post-deployment KPI prediction in a commercial LTE-A Pro network," *Machine Learning and Knowledge Extraction*, vol. 8, no. 9, article 260, 2026.

[12] A. Mehregan and R. De Grande, "TH-GCN: a temporal heterogeneous graph convolutional network for handover optimisation in dense vehicular networks," *arXiv preprint arXiv:2505.04894*, presented at IEEE DCOSS-IoT, 2025.

[13] A. Graser, A. Jalali, J. Lampert, A. Weissenfeld, and K. Janowicz, "MobilityDL: a review of deep learning from trajectory data," *GeoInformatica*, vol. 29, no. 1, pp. 1–33, 2025.

[14] D. Zidic, T. Mastelic, I. N. Kosovic, M. Cagalj, and J. Lorincz, "Analyses of ping-pong handovers in real 4G telecommunication networks," *Computer Networks*, vol. 227, article 109699, 2023.

[15] A. Amirova, D. Tashmukhamedov, and B. Kamalov, "Drive-test-based analysis of handover behaviour in operational LTE and 5G networks," *Future Internet*, vol. 18, no. 6, article 290, 2026.

[16] S. Wiegrebe, P. Kopper, R. Sonabend, B. Bischl, and A. Bender, "Deep learning for survival analysis: a review," *Artificial Intelligence Review*, vol. 57, no. 3, article 65, 2024.

[17] H.-C. Thorsen-Meyer, D. Placido, B. S. Kaas-Hansen, A. P. Nielsen, T. Lange, A. Perner, and S. Brunak, "Discrete-time survival analysis in the critically ill: a deep learning approach using heterogeneous data," *npj Digital Medicine*, vol. 5, article 142, 2022.

[18] K. M. Cohen, S. Park, O. Simeone, and S. Shamai, "Calibrating AI models for wireless communications via conformal prediction," *arXiv preprint arXiv:2212.07775*, 2022.

[19] O. Simeone, S. Park, and M. Zecchin, "Conformal prediction for the design lifecycle of AI in wireless systems," *arXiv preprint arXiv:2504.09310*, 2025.

[20] A. N. Angelopoulos, S. Bates, A. Fisch, L. Lei, and T. Schuster, "Conformal risk control," in *Proceedings of the International Conference on Learning Representations (ICLR)*, 2024.

[21] A. G. Hawkes, "Spectra of some self-exciting and mutually exciting point processes," *Biometrika*, vol. 58, no. 1, pp. 83–90, 1971.

[22] P. J. Laub, Y. Lee, P. K. Pollett, and T. Taimre, "Hawkes models and their applications," *Annual Review of Statistics and Its Application*, vol. 12, pp. 233–258, 2025.

[23] Y. Ogata, "Statistical models for earthquake occurrences and residual analysis for point processes," *Journal of the American Statistical Association*, vol. 83, no. 401, pp. 9–27, 1988.

[24] M. Price-Williams and N. Heard, "Nonparametric self-exciting models for computer network traffic," *Statistics and Computing*, vol. 30, no. 2, pp. 209–220, 2020.

[25] H. Ismail Fawaz, M. Del Grosso, T. Kerdoncuff, A. Boisbunon, and I. Saffar, "Deep unsupervised domain adaptation for time series classification: a benchmark," *arXiv preprint arXiv:2312.09857*, 2023.

[26] B. Sun and K. Saenko, "Deep CORAL: correlation alignment for deep domain adaptation," in *Computer Vision – ECCV 2016 Workshops*, Lecture Notes in Computer Science, vol. 9915, pp. 443–450, 2016.

[27] Y. Shi, X. Ying, and J. Yang, "Deep unsupervised domain adaptation with time series sensor data: a survey," *Sensors*, vol. 22, no. 15, article 5507, 2022.

[28] D. Wagner, T. Michels, F. C. F. Schulz, A. Nair, M. Rudolph, and M. Kloft, "On the impossibility of an ideal point-adjusted metric for time-series anomaly detection," *arXiv preprint arXiv:2510.17562*, 2025.

[29] S. Deb, P. Monogioudis, and D. Calin, "A discrete-time Markov chain analysis of conditional handover in cellular networks," *arXiv preprint arXiv:2403.04379*, 2024.

[30] G. Ke, Q. Meng, T. Finley, T. Wang, W. Chen, W. Ma, Q. Ye, and T.-Y. Liu, "LightGBM: a highly efficient gradient boosting decision tree," in *Advances in Neural Information Processing Systems (NIPS)*, vol. 30, pp. 3146–3154, 2017.

[31] C. Guo, G. Pleiss, Y. Sun, and K. Q. Weinberger, "On calibration of modern neural networks," in *Proceedings of the International Conference on Machine Learning (ICML)*, pp. 1321–1330, 2017.

[32] B. Zadrozny and C. Elkan, "Transforming classifier scores into accurate multiclass probability estimates," in *Proceedings of the ACM SIGKDD International Conference on Knowledge Discovery and Data Mining*, pp. 694–699, 2002.

[33] M. Shafi, S. Rahman, and A. Hossain, "Drive-test-based LTE handover dataset," *Mendeley Data*, v2, doi:10.17632/n2pvmtyn2j.1, 2025.

[34] B. Lakshminarayanan, A. Pritzel, and C. Blundell, "Simple and scalable predictive uncertainty estimation using deep ensembles," in *Advances in Neural Information Processing Systems (NIPS)*, vol. 30, pp. 6402–6413, 2017.

@@APPENDIX|A|FULL PER-HORIZON RESULTS

Table A.1 gives the per-horizon AUPRC of every learner compared in Section 5.2, against the prevalence floor of each horizon. Table A.2 gives the event-level operating characteristics of the primary model at the certified operating point of Section 5.5.

@@TCAP|Table A.1 Complete per-horizon results for all seven learners under the grouped-drive rotation. AUPRC is reported with its prevalence floor; lift is AUPRC divided by prevalence.
| Model | 0.5 s | 1 s | 2 s | 3 s | 5 s |
|---|---|---|---|---|---|
| LightGBM | 0.416 | 0.784 | 0.627 | 0.598 | 0.606 |
| Logistic regression | 0.381 | 0.712 | 0.579 | 0.551 | 0.563 |
| Multi-layer perceptron | 0.352 | 0.681 | 0.552 | 0.528 | 0.541 |
| Temporal convolutional network | 0.331 | 0.646 | 0.527 | 0.505 | 0.519 |
| Transformer | 0.324 | 0.633 | 0.518 | 0.497 | 0.512 |
| Gated recurrent unit | 0.316 | 0.617 | 0.506 | 0.487 | 0.503 |
| Event A3 rule | 0.061 | 0.113 | 0.187 | 0.241 | 0.318 |
| Prevalence floor | 0.037 | 0.067 | 0.125 | 0.175 | 0.259 |

@@TCAP|Table A.2 Event-level operating characteristics of the primary model at the certified operating point of Section 5.5.
| Quantity | Value |
|---|---|
| Handover events detected, 1 s horizon | 44.7 % |
| Handover events detected, 5 s horizon | 65.1 % |
| Ceiling imposed by the 1 Hz grid | 90.5 % |
| Samples alarmed at α = 0.20 | 23 % |
| Realised per-drive miss rate at α = 0.20 | 12.6 % |
| Drives on which the bound held | 82 % |

@@APPENDIX|B|FEATURE INVENTORY

The 107 features retained after the degenerate-feature filter of Section 4.6 are organised as follows. All rolling statistics are computed per drive over backward-looking windows closing at the prediction instant.

**Radio block (83 features).** For each of serving RSRP, serving RSRQ, serving SINR and the corresponding best-neighbour quantities: the instantaneous value; the rolling mean, standard deviation, range and first difference over 3, 5 and 10 second windows; and the serving-to-neighbour gap in each quantity together with its rolling statistics over the same windows.

**Mobility block (17 features).** GPS speed and its rolling mean and standard deviation over 3, 5 and 10 s; heading and absolute heading change over the same windows; longitudinal acceleration and its rolling statistics; and a stationarity indicator derived from the speed trace.

**Signalling block (13 features).** Counts of measurement reports by event type within the preceding 5 and 10 s; time since the most recent report of each type, subject to the leakage guard of Section 4.6; the identifier of the report configuration in force; and the offset and time-to-trigger values it carries.

**History block (7 features).** Serving dwell time; time since the previous handover command; the count of handover commands within the preceding 30 and 60 s; the number of distinct serving cells within the preceding 60 s; and an indicator of whether the previous handover was a return to the cell before it.

@@APPENDIX|C|REPRODUCTION NOTES

The analysis pipeline is organised as a sequence of numbered stages, each of which writes its outputs to a versioned directory and records the configuration under which it ran. The stages are, in order: signalling decoding and configuration-timeline construction; drive segmentation and quality control; feature construction; long-format expansion for the hazard formulation; model fitting under the grouped rotation; calibration; conformal threshold certification; event-level scoring; transfer and external validation; and point-process fitting with residual testing.

Two conventions are enforced throughout and are worth recording because they are the source of most reproduction failures in work of this kind. First, no stage may read a file written by a later stage, which makes the dependency order a directed acyclic graph that can be verified mechanically. Second, every table reported in Chapters 4 and 5 is regenerated from the stage outputs rather than transcribed, so that a change in an upstream stage propagates to the report rather than silently disagreeing with it.

The modelling decisions frozen before the fourth measurement campaign are recorded in a manifest fixing the feature set, the formulation, the model family, the hyperparameter search space and the evaluation protocol. The out-of-sample status of the highway result in Section 5.6 rests on that manifest.

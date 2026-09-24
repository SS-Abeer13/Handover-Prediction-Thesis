# PART 1A: CHAPTER 1 (INTRODUCTION)


# CHAPTER 1: INTRODUCTION

Mobility is the property that distinguishes a cellular network from every other access technology, and the handover is the mechanism that delivers it. Each time a user equipment moves beyond the useful coverage of its serving cell, the network must transfer the connection to a neighbour without interrupting the service carried on it. On a dense urban network this happens constantly: across the measurement campaigns reported in this thesis, a handover occurred on average once every eleven seconds of driving. Every one of those events is a brief window in which throughput drops, latency rises and, occasionally, the radio link fails outright.

This chapter states the problem the thesis addresses, the reason it is worth addressing, and the objectives against which the work should be judged. Section 1.1 describes how handover is triggered in Long Term Evolution (LTE) and why the triggering rule is structurally incapable of providing advance warning. Section 1.2 quantifies the cost of that limitation on measured data. Section 1.3 states the problem formally, Section 1.4 lists the objectives, Section 1.5 bounds the scope, Section 1.6 summarises the contributions, and Section 1.7 describes the organisation of the remainder of the report.


## 1.1 Background

In an LTE network the user equipment (UE) continuously measures the Reference Signal Received Power (RSRP) and Reference Signal Received Quality (RSRQ) of its serving cell and of the neighbour cells it can detect, and reports those measurements to the network when a condition configured by the network is satisfied [1]. The dominant condition governing intra-frequency mobility is Event A3, which is defined in 3GPP TS 36.331 as the condition that a neighbour cell becomes better than the serving cell by a configured offset, and that this relation persists for a configured time-to-trigger (TTT) before the report is sent [1].

Two properties of that definition matter for this thesis. First, the condition is written on a comparison that must already hold: the neighbour must have become better before anything happens. Second, the TTT imposes an additional delay whose purpose is to suppress spurious triggering caused by fast fading. Together they guarantee that by the time a measurement report leaves the handset, the radio environment has already changed. The network then evaluates the report and, if it decides to proceed, issues an RRCConnectionReconfiguration message carrying mobilityControlInfo, which is the handover command itself.

Event A3 is therefore a reaction rule and not a prediction rule, and this is not a deficiency of the standard. The rule was designed to decide reliably, not early, and it performs that function well. What the standard does not provide, and what an increasingly latency-sensitive service mix increasingly wants, is advance notice: an indication, one or two seconds before the fact, that a handover is imminent, so that the target cell can be prepared, the transmission schedule adjusted, or an unnecessary transfer suppressed.


## 1.2 Motivation

The cost of reacting rather than anticipating is measurable, and it was measured on the data collected for this thesis rather than assumed from the literature. Across four campaigns totalling 2.9 hours of driving, 938 signalling-confirmed handovers were observed, a mean interval of eleven seconds with a median gap of three and a half seconds between consecutive events. Of those handovers, 24.5 % returned to the cell just vacated within fifteen seconds; each such pair represents two signalling exchanges and two service interruptions that produced no net change in serving cell. The radio link failed and required re-establishment 341 times. Of 7,385 Event A3 reports transmitted by the handset, 62.9 % were not followed by a handover command within two seconds, indicating that the majority of the control-plane traffic the rule generates does not result in mobility at all.

These are not pathological numbers for a dense urban deployment; they are what the deployed configuration produces. They do, however, establish that even a short prediction horizon has something to act on. A warning one second ahead of a handover command is sufficient time for the network to complete target-cell preparation, and a warning that a handover is likely to be reversed within fifteen seconds is sufficient information to consider not performing it.

The natural question is whether such a predictor already exists. A screening of 108 publications, of which 22 were audited in detail in Chapter 2, indicates that it does not exist in a form an operator could act upon. Of those 22 models, none holds out the mobility unit — a whole drive or a whole device session — when evaluating a per-timestep classification task on measured radio data; none reports a calibration curve, an expected calibration error or a Brier score; and none reports how early its warnings arrive or how many false alarms they generate per unit time. Seven report headline accuracy on tasks whose positive-class prevalence lies between 0.86 % and 11 %, where a constant negative prediction already scores between 89 % and 99 %.


## 1.3 Problem statement

The problem addressed in this thesis is the following. Given the measurements available to a handset at time t — serving and neighbour signal levels and qualities, their short-term statistics, mobility state and the recent signalling history — estimate the probability that the network will issue a handover command within h seconds, for several values of h simultaneously, such that:

- the estimates are mutually consistent, in the sense that the probability for a longer horizon is never smaller than that for a shorter one;
- the estimates are calibrated, in the sense that an asserted probability of p corresponds to an empirical event frequency near p;
- the evaluation protocol cannot transfer information from a test drive into training; and
- the warning derived from the estimates carries a stated bound on the fraction of handovers it will miss on future drives.
None of these four requirements is satisfied jointly anywhere in the audited literature, and the first and fourth are not satisfied anywhere at all in the handover-prediction setting.


## 1.4 Objectives

The specific objectives of this thesis are as follows.

O1. To predict the next handover at five look-ahead times — 0.5, 1, 2, 3 and 5 seconds — using only quantities observable at the handset at the instant of prediction.

O2. To establish an evaluation protocol that cannot leak information between training and test, by grouping every split at the level of the whole drive, and to measure how much that protocol is worth relative to the random-row splitting that is standard in the comparator literature.

O3. To make the resulting probabilities usable by an operator: mutually coherent across horizons, calibrated in value, and accompanied by a distribution-free bound on the per-drive miss rate.

O4. To test whether the result generalises beyond the campaign on which it was developed, both to a corridor and speed regime held out entirely and to an independently collected public dataset.

O5. To explain the mechanism underlying the prediction, rather than reporting accuracy alone, and in doing so to characterise the behaviour of the deployed mobility configuration on this network.


## 1.5 Scope and limitations

The scope of this work is deliberately bounded, and the bounds are stated here rather than deferred to the conclusion.

The study covers one commercial LTE operator, four measurement days, two mobility regimes and 57 drives. It does not claim that the numerical results transfer to another operator or another radio access technology, although Chapter 5 reports an external validation that bears on that question. The measurement export is sampled at one hertz, which caps the fraction of handover events that can in principle be resolved at 90.5 %; this is a property of the instrument and not of the models.

The system developed here is an offline predictor evaluated on recorded data. It is not integrated into a network, and no claim is made that deploying it would improve any network key performance indicator. In particular, no causal claim is made about the benefit of acting on the warning, for the reason given in Chapter 5: the logging policy is deterministic, so the propensities required for off-policy evaluation are zero or one and the causal estimand is not identified on observational data of this kind. Only a counting upper bound is reported.

Finally, the thesis makes no claim relating to human health. No human subjects were involved, no exposure measurements were taken, and the impact analysis in Chapter 6 is confined to what the measurements support.


## 1.6 Contributions

The contributions of this thesis are the following five, each of which is supported by a specific result in Chapter 5.

1. A discrete-time hazard formulation of handover prediction that renders five look-ahead horizons mutually consistent from a single model fit, for any learner, without a held-out calibration split and without post-hoc correction. Measured effect: 0 % horizon-ordering violations against 43.6 % for independent per-horizon classifiers.

2. A measurement of the value of grouped evaluation on drive-test radio data, showing that the inflation caused by random-row splitting is architecture-dependent — 74 % for a gated recurrent unit against 4 % for logistic regression — and therefore reorders the model ranking rather than merely raising it.

3. A distribution-free risk guarantee whose exchangeable unit is the drive, together with the campaign-design rule that follows from it: the number of calibration drives determines the tightest miss-rate target a study can express, independently of model quality.

4. A signalling-decoding correction, in the form of a configuration timeline for message-scoped measurement identifiers, which establishes that the deployed A3 offsets on this network are negative rather than the positive values assumed in the prediction literature.

5. Two characterisations of network behaviour that the prediction literature has not modelled: the A3 report-conversion rate, measured at 62.9 % declined within two seconds, and a ping-pong rate reported together with the three definitional choices that determine its value.


## 1.7 Organisation of the report

The remainder of this report is organised as follows. Chapter 2 reviews the four literatures that bear on this problem — cellular measurement studies, handover prediction, survival analysis and distribution-free uncertainty quantification — presents a protocol audit of the 22 most comparable prediction models, and sets out the methodology adopted, including the approaches that were considered and rejected. Chapter 3 describes the measurement campaign, the signalling-decoding procedure and the construction of the dataset. Chapter 4 develops the predictive formulation, the feature construction, the models compared, the evaluation protocol and the risk-control procedure. Chapter 5 reports and discusses the results against the objectives of Section 1.4. Chapter 6 demonstrates how the work addresses the course outcomes, program outcomes, knowledge profiles and complex engineering problem and activity attributes required of a capstone project. Chapter 7 concludes and identifies the work that follows from the limits of the present study.

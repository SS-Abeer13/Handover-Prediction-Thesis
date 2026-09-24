# PART 4: CHAPTER 6 (OUTCOME BASED EDUCATION), CHAPTER 7 (CONCLUSIONS) & APPENDICES B-C


# CHAPTER 6: DEMONSTRATION OF OUTCOME BASED EDUCATION

This chapter demonstrates how the work reported in Chapters 1 to 5 addresses the course outcomes, program outcomes, knowledge profiles and complex engineering problem and activity attributes required of a capstone project in EEE 4700/4800. Each claim made here refers to a specific section of the thesis rather than asserting an attribute in the abstract, and attributes that the work does not genuinely address are marked as such rather than claimed.


## 6.1 Introduction

Outcome Based Education requires that a capstone project be assessed against what the student is able to do at its conclusion rather than against the volume of work performed. The sections that follow map the activities of this project onto the defined outcomes, in the order set out in the departmental thesis format: course outcomes in Section 6.2, aspects of program outcomes in Section 6.3, knowledge profiles in Section 6.4, the use of complex engineering problems in Section 6.5, the socio-cultural, environmental and ethical impact in Section 6.6, and the attributes of complex engineering problem solving and complex engineering activities in Sections 6.7 and 6.8.


## 6.2 Course outcomes addressed


## 6.3 Aspects of program outcomes addressed


## 6.4 Knowledge profiles addressed


## 6.5 Use of complex engineering problems

The problem addressed here satisfies the defining characteristics of a complex engineering problem in several independent respects.

It cannot be resolved without deep, analytically based knowledge: the incoherence of independent multi-horizon classifiers is not visible without the survival formulation of Section 4.3, and the inadmissibility of class reweighting under that formulation, Section 4.5, follows from a compounding argument that no amount of empirical tuning would reveal.

It involves conflicting technical requirements whose trade-offs must be resolved quantitatively rather than asserted. The clearest is the warning trade-off of Section 5.5: an earlier and more sensitive warning is more useful to the network and also more expensive, and the frontier from a 20 % certified miss rate at a 23 % alarm rate to a 5 % target at a 61 % alarm rate is measured rather than assumed.

It is not amenable to a standard procedure. The evaluation protocol that the comparator literature treats as standard, random-row cross-validation, is demonstrably wrong on this data, and Section 5.3 measures by how much and in which direction.

It spans several sub-disciplines: the LTE control plane, radio propagation, statistical survival analysis, distribution-free inference, point-process modelling and software engineering, and no single one of them is sufficient.


## 6.6 Socio-cultural, environmental and ethical impact

Societal. Bangladesh, and Dhaka in particular, sustains one of the densest populations of mobile subscribers in the world, and on the routes measured here a handover occurs every eleven seconds. Mobile connectivity in this setting is not a convenience but an infrastructure on which financial services, transport and emergency communication depend. A warning one to two seconds ahead of a handover gives the network the opportunity to prepare the target cell before an interruption occurs rather than to recover after it, which bears directly on the continuity of those services.

Environmental and sustainability. The environmental argument made here is confined to what was measured. Section 5.10 shows that 24.5 % of the handovers observed returned to the cell just vacated within fifteen seconds, and that the phenomenon is concentrated in intra-carrier transfers under one dominant configuration profile. Each such pair is signalling work, radio resource occupancy and processing load expended for no change in serving cell. Identifying that fraction is a precondition for reducing it. This thesis does not claim a measured energy saving, because no such measurement was made, and Section 5.13 states why a causal benefit claim is not identified on data of this kind.

Health. No health claim of any kind is made. This project involved no human subjects, took no exposure measurements and conducted no experiment bearing on health. Stating that plainly is itself the ethical position: the temptation in a thesis that touches radio transmission is to assert a health benefit on the grounds that fewer transmissions must be better, and that assertion would not be supported by anything in Chapters 3 to 5.

Ethical and legal. Three ethical considerations arose and were handled explicitly. Measurements were collected from the author's own handset and subscription, so no third-party user data was recorded; no subscriber identifiers appear anywhere in the dataset. The operator is not named in this report, because the findings of Section 3.5 characterise a deployed configuration and the purpose of reporting them is scientific rather than comparative. And negative results were reported rather than omitted: Section 5.11 records four approaches that were implemented and did not work, including one, the ping-pong classifier, that would have been an attractive additional contribution had it succeeded.

Cultural. The measurement campaigns were conducted on public roads under ordinary traffic conditions, and the driving itself conformed to local traffic regulation. No aspect of the work required access to private premises or to restricted infrastructure.


## 6.7 Attributes of complex engineering problem solving addressed


## 6.8 Attributes of complex engineering activities addressed


## 6.9 Project management, resources and budget

The project was conducted over two academic terms. The first term covered problem identification, the literature screening of Section 2.3, the first two measurement campaigns and the construction of the decoding pipeline. The second term covered the formulation and modelling of Chapter 4, the third and fourth campaigns, the evaluation of Chapter 5 and the preparation of this report. The fourth campaign was scheduled deliberately after the freeze of all modelling decisions, which is a scheduling choice with a methodological purpose: the out-of-sample status of the highway result in Section 5.6 depends on it.

The budget falls within the departmental allocation of BDT 15,000 per group. The dominant cost is field data collection rather than computation, which is characteristic of measurement-driven work and is the reason the feasibility floor of Section 5.5 is an economic constraint as much as a statistical one: buying a tighter guarantee means buying more driving.


# CHAPTER 7: CONCLUSIONS


## 7.1 Summary of findings

This thesis set out to determine whether the next LTE handover can be forecast from the measurements a handset already reports, how far in advance, and with what guarantee. On four drive-test campaigns conducted on a live commercial network in Dhaka and Gazipur — 57 drives, 10,260 samples and 938 handovers whose ground truth is decoded from RRC signalling — the answer is that it can, and the five principal findings are the following.

The next handover is predictable one second in advance. Gradient-boosted trees under a discrete-time hazard formulation reach AUROC 0.933 and AUPRC 0.784 against a 6.7 % prevalence floor, a lift of 11.7×, at an expected calibration error of 0.024, using only quantities a handset observes at the instant of prediction. The deployed Event A3 rule, scored on the same data as a predictor, reaches AUROC 0.653 and detects 5.5 % of handovers one second ahead.

A single hazard model makes the five horizons mutually consistent. Because horizon probabilities are recovered as products of per-interval hazards, ordering holds by construction for any learner whose output lies in the unit interval. The measured consequence is 0 % horizon-ordering violations against 43.6 % for the five independent classifiers that the comparator literature implies, achieved from one fit, with no held-out calibration split and no post-hoc repair. The obvious alternative repair, per-horizon isotonic calibration, was implemented and makes coherence worse rather than better.

The evaluation protocol determines which model appears to win. Replacing grouped-drive splitting with the random-row splitting standard in the comparator literature inflates the one-second AUPRC by 74 % for a gated recurrent unit and by 4 % for logistic regression. Because the inflation scales with the temporal memory an architecture carries, a careless protocol reorders the leaderboard rather than merely raising it. This is a result about the field's evidence base, not only about the models compared here.

The result generalises beyond the data it was developed on. Holding out each campaign entirely, AUROC remains between 0.909 and 0.949. The highway campaign, driven after every modelling decision had been frozen, reaches AUROC 0.927 with the highest lift and the lowest calibration error of the four, and adding it to the pool moved the headline figure by nothing. On an independently collected public drive-test dataset the transferred model reaches AUROC 0.752 against 0.745 for a model trained on that dataset directly, indicating that what transfers is the formulation rather than the fit.

The warning carries a stated guarantee, and a stated price. Conformal risk control certified on 28 held-out drives, with the whole drive as the exchangeable unit, holds the expected per-drive miss rate below a chosen target: a 20 % target costs a 23 % alarm rate and realises 12.6 % misses, while a 5 % target costs 61 %. The number of calibration drives sets a feasibility floor of α ≥ 1/(n+1), here 0.034, that no improvement in the model can move.

Alongside these, two properties of the deployed network were characterised that the prediction literature has not modelled. The A3 report-conversion rate is 62.9 % declined within two seconds across 7,385 reports, rising with cell size, so a measurement report is a poor proxy label for a handover. And the ping-pong rate on one fixed set of 938 handovers moves from 24.5 % to 41.3 % depending on three definitional choices that published work routinely leaves unstated; where it concentrates is the carrier relationship, at 31.0 % intra-carrier against 6.5 % inter-carrier, and not the mobility regime, since the highway at three times the urban mean speed returns at 31.1 %.

Underlying all of these is the mechanistic finding of Section 5.8, which is the most compact statement of what the thesis found: the network triggers on its weakest available signal. Serving dwell time alone reaches AUROC 0.874 while the serving-to-neighbour gap that Event A3 thresholds on reaches 0.566. The gap indicates that a handover is permitted; dwell time indicates that one is becoming due; and a rule defined on permission rather than on tendency is structurally late.


## 7.2 Limitations

The limits of the present study are restated here because they determine what follows from it.

The evidence base is 57 drives, one operator, four days and one radio access technology. The deployed configuration is identical across all four campaigns, so the cross-regime transfer of Section 5.6 rests on a single configuration pair; a second operator would test what a second corridor cannot. The one-hertz measurement export caps event-level detection at 90.5 %, which bounds every event-level figure reported.

No causal claim is made about the benefit of acting on the warning. The logging policy is deterministic — given the radio state and the configuration, Event A3 either fires or it does not — so the propensities required for off-policy evaluation take the values zero and one and the causal estimand is not identified. Only a counting upper bound was reported.

Finally, the system is an offline predictor evaluated on recorded data. It has not been integrated into a network and no network key performance indicator has been measured with it in the loop.


## 7.3 Recommendations for future work

Five items follow from those limits, in the order that the limits dictate.

A fuzzy regression-discontinuity design at the A3 boundary. This is the first item because it is the only one that addresses the identification problem, and because it is executable on data already collected. Event A3 imposes a sharp threshold on an observable running variable; drives that fall just either side of that threshold differ locally in treatment but not systematically in anything else. A fuzzy regression-discontinuity design at the boundary would make the local causal effect of the handover decision identifiable without requiring an experimental intervention on a live network.

A second corridor and a second operator. Four days on one network is sufficient for a careful study and insufficient to claim generality. A second operator would additionally break the single-configuration-pair limitation, since the negative A3 offsets reported in Section 3.5 are one operator's choice rather than a property of LTE.

Linking the warning to a measured service outcome. The benefit reported here is a counting bound. Connecting the warning to a measured throughput or interruption effect — ideally in a testbed where the action taken on the warning can be varied — would convert that bound into an estimate.

An experimental test of the time-to-trigger. Section 5.10 identifies the time-to-trigger of the dominant configuration profile as the lever governing ping-pong, having ruled out speed as the driver. Varying that parameter under controlled conditions and measuring the resulting return rate is the direct test of that inference, and it would also supply the treatment variation that the causal design above requires.

Release of code and data. The protocol argument of Section 5.3 is a claim about how results in this field should be produced, and such a claim is only worth making if others can reproduce and contest it. Of the 22 models audited in Section 2.3, two release code and one releases data; releasing both is the minimum consistent with the argument this thesis makes.


## 7.4 Concluding remark

The contribution of this work is not a new learning algorithm, and it is worth closing by saying so directly. Gradient boosting, discrete-time survival analysis and conformal risk control are all established methods, and the thesis is explicit throughout about where each came from. What is new is the combination and the discipline imposed on it: measurement-grade ground truth decoded from signalling rather than inferred from counters, a formulation that makes multi-horizon outputs coherent by construction rather than by correction, an evaluation protocol that holds out the mobility unit and whose value is measured rather than asserted, a guarantee whose exchangeability unit is identified and defended, and a set of results tested on a corridor and a dataset the model had never seen. On the evidence of the protocol audit in Section 2.3, that combination has not previously been assembled for this problem, and the parts of it that are least novel — the grouped split, the calibration curve, the reported false-alarm rate — are the parts the field most consistently omits.


# APPENDIX B: FEATURE INVENTORY

The 107 features retained after the degenerate-feature filter of Section 4.6 are organised as follows. All rolling statistics are computed per drive over backward-looking windows closing at the prediction instant.

Radio block (83 features). For each of serving RSRP, serving RSRQ, serving SINR and the corresponding best-neighbour quantities: the instantaneous value; the rolling mean, standard deviation, range and first difference over 3, 5 and 10 second windows; and the serving-to-neighbour gap in each quantity together with its rolling statistics over the same windows.

Mobility block (17 features). GPS speed and its rolling mean and standard deviation over 3, 5 and 10 s; heading and absolute heading change over the same windows; longitudinal acceleration and its rolling statistics; and a stationarity indicator derived from the speed trace.

Signalling block (13 features). Counts of measurement reports by event type within the preceding 5 and 10 s; time since the most recent report of each type, subject to the leakage guard of Section 4.6; the identifier of the report configuration in force; and the offset and time-to-trigger values it carries.

History block (7 features). Serving dwell time; time since the previous handover command; the count of handover commands within the preceding 30 and 60 s; the number of distinct serving cells within the preceding 60 s; and an indicator of whether the previous handover was a return to the cell before it.


# APPENDIX C: REPRODUCTION NOTES

The analysis pipeline is organised as a sequence of numbered stages, each of which writes its outputs to a versioned directory and records the configuration under which it ran. The stages are, in order: signalling decoding and configuration-timeline construction; drive segmentation and quality control; feature construction; long-format expansion for the hazard formulation; model fitting under the grouped rotation; calibration; conformal threshold certification; event-level scoring; transfer and external validation; and point-process fitting with residual testing.

Two conventions are enforced throughout and are worth recording because they are the source of most reproduction failures in work of this kind. First, no stage may read a file written by a later stage, which makes the dependency order a directed acyclic graph that can be verified mechanically. Second, every table reported in Chapters 4 and 5 is regenerated from the stage outputs rather than transcribed, so that a change in an upstream stage propagates to the report rather than silently disagreeing with it.

The modelling decisions frozen before the fourth measurement campaign are recorded in a manifest fixing the feature set, the formulation, the model family, the hyperparameter search space and the evaluation protocol. The out-of-sample status of the highway result in Section 5.6 rests on that manifest.

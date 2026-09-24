# PART 3: CHAPTER 5 (RESULTS AND DISCUSSION)


# CHAPTER 5: RESULTS AND DISCUSSION

This chapter reports what the system of Chapter 4 achieves on the data of Chapter 3, and discusses each result against the objectives stated in Section 1.4. Section 5.1 reports the primary prediction result. Sections 5.2 to 5.5 report the four results that concern the method rather than the score: model ranking under an equal budget, the measured cost of a careless evaluation protocol, coherence and calibration, and the risk-control frontier. Sections 5.6 and 5.7 report generalisation within and beyond the campaign. Sections 5.8 to 5.10 report the mechanism and the two network findings. Section 5.11 reports the negative results, Section 5.12 discusses the outcome against the objectives, and Section 5.13 states the threats to validity.

All figures in this chapter are computed out of fold under the grouped-drive rotation of Section 4.9 unless stated otherwise.


## 5.1 The primary prediction result

One second before a handover command, the model reaches AUROC 0.933 and AUPRC 0.784 against a prevalence floor of 6.7 %, a lift of 11.7×, at an expected calibration error of 0.024. This is the headline result of the thesis and it answers objective O1.

Two features of Table 5.1 require comment because they are easy to misread. First, the AUPRC value at two seconds (0.627) is lower than at one second (0.784) while the prevalence is higher; the correct comparison is the lift column, where 11.7× at one second falls to 5.0× at two. Reading AUPRC across rows without the floor is precisely the error that Section 2.3 documents in the comparator literature. Second, the calibration error rises monotonically with the horizon, from 0.023 at half a second to 0.141 at five. The model is well calibrated where the task is sharp and poorly calibrated where it is diffuse, and this is reported rather than concealed because it bounds the horizon at which the output can be used as a probability rather than as a ranking.

The comparison that matters operationally is against the rule presently deployed. Scored on the same data as a predictor, Event A3 reaches AUROC 0.653 and detects 5.5 % of handovers one second ahead.

At the event level rather than the sample level, 44.7 % of handover events are detected one second in advance and 65.1 % at five seconds, against a ceiling of 90.5 % imposed by the one-hertz sampling grid described in Section 3.6. The ceiling is a property of the instrument; the gap between 44.7 % and 90.5 % is the property of the model.

Two views of that result are worth separating, because they answer different questions. Figure 5.1 reports where the model sits on the receiver-operating and precision-recall planes at each horizon, restricted to the low-false-positive region an operator would actually use. Figure 5.2 leaves the sample level entirely and plots the quantity an operator pays: the fraction of handover events caught against the number of false-alarm episodes raised per hour of driving.


## 5.2 Model comparison under an equal budget

The ordering is itself a finding. LightGBM leads at every horizon and logistic regression is second, ahead of all four architectures with temporal memory. This is not an argument that sequence models are unsuitable for the task in general; it is a statement about a dataset of 57 drives. With 10,260 samples and 938 events, there is insufficient data for a sequence model to learn a temporal representation that improves on the rolling statistics constructed by hand in Section 4.6, and each of the four was given the same twenty-trial budget in which to try.

The deployed A3 rule sits at the bottom of the table by a wide margin, which is the expected result and not a criticism of the rule: Event A3 is a decision procedure that the standard designed to be reliable rather than early, and Section 5.8 shows the mechanistic reason why the quantity it thresholds on carries little predictive signal.


## 5.3 The evaluation protocol is worth more than the model

The result in this section concerns the protocol rather than the predictor, and it is the one with the widest implication for the comparator literature.

The experiment is a controlled substitution. Everything is held fixed — the data, the features, the formulation, the hyperparameters, the seeds — and only the splitting rule is changed, from grouping by whole drive to splitting rows at random. Table 5.3 reports the resulting inflation.

The mechanism is straightforward once stated. Two samples one second apart on the same drive are near-duplicates: the serving cell is the same, the neighbour set is the same, and the rolling features overlap in nine of their ten seconds. A random split therefore places almost the same row on both sides of it, and the more temporal memory an architecture carries, the more it profits from encountering its own near-neighbour during training. The parameter-free A3 rule has nothing to over-fit with, and its score moves slightly in the opposite direction.

The consequence is sharper than the familiar statement that a leaky protocol raises scores. Because the inflation is architecture-dependent, it reorders the ranking. Under random-row splitting on this data the gated recurrent unit rises from sixth place to a position it does not hold under grouped splitting, which is to say that a study using the standard protocol of the comparator literature could conclude that a sequence model wins on data where it does not. This answers objective O2, and it is why the protocol is presented in this thesis as a contribution rather than as housekeeping.


## 5.4 Coherence and calibration

The hazard formulation produces no horizon-ordering violations, which follows from Equation (4.5) and requires no verification beyond confirming that the implementation matches the equation. The independent-classifier arm violates ordering on 43.6 % of samples.

The isotonic control deserves its own sentence because it is the obvious objection to the whole formulation. If per-horizon calibration can repair the outputs of independent classifiers, the hazard formulation buys nothing that a post-processing step could not. The measurement shows the opposite: applying isotonic regression per horizon makes coherence worse, from 43.6 % to 48.7 % of samples, and enlarges the largest single violation from 0.495 to 0.596. The reason is that the K isotonic maps are fitted independently and are therefore free to reorder the horizons relative to one another. The control can win on calibration error considered alone — it is a more expressive calibrator than temperature scaling — but it cannot win on calibration and coherence together, and it costs a held-out split and two to five AUPRC points to try.

Against an uncalibrated baseline, the calibration of the hazard formulation is superior at every horizon, with p < 0.0001 over the twenty paired folds of Section 4.9.

Because the folds are paired, the appropriate picture is a paired one. Figure 5.6 draws one line per fold between the two formulations: the calibration error falls on every fold without exception, which is what makes the signed-rank test meaningful on only eight observations. Figure 5.7 then follows the same comparison along the horizon axis, and adds the result that bounds the usable range of the output: both formulations degrade steeply beyond two seconds, so the five-second probability should be read as a ranking rather than as a probability.

The operational meaning of an expected calibration error of 0.024 at the one-second horizon is worth stating plainly, because a calibration figure is easy to report and easy to ignore. It means that among the samples on which the system asserts a probability near 0.8, a handover follows within one second on approximately 80 % of occasions. That is what permits the output to enter a decision rule rather than merely to sort samples, and it is what none of the 22 audited models in Section 2.3 reports. Together with Section 5.5 this answers objective O3.


## 5.5 The risk-control frontier and its price

Three observations follow.

First, the guarantee is real and it is cheap at a loose target. At α = 0.20 the certified threshold alarms on 23 % of samples and realises a miss rate of 12.6 %, comfortably inside the promise, and the per-drive bound held on 82 % of held-out drives.

Second, the guarantee becomes expensive quickly. At α = 0.05 the alarm rate rises to 61 % of samples, which is not an operating point any operator would deploy. Reporting the whole frontier rather than a single flattering point is a deliberate choice, and it is the honest form of a claim about guaranteed performance: the guarantee is not free, and its price is the alarm rate.

Third, and most consequentially, the number of calibration drives binds independently of model quality. With n = 28, Equation (4.11) gives a feasibility floor of α ≥ 0.034: no target tighter than approximately 3.4 % can be expressed at all, however good the predictor becomes. A study that wishes to promise 2 % needs at least 49 calibration drives. This converts a modelling question into a campaign-design question, and it is the practical form of the contribution claimed in Section 1.6.


## 5.6 Generalisation across corridors and speed regimes

Objective O4 asks whether the result survives outside the data on which it was developed. Two experiments address it, at increasing distance from the training distribution.

The first holds out each campaign in its entirety, training on the remaining three. Table 5.6 reports the outcome.

AUROC remains between 0.909 and 0.949 across all four, so no single campaign is carrying the pooled result. The weakest row is the urban loop, and the reason is size rather than difficulty: at eight drives, 174 handovers and 24 minutes it is the smallest campaign, so it both contributes least to the training partitions of the other rows and produces the least certain test estimate of its own.

The highway row is the one that bears on the objective. That campaign was driven after every modelling decision had been frozen, so nothing in the model was tuned on it, and it differs from the training data in both corridor and speed regime. It nonetheless reaches AUROC 0.927, with the highest lift and the lowest calibration error of the four. Adding it to the pooled dataset moved the headline AUROC by nothing: 0.933 before and 0.933 after. A fourth campaign that changes the headline result by zero is the strongest available evidence that the first three were not being over-fitted.


## 5.7 External validation on an independently collected dataset

The leave-one-campaign-out experiment still shares an operator, an instrument and an analyst. The second generalisation experiment removes all three by evaluating on a publicly released LTE drive-test dataset collected by a different group on a different network [33].

The transferred model reaches AUROC 0.752 on data it has never seen, against 0.745 for a model trained on that dataset itself. The two figures are close, and the appropriate reading is not that the transferred model is superior — the difference is within the range that resampling produces — but that what transfers is the formulation rather than the fit. A fitted model belongs to the network it was fitted on; a formulation and a feature construction do not, and it is the latter that this thesis offers.


## 5.8 Mechanism: the network triggers on its weakest signal

Objective O5 asks for the mechanism rather than the score, and the answer is uncomfortable for the deployed rule.

The quantity on which the network makes its decision is close to the least informative input available. Serving dwell time — how long the handset has been attached to its current cell — reaches AUROC 0.874 entirely on its own, while the serving-to-neighbour gap reaches 0.566, barely above chance for a single feature.

The signalling explains why. The A3 gap condition is satisfied on 27.1 % of all samples, and three in five of the measurement reports that follow are declined by the network. The gap is therefore a necessary condition that is very far from sufficient: satisfying it changes the probability of a handover far less than the literature's use of it as a feature would suggest.

The interpretation is a statement about the rule rather than about the model. The gap indicates that a handover is permitted; dwell time indicates that one is becoming due. A trigger defined on permission rather than on tendency will always fire late, which is the structural claim made in Section 1.1, now supported by measurement.


## 5.9 The A3 report-conversion rate

The first of the two network findings concerns what happens to a measurement report after it is sent. Table 5.9 reports the fraction of Event A3 reports that are not followed by a handover command within two seconds.

Two qualifiers travel with this number wherever it is quoted, and both are stated here because omitting either changes the figure materially. The measurement counts Event A3 reports only; taken over all measurement report types together the decline rate is 68.7 %. And it uses a two-second conversion window; a different window produces a different number. Both qualifiers are computable only after the configuration-timeline correction of Section 3.3, without which report type cannot be determined reliably.

The finding itself is that a measurement report is not a handover decision. Nearly two thirds of the A3 reports this network receives are declined, and the decline rate rises with cell size. Any model that treats an A3 report as a proxy label for a handover is therefore training on a label that is wrong most of the time.


## 5.10 Ping-pong: definitional instability and its actual source

The second network finding concerns ping-pong, and it has two parts: how much the reported rate depends on unstated definitional choices, and where the phenomenon actually concentrates.

The rate moves by more than sixteen percentage points without a single change to the underlying measurement. This is the quantitative form of the observation in Section 2.4, and it is the reason this thesis quotes the strictest of the four and states all three choices alongside it. It also explains how Amirova et al. [15] arrive at 0.13 % on comparable data: dividing by measurement records rather than by handovers changes the denominator by two orders of magnitude.

The window length is a fourth choice, and Figure 5.18 reports the full grid rather than the single row of Table 5.10. Across three window lengths and four identity-and-return conventions the same 938 handovers yield twelve defensible ping-pong rates between 19.5 % and 38.5 %. No cell in that grid is wrong; what is wrong is publishing one of them without saying which.

Two results follow. Ping-pong is concentrated almost entirely in intra-carrier handovers, at 31.0 % against 6.5 % across carriers, a factor of nearly five. And it is not driven by speed, which is the intuitive explanation: the highway campaign, at three times the urban mean speed, returns at 31.1 %, marginally above the pooled rate. The lever available to an operator is therefore the time-to-trigger of the dominant configuration profile rather than any speed-dependent adaptation. This thesis stops short of claiming a causal effect for such a change, for the reason given in Section 5.13.

Modelling the arrival stream as a self-exciting process supports the same conclusion from a different direction. The fitted Hawkes branching ratio is 0.605 with a 95 % interval of [0.524, 0.673], so each handover triggers on average approximately 0.6 further handovers; per campaign the value runs 0.649, 0.609, 0.567 and 0.513, lowest on the highway. The Ogata residual test of Section 4.11 rejects the exponential kernel (D = 0.074, p = 7 × 10⁻⁴), which is reported rather than suppressed: the clustering is real, but its temporal shape is not the exponential decay that the standard Hawkes kernel assumes.


## 5.11 Negative results

Four approaches were implemented in good faith, measured, and did not help. They are reported because a claim that the formulation and the protocol are what matter is credible only if the alternatives were actually tried.

The dedicated ping-pong classifier is the most informative of the four. Ping-pong is highly structured at the population level, as Section 5.10 shows, and yet it is not predictable at the level of the individual handover from these inputs: whether a particular transfer will be reversed appears to depend on the state of the target cell, which the handset does not observe.

The domain-adaptation null is consistent with published benchmarking rather than indicative of a faulty implementation. Ismail Fawaz et al. [25] benchmark nine unsupervised domain-adaptation algorithms over twelve time-series datasets and find several published methods performing worse than source-only training, with the adaptation technique rather than the backbone driving the outcome; the result here has the same shape.

One further ablation deserves its own figure, because its result is easy to state backwards. Figure 5.23 shows that adding the thirteen signalling features to the radio, mobility and history block changes the one-second AUPRC by nothing at all — 0.811 against 0.811 — while signalling features on their own still reach 0.370, roughly five times the prevalence floor. The signalling block therefore carries genuine information about imminence; the radio features simply carry it already.

Finally, removing the signalling leakage guard of Section 4.6 raises the apparent score substantially, which is the expected behaviour of a leak and is the reason the guard exists. That configuration is not reported as a result anywhere in this thesis.


## 5.12 Discussion against the objectives

Objective O1 is met: the next handover is predicted one second ahead at AUROC 0.933 and AUPRC 0.784, 11.7× the prevalence floor, from quantities a handset already observes, against AUROC 0.653 for the rule presently deployed.

Objective O2 is met, and the answer is larger than anticipated. Grouped evaluation is worth between 4 % and 74 % depending on architecture, and because the dependence is on architecture, the protocol determines which model appears to win rather than merely how well every model appears to do.

Objective O3 is met on both its parts. Coherence is exact by construction, against 43.6 % violations for the obvious alternative, and the guarantee is reported together with the alarm rate it costs and the feasibility floor set by the number of calibration drives.

Objective O4 is met at two distances: AUROC 0.927 on a corridor and speed regime frozen out of every modelling decision, and AUROC 0.752 on an independently collected public dataset against 0.745 for a model trained on it directly.

Objective O5 is met, and produced the most interpretable finding in the thesis: the quantity the network thresholds on is nearly the weakest predictor available, while the strongest is a quantity the rule does not use at all.


## 5.13 Threats to validity

Four threats bear on the results above and are stated here rather than deferred.

Scale and coverage. The evidence is 57 drives on one operator over four days. The cross-regime transfer of Section 5.6 rests on a single configuration pair, because the deployed configuration is identical across all four campaigns. A second operator would test what a second corridor cannot.

Instrument ceiling. The one-hertz export caps event-level detection at 90.5 %. This does not affect the row-level results, which are defined on the grid itself, but it bounds every event-level figure reported in Section 5.1.

Causal identification. No causal claim is made about the benefit of acting on a warning, and this is a matter of identification rather than of effort. The logging policy is deterministic: given the radio state and the configuration, Event A3 either fires or it does not, so the propensity of the observed action is zero or one and the inverse-propensity weights required for off-policy evaluation are undefined. Only a counting upper bound on benefit is therefore reported, and it peaks at a five-percent alarm budget and turns negative by forty. Section 7.3 identifies the design that would make the causal question answerable on data already held.

Comparator availability. The nearest comparator method available on this network — a reinforcement-learning formulation of the handover decision developed on the same operator and instrument — was reimplemented from its method description and scored as a predictor on this data, where it proved close to uninformative. That comparison is not reported as a headline result here, because at the time of writing no publication record for the comparator could be located and a comparison against a reference a reader cannot retrieve is of limited value. The dataset released by the same authors is, however, published under a citable identifier and is the external validation set used in Section 5.7.

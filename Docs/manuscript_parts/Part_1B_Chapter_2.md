# PART 1B: CHAPTER 2 (LITERATURE REVIEW AND METHODOLOGY)


# CHAPTER 2: LITERATURE REVIEW AND METHODOLOGY

Four bodies of work bear on the problem stated in Chapter 1, and they nearly meet without quite touching. The cellular measurement literature establishes what handovers look like in deployed networks but does not build predictors. The handover-prediction literature builds predictors, but predominantly on simulated data and predominantly without an evaluation protocol that would survive scrutiny. The survival-analysis and point-process literatures supply exactly the right mathematical objects — a discrete-time hazard and a self-exciting process validated by time rescaling — but have not been directed at mobility data. The distribution-free uncertainty literature supplies guarantees, but for signal-processing tasks whose exchangeability structure differs from that of an event stream recorded along a drive.

This chapter reviews each in turn, then presents a quantitative audit of the 22 most comparable prediction models, states the research gap that the audit establishes, and describes the methodology adopted in response, including the alternatives that were considered and rejected.


## 2.1 LTE mobility and the Event A3 trigger

The mobility procedure in E-UTRAN is specified in 3GPP TS 36.331 [1] and described at system level in TS 36.300 [2]. The network configures the UE with measurement objects, report configurations and measurement identities that bind the two; the UE evaluates the configured entry condition against its filtered measurements and transmits a MeasurementReport when the condition has held for the configured time-to-trigger.

For intra-frequency mobility the governing condition is Event A3. Writing Mn for the measured neighbour quantity, Ms for the serving quantity, Off for the configured offset, Ocn and Ocs for cell-individual offsets and Hys for hysteresis, the entry condition of TS 36.331 is

M_n + Ocn − Hys  >  M_s + Ocs + Off	(2.1)

and the condition must remain satisfied throughout the time-to-trigger interval before the report is sent. The decision to hand over is then taken by the network, not the UE, and is communicated by an RRCConnectionReconfiguration message carrying mobilityControlInfo.

Three consequences follow, and all three are used later in this thesis. First, the report is evidence that the network may hand over, not that it will; the conversion rate from report to command is an empirical quantity and is measured in Chapter 5. Second, the parameters Off, Hys and the TTT are operator-configured and are not observable without decoding the signalling; the prediction literature that assumes textbook values is therefore assuming something it has not checked. Third, because the condition is defined on a state that must already obtain and must then persist, the earliest instant at which Event A3 can produce any output is strictly after the radio environment has changed.


## 2.2 The measurement literature

A mature line of work in the networking-measurement community recovers operator mobility configurations from control-plane traces on live networks. Deng et al. [3] present the LTE precedent, a measurement study of operational 4G mobility configurations and their consequences. Ghoshal et al. [4] perform the equivalent analysis at large scale on contemporary networks, extracting hysteresis, threshold, offset, time-to-trigger and trigger quantity for events A1–A6, B1 and B2 per operator and band, over more than 15,000 km of driving and 48,426 handovers on three operators. Hassan et al. [5] establish the use of commercial diagnostic tooling for RRC extraction as accepted methodology, and Liu et al. [6] read mobilityControlInfo for mobility analysis without recovering the numerical parameters.

This literature is directly relevant in two ways. Methodologically, it legitimises the decoding pipeline used in Chapter 3 rather than competing with it: the extraction of deployed A3 parameters from measConfig is established practice, and this thesis does not claim it as a contribution. Substantively, it supplies the comparison points against which the configuration measured here is interpreted; Ghoshal et al. report positive A3 offsets of +6 to +10 dB and shortest time-to-trigger values of 256 to 640 ms on the operators they study, whereas the network measured here runs offsets from −15 dB to +5 dB and a shortest time-to-trigger of 160 ms.

What this literature does not do is predict. Ghoshal et al. state explicitly that they perform no machine-learned prediction, no off-policy evaluation and no counterfactual analysis; the work is descriptive by design. The ping-pong rates these studies report are likewise descriptive, and, as Section 2.4 discusses, are reported under definitions that differ enough to change the number by a factor of two.


## 2.3 The prediction literature and a protocol audit

A large body of work predicts handover, radio-link failure or next-cell occupancy using learned models. Recent systematic reviews characterise it unfavourably from the outside. Ankome and Hanada [7] screened 429 records under a PRISMA protocol, retained 336 after deduplication and included 49 studies spanning 2010–2025; they were unable to perform a meta-analysis because simulators and outcome definitions were too heterogeneous, they observe that most studies report percentage improvements over baselines of their own choosing rather than absolute performance, and they report that data splitting, class imbalance and calibration receive minimal explicit discussion anywhere in the included set. Saoud et al. [8] find that the field lacks quantitative cross-comparison between strategies, and Chabira et al. [9] enumerate the metric vocabulary actually in use — handover failure rate, latency, quality of service, energy — in which neither calibration nor any prevalence-aware ranking metric appears.

To convert that general complaint into something specific enough to act on, 108 publications were screened for this thesis and the 22 that present a learned or analytical model predicting handover, radio-link failure or next-cell occupancy were audited on protocol quality rather than on headline performance. Table 2.1 reports the audit.

Two observations from the audit are load-bearing for the remainder of this thesis.

The first concerns metrics. Seven of the 22 report accuracy on tasks whose positive prevalence lies between 0.86 % and 11 %, at which a constant negative prediction scores between 89 % and 99 %; three of the headline figures so reported are 98.03 %, 99.84 % and 94.83 %. A related failure appears in a railway radio-link-failure study that reports area under the ROC curve above 0.95 for all six architectures it compares, on a task with approximately one positive per five hundred samples, and consequently separates none of them.

The second concerns splitting, and the exceptions are named rather than rounded away. Five of the 22 do split on something coarser than a random row: by spatial zone, by device, by time under a rolling-origin protocol on operator data, by travel day [10], and by deployment event [11]. None of the five, however, holds out the mobility unit for a per-timestep classification task on measured radio; the two most recent additions are regression tasks in which prevalence does not arise, and the strongest protocol in the set addresses next-day cell-level radio-link failure rather than a per-sample mobility forecast.

A structural feature of this literature explains the pattern. Protocol quality and measurement quality are anti-correlated within it. The studies with the cleanest splits operate on ray-traced or SUMO-simulated trajectories [10], on aggregated operator key performance indicators, or at cell-and-day granularity [11]; the studies carrying real per-sample drive-test radio, whose data most resembles that used here, are precisely those whose split protocol is unstated. Recent graph-based models illustrate both halves: TH-GCN [12] builds a dynamic UE–cell graph for dense vehicular scenarios but is simulated, states no split protocol and reports relative deltas against baselines of its own choosing, while GRIMCELL [11] applies graph learning to radio-planning, configuration-management and performance-management data from a commercial LTE-A Pro network across 55 real deployment events, but predicts post-deployment key performance indicators per cell per day and is therefore a planning tool rather than a per-second warning system. Graser et al. [13] organise the trajectory-learning literature by data density and observe that the dense individual-trace regime, in which one-hertz drive data sits, is where the literature is thinnest for event prediction as opposed to location prediction.

The narrow claim that the audit supports, and the one made in this thesis, is therefore the following: of twenty-two audited models, ten state no split protocol at all, five split on a unit coarser than a row, and none holds out the mobility unit for a per-timestep classification task on measured radio data; none reports calibration; and none reports how early its warnings arrive.


## 2.4 Ping-pong and its definitional instability

Handover ping-pong — a return to a recently vacated cell — is widely reported and inconsistently defined. There is no standardised definition in 3GPP; what exists is a cell return within an author-chosen window, and the window alone moves the reported rate substantially. Zidic et al. [14] report ping-pong measurements on real 4G networks, and Ghoshal et al. [4] report per-operator rates of 15 % to 25 % under a fifteen-second window with a per-handover denominator.

Three choices determine the number, and papers rarely state all three: whether a cell is identified by physical cell identity alone or by physical cell identity together with carrier; whether any return within the window counts or only a return to the immediately preceding cell; and whether the denominator is the set of raw handover events or of quality-controlled ones. The consequences are severe enough to invalidate cross-paper comparison: Amirova et al. [15] report a ping-pong rate of 0.13 % because they divide by measurement records rather than by handovers. Chapter 5 reports the full ladder of these choices on a single fixed set of 938 handovers, where the rate moves from 24.5 % to 41.3 % without any change in the underlying data.


## 2.5 Survival analysis as the appropriate formulation

The task posed in Section 1.3 — the probability that an event occurs within h seconds, for several values of h — is a time-to-event problem, and the appropriate formulation is therefore a survival model rather than a set of independent classifiers. Wiegrebe et al. [16] review 61 deep time-to-event methods and place the discrete-time route, in which the time axis is binned and binary indicators per interval are trained as classification, firmly in the mainstream. Thorsen-Meyer et al. [17] construct structurally the same object for intensive-care outcome prediction, with a censoring-aware log-likelihood over discretised windows.

This literature is used here without any claim of novelty attaching to the formulation itself, and stating that plainly removes an obvious reviewer objection. What is new is where the formulation is pointed: no model in the 22-paper audit of Section 2.3 poses handover prediction this way, and every one of them therefore inherits the incoherence described in Section 4.2.

One departure from the survival literature is deliberate. That literature evaluates predominantly with the concordance index and the integrated Brier score, both of which aggregate over the horizon axis. An operator, however, acts at a single horizon. A model that ranks well on average while asserting that the probability of a handover within one second exceeds the probability within three seconds on 43.6 % of samples is not deployable whatever its concordance index. Chapter 4 therefore evaluates horizon-wise, reporting AUPRC at each horizon together with a coherence-violation rate.


## 2.6 Distribution-free uncertainty quantification

Conformal prediction supplies finite-sample, distribution-free guarantees under an exchangeability assumption, and it has already been applied inside wireless communications by a strong group. Cohen, Park, Simeone and Shamai [18] apply split and cross-validation conformal prediction to demodulation, modulation classification and channel prediction; Simeone, Park and Zecchin [19] generalise the approach into a deployment lifecycle covering pre-deployment calibration and hyperparameter selection, monitoring under distribution shift, and post-deployment counterfactual analysis. Conformal risk control, which extends the guarantee from coverage of a prediction set to the expectation of a bounded monotone risk, is due to Angelopoulos et al. [20].

The claim made in this thesis is consequently narrower than it might appear, and the narrowing is deliberate. The guarantees in [18] and [19] are over prediction sets, for tasks that are independent and identically distributed within a frame. The guarantee developed in Chapter 4 is over a risk — an operator key performance indicator, the per-drive miss rate — on a stream that is exchangeable only at the level of a whole drive. The identification and defence of that exchangeability unit is the contribution; the campaign-design floor that follows from it is its consequence; and no wireless conformal study located in three screening passes reports a mobility-management case at all.


## 2.7 Point processes and the self-excitation of handover arrivals

Handover events do not arrive independently. The self-exciting point process introduced by Hawkes [21] is the standard model for arrival streams in which each event raises the intensity of subsequent events, and Laub et al. [22] provide the contemporary reference treatment, including the branching-ratio interpretation used in Chapter 5. Fitting such a process is not, by itself, evidence that the process is self-exciting; the fit must be checked. The residual analysis of Ogata [23], in which the time axis is rescaled by the fitted compensator and the transformed arrivals tested against a unit-rate Poisson process, is the standard check, and Price-Williams and Heard [24] establish the precedent for its use in a networking context, validating a self-exciting fit to campus and laboratory network traffic by time rescaling with Kolmogorov–Smirnov tests on held-out data. Chapter 5 follows that precedent and reports the test outcome, including where it rejects the fitted kernel.


## 2.8 Evaluation practice imported from adjacent fields

Two further results from adjacent literatures inform the evaluation design and are cited here because they make the negative results of Chapter 5 interpretable rather than embarrassing. Ismail Fawaz et al. [25] benchmark nine unsupervised domain-adaptation algorithms across twelve time-series datasets and find that several published methods perform worse than source-only training with no adaptation at all, and that the adaptation technique rather than the backbone drives the outcome; the null result reported for Deep CORAL [26] in Chapter 5 is therefore consistent with a published benchmark rather than evidence of faulty implementation. Shi et al. [27] supply the shift taxonomy that names the shift encountered here as a device-and-day shift rather than a sensor-modality shift. Wagner et al. [28] show formally that the commonly used point-adjusted metrics for time-series event detection each satisfy only a subset of the desirable properties and that none satisfies all of them, which is the justification for reporting event-level detection rate, lead time and false alarms per hour alongside row-level AUPRC rather than in place of it.

Finally, the standards track bears on the choice of horizon. Deb et al. [29] model conditional handover as a discrete-time Markov chain over preparation and execution offsets and timers, and their analysis makes explicit that conditional handover consumes a lead time rather than a label: a model that identifies the correct target cell two hundred milliseconds before the event buys nothing, because the preparation message must be sent, acknowledged and stored. This is the analytical justification for reporting a lead-time distribution rather than a detection rate alone, and for retaining horizons of two, three and five seconds even though the deployed trigger fires within a few hundred milliseconds.


## 2.9 Research gap

Collecting the preceding sections, the gap this thesis occupies can be stated precisely. Measurement-grade ground truth exists, but is not joined to prediction. Prediction models exist, but not under an evaluation protocol that holds out the mobility unit, and not with calibrated outputs or event-level costs. The correct formulation exists in the survival literature, but has not been applied to mobility events. Distribution-free guarantees exist in wireless, but for a different exchangeability structure and not for any mobility-management task.

This work sits in that gap: measurement-grade ground truth obtained from decoded signalling, a borrowed formulation made coherent across horizons, a conformal risk bound whose exchangeability unit is stated and defended, and an evaluation protocol designed to be acceptable to a reviewer from the machine-learning community rather than only to one from the wireless community.


## 2.10 Methodology

The methodology adopted follows directly from the gap. It consists of five stages, illustrated in Figure 2.1, and each stage is developed in detail in Chapters 3 and 4.

Stage 1 — Collection. Four drive-test campaigns are conducted on a live commercial LTE network using an instrumented handset, recording a one-hertz radio measurement export and, in parallel, a decoded RRC signalling log.

Stage 2 — Ground truth and configuration recovery. Handover instants are taken from decoded RRCConnectionReconfiguration messages carrying mobilityControlInfo. Because measurement identifiers are scoped to the message that carries them, a configuration timeline is replayed so that every measurement report resolves against the configuration in force at its own timestamp.

Stage 3 — Feature construction. One hundred and fifty-two candidate features are constructed from radio, mobility, history and signalling sources; all are strictly causal, closing at the prediction instant, and none crosses a drive boundary.

Stage 4 — Formulation and modelling. The task is posed as discrete-time survival. A single model estimates the per-interval hazard and horizon probabilities are recovered by the product-limit identity, which guarantees ordering. Seven learners are compared under identical conditions.

Stage 5 — Evaluation and risk control. Splits are grouped by whole drive under a four-fold rotation repeated over five seeds; confidence intervals are bootstrapped over drives; and a warning threshold is certified by conformal risk control whose exchangeable unit is the drive.


### 2.10.1 Approaches considered and rejected

Four alternatives were considered seriously and rejected, and the reasons are recorded here because they constitute part of the methodological argument.

Independent per-horizon classifiers. The obvious approach — one binary classifier per look-ahead time — was implemented and retained as a control arm rather than as the primary method. It is rejected as the primary method because it produces mutually contradictory outputs on a large fraction of samples, as Chapter 5 quantifies, and because repairing that defect after the fact costs both a held-out split and predictive performance.

Random-row cross-validation. The splitting protocol used by the majority of the comparator literature was implemented solely to measure what it is worth. It is rejected because adjacent one-second samples within a drive are near-duplicates, so a random split places nearly identical rows on both sides of it; Chapter 5 shows that the resulting inflation is architecture-dependent and therefore alters the ranking of models.

Class reweighting for imbalance. The standard reflex on a rare-event task is to reweight the positive class. It is rejected in the hazard arm for a reason specific to the formulation: reweighting transforms the fitted probability monotonically, which leaves ranking metrics unchanged but destroys the probability scale, and the product-limit identity multiplies K such probabilities together, so a per-interval multiplicative error compounds with the horizon. Both arms are therefore fitted unweighted, which also keeps the comparison between them fair.

Reinforcement learning of the handover decision. A decision-theoretic formulation, in which an agent learns when to hand over, was considered and is the formulation adopted by the nearest comparator study available on this network. It is rejected here because it answers a different question: it optimises a decision the network is entitled to make at its own pace, whereas this thesis forecasts an event. Chapter 5 reports a reimplementation of that comparator scored as a predictor, for completeness.

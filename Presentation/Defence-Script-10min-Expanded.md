:::center
{title}Final Thesis Defence Script — Expanded
{sub}Predicting the Next LTE Handover from Drive-Test Signalling
{small}Combined by related slides · simplified spoken language · results- and novelty-focused
:::

| | |
|---|---|
| **Full script** | ≈ 2,480 spoken words — **about 17 minutes** at the same pace the 10-minute version assumed |
| **Trimmed** | ≈ 1,970 words — **about 14 minutes** — drop the ten paragraphs marked *(cut)* |
| **Delivery** | Change slides while continuing the same section — the section, not the slide, is the unit of speech |
| **Note** | This is the detailed version. If the slot is strictly 10 minutes, give the original short script and hold this one as the answer bank. |

## Novelty to emphasize during the defence

- Real RRC signalling-confirmed handover ground truth, with the active configuration reconstructed over time.
- A single hazard formulation that gives coherent multi-horizon probabilities instead of five independent classifiers.
- Direct measurement of architecture-dependent leakage: random splitting inflates GRU performance by 74%.
- Validation beyond normal cross-validation: a fully unseen highway capture plus an independent public dataset.
- A calibrated risk threshold that makes the warning / false-alarm trade-off explicit, and states its price.

---

## Slides 1–2 — Title and Outline

**Main takeaway:** Set up the central question and tell the panel what to remember.

Assalamualaikum. Respected chairman, respected members of the board — thank you for your time. Our thesis is about predicting the next LTE handover from real drive-test signalling.

The question is simple to state. Today the network moves your phone from one cell to the next by *reacting* to a condition. We ask whether that handover can be seen coming **before** the rule reacts, how far ahead, and how much the network can trust the warning.

I will cover why the problem matters, what we built, what the results show, and what is genuinely new — with most of the time on the last two.

---

## Slides 3–6 — Background, Motivation, Literature and Objectives

**Main takeaway:** A3 is reactive by construction; the literature has either real measurements or prediction models, but rarely both under a rigorous protocol.

LTE handover mainly follows Event A3. A neighbour cell must become better than the serving cell by a configured offset, and must *stay* better for the whole time-to-trigger, before the phone even sends a report. On the network we measured, those offsets run from minus fifteen to plus five decibels, with time-to-trigger between 160 and 1024 milliseconds.

The important word is *become*. The rule cannot fire until the radio has already changed. A3 is reactive by construction — not a flaw, but what the standard was designed to do.

In our data that lag is measurable and expensive: **938 signalling-confirmed handovers in 2.9 hours**, one every eleven seconds. About a quarter returned to the cell just left within fifteen seconds, and the link had to be re-established 341 times. One second of warning is enough for the network to prepare the target cell, or to suppress a handover that is only going to come straight back.

*(cut)* We screened 108 papers and reviewed 22 comparable models closely. The field splits into two literatures that do not meet. Measurement studies have excellent ground truth but build no predictor. Prediction studies build models, but of those 22, **none** holds out the mobility unit — a whole drive or device session — for a per-timestep task on measured radio, **none** reports calibration, and **none** reports a lead time or false-alarm rate.

That gap set five objectives, deliberately broader than a high score: predict at five look-ahead times from what a phone can observe; group the evaluation by drive; make the probabilities consistent, calibrated and bounded; test outside the training capture; and explain the mechanism rather than only report accuracy.

> **Say:** The novelty starts with that combination. I am not claiming LightGBM, survival analysis or conformal prediction are new — they are standard. What is new is putting signalling-confirmed truth, leakage-safe multi-horizon prediction, calibrated risk and real generalisation into one framework, and reporting the price of each.

---

## Slides 7–12 — Methodology and Proposed System

**Main takeaway:** Exact signalling ground truth, strictly backward-looking features, and a time-to-event formulation that keeps the five answers consistent.

The workflow has five stages: collect real drive-test data, label the exact handover from RRC signalling, build features that look only into the past, train on some drives and test on different drives, and evaluate both prediction quality and operating cost.

**Ground truth.** Our label is not a vendor counter. It is the actual RRC Connection Reconfiguration carrying mobility control information — the handover command itself, millisecond-timestamped. We also rebuild a *configuration timeline*, because the measurement configuration arrives in pieces and its identifiers are scoped to the message carrying them; read one against the wrong moment and the report resolves against the wrong configuration. Doing this properly showed the deployed offsets on this network are **negative**, not the plus three decibels earlier published work assumed.

**Features.** We build 152 columns and 107 survive a degenerate-feature filter: 83 radio features — rolling means, standard deviations, ranges and differences over three, five and ten second windows, plus neighbour gaps — 17 mobility features from GPS, 7 history features, and 13 from the signalling. Every window looks only backwards, closes at the current second, and never crosses a drive boundary.

**The modelling idea.** Rather than five separate classifiers, we treat handover as a time-to-event problem. The reason is concrete: five independent classifiers can return a higher probability within one second than within three, which is impossible. We train **one** model for the next second only — the hazard — and multiply those one-second risks along the time axis. Because the answer is built as a product, it can only rise as the look-ahead grows. The ordering is guaranteed by construction, not by post-processing.

*(cut)* Seven learners are then compared under identical folds, seeds and formulation: LightGBM, logistic regression, an MLP, a temporal convolutional network, a Transformer, a GRU, and the network's own A3 rule scored as a predictor. The goal was never the most complicated model — it was the most trustworthy comparison.

---

## Slides 13–16 — Data and Experimental Design

**Main takeaway:** The entire experimental design is built around whole drives, not randomly mixed samples.

Four campaigns in Dhaka and Gazipur, one operator, an XCAL-equipped handset: **57 drives, about 95 kilometres, 10,260 samples at one per second, 938 signalling-confirmed handovers**. Three are urban — an arterial road, an urban loop, a dense urban area — and the fourth is the Uttara–Gazipur highway at about fifty kilometres an hour.

Two things before anyone asks. The raw logs contain 957 handovers; 938 is the number inside a drive that passes quality control, and every model is scored against those 938. And the A3 configuration is identical across all four campaigns — so the highway result later is a test of a new road and speed regime, not of a different configuration.

**The split.** The whole drive is the unit, and never appears on both sides. We rotate over four folds so every drive is tested exactly once, repeat with five seeds to get twenty paired observations per comparison, and bootstrap every confidence interval over drives, not samples.

*(cut)* Why five seeds? With four folds alone, a paired test can never push its p-value below 0.125 however large the effect — the test would be reporting its own limit rather than the data.

**Why accuracy is the wrong metric.** At one second only 6.7 percent of samples are positive; at half a second, 3.7 percent. A model that always says "no handover" already scores 93.3 percent accuracy and is useless. So we report AUROC, precision-recall read against its own prevalence floor, calibration error, and event-level behaviour — how many handovers we catch, how many false alarms per hour, and how much warning we actually deliver.

---

## Slides 17–20 — Engineering Scope and Impact

**Main takeaway:** Move briskly; stress the engineering trade-off and the honest limit on the claim.

These slides map the work onto the knowledge profile, the complex engineering problem attributes and the complex engineering activities: LTE protocol knowledge to decode the signalling, radio propagation to build meaningful features, statistics for the formulation and the guarantee, drive-test practice to collect the data, and software engineering to hold the pipeline together.

The central trade-off is impossible to escape: an earlier warning is more useful and also less certain. Every decision here sits somewhere on that curve, and our position is that the **curve** should be reported, not one flattering point on it.

On impact we keep the claim narrow. The plausible benefit is better connection continuity and fewer unnecessary handovers and signalling messages — and "about a quarter return within fifteen seconds" is measured, not assumed. But to be explicit: this study measures prediction and network behaviour. **We do not claim a deployed energy saving, and we make no health claim at all** — there were no human subjects and no exposure experiments.

> **Say:** So the innovation is not a new mathematical tool. It is how established tools are combined for a real network problem, under a protocol someone else can check.

---

## Slide 21 — Main Prediction Result

**Main takeaway:** Pause here. This is the headline. Slow down and let it sit.

One second before a handover, LightGBM reaches **AUROC 0.933** and **AUPRC 0.784**, with a bootstrap interval of 0.740 to 0.826. Because only 6.7 percent of samples contain a handover, that precision-recall score is **11.7 times the random baseline**. Calibration error at that point is 0.024.

The network's own A3 rule, scored on exactly the same data as a predictor, reaches AUROC 0.653 and catches 5.5 percent of handovers one second ahead.

*(cut)* The ordering of the seven models is itself a finding. LightGBM leads at every look-ahead time and **logistic regression is second** — ahead of the GRU, the Transformer, the TCN and the MLP. On 57 drives there is not enough data for a sequence model to learn what the engineered features already carry.

*(cut)* At the event level rather than the sample level, we detect 44.7 percent of handovers one second out and 65.1 percent at five, against a ceiling of 90.5 percent imposed by the one-hertz export — a property of the equipment, not of the model.

---

## Slides 22–24 — Leakage, Coherence and the Risk Guarantee

**Main takeaway:** The strongest methodological novelty slides. Do not rush them.

**First, evaluation leakage is architecture-dependent.** Splitting randomly by sample instead of by drive inflates the GRU by **74 percent** and logistic regression by only **4 percent**. Samples one second apart are nearly identical, so a random split puts almost the same row on both sides, and the more temporal memory an architecture has the more it profits. The consequence is sharper than "scores go up": a careless split **reorders the leaderboard**, and can make a deep model look like the winner when it is not.

**Second, coherence.** Five independent classifiers contradict themselves on **43.6 percent** of samples — saying a handover is likelier within one second than within three. Our hazard model has **zero** such contradictions by construction, and beats an uncalibrated baseline on calibration at every look-ahead time, p below 0.0001 over twenty paired folds.

*(cut)* To be fair to the alternative: a baseline with per-horizon isotonic calibration can beat us on calibration error alone. But it spends a held-out split, costs two to five AUPRC points, and makes coherence *worse* — 48.7 percent violations. We report it rather than hide it.

**Third, the alarm threshold is not chosen by hand.** We certify it on 28 held-out calibration drives using conformal risk control, so the expected per-drive miss rate on future drives stays below a target the operator picks. At a 20 percent target, the system alarms on 23 percent of samples and misses 12.6 percent of handovers. Demand 5 percent and the alarm rate climbs to **61 percent** — a guarantee nobody would deploy.

*(cut)* The number of calibration drives is itself the binding constraint: with 28 drives the tightest target we can even express is about 3.4 percent. That turns the guarantee into a campaign-design rule — a tighter promise requires more driving.

> **Say:** This is why the contribution is more than a high AUROC. The work also shows how the model must be tested, how its probabilities should behave, and exactly what the warning costs.

---

## Slides 25–26 — Generalisation

**Main takeaway:** Emphasize that the highway was collected *after* every modelling decision was frozen.

Holding out each campaign completely — training on three, testing on the fourth — AUROC stays between **0.909 and 0.949**. The highway matters most, because it was collected after all modelling decisions were already fixed; nothing was tuned on it. On that new corridor at higher speed the model still scores **0.927**, with the *lowest* calibration error of the four, and adding it did not move the pooled 0.933 at all.

We also test outside our own data entirely, on a public drive-test dataset collected by another team. Our transferred model reaches **0.752 AUROC**; a model trained directly on that dataset reaches 0.745.

> **Say:** So the second half of the novelty is the validation design: whole-drive testing, a genuinely unseen highway capture, and an independent external dataset. Any one alone would be arguable — together they are hard to explain away as memorisation.

---

## Slides 27–30 — Why It Works, and What We Found About the Network

**Main takeaway:** The mechanism — dwell time beats the A3 gap — plus two findings the literature has not modelled.

The discussion explains why prediction is possible, and the answer is slightly uncomfortable for the standard. The best single feature is **how long the phone has already stayed on the current cell** — serving dwell time — at AUROC **0.874** on its own. The A3 serving-to-neighbour gap, the quantity the network actually thresholds on, reaches only **0.566**. In plain terms: the gap says a handover is *allowed*; dwell time says one is *becoming due*.

The signalling supports this. The gap condition holds on 27 percent of samples, and **62.9 percent of A3 reports are not followed by a handover within two seconds**. An A3 report is not a handover decision — three in five are declined.

*(cut)* Two qualifiers on that number, because they change it: it is A3 reports only — all report types convert at 68.7 percent — and it uses a two-second window. Only about half of measurement reports are A3 to begin with.

**Ping-pong is concentrated, not general.** Same-carrier handovers return at **31.0 percent** against **6.5 percent** across carriers. And it is not speed — the highway still returns at 31.1 percent. The dominant configuration, plus one decibel with a 320 millisecond time-to-trigger, carries 72 percent of all handovers and returns at 29.2 percent. That makes time-to-trigger the practical parameter worth testing, though we do not claim a causal effect yet.

*(cut)* The ping-pong rate also depends on three definition choices papers usually leave unstated: whether a cell is identified by PCI alone or PCI plus carrier, whether any return counts or only a return to the previous cell, and whether you count raw or quality-controlled events. On the *same* 938 handovers those choices move the answer from 24.5 percent to 41.3 percent. We quote 24.5 and state all three.

**Negative results.** Extra neighbour data, additional clustering features, a dedicated ping-pong model that came out at chance, and two domain-adaptation methods all failed to help. Reporting them strengthens the main conclusion: formulation, configuration and correct evaluation mattered more than added complexity.

---

## Slides 31–33 — Conclusion, Novelty and Future Work

**Main takeaway:** Repeat the four results, then state the novelty boundary yourself before anyone else does.

Four findings matter most.

**First**, the next LTE handover can be predicted about one second ahead at AUROC 0.933 and AUPRC 0.784 — nearly twelve times the random baseline — from what an ordinary handset already observes.

**Second**, one hazard model gives consistent multi-horizon probabilities with zero time-order contradictions, where five separate classifiers contradict themselves on 43.6 percent of samples.

**Third**, the evaluation is itself part of the contribution: random splitting inflates a GRU by 74 percent and logistic regression by 4 percent, so a careless protocol does not merely raise scores — it changes which model appears to win.

**Fourth**, the result generalises — AUROC 0.927 on a highway collected after every modelling choice was frozen, and 0.752 on an independent public dataset.

> **Say:** So the main novelty is not a new machine-learning algorithm. It is a complete, signalling-grounded framework combining real handover truth, leakage-safe evaluation, coherent multi-horizon probabilities, calibrated risk control and strong real-world validation in one study — with the cost of each reported.

And the boundary, stated by us rather than found by the board: 57 drives, one operator, four days, a one-hertz export. This is an offline predictor, not a deployed controller. We make **no causal claim** about network benefit, because the logging policy is deterministic — A3 either fires or it does not — so off-policy evaluation is not identified on this data, and we report only a counting upper bound.

*(cut)* The next steps follow from that boundary: a fuzzy regression-discontinuity design at the A3 threshold, which makes the causal question identifiable on data we already hold; then a second corridor and operator; then linking the warning to a measured throughput or interruption improvement; and finally an experimental test of the time-to-trigger change the ping-pong analysis points to.

Thank you. I welcome your questions.

---

## Five lines to remember if time runs short

- A3 reacts to a condition; our model predicts the actual handover before that reaction can complete.
- At one second, the main model reaches AUROC 0.933 and AUPRC 0.784 — 11.7 times the prevalence floor.
- Random sample splitting inflates the GRU by 74% and logistic regression by 4%, so the protocol can change the apparent winner.
- The hazard formulation gives coherent multi-horizon probabilities with zero time-order contradictions, against 43.6% for separate classifiers.
- The model still scores AUROC 0.927 on a highway capture collected after all modelling choices were frozen.

**Final novelty sentence:**

> The novelty is not a new machine-learning algorithm; it is a signalling-grounded, leakage-safe and uncertainty-aware framework that turns real handover measurements into coherent predictions and validates them on unseen and external data.

---

## Cutting for time

Dropping the ten paragraphs marked *(cut)* takes the script from about 17 minutes to about 14. None of them carries a result another paragraph depends on. In order: the 22-model audit, the seven-learner list, the five-seeds justification, the model ordering, the event-level detection rates, the isotonic comparison, the calibration-drive floor, the A3-conversion qualifiers, the ping-pong definition ladder, and the future-work list.

Keep all ten in your head anyway — eight of them are the answers to the questions the board is most likely to ask, so they will probably be spoken in the Q&A even if not in the talk.

If the slot is a hard ten minutes, use the original short script and treat this document as the reserve behind it: same sections, same order, so you can always step up into the longer version of a paragraph when a question invites it.

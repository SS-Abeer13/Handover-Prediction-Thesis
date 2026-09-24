:::center
{title}Final Thesis Defence Script — Slide by Slide
{sub}Predicting the Next LTE Handover from Drive-Test Signalling
{small}Keyed to Handover-Thesis-Presentation.pptx · 33 slides · plain English · every sentence carries a figure
:::

| | |
|---|---|
| **What this is** | The full spoken script, in simple language. Short sentences. The numbers sit inside the sentences, so there is no table to read from. |
| **Length, full** | ≈ 4,200 words — **about 31 minutes**. Each slide’s time below is worked out from its own word count, so the numbers add up to a real clock. |
| **Pacing** | Every slide has its own time. If you are 2 minutes late by slide 21, take it out of slides 27 to 30, not out of 21 to 26. |
| **To reach 21 minutes** | **Drop the last paragraph of every slide** except 8, 17–19, 26, 31 and 33. Each of those last paragraphs is an extra point, never the main claim — so this removes about 1,370 words and no result. |
| **To reach 15 minutes** | Do the above, and give slides 5, 7, 8, 12, 13 and 26 as one sentence each, and 17–19 as one sentence for all three. |
| **Rule** | If a number leaves your head in the middle of a sentence, say the point without it and move on. Never guess a number in front of the board. |

---

## Slide 1 · Title — 35 s

Assalamualaikum. Respected chairman, respected members of the board, and my supervisor. This thesis is about predicting the next LTE handover from real drive-test data. We ran four measurement campaigns in Dhaka and Gazipur. That gave us 57 drives, about 95 kilometres of driving, 10,260 samples recorded once per second, and 938 handovers.

Those 938 handovers are not counted from a vendor tool. Each one is read from the network's own signalling message. And there is no simulation anywhere in this work.

## Slide 2 · Outline — 40 s

There are eleven sections. To respect your time, I will spend most of it on three of them: the proposed system in section five, the results in section nine, and the limits of what we claim in section ten.

Here is the headline, so you have it from the start. One second before a handover, our model reaches AUROC 0.933 and a precision-recall score of 0.784, against a handover rate of only 6.7 percent. That is 11.7 times better than random guessing, and the calibration error is 0.024.

---

## Slide 3 · Background — 80 s

*The word to stress is "already".*

The phone measures its own cell and its neighbours once every second. It sends a report when a rule called Event A3 is satisfied. A3 says: a neighbour must become better than the serving cell by a fixed offset, and it must stay better for a fixed waiting time. Only then does the phone send a report. Only then can the network decide.

On this network the offsets are minus fifteen, minus ten, minus six point five, plus one and plus five decibels. The waiting time runs from 160 to 1024 milliseconds. One setting does most of the work: the plus one decibel offset with a 320 millisecond wait carries 679 of our 938 handovers, which is 72 percent of them.

Here is the problem. The rule is written around a change that has already happened. So A3 can never fire early. It can only react. That is what the standard was built to do. Our question is whether the same measurements, read one second earlier, already show the handover coming.

## Slide 4 · Motivation — 65 s

The cost of reacting late shows up in our own data.

938 handovers in 2.9 hours is one handover every eleven seconds, with a middle gap of three and a half seconds. 24.5 percent of them go straight back to the cell they just left, within fifteen seconds. Those are wasted: the phone was moved, and then moved back.

The connection also broke and had to be set up again 341 times across the four campaigns. And out of 7,385 A3 reports the phone sent, 62.9 percent were never acted on within two seconds. So most of the reporting traffic that A3 creates does not turn into a handover at all.

One second of warning would be enough for the network to get the next cell ready, or to stop a handover that is only going to come back. That is the opportunity we are trying to measure.

## Slide 5 · Literature — 55 s

We screened 108 papers and studied 22 prediction models closely. The field splits into two groups, and they do not meet.

Measurement studies have exactly the ground truth we need, from real networks, but they only describe. They do not build a predictor. Prediction studies do build models, but mostly on simulated data. Of the 22 that use real radio data, not one of them keeps a whole drive out of training when predicting second by second. Not one reports calibration. Not one reports how much warning it gives, or how often it raises a false alarm.

Zero out of twenty-two on all three. So the published numbers are not wrong. There is simply no published result here that an operator could act on.

## Slide 6 · Objectives — 45 s

Five objectives, and each one has a number attached to it later in this talk.

O1: predict the handover at five look-ahead times — half a second, one, two, three and five seconds — using only what the phone can see. That is slide 21. O2: compare models under a test that cannot cheat. That is slide 22. O3: make the probabilities consistent with each other, honest in value, and backed by a guarantee. Slides 23 and 24. O4: test on a road the model has never seen. Slide 25. O5: explain why it works, not just how well. Slide 27.

---

## Slide 7 · Research methodology — 55 s

Five steps.

Collect: drive a measurement phone over real roads, recording radio values once per second and the full signalling at the same time. Label: read the handover out of that signalling, instead of guessing it. Build: 152 input columns, and every one of them looks only backwards. Test: train on some drives and test on completely different drives, four rotations, repeated with five random seeds. Evaluate: not just how good the prediction is, but what it costs to use — how many handovers we catch, how many false alarms per hour, and how much warning we give. The last step is where this work differs most: a good score alone does not tell an operator whether the warning is usable.

---

## Slide 8 · Proposed system, five stages — 55 s

Stage one is collection, once per second, with the signalling recorded alongside. Stage two is what makes everything else possible: the handover is the decoded RRC command itself, with a millisecond timestamp, not a counter we have to trust. Stage three uses only the past — 107 inputs, each window ending at the current second, and no window crossing from one drive into another. Stage four is the formulation that keeps the five look-ahead times agreeing with each other. Stage five is testing by whole drive, which is where this work differs from most published work. If any one of those stages is done loosely the final number means nothing, and slide 22 shows exactly how much a loose stage five is worth.

## Slide 9 · Where the ground truth comes from — 85 s

*Go slowly here. It sounds like a small detail and it is actually a contribution.*

A handover is a decoded RRC reconfiguration message carrying mobility control information: a clear command with a millisecond timestamp, not a counter we have to trust.

But the measurement settings do not arrive all at once. They arrive piece by piece, across many messages. The identity numbers inside them only mean something against the settings active at that moment, so the same number means different things at different times in one connection.

Our first parser missed this, and 99.4 percent of reports came out as A3 — including reports where there was no neighbour cell at all. That is impossible, because A3 is defined on a neighbour. That impossible number is what told us the parser was wrong.

The fix is to rebuild a timeline of the settings and resolve every report against whatever was active at that instant. Two things came out of it. Only 43 to 52 percent of reports are really A3, not 99 percent. And the offsets on this network are negative, not the plus three decibels assumed in earlier published work — so this network hands over more eagerly than the literature says.

## Slide 10 · What the model is given — 65 s

We build 152 columns and use 107, after dropping the ones that are empty or never change.

83 of them are radio: rolling averages, spreads, ranges and differences over 3, 5 and 10 second windows, plus the gap between the serving cell and each neighbour. 17 come from GPS: speed, change of heading, acceleration. 13 come from the signalling. And 7 are history features. One of those seven, how long the phone has been on the current cell, turns out to be the single most useful input in the whole set.

Everything looks backwards only, every window ends at the current second, and no window crosses a drive boundary. We also added guards so a report feature cannot carry information about the very handover it belongs to — without them the model can read the answer off its own input.

## Slide 11 · One model, not five — 75 s

*This equation is the heart of the thesis. Show it, then say what it buys us.*

The obvious approach fails. If you train five separate classifiers, one per look-ahead time, they can tell you the chance within one second is higher than the chance within three seconds. That cannot be true. Anything that happens within one second has also happened within three.

So we ask a different question at every step: given that the handover has not happened yet, does it happen in this next second? That is called the hazard. The chance of a handover within k seconds is then one minus the product of the surviving terms: one minus h-one, times one minus h-two, and so on up to h-k. Because it is a product of numbers between zero and one, it can only go up as k goes up.

So the order is correct automatically. One model, one fit, no extra correction step, no data held back for correction. On our data that is the difference between 43.6 percent of samples being self-contradictory and zero.

---

## Slide 12 · What was modelled and compared — 55 s

This is a time-to-event problem, and the hazard is what turns five answers into one answer.

Seven learners were compared, under the same folds, the same seeds and the same formulation. LightGBM and logistic regression stand for the table-based approach. The MLP, the temporal convolutional network, the Transformer and the GRU stand for four different ways of giving a model memory of the recent past. And Event A3 itself is scored as if it were a predictor, so the network's own rule sits on the same scale as everything else.

Every deep model got the same twenty-trial tuning budget, and none beat logistic regression even untuned. That is a statement about having 57 drives, not about deep models.

## Slide 13 · Where the data was collected — 40 s

Four campaigns in Dhaka and Gazipur, 57 drives, about 95 kilometres. Three urban routes — an arterial road, an urban loop and a dense urban area — and one highway run out to Gazipur, at an average speed of 49.5 kilometres an hour, roughly three times the urban speed.

The circles on this map are handovers. They gather at particular junctions instead of spreading evenly along the road — the first sign that the signal is partly about where you are, and the first reason why splitting the data randomly is dangerous.

## Slide 14 · Four measurement campaigns — 65 s

15 drives and 290 handovers in 46 minutes on the urban arterial. 8 drives and 174 handovers in 24 minutes on the urban loop. 20 drives and 297 handovers in 60 minutes in dense urban. And 14 drives with 177 handovers in 43 minutes on the highway.

A drive is a continuous stretch of at least 60 seconds. A whole drive is either used for training or for testing, never both.

Three things I would rather say now than be asked later. The raw logs hold 957 handovers; 938 fall inside a drive that passes our quality check, and 938 is what every model is scored on. The A3 settings are identical across all four campaigns, so a test across campaigns tests road and speed, not settings. And the highway was driven after every modelling decision was already fixed.

## Slide 15 · Every look-ahead time is a rare-event problem — 45 s

10,260 samples on an even one-second grid. The handover rate rises from 3.7 percent at half a second, to 6.7 at one second, 12.5 at two, 17.5 at three, and 25.9 at five.

At one second that means a model which always says "no handover" already scores 93.3 percent accuracy. That is why accuracy appears nowhere in this thesis. Every score is read against its own floor. So when the precision-recall score drops from 0.784 at one second to 0.627 at two seconds, the right way to read it is the lift: 11.7 times the floor at one second, against 5.0 times at two.

## Slide 16 · How the models were tested — 65 s

A whole drive is either trained on or tested on, never both. Four rotations, so every drive is tested exactly once. That means about 14 drives held out against 43 in training on each rotation.

We repeat those rotations with five random seeds, which gives twenty paired comparisons. The reason is practical, not cosmetic. With only four folds, a paired test can never give a p-value below 0.125, no matter how big the difference is. The test would be reporting its own limit instead of the data.

Confidence intervals resample whole drives, not samples, because samples inside one drive are not independent. And the scaler, the alarm threshold and the calibrator are fitted inside the training part only — fitting a scaler on the full dataset is itself a small leak, and it is one of the first things a reviewer checks.

---

## Slides 17, 18, 19 · Knowledge profile, complex problem, complex activities — 15 s each

*Name one row from each and move on. Do not read the tables aloud.*

Seventeen: this work needs WK3 to WK8 together — signalling, radio propagation, statistics, and drive-test practice. No part of it comes from textbook knowledge alone.

Eighteen: all seven complex-problem attributes are present, and every trade-off under P2 is measured rather than assumed. The clearest one is on slide 24: we alarm on 23 percent of samples to hold the miss rate at 12.6 percent.

Nineteen: the new part is where we point established methods, and the protocol that lets somebody else check the result.

## Slide 20 · Impact — 60 s

Society. Dhaka has one of the densest populations of mobile users in the world, and on our routes a handover happens every eleven seconds. A warning of one or two seconds is enough for the network to prepare the next cell before the break instead of after it.

Environment and sustainability. 24.5 percent of handovers go back to the cell they just left within fifteen seconds. That is measured signalling work that did not need to happen. A predictor that can flag it is the first step towards not doing it.

And now the limit, said plainly rather than quietly. We do not claim any energy saving in a live network, because we did not deploy anything. And we make no health claim at all. There were no human subjects and no exposure experiments in this work.

---

## Slide 21 · Main result — 95 s

*Pause before this slide. Read the five look-ahead times at an even pace. Do not speed up.*

At half a second: precision-recall 0.416 against a floor of 3.7 percent, which is 11.3 times better, AUROC 0.916, calibration error 0.023. At one second: 0.784, with a confidence range of 0.740 to 0.826, 11.7 times the floor, AUROC 0.933, calibration error 0.024. At two seconds: 0.627, 5.0 times, AUROC 0.854. At three seconds: 0.598, 3.4 times, AUROC 0.816. At five seconds: 0.606, 2.3 times, AUROC 0.783, with calibration error rising to 0.141 — so the further ahead we look, the less the exact probability can be trusted.

LightGBM is first at every look-ahead time and logistic regression is second, both ahead of the GRU, the Transformer, the TCN and the MLP. With 57 drives there is not enough data for a sequence model to learn what our 107 features already carry.

Event A3 itself, scored on the same data as a predictor, reaches AUROC 0.653 and catches only 5.5 percent of handovers one second ahead. That is the comparison that matters most, because A3 is what is running in the network today.

Counting whole handovers instead of samples, we catch 44.7 percent one second ahead and 65.1 percent at five. The ceiling is 90.5 percent, and it comes from recording once per second, not from the model.

## Slide 22 · Leakage — 75 s

Same data, same models, same formulation. The only change is splitting by whole drive instead of by random sample.

The GRU goes up by 74 percent. The Transformer by 44. The TCN by 27. LightGBM by 20. The MLP by 10. Logistic regression by only 4. And the A3 rule goes down by 2, because it has no parameters to over-fit with.

The reason is simple. Two samples one second apart on the same drive look almost identical. A random split puts almost the same row on both sides. And the more memory of the recent past a model has, the more it gains from seeing its own neighbour during training.

The consequence is worse than "all the scores go up". Because the gain depends on the model type, a careless split changes the ranking — it can make a deep model look like the winner when it is not. That is why we present the test protocol as a contribution, not as housekeeping.

## Slide 23 · Consistency and calibration — 70 s

Five separate classifiers contradict themselves on 43.6 percent of samples, giving a higher chance at one second than at three. Our single-model version contradicts itself on zero, and it cannot do otherwise.

We also tested the obvious alternative, because a reviewer would ask. Adding a separate correction step to each look-ahead time makes consistency worse, not better: 48.7 percent, with the largest contradiction growing from 0.495 to 0.596, and it costs a held-out split and two to five precision-recall points. It can beat us on calibration alone, not on calibration and consistency together.

Our calibration is better than the uncorrected baseline at every look-ahead time, with p below 0.0001 across the twenty paired folds. In practical terms, a calibration error of 0.024 means that when the system says eighty percent, a handover really follows about eighty percent of the time. So the number can be used in a decision, not only to sort samples.

## Slide 24 · The guarantee and its price — 80 s

The alarm threshold is not picked by hand. It is set on 28 drives kept aside for that purpose, using conformal risk control. The result is a promise: on future drives, the average share of handovers we miss stays below a target the operator chooses.

At a 20 percent target it alarms on 23 percent of samples and actually misses 12.6 percent of handovers, and the promise held on 82 percent of individual test drives. At a 5 percent target the alarm rate jumps to 61 percent, which no operator would accept. We show the whole curve, not one flattering point.

The promise rests on one assumption: that drives are interchangeable with each other, not that samples are. That is why the drive had to be the unit from the very beginning.

There is also a hard limit from the 28 drives themselves. With 28 calibration drives, no target tighter than about 3.4 percent can even be expressed, no matter how good the model is. So the promise depends on how much you drove, not on how clever the model is.

## Slide 25 · A road the model has never seen — 70 s

*"Frozen" is the word to stress.*

Each campaign held out completely, trained on the other three.

The urban arterial gives AUROC 0.949, precision-recall 0.826 at 9.9 times the floor, error 0.027. The urban loop gives 0.909 and 0.718 at 9.4 times, error 0.040 — the weakest of the four because it is the smallest campaign: eight drives, 174 handovers, 24 minutes. Dense urban gives 0.943 and 0.832 at 13.2 times, error 0.019.

And the highway gives AUROC 0.927 and precision-recall 0.761 at 14.9 times the floor, with a calibration error of 0.018. That is the highest lift and the best calibration of all four, on the one road and speed the model had never seen, and one that was driven after every modelling choice was frozen.

Adding it to the pool changed the headline number by nothing: AUROC 0.933 before, 0.933 after. A fourth campaign that changes nothing is the strongest sign available that the first three were not over-fitted.

## Slide 26 · Another team's dataset — 40 s

Between our own campaigns, with nothing shared — no drives, no routes, no cells — AUROC stays between 0.88 and 0.93. Then we go outside our data completely. On a public drive-test dataset collected by a different group, on a different network, our model reaches AUROC 0.752 one second ahead. A model trained directly on that dataset reaches 0.745. So what carries over is the method, not the fit. That is the claim worth making, because a fit belongs to one network and a method does not.

---

## Slide 27 · Why it works — 60 s

*The first sentence is the most quotable line in the thesis.*

The network triggers on its weakest signal.

The best single input is how long the phone has already been on this cell. On its own, that reaches AUROC 0.874. Serving SINR reaches 0.830. And the quantity the rule actually uses, the gap between serving and neighbour, reaches only 0.566, which is barely above guessing for a single input.

The signalling explains why. The gap condition is satisfied on 27.1 percent of all samples, and three out of five of the reports that follow are refused. So the gap must be met, but meeting it says very little.

In one sentence: the gap says a handover is allowed, the time on the cell says one is becoming due. A rule that watches permission instead of tendency will always be late.

## Slide 28 · Three in five A3 reports are never acted on — 45 s

7,385 A3 reports were sent across the four campaigns, and 62.9 percent of them are not followed by a handover within two seconds.

The rate rises with cell size: 57.2, 60.1, 63.3 and 71.9 percent across the four campaigns, with the highest figure on the highway, where the cells are biggest.

Two conditions travel with that number, and I will state both. It counts A3 reports only — all report types together give 68.7 percent — and only 43 to 52 percent of reports are A3 in the first place, a number we could only work out after the settings fix on slide 9.

## Slide 29 · Where ping-pong comes from — 80 s

Handovers that stay on the same carrier come back 31.0 percent of the time. Handovers that change carrier come back only 6.5 percent of the time. That is almost five times the difference.

One setting carries it: the plus one decibel offset with a 320 millisecond wait, which covers 72 percent of all handovers and comes back 29.2 percent of the time.

And it is not speed, which is the obvious guess and the wrong one. The highway, at 49.5 kilometres an hour, still comes back 31.1 percent of the time, higher than the urban average. So the thing to change is the waiting time, not the mobility.

One more point the literature usually skips. The rate depends on three choices papers rarely state: whether a cell is identified by PCI alone or PCI plus carrier, whether any return counts or only a return to the cell just left, and whether you count raw or checked events. On the same 938 handovers those choices give 24.5, 29.0, 38.5 and 41.3 percent. We quote 24.5 and state all three.

## Slide 30 · What did not help — 65 s

Added in good faith, and measured: more neighbour-cell data, features that group cells together, a separate ping-pong model, and two methods for adapting between campaigns. None of them helped. The separate ping-pong model reached AUROC 0.51, which is guessing. So ping-pong, treated as its own prediction target, is not predictable from these inputs.

What did help was the formulation, the settings fix, and the test protocol.

Two more findings. Handovers arrive in bursts rather than independently: a self-exciting model gives a branching ratio of 0.605, so each handover sets off about 0.6 more, and a residual test rejects the simple exponential shape at p equal to seven times ten to the minus four. And an upper bound on network benefit peaks at plus 0.34 when we allow alarms on five percent of samples, and turns negative by forty. That is a bound, not an estimate.

---

## Slide 31 · Conclusion — 130 s

Five results.

One. The next handover can be predicted about a second before the network's own rule can react, using only what the phone already measures: AUROC 0.933, precision-recall 0.784, 11.7 times the floor, calibration error 0.024.

Two. One model gives probabilities that never contradict each other, where five separate models contradict themselves on 43.6 percent of samples. One fit, and no data held back for correction.

Three. Testing by whole drive is worth between 4 and 74 percent depending on the model, so the protocol changes the ranking, not just the scores. That is a result about the field, not only about our models.

Four. The result holds at AUROC 0.927 on a road that was frozen out of every modelling decision, and at 0.752 on another team's public dataset.

Five. The guarantee comes with its price attached: alarms on 23 percent of samples to hold the real miss rate at 12.6 percent, with a hard limit of 3.4 percent set by having 28 calibration drives.

So the new part is not a new machine-learning algorithm. It is a complete method, grounded in real signalling, safe against leakage, honest about uncertainty, and tested on roads and data it had never seen.

And now the limits, which I will state rather than wait to be asked. 57 drives, one operator, four days, and a recording rate of one per second that caps event detection at 90.5 percent. We make no claim about cause and effect, because the network's rule is fully determined: given the radio state and the settings, A3 either fires or it does not. So we report only an upper bound. This is an offline predictor, not a deployed controller.

## Slide 32 · Future works — 55 s

In the order the limits demand.

First, compare drives that fall just on either side of the A3 threshold. That is the one step that makes the cause-and-effect question answerable, and it can be done on data we already have.

Then more routes and operators: four days on one network is enough for a careful study, not enough to say the result holds everywhere. Then connect the warning to a measured change in throughput or interruption, so the benefit stops being a bound. Then a real test of the waiting-time change the ping-pong result points to. And finally, release the code and dataset — the protocol argument on slide 22 is only worth making if somebody else can check it.

## Slide 33 · Thank you — 10 s

Thank you for your time and your attention. I welcome your questions.

---

## The eleven figures to have memorised

If one leaves your head in the middle of a sentence, say the point without it and keep going.

- **57 drives, 10,260 samples, 938 handovers** — 957 in the raw logs, 938 inside drives that pass the quality check.
- **0.933 AUROC, 0.784 precision-recall, 11.7 times the floor** at one second, calibration error 0.024.
- **6.7 percent** — the handover rate at one second. Every score is read against it.
- **0.653** — Event A3 scored as a predictor. It catches 5.5 percent one second ahead.
- **43.6 percent down to zero** — self-contradiction, five models versus one.
- **74 percent and 4 percent** — how much a careless split inflates the GRU, and logistic regression.
- **0.927** — the highway, frozen out of every modelling decision.
- **0.874 against 0.566** — time on the cell, against the A3 gap, each on its own.
- **62.9 percent** — A3 reports not acted on within two seconds, out of 7,385.
- **24.5 percent** — ping-pong, counting PCI plus carrier, within fifteen seconds.
- **23 percent for 12.6 percent** — alarm rate, for the real miss rate, at a 20 percent target.

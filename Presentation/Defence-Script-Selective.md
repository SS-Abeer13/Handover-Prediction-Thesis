:::center
{title}Final Thesis Defence Script
{sub}Predicting the Next LTE Handover from Drive-Test Signalling
{small}Keyed to Handover-Thesis-Presentation.pptx · 33 slides · plain English · two or three figures a slide, not twenty
:::

| | |
|---|---|
| **What this is** | The spoken script with the numbers thinned out. Each slide carries only the figures that carry an argument. The rest of the data is on the slide behind you and in the reserve list at the end. |
| **Length** | ≈ 3,000 words — **about 22 minutes**. Each slide’s time below is worked out from its own word count. |
| **Why so few numbers** | A figure the board remembers is worth five they do not. Reciting a table out loud makes every figure equally forgettable. Say the one that makes the point; let them read the rest. |
| **If asked for more** | The reserve list on the last page has every figure this script leaves out, grouped by which slide it belongs to. |
| **Rule** | Never guess a number in front of the board. If one leaves your head, say the point without it. |

---

## Slide 1 · Title — 30 s

Assalamualaikum. Respected chairman, respected members of the board, and my supervisor. This thesis is about predicting the next LTE handover from real drive-test data.

We ran four measurement campaigns in Dhaka and Gazipur. That gave us 57 drives and 938 handovers. Those handovers are not counted from a vendor tool — each one is read out of the network's own signalling. And there is no simulation anywhere in this work.

## Slide 2 · Outline — 30 s

There are eleven sections, and I will spend most of the time on three: the proposed system, the results, and the limits of what we claim.

Here is the headline, so you have it from the start. One second before a handover, our model reaches AUROC 0.933 against a handover rate of only 6.7 percent — that is almost twelve times better than guessing.

---

## Slide 3 · Background — 50 s

*The word to stress is "already".*

The phone measures its own cell and its neighbours once a second, and reports when a rule called Event A3 is satisfied. A3 says a neighbour must become better than the serving cell by a fixed amount, and must stay better for a fixed waiting time. Only then does the phone report. Only then can the network decide.

Here is the problem with that. The rule is written around a change that has already happened, so A3 can never fire early. It can only react. That is what the standard was built to do. Our question is whether the same measurements, read one second earlier, already show the handover coming.

## Slide 4 · Motivation — 40 s

The cost of reacting late shows up in our own data.

A handover happens about once every eleven seconds on our routes. Roughly a quarter of them go straight back to the cell they just left within fifteen seconds — the phone was moved, and then moved back. And the connection broke and had to be set up again 341 times.

One second of warning would be enough for the network to get the next cell ready, or to stop a handover that is only going to come back.

## Slide 5 · Literature — 50 s

We screened 108 papers and studied 22 prediction models closely. The field splits into two groups that do not meet.

Measurement studies have exactly the ground truth we need, from real networks, but they only describe. They do not build a predictor. Prediction studies do build models, but mostly on simulated data.

And of the 22 that use real radio data: not one keeps a whole drive out of training, not one reports calibration, and not one reports how much warning it gives. Zero out of twenty-two, on all three. So the published numbers are not wrong. There is simply no published result an operator could act on.

## Slide 6 · Objectives — 30 s

Five objectives, and each one is answered by a specific slide later.

Predict the handover at five look-ahead times, using only what the phone can see. Compare models under a test that cannot cheat. Make the probabilities consistent with each other, honest in value, and backed by a guarantee. Test on a road the model has never seen. And explain why it works, not just how well.

---

## Slide 7 · Research methodology — 35 s

Five steps. Collect: drive a measurement phone over real roads, recording the radio and the signalling together. Label: read the handover out of the signalling instead of guessing it. Build: features that look only backwards. Test: train on some drives, test on completely different drives. Evaluate: not just how good the prediction is, but what it costs to use.

That last step is where this work differs most. A good score alone does not tell an operator whether the warning is usable.

---

## Slide 8 · Proposed system — 40 s

Five stages. The one that makes everything else possible is stage two: the handover is the decoded RRC command itself, with a millisecond timestamp, not a counter we have to trust. Stage three uses only the past. Stage four is the formulation that keeps the five look-ahead times agreeing with each other. Stage five is testing by whole drive.

If any one of those stages is done loosely, the final number means nothing — and slide 22 shows exactly how much a loose stage five is worth.

## Slide 9 · Where the ground truth comes from — 65 s

*Go slowly. This sounds like a small detail and it is actually a contribution.*

A handover is a decoded RRC reconfiguration message carrying mobility control information. A clear command, with a millisecond timestamp.

But the measurement settings do not arrive all at once. They arrive piece by piece, and the identity numbers inside them only mean something against the settings active at that moment. Our first parser missed that, and almost every report came out as A3 — including reports where there was no neighbour cell at all. That is impossible, because A3 is defined on a neighbour. That impossible result is what told us the parser was wrong.

The fix is to rebuild a timeline of the settings and resolve each report against whatever was active at the time. And it changed a published assumption: the offsets on this network turn out to be negative, not positive. This network hands over more eagerly than the literature says it does.

## Slide 10 · What the model is given — 45 s

We build 152 input columns and use 107 of them, in four groups: radio, mobility, history, and signalling.

Everything looks backwards only. Every window ends at the current second, and no window crosses from one drive into another. We also added guards so that a report feature cannot carry information about the very handover it belongs to — without them, the model can read the answer off its own input.

And one input from the history group turns out to matter more than everything else. I will come back to it on slide 27.

## Slide 11 · One model, not five — 60 s

*This equation is the heart of the thesis.*

The obvious approach fails. Train five separate classifiers, one per look-ahead time, and they can tell you the chance within one second is higher than the chance within three seconds. That cannot be true — anything that happens within one second has also happened within three.

So we ask a different question at every step: given that the handover has not happened yet, does it happen in this next second? That is the hazard. The chance within any longer window is then the product of the surviving terms, so it can only go up as the window grows.

The order is therefore correct automatically. One model, one fit, no separate correction step. On our data that is the difference between 43.6 percent of samples contradicting themselves and zero.

---

## Slide 12 · What was modelled and compared — 45 s

This is a time-to-event problem, and the hazard is what turns five answers into one answer.

Seven learners were compared under the same folds, the same seeds and the same formulation — two table-based models, four different ways of giving a model memory of the recent past, and Event A3 itself scored as if it were a predictor, so the network's own rule sits on the same scale as everything else.

Every deep model got the same tuning budget, and none of them beat logistic regression. That is a statement about having 57 drives, not about deep models.

## Slide 13 · Where the data was collected — 25 s

Four campaigns in Dhaka and Gazipur, about 95 kilometres of driving. Three urban routes, and one highway run out to Gazipur at roughly three times the urban speed.

The circles on this map are handovers. They gather at particular junctions instead of spreading evenly along the road — which is the first reason why splitting the data randomly is dangerous.

## Slide 14 · Four measurement campaigns — 40 s

Three things about this table that I would rather say now than be asked later.

First, the raw logs hold 957 handovers, and 938 of them fall inside a drive that passes our quality check. 938 is the number every model in this thesis is scored on.

Second, the A3 settings are identical across all four campaigns. So when I hold one campaign out later, that is a test of road and speed, not of settings.

Third, the highway was driven after every modelling decision was already fixed.

## Slide 15 · Every look-ahead time is a rare-event problem — 25 s

At one second, only 6.7 percent of samples have a handover coming. That means a model which always says "no handover" already scores 93.3 percent accuracy.

That is why accuracy appears nowhere in this thesis. Every score is read against its own floor, and the rate changes at every look-ahead time, so each one has its own floor.

## Slide 16 · How the models were tested — 50 s

A whole drive is either trained on or tested on, never both. Four rotations, so every drive is tested exactly once, and the whole thing repeated with five random seeds.

The seeds are not decoration. With only four folds, a statistical test can never give a small enough p-value to mean anything, whatever the real difference is — it would be reporting its own limit instead of the data.

And the scaler, the alarm threshold and the calibrator are all fitted inside the training part only. Fitting a scaler on the full dataset is itself a small leak, and it is one of the first things a reviewer checks.

---

## Slides 17, 18, 19 · Knowledge profile, complex problem, complex activities — 10 s each

*Name one row from each and move on. Do not read the tables aloud.*

Seventeen: this work needs WK3 to WK8 together — signalling, radio propagation, statistics, and drive-test practice. No part of it comes from textbook knowledge alone.

Eighteen: all seven complex-problem attributes are present, and every trade-off is measured rather than assumed. The clearest one is on slide 24.

Nineteen: the new part is where we point established methods, and the protocol that lets somebody else check the result.

## Slide 20 · Impact — 50 s

Society: Dhaka has one of the densest populations of mobile users in the world, and a warning of one or two seconds is enough for the network to prepare the next cell before the break rather than after it.

Environment: about a quarter of handovers go back to the cell they just left. That is measured signalling work that did not need to happen.

And the limit, said plainly rather than quietly. We claim no energy saving in a live network, because we did not deploy anything. And we make no health claim at all — there were no human subjects and no exposure experiments in this work.

---

## Slide 21 · Main result — 60 s

*Pause before this slide. This is the number they will remember.*

One second before a handover: AUROC 0.933, and a precision-recall score of 0.784 against a handover rate of 6.7 percent. That is 11.7 times better than guessing.

The comparison that matters most is the last row. Event A3 itself, scored on exactly the same data as a predictor, reaches 0.653 — because A3 is what is running in the network today.

The scores at the other look-ahead times are on the slide. They fall as we look further ahead, which is what you would expect, and the ranking of the models does not change.

One more level, because samples are not what an operator cares about. Counting whole handovers, we catch about 45 percent of them a second ahead. The ceiling is 90 percent, and that ceiling comes from recording once a second, not from the model.

## Slide 22 · Leakage — 60 s

Same data, same models, same formulation. The only change is splitting by whole drive instead of by random sample.

The GRU goes up by 74 percent. Logistic regression goes up by 4.

The reason is simple. Two samples a second apart on the same drive look almost identical, so a random split puts nearly the same row on both sides — and the more memory of the recent past a model has, the more it gains from seeing its own neighbour in training.

The consequence is worse than "all the scores go up". Because the gain depends on the model type, a careless split changes the ranking. It can make a deep model look like the winner when it is not. That is why we present the test protocol as a contribution, not as housekeeping.

## Slide 23 · Consistency and calibration — 50 s

Five separate classifiers contradict themselves on 43.6 percent of samples. Our single-model version contradicts itself on zero, and it cannot do otherwise.

We also tested the obvious alternative, because a reviewer would ask: adding a separate correction step to each look-ahead time. It makes the consistency worse, not better, and it costs a held-out split and some accuracy. It can beat us on calibration alone. It cannot beat us on calibration and consistency together.

And calibration here has a plain meaning. When the system says eighty percent, a handover really follows about eighty percent of the time. So the number can be used in a decision, not only to sort samples.

## Slide 24 · The guarantee and its price — 60 s

The alarm threshold is not picked by hand. It is set on drives kept aside for that purpose, and the result is a promise: on future drives, the share of handovers we miss stays below a target the operator chooses.

Now the price. To promise a 20 percent miss rate, the system alarms on 23 percent of samples — and actually misses 12.6 percent. To promise 5 percent, it has to alarm on 61 percent of samples, which no operator would accept.

We show the whole curve instead of one flattering point. And there is a hard limit underneath it: the promise you can make depends on how many calibration drives you collected, not on how clever the model is. That makes it a question of campaign design.

## Slide 25 · A road the model has never seen — 45 s

*"Frozen" is the word to stress.*

Each campaign held out completely, trained on the other three. AUROC stays between 0.909 and 0.949 — so no single campaign is carrying the result.

The highway is the one that matters. It scores 0.927, with the best calibration of the four, on the one road and speed the model had never seen — and it was driven after every modelling choice was frozen.

And adding it to the pool changed the headline number by nothing. A fourth campaign that changes nothing is the strongest sign available that the first three were not over-fitted.

## Slide 26 · Another team's dataset — 30 s

Then we go outside our own data completely. On a public drive-test dataset collected by a different group, on a different network, our model reaches 0.752. A model trained directly on that dataset reaches 0.745.

So what carries over is the method, not the fit. That is the claim worth making, because a fit belongs to one network and a method does not.

---

## Slide 27 · Why it works — 40 s

*The first sentence is the most quotable line in the thesis.*

The network triggers on its weakest signal.

The best single input is how long the phone has already been on this cell. On its own, that reaches 0.874. The quantity the rule actually uses — the gap between serving and neighbour — reaches only 0.566, barely above guessing.

In one sentence: the gap says a handover is allowed, and the time on the cell says one is becoming due. That is a statement about the rule, not about our model. A rule that watches permission instead of tendency will always be late.

## Slide 28 · Three in five A3 reports are never acted on — 25 s

Across the four campaigns, 62.9 percent of A3 reports are not followed by a handover within two seconds. So a report is not a decision — the network refuses most of them.

Two conditions travel with that number, and I will state both: it counts A3 reports only, and it uses a two-second window. Both are on the slide.

## Slide 29 · Where ping-pong comes from — 50 s

Handovers that stay on the same carrier come back 31 percent of the time. Handovers that change carrier come back only 6.5 percent of the time.

And it is not speed, which is the obvious guess and the wrong one. The highway comes back just as often as the urban routes. So the thing to change is the waiting time in the rule, not the mobility.

One more point the literature usually skips. The ping-pong rate depends on three definition choices that papers rarely state, and on our own data those choices move the answer by more than fifteen points. We quote the strictest one and we state all three.

## Slide 30 · What did not help — 30 s

Added in good faith and measured: more neighbour-cell data, features that group cells together, a separate ping-pong model, and two methods for adapting between campaigns. None of them helped — the separate ping-pong model came out at chance.

What did help was the formulation, the settings fix, and the test protocol. We report the failures because they are what makes that claim credible.

---

## Slide 31 · Conclusion — 95 s

Five results.

One. The next handover can be predicted about a second before the network's own rule can react, using only what the phone already measures — AUROC 0.933.

Two. One model gives probabilities that never contradict each other, where five separate models contradict themselves on 43.6 percent of samples.

Three. Testing by whole drive changes the ranking of the models, not just their scores. That is a result about the field, not only about our work.

Four. The result holds on a road that was frozen out of every modelling decision, and on another team's public dataset.

Five. The guarantee comes with its price attached, and we report the price.

So the new part is not a new machine-learning algorithm. It is a complete method — grounded in real signalling, safe against leakage, honest about uncertainty, and tested on roads and data it had never seen.

And the limits, which I will state rather than wait to be asked. 57 drives, one operator, four days. We make no claim about cause and effect, because the network's rule is fully determined — given the radio state and the settings, A3 either fires or it does not. So we report only an upper bound. This is an offline predictor, not a deployed controller.

## Slide 32 · Future works — 45 s

In the order the limits demand.

First, compare drives that fall just either side of the A3 threshold. That is the one step that makes the cause-and-effect question answerable, and it can be done on data we already have.

Then more routes and more operators. Then connect the warning to a measured change in throughput or interruption, so the benefit stops being a bound. Then a real test of the change in waiting time that the ping-pong result points to. And release the code and the dataset, because the protocol argument is only worth making if somebody else can check it.

## Slide 33 · Thank you — 10 s

Thank you for your time and your attention. I welcome your questions.

---

# Reserve — the figures this script leaves out

Do not say these unless you are asked. They are here so that nothing is missing when you are.

**Dataset (slides 13–15).** 10,260 samples at one per second. 15 drives and 290 handovers on the urban arterial, 8 and 174 on the urban loop, 20 and 297 in dense urban, 14 and 177 on the highway. Highway mean speed 49.5 km/h. 2.9 hours of driving, median gap between handovers 3.5 seconds. Handover rate by look-ahead time: 3.7, 6.7, 12.5, 17.5 and 25.9 percent.

**A3 settings (slide 3).** Offsets −15, −10, −6.5, +1 and +5 dB; waiting time 160 to 1024 ms. The +1 dB / 320 ms setting carries 679 of the 938 handovers, 72 percent.

**Parser fix (slide 9).** 99.4 percent of reports parsed as A3 before the fix; 43 to 52 percent after it. Earlier published work assumed +3 dB offsets.

**Features (slide 10).** 83 radio, 17 mobility, 13 signalling, 7 history, from 152 built.

**Protocol (slide 16).** 4 folds × 5 seeds = 20 paired comparisons; about 14 drives held out against 43 in training. With 4 folds alone no p-value below 0.125 is reachable.

**Main result (slide 21).** By look-ahead time — precision-recall 0.416, 0.784, 0.627, 0.598, 0.606; lift 11.3, 11.7, 5.0, 3.4, 2.3; AUROC 0.916, 0.933, 0.854, 0.816, 0.783; calibration error 0.023, 0.024, 0.061, 0.091, 0.141. Confidence range at one second 0.740 to 0.826. A3 catches 5.5 percent one second ahead. Event level: 44.7 percent at one second, 65.1 at five, ceiling 90.5.

**Leakage (slide 22).** GRU +74, Transformer +44, TCN +27, LightGBM +20, MLP +10, logistic +4, A3 −2 percent.

**Consistency (slide 23).** Separate classifiers 43.6 percent; with per-horizon correction 48.7 percent, largest contradiction 0.495 → 0.596; costs 2 to 5 precision-recall points. Calibration beats the baseline with p below 0.0001 over 20 paired folds.

**Guarantee (slide 24).** 28 calibration drives; the promise held on 82 percent of test drives at a 20 percent target; no target tighter than about 3.4 percent is expressible with 28 drives.

**Generalisation (slide 25).** Held-out AUROC 0.949, 0.909, 0.943, 0.927; precision-recall 0.826, 0.718, 0.832, 0.761; lift 9.9, 9.4, 13.2, 14.9; calibration error 0.027, 0.040, 0.019, 0.018. The urban loop is weakest because it is the smallest campaign.

**Mechanism (slide 27).** Dwell time 0.874, serving SINR 0.830, A3 gap 0.566. The gap condition holds on 27.1 percent of samples.

**A3 conversion (slide 28).** 7,385 reports; 57.2, 60.1, 63.3 and 71.9 percent declined across the four campaigns, pooled 62.9. All report types together, 68.7 percent.

**Ping-pong (slide 29).** 24.5 percent by PCI plus carrier over 15 seconds; 29.0 by PCI alone; 38.5 counting any return; 41.3 ungrouped over 957 raw events. Intra-carrier 31.0 against inter-carrier 6.5. The +1 dB / 320 ms setting returns at 29.2 percent; the highway at 31.1.

**Other (slide 30).** Dedicated ping-pong model AUROC 0.51. Handovers arrive in bursts — branching ratio 0.605, and a residual test rejects the simple exponential shape. Upper bound on benefit peaks at +0.34 at a five percent alarm budget and turns negative by forty.

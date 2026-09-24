# Defence speaking script

### *Uncertainty-Aware Multi-Horizon Handover Prediction from Drive-Test Signalling*

**Deck:** `Handover-Thesis-Defence.pptx` — 52 slides (title + 42 content + thank-you + 8 appendix)
**Full core path:** **21:40** — with 20-minute and 18-minute cut lists below. Slide numbers are the real PowerPoint numbers.

---

## Before you start: the three lengths this deck supports

The deck is organised as **four questions** rather than eight acts, which makes it easy to shorten: slides come out from inside a part without breaking the spine, because the roadmap and the breadcrumbs still account for every part.

**Full — 21:40.** All 42 content slides.

**A 20-minute talk — 19:35.** Hide three slides and trim five.

| | slide | why it is safe |
|---|---|---|
| hide | **8** · *The question this thesis answers* | Slide 2's roadmap and slide 9's objectives already carry it. |
| hide | **15** · *The framework end to end* | Slides 16 to 18 make the same points concretely, one at a time. |
| hide | **36** · *The two fair comparisons* | Jump to it the moment someone quotes a published accuracy figure. |
| trim | **11**, **12**, **13** to 20 s | The map, the statistics table and the RSRP map are three views of one campaign. Make one point on each and move. |
| trim | **34**, **39** to 25 s | Both are strong slides that can be said faster without losing anything. |

**An 18-minute talk — 17:50.** Everything above, plus hide **12** outright, and hide **31** (the Hawkes fit), **32** (the ping-pong definition ladder) and **41** (future work — fold its first item into the limitations slide instead). Slides 31 and 32 are the two best jump-to slides you own, so losing them from the *spoken* path costs nothing in Q&A: slide 33 still quotes 24.5% with its three choices stated, and slide 13 still says the handovers clump.

Below 18 minutes you start losing a substantive result rather than a duplicate. If the limit is 15, ask for 20.

**Two slides stay hidden in every configuration:**

| Slide | Title | Why |
|---|---|---|
| **21** | *Before claiming a winner, every model was given the same tuning budget* | One sentence at the top of slide 22 does the whole job. |
| **28** | *Both zero-cost domain adaptations make transfer worse* | Appendix C (slide 47) is this slide with the arms broken out. |

### Two delivery rules that matter more than the words

1. **One idea per slide, then advance.** Every slide's conclusion is already written in its title. Say the title in your own words, give the one number that proves it, move on. Never read the bullets — the board can read.
2. **When you don't know, name the measurement you would need.** That is the most defensible sentence available to you, and this thesis is built so you always have one.

---

## What changed, and why

The deck was rebuilt onto a **four-question spine** — *why this problem · what was developed · what does the evidence show · what has been achieved* — with a conventional breadcrumb on every slide: MOTIVATION, RELATED WORK, OBJECTIVES, DATA, METHOD, IMPLEMENTATION, EVALUATION, RESULTS, UNCERTAINTY, ROBUSTNESS, NETWORK ANALYSIS, BENEFIT, POSITIONING, NOVELTY, ACHIEVEMENTS, SYNTHESIS, DISCUSSION, FUTURE WORK, CONCLUSION.

**Five slides were added, and two moved to the appendix.**

- **Slide 2, the roadmap**, states the four questions up front. It replaces the old narrative diagram, which showed the same structure less legibly.
- **Slide 7, foundations**, puts the provenance of every borrowed method into one table, *before* any of them is used. It was previously buried in the appendix. Declaring it early is what lets slide 37 make a small, precise novelty claim instead of a large vague one.
- **Slide 9, five objectives**, decomposes the research question into O1 to O5 and names the slide that answers each.
- **Slide 15, the framework**, shows the whole method in five stages before any of it is detailed. It opens Part 2.
- **Slide 38, achievements**, closes O1 to O5 against their evidence with a **boundary column**, and adds a sixth row for the thing that was *not* achieved. This is the strongest structural addition: the board can audit the promise against the delivery in a single view.
- The **pipeline diagram** (now appendix F, slide 50) and the **four-literature map** (appendix G, slide 51) left the spoken path; slides 15 and 7 cover their ground.

**Every content slide now ends in a maroon takeaway strip** — one sentence, always in the same place. It is never a restatement of the title: it is the qualifier, the scope limit, or the consequence. On slide 25 it says the bound is on the expected risk and not on every drive; on slide 32 that published ping-pong rates are not comparable; on slide 23 that the inflation is differential and therefore reorders the leaderboard.

**And the earlier reorderings still hold:** the fourth-capture slide sits with the other robustness tests rather than among the data slides; the hazard result follows the headline immediately; report conversion follows the mechanism slide it proves; the clustering block runs uninterrupted.

## Slide 1 · Title — 20 s · **0:20**

**On screen.** Title, subtitle, your name, supervisor, department, date.

**What it represents.** The framing sentence of the whole defence. The subtitle — *how far ahead can the next LTE handover be seen, and with what guarantee?* — is the question every later slide answers a piece of.

> **Say:** Good morning. I'm Abeer Saadman, and this is my thesis on uncertainty-aware handover prediction from drive-test signalling. It comes down to one question: how far ahead can we see the next LTE handover coming — and how much should anyone trust the number we put on it? Let me start with why the question exists at all.

---

## Slide 2 · Defence roadmap — 30 s · **0:50**

**On screen.** Four numbered questions with a one-line answer each: *01 Why this problem? · 02 What was developed? · 03 What does the evidence show? · 04 What has been achieved?*, over a takeaway strip.

**What it represents.** The spine of the whole talk, and a promise the board can hold you to. Every slide from here belongs to exactly one of the four, and the breadcrumb in the corner of each slide says which. It replaces the old narrative diagram, which showed the same structure with more ink and less legibility.

> **Say:** Before anything else, the shape of the next twenty minutes. Four questions. Why this problem — what the reactive rule actually costs, what the literature does and does not do, and the five objectives that come out of that. What was developed — labels grounded in signalling, a hazard formulation, a feature set, and an evaluation protocol built to resist leakage. What the evidence shows — the benchmark, the calibration, a certified warning threshold, and generalisation to a corridor the model had never seen. And what has been achieved — each objective closed against its evidence, with the boundary of every claim stated. The corner of every slide tells you which of the four you are in.

---

# PART 1 — Why this problem?

---

## Slide 3 · *LTE hands over with a rule that acts only after the radio has already changed* — 40 s · **1:30**
**On screen.** `fig01_a3_event` — serving and neighbour RSRP curves crossing, the A3 entering condition marked, the time-to-trigger window shaded, the handover command at the end of it.

**What it represents.** The motivation, stated physically rather than rhetorically. Event A3 is *by construction* reactive: it cannot fire until the neighbour is already better by an offset **and** has stayed better for a whole time-to-trigger. The network therefore always acts after the radio has gone bad. That lag is the space this thesis works in.

> **Say:** This is how LTE decides to hand over today. The phone watches its serving cell and its neighbours, and Event A3 fires once a neighbour has been better by some offset for a whole time-to-trigger window — on this network, one dB held for 320 milliseconds. Look at where the decision lands. After the crossover. The rule is reactive by design: it cannot fire until the radio has already changed. Everything people complain about downstream follows from that — the interruption, the throughput dip, the ping-pong straight back. One or two seconds of warning would be enough to prepare for it, or to suppress it. That's the opening this thesis works in.

---

## Slide 4 · *The cost is measurable, and the predictor does not exist* — 35 s · **2:05**
**On screen.** `fig27_necessity` — four counted costs on the left (938 handovers, 24.5% ping-pong, 341 re-establishments, 4,645 declined A3 reports); on the right, three "0 of 22" rows from the protocol audit, under a maroon box.

**What it represents.** The necessity of the study, argued entirely from counted quantities rather than from assertion. The left column says the reactive rule is expensive *on this network*; the right says nobody has built the thing that would help. Both halves are needed: a cost with no gap is someone else's problem, and a gap with no cost is not worth filling.

> **Say:** So is this worth doing? Here is the case, and every number on the left is counted from these four capture days. 938 handovers in under three hours — one every eleven seconds. A quarter of them go straight back to the cell just left. Three hundred and forty-one times the link actually dropped and had to be re-established. And of seven thousand A3 reports the phone sent, the network declined four and a half thousand — signalling that bought nothing. That's the cost. On the right is the gap: of 22 comparable papers, none holds out the mobility unit, none reports calibration, and none reports a lead time. The measurement exists in the signalling. Nobody has pointed a predictor at it.

---

## Slide 5 · *Two literatures exist, and neither does what a deployable predictor needs* — 35 s · **2:40**

**On screen.** Two columns — measurement studies (Deng 2018, Ghoshal 2025) left, prediction studies right, each with its strength and its gap.

**What it represents.** The gap, framed as *structural* rather than as a complaint about anyone's paper. Two healthy literatures exist; they simply do not overlap. That framing makes the contribution a bridge rather than a correction, which is much harder to argue with.

> **Say:** There are two literatures here and they don't touch. On the left, measurement studies — Deng's IMC paper, Ghoshal's 2025 work across three US operators. They have exactly the ground truth I need: real configurations recovered from real signalling. They build no predictor. On the right, prediction studies — I screened 108 references over three passes, 22 of which predict handover, link failure or next-cell occupancy. They have the models, but mostly on simulation, and mostly without a grouped split. The ground truth sits on one side, the modelling on the other. This thesis is an attempt to put them in the same room.

---

## Slide 6 · *Of 22 comparable papers, none splits by drive and none reports calibration* — 35 s · **3:15**
**On screen.** `fig06_protocol_audit` — the 22 comparable papers scored against five protocol criteria.

**What it represents.** The evidence behind the gap claim. This is an audit on *protocol*, never on results — it deliberately does not say anyone's number is wrong. That distinction keeps it from sounding like an attack, and it is also what makes it survive scrutiny.

> **Say:** I audited those 22 papers, and I want to be precise about what I audited: protocol, not headline numbers. I'm not saying anyone's result is wrong — I'm saying I can't tell. None of the 22 holds out the mobility unit for a per-timestep task on measured radio, and none reports calibration. I'll name the exceptions rather than round them away: five do split on something coarser than a row — by zone, device, time, travel day, deployment event. That's better than nothing. It just isn't the same test. I widened the survey twice hoping these rows would move. They didn't.

---

## Slide 7 · *Foundations: what is borrowed, and what for* — 30 s · **3:45**
**On screen.** A three-column table: **Methodological strand** (with its primary source) · **The established idea** · **Role in this work**, six rows — discrete-time survival, conformal risk control, wireless conformal prediction, self-exciting point processes, unsupervised adaptation, signalling measurement.

**What it represents.** The provenance of every method in the thesis, declared **before** any of them is used. This is the second half of the related-work section: slide 5 says who else does the task, this says where the machinery came from. Declaring it up front is what lets the novelty slide near the end make a small, precise claim instead of a large vague one.

> **Say:** The other half of related work is where the method came from, and I would rather put it on one slide than let it emerge. Discrete-time survival: an established idea, conditional event hazards, and I use it to get coherent cumulative probabilities out of a single fit. Conformal risk control: distribution-free expected-risk control, used here to certify a warning threshold at a target miss rate. Wireless conformal prediction already exists — Cohen, Simeone — and what it tells me is that the open question is the exchangeable unit. A self-exciting point process, to measure how strongly handovers cluster, with the kernel actually tested. Unsupervised adaptation, tried and reported as a negative. And signalling measurement, which is where the ground truth comes from. None of that column is mine. The right-hand column is.

---

## Slide 8 · *The question this thesis answers, stated once* — 30 s · **4:15**
**On screen.** The research question in a callout box; four short "how" clauses beneath it.

**What it represents.** The contract with the board. Each clause names a standard you will be held to later — a prevalence-aware floor rather than accuracy, five coherent horizons rather than one, a distribution-free guarantee rather than a confidence interval, and signalling-decoded ground truth rather than a vendor flag.

> **Say:** Here is the question, stated once, and I'll be held to it for the rest of the talk. Given what a phone can observe right now, how well can the next handover be predicted, how far ahead, and with what guarantee? Each word does work. *How well* means against the prevalence floor, never accuracy. *How far ahead* means five horizons at once, kept mathematically consistent with each other. *With what guarantee* means a distribution-free bound on missed handovers. And all of it on real drive-test data where the truth comes from decoded RRC signalling.

---

## Slide 9 · *Five objectives, and where each one is answered* — 30 s · **4:45**
**On screen.** O1–O5, each with a one-line statement and the slide numbers that answer it.

**What it represents.** The contract, in checkable form. The previous slide states the research question; this decomposes it into five things you promise to deliver, and tells the board exactly where each is delivered. **Slide 38 closes all five.** That pairing — objectives early, achievements late — is the structural backbone of the talk, and it is what lets a board follow along rather than wait for the end to judge.

> **Say:** That question breaks into five objectives, and I will point at the slide that answers each one as we go. O1: predict the next handover at five horizons from what a phone can observe at the time. O2: establish a benchmark a reviewer would accept — seven learners, grouped by drive, and the cost of getting the split wrong actually measured rather than asserted. O3: make the probabilities usable and not merely well ranked — coherent across horizons, calibrated, and bounded per drive. O4: test generalisation beyond the training capture, by holding out a whole corridor and by scoring on somebody else's dataset. And O5: explain the mechanism rather than only reporting accuracy. Slide 38 comes back to all five with the evidence and the boundary of each claim.

---


# PART 2 — What was developed?

---

## Slide 10 · *measId and reportConfigId are message-scoped, so a flat parse misattributes silently* — 40 s · **5:25**
**On screen.** `m02_signalling` — the configuration-timeline reconstruction: measConfig arrives incrementally, AddMod inserts or replaces, and the timeline holds the state in force at each report.

**What it represents.** The credibility slide for the entire dataset, and it comes *before* any result on purpose. A defect was found in the extraction; it was found by comparison with a published method rather than by luck; and it changed four claims, two of them the thesis's own. Admitting that first is what makes every number afterwards land.

> **Say:** Before any result, the thing that nearly broke this dataset. In RRC, the measurement identifiers are scoped to the message that carries them — the configuration arrives incrementally, and an identifier only means something relative to the state in force at that moment. Parse it flat and you misattribute every report, silently, with no error anywhere. What gave it away was arithmetic: my first parse said 99.4% of reports were A3, and that's impossible, because 43% of reports carry no neighbour at all. I found it by checking my extraction against a published method, not by reading my own code. It changed four claims — two of them mine. One of them is that the offsets deployed here are negative, not the plus-three dB that published work on this network had assumed.

---

## Slide 11 · *57 drives, two corridors, 938 signalling-confirmed handovers* — 30 s · **5:55**
**On screen.** `fig03_map_routes` — four capture days on an OpenStreetMap basemap of Dhaka, handover positions marked, with a drawn key.

**What it represents.** The dataset made concrete and geographic. It also introduces the unit of analysis — **the drive** — which is the hinge of the whole protocol: segmentation, grouping, bootstrapping and the risk guarantee are all defined on it.

> **Say:** Here is the campaign. Four days, 57 drives, 938 handovers confirmed in the signalling — three urban corridors in Dhaka and one run out to Gazipur on the highway. And I want to flag one word that keeps coming back: the *drive*. Not the sample — the drive. It's the unit of segmentation, of grouping, of the bootstrap, and of the guarantee at the end. If you remember one design decision from this talk, that's it.

---

## Slide 12 · *The campaign in numbers, capture by capture* — 30 s · **6:25**
**On screen.** A table: corridor, drives, samples, duration, handovers, measurement-report instants, RRC re-establishments and A3 decline rate, for each of the four captures with a pooled column.

**What it represents.** The dataset laid out so nothing has to be taken on trust. It is also where the 957-vs-938 distinction gets stated once, properly, rather than being explained under pressure later. Do **not** read the table — point at three rows.

> **Say:** The campaign in full, so you can see what is behind every number in this talk. Four days, 57 drives after quality control, ten thousand two hundred and sixty samples, 938 handovers. Three rows are worth pointing at. Re-establishments: 159 in the dense urban core, five on the highway — that is the cleanest physical contrast in the campaign. Decline rate: it climbs from 57% to 72% as the cells get wider. And the footnote: 957 handovers are in the raw logs, 938 are inside drives that pass quality control, and the 938 are what every model is scored against. I say which one I mean every time.

---

## Slide 13 · *Handovers cluster where the link is weak, and a quarter are ping-pongs* — 30 s · **6:55**
**On screen.** `fig04_map_rsrp` — the same routes coloured by RSRP band, handover locations over the top.

**What it represents.** The physical intuition behind all of Act VI, planted early. Handovers are not spread along the route; they clump at specific junctions. That clumping is what the point process later formalises, and the ping-pong rate is its most visible symptom. Say "a quarter" here and leave it — slide 32 comes back and takes that number apart.

> **Say:** Same routes, now coloured by received power. Two things to see. The handovers aren't spread along the route — they clump, at specific junctions, where the link is weakest. And a quarter of them go straight back to the cell they just left within fifteen seconds. That's not a nuisance statistic, it's a clue: handovers arrive in bursts rather than independently. I take it seriously enough later to fit a point process to it.

---

## Slide 14 · *Every horizon is a rare-event problem, so every metric is read against its floor* — 30 s · **7:25**
**On screen.** `fig05_dataset` — prevalence by horizon, 3.7% at half a second up to 26.0% at five seconds.

**What it represents.** The measurement contract. It pre-empts the most common reviewer error in this literature — quoting accuracy on an imbalanced task — and it defends the half-second horizon, which looks impossible on a 1 Hz grid until you notice the event clock is millisecond-precise even though the sample clock isn't.

> **Say:** Ten thousand two hundred and sixty samples on a uniform one-hertz grid. Look at the prevalence: three point seven percent at half a second, twenty-six at five. The difficulty of the task changes with the horizon, so a single accuracy number would be meaningless — every result in this talk is read against its own floor. And one word about that half-second column, because it looks impossible on a one-hertz grid: the *sampling* clock is one hertz, but the *event* clock is millisecond-precise, because the timestamp comes out of the signalling. The horizon is real. It's the detection that's sampling-limited, not the labelling.

---


---

## Slide 15 · *The framework end to end, in five stages* — 30 s · **7:55**
**On screen.** `m14_framework` — five numbered stages left to right: 01 Measure · 02 Ground the labels · 03 Represent · 04 Predict as a hazard · 05 Certify and score. Stages 02 and 04 are highlighted maroon.

**What it represents.** The one slide that shows the whole method before any of it is detailed. It opens Part 2 and gives the board a frame for the four slides that follow. The two highlighted stages are the two that carry the contribution — the ground truth and the hazard formulation — so the highlighting is an argument, not decoration.

> **Say:** The whole method on one slide, then I will take three of these stages in detail. Measure: one-hertz radio, GPS and speed, plus the decoded control plane. Ground the labels — and this is the stage that makes everything else possible: a configuration timeline resolves the message-scoped identifiers, and a handover becomes a decoded RRC command with a millisecond timestamp rather than a vendor counter. Represent: 107 features, every window backward-looking. Predict as a hazard, which is the methodological claim — one fit instead of five classifiers. And certify and score, which is what the comparable literature omits: a threshold with a guarantee attached, and a warning cost an operator would actually be charged for. Eighteen pipeline stages, seventeen passing tests, and a rebuild from raw returns 10,260 samples and 938 handovers exactly.

---

## Slide 16 · *Handover prediction is a discrete-time survival problem, not five separate binary tasks* — 35 s · **8:30**
**On screen.** `m04_hazard` — five independent heads versus one hazard fit, with the product-limit identity between them.

**What it represents.** The central methodological claim, and the easiest one to make intuitive. Five separate classifiers can output a 1-second probability higher than the 3-second probability — a statement that the event happens and then un-happens. One hazard fit makes that impossible by construction rather than by correction, and the property carries to any learner you drop in.

> **Say:** Now the piece I'd most like you to take away. The obvious way to do five horizons is five classifiers, and it produces nonsense: a one-second alarm higher than a three-second alarm, which says the handover happens and then un-happens. That isn't a rounding error — it happens on nearly forty-four percent of rows. So I reformulated. Instead of asking "will it happen within k seconds", ask "given it hasn't happened yet, does it happen *now*" — that's a discrete-time hazard. The horizons are then products of the same hazards, so the ordering is arithmetic, not post-processing. Zero violations, by identity. And it holds for any learner, which is what makes it a contribution rather than a trick.

---

## Slide 17 · *152 columns built, 107 used, four blocks, two guards* — 35 s · **9:05**
**On screen.** `m13_features` — the two raw sources feeding four feature blocks (RF 83, mobility 17, history 7, signalling 13), into 152 columns, through a degenerate filter, to 107 features and a per-fold robust scaler.

**What it represents.** Feature engineering, and the two places where a careless choice would have leaked the answer. The pleasing part of this slide is the size inversion: the smallest block, seven history features, contains the strongest predictor in the study.

> **Say:** What the model is actually given. Four blocks: 83 RF features — rolling means, standard deviations, first and second differences over three, five and ten seconds — seventeen mobility features from GPS, seven history features, and thirteen from the signalling. 152 columns built, 107 surviving a degenerate filter that is fitted on training rows only. And note the size inversion: the smallest block is the strongest. Seven history features, and one of them — how long the phone has been on this cell — reaches AUROC 0.874 on its own. Two guards matter. Every window is backward-looking and closed at t, and none crosses a drive boundary. And the one that nearly caught me: a measurement report precedes its handover command by fifty to two hundred milliseconds, which is *inside* one sample. So the report-count windows stop one sample early. Seven unit tests pin that boundary.

---

## Slide 18 · *Every drive is tested exactly once, and nothing from a test fold is ever fitted* — 25 s · **9:30**
**On screen.** `m03_protocol` — the grouped rotation across 57 drives, repeated over 5 seeds.

**What it represents.** The evaluation protocol, plus an honest answer to "why not just a train/test split?" — with 57 drives a single split leaves 8 in test, and a bootstrap over 8 groups is wide for a reason that has nothing to do with the model.

> **Say:** Why not one held-out split? Because 57 drives leave eight in test, and a bootstrap over eight groups is wide for the wrong reason. And why five seeds? Because with four folds a two-sided Wilcoxon test cannot return a p-value below nought point one two five whatever the data says — the test has no power to reject. So the rotation repeats over five seeds: twenty paired observations, a bootstrap interval on every difference, and every drive tested exactly once.

---


# PART 3 — What does the evidence show?

---

## Slide 19 · *Gradient boosting reaches AUROC 0.933 at 1 s — twelve times the prevalence floor* — 40 s · **10:10**
**On screen.** `fig10_model_comparison` — every learner at the 1-second horizon with the prevalence floor drawn.

**What it represents.** The headline. Read it in this order: the number, the floor it is read against, the calibration, and only then the ranking. The ranking is the part most likely to draw a question, so the explanation for why the sequence models lose is pre-loaded into the script.

> **Say:** The headline. Gradient boosting, one second ahead: AUROC nought point nine three three, and precision–recall nought point seven eight four against a six point seven percent floor — eleven point seven times the floor, with a calibration error of nought point nought two four, so the probabilities mean what they say. Two comparisons make it real. The deployed A3 rule, scored on the same data, reaches nought point six five three and catches five and a half percent of handovers a second ahead. And a linear model comes second here, ahead of every sequence model. I'd rather say why than hide it: on 57 drives the deep models have nothing extra to learn. That's a statement about my sample size, not their architectures. At the event level, where an operator lives: forty-five percent of handovers seen coming one second out, sixty-five percent at five.

---

## Slide 20 · *The hazard model earns coherence; per-horizon calibration buys ECE and destroys it* — 35 s · **10:45**
**On screen.** `fig13_hazard_results` — six arms on identical folds, coherence violations and calibration error side by side.

**What it represents.** The payoff of slide 16, honestly accounted. The hazard model does not win on every axis, and saying so is exactly what makes the axis it *does* win on believable. The narrowed claim at the end is the defensible one — say it in those words.

> **Say:** So what does the hazard formulation actually buy, measured? Calibration improves against an uncalibrated baseline — between nought point nought nought six and nought point nought three ECE, p below nought point nought nought nought one over twenty paired folds. But I'll be straight about the comparison that doesn't go my way: a baseline with a proper calibration step beats me on calibration error alone. It pays for that with a held-out split and two to five points of precision–recall. And the arm that looks like the easy fix makes things worse — isotonic calibration on its own pushes the worst coherence violation from nought point four nine up to nought point six. So the narrowed claim is the defensible one: calibration, coherence and ranking together, out of a single fit.

---

## Slide 21 · *Before claiming a winner, every model was given the same tuning budget* — **HIDDEN**
**Why hidden.** One sentence at the top of slide 22 does the whole job. Jump here by number only if someone presses on tuning fairness and wants the design.

---

## Slide 22 · *The deep baselines really were under-tuned — and it does not change the answer* — 35 s · **11:20**
**On screen.** `fig11_tuning` — paired tuning deltas with drive-level bootstrap intervals.

**What it represents.** A pre-emptive answer to the standard objection, settled by measurement rather than argument. The structure matters: they gain a lot, they still lose, and tuning slightly *hurt* the winner — which is what rules out "favourable defaults" as the explanation.

> **Say:** The obvious objection to that ranking is that I under-tuned the deep baselines. So rather than argue, I measured it — same number of trials, same objective, same folds, same seeds, for every model. They gain a lot: the Transformer picks up nought point one-oh-nine, the TCN nought point one-oh-two, both far outside their intervals. They still lose. No tuned sequence model reaches an *untuned* logistic regression. And here's the detail I'd point at: tuning cost LightGBM nought point nought two one. The winner got slightly worse. So its margin isn't an artefact of defaults that happened to suit it.

**If pressed.** *"Did you tune on the test fold?"* — No. The objective is mean inner-fold AUPRC at the 2-second horizon, computed inside the training folds only. Two seconds because it is the middle horizon, so nothing is tuned to an extreme.

---

## Slide 23 · *Leakage is architecture-dependent: a GRU inflates by 74%, logistic regression by 4%* — 35 s · **11:55**
**On screen.** `fig12_leakage` — the same models under grouped-drive versus random-row splitting.

**What it represents.** The result with the widest implication beyond this thesis, and the reason slide 6's audit matters. The key insight — and the reason it earns a slide — is that the inflation is not a constant offset. It is *differential*, so it reorders the leaderboard rather than just lifting it.

> **Say:** This one has implications past my own thesis. Same data, same models, same metrics — the only thing I change is grouped-drive splitting versus random-row splitting. The GRU inflates by seventy-four percent. Logistic regression by four. The mechanism is simple once you see it: these models use a ten-second window, so a randomly split row shares most of its own history with the training set — and the more memory an architecture has, the more it can exploit that. The uncomfortable consequence is that a published GRU result on a randomly split drive-test set reads as roughly double what grouped evaluation would give. And because the inflation is differential, it doesn't just raise the scores. It reorders them.

---

## Slide 24 · *A distribution-free bound on missed handovers, and what it costs to hold it* — 30 s · **12:25**
**On screen.** `m05_crc` — conformal risk control: 28 calibration drives, a threshold sweep, the certified threshold applied to unseen drives.

**What it represents.** The "with what guarantee" clause of the research question. The contribution here is narrow and precisely stated: not conformal prediction, which already exists in wireless, but the choice of **exchangeable unit** — the whole drive — and the campaign-design rule that follows from it. Say what is *not* yours first; it costs nothing and buys the room.

> **Say:** The last clause of my research question was "with what guarantee". This is it — conformal risk control, which certifies a threshold on held-out drives so the miss rate on future drives stays below a target you choose. I want to be careful about what's mine, because conformal prediction is already in wireless: Cohen in 2022, Simeone in 2025. What's mine is the exchangeable unit. Their guarantees hold over samples independent within a frame; mine holds over whole drives, because that's the only unit this data is exchangeable in. And that choice has a consequence you can design a campaign around — with n calibration drives, the tightest target you can even express is one over n minus one. Twenty-eight drives put my floor at three point four percent.

---

## Slide 25 · *The guarantee is affordable above a 15% miss rate and expensive below it* — 35 s · **13:00**
**On screen.** `fig14_riskcontrol` — the certified alarm rate and the realised miss rate against the target α, usable operating point circled.

**What it represents.** The price of the guarantee, published as a frontier rather than as one flattering point. This is where the thesis is most visibly *not* selling something, which is exactly why it builds credibility rather than costing it.

> **Say:** And here's what it costs, published as a whole frontier rather than the one point that flatters me. Read the maroon curve as the price. At a twenty percent target — meaning you accept missing one handover in five — the certified threshold alarms on twenty-three percent of samples, actually misses twelve point six, and the bound holds on eighty-two percent of test drives with slack everywhere else. That's an operating point a network could run. Go down to a five percent target and the alarm rate is sixty-one percent, which is a guarantee nobody would deploy. I'd rather state that than imply a distribution-free bound is free. It isn't.

---


---

## Slide 26 · *A fourth capture, a new corridor, twice the speed — and the same result* — 35 s · **13:35**
**On screen.** `fig25_capture_transfer` — leave-one-capture-out: each capture held out whole, predicted by a model trained on the other three.

**What it represents.** The strongest generalisation evidence in the thesis, and the pre-emptive answer to the scale objection. This slide *used to sit in Act II*, where it quoted 0.933 before the board had ever seen 0.933. Here it lands properly: the headline is already known, and this shows it survives a corridor and a speed regime the model had never seen.

> **Say:** The fourth capture deserves its own slide, because it was driven *after* the model was frozen, on a corridor the model had never seen, at twice the speed. Two results. Adding it moved pooled AUROC by exactly zero — nought point nine three three before, nought point nine three three after. And the stronger one: hold that highway capture out *whole*, train on the other three, and it comes back at nought point nine two seven, with the highest lift and the lowest calibration error of all four. A model that has never seen a highway predicts one. There's a nice physical detail underneath, too: 159 radio-link re-establishments in the dense urban core, five on the highway, because out there the macro layer overlaps smoothly and the link simply survives.

---

## Slide 27 · *Real-to-real transfer holds, and the model matches an independent dataset's own ceiling* — 35 s · **14:10**
**On screen.** `fig15_transfer` — transfer across captures, to a public dataset, and across A3 configuration regimes.

**What it represents.** External validity on three axes of increasing difficulty, ending on the strongest single comparison in the thesis: on a public dataset collected by other people, the model scores *above that dataset's own in-domain ceiling*. The last line is deliberately the one that costs you — end on the limitation, not the win.

> **Say:** Three transfer tests, getting harder. Across my own captures, with nothing shared — no drives, no routes, no cells, not even the scaler — AUROC holds between nought point eight eight and nought point nine three. Out of domain, on a published dataset collected by other people on a different campaign, I get nought point seven five two, and that dataset's *own* in-domain ceiling is nought point seven four five. So I'm not degrading; I'm reaching what that data supports. And the one that costs me: transfer across A3 configuration regimes loses nought point oh eight eight, and conditioning on the measured A3 parameters recovers none of it. Configuration is a real domain boundary and I can't feature-engineer past it.

---

## Slide 28 · *Both zero-cost domain adaptations make transfer worse, not better* — **HIDDEN**
**Why hidden.** Appendix C (slide 47) is this slide with the arms broken out. Jump there if asked *"why didn't you try domain adaptation?"* — and the answer is that you did, twice, and both lost on both sides of the transfer, including matched-domain accuracy, which rules out a robustness trade.

---


---

## Slide 29 · *The quantity the deployed rule thresholds on is the weakest predictor available* — 35 s · **14:45**
**On screen.** `fig17_mechanism` — single-feature AUROC at 1 second, ranked.

**What it represents.** The mechanistic payoff and the most quotable finding in the thesis: the network triggers on the A3 gap, and the A3 gap is nearly the *worst* single predictor in the feature set. Dwell time — how long the phone has already been camped — beats it outright. The closing sentence sets up the next slide, so do not pause after it.

> **Say:** This is my favourite slide, and it's one number against another. Score every feature on its own and the winner is dwell time — simply how long the phone has already been sitting on this cell — at nought point eight seven four. The A3 gap, the exact quantity the network thresholds on to decide to hand over, scores nought point five six six. Barely above a coin flip. It isn't a paradox once you see why: the gap condition is *necessary*, but nowhere near sufficient. It holds on twenty-seven percent of samples — and three in five of the reports it produces get declined by the network anyway. Which is worth a slide of its own.

---

## Slide 30 · *Three in five A3 reports are declined, and most of all on the highway* — 30 s · **15:15**
**On screen.** `m09_conversion` — 7,385 A3 reports, the two-second conversion decision, and the per-capture decline rates.

**What it represents.** The proof of the previous slide's "necessary but not sufficient", and a task the signalling makes visible that the literature has barely looked at: not *will a handover happen*, but *will the network act on a report it has just been sent*. The per-capture ordering is the intuitive part — decline rate rises with cell size.

> **Say:** Of seven thousand three hundred A3 reports, sixty-three percent are never acted on within two seconds. The network is told the condition is met, and does nothing. And the rate is orderly: fifty-seven percent on the urban arterial, sixty-three in the dense core, seventy-two on the highway. It rises with cell size, which makes physical sense — wide cells satisfy the entering condition early, and the network can afford to wait. Ghoshal's group report sixty-nine to eighty-seven percent non-conversion across three US operators. They don't state their report set or window, so I'd call that directionally consistent rather than a replication.

---

## Slide 31 · *Handovers are strongly self-exciting: six in ten follow another handover* — 30 s · **15:45**
**On screen.** `fig18_hawkes` — the fitted intensity and the branching ratio with its interval.

**What it represents.** The formal version of the clumping seen on slide 13. Note the care in the last line: the exponential kernel is *rejected* by a residual test, and the branching ratio is presented as a calibrated measure of clustering strength under a stated kernel — not as a generative claim about the network. Saying that yourself is worth more than surviving being asked.

> **Say:** Back to the clumping from the map. Fit a self-exciting point process and the branching ratio comes out at nought point six-oh-five — about six in ten handovers triggered by a previous handover rather than arriving on their own. That's stable across all four captures and both mobility regimes, and it decisively rules out a Poisson process and a renewal process. Now the honest part, because someone will check: the exponential kernel I fitted is itself rejected by an Ogata residual test. So I don't claim this is how the network generates handovers. I claim nought point six is a calibrated measure of how strongly they cluster, under a kernel I've named.

---

## Slide 32 · *The same 938 handovers give a ping-pong rate anywhere from 24.5% to 41.3%* — 30 s · **16:15**
**On screen.** `fig23_pingpong_definitions` — four rates, one fixed event set.

**What it represents.** A methodological finding that costs nothing to defend, because it is pure arithmetic on a fixed event set. Three definition choices are almost never stated in the ping-pong literature, and each moves the number by several points — so published rates are not comparable with one another. This is where you cash in the "a quarter" you planted on slide 13.

> **Say:** A quarter of handovers are ping-pongs — I said that earlier, and I want to show you how soft that number is. Same 938 handovers, four definitions, four answers: twenty-four and a half, twenty-nine, thirty-eight and a half, forty-one point three percent. Every one is correct arithmetic. They differ on three choices people rarely state. Identify a cell by PCI alone or PCI plus carrier — four and a half points, because there are six carriers here and PCIs repeat across them. Must the return be immediate — nine and a half points, because handovers come a median of three and a half seconds apart. My thesis quotes the top row and states all three choices beside it. And the finding is that published ping-pong rates aren't comparable. That's a result, not a grievance.

---

## Slide 33 · *Ping-pong is one carrier layer and one A3 profile, not speed* — 35 s · **16:50**
**On screen.** `fig24_pingpong_mechanism` — ping-pong rate by carrier relationship, by A3 profile, and by mobility regime.

**What it represents.** The answer to the obvious follow-up — *why is it so high?* — and it is an answer with an actionable lever in it. The intuitive explanation, speed, is explicitly tested and rejected, which is what makes the real explanation persuasive rather than merely asserted.

> **Say:** So why is it that high? It isn't mysterious, and it isn't what you'd guess. Split by carrier: a handover that stays on its own carrier ping-pongs at thirty-one percent; one that changes carrier, at six and a half. Five times. Split by configuration and it concentrates into a single profile — a plus-one-dB offset with a 320-millisecond time-to-trigger, which covers seventy-two percent of all handovers and returns twenty-nine percent of them. Now the guess everyone makes: speed. I checked. The highway returns thirty-one point one percent — the same. So it isn't mobility. It's a short time-to-trigger on a dense intra-frequency layer, and that time-to-trigger is a parameter someone can change on a Monday morning.

---


---

## Slide 34 · *A warning earns its alarm budget only up to about 20% of samples* — 30 s · **17:20**
**On screen.** `fig20_benefit` — excess coverage over a same-rate random alarm, by alarm budget.

**What it represents.** The operational reading, with the correct reference class. Coverage alone always flatters; measured against a random alarm firing at the same rate, the benefit shrinks by two-thirds at a 10% budget. This slide also carries a refuted prediction of your own, which is worth saying out loud rather than leaving on the slide.

> **Say:** What is a warning worth? Coverage on its own always flatters you, so the reference here is a random alarm firing at the same rate. Against that reference the benefit is real up to about a twenty percent alarm budget, then flattens. Without the reference I'd have overstated it by two-thirds at a ten percent budget. And there's a refuted prediction of my own on this slide that I'd rather state than bury: I expected a dedicated ping-pong predictor to be valuable. It scores nought point five one. Chance. The reason is almost obvious in hindsight — every ping-pong is a handover, and handovers are far more predictable than the subset. The general model already has it.

---


# PART 4 — What has been achieved?

---

## Slide 35 · *The nearest published method on this network scores 0.489 where this work scores 0.921* — 35 s · **17:55**
**On screen.** `m10_departmental` — the reimplemented departmental baseline, arm by arm.

**What it represents.** The only genuinely fair head-to-head available: same operator, same city, same instrument, reimplemented rather than quoted. The middle arm is what makes it an argument about *method* rather than about data — and the reward-versus-agent detail is the memorable one.

> **Say:** The closest prior work on this exact network — same operator, same city, same instrument — is a reinforcement-learning handover agent. I reimplemented it rather than quoting it, and scored it generously, on the rows its own dataset always has. It reaches nought point four eight nine. This work reaches nought point nine two one. But the arm in the middle is the point: give *my* learner only *their* five features and it gets to nought point seven six six. So their inputs are informative — the gap is the method, not the data. And one detail I found hard to look away from: their own hand-written reward function scores nought point six two four, higher than the agent trained on it. The reinforcement learning is subtracting from what the reward already knew.

---

## Slide 36 · *The two comparisons with the literature that are actually fair* — 25 s · **18:20** · **[optional]**
**On screen.** `fig26_literature_headtohead` — reimplementation left; the accuracy trap right.

**What it represents.** The comparison rule this thesis holds itself to: compare by reimplementation or by protocol, never by quoting numbers across datasets. The right-hand panel is the proof that quoting across datasets is meaningless here — a model that always says "no" scores 93.3% accuracy.

> **Say:** Two fair comparisons exist, and I'd like to name the rule I followed. On the left, reimplementation — same rows, same protocol. That's fair. On the right, why quoted numbers aren't: on my data a model that always says "no handover" scores ninety-three point three percent accuracy. Its precision–recall is six point seven. Seven of the twenty-two papers I audited quote accuracy on an imbalanced task. So I never compare across datasets in this thesis — only by reimplementation, or on protocol.

---

## Slide 37 · *Every method here is borrowed on purpose; what is new is where each one is pointed* — 30 s · **18:50**
**On screen.** `fig28_novelty` — six rows: component, borrowed from, what is new here.

**What it represents.** The novelty claim, made in the safest possible form: state the provenance first, in the left two columns, and let the right column be what is left over. A board that has been waiting to ask "what is actually new here?" gets the answer before it asks, with citations attached.

> **Say:** Let me answer the question the room has been holding. Nothing in this thesis is invented — every component is on the left, with its primary source. A discrete-time survival model. Conformal risk control. A Hawkes process. Grouped cross-validation. Signalling decoding. CORAL. What is new is the right-hand column, which is where each one is pointed. Survival analysis aimed at handover, so the horizons are coherent by identity. A conformal guarantee whose exchangeable unit is the drive, which produces a campaign-design rule. A branching ratio for handover arrivals, residual-tested. And a measurement of what grouped splitting is worth on drive-test radio, which turns out to be between four and seventy-four percent depending on the architecture. Borrowing well is a contribution when the pairing is new and the protocol is honest.

---

## Slide 38 · *Objectives, evidence, and the boundary of each claim* — 35 s · **19:25**
**On screen.** A three-column table closing O1–O5: **Objective** · **Evidence delivered** · **Status and boundary**, plus a sixth row for network benefit marked *(not claimed)*.

**What it represents.** The payoff of slide 9, and the most persuasive slide in the deck — not because the results are new here, but because the board can audit the promise against the delivery in one view. The sixth row is deliberate: listing what you did **not** achieve, in the same table and the same format, is what makes the other five rows credible.

> **Say:** Back to the five objectives, with the evidence and the boundary of each. O1, multi-horizon prediction: five horizons, precision–recall nought point seven eight four at one second, eleven point seven times the floor — met, on 57 drives and one operator. O2, the benchmark: seven learners, grouped rotation over five seeds, an equal tuning budget, and the leakage study — met, though the tuned arm is still a three-capture run and I will say so. O3, usable probabilities: zero coherence violations against forty-four percent, and a certified per-drive bound — met, under per-drive exchangeability, which is stated. O4, generalisation: leave-one-capture-out between nought point nine-one and nought point nine-five — met, as a four-point design rather than a large sample. O5, mechanism: dwell time at nought point eight seven against the A3 gap at nought point five seven. And the last row is the one I did not achieve: network benefit. I have a counting upper bound, not a controlled intervention, and the reason is on the limitations slide.

---

## Slide 39 · *More information and more machinery did not help; formulation and configuration did* — 30 s · **19:55**
**On screen.** `fig22_negatives` — six measured negatives above the line; three things that moved the result below it.

**What it represents.** The synthesis, and the slide that carries the thesis's character. Every row above the line was added in good faith, measured, and reported as nothing — which is precisely what gives the three rows below the line their weight. Deliver the list fast; the rhythm is the argument.

> **Say:** Let me put the whole thing on one slide. Above the line, six things I added expecting them to help. Tripling neighbour coverage: nothing. Explicit self-excitation features: nothing, even though the self-excitation is real. The full signalling block: half a point. A dedicated ping-pong target: chance. Domain adaptation: worse. An equal tuning budget: same ordering. Every one of those was measured, not assumed — which is the only reason the pattern is worth stating. Below the line, three things did move it: reformulating the target as a hazard, the configuration regime, and grouping the split by drive. More information didn't help. Formulation and protocol did.

---


---

## Slide 40 · *What this work cannot claim* — 30 s · **20:25**
**On screen.** Five limitations, each paired with the measurement that bounds it.

**What it represents.** The slide that most reliably decides how the Q&A goes. Every limitation here is stated *with a number attached*, which turns each one from a weakness into evidence that you know the size of your own uncertainty. Deliver it at normal pace and without apology.

> **Say:** What this doesn't claim. Scale: 57 drives, one operator, four days. Enough for grouped cross-validation with 57 bootstrap groups and a four-point leave-one-capture-out design; not enough to claim generality across cities or operators, and I don't. Sampling rate: one hertz caps *event detection* at ninety and a half percent — it does not cap horizon resolution, for the reason I gave earlier. Cross-regime transfer rests on a single regime pair, because only two A3 profiles clear the sixty-handover bar on an identical test set. There's no causal estimate of the actuator, and I can tell you exactly why rather than apologising: the logging policy is deterministic — A3 either fires or it doesn't — so off-policy evaluation is unidentified here. And the Hawkes kernel is misspecified. I put that in the thesis rather than leaving it for a reviewer to find.

---

## Slide 41 · *Four directions, and one of them makes the causal question identifiable* — 25 s · **20:50**
**On screen.** Four future-work items, the first a fuzzy regression-discontinuity design at the A3 boundary.

**What it represents.** Future work specific enough to be a plan. The first item matters most: it is the identifiable alternative to the causal estimate the previous slide just ruled out, so slides 40 and 41 answer each other. Say "closes the hole I just admitted to" — it lands.

> **Say:** Four directions, and the first closes the hole I just admitted to. Because A3 has a sharp boundary, a fuzzy regression-discontinuity design compares drives just inside and just outside the firing condition — that's the identifiable route to the causal effect that off-policy evaluation can't give me. Second, one more capture on a new route turns a single regime pair into a matrix. Third, connect the two-second warning to a measured throughput or interruption effect rather than a counting bound. And fourth, release the code and the data: two of the twenty-two papers I audited release code, one releases data, so a release is a citable contribution in its own right.

---

## Slide 42 · Conclusions — 35 s · **21:25**
**On screen.** Four numbered conclusions.

**What it represents.** The landing. **Leave this slide up for the whole Q&A** — it is the frame you want the board arguing inside. Say all four, do not read them.

> **Say:** Four conclusions. One: handover is predictable well ahead of the rule that causes it — nought point nine three three AUROC and nought point seven eight four precision–recall at one second, nearly twelve times the floor, with calibrated probabilities and a per-drive guarantee, and unchanged when a highway capture was added afterwards. Two: formulation beat information. One hazard fit gave coherence, calibration and ranking together; five separate information channels gave nothing. Three: the protocol is as much the contribution as the model — grouped splits, a prevalence floor, event-level costs, a distribution-free bound, none of which the comparable literature reports. And four: the negative results were measured and published rather than discarded, including one prediction of my own that turned out to be wrong. Thank you.

---

## Slide 43 · References — 5 s · **21:30**
**On screen.** Sixteen primary references in two columns, screening counts at the foot.

**What it represents.** Evidence of the survey's scale, on screen for one beat. Do not read it.

> **Say:** Primary sources are here; the full bibliography is a hundred and eight screened references, ninety-three verified against the publisher record.

---

## Slide 44 · Thank you — 10 s · **21:40**
**What it represents.** The handover to the board. Advance **back to slide 42** as soon as questions begin.

> **Say:** Thank you — I'm happy to take questions.

---

> **Clock check.** Full: **21:40**. 20-minute configuration (hide 8, 15, 36; trim 11, 12, 13, 34, 39): **19:35**. 18-minute configuration (also hide 12, 31, 32, 41): **17:50**. Slides 21 and 28 are hidden in every configuration.

---

# Appendix slides — what each is for

Eight pre-built answers. Learn the **slide numbers** so you can jump straight there instead of talking around the question.

| # | Appendix | On screen | Jump here when asked |
|---|---|---|---|
| **45** | A — Configuration-timeline defect | `fig07_config_timeline` — A1/A2/A3 configuration counts in one capture | *"How do you know the flat parse was wrong?"* → 43% of reports carry no neighbour, so 99.4% A3 attribution is arithmetically impossible. |
| **46** | B — The hazard identity | `fig08_hazard_concept`, panel by panel | *"Why not just calibrate five heads?"* → Calibration is per-horizon; nothing couples the horizons. The product-limit identity couples them before any calibration is applied. |
| **47** | C — Domain adaptation | `fig16_adaptation` — per-drive z-scoring and CORAL, arm by arm | *"Did you try domain adaptation?"* → Twice, both unsupervised and free at deployment. Both lose on both sides, and matched-domain AUROC falls too, which rules out a robustness trade. |
| **48** | D — Report conversion | `fig19_conversion` — decline rate pooled and per capture | *"Isn't report conversion just the A3 rule restated?"* → No. The gate is satisfied for every one of these reports, and three in five are still declined. |
| **49** | E — The departmental comparison | `fig21_departmental` — every arm of the reimplementation | *"Is that comparison fair?"* → Every choice was made in their favour. And their published TTT filter consumes TTT seconds of the future, so it is inadmissible as evidence of prediction. |
| **50** | F — The 18-stage pipeline | `m01_pipeline` — the stage graph, with the grouping guard in the split constructor | *"Is this reproducible?"* → A rebuild from the raw captures returns 10,260 samples and 938 handovers exactly. 17 passing tests, and no number typed by hand. |
| **51** | G — The four-literature map | `m11_litmap` — measurement, prediction, survival and conformal, converging on an empty centre | *"Has nobody really done this?"* → Four mature literatures come close. Survival and point processes have never been aimed at a drive test; conformal entered wireless for i.i.d.-within-frame tasks. |
| **52** | H — Two narrowed claims | The conformal claim and the grouped-split claim, both made smaller | *"Isn't conformal prediction in wireless already done?"* or *"Surely somebody splits by group?"* → Both answers are written out here, already narrowed. |

---

# The six questions most likely to come, and one-breath answers

**1. "Fifty-seven drives is small."**
Agreed, and I've bounded it rather than argued about it. Every interval in the talk is a bootstrap over drives, and the leave-one-capture-out design gives four independent generalisation tests. The highway one — a corridor and a speed regime the model had never seen — comes back at nought point nine two seven. *(Slide 26.)*

**2. "Why not deep learning?"**
I ran them, tuned them on an equal budget, and reported that they gained a lot and still lost. On 57 drives there isn't enough data for them to learn anything the tabular features don't already carry — a statement about my sample, not their architectures. And the leakage slide shows they're also the models most inflated by a careless split. *(Slides 22 and 23.)*

**3. "Isn't AUROC 0.933 too good?"**
It's the number that made me build the leakage experiment. Under grouped-drive splitting it's nought point nine three three; under random-row splitting the same pipeline gives a higher number I don't believe. And the reason it's high is on the mechanism slide — dwell time alone reaches nought point eight seven four. Most of the signal is in how long you've been camped, not in anything exotic. *(Slides 23 and 29.)*

**4. "What would an operator actually do with this?"**
At a twenty percent target the certified threshold alarms on twenty-three percent of samples and misses twelve point six percent of handovers — a real operating point. And separately from prediction, the ping-pong analysis points at one parameter, a 320-millisecond time-to-trigger on the intra-frequency layer, that accounts for most of the returns. *(Slides 25 and 33.)*

**5. "Is any of this novel, given you borrowed every method?"**
Every component has a primary source and I say so. What's new is where they're pointed: a discrete-time hazard on handover, conformal risk control whose exchangeable unit is the *drive*, and a protocol audit of 22 papers that none of them satisfies. Borrowing well is a contribution when the pairing is new and the protocol is honest. *(Slide 48.)*

**6. "Why is the ping-pong rate so much higher than published figures?"**
Partly because it genuinely is — this is a dense intra-frequency layer with a short time-to-trigger. But mostly because "ping-pong rate" isn't one definition. The same 938 handovers give anything from twenty-four and a half to forty-one point three percent depending on three choices papers rarely state. I state all three next to my number. *(Slides 32 and 33.)*

---

*Every number here is a four-capture value and matches the deck slide for slide. If a figure is regenerated, re-check the script line that quotes it.*

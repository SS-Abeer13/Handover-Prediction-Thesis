# Defence slide bible

### Every slide, everything on it, every number's source, and the answer to every question it invites

**Deck:** `Handover-Thesis-Defence.pptx` — 49 slides
**Companion:** `Thesis_Defence_Presentation_Script.docx` (what to *say*). This document is what to *know*.

---

## How to use this

The script tells you what to say in 17 minutes. This tells you what stands behind every word of it. Each slide gets six things:

| Section | What it gives you |
|---|---|
| **The claim** | The single sentence the slide exists to establish. If you remember nothing else about a slide, remember this. |
| **On screen** | Every element of the figure, so you can point at things instead of gesturing vaguely. |
| **Every number** | Each figure on the slide, what it means, and which section of the thesis produced it. |
| **The reasoning** | Why the result is what it is — the mechanism, not the measurement. This is what separates an answer from a recital. |
| **If the board asks** | The questions this slide actually invites, with the exact answer. |
| **Do not say** | The overclaim that would get you into trouble on this slide. Usually there is exactly one. |

**Read Part 0 and Part 3 the morning of the defence.** Part 0 is the number card. Part 3 is where the thesis is genuinely soft, and the prepared answer for each — that is the part that decides whether you get stuck.

**The single most important habit:** when you do not know, say what measurement would settle it. "I haven't measured that. The experiment would be *X*, and I'd expect *Y* because *Z*." That answer is never wrong, and this thesis is built so that you always have one.

---

# PART 0 — The number card

Learn these cold. Everything else can be derived or looked up on a slide.

### The dataset

```
4 captures · 57 drives · 10,260 samples at 1 Hz · 938 handovers · ~2.9 h · ~95 km
```

| capture | corridor | samples | drives | handovers | duration | re-establishments |
|---|---|---|---|---|---|---|
| 10 Sept | urban arterial | 2,700 | 15 | 290 | ~46 min | 113 |
| 12 Sept | urban loop | 1,440 | 8 | 174 | ~24 min | 64 |
| 13 Sept | dense urban | 3,600 | 20 | 297 | ~60 min | 159 |
| **15 Sept** | **Uttara→Gazipur highway** | **2,520** | **14** | **177** | **~43 min** | **5** |

**957 vs 938.** The parser finds 957 handovers in the raw logs. 938 fall inside a drive that passes quality control (≥ 60 s, ≥ 60 samples) and are the set every model is scored against. Both are right; they answer different questions. **Always say which one you mean.**

### The features

```
152 columns built · 107 used · RF 83 · mobility 17 · history 7 · signalling 13
```

Robust scaler (median and IQR, clipped at ±8), fitted per fold on training rows only. Every window backward-looking and closed at *t*; report counts stop at *t − Δ*, because a report precedes its handover command by 50–200 ms — inside one sample.

### What the reactive rule costs, counted

```
938 handovers in 2.9 h · 24.5% ping-pong · 341 re-establishments · 4,645 declined A3 reports
```

### The headline

| | |
|---|---|
| **LightGBM, 1 s horizon** | AUPRC **0.784** [0.740, 0.826] · lift **11.7×** · AUROC **0.933** · ECE **0.024** · Brier 0.026 |
| prevalence at 1 s | **6.7%** |
| event level at 1 s | 44.7% of handovers detected · 63.9 false alarms/h · 1.79/km · median lead 0.46 s |
| event level at 5 s | 65.1% detected · 41.6 false alarms/h · 1.17/km · median lead 1.80 s |
| instrument ceiling | **90.5%** of events are detectable at all on a 1 Hz grid |

### Prevalence by horizon

| horizon | 0.5 s | 1 s | 2 s | 3 s | 5 s |
|---|---|---|---|---|---|
| prevalence | 3.7% | **6.7%** | 12.5% | 17.5% | 25.9% |
| LightGBM AUPRC | 0.416 | **0.784** | 0.627 | 0.598 | 0.606 |
| lift | 11.3× | **11.7×** | 5.0× | 3.4× | 2.3× |
| AUROC | 0.916 | **0.933** | 0.854 | 0.816 | 0.783 |
| ECE | 0.023 | **0.024** | 0.061 | 0.091 | 0.141 |

### The deployed configuration (measured, not assumed)

| A3 profile | share of handovers | fires when the gap is below |
|---|---|---|
| **Off +1 dB, Hys 1 dB, TTT 320 ms** | **74.6%** | −2 dB |
| Off −10 dB, Hys 2 dB, TTT 640 ms | 13.1% | +8 dB |
| Off −15 dB, Hys 1 dB, TTT 160 ms | 7.7% | +14 dB |

Two offsets are **negative** — the network hands over while the neighbour is still *weaker*. Published work on this network had assumed +3 dB.

### The five numbers most likely to be challenged

| number | what it is | the one-line defence |
|---|---|---|
| **0.933** | AUROC at 1 s | Grouped by whole drive. Under random-row splitting the same pipeline gives a higher number I don't believe — that's slide 23. |
| **11.7×** | lift over the prevalence floor | AUPRC 0.784 against a 6.7% floor. Lift is always reported *beside* AUPRC, never instead of it. |
| **43.6%** | multi-head coherence violations | Rows where P(≤1 s) > P(≤3 s). Four-capture re-run; it was 47% on three. |
| **24.5%** | ping-pong rate | A→B→A, cell = PCI + carrier, 15 s window. All three choices stated — slide 32 shows what each is worth. |
| **0.605** | Hawkes branching ratio | A calibrated measure of clustering under a stated kernel. The kernel is rejected by an Ogata test and I say so. |

---

# PART 1 — Slide by slide

---

# ACT I — The problem and the gap

---

## Slide 1 · Title
**The claim.** None. This is the frame.

**On screen.** Title, the subtitle *"How far ahead can the next LTE handover be seen, and with what guarantee?"*, your name, student ID, supervisor, department (EEE, Islamic University of Technology, Gazipur), and the defence date.

**⚠ Before the defence:** fill in `[ID]`, `[Supervisor Name, Title]`, `[Date]` and `[email]` on slides 1 and 42.

**Why it exists.** The subtitle is the thesis in one sentence, and it is deliberately a question with three parts — *how far ahead*, *how well*, *with what guarantee*. Slide 8 unpacks all three, and Acts III–V answer one each.

**If the board asks:** *"Why 'uncertainty-aware'?"* — Because the deliverable is not a label, it is a calibrated probability with a distribution-free bound attached. Two of the four conclusions are about the uncertainty rather than the accuracy.

---

## Slide 2 · Defence roadmap
**The claim.** None. This is the promise: four questions, and every slide belongs to one of them.

**On screen.** *01 Why this problem? · 02 What was developed? · 03 What does the evidence show? · 04 What has been achieved?*, each with a one-line expansion, over a takeaway strip.

**Why it exists, and why here.** A board listening to a twenty-minute talk needs a frame in the first minute or it spends the rest of the talk building one. The four questions are the conventional shape of a thesis defence, so they cost nothing to explain, and the breadcrumb in the corner of every later slide names which part you are in. It replaces the narrative diagram this deck used to open with, which showed the same structure with more ink and less legibility.

**The reasoning.** The four questions are not decorative — they map onto the four things a board is actually deciding: *is the problem real*, *is the method sound*, *is the evidence sufficient*, and *does the candidate know what they have and have not shown*. Part 4 is the one most decks under-serve, which is why it has five slides here, including the achievements table and the limitations.

**If the board asks:** *"How long is each part?"* — Roughly four minutes on the problem, four on the method, eight on the evidence, and five on what it adds up to. The evidence section is the longest because that is where the contributions are.

---


# PART 1 — Why this problem?

---

## Slide 3 · *LTE hands over with a rule that acts only after the radio has already changed*
**The claim.** Event A3 is structurally reactive, so there is a predictable interval between "a handover is now inevitable" and "the network acts".

**On screen.** `fig01_a3_event`. Two RSRP traces — serving (falling) and neighbour (rising) — crossing. Marked on the figure: the **entering condition** (the point where the neighbour exceeds the serving cell by the offset plus hysteresis), the **time-to-trigger window** shaded after it, and the **handover command** at the far end. The curves are illustrative; the parameters on them are the deployed ones.

**Every number.**

| number | meaning | source |
|---|---|---|
| +1 dB offset, 1 dB hysteresis, 320 ms TTT | the dominant deployed A3 profile — 74.6% of handovers | MASTER §4.4, read out of `measConfig` |
| gap < −2 dB | what that profile's entering condition actually means | §4.4, §20 Panel A |

**The reasoning.** 3GPP TS 36.331 defines A3's entering condition as `Mn + Ofn + Ocn − Hys > Mp + Ofp + Ocp + Off` — the neighbour must beat the serving cell by a margin, *and* keep beating it for the whole time-to-trigger, before a measurement report is even sent. The network then decides. So three things sit between "the radio has changed" and "the handover happens": the margin, the TTT, and the network's decision. The rule cannot be early; being late is the design.

This is not a criticism of A3. A rule that fires *at* the handover is doing its job. It just means the rule is not a predictor, which is what slide 29 measures directly.

**If the board asks.**

- *"Isn't the TTT there precisely to avoid ping-pong?"* — Yes, and that is exactly why the number matters. This network runs 320 ms on the profile that carries 72% of handovers, which is short. Slide 33 shows that profile returning 29.2% of its handovers to the previous cell, against 10.5% for the 640 ms profile. The TTT is the anti-ping-pong mechanism and it is set too low here.
- *"Why not just make A3 predictive by lowering the offset?"* — You can shift *when* it fires, but you can't make it anticipatory: it is a function of the current gap, and the current gap is a poor predictor — AUROC 0.566, slide 29. Lowering the offset trades lateness for false handovers.
- *"Are these the real curves?"* — The curves are drawn for legibility; the parameters on them are measured from this network's own `measConfig` messages. Appendix A (slide 45) shows the configuration counts in the raw log.

**Do not say** that A3 "fails" or is "broken". It does what it is specified to do. The claim is that it is reactive, which is a statement about its definition, not its quality.

---

## Slide 4 · *The cost is measurable, and the predictor does not exist*
**The claim.** The reactive rule is expensive **on this network, in counted quantities**, and nobody has built the alternative.

**On screen.** `fig27_necessity`, two columns divided by a rule. **Left — what the reactive rule costs, counted on these 57 drives:** 938 handovers · 24.5% ping-pong · 341 RRC re-establishments · 4,645 declined A3 reports, each with a one-line gloss. **Right — and nobody has built the predictor:** three "0 of 22" rows from the protocol audit, under a maroon box reading *the measurement exists in the signalling; nobody has pointed a predictor at it.*

**Every number.**

| number | meaning | source |
|---|---|---|
| **938** in 2.9 h | one handover every ~11 s; median gap 3.5 s | §3, §22 |
| **24.5%** | ping-pong: A→B→A, cell = PCI + carrier, 15 s window — 230 of 938 | §22 |
| **341** | RRC re-establishments: 113 + 64 + 159 + 5 across the four captures | §3, report 25 |
| **4,645** | A3 reports never acted on within 2 s — 62.9% of 7,385 | §20 |
| **0 / 22** ×3 | papers holding out the mobility unit · reporting calibration · reporting lead time or false-alarm rate | §25 |

**Why this slide exists, and why here.** It sits between the A3 mechanism (slide 3) and the research question (slide 8) because that is the exact point at which a board thinks *"fine, but does this matter?"*. The answer has to have two halves: a **cost**, and a **gap**. A cost with no gap is somebody else's problem — the operator's. A gap with no cost is a literature exercise. Together they are a thesis.

**The reasoning.** Every figure on the left is a count, not a model output and not an estimate, which is what makes the slide hard to argue with. And each one is a *different kind* of cost:

- **938 in 2.9 hours** establishes the rate. Handover is not a rare corner case on this network; it is the dominant mobility event, arriving a median 3.5 s apart.
- **24.5% ping-pong** is waste: the handover was unnecessary, and its cost — the interruption, the signalling, the context transfer — was paid twice.
- **341 re-establishments** is the severe tail: not a suboptimal handover but a link that actually failed. 159 of them in one dense-urban capture; five on the highway.
- **4,645 declined reports** is churn on the control plane: the phone measured, filtered and reported, and the network did nothing with it.

The right column is the gap in its narrowest, most defensible form. It is not "nobody has studied handover prediction" — plenty have. It is that of the 22 comparable papers, *none* meets the three protocol conditions under which a number would transfer.

**If the board asks.**

- *"Is 24.5% ping-pong actually high?"* — For a dense intra-frequency layer with a 320 ms time-to-trigger, it is what you would expect, and slide 33 shows exactly where it comes from. Whether it is high *compared with published figures* is a question I cannot answer honestly, because published rates use three unstated definition choices — that is slide 32.
- *"341 re-establishments — over what?"* — Over 57 drives and 2.9 hours. The distribution is the interesting part: 159 in the dense urban core against 5 on 34.6 km of highway.
- *"Aren't declined reports just the system working correctly?"* — Partly, yes, and I say so on slide 30: the network weighs load and target availability, and declining is often right. The cost is not that the network declines; it is that the phone cannot tell in advance, so it measures, filters and reports for nothing three times in five.
- *"Couldn't the operator just fix the configuration instead of predicting?"* — For ping-pong, yes, and that is the recommendation on slide 33 — a time-to-trigger change. Prediction and configuration are complementary: one anticipates the event, the other reduces how many bad ones occur.

**Do not say** that LTE handover is "broken" or that the operator is misconfigured. Say the rule is reactive by definition, that the cost of that is measurable, and that the measurement needed to do better is already in the signalling.

---

## Slide 5 · *Two literatures exist, and neither does what a deployable predictor needs*
**The claim.** Measurement studies have the ground truth and build no predictor; prediction studies build predictors without the ground truth or the protocol.

**On screen.** Two columns. **Left — measurement studies:** Deng et al. (IMC 2018), recovering operator mobility configurations from signalling; Ghoshal et al. (2025), handover configurations across three US operators, 48k handovers. Strength: measurement-grade ground truth. Gap: no predictor. **Right — prediction studies:** 108 references screened over three passes, 22 predicting handover / radio-link failure / next-cell occupancy. Strength: models and architectures. Gap: protocol, calibration, operating cost.

**Every number.**

| number | meaning | source |
|---|---|---|
| 108 | references screened across three passes | §25; 93 fully verified against the publisher or author record, 15 to re-check before submission |
| 22 | of the 108 that are learned or analytical models predicting handover, RLF or next-cell occupancy | §25 |
| 48k | handovers in Ghoshal et al.'s campaign | their paper, arXiv:2511.03116 |

**The reasoning.** The two literatures have opposite strengths because they have opposite costs. Signalling decoding is expensive and yields a few thousand events; simulation is cheap and yields millions of rows. So the people with the truth do not have the scale to train, and the people with the scale do not have the truth to train against. This thesis sits in the expensive corner and compensates with protocol rather than with volume — which is why the protocol is a contribution rather than housekeeping.

**If the board asks.**

- *"Why are those two the measurement studies?"* — They are the two that recover *configuration* from signalling, which is what makes them comparable to this work. Deng is the canonical one; Ghoshal is the most recent and the one this thesis independently replicates on report conversion (slide 30).
- *"Three passes — what changed?"* — Pass 1 was a competitor-driven search. Pass 2 widened it. Pass 3 (doc 22) added nine further threads: standards-track mobility, reviews of reviews, graph and trajectory models, conformal prediction in wireless, survival methodology, point-process methodology, domain adaptation, uncertainty estimation, and event-level evaluation. Two of my own claims got smaller as a result — appendix G.
- *"Have you missed a paper that does both?"* — Possibly, and I widened the survey twice looking for exactly that. What I can say is that after three passes and 108 references, the audit rows on the next slide did not move.

**Do not say** that the prediction literature is bad. Say that it answers a different question on different data, and that its protocol is unstated more often than it is wrong.

---

## Slide 6 · *Of 22 comparable papers, none splits by drive and none reports calibration*
**The claim.** The gap is a protocol gap, and it is measured rather than asserted.

**On screen.** `fig06_protocol_audit` — the 22 comparable papers scored against protocol criteria, with this work's column beside them.

**Every number.**

| protocol property | papers | this work |
|---|---|---|
| splits by **drive or route** | **0 / 22** | yes, every experiment |
| any split coarser than a random row | 5 / 22 | yes |
| states a split protocol at all | 12 / 22 | yes, with a freeze manifest |
| prevalence-aware **ranking** metric | 2 / 22 | AUPRC + floor + lift |
| calibration curve, ECE or Brier | **0 / 22** | ECE, Brier, temperature scaling, conformal risk control |
| lead-time distribution or false alarms/hour | **0 / 22** | yes, and per km |
| headline accuracy on an imbalanced task | 7 / 22 | never |
| releases code | 2 / 22 (+1 on request) | planned |
| releases data | 1 / 22 (+1 on acceptance) | planned |

The seven accuracy papers work at prevalences between **0.86% and 11%**, where a constant "no" scores 89–99%. Three of their headline figures are **98.03%, 99.84% and 94.83%**.

**The five exceptions, by name:** spatial zone (Mandapati) · device (Amirova et al.) · **time**, rolling-origin 5-fold (Hasan et al., 1.8 M samples of real operator data) · **travel day** (Dinh et al.) · **deployment event** (GRIMCELL, commercial LTE-A Pro).

**The reasoning.** The audit is on protocol, never on results, and that is a deliberate rhetorical choice as well as an honest one. Saying "their number is wrong" requires their data. Saying "I cannot tell whether their number is comparable" requires only their methods section — and is unanswerable.

There is also a structural finding underneath the table: **protocol quality and measurement quality are anti-correlated in this literature.** The papers with the cleanest splits work on ray-traced trajectories, SUMO traces over a real map, aggregated operator KPIs, or cell-and-day granularity. The papers carrying real per-sample drive-test radio — the ones whose data most resembles this — are exactly the ones whose split protocol is unstated. That is the hole this work sits in.

**If the board asks.**

- *"Isn't 'none splits by drive' unfair when most of them don't have drives?"* — That is precisely the point, and it is why the claim is worded as *the mobility unit* rather than *the drive*. A whole device-session counts. The narrow claim is: none holds out the mobility unit for a **per-timestep classification task on measured radio**. Hasan et al. has the strongest protocol in the set and its task is next-day cell-level RLF — a different granularity. The two pass-3 additions are regression tasks, where prevalence never arises.
- *"Aren't you cherry-picking the criteria?"* — The criteria were fixed before the audit and are the ones that determine whether a number transfers: how you split, what floor you read against, whether the probabilities mean anything, and what an operator would pay. The counting rules are in the thesis.
- *"Two independent reviews?"* — Yes, and neither is mine. Ankome and Hanada (PRISMA; 429 records, 336 after deduplication, 49 included, 2010–2025) could not run a meta-analysis at all because simulators and outcome definitions were too heterogeneous, and note that splitting, imbalance and calibration receive minimal explicit discussion in all 49. Asif et al. report that 82.6% of surveyed studies use simulated data. Both arrive at this conclusion from the other direction.
- *"Will this claim survive a fourth widening?"* — It has already narrowed twice and I say so. Pass 2 found one paper splitting by time; pass 3 found two more. If a fourth pass finds a per-timestep drive-test paper with a grouped split, the claim narrows again and the leakage result on slide 23 is unaffected — that result does not depend on scarcity, it depends on the inflation being real and differential.

**Do not say** "nobody does this properly". Say "of the 22 I audited, on these criteria, here is the count" — and be ready to name the five exceptions, because someone will ask and naming them instantly is worth more than the finding itself.

---

## Slide 7 · *Foundations: what is borrowed, and what for*
**The claim.** Every method in this thesis has a primary source, declared before the method is used.

**On screen.** Three columns — **Methodological strand** (with its source) · **The established idea** · **Role in this work** — over six rows.

**Every row.**

| strand | the established idea | role here |
|---|---|---|
| Discrete-time survival — Wiegrebe et al., 2024 | conditional event hazards | coherent cumulative probabilities from a single fit |
| Conformal risk control — Angelopoulos et al., 2024 | distribution-free expected-risk control | a warning threshold certified at a target miss rate |
| Wireless conformal prediction — Cohen 2022; Simeone 2025 | uncertainty inside wireless systems | shows the open question is the **exchangeable unit** |
| Self-exciting point process — Hawkes 1971; Ogata 1988 | event clustering, and residual testing of the fit | measures handover burstiness, with the kernel tested |
| Unsupervised adaptation — Sun and Saenko, 2016 | feature alignment without target labels | tried as a zero-cost transfer fix; reported as a negative |
| Signalling measurement — Deng 2018; Ghoshal 2025 | configurations recovered from decoded RRC | ground truth, and a deployed rule that is measured |

**Why it exists, and why here.** Related work owes a board two different things: *who else does the task* (slides 5 and 6) and *where the machinery came from*. This is the second, and putting it in Part 1 rather than the appendix is a deliberate rhetorical choice — **claiming provenance early is what lets the novelty slide claim something small and precise later.** A novelty claim made without this table sounds like an assertion; made after it, it sounds like arithmetic.

**The reasoning.** Read the third column and notice the shape: in every row the contribution is a matter of *where a mature method is aimed and on what unit*. Survival analysis is decades old — aiming it at handover is what buys horizon coherence. Conformal prediction is already inside wireless — choosing the drive as the exchangeable unit is what makes the guarantee an operator quantity. That pattern is the thesis, stated once, before any result.

**If the board asks.**

- *"Why is Cohen 2022 in a foundations table rather than a competitor table?"* — Because it is both, and I would rather concede it early. Their work is the reason my conformal claim is narrow: they got to wireless first, so what is left as mine is the exchangeability unit and the KPI, not the machinery. Appendix H has that written out in full.
- *"Two of these six rows produced negatives. Is that a foundation?"* — Yes, and deliberately. CORAL is in this table because a negative result is only credible if the method was implemented from its primary source rather than substituted for. Naming the source is part of the evidence.
- *"Is this table the same as the novelty slide?"* — They are the two halves of one argument. This one is *borrowed from*; slide 37 is *what is new*. Separating them by twenty minutes is intentional: the claim lands better once the evidence is in.

**Do not say** "we build on the literature" as a throwaway. Point at a row and name what it does.

---

## Slide 8 · *The question this thesis answers, stated once*
**The claim.** The research question, and the four standards it will be judged against.

**On screen.** A callout box with the question, then four clauses: *How well?* (against a prevalence-aware floor, never accuracy) · *How far ahead?* (0.5, 1, 2, 3, 5 s, kept mutually coherent) · *With what guarantee?* (a distribution-free per-drive bound) · *On what evidence?* (real drive-test data, handover truth from decoded RRC).

**Why it exists.** It is a contract. Each clause is a commitment you keep later: slide 19 keeps the first, slide 20 the second, slide 25 the third, slide 10 the fourth. Board members who write the question down will check it off, which is exactly what you want.

**The reasoning.** The four clauses are not decoration — each one rules out a standard failure mode in this literature:

- *Prevalence-aware* rules out "98% accuracy" on a 2%-prevalence task. Seven of the 22 audited papers do this (slide 6).
- *Mutually coherent* rules out five independent classifiers that contradict each other (slide 16).
- *Distribution-free* rules out a guarantee that depends on the model being right.
- *Decoded signalling* rules out a vendor event counter you cannot audit.

**If the board asks.**

- *"Why those five horizons?"* — 0.5 s is the shortest labelable horizon (the event clock is millisecond-precise; §6.4). 5 s is where prevalence reaches 26% and the task stops being rare-event. 1, 2 and 3 s fill the useful range for a network action. Tuning uses 2 s as the objective precisely because it is the middle one, so nothing is tuned to an extreme.
- *"What's the guarantee on, exactly?"* — The per-drive miss rate: the fraction of that drive's handovers the alarm misses. Not coverage of a prediction set. That choice is the contribution (slide 24).

---

## Slide 9 · *Five objectives, and where each one is answered*
**The claim.** The research question decomposed into five deliverables, each with the slide that delivers it.

**On screen.** O1 to O5, each a single sentence, each ending in the slide numbers that answer it.

**The objectives, and what each commits you to.**

| | objective | answered on | the commitment |
|---|---|---|---|
| **O1** | predict the next handover at five horizons from what a phone can observe | 14, 19 | a number read against its prevalence floor, not accuracy |
| **O2** | a benchmark a reviewer would accept | 18, 22, 23 | grouped by drive, equal tuning budget, and the cost of a bad split *measured* |
| **O3** | probabilities that are usable, not merely well ranked | 16, 20, 24, 25 | coherent across horizons, calibrated, bounded per drive |
| **O4** | generalisation beyond the training capture | 26, 27 | a whole corridor held out, and someone else's dataset |
| **O5** | explain the mechanism, not only the accuracy | 29 to 33 | what predicts, what the network does with a report, where ping-pong comes from |

**Why it exists, and why here.** This is the single most useful structural slide in the deck, and it only works as a **pair with slide 38**. Objectives early, achievements late: the board writes five things down at minute four and ticks them off at minute nineteen. It converts a talk from a sequence of results into a claim that can be audited, and it makes the limitations slide read as completeness rather than retreat.

**The reasoning.** Each objective is worded so that it *can fail*. "Predict handovers" cannot fail; "predict at five horizons, read against the prevalence floor" can. "Test robustness" cannot fail; "hold out a whole corridor and score on an independent dataset" can. Stating falsifiable objectives is what makes the achievements table on slide 38 worth anything, and it is why the sixth row there — the objective **not** met — belongs in the same table.

**If the board asks.**

- *"When were these objectives set?"* — Before the fourth capture was driven. That matters, and it is the reason the leave-one-capture-out result on slide 26 is a genuine out-of-sample test rather than a post-hoc selection: the feature set, the horizon set, the split rule and the model configuration were all frozen on the three urban captures.
- *"Isn't O5 unfalsifiable? 'Explain the mechanism' could mean anything."* — Fair, and it is the softest of the five. What makes it checkable is that it names specific quantities in advance: the single-feature ranking, the report-conversion rate, and the branching ratio. All three are reported with intervals or with a goodness-of-fit test.
- *"Where is the QoE objective?"* — Not an objective, because the captures carry PHY throughput but no application-layer RTT or loss. It is listed in the thesis limitations rather than promised here.

---


# PART 2 — What was developed?

---

## Slide 10 · *measId and reportConfigId are message-scoped, so a flat parse misattributes silently*
**The claim.** A defect in the signalling extraction was found, by comparison with a published method, and corrected — and it changed four claims, two of them this thesis's own.

**On screen.** `m02_signalling` — the configuration timeline: `measConfig` arrives incrementally, `AddMod` inserts or replaces an entry, and the timeline reconstructs the state in force at each report instant.

**Every number.**

| number | meaning | source |
|---|---|---|
| 99.4% | what a flat parse claimed was A3 | §4.2 |
| 43% | share of measurement reports carrying no neighbour at all — which makes 99.4% impossible | §4.2 |
| four claims changed | two of them this thesis's | §4.2 |
| offsets are −15, −10, +1 dB | the measured truth, against +3 dB assumed in published work on this network | §4.4, §25.1 |
| 310/310 | parser agreement with the vendor's own event counter on an independent public dataset | §3 |
| 62–79% | neighbour coverage after projecting reported neighbours onto the 1 Hz grid; median report age 0.36 s | §3 |

**The reasoning — this is the one to be able to explain from first principles.** In RRC, `measConfig` is **incremental**. A reconfiguration message does not restate the whole measurement configuration; it adds, modifies or removes entries. `measId` binds a measurement object (a frequency) to a report configuration (an event type and its parameters), and **both identifiers are only meaningful relative to the configuration state in force at that moment**. The same `measId = 1` can mean A2-on-carrier-A in one minute and A3-on-carrier-B in the next.

A flat parse — take the last reportConfig seen, apply it to everything — therefore misattributes reports, and does so **silently**: there is no error, no exception, no missing field. The output looks perfectly well-formed.

The fix is a **configuration timeline**: replay every `measConfig` in timestamp order, maintaining the live map, and resolve each report against `maps.at(t)`.

What gave the defect away was arithmetic, not inspection. If 43% of measurement reports carry no neighbour measurement at all, they cannot be A3 — A3 is defined on a neighbour. So a 99.4% A3 attribution is not merely high, it is impossible. And the comparison that surfaced it was against a *published* method, which is the general lesson: the error was invisible from inside the pipeline.

**If the board asks.**

- *"How do you know the corrected parse is right?"* — Three independent checks. The impossibility argument above no longer fires. The configuration counts in the raw log match what the timeline reconstructs (appendix A, slide 45: 1,424 A1, 1,401 A2, 1,309 A3 configurations in one capture). And on an independent public dataset the same parser agrees **310/310** with the vendor tool's own event counter.
- *"Which four claims changed?"* — Two were mine and two were in published work on this network: the deployed offsets are negative rather than +3 dB, and the A3 attribution rates in the earlier analysis. The correction makes my own results *harder* to obtain, not easier, which is the direction an honest correction usually runs.
- *"Why present a defect before any result?"* — Because it is the strongest thing I can say about the dataset. Anyone can present clean numbers. Presenting the one that nearly broke it, and how it was caught, is what makes the clean ones credible.

**Do not say** that other people's parsers are wrong. Say that a flat parse is wrong, that mine was one, and that it is invisible without an external comparison.

---

## Slide 11 · *57 drives, two corridors, 938 signalling-confirmed handovers*
**The claim.** The campaign, and the unit of analysis: the drive.

**On screen.** `fig03_map_routes` — four capture days drawn on an OpenStreetMap basemap of Dhaka (map data © OpenStreetMap contributors, ODbL), one colour per capture, handover positions circled, with a drawn key giving drives and handovers per capture.

**Every number.**

| number | meaning | source |
|---|---|---|
| 57 drives / 10,260 samples / 938 handovers | the pooled dataset | §3 |
| 15 / 8 / 20 / 14 drives and 290 / 174 / 297 / 177 handovers | per capture | §3 |
| 49.5 km/h | mean speed on the highway capture | report 23 / 25 |
| 34.6 km | length of the highway corridor | report 25 |
| median 3.5 s | gap between consecutive handovers; 59.8% are within 5 s | §22 |
| ~2.9 h / ~95 km | total driving | §3 |

**The reasoning — why the drive, and not the sample, is the unit.** Samples inside one drive share a cell sequence, a traffic condition, a trajectory and a device session. They are strongly dependent. Four consequences follow, and all four appear later in the talk:

1. **Splitting** must hold out whole drives, or the test set is partly its own training set (slide 23 measures what that is worth).
2. **Bootstrapping** must resample whole drives, or the intervals understate uncertainty. B = 400, or 1,000 for headline tables.
3. **The conformal guarantee** is exchangeable in drives, not samples — which sets the feasibility floor (slide 24).
4. **Quality control** operates on drives: ≥ 60 s and ≥ 60 samples, which is what produces the 957 → 938 difference.

**If the board asks.**

- *"What is a 'drive'?"* — A contiguous segment of a capture between stops, segmented by the pipeline on speed and time gaps, subject to the ≥ 60 s / ≥ 60 samples quality bar.
- *"957 or 938?"* — 957 in the raw logs; 938 inside drives that pass quality control. The other 19 sit in the fragment at the start or end of a session. Every model is scored against 938. Report 23 quotes 957 because it reads the signalling directly.
- *"Two corridors or four?"* — Four capture days over three urban corridors plus one highway corridor; "two corridors" in the slide title is shorthand for the two *regimes* — urban and highway. If pressed, say four days, four routes, two mobility regimes.
- *"Is one operator enough?"* — No, and slide 40 says so explicitly. What one operator buys is that the deployed configuration is *measured*, which is what makes the configuration-regime result on slide 27 possible at all.

---

## Slide 12 · *The campaign in numbers, capture by capture*
**The claim.** The dataset, laid out so that nothing has to be taken on trust.

**On screen.** A table with four capture columns and a pooled column: corridor · drives after quality control · samples on the 1 Hz grid · duration · signalling-confirmed handovers · measurement-report instants · RRC re-establishments · A3 reports declined within 2 s. Beneath it, the 957-vs-938 note; under that, the quality-control rule and the A3 configuration ranges.

**Every number.**

| | 10 Sept | 12 Sept | 13 Sept | 15 Sept | pooled |
|---|---|---|---|---|---|
| corridor | urban arterial | urban loop | dense urban | **highway** | 2 regimes |
| drives (after QC) | 15 | 8 | 20 | 14 | **57** |
| samples at 1 Hz | 2,700 | 1,440 | 3,600 | 2,520 | **10,260** |
| duration | 46 min | 24 min | 60 min | 43 min | **2.9 h** |
| handovers | 290 | 174 | 297 | 177 | **938** |
| report instants | 4,688 | 3,702 | 4,098 | 3,237 | **15,725** |
| re-establishments | 113 | 64 | 159 | **5** | **341** |
| A3 declined ≤ 2 s | 57.2% | 60.1% | 63.3% | **71.9%** | **62.9%** |

Quality control: a drive is retained at **≥ 60 s and ≥ 60 samples**. A3 offsets **−15, −10, −6.5, +1, +5 dB** and TTT **160–1024 ms**, identical across all four captures. 152 feature columns built, **107** used. ~95 km driven.

**Why this slide exists, and why here.** It comes straight after the map (slide 11), so the board sees the geography and then the arithmetic. It also lets you state the **957-vs-938** distinction once, in your own time, rather than having it dragged out of you during questions — which is the difference between looking rigorous and looking caught.

**The reasoning — three rows to point at, and why each one.**

1. **Re-establishments: 159 versus 5.** This is the cleanest physical contrast in the campaign, and it validates that the highway capture really is a different regime rather than just a different day. In the dense core, corner shadowing and flyover blockage drop the serving cell faster than the Layer-3 filter and TTT can follow, so the link fails. On the highway the macro layer overlaps smoothly and the link survives.
2. **Decline rate climbing 57.2 → 71.9%.** It rises monotonically with cell size, which is the physically expected direction and is an independent check that the signalling parse is sane.
3. **The 957 / 938 footnote.** The parser finds 957 handovers. 938 fall inside a drive that passes quality control; the other 19 sit in the fragment at the start or end of a session. Every model is scored against 938. Report 23 quotes 957 because it reads the signalling directly. Both are right and they answer different questions.

Note also what is **identical** across the four captures: the A3 offsets and TTT values. The network did not reconfigure between captures, which is what lets the leave-one-capture-out design on slide 26 be read as a geography-and-speed test rather than a configuration test.

**If the board asks.**

- *"Why is 12 Sept so much smaller?"* — It is a 24-minute capture over a loop route: 8 drives, 174 handovers. It is also the weakest leave-one-capture-out result (0.909) and has the widest interval, for exactly that reason. I report it rather than dropping it.
- *"Why is the handover rate higher on 12 Sept than 13 Sept?"* — 174 handovers in 1,440 samples is 12.1 per 100 samples against 8.3 on 13 Sept. The loop route crosses more cell boundaries per unit time. It shows up in the prevalence column on slide 26 too: 7.7% against 6.3%.
- *"What is a 'measurement-report instant'?"* — One decoded `MeasurementReport` message on the signalling log, of any event type. 43–52% of them are A3; the rest are A1, A2, A4 and A5, which carry no handover entering condition. That distinction is the first of the two qualifiers on slide 30.
- *"Why 60 seconds for quality control?"* — Below about a minute a drive carries too few handovers for a fold-level metric to be meaningful, and the rolling windows (up to 10 s) consume a large fraction of it. The bar is stated and the 19 excluded handovers are accounted for rather than quietly dropped.
- *"10,260 samples but only 938 positives — is that enough?"* — At the 1 s horizon the positive rate is 6.7%, so roughly 690 positive rows; at 5 s it is 26%. Every interval in this talk is a cluster bootstrap over the 57 drives, which is the right unit, and slide 40 states the scale limitation explicitly.

**Do not say** "938 handovers" and "957 handovers" in the same talk without saying which is which. This is the single most avoidable trap in the deck, and this slide is where you close it.

---

## Slide 13 · *Handovers cluster where the link is weak, and a quarter are ping-pongs*
**The claim.** Handovers are spatially clustered, not uniform along the route — and a quarter return immediately.

**On screen.** `fig04_map_rsrp` — the same routes, coloured in five discrete RSRP bands with a drawn key, handover locations over the top.

**Every number.**

| number | meaning | source |
|---|---|---|
| 24.5% | ping-pong rate: A→B→A, cell = PCI + carrier, 15 s window | §22 |

**The reasoning.** Clustering has two sources, and separating them is what Act VI does. Spatial: junctions, flyovers and corner-shadowing create places where the serving cell drops faster than the Layer-3 filter and TTT can follow. Temporal: one handover makes the next more likely, independently of where you are — which is what the Hawkes fit on slide 31 measures (branching ratio 0.605).

The "quarter" is planted here deliberately and cashed in on slide 32, where the same 938 handovers give four different rates depending on three definition choices.

**If the board asks.**

- *"Why five discrete bands instead of a continuous colour scale?"* — A rendering constraint of the figure toolchain, and it turns out to read better on a projector: a reader can name a band, not interpolate a colour.
- *"Are the clusters just where you drove slowly?"* — No. Slide 33 tests speed directly: the highway capture, at 49.5 km/h mean, returns 31.1% — essentially the same as the urban intra-carrier rate of 31.0%. Speed is not the driver.

---

## Slide 14 · *Every horizon is a rare-event problem, so every metric is read against its floor*
**The claim.** Prevalence moves from 3.7% to 26.0% across the horizons, so accuracy is meaningless and every metric is read against its own floor — and the 0.5 s horizon is legitimate.

**On screen.** `fig05_dataset` — prevalence by horizon.

**Every number.**

| number | meaning | source |
|---|---|---|
| 10,260 samples, uniform 1 Hz grid | the modelling grid | §5 |
| 3.7% → 26.0% | prevalence from 0.5 s to 5 s | §15 |
| 0.0423 / 0.0732 = **0.578** | the prevalence-ratio sanity check for the 0.5 s label | §6.4 |
| δ = 1 ms | handover timestamp precision, verified on 100% of events | §6.4 |
| **90.5%** | maximum event *detection* rate on a 1 Hz grid | §6.4 |
| 10.1% | share of consecutive handovers less than 1 s apart | §6.4 |

**The reasoning — the two-clocks argument. Know this one verbatim.** A 0.5 s horizon on a 1 Hz grid looks impossible. It is not, because the **event clock and the sample clock are different clocks**.

The label is `y_t^(0.5) = 1{ min_j (τ_j − t)_+ ≤ 0.5 }`. It is well defined whenever the handover times `τ_j` are observed to a precision `δ ≤ 0.5 s`, *regardless of the sample spacing Δ*. Here `δ = 1 ms`, verified on 100% of events, because the timestamp comes from a decoded RRC message rather than from a transition on the sampled grid.

The sanity check: if arrivals are locally uniform at rate λ, then `P(T ≤ h) ≈ λh` for small h, so `π_0.5 / π_1.0 ≈ 0.5`. Measured: **0.578** — slightly above 0.5, exactly as positive dependence near an event predicts, and nowhere near 0 or 1.

What the 1 Hz grid *does* bound is **detection**: two handovers closer together than one sample period cannot both be marked. 10.1% of consecutive handovers are less than 1 s apart, so the maximum achievable detection rate is `1 − 0.101 = 90.5%`. Every event-level number in the thesis is read against that ceiling.

**The distinction — the grid bounds detection, the event clock bounds horizon resolution — is drawn nowhere in this literature.** It is a small contribution and a completely safe one, because it is arithmetic.

**If the board asks.**

- *"So 44.7% detection at 1 s is really 44.7 out of 90.5?"* — Yes, and that is how it should be read: about 49% of what the instrument can detect at all.
- *"Why not just resample to 10 Hz?"* — The export is fixed at 1 Hz by the licence, and I cannot raise it. Slide 40 lists it as a limitation.
- *"Why does AUPRC drop from 0.784 at 1 s to 0.627 at 2 s when prevalence rises?"* — Because the two effects fight. Higher prevalence raises the floor (making AUPRC easier) but the task gets genuinely harder further out (the radio state at *t* says less about *t + 5*). Lift is the metric that separates them: 11.7× at 1 s falling to 2.3× at 5 s, which is a clean statement that the *information* decays with horizon.
- *"Why is 0.5 s AUPRC only 0.416 when 1 s is 0.784?"* — Because the floor is 3.7% rather than 6.7%. Read lift instead: 11.3× against 11.7× — essentially the same. This is exactly why AUPRC is never quoted without its floor.

---


---

## Slide 15 · *The framework end to end, in five stages*
**The claim.** The whole method on one slide, before any of it is detailed.

**On screen.** `m14_framework` — five stages left to right: **01 Measure · 02 Ground the labels · 03 Represent · 04 Predict as a hazard · 05 Certify and score.** Stages 02 and 04 are highlighted maroon; stage 05 navy.

**Every number on it.** 4 captures, 57 drives · 938 handover commands, timestamped to 1 ms · 107 features from four blocks · five horizons · 18 pipeline stages, 17 passing tests · a rebuild returns 10,260 samples and 938 handovers exactly.

**Why it exists, and why here.** It opens Part 2 and gives the board a frame for the four slides that follow, so each of those can go deep without the audience losing the thread. It also replaces the old pipeline-diagram slide on the spoken path — that diagram is now appendix F, where it answers a reproducibility question rather than trying to be an overview.

**The reasoning — and the highlighting is the argument.** Two stages are maroon because they carry the two contributions. **Stage 02** is what makes everything downstream possible: a handover here is a decoded RRC command with a millisecond timestamp, not a vendor event counter, and the configuration timeline is what makes that attribution correct. **Stage 04** is the methodological claim: one discrete-time hazard fit rather than five independent classifiers, so the horizons are coherent by the product-limit identity rather than by post-processing. **Stage 05** is navy because it is what the comparable literature omits entirely — 0 of 22 audited papers report calibration, and 0 of 22 report a lead time or a false-alarm rate.

The bottom line on the slide is the leakage guard, and the word that matters is *structural*: grouping by whole drive is enforced in the split constructor, so an experiment cannot silently forget it.

**If the board asks.**

- *"Why is stage 02 separate from stage 01?"* — Because measuring and *labelling* are different problems, and the second is where this campaign nearly failed. Slide 10 is that story: measurement identifiers are message-scoped, a flat parse misattributes silently, and it took a comparison against a published method to catch it.
- *"What runs where?"* — All five stages are in one reproducible pipeline: 18 stages, 17 passing tests. Appendix F shows the stage graph. No number in the thesis is typed by hand.
- *"Could this framework be applied to 5G?"* — The formulation transfers directly: NR uses the same A3 event family and the same measurement-report structure. What would need re-doing is the parser and the configuration timeline, because the RRC ASN.1 differs. I have not done it, and I would not claim it works until I had.

---

## Slide 16 · *Handover prediction is a discrete-time survival problem, not five separate binary tasks*
**The claim.** The central methodological contribution: reformulating as a discrete-time hazard gives horizon coherence by construction, for any learner.

**On screen.** `m04_hazard` — five independent heads (producing 43.6% non-monotone rows, max violation 0.50) versus one hazard fit, with the product-limit identity between them.

**Every number.**

| number | meaning | source |
|---|---|---|
| **43.6%** | rows where the multi-head baseline's horizon sequence is non-monotone | §17 |
| 0.495 | the largest such violation | §17 |
| 0% | hazard-model violations | §17 |
| *(47% and 0.484 were the three-capture figures — both are reported)* | | §17 |

**The reasoning — the derivation. Be able to write this on a whiteboard.**

Let `h_k(x)` be the hazard: the probability the handover occurs in interval *k*, given it has not occurred before *k*. Then survival to the end of horizon *K* is the product

```
   S_K(x) = Π_{k=1}^{K} ( 1 − h_k(x) )
```

and the incidence — the probability the event has happened by horizon *K* — is

```
   F_K(x) = 1 − S_K(x)
```

Because every `h_k ∈ [0,1]`, `S_K` is non-increasing in *K* by construction, so `F_K` is non-decreasing. **`P(event by 1 s) ≤ P(event by 3 s)` is arithmetic, not a constraint you impose.**

Five independent classifiers have no such coupling. Each learns its own horizon, and nothing stops the 1 s head from exceeding the 3 s head — which is a statement that the event happens and then un-happens. It occurs on **43.6%** of rows, with a largest violation of 0.495, which is enormous.

**Three consequences worth having ready:**

1. The property is a property of the **identity**, not of the learner, so it holds for logistic regression, a GRU, anything. Slide 20 tests this with a second learner.
2. It needs **no held-out calibration split** and no post-hoc projection. The alternatives need both.
3. **Class reweighting is forbidden** in this formulation, because a reweighted hazard compounds through the product and the resulting incidence is no longer a probability of anything. (§7.3.) This is a real constraint, not a footnote — it is why the logistic-regression ECE artefact on slide 22 is interesting.

Training is by the discrete-time survival likelihood with right-censoring at the end of each drive: a drive that ends without a handover censors rather than contributing a negative at every horizon.

**If the board asks.**

- *"Can't you just sort the five outputs?"* — You can, and that is the "+ monotone projection" arm on slide 20. It fixes coherence (0% violations) but it is a second post-hoc step, it needs the calibration split the isotonic arm already spent, and it costs ranking. The hazard gets there in one fit with none of that.
- *"Isn't this just a multi-task network with a monotonicity constraint?"* — No, and the difference matters. A constraint is enforced during optimisation and can be violated at inference or traded against the loss. The product-limit identity cannot be violated at all — there is no configuration of hazards that produces a non-monotone incidence.
- *"Why discrete time rather than a Cox model?"* — Because the data is on a fixed 1 Hz grid, the horizons of interest are a handful of grid multiples, and discrete time makes the likelihood a sequence of per-interval Bernoullis that any classifier can fit. A continuous-time model would need a baseline hazard and buys nothing here.
- *"43.6% seems very high."* — It is, and it is why this is worth a slide. It is also worth noting the direction: per-horizon isotonic calibration, the obvious remedy, makes it **worse** — 48.7% of rows and a 0.596 maximum violation — because each horizon is recalibrated independently and nothing couples them.
- *"Does censoring matter with drives this short?"* — It matters at every drive boundary, which with 57 drives is 57 censoring events, and it is why no slope or window feature is allowed to cross a drive boundary.

**Do not say** the hazard model is "more accurate". It is not, materially — AUPRC deltas against the multi-head baseline run −0.03 to +0.01. The claim is coherence *and* calibration *and* ranking from one fit. Saying "more accurate" invites a table that does not support it.

---

## Slide 17 · *152 columns built, 107 used, four blocks, two guards*
**The claim.** What the model is given, how it was built, and the two places where a careless choice would have leaked the answer.

**On screen.** `m13_features` — the 1 Hz wide CSV and the RRC signalling log feeding four blocks (RF 83 · mobility 17 · history 7 · signalling 13), into 152 built columns, through a degenerate filter fitted on training rows only, to 107 features and a per-fold robust scaler. The history block is highlighted amber and the signalling block maroon.

**Every number.**

| block | count | what is in it |
|---|---|---|
| **RF** | 83 | For each of RSRP, RSRQ, RSSI, SINR, CQI and each window of 3/5/10 s: rolling mean, standard deviation, range, plus first and second backward differences. Top-3 neighbour gaps, best gap, neighbour spread, and a missingness mask per field. |
| **Mobility** | 17 | Speed, acceleration, heading, heading change wrapped to (−π, π], along-track coordinate on the corridor's principal axis, its rate, distance travelled in the drive. |
| **History** | **7** | Serving dwell time (clipped at 180 s), log dwell, time since previous handover, handover count so far, previous target PCI and whether it equals the current serving PCI. |
| **Signalling** | 13 | The A3 hold time and `holdfrac` (a TTT clock), report counts over 1/2/3/5 s windows for all events and for A3 alone, time since the last A3 report, and RF slopes in dB/s over 3 and 5 s. |
| | **152 → 107** | Built, then filtered for zero variance or > 50% missing **on training rows**. |

Scaler: **robust** — median and IQR, clipped to ±8, fitted per fold on training rows only.

**Why this slide exists, and why here.** Act III runs *target → inputs → protocol*: slide 16 says what the model is asked to predict, this slide says what it is given, slide 18 says how it is scored. Feature engineering is also where most of the intellectual work in an applied thesis actually goes, and a board that does not see it will ask about it.

**The reasoning — three things this slide is really saying.**

**1. The size inversion.** The smallest block is the strongest. Seven history features, and one of them — serving dwell time — reaches AUROC 0.874 alone (slide 29), beating all 83 RF features individually. Dwell time is a **sufficient statistic for a renewal-like process**: the longer the phone has been attached, the further it has travelled inside the cell's footprint. It summarises the whole trajectory into the handover in one scalar, where the A3 gap summarises one instant.

**2. Guard one — nothing sees the future.** Every rolling window is backward-looking and closed at *t*. Every RF slope is a backward difference. All of them carry `NaN` at drive boundaries, so no window or slope crosses from one drive into another.

**3. Guard two — the one that nearly caught me.** A measurement report precedes its handover command by **50–200 ms**, which is *inside one sample* on a 1 Hz grid. A feature counting reports "in the current bin" would therefore be reading the outcome, not predicting it. The report-count window is consequently the half-open interval `(t − w, t − Δ]` — it stops one sample early. That choice also makes consecutive windows tile without double-counting a report that lands on a bin boundary. **Seven unit tests** pin it, including the exact-boundary case and the drive-boundary reset.

**If the board asks.**

- *"Why a robust scaler rather than standardisation?"* — RF distributions have heavy tails at cell edges. Median and IQR are not dragged by a dropout sample, and the ±8 clip stops a single deep fade from dominating a tree split or a gradient step.
- *"Doesn't the missingness mask leak?"* — No, and it is deliberate. Neighbour coverage is 62–79%, so some rows genuinely have no neighbour measurement. Imputing a value invents information; the mask lets the model condition on *availability*, which is itself a legitimate observable — the phone knows whether it has a neighbour reading.
- *"Only 107 of 152 — what was dropped?"* — Columns with zero variance or more than 50% missing on the **training** rows of that fold. The filter is fitted per fold, so it cannot see the test rows.
- *"Did you do feature selection or importance analysis?"* — Not as a selection step: all 107 go in, and LightGBM handles redundancy. What I do report is single-feature AUROC (slide 29) as a *mechanism* diagnostic, and block-level ablation — adding the whole signalling block is worth only +0.005 to +0.012 AUPRC (slide 39).
- *"What is `holdfrac`?"* — The A3 hold time divided by the configured TTT, clipped to [0, 10]. A value ≥ 1 means the entering condition has been satisfied for at least the full time-to-trigger — precisely the state in which a report is due. It reaches AUROC 0.615 on its own.
- *"Why is the along-track coordinate not leakage?"* — It is a projection of the GPS trace onto the corridor's principal axis, so it is comparable between drives in either direction. It encodes *where on the corridor* the phone is, which is observable at time *t*. It does not encode anything about the future, and it is unavailable on the external dataset — which is precisely why external transfer scores 0.752 rather than 0.933.

**Do not say** that the feature set is "carefully engineered" as though that were the contribution. Slide 39 shows that adding information mostly did not help. The contribution here is the two guards and the honest per-fold fitting, not the 152 columns.

---

## Slide 18 · *Every drive is tested exactly once, and nothing from a test fold is ever fitted*
**The claim.** The evaluation protocol, and why it has the shape it has.

**On screen.** `m03_protocol` — the grouped rotation over 57 drives, repeated over 5 seeds.

**Every number.**

| number | meaning | source |
|---|---|---|
| 57 drives, 4 folds, 5 seeds | the rotation | §11.1 |
| 20 | paired observations (5 × 4) per comparison | §11.5 |
| 0.125 | the smallest p a two-sided Wilcoxon can return with 4 pairs | §11.5 |
| 8 | drives left in test by a single 15% split | §11.1 |
| B = 400 (1,000 for headline tables) | cluster-bootstrap resamples, by whole drive | §11.4 |

**The reasoning.** Three design decisions, each with a stated reason:

**Why a rotation rather than a single split.** 57 drives with a 15% test share leaves 8 drives in test. A cluster bootstrap over 8 groups produces an interval whose width is dominated by having 8 groups, not by the model's uncertainty. The rotation tests every drive exactly once, so every drive contributes to the estimate.

**Why 5 seeds.** With 4 folds you have 4 paired observations. A two-sided Wilcoxon signed-rank test on 4 pairs has a minimum attainable p-value of **0.125** — it cannot reject at 0.05 no matter how large the effect. The test would be reporting its own floor rather than the data. Five seeds give 20 pairs, which is enough for the test to say something.

**Why grouping is architectural.** The grouping is enforced in the split constructor, not by convention in each experiment, so an experiment cannot silently forget it. Every fitted object — scaler, calibrator, conformal threshold — is fitted on training drives only, per fold.

**If the board asks.**

- *"Aren't 5 seeds just 5 correlated repeats?"* — They are correlated, and that is why the bootstrap is over drives rather than over seed-fold pairs. The seeds buy test power on the *paired* comparison; the drive-level bootstrap is what produces the interval.
- *"Why 4 folds and not 10?"* — 4 folds over 57 drives leaves ~14 drives per test fold, which keeps the per-fold event count high enough for AUPRC to be stable. 10 folds would give ~6 drives per fold, and the fold-level metrics become noisy.
- *"Does the scaler leak?"* — No. Robust scaler (median and IQR, clipped at ±8), fitted on training rows only, per fold. §8.5.

---


# PART 3 — What does the evidence show?

---

## Slide 19 · *Gradient boosting reaches AUROC 0.933 at 1 s — twelve times the prevalence floor*
**The claim.** The headline result, read against its floor, with calibration, and with a ranking whose shape is explained rather than hidden.

**On screen.** `fig10_model_comparison` — all seven learners at the 1 s horizon, with the prevalence floor drawn explicitly.

**Every number.** The full 1 s table — know the top two rows and the last:

| model | AUPRC | lift | AUROC | ECE | Brier |
|---|---|---|---|---|---|
| **LightGBM** | **0.784** | **11.7×** | **0.933** | **0.024** | 0.026 |
| logistic regression | 0.728 | 10.9× | 0.927 | 0.127 | 0.073 |
| MLP | 0.677 | 10.1× | 0.910 | 0.121 | 0.081 |
| TCN | 0.574 | 8.6× | 0.884 | 0.091 | 0.079 |
| Transformer | 0.567 | 8.5× | 0.881 | 0.109 | 0.090 |
| GRU | 0.475 | 7.1× | 0.872 | 0.173 | 0.120 |
| **A3 rule** | 0.118 | 1.8× | **0.653** | 0.163 | 0.157 |

Event level, thresholds set at 5% FPR on in-fold validation drives, pooled by **summing counts** and then recomputing rates (never by averaging fold rates):

| model | horizon | detected | false alarms/h | /km | median lead |
|---|---|---|---|---|---|
| LightGBM | 1 s | **44.7%** | 63.9 | 1.79 | 0.46 s |
| LightGBM | 3 s | 64.2% | 62.8 | 1.76 | 0.97 s |
| LightGBM | 5 s | **65.1%** | 41.6 | 1.17 | 1.80 s |
| A3 rule | 1 s | **5.5%** | 65.8 | 1.85 | 0.50 s |
| A3 rule | 5 s | 27.9% | 57.3 | 1.61 | 2.90 s |

**The reasoning — why a tree ensemble beats three sequence architectures.** Three reasons, in order of importance:

1. **Sample size.** 57 drives and 10,260 samples. Sequence models need to learn the temporal structure from data; the tabular features already *encode* it, in 107 hand-built columns including rolling means, standard deviations, first and second differences, ranges over 3/5/10 s windows, and dwell time. The window is handed to the model rather than learned from it.
2. **Feature form.** The single strongest feature is dwell time — a scalar that summarises the entire trajectory into the handover. A GRU has to infer that from a 10 s window; it is given to LightGBM directly.
3. **Leakage exposure.** The 10 s window that buys the sequence models nothing costs them the exposure measured on slide 23 — a GRU inflates by 74% under a careless split, against 4% for logistic regression.

And a linear model comes second, which is the honest reading of the same fact: on this much data there is not a great deal of non-linear structure left once the features are built.

**If the board asks.**

- *"AUROC 0.933 sounds too good."* — It is the number that made me build the leakage experiment. Under grouped-drive splitting it is 0.933; under random-row splitting the same pipeline gives a higher number I do not believe. And the mechanism slide explains why it is high without being suspicious: dwell time alone reaches 0.874. Most of the signal is in how long you have been camped.
- *"Why is AUROC 0.933 but AUPRC only 0.784?"* — Because AUROC is insensitive to prevalence and AUPRC is not. On a 6.7%-prevalence task, AUPRC's floor is 0.067; 0.784 is 11.7× that. The pair is reported together precisely so neither can be read alone.
- *"Only 44.7% of events detected — isn't that poor?"* — Read it against the 90.5% instrument ceiling: it is about 49% of what is detectable at all, at 1 s, at a 5% false-positive rate, with a median lead of 0.46 s. At 5 s it is 65.1% with 41.6 false alarms per hour. And the operator's own deployed rule detects 5.5% at 1 s.
- *"Why is lead time only 0.46 s at the 1 s horizon?"* — Because the warning window at that horizon is 1 s wide, so the lead is bounded by it. Lead grows with horizon: 0.97 s at 3 s, 1.80 s at 5 s. The quantity an operator would act on is the pair (detection rate, lead time), which is why both are reported.
- *"63.9 false alarms an hour sounds unusable."* — It is an operating point, not a recommendation, and it is chosen at 5% FPR for comparability across models rather than for deployment. Slide 25 is where the deployable operating points live: at α = 0.20 the certified threshold alarms on 23% of samples with a guaranteed per-drive miss rate.
- *"Did you try XGBoost / CatBoost / a transformer with more layers?"* — LightGBM is the tree arm; the tuned comparison on slide 22 gives every architecture the same budget. I would not expect another GBM implementation to change the ordering, and I have not measured it — that is an honest gap rather than a claim.

**Do not say** the sequence models "don't work". Say they have nothing extra to learn *at this sample size*, and point at the tuned arm which shows they gain a lot and still lose.

---

## Slide 20 · *The hazard model earns coherence; per-horizon calibration buys ECE and destroys it*
**The claim.** The hazard formulation delivers calibration, coherence and ranking from one fit — narrowly and honestly stated, with the comparison that does not go your way stated first.

**On screen.** `fig13_hazard_results` — four arms on identical folds, coherence violations and calibration error.

**Every number.**

Coherence:

| arm | non-monotone rows | largest violation |
|---|---|---|
| **hazard** | **0%** | 0 |
| multi-head raw | 43.6% | 0.495 |
| multi-head + isotonic | **48.7%** | **0.596** |
| + isotonic + monotone | 0% | 0 |

Calibration (paired deltas, hazard minus comparator; negative = hazard better):

| comparator | 1 s | 5 s | significance |
|---|---|---|---|
| multi-head raw | **−0.006** [−0.007, −0.005] | **−0.029** [−0.033, −0.026] | p < 0.0001 at every horizon |
| + isotonic | +0.005 [+0.002, +0.008] | +0.025 [+0.014, +0.036] | p ≤ 0.008 |
| + isotonic + monotone | +0.004 [+0.001, +0.007] | +0.025 [+0.014, +0.034] | p ≤ 0.039 |

Ranking: isotonic costs **2–5 AUPRC points** (hazard minus isotonic: +0.023 at 1 s, +0.045 at 5 s, all significant); the monotone projection returns most of it.

The learner control:

| learner | ECE, hazard − multi-head | AUPRC, hazard − multi-head |
|---|---|---|
| LightGBM | −0.006 to −0.029, **p < 0.0001 at every horizon** | −0.03 to +0.01 |
| MLP | −0.003 to +0.004, **not significant** | −0.11 at 1 s |

**The reasoning.** Read the three axes separately, because the answer differs on each:

- **Coherence** is won outright and by construction. It is a property of the product-limit identity, so it does not depend on the learner — which is why it survives the MLP control.
- **Calibration** is won against an *uncalibrated* baseline and lost against a *calibrated* one. That is not a weakness to hide; it is the honest shape. The calibrated baseline pays for its win with a held-out calibration split and 2–5 AUPRC points.
- **Ranking** is a wash.

The learner control is the important experiment and is worth volunteering. Swapping LightGBM for a small MLP: the coherence property survives (it is arithmetic), but the *calibration* advantage vanishes and becomes non-significant. So the honest decomposition is: **coherence is the formulation's, calibration is the formulation-plus-gradient-boosting's.** Saying that yourself separates "the formulation helps" from "LightGBM helps", which is exactly the question a good examiner would pose.

**If the board asks.**

- *"So an isotonic baseline beats you on calibration. Why not just use it?"* — Because of what it costs: a held-out calibration split (drives you do not have), 2–5 AUPRC points, and — critically — it leaves coherence **worse than doing nothing**, at 48.7% violating rows. To fix that you need a second post-hoc step, the monotone projection. The hazard model gets all three properties from one fit with no split.
- *"Why does isotonic make coherence worse?"* — Because it is fitted **per horizon**, independently. Nothing in the procedure couples the five horizons, so each one is moved to its own best-calibrated position and the ordering between them is free to break further than it already had.
- *"20 paired observations is small."* — It is, which is why every delta carries a drive-level bootstrap interval as well as a p-value, and why the seeds exist at all: 4 folds alone would put the Wilcoxon floor at p = 0.125.
- *"Is the ECE improvement of 0.006 meaningful?"* — At 1 s, marginally; at 5 s it is 0.029 on a base of 0.111, which is a quarter of the error. The direction is consistent at every horizon and p < 0.0001 throughout. But I would not build a claim on 0.006 alone, and the claim I do make is the joint one.

**Do not say** the hazard model is "better calibrated than the alternatives". Say "better calibrated than an *uncalibrated* baseline, and the calibrated baseline wins on that axis alone at a stated cost."

---

## Slide 21 · *Before claiming a winner, every model was given the same tuning budget* · **HIDDEN**
**Why hidden.** One sentence on slide 22 does the job. Jump here by number if pressed on tuning design.

**What it says.** Every model re-run under the nested protocol: **20 Optuna trials each, inner `GroupKFold(3)` on training drives only, same objective, same folds, same seed.** The objective is mean inner AUPRC at the **2 s horizon** — the middle horizon, so nothing is tuned to an extreme. The default arm is re-run in the same stage so the two arms differ by the parameters alone.

---

## Slide 22 · *The deep baselines really were under-tuned — and it does not change the answer*
**The claim.** The standard objection is correct, was measured rather than argued, and does not change the ordering.

**On screen.** `fig11_tuning` — paired tuning deltas at 1 s with drive-level bootstrap intervals.

**Every number.**

| model | Δ AUPRC (tuned − default) | 95% CI |
|---|---|---|
| Transformer | **+0.109** | [+0.067, +0.148] |
| TCN | **+0.102** | [+0.074, +0.130] |
| GRU | **+0.050** | [+0.022, +0.082] |
| logistic regression | **+0.029** | [+0.021, +0.038] |
| MLP | +0.004 | [−0.015, +0.024] |
| **LightGBM** | **−0.021** | [−0.031, −0.008] |

The snapshot-over-sequence gap narrows from **0.229 to 0.100** AUPRC and **closes at no horizon**.

**The reasoning.** Three readings, in order:

1. **The objection is correct.** A Transformer gains 0.109 and a TCN 0.102, both far outside their intervals. Anyone who suspected the deep baselines were under-tuned was right.
2. **It does not change the answer.** Given the same budget, no tuned sequence model reaches an *untuned* logistic regression.
3. **The winner got slightly worse.** LightGBM loses 0.021 at 1 s with an interval excluding zero (positive at 0.5, 3 and 5 s; a wash overall). This is the cleanest available evidence that its margin is not a defaults artefact: **the same search that lifts every competitor cannot lift the winner.**

**One number needs a footnote, and volunteering it is worth a lot.** Logistic regression's ECE of 0.127 in the headline table is an artefact of `class_weight='balanced'`, which the search switches off. Tuned, its ECE is **0.0098** — better calibrated than LightGBM — at a *gain* of 0.029 AUPRC. This **sharpens** slide 20 rather than weakening it: the hazard claim was never that no baseline can be well calibrated, it is that calibration, coherence and ranking arrive together from one fit without spending drives on a calibration split.

**⚠ Status.** *This tuned arm was produced on the three-capture dataset.* Its conclusion is a statement about **ordering**, and the four-capture ordering in the headline table is identical. The tuned arm is re-run before submission. **Say this before you are asked** — it costs nothing and being caught on it would cost a great deal. Nothing in the contributions section depends on the tuned figures themselves.

**If the board asks.**

- *"20 trials is a small budget."* — It is, and slide 40 lists it as a limitation. It is small *equally* for every model, which is what makes the comparison fair. A wider search over 57 drives would overfit the inner rotation rather than settle the question. The result to lean on is the direction, not the exact tuned figures — and the same caveat applies in reverse to LightGBM's −0.021: read it as "the search cannot improve on the defaults", not "the defaults are optimal".
- *"Did you tune on the test fold?"* — No. Nested: inner `GroupKFold(3)` on training drives only, objective computed inside the training folds.
- *"Why the 2 s horizon as the objective?"* — It is the middle one. Tuning at 0.5 s or 5 s would optimise for an extreme of the prevalence range.

---

## Slide 23 · *Leakage is architecture-dependent: a GRU inflates by 74%, logistic regression by 4%*
**The claim.** Random-row splitting inflates results, the inflation is architecture-dependent, and it therefore **reorders** the leaderboard rather than merely lifting it.

**On screen.** `fig12_leakage` — the same seven models under grouped-drive versus random-row splitting.

**Every number.** Relative AUPRC inflation from random-row splitting:

| model | 0.5 s | 1 s | 2 s | 3 s | 5 s | **mean** |
|---|---|---|---|---|---|---|
| **GRU** | +71% | +62% | +82% | +84% | +73% | **+74%** |
| **Transformer** | +44% | +27% | +44% | +53% | +52% | **+44%** |
| TCN | +35% | +20% | +27% | +25% | +26% | **+27%** |
| LightGBM | +41% | −1% | +3% | +20% | +37% | **+20%** |
| MLP | +26% | +5% | +3% | +6% | +10% | **+10%** |
| logistic regression | +21% | −3% | −3% | 0% | +4% | **+4%** |
| A3 rule | −1% | −11% | +3% | +1% | −4% | **−2%** |

**The reasoning — the mechanism, and why the ordering is the finding.** A sequence model consumes a 10 s window. Under random-row splitting, a test row's window overlaps windows the model trained on, so **the test set is partly its own training set**. A snapshot model sees one row and has far less to exploit. A rule baseline has none at all — and, as the bottom row confirms, it does not move (−2%, noise).

That ordering is the finding. If leakage were a constant offset it would be an annoyance. Because it scales with how much memory an architecture has, it **changes which model appears to win** — a leaked comparison can crown a GRU that a grouped comparison puts last.

**The implication for reading the literature:** a published GRU result on a randomly split drive-test set should be read as roughly **1.7×** what a grouped split would give.

The ordering is what replicates: it held on three captures and it holds on four.

**If the board asks.**

- *"Is this just overfitting?"* — No, and the distinction matters. Overfitting shows up as a train/test gap under *any* split. This is a *split-construction* artefact: the test set is contaminated. Under grouped splitting the same models do not exhibit it.
- *"Why does LightGBM inflate 41% at 0.5 s but −1% at 1 s?"* — The 0.5 s task has the lowest prevalence (3.7%) and the fewest positives, so the per-fold estimates are noisiest; a single contaminated neighbour row moves the metric more. Read the mean column, and read the *ordering* rather than any single cell.
- *"Are you accusing published papers of leaking?"* — No. I am saying that ten of 22 state no split protocol at all, so a reader cannot tell — and that this measurement says what it would be worth if they did. That is a statement about what can be concluded, not about anyone's integrity.
- *"Could you not just use a blocked or purged split instead?"* — You could, and for a single time series that would be the standard answer. Here the natural blocking unit is already the drive, and blocking within a drive still leaves cell sequence and trajectory shared across the boundary. Grouping by drive is the stronger version of the same idea.

---

## Slide 24 · *A distribution-free bound on missed handovers, and what it costs to hold it*
**The claim.** A distribution-free per-drive guarantee, with a precisely-stated contribution: the exchangeable unit, and the campaign-design rule that follows.

**On screen.** `m05_crc` — 28 calibration drives, a threshold sweep, the certified threshold applied to unseen drives, with the feasibility floor annotated.

**Every number.**

| number | meaning | source |
|---|---|---|
| 28 | calibration drives; 29 test drives | §18 |
| **α ≥ 0.034** | the feasibility floor with n = 28 | §12.3 |
| 0.044 → 0.034 | what the fourth capture's six extra calibration drives bought | §12.3 |
| Cohen et al. 2022, Simeone et al. 2025 | conformal prediction already in wireless | §25.2 |

**The reasoning — the procedure, the choice, and the rule.**

**The procedure** (Angelopoulos et al., conformal risk control). Let `λ` index alarm thresholds and `R(λ)` be a bounded, non-increasing risk. Choose

```
   λ̂ = inf { λ : [ n·R̂(λ) + B ] / (n + 1) ≤ α }
```

where `R̂(λ)` is the empirical risk over *n* exchangeable calibration units and `B = 1` bounds the loss. The guarantee is `E[R_{n+1}(λ̂)] ≤ α` for a fresh exchangeable unit — **distribution-free**, assuming nothing about the model or the data beyond exchangeability.

**The choice — and this is the contribution.** Samples within a drive are *not* exchangeable with samples from another drive: they share a cell sequence, a traffic condition, a trajectory. So the risk is the **per-drive miss rate**

```
   R_d(λ) = |{ t ∈ drive d : y_t = 1 ∧ p̂_t < λ }| / |{ t ∈ drive d : y_t = 1 }|
```

and `R̂` averages over calibration **drives**, not samples. A threshold calibrated on pooled samples leaves a far larger fraction of drives above their target, and that contrast is reported.

**The rule that falls out.** Equation (5) can only be satisfied if its left-hand side can reach α at all. At the most permissive threshold `R̂ = 0`, so the smallest attainable value is `B/(n+1)`:

```
   α ≥ 1/(n+1)      ⟺      n ≥ 1/α − 1
```

**A campaign that wants a 5% guarantee needs at least 19 calibration drives; 2% needs 49.** Here n = 28, so α ≥ 0.034. **This rule is stated nowhere in the handover literature, and it determines how much driving a study must do before its guarantee is even expressible.** It is the cleanest, safest contribution in the thesis — it is algebra.

**If the board asks.**

- *"What exactly is yours here?"* — Not the machinery. Conformal prediction is already in wireless: Cohen et al. 2022, Simeone et al. 2025. Their guarantees are over prediction **sets** for tasks that are i.i.d. within a frame. Mine is a **risk** guarantee on an operator KPI over a stream exchangeable only by whole drive. The exchangeability unit is the contribution and the feasibility floor is its consequence. (Appendix G has this written out.)
- *"Are drives really exchangeable?"* — Approximately, and the assumption is stated rather than assumed away. They are not identically distributed — an urban drive differs from a highway drive — but exchangeability is weaker than i.i.d. and is what the guarantee needs. The leave-one-capture-out result on slide 26 is the empirical check: a whole capture held out still behaves, which is evidence the exchangeability assumption is not badly violated.
- *"What if the network changes configuration after calibration?"* — Then exchangeability breaks and the guarantee lapses. That is exactly the cross-regime result on slide 27 — Δ AUROC 0.088 — and it is a real limitation: the bound is conditional on the configuration regime being stable.
- *"Why not standard conformal prediction intervals?"* — Because an operator does not act on an interval, they act on an alarm, and the quantity they are charged for is missed handovers per drive. Risk control bounds that directly.

---

## Slide 25 · *The guarantee is affordable above a 15% miss rate and expensive below it*
**The claim.** The price of the guarantee, published as a whole frontier.

**On screen.** `fig14_riskcontrol` — certified alarm rate and realised test miss rate against α, with the usable operating point at α = 0.20 circled, the feasibility floor annotated, and the α = target diagonal drawn.

**Every number.** 1 s horizon, hazard-model incidence, 28 calibration drives, 29 test drives:

| α | certified alarm rate | achieved miss rate | per-drive p90 | drives over α |
|---|---|---|---|---|
| 0.05 | **61%** | 0.035 | 0.121 | 18% |
| 0.10 | 37% | 0.074 | 0.226 | 25% |
| 0.15 | 28% | 0.091 | 0.226 | 21% |
| **0.20** | **23%** | **0.126** | 0.290 | **18%** |
| 0.30 | 9.4% | 0.220 | 0.353 | 18% |

**The reasoning.** The bound holds at every level, with slack — the achieved miss rate is always below α. The shape of the price curve is the point: the certified alarm rate rises steeply below α ≈ 0.15, because a distribution-free bound must be conservative enough to cover the worst plausible drive, and buying a tighter guarantee means alarming on more and more of the stream. At α = 0.20 the operator misses 12.6% of handovers while alarming on 23% of samples; at α = 0.30, on under 10%. Those are operating points a network could actually run.

**The fourth capture made both cheaper**, because a wider calibration set certifies a less conservative threshold for the same guarantee.

**If the board asks.**

- *"'18% of drives over α' — doesn't that break the guarantee?"* — No, and this is the most likely misreading on the slide. The guarantee is on the **expected** risk for a fresh drive, `E[R_{n+1}] ≤ α`, not on every individual drive. Some drives exceed α and others sit far below; the mean is bounded. A per-drive worst-case guarantee would require a different and far more conservative procedure.
- *"Why is 'drives over α' 25% at α = 0.10 but 18% at α = 0.20?"* — It is not monotone because it is a small-sample count over 29 test drives — one drive is 3.4 percentage points. The quantity with the guarantee attached is the mean, and that is monotone and always below α.
- *"Which α would you deploy?"* — 0.20 or 0.30, depending on what the alarm costs. Below 0.15 I would not deploy this, and the slide says so. That is the honest answer and it is stronger than picking one.
- *"Is 23% of samples a lot?"* — It is roughly one alarm every four seconds on a 1 Hz stream, which is only usable for a cheap action — pre-fetching a target-cell context, say, not a handover trigger. The thesis does not claim an actuator; slide 40 says the causal effect is unidentified here.

---


---

## Slide 26 · *A fourth capture, a new corridor, twice the speed — and the same result*
**The claim.** The strictest generalisation test the campaign supports: hold out a whole capture, including one that is a new corridor and a new speed regime, driven after the model was frozen.

**On screen.** `fig25_capture_transfer` — leave-one-capture-out, four bars.

**Every number.**

| held out | prevalence @ 1 s | AUPRC | lift | AUROC | ECE |
|---|---|---|---|---|---|
| 10 Sept urban arterial | 8.4% | 0.826 | 9.9× | 0.949 | 0.027 |
| 12 Sept urban loop | 7.7% | 0.718 | 9.4× | 0.909 | 0.040 |
| 13 Sept dense urban | 6.3% | 0.832 | 13.2× | 0.943 | 0.019 |
| **15 Sept highway** | **5.1%** | **0.761** | **14.9×** | **0.927** | **0.018** |

Reference: pooled grouped-drive rotation within the dataset is AUROC 0.933. Adding the fourth capture moved it by **zero** (0.933 → 0.933; AUPRC 0.797 → 0.784, lift 10.98× → 11.70×).

Physical contrast: **159** RRC re-establishments on 13 Sept in the dense urban core, **5** on 15 Sept over 34.6 km of open highway.

**The reasoning.** The highway capture was driven **after every modelling decision in this thesis was frozen** — the feature set, the horizon set, the split rule and the model configuration were fixed on the three urban captures and not touched for it. No retraining, no adaptation, no feature added on its behalf. Held out whole it scores AUROC 0.927 with the **highest** lift and the **lowest** calibration error of the four.

The re-establishment collapse is the cleanest physical contrast in the campaign, and it is worth having ready because it makes the whole thing concrete. In the dense urban core, corner shadowing and flyover blockage drop the serving cell faster than the Layer-3 filter and time-to-trigger can follow, so the link fails and the phone re-establishes. On the highway, the macro layer overlaps smoothly and the link simply survives.

**Two honest qualifiers, and say both.** Four captures give **four points**, so this is a strong *design*, not a large sample. And the highway's lower prevalence (5.1% against 8.4% on 10 Sept) raises lift **mechanically** — which is exactly why lift is reported beside AUPRC and never instead of it.

**If the board asks.**

- *"Why is the highway's lift highest if its AUPRC is not?"* — Because lift is AUPRC divided by prevalence, and the highway has the lowest prevalence (5.1%). The AUPRC ordering is 13 Sept > 10 Sept > 15 Sept > 12 Sept. I quote both for exactly this reason.
- *"Was the highway really held out completely?"* — Completely: no drive, no route, no hour, no corridor, no speed regime shared with anything the model saw. And the model configuration predates the capture.
- *"Four points is not a generalisation study."* — Agreed, and the slide says so. It is the strictest test **this campaign supports**. The second future-work item is one more capture on a new route, which turns a single regime pair into a matrix.
- *"12 Sept is the weakest at 0.909 — why?"* — It is also the smallest capture: 8 drives, 174 handovers, ~24 minutes. Fewer training drives on the other side and the noisiest test estimate. Its interval is the widest of the four.

---

## Slide 27 · *Real-to-real transfer holds, and the model matches an independent dataset's own ceiling*
**The claim.** Three transfer tests of increasing difficulty; the model reaches an external dataset's own in-domain ceiling; and configuration regime is a real boundary that features do not fix.

**On screen.** `fig15_transfer` — between captures, out to a public dataset, across A3 regimes.

**Every number.**

**Between captures** (train one day, test another — different drives, routes, cells, scaler): AUROC **0.883–0.933** at 1 s. Diagonal (held-out drives from the same capture): 0.914–0.933.

**Out to an independent dataset** — Shafi et al. (2025), Mendeley Data, DOI 10.17632/n2pvmtyn2j.1:

| horizon | our model → their data | their own in-domain ceiling |
|---|---|---|
| 1 s | **0.752** | 0.745 |
| 2 s | **0.745** | 0.737 |
| 3 s | **0.712** | 0.686 |
| 5 s | 0.705 | 0.708 |

Our model matches or exceeds what a model trained on that data achieves on itself at **three of four horizons**. Parser agreement with the vendor's event counter: **310/310**.

**Across configuration regimes:** same-regime 0.833 → cross-regime 0.745, **Δ AUROC 0.088**, pooled over horizons. Conditioning on the measured A3 parameters as input features recovers **none** of it (0.744 vs 0.745).

**The reasoning.** The absolute external level (0.752) is lower than on our own captures (0.933) because **that dataset lacks GPS and therefore the entire mobility block** — 17 of the 107 features are unavailable. That is a missing-feature effect, not a transfer failure, and the proof is the comparison column: a model trained on that data reaches only 0.745 on itself.

The configuration result is the one that costs. Configuration shift is a genuine domain boundary, and — the interesting part — **telling the model about the configuration does not help**. Giving it the measured offset, hysteresis and TTT as features recovers 0.744 against 0.745. The regime changes the *relationship* between the radio state and the handover decision, not just the threshold, so a feature cannot patch it.

**If the board asks.**

- *"Beating their own ceiling sounds impossible."* — It is not, and it is worth saying why calmly. Their in-domain ceiling is what a model trained on their (GPS-less, smaller) data achieves on their data. My model is trained on richer data with more drives and transfers the learned structure. More training signal beats matched domain here. At 5 s the two are level (0.705 vs 0.708), which is the expected shape.
- *"Only two A3 regimes?"* — Yes, and slide 40 states it. Only two profiles clear the 60-handover bar needed for a reliable comparison, on an identical 591-row, 13-drive test set. The 0.088 gap is real but narrow in scope — one regime pair, one direction.
- *"Is 0.088 large?"* — In context, yes. Crossing whole captures costs almost nothing (0.883–0.933 against a 0.914–0.933 diagonal). Crossing a configuration regime costs 0.088. So the binding domain boundary in this data is the network's configuration, not the geography — which is a finding, and an actionable one for anyone deploying across a network with mixed configurations.
- *"Did you try to close the 0.088 gap?"* — Yes, two ways. Conditioning on the A3 parameters (recovers nothing) and two unsupervised domain adaptations (appendix C — both lose on both sides). A supervised or adversarial method with target labels might recover it; nothing here rules that out, and slide 40 says so.

---

## Slide 28 · *Both zero-cost domain adaptations make transfer worse* · **HIDDEN** (= appendix C, slide 47)
**The claim.** Two standard unsupervised adaptations were tried in good faith and both lose on both sides of the transfer.

**Every number.** 1 s horizon, LightGBM, same held-out drives on every arm:

| setting | adaptation | matched AUROC | transfer AUROC | gap |
|---|---|---|---|---|
| **regime** | **none** | 0.819 | **0.865** | −0.046 |
| | CORAL | 0.800 | 0.771 | +0.030 |
| | per-drive z | 0.796 | 0.699 | +0.097 |
| **external** | **none** | 0.848 | **0.642** | +0.206 |
| | per-drive z | 0.809 | 0.567 | +0.242 |
| | CORAL | 0.848 | 0.534 | +0.315 |

**The reasoning.** **Matched-domain AUROC falls too** (0.819 → 0.796 / 0.800), which rules out the reading that they trade in-domain accuracy for robustness. They are simply worse.

The mechanism is visible in what they remove: **the absolute level of the radio features carries the signal here.** A serving RSRP of −112 dBm means something on its own — it is near the edge. Per-drive standardisation deletes exactly that and keeps only within-drive shape. CORAL performs the same deletion in second-moment form, rotating the target into a geometry the source-fitted trees never split on.

**The null is in line with a published benchmark, not an outlier.** Ismail Fawaz et al. (2023, Ericsson Research) compare **nine** unsupervised domain-adaptation algorithms over **twelve** time-series datasets and find that the adaptation technique, not the backbone, drives the outcome — and that several published methods, VRADA and CoTMix among them, perform *worse than training on the source and applying it with no adaptation at all*. This result has exactly that shape. **This is the answer to "you implemented CORAL badly".**

**⚠ Read the table carefully if pressed.** These figures are comparable **only across adaptations within this experiment**. Matched and transfer cells are scored on different row populations, which is why the untreated regime row shows a *negative* gap where the controlled experiment measures +0.088. The controlled experiment holds the test set fixed and varies only the training regime, and **it is the one to quote**. Likewise, the external column here (0.642) is not the §19 headline of 0.752, which comes from the locked protocol with temperature scaling and the full feature set.

**If the board asks:** *"Why CORAL rather than a modern adversarial method?"* — Because both methods here are chosen for being **unsupervised and free at deployment**: no target labels, no model fitted on the target side. An adversarial or supervised method needs something you do not have in a live network. Slide 40 lists "domain adaptation was tried in only two forms" as a limitation, and CORAL was implemented from Sun and Saenko's paper rather than substituted for — which matters more than usual, because a negative result invites the reply that it was implemented badly.

---


---

## Slide 29 · *The quantity the deployed rule thresholds on is the weakest predictor available*
**The claim.** Dwell time beats the A3 gap by more than 0.30 AUROC. The rule triggers on nearly the worst single predictor in the feature set.

**On screen.** `fig17_mechanism` — single-feature AUROC at 1 s, ranked.

**Every number.**

| feature | AUROC | block |
|---|---|---|
| **serving dwell time** | **0.874** | history |
| serving SINR | 0.830 | RF |
| time since last A3 report | 0.703 | signalling |
| A3 reports in the previous 3 s | 0.685 | signalling |
| time since previous handover | 0.652 | history |
| A3 hold time (TTT clock) | 0.615 | signalling |
| **serving-to-neighbour gap** | **0.566** | RF |

Plus: the dominant profile (+1 dB, 1 dB hysteresis, 74.6% of handovers) fires when the gap falls below −2 dB, true of only **12.4%** of samples. Weighted by each profile's share of handovers, the entering condition is satisfied on **27.1%** of samples. Inside the firing region the observed handover probability rises from a **7.3%** base rate to roughly **20%** — real but modest.

**The reasoning — why dwell time wins.** Dwell time is a **sufficient statistic for a renewal-like process**: the longer the phone has been attached to a cell, the further it has travelled inside that cell's footprint, and the closer it is to the boundary. It summarises the entire trajectory into the handover in one scalar. The A3 gap summarises one instant.

And the gap condition is **necessary but nowhere near sufficient**, for three separate reasons:

1. It must hold **continuously through the time-to-trigger**, not just now.
2. The network weighs load and target availability.
3. The decision can simply go the other way — which is slide 30, and it is the biggest of the three: three in five resulting reports are declined.

The signalling features are informative *alone* (0.615–0.703) and largely redundant *in combination* — which is why adding the whole signalling block buys only +0.005 to +0.012 AUPRC (slide 39).

**If the board asks.**

- *"Isn't dwell time trivially predictive — of course a handover is coming eventually?"* — That is the mechanism, not an objection, and it is worth owning. The point is that an operator's rule ignores it entirely, and it is free: dwell time is a counter the phone already maintains. 0.874 from a counter, against 0.566 from the quantity the network actually thresholds on, is the finding.
- *"So should the network trigger on dwell time?"* — No, and I would not claim that. A3 is a *decision* rule that needs the radio to have actually changed; dwell time is a *forecast* input. They are different jobs. The claim is that a predictor built on dwell time can warn before A3 can fire.
- *"Is single-feature AUROC a fair measure?"* — It measures marginal information, not joint contribution, and I say so. It is the right diagnostic for *this* question — "is the rule's trigger quantity informative on its own?" — and the ablation results on slide 39 cover the joint question.
- *"Isn't the gap poor just because the neighbour columns are sparse?"* — Neighbour coverage after projecting the signalling reports onto the grid is 62–79% with a median report age of 0.36 s, and there is a missingness mask as a feature so the model can condition on availability rather than on an imputed value. Raising coverage from 28% to 79% is one of the measured negatives on slide 39 — it changed nothing.

---

## Slide 30 · *Three in five A3 reports are declined, and most of all on the highway*
**The claim.** 62.9% of A3 reports never become a handover within 2 s, the rate rises with cell size, and this independently replicates a US-operator finding.

**On screen.** `m09_conversion` — 7,385 A3 reports, the 2 s conversion decision, and the per-capture decline rates.

**Every number.**

| number | meaning |
|---|---|
| 7,385 | A3 report instants across 57 drives |
| **62.9%** | never followed by a handover within 2 s |
| 57.2 / 60.1 / 63.3 / **71.9%** | per capture: urban arterial / urban loop / dense urban / **highway** |
| 68.7% | the same quantity computed over **all** report types |
| 74.5% at 1 s, 54.6% at 3 s | the same quantity at other windows |
| 43–52% | share of measurement reports that are A3 at all |
| 69–87% | Ghoshal et al.'s non-conversion range across three US operators |

**The reasoning.** Reporting an event is not the same as acting on it. Three things sit between the report and the handover: the entering condition must hold continuously through the TTT, the network weighs load and target availability, and the decision can go the other way.

The per-capture ordering is the physically satisfying part: **the decline rate rises with cell size.** On a sparse macro layer with 1–2 km between sites, the entering condition is satisfied early and *stays* satisfied, and the serving cell can afford to wait. In a dense urban core the window is narrower and the network acts sooner.

**Two qualifiers belong in the same sentence as this number, always.** *Which reports* — only 43–52% of measurement reports are A3 at all; the rest are A1, A2, A4 and A5, which carry no handover entering condition. Over all report types the rate is 68.7%, and a document quoting that is answering a different question. *Which window* — at 1 s it is 74.5%, at 3 s 54.6%. **Neither qualifier is optional.**

**If the board asks.**

- *"You said this replicates Ghoshal. How close is it?"* — Directionally, and I say only that. They report 69–87% non-conversion across three US operators; I get 62.9% here. But their report set and window are not stated, and this slide shows both move the number by 10–20 points. So it is a directional replication on a different operator, continent and regulatory environment — not an exact one. My lower rate is what a more aggressive configuration should produce.
- *"Why 2 s?"* — It is the window over which a report that is going to convert has converted; at 3 s the rate falls to 54.6% because slow conversions catch up, at 1 s it rises to 74.5% because fast ones have not yet. 2 s is the middle and it is stated every time the number is.
- *"Can you predict which reports convert?"* — The thesis poses it as a task and the deck does not quote a number, because the four-capture re-run of that stage returned a degenerate result that I have not yet traced. **See Part 3 — this is a soft spot with a prepared answer.**

**Do not say** the number without both qualifiers. This is the single easiest place in the talk to be caught, because the same phenomenon has three defensible values.

---

## Slide 31 · *Handovers are strongly self-exciting: six in ten follow another handover*
**The claim.** Handover arrivals are strongly clustered and decisively non-Poisson; the branching ratio is 0.605; and the fitted kernel is itself rejected, which the thesis states.

**On screen.** `fig18_hawkes` — the fitted intensity and the branching ratio with its bootstrap interval.

**Every number.**

| | pooled | 10 Sept | 12 Sept | 13 Sept | **15 Sept highway** |
|---|---|---|---|---|---|
| background rate μ (/s) | 0.039 | 0.042 | 0.049 | 0.038 | 0.035 |
| **branching ratio n** | **0.605** | 0.649 | 0.609 | 0.567 | **0.513** |
| bootstrap 95% CI | [0.524, 0.673] | [0.454, 0.776] | [0.443, 0.740] | [0.363, 0.688] | [0.335, 0.629] |
| mean cluster size | 2.53 | 2.85 | 2.56 | 2.31 | 2.05 |
| excitation half-life | 6.4 s | 8.6 s | 4.1 s | 7.0 s | 4.1 s |

Goodness of fit:

| test | result | reading |
|---|---|---|
| LR vs homogeneous Poisson (boundary mixture null) | χ² = 256.6, **p ≈ 5 × 10⁻⁵⁸** | emphatically not Poisson |
| gamma renewal alternative | shape **0.78** (< 1 = clustered), KS p = 3 × 10⁻¹² | clustered; renewal rejected hard |
| **Ogata residual KS vs Exp(1)** | D = 0.074, **p = 7 × 10⁻⁴** | the exponential-kernel Hawkes is itself rejected |

**The reasoning.** In a Hawkes process the conditional intensity is `λ(t) = μ + Σ_{τ_j < t} g(t − τ_j)` — a background rate plus a contribution from every past event. The **branching ratio** `n = ∫g` is the expected number of direct offspring per event. `n = 0.605` means about 60% of handovers are self-triggered offspring rather than independent arrivals, and the mean cluster size is `1/(1−n) = 2.53`.

Stability across four independently captured days and two mobility regimes is what makes the estimate credible. The **highway sits lowest (0.513)**, which is the expected direction: wider cells, fewer boundaries per kilometre, less to oscillate between.

**The honest statement, and say it yourself.** The Ogata residual test — time-rescaling the events under the fitted model and testing the residuals against Exp(1) — **rejects the exponential kernel** (D = 0.074, p = 7 × 10⁻⁴). So:

> Handover arrivals are strongly clustered and decisively non-Poisson. An exponential-kernel Hawkes process fits far better than either a Poisson or a gamma renewal alternative, but is itself rejected by an Ogata residual test on the pooled data. So the branching ratio of 0.61 is **a calibrated measure of clustering strength under a stated kernel, not an exact generative model of the process.**

**If the board asks.**

- *"If the model is rejected, why report the number?"* — Because the number answers a comparative question the model is adequate for: *how strongly do handovers cluster, and is that stable across regimes?* It is rejected as an *exact* generative model, which would be a different and much stronger claim. Reporting the rejection is what makes the weaker claim credible.
- *"Why not fit a better kernel?"* — A non-parametric or multivariate kernel would fit better, and slide 41 lists it. With 938 events pooled and ~230 per capture, a non-parametric kernel would be estimating a function from a few hundred points, and the branching-ratio estimate would gain precision it has not earned.
- *"Isn't this just the ping-pong statistic again?"* — Related but not the same. Ping-pong is a *specific* pattern (A→B→A). The branching ratio counts *any* triggered handover, including A→B→C. That is why 60% self-excitation coexists with a 24.5% ping-pong rate.
- *"Why does the test reject if the fit is good?"* — Because with 930 events the test has power to detect a modest misspecification. The KS statistic is D = 0.074, which is a small deviation detected by a well-powered test, not a wild misfit. Saying that is better than pretending it did not reject.

---

## Slide 32 · *The same 938 handovers give a ping-pong rate anywhere from 24.5% to 41.3%*
**The claim.** Three definition choices are rarely stated, each is worth several points, and published ping-pong rates are therefore not comparable with one another.

**On screen.** `fig23_pingpong_definitions` — four rates on a fixed event set.

**Every number.**

| definition | rate | delta |
|---|---|---|
| A→B→A, cell = PCI **+ carrier**, 15 s (what the literature means) | **24.5%** | — |
| A→B→A, cell = PCI only | 29.0% | **+4.5** |
| any return inside the window, PCI only | 38.5% | **+9.5** |
| the same, ungrouped over all 957 raw events | 41.3% | **+2.8** |

Supporting: six carriers on this network, and PCIs repeat across them. Handovers arrive a **median 3.5 s** apart, **59.8% within 5 s**.

**The reasoning — the three choices, and why each one is worth what it is.**

1. **Cell identity: PCI alone, or PCI + carrier? (+4.5 points.)** A Physical Cell Identity is only unique within a carrier. This network runs six carriers, so the same PCI recurs on different frequencies. Counting by PCI alone marks an inter-frequency handover to a *different* cell that happens to share a PCI as a return to the same cell.
2. **The return rule: must it be the *next* handover, or any return in the window? (+9.5 points — the biggest.)** Handovers arrive a median 3.5 s apart, so a 15 s window typically contains three or four handovers. "Any return within 15 s" therefore catches A→B→C→A, which is not a ping-pong in the sense anyone means.
3. **The event denominator: grouped by drive, or all raw events? (+2.8 points.)** Ungrouped counting lets a "return" span a drive boundary — a different session, minutes later.

**The thesis quotes 24.5% and states all three choices in the same sentence.** The finding is that published ping-pong rates are not comparable with each other. That is a result, not a complaint — and it is the safest kind, because it is arithmetic on a fixed event set. There is nothing to attack.

**If the board asks.**

- *"So which is the true rate?"* — All four are true; they measure different things. 24.5% is the one that matches what the literature means by ping-pong and it is what the thesis quotes. If someone else's paper says 35%, my first question would be which of these three choices they made, and their paper will usually not say.
- *"Why 15 seconds?"* — It is the literature-standard window, used so the number is comparable. The 10 s window in the pipeline's own configuration gives a lower rate; both are computed and the thesis reports the 15 s figure for comparability.
- *"This project has quoted 28.3%, 29.4% and 43.2% elsewhere."* — Yes, in earlier internal reports, and all three are correct arithmetic on the same events under different choices. That inconsistency is exactly what motivated this slide. Report 25 reconciles all of them and the index marks the earlier documents accordingly. **Volunteer this if the board has read the internal reports.**

---

## Slide 33 · *Ping-pong is one carrier layer and one A3 profile, not speed*
**The claim.** Ping-pong concentrates in intra-carrier handovers under one A3 profile; speed is explicitly tested and is not the driver; and the lever is a single time-to-trigger parameter.

**On screen.** `fig24_pingpong_mechanism` — rate by carrier relationship, by A3 profile, and by regime.

**Every number.**

| cut | rate | n |
|---|---|---|
| **intra-carrier** | **31.0%** | 690 |
| **inter-carrier** | **6.5%** | 248 |
| **+1 dB, TTT 320 ms** | **29.2%** | **679 (72% of all handovers)** |
| −10 dB, TTT 640 ms | 10.5% | — |
| −15 dB, TTT 160 ms | 11.0% | — |
| highway (49.5 km/h mean) | **31.1%** | — |

The negative-offset profiles are the **inter-frequency** ones (74–79% carrier-changing) and barely oscillate.

**The reasoning — and this is the most actionable finding in the thesis.** Follow the chain:

1. Ping-pong is five times more likely when the handover stays on its carrier (31.0% vs 6.5%). Intra-frequency neighbours overlap heavily; inter-frequency handovers are usually a deliberate layer change with a large margin.
2. The A3 profile that carries 72% of handovers is +1 dB offset with a **320 ms** time-to-trigger, and it returns 29.2%. The two negative-offset profiles return 10.5% and 11.0% — and those are the *inter-frequency* ones, so cuts 1 and 2 are the same fact seen twice.
3. **It is not the negative offsets.** The aggressive-looking −15 dB profile is one of the *low* ping-pong ones.
4. **It is not speed.** The obvious hypothesis is that faster motion crosses boundaries faster. The highway, at 49.5 km/h mean, returns 31.1% — essentially identical to the urban intra-carrier rate. Speed is tested and rejected.

What is left is a **short time-to-trigger on a dense intra-frequency layer**. 320 ms is not long enough for the Layer-3 filter to distinguish a real boundary crossing from a fade, so the phone hands over on a transient and comes straight back.

**And that is a parameter someone can change on a Monday morning** — which is why this is worth saying. It is the one operational recommendation in the talk that follows directly from measurement.

**If the board asks.**

- *"Would raising the TTT actually help?"* — The measurement supports the direction: 640 ms returns 10.5% against 320 ms at 29.2%. But those profiles differ in offset and carrier type too, so it is an association, not a controlled experiment. **The controlled version would be an A/B trial on TTT alone**, which needs operator cooperation. I would state the recommendation exactly that strongly and no more.
- *"Couldn't it just be that intra-frequency cells are smaller?"* — Partly, and that is the same physical story: denser overlap, more boundaries, more opportunities to oscillate. The point is that it is a layer-and-configuration effect rather than a mobility effect, and the speed test is what separates those.
- *"Is 24.5% high compared with published rates?"* — Compared with the numbers people quote, yes. But slide 32 is the caveat: the comparison is only meaningful if the other study states its three choices, and most do not. Zidic et al. (2023) is the closest careful treatment in real 4G networks.

---


---

## Slide 34 · *A warning earns its alarm budget only up to about 20% of samples*
**The claim.** Coverage must be read against a same-rate random alarm; on that reference the predictor earns its keep below about a 20% budget; and a prediction of the author's own was refuted.

**On screen.** `fig20_benefit` — excess coverage over a same-rate random alarm, by alarm budget.

**Every number.**

| alarm budget | ping-pongs warned | same-rate random alarm | **excess** |
|---|---|---|---|
| 2% | 39.4% | 18.4% | **+0.21** |
| 5% | 73.6% | 40.1% | **+0.34** |
| 10% | 90.0% | 65.1% | **+0.25** |
| 20% | 93.7% | 89.3% | **+0.04** |
| 40% | 96.7% | 99.4% | **−0.03** |

Four captures, **269 ping-pong events** in the evaluated folds. Three-capture envelope: +0.21 / +0.32 / +0.22 / +0.03 / −0.02 — the shape is unchanged.

Dedicated ping-pong model: **AUROC 0.51** (0.486–0.518 across seeds, lift 0.95–1.01), against 0.670 on three captures. Coverage at a 10% budget: generic model **90.0%** against the dedicated model's **30.9%**.

**The reasoning.** "90% of ping-pongs warned at a 10% alarm budget" sounds excellent until you notice that a coin flip alarming at the same 10% rate catches 65.1%. **Two thirds of the headline is what chance achieves.** The excess column is the only honest reading, and it peaks at a 5% budget (+0.34) and goes negative by 40%, where the warning window is wide enough that random alarms catch nearly everything.

**The refuted prediction.** A dedicated ping-pong predictor was trained specifically to test whether the generic handover model was the wrong ranker for this task. It is not. On four captures the dedicated model is at **chance** — starker than the 0.670 it reached on three. The reason is almost obvious in hindsight and worth saying: **every ping-pong is a handover, and handovers are far more predictable than the subset.** Ranking by handover imminence catches ping-pongs far more efficiently than ranking by "is this one a ping-pong".

**If the board asks.**

- *"Why is the benefit an upper bound rather than an estimate?"* — Because it is a **counting** bound under a *stated* actuator efficacy. It says: if you could suppress every warned ping-pong, this is how many you would suppress. It does not estimate what suppression would actually achieve, because the causal effect is not identified here — the logging policy is deterministic, so propensities are 0 or 1 and doubly-robust estimators collapse to the direct method. Slide 40 states this and slide 41 gives the identifiable alternative.
- *"Why did the dedicated model get worse with more data?"* — Because 0.670 on three captures was probably optimistic on a small positive set, and the fourth capture both added events and made the folds more heterogeneous. Either way the conclusion is the same and now stronger. I would rather report that it went from "weak" to "chance" than quietly keep the better number.
- *"Isn't a negative result on your own idea a weakness?"* — It is the fourth conclusion of the thesis. It was a specific, pre-registered-in-spirit prediction, it was measured, and it was wrong. Reporting it is what makes the six measured negatives on slide 39 credible as a set.

---


# PART 4 — What has been achieved?

---

## Slide 35 · *The nearest published method on this network scores 0.489 where this work scores 0.921*
**The claim.** The closest comparator — same operator, city, instrument and department — was reimplemented, scored generously, and is close to uninformative as a predictor; and its learned component performs worse than the reward function it was trained on.

**On screen.** `m10_departmental` — the reimplemented baseline, arm by arm.

**Every number.** Grouped-drive rotation over the neighbour-present rows, 1 s horizon:

| model | AUPRC | lift | AUROC |
|---|---|---|---|
| **ours, LightGBM, 107 features** | **0.824** | **6.95×** | **0.921** |
| ours, LightGBM on *their* 5-D state | 0.473 | 3.99× | **0.766** |
| rank by their reward directly, no RL | 0.162 | 1.29× | **0.614** |
| **their Q-learning agent** | 0.146 | 1.17× | **0.505** |
| their HOM/TTT gate alone | 0.134 | 1.07× | 0.523 |

Under their own capture-to-capture design the ordering is identical: ours 0.754 / 0.891, their agent 0.129–0.138 / 0.57–0.58. Models are restricted to the **58.9%** of samples carrying a neighbour measurement — the row population their event-triggered dataset always has.

**The method being compared:** a contextual-bandit formulation of the handover *decision*, solved with tabular Q-learning over a five-dimensional state (serving RSRP, RSRQ, neighbour RSRP, RSRQ, serving CINR), with a hand-specified reward gated on HOM = 3 dB and TTT = 1 s, and nearest-neighbour lookup into the Q-table at test time.

**Three choices made in their favour** — have these ready, because "is this fair?" is the certain question:

1. Scored by its **advantage** `Q(s,1) − Q(s,0)` rather than its thresholded action, so it is credited with the full learned signal rather than a binary decision.
2. Every model restricted to the 58.9% neighbour-present rows — the population their own event-triggered dataset always has.
3. Their TTT gate evaluated **both** as written and in the near-vacuous form their own row spacing produces, with the **more favourable** result quoted.

**The reasoning — two findings, and the second is the memorable one.**

**The gap is the method, not the features.** Their five inputs are informative: my learner reaches AUROC 0.766 on that exact state vector. Their agent extracts 0.505 from the same five numbers. So this is not "my data is better".

**The reinforcement learning does negative work.** Ranking by `r(s,1) − r(s,0)` — their reward function evaluated directly, no episodes, no table — scores **0.614** against the trained agent's **0.505**. Why: a Q-table keyed by continuous vectors is visited roughly once per row, so nearest-neighbour inference into it is a lossy approximation of a closed-form reward the authors had already written down.

**Their evaluation consumes the future.** Their published gate accepts an action only if the handover-margin condition persists for TTT seconds *after* the decision instant. That is legitimate for a *decision* the network waits to make. It is inadmissible as evidence of *prediction*, because it moves the decision to `t + TTT`.

**⚠ Citation status.** No publication record for that study could be found; it is held as a manuscript PDF and marked unpublished in the bibliography. Its **dataset** is published with a DOI and is the external validation set on slide 27. **If it is still unpublished at submission, this comparison must be made without a citation — or with the authors' agreement — rather than against a reference a reader cannot retrieve.** Know this; it is a real procedural issue and the board may raise it.

**If the board asks.**

- *"Is it fair to compare a decision method to a prediction method?"* — No, and I say so explicitly: it optimises a decision while this work forecasts an event. The narrow, fair statement is that **used as a predictor of handover imminence on signalling ground truth**, the nearest published method on this network is close to uninformative. That is the only claim I make, and it is the relevant one because the deck's whole question is prediction.
- *"Did you reimplement it faithfully?"* — It specifies its method completely enough to reimplement without substitution, and it was reimplemented from its method section and reward algorithm and run under both its own train/test design and mine, with the same ordering either way. The three favourable choices above are documented.
- *"Isn't 0.505 suspiciously exactly chance?"* — It is what a lossy nearest-neighbour lookup into a sparsely-visited continuous-keyed Q-table would produce. The evidence that it is real rather than a bug is the reward arm: the same reward function, evaluated in closed form, scores 0.614. The table is destroying signal the reward already contained.

**Do not say** their paper is bad. Say it optimises a different objective, and that as a predictor on this ground truth it is close to uninformative — and that its own reward beats its own agent, which is a statement about the Q-table, not the authors.

---

## Slide 36 · *The two comparisons with the literature that are actually fair* · [optional]
**The claim.** Compare by reimplementation or by protocol, never by quoting numbers across datasets — and here is the proof that quoting across datasets is meaningless.

**On screen.** `fig26_literature_headtohead` — reimplementation left; the accuracy trap right.

**Every number.** 654 rows, same protocol, on the four-capture dataset. Always saying "no handover" scores **93.3% accuracy** here and **6.7% AUPRC**. **7 of 22** audited papers quote accuracy on an imbalanced task; their prevalences run 0.86%–11%, and three of their headline figures are 98.03%, 99.84% and 94.83%.

**The reasoning.** Two comparisons are defensible: reimplementing a method and running it on your data (slide 35), and auditing protocol (slide 6). Everything else — "their paper got 97%, mine gets 93%" — compares datasets, not methods.

The right-hand panel is the proof, and it is deliberately self-deprecating: on *my* data, a trivial constant predictor scores 93.3% accuracy. That is higher than several published headline figures. It establishes that accuracy on an imbalanced task carries no information about the model.

**If the board asks:** *"So you can't compare with the literature at all?"* — Not on headline numbers, and I think that is the honest position rather than a limitation of my work. I compare in the two ways that are valid: I reimplemented the nearest method and ran it on my data, and I audited 22 papers on protocol. Cross-dataset accuracy comparisons appear nowhere in this thesis.

---

## Slide 37 · *Every method here is borrowed on purpose; what is new is where each one is pointed*
**The claim.** The novelty, stated with provenance first: six components, each with its primary source, and what this thesis does with it that has not been done.

**On screen.** `fig28_novelty` — a three-column table: **component** · **borrowed from** · **what is new here**, in maroon. A closing italic line: two tasks fall out of the signalling that the literature has not posed.

**Every row.**

| component | borrowed from | what is new here |
|---|---|---|
| Discrete-time survival | Wiegrebe et al. 2024 (review) | Pointed at handover: horizon coherence by identity, for any learner — **0% violations against 43.6%** |
| Conformal risk control | Angelopoulos et al. 2024; Cohen 2022, Simeone 2025 in wireless | The exchangeable unit is the **drive**, not the sample, giving a campaign-design rule **n ≥ 1/α − 1** |
| Self-exciting point process | Hawkes 1971; Ogata 1988 | A branching ratio for handover arrivals — **0.605**, stable over four captures, kernel residual-tested |
| Grouped cross-validation | standard ML practice | Measured what it is worth on drive-test radio: **+4% to +74%**, architecture-dependent, so it **reorders** |
| Signalling decoding | Deng et al. 2018 (IMC) | A configuration timeline for message-scoped `measId`; the deployed offsets are **negative**, not the assumed +3 dB |
| Unsupervised adaptation | Sun and Saenko 2016 (CORAL) | Reported as a measured negative rather than omitted, matched against a nine-method published benchmark |

Plus two tasks: **report conversion** (will the network act on a report it was just sent?) and **a ping-pong rate whose definition is stated**.

**Why this slide exists, and why here.** "What is actually novel?" is the question a defence board is most likely to hold in reserve. This slide answers it before it is asked — and it answers it in the *safest* possible order: provenance in the left two columns, so the right column is what is genuinely left over. Claiming less makes what remains much harder to dispute.

It sits **after** the two comparison slides (34 and 35), because a novelty claim made before the evidence sounds like a promise and after the evidence sounds like a summary.

**The reasoning.** The pattern across the six rows is deliberate and worth naming out loud: **the contribution is repeatedly a matter of where a mature method is aimed, and what unit it is applied to.** Survival analysis has existed for decades — aiming it at handover is what buys horizon coherence. Conformal prediction is in wireless already — choosing the *drive* as the exchangeable unit is what produces a guarantee an operator can use, and a rule that says how much driving a campaign needs. Grouped splitting is standard practice — *measuring* what ignoring it is worth on this kind of data is what turns a convention into a finding.

Two of the six are **negatives**, and that is deliberate rather than apologetic. A measured null is a contribution when the method is implemented from its primary source rather than substituted for — which is exactly why CORAL was implemented from Sun and Saenko's paper, and why the Ismail Fawaz benchmark is cited beside it.

**If the board asks.**

- *"So you invented nothing?"* — No new estimator, no new architecture, and I would rather say that plainly than have it discovered. What is new is the pairing and the protocol: a discrete-time hazard aimed at handover, a conformal guarantee whose unit is the drive, a branching ratio for handover arrivals, and an audit of 22 papers that none of them satisfies. Borrowing well is a contribution when the pairing is new and the protocol is honest.
- *"Which of these six would survive on its own?"* — The first two. The hazard formulation generalises past this dataset entirely: the coherence property holds for any learner and any horizon set, so anyone doing multi-horizon event prediction can use it. The feasibility floor `n ≥ 1/α − 1` is algebra and applies to any campaign that wants a distribution-free guarantee.
- *"Is 'measuring what grouped splitting is worth' really novel?"* — The *practice* is not. The *measurement on this data* is, and it produced something not obvious: the inflation is not a constant offset, it scales with architectural memory — 74% for a GRU, 4% for logistic regression — so a leaked comparison does not just raise the scores, it reorders them. That is a reusable number.
- *"Why is report conversion a new task?"* — Because it is only visible if you decode the control plane. The literature predicts *handovers*; this asks whether the network will act on a report it has already been sent. Ghoshal et al. measure the rate; nobody models it. I pose it and report the measurement — slide 30 — and deliberately quote no predictor figure today (see Part 3).
- *"How does this differ from appendix F?"* — Appendix F is the same argument at source-by-source granularity, for a board member who wants to check a specific citation. This slide is the version that fits in thirty seconds.

**Do not say** "first ever" about anything. Say "I found none in 108 screened references", which is a claim about your search rather than about the world, and is the only version you can defend.

---

## Slide 38 · *Objectives, evidence, and the boundary of each claim*
**The claim.** All five objectives closed against their evidence, each with the boundary of the claim stated in the same row — plus one row for the thing that was not achieved.

**On screen.** Three columns: **Objective** · **Evidence delivered** · **Status and boundary**, six rows.

**Every row.**

| objective | evidence | status and boundary |
|---|---|---|
| **O1** Multi-horizon prediction | five horizons; 1 s AUPRC 0.784, AUROC 0.933, ECE 0.024 — 11.7× the floor | Met — on 57 drives, one operator, four days |
| **O2** A credible benchmark | seven learners, grouped rotation over 5 seeds, equal tuning budget, leakage study | Met — the tuned arm is still a three-capture run |
| **O3** Usable probabilities | 0% coherence violations against 43.6%; ECE −0.006 to −0.029; a certified per-drive bound | Met — under per-drive exchangeability, stated |
| **O4** Generalisation | leave-one-capture-out 0.909 to 0.949; external 0.752 against that data's own 0.745 | Met — a four-point design, not a large sample |
| **O5** Mechanism | dwell 0.874 against the A3 gap 0.566; 62.9% of reports declined; branching ratio 0.605 | Met — the Hawkes kernel is misspecified, and said so |
| **(not claimed)** Network benefit | a counting upper bound against a same-rate random alarm; no controlled intervention | Future work — off-policy evaluation is unidentified |

**Why it exists, and why here.** This is the payoff of slide 9 and, structurally, the most persuasive slide in the deck — not because the numbers are new (every one has already appeared) but because the board can audit the promise against the delivery in one view. It sits in Part 4 after the positioning and novelty slides, so by the time it appears the evidence column is a reminder rather than a claim.

**The reasoning — the boundary column is the point.** Any deck can list what it achieved. What makes this credible is that every row names its own limit *in the same sentence*, and that the limits are specific rather than modest-sounding: not "results may not generalise" but "a four-point design, not a large sample"; not "some caveats apply" but "under per-drive exchangeability, stated".

**And the sixth row is deliberate.** Listing a thing you did **not** achieve, in the same table and the same format as the five you did, is what makes the five believable. It also pre-empts the most likely hostile question — *"so does this actually improve the network?"* — by answering it before it is asked, and by explaining why the answer is not available rather than apologising for it.

**If the board asks.**

- *"You say O2 is met but the tuned arm is a three-capture run. Is it met or not?"* — Met, because O2 is a claim about *ordering* — that no tuned sequence model overtakes an untuned logistic regression — and the four-capture headline table shows the identical ordering. The tuned arm is re-run before submission, and nothing in the contributions depends on the tuned figures themselves.
- *"What would move 'not claimed' to 'met'?"* — A fuzzy regression-discontinuity design at the A3 boundary, which is the first item on slide 41. It is identifiable on data this campaign already has, and it is the honest alternative to off-policy evaluation, which is unidentified here because the logging policy is deterministic.
- *"Which of the five is weakest?"* — O5, because 'explain the mechanism' is the least falsifiable objective. What holds it up is that it names its quantities in advance: the single-feature ranking, the conversion rate and the branching ratio, each reported with an interval or a goodness-of-fit test — including the one that rejects my own kernel.

**Do not say** "all objectives achieved". Say "met, on the evidence stated", and then read the boundary column. The qualifier is what makes the claim survive.

---

## Slide 39 · *More information and more machinery did not help; formulation and configuration did*
**The claim.** Six things were added in good faith, measured, and reported as nothing; three things moved the result.

**On screen.** `fig22_negatives` — six measured negatives above the line, three winners below it.

**Every number.**

| added in good faith | result |
|---|---|
| neighbour coverage 28% → 79% | no accuracy change |
| explicit self-excitation features | no accuracy change |
| the full RRC signalling block | +0.005 to +0.012 AUPRC |
| a dedicated ping-pong target | at chance on 4 captures (AUROC 0.51) |
| zero-cost domain adaptation | worse, on both sides of the transfer |
| an equal tuning budget for every model | ordering unchanged |

| what actually moved the result | by how much |
|---|---|
| reformulating as a discrete-time hazard | coherence + calibration from one fit |
| the A3 configuration regime | Δ AUROC 0.088 (controlled pair) |
| grouping the split by whole drive | removes a +20% to +74% inflation |

**The reasoning.** The pattern across five independent channels is the point: **more information did not help; formulation and protocol did.** Every row above the line is a hypothesis someone would reasonably have expected to work, and each was measured rather than assumed. That is the only reason the pattern is worth stating — a list of things that did not work is worthless unless each was genuinely tried.

The self-excitation row is the sharpest: the process *is* strongly self-exciting (0.605 branching ratio, slide 31), and adding explicit self-excitation features changes nothing — because the history block already carries time-since-last-handover and handover-count, so the information was in the model before the features were named.

**If the board asks.**

- *"How do you know these are real negatives and not failed implementations?"* — Each is a controlled comparison under the same protocol, same folds, same seeds, and each has a stated mechanism for *why* it fails. The domain-adaptation row additionally matches a published nine-method benchmark (appendix C). A negative with a mechanism is a result; a negative without one is a bug.
- *"Why is the A3 configuration regime a 'winner' if it makes things worse?"* — Because "moved the result" means "changed the answer materially". Configuration shift costs 0.088 AUROC and no feature recovers it — that is a large, real, actionable effect. Most of the things above the line moved nothing at all.
- *"Isn't publishing negatives just padding?"* — Only if they are cheap. Each of these cost a stage and an experiment, and two of them were predictions of mine that turned out wrong. The deck's fourth conclusion is that they were measured and published rather than discarded.

---


---

## Slide 40 · *What this work cannot claim*
**The claim.** Five limitations, each paired with the measurement that bounds it.

**On screen.** Five bullets: scale · sampling rate · cross-regime transfer · no causal estimate of the actuator · the Hawkes kernel is misspecified.

**The reasoning — the full list, including the four that are not on the slide.** The thesis's limitations section has more than the slide shows. Know all of them; a board member who has read the thesis may ask about one that is not on screen.

| limitation | the number that bounds it |
|---|---|
| **Sampling rate** | 1 Hz caps event *detection* at 90.5%. Does **not** cap horizon resolution (§6.4). Cannot be raised with the available licence. |
| **Scale** | 57 drives, 10,260 samples, 938 handovers, two corridors, one operator, four days. Enough for 57 bootstrap groups and a four-point leave-one-capture-out design; not enough for generality across cities or operators. |
| **Cross-regime transfer** | One regime pair, one direction. Only two A3 profiles clear the 60-handover bar on an identical 591-row, 13-drive test set. |
| **The Hawkes kernel** | Misspecified, and §22 says so. The branching ratio is descriptive, not generative. |
| **The tuning budget** | 20 trials. Small *equally* for every model, which is what makes it fair. Lean on the direction, not the figures. |
| **Domain adaptation** | Tried in only two forms, both unsupervised. A supervised or adversarial method might recover the gap; nothing here rules that out. |
| **No causal estimate of the actuator** | Off-policy evaluation is **unidentified**: the logging policy is deterministic, so propensities are 0 or 1 and doubly-robust estimators collapse to the direct method. |
| **The grouped-split claim narrowed twice** | Pass 2 found one paper splitting by time; pass 3 added travel day and deployment event. The claim is now "none holds out the mobility unit", not "almost nobody groups". |
| **The conformal contribution narrowed** | Cohen et al. and Simeone et al. got to wireless conformal first. What is specific here is the exchangeability unit and the KPI, not the machinery. |
| **Four bibliography entries** | `verified=partial` on an author list; to be completed before submission. |
| **The deep-ensemble arm** | Implemented but not reported — `stage03_uncertainty` was never re-run on the pooled XCAL captures. Currently code without a result. Either re-run or drop before submission. |
| **QoE targets** | Not modelled: the captures carry PHY throughput but not application-layer RTT or loss. |

**If the board asks.**

- *"Why is off-policy evaluation unidentified? Explain it."* — Off-policy evaluation needs the logging policy to have assigned a non-zero probability to both actions in each state, so you can reweight. Here the logging policy is A3, which is **deterministic**: given the radio state and the configuration, it either fires or it does not. Propensities are 0 or 1. Inverse-propensity weighting divides by zero, and doubly-robust estimators collapse to the direct method — which means you are just trusting a model, not estimating a causal effect. The identifiable alternative is a **fuzzy regression discontinuity** at the A3 boundary, which is slide 41.
- *"1 Hz caps you at 90.5% — is the whole result therefore capped?"* — Only the *event-level* numbers. Row-level metrics — AUROC, AUPRC, ECE — are unaffected, and the horizon resolution is unaffected because the event clock is millisecond-precise. Every event-level number in Part II is read against the 90.5% ceiling and I say so each time.
- *"You say 57 drives isn't enough for generality — so what is the result good for?"* — It is good for the claims it makes: that handover is predictable well ahead of the rule, that formulation beats information, that leakage is architecture-dependent, and that the protocol matters. None of those requires generality across operators. The leave-one-capture-out design is the strongest generalisation evidence a four-day campaign can produce, and I state it as a design rather than a sample.

**Do not apologise while delivering this slide.** Every limitation has a number attached, which turns it from a weakness into evidence that you know the size of your own uncertainty. Deliver it at normal pace.

---

## Slide 41 · *Four directions, and one of them makes the causal question identifiable*
**The claim.** Future work that is specific enough to be a plan, and the first item closes the hole the previous slide just admitted to.

**On screen.** Four items: fuzzy regression discontinuity at the A3 boundary · a second corridor and a third A3 regime · close the loop to an outcome · release the code and the dataset.

**The reasoning on the first item — know this one properly.** A3 has a **sharp boundary**: the entering condition is a threshold on a continuous quantity (the serving-to-neighbour gap, relative to the offset and hysteresis). Near that threshold, whether the condition fires is *as good as random* with respect to everything else — a fraction of a dB either way is measurement noise, not a systematic difference in the drive.

That is the setup for a **regression discontinuity** design: compare outcomes for drives just inside and just outside the firing condition. It is *fuzzy* rather than sharp because crossing the threshold does not deterministically produce a handover — three in five reports are declined (slide 30) — so the threshold is an instrument for the treatment rather than the treatment itself.

This is the identifiable route to the causal effect that off-policy evaluation cannot give, and it uses data this campaign already has.

**If the board asks.**

- *"What would the second capture actually buy you?"* — It turns a single regime pair into a matrix. Right now cross-regime transfer rests on two profiles in one direction (slide 40). A third regime gives six ordered pairs and turns an observation into a trend.
- *"What does 'close the loop to an outcome' mean?"* — Connecting the 2 s warning to a measured throughput or interruption effect, rather than the counting upper bound on slide 34. That needs either an actuator you control or the RD design above.
- *"Why is releasing code a contribution?"* — Because 2 of the 22 audited papers release code and 1 releases data. In a literature where protocol is the binding constraint, a release is a citable output in its own right.

---

## Slide 42 · Conclusions
**On screen.** Four numbered conclusions. **Leave this up for the entire Q&A** — it is the frame you want the board arguing inside.

| # | The conclusion | The number behind it |
|---|---|---|
| 1 | Handover is predictable well ahead of the rule that causes it | AUROC 0.933, AUPRC 0.784 at 1 s, 11.7× the floor, ECE 0.024, per-drive bound, **unchanged when a highway capture was added** |
| 2 | Formulation beats information | One hazard fit → coherence + calibration + ranking; five information channels → nothing |
| 3 | The protocol is as much the contribution as the model | Grouped splits, prevalence floor, event-level costs, distribution-free bound — 0/22 audited papers report the last three |
| 4 | Negative results were measured and published, not discarded | Six measured negatives, including one prediction of the author's own that was refuted |

**If the board asks:** *"If you had to pick one contribution, which?"* — The discrete-time hazard formulation, because it is the one that generalises past this dataset: the coherence property holds for any learner and any horizon set, so anyone doing multi-horizon event prediction can use it. The protocol findings are close behind but they are about this literature; the formulation is about the problem.

---

## Slide 43 · References
Sixteen primary references in two columns; 108 screened, 93 verified against the publisher or author record. Do not read it.

**If the board asks:** *"Why only sixteen?"* — These are the ones cited in the talk. The full bibliography is 108 screened references with a 22-paper protocol audit; 93 are fully verified and 15 remain to re-check before submission, four of which are `verified=partial` on an author list.

---

## Slide 44 · Thank you
Advance **back to slide 42** as soon as questions begin.

---

# Appendix slides — what each is for, and the numbers on it

| # | Appendix | The question it answers | The numbers on it |
|---|---|---|---|
| **45** | A — The configuration-timeline defect | *"How do you know the flat parse was wrong?"* | 43% of reports carry no neighbour → 99.4% A3 attribution is arithmetically impossible. The log itself shows **1,424 A1, 1,401 A2, 1,309 A3** configurations in one capture. |
| **46** | B — The hazard identity, panel by panel | *"Why not just calibrate five heads?"* | Calibration is per-horizon and nothing couples the horizons; the product-limit identity couples them **before** any calibration. Multi-head + isotonic: 48.7% violating rows, max 0.596. |
| **47** | C — Domain adaptation, arm by arm | *"Did you try domain adaptation?"* | Regime: none 0.819/0.865; CORAL 0.800/0.771; per-drive z 0.796/0.699. External: none 0.848/0.642; z 0.809/0.567; CORAL 0.848/0.534. Matched-domain AUROC falls too (0.819 → 0.796/0.800), ruling out a robustness trade. |
| **48** | D — Report conversion, in numbers | *"Isn't report conversion just the A3 rule restated?"* | The gate is satisfied for **every** one of these reports and three in five are still declined. 57.2 / 63.3 / 71.9% by cell size. |
| **49** | E — The departmental comparison, arm by arm | *"Is that comparison fair?"* | Three choices made in their favour (advantage scoring, their row population, their more favourable gate reading). Their published TTT filter consumes TTT seconds of the future → inadmissible as evidence of prediction. |
| **50** | F — The 18-stage pipeline | *"Is this reproducible?"* | A rebuild from the raw captures returns 10,260 samples and 938 handovers exactly. 17 passing tests; grouping by drive is enforced in the split constructor, not by convention. |
| **51** | G — The four-literature map | *"Has nobody really done this?"* | Measurement, prediction, survival and conformal converge on an empty centre. Survival and point processes have never been aimed at a drive test; conformal entered wireless for i.i.d.-within-frame tasks. |
| **52** | H — Two narrowed claims | *"Isn't wireless conformal already done?"* / *"Surely somebody groups?"* | Conformal: Cohen 2022 and Simeone 2025 got there first; theirs is over prediction SETS for i.i.d.-within-frame tasks, mine is a RISK guarantee on an operator KPI over a per-drive exchangeable stream. Grouping: 10 of 22 state no split, 5 split coarser than a row, none holds out the mobility unit for a per-timestep task on measured radio. |

---

# PART 2 — Cross-cutting question bank

Questions that are not about one slide. Organised by the angle an examiner comes from.

## The "is it real?" angle

**"Your AUROC is higher than most published handover predictors. Why should I believe it?"**
Three reasons, in order. First, the split is grouped by whole drive, and slide 23 measures what a careless split is worth — up to +74%. Second, the mechanism is not exotic: dwell time alone reaches 0.874, so most of the signal is a counter the phone already keeps. Third, a whole capture held out — new corridor, new speed regime, driven after the model was frozen — comes back at 0.927. If this were an artefact, that test is where it would break.

**"Could the model be reading the handover from a feature?"**
The one place that could happen is the measurement-report count, because a report precedes its handover command by 50–200 ms, which is inside one sample. The window is therefore half-open at `t − Δ`, not `t`. Seven unit tests pin exactly that, including the boundary case. Everything else is backward-looking and closed at *t*, and no window or slope crosses a drive boundary.

**"How much of the result is just the 13 signalling features?"**
Almost none: adding the whole signalling block is worth +0.005 to +0.012 AUPRC. That is one of the six measured negatives on slide 39. The signalling matters for **ground truth**, not for features.

**"Show me you didn't tune on test."**
Nested throughout: inner `GroupKFold(3)` on training drives only, objective computed inside the training folds, scaler and calibrator fitted per fold on training rows only, conformal threshold certified on calibration drives disjoint from test.

## The "is it enough?" angle

**"Fifty-seven drives."**
Agreed, and I bound it rather than argue about it. Every interval is a cluster bootstrap over drives (B = 400, or 1,000 for headline tables). Every claim is paired across 20 fold-seed observations. And the four-point leave-one-capture-out design is the strongest generalisation test a four-day campaign supports. It is a strong design, not a large sample, and I say that in those words.

**"One operator, one city."**
Yes, and slide 40 says so. What one operator buys is that the deployed configuration is **measured** rather than assumed, which is what makes the configuration-regime result possible at all. The partial answer to generality is the external dataset on slide 27, where the model reaches that dataset's own in-domain ceiling.

**"Four days is not a longitudinal study."**
Correct, and I make no temporal claim. The leave-one-capture-out design treats each day as a held-out unit, which is the nearest thing four days supports.

## The "why this method?" angle

**"Why LightGBM and not deep learning?"**
I ran three sequence architectures, gave them an equal tuning budget, and reported that they gained a lot and still lost. On 57 drives there is not enough data for them to learn anything the 107 hand-built features do not already carry — and the 10 s window they consume costs them the leakage exposure on slide 23. That is a statement about my sample size, not their architectures.

**"Why not a Cox model / continuous-time survival?"**
The data is on a fixed 1 Hz grid and the horizons of interest are a handful of grid multiples, so discrete time makes the likelihood a sequence of per-interval Bernoullis any classifier can fit. A continuous-time model would need a baseline hazard specification and buys nothing here.

**"Why conformal risk control rather than prediction intervals?"**
Because an operator acts on an alarm, not an interval, and is charged for missed handovers per drive. Risk control bounds that quantity directly. Prediction sets bound something an operator would not use.

**"Why AUPRC rather than F1 or accuracy?"**
AUPRC is threshold-free and prevalence-sensitive, so it can be read against a floor. F1 fixes a threshold, which hides the operating-point choice. Accuracy is meaningless here — slide 36 shows a constant "no" scoring 93.3% on this data.

## The "so what?" angle

**"What would an operator actually do with this?"**
Two things, at different confidence levels. With high confidence: the ping-pong analysis points at one parameter — a 320 ms time-to-trigger on the intra-frequency layer — that accounts for most of the returns, and that is a configuration change. With lower confidence: at α = 0.20 the certified threshold alarms on 23% of samples with a guaranteed per-drive miss rate, which supports a cheap pre-emptive action such as pre-fetching a target-cell context. I do not claim a throughput benefit, because that causal effect is unidentified here.

**"Is 2 seconds of warning actually useful?"**
It is enough for context pre-fetch, for scheduling decisions, and for suppressing a handover that is about to ping-pong. It is not enough for anything requiring core-network signalling. And the honest measurement is the pair: 44.7% of events at 1 s with 0.46 s median lead, 65.1% at 5 s with 1.80 s median lead.

**"Who is the audience for the protocol findings?"**
Anyone building a per-timestep predictor on drive-test data — which, per the audit, is a live and growing area with an unstated-protocol problem. The leakage result in particular is a number anyone can use to reinterpret an existing published result.

## The hostile-but-fair angle

**"You spend a lot of the talk on what didn't work."**
Six of the ~36 slides, and deliberately. The pattern across five independent channels — more information did not help, formulation and protocol did — is one of the four conclusions. And a list of negatives is only worth anything if each was genuinely tried under the same protocol, which is why each one has a controlled comparison and a stated mechanism behind it.

**"Every method here is borrowed."**
Every component has a primary source and I cite it in the section that uses it, not only in related work. What is new is where they are pointed: a discrete-time hazard aimed at handover, conformal risk control whose exchangeable unit is the drive, and a 22-paper protocol audit that none of them satisfies. Borrowing well is a contribution when the pairing is new and the protocol is honest — appendix F, slide 48.

**"Your internal reports disagree with each other on the ping-pong rate."**
They do, and that inconsistency is what produced slide 32. Earlier documents quote 28.3%, 29.4% and 43.2%. All three are correct arithmetic on the same 938 handovers under different definition choices. Report 25 reconciles all of them, the index marks the earlier documents as superseded, and the thesis quotes 24.5% with all three choices stated in the same sentence.

---

# PART 3 — The soft spots, and the prepared answer for each

These are the places where an examiner who reads carefully can find something. **Each one has an answer that is better than being caught.** Where the answer is "I know, here is the status", say it before you are asked.

### 1. The tuned arm is a three-capture run

**The exposure.** Slide 22's figures were produced on three captures. The rest of the deck is four.

**The answer, volunteered on the slide.** "This tuned arm was produced on the three-capture dataset. Its conclusion is about *ordering*, and the four-capture ordering in the headline table is identical. It is re-run before submission, and nothing in the contributions depends on the tuned figures themselves."

**Why this is safe.** Because you said it first, and because the claim it supports — "tuning does not change the ordering" — is verifiable from the four-capture headline table on slide 19.

### 2. The report-conversion predictor is degenerate on four captures

**The exposure.** MASTER §21 reports AUPRC 0.731 and AUROC 0.777 for predicting whether a report converts. That is a **three-capture** number. The four-capture re-run of that stage returned a degenerate result — prevalence 0.995 and AUROC 0.45–0.70 — which has not yet been traced, almost certainly a label-join defect rather than a modelling one.

**What was done.** The deck quotes **no** predictor number anywhere. Slide 30 and appendix D report only the *measurement* — 62.9% declined — which is solid and four-capture.

**The answer if asked "can you predict conversion?"** — "The thesis poses it as a task and I'd rather not quote a figure today. The three-capture run gave AUPRC 0.731 against a 0.391 floor, but the four-capture re-run of that stage returned a degenerate label distribution I haven't finished tracing, so I've pulled the number from the deck rather than quote one I can't stand behind. The measurement it rests on — that 62.9% of A3 reports are declined — is unaffected and is what slide 30 claims."

**Why this is safe.** "I pulled a number I could not stand behind" is the strongest sentence available in a defence. Do not be tempted to quote 0.731.

### 3. The deep-ensemble arm is code without a result

**The exposure.** `stage03_uncertainty` trains a five-member ensemble and was run on the earlier curated dataset. It was never re-run on the pooled XCAL captures, so no ensemble row exists in the results tables.

**The answer.** "It's implemented and it isn't reported, because it was never re-run on this dataset. No ensemble number appears anywhere in the thesis and none is claimed. Before submission I either re-run it or drop the arm." *(§27 records this.)*

**If asked "why not use an ensemble for uncertainty?"** — "The uncertainty machinery I do report is calibration plus a distribution-free bound, which is what an operator needs. A deep ensemble would give epistemic uncertainty, which is a different and complementary quantity — and I would not claim it from an arm I have not run on this data."

### 4. The departmental comparator may be uncitable

**The exposure.** No publication record for that study could be found; it is held as a manuscript PDF.

**The answer.** "Its dataset is published with a DOI and is my external validation set. The study itself I hold as a manuscript and it is marked unpublished in the bibliography. If it is still unpublished at submission, the comparison has to be made without a citation, or with the authors' agreement, rather than against a reference a reader cannot retrieve. That is a live issue and I have flagged it."

### 5. The grouped-split claim has narrowed twice

**The exposure.** Pass 2 found one paper splitting by time; pass 3 added two more.

**The answer** *(this is appendix G, slide 52)*. "The claim narrowed as the survey widened, twice, and the thesis says so in the limitations as well as the positioning section. The honest form is: ten of 22 state no split at all, five split on a unit coarser than a row, and none holds out the mobility unit for a per-timestep classification task on measured radio. And the leakage result does not depend on scarcity — it depends on the inflation being real and differential, 74% against 4%, which was measured."

### 6. The conformal contribution is narrower than it sounds

**The exposure.** Conformal prediction is already in wireless.

**The answer** *(appendix G)*. "Cohen et al. 2022 and Simeone et al. 2025 got there first, and I say so on the slide before anyone asks. Their guarantee is over prediction sets for tasks that are i.i.d. within a frame. Mine is a risk guarantee on an operator KPI over a stream exchangeable only by whole drive. The exchangeability unit is the contribution; the feasibility floor `n ≥ 1/α − 1` is its consequence, and that rule is stated nowhere in the handover literature."

### 7. The Hawkes kernel is rejected

**The exposure.** The Ogata residual test rejects at p = 7 × 10⁻⁴.

**The answer** — say it on the slide. "The exponential kernel is rejected as an exact fit. So 0.605 is a calibrated measure of clustering strength under a stated kernel, not a generative claim. It fits far better than Poisson (p ≈ 5 × 10⁻⁵⁸) or a gamma renewal alternative (KS p = 3 × 10⁻¹²), and its stability across four captures and two regimes is what makes it usable."

### 8. Four bibliography entries are partially verified

**The answer.** "Four entries are `verified=partial` on an author list. All four are cited for context or method provenance rather than for a result, and the verification policy requires them completed before submission."

### 9. "18% of drives exceed α" on slide 25

**The exposure.** It reads like the guarantee failing.

**The answer.** "The guarantee is on the **expected** risk for a fresh exchangeable drive, not on every drive individually. Some drives exceed α and others sit far below; the mean is bounded, and the achieved mean is below α at every operating point on the frontier. A per-drive worst-case guarantee would need a different and far more conservative procedure."

### 10. The 957 / 938 and 62.9% / 68.7% pairs

**The exposure.** Internal documents quote both members of each pair.

**The answer.** "Both are correct and they answer different questions — 957 in the raw logs, 938 inside drives that pass quality control; 62.9% over A3 reports, 68.7% over all report types. The thesis states which it means every time, and that discipline came out of finding the inconsistency in my own earlier documents."

---

# PART 4 — Terms you should be able to define on demand

| term | the one-sentence definition |
|---|---|
| **Event A3** | A neighbour cell becomes better than the serving cell by an offset, and stays better through a time-to-trigger, at which point the UE sends a measurement report. |
| **Offset / hysteresis / TTT** | The margin the neighbour must beat by; the extra margin that prevents chattering at the boundary; the time the condition must hold before a report is sent. |
| **PCI / EARFCN** | Physical Cell Identity, unique only within a carrier; the carrier frequency channel number. A cell is (PCI, EARFCN) — which is why the ping-pong definition needs both. |
| **measId / reportConfigId** | Identifiers binding a measurement object to a report configuration, **scoped to the configuration state in force at that moment** — which is why a flat parse misattributes. |
| **Prevalence floor** | The positive rate. It is the AUPRC of a random ranker, so AUPRC must be read against it; lift is their ratio. |
| **AUPRC vs AUROC** | AUPRC is prevalence-sensitive and reads against a floor; AUROC is prevalence-insensitive and reads against 0.5. Both are reported so neither can be read alone. |
| **ECE** | Expected calibration error: the average gap between predicted probability and observed frequency, binned. Lower is better; 0.024 at 1 s here. |
| **Brier score** | Mean squared error of the probability. A proper scoring rule, so it penalises both miscalibration and poor ranking. |
| **Discrete-time hazard** | P(event in interval *k*, given not before *k*). Survival is the product of (1 − hazard); incidence is 1 − survival, hence monotone in the horizon by construction. |
| **Right-censoring** | A drive that ends without a handover does not contribute a negative at every horizon; it censors, and the likelihood accounts for it. |
| **Horizon coherence** | P(event by 1 s) ≤ P(event by 3 s). Guaranteed by the product-limit identity; violated on 43.6% of rows by five independent heads. |
| **Conformal risk control** | A distribution-free procedure that certifies a threshold on exchangeable calibration units so that the expected risk on a fresh unit is at most α. |
| **Exchangeability** | The joint distribution is invariant to reordering the units. Weaker than i.i.d., and the only assumption conformal risk control needs. |
| **Feasibility floor** | α ≥ 1/(n+1) with n calibration units — so n ≥ 1/α − 1. With 28 drives, α ≥ 0.034. |
| **Hawkes process** | A self-exciting point process: intensity = background rate + a kernel contribution from every past event. |
| **Branching ratio** | The integral of the kernel; the expected direct offspring per event. 0.605 here, giving mean cluster size 1/(1−n) = 2.53. |
| **Ogata residual test** | Time-rescale the events under the fitted model; the residuals should be Exp(1). Rejects here at p = 7 × 10⁻⁴. |
| **Grouped split** | Whole groups — here, whole drives — are assigned entirely to train or test, so no group straddles the boundary. |
| **CORAL** | Correlation Alignment: whiten the target features by the target covariance and recolour by the source covariance, matching means. Unsupervised. |
| **Cluster bootstrap** | Resample whole drives with replacement, recompute the metric, take percentiles. Accounts for within-drive dependence. |
| **Lift** | AUPRC divided by prevalence. Always reported beside AUPRC, never instead of it, because low prevalence inflates it mechanically. |

---

*Every number in this document is a four-capture value taken from `MASTER-Handover-Prediction.md` and matches the deck slide for slide. Where a figure is knowingly a three-capture run — slide 22's tuned arm — it is labelled as such in both places.*

:::center
{title}Final Thesis Defence Script — Data-Dense
{sub}Predicting the Next LTE Handover from Drive-Test Signalling
{small}Same sections and slide grouping · fewer explanations · every number the work produced
:::

| | |
|---|---|
| **Use** | When the board wants results, not teaching. Short spoken lines carry the argument; the tables carry the evidence. |
| **Length** | ≈ 1,100 words of connective speech + **20 result tables** — roughly **12–14 minutes**, depending on how much of each table you speak |
| **Read-aloud rule** | Speak the **bold** figure in each table and move on. The rest is there for the question that follows. |
| **Companion** | The Expanded script *explains* these results. This one *states* them. Same sections, same order — they interleave. |

---

## Slides 1–2 — Title and Outline

Assalamualaikum. Respected chairman, respected members of the board. This thesis predicts the next LTE handover from real drive-test signalling, on 57 drives and 938 signalling-confirmed handovers collected across four campaigns in Dhaka and Gazipur.

Headline, before anything else: **one second ahead, AUROC 0.933 and AUPRC 0.784 against a 6.7 percent prevalence floor** — 11.7 times random — with calibrated probabilities and a distribution-free bound on the per-drive miss rate.

Four sections: the problem, the system, the evidence, and the boundary of the claim.

---

## Slides 3–6 — Background, Motivation, Literature and Objectives

Event A3 fires only after a neighbour has been better by an offset for a full time-to-trigger. It is reactive by construction. Deployed on this network:

| A3 parameter | Values observed |
|---|---|
| Offsets | −15, −10, −6.5, **+1**, +5 dB |
| Time-to-trigger | 160 – 1024 ms, **320 ms dominant** |
| Handovers under the dominant +1 dB / 320 ms profile | **679 of 938 — 72%** |

The cost of that lag, measured:

| Quantity | Value |
|---|---|
| Handovers | **938** in 2.9 h — one every 11 s, median gap 3.5 s |
| Returns to the cell just left within 15 s | **24.5%** |
| Radio-link re-establishments | **341** |
| A3 reports never acted on within 2 s | **62.9%** of 7,385 |

Literature audit: **108 papers screened, 22 comparable models reviewed**. Of those 22 — none holds out the mobility unit for a per-timestep task on measured radio, none reports calibration, none reports a lead time or false-alarm rate. Zero of twenty-two on all three counts.

Five objectives: predict at five look-ahead times from handset-observable data; grouped evaluation; probabilities that are coherent, calibrated and bounded; generalisation beyond the training capture; and a stated mechanism.

---

## Slides 7–12 — Methodology and Proposed System

Ground truth is the decoded `RRCConnectionReconfiguration` carrying `mobilityControlInfo`, millisecond-timestamped. Measurement identifiers are message-scoped, so a configuration timeline is replayed before any report is resolved. That correction is what shows the deployed offsets here are negative, not the +3 dB assumed in earlier published work.

**152 columns built, 107 survive a degenerate-feature filter:**

| Feature family retained | Count |
|---|---|
| Radio — rolling mean, std, range and difference over 3 / 5 / 10 s windows, plus neighbour gaps | **83** |
| Mobility, from GPS | 17 |
| Signalling | 13 |
| History | 7 |

Every window is backward-only, closes at *t*, and never crosses a drive boundary.

Formulation: one per-second hazard model; horizon probabilities are products of hazards, so ordering across the five look-ahead times holds by construction. Seven learners under identical folds, seeds and formulation — LightGBM, logistic regression, MLP, TCN, Transformer, GRU, and the A3 rule scored as a predictor.

---

## Slides 13–16 — Data and Experimental Design

| Capture (2026) | Corridor | Drives | Samples | Handovers | Duration |
|---|---|---|---|---|---|
| 10 September | urban arterial | 15 | 2,700 | 290 | 46 min |
| 12 September | urban loop | 8 | 1,440 | 174 | 24 min |
| 13 September | dense urban | 20 | 3,600 | 297 | 60 min |
| 15 September | Uttara–Gazipur highway | 14 | 2,520 | 177 | 43 min |
| **Pooled** | two mobility regimes | **57** | **10,260** | **938** | **2.9 h** |

957 handovers appear in the raw logs; **938** fall inside a quality-controlled drive and are what every model is scored against. The A3 configuration is identical across all four campaigns. The highway capture, mean speed 49.5 km/h, was driven **after every modelling decision was frozen**.

Protocol: grouped by whole drive, 4-fold rotation so every drive is tested once, repeated over 5 seeds — 20 paired observations per comparison. Bootstrap confidence intervals over drives, not samples. Scaler, threshold and calibrator are fit inside each training fold only.

Prevalence by look-ahead time — why accuracy is not reported:

| Look-ahead | 0.5 s | 1 s | 2 s | 3 s | 5 s |
|---|---|---|---|---|---|
| Positive samples | 3.7% | **6.7%** | 12.5% | 17.5% | 25.9% |
| Accuracy of "never" | 96.3% | **93.3%** | 87.5% | 82.5% | 74.1% |

---

## Slides 17–20 — Engineering Scope and Impact

Knowledge profile WK1–WK8, complex engineering problem attributes P1–P7, complex engineering activities A1–A5 — all mapped in the slide tables, all claiming only what the work does.

The engineering trade-off, quantified rather than described:

| Certified target | Samples alarmed | Handovers actually missed |
|---|---|---|
| 20% per-drive miss rate | **23%** | **12.6%** |
| 5% per-drive miss rate | **61%** | — |

A tighter promise is not a better system — it is a louder one. At a 5% target the alarm rate is 61%, which no operator would deploy.

Impact claim, stated narrowly: better connection continuity and fewer unnecessary handovers and signalling messages. The 24.5% return rate is measured. **No deployed energy saving is claimed. No health claim is made** — no human subjects, no exposure experiments.

---

## Slide 21 — Main Prediction Result

**Pause here.**

| Look-ahead | Prevalence | AUPRC [95% CI] | Lift | AUROC | ECE |
|---|---|---|---|---|---|
| 0.5 s | 0.037 | 0.416 [0.350, 0.490] | 11.3× | 0.916 | 0.023 |
| **1 s** | **0.067** | **0.784 [0.740, 0.826]** | **11.7×** | **0.933** | **0.024** |
| 2 s | 0.125 | 0.627 [0.594, 0.657] | 5.0× | 0.854 | 0.061 |
| 3 s | 0.175 | 0.598 [0.561, 0.636] | 3.4× | 0.816 | 0.091 |
| 5 s | 0.259 | 0.606 [0.564, 0.649] | 2.3× | 0.783 | 0.141 |

LightGBM, out-of-fold over 57 drives. LightGBM leads at every look-ahead time; **logistic regression is second**, ahead of the GRU, Transformer, TCN and MLP.

The network's own A3 rule on the same data: **AUROC 0.653**, detecting **5.5%** of handovers one second ahead.

Event level rather than sample level:

| | 1 s | 5 s | Ceiling |
|---|---|---|---|
| Handovers detected | **44.7%** | 65.1% | 90.5% |

The 90.5% ceiling is imposed by the 1 Hz export — equipment, not model.

---

## Slides 22–24 — Leakage, Coherence and the Risk Guarantee

**Leakage is architecture-dependent.** Random-row splitting instead of grouped-drive splitting:

| Model | Inflation |
|---|---|
| GRU | **+74%** |
| Transformer | +44% |
| TCN | +27% |
| LightGBM | +20% |
| MLP | +10% |
| Logistic regression | **+4%** |
| A3 rule | −2% |

The spread is the finding: a careless split reorders the leaderboard rather than merely lifting it.

**Coherence.**

| Configuration | Horizon violations | Note |
|---|---|---|
| Five independent classifiers | **43.6%** | max violation 0.495 → 0.596 |
| Same, plus per-horizon isotonic | 48.7% | worse, and costs 2–5 AUPRC points and a held-out split |
| Hazard formulation | **0%** | by construction |

Calibration beats the uncalibrated baseline at every look-ahead time, p < 0.0001 over the 20 paired folds.

**Conformal risk control.** Certified on 28 held-out calibration drives. Feasibility floor **α ≥ 0.034** — with 28 drives, no tighter target is expressible. At α = 0.20 the bound held on **82%** of test drives. The number of calibration drives is therefore a campaign-design quantity, not a modelling choice.

---

## Slides 25–26 — Generalisation

Leave-one-capture-out, trained on three, tested on the fourth:

| Held out | AUPRC | Lift | AUROC | ECE |
|---|---|---|---|---|
| 10 Sept urban arterial | 0.826 | 9.9× | 0.949 | 0.027 |
| 12 Sept urban loop | 0.718 | 9.4× | 0.909 | 0.040 |
| 13 Sept dense urban | 0.832 | 13.2× | 0.943 | 0.019 |
| **15 Sept highway** | **0.761** | **14.9×** | **0.927** | **0.018** |

The highway has the **highest lift and the lowest calibration error of the four**, and it was collected after all modelling choices were frozen. Adding it moved the pooled AUROC by zero — 0.933 before and after.

External transfer, on a public drive-test dataset from another team:

| | AUROC at 1 s |
|---|---|
| Our model, transferred | **0.752** |
| Model trained on that dataset itself | 0.745 |

---

## Slides 27–30 — Mechanism and Network Findings

**Single-feature AUROC** — what actually carries the signal:

| Feature | AUROC alone |
|---|---|
| Serving dwell time | **0.874** |
| Serving SINR | 0.830 |
| A3 serving-to-neighbour gap | **0.566** |

The quantity the network thresholds on is nearly the weakest predictor available. The gap condition holds on **27.1%** of samples; three in five of the resulting reports are declined.

**A3 report conversion within 2 s**, by capture:

| Capture | 10 Sept | 12 Sept | 13 Sept | 15 Sept | Pooled |
|---|---|---|---|---|---|
| Converted | 57.2% | 60.1% | 63.3% | 71.9% | **62.9%** |

Two qualifiers that are mandatory whenever this number is quoted: it is **A3 reports only** — all report types convert at 68.7% — and only 43–52% of measurement reports are A3.

**Ping-pong depends on three definition choices** usually left unstated. Same 938 handovers:

| Definition | Rate |
|---|---|
| A→B→A, cell = PCI + carrier, 15 s window | **24.5%** |
| Cell = PCI only | 29.0% |
| Any return within the window | 38.5% |
| Ungrouped, over 957 raw events | 41.3% |

Where it concentrates: intra-carrier **31.0%** against inter-carrier **6.5%**; the +1 dB / 320 ms profile returns at 29.2% on 72% of all handovers; the highway at 49.5 km/h still returns at **31.1%** — so the lever is the time-to-trigger, not speed.

**Handover clustering.** A Hawkes self-exciting fit gives a branching ratio of **0.605 [0.524, 0.673]** — each handover triggers about 0.6 further handovers. Per capture: 0.649 / 0.609 / 0.567 / **0.513**, lowest on the highway. An Ogata residual test rejects the exponential kernel (D = 0.074, p = 7 × 10⁻⁴), so the clustering is real but not exponentially shaped.

**Negative results, reported:**

| Attempted | Outcome |
|---|---|
| Dedicated ping-pong classifier | AUROC **0.51** — chance |
| Additional neighbour-cell features | no gain |
| Cell-clustering features | no gain |
| Two unsupervised domain-adaptation methods | no gain |

**Counting upper bound on benefit** — not a causal estimate:

| Alarm budget | 2% | 5% | 10% | 20% | 40% |
|---|---|---|---|---|---|
| Bound | +0.21 | **+0.34** | +0.25 | +0.04 | −0.03 |

The bound peaks at a 5% budget and goes negative by 40%.

---

## Slides 31–33 — Conclusion, Novelty and Future Work

Five results, in order of how hard they are to argue with:

- **One.** Next handover predicted 1 s ahead at **AUROC 0.933 / AUPRC 0.784**, 11.7× the floor, ECE 0.024.
- **Two.** Hazard formulation: **0% horizon violations** against 43.6% for independent classifiers — from one fit, no calibration split.
- **Three.** Grouped evaluation is worth **+4% to +74%** depending on architecture, so it reorders the leaderboard.
- **Four.** **AUROC 0.927** on a highway corridor frozen out of every modelling decision; 0.752 on an independent public dataset.
- **Five.** A distribution-free per-drive guarantee with its price stated: **23% alarm rate for a 12.6% miss rate**, floor α ≥ 0.034 on 28 drives.

Plus two network findings the literature has not modelled: the A3 report-conversion rate — 62.9% declined, rising with cell size — and a ping-pong rate reported together with its definition.

> The novelty is not a new machine-learning algorithm. It is a signalling-grounded, leakage-safe, uncertainty-aware framework that turns real handover measurements into coherent predictions and validates them on unseen and external data.

**Boundary, stated by us.** 57 drives, one operator, four days, 1 Hz export capping event detection at 90.5%. Cross-regime transfer rests on a single configuration pair. No causal claim: the logging policy is deterministic, so off-policy evaluation is unidentified here and only a counting bound is reported. Offline predictor, not a deployed controller.

**Next, in order:** a fuzzy regression-discontinuity design at the A3 boundary — identifiable on data already collected; a second corridor and operator; linking the warning to a measured throughput or interruption effect; an experimental time-to-trigger change; and release of the code and dataset.

Thank you. I welcome your questions.

---

## The eleven numbers to have on the tip of your tongue

| Number | What it is |
|---|---|
| 57 / 10,260 / 938 | drives / samples / signalling-confirmed handovers (957 raw) |
| 0.933 / 0.784 / 11.7× | AUROC / AUPRC / lift at 1 s |
| 6.7% | prevalence at 1 s — the floor everything is read against |
| 0.653 | the A3 rule scored as a predictor |
| 43.6% → 0% | horizon violations, independent classifiers → hazard |
| +74% / +4% | leakage inflation, GRU / logistic |
| 0.927 | highway, frozen out of every modelling choice |
| 0.874 / 0.566 | dwell time / A3 gap, single-feature AUROC |
| 62.9% | A3 reports declined within 2 s |
| 24.5% | ping-pong, PCI + carrier, 15 s |
| 23% / 12.6% | alarm rate / actual miss rate at a 20% target |

---

## If a number is challenged

- **"Is 938 or 957 the right count?"** — Both are correct. 957 raw, 938 inside quality-controlled drives. Every model is scored on 938. Say which one you mean, every time.
- **"Why is AUPRC lower at 2 s than at 1 s?"** — Because the floor moves. Read the lift column: 11.7× at 1 s against 5.0× at 2 s. The ranking is unchanged.
- **"Isn't 0.933 just memorising the route?"** — Leave-one-capture-out never drops below 0.909, and the highway was driven after the model was frozen.
- **"Why does logistic regression beat the deep models?"** — 57 drives. There is not enough data for a sequence model to learn what the engineered features already carry. The leakage table is the reason this looks surprising in the published literature.
- **"Your ping-pong rate is higher/lower than paper X."** — Almost certainly a different definition. Give the ladder: 24.5 → 29.0 → 38.5 → 41.3 on the same 938 events.
- **"Where is the causal effect?"** — Not identified on this data, and we say so. The logging policy is deterministic. The fix is the regression-discontinuity design, and it is the first item of future work.

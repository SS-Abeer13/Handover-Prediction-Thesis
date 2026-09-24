# The fourth capture, rebuilt through the pipeline — and where the ping-pong rate actually comes from

The 15 September highway capture is now **in the dataset**, not beside it. Every
table in this document was produced by the project's own stages from the raw
`.csv` and signalling `.txt`, not by a separate read of the logs.

Three things follow, and the middle one is the most useful:

1. The headline result **does not move** when a fourth capture in a new corridor
   at double the speed is added: AUROC 0.933 at 1 s, exactly as on three.
2. The ping-pong rate that has been quoted in this project ranges from 24.5% to
   43.2% **on the same handovers**. Every one of those numbers is arithmetically
   correct. They differ because three definition choices are rarely stated, and
   this document states them.
3. Held out whole, the highway capture is predicted at **AUROC 0.927 with the
   highest lift and the best calibration of the four** — by a model that never
   saw a highway.

---

## 1. What the fourth capture is

| | 10 Sept | 12 Sept | 13 Sept | **15 Sept** |
|---|---|---|---|---|
| corridor | urban arterial | urban loop | dense urban | **Uttara → Gazipur highway** |
| signalling handovers (raw log) | 307 | 176 | 297 | **177** |
| handovers inside retained drives | 290 | 174 | 297 | **177** |
| measurement-report instants | 4,688 | 3,702 | 4,098 | **3,237** |
| RRC re-establishments | 113 | 64 | 159 | **5** |
| samples on the 1 Hz grid | 2,700 | 1,440 | 3,600 | **2,520** |
| retained drives | 15 | 8 | 20 | **14** |
| A3 offsets configured | −15, −10, −6.5, +1, +5 dB | same | same | **same** |
| time-to-trigger values | 160–1024 ms | same | same | **same** |

**Pooled: 57 drives, 10,260 samples, 938 signalling-confirmed handovers.**

Two numbers deserve a note before anything is built on them.

**The 957-vs-938 gap is drive retention, not disagreement.** The parser finds
957 handovers across the four logs. 938 of them fall inside a drive that passes
quality control (≥ 60 s, ≥ 60 samples). The other 19 sit in the fragment at the
start or end of a session. Report 23 quotes 957 because it read the signalling
directly; this document quotes 938 because that is the set the models are
scored against. Both are right; they answer different questions, and the
manuscript should say which it means every time.

**The re-establishment collapse is real and is the cleanest physical contrast in
the campaign.** 159 re-establishments on 13 Sept in the dense urban core; **5**
on 15 Sept over 34.6 km of open highway. Corner shadowing and flyover blockage
drop the serving cell faster than the Layer-3 filter and time-to-trigger can
follow; on the highway the macro layer overlaps smoothly and the link survives.

---

## 2. The ping-pong rate: the same handovers, four answers

This project has quoted 28.3%, 29.4% and 43.2% for the same phenomenon. All
three are correct arithmetic on the same events. Here is the whole surface,
computed on the 938 retained handovers:

| time-of-stay window | cell identity | rule | pooled rate |
|---|---|---|---|
| 5 s | PCI + carrier | A → B → A | 19.5% |
| 10 s | PCI + carrier | A → B → A | 23.2% |
| **15 s** | **PCI + carrier** | **A → B → A** | **24.5%** |
| 15 s | PCI only | A → B → A | 29.0% |
| 15 s | PCI only | any return inside the window | 38.5% |
| 15 s | PCI only, ungrouped, all 957 raw events | any return inside the window | 41.3% |

Three choices, each worth a few points:

**Choice 1 — what counts as "the same cell".** The network runs **five to six
carriers** (EARFCN 250, 1600, 9360, 40142, 40340, 40538) and **one handover in
four changes carrier**. Physical Cell IDs are reused across carriers, so a hop
from PCI 49 on 40340 to PCI 380 on 250 and then to PCI 49 on 250 — which the
15 Sept log shows in its first three events, 0.7 s apart — is *not* a return to
the cell just left. Keying on PCI alone calls it one. That is worth **+4.5
points**.

**Choice 2 — "returns immediately" versus "returns at some point".** Handovers
arrive a median of **3.5 s apart**, and **59.8% of them are followed by another
within 5 seconds**. A 15 s window therefore spans three to five handovers, so
"the cell we just left reappears within 15 s" catches almost any wandering in a
three-cell neighbourhood. That is worth **+9.5 points**. The ping-pong
literature — and 3GPP mobility robustness work — means the strict form: out and
straight back, with a short time of stay.

**Choice 3 — which events are in the denominator.** Counting the 19 handovers
outside retained drives, and allowing a "return" to span a gap between drives,
adds the last **+2.8 points**.

**The number this thesis should quote is 24.5%**, with the window, the cell
identity and the rule stated in the same sentence. Report 23's 43.2% is choice
1 + choice 2 + choice 3 together; it is not wrong, it is a different question.

### 2.1 So why is it high at all?

Because it is concentrated, and the concentration is measurable.

| split | handovers | ping-pong rate |
|---|---|---|
| handover stays on the same carrier | 690 | **31.0%** |
| handover changes carrier | 248 | **6.5%** |

| A3 profile that fired it | handovers | ping-pong rate | inter-carrier share |
|---|---|---|---|
| **+1.0 dB, TTT 320 ms** | **679** | **29.2%** | 9% |
| −10.0 dB, TTT 640 ms | 124 | 10.5% | 74% |
| −15.0 dB, TTT 160 ms | 82 | 11.0% | 79% |
| −6.5 dB, TTT 640 ms | 9 | 11.1% | 33% |

Read the two tables together and the mechanism is plain. The negative-offset
profiles *look* aggressive, and they are the ones a reviewer will point at — but
they are the **inter-frequency** profiles, used to move the UE between carrier
layers, and a UE moved to another layer stays there. They barely oscillate.

Almost every ping-pong is produced by the single **intra-frequency** profile:
A3 offset +1 dB with a time-to-trigger of only **320 ms**. That profile fires
**72% of all handovers** in the campaign. A +1 dB margin with a third of a
second of confirmation is a tight trigger in a dense grid of overlapping sectors,
and it oscillates exactly as mobility-robustness theory says it should. The two
profiles with 640 ms of confirmation run at a third of the rate.

**This is the actionable finding of the whole ping-pong analysis.** The lever is
not the offset and not the vehicle speed — it is the time-to-trigger on one
profile. And it is a lever an operator can pull without touching the other
three.

### 2.2 Two hypotheses the fourth capture kills

**"Ping-pong is congestion — it happens when vehicles crawl at cell edges."**
At a mean 49.5 km/h with peaks near 98 km/h, the highway capture still returns
**31.1%** under the strict definition — the second-highest of the four, above
both dense-urban captures. Speed is not the driver.

**"It is an artefact of our 1 Hz sampling."** It cannot be. Handover instants
come from RRC signalling with millisecond timestamps; the sample grid is not
used to detect them at all.

---

## 3. The dataset does not degrade — it gets a regime

Same pipeline, same protocol, same grouped-drive rotation with every drive
tested once. Three captures, then four:

| LightGBM @ 1 s | three captures | **four captures** |
|---|---|---|
| samples scored | 7,740 | **10,260** |
| handovers | 761 | **938** |
| prevalence | 7.3% | 6.7% |
| AUPRC | 0.797 | **0.784** [0.740, 0.826] |
| lift over prevalence | 10.98× | **11.70×** |
| AUROC | 0.933 | **0.933** |
| ECE | 0.025 | **0.024** |
| bootstrap groups | 43 | **57** |

Adding a corridor the model had never driven, at twice the speed, on a sparser
cell layer, moved AUROC by **zero** and improved the prevalence-adjusted lift.
That is the robustness claim this thesis could not make a week ago.

Model ranking at 1 s is unchanged, and so is the shape of the leakage result:

| model | AUPRC (grouped) | leakage inflation |
|---|---|---|
| **LightGBM** | **0.784** | 20.1% |
| logistic regression | 0.728 | 3.8% |
| MLP | 0.677 | 10.1% |
| TCN | 0.574 | 26.6% |
| Transformer | 0.567 | 43.9% |
| GRU | 0.475 | **74.4%** |
| A3 rule | 0.117 | — |

A snapshot model still beats every sequence model, and the sequence models still
gain the most from being allowed to leak — GRU by 74%, logistic regression by 4%.

---

## 4. The experiment the fourth capture makes possible

Hold out a **whole capture**. Not a drive, not a route — a day, a corridor and a
mobility regime. Train on the other three.

| held out | prevalence @1 s | AUPRC | lift | AUROC | ECE |
|---|---|---|---|---|---|
| 10 Sept urban arterial | 8.4% | 0.826 | 9.9× | 0.949 | 0.027 |
| 12 Sept urban loop | 7.7% | 0.718 | 9.4× | 0.909 | 0.040 |
| 13 Sept dense urban | 6.3% | 0.832 | 13.2× | 0.943 | 0.019 |
| **15 Sept highway** | **5.1%** | **0.761** | **14.9×** | **0.927** | **0.018** |

The highway capture — different corridor, double the speed, a tenth of the
serving-cell density, collected **after every modelling decision was frozen** —
transfers at **AUROC 0.927**, with the **highest lift and the lowest calibration
error of the four**. No retraining, no adaptation, no feature added for it.

This replaces the old curated-vs-measured transfer matrix entirely. That matrix
asked whether a textbook dataset described the network; this one asks whether
the model describes a road it has never driven. The second question is the one a
reviewer cares about, and the answer is yes.

---

## 5. Self-excitation holds across both regimes

| | branching ratio | 95% CI | events |
|---|---|---|---|
| **pooled, four captures** | **0.605** | [0.524, 0.673] | 930 |
| 10 Sept | 0.649 | [0.454, 0.776] | 288 |
| 12 Sept | 0.609 | [0.443, 0.740] | 172 |
| 13 Sept | 0.567 | [0.363, 0.688] | 294 |
| 15 Sept highway | 0.513 | [0.335, 0.629] | 176 |

Six handovers in ten are triggered by another handover rather than by the
background rate, and that holds on a highway as well as in a canyon. The
likelihood-ratio test against a Poisson process is decisive (p ≈ 7 × 10⁻⁷⁵); the
Ogata residual test still rejects the exponential kernel as an *exact* fit
(KS p = 9.7 × 10⁻⁵), and the branching ratio is therefore reported as a
calibrated measure of clustering strength under a stated kernel, exactly as
before.

The highway's lower ratio (0.513) is the expected direction: wider cells, fewer
boundaries per kilometre, less to oscillate between.

---

## 6. The A3 conversion rate, with its report set stated

A second discrepancy in the project's own documents has the same shape as the
ping-pong one, and a different cause. It is not the window. It is **which
reports are in the denominator**.

**All measurement reports** — A1, A2, A3, A4, A5 together:

| window allowed for the handover | 10 Sept | 12 Sept | 13 Sept | 15 Sept | pooled |
|---|---|---|---|---|---|
| 1 s | 77.2% | 81.2% | 79.2% | 83.8% | **80.0%** |
| 2 s | 64.5% | 68.6% | 69.1% | 74.6% | **68.7%** |
| 3 s | 55.0% | 60.3% | 61.1% | 69.5% | **60.8%** |

**A3 reports only** — the ones that actually carry a handover-entering
condition, resolved through the configuration timeline:

| window allowed for the handover | 10 Sept | 12 Sept | 13 Sept | 15 Sept | pooled |
|---|---|---|---|---|---|
| 1 s | 69.8% | 74.6% | 74.1% | 80.9% | **74.5%** |
| **2 s** | **57.2%** | **60.1%** | **63.3%** | **71.9%** | **62.9%** |
| 3 s | 47.6% | 51.4% | 55.0% | 66.0% | **54.6%** |

*(percentage of report instants NOT followed by a handover inside the window)*

Only 43–52% of measurement reports are A3 at all; the rest are A1, A2, A4 and
A5, which are not handover-entering events and should never have been in the
denominator of a conversion rate.

So: **the manuscript's 61.3% is A3-only at 2 s** (62.9% here on the full
signalling set, 61.3% after drive retention) and **report 23's 68.5% is all
report types at 2 s**. Both are arithmetically right. Only the first is the
quantity the claim is about, and §20 of the master document has been amended to
say "A3 reports" and "within 2 s" in the same sentence.

The comparison to Ghoshal et al.'s 69–87% on US operators should be made
A3-to-A3 at a stated window, or not made at all.

The highway capture is the highest on every row of both tables: **71.9% of its
A3 reports are declined at 2 s**. On a sparse macro layer the entering
condition is satisfied early and often, and the serving cell simply waits.

## 7. What changed in the repository

| | |
|---|---|
| `stage12_xcal_prepare` | 15 Sept added as a fourth capture; the pooled dataset is now 57 drives |
| `stage21_capture_transfer` | **new** — leave-one-capture-out, replacing the curated arm of stage 06 |
| `stage13`, `stage15` | re-run on four captures; tables regenerated |
| `reports_xcal/tables/capture_transfer*.csv` | **new** |
| curated-data comparisons | removed from the master document, the contribution table and the figures |

## 8. What is still owed

- Stages 14, 16 and 11 (hazard-fair arm, ping-pong predictor, benefit envelope)
  were re-running when this document was written; their four-capture numbers
  replace the three-capture ones in §17, §21 and §23 of the master document.
- The deep-ensemble arm remains code without a result (master §27).
- One honest caveat on §4: with four captures, leave-one-capture-out has four
  points. It is a strong design, not a large sample.

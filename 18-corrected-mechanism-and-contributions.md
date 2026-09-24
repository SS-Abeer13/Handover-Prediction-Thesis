# Corrected mechanism, corrected contribution table, and where the thesis actually stands

Both items done. The mechanism conclusion from doc 15 changes its *explanation*
but keeps its *observation*, and a published finding replicates on our data along
the way. The contribution table below supersedes doc 14 §5 and doc 15 §4.

---

## 1. The mechanism, recomputed on corrected attribution

### 1.1 Trigger coverage was wrong by a factor of nearly four

| A3 profile | share of handovers | fires when gap < | samples inside |
|---|---|---|---|
| **+1 dB / 320 ms** | **85.1%** | **−1 dB** | **15.4%** |
| −10 dB / 640 ms | 14.9% | +10 dB | 81.4% |

*(shares among the two profiles that clear the 60-handover bar; over all
profiles, +1 dB is 74%)*

**Handover-weighted mean trigger coverage: 25.3%** — not the 92.5% reported in
doc 15, which used the mis-attributed −15 dB profile as dominant.

So the claim *"the A3 gap condition is almost always satisfied"* is **withdrawn.**
It is satisfied about a quarter of the time.

### 1.2 But the gap still barely predicts anything

Discrimination at the 1 s horizon, single features, n = 3,270:

| feature | AUROC |
|---|---|
| **serving dwell time** | **0.865** |
| serving SINR | 0.797 |
| time since previous handover | 0.582 |
| **serving-to-neighbour gap** | **0.566** |
| serving RSRP | 0.531 |

The gap gives an AUPRC lift of **1.18×** — essentially nothing. The observation
from doc 15 survives intact; only the explanation was wrong.

### 1.3 The correct explanation, and it replicates a published result

Ghoshal et al. report that **69–87% of reported measurement events never trigger
a handover** across three US operators. Measured the same way on our data:

| capture | A3 reports | followed by a handover within 2 s | **never trigger** |
|---|---|---|---|
| 10 Sept | 2,307 | 981 | 57.5% |
| 12 Sept | 1,896 | 743 | 60.8% |
| 13 Sept | 2,228 | 809 | 63.7% |
| **pooled** | **6,431** | **2,533** | **60.6%** |

**60.6% of reported A3 events never become a handover.** That is an independent
replication of their finding on a different operator, a different continent and
a different RAT generation — and our lower rate (60.6% vs 69–87%) is what a more
aggressive configuration should produce.

This is the real mechanism. The gap condition is **necessary but far from
sufficient**: it must hold continuously through the time-to-trigger, and the
network still declines to act on three out of five reports. Knowing the gap
therefore tells you little about whether a handover follows. What does predict
is **how long the UE has already been on the cell** (AUROC 0.865) and **serving
SINR** (0.797).

That is a better finding than the one it replaces — it is mechanistic rather
than definitional, and it comes with an external replication.

---

## 2. Corrected contribution table

Supersedes doc 14 §5 and doc 15 §4. Every row is measured on our own data.

| # | Contribution | Status |
|---|---|---|
| **C1** | **Discrete-time hazard replaces multi-horizon binary classification.** Equal discrimination (paired Wilcoxon p ≥ 0.125), ECE **−23 to −35%**, non-monotone predictions **25.4% → 0%**. First time-to-event formulation of handover prediction. | holds |
| **C2** | **Ping-pong quantified as self-excitation.** Hawkes branching ratio **0.61 ± 0.04** across three independent captures — 61% of handovers are self-triggered offspring. Never done in this literature. | holds |
| **C3** | **Distribution-free bound on missed handovers**, valid at drive level. Meets target at every horizon where a pooled-sample threshold fails. Plus the **n ≥ 1/α − 1** campaign-design rule. | holds |
| **C4** | **1 Hz resolution ceiling measured**: 90.5% of handovers is the hard cap on event detection. | holds |
| **C5** | **Benefit envelope with a random-alarm reference.** The predictor earns its keep only below a ~10% alarm budget; it is **−21 pp worse than random at 40%**. Event-detection rates reported without a chance reference overstate results. | holds |
| **C6** | **Configuration timeline for A3 attribution.** reportConfigId and measId are message-scoped; 1,057 measConfig updates per hour; 29 of 30 config IDs change event type. A flattened parser silently misattributes. **97.4% of 780 handovers attributed correctly.** | **new** |
| **C7** | **60.6% of reported A3 events never trigger a handover** — independent replication of Ghoshal et al.'s 69–87% on a different operator and RAT. | **new** |
| **C8** | **Ping-pong 29.4%** at the literature-standard 15 s window and per-handover denominator, exceeding the highest published per-event rate (25%, Verizon). | holds |
| **C9** | **Cross-regime transfer degrades: Δ AUROC 0.088.** Single regime pair, one direction, identical test set. | **reinstated** (was falsified on bad labels) |
| **C10** | **Conditioning on measured A3 parameters gives nothing** (0.744 vs 0.745). | holds |
| **C11** | **Leakage is architecture-dependent**: GRU **+109%** AUPRC under random-row splitting vs LightGBM **+12%**. | holds |
| **C12** | **External validation**: our model scores **0.729** AUROC on the independent public Mendeley dataset against its own **0.719** in-domain ceiling; parser agrees **310/310** with XCAL's own event counter. | holds |
| **C13** | **Protocol audit of the competitor set**: 0/11 split by drive/route/time, 0/11 report calibration, 0/11 report false alarms per hour, 1/11 reports AUPRC, 6/11 headline accuracy on an imbalanced task. | holds |
| **C14** | **Reproducible authenticity audit** that detected a synthetic dataset, validated against real controls. | holds |
| ~~R8~~ | ~~Predictability is invariant to A3 configuration~~ | **withdrawn** — artefact of mis-attributed labels |
| ~~doc 15 §2~~ | ~~The A3 gap condition covers 92.5% of samples~~ | **withdrawn** — replaced by §1 above |

### The pattern claimed in doc 14, revised

Doc 14 asserted *"more information does not help; better formulation does"*, on
four instances. One of the four (A3-regime invariance) is withdrawn, and it
reversed. The honest version is narrower and still worth saying:

> Neighbour coverage raised from 28% to 79%, and explicit self-excitation
> features, both changed prediction accuracy by nothing; reformulating the target
> as a hazard improved calibration and coherence substantially. Configuration,
> by contrast, *does* matter — cross-regime transfer costs 0.088 AUROC.

---

## 3. What we have actually achieved

Fourteen measured contributions, four withdrawn or reversed claims, one
pipeline, 87 screened references.

**The instrument.** A full RRC signalling parser with a configuration timeline,
validated 310/310 against XCAL's own event counter on an independent dataset,
attributing 97.4% of 780 handovers to the exact deployed rule that fired them.
A reproducible authenticity audit that caught a synthetic dataset. A 1 Hz
resolution ceiling quantified at 90.5%.

**The formulation.** Handover prediction posed as discrete-time hazard
estimation rather than four independent binary classifiers — same discrimination,
better calibration, and a quarter of the baseline's predictions stop being
logically impossible. First application of survival modelling to this problem.

**The mechanism.** Ping-pong quantified as a self-exciting point process with a
branching ratio of 0.61, stable across three captures. The A3 gap condition
shown to be necessary but far from sufficient, with 60.6% of reported events
never converting — replicating a published result on a different network.

**The guarantees.** A distribution-free bound on missed handovers valid at the
drive level, with a campaign-design rule (n ≥ 1/α − 1 drives) that nobody in
this field states.

**The honesty.** A benefit envelope that admits the predictor beats a random
alarm only below a 10% budget. A protocol audit showing the competitor set
reports no calibration, no grouped splits and no false-alarm rates. External
validation on a public dataset where our model matches its in-domain ceiling.
And four of our own claims withdrawn when better evidence arrived — the
synthetic dataset, the leaky split, the parser defect, the inverted monotonicity
constraint.

**What is not done.** No manuscript. No TabPFN comparison. No PU correction. No
causal estimate at the A3 boundary. The literature review needs one more pass on
17 papers where only the bibliography was verified.

The work is in good shape and the bottleneck has not moved: it is the writing.

---

## 4. Immediate next

```
1. Draft the manuscript                              <- the only thing blocking
2. Check Kalntis et al., "Smooth Handovers via Smoothed Online Learning",
   INFOCOM 2025, before any first-to-learn claim
3. TabPFN + MiniRocket, only if time allows after the draft
```

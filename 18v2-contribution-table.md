# Contribution table, version 2 — after the improvement plan

> **Numbering caution (added 14 Sept, doc 21).** `MASTER-Handover-Prediction.md`
> §24 carries the canonical contribution list and now runs to C17, including
> three rows added after this document was written. Its C-numbers are **not**
> the ones below — this table's C14–C17 are different claims. Cite §24 of the
> master document in the manuscript; read this file for the withdrawal history,
> which §24 does not repeat.

Supersedes doc 18 §2. Every row is measured on the **pooled XCAL signalling
dataset** (57 drives, 10,260 samples, 938 handovers across four captures, grouped K-fold with every
drive tested once) unless the row says otherwise. Doc 20 has the evidence for
each change.

The headline change from version 1: **two contributions are narrower than they
were, three are new, and one hypothesis of my own was refuted.** Nothing was
quietly dropped.

**Update, 15 Sept (doc 22).** Two more rows narrowed, both because the
literature survey was widened rather than because a number moved: C3 (the
conformal claim, now the exchangeability unit rather than the machinery) and
C13 (the protocol audit, now 22 papers with the exceptions named). Both
narrowings are recorded in the rows themselves and in MASTER §25.2 and §27. No
result changed; the *claims about the results* got smaller.

---

## The table

| # | Contribution | Status |
|---|---|---|
| **C1** | **Discrete-time hazard replaces multi-horizon binary classification.** One fit gives horizon-coherent predictions (**0% violations vs 47%**, true for any learner by the product-limit identity) and, with gradient boosting, better calibration than an uncalibrated multi-head baseline (ECE −0.006 to −0.030, p < 0.0001, **20 paired folds**). Two caveats now measured: a calibrated baseline beats it on ECE, at the cost of a held-out calibration split, 2–5 AUPRC points, and — without a second monotone projection — *worse* coherence than no calibration at all (max violation 0.484 → 0.585); and the calibration gain does **not** reproduce with a neural learner (ECE delta ≈ 0, AUPRC −0.11 at 1 s). | **narrowed twice** |
| **C2** | **Ping-pong quantified as self-excitation.** Branching ratio **0.605, bootstrap 95% CI [0.524, 0.673]**, stable over four captures and two mobility regimes (0.513-0.649). Decisively non-Poisson (LR p ≈ 5×10⁻⁵⁸) and better than a gamma renewal alternative, but the exponential-kernel Hawkes is itself rejected by an Ogata residual test (p = 1×10⁻⁴), so 0.61 is a calibrated measure of clustering strength under a stated kernel, not a generative claim. | **narrowed** |
| **C3** | **Distribution-free bound on missed handovers**, valid at drive level, now on the hazard model with pooled calibration drives. Feasibility floor improved **α ≥ 0.077 → α ≥ 0.044**. Frontier published: α = 0.10 costs a 55% alarm rate, α = 0.20 costs 27%, α = 0.30 costs 8.8%. Plus the **n ≥ 1/α − 1** campaign-design rule. **Scope cut on 15 Sept (doc 22 §2M):** conformal prediction inside wireless is prior art — Cohen, Park, Simeone & Shamai (2022) and Simeone, Park & Zecchin (2025). The claim is no longer "conformal guarantees for handover prediction". It is *the exchangeability unit* — the whole drive, not the row — and the campaign-design floor that follows from it. Their guarantees are over prediction **sets** for tasks i.i.d. within a frame; neither reports a mobility case. | strengthened, then **narrowed** |
| **C4** | **1 Hz resolution ceiling measured**: 90.5% of handovers is the hard cap on event detection. | holds |
| **C5** | **Benefit envelope with a random-alarm reference.** On the new data the predictor earns a positive excess up to a **20%** alarm budget (+0.035), strongly positive at 5% (**+0.318**), negative at 40% (−0.019). Event-detection rates reported without a chance reference overstate results. | strengthened |
| **C6** | **Configuration timeline for A3 attribution.** reportConfigId and measId are message-scoped; ~1,060 measConfig updates per capture; 29 of 30 config IDs change event type. A flattened parser silently misattributes. 97% of handovers attributed. | holds |
| **C7** | **61.3% of reported A3 events never trigger a handover** — independent replication of Ghoshal et al.'s 69–87% on a different operator and RAT. | holds |
| **C8** | **Ping-pong 24.5%** at the literature-standard 15 s time-of-stay threshold, with the cell identified by PCI **and carrier** and the return required to be immediate. The same 938 handovers give 41.3% under three unstated choices — see C19. | **restated with its definition** |
| **C9** | **Cross-regime transfer degrades: Δ AUROC 0.088.** Single regime pair, one direction, identical test set. | holds |
| **C10** | **Conditioning on measured A3 parameters gives nothing** (0.744 vs 0.745). | holds |
| **C11** | **Leakage is architecture-dependent, and now an ordering with a mechanism.** Random-row splitting inflates AUPRC by **+65 to +92% (GRU)**, +38 to +64% (Transformer), +42 to +50% (TCN), +17 to +33% (MLP), +3 to +44% (LightGBM), +9 to +15% (logistic regression). Sequence models leak most because a 10 s window straddles the split. | **strengthened** |
| **C12** | **External validation**: 0.729 AUROC on the independent public Mendeley dataset against its own 0.719 in-domain ceiling; parser agrees 310/310 with XCAL's own event counter. | holds |
| **C13** | **Protocol audit of the competitor set.** Widened twice since this row was written — 11 papers → 17 (doc 21) → **22** (doc 22). Current counts: **10/22** state no split protocol at all, **5/22** split on a unit coarser than a random row (zone, device, rolling-origin time, travel day, deployment event) and **0/22** hold out the *mobility unit* for a per-timestep classification task on measured radio, **0/22** report a calibration curve, **0/22** report a lead-time distribution or false alarms per hour, **2/22** report a prevalence-aware ranking metric, **7/22** report headline accuracy on an imbalanced task. | **narrowed twice, and the zeros held** |
| **C14** | **Reproducible authenticity audit** that detected a synthetic dataset, validated against real controls. | holds |
| **C18** | **Leave-one-capture-out generalisation.** Hold out a whole day, corridor and speed regime: 0.949 / 0.909 / 0.943 / **0.927** AUROC at 1 s. The highway capture, frozen-model, scores the highest lift (14.9x) and lowest ECE (0.018) of the four. | **new, 15 Sept** |
| **C19** | **Ping-pong rates in this literature are not comparable.** Three unstated definition choices move the rate from **24.5% to 41.3%** on the same 938 handovers. The mechanism is localised: 31.0% intra-carrier against 6.5% inter-carrier, and 29.2% on the one +1 dB / 320 ms profile that fires 72% of handovers. | **new, 15 Sept** |
| **C15** | **Report-conversion prediction.** Given an A3 report has been sent, will the network act within 2 s? **AUPRC 0.731 (lift 1.87×), AUROC 0.777**, 6,354 reports, 43 drives. Ghoshal et al. measured the non-conversion rate; nobody has modelled it. | **new** **Four-capture re-run returned a degenerate label set; do not quote a number until it is re-checked (MASTER §21).** |
| **C16** | **A sub-sample-period horizon is labelable when the event clock is finer than the sample clock.** Signalling handovers carry millisecond timestamps, so 0.5 s prediction is well posed on a 1 Hz grid: prevalence 4.2%, AUPRC 0.437, lift 10.4×. The 1 Hz ceiling bounds *event detection*, not horizon resolution — a distinction the literature does not draw. | **new** |
| **C17** | **Signalling-derived features are informative alone and redundant in combination.** Time since last A3 report (AUROC 0.703) and A3 reports in the previous 3 s (0.685) beat the A3 gap the deployed rule thresholds on (0.566), yet adding the whole block to the model gains only 0.005–0.012 AUPRC. Fourth instance of the paper's own pattern. | **new** |
| ~~R8~~ | ~~Predictability is invariant to A3 configuration~~ | withdrawn (doc 18) |
| ~~doc 15 §2~~ | ~~The A3 gap condition covers 92.5% of samples~~ | withdrawn; the corrected, hysteresis-inclusive figure is **27.1%** |
| ~~doc 19 item F~~ | ~~A dedicated ping-pong predictor will beat the generic model~~ | **refuted by my own test** — see below |

---

## The one I got wrong

Doc 19 predicted that the benefit envelope was unfair to the predictor because
it ranked samples with a generic handover model rather than a ping-pong model.
It is the other way round.

| | dedicated ping-pong model | generic handover model |
|---|---|---|
| AUROC | 0.670 | 0.933 (on its own task) |
| ping-pongs covered @ 10% alarms | 58.3% | **87.0%** |
| excess over random @ 5% alarms | +0.003 | **+0.318** |

Ping-pong is 8.6% prevalent and weakly predictable before its first leg. Every
ping-pong is a handover, so ranking by handover imminence — which the model
does at AUROC 0.93 — catches them far more efficiently than a noisy dedicated
score. The doc 15 envelope was not being unfair; it was already using the right
ranker.

---

## The pattern from doc 14, revised again

Doc 14 claimed *"more information does not help; better formulation does"* on
four instances, one of which reversed. With the signalling ablation there are
now four standing instances of the first half:

> Neighbour coverage raised from 28% to 79%: no accuracy change. Explicit
> self-excitation features: no accuracy change. The full RRC signalling channel
> added as features: +0.005 to +0.012 AUPRC. A dedicated ping-pong target: worse
> than the generic one. Reformulating as a hazard: coherence and calibration
> from a single fit. Configuration, by contrast, *does* matter — cross-regime
> transfer costs 0.088 AUROC.

Four independent information channels, each measured, each adding nothing. That
is a stronger version of the claim than doc 14 could make, because each of the
four was added in good faith expecting a gain.

---

## What the headline table now says

The curated 6-8 Sept export is no longer part of the evidence base and the
old-versus-new comparison against it has been removed from this document, from
the master document and from the figures. The comparison that replaces it is
the one a reviewer will ask for: **what happened when a fourth capture, in a
new corridor at double the speed, was added to the pool.**

```
LightGBM @ 1 s       three captures        four captures
samples                   7,740               10,260
handovers                   761                  938
prevalence                 7.3%                 6.7%
AUPRC                     0.797                0.784
AUPRC lift               10.98x               11.70x
AUROC                     0.933                0.933
ECE                       0.025                0.024
event detection           44.9%                44.7%
bootstrap groups             43                   57
```

**AUROC moved by zero.** The fourth capture is a highway corridor driven after
every modelling decision was frozen; adding it cost nothing and improved the
prevalence-adjusted lift. Held out whole it is predicted at AUROC 0.927 — see
C18 below and MASTER §19.1.

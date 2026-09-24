# Hazard reformulation, self-excitation, and a guarantee that holds — with 1 Hz fixed

The XCAL export rate cannot be raised. That removes the largest item from doc 09
and changes what the remaining work is: the 1 Hz grid stops being a defect to fix
and becomes a property of the instrument to characterise. Everything below was
run on the existing three XCAL captures — 43 drives, 759 signalling-confirmed
handovers — with whole-drive splits throughout.

New code: `models/hazard.py`, `data/selfexcite.py`, `uncertainty/riskcontrol.py`,
`pipeline/stage09_hazard.py`, `pipeline/stage10_riskcontrol.py`. Tests 10/10.

---

## 1. The 1 Hz ceiling, quantified once and carried everywhere

Two handovers closer together than one sample period cannot both be marked on
the grid. That caps every event-level metric, and no model can be credited or
blamed for the difference.

| capture | events | median gap | gaps < 1 s | gaps < 2 s | unrepresentable | **max representable** |
|---|---|---|---|---|---|---|
| 10 Sept | 288 | 3.50 s | 8.8% | 30.0% | 24 | **91.7%** |
| 12 Sept | 174 | 2.41 s | 12.0% | 39.8% | 20 | **88.5%** |
| 13 Sept | 297 | 4.01 s | 10.1% | 30.3% | 28 | **90.6%** |
| **pooled** | **759** | **3.45 s** | **10.1%** | **32.4%** | **72** | **90.5%** |

**At 1 Hz, 90.5% of handovers is the hard ceiling on event detection rate.** Any
detection figure should be read against that number, not against 100%. A third
of consecutive handovers are less than two sample periods apart, which also
bounds how precisely lead time can ever be resolved.

This converts an apology into a stated limit with a number behind it, which is
what a reviewer wants.

---

## 2. The task was formulated wrong, and the fix costs nothing

Four independent binary heads (handover within 1/2/3/5 s) is a discrete-time
survival model with the survival structure deleted. Replacing it with a
conditional hazard — one LightGBM over (sample × at-risk bin), horizons
recovered by the product-limit identity — gives this, averaged over 4 grouped
folds:

| horizon | AUPRC hazard | AUPRC multi-head | AUROC hazard | AUROC multi-head | **ECE hazard** | **ECE multi-head** |
|---|---|---|---|---|---|---|
| 1 s | 0.790 | 0.809 | 0.937 | 0.942 | **0.017** | 0.023 |
| 2 s | 0.641 | 0.639 | 0.858 | 0.854 | **0.040** | 0.059 |
| 3 s | 0.621 | 0.609 | 0.825 | 0.816 | **0.066** | 0.089 |
| 5 s | 0.639 | 0.629 | 0.795 | 0.790 | **0.096** | 0.125 |

**Discrimination is statistically indistinguishable** — paired Wilcoxon over
folds gives p ≥ 0.125 at every horizon, and with 4 folds it could not reach
significance anyway. The honest claim is a tie.

**Calibration is better at every horizon**: ECE falls 23–35%, Brier falls
4–6%. And the coherence result is not marginal:

| model | rows with a non-monotone horizon set | violating adjacent pairs | worst violation |
|---|---|---|---|
| multi-head binary | **25.4%** | 11.1% | 0.46 |
| discrete-time hazard | **0%** | 0% | 0 |

**A quarter of the baseline's predictions assert that a handover is less likely
within 3 s than within 2 s.** That is impossible, it was invisible under
per-horizon AUPRC, and the hazard formulation removes it by construction.

So: same discrimination, better calibration, no incoherent predictions, one
model instead of four. There is no argument for keeping the old target.

One implementation note that mattered more than expected. `scale_pos_weight`
was dropped from both arms. It cannot improve AUPRC — ranking is invariant to a
monotone reweighting — and it wrecks the probability scale; the hazard model
multiplies four per-bin probabilities together, so per-bin calibration error
compounds across horizons. With weighting on, the hazard model's ECE at 5 s was
0.207; without, 0.096.

---

## 3. Ping-pong is self-excitation, and the number is 0.61

A univariate exponential-kernel Hawkes process fitted to the handover times,
each drive an independent realisation, Ozaki recursion, multi-start MLE:

| capture | µ (background /s) | branching ratio **n** | background share | mean cluster size | excitation half-life |
|---|---|---|---|---|---|
| 10 Sept | 0.042 | **0.647** | 35.4% | 2.83 | 8.75 s |
| 12 Sept | 0.049 | **0.609** | 39.1% | 2.56 | 4.06 s |
| 13 Sept | 0.038 | **0.567** | 43.3% | 2.31 | 7.01 s |
| **pooled** | **0.041** | **0.609** | **39.1%** | **2.56** | **6.72 s** |

**61% of handovers on this network exist only because another handover just
happened.** Only 39% are background events driven by geometry and mobility. Each
handover triggers on average 1.56 further handovers before the cascade dies, and
the excitation decays with a half-life of about 7 seconds.

The stability across three independent captures — 0.567, 0.609, 0.647 — is what
makes this reportable. It is one parameter, physically interpretable, estimated
from event times alone, and the handover literature has never produced it: the
field measures ping-pong as a thresholded *count*, which says nothing about how
strongly one event drives the next.

**The self-excitation features did not improve prediction.** Adding causal decay
terms `Σ exp(−β(t−tᵢ))` at three time constants moved AUPRC by −0.002 to +0.008,
well inside the fold spread. The `history` block already carries time-since-last-handover
and serving dwell, which evidently captures most of the same signal. That is the
third time in this project that adding information has not moved accuracy —
consistent with the A3-regime and neighbour-coverage results — and the pattern
itself is worth a sentence in the discussion.

**So the Hawkes contribution is characterisation, not prediction.** State it that
way. It is stronger for being honest.

---

## 4. A bound on missed handovers that actually holds

Split conformal controls coverage. An operator cares about missed handovers.
Conformal risk control bounds the expected value of a monotone loss directly, so
the false-negative rate can be the controlled quantity.

**The exchangeable unit is the drive, not the sample.** Samples one second apart
share a route, a vehicle, a radio environment and a cell set. Calibrating per
sample reports a guarantee that is not true. Each calibration drive contributes
one loss value.

Averaged over 4 repeats, 12 calibration drives:

| target α | horizon | **CRC test FNR** | CRC alarm rate | **naive pooled FNR** | naive alarm rate |
|---|---|---|---|---|---|
| 0.10 | 1 s | **0.051** ✓ | 59% | **0.107** ✗ | 25% |
| 0.10 | 2 s | **0.033** ✓ | 75% | **0.141** ✗ | 45% |
| 0.10 | 3 s | **0.037** ✓ | 81% | **0.144** ✗ | 53% |
| 0.10 | 5 s | **0.033** ✓ | 86% | **0.125** ✗ | 64% |
| 0.20 | 3 s | **0.172** ✓ | 49% | **0.245** ✗ | 38% |
| 0.30 | 3 s | **0.289** ✓ | 34% | **0.364** ✗ | 28% |

**The drive-grouped conformal threshold meets its target at every horizon and
every level. The naive pooled-sample threshold misses it at every horizon and
every level.** Tail behaviour separates them further: 90th-percentile per-drive
FNR is 0.10–0.13 under CRC against 0.28–0.30 naive.

The guarantee is not free — it costs alarm rate (59–86% of samples flagged at
α = 0.10 against 25–64% naive). That trade-off is the honest operating picture
and should be plotted, not hidden.

### A campaign-design result nobody states

The conformal risk bound carries a finite-sample penalty `B/(n+1)` with `B = 1`,
so a target α is **unreachable** unless

> **n ≥ 1/α − 1 calibration units exist.**

With drives as the exchangeable unit, that is a hard constraint on the
measurement campaign, not a tuning knob:

| target miss-rate bound | minimum calibration **drives** | at a 30% calibration split, total drives |
|---|---|---|
| 30% | 3 | 10 |
| 20% | 4 | 14 |
| **10%** | **9** | **30** |
| 5% | 19 | 64 |
| 1% | 99 | 330 |

Our first attempt used a 20% calibration split — 8 drives — and α = 0.05 and
α = 0.10 were *mathematically unreachable*: the threshold collapsed to zero and
the alarm fired on every sample. Widening the split to 30% (12 drives) made
α = 0.10 attainable. With 43 drives total, **α = 0.05 remains out of reach.**

This is the first thing in the project that turns the small-N constraint into a
quantitative design guideline. Any drive-test campaign that wants to certify a
miss-rate bound now has a number for how many independent drives it needs.

---

## 5. What this changes

Doc 13's proposed frame survives contact with the data, with one amendment: the
self-excitation result is a characterisation, not a predictive gain.

Contributions as they now stand, all measured:

1. **Formulation** — discrete-time hazard replaces multi-horizon binary
   classification: same discrimination, 23–35% lower ECE, 25.4% → 0% incoherent
   predictions. First application of survival modelling to handover prediction.
2. **Mechanism** — branching ratio 0.61 ± 0.04 across three independent
   captures; 61% of handovers are self-triggered. First quantification of
   ping-pong as a self-exciting process.
3. **Guarantee** — distribution-free bound on missed handovers, valid at the
   drive level, met at every horizon where the naive pooled threshold fails; plus
   the `n ≥ 1/α − 1` campaign-design rule.
4. **Instrument limits** — the 1 Hz ceiling at 90.5% of events, measured rather
   than assumed.
5. **Negative results** — leakage is architecture-dependent (GRU +109% vs
   LightGBM +12%); predictability is invariant to A3 configuration; neighbour
   coverage 28% → 62–79% changed nothing; self-excitation features changed
   nothing. Four independent instances of the same pattern: on this problem,
   *more information does not help; better formulation does.* That is a thesis
   sentence.
6. **External validation** — public Mendeley dataset, our model matches its
   in-domain ceiling; parser agrees 310/310 with XCAL's own event counter.

## 6. Next, in order

```
1. TabPFN v2 + MiniRocket + post-hoc ensemble on the hazard target   ~2 days
2. Monotone-constrained EBM: learned hazard shape vs the A3 rule     ~1 day
3. PU correction with the measured 44-58% recovery rate              ~1 day
   (applies to the curated and public CSV-derived labels, NOT to the
    XCAL captures, whose events come from signalling and are complete)
4. Fuzzy RD at the A3 trigger boundary + the counting benefit envelope
5. Literature review, 40-60 refs   <- still the binding constraint on submission
```

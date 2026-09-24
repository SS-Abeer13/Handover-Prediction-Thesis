# Results after the improvement plan: one dataset, a fair baseline, and three claims that changed

Doc 19 listed thirteen possible improvements. Items **A, B, C, D, E, F, G, H and J**
are now done and their results are below. The short version:

```
A  benchmark rerun on XCAL signalling data   DONE    changes every headline number
B  0.5 s horizon reinstated                  DONE    new horizon, prevalence 4.2%
C  fair hazard baseline                      DONE    C1 NARROWED - see §3
D  20 paired observations, CIs on deltas     DONE    every paired claim now has power
E  signalling features + conversion task     DONE    small gain; one strong NEW result
F  dedicated ping-pong predictor             DONE    HYPOTHESIS REFUTED - see §6
G  Hawkes goodness-of-fit                    DONE    C2 NARROWED - see §5
H  CRC frontier on the hazard model          DONE    usable operating point found
J  multi-seed                                DONE    folded into C and E
```

Three claims changed. Two got stronger, one got much weaker and more interesting.
Nothing was hidden.

---

## 1. The dataset split is gone (item A)

Every table in the manuscript now describes the same data.

| | old benchmark | new benchmark |
|---|---|---|
| data | curated 6–8 Sept | pooled XCAL 10/12/13 Sept |
| handover truth | serving-cell transitions | **RRC signalling, ms timestamps** |
| drives | 7 pseudo-drives | **43** |
| samples | 8,347 | 7,740 |
| handovers | — | **761** |
| bootstrap groups | 7 | **43** |
| protocol | one 15% test split | **grouped 5-fold, every drive tested once** |
| feature set | rf+mob+hist+qoe (113) | rf+mob+hist (107) — XCAL has no RTT/loss |

The same LightGBM, on the same task:

| horizon | AUPRC old → new | lift old → new | AUROC old → new | ECE old → new |
|---|---|---|---|---|
| **0.5 s** | — → **0.437** | — → **10.4×** | — → 0.913 | — → 0.026 |
| **1 s** | 0.191 → **0.797** | 3.35× → **10.98×** | 0.816 → **0.933** | 0.037 → **0.025** |
| 2 s | 0.306 → 0.630 | 2.90× → 4.69× | 0.816 → 0.846 | 0.064 → 0.070 |
| 3 s | 0.387 → 0.599 | 2.64× → 3.20× | 0.817 → 0.807 | 0.075 → 0.107 |
| 5 s | 0.494 → 0.600 | 2.29× → 2.18× | 0.816 → 0.769 | 0.088 → 0.155 |

Event level, 1 s horizon: detection **16.9% → 44.9%**, and at 5 s **41.8% → 68.1%**.

The gain is concentrated at short horizons, which is what signalling ground truth
should buy: a transition-derived event log cannot place a handover inside the
second it happened, so the 1 s label was partly noise.

**The 0.5 s horizon is back** (item B). Signalling handovers are 100%
millisecond-timestamped, so the guard that dropped sub-sample-period horizons
does not apply to this event clock. Prevalence 4.2%, almost exactly half of the
1 s rate, which is the sanity check that it is a real label and not an artefact.

### Model ranking, 1 s horizon, out-of-fold over 43 drives

| model | AUPRC | AUROC | ECE | recall @ FPR 5% |
|---|---|---|---|---|
| **LightGBM** | **0.797** | **0.933** | **0.025** | **0.754** |
| logistic regression | 0.741 | 0.920 | 0.123 | 0.738 |
| MLP | 0.689 | 0.913 | 0.080 | 0.704 |
| Transformer | 0.570 | 0.859 | 0.086 | 0.617 |
| TCN | 0.531 | 0.867 | 0.095 | 0.560 |
| GRU | 0.486 | 0.863 | 0.126 | 0.474 |
| A3 rule | 0.128 | 0.656 | 0.166 | 0.107 |

Logistic regression is second. On 43 drives and 7,740 samples the sequence models
have nothing to learn that the snapshot features do not already carry.

---

## 2. The leakage study is now a much better result (item A, side effect)

Same protocol on both sides, seven models, five horizons. Relative AUPRC
inflation from replacing grouped-drive splitting with random-row splitting:

| model | 0.5 s | 1 s | 2 s | 3 s | 5 s |
|---|---|---|---|---|---|
| **GRU** | **+92%** | +65% | **+91%** | **+90%** | **+82%** |
| **Transformer** | +60% | +38% | +54% | **+64%** | +58% |
| **TCN** | +42% | +44% | +45% | +50% | +43% |
| MLP | +33% | +17% | +18% | +17% | +19% |
| LightGBM | +18% | +3% | +15% | +29% | +44% |
| logistic regression | +12% | +9% | +14% | +13% | +15% |
| A3 rule | +65% | +37% | +3% | +5% | −5% |

The old version of this claim was a single pair (GRU +109% vs LightGBM +12%).
It is now an ordering with a mechanism: **sequence models leak most, because a
10 s window straddling a random-row split shares samples with its own training
set.** Snapshot models leak least. A paper that reports random-row results for a
GRU is overstating by roughly a factor of two.

---

## 3. C1 is narrowed: the hazard model wins coherence, not calibration (item C)

This is the claim that changed most, and the change is the whole point of having
run the check.

Six arms, identical folds, 5 seeds × 4 folds = **20 paired observations**.

### Calibration (ECE, lower is better)

| horizon | hazard LGBM | multi-head raw | multi-head + isotonic | + isotonic + monotone |
|---|---|---|---|---|
| 0.5 s | 0.021 | 0.027 | **0.014** | 0.015 |
| 1 s | 0.017 | 0.023 | **0.012** | 0.013 |
| 2 s | 0.042 | 0.060 | **0.031** | 0.032 |
| 3 s | 0.065 | 0.088 | **0.050** | 0.049 |
| 5 s | 0.095 | 0.124 | **0.069** | 0.070 |

Paired deltas, hazard minus comparator (negative = hazard better):

| comparator | metric | 1 s | 5 s | all horizons |
|---|---|---|---|---|
| multi-head raw | ECE | **−0.006** [−0.007, −0.005] | **−0.030** [−0.033, −0.026] | p < 0.0001 |
| multi-head + isotonic | ECE | **+0.005** [+0.003, +0.008] | **+0.026** [+0.014, +0.036] | p ≤ 0.001 |
| multi-head + iso + mono | ECE | +0.004 [+0.001, +0.007] | +0.025 [+0.014, +0.034] | p ≤ 0.011 |

So: **the hazard model is better calibrated than a raw baseline and worse
calibrated than a calibrated one.** The stage 09 claim "ECE −23 to −35%" was
true and was measured against a baseline nobody would deploy.

### Monotonicity (fraction of rows with a non-monotone horizon sequence)

| arm | violating rows | max violation |
|---|---|---|
| **hazard LGBM** | **0%** | 0 |
| multi-head raw | 47.3% | 0.484 |
| multi-head **+ isotonic** | **47.4%** | **0.585** |
| multi-head + isotonic + monotone | 0% | 0 |

**Per-horizon isotonic calibration makes coherence worse, not better** — the max
violation grows from 0.484 to 0.585, because each horizon is recalibrated
independently and nothing couples them. Only an explicit monotone projection
fixes it.

### Ranking (AUPRC), hazard minus comparator

| comparator | 0.5 s | 1 s | 2 s | 3 s | 5 s |
|---|---|---|---|---|---|
| multi-head raw | −0.005 | **−0.023** | −0.009 | +0.002 | +0.009 |
| multi-head + isotonic | **+0.032** | **+0.023** | **+0.037** | **+0.047** | **+0.043** |
| + isotonic + monotone | +0.007 | +0.002 | **+0.017** | **+0.023** | **+0.027** |

Isotonic calibration costs 2–5 AUPRC points; the monotone projection gives most
of it back.

### The learner control: is it the formulation or is it LightGBM?

Arms 5 and 6 repeat the comparison with a small MLP in place of LightGBM, same
folds, 2 seeds × 4 folds = 8 pairs.

| learner | metric | 0.5 s | 1 s | 2 s | 3 s | 5 s |
|---|---|---|---|---|---|---|
| **LightGBM** | ECE (hazard − multi-head) | **−0.006** | **−0.006** | **−0.017** | **−0.024** | **−0.031** |
| | | p=.008 | p=.008 | p=.008 | p=.008 | p=.008 |
| **MLP** | ECE (hazard − multi-head) | −0.002 | +0.001 | +0.001 | +0.004 | −0.003 |
| | | p=.023 | p=1.00 | p=.844 | p=.461 | p=.383 |
| **LightGBM** | AUPRC | −0.003 | −0.028 | −0.006 | +0.002 | +0.009 |
| **MLP** | AUPRC | +0.020 | **−0.113** | **−0.061** | **−0.041** | −0.017 |

**The calibration benefit is learner-dependent.** With gradient boosting the
hazard formulation improves ECE at every horizon; with a neural learner the
same formulation gives nothing on calibration and costs real ranking quality.
The coherence benefit (0% violations) holds for both, because it is a property
of the product-limit identity rather than of the learner.

### The rewritten C1

> A single discrete-time hazard model produces predictions that are
> horizon-coherent by construction and better calibrated than an uncalibrated
> multi-head baseline (ECE −0.006 to −0.030, all p < 0.0001, 20 paired folds).
> The multi-head baseline can match or beat it on calibration, but only by
> spending a held-out calibration split on per-horizon isotonic regression,
> which costs 2–5 AUPRC points and — on its own — makes horizon coherence
> *worse* than leaving it uncalibrated. Recovering coherence needs a second
> post-hoc step. The hazard formulation's contribution is therefore that it
> obtains calibration, coherence and ranking **simultaneously, from one fit,
> without spending drives on calibration** — not that it is uniquely
> well-calibrated. The calibration half of that is specific to the gradient
> boosting learner: repeated with a neural learner, the formulation gives no
> calibration gain and costs ranking. The coherence half holds for any learner,
> because it follows from the product-limit identity rather than from the fit.

That is a narrower claim than doc 14's and a much harder one to attack.

---

## 4. Every paired comparison now has power (item D, J)

Stage 09 ran 4 folds. A two-sided Wilcoxon on 4 pairs cannot return a p below
0.125, so `hazard_paired_test.md` — where the smallest p was exactly 0.125 —
was reporting the floor of the test, not a property of the data.

Now: 5 seeds × 4 folds = 20 pairs, a bootstrap CI on every delta, and p values
down to 1e-5. Several comparisons that looked null are significant, and the
direction of one of them reversed.

---

## 5. C2 is narrowed: strongly self-exciting, imperfectly Hawkes (item G)

| check | pooled result | reading |
|---|---|---|
| branching ratio | **0.611**, bootstrap 95% CI **[0.506, 0.704]** | replaces "± 0.04", which was the spread across captures, not a CI |
| LR vs homogeneous Poisson | χ² = 256.6, **p ≈ 5 × 10⁻⁵⁸** (boundary mixture) | the process is emphatically not Poisson |
| **Ogata residual KS vs Exp(1)** | D = 0.074, **p = 7 × 10⁻⁴** | **the exponential-kernel Hawkes model is rejected as an exact fit** |
| gamma renewal alternative | shape **0.78** (< 1 = clustered), KS p = 3 × 10⁻¹² | the renewal alternative is rejected far more strongly |

Per capture the Ogata KS p values are 0.030 / 0.052 / 0.068 — marginal, and
only the pooled test is decisive, which is what more data does to a
misspecified model.

### The rewritten C2

> Handover arrivals are strongly clustered and decisively non-Poisson
> (LR p ≈ 5 × 10⁻⁵⁸; gamma renewal shape 0.78 < 1). An exponential-kernel
> Hawkes process fits far better than either a Poisson or a gamma renewal
> alternative but is itself rejected by an Ogata residual test on the pooled
> data (p = 7 × 10⁻⁴), so its branching ratio of 0.61 [0.51, 0.70] should be
> read as a calibrated measure of clustering strength under a stated kernel,
> not as an exact generative model of the process.

A reviewer who runs the residual test themselves now finds what the paper
already said.

---

## 6. C3 has a usable operating point (item H)

Conformal risk control now runs on the **hazard model's** incidence with
calibration drives pooled across all three captures (22 drives, so the
feasibility floor drops from α ≥ 0.077 to **α ≥ 0.044**).

1 s horizon:

| α | certified alarm rate | test FNR | per-drive FNR p90 | drives over α |
|---|---|---|---|---|
| 0.05 | 82% | 0.007 | 0.000 | 4.8% |
| 0.10 | 55% | 0.010 | 0.000 | 4.8% |
| 0.15 | 34% | 0.087 | 0.200 | 19% |
| 0.20 | **27%** | 0.115 | 0.250 | 14% |
| 0.30 | **8.8%** | 0.258 | 0.500 | 24% |

The guarantee is expensive below α = 0.15 and cheap above it. At α = 0.2 the
certified threshold alarms on 27% of samples while missing 11.5% of handovers,
and at α = 0.3 on under 9%. This is the frontier figure the paper needs: a
distribution-free bound is not free, and the price is now stated rather than
implied.

---

## 7. Signalling features help a little; report conversion is a new result (item E)

### The ablation

| horizon | rf+mob+hist | **+ signalling** | signalling only |
|---|---|---|---|
| 0.5 s | 0.455 | **0.467** | 0.219 |
| 1 s | 0.8106 | 0.8106 | 0.370 |
| 2 s | 0.646 | **0.651** | 0.381 |
| 3 s | 0.615 | **0.620** | 0.432 |
| 5 s | 0.633 | **0.638** | 0.500 |

AUPRC, mean over 3 seeds. Gains of 0.005–0.012 at every horizon except 1 s,
where there is none. **The signalling channel adds almost nothing on top of
dwell and RF** — which is the fourth instance of the paper's own pattern that
more information does not help.

But the features are informative *on their own*. Single-feature AUROC at 1 s:

```
serving dwell time          0.874
serving SINR                0.830
time since last A3 report   0.703   <- new, signalling
A3 reports, previous 3 s    0.685   <- new, signalling
time since previous HO      0.652
A3 hold time (TTT clock)    0.615   <- new, signalling
serving-to-neighbour gap    0.566
```

The two report features beat everything except dwell and SINR, and comfortably
beat the A3 gap that the deployed rule actually thresholds on. They are
redundant with dwell rather than uninformative.

### Report conversion — the strongest new result

Ghoshal et al. measured that most reported A3 events never become a handover.
Nobody has modelled it. Given that a report has been sent, will the network act
on it within 2 s?

| | |
|---|---|
| reports | 6,354 A3 reports across 43 drives |
| conversion rate | 39.1% |
| **AUPRC** | **0.731 ± 0.003** (lift 1.87×), CI [0.691, 0.765] |
| **AUROC** | **0.777 ± 0.005** |

The network's decision to act on a report is substantially predictable from the
radio state at the moment of the report. That is a clean, previously unmodelled,
network-side task that falls straight out of the signalling parser.

---

## 8. Item F is refuted, which is itself the finding

Doc 19 predicted that ranking by a dedicated ping-pong model would beat ranking
by the generic handover model. It does not — it is much worse.

| | dedicated ping-pong model | generic handover model |
|---|---|---|
| AUPRC | 0.151 ± 0.011 (lift 1.76×) | — |
| AUROC | 0.670 ± 0.004 | 0.933 (handover task) |
| ping-pongs covered @ 10% alarms | 58.3% | **87.0%** |
| **excess over random @ 5% alarms** | **+0.003** | **+0.318** |
| excess over random @ 10% alarms | −0.068 | **+0.218** |
| excess over random @ 20% alarms | −0.145 | +0.035 |
| excess over random @ 40% alarms | −0.078 | −0.019 |

Ping-pong is only 8.6% prevalent and only weakly predictable before its first
leg (AUROC 0.67). The generic model predicts *handovers* at AUROC 0.93, and
since every ping-pong is a handover, ranking by handover imminence catches them
far more efficiently than ranking by a noisy ping-pong score.

**The doc 15 benefit-envelope conclusion survives and improves.** On the new
data the generic ranker earns a positive excess over a same-rate random alarm
up to a **20%** budget (+0.035) rather than 10%, and is strongly positive at 5%
(+0.318 vs the old +0.291). Above 20% it goes negative, as before.

---

## 9. Corrected mechanism numbers (recomputed with hysteresis)

The trigger-coverage calculation in doc 18 omitted hysteresis. With it, and with
three profiles clearing the 30-handover bar on the pooled data:

| A3 profile | share of handovers | fires when gap < | sample coverage |
|---|---|---|---|
| **+1 dB / Hys 1 dB / TTT 320 ms** | **74.6%** | **−2 dB** | **12.4%** |
| −10 dB / Hys 2 dB / TTT 640 ms | 13.1% | +8 dB | 73.6% |
| −15 dB / Hys 1 dB / TTT 160 ms | 7.7% | +14 dB | 91.4% |

**Handover-weighted trigger coverage: 27.1%** (doc 18 said 25.3%, doc 15 said
92.5%). Non-conversion on the pooled QC'd drives: **61.3%** (doc 18: 60.6%).

`fig_mechanism_a3.png` is regenerated from these numbers and is now produced by
a pipeline stage rather than by hand, so it cannot go stale again.

---

## 10. What is in the repo now

New modules:

```
src/hoproj/data/signalling_features.py    TTT clock, report history, RF slopes
src/hoproj/models/monotone.py             PAVA projection, isotonic, neural hazard
src/hoproj/eval/figures.py                manuscript figures, computed not typed
tests/test_signalling_features.py         7 tests pinning the leakage boundary
```

New stages:

```
stage12_xcal_prepare      pooled XCAL dataset in stage01's layout
stage13_xcal_benchmark    7 models x 5 horizons, grouped K-fold, leakage control
stage14_hazard_fair       6 arms, 5 seeds x 4 folds, CIs on every delta
stage15_gof_frontier      Ogata residuals, LR test, bootstrap CI, CRC frontier
stage16_signalling_pingpong  ablation, report conversion, ping-pong predictor
stage17_figures           the mechanism figure
```

Tests: **17 passing** (10 before, 7 new).

One behaviour change to an existing module: `labels.usable_horizons` now accepts
sub-sample-period horizons when `labels.allow_subperiod_horizons` is set, which
only the XCAL adapter sets. The guard still fires by default for the curated
adapter, where it is correct.

---

## 11. What is left

```
I  equal tuning budget (nested grouped CV)      not started
K  per-drive z-scoring / CORAL transfer         not started
L  FinalManuscript model under our protocol     not started
M  one more capture day                         field work
   hazard MLP learner control (arms 5-6)        DONE - see §3
   literature pass 2 on 17 papers               not started
   THE MANUSCRIPT                               not started
```

Item I matters less than it did: LightGBM beats every deep model by a wide
margin on the new data, and logistic regression is second, so "the deep
baselines were under-tuned" is a weaker objection when a linear model also
beats them.

The bottleneck has not moved. It is the writing.

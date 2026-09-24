# The decision link, the mechanism figure, and two errors caught

Continuing from doc 14 with 1 Hz accepted as permanent. New code:
`eval/benefit.py`, `pipeline/stage11_mechanism_benefit.py`. Tests 10/10.

Two of my own mistakes surfaced here and both changed a conclusion, so they are
recorded in place rather than quietly fixed.

---

## 1. What predicting handovers could actually buy

Off-policy evaluation is unavailable — the A3 rule is a deterministic logging
policy, so every estimator collapses to the analyst's own outcome model
(doc 13 §6). What *is* identified, by counting alone, is an upper bound.

For each observed ping-pong, ask a purely factual question: **did the predictor
raise an alarm at least τ seconds before it?** If not, no intervention driven by
this predictor could have prevented that event, whatever the intervention was.
`K(τ)/N` is then an upper bound on the avoidable fraction, requiring no
counterfactual whatsoever.

Test drives, hazard model, 2 s horizon score, 39 ping-pong events:

| alarm budget | ≥1 s warning | ≥2 s | ≥3 s | ≥5 s |
|---|---|---|---|---|
| 2% | 28.2% | 28.2% | 23.1% | 10.3% |
| 5% | 53.8% | 48.7% | 33.3% | 17.9% |
| 10% | 69.2% | 66.7% | 61.5% | 43.6% |
| 20% | 76.9% | 71.8% | 71.8% | 53.8% |

Multiply by an actuator-efficacy parameter η ∈ [0,1] for the attainable
benefit. η is swept, never estimated — the assumption stays visible and
separate from the measurement.

### The part that matters: a random alarm at the same rate

An alarm firing independently at rate *p* already covers `1 − (1−p)^W` of events
over a W-second warning window. Without that reference the table above flatters
itself badly.

**Excess over a same-rate random alarm** (percentage points):

| alarm budget | ≥1 s | ≥2 s | ≥3 s | ≥5 s |
|---|---|---|---|---|
| 2% | **+11.5** | **+13.2** | **+9.8** | +0.6 |
| 5% | **+16.9** | **+15.1** | +3.2 | −4.7 |
| 10% | +8.0 | +9.7 | +9.4 | +2.6 |
| 20% | −9.7 | **−11.4** | −7.2 | −13.4 |
| 40% | −16.9 | **−21.4** | −20.3 | −23.0 |

**The predictor beats a random alarm only below about a 10% alarm budget, and
is clearly worse than random above 20%.** The reason is alarm clustering: a good
ranker fires in bursts around the events it is confident about, and a burst
covers fewer *distinct* events than the same number of independent alarms spread
uniformly. At a 40% budget a random alarm hits essentially every 8-second window.

Two consequences worth stating in the paper:

1. **The useful operating region for this predictor is a low alarm budget** —
   roughly 2–10%, peaking around 5% with a +15 pp excess at 2 s lead.
2. **Event-detection rate reported without a random-alarm reference overstates
   the result**, and the handover-prediction literature reports it that way
   throughout. This is a cheap, general methodological point that costs one
   extra column in any results table.

---

## 2. The mechanism figure, and why the neighbour features never helped

`reports/figures/fig_mechanism_a3.png` — a monotone-constrained Explainable
Boosting Machine fitted to the same discrete-time hazard, its learned shape
function for the serving-to-neighbour gap plotted against the empirical hazard,
with every deployed A3 offset marked at the gap value where it fires.

The figure answers a question left open since doc 10.

The A3 event fires when `Mn − Ms > Off`, i.e. when the gap `Ms − Mn < −Off`. The
four deployed profiles therefore trigger at these gap values, and these fractions
of observed samples sit inside each trigger region:

| A3 profile | fires when gap < | samples inside |
|---|---|---|
| −15 dB | **+15 dB** | **92.5%** |
| −10 dB | +10 dB | 81.4% |
| +1 dB | −1 dB | 15.4% |
| +5 dB | −5 dB | 6.7% |

**The dominant profile's gap condition is satisfied on 92.5% of all samples.** On
this network the A3 gap test is almost always true, so whether it is true carries
almost no information, and the handover timing is governed by time-to-trigger and
by which cells are configured as candidates — not by the gap.

That is a mechanistic explanation for a result that has been unexplained since
doc 10: raising neighbour coverage from 28% to 62–79% changed prediction
accuracy by nothing. The neighbour measurement is not the bottleneck because the
neighbour *condition* is not the discriminating variable on this network. Both
the learned curve and the empirical rate show the expected monotone decrease with
the gap, but the effect is shallow — the hazard contribution spans only about
0.1 log-odds across a 50 dB range.

**Interpretability price, measured:** the additive EBM costs 0.07–0.10 AUPRC
against the LightGBM hazard model (0.651 vs 0.756 at 1 s, 0.530 vs 0.598 at 2 s).
It is a companion mechanism model, not a replacement — report both.

---

## 3. Two errors caught, both worth recording

**I constrained the monotonicity backwards.** `gap_serving_nbr1` is
`serving − neighbour`, so a larger gap means the serving cell is further ahead and
a handover is *less* likely. My first pass imposed an increasing constraint, which
forced the model to fit against the physics. Caught only because the empirical
curve in the second panel ran the opposite way to the learned one. The corrected
constraint barely changed accuracy (0.6507 vs 0.6516 AUPRC), but the shape
function — the entire point of the figure — was inverted and would have been
wrong in the paper.

**I plotted the A3 thresholds at the wrong x-positions.** The offsets are −15,
−10, +1, +5 dB, but on a `serving − neighbour` axis they fire at +15, +10, −1,
−5 dB. Plotting them at their raw values put the aggressive profiles on the wrong
side of zero and hid the 92.5% coverage finding entirely. The corrected placement
is what produced §2.

Both are the same class of error: a sign convention assumed rather than checked.
Worth a line in the methods section about verifying feature-sign conventions
against the physics before imposing priors on them.

---

## 4. Where the project now stands

Measured contributions, all from existing data:

| # | Contribution | Status |
|---|---|---|
| 1 | Discrete-time hazard replaces multi-horizon binary classification — equal discrimination, ECE −23 to −35%, incoherent predictions 25.4% → 0% | done |
| 2 | Ping-pong as self-excitation: Hawkes branching ratio **0.61 ± 0.04** across three captures | done |
| 3 | Distribution-free bound on missed handovers, valid at drive level, met where the naive pooled threshold fails; plus the **n ≥ 1/α − 1** campaign-design rule | done |
| 4 | 1 Hz resolution ceiling: **90.5%** of handovers is the hard cap on event detection | done |
| 5 | Benefit envelope with a random-alarm reference: predictor earns its keep only below a ~10% alarm budget | done |
| 6 | Mechanism: the dominant A3 profile's gap condition covers 92.5% of samples, explaining why neighbour data never helped | done |
| 7 | External validation on the public Mendeley dataset; parser agrees 310/310 with XCAL's own counter | done |
| 8 | Negative results: leakage is architecture-dependent; predictability invariant to A3 configuration; neighbour coverage and self-excitation features changed nothing | done |

**Still open, in priority order:**

1. **Literature review, 40–60 references.** Unchanged as the binding constraint
   on submission. Docs 13 and 14 supply roughly 80 screened references toward it.
2. **TabPFN v2 + MiniRocket + post-hoc ensemble** on the hazard target — the one
   remaining shot at a material accuracy gain (~2 days).
3. **PU correction** with the measured 44–58% label-recovery rate. Applies to the
   curated and public CSV-derived labels, *not* to the XCAL captures, whose
   events come from signalling and are complete.
4. **Fuzzy RD at the A3 trigger boundary** — the local causal effect. Given §2,
   the discontinuity is thin on this network (the dominant profile's boundary sits
   at +15 dB, in the tail of the gap distribution), so expect a small usable
   sample. Worth a feasibility check before committing.
5. **Draft the manuscript.** Everything in the table above is measured; nothing
   is waiting on data.

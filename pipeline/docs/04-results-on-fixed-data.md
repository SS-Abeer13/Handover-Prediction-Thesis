# Results on the fixed data — supersedes `02-first-full-run-results-VOID.md`

Handover log regenerated from the fixed sample export, then the full pipeline
re-run. Budget: 25 epochs, patience 6, 3-member ensembles, 300-draw drive-level
bootstrap, CPU.

Everything from `first-full-run-results.md` is void — it was measured on the
synthetic file. On the device those outputs are parked in
`reports_SYNTHETIC_RUN_do_not_use/` and `artifacts_SYNTHETIC_RUN_do_not_use/`
(they could not be deleted; they can be removed by hand).

## The regenerated event log

`HANDOVER_LOG_REGENERATED.csv`, built by `python -m hoproj.data.event_log` from
the sample file's own serving-cell transitions. Validation:

| | |
|---|---|
| events | 6,515 |
| targets that appear as a serving cell | **100%** |
| target matches the sample at the event instant | **100%** |
| median gap between events | 4.0 s |
| rate | 4.8 / active minute |

The old `HANDOVER_LOG_1.csv` shared **zero** cell names with the fixed export.
`configs/base.yaml` now points at the regenerated log by default.

## Dataset

81,141 samples, 81 drives, 3 corridors, 22.5 h, 725 km, 46 serving cells,
**6,515 handovers, 37.7% ping-pong**.

| corridor | drives | km | mean km/h | handovers | ping-pong | HO/km |
|---|---|---|---|---|---|---|
| farmgate_sciencelab_newmarket | 13 | 127 | 14.0 | 1,823 | 627 | 14.4 |
| gulshan_banani_mohakhali | 33 | 304 | 29.9 | 2,351 | 939 | 7.7 |
| kuril_badda_rampura_malibagh (locked) | 35 | 294 | 44.6 | 2,341 | 890 | 8.0 |

This now matches the real XCAL captures: 4.8 HO/min here against 6.7–7.3 there,
37.7% ping-pong against 23–47%. The synthetic file showed 1.7/min and 7.7%.

## The problem is much harder than the synthetic file suggested

AUPRC, grouped-drive condition. Prevalence: 5.7 / 10.5 / 14.7 / 21.6%.

| model | 1 s | 2 s | 3 s | 5 s |
|---|---|---|---|---|
| A3-style rule | 0.126 | 0.210 | 0.283 | 0.392 |
| logreg | 0.173 | 0.273 | 0.358 | 0.470 |
| **LightGBM** | **0.191** | **0.305** | **0.387** | **0.494** |
| GRU | 0.187 | 0.277 | 0.355 | 0.467 |
| TCN | 0.188 | 0.292 | 0.364 | 0.477 |
| Transformer | 0.177 | 0.269 | 0.349 | 0.461 |

Lift over prevalence is now **2.3–3.3x**, against 5–12x on the synthetic file.
Same code, same protocol — the earlier numbers were the generator being easy.

**LightGBM is the best model at every horizon.** The sequence models do not beat
a snapshot gradient-boosted tree on this data.

### The false-alarm story from the synthetic run does not survive

| model | FA/hour @2 s | detection @2 s |
|---|---|---|
| rule | 28.6 | 0.125 |
| GRU | 61.7 | 0.233 |
| logreg | 65.8 | 0.226 |
| Transformer | 69.9 | 0.248 |
| TCN | 70.7 | 0.258 |
| LightGBM | 77.4 | 0.254 |

The GRU still has the lowest false-alarm rate among the learned models, but the
margin is 1.25x rather than 5.5x, and it comes with a slightly lower detection
rate. Event detection is 23–26% at 2 s against 70% before. **Do not repeat the
"GRU gives the same warnings for a fifth of the false alarms" claim.**

## RQ3 — leakage is worse, and the architecture split holds

Relative AUPRC inflation from random row-level splitting:

| model | 1 s | 2 s | 3 s | 5 s |
|---|---|---|---|---|
| **GRU** | **+59%** | **+109%** | **+96%** | **+69%** |
| LightGBM | -5% | +12% | +25% | +29% |

The GRU's apparent AUPRC **more than doubles** at 2 s (0.277 -> 0.579) purely
from the splitting protocol. LightGBM inflates far less and is even slightly
*worse* under random splitting at 1 s.

This is the strongest result in the run, and it survived the data change — which
is itself evidence that it is about overlapping windows rather than about any
particular dataset. It is the most publishable finding here.

## RQ2 — the locked route

| horizon | AUPRC | 95% CI | prevalence | AUROC | detection | lead | FA/hour | ECE |
|---|---|---|---|---|---|---|---|---|
| 1 s | 0.270 | 0.249–0.296 | 0.070 | 0.834 | 0.143 | 1 s | 56.3 | 0.279 |
| 2 s | 0.387 | 0.354–0.416 | 0.126 | 0.824 | 0.220 | 2 s | 51.2 | 0.242 |
| 3 s | 0.462 | 0.426–0.493 | 0.171 | 0.816 | 0.299 | 2 s | 44.3 | 0.217 |
| 5 s | 0.566 | 0.530–0.599 | 0.244 | 0.814 | 0.374 | 3 s | 30.3 | 0.170 |

External AUPRC again exceeds the development holdout (0.387 vs 0.277 at 2 s),
but prevalence on that route is also higher (12.6% vs 10.5%), so most of the
difference is base rate, not transfer skill. AUROC is the fairer comparison and
sits at 0.81–0.83.

**Calibration is poor on the external route** — ECE 0.17–0.28, far worse than
the ~0.10 seen in development. Temperature scaling fitted on development
calibration drives does not transfer to the new corridor. That is a genuine,
reportable finding about distribution shift, and it is new: the synthetic file
hid it.

## RQ5 — the feature ablation reverses

| feature set | 1 s | 2 s | 3 s | 5 s |
|---|---|---|---|---|
| RF only | 0.174 | 0.261 | 0.343 | 0.461 |
| + mobility | 0.180 | 0.261 | 0.338 | 0.434 |
| **+ cell history** | **0.191** | **0.284** | **0.364** | **0.480** |
| + QoE | 0.187 | 0.277 | 0.355 | 0.467 |

On the synthetic file RF alone was best. Here **cell history is the best feature
set at every horizon** — time since last handover, serving dwell, return-to-source.
That makes sense in a network with 38% ping-pong: recent history predicts the
next bounce. QoE still adds nothing.

Regime: topology-agnostic 0.187/0.277/0.355/0.467 beats context-rich
0.169/0.262/0.340/0.458. Adding GPS, route and cell identity *hurts*. Good for
the transfer claim.

## RQ4 — conformal holds, abstention weakens

Conformal coverage 0.891–0.896 against a 0.90 target, per-drive minimum 0.867.
Solid.

Abstention on the external route is much flatter than before:

| coverage | error | missed handovers |
|---|---|---|
| 100% | 0.281 | 0.218 |
| 90% | 0.290 | 0.191 |
| 80% | 0.289 | 0.167 |
| 70% | 0.278 | 0.145 |
| 50% | 0.229 | 0.095 |

Answering 80% of samples cuts missed handovers by 1.3x (was 4.4x). The
uncertainty signal still carries information, but far less of it.

## What to do with this

1. **Rewrite any draft text based on the old numbers.** Particularly the
   false-alarm claim and the feature-ablation conclusion, both of which reversed.
2. **Lead with RQ3.** GRU AUPRC doubling under random splitting, against
   LightGBM's +12%, is a clean methodological result that held across two very
   different datasets.
3. **Report that sequence models lose to LightGBM here.** It is a negative result
   and the proposal explicitly commits to reporting those.
4. **The external-route calibration failure is a new finding** worth its own
   subsection — it is exactly the "confidently wrong under distribution shift"
   problem the thesis set out to study.
5. **Provenance is still unresolved.** The fixed file passes the physical checks,
   but nobody has yet said where it comes from. Establish that before submission.
6. Longer budget on the GPU (`HO_EPOCHS=120`, `HO_ENSEMBLE=5`, `HO_BOOT=2000`)
   and tune window length inside the development domain.

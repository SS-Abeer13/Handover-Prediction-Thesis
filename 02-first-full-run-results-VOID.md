# First full pipeline run — results  [VOID]

> **VOID.** These numbers were measured on `DRIVETEST_LOGS_1.csv`, which was
> later shown to be synthetic (doc 03). Superseded by doc 04. Kept only so the
> record shows what was claimed and why it was withdrawn. **Do not cite.**

Budget: 25 epochs, patience 6, 3-member ensembles, 300-draw drive-level
bootstrap, CPU. Notebook `pipeline/notebooks/handover_pipeline.ipynb` (+ .html).

## RQ1 / RQ7 — models (grouped-drive, topology-agnostic)

AUPRC by horizon. Prevalence: 3.0 / 6.0 / 9.0 / 14.8%.

| model | 1 s | 2 s | 3 s | 5 s |
|---|---|---|---|---|
| A3-style rule | 0.214 | 0.343 | 0.430 | 0.548 |
| logreg | 0.345 | 0.545 | 0.659 | 0.780 |
| LightGBM | 0.362 | 0.567 | 0.672 | 0.799 |
| GRU | 0.359 | 0.553 | 0.665 | 0.783 |
| TCN | 0.383 | 0.560 | 0.670 | 0.784 |
| Transformer | 0.378 | 0.572 | 0.685 | 0.802 |

False alarms per hour at a 5% FPR threshold fixed on validation drives:

| model | 1 s | 2 s | 3 s | 5 s |
|---|---|---|---|---|
| LightGBM | 46.2 | 37.0 | 29.9 | 25.1 |
| logreg | 24.6 | 21.7 | 22.8 | 23.6 |
| Transformer | 9.3 | 10.1 | 8.6 | 16.1 |
| TCN | 11.6 | 8.2 | 9.3 | 12.8 |
| **GRU** | **7.1** | **6.7** | **6.7** | **9.8** |

**Withdrawn claim:** "the GRU gets the same warnings for a fifth of the false
alarms." On real data the margin is 1.25x, not 5.5x (doc 04).

## RQ3 — leakage

| model | 1 s | 2 s | 3 s | 5 s |
|---|---|---|---|---|
| GRU | +65% | +46% | +35% | +21% |
| LightGBM | +2% | +4% | +7% | +5% |

This is the one result that **survived** the data change — and got stronger on
real data (GRU +109% at 2 s). See doc 04.

## RQ5 — feature ablation

| feature set | 1 s | 2 s | 3 s | 5 s |
|---|---|---|---|---|
| RF only | 0.362 | 0.564 | **0.685** | **0.811** |
| + mobility | 0.368 | 0.560 | 0.668 | 0.794 |
| + cell history | 0.349 | 0.547 | 0.677 | 0.792 |
| + QoE | 0.359 | 0.553 | 0.665 | 0.783 |

**Withdrawn conclusion:** "RF alone is best." On real data cell history wins at
every horizon (doc 04). The ablation reversed.

## RQ2 — the locked route

| horizon | AUPRC | AUROC | detection | FA/hour | ECE |
|---|---|---|---|---|---|
| 1 s | 0.405 | 0.951 | 0.563 | 3.4 | 0.133 |
| 2 s | 0.599 | 0.953 | 0.672 | 5.3 | 0.140 |
| 3 s | 0.709 | 0.955 | 0.760 | 4.9 | 0.127 |
| 5 s | 0.811 | 0.957 | 0.838 | 5.0 | 0.119 |

AUROC ~0.95 is the clearest fingerprint of the synthetic generator; on real data
the same protocol gives 0.81-0.83.

## RQ4 — abstention

| coverage | overall error | missed handovers |
|---|---|---|
| 100% | 0.141 | 0.080 |
| 90% | 0.122 | 0.045 |
| 80% | 0.099 | 0.018 |
| 70% | 0.063 | 0.004 |

4.4x reduction, against 1.3x on real data.

## Two real bugs this run exposed and fixed (these do carry over)

1. Features were only built for the blocks the global config named, so the
   topology-agnostic vs context-rich ablation compared a config against itself.
   Features are now built as a superset; the regime filters at selection time.
2. The context block's `lat`/`lon` collided with the metadata columns of the same
   name. Renamed to `ctx_lat`/`ctx_lon`, with a column-uniqueness assertion.

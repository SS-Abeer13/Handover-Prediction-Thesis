> **VOID — these numbers were measured on the synthetic original file.**
> Superseded by `04-results-on-fixed-data.md`. Kept for the record only.

# First full pipeline run — results

Executed notebook: `D:\Handover Thesis\pipeline\notebooks\handover_pipeline.ipynb`
(+ `.html`). Budget: 25 epochs, early stopping patience 6, 3-member ensembles,
300-draw drive-level bootstrap. CPU. Every table below is regenerable from
`configs/base.yaml` + the capture.

Treat these as a real first pass, not final numbers — epoch budget is modest and
the ensembles are small.

## RQ1 / RQ7 — models (grouped-drive, topology-agnostic, RF+mob+hist+QoE)

AUPRC by horizon. Prevalence: 3.0% / 6.0% / 9.0% / 14.8%.

| model | 1 s | 2 s | 3 s | 5 s |
|---|---|---|---|---|
| A3-style rule | 0.214 | 0.343 | 0.430 | 0.548 |
| logreg | 0.345 | 0.545 | 0.659 | 0.780 |
| LightGBM | 0.362 | 0.567 | 0.672 | 0.799 |
| GRU | 0.359 | 0.553 | 0.665 | 0.783 |
| TCN | 0.383 | 0.560 | 0.670 | 0.784 |
| Transformer | 0.378 | 0.572 | 0.685 | 0.802 |

**On AUPRC the models are indistinguishable** — LightGBM, GRU, TCN and Transformer
sit inside each other's confidence intervals. Only the rule baseline is clearly
behind.

**The separation is entirely at the operating point.** False alarms per hour at a
5% FPR threshold fixed on validation drives:

| model | 1 s | 2 s | 3 s | 5 s |
|---|---|---|---|---|
| LightGBM | 46.2 | 37.0 | 29.9 | 25.1 |
| logreg | 24.6 | 21.7 | 22.8 | 23.6 |
| Transformer | 9.3 | 10.1 | 8.6 | 16.1 |
| TCN | 11.6 | 8.2 | 9.3 | 12.8 |
| **GRU** | **7.1** | **6.7** | **6.7** | **9.8** |

Detection rates are comparable (GRU 0.70 vs LightGBM 0.72 at 2 s), so the GRU
gets the same warnings for a fifth to a sixth of the false alarms. **This is the
headline, not AUPRC** — and it is an argument for event-level evaluation as a
methodological contribution, since a sample-level metric hides it completely.

Inference cost, CPU, batch 1: Transformer 0.66 ms / 170k params, TCN 0.72 ms /
102k, GRU 0.88 ms / 131k. All trivially real-time; RQ7's "compact models are
competitive" holds, though at this scale the GRU is the *slowest* of the three
because it cannot parallelise across the window.

## RQ3 — leakage is architecture-dependent

Relative AUPRC inflation from random row-level splitting versus grouped-by-drive:

| model | 1 s | 2 s | 3 s | 5 s |
|---|---|---|---|---|
| GRU | **+65%** | +46% | +35% | +21% |
| LightGBM | +2% | +4% | +7% | +5% |

The GRU's random-split AUPRC reaches 0.94 at 5 s against 0.78 honest. Sequence
models memorise overlapping near-duplicate windows; a snapshot tree model has
much less to memorise. This is a sharper result than a single global inflation
figure, and it predicts that published sequence-model handover results using
random splits are the ones most likely to be inflated. Worth making a section of
the paper.

## RQ5 — mobility, history and QoE do not pay (yet)

| feature set | 1 s | 2 s | 3 s | 5 s |
|---|---|---|---|---|
| RF only | 0.362 | 0.564 | **0.685** | **0.811** |
| + mobility | 0.368 | 0.560 | 0.668 | 0.794 |
| + cell history | 0.349 | 0.547 | 0.677 | 0.792 |
| + QoE | 0.359 | 0.553 | 0.665 | 0.783 |

RF alone is as good or better at every horizon. A clean negative result. Two
readings, both worth stating: at 117 drives the extra blocks mostly add variance,
and this capture's QoE fields may be too smooth to carry event information. Keep
it in the paper.

Regime: context-rich 0.342/0.545/0.663/0.804 vs topology-agnostic
0.359/0.553/0.665/0.783 — adding GPS, route and cell identity does **not** help.
Good news for the transfer claim: the model is not navigating by landmark.

## RQ2 — the locked route

`kuril_badda_rampura_malibagh`, 33 drives, 650 handovers, never touched before
this point (freeze manifest enforced).

| horizon | AUPRC | 95% CI | AUROC | detection | lead | FA/hour | ECE |
|---|---|---|---|---|---|---|---|
| 1 s | 0.405 | 0.378–0.438 | 0.951 | 0.563 | 1.0 s | 3.4 | 0.133 |
| 2 s | 0.599 | 0.571–0.626 | 0.953 | 0.672 | 2.0 s | 5.3 | 0.140 |
| 3 s | 0.709 | 0.682–0.732 | 0.955 | 0.760 | 3.0 s | 4.9 | 0.127 |
| 5 s | 0.811 | 0.791–0.829 | 0.957 | 0.838 | 4.0 s | 5.0 | 0.119 |

**No generalisation collapse — external AUPRC is slightly above the development
holdout** (0.599 vs 0.553 at 2 s). Word this carefully: that corridor is faster
(44 km/h mean) and has sparser handovers (2.2/km vs 3.3 and 5.2), so it is
plausibly an easier corridor rather than evidence of superior transfer. The
defensible claim is the weaker, sturdier one: performance is maintained on a
geographically disjoint route.

Geographic OOD separation via ensemble disagreement is near chance (AUROC ~ 0.47)
— the ensemble does *not* find the new route unfamiliar. Consistent with the
transfer result, and itself a finding: on this data an uncertainty-based OOD
detector cannot flag a route change.

## RQ4 — calibration and abstention

Conformal coverage lands on target: 0.907–0.912 empirical against a 0.90 nominal,
with per-drive minimum 0.864 — so temporal dependence costs a few points on the
worst drive but does not break coverage.

Abstention on the external route, thresholds frozen beforehand. `fn_risk` =
fraction of real upcoming handovers missed among samples the model still answers:

| coverage | overall error | missed handovers |
|---|---|---|
| 100% | 0.141 | 0.080 |
| 90% | 0.122 | 0.045 |
| 80% | 0.099 | 0.018 |
| 70% | 0.063 | 0.004 |

Answering 80% of samples cuts missed handovers by **4.4×**. That is the RQ4
result, and it is strong.

## Two bugs the full run exposed and fixed

1. Features were only built for the blocks the global config named, so the
   topology-agnostic vs context-rich ablation compared a config against itself
   (identical AUPRC to three decimals gave it away). Features are now built as a
   superset and the regime filters at selection time.
2. The context block's `lat`/`lon` collided with the metadata columns of the same
   name, producing duplicate columns. Renamed to `ctx_lat`/`ctx_lon`, with an
   assertion that the feature frame's columns stay unique.

## Suggested next steps

- Longer budget on the GPU box (`HO_EPOCHS=120`, `HO_ENSEMBLE=5`, `HO_BOOT=2000`)
  and check whether the AUPRC tie between GRU/TCN/Transformer/LightGBM survives.
- Tune window length inside the development domain — 10 s was assumed, never tuned.
- Fix the XCAL logging profile so neighbour and RTT columns populate; the
  candidate-ranking task (RQ6) is untestable until then.
- The false-alarm gap is the paper's spine. Add a sweep of operating points
  rather than the single 5%-FPR threshold.

# Cross-capture transfer: the curated data does not describe your network

> Note: the 4-domain version of this matrix (including 13 Sept) is in
> `09-sept13-regime-transfer-correction.md`. The mechanism section below
> ("Why") is re-labelled there: it is a curated-vs-XCAL difference, not an
> A3-configuration difference.

Train on one capture, test on another. Different days, routes, cells and
equipment settings. The scaler, the decision thresholds and the temperature are
all fitted on the source; the target contributes nothing.

Code: `src/hoproj/pipeline/stage06_cross_capture.py`.
Figures and tables: `notebooks/results_visualisation.ipynb` (+ `.html`),
`reports/figures/viz_*.png`, `reports/tables/cross_capture_*.csv`.

## The matrix

AUROC, mean over the 1–5 s horizons, robust feature set, LightGBM. AUROC is the
right metric here because prevalence differs between captures. **0.5 is chance;
below 0.5 means the model is systematically wrong.**

| trained on / tested on -> | curated 6–8 Sept | XCAL 10 Sept | XCAL 12 Sept |
|---|---|---|---|
| **curated 6–8 Sept** | 0.83 *(own)* | 0.56 | 0.66 |
| **XCAL 10 Sept** | **0.36** | 0.84 *(own)* | **0.83** |
| **XCAL 12 Sept** | 0.57 | **0.82** | 0.77 *(own)* |

Three things fall out of it.

**1. Real -> real transfer is essentially free.** Train on 10 Sept, test on
12 Sept: AUROC 0.83, against 0.84 on its own held-out drives. The reverse: 0.82
against 0.77 — transfer is *better* than the source's own holdout. Two
independent drives, two days apart, different routes and cells, and the model
barely notices. That is a strong generalisation result and it is the one worth
building the paper on.

**2. The curated capture does not transfer to your real network.** Train on
curated, test on real: AUROC 0.56 and 0.66 — barely above chance, against 0.83
on its own drives.

**3. Train on real, test on curated: AUROC 0.36.** Well *below* chance. A model
that learned real LTE mobility is systematically wrong on the curated data — it
would score better with its predictions inverted. The GRU shows the same
pattern more mildly (0.53–0.63 everywhere off-diagonal).

## Why — and it is not that the file is fake

The curated file passes every physical check (see
`03-dataset-audit-DRIVETEST_LOGS_1.md`). The failure is in the *dynamics*.

Mean feature value one second before a handover, in standard deviations from
that capture's own baseline:

| feature | curated | XCAL 10 Sept | XCAL 12 Sept |
|---|---|---|---|
| serving RSRP | -0.88 | -0.04 | -0.26 |
| **serving RSRP slope** | **-0.25** | **+0.19** | **+0.26** |
| serving SINR | -0.57 | -0.89 | -0.98 |
| **serving-to-best-neighbour gap** | **-0.63** | **+0.12** | **+0.09** |
| neighbour-better streak | +0.40 | +0.03 | +0.13 |
| serving dwell | -0.50 | -0.61 | -0.61 |

Two features point the opposite way, and they are the two a handover predictor
leans on hardest.

In the curated capture a handover is preceded by a long clean decline: RSRP
falling, the best neighbour already ~6 dB ahead and ahead for many seconds. In
both real captures the serving cell is still marginally *stronger* at the moment
of the command, and its RSRP is momentarily *rising*.

**Caveat added 13 Sept:** the original reading of this table attributed the
difference to A3 configuration. The controlled within-campaign experiment
(doc 09) shows A3 regime does **not** produce this signature difference — the
same table computed across regimes inside the real captures separates by
0.2 dB/s against a 2.2 dB/s spread. The curated-vs-XCAL difference is real; its
cause is still open.

## What this means for the thesis

**The curated dataset cannot be the evidence base.** It is a valid textbook-A3
network; it is not the network you measured. Any result from it describes a
different mobility configuration, and the transfer matrix is the proof.

**It is also a genuinely publishable finding.** A predictor trained on one
capture scoring below chance on another, with a documented mechanism, is a
stronger contribution than another architecture comparison — and it lands
directly on the proposal's Gap 6 (limited independent real-world validation) and
Gap 7 (architecture-centred novelty).

**Real -> real transfer holding at 0.82–0.83 is the positive result.** It says
the approach works when the training and target networks are configured alike.

## Caveats to state in the write-up

- The real captures are small: 15 and 8 pseudo-drives, 290 and 174 handovers.
  Two drives is not a generalisation study; it is two points that agree.
- The label sources differ — curated uses serving-cell transitions, the XCAL
  captures use signalling-confirmed handovers. Some of the gap is definitional.
  It cannot explain AUROC 0.36.
- Only 29–33% of XCAL samples carry a neighbour measurement. The `robust`
  feature set (which drops the sparse neighbour features) gives the same
  picture, so this is not the cause, but it caps what the real captures can
  show.

## Next

1. **Re-plan the campaign around this.** 30+ drives on the real network, and
   the paper is about transfer across captures, with the curated set as a
   contrast case rather than the training set.
2. **Record the A3 parameters for every drive.** The signalling parser already
   extracts them.
3. **Rerun this stage after each new capture** — it is the fastest check that a
   new drive belongs in the same pool as the others.

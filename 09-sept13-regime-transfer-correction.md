# 13 September verification, corrected regime transfer, and what to collect next

Supersedes the hypothesis section of `08-thesis-frame-and-field-plan.md`. Two of
the five hypotheses in that document are now falsified by my own experiment, and
one of the "results already in hand" was misattributed. This doc records the
correction before anything gets written into the thesis.

## 1. The 13 September capture

| | |
|---|---|
| Samples | 3,605 rows, 1 Hz, 60 min (13:54–14:54) |
| Signalling | 28.8 MB, 5,010 measurement reports, 297 handover commands, 297 completions, 159 re-establishments |
| Authenticity audit | **CONSISTENT WITH MEASURED DATA** — every decisive check passes |
| Neighbour identity | 74.3% (best of the three captures) |
| Target-is-neighbour, top-3 | 69.7% (best of the three) |
| Drives after QC | 20 |
| A3 attribution | 100% of 297 handovers |
| Ping-pong rate | 26.3% (vs 42.5% on 12 Sept) |

It is the strongest capture so far. **But the export rate is still 1 Hz** — the
recommended change to 100–200 ms was not applied. See section 4; this is the
single highest-value fix available.

## 2. Four-domain cross-capture transfer

AUROC, LightGBM, full feature set, whole drives held out on both sides.

| train \ test | curated 6–8 Sep | XCAL 10 Sep | XCAL 12 Sep | XCAL 13 Sep |
|---|---|---|---|---|
| curated 6–8 Sep | **0.83** | 0.57 | 0.66 | 0.61 |
| XCAL 10 Sep | 0.35 | **0.83** | 0.82 | 0.81 |
| XCAL 12 Sep | 0.61 | 0.81 | **0.78** | 0.82 |
| XCAL 13 Sep | 0.58 | 0.82 | 0.83 | **0.84** |

The 3x3 real block is uniformly 0.81–0.84 — transfer between independent real
captures is essentially free. The curated row/column is the only anomaly, and it
is asymmetric: curated->real loses ~0.2 AUROC, real->curated collapses to **0.35**,
below chance.

## 3. Configuration-regime transfer — the corrected experiment

### The flaw I found and fixed

A3 regimes co-exist *inside* a single drive, because they follow the carrier.
My first cross-regime split therefore put the same drives on both sides of the
train/test boundary — precisely the leakage the rest of the pipeline forbids.
Fixed by holding out 30% of drives **globally** first, then intersecting every
evaluation (same-regime and cross-regime alike) with that held-out set. All
numbers below are from the leakage-free rerun. 761 handovers, 43 drives,
3 testable regimes (the +5 dB/640 ms profile exists only on 10 Sept and has too
few held-out rows to test).

### Result: configuration shift barely matters

Mean AUROC over all regime pairs and horizons:

| model | same regime | cross regime | paired delta (mean +/- sd over 12 pairs) |
|---|---|---|---|
| LightGBM | 0.828 | 0.814 | **+0.015 +/- 0.028** |
| GRU | 0.802 | 0.764 | +0.038 +/- 0.025 |

The LightGBM gap is within its own spread — not a usable effect. It is
concentrated entirely at the 5 s horizon (+0.056 and +0.073 on two of three
target regimes) and is zero or negative at 1 s.

### Result: A3 conditioning does not help

Adding the measured offset / hysteresis / TTT / carrier as model inputs:

| model | mean delta-AUROC | Wilcoxon p |
|---|---|---|
| LightGBM | -0.0006 | 0.57 |
| GRU | -0.020 | <0.001 |

No benefit for the tree model; a **significant harm** for the sequence model,
which overfits four near-constant columns.

### Result: the claimed mechanism is not a regime effect

Pre-handover serving-RSRP slope over the 5 s before each handover, by regime,
within the real campaign:

| regime | mean slope (dB/s) | sd | n |
|---|---|---|---|
| A3 +1 dB / 320 ms | -0.101 | 2.21 | 205 |
| A3 +5 dB / 640 ms | -0.088 | 2.41 | 85 |
| A3 -10 dB / 640 ms | -0.009 | 2.28 | 215 |
| A3 -15 dB / 160 ms | +0.103 | 2.19 | 233 |

Separation of 0.2 dB/s against a 2.2 dB/s within-regime spread. The
"opposite-sign pre-handover signature" recorded as R4 is a **curated-vs-XCAL**
difference, not a configuration-regime difference. R4 must be re-labelled.

### What survives

**H1 partially holds.** The aggressive -15 dB / 160 ms regime carries ~1.7x the
prevalence and the lowest AUPRC lift (7.16 vs 9.93–10.37 at 1 s). Difficulty
does vary with configuration — but through event density, not through a changed
radio signature, and it does not break transfer.

**H2 falsified** (for the tree model; marginal and long-horizon-only for the GRU).
**H3 falsified**, with the GRU result running the wrong way.
H4, H5 untouched by this experiment and still stand.

### Consequence for the thesis frame

The title and central question in `08-thesis-frame-and-field-plan.md` — built on
configuration-driven transfer failure — are not supported by the data. Two
honest options:

1. **Keep the configuration work as a negative result.** "Handover predictability
   is invariant to A3 control parameters within a network" is a real, cleanly
   controlled, publishable finding, and it directly contradicts the intuition
   the framing was built on. It needs a positive companion contribution.
2. **Move the headline to what the data actually shows.** The one large,
   reproducible failure in the whole study is the curated<->XCAL collapse to 0.35.
   That is a domain-shift result with teeth — but its *cause* is currently
   unidentified, and identifying it is the highest-value experiment left.

Option 2 is the stronger paper if the cause can be pinned down in the remaining
field time. Section 4 says how.

## 4. Which data most benefits the research — ranked

Ranked by expected effect on the thesis per hour of driving.

### 1. Raise the export rate (zero driving hours, largest single gain)
Still 1 Hz. At 1 Hz: sub-second horizons are unmeasurable, lead time resolves
only to +/-1 s, and 64–84% of inter-handover gaps are under 10 s, so the useful
prediction window is a handful of samples wide. Going to 100–200 ms multiplies
usable rows per minute by 5–10x **at no extra driving cost**, and opens the
0.25/0.5 s horizons — exactly where discrimination is strongest (AUROC 0.93 at
1 s vs 0.73 at 5 s). If only one thing changes before the next drive, this is it.

### 2. Re-drive the curated route with XCAL signalling on (~2 h)
This is the experiment that decides the thesis frame. The curated<->XCAL collapse
has two candidate causes and they are separable by one drive:
- **feature availability** — the curated capture has no signalling, so the
  neighbour block is absent and the model leans on different inputs; or
- **environment / network state** — genuinely different cells, carriers, load.

Drive the 6–8 Sept corridor with the current XCAL setup. If a model trained on
the new capture transfers to the curated data at ~0.8, the cause is
instrumentation; if it still collapses, the cause is environmental. Either answer
is a headline result. Nothing else available gives that much per hour.

### 3. More independent drives, short and repeated (rest of the time)
The evaluation unit is the drive, not the sample — cluster bootstrap CIs are set
by drive count, and there are only 43. 13 Sept produced 20 drives from 60
minutes; two more days at that rate roughly doubles the count and cuts CI widths
by ~30%. Rule: **10–15 minute loops, repeated, both directions**, logged with
start/end times. More loops beats longer loops.

### 4. A contrasting speed/environment regime (~2 h)
Every capture so far is dense urban at low speed. One arterial or highway loop
gives a mobility-shift axis, which — unlike configuration — is a plausible
source of real transfer failure and is a standard external-validity axis for
reviewers. Worth one dedicated session.

### 5. Time-of-day repetition on an already-driven route (~1 h)
Same geometry, different load. Cheap controlled contrast, free second shift axis.

### What NOT to spend time on
- **Chasing new A3 regimes.** Section 3 shows configuration shift is worth ~0.015
  AUROC. Deliberately hunting the +5 dB/640 ms profile to complete the 4x4
  matrix would tidy a table that has already answered its question.
- **A second operator SIM**, unless it costs nothing — it reintroduces every
  confound the within-campaign design removes.
- **Longer single sessions.** They add samples but few drives, and drives are the
  currency.

## 5. Artefacts
- `src/hoproj/data/config_regime.py` — A3 attribution (new)
- `src/hoproj/pipeline/stage07_regime_transfer.py` — leakage-free regime transfer (new)
- `src/hoproj/pipeline/stage06_cross_capture.py` — extended to 4 domains
- `reports/tables/config_regimes.{csv,md}`, `regime_transfer.{csv,md,tex}`,
  `cross_capture_*` refreshed

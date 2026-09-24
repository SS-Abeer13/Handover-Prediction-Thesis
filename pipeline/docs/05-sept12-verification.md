# 12 September capture — verification

Two new files: `test 12 sept.csv` (1,469 rows, 1 Hz, 24.5 min) and
`test 12 sept signalling.txt` (18.5 MB, 617k lines of decoded RRC).

**Headline: the signalling log clears three of the gate items the 10 Sept pilot
failed. The CSV alone still does not — the signalling is doing all the work.**

New code, all on your disk and tested:
`src/hoproj/data/signalling.py`, `configs/adapters/xcal_signalling.yaml`,
signalling-aware `ingest.py` and `stage00_field_dictionary.py`.
Reports in `pipeline/sept12/reports/`.

## Gate: 10 Sept vs 12 Sept

| task | 10 Sept | 12 Sept | why it changed |
|---|---|---|---|
| multi-horizon HO forecasting | supported | supported | — |
| **signalling-confirmed HO + target cell** | absent | **supported** | 176 `mobilityControlInfo` commands, all with `targetPhysCellId` |
| **HOF / RLF labels** | absent | **supported** | 64 RRC re-establishments with explicit causes |
| **candidate-neighbour ranking (RQ6)** | NOT supported | **degraded** | neighbours come from MeasurementReports, not the CSV — 33% grid coverage |
| A3 baseline with the network's own params | unknown | degraded | a3-offset, hysteresis, TTT all recoverable from `measConfig` |
| QoE regression (RTT / loss) | NOT supported | **still NOT supported** | RTT and packet-loss columns remain empty |

The CSV's `Best_N1..N3` columns are still 100% empty. Every neighbour value now
in the pipeline is parsed out of the UE's own MeasurementReports and projected
onto the 1 Hz grid (median report age 0.27 s, `mr_age_s` carried alongside so
staleness can be masked or modelled).

## What the signalling says about this network

This is the part worth a second look before the data is used for training.

- **176 handovers in 24.3 minutes** = 7.3/min.
- **Median gap between consecutive handovers: 2.6 s. 81% are under 10 s.**
- Ping-pong rate under our temporal definition: **41%** (vs 7.7% in the curated
  Sept 6–8 dataset).
- Handover interruption is near zero (median 0 ms, max 104 ms), so they complete —
  the UE is not failing, it is thrashing.
- The network's own A3 settings, read out of `measConfig`:

| a3-offset | hysteresis | TTT | reading |
|---|---|---|---|
| +1.0 dB | 1.0 dB | 320 ms | conventional |
| +5.0 dB | 2.0 dB | 640 ms | conservative |
| **-10.0 dB** | 2.0 dB | 640 ms | aggressive |
| **-15.0 dB** | 1.0 dB | 160 ms | very aggressive |

A negative A3 offset triggers a handover while the neighbour is still *worse*
than the serving cell. Combined with a 160 ms time-to-trigger, that is a
plausible mechanical explanation for the 2.6 s handover spacing.

Two things to settle before this becomes training data:

1. Are some of these intra-eNB or SCell reconfigurations rather than true
   inter-cell handovers? A 0 ms interruption at 7.3/min is unusual.
2. Was the UE stationary or slow-moving in a dense multi-carrier pocket? GPS is
   88% populated, so this is checkable.

Either way it is a finding: **the operator is running multiple A3 profiles
simultaneously, including two aggressive ones.** That belongs in the paper — it
is exactly the parameter trade-off the literature (Saad et al. [5]) describes,
observed live.

Also: 62% of MeasurementReports carry **zero** neighbours (A1/A2 serving-only
events). Only 1,809 of 4,761 report a neighbour. That, not the parser, is why
grid coverage is 33%.

## Micro-pilot (R4) — the pipeline passes, the data is too small

Whole pipeline end to end on this one drive: ingest -> signalling merge ->
segmentation (12 pseudo-drives at 120 s) -> QC (12/13 pass) -> labels -> features
(151) -> windows -> four models. **R4 gate cleared: a raw capture converts
automatically into a labelled sequence dataset.**

The numbers are another matter. Prevalence is 8.6/16.1/22.6/31.4%.

| model | 1 s | 2 s | 3 s | 5 s |
|---|---|---|---|---|
| prevalence floor | 0.086 | 0.161 | 0.226 | 0.314 |
| LightGBM | 0.464 | 0.422 | 0.411 | 0.421 |
| logreg | 0.181 | 0.218 | 0.282 | 0.261 |
| rule | 0.087 | 0.201 | 0.265 | 0.343 |
| **GRU** | **0.089** | **0.147** | **0.203** | **0.272** |

**The GRU is at or below the prevalence floor at every horizon.** With six
training drives and 24 minutes of data that is the expected outcome, not a
defect — it is the same overfitting the Sept 6–8 leakage study predicted
(train loss 0.22, validation loss 4.07 by epoch 24). Only LightGBM clears the
floor, and only by 2.6x.

**Do not read any model conclusion from this capture.** It verifies plumbing,
not performance. False-alarm rates of 80–250/hour say the same thing.

## What this changes for the thesis

1. **RQ6 is back on the table**, conditional on neighbour coverage. At 33% it is
   thin; 60%+ would make candidate ranking properly testable. Ask the operator
   or reconfigure logging for periodic rather than purely event-triggered
   reporting.
2. **HOF/RLF moves from exploratory toward primary** if the re-establishment rate
   holds — 64 in 24 min is a lot of events.
3. **The A3 rule baseline stops being a guess.** We can now parameterise it with
   the network's actual offset, hysteresis and TTT, which makes "the learned
   model beats the deployed policy" a claim with a real comparator.
4. **QoE is still the gap.** RTT and packet loss are empty in both XCAL captures.
   Client-side active tests (iPerf / ping to a controlled endpoint) during the
   drive are the fix, as section 10.2 of the proposal anticipated.

## Next

- Confirm whether the 2.6 s handovers are genuine inter-cell events.
- Re-log with neighbour reporting turned up, then re-run
  `stage00_field_dictionary --adapter xcal_signalling` and check coverage.
- Add active QoE tests to the drive protocol.
- Collect enough signalling drives (30+) to make the signalling path a training
  set rather than a pilot.

# What to do next — data collection plan

Written after parsing both signalling logs (10 Sept, 45.7 min; 12 Sept, 24.3 min).
Plain-language version of the decisions.

## The two drives agree with each other

| | 10 Sept | 12 Sept |
|---|---|---|
| duration | 45.7 min | 24.3 min |
| handovers (confirmed by network messages) | 307 | 176 |
| rate | 6.7/min | 7.3/min |
| median time between handovers | 3.6 s | 2.6 s |
| handovers less than 10 s apart | 79% | 81% |
| immediate bounce-back (A->B->A) | 23% | 47% |
| dropped-connection recoveries | 113 | 64 |
| neighbour info available on the 1-second grid | 29% | 33% |

Same pattern twice, two days apart. Real network behaviour, not a logging artefact.

## Why it happens

The network tells the phone when to switch cells using a rule called **A3**:
*switch when a neighbouring cell is better than the current one by X dB, and
stays better for Y milliseconds.* X is the "offset", Y is the "time-to-trigger".
The logs contain the values the operator is actually using:

| offset | time-to-trigger | meaning |
|---|---|---|
| +1 to +5 dB | 320–640 ms | normal |
| **-10 dB** | 640 ms | switch even when the neighbour is *worse* |
| **-15 dB** | 160 ms | switch almost immediately, to a much worse cell |

Negative offsets plus a 160 ms trigger explain the 2.6-second spacing.

## Four problems, in priority order

### 1. The 1-second sampling rate is too slow — blocking

Only **44% (10 Sept) and 58% (12 Sept)** of the handovers confirmed in the
signalling log show up as a cell change in the CSV within 2 seconds. Handovers
2.6 s apart cannot be resolved by a 1 Hz grid; pairs collapse into one sample
and bounce-backs vanish entirely.

**Action:** raise the XCAL export rate to 100–200 ms, then re-check the match
rate with `stage00_field_dictionary`.

### 2. Neighbour measurements are too sparse — blocking RQ6

62–63% of the phone's measurement reports contain **no neighbour at all**. Only
~30% of grid samples end up with a neighbour value, so the serving-to-neighbour
gap — the strongest single predictor — is missing on 70% of samples.

**Action:** enable periodic measurement reporting alongside the event-triggered
ones. Target 60%+ coverage.

### 3. No service-quality data at all — blocking RQ5's QoE half

Round-trip-time and packet-loss columns are empty in both captures. Throughput
appears on under 1% of rows.

**Action:** run continuous active tests during the drive — a ping to a fixed
server for latency, an iPerf or large HTTP download for throughput. This is a
second program on the laptop; nothing about the phone or XCAL changes.

### 4. Volume — blocking everything

Two drives, ~70 minutes total. The micro-pilot put the GRU *below* the prevalence
floor at every horizon, which is what 6 training drives buys.

**Action:** 30+ drives with signalling before any model claim.

## A framing opportunity

An 80% rate of handovers under 10 seconds apart, with the operator's own
aggressive A3 settings visible in the log, is unusual and well-documented here.
Strong angle: *predicting which handovers are unnecessary, in a network
demonstrably configured to over-handover.* Uses the ping-pong labels the pipeline
already produces; needs no new capability, only more drives.

## Sequence

```
now --> fix logging rate + neighbour reporting   (one XCAL config session)
    --> add ping/iPerf to the drive protocol      (one laptop script)
    --> one validation drive, re-run the gate     (30 min, checks 1-3 worked)
    --> freeze the protocol                       (R2)
    --> 30+ drives across 3-4 routes              (the real campaign)
    --> retrain, then open the locked route
```

Do not skip the validation drive. It costs 30 minutes and protects the campaign
from repeating a logging mistake across 30 drives.

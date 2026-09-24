# Thesis frame + field plan (revised 13 Sept)

> **Revision notice.** The original version of this document (12 Sept) built the
> thesis on configuration-driven transfer failure. The leakage-free rerun of that
> experiment on 13 Sept **falsified H2 and H3** and showed R4 was misattributed.
> See `09-sept13-regime-transfer-correction.md` for the numbers. This version
> keeps what survived and marks what did not.

Written against two hard constraints: two days of drive testing left, and the
finding that the curated dataset does not describe the network you measured.

## What is established

Every handover in all three XCAL captures can be traced to the exact A3 rule
that triggered it. The chain is complete in the signalling:

```
measurementReport.measId
   -> measIdToAddModList:  measId -> measObjectId + reportConfigId
   -> reportConfigToAddModList:  reportConfigId -> A3 offset / hysteresis / TTT
   -> measObjectId -> carrier frequency
```

**100% attribution, 761 handovers, 43 drives, 3 captures.** Grameenphone runs
four A3 profiles concurrently across its carriers:

| A3 offset | hysteresis | TTT | 10 Sep | 12 Sep | 13 Sep | total |
|---|---|---|---|---|---|---|
| -15.0 dB | 1.0 dB | 160 ms | 124 | 54 | 76 | **254** |
| -10.0 dB | 2.0 dB | 640 ms | 70 | 50 | 103 | **223** |
| +1.0 dB | 1.0 dB | 320 ms | 19 | 72 | 118 | **209** |
| +5.0 dB | 2.0 dB | 640 ms | 92 | — | — | **92** |

This instrumentation stands regardless of what the transfer experiment showed —
it is a reusable contribution on its own.

## Results in hand

| # | Result | Status |
|---|---|---|
| R1 | Every handover attributable to its A3 rule; four profiles concurrent | **holds** |
| R2 | Real->real transfer holds: AUROC 0.81–0.84 across three captures | **holds** |
| R3 | Curated<->XCAL transfer fails and inverts: 0.35 (real->curated) | **holds — but cause unidentified** |
| R4 | Opposite-sign pre-handover RSRP signature | **re-labelled**: a curated-vs-XCAL difference, *not* a regime difference |
| R5 | Leakage is architecture-dependent: GRU +109% AUPRC vs LightGBM +12% | **holds** |
| R6 | Calibration does not transfer: ECE 0.17–0.28 external vs ~0.10 in-domain | **holds** |
| R7 | A published-style curated dataset failed physical authenticity checks | **holds** |
| R8 | Handover predictability is **invariant** to A3 control parameters within a network (delta AUROC 0.015 +/- 0.028); conditioning on A3 parameters gives no gain and harms sequence models | **new — negative result** |

## Hypotheses, after the correction

- **H1** *(partially supported)* Difficulty varies with configuration: the
  aggressive -15 dB/160 ms regime has ~1.7x the prevalence and the lowest AUPRC
  lift (7.16 vs 9.93–10.37 at 1 s). The effect is event density, not a changed
  radio signature.
- ~~**H2** Cross-regime transfer degrades with configuration distance.~~
  **Falsified.** LightGBM delta = +0.015 +/- 0.028 AUROC; GRU +0.038, long-horizon only.
- ~~**H3** Conditioning on measured A3 parameters recovers the loss.~~
  **Falsified.** LightGBM -0.0006 (p = 0.57); GRU -0.020 (p < 0.001, harmful).
- **H4** *(stands, untested by this experiment)* Calibration degrades faster than
  discrimination under shift.
- **H5** *(stands, confirmed)* Random-row splitting inflates sequence models far
  more than snapshot models.
- **H6** *(new, and the open question)* The curated<->XCAL collapse is caused by
  **feature availability** (no signalling -> no neighbour block) rather than by
  environment. Decidable with one drive — see the field plan.

## Two candidate frames

1. **Invariance frame.** "Handover predictability is invariant to A3 control
   parameters within a network, but collapses across capture instrumentation."
   Cleanly controlled; the negative result contradicts an intuitive prior; needs
   the positive companion from H6.
2. **Instrumentation frame.** Headline the 0.35 collapse and identify its cause.
   Stronger paper, contingent on the H6 drive resolving it.

Both require the H6 drive. Decide after it.

Venue fit unchanged: IEEE TMLCN or IEEE OJ-COMS.

## The two-day field plan (revised)

Priority order, by expected thesis value per driving hour. Full reasoning in
`09-sept13-regime-transfer-correction.md` section 4.

### Before driving — non-negotiable, zero driving cost

| # | Change | Why |
|---|---|---|
| 1 | XCAL export rate 1 s -> **100–200 ms** | Still 1 Hz on 13 Sept. Sub-second horizons are unmeasurable; lead time resolves only to +/-1 s; 64–84% of inter-handover gaps are under 10 s. 5–10x usable rows per minute for free. |
| 2 | Enable **periodic** measurement reporting alongside event-triggered | Neighbour grid coverage is 28% on 13 Sept. Target 60%+. |
| 3 | Verify signalling export on for every session | It is what makes R1 possible. |

Then a 20-minute validation drive and `stage00_field_dictionary --adapter
xcal_signalling`. If neighbour coverage has not moved above 50%, fix reporting
before spending day two.

### Day 1

- **The H6 drive (~2 h).** Re-drive the 6–8 Sept curated corridor with the
  current XCAL setup and signalling on. This decides the thesis frame.
- **Repeat short loops (rest of the day).** 10–15 min loops, both directions,
  each repeated >=4 times. The evaluation unit is the drive: 43 exist, and
  cluster-bootstrap CI width is set by that count. 13 Sept gave 20 drives from
  60 minutes; match that rate.

### Day 2

- **One arterial / high-speed loop (~2 h).** Every capture so far is dense urban
  at low speed. A mobility-shift axis is a plausible real source of transfer
  failure and a standard external-validity axis.
- **Time-of-day repetition (~1 h)** on an already-driven route — same geometry,
  different load.
- Remaining time: more short repeated loops.

### Dropped

- **Chasing new A3 regimes / completing the 4x4 regime matrix.** R8 has already
  answered that question.
- **Second-operator SIM**, unless free — it reintroduces every confound the
  within-campaign design removes.
- **Longer single sessions.** Samples are cheap; independent drives are not.
- QoE as a primary task; architecture comparison as a contribution.

## The honest risk

Small-N. 43 drives, 761 handovers. Handle it by reporting drive-level bootstrap
intervals everywhere (implemented), never claiming a regime *ranking*, presenting
contrasts rather than population estimates, and stating sample size in the
abstract.

## Assumptions

1. The XCAL export rate and reporting configuration can be changed.
2. ~4–6 driving hours per day.
3. One SIM/operator, one XCAL-capable UE.

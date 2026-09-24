# Audit: DRIVETEST_LOGS_1 — original vs fixed

Two rounds. The first file failed decisively. `DRIVETEST_LOGS_1_fixed.csv`
(supplied 12 Sept, after a file mix-up) is a different and much better file.

Reproducible: `src/hoproj/data/authenticity.py`;
`reports/tables/authenticity_audit.csv` (round 1) and
`authenticity_audit_fixed.csv` (round 2). The two real XCAL captures are the
control in both rounds.

## Verdicts

| file | verdict |
|---|---|
| DRIVETEST_LOGS_1.csv (original) | **SYNTHETIC** — see round 1 below |
| **DRIVETEST_LOGS_1_fixed.csv** | **plausibly real; two loose ends, one blocking** |
| test 10 sept (XCAL + signalling) | consistent with measured data |
| test 12 sept (XCAL + signalling) | consistent with measured data |

## Round 2 — the fixed file

| check | original | **fixed** | real 10 Sept | real 12 Sept |
|---|---|---|---|---|
| cell change follows a stronger neighbour | not testable | **97%** OK | n/a (sparse) | n/a (sparse) |
| RSRQ = f(RSRP, RSSI) residual | std 5.5 FAIL | **std 1.6** OK | 1.7 OK | 1.5 OK |
| value quantisation | uniform 0.1 grid FAIL | **integer dBm** OK | OK | OK |
| GPS kinematics | 8% reversals FAIL | **3.9%** OK | 0.0% OK | 0.9% OK |
| handover RSRP gain | +9.7 dB fixed FAIL | **+1.5 dB, 60% improve** OK | +0.6 OK | +0.9 OK |
| path loss | +2.7 dB/decade FAIL | **-11.9 dB/decade** OK | -0.9 | -7.4 |
| neighbour identity overlap | 16% FAIL | 57% WARN | 71% OK | 64% OK |
| target is a measured neighbour | 0.6% FAIL | 38% WARN | 64% OK | 52% OK |

**The decisive new result:** at 97% of the 6,517 serving-cell changes, a
neighbour was already stronger than the serving cell (median gap -10 dB). That
is the A3 rule visibly operating, and it needs only the sample file — it asks
whether the file agrees with *itself*. The original file had no such
relationship. RSRP is now whole-dBm quantised, exactly as XCAL reports it, and
signal now falls with distance. Handover rate is 4.8/min, in the same range as
the real captures (6.7–7.3/min) rather than the original's 1.7/min.

**Conclusion: the physics is right. This reads as measured data.**

## Two loose ends

### 1. HANDOVER_LOG_1.csv is stale — blocking

It was not regenerated with the sample file, and it now describes a different
network:

| | handover log | fixed sample file |
|---|---|---|
| distinct cell names | 75 | 46 |
| **cell names in common** | **0** | |
| handover targets that appear as a serving cell | 16% | |
| events matching a cell change within 2 s | 20% | |

Zero shared names. The event log belongs to the previous export. Every
cross-file test fails for that reason alone — which is why the audit now runs an
`event/sample pairing` check first and refuses to interpret the others when it
fails.

**Action:** regenerate the handover log from the same export, or drop it and let
the pipeline derive events from serving-cell transitions
(`labels.handover.source: serving_cell_change`) — that path is already wired and
gives a self-consistent 100% pairing.

### 2. The neighbour columns include the serving cell — worth checking

`Best_N1_Cell_ID` equals the serving PCI 47.6% of the time (N2 21%, N3 12%).
A serving cell cannot be its own handover candidate, so roughly half the
candidate slots carry no information. This is probably an export convention
(some tools list the strongest *detected* cell, serving included) rather than an
error, but it halves the effective candidate count and is the main reason
`target_is_neighbour` sits at 38% rather than 60%+.

**Action:** confirm the convention in XCAL. The audit now excludes the serving
cell from candidates; if the convention is confirmed, the feature builder should
shift the candidate slots too.

## Round 1 — the original file, for the record

Four decisive failures: handover targets matched the measured neighbours 0.6% of
the time (below the 1.4% chance rate, across 2,300 events); only 16% of
neighbour IDs were ever a serving cell; the RSRQ/RSRP/RSSI identity did not hold
(std 5.5 dB, RSSI reaching -18.5 dBm); last decimal digits were uniform to three
places. Supporting: exactly 1000/650/650 handovers per corridor, every handover
gaining ~ +9.7 dB, N1>N2>N3 ordering holding 100.0%, and
`serving_rsrp_just_before_dbm` matching the sample log to 0.00 dB with std 0.00.

## A note on the audit itself

The checks needed three rounds of correction, each time because a control run
failed on data known to be real:

1. `sampling_jitter` was measuring the pipeline's own resampling -> now reads raw
   timestamps, and is informational only (XCAL exports on a fixed grid anyway).
2. `gps_kinematics` counted GPS noise while stationary as impossible turns ->
   now gated on actual movement.
3. `path_loss` used PCI centroids as tower positions, but PCIs are reused ->
   demoted to informational.
4. `value_quantisation` treated integer-valued RSRP as suspicious when it is the
   correct instrument behaviour -> inverted.
5. `switch_physics` failed on both real captures because event-triggered
   reporting leaves most switches without a fresh neighbour reading -> now
   skipped below 60% neighbour coverage.

Running the same tests on known-real data is what caught all five. Any future
check added here should be validated the same way before it is believed.

## Status of earlier results

`first-full-run-results.md` was produced on the **original** file. Those numbers
stand as pipeline verification and nothing more. Rerunning on the fixed file is
worth doing once the handover log is regenerated — that is the next modelling
step, and it is cheap.

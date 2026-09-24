# Training pipeline — decisions log (v1)

Built from the proposal *Uncertainty-Aware Multi-Horizon LTE Handover and QoE
Forecasting*. Code home: `D:\Handover Thesis\pipeline`.

## Data found

| File | Rows | Role |
|---|---|---|
| `DRIVETEST_LOGS_1.csv` | 81,141 @ 1 Hz | main modelling capture (3 corridor sessions, 6–8 Sep 2026) |
| `HANDOVER_LOG_1.csv` | 2,300 events | handover labels, with corridor names |
| `test 10 sept-M1.csv` | 2,756 rows | raw XCAL wide export — the R0 pilot |

Curated capture is fully populated: serving RSRP/RSRQ/RSSI/SINR/CQI, three best
neighbours with cell IDs, throughput, RTT, packet loss. 75 serving cells, 723 km,
22.5 h, 7.7 % ping-pong.

## Decisions that need your sign-off

**1. Drives are derived geometrically, not given.** The capture is three long
continuous sessions — one group per corridor, which makes grouped CV and
trip-level bootstrap impossible. Each session is actually ~16–24 repeated
traversals. The pipeline projects GPS onto the corridor's principal axis and cuts
at direction reversals, giving **117 pseudo-drives** (median 696 s, 5.3 km), each
tagged with route and direction. All splits, bootstraps and calibration sets use
these as the unit. This is the single most consequential choice in the build.

**2. The 0.5 s horizon is not measurable at 1 Hz.** On a 1 s grid no event can
fall in (t, t+0.5], so it would silently produce an all-negative target. Horizons
are now **1, 2, 3, 5 s**, and the code drops any horizon below the sample period
with a loud warning. 0.5 s comes back only with a sub-second XCAL export.

**3. Locked external route: `kuril_badda_rampura_malibagh`.** Chosen as the
highest-speed, lowest-HO-density corridor — the hardest transfer. Development
runs on the other two. The external stage **refuses to run** without a freeze
manifest recording the config fingerprint, model, calibrator and abstention
thresholds; if the fingerprint later changes, the report says so.

**4. Four-way development split**, not three: train (42 drives) / val (14) /
calib (14) / test (14). Early stopping and operating thresholds use `val`;
calibration, conformal and abstention use `calib`; `test` is untouched until
reporting. The proposal implied three; separating val from test matters more here
than the extra data.

**5. Your XCAL pilot cannot yet support two of the proposal's tasks.** In
`test 10 sept-M1.csv` the Best_N1–N3 neighbour columns, RTT and packet-loss
columns are present but **entirely empty**; application throughput is populated in
0.04 % of rows; RRC state in 3 %. So candidate-neighbour ranking and QoE
regression are *not supported* by that logging configuration. Handover forecasting
and mobility features are fine. `stage00_field_dictionary` produces this verdict
table automatically — run it on every new capture before designing anything, and
fix the XCAL logging profile before the main campaign.

**6. Conformal uses plain split conformal over whole calibration drives**, not
score-averaging within drives (which under-covers badly: 0.78 against a 0.90
target). Temporal dependence is surfaced instead by reporting per-drive coverage
spread. Verified coverage 0.905 at alpha = 0.10.

## Verification run (short training budget, CPU)

Grouped-drive condition, topology-agnostic regime, RF+mobility+history+QoE:

| model | AUPRC @2 s | AUPRC @5 s | event detection @2 s | median lead | FA/hour |
|---|---|---|---|---|---|
| A3-style rule | 0.343 | 0.548 | 0.35 | 2 s | 27.3 |
| LightGBM | 0.567 | 0.799 | 0.72 | 2 s | 37.0 |
| GRU | 0.576 | 0.806 | 0.69 | 2 s | 6.3 |
| TCN | 0.570 | 0.799 | 0.72 | 2 s | 7.8 |
| Transformer | 0.571 | 0.808 | 0.70 | 2 s | 10.1 |

Numbers are from 3–4 epoch runs on the file later found to be synthetic; treat as
wiring evidence only. See docs 03 and 04.

## What to run next

```
make prepare          # R7-R10
make experiments      # main, leakage, ablations, multi-task
make uncertainty      # R14
make freeze && make external    # R15, only when the protocol is final
make report
```

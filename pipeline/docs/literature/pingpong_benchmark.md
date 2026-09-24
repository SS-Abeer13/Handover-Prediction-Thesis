## Ping-pong rate, defined comparably to the literature

Definition used here and by Ghoshal et al. (2025): for consecutive handovers
A→B then B→C, the second is a ping-pong if C = A and it occurs within a return
window. **Denominator = handovers.** Stating the window and the denominator
matters: Amirova et al. (2026) report 0.13% because their denominator is
measurement records, not handovers — two orders of magnitude apart.

### Sensitivity to the return window (pooled, n = 759)

| window | 1 s | 2 s | 3 s | 5 s | 10 s | 15 s | 20 s | 30 s |
|---|---|---|---|---|---|---|---|---|
| ping-pong rate | 0.051 | 0.142 | 0.183 | 0.237 | 0.281 | **0.294** | 0.303 | 0.314 |

The rate saturates above ~10 s, so the headline figure is not an artefact of
the window choice.

### Against the only comparable large-scale measurement

At Ghoshal et al.'s 15 s window and per-handover denominator:

| network | ping-pong rate | A3 offset + hysteresis | TTT |
|---|---|---|---|
| AT&T (US) | 15–16% | +8 dB | 640 ms |
| T-Mobile (US) | 15–16% | +8 / +10 dB | 640 / 320 ms |
| Verizon (US) | 25% | +6 / +8 dB | **256 ms** |
| **This network, 10 Sept** | **22.9%** | −15 / −10 / +1 / +5 dB | 160 / 320 / 640 ms |
| **This network, 13 Sept** | **27.3%** | " | " |
| **This network, 12 Sept** | **43.7%** | " | " |
| **This network, pooled** | **29.4%** | " | " |

Two contrasts stand out and both are verifiable from the signalling:

1. **This operator runs negative A3 offsets** (−15 and −10 dB), meaning a
   handover is triggered while the neighbour is still *weaker* than the serving
   cell. All three US operators run positive combined offsets of +6 to +10 dB.
2. **Its shortest time-to-trigger is 160 ms**, below Verizon's 256 ms — and
   Verizon's 256 ms is the mechanism Ghoshal et al. give for its 25% rate, the
   highest they measured.

So a pooled 29.4% is high but coherent: it exceeds the worst US operator on a
configuration that is more aggressive than that operator's on both axes.

### But the within-network mechanism is not that simple

Ping-pong at 15 s, broken down by the A3 profile that fired the handover:

| A3 offset | TTT | n | ping-pong @15 s |
|---|---|---|---|
| −15 dB | 160 ms | 246 | 0.280 |
| −10 dB | 640 ms | 218 | **0.339** |
| +1 dB | 320 ms | 207 | 0.290 |
| +5 dB | 640 ms | 88 | 0.227 |

The most aggressive profile is **not** the one with the most ping-pong. The
short-TTT mechanism that explains the cross-operator contrast does not explain
the within-network variation, which is consistent with this project's earlier
finding that predictability is invariant to the A3 regime.

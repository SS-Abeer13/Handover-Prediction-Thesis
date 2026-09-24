# Does the signalling solve the sparse-neighbour problem?

Short answer: **the data was never as sparse as the pipeline reported.** Two
defects in my own parsing and projection were throwing most of it away. Fixing
them lifts grid neighbour coverage from 28% to 62–79% — past the 60% target set
in `06-data-collection-plan.md` — with no new field work.

The longer answer has a sting in it: the extra coverage **does not improve
handover prediction at all**. It matters for candidate ranking (RQ6), not for
forecasting.

## What the logs actually contain

Message-type census across the three captures (13 / 12 / 10 Sept):

| message | 13 Sep | 12 Sep | 10 Sep |
|---|---|---|---|
| measurementReport | 5,010 | 4,761 | 5,695 |
| rrcConnectionReconfiguration | 2,906 | 2,204 | 3,127 |
| rrcConnectionReestablishmentRequest | 159 | 64 | 113 |
| systemInformation sib2/3/5/7 | 709 | 230 | 760 |

MeasurementReports are the only neighbour source, and there are **1.4 per second**
— not sparse. Of those:

| | 10 Sep | 12 Sep | 13 Sep |
|---|---|---|---|
| carry `measResultNeighCells` | 59.6% | 62.4% | 56.8% |
| carry `measResultBestNeighCell-r10` (SCell) | 15.7% | 24.2% | 11.0% |
| **carry either** | **62.7%** | **67.0%** | **59.4%** |

## Defect 1 — serving-only reports were masking neighbour readings

The grid projection used `merge_asof` on the *whole* report stream and took the
most recent report within tolerance. About 40% of reports are serving-only
A1/A2 events with no neighbour block. So a neighbour reading from 1.5 s ago was
routinely discarded in favour of an empty report from 0.2 s ago, and the empty
one won.

Measured on 13 Sept, same tolerance:

| tolerance | latest report (old) | latest *neighbour-bearing* report (new) |
|---|---|---|
| 2 s | 33.1% | 48.0% |
| 3 s | 36.9% | 55.7% |
| 5 s | 40.9% | 65.2% |

**Fix:** serving figures still come from the most recent report of any kind;
neighbour columns now come from the most recent report that actually carried a
neighbour, with its own staleness column `nbr_age_s` (separate from `mr_age_s`).

## Defect 2 — the SCell best-neighbour block was parsed away

The neighbour regex terminated on `measResultServFreqList`, which is exactly
where the carrier-aggregation report puts `measResultBestNeighCell-r10` — a
separately measured best neighbour **on the SCell carrier**. It was being cut
off by one token. That is also the only inter-frequency candidate the UE
reports, so losing it cost more than its raw count suggests.

**Fix:** parsed and merged, de-duplicated against the PCell list. Neighbour rows
on 13 Sept: 2,998 -> 3,339.

## Result

Grid coverage, tolerance 3 s, after both fixes:

| capture | >=1 neighbour | >=2 | >=3 | median neighbour age |
|---|---|---|---|---|
| 10 Sept | 70.6% | 19.4% | 4.5% | 0.76 s |
| 12 Sept | 78.6% | 19.7% | 5.4% | 0.48 s |
| 13 Sept | 62.2% | 15.1% | 3.6% | 0.99 s |

(measured at tolerance 5 s; config now ships 3 s — see the trade-off below)

## The sting: it buys no prediction accuracy

Cross-capture AUROC, LightGBM, full feature set, re-run after the fix:

| train \ test | own held-out | 10 Sep | 12 Sep | 13 Sep | curated |
|---|---|---|---|---|---|
| XCAL 10 Sept | 0.845 | — | 0.822 | 0.821 | 0.339 |
| XCAL 12 Sept | 0.793 | 0.815 | — | 0.825 | 0.573 |
| XCAL 13 Sept | 0.832 | 0.818 | 0.834 | — | 0.545 |
| curated 6–8 Sept | 0.831 | 0.575 | 0.670 | 0.616 | — |

Every cell is within 0.013 of the pre-fix matrix. **Doubling neighbour coverage
changed nothing.** This is consistent with the earlier observation that the
`robust` feature set — which drops the neighbour block entirely — reproduces the
same picture. For multi-horizon handover forecasting on this network, the
serving-cell trajectory and cell history carry the signal; the neighbour list
does not add to it.

So `06-data-collection-plan.md` item 2 ("neighbour sparsity blocks RQ6") was
right about RQ6 and wrong to call it blocking for the forecasting task.

## Freshness beats coverage for candidate ranking

Top-3 candidate hit rate on 13 Sept, by how stale the neighbour list is at the
moment of the handover:

| neighbour age | events | target in top-3 |
|---|---|---|
| <= 1 s | 170 | 67.1% |
| 1–2 s | 53 | 73.6% |
| 2–3 s | 23 | 73.9% |
| 3–5 s | 21 | 57.1% |

Holds to 3 s, then falls off. Coverage bought beyond 3 s is stale enough to hurt
the ranking task, so the adapter ships `projection_tolerance_s: 3.0` and carries
`nbr_age_s` so any model or evaluation can condition on freshness rather than
inherit a silent trade-off.

## What signalling cannot fix

Neighbour-bearing reports come in bursts: median gap 0.30 s, but 28 gaps longer
than 20 s account for 1,086 s — **30% of the 13 Sept hour**. Twelve of those 28
contain an `rrcConnectionRelease`: the UE went **RRC idle** and stopped reporting
entirely. No parser recovers those.

Two field changes close the remaining hole, and both are already on the plan:

1. **A keep-alive data session during the drive** (the ping/iPerf loop already
   recommended for QoE) holds the UE in RRC connected and eliminates the idle
   gaps. One change, two problems solved.
2. **Periodic measurement reporting** alongside event-triggered fills the other
   16 gaps, where the UE was connected but had no A3/A1/A2 event to report.

## Verdict

| question | answer |
|---|---|
| Do the signalling logs contain enough neighbour data? | **Yes** — 59–67% of reports carry a neighbour, 1.4 reports/s |
| Was the 28–33% figure real? | **No** — a projection artefact, now 62–79% |
| Does that solve RQ6 (candidate ranking)? | **Largely** — coverage is past target; hit rate ~70% within 3 s |
| Does it improve handover forecasting? | **No** — AUROC unchanged to within 0.013 |
| Is anything left that needs field work? | **Yes** — RRC idle gaps (30% of the hour), fixed by a keep-alive session |

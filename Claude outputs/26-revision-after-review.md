# Revision after the 17 September review — what changed and why

**Status:** all experiments re-run; revised manuscript, response letter and verification report
produced on 18 September 2026. The reviewed draft is kept unchanged as
`Docs/Handover_Thesis_Manuscript_Draft.docx`; the revision is
`Docs/Handover_Thesis_Manuscript_Revised.docx`.

## The decision that drove everything else

The 1 Hz XCAL export row stamped *t* describes the second that **follows** its timestamp. Audited
against the RRC command stream: in 75.9 % of handovers (isolated handovers:
74.6 %) the row stamped inside the second before the handover command already shows
the post-handover serving cell, against a background of 12.1 % three rows earlier.
So the v1 features contained the answer.

Every export feature is now lagged one row. Headline effect, same model, same folds:

| 1 s horizon | v1 (unlagged) | v2 (lagged) |
|---|---|---|
| AUPRC | 0.600 | **0.179** (floor 6.8 %, 2.6x) |
| AUROC | 0.911 | **0.777** |
| dwell alone (AUROC) | 0.873 | **0.664** |

At 5 s: AUPRC 0.475 (1.8x). Deployed A3 rule at 1 s: AUPRC
0.116.

## Other substantive changes

1. **Unit of independence.** Each campaign is one continuous session, so there are four independent
   units, not 57. Leave-one-campaign-out is the primary protocol. Protocol ladder at 1 s (primary
   model): LOCO 0.179 → blocked+purge → random 180 s blocks (+13 %)
   → random rows (+48 %).
2. **Configuration timeline v2.** The parser now applies removal lists (15,100
   measId removals), the inter-frequency measId swap (5.5.6.1, 187 occurrences) and
   configuration release on leaving RRC_CONNECTED (56). 17.7 %
   of reports change event type.
3. **Offsets, weighted by handovers.** 75 % of A3-triggered handovers fire under
   a **positive** offset (+1 dB / 320 ms / 1 dB hysteresis). The negative-offset configurations are
   long-interval re-reporting configurations. The v1 contribution claim is reversed.
4. **A3 conversion per trigger episode.** 8,136 reports → 2,361 episodes
   (3.4 reports each). Declined: 30 % per episode
   vs 63 % per report; the dominant mobility profile is declined on
   2.3 % of episodes.
5. **Re-establishments.** 341 total: 321 reconfigurationFailure,
   17 otherFailure, 3 handoverFailure. Not radio link failures
   during mobility. Treated as a competing event; censoring them moves the 1 s lift by
   +0.03x.
6. **Coherence.** Independent heads violate ordering on 40.2 % of rows; a cumulative-max
   projection also reaches zero, so the hazard argument now rests on calibration
   (0.012 vs 0.047 at 1 s) and on one fit instead of five.
7. **Conformal risk control.** Reported in both regimes: exchangeable chunk pool (realised
   0.168 at α = 0.20, alarm rate 47 %) and cross-campaign
   (realised 0.153, bound respected in 83 % of
   12 rotations).
8. **External check.** Same operator/city/instrument/institution — relabelled "independent collection
   on the same network". Both domains rebuilt from L3 signalling: ours→public AUROC
   0.760, public→public 0.711, ours→ours
   0.730.

## What the paper now claims

A leakage-audited, signalling-grounded forecasting framework, with the timestamp-alignment audit as
the headline methodological contribution, a modest but real predictive signal
(2.6x at 1 s, 1.8x at 5 s), and corrected characterisations of the deployed
network. Title: *Leakage-Audited Multi-Horizon Handover Forecasting from LTE Drive-Test Signalling*.

## What still needs the user

- Native-rate (message-rate) re-export of the four captures — would settle the row-time semantics and
  allow sub-second horizons.
- More independent sessions (8–10) — four units cannot support a paired test (best possible
  two-sided sign-test p = 0.125).
- A second operator for a genuine external network.
- Approval-page date, and confirmation of the "two academic terms" schedule.
- Three references still carry a bracketed "author list to verify" note.

## Code

New stages in `pipeline/src/hoproj/`: `data/config_timeline_v2.py`, `revision/{data,models,evaluation}.py`,
`pipeline/stage22_revision.py` (audit, protocols, main, coherence, CRC, ablation),
`stage23_signalling_revision.py`, `stage24_external_revision.py`, `stage25_rev_figures.py`,
`stage26_rev_extras.py`. Outputs in `pipeline/reports_rev/{tables,figures}`. The v1 pipeline and
`reports_xcal` are untouched.

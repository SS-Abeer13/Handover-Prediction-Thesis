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

**The mechanism, not just the observation (18 Sept).** A row written at the end of its second carries
the post-handover cell exactly when the handover completes before that second closes — margin
m = 1 − δ − x, for δ the command's position in the second and x the execution and reporting delay.
Our signalling stream records x, so the prediction is testable: of the 15 handovers
with m < 0, **none** contaminates its row; of the 923 with m > 0,
77.1 % do. The residual (22.5 % of handovers) is the export
refreshing its serving-cell field one row late — row t+1 carries the target in
84 % of those.

**Two external datasets, one control and one replication.**

- *Control.* Irish 4G/5G drive-test traces (Raca et al., MMSys 2020; G-NetTrack Pro, which samples
  rather than aggregates). No contamination: 29.4 % of 1,175 cell
  changes, and the t−1→t prediction gain (38 %) is smaller than the t−2→t−1 gain
  (57 %) — freshness, not contamination.
- *Replication with the rule under our control.* NUWiNS multi-carrier corpus (PAM 2025), raw XCAL at
  10 Hz, 3 US tier-1 operators, two cross-country routes. Keeping the **last**
  sample of each second: 93.2 % contaminated over 4,712 handovers in
  12 files (92.8 % isolated), row t−1 at 0.1 %. Keeping the
  **first** sample instead: 4.1 % on the same handovers.

Conclusion, revised: the alignment error is a property of the **row-aggregation rule**, not of a
vendor, a network or a region. Stronger and more useful than the earlier "check per dataset".

**A by-product.** In the last fifth of a second, a row is contaminated precisely when the serving-cell
register updates before the second closes, so the contamination share estimates the update-delay
distribution: 98 % with 75–100 ms left, 44 % with 50–75 ms,
0 % below 50 ms, over 903 handovers. The artefact recovers a
sub-second quantity from a one-hertz export. In the manuscript as Section 5.1, Figure 5.1 and
Table A.3; contribution 2 of six.

## Other substantive changes

1. **Unit of independence.** Each campaign is one continuous session, so there are four independent
   units, not 57. Leave-one-campaign-out is the primary protocol. Protocol ladder at 1 s (primary
   model): LOCO 0.179 → blocked+purge → random 180 s blocks (+13 %)
   → random rows (+48 %).
2. **Configuration timeline v2.** The parser now applies removal lists (15,100
   measId removals), the inter-frequency measId swap (5.5.6.1, 187 occurrences) and
   configuration release on leaving RRC_CONNECTED (56). 17.7 %
   of reports change event type.
3. **Offsets, weighted by handovers.** 74.8 % of A3-triggered handovers fire under
   a **positive** offset (+1 dB / 320 ms / 1 dB hysteresis). The negative-offset configurations are
   long-interval re-reporting configurations. The v1 contribution claim is reversed.
4. **A3 conversion has no unit-free value** (corrected again after the second review round).
   8,136 reports → 2,361 episodes (3.4 reports
   each). Declined: 63 % per report, 30 % per
   episode under a loose rule, **73 %** once each command is matched to one
   episode. The loose rule let 2,361 episodes claim 1,647 of
   957 commands (2.6x over-counting) and rewarded verbose
   configurations. What survives every unit, and sharpens under the strictest: mobility profile
   36.9 % declined against 95.2 % for the
   dominant monitoring profile. Reported as a definitional-instability finding, like ping-pong.
5. **Re-establishments.** 341 total: 321 reconfigurationFailure,
   17 otherFailure, 3 handoverFailure. Not radio link failures
   during mobility. Treated as a competing event; censoring them moves the 1 s lift by
   +0.03x.
6. **Coherence.** Independent heads violate ordering on 40.2 % of rows (single fit;
   29.0 % for the three-seed ensemble, now reported as a separate column so the two
   are never mixed); a cumulative-max
   projection also reaches zero, so the hazard argument now rests on calibration
   (0.036 vs 0.047 at 1 s, same arm, paired difference
   -0.010 [-0.014, -0.006])
   and on one fit instead of five. It does not rank better than the control, and the
   isotonic composite calibrates better than it does; both now stated.
7. **Conformal risk control.** Reported in both regimes: exchangeable chunk pool (realised
   0.168 at α = 0.20, alarm rate 47 %) and cross-campaign
   (realised 0.153, bound respected in 83 % of
   12 rotations).
8. **External check.** Same operator/city/instrument/institution — relabelled "independent collection
   on the same network". Both domains rebuilt from L3 signalling: ours→public AUROC
   0.760, public→public 0.711, ours→ours
   0.730.

## Round 3 (19 September): three changes that alter claims

1. **The lag confounding objection fails, and the mechanism sharpens.** Four arms on one common row
   set (Table 5.2b, 1 s AUPRC): nothing lagged 0.607; neighbour and gap columns
   only 0.595; serving-cell radio scalars only 0.178; all
   serving-relative with GPS live 0.159; everything 0.160.
   The serving-cell radio scalars carry 95.8 % of the drop, the neighbour/gap
   columns 2.5 %, and lagging GPS costs nothing. So the repair is not
   conservative and 0.600 → 0.179 is the leak. **The leak lives in `serving_rsrp`,
   `serving_sinr` and kin** — they report whichever cell the export treats as serving, so they
   change referent at the flip. That is the transferable warning, not "lag everything".
2. **Conformal risk control was certifying rows while promising handovers.** An event-level loss is
   now carried through. 36.4 % of commands have no usable row in the 1 s lead
   window, so no per-handover target is feasible at 1 s in more than
   25 % of rotations. At 3 s (12.0 % unresolvable)
   α = 0.20 is feasible in 75 % of rotations. **The sampling rate of the
   instrument, not the model or the calibration set, bounds what may be promised.** O3 is now "met in
   part".
3. **Ground truth is sound, and now evidenced.** All 957 commands carry a decoded
   RRCConnectionReconfigurationComplete; only 36 are followed by a
   re-establishment within 5 s (new Table 3.3).

Also: arm labels on Tables 5.3–5.6, the reordering claim restricted to untuned learners, Table 3.1
sums to 957, the operating point in the abstract, a competing-interests declaration, and
the NUWiNS experiment reframed as a controlled demonstration rather than a replication.

## Round 4 (19 September): claims withdrawn, and the bookkeeping closed

The round-3 panel's remaining findings were about claims the data do not support and about numbers
that did not reconcile. Four claims are now withdrawn in the text rather than softened.

1. **The ping-pong "lever" is withdrawn entirely.** §3.5 establishes the configuration set is stable
   across all four campaigns, so there is no TTT or offset variation anywhere in the data and
   neither parameter can be associated with the return rate in either direction. "Having ruled out
   speed as the driver" is also withdrawn: the *fastest* campaign has the *highest* return rate
   (32.2 % against 25.0 %), which is the opposite of a speed-protective
   account, and with one campaign per regime speed is confounded with route, cell density and time
   of day. The Hawkes branching ratio is now read as a clustering summary, not as a count of
   triggered handovers, because the paper's own Ogata test rejects the kernel that reading depends on.
2. **Table 5.14's two stratifications now reconcile, and the bug was real.** The detector was being
   re-run inside each stratum, which redefines "the immediately previous cell" as the previous cell
   *within the stratum*; the carrier rows implied 218 ping-pongs and the regime rows 252 on the same
   957 commands. Flags are now computed once on the full sequence and partitioned. Both
   stratifications give 252, and the carrier contrast sharpens: 31.1 %
   intra-frequency against 9.1 % inter-frequency.
3. **The censoring advantage is withdrawn, and the hazard arm's ranking claim with it.** §4.1 argued
   censoring must be modelled while §4.4 states no row is censored inside the horizon grid; the
   likelihood is correct and general but inert here, and is no longer counted as a benefit. Paired
   bootstrap on identical resampled blocks (new Table 5.6b): **no** AUPRC difference between the
   hazard arm and any control excludes zero (-0.001
   [-0.013, +0.010] against raw independent heads).
   What does survive is calibration — the hazard arm beats every no-split control by
   0.010 [0.006, 0.015],
   and the isotonic composite beats the hazard arm by 0.018. Contribution 4
   is now a convenience-plus-calibration argument and says so.
4. **The primary model has never been externally tested, stated at full strength.** Both arms of
   Table 5.9 are signalling-only, because the public dataset publishes no periodic radio export, so
   the 89 radio and 17 mobility features — essentially all of
   the signal — cannot be built on it. §5.7 now says the external evidence covers the formulation
   and the feature construction, not the predictor.

Novelty narrowed rather than defended: the screen returns no pre-2020 work, and the
cell-sojourn-time literature (Hong & Rappaport 1986; Lin et al. 2013; Sadr & Adve 2015) models the
same survival function. The claim is now *learned, covariate-conditional, per-sample* hazards on
measured data against analytical marginal laws. Prognos is compared numerically (F1 0.92–0.94 on
events vs our 0.179 AUPRC on rows) with the reason the two are not comparable.

Bookkeeping closed: feature counts are read from one generated table (89 radio +
17 mobility + 6 history = 112, plus
10 signalling columns reserved for the ablation = 122 on
disk — the 152/106/107/120 variants are gone); the two distances are labelled separately
(96 km recorded, 78 km in the modelling frame); "five seeds" corrected
to three; every citation is generated from one reference list and no entry is uncited; the
positive-offset share (74.8 %) belongs to the positive-offset profiles collectively,
not to the +1 dB profile alone (72.5 %); tuning has an explicit selection-accounting paragraph; and the two
release rows of Table 2.1 now commit to a versioned archive on acceptance instead of reading
"Planned" in a table that grades 22 papers on exactly that. Verification is at 113 checks, 0 failures.

## Round 5 (19 September): a third panel, and the worst finding so far

Three fresh reviewers read the round-4 manuscript. Their verdict was again major revision, and one
of their smaller observations led to the most serious defect found in any round.

1. **The paired-difference intervals were pseudo-replication.** Round 4's Table 5.6b bootstrapped
   over 180-second blocks -- the unit Section 5.3 proves is dependent (13 %
   inflation when you split on it). Resampling it deflates the standard error, so "interval excludes
   zero" was never earned. Withdrawn. Table 5.6b now reports the paired difference on each of the
   4 held-out campaigns and states that a sign test on four units cannot go below
   p = 0.125.
2. **That resolved a contradiction, in the opposite direction to the reviewer's guess.** §5.4 said
   the hazard arm won 0 of 4 campaigns while the pooled table favoured it. Cause: the per-campaign
   count came from the **tuned** arm and the pooled number from the **coherence** arm. Within one
   arm, the hazard arm calibrates better on **4 of 4** campaigns, so
   the pooled result stands. The per-campaign table promised to Appendix A and never printed is now
   Table A.4. Two side-effects: no AUPRC difference supports a ranking claim (pooled
   -0.001, yet positive on all four campaigns separately -- a sign reversal at
   a magnitude of a thousandth), and the isotonic composite's calibration advantage holds on three
   campaigns and **fails on the highway**, which round 4 missed by reporting only the pooled number.
3. **Ten stale citation numbers.** The panel flagged duplicated equation tags (4.9 and 4.11 each
   used twice, 4.10 never defined) and two references to a non-existent Section 3.7. Checking those
   surfaced something worse: the reference list gained two entries in round 2, and every hand-typed
   citation downstream of that in an un-rewritten paragraph was silently wrong -- Hawkes, Laub,
   Ogata, Price-Williams, Ismail Fawaz, CORAL, Shi, Wagner, Deb, temperature scaling, and the
   conformal-risk-control reference itself. Existing checks passed because every number was in
   range and every reference was cited *somewhere*. Verification now asserts the number beside each
   author's name equals that entry's position, and that equation tags are unique and gap-free.
4. **No qualitative error analysis existed.** The only trace anywhere was the idealised Figure 1.1.
   Table 5.16 and Figure 5.20 now draw nine cases uniformly at random under a fixed seed -- three
   true positives, three false alarms, three misses -- as full time series. Table A.6 settles the
   alignment residual one handover at a time: 178 of 211 residual
   handovers carry the target in row t+1, and the residual's median margin is indistinguishable
   from the contaminated cases', which kills the competing explanation.
5. **Four post-hoc windows are now varied** (Table A.5). Random-block inflation is positive at
   every block length (5.9-17.6 %); the quiet-over-burst
   ordering holds at every cutoff from 5 to 20 s; the lift is stable across the blank window. One
   result does **not** survive and is reported as such: the blocked protocol sits between
   -5.6 % and +3.7 % of LOCO depending on the purge,
   straddling zero.
6. **The quiet-vs-burst split had a survivor bias, and fixing it sharpened the claim.**
   100 % of positive "quiet" rows precede a command that *opens a
   burst*. So the finding is that the model predicts burst **onset** better than continuation --
   sharper and more useful than the original wording.

Also withdrawn: §1.2's "one second is sufficient for target-cell preparation" (the operating point
that would deliver it does not exist on this instrument); conformal risk control is reframed in the
abstract, Contribution 5 and O3 as a **boundary result**, not a delivered guarantee. The Ogata test
now reports D = 0.065, p = 0.0007. Three reviewer-supplied arXiv references
were checked and all three are real; two are cited as post-screen work, deliberately outside the
22-paper counts.

**Administrative.** One reviewer wanted Chapter 6 (outcome-based education) replaced with case
studies -- he was misled by a filename the review tooling generated, not by the manuscript, which is
correctly titled. Chapter 6 stays in full; the case studies went into Chapter 5. Separately, the
List of Figures and List of Tables were built from a hand-written range ending at Table 5.15, so
nine tables added during the revision were in the body but not the front matter. Both lists are now
generated and complete, including the Chapter 6 tables. **144 checks, 0 failing.**

**One thing to check yourself:** §6.2 says the course outcomes are those of **EEE 4700**. Confirm
that is the right course code before submission.

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
`stage28_nuwins_audit.py` (NUWiNS fetch/cache/aggregate), `stage29_alignment_mechanism.py`
(intra-second geometry, falsification test, three-dataset table),
`stage23_signalling_revision.py`, `stage24_external_revision.py`, `stage25_rev_figures.py`,
`stage26_rev_extras.py`. Outputs in `pipeline/reports_rev/{tables,figures}`. The v1 pipeline and
`reports_xcal` are untouched.

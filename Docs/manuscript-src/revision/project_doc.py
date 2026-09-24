# -*- coding: utf-8 -*-
"""Project doc for the Handover Thesis project: what the revision changed and why."""
from pathlib import Path

from msnumbers import build

OUT = Path("/home/claude/w/ms/revision-2026-09-18.md")


def main():
    N = build()
    p = lambda x, n=1: f"{100 * x:.{n}f} %"  # noqa: E731
    md = f"""# Revision after the 17 September review — what changed and why

**Status:** all experiments re-run; revised manuscript, response letter and verification report
produced on 18 September 2026. The reviewed draft is kept unchanged as
`Docs/Handover_Thesis_Manuscript_Draft.docx`; the revision is
`Docs/Handover_Thesis_Manuscript_Revised.docx`.

## The decision that drove everything else

The 1 Hz XCAL export row stamped *t* describes the second that **follows** its timestamp. Audited
against the RRC command stream: in {p(N['align_t0'])} of handovers (isolated handovers:
{p(N['align_iso_t0'])}) the row stamped inside the second before the handover command already shows
the post-handover serving cell, against a background of {p(N['align_iso_tm3'])} three rows earlier.
So the v1 features contained the answer.

Every export feature is now lagged one row. Headline effect, same model, same folds:

| 1 s horizon | v1 (unlagged) | v2 (lagged) |
|---|---|---|
| AUPRC | {N['lag0_auprc1']:.3f} | **{N['auprc1']:.3f}** (floor {p(N['prev1'])}, {N['lift1']:.1f}x) |
| AUROC | {N['lag0_auroc1']:.3f} | **{N['auroc1']:.3f}** |
| dwell alone (AUROC) | {N['lag0_dwell_auroc']:.3f} | **{N['dwell_auroc']:.3f}** |

At 5 s: AUPRC {N['auprc5']:.3f} ({N['lift5']:.1f}x). Deployed A3 rule at 1 s: AUPRC
{N['a3_auprc1']:.3f}.

**The mechanism, not just the observation (18 Sept).** A row written at the end of its second carries
the post-handover cell exactly when the handover completes before that second closes — margin
m = 1 − δ − x, for δ the command's position in the second and x the execution and reporting delay.
Our signalling stream records x, so the prediction is testable: of the {N['mech_n_neg']} handovers
with m < 0, **none** contaminates its row; of the {N['mech_n_pos']} with m > 0,
{p(N['mech_hit_pos'])} do. The residual ({p(N['mech_resid_share'])} of handovers) is the export
refreshing its serving-cell field one row late — row t+1 carries the target in
{p(N['mech_resid_tp1'], 0)} of those.

**Two external datasets, one control and one replication.**

- *Control.* Irish 4G/5G drive-test traces (Raca et al., MMSys 2020; G-NetTrack Pro, which samples
  rather than aggregates). No contamination: {p(N['ext_align_share'])} of {N['ext_align_n']:,} cell
  changes, and the t−1→t prediction gain ({N['ext_gain_t']:.0f} %) is smaller than the t−2→t−1 gain
  ({N['ext_gain_t1']:.0f} %) — freshness, not contamination.
- *Replication with the rule under our control.* NUWiNS multi-carrier corpus (PAM 2025), raw XCAL at
  10 Hz, {N['nw_operators']} US tier-1 operators, two cross-country routes. Keeping the **last**
  sample of each second: {p(N['nw_t0'])} contaminated over {N['nw_n']:,} handovers in
  {N['nw_files']} files ({p(N['nw_iso_t0'])} isolated), row t−1 at {p(N['nw_tm1'])}. Keeping the
  **first** sample instead: {p(N['nw_first_t0'])} on the same handovers.

Conclusion, revised: the alignment error is a property of the **row-aggregation rule**, not of a
vendor, a network or a region. Stronger and more useful than the earlier "check per dataset".

**A by-product.** In the last fifth of a second, a row is contaminated precisely when the serving-cell
register updates before the second closes, so the contamination share estimates the update-delay
distribution: {p(N['nw_cliff_hi'], 0)} with 75–100 ms left, {p(N['nw_cliff_mid'], 0)} with 50–75 ms,
{p(N['nw_cliff_lo'], 0)} below 50 ms, over {N['nw_cliff_n']:,} handovers. The artefact recovers a
sub-second quantity from a one-hertz export. In the manuscript as Section 5.1, Figure 5.1 and
Table A.3; contribution 2 of six.

## Other substantive changes

1. **Unit of independence.** Each campaign is one continuous session, so there are four independent
   units, not 57. Leave-one-campaign-out is the primary protocol. Protocol ladder at 1 s (primary
   model): LOCO {N['auprc1']:.3f} → blocked+purge → random 180 s blocks ({N['infl_chunk_lgbm']:+.0f} %)
   → random rows ({N['infl_row_lgbm']:+.0f} %).
2. **Configuration timeline v2.** The parser now applies removal lists ({N.get('tl_removals', 0):,}
   measId removals), the inter-frequency measId swap (5.5.6.1, {N.get('tl_swaps', 0)} occurrences) and
   configuration release on leaving RRC_CONNECTED ({N.get('tl_resets', 0)}). {p(N.get('tl_disagree', 0))}
   of reports change event type.
3. **Offsets, weighted by handovers.** {p(N['a3_pos_share'], 1)} of A3-triggered handovers fire under
   a **positive** offset (+1 dB / 320 ms / 1 dB hysteresis). The negative-offset configurations are
   long-interval re-reporting configurations. The v1 contribution claim is reversed.
4. **A3 conversion has no unit-free value** (corrected again after the second review round).
   {N['a3_reports']:,} reports → {N['a3_episodes']:,} episodes ({N['reports_per_episode']:.1f} reports
   each). Declined: {p(N['conv_rep_declined'], 0)} per report, {p(N['conv_ep_declined'], 0)} per
   episode under a loose rule, **{p(N['conv_ep1_declined'], 0)}** once each command is matched to one
   episode. The loose rule let {N['a3_episodes']:,} episodes claim {N['conv_mult_any']:,} of
   {N['ho_all']} commands ({N['conv_mult_factor']:.1f}x over-counting) and rewarded verbose
   configurations. What survives every unit, and sharpens under the strictest: mobility profile
   {p(N['conv_dom_declined_1to1'])} declined against {p(N['conv_mon_declined_1to1'])} for the
   dominant monitoring profile. Reported as a definitional-instability finding, like ping-pong.
5. **Re-establishments.** {N['reest_all']} total: {N['reest_reconf']} reconfigurationFailure,
   {N['reest_other']} otherFailure, {N['reest_hofail']} handoverFailure. Not radio link failures
   during mobility. Treated as a competing event; censoring them moves the 1 s lift by
   {N['censor_delta_lift1']:+.2f}x.
6. **Coherence.** Independent heads violate ordering on {p(N['viol_indep'])} of rows (single fit;
   {p(N['viol_indep_ens'])} for the three-seed ensemble, now reported as a separate column so the two
   are never mixed); a cumulative-max
   projection also reaches zero, so the hazard argument now rests on calibration
   ({N['ece1_hazard']:.3f} vs {N['ece1_cummax']:.3f} at 1 s, same arm, paired difference
   {N['dif_ece_cummax']:+.3f} [{N['dif_ece_cummax_lo']:+.3f}, {N['dif_ece_cummax_hi']:+.3f}])
   and on one fit instead of five. It does not rank better than the control, and the
   isotonic composite calibrates better than it does; both now stated.
7. **Conformal risk control.** Reported in both regimes: exchangeable chunk pool (realised
   {N['crc_loss20']:.3f} at α = 0.20, alarm rate {p(N['crc_alarm20'], 0)}) and cross-campaign
   (realised {N['crc_cross_loss20']:.3f}, bound respected in {p(N['crc_cross_ok20'], 0)} of
   {N['crc_rotations']} rotations).
8. **External check.** Same operator/city/instrument/institution — relabelled "independent collection
   on the same network". Both domains rebuilt from L3 signalling: ours→public AUROC
   {N['ext_ours_to_pub_auroc']:.3f}, public→public {N['ext_pub_auroc']:.3f}, ours→ours
   {N['ext_ours_auroc']:.3f}.

## Round 3 (19 September): three changes that alter claims

1. **The lag confounding objection fails, and the mechanism sharpens.** Four arms on one common row
   set (Table 5.2b, 1 s AUPRC): nothing lagged {N['sel_v1_auprc1']:.3f}; neighbour and gap columns
   only {N['sel_nbr_auprc1']:.3f}; serving-cell radio scalars only {N['sel_srv_auprc1']:.3f}; all
   serving-relative with GPS live {N['sel_asg_auprc1']:.3f}; everything {N['sel_v2_auprc1']:.3f}.
   The serving-cell radio scalars carry {p(N['sel_share_srv'], 1)} of the drop, the neighbour/gap
   columns {p(N['sel_share_nbr'], 1)}, and lagging GPS costs nothing. So the repair is not
   conservative and 0.600 → {N['auprc1']:.3f} is the leak. **The leak lives in `serving_rsrp`,
   `serving_sinr` and kin** — they report whichever cell the export treats as serving, so they
   change referent at the flip. That is the transferable warning, not "lag everything".
2. **Conformal risk control was certifying rows while promising handovers.** An event-level loss is
   now carried through. {p(N['crc_unresolvable1'])} of commands have no usable row in the 1 s lead
   window, so no per-handover target is feasible at 1 s in more than
   {p(N['crc_ev_feasible1_max'], 0)} of rotations. At 3 s ({p(N['crc_unresolvable3'])} unresolvable)
   α = 0.20 is feasible in {p(N['crc_ev_feasible3_20'], 0)} of rotations. **The sampling rate of the
   instrument, not the model or the calibration set, bounds what may be promised.** O3 is now "met in
   part".
3. **Ground truth is sound, and now evidenced.** All {N['gt_commands']} commands carry a decoded
   RRCConnectionReconfigurationComplete; only {N['gt_reest_after']} are followed by a
   re-establishment within 5 s (new Table 3.3).

Also: arm labels on Tables 5.3–5.6, the reordering claim restricted to untuned learners, Table 3.1
sums to {N['ho_all']}, the operating point in the abstract, a competing-interests declaration, and
the NUWiNS experiment reframed as a controlled demonstration rather than a replication.

## Round 4 (19 September): claims withdrawn, and the bookkeeping closed

The round-3 panel's remaining findings were about claims the data do not support and about numbers
that did not reconcile. Four claims are now withdrawn in the text rather than softened.

1. **The ping-pong "lever" is withdrawn entirely.** §3.5 establishes the configuration set is stable
   across all four campaigns, so there is no TTT or offset variation anywhere in the data and
   neither parameter can be associated with the return rate in either direction. "Having ruled out
   speed as the driver" is also withdrawn: the *fastest* campaign has the *highest* return rate
   ({p(N['pp_highway'])} against {p(N['pp_urban'])}), which is the opposite of a speed-protective
   account, and with one campaign per regime speed is confounded with route, cell density and time
   of day. The Hawkes branching ratio is now read as a clustering summary, not as a count of
   triggered handovers, because the paper's own Ogata test rejects the kernel that reading depends on.
2. **Table 5.14's two stratifications now reconcile, and the bug was real.** The detector was being
   re-run inside each stratum, which redefines "the immediately previous cell" as the previous cell
   *within the stratum*; the carrier rows implied 218 ping-pongs and the regime rows 252 on the same
   {N['ho_all']} commands. Flags are now computed once on the full sequence and partitioned. Both
   stratifications give {N['pp_n_total']}, and the carrier contrast sharpens: {p(N['pp_intra'])}
   intra-frequency against {p(N['pp_inter'])} inter-frequency.
3. **The censoring advantage is withdrawn, and the hazard arm's ranking claim with it.** §4.1 argued
   censoring must be modelled while §4.4 states no row is censored inside the horizon grid; the
   likelihood is correct and general but inert here, and is no longer counted as a benefit. Paired
   bootstrap on identical resampled blocks (new Table 5.6b): **no** AUPRC difference between the
   hazard arm and any control excludes zero ({N['dif_auprc_indep']:+.3f}
   [{N['dif_auprc_indep_lo']:+.3f}, {N['dif_auprc_indep_hi']:+.3f}] against raw independent heads).
   What does survive is calibration — the hazard arm beats every no-split control by
   {abs(N['dif_ece_indep']):.3f} [{abs(N['dif_ece_indep_hi']):.3f}, {abs(N['dif_ece_indep_lo']):.3f}],
   and the isotonic composite beats the hazard arm by {abs(N['dif_ece_isopav']):.3f}. Contribution 4
   is now a convenience-plus-calibration argument and says so.
4. **The primary model has never been externally tested, stated at full strength.** Both arms of
   Table 5.9 are signalling-only, because the public dataset publishes no periodic radio export, so
   the {N['n_feat_radio']} radio and {N['n_feat_mobility']} mobility features — essentially all of
   the signal — cannot be built on it. §5.7 now says the external evidence covers the formulation
   and the feature construction, not the predictor.

Novelty narrowed rather than defended: the screen returns no pre-2020 work, and the
cell-sojourn-time literature (Hong & Rappaport 1986; Lin et al. 2013; Sadr & Adve 2015) models the
same survival function. The claim is now *learned, covariate-conditional, per-sample* hazards on
measured data against analytical marginal laws. Prognos is compared numerically (F1 0.92–0.94 on
events vs our {N['auprc1']:.3f} AUPRC on rows) with the reason the two are not comparable.

Bookkeeping closed: feature counts are read from one generated table ({N['n_feat_radio']} radio +
{N['n_feat_mobility']} mobility + {N['n_feat_history']} history = {N['n_features']}, plus
{N['n_feat_signalling']} signalling columns reserved for the ablation = {N['n_feat_matrix']} on
disk — the 152/106/107/120 variants are gone); the two distances are labelled separately
({N['km_driven']:.0f} km recorded, {N['km']:.0f} km in the modelling frame); "five seeds" corrected
to three; every citation is generated from one reference list and no entry is uncited; the
positive-offset share ({p(N['a3_pos_share'], 1)}) belongs to the positive-offset profiles collectively,
not to the +1 dB profile alone ({p(N['a3_dom_share_of_a3'], 1)}); tuning has an explicit selection-accounting paragraph; and the two
release rows of Table 2.1 now commit to a versioned archive on acceptance instead of reading
"Planned" in a table that grades 22 papers on exactly that. Verification is at 113 checks, 0 failures.

## Round 5 (19 September): a third panel, and the worst finding so far

Three fresh reviewers read the round-4 manuscript. Their verdict was again major revision, and one
of their smaller observations led to the most serious defect found in any round.

1. **The paired-difference intervals were pseudo-replication.** Round 4's Table 5.6b bootstrapped
   over 180-second blocks -- the unit Section 5.3 proves is dependent ({p(N['infl_chunk_lgbm'] / 100, 0)}
   inflation when you split on it). Resampling it deflates the standard error, so "interval excludes
   zero" was never earned. Withdrawn. Table 5.6b now reports the paired difference on each of the
   {N['n_campaigns']} held-out campaigns and states that a sign test on four units cannot go below
   p = {N['min_p']:.3f}.
2. **That resolved a contradiction, in the opposite direction to the reviewer's guess.** §5.4 said
   the hazard arm won 0 of 4 campaigns while the pooled table favoured it. Cause: the per-campaign
   count came from the **tuned** arm and the pooled number from the **coherence** arm. Within one
   arm, the hazard arm calibrates better on **{N['ece_wins']} of {N['n_campaigns']}** campaigns, so
   the pooled result stands. The per-campaign table promised to Appendix A and never printed is now
   Table A.4. Two side-effects: no AUPRC difference supports a ranking claim (pooled
   {N['dif_auprc_indep']:+.3f}, yet positive on all four campaigns separately -- a sign reversal at
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
   alignment residual one handover at a time: {N['resid_tp1_n']} of {N['resid_n']} residual
   handovers carry the target in row t+1, and the residual's median margin is indistinguishable
   from the contaminated cases', which kills the competing explanation.
5. **Four post-hoc windows are now varied** (Table A.5). Random-block inflation is positive at
   every block length ({N['sens_block_min']:.1f}-{N['sens_block_max']:.1f} %); the quiet-over-burst
   ordering holds at every cutoff from 5 to 20 s; the lift is stable across the blank window. One
   result does **not** survive and is reported as such: the blocked protocol sits between
   {N['sens_purge_min']:+.1f} % and {N['sens_purge_max']:+.1f} % of LOCO depending on the purge,
   straddling zero.
6. **The quiet-vs-burst split had a survivor bias, and fixing it sharpened the claim.**
   {p(N['burst_init_quiet_share'], 0)} of positive "quiet" rows precede a command that *opens a
   burst*. So the finding is that the model predicts burst **onset** better than continuation --
   sharper and more useful than the original wording.

Also withdrawn: §1.2's "one second is sufficient for target-cell preparation" (the operating point
that would deliver it does not exist on this instrument); conformal risk control is reframed in the
abstract, Contribution 5 and O3 as a **boundary result**, not a delivered guarantee. The Ogata test
now reports D = {N['ogata_D']:.3f}, p = {N['ogata_p']:.4f}. Three reviewer-supplied arXiv references
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
({N['lift1']:.1f}x at 1 s, {N['lift5']:.1f}x at 5 s), and corrected characterisations of the deployed
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

New stages in `pipeline/src/hoproj/`: `data/config_timeline_v2.py`, `revision/{{data,models,evaluation}}.py`,
`pipeline/stage22_revision.py` (audit, protocols, main, coherence, CRC, ablation),
`stage28_nuwins_audit.py` (NUWiNS fetch/cache/aggregate), `stage29_alignment_mechanism.py`
(intra-second geometry, falsification test, three-dataset table),
`stage23_signalling_revision.py`, `stage24_external_revision.py`, `stage25_rev_figures.py`,
`stage26_rev_extras.py`. Outputs in `pipeline/reports_rev/{{tables,figures}}`. The v1 pipeline and
`reports_xcal` are untouched.
"""
    OUT.write_text(md)
    print(md[:400])


if __name__ == "__main__":
    main()

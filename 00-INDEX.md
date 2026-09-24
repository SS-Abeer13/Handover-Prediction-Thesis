# Handover Thesis — report index and reading guide

All twenty-six reports live in this folder. They were written in order as the
work happened, so later ones correct earlier ones. **Read the status column
before citing anything.**

---

## If you read only five

This is the shortest path to the whole story, start to finish:

```
03  ->  13  ->  17  ->  20  ->  18v2
audit   the     the     the     what
the     reframe parser  rerun   stands
data            defect          now
```

| order | doc | why it matters |
|---|---|---|
| 1 | **03** — dataset audit | The first dataset was synthetic. Everything before this is void. Start here or you will believe the wrong numbers. |
| 2 | **13** — algorithm exploration and reframe | The task was formulated wrong. Handover prediction is discrete-time survival; ping-pong is self-excitation; off-policy evaluation is unidentified under a deterministic rule. This is where the thesis found its shape. |
| 3 | **17** — papers read and the attribution fix | The parser defect that invalidated several results, found only by comparing our extraction against a published method. `reportConfigId` is message-scoped, not global. |
| 4 | **20** — results after the improvement plan | The benchmark rerun on signalling ground truth. Every headline number changes. Two claims narrow under a fair test; three new results appear. |
| 5 | **18v2** — contribution table v2 | What actually stands, C1–C17, with what was withdrawn and why. |

Add **19** if you want the improvement plan those reruns came from, and **08**
for the thesis framing and field plan.

---

## Full list, in order written

| # | Doc | What it covers | Status |
|---|---|---|---|
| 01 | `01-pipeline-decisions.md` | Pipeline design choices: pseudo-drives from GPS, horizons, locked external route, 4-way split, conformal method | current |
| 02 | `02-first-full-run-results-VOID.md` | First full run | **VOID — synthetic data. Do not cite.** |
| 03 | `03-dataset-audit-DRIVETEST_LOGS_1.md` | Authenticity audit. Original file synthetic; replacement real. How the audit itself was validated | current |
| 04 | `04-results-on-fixed-data.md` | Full re-run on real data. The honest baseline | **superseded by 20** for every headline number; the method notes stand |
| 05 | `05-sept12-verification.md` | First XCAL + RRC signalling capture. What the signalling unlocks | current |
| 06 | `06-data-collection-plan.md` | Field fixes: sampling rate, neighbour reporting, QoE, volume | partly superseded by 10 |
| 07 | `07-cross-capture-transfer.md` | Transfer matrix across captures. The curated set does not describe the measured network | **historical**; the curated dataset is out of the evidence base and its transfer matrix is replaced by leave-one-capture-out (MASTER §19.1, doc 25 §4) |
| 08 | `08-thesis-frame-and-field-plan.md` | Thesis frame, hypotheses, results register, field plan | revised 13 Sept |
| 09 | `09-sept13-regime-transfer-correction.md` | Leakage-free regime transfer; H2/H3 falsified on the then-current labels | **H2 reinstated by 18** (Δ AUROC 0.088 on corrected labels) |
| 10 | `10-neighbour-coverage-signalling.md` | Two parser defects found and fixed; coverage 28% → 62–79%, accuracy unchanged | current |
| 11 | `11-benchmark-vs-finalmanuscript.md` | Benchmark against the same-department IUT manuscript | current |
| 12 | `12-public-dataset-external-validation.md` | External validation on the public Mendeley dataset; parser agrees 310/310 with XCAL | current |
| 13 | `13-algorithm-exploration-and-reframe.md` | ~120-paper algorithm sweep and the reframe: hazard, self-excitation, unidentified OPE | current |
| 14 | `14-hazard-selfexcitation-riskcontrol.md` | Doc 13 implemented: hazard reframe, Hawkes 0.61, conformal risk control, the n ≥ 1/α − 1 rule | **§5 superseded by 18v2**; C1 and C2 narrowed by 20 |
| 15 | `15-benefit-envelope-and-mechanism.md` | Benefit envelope with a chance reference; the mechanism figure | **§2 WITHDRAWN** (92.5% trigger coverage → 27.1%); the envelope itself strengthened by 20 |
| 16 | `16-literature-review-pass1.md` | 87 screened references + protocol audit of the competitor set | **counts superseded by 22**; the two findings stand |
| 17 | `17-papers-read-and-attribution-fix.md` | Three papers read in full, and the configuration-timeline fix they exposed | current |
| 18 | `18-corrected-mechanism-and-contributions.md` | Corrected mechanism and contribution table v1 | **superseded by 18v2** |
| 19 | `19-improvement-plan.md` | Audit of the tables against what a reviewer will ask; thirteen ranked improvements with steps | A–L all done (I, K, L in doc 21); only M, a field day, remains |
| 20 | `20-results-after-improvement-plan.md` | The reruns. One dataset, a fair baseline, power in every paired test, three claims changed | current for method; **every headline number is now the four-capture one in 25 and MASTER** |
| 18v2 | `18v2-contribution-table.md` | C1–C19 with status, withdrawals, and the one hypothesis of mine that was refuted | current; C3 and C13 narrowed, C18 and C19 added on 15 Sept; the curated comparison removed |
| 21 | `21-outstanding-items-closed.md` | Items I, K and L closed and literature pass 2 done. Adaptation hurts; the departmental method measured; the under-tuned-baselines objection granted and survived; four citation errors fixed | current |
| 22 | `22-literature-review-pass3.md` | Survey widened from 88 to 108 references across nine new threads; protocol audit from 17 to 22 rows. Four more citation errors fixed. Two claims narrowed: conformal-in-wireless is prior art, and two more competitors use a non-random split | current |
| 23 | `23-sept15-highway-validation-and-cross-campaign.md` | Fourth drive campaign (15 Sept, 34.6 km, 49.5 km/h highway corridor to Gazipur/IUT). RLFs collapse 159 → 5; the physical contrast between regimes | current for the **campaign description**; its handover counts are raw-log counts and its ping-pong and A3 rates use looser definitions than the pipeline — **use 25 for every rate** |
| 24 | `24-comparative-analysis-shafi-et-al-dataset.md` | Comparative analysis against Shafi et al. (2025 Mendeley Data v2.0): dataset architecture, sampling continuity, RRC state, parser agreement | current for the **dataset comparison**; the performance figures in it were not produced by the pipeline and are not the ones in MASTER §19.2 and §25.1 |
| 25 | `25-fourth-capture-and-pingpong-forensics.md` | 15 Sept rebuilt **through the pipeline**. Four-capture benchmark, leave-one-capture-out (highway held out whole: AUROC 0.927), the ping-pong definition ladder 24.5% → 41.3% and where the rate actually comes from, and the A3 report-set reconciliation | **newest** |

---

## The progression, in one page

**Build (01).** A pipeline was built from the proposal. The capture was three
long continuous sessions, not drives, so drives were reconstructed
geometrically from GPS. The 0.5 s horizon was dropped as unmeasurable at 1 Hz.

**A false start (02).** The first full run looked excellent. AUROC 0.95.

**The floor falls out (03).** An authenticity audit — written because those
numbers looked too clean — showed the dataset was synthetic. Handover targets
matched measured neighbours 0.6% of the time, below the 1.4% chance rate.

**The real baseline (04).** Re-run on real data, the problem looked much
harder: AUPRC lift 2.3–3.3×, LightGBM beating every sequence model, and one
result that got *stronger* — random-row splitting inflates GRU AUPRC by 109%
against LightGBM's 12%.

**Signalling changes the game (05, 06).** XCAL captures with decoded RRC
arrive: confirmed handovers with target cells, RLF events, and the operator's
own A3 parameters.

**The failure worth publishing (07).** Train on one capture, test on another.
Real to real transfers at 0.82–0.83. Real to curated lands at 0.36 — below
chance.

**A frame, then a correction (08, 09).** A thesis frame built on A3
configuration as the cause of that failure was falsified by a controlled
within-campaign experiment, after a leak in my own design was found and fixed.

**Cleaning my own instrument (10).** "Sparse neighbours" turned out to be two
defects in my parser. Coverage 28% → 79%, accuracy change: none.

**Finding the real shape of the problem (13, 14).** A literature sweep showed
the target was formulated wrong. Reformulated as discrete-time survival, with
ping-pong as a self-exciting point process and a distribution-free bound on
missed handovers.

**The parser defect that mattered most (17).** `reportConfigId` and `measId`
are *message-scoped indices*, not global identifiers. A flattened parse
attributed 99.4% of reports to A3, which is impossible when 43% of reports
carry no neighbour. Found only by comparing our extraction against Ghoshal et
al.'s. A configuration timeline fixed it — and four claims, including two of
mine, changed or died.

**The audit of my own tables (19).** Reading the result files as a reviewer
would exposed the real problem: the benchmark tables and the contribution
tables described **two different datasets with two different label
definitions**, and the headline table was on the weaker one.

**The rerun (20, 18v2).** Everything now runs on the pooled XCAL signalling
captures under grouped K-fold with every drive tested once. The same LightGBM
goes from AUROC 0.816 to **0.933** at 1 s. The 0.5 s horizon comes back,
because the *event* clock is millisecond-precise even though the sample clock
is not. And under a baseline allowed to fight back, the hazard model's
calibration advantage turns out to belong to isotonic regression, while its
coherence advantage is real and cheap. Two claims narrowed, three added, one of
my own predictions refuted.

---

## Where the evidence lives

| what | where |
|---|---|
| **The technical document** | `MASTER-Handover-Prediction.md` — 29 sections, updated 14 Sept with §11.6, §15's tuned arm, §19's adaptation arms, §24 C15–C17 and §25.1; bundled with its figures in `master-doc.zip` |
| **Current tables** (csv / md / **tex**) | `pipeline\reports_xcal\tables\` — the XCAL rerun; `.tex` drops into LaTeX |
| Superseded tables | `pipeline\reports\tables\` — the curated-data run. **Not cited anywhere**; kept only so the audit trail is complete |
| **Mechanism figure** | `pipeline\reports_xcal\figures\fig_mechanism_a3.png` — regenerated by `stage17` |
| Other figures | `pipeline\reports\figures\viz_*.png` |
| Bibliography | `pipeline\docs\literature\references.bib` (108 entries, verification-tagged: 93 full, 15 partial; originals in `.bak`) |
| Protocol audit | `pipeline\docs\literature\protocol_audit.csv` (22 competitor rows + ours) |
| Executed notebooks | `Claude outputs\*.html` |
| Pipeline code | `pipeline\src\hoproj\` — 18 stages, stage00 to stage17 |
| Tests | `pipeline\tests\` — 17 passing |
| Original proposal | `Docs\Proposal\` |
| Papers read | `Docs\Literature\` |
| Raw captures | `Drivetest Data\` |

---

## Where things stand right now

1. **One dataset, now four captures.** Every table in the manuscript describes
   the pooled XCAL captures: **57 drives, 10,260 samples, 938
   signalling-confirmed handovers**, grouped K-fold with every drive tested once
   and 57 bootstrap groups. The curated 6-8 Sept export has been removed from
   every comparison, document and figure.
1b. **The fourth capture changed nothing, which is the result.** 15 Sept is a
   highway corridor at 49.5 km/h mean, driven after every modelling decision was
   frozen. Pooled AUROC at 1 s: **0.933 before, 0.933 after**. Held out whole it
   is predicted at **AUROC 0.927 with the highest lift (14.9×) and the lowest
   calibration error (0.018) of the four captures**.
2. **1 Hz is permanent, and now correctly scoped.** It bounds *event detection*
   at 90.5%; it does not bound horizon resolution, because handover timestamps
   are millisecond-precise. The 0.5 s horizon is back.
3. **C1 and C2 are narrower than they were** (doc 20 §3 and §5) and much harder
   to attack. C3, C5 and C11 are stronger.
3b. **The ping-pong rate is settled, and the settling is itself a finding.**
   **24.5%** at the literature-standard 15 s threshold with cell identity and
   the return rule stated. The same 938 handovers give 41.3% under three
   unstated choices — which is why published rates are not comparable. The
   mechanism is localised: **31.0% intra-carrier against 6.5% inter-carrier**,
   and **29.2% on the single +1 dB / 320 ms A3 profile that fires 72% of all
   handovers**. The lever is that profile's time-to-trigger, not the offset and
   not vehicle speed — at 49.5 km/h the highway still returns 31.1%.
4. **Five information channels now measured, five gains of nothing**: neighbour
   coverage, self-excitation features, the full signalling channel, a dedicated
   ping-pong target, and — as of doc 21 — zero-cost domain adaptation, which
   makes transfer measurably *worse*. Configuration is the one thing that does
   matter.
5. **The closest comparator has been measured, not just argued** (doc 21 §3).
   The departmental manuscript's method, reimplemented on our data, predicts
   handovers at AUROC 0.505; ranking by its own reward function without any
   reinforcement learning scores 0.614; our LightGBM on the same rows scores
   0.921.
6. **The bibliography is eight citation errors safer** across three passes
   (doc 21 §4, doc 22 §6), and the protocol audit now covers 22 papers rather
   than 11. C13 has been amended twice: five papers in the enlarged set split
   on a unit coarser than a row — by zone, device, time, travel day and
   deployment event — and none of them holds out the mobility unit for a
   per-timestep classification task on measured radio. The columns that did not
   move under a third widening are the ones that matter: **zero of 22** report a
   calibration curve, and **zero of 22** report how early their warnings
   arrive.
7. **The under-tuned-baselines objection is closed** (doc 21 §5). Under an equal
   20-trial nested-CV budget the sequence models gain a lot — Transformer +0.109
   AUPRC at 1 s — and still rank below an untuned logistic regression, while
   tuning LightGBM itself costs 0.021. One correction falls out of it: logistic
   regression's ECE of 0.123 in doc 20 is a `class_weight` artefact; tuned it is
   0.0098.
8. **Two claims are now smaller and better defended** (doc 22 §4). Conformal
   prediction inside wireless is established work by Cohen et al. and Simeone et
   al.; ours is the exchangeability unit and the KPI, not the machinery. And
   the discrete-time survival formulation is mainstream in the survival
   literature — which removes a novelty claim and removes, with it, the
   question of why we invented it. Both narrowings are now written into
   MASTER §12, §24 (C3, C13), §25.2 and §27, and into 18v2.
9. **One more quiet overclaim found and closed.** Wiring the provenance
   citations into the master document meant looking for the section that
   documents the deep-ensemble arm — and there isn't one. `stage03_uncertainty`
   trains a five-member ensemble, it was run on the old curated dataset, and it
   was never re-run on the pooled XCAL captures: there is no ensemble row in
   `reports_xcal\tables\`. The protocol audit had been claiming "ensembles"
   among our uncertainty methods. That row is corrected, MASTER §27 records the
   gap, and the arm must be re-run or dropped before submission. This is the
   second claim to outlive the thing it described; both were caught by trying
   to cite them.
10. **The bottleneck is the manuscript.** Every desk-closable item in doc 19 is
   now closed; only a field day and the writing remain.

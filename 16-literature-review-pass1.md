# Literature review — pass 1, and the positioning it buys

> **Status, 15 Sept 2026 — superseded on the counts, current on the argument.**
> The survey has been through two more passes since this document. Pass 2
> (doc 21 §4) re-verified 18 entries and fixed four citation errors; pass 3
> (doc 22) widened it from 88 to **108 entries** across nine further threads and
> the protocol audit from 11 papers to **22**, fixed four more errors, and
> forced two claims to narrow. **Do not quote the counts below** — quote doc 22
> §3, or MASTER §25. The two findings this document identifies as changing the
> thesis both survived all three passes.

All four screening threads are complete: A (ML/DL handover and RLF
prediction), B (control-parameter optimisation), C (measurement studies,
datasets, ping-pong, dwell time, 3GPP), D (evaluation methodology and
reproducibility). Together with the method references from docs 13 and 14 this
is **87 screened entries**.

**Two findings change the thesis. Read §2 and §3 before writing anything.**

Deliverables now in the repo:

- `docs/literature/references.bib` — **87 entries**, every one tagged
  `verified=full` (39), `verified=partial` (17) or `verified=id-only` (12).
  Anything not `full` must be re-checked against the publisher record before
  submission; several are 2025–26 preprints.
- `docs/literature/protocol_audit.csv` — the protocol-quality audit, one row per
  paper, with our own work as the last row.
- `docs/literature/pingpong_benchmark.md` — our ping-pong rate recomputed to be
  directly comparable to the one large-scale measurement study that reports it.

---

## 1. The finding that justifies the whole thesis

I screened every paper in the direct competitor set for how it separated
training from test data, what it measured, and whether it quantified
uncertainty. Denominator is the **11 papers that actually train and evaluate a
predictive model** (three further entries are dataset papers).

| protocol property | papers satisfying it |
|---|---|
| Leakage-safe **grouped** split | **2 / 11** |
| Split by **drive, route or trajectory** | **0 / 11** |
| Split by **time** | **0 / 11** |
| Prevalence-aware metric (AUPRC or PR curve) | **1 / 11** |
| Any **calibration** measure (reliability, Brier, ECE) | **0 / 11** |
| Any **predictive uncertainty** (interval, conformal, ensemble spread) | **0 / 11** |
| **False alarms per hour or per km** | **0 / 11** |
| **Lead-time distribution** on detected events | **0 / 11** |
| Real measured field data (not a simulator) | 3 / 11 (5 / 11 counting radio testbeds) |
| Headline **accuracy on an imbalanced task** | **6 / 11** |
| Code released | 1 / 11 |
| Data released | 1 / 11 |

Six of eleven state no split protocol at all. Three use a plain random ratio
split with no grouping — including one that pools 200 simulated trajectories
into a single row set and then samples 60/20/20 from it, which is the exact
window-overlap leakage our own study measured at **GRU +109% AUPRC**.

The sharpest single instance: a 2026 railway RLF paper reports AUC-ROC above
0.95 for all six architectures it compares on a task with **1 positive per 500
samples** — and separates none of them, because ROC-AUC is near-uninformative at
that prevalence. It also reports accuracy on that task, states no split
protocol, and reports no calibration.

**This is the gap statement.** Not "nobody has applied model X" — that argument
ages badly and invites a reviewer to name a paper. The argument is that the
field's evaluation protocol does not support the claims it makes, and we can
demonstrate that with counts.

## 2. The A3-recovery novelty claim is dead. Reframe it.

**Correction to doc 14 and the contribution list.** Recovering an operator's
deployed A3 parameters from RRC signalling on a live commercial network is
**not novel**. There is an established line of it in the networking-measurement
community — IMC, SIGCOMM, MobiCom — which is a different venue community from
the handover-optimisation literature the project had been reading.

| prior work | what it does |
|---|---|
| **Deng, Peng, Fida, Meng, Hu, IMC 2018** | The **LTE precedent**. Measurement study of operational 4G mobility configurations. **Obtain and read this before writing the contribution list** — it is the paper most likely to pre-empt us. |
| **Ghoshal et al., arXiv:2511.03116, 2025** | Does exactly what we do, at ~100× the scale. Accuver **XCAL** on the Qualcomm Diag interface; extracts hysteresis, threshold, offset, TTT and trigger quantity for events A1–A6, B1, B2, per operator and band. 15,000+ km, **48,426 handovers**, three US operators. |
| **Hassan et al., SIGCOMM 2022** | Establishes XCAL-based RRC extraction as accepted methodology. Cite it — it legitimises our pipeline rather than threatening it. |
| **Liu et al., MobiCom 2024 (M2HO)** | Reads `mobilityControlInfo` but explicitly does *not* recover numerical parameters. A useful contrast case. |

Claiming the extraction itself would risk a desk reject at any venue with an
IMC- or SIGCOMM-literate reviewer.

**What is still genuinely open.** None of those papers builds a predictive
model — Ghoshal et al. state outright that they do no ML prediction, no
off-policy evaluation and no counterfactual analysis; the work is descriptive.
Conversely the handover-prediction papers on real data treat A3 as an assumed
baseline with textbook values. So the defensible claim is the join:

> We use operator-deployed A3 parameters, recovered per carrier from RRC
> `measConfig`/`reportConfigEUTRA`, as the label-generating and
> feature-construction basis for a supervised handover-prediction pipeline —
> closing the gap between a measurement literature that recovers configurations
> but does not predict, and a prediction literature that predicts but assumes
> configurations.

Additional uncontested value: **LTE** (the extraction work has moved to 5G), a
**non-US single-operator** deployment (all of it is US-centric bar one Chennai
dataset), and the **configuration-conditioned evaluation**.

## 3. Our ping-pong rate, finally comparable — and a sharper finding underneath

There is no 3GPP-standardised ping-pong definition. What exists is
cell-return within an author-chosen window, and the window moves the number by
an order of magnitude. Recomputed at Ghoshal et al.'s **15 s window** with a
**per-handover denominator**:

| network | ping-pong | A3 offset + hysteresis | shortest TTT |
|---|---|---|---|
| AT&T, T-Mobile (US) | 15–16% | +8 to +10 dB | 320–640 ms |
| Verizon (US) | 25% | +6 to +8 dB | 256 ms |
| **This network, pooled** | **29.4%** | **−15 to +5 dB** | **160 ms** |

**29.4% is high but coherent.** It exceeds the worst US operator, on a
configuration that is more aggressive than that operator's on both axes: this
operator runs **negative** A3 offsets — triggering while the neighbour is still
*weaker* — where all three US operators run positive ones, and its shortest TTT
is 160 ms against Verizon's 256 ms. Verizon's 256 ms is exactly the mechanism
Ghoshal et al. give for its 25%. The rate also saturates above a 10 s window
(0.281 → 0.294 → 0.314 at 10/15/30 s), so it is not a window artefact.

Underneath, though, the simple story fails: the **−10 dB / 640 ms** profile has
the highest within-network ping-pong (33.9%), not the aggressive **−15 dB /
160 ms** one (28.0%). The cross-operator mechanism does not explain the
within-network variation — consistent with our own finding that predictability
is invariant to the A3 regime.

**Two cheap methodological points fall out of this**, both worth stating because
the literature is careless about them: always state the **return window**, and
always state the **denominator**. Amirova et al. report 0.13% ping-pong because
they divide by measurement records rather than handovers.

## 4. The one paper that is genuinely close, and how to treat it

**Amirova et al., *Future Internet* 18(6):290, 2026** — real LTE/5G drive test in
Astana, ~27,000 records, 232 handovers (0.86% prevalence), device-level hold-out
with downsampling confined to the training subset, PR curves, bootstrap CIs on
AUC. It is the only paper in the set with a leakage-aware, prevalence-preserving
protocol, and its honest headline is a random forest at **precision 0.117 for
recall 0.843**.

Cite it as an ally, not a rival. It corroborates our position and gives a real
comparator for what an imbalanced handover task looks like once accuracy is
abandoned. Our advances over it are concrete and statable: grouping by **drive
and route** rather than device, signalling-confirmed rather than CSV-derived
labels, a hazard rather than a single binary target, calibration and conformal
guarantees, and external validation on an independent public dataset.

## 5. Gap statements, mapped to what we already measured

Each line is a claim we can defend with a number from our own results and a
citation count from the audit.

| # | Gap in the literature | Our evidence |
|---|---|---|
| G1 | No handover-prediction study splits by drive, route or time; window-overlap leakage is unmeasured | Leakage is architecture-dependent: GRU **+109%** AUPRC under random-row splitting vs LightGBM **+12%** |
| G2 | Handover prediction is universally posed as classification; no study uses a time-to-event formulation | Discrete-time hazard: equal discrimination, **ECE −23 to −35%**, incoherent predictions **25.4% → 0%** |
| G3 | Ping-pong is measured as a thresholded count; nobody models it as a stochastic process | Hawkes **branching ratio 0.61 ± 0.04** across three independent captures — 61% of handovers are self-triggered |
| G4 | Zero studies report predictive calibration or uncertainty | Split conformal 0.89–0.91 coverage; conformal risk control meets its FNR target at every horizon where a pooled-sample threshold fails |
| G5 | **REVISED.** Configuration recovery exists (Deng 2018, Ghoshal 2025) but is never joined to prediction; prediction papers assume textbook A3 values | 100% attribution of 761 handovers to the deployed profile, used as the label and feature basis; the dominant profile's gap condition covers **92.5%** of samples, which explains why neighbour features never helped |
| G6 | Event-detection rates are reported without a chance reference, and never with false alarms per hour | Our predictor beats a same-rate random alarm only below a ~10% alarm budget, and is **−21 pp worse than random at 40%** |
| G7 | Instrument limits are not quantified; detection rates are implicitly compared against 100% | At 1 Hz, **90.5%** of handovers is the hard ceiling on event detection |
| G8 | One dataset per paper; no independent external validation | Our model scores **0.729** AUROC on an independent public dataset against its own **0.719** in-domain ceiling |

G1, G4, G6 and G7 are methodological and generalise beyond handover — they are
what makes this a methods paper rather than an application paper.

## 6. Proposed Related Work structure

Six subsections, ~1,400 words, in the order a reader needs them.

1. **Handover control and its parameters** — 3GPP A3, hysteresis,
   time-to-trigger; MRO/HCP self-optimisation; fuzzy and metaheuristic tuning.
   *Thread B, pending.* Framing: this literature *tunes* the rule; we *predict*
   its firing.
2. **Learned handover and link-failure prediction** — the competitor set above,
   organised by target (occurrence / target cell / RLF / ping-pong) and by data
   provenance (simulated / testbed / measured).
3. **Measurement-based studies and public datasets** — the drive-test corpora,
   including the Mendeley set we use for external validation, DoNext and Vienna
   as future validation targets, and the norm (or absence) of data release.
4. **Evaluation practice in wireless ML** — the protocol audit as a table. This
   subsection is a contribution, not background.
5. **Time-to-event modelling and point processes** — survival analysis,
   discrete-time hazards, self-exciting processes; and the honest observation
   that the cellular-mobility literature has not used them.
6. **Distribution-free uncertainty and policy evaluation from logged data** —
   conformal prediction and risk control; why off-policy evaluation is
   unidentified under a deterministic A3 logging policy.

## 7. What still needs screening

All four screening threads are complete. What remains is **retrieval**, not
search — four specific papers must be read in full, and none could be fetched
from this session because of publisher rate limits and egress restrictions.

| priority | paper | why it must be read |
|---|---|---|
| **1** | **Deng et al., IMC 2018** — mobility configurations in operational 4G | The LTE precedent for configuration recovery. Our contribution list cannot be finalised until someone has read it. |
| **2** | **Zidic et al., *Computer Networks* 227:109699, 2023** — ping-pong in real 4G | The only journal paper devoted to ping-pong rates on a real 4G network. Hybrid open access — retrievable from any browser. |
| **3** | **Ghoshal et al., arXiv:2511.03116, 2025** | Read in full; it is both our benchmark and our closest pre-emption risk. |
| **4** | *Handover Optimization in LTE Networks Using Contextual Bandit RL and Real-World Data*, 2025 | Entirely unverified; ResearchGate 429. Title claims both a bandit and real data. If it does valid off-policy evaluation it is our nearest methodological competitor; if it replays a self-designed reward, it is a citation we critique. |

Also pending, lower priority: method extraction for the 17 thread-A papers
where only the bibliography was verified — prioritise the cross-operator outage
study (*Ad Hoc Networks* 2026), the GNN handover-forecasting papers, and Lee &
Cho's conditional-handover baseline.

Target is 40–60 references in the submitted manuscript. We have **87 screened**;
after pruning, expect ~55–60 cited.

### Three literature absences worth one sentence each in the manuscript

Stated as *"we are not aware of"*, never as *"none exists"*:

- **No leakage or evaluation-practice critique exists for ML in wireless.** The
  closest analogues are Arp et al. (USENIX Security 2022) for security and
  Jacobs et al. (CCS 2022) for networking. Our protocol audit is the first for
  cellular mobility prediction.
- **No peer-reviewed South-Asian LTE drive-test *handover* study** surfaced.
  The nearest is the IIT Madras 5G dataset (Chennai, arXiv:2605.12453), whose
  data is not yet released.
- **The metaheuristic handover literature is thinner than it looks.** Grey
  wolf, cuckoo search and mayfly return almost nothing for A3/HOM/TTT tuning;
  the strand is dominated by fuzzy logic, simulated annealing and RL. Do not
  over-claim a large metaheuristic field.

## 8. Cautions

**The optimisation literature has no valid policy evaluation either.** Across 25
screened tuning papers: **15 evaluate purely in simulation**, 2 use ray tracing
over a real layout with synthetic outcomes, and **zero** evaluate a learned
handover policy on real operator logs with any off-policy estimator or live A/B
test. One paper states explicitly that it has no off-policy evaluation; another
claims a 98% ping-pong reduction by replaying its own policy over a logged
trace, which assumes the trajectory would have been unchanged under different
handover decisions. Our doc-13 finding that OPE is unidentified under
deterministic A3 logging is therefore not a limitation peculiar to us — it is an
unacknowledged hole in the whole field, and saying so plainly is a contribution.

**Verification.** Several entries are very recent arXiv preprints whose
identifiers resolved but whose author lists or venues I could not fully confirm.
They are tagged. Do not submit with a `verified=partial` or `id-only` entry
un-rechecked — a wrong citation is the cheapest possible way to lose a reviewer.

**Do not overclaim novelty.** The defensible claim is *"no study in this set
does X"*, with the count and the screening protocol stated, not *"nobody has
ever done X"*. Thread B may yet turn up an A3-parameter-recovery paper; the
query was interrupted before it ran.

# The widened survey: nine threads, twenty papers, and two claims that have to narrow

Doc 16 screened 87 references and audited 11 competitors on protocol. Doc 21 §4
re-verified 18 of them and fixed four citation errors. Both passes worked
*outward from thread A* — the papers that predict handovers — and left the
methodological threads we actually borrow from thin, and the standards-track
question (what a prediction is *allowed* to drive) almost untouched.

This pass fixes that.

```
bibliography        88 entries  ->  107        (92 verified=full, 15 partial)
protocol audit      17 rows     ->  22 rows
threads             A,C,F,G,H,I ->  + J,K,L,M,N,O,P,Q,R
```

The short version: **the widened survey strengthens four of our claims, and
forces two of them to narrow.** Conformal prediction has already been applied
inside wireless — twice, by a strong group — so "conformal in telecom" was never
ours to claim; what is ours is the exchangeability unit and the KPI. And the
grouped-split claim, already amended once in doc 21, needs a second amendment:
two more papers in the enlarged set do split by something other than a random
row.

Everything below was checked against the publisher or arXiv record on
15 Sept 2026. Entries that could not be fully confirmed are marked, in the `.bib`
and here, and must be completed before submission.

---

## 1. Why the earlier passes were lopsided

Passes 1 and 2 were competitor-driven. That is the right instinct for a
positioning section and the wrong one for a methods section: it meant the
`.bib` could tell a reviewer exactly who else predicts handovers and almost
nothing about where the discrete-time hazard, the Ogata residual test, the CORAL
arm or the event-level metrics come from. Three of our four *methodological*
choices rested on a single citation each, and one — the ensemble baseline — on
none at all.

Nine threads were opened:

| thread | what it answers | entries |
|---|---|---|
| **J** standards-track mobility | what a prediction is allowed to drive | 2 |
| **K** review of reviews | how the field describes its own evidence base | 2 |
| **L** graph and trajectory models | the strongest non-sequence competitors | 4 |
| **M** conformal inside wireless | our nearest methodological kin | 2 |
| **N** survival / time-to-event | where the hazard formulation comes from | 2 |
| **O** point processes | where the Hawkes validation comes from | 2 |
| **P** domain adaptation | what CORAL is and what it is known to do | 3 |
| **Q** uncertainty | the ensemble baseline | 1 |
| **R** event-level evaluation | why a per-row score is not enough | 1 |

---

## 2. Thread by thread

### J. Conditional handover and lower-layer triggered mobility

Deb et al. (arXiv:2403.04379) model conditional handover as a discrete-time
Markov chain over the CHO execution and preparation offsets and timers, under
Rayleigh and Rician fading, validated against Python and ns-3 simulation. There
is no learned component and no measured data. It matters to us for one reason:
**CHO consumes a lead time, not a label.** A model that names the right cell but
names it 200 ms before the event buys nothing, because the preparation message
has to be sent, acknowledged and stored. This is the analytical justification
for reporting a lead-time distribution rather than a detection rate alone — and
it is the paper to cite when a reviewer asks why we bother with 2, 3 and 5 s
horizons when the A3 trigger fires at 480 ms.

Rel-18 lower-layer triggered mobility (Khodapanah, Goyal et al.) pushes the
cell-switch decision below RRC, which *shortens* the actionable horizon. The
naive reading is that this makes second-scale prediction obsolete. The correct
reading is the opposite: when the execution path gets faster, the binding
constraint moves from execution latency to **decision confidence**, which is
exactly what a calibrated hazard supplies and an uncalibrated classifier does
not. This entry is `verified=partial`; only the title, venue and first two
authors are confirmed.

### K. What the field says about itself

Two systematic reviews now corroborate, from outside, the complaint our protocol
audit makes from inside.

Ankome and Hanada (MAKE 8(5):133, 2026) screened 429 records, kept 336 after
deduplication and included 49 studies spanning 2010–2025 — signal-based 12%,
ML 37%, RL 27%, FL 12%, SDN 12%. Three of their findings are load-bearing for
us:

1. Heterogeneity of simulators and outcome definitions **prevented a
   meta-analysis outright.**
2. Most studies report *percentage improvements over paper-chosen baselines*
   rather than absolute performance.
3. Data splitting, class imbalance and calibration receive **minimal explicit
   discussion** across all 49.

Point 3 is the single most useful sentence the widened survey produced. It is a
third party, with a PRISMA protocol, saying what our audit column
`split_protocol = NOT STATED` says 12 times over.

Saoud et al. (Technologies 13(8):352, 2025) add that the field lacks
quantitative cross-comparison between strategies at all. Chabira et al.
(Technologies 13(7):276, 2025) enumerate the metric vocabulary actually in use —
handover failure rate, latency, QoS, energy — and neither calibration nor any
prevalence-aware ranking metric appears in it.

### L. Graph and trajectory models

This is where the strongest recent competitors are, and the news is mixed.

**TH-GCN** (Mehregan and De Grande, arXiv:2505.04894, IEEE DCOSS-IoT 2025)
builds a dynamic UE–cell graph for dense vehicular 5G. It is simulated, the
split protocol is not stated, and its headline results are relative deltas —
up to 78% fewer handovers, 10% better signal quality — against baselines it
chose. It is, almost line for line, the reporting style Ankome and Hanada
criticise.

**GRIMCELL** (Sánchez-Martín et al., MAKE 8(9):260, 2026) is the one that should
worry us, and does not. It runs XENet message passing over radio-planning,
configuration-management and performance-management data from a *commercial
LTE-A Pro network*, across 55 real deployment events. Operator-grade graph
learning on real data is clearly publishable. But it predicts post-deployment
KPIs **per cell, per day**. It is a planning tool. Nothing in it operates at the
per-second granularity a handover warning needs, and nothing in it is a
classification problem with a prevalence floor.

Dinh, Fazio and Voznak (PLOS ONE 21(8):e0355372, 2026) predict the next cell
sequence *and* the resource blocks it will need, from SUMO trajectories over a
real Singapore map, held out by travel day. Regression metrics — accuracy, R²,
MSE — so prevalence never enters. The held-out-by-day split is noted in §4
below.

Graser et al. (GeoInformatica 29(1), 2025) organise the trajectory-learning
literature by **data density** rather than architecture, which is a more useful
axis than it sounds: our 1 Hz drives sit at the dense-individual-trace end, and
the review observes that this is precisely where the literature is thinnest for
*event* prediction as opposed to location prediction.

### M. Conformal prediction inside wireless — and what we can no longer claim

Cohen, Park, Simeone and Shamai (arXiv:2212.07775) apply split and
cross-validation conformal prediction to demodulation, modulation
classification and channel prediction. Simeone, Park and Zecchin
(arXiv:2504.09310) generalise it into a lifecycle: pre-deployment calibration
and hyperparameter selection, deployment-time monitoring under distribution
shift, post-deployment counterfactual analysis.

So **conformal prediction in wireless is established work by a strong group, and
we must stop implying otherwise.** What survives, and is genuinely ours:

- their guarantee is over *prediction sets* for tasks that are i.i.d. within a
  frame; ours is a **risk** guarantee on a KPI — missed handovers — over a
  stream that is exchangeable only at the level of a whole drive;
- the unit of exchangeability is the thing a reviewer will attack, and no
  wireless conformal paper we found defends one;
- neither paper reports a mobility-management case at all.

The claim narrows from "we bring conformal guarantees to handover prediction"
to "we identify the exchangeability unit that makes a conformal risk bound
meaningful for drive-test mobility data, and we report the feasibility floor
n ≥ 1/α − 1 that follows from it." That is a smaller claim and a defensible one.

### N. Survival, and the same narrowing in a gentler form

Wiegrebe et al. (AI Review 57(3):65, 2024) review 61 deep time-to-event methods.
Discrete-time survival — binary indicators per interval, trained as
classification — is a **mainstream branch**, not an improvisation. Thorsen-Meyer
et al. (npj Digital Medicine 5:142, 2022) build exactly our object in intensive
care: a multilabel head over discretised windows with a censoring-aware
log-likelihood.

This cuts both ways and we should say so. It removes any claim that the
*formulation* is novel. It also removes the reviewer question "why have you
invented this?", and gives us a literature to point at when we argue that
per-horizon independent heads are the wrong default.

One deliberate departure worth defending in the manuscript: the survival
literature evaluates with the C-index and the integrated Brier score, both of
which aggregate over the horizon axis. We report horizon-wise AUPRC plus a
coherence-violation rate, because **an operator acts at one horizon**, and a
model that ranks well on average while producing P(event by 1 s) > P(event by
3 s) on 47% of rows is not deployable regardless of its C-index.

### O. Point processes, and why we ran the residual test

Laub, Lee, Pollett and Taimre (Annual Review of Statistics and Its Application
12:233–258, 2025) is now the reference treatment: construction, simulation,
multivariate, marked and spatiotemporal extensions. It replaces our reliance on
Hawkes (1971) alone for the modelling claims and is the cleanest citation for
the branching-ratio interpretation.

Price-Williams and Heard (Statistics and Computing 30(2):209–220, 2020) is the
precedent that matters more. They fit a Wold process with a monotone step
excitation to network traffic from Imperial College and Los Alamos, and
**validate it by time-rescaling with Kolmogorov–Smirnov tests on held-out
data.** In networking, a self-exciting fit is expected to be *checked*. Our
Ogata residual test is not a flourish; it is the local standard, and this is the
citation for it.

### P. Domain adaptation, and why our null result is not an implementation bug

Sun and Saenko (ECCV 2016 Workshops, LNCS 9915:443–450) is the primary source
for Deep CORAL, which stage 19 implements. Citing the primary source matters
more than usual here because we report a **negative** result with it.

Ismail Fawaz et al. (arXiv:2312.09857, Ericsson Research) benchmark nine
unsupervised domain-adaptation algorithms over twelve time-series datasets and
find that several published methods — VRADA and CoTMix among them — perform
*worse than source-only training with no adaptation at all*, and that the
adaptation technique rather than the backbone drives the outcome. Our measured
CORAL null is therefore consistent with a published benchmark rather than
evidence that we implemented it wrong. Shi, Ying and Yang (Sensors 22(15):5507,
2022) supply the taxonomy that lets us name the shift we face — device and day,
not sensor modality — and justify per-drive z-scoring as the cheap baseline it
is.

### Q. The ensemble baseline

Lakshminarayanan, Pritzel and Blundell (NIPS 2017) had no entry at all, despite
the ensemble being our uncertainty baseline before conformal. Fixed.

### R. Event-level evaluation

Wagner et al. (arXiv:2510.17562) show formally that the common point-adjusted
time-series anomaly metrics each satisfy only a few desirable properties and
none satisfy all — which is why published comparisons in that field disagree
with each other. This is direct support for reporting event-level detection
rate, lead time and false alarms per hour and per km **alongside** row-level
AUPRC rather than instead of it: no single aggregate is trustworthy, so we
publish the pair and let the reader see both. Entry is `verified=partial` — a
24-author list, of which three are confirmed here.

---

## 3. What the widened audit now shows

Twenty-two competitor rows, recounted from `protocol_audit.csv` rather than
carried forward from doc 21. Counting rules are stated because the previous
version of this table was loose about them.

| column | of 22 | counting rule | change |
|---|---|---|---|
| split protocol **not stated at all** | 10 | the field reads NOT STATED / NOT VERIFIED; an 11th (A06) says "two separate sets, unspecified" | +3 |
| split **coarser than a random row** | 5 | a unit larger than a row held out whole: spatial zone, device, rolling origin, travel day, deployment event | **+2** |
| prevalence-aware **ranking** metric | 2 | AUPRC / AP / PR curve. A further 4 report precision and recall at one threshold, which is not a ranking metric | unchanged |
| accuracy reported on imbalanced data | 7 | includes 98.03%, 99.84% and 94.83% headline accuracies | +0 |
| any uncertainty artefact at all | 3 | CIs over repeats (A11), bootstrap CI on AUC (A12), threshold tuning (A15) | unchanged |
| a **calibration** curve, ECE or Brier score | **0** | — | unchanged |
| lead-time distribution or false alarms per hour/km | **0** | 4 report something event-adjacent: alarm-confirmation policies, missed-HO rate, CHO preparation success, HOF probability | unchanged |
| real measured data, not simulated or testbed | 7 | +1 testbed-only (A23), +1 unverified claim of real data (A10) | +1 |
| code released | 2 | +1 "on request" (A12) | unchanged |
| data released | 1 | +1 "on acceptance" (A22) | unchanged |

The rows that did not move are the interesting ones. Adding five papers,
including two on real operator data, changed **nothing** about calibration,
event-level evaluation, code release or data release. Across twenty-two papers
on predicting a rare mobility event: two use a ranking metric that survives
class imbalance, **none** reports a calibration curve, and **none** reports how
early its warnings arrive.

---

## 4. Two claims that have to narrow

**C13 — grouped splitting.** Doc 21 already amended this once: Hasan et al.
(A16) split temporally by rolling origin. The enlarged set adds two more
non-random splits — Dinh et al. (A26) hold out by *travel day*, and GRIMCELL
(A29) holds out by *deployment event*. Both are grouped splits in the broad
sense: a unit larger than a row is held out whole.

The honest form of C13 is now:

> Of 22 audited papers, 10 do not state a split protocol at all and 5 use a
> split coarser than a random row. Of those 5, none holds out the **mobility
> unit** — a whole drive, or a whole device-session — for a per-timestep
> classification task on measured radio data. Amirova et al. (A12) come closest
> with a device-level hold-out.

That is weaker than "we are the only ones", and it is what the evidence
supports. It is also still enough to carry §16, because §16's result — that
leakage from random-row splitting is *architecture-dependent*, inflating GRU
AUPRC by 92% and logistic regression's by 12% — does not depend on scarcity. It
depends on the effect being real and being differential, which we measured.

**C-conformal.** See §2M. "Conformal guarantees for handover prediction" becomes
"the exchangeability unit and the feasibility floor for conformal risk control
on drive-test mobility data". Cohen et al. and Simeone et al. must be cited in
the same paragraph that introduces our conformal section, not buried in related
work.

---

## 5. Four claims the widened survey strengthens

1. **Real measured data is the scarce resource.** Asif et al. report 82.6% of
   surveyed studies rely on simulated datasets; Ankome and Hanada say evidence
   quality is limited by simulation-based assessment and few real datasets. Two
   independent reviews, same conclusion.
2. **Reporting practice is the field's known weak point.** Ankome and Hanada
   could not run a meta-analysis *because* of it, and name relative-delta
   reporting explicitly. Our absolute numbers with bootstrap intervals are not
   fussiness; they are the thing the reviews ask for.
3. **The CORAL null is a finding, not a bug** (Ismail Fawaz et al.).
4. **Validating the Hawkes fit is the local norm** (Price-Williams and Heard),
   so reporting the residual test is expected rather than defensive.

---

## 6. Corrections made to the existing bibliography

Four entries were patched in place; `references.bib.bak` holds the originals.

| key | what was wrong | now |
|---|---|---|
| `survey2024mlhandover` | **no author list at all** | Thillaigovindhan, Roslee, Mitani, Osman, Ali |
| `asif2026aimobility` | first author truncated to "Asif," with no given name | Asif, Hafiz M.; Bait-Suwailam's initial added |
| `benzaghta2025bohandover` | second author truncated to "Ammar," | Ammar, Sahar; entry upgraded to `verified=full` |
| `ankome2026review` | note carried one statistic | screening counts, taxonomy shares and the three findings in §2K |

Running total across three passes: **eight citation errors found and fixed in
our own bibliography.** Two of them — a missing author list and a truncated
surname — would have been caught by any copy-editor. The other six would not.

---

## 7. What is still unverified

Four entries carry `verified=partial` for a reason a reviewer could probe, and
all four must be completed before submission:

| key | what is missing |
|---|---|
| `khodapanah2024ltm` | author list beyond the first two; IEEE Xplore was not retrievable |
| `thorsenmeyer2022discrete` | full author list — the publisher page truncates with *et al.* |
| `wagner2025tsadmetrics` | tail of a 24-author list |
| 11 others from passes 1–2 | see the `verified=partial` tags in `references.bib` |

None of them is load-bearing for a *result*; all four are cited for context or
method provenance. But the verification policy in the `.bib` header says
anything not `verified=full` gets re-checked, and that policy is worth more than
the four entries.

---

## 8. What this changes in the manuscript

- **§25** gains the thread structure above and the narrowed C13 wording.
- **§12** (distribution-free risk control) must open by citing Cohen et al. and
  Simeone et al., and state the narrowed claim in its first paragraph.
- **§7** (the survival formulation) gains Wiegrebe et al. and Thorsen-Meyer et
  al., and should say plainly that the formulation is standard elsewhere and
  new *here*.
- **§13/§22** (point process) gains Laub et al. for the model and
  Price-Williams and Heard for the validation norm.
- **§19** (transfer) gains Sun and Saenko for the method and Ismail Fawaz et al.
  for why the null is credible.
- **§11** (metrics) gains Wagner et al. for the event-level pair.
- **§27** (limitations) gains one line: two more audited papers use a
  non-random split than doc 21 knew about.

Nothing in the results changes. Six sections get a better-defended argument and
two claims get smaller.

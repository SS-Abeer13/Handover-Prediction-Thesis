# Closing the outstanding items: adaptation, the departmental baseline, and a bibliography that survives a reviewer

Doc 20 §11 left four technical items open and a literature pass unfinished. This
document reports **I**, **K**, **L** and **literature pass 2**. Item **M** is
field work and is the only one left.

```
I  equal tuning budget (nested grouped CV)     DONE      §5 - OBJECTION GRANTED AND SURVIVED
K  per-drive z-scoring / CORAL transfer        DONE      §2 - BOTH ADAPTATIONS HURT
L  FinalManuscript model under our protocol    DONE      §3 - new positioning result
   literature pass 2                           DONE      §4 - one venue error, three
                                                               author-list errors fixed
M  one more capture day                        field work
```

The short version: **two more measured negatives, one conceded objection that
does not survive being granted, and a bibliography four errors safer.** Zero-cost
domain adaptation makes every transfer we report *worse*, which is the fifth
independent instance of this paper's own pattern. The departmental manuscript's
method, reimplemented and run on our data, predicts handovers at AUROC 0.49–0.58
where the same rows give LightGBM 0.921 — and, more usefully, ranking by its own
reward function directly beats its Q-learning agent, which is the empirical form
of the criticism doc 11 could previously only argue. And on an equal 20-trial
budget the deep baselines really were under-tuned - a Transformer gains +0.109
AUPRC - and still finish below an *untuned* logistic regression, while tuning
LightGBM makes it slightly worse.

---

## 1. What was built

Three new pipeline stages, all reproducible from `configs/` plus the staged raw
captures:

```
stage18_tuning_budget          nested grouped CV, equal Optuna budget per model  (item I)
stage19_transfer_adaptation    per-drive z-scoring and CORAL on both transfers   (item K)
stage20_departmental_baseline  Shafi et al. reimplemented under both protocols   (item L)
```

Every stage was run against the pooled XCAL dataset rebuilt from scratch by
`stage12`. The rebuild reproduces doc 20 exactly — 7,740 samples, 43 drives, 761
handovers, prevalence 0.0423 / 0.0732 / 0.1356 / 0.1890 / 0.2771 — so nothing
below rests on a stale artefact.

---

## 2. Item K: both zero-cost adaptations make transfer worse

### What was tried

Two unsupervised adaptations, chosen because they cost nothing at deployment and
because a reviewer will name them:

| method | what it does | what it uses from the target |
|---|---|---|
| `per_drive_z` | standardises each drive by its own median and IQR-scale, on both sides | that drive's own **features** only |
| `coral` | whitens the target by the target covariance, recolours by the source covariance, matches means | the target domain's **features** only |

Neither touches target labels, and neither fits a model on the target side. The
`none` arm is exactly the protocol of stages 07 and 08, so the arms differ only
by the adaptation. LightGBM throughout; the same held-out drives on every arm.

### Result, 1 s horizon

| setting | adaptation | matched AUROC | transfer AUROC | gap |
|---|---|---|---|---|
| **regime** (within campaign) | **none** | 0.819 | **0.865** | **−0.046** |
| | per_drive_z | 0.796 | 0.699 | +0.097 |
| | coral | 0.800 | 0.771 | +0.030 |
| **external** (ours ↔ public IUT) | **none** | 0.848 | **0.642** | **+0.206** |
| | per_drive_z | 0.809 | 0.567 | +0.242 |
| | coral | 0.848 | 0.534 | +0.315 |

AUPRC tells the same story, more sharply: on regime transfer the untreated arm
reaches 0.782 and the two adapted arms 0.494 and 0.388.

At 2 s the ordering is unchanged (regime gap: none +0.030, coral +0.081,
per_drive_z +0.089).

### Why, and what to claim

The adaptations do not trade in-domain accuracy for transfer — they lose on
**both** sides (matched AUROC 0.819 → 0.796 / 0.800). That rules out the
charitable reading and points at the mechanism: on this problem the *absolute
level* of the radio features carries the signal. A serving RSRP of −112 dBm
means something in itself; per-drive z-scoring deletes exactly that and keeps
only within-drive shape. CORAL's failure is the same fault in second-moment
form — it rotates and rescales the target into a geometry the source-fitted
trees never split on.

> **Claim to make.** Two standard zero-cost domain adaptations — per-drive
> standardisation and CORAL — were applied to both transfer settings under an
> otherwise identical protocol. Both *reduce* transfer performance (regime
> transfer AUROC 0.865 untreated vs 0.771 and 0.699; external transfer 0.642 vs
> 0.534 and 0.567), and both also reduce matched-domain performance. Feature
> alignment removes the absolute-level information the task depends on. We
> therefore report untreated transfer as the honest number and do not claim a
> domain-adaptation contribution.

This is the **fifth** measured channel that does not help, after neighbour
coverage, self-excitation features, the full signalling channel and a dedicated
ping-pong target. The pattern in doc 20 §24 gains a line:

```
  zero-cost domain adaptation (z-score, CORAL)   ...worse, on both sides
```

### One caveat to carry

The external numbers here (matched 0.848, transfer 0.642) are **not** comparable
to doc 12's 0.752 — that figure came from a different protocol (temperature
scaling, a different feature set and a single locked direction). Stage 19's
numbers are only ever to be read *across adaptations within the stage*. Doc 12
remains the citable external-validation result.

`reports_xcal/tables/transfer_adaptation.{csv,md,tex}` and `_summary`.

---

## 3. Item L: the departmental method, reimplemented and measured

### What was implemented

`FinalManuscript.pdf` (Shafi, Istiaque, Sowad, Kawser — IUT EEE) specifies its
method completely enough to reimplement, and stage 20 does so from Section III
and Algorithm 1 without substitution:

* **state** `s = [serving RSRP, serving RSRQ, neighbour RSRP, neighbour RSRQ,
  serving CINR]`, StandardScaler fitted on the training set
* **reward** their exact piecewise function, HOM = 3 dB, TTT = 1 s, rewards in
  {−20, −8, −5, −4, +1, +3, +5}
* **agent** tabular Q-learning, α = 0.1, γ = 0.9, ε 1 → 0.01 at decay 0.995,
  10,000 episodes, Q initialised to zero
* **inference** 1-nearest-neighbour lookup of the test state into the Q-table
  keys, plus their external TTT filter

Three decisions had to be made to compare a decision rule against a forecaster,
and each was made in their favour:

1. **Scoring.** Their output is an action; ours is a probability. The agent is
   scored by its **advantage** `Q(s,1) − Q(s,0)` — the full learned signal, not
   the thresholded action.
2. **Rows.** Their dataset is event-triggered, so every row carries a neighbour
   measurement; on our 1 Hz grid only 58.9% do. Every model here is trained and
   scored on **neighbour-present rows only**, and our LightGBM is restricted to
   exactly the same rows.
3. **The TTT gate.** Walked over our 1 Hz grid it is stringent (it fires on 0.6%
   of rows); at their row spacing of ~0.24 rows/s the same loop usually breaks
   before testing anything, so it is nearly vacuous on their own data. Both
   readings are run (`gate_mode = grid` and `hom_only`) and the more favourable
   one is quoted below.

### Result, 1 s horizon, our grouped-drive rotation

| model | AUPRC | lift | AUROC | recall @ FPR 5% |
|---|---|---|---|---|
| **ours, LightGBM, 107 features** | **0.824** | **6.95×** | **0.921** | 0.760 |
| ours, LightGBM on *their* 5-D state | 0.473 | 3.99× | 0.766 | 0.373 |
| rank by their reward directly (no RL) | 0.162 | 1.29× | 0.614 | 0.041 |
| **their Q-agent** | 0.146 | 1.17× | **0.505** | 0.077 |
| their Q-agent + their TTT filter | 0.138 | 1.09× | 0.523 | 0.075 |
| their HOM/TTT gate alone | 0.134 | 1.07× | 0.523 | 0.000 |

Under **their** design (train 10 Sept → test 12 Sept, train 13 Sept → test
12 Sept — the analogue of their Day 1 → Day 2 and Day 3 → Day 2) the ordering is
identical: ours 0.754 AUPRC / 0.891 AUROC, their agent 0.129–0.138 / 0.57–0.58.

### The three findings worth putting in the paper

**3.1 The gap is the method, not the features.** Their five features are
informative: our own learner on that exact 5-D state reaches AUROC 0.766. Their
agent extracts AUROC 0.505 from the same five numbers. Roughly half the total
gap to our full model is feature poverty; the other half is that the method
discards most of what its own inputs carry.

**3.2 The RL machinery is doing negative work.** Ranking by
`r(s,1) − r(s,0)` — the reward function evaluated directly, with no Q-learning,
no episodes and no table — scores **AUROC 0.614 against the trained agent's
0.505**. Doc 11 §3.3 argued that "tabular" Q-learning over continuous keys
reduces to 1-NN regression on a closed-form reward; this measures it, and finds
the RL step is not neutral but lossy. Stated carefully:

> Their policy is a deterministic function of a hand-specified reward over five
> features. Ranking by that reward directly outperforms the learned Q-table it
> is used to train (AUROC 0.614 vs 0.505 on the same rows), so the reinforcement
> learning contributes nothing that the reward function does not already
> contain, and the nearest-neighbour projection of a sparsely-visited table
> loses signal relative to the reward itself.

**3.3 Their evaluation consumes the future.** The published TTT filter accepts
an action only if the HOM condition persists for TTT seconds *after* the
decision instant. For a handover *decision* this is legitimate — the network
does wait. Used to license a prediction it means the "prediction" at *t* is
really made at *t* + TTT. We report both variants and label them; neither
changes the conclusion.

### How to frame it, and what not to say

This is not a like-for-like defeat of their paper on its own task. They optimise
a **decision**; we forecast an **event**. What stage 20 establishes is narrower
and fairer: *used as a predictor of handover imminence on signalling ground
truth, their method is close to uninformative, and the learned component of it
is worse than its own hand-written reward.* That, plus doc 11 §2.1 (their
HOM = 3 dB assumption is not the network's deployed configuration: the measured
offsets are −15, −10, +1 dB), is the positioning paragraph.

`reports_xcal/tables/departmental_baseline.{csv,md,tex}` and `_summary`.

---

## 4. Literature pass 2

### 4.1 Eighteen entries verified, four errors found

`verified=full` went from 55 to 72 entries; 14 remain (§4.4). Four of the
corrections would have cost credibility with a reviewer:

| entry | pass-1 record | what it actually is |
|---|---|---|
| `lee2020cho` | *IEEE **Transactions** on Vehicular Technology*, two authors "Lee and Cho" | **IEEE Vehicular Technology *Magazine*** 15(1):54–62, **four** authors — Changsung Lee, Hyoungjun Cho, Sooeun Song, Jong Moon Chung. DOI 10.1109/MVT.2019.2959065 |
| `alkhateeb2018blockage` | three authors | **two** — Alkhateeb and Beltagy. The third was not on the paper |
| `panitsas2024predictive` | title *"Predictive Handover Strategy in 6G and Beyond"* | **retitled between versions** to *"A Deep and Transfer Learning Approach for Handover Management in O-RAN"*; cite the current title |
| `stgnn2023handover` | `booktitle = {IEEE}`, no authors | Djuikom Foka, Stanica, Naboulsi — **NoF 2023**, Izmir, pp. 80–88, DOI 10.1109/NoF58724.2023.10302814 |

Also resolved: `transformer2024rlf` has a **journal version** (IEEE Xplore
11018489, *A Generalized GNN-Transformer-Based RLF Prediction Framework in 5G
RAN*) that should be cited instead of the preprint; `hgclstm2025` is *Computer
Networks* **270**:111497 by the same three authors as the NoF paper; and the
three papers read in full in doc 17 (`deng2018mobilityconfig`,
`zidic2023pingpong`, `ghoshal2025handoverconfigs`) had stale `verified=partial`
notes that said their content had not been retrieved.

### 4.2 The protocol audit is now 17 papers, not 11

Method extraction was completed for the thread-A papers doc 16 left pending. Six
new rows (A15–A17, A22–A24) and method detail folded into five existing ones.
Recounted over **17** audited papers:

| protocol property | papers doing it | this work |
|---|---|---|
| splits by **drive or route** | **0 / 17** | yes, every experiment |
| any grouped or temporal split at all | **3 / 17** — A07 spatial zone, A12 device, A16 time | yes |
| reports a prevalence-aware metric | 2 / 17 | AUPRC + floor + lift |
| reports calibration or uncertainty | **0 / 17** | ECE, Brier, temperature scaling, conformal risk control |
| reports event-level false alarms per hour | **0 / 17** | yes, and per km |
| reports headline accuracy on an imbalanced task | 7 / 17 | never |
| releases code | 2 / 17 | planned |
| releases data | 1 / 17 | planned |

**C13 needs one honest amendment.** The pass-1 claim was "0/11 split by
drive/route/time". One paper in the enlarged set — Hasan et al., real Turkcell
data, 1.8M samples — does split by **time**, with a rolling-origin 5-fold
protocol. Its task is next-day cell-level RLF rather than a per-sample mobility
forecast, so whether it belongs in the comparable set is a judgement call. Make
the call in the open:

> Of 17 audited learned-prediction papers, none splits by drive or route; one
> splits temporally (on a cell-day rather than a per-sample task), one by
> spatial zone and one by device. None reports calibration, and none reports
> event-level false alarms per hour.

That is a weaker headline than "0/11" and a far harder one to attack — and
naming the one paper that does it right is what makes the rest of the audit
credible.

### 4.3 Two findings from the extraction worth a sentence each

**The grouped-split papers are the simulated ones.** A07 (GeoLife traces +
DeepMIMO ray tracing) and A16 (operator KPI aggregates) have the cleanest
protocols in the set and the least measured radio. The papers with real
per-sample drive-test data — A01, A02, A12, A23 — are the ones whose split is
"NOT STATED". Protocol quality and measurement quality are anti-correlated in
this literature, which is precisely the gap this thesis sits in.

**The newest real-data papers are dataset releases without baselines.** A22
(IIT Madras, 117,390 measurement reports, 1,546 A3 handovers, Chennai) proposes
handover prediction as a task and trains nothing. Our pipeline on our own
captures is, as far as this screening shows, the only per-sample handover
forecast on signalling-confirmed ground truth with a grouped protocol.

### 4.4 What is still unverified

Fourteen entries remain `verified=partial` or `id-only`, none of them load-
bearing: `paropkari2022deepmobility`, `chien2024federated`, `sun2025proactive`,
`intime2025cho`, `residuallstm2024mobility`, `sulaiman2025predictive`,
`preho2026leo`, `wiedner2026vienna`, `alizadeh2025offlinemro`,
`benzaghta2025bomobility`, `benzaghta2025bohandover`, `liu2024m2ho`,
`ghoshal2025handoverconfigs` (venue only — the content is read),
`oran2024connectedvehicles` (resolved, note pending). Publisher sites
(ScienceDirect, IEEE Xplore, PMC) block automated retrieval from this
environment; these need a browser session or an institutional login. **None
should reach submission unchecked.**

---

## 5. Item I: an equal tuning budget, and what it costs the objection

### Protocol

The stage-13 grouped 5-fold rotation as the outer loop; `GroupKFold(3)` over the
training drives of each outer fold as the inner loop; **20 Optuna trials for
every model**, the same objective (mean inner AUPRC at the 2 s horizon), median
pruning on the inner-fold running mean; the winning parameters refit on the whole
outer-train and scored once on the held-out fold. Test drives never enter a
search. The default arm is re-run in the same stage rather than copied from doc
20, so both arms share fold assignment, seed and code path.

**The default arm reproduces doc 20 to three decimals on every model** - logreg
0.741 / 0.920, LightGBM 0.800 / 0.933, MLP 0.689 / 0.913, GRU 0.486 / 0.863 -
which validates the harness before any tuned number is read.

### Result, 1 s horizon, out-of-fold over 43 drives

| model | AUPRC default → tuned | AUROC default → tuned | ECE default → tuned |
|---|---|---|---|
| **LightGBM** | **0.800 → 0.779** | 0.933 → 0.925 | 0.025 → 0.019 |
| logistic regression | 0.741 → **0.770** | 0.920 → 0.926 | **0.123 → 0.010** |
| MLP | 0.689 → 0.693 | 0.913 → 0.916 | 0.080 → 0.115 |
| Transformer | 0.570 → **0.679** | 0.859 → 0.901 | 0.086 → 0.064 |
| TCN | 0.531 → **0.633** | 0.867 → 0.893 | 0.095 → 0.080 |
| GRU | 0.486 → **0.536** | 0.863 → 0.874 | 0.126 → 0.140 |

Paired delta AUPRC, tuned minus default, with a drive-level bootstrap CI at 1 s:

| model | 0.5 s | **1 s** | 2 s | 3 s | 5 s | CI at 1 s |
|---|---|---|---|---|---|---|
| Transformer | +0.066 | **+0.109** | +0.067 | +0.049 | +0.040 | [+0.067, +0.148] |
| TCN | +0.091 | **+0.102** | +0.030 | +0.040 | +0.021 | [+0.074, +0.130] |
| GRU | +0.036 | **+0.050** | +0.025 | +0.027 | +0.020 | [+0.022, +0.082] |
| logistic regression | +0.017 | **+0.029** | +0.012 | +0.008 | +0.003 | [+0.021, +0.038] |
| MLP | +0.044 | +0.004 | +0.014 | +0.012 | +0.011 | [−0.015, +0.024] |
| **LightGBM** | +0.025 | **−0.021** | −0.002 | +0.016 | +0.016 | [−0.031, −0.008] |

### What this settles, and what it concedes

**The objection was partly right, and it does not survive being granted.** The
sequence models *were* under-tuned: a Transformer gains +0.109 AUPRC at 1 s and a
TCN +0.102, both far outside their confidence intervals. Concede that plainly.
Then give the ranking under an equal budget, every model tuned the same way on
the same folds:

```
  LightGBM      default 0.800   tuned 0.779
  logreg        default 0.741   tuned 0.770
  MLP                           tuned 0.693
  Transformer                   tuned 0.679
  TCN                           tuned 0.633
  GRU                           tuned 0.536
```

**A tuned Transformer does not reach an untuned logistic regression.** The gap
between the best snapshot model and the best sequence model narrows from 0.229 to
0.100 AUPRC and does not close, and the ordering - snapshot above sequence - is
unchanged at every horizon.

**Tuning LightGBM makes it slightly worse.** −0.021 AUPRC at 1 s, CI excluding
zero, positive at 0.5, 3 and 5 s, a wash overall. With 43 drives a 20-trial inner
search cannot improve on the coded defaults and sometimes overfits the inner
rotation. That is worth one sentence: the headline model is not winning because
its defaults happened to suit it, because its defaults are not beatable by the
same search that lifts every competitor.

**One published number needs a footnote.** Logistic regression's ECE of 0.123 in
doc 20 is an artefact of `class_weight='balanced'`, which the search turns off:
tuned ECE is **0.0098**, a twelve-fold improvement, at a *gain* of 0.029 AUPRC.
The linear baseline was handicapped on calibration and the paper should say so
rather than let a reviewer find it. Note the direction of this: it makes the
strongest non-hazard baseline *better calibrated than LightGBM* (0.010 vs 0.019),
which sharpens rather than weakens C1 - the hazard model's contribution was never
that nothing else can be calibrated, but that it gets calibration, coherence and
ranking from one fit without spending a calibration split.

### The rewritten claim

> Every model was given the same tuning budget - 20 Optuna trials under nested
> grouped cross-validation, inner `GroupKFold(3)` on training drives only,
> objective mean inner AUPRC at 2 s. Tuning lifts the sequence models
> substantially (Transformer +0.109, TCN +0.102, GRU +0.050 AUPRC at 1 s, all
> CIs excluding zero) and leaves the ordering unchanged: the best tuned sequence
> model reaches AUPRC 0.679 against 0.779 for a tuned and 0.800 for an untuned
> LightGBM, and does not reach the 0.741 of an untuned logistic regression.
> Tuning LightGBM itself yields −0.021 at 1 s, so the primary model's margin is
> not an artefact of favourable defaults.

`reports_xcal/tables/tuning_budget_all.{csv,md}` and `_delta`; per-fold chosen
parameters in `artifacts_xcal/tuning_budget{,_deep}.json`.

---

## 6. What changes in the manuscript

1. **§24 contributions** gain a fifth "measured nothing" channel (adaptation,
   §2) and C13 is restated over 17 papers with the temporal-split exception
   named (§4.2).
2. **§25 positioning** gains the departmental comparison as a measured result
   rather than an argument, including the reward-beats-its-own-agent finding
   (§3.2), and the observation that protocol quality and measurement quality are
   anti-correlated in this literature (§4.3).
3. **§19 transfer** states untreated transfer as the reported number, with
   adaptation reported as a tried-and-failed arm rather than omitted.
4. **§15 model comparison** gains the tuned arm as a second block (§5): the
   ordering is unchanged, the sequence-model gap narrows from 0.229 to 0.100
   AUPRC, and the logistic-regression ECE of 0.123 is footnoted as a
   `class_weight` artefact that tuning removes (0.0098).
5. **The bibliography** is four corrections safer, and 14 entries still need a
   browser.

---

## 7. What is left

```
M  one more capture day        field work, unchanged
   14 bibliography entries     need a browser session (publisher blocks)
   THE MANUSCRIPT              not started
```

Every item in doc 19 that could be closed at a desk is closed.

The bottleneck has still not moved. It is the writing.

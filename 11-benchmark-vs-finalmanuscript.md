# Benchmark against `FinalManuscript.pdf` — where your work is stronger, and where it is not

The manuscript: *Handover Optimization in LTE Networks Using Contextual Bandit
Reinforcement Learning and Real-World Data* — Shafi, Istiaque, Sowad and Kawser,
EEE, IUT. Six pages, IEEE conference format, 26 references. Grameenphone LTE,
Dhaka, XCAL-M on a Galaxy S10, three evening drives on a 13 km Uttara–BRAC route.

**Read this first: it is the same department and the same supervisor, on the
same operator, in the same city, with the same tool.** That makes it your closest
comparator, your most likely reviewer, and a possible overlap risk. It also makes
their published dataset directly useful to you — see §5.

---

## 1. The two studies side by side

| | **FinalManuscript** | **Your work** |
|---|---|---|
| Task | Handover **decision** (act / don't act) | Handover **forecasting** (1/2/3/5 s ahead) |
| Method | Tabular Q-learning as a contextual bandit | 6 model families + rule baseline, multi-horizon |
| Data | 2,155 points, 367 HOs, 3 evening drives, 1 route | 81k curated samples + 43 signalling drives, 761 attributed HOs, 4 captures |
| Ground truth for HOs | Serving-cell change in the XCAL export | **RRC `mobilityControlInfo`**, 100% signalling-confirmed |
| Mobility parameters | HOM = 3 dB, TTT = 0.7/1.0 s — **assumed constants** | **Measured from `measConfig`**: offsets −15/−10/+1/+5 dB, TTT 160–640 ms, 100% attributed |
| Train/test split | Day 1 → Day 2; Day 3 → Day 2 | Grouped whole-drive, 4-way (train/val/calib/test) + locked external route under freeze manifest |
| Uncertainty | none | deep ensembles, temperature scaling, split conformal (coverage 0.891–0.912), abstention |
| Statistics | none — no CIs, no tests | drive-level cluster bootstrap, paired permutation, Holm correction |
| Leakage analysis | none | quantified and architecture-dependent (GRU +109% AUPRC vs LightGBM +12%) |
| Data authenticity | assumed | reproducible audit module, validated against real controls |
| Baselines compared | **none** (only raw HO count) | A3 rule, logreg, LightGBM, GRU, TCN, Transformer |
| Outcome metric | HO count only | AUPRC + lift, AUROC, recall@FPR, event detection, lead time, FA/hour and /km, ECE, Brier |
| Deliverable | **finished 6-page paper + Mendeley dataset with DOI** | pipeline + 11 internal reports, **no manuscript, no data release** |

---

## 2. Where you are clearly ahead

**2.1 You measure what they assume.** Their entire reward gate is HOM = 3 dB and
TTT = 0.7–1.0 s. Your signalling parse shows Grameenphone actually runs **four A3
profiles concurrently**, with offsets from −15 dB to +5 dB and TTT from 160 ms to
640 ms. A **negative** offset means the network hands over to a *worse* neighbour.
So a 3 dB positive margin does not describe the network they measured, on the
carriers they measured it on. Their agent is optimising against a rule the network
is not running. This is the single most defensible advantage you have, and it is
verifiable from the same raw logs they collected.

**2.2 Their evaluation cannot detect the failure mode you quantified.** Day 2 is
the test set in *both* of their configurations, so the two "cases" are not
independent evidence. There is no validation set, no held-out route, no
confidence interval, and n = 1 test trace. Your grouped-drive protocol, freeze
manifest and cluster bootstrap exist precisely to prevent the conclusions this
setup would license.

**2.3 Ground truth.** They label handovers from serving-cell changes in the CSV.
Your own measurement says that at 1 Hz **only 44–58% of signalling-confirmed
handovers appear as a cell change within 2 s** on this network. Their 99/150/118
HO counts are therefore likely undercounts of the true event set, by a factor you
have measured and they have not.

**2.4 You have a negative-result discipline they do not.** You void your own
synthetic-data results, you find and fix a leak in your own experiment, and you
report falsified hypotheses. That is rarer than it should be and it is exactly
what a Q1 methods reviewer rewards.

---

## 3. Four problems in their paper a Q1 reviewer would raise

Useful to you twice: as positioning, and as a checklist of traps to avoid.

**3.1 The evaluation is circular.** The agent is rewarded for suppressing
handovers, and success is measured by the number of handovers suppressed. "The
optimized HO count aligned with the reward function's objectives" restates the
reward. There is no external outcome anywhere in the results — no throughput, no
RLF or drop rate, no latency, no ping-pong measured independently of the reward.
So the paper cannot say whether the suppressed handovers were actually
unnecessary.

**3.2 The model contradicts its own framing.** The paper states the problem is a
contextual bandit — "each entry is a timestamped but independent snapshot, with
no influence on future states" — and then applies the full Q-learning update with
γ = 0.9 and a `max_a' Q(s', a')` bootstrap over a next state it has just declared
does not exist. One of the two is wrong.

**3.3 "Tabular" Q-learning over continuous keys is not tabular.** The Q-table is
keyed by standardized 5-D continuous vectors, so essentially every key is unique
and is visited only through repeated sampling of the same row. At test time,
nearest-neighbour lookup into that table reduces to **1-NN regression on a
deterministic, hand-written reward function**. Since the reward is a closed-form
function of the same five features, the learned policy can be computed directly
without any RL. The RL machinery is doing no work that the reward function is not
already doing.

**3.4 No baseline and no statistics.** Nothing is compared against the 3GPP A3
rule, a fixed HOM/TTT policy, or any supervised model. The reward magnitudes
(−20, −8, −5, +1, +3, +5) are unjustified and never subjected to sensitivity
analysis. There are no confidence intervals and no significance tests.

None of this makes the paper worthless — it is a reasonable conference
contribution. But it sets the bar you have to clear, and you clear it on protocol
already.

---

## 4. Where they are ahead of you — read this part twice

**4.1 They have a paper. You have a pipeline.** Six pages, submitted shape, clean
narrative, 26 references. You have 11 internal reports and no manuscript. For the
thesis timeline this is the gap that matters most.

**4.2 Literature engagement is your biggest deficit.** Their related-work section
covers 25 papers in four organised threads: drive-test characterisation,
metaheuristic optimisation, fuzzy/HCP self-optimisation, and ML/RL handover.
**Your project documents cite almost nothing.** For a Q1 journal you need roughly
40–60 references with a defensible positioning statement, and right now you
cannot state what is novel relative to the field — only relative to your own
earlier runs. This is the difference between "careful engineering" and "research
contribution", and reviewers apply it first.

**4.3 They close the loop; you stop at prediction.** They make a *decision* and
show its effect. You produce a probability. A reviewer will ask: what does a 2 s
warning buy? Until prediction is connected to a downstream action or outcome,
"prediction" alone is a weaker contribution than "optimisation", regardless of how
much better the protocol is.

**4.4 They published the dataset with a DOI.** Mendeley Data, `10.17632/n2pvmtyn2j.1`.
Data and code release is close to expected at Q1 in 2026, and it is also a
citable output in its own right. You have no release plan.

**4.5 They have an outcome story; your headline is currently a set of negative
results.** Honest, but a paper needs a positive claim. Right now your strongest
positive result is R2 (real→real transfer holds at 0.81–0.84) and your strongest
negative is R8 (predictability is invariant to A3 configuration). Neither is yet
framed as a contribution a reader takes away.

---

## 5. Three concrete actions this comparison hands you

**5.1 Download their Mendeley dataset and run it through `stage06`.** DOI
`10.17632/n2pvmtyn2j.1`. Same operator, same city, same tool, different route and
different days. It becomes a **fifth independent domain** in your transfer matrix
at zero field cost, and it is the cleanest external validation available to you.
If your model transfers to it at ~0.8, R2 stops being three captures that agree
and becomes a generalisation result with an independent, publicly verifiable
holdout.

**5.2 It may also answer your open provenance question.** Doc 04 item 5 still
records that nobody has said where `DRIVETEST_LOGS_1_fixed.csv` came from. Sizes
do not match (theirs: 2,155 points / 367 HOs; yours: 81,141 / 6,515), so it is
not the same file — but it is the same lab, same operator, same city. Check
whether the curated file derives from this group's collection before you write
anything about its provenance.

**5.3 Turn their assumption into your result.** They assume HOM = 3 dB / TTT = 1 s.
You can show, from the same network and the same tool, that the deployed
parameters are −15 to +5 dB and 160–640 ms, with 100% attribution. "Published
work on this network optimises against mobility parameters the network does not
use, and here is the signalling that proves it" is a sharp, verifiable, citable
contribution — and it repositions your A3 attribution work (R1) from
instrumentation to a finding.

---

## 6. Verdict

| axis | who leads | margin |
|---|---|---|
| Experimental protocol and validity | **You** | large |
| Data scale and label quality | **You** | large |
| Uncertainty and statistics | **You** | total — they have none |
| Reproducibility of the analysis | **You** | large |
| Ground truth about the network | **You** | large |
| Literature positioning | **Them** | large |
| Closing the loop to a decision or outcome | **Them** | moderate |
| Publication readiness | **Them** | total — you have no draft |
| Data/code release | **Them** | total |

**Your research is methodologically stronger than this manuscript by a wide
margin, and rhetorically weaker by about the same margin.** The work is not the
bottleneck. The bottleneck is that none of it is yet positioned against the
literature, connected to an outcome, or written up.

Priority order, unchanged by anything else on your list:

```
1. Literature review, 40-60 refs, four threads   <- start now, runs in parallel with field work
2. Pull the Mendeley dataset into the transfer matrix
3. Decide the thesis frame (doc 09 gives the two options)
4. Connect prediction to an outcome, even a simple one
5. Write the manuscript
```

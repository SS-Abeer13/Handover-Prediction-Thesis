# Algorithm exploration: what to add, what to skip, and the one reframing that matters

Four parallel literature sweeps (event-time models; small-N tabular and time-series;
policy learning from logged data; robustness, label noise, guarantees and
interpretability). Roughly 120 papers screened, 2015–2026. This doc is the
shortlist and the reasoning, not the dump.

Everything below is judged against three hard constraints that will not change:
**43 independent drives**, **~760 events**, **no ability to deploy a policy**.

---

## 0. The headline: your task is formulated wrong, and fixing it is the contribution

You predict four independent binary labels: handover within 1 s, 2 s, 3 s, 5 s.
Nothing in the model enforces `P(T≤1) ≤ P(T≤2) ≤ P(T≤3) ≤ P(T≤5)`, and censoring
at drive end is handled implicitly by dropping tail rows. **That is a
discrete-time survival model with the survival structure removed.**

The correct object is the **conditional hazard** `h_k = P(T=k | T≥k)`: one model,
one output per time bin, from which every horizon follows as
`F(k) = 1 − Π(1−h_j)`. At 1 Hz your time grid is already discrete and uniform, so
this is nearly free.

**It can be done with LightGBM.** Reshape to long format — one row per
(sample × at-risk bin), with bin index as a feature — and fit a single binary
LightGBM on the hazard indicator. You keep the model that is already winning,
and you gain: coherent monotone horizons, explicit censoring, a proper
likelihood, and access to the whole survival-analysis metric suite (time-dependent
AUC, IPCW Brier, D-calibration) instead of four disconnected AUPRCs.

> Gensheimer & Narasimhan, *PeerJ* 7:e6257, 2019 (discrete-time logistic hazard);
> Kvamme & Borgan, *Lifetime Data Analysis* 27:710–736, 2021 (PC-Hazard; shows
> the discretisation scheme matters more than the architecture); Lee et al.,
> *AAAI* 2018 (DeepHit).

**Verified novelty check: no published work applies discrete-time survival or
temporal point processes to handover, RLF, or cell reselection prediction.** The
teletraffic literature models cell dwell time analytically for capacity
dimensioning; the ML literature treats handover as classification or RL. Nobody
has estimated a *conditional hazard from radio measurements*. That sentence is
your positioning statement, and it is defensible.

---

## 1. The novelty claim: ping-pong is self-excitation, and nobody has said so

Your ping-pong rate is 26–42%. A handover raises the probability of another
handover shortly after. **That is the textbook definition of a self-exciting
point process**, and the handover literature treats ping-pong purely as a
control problem (tune TTT/hysteresis/MRO) — never as a stochastic process to be
characterised.

The cheap, high-value version — do not start with a neural TPP:

1. Fit a univariate exponential-kernel Hawkes process to the handover times
   pooled across drives (`tick`, a few lines).
2. Report the **branching ratio**: the fraction of handovers that are
   self-triggered offspring rather than background, geometry-driven events.
   **That single number is a quantitative characterisation of ping-pong that the
   entire mitigation literature has never produced**, and you can check it
   against your measured ping-pong rate.
3. Add the Hawkes self-excitation term as a feature to your hazard LightGBM —
   `Σ exp(−β(t−tᵢ))` over recent handovers — and show it improves prediction.

You get the point-process framing without the small-N fragility of a neural TPP.

**Neural TPPs belong in the paper as baselines you expect to lose.** RMTPP (Du
et al., KDD 2016), Neural Hawkes (Mei & Eisner, NeurIPS 2017), Transformer
Hawkes (Zuo et al., ICML 2020), intensity-free (Shchur et al., ICLR 2020) — all
validated on 10⁴–10⁶ events; you have 760. The EasyTPP benchmark (Xue et al.,
ICLR 2024) found architectural differences among them are mostly within noise,
which corroborates your existing LightGBM-beats-deep result. Use `EasyTPP`,
budget half a day, report the negative.

---

## 2. Where the real performance gain probably is

Ranked by expected AUPRC movement per hour of work.

| # | Method | Why it fits | Effort |
|---|---|---|---|
| 1 | **TabPFN v2 / 2.5** | Published envelope is ≤10k rows × ≤500 features. You have 7,700 × 113 — dead centre, not an extrapolation. TabArena finds it beats *tuned, ensembled AutoGluon* in exactly this regime. | 1 day |
| 2 | **Post-hoc cross-model ensemble** (LightGBM + TabPFN + TabM, greedy selection on OOF predictions) | TabArena's central finding is that peak performance is misrepresented without post-hoc ensembling, and cross-model ensembles beat every standalone model. | ½ day |
| 3 | **MiniRocket features concatenated with your 113 engineered features** | Random convolutional kernels capture window shapes your hand-built deltas and slopes do not. Complementary inductive bias, ridge head, no overfitting risk. | 2 h |
| 4 | **RealMLP + TabM** via `pytabkit` / `tabm` | Both top-3 on TabArena; `pytabkit` also ships *tuned-default* GBDTs, which closes the "did you tune your baselines?" reviewer attack. | 1 day |

Two warnings on TabPFN, both of which bite your exact setup:

- **Majority-class bias under imbalance.** It becomes progressively
  majority-biased as imbalance grows. AUPRC is threshold-free so you are
  partially insulated, but any thresholded metric must use τ = minority
  prevalence.
- **It degrades under concept drift** (Cheng et al., 2025) — i.e. it may win
  in-distribution and *lose* on your cross-capture transfer. That contrast is
  itself a publishable result, not a problem.

> Hollmann et al., *Nature* 637, 2025; Erickson et al., TabArena, arXiv:2506.16791;
> Dempster et al., MiniRocket, KDD 2021; Middlehurst et al., "Bake off redux",
> *DMKD* 38, 2024.

**One genuinely novel recipe worth a shot:** RocketPFN (arXiv:2606.21786) —
ROCKET features fed to TabPFN v2.5, fully training-free, kernels split into
groups of 1,000 and probabilities ensembled. Matches HIVE-COTE 2.0 on UCR and
significantly beats MOMENT and Mantis. Nobody has applied it to handover.

---

## 3. Guarantees: your strongest lever, and currently your biggest trap

You report split conformal coverage 0.89–0.91. Two problems and two upgrades.

**The trap.** Standard conformal assumes exchangeable observations. Your 1 Hz
samples within a drive are massively autocorrelated, and the real exchangeable
unit is the **drive**. If a reviewer checks, sample-level calibration on
overlapping windows is indefensible. You already calibrate on whole drives,
which is right — but the guarantee needs to be *stated* at the drive level and
justified with the hierarchical-conformal literature, not asserted.

> Dunn, Wasserman & Ramdas, *JASA* 118(544), 2023 (two-layer hierarchical
> conformal; recommends repeated subsampling); Lee, Barber & Willett, *ACM J.
> Data Science*, 2025; Barber, Candès, Ramdas & Tibshirani, *Annals of
> Statistics* 51(2):816–845, 2023 (conformal beyond exchangeability, with an
> explicit coverage-gap bound under drift).

**Upgrade 1 — control the thing you care about.** Coverage is not the operator's
quantity of interest; **missed handovers** are. Conformal risk control extends
conformal to bound the expected value of any monotone loss, and the paper's own
worked examples include bounding the **false-negative rate**. That converts your
risk–coverage curve from a descriptive plot into a distribution-free guarantee:
*"we miss at most X% of handovers."*

> Angelopoulos, Bates, Fisch, Lei, Schuster, *Conformal Risk Control*, ICLR 2024,
> arXiv:2208.02814. Reference code is small and portable.

**Upgrade 2 — adaptive conformal for drift.** Gibbs & Candès (NeurIPS 2021)
adjust α online to maintain long-run coverage under arbitrary distribution
shift. Directly addresses your finding that temperature scaling does not
transfer to the external route (ECE 0.17–0.28).

This is the cheapest path from "good applied ML" to a methodological
contribution: it is all post-hoc on a frozen model, needs no retraining, and
targets the operator-facing claim.

---

## 4. Your undercounted labels are an asset, not just a defect

You measured that at 1 Hz only **44–58%** of signalling-confirmed handovers
appear as a cell change in the sample export. That is textbook **one-sided label
noise**: every labelled positive is real, an unknown fraction of true positives
is labelled negative. It is exactly the positive-unlabelled setting.

**What makes this publishable rather than embarrassing:** almost nobody in the
PU literature knows their label-recovery constant `c`. **You measured it.**
Under Elkan & Noto's result, a classifier trained on labelled-vs-unlabelled data
outputs a constant multiple of the true posterior, so `p(y=1|x) = g(x)/c` — a
two-line correction that makes every calibrated probability in the paper
defensible. Sweep `c` over [0.44, 0.58] as a sensitivity analysis; run nnPU as
the principled comparator.

State plainly that SCAR is probably violated (missed handovers correlate with
speed and signal dynamics), cite Bekker, Robberechts & Davis (ECML-PKDD 2019),
and treat SCAR as an approximation whose sensitivity you test.

**Bonus:** this gives you a principled story for the curated dataset collapsing
to 0.35 — a labelling-convention mismatch rather than a model failure.

> Elkan & Noto, KDD 2008; Kiryo et al., nnPU, NeurIPS 2017; Bekker & Davis,
> *Machine Learning* 109:719–760, 2020.

---

## 5. One figure that would carry the paper

A **monotone-constrained Explainable Boosting Machine**, with its learned
log-odds shape function for the serving-to-neighbour gap **overlaid on the
analytic 3GPP A3 threshold**, one curve per co-existing A3 regime.

- The A3 event fires when `Mn + Ofn + Ocn − Hys > Ms + Ofs + Ocs + Off`, which is
  **monotone increasing in the neighbour-minus-serving gap**. Constraining the
  model to respect that is a genuine physics prior and costs one LightGBM /
  `interpret` parameter.
- EBM gives you the shape function directly. The offset and hysteresis appear as
  the location of the knee. It connects your regime finding, the physics, and
  the interpretability requirement in a single artefact.
- Whether the monotone constraint closes part of your cross-capture transfer gap
  is a clean, novel, domain-grounded ablation no handover paper has run — and if
  it *hurts* in-distribution, that is also interesting, because it means the
  model was exploiting a non-A3 shortcut.

Be careful not to overclaim: "monotone constraints improve OOD generalisation"
is practitioner consensus, not a benchmarked result. Report it as an empirical
finding on your data.

> Lou, Caruana, Gehrke & Hooker, GA2M, KDD 2013; Nori et al., InterpretML,
> arXiv:1909.09223; Gupta et al., *JMLR* 17(109), 2016 (monotonic lattices);
> Nolte, arXiv:2011.00986 (why LightGBM's constraint method does not cost
> accuracy). Skip Neural Additive Models — more compute, no gain on tabular.

---

## 6. The uncomfortable finding about RL

You want to close the loop (doc 11 §4.3). Here is the honest position.

**The 3GPP A3 rule is a deterministic logging policy.** Propensities are 0 or 1.
Under that condition **every off-policy evaluation estimator is unidentified** —
IPS, self-normalised IPS, doubly robust, switch-DR, DR-shrinkage, MAGIC,
marginalised importance sampling. They do not degrade gracefully; they **collapse
to the direct method** (your own outcome regression) wherever the new policy
disagrees with A3. Doubly robust becomes singly robust: the correction term is
identically zero, so there is no second chance. Every variance-reduction trick in
that literature interpolates between IPS and the direct method, and deterministic
logging pins the interpolation at the direct-method end.

**This means the departmental paper's circularity cannot be fixed by better
estimators.** It is structural. And it means you must not report a DR or IPS
number as if it were unbiased — a reviewer who knows OPE will catch it.

Deep offline RL is worse, not better. CQL/IQL/TD3+BC/Decision Transformer were
tuned on 10⁵–10⁶ transitions from *diverse* behaviour policies; you have ~760
decision events from **one deterministic expert**. Behavioural cloning on your
data reproduces A3 and nothing more, and you cannot select hyperparameters
because offline model selection requires the OPE you do not have.

> Dudík, Langford & Li, ICML 2011; Wang, Agarwal & Dudík, ICML 2017; Su et al.,
> ICML 2020; Sachdeva, Su & Joachims, KDD 2020 (deficient support); Fu et al.,
> ICLR 2021 (no OPE method is reliable for policy selection under poor coverage);
> Kumar et al., ICLR 2022 ("Should I run offline RL or behavioural cloning?").

### What IS identifiable — and it is better than what you were going to claim

**(a) Fuzzy regression discontinuity at the A3 boundary.** The rule is
deterministic in the *reported, L3-filtered, 1 dB-quantised* measurements — but
**stochastic in the true radio state**, because of filter lag, quantisation, fast
fading and report jitter. Two samples with near-identical propagation can land on
opposite sides of the trigger. That makes the quasi-propensity score
non-degenerate in a shrinking neighbourhood of the boundary and identifies a
local treatment effect: *"for UE-samples marginal to the A3 trigger, what is the
effect of triggering on ping-pong / HOF / continuity over the next N seconds?"*
Local and narrow — but a **real causal number from a real network**, which the
simulator papers cannot produce.

> Narita & Yata, *Algorithm is Experiment*, arXiv:2104.12909 — the quasi-propensity
> score, which unifies propensity-score and RD identification for deterministic
> algorithms. This is the key citation for your setting.

**(b) The natural experiment you already own.** You recovered **per-carrier A3
parameters from signalling**, and different carriers run different
(offset, hysteresis, TTT). That is genuine variation in the policy itself,
generated by the operator's planning decisions rather than by you. Estimate the
effect of offset/TTT on ping-pong and RLF with AIPW/DML, with overlap
diagnostics and a sensitivity analysis. **I found no handover paper exploiting
this.** It is the most valuable asset in your dataset.

**(c) The benefit envelope — identified by counting alone.** For each observed
ping-pong or failure, ask whether the predictor flagged it with lead time ≥ τ.
Under perfect action efficacy, at most K(τ) of N events could have been avoided.
**K(τ)/N is an upper bound on achievable benefit and requires no counterfactual
whatsoever.** Then sweep an action-efficacy parameter η ∈ [0,1] and report
η·K(τ)/N as a benefit surface over (τ, η), anchoring plausible η with the RD
estimate from (a).

That reframes the contribution from *"we learned a better policy"* — which you
cannot support — to *"we quantify the attainable decision benefit of handover
prediction and identify the local causal effect of the operator's A3 trigger."*
Honest, novel, decision-connected, and immune to the circularity charge.

**(d) A negative result with teeth.** Safe policy improvement with baseline
bootstrapping (Laroche et al., ICML 2019) only permits deviation where
state-action support is sufficient. With a deterministic baseline it will revert
to A3 everywhere. *"No region of this dataset has sufficient support to license
deviation from the operator's rule"* is a real, citable finding — and an
implicit rebuttal of the departmental paper.

**If you want a simulator anyway:** build an A3 replay engine over your own
logged traces with the recovered parameters, and **validate it by checking it
reproduces the 760 real handovers when run with the real parameters**. Report
that validation as a first-class result. Without it, the simulator is worthless;
with it, it is a reasonable secondary contribution — and it is what Ericsson and
the UPF group do.

---

## 7. What to skip, and how to say so

Each of these deserves a cited paragraph explaining the decision. That reads as
judgment; silence reads as a gap.

| Skip | Why | Cite |
|---|---|---|
| **IRM, DANN, Fish** | IRM's guarantees need more environments than spurious-feature dimensions; you have 4 captures. DomainBed: properly tuned ERM matches or beats everything. | Gulrajani & Lopez-Paz, ICLR 2021; Rosenfeld et al., ICLR 2021; WOODS, arXiv:2203.09978 |
| **Test-time adaptation** | TENT adapts BatchNorm — meaningless for GBDT — and needs a test batch; you have a 1 Hz stream. Benchmarks show it frequently fails to beat the unadapted model. Use per-drive recalibration + adaptive conformal instead. | Zhao et al., *On Pitfalls of Test-Time Adaptation*, ICML 2023 |
| **Self-supervised pretraining** (TS2Vec, TF-C, SimMTM) | Your entire unlabelled corpus is the same 43 drives. Pretraining on the data you then fine-tune on adds no information and *increases* your window-overlap leakage surface — the exact failure you measured at GRU +109%. | — |
| **Mamba / S4 / S5** | Built for thousands-to-millions of steps. Your sequences are **10 steps**. The architectural advantage does not exist here. | — |
| **Time-series foundation models** (Chronos, Moirai, TimesFM, Lag-Llama) | Forecasting models with no classification head. Two independent 2025 evaluations found ROCKET/MiniRocket beat every TSFM on multivariate classification, because current TSFMs process channels independently — and your data is maximally channel-dependent. | Isiacik et al., ECML PKDD 2025 |
| **Learning-to-rank for target cells** | Technically sound, nearly free in LightGBM — but your target-cell labels are sparser and noisier than your event labels. Second paper, not this one. | — |

Run **Mantis** (small, classification-native TSFM) for half a day purely so the
paper can report "we tested a foundation model and it lost." Negative results of
that kind are increasingly expected.

**One point that is load-bearing regardless of which model wins:** with 43
drives, report **per-drive metric distributions and paired tests across drives**
(Wilcoxon signed-rank, critical-difference diagrams), not a single pooled number.
A pooled AUPRC over overlapping windows from 43 groups is the exact statistic a
reviewer will attack.

---

## 8. The frame this all points to

> **Handover forecasting as a self-exciting recurrent-event process: a
> discrete-time hazard model with distribution-free risk control, validated
> across four independent captures and one public dataset.**

Contributions, in the order a reader should meet them:

1. **Formulation.** Handover prediction as discrete-time hazard estimation, not
   multi-horizon binary classification. First application of survival /
   point-process modelling to this problem.
2. **Mechanism.** Ping-pong quantified as self-excitation via the Hawkes
   branching ratio — a number the mitigation literature has never produced.
3. **Guarantees.** Distribution-free bound on missed handovers, valid at the
   drive level, under conformal risk control.
4. **Instrumentation.** A3 attribution from RRC signalling at 100%; parser
   validated 310/310 against XCAL's own event counter; the reproducible
   authenticity audit.
5. **Negative results with teeth.** Leakage is architecture-dependent (GRU +109%
   vs LightGBM +12%); predictability is invariant to A3 configuration;
   deterministic logging makes off-policy evaluation of handover policies
   unidentified.
6. **External validation.** Independent public dataset; our model matches its
   in-domain ceiling.

That is a Q1 paper, and every element of it is either already done or reachable
from what you have.

---

## 9. Do it in this order

```
Week 1  discrete-time hazard reframe on LightGBM        <- the formulation
        Hawkes branching ratio + self-excitation feature <- the novelty
Week 2  conformal risk control, drive-grouped            <- the guarantee
        PU correction with measured c, sensitivity sweep <- the label story
Week 3  TabPFN v2 + MiniRocket + post-hoc ensemble       <- the performance
        monotone EBM figure vs the A3 rule               <- the mechanism figure
Week 4  fuzzy RD at the A3 boundary + benefit envelope   <- the decision link
        neural TPP / Mantis baselines (report negatives)
ongoing literature review, 40-60 refs                    <- doc 11 gap
```

Weeks 1–2 alone lift the paper from applied ML to a methods contribution. Week 4
is what answers "so what?".

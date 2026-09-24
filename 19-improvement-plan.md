# Improvement plan — what can still move the results, ranked, with steps

Nothing in this document has been executed. It is an audit of the current
result tables against what a Q1 reviewer will ask, and a step-by-step guide for
each fix. Numbers quoted are read from `reports/tables/` as of today.

---

## 0. The one finding that matters most

The manuscript currently rests on **two different datasets with two different
label definitions**, and the headline table is on the weaker one.

```
                          benchmark tables            C1–C7 tables
                          (main_results, leakage,     (hazard, Hawkes, CRC,
                           ablation, uncertainty,      benefit, mechanism)
                           external)
------------------------------------------------------------------------
data                      curated 6–8 Sept            XCAL 10–13 Sept pooled
drives                    7 pseudo-drives             26 drives
rows                      8,347                       ~6,200
handover ground truth     regenerated from            RRC signalling,
                          serving-cell changes        97.4% attributed to
                          (HANDOVER_LOG_REGENERATED)  the deployed A3 rule
LightGBM AUROC @ 1 s      0.816                       0.94
AUPRC lift @ 1 s          3.3×                        11.1×
bootstrap groups          7                           26
```

`configs/base.yaml` still points `data.adapter` at `curated_v1`. Every table
that stage02 produces — the six-model comparison, the leakage study, the
feature ablation, the uncertainty/abstention tables, the event-level metrics
(detection rate 16.9 %, 88 false alarms/hour) — is on the curated data.

A reviewer will notice that the model in Table 2 scores 0.82 and the same model
in Table 5 scores 0.94, and will ask which one the paper is about.

**Fixing this is item A below and it is the single largest improvement
available.** It costs no new modelling.

---

## 1. Ranked list

| # | Change | Reviewer question it answers | Expected effect | Effort |
|---|---|---|---|---|
| **A** | Rerun the whole stage02 benchmark on the XCAL signalling captures | "Which dataset is this paper about?" | Headline AUROC 0.82 → ~0.94; event metrics on real ground truth; CIs from 26 drives not 7 | 1 day, reruns only |
| **B** | Reinstate the 0.5 s horizon on XCAL data | "The proposal promised 0.5 s" | Fifth horizon and hazard bin; recovers the proposal's spec | 2 h |
| **C** | Calibrated + monotone-projected multi-head baseline, plus one classical survival baseline | "Isn't the hazard win just missing temperature scaling?" | C1 becomes reviewer-proof, or is honestly narrowed before a reviewer narrows it | 1 day |
| **D** | Paired test with real power: repeated seeds or leave-one-drive-out; bootstrap CIs on deltas | "Wilcoxon with 4 folds cannot reject anything" (min p = 0.125) | Every paired claim gets a CI | 3 h |
| **E** | Signalling-derived features: TTT clock, recent-A3-report flag, RF slopes | "You parsed the signalling and then never used it as input?" | Most likely place accuracy itself rises, mainly at 2–5 s; opens a new task (report-conversion prediction) | 1–2 days |
| **F** | Dedicated ping-pong predictor for the benefit envelope | "Why use a generic HO model to flag ping-pongs?" | Excess-over-random positive above the 10 % budget, or a cleaner negative | 1 day |
| **G** | Hawkes goodness-of-fit and CI on the branching ratio | "0.61 is a fitted parameter; does the model fit?" | C2 gets a residual test, LR test vs Poisson, bootstrap CI | 3 h |
| **H** | CRC on the hazard model with pooled calibration drives; publish the (α, alarm-rate) frontier | "α = 0.1 costs 59–86 % alarm rate — what is this for?" | Guarantee at a usable operating point, or an honest frontier figure | 4 h |
| **I** | Equal tuning budget for every model (nested grouped CV) | "Your deep baselines are untuned" | Removes the under-tuned-DL objection; LightGBM probably still wins | 1 day compute |
| **J** | Five seeds, mean ± sd on every headline table | "Single seed" | Free robustness | 2 h |
| **K** | Per-drive standardisation / CORAL as a zero-cost transfer baseline | "No domain adaptation at all?" | Small gains on public↔ours and cross-regime | 3 h |
| **L** | Reimplement the FinalManuscript model on our data under our protocol | "How does the existing IUT paper do on your data?" | Direct like-for-like comparison | 1 day |
| **M** | One more capture day on a new route/time (if XCAL access allows) | "Cross-regime transfer is one pair, one direction" | A third regime clearing the 60-handover bar | field day |

Do A, B, D, J first — they are reruns, not research, and A changes every
number the manuscript will quote. Then C, G, H (they harden claims already
made). Then E, F (the only items that can move accuracy). I, K, L, M as time
allows.

---

## 2. Step-by-step

### A. Unify the benchmark on the XCAL captures

Why: see §0.

```
1. Copy configs/base.yaml → configs/base_xcal.yaml
2. Set  data.adapter  to the XCAL signalling adapter that stage06 already uses
   (stage06_cross_capture.py builds the pooled frame with per-capture drive
   prefixes — reuse that prepare path, do not write a new one)
3. Set  labels.handover.source: handover_log  with the signalling log as source
   (this is the 780-handover log that C6 attributes)
4. Set  qc.core_fields  as in stage08 if GPS is missing in any capture
5. Run stage01 → stage02 for experiments main, leakage_study,
   ablation_features, uncertainty → stage04 external → stage05 report
6. Diff the new main_results.csv against the old one; expect
      n_groups 7 → 26, AUROC 0.82 → ~0.94 at 1 s, ECE roughly unchanged
7. Recompute main_events.csv on the new run; the current 16.9 % detection /
   88 FA/h at 1 s will change and must be re-quoted everywhere
8. Keep the curated-data run as an appendix table titled
   "robustness on an independent capture with transition-derived labels"
```

Check before trusting the result: the drive-ID prefix fix from stage06
(`tag + drive_id`) must be active, otherwise pooled AUROC jumps to ~0.99 and
that is leakage, not skill.

### B. Reinstate the 0.5 s horizon

Why: `base.yaml` drops 0.5 s because "a horizon shorter than one sample period
cannot carry a positive label." That is true only when handover timestamps sit
on the 1 s grid, which they do in the curated data. The signalling log has
millisecond timestamps, so at a 1 Hz sample time t the label "handover in
(t, t + 0.5]" is well-defined.

```
1. In the XCAL config set  labels.horizons_s: [0.5, 1.0, 2.0, 3.0, 5.0]
2. Remove or relax the guard that drops horizons < target_period_s when the
   handover source carries sub-second timestamps
3. Sanity check: positives at 0.5 s should be roughly half of positives at 1 s
   (0.0735 × ~0.5 ≈ 0.035); if it is 0, the timestamps were floored somewhere
4. Add 0.5 to EDGES in stage09_hazard.py so the hazard model gets a fifth bin
5. Rerun A and stage09
```

### C. Make C1 reviewer-proof

Why: in `stage09_hazard.py::run_fold` the multi-head arm is raw LightGBM —
no temperature scaling, no isotonic, no monotone projection. The ECE
improvement of −23 to −35 % and the 25.4 % → 0 % non-monotonicity are compared
against a baseline nobody would deploy uncalibrated. The code to fix the
baseline already exists in `uncertainty/calibration.py`.

```
1. Add arm "multi-head + per-horizon isotonic" — fit on calibration drives
   inside the training fold (never on test), using calibration.py
2. Add arm "multi-head + isotonic + monotone projection" — for each row,
   pool-adjacent-violators across the horizon axis so P(1s) ≤ P(2s) ≤ ...
3. Add one classical survival baseline so "first time-to-event formulation"
   has a comparator:
      cheapest: logistic-hazard MLP (Nnet-survival / Gensheimer & Narasimhan)
      or Cox PH with time-varying covariates (lifelines) on the same long format
4. Re-run hazard_vs_multihead with all arms, same folds, same seeds
5. Decide the claim from the numbers:
      hazard still wins ECE  → keep C1 as written, now against a fair baseline
      parity after step 2    → rewrite C1 as "one model replaces four heads
                               plus two post-hoc corrections, at equal quality"
   Either outcome is publishable; being surprised by a reviewer is not.
```

### D. Statistical power for paired comparisons

Why: `hazard_paired_test.csv` has n_folds = 4. A two-sided Wilcoxon on four
pairs has a minimum attainable p of 0.125. The test is decorative.

```
1. Option 1 (cheap): repeat the grouped 4-fold split over 5 seeds → 20 pairs
   Option 2 (cleaner): leave-one-drive-out over the 26 drives → 26 pairs,
   but some drives have too few events for AUPRC; use event-weighted deltas
2. Report for every paired claim: mean delta, cluster-bootstrap 95 % CI on the
   delta (resample drives, not rows), and the Wilcoxon p as a secondary
3. Apply the same to: hazard vs multi-head (AUPRC and ECE), regime_transfer
   same vs cross (n = 591 — CI is essential), with-A3 vs without-A3 (C10)
4. Report ECE with a bootstrap CI; ECE from 10 bins on ~1,400 rows is noisy
```

### E. Signalling-derived features

Why: the parser attributes 97.4 % of handovers to the deployed rule, and the
mechanism section shows the gap condition alone is weak (AUROC 0.566). But the
feature set never sees the signalling. Two observables are legitimately
available online and are not in any competitor paper:

```
Feature 1 — TTT clock
   consecutive seconds for which the A3 entering condition has held under the
   profile deployed at that instant (from RegimeMaps.at(t)); reset on exit.
   Captures "how far through the time-to-trigger are we" — the part of the
   rule that the static gap ignores.

Feature 2 — recent A3 report
   flag / count of measurementReport(A3) in the previous k seconds, k = 1..5,
   from the same signalling log. The network sees this in real time.
   LEAKAGE GUARD: a report precedes the handover command by ~50–200 ms, so a
   report in the SAME 1 s bin as the sample is not a forecast. Use only reports
   in strictly earlier bins.

Feature 3 — slopes
   d(RSRP)/dt, d(SINR)/dt, d(gap)/dt over 3 s and 5 s windows, if not already
   present in the feature registry.
```

```
1. Build features 1–3 in the feature stage with attrs registered as a new block
   "signalling" so select_blocks can ablate it
2. Run the feature ablation: base / +signalling / +signalling −dwell
3. Run stage09 with the new block
4. Expected: dwell stays dominant at 1 s; the report flag should add most at
   2–5 s because 39 % of reports convert and conversion takes up to TTT + RRC
   procedure time
5. New sub-task worth a subsection: report-conversion prediction —
   P(handover within k s | A3 report at t). Positives = converted reports,
   negatives = the 60.6 % that never do. This is a well-posed learning task
   that Ghoshal et al. measured but did not model.
```

### F. Dedicated ping-pong predictor

Why: `benefit_envelope_pingpong.md` flags ping-pongs with the generic handover
model. Excess over random is +0.29 at a 5 % budget and −0.21 at 40 %. The
generic model ranks by "will a handover happen", not "will it be a ping-pong".

```
1. Label: for each sample, y_pp = 1 if the next handover is followed by a
   return to the source cell within 15 s (the literature-standard window from
   pingpong_benchmark.md)
2. Features: full block + Hawkes excitation columns + t_since_prev_ho +
   serving_dwell + previous-cell identity match (are we back on the cell we
   just left?)
3. Train LightGBM, grouped by drive, same folds as stage09
4. Recompute the benefit envelope with this model's ranking
5. Either outcome is a result:
      positive excess to 20–40 %  → the predictor earns its keep at usable budgets
      still negative               → ping-pong is not forecastable before its
                                     first leg; report it and drop the envelope
                                     to an appendix
```

### G. Hawkes goodness-of-fit

Why: a branching ratio of 0.61 is only meaningful if the Hawkes model fits
better than the alternatives. Currently there is no fit test and the ± 0.04 is
the spread across captures, not a confidence interval.

```
1. Ogata residual analysis: transform event times with the fitted compensator
   Λ(t); the rescaled inter-event times should be Exp(1). KS test per capture.
2. Likelihood-ratio test vs homogeneous Poisson (α = 0, same data)
3. One renewal alternative (gamma or Weibull inter-event) — if a renewal
   process fits as well, "self-excitation" is not the right word
4. Parametric bootstrap: simulate 200 realisations from the fitted model with
   the observed drive durations, refit, take the 2.5–97.5 % of n = α/β
5. Add a column to hawkes_selfexcitation.csv: KS p, LR p, n_CI_low, n_CI_high
```

### H. Conformal risk control at a usable operating point

Why: at α = 0.1 the certified thresholds alarm on 59–86 % of samples. The
guarantee holds and is worthless. Twelve calibration drives give
min α = 0.077.

```
1. Run CRC on the hazard model's incidence (better calibrated than the
   multi-head it currently uses) — the certified threshold should drop
2. Pool calibration drives across the three captures (and the curated capture
   if item A's cross-capture table shows it is exchangeable enough); each extra
   drive lowers min α by 1/(n+1)
3. Plot the frontier: x = α, y = alarm rate, one curve per horizon, with the
   naive pooled-sample threshold as a dashed line and its per-drive FNR p90
   annotated. This figure is the honest statement of what the guarantee costs.
4. State the design rule in the text with numbers: α = 0.05 needs ≥ 19
   calibration drives; α = 0.02 needs ≥ 49.
```

### I. Equal tuning budget

Why: LightGBM uses fixed params (400 rounds, lr 0.05, 31 leaves); the GRU /
TCN / Transformer scores (0.80) sit below LightGBM (0.82) on the curated data,
which reads as under-tuned deep baselines.

```
1. Nested grouped CV: outer = existing drive folds; inner = GroupKFold(3) on
   training drives only
2. Same budget for every model: e.g. 20 Optuna trials, objective = inner AUPRC
   at the 2 s horizon (the middle horizon; avoids tuning to one extreme)
3. Search spaces kept small — with 26 drives a large search overfits the CV
4. Report default vs tuned side by side; if the ranking does not change, say so
```

### J. Multi-seed

```
1. seeds = [1337, 1338, 1339, 1340, 1341]
2. Every headline table: mean ± sd across seeds, CIs from the pooled
   cluster bootstrap
3. Cheap once A is done; run it in the same job
```

### K. Zero-cost transfer baselines

```
1. Per-drive z-scoring of RSRP/RSRQ/SINR features (removes device and
   operator offsets)
2. CORAL (align second moments of source and target features) — ten lines
3. Rerun stage08 both directions and stage07; report untreated / z-scored /
   CORAL
```

### L. Departmental paper reimplemented under our protocol

```
1. Extract from FinalManuscript.pdf: exact feature list, model, window length,
   split method (doc 11 has most of it)
2. Implement as one more model entry in configs/experiments/main.yaml
3. Evaluate under grouped-drive split with our metrics; also under their
   split so the paper can show both numbers side by side
```

### M. If one more capture day is possible

```
1. Different route or time of day → chance of a third A3 profile clearing the
   60-handover bar (doc 06 has the field checklist)
2. Even the same route adds calibration drives for H and bootstrap groups for D
```

---

## 3. What not to do

```
- Do not re-add scale_pos_weight to the hazard arm (it broke calibration once)
- Do not tune on test drives, or on calibration drives used by CRC
- Do not report random-row splits anywhere but the leakage study
- Do not drop the withdrawn claims from the paper's history — the
  configuration-timeline defect is itself a contribution (C6)
- Do not chase the 1 Hz ceiling; it is measured (90.5 %) and stated
```

---

## 4. Suggested order

```
week 1   A → B → J → D          reruns; every headline number becomes final
week 2   C → G → H              harden C1, C2, C3 before a reviewer does
week 3   E → F                  the only items that can raise accuracy
then     I → K → L → M          as time allows
```

Start the manuscript skeleton in week 1 with placeholders; item A changes the
numbers in every table, so nothing should be typeset before it finishes.
Regenerate `fig_mechanism_a3.png` (still stale) in the same pass as A.

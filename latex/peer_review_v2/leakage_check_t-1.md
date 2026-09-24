# Leakage check at row t−1 (reviewer alfa, v2 panel concern #6) — 2026-09-23

**Question:** Is the headline 1 s AUPRC of 0.179 partly caused by leftover leakage at the corrected row t−1? The reviewer's argument: t−1 contamination is 15.6% across all handovers but 11.7% for isolated ones.

**Answer: no. Your existing pipeline outputs already rule it out.** No new run was needed. A fresh run wasn't possible anyway: `data/processed_xcal`, `data/rev/*.pkl` and the `oof_*.npy` predictions are not in the folder, and scikit-learn isn't installed in the build environment. All numbers below come from `pipeline/reports_rev/tables/`.

## Evidence

### 1. There is no step at t−1 in either subset (`c9_row_alignment_audit`)

| subset | n | t−3 | t−2 | t−1 | t+0 |
|---|---|---|---|---|---|
| all handovers | 938 | 23.7% | 21.7% | **15.6%** | 75.9% |
| isolated (>8 s) | 291 | 12.1% | 12.1% | **11.7%** | 74.6% |

Leakage would show up as a jump at t−1 compared with the rows before it. Instead, t−1 is *below* the earlier rows in both subsets. The 15.6% vs 11.7% gap compares two different baselines. Across all handovers, the target cell often served 2–3 s earlier because of ping-pong, so the baseline is higher (~22–24%). The only jump is at t+0, the aggregation defect that the lag already removes.

### 2. The model does better on isolated handovers, not worse (`c8_burst_strata`, LightGBM, 1 s, LOCO, 3-seed mean)

| stratum | rows | prevalence | AUPRC | lift | AUROC |
|---|---|---|---|---|---|
| pooled | 8,586 | 6.8% | 0.179 | 2.6× | 0.777 |
| quiet (no HO in previous 10 s) | 5,518 | 4.3% | 0.133 | **3.1×** | 0.772 |
| in burst (HO 2–10 s earlier) | 3,068 | 11.2% | 0.212 | 1.9× | 0.720 |

`c19_burst_initiators` shows that all 238 positive quiet rows come right before a handover with no command in the previous ~10 s. The quiet stratum is therefore the isolated-handover test the reviewer asked for (with a stricter gap: ~10 s rather than 8 s). There, lift is higher and AUROC is essentially the same. If burst leakage were inflating the number, the pattern would be reversed. The ordering also holds for burst cutoffs of 5–20 s (`c19_sens_burst_cutoff`: quiet 2.6–3.2× vs burst 1.5–1.9×).

**Caveat:** isolated-handover AUPRC (0.133) is lower than 0.179 only because prevalence is lower (4.3% vs 6.8%). Compare lift or AUROC, not raw AUPRC. Also, `c19_sens_burst_cutoff` at 10 s gives quiet AUPRC 0.113 / lift 2.6×, not 0.133 / 3.1×. It is probably a fixed-hyperparameter run, and the table should say so.

## Problems found in the manuscript text (`ch5_results_and_analysis.tex`, line ~33)

The paragraph that already answers this concern has errors a reviewer would catch:

1. **Wrong stratum definition and numbers.** It says quiet rows are "> 60 s since the previous command" with "AUPRC 0.053 vs 0.017 floor" and in-burst "AUPRC 0.380 vs 0.203 floor". None of these numbers appears in any pipeline table. Table 5.11 and `c8_burst_strata` use a **10 s** cutoff: 0.133 vs 4.3% (quiet) and 0.212 vs 11.2% (burst).
2. **Wrong comparison.** It calls 15.6% "a 3.9-percentage-point elevation" by comparing pooled t−1 with the *isolated* baseline. Against its own pooled baseline (t−2 = 21.7%, t−3 = 23.7%), pooled t−1 is not elevated at all. This framing is what prompted alfa's concern.
3. **Contradicts §5.8.** It says quiet rows are where "row t−1 sits strictly at background". Line ~562 correctly says quiet positives are burst *onsets*, not lone handovers. These are consistent, but the line-33 wording blurs them.
4. **Overclaim.** "proves that the 0.179 pooled AUPRC reflects genuine…" should be "is inconsistent with residual leakage driving…".

The same "3.9 pp" / "1–4 s" wording is repeated in the threats-to-validity bullet (line ~841).

## Suggested replacement paragraph (line ~33)

> Table~\ref{tab:5_1} also bears on whether the one-row lag leaves residual contamination. It does not show any. Leakage from the aggregation rule would appear as a step at the last row before the command. Instead, the share of rows already showing the target cell *falls* from t−3 to t−1 in both subsets: from 23.7\% to 15.6\% across all handovers, and from 12.1\% to 11.7\% on isolated ones. It then jumps only at t+0. The higher pooled level is a baseline effect, not a lag effect. With 26.3\% of commands being ping-pong returns within 15~s, the next target cell has often served within the last few seconds. The model-side check points the same way. On quiet rows (no command in the previous 10~s), whose 238 positives all precede a command with no other command in the preceding 10~s, LightGBM reaches AUPRC 0.133 against a 4.3\% floor (3.1$\times$ lift, AUROC 0.772). On in-burst rows it reaches 0.212 against 11.2\% (1.9$\times$, AUROC 0.720) (Table~\ref{tab:5_11}). The ordering holds for burst cutoffs from 5 to 20~s (Table A.5). If residual burst contamination were carrying the result, lift would be highest inside bursts. It is lowest there, which is inconsistent with residual leakage driving the pooled 0.179.

Threats bullet (line ~841): replace "reaches 15.6% … 1–4 s … demonstrating" with "is 15.6% across pooled handovers, which is below that subset's own t−2/t−3 baseline (21.7%/23.7%), so there is no step at t−1. Lift is highest in quiet rows (3.1× vs 1.9×; Table 5.11), which is inconsistent with residual burst contamination driving the result."

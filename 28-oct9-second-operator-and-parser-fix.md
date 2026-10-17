# 28 — 9 October 2026 capture: blind second-operator test, a parser fix, and re-evaluation

**Date:** 14 October 2026
**Status:** Current. Extends `26-revision-after-review.md`; nothing in `pipeline/reports_rev/` was overwritten.
**Pipeline:** `stage32_second_operator.py` (new). The corrected-parser re-run of stage 22 is in `pipeline/reports_rev_parserfix/`, and the 9 Oct outputs are in `pipeline/second_operator/`.

---

## 1. Summary

1. **The 9 Oct capture is on a different operator.** It is Banglalink (MCC 470 / MNC 03); every earlier campaign is Grameenphone (MNC 01). It was recorded after the modelling freeze and after the alignment audit, so it is the first test that is blind to *every* pipeline decision, the one-row lag included. That answers review item 2 ("campaign 4 is not blind") and the second-operator limitation in §7.2 / §7.3.
2. **A parser bug was found, and it affects the frozen data too.** The measurement-report parser required `rsrqResult` after every `rsrpResult`. In TS 36.331 that field is optional, and Grameenphone omits it in 25–36% of neighbour entries. The old pattern dropped those entries and, where one was followed by a full entry, gave the second entry's measurement to the first entry's PCI. On 9 Oct the parser recovered 16 of 776 neighbour rows. The fix is a correctness fix, made without looking at any model output.
3. **The four-campaign results survive the fix, a little lower.** The headline LightGBM 1 s AUPRC goes from **0.179 to 0.169** (lift 2.63× → 2.49×, AUROC 0.777 → 0.773). The model ordering is unchanged. The lag collapse (≈0.60 → ≈0.16 at fixed hyper-parameters), coherence, the risk-control frontier, and the "weak A3 gap" mechanism all hold.
4. **Both methodological findings replicate blind on the second operator.**
   - At the command row, the target cell already serves for 66.7% of 9 Oct handovers; at the row before, only 4.6% (0% for isolated handovers).
   - The unlagged model scores AUPRC **0.512** on 9 Oct against **0.119** lagged, the same ≈4× inflation as on Grameenphone.
   - Neither was tuned on this capture.
5. **The prediction ranking does not transfer.** Trained on the four Grameenphone campaigns and scored blind on 9 Oct, the primary model (LightGBM) reaches **AUPRC 0.137** (lift 2.3×, AUROC 0.773).
   - That is inside the Grameenphone per-campaign range, 0.125–0.223.
   - It is not distinguishable from the deployed A3 rule (0.159), although it ranks better (AUROC 0.773 vs 0.691).
   - **Logistic regression is clearly better on 9 Oct:** AUPRC 0.261, AUROC 0.842. It beats LightGBM in 99% of paired within-session bootstrap draws.
   - History-only models (dwell, Hawkes) also beat LightGBM there.
   - So "LightGBM is the primary model" is a Grameenphone result. The thesis should say that.
6. **The network behaves differently.**
   - 59% of handovers are inter-frequency (Grameenphone 13–23%).
   - The dominant trigger is A5 (37% of handovers), not A3 +1 dB/320 ms. That Grameenphone profile is absent.
   - Ping-pong is 13.8% (Grameenphone 19.5–40.3%), and the carrier pattern *reverses*: inter-frequency 19.6% against intra-frequency 5.6%.
   - The "carrier relationship / TTT is the lever" reading of §5.10 is therefore operator-specific.

---

## 2. The capture

| | 9 Oct (new) | GP range, 4 campaigns |
|---|---|---|
| Operator | **Banglalink (MNC 03)** | Grameenphone (MNC 01) |
| Route | Gazipur, near IUT | Dhaka urban + Uttara–Gazipur highway |
| Duration | 17.4 min (1 session) | 24–60 min |
| Rows (QC / usable) | 1,045 / 883 | 1,440–3,600 / 1,131–3,072 |
| 180 s blocks (all pass QC) | 6 | 8–20 |
| Distance, mean speed | 6.2 km, 27 km/h | 9–34 km, 21–51 km/h |
| Main band | Band 40 (TDD), about two-thirds of rows | Bands 1/3/28/41 |
| Handover commands (completed) | 87 (87) | 176–307 (100%) |
| Inter-frequency share | **59%** (51/87) | 13–23% |
| Re-establishments | 8 | 5–159 |
| Measurement reports | 1,133 | 3,923–5,695 |
| 1 s prevalence | 5.9% | 5.1–8.4% |

GPS is missing on 15% of export rows (4% on 15 Sept). Only the mobility block is affected.

---

## 3. The parser bug (`hoproj/data/signalling.py`)

**What was wrong.** The pattern was:

```
physCellId (\d+) , measResult .*? rsrpResult (\d+) , rsrqResult (-?\d+)
```

It used `re.S`, so `.*?` could run past the end of an entry. Two things followed when an entry carried RSRP only (reportQuantity = rsrp, which TS 36.331 §6.3.5 allows):

- **(a)** an RSRP-only entry at the end of the list was dropped;
- **(b)** an RSRP-only entry followed by a full entry received the *second* entry's RSRP/RSRQ, and the second entry was then consumed.

**The fix.** Split the neighbour list per `physCellId`, take each entry's RSRP inside that entry only, and treat RSRQ as optional (NaN when absent). The serving-cell pattern now also accepts RSRP-only, but falls back to the original pattern, so the four Grameenphone logs parse their serving cell exactly as before. Only the neighbour table and `n_neighbours` change.

**Impact on every log:**

| Log | Neighbour rows, old → fixed | Reports with a neighbour, old → fixed | RSRP-only entries | Old rows with a wrong PCI/RSRP pair |
|---|---|---|---|---|
| 10 Sept | 3,747 → 5,234 | 2,518 → 3,562 | 1,615 | 118 |
| 12 Sept | 3,503 → 4,785 | 2,372 → 3,190 | 1,440 | 143 |
| 13 Sept | 3,339 → 4,392 | 2,176 → 2,956 | 1,078 | 23 |
| 15 Sept | 2,450 → 3,607 | 1,718 → 2,500 | 1,309 | 141 |
| **9 Oct** | **16 → 776** | **10 → 628** | 760 | 0 |

The share of modelling rows with a serving-to-neighbour gap feature rises from 52% to 56% on Grameenphone, and from 0.7% to 48% on 9 Oct. A backup of the original file is kept as `signalling.py.bak_20261014`.

---

## 4. Re-evaluation of the four-campaign study (corrected parser)

All stage-22 experiments were re-run on the frozen four campaigns with the corrected parser, in the same environment. Three of the learners do not use neighbour features: dwell-only, history-only and the Hawkes kernel. They reproduce the original tables **bit-for-bit** (0.1055 / 0.1138 / 0.1203). So the differences below are the parser fix, plus LightGBM's multi-thread noise of about ±0.005 on the full feature set.

### 4.1 Main LOCO (Table 5.x / `c3_main_loco`), 1 s

| Learner | AUPRC orig → fixed | Lift | AUROC orig → fixed | ECE fixed |
|---|---|---|---|---|
| **LightGBM** | **0.179 → 0.169** [0.150, 0.196] | 2.63 → 2.49× | 0.777 → 0.773 | 0.014 |
| MLP | 0.173 → 0.168 | 2.54 → 2.47× | 0.755 → 0.762 | 0.017 |
| TCN | 0.167 → 0.163 | 2.45 → 2.40× | 0.755 → 0.756 | 0.022 |
| Transformer | 0.152 → 0.149 | 2.24 → 2.19× | 0.728 → 0.729 | 0.023 |
| GRU | 0.130 → 0.130 | 1.92 → 1.92× | 0.710 → 0.702 | 0.034 |
| Logistic regression | 0.130 → 0.119 | 1.92 → 1.75× | 0.671 → 0.624 | 0.187 |
| Event A3 rule | 0.116 → 0.114 | 1.71 → 1.68× | 0.689 → 0.685 | 0.370 |
| Hawkes / history / dwell | unchanged | | | |

LightGBM still beats every comparator on all four held-out campaigns except logistic regression (3 of 4); the exact sign test is p = 0.125 at n = 4, as before. Per campaign, LightGBM at 1 s with the fixed parser scores 0.199 / 0.223 / 0.198 / 0.125 (10 / 12 / 13 / 15 Sept). The originals were 0.196 / 0.233 / 0.203 / 0.132.

### 4.2 Other experiments

- **Lag ablation** (`c18_ablation`, fixed hyper-parameters): no lag 0.600 → 0.604, lagged 0.160 → 0.157. The headline collapse stands.
- **Coherence** (`c11`): independent heads violate on 38.9% of rows (was 40.2%), isotonic on 44.4% (was 45.9%), hazard on 0%. Unchanged in substance.
- **Risk control** (`c10_crc_frontier`), 1 s, α = 0.20:
  - alarm rate 54.6% → 53.9%, mean per-drive miss 0.153 → 0.156;
  - rotations meeting α: 10/12 → **8/12**.
  - The abstract's "83% of 12 rotations" becomes "67% of 12" (n = 4 campaigns, so this is two rotations flipping).
- **Mechanism** (single-feature AUROC at 1 s, lagged): the A3 gap goes 0.618 → **0.601**, serving SINR is 0.723 in both, dwell is unchanged. The "network triggers on its weakest signal" finding holds and gets slightly stronger.

---

## 5. Blind second-operator test

**Protocol:** the frozen stage-22 protocol, unchanged. Fit and calibration rows come from the four Grameenphone campaigns (temporal calibration split), with nested 20-trial tuning, seeds 0–2, scored on 9 Oct only. This is exactly the 9 Oct fold of leave-one-campaign-out. 883 rows, 52 positives at 1 s, 87 handovers.

**Bootstrap:** brackets are a paired bootstrap over eighteen contiguous 60 s segments. They are *within-session* intervals and do not include between-day or between-operator variance.

| Learner (1 s) | AUPRC [95%] | Lift | AUROC | ECE | Δ AUPRC vs LightGBM [95%] |
|---|---|---|---|---|---|
| LightGBM (primary) | **0.137** [0.099, 0.242] | 2.32× | 0.773 | 0.047 | — |
| Logistic regression | **0.261** [0.137, 0.406] | 4.43× | **0.842** | 0.132 | **+0.124 [+0.025, +0.208]** |
| Hawkes kernel (LR) | 0.192 [0.126, 0.250] | 3.26× | 0.786 | 0.028 | +0.055 [−0.024, +0.085] |
| Dwell time only | 0.190 [0.105, 0.281] | 3.22× | 0.792 | 0.030 | +0.053 [−0.040, +0.115] |
| History block only | 0.175 [0.105, 0.277] | 2.98× | 0.760 | 0.041 | +0.039 [−0.031, +0.101] |
| Event A3 rule | 0.159 [0.093, 0.231] | 2.71× | 0.691 | 0.349 | +0.023 [−0.045, +0.053] |
| MLP | 0.135 [0.101, 0.218] | 2.29× | 0.767 | 0.058 | −0.002 [−0.056, +0.044] |
| Transformer | 0.143 | 2.43× | 0.792 | 0.040 | |
| GRU | 0.144 | 2.44× | 0.787 | 0.037 | |
| TCN | 0.136 | 2.31× | 0.775 | 0.046 | |

The three sequence models are not in the bootstrap; they land at LightGBM's level, 0.136–0.144.

At 5 s: LightGBM 0.357 (1.8×); logistic regression 0.552 (Δ +0.195 [+0.090, +0.261]); Hawkes 0.526; A3 rule 0.355.

### What this says

- **The formulation transfers; the model choice does not.** On the new operator, the hazard LightGBM's lift (2.3×) and AUROC (0.773) sit inside its Grameenphone per-campaign range. It loses its lead, though. The simplest model, logistic regression, ranks best, and the models that use only handover history are competitive.
- **Where the loss comes from.** The neighbour/radio block appears not to transfer between operators. With the *old* parser (9 Oct neighbour features almost all missing), the same fixed-parameter LightGBM scored 0.176 on 9 Oct; with them present it scores 0.122. This is post-hoc and should be stated as a hypothesis, not a result. Banglalink reports RSRP only, configures different offsets, and hands over mostly between carriers, so neighbour-gap features mean something different there.
- **Calibration.** Logistic regression ranks best but is badly calibrated (ECE 0.13). LightGBM and the history models stay calibrated (ECE ≤ 0.05).
- **Scale.** This is one 17-minute session. It is a single external data point, not an estimate of cross-operator performance.

---

## 6. Confirmatory checks on 9 Oct (pre-specified by the four-campaign work)

**Alignment audit (`c32_alignment_audit_per_campaign`).** Share of handovers whose target cell already serves in the export row at each offset:

| | t−3 | t−2 | t−1 | **t+0** | t+1 |
|---|---|---|---|---|---|
| 9 Oct, all (87) | 0.138 | 0.080 | 0.046 | **0.667** | 0.885 |
| 9 Oct, isolated (20) | 0 | 0 | 0 | **0.650** | 0.950 |
| GP, all, per campaign | 0.19–0.35 | 0.15–0.30 | 0.13–0.19 | 0.67–0.81 | 0.83–0.88 |

The end-of-second flip replicates on a different operator's network with the same instrument. The one-row lag was fixed before this capture existed.

**Lag inflation on 9 Oct** (fixed-parameter LightGBM trained on Grameenphone):

| | AUPRC | Lift | AUROC |
|---|---|---|---|
| Lag 0 (v1 alignment) | 0.512 | 8.7× | 0.874 |
| Lag 1 (as reported) | 0.119 | 2.0× | 0.754 |

That is 4.3× inflation on 9 Oct, against 3.8× on Grameenphone. The thesis's main methodological claim now holds on a held-out operator.

**Risk control transferred to 9 Oct.** Fitted on two Grameenphone campaigns, calibrated on a third, tested on 9 Oct (`oct9_crc_test_rotations.csv`). At 1 s, α = 0.20, all four rotations are feasible. The realised per-drive miss is 0.03–0.08, well under α, at alarm rates of 44–69%. The bound holds but is conservative. There are six 180 s units in the test session, so this is descriptive only.

---

## 7. Network characterisation

| | 9 Oct (Banglalink) | GP campaigns |
|---|---|---|
| Dominant trigger | **A5, TTT 480 ms (37%)**; A3 +5 dB/320 ms (26%); A3 −10 dB/640 ms (9%) | A3 +1 dB/320 ms (44–54%) |
| Negative-offset A3 share of handovers | 9% | 16–19% |
| A3 reports declined (per report) | 64.3% | 57.2–71.6% |
| A3 episodes declined (one-to-one) | **87.1%** | 71.1–76.9% |
| A3 episodes with no command within 2 s | **64.2%** | 26.7–35.1% |
| Ping-pong, previous cell PCI+carrier 15 s | **13.8%** | 19.5–40.3% |
| PCI only / any return | 18.4% / 29.9% | 25.4–45.5% / 36.7–64.2% |
| Ping-pong intra- vs inter-frequency | **5.6% (n=36) vs 19.6% (n=51)** | intra ≫ inter, e.g. 23.0% vs 7.4% (10 Sept) |
| Hawkes branching ratio | 0.83 (one short session) | 0.49–0.67 |

On Banglalink, A3 reports are a weaker proxy for an imminent handover than on Grameenphone. Handovers there are driven more by A5 and by inter-frequency mobility.

---

## 8. What changes in the manuscript

**Must change (parser fix):**

1. **Abstract, §1.6, Table 5.4 / main LOCO, §7.1:** 1 s AUPRC 0.179 → 0.169, lift 2.6× → 2.5×, AUROC 0.777 → 0.773. Re-quote every derived number from `reports_rev_parserfix/tables`.
2. **§3.3 (signalling decoding):** one sentence on the optional RSRQ field and the fix. **§5.13 (threats):** the neighbour-feature coverage figure (52% → 56%).
3. **Risk control:** "83% of 12 rotations" becomes 67% (8/12). Keep the n = 4 caveat next to it.
4. **§5.8:** the A3 gap AUROC 0.618 → 0.601, wherever it is quoted.

**Should add (second operator):**

5. A new §5.x, "Blind test on a second operator", built from §5–6 of this document. It strengthens the two central methodological claims: the alignment flip and the lag inflation replicate blind. It also states honestly that the model ranking does not transfer.
6. **§5.10:** soften "the carrier relationship / TTT is the lever" to "on Grameenphone"; on Banglalink the carrier pattern reverses.
7. **§7.2 / §7.3:** the second-operator limitation is now partly addressed, with one short session. Keep the recommendation for a longer second-operator campaign.
8. **Primary-model language** (reviewer concern about post-hoc selection): say plainly that LightGBM's lead is within-operator. On the blind operator, logistic regression and the history-only baselines rank higher.

**Do not:**

- Pool 9 Oct into the headline LOCO. It would stop being blind, and it is a different operator.
- Re-tune anything on it.

Five-campaign pooled tables exist under `second_operator/reports/tables` for reference only. In those, the "urban campaigns" ping-pong stratum includes 9 Oct.

---

## 9. Reproduction

```
cd pipeline
# raw files: oct09/data/raw/oct-9-2026.csv and oct-9-2026.txt (same convention as sept10 … sept15)
python -m hoproj.pipeline.stage12_xcal_prepare      # 4 GP campaigns, corrected parser
python -m hoproj.pipeline.run_revision --offline    # → reports_rev (now corrected-parser numbers)
python -m hoproj.pipeline.stage32_second_operator   # → second_operator/reports/tables (c32_*)
```

The data/rev pickles that stages 22–31 read had no builder in `src/`. `stage32_second_operator.build_pickles` now provides one; it is the same construction used for every number above.

**Environment for these runs:** Python 3.11, pandas 2.3.3, scikit-learn 1.8.0, LightGBM 4.7.0, torch 2.14. Rows, prevalences and the three non-neighbour baselines reproduce the original tables exactly.

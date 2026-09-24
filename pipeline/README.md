# Uncertainty-Aware Multi-Horizon LTE Handover and QoE Forecasting

Training pipeline implementing the thesis *"Uncertainty-Aware Multi-Horizon
LTE Handover Prediction from Drive-Test Signalling"*.

The pipeline's organising principle is **trustworthy, leakage-free generalisation**:
- Grouped whole-drive splits are strictly enforced across 57 drives.
- Dynamic ASN.1 RRC Connection Reconfiguration timeline tracking fixes stateful `measId` and `reportConfigId` misattribution.
- Multi-horizon prediction is formulated via discrete-time survival hazard analysis ($S(t) = \prod_{k \le t}(1 - h(k))$) to guarantee 0% monotonicity violations.
- Conformal Risk Control (CRC) establishes finite-sample, distribution-free risk guarantees ($\mathbb{E}[L] \le \alpha$) on missed handovers.
- All deep sequence baselines are tuned with an identical 50-trial Optuna Bayesian search budget.
- Independent cross-dataset transfer (Astana public dataset) and leave-one-capture-out (LOCO) highway transfer evaluate domain bounds.

---

## Quick Start (Modern XCAL Pipeline)

```bash
# Set Python path to include src
export PYTHONPATH=$PWD/src            # Linux / macOS
$env:PYTHONPATH="D:\Handover Thesis\pipeline\src"  # Windows PowerShell

# Run the complete modern XCAL pipeline (Stages 12 to 21)
python -m hoproj.pipeline.run_all

# Or run any specific stage:
python -m hoproj.pipeline.run_all --stage stage12   # Materialise pooled XCAL dataset
python -m hoproj.pipeline.run_all --stage stage13   # Grouped K-fold benchmark across models
python -m hoproj.pipeline.run_all --stage stage14   # Fair hazard coherence & calibration evaluation
python -m hoproj.pipeline.run_all --stage stage15   # Hawkes point process GoF & Conformal Risk frontier
python -m hoproj.pipeline.run_all --stage stage16   # Signalling ablation & ping-pong definitions
python -m hoproj.pipeline.run_all --stage stage17   # Generate manuscript figures
python -m hoproj.pipeline.run_all --stage stage18   # 50-trial Bayesian tuning budget ablation
python -m hoproj.pipeline.run_all --stage stage19   # Astana transfer & UDA CORAL/MMD negative result
python -m hoproj.pipeline.run_all --stage stage20   # Shafi et al. RL departmental baseline comparison
python -m hoproj.pipeline.run_all --stage stage21   # Leave-One-Capture-Out highway transfer
```

Everything lands in:
- `reports_xcal/tables/` (CSV tables)
- `reports_xcal/figures/` (PNG publication figures)
- `artifacts_xcal/` (serialized metadata and cache)

---

## Pipeline Architecture & Stages

| Stage | Name | Description | Output Table / Artifact |
|:---:|---|---|---|
| **00** | `stage00_field_dictionary` | Evaluates raw XCAL variable availability and feasibility. | `xcal_field_dictionary.csv` |
| **01** | `stage01_prepare` | Legacy ingestion & segmentation of curated pilot drives. | `data/processed/` |
| **02** | `stage02_experiment` | Legacy model grid on curated data. | `reports/tables/main_results.csv` |
| **03** | `stage03_uncertainty` | Deep ensemble & temperature scaling on curated data. | `reports/tables/uncertainty.csv` |
| **04** | `stage04_external` | Locked external route evaluation on curated data. | `reports/tables/external.csv` |
| **05** | `stage05_report` | Consolidates legacy report tables. | `reports/consolidated_report.md` |
| **06** | `stage06_cross_capture` | Initial cross-capture transfer matrix. | `reports/tables/cross_capture.csv` |
| **07** | `stage07_regime_transfer` | Context-rich vs. topology-agnostic regime transfer. | `reports/tables/regime_transfer.csv` |
| **08** | `stage08_public_dataset` | Ingestion and benchmark on Astana public LTE dataset. | `reports/tables/public_astana.csv` |
| **09** | `stage09_hazard` | Initial discrete-time hazard formulation prototype. | `reports/tables/hazard_prototype.csv` |
| **10** | `stage10_riskcontrol` | Initial Conformal Risk Control calibration prototype. | `reports/tables/riskcontrol_proto.csv` |
| **11** | `stage11_mechanism_benefit` | Single-feature power analysis & early-warning benefit envelope. | `reports/tables/benefit_proto.csv` |
| **12** | `stage12_xcal_prepare` | **THE Core Ingestion Stage.** Pools all 4 measured campaigns (Sept 10, 12, 13, and 15 highway corridor; 57 drives, 10,260 s, 938 HOs). Reconstructs stateful ASN.1 RRC timeline. | `data/processed_xcal/` |
| **13** | `stage13_xcal_benchmark` | **Primary Empirical Benchmark.** Grouped K-fold rotation over all 57 drives. Out-of-fold metrics across LightGBM, Logistic Regression, MLP, GRU, TabNet, and A3 rule. | `reports_xcal/tables/xcal_main.csv` |
| **14** | `stage14_hazard_fair` | **Survival Coherence & Calibration.** Evaluates discrete hazard model vs. independent multi-head classifiers. Proves 0% monotonicity violations and ECE 0.037. | `reports_xcal/tables/hazard_fair_summary.csv` |
| **15** | `stage15_gof_frontier` | **Hawkes GoF & Conformal Risk.** Fits Hawkes self-exciting point process (branching ratio $n=0.611$) and computes empirical loss vs. alarm budget across $\alpha \in (0, 1)$. | `reports_xcal/tables/risk_control_frontier.csv` |
| **16** | `stage16_signalling_pingpong` | **Feature Ablation & Ping-Pong Sensitivity.** Compares Full vs. RF+Mob+Hist vs. Signalling Only across horizons. Quantifies ping-pong definition sensitivity (24.5%–41.3%). | `reports_xcal/tables/signalling_ablation.csv` |
| **17** | `stage17_figures` | Generates publication-ready figures from XCAL experimental tables. | `reports_xcal/figures/` |
| **18** | `stage18_tuning_budget` | **Controlled Hyperparameter Tuning.** Provides identical 50-trial Optuna Bayesian search budgets to all model families, isolating inductive bias from under-tuning. | `reports_xcal/tables/tuning_budget_all.csv` |
| **19** | `stage19_transfer_adaptation` | **Zero-Shot Transfer & Domain Adaptation.** Evaluates cross-dataset transfer to Astana LTE data and audits CORAL/MMD feature alignment negative results. | `reports_xcal/tables/transfer_adaptation_summary.csv` |
| **20** | `stage20_departmental_baseline` | **Head-to-Head Departmental Comparison.** Faithful re-implementation of Shafi et al.'s Q-learning reinforcement learning baseline on our drive-test dataset. | `reports_xcal/tables/departmental_baseline_summary.csv` |
| **21** | `stage21_capture_transfer` | **Leave-One-Capture-Out (LOCO) Highway Transfer.** Evaluates model trained on 25 km/h urban drives against unseen 60 km/h highway corridor (Capture 4). | `reports_xcal/tables/capture_transfer.csv` |

---

## Leakage Prevention Protocol

1. **Grouped Whole-Drive Holdouts:** Samples are partitioned strictly by complete vehicle trip. Adjacent 1 Hz seconds from the same run never cross between train and test folds.
2. **Causal Backward Features:** Rolling averages and derivatives are strictly backward-looking ($t-L+1 \dots t$).
3. **Strict Feature Causal Ordering:** Signalling measurement report features count reports in strictly preceding windows ($t-W \dots t-1$). The current time bin $[t-1, t)$ is firewalled to prevent target leakage.
4. **Fitted-Inside-the-Fold Preprocessing:** Scaling, imputation, calibration temperatures, and conformal thresholds are fitted strictly on training/calibration folds.

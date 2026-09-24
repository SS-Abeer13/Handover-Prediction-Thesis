# Pipeline Notebooks

This folder contains interactive Jupyter notebooks and pre-rendered HTML reports for the thesis pipeline:
* **`results_visualisation.ipynb`** (and pre-rendered **`results_visualisation.html`**): Interactive results visualization covering the complete progression of the study from initial formulation to the final multi-carrier audited revision.
* **`handover_pipeline.ipynb`**: End-to-end model training, evaluation, and revision runner pipeline.

---

## Structure of `results_visualisation.ipynb`

The visualization notebook is organized into three distinct parts reflecting the chronological and methodological evolution of the research:

### Part I: Pre-Audit Baseline Pipeline (Stages 1–11)
* Initial formulation on the 57-drive development corpus.
* Unlagged feature extraction and grouped-drive cross-validation.
* Development vs. locked-route evaluation.
* *Note: Kept for provenance and historical comparison as the baseline overturned by the audit.*

### Part II: Modern XCAL Signalling Visualisation (Stages 12–21)
* Introduction of 1 Hz pooled XCAL L3 RRC signalling data.
* Initial discrete-time survival hazard formulation and monotonicity checks.
* Equal 50-trial Bayesian tuning budget (Optuna).
* Departmental baseline comparison (Shafi et al. Q-learning re-implementation).

### Part III: Audited Revision & Multi-Carrier Alignment Replication (Stages 22–31)
* **8.1 Timestamp Alignment Audit (Grameenphone XCAL):** Proof that row $t+0$ suffers 74.6% cell identity contamination, dropping to 0.0% at row $t-1$.
* **8.2 External Replication on US Tier-1 Carriers (NUWiNS PAM 2025):** Independent replication on AT&T (91.1% isolated) and T-Mobile (95.6% isolated) XCAL traces, confirming 0.0% contamination under strict row lag ($t-1$).
* **8.3 Sub-Second Native RRC Signalling Audit:** 100 ms millisecond-accurate RRC analysis establishing the 40–80 ms physical execution interruption window.
* **8.4 Cross-Instrument Synthesis:** Synthesis comparing continuous 1 Hz logging (Grameenphone), instantaneous discrete sampling (Irish MMSys 2020 G-NetTrack), and dual-rate logging (NUWiNS).
* **8.5 Protocol Ladder & Lag Inversion:** Evaluation protocol ladder (Random Row $\to$ Grouped Drive $\to$ LOCO) and the 0.607 (lag-0 leaked) vs. 0.179 (lag-1 audited) AUPRC overturn.
* **8.6 Leave-One-Campaign-Out (LOCO) Benchmark:** Multi-horizon comparisons across 6 architectures (LightGBM, Logistic Regression, MLP, GRU, TCN, Transformer).
* **8.7 Discrete-Time Survival Hazard Coherence:** 0.0% monotonicity violations vs. 14.8% for unconstrained binary heads.
* **8.8 Conformal Risk Control (CRC) Frontier:** Distribution-free finite-sample miss-rate bounds ($\alpha \in \{0.05, 0.10, 0.15, 0.20\}$).
* **8.9 Audited Feature Power Inversion:** Dwell time (0.874 AUROC) vs. A3 threshold quantity (0.566 AUROC) and feature block ablation.
* **8.10 A3 Measurement Report Conversion Non-Determinism:** Proves only 34.6% of A3 episodes convert to handover commands.
* **8.11 Temporal Point Processes & Hawkes Self-Excitation:** Quantifying secondary handover clustering ($n \approx 0.61–0.67$).
* **8.12 Sensitivity Analysis & Case Studies:** Robustness to purge windows and unsifted TP/FP/FN trajectories.

---

## Quick Viewing

To inspect all high-resolution figures, tables, and narrative without running Jupyter:
Open **`results_visualisation.html`** in any web browser.

---

## Running the Notebooks

Both notebooks import from `../src` (`hoproj`).

### Setup with Conda / Python 3.12+

```bat
cd "D:\Handover Thesis\pipeline"
python -m pip install -r requirements.txt
python -m pip install jupyterlab nbconvert
jupyter lab notebooks\results_visualisation.ipynb
```

### Headless Execution & HTML Re-generation

To re-execute all cells and export to standalone HTML:

```bat
cd "D:\Handover Thesis\pipeline"
python -m nbconvert --to notebook --execute --inplace notebooks\results_visualisation.ipynb
python -m nbconvert --to html notebooks\results_visualisation.ipynb
```

---

## Reproducing the Entire Thesis Pipeline via CLI

To re-run the complete revision pipeline (Stages 22 to 31) programmatically:

```bat
cd "D:\Handover Thesis\pipeline"
python -m hoproj.pipeline.run_revision            REM runs all stages 22 to 31
python -m hoproj.pipeline.run_revision --offline  REM skips stage 28 download
make manuscript                                  REM rebuilds and validates manuscript .docx
```

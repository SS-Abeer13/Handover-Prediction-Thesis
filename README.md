# Conformalized Discrete-Time Hazard Modeling for Multi-Horizon Handover Forecasting in Cellular Networks

[![Thesis Status](https://img.shields.io/badge/Thesis-Completed-success.svg)](#)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Academic%20Use%20Only-lightgrey.svg)](#)

> **B.Sc. Project and Thesis**  
> Department of Electrical and Electronic Engineering  
> Islamic University of Technology (IUT), Organization of Islamic Cooperation (OIC), Gazipur, Bangladesh  
>
> **Candidates:**  
> - **Saadman Sakib** (Student ID: 210021110)  
> - **Adhnan Kalim** (Student ID: 210021308)  
> - **Evan Ashfaque** (Student ID: 210021335)  
> 
> **Supervisor:**  
> - **Dr. Mohammad Tawhid Kawser**, Professor, Department of EEE, IUT  

---

## 📌 Abstract

LTE hands over using Event A3, a reactive rule that can only fire *after* the radio link has already deteriorated. This thesis asks whether the next handover can be anticipated in advance, how far ahead, and with what rigorous statistical guarantee.

Using four extensive drive-test campaigns across Dhaka and Gazipur (57 quality-controlled drives, 10,260 1 Hz samples, and 938 handovers with ground truth decoded directly from RRC signalling via XCAL-M), a gradient-boosted hazard model predicts the next handover 1 to 5 seconds ahead at **AUROC 0.933** and **AUPRC 0.784** against a 6.7% prevalence floor (11.7× lift), with well-calibrated probabilities (ECE 0.024) and distribution-free Conformal Risk Control bounds ($\mathbb{E}[L] \le \alpha$).

The predictive validity holds out-of-sample on an unseen high-speed highway corridor (Uttara–Gazipur, 49.5 km/h mean speed) with AUROC 0.927. A systematic benchmark across 22 published studies demonstrates that this framework is the first to simultaneously deliver multi-horizon lead time, group-safe evaluation, and finite-sample risk control.

---

## 📂 Repository Structure

```text
├── 00-INDEX.md                     # Index and chronological reading guide of all research reports
├── 01-27-*.md                      # 27 sequential research reports and audit milestones
├── MASTER-Handover-Prediction.md   # Complete technical documentation & monograph (self-contained)
├── Thesis-Synopsis.md              # Thesis synopsis document
├── Thesis-Synopsis.pdf             # Compiled synopsis PDF
├── pipeline/                       # Full Python experimental pipeline and reproduction code
│   ├── src/hoproj/                 # Pipeline source code (stages 00 through 30)
│   ├── configs/                    # Experiment configuration files
│   ├── notebooks/                  # Analysis and visualization Jupyter notebooks
│   ├── tests/                      # Automated test suite
│   ├── reports_xcal/               # Publication figures and benchmark tables
│   ├── pyproject.toml              # Dependencies and project definition
│   └── README.md                   # Pipeline reproduction guide
├── latex/                          # Complete LaTeX source of thesis manuscript and appendices
│   ├── main.tex                    # Master LaTeX document
│   ├── chapters/                   # Thesis chapters
│   ├── appendices/                 # Extended appendices
│   └── references.tex              # Comprehensive bibliography
├── Drivetest Data/                 # Empirical drive-test campaign logs and signalling decodes
├── Presentation/                   # Thesis defence slide deck, script, and presentation figures
├── Docs/                           # Proposal, literature review, OBE forms, and documentation
├── figures/                        # Core manuscript and mechanism figures
└── tools/                          # Manuscript and table verification utilities
```

---

## 🚀 Quick Start (Reproduction Pipeline)

The pipeline is organized in modular stages (`stage00` to `stage30`):

```bash
cd pipeline

# Install dependencies (Python 3.11+)
pip install -e .

# Run the complete modern XCAL pipeline (Stages 12 to 21)
python -m hoproj.pipeline.run_all

# Or run specific stages:
python -m hoproj.pipeline.run_all --stage stage12   # Materialise pooled XCAL dataset
python -m hoproj.pipeline.run_all --stage stage13   # Grouped K-fold benchmark across models
python -m hoproj.pipeline.run_all --stage stage14   # Fair hazard coherence & calibration evaluation
python -m hoproj.pipeline.run_all --stage stage15   # Hawkes point process GoF & Conformal Risk frontier
python -m hoproj.pipeline.run_all --stage stage16   # Signalling ablation & ping-pong definitions
python -m hoproj.pipeline.run_all --stage stage17   # Generate manuscript figures
python -m hoproj.pipeline.run_all --stage stage21   # Leave-One-Capture-Out highway transfer
```

Output figures and tables are written to `pipeline/reports_xcal/figures/` and `pipeline/reports_xcal/tables/`.

---

## 📖 Key Findings & Contributions

1. **Survival Hazard Formulation:** Formulating handover forecasting as discrete-time hazard analysis ($S(t) = \prod_{k \le t}(1 - h(k))$) eliminates 100% of multi-horizon monotonicity violations inherent in independent multi-head classifiers.
2. **Leakage-Free Protocol:** Grouped whole-drive splits across 57 drives prevent temporal data leakage that inflates baseline metrics in prior literature.
3. **Conformal Risk Control (CRC):** Provides finite-sample, distribution-free statistical risk guarantees on missed handovers without distributional assumptions.
4. **Signalling-Informed Ground Truth:** Dynamic ASN.1 RRC Connection Reconfiguration timeline tracking decouples true handover executions from unacted A3 measurement reports.
5. **Domain Transfer:** Validated across urban and highway driving regimes, demonstrating out-of-domain robustness.

For an extensive reading guide, refer to [`00-INDEX.md`](00-INDEX.md) and [`MASTER-Handover-Prediction.md`](MASTER-Handover-Prediction.md).

---

## 🎓 Citation & Contact

For academic inquiries or citation information regarding this thesis project:
- Islamic University of Technology (IUT), Gazipur, Bangladesh
- GitHub: [@SS-Abeer13](https://github.com/SS-Abeer13)

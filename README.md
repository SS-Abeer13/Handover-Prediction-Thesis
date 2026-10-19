# Conformalized Discrete-Time Hazard Modeling for Multi-Horizon Handover Forecasting in Cellular Networks

> **B.Sc. Project and Thesis**, Department of Electrical and Electronic Engineering,
> Islamic University of Technology (IUT), Gazipur, Bangladesh
>
> **Authors:** Saadman Sakib (210021110), Adhnan Kalim (210021308), Evan Ashfaque (210021335)
> **Supervisor:** Dr. Mohammad Tawhid Kawser, Professor, Department of EEE, IUT
>
> **Journal manuscript derived from this thesis:** `paper/` (*One row too late: timestamp-alignment leakage in drive-test handover prediction, its cost, and a blind second-operator test*)

---

## Read this first: which numbers are current

An early version of this project reported a one-second AUPRC of about 0.78 (AUROC about 0.93). **That result is retracted.** An audit of the one-hertz XCAL export against decoded RRC timestamps found that the export row stamped just before a handover command already carries the post-handover serving cell in 76% of handovers, which shows the model the answer. Every result below comes from features lagged by one row, leave-one-campaign-out evaluation, and the corrected measurement-report parser.

| Quantity (operator A, 4 campaigns, LOCO) | Value |
|---|---|
| Handover commands (raw / quality-controlled) | 957 / 938 |
| One-hertz samples / prediction rows | 10,260 / 8,586 |
| Export row before the command already shows the target cell | 75.9% (15.6% one row earlier) |
| 1 s AUPRC, same model, unlagged vs lagged features | 0.604 vs 0.156 (3.9-fold) |
| Share of that fall due to serving-cell radio scalars | 94% |
| 1 s AUPRC, tuned LightGBM (floor 6.8%) | 0.169, range over held-out campaigns 0.125–0.223, AUROC 0.773 |
| 5 s AUPRC (floor 26.1%) | 0.454, range 0.385–0.531 |
| Random-row split inflation over LOCO (LightGBM / logistic regression) | +49% / +8% |
| Commands detected at 1 s, 5% FPR threshold | 33% at 169 false alarms per hour, median lead 0.50 s |

**What is exploratory and what is blind.** The four operator-A campaigns are exploratory. The alignment repair was derived with all four in view, so Campaign 4 (highway) is held out from model fitting but is **not** blind to pipeline design. A fifth capture on a second operator (operator B, 9 Oct 2026) was recorded after the freeze. It is blind to every pipeline decision, and it replicates the leakage findings: 66.7% at the command row, and 4.3-fold inflation. The ranking of learners does **not** transfer: logistic regression scores 0.261, and LightGBM scores 0.137. The public dataset of Shafi et al. (Mendeley Data, doi:10.17632/n2pvmtyn2j.2) is a **same-institution** replication: same operator and city, collected by an earlier cohort in this department.

Conformal risk control is reported as an empirical calibration diagnostic, not as an operating guarantee. Campaigns are not exchangeable, and the 12 cross-campaign rotations are pseudoreplicates of 4 sessions.

---

## Repository layout

```text
├── paper/                    Journal manuscript (elsarticle) and its figures
├── latex/                    Thesis LaTeX source (main.tex, chapters/, appendices/)
├── pipeline/
│   ├── src/hoproj/           Pipeline source
│   │   ├── pipeline/         Stages 00–32 (current results: stages 22–32)
│   │   ├── revision/         Revision data builders, alignment audit, protocols
│   │   └── data/signalling.py  RRC decoding (corrected RSRP-only neighbour parser)
│   ├── reports_rev_parserfix/  Tables behind every number in the thesis and paper
│   ├── reports_rev/          Earlier run with the original parser, kept as evidence
│   ├── second_operator/      Blind operator-B test (stage 32) tables
│   └── reports_xcal/         Pre-audit v1 pipeline output (retracted; kept as evidence)
├── Drivetest Data/           Raw XCAL exports and decoded signalling logs
├── 00-INDEX.md, 01–28-*.md   Research log, in chronological order
└── Presentation/, Docs/      Defence material and working documents
```

## Reproducing the current results

```bash
cd pipeline
pip install -e .
export PYTHONPATH=$PWD/src          # Windows PowerShell: $env:PYTHONPATH="$PWD\src"

python -m hoproj.pipeline.run_revision             # stages 22–31 (stage 28 needs network access)
python -m hoproj.pipeline.stage32_second_operator  # blind operator-B test
```

- Stage 22 runs the alignment audit, the lag decomposition, the protocol ladder, the main leave-one-campaign-out comparison, coherence, risk control and the ablation.
- Stage 22 writes to `reports_rev/tables`. The thesis and paper quote the corrected-parser run, which is archived in `reports_rev_parserfix/tables`.
- `run_all.py`, the Makefile and the notebooks reproduce the **pre-audit** v1 study (stages 1–21). They are kept only as the evidence the audit overturned.

The alignment audit is `row_alignment_audit()` in `pipeline/src/hoproj/revision/data.py`.

## Citation

Please cite the archived release (see `CITATION.cff`). The Zenodo DOI is added on the first archived release.

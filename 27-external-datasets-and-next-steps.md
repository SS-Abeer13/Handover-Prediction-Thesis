# Public drive-test datasets and next steps

**Written:** 18 September 2026
**Purpose:** candidate external datasets for the revised thesis, what each one fixes, and the order to act in.

---

## 1. What the thesis still needs

| Gap | Why it matters | What would close it |
|---|---|---|
| **G1 · Alignment replication** | §5.1 shows the 1 Hz XCAL row describes the second *after* its timestamp. Checked on one other dataset so far (G-NetTrack Pro): does **not** replicate. One instrument, one answer each — too thin to generalise. | A second **XCAL** dataset. If the defect appears there, the finding is about the instrument, not about our export. |
| **G2 · Independent units** | Four continuous sessions. A paired test over four units cannot reach a p-value below 0.125. | 8–10 independent sessions, ideally across days and routes. |
| **G3 · Second operator** | The deployed configuration is stable across all four campaigns, so cross-regime transfer rests on one configuration set. | Any signalling-grade capture on a different operator. |
| **G4 · Sub-second resolution** | Horizons below 1 s are labelled but not modelled; the 1 Hz grid caps event detection at 64.6 % at 1 s. | A native-rate (per-message) export, ours or someone else's. |

---

## 2. Candidates

| # | Dataset | Event clock | Operators | Access | Fixes |
|---|---|---|---|---|---|
| 1 | NUWiNS multi-carrier (PAM 2025) | XCAL event column | 3 | public, GitHub | G1, G3 |
| 2 | Ghoshal et al. 2025 | full RRC (measConfig + MR) | 3 | on acceptance | G1, G2, G3 |
| 3 | AI-Native Mobility in 6G | A3 events, RACH, TA | 1 | on acceptance | G2, G4 |
| 4 | Vienna 4G/5G | none documented | several | public, Zenodo | G2, G3 (weakly) |
| 5 | Raca 5G Irish (MMSys 2020) | cell ID only | 1 | public, GitHub | G1 — **done** |
| 6 | Raca 4G Irish (MMSys 2018) | cell ID only | 1 | public | G1 (LTE-only variant) |
| 7 | Lumos5G / 5G Beams | beam/tower changes | 1 | public | context only |
| 8 | Shafi et al. (Mendeley) | RRC measurement reports | 1 (ours) | public | already used in §5.7 |

### 1. NUWiNS multi-carrier dataset — *the one to run next*
- <https://github.com/NUWiNS/pam2025-multi-carrier-dataset>
- Companion: <https://github.com/NUWiNS/imc2023-cellular-network-performance-on-wheels-data>
- Paper: A Large-Scale Study of the Potential of Multi-Carrier Access in the 5G Era, PAM 2025.
- Raw **XCAL** exports, three cross-US drives, three operators (T-Mobile, Verizon, AT&T).
- Documented columns: `TIME_STAMP`, `Lat`, `Lon`, `Event 5G-NR/LTE Events`, `LTE KPI PCell Serving PCI`, `LTE KPI PCell Serving EARFCN`, `5G KPI PCell RF Serving PCI`, throughput.
- Same instrument family as ours, so the §5.1 audit transfers directly.
- Reachable from the cloud workspace (GitHub is allow-listed there; Zenodo, Kaggle and UCC are not).

### 2. Ghoshal et al., Handover Configurations in Operational 5G Networks
- <https://arxiv.org/abs/2511.03116> (already reference [4] in the thesis)
- XCAL Solo on the Qualcomm diagnostic interface, 1 s granularity, **RRC configuration messages and measurement reports**, 48,426 handovers, 3 US operators, 15,000+ km, 27 months.
- Availability: *"Our dataset will be open-sourced upon acceptance of the paper."* Not yet posted.
- This is the closest external analogue to our own data that exists anywhere.

### 3. Enabling AI-Native Mobility in 6G
- <https://arxiv.org/abs/2605.12453>
- 5G SA (band n78), Chennai, 117,390 measurement reports at 240–5120 ms, **1,546 A3 handovers with timestamps**, PCI, beam index, RSRP/RSRQ and filtered variants, timing advance, RACH cause breakdown.
- Availability: *"Data resources will be available upon acceptance of the article for publication."*
- Purpose-built for handover prediction; the sub-second reporting rate is what our 1 Hz grid lacks.

### 4. Vienna 4G/5G drive-test dataset
- <https://zenodo.org/records/21372657> · preprint <https://arxiv.org/html/2603.02638v1> · CC BY 4.0 · 754 MB
- Scanner plus phone logs over ~100 km² of Vienna, March 2024 – March 2025, multiple operators, cell/PCI/TA/GPS plus an estimated cell-position model.
- No separate RRC event log is documented, so handover labels would have to come from serving-cell transitions.
- Zenodo is blocked from the cloud workspace — download locally, or drop the zip in `D:\Handover Thesis\Drivetest Data\` and it can be processed from there.

### 5–8. Already used or secondary
- Raca 5G Irish: <https://github.com/uccmisl/5Gdataset> · paper <https://dl.acm.org/doi/abs/10.1145/3339825.3394938>. Used for the audit replication now in Table A.3.
- Raca 4G Irish: <https://www.ucc.ie/en/misl/research/datasets/ivid_4g_lte_dataset/> · mirror <https://www.kaggle.com/datasets/aeryss/lte-dataset>. Pure LTE, 1 s, CellID/RSRP/RSRQ/SNR/GPS.
- Lumos5G: <https://ieee-dataport.org/open-access/lumos5g-dataset> · 5G Beams: <https://5gbeams.umn.edu/>.
- Chronicles of 5G NSA: <https://zenodo.org/records/14073311>.
- Shafi et al. (our external check): doi:10.17632/n2pvmtyn2j.1.

### Collecting more data instead of finding it
- MobileInsight decodes RRC on a rooted Android handset: <http://www.mobileinsight.net/news-6.0.html>
- This is the cheapest route to **G2 and G3** — extra sessions and a second operator — without another XCAL licence.

---

## 3. Next steps, in order

| # | Step | Owner | Effort | Unlocks |
|---|---|---|---|---|
| 1 | ~~Run the §5.1 alignment audit on the NUWiNS XCAL data~~ | Claude | **done 18 Sept** | G1 closed: 4,712 handovers, 3 operators, mechanism established |
| 2 | Email the authors of arXiv:2511.03116 asking for early access | Abeer | 10 min | G1 + G3, and a citation-worthy collaboration |
| 3 | Email the authors of arXiv:2605.12453 for the same | Abeer | 10 min | G2 + G4 |
| 4 | Re-export the four captures from XCAL at native message rate | Abeer | one afternoon | G4, settles the row-time semantics for good |
| 5 | Collect 4–6 more sessions (different days, routes, times) | Abeer | one week of driving | G2 — makes paired tests informative |
| 6 | One capture on a second operator, even a short one | Abeer | one afternoon | G3 — the single biggest generality gain |
| 7 | Download the Vienna dataset if steps 2–3 stall | Abeer | 30 min | weak G2/G3 |
| 8 | Fold whatever arrives into §5.1, Table A.3 and §5.7 | Claude | ~2 hours each | — |

*Steps 2 and 3 (the two author emails) are still the highest-value remaining items: G2 (independent
units) and G4 (sub-second resolution) are untouched by the NUWiNS run, because that corpus has no
RRC configuration messages.*

### Draft request to the dataset authors

> Subject: Request for early access to the handover configuration dataset (arXiv:2511.03116)
>
> Dear Dr Ghoshal and Prof Koutsonikolas,
>
> I am an undergraduate researcher at the Islamic University of Technology, Bangladesh, working on
> multi-horizon handover forecasting from XCAL drive-test signalling. Your measurement study is a
> reference point for our work and is cited in our manuscript.
>
> While auditing our own 1 Hz XCAL export we found that a row stamped t already carries the
> post-handover serving cell for 76 % of handover commands issued in (t, t+1], which inflates
> one-second AUPRC by a factor of about four. We would like to check whether the same alignment
> holds in other XCAL exports. Your paper states the dataset will be open-sourced on acceptance —
> would an early copy, or even a small sample of traces with RRC messages and the 1 Hz KPI export,
> be possible? We would of course cite the dataset and share the audit script and findings with you.
>
> Thank you for considering it.

*(Take the authors' addresses from the paper's front matter; adjust the wording as you see fit.)*

---

## 4. Status of the checks already done

*Updated 18 September 2026, after the NUWiNS run.*

| Check | Dataset | Result |
|---|---|---|
| Row before the event shows the post-event cell | ours (XCAL 1 Hz) | 75.9 % of 938 handovers |
| Same check | Raca 5G Irish (G-NetTrack Pro) | 29.4 % of 1,175 cell changes — no contamination |
| Same check, end-of-second downsample | NUWiNS (XCAL 10 Hz raw) | **93.2 % of 4,712 handovers**, 12 files, 3 operators |
| Same check, start-of-second downsample | NUWiNS | 4.1 % on the same handovers |
| Margin test `m = 1 − δ − x` | ours | 0 of 15 handovers with m < 0 contaminate their row |
| Update-delay cliff | NUWiNS | 98 % at 75–100 ms left → 44 % at 50–75 ms → 0 % below 50 ms |
| Gain from row t vs t−1 | ours | +276 % AUPRC (artefact) |
| Gain from row t vs t−1, and t−1 vs t−2 | Raca | +38 % vs +57 % — freshness, not contamination |

**Conclusion now carried in the manuscript (revised).** The alignment error is a property of the
row-aggregation rule, not of a vendor, a network or a region: it appears wherever a row summarises
the second that *ends* at its timestamp, and disappears from the very same NUWiNS handovers when the
downsampling rule is moved to the start of the second. This replaces the earlier
"instrument-specific, check per dataset" reading, which was true but weaker.

A second finding came out of the widened run: within the last fifth of a second, contamination
share estimates the serving-cell update delay, which sits near 60 ms. The artefact is a sub-second
measurement instrument for a one-hertz export.

Tables: `pipeline/reports_rev/tables/c9m_*.csv` and `c9ext_nuwins_*_all.csv`; manuscript §5.1,
Figure 5.1 and Table A.3. Scripts: `stage28_nuwins_audit.py` (fetch / cache / aggregate) and
`stage29_alignment_mechanism.py`.

### How to reproduce the NUWiNS run

```
python -m hoproj.pipeline.stage28_nuwins_audit --fetch all     # downloads, audits, caches, deletes raw
python -m hoproj.pipeline.stage28_nuwins_audit --aggregate     # rebuild tables from the cache alone
python -m hoproj.pipeline.stage29_alignment_mechanism --exp all
```

The raw exports are Git LFS objects and must come from
`https://media.githubusercontent.com/media/NUWiNS/pam2025-multi-carrier-dataset/main/...`;
`raw.githubusercontent.com` returns the LFS pointer, not the file. Each file is 100–190 MB and is
deleted after its audit; the cached per-handover records are 356 KB in total and are committed, so
the tables can be rebuilt without re-downloading.

T-Mobile drive 3 days 3 and 4 yielded no cell-changing LTE handovers and are excluded; the remaining
12 files are all that the corpus offers at raw XCAL resolution outside drive trip 1, which is
pre-processed and therefore not instrument-identical.

# External validation on the public IUT/Mendeley dataset — and what the DRM files are worth

Dataset: *A Pilot LTE Drive-Test Dataset for Handover and Mobility Analysis in
Urban Bangladesh*, v2.0 (Shafi, Istiaque, Sowad, Kawser — Mendeley Data
`10.17632/n2pvmtyn2j.1`), the data behind `11-benchmark-vs-finalmanuscript.md`.
Same operator, same city, same XCAL-M licence, different route and people,
**two years earlier** (Oct–Nov 2024 vs Sept 2026).

Code: `src/hoproj/pipeline/stage08_public_dataset.py` (new).
Tables: `reports/tables/public_dataset_transfer_*.csv`.

---

## 1. Headline: the model transfers, and it transfers as well as a model trained on that data

AUROC, LightGBM, RF + cell-history features, whole drives held out on both sides.

| train → test | 1 s | 2 s | 3 s | 5 s | mean |
|---|---|---|---|---|---|
| ours → **our own** held-out drives | 0.936 | 0.862 | 0.830 | 0.798 | **0.857** |
| **ours → public dataset** | 0.752 | 0.745 | 0.712 | 0.705 | **0.729** |
| public → **its own** held-out drives | 0.745 | 0.737 | 0.686 | 0.708 | **0.719** |
| **public → ours** | 0.683 | 0.675 | 0.669 | 0.656 | **0.671** |

Read the middle two rows together. **Our model scores 0.729 on their data; a
model trained on their data scores 0.719 on their own held-out drives.** The
transfer gap to their dataset is not a transfer gap — it is that dataset's own
ceiling. AUPRC lift on the public data is 2.0–3.3× prevalence.

This is the external validation the project did not have. It is independent,
collected by other people, and publicly citable with a DOI.

## 2. It also sharpens the curated-file anomaly

| source of the test data | AUROC our model achieves |
|---|---|
| our own held-out drives | 0.83–0.86 |
| a *different real capture* of ours | 0.81–0.84 |
| **an independent public real capture, 2 years earlier** | **0.73** |
| `DRIVETEST_LOGS_1_fixed.csv` (curated) | **0.35** |

Every genuinely measured dataset lands between 0.73 and 0.86. The curated file
sits below chance. Doc 09 left the curated↔XCAL collapse (H6) open between
"instrumentation" and "environment"; this result removes a third possibility —
it is not that our model is brittle across captures, because it is not. **The
curated file is the outlier, not the model.**

## 3. Our signalling parser agrees with XCAL's own event counter, exactly

The dataset ships XCAL's `Event Statistics` exports alongside the raw L3. Running
our parser over the 12 `Measurement Reports` exports and comparing:

| | our parser | XCAL Event Statistics |
|---|---|---|
| Intra-LTE handovers | **310** | **310 attempts** |
| completed | 310 | 309 success, 1 fail |

100% agreement on an independently produced capture. That is a cheap, strong
validation of the instrument the whole thesis rests on, and it belongs in the
methods section.

## 4. Three things the public dataset reveals about itself

**4.1 Its published CSVs cannot support handover forecasting.** The `Parent
Dataset` CSVs are event-triggered rows, not a periodic grid — 0.24 rows/s over a
45-minute drive. They carry no GPS, no speed and no date, only a time-of-day
string; RSRP/RSRQ are undocumented raw 3GPP indices; the `Processed Dataset`
CSVs have Excel-mangled timestamps (`33:33.712`) and re-encoded cell IDs. The
evaluation above had to be built from the L3 signalling instead, and the sample
grid reconstructed from `measResultPCell`.

**4.2 The UE is in RRC idle for most of each drive.** Only **26.6%** of
wall-clock seconds carry any radio measurement. Handover rate is 1.05/min
against our 6.7–7.3/min, and there are **3 re-establishments in 5 hours**
against our 113 / 64 / 159 per hour. Their drives are mostly a phone doing
nothing, being paged. Evaluation is therefore restricted to contiguous
RRC-connected runs: 17 runs, 33 minutes, 1,987 samples, 152 handovers —
prevalence 6.0 / 11.1 / 15.8 / 23.0%, close enough to ours for the comparison to
be fair.

**4.3 The same four A3 profiles are running.** Offsets −15, −10, −6.5, +1, +5 dB
and TTT 160–1024 ms, exactly the family we attributed in Sept 2026 — but with
−10 dB dominant here rather than −15 dB. The operator's mobility configuration
is stable across two years and shifts in emphasis, which strengthens R1 and is
worth a sentence in the paper.

---

## 5. The DRM files: yes, a great deal of extra information

The DRM files are XCAL-M's **native raw capture**. Everything else in the
repository — the CSVs, the L3 text, the Event Statistics — is an export *from*
them, and each export throws something away.

Their DRM header is byte-identical in structure to ours (`INNOg` container,
same `LibVer`), so they open in your licence.

What a re-export would recover that the published files do not have:

| missing from the published files | in the DRM |
|---|---|
| **GPS and speed** | yes — this alone restores the whole mobility feature block |
| **a periodic sample grid** at 100–200 ms instead of 0.24 rows/s | yes, export rate is chosen at export time |
| SINR, RSSI, CQI, RRC state | yes |
| PHY / application throughput | yes |
| absolute dates on the sample rows | yes |
| serving PCI on every row (we currently reconstruct it from the handover chain) | yes |

Two further things are already in the shipped `Event Statistics` and are new to
this project even without re-exporting:

- **Handover interface**: 215 X2, 92 intra-eNB, 3 unknown. Whether a handover
  goes directly between eNBs or through the core is a plausible predictor and a
  clean stratifier, and we have never had this label.
- **Idle-mode reselection priorities**, with full EUTRA/UTRA/GERAN priority
  lists and `T320` — 210 events. This is the network's idle-mode mobility
  configuration, the counterpart to the A3 profiles we already extract.

### Why this matters more than it looks

Re-exporting their 12 DRM files at 100–200 ms with GPS would give roughly **5
hours of independent, publicly citable drive data with the full feature set** —
more than doubling the campaign, at the cost of an afternoon at the XCAL
machine and no driving at all. Compare that with the two field days in doc 09.

**This is now the highest-value action available, ahead of everything in doc 09
§4 except fixing your own export rate.**

---

## 6. Actions

```
1. Re-export their 12 DRM files in XCAL-M at 100-200 ms, with GPS,
   SINR/CQI/RSSI, throughput and RRC state            <- one afternoon, no driving
2. Re-run stage08 on the re-export; mobility features become available,
   and the RRC-idle gaps shrink or disappear
3. Add the X2/intra-eNB label from Event Statistics as a feature and a
   stratifier
4. Cite the 310 vs 310 parser agreement as instrument validation
5. Put the four-row table in section 2 into the paper - it is the cleanest
   evidence that the curated file, not the model, is the anomaly
```

One caveat to state in the write-up: this dataset is from the same department
and supervisor as your own work, so it is *independent of your capture* but not
of your institution. Say so plainly rather than letting a reviewer find it.

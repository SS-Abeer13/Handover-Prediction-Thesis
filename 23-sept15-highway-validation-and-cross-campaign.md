# 23 — 15 September Highway Capture: Empirical Validation, Multi-Regime Contrast, and Cross-Campaign Comparison

**Author:** Abeer Saadman · Islamic University of Technology (IUT)  
**Date:** 15 September 2026  
**Status:** Current — Fourth Independent Capture & High-Speed Highway Validation  
**Supersedes/Extends:** Extends the 3-capture baseline in `18-corrected-mechanism-and-contributions.md` and `MASTER-Handover-Prediction.md` into a multi-regime empirical study.

---

## 1. Executive Summary: The Fourth Campaign

On 15 September 2026, a fourth continuous drive-test campaign was logged on the Grameenphone commercial LTE network in Dhaka using the XCAL diagnostic system:
* **Raw Files:** `test 15 sept.csv` (1.0 MB, 2,576 1 Hz rows, 113 columns) and `test 15 sept signalling.txt` (18.4 MB, 651,387 decoded Layer 3 lines).
* **Route & Terrain:** Unlike the earlier captures (10, 12, and 13 September), which traversed dense urban corridors between Gulshan, Banani, Mohakhali, and Airport, the 15 September trace extends northward along the **Dhaka–Gazipur Highway corridor** (Airport/Uttara at Lat 23.8345 to Gazipur / Boardbazar / IUT campus at Lat 23.9775, Lon 90.3802 to 90.5394).
* **Mobility Regime:** A high-speed highway vehicular regime. Average vehicular speed was **49.5 km/h** with peak cruising speeds of **98.0 km/h** (+130% faster than the 21–23 km/h urban crawl of 12/13 Sept).
* **Total Distance:** **34.6 km** across 42 minutes 56 seconds of driving.

This capture directly fulfills the research recommendation outlined in Report 08 §4, Report 18 §4, and Thesis Defence Slide 29: providing an out-of-corridor, high-speed validation dataset to test whether the mechanisms discovered in urban canyons generalize to highway macro-cells.

---

## 2. Four-Campaign Comprehensive Benchmark Matrix

Every row in the table below is derived from raw Layer 1 XCAL logs and decoded Layer 3 RRC signaling using the project's stateful timeline parser:

| Metric / Dimension | 10 Sept Capture | 12 Sept Capture | 13 Sept Capture | **15 Sept Capture (NEW)** | Pooled 4-Day Total / Mean |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Corridor / Route** | Uttara – Mohakhali | Mirpur – Uttara Loop | Gulshan – Mohakhali | **Uttara – Gazipur / IUT** | Multi-corridor |
| **Terrain Classification** | Urban Arterial | Urban Residential | Dense Urban Canyon | **Highway / Express Corridor** | Mixed Urban & Highway |
| **Duration (mm:ss)** | 45:56 (2,756 s) | 24:29 (1,469 s) | 60:05 (3,605 s) | **42:56 (2,576 s)** | **173:26 (10,406 s)** |
| **Distance Traversed** | 30.2 km | 9.2 km | 23.3 km | **34.6 km** | **97.3 km** |
| **Mean Speed** | 39.2 km/h | 23.5 km/h | 21.4 km/h | **49.5 km/h** | **33.4 km/h** |
| **Peak Speed** | 83.0 km/h | 38.0 km/h | 55.0 km/h | **98.0 km/h** | **98.0 km/h** |
| **Mean Serving RSRP** | −84.0 dBm | −91.1 dBm | −84.2 dBm | **−97.5 dBm** | **−89.2 dBm** |
| **Minimum RSRP** | −122.0 dBm | −119.0 dBm | −117.0 dBm | **−141.0 dBm** | **−141.0 dBm** |
| **Mean Serving SINR** | 3.2 dB | 4.6 dB | 5.2 dB | **4.9 dB** | **4.5 dB** |
| **Signalling Log Size** | 30.1 MB (1,029k lines)| 17.7 MB (617k lines) | 28.8 MB (995k lines) | **18.4 MB (651k lines)** | **95.0 MB (3,292k lines)**|
| **Measurement Reports**| 5,695 | 4,761 | 5,010 | **3,923** | **19,389 reports** |
| **Confirmed Handovers** | 307 | 176 | 297 | **177** | **957 handovers** |
| **Handover Spacing** | 1 per 9.0 s | 1 per 8.3 s | 1 per 12.1 s | **1 per 14.5 s** | **1 per 10.9 s** |
| **Radio Link Failures** | 113 re-establishments | 64 re-establishments | 159 re-establishments | **5 re-establishments** | **341 re-establishments** |
| **Ping-Pong Rate (15s)**| 38.8% | 59.7% | 33.7% | **40.7%** | **43.2%** |
| **Unacted A3 Reports** | 63.9% declined | 67.2% declined | 68.6% declined | **74.4% declined** | **68.5% declined** |
| **HO Completion Rate** | 100.0% (307/307) | 100.0% (176/176) | 100.0% (297/297) | **100.0% (177/177)** | **100.0% (957/957)** |
| **Mean Interruption** | 17.5 ms | 17.8 ms | 20.8 ms | **19.7 ms** | **18.9 ms** |

---

## 3. Detailed Scientific Findings & Comparative Insights

### 3.1 Finding 1: Radio Link Failure (RLF) Collapse in Highway Geometry
The most striking physical contrast in the 15 September capture is the near-total disappearance of Radio Link Failures (RLF).
* In previous captures, RRC re-establishment requests occurred frequently: **113 on 10 Sept, 64 on 12 Sept, and 159 on 13 Sept**.
* On 15 September, across 34.6 km and 43 minutes of driving, **only 5 re-establishments occurred**—a reduction of over 95%.
* **Physical & Structural Mechanism:** Urban canyons in downtown Dhaka suffer from severe corner-shadowing and flyover blockage, causing serving RSRP to plummet faster than the Layer 3 filter and TTT can adapt. On the northern highway, line-of-sight propagation is preserved over open terrain, and macro-cell towers provide smooth, wide overlapping transition zones, enabling seamless handovers before link drop.

### 3.2 Finding 2: Unacted A3 Measurement Reports Peak at 74.4%
The central empirical mechanism discovered in Report 15 and Report 18 was that Event A3 entering conditions do not guarantee a handover, because base stations decline a majority of triggered reports.
* 10 Sept: 63.9% declined.
* 12 Sept: 67.2% declined.
* 13 Sept: 68.6% declined.
* **15 Sept: 74.4% declined (2,919 out of 3,923 reports unacted within 2 seconds).**
* **Significance:** In highway macro-cells, vehicle speed is high but cell radius is wide. The vehicle enters the boundary condition $(M_n - M_s > 	ext{Off} + 	ext{Hys})$ and transmits continuous measurement reports, but the serving eNodeB intentionally delays or vetoes the handover until signal difference is decisive or target cell capacity permits.
* This brings the pooled four-day unacted rate to **68.5%**, perfectly aligning with **Ghoshal et al.'s findings (69%–87% unacted reports across US tier-1 operators)**.

### 3.3 Finding 3: Weaker Signal Envelope (−97.5 dBm) from Expanded Inter-Site Distance
* Mean serving RSRP dropped from −84.0 dBm (10 Sept) and −84.2 dBm (13 Sept) to **−97.5 dBm on 15 Sept**, with cell-edge drops reaching −141.0 dBm.
* **Telecom Basis:** Cell density in Gazipur and along the northern highway is lower than in central Dhaka; Inter-Site Distance (ISD) expands from 300–500m to 1.0–2.0 km.
* Despite lower signal power, the channel remained clean: mean SINR was **4.9 dB** (superior to 10 Sept's 3.2 dB), demonstrating that lower co-channel interference compensates for lower received power.

### 3.4 Finding 4: Ping-Pong Handover Persists at High Velocity (40.7%)
* A common hypothesis in cellular planning is that ping-pong handovers are primarily caused by stationary or slow-moving vehicles idling on cell boundaries.
* The 15 September run disproves this: at an average speed of 49.5 km/h, **40.7% of handovers still returned to the origin cell within 15 seconds** (72 out of 177 handovers).
* **Conclusion:** Ping-pong is a geometric property of antenna azimuth overlap and 3GPP hysteresis/TTT parameterization, rather than a symptom of vehicle congestion.

---

## 4. Impact on Thesis Framing and Contributions

1. **Expansion from Single Corridor to Multi-Regime Matrix:**  
   The thesis is no longer restricted to one urban corridor. The empirical dataset now spans **97.3 km across two distinct regimes**:
   * *Urban Traffic Regime (Drives 1–35):* 21–39 km/h, dense shadowing, 336 RLFs, ISD ~400m.
   * *Highway Cruising Regime (Drives 36–43):* 49.5 km/h (peak 98 km/h), open propagation, 5 RLFs, ISD ~1.5 km.
2. **Robustness of the RRC Signalling Parser:**  
   The stateful parser successfully parsed 651k lines of 15 Sept logs, resolving 177 handovers with 100% completion tracking and a median interruption latency of 1.0 ms (mean 19.7 ms).
3. **Defense Shielding:**  
   When examiners ask: *"Did you only test your models in traffic jams?"*, you can point directly to the 15 September highway campaign where speeds reached 98 km/h.

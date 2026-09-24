# The papers arrived, and one of them broke my own pipeline

All four are now accounted for. Three were read in full; the fourth turned out
to be a paper we already have.

**A defect in our A3 attribution surfaced while checking our method against
Ghoshal et al.'s. It is fixed, and it invalidates several published-in-our-docs
numbers. Section 3 is the important part of this document.**

---

## 1. The four papers

| # | Paper | Status |
|---|---|---|
| 1 | **Deng, Peng, Fida, Meng, Hu**, "Mobility Support in Cellular Networks: A Measurement Study on Its Configurations and Implications", **IMC '18, pp. 147–160**, DOI 10.1145/3278532.3278546 | read |
| 2 | **Ghoshal, Khan, Dinh, Kong, Basit, Wang, Feng, Hu, Koutsonikolas**, "Handover Configurations in Operational 5G Networks", **arXiv:2511.03116v2**, Nov 2025 — **arXiv only, under review**, no DOI | read |
| 3 | **Zidic, Mastelić, Nižetić Kosović, Čagalj, Lorincz**, "Analyses of ping-pong handovers in real 4G telecommunication networks", ***Computer Networks* 227:109699, 2023**, DOI 10.1016/j.comnet.2023.109699 | read |
| 4 | "Handover Optimization in LTE Networks Using Contextual Bandit RL and Real-World Data" | **It is `FinalManuscript.pdf`** — the same-department IUT manuscript already analysed in doc 11. Its circular evaluation is confirmed: it replays a self-designed reward, with no off-policy estimator. |

---

## 2. A defect in our pipeline, found by reading their methods

Ghoshal et al. warn that assuming "the last measurement report triggered the
handover" misattributes ~12% of handovers. Checking ours against that turned up
a **different and larger error of our own**.

`reportConfigId` and `measId` are **indices into the UE's current measurement
configuration, not global identifiers.** The network rewrites that
configuration constantly — we observe **1,057 measConfig updates in one 60-minute
capture**. In that capture:

- **29 of 30 reportConfigIds denote a different event type** (A1/A2/A3/A4/A5/A6)
  at different points in the log. reportConfigId 1 is eventA1 in one message and
  eventA3, A4, A5 and A6 in others.
- **All 32 measIds** point at many different reportConfigIds over time.

Our parser flattened the whole file into one dictionary, so later definitions
silently overwrote earlier ones. The symptom that gave it away: the raw log
contains 1,424 A1, 1,401 A2, 1,309 A3, 195 A5 and 506 A6 configurations, yet our
parser kept 28 configs of which **100% were A3**, and resolved **99.4% of all
measurement reports to an A3 rule** — impossible, when 43% of reports carry no
neighbour at all (the A1/A2 signature).

**Fixed.** `config_regime.py` now maintains a **configuration timeline**: every
measConfig occurrence updates a running state (3GPP measConfig is incremental —
AddMod inserts or replaces), and each report is resolved against the state in
force at its own timestamp. Tests pass.

After the fix the event mix is what it should be: **44.5% A3, 27.7% A1, 5.3% A5,
3.4% A4, 2.0% A2**, and attribution of handovers to an A3 profile is **97.4% of
780** rather than a suspicious 100%.

Our own exposure to Ghoshal's 12% warning, separately checked: **0%**. The last
measurement report before a handover resolves to an A3 rule in every case, so
the last-report assumption costs us nothing.

---

## 3. What this changes — corrections to docs 09, 14 and 15

### 3.1 The regime distribution was wrong, and it inverts a mechanism claim

| A3 offset | hysteresis | TTT | handovers | share |
|---|---|---|---|---|
| **+1.0 dB** | 1.0 dB | 320 ms | **564** | **74.2%** |
| −10.0 dB | 2.0 dB | 640 ms | 100 | 13.2% |
| −15.0 dB | 1.0 dB | 160 ms | 62 | 8.2% |
| +2.0 dB | 1.0 dB | 320 ms | 13 | 1.7% |
| −15.0 dB | 1.0 dB | 320 ms | 9 | 1.2% |
| −6.5 dB | 2.0 dB | 640 ms | 9 | 1.2% |
| +2.0 dB | 1.0 dB | 640 ms | 3 | 0.4% |

Previously reported as a near-balanced split across three profiles. It is not:
**one profile carries three quarters of all handovers**, and the pattern is
stable across all three captures (66%, 77%, 76%).

**This inverts doc 15's headline mechanism finding.** That doc said the dominant
profile was −15 dB, firing whenever the gap is below +15 dB — 92.5% of samples —
and concluded the A3 gap condition is "almost always satisfied and carries
little information". The dominant profile is actually **+1 dB**, which fires at
gap < −1 dB, covering only **15.4%** of samples. The conclusion must be redone,
and it may reverse.

**Doc 15 section 2 and `fig_mechanism_a3.png` are withdrawn pending a rerun.**

### 3.2 The regime-transfer result REVERSES — H2 is back

Re-run on the corrected labels. The null was a label-noise artefact.

| | same regime | cross regime | gap |
|---|---|---|---|
| **before** (flat-map labels) | 0.828 | 0.814 | **+0.015** |
| **after** (timeline labels) | **0.833** | **0.745** | **+0.088** |

Per horizon, after: 0.955 → 0.889 (1 s), 0.830 → 0.720 (2 s), 0.791 → 0.702
(3 s), 0.756 → 0.670 (5 s). Consistently 0.07–0.11 at every horizon.

**So H2 is no longer falsified.** Cross-regime transfer does degrade, by about
six times the effect the mislabelled run measured. Doc 09's falsification of H2
and doc 14's R8 ("predictability is invariant to A3 control parameters") are
both **withdrawn**.

**H3 stays falsified.** Adding the measured A3 parameters as features still
gives nothing: 0.744 vs 0.745 cross-regime, 0.835 vs 0.833 same-regime.

Read the strength of this carefully before writing it up. The corrected
attribution concentrates 74% of handovers in one profile, so only **two**
regimes now clear the 60-handover bar, and the experiment reduces to **a single
regime pair in one direction**: train on +1 dB/320 ms versus train on
−10 dB/640 ms, both evaluated on the *identical* −10 dB test set (591 rows,
13 held-out drives, same prevalence). That is a clean paired contrast — only the
training regime differs — but it is one pair, not a matrix. State it as such.

The pattern claimed in doc 14 — *"more information does not help; better
formulation does"* — loses one of its four instances and should be softened.

### 3.3 The "negative offsets" contrast is weakened but survives

Negative offsets are real and outside the published range — Deng et al. report
a3-Offset ∈ [0, 5] dB for AT&T and **[−1, 15] dB for T-Mobile across 30 carriers
in 15 countries**, with −1 dB the most negative value anywhere; Ghoshal et al.
report no negative offset at all. But they are a **minority configuration here
(22% of handovers), not this network's norm.** Write it as: *this network
deploys a3-Offset values of −15 and −10 dB on a minority of carriers, outside
the [−1, 15] dB range reported across 30 operators.* Not "this network runs
negative offsets."

---

## 4. The novelty statement, now settled

Deng et al. recover numerical a3-Offset, hysteresis and time-to-trigger
device-side from broadcast RRC, across 30 carriers, 15 countries, 32,033 cells —
in 2018, using MobileInsight rather than XCAL. **Extraction is not novel and
claiming it would be fatal.**

But neither they nor Ghoshal et al. build any model. Deng et al. write:

> "given the observable configurations, it is feasible to predict handoffs at
> runtime at the mobile device… such predictions can be highly accurate"

and then never do it — no model, no features, no labels, no split, no metric.
They also explicitly scope themselves out of our territory: *"We look into
persistent and structural factors… instead of transient factors like
time-varying radio channel quality"*, and *"we examine why and how a handoff is
triggered… rather than which cell is eventually chosen."*

So the defensible framing is to cite that sentence as **the open problem we
close**, which is stronger than pretending it is not there:

> Deng et al. established that deployed handover configurations can be recovered
> device-side from RRC signalling and observed that runtime handover prediction
> would therefore be feasible, but built no predictive model and restricted their
> analysis to persistent structural factors rather than time-varying radio
> conditions. We take up that open problem: the recovered per-carrier A3
> parameters become the label-generating and feature-construction basis for a
> supervised, leakage-controlled handover-prediction pipeline.

## 5. Ping-pong: the comparison is now exact

| | this work | Ghoshal et al. | Zidic et al. |
|---|---|---|---|
| criterion | return to source PCI | return to source PCI — identical | return to source cell |
| **window** | **15 s** | **15 s** | **1 s** (3GPP TR 36.839 MTS — now verified) |
| denominator | **all handovers** | **one event type** (A3, or B1) | one eNB, 13 days |
| rate | **29.4%** pooled | A3: 15–16% AT&T/T-Mobile, **25%** Verizon | 2.6% urban, 3.1% suburban, 9.4% rural |

**Zidic is not a yardstick for our number** — a 1 s dwell threshold against our
15 s measures a different thing, and juxtaposing them reads as a 10× error. Cite
Zidic for its conceptual contributions instead: raw ping-pong rate is diluted by
"unavoidable" handovers, ping-pongs concentrate where cell dominance is
contested, and rural rates exceed urban ones.

**Ghoshal is the right yardstick and our rate is above all of theirs.** Their
denominator is per-event and A3 is their highest-rate event, so a pooled Ghoshal
figure would sit *below* their 25%. Ours is pooled and higher.

The safe sentence:

> Under the same return-to-source-PCI criterion and the same 15 s window as
> Ghoshal et al., our pooled ping-pong rate of 29.4% of all handovers exceeds
> the highest per-event rate they report for any US operator (25% of
> A3-triggered handovers, for the operator running the shortest
> time-to-trigger).

Two precision guards: their 4–10 dB figures are the **sum** of offset and
hysteresis and are **5G→5G only** (they never publish LTE A3 values, only that
each operator uses 9–17 distinct ones); and never quote their loose §VIII phrase
"up to 25% of the total HOs" as an all-handover rate.

---

## 6. Next, in order

```
1. Re-run stage07 regime transfer on corrected labels        <- top priority
2. Re-run the mechanism figure and the A3 trigger-coverage
   analysis; withdraw or revise doc 15 section 2
3. Re-run stage09 (hazard) - regime is not a feature there, so
   only the reported regime counts change, but verify
4. Check Kalntis et al., "Smooth Handovers via Smoothed Online
   Learning", INFOCOM 2025 - the closest learning paper in
   Ghoshal's bibliography, before any first-to-learn claim
5. Draft the manuscript
```

One methodological note worth keeping for the paper: this defect was invisible
to every check we had — the pipeline reported *100% attribution*, which looked
like success. It was caught only by comparing our extraction method against a
published one. That is an argument for the protocol audit in doc 16 being a
contribution rather than a formality.

"""Stage 20 - the departmental manuscript's method, reimplemented and run under
our protocol (doc 19, item L).

Shafi, Istiaque, Sowad and Kawser, *Handover Optimization in LTE Networks Using
Contextual Bandit Reinforcement Learning and Real-World Data* (IUT EEE), is the
closest comparator this project has: same operator, same city, same tool, same
department. It is reimplemented here exactly as specified in their Section III,
then evaluated twice - once under their own train/test design and once under
ours - so the paper can state a like-for-like number instead of an argument.

Their method, as published
--------------------------
state    s = [serving RSRP, serving RSRQ, neighbour RSRP, neighbour RSRQ,
              serving CINR], StandardScaler fitted on the training set
action   a in {0 = stay, 1 = hand over}
reward   Algorithm 1: a HOM gate (neighbour RSRP >= serving RSRP + 3 dB) and a
         TTT persistence check (the gate must hold for TTT seconds), then a
         piecewise constant reward in {-20, -8, -5, -4, +1, +3, +5}
agent    tabular Q-learning, alpha 0.1, gamma 0.9, epsilon 1 -> 0.01 at decay
         0.995, 10,000 episodes, Q initialised to zero
test     1-nearest-neighbour lookup of the test state into the Q-table keys,
         argmax over that state's two Q-values, plus an external TTT filter

What had to be decided here, and why
------------------------------------
*Scoring.* Their output is an action, ours is a probability. To place both on
one axis the agent's **advantage** ``Q(s,1) - Q(s,0)`` at the matched key is used
as the ranking score. This is the most generous reading available: it uses the
full learned signal rather than the thresholded action.

*Rows.* Their dataset is event-triggered, so every row carries a neighbour
measurement. On our 1 Hz grid only 59% of samples do. Every model in this stage
is therefore trained and scored on **neighbour-present rows only** - the subset
most favourable to their method - and our LightGBM is restricted to exactly the
same rows so the comparison is paired.

*The TTT filter looks forward.* Their evaluation accepts an action only if the
HOM condition persists for TTT seconds *after* the decision instant. For a
handover *decision* that is legitimate - the network does wait. For a *forecast*
it consumes TTT seconds of the future, so a "prediction" at t is really made at
t + TTT. Both variants are reported and labelled; the unfiltered one is the
honest comparator for a forecasting task.
"""
from __future__ import annotations

import argparse
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

from ..config import Config, deep_merge, load_config, resolve_paths
from ..data import ingest, qc, segment
from ..data import labels as L
from ..data.features import build_features, select_blocks
from ..data.signalling import parse_signalling
from ..data.transforms import TabularTransform
from ..eval import metrics as MET
from ..eval import report as RPT
from ..models.registry import build_model
from ..utils import get_logger, set_seed, timed, write_json

LOG = get_logger("hoproj.stage20")

# ---- their published constants (Section III-C, Table I)
HOM_MARGIN_DB = 3.0
TTT_SECONDS = (1.0, 0.7)
ALPHA, GAMMA = 0.1, 0.9
EPS0, EPS_MIN, EPS_DECAY = 1.0, 0.01, 0.995
EPISODES = 10_000

STATE_COLS = ["serving_rsrp", "serving_rsrq", "nbr1_rsrp", "nbr1_rsrq", "serving_sinr"]
BLOCKS = ["rf", "mobility", "history"]
CAPTURES = [
    ("10Sept", "sept10/data/raw", "test 10 sept-M1.csv", "test_10_sept_signalling.txt"),
    ("12Sept", "sept12/data/raw", "test 12 sept.csv", "test 12 sept signalling.txt"),
    ("13Sept", "sept13/data/raw", "test 13 sept.csv", "test 13 sept signalling.txt"),
]


# --------------------------------------------------------------------- dataset
def build_capture(tag: str, raw: str, csv: str, sig: str, horizons: list[float]):
    """Sample grid + labels + our feature matrix, with the five state columns kept."""
    ov = {"data": {"sources": {"samples": csv, "signalling": sig}},
          "features": {"blocks": BLOCKS, "regime": "topology_agnostic"},
          "segmentation": {"method": "fixed_duration", "fixed_duration_s": 180,
                           "route_from": "config"},
          "qc": {"min_drive_duration_s": 60, "min_drive_samples": 60},
          "labels": {"horizons_s": list(horizons), "allow_subperiod_horizons": True}}
    cfg = Config(deep_merge(load_config("base.yaml", adapter="xcal_signalling"), ov))
    rawp = Path(raw)
    samples, events = ingest.ingest(cfg, rawp)
    samples = segment.assign_routes(samples, events, cfg)
    samples = segment.segment_drives(samples, cfg)
    samples["drive_id"] = tag + "__" + samples["drive_id"].astype(str)
    drives = segment.drive_table(samples)
    samples = qc.apply_qc(samples, qc.drive_quality(samples, drives, cfg))
    ho = L.handover_events(samples, events, cfg)
    ho = ho[ho["drive_id"].isin(set(samples["drive_id"]))].reset_index(drop=True)
    lab = L.build_labels(samples, ho, cfg)
    feats = build_features(samples, lab, cfg)
    lab = (feats[["drive_id", "t"]].merge(lab, on=["drive_id", "t"], how="left")
           .reset_index(drop=True))
    src = samples.set_index(["drive_id", "t"])
    idx = pd.MultiIndex.from_frame(feats[["drive_id", "t"]])
    state = pd.DataFrame({c: (src.reindex(idx)[c].to_numpy() if c in src.columns else np.nan)
                          for c in STATE_COLS})
    state["drive_id"] = feats["drive_id"].to_numpy()
    state["t"] = feats["t"].to_numpy()
    state["capture"] = tag
    feats["capture"] = tag
    LOG.info("%s: %d rows, %d drives, %d handovers, neighbour present on %.1f%%",
             tag, len(feats), feats["drive_id"].nunique(), len(ho),
             100 * state["nbr1_rsrp"].notna().mean())
    return feats, lab, state, cfg


# ------------------------------------------------------- their reward function
def rewards(state: pd.DataFrame, ttt_s: float,
            gate_mode: str = "grid") -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Algorithm 1, vectorised per drive. Returns (R_a0, R_a1, gate).

    ``gate`` is their ``ho_cond AND ttt_met``: the HOM condition holding
    continuously from this sample for TTT seconds.

    Two gate modes, because the TTT check does different work at different row
    spacings. Their dataset is event-triggered at ~0.24 rows/s, so the next row
    is usually further ahead than TTT and their loop breaks before testing
    anything - the persistence check is close to vacuous on their own data. On
    our 1 Hz grid the same code tests every intervening second and is stringent.

    ``grid``      the check as written, walked over our 1 Hz samples
    ``hom_only``  the HOM condition alone, which is what their row spacing
                  effectively evaluates - the arm that is fairest to them
    """
    s_rsrp = state["serving_rsrp"].to_numpy(float)
    s_rsrq = state["serving_rsrq"].to_numpy(float)
    n_rsrp = state["nbr1_rsrp"].to_numpy(float)
    n_rsrq = state["nbr1_rsrq"].to_numpy(float)
    cinr = state["serving_sinr"].to_numpy(float)
    ho_cond = n_rsrp >= s_rsrp + HOM_MARGIN_DB

    if gate_mode == "hom_only":
        gate = ho_cond.copy()
    else:
        gate = _ttt_gate(state, ho_cond, ttt_s)

    r1 = np.where(gate,
                  np.where((n_rsrq > s_rsrq) & (cinr > 20), 3.0,
                           np.where((n_rsrp > s_rsrp) & (n_rsrq > s_rsrq), 1.0, -8.0)),
                  -20.0)
    r0 = np.where(gate, -5.0,
                  np.where((cinr > 25) & (s_rsrp > -85), 5.0,
                           np.where((cinr <= 5) | (s_rsrp < -110), -4.0, 3.0)))
    return r0, r1, gate


def _ttt_gate(state: pd.DataFrame, ho_cond: np.ndarray, ttt_s: float) -> np.ndarray:
    """TTT persistence, walked forward inside each drive exactly as Algorithm 1."""
    gate = np.zeros(len(state), dtype=bool)
    t = state["t"].to_numpy()
    for d in state["drive_id"].unique():
        sel = np.where(state["drive_id"].to_numpy() == d)[0]
        cond = ho_cond[sel]
        times = pd.to_datetime(t[sel]).astype("int64") / 1e9
        for k in range(len(sel)):
            if not cond[k]:
                continue
            ok, j = True, k
            while j + 1 < len(sel) and (times[j + 1] - times[k]) <= ttt_s:
                if not cond[j + 1]:
                    ok = False
                    break
                j += 1
            gate[sel[k]] = ok
    return gate


# --------------------------------------------------------------- their Q-agent
def train_q(Z: np.ndarray, r0: np.ndarray, r1: np.ndarray, seed: int,
            episodes: int = EPISODES) -> np.ndarray:
    """Tabular Q-learning over continuous keys: one table row per training state."""
    rng = np.random.default_rng(seed)
    Q = np.zeros((len(Z), 2), dtype=np.float64)
    R = np.column_stack([r0, r1])
    eps = EPS0
    for _ in range(episodes):
        i = int(rng.integers(len(Z)))
        a = int(rng.integers(2)) if rng.random() < eps else int(np.argmax(Q[i]))
        nxt = min(i + 1, len(Z) - 1)          # their max_a' Q(s',a') bootstrap
        target = R[i, a] + GAMMA * float(np.max(Q[nxt]))
        Q[i, a] += ALPHA * (target - Q[i, a])
        eps = max(EPS_MIN, eps * EPS_DECAY)
    return Q


def q_lookup(Z_train: np.ndarray, Q: np.ndarray, Z_test: np.ndarray) -> np.ndarray:
    from sklearn.neighbors import NearestNeighbors
    nn = NearestNeighbors(n_neighbors=1).fit(Z_train)
    _, idx = nn.kneighbors(Z_test)
    return Q[idx[:, 0]]


# --------------------------------------------------------------------- scoring
def _standardise(train: np.ndarray, other: list[np.ndarray]):
    mu, sd = np.nanmean(train, 0), np.nanstd(train, 0)
    sd[~np.isfinite(sd) | (sd < 1e-9)] = 1.0
    f = lambda A: np.nan_to_num((A - mu) / sd)
    return f(train), [f(A) for A in other]


def score_arms(train_state, test_state, train_feats, test_feats, train_lab, test_lab,
               cfg, horizons, tags, seed, ttt_s, gate_mode="grid"):
    """Run every arm on one (train, test) pair. Returns a list of metric tables."""
    Ytr = np.column_stack([train_lab[f"y_ho_{t}"].to_numpy(np.float32) for t in tags])
    Mtr = np.column_stack([train_lab[f"m_ho_{t}"].to_numpy(np.float32) for t in tags])
    Yte = np.column_stack([test_lab[f"y_ho_{t}"].to_numpy(np.float32) for t in tags])
    Mte = np.column_stack([test_lab[f"m_ho_{t}"].to_numpy(np.float32) for t in tags])

    Ztr_raw = train_state[STATE_COLS].to_numpy(float)
    Zte_raw = test_state[STATE_COLS].to_numpy(float)
    Ztr, (Zte,) = _standardise(Ztr_raw, [Zte_raw])

    r0, r1, gate_tr = rewards(train_state, ttt_s, gate_mode)
    r0_te, r1_te, gate_te = rewards(test_state, ttt_s, gate_mode)
    set_seed(seed)
    Q = train_q(Ztr, r0, r1, seed)
    Qte = q_lookup(Ztr, Q, Zte)
    adv = Qte[:, 1] - Qte[:, 0]
    # map the advantage onto [0,1] so the same metric code applies; monotone, so
    # every ranking metric is unaffected
    lo, hi = np.nanmin(adv), np.nanmax(adv)
    p_q = (adv - lo) / (hi - lo) if hi > lo else np.zeros_like(adv)

    out = []

    def add(name, P, note=""):
        tbl = MET.multi_horizon_table(Yte, np.column_stack([P] * len(horizons)),
                                      Mte, horizons, (0.01, 0.05, 0.10))
        tbl.insert(0, "model", name)
        tbl["note"] = note
        out.append(tbl)

    add("departmental_q", p_q, "Q(s,1)-Q(s,0), 1-NN lookup, no TTT filter")
    add("departmental_q_ttt", np.where(gate_te, p_q, 0.0),
        f"their evaluation: TTT filter over the following {ttt_s}s (uses future samples)")
    add("departmental_gate", gate_te.astype(float),
        f"their gate alone ({gate_mode}): neighbour >= serving + {HOM_MARGIN_DB} dB")

    # The reward is a closed-form function of the same five features, so a direct
    # ranking by (r1 - r0) needs no RL at all. If it matches the agent, the
    # Q-learning machinery is doing no work the reward function was not.
    d = r1_te - r0_te
    lo2, hi2 = np.nanmin(d), np.nanmax(d)
    add("reward_only_control", (d - lo2) / (hi2 - lo2) if hi2 > lo2 else np.zeros_like(d),
        "rank by r(s,1) - r(s,0) directly; no Q-learning")

    # our model, same rows, same labels
    names = [n for n in select_blocks(train_feats, BLOCKS) if n in train_feats.columns
             and n in test_feats.columns]
    tf = TabularTransform(cfg.get_path("features.scaler", "robust"),
                          clip_sigma=float(cfg.get_path("features.clip_sigma", 8.0)))
    tf.fit(train_feats[names])
    Xtr = np.asarray(tf.transform(train_feats[names]))
    Xte = np.asarray(tf.transform(test_feats[names]))
    set_seed(seed)
    mdl = build_model("lgbm", cfg, Xtr.shape[1], len(horizons), seed=seed,
                      params={"n_jobs": 1})
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        mdl.fit(Xtr, Ytr, masks=Mtr)
    P = mdl.predict_proba(Xte)
    tbl = MET.multi_horizon_table(Yte, P, Mte, horizons, (0.01, 0.05, 0.10))
    tbl.insert(0, "model", "ours_lgbm")
    tbl["note"] = "same rows, same labels, 107 features"
    out.append(tbl)

    # five-feature control: our learner on THEIR state vector only
    set_seed(seed)
    mdl5 = build_model("lgbm", cfg, 5, len(horizons), seed=seed, params={"n_jobs": 1})
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        mdl5.fit(np.nan_to_num(Ztr), Ytr, masks=Mtr)
    tbl = MET.multi_horizon_table(Yte, mdl5.predict_proba(np.nan_to_num(Zte)), Mte,
                                  horizons, (0.01, 0.05, 0.10))
    tbl.insert(0, "model", "ours_lgbm_5feat")
    tbl["note"] = "our learner on their 5-D state, to separate method from features"
    out.append(tbl)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="Stage 20: departmental baseline")
    ap.add_argument("--root", default=None)
    ap.add_argument("--seed", type=int, default=1337)
    ap.add_argument("--ttt", type=float, default=1.0, choices=list(TTT_SECONDS))
    ap.add_argument("--folds", type=int, default=5)
    ap.add_argument("--tag", default="departmental_baseline")
    a = ap.parse_args(argv)

    horizons = [0.5, 1.0, 2.0, 3.0, 5.0]
    built = {tag: build_capture(tag, raw, csv, sig, horizons)
             for tag, raw, csv, sig in CAPTURES}
    cfg = built["10Sept"][3]
    tags = L.horizon_tags(cfg)
    horizons = L.usable_horizons(cfg)

    F = pd.concat([built[t][0] for t in built], ignore_index=True)
    F.attrs = dict(built["10Sept"][0].attrs)
    Y = pd.concat([built[t][1] for t in built], ignore_index=True)
    S = pd.concat([built[t][2] for t in built], ignore_index=True)
    present = S["nbr1_rsrp"].notna().to_numpy()
    LOG.info("pooled %d rows; neighbour present on %d (%.1f%%)",
             len(S), present.sum(), 100 * present.mean())
    F, Y, S = F[present].reset_index(drop=True), Y[present].reset_index(drop=True), \
        S[present].reset_index(drop=True)

    rows = []
    for gate_mode in ("grid", "hom_only"):
        # ---- their design: Day 1 -> Day 2, and Day 3 -> Day 2
        for src, tgt in (("10Sept", "12Sept"), ("13Sept", "12Sept")):
            tr, te = (S["capture"] == src).to_numpy(), (S["capture"] == tgt).to_numpy()
            with timed(f"[{gate_mode}] their split {src}->{tgt}"):
                for tbl in score_arms(S[tr], S[te], F[tr], F[te], Y[tr], Y[te],
                                      cfg, horizons, tags, a.seed, a.ttt, gate_mode):
                    tbl.insert(1, "protocol", "theirs (capture -> capture)")
                    tbl.insert(2, "gate_mode", gate_mode)
                    tbl.insert(3, "split", f"{src}->{tgt}")
                    rows.append(tbl)

        # ---- our design: grouped rotation over drives, every drive tested once
        drives = np.array(sorted(S["drive_id"].unique()))
        rng = np.random.default_rng(a.seed)
        rng.shuffle(drives)
        assign = {d: i % a.folds for i, d in enumerate(drives)}
        for f in range(a.folds):
            te_d = {d for d, k in assign.items() if k == f}
            te = S["drive_id"].isin(te_d).to_numpy()
            tr = ~te
            with timed(f"[{gate_mode}] our split fold{f}"):
                for tbl in score_arms(S[tr], S[te], F[tr], F[te], Y[tr], Y[te],
                                      cfg, horizons, tags, a.seed, a.ttt, gate_mode):
                    tbl.insert(1, "protocol", "ours (grouped drive K-fold)")
                    tbl.insert(2, "gate_mode", gate_mode)
                    tbl.insert(3, "split", f"fold{f}")
                    rows.append(tbl)

    df = pd.concat(rows, ignore_index=True)
    paths = resolve_paths(Config(deep_merge(cfg, {
        "project": {"paths": {"reports": "reports_xcal", "artifacts": "artifacts_xcal",
                              "processed": "data/processed_xcal",
                              "interim": "data/interim_xcal"}}})), a.root)
    RPT.save_table(df, paths["reports"], a.tag)

    num = df.select_dtypes(include=[np.number]).columns
    summ = (df.groupby(["protocol", "gate_mode", "model", "horizon_s"], as_index=False)[list(num)]
            .mean().sort_values(["protocol", "gate_mode", "horizon_s", "auprc"],
                                ascending=[True, True, True, False]))
    RPT.save_table(summ, paths["reports"], f"{a.tag}_summary")
    write_json({"method": "Shafi et al., tabular Q-learning contextual bandit, "
                          "reimplemented from Section III and Algorithm 1",
                "hom_db": HOM_MARGIN_DB, "ttt_s": a.ttt, "episodes": EPISODES,
                "rows": "neighbour-present samples only", "seed": a.seed},
               paths["artifacts"] / f"{a.tag}.json")
    print(summ.query("horizon_s == 1.0")[
        ["protocol", "gate_mode", "model", "auprc", "auprc_lift", "auroc"]].to_string(index=False))
    LOG.info("stage 20 complete: %d rows", len(df))


if __name__ == "__main__":
    main()

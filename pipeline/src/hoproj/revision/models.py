"""Learners for the revision. Every learner sees the same feature matrix and
emits an (n, K) matrix of cumulative incidences F_k = P(T <= edge_k | x).

"Only the learner varies" (C17) is enforced here: the sequence models consume
windows of the very same lagged feature vectors the tabular models see,
including the history block.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .data import EDGES

K = len(EDGES)
LO = np.array([0.0] + EDGES[:-1])
HI = np.array(EDGES)


# ------------------------------------------------------------------ long format
def to_long(X: np.ndarray, t_next: np.ndarray):
    """(sample x at-risk bin). All rows have >= 5 s follow-up, so no censoring."""
    rows, bins, ys = [], [], []
    for k in range(K):
        at = t_next > LO[k]
        idx = np.flatnonzero(at)
        rows.append(idx)
        bins.append(np.full(idx.size, k))
        ys.append(((t_next[idx] > LO[k]) & (t_next[idx] <= HI[k])).astype(int))
    r = np.concatenate(rows)
    b = np.concatenate(bins)
    return r, b, np.concatenate(ys)


def bin_onehot(b: np.ndarray) -> np.ndarray:
    return np.eye(K)[b]


def incidence(H: np.ndarray) -> np.ndarray:
    return 1.0 - np.cumprod(1.0 - np.clip(H, 1e-7, 1 - 1e-7), axis=1)


def hazard_table(t_next: np.ndarray) -> pd.DataFrame:
    """Empirical per-bin hazard and its product-limit reconstruction."""
    out, S = [], 1.0
    for k in range(K):
        at = t_next > LO[k]
        ev = at & (t_next <= HI[k])
        h = ev.sum() / max(at.sum(), 1)
        S *= 1 - h
        out.append({"bin": k + 1, "interval_s": f"({LO[k]:g}, {HI[k]:g}]",
                    "at_risk": int(at.sum()), "events": int(ev.sum()),
                    "hazard": h, "F_from_hazards": 1 - S,
                    "prevalence_direct": float((t_next <= HI[k]).mean())})
    return pd.DataFrame(out)


class _Imputer:
    def fit(self, X):
        self.med = np.nanmedian(X, axis=0)
        self.med = np.where(np.isfinite(self.med), self.med, 0.0)
        Z = np.where(np.isnan(X), self.med, X)
        self.mu = Z.mean(0)
        self.sd = Z.std(0) + 1e-6
        return self

    def __call__(self, X):
        Z = np.where(np.isnan(X), self.med, X)
        return np.clip((Z - self.mu) / self.sd, -8, 8)


# ------------------------------------------------------------------ tabular
def _lgb_params(p: dict, seed: int) -> dict:
    base = dict(objective="binary", learning_rate=0.05, num_leaves=31, min_data_in_leaf=40,
                feature_fraction=0.8, bagging_fraction=0.8, bagging_freq=1, lambda_l2=1.0,
                verbose=-1, seed=seed, num_threads=2)
    base.update({k: v for k, v in p.items() if k != "rounds"})
    return base


class HazardLGBM:
    name = "LightGBM (hazard)"
    space = {"learning_rate": ("log", 0.01, 0.2), "num_leaves": ("int", 7, 63),
             "min_data_in_leaf": ("int", 10, 200), "feature_fraction": ("float", 0.4, 1.0),
             "lambda_l2": ("log", 1e-3, 10.0), "rounds": ("int", 100, 800)}

    def __init__(self, seed=0, **p):
        self.seed, self.p = seed, p

    def fit(self, X, t_next):
        import lightgbm as lgb
        r, b, y = to_long(X, t_next)
        Z = np.column_stack([X[r], b])
        self.m = lgb.train(_lgb_params(self.p, self.seed), lgb.Dataset(Z, y),
                           num_boost_round=int(self.p.get("rounds", 400)))
        return self

    def hazards(self, X):
        return np.column_stack([self.m.predict(np.column_stack([X, np.full(len(X), k)]))
                                for k in range(K)])

    def predict(self, X):
        return incidence(self.hazards(X))


class IndepLGBM(HazardLGBM):
    """K independent binary heads on the same rows (the control arm)."""
    name = "LightGBM (independent heads)"

    def fit(self, X, t_next):
        import lightgbm as lgb
        self.ms = []
        for k in range(K):
            y = (t_next <= HI[k]).astype(int)
            self.ms.append(lgb.train(_lgb_params(self.p, self.seed), lgb.Dataset(X, y),
                                     num_boost_round=int(self.p.get("rounds", 400))))
        return self

    def predict(self, X):
        return np.column_stack([m.predict(X) for m in self.ms])


class HazardLR:
    name = "Logistic regression (hazard)"
    space = {"C": ("log", 1e-3, 10.0)}

    def __init__(self, seed=0, C=0.1):
        self.seed, self.C = seed, C

    def fit(self, X, t_next):
        from sklearn.linear_model import LogisticRegression
        self.imp = _Imputer().fit(X)
        Z = self.imp(X)
        r, b, y = to_long(Z, t_next)
        D = np.column_stack([Z[r], bin_onehot(b)])
        self.m = LogisticRegression(C=self.C, max_iter=3000, fit_intercept=False)
        self.m.fit(D, y)
        return self

    def predict(self, X):
        Z = self.imp(X)
        H = np.column_stack([self.m.predict_proba(
            np.column_stack([Z, np.tile(np.eye(K)[k], (len(Z), 1))]))[:, 1] for k in range(K)])
        return incidence(H)


class HazardMLP:
    name = "MLP (hazard)"
    space = {"hidden": ("choice", [32, 64, 128, 256]), "alpha": ("log", 1e-5, 1e-1),
             "lr": ("log", 1e-4, 1e-2)}

    def __init__(self, seed=0, hidden=64, alpha=1e-3, lr=1e-3):
        self.seed, self.hidden, self.alpha, self.lr = seed, hidden, alpha, lr

    def fit(self, X, t_next):
        from sklearn.neural_network import MLPClassifier
        self.imp = _Imputer().fit(X)
        Z = self.imp(X)
        r, b, y = to_long(Z, t_next)
        D = np.column_stack([Z[r], bin_onehot(b)])
        self.m = MLPClassifier(hidden_layer_sizes=(self.hidden, self.hidden), alpha=self.alpha,
                               learning_rate_init=self.lr, max_iter=200, early_stopping=True,
                               validation_fraction=0.15, n_iter_no_change=10,
                               random_state=self.seed)
        self.m.fit(D, y)
        return self

    def predict(self, X):
        Z = self.imp(X)
        H = np.column_stack([self.m.predict_proba(
            np.column_stack([Z, np.tile(np.eye(K)[k], (len(Z), 1))]))[:, 1] for k in range(K)])
        return incidence(H)


# ------------------------------------------------------------------ rule
class A3Rule:
    """Deployed-rule score, parameter free (Eq. 2.1 with the recovered Off/Hys).

    score = margin of (M_n - Hys) - (M_s + Off) plus how long it has held;
    fitted on nothing. Scored with the lagged export like every other arm.
    """
    name = "Event A3 rule (deployed parameters)"
    space = {}

    def __init__(self, seed=0, cols=None, off=None, hys=None):
        self.cols, self.off, self.hys = cols, off, hys

    def fit(self, X, t_next):
        return self

    def predict(self, X):
        c = self.cols
        gap = X[:, c["gap"]]                       # serving - best neighbour (dB)
        off = np.nan_to_num(X[:, c["off"]], nan=1.0) if c.get("off") is not None else 1.0
        hys = np.nan_to_num(X[:, c["hys"]], nan=1.0) if c.get("hys") is not None else 1.0
        margin = -np.nan_to_num(gap, nan=20.0) - off - hys
        streak = np.nan_to_num(X[:, c["streak"]], nan=0.0)
        z = margin / 2.0 + np.clip(streak, 0, 5)
        p = 1 / (1 + np.exp(-z))
        return np.tile(p[:, None], (1, K))


# ------------------------------------------------------------------ sequence
class SeqHazard:
    """GRU / TCN / Transformer over windows of the same lagged feature rows."""
    space = {"hidden": ("choice", [16, 32, 64]), "lr": ("log", 3e-4, 3e-3),
             "dropout": ("float", 0.0, 0.4), "wd": ("log", 1e-6, 1e-3)}

    def __init__(self, arch="gru", seed=0, hidden=32, lr=1e-3, dropout=0.1, wd=1e-4,
                 window=10, epochs=25):
        self.arch, self.seed, self.hidden, self.lr = arch, seed, hidden, lr
        self.dropout, self.wd, self.window, self.epochs = dropout, wd, window, epochs
        self.name = {"gru": "GRU (hazard)", "tcn": "TCN (hazard)",
                     "transformer": "Transformer (hazard)"}[arch]

    # windows are built by the caller: (n, W, d) with the row itself last
    def _net(self, d):
        import torch.nn as nn
        H, arch, dr = self.hidden, self.arch, self.dropout

        class Net(nn.Module):
            def __init__(s):
                super().__init__()
                if arch == "gru":
                    s.enc = nn.GRU(d, H, batch_first=True)
                elif arch == "tcn":
                    s.enc = nn.Sequential(nn.Conv1d(d, H, 3, padding=2, dilation=1), nn.ReLU(),
                                          nn.Conv1d(H, H, 3, padding=4, dilation=2), nn.ReLU())
                else:
                    s.inp = nn.Linear(d, H)
                    s.enc = nn.TransformerEncoder(nn.TransformerEncoderLayer(
                        H, 4, 2 * H, dropout=dr, batch_first=True), 2)
                s.head = nn.Sequential(nn.Dropout(dr), nn.Linear(H, K))

            def forward(s, x):
                if arch == "gru":
                    o, _ = s.enc(x)
                    z = o[:, -1]
                elif arch == "tcn":
                    z = s.enc(x.transpose(1, 2))[:, :, -1 - 0]
                else:
                    z = s.enc(s.inp(x))[:, -1]
                return s.head(z)
        return Net()

    def fit(self, W, t_next):
        import torch
        torch.manual_seed(self.seed)
        np.random.seed(self.seed)
        torch.set_num_threads(2)
        n, L, d = W.shape
        flat = W.reshape(-1, d)
        self.imp = _Imputer().fit(flat)
        Z = self.imp(flat).reshape(n, L, d).astype(np.float32)
        at = np.column_stack([t_next > LO[k] for k in range(K)]).astype(np.float32)
        ev = np.column_stack([(t_next > LO[k]) & (t_next <= HI[k]) for k in range(K)]).astype(np.float32)
        # temporal tail as early-stopping split
        cut = int(n * 0.85)
        self.net = self._net(d)
        opt = torch.optim.AdamW(self.net.parameters(), lr=self.lr, weight_decay=self.wd)
        bce = torch.nn.BCEWithLogitsLoss(reduction="none")
        Xt, At, Et = map(torch.tensor, (Z, at, ev))
        best, best_state, bad = np.inf, None, 0
        for ep in range(self.epochs):
            self.net.train()
            perm = torch.randperm(cut)
            for i in range(0, cut, 256):
                b = perm[i:i + 256]
                out = self.net(Xt[b])
                loss = (bce(out, Et[b]) * At[b]).sum() / At[b].sum()
                opt.zero_grad()
                loss.backward()
                opt.step()
            self.net.eval()
            with torch.no_grad():
                out = self.net(Xt[cut:])
                vl = float((bce(out, Et[cut:]) * At[cut:]).sum() / At[cut:].sum())
            if vl < best - 1e-4:
                best, bad = vl, 0
                best_state = {k: v.clone() for k, v in self.net.state_dict().items()}
            else:
                bad += 1
                if bad >= 5:
                    break
        self.net.load_state_dict(best_state)
        return self

    def predict(self, W):
        import torch
        n, L, d = W.shape
        Z = self.imp(W.reshape(-1, d)).reshape(n, L, d).astype(np.float32)
        self.net.eval()
        with torch.no_grad():
            H = torch.sigmoid(self.net(torch.tensor(Z))).numpy()
        return incidence(H)


def make_windows(X: np.ndarray, frame: pd.DataFrame, full_X: np.ndarray, full_key: pd.Series,
                 L: int = 10) -> np.ndarray:
    """Windows of the L most recent feature rows (same capture, 1 s steps).

    ``full_X``/``full_key`` hold every row of the session (not only usable
    ones) keyed by (capture, whole-second time) so a window can reach into
    rows that are masked for labelling (e.g. the 2 s post-handover blank).
    """
    pos = pd.Series(np.arange(len(full_key)), index=pd.MultiIndex.from_frame(full_key))
    out = np.full((len(frame), L, X.shape[1]), np.nan, dtype=np.float32)
    caps = frame["capture"].to_numpy()
    ts = frame["t"].to_numpy()
    for j in range(L):
        dt = np.timedelta64(L - 1 - j, "s")
        keys = pd.MultiIndex.from_arrays([caps, ts - dt])
        p = pos.reindex(keys).to_numpy()
        ok = ~np.isnan(p)
        out[ok, j] = full_X[p[ok].astype(int)]
    return out


def sample_params(space: dict, rng: np.random.Generator) -> dict:
    p = {}
    for k, (kind, *a) in space.items():
        if kind == "log":
            p[k] = float(np.exp(rng.uniform(np.log(a[0]), np.log(a[1]))))
        elif kind == "int":
            p[k] = int(rng.integers(a[0], a[1] + 1))
        elif kind == "float":
            p[k] = float(rng.uniform(a[0], a[1]))
        else:
            p[k] = a[0][int(rng.integers(len(a[0])))]
    return p

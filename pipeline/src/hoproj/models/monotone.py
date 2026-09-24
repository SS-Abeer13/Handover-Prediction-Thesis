"""Monotone projection across the horizon axis, and a neural discrete-time hazard.

Both exist for one reason: to make the comparison in stage 09 fair.

The hazard formulation's two claimed advantages over four independent binary
heads are (a) better-calibrated probabilities and (b) predictions that respect
``P(T<=1) <= P(T<=2) <= ... `` by construction. Neither claim means anything
against a baseline that has been denied the obvious post-hoc fixes. A reviewer
will ask, correctly, whether isotonic calibration plus a monotone projection
closes the gap. So the baseline gets both, and a neural hazard model is added
so that "the hazard wins" cannot be confused with "LightGBM wins".
"""
from __future__ import annotations

import numpy as np

from ..utils import get_logger

LOG = get_logger("hoproj.monotone")


def pava_rows(P: np.ndarray, increasing: bool = True) -> np.ndarray:
    """Least-squares isotonic projection along axis 1, one row at a time.

    Pool-adjacent-violators. Unlike a running maximum - which is also monotone
    but only ever raises values, and so inflates every long-horizon probability
    - this is the L2-closest monotone sequence, which is the projection the
    baseline deserves.

    With a handful of horizons the loop over blocks is short, and the whole
    operation is a few milliseconds for thousands of rows.
    """
    Q = np.array(P, dtype=float, copy=True)
    if not increasing:
        Q = -Q
    n, k = Q.shape
    for i in range(n):
        v = Q[i]
        # each block is (sum, count); merge while the previous mean exceeds this
        means = np.empty(k)
        counts = np.empty(k)
        top = 0
        for j in range(k):
            means[top] = v[j]
            counts[top] = 1.0
            top += 1
            while top > 1 and means[top - 2] > means[top - 1]:
                s = means[top - 2] * counts[top - 2] + means[top - 1] * counts[top - 1]
                c = counts[top - 2] + counts[top - 1]
                top -= 1
                means[top - 1] = s / c
                counts[top - 1] = c
        out, pos = np.empty(k), 0
        for b in range(top):
            c = int(counts[b])
            out[pos:pos + c] = means[b]
            pos += c
        Q[i] = out
    return -Q if not increasing else Q


def isotonic_per_horizon(P_fit: np.ndarray, Y_fit: np.ndarray, M_fit: np.ndarray,
                         P_apply: np.ndarray) -> np.ndarray:
    """Fit one isotonic regression per horizon on held-out data, apply elsewhere.

    This is the standard post-hoc calibration a practitioner would reach for,
    and it is fitted on the fold's calibration rows only - never on the rows it
    is then scored against.
    """
    from sklearn.isotonic import IsotonicRegression

    out = np.array(P_apply, dtype=float, copy=True)
    for k in range(P_fit.shape[1]):
        sel = M_fit[:, k].astype(bool)
        if sel.sum() < 50 or len(np.unique(Y_fit[sel, k])) < 2:
            LOG.warning("horizon %d: too little calibration data, left uncalibrated", k)
            continue
        iso = IsotonicRegression(out_of_bounds="clip", y_min=0.0, y_max=1.0)
        iso.fit(P_fit[sel, k], Y_fit[sel, k])
        out[:, k] = iso.predict(P_apply[:, k])
    return out


class LogisticHazardMLP:
    """Neural discrete-time logistic hazard (Gensheimer & Narasimhan, 2019).

    Same long-format target as the LightGBM hazard model, different function
    class. Its role is to separate the two things the stage 09 result could
    mean: that the survival *formulation* helps, or that gradient boosting
    happens to be the better learner on this data. If the neural hazard also
    beats the neural multi-head, the formulation is doing the work.

    Kept deliberately small - this data is a few thousand rows.
    """

    def __init__(self, n_features: int, hidden: tuple[int, ...] = (48, 24),
                 lr: float = 3e-3, epochs: int = 40, batch: int = 1024,
                 weight_decay: float = 1e-4, seed: int = 0):
        self.n_features = n_features
        self.hidden = hidden
        self.lr = lr
        self.epochs = epochs
        self.batch = batch
        self.weight_decay = weight_decay
        self.seed = seed
        self.model = None

    def _build(self):
        import torch
        import torch.nn as nn

        torch.manual_seed(self.seed)
        layers, prev = [], self.n_features
        for h in self.hidden:
            layers += [nn.Linear(prev, h), nn.ReLU(), nn.Dropout(0.1)]
            prev = h
        layers += [nn.Linear(prev, 1)]
        return nn.Sequential(*layers)

    def fit(self, X: np.ndarray, y: np.ndarray):
        import torch

        # This box has two cores and several stages contend for them; letting
        # torch spawn its own pool makes every arm slower, not faster.
        torch.set_num_threads(1)
        from torch.utils.data import DataLoader, TensorDataset

        self.model = self._build()
        opt = torch.optim.AdamW(self.model.parameters(), lr=self.lr,
                                weight_decay=self.weight_decay)
        lossf = torch.nn.BCEWithLogitsLoss()
        ds = TensorDataset(torch.tensor(np.asarray(X, dtype=np.float32)),
                           torch.tensor(np.asarray(y, dtype=np.float32)))
        dl = DataLoader(ds, batch_size=self.batch, shuffle=True)
        self.model.train()
        for _ in range(self.epochs):
            for xb, yb in dl:
                opt.zero_grad()
                loss = lossf(self.model(xb).squeeze(-1), yb)
                loss.backward()
                opt.step()
        return self

    def predict(self, X) -> np.ndarray:
        import torch

        self.model.eval()
        with torch.no_grad():
            z = self.model(torch.tensor(np.asarray(X, dtype=np.float32))).squeeze(-1)
            return torch.sigmoid(z).numpy()

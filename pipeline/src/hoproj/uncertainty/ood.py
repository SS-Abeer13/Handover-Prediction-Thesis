"""Out-of-distribution scoring (section 22).

OOD here is not an abstract score: it is a set of *declared* experimental shifts
(geographic, temporal, mobility, operator, service, device).  The scores below
are the detectors; ``evaluate_ood`` measures whether a detector separates a
declared shift from held-out in-distribution drives, using AUROC and the
detection rate at a false-positive rate fixed on in-distribution data.
"""
from __future__ import annotations

import numpy as np

from ..utils import get_logger

LOG = get_logger("hoproj.ood")


class MahalanobisScorer:
    """Distance to the training representation cloud (shrunk covariance)."""

    name = "mahalanobis"

    def __init__(self, shrinkage: float = 1e-3):
        self.shrinkage = shrinkage
        self.mu_: np.ndarray | None = None
        self.prec_: np.ndarray | None = None

    def fit(self, Z: np.ndarray) -> "MahalanobisScorer":
        Z = np.asarray(Z, dtype=np.float64)
        self.mu_ = Z.mean(axis=0)
        cov = np.cov(Z - self.mu_, rowvar=False)
        cov = np.atleast_2d(cov)
        cov += self.shrinkage * np.trace(cov) / cov.shape[0] * np.eye(cov.shape[0])
        self.prec_ = np.linalg.pinv(cov)
        return self

    def score(self, Z: np.ndarray) -> np.ndarray:
        d = np.asarray(Z, dtype=np.float64) - self.mu_
        return np.einsum("ij,jk,ik->i", d, self.prec_, d)


class KnnScorer:
    """Mean distance to the k nearest training representations."""

    name = "knn"

    def __init__(self, k: int = 20, subsample: int = 20000, seed: int = 0):
        self.k = int(k)
        self.subsample = int(subsample)
        self.seed = seed
        self.nn_ = None

    def fit(self, Z: np.ndarray) -> "KnnScorer":
        from sklearn.neighbors import NearestNeighbors

        Z = np.asarray(Z, dtype=np.float32)
        if len(Z) > self.subsample:
            rng = np.random.default_rng(self.seed)
            Z = Z[rng.choice(len(Z), self.subsample, replace=False)]
        Z = Z / np.maximum(np.linalg.norm(Z, axis=1, keepdims=True), 1e-9)
        self.nn_ = NearestNeighbors(n_neighbors=min(self.k, len(Z))).fit(Z)
        return self

    def score(self, Z: np.ndarray) -> np.ndarray:
        Z = np.asarray(Z, dtype=np.float32)
        Z = Z / np.maximum(np.linalg.norm(Z, axis=1, keepdims=True), 1e-9)
        d, _ = self.nn_.kneighbors(Z)
        return d.mean(axis=1)


class DisagreementScorer:
    """Ensemble standard deviation (no fitting required)."""

    name = "ensemble_disagreement"

    def fit(self, *_a, **_k):
        return self

    def score(self, std: np.ndarray) -> np.ndarray:
        return np.asarray(std, float).mean(axis=1) if np.ndim(std) > 1 else np.asarray(std, float)


class EnergyScorer:
    """Negative log-sum-exp of the horizon logits: low energy = in-distribution."""

    name = "energy"

    def fit(self, *_a, **_k):
        return self

    def score(self, p: np.ndarray) -> np.ndarray:
        p = np.clip(np.atleast_2d(p), 1e-7, 1 - 1e-7)
        logits = np.log(p / (1 - p))
        return -np.log(np.exp(logits).sum(axis=1) + 1.0)


def build_scorers(cfg) -> dict:
    wanted = cfg.get_path("uncertainty.ood.scores", ["ensemble_disagreement", "mahalanobis", "knn"])
    out = {}
    for name in wanted:
        if name == "mahalanobis":
            out[name] = MahalanobisScorer()
        elif name == "knn":
            out[name] = KnnScorer(k=int(cfg.get_path("uncertainty.ood.knn_k", 20)),
                                  subsample=int(cfg.get_path("uncertainty.ood.knn_subsample", 20000)),
                                  seed=int(cfg.get_path("project.seed", 0)))
        elif name == "ensemble_disagreement":
            out[name] = DisagreementScorer()
        elif name == "energy":
            out[name] = EnergyScorer()
    return out


def evaluate_ood(score_in: np.ndarray, score_out: np.ndarray, fpr: float = 0.05) -> dict:
    """AUROC plus the shifted-data detection rate at a threshold set on in-distribution."""
    from sklearn.metrics import roc_auc_score

    score_in = np.asarray(score_in, float)
    score_out = np.asarray(score_out, float)
    score_in = score_in[np.isfinite(score_in)]
    score_out = score_out[np.isfinite(score_out)]
    if len(score_in) < 10 or len(score_out) < 10:
        return {"auroc": float("nan"), "detection_rate": float("nan"), "threshold": float("nan")}
    y = np.concatenate([np.zeros(len(score_in)), np.ones(len(score_out))])
    s = np.concatenate([score_in, score_out])
    thr = float(np.quantile(score_in, 1 - fpr))
    return {"auroc": float(roc_auc_score(y, s)),
            "detection_rate": float((score_out > thr).mean()),
            "threshold": thr,
            "fpr_in_distribution": float((score_in > thr).mean()),
            "n_in": len(score_in), "n_out": len(score_out)}


DECLARED_SHIFTS = {
    "geographic": "held-out route",
    "temporal": "different day / time period",
    "mobility": "substantially different speed distribution",
    "operator": "different operator (if collected)",
    "service": "different traffic / application condition",
    "device": "optional second UE",
}


def declare_shift_groups(drives, kind: str, dev_drives: list[str], ext_drives: list[str]) -> dict:
    """Map a declared shift name onto two drive sets (in-distribution, shifted)."""
    d = drives.set_index("drive_id")
    if kind == "geographic":
        return {"in": dev_drives, "out": ext_drives}
    if kind == "temporal":
        dates = sorted(d.loc[dev_drives, "date"].unique())
        if len(dates) < 2:
            return {}
        last = dates[-1]
        return {"in": [x for x in dev_drives if d.loc[x, "date"] != last],
                "out": [x for x in dev_drives if d.loc[x, "date"] == last]}
    if kind == "mobility":
        sp = d.loc[dev_drives, "mean_speed_kmh"]
        hi = sp.quantile(0.75)
        return {"in": sp[sp <= hi].index.tolist(), "out": sp[sp > hi].index.tolist()}
    return {}

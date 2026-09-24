"""Deep ensembles (Lakshminarayanan et al., [20]).

Members differ only by initialisation seed and batch order, trained on the same
grouped training drives.  The ensemble mean is the point prediction; the
disagreement between members is the epistemic-uncertainty signal used by the OOD
scorer and the abstention policy.
"""
from __future__ import annotations

import numpy as np

from ..utils import get_logger

LOG = get_logger("hoproj.ensemble")


class DeepEnsemble:
    def __init__(self, members: list):
        self.members = members

    @property
    def size(self) -> int:
        return len(self.members)

    def predict_matrix(self, ds, want: str = "handover") -> np.ndarray:
        """(M, N, H) stack of member predictions."""
        outs = []
        for i, m in enumerate(self.members):
            pred = m.predict(ds, want=(want,))[want]
            outs.append(np.atleast_2d(pred))
        return np.stack(outs, axis=0)

    def predict(self, ds, want: str = "handover") -> dict[str, np.ndarray]:
        P = self.predict_matrix(ds, want)
        mean = P.mean(axis=0)
        std = P.std(axis=0)
        # mutual information style decomposition for Bernoulli outputs
        ent_mean = _bernoulli_entropy(mean)
        mean_ent = _bernoulli_entropy(P).mean(axis=0)
        return {"mean": mean, "std": std,
                "total_entropy": ent_mean,
                "aleatoric": mean_ent,
                "epistemic": np.clip(ent_mean - mean_ent, 0, None)}

    def embeddings(self, ds) -> np.ndarray:
        """Mean representation across members (for distance-based OOD)."""
        zs = [m.predict(ds, want=("z",))["z"] for m in self.members]
        return np.mean(np.stack(zs, axis=0), axis=0)

    def save(self, dirpath):
        from pathlib import Path

        Path(dirpath).mkdir(parents=True, exist_ok=True)
        for i, m in enumerate(self.members):
            m.save(Path(dirpath) / f"member_{i:02d}.pt")


def _bernoulli_entropy(p: np.ndarray) -> np.ndarray:
    p = np.clip(p, 1e-7, 1 - 1e-7)
    return -(p * np.log(p) + (1 - p) * np.log(1 - p))

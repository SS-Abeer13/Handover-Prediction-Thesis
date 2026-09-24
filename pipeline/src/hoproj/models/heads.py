"""Task heads on a shared temporal representation (sections 19, 20).

``handover``  H independent logits, one per forecast horizon.
``qoe``       H independent logits for service degradation.
``dwell``     one scalar (log1p seconds) regression.
``target``    candidate-neighbour *ranking* head (section 17): the score of each
              candidate is computed from that candidate's own features plus the
              shared context, with shared weights across candidate slots.  There
              is no fixed Cell-ID output layer, so the head transfers to cells
              that never appeared in training.
"""
from __future__ import annotations

import torch
import torch.nn as nn


class BinaryMultiHorizonHead(nn.Module):
    def __init__(self, d_in: int, n_horizons: int, hidden: int = 64, dropout: float = 0.1):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(d_in, hidden), nn.GELU(), nn.Dropout(dropout),
                                 nn.Linear(hidden, n_horizons))

    def forward(self, z):
        return self.net(z)


class ScalarHead(nn.Module):
    def __init__(self, d_in: int, hidden: int = 64, dropout: float = 0.1):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(d_in, hidden), nn.GELU(), nn.Dropout(dropout),
                                 nn.Linear(hidden, 1))

    def forward(self, z):
        return self.net(z).squeeze(-1)


class CandidateRankingHead(nn.Module):
    """Shared-weight scorer over K candidate neighbours.

    Input ``cand`` has shape (B, K, C): per-candidate transferable attributes
    (its RSRP, the serving-to-candidate gap, its rank, its trend, whether it is
    the previous serving cell, ...).  The same MLP scores every slot, so adding a
    candidate - or meeting an unseen cell - needs no retraining of an output
    layer.
    """

    def __init__(self, d_ctx: int, d_cand: int, hidden: int = 64, dropout: float = 0.1):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(d_ctx + d_cand, hidden), nn.GELU(), nn.Dropout(dropout),
            nn.Linear(hidden, hidden // 2), nn.GELU(),
            nn.Linear(hidden // 2, 1))

    def forward(self, z, cand, cand_mask=None):
        B, K, _ = cand.shape
        ctx = z.unsqueeze(1).expand(B, K, z.shape[-1])
        scores = self.net(torch.cat([ctx, cand], dim=-1)).squeeze(-1)
        if cand_mask is not None:
            scores = scores.masked_fill(~cand_mask.bool(), float("-inf"))
        return scores


class MultiTaskModel(nn.Module):
    def __init__(self, encoder: nn.Module, n_horizons: int, tasks: dict,
                 d_cand: int = 0, head_hidden: int = 64, dropout: float = 0.1):
        super().__init__()
        self.encoder = encoder
        d = encoder.out_dim
        self.tasks = {k: v for k, v in tasks.items() if v.get("enabled")}
        self.ho_head = BinaryMultiHorizonHead(d, n_horizons, head_hidden, dropout) \
            if "handover" in self.tasks else None
        self.qoe_head = BinaryMultiHorizonHead(d, n_horizons, head_hidden, dropout) \
            if "qoe" in self.tasks else None
        self.dwell_head = ScalarHead(d, head_hidden, dropout) if "dwell" in self.tasks else None
        self.target_head = CandidateRankingHead(d, d_cand, head_hidden, dropout) \
            if ("target" in self.tasks and d_cand > 0) else None

    def embed(self, x):
        return self.encoder(x)

    def forward(self, x, cand=None, cand_mask=None):
        z = self.encoder(x)
        out = {"z": z}
        if self.ho_head is not None:
            out["handover"] = self.ho_head(z)
        if self.qoe_head is not None:
            out["qoe"] = self.qoe_head(z)
        if self.dwell_head is not None:
            out["dwell"] = self.dwell_head(z)
        if self.target_head is not None and cand is not None:
            out["target"] = self.target_head(z, cand, cand_mask)
        return out

    @property
    def n_params(self) -> int:
        return sum(p.numel() for p in self.parameters())

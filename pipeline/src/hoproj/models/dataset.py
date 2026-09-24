"""Torch datasets over the windowed tensors."""
from __future__ import annotations

import numpy as np
import torch
from torch.utils.data import Dataset


class SequenceDataset(Dataset):
    """(B, L, F) windows + masked multi-task targets.

    ``y_ho`` / ``m_ho``  (N, H) labels and per-horizon validity masks
    ``y_qoe`` / ``m_qoe``(N, H)
    ``y_dwell``/``m_dwell`` (N,)
    ``cand``             (N, K, C) per-candidate features for the ranking head
    ``y_target``         (N,) index of the true candidate, -1 where undefined
    """

    def __init__(self, X: np.ndarray, y_ho=None, m_ho=None, y_qoe=None, m_qoe=None,
                 y_dwell=None, m_dwell=None, cand=None, cand_mask=None, y_target=None):
        self.X = X
        self.y_ho, self.m_ho = y_ho, m_ho
        self.y_qoe, self.m_qoe = y_qoe, m_qoe
        self.y_dwell, self.m_dwell = y_dwell, m_dwell
        self.cand, self.cand_mask, self.y_target = cand, cand_mask, y_target

    def __len__(self) -> int:
        return len(self.X)

    def __getitem__(self, i: int) -> dict:
        item = {"x": torch.from_numpy(np.ascontiguousarray(self.X[i])).float()}
        if self.y_ho is not None:
            item["y_ho"] = torch.from_numpy(self.y_ho[i]).float()
            item["m_ho"] = torch.from_numpy(self.m_ho[i]).float()
        if self.y_qoe is not None:
            item["y_qoe"] = torch.from_numpy(self.y_qoe[i]).float()
            item["m_qoe"] = torch.from_numpy(self.m_qoe[i]).float()
        if self.y_dwell is not None:
            item["y_dwell"] = torch.tensor(float(self.y_dwell[i]))
            item["m_dwell"] = torch.tensor(float(self.m_dwell[i]))
        if self.cand is not None:
            item["cand"] = torch.from_numpy(self.cand[i]).float()
            item["cand_mask"] = torch.from_numpy(self.cand_mask[i]).float()
            item["y_target"] = torch.tensor(int(self.y_target[i]))
        return item

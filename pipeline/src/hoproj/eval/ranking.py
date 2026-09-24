"""Target-cell ranking metrics (section 23.3), including the unseen-cell split (RQ6)."""
from __future__ import annotations

import numpy as np
import pandas as pd


def ranking_metrics(scores: np.ndarray, y_idx: np.ndarray, valid: np.ndarray | None = None,
                    cand_mask: np.ndarray | None = None, top_k=(1, 2, 3)) -> dict:
    scores = np.atleast_2d(np.asarray(scores, float))
    y_idx = np.asarray(y_idx, int)
    sel = (y_idx >= 0) if valid is None else (valid.astype(bool) & (y_idx >= 0))
    if sel.sum() == 0:
        return {"n": 0, **{f"top{k}": np.nan for k in top_k}, "mrr": np.nan}
    s, y = scores[sel], y_idx[sel]
    order = np.argsort(-s, axis=1)
    ranks = np.argmax(order == y[:, None], axis=1) + 1
    out = {"n": int(sel.sum()), "mrr": float(np.mean(1.0 / ranks))}
    for k in top_k:
        out[f"top{k}"] = float((ranks <= k).mean())
    out["mean_rank"] = float(ranks.mean())
    return out


def unseen_cell_breakdown(scores: np.ndarray, y_idx: np.ndarray, target_cell: np.ndarray,
                          seen_cells: set, valid: np.ndarray | None = None) -> pd.DataFrame:
    """Split ranking performance by whether the true target cell was seen in training."""
    target_cell = pd.Series(target_cell).astype(str).to_numpy()
    is_seen = np.isin(target_cell, np.array(sorted(seen_cells), dtype=object).astype(str))
    rows = []
    for label, mask in (("seen_cells", is_seen), ("unseen_cells", ~is_seen)):
        v = mask if valid is None else (mask & valid.astype(bool))
        met = ranking_metrics(scores, y_idx, valid=v)
        met["subset"] = label
        rows.append(met)
    df = pd.DataFrame(rows)
    return df[["subset"] + [c for c in df.columns if c != "subset"]]


def fixed_classifier_metrics(pred_cell: np.ndarray, true_cell: np.ndarray,
                             seen_cells: set) -> dict:
    """Baseline: a fixed Cell-ID softmax cannot emit an unseen class - quantify that."""
    pred_cell = pd.Series(pred_cell).astype(str).to_numpy()
    true_cell = pd.Series(true_cell).astype(str).to_numpy()
    seen = np.array(sorted(map(str, seen_cells)), dtype=object).astype(str)
    is_seen = np.isin(true_cell, seen)
    return {
        "top1_overall": float((pred_cell == true_cell).mean()),
        "top1_seen": float((pred_cell[is_seen] == true_cell[is_seen]).mean()) if is_seen.any() else np.nan,
        "top1_unseen": 0.0 if (~is_seen).any() else np.nan,
        "unseen_fraction": float((~is_seen).mean()),
        "note": "a fixed Cell-ID classifier is structurally incapable of predicting an unseen class",
    }

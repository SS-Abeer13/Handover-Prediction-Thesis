"""Training / inference wrapper for the torch models.

Responsibilities
----------------
* masked multi-task loss (a sample contributes to a head only where its mask is 1)
* per-horizon positive weighting derived from *training* prevalence
* early stopping on a grouped validation split, never on test
* representation extraction (needed by the Mahalanobis / kNN OOD scores)
* deterministic seeding, so a deep ensemble differs only by its seed
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader

from ..utils import get_logger, set_seed
from .dataset import SequenceDataset
from .heads import MultiTaskModel
from .temporal import build_encoder

LOG = get_logger("hoproj.wrapper")


def pick_device(spec: str = "auto") -> torch.device:
    if spec and spec != "auto":
        return torch.device(spec)
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


@dataclass
class TrainHistory:
    epochs: list[int] = field(default_factory=list)
    train_loss: list[float] = field(default_factory=list)
    val_loss: list[float] = field(default_factory=list)
    val_metric: list[float] = field(default_factory=list)
    best_epoch: int = -1
    best_metric: float = float("-inf")


class TorchSeqModel:
    def __init__(self, name: str, n_features: int, n_horizons: int, tasks: dict,
                 params: dict, train_cfg: dict, d_cand: int = 0, seed: int = 0):
        self.name = name
        self.n_features = n_features
        self.n_horizons = n_horizons
        self.tasks = tasks
        self.params = params or {}
        self.train_cfg = train_cfg or {}
        self.d_cand = d_cand
        self.seed = seed
        self.device = pick_device(self.train_cfg.get("device", "auto"))
        set_seed(seed)
        encoder = build_encoder(name, n_features, self.params)
        self.model = MultiTaskModel(encoder, n_horizons, tasks, d_cand=d_cand).to(self.device)
        self.pos_weight_: torch.Tensor | None = None
        self.history = TrainHistory()

    # ------------------------------------------------------------------ loss
    def _compute_pos_weight(self, y: np.ndarray, m: np.ndarray) -> torch.Tensor:
        cap = float(self.train_cfg.get("pos_weight_cap", 20.0))
        w = []
        for j in range(y.shape[1]):
            sel = m[:, j].astype(bool)
            p = float(y[sel, j].mean()) if sel.any() else 0.5
            w.append(min(cap, (1 - p) / max(p, 1e-6)) if p > 0 else 1.0)
        return torch.tensor(w, dtype=torch.float32, device=self.device)

    def _loss(self, out: dict, batch: dict) -> tuple[torch.Tensor, dict]:
        parts = {}
        total = torch.zeros((), device=self.device)
        if "handover" in out and "y_ho" in batch:
            w = self.tasks.get("handover", {}).get("weight", 1.0)
            l = _masked_bce(out["handover"], batch["y_ho"], batch["m_ho"], self.pos_weight_)
            parts["handover"] = float(l.detach()); total = total + w * l
        if "qoe" in out and "y_qoe" in batch:
            w = self.tasks.get("qoe", {}).get("weight", 0.3)
            l = _masked_bce(out["qoe"], batch["y_qoe"], batch["m_qoe"], None)
            parts["qoe"] = float(l.detach()); total = total + w * l
        if "dwell" in out and "y_dwell" in batch:
            w = self.tasks.get("dwell", {}).get("weight", 0.1)
            m = batch["m_dwell"]
            diff = torch.nn.functional.smooth_l1_loss(out["dwell"], batch["y_dwell"], reduction="none")
            l = (diff * m).sum() / m.sum().clamp_min(1.0)
            parts["dwell"] = float(l.detach()); total = total + w * l
        if "target" in out and "y_target" in batch:
            w = self.tasks.get("target", {}).get("weight", 0.3)
            y = batch["y_target"]
            valid = y >= 0
            if valid.any():
                l = torch.nn.functional.cross_entropy(out["target"][valid], y[valid])
                parts["target"] = float(l.detach()); total = total + w * l
        return total, parts

    # ------------------------------------------------------------------- fit
    def fit(self, train_ds: SequenceDataset, val_ds: SequenceDataset | None = None,
            metric_fn=None) -> "TorchSeqModel":
        cfg = self.train_cfg
        bs = int(cfg.get("batch_size", 256))
        loader = DataLoader(train_ds, batch_size=bs, shuffle=True, drop_last=False,
                            num_workers=int(cfg.get("num_workers", 0)))
        val_loader = DataLoader(val_ds, batch_size=bs * 2, shuffle=False,
                                num_workers=int(cfg.get("num_workers", 0))) if val_ds else None
        if train_ds.y_ho is not None and cfg.get("pos_weight", "auto") == "auto":
            self.pos_weight_ = self._compute_pos_weight(train_ds.y_ho, train_ds.m_ho)
            LOG.info("%s pos_weight per horizon: %s", self.name,
                     np.round(self.pos_weight_.cpu().numpy(), 2).tolist())
        opt = torch.optim.AdamW(self.model.parameters(), lr=float(cfg.get("lr", 1e-3)),
                                weight_decay=float(cfg.get("weight_decay", 1e-4)))
        epochs = int(cfg.get("epochs", 60))
        sched = torch.optim.lr_scheduler.OneCycleLR(
            opt, max_lr=float(cfg.get("lr", 1e-3)), total_steps=max(1, epochs * max(1, len(loader))),
            pct_start=0.25)
        patience = int(cfg.get("early_stop_patience", 8))
        clip = float(cfg.get("grad_clip", 1.0))
        best_state, bad = None, 0

        for ep in range(1, epochs + 1):
            self.model.train()
            run, nb = 0.0, 0
            for batch in loader:
                batch = {k: v.to(self.device, non_blocking=True) for k, v in batch.items()}
                out = self.model(batch["x"], batch.get("cand"), batch.get("cand_mask"))
                loss, _ = self._loss(out, batch)
                opt.zero_grad(set_to_none=True)
                loss.backward()
                if clip:
                    nn.utils.clip_grad_norm_(self.model.parameters(), clip)
                opt.step()
                sched.step()
                run += float(loss.detach()); nb += 1
            tr_loss = run / max(nb, 1)

            val_loss, val_metric = float("nan"), float("nan")
            if val_loader is not None:
                val_loss, preds, ys, ms = self._evaluate(val_loader)
                val_metric = metric_fn(ys, preds, ms) if metric_fn else -val_loss
            self.history.epochs.append(ep)
            self.history.train_loss.append(tr_loss)
            self.history.val_loss.append(val_loss)
            self.history.val_metric.append(val_metric)

            score = val_metric if np.isfinite(val_metric) else -tr_loss
            if score > self.history.best_metric + 1e-6:
                self.history.best_metric, self.history.best_epoch, bad = score, ep, 0
                best_state = {k: v.detach().cpu().clone() for k, v in self.model.state_dict().items()}
            else:
                bad += 1
            if ep == 1 or ep % 5 == 0 or bad >= patience:
                LOG.info("%s ep%03d train=%.4f val=%.4f metric=%.4f (best %.4f @ep%d)",
                         self.name, ep, tr_loss, val_loss, val_metric,
                         self.history.best_metric, self.history.best_epoch)
            if bad >= patience:
                LOG.info("%s early stop at epoch %d", self.name, ep)
                break
        if best_state is not None:
            self.model.load_state_dict(best_state)
        return self

    @torch.no_grad()
    def _evaluate(self, loader) -> tuple[float, np.ndarray, np.ndarray, np.ndarray]:
        self.model.eval()
        tot, nb = 0.0, 0
        P, Y, M = [], [], []
        for batch in loader:
            batch = {k: v.to(self.device) for k, v in batch.items()}
            out = self.model(batch["x"], batch.get("cand"), batch.get("cand_mask"))
            loss, _ = self._loss(out, batch)
            tot += float(loss); nb += 1
            if "handover" in out:
                P.append(torch.sigmoid(out["handover"]).cpu().numpy())
                Y.append(batch["y_ho"].cpu().numpy())
                M.append(batch["m_ho"].cpu().numpy())
        return (tot / max(nb, 1),
                np.concatenate(P) if P else np.empty((0, 0)),
                np.concatenate(Y) if Y else np.empty((0, 0)),
                np.concatenate(M) if M else np.empty((0, 0)))

    # --------------------------------------------------------------- predict
    @torch.no_grad()
    def predict(self, ds: SequenceDataset, batch_size: int | None = None,
                want: tuple[str, ...] = ("handover",)) -> dict[str, np.ndarray]:
        bs = batch_size or int(self.train_cfg.get("batch_size", 256)) * 2
        loader = DataLoader(ds, batch_size=bs, shuffle=False)
        self.model.eval()
        buckets: dict[str, list] = {k: [] for k in want}
        for batch in loader:
            batch = {k: v.to(self.device) for k, v in batch.items()}
            out = self.model(batch["x"], batch.get("cand"), batch.get("cand_mask"))
            for key in want:
                if key == "z":
                    buckets["z"].append(out["z"].cpu().numpy())
                elif key == "dwell" and "dwell" in out:
                    buckets["dwell"].append(out["dwell"].cpu().numpy())
                elif key == "target" and "target" in out:
                    buckets["target"].append(out["target"].cpu().numpy())
                elif key in out:
                    buckets[key].append(torch.sigmoid(out[key]).cpu().numpy())
        return {k: np.concatenate(v) for k, v in buckets.items() if v}

    def predict_proba(self, ds, **kw) -> np.ndarray:
        return self.predict(ds, want=("handover",), **kw)["handover"]

    # ------------------------------------------------------------------- io
    def save(self, path: str | Path) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        torch.save({"state_dict": self.model.state_dict(), "name": self.name,
                    "n_features": self.n_features, "n_horizons": self.n_horizons,
                    "tasks": self.tasks, "params": self.params, "d_cand": self.d_cand,
                    "seed": self.seed, "history": self.history.__dict__}, path)

    @classmethod
    def load(cls, path: str | Path, train_cfg: dict | None = None) -> "TorchSeqModel":
        blob = torch.load(path, map_location="cpu", weights_only=False)
        obj = cls(blob["name"], blob["n_features"], blob["n_horizons"], blob["tasks"],
                  blob["params"], train_cfg or {}, blob.get("d_cand", 0), blob.get("seed", 0))
        obj.model.load_state_dict(blob["state_dict"])
        return obj

    @property
    def n_params(self) -> int:
        return self.model.n_params


def _masked_bce(logits, y, m, pos_weight):
    loss = torch.nn.functional.binary_cross_entropy_with_logits(
        logits, y, reduction="none", pos_weight=pos_weight)
    return (loss * m).sum() / m.sum().clamp_min(1.0)

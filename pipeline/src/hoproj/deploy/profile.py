"""Deployment profiling (section 23.7): latency, model size, memory, throughput."""
from __future__ import annotations

import time
from pathlib import Path

import numpy as np

from ..utils import get_logger

LOG = get_logger("hoproj.deploy")


def profile_torch_model(model, window_len: int, n_features: int,
                        batch_sizes=(1, 32, 256), repeats: int = 50,
                        device: str | None = None) -> list[dict]:
    import torch

    dev = torch.device(device) if device else next(model.parameters()).device
    model = model.to(dev).eval()
    rows = []
    for bs in batch_sizes:
        x = torch.randn(bs, window_len, n_features, device=dev)
        with torch.no_grad():
            for _ in range(5):
                model(x)
            if dev.type == "cuda":
                torch.cuda.synchronize()
                torch.cuda.reset_peak_memory_stats()
            times = []
            for _ in range(repeats):
                t0 = time.perf_counter()
                model(x)
                if dev.type == "cuda":
                    torch.cuda.synchronize()
                times.append((time.perf_counter() - t0) * 1000.0)
        times = np.array(times)
        row = {
            "device": dev.type, "batch_size": bs,
            "latency_ms_mean": float(times.mean()),
            "latency_ms_p50": float(np.percentile(times, 50)),
            "latency_ms_p95": float(np.percentile(times, 95)),
            "per_sample_ms": float(times.mean() / bs),
            "predictions_per_second": float(bs / (times.mean() / 1000.0)),
        }
        if dev.type == "cuda":
            row["peak_gpu_mb"] = float(torch.cuda.max_memory_allocated() / 1024**2)
        rows.append(row)
    return rows


def model_footprint(model) -> dict:
    import torch

    n_params = sum(p.numel() for p in model.parameters())
    n_train = sum(p.numel() for p in model.parameters() if p.requires_grad)
    bytes_ = sum(p.numel() * p.element_size() for p in model.parameters())
    bytes_ += sum(b.numel() * b.element_size() for b in model.buffers())
    return {"n_parameters": int(n_params), "n_trainable": int(n_train),
            "state_size_mb": float(bytes_ / 1024**2)}


def export_onnx(model, window_len: int, n_features: int, path: str | Path) -> str | None:
    import torch

    try:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        dummy = torch.randn(1, window_len, n_features)
        torch.onnx.export(model.cpu().eval(), (dummy,), str(path),
                          input_names=["window"], output_names=["handover_logits"],
                          dynamic_axes={"window": {0: "batch"}}, opset_version=17)
        return str(path)
    except Exception as exc:                        # pragma: no cover
        LOG.warning("ONNX export failed: %s", exc)
        return None

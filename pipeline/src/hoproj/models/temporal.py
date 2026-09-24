"""Temporal encoders: GRU, LSTM, TCN, Transformer (section 19).

All four expose the same contract - ``(B, L, F) -> (B, D)`` - so the multi-task
head stack, the ensemble, the OOD scorer and the latency profiler are identical
across architectures.  That is what makes the accuracy/latency comparison in RQ7
a fair one.
"""
from __future__ import annotations

import math

import torch
import torch.nn as nn


class GRUEncoder(nn.Module):
    def __init__(self, n_features: int, hidden: int = 96, layers: int = 2,
                 dropout: float = 0.2, bidirectional: bool = False, **_):
        super().__init__()
        self.rnn = nn.GRU(n_features, hidden, num_layers=layers, batch_first=True,
                          dropout=dropout if layers > 1 else 0.0, bidirectional=bidirectional)
        self.out_dim = hidden * (2 if bidirectional else 1)
        self.norm = nn.LayerNorm(self.out_dim)

    def forward(self, x):
        h, _ = self.rnn(x)
        return self.norm(h[:, -1])


class LSTMEncoder(nn.Module):
    def __init__(self, n_features: int, hidden: int = 96, layers: int = 2,
                 dropout: float = 0.2, bidirectional: bool = False, **_):
        super().__init__()
        self.rnn = nn.LSTM(n_features, hidden, num_layers=layers, batch_first=True,
                           dropout=dropout if layers > 1 else 0.0, bidirectional=bidirectional)
        self.out_dim = hidden * (2 if bidirectional else 1)
        self.norm = nn.LayerNorm(self.out_dim)

    def forward(self, x):
        h, _ = self.rnn(x)
        return self.norm(h[:, -1])


class _Chomp(nn.Module):
    def __init__(self, size: int):
        super().__init__()
        self.size = size

    def forward(self, x):
        return x[:, :, : -self.size] if self.size > 0 else x


class _TCNBlock(nn.Module):
    """Causal dilated residual block - no leakage from future timesteps."""

    def __init__(self, c_in: int, c_out: int, kernel: int, dilation: int, dropout: float):
        super().__init__()
        pad = (kernel - 1) * dilation
        self.net = nn.Sequential(
            nn.Conv1d(c_in, c_out, kernel, padding=pad, dilation=dilation),
            _Chomp(pad), nn.GELU(), nn.Dropout(dropout),
            nn.Conv1d(c_out, c_out, kernel, padding=pad, dilation=dilation),
            _Chomp(pad), nn.GELU(), nn.Dropout(dropout),
        )
        self.down = nn.Conv1d(c_in, c_out, 1) if c_in != c_out else nn.Identity()

    def forward(self, x):
        return torch.nn.functional.gelu(self.net(x) + self.down(x))


class TCNEncoder(nn.Module):
    def __init__(self, n_features: int, channels=(64, 64, 64), kernel_size: int = 3,
                 dropout: float = 0.15, **_):
        super().__init__()
        blocks, c_in = [], n_features
        for i, c_out in enumerate(channels):
            blocks.append(_TCNBlock(c_in, c_out, kernel_size, 2 ** i, dropout))
            c_in = c_out
        self.net = nn.Sequential(*blocks)
        self.out_dim = c_in
        self.norm = nn.LayerNorm(c_in)

    def forward(self, x):
        h = self.net(x.transpose(1, 2))
        return self.norm(h[:, :, -1])


class _PositionalEncoding(nn.Module):
    def __init__(self, d_model: int, max_len: int = 512):
        super().__init__()
        pe = torch.zeros(max_len, d_model)
        pos = torch.arange(max_len).unsqueeze(1).float()
        div = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))
        pe[:, 0::2] = torch.sin(pos * div)
        pe[:, 1::2] = torch.cos(pos * div[: pe[:, 1::2].shape[1]])
        self.register_buffer("pe", pe.unsqueeze(0))

    def forward(self, x):
        return x + self.pe[:, : x.size(1)]


class TransformerEncoder(nn.Module):
    def __init__(self, n_features: int, d_model: int = 96, nhead: int = 4, layers: int = 2,
                 ff: int = 192, dropout: float = 0.15, **_):
        super().__init__()
        self.proj = nn.Linear(n_features, d_model)
        self.pos = _PositionalEncoding(d_model)
        layer = nn.TransformerEncoderLayer(d_model, nhead, ff, dropout, batch_first=True,
                                           norm_first=True, activation="gelu")
        self.enc = nn.TransformerEncoder(layer, layers)
        self.out_dim = d_model
        self.norm = nn.LayerNorm(d_model)

    def forward(self, x):
        L = x.size(1)
        causal = torch.triu(torch.ones(L, L, device=x.device, dtype=torch.bool), diagonal=1)
        h = self.enc(self.pos(self.proj(x)), mask=causal)
        return self.norm(h[:, -1])


class MLPEncoder(nn.Module):
    """Snapshot neural baseline: uses only the last timestep."""

    def __init__(self, n_features: int, hidden=(128, 64), dropout: float = 0.2, **_):
        super().__init__()
        dims, layers = [n_features, *hidden], []
        for a, b in zip(dims[:-1], dims[1:]):
            layers += [nn.Linear(a, b), nn.GELU(), nn.Dropout(dropout)]
        self.net = nn.Sequential(*layers)
        self.out_dim = dims[-1]

    def forward(self, x):
        return self.net(x[:, -1])


ENCODERS = {
    "gru": GRUEncoder, "lstm": LSTMEncoder, "tcn": TCNEncoder,
    "transformer": TransformerEncoder, "mlp": MLPEncoder,
}


def build_encoder(name: str, n_features: int, params: dict) -> nn.Module:
    if name not in ENCODERS:
        raise KeyError(f"unknown encoder {name!r}; known: {sorted(ENCODERS)}")
    kwargs = dict(params or {})
    if name == "tcn" and "channels" in kwargs:
        kwargs["channels"] = tuple(kwargs["channels"])
    if name == "mlp" and "hidden" in kwargs:
        kwargs["hidden"] = tuple(kwargs["hidden"])
    return ENCODERS[name](n_features, **kwargs)

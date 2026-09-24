"""Smoke and correctness tests. Run with: pytest -q"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from hoproj.config import Config, deep_merge, load_config, parse_cli_overrides
from hoproj.data import labels as L
from hoproj.data.segment import drive_table, segment_drives
from hoproj.data.splits import make_splits, row_masks
from hoproj.data.transforms import TabularTransform
from hoproj.data.windows import build_window_index, materialise
from hoproj.eval.events import event_level_metrics
from hoproj.eval.metrics import classification_metrics, recall_at_fpr
from hoproj.uncertainty.calibration import TemperatureScaler, expected_calibration_error
from hoproj.uncertainty.conformal import BinaryMondrianConformal


def synth(n_drives=8, n=400, seed=0):
    rng = np.random.default_rng(seed)
    rows = []
    t0 = pd.Timestamp("2026-01-01")
    for d in range(n_drives):
        t = t0 + pd.to_timedelta(np.arange(n) + d * 10_000, unit="s")
        lat = 23.78 + np.linspace(0, 0.02, n) * (1 if d % 2 == 0 else -1)
        rows.append(pd.DataFrame({
            "t": t, "lat": lat, "lon": 90.41 + rng.normal(0, 1e-5, n),
            "speed_kmh": np.clip(rng.normal(30, 5, n), 0, None),
            "serving_rsrp": -80 + 10 * np.sin(np.arange(n) / 30) + rng.normal(0, 1, n),
            "serving_rsrq": rng.normal(-10, 1, n), "serving_sinr": rng.normal(10, 3, n),
            "serving_rssi": rng.normal(-60, 3, n), "serving_cqi": rng.integers(3, 15, n),
            "serving_pci": (np.arange(n) // 50 % 5).astype(float),
            "serving_cell_name": ["c%d" % (i // 50 % 5) for i in range(n)],
            "nbr1_id": ((np.arange(n) // 50 + 1) % 5).astype(float),
            "nbr1_rsrp": rng.normal(-85, 3, n),
            "nbr2_id": ((np.arange(n) // 50 + 2) % 5).astype(float),
            "nbr2_rsrp": rng.normal(-90, 3, n),
            "nbr3_id": ((np.arange(n) // 50 + 3) % 5).astype(float),
            "nbr3_rsrp": rng.normal(-95, 3, n),
            "dl_tp_kbps": np.clip(rng.normal(20000, 5000, n), 0, None),
            "ul_tp_kbps": np.clip(rng.normal(4000, 800, n), 0, None),
            "rtt_ms": np.clip(rng.normal(60, 15, n), 1, None),
            "pkt_loss_pct": np.clip(rng.normal(1.5, 0.7, n), 0, None),
            "phy_dl_kbps": np.nan, "phy_ul_kbps": np.nan,
            "serving_band": "Band 3", "serving_earfcn": 1500.0, "serving_enb": 1.0,
            "plmn": 101.0, "is_interpolated": False, "session_id": d, "route_id": "r1",
        }))
    return pd.concat(rows, ignore_index=True)


@pytest.fixture(scope="module")
def cfg():
    c = load_config("base.yaml", adapter="curated_v1")
    c.set_path("project.seed", 7)
    return c


def test_config_merge_and_overrides():
    merged = deep_merge({"a": {"b": 1, "c": 2}}, {"a": {"b": 9}})
    assert merged == {"a": {"b": 9, "c": 2}}
    assert parse_cli_overrides(["train.epochs=3"]) == {"train": {"epochs": 3}}
    c = Config({"x": {"y": 5}})
    assert c.get_path("x.y") == 5 and c.get_path("x.z", "d") == "d"


def test_segmentation_splits_directions(cfg):
    s = segment_drives(synth(), cfg)
    tbl = drive_table(s)
    assert tbl["drive_id"].is_unique
    assert len(tbl) >= 8
    assert set(tbl["direction"]) <= {"fwd", "rev"}


def test_labels_are_causal_and_masked(cfg):
    s = segment_drives(synth(), cfg)
    ho = L.handover_events(s, None, Config(deep_merge(
        cfg, {"labels": {"handover": {"source": "serving_cell_change"}}})))
    lab = L.build_labels(s, ho, cfg, {"dl_tp_low": 15000.0, "min_rules": 1})
    tags = L.horizon_tags(cfg)
    # a longer horizon can never have fewer positives than a shorter one
    pos = [lab[f"y_ho_{t}"].sum() for t in tags]
    assert pos == sorted(pos)
    # samples just after a handover are masked out
    blank = float(cfg.get_path("labels.handover.post_event_blank_s"))
    just_after = lab["t_since_prev_ho_s"].fillna(1e9) < blank
    assert lab.loc[just_after, f"m_ho_{tags[0]}"].sum() == 0


def test_usable_horizons_drops_subsample(cfg):
    c = Config(deep_merge(cfg, {"data": {"target_period_s": 1.0},
                                "labels": {"horizons_s": [0.25, 0.5, 1.0, 2.0]}}))
    assert L.usable_horizons(c) == [1.0, 2.0]


def test_splits_are_disjoint_by_drive(cfg):
    raw = synth(n_drives=20)
    raw["route_id"] = np.where(raw["session_id"] < 14, "dev_route", "ext_route")
    s = segment_drives(raw, cfg)
    tbl = drive_table(s)
    c = Config(deep_merge(cfg, {"splits": {"external_route": "ext_route"}}))
    sp = make_splits(tbl, c)
    g = sp["grouped_drive"]
    parts = [set(g.train), set(g.val), set(g.calib), set(g.test)]
    for i in range(len(parts)):
        for j in range(i + 1, len(parts)):
            assert not parts[i] & parts[j], "development partitions share a drive"
    assert not set(sp["external_route"].test) & set(sp["external_route"].train)
    ext_ids = set(tbl.loc[tbl["route_id"] == "ext_route", "drive_id"])
    assert set(sp["external_route"].test) == ext_ids


def test_transform_is_fitted_on_train_only():
    X = pd.DataFrame({"a": np.arange(100.0), "b": np.r_[np.zeros(50), np.ones(50) * 1000]})
    train = np.r_[np.ones(50, bool), np.zeros(50, bool)]
    tf = TabularTransform("robust").fit(X.loc[train])
    out = tf.transform(X)
    assert np.isfinite(out).all()
    # the transform never saw the second half, so its scale reflects only the first
    assert tf.center_["b"] == 0.0


def test_windows_never_cross_drives():
    frame = pd.DataFrame({"drive_id": ["a"] * 20 + ["b"] * 20,
                          "route_id": ["r"] * 40})
    wi = build_window_index(frame, length=5, stride=1)
    for s, e, d in zip(wi.start_pos, wi.end_pos, wi.drive_id):
        assert set(frame["drive_id"].iloc[s:e + 1]) == {d}
    X = np.arange(40 * 3, dtype=np.float32).reshape(40, 3)
    T = materialise(X, wi)
    assert T.shape == (len(wi), 5, 3)
    assert np.allclose(T[0], X[0:5])


def test_metrics_and_calibration():
    rng = np.random.default_rng(0)
    y = (rng.random(5000) < 0.1).astype(float)
    p = np.clip(0.1 + 0.6 * y + rng.normal(0, 0.15, 5000), 0.001, 0.999)
    m = classification_metrics(y, p)
    assert m["auprc"] > m["positive_rate"]
    r, thr = recall_at_fpr(y, p, 0.05)
    assert 0 <= r <= 1
    # temperature scaling optimises NLL on the calibration pool; it must not make
    # the negative log likelihood worse, and it must leave the ranking untouched.
    over = np.clip(p ** 3, 1e-4, 1 - 1e-4)
    ts = TemperatureScaler().fit(over[:, None], y[:, None])
    cal = ts.transform(over[:, None])[:, 0]
    nll = lambda q: -np.mean(y * np.log(q) + (1 - y) * np.log(1 - q))
    assert nll(cal) <= nll(over) + 1e-9
    assert classification_metrics(y, cal)["auprc"] == pytest.approx(
        classification_metrics(y, over)["auprc"], abs=1e-9)
    assert np.isfinite(expected_calibration_error(y, cal))


def test_conformal_coverage_is_near_nominal():
    rng = np.random.default_rng(1)
    n = 6000
    y = (rng.random(n) < 0.2).astype(int)
    p = np.clip(np.where(y == 1, rng.beta(6, 3, n), rng.beta(3, 6, n)), 1e-4, 1 - 1e-4)
    cp = BinaryMondrianConformal(alpha=0.1).fit(p[:3000, None], y[:3000, None])
    cov = cp.coverage(p[3000:, None], y[3000:, None])
    assert 0.85 <= cov[0]["empirical_coverage"] <= 0.96


def test_event_metrics_count_each_event_once():
    t = pd.date_range("2026-01-01", periods=60, freq="1s")
    meta = pd.DataFrame({"t": t, "drive_id": "d1", "dist_in_drive_m": np.arange(60) * 10.0})
    p = np.zeros(60)
    p[25:30] = 0.9                       # one long alarm before the event at 30
    ho = pd.DataFrame({"drive_id": ["d1"], "t": [t[30]]})
    res = event_level_metrics(meta, p, ho, threshold=0.5, warn_horizon_s=5.0)
    assert res["n_events"] == 1
    assert res["n_detected"] == 1
    assert res["n_alarm_episodes"] == 1
    assert res["median_lead_time_s"] == 5.0
    assert res["n_false_alarm_episodes"] == 0

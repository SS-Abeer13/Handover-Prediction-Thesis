"""The signalling features are the ones most able to leak, so they get tests.

A measurement report precedes the handover command it triggers by 50-200 ms,
which is well inside one 1 Hz sample. Any feature that counts reports in the
*current* bin is therefore reading the answer, and the model would look
excellent for the wrong reason. These tests pin the boundary.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from hoproj.data.signalling_features import (a3_condition_held, report_history,
                                             rf_slopes, ttt_clock)


def _frame(n=10, drive="d1", start="2026-09-10 12:00:00"):
    t = pd.date_range(start, periods=n, freq="1s")
    return pd.DataFrame({"t": t, "drive_id": drive,
                         "gap_serving_nbr1": np.zeros(n),
                         "a3_offset_db": np.full(n, 1.0),
                         "hysteresis_db": np.zeros(n),
                         "time_to_trigger_ms": np.full(n, 320.0),
                         "serving_rsrp": np.arange(n, dtype=float),
                         "serving_sinr": np.zeros(n)})


def test_report_counts_exclude_the_current_bin():
    """A report inside the current sample must not be visible to that sample."""
    f = _frame(5)
    # one report at exactly the 3rd sample's timestamp
    reports = pd.DataFrame({"t": [f["t"].iloc[3]], "event_id": ["A3"]})
    out = report_history(f, reports, period_s=1.0)
    assert out["sig_a3_reports_prev1s"].iloc[3] == 0.0, "current bin leaked"
    # it becomes visible one sample later
    assert out["sig_a3_reports_prev1s"].iloc[4] == 1.0


def test_report_counts_respect_the_window_length():
    f = _frame(8)
    reports = pd.DataFrame({"t": [f["t"].iloc[1], f["t"].iloc[2]],
                            "event_id": ["A3", "A1"]})
    out = report_history(f, reports, period_s=1.0)
    # at sample 5 the visible window (t-3, t-1] covers samples 2..4
    assert out["sig_reports_prev3s"].iloc[5] == 1.0
    # only one of the two is an A3
    assert out["sig_a3_reports_prev3s"].iloc[5] == 0.0


def test_a3_condition_uses_the_negated_offset():
    """A3 fires when gap < -(offset + hysteresis), not when gap < offset."""
    f = _frame(3)
    f["gap_serving_nbr1"] = [-2.0, 0.0, 2.0]
    f["a3_offset_db"] = 1.0
    f["hysteresis_db"] = 0.0
    held = a3_condition_held(f).to_numpy()
    assert held.tolist() == [True, False, False]


def test_a3_condition_handles_negative_offsets():
    f = _frame(3)
    f["gap_serving_nbr1"] = [5.0, 9.0, 11.0]
    f["a3_offset_db"] = -10.0
    f["hysteresis_db"] = 0.0
    # fires when gap < 10
    assert a3_condition_held(f).to_numpy().tolist() == [True, True, False]


def test_ttt_clock_accumulates_and_resets():
    f = _frame(6)
    f["gap_serving_nbr1"] = [-5, -5, -5, 5, -5, -5]
    out = ttt_clock(f)
    # first True credits 0, then one second per sample, reset by the False
    assert out["sig_a3_hold_s"].tolist() == [0.0, 1.0, 2.0, 0.0, 0.0, 1.0]


def test_ttt_clock_resets_at_a_drive_boundary():
    a, b = _frame(3, "d1"), _frame(3, "d2", "2026-09-10 13:00:00")
    f = pd.concat([a, b], ignore_index=True)
    f["gap_serving_nbr1"] = -5.0
    out = ttt_clock(f)
    assert out["sig_a3_hold_s"].iloc[3] == 0.0, "clock carried across drives"


def test_slopes_are_backward_looking_and_per_drive():
    a, b = _frame(6, "d1"), _frame(6, "d2", "2026-09-10 13:00:00")
    f = pd.concat([a, b], ignore_index=True)
    out = rf_slopes(f, period_s=1.0)
    col = "sig_dserving_rsrp_3s"
    assert np.isnan(out[col].iloc[0]), "first sample cannot have a slope"
    assert np.isnan(out[col].iloc[6]), "slope leaked across the drive boundary"
    # serving_rsrp increases by 1 per sample, so a 3 s slope is 1.0 dB/s
    assert np.isclose(out[col].iloc[3], 1.0)

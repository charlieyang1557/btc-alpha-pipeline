# tests/test_patha_floors.py
"""Path A hypothesis-class eligibility floors (Task C7).

LOCK Pre-registration 3:
  H1 (long-biased overlay): >= 200 DEFENSIVE FLAT-EXIT EPISODES (long->flat
    transitions, the funding-signal firings) over TRAIN — NOT long-bar occupancy.
  H2 / H3 (state-class): zero_fraction < 0.50 AND >= 200 trades over TRAIN.
Under-floor -> INDETERMINATE (not a Tier-5 pass/fail).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from backtest.patha_orchestrator import (
    INDETERMINATE,
    count_flat_exit_episodes,
    h1_floor,
    h2h3_floor,
    position_series_from_trades,
    zero_fraction_from_positions,
)


# ---------------------------------------------------------------------------
# count_flat_exit_episodes (long->flat transitions on a position series)
# ---------------------------------------------------------------------------


def test_count_flat_exit_episodes_counts_long_to_flat_transitions():
    # position: 0 1 1 0 1 0  -> two long->flat transitions (index 2->3, 4->5).
    pos = np.array([0, 1, 1, 0, 1, 0])
    assert count_flat_exit_episodes(pos) == 2


def test_count_flat_exit_episodes_ignores_flat_to_long():
    # 0->1 is an ENTRY, not a defensive flat-exit; only 1->0 counts.
    pos = np.array([0, 1, 0, 1])
    assert count_flat_exit_episodes(pos) == 1  # only the single 1->0


def test_count_flat_exit_episodes_all_long_is_zero():
    pos = np.ones(500)
    assert count_flat_exit_episodes(pos) == 0


# ---------------------------------------------------------------------------
# H1 floor: >= 200 flat-exit episodes
# ---------------------------------------------------------------------------


def test_h1_floor_eligible_at_200_episodes():
    # build a position series with exactly 200 long->flat transitions.
    pos = np.tile([1, 0], 200)  # 200 (1->0) transitions
    out = h1_floor(pos)
    assert out["eligible"] is True
    assert out["flat_exit_episodes"] == 200
    assert out["status"] != INDETERMINATE


def test_h1_floor_under_floor_is_indeterminate():
    pos = np.tile([1, 0], 50)  # 50 transitions < 200
    out = h1_floor(pos)
    assert out["eligible"] is False
    assert out["status"] == INDETERMINATE
    assert out["flat_exit_episodes"] == 50


# ---------------------------------------------------------------------------
# H2/H3 floor: zero_fraction < 0.50 AND >= 200 trades
# ---------------------------------------------------------------------------


def test_h2h3_floor_eligible_when_active_and_enough_trades():
    out = h2h3_floor(zero_fraction=0.30, total_trades=250)
    assert out["eligible"] is True
    assert out["status"] != INDETERMINATE


def test_h2h3_floor_indeterminate_when_too_inactive():
    out = h2h3_floor(zero_fraction=0.60, total_trades=250)
    assert out["eligible"] is False
    assert out["status"] == INDETERMINATE


def test_h2h3_floor_indeterminate_when_too_few_trades():
    out = h2h3_floor(zero_fraction=0.30, total_trades=199)
    assert out["eligible"] is False
    assert out["status"] == INDETERMINATE


def test_h2h3_floor_boundary_zero_fraction_half_is_under_floor():
    # zero_fraction < 0.50 strict; exactly 0.50 is NOT eligible.
    out = h2h3_floor(zero_fraction=0.50, total_trades=300)
    assert out["eligible"] is False


# ---------------------------------------------------------------------------
# position_series_from_trades: reconstruct a per-bar long/flat position series
# from the engine's (entry_time_utc, exit_time_utc) trade records over an index.
# Used to compute the H1 flat-exit-episode count + the H2/H3 zero_fraction over
# the TRAIN window without an explicit per-bar position channel from the engine.
# ---------------------------------------------------------------------------


def test_position_series_marks_long_inside_trade_interval():
    idx = pd.date_range("2020-01-01", periods=6, freq="h", tz="UTC")
    # one trade: long on bars [1, 3) -> positions 0 1 1 0 0 0.
    trades = [{"entry_time_utc": "2020-01-01T01:00:00Z",
               "exit_time_utc": "2020-01-01T03:00:00Z"}]
    pos = position_series_from_trades(idx, trades)
    assert list(pos) == [0, 1, 1, 0, 0, 0]


def test_position_series_back_to_back_trades_have_no_flat_gap():
    idx = pd.date_range("2020-01-01", periods=6, freq="h", tz="UTC")
    # trade A long [1,3), trade B long [3,5): bars 1..4 all long -> a SINGLE
    # long->flat transition at bar 5 (no flat bar between the two trades).
    trades = [
        {"entry_time_utc": "2020-01-01T01:00:00Z", "exit_time_utc": "2020-01-01T03:00:00Z"},
        {"entry_time_utc": "2020-01-01T03:00:00Z", "exit_time_utc": "2020-01-01T05:00:00Z"},
    ]
    pos = position_series_from_trades(idx, trades)
    assert list(pos) == [0, 1, 1, 1, 1, 0]
    assert count_flat_exit_episodes(pos) == 1  # only one defensive flat-exit


def test_position_series_empty_trades_all_flat():
    idx = pd.date_range("2020-01-01", periods=4, freq="h", tz="UTC")
    pos = position_series_from_trades(idx, [])
    assert list(pos) == [0, 0, 0, 0]


def test_zero_fraction_counts_flat_bars():
    pos = np.array([0, 1, 1, 0, 0, 0])  # 4 of 6 bars flat
    assert zero_fraction_from_positions(pos) == 4 / 6


def test_zero_fraction_empty_is_one():
    # No bars -> degenerate: treat as fully inactive (zero_fraction 1.0, under-floor).
    assert zero_fraction_from_positions(np.array([])) == 1.0

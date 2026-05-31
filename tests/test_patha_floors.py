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

from backtest.patha_orchestrator import (
    INDETERMINATE,
    count_flat_exit_episodes,
    h1_floor,
    h2h3_floor,
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

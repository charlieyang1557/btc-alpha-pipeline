# tests/test_pathc_floors.py
"""Task C7: hypothesis-class eligibility floors (LOCKed deterministic-θ rule).

Tests for:
  - resolve_theta: deterministic 0.90/0.85 fallback rule (LOCK Pre-reg 1).
  - h1_floor_eligible: episodes >= 200 at the FROZEN θ.
  - h2_derisk_occupancy_eligible: de-risk-cell occupancy >= 0.10 (B2 Finding 6).
  - H2/H3 state-class floor (zero_fraction + trade count) via h2h3_floor.

LOCK values frozen (never tune): 200, 0.90, 0.85, 0.50, 0.10.
"""
from __future__ import annotations

import pytest

from backtest.pathc_orchestrator import (
    h1_floor_eligible,
    h2_derisk_occupancy_eligible,
    h2h3_floor,
    resolve_theta,
)


# ---------------------------------------------------------------------------
# Task-spec required tests (verbatim from task brief)
# ---------------------------------------------------------------------------

def test_deterministic_theta_and_frozen_floor():
    """LOCK Pre-reg 1: fallback fires at < 200; default at >= 200."""
    assert resolve_theta(episodes_at_090=150) == 0.85
    assert resolve_theta(episodes_at_090=250) == 0.90
    assert h1_floor_eligible(episodes_at_frozen_theta=210) is True
    assert h1_floor_eligible(episodes_at_frozen_theta=180) is False


def test_h2_derisk_occupancy_floor():
    """B2 Finding 6: de-risk-cell occupancy >= 0.10 required for H2."""
    assert h2_derisk_occupancy_eligible(occupancy=0.20) is True
    assert h2_derisk_occupancy_eligible(occupancy=0.08) is False


# ---------------------------------------------------------------------------
# resolve_theta boundary cases
# ---------------------------------------------------------------------------

def test_resolve_theta_at_exact_boundary():
    """Floor boundary: exactly 200 episodes → default θ=0.90 (no fallback)."""
    assert resolve_theta(episodes_at_090=200) == 0.90


def test_resolve_theta_at_199_fires_fallback():
    """One below the boundary fires the fallback."""
    assert resolve_theta(episodes_at_090=199) == 0.85


def test_resolve_theta_at_zero_fires_fallback():
    """Degenerate: zero episodes fires fallback."""
    assert resolve_theta(episodes_at_090=0) == 0.85


# ---------------------------------------------------------------------------
# h1_floor_eligible boundary cases
# ---------------------------------------------------------------------------

def test_h1_floor_eligible_at_exact_boundary():
    """Exactly 200 episodes at frozen θ is eligible."""
    assert h1_floor_eligible(episodes_at_frozen_theta=200) is True


def test_h1_floor_eligible_at_199_is_ineligible():
    """199 episodes at frozen θ is INDETERMINATE (under-floor)."""
    assert h1_floor_eligible(episodes_at_frozen_theta=199) is False


def test_h1_floor_eligible_at_zero_is_ineligible():
    """Zero episodes is definitively ineligible."""
    assert h1_floor_eligible(episodes_at_frozen_theta=0) is False


# ---------------------------------------------------------------------------
# h2_derisk_occupancy_eligible boundary cases
# ---------------------------------------------------------------------------

def test_h2_derisk_occupancy_at_exact_boundary():
    """Exactly 0.10 occupancy is eligible."""
    assert h2_derisk_occupancy_eligible(occupancy=0.10) is True


def test_h2_derisk_occupancy_just_below_is_ineligible():
    """Just below 0.10 is ineligible."""
    assert h2_derisk_occupancy_eligible(occupancy=0.099) is False


def test_h2_derisk_occupancy_at_zero_is_ineligible():
    """Zero occupancy (no bars in de-risk cell) is ineligible."""
    assert h2_derisk_occupancy_eligible(occupancy=0.0) is False


# ---------------------------------------------------------------------------
# H2/H3 state-class floor (zero_fraction + trade count)
# ---------------------------------------------------------------------------

def test_h2h3_floor_eligible_both_conditions_met():
    """H2/H3 eligible when zero_fraction < 0.50 AND >= 200 trades."""
    result = h2h3_floor(zero_fraction=0.30, total_trades=250)
    assert result["eligible"] is True
    assert result["status"] == "ELIGIBLE"


def test_h2h3_floor_ineligible_zero_fraction_too_high():
    """H2/H3 INDETERMINATE when zero_fraction >= 0.50 (state-class floor)."""
    result = h2h3_floor(zero_fraction=0.62, total_trades=300)
    assert result["eligible"] is False
    assert result["status"] == "INDETERMINATE"


def test_h2h3_floor_ineligible_too_few_trades():
    """H2/H3 INDETERMINATE when trade count < 200."""
    result = h2h3_floor(zero_fraction=0.30, total_trades=150)
    assert result["eligible"] is False
    assert result["status"] == "INDETERMINATE"


def test_h2h3_floor_ineligible_both_conditions_fail():
    """H2/H3 INDETERMINATE when both conditions fail."""
    result = h2h3_floor(zero_fraction=0.67, total_trades=50)
    assert result["eligible"] is False


def test_h2h3_floor_at_zero_fraction_boundary():
    """zero_fraction exactly 0.50 is NOT eligible (strict <)."""
    result = h2h3_floor(zero_fraction=0.50, total_trades=300)
    assert result["eligible"] is False


def test_h2h3_floor_at_trade_count_boundary():
    """Exactly 200 trades with low zero_fraction is eligible."""
    result = h2h3_floor(zero_fraction=0.30, total_trades=200)
    assert result["eligible"] is True

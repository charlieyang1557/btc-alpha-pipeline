# tests/test_pathd_floors.py
"""Task C7: hypothesis-class eligibility floors (LOCKed deterministic-θ rule).

Tests for:
  - resolve_theta: deterministic 0.90/0.85 fallback rule (LOCK Pre-reg 1).
  - h1_floor_eligible: episodes >= 200 at the FROZEN θ.
  - h2_derisk_occupancy_eligible: de-risk-cell occupancy >= 0.10.
  - H2/H3 state-class floor (zero_fraction + trade count) via h2h3_floor.

LOCK values frozen (never tune): 200, 0.90, 0.85, 0.50, 0.10.

Adapted from tests/test_pathc_floors.py; retargeted to pathd_orchestrator.
"""
from __future__ import annotations

import pytest

from backtest.pathd_orchestrator import (
    h1_floor_eligible,
    h2_derisk_occupancy_eligible,
    h2h3_floor,
    resolve_theta,
)


# ---------------------------------------------------------------------------
# Task-spec required tests
# ---------------------------------------------------------------------------

def test_deterministic_theta_and_frozen_floor():
    """LOCK Pre-reg 1: fallback fires at < 200; default at >= 200."""
    assert resolve_theta(episodes_at_090=150) == 0.85
    assert resolve_theta(episodes_at_090=250) == 0.90
    assert h1_floor_eligible(episodes_at_frozen_theta=210) is True
    assert h1_floor_eligible(episodes_at_frozen_theta=180) is False


def test_h2_derisk_occupancy_floor():
    """de-risk-cell occupancy >= 0.10 required for H2."""
    assert h2_derisk_occupancy_eligible(occupancy=0.20) is True
    assert h2_derisk_occupancy_eligible(occupancy=0.08) is False


# ---------------------------------------------------------------------------
# resolve_theta boundary cases
# ---------------------------------------------------------------------------

def test_resolve_theta_returns_090_when_episodes_gte_200():
    assert resolve_theta(200) == 0.90
    assert resolve_theta(201) == 0.90
    assert resolve_theta(999) == 0.90


def test_resolve_theta_returns_085_when_episodes_lt_200():
    assert resolve_theta(0) == 0.85
    assert resolve_theta(150) == 0.85
    assert resolve_theta(199) == 0.85


def test_resolve_theta_at_exact_boundary():
    assert resolve_theta(episodes_at_090=200) == 0.90


def test_resolve_theta_at_199_fires_fallback():
    assert resolve_theta(episodes_at_090=199) == 0.85


def test_resolve_theta_at_zero_fires_fallback():
    assert resolve_theta(episodes_at_090=0) == 0.85


def test_resolve_theta_boundary_at_200():
    assert resolve_theta(200) == 0.90  # boundary: >=200 stays at 0.90
    assert resolve_theta(199) == 0.85  # just below: falls back


# ---------------------------------------------------------------------------
# h1_floor_eligible boundary cases
# ---------------------------------------------------------------------------

def test_h1_floor_eligible_at_exact_boundary():
    assert h1_floor_eligible(episodes_at_frozen_theta=200) is True


def test_h1_floor_eligible_at_199_is_ineligible():
    assert h1_floor_eligible(episodes_at_frozen_theta=199) is False


def test_h1_floor_eligible_at_zero_is_ineligible():
    assert h1_floor_eligible(episodes_at_frozen_theta=0) is False


# ---------------------------------------------------------------------------
# h2_derisk_occupancy_eligible boundary cases
# ---------------------------------------------------------------------------

def test_h2_derisk_occupancy_at_exact_boundary():
    assert h2_derisk_occupancy_eligible(occupancy=0.10) is True


def test_h2_derisk_occupancy_just_below_is_ineligible():
    assert h2_derisk_occupancy_eligible(occupancy=0.099) is False


def test_h2_derisk_occupancy_at_zero_is_ineligible():
    assert h2_derisk_occupancy_eligible(occupancy=0.0) is False


# ---------------------------------------------------------------------------
# H2/H3 state-class floor
# ---------------------------------------------------------------------------

def test_h2h3_floor_eligible_both_conditions_met():
    result = h2h3_floor(zero_fraction=0.30, total_trades=250)
    assert result["eligible"] is True
    assert result["status"] == "ELIGIBLE"


def test_h2h3_floor_ineligible_zero_fraction_too_high():
    result = h2h3_floor(zero_fraction=0.62, total_trades=300)
    assert result["eligible"] is False
    assert result["status"] == "INDETERMINATE"


def test_h2h3_floor_ineligible_too_few_trades():
    result = h2h3_floor(zero_fraction=0.30, total_trades=150)
    assert result["eligible"] is False
    assert result["status"] == "INDETERMINATE"


def test_h2h3_floor_ineligible_both_conditions_fail():
    result = h2h3_floor(zero_fraction=0.67, total_trades=50)
    assert result["eligible"] is False


def test_h2h3_floor_at_zero_fraction_boundary():
    result = h2h3_floor(zero_fraction=0.50, total_trades=300)
    assert result["eligible"] is False


def test_h2h3_floor_at_trade_count_boundary():
    result = h2h3_floor(zero_fraction=0.30, total_trades=200)
    assert result["eligible"] is True

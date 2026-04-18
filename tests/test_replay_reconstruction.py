"""Tests for agents/critic/replay.py — D7 replay reconstruction (D7 Stage 2a).

Covers:
    - reconstruct_prior_factor_sets() with no pending_backtest calls
    - reconstruct_prior_factor_sets() excludes non-pending_backtest
    - reconstruct_prior_factor_sets() deduplicates identical factor sets
    - reconstruct_prior_factor_sets() preserves first-seen order
    - reconstruct_prior_factor_sets() excludes empty factor sets
    - reconstruct_prior_factor_sets() respects up_to_position_exclusive
    - reconstruct_prior_hashes() collects hashes from pending_backtest only
    - reconstruct_prior_hashes() respects position boundary
"""

from __future__ import annotations

import pytest

from agents.critic.replay import (
    reconstruct_prior_factor_sets,
    reconstruct_prior_hashes,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _call(
    position: int,
    lifecycle_state: str = "pending_backtest",
    factors_used: list[str] | None = None,
    hypothesis_hash: str | None = None,
    theme: str = "momentum",
) -> dict:
    """Build a synthetic per-call record matching the Stage 2d summary format."""
    record: dict = {
        "position": position,
        "lifecycle_state": lifecycle_state,
        "factors_used": factors_used or [],
        "hypothesis_hash": hypothesis_hash,
        "theme": theme,
    }
    return record


# ---------------------------------------------------------------------------
# reconstruct_prior_factor_sets tests
# ---------------------------------------------------------------------------


def test_no_pending_backtest_calls_returns_empty():
    """With no pending_backtest calls, prior_factor_sets is empty."""
    calls = [
        _call(1, lifecycle_state="proposer_invalid_dsl"),
        _call(2, lifecycle_state="duplicate"),
    ]
    result = reconstruct_prior_factor_sets(calls, up_to_position_exclusive=3)
    assert result == ()


def test_excludes_non_pending_backtest():
    """Only pending_backtest records contribute factor sets."""
    calls = [
        _call(1, lifecycle_state="pending_backtest", factors_used=["rsi_14", "atr_14"]),
        _call(2, lifecycle_state="critic_rejected", factors_used=["sma_20", "sma_50"]),
        _call(3, lifecycle_state="pending_backtest", factors_used=["macd_hist"]),
    ]
    result = reconstruct_prior_factor_sets(calls, up_to_position_exclusive=4)
    assert len(result) == 2
    # Non-pending_backtest at position 2 is excluded.
    factor_names = [set(fs) for fs in result]
    assert {"rsi_14", "atr_14"} in factor_names
    assert {"macd_hist"} in factor_names
    assert {"sma_20", "sma_50"} not in factor_names


def test_deduplicates_identical_factor_sets():
    """Identical factor sets (same factors, different order) appear only once."""
    calls = [
        _call(1, factors_used=["rsi_14", "atr_14"]),
        _call(2, factors_used=["atr_14", "rsi_14"]),  # Same set, different order.
    ]
    result = reconstruct_prior_factor_sets(calls, up_to_position_exclusive=3)
    assert len(result) == 1
    assert result[0] == ("atr_14", "rsi_14")


def test_preserves_first_seen_order():
    """Distinct factor sets appear in first-seen order."""
    calls = [
        _call(1, factors_used=["macd_hist"]),
        _call(2, factors_used=["rsi_14", "atr_14"]),
        _call(3, factors_used=["sma_20"]),
    ]
    result = reconstruct_prior_factor_sets(calls, up_to_position_exclusive=4)
    assert len(result) == 3
    assert result[0] == ("macd_hist",)
    assert result[1] == ("atr_14", "rsi_14")
    assert result[2] == ("sma_20",)


def test_excludes_empty_factor_sets():
    """Calls with empty factor sets are excluded."""
    calls = [
        _call(1, factors_used=[]),
        _call(2, factors_used=["rsi_14"]),
        _call(3, factors_used=None),
    ]
    result = reconstruct_prior_factor_sets(calls, up_to_position_exclusive=4)
    assert len(result) == 1
    assert result[0] == ("rsi_14",)


def test_respects_up_to_position_exclusive():
    """Only calls at positions < up_to_position_exclusive contribute."""
    calls = [
        _call(1, factors_used=["rsi_14"]),
        _call(2, factors_used=["atr_14"]),
        _call(3, factors_used=["sma_20"]),
        _call(4, factors_used=["macd_hist"]),
    ]
    result = reconstruct_prior_factor_sets(calls, up_to_position_exclusive=3)
    assert len(result) == 2
    factor_names = [set(fs) for fs in result]
    assert {"rsi_14"} in factor_names
    assert {"atr_14"} in factor_names
    assert {"sma_20"} not in factor_names
    assert {"macd_hist"} not in factor_names


# ---------------------------------------------------------------------------
# reconstruct_prior_hashes tests
# ---------------------------------------------------------------------------


def test_prior_hashes_collects_pending_backtest_only():
    """Only pending_backtest calls contribute hashes."""
    calls = [
        _call(1, lifecycle_state="pending_backtest", hypothesis_hash="hash_a"),
        _call(2, lifecycle_state="duplicate", hypothesis_hash="hash_b"),
        _call(3, lifecycle_state="pending_backtest", hypothesis_hash="hash_c"),
    ]
    result = reconstruct_prior_hashes(calls, up_to_position_exclusive=4)
    assert result == ("hash_a", "hash_c")


def test_prior_hashes_respects_position_boundary():
    """Hashes at or after the boundary are excluded."""
    calls = [
        _call(1, hypothesis_hash="h1"),
        _call(2, hypothesis_hash="h2"),
        _call(3, hypothesis_hash="h3"),
    ]
    result = reconstruct_prior_hashes(calls, up_to_position_exclusive=2)
    assert result == ("h1",)

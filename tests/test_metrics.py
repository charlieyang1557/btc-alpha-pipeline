"""Tests for backtest/metrics.py.

Verifies:
- Sharpe ratio against hand calculation
- Max drawdown on known equity curves
- Max drawdown duration in hours
- Trade statistics (win rate, profit factor, avg return)
- Full metrics pipeline
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd
import pytest

from backtest.metrics import (
    compute_all_metrics,
    compute_max_drawdown,
    compute_max_drawdown_duration_hours,
    compute_sharpe_ratio,
    compute_trade_stats,
)


# ---------------------------------------------------------------------------
# Sharpe ratio
# ---------------------------------------------------------------------------


class TestSharpeRatio:
    """Verify Sharpe ratio computation against hand calculations."""

    def test_known_returns(self):
        """Verify against manual calculation.

        returns = [0.01, -0.005, 0.008, 0.003, -0.002]
        mean = 0.0028
        std(ddof=1) = 0.006099...
        annualized = 0.0028 / 0.006099 * sqrt(8766) = 42.96...

        Note: hourly returns annualized to 8766 periods.
        """
        returns = np.array([0.01, -0.005, 0.008, 0.003, -0.002])
        mean = np.mean(returns)
        std = np.std(returns, ddof=1)
        expected = mean / std * math.sqrt(8766)

        result = compute_sharpe_ratio(returns)
        assert result == pytest.approx(expected, rel=1e-6)

    def test_zero_returns(self):
        """All-zero returns → Sharpe = 0."""
        returns = np.zeros(100)
        assert compute_sharpe_ratio(returns) == 0.0

    def test_constant_positive_returns(self):
        """Constant positive returns → std=0 → Sharpe = 0 (avoid div by zero)."""
        returns = np.full(100, 0.001)
        assert compute_sharpe_ratio(returns) == 0.0

    def test_single_return(self):
        """Single return → insufficient data → Sharpe = 0."""
        assert compute_sharpe_ratio(np.array([0.05])) == 0.0

    def test_empty_returns(self):
        """Empty array → Sharpe = 0."""
        assert compute_sharpe_ratio(np.array([])) == 0.0

    def test_negative_sharpe(self):
        """Predominantly negative returns → negative Sharpe."""
        returns = np.array([-0.01, -0.02, 0.001, -0.015, -0.005])
        result = compute_sharpe_ratio(returns)
        assert result < 0


# ---------------------------------------------------------------------------
# Max drawdown
# ---------------------------------------------------------------------------


class TestMaxDrawdown:
    """Verify max drawdown computation."""

    def test_simple_drawdown(self):
        """Peak 100 → trough 80 = 20% drawdown."""
        equity = np.array([100, 110, 105, 80, 90, 100])
        dd = compute_max_drawdown(equity)
        # Peak = 110, trough = 80, drawdown = (110-80)/110 = 0.2727...
        assert dd == pytest.approx(30 / 110, rel=1e-6)

    def test_no_drawdown(self):
        """Monotonically increasing equity → 0 drawdown."""
        equity = np.array([100, 110, 120, 130, 140])
        assert compute_max_drawdown(equity) == pytest.approx(0.0)

    def test_full_loss(self):
        """Equity drops to near-zero."""
        equity = np.array([100, 50, 10, 1])
        dd = compute_max_drawdown(equity)
        # (100 - 1) / 100 = 0.99
        assert dd == pytest.approx(0.99, rel=1e-6)

    def test_single_value(self):
        """Single equity value → 0 drawdown."""
        assert compute_max_drawdown(np.array([100])) == 0.0


# ---------------------------------------------------------------------------
# Max drawdown duration
# ---------------------------------------------------------------------------


class TestMaxDrawdownDuration:
    """Verify max drawdown duration computation."""

    def test_known_duration(self):
        """3-hour drawdown period."""
        index = pd.date_range("2024-01-01", periods=6, freq="h")
        # Peak at bar 1, recovery at bar 4 (3 hours in drawdown)
        equity = pd.Series([100, 110, 105, 100, 110, 120], index=index)
        dur = compute_max_drawdown_duration_hours(equity)
        # Drawdown from bar 1 (110) to bar 3 (100), recovery at bar 4 (110)
        # Duration = bar 4 - bar 2 = 2 hours (bars 2 and 3 are in drawdown)
        assert dur == pytest.approx(2.0)

    def test_no_drawdown_duration(self):
        """No drawdown → 0 hours."""
        index = pd.date_range("2024-01-01", periods=5, freq="h")
        equity = pd.Series([100, 110, 120, 130, 140], index=index)
        assert compute_max_drawdown_duration_hours(equity) == 0.0

    def test_drawdown_to_end(self):
        """Drawdown that extends to end of series."""
        index = pd.date_range("2024-01-01", periods=6, freq="h")
        equity = pd.Series([100, 110, 105, 100, 95, 90], index=index)
        dur = compute_max_drawdown_duration_hours(equity)
        # Peak at bar 1 (110), drawdown starts at bar 2 (105)
        # Never recovers, last bar is bar 5
        # Duration = bar 5 - bar 2 = 3 hours
        assert dur == pytest.approx(3.0)


# ---------------------------------------------------------------------------
# Trade statistics
# ---------------------------------------------------------------------------


class TestTradeStats:
    """Verify trade-level statistics."""

    def _make_trades(self) -> list[dict]:
        """Create sample trades for testing."""
        return [
            {
                "pnl": 100.0,
                "pnl_pct": 0.01,
                "entry_time_utc": "2024-01-01T10:00:00Z",
                "exit_time_utc": "2024-01-02T10:00:00Z",
            },
            {
                "pnl": -50.0,
                "pnl_pct": -0.005,
                "entry_time_utc": "2024-01-03T10:00:00Z",
                "exit_time_utc": "2024-01-04T10:00:00Z",
            },
            {
                "pnl": 200.0,
                "pnl_pct": 0.02,
                "entry_time_utc": "2024-01-05T10:00:00Z",
                "exit_time_utc": "2024-01-07T10:00:00Z",
            },
        ]

    def test_total_trades(self):
        stats = compute_trade_stats(self._make_trades())
        assert stats["total_trades"] == 3

    def test_win_rate(self):
        stats = compute_trade_stats(self._make_trades())
        assert stats["win_rate"] == pytest.approx(2 / 3)

    def test_avg_trade_return(self):
        stats = compute_trade_stats(self._make_trades())
        expected = (0.01 + (-0.005) + 0.02) / 3
        assert stats["avg_trade_return"] == pytest.approx(expected)

    def test_profit_factor(self):
        stats = compute_trade_stats(self._make_trades())
        # Gross profit = 100 + 200 = 300, gross loss = 50
        assert stats["profit_factor"] == pytest.approx(300 / 50)

    def test_avg_duration(self):
        stats = compute_trade_stats(self._make_trades())
        # Trade 1: 24h, Trade 2: 24h, Trade 3: 48h → avg = 32h
        assert stats["avg_trade_duration_hours"] == pytest.approx(32.0)

    def test_empty_trades(self):
        stats = compute_trade_stats([])
        assert stats["total_trades"] == 0
        assert stats["win_rate"] == 0.0
        assert stats["profit_factor"] == 0.0

    def test_all_winners(self):
        trades = [
            {"pnl": 100, "pnl_pct": 0.01, "entry_time_utc": "2024-01-01T00:00:00Z", "exit_time_utc": "2024-01-02T00:00:00Z"},
            {"pnl": 200, "pnl_pct": 0.02, "entry_time_utc": "2024-01-03T00:00:00Z", "exit_time_utc": "2024-01-04T00:00:00Z"},
        ]
        stats = compute_trade_stats(trades)
        assert stats["win_rate"] == 1.0
        assert stats["profit_factor"] == float("inf")


# ---------------------------------------------------------------------------
# Full metrics pipeline
# ---------------------------------------------------------------------------


class TestComputeAllMetrics:
    """Verify compute_all_metrics integrates correctly."""

    def test_basic_pipeline(self):
        """Verify all expected keys are present."""
        index = pd.date_range("2024-01-01", periods=100, freq="h")
        equity = pd.Series(
            10000 + np.cumsum(np.random.default_rng(42).normal(0, 10, 100)),
            index=index,
        )
        trades = [
            {
                "pnl": 50.0,
                "pnl_pct": 0.005,
                "entry_time_utc": "2024-01-01T10:00:00Z",
                "exit_time_utc": "2024-01-02T10:00:00Z",
            },
        ]

        metrics = compute_all_metrics(equity, trades, initial_capital=10000.0)

        expected_keys = {
            "total_return", "sharpe_ratio", "max_drawdown",
            "max_drawdown_duration_hours", "initial_capital", "final_capital",
            "total_trades", "win_rate", "avg_trade_return",
            "avg_trade_duration_hours", "profit_factor",
        }
        assert expected_keys <= set(metrics.keys())
        assert metrics["total_trades"] == 1
        assert isinstance(metrics["sharpe_ratio"], float)
        assert isinstance(metrics["max_drawdown"], float)

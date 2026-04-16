"""Tests for additional baseline strategies (Deliverable 13).

Verifies:
- Volatility breakout and mean reversion run without error
- Both produce trades on the 2024 validation range
- Sharpe < 2.0 sanity check (high Sharpe → investigate for bugs)
- Both are found by engine auto-discovery
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from backtest.engine import (
    STRATEGY_REGISTRY,
    BacktestResult,
    _ensure_strategies_loaded,
    run_backtest,
)
from strategies.baseline.mean_reversion import MeanReversion
from strategies.baseline.volatility_breakout import VolatilityBreakout

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PARQUET_PATH = PROJECT_ROOT / "data" / "raw" / "btcusdt_1h.parquet"

# Skip if canonical data is missing
pytestmark = pytest.mark.skipif(
    not PARQUET_PATH.exists(),
    reason=f"Canonical parquet not found: {PARQUET_PATH}",
)

START_DATE = datetime(2024, 1, 1, tzinfo=timezone.utc)
END_DATE = datetime(2024, 6, 30, 23, 0, tzinfo=timezone.utc)


# ---------------------------------------------------------------------------
# Fixtures: one run per strategy, shared across module
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def volatility_result():
    """Run volatility breakout on 2024 H1 data."""
    return run_backtest(
        strategy_cls=VolatilityBreakout,
        start_date=START_DATE,
        end_date=END_DATE,
        parquet_path=PARQUET_PATH,
        write_registry=False,
    )


@pytest.fixture(scope="module")
def mean_reversion_result():
    """Run mean reversion on 2024 H1 data."""
    return run_backtest(
        strategy_cls=MeanReversion,
        start_date=START_DATE,
        end_date=END_DATE,
        parquet_path=PARQUET_PATH,
        write_registry=False,
    )


# ---------------------------------------------------------------------------
# Volatility breakout
# ---------------------------------------------------------------------------


class TestVolatilityBreakout:
    """Verify volatility breakout strategy runs correctly."""

    def test_runs_without_error(self, volatility_result):
        """Strategy must complete without raising."""
        assert isinstance(volatility_result, BacktestResult)
        assert volatility_result.strategy_name == "volatility_breakout"

    def test_produces_trades(self, volatility_result):
        """Must produce at least one trade on 2024 data."""
        assert len(volatility_result.trades) > 0, (
            "Volatility breakout produced 0 trades — check default parameters"
        )

    def test_sharpe_sanity(self, volatility_result):
        """Sharpe < 2.0 — high Sharpe on a naive strategy is suspicious."""
        sharpe = volatility_result.metrics["sharpe_ratio"]
        assert sharpe < 2.0, (
            f"Suspiciously high Sharpe ({sharpe:.3f}) for volatility breakout — "
            f"investigate for bugs"
        )

    def test_warmup_bars(self, volatility_result):
        """Warmup must equal bb_period (24)."""
        assert volatility_result.warmup_bars == 24

    def test_equity_curve_non_empty(self, volatility_result):
        """Equity curve must have data points."""
        assert len(volatility_result.equity_curve) > 0


# ---------------------------------------------------------------------------
# Mean reversion
# ---------------------------------------------------------------------------


class TestMeanReversion:
    """Verify mean reversion strategy runs correctly."""

    def test_runs_without_error(self, mean_reversion_result):
        """Strategy must complete without raising."""
        assert isinstance(mean_reversion_result, BacktestResult)
        assert mean_reversion_result.strategy_name == "mean_reversion"

    def test_produces_trades(self, mean_reversion_result):
        """Must produce at least one trade on 2024 data."""
        assert len(mean_reversion_result.trades) > 0, (
            "Mean reversion produced 0 trades — check default parameters"
        )

    def test_sharpe_sanity(self, mean_reversion_result):
        """Sharpe < 2.0 — high Sharpe on a naive strategy is suspicious."""
        sharpe = mean_reversion_result.metrics["sharpe_ratio"]
        assert sharpe < 2.0, (
            f"Suspiciously high Sharpe ({sharpe:.3f}) for mean reversion — "
            f"investigate for bugs"
        )

    def test_warmup_bars(self, mean_reversion_result):
        """Warmup must equal zscore_period (48)."""
        assert mean_reversion_result.warmup_bars == 48

    def test_equity_curve_non_empty(self, mean_reversion_result):
        """Equity curve must have data points."""
        assert len(mean_reversion_result.equity_curve) > 0


# ---------------------------------------------------------------------------
# Auto-discovery
# ---------------------------------------------------------------------------


class TestAutoDiscovery:
    """Verify both strategies are found by engine auto-discovery."""

    @pytest.fixture(autouse=True)
    def _load_strategies(self):
        """Ensure strategies are loaded."""
        _ensure_strategies_loaded()

    def test_volatility_breakout_registered(self):
        """volatility_breakout must be in STRATEGY_REGISTRY."""
        assert "volatility_breakout" in STRATEGY_REGISTRY
        assert STRATEGY_REGISTRY["volatility_breakout"] is VolatilityBreakout

    def test_mean_reversion_registered(self):
        """mean_reversion must be in STRATEGY_REGISTRY."""
        assert "mean_reversion" in STRATEGY_REGISTRY
        assert STRATEGY_REGISTRY["mean_reversion"] is MeanReversion

    def test_all_four_baselines_registered(self):
        """All 4 baseline strategies must be discoverable."""
        expected = {"sma_crossover", "momentum", "volatility_breakout", "mean_reversion"}
        assert expected <= set(STRATEGY_REGISTRY.keys())

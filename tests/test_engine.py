"""Tests for backtest/engine.py.

Verifies:
- Single-run engine produces correct results
- Trade time semantics (signal time vs fill time)
- Warmup handling (no trades during warmup, effective_start)
- Trade CSV output
- Registry integration
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import backtrader as bt
import numpy as np
import pandas as pd
import pytest

from backtest.engine import (
    BacktestResult,
    EquityCurveCollector,
    TradeCollector,
    run_backtest,
)
from strategies.template import BaseStrategy


# ---------------------------------------------------------------------------
# Test strategies
# ---------------------------------------------------------------------------


class _BuyOnBar5(BaseStrategy):
    """Buy on bar 5, sell on bar 15. Simple for testing."""

    STRATEGY_NAME = "test_buy_bar5"
    WARMUP_BARS = 0

    params = (
        ("buy_bar", 5),
        ("sell_bar", 15),
    )

    def __init__(self):
        self.bar_idx = 0

    def next(self):
        if self.bar_idx == self.p.buy_bar and not self.position:
            self.buy()
        elif self.bar_idx == self.p.sell_bar and self.position:
            self.close()
        self.bar_idx += 1


class _WarmupStrategy(BaseStrategy):
    """Strategy with warmup period for testing warmup enforcement.

    Uses a 10-period SMA so next() isn't called until bar 10.
    Buys on bar 12 (2 bars after warmup) to verify no early trades.
    """

    STRATEGY_NAME = "test_warmup"
    WARMUP_BARS = 10

    def __init__(self):
        self.sma = bt.indicators.SMA(self.data.close, period=10)
        self.bar_idx = 0
        self._next_called_bars = []

    def next(self):
        self._next_called_bars.append(self.bar_idx)
        if self.bar_idx == 2 and not self.position:
            self.buy()
        elif self.bar_idx == 8 and self.position:
            self.close()
        self.bar_idx += 1


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_test_parquet(
    tmp_path: Path,
    n_hours: int = 30,
    start: str = "2024-01-01",
    volumes: list[float] | None = None,
) -> Path:
    """Create a synthetic parquet file with deterministic prices."""
    timestamps = pd.date_range(start=start, periods=n_hours, freq="h", tz="UTC")
    vols = volumes if volumes else [1000.0] * n_hours

    df = pd.DataFrame({
        "open_time_utc": timestamps.astype("datetime64[ms, UTC]"),
        "open": [100.0 + i for i in range(n_hours)],
        "high": [110.0 + i for i in range(n_hours)],
        "low": [90.0 + i for i in range(n_hours)],
        "close": [105.0 + i for i in range(n_hours)],
        "volume": vols,
        "quote_volume": [100_000.0] * n_hours,
        "trade_count": np.arange(5000, 5000 + n_hours, dtype="int64"),
        "ingested_at_utc": pd.Timestamp.now(tz="UTC").floor("ms"),
        "source": pd.array(["binance_vision"] * n_hours, dtype="string"),
    })
    df["ingested_at_utc"] = df["ingested_at_utc"].astype("datetime64[ms, UTC]")

    path = tmp_path / "test.parquet"
    df.to_parquet(path, engine="pyarrow", index=False)
    return path


# ---------------------------------------------------------------------------
# Tests: Basic engine functionality
# ---------------------------------------------------------------------------


class TestEngineBasic:
    """Test basic engine run and result structure."""

    def test_returns_backtest_result(self, tmp_path):
        """Engine returns a BacktestResult object."""
        path = _make_test_parquet(tmp_path, n_hours=30)
        result = run_backtest(
            strategy_cls=_BuyOnBar5,
            start_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
            end_date=datetime(2024, 1, 2, 5, 0, tzinfo=timezone.utc),
            parquet_path=path,
            write_registry=False,
        )
        assert isinstance(result, BacktestResult)
        assert result.run_id is not None
        assert result.strategy_name == "test_buy_bar5"

    def test_produces_trades(self, tmp_path):
        """Engine should produce at least one trade."""
        path = _make_test_parquet(tmp_path, n_hours=30)
        result = run_backtest(
            strategy_cls=_BuyOnBar5,
            start_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
            end_date=datetime(2024, 1, 2, 5, 0, tzinfo=timezone.utc),
            parquet_path=path,
            write_registry=False,
        )
        assert len(result.trades) == 1

    def test_equity_curve_non_empty(self, tmp_path):
        """Equity curve should have data points."""
        path = _make_test_parquet(tmp_path, n_hours=30)
        result = run_backtest(
            strategy_cls=_BuyOnBar5,
            start_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
            end_date=datetime(2024, 1, 2, 5, 0, tzinfo=timezone.utc),
            parquet_path=path,
            write_registry=False,
        )
        assert len(result.equity_curve) == 30

    def test_metrics_populated(self, tmp_path):
        """Metrics dict should have all expected keys."""
        path = _make_test_parquet(tmp_path, n_hours=30)
        result = run_backtest(
            strategy_cls=_BuyOnBar5,
            start_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
            end_date=datetime(2024, 1, 2, 5, 0, tzinfo=timezone.utc),
            parquet_path=path,
            write_registry=False,
        )
        expected_keys = {
            "total_return", "sharpe_ratio", "max_drawdown",
            "total_trades", "win_rate", "profit_factor",
        }
        assert expected_keys <= set(result.metrics.keys())


# ---------------------------------------------------------------------------
# Tests: Trade time semantics (CRITICAL)
# ---------------------------------------------------------------------------


class TestTradeTimeSemantics:
    """Verify trade signal/fill time semantics are correct.

    This is the most critical test class. The user specifically flagged:
    - entry_signal_time_utc = bar N close time (when signal was computed)
    - entry_time_utc = bar N+1 open time (actual fill)
    """

    def test_entry_signal_vs_fill_time(self, tmp_path):
        """entry_signal_time must be 1 bar before entry_time."""
        path = _make_test_parquet(tmp_path, n_hours=30)
        result = run_backtest(
            strategy_cls=_BuyOnBar5,
            start_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
            end_date=datetime(2024, 1, 2, 5, 0, tzinfo=timezone.utc),
            parquet_path=path,
            write_registry=False,
        )

        trade = result.trades[0]
        signal_dt = pd.Timestamp(trade["entry_signal_time_utc"])
        fill_dt = pd.Timestamp(trade["entry_time_utc"])

        # Signal on bar 5 → fill on bar 6
        # Signal time should be bar 5's datetime
        # Fill time should be bar 6's datetime (1 hour later)
        assert fill_dt - signal_dt == pd.Timedelta(hours=1)

    def test_entry_fill_price_matches_next_bar_open(self, tmp_path):
        """entry_price must equal the fill bar's open price."""
        path = _make_test_parquet(tmp_path, n_hours=30)
        result = run_backtest(
            strategy_cls=_BuyOnBar5,
            start_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
            end_date=datetime(2024, 1, 2, 5, 0, tzinfo=timezone.utc),
            parquet_path=path,
            write_registry=False,
        )

        trade = result.trades[0]
        # Buy on bar 5 → fill at bar 6 open = 100 + 6 = 106.0
        assert trade["entry_price"] == pytest.approx(106.0)

    def test_exit_signal_vs_fill_time(self, tmp_path):
        """exit_signal_time must be 1 bar before exit_time."""
        path = _make_test_parquet(tmp_path, n_hours=30)
        result = run_backtest(
            strategy_cls=_BuyOnBar5,
            start_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
            end_date=datetime(2024, 1, 2, 5, 0, tzinfo=timezone.utc),
            parquet_path=path,
            write_registry=False,
        )

        trade = result.trades[0]
        signal_dt = pd.Timestamp(trade["exit_signal_time_utc"])
        fill_dt = pd.Timestamp(trade["exit_time_utc"])

        assert fill_dt - signal_dt == pd.Timedelta(hours=1)

    def test_exit_fill_price_matches_next_bar_open(self, tmp_path):
        """exit_price must equal the fill bar's open price."""
        path = _make_test_parquet(tmp_path, n_hours=30)
        result = run_backtest(
            strategy_cls=_BuyOnBar5,
            start_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
            end_date=datetime(2024, 1, 2, 5, 0, tzinfo=timezone.utc),
            parquet_path=path,
            write_registry=False,
        )

        trade = result.trades[0]
        # Sell on bar 15 → fill at bar 16 open = 100 + 16 = 116.0
        assert trade["exit_price"] == pytest.approx(116.0)

    def test_signal_time_is_not_fill_time(self, tmp_path):
        """Signal time and fill time must be different (no same-bar execution)."""
        path = _make_test_parquet(tmp_path, n_hours=30)
        result = run_backtest(
            strategy_cls=_BuyOnBar5,
            start_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
            end_date=datetime(2024, 1, 2, 5, 0, tzinfo=timezone.utc),
            parquet_path=path,
            write_registry=False,
        )

        trade = result.trades[0]
        assert trade["entry_signal_time_utc"] != trade["entry_time_utc"]
        assert trade["exit_signal_time_utc"] != trade["exit_time_utc"]


# ---------------------------------------------------------------------------
# Tests: Trade CSV output
# ---------------------------------------------------------------------------


class TestTradeCSV:
    """Verify trade CSV is saved correctly."""

    def test_csv_created(self, tmp_path):
        """Trade CSV should be created when trades exist."""
        path = _make_test_parquet(tmp_path, n_hours=30)
        result = run_backtest(
            strategy_cls=_BuyOnBar5,
            start_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
            end_date=datetime(2024, 1, 2, 5, 0, tzinfo=timezone.utc),
            parquet_path=path,
            write_registry=False,
        )
        assert result.trade_csv_path is not None
        assert result.trade_csv_path.exists()

    def test_csv_columns(self, tmp_path):
        """Trade CSV must contain all required columns."""
        path = _make_test_parquet(tmp_path, n_hours=30)
        result = run_backtest(
            strategy_cls=_BuyOnBar5,
            start_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
            end_date=datetime(2024, 1, 2, 5, 0, tzinfo=timezone.utc),
            parquet_path=path,
            write_registry=False,
        )

        df = pd.read_csv(result.trade_csv_path)
        expected_cols = {
            "trade_id", "entry_signal_time_utc", "entry_time_utc",
            "entry_price", "entry_bar_volume", "exit_signal_time_utc",
            "exit_time_utc", "exit_price", "exit_bar_volume",
            "size", "entry_commission", "exit_commission",
            "total_commission", "pnl", "pnl_pct",
        }
        assert expected_cols <= set(df.columns)

    def test_csv_row_count(self, tmp_path):
        """CSV row count must match trade count."""
        path = _make_test_parquet(tmp_path, n_hours=30)
        result = run_backtest(
            strategy_cls=_BuyOnBar5,
            start_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
            end_date=datetime(2024, 1, 2, 5, 0, tzinfo=timezone.utc),
            parquet_path=path,
            write_registry=False,
        )

        df = pd.read_csv(result.trade_csv_path)
        assert len(df) == len(result.trades)


# ---------------------------------------------------------------------------
# Tests: Warmup handling
# ---------------------------------------------------------------------------


class TestWarmupHandling:
    """Verify warmup period is correctly enforced."""

    def test_effective_start_after_warmup(self, tmp_path):
        """effective_start should be after warmup bars."""
        path = _make_test_parquet(tmp_path, n_hours=30)
        result = run_backtest(
            strategy_cls=_WarmupStrategy,
            start_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
            end_date=datetime(2024, 1, 2, 5, 0, tzinfo=timezone.utc),
            parquet_path=path,
            write_registry=False,
        )

        # 10-bar warmup on hourly data starting 2024-01-01 00:00
        # First next() call at bar index 9 (0-based) = 2024-01-01 09:00
        # But equity curve starts recording from first next() call
        assert result.effective_start is not None
        assert result.warmup_bars == 10

        # Equity curve should have fewer bars than total data
        assert len(result.equity_curve) < 30

    def test_equity_curve_excludes_warmup(self, tmp_path):
        """Equity curve should only cover post-warmup bars."""
        path = _make_test_parquet(tmp_path, n_hours=30)
        result = run_backtest(
            strategy_cls=_WarmupStrategy,
            start_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
            end_date=datetime(2024, 1, 2, 5, 0, tzinfo=timezone.utc),
            parquet_path=path,
            write_registry=False,
        )

        # 30 bars - 9 warmup bars (SMA(10) starts at bar 9) = 21 bars
        # (Backtrader SMA needs period bars, so first value at bar period-1)
        assert len(result.equity_curve) == 30 - 9


# ---------------------------------------------------------------------------
# Tests: Registry integration
# ---------------------------------------------------------------------------


class TestRegistryIntegration:
    """Verify engine writes to experiment registry correctly."""

    def test_registry_write(self, tmp_path):
        """Run should be written to experiments.db."""
        import sqlite3

        db_path = tmp_path / "test_experiments.db"
        path = _make_test_parquet(tmp_path, n_hours=30)

        result = run_backtest(
            strategy_cls=_BuyOnBar5,
            start_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
            end_date=datetime(2024, 1, 2, 5, 0, tzinfo=timezone.utc),
            parquet_path=path,
            write_registry=True,
            db_path=db_path,
        )

        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(
            "SELECT * FROM runs WHERE run_id = ?", (result.run_id,)
        )
        row = dict(cursor.fetchone())
        conn.close()

        assert row["run_type"] == "single_run"
        assert row["strategy_name"] == "test_buy_bar5"
        assert row["fee_model"] == "effective_7bps_per_side"
        assert row["total_trades"] == 1
        assert row["warmup_bars"] == 0
        assert row["train_start"] is None
        assert row["validation_start"] is None

    def test_no_registry_write_when_disabled(self, tmp_path):
        """Registry should not be written when disabled."""
        db_path = tmp_path / "test_experiments.db"
        path = _make_test_parquet(tmp_path, n_hours=30)

        run_backtest(
            strategy_cls=_BuyOnBar5,
            start_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
            end_date=datetime(2024, 1, 2, 5, 0, tzinfo=timezone.utc),
            parquet_path=path,
            write_registry=False,
            db_path=db_path,
        )

        assert not db_path.exists()

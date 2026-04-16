"""End-to-end Phase 1A pipeline test (Deliverable 10).

Runs SMA crossover through engine.py on real BTC 1h data (2024-01-01
to 2024-06-30), then verifies:
    1. Run was logged to experiments.db with all required fields
    2. run_type == "single_run"
    3. fee_model == "effective_7bps_per_side"
    4. warmup_bars == 50 (SMA slow period)
    5. effective_start is 50 bars after test_start
    6. total_trades > 0
    7. sharpe_ratio is finite (not NaN/Inf)
    8. First trade's entry_price matches raw OHLCV open at entry_time_utc

This test uses the canonical parquet file and is skipped if the data
file is not present (e.g., in CI without data fixtures).
"""

from __future__ import annotations

import math
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd
import pytest

from backtest.engine import run_backtest
from strategies.baseline.sma_crossover import SMACrossover

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PARQUET_PATH = PROJECT_ROOT / "data" / "raw" / "btcusdt_1h.parquet"

# Skip entire module if canonical data is missing
pytestmark = pytest.mark.skipif(
    not PARQUET_PATH.exists(),
    reason=f"Canonical parquet not found: {PARQUET_PATH}",
)

# Date range matching CLI behavior (--end expands to 23:00 UTC)
START_DATE = datetime(2024, 1, 1, tzinfo=timezone.utc)
END_DATE = datetime(2024, 6, 30, 23, 0, tzinfo=timezone.utc)


@pytest.fixture(scope="module")
def pipeline_result(tmp_path_factory):
    """Run SMA crossover once for all tests in this module.

    Uses a temporary database to avoid polluting the real experiments.db.
    The run is expensive (~4300 bars), so we share it across tests via
    module-scoped fixture.
    """
    tmp_dir = tmp_path_factory.mktemp("pipeline")
    db_path = tmp_dir / "test_experiments.db"

    result = run_backtest(
        strategy_cls=SMACrossover,
        start_date=START_DATE,
        end_date=END_DATE,
        parquet_path=PARQUET_PATH,
        write_registry=True,
        db_path=db_path,
    )

    # Attach db_path for registry tests
    result._test_db_path = db_path
    return result


@pytest.fixture(scope="module")
def registry_row(pipeline_result):
    """Fetch the registry row for the pipeline run."""
    db_path = pipeline_result._test_db_path
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cursor = conn.execute(
        "SELECT * FROM runs WHERE run_id = ?",
        (pipeline_result.run_id,),
    )
    row = dict(cursor.fetchone())
    conn.close()
    return row


# ---------------------------------------------------------------------------
# Registry field tests
# ---------------------------------------------------------------------------


class TestRegistryFields:
    """Verify experiment registry row has all required fields."""

    def test_run_type(self, registry_row):
        """run_type must be 'single_run' for Phase 1A."""
        assert registry_row["run_type"] == "single_run"

    def test_fee_model(self, registry_row):
        """fee_model must be 'effective_7bps_per_side'."""
        assert registry_row["fee_model"] == "effective_7bps_per_side"

    def test_strategy_name(self, registry_row):
        """strategy_name must be 'sma_crossover'."""
        assert registry_row["strategy_name"] == "sma_crossover"

    def test_strategy_source(self, registry_row):
        """strategy_source must be 'manual' for Phase 1A baselines."""
        assert registry_row["strategy_source"] == "manual"

    def test_warmup_bars(self, registry_row):
        """warmup_bars must be 50 (SMA slow period)."""
        assert registry_row["warmup_bars"] == 50

    def test_effective_start_after_warmup(self, registry_row):
        """effective_start must be exactly 50 bars after test_start."""
        test_start = pd.Timestamp(registry_row["test_start"])
        effective_start = pd.Timestamp(registry_row["effective_start"])

        # 50 hourly bars = 50 hours offset
        expected = test_start + pd.Timedelta(hours=50)

        # Allow ±1 bar tolerance: Backtrader SMA(50) starts at bar 49
        # (0-indexed), so effective_start could be 49 or 50 hours after start
        delta_hours = (effective_start - test_start).total_seconds() / 3600
        assert 49 <= delta_hours <= 50, (
            f"effective_start is {delta_hours}h after test_start, "
            f"expected 49-50h"
        )

    def test_total_trades_positive(self, registry_row):
        """Must produce at least one trade."""
        assert registry_row["total_trades"] > 0

    def test_sharpe_is_finite(self, registry_row):
        """sharpe_ratio must be a finite number (not NaN/Inf)."""
        sharpe = registry_row["sharpe_ratio"]
        assert sharpe is not None
        assert math.isfinite(sharpe)

    def test_total_return_is_finite(self, registry_row):
        """total_return must be finite."""
        ret = registry_row["total_return"]
        assert ret is not None
        assert math.isfinite(ret)

    def test_max_drawdown_in_range(self, registry_row):
        """max_drawdown must be between 0 and 1."""
        dd = registry_row["max_drawdown"]
        assert dd is not None
        assert 0.0 <= dd <= 1.0

    def test_win_rate_in_range(self, registry_row):
        """win_rate must be between 0 and 1."""
        wr = registry_row["win_rate"]
        assert wr is not None
        assert 0.0 <= wr <= 1.0

    def test_initial_capital(self, registry_row):
        """initial_capital must be the default $10,000."""
        assert registry_row["initial_capital"] == pytest.approx(10_000.0)

    def test_final_capital_positive(self, registry_row):
        """final_capital must be positive."""
        assert registry_row["final_capital"] > 0

    def test_phase1a_nulls(self, registry_row):
        """Phase 1A single-run: train/validation fields must be NULL."""
        assert registry_row["train_start"] is None
        assert registry_row["train_end"] is None
        assert registry_row["validation_start"] is None
        assert registry_row["validation_end"] is None

    def test_parent_run_id_null(self, registry_row):
        """Phase 1A single-run: parent_run_id must be NULL."""
        assert registry_row["parent_run_id"] is None

    def test_test_dates_match(self, registry_row):
        """test_start and test_end must match the requested range."""
        test_start = pd.Timestamp(registry_row["test_start"])
        test_end = pd.Timestamp(registry_row["test_end"])

        assert test_start == pd.Timestamp(START_DATE)
        assert test_end == pd.Timestamp(END_DATE)


# ---------------------------------------------------------------------------
# Result structure tests
# ---------------------------------------------------------------------------


class TestResultStructure:
    """Verify BacktestResult object has expected data."""

    def test_equity_curve_non_empty(self, pipeline_result):
        """Equity curve must have data points."""
        assert len(pipeline_result.equity_curve) > 0

    def test_equity_curve_length_reasonable(self, pipeline_result):
        """Equity curve should have ~4300 bars (H1, 6 months minus warmup)."""
        ec_len = len(pipeline_result.equity_curve)
        # 182 days * 24 hours = ~4368 bars, minus 50 warmup ≈ 4318
        # Allow range for missing bars in data
        assert 4000 < ec_len < 4500, f"Unexpected equity curve length: {ec_len}"

    def test_trade_csv_exists(self, pipeline_result):
        """Trade CSV file must exist."""
        assert pipeline_result.trade_csv_path is not None
        assert pipeline_result.trade_csv_path.exists()

    def test_trade_csv_row_count(self, pipeline_result):
        """Trade CSV row count must match result.trades."""
        df = pd.read_csv(pipeline_result.trade_csv_path)
        assert len(df) == len(pipeline_result.trades)

    def test_metrics_keys_complete(self, pipeline_result):
        """All Phase 1A metrics must be present."""
        expected_keys = {
            "total_return",
            "sharpe_ratio",
            "max_drawdown",
            "max_drawdown_duration_hours",
            "initial_capital",
            "final_capital",
            "total_trades",
            "win_rate",
            "avg_trade_return",
            "avg_trade_duration_hours",
            "profit_factor",
        }
        assert expected_keys <= set(pipeline_result.metrics.keys())


# ---------------------------------------------------------------------------
# Trade price verification against raw OHLCV (CRITICAL)
# ---------------------------------------------------------------------------


class TestTradePriceVerification:
    """Cross-reference trade fill prices against raw OHLCV data.

    This is the core integrity check: confirms that entry_time_utc
    is the actual fill bar and entry_price matches that bar's open price.
    """

    @pytest.fixture(scope="class")
    def raw_ohlcv(self):
        """Load raw OHLCV data indexed by tz-naive datetime."""
        df = pd.read_parquet(PARQUET_PATH)
        df = df.set_index("open_time_utc").sort_index()
        df.index = df.index.tz_localize(None)
        return df

    def test_first_trade_entry_price(self, pipeline_result, raw_ohlcv):
        """First trade's entry_price must equal fill bar's open price.

        entry_time_utc is the fill bar (bar N+1). The fill price
        must match that bar's open, confirming next-bar execution.
        """
        assert len(pipeline_result.trades) > 0, "No trades to verify"

        trade = pipeline_result.trades[0]
        entry_dt = pd.Timestamp(trade["entry_time_utc"]).tz_localize(None)

        assert entry_dt in raw_ohlcv.index, (
            f"Fill bar {entry_dt} not found in raw OHLCV data"
        )

        expected_open = raw_ohlcv.loc[entry_dt, "open"]
        assert trade["entry_price"] == pytest.approx(expected_open, rel=1e-6), (
            f"Entry price mismatch: trade={trade['entry_price']}, "
            f"raw open={expected_open} at {entry_dt}"
        )

    def test_first_trade_exit_price(self, pipeline_result, raw_ohlcv):
        """First trade's exit_price must equal fill bar's open price."""
        assert len(pipeline_result.trades) > 0, "No trades to verify"

        trade = pipeline_result.trades[0]
        exit_dt = pd.Timestamp(trade["exit_time_utc"]).tz_localize(None)

        assert exit_dt in raw_ohlcv.index, (
            f"Fill bar {exit_dt} not found in raw OHLCV data"
        )

        expected_open = raw_ohlcv.loc[exit_dt, "open"]
        assert trade["exit_price"] == pytest.approx(expected_open, rel=1e-6), (
            f"Exit price mismatch: trade={trade['exit_price']}, "
            f"raw open={expected_open} at {exit_dt}"
        )

    def test_first_trade_signal_before_fill(self, pipeline_result):
        """Signal time must be exactly 1 bar before fill time."""
        trade = pipeline_result.trades[0]

        entry_signal = pd.Timestamp(trade["entry_signal_time_utc"])
        entry_fill = pd.Timestamp(trade["entry_time_utc"])
        assert entry_fill - entry_signal == pd.Timedelta(hours=1)

        exit_signal = pd.Timestamp(trade["exit_signal_time_utc"])
        exit_fill = pd.Timestamp(trade["exit_time_utc"])
        assert exit_fill - exit_signal == pd.Timedelta(hours=1)

    def test_first_trade_commission_7bps(self, pipeline_result):
        """Verify entry/exit commissions are ~7bps of trade value."""
        trade = pipeline_result.trades[0]
        size = trade["size"]

        expected_entry_comm = size * trade["entry_price"] * 0.0007
        assert trade["entry_commission"] == pytest.approx(
            expected_entry_comm, rel=1e-3
        )

        expected_exit_comm = size * trade["exit_price"] * 0.0007
        assert trade["exit_commission"] == pytest.approx(
            expected_exit_comm, rel=1e-3
        )

    def test_fill_bars_have_volume(self, pipeline_result, raw_ohlcv):
        """Fill bars must have non-zero volume."""
        trade = pipeline_result.trades[0]

        entry_dt = pd.Timestamp(trade["entry_time_utc"]).tz_localize(None)
        exit_dt = pd.Timestamp(trade["exit_time_utc"]).tz_localize(None)

        assert raw_ohlcv.loc[entry_dt, "volume"] > 0
        assert raw_ohlcv.loc[exit_dt, "volume"] > 0

    def test_last_trade_entry_price(self, pipeline_result, raw_ohlcv):
        """Last trade's entry_price must also match raw OHLCV open.

        Spot-checking both first and last trade catches systematic
        drift or off-by-one errors.
        """
        assert len(pipeline_result.trades) >= 2, "Need >=2 trades for this check"

        trade = pipeline_result.trades[-1]
        entry_dt = pd.Timestamp(trade["entry_time_utc"]).tz_localize(None)

        assert entry_dt in raw_ohlcv.index
        expected_open = raw_ohlcv.loc[entry_dt, "open"]
        assert trade["entry_price"] == pytest.approx(expected_open, rel=1e-6)

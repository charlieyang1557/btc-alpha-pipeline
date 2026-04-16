"""Tests for walk-forward mode (Phase 1B, Deliverable 11).

Verifies:
- Window generation produces correct date tuples
- Walk-forward run completes without error
- Registry has N walk_forward_window rows + 1 walk_forward_summary row
- All window rows share parent_run_id matching summary's run_id
- Summary row has non-NULL aggregate metrics
- Single-run mode still works unchanged (backward compatibility)
"""

from __future__ import annotations

import math
import sqlite3
from datetime import date, datetime, timezone
from pathlib import Path

import pytest

from backtest.engine import (
    BacktestResult,
    WalkForwardResult,
    generate_walk_forward_windows,
    run_backtest,
    run_walk_forward,
)
from strategies.baseline.sma_crossover import SMACrossover

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PARQUET_PATH = PROJECT_ROOT / "data" / "raw" / "btcusdt_1h.parquet"


# ---------------------------------------------------------------------------
# Window generation (unit tests — no backtest needed)
# ---------------------------------------------------------------------------


class TestGenerateWindows:
    """Verify walk-forward window generation logic."""

    def test_basic_windows(self):
        """12m train, 3m test, 3m step over 2 years → correct count."""
        windows = generate_walk_forward_windows(
            overall_start=date(2020, 1, 1),
            overall_end=date(2021, 12, 31),
            train_months=12,
            test_months=3,
            step_months=3,
        )
        # Train 2020-01 to 2020-12, Test 2021-01 to 2021-03 → fits
        # Train 2020-04 to 2021-03, Test 2021-04 to 2021-06 → fits
        # Train 2020-07 to 2021-06, Test 2021-07 to 2021-09 → fits
        # Train 2020-10 to 2021-09, Test 2021-10 to 2021-12 → fits
        # Train 2021-01 to 2021-12, Test 2022-01 to 2022-03 → exceeds
        assert len(windows) == 4

    def test_first_window_dates(self):
        """First window has correct train/test boundaries."""
        windows = generate_walk_forward_windows(
            overall_start=date(2020, 1, 1),
            overall_end=date(2021, 12, 31),
            train_months=12,
            test_months=3,
            step_months=3,
        )
        train_start, train_end, test_start, test_end = windows[0]
        assert train_start == date(2020, 1, 1)
        assert train_end == date(2020, 12, 31)
        assert test_start == date(2021, 1, 1)
        assert test_end == date(2021, 3, 31)

    def test_second_window_dates(self):
        """Second window shifts by step_months."""
        windows = generate_walk_forward_windows(
            overall_start=date(2020, 1, 1),
            overall_end=date(2021, 12, 31),
            train_months=12,
            test_months=3,
            step_months=3,
        )
        train_start, train_end, test_start, test_end = windows[1]
        assert train_start == date(2020, 4, 1)
        assert train_end == date(2021, 3, 31)
        assert test_start == date(2021, 4, 1)
        assert test_end == date(2021, 6, 30)

    def test_no_windows_if_range_too_short(self):
        """Date range shorter than train+test → empty list."""
        windows = generate_walk_forward_windows(
            overall_start=date(2024, 1, 1),
            overall_end=date(2024, 6, 30),
            train_months=12,
            test_months=3,
            step_months=3,
        )
        assert windows == []

    def test_short_windows(self):
        """2m train, 1m test, 1m step over 9 months → many windows."""
        windows = generate_walk_forward_windows(
            overall_start=date(2024, 1, 1),
            overall_end=date(2024, 9, 30),
            train_months=2,
            test_months=1,
            step_months=1,
        )
        # W1: T 01-02, test 03
        # W2: T 02-03, test 04
        # W3: T 03-04, test 05
        # W4: T 04-05, test 06
        # W5: T 05-06, test 07
        # W6: T 06-07, test 08
        # W7: T 07-08, test 09
        assert len(windows) == 7

    def test_test_end_equals_last_day_of_month(self):
        """test_end should be the last day of the test month."""
        windows = generate_walk_forward_windows(
            overall_start=date(2024, 1, 1),
            overall_end=date(2024, 12, 31),
            train_months=3,
            test_months=1,
            step_months=1,
        )
        # Check February (leap year 2024 has 29 days)
        feb_window = [w for w in windows if w[2].month == 2]
        if feb_window:
            assert feb_window[0][3] == date(2024, 2, 29)

    def test_windows_are_contiguous(self):
        """Adjacent windows' test periods are contiguous (no gaps/overlaps)."""
        windows = generate_walk_forward_windows(
            overall_start=date(2020, 1, 1),
            overall_end=date(2021, 12, 31),
            train_months=12,
            test_months=3,
            step_months=3,
        )
        for i in range(len(windows) - 1):
            # Current test_end + 1 day = next test_start
            assert windows[i][3] + __import__("datetime").timedelta(days=1) == windows[i + 1][2]

    def test_full_pipeline_range(self):
        """Full 2020-2025 range with default 12/3/3 produces ~16 windows."""
        windows = generate_walk_forward_windows(
            overall_start=date(2020, 1, 1),
            overall_end=date(2025, 12, 31),
            train_months=12,
            test_months=3,
            step_months=3,
        )
        # 6 years: first test ends 2021-03, last test ends 2025-12
        # Windows: 2021-Q1 through 2025-Q4 = 20 quarters
        # But first window needs 12m train, so first test = Q1 2021
        # Last possible test = Q4 2025 → about 20 windows
        assert len(windows) >= 16
        assert len(windows) <= 20


# ---------------------------------------------------------------------------
# Walk-forward integration (uses real data, skipped if missing)
# ---------------------------------------------------------------------------


pytestmark_data = pytest.mark.skipif(
    not PARQUET_PATH.exists(),
    reason=f"Canonical parquet not found: {PARQUET_PATH}",
)


@pytest.fixture(scope="module")
def walk_forward_result(tmp_path_factory):
    """Run walk-forward with short windows on 2024 data.

    Uses 2m train / 1m test / 1m step to produce multiple windows
    without requiring years of data. Scoped to module for efficiency.

    Date range 2024-01-01 to 2024-05-31 produces 3 windows:
      W1: Train Jan-Feb, Test Mar
      W2: Train Feb-Mar, Test Apr
      W3: Train Mar-Apr, Test May
    This fits within the canonical parquet (ends ~2024-06-27).
    """
    if not PARQUET_PATH.exists():
        pytest.skip("Canonical parquet not found")

    tmp_dir = tmp_path_factory.mktemp("walk_forward")
    db_path = tmp_dir / "test_wf.db"

    wf_result = run_walk_forward(
        strategy_cls=SMACrossover,
        parquet_path=PARQUET_PATH,
        cash=10_000.0,
        db_path=db_path,
        walk_forward_config={
            "train_window_months": 2,
            "test_window_months": 1,
            "step_months": 1,
        },
        overall_start=date(2024, 1, 1),
        overall_end=date(2024, 5, 31),
    )

    # Attach db_path for registry tests
    wf_result._test_db_path = db_path
    return wf_result


@pytestmark_data
class TestWalkForwardRun:
    """Verify walk-forward run completes and produces expected results."""

    def test_returns_walk_forward_result(self, walk_forward_result):
        """Must return a WalkForwardResult."""
        assert isinstance(walk_forward_result, WalkForwardResult)

    def test_correct_number_of_windows(self, walk_forward_result):
        """Should produce 3 windows (2m/1m/1m over 5 months)."""
        assert len(walk_forward_result.windows) == 3
        assert len(walk_forward_result.window_results) == 3

    def test_window_results_are_backtest_results(self, walk_forward_result):
        """Each window result must be a BacktestResult."""
        for wr in walk_forward_result.window_results:
            assert isinstance(wr, BacktestResult)

    def test_summary_run_id_is_uuid(self, walk_forward_result):
        """Summary run_id must be a valid UUID string."""
        rid = walk_forward_result.summary_run_id
        assert len(rid) == 36  # UUID4 format: 8-4-4-4-12
        assert rid.count("-") == 4


@pytestmark_data
class TestWalkForwardRegistry:
    """Verify walk-forward registry rows are written correctly."""

    @pytest.fixture(scope="class")
    def db_rows(self, walk_forward_result):
        """Fetch all registry rows for this walk-forward run."""
        db_path = walk_forward_result._test_db_path
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        rows = [dict(r) for r in conn.execute("SELECT * FROM runs").fetchall()]
        conn.close()
        return rows

    def test_total_row_count(self, db_rows, walk_forward_result):
        """Registry must have N window rows + 1 summary row."""
        n_windows = len(walk_forward_result.windows)
        assert len(db_rows) == n_windows + 1

    def test_window_rows_have_correct_type(self, db_rows):
        """Window rows must have run_type='walk_forward_window'."""
        window_rows = [r for r in db_rows if r["run_type"] == "walk_forward_window"]
        assert len(window_rows) >= 3  # At least 3 windows

    def test_summary_row_exists(self, db_rows):
        """Exactly one walk_forward_summary row must exist."""
        summary_rows = [r for r in db_rows if r["run_type"] == "walk_forward_summary"]
        assert len(summary_rows) == 1

    def test_window_parent_ids_match_summary(self, db_rows, walk_forward_result):
        """All window rows must have parent_run_id = summary's run_id."""
        summary_id = walk_forward_result.summary_run_id
        window_rows = [r for r in db_rows if r["run_type"] == "walk_forward_window"]
        for wr in window_rows:
            assert wr["parent_run_id"] == summary_id

    def test_summary_parent_id_is_null(self, db_rows):
        """Summary row must have parent_run_id = NULL."""
        summary = [r for r in db_rows if r["run_type"] == "walk_forward_summary"][0]
        assert summary["parent_run_id"] is None

    def test_window_rows_have_train_dates(self, db_rows):
        """Window rows must have non-NULL train_start and train_end."""
        window_rows = [r for r in db_rows if r["run_type"] == "walk_forward_window"]
        for wr in window_rows:
            assert wr["train_start"] is not None
            assert wr["train_end"] is not None

    def test_window_rows_have_test_dates(self, db_rows):
        """Window rows must have non-NULL test_start and test_end."""
        window_rows = [r for r in db_rows if r["run_type"] == "walk_forward_window"]
        for wr in window_rows:
            assert wr["test_start"] is not None
            assert wr["test_end"] is not None

    def test_window_fee_model(self, db_rows):
        """All rows must have fee_model='effective_7bps_per_side'."""
        for row in db_rows:
            assert row["fee_model"] == "effective_7bps_per_side"

    def test_window_strategy_name(self, db_rows):
        """All rows must have strategy_name='sma_crossover'."""
        for row in db_rows:
            assert row["strategy_name"] == "sma_crossover"


@pytestmark_data
class TestTradeArtifactIsolation:
    """Verify per-window trade CSVs contain only test-period trades.

    This is the strongest check for no trade/position leakage. For every
    window, the persisted trade CSV must contain only trades whose
    entry and exit times fall within that window's test_start to test_end.
    """

    @pytest.fixture(scope="class")
    def window_rows(self, walk_forward_result):
        """Fetch window registry rows with their trade CSVs."""
        db_path = walk_forward_result._test_db_path
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        rows = [
            dict(r) for r in conn.execute(
                "SELECT * FROM runs WHERE run_type = 'walk_forward_window'"
            ).fetchall()
        ]
        conn.close()
        return rows

    def test_all_window_csvs_exist(self, window_rows):
        """Every window must have a trade CSV on disk."""
        from backtest.engine import RESULTS_DIR
        for row in window_rows:
            csv_path = RESULTS_DIR / f"trades_{row['run_id']}.csv"
            assert csv_path.exists(), f"Missing: {csv_path}"

    def test_csv_row_counts_match_registry(self, window_rows):
        """Trade CSV row count must match registry total_trades."""
        import pandas as _pd
        from backtest.engine import RESULTS_DIR
        for row in window_rows:
            csv_path = RESULTS_DIR / f"trades_{row['run_id']}.csv"
            if not csv_path.exists():
                continue
            trades = _pd.read_csv(csv_path)
            assert len(trades) == row["total_trades"], (
                f"Window {row['run_id'][:8]}: CSV has {len(trades)} rows, "
                f"registry has {row['total_trades']}"
            )

    def test_all_entries_within_test_window(self, window_rows):
        """Every trade entry_time_utc must be >= test_start."""
        import pandas as _pd
        from backtest.engine import RESULTS_DIR
        for row in window_rows:
            csv_path = RESULTS_DIR / f"trades_{row['run_id']}.csv"
            if not csv_path.exists():
                continue
            trades = _pd.read_csv(csv_path, parse_dates=["entry_time_utc"])
            if len(trades) == 0:
                continue
            test_start = _pd.Timestamp(row["test_start"])
            leaked = trades[trades["entry_time_utc"] < test_start]
            assert len(leaked) == 0, (
                f"Window {row['run_id'][:8]}: {len(leaked)} trade entries "
                f"before test_start={test_start}"
            )

    def test_all_exits_within_test_window(self, window_rows):
        """Every trade exit_time_utc must be <= test_end."""
        import pandas as _pd
        from backtest.engine import RESULTS_DIR
        for row in window_rows:
            csv_path = RESULTS_DIR / f"trades_{row['run_id']}.csv"
            if not csv_path.exists():
                continue
            trades = _pd.read_csv(csv_path, parse_dates=["exit_time_utc"])
            if len(trades) == 0:
                continue
            test_end = _pd.Timestamp(row["test_end"])
            leaked = trades[trades["exit_time_utc"] > test_end]
            assert len(leaked) == 0, (
                f"Window {row['run_id'][:8]}: {len(leaked)} trade exits "
                f"after test_end={test_end}"
            )


@pytestmark_data
class TestWalkForwardSummaryMetrics:
    """Verify summary metrics are populated and reasonable."""

    def test_sharpe_is_finite(self, walk_forward_result):
        """Summary sharpe_ratio must be finite."""
        sharpe = walk_forward_result.summary_metrics["sharpe_ratio"]
        assert math.isfinite(sharpe)

    def test_total_return_is_finite(self, walk_forward_result):
        """Summary total_return must be finite."""
        ret = walk_forward_result.summary_metrics["total_return"]
        assert math.isfinite(ret)

    def test_max_drawdown_in_range(self, walk_forward_result):
        """Summary max_drawdown must be between 0 and 1."""
        dd = walk_forward_result.summary_metrics["max_drawdown"]
        assert 0.0 <= dd <= 1.0

    def test_total_trades_positive(self, walk_forward_result):
        """Summary total_trades must be > 0 (sum across windows)."""
        assert walk_forward_result.summary_metrics["total_trades"] > 0

    def test_win_rate_in_range(self, walk_forward_result):
        """Summary win_rate must be between 0 and 1."""
        wr = walk_forward_result.summary_metrics["win_rate"]
        assert 0.0 <= wr <= 1.0

    def test_summary_notes_has_metadata(self, walk_forward_result):
        """Summary registry row notes must include num_windows."""
        db_path = walk_forward_result._test_db_path
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        summary = dict(conn.execute(
            "SELECT * FROM runs WHERE run_type = 'walk_forward_summary'"
        ).fetchone())
        conn.close()

        import json
        notes = json.loads(summary["notes"])
        assert notes["num_windows"] == len(walk_forward_result.windows)
        assert notes["train_months"] == 2
        assert notes["test_months"] == 1


# ---------------------------------------------------------------------------
# Backward compatibility
# ---------------------------------------------------------------------------


class TestBackwardCompatibility:
    """Verify Phase 1A single-run mode still works unchanged."""

    def test_single_run_still_produces_trades(self, tmp_path):
        """Single-run engine path must be completely unchanged."""
        from tests.test_engine import _BuyOnBar5, _make_test_parquet

        path = _make_test_parquet(tmp_path, n_hours=30)
        result = run_backtest(
            strategy_cls=_BuyOnBar5,
            start_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
            end_date=datetime(2024, 1, 2, 5, 0, tzinfo=timezone.utc),
            parquet_path=path,
            write_registry=False,
        )
        assert isinstance(result, BacktestResult)
        assert len(result.trades) == 1
        assert result.strategy_name == "test_buy_bar5"

    def test_single_run_registry_defaults(self, tmp_path):
        """Single-run registry row must still use Phase 1A defaults."""
        from tests.test_engine import _BuyOnBar5, _make_test_parquet

        db_path = tmp_path / "compat.db"
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
        row = dict(conn.execute(
            "SELECT * FROM runs WHERE run_id = ?", (result.run_id,)
        ).fetchone())
        conn.close()

        # Phase 1A defaults preserved
        assert row["run_type"] == "single_run"
        assert row["parent_run_id"] is None
        assert row["train_start"] is None
        assert row["train_end"] is None

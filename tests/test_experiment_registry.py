"""Tests for backtest/experiment_registry.py.

Tests create, insert, query, stats, and review update operations
using an in-memory SQLite database.
"""

from __future__ import annotations

import sqlite3

import pytest

from backtest.experiment_registry import (
    create_table,
    get_connection,
    get_run,
    get_stats,
    insert_run,
    list_runs,
    update_review,
    compute_config_hash,
    get_split_version,
)


@pytest.fixture
def db_conn():
    """Create an in-memory SQLite database with the runs table.

    Yields:
        sqlite3.Connection ready for testing.
    """
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    create_table(conn)
    yield conn
    conn.close()


def _sample_run(**overrides) -> dict:
    """Create a sample run dict with sensible defaults.

    Args:
        **overrides: Fields to override.

    Returns:
        Dict suitable for insert_run().
    """
    data = {
        "strategy_name": "sma_crossover_20_50",
        "strategy_source": "manual",
        "data_snapshot_date": "2026-04-15",
        "train_start": "2020-01-01",
        "train_end": "2023-12-31",
        "validation_start": "2024-01-01",
        "validation_end": "2024-12-31",
        "test_start": "2025-01-01",
        "test_end": "2025-12-31",
        "total_return": 0.15,
        "sharpe_ratio": 1.2,
        "max_drawdown": 0.18,
        "total_trades": 48,
        "win_rate": 0.55,
        "avg_trade_duration_hours": 72.5,
        "fee_model": "taker_4bps_slip_3bps",
        "notes": "Test run",
    }
    data.update(overrides)
    return data


# ---------------------------------------------------------------------------
# Table creation
# ---------------------------------------------------------------------------


class TestCreateTable:
    def test_table_created(self, db_conn):
        cursor = db_conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='runs'"
        )
        assert cursor.fetchone() is not None

    def test_idempotent(self, db_conn):
        # Second call should not fail
        create_table(db_conn)
        cursor = db_conn.execute("SELECT COUNT(*) FROM runs")
        assert cursor.fetchone()[0] == 0


# ---------------------------------------------------------------------------
# Insert
# ---------------------------------------------------------------------------


class TestInsertRun:
    def test_basic_insert(self, db_conn):
        run_id = insert_run(db_conn, _sample_run())
        assert run_id is not None
        assert len(run_id) == 36  # UUID format

    def test_auto_fields_populated(self, db_conn):
        run_id = insert_run(db_conn, _sample_run())
        row = get_run(db_conn, run_id)
        assert row is not None
        assert row["created_at_utc"] is not None
        assert row["config_hash"] is not None
        assert row["split_version"] is not None
        assert row["feature_version"] == "none"
        assert row["review_status"] == "pending"

    def test_missing_required_field_raises(self, db_conn):
        with pytest.raises(ValueError, match="Missing required field"):
            insert_run(db_conn, {"strategy_name": "test"})

    def test_custom_run_id(self, db_conn):
        custom_id = "custom-id-12345"
        run_id = insert_run(db_conn, _sample_run(run_id=custom_id))
        assert run_id == custom_id

    def test_multiple_inserts(self, db_conn):
        insert_run(db_conn, _sample_run())
        insert_run(db_conn, _sample_run(strategy_name="momentum_5d"))
        insert_run(db_conn, _sample_run(strategy_name="mean_reversion_zscore"))

        runs = list_runs(db_conn, limit=100)
        assert len(runs) == 3

    def test_null_optional_fields(self, db_conn):
        run_id = insert_run(
            db_conn,
            {
                "strategy_name": "simple",
                "strategy_source": "manual",
                "total_return": None,
                "sharpe_ratio": None,
            },
        )
        row = get_run(db_conn, run_id)
        assert row["total_return"] is None
        assert row["sharpe_ratio"] is None


# ---------------------------------------------------------------------------
# Query
# ---------------------------------------------------------------------------


class TestGetRun:
    def test_get_existing(self, db_conn):
        run_id = insert_run(db_conn, _sample_run())
        row = get_run(db_conn, run_id)
        assert row is not None
        assert row["strategy_name"] == "sma_crossover_20_50"
        assert row["total_return"] == 0.15

    def test_get_nonexistent(self, db_conn):
        row = get_run(db_conn, "nonexistent-id")
        assert row is None

    def test_all_fields_round_trip(self, db_conn):
        data = _sample_run()
        run_id = insert_run(db_conn, data)
        row = get_run(db_conn, run_id)

        assert row["strategy_source"] == "manual"
        assert row["train_start"] == "2020-01-01"
        assert row["test_end"] == "2025-12-31"
        assert row["total_trades"] == 48
        assert row["win_rate"] == 0.55
        assert row["fee_model"] == "taker_4bps_slip_3bps"


class TestListRuns:
    def test_empty_db(self, db_conn):
        runs = list_runs(db_conn)
        assert runs == []

    def test_list_all(self, db_conn):
        for i in range(5):
            insert_run(db_conn, _sample_run(strategy_name=f"strat_{i}"))
        runs = list_runs(db_conn)
        assert len(runs) == 5

    def test_filter_by_strategy(self, db_conn):
        insert_run(db_conn, _sample_run(strategy_name="sma"))
        insert_run(db_conn, _sample_run(strategy_name="sma"))
        insert_run(db_conn, _sample_run(strategy_name="momentum"))

        sma_runs = list_runs(db_conn, strategy_name="sma")
        assert len(sma_runs) == 2

        mom_runs = list_runs(db_conn, strategy_name="momentum")
        assert len(mom_runs) == 1

    def test_limit(self, db_conn):
        for i in range(10):
            insert_run(db_conn, _sample_run(strategy_name=f"strat_{i}"))
        runs = list_runs(db_conn, limit=3)
        assert len(runs) == 3

    def test_ordered_by_created_at_desc(self, db_conn):
        insert_run(db_conn, _sample_run(
            strategy_name="first", created_at_utc="2026-01-01T00:00:00Z"
        ))
        insert_run(db_conn, _sample_run(
            strategy_name="second", created_at_utc="2026-02-01T00:00:00Z"
        ))
        insert_run(db_conn, _sample_run(
            strategy_name="third", created_at_utc="2026-03-01T00:00:00Z"
        ))
        runs = list_runs(db_conn)
        assert runs[0]["strategy_name"] == "third"
        assert runs[2]["strategy_name"] == "first"


# ---------------------------------------------------------------------------
# Stats
# ---------------------------------------------------------------------------


class TestGetStats:
    def test_empty_db(self, db_conn):
        stats = get_stats(db_conn)
        assert stats["total_runs"] == 0

    def test_basic_stats(self, db_conn):
        insert_run(db_conn, _sample_run(sharpe_ratio=1.0, total_return=0.10))
        insert_run(db_conn, _sample_run(sharpe_ratio=2.0, total_return=0.20))
        insert_run(db_conn, _sample_run(
            strategy_name="momentum", sharpe_ratio=0.5, total_return=0.05
        ))

        stats = get_stats(db_conn)
        assert stats["total_runs"] == 3
        assert stats["unique_strategies"] == 2
        assert abs(stats["avg_sharpe"] - (1.0 + 2.0 + 0.5) / 3) < 0.001
        assert stats["min_sharpe"] == 0.5
        assert stats["max_sharpe"] == 2.0

    def test_review_breakdown(self, db_conn):
        insert_run(db_conn, _sample_run())
        insert_run(db_conn, _sample_run())

        # Update one to approved
        runs = list_runs(db_conn)
        update_review(db_conn, runs[0]["run_id"], "approved", "Good results")

        stats = get_stats(db_conn)
        assert stats["review_breakdown"]["pending"] == 1
        assert stats["review_breakdown"]["approved"] == 1

    def test_by_strategy_breakdown(self, db_conn):
        insert_run(db_conn, _sample_run(strategy_name="sma", sharpe_ratio=1.5))
        insert_run(db_conn, _sample_run(strategy_name="sma", sharpe_ratio=1.0))
        insert_run(db_conn, _sample_run(strategy_name="momentum", sharpe_ratio=2.0))

        stats = get_stats(db_conn)
        assert len(stats["by_strategy"]) == 2
        # Sorted by avg_sharpe DESC, so momentum first
        assert stats["by_strategy"][0]["strategy_name"] == "momentum"


# ---------------------------------------------------------------------------
# Review update
# ---------------------------------------------------------------------------


class TestUpdateReview:
    def test_approve(self, db_conn):
        run_id = insert_run(db_conn, _sample_run())
        result = update_review(db_conn, run_id, "approved", "Meets DSR criteria")
        assert result is True

        row = get_run(db_conn, run_id)
        assert row["review_status"] == "approved"
        assert row["review_reason"] == "Meets DSR criteria"

    def test_reject(self, db_conn):
        run_id = insert_run(db_conn, _sample_run())
        result = update_review(db_conn, run_id, "rejected", "Overfit")
        assert result is True

        row = get_run(db_conn, run_id)
        assert row["review_status"] == "rejected"

    def test_invalid_status(self, db_conn):
        run_id = insert_run(db_conn, _sample_run())
        with pytest.raises(ValueError, match="Invalid status"):
            update_review(db_conn, run_id, "invalid_status")

    def test_nonexistent_run(self, db_conn):
        result = update_review(db_conn, "nonexistent-id", "approved")
        assert result is False


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class TestHelpers:
    def test_config_hash_deterministic(self):
        h1 = compute_config_hash()
        h2 = compute_config_hash()
        assert h1 == h2
        assert h1.startswith("sha256:")

    def test_split_version(self):
        version = get_split_version()
        assert version == "v1"

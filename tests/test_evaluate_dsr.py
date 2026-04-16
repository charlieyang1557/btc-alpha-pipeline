"""Tests for backtest/evaluate_dsr.py.

Verifies:
- Expected maximum Sharpe threshold computation
- Evaluation logic (survive/not survive) across edge cases
- Registry query integration
- Empty query produces clean output
"""

from __future__ import annotations

import math
import sqlite3
from pathlib import Path

import pytest

from backtest.evaluate_dsr import (
    compute_expected_max_sharpe,
    evaluate_trials,
    query_sharpe_ratios,
)


# ---------------------------------------------------------------------------
# Threshold computation
# ---------------------------------------------------------------------------


class TestComputeThreshold:
    """Verify sqrt(2 * ln(N)) threshold computation."""

    def test_n1_threshold_is_zero(self):
        """N=1: threshold = 0, any positive Sharpe survives."""
        assert compute_expected_max_sharpe(1) == 0.0

    def test_n0_threshold_is_zero(self):
        """N=0: degenerate case, threshold = 0."""
        assert compute_expected_max_sharpe(0) == 0.0

    def test_n20_threshold(self):
        """N=20: threshold ≈ sqrt(2 * ln(20)) ≈ 2.448."""
        expected = math.sqrt(2.0 * math.log(20))
        assert compute_expected_max_sharpe(20) == pytest.approx(expected)
        # Verify numerical value
        assert compute_expected_max_sharpe(20) == pytest.approx(2.448, rel=1e-2)

    def test_n5_threshold(self):
        """N=5: threshold ≈ sqrt(2 * ln(5)) ≈ 1.794."""
        expected = math.sqrt(2.0 * math.log(5))
        assert compute_expected_max_sharpe(5) == pytest.approx(expected)
        assert compute_expected_max_sharpe(5) == pytest.approx(1.794, rel=1e-2)

    def test_n100_threshold(self):
        """N=100: threshold ≈ sqrt(2 * ln(100)) ≈ 3.034."""
        expected = math.sqrt(2.0 * math.log(100))
        assert compute_expected_max_sharpe(100) == pytest.approx(expected)

    def test_monotonically_increasing(self):
        """Threshold increases with N."""
        thresholds = [compute_expected_max_sharpe(n) for n in [2, 5, 10, 50, 100]]
        for i in range(len(thresholds) - 1):
            assert thresholds[i] < thresholds[i + 1]


# ---------------------------------------------------------------------------
# Evaluation logic
# ---------------------------------------------------------------------------


class TestEvaluateTrials:
    """Verify the survive/not-survive decision logic."""

    def test_n1_any_positive_survives(self):
        """N=1: threshold=0, any positive Sharpe survives."""
        result = evaluate_trials({"strat_a": 0.5})
        assert result["n_trials"] == 1
        assert result["threshold"] == 0.0
        assert result["survives"] is True
        assert result["best_strategy"] == "strat_a"

    def test_n20_low_sharpe_does_not_survive(self):
        """N=20, best Sharpe=0.5: should NOT survive (threshold ≈ 2.45)."""
        sharpes = {f"strat_{i}": 0.5 - i * 0.02 for i in range(20)}
        result = evaluate_trials(sharpes)
        assert result["n_trials"] == 20
        assert result["threshold"] == pytest.approx(2.448, rel=1e-2)
        assert result["best_sharpe"] == pytest.approx(0.5)
        assert result["survives"] is False

    def test_n5_high_sharpe_survives(self):
        """N=5, best Sharpe=3.0: should survive (threshold ≈ 1.79)."""
        sharpes = {"alpha": 3.0, "beta": 1.0, "gamma": 0.5, "delta": -0.2, "epsilon": -1.0}
        result = evaluate_trials(sharpes)
        assert result["n_trials"] == 5
        assert result["threshold"] == pytest.approx(1.794, rel=1e-2)
        assert result["best_sharpe"] == pytest.approx(3.0)
        assert result["survives"] is True

    def test_empty_no_error(self):
        """Empty input → clean result, not an error."""
        result = evaluate_trials({})
        assert result["n_trials"] == 0
        assert result["survives"] is False
        assert result["best_strategy"] is None
        assert result["rankings"] == []

    def test_rankings_sorted_descending(self):
        """Rankings must be sorted by Sharpe descending."""
        sharpes = {"a": -1.0, "b": 2.0, "c": 0.5}
        result = evaluate_trials(sharpes)
        rankings = result["rankings"]
        assert rankings[0]["strategy"] == "b"
        assert rankings[1]["strategy"] == "c"
        assert rankings[2]["strategy"] == "a"

    def test_mean_sharpe(self):
        """Mean Sharpe must be the arithmetic mean."""
        sharpes = {"a": 1.0, "b": 2.0, "c": 3.0}
        result = evaluate_trials(sharpes)
        assert result["mean_sharpe"] == pytest.approx(2.0)

    def test_worst_sharpe(self):
        """Worst Sharpe is the minimum."""
        sharpes = {"a": 1.0, "b": -2.0, "c": 0.5}
        result = evaluate_trials(sharpes)
        assert result["worst_sharpe"] == pytest.approx(-2.0)

    def test_negative_best_does_not_survive(self):
        """If best Sharpe is negative, it should not survive."""
        sharpes = {"a": -0.5, "b": -1.0}
        result = evaluate_trials(sharpes)
        assert result["survives"] is False

    def test_exactly_at_threshold_does_not_survive(self):
        """Sharpe exactly at threshold does NOT survive (strict >)."""
        # N=2: threshold = sqrt(2 * ln(2)) ≈ 1.1774
        threshold = math.sqrt(2.0 * math.log(2))
        sharpes = {"a": threshold, "b": 0.0}
        result = evaluate_trials(sharpes)
        assert result["survives"] is False


# ---------------------------------------------------------------------------
# Registry query integration
# ---------------------------------------------------------------------------


class TestQuerySharpeRatios:
    """Verify registry query with real SQLite data."""

    @pytest.fixture
    def populated_db(self, tmp_path):
        """Create a test DB with sample runs."""
        from backtest.experiment_registry import create_table, get_connection, insert_run

        db_path = tmp_path / "test.db"
        conn = get_connection(db_path)
        create_table(conn)

        runs = [
            {
                "strategy_name": "sma_crossover",
                "strategy_source": "manual",
                "run_type": "walk_forward_summary",
                "sharpe_ratio": 0.8,
                "split_version": "v1",
            },
            {
                "strategy_name": "momentum",
                "strategy_source": "manual",
                "run_type": "walk_forward_summary",
                "sharpe_ratio": -0.3,
                "split_version": "v1",
            },
            {
                "strategy_name": "mean_reversion",
                "strategy_source": "manual",
                "run_type": "walk_forward_summary",
                "sharpe_ratio": 1.5,
                "split_version": "v1",
            },
            {
                "strategy_name": "broken",
                "strategy_source": "manual",
                "run_type": "walk_forward_summary",
                "sharpe_ratio": None,  # NULL — should be excluded
                "split_version": "v1",
            },
            {
                "strategy_name": "other_version",
                "strategy_source": "manual",
                "run_type": "walk_forward_summary",
                "sharpe_ratio": 5.0,
                "split_version": "v2",  # Different version
            },
            {
                "strategy_name": "sma_single",
                "strategy_source": "manual",
                "run_type": "single_run",
                "sharpe_ratio": 0.5,
                "split_version": "v1",
            },
        ]
        for run in runs:
            insert_run(conn, run)
        conn.close()

        return db_path

    def test_filters_by_split_version(self, populated_db):
        """Only v1 runs returned when querying v1."""
        result = query_sharpe_ratios("v1", db_path=populated_db)
        assert len(result) == 3  # sma_crossover, momentum, mean_reversion

    def test_excludes_null_sharpe(self, populated_db):
        """Runs with NULL sharpe_ratio are excluded."""
        result = query_sharpe_ratios("v1", db_path=populated_db)
        # "broken" has NULL sharpe — should not appear
        assert all("broken" not in k for k in result.keys())

    def test_excludes_wrong_version(self, populated_db):
        """v2 runs should not appear in v1 query."""
        result = query_sharpe_ratios("v1", db_path=populated_db)
        assert all("other_version" not in k for k in result.keys())

    def test_filters_by_run_type(self, populated_db):
        """Only walk_forward_summary rows by default."""
        result = query_sharpe_ratios("v1", db_path=populated_db)
        assert all("sma_single" not in k for k in result.keys())

    def test_single_run_type_filter(self, populated_db):
        """Can query single_run type."""
        result = query_sharpe_ratios(
            "v1", run_type="single_run", db_path=populated_db
        )
        assert len(result) == 1
        assert any("sma_single" in k for k in result.keys())

    def test_strategy_filter(self, populated_db):
        """Can filter by strategy_name."""
        result = query_sharpe_ratios(
            "v1", strategy_name="momentum", db_path=populated_db
        )
        assert len(result) == 1
        assert any("momentum" in k for k in result.keys())

    def test_empty_query(self, populated_db):
        """Non-existent version returns empty dict."""
        result = query_sharpe_ratios("v99", db_path=populated_db)
        assert result == {}

    def test_sharpe_values_correct(self, populated_db):
        """Queried Sharpe values match what was inserted."""
        result = query_sharpe_ratios("v1", db_path=populated_db)
        sharpes = set(result.values())
        assert 0.8 in sharpes
        assert -0.3 in sharpes
        assert 1.5 in sharpes


# ---------------------------------------------------------------------------
# End-to-end: query + evaluate
# ---------------------------------------------------------------------------


class TestEndToEnd:
    """Verify full pipeline: query → evaluate → decision."""

    @pytest.fixture
    def db_with_strategies(self, tmp_path):
        """Create DB with strategies that should NOT survive."""
        from backtest.experiment_registry import create_table, get_connection, insert_run

        db_path = tmp_path / "e2e.db"
        conn = get_connection(db_path)
        create_table(conn)

        # 5 strategies, best Sharpe = 0.8
        # threshold = sqrt(2*ln(5)) ≈ 1.794 → best does NOT survive
        for i, (name, sharpe) in enumerate([
            ("alpha", 0.8),
            ("beta", 0.3),
            ("gamma", -0.1),
            ("delta", -0.5),
            ("epsilon", 0.1),
        ]):
            insert_run(conn, {
                "strategy_name": name,
                "strategy_source": "manual",
                "run_type": "walk_forward_summary",
                "sharpe_ratio": sharpe,
                "split_version": "v1",
            })
        conn.close()
        return db_path

    def test_none_survive(self, db_with_strategies):
        """5 strategies with best=0.8: none survive (threshold ≈ 1.79)."""
        sharpes = query_sharpe_ratios("v1", db_path=db_with_strategies)
        result = evaluate_trials(sharpes)
        assert result["n_trials"] == 5
        assert result["survives"] is False

    def test_single_strong_survives(self, tmp_path):
        """1 strategy with Sharpe=2.0: survives (N=1, threshold=0)."""
        from backtest.experiment_registry import create_table, get_connection, insert_run

        db_path = tmp_path / "single.db"
        conn = get_connection(db_path)
        create_table(conn)
        insert_run(conn, {
            "strategy_name": "winner",
            "strategy_source": "manual",
            "run_type": "walk_forward_summary",
            "sharpe_ratio": 2.0,
            "split_version": "v1",
        })
        conn.close()

        sharpes = query_sharpe_ratios("v1", db_path=db_path)
        result = evaluate_trials(sharpes)
        assert result["n_trials"] == 1
        assert result["survives"] is True

"""Tests for Phase 2A D4 — Regime Holdout Integration.

Covers:
    - ``_evaluate_regime_holdout_pass`` 4-condition AND gate (exhaustive
      boundary + the exact spec cases from the D4 blueprint).
    - ``_load_v2_train_ranges`` rejects non-v2 configs and reads
      disjoint ranges correctly.
    - v2 walk-forward window generation contains zero 2022 bars.
    - Train-side summaries are per-range aggregates; equity curves are
      NEVER stitched across the 2022 gap
      (``_aggregate_walk_forward_metrics`` preserves independence).
    - ``run_regime_holdout`` produces a registry row with correct
      ``run_type``, ``parent_run_id``, ``batch_id``, ``hypothesis_hash``,
      and the ``regime_holdout_passed`` INTEGER encoding.
    - End-to-end integration: DSL-compiled SMA crossover on v2 train
      ranges + 2022 holdout yields two ``walk_forward_summary`` rows
      (one per range) + one ``regime_holdout`` row linked via
      ``parent_run_id``.
    - Registry migration is idempotent and preserves Phase 1 rows.
"""

from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import date, datetime, timezone
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PARQUET_PATH = PROJECT_ROOT / "data" / "raw" / "btcusdt_1h.parquet"


# ===========================================================================
# 1. Passing-criteria AND gate — exhaustive boundary + spec cases.
# ===========================================================================


PASS_CRITERIA = {
    "min_sharpe": -0.5,
    "max_drawdown": 0.25,
    "min_total_return": -0.15,
    "min_total_trades": 5,
}


def _metrics(sharpe, dd, ret, trades):
    """Build a minimal metrics dict shaped like ``compute_all_metrics``."""
    return {
        "sharpe_ratio": sharpe,
        "max_drawdown": dd,
        "total_return": ret,
        "total_trades": trades,
    }


class TestPassingCriteriaSpecCases:
    """The five labelled cases from the D4 blueprint spec."""

    def test_sharpe_gate_fails(self):
        from backtest.engine import _evaluate_regime_holdout_pass
        m = _metrics(-0.6, 0.20, -0.10, 10)
        assert _evaluate_regime_holdout_pass(m, PASS_CRITERIA) is False

    def test_drawdown_gate_fails(self):
        from backtest.engine import _evaluate_regime_holdout_pass
        m = _metrics(0.0, 0.30, -0.10, 10)
        assert _evaluate_regime_holdout_pass(m, PASS_CRITERIA) is False

    def test_return_gate_fails(self):
        from backtest.engine import _evaluate_regime_holdout_pass
        m = _metrics(0.0, 0.20, -0.20, 10)
        assert _evaluate_regime_holdout_pass(m, PASS_CRITERIA) is False

    def test_trade_count_gate_fails(self):
        from backtest.engine import _evaluate_regime_holdout_pass
        m = _metrics(0.5, 0.20, -0.05, 3)
        assert _evaluate_regime_holdout_pass(m, PASS_CRITERIA) is False

    def test_all_four_pass(self):
        from backtest.engine import _evaluate_regime_holdout_pass
        m = _metrics(-0.3, 0.20, -0.10, 10)
        assert _evaluate_regime_holdout_pass(m, PASS_CRITERIA) is True


class TestPassingCriteriaBoundaries:
    """Exhaustive boundary tests — each gate at its exact threshold and
    just off it. Verifies operator direction (>= vs >, <= vs <)."""

    def test_sharpe_at_lower_bound_passes(self):
        from backtest.engine import _evaluate_regime_holdout_pass
        assert _evaluate_regime_holdout_pass(
            _metrics(-0.5, 0.20, -0.10, 10), PASS_CRITERIA
        ) is True

    def test_sharpe_just_below_fails(self):
        from backtest.engine import _evaluate_regime_holdout_pass
        assert _evaluate_regime_holdout_pass(
            _metrics(-0.500001, 0.20, -0.10, 10), PASS_CRITERIA
        ) is False

    def test_drawdown_at_upper_bound_passes(self):
        from backtest.engine import _evaluate_regime_holdout_pass
        assert _evaluate_regime_holdout_pass(
            _metrics(0.0, 0.25, -0.10, 10), PASS_CRITERIA
        ) is True

    def test_drawdown_just_above_fails(self):
        from backtest.engine import _evaluate_regime_holdout_pass
        assert _evaluate_regime_holdout_pass(
            _metrics(0.0, 0.250001, -0.10, 10), PASS_CRITERIA
        ) is False

    def test_return_at_lower_bound_passes(self):
        from backtest.engine import _evaluate_regime_holdout_pass
        assert _evaluate_regime_holdout_pass(
            _metrics(0.0, 0.20, -0.15, 10), PASS_CRITERIA
        ) is True

    def test_return_just_below_fails(self):
        from backtest.engine import _evaluate_regime_holdout_pass
        assert _evaluate_regime_holdout_pass(
            _metrics(0.0, 0.20, -0.150001, 10), PASS_CRITERIA
        ) is False

    def test_trades_at_lower_bound_passes(self):
        from backtest.engine import _evaluate_regime_holdout_pass
        assert _evaluate_regime_holdout_pass(
            _metrics(0.0, 0.20, -0.10, 5), PASS_CRITERIA
        ) is True

    def test_trades_just_below_fails(self):
        from backtest.engine import _evaluate_regime_holdout_pass
        assert _evaluate_regime_holdout_pass(
            _metrics(0.0, 0.20, -0.10, 4), PASS_CRITERIA
        ) is False

    def test_nan_sharpe_fails(self):
        from backtest.engine import _evaluate_regime_holdout_pass
        assert _evaluate_regime_holdout_pass(
            _metrics(float("nan"), 0.20, -0.10, 10), PASS_CRITERIA
        ) is False

    def test_zero_trades_fails(self):
        from backtest.engine import _evaluate_regime_holdout_pass
        assert _evaluate_regime_holdout_pass(
            _metrics(1.0, 0.0, 0.5, 0), PASS_CRITERIA
        ) is False

    def test_generous_pass(self):
        from backtest.engine import _evaluate_regime_holdout_pass
        assert _evaluate_regime_holdout_pass(
            _metrics(2.0, 0.05, 0.5, 100), PASS_CRITERIA
        ) is True


# ===========================================================================
# 2. v2 config: train_windows loading + walk-forward skips 2022.
# ===========================================================================


class TestV2ConfigLoader:
    """Verify ``_load_v2_train_ranges`` reads the canonical v2 yaml."""

    def test_reads_disjoint_ranges_from_disk(self):
        import yaml
        from backtest.engine import _load_v2_train_ranges

        env_path = PROJECT_ROOT / "config" / "environments.yaml"
        with open(env_path) as f:
            env_config = yaml.safe_load(f)

        ranges = _load_v2_train_ranges(env_config)
        assert ranges == [
            (date(2020, 1, 1), date(2021, 12, 31)),
            (date(2023, 1, 1), date(2023, 12, 31)),
        ]

    def test_version_is_v2(self):
        import yaml
        env_path = PROJECT_ROOT / "config" / "environments.yaml"
        with open(env_path) as f:
            env_config = yaml.safe_load(f)
        assert env_config["version"] == "v2"

    def test_regime_holdout_block_present_with_4_criteria(self):
        import yaml
        env_path = PROJECT_ROOT / "config" / "environments.yaml"
        with open(env_path) as f:
            env_config = yaml.safe_load(f)

        block = env_config["splits"]["regime_holdout"]
        assert block["start"] == "2022-01-01"
        assert block["end"] == "2022-12-31"
        assert block["label"] == "bear_2022"
        crit = block["passing_criteria"]
        assert crit["min_sharpe"] == -0.5
        assert crit["max_drawdown"] == 0.25
        assert crit["min_total_return"] == -0.15
        assert crit["min_total_trades"] == 5

    def test_validation_and_test_placeholders_present(self):
        import yaml
        env_path = PROJECT_ROOT / "config" / "environments.yaml"
        with open(env_path) as f:
            env_config = yaml.safe_load(f)
        assert env_config["splits"]["validation"]["start"] == "2024-01-01"
        assert env_config["splits"]["validation"]["end"] == "2024-12-31"
        assert env_config["splits"]["test"]["start"] == "2025-01-01"
        assert env_config["splits"]["test"]["end"] == "2025-12-31"

    def test_loader_rejects_v1_shape(self):
        from backtest.engine import _load_v2_train_ranges
        legacy = {"splits": {"training": {"start": "2020-01-01",
                                          "end": "2023-12-31"}}}
        with pytest.raises(ValueError, match="train_windows"):
            _load_v2_train_ranges(legacy)


class TestWalkForwardSkipsTwentyTwo:
    """Hard constraint: ``NEVER include 2022 bars in any walk-forward
    training window``. Verified at the window-generation layer so the
    property holds regardless of whether the engine runs on real data."""

    def test_no_window_overlaps_2022(self):
        from backtest.engine import (
            _load_v2_train_ranges,
            generate_walk_forward_windows,
        )
        import yaml
        env_path = PROJECT_ROOT / "config" / "environments.yaml"
        with open(env_path) as f:
            env_config = yaml.safe_load(f)

        wf = env_config["walk_forward"]
        ranges = _load_v2_train_ranges(env_config)

        year_2022_start = date(2022, 1, 1)
        year_2022_end = date(2022, 12, 31)

        all_windows = []
        for r_start, r_end in ranges:
            all_windows.extend(generate_walk_forward_windows(
                r_start, r_end,
                wf["train_window_months"],
                wf["test_window_months"],
                wf["step_months"],
            ))

        for w_train_start, w_train_end, w_test_start, w_test_end in all_windows:
            for d in (w_train_start, w_train_end, w_test_start, w_test_end):
                assert not (year_2022_start <= d <= year_2022_end), (
                    f"Window {(w_train_start, w_train_end, w_test_start, w_test_end)} "
                    f"touches 2022 at {d}"
                )

    def test_2020_2021_range_produces_sub_windows(self):
        from backtest.engine import generate_walk_forward_windows
        windows = generate_walk_forward_windows(
            date(2020, 1, 1), date(2021, 12, 31),
            train_months=12, test_months=3, step_months=3,
        )
        assert len(windows) == 4
        for w in windows:
            assert all(d.year in (2020, 2021) for d in w)

    def test_2023_range_too_short_yields_zero_sub_windows(self):
        """12m range can't fit 12m train + 3m test — silent skip is OK."""
        from backtest.engine import generate_walk_forward_windows
        windows = generate_walk_forward_windows(
            date(2023, 1, 1), date(2023, 12, 31),
            train_months=12, test_months=3, step_months=3,
        )
        assert windows == []


# ===========================================================================
# 3. Train aggregation is never stitched across disjoint ranges.
# ===========================================================================


class TestTrainAggregationNotStitched:
    """``_aggregate_walk_forward_metrics`` must combine per-window
    Sharpes/returns via mean/max/sum. A stitched continuous equity
    curve (multiplying returns) is a blueprint violation.
    """

    def test_mean_sharpe_not_product(self):
        from backtest.engine import _aggregate_walk_forward_metrics
        per_window = [
            {"sharpe_ratio": 1.0, "total_return": 0.10, "max_drawdown": 0.05,
             "max_drawdown_duration_hours": 1.0, "initial_capital": 10_000.0,
             "total_trades": 4, "win_rate": 0.5,
             "avg_trade_duration_hours": 10.0, "avg_trade_return": 0.02,
             "profit_factor": 1.5},
            {"sharpe_ratio": 0.0, "total_return": 0.00, "max_drawdown": 0.10,
             "max_drawdown_duration_hours": 2.0, "initial_capital": 10_000.0,
             "total_trades": 6, "win_rate": 0.5,
             "avg_trade_duration_hours": 12.0, "avg_trade_return": 0.01,
             "profit_factor": 1.0},
        ]
        agg = _aggregate_walk_forward_metrics(per_window, 2)
        assert agg["sharpe_ratio"] == pytest.approx(0.5)  # mean, not product
        assert agg["total_return"] == pytest.approx(0.05)
        assert agg["max_drawdown"] == pytest.approx(0.10)  # worst, not sum
        assert agg["total_trades"] == 10  # sum across windows


# ===========================================================================
# 4. run_regime_holdout: registry row shape + 4-condition gate plumbing.
# ===========================================================================


def _make_holdout_parquet(tmp_path: Path) -> Path:
    """Synthesize 2021-10 through 2022-12 hourly bars.

    The three extra months before 2022-01-01 give any reasonable
    warmup_bars (e.g. SMA(50)) enough pre-fromdate history to be served
    naturally by the feed. Prices follow a mild sinusoid so baseline
    strategies produce a handful of trades inside the holdout window.
    """
    import numpy as np
    import pandas as pd

    timestamps = pd.date_range(
        start="2021-10-01", end="2022-12-31 23:00", freq="h", tz="UTC"
    )
    n = len(timestamps)
    t = np.arange(n, dtype=float)
    # Mild drift + sinusoidal swings so crossovers fire a few times.
    close = 100.0 + 0.0005 * t + 5.0 * np.sin(t / 240.0)
    openp = close - 0.05
    high = close + 0.5
    low = close - 0.5

    df = pd.DataFrame({
        "open_time_utc": timestamps.astype("datetime64[ms, UTC]"),
        "open": openp,
        "high": high,
        "low": low,
        "close": close,
        "volume": np.full(n, 1000.0),
        "quote_volume": np.full(n, 100_000.0),
        "trade_count": np.arange(n, dtype="int64") + 5000,
        "ingested_at_utc": pd.Timestamp.now(tz="UTC").floor("ms"),
        "source": pd.array(["binance_vision"] * n, dtype="string"),
    })
    df["ingested_at_utc"] = df["ingested_at_utc"].astype("datetime64[ms, UTC]")

    path = tmp_path / "holdout.parquet"
    df.to_parquet(path, engine="pyarrow", index=False)
    return path


def _make_v2_env_config() -> dict:
    """Return an in-memory v2 env config matching environments.yaml."""
    return {
        "version": "v2",
        "splits": {
            "train_windows": [
                ["2020-01-01", "2021-12-31"],
                ["2023-01-01", "2023-12-31"],
            ],
            "regime_holdout": {
                "start": "2022-01-01",
                "end": "2022-12-31",
                "label": "bear_2022",
                "passing_criteria": {
                    "min_sharpe": -0.5,
                    "max_drawdown": 0.25,
                    "min_total_return": -0.15,
                    "min_total_trades": 5,
                },
            },
        },
        "walk_forward": {
            "train_window_months": 12,
            "test_window_months": 3,
            "step_months": 3,
        },
    }


class TestRunRegimeHoldoutRegistryRow:
    """``run_regime_holdout`` writes exactly one registry row with the
    correct run_type, parent linkage, and 4-column D4 metadata."""

    def test_row_shape_and_lineage(self, tmp_path):
        from backtest.engine import run_regime_holdout
        from strategies.baseline.sma_crossover import SMACrossover

        parquet = _make_holdout_parquet(tmp_path)
        db_path = tmp_path / "experiments.db"
        batch_id = str(uuid.uuid4())
        parent_run_id = str(uuid.uuid4())

        result = run_regime_holdout(
            dsl=None,
            batch_id=batch_id,
            parent_run_id=parent_run_id,
            strategy_cls=SMACrossover,
            strategy_params={"fast_period": 20, "slow_period": 50},
            parquet_path=parquet,
            db_path=db_path,
            env_config=_make_v2_env_config(),
        )

        assert result.batch_id == batch_id
        assert result.parent_run_id == parent_run_id
        assert result.regime_holdout_passed in (True, False)

        # Inspect the registry row.
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        try:
            rows = conn.execute(
                "SELECT * FROM runs WHERE run_id = ?", (result.run_id,)
            ).fetchall()
        finally:
            conn.close()

        assert len(rows) == 1
        row = dict(rows[0])
        assert row["run_type"] == "regime_holdout"
        assert row["parent_run_id"] == parent_run_id
        assert row["batch_id"] == batch_id
        # hypothesis_hash is NULL when strategy_cls is passed without dsl.
        assert row["hypothesis_hash"] is None
        # INTEGER 0/1 encoding — never NULL for a holdout row.
        assert row["regime_holdout_passed"] in (0, 1)
        assert isinstance(row["regime_holdout_passed"], int)
        # Orchestrator writes lifecycle_state; D4 must leave it NULL.
        assert row["lifecycle_state"] is None
        assert row["split_version"] == "v2"
        # Holdout range is exactly 2022-01-01 .. 2022-12-31 23:00:00Z.
        assert row["test_start"] == "2022-01-01T00:00:00Z"
        assert row["test_end"] == "2022-12-31T23:00:00Z"
        # Train columns are NULL — the holdout is a standalone run.
        assert row["train_start"] is None
        assert row["train_end"] is None

    def test_passed_flag_matches_gate(self, tmp_path):
        """End-to-end: the row's ``regime_holdout_passed`` encoding must
        match ``_evaluate_regime_holdout_pass`` applied to the metrics."""
        from backtest.engine import (
            _evaluate_regime_holdout_pass,
            run_regime_holdout,
        )
        from strategies.baseline.sma_crossover import SMACrossover

        parquet = _make_holdout_parquet(tmp_path)
        db_path = tmp_path / "experiments.db"
        env = _make_v2_env_config()

        result = run_regime_holdout(
            dsl=None,
            batch_id=str(uuid.uuid4()),
            parent_run_id=str(uuid.uuid4()),
            strategy_cls=SMACrossover,
            parquet_path=parquet,
            db_path=db_path,
            env_config=env,
        )

        expected = _evaluate_regime_holdout_pass(
            result.metrics, env["splits"]["regime_holdout"]["passing_criteria"]
        )
        assert result.regime_holdout_passed is expected

        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        try:
            row = dict(conn.execute(
                "SELECT regime_holdout_passed FROM runs WHERE run_id = ?",
                (result.run_id,),
            ).fetchone())
        finally:
            conn.close()

        assert row["regime_holdout_passed"] == (1 if expected else 0)

    def test_requires_dsl_or_strategy_cls(self, tmp_path):
        from backtest.engine import run_regime_holdout

        with pytest.raises(ValueError, match="dsl or strategy_cls"):
            run_regime_holdout(
                dsl=None,
                batch_id=str(uuid.uuid4()),
                parent_run_id=str(uuid.uuid4()),
                strategy_cls=None,
                db_path=tmp_path / "unused.db",
                env_config=_make_v2_env_config(),
            )


# ===========================================================================
# 5. Integration: two walk-forward summaries + one holdout linked by parent.
# ===========================================================================


def _make_v2_full_range_parquet(tmp_path: Path) -> Path:
    """Synthesize hourly bars from 2019-12 through 2023-12 so BOTH v2
    train ranges (2020-2021 + 2023) and the 2022 holdout all fit in
    one parquet. The 2019-12 cushion serves SMA(50) warmup before the
    2020-01-01 start.
    """
    import numpy as np
    import pandas as pd

    timestamps = pd.date_range(
        start="2019-12-01", end="2023-12-31 23:00", freq="h", tz="UTC"
    )
    n = len(timestamps)
    t = np.arange(n, dtype=float)
    close = 100.0 + 0.0005 * t + 8.0 * np.sin(t / 300.0)
    openp = close - 0.05
    high = close + 0.5
    low = close - 0.5

    df = pd.DataFrame({
        "open_time_utc": timestamps.astype("datetime64[ms, UTC]"),
        "open": openp,
        "high": high,
        "low": low,
        "close": close,
        "volume": np.full(n, 1000.0),
        "quote_volume": np.full(n, 100_000.0),
        "trade_count": np.arange(n, dtype="int64") + 5000,
        "ingested_at_utc": pd.Timestamp.now(tz="UTC").floor("ms"),
        "source": pd.array(["binance_vision"] * n, dtype="string"),
    })
    df["ingested_at_utc"] = df["ingested_at_utc"].astype("datetime64[ms, UTC]")

    path = tmp_path / "v2_full.parquet"
    df.to_parquet(path, engine="pyarrow", index=False)
    return path


class TestIntegrationTwoSummariesPlusHoldout:
    """Orchestrator pattern per hypothesis, using hand-coded SMACrossover:

        1. run_walk_forward on the 2020-2021 train range → summary row 1
        2. run_walk_forward on the 2023 train range → summary row 2
        3. run_regime_holdout linked to summary 1 via parent_run_id

    The 12m train + 3m test + 3m step default cannot fit in a 12-month
    2023 range, so the integration test uses a shorter 6m/3m/3m config
    so both ranges yield ≥1 sub-window and BOTH summaries get written.
    This locks in the "two v2 ranges → two summaries" invariant without
    depending on the canonical 12m walk-forward configuration.
    """

    def test_two_summaries_and_linked_holdout(self, tmp_path):
        from backtest.engine import run_regime_holdout, run_walk_forward
        from strategies.baseline.sma_crossover import SMACrossover

        parquet = _make_v2_full_range_parquet(tmp_path)
        db_path = tmp_path / "experiments.db"

        wf_cfg = {"train_window_months": 6, "test_window_months": 3, "step_months": 3}

        # --- Summary 1: 2020-2021 range ---
        wf1 = run_walk_forward(
            strategy_cls=SMACrossover,
            strategy_params={"fast_period": 20, "slow_period": 50},
            parquet_path=parquet,
            db_path=db_path,
            walk_forward_config=wf_cfg,
            train_ranges=[(date(2020, 1, 1), date(2021, 12, 31))],
        )

        # --- Summary 2: 2023 range ---
        wf2 = run_walk_forward(
            strategy_cls=SMACrossover,
            strategy_params={"fast_period": 20, "slow_period": 50},
            parquet_path=parquet,
            db_path=db_path,
            walk_forward_config=wf_cfg,
            train_ranges=[(date(2023, 1, 1), date(2023, 12, 31))],
        )

        # --- Holdout linked to summary 1 ---
        ho = run_regime_holdout(
            dsl=None,
            batch_id=str(uuid.uuid4()),
            parent_run_id=wf1.summary_run_id,
            strategy_cls=SMACrossover,
            strategy_params={"fast_period": 20, "slow_period": 50},
            parquet_path=parquet,
            db_path=db_path,
            env_config=_make_v2_env_config(),
        )

        # Inspect registry.
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        try:
            summaries = conn.execute(
                "SELECT * FROM runs WHERE run_type = 'walk_forward_summary' "
                "ORDER BY created_at_utc"
            ).fetchall()
            holdouts = conn.execute(
                "SELECT * FROM runs WHERE run_type = 'regime_holdout'"
            ).fetchall()
            windows = conn.execute(
                "SELECT * FROM runs WHERE run_type = 'walk_forward_window'"
            ).fetchall()
        finally:
            conn.close()

        # Two summaries (one per v2 train range) + exactly one holdout.
        assert len(summaries) == 2
        assert len(holdouts) == 1

        summary_ids = {dict(s)["run_id"] for s in summaries}
        assert wf1.summary_run_id in summary_ids
        assert wf2.summary_run_id in summary_ids

        holdout_row = dict(holdouts[0])
        # Holdout lineage points at summary 1 specifically.
        assert holdout_row["parent_run_id"] == wf1.summary_run_id
        assert holdout_row["run_id"] == ho.run_id

        # Every window points to exactly one of the two summaries.
        window_rows = [dict(w) for w in windows]
        for w in window_rows:
            assert w["parent_run_id"] in summary_ids

        # Summaries' notes record the exact per-call train_ranges
        # provenance — confirming the engine did not merge ranges.
        summary_rows = [dict(s) for s in summaries]
        notes_by_id = {
            s["run_id"]: json.loads(s["notes"]) for s in summary_rows
        }
        assert notes_by_id[wf1.summary_run_id]["train_ranges"] == [
            ["2020-01-01", "2021-12-31"]
        ]
        assert notes_by_id[wf2.summary_run_id]["train_ranges"] == [
            ["2023-01-01", "2023-12-31"]
        ]

        # Hard constraint: NO window touches a 2022 bar.
        for w in window_rows:
            test_start = datetime.strptime(
                w["test_start"], "%Y-%m-%dT%H:%M:%SZ"
            )
            test_end = datetime.strptime(
                w["test_end"], "%Y-%m-%dT%H:%M:%SZ"
            )
            assert test_start.year != 2022
            assert test_end.year != 2022
            train_start = datetime.strptime(
                w["train_start"], "%Y-%m-%dT%H:%M:%SZ"
            )
            train_end = datetime.strptime(
                w["train_end"], "%Y-%m-%dT%H:%M:%SZ"
            )
            assert train_start.year != 2022
            assert train_end.year != 2022


class TestIntegrationDslCompiledEndToEnd:
    """End-to-end with a DSL-COMPILED strategy — not hand-coded. Drives
    ``run_regime_holdout(dsl=...)`` through the full compile path so
    the registry captures ``hypothesis_hash`` + ``strategy_source``.

    Uses the canonical OHLCV and features parquets (skips gracefully
    if either is missing) because the DSL compiler expects a real
    features parquet produced by ``factors.build_features``. This test
    is the one that exercises the full lineage Phase 2B will use:

        DSL → compile_dsl_to_strategy → run_walk_forward (train)
            → run_regime_holdout(dsl=..., parent_run_id=summary)
    """

    FEATURES_PATH = PROJECT_ROOT / "data" / "features" / "btcusdt_1h_features.parquet"

    def _sma_crossover_dsl(self):
        from strategies.dsl import StrategyDSL
        return StrategyDSL.model_validate({
            "name": "sma_crossover_v2_integration",
            "description": "SMA 20/50 crossover for D4 integration test",
            "entry": [{"conditions": [
                {"factor": "sma_20", "op": "crosses_above", "value": "sma_50"}
            ]}],
            "exit": [{"conditions": [
                {"factor": "sma_20", "op": "crosses_below", "value": "sma_50"}
            ]}],
            "position_sizing": "full_equity",
        })

    def test_dsl_compiled_hypothesis_hash_roundtrip(self, tmp_path):
        if not PARQUET_PATH.exists() or not self.FEATURES_PATH.exists():
            pytest.skip("canonical OHLCV or features parquet not available")

        from backtest.engine import run_regime_holdout, run_walk_forward
        from factors.registry import get_registry
        from strategies.dsl import compute_dsl_hash
        from strategies.dsl_compiler import compile_dsl_to_strategy

        dsl = self._sma_crossover_dsl()
        expected_hash = compute_dsl_hash(dsl)

        manifest_dir = tmp_path / "manifests"
        manifest_dir.mkdir()
        db_path = tmp_path / "experiments.db"

        compiled_cls = compile_dsl_to_strategy(
            dsl, registry=get_registry(), manifest_dir=manifest_dir
        )

        # Train on 2020-2021 via compiled strategy.
        wf = run_walk_forward(
            strategy_cls=compiled_cls,
            parquet_path=PARQUET_PATH,
            db_path=db_path,
            walk_forward_config={
                "train_window_months": 6,
                "test_window_months": 3,
                "step_months": 3,
            },
            train_ranges=[(date(2020, 1, 1), date(2021, 12, 31))],
        )

        # Drive run_regime_holdout(dsl=...) — this is the production
        # code path the orchestrator will call. Registry row must
        # capture strategy_source='dsl' and hypothesis_hash=SHA256(dsl).
        batch_id = str(uuid.uuid4())
        ho = run_regime_holdout(
            dsl=dsl,
            batch_id=batch_id,
            parent_run_id=wf.summary_run_id,
            parquet_path=PARQUET_PATH,
            db_path=db_path,
            env_config=_make_v2_env_config(),
            registry=get_registry(),
            manifest_dir=manifest_dir,
        )

        assert ho.hypothesis_hash == expected_hash
        assert ho.batch_id == batch_id
        assert ho.parent_run_id == wf.summary_run_id

        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        try:
            row = dict(conn.execute(
                "SELECT * FROM runs WHERE run_id = ?", (ho.run_id,)
            ).fetchone())
        finally:
            conn.close()

        # DSL-compiled row: must record the canonical hypothesis hash,
        # the DSL source label, and the regime_holdout_passed INT flag.
        assert row["run_type"] == "regime_holdout"
        assert row["hypothesis_hash"] == expected_hash
        assert row["strategy_source"] == "dsl"
        assert row["batch_id"] == batch_id
        assert row["parent_run_id"] == wf.summary_run_id
        assert row["regime_holdout_passed"] in (0, 1)
        # feature_version is captured best-effort — must be a non-empty
        # string (SHA256 hex) or NULL; never an empty string.
        fv = row["feature_version"]
        assert fv is None or (isinstance(fv, str) and len(fv) > 0)


# ===========================================================================
# 6. Migration idempotency + Phase 1 row preservation.
# ===========================================================================


class TestRegistryMigration:
    """``create_table`` must add D4 columns without touching existing rows."""

    def test_idempotent_create_table(self, tmp_path):
        from backtest.experiment_registry import create_table, get_connection

        db_path = tmp_path / "idempotent.db"
        conn = get_connection(db_path)
        try:
            create_table(conn)
            first_cols = {
                r[1] for r in conn.execute("PRAGMA table_info(runs)").fetchall()
            }
            # Running it again must not raise and must not add columns.
            create_table(conn)
            second_cols = {
                r[1] for r in conn.execute("PRAGMA table_info(runs)").fetchall()
            }
        finally:
            conn.close()

        assert first_cols == second_cols
        # D4 columns must be present after the first create_table call.
        for col in (
            "batch_id", "hypothesis_hash", "regime_holdout_passed",
            "lifecycle_state", "feature_version",
        ):
            assert col in first_cols

    def test_phase1_row_preserved_after_migration(self, tmp_path):
        """A DB pre-populated with a Phase 1A-shaped row must survive the
        D4 migration untouched, with new columns defaulting to NULL."""
        from backtest.experiment_registry import create_table, get_connection

        db_path = tmp_path / "legacy.db"

        # Build a minimal Phase 1A schema manually — no D4 columns.
        legacy_sql = """
        CREATE TABLE runs (
            run_id TEXT PRIMARY KEY,
            run_type TEXT NOT NULL DEFAULT 'single_run',
            parent_run_id TEXT,
            strategy_name TEXT NOT NULL,
            strategy_source TEXT NOT NULL,
            git_commit TEXT,
            config_hash TEXT,
            data_snapshot_date TEXT,
            split_version TEXT,
            train_start TEXT,
            train_end TEXT,
            validation_start TEXT,
            validation_end TEXT,
            test_start TEXT,
            test_end TEXT,
            effective_start TEXT,
            warmup_bars INTEGER,
            initial_capital REAL,
            final_capital REAL,
            total_return REAL,
            sharpe_ratio REAL,
            max_drawdown REAL,
            max_drawdown_duration_hours REAL,
            total_trades INTEGER,
            win_rate REAL,
            avg_trade_duration_hours REAL,
            avg_trade_return REAL,
            profit_factor REAL,
            fee_model TEXT,
            notes TEXT,
            review_status TEXT DEFAULT 'pending',
            review_reason TEXT,
            created_at_utc TEXT NOT NULL
        )
        """
        conn = sqlite3.connect(str(db_path))
        conn.executescript(legacy_sql)
        legacy_run_id = str(uuid.uuid4())
        conn.execute(
            "INSERT INTO runs (run_id, run_type, strategy_name, strategy_source, "
            "sharpe_ratio, total_return, fee_model, created_at_utc) "
            "VALUES (?, 'single_run', 'legacy_strategy', 'manual', "
            "1.25, 0.33, 'effective_7bps_per_side', '2024-01-01T00:00:00Z')",
            (legacy_run_id,),
        )
        conn.commit()
        conn.close()

        # Now apply the D4 migration.
        conn = get_connection(db_path)
        try:
            create_table(conn)
            row = dict(conn.execute(
                "SELECT * FROM runs WHERE run_id = ?", (legacy_run_id,)
            ).fetchone())
        finally:
            conn.close()

        # Original values untouched.
        assert row["strategy_name"] == "legacy_strategy"
        assert row["sharpe_ratio"] == 1.25
        assert row["total_return"] == 0.33
        assert row["fee_model"] == "effective_7bps_per_side"

        # New columns default to NULL / 'none'.
        assert row["batch_id"] is None
        assert row["hypothesis_hash"] is None
        assert row["regime_holdout_passed"] is None
        assert row["lifecycle_state"] is None
        # feature_version has a 'none' sentinel default in the schema
        # and is back-filled to NULL on ALTER TABLE ADD COLUMN — either
        # is acceptable (SQLite fills existing rows with the column's
        # default, which is 'none' per MIGRATION_COLUMNS).
        assert row["feature_version"] in ("none", None)


# ===========================================================================
# 7. CLI absence — mechanical self-check mirroring the D4 blueprint gate.
# ===========================================================================


class TestNoHoldoutCli:
    """The regime-holdout execution path must not be reachable from any
    argparse surface. Verified mechanically by string-searching the
    engine module for ``holdout`` references outside docstrings and
    comments."""

    def test_main_has_no_holdout_choice(self):
        """``main()`` argparse choices must not include 'regime-holdout'
        or 'holdout' as a mode."""
        import inspect

        from backtest import engine

        src = inspect.getsource(engine.main)
        assert "holdout" not in src.lower(), (
            "backtest.engine.main() must not expose a CLI surface for "
            "regime holdout — CLAUDE.md hard constraint."
        )

    def test_cli_walk_forward_has_no_holdout_hook(self):
        import inspect

        from backtest import engine

        src = inspect.getsource(engine._cli_walk_forward)
        assert "holdout" not in src.lower(), (
            "_cli_walk_forward must not invoke run_regime_holdout — "
            "holdout is orchestrator-internal only."
        )

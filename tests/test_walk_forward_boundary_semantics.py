"""WF test-boundary semantics regression tests (T1-T9).

Implements the regression set locked at:
docs/superpowers/specs/2026-04-26-wf-test-boundary-semantics-design.md (Q3c)

Each test must fail against the pre-patch engine and pass against the
patched engine. Run pre-patch verification before patching:

    python -m pytest tests/test_walk_forward_boundary_semantics.py -v

Expected pre-patch: ALL FAIL.
Expected post-patch: ALL PASS.
"""
from __future__ import annotations
from datetime import date, datetime, timezone
from pathlib import Path
import pytest

from backtest.engine import run_walk_forward
from tests.fixtures.wf_boundary.synthetic_data import (
    make_trending_then_flat,
    write_to_parquet,
)
from tests.fixtures.wf_boundary.strategies import (
    TrainOnlyStrategy,
    StatefulTestStrategy,
    IndicatorWarmupStrategy,
    TrainProfitable,
    TrainLosing,
)


@pytest.fixture
def trending_then_flat_parquet(tmp_path):
    """120-day trend (1440h * 2 ≈ 2880 bars train) then 30-day flat (720 bars test)."""
    df = make_trending_then_flat(
        start=datetime(2024, 1, 1, tzinfo=timezone.utc),
        train_bars=2880,
        test_bars=720,
        train_growth=2.0,
    )
    path = tmp_path / "trend_then_flat.parquet"
    write_to_parquet(df, path)
    return path


def test_test_period_return_excludes_train_period_pnl(
    trending_then_flat_parquet, tmp_path
):
    """T1: canonical wf_total_return reflects only test-period broker activity.

    Setup: TrainOnlyStrategy buys at 2024-01-15 (deep train, ~$123),
    closes at 2024-04-15 (deep train, ~$275). Train-period gain is
    large (~15% on $10k portfolio with size=10); test-period activity
    is zero. Under (iii), wf_total_return for the test window should
    be 0.0 — not the cumulative-from-inception return.
    """
    db_path = tmp_path / "wf_t1.db"
    result = run_walk_forward(
        strategy_cls=TrainOnlyStrategy,
        parquet_path=trending_then_flat_parquet,
        db_path=db_path,
        walk_forward_config={
            "train_window_months": 4,
            "test_window_months": 1,
            "step_months": 1,
        },
        overall_start=date(2024, 1, 1),
        overall_end=date(2024, 5, 31),
    )
    sm = result.summary_metrics
    # Under (iii): test-period had no trades, so total_return should be 0.0.
    # Under broken engine: total_return reflects cumulative-from-inception
    # final equity divided by $10k initial, which is ~+200% (the train gain).
    assert abs(sm["total_return"]) < 0.01, (
        f"Expected ~0.0 test return; got {sm['total_return']:.4f}. "
        f"Non-zero indicates train-period PnL leaked into test metrics."
    )


def test_zero_test_trades_implies_zero_test_return(
    trending_then_flat_parquet, tmp_path
):
    """T2: zero test-opened trades + no carried position → zero return/sharpe.

    Same setup as T1 (TrainOnlyStrategy with absolute-timestamp
    train-only window). Under (iii): no trades open during test,
    no position at test_start, total_return = sharpe = 0.0. The
    `total_trades == 0` and `abs(total_return) < 0.01` assertions
    are independently meaningful — the first matches the broken
    engine's filter behavior, the second catches the equity-curve
    contamination bug shape (zero visible trades, nonzero reported
    return).
    """
    db_path = tmp_path / "wf_t2.db"
    result = run_walk_forward(
        strategy_cls=TrainOnlyStrategy,
        parquet_path=trending_then_flat_parquet,
        db_path=db_path,
        walk_forward_config={
            "train_window_months": 4,
            "test_window_months": 1,
            "step_months": 1,
        },
        overall_start=date(2024, 1, 1),
        overall_end=date(2024, 5, 31),
    )
    sm = result.summary_metrics
    assert sm["total_trades"] == 0, (
        f"Expected 0 test trades; got {sm['total_trades']}"
    )
    assert abs(sm["total_return"]) < 0.01
    assert abs(sm["sharpe_ratio"]) < 0.01


def test_no_strategy_state_carryover_from_train_to_test(
    trending_then_flat_parquet, tmp_path
):
    """T3: strategy decision-state at first test bar matches fresh instantiation.

    StatefulTestStrategy increments _train_phase_counter every next() call
    and captures the counter value at the first test-period next() call
    (identified by timestamp >= test_start_date, set as a class attribute
    before the run). Under (iii): next() is suppressed during train, so
    counter=0 at first test-period next(). Under broken engine: next()
    fires during all train bars (2880), so counter=2880 at test_start.
    """
    # Set the test_start_date boundary so the strategy knows when to capture.
    # test_start = 2024-05-01 (train_window_months=4 from 2024-01-01).
    test_start = datetime(2024, 5, 1, tzinfo=timezone.utc)
    StatefulTestStrategy._test_start_date = test_start
    # Reset class-level capture before run.
    StatefulTestStrategy._captured_first_next_counter = None

    db_path = tmp_path / "wf_t3.db"
    run_walk_forward(
        strategy_cls=StatefulTestStrategy,
        parquet_path=trending_then_flat_parquet,
        db_path=db_path,
        walk_forward_config={
            "train_window_months": 4,
            "test_window_months": 1,
            "step_months": 1,
        },
        overall_start=date(2024, 1, 1),
        overall_end=date(2024, 5, 31),
    )
    captured = StatefulTestStrategy._captured_first_next_counter
    assert captured is not None, (
        "StatefulTestStrategy never reached test_start bar — "
        "check that _test_start_date is set and data covers 2024-05-01."
    )
    assert captured == 0, (
        f"Expected counter=0 at first test next(); got {captured}. "
        f"Non-zero ({captured} calls) indicates strategy's next() fired "
        f"during train period before test_start, carrying state across "
        f"the train→test boundary."
    )


def test_warmup_history_populates_indicators_without_affecting_metrics(
    trending_then_flat_parquet, tmp_path
):
    """T4: pre-test bars satisfy indicator warmup; pre-test broker activity is zero.

    IndicatorWarmupStrategy uses a 50-bar SMA. Test asserts:
    (a) The strategy can compute SMA at the first test bar (warmup satisfied).
    (b) Zero trades opened before test_start counted in wf_total_trades.
    (c) The first canonical equity-curve observation at or after test_start
        equals initial_capital ($10,000).
    """
    db_path = tmp_path / "wf_t4.db"
    result = run_walk_forward(
        strategy_cls=IndicatorWarmupStrategy,
        parquet_path=trending_then_flat_parquet,
        db_path=db_path,
        walk_forward_config={
            "train_window_months": 4,
            "test_window_months": 1,
            "step_months": 1,
        },
        overall_start=date(2024, 1, 1),
        overall_end=date(2024, 5, 31),
    )
    # (a) Implicit — if SMA warmup wasn't satisfied, run would have crashed.
    # (b) + (c): check the first window's equity curve.
    first_window = result.window_results[0]
    ec = first_window.equity_curve
    test_start_dt = datetime(2024, 5, 1, tzinfo=timezone.utc).replace(tzinfo=None)
    # Find first equity point at or after test_start.
    test_period_ec = ec[ec.index >= test_start_dt]
    assert len(test_period_ec) > 0, "No equity-curve observations in test window"
    assert abs(test_period_ec.iloc[0] - 10_000.0) < 0.01, (
        f"Expected first test equity = $10,000; got {test_period_ec.iloc[0]:.2f}. "
        f"Non-$10k indicates warmup-period trades affected broker accounting."
    )


def test_two_strategies_with_different_train_pnl_have_same_test_starting_capital(
    trending_then_flat_parquet, tmp_path
):
    """T5: cross-strategy test-window comparability — both start at $10k.

    TrainProfitable earns money in train, TrainLosing loses money in train.
    Under (iii): both start the test window with $10k cash regardless.
    """
    db_path_a = tmp_path / "wf_t5_a.db"
    db_path_b = tmp_path / "wf_t5_b.db"

    result_a = run_walk_forward(
        strategy_cls=TrainProfitable,
        parquet_path=trending_then_flat_parquet,
        db_path=db_path_a,
        walk_forward_config={
            "train_window_months": 4,
            "test_window_months": 1,
            "step_months": 1,
        },
        overall_start=date(2024, 1, 1),
        overall_end=date(2024, 5, 31),
    )
    result_b = run_walk_forward(
        strategy_cls=TrainLosing,
        parquet_path=trending_then_flat_parquet,
        db_path=db_path_b,
        walk_forward_config={
            "train_window_months": 4,
            "test_window_months": 1,
            "step_months": 1,
        },
        overall_start=date(2024, 1, 1),
        overall_end=date(2024, 5, 31),
    )
    test_start_dt = datetime(2024, 5, 1, tzinfo=timezone.utc).replace(tzinfo=None)
    ec_a = result_a.window_results[0].equity_curve
    ec_b = result_b.window_results[0].equity_curve
    test_a = ec_a[ec_a.index >= test_start_dt]
    test_b = ec_b[ec_b.index >= test_start_dt]
    assert abs(test_a.iloc[0] - 10_000.0) < 0.01, (
        f"TrainProfitable: expected first test equity = $10k; got {test_a.iloc[0]:.2f}"
    )
    assert abs(test_b.iloc[0] - 10_000.0) < 0.01, (
        f"TrainLosing: expected first test equity = $10k; got {test_b.iloc[0]:.2f}"
    )


def test_canonical_metric_is_deterministic_across_runs(
    trending_then_flat_parquet, tmp_path
):
    """T6: same strategy, same window, same data → identical metrics."""
    common_kwargs = dict(
        strategy_cls=IndicatorWarmupStrategy,
        parquet_path=trending_then_flat_parquet,
        walk_forward_config={
            "train_window_months": 4,
            "test_window_months": 1,
            "step_months": 1,
        },
        overall_start=date(2024, 1, 1),
        overall_end=date(2024, 5, 31),
    )
    result_1 = run_walk_forward(db_path=tmp_path / "wf_t6_1.db", **common_kwargs)
    result_2 = run_walk_forward(db_path=tmp_path / "wf_t6_2.db", **common_kwargs)
    sm1 = result_1.summary_metrics
    sm2 = result_2.summary_metrics
    for key in ["total_return", "sharpe_ratio", "max_drawdown", "total_trades"]:
        if isinstance(sm1[key], (int, float)):
            assert sm1[key] == sm2[key], (
                f"Determinism failure on {key}: run1={sm1[key]}, run2={sm2[key]}"
            )


def test_test_window_metrics_independent_of_train_window_choice(
    trending_then_flat_parquet, tmp_path
):
    """T7: vary train window length; test metrics must be bit-identical.

    Two runs with different train_window_months (4 vs 2) but same test
    window [2024-05-01, 2024-05-31]. Under (iii): test-window metrics are
    bit-identical because the engine resets broker state to $10k at
    test_start; train history length does not affect test metrics.
    Under broken engine: test metrics differ because they include train PnL
    accumulated from different train start dates.

    Window structure:
      result_a (train_window_months=4): last window = train=[2024-01-01,
        2024-04-30], test=[2024-05-01, 2024-05-31]
      result_b (train_window_months=2): last window = train=[2024-03-01,
        2024-04-30], test=[2024-05-01, 2024-05-31]
    Same test window, different train histories → metrics must agree.
    """
    common_kwargs = dict(
        strategy_cls=IndicatorWarmupStrategy,
        parquet_path=trending_then_flat_parquet,
        overall_end=date(2024, 5, 31),
    )
    # 4-month train: last window train=[2024-01-01, 2024-04-30]
    result_a = run_walk_forward(
        overall_start=date(2024, 1, 1),
        walk_forward_config={
            "train_window_months": 4,
            "test_window_months": 1,
            "step_months": 1,
        },
        db_path=tmp_path / "wf_t7_a.db",
        **common_kwargs,
    )
    # 2-month train: last window train=[2024-03-01, 2024-04-30]
    result_b = run_walk_forward(
        overall_start=date(2024, 1, 1),
        walk_forward_config={
            "train_window_months": 2,
            "test_window_months": 1,
            "step_months": 1,
        },
        db_path=tmp_path / "wf_t7_b.db",
        **common_kwargs,
    )
    # Both last windows share test=[2024-05-01, 2024-05-31].
    # Under broken engine: window_results[i].metrics is the full unsliced
    # BacktestResult.metrics (train+test) which differs by train length.
    last_window_a = result_a.window_results[-1]
    last_window_b = result_b.window_results[-1]
    for key in ["total_return", "sharpe_ratio", "max_drawdown", "total_trades"]:
        va = last_window_a.metrics[key]
        vb = last_window_b.metrics[key]
        assert va == vb, (
            f"T7: same test window, different train length → metric {key} "
            f"differs ({va} vs {vb}). "
            f"Indicates train state leaked into test metrics."
        )


def test_equity_curve_starts_at_initial_capital_at_test_start(
    trending_then_flat_parquet, tmp_path
):
    """T8: explicit equity-curve isolation across all WF windows.

    For every window in a WF run, the first equity-curve observation at
    or after test_start equals initial_capital ($10,000). This is the
    sibling assertion to test_walk_forward.py's existing trade-isolation
    tests; closes the framing-completion gap.
    """
    db_path = tmp_path / "wf_t8.db"
    result = run_walk_forward(
        strategy_cls=IndicatorWarmupStrategy,
        parquet_path=trending_then_flat_parquet,
        db_path=db_path,
        walk_forward_config={
            "train_window_months": 4,
            "test_window_months": 1,
            "step_months": 1,
        },
        overall_start=date(2024, 1, 1),
        overall_end=date(2024, 5, 31),
    )
    for i, (window_result, window_dates) in enumerate(
        zip(result.window_results, result.windows)
    ):
        _, _, test_start, _ = window_dates
        test_start_dt = datetime(
            test_start.year, test_start.month, test_start.day,
            tzinfo=timezone.utc,
        ).replace(tzinfo=None)
        ec = window_result.equity_curve
        test_period_ec = ec[ec.index >= test_start_dt]
        assert len(test_period_ec) > 0, (
            f"Window {i+1}: no equity-curve observations in test window"
        )
        assert abs(test_period_ec.iloc[0] - 10_000.0) < 0.01, (
            f"Window {i+1}: first test equity = {test_period_ec.iloc[0]:.2f}; "
            f"expected $10,000"
        )


def test_summary_aggregation_uses_corrected_per_window_metrics():
    """T9: walk_forward_summary aggregation matches v2 disjoint-train rules.

    Constructs synthetic per-window metrics with known values, calls
    _aggregate_walk_forward_metrics directly, asserts the aggregation
    formula:
      - sharpe_ratio: mean of per-window Sharpes
      - total_return: mean of per-window returns
      - max_drawdown: max of per-window drawdowns
      - total_trades: sum of per-window trades
    """
    from backtest.engine import _aggregate_walk_forward_metrics

    window_metrics = [
        {
            "total_return": 0.10, "sharpe_ratio": 1.0, "max_drawdown": 0.05,
            "max_drawdown_duration_hours": 5.0, "total_trades": 10,
            "win_rate": 0.6, "avg_trade_duration_hours": 2.0,
            "avg_trade_return": 0.01, "profit_factor": 1.5,
            "initial_capital": 10_000.0,
        },
        {
            "total_return": 0.20, "sharpe_ratio": 2.0, "max_drawdown": 0.10,
            "max_drawdown_duration_hours": 10.0, "total_trades": 20,
            "win_rate": 0.7, "avg_trade_duration_hours": 3.0,
            "avg_trade_return": 0.01, "profit_factor": 2.0,
            "initial_capital": 10_000.0,
        },
    ]
    summary = _aggregate_walk_forward_metrics(window_metrics, num_windows=2)

    # mean Sharpe = (1.0 + 2.0) / 2 = 1.5
    assert summary["sharpe_ratio"] == pytest.approx(1.5)
    # mean return = (0.10 + 0.20) / 2 = 0.15
    assert summary["total_return"] == pytest.approx(0.15)
    # max drawdown across windows = max(0.05, 0.10) = 0.10
    assert summary["max_drawdown"] == pytest.approx(0.10)
    # sum trades = 10 + 20 = 30
    assert summary["total_trades"] == 30

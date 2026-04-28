"""Backtest engine: single-run (Phase 1A) and walk-forward (Phase 1B).

Orchestrates a complete backtest: loads data, configures Cerebro,
runs the strategy, collects trade artifacts with correct time
semantics, computes metrics, and logs to the experiment registry.

Usage:
    # Single-run (Phase 1A):
    python -m backtest.engine --strategy sma_crossover \\
        --start 2024-01-01 --end 2024-12-31

    # Walk-forward (Phase 1B):
    python -m backtest.engine --strategy sma_crossover --mode walk-forward

Trade time semantics (CRITICAL):
    - entry_signal_time_utc: bar N close time — when signal was computed
    - entry_time_utc: bar N+1 open time — when order actually filled
    - exit_signal_time_utc: bar M close time — when exit signal was computed
    - exit_time_utc: bar M+1 open time — when close order actually filled

These are enforced by recording order.created.dt (signal bar) and
order.executed.dt (fill bar) directly from Backtrader's order lifecycle.
"""

from __future__ import annotations

import argparse
import calendar
import json
import logging
import sys
import uuid
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import backtrader as bt
import numpy as np
import pandas as pd

from backtest.bt_parquet_feed import ParquetFeed
from backtest.execution_model import configure_cerebro
from backtest.metrics import compute_all_metrics
from backtest.slippage import load_execution_config

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = PROJECT_ROOT / "data" / "results"

# ---------------------------------------------------------------------------
# Strategy registry — maps names to classes
# ---------------------------------------------------------------------------

STRATEGY_REGISTRY: dict[str, type[bt.Strategy]] = {}


def register_strategy(cls: type[bt.Strategy]) -> type[bt.Strategy]:
    """Register a strategy class by its STRATEGY_NAME.

    Raises:
        ValueError: If cls has no STRATEGY_NAME or if a different class
            is already registered under the same name.
    """
    name = getattr(cls, "STRATEGY_NAME", None)
    if name is None:
        raise ValueError(f"{cls.__name__} must define STRATEGY_NAME")

    existing = STRATEGY_REGISTRY.get(name)
    if existing is not None and existing is not cls:
        raise ValueError(
            f"Strategy name conflict: '{name}' already registered by "
            f"{existing.__name__}, cannot register {cls.__name__}"
        )

    STRATEGY_REGISTRY[name] = cls
    return cls


def _ensure_strategies_loaded() -> None:
    """Import and register all baseline strategies.

    Scans strategies/baseline/ for Python modules and registers
    concrete BaseStrategy subclasses. Skips:
    - The BaseStrategy abstract base class itself
    - Classes with STRATEGY_NAME == "unnamed" (unoverridden default)
    - Non-BaseStrategy classes

    Logs errors explicitly if a module fails to import.
    """
    if STRATEGY_REGISTRY:
        return

    import importlib
    import pkgutil

    from strategies.template import BaseStrategy

    import strategies.baseline as baseline_pkg

    for _importer, modname, ispkg in pkgutil.iter_modules(baseline_pkg.__path__):
        try:
            module = importlib.import_module(f"strategies.baseline.{modname}")
        except Exception:
            logger.exception("Failed to import strategy module: %s", modname)
            continue

        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (
                isinstance(attr, type)
                and issubclass(attr, BaseStrategy)
                and attr is not BaseStrategy
                and getattr(attr, "STRATEGY_NAME", "unnamed") != "unnamed"
            ):
                register_strategy(attr)


# ---------------------------------------------------------------------------
# Trade collector — Backtrader analyzer for trade artifact extraction
# ---------------------------------------------------------------------------


class TradeCollector(bt.Analyzer):
    """Collects completed trades with correct signal/fill time semantics.

    Phase 1A limitation: only supports single-position long/flat strategies.
    Does NOT support partial exits, scaling in/out, short positions, or
    overlapping positions. If used with such strategies, trade matching
    will silently produce incorrect artifacts.

    For each completed round-trip trade, records:
    - Signal times (order.created.dt) — when the signal was generated
    - Fill times (order.executed.dt) — when the order was actually filled
    - Fill prices, volumes, commissions, PnL

    This analyzer attaches to the strategy and listens to order and trade
    notifications via Backtrader's analyzer lifecycle.
    """

    def __init__(self) -> None:
        super().__init__()
        self._open_orders: dict[int, dict[str, Any]] = {}
        self._trades: list[dict[str, Any]] = []
        self._trade_counter = 0

    def notify_order(self, order: bt.order.Order) -> None:
        """Track order lifecycle for signal/fill time extraction.

        When an order is completed, we record its created.dt (signal time)
        and executed.dt (fill time). These are then matched to trades.
        """
        if order.status != order.Completed:
            return

        # Convert Backtrader float datetimes to Python datetimes
        signal_dt = bt.num2date(order.created.dt)
        fill_dt = bt.num2date(order.executed.dt)

        fill_info = {
            "signal_time": signal_dt,
            "fill_time": fill_dt,
            "price": order.executed.price,
            "size": order.executed.size,
            "comm": order.executed.comm,
            "value": order.executed.value,
            "is_buy": order.isbuy(),
            "ref": order.ref,
        }

        # Store as entry or exit based on direction
        if order.isbuy():
            # Opening a long position
            self._open_orders[order.ref] = fill_info
        else:
            # Closing — find the matching entry
            # For simple strategies, there's only one open position
            self._record_trade(fill_info)

    def _record_trade(self, exit_info: dict[str, Any]) -> None:
        """Match exit fill to most recent entry fill and record trade."""
        if not self._open_orders:
            logger.warning(
                "Exit order %d with no matching entry — orphan sell",
                exit_info["ref"],
            )
            return

        # Pop the oldest entry (FIFO matching for simple strategies)
        entry_ref = min(self._open_orders.keys())
        entry_info = self._open_orders.pop(entry_ref)

        size = abs(entry_info["size"])
        entry_value = size * entry_info["price"]
        exit_value = size * exit_info["price"]

        # PnL: (exit - entry) * size - commissions
        gross_pnl = exit_value - entry_value
        total_comm = entry_info["comm"] + exit_info["comm"]
        net_pnl = gross_pnl - total_comm
        pnl_pct = net_pnl / entry_value if entry_value > 0 else 0.0

        # Volume of fill bars — need to look up from data
        data = self.strategy.data
        entry_bar_vol = self._get_bar_volume(data, entry_info["fill_time"])
        exit_bar_vol = self._get_bar_volume(data, exit_info["fill_time"])

        self._trade_counter += 1
        trade_record = {
            "trade_id": self._trade_counter,
            "entry_signal_time_utc": entry_info["signal_time"].strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            ),
            "entry_time_utc": entry_info["fill_time"].strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            ),
            "entry_price": entry_info["price"],
            "entry_bar_volume": entry_bar_vol,
            "exit_signal_time_utc": exit_info["signal_time"].strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            ),
            "exit_time_utc": exit_info["fill_time"].strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            ),
            "exit_price": exit_info["price"],
            "exit_bar_volume": exit_bar_vol,
            "size": size,
            "entry_commission": entry_info["comm"],
            "exit_commission": exit_info["comm"],
            "total_commission": total_comm,
            "pnl": net_pnl,
            "pnl_pct": pnl_pct,
        }

        self._trades.append(trade_record)

    def _get_bar_volume(self, data: bt.feeds.DataBase, fill_dt: datetime) -> float:
        """Look up the volume of the bar at the given fill datetime.

        Args:
            data: Backtrader data feed.
            fill_dt: Fill datetime (naive, from bt.num2date).

        Returns:
            Volume of the bar, or 0.0 if not found.
        """
        # Search backwards from current position for matching datetime
        for i in range(len(data)):
            bar_dt = data.datetime.datetime(-i)
            if bar_dt == fill_dt:
                return float(data.volume[-i])
        return 0.0

    def get_trades(self) -> list[dict[str, Any]]:
        """Return all completed trades."""
        return list(self._trades)


# ---------------------------------------------------------------------------
# Equity curve collector
# ---------------------------------------------------------------------------


class EquityCurveCollector(bt.Analyzer):
    """Records portfolio value at each bar for equity curve construction.

    Starts recording only after the warmup period (i.e., once next()
    is being called). The resulting equity curve is used for metrics
    computation (Sharpe, drawdown, etc.).
    """

    def __init__(self) -> None:
        super().__init__()
        self._equity: list[tuple[datetime, float]] = []

    def prenext(self) -> None:
        """Skip warmup bars — do not record equity during prenext phase.

        Backtrader's default Analyzer.prenext() calls next(), which would
        include warmup bars in the equity curve. We override to prevent
        that, ensuring metrics are computed only on the post-warmup period.
        """

    def next(self) -> None:
        """Record portfolio value on each bar (post-warmup only)."""
        dt = self.strategy.data.datetime.datetime(0)
        value = self.strategy.broker.getvalue()
        self._equity.append((dt, value))

    def get_equity_curve(self) -> pd.Series:
        """Return datetime-indexed Series of portfolio values.

        Returns:
            pd.Series with datetime index and float values.
        """
        if not self._equity:
            return pd.Series(dtype=float)
        dts, vals = zip(*self._equity)
        return pd.Series(vals, index=pd.DatetimeIndex(dts), dtype=float)


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------


@dataclass
class BacktestResult:
    """Container for single-run backtest results."""

    run_id: str
    strategy_name: str
    trades: list[dict[str, Any]]
    equity_curve: pd.Series
    metrics: dict[str, Any]
    trade_csv_path: Path | None
    warmup_bars: int
    effective_start: datetime | None
    start_date: datetime
    end_date: datetime
    params: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Engine core
# ---------------------------------------------------------------------------


def run_backtest(
    strategy_cls: type[bt.Strategy],
    start_date: datetime,
    end_date: datetime,
    strategy_params: dict[str, Any] | None = None,
    parquet_path: str | Path | None = None,
    cash: float = 10_000.0,
    write_registry: bool = True,
    db_path: Path | None = None,
) -> BacktestResult:
    """Execute a single-run backtest.

    This is the main entry point for Phase 1A backtesting. It:
    1. Loads data from the parquet feed
    2. Configures Cerebro with the execution model
    3. Runs the strategy
    4. Extracts trades with correct signal/fill time semantics
    5. Computes metrics on the post-warmup equity curve
    6. Saves trade log CSV
    7. Optionally writes to the experiment registry

    Args:
        strategy_cls: Backtrader Strategy class to run.
        start_date: Start of backtest date range (inclusive).
        end_date: End of backtest date range (inclusive).
        strategy_params: Dict of strategy parameters (passed to addstrategy).
        parquet_path: Path to OHLCV parquet file. Uses default if None.
        cash: Initial capital (default $10,000).
        write_registry: Whether to log the run to experiments.db.
        db_path: Path to experiment registry DB. Uses default if None.

    Returns:
        BacktestResult with trades, equity curve, metrics, and paths.
    """
    run_id = str(uuid.uuid4())
    strategy_params = strategy_params or {}

    # 1. Load data
    logger.info(
        "Starting backtest: strategy=%s, range=[%s, %s], run_id=%s",
        getattr(strategy_cls, "STRATEGY_NAME", strategy_cls.__name__),
        start_date.date(),
        end_date.date(),
        run_id[:8],
    )

    feed_kwargs = {"fromdate": start_date, "todate": end_date}
    if parquet_path:
        feed_kwargs["path"] = parquet_path
    feed = ParquetFeed.from_parquet(**feed_kwargs)

    # 2. Configure Cerebro
    config = load_execution_config()
    cerebro = bt.Cerebro()
    cerebro.adddata(feed)
    cost_model = configure_cerebro(cerebro, config=config, cash=cash)

    # 3. Add strategy and analyzers
    cerebro.addstrategy(strategy_cls, **strategy_params)
    cerebro.addanalyzer(TradeCollector, _name="trade_collector")
    cerebro.addanalyzer(EquityCurveCollector, _name="equity_curve")

    # 4. Run
    results = cerebro.run()
    strat = results[0]

    # 5. Extract results
    warmup_bars = getattr(strat, "WARMUP_BARS", 0)
    trade_collector = strat.analyzers.trade_collector
    equity_collector = strat.analyzers.equity_curve

    trades = trade_collector.get_trades()
    equity_curve = equity_collector.get_equity_curve()

    # Determine effective_start (first bar after warmup)
    effective_start = None
    if len(equity_curve) > 0:
        effective_start = equity_curve.index[0].to_pydatetime()

    # 6. Compute metrics on post-warmup equity curve
    metrics = compute_all_metrics(equity_curve, trades, cash)

    # 7. Save trade log CSV
    trade_csv_path = _save_trade_csv(run_id, trades)

    # 8. Write to registry
    if write_registry:
        _write_to_registry(
            run_id=run_id,
            strategy_cls=strategy_cls,
            strategy_params=strategy_params,
            start_date=start_date,
            end_date=end_date,
            effective_start=effective_start,
            warmup_bars=warmup_bars,
            cost_model=cost_model,
            metrics=metrics,
            db_path=db_path,
        )

    result = BacktestResult(
        run_id=run_id,
        strategy_name=getattr(strat, "STRATEGY_NAME", strategy_cls.__name__),
        trades=trades,
        equity_curve=equity_curve,
        metrics=metrics,
        trade_csv_path=trade_csv_path,
        warmup_bars=warmup_bars,
        effective_start=effective_start,
        start_date=start_date,
        end_date=end_date,
        params=strategy_params,
    )

    logger.info(
        "Backtest complete: %d trades, return=%.4f, sharpe=%.3f, csv=%s",
        metrics["total_trades"],
        metrics["total_return"],
        metrics["sharpe_ratio"],
        trade_csv_path,
    )

    return result


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _save_trade_csv(run_id: str, trades: list[dict[str, Any]]) -> Path | None:
    """Save trade log to CSV file.

    Args:
        run_id: UUID for this run.
        trades: List of trade dicts.

    Returns:
        Path to the saved CSV, or None if no trades.
    """
    if not trades:
        logger.info("No trades to save")
        return None

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = RESULTS_DIR / f"trades_{run_id}.csv"

    df = pd.DataFrame(trades)
    df.to_csv(csv_path, index=False)
    logger.info("Trade log saved: %s (%d trades)", csv_path, len(trades))
    return csv_path


def _write_to_registry(
    run_id: str,
    strategy_cls: type[bt.Strategy],
    strategy_params: dict[str, Any],
    start_date: datetime,
    end_date: datetime,
    effective_start: datetime | None,
    warmup_bars: int,
    cost_model: Any,
    metrics: dict[str, Any],
    db_path: Path | None = None,
    *,
    run_type: str = "single_run",
    parent_run_id: str | None = None,
    train_start: datetime | None = None,
    train_end: datetime | None = None,
    notes: str | None = None,
    batch_id: str | None = None,
    hypothesis_hash: str | None = None,
    regime_holdout_passed: bool | None = None,
    lifecycle_state: str | None = None,
    strategy_source: str = "manual",
    feature_version: str | None = None,
) -> None:
    """Write run results to the experiment registry.

    Defaults preserve Phase 1A single-run semantics:
    - run_type="single_run", parent_run_id=None
    - test_start/test_end = engine's date range (start_date/end_date)
    - train_start/train_end/validation_start/validation_end = NULL
    - batch_id/hypothesis_hash/regime_holdout_passed/lifecycle_state = NULL

    For walk-forward windows, callers pass:
    - run_type="walk_forward_window"
    - parent_run_id=<summary_uuid>
    - train_start/train_end from the window definition
    - start_date/end_date set to the window's test dates

    For Phase 2A D4 regime holdout, callers additionally pass:
    - run_type="regime_holdout"
    - parent_run_id=<walk_forward_summary_uuid>
    - batch_id, hypothesis_hash
    - regime_holdout_passed (bool; stored as SQLite INTEGER 0/1)

    Args:
        run_id: UUID for this run.
        strategy_cls: Strategy class.
        strategy_params: Strategy params dict.
        start_date: Test start date (used as test_start in registry).
        end_date: Test end date (used as test_end in registry).
        effective_start: First bar after warmup.
        warmup_bars: Number of warmup bars.
        cost_model: ConstantSlippage instance.
        metrics: Computed metrics dict.
        db_path: Path to DB (uses default if None).
        run_type: Registry run type (default "single_run").
        parent_run_id: Parent run UUID for walk-forward windows.
        train_start: Train window start (NULL for Phase 1A).
        train_end: Train window end (NULL for Phase 1A).
        notes: Custom notes string. Falls back to JSON params if None.
        batch_id: Phase 2B batch UUID (NULL for pre-batch runs).
        hypothesis_hash: DSL canonical hash (NULL for hand-written
            baselines; set for DSL-compiled runs).
        regime_holdout_passed: Regime-holdout AND gate outcome. NULL
            means "holdout did not run for this row" (applies to every
            run_type other than ``"regime_holdout"``).
        lifecycle_state: D8 lifecycle marker. Written by the D8
            orchestrator only; D4 always passes None.
        strategy_source: ``"manual"`` for hand-coded strategies,
            ``"dsl"`` for DSL-compiled strategies.
        feature_version: FactorRegistry version hash for DSL-compiled
            runs. None preserves the default 'none' sentinel.
    """
    from backtest.experiment_registry import (
        create_table,
        get_connection,
        insert_run,
    )

    strategy_name = getattr(strategy_cls, "STRATEGY_NAME", strategy_cls.__name__)

    if notes is None:
        notes = json.dumps(strategy_params) if strategy_params else None

    run_data = {
        "run_id": run_id,
        "run_type": run_type,
        "parent_run_id": parent_run_id,
        "strategy_name": strategy_name,
        "strategy_source": strategy_source,
        "test_start": start_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "test_end": end_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "effective_start": (
            effective_start.strftime("%Y-%m-%dT%H:%M:%SZ")
            if effective_start
            else None
        ),
        "warmup_bars": warmup_bars,
        "train_start": (
            train_start.strftime("%Y-%m-%dT%H:%M:%SZ")
            if train_start
            else None
        ),
        "train_end": (
            train_end.strftime("%Y-%m-%dT%H:%M:%SZ")
            if train_end
            else None
        ),
        "validation_start": None,
        "validation_end": None,
        "fee_model": cost_model.fee_model_label,
        "initial_capital": metrics.get("initial_capital"),
        "final_capital": metrics.get("final_capital"),
        "total_return": metrics.get("total_return"),
        "sharpe_ratio": metrics.get("sharpe_ratio"),
        "max_drawdown": metrics.get("max_drawdown"),
        "max_drawdown_duration_hours": metrics.get("max_drawdown_duration_hours"),
        "total_trades": metrics.get("total_trades"),
        "win_rate": metrics.get("win_rate"),
        "avg_trade_duration_hours": metrics.get("avg_trade_duration_hours"),
        "avg_trade_return": metrics.get("avg_trade_return"),
        "profit_factor": metrics.get("profit_factor"),
        "notes": notes,
        "batch_id": batch_id,
        "hypothesis_hash": hypothesis_hash,
        "regime_holdout_passed": (
            None if regime_holdout_passed is None
            else (1 if regime_holdout_passed else 0)
        ),
        "lifecycle_state": lifecycle_state,
    }
    if feature_version is not None:
        run_data["feature_version"] = feature_version

    conn = get_connection(db_path)
    try:
        create_table(conn)
        insert_run(conn, run_data)
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Walk-forward (Phase 1B)
# ---------------------------------------------------------------------------


def _add_months(d: date, months: int) -> date:
    """Add calendar months to a date, pinning to the 1st of the month.

    Args:
        d: Starting date (should be 1st of month for walk-forward).
        months: Number of months to add.

    Returns:
        New date with months added.
    """
    total_months = (d.year * 12 + d.month - 1) + months
    year = total_months // 12
    month = total_months % 12 + 1
    day = min(d.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def generate_walk_forward_windows(
    overall_start: date,
    overall_end: date,
    train_months: int = 12,
    test_months: int = 3,
    step_months: int = 3,
) -> list[tuple[date, date, date, date]]:
    """Generate rolling walk-forward window date tuples.

    Each window is (train_start, train_end, test_start, test_end).
    Windows roll forward by step_months. A window is included only
    if its test_end falls on or before overall_end.

    Args:
        overall_start: First possible train_start (1st of month).
        overall_end: Last possible test_end (last of month).
        train_months: Length of training window in months.
        test_months: Length of test window in months.
        step_months: Step size in months between consecutive windows.

    Returns:
        List of (train_start, train_end, test_start, test_end) tuples.
    """
    windows = []
    train_start = overall_start

    while True:
        test_start = _add_months(train_start, train_months)
        train_end = test_start - timedelta(days=1)
        test_end = _add_months(test_start, test_months) - timedelta(days=1)

        if test_end > overall_end:
            break

        windows.append((train_start, train_end, test_start, test_end))
        train_start = _add_months(train_start, step_months)

    return windows


@dataclass
class WalkForwardResult:
    """Container for walk-forward backtest results."""

    summary_run_id: str
    window_results: list[BacktestResult]
    summary_metrics: dict[str, Any]
    windows: list[tuple[date, date, date, date]]


def _load_v2_train_ranges(env_config: dict[str, Any]) -> list[tuple[date, date]]:
    """Read disjoint training ranges from v2 ``splits.train_windows``.

    Returns a list of ``(start, end)`` date tuples. Raises if the config
    is not v2-shaped — callers should provide an explicit override
    (``overall_start``/``overall_end`` or ``train_ranges``) when running
    against legacy or test fixtures.
    """
    splits = env_config.get("splits", {})
    raw = splits.get("train_windows")
    if not raw:
        raise ValueError(
            "environments.yaml does not contain splits.train_windows; "
            "expected v2 schema. Pass overall_start/overall_end or "
            "train_ranges to override."
        )
    ranges: list[tuple[date, date]] = []
    for entry in raw:
        if len(entry) != 2:
            raise ValueError(
                f"train_windows entries must be [start, end]; got {entry!r}"
            )
        ranges.append(
            (date.fromisoformat(entry[0]), date.fromisoformat(entry[1]))
        )
    return ranges


class _TestStartGatedStrategy:
    """Factory for strategy wrappers that suppress hooks before test_start.

    Per docs/decisions/WF_TEST_BOUNDARY_SEMANTICS.md Q2 (iii):
    no user-strategy decision logic, order submission, broker mutation,
    or decision-state mutation may occur before test_start. Indicator/
    factor warmup state is allowed to populate during the warmup span.

    This wrapper enforces (iii) via explicit timestamp comparison
    rather than relying on Backtrader's minperiod alignment, which
    is fragile (minperiod-suppressed next() can still fire 1+ bars
    before test_start under some buffer/strategy combinations).

    Note: when nextstart() fires post-test_start, the wrapper's
    nextstart() delegates to super().nextstart() which (by Backtrader
    convention) invokes next() once. The wrapper's next() will
    redundantly verify the timestamp on that first call. This is a
    benign double-check; do not optimize away the next() timestamp
    check, as that would create a bypass path through nextstart().
    """

    @staticmethod
    def make_wrapped_class(
        base_cls: type[bt.Strategy],
        test_start_dt: datetime,
    ) -> type[bt.Strategy]:
        """Return a subclass of base_cls with next/prenext/nextstart gated.

        The subclass preserves base_cls's params, class attributes, and
        Backtrader strategy registration behavior. If direct subclassing
        is found to break param handling (Backtrader uses a metaclass
        for params), switch to a tested wrapper/factory pattern that
        preserves Backtrader semantics — silent param-handling breakage
        would invalidate any test that uses parameterized strategies.
        """
        # Backtrader uses naive datetimes internally (parquet feed strips tz).
        test_start_naive = test_start_dt.replace(tzinfo=None)

        class GatedStrategy(base_cls):
            """Subclass with test_start gating."""

            def _is_pre_test(self) -> bool:
                """True if current bar is before test_start."""
                cur_dt = self.data.datetime.datetime(0)
                return cur_dt < test_start_naive

            def prenext(self) -> None:
                # Always suppress — prenext is by definition pre-warmup.
                # Both pre-test_start (suppressed) and post-test_start-
                # pre-warmup (impossible since test_start is post-warmup
                # given correct WARMUP_BARS) are handled by suppression.
                return

            def nextstart(self) -> None:
                # The first call where minperiod is satisfied. May fire
                # before test_start if minperiod aligns earlier. Suppress
                # if pre-test; delegate to parent's nextstart (which by
                # Backtrader convention calls next() once) if not.
                if self._is_pre_test():
                    return
                # Temporarily reset __class__ to base_cls so that
                # type(self) inside base_cls.nextstart() resolves to
                # base_cls, not GatedStrategy. This ensures that
                # strategies using type(self) for class-attribute writes
                # (e.g., class-level capture variables) write to the
                # correct class rather than to GatedStrategy.
                _saved_class = self.__class__
                self.__class__ = base_cls
                try:
                    base_cls.nextstart(self)
                finally:
                    self.__class__ = _saved_class

            def next(self) -> None:
                if self._is_pre_test():
                    return
                # Temporarily reset __class__ to base_cls so that
                # type(self) inside base_cls.next() resolves to base_cls,
                # not GatedStrategy. This ensures that strategies using
                # type(self) for class-attribute writes (e.g., class-level
                # capture variables) write to the correct class rather
                # than to GatedStrategy.
                _saved_class = self.__class__
                self.__class__ = base_cls
                try:
                    base_cls.next(self)
                finally:
                    self.__class__ = _saved_class

        GatedStrategy.__name__ = f"Gated_{base_cls.__name__}"
        GatedStrategy.STRATEGY_NAME = getattr(base_cls, "STRATEGY_NAME", base_cls.__name__)
        GatedStrategy.WARMUP_BARS = getattr(base_cls, "WARMUP_BARS", 0)
        return GatedStrategy


def run_walk_forward(
    strategy_cls: type[bt.Strategy],
    strategy_params: dict[str, Any] | None = None,
    parquet_path: str | Path | None = None,
    cash: float = 10_000.0,
    db_path: Path | None = None,
    walk_forward_config: dict[str, int] | None = None,
    overall_start: date | None = None,
    overall_end: date | None = None,
    train_ranges: list[tuple[date, date]] | None = None,
) -> WalkForwardResult:
    """Execute walk-forward backtesting across rolling windows.

    Per Q2 (iii) of WF_TEST_BOUNDARY_SEMANTICS decision:
    each window wraps the strategy class in a _TestStartGatedStrategy
    that suppresses next/prenext/nextstart before test_start. The data
    feed loads [train_start, test_end] (unchanged from prior behavior),
    but the wrapper's explicit timestamp comparison ensures no
    user-strategy decision logic, order submission, broker mutation,
    or decision-state mutation occurs pre-test_start. At the first
    non-suppressed next() call (= test_start), the broker holds $10k,
    no positions are open, and custom decision-state fields are at
    their __init__ values. Test-window metrics (return, Sharpe,
    drawdown, trades) reflect only test-period activity by construction.

    For Phase 1B baselines, no parameter optimization is performed.
    The train window is loaded into the data feed (so indicators warm
    up across the full pre-test history), but the wrapper suppresses
    decision logic until test_start. The post-hoc equity-curve trim
    isolates the canonical metric slice from the constant-equity
    warmup observations.

    Range resolution precedence (highest first):
        1. Explicit ``train_ranges`` argument (list of disjoint ranges).
        2. Explicit ``overall_start`` + ``overall_end`` (single range,
           preserved for Phase 1B back-compat).
        3. v2 ``splits.train_windows`` from environments.yaml. Sub-windows
           are generated independently from each range and concatenated;
           a range too short to fit (train_months + test_months) yields
           zero sub-windows and is skipped silently.

    Per-range sub-windows are concatenated into a single window list.
    A single ``walk_forward_summary`` row aggregates metrics across all
    sub-windows per the v2 train-summary aggregation rules
    (mean Sharpe/return, max DD, summed trade count). Per-window equity
    curves are NEVER stitched into a continuous series across disjoint
    ranges — the 2020-2021 and 2023 ranges are independent observations.

    Args:
        strategy_cls: Backtrader Strategy class to run.
        strategy_params: Strategy parameters (passed to each window run).
        parquet_path: Path to OHLCV parquet file. Uses default if None.
        cash: Initial capital per window (default $10,000).
        db_path: Path to experiment registry DB. Uses default if None.
        walk_forward_config: Override window params dict with keys:
            train_months, test_months, step_months.
        overall_start: Override start date for window generation
            (single-range path; back-compat with Phase 1B tests).
        overall_end: Override end date for window generation
            (single-range path; back-compat with Phase 1B tests).
        train_ranges: Explicit list of (start, end) date tuples for v2
            disjoint-range execution. Takes precedence over the env config.

    Returns:
        WalkForwardResult with per-window results and summary.
    """
    import yaml

    strategy_params = strategy_params or {}
    strategy_name = getattr(strategy_cls, "STRATEGY_NAME", strategy_cls.__name__)

    # Load config from environments.yaml (with overrides)
    env_path = PROJECT_ROOT / "config" / "environments.yaml"
    with open(env_path) as f:
        env_config = yaml.safe_load(f)

    wf_config = env_config.get("walk_forward", {})
    if walk_forward_config:
        wf_config.update(walk_forward_config)

    train_months = wf_config.get("train_window_months", 12)
    test_months = wf_config.get("test_window_months", 3)
    step_months = wf_config.get("step_months", 3)

    # Resolve training ranges (precedence: train_ranges > overall_*  > config)
    if train_ranges is not None:
        ranges: list[tuple[date, date]] = list(train_ranges)
    elif overall_start is not None and overall_end is not None:
        ranges = [(overall_start, overall_end)]
    else:
        ranges = _load_v2_train_ranges(env_config)

    # Generate sub-windows per range and concatenate. A range too short
    # to fit (train + test) months produces zero sub-windows.
    windows: list[tuple[date, date, date, date]] = []
    for r_start, r_end in ranges:
        sub = generate_walk_forward_windows(
            r_start, r_end, train_months, test_months, step_months,
        )
        windows.extend(sub)

    if not windows:
        raise ValueError(
            f"No walk-forward windows fit in train_ranges {ranges} with "
            f"train={train_months}m, test={test_months}m, step={step_months}m"
        )

    logger.info(
        "Walk-forward: %d windows, %s strategy, train=%dm test=%dm step=%dm",
        len(windows), strategy_name, train_months, test_months, step_months,
    )

    # Pre-generate summary run_id — windows point to this
    summary_run_id = str(uuid.uuid4())

    # Load cost model once for registry writes
    config = load_execution_config()
    from backtest.execution_model import ConstantSlippage
    cost_model = ConstantSlippage.from_config(config)

    window_results: list[BacktestResult] = []
    window_metrics_list: list[dict[str, Any]] = []

    for i, (w_train_start, w_train_end, w_test_start, w_test_end) in enumerate(windows):
        logger.info(
            "  Window %d/%d: train=[%s, %s] test=[%s, %s]",
            i + 1, len(windows),
            w_train_start, w_train_end, w_test_start, w_test_end,
        )

        # Convert dates to UTC datetimes for run_backtest (unchanged)
        data_start_dt = datetime(
            w_train_start.year, w_train_start.month, w_train_start.day,
            tzinfo=timezone.utc,
        )
        data_end_dt = datetime(
            w_test_end.year, w_test_end.month, w_test_end.day,
            hour=23, tzinfo=timezone.utc,
        )
        test_start_dt = datetime(
            w_test_start.year, w_test_start.month, w_test_start.day,
            tzinfo=timezone.utc,
        )

        # Q2 (iii) enforcement via gated wrapper:
        # wrap the strategy class so its next/prenext/nextstart are
        # suppressed before test_start. Decision logic, orders, broker
        # mutation, and decision-state mutation are all blocked pre-test;
        # indicator warmup state populates normally.
        gated_cls = _TestStartGatedStrategy.make_wrapped_class(
            strategy_cls, test_start_dt
        )

        # Run engine on FULL train+test span (unchanged data range);
        # the wrapper enforces test-period-only semantics via explicit
        # timestamp comparison in next/prenext/nextstart, not via
        # data-range manipulation.
        result = run_backtest(
            strategy_cls=gated_cls,
            start_date=data_start_dt,
            end_date=data_end_dt,
            strategy_params=strategy_params,
            parquet_path=parquet_path,
            cash=cash,
            write_registry=False,
        )

        # Canonical-metric slice: equity from test_start onward.
        # Pre-test equity observations (if any) are at the constant
        # initial_capital value (no trades fired pre-test); slice them
        # out so the metric computation uses only the test-period
        # post-test_start observations.
        ec = result.equity_curve
        test_start_naive = test_start_dt.replace(tzinfo=None)
        ec_test = ec[ec.index >= test_start_naive]

        # Trades are also test-period-only by wrapper construction
        # (next() suppression prevented pre-test orders from firing),
        # but apply the entry-time filter as a defensive belt-and-
        # suspenders check. Should be a no-op under correct wrapper.
        trades_test = [
            t for t in result.trades
            if pd.Timestamp(t["entry_time_utc"]).tz_localize(None)
               >= test_start_naive
        ]
        # Defensive assertion: wrapper should have prevented all pre-test trades.
        if len(trades_test) != len(result.trades):
            raise RuntimeError(
                f"Window {i+1}: wrapper failed — {len(result.trades) - len(trades_test)} "
                f"pre-test trades present in result. Engine patch is broken."
            )

        # Compute metrics on test-only slice (canonical Q2 (iii) metrics).
        test_metrics = compute_all_metrics(ec_test, trades_test, cash)

        # Determine effective_start for the test portion
        test_effective_start = None
        if len(ec_test) > 0:
            test_effective_start = ec_test.index[0].to_pydatetime()

        # Update result.metrics to test-only so window_result.metrics
        # reflects canonical test-period activity (required for T7:
        # same test window with different train lengths must be
        # bit-identical on window_result.metrics).
        result.metrics = test_metrics

        # Write window registry row
        window_run_id = result.run_id
        _write_to_registry(
            run_id=window_run_id,
            strategy_cls=strategy_cls,
            strategy_params=strategy_params,
            start_date=test_start_dt,
            end_date=data_end_dt,
            effective_start=test_effective_start,
            warmup_bars=result.warmup_bars,
            cost_model=cost_model,
            metrics=test_metrics,
            db_path=db_path,
            run_type="walk_forward_window",
            parent_run_id=summary_run_id,
            train_start=data_start_dt,
            train_end=datetime(
                w_train_end.year, w_train_end.month, w_train_end.day,
                hour=23, tzinfo=timezone.utc,
            ),
        )

        window_results.append(result)
        window_metrics_list.append(test_metrics)

        logger.info(
            "    Window %d: %d trades, return=%.4f, sharpe=%.3f",
            i + 1,
            test_metrics["total_trades"],
            test_metrics["total_return"],
            test_metrics["sharpe_ratio"],
        )

    # Compute summary metrics across all windows
    summary_metrics = _aggregate_walk_forward_metrics(
        window_metrics_list, len(windows)
    )

    # Write summary registry row
    first_test_start_dt = datetime(
        windows[0][2].year, windows[0][2].month, windows[0][2].day,
        tzinfo=timezone.utc,
    )
    last_test_end_dt = datetime(
        windows[-1][3].year, windows[-1][3].month, windows[-1][3].day,
        hour=23, tzinfo=timezone.utc,
    )
    first_train_start_dt = datetime(
        windows[0][0].year, windows[0][0].month, windows[0][0].day,
        tzinfo=timezone.utc,
    )
    last_train_end_dt = datetime(
        windows[-1][1].year, windows[-1][1].month, windows[-1][1].day,
        hour=23, tzinfo=timezone.utc,
    )

    _write_to_registry(
        run_id=summary_run_id,
        strategy_cls=strategy_cls,
        strategy_params=strategy_params,
        start_date=first_test_start_dt,
        end_date=last_test_end_dt,
        effective_start=None,
        warmup_bars=window_results[0].warmup_bars if window_results else 0,
        cost_model=cost_model,
        metrics=summary_metrics,
        db_path=db_path,
        run_type="walk_forward_summary",
        parent_run_id=None,
        train_start=first_train_start_dt,
        train_end=last_train_end_dt,
        notes=json.dumps({
            "num_windows": len(windows),
            "train_months": train_months,
            "test_months": test_months,
            "step_months": step_months,
            # Disjoint-range provenance: callers reading the summary
            # row should consult train_ranges (not the train_start /
            # train_end span) for the actual training periods.
            "train_ranges": [
                [r_start.isoformat(), r_end.isoformat()]
                for r_start, r_end in ranges
            ],
            "params": strategy_params or {},
        }),
    )

    logger.info(
        "Walk-forward complete: %d windows, mean_sharpe=%.3f, "
        "mean_return=%.4f, total_trades=%d",
        len(windows),
        summary_metrics.get("sharpe_ratio", 0.0),
        summary_metrics.get("total_return", 0.0),
        summary_metrics.get("total_trades", 0),
    )

    return WalkForwardResult(
        summary_run_id=summary_run_id,
        window_results=window_results,
        summary_metrics=summary_metrics,
        windows=windows,
    )


def _aggregate_walk_forward_metrics(
    window_metrics: list[dict[str, Any]],
    num_windows: int,
) -> dict[str, Any]:
    """Aggregate per-window metrics into walk-forward summary statistics.

    The summary row stores aggregated statistics across window runs
    and must not be interpreted as a single contiguous backtest.

    Args:
        window_metrics: List of metrics dicts, one per window.
        num_windows: Total number of windows.

    Returns:
        Dict with aggregate metrics matching the registry schema.
    """
    if not window_metrics:
        return {
            "total_return": 0.0,
            "sharpe_ratio": 0.0,
            "max_drawdown": 0.0,
            "max_drawdown_duration_hours": 0.0,
            "initial_capital": 0.0,
            "final_capital": None,
            "total_trades": 0,
            "win_rate": 0.0,
            "avg_trade_duration_hours": 0.0,
            "avg_trade_return": 0.0,
            "profit_factor": None,
        }

    sharpes = [m["sharpe_ratio"] for m in window_metrics]
    returns = [m["total_return"] for m in window_metrics]
    drawdowns = [m["max_drawdown"] for m in window_metrics]
    dd_durations = [m["max_drawdown_duration_hours"] for m in window_metrics]
    total_trades = sum(m["total_trades"] for m in window_metrics)

    # Aggregate win rate: sum winners across windows / total trades
    total_winners = sum(
        round(m["win_rate"] * m["total_trades"])
        for m in window_metrics
        if m["total_trades"] > 0
    )
    overall_win_rate = total_winners / total_trades if total_trades > 0 else 0.0

    # Aggregate profit factor: sum gross profit / sum gross loss
    # We don't have raw P&L per window, so use mean of non-None values
    profit_factors = [
        m["profit_factor"] for m in window_metrics
        if m["profit_factor"] is not None
    ]
    overall_pf = (
        float(np.mean(profit_factors)) if profit_factors else None
    )

    # Aggregate trade duration
    durations = [
        m["avg_trade_duration_hours"] for m in window_metrics
        if m["total_trades"] > 0
    ]
    avg_duration = float(np.mean(durations)) if durations else 0.0

    # Aggregate trade return
    trade_returns = [
        m["avg_trade_return"] for m in window_metrics
        if m["total_trades"] > 0
    ]
    avg_trade_ret = float(np.mean(trade_returns)) if trade_returns else 0.0

    return {
        "total_return": float(np.mean(returns)),
        "sharpe_ratio": float(np.mean(sharpes)),
        "max_drawdown": float(max(drawdowns)),
        "max_drawdown_duration_hours": float(max(dd_durations)),
        "initial_capital": window_metrics[0].get("initial_capital"),
        "final_capital": None,
        "total_trades": total_trades,
        "win_rate": overall_win_rate,
        "avg_trade_duration_hours": avg_duration,
        "avg_trade_return": avg_trade_ret,
        "profit_factor": overall_pf,
    }


# ---------------------------------------------------------------------------
# Regime holdout (Phase 2A D4) — orchestrator-internal only.
#
# CONTRACT BOUNDARY: this section MUST NOT be wired into argparse,
# main(), or any other CLI surface. Each invocation of
# :func:`run_regime_holdout` is an observation of the held-out 2022
# bear-market data; exposing a CLI flag would let people casually re-run
# it for ad-hoc analysis and silently degrade the holdout's
# epistemic value. The mechanical ripgrep self-check in the D4
# checklist enforces absence by name. If a future phase needs a CLI
# wrapper, it must be paired with an explicit invocation budget — not
# added here on a whim.
# ---------------------------------------------------------------------------


@dataclass
class RegimeHoldoutResult:
    """Container for a regime-holdout evaluation.

    The four passing-criteria fields mirror the v2 environments.yaml
    block. ``regime_holdout_passed`` is the AND of all four — see
    :func:`_evaluate_regime_holdout_pass` for the exact comparison.
    """

    run_id: str
    parent_run_id: str
    batch_id: str
    hypothesis_hash: str | None
    regime_holdout_passed: bool
    sharpe_ratio: float
    max_drawdown: float
    total_return: float
    total_trades: int
    passing_criteria: dict[str, float]
    metrics: dict[str, Any]


def _load_regime_block_config(
    env_config: dict[str, Any] | None = None,
    regime_key: str = "v2.regime_holdout",
) -> dict[str, Any]:
    """Read a named regime block from environments.yaml.

    Generalizes the prior ``_load_regime_holdout_config`` to support
    multiple regime blocks across two namespaces:

    * ``v2.<block_name>`` — versioned splits namespace (PHASE2C_7.1 §3).
      The ``v2`` prefix must match ``env_config["version"]``; ``block_name``
      is the key under ``env_config["splits"]``. Examples:
      ``"v2.regime_holdout"``, ``"v2.validation"``.
    * ``evaluation_regimes.<block_name>`` — additive structural
      namespace (PHASE2C_8.1 §3.4). Top-level YAML key
      ``evaluation_regimes`` houses PHASE2C_8.1's novel evaluation
      regimes (eval_2020_v1, eval_2021_v1). Lookups in this namespace
      bypass version validation because the namespace is structural,
      not versioned. Future arcs that bump env_config version still
      resolve ``evaluation_regimes.<name>`` via the structural
      top-level key.

    Args:
        env_config: Pre-loaded env config dict (testing). When None,
            reads ``config/environments.yaml`` from disk.
        regime_key: Dotted regime identifier, e.g.
            ``"v2.regime_holdout"``, ``"v2.validation"``, or
            ``"evaluation_regimes.eval_2020_v1"``. Default preserves
            the PHASE2C_6 production path for backward-compat.

    Returns:
        The named regime block.

    Raises:
        ValueError: If ``regime_key`` is malformed, an unknown namespace
            prefix is used, the v2-namespace version mismatches
            ``env_config["version"]``, or the named block is absent
            from its target namespace section.
    """
    if env_config is None:
        import yaml
        env_path = PROJECT_ROOT / "config" / "environments.yaml"
        with open(env_path) as f:
            env_config = yaml.safe_load(f)

    if "." not in regime_key:
        raise ValueError(
            f"regime_key must be of the form '<namespace>.<block_name>'; "
            f"got {regime_key!r}"
        )
    namespace, block_name = regime_key.split(".", 1)

    if namespace == "evaluation_regimes":
        # PHASE2C_8.1 §3.4 — structural namespace; no version validation.
        block = env_config.get("evaluation_regimes", {}).get(block_name)
        if not block:
            raise ValueError(
                f"environments.yaml is missing "
                f"evaluation_regimes.{block_name} "
                f"(regime_key={regime_key!r})"
            )
        return block

    # Versioned splits namespace (PHASE2C_7.1 §3 — v2.<block>).
    actual_version = env_config.get("version")
    if actual_version != namespace:
        raise ValueError(
            f"regime_key={regime_key!r} requires environments.yaml "
            f"version {namespace!r}; found {actual_version!r}"
        )
    block = env_config.get("splits", {}).get(block_name)
    if not block:
        raise ValueError(
            f"environments.yaml is missing splits.{block_name} "
            f"(regime_key={regime_key!r})"
        )
    return block


def _resolve_passing_criteria_with_inheritance(
    env_config: dict[str, Any],
    regime_key: str,
) -> tuple[dict[str, float], str]:
    """Resolve the 4-criterion passing_criteria for a regime evaluation.

    PHASE2C_7.1 §3 / Q1 cross-block coupling. The validation block in
    environments.yaml has no ``passing_criteria`` field; the gate
    thresholds inherit from the canonical ``regime_holdout`` block so
    multi-regime evaluation arcs share a single source of truth for
    "what does it mean to pass". This function makes the inheritance
    visible and testable rather than burying it inside
    ``run_regime_holdout``.

    Args:
        env_config: Pre-loaded env config dict.
        regime_key: Dotted regime identifier (see
            :func:`_load_regime_block_config`).

    Returns:
        ``(passing_criteria, source_block_name)`` — ``source_block_name``
        is the name of the block from which the criteria were loaded
        (``"regime_holdout"`` on inheritance, the requested block name
        otherwise). Used by callers for explicit run-time logging of
        the cross-block coupling.
    """
    block = _load_regime_block_config(env_config, regime_key)
    requested_block_name = regime_key.split(".", 1)[1]
    if "passing_criteria" in block:
        return block["passing_criteria"], requested_block_name

    # Inherit from the canonical regime_holdout block. Re-uses the
    # same env_config dict, so no additional disk I/O.
    fallback = _load_regime_block_config(env_config, "v2.regime_holdout")
    return fallback["passing_criteria"], "regime_holdout"


def _evaluate_regime_holdout_pass(
    metrics: dict[str, Any], passing_criteria: dict[str, float]
) -> bool:
    """4-condition AND gate for regime_holdout_passed.

    The gate is intentionally strict — ALL four conditions must hold.
    NaN on any metric collapses to False (NaN comparisons in Python
    return False, which is the desired conservative behavior here).
    Mirrors CLAUDE.md's hard constraint:

        "❌ NEVER mark regime_holdout_passed = True unless ALL four
         criteria are met"

    Args:
        metrics: Output of compute_all_metrics for the 2022 holdout run.
        passing_criteria: Dict with keys min_sharpe, max_drawdown,
            min_total_return, min_total_trades.

    Returns:
        True iff every condition holds.
    """
    sharpe = metrics.get("sharpe_ratio", float("nan"))
    dd = metrics.get("max_drawdown", float("nan"))
    ret = metrics.get("total_return", float("nan"))
    trades = metrics.get("total_trades", 0) or 0
    # CONTRACT GAP: The passing_criteria thresholds in environments.yaml
    # are calibrated for the current D4 feed-loading semantics (see the
    # DESIGN INVARIANT block above run_regime_holdout): first WARMUP_BARS
    # bars of 2022 are NOT signal-eligible, effective holdout sample is
    # ~8700 bars for WARMUP_BARS ≈ 50. If a later phase modifies the
    # holdout feed loader to prepend pre-window history, the effective
    # sample grows to the full 8760 bars and these thresholds —
    # especially min_total_trades=5 — should be re-validated in the
    # same PR that introduces the feed change.
    return bool(
        sharpe >= passing_criteria["min_sharpe"]
        and dd <= passing_criteria["max_drawdown"]
        and ret >= passing_criteria["min_total_return"]
        and trades >= passing_criteria["min_total_trades"]
    )


# DESIGN INVARIANT: feed loading for the regime holdout run.
#
# Earlier D4 wording (both in this file's surrounding prose and in
# PHASE2_BLUEPRINT.md §D4) suggested that "warmup is naturally served by
# the bars preceding fromdate within the parquet" — implying that late-2021
# bars fill the warmup for a 2022 holdout run. That wording was INACCURATE
# relative to the actual Phase 1A engine behavior.
#
# What actually happens (and what D4 signs off on):
#   - run_regime_holdout calls run_backtest with
#         fromdate = 2022-01-01  (holdout start)
#         todate   = 2022-12-31  (holdout end)
#   - ParquetFeed.from_parquet(fromdate=..., todate=...) at engine.py:376
#     filters the parquet down to bars strictly inside that window. The
#     feed for the holdout run therefore contains ONLY 2022 bars — not a
#     full dataset with pre-window history attached.
#   - Backtrader consumes the first WARMUP_BARS bars of 2022 to warm up
#     the strategy's indicators. Those early-January 2022 bars are
#     therefore NOT signal-eligible. Metrics (Sharpe, drawdown, etc.)
#     are computed only from the first post-warmup bar onward, exactly
#     as in every other run_backtest call.
#   - Consequence: the first small fraction of the 2022 holdout window
#     (WARMUP_BARS hours — typically ≤ a few days for the baselines) is
#     not evaluated. The 4-condition holdout gate operates on what
#     remains.
#
# Why this is acceptable for D4 sign-off and why we are NOT reopening it:
#   1. It is the exact behavior of the trusted Phase 1A single-run engine.
#      Every run in the registry — train walk-forward windows, validation,
#      test, and now regime holdout — uses the same feed-loading rule, so
#      strategies are compared on a level playing field.
#   2. D4's 4-condition holdout gate (min_sharpe, max_drawdown,
#      min_total_return, min_total_trades) remains operationally
#      meaningful over an 8,700-bar year minus ~50 warmup bars. Losing
#      the first few days does not change whether a strategy survives
#      a bear regime.
#   3. Modifying ParquetFeed or run_backtest to prepend pre-window
#      history purely for holdout runs would be a Phase 1 engine change
#      touching code paths used by every existing backtest. That is
#      explicitly OUT OF SCOPE for D4. If a future phase decides the
#      missing warmup window is material, it must be proposed as a
#      scoped Phase 1 revision, not smuggled in through D4.
#
# CONTRACT BOUNDARY with the no-CLI rule above still applies: this
# function is orchestrator-internal, and the warmup convention here does
# not change that.
def run_regime_holdout(
    dsl: "Any",
    batch_id: str,
    parent_run_id: str,
    *,
    regime_key: str = "v2.regime_holdout",
    # FUTURE-DEPRECATION: the default preserves PHASE2C_6 reproducibility
    # (single-regime 2022 evaluation). Once multi-regime evaluation
    # callers (PHASE2C_7.1+) are the production norm, this default is a
    # candidate for removal so callers must be explicit about regime
    # identity. Remove only when no implicit-default callers remain.
    strategy_cls: type[bt.Strategy] | None = None,
    strategy_params: dict[str, Any] | None = None,
    parquet_path: str | Path | None = None,
    cash: float = 10_000.0,
    db_path: Path | None = None,
    env_config: dict[str, Any] | None = None,
    registry: "Any" = None,
    manifest_dir: Path | None = None,
) -> RegimeHoldoutResult:
    """Run the 2022 regime holdout for a single hypothesis.

    Orchestrator-internal only. The 2022 bear-market window is a fixed
    stress test that the AI must never see — see CLAUDE.md and the
    CONTRACT BOUNDARY block above this function for the no-CLI rule.

    Execution model:
        - Compiles the DSL (or accepts a pre-compiled override via
          ``strategy_cls``) and invokes :func:`run_backtest` over the
          fixed 2022-01-01..2022-12-31 range.
        - The Backtrader feed is loaded with fromdate / todate set to
          exactly this holdout range — see the DESIGN INVARIANT block
          immediately above this function for why warmup is served
          from *inside* the holdout window rather than from late-2021
          bars, and why that is the correct behavior for D4.
        - This is a SEPARATE run — never sliced from a longer
          continuous run, because slicing a continuous-run equity curve
          for holdout metrics is a CLAUDE.md hard prohibition.
        - Computes :func:`compute_all_metrics` over the holdout-only
          equity curve and applies :func:`_evaluate_regime_holdout_pass`
          for the 4-condition AND gate.
        - Writes a single registry row with
          ``run_type="regime_holdout"``, ``parent_run_id`` linking the
          row to the train walk-forward summary, and the v2 D4 columns
          (``batch_id``, ``hypothesis_hash``, ``regime_holdout_passed``).

    Args:
        dsl: Validated :class:`StrategyDSL` instance describing the
            hypothesis. May be None if ``strategy_cls`` is provided
            (testing path with hand-coded strategies).
        batch_id: Phase 2B batch UUID this hypothesis belongs to.
        parent_run_id: ``run_id`` of the train walk-forward summary
            row that produced this hypothesis. Stored verbatim in the
            registry's ``parent_run_id`` column for lineage queries.
        strategy_cls: Pre-compiled BaseStrategy override (testing). When
            None, compiles ``dsl`` via :func:`compile_dsl_to_strategy`.
        strategy_params: Extra kwargs passed to ``cerebro.addstrategy``.
        parquet_path: Override OHLCV parquet path. None uses the canonical
            dataset.
        cash: Initial capital (default $10,000).
        db_path: Path to experiment registry DB. None uses default.
        env_config: Pre-loaded env config dict (testing).
        registry: FactorRegistry override (testing).
        manifest_dir: Compilation manifest directory (testing).

    Returns:
        RegimeHoldoutResult with the per-criterion outcome and run_id.
    """
    # Resolve env config once, then thread to both block + criteria
    # lookups so disk I/O is paid at most once per call.
    if env_config is None:
        import yaml
        env_path = PROJECT_ROOT / "config" / "environments.yaml"
        with open(env_path) as f:
            resolved_env_config = yaml.safe_load(f)
    else:
        resolved_env_config = env_config

    block = _load_regime_block_config(resolved_env_config, regime_key)
    passing_criteria, criteria_source_block = (
        _resolve_passing_criteria_with_inheritance(
            resolved_env_config, regime_key
        )
    )

    requested_block_name = regime_key.split(".", 1)[1]
    if criteria_source_block != requested_block_name:
        # PHASE2C_7.1 §3 / Q1 cross-block coupling: explicit run-time
        # breadcrumb so a future maintainer can trace where the gate
        # thresholds came from when running against a regime block
        # that has no passing_criteria of its own (e.g. validation).
        logger.info(
            "Regime evaluation regime_key=%s: passing_criteria inherited "
            "from %s block (no passing_criteria field on %s block in "
            "environments.yaml; cross-block coupling per PHASE2C_7.1 §3)",
            regime_key, criteria_source_block, requested_block_name,
        )

    holdout_start = date.fromisoformat(block["start"])
    holdout_end = date.fromisoformat(block["end"])

    start_dt = datetime(
        holdout_start.year, holdout_start.month, holdout_start.day,
        tzinfo=timezone.utc,
    )
    # Include all hourly bars on the last day (matches single-run CLI).
    end_dt = datetime(
        holdout_end.year, holdout_end.month, holdout_end.day,
        hour=23, tzinfo=timezone.utc,
    )

    hypothesis_hash: str | None = None
    feature_version: str | None = None
    strategy_source = "manual"

    if strategy_cls is None:
        if dsl is None:
            raise ValueError(
                "run_regime_holdout requires either dsl or strategy_cls"
            )
        # Local import to avoid pulling pydantic / DSL machinery into
        # callers that only use the Phase 1 single-run path.
        from strategies.dsl_compiler import compile_dsl_to_strategy
        from strategies.dsl import compute_dsl_hash

        compile_kwargs: dict[str, Any] = {}
        if registry is not None:
            compile_kwargs["registry"] = registry
        if manifest_dir is not None:
            compile_kwargs["manifest_dir"] = manifest_dir

        strategy_cls = compile_dsl_to_strategy(dsl, **compile_kwargs)
        hypothesis_hash = compute_dsl_hash(dsl)
        strategy_source = "dsl"

        # Best-effort feature_version capture for registry lineage.
        try:
            from factors.registry import compute_feature_version, get_registry
            reg = registry if registry is not None else get_registry()
            feature_version = compute_feature_version(reg)
        except Exception:
            feature_version = None
    elif dsl is not None:
        # Allow tests to pass both — derive hypothesis_hash from dsl.
        try:
            from strategies.dsl import compute_dsl_hash
            hypothesis_hash = compute_dsl_hash(dsl)
        except Exception:
            hypothesis_hash = None

    result = run_backtest(
        strategy_cls=strategy_cls,
        start_date=start_dt,
        end_date=end_dt,
        strategy_params=strategy_params or {},
        parquet_path=parquet_path,
        cash=cash,
        write_registry=False,
    )

    passed = _evaluate_regime_holdout_pass(result.metrics, passing_criteria)

    # Registry row uses the fresh holdout run_id (already minted by
    # run_backtest); the orchestrator links via parent_run_id, not by
    # collapsing the train and holdout rows.
    holdout_run_id = result.run_id

    from backtest.execution_model import ConstantSlippage
    cost_model = ConstantSlippage.from_config(load_execution_config())

    notes_payload = {
        "label": block.get("label"),
        "passing_criteria": passing_criteria,
        "criterion_outcomes": {
            "sharpe_ratio": result.metrics.get("sharpe_ratio"),
            "max_drawdown": result.metrics.get("max_drawdown"),
            "total_return": result.metrics.get("total_return"),
            "total_trades": result.metrics.get("total_trades"),
        },
    }

    _write_to_registry(
        run_id=holdout_run_id,
        strategy_cls=strategy_cls,
        strategy_params=strategy_params or {},
        start_date=start_dt,
        end_date=end_dt,
        effective_start=result.effective_start,
        warmup_bars=result.warmup_bars,
        cost_model=cost_model,
        metrics=result.metrics,
        db_path=db_path,
        run_type="regime_holdout",
        parent_run_id=parent_run_id,
        train_start=None,
        train_end=None,
        notes=json.dumps(notes_payload),
        batch_id=batch_id,
        hypothesis_hash=hypothesis_hash,
        regime_holdout_passed=passed,
        lifecycle_state=None,
        strategy_source=strategy_source,
        feature_version=feature_version,
    )

    logger.info(
        "Regime holdout %s: passed=%s sharpe=%.3f dd=%.3f ret=%.4f trades=%d",
        holdout_run_id[:8], passed,
        result.metrics.get("sharpe_ratio", float("nan")),
        result.metrics.get("max_drawdown", float("nan")),
        result.metrics.get("total_return", float("nan")),
        result.metrics.get("total_trades", 0),
    )

    return RegimeHoldoutResult(
        run_id=holdout_run_id,
        parent_run_id=parent_run_id,
        batch_id=batch_id,
        hypothesis_hash=hypothesis_hash,
        regime_holdout_passed=passed,
        sharpe_ratio=float(result.metrics.get("sharpe_ratio", float("nan"))),
        max_drawdown=float(result.metrics.get("max_drawdown", float("nan"))),
        total_return=float(result.metrics.get("total_return", float("nan"))),
        total_trades=int(result.metrics.get("total_trades", 0) or 0),
        passing_criteria=dict(passing_criteria),
        metrics=dict(result.metrics),
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> int:
    """CLI entry point for single-run and walk-forward backtesting.

    Returns:
        Exit code: 0 on success, 1 on failure.
    """
    logging.basicConfig(
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%SZ",
        level=logging.INFO,
    )

    parser = argparse.ArgumentParser(
        description="Run backtests (Phase 1A single-run or Phase 1B walk-forward)"
    )
    parser.add_argument(
        "--strategy",
        type=str,
        required=True,
        help="Strategy name (e.g. sma_crossover)",
    )
    parser.add_argument(
        "--mode",
        type=str,
        choices=["single-run", "walk-forward"],
        default="single-run",
        help="Run mode (default: single-run)",
    )
    parser.add_argument(
        "--start",
        type=str,
        default=None,
        help="Start date YYYY-MM-DD (single-run only, required for single-run)",
    )
    parser.add_argument(
        "--end",
        type=str,
        default=None,
        help="End date YYYY-MM-DD (single-run only, required for single-run)",
    )
    parser.add_argument(
        "--cash",
        type=float,
        default=10_000.0,
        help="Initial capital (default: 10000)",
    )
    parser.add_argument(
        "--no-registry",
        action="store_true",
        help="Skip writing to experiment registry",
    )
    parser.add_argument(
        "--parquet",
        type=str,
        default=None,
        help="Path to OHLCV parquet file (uses default if omitted)",
    )
    parser.add_argument(
        "--params",
        type=str,
        default=None,
        help='Strategy params as JSON (e.g. \'{"fast_period": 10}\')',
    )
    args = parser.parse_args()

    # Look up strategy
    _ensure_strategies_loaded()
    if args.strategy not in STRATEGY_REGISTRY:
        logger.error(
            "Unknown strategy: %s. Available: %s",
            args.strategy,
            list(STRATEGY_REGISTRY.keys()),
        )
        return 1

    strategy_cls = STRATEGY_REGISTRY[args.strategy]
    strategy_params = json.loads(args.params) if args.params else {}
    parquet_path = Path(args.parquet) if args.parquet else None

    if args.mode == "walk-forward":
        return _cli_walk_forward(args, strategy_cls, strategy_params, parquet_path)

    # Single-run mode
    if not args.start or not args.end:
        logger.error("--start and --end are required for single-run mode")
        return 1

    start_date = datetime.strptime(args.start, "%Y-%m-%d").replace(
        tzinfo=timezone.utc
    )
    # --end 2024-12-31 means "include all bars on that day"
    # Expand to 23:00 UTC (last hourly bar of the day)
    end_date = (
        datetime.strptime(args.end, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        + timedelta(hours=23)
    )

    result = run_backtest(
        strategy_cls=strategy_cls,
        start_date=start_date,
        end_date=end_date,
        strategy_params=strategy_params,
        parquet_path=parquet_path,
        cash=args.cash,
        write_registry=not args.no_registry,
    )

    _print_single_run_summary(result)
    return 0


def _cli_walk_forward(
    args: argparse.Namespace,
    strategy_cls: type[bt.Strategy],
    strategy_params: dict[str, Any],
    parquet_path: Path | None,
) -> int:
    """Handle walk-forward CLI mode.

    In walk-forward mode, --start/--end are ignored. Dates come from
    environments.yaml.

    Args:
        args: Parsed CLI args.
        strategy_cls: Strategy class.
        strategy_params: Strategy params dict.
        parquet_path: Optional parquet path.

    Returns:
        Exit code: 0 on success.
    """
    if args.start or args.end:
        logger.warning(
            "--start/--end are ignored in walk-forward mode "
            "(dates come from environments.yaml)"
        )

    wf_result = run_walk_forward(
        strategy_cls=strategy_cls,
        strategy_params=strategy_params,
        parquet_path=parquet_path,
        cash=args.cash,
        db_path=None if not args.no_registry else Path("/dev/null"),
    )

    # Print summary
    sm = wf_result.summary_metrics
    print(f"\n{'='*60}")
    print(f"WALK-FORWARD SUMMARY")
    print(f"{'='*60}")
    print(f"Summary ID:   {wf_result.summary_run_id[:8]}...")
    print(f"Strategy:     {getattr(strategy_cls, 'STRATEGY_NAME', '?')}")
    print(f"Windows:      {len(wf_result.windows)}")
    print(f"{'='*60}")
    print(f"Mean Return:    {sm['total_return']:.4f} ({sm['total_return']*100:.2f}%)")
    print(f"Mean Sharpe:    {sm['sharpe_ratio']:.3f}")
    print(f"Worst Drawdown: {sm['max_drawdown']:.4f} ({sm['max_drawdown']*100:.2f}%)")
    print(f"Total Trades:   {sm['total_trades']}")
    print(f"Win Rate:       {sm['win_rate']:.2f}")
    pf = sm.get("profit_factor")
    print(f"Profit Factor:  {pf:.2f}" if pf is not None else "Profit Factor:  N/A")
    print(f"{'='*60}")

    # Per-window breakdown
    print(f"\n{'Window':<8s} {'Train Period':<24s} {'Test Period':<24s} "
          f"{'Trades':>7s} {'Return':>8s} {'Sharpe':>8s}")
    print(f"{'-'*8} {'-'*24} {'-'*24} {'-'*7} {'-'*8} {'-'*8}")
    for i, (w_result, window) in enumerate(
        zip(wf_result.window_results, wf_result.windows)
    ):
        train_str = f"{window[0]} to {window[1]}"
        test_str = f"{window[2]} to {window[3]}"
        # Window metrics are the test-only metrics stored in registry;
        # for display, we show the original full-run result counts
        print(f"  {i+1:<6d} {train_str:<24s} {test_str:<24s} "
              f"{w_result.metrics['total_trades']:>7d} "
              f"{w_result.metrics['total_return']:>8.4f} "
              f"{w_result.metrics['sharpe_ratio']:>8.3f}")

    print(f"{'='*60}\n")
    return 0


def _print_single_run_summary(result: BacktestResult) -> None:
    """Print summary for a single-run backtest.

    Args:
        result: BacktestResult from run_backtest().
    """
    print(f"\n{'='*60}")
    print(f"Run ID:     {result.run_id}")
    print(f"Strategy:   {result.strategy_name}")
    print(f"Range:      {result.start_date.date()} to {result.end_date.date()}")
    print(f"Warmup:     {result.warmup_bars} bars")
    if result.effective_start:
        print(f"Eff. Start: {result.effective_start}")
    print(f"{'='*60}")
    print(f"Total Return:   {result.metrics['total_return']:.4f} ({result.metrics['total_return']*100:.2f}%)")
    print(f"Sharpe Ratio:   {result.metrics['sharpe_ratio']:.3f}")
    print(f"Max Drawdown:   {result.metrics['max_drawdown']:.4f} ({result.metrics['max_drawdown']*100:.2f}%)")
    print(f"DD Duration:    {result.metrics['max_drawdown_duration_hours']:.0f} hours")
    print(f"Total Trades:   {result.metrics['total_trades']}")
    print(f"Win Rate:       {result.metrics['win_rate']:.2f}")
    pf = result.metrics['profit_factor']
    print(f"Profit Factor:  {pf:.2f}" if pf is not None else "Profit Factor:  N/A (no losses)")
    print(f"Avg Trade Ret:  {result.metrics['avg_trade_return']:.4f}")
    if result.trade_csv_path:
        print(f"Trade Log:      {result.trade_csv_path}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    sys.exit(main())

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
) -> None:
    """Write run results to the experiment registry.

    Defaults preserve Phase 1A single-run semantics:
    - run_type="single_run", parent_run_id=None
    - test_start/test_end = engine's date range (start_date/end_date)
    - train_start/train_end/validation_start/validation_end = NULL

    For walk-forward windows, callers pass:
    - run_type="walk_forward_window"
    - parent_run_id=<summary_uuid>
    - train_start/train_end from the window definition
    - start_date/end_date set to the window's test dates

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
        "strategy_source": "manual",
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
    }

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


def run_walk_forward(
    strategy_cls: type[bt.Strategy],
    strategy_params: dict[str, Any] | None = None,
    parquet_path: str | Path | None = None,
    cash: float = 10_000.0,
    db_path: Path | None = None,
    walk_forward_config: dict[str, int] | None = None,
    overall_start: date | None = None,
    overall_end: date | None = None,
) -> WalkForwardResult:
    """Execute walk-forward backtesting across rolling windows.

    Orchestration layer over the Phase 1A single-run engine. Each window
    calls run_backtest() unchanged — the strategy runs across the full
    train+test span so indicators evolve continuously, but metrics are
    computed only on the test portion.

    For Phase 1B baselines, no parameter optimization is performed.
    The train window represents in-sample context and is logged as such.

    Args:
        strategy_cls: Backtrader Strategy class to run.
        strategy_params: Strategy parameters (passed to each window run).
        parquet_path: Path to OHLCV parquet file. Uses default if None.
        cash: Initial capital per window (default $10,000).
        db_path: Path to experiment registry DB. Uses default if None.
        walk_forward_config: Override window params dict with keys:
            train_months, test_months, step_months.
        overall_start: Override start date for window generation.
        overall_end: Override end date for window generation.

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

    # Determine overall date range from splits
    if overall_start is None:
        overall_start = date.fromisoformat(
            env_config["splits"]["training"]["start"]
        )
    if overall_end is None:
        overall_end = date.fromisoformat(
            env_config["splits"]["test"]["end"]
        )

    # Generate windows
    windows = generate_walk_forward_windows(
        overall_start, overall_end,
        train_months, test_months, step_months,
    )

    if not windows:
        raise ValueError(
            f"No walk-forward windows fit in range "
            f"[{overall_start}, {overall_end}] with "
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

        # Convert dates to UTC datetimes for run_backtest
        data_start_dt = datetime(
            w_train_start.year, w_train_start.month, w_train_start.day,
            tzinfo=timezone.utc,
        )
        # Include all bars on the last day
        data_end_dt = datetime(
            w_test_end.year, w_test_end.month, w_test_end.day,
            hour=23, tzinfo=timezone.utc,
        )
        test_start_dt = datetime(
            w_test_start.year, w_test_start.month, w_test_start.day,
            tzinfo=timezone.utc,
        )

        # Run the Phase 1A engine unchanged — no registry write
        result = run_backtest(
            strategy_cls=strategy_cls,
            start_date=data_start_dt,
            end_date=data_end_dt,
            strategy_params=strategy_params,
            parquet_path=parquet_path,
            cash=cash,
            write_registry=False,
        )

        # Trim equity curve to test period only
        ec = result.equity_curve
        test_start_naive = test_start_dt.replace(tzinfo=None)
        ec_test = ec[ec.index >= test_start_naive]

        # Filter trades to test period (entry in test window)
        trades_test = [
            t for t in result.trades
            if pd.Timestamp(t["entry_time_utc"]).tz_localize(None)
               >= test_start_naive
        ]

        # Renumber trade_ids sequentially within the test-only set
        for idx, t in enumerate(trades_test, start=1):
            t["trade_id"] = idx

        # Overwrite the trade CSV with test-only trades.
        # run_backtest() already saved the full train+test CSV; we must
        # replace it so the persisted artifact is test-window isolated.
        _save_trade_csv(result.run_id, trades_test)

        # Recompute metrics on test-only data
        test_metrics = compute_all_metrics(ec_test, trades_test, cash)

        # Determine effective_start for the test portion
        test_effective_start = None
        if len(ec_test) > 0:
            test_effective_start = ec_test.index[0].to_pydatetime()

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

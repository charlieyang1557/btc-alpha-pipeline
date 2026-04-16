"""Single-run backtest engine for Phase 1A.

Orchestrates a complete backtest: loads data, configures Cerebro,
runs the strategy, collects trade artifacts with correct time
semantics, computes metrics, and logs to the experiment registry.

Usage:
    python -m backtest.engine --strategy sma_crossover \\
        --start 2024-01-01 --end 2024-12-31

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
import json
import logging
import sys
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
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
    """Register a strategy class by its STRATEGY_NAME."""
    name = getattr(cls, "STRATEGY_NAME", None)
    if name is None:
        raise ValueError(f"{cls.__name__} must define STRATEGY_NAME")
    STRATEGY_REGISTRY[name] = cls
    return cls


def _ensure_strategies_loaded() -> None:
    """Import baseline strategies so they register themselves."""
    if not STRATEGY_REGISTRY:
        from strategies.baseline.sma_crossover import SMACrossover  # noqa: F401
        register_strategy(SMACrossover)


# ---------------------------------------------------------------------------
# Trade collector — Backtrader analyzer for trade artifact extraction
# ---------------------------------------------------------------------------


class TradeCollector(bt.Analyzer):
    """Collects completed trades with correct signal/fill time semantics.

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
) -> None:
    """Write run results to the experiment registry.

    Phase 1A single-run mode:
    - test_start/test_end = engine's date range
    - train_start/train_end/validation_start/validation_end = NULL

    Args:
        run_id: UUID for this run.
        strategy_cls: Strategy class.
        strategy_params: Strategy params dict.
        start_date: Backtest start date.
        end_date: Backtest end date.
        effective_start: First bar after warmup.
        warmup_bars: Number of warmup bars.
        cost_model: ConstantSlippage instance.
        metrics: Computed metrics dict.
        db_path: Path to DB (uses default if None).
    """
    from backtest.experiment_registry import (
        create_table,
        get_connection,
        insert_run,
    )

    strategy_name = getattr(strategy_cls, "STRATEGY_NAME", strategy_cls.__name__)

    run_data = {
        "run_id": run_id,
        "run_type": "single_run",
        "parent_run_id": None,
        "strategy_name": strategy_name,
        "strategy_source": json.dumps(strategy_params) if strategy_params else "{}",
        "test_start": start_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "test_end": end_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "effective_start": (
            effective_start.strftime("%Y-%m-%dT%H:%M:%SZ")
            if effective_start
            else None
        ),
        "warmup_bars": warmup_bars,
        # Phase 1A: train/validation are NULL
        "train_start": None,
        "train_end": None,
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
    }

    conn = get_connection(db_path)
    try:
        create_table(conn)
        insert_run(conn, run_data)
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> int:
    """CLI entry point for single-run backtesting.

    Returns:
        Exit code: 0 on success, 1 on failure.
    """
    logging.basicConfig(
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%SZ",
        level=logging.INFO,
    )

    parser = argparse.ArgumentParser(
        description="Run a single backtest (Phase 1A)"
    )
    parser.add_argument(
        "--strategy",
        type=str,
        required=True,
        help="Strategy name (e.g. sma_crossover)",
    )
    parser.add_argument(
        "--start",
        type=str,
        required=True,
        help="Start date (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--end",
        type=str,
        required=True,
        help="End date (YYYY-MM-DD)",
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
    start_date = datetime.strptime(args.start, "%Y-%m-%d").replace(
        tzinfo=timezone.utc
    )
    end_date = datetime.strptime(args.end, "%Y-%m-%d").replace(
        tzinfo=timezone.utc
    )

    strategy_params = {}
    if args.params:
        strategy_params = json.loads(args.params)

    parquet_path = Path(args.parquet) if args.parquet else None

    result = run_backtest(
        strategy_cls=strategy_cls,
        start_date=start_date,
        end_date=end_date,
        strategy_params=strategy_params,
        parquet_path=parquet_path,
        cash=args.cash,
        write_registry=not args.no_registry,
    )

    # Print summary
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
    print(f"Profit Factor:  {result.metrics['profit_factor']:.2f}")
    print(f"Avg Trade Ret:  {result.metrics['avg_trade_return']:.4f}")
    if result.trade_csv_path:
        print(f"Trade Log:      {result.trade_csv_path}")
    print(f"{'='*60}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())

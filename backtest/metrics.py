"""Core performance metrics for backtest results.

Phase 1A metrics computed from equity curve and trade list:
- total_return: (final / initial) - 1
- sharpe_ratio: annualized from hourly returns, rf=0
- max_drawdown: peak-to-trough decline (decimal)
- max_drawdown_duration_hours: longest time below previous peak
- total_trades: count of round-trip trades
- win_rate: winning / total trades
- avg_trade_duration_hours: mean holding period
- avg_trade_return: mean per-trade return after costs
- profit_factor: gross profits / gross losses

NOT in Phase 1A:
- Deflated Sharpe Ratio (Phase 1B evaluate_dsr.py)
- Rolling metrics, Calmar, Sortino
"""

from __future__ import annotations

import logging
import math
from typing import Any

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# Hours per year for annualization (365 * 24)
HOURS_PER_YEAR = 8760


def compute_sharpe_ratio(
    returns: np.ndarray | pd.Series,
    periods_per_year: int = HOURS_PER_YEAR,
) -> float:
    """Compute annualized Sharpe ratio from periodic returns.

    Uses the standard formula: mean(r) / std(r) * sqrt(N)
    where N is periods per year. Risk-free rate is assumed zero.

    Args:
        returns: Array of periodic (hourly) returns.
        periods_per_year: Annualization factor. Default 8766 for hourly data.

    Returns:
        Annualized Sharpe ratio. Returns 0.0 if std is zero or insufficient data.
    """
    returns = np.asarray(returns, dtype=np.float64)
    if len(returns) < 2:
        return 0.0

    std = np.std(returns, ddof=1)
    if std < 1e-15 or np.isnan(std):
        return 0.0

    mean = np.mean(returns)
    return float(mean / std * math.sqrt(periods_per_year))


def compute_max_drawdown(equity_curve: np.ndarray | pd.Series) -> float:
    """Compute maximum drawdown as a decimal fraction.

    Args:
        equity_curve: Time series of portfolio values (not returns).

    Returns:
        Max drawdown as a positive decimal (e.g. 0.20 = 20% decline).
        Returns 0.0 if equity curve is constant or too short.
    """
    equity = np.asarray(equity_curve, dtype=np.float64)
    if len(equity) < 2:
        return 0.0

    peak = np.maximum.accumulate(equity)
    drawdown = (peak - equity) / peak
    # Handle division by zero if peak is 0 (shouldn't happen with real equity)
    drawdown = np.nan_to_num(drawdown, nan=0.0)
    return float(np.max(drawdown))


def compute_max_drawdown_duration_hours(
    equity_curve: pd.Series,
) -> float:
    """Compute the longest drawdown duration in hours.

    Requires a datetime-indexed Series so durations can be measured in
    real time rather than bar counts.

    Args:
        equity_curve: Datetime-indexed Series of portfolio values.

    Returns:
        Duration in hours of the longest drawdown. Returns 0.0 if
        no drawdown occurs.
    """
    if len(equity_curve) < 2:
        return 0.0

    equity = equity_curve.values.astype(np.float64)
    peak = np.maximum.accumulate(equity)
    in_drawdown = equity < peak

    if not np.any(in_drawdown):
        return 0.0

    # Find drawdown periods by grouping consecutive in-drawdown bars
    index = equity_curve.index
    max_duration_hours = 0.0

    dd_start = None
    for i in range(len(equity)):
        if in_drawdown[i]:
            if dd_start is None:
                dd_start = i
        else:
            if dd_start is not None:
                duration = (index[i] - index[dd_start]).total_seconds() / 3600.0
                max_duration_hours = max(max_duration_hours, duration)
                dd_start = None

    # Handle drawdown that extends to the end of the series
    if dd_start is not None:
        duration = (index[-1] - index[dd_start]).total_seconds() / 3600.0
        max_duration_hours = max(max_duration_hours, duration)

    return max_duration_hours


def compute_trade_stats(trades: list[dict[str, Any]]) -> dict[str, Any]:
    """Compute trade-level statistics from a list of trade records.

    Args:
        trades: List of trade dicts, each containing at minimum:
            - pnl: profit/loss after commissions
            - pnl_pct: percentage return after commissions
            - entry_time_utc: fill timestamp (datetime or string)
            - exit_time_utc: fill timestamp (datetime or string)

    Returns:
        Dict with: total_trades, win_rate, avg_trade_return,
        avg_trade_duration_hours, profit_factor.
    """
    n = len(trades)
    if n == 0:
        return {
            "total_trades": 0,
            "win_rate": 0.0,
            "avg_trade_return": 0.0,
            "avg_trade_duration_hours": 0.0,
            "profit_factor": 0.0,
        }

    pnls = [t["pnl"] for t in trades]
    pnl_pcts = [t["pnl_pct"] for t in trades]

    winners = sum(1 for p in pnls if p > 0)
    win_rate = winners / n

    avg_trade_return = float(np.mean(pnl_pcts))

    # Compute average trade duration
    durations_hours = []
    for t in trades:
        entry = pd.Timestamp(t["entry_time_utc"])
        exit_ = pd.Timestamp(t["exit_time_utc"])
        dur = (exit_ - entry).total_seconds() / 3600.0
        durations_hours.append(dur)
    avg_duration = float(np.mean(durations_hours)) if durations_hours else 0.0

    # Profit factor: gross profits / gross losses
    gross_profit = sum(p for p in pnls if p > 0)
    gross_loss = abs(sum(p for p in pnls if p < 0))
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else None

    return {
        "total_trades": n,
        "win_rate": win_rate,
        "avg_trade_return": avg_trade_return,
        "avg_trade_duration_hours": avg_duration,
        "profit_factor": profit_factor,
    }


def compute_all_metrics(
    equity_curve: pd.Series,
    trades: list[dict[str, Any]],
    initial_capital: float,
) -> dict[str, Any]:
    """Compute all Phase 1A metrics from equity curve and trade list.

    This is the main entry point called by the engine after a backtest run.

    Args:
        equity_curve: Datetime-indexed Series of portfolio values,
            covering the post-warmup period only.
        trades: List of trade dicts from the engine's trade collector.
        initial_capital: Starting capital for total_return computation.

    Returns:
        Dict with all Phase 1A metrics.
    """
    final_capital = float(equity_curve.iloc[-1]) if len(equity_curve) > 0 else initial_capital
    total_return = (final_capital / initial_capital) - 1.0

    # Compute hourly returns from equity curve
    if len(equity_curve) >= 2:
        returns = equity_curve.pct_change().dropna().values
    else:
        returns = np.array([])

    sharpe = compute_sharpe_ratio(returns)
    max_dd = compute_max_drawdown(equity_curve.values)
    max_dd_dur = compute_max_drawdown_duration_hours(equity_curve)

    trade_stats = compute_trade_stats(trades)

    metrics = {
        "total_return": total_return,
        "sharpe_ratio": sharpe,
        "max_drawdown": max_dd,
        "max_drawdown_duration_hours": max_dd_dur,
        "initial_capital": initial_capital,
        "final_capital": final_capital,
        **trade_stats,
    }

    logger.info(
        "Metrics: return=%.4f sharpe=%.3f maxDD=%.4f trades=%d win_rate=%.2f PF=%.2f",
        total_return,
        sharpe,
        max_dd,
        trade_stats["total_trades"],
        trade_stats["win_rate"],
        trade_stats["profit_factor"],
    )

    return metrics

"""Simple momentum baseline strategy.

Second baseline to cross-validate the engine with different execution
patterns than SMA crossover (threshold-based vs crossover-based).

Inputs:
    OHLCV 1h bars via Backtrader data feed.

Computation:
    lookback_return = (close[0] / close[-lookback_period]) - 1
    Buy signal: lookback_return > entry_threshold (default +2%)
    Exit signal: lookback_return < exit_threshold (default 0%)

Warmup period:
    lookback_period bars (default 24). Backtrader's prenext()/next()
    split ensures next() is only called after the ROC indicator has
    enough data.

Output:
    Market orders via self.buy() / self.close(). Fills are recorded
    by the engine's trade collector.

Expected behavior (BTC 1h, after 7bps/side fees):
    - More frequent trading than SMA crossover
    - Different holding periods (shorter, threshold-driven)
    - Sharpe between -1.0 and 1.5
"""

from __future__ import annotations

import backtrader as bt

from strategies.template import BaseStrategy


class Momentum(BaseStrategy):
    """Simple momentum (rate of change) strategy."""

    STRATEGY_NAME = "momentum"

    params = (
        ("lookback_period", 24),
        ("entry_threshold", 0.02),   # +2% return to enter
        ("exit_threshold", 0.0),     # 0% return to exit
    )

    @property
    def WARMUP_BARS(self) -> int:  # type: ignore[override]
        """Warmup equals the lookback period."""
        return self.p.lookback_period

    def __init__(self) -> None:
        self.pct_change = bt.indicators.PctChange(
            self.data.close, period=self.p.lookback_period
        )

    def next(self) -> None:
        """Execute trading logic on each bar after warmup.

        PctChange returns decimal (e.g., 0.02 for +2%).
        """
        ret = self.pct_change[0]

        if ret > self.p.entry_threshold and not self.position:
            self.buy()
        elif ret < self.p.exit_threshold and self.position:
            self.close()

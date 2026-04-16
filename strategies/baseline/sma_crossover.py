"""SMA Crossover baseline strategy.

The simplest trend-following strategy:
- Buy when fast SMA crosses above slow SMA (golden cross)
- Sell (close position) when fast SMA crosses below slow SMA (death cross)
- Always fully invested or fully flat (no partial positions)

Inputs:
    OHLCV 1h bars via Backtrader data feed.

Computation:
    fast_sma = SMA(close, fast_period)
    slow_sma = SMA(close, slow_period)
    Buy signal: fast_sma crosses above slow_sma
    Sell signal: fast_sma crosses below slow_sma

Warmup period:
    slow_period bars (default 50). Backtrader's prenext()/next() split
    ensures next() is only called after both SMAs have enough data.

Output:
    Market orders via self.buy() / self.close(). No direct data output;
    fills are recorded by the engine's trade collector.

Expected behavior (BTC 1h, after 7bps/side fees):
    - Sharpe between -0.5 and 1.5
    - Total trades: 5-500 per year
    - If Sharpe > 2.0, engine likely has a bug
"""

from __future__ import annotations

import backtrader as bt

from strategies.template import BaseStrategy


class SMACrossover(BaseStrategy):
    """SMA crossover trend-following strategy."""

    STRATEGY_NAME = "sma_crossover"

    params = (
        ("fast_period", 20),
        ("slow_period", 50),
    )

    @property
    def WARMUP_BARS(self) -> int:  # type: ignore[override]
        """Warmup equals the slow SMA period."""
        return self.p.slow_period

    def __init__(self) -> None:
        self.fast_sma = bt.indicators.SMA(self.data.close, period=self.p.fast_period)
        self.slow_sma = bt.indicators.SMA(self.data.close, period=self.p.slow_period)
        self.crossover = bt.indicators.CrossOver(self.fast_sma, self.slow_sma)

    def next(self) -> None:
        """Execute trading logic on each bar after warmup.

        CrossOver indicator:
            +1.0 = fast crossed above slow (golden cross) → buy
            -1.0 = fast crossed below slow (death cross) → sell
        """
        if self.crossover > 0 and not self.position:
            self.buy()
        elif self.crossover < 0 and self.position:
            self.close()

"""Volatility breakout baseline strategy.

Bollinger-band-style breakout: enters when price breaks above the
upper band, exits on mean reversion back to center.

Inputs:
    OHLCV 1h bars via Backtrader data feed.

Computation:
    center = SMA(close, bb_period)
    std = StdDev(close, bb_period)
    upper_band = center + num_std * std
    Buy signal: close > upper_band (breakout above upper band)
    Exit signal: close < center (mean reversion to center)

Warmup period:
    bb_period bars (default 24). Backtrader's prenext()/next()
    split ensures next() is only called after SMA and StdDev
    have enough data.

Output:
    Market orders via self.buy() / self.close(). Fills are recorded
    by the engine's trade collector.

Expected behavior (BTC 1h, after 7bps/side fees):
    - Structurally disadvantaged: buying breakouts on an already-
      volatile asset tends to buy tops
    - Sharpe between -1.5 and 1.0
    - If Sharpe > 1.5, investigate for bugs before celebrating
"""

from __future__ import annotations

import backtrader as bt

from strategies.template import BaseStrategy


class VolatilityBreakout(BaseStrategy):
    """Bollinger band breakout strategy."""

    STRATEGY_NAME = "volatility_breakout"

    params = (
        ("bb_period", 24),
        ("num_std", 2.0),
    )

    @property
    def WARMUP_BARS(self) -> int:  # type: ignore[override]
        """Warmup equals the Bollinger band period."""
        return self.p.bb_period

    def __init__(self) -> None:
        self.sma = bt.indicators.SMA(self.data.close, period=self.p.bb_period)
        self.std = bt.indicators.StdDev(self.data.close, period=self.p.bb_period)

    def next(self) -> None:
        """Execute trading logic on each bar after warmup.

        Buy on upper band breakout, exit on mean reversion to center.
        """
        upper = self.sma[0] + self.p.num_std * self.std[0]

        if self.data.close[0] > upper and not self.position:
            self.buy()
        elif self.data.close[0] < self.sma[0] and self.position:
            self.close()

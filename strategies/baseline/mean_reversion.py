"""Mean reversion baseline strategy.

Z-score-based contrarian strategy: buys oversold conditions and
exits on reversion to the mean.

Inputs:
    OHLCV 1h bars via Backtrader data feed.

Computation:
    sma = SMA(close, zscore_period)
    std = StdDev(close, zscore_period)
    z = (close - sma) / std
    Buy signal: z < entry_z (default -2.0, oversold)
    Exit signal: z > exit_z (default 0.0, return to mean)

Warmup period:
    zscore_period bars (default 48). Backtrader's prenext()/next()
    split ensures next() is only called after SMA and StdDev
    have enough data.

Output:
    Market orders via self.buy() / self.close(). Fills are recorded
    by the engine's trade collector.

Expected behavior (BTC 1h, after 7bps/side fees):
    - Structurally disadvantaged: mean reversion on a trending
      asset (BTC) buys dips that often continue dipping
    - Sharpe between -1.5 and 1.0
    - If Sharpe > 1.5, investigate for bugs before celebrating
"""

from __future__ import annotations

import backtrader as bt

from strategies.template import BaseStrategy


class MeanReversion(BaseStrategy):
    """Z-score mean reversion strategy."""

    STRATEGY_NAME = "mean_reversion"

    params = (
        ("zscore_period", 48),
        ("entry_z", -2.0),
        ("exit_z", 0.0),
    )

    @property
    def WARMUP_BARS(self) -> int:  # type: ignore[override]
        """Warmup equals the z-score lookback period."""
        return self.p.zscore_period

    def __init__(self) -> None:
        self.sma = bt.indicators.SMA(self.data.close, period=self.p.zscore_period)
        self.std = bt.indicators.StdDev(self.data.close, period=self.p.zscore_period)

    def next(self) -> None:
        """Execute trading logic on each bar after warmup.

        Buy when z-score drops below entry threshold (oversold),
        exit when z-score rises above exit threshold (mean reversion).
        """
        std_val = self.std[0]
        if std_val < 1e-10:
            return  # Avoid division by near-zero std

        z = (self.data.close[0] - self.sma[0]) / std_val

        if z < self.p.entry_z and not self.position:
            self.buy()
        elif z > self.p.exit_z and self.position:
            self.close()

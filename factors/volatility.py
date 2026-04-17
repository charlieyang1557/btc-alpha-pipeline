"""Volatility factors.

- ``realized_vol_24h``: rolling standard deviation of 1-bar returns over
  the last 24 bars. Causal because ``pct_change(1)`` uses only the
  current and prior close, and ``rolling(24)`` is strictly backward-
  looking.
- ``atr_14``: Average True Range over 14 bars. True Range at bar T uses
  high[T], low[T], and close[T-1] (via ``close.shift(+1)``, which is
  causal). ATR is the simple rolling mean of TR over 14 bars — Wilder's
  smoothing is a valid alternative but the simple-SMA form is sufficient
  for D1 and keeps the implementation obviously causal.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from factors.registry import FactorSpec


def compute_realized_vol_24h(df: pd.DataFrame) -> pd.Series:
    """Rolling 24-bar standard deviation of 1-bar log/arithmetic returns.

    Uses ``close.pct_change(1)`` then ``rolling(24).std()``. Population
    vs sample std doesn't matter for causal correctness; we use the
    pandas default (sample, ddof=1).

    Inputs: ``close``.
    Warmup: 24 bars (1 bar lost to ``pct_change``, 23 to the rolling
    window; the first fully-populated rolling std is at position 24).
    Output dtype: float64.
    Null policy: NaN only at positions 0..23.
    """
    returns = df["close"].pct_change(1)
    return returns.rolling(24).std()


def compute_atr_14(df: pd.DataFrame) -> pd.Series:
    """Average True Range over 14 bars (simple rolling mean of TR).

    True Range at bar T = max(high[T] - low[T],
                              |high[T] - close[T-1]|,
                              |low[T]  - close[T-1]|).

    Inputs: ``high``, ``low``, ``close``.
    Warmup: 14 bars (1 lost to ``close.shift(+1)``, 13 more to the
    rolling window; first valid at position 14).
    Output dtype: float64.
    Null policy: NaN only at positions 0..13.
    """
    prev_close = df["close"].shift(1)
    tr1 = df["high"] - df["low"]
    tr2 = (df["high"] - prev_close).abs()
    tr3 = (df["low"] - prev_close).abs()
    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    # tr1 has no NaN but tr2/tr3 are NaN at position 0; pd.concat.max(axis=1)
    # with skipna=True (default) would hide that by returning tr1[0], which
    # is technically non-NaN but semantically wrong. Force NaN where prev_close
    # is NaN.
    true_range = true_range.where(prev_close.notna(), other=np.nan)
    return true_range.rolling(14).mean()


def compute_bb_upper_24_2(df: pd.DataFrame) -> pd.Series:
    """Bollinger upper band: SMA(close, 24) + 2 * StdDev(close, 24).

    Uses **population** standard deviation (ddof=0) to match Backtrader's
    ``bt.indicators.StdDev`` which divides by ``period`` (not ``period-1``).
    This is critical for exact parity with the hand-written
    volatility_breakout baseline.

    Inputs: ``close``.
    Warmup: 23 bars (both ``rolling(24).mean()`` and ``rolling(24).std()``
    produce NaN for positions 0..22).
    Output dtype: float64.
    Null policy: NaN only at positions 0..22.

    Added as a D1 retroactive addition during D5 to support the
    volatility_breakout baseline (entry condition: close > bb_upper_24_2).
    """
    sma = df["close"].rolling(24).mean()
    std = df["close"].rolling(24).std(ddof=0)
    return sma + 2.0 * std


def compute_zscore_48(df: pd.DataFrame) -> pd.Series:
    """48-bar z-score of close: (close - SMA(48)) / StdDev(48).

    Uses **population** standard deviation (ddof=0) to match Backtrader's
    ``bt.indicators.StdDev`` which divides by ``period`` (not ``period-1``).
    This is critical for exact parity with the hand-written mean_reversion
    baseline.

    When the rolling standard deviation is below 1e-10 (effectively zero),
    the z-score is set to 0.0. This matches the hand-written baseline's
    ``if std_val < 1e-10: return`` guard, which skips the bar (no entry
    or exit). A z-score of 0.0 produces the same skip behavior:
    ``0.0 < -2.0`` is False (no entry) and ``0.0 > 0.0`` is False (no
    exit).

    Inputs: ``close``.
    Warmup: 47 bars (``rolling(48)`` produces NaN for positions 0..46;
    first valid at position 47).
    Output dtype: float64.
    Null policy: NaN only at positions 0..46.

    Added as a D1 retroactive addition during D5 to support the
    mean_reversion baseline.
    """
    sma = df["close"].rolling(48).mean()
    std = df["close"].rolling(48).std(ddof=0)

    warmup_mask = sma.isna() | std.isna()
    flat_mask = (std < 1e-10) & (~warmup_mask)

    with np.errstate(divide="ignore", invalid="ignore"):
        z = (df["close"] - sma) / std

    z = z.where(~flat_mask, other=0.0)
    z = z.where(~warmup_mask, other=np.nan)
    return z


SPEC_BB_UPPER_24_2 = FactorSpec(
    name="bb_upper_24_2",
    category="volatility",
    warmup_bars=23,
    inputs=["close"],
    output_dtype="float64",
    compute=compute_bb_upper_24_2,
    docstring=compute_bb_upper_24_2.__doc__ or "",
)

SPEC_ZSCORE_48 = FactorSpec(
    name="zscore_48",
    category="volatility",
    warmup_bars=47,
    inputs=["close"],
    output_dtype="float64",
    compute=compute_zscore_48,
    docstring=compute_zscore_48.__doc__ or "",
)

SPEC_REALIZED_VOL_24H = FactorSpec(
    name="realized_vol_24h",
    category="volatility",
    warmup_bars=24,
    inputs=["close"],
    output_dtype="float64",
    compute=compute_realized_vol_24h,
    docstring=compute_realized_vol_24h.__doc__ or "",
)

SPEC_ATR_14 = FactorSpec(
    name="atr_14",
    category="volatility",
    warmup_bars=14,
    inputs=["high", "low", "close"],
    output_dtype="float64",
    compute=compute_atr_14,
    docstring=compute_atr_14.__doc__ or "",
)

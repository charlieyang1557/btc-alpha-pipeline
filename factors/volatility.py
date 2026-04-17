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

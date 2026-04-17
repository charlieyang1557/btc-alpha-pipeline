"""Momentum factors.

- ``rsi_14``: 14-bar Relative Strength Index, Wilder-style (here
  implemented with simple rolling means of up/down moves — a legitimate
  "Cutler's RSI" variant that is trivially causal via ``rolling(14)``).
  For a perfectly flat 14-bar window (avg_gain == 0 AND avg_loss == 0),
  RSI is defined as 50 (neutral) to avoid 0/0 NaN pollution.
- ``macd_hist``: MACD histogram = (EMA(12) - EMA(26)) - signal, where
  signal = EMA(9) of the MACD line. All EMAs use ``adjust=False`` and
  are causal.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from factors.registry import FactorSpec


def compute_rsi_14(df: pd.DataFrame) -> pd.Series:
    """14-bar RSI using rolling means of up/down moves (Cutler's variant).

    delta = close.diff()
    gain  = delta.clip(lower=0)
    loss  = (-delta).clip(lower=0)
    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()
    rs  = avg_gain / avg_loss
    rsi = 100 - 100 / (1 + rs)

    Flat-window handling: when ``avg_gain == 0`` AND ``avg_loss == 0``,
    RSI is set to 50.0 (neutral). Pure-gain (loss == 0, gain > 0) →
    rs = inf → rsi = 100. Pure-loss (gain == 0, loss > 0) → rs = 0 →
    rsi = 0. These edge cases are finite (no NaN) post-warmup.

    Inputs: ``close``.
    Warmup: 14 bars (``diff`` loses 1 + ``rolling(14)`` loses 13 more;
    first valid at position 14).
    Output dtype: float64.
    Null policy: NaN only at positions 0..13.
    """
    delta = df["close"].diff()
    gain = delta.clip(lower=0.0)
    loss = (-delta).clip(lower=0.0)
    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()

    # Preserve NaN during warmup; handle flat-window post-warmup.
    warmup_mask = avg_gain.isna() | avg_loss.isna()
    flat_mask = (avg_gain == 0) & (avg_loss == 0) & (~warmup_mask)

    with np.errstate(divide="ignore", invalid="ignore"):
        rs = avg_gain / avg_loss
        rsi = 100.0 - 100.0 / (1.0 + rs)

    rsi = rsi.where(~flat_mask, other=50.0)
    rsi = rsi.where(~warmup_mask, other=np.nan)
    return rsi


def compute_macd_hist(df: pd.DataFrame) -> pd.Series:
    """MACD histogram: (EMA(12) - EMA(26)) minus signal=EMA(9) of MACD.

    Inputs: ``close``.
    Warmup: 35 bars (EMA(26) settle ~26 + EMA(9) settle ~9; declared as
    35 to match blueprint convention. Pandas ``ewm(adjust=False)`` begins
    emitting values at position 0, so the null policy tolerates the
    declared warmup without producing post-warmup NaN.).
    Output dtype: float64.
    Null policy: NaN only at positions 0..34 (in practice, no NaN anywhere).
    """
    ema12 = df["close"].ewm(span=12, adjust=False).mean()
    ema26 = df["close"].ewm(span=26, adjust=False).mean()
    macd_line = ema12 - ema26
    signal = macd_line.ewm(span=9, adjust=False).mean()
    return macd_line - signal


SPEC_RSI_14 = FactorSpec(
    name="rsi_14",
    category="momentum",
    warmup_bars=14,
    inputs=["close"],
    output_dtype="float64",
    compute=compute_rsi_14,
    docstring=compute_rsi_14.__doc__ or "",
)

SPEC_MACD_HIST = FactorSpec(
    name="macd_hist",
    category="momentum",
    warmup_bars=35,
    inputs=["close"],
    output_dtype="float64",
    compute=compute_macd_hist,
    docstring=compute_macd_hist.__doc__ or "",
)

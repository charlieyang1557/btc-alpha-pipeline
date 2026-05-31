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

from factors.operators import rolling_backward_percentile
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


def compute_range_over_atr(df: pd.DataFrame) -> pd.Series:
    """Bar range normalized by ATR-14: ``(high - low) / atr_14``.

    A value > 1 means the current bar's high-low range is wider than the
    14-bar average true range (an expansion bar); < 1 means a quiet bar.

    ATR-14 is recomputed internally rather than read from a precomputed
    column so this factor is self-contained and obviously causal:
    ``prev_close = close.shift(1)`` (causal +1 shift), true range
    ``TR = max(high-low, |high-prev_close|, |low-prev_close|)`` forced to
    NaN at position 0 where ``prev_close`` is NaN, then ``rolling(14).mean()``.
    This mirrors ``compute_atr_14`` exactly.

    Inputs: ``high``, ``low``, ``close``.
    Warmup: 14 bars (inherited from ATR-14: 1 bar to ``shift(1)`` plus 13 to
        the rolling mean; first valid at position 14).
    Output dtype: float64.
    Null policy: NaN only at positions 0..13.  Edge: a full 14-bar perfectly-flat
        window would give atr14=0, producing a post-warmup 0/0=NaN (a null-policy
        edge); this cannot occur in the canonical dataset (the 3 known frozen-price
        bars are isolated, not 14 consecutive), and the real-data build confirms
        no post-warmup NaN; a future hardening should guard atr14==0 if this factor
        is ever applied to data that could contain flat windows.
    """
    prev_close = df["close"].shift(1)
    tr1 = df["high"] - df["low"]
    tr2 = (df["high"] - prev_close).abs()
    tr3 = (df["low"] - prev_close).abs()
    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    # Force NaN where prev_close is NaN (position 0) — same guard as
    # compute_atr_14 so the two warmup profiles match exactly.
    true_range = true_range.where(prev_close.notna(), other=np.nan)
    atr14 = true_range.rolling(14).mean()
    return ((df["high"] - df["low"]) / atr14).astype("float64")


SPEC_RANGE_OVER_ATR = FactorSpec(
    name="range_over_atr",
    category="volatility",
    warmup_bars=14,
    inputs=["high", "low", "close"],
    output_dtype="float64",
    compute=compute_range_over_atr,
    docstring=compute_range_over_atr.__doc__ or "",
)


def compute_cdf_realized_vol_720(df: pd.DataFrame) -> pd.Series:
    """30-day (720-bar) backward percentile rank of realized 24h volatility.

    Two-stage causal composition:
      1. ``realized_vol_24h = close.pct_change(1).rolling(24).std()`` —
         the same definition as ``compute_realized_vol_24h``, recomputed
         internally so this factor is self-contained.
      2. ``rolling_backward_percentile(realized_vol_24h, 720)`` — where the
         current realized-vol reading sits within its trailing 30-day
         (720-bar) distribution. 1.0 = highest vol in 30 days, 0.0 = lowest.

    Both stages are strictly backward-looking, so the factor is causal.

    PERFORMANCE: the inner ``rolling(720).apply(...)`` (inside the primitive)
    is O(N * 720) and is the single slowest factor in the library. On the
    full canonical dataset (~55k bars) a ``--force-rebuild`` spends most of
    its wall time here (tens of seconds). This is acceptable for the
    research build; do not "optimize" it into a non-causal vectorized rank.

    Inputs: ``close``.
    Warmup: 743 bars (24 for realized_vol_24h + 719 for the 720-bar
        percentile window; first valid at position 743).
    Output dtype: float64.
    Null policy: NaN only at positions 0..742.
    """
    realized_vol = df["close"].pct_change(1).rolling(24).std()
    return rolling_backward_percentile(realized_vol, 720).astype("float64")


SPEC_CDF_REALIZED_VOL_720 = FactorSpec(
    name="cdf_realized_vol_720",
    category="volatility",
    warmup_bars=743,
    inputs=["close"],
    output_dtype="float64",
    compute=compute_cdf_realized_vol_720,
    docstring=compute_cdf_realized_vol_720.__doc__ or "",
)

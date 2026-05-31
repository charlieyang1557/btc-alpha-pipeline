"""Moving-average factors.

Simple moving averages use ``pandas.Series.rolling(N).mean()``; exponential
moving averages use ``pandas.Series.ewm(span=N, adjust=False).mean()``.
Both are strictly causal (no peek into future bars).

``adjust=False`` is required so the EMA recursion is the "classic"
form ``y[T] = alpha * x[T] + (1 - alpha) * y[T-1]`` rather than the
finite-window adjusted form; the adjusted form divides by the sum of
weights, which is fine causally but introduces a slightly different
convergence profile. We use unadjusted to match standard trading EMAs.
"""

from __future__ import annotations

import pandas as pd

from factors.operators import decay_linear
from factors.registry import FactorSpec


def compute_sma_20(df: pd.DataFrame) -> pd.Series:
    """Simple moving average of close over 20 bars.

    Inputs: ``close``.
    Warmup: 19 bars (``rolling(20)`` is NaN for positions 0..18).
    Output dtype: float64.
    Null policy: NaN only at positions 0..18.
    """
    return df["close"].rolling(20).mean()


def compute_sma_50(df: pd.DataFrame) -> pd.Series:
    """Simple moving average of close over 50 bars.

    Inputs: ``close``.
    Warmup: 49 bars.
    Output dtype: float64.
    Null policy: NaN only at positions 0..48.
    """
    return df["close"].rolling(50).mean()


def compute_ema_12(df: pd.DataFrame) -> pd.Series:
    """Exponential moving average of close, span=12, ``adjust=False``.

    Inputs: ``close``.
    Warmup: 12 bars (declared for stability; pandas returns non-NaN from
    position 0, but the EMA has not converged until ~1 span has elapsed).
    Output dtype: float64.
    Null policy: may be non-NaN at all positions; post-warmup must not be NaN.
    """
    return df["close"].ewm(span=12, adjust=False).mean()


def compute_ema_26(df: pd.DataFrame) -> pd.Series:
    """Exponential moving average of close, span=26, ``adjust=False``.

    Inputs: ``close``.
    Warmup: 26 bars (declared for stability; see ``ema_12``).
    Output dtype: float64.
    Null policy: may be non-NaN at all positions; post-warmup must not be NaN.
    """
    return df["close"].ewm(span=26, adjust=False).mean()


def compute_sma_24(df: pd.DataFrame) -> pd.Series:
    """Simple moving average of close over 24 bars.

    Inputs: ``close``.
    Warmup: 23 bars (``rolling(24)`` is NaN for positions 0..22).
    Output dtype: float64.
    Null policy: NaN only at positions 0..22.

    Added as a D1 retroactive addition during D5 to support the
    volatility_breakout baseline (exit condition: close < sma_24).
    """
    return df["close"].rolling(24).mean()


SPEC_SMA_20 = FactorSpec(
    name="sma_20",
    category="moving_averages",
    warmup_bars=19,
    inputs=["close"],
    output_dtype="float64",
    compute=compute_sma_20,
    docstring=compute_sma_20.__doc__ or "",
)

SPEC_SMA_50 = FactorSpec(
    name="sma_50",
    category="moving_averages",
    warmup_bars=49,
    inputs=["close"],
    output_dtype="float64",
    compute=compute_sma_50,
    docstring=compute_sma_50.__doc__ or "",
)

SPEC_SMA_24 = FactorSpec(
    name="sma_24",
    category="moving_averages",
    warmup_bars=23,
    inputs=["close"],
    output_dtype="float64",
    compute=compute_sma_24,
    docstring=compute_sma_24.__doc__ or "",
)

SPEC_EMA_12 = FactorSpec(
    name="ema_12",
    category="moving_averages",
    warmup_bars=12,
    inputs=["close"],
    output_dtype="float64",
    compute=compute_ema_12,
    docstring=compute_ema_12.__doc__ or "",
)

SPEC_EMA_26 = FactorSpec(
    name="ema_26",
    category="moving_averages",
    warmup_bars=26,
    inputs=["close"],
    output_dtype="float64",
    compute=compute_ema_26,
    docstring=compute_ema_26.__doc__ or "",
)


def compute_decay_linear_close_48(df: pd.DataFrame) -> pd.Series:
    """Linearly-decay-weighted moving average of close over 48 bars.

    Thin wrapper over ``factors.operators.decay_linear(close, 48)``: the
    most recent of the trailing 48 closes gets weight 48, the oldest gets
    weight 1, normalized by ``sum(1..48)``. Strictly causal (trailing
    window, no center, no future bar).

    Inputs: ``close``.
    Warmup: 47 bars (``decay_linear`` is NaN until its first full 48-bar
        window; first valid at position 47).
    Output dtype: float64.
    Null policy: NaN only at positions 0..46.
    """
    return decay_linear(df["close"], 48).astype("float64")


def compute_decay_linear_close_168(df: pd.DataFrame) -> pd.Series:
    """Linearly-decay-weighted moving average of close over 168 bars (1 week).

    Thin wrapper over ``factors.operators.decay_linear(close, 168)``. 168 =
    7 days of hourly bars, so this is a week-scale decay-weighted trend.
    Strictly causal.

    Inputs: ``close``.
    Warmup: 167 bars (first valid at position 167).
    Output dtype: float64.
    Null policy: NaN only at positions 0..166.
    """
    return decay_linear(df["close"], 168).astype("float64")


SPEC_DECAY_LINEAR_CLOSE_48 = FactorSpec(
    name="decay_linear_close_48",
    category="moving_averages",
    warmup_bars=47,
    inputs=["close"],
    output_dtype="float64",
    compute=compute_decay_linear_close_48,
    docstring=compute_decay_linear_close_48.__doc__ or "",
)

SPEC_DECAY_LINEAR_CLOSE_168 = FactorSpec(
    name="decay_linear_close_168",
    category="moving_averages",
    warmup_bars=167,
    inputs=["close"],
    output_dtype="float64",
    compute=compute_decay_linear_close_168,
    docstring=compute_decay_linear_close_168.__doc__ or "",
)

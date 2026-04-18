"""Return factors: fractional price changes over fixed horizons.

All returns are **backward-looking**: the value at bar T is
``(close[T] - close[T-k]) / close[T-k]``. This is causal — each value
depends only on closes at indices ``<= T``.

Null policy: NaN only for the first ``k`` bars (before we have enough
history). After that, non-NaN is enforced by the registry.
"""

from __future__ import annotations

import pandas as pd

from factors.registry import FactorSpec


def compute_return_1h(df: pd.DataFrame) -> pd.Series:
    """Return over 1 bar: (close[T] - close[T-1]) / close[T-1].

    Inputs: ``close``.
    Warmup: 1 bar (first row is NaN from ``pct_change(1)``).
    Output dtype: float64.
    Null policy: NaN at position 0 only.
    """
    return df["close"].pct_change(1)


def compute_return_24h(df: pd.DataFrame) -> pd.Series:
    """Return over 24 bars: (close[T] - close[T-24]) / close[T-24].

    Inputs: ``close``.
    Warmup: 24 bars.
    Output dtype: float64.
    Null policy: NaN at positions 0..23 only.
    """
    return df["close"].pct_change(24)


def compute_return_168h(df: pd.DataFrame) -> pd.Series:
    """Return over 168 bars (1 week): (close[T] - close[T-168]) / close[T-168].

    Inputs: ``close``.
    Warmup: 168 bars.
    Output dtype: float64.
    Null policy: NaN at positions 0..167 only.
    """
    return df["close"].pct_change(168)


SPEC_RETURN_1H = FactorSpec(
    name="return_1h",
    category="returns",
    warmup_bars=1,
    inputs=["close"],
    output_dtype="float64",
    compute=compute_return_1h,
    docstring=compute_return_1h.__doc__ or "",
)

SPEC_RETURN_24H = FactorSpec(
    name="return_24h",
    category="returns",
    warmup_bars=24,
    inputs=["close"],
    output_dtype="float64",
    compute=compute_return_24h,
    docstring=compute_return_24h.__doc__ or "",
)

SPEC_RETURN_168H = FactorSpec(
    name="return_168h",
    category="returns",
    warmup_bars=168,
    inputs=["close"],
    output_dtype="float64",
    compute=compute_return_168h,
    docstring=compute_return_168h.__doc__ or "",
)

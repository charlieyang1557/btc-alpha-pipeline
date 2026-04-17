"""Price identity factors.

- ``close``: raw close price passed through as a factor. Zero warmup.
  This exists so DSL conditions can reference the close price against
  derived factors (e.g., ``close > bb_upper_24_2``). The factor is a
  trivial identity — it adds no computation beyond a dtype cast.

Added as a D1 retroactive addition during D5 (Baselines in DSL) to
support the volatility_breakout baseline, which compares close against
Bollinger upper band and SMA(24).
"""

from __future__ import annotations

import pandas as pd

from factors.registry import FactorSpec


def compute_close(df: pd.DataFrame) -> pd.Series:
    """Identity factor: return close price verbatim.

    Inputs: ``close``.
    Warmup: 0 bars.
    Output dtype: float64.
    Null policy: no NaN at any position (close is always present in
    canonical OHLCV data).
    """
    return df["close"].astype("float64")


SPEC_CLOSE = FactorSpec(
    name="close",
    category="price",
    warmup_bars=0,
    inputs=["close"],
    output_dtype="float64",
    compute=compute_close,
    docstring=compute_close.__doc__ or "",
)

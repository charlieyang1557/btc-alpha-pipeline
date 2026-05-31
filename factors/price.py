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


def compute_intrabar_push(df: pd.DataFrame) -> pd.Series:
    """Intrabar directional push: where close sits in the bar's range.

    ``intrabar_push = (close - open) / ((high - low) + 1e-9)``

    Positive when the bar closed above its open (buying pressure), negative
    below. The ``+ 1e-9`` floor on the denominator keeps a frozen-price bar
    (``open == high == low == close``) finite at 0.0 rather than producing
    NaN/inf — this matters because the canonical dataset contains 3 known
    zero-volume frozen-price bars (see CLAUDE.md Known Data Characteristics).

    All four inputs are observed at bar T's close, so this is causal: it
    uses no prior or future bar.

    Inputs: ``open``, ``high``, ``low``, ``close``.
    Warmup: 0 bars (every bar is fully self-contained).
    Output dtype: float64.
    Null policy: no NaN at any position (denominator is floored at 1e-9).
    """
    rng = (df["high"] - df["low"]) + 1e-9
    return ((df["close"] - df["open"]) / rng).astype("float64")


SPEC_INTRABAR_PUSH = FactorSpec(
    name="intrabar_push",
    category="price",
    warmup_bars=0,
    inputs=["open", "high", "low", "close"],
    output_dtype="float64",
    compute=compute_intrabar_push,
    docstring=compute_intrabar_push.__doc__ or "",
)

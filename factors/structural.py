"""Structural (calendar) factors.

Derived from ``open_time_utc`` only. No price or volume inputs. Zero
warmup — every bar has a valid calendar position from the first row.
"""

from __future__ import annotations

import pandas as pd

from factors.registry import FactorSpec


def compute_hour_of_day(df: pd.DataFrame) -> pd.Series:
    """Hour of day in UTC (0..23), read from ``open_time_utc``.

    Inputs: ``open_time_utc``.
    Warmup: 0 bars.
    Output dtype: int64.
    Null policy: no NaN at any position.
    """
    ts = df["open_time_utc"]
    # Safety: this column is canonical UTC-aware per project rules.
    return ts.dt.hour.astype("int64")


def compute_day_of_week(df: pd.DataFrame) -> pd.Series:
    """Day of week (0=Monday..6=Sunday), read from ``open_time_utc``.

    Inputs: ``open_time_utc``.
    Warmup: 0 bars.
    Output dtype: int64.
    Null policy: no NaN at any position.
    """
    ts = df["open_time_utc"]
    return ts.dt.dayofweek.astype("int64")


SPEC_HOUR_OF_DAY = FactorSpec(
    name="hour_of_day",
    category="structural",
    warmup_bars=0,
    inputs=["open_time_utc"],
    output_dtype="int64",
    compute=compute_hour_of_day,
    docstring=compute_hour_of_day.__doc__ or "",
)

SPEC_DAY_OF_WEEK = FactorSpec(
    name="day_of_week",
    category="structural",
    warmup_bars=0,
    inputs=["open_time_utc"],
    output_dtype="int64",
    compute=compute_day_of_week,
    docstring=compute_day_of_week.__doc__ or "",
)

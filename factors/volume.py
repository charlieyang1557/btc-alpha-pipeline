"""Volume factors.

- ``volume_zscore_24h``: standardized volume over a 24-bar lookback.
  Uses rolling mean and rolling std — both strictly causal.

  Flat-window handling: when rolling std is 0 over the window (all 24
  identical volume values), z-score is set to 0.0 instead of 0/0=NaN.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from factors.registry import FactorSpec


def compute_volume_zscore_24h(df: pd.DataFrame) -> pd.Series:
    """Rolling 24-bar z-score of volume.

    z[T] = (volume[T] - rolling_mean_24(volume)[T]) /
           rolling_std_24(volume)[T]

    When the rolling std is 0 (flat volume window), z is set to 0.0 to
    avoid 0/0 NaN post-warmup.

    Inputs: ``volume``.
    Warmup: 23 bars (``rolling(24)`` first valid at position 23).
    Output dtype: float64.
    Null policy: NaN only at positions 0..22.
    """
    v = df["volume"]
    mean_24 = v.rolling(24).mean()
    std_24 = v.rolling(24).std()

    warmup_mask = mean_24.isna() | std_24.isna()
    flat_mask = (std_24 == 0) & (~warmup_mask)

    with np.errstate(divide="ignore", invalid="ignore"):
        z = (v - mean_24) / std_24

    z = z.where(~flat_mask, other=0.0)
    z = z.where(~warmup_mask, other=np.nan)
    return z


SPEC_VOLUME_ZSCORE_24H = FactorSpec(
    name="volume_zscore_24h",
    category="volume",
    warmup_bars=23,
    inputs=["volume"],
    output_dtype="float64",
    compute=compute_volume_zscore_24h,
    docstring=compute_volume_zscore_24h.__doc__ or "",
)

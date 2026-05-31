"""Funding-rate factors computed on the 8h settlement series (causal, rolling
over settlement units). Carried onto 1h bars downstream by
``factors.funding_align.carry_funding_to_bars`` (Task B4).

All factors are top-level named callables, rolling/causal only (they pass the
G1-G4 leakage guards: G1 static AST no-future-ops scan, G2/G4 future-bar
invariance). Input: a DataFrame with a ``funding_rate`` column ordered by
settlement (``open_time_utc`` ascending). All times UTC.

DESIGN INVARIANT: these factors are tagged ``input_source="funding"`` in the
registry so the build routes them onto the 8h settlement frame, not the 1h
OHLCV frame (which has no ``funding_rate`` column). See
``factors/registry.py`` and ``factors/build_features.py``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def funding_sign(df: pd.DataFrame) -> pd.Series:
    """Sign of the settled funding rate.

    Inputs: ``funding_rate``.
    Computation: ``numpy.sign`` of the per-settlement funding rate
        (positive funding -> +1.0, negative -> -1.0, exactly zero -> 0.0).
        Pointwise; reads only the current settlement.
    Warmup: 0 settlements.
    Output dtype: float64 in {-1.0, 0.0, 1.0}.
    Null policy: NaN ``funding_rate`` -> NaN (``np.sign`` propagates NaN).
    """
    return np.sign(df["funding_rate"]).astype("float64")

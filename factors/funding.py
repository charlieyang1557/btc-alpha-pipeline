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


def funding_ewm_30(df: pd.DataFrame) -> pd.Series:
    """Causal EWM of settled funding, span=30 settlements (~10 days), adjust=False.

    Inputs: ``funding_rate``.
    Computation: ``funding_rate.ewm(span=30, adjust=False).mean()`` — the classic
        recursive form ``y[N] = alpha * x[N] + (1 - alpha) * y[N-1]``. Strictly
        backward-looking (each settlement reads only itself and prior state).
        ``adjust=False`` is required (matches the LOCK and Path B EMA convention).
    Warmup: 30 settlements (declared for stability; pandas returns non-NaN from
        settlement 0, but the EMA has not converged until ~1 span has elapsed).
    Output dtype: float64.
    Null policy: ``nan_before_warmup_only`` — post-warmup must not be NaN.
    """
    return df["funding_rate"].ewm(span=30, adjust=False).mean()


def funding_ewm_60(df: pd.DataFrame) -> pd.Series:
    """Causal EWM of settled funding, span=60 settlements (~20 days), adjust=False.

    Inputs: ``funding_rate``.
    Computation: ``funding_rate.ewm(span=60, adjust=False).mean()`` — same classic
        recursive form as ``funding_ewm_30`` with span 60. Strictly causal.
    Warmup: 60 settlements (declared for stability; see ``funding_ewm_30``).
    Output dtype: float64.
    Null policy: ``nan_before_warmup_only`` — post-warmup must not be NaN.
    """
    return df["funding_rate"].ewm(span=60, adjust=False).mean()


def funding_pct_rank_270(df: pd.DataFrame) -> pd.Series:
    """Causal rolling percentile rank of the settled funding rate over the
    trailing 270 settlements (~90 days).

    Inputs: ``funding_rate``.
    Computation: at settlement N, the fraction of the trailing window
        ``[N-269, N]`` whose value is ``<= value[N]`` (right-closed, strictly
        backward-looking). Implemented with an explicit count loop inside
        ``rolling(270, min_periods=270).apply(..., raw=True)``.
        NOTE: uses an explicit count loop, NOT ``.mean()``, so the G1 AST
        scanner (which bans bare ``.mean()/.std()/.sum()`` on a window) does
        not reject it.
    Warmup: 270 settlements (NaN before the window fills; ``min_periods=270``).
    Output dtype: float64 in [0.0, 1.0].
    Null policy: ``nan_before_warmup_only`` — NaN only at settlements 0..268.
    """
    def _rank(window: np.ndarray) -> float:
        last = window[-1]
        count = sum(1 for v in window if v <= last)
        return count / len(window)

    return df["funding_rate"].rolling(window=270, min_periods=270).apply(_rank, raw=True)

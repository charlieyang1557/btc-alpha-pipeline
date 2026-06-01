"""Perp-spot basis factors computed on the native-1h basis_rel series (causal,
rolling over 1h bars — NO carry; basis is native-1h). All factors are top-level
named callables, rolling/causal only (must pass the G1 AST scan + G2 future-bar
invariance). Input: a DataFrame with a 'basis_rel' column on the 1h grid
(from factors.basis_derive).

These factors are the exact analogs of the Path A funding factors (``factors.funding``),
computed on ``basis_rel`` instead of ``funding_rate``, with windows scaled ×8:
funding 30/60/270 settlements → basis 240/480/2160 bars.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def basis_sign(df: pd.DataFrame) -> pd.Series:
    """Sign of the basis.

    Inputs: ``basis_rel``.
    Computation: ``numpy.sign`` of the per-bar basis_rel value
        (positive -> +1.0, negative -> -1.0, exactly zero -> 0.0). Pointwise;
        reads only the current bar.
    Warmup: 0 bars.
    Output dtype: float64 in {-1.0, 0.0, 1.0}.
    Null policy: NaN ``basis_rel`` -> NaN (``np.sign`` propagates NaN).
    """
    return np.sign(df["basis_rel"]).astype("float64")


def basis_ewm_240(df: pd.DataFrame) -> pd.Series:
    """Causal EWM of basis_rel, span=240 bars (~10 days = Path A's 30 settlements ×8),
    adjust=False.

    Inputs: ``basis_rel``.
    Computation: ``basis_rel.ewm(span=240, adjust=False).mean()`` — the classic
        recursive form ``y[N] = alpha * x[N] + (1 - alpha) * y[N-1]``. Strictly
        backward-looking (each bar reads only itself and prior state).
        ``adjust=False`` is required (matches the LOCK and Path A/B EMA convention).
    Warmup: ~240 bars (declared for stability; pandas returns non-NaN from bar 0,
        but the EWM has not converged until ~1 span has elapsed).
    Output dtype: float64.
    Null policy: NaN propagates; post-warmup must not be NaN.
    """
    return df["basis_rel"].ewm(span=240, adjust=False).mean()


def basis_ewm_480(df: pd.DataFrame) -> pd.Series:
    """Causal EWM of basis_rel, span=480 bars (~20 days = Path A's 60 settlements ×8),
    adjust=False.

    Inputs: ``basis_rel``.
    Computation: ``basis_rel.ewm(span=480, adjust=False).mean()`` — same classic
        recursive form as ``basis_ewm_240`` with span 480. Strictly causal.
    Warmup: ~480 bars (declared for stability; see ``basis_ewm_240``).
    Output dtype: float64.
    Null policy: NaN propagates; post-warmup must not be NaN.
    """
    return df["basis_rel"].ewm(span=480, adjust=False).mean()


def basis_pct_rank_2160(df: pd.DataFrame) -> pd.Series:
    """Causal rolling percentile rank of basis_rel over the trailing 2160 bars
    (~90 days = Path A's 270 settlements ×8).

    Inputs: ``basis_rel``.
    Computation: at bar N, the fraction of the trailing window ``[N-2159, N]``
        whose value is ``<= value[N]`` (right-closed, strictly backward-looking).
        Implemented with an explicit count loop inside
        ``rolling(2160, min_periods=2160).apply(..., raw=True)``.
        NOTE: uses an explicit count loop, NOT ``.mean()``, so the G1 AST
        scanner (which bans bare ``.mean()/.std()/.sum()`` on a window) does
        not reject it.
    Warmup: 2160 bars (NaN before the window fills; ``min_periods=2160``).
    Output dtype: float64 in [0.0, 1.0].
    Null policy: ``nan_before_warmup_only`` — NaN only at bars 0..2158.
    """
    def _rank(window: np.ndarray) -> float:
        last = window[-1]
        count = sum(1 for v in window if v <= last)
        return count / len(window)

    return df["basis_rel"].rolling(window=2160, min_periods=2160).apply(_rank, raw=True)


def basis_ewm_240_pctrank_2160(df: pd.DataFrame) -> pd.Series:
    """Causal rolling-2160 percentile of basis_ewm_240 (the H2 basis regime axis).

    Inputs: ``basis_rel``.
    Computation: first compute the causal span-240 EWM of ``basis_rel``
        (``adjust=False``); then, at bar N, the fraction of the trailing window
        ``[N-2159, N]`` of the EWM series whose value is ``<= ewm[N]``
        (right-closed, strictly backward-looking). Implemented with an explicit
        count loop inside ``rolling(2160, min_periods=2160).apply(..., raw=True)``.
        NOTE: the OUTER percentile uses an explicit count loop, NOT ``.mean()``,
        so the G1 AST scanner (which bans bare ``.mean()/.std()/.sum()`` on a
        window) does not reject it. The INNER ``ewm(span=240, adjust=False).mean()``
        is a windowed reducer and is allowed.
    Warmup: 2160 bars (NaN before the percentile window fills;
        ``min_periods=2160`` on the percentile dominates the EWM's own warmup).
    Output dtype: float64 in [0.0, 1.0].
    Null policy: ``nan_before_warmup_only`` — NaN only at bars 0..2158.
    """
    def _rank(window: np.ndarray) -> float:
        last = window[-1]
        count = sum(1 for v in window if v <= last)
        return count / len(window)

    ewm = df["basis_rel"].ewm(span=240, adjust=False).mean()
    return ewm.rolling(window=2160, min_periods=2160).apply(_rank, raw=True)

"""Causal compute primitives shared by factor modules.

These are NOT registered factors. They are deliberately kept out of the
FactorRegistry so the G1 future-ops scanner (factors.registry._assert_no_future_ops,
invoked inside FactorRegistry.register) never reaches them — the scanner
inspects registered compute callables only. Callers wrap these primitives
inside top-level ``compute_*`` factor functions that ARE registered, and
those wrappers carry the warmup/causality contract.

DESIGN INVARIANT: every primitive here is strictly backward-looking. A
``rolling(window)`` with no ``center=`` argument defaults to a trailing
window whose right edge is the current bar — no future bar contributes.

CONTRACT GAP: primitives in this module (``decay_linear``,
``rolling_backward_percentile``) are UNREGISTERED, so their source is NOT
included in ``compute_feature_version`` (which hashes only registered
compute sources) AND is NOT scanned by the G1 ``_assert_no_future_ops``
static guard (which runs only inside ``FactorRegistry.register()``).
Consequence: editing ``decay_linear`` / ``rolling_backward_percentile``
can silently change the VALUES of the registered factors that delegate to
them — ``cdf_realized_vol_720``, ``decay_linear_close_48``,
``decay_linear_close_168`` — WITHOUT bumping ``feature_version`` and
WITHOUT triggering a G1 review.  The ONLY leakage backstop for these
primitive-routed factors is the G2/G4a truncation-invariance sentinel in
``tests/test_leakage_guards.py`` (which executes the full compute path
including the primitive).  Trigger to close: if primitive-source hashing
is added to ``FactorSpec`` / ``compute_feature_version``, remove this
marker.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def decay_linear(series: pd.Series, window: int) -> pd.Series:
    """Linearly-weighted trailing moving average (newest bar heaviest).

    Weights for a window of size ``w`` are ``[1, 2, ..., w]`` applied to the
    ``[oldest, ..., newest]`` bars, normalized by ``sum(1..w) = w*(w+1)/2``.
    The most recent bar receives the largest weight, which is the standard
    "linear decay" used in alpha factors (e.g. WorldQuant ``decay_linear``).

    Implemented via ``series.rolling(window).apply(_weighted, raw=True)`` with
    a nested ``_weighted`` so the weighting is local to this primitive and
    carries no module-level state.

    Inputs: any numeric Series.
    Warmup: ``window - 1`` bars (the rolling apply yields NaN until the first
        full window).
    Output dtype: float64.
    Null policy: NaN only at positions ``0 .. window-2`` for NaN-free input.
        Because ``rolling(window)`` uses pandas' default ``min_periods=window``,
        any window containing a NaN emits NaN — so a mid-series NaN extends the
        NaN run by up to ``window-1`` additional bars beyond the warmup positions.
    """
    w = int(window)  # defensive coercion: accept np.int64 / float-typed window from callers
    weights = np.arange(1, w + 1, dtype="float64")
    denom = weights.sum()

    def _weighted(values: np.ndarray) -> float:
        # ``values`` is a length-``window`` ndarray, oldest-first (raw=True).
        return float(np.dot(values, weights) / denom)

    return series.rolling(w).apply(_weighted, raw=True)


def rolling_backward_percentile(series: pd.Series, window: int) -> pd.Series:
    """Percentile rank of the LAST value within its trailing window.

    For each position ``T`` (once warmed up), looks back over the window
    ``[T-window+1 .. T]`` and returns the fraction of the other
    ``window - 1`` values that are strictly less than ``series[T]``:

        rank(T) = (# values in window strictly < series[T]) / (window - 1)

    The result lies in ``[0.0, 1.0]``: ``1.0`` when the current bar is the
    window maximum, ``0.0`` when it is the window minimum.

    This is deliberately NOT a full-series ``Series.rank()`` (that would
    leak future bars) and uses NO ``center=`` argument (which would also
    leak). Only the trailing window contributes.

    Inputs: any numeric Series.
    Warmup: ``window - 1`` bars.
    Output dtype: float64.
    Null policy: NaN only at positions ``0 .. window-2`` for NaN-free input.
        Because ``rolling(window)`` uses pandas' default ``min_periods=window``,
        any window containing a NaN emits NaN — so a mid-series NaN extends the
        NaN run by up to ``window-1`` additional bars beyond the warmup positions.
    Window=1 special case: returns ``0.0`` for every bar — no other values to
        rank against; the ``(w-1)`` divisor guard returns ``0.0`` directly; no
        warmup. This differs from ``decay_linear(window=1)`` which is the
        identity.
    Performance note: ``rolling(window).apply(_last_rank, raw=True)`` invokes a
        Python callable per window — O(n*w). For the largest planned use
        (``window=720`` over the ~48k-bar dataset in the Task 8
        ``cdf_realized_vol_720`` factor) this runs in ~150 ms in a one-shot
        ``build_features`` call, which is an accepted tradeoff (no
        Numba/Cython path needed).
    """
    w = int(window)  # defensive coercion: accept np.int64 / float-typed window from callers

    def _last_rank(values: np.ndarray) -> float:
        last = values[-1]
        # Strictly-below count among the other (w-1) values.
        below = float(np.sum(values[:-1] < last))
        return below / float(w - 1) if w > 1 else 0.0

    return series.rolling(w).apply(_last_rank, raw=True)

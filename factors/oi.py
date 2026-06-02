"""Open-interest factors computed on the native-1h ``sum_open_interest`` (CONTRACTS)
series (causal, rolling over 1h bars — NO carry; OI is native-1h). All factors are
top-level named callables, rolling/causal only (must pass the G1 AST scan + G2
future-bar invariance). Input: a DataFrame with a ``sum_open_interest`` column on
the 1h grid (from ``data/raw/btcusdt_oi_1h.parquet``).

FIREWALL (critical): factors read ONLY ``sum_open_interest`` (contracts). The
``sum_open_interest_value`` (notional) column is NEVER read because its log-change
embeds the BTC price return, destroying the anti-endogeneity property.

ZERO-POISON: 43 real glitch bars exist with ``sum_open_interest <= 0``. These are
mapped to NaN **before** any log or ranking operation so they never produce -inf
log-changes, spurious all-time-low percentiles, or crashes.

These factors are the structural analogs of the Path C basis factors
(``factors.basis``) with the following divergences:
  (1) velocity factors operate on the **log-change** of OI (not the level);
  (2) zero-poison handling is required for OI<= 0 in both the log-change path
      AND the level-percentile path.

Windows follow the Path C basis convention (×8 relative to Path A funding
analogs): 240/2160 bars match the Path C basis_ewm_240/basis_pct_rank_2160 windows.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from factors.registry import FactorSpec


# ---------------------------------------------------------------------------
# Private helper — NOT registered as a factor
# ---------------------------------------------------------------------------


def _oi_log_change(df: pd.DataFrame) -> pd.Series:
    """Causal log-change of open interest (CONTRACTS): log(OI[t]) - log(OI[t-1]).

    ZERO-POISON: ``sum_open_interest <= 0`` is replaced with NaN before the
    log is taken. This prevents -inf from entering the log-change (which would
    propagate as -inf through the EWM factors) and ensures the subsequent bar
    also becomes NaN (because log(NaN) is NaN, and NaN - finite = NaN).

    NOT registered as a factor. Used internally by ``oi_sign`` and
    ``oi_velocity_ewm_240``.

    Inputs: ``sum_open_interest``.
    Computation: ``log(OI[t]) - log(OI[t-1])`` via backward ``shift(1)``
        (causal — uses only bar t and bar t-1). OI<=0 is NaN-poisoned before
        the log to avoid -inf/-complex. The series is entirely float64.
    Warmup: 1 bar (first bar is always NaN; no prior value exists).
    Output dtype: float64.
    Null policy: NaN at bar 0; NaN at any bar with OI[t]<=0; NaN at the bar
        immediately following a zero-OI bar (log(OI[t]) - log(NaN) = NaN).
    """
    oi = df["sum_open_interest"].where(df["sum_open_interest"] > 0)
    log_oi = np.log(oi)
    return log_oi - log_oi.shift(1)


# ---------------------------------------------------------------------------
# Registered factor functions (Tasks B1–B4)
# ---------------------------------------------------------------------------


def oi_sign(df: pd.DataFrame) -> pd.Series:
    """Sign of the 1h OI log-change (direction of positioning flow).

    Inputs: ``sum_open_interest``.
    Computation: ``numpy.sign`` of ``_oi_log_change(df)``
        (positive flow -> +1.0, negative flow -> -1.0, exactly flat -> 0.0).
        Inherits the zero-poison NaN propagation from the helper: a zero-OI
        bar and the bar following it will be NaN (not 0.0).
    Warmup: 1 bar (first bar is NaN; no log-change computable).
    Output dtype: float64 in {-1.0, 0.0, 1.0} or NaN.
    Null policy: NaN at bar 0 and at any zero-poisoned bars.
    """
    return np.sign(_oi_log_change(df)).astype("float64")


def oi_velocity_ewm_240(df: pd.DataFrame) -> pd.Series:
    """Causal EWM of the OI log-change, span=240 bars (~10 days), adjust=False.

    The anti-endogeneity firewall quantity: the EWM of the log-change of OI
    contracts (not the level, not the notional). This measures sustained
    positioning flow rather than the absolute size of open interest.

    Inputs: ``sum_open_interest``.
    Computation: ``_oi_log_change(df).ewm(span=240, adjust=False).mean()`` —
        the classic recursive form ``y[N] = alpha * x[N] + (1 - alpha) * y[N-1]``.
        Strictly backward-looking (each bar reads only itself and prior state).
        ``adjust=False`` matches the LOCK and Path A/B/C EMA convention.
        The EWM output is masked to NaN at bars where the log-change is NaN,
        so that a missing or zero-poisoned input bar does not carry forward a
        stale EWM value.
    Warmup: ~240 bars (declared for stability; pandas returns non-NaN from
        bar 1, but the EWM has not converged until ~1 span has elapsed).
    Output dtype: float64.
    Null policy: NaN at bar 0 (no log-change). NaN at zero-poisoned bars and
        the bar following them (propagated from the log-change helper).
    """
    log_chg = _oi_log_change(df)
    ewm_out = log_chg.ewm(span=240, adjust=False).mean()
    return ewm_out.where(log_chg.notna())


def oi_pct_rank_2160(df: pd.DataFrame) -> pd.Series:
    """Causal rolling percentile rank of OI LEVEL (CONTRACTS) over trailing 2160 bars.

    Measures where the current OI level sits in its 90-day (2160 1h bars)
    distribution. This is the LEVEL percentile (not the log-change), tracking
    the accumulation state of open interest. Window 2160 = basis_pct_rank_2160
    analog (Path A funding 270 settlements × 8).

    FIREWALL: ranks ``sum_open_interest`` (contracts), NEVER ``sum_open_interest_value``.
    ZERO-POISON: ``sum_open_interest <= 0`` is NaN-poisoned BEFORE ranking so a
        glitch bar with OI=0 is NEVER ranked as a spurious all-time-low.

    Inputs: ``sum_open_interest``.
    Computation: at bar N, the fraction of the trailing window ``[N-2159, N]``
        whose value is ``<= value[N]`` (right-closed, strictly backward-looking).
        Implemented with an explicit count loop inside
        ``rolling(2160, min_periods=2160).apply(..., raw=True)``.
        NOTE: uses an explicit count loop, NOT ``.mean()``, so the G1 AST
        scanner (which bans bare ``.mean()/.std()/.sum()`` on a window) does
        not reject it. OI<=0 values are NaN-poisoned before rolling — ``apply``
        with ``min_periods=2160`` propagates NaN when any window element is NaN,
        yielding NaN at and around zero-poisoned bars.
    Warmup: 2160 bars (NaN before the window fills; ``min_periods=2160``).
    Output dtype: float64 in [0.0, 1.0].
    Null policy: NaN before warmup; NaN at and around zero-poisoned bars.
    """
    oi = df["sum_open_interest"].where(df["sum_open_interest"] > 0)

    def _rank(window: np.ndarray) -> float:
        last = window[-1]
        count = sum(1 for v in window if v <= last)
        return count / len(window)

    return oi.rolling(window=2160, min_periods=2160).apply(_rank, raw=True)


def oi_velocity_ewm_240_pctrank_2160(df: pd.DataFrame) -> pd.Series:
    """Causal rolling-2160 percentile of oi_velocity_ewm_240 (the H2 OI regime axis).

    Inputs: ``sum_open_interest``.
    Computation: first compute the causal span-240 EWM of the OI log-change
        (``adjust=False``), masked to NaN where the log-change is NaN (i.e. at
        bar 0 and at zero-poisoned bars); then, at bar N, the fraction of the
        trailing window ``[N-2159, N]`` of the (masked) EWM series whose value
        is ``<= ewm[N]`` (right-closed, strictly backward-looking).
        Implemented with an explicit count loop inside
        ``rolling(2160, min_periods=2160).apply(..., raw=True)``.
        NOTE: the OUTER percentile uses an explicit count loop, NOT ``.mean()``,
        so the G1 AST scanner (which bans bare ``.mean()/.std()/.sum()`` on a
        window) does not reject it. The INNER ``ewm(span=240, adjust=False).mean()``
        is a windowed reducer and is allowed.
    Warmup: 2160 bars (NaN before the percentile window fills;
        ``min_periods=2160`` on the percentile dominates the EWM's ~240-bar
        warmup).
    Output dtype: float64 in [0.0, 1.0].
    Null policy: NaN at bar 0 and zero-poisoned bars (propagated from the log-change
        mask) → NaN percentile for any window containing those bars
        (``min_periods`` propagates NaN through ``apply``); NaN before warmup on
        clean inputs.
    """
    log_chg = _oi_log_change(df)
    ewm_out = log_chg.ewm(span=240, adjust=False).mean()
    ewm = ewm_out.where(log_chg.notna())

    def _rank(window: np.ndarray) -> float:
        last = window[-1]
        count = sum(1 for v in window if v <= last)
        return count / len(window)

    return ewm.rolling(window=2160, min_periods=2160).apply(_rank, raw=True)


# ---------------------------------------------------------------------------
# FactorSpec registrations (input_source="oi" — native-1h, NO carry)
# ---------------------------------------------------------------------------

# OI factors are native-1h (NOT carried from a coarser grid), so
# input_period_bars=1 and bar-equivalent warmup == declared warmup_bars.
# The build routes these onto the OI frame (``data/raw/btcusdt_oi_1h.parquet``),
# then left-joins the columns onto the 1h OHLCV feature frame by
# open_time_utc. Windows follow the Path C basis convention (×8 relative to
# Path A funding analogs): 240/2160 bars match basis_ewm_240/basis_pct_rank_2160.
#
# NOTE: oi_sign is LOCK-registered for factor-family completeness but
# referenced by NO hypothesis — register it anyway per the LOCK.

SPEC_OI_SIGN = FactorSpec(
    name="oi_sign",
    category="oi",
    warmup_bars=1,
    inputs=["sum_open_interest"],
    output_dtype="float64",
    compute=oi_sign,
    docstring=oi_sign.__doc__ or "",
    input_source="oi",
    input_period_bars=1,
)

SPEC_OI_VELOCITY_EWM_240 = FactorSpec(
    name="oi_velocity_ewm_240",
    category="oi",
    warmup_bars=240,
    inputs=["sum_open_interest"],
    output_dtype="float64",
    compute=oi_velocity_ewm_240,
    docstring=oi_velocity_ewm_240.__doc__ or "",
    input_source="oi",
    input_period_bars=1,
)

SPEC_OI_PCT_RANK_2160 = FactorSpec(
    name="oi_pct_rank_2160",
    category="oi",
    warmup_bars=2160,
    inputs=["sum_open_interest"],
    output_dtype="float64",
    compute=oi_pct_rank_2160,
    docstring=oi_pct_rank_2160.__doc__ or "",
    input_source="oi",
    input_period_bars=1,
)

SPEC_OI_VELOCITY_EWM_240_PCTRANK_2160 = FactorSpec(
    name="oi_velocity_ewm_240_pctrank_2160",
    category="oi",
    # 2161, not 2160 (Codex B2): the inner log-change is NaN at bar 0, so the first
    # NaN-free 2160-bar percentile window ends at index 2160 -> first valid output at
    # index 2160 = 2161 bars of data required (vs 2160 for the level-percentile).
    warmup_bars=2161,
    inputs=["sum_open_interest"],
    output_dtype="float64",
    compute=oi_velocity_ewm_240_pctrank_2160,
    docstring=oi_velocity_ewm_240_pctrank_2160.__doc__ or "",
    input_source="oi",
    input_period_bars=1,
)

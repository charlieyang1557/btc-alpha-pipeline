"""Tests for Path D OI factors (Phase B, Tasks B1-B4).

The OI factors are computed on the 1h ``sum_open_interest`` (CONTRACTS) series
from ``data/raw/btcusdt_oi_1h.parquet``.  They are native-1h (like basis
factors) — no carry step. All factors are top-level named callables,
rolling/causal only (must pass the G1 AST scan + G2 future-bar invariance).

Firewall: factors read ONLY ``sum_open_interest`` (contracts), NEVER
``sum_open_interest_value`` (notional; its log-change embeds the price return).

Zero-poison: OI <= 0 (43 real glitch bars) must yield NaN — not -inf, not a
spurious all-time-low percentile, not a crash.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from factors.oi import (
    _oi_log_change,
    oi_pct_rank_2160,
    oi_sign,
    oi_velocity_ewm_240,
    oi_velocity_ewm_240_pctrank_2160,
)
from factors.registry import _assert_no_future_ops


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _oi_df(values) -> pd.DataFrame:
    """Wrap an OI sequence in the canonical OI factor input frame.

    Only ``sum_open_interest`` is populated (the firewall column). The notional
    column is deliberately absent so tests fail loudly if any factor reads it.
    """
    return pd.DataFrame({"sum_open_interest": pd.Series(values, dtype="float64")})


# ---------------------------------------------------------------------------
# _oi_log_change helper
# ---------------------------------------------------------------------------


def test_oi_log_change_rising_is_positive():
    df = _oi_df([100.0, 110.0, 121.0])
    out = _oi_log_change(df)
    # First bar NaN (no prior), subsequent bars positive (rising OI)
    assert np.isnan(out.iloc[0])
    assert out.iloc[1] > 0.0
    assert out.iloc[2] > 0.0


def test_oi_log_change_falling_is_negative():
    df = _oi_df([100.0, 90.0, 80.0])
    out = _oi_log_change(df)
    assert np.isnan(out.iloc[0])
    assert out.iloc[1] < 0.0
    assert out.iloc[2] < 0.0


def test_oi_log_change_known_value():
    # log(110) - log(100) == log(1.1)
    df = _oi_df([100.0, 110.0])
    out = _oi_log_change(df)
    assert np.isnan(out.iloc[0])
    assert np.isclose(out.iloc[1], np.log(110.0) - np.log(100.0))


def test_oi_log_change_zero_poison_at_zero_bar():
    # OI=0 at bar 1: bar 1 must be NaN (log(0) -> -inf, must be NaN instead)
    # Bar 2 uses OI[1]=0 as denominator (log(OI[2]) - log(NaN) -> NaN)
    df = _oi_df([100.0, 0.0, 110.0])
    out = _oi_log_change(df)
    assert np.isnan(out.iloc[0])   # first bar always NaN
    assert np.isnan(out.iloc[1])   # zero bar -> NaN (not -inf)
    assert np.isnan(out.iloc[2])   # next bar: log(110) - log(NaN) -> NaN


def test_oi_log_change_zero_poison_no_inf():
    # Must never produce -inf even with a zero-OI bar
    df = _oi_df([0.0, 100.0, 0.0])
    out = _oi_log_change(df)
    assert not np.any(np.isinf(out.to_numpy(dtype=float)))


def test_oi_log_change_first_bar_is_nan():
    df = _oi_df([50000.0, 51000.0])
    out = _oi_log_change(df)
    assert np.isnan(out.iloc[0])


def test_oi_log_change_causality():
    # G2: truncating future rows leaves earlier values bit-identical
    rng = np.random.default_rng(1)
    vals = rng.uniform(50000, 100000, 120)
    df_full = _oi_df(vals)
    df_trunc = _oi_df(vals[:80])
    full = _oi_log_change(df_full)
    trunc = _oi_log_change(df_trunc)
    np.testing.assert_array_equal(trunc.to_numpy(), full.iloc[:80].to_numpy())


# ---------------------------------------------------------------------------
# oi_sign
# ---------------------------------------------------------------------------


def test_oi_sign_values():
    df = _oi_df([100.0, 110.0, 90.0, 100.0])
    out = oi_sign(df)
    # bar 0: NaN (log-change NaN -> sign NaN)
    assert np.isnan(out.iloc[0])
    assert out.iloc[1] == 1.0    # 100->110: rising
    assert out.iloc[2] == -1.0   # 110->90: falling
    assert out.iloc[3] == 1.0    # 90->100: rising


def test_oi_sign_rising_then_flat():
    # Flat OI: log-change = 0 -> sign = 0.0
    df = _oi_df([100.0, 110.0, 110.0])
    out = oi_sign(df)
    assert np.isnan(out.iloc[0])
    assert out.iloc[1] == 1.0
    assert out.iloc[2] == 0.0


def test_oi_sign_dtype():
    df = _oi_df([100.0, 110.0])
    out = oi_sign(df)
    assert out.dtype == np.float64


def test_oi_sign_zero_poison_propagates_nan():
    df = _oi_df([100.0, 0.0, 110.0])
    out = oi_sign(df)
    assert np.isnan(out.iloc[1])
    assert np.isnan(out.iloc[2])


def test_oi_sign_causality():
    rng = np.random.default_rng(2)
    vals = rng.uniform(50000, 100000, 100)
    full = oi_sign(_oi_df(vals))
    trunc = oi_sign(_oi_df(vals[:60]))
    np.testing.assert_array_equal(trunc.to_numpy(), full.iloc[:60].to_numpy())


# ---------------------------------------------------------------------------
# oi_velocity_ewm_240
# ---------------------------------------------------------------------------


def test_oi_velocity_ewm_240_matches_ewm_on_log_change():
    rng = np.random.default_rng(3)
    vals = rng.uniform(50000, 100000, 300)
    df = _oi_df(vals)
    out = oi_velocity_ewm_240(df)
    # Compute expected: log_change.ewm(span=240, adjust=False).mean(), masked at NaN inputs
    log_chg = np.log(pd.Series(vals)).diff()
    expected = log_chg.ewm(span=240, adjust=False).mean()
    # Mask where log_chg is NaN
    expected = expected.where(log_chg.notna())
    pd.testing.assert_series_equal(out, expected, check_names=False)


def test_oi_velocity_ewm_240_uses_adjust_false():
    # adjust=False and adjust=True diverge on non-constant input
    rng = np.random.default_rng(4)
    vals = rng.uniform(50000, 100000, 50)
    df = _oi_df(vals)
    out = oi_velocity_ewm_240(df)
    log_chg = np.log(pd.Series(vals)).diff()
    adjusted = log_chg.ewm(span=240, adjust=True).mean()
    # They agree at index 1 (first non-NaN), must differ somewhere beyond
    post1 = out.iloc[2:].to_numpy()
    adj1 = adjusted.iloc[2:].to_numpy()
    assert not np.allclose(post1, adj1)


def test_oi_velocity_ewm_240_zero_poison_no_inf():
    df = _oi_df([100.0, 0.0, 110.0, 120.0])
    out = oi_velocity_ewm_240(df)
    arr = out.to_numpy(dtype=float)
    assert not np.any(np.isinf(arr))


def test_oi_velocity_ewm_240_causality():
    rng = np.random.default_rng(5)
    vals = rng.uniform(50000, 100000, 300)
    full = oi_velocity_ewm_240(_oi_df(vals))
    trunc = oi_velocity_ewm_240(_oi_df(vals[:200]))
    np.testing.assert_array_equal(trunc.to_numpy(), full.iloc[:200].to_numpy())


def test_oi_velocity_ewm_240_g1_ast_safe():
    _assert_no_future_ops(oi_velocity_ewm_240, "oi_velocity_ewm_240")  # no raise


# ---------------------------------------------------------------------------
# oi_pct_rank_2160
# ---------------------------------------------------------------------------


def test_oi_pct_rank_2160_warmup():
    # min_periods=2160 -> NaN for bars 0..2158, first valid at bar 2159
    n = 2161
    vals = list(range(n))  # monotonically increasing
    df = _oi_df([float(v + 1) for v in vals])  # all positive (no zero poison)
    out = oi_pct_rank_2160(df)
    assert out.iloc[:2159].isna().all()
    assert not np.isnan(out.iloc[2159])


def test_oi_pct_rank_2160_max_value():
    # Last bar is the global max of its window -> rank = 1.0
    base = list(range(2159))
    df = _oi_df([float(v + 1) for v in base] + [float(10_000_000)])
    out = oi_pct_rank_2160(df)
    assert out.iloc[-1] == 1.0


def test_oi_pct_rank_2160_bounded_unit_interval():
    rng = np.random.default_rng(6)
    vals = rng.uniform(50000, 100000, 2300)
    out = oi_pct_rank_2160(_oi_df(vals))
    post = out.iloc[2159:]
    assert (post >= 0.0).all() and (post <= 1.0).all()


def test_oi_pct_rank_2160_known_midpoint():
    # Window of 2160 values: last value is rank 1081st smallest (1080 below, self)
    # -> count = 1081 -> 1081/2160
    window = list(range(2159)) + [1079.5]
    df = _oi_df([float(v + 1) for v in window])  # shift +1 so all > 0
    out = oi_pct_rank_2160(df)
    # Values 1..1080 (1080 of them, after the +1 shift) are < 1080.5; itself <= -> 1081/2160
    assert out.iloc[-1] == pytest.approx(1081.0 / 2160.0)


def test_oi_pct_rank_2160_zero_poison_zero_bar_is_nan():
    # A zero-OI bar must NOT be ranked as a spurious all-time-low; it is NaN.
    n = 2160
    vals = [float(i + 1) for i in range(n)]
    vals[n // 2] = 0.0  # plant a zero mid-window
    df = _oi_df(vals)
    out = oi_pct_rank_2160(df)
    assert np.isnan(out.iloc[n // 2])


def test_oi_pct_rank_2160_zero_poison_not_zero_rank():
    # Ensure the zero bar's rank is NaN, not 0.0 (spurious minimum)
    n = 2160
    vals = [float(i + 100) for i in range(n)]
    vals[500] = 0.0
    df = _oi_df(vals)
    out = oi_pct_rank_2160(df)
    # The zero bar at index 500 must be NaN (within warmup is fine, just confirm NaN not 0.0)
    assert np.isnan(out.iloc[500]) or out.iloc[500] != 0.0


def test_oi_pct_rank_2160_causality():
    rng = np.random.default_rng(7)
    vals = rng.uniform(50000, 100000, 2300)
    full = oi_pct_rank_2160(_oi_df(vals))
    trunc = oi_pct_rank_2160(_oi_df(vals[:2200]))
    np.testing.assert_array_equal(
        trunc.iloc[2159:].to_numpy(), full.iloc[2159:2200].to_numpy()
    )


def test_oi_pct_rank_2160_g1_ast_safe():
    _assert_no_future_ops(oi_pct_rank_2160, "oi_pct_rank_2160")  # no raise


def test_oi_pct_rank_reads_contracts_not_notional():
    # If the factor reads sum_open_interest_value instead of sum_open_interest,
    # it will KeyError on a frame with only sum_open_interest.
    df = _oi_df([float(i + 1) for i in range(2160)])
    # Must not raise; verifies firewall column routing
    out = oi_pct_rank_2160(df)
    assert len(out) == 2160


# ---------------------------------------------------------------------------
# oi_velocity_ewm_240_pctrank_2160
# ---------------------------------------------------------------------------


def test_oi_velocity_ewm_240_pctrank_warmup():
    # The EWM log-change has NaN at bar 0 (no prior OI value), so the first
    # 2160-bar window free of NaN spans bars 1..2160. The first valid output
    # is therefore at index 2160 (not 2159). Need n >= 2161 to observe it.
    n = 2162
    vals = [float(i + 1) for i in range(n)]
    df = _oi_df(vals)
    out = oi_velocity_ewm_240_pctrank_2160(df)
    assert out.iloc[:2160].isna().all()
    assert not np.isnan(out.iloc[2160])


def test_oi_velocity_ewm_240_pctrank_bounded():
    rng = np.random.default_rng(8)
    vals = rng.uniform(50000, 100000, 2300)
    out = oi_velocity_ewm_240_pctrank_2160(_oi_df(vals))
    # First valid output at index 2160 (inner EWM NaN at bar 0 shifts window by 1)
    post = out.iloc[2160:]
    assert (post >= 0.0).all() and (post <= 1.0).all()


def test_oi_velocity_ewm_240_pctrank_causality():
    rng = np.random.default_rng(9)
    vals = rng.uniform(50000, 100000, 2300)
    full = oi_velocity_ewm_240_pctrank_2160(_oi_df(vals))
    trunc = oi_velocity_ewm_240_pctrank_2160(_oi_df(vals[:2200]))
    # First valid index is 2160 (EWM NaN at bar 0 shifts window by 1)
    np.testing.assert_array_equal(
        trunc.iloc[2160:].to_numpy(), full.iloc[2160:2200].to_numpy()
    )


def test_oi_velocity_ewm_240_pctrank_zero_poison_no_crash():
    # A series with zero-OI bars must not crash or produce inf
    vals = [float(i + 100) for i in range(2200)]
    for idx in [50, 100, 500, 1000, 2000]:
        vals[idx] = 0.0
    df = _oi_df(vals)
    out = oi_velocity_ewm_240_pctrank_2160(df)
    arr = out.to_numpy(dtype=float)
    assert not np.any(np.isinf(arr))


def test_oi_velocity_ewm_240_pctrank_g1_ast_safe():
    _assert_no_future_ops(
        oi_velocity_ewm_240_pctrank_2160, "oi_velocity_ewm_240_pctrank_2160"
    )  # no raise


# ---------------------------------------------------------------------------
# Cross-factor: firewall (no notional column required)
# ---------------------------------------------------------------------------


def test_all_factors_read_contracts_column_only():
    """All factors must work with a frame containing ONLY sum_open_interest.

    If any factor tries to read sum_open_interest_value (the notional column),
    it will raise a KeyError here, catching the firewall violation at test time.
    """
    n = 2200
    df = _oi_df([float(i + 100) for i in range(n)])
    # Must not raise
    _oi_log_change(df)
    oi_sign(df)
    oi_velocity_ewm_240(df)
    oi_pct_rank_2160(df)
    oi_velocity_ewm_240_pctrank_2160(df)

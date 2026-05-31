"""Tests for Path A funding-rate factors (Phase B, Tasks B1-B5).

The funding factors are computed on the 8h settlement series (causal, rolling
over settlement units). They are carried onto the 1h bar grid downstream by
``factors.funding_align.carry_funding_to_bars`` (Task B4). All factors are
top-level named callables, rolling/causal only (must pass the G1-G4 leakage
guards). All UTC. Mirrors the OHLCV factor test conventions.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from factors.funding import funding_ewm_30, funding_ewm_60, funding_sign


def _funding_df(values) -> pd.DataFrame:
    """Wrap a funding-rate sequence in the canonical funding factor input frame."""
    return pd.DataFrame({"funding_rate": pd.Series(values, dtype="float64")})


# ---------------------------------------------------------------------------
# Task B1: funding_sign
# ---------------------------------------------------------------------------


def test_funding_sign():
    s = pd.Series([0.0002, -0.0001, 0.0, 0.00005])
    out = funding_sign(pd.DataFrame({"funding_rate": s}))
    assert out.tolist() == [1.0, -1.0, 0.0, 1.0]


# ---------------------------------------------------------------------------
# Task B2: funding_ewm_30 / funding_ewm_60
# ---------------------------------------------------------------------------


def test_funding_ewm_30_matches_unadjusted_ewm():
    rng = np.random.default_rng(11)
    s = pd.Series(rng.normal(0, 1e-4, 200), dtype="float64")
    out = funding_ewm_30(_funding_df(s))
    expected = s.ewm(span=30, adjust=False).mean()
    pd.testing.assert_series_equal(out, expected, check_names=False)


def test_funding_ewm_60_matches_unadjusted_ewm():
    rng = np.random.default_rng(12)
    s = pd.Series(rng.normal(0, 1e-4, 200), dtype="float64")
    out = funding_ewm_60(_funding_df(s))
    expected = s.ewm(span=60, adjust=False).mean()
    pd.testing.assert_series_equal(out, expected, check_names=False)


def test_funding_ewm_uses_adjust_false():
    # adjust=False and adjust=True diverge on a non-constant series; assert the
    # factor uses the unadjusted (classic recursive) form, not the adjusted one.
    s = pd.Series([1e-4, -2e-4, 3e-4, -1e-4, 5e-5], dtype="float64")
    out = funding_ewm_30(_funding_df(s))
    adjusted = s.ewm(span=30, adjust=True).mean()
    # The two forms agree at index 0 but must differ thereafter.
    assert not np.allclose(out.to_numpy(), adjusted.to_numpy())


def test_funding_ewm_is_causal_delete_future_invariant():
    # Value at settlement N must be independent of settlements > N: truncating
    # the future leaves earlier values bit-identical.
    rng = np.random.default_rng(13)
    s = pd.Series(rng.normal(0, 1e-4, 120), dtype="float64")
    full = funding_ewm_30(_funding_df(s))
    trunc = funding_ewm_30(_funding_df(s.iloc[:80]))
    np.testing.assert_array_equal(trunc.to_numpy(), full.iloc[:80].to_numpy())

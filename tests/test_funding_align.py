"""Tests for the 8h->1h causal funding carry-forward (Phase B, Task B4).

``carry_funding_to_bars`` joins 8h funding features onto the 1h bar grid by a
backward as-of join: each bar at close ``c`` receives the most recent
settlement with ``calc_time <= c`` (discrete-settlement carry, NOT
interpolation, never a future settlement). All UTC.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from factors.funding_align import carry_funding_to_bars


def test_carry_is_backward_asof_and_causal():
    feat = pd.DataFrame({
        "open_time_utc": pd.to_datetime(
            ["2020-01-01 00:00", "2020-01-01 08:00"], utc=True
        ),
        "funding_ewm_30": [0.1, 0.2],
    })
    bars = pd.DataFrame({"open_time_utc": pd.to_datetime(
        ["2020-01-01 00:00", "2020-01-01 03:00", "2020-01-01 08:00", "2020-01-01 09:00"],
        utc=True,
    )})
    out = carry_funding_to_bars(bars, feat, ["funding_ewm_30"])
    assert out["funding_ewm_30"].tolist() == [0.1, 0.1, 0.2, 0.2]  # carried within window
    # causality: a future settlement cannot change an earlier bar
    out2 = carry_funding_to_bars(bars.iloc[:2], feat.iloc[:1], ["funding_ewm_30"])
    assert out2["funding_ewm_30"].tolist() == [0.1, 0.1]


def test_bars_before_first_settlement_are_nan():
    feat = pd.DataFrame({
        "open_time_utc": pd.to_datetime(["2020-01-01 08:00"], utc=True),
        "funding_ewm_30": [0.5],
    })
    bars = pd.DataFrame({"open_time_utc": pd.to_datetime(
        ["2020-01-01 00:00", "2020-01-01 07:00", "2020-01-01 08:00"], utc=True,
    )})
    out = carry_funding_to_bars(bars, feat, ["funding_ewm_30"])
    assert np.isnan(out["funding_ewm_30"].iloc[0])
    assert np.isnan(out["funding_ewm_30"].iloc[1])
    assert out["funding_ewm_30"].iloc[2] == 0.5


def test_carry_preserves_bar_rows_and_order():
    feat = pd.DataFrame({
        "open_time_utc": pd.to_datetime(["2020-01-01 00:00"], utc=True),
        "funding_sign": [1.0],
    })
    bars = pd.DataFrame({
        "open_time_utc": pd.to_datetime(
            ["2020-01-01 00:00", "2020-01-01 01:00", "2020-01-01 02:00"], utc=True
        ),
        "close": [100.0, 101.0, 102.0],
    })
    out = carry_funding_to_bars(bars, feat, ["funding_sign"])
    assert len(out) == len(bars)
    assert out["open_time_utc"].tolist() == bars["open_time_utc"].tolist()
    assert out["close"].tolist() == [100.0, 101.0, 102.0]  # original bar columns kept
    assert "funding_sign" in out.columns


# ---------------------------------------------------------------------------
# FIX 2 (2-leg B2 HIGH): the as-of join must key on the bar's CLOSE, not its
# OPEN. Real funding calc_time jitters a few ms off the nominal 8h boundary; a
# settlement at 08:00:00.001 is KNOWN well before the 08:00 bar's close
# (08:59:59.999), so it must be carried to the 08:00 bar — NOT delayed to 09:00.
# Conversely a settlement at the next bar's open (09:00:00.000) settles AFTER
# the 08:00 bar's close and must NOT reach the 08:00 bar (leak-free).
# ---------------------------------------------------------------------------


def test_settlement_jittered_just_after_open_carries_to_same_bar():
    """A settlement at 08:00:00.001 IS carried to the 08:00 bar (whose close is
    08:59:59.999), not delayed to the 09:00 bar."""
    feat = pd.DataFrame({
        "open_time_utc": pd.to_datetime(
            ["2020-01-01 00:00:00.000", "2020-01-01 08:00:00.001"], utc=True
        ),
        "funding_ewm_30": [0.1, 0.2],
    })
    bars = pd.DataFrame({"open_time_utc": pd.to_datetime(
        ["2020-01-01 07:00:00", "2020-01-01 08:00:00", "2020-01-01 09:00:00"],
        utc=True,
    )})
    out = carry_funding_to_bars(bars, feat, ["funding_ewm_30"])
    # 07:00 bar: only the 00:00 settlement is <= its close (07:59:59.999) -> 0.1.
    # 08:00 bar: the 08:00:00.001 settlement IS <= its close (08:59:59.999) -> 0.2.
    # 09:00 bar: still 0.2.
    assert out["funding_ewm_30"].tolist() == [0.1, 0.2, 0.2]
    # Row count + open_time_utc preserved (the close key is internal only).
    assert out["open_time_utc"].tolist() == bars["open_time_utc"].tolist()


def test_settlement_at_next_bar_open_does_not_leak_into_prior_bar():
    """A settlement at exactly 09:00:00.000 settles AFTER the 08:00 bar's close
    (08:59:59.999), so it must NOT be available to the 08:00 bar — leak-free."""
    feat = pd.DataFrame({
        "open_time_utc": pd.to_datetime(
            ["2020-01-01 00:00:00.000", "2020-01-01 09:00:00.000"], utc=True
        ),
        "funding_ewm_30": [0.1, 0.9],
    })
    bars = pd.DataFrame({"open_time_utc": pd.to_datetime(
        ["2020-01-01 08:00:00", "2020-01-01 09:00:00"], utc=True,
    )})
    out = carry_funding_to_bars(bars, feat, ["funding_ewm_30"])
    # 08:00 bar (close 08:59:59.999): only the 00:00 settlement qualifies -> 0.1.
    # 09:00 bar (close 09:59:59.999): the 09:00:00.000 settlement qualifies -> 0.9.
    assert out["funding_ewm_30"].tolist() == [0.1, 0.9]


def test_carry_multiple_columns():
    feat = pd.DataFrame({
        "open_time_utc": pd.to_datetime(
            ["2020-01-01 00:00", "2020-01-01 08:00"], utc=True
        ),
        "funding_sign": [1.0, -1.0],
        "funding_ewm_30": [0.1, 0.2],
    })
    bars = pd.DataFrame({"open_time_utc": pd.to_datetime(
        ["2020-01-01 04:00", "2020-01-01 12:00"], utc=True
    )})
    out = carry_funding_to_bars(bars, feat, ["funding_sign", "funding_ewm_30"])
    assert out["funding_sign"].tolist() == [1.0, -1.0]
    assert out["funding_ewm_30"].tolist() == [0.1, 0.2]


# ---------------------------------------------------------------------------
# Task B4 Step 5: dedicated causality sentinel (mirror Path B G2).
# ---------------------------------------------------------------------------


def _random_settlements(n: int, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    # FIX 2: jitter the nominal 8h boundary by +1ms so the carry's bar-CLOSE
    # keying is exercised (a settlement landing 1ms into a bar must be available
    # to THAT bar, not delayed to the next). Real funding calc_time jitters off
    # the nominal boundary; the carry must remain causal under that jitter.
    times = pd.date_range("2020-01-01", periods=n, freq="8h", tz="UTC") + pd.Timedelta("1ms")
    return pd.DataFrame({
        "open_time_utc": times,
        "funding_feat": rng.normal(0, 1e-4, n),
    })


def _bar_grid(n_settlements: int) -> pd.DataFrame:
    # 1h bars spanning the same range as n_settlements 8h settlements.
    times = pd.date_range("2020-01-01", periods=n_settlements * 8, freq="1h", tz="UTC")
    return pd.DataFrame({"open_time_utc": times})


def test_causality_sentinel_delete_reverse_shuffle_future_settlements():
    """For every bar, the carried value is bit-identical when settlements
    strictly after that bar's CLOSE are deleted, reversed, or shuffled.

    This is the carry-layer analogue of Path B's G2 future-bar invariance
    sentinel: a future settlement must never change an earlier bar's value.
    FIX 2: settlements jitter +1ms off the boundary and the carry keys on the
    bar's CLOSE, so "the future" is everything with calc_time strictly greater
    than the bar's close (open + 1h - 1ms) — NOT the bar's open. A settlement
    landing within the bar (e.g. open+1ms) is legitimately available to it.
    """
    n_settle = 50
    feat = _random_settlements(n_settle, seed=7)
    bars = _bar_grid(n_settle)
    cols = ["funding_feat"]

    baseline = carry_funding_to_bars(bars, feat, cols)["funding_feat"].to_numpy()
    rng = np.random.default_rng(99)

    # Test a representative spread of cut points across the grid.
    for cut_idx in range(0, len(bars), 7):
        # The bar's close is its open + 1h - 1ms (1h bar grid). Settlements at
        # or before the bar's close are the only ones that may legitimately
        # affect it; everything strictly after the close is "the future".
        bar_open = bars["open_time_utc"].iloc[cut_idx]
        bar_close = bar_open + pd.Timedelta(hours=1) - pd.Timedelta("1ms")

        past = feat[feat["open_time_utc"] <= bar_close]
        future = feat[feat["open_time_utc"] > bar_close]

        # (1) delete future settlements
        deleted = past.reset_index(drop=True)
        out_deleted = carry_funding_to_bars(bars, deleted, cols)["funding_feat"].to_numpy()
        np.testing.assert_array_equal(
            out_deleted[cut_idx], baseline[cut_idx],
            err_msg=f"deleting future changed bar {cut_idx}",
        )

        # (2) reverse the future settlements (then re-concat, unsorted)
        reversed_future = future.iloc[::-1]
        perturbed_rev = pd.concat([past, reversed_future], ignore_index=True)
        out_rev = carry_funding_to_bars(bars, perturbed_rev, cols)["funding_feat"].to_numpy()
        np.testing.assert_array_equal(
            out_rev[cut_idx], baseline[cut_idx],
            err_msg=f"reversing future changed bar {cut_idx}",
        )

        # (3) shuffle the future settlements
        shuffled_future = future.sample(frac=1.0, random_state=int(rng.integers(1, 1_000_000)))
        perturbed_shuf = pd.concat([past, shuffled_future], ignore_index=True)
        out_shuf = carry_funding_to_bars(bars, perturbed_shuf, cols)["funding_feat"].to_numpy()
        np.testing.assert_array_equal(
            out_shuf[cut_idx], baseline[cut_idx],
            err_msg=f"shuffling future changed bar {cut_idx}",
        )

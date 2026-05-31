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
    times = pd.date_range("2020-01-01", periods=n, freq="8h", tz="UTC")
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
    strictly AFTER that bar are deleted, reversed, or shuffled.

    This is the carry-layer analogue of Path B's G2 future-bar invariance
    sentinel: a future settlement must never change an earlier bar's value.
    """
    n_settle = 50
    feat = _random_settlements(n_settle, seed=7)
    bars = _bar_grid(n_settle)
    cols = ["funding_feat"]

    baseline = carry_funding_to_bars(bars, feat, cols)["funding_feat"].to_numpy()
    rng = np.random.default_rng(99)

    # Test a representative spread of cut points across the grid.
    for cut_idx in range(0, len(bars), 7):
        cut_time = bars["open_time_utc"].iloc[cut_idx]

        # Settlements at or before the bar's close are the only ones that may
        # legitimately affect it; everything strictly after is "the future".
        past = feat[feat["open_time_utc"] <= cut_time]
        future = feat[feat["open_time_utc"] > cut_time]

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

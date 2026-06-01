"""Tests for native-1h basis_rel derivation + cross-stream join-integrity (Path C Phase B, Task B0).

``derive_basis_rel`` computes ``basis_rel[t] = (mark_close[t] - spot_close[t]) /
spot_close[t]`` on the shared inner-join of the markprice and spot 1h grids.

Design:
- Inner-join on ``open_time_utc`` (keeps only bars present in BOTH streams).
- Log dropped-bar counts (markprice-only + spot-only) at INFO.
- Raise ``ValueError("cross-stream ...")`` if:
    - the non-shared fraction > CROSS_STREAM_DROP_TOL (5%), OR
    - zero overlap (no shared timestamps in the overlap window).
- Causal by construction: same-grid join, no carry, mark@t and spot@t are
  both bar-N-close values; orders fill at N+1 open per the execution convention.
"""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd
import pytest

from factors.basis_derive import CROSS_STREAM_DROP_TOL, derive_basis_rel


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _mark(times: list[str], marks: list[float]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "open_time_utc": pd.to_datetime(times, utc=True),
            "mark_close": marks,
        }
    )


def _spot(times: list[str], closes: list[float]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "open_time_utc": pd.to_datetime(times, utc=True),
            "close": closes,
        }
    )


# ---------------------------------------------------------------------------
# Step 1: basic correctness
# ---------------------------------------------------------------------------


def test_basis_rel_same_grid_join():
    """Happy path: both streams on same 1h grid -> basis_rel computed for each bar."""
    out = derive_basis_rel(
        _mark(["2020-01-01 00:00", "2020-01-01 01:00"], [7005.0, 7012.0]),
        _spot(["2020-01-01 00:00", "2020-01-01 01:00"], [7000.0, 7000.0]),
    )
    assert out["basis_rel"].tolist() == pytest.approx(
        [(7005 - 7000) / 7000, (7012 - 7000) / 7000]
    )
    assert list(out.columns) == ["open_time_utc", "basis_rel"]


def test_basis_rel_output_columns_only():
    """Output frame must have exactly [open_time_utc, basis_rel] — no extra columns."""
    out = derive_basis_rel(
        _mark(["2020-01-01 00:00"], [10000.0]),
        _spot(["2020-01-01 00:00"], [10000.0]),
    )
    assert list(out.columns) == ["open_time_utc", "basis_rel"]


def test_basis_rel_zero_basis():
    """When mark == spot, basis_rel is exactly 0."""
    out = derive_basis_rel(
        _mark(["2020-01-01 00:00", "2020-01-01 01:00"], [8000.0, 9000.0]),
        _spot(["2020-01-01 00:00", "2020-01-01 01:00"], [8000.0, 9000.0]),
    )
    assert out["basis_rel"].tolist() == pytest.approx([0.0, 0.0])


def test_basis_rel_output_sorted_by_open_time_utc():
    """Output rows are sorted ascending by open_time_utc."""
    # Provide inputs in reversed order to exercise sorting.
    out = derive_basis_rel(
        _mark(["2020-01-01 01:00", "2020-01-01 00:00"], [7012.0, 7005.0]),
        _spot(["2020-01-01 01:00", "2020-01-01 00:00"], [7000.0, 7000.0]),
    )
    assert out["open_time_utc"].tolist() == pd.to_datetime(
        ["2020-01-01 00:00", "2020-01-01 01:00"], utc=True
    ).tolist()


# ---------------------------------------------------------------------------
# Step 2: small misalignment -> inner-join + log (no raise)
# ---------------------------------------------------------------------------


def test_basis_rel_small_misalignment_inner_joins_and_logs(caplog):
    """99 shared + 1 spot-only -> 1% non-shared < 5% -> inner-join, no raise,
    logs the dropped count."""
    t = pd.date_range("2020-01-01", periods=100, freq="1h", tz="UTC")
    mark = _mark(list(t[:99].astype(str)), list(np.full(99, 7005.0)))  # missing last bar
    spot = _spot(list(t.astype(str)), list(np.full(100, 7000.0)))       # has all 100

    with caplog.at_level(logging.INFO, logger="factors.basis_derive"):
        out = derive_basis_rel(mark, spot)

    assert len(out) == 99  # only the 99 shared bars survive the inner join
    assert any(
        "drop" in r.message.lower() or "non-shared" in r.message.lower()
        for r in caplog.records
    )


def test_basis_rel_markprice_missing_bars_inner_joined():
    """When markprice has fewer bars (within tolerance), result length == shared count."""
    t = pd.date_range("2020-01-01", periods=200, freq="1h", tz="UTC")
    # 2 markprice-only gaps (out of 201 union bars) -> ~1% non-shared
    mark = _mark(
        list(t[[i for i in range(200) if i not in (50, 150)]].astype(str)),
        list(np.full(198, 7001.0)),
    )
    spot = _spot(list(t.astype(str)), list(np.full(200, 7000.0)))
    out = derive_basis_rel(mark, spot)
    assert len(out) == 198


def test_basis_rel_spot_only_bars_excluded():
    """Spot-only bars are dropped from the output (inner join).

    Use 200 bars with only 2 spot-only bars (1% non-shared < 5% threshold)
    so the sanity check passes and the inner-join behaviour is exercised.
    """
    t = pd.date_range("2020-01-01", periods=200, freq="1h", tz="UTC")
    # markprice is missing the last 2 bars; spot has all 200.
    # non-shared = 2 spot-only out of union 200 = 1% < 5%.
    mark = _mark(list(t[:198].astype(str)), list(np.full(198, 7005.0)))
    spot = _spot(list(t.astype(str)), list(np.full(200, 7000.0)))
    out = derive_basis_rel(mark, spot)
    assert len(out) == 198  # the 2 spot-only bars are excluded from the inner join


def test_basis_rel_constant_CROSS_STREAM_DROP_TOL():
    """Sanity-check the exported constant value."""
    assert CROSS_STREAM_DROP_TOL == pytest.approx(0.05)


# ---------------------------------------------------------------------------
# Step 3: gross misalignment -> raise
# ---------------------------------------------------------------------------


def test_basis_rel_raises_on_gross_misalignment():
    """Completely disjoint grids: non-shared fraction = 100% (> 5%) -> raise."""
    t = pd.date_range("2020-01-01", periods=100, freq="1h", tz="UTC")
    t2 = pd.date_range("2021-06-01", periods=100, freq="1h", tz="UTC")  # no overlap with t
    mark = _mark(list(t.astype(str)), list(np.full(100, 7005.0)))
    spot = _spot(list(t2.astype(str)), list(np.full(100, 7000.0)))
    with pytest.raises(ValueError, match="cross-stream"):
        derive_basis_rel(mark, spot)


def test_basis_rel_raises_on_zero_overlap():
    """Explicit zero-overlap test: streams that share no timestamps at all -> raise."""
    mark = _mark(["2020-01-01 00:00", "2020-01-01 01:00"], [7005.0, 7006.0])
    spot = _spot(["2021-01-01 00:00", "2021-01-01 01:00"], [50000.0, 50001.0])
    with pytest.raises(ValueError, match="cross-stream"):
        derive_basis_rel(mark, spot)


def test_basis_rel_raises_when_non_shared_fraction_exceeds_threshold():
    """5 shared + 96 mark-only -> ~96% non-shared (> 5%) -> raise."""
    t_long = pd.date_range("2020-01-01", periods=100, freq="1h", tz="UTC")
    t_short = t_long[:5]  # only the first 5 match
    mark = _mark(list(t_long.astype(str)), list(np.full(100, 7005.0)))
    spot = _spot(list(t_short.astype(str)), list(np.full(5, 7000.0)))
    with pytest.raises(ValueError, match="cross-stream"):
        derive_basis_rel(mark, spot)


def test_basis_rel_zero_spot_close_is_nan():
    """spot_close == 0 on one bar -> that bar's basis_rel is NaN (not inf).

    Guards the div-by-zero case: (mark - 0) / 0 must not silently produce inf.
    """
    out = derive_basis_rel(
        _mark(["2020-01-01 00:00", "2020-01-01 01:00"], [7005.0, 7012.0]),
        _spot(["2020-01-01 00:00", "2020-01-01 01:00"], [7000.0, 0.0]),
    )
    # Bar 0: normal computation
    assert out["basis_rel"].iloc[0] == pytest.approx((7005 - 7000) / 7000)
    # Bar 1: spot_close == 0 -> NaN (not inf)
    assert pd.isna(out["basis_rel"].iloc[1]), (
        f"Expected NaN for spot_close==0 bar, got {out['basis_rel'].iloc[1]!r}"
    )


def test_basis_rel_boundary_exactly_five_percent():
    """Non-shared fraction == exactly 0.05 PASSES (threshold is strict >).

    Constructs union of 100 timestamps with exactly 5 non-shared (all spot-only)
    -> non_shared_fraction = 5/100 = 0.05 -> no raise, returns 95 shared bars.
    A just-above-5% case (6/101 union with 6 non-shared = ~5.94%) raises.
    """
    t = pd.date_range("2020-01-01", periods=100, freq="1h", tz="UTC")
    # mark: first 95 bars (95 shared with spot's first 95)
    # spot: all 100 bars
    # union = 100, non-shared = 5 spot-only -> 5/100 = 0.05 exactly
    mark = _mark(list(t[:95].astype(str)), list(np.full(95, 7005.0)))
    spot = _spot(list(t.astype(str)), list(np.full(100, 7000.0)))

    # Must NOT raise at exactly 5%
    out = derive_basis_rel(mark, spot)
    assert len(out) == 95, f"Expected 95 shared bars, got {len(out)}"

    # Just above 5%: 6 non-shared out of 101 union bars = ~5.94% -> must raise
    t2 = pd.date_range("2020-01-01", periods=101, freq="1h", tz="UTC")
    mark2 = _mark(list(t2[:95].astype(str)), list(np.full(95, 7005.0)))
    spot2 = _spot(list(t2.astype(str)), list(np.full(101, 7000.0)))
    with pytest.raises(ValueError, match="cross-stream"):
        derive_basis_rel(mark2, spot2)


# ---------------------------------------------------------------------------
# Step 5: causality sentinel (mirror Path A/B G2)
# ---------------------------------------------------------------------------


def test_causality_sentinel_delete_reverse_shuffle_future_bars():
    """basis_rel at every bar is bit-identical when bars strictly after it are
    deleted, reversed, or shuffled in BOTH input frames.

    A same-grid join is trivially causal (no carry/shift), but we assert it
    explicitly to guard against any future refactoring that might introduce
    a rolling window or look-ahead read on the joined frame.
    """
    n = 100
    rng = np.random.default_rng(42)
    t = pd.date_range("2020-01-01", periods=n, freq="1h", tz="UTC")
    mark_vals = 7000.0 + rng.normal(0, 5.0, n)
    spot_vals = 7000.0 + rng.normal(0, 5.0, n)

    mark_df = pd.DataFrame({"open_time_utc": t, "mark_close": mark_vals})
    spot_df = pd.DataFrame({"open_time_utc": t, "close": spot_vals})

    baseline = derive_basis_rel(mark_df, spot_df)["basis_rel"].to_numpy()

    rng2 = np.random.default_rng(99)
    # Check a representative spread of cut points.
    for cut_idx in range(0, n, 7):
        cut_time = t[cut_idx]

        # Split both streams at the cut bar (inclusive past, exclusive future).
        mark_past = mark_df[mark_df["open_time_utc"] <= cut_time]
        mark_future = mark_df[mark_df["open_time_utc"] > cut_time]
        spot_past = spot_df[spot_df["open_time_utc"] <= cut_time]
        spot_future = spot_df[spot_df["open_time_utc"] > cut_time]

        # (1) delete future bars in both streams
        out_del = derive_basis_rel(
            mark_past.reset_index(drop=True),
            spot_past.reset_index(drop=True),
        )["basis_rel"].to_numpy()
        np.testing.assert_array_equal(
            out_del[cut_idx],
            baseline[cut_idx],
            err_msg=f"deleting future bars changed bar {cut_idx}",
        )

        # (2) reverse future bars in both streams
        mark_rev = pd.concat(
            [mark_past, mark_future.iloc[::-1]], ignore_index=True
        )
        spot_rev = pd.concat(
            [spot_past, spot_future.iloc[::-1]], ignore_index=True
        )
        out_rev = derive_basis_rel(mark_rev, spot_rev)["basis_rel"].to_numpy()
        np.testing.assert_array_equal(
            out_rev[cut_idx],
            baseline[cut_idx],
            err_msg=f"reversing future bars changed bar {cut_idx}",
        )

        # (3) shuffle future bars in both streams
        seed = int(rng2.integers(1, 1_000_000))
        mark_shuf = pd.concat(
            [mark_past, mark_future.sample(frac=1.0, random_state=seed)],
            ignore_index=True,
        )
        spot_shuf = pd.concat(
            [spot_past, spot_future.sample(frac=1.0, random_state=seed)],
            ignore_index=True,
        )
        out_shuf = derive_basis_rel(mark_shuf, spot_shuf)["basis_rel"].to_numpy()
        np.testing.assert_array_equal(
            out_shuf[cut_idx],
            baseline[cut_idx],
            err_msg=f"shuffling future bars changed bar {cut_idx}",
        )

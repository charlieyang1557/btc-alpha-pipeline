# tests/test_pathb_train_sanity.py
"""Train-only mechanism sanity: parse train_windows list; reject 2022/2024/2025."""
from __future__ import annotations

import pandas as pd
import pytest

import backtest.pathb_train_sanity as ts


def test_train_windows_parsed_as_list_of_timestamp_pairs():
    windows = ts.load_train_windows()
    assert len(windows) == 2
    lo0, hi0 = windows[0]
    assert lo0 == pd.Timestamp("2020-01-01")
    assert hi0 == pd.Timestamp("2021-12-31")
    lo1, hi1 = windows[1]
    assert lo1 == pd.Timestamp("2023-01-01")
    assert hi1 == pd.Timestamp("2023-12-31")


def test_timestamp_inside_allowed_window():
    windows = ts.load_train_windows()
    assert ts.in_train_window(pd.Timestamp("2020-06-15"), windows) is True
    assert ts.in_train_window(pd.Timestamp("2023-07-01"), windows) is True


@pytest.mark.parametrize("forbidden", ["2022-06-01", "2024-03-01", "2025-09-01"])
def test_2022_validation_test_excluded(forbidden):
    windows = ts.load_train_windows()
    assert ts.in_train_window(pd.Timestamp(forbidden), windows) is False


def test_require_train_only_raises_on_out_of_window_timestamps():
    windows = ts.load_train_windows()
    df = pd.DataFrame({"open_time_utc": pd.to_datetime(
        ["2020-02-01", "2022-02-01"], utc=False)})
    with pytest.raises(ValueError, match="outside train_windows"):
        ts.require_train_only(df["open_time_utc"], windows)


def test_tz_aware_timestamps_handled():
    # Real raw data is tz-aware UTC; membership must work without raising.
    windows = ts.load_train_windows()
    assert ts.in_train_window(pd.Timestamp("2020-06-15", tz="UTC"), windows) is True
    assert ts.in_train_window(pd.Timestamp("2022-06-15", tz="UTC"), windows) is False


def test_sanity_table_has_no_validation_or_test_rows():
    windows = ts.load_train_windows()
    df = pd.DataFrame({
        "open_time_utc": pd.to_datetime(
            ["2020-02-01", "2021-05-01", "2023-08-01"], utc=False),
        "fwd_ret_sign": [1, -1, 1],
    })
    table = ts.build_sanity_table(df, windows)
    assert table["n_train_rows"] == 3
    assert table["touched_validation_or_test"] is False


def test_intraday_bars_on_window_end_day_are_in_train():
    # Regression: an hourly bar on the LAST day of a train window (2021-12-31
    # 23:00) must be IN train (the window is inclusive of the whole end-day),
    # while the first hour of the excluded next year (2022-01-01 00:00) is OUT.
    windows = ts.load_train_windows()
    assert ts.in_train_window(pd.Timestamp("2021-12-31 23:00"), windows) is True
    assert ts.in_train_window(pd.Timestamp("2023-12-31 23:00"), windows) is True
    assert ts.in_train_window(pd.Timestamp("2022-01-01 00:00"), windows) is False

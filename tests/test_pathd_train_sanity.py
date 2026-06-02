# tests/test_pathd_train_sanity.py
"""Path D train-window sanity helpers.

Adapted from tests/test_pathc_train_sanity.py (if it exists) or the analogous
patha module. Verifies load_train_windows, in_train_window, require_train_only.
"""
from __future__ import annotations

import pytest
import pandas as pd

from backtest.pathd_train_sanity import (
    in_train_window,
    load_train_windows,
    require_train_only,
)


def test_load_train_windows_returns_nonempty_list():
    windows = load_train_windows()
    assert isinstance(windows, list)
    assert len(windows) >= 1
    for w in windows:
        assert len(w) == 2
        lo, hi = w
        assert lo < hi


def test_2022_not_in_any_train_window():
    """2022 is the regime holdout — must be absent from all train windows."""
    windows = load_train_windows()
    ts_2022 = pd.Timestamp("2022-06-01")
    assert not in_train_window(ts_2022, windows), (
        "2022 is the regime holdout and must NOT be in any train window"
    )


def test_2020_is_in_train_window():
    windows = load_train_windows()
    ts_2020 = pd.Timestamp("2020-06-01")
    assert in_train_window(ts_2020, windows)


def test_2024_validation_not_in_train_window():
    windows = load_train_windows()
    ts_2024 = pd.Timestamp("2024-06-01")
    assert not in_train_window(ts_2024, windows)


def test_2025_test_not_in_train_window():
    windows = load_train_windows()
    ts_2025 = pd.Timestamp("2025-01-01")
    assert not in_train_window(ts_2025, windows)


def test_require_train_only_raises_on_2022():
    windows = load_train_windows()
    times = pd.Series([pd.Timestamp("2022-03-15")])
    with pytest.raises(ValueError, match="outside train_windows"):
        require_train_only(times, windows)


def test_require_train_only_passes_on_2020():
    windows = load_train_windows()
    times = pd.Series([pd.Timestamp("2020-06-01")])
    require_train_only(times, windows)  # must not raise

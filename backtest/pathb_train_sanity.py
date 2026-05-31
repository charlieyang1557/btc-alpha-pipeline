# backtest/pathb_train_sanity.py
"""Train-only mechanism sanity table.

Parses config/environments.yaml splits.train_windows (a LIST of [start,end]
pairs; 2022 is DELIBERATELY EXCLUDED) and requires every timestamp used in a
sanity computation to fall inside an allowed window. There is NO splits.v2 key
and NO single train_start/train_end — train_windows is the disjoint-range list.

Hard rule: this module NEVER reads validation (2024) or test (2025) data.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = PROJECT_ROOT / "config/environments.yaml"

TrainWindow = tuple[pd.Timestamp, pd.Timestamp]


def load_train_windows(env_path: Path = ENV_PATH) -> list[TrainWindow]:
    """Load splits.train_windows as a list of (start, end) Timestamp pairs.

    Args:
        env_path: Path to environments.yaml.

    Returns:
        A list of (pd.Timestamp(start), pd.Timestamp(end)) pairs. 2022 is not
        present in any window (it is the regime holdout, held out from train).

    Raises:
        ValueError: If splits.train_windows is missing or not a non-empty list.
    """
    cfg = yaml.safe_load(env_path.read_text()) or {}
    raw = (cfg.get("splits") or {}).get("train_windows")
    if not isinstance(raw, list) or not raw:
        raise ValueError("splits.train_windows missing or not a non-empty list")
    return [(pd.Timestamp(w[0]), pd.Timestamp(w[1])) for w in raw]


def in_train_window(ts: pd.Timestamp, windows: list[TrainWindow]) -> bool:
    """Return True iff ``ts`` falls inside any allowed train window (end-day inclusive).

    Real raw data is timezone-aware UTC (``build_features.py`` enforces this),
    while the date-only ``train_windows`` bounds are naive. We strip the tz to
    compare on naive UTC wall-time, so a tz-aware bar and a naive window bound
    compare cleanly instead of raising ``TypeError`` on aware-vs-naive.

    Args:
        ts: A timestamp (tz-aware or naive).
        windows: Output of :func:`load_train_windows`.

    Returns:
        True iff ``lo <= ts < hi + 1 day`` for some window (lo, hi).
    """
    t = pd.Timestamp(ts)
    if t.tzinfo is not None:
        t = t.tz_localize(None)
    # Upper bound is inclusive of the WHOLE end-day: the window strings are
    # date-only (midnight), so a comparison `t <= hi` would drop intraday bars
    # on the last day (e.g. 2021-12-31 23:00). Use a half-open [lo, hi+1day) so
    # every hour of the end-day is in-window while the next day is excluded.
    one_day = pd.Timedelta(days=1)
    return any(lo <= t < (hi + one_day) for lo, hi in windows)


def require_train_only(times: pd.Series, windows: list[TrainWindow]) -> None:
    """Raise if ANY timestamp is outside the allowed train windows.

    Args:
        times: A Series of timestamps.
        windows: Output of :func:`load_train_windows`.

    Raises:
        ValueError: If any timestamp falls outside train_windows (e.g. a 2022,
            2024, or 2025 bar leaked into a train-only mechanism table).
    """
    bad = [t for t in pd.to_datetime(times) if not in_train_window(pd.Timestamp(t), windows)]
    if bad:
        raise ValueError(
            f"{len(bad)} timestamp(s) outside train_windows (first={bad[0]}); "
            f"train-only sanity must NEVER touch 2022/validation/test"
        )


def build_sanity_table(df: pd.DataFrame, windows: list[TrainWindow]) -> dict:
    """Build a train-only mechanism sanity table; assert no out-of-window rows.

    Args:
        df: A frame carrying an ``open_time_utc`` column (train rows only).
        windows: Output of :func:`load_train_windows`.

    Returns:
        A dict with ``n_train_rows`` and ``touched_validation_or_test=False``.

    Raises:
        ValueError: If any row is outside train_windows (via require_train_only).
    """
    require_train_only(df["open_time_utc"], windows)
    return {
        "n_train_rows": int(len(df)),
        "touched_validation_or_test": False,
    }

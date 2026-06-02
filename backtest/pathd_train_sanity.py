# backtest/pathd_train_sanity.py
"""Train-window helpers for the Path D OI mechanism-sanity table.

Adapted near-verbatim from backtest/pathc_train_sanity.py. Parses
config/environments.yaml splits.train_windows (a LIST of [start,end] pairs; 2022 is
DELIBERATELY EXCLUDED as the regime holdout) and requires every timestamp used in a
sanity computation to fall inside an allowed window.

Hard rule: this module NEVER reads validation (2024) or test (2025) data, and 2022
(the regime holdout) is excluded from every train window.

NOTE: OI factors are heavily NaN in 2024/2025 (pctrank/EWM windows require 2160
bars to warm). Floor eligibility is computed on the non-NaN subset of the train
frame; callers must handle NaN gracefully and must NOT crash on NaN-heavy subsets.
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

    Real raw data is timezone-aware UTC; the date-only train_windows bounds are naive.
    Strip the tz to compare on naive UTC wall-time. Uses a half-open [lo, hi+1day) so
    every hour of the end-day is in-window while the next day is excluded.
    """
    t = pd.Timestamp(ts)
    if t.tzinfo is not None:
        t = t.tz_localize(None)
    one_day = pd.Timedelta(days=1)
    return any(lo <= t < (hi + one_day) for lo, hi in windows)


def require_train_only(times: pd.Series, windows: list[TrainWindow]) -> None:
    """Raise if ANY timestamp is outside the allowed train windows.

    Raises:
        ValueError: If any timestamp falls outside train_windows (e.g. a 2022, 2024,
            or 2025 bar leaked into a train-only mechanism table).
    """
    bad = [t for t in pd.to_datetime(times) if not in_train_window(pd.Timestamp(t), windows)]
    if bad:
        raise ValueError(
            f"{len(bad)} timestamp(s) outside train_windows (first={bad[0]}); "
            f"train-only sanity must NEVER touch 2022/validation/test"
        )

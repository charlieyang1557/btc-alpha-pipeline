"""Deterministic OHLCV data for WF boundary regression tests.

Generates hourly bars with controllable price trajectories. Used by
T1-T10 to exercise specific train-period vs test-period scenarios
without depending on the canonical parquet (which is large and would
make tests slow and order-dependent).
"""
from __future__ import annotations
from datetime import datetime, timedelta, timezone
from pathlib import Path
import pandas as pd
import numpy as np


def make_ohlcv(
    start: datetime,
    n_bars: int,
    price_func,
    volume: float = 1000.0,
) -> pd.DataFrame:
    """Generate a deterministic OHLCV DataFrame.

    Args:
        start: First bar's open_time_utc.
        n_bars: Number of hourly bars.
        price_func: Callable (bar_idx) -> price. Determines close price
            at each bar; OHLC derived as O=H=L=C for simplicity.
        volume: Constant volume per bar.

    Returns:
        DataFrame with columns: open_time_utc, open, high, low, close,
        volume, source, ingested_at_utc. Indexed for ParquetFeed
        compatibility (datetime index).
    """
    times = [start + timedelta(hours=i) for i in range(n_bars)]
    prices = [float(price_func(i)) for i in range(n_bars)]
    df = pd.DataFrame({
        "open_time_utc": pd.to_datetime(times, utc=True),
        "open": prices,
        "high": prices,
        "low": prices,
        "close": prices,
        "volume": [volume] * n_bars,
        "source": ["synthetic"] * n_bars,
        "ingested_at_utc": pd.to_datetime(
            [datetime.now(timezone.utc)] * n_bars, utc=True
        ),
    })
    df = df.set_index("open_time_utc")
    return df


def make_trending_then_flat(
    start: datetime,
    train_bars: int,
    test_bars: int,
    train_growth: float = 2.0,
    test_price: float | None = None,
) -> pd.DataFrame:
    """Train period: linear price uptrend. Test period: flat.

    Train: price rises from $100 to $100 * (1 + train_growth).
    Test: price stays at the train-end value (or `test_price` if given).
    """
    train_start_price = 100.0
    train_end_price = train_start_price * (1.0 + train_growth)
    flat_price = test_price if test_price is not None else train_end_price

    def price_func(i: int) -> float:
        if i < train_bars:
            return train_start_price + (train_end_price - train_start_price) * (i / max(train_bars - 1, 1))
        return flat_price

    return make_ohlcv(start, train_bars + test_bars, price_func)


def write_to_parquet(df: pd.DataFrame, path: Path) -> Path:
    """Write a synthetic DataFrame to a temporary parquet file.

    The parquet schema must match what ParquetFeed.from_parquet expects.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    df.reset_index().to_parquet(path, engine="pyarrow", index=False)
    return path

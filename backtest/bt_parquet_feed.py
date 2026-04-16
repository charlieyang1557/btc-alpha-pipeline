"""Custom Backtrader data feed that loads OHLCV data from Parquet files.

Maps the project's canonical Parquet schema (open_time_utc, open, high,
low, close, volume) to Backtrader's expected data lines. Supports date
range filtering via fromdate/todate parameters.

Backtrader internally works with timezone-naive datetimes, so this feed
strips the UTC tzinfo from the index after filtering. All comparisons
and filtering happen in UTC before the strip.

Usage:
    feed = ParquetFeed.from_parquet("data/raw/btcusdt_1h.parquet")
    cerebro.adddata(feed)

    # With date range:
    feed = ParquetFeed.from_parquet(
        "data/raw/btcusdt_1h.parquet",
        fromdate=datetime(2023, 1, 1),
        todate=datetime(2023, 12, 31),
    )
"""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path

import backtrader as bt
import pandas as pd

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PARQUET = PROJECT_ROOT / "data" / "raw" / "btcusdt_1h.parquet"


class ParquetFeed(bt.feeds.PandasData):
    """Backtrader data feed backed by a Parquet file.

    Reads the canonical OHLCV parquet, maps columns to Backtrader lines,
    and supports date range filtering.

    Extra lines beyond standard OHLCV:
        quote_volume: Quote asset volume (USDT).
        trade_count: Number of trades per bar.

    These are accessible in strategies as self.data.quote_volume[0], etc.
    """

    lines = ("quote_volume", "trade_count")

    params = (
        ("datetime", None),  # Use DataFrame index
        ("open", "open"),
        ("high", "high"),
        ("low", "low"),
        ("close", "close"),
        ("volume", "volume"),
        ("openinterest", -1),  # No open interest data
        ("quote_volume", "quote_volume"),
        ("trade_count", "trade_count"),
    )

    @classmethod
    def from_parquet(
        cls,
        path: str | Path = DEFAULT_PARQUET,
        fromdate: datetime | None = None,
        todate: datetime | None = None,
        **kwargs,
    ) -> ParquetFeed:
        """Load a Parquet file and return a configured feed instance.

        Reads the parquet, validates required columns, filters by date
        range, converts the index to tz-naive datetime (Backtrader
        requirement), and returns a ready-to-use feed.

        Args:
            path: Path to the Parquet file.
            fromdate: Start date filter (inclusive). Interpreted as UTC.
            todate: End date filter (inclusive). Interpreted as UTC.
            **kwargs: Additional Backtrader PandasData params.

        Returns:
            Configured ParquetFeed instance.

        Raises:
            FileNotFoundError: If the parquet file does not exist.
            ValueError: If required columns are missing or date range is empty.
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Parquet file not found: {path}")

        logger.info("Loading parquet feed: %s", path)
        df = pd.read_parquet(path)

        # Validate required columns
        required = {"open_time_utc", "open", "high", "low", "close", "volume"}
        missing = required - set(df.columns)
        if missing:
            raise ValueError(f"Parquet missing required columns: {sorted(missing)}")

        # Defensive checks on primary key column
        if not pd.api.types.is_datetime64_any_dtype(df["open_time_utc"]):
            raise ValueError("open_time_utc must be datetime-like")
        if df["open_time_utc"].duplicated().any():
            raise ValueError("Duplicate open_time_utc values found")

        # Ensure optional extra-line columns exist (fill with 0 if missing)
        for col, default in [("quote_volume", 0.0), ("trade_count", 0)]:
            if col not in df.columns:
                df[col] = default

        # Filter by date range (using UTC-aware comparison).
        # Handle both tz-naive and tz-aware inputs safely.
        if fromdate is not None:
            from_ts = pd.Timestamp(fromdate)
            if from_ts.tz is None:
                from_ts = from_ts.tz_localize("UTC")
            else:
                from_ts = from_ts.tz_convert("UTC")
            df = df[df["open_time_utc"] >= from_ts]
        if todate is not None:
            to_ts = pd.Timestamp(todate)
            if to_ts.tz is None:
                to_ts = to_ts.tz_localize("UTC")
            else:
                to_ts = to_ts.tz_convert("UTC")
            df = df[df["open_time_utc"] <= to_ts]

        if len(df) == 0:
            raise ValueError(
                f"No data in range [{fromdate}, {todate}] from {path}"
            )

        # Set open_time_utc as index, strip timezone for Backtrader
        df = df.set_index("open_time_utc").sort_index()
        df.index = df.index.tz_localize(None)

        # Backtrader lines are float-typed internally; cast trade_count
        # from int64 to float64 for compatibility.
        df["trade_count"] = df["trade_count"].astype("float64")

        logger.info(
            "  Loaded %d bars: %s to %s",
            len(df),
            df.index[0],
            df.index[-1],
        )

        return cls(dataname=df, **kwargs)

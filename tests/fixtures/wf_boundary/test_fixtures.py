"""Smoke tests for WF boundary fixture infrastructure."""
from datetime import datetime, timezone
from pathlib import Path
from tests.fixtures.wf_boundary.synthetic_data import (
    make_ohlcv,
    make_trending_then_flat,
    write_to_parquet,
)
from tests.fixtures.wf_boundary.strategies import (
    TrainOnlyStrategy,
    StatefulTestStrategy,
    IndicatorWarmupStrategy,
    TrainProfitable,
    TrainLosing,
)


def test_make_ohlcv_basic_shape():
    df = make_ohlcv(
        start=datetime(2024, 1, 1, tzinfo=timezone.utc),
        n_bars=10,
        price_func=lambda i: 100.0 + i,
    )
    assert len(df) == 10
    assert list(df.columns) == [
        "open", "high", "low", "close", "volume",
        "source", "ingested_at_utc",
    ]
    assert df.iloc[0]["close"] == 100.0
    assert df.iloc[9]["close"] == 109.0


def test_make_trending_then_flat_train_test_shape():
    df = make_trending_then_flat(
        start=datetime(2024, 1, 1, tzinfo=timezone.utc),
        train_bars=100,
        test_bars=50,
        train_growth=2.0,  # train: 100 -> 300
    )
    assert len(df) == 150
    # Train end (bar 99) should be ~$300
    assert abs(df.iloc[99]["close"] - 300.0) < 0.01
    # Test bars (100..149) should all equal train-end price
    for i in range(100, 150):
        assert df.iloc[i]["close"] == df.iloc[99]["close"]


def test_write_to_parquet_roundtrip(tmp_path):
    import pandas as pd
    df = make_ohlcv(
        start=datetime(2024, 1, 1, tzinfo=timezone.utc),
        n_bars=5,
        price_func=lambda i: 100.0,
    )
    path = tmp_path / "synthetic.parquet"
    write_to_parquet(df, path)
    assert path.exists()
    loaded = pd.read_parquet(path)
    assert len(loaded) == 5


def test_fixture_strategies_have_required_attributes():
    for cls in [TrainOnlyStrategy, StatefulTestStrategy,
                IndicatorWarmupStrategy, TrainProfitable, TrainLosing]:
        assert hasattr(cls, "STRATEGY_NAME")
        assert hasattr(cls, "WARMUP_BARS")
        assert cls.STRATEGY_NAME != "unnamed"

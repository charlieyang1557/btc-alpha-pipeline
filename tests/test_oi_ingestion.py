import pytest
import pandas as pd
import yaml
from pathlib import Path


def test_oi_schema_block_exists():
    schemas = yaml.safe_load(Path("config/schemas.yaml").read_text())
    m = schemas["oi"]
    assert m["primary_key"] == "open_time_utc"
    cols = set(m["columns"].keys())   # columns is a name-keyed MAPPING (mirror the ohlcv/markprice block)
    assert {"open_time_utc", "sum_open_interest", "sum_open_interest_value",
            "source", "ingested_at_utc"} <= cols
    assert set(m["columns"]["source"]["allowed_values"]) >= {"binance_vision", "ccxt_binance"}


# ---------------------------------------------------------------------------
# A2: parse_metrics_csv tests
# ---------------------------------------------------------------------------

from ingestion.oi_bulk_download import parse_metrics_csv


def test_parse_oi_metrics_with_header(tmp_path):
    # Binance Vision metrics: HEADER row + create_time as a UTC datetime string, 5-min cadence.
    csv = tmp_path / "BTCUSDT-metrics-2020-09-01.csv"
    csv.write_text(
        "create_time,symbol,sum_open_interest,sum_open_interest_value,"
        "count_toptrader_long_short_ratio,sum_toptrader_long_short_ratio,"
        "count_long_short_ratio,sum_taker_long_short_vol_ratio\n"
        "2020-09-01 00:00:00,BTCUSDT,12345.6,98765432.1,1.2,1.3,1.1,0.9\n"
        "2020-09-01 00:05:00,BTCUSDT,12350.0,98800000.0,1.2,1.3,1.1,0.9\n"
    )
    df = parse_metrics_csv(csv)
    assert list(df["open_time_utc"]) == [
        pd.Timestamp("2020-09-01 00:00:00", tz="UTC"),
        pd.Timestamp("2020-09-01 00:05:00", tz="UTC"),
    ]
    assert df["sum_open_interest"].tolist() == [12345.6, 12350.0]
    assert df["sum_open_interest_value"].tolist() == [98765432.1, 98800000.0]
    assert str(df["open_time_utc"].dtype) == "datetime64[ms, UTC]"
    assert (df["source"] == "binance_vision").all()


def test_parse_oi_metrics_headerless_variant(tmp_path):
    """Headerless variant (first field is a datetime string) parses the same way as the
    header variant. This is the defensive path — metrics normally has a header, but the
    autodetect must not break if the header row is absent."""
    csv = tmp_path / "BTCUSDT-metrics-2020-09-01-noheader.csv"
    # No header row; first field starts with a datetime string (not numeric).
    csv.write_text(
        "2020-09-01 00:00:00,BTCUSDT,12345.6,98765432.1,1.2,1.3,1.1,0.9\n"
        "2020-09-01 00:05:00,BTCUSDT,12350.0,98800000.0,1.2,1.3,1.1,0.9\n"
    )
    df = parse_metrics_csv(csv)
    assert list(df["open_time_utc"]) == [
        pd.Timestamp("2020-09-01 00:00:00", tz="UTC"),
        pd.Timestamp("2020-09-01 00:05:00", tz="UTC"),
    ]
    assert df["sum_open_interest"].tolist() == [12345.6, 12350.0]
    assert str(df["open_time_utc"].dtype) == "datetime64[ms, UTC]"


def test_parse_oi_metrics_missing_required_column_raises(tmp_path):
    """A CSV missing a required column (e.g. sum_open_interest) raises ValueError."""
    csv = tmp_path / "BTCUSDT-metrics-bad.csv"
    # Only create_time and symbol; no sum_open_interest or sum_open_interest_value.
    csv.write_text(
        "create_time,symbol\n"
        "2020-09-01 00:00:00,BTCUSDT\n"
    )
    with pytest.raises(ValueError, match="missing required columns"):
        parse_metrics_csv(csv)

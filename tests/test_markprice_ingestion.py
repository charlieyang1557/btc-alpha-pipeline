import yaml
from pathlib import Path
import pandas as pd
from ingestion.markprice_bulk_download import parse_kline_csv


def test_markprice_schema_block_exists():
    schemas = yaml.safe_load(Path("config/schemas.yaml").read_text())
    m = schemas["markprice"]
    assert m["primary_key"] == "open_time_utc"
    cols = set(m["columns"].keys())   # columns is a name-keyed MAPPING (mirror the ohlcv block)
    assert {"open_time_utc", "mark_close", "index_close",
            "source", "ingested_at_utc"} <= cols
    assert set(m["columns"]["source"]["allowed_values"]) >= {"binance_vision", "ccxt_binance"}


def test_parse_markprice_kline_real_format(tmp_path):
    # Binance Vision *PriceKlines: 12 headerless cols
    # open_time, open, high, low, close, volume, close_time, quote_vol, count, taker_base, taker_quote, ignore
    csv = tmp_path / "BTCUSDT-1h-2020-01.csv"
    csv.write_text(
        "1577836800000,7000,7010,6990,7005,0,1577840399999,0,0,0,0,0\n"
        "1577840400000,7005,7020,7000,7012,0,1577843999999,0,0,0,0,0\n"
    )
    df = parse_kline_csv(csv, close_col_name="mark_close")
    assert list(df["open_time_utc"]) == [
        pd.Timestamp("2020-01-01 00:00:00", tz="UTC"),
        pd.Timestamp("2020-01-01 01:00:00", tz="UTC"),
    ]
    assert df["mark_close"].tolist() == [7005.0, 7012.0]
    assert str(df["open_time_utc"].dtype) == "datetime64[ms, UTC]"
    assert (df["source"] == "binance_vision").all()
    assert str(df["ingested_at_utc"].dtype) == "datetime64[ms, UTC]"

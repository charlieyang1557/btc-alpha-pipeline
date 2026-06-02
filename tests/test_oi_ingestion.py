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

"""Tests for Path A funding-rate ingestion (Tasks A1-A5).

Covers the funding schema block, Binance Vision CSV parsing, the funding
validator, archive-before-overwrite reconcile, and CCXT incremental update.
All UTC. Mirrors the OHLCV ingestion test conventions.
"""

import yaml
from pathlib import Path


def test_funding_schema_block_exists():
    schemas = yaml.safe_load(Path("config/schemas.yaml").read_text())
    f = schemas["funding"]
    assert f["primary_key"] == "open_time_utc"
    cols = set(f["columns"].keys())   # columns is a name-keyed MAPPING (mirror the ohlcv block)
    assert {"open_time_utc", "funding_rate", "funding_interval_hours",
            "source", "ingested_at_utc"} <= cols
    # allowed sources live under the `source` column's allowed_values (mirror ohlcv)
    assert set(f["columns"]["source"]["allowed_values"]) >= {"binance_vision", "ccxt_binance"}

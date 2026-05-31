"""Tests for Path A funding-rate ingestion (Tasks A1-A5).

Covers the funding schema block, Binance Vision CSV parsing, the funding
validator, archive-before-overwrite reconcile, and CCXT incremental update.
All UTC. Mirrors the OHLCV ingestion test conventions.
"""

import yaml
from pathlib import Path

import pandas as pd


def test_funding_schema_block_exists():
    schemas = yaml.safe_load(Path("config/schemas.yaml").read_text())
    f = schemas["funding"]
    assert f["primary_key"] == "open_time_utc"
    cols = set(f["columns"].keys())   # columns is a name-keyed MAPPING (mirror the ohlcv block)
    assert {"open_time_utc", "funding_rate", "funding_interval_hours",
            "source", "ingested_at_utc"} <= cols
    # allowed sources live under the `source` column's allowed_values (mirror ohlcv)
    assert set(f["columns"]["source"]["allowed_values"]) >= {"binance_vision", "ccxt_binance"}


# ---------------------------------------------------------------------------
# Task A2: funding bulk download — CSV parse
# ---------------------------------------------------------------------------

from ingestion.funding_bulk_download import parse_funding_csv


def test_parse_funding_csv_real_format(tmp_path):
    # Real Binance Vision fundingRate columns: calc_time(ms), funding_interval_hours, last_funding_rate
    csv = tmp_path / "BTCUSDT-fundingRate-2020-01.csv"
    csv.write_text(
        "calc_time,funding_interval_hours,last_funding_rate\n"
        "1577836800000,8,0.0001\n"
        "1577865600000,8,-0.00005\n"
    )
    df = parse_funding_csv(csv)
    assert list(df["open_time_utc"]) == [
        pd.Timestamp("2020-01-01 00:00:00", tz="UTC"),
        pd.Timestamp("2020-01-01 08:00:00", tz="UTC"),
    ]
    assert df["funding_rate"].tolist() == [0.0001, -0.00005]
    assert df["funding_interval_hours"].tolist() == [8, 8]
    assert str(df["open_time_utc"].dtype) == "datetime64[ms, UTC]"
    assert (df["source"] == "binance_vision").all()


# ---------------------------------------------------------------------------
# Task A3: funding validator
# ---------------------------------------------------------------------------

from ingestion.validators import validate_funding


def _good():
    return pd.DataFrame({
        "open_time_utc": pd.to_datetime([1577836800000, 1577865600000], unit="ms", utc=True).as_unit("ms"),
        "funding_rate": [0.0001, -0.00005], "funding_interval_hours": [8, 8],
        "source": ["binance_vision"] * 2, "ingested_at_utc": pd.to_datetime([0, 0], unit="ms", utc=True).as_unit("ms"),
    })


def test_validate_funding_accepts_good():
    report = validate_funding(_good())
    assert report["ok"] is True


def test_validate_funding_rejects_duplicate_pk():
    df = _good(); df.loc[1, "open_time_utc"] = df.loc[0, "open_time_utc"]
    report = validate_funding(df)
    assert report["ok"] is False and "duplicate" in report["errors"][0].lower()


def test_validate_funding_rejects_unsorted():
    df = _good().iloc[::-1].reset_index(drop=True)
    report = validate_funding(df)
    assert report["ok"] is False

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


from ingestion.validators import validate_markprice  # noqa: E402


def _good():
    return pd.DataFrame({
        "open_time_utc": pd.to_datetime([1577836800000, 1577840400000], unit="ms", utc=True).as_unit("ms"),
        "mark_close": [7005.0, 7012.0], "index_close": [7004.0, 7011.0],
        "source": ["binance_vision"]*2, "ingested_at_utc": pd.to_datetime([0, 0], unit="ms", utc=True).as_unit("ms"),
    })


def test_validate_markprice_accepts_good():
    assert validate_markprice(_good())["ok"] is True


def test_validate_markprice_rejects_duplicate_pk():
    df = _good(); df.loc[1, "open_time_utc"] = df.loc[0, "open_time_utc"]
    r = validate_markprice(df)
    assert r["ok"] is False and "duplicate" in r["errors"][0].lower()


def test_validate_markprice_flags_mark_index_wedge():
    # (mark-index)/index far above a sane perp premium -> warning, not silent pass
    df = _good(); df.loc[0, "mark_close"] = 7004.0 * 2.0
    r = validate_markprice(df)
    assert any("wedge" in w.lower() or "cross-check" in w.lower() for w in r["warnings"])


# ---------------------------------------------------------------------------
# Task A4: markprice reconcile + archive
# ---------------------------------------------------------------------------

from ingestion import markprice_reconcile  # noqa: E402


def _mp_row(ts_ms: int, mark: float, source: str) -> dict:
    return {
        "open_time_utc": pd.to_datetime(ts_ms, unit="ms", utc=True),
        "mark_close": mark,
        "index_close": mark - 1.0,
        "source": source,
        "ingested_at_utc": pd.to_datetime(0, unit="ms", utc=True),
    }


def test_markprice_reconcile_dedup_prefers_binance_vision():
    """Duplicate open_time_utc resolves to the binance_vision row."""
    existing = pd.DataFrame([
        _mp_row(1577836800000, 7000.0, "ccxt_binance"),
        _mp_row(1577840400000, 7005.0, "ccxt_binance"),
    ])
    new = pd.DataFrame([
        _mp_row(1577836800000, 7999.0, "binance_vision"),  # conflict
        _mp_row(1577844000000, 7010.0, "binance_vision"),  # new PK
    ])
    merged, stats = markprice_reconcile.reconcile_markprice(existing, new)
    assert merged["open_time_utc"].is_monotonic_increasing
    assert merged["open_time_utc"].duplicated().sum() == 0
    first = merged.iloc[0]
    assert first["source"] == "binance_vision"
    assert first["mark_close"] == 7999.0
    assert len(merged) == 3


def test_markprice_reconcile_output_unique_sorted():
    """Output is unique on open_time_utc and sorted ascending."""
    existing = pd.DataFrame([_mp_row(1577844000000, 7010.0, "binance_vision")])
    new = pd.DataFrame([
        _mp_row(1577836800000, 7000.0, "ccxt_binance"),
        _mp_row(1577840400000, 7005.0, "ccxt_binance"),
    ])
    merged, _ = markprice_reconcile.reconcile_markprice(existing, new)
    assert merged["open_time_utc"].is_monotonic_increasing
    assert merged["open_time_utc"].duplicated().sum() == 0
    assert len(merged) == 3


def test_markprice_archive_before_overwrite(tmp_path):
    """archive_file writes a timestamped snapshot to archive_dir; original preserved."""
    archive_dir = tmp_path / "archive"
    canonical = tmp_path / "btcusdt_markprice_1h.parquet"
    df = pd.DataFrame([_mp_row(1577836800000, 7000.0, "binance_vision")])
    df.to_parquet(canonical, engine="pyarrow", index=False)

    archived = markprice_reconcile.archive_file(canonical, archive_dir=archive_dir)
    assert archived is not None
    assert archived.exists()
    assert archived.parent == archive_dir
    assert archived.name.startswith("btcusdt_markprice_1h_")
    assert archived.suffix == ".parquet"
    # copy not move — original must still be present
    assert canonical.exists()

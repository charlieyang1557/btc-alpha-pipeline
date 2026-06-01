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


def test_parse_markprice_kline_with_header_row(tmp_path):
    # Newer Binance Vision monthly kline CSVs include a header row as the first line.
    # parse_kline_csv must detect and skip it, not crash or silently drop all rows.
    csv = tmp_path / "BTCUSDT-1h-2022-06.csv"
    csv.write_text(
        "open_time,open,high,low,close,volume,close_time,quote_volume,count,taker_base,taker_quote,ignore\n"
        "1577836800000,7000,7010,6990,7005,0,1577840399999,0,0,0,0,0\n"
        "1577840400000,7005,7020,7000,7012,0,1577843999999,0,0,0,0,0\n"
    )
    df = parse_kline_csv(csv, close_col_name="mark_close")
    assert len(df) == 2, f"Expected 2 rows after header skip, got {len(df)}"
    assert list(df["open_time_utc"]) == [
        pd.Timestamp("2020-01-01 00:00:00", tz="UTC"),
        pd.Timestamp("2020-01-01 01:00:00", tz="UTC"),
    ]
    assert df["mark_close"].tolist() == [7005.0, 7012.0]
    assert str(df["open_time_utc"].dtype) == "datetime64[ms, UTC]"
    assert (df["source"] == "binance_vision").all()


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


# ---------------------------------------------------------------------------
# Task A5: CCXT incremental markprice update
# ---------------------------------------------------------------------------

from ingestion import markprice_incremental_update  # noqa: E402


class _FakeMarkpriceExchange:
    """Minimal CCXT-shaped stub exposing fetch_ohlcv with a `price` param.

    The implementation calls fetch_ohlcv(symbol, timeframe, since, params={"price":"mark"})
    and fetch_ohlcv(symbol, timeframe, since, params={"price":"index"}).  This stub
    routes on the `price` key and returns synthetic OHLCV rows for each series.

    Each OHLCV row is: [timestamp_ms, open, high, low, close, volume].
    Only `close` (index 4) is used by the normalizer.
    """

    def __init__(self, mark_rows: list[list], index_rows: list[list]):
        self._mark = mark_rows
        self._index = index_rows
        self.calls: list[dict] = []

    def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str,
        since: int | None = None,
        limit: int | None = None,
        params: dict | None = None,
    ) -> list[list]:
        price_type = (params or {}).get("price", "mark")
        self.calls.append({"symbol": symbol, "timeframe": timeframe, "since": since, "price": price_type})
        rows = self._mark if price_type == "mark" else self._index
        if since is not None:
            rows = [r for r in rows if r[0] >= since]
        if limit is not None:
            rows = rows[:limit]
        return rows


_T0 = 1577836800000   # 2020-01-01 00:00 UTC
_T1 = 1577840400000   # 2020-01-01 01:00 UTC


def _mark_rows() -> list[list]:
    return [
        [_T0, 7000.0, 7010.0, 6990.0, 7005.0, 0],
        [_T1, 7005.0, 7020.0, 7000.0, 7012.0, 0],
    ]


def _index_rows() -> list[list]:
    return [
        [_T0, 6999.0, 7009.0, 6989.0, 7004.0, 0],
        [_T1, 7004.0, 7019.0, 6999.0, 7011.0, 0],
    ]


def test_fetch_markprice_normalizes_to_schema():
    """fetch_all_markprice + ohlcv_to_markprice_dataframe produce the correct schema."""
    ex = _FakeMarkpriceExchange(_mark_rows(), _index_rows())
    mark_raw, index_raw = markprice_incremental_update.fetch_all_markprice(
        ex, symbol="BTC/USDT:USDT", timeframe="1h", since_ms=_T0
    )
    df = markprice_incremental_update.ohlcv_to_markprice_dataframe(mark_raw, index_raw)

    assert list(df.columns) == ["open_time_utc", "mark_close", "index_close", "source", "ingested_at_utc"]
    assert str(df["open_time_utc"].dtype) == "datetime64[ms, UTC]"
    assert str(df["ingested_at_utc"].dtype) == "datetime64[ms, UTC]"
    assert (df["source"] == "ccxt_binance").all()
    assert df["mark_close"].tolist() == [7005.0, 7012.0]
    assert df["index_close"].tolist() == [7004.0, 7011.0]
    # verify exchange was called with price="mark" and price="index"
    price_types = {c["price"] for c in ex.calls}
    assert "mark" in price_types
    assert "index" in price_types


def test_fetch_markprice_with_backoff_retries_then_succeeds(monkeypatch):
    """fetch_markprice_with_backoff retries on NetworkError and succeeds on attempt 3."""
    import ccxt

    class _FlakyExchange:
        def __init__(self):
            self.attempts = 0

        def fetch_ohlcv(self, symbol, timeframe, since=None, limit=None, params=None):
            self.attempts += 1
            if self.attempts < 3:
                raise ccxt.NetworkError("transient")
            return [[_T0, 7000.0, 7010.0, 6990.0, 7005.0, 0]]

    monkeypatch.setattr(markprice_incremental_update.time, "sleep", lambda *_: None)
    ex = _FlakyExchange()
    out = markprice_incremental_update.fetch_markprice_with_backoff(
        ex, symbol="BTC/USDT:USDT", timeframe="1h", since=_T0, price_type="mark"
    )
    assert ex.attempts == 3
    assert out[0][4] == 7005.0


def test_fetch_markprice_inner_joins_mark_and_index():
    """ohlcv_to_markprice_dataframe inner-joins: timestamps missing from either series are dropped."""
    mark_raw = [
        [_T0, 7000.0, 7010.0, 6990.0, 7005.0, 0],
        [_T1, 7005.0, 7020.0, 7000.0, 7012.0, 0],
    ]
    # index missing _T1 → inner join drops _T1
    index_raw = [
        [_T0, 6999.0, 7009.0, 6989.0, 7004.0, 0],
    ]
    df = markprice_incremental_update.ohlcv_to_markprice_dataframe(mark_raw, index_raw)
    assert len(df) == 1
    assert df["open_time_utc"].iloc[0] == pd.Timestamp("2020-01-01 00:00:00", tz="UTC")
    assert df["mark_close"].iloc[0] == 7005.0
    assert df["index_close"].iloc[0] == 7004.0


def test_ohlcv_to_markprice_dataframe_empty():
    """ohlcv_to_markprice_dataframe on empty input returns empty schema-compliant DataFrame."""
    df = markprice_incremental_update.ohlcv_to_markprice_dataframe([], [])
    assert list(df.columns) == ["open_time_utc", "mark_close", "index_close", "source", "ingested_at_utc"]
    assert len(df) == 0

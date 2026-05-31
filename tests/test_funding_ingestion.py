"""Tests for Path A funding-rate ingestion (Tasks A1-A5).

Covers the funding schema block, Binance Vision CSV parsing, the funding
validator, archive-before-overwrite reconcile, and CCXT incremental update.
All UTC. Mirrors the OHLCV ingestion test conventions.
"""

import sys
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


# ---------------------------------------------------------------------------
# Task A4: funding reconcile + archive
# ---------------------------------------------------------------------------

from ingestion import funding_reconcile


def _funding_row(ts_ms, rate, source):
    return {
        "open_time_utc": pd.to_datetime(ts_ms, unit="ms", utc=True),
        "funding_rate": rate,
        "funding_interval_hours": 8,
        "source": source,
        "ingested_at_utc": pd.to_datetime(0, unit="ms", utc=True),
    }


def test_reconcile_dedup_prefers_binance_vision():
    # Same PK present in both venues; binance_vision must win.
    existing = pd.DataFrame([
        _funding_row(1577836800000, 0.0001, "ccxt_binance"),
        _funding_row(1577865600000, -0.00005, "ccxt_binance"),
    ])
    new = pd.DataFrame([
        _funding_row(1577836800000, 0.0009, "binance_vision"),   # conflict on first PK
        _funding_row(1577894400000, 0.0002, "binance_vision"),   # new PK
    ])
    merged, stats = funding_reconcile.reconcile_funding(existing, new)
    # unique + sorted PK
    assert merged["open_time_utc"].is_monotonic_increasing
    assert merged["open_time_utc"].duplicated().sum() == 0
    # binance_vision won the conflict on the first PK
    first = merged.iloc[0]
    assert first["source"] == "binance_vision"
    assert first["funding_rate"] == 0.0009
    assert len(merged) == 3


def test_reconcile_archives_before_overwrite(tmp_path):
    archive_dir = tmp_path / "archive"
    canonical = tmp_path / "btcusdt_funding_8h.parquet"
    df = pd.DataFrame([_funding_row(1577836800000, 0.0001, "binance_vision")])
    df.to_parquet(canonical, engine="pyarrow", index=False)

    archived = funding_reconcile.archive_file(canonical, archive_dir=archive_dir)
    assert archived is not None
    assert archived.exists()
    assert archived.parent == archive_dir
    assert archived.name.startswith("btcusdt_funding_8h_")
    assert archived.suffix == ".parquet"
    # original is preserved (copy, not move)
    assert canonical.exists()


# ---------------------------------------------------------------------------
# Task A5: CCXT incremental funding update
# ---------------------------------------------------------------------------

from ingestion import funding_incremental_update


class _FakeFundingExchange:
    """Minimal CCXT-shaped stub exposing fetch_funding_rate_history (snake_case).

    Returns the standard CCXT unified funding-rate-history shape: a list of
    dicts with `timestamp` (ms) and `fundingRate`. Paginates by `since` and
    stops once the window is exhausted (mirrors how the real client behaves).
    """

    def __init__(self, rows):
        self._rows = rows
        self.calls = []

    def fetch_funding_rate_history(self, symbol=None, since=None, limit=None, params=None):
        self.calls.append({"symbol": symbol, "since": since, "limit": limit})
        if since is None:
            out = list(self._rows)
        else:
            out = [r for r in self._rows if r["timestamp"] >= since]
        # Respect the page-size cap so pagination is exercised realistically.
        if limit is not None:
            out = out[:limit]
        return out


def test_fetch_funding_history_normalizes_to_schema():
    rows = [
        {"timestamp": 1577836800000, "fundingRate": 0.0001, "symbol": "BTC/USDT:USDT"},
        {"timestamp": 1577865600000, "fundingRate": -0.00005, "symbol": "BTC/USDT:USDT"},
    ]
    ex = _FakeFundingExchange(rows)
    df = funding_incremental_update.fetch_all_funding(
        ex, symbol="BTC/USDT:USDT", since_ms=1577836800000
    )
    df = funding_incremental_update.funding_history_to_dataframe(df)

    assert list(df["open_time_utc"]) == [
        pd.Timestamp("2020-01-01 00:00:00", tz="UTC"),
        pd.Timestamp("2020-01-01 08:00:00", tz="UTC"),
    ]
    assert df["funding_rate"].tolist() == [0.0001, -0.00005]
    assert (df["source"] == "ccxt_binance").all()
    assert str(df["open_time_utc"].dtype) == "datetime64[ms, UTC]"
    assert (df["funding_interval_hours"] == 8).all()
    # the implementation called the snake_case CCXT method
    assert ex.calls and ex.calls[0]["symbol"] == "BTC/USDT:USDT"


def test_fetch_with_funding_backoff_retries_then_succeeds(monkeypatch):
    import ccxt

    class _FlakyExchange:
        def __init__(self):
            self.attempts = 0

        def fetch_funding_rate_history(self, symbol=None, since=None, limit=None, params=None):
            self.attempts += 1
            if self.attempts < 3:
                raise ccxt.NetworkError("transient")
            return [{"timestamp": 1577836800000, "fundingRate": 0.0001}]

    monkeypatch.setattr(funding_incremental_update.time, "sleep", lambda *_: None)
    ex = _FlakyExchange()
    out = funding_incremental_update.fetch_funding_with_backoff(
        ex, symbol="BTC/USDT:USDT", since=0
    )
    assert ex.attempts == 3
    assert out[0]["fundingRate"] == 0.0001


# ---------------------------------------------------------------------------
# B2 review fix #1: CCXT None/NaN fundingRate guard in to_dataframe
# ---------------------------------------------------------------------------


def test_funding_history_to_dataframe_drops_none_funding_rate():
    # Binance returns fundingRate=None during outages; must not crash, must drop.
    rows = [
        {"timestamp": 1577836800000, "fundingRate": 0.0001},
        {"timestamp": 1577865600000, "fundingRate": None},
        {"timestamp": 1577894400000, "fundingRate": -0.00005},
    ]
    df = funding_incremental_update.funding_history_to_dataframe(rows)
    assert len(df) == 2
    assert df["funding_rate"].tolist() == [0.0001, -0.00005]
    assert df["funding_rate"].isna().sum() == 0


def test_funding_history_to_dataframe_all_none_returns_empty_schema():
    rows = [
        {"timestamp": 1577836800000, "fundingRate": None},
        {"timestamp": 1577865600000, "fundingRate": float("nan")},
    ]
    df = funding_incremental_update.funding_history_to_dataframe(rows)
    assert len(df) == 0
    assert list(df.columns) == [
        "open_time_utc", "funding_rate", "funding_interval_hours",
        "ingested_at_utc", "source",
    ]


# ---------------------------------------------------------------------------
# B2 review fix #4 + #10: pagination must not skip a settlement between page
# boundaries (advance cursor by last_ts + 1ms, not + 8h).
# ---------------------------------------------------------------------------


def test_fetch_all_funding_does_not_skip_mid_interval_settlement():
    # FUNDING_LIMIT settlements 8h apart, then a settlement at last_ts + 4h
    # (between page boundaries). The +8h cursor advance would skip it; the
    # +1ms advance must fetch it.
    limit = funding_incremental_update.FUNDING_LIMIT
    base = 1577836800000
    eight_h = funding_incremental_update.EIGHT_HOURS_MS
    rows = [{"timestamp": base + i * eight_h, "fundingRate": 0.0001} for i in range(limit)]
    last_full = rows[-1]["timestamp"]
    mid = last_full + eight_h // 2  # +4h between page boundaries
    rows.append({"timestamp": mid, "fundingRate": 0.0002})

    ex = _FakeFundingExchange(rows)
    out = funding_incremental_update.fetch_all_funding(ex, symbol="BTC/USDT:USDT", since_ms=base)
    fetched_ts = {r["timestamp"] for r in out}
    assert mid in fetched_ts, "settlement at last_ts + 4h was skipped (off-by-8h pagination)"
    assert len(out) == limit + 1


# ---------------------------------------------------------------------------
# B2 review fix #11: non-BTCUSDT pair is rejected (Phase A is BTCUSDT only)
# ---------------------------------------------------------------------------


def test_incremental_main_rejects_non_btcusdt_pair(monkeypatch):
    import pytest as _pytest
    monkeypatch.setattr(sys, "argv", ["funding_incremental_update", "--pair", "ETHUSDT"])
    with _pytest.raises(ValueError):
        funding_incremental_update.main()


# ---------------------------------------------------------------------------
# B2 review fix #5: reconcile write is atomic (staging -> replace)
# ---------------------------------------------------------------------------


def test_reconcile_main_writes_atomically(tmp_path, monkeypatch):
    existing = tmp_path / "btcusdt_funding_8h.parquet"
    update = tmp_path / "btcusdt_funding_8h_update.parquet"
    pd.DataFrame([_funding_row(1577836800000, 0.0001, "binance_vision")]).to_parquet(
        existing, engine="pyarrow", index=False
    )
    pd.DataFrame([_funding_row(1577865600000, 0.0002, "binance_vision")]).to_parquet(
        update, engine="pyarrow", index=False
    )

    captured = {}
    real_replace = Path.replace

    def _spy_replace(self, target):
        captured["staging"] = str(self)
        captured["target"] = str(target)
        return real_replace(self, target)

    monkeypatch.setattr(Path, "replace", _spy_replace)
    monkeypatch.setattr(funding_reconcile, "QUALITY_DIR", tmp_path / "quality")
    monkeypatch.setattr(funding_reconcile, "ARCHIVE_DIR", tmp_path / "archive")
    monkeypatch.setattr(
        sys, "argv",
        ["funding_reconcile", "--existing", str(existing), "--new", str(update)],
    )
    rc = funding_reconcile.main()
    assert rc == 0
    assert captured.get("staging", "").endswith(".staging")
    assert captured.get("target") == str(existing)
    merged = pd.read_parquet(existing)
    assert len(merged) == 2
    # no leftover staging file
    assert not (tmp_path / "btcusdt_funding_8h.parquet.staging").exists()


# ---------------------------------------------------------------------------
# B2 review fix #2, #3, #6, #8, #9: validator negative + gap cases
# ---------------------------------------------------------------------------


def test_validate_funding_rejects_null_source():
    df = _good()
    df.loc[1, "source"] = None
    report = validate_funding(df)
    assert report["ok"] is False
    assert any("null" in e.lower() and "source" in e.lower() for e in report["errors"])


def test_validate_funding_rejects_unrecognized_source():
    df = _good()
    df["source"] = ["binance_vision", "ftx_dead"]
    report = validate_funding(df)
    assert report["ok"] is False
    assert any("invalid" in e.lower() for e in report["errors"])


def test_validate_funding_rejects_nonpositive_interval():
    df = _good()
    df.loc[1, "funding_interval_hours"] = 0
    report = validate_funding(df)
    assert report["ok"] is False
    assert any("funding_interval_hours" in e for e in report["errors"])


def test_validate_funding_rejects_nan_interval():
    df = _good()
    df["funding_interval_hours"] = df["funding_interval_hours"].astype("float64")
    df.loc[1, "funding_interval_hours"] = float("nan")
    report = validate_funding(df)
    assert report["ok"] is False
    assert any("funding_interval_hours" in e for e in report["errors"])


def test_validate_funding_rejects_missing_required_column():
    df = _good().drop(columns=["funding_rate"])
    report = validate_funding(df)
    assert report["ok"] is False
    assert any("Missing columns" in e for e in report["errors"])


def test_validate_funding_rejects_nan_funding_rate():
    df = _good()
    df.loc[1, "funding_rate"] = float("nan")
    report = validate_funding(df)
    assert report["ok"] is False
    assert any("funding_rate" in e for e in report["errors"])


def test_validate_funding_flags_gap_even_when_error_present():
    # A gap (24h between two settlements) AND an error (bad source) coexist.
    # Gap must still be flagged as a warning (no_forward_fill rule).
    df = pd.DataFrame({
        "open_time_utc": pd.to_datetime(
            [1577836800000, 1577836800000 + 24 * 3_600_000], unit="ms", utc=True
        ).as_unit("ms"),
        "funding_rate": [0.0001, -0.00005],
        "funding_interval_hours": [8, 8],
        "source": ["binance_vision", "ftx_dead"],  # invalid -> error
        "ingested_at_utc": pd.to_datetime([0, 0], unit="ms", utc=True).as_unit("ms"),
    })
    report = validate_funding(df)
    assert report["ok"] is False  # error present
    assert any("gap" in w.lower() for w in report["warnings"])  # but gap still flagged


def test_validate_funding_jitter_is_not_a_gap():
    # A6 regression: Binance calc_time jitters a few ms off the nominal 8h
    # boundary (8h +/- 1-2ms). Sub-minute jitter must NOT be flagged as a gap.
    # (An exact-8h comparison spuriously flagged ~61% of real settlements.)
    base = 1577836800000
    ms = [base, base + 8 * 3_600_000 + 1, base + 16 * 3_600_000 - 1, base + 24 * 3_600_000 + 2]
    df = pd.DataFrame({
        "open_time_utc": pd.to_datetime(ms, unit="ms", utc=True).as_unit("ms"),
        "funding_rate": [0.0001, -0.00005, 0.0002, 0.0],
        "funding_interval_hours": [8, 8, 8, 8],
        "source": ["binance_vision"] * 4,
        "ingested_at_utc": pd.to_datetime([0, 0, 0, 0], unit="ms", utc=True).as_unit("ms"),
    })
    report = validate_funding(df)
    assert report["ok"] is True
    assert not any("gap" in w.lower() for w in report["warnings"])  # jitter != gap


def test_validate_funding_flags_real_missing_settlement():
    # A real missing settlement: 16h spacing (2x the 8h interval) IS a gap.
    base = 1577836800000
    ms = [base, base + 16 * 3_600_000]  # the 8h-mark settlement is missing
    df = pd.DataFrame({
        "open_time_utc": pd.to_datetime(ms, unit="ms", utc=True).as_unit("ms"),
        "funding_rate": [0.0001, -0.00005],
        "funding_interval_hours": [8, 8],
        "source": ["binance_vision"] * 2,
        "ingested_at_utc": pd.to_datetime([0, 0], unit="ms", utc=True).as_unit("ms"),
    })
    report = validate_funding(df)
    assert report["ok"] is True  # gap is a warning, not an error
    assert any("gap" in w.lower() for w in report["warnings"])

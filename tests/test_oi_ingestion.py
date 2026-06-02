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


# ---------------------------------------------------------------------------
# A3: downsample_oi_to_1h tests
# ---------------------------------------------------------------------------

import numpy as np
from ingestion.oi_bulk_download import downsample_oi_to_1h


def test_downsample_bar_close_is_last_obs_within_bar():
    # row N (bar [N, N+1h)) = the LAST 5-min obs WITHIN the bar (the mark_close analog),
    # stamped at N to align with the OHLCV open_time grid. label='left', closed='left'.
    ts = pd.date_range("2020-09-01 00:00", "2020-09-01 02:00", freq="5min", tz="UTC")
    df5 = pd.DataFrame({"open_time_utc": ts,
                        "sum_open_interest": np.arange(len(ts), dtype="float64"),
                        "sum_open_interest_value": np.arange(len(ts), dtype="float64") * 10.0,
                        "source": "binance_vision"})
    out = downsample_oi_to_1h(df5)
    # bar [01:00, 02:00) -> last within-bar obs is 01:55 (index 23) -> value 23.0
    row01 = out.loc[out.open_time_utc == pd.Timestamp("2020-09-01 01:00", tz="UTC")]
    assert row01["sum_open_interest"].iloc[0] == 23.0
    assert str(out["open_time_utc"].dtype) == "datetime64[ms, UTC]"
    assert (out["open_time_utc"].diff().dropna() == pd.Timedelta("1h")).all()


def test_downsample_row_depends_only_on_within_bar_obs():
    # Causality: row 01:00 (bar [01:00,02:00)) is unchanged when obs at/after the NEXT
    # bar boundary (02:00) are deleted -> it never reads a future bar.
    ts = pd.date_range("2020-09-01 00:00", "2020-09-01 03:00", freq="5min", tz="UTC")
    df5 = pd.DataFrame({"open_time_utc": ts, "sum_open_interest": np.arange(len(ts), dtype="float64"),
                        "sum_open_interest_value": np.zeros(len(ts)), "source": "binance_vision"})
    full = downsample_oi_to_1h(df5)
    truncated = downsample_oi_to_1h(df5[df5.open_time_utc < pd.Timestamp("2020-09-01 02:00", tz="UTC")])
    key = pd.Timestamp("2020-09-01 01:00", tz="UTC")
    v_full = full.loc[full.open_time_utc == key, "sum_open_interest"].iloc[0]
    v_trunc = truncated.loc[truncated.open_time_utc == key, "sum_open_interest"].iloc[0]
    assert v_full == v_trunc


def test_downsample_gap_within_hour_yields_no_row():
    # If an entire 1h window has no OI observations, that 1h bar is absent from output
    # (gap NOT filled/interpolated). The surrounding bars are unaffected.
    ts_before = pd.date_range("2020-09-01 00:00", "2020-09-01 00:55", freq="5min", tz="UTC")
    # Skip all of 01:xx (the entire 01:00 hour)
    ts_after = pd.date_range("2020-09-01 02:00", "2020-09-01 02:55", freq="5min", tz="UTC")
    ts = ts_before.append(ts_after)
    vals = np.arange(len(ts), dtype="float64")
    df5 = pd.DataFrame({"open_time_utc": ts, "sum_open_interest": vals,
                        "sum_open_interest_value": vals * 10.0, "source": "binance_vision"})
    out = downsample_oi_to_1h(df5)
    out_times = list(out["open_time_utc"])
    # The 01:00 bar must be absent
    assert pd.Timestamp("2020-09-01 01:00", tz="UTC") not in out_times
    # The 00:00 and 02:00 bars must be present
    assert pd.Timestamp("2020-09-01 00:00", tz="UTC") in out_times
    assert pd.Timestamp("2020-09-01 02:00", tz="UTC") in out_times


def test_downsample_boundary_obs_at_exactly_N_plus_1h_does_not_leak():
    # LEAKAGE GUARD (A3 review MEDIUM): an obs stamped at exactly the bar boundary N+1h
    # (02:00) belongs to bar 02:00, NOT bar 01:00. closed='left' makes [N, N+1h) half-open,
    # so a large boundary value (999) must NOT appear in bar 01:00 (would prove look-ahead).
    ts = pd.to_datetime(["2020-09-01 01:55", "2020-09-01 02:00"], utc=True)
    df5 = pd.DataFrame({"open_time_utc": ts, "sum_open_interest": [23.0, 999.0],
                        "sum_open_interest_value": [0.0, 0.0], "source": "binance_vision"})
    out = downsample_oi_to_1h(df5)
    bar01 = out.loc[out.open_time_utc == pd.Timestamp("2020-09-01 01:00", tz="UTC"), "sum_open_interest"].iloc[0]
    assert bar01 == 23.0   # 999.0 would indicate the N+1h boundary obs leaked into bar N
    bar02 = out.loc[out.open_time_utc == pd.Timestamp("2020-09-01 02:00", tz="UTC"), "sum_open_interest"].iloc[0]
    assert bar02 == 999.0  # the boundary obs belongs to bar 02:00

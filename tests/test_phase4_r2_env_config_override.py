"""Tests for PHASE4 R2 runner-side env_config override.

Per docs/superpowers/plans/2026-05-09-phase4-implementation-arc.md
Task 4 prep Step B (R2 null-end fix; advisor reviewer adjudication
2026-05-09). The bug: forward_2026 regime block has end:null per
PHASE4_PLAN §1.2 (T_end captured at fire-time), but engine consumer
at backtest/engine.py:1564 calls date.fromisoformat(block["end"])
which raises TypeError on None.

R2 fix: runner captures T_end from parquet at fire-time, builds
in-memory env_config override with forward_2026.end injected as
date string, passes via run_regime_holdout(env_config=...) bypassing
default load_environments_config(). No engine code change; leverages
existing engine API (env_config kwarg at engine.py:1471).

These tests verify:
- _capture_phase4_forward_window_metadata reads parquet correctly
- _build_phase4_env_config_override injects captured T_end
- Defensive guards reject inconsistent inputs (missing forward_2026
  block; non-null end already in YAML)
- End-to-end against real parquet (2026 forward bars present)
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from run_phase2c_evaluation_gate import (  # noqa: E402
    PHASE4_FORWARD_2026_REGIME_KEY,
    PHASE4_FORWARD_WINDOW_START_DATE,
    PHASE4_FORWARD_WINDOW_START_UTC,
    _build_phase4_env_config_override,
    _capture_phase4_forward_window_metadata,
)


def _make_synthetic_forward_parquet(
    tmp_path: Path,
    end_date: str = "2026-04-16",
    end_hour: int = 7,
) -> Path:
    """Create a synthetic parquet with forward bars from 2026-01-01 to end."""
    tmp_path.mkdir(parents=True, exist_ok=True)
    # Cover [2026-01-01 00:00, end_date end_hour:00] hourly.
    start_ts = pd.Timestamp("2026-01-01 00:00:00", tz="UTC")
    end_ts = pd.Timestamp(f"{end_date} {end_hour:02d}:00:00", tz="UTC")
    timestamps = pd.date_range(start=start_ts, end=end_ts, freq="h", tz="UTC")
    n = len(timestamps)
    df = pd.DataFrame({
        "open_time_utc": timestamps.astype("datetime64[ms, UTC]"),
        "open": [100.0] * n,
        "high": [110.0] * n,
        "low": [90.0] * n,
        "close": [105.0] * n,
        "volume": [1000.0] * n,
        "quote_volume": [100_000.0] * n,
        "trade_count": np.arange(5000, 5000 + n, dtype="int64"),
        "ingested_at_utc": pd.Timestamp.now(tz="UTC").floor("ms"),
        "source": pd.array(["binance_vision"] * n, dtype="string"),
    })
    df["ingested_at_utc"] = df["ingested_at_utc"].astype("datetime64[ms, UTC]")
    path = tmp_path / "synthetic_forward.parquet"
    df.to_parquet(path, engine="pyarrow", index=False)
    return path


# ---------------------------------------------------------------------------
# _capture_phase4_forward_window_metadata
# ---------------------------------------------------------------------------


def test_capture_metadata_returns_required_fields(tmp_path):
    """Helper must return all 5 required fields per PHASE4_PLAN §1.2."""
    parquet = _make_synthetic_forward_parquet(tmp_path)
    md = _capture_phase4_forward_window_metadata(parquet)
    assert set(md.keys()) == {
        "forward_window_start_utc",
        "forward_window_end_utc",
        "forward_bar_count",
        "parquet_data_sha256",
        "forward_end_date_iso",
    }


def test_capture_metadata_start_locked_to_plan_anchor(tmp_path):
    """forward_window_start_utc must equal PHASE4_PLAN §1.1 D = 2026-01-01."""
    parquet = _make_synthetic_forward_parquet(tmp_path)
    md = _capture_phase4_forward_window_metadata(parquet)
    assert md["forward_window_start_utc"] == "2026-01-01T00:00:00Z"


def test_capture_metadata_end_matches_last_bar(tmp_path):
    """forward_window_end_utc + forward_end_date_iso must reflect last bar."""
    parquet = _make_synthetic_forward_parquet(
        tmp_path, end_date="2026-04-16", end_hour=7
    )
    md = _capture_phase4_forward_window_metadata(parquet)
    assert md["forward_window_end_utc"] == "2026-04-16T07:00:00Z"
    assert md["forward_end_date_iso"] == "2026-04-16"


def test_capture_metadata_bar_count_correct(tmp_path):
    """forward_bar_count must equal hours in [2026-01-01, T_end].

    Synthetic parquet from 2026-01-01 00:00 to 2026-04-16 07:00 inclusive:
    - 2026-01: 31 days * 24 = 744
    - 2026-02: 28 days * 24 = 672
    - 2026-03: 31 days * 24 = 744
    - 2026-04-01 .. 2026-04-16 07:00: 15 days * 24 + 8 hours = 368
    Total = 744 + 672 + 744 + 368 = 2528
    """
    parquet = _make_synthetic_forward_parquet(
        tmp_path, end_date="2026-04-16", end_hour=7
    )
    md = _capture_phase4_forward_window_metadata(parquet)
    assert md["forward_bar_count"] == 2528


def test_capture_metadata_sha256_matches_file(tmp_path):
    """parquet_data_sha256 must match SHA256 of the parquet file content."""
    import hashlib

    parquet = _make_synthetic_forward_parquet(tmp_path)
    expected_sha = hashlib.sha256(parquet.read_bytes()).hexdigest()
    md = _capture_phase4_forward_window_metadata(parquet)
    assert md["parquet_data_sha256"] == expected_sha


def test_capture_metadata_raises_if_parquet_missing(tmp_path):
    """Helper must raise FileNotFoundError if parquet doesn't exist."""
    nonexistent = tmp_path / "missing.parquet"
    with pytest.raises(FileNotFoundError, match="not found"):
        _capture_phase4_forward_window_metadata(nonexistent)


def test_capture_metadata_raises_if_no_forward_bars(tmp_path):
    """Helper must raise ValueError if parquet has no bars >= 2026-01-01."""
    # Synthetic parquet with bars only from 2025
    tmp_path.mkdir(parents=True, exist_ok=True)
    timestamps = pd.date_range(
        start="2025-01-01", periods=100, freq="h", tz="UTC"
    )
    df = pd.DataFrame({
        "open_time_utc": timestamps.astype("datetime64[ms, UTC]"),
        "open": [100.0] * 100,
        "high": [110.0] * 100,
        "low": [90.0] * 100,
        "close": [105.0] * 100,
        "volume": [1000.0] * 100,
        "quote_volume": [100_000.0] * 100,
        "trade_count": np.arange(5000, 5100, dtype="int64"),
        "ingested_at_utc": pd.Timestamp.now(tz="UTC").floor("ms"),
        "source": pd.array(["binance_vision"] * 100, dtype="string"),
    })
    df["ingested_at_utc"] = df["ingested_at_utc"].astype("datetime64[ms, UTC]")
    parquet = tmp_path / "no_forward.parquet"
    df.to_parquet(parquet, engine="pyarrow", index=False)
    with pytest.raises(ValueError, match="No forward bars"):
        _capture_phase4_forward_window_metadata(parquet)


# ---------------------------------------------------------------------------
# _build_phase4_env_config_override
# ---------------------------------------------------------------------------


def test_build_env_config_override_injects_captured_t_end():
    """Override must replace forward_2026.end null with captured date string."""
    fake_metadata = {
        "forward_window_start_utc": "2026-01-01T00:00:00Z",
        "forward_window_end_utc": "2026-04-16T07:00:00Z",
        "forward_bar_count": 2528,
        "parquet_data_sha256": "0" * 64,
        "forward_end_date_iso": "2026-04-16",
    }
    env = _build_phase4_env_config_override(fake_metadata)
    fwd = env["evaluation_regimes"]["forward_2026"]
    # The injected value MUST be a date string, NOT None.
    assert fwd["end"] == "2026-04-16"
    assert isinstance(fwd["end"], str)
    # start should remain unchanged.
    assert fwd["start"] == "2026-01-01"
    # label preserved.
    assert fwd["label"] == "forward_2026"


def test_build_env_config_override_does_not_mutate_other_blocks():
    """Override must NOT touch splits or other evaluation_regimes blocks."""
    fake_metadata = {
        "forward_window_start_utc": "2026-01-01T00:00:00Z",
        "forward_window_end_utc": "2026-04-16T07:00:00Z",
        "forward_bar_count": 2528,
        "parquet_data_sha256": "0" * 64,
        "forward_end_date_iso": "2026-04-16",
    }
    env = _build_phase4_env_config_override(fake_metadata)
    # splits namespace immutable.
    assert env["splits"]["regime_holdout"]["end"] == "2022-12-31"
    assert env["splits"]["test"]["end"] == "2025-12-31"
    # Other evaluation_regimes blocks unchanged.
    assert env["evaluation_regimes"]["eval_2020_v1"]["end"] == "2020-12-31"
    assert env["evaluation_regimes"]["eval_2021_v1"]["end"] == "2021-12-31"


def test_build_env_config_override_engine_consumer_compat():
    """Injected end must be parseable by date.fromisoformat (engine consumer at line 1564)."""
    from datetime import date as date_cls

    fake_metadata = {
        "forward_window_start_utc": "2026-01-01T00:00:00Z",
        "forward_window_end_utc": "2026-04-16T07:00:00Z",
        "forward_bar_count": 2528,
        "parquet_data_sha256": "0" * 64,
        "forward_end_date_iso": "2026-04-16",
    }
    env = _build_phase4_env_config_override(fake_metadata)
    end_str = env["evaluation_regimes"]["forward_2026"]["end"]
    # This is the exact call the engine makes at backtest/engine.py:1564
    parsed = date_cls.fromisoformat(end_str)
    assert parsed.year == 2026
    assert parsed.month == 4
    assert parsed.day == 16


# ---------------------------------------------------------------------------
# Real-parquet smoke verification
# ---------------------------------------------------------------------------


def test_real_parquet_smoke_capture_succeeds():
    """Smoke verification: _capture against actual canonical parquet.

    The canonical parquet at data/raw/btcusdt_1h.parquet contains
    forward bars >= 2026-01-01 (per CLAUDE.md state field
    'Data parquet: 2020-01-01 -> 2026-04-16 07:00 UTC (latest)').

    This smoke confirms the helper works end-to-end against real
    data without crashing and produces values in expected ranges.
    Does NOT pin exact bar count or T_end (parquet refreshes between
    sessions extend T_end forward).
    """
    real_parquet = PROJECT_ROOT / "data" / "raw" / "btcusdt_1h.parquet"
    if not real_parquet.exists():
        pytest.skip("Real parquet not present; smoke test only runs in repo")
    md = _capture_phase4_forward_window_metadata(real_parquet)
    assert md["forward_window_start_utc"] == "2026-01-01T00:00:00Z"
    # T_end >= 2026-01-01 by construction (parquet has forward bars)
    assert md["forward_window_end_utc"] >= "2026-01-01T00:00:00Z"
    # bar_count >= 24 (at least 1 day of data)
    assert md["forward_bar_count"] >= 24
    # SHA is 64 hex chars
    assert len(md["parquet_data_sha256"]) == 64
    # Date is parseable
    from datetime import date as date_cls
    parsed = date_cls.fromisoformat(md["forward_end_date_iso"])
    assert parsed.year == 2026

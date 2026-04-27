"""Smoke tests for scripts/run_phase1b_corrected.py.

Verifies:
  1. The script's lineage guard fires BEFORE any engine call.
  2. Both per-baseline AND aggregate summaries carry all 4 lineage fields.
  3. The script refuses to overwrite a non-empty existing batch dir
     without --force.

These tests do NOT exercise the corrected engine itself — that is
covered by the engine tests under tests/test_engine_*.py. Here we
mock run_walk_forward and only verify the script's plumbing
(arg-parse → guard ordering → metadata stamping → overwrite gate).
"""
from __future__ import annotations

import importlib
import json
import sys
from datetime import date
from pathlib import Path
from unittest.mock import patch

import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backtest.engine import BacktestResult, WalkForwardResult  # noqa: E402

# Import the script as a module for direct main() invocation.
runner = importlib.import_module("scripts.run_phase1b_corrected")


# ---------------------------------------------------------------------------
# Stub builder
# ---------------------------------------------------------------------------


def _build_stub_backtest_result(
    run_id: str,
    strategy_name: str,
    test_start_iso: str,
    test_end_iso: str,
) -> BacktestResult:
    """Build a stub BacktestResult matching the dataclass shape in engine.py."""
    idx = pd.DatetimeIndex(pd.date_range(test_start_iso, test_end_iso, freq="h"))
    equity = pd.Series([10000.0] * len(idx), index=idx, dtype=float)
    return BacktestResult(
        run_id=run_id,
        strategy_name=strategy_name,
        trades=[],
        equity_curve=equity,
        metrics={
            "total_return": -0.05,
            "sharpe_ratio": -0.2,
            "max_drawdown": 0.1,
            "max_drawdown_duration_hours": 24.0,
            "initial_capital": 10000.0,
            "final_capital": 9500.0,
            "total_trades": 12,
            "win_rate": 0.4,
            "avg_trade_duration_hours": 6.0,
            "avg_trade_return": -0.004,
            "profit_factor": 0.8,
        },
        trade_csv_path=None,
        warmup_bars=50,
        effective_start=None,
        start_date=pd.Timestamp(test_start_iso).to_pydatetime(),
        end_date=pd.Timestamp(test_end_iso).to_pydatetime(),
        params={},
    )


def _build_stub_wf_result(strategy_name: str = "sma_crossover") -> WalkForwardResult:
    """Build a stub WalkForwardResult with one window's BacktestResult."""
    windows = [
        (
            date(2020, 1, 1), date(2020, 12, 31),
            date(2021, 1, 1), date(2021, 3, 31),
        ),
    ]
    window_results = [
        _build_stub_backtest_result(
            run_id="stub-window-1",
            strategy_name=strategy_name,
            test_start_iso="2021-01-01",
            test_end_iso="2021-03-31",
        ),
    ]
    summary_metrics = {
        "total_return": -0.05,
        "sharpe_ratio": -0.2,
        "max_drawdown": 0.1,
        "max_drawdown_duration_hours": 24.0,
        "initial_capital": 10000.0,
        "final_capital": None,
        "total_trades": 12,
        "win_rate": 0.4,
        "avg_trade_duration_hours": 6.0,
        "avg_trade_return": -0.004,
        "profit_factor": 0.8,
    }
    return WalkForwardResult(
        summary_run_id="stub-summary-1",
        window_results=window_results,
        summary_metrics=summary_metrics,
        windows=windows,
    )


# ---------------------------------------------------------------------------
# Test 1 — guard fires before any run_walk_forward call
# ---------------------------------------------------------------------------


def test_script_imports_lineage_guard(tmp_path, monkeypatch):
    """enforce_corrected_engine_lineage() runs before run_walk_forward."""
    call_order: list[str] = []

    def _fake_guard():
        call_order.append("guard")
        return "deadbeef"

    def _fake_run_wf(strategy_cls, **kwargs):
        call_order.append(f"wf:{strategy_cls.__name__}")
        return _build_stub_wf_result(strategy_cls.__name__)

    monkeypatch.setattr(
        runner, "enforce_corrected_engine_lineage", _fake_guard
    )
    monkeypatch.setattr(runner, "run_walk_forward", _fake_run_wf)
    monkeypatch.setattr(
        sys, "argv",
        [
            "run_phase1b_corrected.py",
            "--baseline", "sma_crossover",
            "--batch-id", "smoke-guard-order",
            "--output-root", str(tmp_path),
        ],
    )

    rc = runner.main()
    assert rc == 0
    # Guard fires first; then exactly one WF call for sma_crossover.
    assert call_order[0] == "guard", f"call_order={call_order}"
    assert any(c.startswith("wf:") for c in call_order), (
        f"no run_walk_forward call observed: {call_order}"
    )
    guard_idx = call_order.index("guard")
    first_wf_idx = next(
        i for i, c in enumerate(call_order) if c.startswith("wf:")
    )
    assert guard_idx < first_wf_idx, (
        f"guard ({guard_idx}) must precede WF ({first_wf_idx}); "
        f"call_order={call_order}"
    )


# ---------------------------------------------------------------------------
# Test 2 — metadata stamping at BOTH levels
# ---------------------------------------------------------------------------


REQUIRED_LINEAGE_FIELDS = (
    "wf_semantics",
    "corrected_wf_semantics_commit",
    "current_git_sha",
    "lineage_check",
)


def test_script_stamps_metadata_at_both_levels(tmp_path, monkeypatch):
    """Both per-baseline AND aggregate summaries carry lineage fields."""
    monkeypatch.setattr(
        runner,
        "enforce_corrected_engine_lineage",
        lambda: "feedface00112233",
    )
    monkeypatch.setattr(
        runner,
        "run_walk_forward",
        lambda strategy_cls, **kwargs: _build_stub_wf_result(
            strategy_cls.__name__
        ),
    )
    monkeypatch.setattr(
        sys, "argv",
        [
            "run_phase1b_corrected.py",
            "--baseline", "sma_crossover",
            "--batch-id", "smoke",
            "--output-root", str(tmp_path),
            "--force",
        ],
    )
    rc = runner.main()
    assert rc == 0

    batch_dir = tmp_path / "smoke"
    per_baseline_summary = batch_dir / "sma_crossover" / "walk_forward_summary.json"
    aggregate_summary = batch_dir / "walk_forward_summary.json"

    assert per_baseline_summary.exists()
    assert aggregate_summary.exists()

    with open(per_baseline_summary) as f:
        pb = json.load(f)
    with open(aggregate_summary) as f:
        agg = json.load(f)

    for field_name in REQUIRED_LINEAGE_FIELDS:
        assert field_name in pb, (
            f"per-baseline summary missing {field_name!r}: {sorted(pb.keys())}"
        )
        assert field_name in agg, (
            f"aggregate summary missing {field_name!r}: {sorted(agg.keys())}"
        )

    # Aggregate also carries baselines_run + per_baseline_summary_paths
    # + aggregate_metrics — these are aggregate-only.
    assert "baselines_run" in agg
    assert "per_baseline_summary_paths" in agg
    assert "aggregate_metrics" in agg
    assert agg["aggregate_metrics"]["n_baselines"] == 1


# ---------------------------------------------------------------------------
# Test 3 — refuses to overwrite without --force
# ---------------------------------------------------------------------------


def test_script_refuses_overwrite_without_force(tmp_path, monkeypatch, capsys):
    """An existing non-empty batch dir without --force → error mentioning --force."""
    monkeypatch.setattr(
        runner,
        "enforce_corrected_engine_lineage",
        lambda: "deadbeef",
    )
    # Pre-create a non-empty batch dir.
    batch_id = "preexisting-batch"
    batch_dir = tmp_path / batch_id
    batch_dir.mkdir()
    (batch_dir / "stale_artifact.txt").write_text("not empty\n")

    monkeypatch.setattr(
        sys, "argv",
        [
            "run_phase1b_corrected.py",
            "--baseline", "sma_crossover",
            "--batch-id", batch_id,
            "--output-root", str(tmp_path),
        ],
    )
    rc = runner.main()
    assert rc == 1, "must exit non-zero when batch dir already non-empty"
    captured = capsys.readouterr()
    combined = captured.out + captured.err
    assert "--force" in combined, (
        f"error message must mention --force; got: {combined!r}"
    )

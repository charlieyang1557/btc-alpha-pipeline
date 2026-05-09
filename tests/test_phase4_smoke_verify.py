"""Self-tests for scripts/verify_phase4_smoke.py.

Tight-scope sleeve covering 5 critical bad-input detection classes per
Mac Mini session 2026-05-09 adjudication: synthetic positive + 4
fail-mode tests for the assertion classes most likely to silently
mis-flag a real artifact (sha256 mismatch, missing forward window
metadata block, wrong regime, non-finite sharpe with passed lifecycle).

Verifier runs 5x across smoke + 4 production fires; a silent verifier
bug would cascade. The cost of these 5 self-tests (~5 min beyond
verifier authoring) is justified per §31 P1 instance #4 evidence
(this session's "verify script committed" overclaim is fresh evidence
the convergence-on-claim-accuracy pattern is still firing — Mac Mini
session 2026-05-09 carry-forward observation).

Tests import verify() directly rather than subprocess'ing the script
(faster, instrumentable failure messages).
"""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from verify_phase4_smoke import (  # noqa: E402  (sys.path hack required)
    VerificationFailure,
    verify,
)

_CSV_FIELDS = (
    "hypothesis_hash",
    "position",
    "theme",
    "name",
    "wf_test_period_sharpe",
    "lifecycle_state",
    "holdout_passed",
    "holdout_sharpe",
    "holdout_max_drawdown",
    "holdout_total_return",
    "holdout_total_trades",
    "wall_clock_seconds",
    "error_message",
)


def _build_summary_skeleton(
    cost_yaml_path: Path,
    parquet_path: Path,
) -> dict[str, Any]:
    """Build a Phase-4-shaped holdout_summary dict using real file hashes."""
    cost_sha = hashlib.sha256(cost_yaml_path.read_bytes()).hexdigest()
    parquet_sha = hashlib.sha256(parquet_path.read_bytes()).hexdigest()
    return {
        "run_id": "phase4_smoke_15bps_test",
        "source_batch_id": "synthetic-batch-id",
        "regime_key": "evaluation_regimes.forward_2026",
        "regime_label": "forward_2026",
        "evaluation_semantics": "single_run_holdout_v1",
        "artifact_schema_version": "phase2c_7_1",
        "engine_commit": "eb1c87f",
        "engine_corrected_lineage": "wf-corrected-v1",
        "current_git_sha": "deadbeef",
        "lineage_check": "passed",
        "execution_config_path": (
            f"config/{cost_yaml_path.name}"
        ),
        "execution_config_sha256": cost_sha,
        "forward_window_metadata": {
            "forward_window_start_utc": "2026-01-01T00:00:00Z",
            "forward_window_end_utc": "2026-04-16T07:00:00Z",
            "forward_bar_count": 2528,
            "parquet_data_sha256": parquet_sha,
        },
        "counts": {
            "total": 1, "holdout_passed": 0,
            "holdout_failed": 1, "holdout_error": 0,
        },
    }


def _base_csv_row() -> dict[str, Any]:
    return {
        "hypothesis_hash": "abcdef0123456789",
        "position": 0,
        "theme": "calendar_effect",
        "name": "synthetic_strat",
        "wf_test_period_sharpe": "0.500000",
        "lifecycle_state": "holdout_failed",
        "holdout_passed": "0",
        "holdout_sharpe": "0.250000",
        "holdout_max_drawdown": "-0.100000",
        "holdout_total_return": "0.050000",
        "holdout_total_trades": "10",
        "wall_clock_seconds": 1.5,
        "error_message": "",
    }


def _write_synthetic_run(
    output_root: Path,
    run_id: str,
    *,
    cost_yaml_path: Path,
    parquet_path: Path,
    summary_overrides: dict[str, Any] | None = None,
    fwm_overrides: dict[str, Any] | None = None,
    drop_fwm: bool = False,
    csv_rows: list[dict[str, Any]] | None = None,
) -> Path:
    """Fabricate holdout_summary.json + holdout_results.csv at output_root/run_id.

    summary_overrides: mutates top-level keys of summary
    fwm_overrides: mutates forward_window_metadata sub-block
    drop_fwm: if True, removes forward_window_metadata entirely
    csv_rows: list of row-dicts (defaults applied via _base_csv_row)
    """
    run_dir = output_root / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    summary = _build_summary_skeleton(cost_yaml_path, parquet_path)
    if drop_fwm:
        summary.pop("forward_window_metadata", None)
    elif fwm_overrides:
        summary["forward_window_metadata"].update(fwm_overrides)
    if summary_overrides:
        summary.update(summary_overrides)

    (run_dir / "holdout_summary.json").write_text(
        json.dumps(summary, indent=2)
    )

    if csv_rows is None:
        rows = [_base_csv_row()]
    else:
        base = _base_csv_row()
        rows = [{**base, **r} for r in csv_rows]

    csv_path = run_dir / "holdout_results.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=_CSV_FIELDS)
        writer.writeheader()
        for r in rows:
            writer.writerow({k: r.get(k, "") for k in _CSV_FIELDS})

    return run_dir


# ---------------------------------------------------------------------------
# Fixtures: skip if real Phase-4 artifacts (cost YAML + parquet) are missing
# (e.g., in a CI environment without the full data tree). Verifier needs both
# real files to compute expected sha256s.
# ---------------------------------------------------------------------------


@pytest.fixture
def cost_yaml_15bps() -> Path:
    p = PROJECT_ROOT / "config" / "execution_phase4_15bps.yaml"
    if not p.exists():
        pytest.skip(f"{p} not present (Phase 4 config required)")
    return p


@pytest.fixture
def parquet() -> Path:
    p = PROJECT_ROOT / "data" / "raw" / "btcusdt_1h.parquet"
    if not p.exists():
        pytest.skip(f"{p} not present (canonical parquet required)")
    return p


# ---------------------------------------------------------------------------
# 5 focused tests
# ---------------------------------------------------------------------------


def test_verifier_passes_on_synthetic_valid_artifact(
    tmp_path, cost_yaml_15bps, parquet, capsys
):
    output_root = tmp_path / "evaluation_gate"
    _write_synthetic_run(
        output_root,
        "phase4_smoke_15bps_test",
        cost_yaml_path=cost_yaml_15bps,
        parquet_path=parquet,
    )

    # No exception means PASS.
    verify(
        "phase4_smoke_15bps_test",
        cost_bps=15,
        expected_candidate_count=1,
        output_root=output_root,
        parquet_path=parquet,
    )

    captured = capsys.readouterr()
    assert "ALL 9 assertions PASS" in captured.out


def test_verifier_fails_on_sha256_mismatch(
    tmp_path, cost_yaml_15bps, parquet
):
    output_root = tmp_path / "evaluation_gate"
    _write_synthetic_run(
        output_root,
        "phase4_smoke_15bps_test",
        cost_yaml_path=cost_yaml_15bps,
        parquet_path=parquet,
        summary_overrides={"execution_config_sha256": "0" * 64},
    )

    with pytest.raises(VerificationFailure, match="execution_config_sha256"):
        verify(
            "phase4_smoke_15bps_test",
            cost_bps=15,
            output_root=output_root,
            parquet_path=parquet,
        )


def test_verifier_fails_on_missing_forward_window_metadata(
    tmp_path, cost_yaml_15bps, parquet
):
    output_root = tmp_path / "evaluation_gate"
    _write_synthetic_run(
        output_root,
        "phase4_smoke_15bps_test",
        cost_yaml_path=cost_yaml_15bps,
        parquet_path=parquet,
        drop_fwm=True,
    )

    with pytest.raises(VerificationFailure, match="forward_window_metadata"):
        verify(
            "phase4_smoke_15bps_test",
            cost_bps=15,
            output_root=output_root,
            parquet_path=parquet,
        )


def test_verifier_fails_on_wrong_regime_key(
    tmp_path, cost_yaml_15bps, parquet
):
    output_root = tmp_path / "evaluation_gate"
    _write_synthetic_run(
        output_root,
        "phase4_smoke_15bps_test",
        cost_yaml_path=cost_yaml_15bps,
        parquet_path=parquet,
        summary_overrides={"regime_key": "v2.regime_holdout"},
    )

    with pytest.raises(VerificationFailure, match="lineage anchors"):
        verify(
            "phase4_smoke_15bps_test",
            cost_bps=15,
            output_root=output_root,
            parquet_path=parquet,
        )


def test_verifier_fails_on_nonfinite_holdout_sharpe_with_passed_lifecycle(
    tmp_path, cost_yaml_15bps, parquet
):
    output_root = tmp_path / "evaluation_gate"
    _write_synthetic_run(
        output_root,
        "phase4_smoke_15bps_test",
        cost_yaml_path=cost_yaml_15bps,
        parquet_path=parquet,
        csv_rows=[{
            "lifecycle_state": "holdout_passed",
            "holdout_sharpe": "NaN",
        }],
    )

    with pytest.raises(VerificationFailure, match="holdout_results.csv"):
        verify(
            "phase4_smoke_15bps_test",
            cost_bps=15,
            output_root=output_root,
            parquet_path=parquet,
        )

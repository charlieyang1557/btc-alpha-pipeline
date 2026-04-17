"""D6 Stage 2d — 200-hypothesis sequential batch tests.

Covers:
    - Core orchestration (200 calls, lifecycle invariant, summaries)
    - Incremental checkpointing (partial JSON, atomic write, crash state)
    - Factor-set saturation aggregates
    - Block trends (4 blocks of 50)
    - Interim snapshots (at 50, 100, 150, 200)
    - Per-theme aggregates at N=40
    - Two-tier parse-rate catastrophic stops
    - Per-theme single-mode failure (36/40 threshold)
    - Cardinality violation (>10 threshold)
    - Cumulative $30 Stage-2 spend cap
    - Helper functions

All tests inject a mock backend and temp ledger/payload dirs.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from agents.orchestrator.budget_ledger import BudgetLedger
from agents.orchestrator.ingest import (
    BACKEND_EMPTY_OUTPUT,
    DUPLICATE,
    INVALID_DSL,
    PENDING_BACKTEST,
    REJECTED_COMPLEXITY,
)
from agents.proposer.interface import (
    BatchContext,
    InvalidCandidate,
    ProposerOutput,
    ValidCandidate,
)
from agents.proposer.stage2d_batch import (
    APPROVED_EXAMPLES_CAP,
    BLOCK_SIZE,
    CARDINALITY_VIOLATION_STOP,
    MODEL_NAME,
    PROMPT_CACHING_ENABLED,
    SINGLE_MODE_THRESHOLD,
    SNAPSHOT_POSITIONS,
    STAGE2D_BATCH_CAP_USD,
    STAGE2D_BATCH_SIZE,
    STAGE2D_CUMULATIVE_CAP_USD,
    STAGE_LABEL,
    THEME_CALLS_TOTAL,
    THEME_CYCLE_LEN,
    THEME_HINTS,
    THEME_ROTATION_MODE,
    TIER1_K,
    TIER1_THRESHOLD,
    TIER2_K,
    TIER2_THRESHOLD,
    VALID_STATUS_TRUNCATED,
    VALID_STATUS_VALID,
    _aggregate_per_theme,
    _atomic_write_json,
    _build_anomaly_log,
    _check_single_mode_failure,
    _classify_cardinality,
    _classify_error,
    _compute_block_trends,
    _compute_factor_set_saturation,
    _compute_interim_snapshot,
    _estimate_input_tokens,
    _extract_factors,
    _is_cardinality_violation,
    _theme_for_position,
    _valid_status_from_lifecycle,
    run_stage2d,
)
from agents.proposer.stub_backend import classify_raw_json
from agents.themes import THEMES
from factors.registry import get_registry


@pytest.fixture
def registry():
    return get_registry()


@pytest.fixture
def tmp_ledger(tmp_path):
    return tmp_path / "test_ledger.db"


@pytest.fixture
def tmp_payloads(tmp_path):
    return tmp_path / "payloads"


# ---------------------------------------------------------------------------
# Mock backends
# ---------------------------------------------------------------------------


class _VariedValidBackend:
    """Produces a unique valid DSL per call with themed factor."""

    _THEME_FACTOR = {
        "momentum": "return_24h",
        "mean_reversion": "zscore_48",
        "volatility_regime": "atr_14",
        "volume_divergence": "volume_zscore_24h",
        "calendar_effect": "day_of_week",
    }

    def __init__(self, registry):
        self._registry = registry
        self._n = 0

    def generate(self, context: BatchContext) -> ProposerOutput:
        self._n += 1
        theme = THEMES[(context.position - 1) % THEME_CYCLE_LEN]
        factor = self._THEME_FACTOR.get(theme, "return_24h")
        dsl_dict = {
            "name": f"s_{self._n}",
            "description": f"Variant {self._n} on {factor}.",
            "entry": [{"conditions": [
                {"factor": factor, "op": ">",
                 "value": round(0.01 * self._n, 4)}
            ]}],
            "exit": [{"conditions": [
                {"factor": factor, "op": "<", "value": 0.0}
            ]}],
            "position_sizing": "full_equity",
            "max_hold_bars": None,
        }
        raw_json = json.dumps(dsl_dict)
        cand = classify_raw_json(raw_json, registry=self._registry)
        return ProposerOutput(
            candidates=(cand,),
            cost_estimate_usd=0.01,
            cost_actual_usd=0.01,
            backend_name="test_varied",
            telemetry={"input_tokens": 500, "output_tokens": 100},
        )


class _AllInvalidSchemaBackend:
    """Emits an InvalidCandidate with a fixed schema error."""

    def __init__(self, parse_error: str = "missing required field 'name'"):
        self._err = parse_error

    def generate(self, context: BatchContext) -> ProposerOutput:
        cand = InvalidCandidate(
            raw_json="{}",
            parse_error=self._err,
            error_kind="schema",
            provenance={"validation_errors": [
                {"type": "missing", "loc": ("name",), "msg": self._err}
            ]},
        )
        return ProposerOutput(
            candidates=(cand,),
            cost_estimate_usd=0.01,
            cost_actual_usd=0.01,
            backend_name="test_all_invalid",
            telemetry={"input_tokens": 500, "output_tokens": 50},
        )


class _MixedBackend:
    """Valid on most calls; invalid every Nth call (default every 5th)."""

    def __init__(self, registry, *, fail_every: int = 5):
        self._registry = registry
        self._fail_every = fail_every
        self._n = 0

    def generate(self, context: BatchContext) -> ProposerOutput:
        self._n += 1
        if self._n % self._fail_every == 0:
            cand = InvalidCandidate(
                raw_json='{"bad": true}',
                parse_error="missing required field 'name'",
                error_kind="schema",
            )
        else:
            dsl_dict = {
                "name": f"s_{self._n}",
                "description": f"Strategy {self._n}.",
                "entry": [{"conditions": [
                    {"factor": "return_24h", "op": ">",
                     "value": round(0.01 * self._n, 4)}
                ]}],
                "exit": [{"conditions": [
                    {"factor": "return_24h", "op": "<", "value": 0.0}
                ]}],
                "position_sizing": "full_equity",
                "max_hold_bars": None,
            }
            cand = classify_raw_json(
                json.dumps(dsl_dict), registry=self._registry)
        return ProposerOutput(
            candidates=(cand,),
            cost_estimate_usd=0.01,
            cost_actual_usd=0.01,
            backend_name="test_mixed",
            telemetry={"input_tokens": 500, "output_tokens": 100},
        )


class _CardinalityViolationBackend:
    """Writes a JSON array to response file; candidate is invalid."""

    def __init__(self, payload_dir: Path):
        self._payload_dir = payload_dir
        self._n = 0

    def generate(self, context: BatchContext) -> ProposerOutput:
        self._n += 1
        batch_dir = self._payload_dir / f"batch_{context.batch_id}"
        batch_dir.mkdir(parents=True, exist_ok=True)
        resp = batch_dir / f"attempt_{context.position:04d}_response.txt"
        resp.write_text('[{"foo":1},{"bar":2}]', encoding="utf-8")
        cand = InvalidCandidate(
            raw_json='[{"foo":1},{"bar":2}]',
            parse_error="expected object, got list",
            error_kind="schema",
        )
        return ProposerOutput(
            candidates=(cand,),
            cost_estimate_usd=0.01,
            cost_actual_usd=0.01,
            backend_name="test_card_viol",
            telemetry={"input_tokens": 500, "output_tokens": 50},
        )


# ---------------------------------------------------------------------------
# Chunk 9 — Core orchestration tests
# ---------------------------------------------------------------------------


def test_runs_200_calls_to_completion(registry, tmp_ledger, tmp_payloads):
    summary = run_stage2d(
        dry_run=True,
        _backend=_VariedValidBackend(registry),
        _ledger_path=tmp_ledger,
        _payload_dir=tmp_payloads,
    )
    assert summary["hypotheses_attempted"] == STAGE2D_BATCH_SIZE
    assert summary["unissued_slots"] == 0
    assert summary["truncated"] is False
    assert summary["early_stop_reason"] is None
    assert summary["batch_status"] == "completed"
    assert summary["lifecycle_invariant_ok"] is True
    assert len(summary["calls"]) == STAGE2D_BATCH_SIZE


def test_lifecycle_invariant_at_close(registry, tmp_ledger, tmp_payloads):
    summary = run_stage2d(
        dry_run=True,
        _backend=_VariedValidBackend(registry),
        _ledger_path=tmp_ledger,
        _payload_dir=tmp_payloads,
    )
    total = sum(summary["lifecycle_counts"].values())
    assert total == summary["hypotheses_attempted"]


def test_summary_json_and_partial_exist(registry, tmp_ledger, tmp_payloads):
    summary = run_stage2d(
        dry_run=True,
        _backend=_VariedValidBackend(registry),
        _ledger_path=tmp_ledger,
        _payload_dir=tmp_payloads,
    )
    batch_dir = tmp_payloads / f"batch_{summary['batch_id']}"
    full = batch_dir / "stage2d_summary.json"
    partial = batch_dir / "stage2d_summary_partial.json"
    assert full.exists()
    assert partial.exists()
    loaded_full = json.loads(full.read_text())
    loaded_partial = json.loads(partial.read_text())
    assert loaded_full["batch_id"] == summary["batch_id"]
    assert loaded_partial["batch_status"] == "completed"
    assert "config" in loaded_full
    assert "per_theme" in loaded_full
    assert "block_trends" in loaded_full
    assert "interim_snapshots" in loaded_full


def test_theme_rotation_40_per_theme(registry, tmp_ledger, tmp_payloads):
    summary = run_stage2d(
        dry_run=True,
        _backend=_VariedValidBackend(registry),
        _ledger_path=tmp_ledger,
        _payload_dir=tmp_payloads,
    )
    theme_counts: dict[str, int] = {}
    for c in summary["calls"]:
        theme_counts[c["theme"]] = theme_counts.get(c["theme"], 0) + 1
    for t in THEMES[:THEME_CYCLE_LEN]:
        assert theme_counts[t] == THEME_CALLS_TOTAL
    assert "multi_factor_combination" not in theme_counts


def test_approved_examples_cap(registry, tmp_ledger, tmp_payloads):
    summary = run_stage2d(
        dry_run=True,
        _backend=_VariedValidBackend(registry),
        _ledger_path=tmp_ledger,
        _payload_dir=tmp_payloads,
    )
    for c in summary["calls"]:
        n = c.get("approved_examples_count_in_prompt_before_call")
        if n is not None:
            assert n <= APPROVED_EXAMPLES_CAP


def test_batch_duration_positive(registry, tmp_ledger, tmp_payloads):
    summary = run_stage2d(
        dry_run=True,
        _backend=_VariedValidBackend(registry),
        _ledger_path=tmp_ledger,
        _payload_dir=tmp_payloads,
    )
    assert summary["batch_duration_seconds"] > 0
    assert summary["config"]["batch_duration_seconds"] > 0


# ---------------------------------------------------------------------------
# Chunk 10 — Telemetry, saturation, config, per-theme
# ---------------------------------------------------------------------------


def test_per_call_telemetry_fields(registry, tmp_ledger, tmp_payloads):
    summary = run_stage2d(
        dry_run=True,
        _backend=_VariedValidBackend(registry),
        _ledger_path=tmp_ledger,
        _payload_dir=tmp_payloads,
    )
    required = {
        "factors_used", "overlap_count", "overlap_ratio",
        "out_of_theme_factor_count", "contains_default_momentum_factor",
        "default_momentum_factors_used",
        "approved_example_names_before_call",
        "approved_example_logic_notes", "valid_status",
    }
    for c in summary["calls"]:
        missing = required - set(c.keys())
        assert not missing, f"call {c['position']} missing: {missing}"


def test_config_block(registry, tmp_ledger, tmp_payloads):
    summary = run_stage2d(
        dry_run=True,
        _backend=_VariedValidBackend(registry),
        _ledger_path=tmp_ledger,
        _payload_dir=tmp_payloads,
    )
    cfg = summary["config"]
    assert cfg["stage_label"] == STAGE_LABEL
    assert cfg["model_name"] == MODEL_NAME
    assert cfg["prompt_caching_enabled"] is False
    assert cfg["batch_size"] == STAGE2D_BATCH_SIZE
    assert cfg["batch_cap_usd"] == STAGE2D_BATCH_CAP_USD
    assert cfg["parse_rate_gate_k5_threshold"] == TIER1_THRESHOLD
    assert cfg["parse_rate_gate_k20_threshold"] == TIER2_THRESHOLD
    assert cfg["batch_status"] == "completed"
    assert isinstance(cfg["git_commit"], str)


def test_per_theme_n40(registry, tmp_ledger, tmp_payloads):
    summary = run_stage2d(
        dry_run=True,
        _backend=_VariedValidBackend(registry),
        _ledger_path=tmp_ledger,
        _payload_dir=tmp_payloads,
    )
    for row in summary["per_theme"]:
        assert row["n_calls"] == THEME_CALLS_TOTAL


def test_factor_set_saturation_fields(registry, tmp_ledger, tmp_payloads):
    summary = run_stage2d(
        dry_run=True,
        _backend=_VariedValidBackend(registry),
        _ledger_path=tmp_ledger,
        _payload_dir=tmp_payloads,
    )
    assert "total_valid_count" in summary
    assert "distinct_hash_count" in summary
    assert "distinct_factor_set_count" in summary
    assert "unique_factor_set_ratio" in summary
    assert "repeated_factor_sets" in summary
    assert "valid_with_empty_factor_set_count" in summary
    assert "valid_with_empty_factor_set_calls" in summary
    assert summary["total_valid_count"] == STAGE2D_BATCH_SIZE
    assert summary["valid_with_empty_factor_set_count"] == 0


def test_factor_set_saturation_unit():
    """Direct unit test of _compute_factor_set_saturation."""
    calls = [
        {"position": 1, "lifecycle_state": PENDING_BACKTEST,
         "truncated_by_cap": False, "hypothesis_hash": "h1",
         "factors_used": ["a", "b"], "theme": "momentum"},
        {"position": 2, "lifecycle_state": PENDING_BACKTEST,
         "truncated_by_cap": False, "hypothesis_hash": "h2",
         "factors_used": ["a", "b"], "theme": "momentum"},
        {"position": 3, "lifecycle_state": PENDING_BACKTEST,
         "truncated_by_cap": False, "hypothesis_hash": "h3",
         "factors_used": ["c"], "theme": "momentum"},
        {"position": 4, "lifecycle_state": INVALID_DSL,
         "truncated_by_cap": False, "hypothesis_hash": None,
         "factors_used": [], "theme": "momentum"},
    ]
    sat = _compute_factor_set_saturation(calls)
    assert sat["total_valid_count"] == 3
    assert sat["distinct_hash_count"] == 3
    assert sat["distinct_factor_set_count"] == 2  # {a,b} and {c}
    assert sat["unique_factor_set_ratio"] == round(2 / 3, 4)
    assert len(sat["repeated_factor_sets"]) == 1
    rep = sat["repeated_factor_sets"][0]
    assert rep["factor_set"] == ["a", "b"]
    assert rep["occurrence_count"] == 2
    assert rep["distinct_hashes_within_factor_set"] == 2


def test_empty_factor_set_excluded_from_saturation():
    calls = [
        {"position": 1, "lifecycle_state": PENDING_BACKTEST,
         "truncated_by_cap": False, "hypothesis_hash": "h1",
         "factors_used": [], "theme": "momentum"},
        {"position": 2, "lifecycle_state": PENDING_BACKTEST,
         "truncated_by_cap": False, "hypothesis_hash": "h2",
         "factors_used": ["a"], "theme": "momentum"},
    ]
    sat = _compute_factor_set_saturation(calls)
    assert sat["valid_with_empty_factor_set_count"] == 1
    assert sat["valid_with_empty_factor_set_calls"] == [1]
    assert sat["distinct_factor_set_count"] == 1
    assert sat["unique_factor_set_ratio"] == 1.0


def test_block_trends_shape(registry, tmp_ledger, tmp_payloads):
    summary = run_stage2d(
        dry_run=True,
        _backend=_VariedValidBackend(registry),
        _ledger_path=tmp_ledger,
        _payload_dir=tmp_payloads,
    )
    bt = summary["block_trends"]
    assert len(bt) == 4
    for b in bt:
        assert b["complete"] is True
        assert b["call_count"] == BLOCK_SIZE
        assert b["valid_rate"] is not None


def test_interim_snapshots_at_completion(registry, tmp_ledger, tmp_payloads):
    summary = run_stage2d(
        dry_run=True,
        _backend=_VariedValidBackend(registry),
        _ledger_path=tmp_ledger,
        _payload_dir=tmp_payloads,
    )
    snaps = summary["interim_snapshots"]
    assert len(snaps) == len(SNAPSHOT_POSITIONS)
    for snap, expected_k in zip(snaps, SNAPSHOT_POSITIONS):
        assert snap["at_call"] == expected_k
        assert "cumulative_valid_count" in snap
        assert "cumulative_distinct_hash_count" in snap
        assert "cumulative_unique_factor_set_ratio" in snap
        assert "cumulative_actual_cost_usd" in snap
        assert "avg_input_tokens_since_last_snapshot" in snap


def test_interim_snapshot_recomputable(registry, tmp_ledger, tmp_payloads):
    """Interim snapshot counts MUST be recomputable from per-call state."""
    summary = run_stage2d(
        dry_run=True,
        _backend=_VariedValidBackend(registry),
        _ledger_path=tmp_ledger,
        _payload_dir=tmp_payloads,
    )
    calls = summary["calls"]
    for snap in summary["interim_snapshots"]:
        k = snap["at_call"]
        prefix = [c for c in calls[:k] if not c.get("truncated_by_cap")]
        valid = [c for c in prefix
                 if c.get("lifecycle_state") == PENDING_BACKTEST]
        assert snap["cumulative_valid_count"] == len(valid)
        hashes = {c.get("hypothesis_hash") for c in valid
                  if c.get("hypothesis_hash")}
        assert snap["cumulative_distinct_hash_count"] == len(hashes)


# ---------------------------------------------------------------------------
# Chunk 11 — Catastrophic stop tests
# ---------------------------------------------------------------------------


def test_tier1_early_stop_at_k5(registry, tmp_ledger, tmp_payloads):
    """All-invalid → parse_rate=0 < 0.50; tier-1 fires at k=5."""
    summary = run_stage2d(
        dry_run=True,
        _backend=_AllInvalidSchemaBackend(),
        _ledger_path=tmp_ledger,
        _payload_dir=tmp_payloads,
    )
    assert summary["early_stop_reason"] == "tier1_parse_rate_below_threshold"
    detail = summary["early_stop_detail"]
    assert detail["at_call"] == TIER1_K
    assert detail["parse_rate"] == 0.0
    assert summary["hypotheses_attempted"] == TIER1_K
    # Partial should exist with crash status
    batch_dir = tmp_payloads / f"batch_{summary['batch_id']}"
    partial = json.loads(
        (batch_dir / "stage2d_summary_partial.json").read_text()
    )
    assert partial["batch_status"].startswith("crashed_at_call_")


def test_tier2_early_stop_at_k20(registry, tmp_ledger, tmp_payloads):
    """Mixed backend with fail_every=4 → 15/20 valid = 75% → tier-2
    fires (threshold is <=0.75)."""
    backend = _MixedBackend(registry, fail_every=4)
    summary = run_stage2d(
        dry_run=True,
        _backend=backend,
        _ledger_path=tmp_ledger,
        _payload_dir=tmp_payloads,
    )
    assert summary["early_stop_reason"] == "tier2_parse_rate_at_or_below_threshold"
    detail = summary["early_stop_detail"]
    assert detail["at_call"] == TIER2_K
    assert detail["parse_rate"] <= TIER2_THRESHOLD


def test_tier2_not_triggered_above_threshold(registry, tmp_ledger, tmp_payloads):
    """All-valid backend → 100% rate → tier-2 does NOT fire."""
    summary = run_stage2d(
        dry_run=True,
        _backend=_VariedValidBackend(registry),
        _ledger_path=tmp_ledger,
        _payload_dir=tmp_payloads,
    )
    assert summary["early_stop_reason"] is None
    assert summary["hypotheses_attempted"] == STAGE2D_BATCH_SIZE


def test_single_mode_failure_unit_36_of_40():
    """_check_single_mode_failure fires when ≥36/40 share same signature."""
    calls = []
    for k in range(1, 201):
        theme = _theme_for_position(k)
        if theme == "momentum":
            calls.append({
                "position": k, "theme": "momentum",
                "truncated_by_cap": False,
                "lifecycle_state": INVALID_DSL,
                "error_info": {
                    "error_category": "json_parse",
                    "error_signature": "malformed_json",
                },
            })
    # We have 40 momentum calls, all invalid with same sig.
    assert len([c for c in calls if c["theme"] == "momentum"]) == 40
    triggered, cat, sig = _check_single_mode_failure(calls, "momentum")
    assert triggered is True
    assert cat == "json_parse"
    assert sig == "malformed_json"


def test_single_mode_not_triggered_below_36():
    """35/40 same error + 5 valid → does not trigger."""
    calls = []
    count = 0
    for k in range(1, 201):
        theme = _theme_for_position(k)
        if theme == "momentum":
            count += 1
            if count <= 35:
                calls.append({
                    "position": k, "theme": "momentum",
                    "truncated_by_cap": False,
                    "lifecycle_state": INVALID_DSL,
                    "error_info": {
                        "error_category": "json_parse",
                        "error_signature": "malformed_json",
                    },
                })
            else:
                calls.append({
                    "position": k, "theme": "momentum",
                    "truncated_by_cap": False,
                    "lifecycle_state": PENDING_BACKTEST,
                    "error_info": None,
                })
    triggered, _, _ = _check_single_mode_failure(calls, "momentum")
    assert triggered is False


def test_cardinality_violation_stop(registry, tmp_ledger, tmp_payloads):
    """Cardinality violation backend → stop fires when count > 10.
    However, tier-1 at k=5 (all invalid) fires first."""
    backend = _CardinalityViolationBackend(tmp_payloads)
    summary = run_stage2d(
        dry_run=True,
        _backend=backend,
        _ledger_path=tmp_ledger,
        _payload_dir=tmp_payloads,
    )
    assert summary["early_stop_reason"] is not None
    assert summary["cardinality_violation_count"] >= 1


def test_cumulative_spend_stop(registry, tmp_ledger, tmp_payloads):
    """Seed ledger to $29.99; first call trips cumulative $30 cap."""
    ledger = BudgetLedger(tmp_ledger)
    row_id = ledger.write_pending(
        batch_id="seed", api_call_kind="proposer",
        estimated_cost_usd=29.99,
        now=datetime.now(timezone.utc),
    )
    ledger.finalize(row_id, actual_cost_usd=29.99,
                    now=datetime.now(timezone.utc))
    summary = run_stage2d(
        dry_run=True,
        _backend=_VariedValidBackend(registry),
        _ledger_path=tmp_ledger,
        _payload_dir=tmp_payloads,
    )
    assert summary["early_stop_reason"] == "cumulative_stage2_spend_exceeded"
    assert summary["early_stop_detail"]["at_call"] == 1


def test_truncated_slots_have_correct_status(
    registry, tmp_ledger, tmp_payloads,
):
    summary = run_stage2d(
        dry_run=True,
        _backend=_AllInvalidSchemaBackend(),
        _ledger_path=tmp_ledger,
        _payload_dir=tmp_payloads,
    )
    truncated = [c for c in summary["calls"] if c["truncated_by_cap"]]
    assert len(truncated) > 0
    for c in truncated:
        assert c["valid_status"] == VALID_STATUS_TRUNCATED
        assert c["lifecycle_state"] is None


# ---------------------------------------------------------------------------
# Chunk 12 — Checkpoint, block trends, helpers
# ---------------------------------------------------------------------------


def test_atomic_write_json(tmp_path):
    """_atomic_write_json writes valid JSON via rename."""
    p = tmp_path / "test.json"
    _atomic_write_json(p, {"key": "value"})
    assert p.exists()
    loaded = json.loads(p.read_text())
    assert loaded["key"] == "value"
    # No leftover .tmp
    assert not p.with_suffix(".json.tmp").exists()


def test_partial_checkpoint_updated_per_call(
    registry, tmp_ledger, tmp_payloads,
):
    """After full batch, partial should contain all calls."""
    summary = run_stage2d(
        dry_run=True,
        _backend=_VariedValidBackend(registry),
        _ledger_path=tmp_ledger,
        _payload_dir=tmp_payloads,
    )
    batch_dir = tmp_payloads / f"batch_{summary['batch_id']}"
    partial = json.loads(
        (batch_dir / "stage2d_summary_partial.json").read_text()
    )
    assert partial["batch_status"] == "completed"
    assert len(partial["calls"]) == STAGE2D_BATCH_SIZE


def test_block_trends_unit():
    calls = []
    for i in range(1, 201):
        calls.append({
            "position": i, "truncated_by_cap": False,
            "lifecycle_state": PENDING_BACKTEST,
            "input_tokens": 1000, "output_tokens": 200,
            "actual_cost_usd": 0.01,
            "factors_used": ["a", "b"] if i % 2 == 0 else ["c"],
        })
    bt = _compute_block_trends(calls)
    assert len(bt) == 4
    for b in bt:
        assert b["complete"] is True
        assert b["call_count"] == 50
        assert b["valid_count"] == 50
        assert b["valid_rate"] == 1.0
        assert b["input_tokens_mean"] == 1000
        assert b["actual_cost_total"] == 0.5


def test_block_trends_incomplete_block():
    """Partial block (e.g., batch stopped at call 30)."""
    calls = []
    for i in range(1, 31):
        calls.append({
            "position": i, "truncated_by_cap": False,
            "lifecycle_state": PENDING_BACKTEST,
            "input_tokens": 1000, "output_tokens": 200,
            "actual_cost_usd": 0.01,
            "factors_used": ["a"],
        })
    for i in range(31, 201):
        calls.append({
            "position": i, "truncated_by_cap": True,
            "lifecycle_state": None,
            "input_tokens": None, "output_tokens": None,
            "actual_cost_usd": None,
            "factors_used": [],
        })
    bt = _compute_block_trends(calls)
    assert bt[0]["complete"] is False
    assert bt[0]["call_count"] == 30
    assert bt[1]["call_count"] == 0


def test_interim_snapshot_unit():
    calls = []
    for i in range(1, 51):
        calls.append({
            "position": i, "truncated_by_cap": False,
            "lifecycle_state": PENDING_BACKTEST,
            "hypothesis_hash": f"h{i}",
            "factors_used": ["a"] if i % 2 == 0 else ["b"],
            "input_tokens": 1000, "output_tokens": 200,
            "actual_cost_usd": 0.01,
        })
    snap = _compute_interim_snapshot(calls, 50, 0)
    assert snap["at_call"] == 50
    assert snap["cumulative_valid_count"] == 50
    assert snap["cumulative_distinct_hash_count"] == 50
    assert snap["cumulative_distinct_factor_set_count"] == 2
    assert snap["cumulative_unique_factor_set_ratio"] == round(2 / 50, 4)
    assert snap["cumulative_actual_cost_usd"] == 0.5


def test_theme_for_position_200():
    counts: dict[str, int] = {}
    for k in range(1, 201):
        t = _theme_for_position(k)
        counts[t] = counts.get(t, 0) + 1
    assert all(v == 40 for v in counts.values())
    assert len(counts) == 5
    assert "multi_factor_combination" not in counts


def test_anomaly_log_hash_duplication():
    """Hash duplication anomaly fires when distinct < total."""
    sat = {
        "total_valid_count": 10,
        "distinct_hash_count": 8,
        "valid_with_empty_factor_set_count": 0,
        "valid_with_empty_factor_set_calls": [],
        "repeated_factor_sets": [],
    }
    calls = [
        {"position": i, "lifecycle_state": PENDING_BACKTEST,
         "truncated_by_cap": False, "hypothesis_hash": f"h{i % 8}",
         "factors_used": ["a"]}
        for i in range(10)
    ]
    flags = _build_anomaly_log(calls, sat, [], [])
    kinds = [f["kind"] for f in flags]
    assert "hash_duplication" in kinds


def test_anomaly_log_repeated_factor_set_high():
    sat = {
        "total_valid_count": 50,
        "distinct_hash_count": 50,
        "valid_with_empty_factor_set_count": 0,
        "valid_with_empty_factor_set_calls": [],
        "repeated_factor_sets": [
            {"factor_set": ["a", "b"], "occurrence_count": 12,
             "distinct_hashes_within_factor_set": 12,
             "occurring_at_calls": list(range(12)),
             "themes_used_in": ["momentum"] * 12},
        ],
    }
    flags = _build_anomaly_log([], sat, [], [])
    kinds = [f["kind"] for f in flags]
    assert "repeated_factor_set_high" in kinds


def test_constants():
    assert STAGE2D_BATCH_SIZE == 200
    assert STAGE2D_BATCH_CAP_USD == 20.0
    assert TIER1_K == 5
    assert TIER1_THRESHOLD == 0.50
    assert TIER2_K == 20
    assert TIER2_THRESHOLD == 0.75
    assert SINGLE_MODE_THRESHOLD == 36
    assert THEME_CALLS_TOTAL == 40
    assert CARDINALITY_VIOLATION_STOP == 10
    assert BLOCK_SIZE == 50
    assert SNAPSHOT_POSITIONS == (50, 100, 150, 200)

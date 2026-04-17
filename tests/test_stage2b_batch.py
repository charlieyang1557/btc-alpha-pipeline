"""D6 Stage 2b — sequential batch loop tests.

Tests the stage2b orchestration without live API calls, using the stub
backend and a test-only mock backend that produces distinct valid DSLs.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from agents.orchestrator.budget_ledger import BudgetLedger
from agents.orchestrator.ingest import PENDING_BACKTEST
from agents.proposer.interface import (
    BatchContext,
    ProposerOutput,
    ValidCandidate,
)
from agents.proposer.stage2b_batch import (
    APPROVED_EXAMPLES_CAP,
    STAGE2B_BATCH_SIZE,
    _classify_cardinality,
    _classify_theme_adherence,
    _estimate_input_tokens,
    _extract_factors,
    run_stage2b,
)
from agents.proposer.stub_backend import classify_raw_json
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
# Mock backend that produces distinct valid DSLs (avoids duplicate lifecycle)
# ---------------------------------------------------------------------------


class _VariedValidBackend:
    """Produces a unique valid DSL per call (never duplicates)."""

    def __init__(self, registry):
        self._registry = registry
        self._call_count = 0

    def generate(self, context: BatchContext) -> ProposerOutput:
        self._call_count += 1
        dsl_dict = {
            "name": f"test_strategy_{self._call_count}",
            "description": f"Variant {self._call_count}: "
            f"enter on return_24h > {0.01 * self._call_count:.2f}.",
            "entry": [
                {
                    "conditions": [
                        {
                            "factor": "return_24h",
                            "op": ">",
                            "value": round(0.01 * self._call_count, 4),
                        }
                    ]
                }
            ],
            "exit": [
                {
                    "conditions": [
                        {"factor": "return_24h", "op": "<", "value": 0.0}
                    ]
                }
            ],
            "position_sizing": "full_equity",
            "max_hold_bars": None,
        }
        raw_json = json.dumps(dsl_dict)
        candidate = classify_raw_json(raw_json, registry=self._registry)
        return ProposerOutput(
            candidates=(candidate,),
            cost_estimate_usd=0.01,
            cost_actual_usd=0.01,
            backend_name="test_varied",
            telemetry={"input_tokens": 500, "output_tokens": 100},
        )


class _AllFailBackend:
    """Always returns empty output (backend_empty_output lifecycle)."""

    def generate(self, context: BatchContext) -> ProposerOutput:
        return ProposerOutput(
            candidates=(),
            cost_estimate_usd=0.0,
            cost_actual_usd=0.0,
            backend_name="test_fail",
            telemetry={"error": "forced_empty"},
        )


# ---------------------------------------------------------------------------
# Sequential approved_examples accumulation
# ---------------------------------------------------------------------------


def test_approved_examples_accumulate_correctly(
    registry, tmp_ledger, tmp_payloads,
):
    """Each valid call should add one entry to approved_so_far. The
    count-in-prompt should reflect the accumulation from prior calls."""
    backend = _VariedValidBackend(registry)
    summary = run_stage2b(
        dry_run=True,
        _backend=backend,
        _ledger_path=tmp_ledger,
        _payload_dir=tmp_payloads,
    )

    calls = summary["calls"]
    assert len(calls) == STAGE2B_BATCH_SIZE

    expected_counts = [0, 1, 2, 3, 3]
    for i, call in enumerate(calls):
        actual = call["approved_examples_count_in_prompt_before_call"]
        assert actual == expected_counts[i], (
            f"Call {i + 1}: expected {expected_counts[i]} examples, "
            f"got {actual}"
        )


def test_approved_examples_cap_at_3(registry, tmp_ledger, tmp_payloads):
    """Even with 5 valid calls, the cap stays at 3."""
    backend = _VariedValidBackend(registry)
    summary = run_stage2b(
        dry_run=True,
        _backend=backend,
        _ledger_path=tmp_ledger,
        _payload_dir=tmp_payloads,
    )

    for call in summary["calls"]:
        assert (
            call["approved_examples_count_in_prompt_before_call"]
            <= APPROVED_EXAMPLES_CAP
        )


def test_approved_examples_empty_when_all_fail(
    registry, tmp_ledger, tmp_payloads,
):
    """If all calls fail, approved_examples stays empty throughout."""
    backend = _AllFailBackend()
    summary = run_stage2b(
        dry_run=True,
        _backend=backend,
        _ledger_path=tmp_ledger,
        _payload_dir=tmp_payloads,
    )

    for call in summary["calls"]:
        assert call["approved_examples_count_in_prompt_before_call"] == 0


def test_only_pending_backtest_appended(registry, tmp_ledger, tmp_payloads):
    """Stub backend: only the first 'valid' call produces pending_backtest;
    others (invalid_json, duplicate, etc.) must NOT add to approved_so_far."""
    summary = run_stage2b(
        dry_run=True,
        _ledger_path=tmp_ledger,
        _payload_dir=tmp_payloads,
    )

    calls = summary["calls"]
    pb_count = sum(1 for c in calls
                   if c["lifecycle_state"] == PENDING_BACKTEST)
    assert pb_count == 1
    assert calls[0]["lifecycle_state"] == PENDING_BACKTEST
    for c in calls[1:]:
        assert c["approved_examples_count_in_prompt_before_call"] <= 1


# ---------------------------------------------------------------------------
# Lifecycle invariant
# ---------------------------------------------------------------------------


def test_lifecycle_invariant_holds(registry, tmp_ledger, tmp_payloads):
    summary = run_stage2b(
        dry_run=True,
        _ledger_path=tmp_ledger,
        _payload_dir=tmp_payloads,
    )
    assert summary["lifecycle_invariant_ok"]
    total_lc = sum(summary["lifecycle_counts"].values())
    assert total_lc == summary["hypotheses_attempted"]


def test_all_five_calls_attempted(registry, tmp_ledger, tmp_payloads):
    summary = run_stage2b(
        dry_run=True,
        _ledger_path=tmp_ledger,
        _payload_dir=tmp_payloads,
    )
    assert summary["hypotheses_attempted"] == STAGE2B_BATCH_SIZE
    assert summary["unissued_slots"] == 0
    assert not summary["truncated"]


# ---------------------------------------------------------------------------
# Budget cap truncation
# ---------------------------------------------------------------------------


def test_budget_cap_truncation(registry, tmp_ledger, tmp_payloads):
    """With an extremely tight batch cap, at least one call should
    be truncated. Truncated calls must NOT count as attempted."""
    backend = _VariedValidBackend(registry)

    # Monkey-patch the batch cap to something tiny
    import agents.proposer.stage2b_batch as mod
    orig_cap = mod.STAGE2B_BATCH_CAP_USD
    mod.STAGE2B_BATCH_CAP_USD = 0.015
    try:
        summary = run_stage2b(
            dry_run=True,
            _backend=backend,
            _ledger_path=tmp_ledger,
            _payload_dir=tmp_payloads,
        )
    finally:
        mod.STAGE2B_BATCH_CAP_USD = orig_cap

    assert summary["truncated"]
    truncated = [c for c in summary["calls"] if c["truncated_by_cap"]]
    attempted = [c for c in summary["calls"] if not c["truncated_by_cap"]]
    assert len(truncated) > 0
    assert summary["hypotheses_attempted"] == len(attempted)
    assert summary["unissued_slots"] == len(truncated)

    for t in truncated:
        assert t["lifecycle_state"] is None
        assert t["hypothesis_hash"] is None


# ---------------------------------------------------------------------------
# Summary JSON artifact
# ---------------------------------------------------------------------------


def test_summary_json_written_and_parseable(
    registry, tmp_ledger, tmp_payloads,
):
    summary = run_stage2b(
        dry_run=True,
        _ledger_path=tmp_ledger,
        _payload_dir=tmp_payloads,
    )

    batch_id = summary["batch_id"]
    summary_path = (
        tmp_payloads / f"batch_{batch_id}" / "stage2b_summary.json"
    )
    assert summary_path.exists()

    loaded = json.loads(summary_path.read_text(encoding="utf-8"))
    assert loaded["batch_id"] == batch_id
    assert loaded["hypotheses_attempted"] == summary["hypotheses_attempted"]
    assert loaded["lifecycle_invariant_ok"] is True
    assert "calls" in loaded
    assert len(loaded["calls"]) == STAGE2B_BATCH_SIZE


# ---------------------------------------------------------------------------
# Pre-flight pending entry cleanup
# ---------------------------------------------------------------------------


def test_pre_flight_clears_stale_pending(registry, tmp_ledger, tmp_payloads):
    """Stale pending entries from prior batches must be marked crashed
    before the batch starts."""
    ledger = BudgetLedger(tmp_ledger)
    stale_id = ledger.write_pending(
        batch_id="stale-batch",
        api_call_kind="proposer",
        estimated_cost_usd=0.05,
    )
    assert len(ledger.pending_entries()) == 1

    summary = run_stage2b(
        dry_run=True,
        _ledger_path=tmp_ledger,
        _payload_dir=tmp_payloads,
    )

    ledger2 = BudgetLedger(tmp_ledger)
    assert len(ledger2.pending_entries()) == 0
    entries = ledger2.list_entries(batch_id="stale-batch")
    assert entries[0].status == "crashed"


# ---------------------------------------------------------------------------
# Helper function tests
# ---------------------------------------------------------------------------


def test_estimate_input_tokens():
    assert _estimate_input_tokens("x" * 2900) == 1000
    assert _estimate_input_tokens("x" * 100) == 500  # floor


def test_classify_cardinality():
    assert _classify_cardinality('{"a": 1}') == "single_object"
    assert _classify_cardinality('[{"a": 1}, {"b": 2}]') == "json_array_2"
    assert _classify_cardinality("") == "zero_objects"
    assert _classify_cardinality("   ") == "zero_objects"
    assert _classify_cardinality("Here is json: {bad") == "prose_plus_object"
    assert _classify_cardinality('```json\n{"a":1}\n```') == "single_object"


def test_classify_theme_adherence(registry):
    from strategies.dsl import StrategyDSL

    dsl = StrategyDSL.model_validate(
        {
            "name": "momentum_test",
            "description": "Uses return_24h only.",
            "entry": [
                {
                    "conditions": [
                        {"factor": "return_24h", "op": ">", "value": 0.02}
                    ]
                }
            ],
            "exit": [
                {
                    "conditions": [
                        {"factor": "return_24h", "op": "<", "value": 0.0}
                    ]
                }
            ],
            "position_sizing": "full_equity",
            "max_hold_bars": None,
        },
        context={"registry": registry},
    )
    assert _classify_theme_adherence(dsl, "momentum") == "Yes"
    assert _classify_theme_adherence(dsl, "volume_divergence") == "No"


def test_extract_factors(registry):
    from strategies.dsl import StrategyDSL

    dsl = StrategyDSL.model_validate(
        {
            "name": "multi_factor",
            "description": "Uses rsi_14 and return_24h.",
            "entry": [
                {
                    "conditions": [
                        {"factor": "rsi_14", "op": ">", "value": 30},
                        {"factor": "return_24h", "op": ">", "value": 0.01},
                    ]
                }
            ],
            "exit": [
                {
                    "conditions": [
                        {"factor": "rsi_14", "op": "<", "value": 70}
                    ]
                }
            ],
            "position_sizing": "full_equity",
            "max_hold_bars": None,
        },
        context={"registry": registry},
    )
    factors = _extract_factors(dsl)
    assert factors == {"rsi_14", "return_24h"}

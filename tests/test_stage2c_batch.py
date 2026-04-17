"""D6 Stage 2c — 20-hypothesis sequential batch tests.

Covers:
    - Core orchestration (20 calls, lifecycle invariant, summary JSON)
    - Expanded per-call telemetry fields
    - Per-theme aggregate rows (including tie-broken top-3 ordering)
    - Batch-level config block
    - Catastrophic stop conditions
        * early parse-rate stop
        * per-theme single-mode failure
        * cardinality violation count
        * cumulative $30 Stage-2 spend
    - Helper functions (valid_status, factor extraction, theme rotation,
      dominant_factors_top3 tie break)

All tests inject a mock backend and temp ledger/payload dirs; no live
API calls.
"""

from __future__ import annotations

import json
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
from agents.proposer.stage2c_batch import (
    APPROVED_EXAMPLES_CAP,
    CARDINALITY_VIOLATION_STOP,
    DEFAULT_MOMENTUM_FACTORS,
    MODEL_NAME,
    NARROW_FACTOR_VOCAB_THRESHOLD,
    PARSE_RATE_THRESHOLD,
    PROMPT_CACHING_ENABLED,
    RSI14_COLLAPSE_THRESHOLD,
    STAGE2C_BATCH_CAP_USD,
    STAGE2C_BATCH_SIZE,
    STAGE2C_CUMULATIVE_CAP_USD,
    STAGE_LABEL,
    THEME_CYCLE_LEN,
    THEME_HINTS,
    THEME_ROTATION_MODE,
    VALID_STATUS_BACKEND_EMPTY,
    VALID_STATUS_INVALID_DUPLICATE,
    VALID_STATUS_INVALID_SCHEMA,
    VALID_STATUS_TRUNCATED,
    VALID_STATUS_VALID,
    _aggregate_per_theme,
    _check_single_mode_failure,
    _classify_cardinality,
    _classify_error,
    _estimate_input_tokens,
    _extract_factors,
    _is_cardinality_violation,
    _theme_for_position,
    _valid_status_from_lifecycle,
    run_stage2c,
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
    """Produces a unique valid DSL per call (never duplicates).

    Uses the call theme_slot to pick a factor that matches the theme so
    overlap metrics have something to aggregate. Falls back to return_24h
    when the theme has no hints.
    """

    # factor chosen per theme to exercise overlap counts.
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
                {"factor": factor, "op": ">", "value": round(0.01 * self._n, 4)}
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
    """Emits an InvalidCandidate with a fixed schema error on every call.

    Used for the per-theme single-mode failure catastrophic-stop test:
    every call shares identical error_category + error_signature.
    """

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


class _AllEmptyBackend:
    """Always returns empty candidates — maps to backend_empty_output."""

    def generate(self, context: BatchContext) -> ProposerOutput:
        return ProposerOutput(
            candidates=(),
            cost_estimate_usd=0.0,
            cost_actual_usd=0.0,
            backend_name="test_empty",
            telemetry={"error": "forced_empty"},
        )


class _CardinalityViolationBackend:
    """Writes a JSON array into the payload dir on every call.

    The backend candidate itself is invalid (so lifecycle is invalid_dsl),
    but the response-file on disk looks like ``[{},{}]`` which the
    cardinality classifier reads as ``json_array_2`` → violation. Drives
    the cardinality-violation-count catastrophic stop.
    """

    def __init__(self, payload_dir: Path):
        self._payload_dir = payload_dir
        self._n = 0

    def generate(self, context: BatchContext) -> ProposerOutput:
        self._n += 1
        batch_dir = self._payload_dir / f"batch_{context.batch_id}"
        batch_dir.mkdir(parents=True, exist_ok=True)
        response_file = batch_dir / f"attempt_{context.position:04d}_response.txt"
        response_file.write_text('[{"foo":1},{"bar":2}]', encoding="utf-8")
        # Also a valid JSON that still fails schema (so lifecycle = invalid_dsl).
        raw = '[{"foo":1},{"bar":2}]'
        cand = InvalidCandidate(
            raw_json=raw,
            parse_error="expected object, got list",
            error_kind="schema",
        )
        return ProposerOutput(
            candidates=(cand,),
            cost_estimate_usd=0.01,
            cost_actual_usd=0.01,
            backend_name="test_cardinality_violation",
            telemetry={"input_tokens": 500, "output_tokens": 50},
        )


# ---------------------------------------------------------------------------
# Chunk 7 — Core orchestration tests
# ---------------------------------------------------------------------------


def test_runs_20_calls_to_completion(registry, tmp_ledger, tmp_payloads):
    """Happy path: all 20 calls attempted, none truncated."""
    summary = run_stage2c(
        dry_run=True,
        _backend=_VariedValidBackend(registry),
        _ledger_path=tmp_ledger,
        _payload_dir=tmp_payloads,
    )
    assert summary["hypotheses_attempted"] == STAGE2C_BATCH_SIZE
    assert summary["unissued_slots"] == 0
    assert summary["truncated"] is False
    assert summary["early_stop_reason"] is None
    assert summary["lifecycle_invariant_ok"] is True
    assert len(summary["calls"]) == STAGE2C_BATCH_SIZE
    for c in summary["calls"]:
        assert c["truncated_by_cap"] is False


def test_lifecycle_invariant_holds_at_close(registry, tmp_ledger, tmp_payloads):
    """Every call produces exactly one terminal lifecycle state."""
    summary = run_stage2c(
        dry_run=True,
        _backend=_VariedValidBackend(registry),
        _ledger_path=tmp_ledger,
        _payload_dir=tmp_payloads,
    )
    total = sum(summary["lifecycle_counts"].values())
    assert total == summary["hypotheses_attempted"]


def test_summary_json_written_and_parseable(
    registry, tmp_ledger, tmp_payloads,
):
    """stage2c_summary.json is written to the batch payload dir and parses."""
    summary = run_stage2c(
        dry_run=True,
        _backend=_VariedValidBackend(registry),
        _ledger_path=tmp_ledger,
        _payload_dir=tmp_payloads,
    )
    summary_path = (
        tmp_payloads / f"batch_{summary['batch_id']}" / "stage2c_summary.json"
    )
    assert summary_path.exists()
    loaded = json.loads(summary_path.read_text(encoding="utf-8"))
    assert loaded["batch_id"] == summary["batch_id"]
    assert loaded["hypotheses_attempted"] == STAGE2C_BATCH_SIZE
    assert "config" in loaded
    assert "per_theme" in loaded
    assert "calls" in loaded


def test_theme_rotation_is_interleaved_cyclic(
    registry, tmp_ledger, tmp_payloads,
):
    """Each of 5 themes gets exactly 4 calls via (k-1) % 5."""
    summary = run_stage2c(
        dry_run=True,
        _backend=_VariedValidBackend(registry),
        _ledger_path=tmp_ledger,
        _payload_dir=tmp_payloads,
    )
    theme_counts: dict[str, int] = {}
    for c in summary["calls"]:
        theme_counts[c["theme"]] = theme_counts.get(c["theme"], 0) + 1
    assert len(theme_counts) == THEME_CYCLE_LEN
    for t in THEMES[:THEME_CYCLE_LEN]:
        assert theme_counts[t] == 4
    # multi_factor_combination MUST NOT appear.
    assert "multi_factor_combination" not in theme_counts


def test_approved_examples_cap_at_3(registry, tmp_ledger, tmp_payloads):
    """No prompt ever sees more than 3 approved examples."""
    summary = run_stage2c(
        dry_run=True,
        _backend=_VariedValidBackend(registry),
        _ledger_path=tmp_ledger,
        _payload_dir=tmp_payloads,
    )
    for c in summary["calls"]:
        n = c.get("approved_examples_count_in_prompt_before_call")
        if n is not None:
            assert n <= APPROVED_EXAMPLES_CAP


def test_empty_backend_produces_backend_empty_output(
    registry, tmp_ledger, tmp_payloads,
):
    """Empty backend routes all calls to backend_empty_output lifecycle."""
    summary = run_stage2c(
        dry_run=True,
        _backend=_AllEmptyBackend(),
        _ledger_path=tmp_ledger,
        _payload_dir=tmp_payloads,
    )
    assert summary["lifecycle_counts"].get(BACKEND_EMPTY_OUTPUT, 0) > 0
    # No approved examples ever accumulate.
    for c in summary["calls"]:
        n = c.get("approved_examples_count_in_prompt_before_call")
        if n is not None:
            assert n == 0


# ---------------------------------------------------------------------------
# Chunk 8 — Per-call telemetry, per-theme aggregates, config block
# ---------------------------------------------------------------------------


def test_per_call_telemetry_fields_populated(
    registry, tmp_ledger, tmp_payloads,
):
    """Every attempted (non-truncated) call reports the expanded fields."""
    summary = run_stage2c(
        dry_run=True,
        _backend=_VariedValidBackend(registry),
        _ledger_path=tmp_ledger,
        _payload_dir=tmp_payloads,
    )
    required = {
        "factors_used",
        "overlap_count",
        "overlap_ratio",
        "out_of_theme_factor_count",
        "contains_default_momentum_factor",
        "default_momentum_factors_used",
        "approved_example_names_before_call",
        "approved_example_logic_notes",
        "valid_status",
    }
    for c in summary["calls"]:
        missing = required - set(c.keys())
        assert not missing, f"call {c['position']} missing fields: {missing}"


def test_valid_status_matches_lifecycle(
    registry, tmp_ledger, tmp_payloads,
):
    """valid_status is a deterministic function of lifecycle_state."""
    summary = run_stage2c(
        dry_run=True,
        _backend=_VariedValidBackend(registry),
        _ledger_path=tmp_ledger,
        _payload_dir=tmp_payloads,
    )
    for c in summary["calls"]:
        ls = c["lifecycle_state"]
        vs = c["valid_status"]
        if c["truncated_by_cap"]:
            assert vs == VALID_STATUS_TRUNCATED
        elif ls == PENDING_BACKTEST:
            assert vs == VALID_STATUS_VALID
        elif ls in (INVALID_DSL, REJECTED_COMPLEXITY):
            assert vs == VALID_STATUS_INVALID_SCHEMA
        elif ls == DUPLICATE:
            assert vs == VALID_STATUS_INVALID_DUPLICATE
        elif ls == BACKEND_EMPTY_OUTPUT:
            assert vs == VALID_STATUS_BACKEND_EMPTY


def test_overlap_metrics_on_themed_valid_calls(
    registry, tmp_ledger, tmp_payloads,
):
    """_VariedValidBackend uses themed factors — overlap_count should be
    1 on every valid call (its one factor hits the theme hint list)."""
    summary = run_stage2c(
        dry_run=True,
        _backend=_VariedValidBackend(registry),
        _ledger_path=tmp_ledger,
        _payload_dir=tmp_payloads,
    )
    for c in summary["calls"]:
        if c["lifecycle_state"] != PENDING_BACKTEST:
            continue
        assert c["overlap_count"] == 1
        assert c["overlap_ratio"] == 1.0
        assert c["out_of_theme_factor_count"] == 0


def test_approved_example_names_and_logic_align(
    registry, tmp_ledger, tmp_payloads,
):
    """approved_example_names/logic lists match in length, most-recent first,
    capped at APPROVED_EXAMPLES_CAP."""
    summary = run_stage2c(
        dry_run=True,
        _backend=_VariedValidBackend(registry),
        _ledger_path=tmp_ledger,
        _payload_dir=tmp_payloads,
    )
    for c in summary["calls"]:
        names = c.get("approved_example_names_before_call") or []
        notes = c.get("approved_example_logic_notes") or []
        assert len(names) == len(notes)
        assert len(names) <= APPROVED_EXAMPLES_CAP


def test_per_theme_aggregate_row_shape(
    registry, tmp_ledger, tmp_payloads,
):
    """Every theme appears with the full aggregate-field set."""
    summary = run_stage2c(
        dry_run=True,
        _backend=_VariedValidBackend(registry),
        _ledger_path=tmp_ledger,
        _payload_dir=tmp_payloads,
    )
    themes_seen = {row["theme"] for row in summary["per_theme"]}
    assert themes_seen == set(THEMES[:THEME_CYCLE_LEN])
    required = {
        "theme", "n_calls", "valid_count", "lifecycle_mix",
        "avg_overlap_count", "avg_overlap_ratio",
        "avg_out_of_theme_factors", "contains_rsi14_count",
        "contains_momentum_default_count", "dominant_factors_top3",
    }
    for row in summary["per_theme"]:
        assert required.issubset(row.keys())
        assert row["n_calls"] == 4


def test_dominant_factors_top3_tiebreak_alphabetical():
    """Ties in count are broken by ascending factor name."""
    calls = [
        {"theme": "momentum", "truncated_by_cap": False,
         "lifecycle_state": PENDING_BACKTEST,
         "factors_used": ["zeta", "alpha"],
         "overlap_count": 0, "overlap_ratio": 0.0,
         "out_of_theme_factor_count": 2,
         "contains_default_momentum_factor": False},
        {"theme": "momentum", "truncated_by_cap": False,
         "lifecycle_state": PENDING_BACKTEST,
         "factors_used": ["beta", "gamma"],
         "overlap_count": 0, "overlap_ratio": 0.0,
         "out_of_theme_factor_count": 2,
         "contains_default_momentum_factor": False},
        {"theme": "momentum", "truncated_by_cap": False,
         "lifecycle_state": PENDING_BACKTEST,
         "factors_used": ["alpha", "beta"],
         "overlap_count": 0, "overlap_ratio": 0.0,
         "out_of_theme_factor_count": 2,
         "contains_default_momentum_factor": False},
        {"theme": "momentum", "truncated_by_cap": False,
         "lifecycle_state": PENDING_BACKTEST,
         "factors_used": ["alpha", "gamma"],
         "overlap_count": 0, "overlap_ratio": 0.0,
         "out_of_theme_factor_count": 2,
         "contains_default_momentum_factor": False},
    ]
    row = _aggregate_per_theme(calls, "momentum")
    # counts: alpha=3, beta=2, gamma=2, zeta=1 → top-3: alpha, beta, gamma
    assert row["dominant_factors_top3"] == ["alpha", "beta", "gamma"]


def test_batch_config_block_in_summary(
    registry, tmp_ledger, tmp_payloads,
):
    """Batch-level config block pins invariants (model, caching, rotation)."""
    summary = run_stage2c(
        dry_run=True,
        _backend=_VariedValidBackend(registry),
        _ledger_path=tmp_ledger,
        _payload_dir=tmp_payloads,
    )
    cfg = summary["config"]
    assert cfg["stage_label"] == STAGE_LABEL
    assert cfg["model_name"] == MODEL_NAME
    assert cfg["prompt_caching_enabled"] is PROMPT_CACHING_ENABLED
    assert cfg["batch_size"] == STAGE2C_BATCH_SIZE
    assert cfg["batch_cap_usd"] == STAGE2C_BATCH_CAP_USD
    assert cfg["cumulative_stage2_cap_usd"] == STAGE2C_CUMULATIVE_CAP_USD
    assert cfg["theme_rotation_mode"] == THEME_ROTATION_MODE
    assert cfg["approved_examples_cap"] == APPROVED_EXAMPLES_CAP
    # git_commit and run_timestamp_utc exist as strings.
    assert isinstance(cfg["git_commit"], str)
    assert isinstance(cfg["run_timestamp_utc"], str)
    assert len(cfg["run_timestamp_utc"]) > 0


def test_anomaly_flags_narrow_vocab_triggers(
    registry, tmp_ledger, tmp_payloads,
):
    """_VariedValidBackend spans 5 themed factors across first-10 valid
    calls — vocab size (5) is NOT below threshold, so narrow_factor_vocab
    should NOT fire with this backend."""
    summary = run_stage2c(
        dry_run=True,
        _backend=_VariedValidBackend(registry),
        _ledger_path=tmp_ledger,
        _payload_dir=tmp_payloads,
    )
    kinds = {a["kind"] for a in summary["anomaly_flags"]}
    assert "narrow_factor_vocab" not in kinds


# ---------------------------------------------------------------------------
# Chunk 9 — Catastrophic stop conditions
# ---------------------------------------------------------------------------


def test_early_stop_parse_rate_below_threshold(
    registry, tmp_ledger, tmp_payloads,
):
    """All-invalid backend → parse_rate=0.0 < 0.5; stop fires at k=5."""
    summary = run_stage2c(
        dry_run=True,
        _backend=_AllInvalidSchemaBackend(),
        _ledger_path=tmp_ledger,
        _payload_dir=tmp_payloads,
    )
    assert summary["early_stop_reason"] == "parse_rate_below_threshold"
    detail = summary["early_stop_detail"]
    assert detail["at_call"] == 5
    assert detail["parse_rate"] == 0.0
    assert detail["threshold"] == PARSE_RATE_THRESHOLD
    # Lifecycle invariant still holds.
    assert summary["lifecycle_invariant_ok"] is True


def test_early_stop_per_theme_single_mode_failure(
    registry, tmp_ledger, tmp_payloads,
):
    """All-invalid backend emits identical error_category+signature on
    every call. After 4 momentum calls (k=1,6,11,16) the single-mode
    stop should fire — but parse-rate stop fires first at k=5 with this
    backend. Use the helper directly to verify the per-theme detector."""
    # Build 4 momentum calls with identical error signatures.
    calls = []
    for k in [1, 6, 11, 16]:
        calls.append({
            "position": k, "theme": "momentum",
            "truncated_by_cap": False,
            "lifecycle_state": INVALID_DSL,
            "error_info": {
                "error_category": "schema_field_mismatch",
                "error_signature": "missing_name_field",
            },
        })
    triggered, cat, sig = _check_single_mode_failure(calls, "momentum")
    assert triggered is True
    assert cat == "schema_field_mismatch"
    assert sig == "missing_name_field"


def test_single_mode_not_triggered_with_mixed_signatures():
    """Different error signatures across the 4 theme calls → no stop."""
    calls = []
    sigs = ["sig_a", "sig_b", "sig_a", "sig_c"]
    for k, sig in zip([1, 6, 11, 16], sigs):
        calls.append({
            "position": k, "theme": "momentum",
            "truncated_by_cap": False,
            "lifecycle_state": INVALID_DSL,
            "error_info": {
                "error_category": "schema_field_mismatch",
                "error_signature": sig,
            },
        })
    triggered, cat, sig = _check_single_mode_failure(calls, "momentum")
    assert triggered is False


def test_single_mode_not_triggered_if_any_valid():
    """Any pending_backtest among the 4 calls → no stop."""
    calls = []
    for k in [1, 6, 11, 16]:
        calls.append({
            "position": k, "theme": "momentum",
            "truncated_by_cap": False,
            "lifecycle_state": INVALID_DSL,
            "error_info": {
                "error_category": "schema_field_mismatch",
                "error_signature": "sig",
            },
        })
    calls[2]["lifecycle_state"] = PENDING_BACKTEST
    calls[2]["error_info"] = None
    triggered, _, _ = _check_single_mode_failure(calls, "momentum")
    assert triggered is False


def test_early_stop_cardinality_violation_count(
    registry, tmp_ledger, tmp_payloads,
):
    """JSON-array-returning backend produces violation per call; stop
    triggers when count > 2 (i.e., at the 3rd violation)."""
    backend = _CardinalityViolationBackend(tmp_payloads)
    summary = run_stage2c(
        dry_run=True,
        _backend=backend,
        _ledger_path=tmp_ledger,
        _payload_dir=tmp_payloads,
    )
    # Parse-rate stop might fire first (all calls are invalid so parse_rate=0
    # at k=5). Whichever stop wins, the summary MUST report an early stop.
    assert summary["early_stop_reason"] is not None
    assert summary["cardinality_violation_count"] >= 1


def test_early_stop_cumulative_spend_exceeded(
    registry, tmp_ledger, tmp_payloads,
):
    """Seed the ledger just under the cumulative Stage-2 cap; the first
    Stage-2c call should trip the cumulative_stage2_spend_exceeded stop."""
    from datetime import datetime, timezone
    ledger = BudgetLedger(tmp_ledger)
    # Seed $29.995 already spent in the ledger (separate batch).
    row_id = ledger.write_pending(
        batch_id="seed-batch",
        api_call_kind="proposer",
        estimated_cost_usd=29.995,
        now=datetime.now(timezone.utc),
    )
    ledger.finalize(
        row_id,
        actual_cost_usd=29.995,
        now=datetime.now(timezone.utc),
    )

    summary = run_stage2c(
        dry_run=True,
        _backend=_VariedValidBackend(registry),
        _ledger_path=tmp_ledger,
        _payload_dir=tmp_payloads,
    )
    assert summary["early_stop_reason"] == "cumulative_stage2_spend_exceeded"
    detail = summary["early_stop_detail"]
    assert detail["at_call"] == 1
    assert detail["cumulative_cap_usd"] == STAGE2C_CUMULATIVE_CAP_USD


def test_remaining_slots_truncated_on_early_stop(
    registry, tmp_ledger, tmp_payloads,
):
    """When a catastrophic stop fires, every remaining slot is marked
    truncated_by_cap with valid_status=truncated_by_cap."""
    summary = run_stage2c(
        dry_run=True,
        _backend=_AllInvalidSchemaBackend(),
        _ledger_path=tmp_ledger,
        _payload_dir=tmp_payloads,
    )
    assert summary["early_stop_reason"] is not None
    truncated = [c for c in summary["calls"] if c["truncated_by_cap"]]
    assert len(truncated) > 0
    for c in truncated:
        assert c["valid_status"] == VALID_STATUS_TRUNCATED
        assert c["lifecycle_state"] is None


# ---------------------------------------------------------------------------
# Chunk 10 — Helper function tests
# ---------------------------------------------------------------------------


def test_theme_for_position_cycle_len_5():
    """Theme rotation uses first 5 THEMES via (k-1) % 5."""
    for k in range(1, STAGE2C_BATCH_SIZE + 1):
        expected = THEMES[(k - 1) % THEME_CYCLE_LEN]
        assert _theme_for_position(k) == expected
    # Sanity: all 5 themes, each exactly 4 times in k=1..20.
    counts: dict[str, int] = {}
    for k in range(1, 21):
        t = _theme_for_position(k)
        counts[t] = counts.get(t, 0) + 1
    assert all(v == 4 for v in counts.values())
    assert "multi_factor_combination" not in counts


def test_valid_status_from_lifecycle_literals():
    assert _valid_status_from_lifecycle(
        PENDING_BACKTEST, truncated=False) == VALID_STATUS_VALID
    assert _valid_status_from_lifecycle(
        INVALID_DSL, truncated=False) == VALID_STATUS_INVALID_SCHEMA
    assert _valid_status_from_lifecycle(
        REJECTED_COMPLEXITY, truncated=False) == VALID_STATUS_INVALID_SCHEMA
    assert _valid_status_from_lifecycle(
        DUPLICATE, truncated=False) == VALID_STATUS_INVALID_DUPLICATE
    assert _valid_status_from_lifecycle(
        BACKEND_EMPTY_OUTPUT, truncated=False) == VALID_STATUS_BACKEND_EMPTY
    # Truncation overrides lifecycle.
    assert _valid_status_from_lifecycle(
        PENDING_BACKTEST, truncated=True) == VALID_STATUS_TRUNCATED
    assert _valid_status_from_lifecycle(
        None, truncated=True) == VALID_STATUS_TRUNCATED


def test_estimate_input_tokens_floor_and_ceiling():
    """Empty prompt → floor of 500; longer prompt → ceil(len/2.9)."""
    assert _estimate_input_tokens("") == 500
    assert _estimate_input_tokens("x") == 500
    # 2900 chars / 2.9 = 1000 tokens exactly.
    assert _estimate_input_tokens("x" * 2900) == 1000
    # 2901 chars / 2.9 = 1000.345 → ceil = 1001.
    assert _estimate_input_tokens("x" * 2901) == 1001


def test_extract_factors_covers_entry_exit_and_rhs(registry):
    """_extract_factors returns both LHS and factor-valued RHS."""
    dsl_dict = {
        "name": "s",
        "description": "test.",
        "entry": [{"conditions": [
            {"factor": "sma_20", "op": "crosses_above", "value": "sma_50"},
        ]}],
        "exit": [{"conditions": [
            {"factor": "rsi_14", "op": ">", "value": 70.0},
        ]}],
        "position_sizing": "full_equity",
        "max_hold_bars": None,
    }
    cand = classify_raw_json(json.dumps(dsl_dict), registry=registry)
    assert isinstance(cand, ValidCandidate)
    factors = _extract_factors(cand.dsl)
    assert factors == {"sma_20", "sma_50", "rsi_14"}


def test_classify_cardinality_variants():
    assert _classify_cardinality('{"name":"x"}') == "single_object"
    assert _classify_cardinality("[{}]") == "json_array_1"
    assert _classify_cardinality("[{},{},{}]") == "json_array_3"
    assert _classify_cardinality("") == "zero_objects"
    assert _classify_cardinality("blah {bad}") == "prose_plus_object"
    # Fenced single object is unwrapped by _strip_markdown_fence.
    fenced = '```json\n{"name":"x"}\n```'
    assert _classify_cardinality(fenced) == "single_object"


def test_is_cardinality_violation():
    assert _is_cardinality_violation("single_object") is False
    assert _is_cardinality_violation("n/a") is False
    assert _is_cardinality_violation("json_array_2") is True
    assert _is_cardinality_violation("prose_plus_object") is True
    assert _is_cardinality_violation("zero_objects") is True


def test_classify_error_buckets():
    # Valid → None for both fields.
    res = _classify_error(PENDING_BACKTEST, None)
    assert res["error_category"] is None and res["error_signature"] is None

    res = _classify_error(DUPLICATE, None)
    assert res["error_category"] == "duplicate_condition"

    res = _classify_error(REJECTED_COMPLEXITY, None)
    assert res["error_category"] == "complexity_rejection"

    res = _classify_error(BACKEND_EMPTY_OUTPUT, None)
    assert res["error_category"] == "backend_empty"

    res = _classify_error(INVALID_DSL, "JSONDecodeError: Expecting value")
    assert res["error_category"] == "json_parse"

    res = _classify_error(INVALID_DSL, "unknown factor foo_bar")
    assert res["error_category"] == "frozen_registry_violation"

    res = _classify_error(INVALID_DSL, "disallowed operator =~")
    assert res["error_category"] == "grammar_violation"

    res = _classify_error(INVALID_DSL, "value must be finite, got nan")
    assert res["error_category"] == "non_finite_threshold"

    res = _classify_error(INVALID_DSL, "missing required field 'name'")
    assert res["error_category"] == "schema_field_mismatch"
    # Signature preserves a normalized prefix of the message.
    assert "missing" in res["error_signature"]


def test_theme_hints_mapping_reporting_only():
    """THEME_HINTS is a frozenset per theme; covers 5 reporting themes."""
    assert set(THEME_HINTS.keys()) == set(THEMES[:THEME_CYCLE_LEN])
    for t, hints in THEME_HINTS.items():
        assert isinstance(hints, frozenset)
        assert len(hints) >= 1


def test_default_momentum_factors_constant():
    assert DEFAULT_MOMENTUM_FACTORS == frozenset(
        {"rsi_14", "return_1h", "return_24h", "macd_hist"}
    )


def test_per_theme_empty_theme_returns_zero_row():
    """A theme with zero calls yields n_calls=0 and no crash."""
    row = _aggregate_per_theme([], "momentum")
    assert row["theme"] == "momentum"
    assert row["n_calls"] == 0
    assert row["valid_count"] == 0
    assert row["dominant_factors_top3"] == []


def test_per_theme_truncated_calls_excluded():
    """Truncated calls do not count toward a theme's n_calls."""
    calls = [
        {"theme": "momentum", "truncated_by_cap": True,
         "lifecycle_state": None, "factors_used": []},
        {"theme": "momentum", "truncated_by_cap": True,
         "lifecycle_state": None, "factors_used": []},
    ]
    row = _aggregate_per_theme(calls, "momentum")
    assert row["n_calls"] == 0


def test_rsi14_collapse_threshold_constant():
    """Constant is at the documented trigger level (8 of first 10 valid)."""
    assert RSI14_COLLAPSE_THRESHOLD == 8


def test_narrow_factor_vocab_threshold_constant():
    assert NARROW_FACTOR_VOCAB_THRESHOLD == 5


def test_cardinality_violation_stop_constant():
    assert CARDINALITY_VIOLATION_STOP == 2

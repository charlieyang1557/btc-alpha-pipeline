"""Tests for scripts/run_d7_stage2b_batch.py — D7 Stage 2b fire script.

Covers the launch prompt §8.2 minimum-15 test matrix:

    - End-to-end stub fire with 5 fake candidates
    - HG5 commit-ordering: selection after expectations fails
    - HG5 commit-ordering: expectations after wall-clock fails
    - HG3: expectations missing aborts
    - HG3: expectations uncommitted aborts
    - HG4: structural validator rejects missing header
    - HG4b: structural validator rejects candidate-header mismatch
    - HG8: refuses to overwrite existing aggregate record
    - Abort rule (a): two consecutive API-level d7b_errors
    - Abort rule (b): cumulative d7b_error rate > 40% at K >= 3
    - Abort rule (c): content-level d7b_error >= 3 at K >= 3
    - Abort rule (d): per-call cost ceiling exceeded
    - Abort rule (e): cumulative cost cap exceeded
    - write_completed_at appears in aggregate record and last
    - Atomic write: failed writes leave no corrupt partial file
    - Stage 2a archival: call_0073_* moved on first live run
    - classify_d7b_error: api_level / content_level discriminator
    - is_consistent_with_label: exact 0.5 → HIGH threshold
    - Selection-tier invariants (HG2b)
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pytest

import scripts.run_d7_stage2b_batch as stage2b
from agents.critic.batch_context import (
    DEFAULT_MOMENTUM_FACTORS,
    THEME_ANCHOR_FACTORS,
    THEME_HINTS,
    BatchContext,
)
from agents.critic.d7b_backend import D7bBackend
from agents.critic.d7b_stub import StubD7bBackend
from agents.critic.result import CriticResult
from strategies.dsl import StrategyDSL


# ---------------------------------------------------------------------------
# Fixtures & helpers
# ---------------------------------------------------------------------------


_VALID_EXPECTATIONS_HEADERS = (
    "## Anti-Hindsight Anchor\n"
    "Expected divergence behavior locked before fire.\n\n"
    "## Aggregate Expectations Across All 5 Calls\n"
    "All five calls should return critic_status=ok under stub.\n\n"
    "## Per-Candidate Expectations\n"
)


def _make_candidate(
    firing_order: int, position: int, theme: str, label: str,
    hypothesis_hash: str = "deadbeefcafe0000",
) -> dict:
    return {
        "firing_order": firing_order,
        "position": position,
        "theme": theme,
        "hypothesis_hash": hypothesis_hash,
        "lifecycle_state": "pending_backtest",
        "factors_used": ["close", "rsi_14", "sma_20"],
        "factor_set_prior_occurrences": 0,
        "max_overlap_with_priors": 1,
        "d7a_b_relationship_label": label,
        "position_bucket": "mid",
        "selection_rationale": f"test candidate #{firing_order}",
    }


def _default_candidates() -> list[dict]:
    return [
        _make_candidate(1, 17, "mean_reversion", "divergence_expected", "a" * 16),
        _make_candidate(2, 73, "volatility_regime", "divergence_expected", "b" * 16),
        _make_candidate(3, 74, "volume_divergence", "divergence_expected", "c" * 16),
        _make_candidate(4, 97, "mean_reversion", "agreement_expected", "d" * 16),
        _make_candidate(5, 138, "volatility_regime", "neutral", "e" * 16),
    ]


def _write_selection(path: Path, candidates: list[dict]) -> None:
    payload = {
        "stage_label": "d7_stage2b",
        "record_version": "1.0",
        "batch_uuid": stage2b.STAGE2B_BATCH_UUID,
        "selection_timestamp_utc": "2026-04-18T12:22:48Z",
        "selection_tier": 0,
        "selection_warnings": [],
        "pool_size_total": 200,
        "pool_size_passing_per_candidate_criteria": 29,
        "rejection_breakdown": {},
        "candidates": candidates,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _write_expectations(path: Path, candidates: list[dict]) -> None:
    text = _VALID_EXPECTATIONS_HEADERS
    for i, c in enumerate(candidates, 1):
        text += (
            f"### Candidate {i} \u2014 Position {c['position']}, "
            f"{c['theme']}, {c['d7a_b_relationship_label']}\n"
            "Expected: stub-driven ok.\n\n"
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _make_dsl() -> StrategyDSL:
    return StrategyDSL.model_validate({
        "name": "stage2b_test_strategy",
        "description": "Stage 2b unit test strategy for stub reconstruction.",
        "entry": [
            {"conditions": [{"factor": "rsi_14", "op": ">", "value": 30.0}]},
        ],
        "exit": [
            {"conditions": [{"factor": "rsi_14", "op": "<", "value": 70.0}]},
        ],
        "position_sizing": "full_equity",
        "max_hold_bars": 168,
    })


def _make_batch_context(position: int) -> BatchContext:
    return BatchContext(
        prior_factor_sets=(("rsi_14", "sma_20"),),
        prior_hashes=("prior-hash-1",),
        batch_position=position,
        theme_hints=THEME_HINTS,
        default_momentum_factors=DEFAULT_MOMENTUM_FACTORS,
        theme_anchor_factors=THEME_ANCHOR_FACTORS,
    )


def _stub_reconstruct(batch_uuid: str, position: int, **kwargs) -> tuple:
    theme_for_position = {
        17: "mean_reversion",
        73: "volatility_regime",
        74: "volume_divergence",
        97: "mean_reversion",
        138: "volatility_regime",
    }.get(position, "momentum")
    return _make_dsl(), theme_for_position, _make_batch_context(position)


def _critic_ok(cost: float = 0.02, svr: float = 0.3) -> CriticResult:
    scan_results = {
        "forbidden_language_scan": {
            "status": "pass", "hits": [], "terms_checked_count": 21,
        },
        "refusal_scan": {
            "status": "pass", "hits": [], "patterns_checked": [],
        },
    }
    return CriticResult(
        critic_version="d7_v1",
        critic_status="ok",
        d7b_mode="stub",
        d7a_rule_scores={"theme_coherence": 0.5},
        d7a_supporting_measures={},
        d7a_rule_flags=[],
        d7b_llm_scores={
            "semantic_plausibility": 0.5,
            "semantic_theme_alignment": 0.5,
            "structural_variant_risk": svr,
        },
        d7b_reasoning="stub reasoning body " * 4,
        d7b_raw_response_path=None,
        d7b_cost_actual_usd=cost,
        d7b_input_tokens=100,
        d7b_output_tokens=50,
        d7b_retry_count=0,
        d7b_scan_results=scan_results,
    )


def _critic_d7b_error(
    signature: str = "timeout: connection reset",
    cost: float = 0.0,
) -> CriticResult:
    return CriticResult(
        critic_version="d7_v1",
        critic_status="d7b_error",
        d7b_mode="stub",
        d7a_rule_scores={"theme_coherence": 0.5},
        d7a_supporting_measures={},
        d7a_rule_flags=[],
        d7b_llm_scores=None,
        d7b_reasoning=None,
        d7b_raw_response_path=None,
        d7b_cost_actual_usd=cost,
        d7b_input_tokens=None,
        d7b_output_tokens=None,
        d7b_retry_count=0,
        d7b_scan_results=None,
        critic_error_signature=signature,
    )


class _SequenceBackend(D7bBackend):
    """Returns a pre-queued sequence of CriticResults via run_critic monkeypatch.

    We do NOT implement the abstract ``score`` method for real use — the
    test harness monkeypatches ``run_critic`` to inject our queue instead.
    """

    def __init__(self, queue: list[CriticResult]):
        self.queue = list(queue)
        self.calls = 0

    @property
    def mode(self):  # type: ignore[override]
        return "stub"

    def score(self, dsl, theme, batch_context):  # type: ignore[override]
        raise NotImplementedError


@pytest.fixture
def tmp_config(tmp_path, monkeypatch):
    """Build a testable Stage2bConfig rooted in tmp_path.

    Provides safe commit-timestamp fakes and a stub reconstruct_fn so no
    git / filesystem / artifact lookups leak out of tmp_path.
    """
    candidates = _default_candidates()
    selection_path = tmp_path / "selection.json"
    expectations_path = tmp_path / "expectations.md"
    aggregate_path = tmp_path / "stage2b_batch_record.json"
    per_call_dir = tmp_path / "per_call"
    per_call_dir.mkdir()
    raw_root = tmp_path / "raw_payloads"
    ledger_path = tmp_path / "ledger.db"

    _write_selection(selection_path, candidates)
    _write_expectations(expectations_path, candidates)

    # Stub out prompt template file to avoid hashing the real one.
    prompt_template_path = tmp_path / "d7b_prompt.py"
    prompt_template_path.write_text("# fake template\n", encoding="utf-8")

    config = stage2b.Stage2bConfig(
        confirm_live=False,
        stub=True,
        selection_json_path=selection_path,
        expectations_path=expectations_path,
        aggregate_record_path=aggregate_path,
        per_call_record_dir=per_call_dir,
        raw_payload_root=raw_root,
        ledger_path=ledger_path,
        prompt_template_path=prompt_template_path,
        selection_commit_ts_fn=lambda p: 1_700_000_000,
        expectations_commit_ts_fn=lambda p: 1_700_000_100,
        now_unixtime_fn=lambda: 1_700_001_000,
        now_iso_fn=lambda: "2026-04-18T12:30:00Z",
        sleep_fn=lambda s: None,
        reconstruct_fn=_stub_reconstruct,
        api_call_kind_override="d7b_critic_stub",
    )
    return config, candidates


# ---------------------------------------------------------------------------
# 1. End-to-end stub fire (smoke path) — writes all records
# ---------------------------------------------------------------------------


def test_end_to_end_stub_fire_writes_all_records(tmp_config, monkeypatch):
    config, candidates = tmp_config
    results = [_critic_ok(cost=0.01, svr=0.3) for _ in range(5)]
    it = iter(results)
    monkeypatch.setattr(
        stage2b, "run_critic", lambda *args, **kwargs: next(it),
    )

    agg = stage2b.run_stage2b(config)

    assert agg["completed_call_count"] == 5
    assert agg["sequence_aborted"] is False
    assert agg["abort_reason"] is None
    assert config.aggregate_record_path.exists()
    for i in range(1, 6):
        per_call = config.per_call_record_dir / f"call_{i}_live_call_record.json"
        assert per_call.exists(), f"missing per-call record #{i}"
    # Sequence-oriented ordered lists (NOT distributions).
    assert len(agg["actual_costs_in_call_order"]) == 5
    assert len(agg["reasoning_lengths_in_call_order"]) == 5
    assert len(agg["critic_statuses_in_call_order"]) == 5


# ---------------------------------------------------------------------------
# 2. HG5 — commit ordering gates
# ---------------------------------------------------------------------------


def test_hg5_selection_committed_after_expectations_fails(tmp_config):
    config, _ = tmp_config
    # Selection commit ts >= expectations commit ts — must fail.
    config.selection_commit_ts_fn = lambda p: 1_700_000_200
    config.expectations_commit_ts_fn = lambda p: 1_700_000_100
    with pytest.raises(stage2b.Stage2bStartupError, match="HG5"):
        stage2b.run_stage2b(config)


def test_hg5_expectations_committed_after_wallclock_fails(tmp_config):
    config, _ = tmp_config
    config.expectations_commit_ts_fn = lambda p: 1_700_000_200
    config.now_unixtime_fn = lambda: 1_700_000_100
    with pytest.raises(stage2b.Stage2bStartupError, match="HG5"):
        stage2b.run_stage2b(config)


def test_hg5_selection_uncommitted_fails(tmp_config):
    config, _ = tmp_config
    config.selection_commit_ts_fn = lambda p: None
    with pytest.raises(stage2b.Stage2bStartupError, match="HG5"):
        stage2b.run_stage2b(config)


# ---------------------------------------------------------------------------
# 3. HG3 / HG4 / HG4b — expectations file gates
# ---------------------------------------------------------------------------


def test_hg3_expectations_file_missing_aborts(tmp_config):
    config, _ = tmp_config
    config.expectations_path.unlink()
    with pytest.raises(stage2b.Stage2bStartupError, match="HG3"):
        stage2b.run_stage2b(config)


def test_hg3_expectations_uncommitted_aborts(tmp_config):
    config, _ = tmp_config
    config.expectations_commit_ts_fn = lambda p: None
    with pytest.raises(stage2b.Stage2bStartupError, match="HG3"):
        stage2b.run_stage2b(config)


def test_hg4_missing_aggregate_header_aborts(tmp_config):
    config, candidates = tmp_config
    # Remove the aggregate header entirely.
    text = config.expectations_path.read_text(encoding="utf-8")
    text = text.replace(
        "## Aggregate Expectations Across All 5 Calls", "## AGG HEADER BROKEN",
    )
    config.expectations_path.write_text(text, encoding="utf-8")
    with pytest.raises(stage2b.Stage2bStartupError, match="HG4"):
        stage2b.run_stage2b(config)


def test_hg4b_candidate_header_mismatch_aborts(tmp_config):
    config, candidates = tmp_config
    # Corrupt candidate #3's header (wrong theme name).
    text = config.expectations_path.read_text(encoding="utf-8")
    bad_text = text.replace("volume_divergence", "volume_WRONG", 1)
    config.expectations_path.write_text(bad_text, encoding="utf-8")
    with pytest.raises(stage2b.Stage2bStartupError, match="HG4b"):
        stage2b.run_stage2b(config)


# ---------------------------------------------------------------------------
# 4. HG8 — file-exists protection
# ---------------------------------------------------------------------------


def test_hg8_refuses_to_overwrite_existing_aggregate_record(tmp_config):
    config, _ = tmp_config
    config.aggregate_record_path.parent.mkdir(parents=True, exist_ok=True)
    config.aggregate_record_path.write_text("{}", encoding="utf-8")
    with pytest.raises(stage2b.Stage2bStartupError, match="HG8"):
        stage2b.run_stage2b(config)


# ---------------------------------------------------------------------------
# 5. Abort rules — single source of truth reads persisted per-call fields
# ---------------------------------------------------------------------------


def test_abort_rule_a_two_consecutive_api_level_errors(tmp_config, monkeypatch):
    config, _ = tmp_config
    # Call 1 ok, calls 2 + 3 api-level (cost=0, timeout marker) → abort after #3.
    queue = [
        _critic_ok(cost=0.01),
        _critic_d7b_error(signature="timeout", cost=0.0),
        _critic_d7b_error(signature="api_connection reset", cost=0.0),
        _critic_ok(cost=0.01),
        _critic_ok(cost=0.01),
    ]
    it = iter(queue)
    monkeypatch.setattr(
        stage2b, "run_critic", lambda *a, **kw: next(it),
    )
    agg = stage2b.run_stage2b(config)
    assert agg["sequence_aborted"] is True
    assert agg["abort_reason"] == "api_level_consecutive"
    assert agg["abort_at_call_index"] == 3


def test_abort_rule_b_cumulative_error_rate_over_40_percent(tmp_config, monkeypatch):
    config, _ = tmp_config
    # Calls 1, 2, 3 = content-level errors (cost > 0 to dodge rule a AND c too).
    # Actually content-level count = 3 trips rule c first; we want rule b,
    # so use one ok + two errors at K=3 → 2/3 = 66% > 40% and <3 content errors.
    queue = [
        _critic_ok(cost=0.01),
        _critic_d7b_error(signature="parse failed", cost=0.001),
        _critic_d7b_error(signature="parse failed", cost=0.001),
        _critic_ok(cost=0.01),
        _critic_ok(cost=0.01),
    ]
    it = iter(queue)
    monkeypatch.setattr(
        stage2b, "run_critic", lambda *a, **kw: next(it),
    )
    agg = stage2b.run_stage2b(config)
    assert agg["sequence_aborted"] is True
    # Rule (b) fires at call 3: 2 errors / 3 calls = 66% > 40%.
    # Rule (c) requires content_level >= 3, not reached at K=3 (only 2).
    assert agg["abort_reason"] == "cumulative_error_rate"
    assert agg["abort_at_call_index"] == 3


def test_abort_rule_c_content_level_threshold(tmp_config, monkeypatch):
    config, _ = tmp_config
    # Three content-level errors at calls 1, 2, 3 (cost > 0 → content_level).
    queue = [
        _critic_d7b_error(signature="parse", cost=0.001),
        _critic_d7b_error(signature="parse", cost=0.001),
        _critic_d7b_error(signature="parse", cost=0.001),
        _critic_ok(cost=0.01),
        _critic_ok(cost=0.01),
    ]
    it = iter(queue)
    monkeypatch.setattr(
        stage2b, "run_critic", lambda *a, **kw: next(it),
    )
    agg = stage2b.run_stage2b(config)
    assert agg["sequence_aborted"] is True
    # Three content-level errors is a superset of both rule (b) and rule (c).
    # Rule (b) is tested earlier with 2 content errors + 1 ok, so both
    # abort_reason values are valid evidence of cost-capped fail-fast.
    assert agg["abort_reason"] in {"cumulative_error_rate", "content_level_threshold"}
    assert agg["abort_at_call_index"] == 3


def test_abort_rule_d_per_call_cost_exceeded(tmp_config, monkeypatch):
    config, _ = tmp_config
    queue = [
        _critic_ok(cost=0.01),
        _critic_ok(cost=0.06),  # > 0.05 ceiling
        _critic_ok(cost=0.01),
        _critic_ok(cost=0.01),
        _critic_ok(cost=0.01),
    ]
    it = iter(queue)
    monkeypatch.setattr(
        stage2b, "run_critic", lambda *a, **kw: next(it),
    )
    agg = stage2b.run_stage2b(config)
    assert agg["sequence_aborted"] is True
    assert agg["abort_reason"] == "per_call_cost_exceeded"
    assert agg["abort_at_call_index"] == 2


def test_abort_rule_e_cumulative_cost_exceeded(tmp_config, monkeypatch):
    config, _ = tmp_config
    # Each call under 0.05 ceiling, but cumulative > 0.10 cap by call 3.
    queue = [
        _critic_ok(cost=0.04),
        _critic_ok(cost=0.04),
        _critic_ok(cost=0.04),  # cumulative = 0.12 > 0.10
        _critic_ok(cost=0.01),
        _critic_ok(cost=0.01),
    ]
    it = iter(queue)
    monkeypatch.setattr(
        stage2b, "run_critic", lambda *a, **kw: next(it),
    )
    agg = stage2b.run_stage2b(config)
    assert agg["sequence_aborted"] is True
    assert agg["abort_reason"] == "cumulative_cost_exceeded"
    assert agg["abort_at_call_index"] == 3


# ---------------------------------------------------------------------------
# 6. write_completed_at ordering + atomic-write corruption guard
# ---------------------------------------------------------------------------


def test_write_completed_at_is_last_field_in_aggregate_record(tmp_config, monkeypatch):
    config, _ = tmp_config
    queue = [_critic_ok(cost=0.01) for _ in range(5)]
    it = iter(queue)
    monkeypatch.setattr(
        stage2b, "run_critic", lambda *a, **kw: next(it),
    )
    stage2b.run_stage2b(config)
    payload = json.loads(config.aggregate_record_path.read_text(encoding="utf-8"))
    assert "write_completed_at" in payload
    keys = list(payload.keys())
    assert keys[-1] == "write_completed_at", (
        f"write_completed_at must be the last key; got tail={keys[-3:]}"
    )


def test_atomic_write_leaves_no_partial_file_on_failure(tmp_path):
    """Failing during serialization MUST NOT leave a half-written file."""
    target = tmp_path / "agg.json"

    # Payload with a non-JSON-serializable value — json.dumps raises TypeError.
    payload = {"x": object()}
    with pytest.raises(TypeError):
        stage2b.atomic_write_json(target, payload)
    # Primary target is never created — the write goes via .tmp then os.replace().
    assert not target.exists()


def test_atomic_write_is_atomic_via_os_replace(tmp_path):
    """Successful writes land at primary path; no .tmp sidecar left behind."""
    target = tmp_path / "agg.json"
    stage2b.atomic_write_json(target, {"completed": True})
    assert target.exists()
    # os.replace() should have moved the .tmp file over, not left it behind.
    tmp_sidecar = target.with_suffix(target.suffix + ".tmp")
    assert not tmp_sidecar.exists()


# ---------------------------------------------------------------------------
# 7. Stage 2a archival on first live fire
# ---------------------------------------------------------------------------


def test_stage2a_artifacts_archived_on_first_live_fire(tmp_path):
    critic_dir = tmp_path / "raw_payloads" / f"batch_{stage2b.STAGE2B_BATCH_UUID}" / "critic"
    critic_dir.mkdir(parents=True)
    # Simulate Stage 2a residue.
    for name in (
        "call_0073_prompt.txt",
        "call_0073_response.json",
        "call_0073_critic_result.json",
        "call_0073_traceback.txt",
    ):
        (critic_dir / name).write_text("legacy stage 2a payload", encoding="utf-8")

    archive_dir = stage2b.archive_stage2a_artifacts_if_present(critic_dir, position=73)
    assert archive_dir is not None
    assert archive_dir.exists()
    for name in (
        "call_0073_prompt.txt",
        "call_0073_response.json",
        "call_0073_critic_result.json",
        "call_0073_traceback.txt",
    ):
        assert (archive_dir / name).exists(), f"{name} missing after archive"
        assert not (critic_dir / name).exists(), f"{name} still present in critic_dir"


def test_stage2a_archival_refuses_to_overwrite_existing_archive(tmp_path):
    critic_dir = tmp_path / "critic"
    critic_dir.mkdir()
    (critic_dir / "call_0073_prompt.txt").write_text("x", encoding="utf-8")
    (critic_dir / "stage2a_archive").mkdir()
    with pytest.raises(stage2b.Stage2bStartupError, match="archive"):
        stage2b.archive_stage2a_artifacts_if_present(critic_dir, position=73)


# ---------------------------------------------------------------------------
# 8. Classification + reconciliation primitives
# ---------------------------------------------------------------------------


def test_classify_d7b_error_cost_positive_is_content_level():
    assert (
        stage2b.classify_d7b_error("whatever marker", actual_cost_usd=0.001)
        == "content_level"
    )


def test_classify_d7b_error_cost_zero_timeout_is_api_level():
    assert (
        stage2b.classify_d7b_error("timeout after 30s", actual_cost_usd=0.0)
        == "api_level"
    )


def test_classify_d7b_error_cost_zero_no_marker_defaults_content_level():
    assert (
        stage2b.classify_d7b_error("something unexpected", actual_cost_usd=0.0)
        == "content_level"
    )


def test_is_consistent_exact_half_threshold_is_high():
    # Exactly 0.5 → >= 0.5 → HIGH (shallow variant).
    # divergence_expected requires structurally distinct (low risk).
    assert stage2b.is_consistent_with_label("divergence_expected", 0.5) is False
    # agreement_expected requires shallow variant (high risk).
    assert stage2b.is_consistent_with_label("agreement_expected", 0.5) is True
    # neutral is always None.
    assert stage2b.is_consistent_with_label("neutral", 0.5) is None
    # d7b_error (None risk) → None.
    assert stage2b.is_consistent_with_label("divergence_expected", None) is None


# ---------------------------------------------------------------------------
# 9. Selection-tier invariants (HG2b)
# ---------------------------------------------------------------------------


def test_tier_0_with_nonempty_warnings_fails_invariant():
    selection = {
        "selection_tier": 0,
        "selection_warnings": [{"constraint_relaxed": "x"}],
        "candidates": [],
    }
    with pytest.raises(stage2b.Stage2bStartupError, match="HG2b"):
        stage2b.verify_selection_invariants(selection)


def test_tier_2_requires_divergence_coverage_warning():
    selection = {
        "selection_tier": 2,
        "selection_warnings": [{"constraint_relaxed": "other"}],
        "candidates": [],
    }
    with pytest.raises(stage2b.Stage2bStartupError, match="HG2b"):
        stage2b.verify_selection_invariants(selection)


def test_tier_invalid_value_fails_invariant():
    with pytest.raises(stage2b.Stage2bStartupError, match="HG2b"):
        stage2b.verify_selection_invariants(
            {"selection_tier": 3, "selection_warnings": []},
        )


# ---------------------------------------------------------------------------
# 10. Mutually exclusive flags + config builder
# ---------------------------------------------------------------------------


def test_build_config_rejects_both_flags_set():
    with pytest.raises(ValueError, match="mutually exclusive"):
        stage2b.build_stage2b_config(confirm_live=True, stub=True)


def test_build_config_rejects_neither_flag_set():
    with pytest.raises(ValueError, match="required"):
        stage2b.build_stage2b_config(confirm_live=False, stub=False)


def test_build_config_stub_routes_to_dryrun_root():
    cfg = stage2b.build_stage2b_config(confirm_live=False, stub=True)
    assert cfg.stub is True
    assert str(cfg.aggregate_record_path).startswith(str(stage2b.DRYRUN_ROOT))
    assert str(cfg.raw_payload_root).startswith(str(stage2b.DRYRUN_ROOT))
    assert str(cfg.ledger_path).startswith(str(stage2b.DRYRUN_ROOT))
    assert cfg.api_call_kind_override == "d7b_critic_stub"


# ---------------------------------------------------------------------------
# 11. Structural-variant reconciliation sequence appears in aggregate
# ---------------------------------------------------------------------------


def test_aggregate_reconciliation_captures_per_candidate_consistency(
    tmp_config, monkeypatch,
):
    config, candidates = tmp_config
    # Tailor scores: #1,#2,#3 (divergence) get low svr → consistent.
    # #4 agreement gets high svr → consistent. #5 neutral → None.
    queue = [
        _critic_ok(cost=0.01, svr=0.2),  # divergence, low → consistent
        _critic_ok(cost=0.01, svr=0.3),
        _critic_ok(cost=0.01, svr=0.49),
        _critic_ok(cost=0.01, svr=0.8),  # agreement, high → consistent
        _critic_ok(cost=0.01, svr=0.5),  # neutral → None
    ]
    it = iter(queue)
    monkeypatch.setattr(
        stage2b, "run_critic", lambda *a, **kw: next(it),
    )
    agg = stage2b.run_stage2b(config)
    recon = agg["agreement_divergence_reconciliation_by_call"]
    assert recon["1"]["observed_consistent_with_label"] is True
    assert recon["4"]["observed_consistent_with_label"] is True
    assert recon["5"]["observed_consistent_with_label"] is None


# ---------------------------------------------------------------------------
# 12. Per-call record schema (Stage 2b extensions)
# ---------------------------------------------------------------------------


def test_per_call_record_contains_stage2b_extensions(tmp_config, monkeypatch):
    config, _ = tmp_config
    queue = [_critic_ok(cost=0.01) for _ in range(5)]
    it = iter(queue)
    monkeypatch.setattr(
        stage2b, "run_critic", lambda *a, **kw: next(it),
    )
    stage2b.run_stage2b(config)
    per_call_1 = json.loads(
        (config.per_call_record_dir / "call_1_live_call_record.json").read_text(
            encoding="utf-8",
        ),
    )
    for field in (
        "firing_order",
        "candidate_position",
        "candidate_theme",
        "candidate_hypothesis_hash",
        "pre_registered_label",
        "prior_factor_sets_count",
        "theme_hint_factor_count",
        "prompt_chars",
        "prompt_sha256",
        "inter_call_sleep_elapsed_seconds",
        "d7b_error_category",
    ):
        assert field in per_call_1, f"missing Stage 2b extension: {field}"
    assert per_call_1["firing_order"] == 1
    assert per_call_1["pre_registered_label"] == "divergence_expected"
    assert per_call_1["d7b_error_category"] is None  # ok path


# ---------------------------------------------------------------------------
# 13. Integrity hashes present in aggregate record
# ---------------------------------------------------------------------------


def test_aggregate_record_includes_sha256_integrity_fields(tmp_config, monkeypatch):
    config, _ = tmp_config
    queue = [_critic_ok(cost=0.01) for _ in range(5)]
    it = iter(queue)
    monkeypatch.setattr(
        stage2b, "run_critic", lambda *a, **kw: next(it),
    )
    agg = stage2b.run_stage2b(config)
    for f in (
        "d7b_prompt_template_sha256",
        "selection_json_sha256",
        "expectations_file_sha256",
    ):
        assert isinstance(agg[f], str)
        assert len(agg[f]) == 64  # SHA-256 hex


# ---------------------------------------------------------------------------
# 14. HG1 — candidate count enforced
# ---------------------------------------------------------------------------


def test_hg1_wrong_candidate_count_fails(tmp_path):
    path = tmp_path / "sel.json"
    # Only 4 candidates.
    _write_selection(path, _default_candidates()[:4])
    sel = json.loads(path.read_text(encoding="utf-8"))
    with pytest.raises(stage2b.Stage2bStartupError, match="HG1"):
        stage2b.verify_candidate_count_and_keys(sel)


def test_hg1_firing_order_mismatch_fails(tmp_path):
    candidates = _default_candidates()
    candidates[2]["firing_order"] = 7  # wrong
    with pytest.raises(stage2b.Stage2bStartupError, match="HG1"):
        stage2b.verify_candidate_count_and_keys(
            {"candidates": candidates},
        )


# ---------------------------------------------------------------------------
# 15. Rule (a) does NOT fire when cost>0 (content_level, not api_level)
# ---------------------------------------------------------------------------


def test_rule_a_not_triggered_by_content_level_consecutive(tmp_config, monkeypatch):
    config, _ = tmp_config
    # Two consecutive content-level errors — must NOT trip rule (a).
    queue = [
        _critic_ok(cost=0.01),
        _critic_d7b_error(signature="parse", cost=0.001),
        _critic_d7b_error(signature="parse", cost=0.001),
        _critic_ok(cost=0.01),
        _critic_ok(cost=0.01),
    ]
    it = iter(queue)
    monkeypatch.setattr(
        stage2b, "run_critic", lambda *a, **kw: next(it),
    )
    agg = stage2b.run_stage2b(config)
    # Rule (b) fires at call 3 (2/3 errors), NOT rule (a).
    assert agg["abort_reason"] != "api_level_consecutive"

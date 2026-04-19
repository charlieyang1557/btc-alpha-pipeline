"""Tests for scripts/run_d7_stage2c_batch.py — D7 Stage 2c fire script.

Covers the launch prompt §8.2 minimum-30 test matrix with Stage 2c-specific
extensions:

    - End-to-end 20-call stub fire writes all records + scope-lock counts
    - HG1, HG2b, HG2c (anchor drift), HG3, HG4, HG4b, HG4c (neutral group),
      HG5, HG6b (mid-sequence template drift), HG8
    - Abort rules (a)(b)(c)(d)(e) with Stage 2c scope-lock primacy on (c)
    - Stage 2b overlap archival of 5 candidate positions
    - is_stage2b_overlap boolean per-call + aggregate sequence
    - stage2b_overlap_count / stage2b_overlap_positions / _completed_count
    - svr_by_label partitions with paired positions/svr_values
    - label_counts_in_sequence / theme_counts_in_sequence
    - extract_neutral_group_section_body extraction semantics
    - Stub-mode physical isolation: no writes under raw_payloads/
    - Partial prior Stage 2c run detection
    - write_completed_at ordering + atomic write
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import scripts.run_d7_stage2c_batch as stage2c
from agents.critic.batch_context import (
    DEFAULT_MOMENTUM_FACTORS,
    THEME_ANCHOR_FACTORS,
    THEME_HINTS,
    BatchContext,
)
from agents.critic.result import CriticResult
from strategies.dsl import StrategyDSL


# ---------------------------------------------------------------------------
# Fixtures & helpers
# ---------------------------------------------------------------------------

# Scope-lock signed-off positions (commit b71ffd1 replay_candidates.json).
_POSITIONS = [
    17, 22, 27, 32, 62, 72, 73, 74, 77, 83,
    97, 102, 107, 112, 117, 138, 143, 147, 152, 162,
]
# 8 agreement, 3 divergence, 9 neutral (per scope lock §Lock 1).
_LABELS = (
    ["agreement_expected"] * 8
    + ["divergence_expected"] * 3
    + ["neutral"] * 9
)
# 15 mean_reversion, 4 volatility_regime, 1 volume_divergence.
_THEMES = (
    ["mean_reversion"] * 15
    + ["volatility_regime"] * 4
    + ["volume_divergence"] * 1
)


_NEUTRAL_GROUP_SECTION = (
    "## Aggregate Prediction for Neutral Group\n"
    "The nine-candidate neutral group is expected to distribute "
    "structural_variant_risk across both sides of 0.5 without any skew "
    "toward agreement_expected or divergence_expected at the aggregate "
    "level. This is a falsifiable aggregate prediction.\n\n"
)

_VALID_EXPECTATIONS_HEADERS = (
    "## Anti-Hindsight Anchor\n"
    "Expected behavior locked at commit before fire.\n\n"
    "## Aggregate Expectations Across All 20 Calls\n"
    "All twenty calls should return critic_status=ok under stub.\n\n"
    + _NEUTRAL_GROUP_SECTION
    + "## Per-Candidate Expectations\n"
)


def _make_candidate(
    firing_order: int, position: int, theme: str, label: str,
    hypothesis_hash: str,
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
    out: list[dict] = []
    for i, pos in enumerate(_POSITIONS):
        out.append(
            _make_candidate(
                firing_order=i + 1,
                position=pos,
                theme=_THEMES[i],
                label=_LABELS[i],
                hypothesis_hash=f"{i:x}" * 16,
            )
        )
    return out


def _write_selection(path: Path, candidates: list[dict]) -> None:
    payload = {
        "stage_label": "d7_stage2c",
        "record_version": "1.0",
        "batch_uuid": stage2c.STAGE2C_BATCH_UUID,
        "selection_timestamp_utc": "2026-04-18T12:22:48Z",
        "selection_tier": 0,
        "selection_warnings": [],
        "pool_size_total": 200,
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
        "name": "stage2c_test_strategy",
        "description": "Stage 2c unit test strategy for stub reconstruction.",
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


def _theme_for_position(position: int) -> str:
    idx = _POSITIONS.index(position)
    return _THEMES[idx]


def _stub_reconstruct(batch_uuid: str, position: int, **kwargs) -> tuple:
    return _make_dsl(), _theme_for_position(position), _make_batch_context(position)


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


def _persisted_record(
    status: str = "ok",
    category: str | None = None,
    actual_cost: float = 0.02,
) -> dict:
    """Build a minimal per-call record dict for should_abort unit tests."""
    return {
        "critic_status": status,
        "d7b_error_category": category,
        "actual_cost_usd": actual_cost,
    }


@pytest.fixture
def tmp_config(tmp_path):
    """Testable Stage2cConfig rooted in tmp_path with HG2c bypass."""
    candidates = _default_candidates()
    selection_path = tmp_path / "selection.json"
    expectations_path = tmp_path / "expectations.md"
    aggregate_path = tmp_path / "stage2c_batch_record.json"
    per_call_dir = tmp_path / "per_call"
    per_call_dir.mkdir()
    raw_root = tmp_path / "raw_payloads_tmp"
    ledger_path = tmp_path / "ledger.db"

    _write_selection(selection_path, candidates)
    _write_expectations(expectations_path, candidates)

    prompt_template_path = tmp_path / "d7b_prompt.py"
    prompt_template_path.write_text("# fake template\n", encoding="utf-8")

    config = stage2c.Stage2cConfig(
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
        skip_anchor_check=True,
    )
    return config, candidates


# ---------------------------------------------------------------------------
# 1. End-to-end 20-call stub fire
# ---------------------------------------------------------------------------


def test_end_to_end_stub_fire_writes_20_records(tmp_config, monkeypatch):
    config, candidates = tmp_config
    results = [_critic_ok(cost=0.01, svr=0.3) for _ in range(20)]
    it = iter(results)
    monkeypatch.setattr(stage2c, "run_critic", lambda *a, **kw: next(it))

    agg = stage2c.run_stage2c(config)

    assert agg["completed_call_count"] == 20
    assert agg["sequence_aborted"] is False
    assert agg["abort_reason"] is None
    assert config.aggregate_record_path.exists()
    for i in range(1, 21):
        per_call = config.per_call_record_dir / f"call_{i}_live_call_record.json"
        assert per_call.exists(), f"missing per-call record #{i}"
    assert len(agg["actual_costs_in_call_order"]) == 20
    assert len(agg["reasoning_lengths_in_call_order"]) == 20
    assert len(agg["critic_statuses_in_call_order"]) == 20
    assert len(agg["is_stage2b_overlap_in_call_order"]) == 20


def test_end_to_end_stub_fire_matches_scope_lock_aggregates(tmp_config, monkeypatch):
    config, _ = tmp_config
    results = [_critic_ok(cost=0.01, svr=0.3) for _ in range(20)]
    it = iter(results)
    monkeypatch.setattr(stage2c, "run_critic", lambda *a, **kw: next(it))

    agg = stage2c.run_stage2c(config)

    # Scope-lock §Lock 1 signed-off counts.
    assert agg["label_counts_in_sequence"] == {
        "agreement_expected": 8,
        "divergence_expected": 3,
        "neutral": 9,
    }
    assert agg["theme_counts_in_sequence"] == {
        "mean_reversion": 15,
        "volatility_regime": 4,
        "volume_divergence": 1,
    }
    assert agg["stage2b_overlap_count"] == 5
    assert agg["stage2b_overlap_positions"] == [17, 73, 74, 97, 138]
    assert agg["stage2b_overlap_completed_count"] == 5
    # All five overlap candidates completed as critic_status=ok under stub.


# ---------------------------------------------------------------------------
# 2. is_stage2b_overlap per-call boolean
# ---------------------------------------------------------------------------


def test_is_stage2b_overlap_per_call_sequence(tmp_config, monkeypatch):
    config, candidates = tmp_config
    results = [_critic_ok(cost=0.01, svr=0.3) for _ in range(20)]
    it = iter(results)
    monkeypatch.setattr(stage2c, "run_critic", lambda *a, **kw: next(it))

    agg = stage2c.run_stage2c(config)

    seq = agg["is_stage2b_overlap_in_call_order"]
    assert sum(1 for b in seq if b) == 5
    assert sum(1 for b in seq if not b) == 15

    # Overlap-boolean per-call file contents.
    overlap_positions = {17, 73, 74, 97, 138}
    for i, c in enumerate(candidates, 1):
        rec = json.loads(
            (config.per_call_record_dir / f"call_{i}_live_call_record.json").read_text(
                encoding="utf-8",
            ),
        )
        expected = c["position"] in overlap_positions
        assert rec["is_stage2b_overlap"] is expected, (
            f"call #{i} position {c['position']} overlap flag mismatch"
        )


# ---------------------------------------------------------------------------
# 3. svr_by_label partitions
# ---------------------------------------------------------------------------


def test_svr_by_label_partition_pairs_positions_and_values(tmp_config, monkeypatch):
    config, candidates = tmp_config
    # Assign distinct SVRs per-label so grouping is falsifiable.
    svrs = []
    for c in candidates:
        label = c["d7a_b_relationship_label"]
        if label == "agreement_expected":
            svrs.append(0.8)
        elif label == "divergence_expected":
            svrs.append(0.2)
        else:
            svrs.append(0.5)
    results = [_critic_ok(cost=0.01, svr=s) for s in svrs]
    it = iter(results)
    monkeypatch.setattr(stage2c, "run_critic", lambda *a, **kw: next(it))

    agg = stage2c.run_stage2c(config)

    svr_by_label = agg["svr_by_label"]
    assert set(svr_by_label.keys()) == {
        "agreement_expected", "divergence_expected", "neutral",
    }
    # Counts match label distribution.
    assert svr_by_label["agreement_expected"]["completed_count"] == 8
    assert svr_by_label["divergence_expected"]["completed_count"] == 3
    assert svr_by_label["neutral"]["completed_count"] == 9
    # Paired positions sorted ascending.
    for bucket in svr_by_label.values():
        assert bucket["positions"] == sorted(bucket["positions"])
        assert len(bucket["positions"]) == len(bucket["svr_values"])
    # Agreement SVRs all 0.8.
    assert all(v == 0.8 for v in svr_by_label["agreement_expected"]["svr_values"])
    assert all(v == 0.2 for v in svr_by_label["divergence_expected"]["svr_values"])


def test_svr_by_label_excludes_d7b_error_calls(tmp_config, monkeypatch):
    config, candidates = tmp_config
    results: list[CriticResult] = []
    for c in candidates:
        if c["position"] == 17:
            # First candidate errors → SVR omitted from partition.
            results.append(_critic_d7b_error(signature="parse", cost=0.001))
        else:
            label = c["d7a_b_relationship_label"]
            svr = 0.8 if label == "agreement_expected" else (
                0.2 if label == "divergence_expected" else 0.5
            )
            results.append(_critic_ok(cost=0.01, svr=svr))
    it = iter(results)
    monkeypatch.setattr(stage2c, "run_critic", lambda *a, **kw: next(it))

    agg = stage2c.run_stage2c(config)
    # Rule (b) may trigger early on a single error; if sequence aborts,
    # still verify svr_by_label excludes the error candidate regardless.
    neutral = agg["svr_by_label"]["neutral"]
    assert 17 not in neutral["positions"]


# ---------------------------------------------------------------------------
# 4. HG1 — count + key validation
# ---------------------------------------------------------------------------


def test_hg1_wrong_candidate_count_fails(tmp_path):
    path = tmp_path / "sel.json"
    _write_selection(path, _default_candidates()[:19])
    sel = json.loads(path.read_text(encoding="utf-8"))
    with pytest.raises(stage2c.Stage2cStartupError, match="HG1"):
        stage2c.verify_candidate_count_and_keys(sel)


def test_hg1_firing_order_mismatch_fails():
    candidates = _default_candidates()
    candidates[5]["firing_order"] = 99
    with pytest.raises(stage2c.Stage2cStartupError, match="HG1"):
        stage2c.verify_candidate_count_and_keys({"candidates": candidates})


def test_hg1_missing_required_key_fails():
    candidates = _default_candidates()
    del candidates[0]["hypothesis_hash"]
    with pytest.raises(stage2c.Stage2cStartupError, match="HG1"):
        stage2c.verify_candidate_count_and_keys({"candidates": candidates})


# ---------------------------------------------------------------------------
# 5. HG2b — selection tier invariants
# ---------------------------------------------------------------------------


def test_hg2b_tier_0_with_warnings_fails():
    with pytest.raises(stage2c.Stage2cStartupError, match="HG2b"):
        stage2c.verify_selection_invariants(
            {"selection_tier": 0, "selection_warnings": [{"x": 1}]},
        )


def test_hg2b_tier_2_requires_divergence_coverage_warning():
    with pytest.raises(stage2c.Stage2cStartupError, match="HG2b"):
        stage2c.verify_selection_invariants(
            {"selection_tier": 2, "selection_warnings": [{"constraint_relaxed": "x"}]},
        )


def test_hg2b_invalid_tier_fails():
    with pytest.raises(stage2c.Stage2cStartupError, match="HG2b"):
        stage2c.verify_selection_invariants(
            {"selection_tier": 3, "selection_warnings": []},
        )


# ---------------------------------------------------------------------------
# 6. HG2c — scope-lock anchor hash
# ---------------------------------------------------------------------------


def test_hg2c_anchor_hash_drift_fails(tmp_config, monkeypatch):
    config, _ = tmp_config
    config.skip_anchor_check = False
    # Inject an anchor_hash_fn returning a DIFFERENT hash than on-disk.
    config.anchor_hash_fn = lambda c, p: "deadbeef" * 8
    monkeypatch.setattr(stage2c, "run_critic", lambda *a, **kw: _critic_ok(cost=0.01))
    with pytest.raises(stage2c.Stage2cStartupError, match="HG2c"):
        stage2c.run_stage2c(config)


def test_hg2c_anchor_commit_unresolvable_fails(tmp_config, monkeypatch):
    config, _ = tmp_config
    config.skip_anchor_check = False
    config.anchor_hash_fn = lambda c, p: None
    monkeypatch.setattr(stage2c, "run_critic", lambda *a, **kw: _critic_ok(cost=0.01))
    with pytest.raises(stage2c.Stage2cStartupError, match="HG2c"):
        stage2c.run_stage2c(config)


def test_hg2c_anchor_hash_match_passes(tmp_config, monkeypatch):
    config, _ = tmp_config
    config.skip_anchor_check = False
    # Compute on-disk hash and return it exactly from the fn.
    on_disk = stage2c._file_sha256(config.selection_json_path)
    config.anchor_hash_fn = lambda c, p: on_disk
    monkeypatch.setattr(
        stage2c, "run_critic",
        lambda *a, **kw: _critic_ok(cost=0.01),
    )
    agg = stage2c.run_stage2c(config)
    assert agg["completed_call_count"] == 20


# ---------------------------------------------------------------------------
# 7. HG3 / HG4 / HG4b — expectations file structure
# ---------------------------------------------------------------------------


def test_hg3_expectations_file_missing_aborts(tmp_config):
    config, _ = tmp_config
    config.expectations_path.unlink()
    with pytest.raises(stage2c.Stage2cStartupError, match="HG3"):
        stage2c.run_stage2c(config)


def test_hg3_expectations_uncommitted_aborts(tmp_config):
    config, _ = tmp_config
    config.expectations_commit_ts_fn = lambda p: None
    with pytest.raises(stage2c.Stage2cStartupError, match="HG3"):
        stage2c.run_stage2c(config)


def test_hg4_missing_aggregate_header_aborts(tmp_config):
    config, _ = tmp_config
    text = config.expectations_path.read_text(encoding="utf-8")
    text = text.replace(
        "## Aggregate Expectations Across All 20 Calls",
        "## AGG BROKEN",
    )
    config.expectations_path.write_text(text, encoding="utf-8")
    with pytest.raises(stage2c.Stage2cStartupError, match="HG4"):
        stage2c.run_stage2c(config)


def test_hg4b_candidate_header_mismatch_aborts(tmp_config):
    config, _ = tmp_config
    text = config.expectations_path.read_text(encoding="utf-8")
    bad = text.replace("Position 97", "Position 999", 1)
    config.expectations_path.write_text(bad, encoding="utf-8")
    with pytest.raises(stage2c.Stage2cStartupError, match="HG4b"):
        stage2c.run_stage2c(config)


# ---------------------------------------------------------------------------
# 8. HG4c — neutral-group aggregate prediction
# ---------------------------------------------------------------------------


def test_hg4c_missing_neutral_group_header_fails(tmp_config):
    config, _ = tmp_config
    text = config.expectations_path.read_text(encoding="utf-8")
    text = text.replace(
        "## Aggregate Prediction for Neutral Group",
        "## Random Other Header",
    )
    config.expectations_path.write_text(text, encoding="utf-8")
    with pytest.raises(stage2c.Stage2cStartupError, match="HG4c"):
        stage2c.run_stage2c(config)


def test_hg4c_neutral_group_body_too_short_fails(tmp_config):
    config, _ = tmp_config
    # Replace the full neutral section body with just a handful of chars.
    body = (
        "## Aggregate Prediction for Neutral Group\n"
        "short.\n\n"
    )
    text = config.expectations_path.read_text(encoding="utf-8")
    # Replace the current well-formed section with the short one.
    import re
    pat = re.compile(
        r"## Aggregate Prediction for Neutral Group\n.*?(?=\n## )",
        re.DOTALL,
    )
    replaced = pat.sub(body.rstrip("\n"), text, count=1)
    config.expectations_path.write_text(replaced, encoding="utf-8")
    with pytest.raises(stage2c.Stage2cStartupError, match="HG4c"):
        stage2c.run_stage2c(config)


def test_extract_neutral_group_section_body_returns_body():
    text = (
        "## Aggregate Prediction for Neutral Group\n"
        "hello neutral body text.\n"
        "more body text here.\n"
        "## Next Header\n"
        "next header body.\n"
    )
    body = stage2c.extract_neutral_group_section_body(text)
    assert body is not None
    assert "hello neutral body text" in body
    assert "Next Header" not in body


def test_extract_neutral_group_section_body_returns_none_when_missing():
    text = (
        "## Other Header\n"
        "only other sections.\n"
    )
    assert stage2c.extract_neutral_group_section_body(text) is None


def test_extract_neutral_group_section_body_stops_at_next_hash_hash_header():
    text = (
        "## Aggregate Prediction for Neutral Group\n"
        "Line 1 of neutral body.\n"
        "### Subsection still in neutral group\n"
        "Line 2 with ### subsection kept.\n"
        "## Per-Candidate Expectations\n"
        "Out of neutral group.\n"
    )
    body = stage2c.extract_neutral_group_section_body(text)
    assert body is not None
    # ### subsection is NOT a terminator.
    assert "Subsection still in neutral group" in body
    assert "Out of neutral group" not in body


# ---------------------------------------------------------------------------
# 9. HG5 — commit ordering gates
# ---------------------------------------------------------------------------


def test_hg5_selection_committed_after_expectations_fails(tmp_config):
    config, _ = tmp_config
    config.selection_commit_ts_fn = lambda p: 1_700_000_200
    config.expectations_commit_ts_fn = lambda p: 1_700_000_100
    with pytest.raises(stage2c.Stage2cStartupError, match="HG5"):
        stage2c.run_stage2c(config)


def test_hg5_expectations_committed_after_wallclock_fails(tmp_config):
    config, _ = tmp_config
    config.expectations_commit_ts_fn = lambda p: 1_700_000_200
    config.now_unixtime_fn = lambda: 1_700_000_100
    with pytest.raises(stage2c.Stage2cStartupError, match="HG5"):
        stage2c.run_stage2c(config)


def test_hg5_selection_uncommitted_fails(tmp_config):
    config, _ = tmp_config
    config.selection_commit_ts_fn = lambda p: None
    with pytest.raises(stage2c.Stage2cStartupError, match="HG5"):
        stage2c.run_stage2c(config)


# ---------------------------------------------------------------------------
# 10. HG8 — file-exists protection
# ---------------------------------------------------------------------------


def test_hg8_refuses_to_overwrite_existing_aggregate_record(tmp_config):
    config, _ = tmp_config
    config.aggregate_record_path.parent.mkdir(parents=True, exist_ok=True)
    config.aggregate_record_path.write_text("{}", encoding="utf-8")
    with pytest.raises(stage2c.Stage2cStartupError, match="HG8"):
        stage2c.run_stage2c(config)


# ---------------------------------------------------------------------------
# 11. Abort rules
# ---------------------------------------------------------------------------


def test_abort_rule_a_two_consecutive_api_level_errors(tmp_config, monkeypatch):
    config, _ = tmp_config
    # ok, api, api → abort after call 3.
    queue = [_critic_ok(cost=0.01)] + [
        _critic_d7b_error(signature="timeout", cost=0.0),
        _critic_d7b_error(signature="api_connection reset", cost=0.0),
    ] + [_critic_ok(cost=0.01) for _ in range(17)]
    it = iter(queue)
    monkeypatch.setattr(stage2c, "run_critic", lambda *a, **kw: next(it))

    agg = stage2c.run_stage2c(config)
    assert agg["sequence_aborted"] is True
    assert agg["abort_reason"] == "api_level_consecutive"
    assert agg["abort_at_call_index"] == 3


def test_abort_rule_b_cumulative_error_rate_over_40_percent(tmp_config, monkeypatch):
    config, _ = tmp_config
    # ok, content-error, content-error at K=3 → 2/3 > 40%, rule (b) fires.
    # Use cost > 0 so classified content_level; only 2 content errors (< 4)
    # ensures rule (c) does NOT trigger even if K>=8 were reached.
    queue = [
        _critic_ok(cost=0.01),
        _critic_d7b_error(signature="parse failed", cost=0.001),
        _critic_d7b_error(signature="parse failed", cost=0.001),
    ] + [_critic_ok(cost=0.01) for _ in range(17)]
    it = iter(queue)
    monkeypatch.setattr(stage2c, "run_critic", lambda *a, **kw: next(it))

    agg = stage2c.run_stage2c(config)
    assert agg["sequence_aborted"] is True
    assert agg["abort_reason"] == "cumulative_error_rate"
    assert agg["abort_at_call_index"] == 3


def test_abort_rule_c_does_not_fire_with_3_content_errors():
    """Rule (c) requires content_errors >= 4 regardless of K."""
    history = (
        [_persisted_record("d7b_error", "content_level", 0.001)] * 3
        + [_persisted_record("ok", None, 0.01)] * 7
    )
    abort, reason = stage2c.should_abort(10, history, 0.01, 0.03)
    assert abort is False
    assert reason is None


def test_abort_rule_c_fires_at_4_content_errors_when_rule_b_does_not():
    """Rule (c) independent trigger: rate = 4/10 = 40% (not >40%)."""
    # 6 ok first (calls 1-6), then 4 content errors (calls 7-10).
    history = (
        [_persisted_record("ok", None, 0.01)] * 6
        + [_persisted_record("d7b_error", "content_level", 0.001)] * 4
    )
    # At call_index=10, rate=4/10=0.40 — rule (b) threshold is strictly >.
    abort, reason = stage2c.should_abort(10, history, 0.001, 0.064)
    assert abort is True
    assert reason == "content_level_threshold"


def test_abort_rule_c_fires_at_k_4_with_4_content_errors():
    """No K floor: rule (c) can fire as early as K=4 with 4 content errors.

    Rule (b) also fires here (rate=100%>40%). Implementation ordering checks
    rule (b) before rule (c), so reason == cumulative_error_rate in practice;
    launch prompt v2 doesn't mandate which abort reason wins in ties, so the
    test verifies only that the sequence aborts with a recognized reason.
    """
    history = [_persisted_record("d7b_error", "content_level", 0.001)] * 4
    abort, reason = stage2c.should_abort(4, history, 0.001, 0.004)
    assert abort is True
    assert reason in {"cumulative_error_rate", "content_level_threshold"}


def test_abort_rule_c_no_k_floor_constant_removed():
    """Regression guard: STAGE2C_CONTENT_ERROR_MIN_K must not be re-introduced."""
    assert not hasattr(stage2c, "STAGE2C_CONTENT_ERROR_MIN_K")


def test_abort_rule_c_deterministic_at_k_7():
    """K=7 with 4 content errors: old K=8 floor would suppress rule (c);
    new contract fires on absolute count alone. Rule (b) also fires at
    rate=4/7>40%; either reason is acceptable per launch prompt v2.
    """
    history = (
        [_persisted_record("d7b_error", "content_level", 0.001)] * 4
        + [_persisted_record("ok", None, 0.01)] * 3
    )
    abort, reason = stage2c.should_abort(7, history, 0.01, 0.034)
    assert abort is True
    assert reason in {"cumulative_error_rate", "content_level_threshold"}


def test_abort_rule_d_per_call_cost_exceeded(tmp_config, monkeypatch):
    config, _ = tmp_config
    queue = [_critic_ok(cost=0.01)] + [_critic_ok(cost=0.06)] + [
        _critic_ok(cost=0.01) for _ in range(18)
    ]
    it = iter(queue)
    monkeypatch.setattr(stage2c, "run_critic", lambda *a, **kw: next(it))

    agg = stage2c.run_stage2c(config)
    assert agg["sequence_aborted"] is True
    assert agg["abort_reason"] == "per_call_cost_exceeded"
    assert agg["abort_at_call_index"] == 2


def test_abort_rule_e_cumulative_cost_scaled_to_point_50(tmp_config, monkeypatch):
    config, _ = tmp_config
    # Each call under 0.05 ceiling but cumulative > 0.50 at some point.
    # 13 calls × 0.04 = 0.52 > 0.50 → aborts at call 13.
    queue = [_critic_ok(cost=0.04) for _ in range(20)]
    it = iter(queue)
    monkeypatch.setattr(stage2c, "run_critic", lambda *a, **kw: next(it))

    agg = stage2c.run_stage2c(config)
    assert agg["sequence_aborted"] is True
    assert agg["abort_reason"] == "cumulative_cost_exceeded"
    assert agg["abort_at_call_index"] == 13


def test_rule_e_under_point_10_no_longer_fires_at_point_10_boundary(tmp_config, monkeypatch):
    """Stage 2b's cap was $0.10; Stage 2c scaled to $0.50 — verify no false abort."""
    config, _ = tmp_config
    # 5 calls × 0.04 = 0.20 — would have tripped Stage 2b's $0.10 cap.
    # Stage 2c cap is $0.50; 20 × 0.02 = $0.40 < $0.50 — should complete.
    queue = [_critic_ok(cost=0.02) for _ in range(20)]
    it = iter(queue)
    monkeypatch.setattr(stage2c, "run_critic", lambda *a, **kw: next(it))

    agg = stage2c.run_stage2c(config)
    assert agg["sequence_aborted"] is False
    assert agg["completed_call_count"] == 20


# ---------------------------------------------------------------------------
# 12. write_completed_at ordering + atomic write
# ---------------------------------------------------------------------------


def test_write_completed_at_is_last_field_in_aggregate_record(tmp_config, monkeypatch):
    config, _ = tmp_config
    queue = [_critic_ok(cost=0.01) for _ in range(20)]
    it = iter(queue)
    monkeypatch.setattr(stage2c, "run_critic", lambda *a, **kw: next(it))
    stage2c.run_stage2c(config)
    payload = json.loads(config.aggregate_record_path.read_text(encoding="utf-8"))
    assert "write_completed_at" in payload
    keys = list(payload.keys())
    assert keys[-1] == "write_completed_at", (
        f"write_completed_at must be last; got tail={keys[-3:]}"
    )


def test_atomic_write_leaves_no_partial_file_on_failure(tmp_path):
    target = tmp_path / "agg.json"
    payload = {"x": object()}
    with pytest.raises(TypeError):
        stage2c.atomic_write_json(target, payload)
    assert not target.exists()


def test_atomic_write_is_atomic_via_os_replace(tmp_path):
    target = tmp_path / "agg.json"
    stage2c.atomic_write_json(target, {"completed": True})
    assert target.exists()
    tmp_sidecar = target.with_suffix(target.suffix + ".tmp")
    assert not tmp_sidecar.exists()


# ---------------------------------------------------------------------------
# 13. Stage 2b overlap archival
# ---------------------------------------------------------------------------


def test_stage2b_overlap_archival_moves_all_five_positions(tmp_path):
    critic_dir = tmp_path / "critic"
    critic_dir.mkdir()
    overlap_positions = [17, 73, 74, 97, 138]
    for pos in overlap_positions:
        for suffix in ("prompt.txt", "response.json", "critic_result.json", "traceback.txt"):
            (critic_dir / f"call_{pos:04d}_{suffix}").write_text(
                f"stage 2b {pos} residue", encoding="utf-8",
            )
    archive_dir = stage2c.archive_stage2b_overlap_artifacts_if_present(critic_dir)
    assert archive_dir is not None
    assert archive_dir.name == "stage2b_archive"
    for pos in overlap_positions:
        for suffix in ("prompt.txt", "response.json", "critic_result.json", "traceback.txt"):
            name = f"call_{pos:04d}_{suffix}"
            assert (archive_dir / name).exists(), f"{name} missing in archive"
            assert not (critic_dir / name).exists(), f"{name} still in critic_dir"


def test_stage2b_overlap_archival_noop_when_no_residue(tmp_path):
    critic_dir = tmp_path / "critic"
    critic_dir.mkdir()
    assert stage2c.archive_stage2b_overlap_artifacts_if_present(critic_dir) is None
    assert not (critic_dir / "stage2b_archive").exists()


def test_stage2b_overlap_archival_refuses_to_overwrite_existing_archive(tmp_path):
    critic_dir = tmp_path / "critic"
    critic_dir.mkdir()
    (critic_dir / "call_0017_prompt.txt").write_text("x", encoding="utf-8")
    (critic_dir / "stage2b_archive").mkdir()
    with pytest.raises(stage2c.Stage2cStartupError, match="archive"):
        stage2c.archive_stage2b_overlap_artifacts_if_present(critic_dir)


# ---------------------------------------------------------------------------
# 14. Partial-prior Stage 2c run detection
# ---------------------------------------------------------------------------


def test_partial_prior_stage2c_run_non_overlap_remnant_aborts(tmp_path):
    critic_dir = tmp_path / "critic"
    critic_dir.mkdir()
    # Non-overlap remnant (position 32 is in selection but not Stage 2b overlap).
    (critic_dir / "call_0032_prompt.txt").write_text("prior run leftover", encoding="utf-8")

    with pytest.raises(stage2c.Stage2cStartupError, match="partial|unexpected"):
        stage2c.detect_unexpected_stage2c_remnants(
            critic_dir=critic_dir,
            stage2c_positions=_POSITIONS,
            aggregate_record_path=tmp_path / "agg.json",
            per_call_record_dir=tmp_path / "per_call",
        )


def test_partial_prior_only_overlap_remnants_does_not_abort(tmp_path):
    critic_dir = tmp_path / "critic"
    critic_dir.mkdir()
    # Only overlap positions present — Stage 2b archival will handle these.
    (critic_dir / "call_0017_prompt.txt").write_text("stage 2b residue", encoding="utf-8")
    per_call_dir = tmp_path / "per_call"
    per_call_dir.mkdir()

    stage2c.detect_unexpected_stage2c_remnants(
        critic_dir=critic_dir,
        stage2c_positions=_POSITIONS,
        aggregate_record_path=tmp_path / "agg.json",
        per_call_record_dir=per_call_dir,
    )


def test_partial_prior_with_completed_aggregate_does_not_abort(tmp_path):
    critic_dir = tmp_path / "critic"
    critic_dir.mkdir()
    (critic_dir / "call_0032_prompt.txt").write_text("x", encoding="utf-8")
    per_call_dir = tmp_path / "per_call"
    per_call_dir.mkdir()
    agg_path = tmp_path / "agg.json"
    agg_path.write_text("{}", encoding="utf-8")
    # Already-finished prior run → archival handled externally; no abort.
    stage2c.detect_unexpected_stage2c_remnants(
        critic_dir=critic_dir,
        stage2c_positions=_POSITIONS,
        aggregate_record_path=agg_path,
        per_call_record_dir=per_call_dir,
    )


# ---------------------------------------------------------------------------
# 15. HG6b — mid-sequence prompt template drift
# ---------------------------------------------------------------------------


def test_hg6b_mid_sequence_template_drift_aborts(tmp_config, monkeypatch):
    config, _ = tmp_config

    call_counter = {"n": 0}
    original_sha256 = stage2c._file_sha256

    def drifting_sha256(p: Path) -> str:
        # Return original bytes for non-template files always.
        if p != config.prompt_template_path:
            return original_sha256(p)
        call_counter["n"] += 1
        if call_counter["n"] == 1:
            # First call during _startup_gates — return real hash.
            return original_sha256(p)
        # Second call is inside _run_one_call's HG6b check — mutate.
        return "deadbeef" * 8

    monkeypatch.setattr(stage2c, "_file_sha256", drifting_sha256)
    monkeypatch.setattr(stage2c, "run_critic", lambda *a, **kw: _critic_ok(cost=0.01))

    agg = stage2c.run_stage2c(config)
    assert agg["sequence_aborted"] is True
    assert agg["abort_reason"] == "prompt_template_mutated_mid_run"
    assert agg["abort_at_call_index"] == 1


# ---------------------------------------------------------------------------
# 16. Classification + reconciliation primitives
# ---------------------------------------------------------------------------


def test_classify_d7b_error_cost_positive_is_content_level():
    assert stage2c.classify_d7b_error("anything", 0.001) == "content_level"


def test_classify_d7b_error_cost_zero_timeout_is_api_level():
    assert stage2c.classify_d7b_error("timeout after 30s", 0.0) == "api_level"


def test_classify_d7b_error_cost_zero_no_marker_defaults_content_level():
    assert stage2c.classify_d7b_error("weird thing", 0.0) == "content_level"


def test_is_consistent_exact_half_threshold_is_high():
    # divergence_expected (low-risk required) → 0.5 maps to high → inconsistent.
    assert stage2c.is_consistent_with_label("divergence_expected", 0.5) is False
    assert stage2c.is_consistent_with_label("agreement_expected", 0.5) is True
    assert stage2c.is_consistent_with_label("neutral", 0.5) is None
    assert stage2c.is_consistent_with_label("divergence_expected", None) is None


def test_reconciliation_rationale_mentions_label_and_svr():
    r = stage2c.reconciliation_rationale("agreement_expected", 0.8)
    assert "agreement_expected" in r
    assert "0.8" in r
    r2 = stage2c.reconciliation_rationale("neutral", 0.5)
    assert "aggregate-level" in r2


# ---------------------------------------------------------------------------
# 17. Stub-mode physical isolation
# ---------------------------------------------------------------------------


def test_stub_mode_never_writes_under_raw_payloads(tmp_config, monkeypatch):
    config, _ = tmp_config
    queue = [_critic_ok(cost=0.01) for _ in range(20)]
    it = iter(queue)
    monkeypatch.setattr(stage2c, "run_critic", lambda *a, **kw: next(it))
    stage2c.run_stage2c(config)

    production_raw = Path("raw_payloads").resolve()
    # Verify no Stage 2c artifact path resolves under production raw_payloads/.
    all_paths = [
        config.aggregate_record_path,
        config.per_call_record_dir,
        config.raw_payload_root,
        config.ledger_path,
    ]
    for p in all_paths:
        resolved = str(p.resolve())
        assert str(production_raw) not in resolved or "dryrun" in resolved, (
            f"Stub path {p} resolves under production raw_payloads/"
        )


def test_assert_stub_isolation_raises_on_raw_payloads_path(tmp_path):
    # Construct a stub config that WOULD write under raw_payloads/ — reject.
    bad_raw = Path("raw_payloads") / "whatever"
    config = stage2c.Stage2cConfig(
        confirm_live=False,
        stub=True,
        selection_json_path=tmp_path / "sel.json",
        expectations_path=tmp_path / "exp.md",
        aggregate_record_path=tmp_path / "agg.json",
        per_call_record_dir=tmp_path / "pc",
        raw_payload_root=bad_raw,
        ledger_path=tmp_path / "ledger.db",
        prompt_template_path=tmp_path / "tpl.py",
    )
    with pytest.raises(stage2c.Stage2cStartupError, match="raw_payloads"):
        stage2c._assert_stub_isolation(config)


def test_assert_stub_isolation_passes_for_dryrun_paths(tmp_path):
    config = stage2c.Stage2cConfig(
        confirm_live=False,
        stub=True,
        selection_json_path=tmp_path / "sel.json",
        expectations_path=tmp_path / "exp.md",
        aggregate_record_path=stage2c.DRYRUN_ROOT / "agg.json",
        per_call_record_dir=stage2c.DRYRUN_ROOT,
        raw_payload_root=stage2c.DRYRUN_ROOT / "raw_payloads",
        ledger_path=stage2c.DRYRUN_ROOT / "ledger.db",
        prompt_template_path=tmp_path / "tpl.py",
    )
    # Should not raise.
    stage2c._assert_stub_isolation(config)


# ---------------------------------------------------------------------------
# 18. CLI config builder
# ---------------------------------------------------------------------------


def test_build_config_rejects_both_flags_set():
    with pytest.raises(ValueError, match="mutually exclusive"):
        stage2c.build_stage2c_config(confirm_live=True, stub=True)


def test_build_config_rejects_neither_flag_set():
    with pytest.raises(ValueError, match="required"):
        stage2c.build_stage2c_config(confirm_live=False, stub=False)


def test_build_config_stub_routes_to_dryrun_root():
    cfg = stage2c.build_stage2c_config(confirm_live=False, stub=True)
    assert cfg.stub is True
    assert str(cfg.aggregate_record_path).startswith(str(stage2c.DRYRUN_ROOT))
    assert str(cfg.raw_payload_root).startswith(str(stage2c.DRYRUN_ROOT))
    assert str(cfg.ledger_path).startswith(str(stage2c.DRYRUN_ROOT))
    assert cfg.api_call_kind_override == "d7b_critic_stub"


def test_build_config_live_routes_to_production_paths():
    cfg = stage2c.build_stage2c_config(confirm_live=True, stub=False)
    assert cfg.confirm_live is True
    assert cfg.stub is False
    assert cfg.aggregate_record_path == stage2c.AGGREGATE_RECORD_PATH
    assert cfg.raw_payload_root == stage2c.RAW_PAYLOAD_ROOT
    assert cfg.api_call_kind_override == "d7b_critic_live"


# ---------------------------------------------------------------------------
# 19. Integrity hashes in aggregate record
# ---------------------------------------------------------------------------


def test_aggregate_record_includes_sha256_integrity_fields(tmp_config, monkeypatch):
    config, _ = tmp_config
    queue = [_critic_ok(cost=0.01) for _ in range(20)]
    it = iter(queue)
    monkeypatch.setattr(stage2c, "run_critic", lambda *a, **kw: next(it))
    agg = stage2c.run_stage2c(config)
    for f in (
        "d7b_prompt_template_sha256",
        "selection_json_sha256",
        "expectations_file_sha256",
    ):
        assert isinstance(agg[f], str)
        assert len(agg[f]) == 64  # SHA-256 hex length


def test_aggregate_record_stage2c_identity_fields(tmp_config, monkeypatch):
    config, _ = tmp_config
    queue = [_critic_ok(cost=0.01) for _ in range(20)]
    it = iter(queue)
    monkeypatch.setattr(stage2c, "run_critic", lambda *a, **kw: next(it))
    agg = stage2c.run_stage2c(config)
    assert agg["stage_label"] == "d7_stage2c"
    assert agg["record_version"] == "1.0"
    assert agg["batch_uuid"] == stage2c.STAGE2C_BATCH_UUID


# ---------------------------------------------------------------------------
# 20. Per-call record schema (Stage 2c extension)
# ---------------------------------------------------------------------------


def test_per_call_record_contains_is_stage2b_overlap(tmp_config, monkeypatch):
    config, _ = tmp_config
    queue = [_critic_ok(cost=0.01) for _ in range(20)]
    it = iter(queue)
    monkeypatch.setattr(stage2c, "run_critic", lambda *a, **kw: next(it))
    stage2c.run_stage2c(config)
    # Candidate #1 is position 17 → overlap True.
    rec_1 = json.loads(
        (config.per_call_record_dir / "call_1_live_call_record.json").read_text(
            encoding="utf-8",
        ),
    )
    assert rec_1["is_stage2b_overlap"] is True
    assert rec_1["candidate_position"] == 17
    # Candidate #2 is position 22 → overlap False.
    rec_2 = json.loads(
        (config.per_call_record_dir / "call_2_live_call_record.json").read_text(
            encoding="utf-8",
        ),
    )
    assert rec_2["is_stage2b_overlap"] is False
    assert rec_2["candidate_position"] == 22

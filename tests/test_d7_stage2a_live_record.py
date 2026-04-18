"""Regression tests for D7 Stage 2a live-call record scan fields."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from agents.critic.batch_context import (
    DEFAULT_MOMENTUM_FACTORS,
    THEME_ANCHOR_FACTORS,
    THEME_HINTS,
    BatchContext,
)
from agents.critic.result import CriticResult
from strategies.dsl import StrategyDSL

import scripts.run_d7_stage2a_live as stage2a_live


def _make_dsl() -> StrategyDSL:
    return StrategyDSL.model_validate({
        "name": "record_scan_field_test",
        "description": "Momentum strategy for scan field record tests",
        "entry": [
            {"conditions": [{"factor": "rsi_14", "op": ">", "value": 30.0}]},
        ],
        "exit": [
            {"conditions": [{"factor": "rsi_14", "op": "<", "value": 70.0}]},
        ],
        "position_sizing": "full_equity",
        "max_hold_bars": 168,
    })


def _make_context() -> BatchContext:
    return BatchContext(
        prior_factor_sets=(("atr_14", "rsi_14"),),
        prior_hashes=("prior-hash",),
        batch_position=73,
        theme_hints=THEME_HINTS,
        default_momentum_factors=DEFAULT_MOMENTUM_FACTORS,
        theme_anchor_factors=THEME_ANCHOR_FACTORS,
    )


def _scan_results() -> dict:
    return {
        "forbidden_language_scan": {
            "status": "pass",
            "hits": [],
            "terms_checked_count": 21,
        },
        "refusal_scan": {
            "status": "pass",
            "hits": [],
            "patterns_checked": [r"\bi cannot\b"],
        },
    }


def _critic_result(status: str = "ok", scan_results: dict | None = None) -> CriticResult:
    d7b_ok = status in {"ok", "d7a_error"}
    return CriticResult(
        critic_version="d7_v1",
        critic_status=status,
        d7b_mode="stub",
        d7a_rule_scores={"theme_coherence": 0.5} if status != "d7a_error" else None,
        d7a_supporting_measures={},
        d7a_rule_flags=[],
        d7b_llm_scores={"semantic_plausibility": 0.5} if d7b_ok else None,
        d7b_reasoning="stub reasoning" if d7b_ok else None,
        d7b_raw_response_path=None,
        d7b_cost_actual_usd=0.0 if d7b_ok else None,
        d7b_input_tokens=0 if d7b_ok else None,
        d7b_output_tokens=0 if d7b_ok else None,
        d7b_retry_count=0,
        d7b_scan_results=scan_results if d7b_ok else None,
    )


@pytest.fixture
def patched_replay(monkeypatch, tmp_path):
    record_path = tmp_path / "stage2a_live_call_record.json"
    monkeypatch.setattr(stage2a_live, "LIVE_CALL_RECORD_PATH", record_path)
    monkeypatch.setattr(
        stage2a_live,
        "reconstruct_batch_context_at_position",
        lambda *args, **kwargs: (_make_dsl(), "momentum", _make_context()),
    )
    return record_path


def _run_with_result(monkeypatch, tmp_path, result: CriticResult) -> dict:
    monkeypatch.setattr(stage2a_live, "run_critic", lambda *args: result)
    stage2a_live.run_live(
        "5cf76668-47d1-48d7-bd90-db06d31982ed",
        73,
        confirm_live=False,
        artifacts_root=tmp_path / "raw_payloads",
        ledger_path=tmp_path / "ledger.db",
    )
    return json.loads((tmp_path / "stage2a_live_call_record.json").read_text())


def test_live_call_record_populates_scan_fields_on_ok_path(
    monkeypatch, tmp_path, patched_replay,
):
    record = _run_with_result(
        monkeypatch, tmp_path, _critic_result(scan_results=_scan_results()),
    )

    assert record["forbidden_language_scan_result"] == (
        _scan_results()["forbidden_language_scan"]
    )
    assert record["refusal_scan_result"] == _scan_results()["refusal_scan"]


def test_live_call_record_captures_structured_leakage_audit(
    monkeypatch, tmp_path, patched_replay,
):
    record = _run_with_result(
        monkeypatch, tmp_path, _critic_result(scan_results=_scan_results()),
    )

    leakage = record["leakage_audit_result"]
    assert isinstance(leakage, dict)
    assert leakage["status"] == "pass"
    assert leakage["violations"] == []
    assert leakage["protected_terms_checked_count"] > 0


def test_live_call_record_uses_not_reached_scan_results_on_d7b_error(
    monkeypatch, tmp_path, patched_replay,
):
    record = _run_with_result(
        monkeypatch, tmp_path, _critic_result(status="d7b_error"),
    )

    assert record["forbidden_language_scan_result"]["status"] == "not_reached"
    assert record["forbidden_language_scan_result"]["hits"] is None
    assert record["refusal_scan_result"]["status"] == "not_reached"
    assert record["refusal_scan_result"]["hits"] is None
    assert record["leakage_audit_result"]["status"] == "pass"


def test_live_call_record_scan_field_schema_regression_guard(
    monkeypatch, tmp_path, patched_replay,
):
    record = _run_with_result(
        monkeypatch, tmp_path, _critic_result(scan_results=_scan_results()),
    )

    for field in (
        "leakage_audit_result",
        "forbidden_language_scan_result",
        "refusal_scan_result",
    ):
        assert field in record
        assert isinstance(record[field], dict)
        assert record[field] is not None

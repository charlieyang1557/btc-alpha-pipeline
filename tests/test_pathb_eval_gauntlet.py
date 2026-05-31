# tests/test_pathb_eval_gauntlet.py
"""build_h1_dsl + EVAL_GAUNTLET stage->guard routing + Path B namespace."""
from __future__ import annotations

import pytest

import backtest.pathb_eval_gauntlet as eg
from strategies.dsl import StrategyDSL
from strategies.dsl_compiler import compile_dsl_to_strategy


def test_build_h1_dsl_uses_value_and_description_and_compiles():
    dsl = eg.build_h1_dsl()
    assert isinstance(dsl, StrategyDSL)
    assert len(dsl.description) >= 1            # description is REQUIRED
    cond = dsl.entry[0].conditions[0]
    assert hasattr(cond, "value")              # Condition uses value=, not threshold
    # The DSL must actually compile via the REAL compiler API.
    cls = compile_dsl_to_strategy(dsl, write_manifest=False)
    assert isinstance(cls, type)


def test_eval_gauntlet_routes_train_wf_to_wf_guard_and_rest_to_eval_guard():
    routing = eg.EVAL_GAUNTLET
    assert routing["train_wf"] == "check_wf_semantics_or_raise"
    for stage in ("regime_holdout_2022", "validation_2024", "tier5"):
        assert routing[stage] == "check_evaluation_semantics_or_raise"


def test_pathb_owns_its_namespace_not_the_sealed_cohort():
    assert eg.PATHB_EVAL_DIR.name == "pathb_eval_gauntlet_v1"
    assert "tier6_dsr_v1" not in eg.PATHB_EVAL_DIR.parts


def test_route_guard_dispatches_correct_callable(monkeypatch):
    seen = {}

    def fake_wf(summary, *, artifact_path=None):
        seen["wf"] = True

    def fake_eval(summary, *, artifact_path=None):
        seen["eval"] = True

    monkeypatch.setattr(eg, "check_wf_semantics_or_raise", fake_wf)
    monkeypatch.setattr(eg, "check_evaluation_semantics_or_raise", fake_eval)

    eg.route_guard("train_wf", {})
    eg.route_guard("tier5", {})
    assert seen == {"wf": True, "eval": True}


def test_route_guard_unknown_stage_raises():
    with pytest.raises(ValueError, match="unknown gauntlet stage"):
        eg.route_guard("nonexistent", {})

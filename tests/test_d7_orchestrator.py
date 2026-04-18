"""Tests for D7 orchestrator (run_critic), CriticResult, StubD7bBackend,
and reliability fuse scaffolding.

Covers:
    - CriticResult serialization round-trip
    - All status × mode combinations
    - Null-vs-zero distinction
    - StubD7bBackend determinism and magic prefix
    - run_critic() ok/d7a_error/d7b_error/both_error paths
    - Never-raises property (fuzz-style)
    - Reliability fuse counting and scaffold-only enforcement
"""

from __future__ import annotations

import random

import pytest

from factors.registry import get_registry
from strategies.dsl import StrategyDSL

from agents.critic.batch_context import (
    DEFAULT_MOMENTUM_FACTORS,
    THEME_ANCHOR_FACTORS,
    THEME_HINTS,
    BatchContext,
)
from agents.critic.d7b_backend import D7B_SCORE_KEYS, D7bBackend
from agents.critic.d7b_stub import (
    STUB_REASONING,
    STUB_REASONING_PREFIX,
    StubD7bBackend,
)
from agents.critic.orchestrator import (
    CRITIC_VERSION,
    compute_reliability_stats,
    run_critic,
    should_fuse_halt,
)
from agents.critic.result import CriticResult


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


@pytest.fixture
def reg():
    return get_registry()


def _make_dsl(
    entry: list | None = None,
    exit_: list | None = None,
    description: str = "test description",
    max_hold_bars: int | None = None,
    name: str = "test_strat",
) -> StrategyDSL:
    if entry is None:
        entry = [
            {"conditions": [{"factor": "sma_20", "op": ">", "value": 50000.0}]}
        ]
    if exit_ is None:
        exit_ = [
            {"conditions": [{"factor": "sma_20", "op": "<", "value": 45000.0}]}
        ]
    return StrategyDSL.model_validate({
        "name": name,
        "description": description,
        "entry": entry,
        "exit": exit_,
        "position_sizing": "full_equity",
        "max_hold_bars": max_hold_bars,
    })


def _make_ctx(
    prior_factor_sets: tuple[tuple[str, ...], ...] = (),
    prior_hashes: tuple[str, ...] = (),
    batch_position: int = 1,
) -> BatchContext:
    return BatchContext(
        prior_factor_sets=prior_factor_sets,
        prior_hashes=prior_hashes,
        batch_position=batch_position,
        theme_hints=THEME_HINTS,
        default_momentum_factors=DEFAULT_MOMENTUM_FACTORS,
        theme_anchor_factors=THEME_ANCHOR_FACTORS,
    )


class _FailingD7bBackend(D7bBackend):
    """D7b backend that always raises."""

    @property
    def mode(self):
        return "stub"

    def score(self, dsl, theme, batch_context):
        raise RuntimeError("D7b backend failure")


class _FailingD7aInducingBackend(D7bBackend):
    """Normal stub that doesn't fail — used with a monkeypatched D7a."""

    @property
    def mode(self):
        return "stub"

    def score(self, dsl, theme, batch_context):
        return StubD7bBackend().score(dsl, theme, batch_context)


# ---------------------------------------------------------------------------
# CriticResult
# ---------------------------------------------------------------------------


class TestCriticResult:
    def test_round_trip(self, reg):
        dsl = _make_dsl()
        ctx = _make_ctx()
        backend = StubD7bBackend()
        result = run_critic(dsl, "momentum", ctx, backend)
        d = result.to_dict()
        restored = CriticResult.from_dict(d)
        assert restored.critic_version == result.critic_version
        assert restored.critic_status == result.critic_status
        assert restored.d7b_mode == result.d7b_mode
        assert restored.d7a_rule_scores == result.d7a_rule_scores
        assert restored.d7a_rule_flags == result.d7a_rule_flags
        assert restored.d7b_llm_scores == result.d7b_llm_scores
        assert restored.d7b_reasoning == result.d7b_reasoning

    def test_null_vs_zero_distinction(self):
        result_none = CriticResult(
            critic_version="d7_v1",
            critic_status="d7a_error",
            d7b_mode="stub",
            d7a_rule_scores=None,
            d7a_supporting_measures={},
            d7a_rule_flags=[],
            d7b_llm_scores={"semantic_plausibility": 0.5,
                            "semantic_theme_alignment": 0.5,
                            "structural_variant_risk": 0.5},
            d7b_reasoning=STUB_REASONING,
            d7b_raw_response_path=None,
            d7b_cost_actual_usd=0.0,
            d7b_input_tokens=0,
            d7b_output_tokens=0,
            d7b_retry_count=0,
        )
        assert result_none.d7a_rule_scores is None
        d = result_none.to_dict()
        assert d["d7a_rule_scores"] is None

        result_zero = CriticResult(
            critic_version="d7_v1",
            critic_status="ok",
            d7b_mode="stub",
            d7a_rule_scores={"theme_coherence": 0.0,
                             "structural_novelty": 0.0,
                             "default_momentum_fallback": 0.0,
                             "complexity_appropriateness": 0.0},
            d7a_supporting_measures={},
            d7a_rule_flags=[],
            d7b_llm_scores={"semantic_plausibility": 0.5,
                            "semantic_theme_alignment": 0.5,
                            "structural_variant_risk": 0.5},
            d7b_reasoning=STUB_REASONING,
            d7b_raw_response_path=None,
            d7b_cost_actual_usd=0.0,
            d7b_input_tokens=0,
            d7b_output_tokens=0,
            d7b_retry_count=0,
        )
        d_zero = result_zero.to_dict()
        assert d_zero["d7a_rule_scores"] is not None
        assert all(v == 0.0 for v in d_zero["d7a_rule_scores"].values())

    def test_all_status_mode_combinations(self):
        statuses = ["ok", "d7a_error", "d7b_error", "both_error"]
        modes = ["stub", "live"]
        for status in statuses:
            for mode in modes:
                result = CriticResult(
                    critic_version="d7_v1",
                    critic_status=status,
                    d7b_mode=mode,
                    d7a_rule_scores=None,
                    d7a_supporting_measures={},
                    d7a_rule_flags=[],
                    d7b_llm_scores=None,
                    d7b_reasoning=None,
                    d7b_raw_response_path=None,
                    d7b_cost_actual_usd=None,
                    d7b_input_tokens=None,
                    d7b_output_tokens=None,
                    d7b_retry_count=0,
                )
                assert result.critic_status == status
                assert result.d7b_mode == mode

    def test_flags_always_list(self):
        result = CriticResult(
            critic_version="d7_v1",
            critic_status="ok",
            d7b_mode="stub",
            d7a_rule_scores={},
            d7a_supporting_measures={},
            d7a_rule_flags=[],
            d7b_llm_scores={},
            d7b_reasoning="",
            d7b_raw_response_path=None,
            d7b_cost_actual_usd=0.0,
            d7b_input_tokens=0,
            d7b_output_tokens=0,
            d7b_retry_count=0,
        )
        assert isinstance(result.d7a_rule_flags, list)


# ---------------------------------------------------------------------------
# StubD7bBackend
# ---------------------------------------------------------------------------


class TestStubD7bBackend:
    def test_mode_returns_stub(self):
        backend = StubD7bBackend()
        assert backend.mode == "stub"

    def test_deterministic_100_calls(self, reg):
        dsl = _make_dsl()
        ctx = _make_ctx()
        backend = StubD7bBackend()
        results = [backend.score(dsl, "momentum", ctx) for _ in range(100)]
        first = results[0]
        for r in results[1:]:
            assert r == first

    def test_reasoning_matches_constant(self, reg):
        dsl = _make_dsl()
        ctx = _make_ctx()
        backend = StubD7bBackend()
        _, reasoning, _ = backend.score(dsl, "momentum", ctx)
        assert reasoning == STUB_REASONING

    def test_reasoning_starts_with_prefix(self, reg):
        dsl = _make_dsl()
        ctx = _make_ctx()
        backend = StubD7bBackend()
        _, reasoning, _ = backend.score(dsl, "momentum", ctx)
        assert reasoning.startswith(STUB_REASONING_PREFIX)

    def test_score_keys_match(self, reg):
        dsl = _make_dsl()
        ctx = _make_ctx()
        backend = StubD7bBackend()
        scores, _, _ = backend.score(dsl, "momentum", ctx)
        assert set(scores.keys()) == set(D7B_SCORE_KEYS)

    def test_all_scores_are_0_5(self, reg):
        dsl = _make_dsl()
        ctx = _make_ctx()
        backend = StubD7bBackend()
        scores, _, _ = backend.score(dsl, "momentum", ctx)
        for v in scores.values():
            assert v == 0.5

    def test_metadata_shape(self, reg):
        dsl = _make_dsl()
        ctx = _make_ctx()
        backend = StubD7bBackend()
        _, _, metadata = backend.score(dsl, "momentum", ctx)
        assert metadata["raw_response_path"] is None
        assert metadata["cost_actual_usd"] == 0.0
        assert metadata["input_tokens"] == 0
        assert metadata["output_tokens"] == 0
        assert metadata["retry_count"] == 0


# ---------------------------------------------------------------------------
# run_critic
# ---------------------------------------------------------------------------


class TestRunCritic:
    def test_ok_path(self, reg):
        dsl = _make_dsl()
        ctx = _make_ctx()
        backend = StubD7bBackend()
        result = run_critic(dsl, "momentum", ctx, backend)
        assert result.critic_status == "ok"
        assert result.critic_version == CRITIC_VERSION
        assert result.d7b_mode == "stub"
        assert result.d7a_rule_scores is not None
        assert result.d7b_llm_scores is not None
        assert result.d7b_reasoning == STUB_REASONING
        assert result.d7b_cost_actual_usd == 0.0

    def test_d7b_error_path(self, reg):
        dsl = _make_dsl()
        ctx = _make_ctx()
        backend = _FailingD7bBackend()
        result = run_critic(dsl, "momentum", ctx, backend)
        assert result.critic_status == "d7b_error"
        assert result.d7a_rule_scores is not None
        assert result.d7b_llm_scores is None
        assert result.d7b_reasoning is None

    def test_d7a_error_path(self, reg, monkeypatch):
        import agents.critic.orchestrator as orch

        def _failing_score_d7a(dsl, theme, batch_context):
            raise ValueError("D7a rule failure")

        monkeypatch.setattr(orch, "score_d7a", _failing_score_d7a)
        dsl = _make_dsl()
        ctx = _make_ctx()
        backend = StubD7bBackend()
        result = run_critic(dsl, "momentum", ctx, backend)
        assert result.critic_status == "d7a_error"
        assert result.d7a_rule_scores is None
        assert result.d7b_llm_scores is not None

    def test_both_error_path(self, reg, monkeypatch):
        import agents.critic.orchestrator as orch

        def _failing_score_d7a(dsl, theme, batch_context):
            raise ValueError("D7a rule failure")

        monkeypatch.setattr(orch, "score_d7a", _failing_score_d7a)
        dsl = _make_dsl()
        ctx = _make_ctx()
        backend = _FailingD7bBackend()
        result = run_critic(dsl, "momentum", ctx, backend)
        assert result.critic_status == "both_error"
        assert result.d7a_rule_scores is None
        assert result.d7b_llm_scores is None

    def test_never_raises_fuzz(self, reg):
        """200 random inputs, assert no exception bubbles up."""
        all_factors = sorted(get_registry().list_names())
        themes = ["momentum", "mean_reversion", "volatility_regime",
                  "volume_divergence", "calendar_effect"]
        rng = random.Random(42)
        backend = StubD7bBackend()

        for _ in range(200):
            n_factors = rng.randint(1, 4)
            factors = rng.sample(all_factors, min(n_factors, len(all_factors)))
            entry_conds = [
                {"factor": f, "op": ">", "value": float(rng.randint(1, 100000))}
                for f in factors[:min(4, len(factors))]
            ]
            exit_conds = [
                {"factor": factors[0], "op": "<", "value": float(rng.randint(1, 100000))}
            ]
            desc = "x" * rng.randint(1, 300)
            name = f"fuzz_{rng.randint(0, 999999)}"
            dsl = StrategyDSL.model_validate({
                "name": name[:64],
                "description": desc,
                "entry": [{"conditions": entry_conds}],
                "exit": [{"conditions": exit_conds}],
                "position_sizing": "full_equity",
            })
            theme = rng.choice(themes)
            n_prior = rng.randint(0, 10)
            prior_fs = tuple(
                tuple(sorted(rng.sample(all_factors, rng.randint(1, 3))))
                for _ in range(n_prior)
            )
            ctx = _make_ctx(prior_factor_sets=prior_fs, batch_position=rng.randint(1, 200))
            result = run_critic(dsl, theme, ctx, backend)
            assert isinstance(result, CriticResult)
            assert result.critic_status in ("ok", "d7a_error", "d7b_error", "both_error")

    def test_timing_recorded(self, reg):
        dsl = _make_dsl()
        ctx = _make_ctx()
        backend = StubD7bBackend()
        result = run_critic(dsl, "momentum", ctx, backend)
        assert "d7a_ms" in result.critic_timing_ms
        assert "d7b_ms" in result.critic_timing_ms
        assert result.critic_timing_ms["d7a_ms"] >= 0
        assert result.critic_timing_ms["d7b_ms"] >= 0


# ---------------------------------------------------------------------------
# Reliability fuse
# ---------------------------------------------------------------------------


class TestReliabilityFuse:
    def test_compute_stats(self):
        stats = compute_reliability_stats(
            critic_ok_count=15,
            critic_d7a_error_count=3,
            critic_d7b_error_count=1,
            critic_both_error_count=1,
        )
        assert stats["critic_total_count"] == 20
        assert stats["critic_failure_count"] == 5
        assert stats["critic_failure_rate"] == 0.25
        assert stats["fuse_enforced"] is False

    def test_compute_stats_zero_total(self):
        stats = compute_reliability_stats(0, 0, 0, 0)
        assert stats["critic_total_count"] == 0
        assert stats["critic_failure_rate"] == 0.0

    def test_fuse_not_enforced_stage1(self):
        assert should_fuse_halt(20, 0.50) is False
        assert should_fuse_halt(50, 0.20) is False
        assert should_fuse_halt(100, 0.90) is False

    def test_injected_d7a_failures_counted(self, reg, monkeypatch):
        """Inject 5 D7a failures out of 20 calls, verify counts."""
        import agents.critic.orchestrator as orch

        call_count = {"n": 0}

        original_score_d7a = orch.score_d7a

        def _sometimes_failing_score_d7a(dsl, theme, batch_context):
            call_count["n"] += 1
            if call_count["n"] in {3, 7, 11, 15, 19}:
                raise ValueError("injected failure")
            return original_score_d7a(dsl, theme, batch_context)

        monkeypatch.setattr(orch, "score_d7a", _sometimes_failing_score_d7a)

        dsl = _make_dsl()
        ctx = _make_ctx()
        backend = StubD7bBackend()

        ok_count = 0
        d7a_err_count = 0
        d7b_err_count = 0
        both_err_count = 0

        for _ in range(20):
            result = run_critic(dsl, "momentum", ctx, backend)
            if result.critic_status == "ok":
                ok_count += 1
            elif result.critic_status == "d7a_error":
                d7a_err_count += 1
            elif result.critic_status == "d7b_error":
                d7b_err_count += 1
            elif result.critic_status == "both_error":
                both_err_count += 1

        assert d7a_err_count == 5
        assert ok_count == 15
        assert d7b_err_count == 0
        assert both_err_count == 0

        stats = compute_reliability_stats(
            ok_count, d7a_err_count, d7b_err_count, both_err_count,
        )
        assert stats["critic_failure_rate"] == 0.25
        assert not should_fuse_halt(stats["critic_total_count"],
                                     stats["critic_failure_rate"])

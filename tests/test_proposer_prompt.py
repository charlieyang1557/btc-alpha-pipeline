"""D6 Stage 1 — Proposer prompt builder + leakage audit.

The leakage audit is the single most important Stage 1 safety net: it
fails the build if any forbidden substring ever appears in a
constructed prompt across any synthetic context. Stage 2 (live Sonnet)
is gated on these tests passing.
"""

from __future__ import annotations

import pytest

from agents.proposer import BatchContext
from agents.proposer.prompt_builder import (
    FORBIDDEN_SUBSTRINGS,
    ProposerPrompt,
    THEMES,
    audit_prompt_for_leakage,
    build_prompt,
)
from factors.registry import get_registry


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def registry():
    return get_registry()


def _ctx(position: int, theme_slot: int, registry) -> BatchContext:
    return BatchContext(
        batch_id="00000000-0000-0000-0000-000000000001",
        position=position,
        batch_size=200,
        allowed_factors=tuple(registry.list_names()),
        allowed_operators=(
            "<", "<=", ">", ">=", "==", "crosses_above", "crosses_below",
        ),
        theme_slot=theme_slot,
    )


# ---------------------------------------------------------------------------
# Structure
# ---------------------------------------------------------------------------


def test_build_prompt_returns_three_part_prompt(registry):
    prompt = build_prompt(_ctx(1, 0, registry), registry=registry)
    assert isinstance(prompt, ProposerPrompt)
    assert prompt.system and prompt.user and prompt.factor_menu


def test_factor_menu_references_registered_factors_only(registry):
    prompt = build_prompt(_ctx(1, 0, registry), registry=registry)
    # Every line after the header mentions a registered factor name.
    names = set(registry.list_names())
    for line in prompt.factor_menu.splitlines():
        line = line.strip()
        if not line.startswith("- "):
            continue
        head = line[2:].split(" ", 1)[0]
        assert head in names, f"unregistered factor in menu: {head!r}"


def test_theme_slot_rotates_through_canonical_themes(registry):
    for slot in range(len(THEMES) * 2):
        prompt = build_prompt(_ctx(1, slot, registry), registry=registry)
        expected = THEMES[slot % len(THEMES)]
        assert f"theme (rotating): {expected}" in prompt.user


# ---------------------------------------------------------------------------
# Leakage audit — the hard safety net
# ---------------------------------------------------------------------------


def test_clean_prompt_has_empty_audit(registry):
    prompt = build_prompt(_ctx(1, 0, registry), registry=registry)
    assert audit_prompt_for_leakage(prompt) == []


def test_audit_detects_a_known_forbidden_substring():
    dirty = ProposerPrompt(
        system="You may use 2024-01 results as a reference.",
        user="",
        factor_menu="",
    )
    findings = audit_prompt_for_leakage(dirty)
    assert "2024-" in findings


def test_audit_is_case_insensitive():
    dirty = ProposerPrompt(
        system="Consider BEAR_2022 regime context.",
        user="",
        factor_menu="",
    )
    findings = audit_prompt_for_leakage(dirty)
    assert "bear_2022" in findings


def test_audit_detects_leaderboard_contamination():
    dirty = ProposerPrompt(
        system="",
        user="See the leaderboard for top performers.",
        factor_menu="",
    )
    assert "leaderboard" in audit_prompt_for_leakage(dirty)


def test_audit_clean_across_many_positions_and_themes(registry):
    for pos in (1, 7, 42, 199, 200):
        for slot in range(len(THEMES)):
            prompt = build_prompt(
                _ctx(pos, slot, registry),
                registry=registry,
                dedup_rate_so_far=0.37,
                critic_rejection_count_last_50=11,
                top_factors=("return_24h", "rsi_14", "volatility_24h"),
            )
            findings = audit_prompt_for_leakage(prompt)
            assert findings == [], f"leak at pos={pos} slot={slot}: {findings}"


def test_audit_clean_when_approved_examples_are_pure_dsl(registry):
    """DSL-only examples must not contain any leakage markers themselves.

    This pins the contract that callers must pre-strip examples; the
    builder does not redact.
    """
    dsl_example = (
        '{"name":"ex_1","description":"Enter on 24h return > 2%.",'
        '"entry":[{"conditions":[{"factor":"return_24h","op":">","value":0.02}]}],'
        '"exit":[{"conditions":[{"factor":"return_24h","op":"<","value":0.0}]}],'
        '"position_sizing":"full_equity","max_hold_bars":null}'
    )
    prompt = build_prompt(
        _ctx(1, 0, registry),
        registry=registry,
        approved_examples=(dsl_example,),
    )
    assert audit_prompt_for_leakage(prompt) == []


def test_forbidden_list_includes_all_phase2_leakage_surfaces():
    """If this test fails after a FORBIDDEN_SUBSTRINGS edit, the hard
    constraint in CLAUDE.md has been weakened — revisit review."""
    required_tokens = {
        "2022-", "2024-", "2025-",
        "bear_2022", "regime_holdout",
        "holdout_sharpe", "validation_sharpe", "test_sharpe",
        "leaderboard",
    }
    missing = required_tokens - set(FORBIDDEN_SUBSTRINGS)
    assert not missing, f"missing forbidden tokens: {missing}"

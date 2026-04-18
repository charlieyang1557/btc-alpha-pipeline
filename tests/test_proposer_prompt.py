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
    FORBIDDEN_PATTERNS,
    FORBIDDEN_SUBSTRINGS,
    ProposerPrompt,
    THEMES,
    audit_prompt_for_leakage,
    build_prompt,
)
from agents.themes import THEMES as THEMES_CANONICAL
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


def test_audit_detects_a_known_forbidden_pattern():
    dirty = ProposerPrompt(
        system="You may use 2024-01 results as a reference.",
        user="",
        factor_menu="",
    )
    findings = audit_prompt_for_leakage(dirty)
    assert any("2024" in f for f in findings)


def test_audit_is_case_insensitive():
    dirty = ProposerPrompt(
        system="Consider BEAR_2022 regime context.",
        user="",
        factor_menu="",
    )
    findings = audit_prompt_for_leakage(dirty)
    assert any("bear" in f for f in findings)


def test_audit_detects_leaderboard_contamination():
    dirty = ProposerPrompt(
        system="",
        user="See the leaderboard for top performers.",
        factor_menu="",
    )
    findings = audit_prompt_for_leakage(dirty)
    assert any("leaderboard" in f for f in findings)


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
    """If this test fails after a FORBIDDEN_PATTERNS edit, the hard
    constraint in CLAUDE.md has been weakened — revisit review."""
    joined = " ".join(FORBIDDEN_PATTERNS)
    for token in ("2022", "2024", "2025", "bear", "regime",
                  "holdout", "validation", "test",
                  "leaderboard", "pending", "dsr",
                  "out", "sample", "oos", "sharpe"):
        assert token in joined, f"missing coverage for {token!r}"


def test_themes_reexport_matches_canonical():
    """prompt_builder's THEMES must be the canonical agents.themes.THEMES."""
    assert THEMES is THEMES_CANONICAL


# ---------------------------------------------------------------------------
# Adversarial leakage cases (Issue 2 regression suite)
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Stage 2a calibration: concrete JSON example + synonym negative guidance
# ---------------------------------------------------------------------------
#
# Stage 2a's first live Sonnet response emitted plausible-wrong field names
# (``hypothesis_id`` instead of ``name``, ``entry_conditions`` instead of
# ``entry``, etc.) wrapped in a ```json fence. The prompt now carries an
# explicit positive schema block and an explicit negative synonym block.


def test_prompt_contains_concrete_example_and_negative_guidance(registry):
    prompt = build_prompt(_ctx(1, 0, registry), registry=registry)
    sys = prompt.system

    # Positive block: exact JSON shape header.
    assert (
        "Your output must be a JSON object matching EXACTLY this shape:" in sys
    )
    # Positive block: key field markers appear verbatim.
    assert '"name": "short_strategy_name"' in sys
    assert '"description": "one-sentence economic rationale"' in sys
    assert '"entry": [' in sys
    assert '"exit": [' in sys
    assert '"factor": "<factor_name>"' in sys
    assert '"op": "<operator>"' in sys
    assert '"value": <number or factor_name>' in sys
    assert '"position_sizing": "full_equity"' in sys
    assert '"max_hold_bars": <integer or null>' in sys

    # Negative block: header.
    assert (
        "Use these EXACT field names. Do NOT use synonyms or alternative "
        "names such as:"
    ) in sys
    # Negative block: each observed synonym enumerated.
    assert '"hypothesis_id" (use "name")' in sys
    assert '"entry_conditions" / "exit_conditions"' in sys
    assert '"left_factor" / "right_value"' in sys
    assert '"operator" (use "op")' in sys
    assert '"condition_group_id", "join_operator"' in sys
    # Negative block: no markdown fences.
    assert (
        "Respond with raw JSON only. Do NOT wrap the output in markdown "
        "code fences (triple backticks)."
    ) in sys


def test_leakage_audit_clean_on_new_prompt(registry):
    """The positive + negative blocks must not accidentally fire any
    forbidden leakage pattern."""
    prompt = build_prompt(_ctx(1, 0, registry), registry=registry)
    findings = audit_prompt_for_leakage(prompt)
    assert findings == [], (
        f"New prompt blocks leaked: {findings}. Review FORBIDDEN_PATTERNS "
        f"and/or the new system_lines text."
    )


@pytest.mark.parametrize(
    "snippet,should_fire",
    [
        # Year variants the old substring approach missed
        ("results from 2022:", True),
        ("year 2022.", True),
        ("(2022)", True),
        ("2022,Q1", True),
        ("in 2022\n", True),
        ('"2022"', True),
        ("2022\there", True),
        ("2024-01", True),
        ("2025 Q3", True),
        # Regime / holdout wording variants
        ("bear_2022", True),
        ("bear market data", True),
        ("bear regime signal", True),
        ("regime_holdout", True),
        ("holdout data", True),
        # OOS aliases
        ("out_of_sample sharpe", True),
        ("out-of-sample test", True),
        ("oos_sharpe", True),
        ("oos-return", True),
        # Metric name variants
        ("validation period", True),
        ("test period", True),
        ("pending_dsr", True),
        # Clean text that must NOT fire
        ("strategy #2023 is great", False),
        ("return_24h > 0.02", False),
        ("hypothesis testing framework", False),
        ("factor_momentum_30", False),
    ],
)
def test_adversarial_leakage_cases(snippet, should_fire):
    findings = audit_prompt_for_leakage(snippet)
    if should_fire:
        assert len(findings) > 0, f"expected leak for {snippet!r} but got none"
    else:
        assert len(findings) == 0, f"false positive for {snippet!r}: {findings}"

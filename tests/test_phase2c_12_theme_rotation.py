"""PHASE2C_12 Step 1 — theme rotation Q9 + Q10 implementation tests.

Covers:
    - Q9 smoke theme override (``theme_override`` parameter at
      ``_theme_for_position``)
    - Q9 R1 validation (invalid ``theme_override`` raises ``ValueError``)
    - Q10 ``PHASE2C_THEME_CYCLE_LEN`` env-var-driven ``THEME_CYCLE_LEN`` at
      module-load register
    - R3 unset-env fall-through preserves canonical 5-theme rotation

Test scope: both ``agents.proposer.stage2c_batch._theme_for_position`` AND
``agents.proposer.stage2d_batch._theme_for_position`` (separate code
surfaces per Q9/Q10 LOCKED implementation surface citations at
``PHASE2C_12_PLAN.md`` §11.8).

TDD-RED state: tests fail until Q9 + Q10 implementations land at
``stage2c_batch.py`` + ``stage2d_batch.py``.

Binding source: ``docs/phase2c/PHASE2C_12_PLAN.md`` §3.3 Q9 + Q10 LOCKED.
"""

from __future__ import annotations

import importlib

import pytest

from agents.themes import THEMES


MODULE_PATHS = [
    "agents.proposer.stage2c_batch",
    "agents.proposer.stage2d_batch",
]

ENV_THEME_CYCLE_LEN = "PHASE2C_THEME_CYCLE_LEN"
ENV_SMOKE_OVERRIDE = "PHASE2C_SMOKE_THEME_OVERRIDE"


@pytest.fixture
def reload_module(monkeypatch):
    """Reload a target module after mutating env vars.

    Returns a callable that takes a module path and returns the freshly
    reloaded module. Both PHASE2C env vars are cleared on entry to avoid
    cross-test contamination, and the modules are reloaded on teardown
    so canonical state (THEME_CYCLE_LEN=5) is restored for downstream
    tests in the same pytest session.
    """
    monkeypatch.delenv(ENV_THEME_CYCLE_LEN, raising=False)
    monkeypatch.delenv(ENV_SMOKE_OVERRIDE, raising=False)

    def _reload(module_path: str):
        mod = importlib.import_module(module_path)
        return importlib.reload(mod)

    yield _reload

    monkeypatch.delenv(ENV_THEME_CYCLE_LEN, raising=False)
    monkeypatch.delenv(ENV_SMOKE_OVERRIDE, raising=False)
    for mp in MODULE_PATHS:
        importlib.reload(importlib.import_module(mp))


@pytest.mark.parametrize("module_path", MODULE_PATHS)
def test_theme_for_position_canonical_5theme_rotation(
    module_path, reload_module
):
    """R3 fall-through: unset env vars preserve canonical 5-theme rotation.

    Verifies:
        - ``THEME_CYCLE_LEN`` defaults to 5 (Stage 2c/2d operational
          invariant)
        - ``_theme_for_position(k)`` cycles through first 5 THEMES
        - ``multi_factor_combination`` NOT in default rotation
    """
    mod = reload_module(module_path)
    assert mod.THEME_CYCLE_LEN == 5
    counts: dict[str, int] = {}
    for k in range(1, 21):
        t = mod._theme_for_position(k)
        counts[t] = counts.get(t, 0) + 1
    assert all(v == 4 for v in counts.values())
    assert "multi_factor_combination" not in counts
    # k=1..5 enumerates first 5 THEMES exactly once.
    assert [mod._theme_for_position(k) for k in range(1, 6)] == list(
        THEMES[:5]
    )


@pytest.mark.parametrize("module_path", MODULE_PATHS)
def test_theme_for_position_main_6theme_rotation(
    module_path, monkeypatch, reload_module
):
    """Q10: ``PHASE2C_THEME_CYCLE_LEN=6`` enables 6-theme rotation
    including ``multi_factor_combination``.

    PHASE2C_12 main batch fire register: 33 candidates per theme × 6
    themes = 198 clean integer distribution per Q6 LOCKED.
    """
    monkeypatch.setenv(ENV_THEME_CYCLE_LEN, "6")
    mod = reload_module(module_path)
    assert mod.THEME_CYCLE_LEN == 6
    counts: dict[str, int] = {}
    for k in range(1, 199):
        t = mod._theme_for_position(k)
        counts[t] = counts.get(t, 0) + 1
    # 198 / 6 = 33 candidates per theme exactly.
    assert all(v == 33 for v in counts.values())
    assert len(counts) == 6
    assert "multi_factor_combination" in counts
    assert counts["multi_factor_combination"] == 33
    # k=1..6 enumerates all 6 THEMES exactly once.
    assert [mod._theme_for_position(k) for k in range(1, 7)] == list(THEMES)


@pytest.mark.parametrize("module_path", MODULE_PATHS)
def test_theme_for_position_smoke_override(
    module_path, monkeypatch, reload_module
):
    """Q9: ``theme_override`` returns the override regardless of ``k`` AND
    regardless of ``THEME_CYCLE_LEN``.

    Cross-product check: override stable under both default 5-theme
    rotation register and PHASE2C_12 6-theme rotation register.
    """
    mod = reload_module(module_path)
    # Default 5-theme rotation register.
    for k in range(1, 41):
        assert mod._theme_for_position(
            k, theme_override="multi_factor_combination"
        ) == "multi_factor_combination"

    # 6-theme rotation register (Q9 × Q10 cross-product).
    monkeypatch.setenv(ENV_THEME_CYCLE_LEN, "6")
    mod = reload_module(module_path)
    for k in range(1, 41):
        assert mod._theme_for_position(
            k, theme_override="momentum"
        ) == "momentum"


@pytest.mark.parametrize("module_path", MODULE_PATHS)
def test_theme_for_position_invalid_override_raises(
    module_path, reload_module
):
    """Q9 R1 validation: ``theme_override`` not in canonical ``THEMES``
    tuple raises ``ValueError``.

    Anti-fishing-license boundary at theme-content register-precision
    (only canonical THEMES members accepted; case-sensitive; empty
    string rejected).
    """
    mod = reload_module(module_path)
    with pytest.raises(ValueError, match="not in canonical THEMES"):
        mod._theme_for_position(1, theme_override="not_a_theme")
    with pytest.raises(ValueError, match="not in canonical THEMES"):
        mod._theme_for_position(1, theme_override="MULTI_FACTOR_COMBINATION")
    with pytest.raises(ValueError, match="not in canonical THEMES"):
        mod._theme_for_position(1, theme_override="")


# ---------------------------------------------------------------------------
# Codex first-fire hotfix tests (Findings #2 + #3 + #4)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("module_path", MODULE_PATHS)
def test_resolve_smoke_theme_override_unset_returns_none(
    module_path, reload_module
):
    """Codex Finding #2 PARTIAL ADOPT: env var unset → ``None``
    (R3 canonical-rotation fall-through preserved)."""
    mod = reload_module(module_path)
    assert mod._resolve_smoke_theme_override() is None


@pytest.mark.parametrize("module_path", MODULE_PATHS)
def test_resolve_smoke_theme_override_empty_raises(
    module_path, monkeypatch, reload_module
):
    """Codex Finding #2 PARTIAL ADOPT: env var set to empty string →
    ``ValueError`` (anti-fishing-license at malformed-config register).
    """
    monkeypatch.setenv(ENV_SMOKE_OVERRIDE, "")
    mod = reload_module(module_path)
    with pytest.raises(ValueError, match="empty/whitespace"):
        mod._resolve_smoke_theme_override()


@pytest.mark.parametrize("module_path", MODULE_PATHS)
def test_resolve_smoke_theme_override_whitespace_raises(
    module_path, monkeypatch, reload_module
):
    """Codex Finding #2 PARTIAL ADOPT: env var set to whitespace-only
    string → ``ValueError`` (post-``strip()`` empty)."""
    monkeypatch.setenv(ENV_SMOKE_OVERRIDE, "   ")
    mod = reload_module(module_path)
    with pytest.raises(ValueError, match="empty/whitespace"):
        mod._resolve_smoke_theme_override()


@pytest.mark.parametrize("module_path", MODULE_PATHS)
def test_resolve_smoke_theme_override_valid_returns_value(
    module_path, monkeypatch, reload_module
):
    """Codex Finding #2 PARTIAL ADOPT: env var set to non-empty string
    → returns value verbatim. Validation against THEMES is deferred to
    ``_theme_for_position`` (helper does NOT validate THEMES membership;
    this is intentional separation of responsibilities)."""
    monkeypatch.setenv(ENV_SMOKE_OVERRIDE, "multi_factor_combination")
    mod = reload_module(module_path)
    assert mod._resolve_smoke_theme_override() == "multi_factor_combination"


@pytest.mark.parametrize(
    "bad_value",
    ["0", "-1", "-3", "7", "100"],
)
@pytest.mark.parametrize("module_path", MODULE_PATHS)
def test_theme_cycle_len_range_validation_raises(
    bad_value, module_path, monkeypatch, reload_module
):
    """Codex Finding #3 ADOPT: ``PHASE2C_THEME_CYCLE_LEN`` outside
    ``[1, len(THEMES)=6]`` raises ``ValueError`` at module-load
    register (fail-fast bound)."""
    monkeypatch.setenv(ENV_THEME_CYCLE_LEN, bad_value)
    with pytest.raises(ValueError, match="out of range"):
        reload_module(module_path)


@pytest.mark.parametrize("module_path", MODULE_PATHS)
def test_theme_cycle_len_range_validation_non_integer_raises(
    module_path, monkeypatch, reload_module
):
    """Codex Finding #3 ADOPT: non-integer ``PHASE2C_THEME_CYCLE_LEN``
    raises ``ValueError`` at module-load register."""
    monkeypatch.setenv(ENV_THEME_CYCLE_LEN, "five")
    with pytest.raises(ValueError, match="not a valid integer"):
        reload_module(module_path)


@pytest.mark.parametrize(
    "good_value", ["1", "2", "3", "4", "5", "6"],
)
@pytest.mark.parametrize("module_path", MODULE_PATHS)
def test_theme_cycle_len_range_validation_in_bounds_loads(
    good_value, module_path, monkeypatch, reload_module
):
    """Codex Finding #3 ADOPT: ``PHASE2C_THEME_CYCLE_LEN`` inside
    ``[1, len(THEMES)=6]`` loads without raising (defensive-but-not-
    prescriptive bound; anti-pre-naming preserved at validation
    register-precision)."""
    monkeypatch.setenv(ENV_THEME_CYCLE_LEN, good_value)
    mod = reload_module(module_path)
    assert mod.THEME_CYCLE_LEN == int(good_value)


# ---------------------------------------------------------------------------
# Prompt-LLM-visible integration tests (Codex Finding #1 + #4)
#
# These tests close the register-class-eligibility-skip surfaced by
# Codex Finding #1: direct ``_theme_for_position`` tests verify the
# telemetry register only; the prompt-LLM-visible register requires
# end-to-end verification at ``build_prompt()`` register.
# ---------------------------------------------------------------------------


def _build_smoke_context(
    *, position: int, theme_slot: int, theme_override: str | None,
):
    """Construct a minimal BatchContext for build_prompt() integration."""
    from agents.proposer.interface import BatchContext

    return BatchContext(
        batch_id="test-batch",
        position=position,
        batch_size=40,
        allowed_factors=("close", "rsi_14"),
        allowed_operators=("<", ">", "crosses_above", "crosses_below"),
        theme_slot=theme_slot,
        theme_override=theme_override,
    )


def test_build_prompt_smoke_override_visible_in_prompt():
    """Codex Finding #1 ADOPT: when ``theme_override`` is set on
    BatchContext, ``build_prompt()`` injects the override theme into
    the prompt-LLM-visible register regardless of ``theme_slot`` rotation
    position. This is the load-bearing prevention discipline at smoke
    fire register-precision (Q9 LOCKED at PHASE2C_12_PLAN.md §3.3 +
    §4.1)."""
    from agents.proposer.prompt_builder import build_prompt

    # Iterate across rotation positions; override should win at every k.
    for k in range(1, 41):
        ctx = _build_smoke_context(
            position=k,
            theme_slot=(k - 1) % 5,
            theme_override="multi_factor_combination",
        )
        prompt = build_prompt(ctx)
        assert "theme (rotating): multi_factor_combination" in prompt.user, (
            f"prompt at position k={k} did not surface override theme; "
            f"prompt.user starts: {prompt.user[:300]!r}"
        )


def test_build_prompt_canonical_rotation_when_override_unset():
    """Codex Finding #4 ADOPT: with ``theme_override=None``,
    ``build_prompt()`` falls through to canonical ``theme_slot``
    rotation (R3 fall-through preserved at integration register)."""
    from agents.proposer.prompt_builder import build_prompt

    ctx = _build_smoke_context(
        position=1, theme_slot=0, theme_override=None,
    )
    prompt = build_prompt(ctx)
    assert "theme (rotating): momentum" in prompt.user
    # k=2 → theme_slot=1 → mean_reversion under default 5-rotation.
    ctx_k2 = _build_smoke_context(
        position=2, theme_slot=1, theme_override=None,
    )
    prompt_k2 = build_prompt(ctx_k2)
    assert "theme (rotating): mean_reversion" in prompt_k2.user


def test_build_prompt_override_supersedes_theme_slot_telemetry_preserved():
    """Codex Finding #1 ADOPT: ``theme_slot`` remains pure rotation-
    position metadata even when ``theme_override`` is active. The
    prompt-visible theme reflects the override; the BatchContext
    object retains the rotation slot for telemetry/audit-trail."""
    ctx = _build_smoke_context(
        position=7, theme_slot=2, theme_override="multi_factor_combination",
    )
    # Telemetry register (BatchContext fields) preserved independently.
    assert ctx.theme_slot == 2
    assert ctx.theme_override == "multi_factor_combination"

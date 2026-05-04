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

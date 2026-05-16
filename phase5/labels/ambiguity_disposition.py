"""§3.2 Diagnostic ambiguity disposition — Case A condition + terminal-trigger.

Sealed prose at docs/phase5/PHASE5_DIAGNOSTIC_SUBSPEC.md §3.2 (sealed at
ef770be; D3''''''^b lock). δ hybrid framing analog at §3.2 narrowed register;
single-case Case A scope; XOR complementarity with §3.1 firing pattern.
"""

from __future__ import annotations

from typing import Any


def evaluate_case_a(
    detections: dict[str, bool | None],
    nan_modes: list[str] | None = None,
    suspended_modes: list[str] | None = None,
) -> dict[str, Any]:
    """Evaluate §3.2 Case A condition + emit {label, terminal_trigger}.

    Case A condition: all 6 §2.x mode outputs are canonical binary AND resolve
    to `not-detected`. Any §2.x-self-suspended or (ε'-narrow)-class-real-data-NaN
    state routes to edge-handling branch (NaN-handling rule section per
    sealed §3.2).

    Returns dict with:
      - label: str | None  ("no-mode-detected reading" if Case A fires;
        "indeterminate-Case-A reading" if NaN propagation; None if §3.2 silent
        per XOR complementarity with §3.1)
      - terminal_trigger: structured object per sealed §3.2 D2''''''^b
      - execution_suspended: bool
    """
    nan_modes = sorted(nan_modes or [])
    suspended_modes = sorted(suspended_modes or [])
    expected_modes = {
        "signal_decay",
        "cost_drag",
        "cohort_weakness",
        "andgate_overfit",
        "success_metric_mismatch",
        "regime_change",
    }
    if set(detections.keys()) != expected_modes:
        return {
            "label": None,
            "terminal_trigger": None,
            "execution_suspended": True,
            "suspension_cause": "input_space_canonical_check_failed",
            "expected_modes": sorted(expected_modes),
            "actual_modes": sorted(detections.keys()),
            "narrative_anchor": (
                "§3.2 execution suspends per (ε') execution-invalidity branch; "
                "§6 enumerates the discrepancy; Charlie register re-adjudicates "
                "per §2.d D2''' / §2.f parquet-mismatch suspension precedent"
            ),
        }

    if suspended_modes:
        return {
            "label": None,
            "terminal_trigger": None,
            "execution_suspended": True,
            "suspension_cause": "upstream_§2.x_self_suspended",
            "suspended_modes": suspended_modes,
            "narrative_anchor": (
                "§3.2 execution suspends per (ε') execution-invalidity branch; "
                "§6 enumerates the discrepancy; Charlie register re-adjudicates "
                "per §2.d D2''' / §2.f parquet-mismatch suspension precedent"
            ),
        }

    if nan_modes:
        return {
            "label": "indeterminate-Case-A reading",
            "terminal_trigger": {
                "triggered": False,
                "basis": {
                    "canonical_0_mode": False,
                    "suspended_modes": suspended_modes,
                    "nan_modes": nan_modes,
                },
            },
            "execution_suspended": False,
            "register_class": "binding | procedural-state | (ε'-narrow) indeterminate-Case-A",
        }

    # All 6 §2.x outputs are canonical binary. Check Case A condition.
    firing_modes = [m for m, d in detections.items() if d is True]
    if len(firing_modes) >= 1:
        # §3.1 fires; §3.2 silent per XOR complementarity sealed property.
        return {
            "label": None,
            "terminal_trigger": None,
            "execution_suspended": False,
            "silent_state": True,
            "reason_silent": (
                "≥1 §2.x at canonical detected register; §3.1 emits labels per "
                "its register-class; §3.2 emits no substantive output per XOR "
                "complementarity sealed property"
            ),
            "firing_modes": sorted(firing_modes),
        }

    # Case A condition satisfied — all 6 §2.x not-detected at canonical binary register.
    return {
        "label": "no-mode-detected reading",
        "terminal_trigger": {
            "triggered": True,
            "basis": {
                "canonical_0_mode": True,
                "suspended_modes": [],
                "nan_modes": [],
            },
        },
        "execution_suspended": False,
        "register_class": "binding | procedural-state | Case A condition satisfied",
        "narrative_anchor": (
            "Case A: all 6 §2.x not-detected at canonical binary register; §3.2 "
            "emits separate-field output {label, terminal_trigger}; substantive "
            "narrative determination of what Case A occurrence means is §6 author "
            "register scope per anti-circularity (iii)"
        ),
    }

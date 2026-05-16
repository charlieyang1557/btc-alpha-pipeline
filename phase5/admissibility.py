"""§5 Substantive-vs-operational admissibility flagging.

Sealed prose at docs/phase5/PHASE5_DIAGNOSTIC_SUBSPEC.md §5 (lines 675-836,
D''''''^e lock-set). Fixed-shape 2-slot output per D1.1 β'-fixed-shape lock.
D2.1 α HARD LOCK substantive ⟺ §3.2 Case A canonical state.
D2.2 1-CASE α LOCK operational ⟺ CASE 1 §4a residual ambiguity.
NaN-propagation evaluation precedes canonical D2.1/D2.2 evaluation per sealed
line 754 (short-circuit precedence).

Admissibility ≠ selection / invocation (anti-circularity (x); Phase 5 SEAL
author register retains terminal-conclusion invocation authority).
"""

from __future__ import annotations

from typing import Any

# Sealed §2.5 verbatim source language for basis fields (per §5 D1.2 4-field schema lock).
SUBSTANTIVE_ADMIT_BASIS = (
    "the AND-gate paradigm is likely exhausted for deployable BTC alpha under realistic costs"
)
OPERATIONAL_ADMIT_BASIS_PREFIX = (
    "Phase 5 is permitted to conclude that no successor empirical cycle is currently justified"
)
NOT_ADMIT_BASIS = "criteria not satisfied at canonical execution"


def _slot(availability_type: str, admissible: Any, basis: str, propagation_state: str) -> dict[str, Any]:
    """Build fixed-shape 4-field slot object per D1.2 lock."""
    return {
        "availability_type": availability_type,
        "admissible": admissible,
        "basis": basis,
        "propagation_state": propagation_state,
    }


def _both_slots_null(propagation_state: str, basis: str) -> dict[str, Any]:
    """Emit both substantive + operational slots with admissible=null per propagation_state."""
    return {
        "register": "§5 substantive-vs-operational admissibility",
        "substantive": _slot("substantive", None, basis, propagation_state),
        "operational": _slot("operational", None, basis, propagation_state),
    }


def _is_case_a_canonical(case_a_result: dict[str, Any]) -> bool:
    """Check sealed §5 D2.1 5-condition substantive admissibility criterion."""
    if case_a_result.get("label") != "no-mode-detected reading":
        return False
    tt = case_a_result.get("terminal_trigger")
    if not isinstance(tt, dict):
        return False
    if tt.get("triggered") is not True:
        return False
    basis = tt.get("basis")
    if not isinstance(basis, dict):
        return False
    return (
        basis.get("canonical_0_mode") is True
        and basis.get("suspended_modes") == []
        and basis.get("nan_modes") == []
    )


def _is_silent_state_or_terminal_trigger_false(case_a_result: dict[str, Any]) -> bool:
    """Sealed §5 line 734: silent state semantically equivalent to terminal_trigger=False at §5 consumption register."""
    if case_a_result.get("silent_state") is True:
        return True
    tt = case_a_result.get("terminal_trigger")
    if isinstance(tt, dict) and tt.get("triggered") is False:
        return True
    return False


def _distinct_unresolved_assignment_count(successor_class_result: dict[str, Any]) -> int:
    """Count distinct successor-cycle-class assignments at §4a output (post §4a-internal precedence)."""
    assignments = successor_class_result.get("assignments")
    if not isinstance(assignments, list):
        return 0
    # Exclude indeterminate-cycle-class entries from the count (those are not resolved successor classes).
    distinct_classes = {
        a["class"]
        for a in assignments
        if a.get("class") and a["class"] != "indeterminate-cycle-class"
    }
    return len(distinct_classes)


def flag_admissibility(
    multi_mode_result: dict[str, Any],
    case_a_result: dict[str, Any],
    successor_class_result: dict[str, Any],
    framing_pressure_result: dict[str, Any],
) -> dict[str, Any]:
    """§5 admissibility flagging per sealed sub-spec.

    Consumes §3.1 + §3.2 + §4a + §4b sealed outputs at canonical register.
    Emits fixed-shape 2-slot output {substantive, operational} per D1.1 β'-fixed-shape lock.
    NaN-propagation short-circuit precedes canonical D2.1/D2.2 evaluation per sealed line 754.
    """
    # (ε') execution-invalidity branch — highest precedence per sealed NaN-handling.
    if (
        multi_mode_result.get("execution_suspended")
        or case_a_result.get("execution_suspended")
        or successor_class_result.get("execution_suspended")
        or framing_pressure_result.get("execution_suspended")
    ):
        if multi_mode_result.get("execution_suspended"):
            upstream = "§3.1"
        elif case_a_result.get("execution_suspended"):
            upstream = "§3.2"
        elif successor_class_result.get("execution_suspended"):
            upstream = "§4a"
        else:
            upstream = "§4b"
        return _both_slots_null(
            "execution-suspended-from-upstream",
            f"upstream {upstream} execution suspended",
        )

    # NaN-propagation short-circuit per sealed line 754 (precedes canonical D2.1/D2.2 evaluation).
    upstream_indeterminate = bool(
        multi_mode_result.get("indeterminate_labels")
        or case_a_result.get("label") == "indeterminate-Case-A reading"
    )
    if upstream_indeterminate:
        # Source of indeterminacy for basis field.
        if case_a_result.get("label") == "indeterminate-Case-A reading":
            basis = "indeterminate-Case-A reading"
        else:
            indet_keys = sorted((multi_mode_result.get("indeterminate_labels") or {}).keys())
            basis = f"upstream §3.1 indeterminate at modes: {', '.join(indet_keys)}"
        return _both_slots_null("upstream-indeterminacy-propagated", basis)

    # Canonical D2.1 substantive admissibility evaluation.
    if _is_case_a_canonical(case_a_result):
        substantive = _slot("substantive", True, SUBSTANTIVE_ADMIT_BASIS, "active")
    else:
        substantive = _slot("substantive", False, NOT_ADMIT_BASIS, "active")

    # Canonical D2.2 CASE 1 operational admissibility evaluation.
    silent_or_terminal_false = _is_silent_state_or_terminal_trigger_false(case_a_result)
    distinct_count = _distinct_unresolved_assignment_count(successor_class_result)
    operational_admissible = silent_or_terminal_false and distinct_count >= 2

    if operational_admissible:
        unresolved_classes = sorted(
            {
                a["class"]
                for a in successor_class_result.get("assignments", [])
                if a.get("class") and a["class"] != "indeterminate-cycle-class"
            }
        )
        operational_basis = (
            f"{OPERATIONAL_ADMIT_BASIS_PREFIX} "
            f"(§4a unresolved successor-cycle-class set: {unresolved_classes})"
        )
        operational = _slot("operational", True, operational_basis, "active")
    else:
        operational = _slot("operational", False, NOT_ADMIT_BASIS, "active")

    # Mechanical-routing provenance per ChatGPT structural-overlay MEDIUM-3 fix
    # (non-interpretive; exposes WHICH case condition triggered the admissibility flag
    # for machine-readable downstream auditability without interpretive narration).
    provenance = {
        "substantive_evaluated_case": "D2.1_case_a_canonical_5_condition_check",
        "substantive_case_a_canonical_check_passed": _is_case_a_canonical(case_a_result),
        "operational_evaluated_case": "D2.2_CASE_1_residual_ambiguity_check",
        "operational_case_1_silent_or_terminal_false": silent_or_terminal_false,
        "operational_distinct_assignment_count": distinct_count,
        "operational_case_1_threshold": 2,
    }

    return {
        "register": "§5 substantive-vs-operational admissibility",
        "substantive": substantive,
        "operational": operational,
        "mechanical_routing_provenance": provenance,
    }

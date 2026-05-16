"""§4b Framing-question resolution-pressure assessment.

Sealed prose at docs/phase5/PHASE5_DIAGNOSTIC_SUBSPEC.md §4b (lines 556-674,
D''''''^d lock-set). β union-of-labels composite emission. Per-finding 6-field
schema: {pressure_label, pivot_direction_dependency, basis, propagation_state,
context_qualifiers, finding_source}.

procedure ≠ resolution discipline (advisor Refinement 1 critical distinction).
§4b emits pressure labels only; framing-question RESOLUTION is Phase 5 SEAL
author register scope per scoping §2.4.

Downstream consumer note (per ChatGPT structural-overlay MEDIUM-2): the
`deferred` pressure_label is **suspended-state pressure under indeterminate
framing**, NOT equivalent to resolved / nullified / inactive pressure. Co-occurs
with `propagation_state="active"` to indicate still-live pressure that defers
framing-question engagement (per sealed §2.4 (a)/(b) verbatim). Distinguish
from `propagation_state="upstream-indeterminacy-propagated"` (epistemic
indeterminacy from upstream NaN; pressure_label=null) and
`propagation_state="execution-suspended-from-upstream"` (infrastructure
suspension from upstream (ε') execution-invalidity branch; pressure_label=null).
"""

from __future__ import annotations

from typing import Any

from phase5.successor_class import (
    LINE1_FORWARD_APPLICABILITY_RECIPIENTS,
    LINE1_REGIME_CONDITIONAL_RECIPIENTS,
)

# Single-finding pressure mapping table (sealed §4b lines 577-584, verbatim
# scoping §2.4 source language). Tuple: (pressure_label, pivot_direction_dependency, basis).
SINGLE_FINDING_PRESSURE: dict[str, tuple[str, str, str]] = {
    "signal_decay": (
        "deferred",
        "none",
        (
            "framing question can stay deferred under (4) indeterminate; "
            "empirically-conditioned continuation defensible under any framing"
        ),
    ),
    "cost_drag": (
        "deferred",
        "none",
        (
            "framing question can stay deferred under (4) indeterminate; "
            "empirically-conditioned continuation defensible under any framing"
        ),
    ),
    "cohort_weakness": (
        "load-bearing-at-Phase-5-SEAL",
        "depends-on-framing",
        (
            "framing question becomes load-bearing at Phase 5 SEAL; "
            "pivot direction depends on framing; "
            "Charlie register engagement required at successor cycle entry"
        ),
    ),
    "andgate_overfit": (
        "load-bearing-at-Phase-5-SEAL",
        "depends-on-framing",
        (
            "framing question becomes load-bearing at Phase 5 SEAL; "
            "pivot direction depends on framing; "
            "Charlie register engagement required at successor cycle entry"
        ),
    ),
    "success_metric_mismatch": (
        "ambiguous",
        "implicit-via-Phase-5-SEAL-surfacing",
        "ambiguous; Phase 5 SEAL surfaces framing engagement explicitly",
    ),
    "regime_change": (
        "load-bearing",
        "depends-on-framing-substantively",
        (
            "framing question becomes load-bearing; pivot direction substantively "
            "determined by framing"
        ),
    ),
}

# Terminal-conclusion finding pressure (sealed §4b line 584 + Case A mapping at line 597).
TERMINAL_CONCLUSION_PRESSURE: tuple[str, str, str] = (
    "load-bearing-immediately",
    "project-identity-engagement-implicit",
    (
        "Terminal-conclusion finding (per §2.5) → framing question becomes "
        "load-bearing immediately; engages directly with project-identity question"
    ),
)

# §2.X register identifier per sealed §2.x naming.
MODE_TO_SECTION: dict[str, str] = {
    "signal_decay": "§2.a",
    "cost_drag": "§2.b",
    "cohort_weakness": "§2.c",
    "andgate_overfit": "§2.d",
    "success_metric_mismatch": "§2.e",
    "regime_change": "§2.f",
}

def _extract_context_qualifiers(mode: str, firing_modes: list[str]) -> list[str]:
    """Extract structural composition qualifiers per sealed §4b D2.5 β qualifier-as-context.

    Carries qualifiers as `context_qualifiers` field without altering
    `pressure_label` per sealed §4b qualifier-stripping rule (case routing
    operates on raw §2.x finding type only). Qualifier-scope constants
    imported from `phase5.successor_class` to keep §4a / §4b single-source.
    """
    regime_fires = "regime_change" in firing_modes
    andgate_fires = "andgate_overfit" in firing_modes
    qualifiers: list[str] = []
    if regime_fires and mode != "regime_change":
        if mode in LINE1_REGIME_CONDITIONAL_RECIPIENTS:
            qualifiers.append("regime-conditional")
        elif mode in LINE1_FORWARD_APPLICABILITY_RECIPIENTS:
            qualifiers.append("forward-applicability-conditioned")
    if mode == "cohort_weakness" and andgate_fires:
        qualifiers.append("gate-validity-conditioned")
    return qualifiers


def _firing_finding_object(mode: str, firing_modes: list[str]) -> dict[str, Any]:
    """Build 6-field schema object for a firing §2.x finding."""
    pressure_label, pivot_dep, basis = SINGLE_FINDING_PRESSURE[mode]
    return {
        "pressure_label": pressure_label,
        "pivot_direction_dependency": pivot_dep,
        "basis": basis,
        "propagation_state": "active",
        "context_qualifiers": _extract_context_qualifiers(mode, firing_modes),
        "finding_source": MODE_TO_SECTION[mode],
    }


def _indeterminate_finding_object(mode: str, label: str) -> dict[str, Any]:
    """Build upstream-indeterminacy-propagated 6-field object for a §3.1 indeterminate mode."""
    return {
        "pressure_label": None,
        "pivot_direction_dependency": None,
        "basis": label,
        "propagation_state": "upstream-indeterminacy-propagated",
        "context_qualifiers": [],
        "finding_source": MODE_TO_SECTION.get(mode, mode),
    }


def _terminal_conclusion_object() -> dict[str, Any]:
    """Build terminal-conclusion scalar pressure object per sealed §4b Case A mapping."""
    pressure_label, pivot_dep, basis = TERMINAL_CONCLUSION_PRESSURE
    return {
        "pressure_label": pressure_label,
        "pivot_direction_dependency": pivot_dep,
        "basis": basis,
        "propagation_state": "active",
        "context_qualifiers": [],
        "finding_source": "terminal-conclusion",
    }


def assess_framing_pressure(
    multi_mode_result: dict[str, Any],
    case_a_result: dict[str, Any],
    successor_class_result: dict[str, Any],
) -> dict[str, Any]:
    """§4b framing-question resolution-pressure assessment per sealed sub-spec.

    Consumes §3.1 multi_mode_result + §3.2 case_a_result + §4a successor_class_result
    at sealed-output canonical register. Emits β union-of-labels pressure-label-set
    as list of per-finding 6-field objects; no §4b-internal precedence.
    """
    # (ε') execution-invalidity branch — highest precedence per sealed NaN-handling.
    if (
        multi_mode_result.get("execution_suspended")
        or case_a_result.get("execution_suspended")
        or successor_class_result.get("execution_suspended")
    ):
        if multi_mode_result.get("execution_suspended"):
            upstream = "§3.1"
        elif case_a_result.get("execution_suspended"):
            upstream = "§3.2"
        else:
            upstream = "§4a"
        return {
            "register": "§4b framing-resolution-pressure assessment",
            "execution_suspended": True,
            "suspension_cause": f"upstream_{upstream}_execution_suspended",
            "pressure_label_set": [
                {
                    "pressure_label": None,
                    "pivot_direction_dependency": None,
                    "basis": f"upstream {upstream} execution suspended",
                    "propagation_state": "execution-suspended-from-upstream",
                    "context_qualifiers": [],
                    "finding_source": None,
                }
            ],
        }

    firing_modes = list(multi_mode_result.get("firing_modes", []))
    indeterminate_labels = multi_mode_result.get("indeterminate_labels", {}) or {}

    pressure_label_set: list[dict[str, Any]] = []

    # Per-firing finding objects (β union; no precedence).
    for mode in firing_modes:
        pressure_label_set.append(_firing_finding_object(mode, firing_modes))

    # §3.2 Case A canonical → terminal-conclusion scalar.
    # Per Codex adversarial review HIGH-3 + sealed §4b D2.2 line 592 ("NO §4b silent
    # collapse of 'incoherent' co-occurrence"): emit terminal-conclusion whenever
    # Case A canonical state is present, regardless of §3.1 firing state. At canonical
    # execution (XOR complementarity) case_a_result.label is None when §3.1 fires,
    # so output is identical; at edge-case data divergence, co-fire diagnostic signal
    # is preserved per sealed §4b composite-handling rule for SEAL author register.
    terminal_trigger = case_a_result.get("terminal_trigger")
    if (
        case_a_result.get("label") == "no-mode-detected reading"
        and isinstance(terminal_trigger, dict)
        and terminal_trigger.get("triggered") is True
    ):
        pressure_label_set.append(_terminal_conclusion_object())

    # §3.2 indeterminate-Case-A → upstream-indeterminacy-propagated terminal pressure
    # (guard on `not firing_modes` retained because §3.1 indeterminate_labels path
    # below already emits per-mode indeterminate objects when both states co-exist).
    if (
        not firing_modes
        and case_a_result.get("label") == "indeterminate-Case-A reading"
    ):
        pressure_label_set.append(
            {
                "pressure_label": None,
                "pivot_direction_dependency": None,
                "basis": "indeterminate-Case-A reading",
                "propagation_state": "upstream-indeterminacy-propagated",
                "context_qualifiers": [],
                "finding_source": "terminal-conclusion",
            }
        )

    # §3.1 indeterminate-X readings → per-finding upstream-indeterminacy-propagated objects.
    for mode in sorted(indeterminate_labels.keys()):
        if mode in firing_modes:
            continue  # Already emitted as firing finding above.
        pressure_label_set.append(_indeterminate_finding_object(mode, indeterminate_labels[mode]))

    # Sort by finding_source for deterministic output ordering.
    pressure_label_set.sort(
        key=lambda o: (o.get("finding_source") or "", o.get("propagation_state") or "")
    )

    return {
        "register": "§4b framing-resolution-pressure assessment",
        "execution_suspended": False,
        "pressure_label_set": pressure_label_set,
        "composition_order": (
            "β union-of-labels per active finding contribution; no §4b-internal "
            "precedence among multi-finding composite outputs"
        ),
    }

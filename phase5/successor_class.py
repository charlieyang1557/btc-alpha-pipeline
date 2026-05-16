"""§4a Successor-cycle-class mapping — hybrid-contextual union (δ'').

Sealed prose at docs/phase5/PHASE5_DIAGNOSTIC_SUBSPEC.md §4a (lines 437-555,
D''''''^c lock-set). Consumes §3.1 partition table rows + §3.2 {label,
terminal_trigger} as inputs and produces structured-object successor-cycle-class
assignments per δ'' hybrid-contextual union mapping with §2.d → §2.c precedence
elevation and §2.f / §2.d upstream-conditioning qualifier carry-through.

No new measurement / no new thresholds at §4a register; mechanical traversal of
locked mapping rules only.
"""

from __future__ import annotations

from typing import Any

# Single-mode successor-class mapping table (sealed §4a lines 455-460, verbatim
# scoping §2.3 source language). Tuple: (class, disposition, verbatim_label).
#
# Downstream consumer note (per ChatGPT structural-overlay MEDIUM-1): the
# `verbatim_label` field in §4a output objects is **display-only sealed-prose
# fidelity** — it MUST NOT supersede the decomposed canonical fields (`class`,
# `disposition`, `qualifier`). Downstream consumers parsing the structured
# §4a output should authoritatively read `class` + `disposition` + `qualifier`
# fields; `verbatim_label` is provided for human-readable surface enumeration
# only and re-fuses the canonical fields into the sealed §2.3 source-language
# phrase.
SINGLE_MODE_SUCCESSOR_CLASS: dict[str, tuple[str, str, str]] = {
    "signal_decay": (
        "empirical-continuation",
        "eligible",
        "empirical-continuation eligible (extended forward window, additional regime testing)",
    ),
    "cost_drag": (
        "cost-model investigation",
        "eligible",
        "cost-model investigation eligible (gross-vs-realistic decomposition)",
    ),
    "cohort_weakness": (
        "cohort-paradigm pivot",
        "required",
        "cohort-paradigm pivot required (alternative cohort sourcing)",
    ),
    "andgate_overfit": (
        "gate-criterion pivot",
        "required",
        "gate-criterion pivot required (alternative gate design)",
    ),
    "success_metric_mismatch": (
        "metric-redefinition cycle",
        "eligible",
        "metric-redefinition cycle eligible (alternative success criteria)",
    ),
    "regime_change": (
        "meta-paradigm pivot",
        "eligible",
        "meta-paradigm pivot eligible (different research framing or universe)",
    ),
}

# Sealed §4a D2.5 (γ-revised) Line 1 qualifier scopes.
# §2.f Line 1 content-attribution bilateral → regime-conditional on §2.a/§2.b/§2.e (downstream recipients).
LINE1_REGIME_CONDITIONAL_RECIPIENTS = {"signal_decay", "cost_drag", "success_metric_mismatch"}
# §2.f Line 1 forward-applicability univocal → forward-applicability-conditioned on §2.c/§2.d.
LINE1_FORWARD_APPLICABILITY_RECIPIENTS = {"cohort_weakness", "andgate_overfit"}

# Case A terminal-conclusion-routing options set (sealed §4a lines 470-472, anti-pre-naming preserved).
CASE_A_TERMINAL_OPTIONS = [
    {
        "class": "meta-paradigm pivot",
        "disposition": "eligible",
        "verbatim_label": "meta-paradigm pivot eligible",
    },
    {
        "class": "project pause / declared-research-line-exhausted close",
        "disposition": "eligible",
        "verbatim_label": "project pause / declared-research-line-exhausted close",
    },
]


def _qualifier_for(mode: str, regime_fires: bool) -> str | None:
    """Compute Line 1 qualifier per sealed §4a D2.5 γ-revised selective carry."""
    if not regime_fires or mode == "regime_change":
        return None
    if mode in LINE1_REGIME_CONDITIONAL_RECIPIENTS:
        return "regime-conditional"
    if mode in LINE1_FORWARD_APPLICABILITY_RECIPIENTS:
        return "forward-applicability-conditioned"
    return None


def _build_initial_assignment(mode: str, regime_fires: bool) -> dict[str, Any]:
    """Build per-mode hybrid object before elevation / de-dup."""
    klass, disposition, verbatim_label = SINGLE_MODE_SUCCESSOR_CLASS[mode]
    return {
        "class": klass,
        "disposition": disposition,
        "qualifier": _qualifier_for(mode, regime_fires),
        "verbatim_label": verbatim_label,
        "source_modes": [mode],
    }


def _apply_elevation(
    assignments_by_mode: dict[str, dict[str, Any]],
    andgate_fires: bool,
    cohort_fires: bool,
) -> None:
    """Apply sealed §4a D2.2 §2.d → §2.c precedence elevation in-place.

    When §2.d + §2.c co-fire: §2.c assignment replaced with gate-criterion-pivot
    template; §2.c-specific qualifiers DROPPED at elevation per sealed line 485.
    """
    if not (andgate_fires and cohort_fires):
        return
    elevated_class, elevated_disposition, elevated_label = SINGLE_MODE_SUCCESSOR_CLASS[
        "andgate_overfit"
    ]
    cohort_entry = assignments_by_mode["cohort_weakness"]
    cohort_entry["class"] = elevated_class
    cohort_entry["disposition"] = elevated_disposition
    cohort_entry["verbatim_label"] = elevated_label
    cohort_entry["qualifier"] = None  # §2.c-specific qualifiers DROPPED at elevation.


def _de_duplicate_by_class(
    assignments_by_mode: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    """De-dup hybrid objects by class; surviving qualifier comes from §2.d-direct.

    Sealed §4a line 485: "After de-duplication with §2.d-direct's own gate-criterion-
    pivot-required contribution, the surviving qualifiers come from §2.d-direct's
    own conditioning."
    """
    by_class: dict[str, dict[str, Any]] = {}
    for mode in sorted(assignments_by_mode.keys()):
        entry = assignments_by_mode[mode]
        klass = entry["class"]
        if klass not in by_class:
            by_class[klass] = {
                "class": klass,
                "disposition": entry["disposition"],
                "qualifier": entry["qualifier"],
                "verbatim_label": entry["verbatim_label"],
                "source_modes": list(entry["source_modes"]),
            }
        else:
            merged = by_class[klass]
            for sm in entry["source_modes"]:
                if sm not in merged["source_modes"]:
                    merged["source_modes"].append(sm)
            # Surviving qualifier comes from non-None entry (i.e., §2.d-direct after elevation drops §2.c's).
            if merged["qualifier"] is None and entry["qualifier"] is not None:
                merged["qualifier"] = entry["qualifier"]
    out: list[dict[str, Any]] = []
    for klass in by_class:
        entry = by_class[klass]
        entry["source_modes"] = sorted(entry["source_modes"])
        out.append(entry)
    out.sort(key=lambda e: e["class"])
    return out


def _emit_indeterminate_assignments(
    indeterminate_labels: dict[str, str],
) -> list[dict[str, Any]]:
    """Emit indeterminate-cycle-class entries for §3.1 indeterminate modes."""
    out: list[dict[str, Any]] = []
    for mode in sorted(indeterminate_labels.keys()):
        out.append(
            {
                "class": "indeterminate-cycle-class",
                "disposition": None,
                "qualifier": None,
                "verbatim_label": indeterminate_labels[mode],
                "source_modes": [mode],
            }
        )
    return out


def map_successor_classes(
    multi_mode_result: dict[str, Any],
    case_a_result: dict[str, Any],
) -> dict[str, Any]:
    """§4a successor-cycle-class mapping per sealed sub-spec.

    Consumes §3.1 multi_mode_result (output of assemble_multi_mode_labels) +
    §3.2 case_a_result (output of evaluate_case_a) at sealed-output canonical
    register. Emits structured-object successor-cycle-class assignments per
    δ'' hybrid-contextual union mapping.
    """
    # (ε') execution-invalidity branch — highest precedence per sealed NaN-handling.
    if multi_mode_result.get("execution_suspended") or case_a_result.get("execution_suspended"):
        upstream = (
            "§3.1"
            if multi_mode_result.get("execution_suspended")
            else "§3.2"
        )
        return {
            "register": "§4a successor-cycle-class mapping",
            "execution_suspended": True,
            "suspension_cause": f"upstream_{upstream}_execution_suspended",
            "narrative_anchor": (
                "§4a execution suspends per (ε') execution-invalidity branch "
                "inherited per §3.x; §6 enumerates the discrepancy; Charlie "
                "register re-adjudicates per §2.d D2''' / §2.f parquet-mismatch "
                "suspension precedent"
            ),
        }

    # §3.1 firing-modes path takes precedence when §3.1 actually fires (sealed §4a
    # lines 476-479: §3.1 indeterminate-X → per-mode indeterminate-cycle-class
    # alongside firing-mode assignments). Case A / indeterminate-Case-A terminal-
    # routing emission is NOT guarded by `not firing_modes` per Codex adversarial
    # review HIGH-3 + sealed §4b D2.2 (line 592) co-fire-preservation discipline:
    # at canonical execution (XOR complementarity) case_a_result.label is None when
    # §3.1 fires, so guard would be redundant; at edge-case data divergence,
    # preserving terminal-routing alongside firing assignments surfaces diagnostic
    # signal for SEAL author register per sealed §4b D2.2 "NO silent collapse".
    firing_modes = list(multi_mode_result.get("firing_modes", []))

    # §3.2 Case A canonical state → structured terminal object.
    terminal_trigger = case_a_result.get("terminal_trigger")
    if (
        case_a_result.get("label") == "no-mode-detected reading"
        and isinstance(terminal_trigger, dict)
        and terminal_trigger.get("triggered") is True
    ):
        return {
            "register": "§4a successor-cycle-class mapping",
            "execution_suspended": False,
            "input_pattern": "case_a_terminal",
            "terminal_routing": {
                "class": "terminal-conclusion-routing",
                "options": [dict(o) for o in CASE_A_TERMINAL_OPTIONS],
                "basis": terminal_trigger.get("basis"),
                "anti_pre_naming": True,
            },
        }

    # §3.2 indeterminate-Case-A → §4a indeterminate-terminal-routing.
    if case_a_result.get("label") == "indeterminate-Case-A reading" and not firing_modes:
        basis = case_a_result.get("terminal_trigger", {}).get("basis", {})
        nan_modes = sorted(basis.get("nan_modes", []))
        return {
            "register": "§4a successor-cycle-class mapping",
            "execution_suspended": False,
            "input_pattern": "indeterminate_case_a",
            "terminal_routing": {
                "class": "indeterminate-terminal-routing",
                "source": nan_modes,
            },
        }

    # §3.1 fires (silent §3.2 per XOR complementarity OR §3.2 indeterminate-Case-A
    # while §3.1 fires in mixed-NaN case) — build per-mode assignments.
    regime_fires = "regime_change" in firing_modes
    andgate_fires = "andgate_overfit" in firing_modes
    cohort_fires = "cohort_weakness" in firing_modes

    assignments_by_mode: dict[str, dict[str, Any]] = {}
    for mode in firing_modes:
        assignments_by_mode[mode] = _build_initial_assignment(mode, regime_fires)

    _apply_elevation(assignments_by_mode, andgate_fires, cohort_fires)
    firing_assignments = _de_duplicate_by_class(assignments_by_mode)

    # Indeterminate-cycle-class entries from §3.1 indeterminate_labels.
    indeterminate_labels = multi_mode_result.get("indeterminate_labels", {}) or {}
    indeterminate_assignments = _emit_indeterminate_assignments(indeterminate_labels)

    all_assignments = firing_assignments + indeterminate_assignments

    if len(firing_assignments) == 1 and not indeterminate_assignments:
        input_pattern = "single_mode"
    elif len(firing_assignments) >= 2 or indeterminate_assignments:
        input_pattern = "multi_mode_union"
    else:
        input_pattern = "empty"  # Defensive; should not occur at canonical execution.

    return {
        "register": "§4a successor-cycle-class mapping",
        "execution_suspended": False,
        "input_pattern": input_pattern,
        "assignments": all_assignments,
        "composition_order": (
            "single-mode lookup → Line 1 qualifier (§2.f) → §2.d→§2.c elevation → "
            "de-duplication (surviving qualifier from §2.d-direct)"
        ),
    }

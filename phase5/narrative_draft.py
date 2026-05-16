"""§6 Initial narrative draft — structural-template traversal (Session-2).

Sealed prose at docs/phase5/PHASE5_DIAGNOSTIC_SUBSPEC.md §6 (lines 838-1117,
D''''''^f/g/h lock-sets). §6.a (§3.x-consumer) + §6.b (§4-consumer) + §6.c
(§5-consumer) structural-template traversal output.

DISCIPLINE LOCK (Patch 1 + V12 anchor): strict structural-template traversal
output only. MUST NOT decide (a) terminal-conclusion invocation, (b) framing-
question (1)/(2)/(3)/(4) resolution, (c) final admissibility-flag interpretive
narration. These are reserved for Phase 5 SEAL author register at arc-level
closeout SEAL per sealed §6 (vii)(c) inheritance.
"""

from __future__ import annotations

import re
from typing import Any

from phase5.framing_pressure import MODE_TO_SECTION

# Display labels mirroring sealed §6.a per-mode finding section narrative requirements.
MODE_DISPLAY_NAMES: dict[str, str] = {
    "signal_decay": "§2.a signal decay",
    "cost_drag": "§2.b cost drag",
    "cohort_weakness": "§2.c cohort weakness",
    "andgate_overfit": "§2.d AND-gate overfit",
    "success_metric_mismatch": "§2.e success-metric mismatch",
    "regime_change": "§2.f regime change",
}

# Cross-§3.1 partition table base labels per sealed §3.1 BASE_LABELS.
CROSS_3_1_ANCHORS: dict[str, str] = {
    "signal_decay": "signal-decay reading",
    "cost_drag": "cost-drag reading",
    "cohort_weakness": "cohort-substrate-weakness reading",
    "andgate_overfit": "AND-gate-overfit reading",
    "success_metric_mismatch": "success-metric-mismatch reading",
    "regime_change": "regime-change-detected reading",
}

# V12 anchor: forbidden DECISIONAL language patterns scanning §6 narrative draft.
# Three categories per Patch 1: (a) terminal-conclusion invocation,
# (b) framing-question resolution, (c) admissibility-flag interpretive narration.
FORBIDDEN_DECISIONAL_PATTERNS: list[tuple[str, str]] = [
    # (a) Terminal-conclusion invocation language.
    (
        "terminal_conclusion_invocation",
        r"\b(?:phase\s*5|we)\s+(?:concludes?|invokes?|determines?|selects?|chooses?)\b",
    ),
    # (b) Framing-question resolution language.
    (
        "framing_question_resolution",
        r"\bframing\s*question\s*\([1-4]\)\s+(?:resolves?|is\s+(?:resolved|chosen|selected))\b",
    ),
    # (c) Interpretive narration patterns asserting paradigm exhaustion / cycle justification.
    (
        "admissibility_flag_interpretive_narration",
        r"\b(?:the\s+paradigm\s+is\s+exhausted|no\s+successor\s+cycle\s+is\s+currently\s+justified)\b",
    ),
]


def scan_forbidden_language(text: str) -> list[dict[str, Any]]:
    """Scan text for V12 anchor forbidden decisional patterns.

    Returns list of {category, pattern, match} dicts; empty list if clean.
    Verbatim §2.5 source language quoted at sealed §5 basis fields is permitted
    only when wrapped as quoted attribute reference (the patterns here match
    bare interpretive narration, not quoted basis fields).
    """
    # Permit verbatim §2.5 quotes when wrapped as quoted basis reference attribute.
    text_for_scan = re.sub(
        r"`basis`?\s*:\s*\"[^\"]*\"", " ", text, flags=re.IGNORECASE
    )
    text_for_scan = re.sub(
        r"\*\*basis\*\*\s*:?\s*\"[^\"]*\"", " ", text_for_scan, flags=re.IGNORECASE
    )
    matches: list[dict[str, Any]] = []
    for category, pattern in FORBIDDEN_DECISIONAL_PATTERNS:
        for m in re.finditer(pattern, text_for_scan, flags=re.IGNORECASE):
            matches.append(
                {
                    "category": category,
                    "pattern": pattern,
                    "match": m.group(0),
                }
            )
    return matches


def _per_mode_finding_blocks(
    detections: dict[str, bool],
    indicator_outputs: dict[str, Any],
    multi_mode_result: dict[str, Any],
    framing_pressure_result: dict[str, Any],
) -> list[dict[str, Any]]:
    """Build 6 per-mode finding blocks per sealed §6.a D2.1.

    Binary detection status derives from explicit upstream sets in
    multi_mode_result (firing_modes / not_detected_modes / nan_modes /
    suspended_modes) per Codex adversarial review HIGH-2 fix — sealed §6.a
    enumerates 4 states (detected / not-detected / (ε'-narrow)-real-data-NaN /
    self-suspended); coercing all falsey indicator values to "not-detected"
    silently hides upstream data-quality state.
    """
    mode_results = indicator_outputs.get("mode_results", {})
    fp_by_source = {
        o.get("finding_source"): o for o in framing_pressure_result.get("pressure_label_set", [])
    }
    firing_set = set(multi_mode_result.get("firing_modes", []))
    not_detected_set = set(multi_mode_result.get("not_detected_modes", []))
    nan_set = set(multi_mode_result.get("nan_modes", []))
    suspended_set = set(multi_mode_result.get("suspended_modes", []))
    blocks: list[dict[str, Any]] = []
    for mode_key in [
        "signal_decay",
        "cost_drag",
        "cohort_weakness",
        "andgate_overfit",
        "success_metric_mismatch",
        "regime_change",
    ]:
        mr = mode_results.get(mode_key, {})
        # Derive binary_detection_status from sealed upstream sets (4-state enumeration).
        if mode_key in suspended_set:
            binary_status = "self-suspended"
        elif mode_key in nan_set:
            binary_status = "real-data-NaN"
        elif mode_key in firing_set:
            binary_status = "detected"
        elif mode_key in not_detected_set:
            binary_status = "not-detected"
        else:
            binary_status = "unknown"  # Defensive; should never occur at canonical execution.
        # Indicator value reference (mode-specific headline statistic where available).
        indicator_value = None
        if "p_value" in mr:
            indicator_value = {"statistic": "p_value", "value": mr["p_value"]}
        elif "tost_p_value" in mr:
            indicator_value = {"statistic": "tost_p_value", "value": mr["tost_p_value"]}
        elif "forward_T" in mr:
            indicator_value = {"statistic": "forward_T", "value": mr["forward_T"]}
        # Framing-question context anchor cross-references §4b pressure object pressure_label.
        section = MODE_TO_SECTION[mode_key]
        fp_obj = fp_by_source.get(section, {})
        framing_context = fp_obj.get("pressure_label")
        blocks.append(
            {
                "mode_key": mode_key,
                "display_name": MODE_DISPLAY_NAMES[mode_key],
                "binary_detection_status": binary_status,
                "indicator_value_reference": indicator_value,
                "cross_3_1_anchor": CROSS_3_1_ANCHORS[mode_key],
                "cross_3_x_sealed_prose_anchor": (
                    f"sealed {MODE_TO_SECTION[mode_key]} register-class identity per sealed prose"
                ),
                "framing_question_context_anchor": framing_context,
            }
        )
    return blocks


def _multi_mode_disposition(multi_mode_result: dict[str, Any]) -> dict[str, Any]:
    """Multi-mode disposition section per sealed §6.a D2.2."""
    firing_modes = list(multi_mode_result.get("firing_modes", []))
    if len(firing_modes) < 2:
        return {
            "applicable": False,
            "reason": "single-mode firing or no firing — multi-mode composite not applicable",
        }
    return {
        "applicable": True,
        "active_modes": sorted(firing_modes),
        "composite_categorical_labels": dict(multi_mode_result.get("per_mode_labels", {})),
        "composition_order": multi_mode_result.get("composition_order"),
        "partition_table_reference": "see sealed §3.1 partition table at session-1 multi_mode_labels.json",
    }


def _ambiguity_disposition(case_a_result: dict[str, Any]) -> dict[str, Any]:
    """Diagnostic ambiguity disposition section per sealed §6.a D2.3."""
    if case_a_result.get("silent_state") is True:
        return {
            "state": "silent",
            "narrative_anchor": (
                "§3.2 silent state per §3.1↔§3.2 XOR complementarity sealed property; "
                "≥1 §2.x at canonical detected register"
            ),
        }
    if case_a_result.get("label") == "no-mode-detected reading":
        return {
            "state": "case_a_canonical",
            "narrative_anchor": (
                "§3.2 Case A canonical state per sealed schema; all 6 §2.x not-detected "
                "at canonical binary register"
            ),
            "terminal_trigger_basis_reference": case_a_result.get("terminal_trigger", {}).get(
                "basis"
            ),
        }
    if case_a_result.get("label") == "indeterminate-Case-A reading":
        return {
            "state": "indeterminate_case_a",
            "narrative_anchor": (
                "§3.2 indeterminate-Case-A reading per sealed (ε'-narrow) semantics; "
                "cross-§5 NaN-handling rule short-circuit precedence inheritance"
            ),
        }
    if case_a_result.get("execution_suspended"):
        return {
            "state": "execution_suspended",
            "narrative_anchor": case_a_result.get("narrative_anchor"),
        }
    return {"state": "unknown"}


def _section_6b_successor(successor_class_result: dict[str, Any]) -> dict[str, Any]:
    """§6.b successor-class mapping disposition section per sealed structural template."""
    if successor_class_result.get("execution_suspended"):
        return {
            "output_type": "execution_suspended",
            "narrative_anchor": successor_class_result.get("narrative_anchor"),
        }
    input_pattern = successor_class_result.get("input_pattern")
    if input_pattern == "case_a_terminal":
        return {
            "output_type": "case_a_terminal",
            "terminal_routing_reference": successor_class_result.get("terminal_routing"),
        }
    if input_pattern == "indeterminate_case_a":
        return {
            "output_type": "indeterminate_terminal_routing",
            "terminal_routing_reference": successor_class_result.get("terminal_routing"),
        }
    assignments = successor_class_result.get("assignments", [])
    if input_pattern == "single_mode":
        output_type = "single_class_hybrid_object"
    elif input_pattern == "multi_mode_union":
        output_type = "multi_class_via_beta_union"
    else:
        output_type = input_pattern or "unknown"
    return {
        "output_type": output_type,
        "assignments": [dict(a) for a in assignments],
    }


def _section_6b_framing_pressure(framing_pressure_result: dict[str, Any]) -> dict[str, Any]:
    """§6.b framing-resolution-pressure disposition section per sealed structural template."""
    if framing_pressure_result.get("execution_suspended"):
        return {
            "output_type": "execution_suspended",
            "suspension_cause": framing_pressure_result.get("suspension_cause"),
        }
    objects = framing_pressure_result.get("pressure_label_set", [])
    active = [o for o in objects if o.get("propagation_state") == "active"]
    # XOR-complementarity invariant: terminal-conclusion finding emits only when
    # §3.1 silent (no firing_modes), while §3.1 indeterminate-X emits only when at
    # least one §2.x is NaN; the two paths are mutually exclusive at canonical
    # execution per sealed §3.1↔§3.2 sealed property. Output-type classification
    # ordering below therefore does not need to handle terminal+indeterminate co-fire.
    if not objects:
        output_type = "empty"
    elif len(active) == 1 and len(objects) == 1:
        output_type = "single_finding_pressure_object"
    elif any(o.get("finding_source") == "terminal-conclusion" for o in objects):
        output_type = "terminal_conclusion_finding"
    elif any(
        o.get("propagation_state") == "upstream-indeterminacy-propagated" for o in objects
    ):
        output_type = "upstream_indeterminacy_propagated"
    else:
        output_type = "multi_finding_via_beta_union"
    return {
        "output_type": output_type,
        "pressure_objects": [dict(o) for o in objects],
    }


def _section_6c_substantive(admissibility_result: dict[str, Any]) -> dict[str, Any]:
    """§6.c substantive terminal-conclusion narrative sub-block per sealed structural template."""
    slot = admissibility_result.get("substantive", {})
    admissible = slot.get("admissible")
    propagation_state = slot.get("propagation_state")
    if propagation_state == "upstream-indeterminacy-propagated":
        block_type = "substantive-upstream-indeterminacy-propagated"
    elif propagation_state == "execution-suspended-from-upstream":
        block_type = "substantive-execution-suspended-from-upstream"
    elif admissible is True:
        block_type = "substantive-admit"
    elif admissible is False:
        block_type = "substantive-not-admit"
    else:
        block_type = "substantive-unknown"
    return {
        "block_type": block_type,
        "admissible": admissible,
        "basis": slot.get("basis"),
        "propagation_state": propagation_state,
    }


def _section_6c_operational(admissibility_result: dict[str, Any]) -> dict[str, Any]:
    """§6.c operational terminal-conclusion narrative sub-block per sealed structural template."""
    slot = admissibility_result.get("operational", {})
    admissible = slot.get("admissible")
    propagation_state = slot.get("propagation_state")
    if propagation_state == "upstream-indeterminacy-propagated":
        block_type = "operational-upstream-indeterminacy-propagated"
    elif propagation_state == "execution-suspended-from-upstream":
        block_type = "operational-execution-suspended-from-upstream"
    elif admissible is True:
        block_type = "operational-admit"
    elif admissible is False:
        block_type = "operational-not-admit"
    else:
        block_type = "operational-unknown"
    return {
        "block_type": block_type,
        "admissible": admissible,
        "basis": slot.get("basis"),
        "propagation_state": propagation_state,
    }


def _render_markdown(section_6a: dict, section_6b: dict, section_6c: dict) -> str:
    """Render structural-template traversal output to markdown.

    No interpretive narration; only structural enumeration of sealed-output
    canonical register values + cross-§ anchor references.
    """
    lines: list[str] = []
    lines.append("# §6 Initial Narrative Draft (Structural-Template Traversal — Session-2)")
    lines.append("")
    lines.append(
        "> Anchored to sealed sub-spec at `docs/phase5/PHASE5_DIAGNOSTIC_SUBSPEC.md` "
        "(sub-spec drafting cycle SEAL at `49ae7e3`). Per pre-fire plan Patch 1 + "
        "V12 anchor: strict structural-template traversal output only — "
        "terminal-conclusion invocation, framing-question (1)/(2)/(3)/(4) resolution, "
        "and admissibility-flag interpretive narration are reserved for Phase 5 SEAL "
        "author register at arc-level closeout SEAL per sealed §6 (vii)(c) inheritance."
    )
    lines.append("")
    # §6.a
    lines.append("## §6.a — §3.x-class consumer cluster")
    lines.append("")
    lines.append("### Per-mode finding section")
    lines.append("")
    for block in section_6a["per_mode_finding_blocks"]:
        iv = block.get("indicator_value_reference")
        iv_str = (
            f"{iv['statistic']}={iv['value']:.6g}" if iv else "(no headline statistic)"
        )
        lines.append(
            f"- **{block['display_name']}** — "
            f"binary detection status: {block['binary_detection_status']}; "
            f"indicator value reference: {iv_str}; "
            f"cross-§3.1 anchor: `{block['cross_3_1_anchor']}`; "
            f"framing-question context anchor (cross-§4b): "
            f"`{block['framing_question_context_anchor']}`"
        )
    lines.append("")
    lines.append("### Multi-mode disposition section")
    lines.append("")
    mmd = section_6a["multi_mode_disposition"]
    if mmd["applicable"]:
        lines.append(
            f"Active modes: {mmd['active_modes']}; composite categorical labels: "
            f"{mmd['composite_categorical_labels']}; composition order: "
            f"{mmd['composition_order']}"
        )
    else:
        lines.append(f"NOT APPLICABLE — {mmd['reason']}")
    lines.append("")
    lines.append("### Diagnostic ambiguity disposition section")
    lines.append("")
    ad = section_6a["ambiguity_disposition"]
    lines.append(
        f"State: `{ad['state']}`; narrative anchor: {ad.get('narrative_anchor', '(none)')}"
    )
    lines.append("")
    # §6.b
    lines.append("## §6.b — §4-class consumer cluster")
    lines.append("")
    lines.append("### Successor-class mapping disposition section")
    lines.append("")
    scd = section_6b["successor_class_mapping_disposition"]
    lines.append(f"Output type: `{scd['output_type']}`")
    if "assignments" in scd:
        for a in scd["assignments"]:
            qual = f"; qualifier: {a['qualifier']}" if a.get("qualifier") else ""
            lines.append(
                f"- class: `{a['class']}`; disposition: {a['disposition']}; "
                f"verbatim_label: \"{a['verbatim_label']}\"; "
                f"source_modes: {a.get('source_modes', [])}{qual}"
            )
    elif "terminal_routing_reference" in scd:
        lines.append(f"Terminal routing reference: {scd['terminal_routing_reference']}")
    lines.append("")
    lines.append("### Framing-resolution-pressure disposition section")
    lines.append("")
    fpd = section_6b["framing_pressure_disposition"]
    lines.append(f"Output type: `{fpd['output_type']}`")
    for o in fpd.get("pressure_objects", []):
        lines.append(
            f"- pressure_label: `{o.get('pressure_label')}`; "
            f"finding_source: `{o.get('finding_source')}`; "
            f"pivot_direction_dependency: `{o.get('pivot_direction_dependency')}`; "
            f"propagation_state: `{o.get('propagation_state')}`; "
            f"context_qualifiers: {o.get('context_qualifiers', [])}; "
            f"`basis`: \"{o.get('basis')}\""
        )
    lines.append("")
    # §6.c
    lines.append("## §6.c — §5-class consumer cluster")
    lines.append("")
    lines.append("### Substantive terminal-conclusion narrative section")
    lines.append("")
    sub = section_6c["substantive_terminal_conclusion"]
    lines.append(
        f"Block type: `{sub['block_type']}`; admissible: `{sub['admissible']}`; "
        f"propagation_state: `{sub['propagation_state']}`; "
        f"`basis`: \"{sub['basis']}\""
    )
    lines.append("")
    lines.append("### Operational terminal-conclusion narrative section")
    lines.append("")
    op = section_6c["operational_terminal_conclusion"]
    lines.append(
        f"Block type: `{op['block_type']}`; admissible: `{op['admissible']}`; "
        f"propagation_state: `{op['propagation_state']}`; "
        f"`basis`: \"{op['basis']}\""
    )
    lines.append("")
    # Phase 4 verdict invariance reference per sealed §6 umbrella precedent.
    lines.append("## Phase 4 verdict invariance")
    lines.append("")
    lines.append(
        "§6 structural-template traversal at session-2 does NOT modify the Phase 4 "
        "closeout verdict at 15bps (no forward persistence detected at PLAN §1.5 "
        "success criterion); the Phase 4 verdict is sealed at PLAN §1.5 framework "
        "register per scoping §4.6 sealed-content invariance, anchored at "
        "`docs/closeout/PHASE4_RESULTS.md` commit `e8f62f1` + tag "
        "`phase4-forward-test-v1`."
    )
    lines.append("")
    return "\n".join(lines)


def draft_narrative(
    detections: dict[str, bool],
    indicator_outputs: dict[str, Any],
    multi_mode_result: dict[str, Any],
    case_a_result: dict[str, Any],
    successor_class_result: dict[str, Any],
    framing_pressure_result: dict[str, Any],
    admissibility_result: dict[str, Any],
) -> dict[str, Any]:
    """Generate §6 initial narrative draft via structural-template traversal.

    NO closeout interpretation per Patch 1 + V12 anchor. Pure mechanical
    rendering of §6.a/§6.b/§6.c sealed structural templates over §3.x/§4/§5
    outputs.
    """
    section_6a = {
        "per_mode_finding_blocks": _per_mode_finding_blocks(
            detections, indicator_outputs, multi_mode_result, framing_pressure_result
        ),
        "multi_mode_disposition": _multi_mode_disposition(multi_mode_result),
        "ambiguity_disposition": _ambiguity_disposition(case_a_result),
    }
    section_6b = {
        "successor_class_mapping_disposition": _section_6b_successor(successor_class_result),
        "framing_pressure_disposition": _section_6b_framing_pressure(framing_pressure_result),
    }
    section_6c = {
        "substantive_terminal_conclusion": _section_6c_substantive(admissibility_result),
        "operational_terminal_conclusion": _section_6c_operational(admissibility_result),
    }
    markdown = _render_markdown(section_6a, section_6b, section_6c)
    # V12 anchor self-audit: scan rendered markdown for forbidden decisional patterns.
    forbidden_matches = scan_forbidden_language(markdown)
    audit = {
        "no_terminal_conclusion_invocation": not any(
            m["category"] == "terminal_conclusion_invocation" for m in forbidden_matches
        ),
        "no_framing_question_resolution": not any(
            m["category"] == "framing_question_resolution" for m in forbidden_matches
        ),
        "no_admissibility_flag_interpretive_narration": not any(
            m["category"] == "admissibility_flag_interpretive_narration"
            for m in forbidden_matches
        ),
        "forbidden_pattern_matches": forbidden_matches,
    }
    return {
        "register": "§6 attribution report deliverable structure — initial narrative draft (structural-template traversal)",
        "narrative_markdown": markdown,
        "section_6a": section_6a,
        "section_6b": section_6b,
        "section_6c": section_6c,
        "anti_pre_emption_audit": audit,
    }

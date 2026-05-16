"""Smoke tests for §6 initial narrative draft (structural-template traversal).

Sealed prose at docs/phase5/PHASE5_DIAGNOSTIC_SUBSPEC.md §6 (lines 838-1117,
D''''''^f/g/h lock-sets). §6.a (§3.x-consumer) + §6.b (§4-consumer) + §6.c
(§5-consumer) structural-template traversal output.

Per Charlie register Patch 1 (Anti-pre-emption discipline + V12 anchor): strict
structural-template traversal output only; NO terminal-conclusion invocation /
framing-question resolution / admissibility-flag interpretive narration.
"""

from __future__ import annotations

from phase5.admissibility import flag_admissibility
from phase5.framing_pressure import assess_framing_pressure
from phase5.labels.ambiguity_disposition import evaluate_case_a
from phase5.labels.multi_mode_rules import assemble_multi_mode_labels
from phase5.framing_pressure import MODE_TO_SECTION
from phase5.narrative_draft import (
    FORBIDDEN_DECISIONAL_PATTERNS,
    draft_narrative,
    scan_forbidden_language,
)
from phase5.successor_class import map_successor_classes

ALL_MODES = [
    "signal_decay",
    "cost_drag",
    "cohort_weakness",
    "andgate_overfit",
    "success_metric_mismatch",
    "regime_change",
]


def _detections(**overrides: bool) -> dict[str, bool]:
    out = {m: False for m in ALL_MODES}
    out.update(overrides)
    return out


def _stub_indicator_outputs(detections: dict[str, bool]) -> dict:
    """Minimal indicator_outputs fixture for narrative_draft consumption."""
    return {
        "mode_results": {
            "signal_decay": {
                "mode": "§2.a signal decay",
                "detected": detections["signal_decay"],
                "p_value": 0.2558,
            },
            "cost_drag": {
                "mode": "§2.b cost drag",
                "detected": detections["cost_drag"],
                "p_value": 1.82e-12,
            },
            "cohort_weakness": {
                "mode": "§2.c cohort weakness",
                "detected": detections["cohort_weakness"],
            },
            "andgate_overfit": {
                "mode": "§2.d AND-gate overfit",
                "detected": detections["andgate_overfit"],
                "tost_p_value": 1.0,
            },
            "success_metric_mismatch": {
                "mode": "§2.e success-metric mismatch",
                "detected": detections["success_metric_mismatch"],
            },
            "regime_change": {
                "mode": "§2.f regime change",
                "detected": detections["regime_change"],
                "forward_T": 0.00533,
            },
        }
    }


def _run(detections, nan_modes=None, suspended_modes=None) -> dict:
    nan_modes = nan_modes or []
    suspended_modes = suspended_modes or []
    multi = assemble_multi_mode_labels(detections, nan_modes, suspended_modes)
    case_a = evaluate_case_a(detections, nan_modes, suspended_modes)
    sc = map_successor_classes(multi, case_a)
    fp = assess_framing_pressure(multi, case_a, sc)
    adm = flag_admissibility(multi, case_a, sc, fp)
    return draft_narrative(
        detections=detections,
        indicator_outputs=_stub_indicator_outputs(detections),
        multi_mode_result=multi,
        case_a_result=case_a,
        successor_class_result=sc,
        framing_pressure_result=fp,
        admissibility_result=adm,
    )


# ---------- Top-level shape ----------


def test_6_output_has_required_top_level_fields():
    r = _run(_detections(cost_drag=True))
    assert set(r.keys()) >= {
        "register",
        "narrative_markdown",
        "section_6a",
        "section_6b",
        "section_6c",
        "anti_pre_emption_audit",
    }
    assert r["register"].startswith("§6")


# ---------- §6.a — §3.x-consumer cluster ----------


def test_6a_per_mode_finding_section_enumerates_all_6_modes():
    """Per-mode finding section consists of 6 narrative blocks per sealed §6.a D2.1."""
    r = _run(_detections(cost_drag=True))
    blocks = r["section_6a"]["per_mode_finding_blocks"]
    assert len(blocks) == 6
    by_mode = {b["mode_key"]: b for b in blocks}
    assert set(by_mode.keys()) == set(ALL_MODES)
    # Each block carries indicator value reference + binary detection + cross-§3.1 anchor + framing-question anchor.
    cd = by_mode["cost_drag"]
    assert cd["binary_detection_status"] == "detected"
    assert cd["cross_3_1_anchor"] == "cost-drag reading"
    # Framing-question context anchor cross-references §4b pressure object.
    assert "deferred" == cd["framing_question_context_anchor"]


def test_6a_cross_3x_sealed_prose_anchor_uses_correct_section_identifier_for_each_mode():
    """V12 anchor coverage: cross_3_x_sealed_prose_anchor cites canonical §2.X per MODE_TO_SECTION (not mode_key[0])."""
    r = _run(_detections(cost_drag=True))
    by_mode = {b["mode_key"]: b for b in r["section_6a"]["per_mode_finding_blocks"]}
    for mode_key in ALL_MODES:
        anchor = by_mode[mode_key]["cross_3_x_sealed_prose_anchor"]
        expected_section = MODE_TO_SECTION[mode_key]
        assert expected_section in anchor, (
            f"mode {mode_key} cross_3_x_sealed_prose_anchor expected to reference "
            f"`{expected_section}`, got: {anchor!r}"
        )


def test_6a_per_mode_binary_status_4_state_enumeration_per_codex_high_2():
    """Codex HIGH-2 regression: binary_detection_status must enumerate 4 sealed states.

    Per sealed §6.a per-mode finding section: detected / not-detected /
    (ε'-narrow)-class-real-data-NaN / §2.x-self-suspended. Coercing all falsey
    indicator values to 'not-detected' (the bug) hides upstream data-quality
    state. Verify NaN and suspended states render with explicit labels.
    """
    from phase5.narrative_draft import draft_narrative
    from phase5.framing_pressure import assess_framing_pressure
    from phase5.successor_class import map_successor_classes
    from phase5.admissibility import flag_admissibility

    # Construct §3.1-style synthetic with one NaN + one self-suspended + others not-detected.
    synthetic_multi = {
        "emits_substantive": False,
        "execution_suspended": False,
        "firing_modes": [],
        "not_detected_modes": ["cost_drag", "cohort_weakness", "success_metric_mismatch"],
        "nan_modes": ["signal_decay"],
        "suspended_modes": ["regime_change"],
        "per_mode_labels": {},
        "partition_table": [],
        "indeterminate_labels": {"signal_decay": "indeterminate signal-decay reading"},
    }
    synthetic_case_a = {
        "label": "indeterminate-Case-A reading",
        "terminal_trigger": {
            "triggered": False,
            "basis": {"canonical_0_mode": False, "suspended_modes": ["regime_change"], "nan_modes": ["signal_decay"]},
        },
        "execution_suspended": False,
    }
    detections = {m: False for m in ALL_MODES}
    sc = map_successor_classes(synthetic_multi, synthetic_case_a)
    fp = assess_framing_pressure(synthetic_multi, synthetic_case_a, sc)
    adm = flag_admissibility(synthetic_multi, synthetic_case_a, sc, fp)
    r = draft_narrative(
        detections=detections,
        indicator_outputs=_stub_indicator_outputs(detections),
        multi_mode_result=synthetic_multi,
        case_a_result=synthetic_case_a,
        successor_class_result=sc,
        framing_pressure_result=fp,
        admissibility_result=adm,
    )
    by_mode = {b["mode_key"]: b for b in r["section_6a"]["per_mode_finding_blocks"]}
    assert by_mode["signal_decay"]["binary_detection_status"] == "real-data-NaN"
    assert by_mode["regime_change"]["binary_detection_status"] == "self-suspended"
    assert by_mode["cost_drag"]["binary_detection_status"] == "not-detected"
    # andgate_overfit not in any sealed set above → defensive 'unknown' label.
    assert by_mode["andgate_overfit"]["binary_detection_status"] in {"unknown", "not-detected"}


def test_6a_multi_mode_disposition_not_applicable_for_single_mode_firing():
    """Multi-mode disposition section NOT APPLICABLE when single-mode fires."""
    r = _run(_detections(cost_drag=True))
    assert r["section_6a"]["multi_mode_disposition"]["applicable"] is False


def test_6a_ambiguity_disposition_records_3_2_silent_state_when_3_1_fires():
    """§3.2 silent state per XOR complementarity → ambiguity disposition records silent_state."""
    r = _run(_detections(cost_drag=True))
    ad = r["section_6a"]["ambiguity_disposition"]
    assert ad["state"] == "silent"
    assert "XOR complementarity" in ad["narrative_anchor"]


def test_6a_ambiguity_disposition_records_case_a_canonical_when_no_modes_fire():
    """All 6 modes not-detected → §3.2 Case A canonical → ambiguity disposition records Case A."""
    r = _run(_detections())
    ad = r["section_6a"]["ambiguity_disposition"]
    assert ad["state"] == "case_a_canonical"


# ---------- §6.b — §4-consumer cluster ----------


def test_6b_successor_class_mapping_disposition_records_single_class_assignment():
    """Single-class assignment block per sealed §6.b successor-class mapping disposition."""
    r = _run(_detections(cost_drag=True))
    scd = r["section_6b"]["successor_class_mapping_disposition"]
    assert scd["output_type"] == "single_class_hybrid_object"
    assignments = scd["assignments"]
    assert len(assignments) == 1
    a = assignments[0]
    assert a["class"] == "cost-model investigation"
    assert a["disposition"] == "eligible"
    assert (
        a["verbatim_label"]
        == "cost-model investigation eligible (gross-vs-realistic decomposition)"
    )


def test_6b_framing_pressure_disposition_records_single_finding_pressure_object():
    """Single-finding pressure object block per sealed §6.b framing-pressure disposition."""
    r = _run(_detections(cost_drag=True))
    fpd = r["section_6b"]["framing_pressure_disposition"]
    assert fpd["output_type"] == "single_finding_pressure_object"
    objects = fpd["pressure_objects"]
    assert len(objects) == 1
    o = objects[0]
    assert o["pressure_label"] == "deferred"
    assert o["finding_source"] == "§2.b"


# ---------- §6.c — §5-consumer cluster ----------


def test_6c_substantive_narrative_records_not_admit_block_at_session_2_state():
    """Session-2: §3.2 silent → substantive NOT admit → §6.c substantive-not-admit block."""
    r = _run(_detections(cost_drag=True))
    sub = r["section_6c"]["substantive_terminal_conclusion"]
    assert sub["block_type"] == "substantive-not-admit"
    assert sub["admissible"] is False
    assert sub["basis"] == "criteria not satisfied at canonical execution"


def test_6c_operational_narrative_records_not_admit_block_at_session_2_state():
    """Session-2: single-class §4a → CASE 1 unmet → operational NOT admit → §6.c operational-not-admit block."""
    r = _run(_detections(cost_drag=True))
    op = r["section_6c"]["operational_terminal_conclusion"]
    assert op["block_type"] == "operational-not-admit"
    assert op["admissible"] is False


def test_6c_f_distinct_2_sub_block_structural_separation_preserved():
    """§6.c maintains 2 register-class-distinct sub-blocks (substantive + operational) per sealed F1 distinctness."""
    r = _run(_detections(cost_drag=True))
    assert "substantive_terminal_conclusion" in r["section_6c"]
    assert "operational_terminal_conclusion" in r["section_6c"]


# ---------- Anti-pre-emption discipline (V12 anchor) ----------


def test_6_narrative_markdown_contains_no_forbidden_decisional_language():
    """V12 anchor: §6 initial narrative draft must NOT pre-name SEAL author register adjudications."""
    r = _run(_detections(cost_drag=True))
    md = r["narrative_markdown"]
    found = scan_forbidden_language(md)
    assert found == [], f"Forbidden decisional language found in §6 narrative draft: {found}"


def test_6_anti_pre_emption_audit_flags_clean_for_session_2_case():
    """anti_pre_emption_audit struct asserts all 3 forbidden surfaces clean."""
    r = _run(_detections(cost_drag=True))
    audit = r["anti_pre_emption_audit"]
    assert audit["no_terminal_conclusion_invocation"] is True
    assert audit["no_framing_question_resolution"] is True
    assert audit["no_admissibility_flag_interpretive_narration"] is True
    assert audit["forbidden_pattern_matches"] == []


def test_6_anti_pre_emption_audit_flags_detect_decisional_language_when_injected():
    """Anti-pre-emption scanner must detect forbidden patterns when present."""
    # Inject forbidden pattern into a known-clean markdown.
    forbidden_test_cases = [
        "Phase 5 concludes that the paradigm is exhausted.",
        "We conclude that framing question (1) resolves.",
        "Framing question (2) is resolved at session-2.",
    ]
    for s in forbidden_test_cases:
        assert scan_forbidden_language(s), f"Failed to detect forbidden pattern in: {s!r}"


def test_6_forbidden_pattern_list_contains_at_least_3_categories():
    """FORBIDDEN_DECISIONAL_PATTERNS covers terminal-conclusion + framing-resolution + interpretive-narration."""
    assert len(FORBIDDEN_DECISIONAL_PATTERNS) >= 3


# ---------- Phase 4 verdict invariance reference (sealed precedent) ----------


def test_6_narrative_markdown_references_phase_4_verdict_invariance():
    """§6 narrative draft includes Phase 4 verdict invariance reference per sealed §6 umbrella precedent."""
    r = _run(_detections(cost_drag=True))
    md = r["narrative_markdown"].lower()
    assert "phase 4 verdict invariance" in md

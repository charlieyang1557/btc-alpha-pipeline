"""Smoke tests for §4a successor-cycle-class mapping.

Sealed prose at docs/phase5/PHASE5_DIAGNOSTIC_SUBSPEC.md §4a (lines 437-555,
D''''''^c lock-set). Hybrid-contextual union mapping (δ'') with §2.d → §2.c
precedence elevation and §2.f / §2.d upstream-conditioning qualifier
carry-through (D2.5 γ-revised).
"""

from __future__ import annotations

from phase5.labels.ambiguity_disposition import evaluate_case_a
from phase5.labels.multi_mode_rules import assemble_multi_mode_labels
from phase5.successor_class import (
    SINGLE_MODE_SUCCESSOR_CLASS,
    map_successor_classes,
)

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


def _run(detections: dict[str, bool], nan_modes=None, suspended_modes=None) -> dict:
    """End-to-end pipeline §3.1 + §3.2 → §4a."""
    nan_modes = nan_modes or []
    suspended_modes = suspended_modes or []
    multi = assemble_multi_mode_labels(detections, nan_modes, suspended_modes)
    case_a = evaluate_case_a(detections, nan_modes, suspended_modes)
    return map_successor_classes(multi, case_a)


# ---------- Mapping table fidelity (V5 anchor) ----------


def test_4a_single_mode_table_byte_identical_to_sealed_subspec():
    """SINGLE_MODE_SUCCESSOR_CLASS entries match sealed §4a lines 455-460 verbatim."""
    assert SINGLE_MODE_SUCCESSOR_CLASS["signal_decay"] == (
        "empirical-continuation",
        "eligible",
        "empirical-continuation eligible (extended forward window, additional regime testing)",
    )
    assert SINGLE_MODE_SUCCESSOR_CLASS["cost_drag"] == (
        "cost-model investigation",
        "eligible",
        "cost-model investigation eligible (gross-vs-realistic decomposition)",
    )
    assert SINGLE_MODE_SUCCESSOR_CLASS["cohort_weakness"] == (
        "cohort-paradigm pivot",
        "required",
        "cohort-paradigm pivot required (alternative cohort sourcing)",
    )
    assert SINGLE_MODE_SUCCESSOR_CLASS["andgate_overfit"] == (
        "gate-criterion pivot",
        "required",
        "gate-criterion pivot required (alternative gate design)",
    )
    assert SINGLE_MODE_SUCCESSOR_CLASS["success_metric_mismatch"] == (
        "metric-redefinition cycle",
        "eligible",
        "metric-redefinition cycle eligible (alternative success criteria)",
    )
    assert SINGLE_MODE_SUCCESSOR_CLASS["regime_change"] == (
        "meta-paradigm pivot",
        "eligible",
        "meta-paradigm pivot eligible (different research framing or universe)",
    )


# ---------- Single-mode mapping (session-2 actual case + 5 sibling sanity) ----------


def test_4a_single_mode_cost_drag_session_2_actual_case():
    """Session-2 actual input: only §2.b fires; expect single cost-model investigation entry."""
    r = _run(_detections(cost_drag=True))
    assert r["execution_suspended"] is False
    assert r["input_pattern"] == "single_mode"
    assert r["assignments"] == [
        {
            "class": "cost-model investigation",
            "disposition": "eligible",
            "qualifier": None,
            "verbatim_label": "cost-model investigation eligible (gross-vs-realistic decomposition)",
            "source_modes": ["cost_drag"],
        }
    ]
    # Anti-pre-emption (v) §4a → §4b: no §4b-pre-naming in output.
    for a in r["assignments"]:
        assert "pressure_label" not in a
    # Anti-circularity (iv) §4a → §5: no §5-pre-naming.
    assert "admissible" not in r


def test_4a_single_mode_signal_decay():
    r = _run(_detections(signal_decay=True))
    assert r["assignments"][0]["class"] == "empirical-continuation"
    assert r["assignments"][0]["disposition"] == "eligible"


def test_4a_single_mode_cohort_weakness_required_disposition():
    r = _run(_detections(cohort_weakness=True))
    assert r["assignments"][0]["disposition"] == "required"


# ---------- Multi-mode β union (no collapse; anti-dominance (vii)) ----------


def test_4a_regime_change_plus_signal_decay_emits_two_entries_with_regime_conditional_on_signal_decay():
    """§2.f + §2.a → 2 entries; regime-conditional qualifier on §2.a-derived class only."""
    r = _run(_detections(signal_decay=True, regime_change=True))
    assert r["input_pattern"] == "multi_mode_union"
    classes = {a["class"]: a for a in r["assignments"]}
    assert set(classes.keys()) == {"meta-paradigm pivot", "empirical-continuation"}
    # Upstream source (§2.f-derived class): no qualifier.
    assert classes["meta-paradigm pivot"]["qualifier"] is None
    # Downstream recipient (§2.a-derived class): regime-conditional qualifier.
    assert classes["empirical-continuation"]["qualifier"] == "regime-conditional"
    # Bilateral attribution caveat parenthetical from §3.1 DROPS at §4a (anti-circularity (iii)).
    assert "bilateral" not in classes["empirical-continuation"]["verbatim_label"].lower()


def test_4a_regime_change_plus_cohort_weakness_emits_forward_applicability_conditioned_on_cohort():
    """§2.f + §2.c → forward-applicability-conditioned qualifier on §2.c-derived class."""
    r = _run(_detections(cohort_weakness=True, regime_change=True))
    classes = {a["class"]: a for a in r["assignments"]}
    assert classes["meta-paradigm pivot"]["qualifier"] is None
    assert classes["cohort-paradigm pivot"]["qualifier"] == "forward-applicability-conditioned"


# ---------- §2.d → §2.c elevation precedence rule (D2.2) ----------


def test_4a_andgate_plus_cohort_elevates_cohort_to_gate_criterion_pivot_de_duped():
    """§2.d + §2.c → single gate-criterion-pivot entry; §2.c-elevation absorbs §2.d's own entry."""
    r = _run(_detections(andgate_overfit=True, cohort_weakness=True))
    # Only one entry after de-dup (both §2.d-direct and §2.c-elevated map to gate-criterion pivot).
    assert len(r["assignments"]) == 1
    assignment = r["assignments"][0]
    assert assignment["class"] == "gate-criterion pivot"
    assert assignment["disposition"] == "required"
    # §2.c-specific qualifiers DROPPED at elevation per sealed prose; no qualifier on de-duped entry.
    assert assignment["qualifier"] is None
    assert set(assignment["source_modes"]) == {"andgate_overfit", "cohort_weakness"}


def test_4a_regime_plus_andgate_plus_cohort_keeps_forward_applicability_from_andgate_after_elevation_de_dup():
    """§2.f + §2.d + §2.c → meta-paradigm pivot + gate-criterion pivot with forward-applicability-conditioned."""
    r = _run(_detections(regime_change=True, andgate_overfit=True, cohort_weakness=True))
    classes = {a["class"]: a for a in r["assignments"]}
    # §2.f-derived class: no qualifier (upstream source).
    assert classes["meta-paradigm pivot"]["qualifier"] is None
    # Surviving qualifier on de-duped gate-criterion pivot comes from §2.d-direct's own §2.f conditioning.
    assert classes["gate-criterion pivot"]["qualifier"] == "forward-applicability-conditioned"


# ---------- Case A terminal-conclusion-routing object ----------


def test_4a_case_a_emits_terminal_routing_options_set_with_anti_pre_naming():
    """All 6 modes not-detected → §3.2 Case A → §4a structured terminal object."""
    r = _run(_detections())  # all False
    assert r["input_pattern"] == "case_a_terminal"
    obj = r["terminal_routing"]
    assert obj["class"] == "terminal-conclusion-routing"
    assert obj["anti_pre_naming"] is True
    option_classes = {o["class"] for o in obj["options"]}
    assert option_classes == {
        "meta-paradigm pivot",
        "project pause / declared-research-line-exhausted close",
    }
    # §4a does NOT pre-name §5 terminal-conclusion outcome (anti-circularity (iv)).
    assert "selected_option" not in obj


# ---------- Indeterminate-cycle-class propagation ----------


def test_4a_indeterminate_at_non_upstream_mode_emits_indeterminate_cycle_class_for_that_mode():
    """§2.a NaN → indeterminate-cycle-class for §2.a; other modes unaffected if firing."""
    r = _run(_detections(cost_drag=True), nan_modes=["signal_decay"])
    indet = [a for a in r["assignments"] if a["class"] == "indeterminate-cycle-class"]
    assert len(indet) == 1
    assert indet[0]["source_modes"] == ["signal_decay"]
    # Cost-drag mapping unaffected.
    classes_present = {a["class"] for a in r["assignments"]}
    assert "cost-model investigation" in classes_present


def test_4a_indeterminate_case_a_routes_to_indeterminate_terminal_routing():
    """§2.x NaN with all others not-detected → §3.2 indeterminate-Case-A → §4a indeterminate-terminal-routing."""
    r = _run(_detections(), nan_modes=["cost_drag"])
    assert r["input_pattern"] == "indeterminate_case_a"
    obj = r["terminal_routing"]
    assert obj["class"] == "indeterminate-terminal-routing"
    assert obj["source"] == ["cost_drag"]


# ---------- Execution-suspended (ε') hybrid propagation ----------


def test_4a_upstream_suspension_propagates_to_4a_suspension():
    """Upstream §2.x self-suspended → §3.x execution suspends → §4a execution suspends."""
    r = _run(_detections(), suspended_modes=["regime_change"])
    assert r["execution_suspended"] is True
    assert "suspension_cause" in r
    assert "assignments" not in r
    assert "terminal_routing" not in r


# ---------- Anti-pre-emption discipline (V10/V12 anchors) ----------


def test_4a_no_pre_emption_of_4b_5_6_in_output_schema():
    """§4a output schema must not contain §4b pressure / §5 admissibility / §6 narrative fields."""
    r = _run(_detections(cost_drag=True))
    forbidden_top_level = {"pressure_label_set", "substantive", "operational", "narrative"}
    assert not (forbidden_top_level & set(r.keys()))
    for a in r["assignments"]:
        forbidden_per_assignment = {
            "pressure_label",
            "admissible",
            "narrative_text",
            "framing_resolution",
        }
        assert not (forbidden_per_assignment & set(a.keys()))

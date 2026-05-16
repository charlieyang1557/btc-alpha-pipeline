"""Smoke tests for §5 substantive-vs-operational admissibility flagging.

Sealed prose at docs/phase5/PHASE5_DIAGNOSTIC_SUBSPEC.md §5 (lines 675-836,
D''''''^e lock-set). Fixed-shape 2-slot output per D1.1 β'-fixed-shape lock;
D2.1 α HARD LOCK substantive ⟺ §3.2 Case A canonical state; D2.2 1-CASE α
LOCK operational ⟺ CASE 1 §4a residual ambiguity; NaN-propagation short-circuit
precedes canonical evaluation per sealed line 754.
"""

from __future__ import annotations

from phase5.admissibility import flag_admissibility
from phase5.framing_pressure import assess_framing_pressure
from phase5.labels.ambiguity_disposition import evaluate_case_a
from phase5.labels.multi_mode_rules import assemble_multi_mode_labels
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


def _run(detections: dict[str, bool], nan_modes=None, suspended_modes=None) -> dict:
    """End-to-end pipeline §3.1 + §3.2 + §4a + §4b → §5."""
    nan_modes = nan_modes or []
    suspended_modes = suspended_modes or []
    multi = assemble_multi_mode_labels(detections, nan_modes, suspended_modes)
    case_a = evaluate_case_a(detections, nan_modes, suspended_modes)
    sc = map_successor_classes(multi, case_a)
    fp = assess_framing_pressure(multi, case_a, sc)
    return flag_admissibility(multi, case_a, sc, fp)


# ---------- Fixed-shape 2-slot output (D1.1 β' lock) ----------


def test_5_output_is_fixed_shape_2_slot_with_4_fields_each():
    r = _run(_detections(cost_drag=True))
    assert set(r.keys()) >= {"substantive", "operational"}
    for slot_key in ["substantive", "operational"]:
        slot = r[slot_key]
        assert set(slot.keys()) == {"availability_type", "admissible", "basis", "propagation_state"}
        assert slot["availability_type"] == slot_key


def test_5_output_includes_mechanical_routing_provenance_per_chatgpt_medium_3():
    """ChatGPT MEDIUM-3: expose CASE-routing provenance fields for machine-readable auditability."""
    r = _run(_detections(cost_drag=True))
    assert "mechanical_routing_provenance" in r
    p = r["mechanical_routing_provenance"]
    assert p["substantive_evaluated_case"] == "D2.1_case_a_canonical_5_condition_check"
    assert p["substantive_case_a_canonical_check_passed"] is False
    assert p["operational_evaluated_case"] == "D2.2_CASE_1_residual_ambiguity_check"
    assert p["operational_case_1_silent_or_terminal_false"] is True
    assert p["operational_distinct_assignment_count"] == 1
    assert p["operational_case_1_threshold"] == 2


# ---------- Session-2 actual case (both NOT admit) ----------


def test_5_session_2_actual_case_both_not_admit():
    """Session-2: cost_drag firing → §3.2 silent + §4a single-class → substantive NOT admit + operational CASE 1 unmet."""
    r = _run(_detections(cost_drag=True))
    assert r["substantive"]["admissible"] is False
    assert r["substantive"]["basis"] == "criteria not satisfied at canonical execution"
    assert r["substantive"]["propagation_state"] == "active"
    assert r["operational"]["admissible"] is False
    assert r["operational"]["basis"] == "criteria not satisfied at canonical execution"
    assert r["operational"]["propagation_state"] == "active"


# ---------- D2.1 substantive admissibility (§3.2 Case A canonical only) ----------


def test_5_substantive_admit_when_3_2_case_a_canonical():
    """All 6 §2.x not-detected → §3.2 Case A canonical → substantive admit with verbatim §2.5 basis."""
    r = _run(_detections())  # all False
    assert r["substantive"]["admissible"] is True
    assert (
        r["substantive"]["basis"]
        == "the AND-gate paradigm is likely exhausted for deployable BTC alpha under realistic costs"
    )
    # Operational NOT admit per procedural mutual-exclusivity at canonical Case A.
    assert r["operational"]["admissible"] is False


def test_5_substantive_not_admit_at_3_1_single_mode():
    """Single-mode §3.1 firing → §3.2 silent → substantive NOT admit."""
    r = _run(_detections(signal_decay=True))
    assert r["substantive"]["admissible"] is False


# ---------- D2.2 CASE 1 operational admissibility (§4a residual ambiguity) ----------


def test_5_operational_admit_when_4a_has_2_plus_distinct_unresolved():
    """§2.f + §2.a fires → §4a β union 2 distinct classes → CASE 1 satisfied → operational admit."""
    r = _run(_detections(signal_decay=True, regime_change=True))
    assert r["operational"]["admissible"] is True
    assert (
        "Phase 5 is permitted to conclude that no successor empirical cycle is currently justified"
        in r["operational"]["basis"]
    )
    # Substantive NOT admit per §3.1 firing.
    assert r["substantive"]["admissible"] is False


def test_5_operational_not_admit_when_4a_resolved_by_elevation():
    """§2.d + §2.c fires → §4a elevation collapses to single class → CASE 1 ≥2-distinct unmet → operational NOT admit."""
    r = _run(_detections(andgate_overfit=True, cohort_weakness=True))
    assert r["operational"]["admissible"] is False
    assert r["substantive"]["admissible"] is False


def test_5_operational_not_admit_when_4a_single_class_single_mode():
    """Single-mode firing → §4a single-class → CASE 1 ≥2-distinct unmet → operational NOT admit."""
    r = _run(_detections(cost_drag=True))
    assert r["operational"]["admissible"] is False


# ---------- Silent-state-equivalent rule (sealed line 734) ----------


def test_5_silent_state_treated_as_terminal_trigger_false_for_operational_check():
    """§3.1 fires → §3.2 silent state semantically equiv to terminal_trigger=False per XOR complementarity (sealed line 734)."""
    # §2.f + §2.a fires; operational CASE 1 requires §3.2.terminal_trigger=False which silent state satisfies.
    r = _run(_detections(signal_decay=True, regime_change=True))
    assert r["operational"]["admissible"] is True


# ---------- NaN-propagation short-circuit (D3.3, precedes canonical eval per line 754) ----------


def test_5_nan_propagation_short_circuits_to_null_admissible_both_slots():
    """§2.f NaN → upstream-indeterminacy-propagated → both slots admissible=null."""
    r = _run(_detections(cost_drag=True), nan_modes=["regime_change"])
    assert r["substantive"]["admissible"] is None
    assert r["substantive"]["propagation_state"] == "upstream-indeterminacy-propagated"
    assert r["operational"]["admissible"] is None
    assert r["operational"]["propagation_state"] == "upstream-indeterminacy-propagated"


def test_5_execution_suspended_propagates_to_null_admissible_both_slots():
    """Upstream §2.x self-suspended → both slots admissible=null + propagation_state=execution-suspended-from-upstream."""
    r = _run(_detections(), suspended_modes=["regime_change"])
    assert r["substantive"]["admissible"] is None
    assert r["substantive"]["propagation_state"] == "execution-suspended-from-upstream"
    assert r["operational"]["admissible"] is None
    assert r["operational"]["propagation_state"] == "execution-suspended-from-upstream"


# ---------- Anti-pre-emption discipline (V10/V12 anchors) ----------


def test_5_no_pre_naming_of_seal_author_invocation_or_6_narrative_in_output():
    """§5 output must not contain SEAL author terminal-conclusion invocation / §6 narrative determination."""
    r = _run(_detections(cost_drag=True))
    forbidden_top_level = {"invocation", "selected_outcome", "narrative_text", "framing_resolution"}
    assert not (forbidden_top_level & set(r.keys()))
    for slot in [r["substantive"], r["operational"]]:
        forbidden_slot = {"invoke", "selected", "narrative", "framing_resolution"}
        assert not (forbidden_slot & set(slot.keys()))

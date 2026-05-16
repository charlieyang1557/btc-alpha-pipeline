"""Smoke tests for §4b framing-question resolution-pressure assessment.

Sealed prose at docs/phase5/PHASE5_DIAGNOSTIC_SUBSPEC.md §4b (lines 556-674,
D''''''^d lock-set). β union-of-labels composite emission; per-finding 6-field
schema; qualifier-stripping rule (qualifiers carried as context_qualifiers
without altering pressure_label per scoping §2.4 verbatim case routing).
"""

from __future__ import annotations

from phase5.framing_pressure import (
    SINGLE_FINDING_PRESSURE,
    assess_framing_pressure,
)
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
    """End-to-end pipeline §3.1 + §3.2 + §4a → §4b."""
    nan_modes = nan_modes or []
    suspended_modes = suspended_modes or []
    multi = assemble_multi_mode_labels(detections, nan_modes, suspended_modes)
    case_a = evaluate_case_a(detections, nan_modes, suspended_modes)
    sc = map_successor_classes(multi, case_a)
    return assess_framing_pressure(multi, case_a, sc)


# ---------- Mapping table fidelity (V6 anchor) ----------


def test_4b_single_finding_table_byte_identical_to_sealed_subspec():
    """SINGLE_FINDING_PRESSURE entries match sealed §4b lines 577-584 verbatim."""
    deferred_basis = (
        "framing question can stay deferred under (4) indeterminate; "
        "empirically-conditioned continuation defensible under any framing"
    )
    load_bearing_at_seal_basis = (
        "framing question becomes load-bearing at Phase 5 SEAL; "
        "pivot direction depends on framing; "
        "Charlie register engagement required at successor cycle entry"
    )
    assert SINGLE_FINDING_PRESSURE["signal_decay"] == (
        "deferred",
        "none",
        deferred_basis,
    )
    assert SINGLE_FINDING_PRESSURE["cost_drag"] == (
        "deferred",
        "none",
        deferred_basis,
    )
    assert SINGLE_FINDING_PRESSURE["cohort_weakness"] == (
        "load-bearing-at-Phase-5-SEAL",
        "depends-on-framing",
        load_bearing_at_seal_basis,
    )
    assert SINGLE_FINDING_PRESSURE["andgate_overfit"] == (
        "load-bearing-at-Phase-5-SEAL",
        "depends-on-framing",
        load_bearing_at_seal_basis,
    )
    assert SINGLE_FINDING_PRESSURE["success_metric_mismatch"] == (
        "ambiguous",
        "implicit-via-Phase-5-SEAL-surfacing",
        "ambiguous; Phase 5 SEAL surfaces framing engagement explicitly",
    )
    assert SINGLE_FINDING_PRESSURE["regime_change"] == (
        "load-bearing",
        "depends-on-framing-substantively",
        "framing question becomes load-bearing; pivot direction substantively determined by framing",
    )


# ---------- Single-finding mapping (session-2 actual + sibling sanity) ----------


def test_4b_single_finding_cost_drag_session_2_actual_case():
    """Session-2 actual input: only §2.b firing → single deferred pressure object."""
    r = _run(_detections(cost_drag=True))
    assert r["execution_suspended"] is False
    assert len(r["pressure_label_set"]) == 1
    obj = r["pressure_label_set"][0]
    assert obj == {
        "pressure_label": "deferred",
        "pivot_direction_dependency": "none",
        "basis": (
            "framing question can stay deferred under (4) indeterminate; "
            "empirically-conditioned continuation defensible under any framing"
        ),
        "propagation_state": "active",
        "context_qualifiers": [],
        "finding_source": "§2.b",
    }


def test_4b_single_finding_regime_change_emits_load_bearing():
    r = _run(_detections(regime_change=True))
    obj = r["pressure_label_set"][0]
    assert obj["pressure_label"] == "load-bearing"
    assert obj["finding_source"] == "§2.f"


def test_4b_single_finding_success_metric_mismatch_emits_ambiguous():
    r = _run(_detections(success_metric_mismatch=True))
    obj = r["pressure_label_set"][0]
    assert obj["pressure_label"] == "ambiguous"
    assert obj["finding_source"] == "§2.e"


# ---------- Multi-finding β union (no §4b-internal precedence) ----------


def test_4b_multi_finding_emits_union_with_no_internal_precedence():
    """§2.f + §2.a both fire → 2 pressure objects (β union); no collapse."""
    r = _run(_detections(signal_decay=True, regime_change=True))
    by_source = {o["finding_source"]: o for o in r["pressure_label_set"]}
    assert set(by_source.keys()) == {"§2.a", "§2.f"}
    # §2.f-derived: load-bearing.
    assert by_source["§2.f"]["pressure_label"] == "load-bearing"
    # §2.a-derived: deferred (NOT collapsed by §2.f's load-bearing).
    assert by_source["§2.a"]["pressure_label"] == "deferred"


# ---------- Qualifier-stripping rule (D2.5 β lock) ----------


def test_4b_qualifier_stripped_for_routing_but_carried_as_context_qualifiers():
    """§3.1 `regime-conditional signal-decay reading` → §4b routes on raw §2.a; carries regime-conditional as context_qualifiers."""
    r = _run(_detections(signal_decay=True, regime_change=True))
    by_source = {o["finding_source"]: o for o in r["pressure_label_set"]}
    sa = by_source["§2.a"]
    # Routing on raw §2.a → deferred (NOT shifted by qualifier).
    assert sa["pressure_label"] == "deferred"
    # Qualifier preserved as context_qualifiers field.
    assert "regime-conditional" in sa["context_qualifiers"]


def test_4b_andgate_plus_cohort_emits_both_findings_with_gate_validity_conditioned_on_cohort():
    """§2.d + §2.c → both pressure objects emit (§2.d-direct + §2.c with gate-validity-conditioned)."""
    r = _run(_detections(andgate_overfit=True, cohort_weakness=True))
    by_source = {o["finding_source"]: o for o in r["pressure_label_set"]}
    assert set(by_source.keys()) == {"§2.c", "§2.d"}
    # Both have same pressure label per (c)/(d) verbatim; finding_source distinguishes them.
    assert by_source["§2.c"]["pressure_label"] == "load-bearing-at-Phase-5-SEAL"
    assert by_source["§2.d"]["pressure_label"] == "load-bearing-at-Phase-5-SEAL"
    # §2.c gets gate-validity-conditioned qualifier; §2.d does not.
    assert "gate-validity-conditioned" in by_source["§2.c"]["context_qualifiers"]
    assert by_source["§2.d"]["context_qualifiers"] == []


# ---------- Case A terminal-conclusion finding (scalar) ----------


def test_4b_case_a_emits_load_bearing_immediately_scalar():
    """§3.2 Case A canonical → single load-bearing-immediately pressure object with terminal-conclusion finding_source."""
    r = _run(_detections())  # all False
    assert len(r["pressure_label_set"]) == 1
    obj = r["pressure_label_set"][0]
    assert obj["pressure_label"] == "load-bearing-immediately"
    assert obj["pivot_direction_dependency"] == "project-identity-engagement-implicit"
    assert obj["finding_source"] == "terminal-conclusion"
    assert obj["propagation_state"] == "active"
    # §4b does NOT pre-name framing-question resolution (anti-circularity (vii)).
    assert "framing_resolution" not in obj


def test_4b_terminal_conclusion_co_fire_preserves_both_objects_per_codex_high_3():
    """Codex HIGH-3 regression: synthetic Case A canonical + §3.1 firing should NOT
    silently drop terminal-conclusion pressure object per sealed §4b D2.2 line 592.

    At canonical execution (XOR complementarity) this state cannot arise via
    evaluate_case_a; construct the upstream state manually to verify §4b preserves
    co-fire diagnostic signal per sealed prose "NO §4b silent collapse".
    """
    from phase5.framing_pressure import assess_framing_pressure
    from phase5.successor_class import map_successor_classes

    synthetic_multi = {
        "emits_substantive": True,
        "execution_suspended": False,
        "firing_modes": ["signal_decay"],
        "not_detected_modes": [],
        "nan_modes": [],
        "per_mode_labels": {"signal_decay": "signal-decay reading"},
        "partition_table": [],
        "indeterminate_labels": {},
    }
    synthetic_case_a = {
        "label": "no-mode-detected reading",
        "terminal_trigger": {
            "triggered": True,
            "basis": {"canonical_0_mode": True, "suspended_modes": [], "nan_modes": []},
        },
        "execution_suspended": False,
    }
    sc = map_successor_classes(synthetic_multi, synthetic_case_a)
    r = assess_framing_pressure(synthetic_multi, synthetic_case_a, sc)
    sources = {o["finding_source"] for o in r["pressure_label_set"]}
    assert "terminal-conclusion" in sources, (
        "Codex HIGH-3 regression: terminal-conclusion pressure must NOT be dropped "
        "during co-fire per sealed §4b D2.2 line 592 'NO silent collapse' discipline"
    )
    assert "§2.a" in sources, "signal_decay firing pressure must also emit"


# ---------- NaN propagation (D2.4 γ) ----------


def test_4b_upstream_indeterminacy_propagated_when_nan_at_signal_decay():
    """§2.a NaN with cost_drag firing → cost_drag pressure object active + signal_decay indeterminate-propagated."""
    r = _run(_detections(cost_drag=True), nan_modes=["signal_decay"])
    sources = {o["finding_source"]: o for o in r["pressure_label_set"]}
    # cost_drag active per §2.b mapping.
    assert sources["§2.b"]["pressure_label"] == "deferred"
    assert sources["§2.b"]["propagation_state"] == "active"
    # signal_decay indeterminate-propagated.
    assert sources["§2.a"]["pressure_label"] is None
    assert sources["§2.a"]["propagation_state"] == "upstream-indeterminacy-propagated"


# ---------- Execution-suspended (ε') hybrid propagation ----------


def test_4b_upstream_suspension_propagates_to_4b_suspension():
    """Upstream §2.x self-suspended → §4b execution suspends."""
    r = _run(_detections(), suspended_modes=["regime_change"])
    assert r["execution_suspended"] is True


# ---------- Anti-pre-emption discipline (V10 anchor) ----------


def test_4b_no_pre_naming_of_framing_resolution_5_or_6_in_output():
    """§4b output schema must not contain framing-resolution / §5 admissibility / §6 narrative content."""
    r = _run(_detections(cost_drag=True))
    forbidden_top_level = {"framing_resolution", "substantive", "operational", "narrative"}
    assert not (forbidden_top_level & set(r.keys()))
    for o in r["pressure_label_set"]:
        forbidden_per_obj = {"framing_resolved", "admissible", "narrative_text"}
        assert not (forbidden_per_obj & set(o.keys()))

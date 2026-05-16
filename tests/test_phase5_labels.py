"""Smoke tests for §3.1 multi-mode rule-tree + §3.2 ambiguity disposition.

Tests the deterministic label assembly + Case A condition evaluation against
sealed prose at docs/phase5/PHASE5_DIAGNOSTIC_SUBSPEC.md §3.1 + §3.2.
"""

from __future__ import annotations

from phase5.labels.ambiguity_disposition import evaluate_case_a
from phase5.labels.multi_mode_rules import (
    BASE_LABELS,
    assemble_multi_mode_labels,
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


def test_3_1_single_mode_signal_decay_only():
    """Single-mode §2.a fires → base label 'signal-decay reading' without modifier."""
    r = assemble_multi_mode_labels(_detections(signal_decay=True))
    assert r["emits_substantive"] is True
    assert r["firing_modes"] == ["signal_decay"]
    assert r["per_mode_labels"]["signal_decay"] == "signal-decay reading"


def test_3_1_regime_conditional_prefix_on_signal_decay_when_regime_change_fires():
    """§2.f + §2.a fires → 'regime-conditional signal-decay reading (with bilateral attribution caveat)'."""
    r = assemble_multi_mode_labels(_detections(signal_decay=True, regime_change=True))
    assert r["emits_substantive"] is True
    label = r["per_mode_labels"]["signal_decay"]
    assert label == "regime-conditional signal-decay reading (with bilateral attribution caveat)"
    # §2.f itself carries no Line 1 modifier (upstream source).
    assert r["per_mode_labels"]["regime_change"] == "regime-change-detected reading"


def test_3_1_forward_applicability_conditioned_prefix_on_cohort_weakness_when_regime_change_fires():
    """§2.f + §2.c fires → 'forward-applicability-conditioned cohort-substrate-weakness reading' (no bilateral suffix on §2.c)."""
    r = assemble_multi_mode_labels(_detections(cohort_weakness=True, regime_change=True))
    label = r["per_mode_labels"]["cohort_weakness"]
    assert label == "forward-applicability-conditioned cohort-substrate-weakness reading"


def test_3_1_gate_validity_conditioned_on_cohort_weakness_when_andgate_fires():
    """§2.d + §2.c fires → 'gate-validity-conditioned cohort-substrate-weakness reading'."""
    r = assemble_multi_mode_labels(_detections(cohort_weakness=True, andgate_overfit=True))
    assert (
        r["per_mode_labels"]["cohort_weakness"]
        == "gate-validity-conditioned cohort-substrate-weakness reading"
    )
    # §2.d itself: no Line 2 modifier on §2.d (upstream source).
    assert r["per_mode_labels"]["andgate_overfit"] == "AND-gate-overfit reading"


def test_3_1_stacked_modifiers_regime_change_andgate_cohort():
    """§2.f + §2.d + §2.c stacked: forward-applicability-conditioned gate-validity-conditioned cohort-substrate-weakness."""
    r = assemble_multi_mode_labels(
        _detections(regime_change=True, andgate_overfit=True, cohort_weakness=True)
    )
    label = r["per_mode_labels"]["cohort_weakness"]
    # Composition order per sealed: Line 1 (§2.f) → Line 2 (§2.d) → base. So Line 1 prefix is outermost.
    assert (
        label
        == "forward-applicability-conditioned gate-validity-conditioned cohort-substrate-weakness reading"
    )


def test_3_1_silent_state_at_0_mode():
    """0 modes detected → §3.1 silent (no substantive output)."""
    r = assemble_multi_mode_labels(_detections())
    assert r["emits_substantive"] is False
    assert r["partition_table"] == []


def test_3_1_execution_suspended_when_upstream_suspended():
    """Suspended §2.x → §3.1 execution suspends per (ε') execution-invalidity branch."""
    r = assemble_multi_mode_labels(_detections(), suspended_modes=["regime_change"])
    assert r["execution_suspended"] is True
    assert "regime_change" in r["suspended_modes"]


def test_3_1_indeterminate_regime_change_absorbs_candidate_level():
    """§2.f indeterminate → absorbing-propagation labels for all candidate-level modes."""
    detections = _detections()
    detections["regime_change"] = None
    r = assemble_multi_mode_labels(detections, nan_modes=["regime_change"])
    ind = r["indeterminate_labels"]
    assert ind["signal_decay"] == "indeterminate-regime-conditional signal-decay reading"
    assert ind["cost_drag"] == "indeterminate-regime-conditional cost-drag reading"
    assert (
        ind["success_metric_mismatch"]
        == "indeterminate-regime-conditional success-metric-mismatch reading"
    )
    assert (
        ind["cohort_weakness"]
        == "indeterminate-forward-applicability-conditioned cohort-substrate-weakness reading"
    )
    assert (
        ind["andgate_overfit"]
        == "indeterminate-forward-applicability-conditioned AND-gate-overfit reading"
    )


def test_3_1_indeterminate_andgate_absorbs_cohort_weakness_only():
    """§2.d indeterminate → absorbing-propagation §2.c only per §2.d-specific gate scope."""
    detections = _detections()
    detections["andgate_overfit"] = None
    r = assemble_multi_mode_labels(detections, nan_modes=["andgate_overfit"])
    ind = r["indeterminate_labels"]
    assert (
        ind["cohort_weakness"]
        == "indeterminate-gate-validity-conditioned cohort-substrate-weakness reading"
    )
    assert ind["andgate_overfit"] == "indeterminate AND-gate-overfit reading"
    # Other modes unaffected.
    assert "signal_decay" not in ind
    assert "cost_drag" not in ind


# ---------------------------------------------------------------------------
# §3.2 Case A condition evaluation
# ---------------------------------------------------------------------------


def test_3_2_case_a_fires_when_all_not_detected():
    r = evaluate_case_a(_detections())
    assert r["label"] == "no-mode-detected reading"
    assert r["terminal_trigger"]["triggered"] is True
    assert r["terminal_trigger"]["basis"]["canonical_0_mode"] is True
    assert r["terminal_trigger"]["basis"]["suspended_modes"] == []
    assert r["terminal_trigger"]["basis"]["nan_modes"] == []
    assert r.get("silent_state") is not True


def test_3_2_silent_when_any_mode_detected():
    """§3.1 ↔ §3.2 XOR complementarity: §3.2 silent when ≥1 §2.x detected."""
    r = evaluate_case_a(_detections(signal_decay=True))
    assert r["label"] is None
    assert r["terminal_trigger"] is None
    assert r["silent_state"] is True
    assert "signal_decay" in r["firing_modes"]


def test_3_2_indeterminate_case_a_when_any_nan():
    """NaN at any §2.x → indeterminate-Case-A reading."""
    detections = _detections()
    detections["cost_drag"] = None
    r = evaluate_case_a(detections, nan_modes=["cost_drag"])
    assert r["label"] == "indeterminate-Case-A reading"
    assert r["terminal_trigger"]["triggered"] is False
    assert r["terminal_trigger"]["basis"]["canonical_0_mode"] is False
    assert "cost_drag" in r["terminal_trigger"]["basis"]["nan_modes"]


def test_3_2_execution_suspended_when_upstream_suspended():
    detections = _detections()
    detections["regime_change"] = None
    r = evaluate_case_a(detections, suspended_modes=["regime_change"])
    assert r["execution_suspended"] is True
    assert "regime_change" in r["suspended_modes"]


def test_3_2_input_space_canonical_check_rejects_unexpected_modes():
    """Sealed §3.2 V# anchor: verify input space canonical-ness (6 expected modes)."""
    bad = {"signal_decay": False}  # missing 5 expected modes
    r = evaluate_case_a(bad)
    assert r["execution_suspended"] is True
    assert r["suspension_cause"] == "input_space_canonical_check_failed"


def test_3_2_xor_complementarity_with_3_1():
    """Sealed §3.1 ↔ §3.2 XOR firing pattern: never both, never neither (at canonical binary inputs)."""
    for fire_mask in [
        {},
        {"signal_decay": True},
        {"cost_drag": True, "regime_change": True},
        {"andgate_overfit": True, "cohort_weakness": True},
    ]:
        det = _detections(**fire_mask)
        r3_1 = assemble_multi_mode_labels(det)
        r3_2 = evaluate_case_a(det)
        s1 = r3_1["emits_substantive"]
        s2 = r3_2.get("label") == "no-mode-detected reading"
        assert s1 != s2, f"XOR violation at fire_mask={fire_mask}: §3.1 emits={s1} §3.2 fires={s2}"


def test_3_1_base_labels_match_sealed_prose():
    """Sealed §3.1 Categorical label set: verbatim base labels."""
    assert BASE_LABELS["signal_decay"] == "signal-decay reading"
    assert BASE_LABELS["cost_drag"] == "cost-drag reading"
    assert BASE_LABELS["cohort_weakness"] == "cohort-substrate-weakness reading"
    assert BASE_LABELS["andgate_overfit"] == "AND-gate-overfit reading"
    assert BASE_LABELS["success_metric_mismatch"] == "success-metric-mismatch reading"
    assert BASE_LABELS["regime_change"] == "regime-change-detected reading"

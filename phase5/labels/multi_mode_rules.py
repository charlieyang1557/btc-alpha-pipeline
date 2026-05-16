"""§3.1 Multi-mode coexistence — rule-tree label assembly.

Sealed prose at docs/phase5/PHASE5_DIAGNOSTIC_SUBSPEC.md §3.1 (sealed at
6e5fd91; D3''''''^a lock). δ hybrid framing: rule-tree primary + supplementary
partition mapping. Compositional label assembly per Line/Tier/Residual structure
with locked composition order.
"""

from __future__ import annotations

from typing import Any

# Base labels (6, one per §2.x mode) per sealed §3.1 Categorical label set.
BASE_LABELS = {
    "signal_decay": "signal-decay reading",
    "cost_drag": "cost-drag reading",
    "cohort_weakness": "cohort-substrate-weakness reading",
    "andgate_overfit": "AND-gate-overfit reading",
    "success_metric_mismatch": "success-metric-mismatch reading",
    "regime_change": "regime-change-detected reading",
}

# Line 1 modifier — 2 sub-modifier classes per sealed §3.1 D1''''''^a Line 1 re-lock.
LINE1_REGIME_CONDITIONAL_MODES = {"signal_decay", "cost_drag", "success_metric_mismatch"}
LINE1_FORWARD_APPLICABILITY_MODES = {"cohort_weakness", "andgate_overfit"}

# Modes that are §2.f-bilateral-applicable per sealed §2.f anti-circularity (A)/(B)/(C).
TIER_BILATERAL_MODES = {"signal_decay", "cost_drag", "success_metric_mismatch"}


def _compositional_label(
    mode_key: str,
    regime_change_fires: bool,
    andgate_fires: bool,
) -> str:
    """Assemble compositional label per locked composition order:

        Line 1 modifier (§2.f) → Line 2 modifier (§2.d on §2.c only) → Tier bilateral overlay → base label.
    """
    base = BASE_LABELS[mode_key]

    # Line 2: gate-validity-conditioned on §2.c only when §2.d fires.
    if mode_key == "cohort_weakness" and andgate_fires:
        base = f"gate-validity-conditioned {base}"

    # Line 1: regime-conditional vs forward-applicability-conditioned per §2.f anti-circularity.
    if regime_change_fires and mode_key != "regime_change":
        if mode_key in LINE1_REGIME_CONDITIONAL_MODES:
            base = f"regime-conditional {base}"
        elif mode_key in LINE1_FORWARD_APPLICABILITY_MODES:
            base = f"forward-applicability-conditioned {base}"

    # Tier bilateral overlay: parenthetical suffix on §2.a/§2.b/§2.e when §2.f fires alongside.
    if regime_change_fires and mode_key in TIER_BILATERAL_MODES:
        base = f"{base} (with bilateral attribution caveat)"

    return base


def assemble_multi_mode_labels(
    detections: dict[str, bool | None],
    nan_modes: list[str] | None = None,
    suspended_modes: list[str] | None = None,
) -> dict[str, Any]:
    """Assemble §3.1 multi-mode composite categorical labels + partition table rows.

    detections: per-mode binary detection state {mode_key: True | False | None}.
        None denotes (ε'-narrow) indeterminate or suspended state — surfaced via
        nan_modes / suspended_modes parameters for §3.1 (ε') hybrid handling.

    Returns dict with:
      - emits_substantive: bool (§3.1 fires labels iff >=1 §2.x detected at canonical binary register)
      - partition_table: list of partition table row dicts
      - per_mode_labels: dict {mode_key: label} for firing modes only
      - indeterminate_propagation: per sealed §3.1 (ε') hybrid + (b-symm-improved) absorbing rules
    """
    nan_modes = nan_modes or []
    suspended_modes = suspended_modes or []

    # Execution invalidity short-circuit per (ε') execution-invalidity branch.
    if suspended_modes:
        return {
            "emits_substantive": False,
            "execution_suspended": True,
            "suspension_cause": "upstream_§2.x_self_suspended",
            "suspended_modes": suspended_modes,
            "narrative_anchor": (
                "§3.1 execution suspends; §6 enumerates the discrepancy; "
                "Charlie register re-adjudicates per §2.d D2''' / §2.f "
                "parquet-mismatch suspension precedent"
            ),
        }

    # Identify firing modes (canonical binary detected=True only).
    firing_modes = [m for m, d in detections.items() if d is True]
    not_detected_modes = [m for m, d in detections.items() if d is False]

    # §3.1 emits substantive output iff >=1 §2.x at canonical detected register.
    emits_substantive = len(firing_modes) >= 1

    regime_change_fires = "regime_change" in firing_modes
    andgate_fires = "andgate_overfit" in firing_modes

    per_mode_labels: dict[str, str] = {}
    for m in firing_modes:
        per_mode_labels[m] = _compositional_label(m, regime_change_fires, andgate_fires)

    # Handle indeterminate-propagation per sealed §3.1 (b-symm-improved) absorbing rules.
    indeterminate_labels: dict[str, str] = {}
    if "regime_change" in nan_modes:
        # §2.f indeterminate absorbs all candidate-level readings per Line 1 universe-upstream scope.
        for m in BASE_LABELS:
            if m == "regime_change":
                indeterminate_labels[m] = f"indeterminate {BASE_LABELS[m]}"
            elif m in LINE1_REGIME_CONDITIONAL_MODES:
                indeterminate_labels[m] = (
                    f"indeterminate-regime-conditional {BASE_LABELS[m]}"
                )
            elif m in LINE1_FORWARD_APPLICABILITY_MODES:
                indeterminate_labels[m] = (
                    f"indeterminate-forward-applicability-conditioned {BASE_LABELS[m]}"
                )
    elif "andgate_overfit" in nan_modes:
        # §2.d indeterminate absorbs §2.c only per §2.d-specific gate scope.
        indeterminate_labels["andgate_overfit"] = (
            f"indeterminate {BASE_LABELS['andgate_overfit']}"
        )
        if "cohort_weakness" not in nan_modes:
            indeterminate_labels["cohort_weakness"] = (
                f"indeterminate-gate-validity-conditioned {BASE_LABELS['cohort_weakness']}"
            )
    # Locally-scoped per-mode (ε'-narrow) NaN for non-upstream-conditioning modes.
    for m in nan_modes:
        if m in {"regime_change", "andgate_overfit"}:
            continue
        if m in indeterminate_labels:
            continue
        indeterminate_labels[m] = f"indeterminate {BASE_LABELS[m]}"

    # Build partition table: one row per firing mode at execution time
    # (sealed §3.1: "execution enumerates partition rows based on actual §2.x
    # output combination at §3.1 execution time").
    partition_table: list[dict[str, Any]] = []
    if emits_substantive:
        for m in firing_modes:
            partition_table.append(
                {
                    "active_modes": sorted(firing_modes),
                    "mode": m,
                    "categorical_label": per_mode_labels[m],
                    "line1_regime_change_fires": regime_change_fires,
                    "line2_andgate_fires": andgate_fires,
                    "tier_bilateral_applicable": m in TIER_BILATERAL_MODES
                    and regime_change_fires,
                    "downstream_consumer_note": (
                        "Resolved at §6 narrative; specific successor-class "
                        "mapping is §4a scope; framing-resolution-pressure "
                        "is §4b scope; admissibility is §5 scope."
                    ),
                }
            )

    return {
        "emits_substantive": emits_substantive,
        "execution_suspended": False,
        "firing_modes": sorted(firing_modes),
        "not_detected_modes": sorted(not_detected_modes),
        "nan_modes": sorted(nan_modes),
        "per_mode_labels": per_mode_labels,
        "partition_table": partition_table,
        "indeterminate_labels": indeterminate_labels,
        "composition_order": "Line 1 (§2.f) → Line 2 (§2.d on §2.c only) → Tier bilateral overlay → base label",
        "register_class": "binding | rule-based primary + categorical interpretation outputs (no new thresholds)",
    }

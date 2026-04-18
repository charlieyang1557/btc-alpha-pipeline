"""D7 Stage 2a — replay candidate selection from a signed-off Stage 2d batch.

Scans a Stage 2d summary and selects the first call that passes all seven
selection criteria for use as the forensic replay target. If no candidate
passes, prints a diagnostic breakdown and exits non-zero.

Selection criteria (all must hold):
    1. lifecycle_state == "pending_backtest"
    2. theme != "momentum"
    3. ``n_factors_range[0]`` <= len(factors_used) <= ``n_factors_range[1]``
       (defaults to Stage 2a's ``(3, 5)``; Stage 2b's N=5 path widens the
       upper bound to ``7`` to match the D6 proposer's empirical factor-
       count distribution — see ``STAGE2A_N_FACTORS_RANGE`` /
       ``STAGE2B_N_FACTORS_RANGE`` below)
    4. At least one crosses_above or crosses_below operator in the DSL
    5. rsi_14 is not the sole factor
    6. position in [10, 190]
    7. thin_theme_momentum_bleed flag would NOT fire on this call
       (routed through ``agents.critic.d7a_feature_extraction.
       is_thin_theme_momentum_bleed`` — the same predicate used by
       ``d7a_rules.compute_rule_flags``, so selection and flag evaluation
       cannot drift).

NOTE on criterion 7: this is a probe-QUALITY filter, not a probe-VALIDITY
filter. The goal is to pick a replay candidate whose critique is
informative on its own semantic merits rather than dominated by a
known-to-fire D7a flag. Relaxing this criterion (e.g., to admit
flagged candidates for the explicit purpose of auditing the flag's
behavior in the live critic) is a deliberate research decision that
MUST be documented in the acceptance notebook and in
``docs/d7_stage2a/replay_candidate_expectations.md`` before re-running
selection.

Determinism: scan order is ``sorted(calls, key=(position, hypothesis_hash))``
so two invocations of this script against the same ``stage2d_summary.json``
return the same candidate even if the summary's native ordering changes
across serialization layers.

The script reads signed-off artifacts only. It never generates new DSLs,
never mutates on-disk state, and never imports anthropic.
"""

from __future__ import annotations

import argparse
import datetime
import json
import sys
from pathlib import Path


# Allow bare ``python scripts/select_replay_candidate.py`` invocation
# from the repo root without requiring ``python -m`` or PYTHONPATH export.
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from agents.critic.d7a_feature_extraction import (  # noqa: E402
    compute_max_overlap,
    is_thin_theme_momentum_bleed,
)


# -----------------------------------------------------------------------
# Selection criteria
# -----------------------------------------------------------------------

MIN_POSITION = 10
MAX_POSITION = 190

# Factor-count range is split by selection scope.
#
# * Stage 2a (N=1) retains ``(3, 5)`` — the signed-off Stage 2a selection
#   artifact at ``docs/d7_stage2a/replay_candidate_selection.json`` was
#   produced under this criterion and must remain reproducible. Widening
#   the range here retroactively would invalidate that sign-off.
#
# * Stage 2b (N=5) widens the upper bound to ``7`` because an empirical
#   diagnostic against the signed-off Stage 2d batch
#   ``5cf76668-47d1-48d7-bd90-db06d31982ed`` showed the D6 proposer's
#   factor-count distribution is modal at ``n_factors=6`` (68 calls),
#   with 36 calls at ``n_factors=7`` and only one outlier at
#   ``n_factors=8``. Retaining the original ``(3, 5)`` cap filters out
#   ~66% of non-momentum candidates, making the Stage 2b hard constraints
#   (>=3 themes, all 3 buckets, 5 candidates) infeasible.
#
# CONTRACT BOUNDARY: these two constants are deliberately kept separate.
# Do not collapse them into a single module-level constant; ``--n 1`` and
# ``--n 5`` code paths must remain independently auditable.
STAGE2A_N_FACTORS_RANGE: tuple[int, int] = (3, 5)
STAGE2B_N_FACTORS_RANGE: tuple[int, int] = (3, 7)

# -----------------------------------------------------------------------
# Stage 2c — N=20 selection constants
#
# Stage 2c extends Stage 2b's N=5 path to select 20 replay candidates
# for the full forensic sweep. Per-candidate criteria (the seven rules
# enforced by ``passes_selection``) and the factor-count range
# (``STAGE2B_N_FACTORS_RANGE``) are inherited verbatim — Stage 2c does
# not introduce a new per-candidate gate. The scaling happens at the
# cross-candidate constraint layer:
#
#   * Bucket coverage: early/mid/late each require >= 5 candidates
#     (scaled from Stage 2b's >= 1). Total bucket-forced picks = 15.
#   * Theme diversity: >= 3 themes (unchanged; pool-limited).
#   * Agreement floor: >= 4 ``agreement_expected`` candidates in the
#     selection. This is a HARD constraint at all tiers, never relaxed,
#     pre-checked against the pool before any tier attempt.
#   * Unique hypothesis hashes (unchanged).
#
# Soft tier ladder (fixed order):
#   * Tier 0: >= 2 cross-theme ``divergence_expected`` candidates.
#   * Tier 1: >= 1 ``divergence_expected`` candidate, with two sub-cases
#     tried in order — two same-theme divergences first (more coverage),
#     then a single divergence as a further fallback.
#   * Tier 2: zero divergence coverage; agreement floor still enforced.
#
# CONTRACT BOUNDARY: ``STAGE2B_N_FACTORS_RANGE`` is REUSED by Stage 2c
# (not renamed / not duplicated). The factor-count bound is a property
# of the D6 proposer's empirical distribution, not of the selection
# fan-out. Do not introduce a ``STAGE2C_N_FACTORS_RANGE`` constant; a
# Stage 2c code path that read its own range would desynchronize from
# Stage 2b's pool-eligibility rules.
STAGE2C_N_CANDIDATES: int = 20
STAGE2C_THEMES_MIN: int = 3
STAGE2C_BUCKET_MIN: int = 5
STAGE2C_AGREEMENT_FLOOR: int = 4
STAGE2C_TIER_0_DIVERGENCE_MIN: int = 2
STAGE2C_TIER_1_DIVERGENCE_MIN: int = 1


def _has_cross_operator(response_text: str) -> bool:
    """Check whether the raw response contains a cross operator.

    Parses the JSON DSL from the response and looks for
    ``crosses_above`` or ``crosses_below`` in any condition's
    ``operator`` field. Falls back to a plain substring search if
    JSON parsing fails (defensive).
    """
    try:
        payload = json.loads(response_text)
        if isinstance(payload, dict):
            return _scan_conditions_for_cross(payload)
    except (json.JSONDecodeError, KeyError, TypeError):
        pass
    return "crosses_above" in response_text or "crosses_below" in response_text


def _scan_conditions_for_cross(dsl: dict) -> bool:
    """Walk entry/exit groups looking for cross operators."""
    for block_key in ("entry", "exit"):
        block = dsl.get(block_key)
        if not isinstance(block, list):
            continue
        for group in block:
            if not isinstance(group, dict):
                continue
            conditions = group.get("conditions", [])
            if not isinstance(conditions, list):
                continue
            for cond in conditions:
                op = cond.get("op") or cond.get("operator", "")
                if op in ("crosses_above", "crosses_below"):
                    return True
    return False


def _call_would_trigger_thin_theme_momentum_bleed(call: dict) -> bool:
    """Check whether this call would trigger the D7a ``thin_theme_momentum_bleed`` flag.

    Adapts a Stage 2d per-call summary record to the canonical predicate
    in ``agents.critic.d7a_feature_extraction.is_thin_theme_momentum_bleed``.
    The per-call record exposes ``default_momentum_factors_used`` as a
    list of distinct factor names; its length is the exact input the
    predicate expects.
    """
    theme = call.get("theme", "")
    momentum_used = call.get("default_momentum_factors_used") or []
    return is_thin_theme_momentum_bleed(theme, len(momentum_used))


def passes_selection(
    call: dict,
    *,
    batch_dir: Path,
    batch_uuid: str,
    n_factors_range: tuple[int, int] = STAGE2A_N_FACTORS_RANGE,
) -> tuple[bool, str]:
    """Check all seven criteria. Returns (pass, reason).

    ``n_factors_range`` controls the factor-count criterion and defaults
    to the Stage 2a ``(3, 5)`` range so that the N=1 path (and any caller
    that doesn't opt into the widened Stage 2b range explicitly) retains
    byte-identical behavior. Stage 2b's ``build_eligible_pool`` passes
    ``STAGE2B_N_FACTORS_RANGE`` to widen the upper bound to ``7``.
    """
    pos = call.get("position")
    min_factors, max_factors = n_factors_range

    if call.get("lifecycle_state") != "pending_backtest":
        return False, "lifecycle_state != pending_backtest"

    if call.get("theme") == "momentum":
        return False, "theme == momentum"

    factors = call.get("factors_used") or []
    if not (min_factors <= len(factors) <= max_factors):
        return False, f"n_factors={len(factors)} outside [{min_factors},{max_factors}]"

    if factors == ["rsi_14"]:
        return False, "rsi_14 is sole factor"

    if pos is None or not (MIN_POSITION <= pos <= MAX_POSITION):
        return False, f"position={pos} outside [{MIN_POSITION},{MAX_POSITION}]"

    if _call_would_trigger_thin_theme_momentum_bleed(call):
        return False, "thin_theme_momentum_bleed would fire"

    response_path = _find_response_path(batch_dir, pos)
    if response_path is None:
        return False, f"response file not found for position {pos}"

    try:
        response_text = response_path.read_text(encoding="utf-8")
    except OSError as exc:
        return False, f"cannot read response: {exc}"

    if not _has_cross_operator(response_text):
        return False, "no crosses_above/crosses_below operator"

    return True, "all criteria met"


def _find_response_path(batch_dir: Path, position: int) -> Path | None:
    """Locate the response file for a position, handling retries."""
    primary = batch_dir / f"attempt_{position:04d}_response.txt"
    if primary.exists():
        return primary
    retries = sorted(
        batch_dir.glob(f"attempt_{position:04d}_retry_*_response.txt")
    )
    if retries:
        return retries[-1]
    return None


# -----------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------


def select_candidate(
    batch_uuid: str,
    *,
    artifacts_root: Path = Path("raw_payloads"),
    summary_name: str = "stage2d_summary.json",
) -> dict | None:
    """Return the first call record passing all criteria, or None."""
    batch_dir = artifacts_root / f"batch_{batch_uuid}"
    summary_path = batch_dir / summary_name

    if not summary_path.exists():
        print(
            f"[select] summary not found: {summary_path}\n"
            f"[select] batch {batch_uuid} may not exist in {artifacts_root}/",
            file=sys.stderr,
        )
        return None

    with summary_path.open(encoding="utf-8") as fh:
        summary = json.load(fh)

    calls: list[dict] = summary.get("calls", [])
    if not calls:
        print("[select] summary has no calls", file=sys.stderr)
        return None

    # Deterministic scan order: position ascending, then hypothesis_hash
    # lexicographic as a stable tiebreak. This pins the selection to a
    # reproducible candidate even if the upstream summary's native
    # ordering shifts across serialization or aggregation layers.
    calls = sorted(
        calls,
        key=lambda c: (
            c.get("position", float("inf")),
            c.get("hypothesis_hash", ""),
        ),
    )

    rejection_reasons: dict[str, int] = {}
    for call in calls:
        ok, reason = passes_selection(
            call, batch_dir=batch_dir, batch_uuid=batch_uuid,
        )
        if ok:
            return call
        rejection_reasons[reason] = rejection_reasons.get(reason, 0) + 1

    print(
        f"[select] no candidate passed all criteria "
        f"({len(calls)} calls examined):",
        file=sys.stderr,
    )
    for reason, count in sorted(
        rejection_reasons.items(), key=lambda x: -x[1]
    ):
        print(f"  {count:4d}  {reason}", file=sys.stderr)
    return None


# -----------------------------------------------------------------------
# Stage 2b — N=5 selection (constraint-first targeted slot-filling)
#
# The N=5 path is strictly additive on top of the Stage 2a N=1 behavior.
# The per-candidate criteria (the seven rules enforced by
# ``passes_selection``) are reused verbatim; Stage 2b adds cross-candidate
# hard constraints (>=3 themes, early/mid/late bucket coverage, unique
# hypothesis hashes) and a soft divergence-coverage preference that
# degrades in three fixed tiers.
# -----------------------------------------------------------------------

STAGE2B_DEFAULT_OUTPUT = Path("docs/d7_stage2b/replay_candidates.json")
STAGE2B_STAGE_LABEL = "d7_stage2b"
STAGE2B_RECORD_VERSION = "1.0"

POSITION_BUCKETS: tuple[tuple[str, int, int], ...] = (
    ("early", 10, 66),
    ("mid", 67, 133),
    ("late", 134, 190),
)
BUCKET_NAMES: tuple[str, ...] = tuple(b[0] for b in POSITION_BUCKETS)

ALL_REJECTION_KEYS: tuple[str, ...] = (
    "lifecycle_not_pending_backtest",
    "theme_is_momentum",
    "factor_count_out_of_range",
    "no_cross_operator",
    "rsi14_is_sole_factor",
    "position_out_of_range",
    "thin_theme_momentum_bleed",
)

AGREEMENT_LABEL = "agreement_expected"
DIVERGENCE_LABEL = "divergence_expected"
NEUTRAL_LABEL = "neutral"


def _position_bucket(position: int | None) -> str | None:
    """Return bucket name for a valid position, or None if out of range."""
    if position is None:
        return None
    for name, lo, hi in POSITION_BUCKETS:
        if lo <= position <= hi:
            return name
    return None


def _rejection_key(reason: str) -> str:
    """Map freeform rejection reason to one of the seven bucketed keys."""
    if reason.startswith("lifecycle_state"):
        return "lifecycle_not_pending_backtest"
    if reason.startswith("theme == momentum"):
        return "theme_is_momentum"
    if reason.startswith("n_factors="):
        return "factor_count_out_of_range"
    if reason.startswith("rsi_14 is sole"):
        return "rsi14_is_sole_factor"
    if reason.startswith("position="):
        return "position_out_of_range"
    if reason.startswith("thin_theme_momentum_bleed"):
        return "thin_theme_momentum_bleed"
    # Remaining: missing/unreadable response or no cross operator all fall
    # into "no_cross_operator" for audit purposes — a call without a
    # parseable DSL containing a cross operator cannot be a valid replay.
    return "no_cross_operator"


def compute_relationship_label(
    factor_set_prior_occurrences: int,
    f_current: set[str],
    f_priors: list[set[str]],
) -> str:
    """agreement_expected / divergence_expected / neutral."""
    if factor_set_prior_occurrences > 0:
        return AGREEMENT_LABEL
    max_overlap = compute_max_overlap(f_current, f_priors)
    if max_overlap <= 2:
        return DIVERGENCE_LABEL
    return NEUTRAL_LABEL


def build_eligible_pool(
    summary: dict,
    *,
    batch_dir: Path,
    batch_uuid: str,
) -> dict:
    """Filter calls by per-candidate criteria and enrich survivors.

    Returns a dict with keys:
        pool: list of enriched candidate dicts (sorted by position asc,
            hypothesis_hash lexicographic as tiebreak).
        rejection_breakdown: dict with all 7 rejection keys populated.
        pool_size_total: total number of calls in the summary.
        pool_size_passing: number of candidates that passed all criteria.
    """
    calls = list(summary.get("calls", []))
    total = len(calls)
    calls_sorted = sorted(
        calls,
        key=lambda c: (
            c.get("position", float("inf")),
            c.get("hypothesis_hash", ""),
        ),
    )

    breakdown = {k: 0 for k in ALL_REJECTION_KEYS}
    passing_calls: list[dict] = []
    for call in calls_sorted:
        ok, reason = passes_selection(
            call,
            batch_dir=batch_dir,
            batch_uuid=batch_uuid,
            n_factors_range=STAGE2B_N_FACTORS_RANGE,
        )
        if ok:
            passing_calls.append(call)
        else:
            breakdown[_rejection_key(reason)] += 1

    # Enrich passing candidates with prior-occurrence / overlap / label.
    # Priors are the distinct, non-empty factor sets of candidates that
    # precede the current one in the deterministic scan order.
    occurrence_counter: dict[tuple[str, ...], int] = {}
    seen_factor_sets: set[tuple[str, ...]] = set()
    distinct_priors: list[set[str]] = []

    pool: list[dict] = []
    for call in passing_calls:
        factors_tuple: tuple[str, ...] = tuple(
            sorted(call.get("factors_used") or [])
        )
        factor_set: set[str] = set(factors_tuple)

        occurrences = occurrence_counter.get(factors_tuple, 0)
        max_overlap = (
            compute_max_overlap(factor_set, distinct_priors)
            if factor_set
            else 0
        )
        label = compute_relationship_label(
            occurrences, factor_set, distinct_priors,
        )

        bucket = _position_bucket(call.get("position"))
        pool.append({
            "position": call.get("position"),
            "theme": call.get("theme"),
            "hypothesis_hash": call.get("hypothesis_hash"),
            "lifecycle_state": call.get("lifecycle_state"),
            "factors_used": list(call.get("factors_used") or []),
            "factor_set_prior_occurrences": occurrences,
            "max_overlap_with_priors": max_overlap,
            "d7a_b_relationship_label": label,
            "position_bucket": bucket,
        })

        # Update priors with THIS candidate for subsequent iterations.
        occurrence_counter[factors_tuple] = occurrences + 1
        if factor_set and factors_tuple not in seen_factor_sets:
            seen_factor_sets.add(factors_tuple)
            distinct_priors.append(factor_set)

    return {
        "pool": pool,
        "rejection_breakdown": breakdown,
        "pool_size_total": total,
        "pool_size_passing": len(pool),
    }


def _count_labels(pool: list[dict]) -> dict[str, int]:
    return {
        AGREEMENT_LABEL: sum(
            1 for c in pool if c["d7a_b_relationship_label"] == AGREEMENT_LABEL
        ),
        DIVERGENCE_LABEL: sum(
            1 for c in pool if c["d7a_b_relationship_label"] == DIVERGENCE_LABEL
        ),
        NEUTRAL_LABEL: sum(
            1 for c in pool if c["d7a_b_relationship_label"] == NEUTRAL_LABEL
        ),
    }


def _rank_agreement_key(c: dict, selected: list[dict]) -> tuple:
    """Local rank key for the agreement slot.

    Preferences, in order:
        1. candidate whose theme helps satisfy >=3-theme requirement
        2. candidate whose bucket helps fill missing early/mid/late coverage
        3. lower n_factors distance from 4 (prefer 4, then 3/5)
        4. lower position
    """
    themes_covered = {s["theme"] for s in selected}
    buckets_covered = {s["position_bucket"] for s in selected}
    missing_buckets = set(BUCKET_NAMES) - buckets_covered
    need_theme_diversity = len(themes_covered) < 3
    p1 = 0 if (need_theme_diversity and c["theme"] not in themes_covered) else 1
    p2 = 0 if c["position_bucket"] in missing_buckets else 1
    p3 = abs(len(c["factors_used"]) - 4)
    p4 = c["position"]
    return (p1, p2, p3, p4)


def _rank_divergence_key(c: dict, agreement: dict) -> tuple:
    """Local rank key for the divergence slot given an agreement pick.

    Preferences, in order:
        1. different theme from the selected agreement candidate
        2. lower max_overlap_with_priors
        3. candidate whose bucket fills missing coverage
        4. lower n_factors distance from 4
        5. lower position
    """
    buckets_covered = {agreement["position_bucket"]}
    missing_buckets = set(BUCKET_NAMES) - buckets_covered
    p1 = 0 if c["theme"] != agreement["theme"] else 1
    p2 = c.get("max_overlap_with_priors", 0)
    p3 = 0 if c["position_bucket"] in missing_buckets else 1
    p4 = abs(len(c["factors_used"]) - 4)
    p5 = c["position"]
    return (p1, p2, p3, p4, p5)


def _fill_rest(
    pool: list[dict],
    selected: list[dict],
    *,
    n_target: int = 5,
) -> list[dict] | None:
    """Greedy deterministic fill for remaining slots.

    Returns the newly added candidates (excluding ``selected``) if filling
    succeeds AND hard constraints (>=3 themes, all 3 buckets covered,
    unique hashes) are satisfied. Returns ``None`` otherwise.

    Local rank preferences for each remaining slot, in order:
        1. fills a missing position bucket
        2. adds a new theme (only when total distinct themes < 3)
        3. lower position
    """
    added: list[dict] = []
    used_hashes: set[str] = {c["hypothesis_hash"] for c in selected}
    pool_sorted = sorted(
        pool, key=lambda c: (c["position"], c["hypothesis_hash"]),
    )

    while len(selected) + len(added) < n_target:
        current = selected + added
        buckets_covered = {c["position_bucket"] for c in current}
        themes_covered = {c["theme"] for c in current}
        missing_buckets = set(BUCKET_NAMES) - buckets_covered
        need_theme_diversity = len(themes_covered) < 3

        remaining = [
            c for c in pool_sorted if c["hypothesis_hash"] not in used_hashes
        ]
        if not remaining:
            return None

        def rank_key(c: dict) -> tuple:
            p1 = 0 if c["position_bucket"] in missing_buckets else 1
            p2 = (
                0
                if (need_theme_diversity and c["theme"] not in themes_covered)
                else 1
            )
            return (p1, p2, c["position"])

        remaining.sort(key=rank_key)
        chosen = remaining[0]
        added.append(chosen)
        used_hashes.add(chosen["hypothesis_hash"])

    all_selected = selected + added
    buckets_covered = {c["position_bucket"] for c in all_selected}
    themes_covered = {c["theme"] for c in all_selected}
    if len(buckets_covered) < 3:
        return None
    if len(themes_covered) < 3:
        return None
    if len({c["hypothesis_hash"] for c in all_selected}) != len(all_selected):
        return None
    return added


def _try_agreement_divergence_tier(
    pool: list[dict],
    *,
    different_themes_required: bool,
    tier: int,
) -> tuple[list[dict], list[dict]] | None:
    """Try Tier 0 (different themes) or Tier 1 (same theme allowed)."""
    agreement_pool = [
        c for c in pool if c["d7a_b_relationship_label"] == AGREEMENT_LABEL
    ]
    divergence_pool = [
        c for c in pool if c["d7a_b_relationship_label"] == DIVERGENCE_LABEL
    ]
    if not agreement_pool or not divergence_pool:
        return None

    ranked_agreement = sorted(
        agreement_pool, key=lambda c: _rank_agreement_key(c, []),
    )

    for a in ranked_agreement:
        div_candidates = [
            c for c in divergence_pool
            if c["hypothesis_hash"] != a["hypothesis_hash"]
        ]
        if different_themes_required:
            div_candidates = [
                c for c in div_candidates if c["theme"] != a["theme"]
            ]
        if not div_candidates:
            continue

        ranked_divergence = sorted(
            div_candidates, key=lambda c: _rank_divergence_key(c, a),
        )

        for d in ranked_divergence:
            filled = _fill_rest(pool, [a, d])
            if filled is None:
                continue
            warnings: list[dict] = []
            if tier == 1:
                label_counts = _count_labels(pool)
                warnings.append({
                    "tier": 1,
                    "constraint_relaxed": (
                        "divergence_pair_different_themes_preference"
                    ),
                    "reason": (
                        "no eligible theme pair in the candidate pool "
                        "contains both an agreement-expected and "
                        "divergence-expected candidate"
                    ),
                    "pool_size_searched": len(pool),
                    "pool_breakdown_by_label": label_counts,
                    "rejection_breakdown": {},
                })
            return [a, d] + filled, warnings

    return None


def _try_tier2(pool: list[dict]) -> tuple[list[dict], list[dict]] | None:
    """Tier 2: drop divergence coverage. Fill 5 under hard constraints."""
    filled = _fill_rest(pool, [])
    if filled is None:
        return None
    label_counts = _count_labels(pool)
    warnings = [{
        "tier": 2,
        "constraint_relaxed": "divergence_coverage",
        "reason": (
            "pool lacks either agreement-expected or divergence-expected "
            "candidates that fit within hard-constraint-satisfying selection"
        ),
        "pool_size_searched": len(pool),
        "pool_breakdown_by_label": label_counts,
        "hard_constraint_constrained": True,
        "rejection_breakdown": {},
    }]
    return filled, warnings


def _render_rationale(candidate: dict) -> str:
    """Mechanical template — never freeform text."""
    return (
        f"fills {candidate['position_bucket']} bucket; "
        f"adds theme {candidate['theme']}; "
        f"label={candidate['d7a_b_relationship_label']}"
    )


def select_stage2b(pool: list[dict]) -> dict:
    """Select 5 candidates under Stage 2b constraints.

    Returns a dict with:
        status: "ok" or "hard_fail"
        error: str (on hard_fail)
        candidates: list of 5 enriched candidates, sorted by position asc
                    and tagged with firing_order + selection_rationale
        tier: 0 | 1 | 2
        warnings: list of warning payloads
        bucket_counts: dict (on empty-bucket hard_fail only)
        theme_count: int (on few-themes hard_fail only)
    """
    if len(pool) < 5:
        return {
            "status": "hard_fail",
            "error": (
                f"only {len(pool)} candidates pass per-candidate criteria; "
                f"need >= 5"
            ),
            "pool_size_passing": len(pool),
        }

    buckets_present = {c["position_bucket"] for c in pool}
    bucket_counts = {
        name: sum(1 for c in pool if c["position_bucket"] == name)
        for name in BUCKET_NAMES
    }
    for name in BUCKET_NAMES:
        if name not in buckets_present:
            return {
                "status": "hard_fail",
                "error": (
                    f"position bucket {name} is empty; "
                    f"cannot satisfy hard constraint"
                ),
                "bucket_counts": bucket_counts,
            }

    themes_present = {c["theme"] for c in pool}
    if len(themes_present) < 3:
        return {
            "status": "hard_fail",
            "error": (
                f"only {len(themes_present)} distinct themes in pool; "
                f"cannot satisfy hard constraint of >= 3 themes"
            ),
            "theme_count": len(themes_present),
        }

    for tier in (0, 1, 2):
        if tier == 0:
            result = _try_agreement_divergence_tier(
                pool, different_themes_required=True, tier=0,
            )
        elif tier == 1:
            result = _try_agreement_divergence_tier(
                pool, different_themes_required=False, tier=1,
            )
        else:
            result = _try_tier2(pool)

        if result is None:
            continue

        candidates, warnings = result
        candidates = sorted(candidates, key=lambda c: c["position"])
        for idx, cand in enumerate(candidates, start=1):
            cand["firing_order"] = idx
            cand["selection_rationale"] = _render_rationale(cand)

        # Final validator: hard constraints must hold.
        if not _validate_hard_constraints(candidates):
            continue

        return {
            "status": "ok",
            "candidates": candidates,
            "tier": tier,
            "warnings": warnings,
        }

    return {
        "status": "hard_fail",
        "error": "hard constraints cannot be simultaneously satisfied",
    }


def _validate_hard_constraints(candidates: list[dict]) -> bool:
    if len(candidates) != 5:
        return False
    if len({c["hypothesis_hash"] for c in candidates}) != 5:
        return False
    if len({c["theme"] for c in candidates}) < 3:
        return False
    buckets = {c["position_bucket"] for c in candidates}
    if not set(BUCKET_NAMES).issubset(buckets):
        return False
    positions = [c["position"] for c in candidates]
    if positions != sorted(positions):
        return False
    return True


def _candidate_to_output(c: dict) -> dict:
    """Stable JSON ordering for a single candidate record."""
    return {
        "firing_order": c["firing_order"],
        "position": c["position"],
        "theme": c["theme"],
        "hypothesis_hash": c["hypothesis_hash"],
        "lifecycle_state": c["lifecycle_state"],
        "factors_used": list(c["factors_used"]),
        "factor_set_prior_occurrences": c["factor_set_prior_occurrences"],
        "max_overlap_with_priors": c["max_overlap_with_priors"],
        "d7a_b_relationship_label": c["d7a_b_relationship_label"],
        "position_bucket": c["position_bucket"],
        "selection_rationale": c["selection_rationale"],
    }


def build_stage2b_output(
    batch_uuid: str,
    selection_result: dict,
    eligible: dict,
    *,
    timestamp_utc: str | None = None,
) -> dict:
    """Assemble the Stage 2b output JSON (in-memory, not yet written)."""
    if timestamp_utc is None:
        timestamp_utc = datetime.datetime.now(
            datetime.timezone.utc
        ).strftime("%Y-%m-%dT%H:%M:%SZ")

    return {
        "stage_label": STAGE2B_STAGE_LABEL,
        "record_version": STAGE2B_RECORD_VERSION,
        "batch_uuid": batch_uuid,
        "selection_timestamp_utc": timestamp_utc,
        "selection_tier": selection_result["tier"],
        "selection_warnings": list(selection_result["warnings"]),
        "pool_size_total": eligible["pool_size_total"],
        "pool_size_passing_per_candidate_criteria": eligible["pool_size_passing"],
        "rejection_breakdown": dict(eligible["rejection_breakdown"]),
        "candidates": [
            _candidate_to_output(c) for c in selection_result["candidates"]
        ],
    }


def run_stage2b(
    batch_uuid: str,
    *,
    artifacts_root: Path,
    summary_name: str,
    output_path: Path,
) -> int:
    """Execute the full N=5 Stage 2b selection pipeline.

    Returns a Unix-style exit code (0 success, 1 any failure).
    """
    batch_dir = artifacts_root / f"batch_{batch_uuid}"
    summary_path = batch_dir / summary_name

    if not summary_path.exists():
        print(
            f"[select] summary not found: {summary_path}\n"
            f"[select] batch {batch_uuid} may not exist in {artifacts_root}/",
            file=sys.stderr,
        )
        return 1

    with summary_path.open(encoding="utf-8") as fh:
        summary = json.load(fh)

    eligible = build_eligible_pool(
        summary, batch_dir=batch_dir, batch_uuid=batch_uuid,
    )

    if len(eligible["pool"]) < 5:
        print(
            f"[select] ERROR: only {len(eligible['pool'])} candidates pass "
            f"per-candidate criteria; need >= 5.",
            file=sys.stderr,
        )
        print(
            f"[select] Breakdown: {eligible['rejection_breakdown']}",
            file=sys.stderr,
        )
        return 1

    result = select_stage2b(eligible["pool"])
    if result["status"] != "ok":
        err = result.get("error", "unknown hard fail")
        print(f"[select] ERROR: {err}.", file=sys.stderr)
        if "bucket_counts" in result:
            bc = result["bucket_counts"]
            print(
                f"[select] Pool counts: early={bc.get('early', 0)}, "
                f"mid={bc.get('mid', 0)}, late={bc.get('late', 0)}",
                file=sys.stderr,
            )
        return 1

    output = build_stage2b_output(batch_uuid, result, eligible)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(output, indent=2) + "\n", encoding="utf-8",
    )

    print(
        f"[select] wrote {output_path} "
        f"(tier={result['tier']}, n=5, "
        f"warnings={len(result['warnings'])})",
        file=sys.stderr,
    )
    return 0


# -----------------------------------------------------------------------
# Stage 2c — N=20 selection (two-phase slot-filling with agreement floor)
#
# The Stage 2c path reuses Stage 2b's pool-building machinery
# (``build_eligible_pool`` with ``STAGE2B_N_FACTORS_RANGE``) verbatim
# and layers a scaled constraint check plus a three-tier soft ladder on
# top. See the ``STAGE2C_*`` constants block above for the full rule
# list. The implementation below is intentionally kept separate from the
# Stage 2b ``_fill_rest`` / ``_try_*`` helpers: Stage 2c's agreement
# floor and scaled per-bucket minimum make its filler a different enough
# shape that co-mingling the two would obscure the cross-candidate
# invariants of each path.
# -----------------------------------------------------------------------

STAGE2C_DEFAULT_OUTPUT = Path("docs/d7_stage2c/replay_candidates.json")
STAGE2C_STAGE_LABEL = "d7_stage2c"
STAGE2C_RECORD_VERSION = "1.0"
STAGE2B_REFERENCE_DEFAULT = Path("docs/d7_stage2b/replay_candidates.json")


def _render_rationale_stage2c(
    candidate: dict, candidates_before: list[dict],
) -> str:
    """Context-aware rationale for a Stage 2c candidate.

    Uses ``adds theme`` on the first appearance of a theme in the
    firing-order-ordered candidate list, and ``retains theme`` on all
    subsequent appearances. The label clause is always the mechanical
    ``label=<agreement|divergence|neutral>_expected`` template.
    """
    themes_seen = {c["theme"] for c in candidates_before}
    if candidate["theme"] in themes_seen:
        theme_clause = f"retains theme {candidate['theme']}"
    else:
        theme_clause = f"adds theme {candidate['theme']}"
    return (
        f"fills {candidate['position_bucket']} bucket; "
        f"{theme_clause}; "
        f"label={candidate['d7a_b_relationship_label']}"
    )


def _fill_rest_stage2c(
    pool: list[dict],
    seed: list[dict],
    *,
    n_target: int = STAGE2C_N_CANDIDATES,
    bucket_min: int = STAGE2C_BUCKET_MIN,
    agreement_floor: int = STAGE2C_AGREEMENT_FLOOR,
) -> list[dict] | None:
    """Two-phase greedy fill for Stage 2c.

    Phase 1 enforces the agreement floor by force-picking
    ``agreement_expected`` candidates from the pool until the selection
    contains at least ``agreement_floor`` of them (or the pool runs
    out, in which case we return ``None``). Within Phase 1, bucket /
    theme coverage is still used as a tiebreak so the forced agreements
    help satisfy the other hard constraints.

    Phase 2 fills the remaining slots with bucket / theme priorities
    identical to Stage 2b's ``_fill_rest`` — ordered: fill
    under-populated buckets, then add missing themes, then lower
    position.

    Returns the newly added candidates (excluding ``seed``) if filling
    succeeds AND all hard constraints hold. Returns ``None`` otherwise.
    """
    added: list[dict] = []
    used_hashes: set[str] = {c["hypothesis_hash"] for c in seed}
    pool_sorted = sorted(
        pool, key=lambda c: (c["position"], c["hypothesis_hash"]),
    )

    def current() -> list[dict]:
        return seed + added

    def agreement_count() -> int:
        return sum(
            1 for c in current()
            if c["d7a_b_relationship_label"] == AGREEMENT_LABEL
        )

    def bucket_counts_now() -> dict[str, int]:
        sel = current()
        return {
            n: sum(1 for c in sel if c["position_bucket"] == n)
            for n in BUCKET_NAMES
        }

    # Phase 1 — force agreement floor
    while (
        agreement_count() < agreement_floor
        and len(current()) < n_target
    ):
        remaining_agreements = [
            c for c in pool_sorted
            if c["hypothesis_hash"] not in used_hashes
            and c["d7a_b_relationship_label"] == AGREEMENT_LABEL
        ]
        if not remaining_agreements:
            return None

        bc = bucket_counts_now()
        buckets_needing_fill = {
            n for n in BUCKET_NAMES if bc[n] < bucket_min
        }
        themes_covered = {c["theme"] for c in current()}
        need_theme_diversity = len(themes_covered) < STAGE2C_THEMES_MIN

        def rank_key_phase1(c: dict) -> tuple:
            p1 = 0 if c["position_bucket"] in buckets_needing_fill else 1
            p2 = (
                0
                if (need_theme_diversity and c["theme"] not in themes_covered)
                else 1
            )
            return (p1, p2, c["position"])

        remaining_agreements.sort(key=rank_key_phase1)
        chosen = remaining_agreements[0]
        added.append(chosen)
        used_hashes.add(chosen["hypothesis_hash"])

    # Phase 2 — bucket/theme-driven fill for remaining slots
    while len(current()) < n_target:
        bc = bucket_counts_now()
        buckets_needing_fill = {
            n for n in BUCKET_NAMES if bc[n] < bucket_min
        }
        themes_covered = {c["theme"] for c in current()}
        need_theme_diversity = len(themes_covered) < STAGE2C_THEMES_MIN

        remaining = [
            c for c in pool_sorted if c["hypothesis_hash"] not in used_hashes
        ]
        if not remaining:
            return None

        def rank_key_phase2(c: dict) -> tuple:
            p1 = 0 if c["position_bucket"] in buckets_needing_fill else 1
            p2 = (
                0
                if (need_theme_diversity and c["theme"] not in themes_covered)
                else 1
            )
            return (p1, p2, c["position"])

        remaining.sort(key=rank_key_phase2)
        chosen = remaining[0]
        added.append(chosen)
        used_hashes.add(chosen["hypothesis_hash"])

    # Post-fill hard-constraint validation
    all_sel = seed + added
    if len({c["hypothesis_hash"] for c in all_sel}) != len(all_sel):
        return None
    final_bc = {
        n: sum(1 for c in all_sel if c["position_bucket"] == n)
        for n in BUCKET_NAMES
    }
    if any(final_bc[n] < bucket_min for n in BUCKET_NAMES):
        return None
    if len({c["theme"] for c in all_sel}) < STAGE2C_THEMES_MIN:
        return None
    final_agree = sum(
        1 for c in all_sel
        if c["d7a_b_relationship_label"] == AGREEMENT_LABEL
    )
    if final_agree < agreement_floor:
        return None
    return added


def _try_tier0_stage2c(
    pool: list[dict],
) -> tuple[list[dict], list[dict]] | None:
    """Tier 0: >= 2 cross-theme divergence candidates in the selection."""
    divergences = [
        c for c in pool if c["d7a_b_relationship_label"] == DIVERGENCE_LABEL
    ]
    if len(divergences) < STAGE2C_TIER_0_DIVERGENCE_MIN:
        return None

    # Rank divergences by low overlap-with-priors (strongest divergence
    # signal first), then lower position as deterministic tiebreak.
    ranked = sorted(
        divergences,
        key=lambda c: (c["max_overlap_with_priors"], c["position"]),
    )

    for i, d1 in enumerate(ranked):
        for d2 in ranked[i + 1:]:
            if d1["theme"] == d2["theme"]:
                continue
            filled = _fill_rest_stage2c(pool, [d1, d2])
            if filled is None:
                continue
            return [d1, d2] + filled, []
    return None


def _try_tier1_stage2c(
    pool: list[dict],
) -> tuple[list[dict], list[dict]] | None:
    """Tier 1: single-divergence OR same-theme-divergences seed.

    Tries the stronger sub-case (two same-theme divergences) first,
    falling back to a single divergence if that sub-case is infeasible.
    Attaches a Tier-1 warning payload in either sub-case.
    """
    divergences = [
        c for c in pool if c["d7a_b_relationship_label"] == DIVERGENCE_LABEL
    ]
    if not divergences:
        return None

    ranked = sorted(
        divergences,
        key=lambda c: (c["max_overlap_with_priors"], c["position"]),
    )

    warning = {
        "tier": 1,
        "constraint_relaxed": "cross_theme_divergence_coverage",
        "reason": (
            "fewer than 2 cross-theme divergence-expected candidates "
            "fit within bucket / theme / agreement-floor-satisfying "
            "selection"
        ),
        "pool_size_searched": len(pool),
        "pool_breakdown_by_label": _count_labels(pool),
        "rejection_breakdown": {},
    }

    # Sub-case A: two same-theme divergences
    for i, d1 in enumerate(ranked):
        for d2 in ranked[i + 1:]:
            if d1["theme"] != d2["theme"]:
                continue
            filled = _fill_rest_stage2c(pool, [d1, d2])
            if filled is None:
                continue
            return [d1, d2] + filled, [dict(warning)]

    # Sub-case B: single divergence
    for d in ranked:
        filled = _fill_rest_stage2c(pool, [d])
        if filled is None:
            continue
        return [d] + filled, [dict(warning)]

    return None


def _try_tier2_stage2c(
    pool: list[dict],
) -> tuple[list[dict], list[dict]] | None:
    """Tier 2: drop divergence coverage. Agreement floor still enforced."""
    filled = _fill_rest_stage2c(pool, [])
    if filled is None:
        return None
    warnings = [{
        "tier": 2,
        "constraint_relaxed": "divergence_coverage",
        "reason": (
            "no divergence-expected seed feasible under bucket / theme / "
            "agreement-floor constraints"
        ),
        "pool_size_searched": len(pool),
        "pool_breakdown_by_label": _count_labels(pool),
        "hard_constraint_constrained": True,
        "rejection_breakdown": {},
    }]
    return filled, warnings


def _validate_hard_constraints_stage2c(candidates: list[dict]) -> bool:
    if len(candidates) != STAGE2C_N_CANDIDATES:
        return False
    if len({c["hypothesis_hash"] for c in candidates}) != STAGE2C_N_CANDIDATES:
        return False
    if len({c["theme"] for c in candidates}) < STAGE2C_THEMES_MIN:
        return False
    bucket_counts = {
        n: sum(1 for c in candidates if c["position_bucket"] == n)
        for n in BUCKET_NAMES
    }
    if any(bucket_counts[n] < STAGE2C_BUCKET_MIN for n in BUCKET_NAMES):
        return False
    agree = sum(
        1 for c in candidates
        if c["d7a_b_relationship_label"] == AGREEMENT_LABEL
    )
    if agree < STAGE2C_AGREEMENT_FLOOR:
        return False
    positions = [c["position"] for c in candidates]
    if positions != sorted(positions):
        return False
    return True


def select_stage2c(pool: list[dict]) -> dict:
    """Select 20 candidates under Stage 2c constraints.

    Returns a dict with:
        status: "ok" or "hard_fail"
        error: str (on hard_fail)
        candidates: list of 20 candidates, sorted by position asc and
                    tagged with firing_order + selection_rationale
        tier: 0 | 1 | 2
        warnings: list of warning payloads
        bucket_counts: dict (on empty-bucket hard_fail only)
        theme_count: int (on few-themes hard_fail only)
        agreement_count: int (on agreement-floor hard_fail only)
    """
    if len(pool) < STAGE2C_N_CANDIDATES:
        return {
            "status": "hard_fail",
            "error": (
                f"only {len(pool)} candidates pass per-candidate criteria; "
                f"need >= {STAGE2C_N_CANDIDATES}"
            ),
            "pool_size_passing": len(pool),
        }

    bucket_counts = {
        n: sum(1 for c in pool if c["position_bucket"] == n)
        for n in BUCKET_NAMES
    }
    for name in BUCKET_NAMES:
        if bucket_counts[name] < STAGE2C_BUCKET_MIN:
            return {
                "status": "hard_fail",
                "error": (
                    f"position bucket {name} has only {bucket_counts[name]} "
                    f"candidates; need >= {STAGE2C_BUCKET_MIN}"
                ),
                "bucket_counts": bucket_counts,
            }

    themes_present = {c["theme"] for c in pool}
    if len(themes_present) < STAGE2C_THEMES_MIN:
        return {
            "status": "hard_fail",
            "error": (
                f"only {len(themes_present)} distinct themes in pool; "
                f"cannot satisfy hard constraint of >= "
                f"{STAGE2C_THEMES_MIN} themes"
            ),
            "theme_count": len(themes_present),
        }

    agreement_pool_count = sum(
        1 for c in pool
        if c["d7a_b_relationship_label"] == AGREEMENT_LABEL
    )
    if agreement_pool_count < STAGE2C_AGREEMENT_FLOOR:
        return {
            "status": "hard_fail",
            "error": (
                f"only {agreement_pool_count} agreement_expected candidates "
                f"in pool; need >= {STAGE2C_AGREEMENT_FLOOR} (HARD)"
            ),
            "agreement_count": agreement_pool_count,
        }

    for tier in (0, 1, 2):
        if tier == 0:
            result = _try_tier0_stage2c(pool)
        elif tier == 1:
            result = _try_tier1_stage2c(pool)
        else:
            result = _try_tier2_stage2c(pool)

        if result is None:
            continue

        candidates, warnings = result
        candidates = sorted(candidates, key=lambda c: c["position"])
        for idx, cand in enumerate(candidates, start=1):
            cand["firing_order"] = idx
            cand["selection_rationale"] = _render_rationale_stage2c(
                cand, candidates[: idx - 1],
            )

        if not _validate_hard_constraints_stage2c(candidates):
            continue

        return {
            "status": "ok",
            "candidates": candidates,
            "tier": tier,
            "warnings": warnings,
        }

    return {
        "status": "hard_fail",
        "error": (
            "hard constraints cannot be simultaneously satisfied at any tier"
        ),
    }


def _compute_stage2b_overlap(
    stage2c_candidates: list[dict],
    stage2b_reference_path: Path,
) -> tuple[int, list[int]]:
    """Compute overlap against the signed-off Stage 2b candidate file.

    Overlap is defined as candidates whose ``hypothesis_hash`` appears in
    both the Stage 2b reference file and the Stage 2c selection. Returns
    ``(overlap_count, sorted_overlap_positions)``. When the reference
    file is missing or unreadable, returns ``(0, [])`` without raising —
    Stage 2c is a pure research diagnostic, not a hard dependency on
    Stage 2b's presence.
    """
    if not stage2b_reference_path.exists():
        return 0, []
    try:
        data = json.loads(
            stage2b_reference_path.read_text(encoding="utf-8"),
        )
    except (OSError, json.JSONDecodeError):
        return 0, []
    stage2b_hashes = {
        c.get("hypothesis_hash")
        for c in data.get("candidates", [])
        if c.get("hypothesis_hash")
    }
    overlap_positions = sorted(
        c["position"]
        for c in stage2c_candidates
        if c["hypothesis_hash"] in stage2b_hashes
    )
    return len(overlap_positions), overlap_positions


def _count_themes_in(candidates: list[dict]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for c in candidates:
        counts[c["theme"]] = counts.get(c["theme"], 0) + 1
    return counts


def _count_labels_in(candidates: list[dict]) -> dict[str, int]:
    return {
        AGREEMENT_LABEL: sum(
            1 for c in candidates
            if c["d7a_b_relationship_label"] == AGREEMENT_LABEL
        ),
        DIVERGENCE_LABEL: sum(
            1 for c in candidates
            if c["d7a_b_relationship_label"] == DIVERGENCE_LABEL
        ),
        NEUTRAL_LABEL: sum(
            1 for c in candidates
            if c["d7a_b_relationship_label"] == NEUTRAL_LABEL
        ),
    }


def build_stage2c_output(
    batch_uuid: str,
    selection_result: dict,
    eligible: dict,
    *,
    timestamp_utc: str | None = None,
    stage2b_overlap_count: int = 0,
    stage2b_overlap_positions: list[int] | None = None,
) -> dict:
    """Assemble the Stage 2c output JSON (in-memory, not yet written)."""
    if timestamp_utc is None:
        timestamp_utc = datetime.datetime.now(
            datetime.timezone.utc
        ).strftime("%Y-%m-%dT%H:%M:%SZ")
    if stage2b_overlap_positions is None:
        stage2b_overlap_positions = []

    candidates = selection_result["candidates"]
    theme_counts = _count_themes_in(candidates)
    label_counts = _count_labels_in(candidates)

    return {
        "stage_label": STAGE2C_STAGE_LABEL,
        "record_version": STAGE2C_RECORD_VERSION,
        "batch_uuid": batch_uuid,
        "selection_timestamp_utc": timestamp_utc,
        "selection_tier": selection_result["tier"],
        "selection_warnings": list(selection_result["warnings"]),
        "pool_size_total": eligible["pool_size_total"],
        "pool_size_passing_per_candidate_criteria": eligible[
            "pool_size_passing"
        ],
        "rejection_breakdown": dict(eligible["rejection_breakdown"]),
        "stage2b_overlap_count": stage2b_overlap_count,
        "stage2b_overlap_positions": list(stage2b_overlap_positions),
        "theme_counts_in_selected": theme_counts,
        "label_counts_in_selected": label_counts,
        "candidates": [
            _candidate_to_output(c) for c in candidates
        ],
    }


def run_stage2c(
    batch_uuid: str,
    *,
    artifacts_root: Path,
    summary_name: str,
    output_path: Path,
    stage2b_reference_path: Path,
) -> int:
    """Execute the full N=20 Stage 2c selection pipeline.

    Returns a Unix-style exit code (0 success, 1 any failure).
    """
    batch_dir = artifacts_root / f"batch_{batch_uuid}"
    summary_path = batch_dir / summary_name

    if not summary_path.exists():
        print(
            f"[select] summary not found: {summary_path}\n"
            f"[select] batch {batch_uuid} may not exist in {artifacts_root}/",
            file=sys.stderr,
        )
        return 1

    with summary_path.open(encoding="utf-8") as fh:
        summary = json.load(fh)

    eligible = build_eligible_pool(
        summary, batch_dir=batch_dir, batch_uuid=batch_uuid,
    )

    result = select_stage2c(eligible["pool"])

    if result["status"] != "ok":
        err = result.get("error", "unknown hard fail")
        print(f"[select] ERROR: {err}.", file=sys.stderr)
        if "bucket_counts" in result:
            bc = result["bucket_counts"]
            print(
                f"[select] Pool counts: early={bc.get('early', 0)}, "
                f"mid={bc.get('mid', 0)}, late={bc.get('late', 0)}",
                file=sys.stderr,
            )
        if "pool_size_passing" in result:
            print(
                f"[select] Breakdown: {eligible['rejection_breakdown']}",
                file=sys.stderr,
            )
        return 1

    overlap_count, overlap_positions = _compute_stage2b_overlap(
        result["candidates"], stage2b_reference_path,
    )

    output = build_stage2c_output(
        batch_uuid, result, eligible,
        stage2b_overlap_count=overlap_count,
        stage2b_overlap_positions=overlap_positions,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(output, indent=2) + "\n", encoding="utf-8",
    )

    positions = [c["position"] for c in result["candidates"]]
    theme_counts = output["theme_counts_in_selected"]
    label_counts = output["label_counts_in_selected"]

    print(f"[select] wrote {output_path}")
    print(f"[select] positions: {positions}")
    print(f"[select] themes: {theme_counts}")
    print(f"[select] labels: {label_counts}")
    print(
        f"[select] stage2b overlap: {overlap_count} "
        f"positions={overlap_positions}"
    )

    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Select a D7 Stage 2a replay candidate from a Stage 2d batch.",
    )
    parser.add_argument(
        "batch_uuid",
        help="UUID of the signed-off Stage 2d batch",
    )
    parser.add_argument(
        "--artifacts-root",
        type=Path,
        default=Path("raw_payloads"),
        help="Root directory containing batch_<uuid>/ subdirs",
    )
    parser.add_argument(
        "--summary-name",
        default="stage2d_summary.json",
        help="Filename of the summary JSON within the batch dir",
    )
    parser.add_argument(
        "--n",
        type=int,
        default=1,
        choices=(1, 5, 20),
        help=(
            "Number of candidates to select. Must be 1, 5, or 20. "
            "Default: 1. N=5 triggers Stage 2b selection logic; "
            "N=20 triggers Stage 2c selection logic."
        ),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help=(
            "Override default output path (Stage 2b/2c only; ignored when "
            "--n=1). Defaults: docs/d7_stage2b/replay_candidates.json "
            "for --n=5; docs/d7_stage2c/replay_candidates.json for --n=20."
        ),
    )
    parser.add_argument(
        "--stage2b-reference",
        type=Path,
        default=None,
        help=(
            "Override Stage 2b reference path used by --n=20 to compute "
            "the stage2b_overlap_count / stage2b_overlap_positions "
            "fields. Default: docs/d7_stage2b/replay_candidates.json."
        ),
    )
    args = parser.parse_args()

    if args.n == 1:
        result = select_candidate(
            args.batch_uuid,
            artifacts_root=args.artifacts_root,
            summary_name=args.summary_name,
        )
        if result is None:
            sys.exit(1)

        print(json.dumps(result, indent=2))
        print(
            f"\n[select] recommended: position={result['position']}, "
            f"theme={result['theme']}, "
            f"n_factors={len(result.get('factors_used', []))}",
            file=sys.stderr,
        )
        return

    if args.n == 5:
        output_path = args.output or STAGE2B_DEFAULT_OUTPUT
        exit_code = run_stage2b(
            args.batch_uuid,
            artifacts_root=args.artifacts_root,
            summary_name=args.summary_name,
            output_path=output_path,
        )
        sys.exit(exit_code)

    # N == 20 — Stage 2c path.
    output_path = args.output or STAGE2C_DEFAULT_OUTPUT
    stage2b_ref = args.stage2b_reference or STAGE2B_REFERENCE_DEFAULT
    exit_code = run_stage2c(
        args.batch_uuid,
        artifacts_root=args.artifacts_root,
        summary_name=args.summary_name,
        output_path=output_path,
        stage2b_reference_path=stage2b_ref,
    )
    sys.exit(exit_code)


if __name__ == "__main__":
    main()

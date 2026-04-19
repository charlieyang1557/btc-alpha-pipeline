"""D7 Stage 2d — build replay candidates JSON (Task 2B).

Produces ``docs/d7_stage2d/replay_candidates.json`` — the fire-script-
consumed enumeration of all 200 D6 Stage 2d source positions in
firing-order ascending (firing_order == position for Stage 2d).

Inputs (read-only):
  * ``raw_payloads/batch_5cf76668-.../stage2d_summary.json``
  * ``docs/d7_stage2d/label_universe_analysis.json`` (committed Task 2A
    output; cross-referenced by SHA256)

Derivation:
  * Per-candidate metadata (theme, factor_set_size,
    factor_set_prior_occurrences, max_overlap_with_priors) comes from a
    Universe-B-style scan (ascending position, hypothesis_hash tiebreak)
    over the 199 pending_backtest calls, using the SAME primitives the
    Stage 2b/2c selector uses (``compute_max_overlap``,
    ``compute_relationship_label``). This matches Task 2A's Universe B
    derivation byte-for-byte.
  * Universe A labels come from the committed Task 2A
    ``universe_a.candidate_positions`` (29 positions); all other
    positions receive ``universe_a_label == null``.
  * Universe B labels come from the committed Task 2A
    ``universe_b.candidate_positions`` (199 positions); pos 116 gets
    ``universe_b_label == null``.
  * Position 116 is emitted with ``is_skipped_source=true`` and the
    full skip schema per scope lock Lock 1.5.

Deterministic: re-running produces byte-identical output (no timestamp
field).
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts.select_replay_candidate import (  # noqa: E402
    AGREEMENT_LABEL,
    DIVERGENCE_LABEL,
    NEUTRAL_LABEL,
    compute_relationship_label,
)
from agents.critic.d7a_feature_extraction import compute_max_overlap  # noqa: E402


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SOURCE_BATCH_UUID: str = "5cf76668-47d1-48d7-bd90-db06d31982ed"
SCOPE_LOCK_COMMIT: str = "4303d8de2882362ec55c8c581519331c5f6404c6"

BATCH_DIR: Path = _REPO_ROOT / "raw_payloads" / f"batch_{SOURCE_BATCH_UUID}"
BATCH_SUMMARY_PATH: Path = BATCH_DIR / "stage2d_summary.json"
LABEL_UNIVERSE_PATH: Path = (
    _REPO_ROOT / "docs" / "d7_stage2d" / "label_universe_analysis.json"
)
OUTPUT_PATH: Path = (
    _REPO_ROOT / "docs" / "d7_stage2d" / "replay_candidates.json"
)

EXPECTED_SOURCE_N: int = 200
EXPECTED_LIVE_D7B_CALL_N: int = 199
SKIPPED_POSITIONS: list[int] = [116]
POS_116_SKIP_REASON: str = (
    "source candidate is not pending_backtest and cannot be replayed by "
    "BatchContext reconstruction"
)

VALID_LABELS: frozenset[str] = frozenset(
    {AGREEMENT_LABEL, DIVERGENCE_LABEL, NEUTRAL_LABEL}
)


# ---------------------------------------------------------------------------
# I/O helpers
# ---------------------------------------------------------------------------


def sha256_of(path: Path) -> str:
    """Streaming SHA256 of a file."""
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


# ---------------------------------------------------------------------------
# Universe-B style scan (mirrors Task 2A derive_universe_b)
# ---------------------------------------------------------------------------


def scan_universe_b(summary: dict[str, Any]) -> dict[int, dict[str, Any]]:
    """Return ``{position -> metadata}`` for the 199 pending_backtest calls.

    Metadata includes: theme, factor_set_size,
    factor_set_prior_occurrences, max_overlap_with_priors,
    universe_b_label. This mirrors Task 2A's Universe B scan step-for-
    step so Universe B labels match by construction.
    """
    eligible_calls = [
        c for c in summary.get("calls", [])
        if c.get("lifecycle_state") == "pending_backtest"
    ]
    eligible_calls.sort(
        key=lambda c: (
            c.get("position", float("inf")),
            c.get("hypothesis_hash") or "",
        )
    )

    occurrence_counter: dict[tuple[str, ...], int] = {}
    seen_factor_sets: set[tuple[str, ...]] = set()
    distinct_priors: list[set[str]] = []

    per_position: dict[int, dict[str, Any]] = {}
    for call in eligible_calls:
        factors_used: list[str] = list(call.get("factors_used") or [])
        factors_tuple: tuple[str, ...] = tuple(sorted(factors_used))
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

        per_position[call["position"]] = {
            "theme": call.get("theme"),
            "factor_set_size": len(factors_used),
            "factor_set_prior_occurrences": occurrences,
            "max_overlap_with_priors": max_overlap,
            "universe_b_label": label,
        }

        occurrence_counter[factors_tuple] = occurrences + 1
        if factor_set and factors_tuple not in seen_factor_sets:
            seen_factor_sets.add(factors_tuple)
            distinct_priors.append(factor_set)

    return per_position


def universe_a_label_map(label_universe: dict[str, Any]) -> dict[int, str]:
    """Return ``{position -> universe_a_label}`` for the 29 UA positions."""
    mapping: dict[int, str] = {}
    buckets = label_universe["universe_a"]["candidate_positions"]
    for label, positions in buckets.items():
        for p in positions:
            mapping[p] = label
    return mapping


# ---------------------------------------------------------------------------
# Candidate construction
# ---------------------------------------------------------------------------


def build_candidate_entry(
    position: int,
    summary_call: dict[str, Any],
    ub_meta: dict[str, Any] | None,
    ua_label: str | None,
) -> dict[str, Any]:
    """Build one per-position entry."""
    if position == 116:
        return {
            "position": 116,
            "firing_order": 116,
            "is_skipped_source": True,
            "lifecycle_state": "rejected_complexity",
            "source_valid_status": "invalid_schema",
            "theme": None,
            "factor_set_size": None,
            "factor_set_prior_occurrences": None,
            "max_overlap_with_priors": None,
            "universe_a_label": None,
            "universe_b_label": None,
            "skip_reason": POS_116_SKIP_REASON,
        }

    assert ub_meta is not None, (
        f"universe-B metadata missing for position {position}"
    )
    return {
        "position": position,
        "firing_order": position,
        "is_skipped_source": False,
        "lifecycle_state": summary_call.get("lifecycle_state"),
        "theme": ub_meta["theme"],
        "factor_set_size": ub_meta["factor_set_size"],
        "factor_set_prior_occurrences": ub_meta["factor_set_prior_occurrences"],
        "max_overlap_with_priors": ub_meta["max_overlap_with_priors"],
        "universe_a_label": ua_label,
        "universe_b_label": ub_meta["universe_b_label"],
    }


# ---------------------------------------------------------------------------
# Invariants B1-B16
# ---------------------------------------------------------------------------


def run_invariants(
    result: dict[str, Any],
    label_universe: dict[str, Any],
    label_universe_sha256_actual: str,
) -> None:
    """Assert all 16 scope-lock invariants. Raises AssertionError on failure."""
    candidates: list[dict[str, Any]] = result["candidates"]

    # B1
    assert len(candidates) == 200, (
        f"B1: candidates count {len(candidates)} != 200"
    )
    # B2
    positions = [c["position"] for c in candidates]
    assert positions == list(range(1, 201)), (
        "B2: positions not strictly 1..200 ascending"
    )
    # B3
    firing_orders = [c["firing_order"] for c in candidates]
    assert firing_orders == list(range(1, 201)), (
        "B3: firing_orders not strictly 1..200 ascending"
    )
    # B4
    skipped = [c for c in candidates if c["is_skipped_source"]]
    assert len(skipped) == 1, (
        f"B4: expected exactly 1 skipped-source entry, got {len(skipped)}"
    )
    # B5
    assert skipped[0]["position"] == 116, (
        f"B5: skipped-source position is {skipped[0]['position']}, expected 116"
    )
    # B6
    non_skipped = [c for c in candidates if not c["is_skipped_source"]]
    assert len(non_skipped) == 199, (
        f"B6: expected 199 non-skipped entries, got {len(non_skipped)}"
    )
    # B7
    for c in non_skipped:
        assert c["lifecycle_state"] == "pending_backtest", (
            f"B7: position {c['position']} lifecycle_state="
            f"{c['lifecycle_state']!r}, expected pending_backtest"
        )
    # B8
    p116 = skipped[0]
    assert p116["lifecycle_state"] == "rejected_complexity", (
        f"B8: pos 116 lifecycle_state={p116['lifecycle_state']!r}, "
        "expected rejected_complexity"
    )
    assert p116["source_valid_status"] == "invalid_schema", (
        f"B8: pos 116 source_valid_status={p116['source_valid_status']!r}, "
        "expected invalid_schema"
    )
    # B9
    ub_counts = {AGREEMENT_LABEL: 0, DIVERGENCE_LABEL: 0, NEUTRAL_LABEL: 0}
    for c in non_skipped:
        lbl = c["universe_b_label"]
        assert lbl in VALID_LABELS, (
            f"B9: pos {c['position']} universe_b_label={lbl!r} invalid"
        )
        ub_counts[lbl] += 1
    expected_ub = label_universe["universe_b"]["counts"]
    assert ub_counts == expected_ub, (
        f"B9: universe_b distribution {ub_counts} != expected {expected_ub}"
    )
    # B10
    ua_non_null = [c for c in candidates if c["universe_a_label"] is not None]
    assert len(ua_non_null) == 29, (
        f"B10: non-null universe_a_label count {len(ua_non_null)} != 29"
    )
    expected_ua_positions: set[int] = set()
    for positions_list in label_universe["universe_a"][
        "candidate_positions"
    ].values():
        expected_ua_positions.update(positions_list)
    actual_ua_positions = {c["position"] for c in ua_non_null}
    assert actual_ua_positions == expected_ua_positions, (
        f"B10: UA positions mismatch — "
        f"missing={sorted(expected_ua_positions - actual_ua_positions)}, "
        f"extra={sorted(actual_ua_positions - expected_ua_positions)}"
    )
    # B11
    ua_counts = {AGREEMENT_LABEL: 0, DIVERGENCE_LABEL: 0, NEUTRAL_LABEL: 0}
    for c in ua_non_null:
        ua_counts[c["universe_a_label"]] += 1
    expected_ua = label_universe["universe_a"]["counts"]
    assert ua_counts == expected_ua, (
        f"B11: universe_a distribution {ua_counts} != expected {expected_ua}"
    )
    # B12
    assert result["scope_lock_commit"] == SCOPE_LOCK_COMMIT, (
        f"B12: scope_lock_commit={result['scope_lock_commit']!r}, expected "
        f"{SCOPE_LOCK_COMMIT!r}"
    )
    # B13
    assert result["label_universe_analysis_sha256"] == label_universe_sha256_actual, (
        f"B13: label_universe_analysis_sha256="
        f"{result['label_universe_analysis_sha256']!r} != actual "
        f"{label_universe_sha256_actual!r}"
    )
    # B14
    assert result["source_batch_uuid"] == SOURCE_BATCH_UUID, (
        f"B14: source_batch_uuid={result['source_batch_uuid']!r} != "
        f"{SOURCE_BATCH_UUID!r}"
    )
    assert BATCH_DIR.name == f"batch_{SOURCE_BATCH_UUID}", (
        f"B14: BATCH_DIR name {BATCH_DIR.name!r} does not match uuid"
    )
    # B15
    assert result["source_n"] == 200, f"B15: source_n={result['source_n']}"
    assert result["live_d7b_call_n"] == 199, (
        f"B15: live_d7b_call_n={result['live_d7b_call_n']}"
    )
    assert result["skipped_source_positions"] == [116], (
        f"B15: skipped_source_positions={result['skipped_source_positions']}"
    )
    # B16 is enforced at write time (sort_keys=True, indent=2).


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    if not LABEL_UNIVERSE_PATH.exists():
        raise SystemExit(
            "label_universe_analysis.json not found — Task 2A must be "
            "committed before Task 2B"
        )
    label_universe_sha = sha256_of(LABEL_UNIVERSE_PATH)
    label_universe = load_json(LABEL_UNIVERSE_PATH)
    summary = load_json(BATCH_SUMMARY_PATH)

    ub_scan = scan_universe_b(summary)
    ua_labels = universe_a_label_map(label_universe)

    call_by_position: dict[int, dict[str, Any]] = {
        c["position"]: c for c in summary.get("calls", [])
    }

    candidates: list[dict[str, Any]] = []
    for position in range(1, 201):
        call = call_by_position.get(position, {})
        ub_meta = ub_scan.get(position)
        ua_label = ua_labels.get(position)
        candidates.append(
            build_candidate_entry(position, call, ub_meta, ua_label)
        )

    result: dict[str, Any] = {
        "source_batch_uuid": SOURCE_BATCH_UUID,
        "stage": "d7_stage2d",
        "scope_lock_commit": SCOPE_LOCK_COMMIT,
        "label_universe_analysis_sha256": label_universe_sha,
        "source_n": EXPECTED_SOURCE_N,
        "live_d7b_call_n": EXPECTED_LIVE_D7B_CALL_N,
        "skipped_source_positions": list(SKIPPED_POSITIONS),
        "candidates": candidates,
    }

    run_invariants(result, label_universe, label_universe_sha)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8") as fh:
        json.dump(result, fh, sort_keys=True, indent=2)
        fh.write("\n")

    ua_counts = {AGREEMENT_LABEL: 0, DIVERGENCE_LABEL: 0, NEUTRAL_LABEL: 0}
    ub_counts = {AGREEMENT_LABEL: 0, DIVERGENCE_LABEL: 0, NEUTRAL_LABEL: 0}
    for c in candidates:
        if c["universe_a_label"] is not None:
            ua_counts[c["universe_a_label"]] += 1
        if c["universe_b_label"] is not None:
            ub_counts[c["universe_b_label"]] += 1

    print(f"source_batch_uuid               = {SOURCE_BATCH_UUID}")
    print(f"scope_lock_commit               = {SCOPE_LOCK_COMMIT}")
    print(f"label_universe_analysis_sha256  = {label_universe_sha}")
    print(f"source_n                        = {result['source_n']}")
    print(f"live_d7b_call_n                 = {result['live_d7b_call_n']}")
    print(f"skipped_source_positions        = {result['skipped_source_positions']}")
    print(f"universe_a label counts         = {ua_counts}")
    print(f"universe_b label counts         = {ub_counts}")
    print(f"universe_a_label == null count  = "
          f"{sum(1 for c in candidates if c['universe_a_label'] is None)}")
    print(f"output                          = "
          f"{OUTPUT_PATH.relative_to(_REPO_ROOT)}")
    print("all 16 invariants (B1-B16) PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())

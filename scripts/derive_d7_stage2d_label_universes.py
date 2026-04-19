"""D7 Stage 2d — derive Universe A / Universe B label universes.

Implements Lock 11.2 of ``docs/d7_stage2d/D7_STAGE2D_SCOPE_LOCK_v2.md``.
Reads the signed-off D6 Stage 2d batch summary
(``raw_payloads/batch_5cf76668-.../stage2d_summary.json``) and produces
``docs/d7_stage2d/label_universe_analysis.json`` — the pre-fire anchor
for Stage 2d's two label universes:

* **Universe A** — Stage 2b/2c eligibility pool (29 candidates).
  Labels derived using the Stage 2b/2c selector verbatim by importing
  ``build_eligible_pool`` from ``scripts/select_replay_candidate.py``.
  No reimplementation; no overload of the selector. The selector's
  output ``d7a_b_relationship_label`` is the Universe A label.

* **Universe B** — full replay-eligible pending-backtest population
  (199 positions; position 116 excluded). Labels are derived with the
  same ``compute_relationship_label`` primitive used by the selector,
  but against the unfiltered 199-position scan (ascending by position
  with ``hypothesis_hash`` tiebreak). Because the selector's
  eligibility filters are not applied, some Stage 2c overlap positions
  receive a different label here than under Universe A — by design
  (Lock 6.1). Specifically, positions 17, 73, 74 emerge as ``neutral``
  in Universe B while frozen as ``divergence_expected`` in Stage 2c.

Invariants (22 total, asserted before writing output):
  A1-A4  source/skipped counts
  A5-A9  Universe A size, counts, subset, pos-116 absence
  A10-A14 Universe B size, counts, set equivalence to {1..200}\\{116}
  A15-A18 Stage 2c overlap comparison shape and conflict semantics
  A19-A20 fresh eligible-pool composition
  A21-A22 Stage 2c subset of Universe A, sort discipline

The script is read-only, deterministic, and takes no arguments. Running
twice in succession produces byte-identical output except for
``derivation_timestamp_utc``.
"""

from __future__ import annotations

import datetime
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from agents.critic.d7a_feature_extraction import compute_max_overlap  # noqa: E402
from scripts.select_replay_candidate import (  # noqa: E402
    AGREEMENT_LABEL,
    DIVERGENCE_LABEL,
    NEUTRAL_LABEL,
    build_eligible_pool,
    compute_relationship_label,
)


# ---------------------------------------------------------------------------
# Constants — batch anchor and hardcoded expectations (per scope lock)
# ---------------------------------------------------------------------------

SOURCE_BATCH_UUID: str = "5cf76668-47d1-48d7-bd90-db06d31982ed"
BATCH_DIR: Path = _REPO_ROOT / "raw_payloads" / f"batch_{SOURCE_BATCH_UUID}"
BATCH_SUMMARY_PATH: Path = BATCH_DIR / "stage2d_summary.json"
OUTPUT_PATH: Path = _REPO_ROOT / "docs" / "d7_stage2d" / "label_universe_analysis.json"

EXPECTED_SOURCE_N: int = 200
EXPECTED_REPLAY_ELIGIBLE_N: int = 199
EXPECTED_NON_CALL_POSITIONS: list[int] = [116]

EXPECTED_UNIVERSE_A_SIZE: int = 29
EXPECTED_UNIVERSE_A_COUNTS: dict[str, int] = {
    AGREEMENT_LABEL: 11,
    DIVERGENCE_LABEL: 3,
    NEUTRAL_LABEL: 15,
}

EXPECTED_UNIVERSE_B_SIZE: int = 199
EXPECTED_UNIVERSE_B_COUNTS: dict[str, int] = {
    AGREEMENT_LABEL: 66,
    DIVERGENCE_LABEL: 5,
    NEUTRAL_LABEL: 128,
}

EXPECTED_FRESH_ELIGIBLE_POOL: list[int] = [
    122, 127, 128, 129, 132, 172, 178, 182, 187,
]

STAGE2C_POSITIONS: list[int] = [
    17, 22, 27, 32, 62, 72, 73, 74, 77, 83,
    97, 102, 107, 112, 117, 138, 143, 147, 152, 162,
]

# Frozen Stage 2c labels — copied verbatim from
# ``docs/d7_stage2c/replay_candidates.json`` at sign-off. These are the
# *authoritative* Stage 2c selector outputs for the 20 replay candidates.
STAGE2C_FROZEN_LABELS: dict[int, str] = {
    17: DIVERGENCE_LABEL,
    22: NEUTRAL_LABEL,
    27: AGREEMENT_LABEL,
    32: NEUTRAL_LABEL,
    62: NEUTRAL_LABEL,
    72: NEUTRAL_LABEL,
    73: DIVERGENCE_LABEL,
    74: DIVERGENCE_LABEL,
    77: NEUTRAL_LABEL,
    83: NEUTRAL_LABEL,
    97: AGREEMENT_LABEL,
    102: AGREEMENT_LABEL,
    107: AGREEMENT_LABEL,
    112: AGREEMENT_LABEL,
    117: NEUTRAL_LABEL,
    138: NEUTRAL_LABEL,
    143: NEUTRAL_LABEL,
    147: AGREEMENT_LABEL,
    152: AGREEMENT_LABEL,
    162: AGREEMENT_LABEL,
}

VALID_LABELS: frozenset[str] = frozenset(
    {AGREEMENT_LABEL, DIVERGENCE_LABEL, NEUTRAL_LABEL}
)


# ---------------------------------------------------------------------------
# Pure derivation functions
# ---------------------------------------------------------------------------


def load_batch_summary() -> dict[str, Any]:
    """Load the signed-off D6 Stage 2d batch summary (read-only)."""
    with BATCH_SUMMARY_PATH.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def derive_universe_a(summary: dict[str, Any]) -> dict[str, Any]:
    """Universe A — Stage 2b/2c eligibility pool.

    Reuses ``build_eligible_pool`` verbatim from
    ``scripts/select_replay_candidate.py``. The selector-returned
    ``d7a_b_relationship_label`` on each pool entry is the Universe A
    label; no reinterpretation.
    """
    pool_result = build_eligible_pool(
        summary, batch_dir=BATCH_DIR, batch_uuid=SOURCE_BATCH_UUID,
    )
    pool = pool_result["pool"]
    buckets: dict[str, list[int]] = {
        AGREEMENT_LABEL: [],
        DIVERGENCE_LABEL: [],
        NEUTRAL_LABEL: [],
    }
    for entry in pool:
        buckets[entry["d7a_b_relationship_label"]].append(entry["position"])
    for label in buckets:
        buckets[label] = sorted(buckets[label])
    return {
        "definition": (
            "Stage 2b/2c selector eligibility pool, following the exact "
            "filters implemented in scripts/select_replay_candidate.py."
        ),
        "size": len(pool),
        "counts": {label: len(buckets[label]) for label in buckets},
        "candidate_positions": buckets,
    }


def derive_universe_b(summary: dict[str, Any]) -> dict[str, Any]:
    """Universe B — full replay-eligible pending-backtest population.

    Scans the 199 positions with ``lifecycle_state == pending_backtest``
    in ascending position order (``hypothesis_hash`` tiebreak, mirroring
    the selector) and applies ``compute_relationship_label`` against
    the running distinct-prior factor-set history. Eligibility filters
    (theme, factor-count range, crosses operator, rsi-14 sole-factor,
    position bracket, thin-theme-momentum-bleed) are NOT applied.
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

    buckets: dict[str, list[int]] = {
        AGREEMENT_LABEL: [],
        DIVERGENCE_LABEL: [],
        NEUTRAL_LABEL: [],
    }
    position_to_label: dict[int, str] = {}

    for call in eligible_calls:
        factors_tuple: tuple[str, ...] = tuple(
            sorted(call.get("factors_used") or [])
        )
        factor_set: set[str] = set(factors_tuple)
        occurrences = occurrence_counter.get(factors_tuple, 0)
        label = compute_relationship_label(
            occurrences, factor_set, distinct_priors,
        )
        position = call["position"]
        position_to_label[position] = label
        buckets[label].append(position)

        occurrence_counter[factors_tuple] = occurrences + 1
        if factor_set and factors_tuple not in seen_factor_sets:
            seen_factor_sets.add(factors_tuple)
            distinct_priors.append(factor_set)

    for label in buckets:
        buckets[label] = sorted(buckets[label])

    universe_b = {
        "definition": (
            "Full replay-eligible pending-backtest population: all "
            "positions 1..200 with lifecycle_state == pending_backtest, "
            "equivalent to the set {1..200} minus {116}."
        ),
        "size": len(eligible_calls),
        "counts": {label: len(buckets[label]) for label in buckets},
        "candidate_positions": buckets,
    }
    # Attach the full position→label map for downstream comparison; not
    # emitted in the final JSON.
    universe_b["_position_to_label"] = position_to_label
    return universe_b


def build_stage2c_overlap_comparison(
    universe_b_position_to_label: dict[int, str],
) -> list[dict[str, Any]]:
    """One entry per Stage 2c overlap position, sorted by position asc."""
    comparison: list[dict[str, Any]] = []
    for position in sorted(STAGE2C_POSITIONS):
        frozen = STAGE2C_FROZEN_LABELS[position]
        universe_b = universe_b_position_to_label[position]
        comparison.append({
            "position": position,
            "stage2c_frozen_label": frozen,
            "universe_b_label": universe_b,
            "conflict": frozen != universe_b,
        })
    return comparison


def compute_fresh_eligible_pool(
    universe_a: dict[str, Any],
) -> list[int]:
    """Universe A positions minus the 20 Stage 2c positions, sorted asc."""
    universe_a_positions: set[int] = set()
    for positions in universe_a["candidate_positions"].values():
        universe_a_positions.update(positions)
    return sorted(universe_a_positions - set(STAGE2C_POSITIONS))


def non_call_position_details(summary: dict[str, Any]) -> list[dict[str, Any]]:
    """One entry per non-pending_backtest position (expected: pos 116)."""
    details: list[dict[str, Any]] = []
    for call in summary.get("calls", []):
        if call.get("lifecycle_state") == "pending_backtest":
            continue
        details.append({
            "position": call["position"],
            "lifecycle_state": call.get("lifecycle_state"),
            "valid_status": call.get("valid_status"),
        })
    details.sort(key=lambda d: d["position"])
    return details


def git_head_commit() -> str:
    """Return ``git rev-parse HEAD`` for the repo."""
    result = subprocess.run(
        ["git", "-C", str(_REPO_ROOT), "rev-parse", "HEAD"],
        capture_output=True, text=True, check=True,
    )
    return result.stdout.strip()


# ---------------------------------------------------------------------------
# Invariant checks
# ---------------------------------------------------------------------------


def run_invariants(result: dict[str, Any]) -> None:
    """Assert all 22 scope-lock invariants. Raises AssertionError on failure."""
    # A1
    assert result["source_n"] == EXPECTED_SOURCE_N, (
        f"A1: source_n expected {EXPECTED_SOURCE_N}, got {result['source_n']}"
    )
    # A2
    non_call = result["non_call_positions"]
    assert len(non_call) == 1 and non_call == EXPECTED_NON_CALL_POSITIONS, (
        f"A2: non_call_positions expected {EXPECTED_NON_CALL_POSITIONS}, "
        f"got {non_call}"
    )
    # A3
    assert result["replay_eligible_n"] == EXPECTED_REPLAY_ELIGIBLE_N, (
        f"A3: replay_eligible_n expected {EXPECTED_REPLAY_ELIGIBLE_N}, "
        f"got {result['replay_eligible_n']}"
    )
    # A4
    assert (
        result["replay_eligible_n"] + len(result["non_call_positions"])
        == result["source_n"]
    ), "A4: replay_eligible_n + non_call = source_n violated"

    ua = result["universe_a"]
    ub = result["universe_b"]
    # A5
    assert ua["size"] == EXPECTED_UNIVERSE_A_SIZE, (
        f"A5: universe_a.size expected {EXPECTED_UNIVERSE_A_SIZE}, "
        f"got {ua['size']}"
    )
    # A6
    assert sum(ua["counts"].values()) == ua["size"] == EXPECTED_UNIVERSE_A_SIZE, (
        f"A6: universe_a.counts sum={sum(ua['counts'].values())}, "
        f"size={ua['size']}, expected both == {EXPECTED_UNIVERSE_A_SIZE}"
    )
    assert ua["counts"] == EXPECTED_UNIVERSE_A_COUNTS, (
        f"A6b: universe_a.counts expected {EXPECTED_UNIVERSE_A_COUNTS}, "
        f"got {ua['counts']}"
    )
    # A7
    all_a: list[int] = []
    for positions in ua["candidate_positions"].values():
        all_a.extend(positions)
    assert len(set(all_a)) == len(all_a) == EXPECTED_UNIVERSE_A_SIZE, (
        f"A7: universe_a concatenated positions have duplicates or wrong count "
        f"(size={len(all_a)}, distinct={len(set(all_a))})"
    )
    # A8
    all_a_set = set(all_a)
    all_b_set: set[int] = set()
    for positions in ub["candidate_positions"].values():
        all_b_set.update(positions)
    assert all_a_set.issubset(all_b_set), (
        f"A8: universe_a positions not a subset of universe_b "
        f"(extras: {sorted(all_a_set - all_b_set)})"
    )
    # A9
    for positions in ua["candidate_positions"].values():
        assert 116 not in positions, (
            "A9: position 116 must not appear in universe_a.candidate_positions"
        )

    # A10
    assert ub["size"] == EXPECTED_UNIVERSE_B_SIZE, (
        f"A10: universe_b.size expected {EXPECTED_UNIVERSE_B_SIZE}, "
        f"got {ub['size']}"
    )
    # A11
    assert (
        sum(ub["counts"].values()) == ub["size"] == EXPECTED_UNIVERSE_B_SIZE
    ), (
        f"A11: universe_b.counts sum={sum(ub['counts'].values())}, "
        f"size={ub['size']}, expected both == {EXPECTED_UNIVERSE_B_SIZE}"
    )
    assert ub["counts"] == EXPECTED_UNIVERSE_B_COUNTS, (
        f"A11b: universe_b.counts expected {EXPECTED_UNIVERSE_B_COUNTS}, "
        f"got {ub['counts']} — material finding, HALT and flag to Charlie"
    )
    # A12
    all_b: list[int] = []
    for positions in ub["candidate_positions"].values():
        all_b.extend(positions)
    assert len(set(all_b)) == len(all_b) == EXPECTED_UNIVERSE_B_SIZE, (
        f"A12: universe_b concatenated positions have duplicates or wrong count "
        f"(size={len(all_b)}, distinct={len(set(all_b))})"
    )
    # A13
    expected_b = set(range(1, EXPECTED_SOURCE_N + 1)) - {116}
    assert set(all_b) == expected_b, (
        f"A13: universe_b set != {{1..200}} \\ {{116}} "
        f"(missing: {sorted(expected_b - set(all_b))}, "
        f"extra: {sorted(set(all_b) - expected_b)})"
    )
    # A14
    for positions in ub["candidate_positions"].values():
        assert 116 not in positions, (
            "A14: position 116 must not appear in universe_b.candidate_positions"
        )

    cmp_list = result["stage2c_overlap_label_comparison"]
    # A15
    assert len(cmp_list) == 20, (
        f"A15: stage2c_overlap_label_comparison expected 20 entries, "
        f"got {len(cmp_list)}"
    )
    # A16
    cmp_positions = {entry["position"] for entry in cmp_list}
    assert cmp_positions == set(STAGE2C_POSITIONS), (
        f"A16: stage2c_overlap positions {sorted(cmp_positions)} "
        f"!= Stage 2c 20 {STAGE2C_POSITIONS}"
    )
    # A17
    for entry in cmp_list:
        assert entry["stage2c_frozen_label"] in VALID_LABELS, (
            f"A17: invalid stage2c_frozen_label {entry['stage2c_frozen_label']!r} "
            f"at position {entry['position']}"
        )
        assert entry["universe_b_label"] in VALID_LABELS, (
            f"A17b: invalid universe_b_label {entry['universe_b_label']!r} "
            f"at position {entry['position']}"
        )
    # A18
    for entry in cmp_list:
        expected_conflict = (
            entry["stage2c_frozen_label"] != entry["universe_b_label"]
        )
        assert entry["conflict"] == expected_conflict, (
            f"A18: conflict flag mismatch at position {entry['position']} — "
            f"frozen={entry['stage2c_frozen_label']}, "
            f"ub={entry['universe_b_label']}, conflict={entry['conflict']}"
        )

    # A19
    fresh = result["fresh_eligible_pool_positions"]
    expected_fresh_computed = sorted(all_a_set - set(STAGE2C_POSITIONS))
    assert fresh == expected_fresh_computed, (
        f"A19: fresh_eligible_pool_positions {fresh} "
        f"!= universe_a \\ stage2c {expected_fresh_computed}"
    )
    # A20
    assert fresh == EXPECTED_FRESH_ELIGIBLE_POOL, (
        f"A20: fresh_eligible_pool_positions {fresh} "
        f"!= expected {EXPECTED_FRESH_ELIGIBLE_POOL} — "
        f"material finding, HALT and flag to Charlie"
    )
    # A21
    assert set(STAGE2C_POSITIONS).issubset(all_a_set), (
        f"A21: Stage 2c positions not fully in universe_a "
        f"(missing: {sorted(set(STAGE2C_POSITIONS) - all_a_set)})"
    )
    # A22
    for label, positions in ua["candidate_positions"].items():
        assert positions == sorted(positions), (
            f"A22: universe_a.{label} positions not sorted ascending"
        )
    for label, positions in ub["candidate_positions"].items():
        assert positions == sorted(positions), (
            f"A22: universe_b.{label} positions not sorted ascending"
        )
    cmp_pos_list = [entry["position"] for entry in cmp_list]
    assert cmp_pos_list == sorted(cmp_pos_list), (
        "A22: stage2c_overlap_label_comparison not sorted by position ascending"
    )
    assert fresh == sorted(fresh), "A22: fresh_eligible_pool_positions not sorted"
    assert result["non_call_positions"] == sorted(result["non_call_positions"]), (
        "A22: non_call_positions not sorted"
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    summary = load_batch_summary()

    universe_a = derive_universe_a(summary)
    universe_b_full = derive_universe_b(summary)
    universe_b_position_to_label: dict[int, str] = universe_b_full.pop(
        "_position_to_label"
    )
    universe_b = universe_b_full

    overlap_comparison = build_stage2c_overlap_comparison(
        universe_b_position_to_label,
    )
    fresh_pool = compute_fresh_eligible_pool(universe_a)

    now_utc = datetime.datetime.now(datetime.timezone.utc)
    timestamp = now_utc.strftime("%Y-%m-%dT%H:%M:%S.") + f"{now_utc.microsecond:06d}Z"

    result: dict[str, Any] = {
        "source_batch_uuid": SOURCE_BATCH_UUID,
        "derivation_script_commit": git_head_commit(),
        "derivation_timestamp_utc": timestamp,
        "source_n": EXPECTED_SOURCE_N,
        "replay_eligible_n": sum(
            1 for c in summary.get("calls", [])
            if c.get("lifecycle_state") == "pending_backtest"
        ),
        "non_call_positions": sorted(
            c["position"] for c in summary.get("calls", [])
            if c.get("lifecycle_state") != "pending_backtest"
        ),
        "non_call_position_details": non_call_position_details(summary),
        "universe_a": universe_a,
        "universe_b": universe_b,
        "stage2c_overlap_label_comparison": overlap_comparison,
        "fresh_eligible_pool_positions": fresh_pool,
    }

    run_invariants(result)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8") as fh:
        json.dump(result, fh, sort_keys=True, indent=2)
        fh.write("\n")

    # ---- stdout summary ----
    conflicts = sum(1 for e in overlap_comparison if e["conflict"])
    print(f"source_n                        = {result['source_n']}")
    print(f"replay_eligible_n               = {result['replay_eligible_n']}")
    print(f"non_call_positions              = {result['non_call_positions']}")
    print(f"universe_a.counts               = {universe_a['counts']}")
    print(f"universe_b.counts               = {universe_b['counts']}")
    print(f"stage2c_overlap_conflict_count  = {conflicts} / 20")
    print(f"fresh_eligible_pool_positions   = {fresh_pool}")
    print(f"output                          = {OUTPUT_PATH.relative_to(_REPO_ROOT)}")
    print("all 22 invariants PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())

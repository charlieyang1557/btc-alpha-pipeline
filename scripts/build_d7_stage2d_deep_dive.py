"""D7 Stage 2d — build deep-dive candidates JSON (Task 2C).

Produces ``docs/d7_stage2d/deep_dive_candidates.json`` — the stratified
20-candidate deep-dive selection per scope lock Lock 4.

Inputs (read-only):
  * ``raw_payloads/batch_5cf76668-.../stage2d_summary.json``
  * ``docs/d7_stage2d/label_universe_analysis.json`` (committed Task 2A)
  * ``docs/d7_stage2d/replay_candidates.json``        (committed Task 2B)

Selection methodology
---------------------
Strata are processed sequentially in the canonical Lock 4.1 order
(S1, S2, S3, S4, S5, S6) with greedy mutual exclusion: each candidate
is assigned to exactly one PRIMARY stratum (the first eligible stratum
in canonical order that still has open slots). Strata each candidate
ALSO qualifies for are recorded in ``also_fits_strata``.

Per-stratum target counts and ranking rules (deterministic):

  S1 RSI-absent volatility_regime (target 5, max 5):
      Pool = {3, 43, 68, 128, 173, 188, 198}.
      Rank by (is_fresh9 desc, max_overlap_with_priors desc, position asc).
      Five maxes the central Stage 2c C16/C17 RSI-absent-low-SVR test
      leverage on fresh candidates.

  S2 RSI-present volatility_regime (target 2, min 2):
      Pool = vol_regime calls with RSI factor present, not in S2C, not
      already selected.
      Rank by position ascending. Two satisfies the control role.

  S3 MR high-recurrence / high-overlap (target 5, max 5):
      Pool = MR calls not in S2C, anchored on the only fresh
      exact-7-factor repeat (pos 197), then expanded with
      max_overlap_with_priors >= 5 candidates.
      Rank: pos 197 first (anchor), then by (is_fresh9 desc,
      max_overlap desc, occurrences desc, position asc).
      Five maxes the agreement-cluster pattern follow-through.

  S4 Early-position 1-50 fresh (target 2, min 2):
      Pool = positions 1..50 not in S2C, not already selected.
      Rank by position ascending. Two = the minimum.

  S5 Late-position 163-200 fresh (target 3):
      Pool = positions 163..200 not in S2C, not already selected.
      Rank by (is_fresh9 desc, position descending).
      Three picks up the three Stage 2c-fresh late-pool positions
      {172, 178, 187} naturally and stays comfortably within max 4.

  S6 Rare-families themes (target 3):
      Pool = themes in {momentum, volume_divergence, calendar_effect},
      not pos 74, not S2C, not already selected.
      Theme-balanced: one pick per rare-family theme, ranked within
      theme by (is_fresh9 desc, position ascending).

Total target = 5 + 2 + 5 + 2 + 3 + 3 = 20.

Fresh-9 inclusion
-----------------
The 9 fresh eligible-pool positions {122, 127, 128, 129, 132, 172, 178,
182, 187} are preferred via the ``is_fresh9 desc`` tiebreaker. Under
this rule 8-9 of them are selected naturally; the deliverable far
exceeds the Lock 4.3 minimum of 3/9.

Anti-hindsight (Lock 4.6)
-------------------------
Selection uses only D6_STAGE2D batch metadata (factor sets, themes,
overlap counts) and signed-off Task 2A/2B labels. No Stage 2d run
data, dry-run data, or pilot data is consulted.

Deterministic: re-running produces byte-identical output (excluding
the single ``selection_timestamp_utc`` field).
"""

from __future__ import annotations

import datetime as _dt
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
REPLAY_CANDIDATES_PATH: Path = (
    _REPO_ROOT / "docs" / "d7_stage2d" / "replay_candidates.json"
)
OUTPUT_PATH: Path = (
    _REPO_ROOT / "docs" / "d7_stage2d" / "deep_dive_candidates.json"
)

S2C_POSITIONS: frozenset[int] = frozenset({
    17, 22, 27, 32, 62, 72, 73, 74, 77, 83,
    97, 102, 107, 112, 117, 138, 143, 147, 152, 162,
})

FRESH_9: frozenset[int] = frozenset(
    {122, 127, 128, 129, 132, 172, 178, 182, 187}
)

S1_FRESH_POOL: frozenset[int] = frozenset({3, 43, 68, 128, 173, 188, 198})

EARLY_POS_RANGE: range = range(1, 51)
LATE_POS_RANGE: range = range(163, 201)
RARE_FAMILY_THEMES: frozenset[str] = frozenset(
    {"momentum", "volume_divergence", "calendar_effect"}
)

# Per-stratum constraints from Lock 4.1
STRATA_SPEC: list[dict[str, Any]] = [
    {
        "stratum_id": 1,
        "name": "RSI-absent volatility_regime",
        "min_count": 3,
        "max_count": 5,
        "target": 5,
        "fresh_pool_size": 7,
    },
    {
        "stratum_id": 2,
        "name": "RSI-present volatility_regime",
        "min_count": 2,
        "max_count": 4,
        "target": 2,
        "fresh_pool_size": 29,
    },
    {
        "stratum_id": 3,
        "name": "MR high-recurrence / high-overlap",
        "min_count": 3,
        "max_count": 5,
        "target": 5,
        "fresh_pool_size": None,  # broadened; not a fixed count
    },
    {
        "stratum_id": 4,
        "name": "Early-position 1-50 fresh",
        "min_count": 2,
        "max_count": 4,
        "target": 2,
        "fresh_pool_size": 46,
    },
    {
        "stratum_id": 5,
        "name": "Late-position 163-200 fresh",
        "min_count": 2,
        "max_count": 4,
        "target": 3,
        "fresh_pool_size": 38,
    },
    {
        "stratum_id": 6,
        "name": "Rare-families themes (momentum, volume_divergence, calendar_effect)",
        "min_count": 2,
        "max_count": 4,
        "target": 3,
        "fresh_pool_size": None,
    },
]

VALID_LABELS: frozenset[str] = frozenset(
    {AGREEMENT_LABEL, DIVERGENCE_LABEL, NEUTRAL_LABEL}
)

SELECTION_METHODOLOGY: str = (
    "Sequential greedy assignment in canonical Lock 4.1 stratum order "
    "(S1..S6). Each candidate gets exactly one primary stratum (the "
    "first eligible in order with an open slot); other qualifying "
    "strata are recorded in `also_fits_strata`. Per-stratum ranking: "
    "S1 by (is_fresh9 desc, max_overlap desc, pos asc); S2 by pos asc; "
    "S3 by pos-197 anchor first then (is_fresh9 desc, max_overlap desc, "
    "occurrences desc, pos asc); S4 by pos asc; S5 by (is_fresh9 desc, "
    "pos desc); S6 theme-balanced one pick per rare-family theme by "
    "(is_fresh9 desc, pos asc). Targets: 5/2/5/2/3/3 = 20. Anti-"
    "hindsight: only D6_STAGE2D metadata + signed-off Task 2A/2B "
    "labels are consulted; no Stage 2d run data."
)

# ---------------------------------------------------------------------------
# I/O helpers
# ---------------------------------------------------------------------------


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


# ---------------------------------------------------------------------------
# Universe-B style scan (mirrors Task 2A / 2B for metadata fidelity)
# ---------------------------------------------------------------------------


def scan_metadata(summary: dict[str, Any]) -> dict[int, dict[str, Any]]:
    """Per-position metadata for the 199 pending_backtest calls."""
    eligible = [
        c for c in summary.get("calls", [])
        if c.get("lifecycle_state") == "pending_backtest"
    ]
    eligible.sort(
        key=lambda c: (c.get("position", float("inf")),
                       c.get("hypothesis_hash") or "")
    )

    occurrence_counter: dict[tuple[str, ...], int] = {}
    seen_factor_sets: set[tuple[str, ...]] = set()
    distinct_priors: list[set[str]] = []

    out: dict[int, dict[str, Any]] = {}
    for call in eligible:
        factors_used: list[str] = list(call.get("factors_used") or [])
        factors_tuple: tuple[str, ...] = tuple(sorted(factors_used))
        factor_set: set[str] = set(factors_tuple)

        occ = occurrence_counter.get(factors_tuple, 0)
        max_overlap = (
            compute_max_overlap(factor_set, distinct_priors)
            if factor_set
            else 0
        )
        label = compute_relationship_label(occ, factor_set, distinct_priors)

        out[call["position"]] = {
            "theme": call.get("theme"),
            "factor_set_size": len(factors_used),
            "factor_set_prior_occurrences": occ,
            "max_overlap_with_priors": max_overlap,
            "universe_b_label": label,
            "rsi_present": any("rsi" in f.lower() for f in factors_used),
        }

        occurrence_counter[factors_tuple] = occ + 1
        if factor_set and factors_tuple not in seen_factor_sets:
            seen_factor_sets.add(factors_tuple)
            distinct_priors.append(factor_set)

    return out


# ---------------------------------------------------------------------------
# Stratum eligibility predicates
# ---------------------------------------------------------------------------


def in_s1(pos: int, m: dict[str, Any]) -> bool:
    return pos in S1_FRESH_POOL


def in_s2(pos: int, m: dict[str, Any]) -> bool:
    return (
        m["theme"] == "volatility_regime"
        and m["rsi_present"]
        and pos not in S2C_POSITIONS
    )


def in_s3(pos: int, m: dict[str, Any]) -> bool:
    if m["theme"] != "mean_reversion" or pos in S2C_POSITIONS:
        return False
    is_exact_7_repeat = (
        m["factor_set_size"] == 7 and m["factor_set_prior_occurrences"] >= 1
    )
    has_high_overlap = m["max_overlap_with_priors"] >= 5
    return is_exact_7_repeat or has_high_overlap


def in_s4(pos: int, m: dict[str, Any]) -> bool:
    return pos in EARLY_POS_RANGE and pos not in S2C_POSITIONS


def in_s5(pos: int, m: dict[str, Any]) -> bool:
    return pos in LATE_POS_RANGE and pos not in S2C_POSITIONS


def in_s6(pos: int, m: dict[str, Any]) -> bool:
    return (
        m["theme"] in RARE_FAMILY_THEMES
        and pos != 74
        and pos not in S2C_POSITIONS
    )


STRATUM_PREDICATES: dict[int, Any] = {
    1: in_s1, 2: in_s2, 3: in_s3, 4: in_s4, 5: in_s5, 6: in_s6,
}


# ---------------------------------------------------------------------------
# Per-stratum ranking + selection
# ---------------------------------------------------------------------------


def _is_fresh9(pos: int) -> int:
    return 0 if pos in FRESH_9 else 1  # 0 first under ascending sort


def _rank_s1(pos: int, m: dict[str, Any]) -> tuple:
    return (_is_fresh9(pos), -m["max_overlap_with_priors"], pos)


def _rank_s2(pos: int, m: dict[str, Any]) -> tuple:
    return (pos,)


def _rank_s3(pos: int, m: dict[str, Any]) -> tuple:
    is_exact_7 = (
        m["factor_set_size"] == 7
        and m["factor_set_prior_occurrences"] >= 1
    )
    return (
        0 if is_exact_7 else 1,
        _is_fresh9(pos),
        -m["max_overlap_with_priors"],
        -m["factor_set_prior_occurrences"],
        pos,
    )


def _rank_s4(pos: int, m: dict[str, Any]) -> tuple:
    return (pos,)


def _rank_s5(pos: int, m: dict[str, Any]) -> tuple:
    return (_is_fresh9(pos), -pos)


STRATUM_RANK_KEYS: dict[int, Any] = {
    1: _rank_s1, 2: _rank_s2, 3: _rank_s3, 4: _rank_s4, 5: _rank_s5,
}


def select_stratum_picks(
    stratum_id: int,
    target: int,
    pool: list[int],
    meta: dict[int, dict[str, Any]],
) -> list[int]:
    """Generic ranked-then-take-target selection."""
    rank_fn = STRATUM_RANK_KEYS[stratum_id]
    pool_sorted = sorted(pool, key=lambda p: rank_fn(p, meta[p]))
    return pool_sorted[:target]


def select_s6_theme_balanced(
    pool: list[int],
    meta: dict[int, dict[str, Any]],
) -> list[int]:
    """Theme-balanced selection: one per rare-family theme, ranked
    within theme by (is_fresh9 desc, position ascending). Themes are
    visited in a fixed alphabetical order so the result is fully
    deterministic and produces 3 picks (one per theme).
    """
    selected: list[int] = []
    for theme in sorted(RARE_FAMILY_THEMES):
        per_theme = [p for p in pool if meta[p]["theme"] == theme]
        per_theme.sort(key=lambda p: (_is_fresh9(p), p))
        if per_theme:
            selected.append(per_theme[0])
    return selected


# ---------------------------------------------------------------------------
# also_fits_strata
# ---------------------------------------------------------------------------


def compute_also_fits(
    pos: int,
    primary: int,
    meta: dict[int, dict[str, Any]],
) -> list[int]:
    m = meta[pos]
    fits: list[int] = []
    for sid in (1, 2, 3, 4, 5, 6):
        if sid == primary:
            continue
        if STRATUM_PREDICATES[sid](pos, m):
            fits.append(sid)
    return fits


# ---------------------------------------------------------------------------
# Invariants C1-C21
# ---------------------------------------------------------------------------


def run_invariants(
    result: dict[str, Any],
    meta: dict[int, dict[str, Any]],
    label_universe_sha: str,
    replay_candidates_sha: str,
    replay_eligible_positions: set[int],
) -> None:
    candidates: list[dict[str, Any]] = result["candidates"]
    strata: list[dict[str, Any]] = result["strata"]

    # C1
    assert result["total_deep_dive_count"] == 20, (
        f"C1: total_deep_dive_count={result['total_deep_dive_count']}"
    )
    # C2
    assert len(candidates) == 20, f"C2: len(candidates)={len(candidates)}"
    # C3
    positions = [c["position"] for c in candidates]
    assert len(set(positions)) == 20, (
        f"C3: duplicate positions in {positions}"
    )
    # C4
    overlap = set(positions) & S2C_POSITIONS
    assert not overlap, f"C4: positions overlap with Stage 2c set: {overlap}"
    # C5
    assert 116 not in positions, "C5: pos 116 must not be selected"
    # C6
    not_eligible = set(positions) - replay_eligible_positions
    assert not not_eligible, (
        f"C6: positions not in replay-eligible set: {not_eligible}"
    )
    # C7
    sum_selected = sum(s["selected_count"] for s in strata)
    assert sum_selected == 20, (
        f"C7: sum(stratum.selected_count)={sum_selected}, expected 20"
    )
    # C8
    for s in strata:
        sc = s["selected_count"]
        assert s["min_count"] <= sc <= s["max_count"], (
            f"C8: stratum {s['stratum_id']} selected_count={sc} not in "
            f"[{s['min_count']}, {s['max_count']}]"
        )
    # C9
    union_strata = set()
    for s in strata:
        union_strata.update(s["selected_positions"])
    assert union_strata == set(positions), (
        f"C9: stratum union != candidates set; "
        f"diff={union_strata.symmetric_difference(set(positions))}"
    )
    # C10
    valid_sids = {s["stratum_id"] for s in strata}
    for c in candidates:
        assert c["primary_stratum_id"] in valid_sids, (
            f"C10: pos {c['position']} primary_stratum_id="
            f"{c['primary_stratum_id']} not in {valid_sids}"
        )
    # C11
    fresh_count = result["fresh_eligible_pool_inclusion_count"]
    assert fresh_count >= 3, (
        f"C11: fresh_eligible_pool_inclusion_count={fresh_count} < 3"
    )
    # C12
    actual_fresh = sum(
        1 for c in candidates if c["is_in_fresh_eligible_pool"]
    )
    assert fresh_count == actual_fresh, (
        f"C12: fresh_eligible_pool_inclusion_count={fresh_count} != "
        f"actual {actual_fresh}"
    )
    # C13
    flagged_fresh = {
        c["position"] for c in candidates if c["is_in_fresh_eligible_pool"]
    }
    bad = flagged_fresh - FRESH_9
    assert not bad, f"C13: flagged-fresh positions not in FRESH_9: {bad}"
    # C14
    assert result["label_universe_analysis_sha256"] == label_universe_sha, (
        f"C14: label_universe_analysis_sha256 mismatch"
    )
    # C15
    assert result["replay_candidates_sha256"] == replay_candidates_sha, (
        f"C15: replay_candidates_sha256 mismatch"
    )
    # C16
    assert result["scope_lock_commit"] == SCOPE_LOCK_COMMIT, (
        f"C16: scope_lock_commit mismatch"
    )
    # C17 — sortedness checks
    for s in strata:
        sp = s["selected_positions"]
        assert sp == sorted(sp), (
            f"C17: stratum {s['stratum_id']} selected_positions not sorted"
        )
    assert positions == sorted(positions), (
        f"C17: candidates not sorted by position ascending"
    )
    # C18 — JSON sort_keys is enforced at write time
    # C19
    for c in candidates:
        expected_ub = meta[c["position"]]["universe_b_label"]
        assert c["universe_b_label"] == expected_ub, (
            f"C19: pos {c['position']} universe_b_label="
            f"{c['universe_b_label']!r}, expected {expected_ub!r}"
        )
    # C20
    s1 = next(s for s in strata if s["stratum_id"] == 1)
    s1_bad = set(s1["selected_positions"]) - S1_FRESH_POOL
    assert not s1_bad, (
        f"C20: S1 selected_positions not in fresh-RSI-absent-vol pool: "
        f"{s1_bad}"
    )
    # C21
    s6 = next(s for s in strata if s["stratum_id"] == 6)
    for p in s6["selected_positions"]:
        assert meta[p]["theme"] in RARE_FAMILY_THEMES, (
            f"C21: S6 pos {p} theme={meta[p]['theme']!r} not rare-family"
        )
        assert p != 74, f"C21: S6 pos 74 must be excluded"


# ---------------------------------------------------------------------------
# Selection rationale strings (per-candidate)
# ---------------------------------------------------------------------------

STRATUM_NAMES: dict[int, str] = {s["stratum_id"]: s["name"] for s in STRATA_SPEC}


def build_rationale(
    pos: int,
    primary: int,
    meta_entry: dict[str, Any],
    is_fresh9: bool,
) -> str:
    fresh_clause = " (fresh-9 anchor)" if is_fresh9 else ""
    if primary == 1:
        return (
            f"S1 RSI-absent vol_regime (pos {pos}){fresh_clause}: tests "
            f"Stage 2c C16/C17 low-SVR claim on fresh candidate "
            f"(max_overlap={meta_entry['max_overlap_with_priors']}, "
            f"factor_set_size={meta_entry['factor_set_size']})."
        )
    if primary == 2:
        return (
            f"S2 RSI-present vol_regime control (pos {pos}): pairs "
            f"against S1 RSI-absent picks for sub-pattern isolation "
            f"(factor_set_size={meta_entry['factor_set_size']})."
        )
    if primary == 3:
        if (
            meta_entry["factor_set_size"] == 7
            and meta_entry["factor_set_prior_occurrences"] >= 1
        ):
            return (
                "S3 MR exact-7-factor repeat anchor (pos 197): only "
                "fresh exact 7-factor MR repeat in the batch; "
                "extends Stage 2c agreement-cluster pattern."
            )
        return (
            f"S3 MR high-overlap{fresh_clause}: max_overlap="
            f"{meta_entry['max_overlap_with_priors']}, "
            f"prior_occurrences={meta_entry['factor_set_prior_occurrences']} "
            "— extends agreement-cluster follow-through under broadened "
            "Lock 4.1 MR stratum."
        )
    if primary == 4:
        return (
            f"S4 early-position fresh (pos {pos} in 1-50): exercises "
            "early-batch behavior before Stage 2c selection-window "
            f"start (theme={meta_entry['theme']})."
        )
    if primary == 5:
        return (
            f"S5 late-position fresh (pos {pos} in 163-200){fresh_clause}: "
            "exercises late-batch behavior under enlarged prior history "
            f"(theme={meta_entry['theme']}, "
            f"max_overlap={meta_entry['max_overlap_with_priors']})."
        )
    if primary == 6:
        return (
            f"S6 rare-family theme '{meta_entry['theme']}'"
            f"{fresh_clause}: theme coverage beyond MR/vol_regime; "
            "earliest-position pick within theme."
        )
    raise ValueError(f"unknown primary stratum {primary}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    if not LABEL_UNIVERSE_PATH.exists():
        raise SystemExit("Task 2A label_universe_analysis.json missing")
    if not REPLAY_CANDIDATES_PATH.exists():
        raise SystemExit("Task 2B replay_candidates.json missing")

    label_universe_sha = sha256_of(LABEL_UNIVERSE_PATH)
    replay_candidates_sha = sha256_of(REPLAY_CANDIDATES_PATH)
    summary = load_json(BATCH_SUMMARY_PATH)
    replay_doc = load_json(REPLAY_CANDIDATES_PATH)

    meta = scan_metadata(summary)

    # Replay-eligible set from Task 2B (positions where is_skipped_source is False)
    replay_eligible: set[int] = {
        c["position"] for c in replay_doc["candidates"]
        if not c["is_skipped_source"]
    }

    # Greedy sequential per-stratum selection
    selected: dict[int, int] = {}  # position -> primary_stratum_id
    strata_picks: dict[int, list[int]] = {sid: [] for sid in (1, 2, 3, 4, 5, 6)}

    for spec in STRATA_SPEC:
        sid = spec["stratum_id"]
        target = spec["target"]
        predicate = STRATUM_PREDICATES[sid]
        # Pool = eligible positions not yet selected
        pool = [
            p for p in sorted(meta.keys())
            if predicate(p, meta[p]) and p not in selected
        ]
        if sid == 6:
            picks = select_s6_theme_balanced(pool, meta)
        else:
            picks = select_stratum_picks(sid, target, pool, meta)
        for p in picks:
            selected[p] = sid
            strata_picks[sid].append(p)

    # Universe A label map (from Task 2A)
    label_universe = load_json(LABEL_UNIVERSE_PATH)
    ua_buckets = label_universe["universe_a"]["candidate_positions"]
    ua_label_map: dict[int, str] = {}
    for label, positions in ua_buckets.items():
        for p in positions:
            ua_label_map[p] = label

    # Build candidate entries
    candidates: list[dict[str, Any]] = []
    for pos in sorted(selected.keys()):
        primary = selected[pos]
        m = meta[pos]
        also = compute_also_fits(pos, primary, meta)
        is_fresh9 = pos in FRESH_9
        candidates.append({
            "position": pos,
            "theme": m["theme"],
            "primary_stratum_id": primary,
            "also_fits_strata": also,
            "is_in_fresh_eligible_pool": is_fresh9,
            "universe_a_label": ua_label_map.get(pos),
            "universe_b_label": m["universe_b_label"],
            "factor_set_size": m["factor_set_size"],
            "factor_set_prior_occurrences": m["factor_set_prior_occurrences"],
            "max_overlap_with_priors": m["max_overlap_with_priors"],
            "selection_rationale": build_rationale(pos, primary, m, is_fresh9),
        })

    fresh_inclusion_count = sum(
        1 for c in candidates if c["is_in_fresh_eligible_pool"]
    )

    strata_out: list[dict[str, Any]] = []
    for spec in STRATA_SPEC:
        sid = spec["stratum_id"]
        sp = sorted(strata_picks[sid])
        out = {
            "stratum_id": sid,
            "name": spec["name"],
            "min_count": spec["min_count"],
            "max_count": spec["max_count"],
            "selected_count": len(sp),
            "fresh_pool_size": spec["fresh_pool_size"],
            "selected_positions": sp,
        }
        strata_out.append(out)

    selection_timestamp = (
        _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    )

    result: dict[str, Any] = {
        "source_batch_uuid": SOURCE_BATCH_UUID,
        "stage": "d7_stage2d",
        "scope_lock_commit": SCOPE_LOCK_COMMIT,
        "label_universe_analysis_sha256": label_universe_sha,
        "replay_candidates_sha256": replay_candidates_sha,
        "selection_timestamp_utc": selection_timestamp,
        "selection_methodology": SELECTION_METHODOLOGY,
        "total_deep_dive_count": 20,
        "fresh_eligible_pool_inclusion_count": fresh_inclusion_count,
        "strata": strata_out,
        "candidates": candidates,
    }

    run_invariants(
        result, meta, label_universe_sha, replay_candidates_sha,
        replay_eligible,
    )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8") as fh:
        json.dump(result, fh, sort_keys=True, indent=2)
        fh.write("\n")

    # Summary
    print(f"source_batch_uuid               = {SOURCE_BATCH_UUID}")
    print(f"scope_lock_commit               = {SCOPE_LOCK_COMMIT}")
    print(f"label_universe_analysis_sha256  = {label_universe_sha}")
    print(f"replay_candidates_sha256        = {replay_candidates_sha}")
    print(f"total_deep_dive_count           = 20")
    print(f"fresh_eligible_pool_inclusion   = {fresh_inclusion_count}/9")
    print(f"output                          = "
          f"{OUTPUT_PATH.relative_to(_REPO_ROOT)}")
    print()
    print("Per-stratum selections:")
    for s in strata_out:
        fresh_in = sum(1 for p in s["selected_positions"] if p in FRESH_9)
        print(f"  S{s['stratum_id']} '{s['name']}': "
              f"{s['selected_count']} (min {s['min_count']}, "
              f"max {s['max_count']}, fresh-9: {fresh_in}) → "
              f"{s['selected_positions']}")
    print()
    print(f"All 20 candidates (sorted): "
          f"{[c['position'] for c in candidates]}")
    print("All 21 invariants (C1-C21) PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())

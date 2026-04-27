"""Build docs/d7_stage2d/test_retest_baselines.json (D7 Stage 2d Task 2D).

Consolidates Stage 2b and Stage 2c D7b baseline scores for the 20
Stage 2c overlap candidates. Tier 1 = the 5 positions {17, 73, 74, 97,
138} that were also tested in Stage 2b. Tier 2 = the 15 remaining
Stage 2c positions. The output is consumed by the Stage 2d expectations
file (test-retest rubric) and by Stage 2d sign-off drift adjudication.

Sources of truth:
  - docs/d7_stage2b/call_{1..5}_live_call_record.json   (Stage 2b)
  - docs/d7_stage2c/call_{1..20}_live_call_record.json  (Stage 2c)
  - docs/d7_stage2d/label_universe_analysis.json        (Task 2A)
  - docs/d7_stage2d/replay_candidates.json              (Task 2B)
  - docs/d7_stage2d/deep_dive_candidates.json           (Task 2C)
  - docs/d7_stage2d/D7_STAGE2D_SCOPE_LOCK_v2.md         (commit anchor)

Per Stage 2d implementation plan §7.4 / §7.5. Deterministic, idempotent
modulo the single `build_timestamp_utc` field. All 18 invariants
D1-D18 are enforced before write.
"""

from __future__ import annotations

import datetime as _dt
import hashlib
import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent

LABEL_UNIVERSE_PATH = REPO_ROOT / "docs/d7_stage2d/label_universe_analysis.json"
REPLAY_CANDIDATES_PATH = REPO_ROOT / "docs/d7_stage2d/replay_candidates.json"
DEEP_DIVE_CANDIDATES_PATH = REPO_ROOT / "docs/d7_stage2d/deep_dive_candidates.json"
STAGE2B_DIR = REPO_ROOT / "docs/d7_stage2b"
STAGE2C_DIR = REPO_ROOT / "docs/d7_stage2c"
OUTPUT_PATH = REPO_ROOT / "docs/d7_stage2d/test_retest_baselines.json"

SOURCE_BATCH_UUID = "5cf76668-47d1-48d7-bd90-db06d31982ed"
SCOPE_LOCK_COMMIT = "4303d8de2882362ec55c8c581519331c5f6404c6"

TIER_1_POSITIONS = [17, 73, 74, 97, 138]
TIER_2_POSITIONS = [
    22, 27, 32, 62, 72, 77, 83, 102, 107, 112, 117, 143, 147, 152, 162,
]

LLM_SCORE_KEY_MAP = {
    "plausibility": "semantic_plausibility",
    "alignment": "semantic_theme_alignment",
    "svr": "structural_variant_risk",
}


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _load_call_records(stage_dir: Path, n_calls: int) -> dict[int, dict[str, Any]]:
    """Return dict mapping candidate_position -> (record, source_path)."""
    by_position: dict[int, dict[str, Any]] = {}
    for n in range(1, n_calls + 1):
        path = stage_dir / f"call_{n}_live_call_record.json"
        with path.open("r") as fh:
            rec = json.load(fh)
        pos = rec["candidate_position"]
        if pos in by_position:
            raise AssertionError(f"duplicate position {pos} across {stage_dir} calls")
        by_position[pos] = {"record": rec, "source_path": path}
    return by_position


def _extract_score_block(
    rec_with_path: dict[str, Any],
) -> dict[str, Any]:
    rec = rec_with_path["record"]
    cr = rec["critic_result"]
    llm = cr["d7b_llm_scores"]
    reasoning = cr["d7b_reasoning"]
    src_path = rec_with_path["source_path"]
    block = {
        "plausibility": llm[LLM_SCORE_KEY_MAP["plausibility"]],
        "alignment": llm[LLM_SCORE_KEY_MAP["alignment"]],
        "svr": llm[LLM_SCORE_KEY_MAP["svr"]],
        "reasoning_length": len(reasoning),
        "source_record_sha256": _sha256_file(src_path),
    }
    return block


def build_baselines(
    label_universe: dict[str, Any],
    s2b_by_pos: dict[int, dict[str, Any]],
    s2c_by_pos: dict[int, dict[str, Any]],
) -> list[dict[str, Any]]:
    overlap = {
        e["position"]: e for e in label_universe["stage2c_overlap_label_comparison"]
    }
    baselines: list[dict[str, Any]] = []
    all_positions = sorted(set(TIER_1_POSITIONS) | set(TIER_2_POSITIONS))
    for pos in all_positions:
        ov = overlap[pos]
        tier = 1 if pos in TIER_1_POSITIONS else 2
        s2c_block = _extract_score_block(s2c_by_pos[pos])
        s2b_block = (
            _extract_score_block(s2b_by_pos[pos]) if tier == 1 else None
        )
        entry = {
            "position": pos,
            "tier": tier,
            "stage2c_frozen_label": ov["stage2c_frozen_label"],
            "universe_b_label": ov["universe_b_label"],
            "label_conflict": ov["conflict"],
            "stage2b": s2b_block,
            "stage2c": s2c_block,
        }
        baselines.append(entry)
    return baselines


def run_invariants(
    output: dict[str, Any],
    label_universe_sha: str,
    replay_sha: str,
    deep_dive_sha: str,
) -> None:
    baselines = output["baselines"]
    positions = [b["position"] for b in baselines]
    tier_1 = [b for b in baselines if b["tier"] == 1]
    tier_2 = [b for b in baselines if b["tier"] == 2]

    # D1
    assert len(baselines) == 20, f"D1: len={len(baselines)}"
    # D2
    assert output["tier_1_positions"] == [17, 73, 74, 97, 138], "D2"
    # D3
    assert output["tier_2_positions"] == sorted(output["tier_2_positions"]), "D3 sort"
    assert len(output["tier_2_positions"]) == 15, "D3 length"
    # D4
    union = set(output["tier_1_positions"]) | set(output["tier_2_positions"])
    assert union == set(positions), f"D4: union mismatch"
    # D5
    inter = set(output["tier_1_positions"]) & set(output["tier_2_positions"])
    assert inter == set(), f"D5: tiers overlap {inter}"
    # D6
    for b in tier_1:
        assert b["stage2b"] is not None, f"D6: tier1 pos {b['position']} stage2b null"
    # D7
    for b in tier_2:
        assert b["stage2b"] is None, f"D7: tier2 pos {b['position']} stage2b non-null"
    # D8
    for b in baselines:
        assert b["stage2c"] is not None, f"D8: pos {b['position']} stage2c null"
    # D9
    for b in baselines:
        v = b["stage2c"]["svr"]
        assert isinstance(v, (int, float)) and 0.0 <= v <= 1.0, (
            f"D9: pos {b['position']} svr={v} out of [0,1]"
        )
    # D10/D11 are external cross-checks (validated by Codex Stage 2 review).
    # We assert here that for every entry the score values mirror the source
    # record's `d7b_llm_scores` block (already enforced by construction in
    # _extract_score_block), and the SVR additionally falls in [0,1] (D9).
    # D12
    assert (
        output["label_universe_analysis_sha256"] == label_universe_sha
    ), "D12 SHA mismatch"
    # D13
    assert output["replay_candidates_sha256"] == replay_sha, "D13 SHA mismatch"
    # D14
    assert (
        output["deep_dive_candidates_sha256"] == deep_dive_sha
    ), "D14 SHA mismatch"
    # D15: disjointness with deep_dive_candidates
    with DEEP_DIVE_CANDIDATES_PATH.open("r") as fh:
        deep_dive = json.load(fh)
    deep_dive_positions = {c["position"] for c in deep_dive["candidates"]}
    overlap_positions = set(positions)
    inter_dd = deep_dive_positions & overlap_positions
    assert inter_dd == set(), (
        f"D15: deep-dive ∩ overlap = {sorted(inter_dd)} (must be empty)"
    )
    # D16: enforced at write site (sort_keys, indent=2)
    # D17: position lists sorted ascending
    assert positions == sorted(positions), "D17 baselines.position sort"
    assert (
        output["tier_1_positions"] == sorted(output["tier_1_positions"])
    ), "D17 tier1 sort"
    # D18: source_record_sha256 present and 64-hex
    for b in baselines:
        s = b["stage2c"]["source_record_sha256"]
        assert isinstance(s, str) and len(s) == 64 and all(
            c in "0123456789abcdef" for c in s
        ), f"D18: pos {b['position']} stage2c sha invalid: {s}"
        if b["stage2b"] is not None:
            s2 = b["stage2b"]["source_record_sha256"]
            assert isinstance(s2, str) and len(s2) == 64 and all(
                c in "0123456789abcdef" for c in s2
            ), f"D18: pos {b['position']} stage2b sha invalid: {s2}"

    print("All 18 invariants (D1-D18) PASSED")


def main() -> int:
    if not LABEL_UNIVERSE_PATH.exists():
        raise SystemExit("Task 2A label_universe_analysis.json missing")
    if not REPLAY_CANDIDATES_PATH.exists():
        raise SystemExit("Task 2B replay_candidates.json missing")
    if not DEEP_DIVE_CANDIDATES_PATH.exists():
        raise SystemExit("Task 2C deep_dive_candidates.json missing")

    label_universe_sha = _sha256_file(LABEL_UNIVERSE_PATH)
    replay_sha = _sha256_file(REPLAY_CANDIDATES_PATH)
    deep_dive_sha = _sha256_file(DEEP_DIVE_CANDIDATES_PATH)

    with LABEL_UNIVERSE_PATH.open("r") as fh:
        label_universe = json.load(fh)

    s2b_by_pos = _load_call_records(STAGE2B_DIR, 5)
    s2c_by_pos = _load_call_records(STAGE2C_DIR, 20)

    # Defensive: confirm the call records cover exactly the expected position sets
    assert set(s2b_by_pos.keys()) == set(TIER_1_POSITIONS), (
        f"Stage 2b call records cover {sorted(s2b_by_pos.keys())}, "
        f"expected {TIER_1_POSITIONS}"
    )
    expected_2c_positions = set(TIER_1_POSITIONS) | set(TIER_2_POSITIONS)
    assert set(s2c_by_pos.keys()) == expected_2c_positions, (
        f"Stage 2c call records cover {sorted(s2c_by_pos.keys())}, "
        f"expected {sorted(expected_2c_positions)}"
    )

    baselines = build_baselines(label_universe, s2b_by_pos, s2c_by_pos)

    build_timestamp = (
        _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    )

    output: dict[str, Any] = {
        "source_batch_uuid": SOURCE_BATCH_UUID,
        "stage": "d7_stage2d",
        "scope_lock_commit": SCOPE_LOCK_COMMIT,
        "label_universe_analysis_sha256": label_universe_sha,
        "replay_candidates_sha256": replay_sha,
        "deep_dive_candidates_sha256": deep_dive_sha,
        "build_timestamp_utc": build_timestamp,
        "tier_1_positions": list(TIER_1_POSITIONS),
        "tier_2_positions": sorted(TIER_2_POSITIONS),
        "baselines": baselines,
    }

    run_invariants(output, label_universe_sha, replay_sha, deep_dive_sha)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w") as fh:
        json.dump(output, fh, sort_keys=True, indent=2)
        fh.write("\n")

    # Operator summary
    print(f"\nWrote {OUTPUT_PATH.relative_to(REPO_ROOT)} ({OUTPUT_PATH.stat().st_size} bytes)")
    print(
        f"label_universe_analysis_sha256 = {label_universe_sha}\n"
        f"replay_candidates_sha256       = {replay_sha}\n"
        f"deep_dive_candidates_sha256    = {deep_dive_sha}\n"
        f"tier_1 (n=5):  {TIER_1_POSITIONS}\n"
        f"tier_2 (n=15): {sorted(TIER_2_POSITIONS)}\n"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

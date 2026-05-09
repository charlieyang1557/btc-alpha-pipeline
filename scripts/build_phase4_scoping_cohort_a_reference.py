"""Build cohort_a candidate-level reference artifact for Phase 4 scoping cycle.

Descriptive-only lookup/index over the 39 cohort_a_unfiltered candidates from
PHASE2C_15 main fire (4-regime AND-gate passers: bear_2022 + validation_2024 +
eval_2020_v1 + eval_2021_v1). NO ranking, NO promotion semantics, NO composite
scoring, NO derived columns implying a selection mechanism.

Per Phase 4 scoping cycle entry binding (Charlie register authorized 2026-05-09):
- Path lean: (c) candidate-level forward-test generally (sub-path c.1/c.2/c.3
  or none-of-above adjudicated scoping-internal after this artifact reveals
  candidate distribution).
- Reference artifact column scope: advisor spec (hypothesis_hash + factors_used
  + theme + batch_id + WF Sharpe + WF total_trades + per-regime sharpe/
  total_trades/passed for 4 regimes + filtered bool).

Sources (verified 2026-05-09 at Phase 4 scoping cycle entry):
- data/phase2c_evaluation_gate/comparison_phase2c_15_main_fire_v1/
    comparison_summary.json   -> cohort_a hash lists
    comparison_matrix.csv     -> per-regime stats + WF sharpe
- data/phase2c_walkforward/batch_phase2c_15_main_fire_combined_corrected/
    walk_forward_results.csv  -> factors_used + batch_id + WF total_trades
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COMPARISON_DIR = ROOT / "data" / "phase2c_evaluation_gate" / "comparison_phase2c_15_main_fire_v1"
WF_BATCH_DIR = ROOT / "data" / "phase2c_walkforward" / "batch_phase2c_15_main_fire_combined_corrected"
OUTPUT_DIR = ROOT / "data" / "phase4_scoping"
OUTPUT_PATH = OUTPUT_DIR / "cohort_a_candidate_reference.csv"

REGIMES: tuple[str, ...] = ("bear_2022", "validation_2024", "eval_2020_v1", "eval_2021_v1")

EXPECTED_UNFILTERED: int = 39
EXPECTED_FILTERED: int = 24


def main() -> None:
    with open(COMPARISON_DIR / "comparison_summary.json") as f:
        summary = json.load(f)
    unfiltered_hashes = set(summary["cohort_a_unfiltered"])
    filtered_hashes = set(summary["cohort_a_filtered"])
    assert len(unfiltered_hashes) == EXPECTED_UNFILTERED, (
        f"cohort_a_unfiltered cardinality drift: {len(unfiltered_hashes)} != {EXPECTED_UNFILTERED}"
    )
    assert len(filtered_hashes) == EXPECTED_FILTERED, (
        f"cohort_a_filtered cardinality drift: {len(filtered_hashes)} != {EXPECTED_FILTERED}"
    )
    assert filtered_hashes.issubset(unfiltered_hashes), (
        "cohort_a_filtered must be a subset of cohort_a_unfiltered"
    )

    comparison_rows: dict[str, dict[str, str]] = {}
    with open(COMPARISON_DIR / "comparison_matrix.csv") as f:
        for row in csv.DictReader(f):
            h = row["hypothesis_hash"]
            if h in unfiltered_hashes:
                comparison_rows[h] = row
    assert len(comparison_rows) == EXPECTED_UNFILTERED, (
        f"comparison_matrix join incomplete: {len(comparison_rows)} != {EXPECTED_UNFILTERED}"
    )

    wf_rows: dict[str, dict[str, str]] = {}
    with open(WF_BATCH_DIR / "walk_forward_results.csv") as f:
        for row in csv.DictReader(f):
            h = row["hypothesis_hash"]
            if h in unfiltered_hashes:
                wf_rows[h] = row
    assert len(wf_rows) == EXPECTED_UNFILTERED, (
        f"walk_forward_results join incomplete: {len(wf_rows)} != {EXPECTED_UNFILTERED}"
    )

    output_rows: list[dict[str, object]] = []
    for h in sorted(unfiltered_hashes):
        cm = comparison_rows[h]
        wf = wf_rows[h]
        # theme cross-check between sources (defensive — both should agree)
        assert cm["theme"] == wf["theme"], (
            f"theme drift for {h}: comparison_matrix={cm['theme']!r} vs walk_forward_results={wf['theme']!r}"
        )
        row: dict[str, object] = {
            "hypothesis_hash": h,
            "factors_used": wf["factors_used"],
            "theme": cm["theme"],
            "batch_id": wf["batch_id"],
            "wf_test_period_sharpe": cm["wf_test_period_sharpe"],
            "wf_test_period_total_trades": wf["wf_test_period_total_trades"],
        }
        for regime in REGIMES:
            row[f"holdout_{regime}_sharpe"] = cm[f"holdout_{regime}_sharpe"]
            row[f"holdout_{regime}_total_trades"] = cm[f"holdout_{regime}_total_trades"]
            row[f"holdout_{regime}_passed"] = cm[f"holdout_{regime}_passed"]
        row["filtered"] = h in filtered_hashes
        output_rows.append(row)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    fieldnames = list(output_rows[0].keys())
    with open(OUTPUT_PATH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)

    n_filtered = sum(1 for r in output_rows if r["filtered"])
    assert len(output_rows) == EXPECTED_UNFILTERED
    assert n_filtered == EXPECTED_FILTERED

    rel = OUTPUT_PATH.relative_to(ROOT)
    print(f"Wrote {len(output_rows)} rows to {rel}")
    print(f"  cohort_a_unfiltered: {len(output_rows)} (expected {EXPECTED_UNFILTERED})")
    print(f"  cohort_a_filtered:   {n_filtered} (expected {EXPECTED_FILTERED})")
    print(f"  columns ({len(fieldnames)}): {', '.join(fieldnames)}")


if __name__ == "__main__":
    main()

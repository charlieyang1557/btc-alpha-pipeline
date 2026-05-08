"""PHASE2C_15 main-fire variant scripts — K=5 synthetic-fixture unit test.

Verifies that scripts/build_phase2c_15_main_fire_synthetic_batch.py +
scripts/build_phase2c_15_main_fire_partitioning_stats.py operate
correctly at K=5 universe (5 batches x 200 candidates = 1000 universe).

Test purpose per advisor Sub-Q2 reasoning: confirm no K=2 hardcode
survived parameterization and assertion paths fire correctly at K=5.

Constructed K=5 synthetic fixture exercises end-to-end pipeline:
1. Synthetic merged batch construction (5 sources -> 1000-row WF CSV)
2. Hash -> batch_id partitioning at K=5
3. Role 1 strict-exceedance + Fisher exact vs PHASE2C_12 baseline
4. Role 2 FFH Monte Carlo on 5x2 contingency
5. Role 2 supplementary pairwise = 10 pairs (5 choose 2)
"""
from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SYNTHETIC_BATCH_SCRIPT = (
    PROJECT_ROOT / "scripts" / "build_phase2c_15_main_fire_synthetic_batch.py"
)
PARTITIONING_STATS_SCRIPT = (
    PROJECT_ROOT / "scripts" / "build_phase2c_15_main_fire_partitioning_stats.py"
)

K = 5
N_PER_BATCH = 200
N_TOTAL = K * N_PER_BATCH  # 1000

# Per-batch success counts chosen so totals exceed 2.07% Wilson threshold,
# producing non-trivial contingency for FFH MC + pairwise tests.
# 5 + 6 + 5 + 6 + 5 = 27 / 1000 = 2.7%
PER_BATCH_SUCCESS = [5, 6, 5, 6, 5]
TOTAL_SUCCESS = sum(PER_BATCH_SUCCESS)  # 27

WF_CSV_FIELDNAMES = [
    "batch_id", "position", "hypothesis_hash", "name", "theme", "factors_used",
    "compile_status", "runtime_status",
    "wf_test_period_sharpe", "wf_test_period_return",
    "wf_test_period_max_drawdown", "wf_test_period_total_trades",
    "wf_test_period_win_rate", "wf_test_period_window_count",
    "elapsed_seconds", "error_message",
]

COMPARE_MATRIX_FIELDNAMES = [
    "hypothesis_hash", "theme", "partition", "wf_test_period_sharpe",
    "holdout_bear_2022_passed", "holdout_bear_2022_filter_state",
    "holdout_bear_2022_total_trades", "holdout_bear_2022_sharpe",
    "holdout_bear_2022_in_sample_caveat",
    "holdout_validation_2024_passed", "holdout_validation_2024_filter_state",
    "holdout_validation_2024_total_trades", "holdout_validation_2024_sharpe",
    "holdout_validation_2024_in_sample_caveat",
    "holdout_eval_2020_v1_passed", "holdout_eval_2020_v1_filter_state",
    "holdout_eval_2020_v1_total_trades", "holdout_eval_2020_v1_sharpe",
    "holdout_eval_2020_v1_in_sample_caveat",
    "holdout_eval_2021_v1_passed", "holdout_eval_2021_v1_filter_state",
    "holdout_eval_2021_v1_total_trades", "holdout_eval_2021_v1_sharpe",
    "holdout_eval_2021_v1_in_sample_caveat",
    "pass_count_unfiltered", "pass_count_filtered",
]

LINEAGE_DEFAULTS = {
    "corrected_wf_semantics_commit": "eb1c87f",
    "wf_semantics": "corrected_test_boundary_v1",
    "lineage_check": "passed",
    "git_sha": "eb1c87f",
    "current_git_sha": "5f73818",
    "phase1_success_threshold": 0.5,
}


def _hash_for(batch_idx: int, position: int) -> str:
    """Deterministic 16-char mock hypothesis_hash."""
    return f"k5b{batch_idx:02d}p{position:04d}xx"[:16].ljust(16, "0")


def _make_wf_artifact(
    wf_root: Path, batch_id: str, batch_idx: int, success_count: int
) -> None:
    """Author walk_forward_results.csv + walk_forward_summary.json for one batch."""
    batch_dir = wf_root / f"batch_{batch_id}_corrected"
    batch_dir.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, str]] = []
    for pos in range(1, N_PER_BATCH + 1):
        sharpe = "1.0" if pos <= success_count else "-0.1"
        rows.append({
            "batch_id": batch_id,
            "position": str(pos),
            "hypothesis_hash": _hash_for(batch_idx, pos),
            "name": f"mock_strat_{batch_idx}_{pos}",
            "theme": "momentum",
            "factors_used": "rsi_14;sma_50",
            "compile_status": "ok",
            "runtime_status": "ok",
            "wf_test_period_sharpe": sharpe,
            "wf_test_period_return": "0.1",
            "wf_test_period_max_drawdown": "0.05",
            "wf_test_period_total_trades": "30",
            "wf_test_period_win_rate": "0.55",
            "wf_test_period_window_count": "1",
            "elapsed_seconds": "1.0",
            "error_message": "",
        })

    csv_path = batch_dir / "walk_forward_results.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=WF_CSV_FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)

    summary = {
        "batch_id": batch_id,
        "compile_status_counts": {"ok": N_PER_BATCH},
        "runtime_status_counts": {"ok": N_PER_BATCH},
        "total_candidates": N_PER_BATCH,
        "total_elapsed_seconds": 200.0,
        "mean_elapsed_per_candidate_seconds": 1.0,
        "run_started_utc": f"2026-05-08T00:0{batch_idx}:00Z",
        "run_finished_utc": f"2026-05-08T00:0{batch_idx}:30Z",
        "phase1_binary_success_criterion_met": success_count > 0,
        **LINEAGE_DEFAULTS,
    }
    with open(batch_dir / "walk_forward_summary.json", "w") as f:
        json.dump(summary, f)


def _make_raw_payloads(
    raw_root: Path, batch_id: str, batch_idx: int
) -> None:
    """Author N attempt_*_response.txt placeholder files + stage2d_summary.json."""
    batch_dir = raw_root / f"batch_{batch_id}"
    batch_dir.mkdir(parents=True, exist_ok=True)

    # Tiny placeholder response files
    for pos in range(1, N_PER_BATCH + 1):
        (batch_dir / f"attempt_{pos:04d}_response.txt").write_text("placeholder\n")

    # stage2d_summary with calls covering all hashes
    calls = [
        {
            "position": pos,
            "hypothesis_hash": _hash_for(batch_idx, pos),
            "lifecycle_state": "approved",
            "valid_status": "ok",
        }
        for pos in range(1, N_PER_BATCH + 1)
    ]
    stage2d = {
        "batch_id": batch_id,
        "calls": calls,
        "total_valid_count": N_PER_BATCH,
        "distinct_hash_count": N_PER_BATCH,
    }
    with open(batch_dir / "stage2d_summary.json", "w") as f:
        json.dump(stage2d, f)


def _make_compare_matrix(compare_dir: Path) -> None:
    """Author comparison_matrix.csv + comparison_summary.json over K=5 universe.

    Per-batch success cohorts as defined in PER_BATCH_SUCCESS; pass_count == 4
    (all four regimes pass) for success rows.
    """
    compare_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, str]] = []
    for batch_idx, success_count in enumerate(PER_BATCH_SUCCESS):
        for pos in range(1, N_PER_BATCH + 1):
            is_success = pos <= success_count
            pass_count = 4 if is_success else 1
            row: dict[str, str] = {
                "hypothesis_hash": _hash_for(batch_idx, pos),
                "theme": "momentum",
                "partition": "audit_only",
                "wf_test_period_sharpe": "1.0" if is_success else "-0.1",
                "pass_count_unfiltered": str(pass_count),
                "pass_count_filtered": str(pass_count),
            }
            for regime in ("bear_2022", "validation_2024", "eval_2020_v1", "eval_2021_v1"):
                row[f"holdout_{regime}_passed"] = "True" if is_success else "False"
                row[f"holdout_{regime}_filter_state"] = "passing"
                row[f"holdout_{regime}_total_trades"] = "30"
                row[f"holdout_{regime}_sharpe"] = "1.0" if is_success else "-0.1"
                row[f"holdout_{regime}_in_sample_caveat"] = "False"
            rows.append(row)

    matrix_path = compare_dir / "comparison_matrix.csv"
    with open(matrix_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=COMPARE_MATRIX_FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)

    summary = {
        "comparison_schema_version": "comparison_schema_v2",
        "produced_at_utc": "2026-05-08T01:00:00Z",
        "cohort_a_cardinality_unfiltered": TOTAL_SUCCESS,
        "cohort_a_cardinality_filtered": TOTAL_SUCCESS,
        "cohort_a_unfiltered": [r["hypothesis_hash"] for r in rows[:TOTAL_SUCCESS]],
        "cohort_a_filtered": [r["hypothesis_hash"] for r in rows[:TOTAL_SUCCESS]],
        "cohort_c_cardinality_unfiltered": 0,
        "cohort_c_unfiltered": [],
        "in_sample_caveat_stratification": {},
        "pass_count_distribution": {"0": 0, "1": N_TOTAL - TOTAL_SUCCESS, "2": 0, "3": 0, "4": TOTAL_SUCCESS},
        "regime_metadata": {},
        "totals": {"valid_N": N_TOTAL},
    }
    with open(compare_dir / "comparison_summary.json", "w") as f:
        json.dump(summary, f)


@pytest.fixture
def k5_fixture(tmp_path: Path) -> dict[str, object]:
    """K=5 synthetic fixture: 5 batches x 200 candidates = 1000 universe."""
    wf_root = tmp_path / "wf"
    raw_root = tmp_path / "raw"
    compare_dir = tmp_path / "compare"
    wf_root.mkdir()
    raw_root.mkdir()

    batch_ids = [
        f"k5b{i:02d}-mock-aaaa-bbbb-cccccccccccc" for i in range(K)
    ]
    for batch_idx, (batch_id, success_count) in enumerate(
        zip(batch_ids, PER_BATCH_SUCCESS)
    ):
        _make_wf_artifact(wf_root, batch_id, batch_idx, success_count)
        _make_raw_payloads(raw_root, batch_id, batch_idx)

    return {
        "tmp": tmp_path,
        "wf_root": wf_root,
        "raw_root": raw_root,
        "compare_dir": compare_dir,
        "batch_ids": batch_ids,
        "synthetic_batch_id": "k5_test_combined",
    }


def test_synthetic_batch_script_at_k5(k5_fixture: dict[str, object]) -> None:
    """Synthetic batch script merges 5 sources into 1000-row WF CSV."""
    assert SYNTHETIC_BATCH_SCRIPT.exists(), (
        f"Main-fire synthetic batch script not yet authored at "
        f"{SYNTHETIC_BATCH_SCRIPT}. Step 1 of advisor sequence."
    )

    wf_root = k5_fixture["wf_root"]
    raw_root = k5_fixture["raw_root"]
    batch_ids = k5_fixture["batch_ids"]
    synthetic_batch_id = k5_fixture["synthetic_batch_id"]

    cmd = [
        sys.executable, str(SYNTHETIC_BATCH_SCRIPT),
        "--source-batch-ids", *batch_ids,
        "--synthetic-batch-id", synthetic_batch_id,
        "--wf-root", str(wf_root),
        "--raw-payloads-root", str(raw_root),
        "--expected-k", str(K),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0, (
        f"Synthetic batch script failed at K=5:\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )

    synth_wf = wf_root / f"batch_{synthetic_batch_id}_corrected"
    assert synth_wf.exists()

    with open(synth_wf / "walk_forward_results.csv") as f:
        merged_rows = list(csv.DictReader(f))
    assert len(merged_rows) == N_TOTAL, (
        f"Expected {N_TOTAL} merged rows; got {len(merged_rows)}"
    )

    positions = [int(r["position"]) for r in merged_rows]
    assert positions == list(range(1, N_TOTAL + 1)), (
        "Position contiguity 1..1000 violated post-merge"
    )

    per_batch = {bid: 0 for bid in batch_ids}
    for r in merged_rows:
        per_batch[r["batch_id"]] += 1
    assert all(c == N_PER_BATCH for c in per_batch.values()), (
        f"Per-batch row counts: {per_batch}; expected {N_PER_BATCH} each"
    )

    with open(synth_wf / "walk_forward_summary.json") as f:
        synth_summary = json.load(f)
    assert synth_summary["total_candidates"] == N_TOTAL
    assert synth_summary["batch_id"] == synthetic_batch_id
    assert synth_summary["lineage_check"] == "passed"

    synth_raw = raw_root / f"batch_{synthetic_batch_id}"
    response_links = list(synth_raw.glob("attempt_*_response.txt"))
    assert len(response_links) == N_TOTAL, (
        f"Expected {N_TOTAL} response symlinks; got {len(response_links)}"
    )


def test_partitioning_stats_script_at_k5(k5_fixture: dict[str, object]) -> None:
    """Partitioning stats script computes K=5 partitioning + Role 1 + Role 2 FFH MC + 10 pairwise."""
    assert PARTITIONING_STATS_SCRIPT.exists(), (
        f"Main-fire partitioning stats script not yet authored at "
        f"{PARTITIONING_STATS_SCRIPT}. Step 1 of advisor sequence."
    )

    wf_root = k5_fixture["wf_root"]
    raw_root = k5_fixture["raw_root"]
    compare_dir = k5_fixture["compare_dir"]
    batch_ids = k5_fixture["batch_ids"]
    synthetic_batch_id = k5_fixture["synthetic_batch_id"]

    # First, run synthetic batch script to produce synthetic raw_payloads dir
    # with source_stage2d_summary_<batch_id>.json symlinks.
    synth_cmd = [
        sys.executable, str(SYNTHETIC_BATCH_SCRIPT),
        "--source-batch-ids", *batch_ids,
        "--synthetic-batch-id", synthetic_batch_id,
        "--wf-root", str(wf_root),
        "--raw-payloads-root", str(raw_root),
        "--expected-k", str(K),
    ]
    synth_result = subprocess.run(synth_cmd, capture_output=True, text=True)
    assert synth_result.returncode == 0, (
        f"Synthetic batch prereq failed:\n{synth_result.stdout}\n{synth_result.stderr}"
    )

    # Author comparison_matrix + comparison_summary
    _make_compare_matrix(compare_dir)

    synth_raw = raw_root / f"batch_{synthetic_batch_id}"
    cmd = [
        sys.executable, str(PARTITIONING_STATS_SCRIPT),
        "--compare-dir", str(compare_dir),
        "--synthetic-raw-dir", str(synth_raw),
        "--expected-k", str(K),
        "--mc-iterations", "200",  # small B for unit test speed
        "--mc-seed", "42",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0, (
        f"Partitioning stats script failed at K=5:\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )

    # Verify per_batch_partition.json
    with open(compare_dir / "per_batch_partition.json") as f:
        partition = json.load(f)
    assert len(partition["batch_ids"]) == K
    assert partition["n_regimes"] == 4
    assert partition["totals"]["cohort_a_unfiltered"] == TOTAL_SUCCESS
    assert partition["totals"]["valid_N"] == N_TOTAL

    # Per-batch counts match expected per-batch successes
    for batch_id, expected_success in zip(batch_ids, PER_BATCH_SUCCESS):
        per = partition["per_batch_counts"][batch_id]
        assert per["valid_N"] == N_PER_BATCH
        assert per["cohort_a_unfiltered"] == expected_success

    # K x 2 contingency has 5 rows
    kx2 = partition["role2_kx2_contingency_unfiltered"]["rows"]
    assert len(kx2) == K, f"Expected {K} K×2 rows; got {len(kx2)}"

    # Verify statistical_summary.json
    with open(compare_dir / "statistical_summary.json") as f:
        stat = json.load(f)

    assert stat["n_total"] == N_TOTAL
    assert stat["cohort_a_unfiltered"] == TOTAL_SUCCESS
    observed_rate = TOTAL_SUCCESS / N_TOTAL
    assert abs(stat["observed_rate_unfiltered"] - observed_rate) < 1e-12
    assert stat["pre_registered_threshold"] == 0.0207

    # Role 1 strict-exceedance: 27/1000 = 2.7% > 2.07% → True
    assert stat["role1_strict_exceedance"]["unfiltered"]["exceeds_threshold"] is True

    # Role 1 auxiliary Fisher exact valid
    aux = stat["role1_auxiliary_fisher_exact_vs_phase2c_12"]
    assert 0.0 <= aux["p_value_two_sided"] <= 1.0
    assert aux["odds_ratio"] >= 0
    assert aux["phase2c_12_baseline"]["cohort_a"] == 8
    assert aux["phase2c_12_baseline"]["n"] == 197

    # Role 2 omnibus FFH at K=5 (Monte Carlo)
    role2 = stat["role2_omnibus_ffh_kx2"]
    assert role2["K"] == K
    assert role2["computation_method"] in ("monte_carlo", "exact")
    assert 0.0 <= role2["p_value_two_sided"] <= 1.0
    assert len(role2["contingency_table"]) == K
    for row in role2["contingency_table"]:
        assert len(row) == 2

    # Role 2 supplementary pairwise = K choose 2 = 10 pairs at K=5
    pairwise = stat["role2_supplementary_pairwise"]
    expected_n_pairs = K * (K - 1) // 2  # 10
    assert pairwise["n_pairs"] == expected_n_pairs
    assert len(pairwise["pairs"]) == expected_n_pairs
    for pair in pairwise["pairs"]:
        assert "batch_id_a" in pair and "batch_id_b" in pair
        assert "odds_ratio" in pair
        assert 0.0 <= pair["p_value_two_sided"] <= 1.0


def test_partitioning_stats_script_rejects_k_mismatch(
    k5_fixture: dict[str, object],
) -> None:
    """Partitioning stats script raises NotImplementedError if expected_k != actual K."""
    assert PARTITIONING_STATS_SCRIPT.exists()

    wf_root = k5_fixture["wf_root"]
    raw_root = k5_fixture["raw_root"]
    compare_dir = k5_fixture["compare_dir"]
    batch_ids = k5_fixture["batch_ids"]
    synthetic_batch_id = k5_fixture["synthetic_batch_id"]

    synth_cmd = [
        sys.executable, str(SYNTHETIC_BATCH_SCRIPT),
        "--source-batch-ids", *batch_ids,
        "--synthetic-batch-id", synthetic_batch_id,
        "--wf-root", str(wf_root),
        "--raw-payloads-root", str(raw_root),
        "--expected-k", str(K),
    ]
    subprocess.run(synth_cmd, check=True, capture_output=True)
    _make_compare_matrix(compare_dir)

    synth_raw = raw_root / f"batch_{synthetic_batch_id}"
    # Pass expected-k=7 to force mismatch (actual K=5 in fixture)
    cmd = [
        sys.executable, str(PARTITIONING_STATS_SCRIPT),
        "--compare-dir", str(compare_dir),
        "--synthetic-raw-dir", str(synth_raw),
        "--expected-k", "7",
        "--mc-iterations", "200",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode != 0, (
        "Script should fail when expected_k mismatches actual K"
    )
    assert "expected" in result.stderr.lower() or "expected" in result.stdout.lower() or "k" in result.stderr.lower()

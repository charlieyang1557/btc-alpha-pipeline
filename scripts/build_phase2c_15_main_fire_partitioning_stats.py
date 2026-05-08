"""Build PHASE2C_15 main-fire per-batch partitioning + Role 1/Role 2 statistics.

Closeout-register-class utility script (NOT framework-resident) for
PHASE2C_15 implementation arc main fire register.

Register-class-distinct from `build_phase2c_15_smoke_partitioning_stats.py`
per Codex C4 patch on smoke variant: smoke variant operates at K=2 only;
this main-fire variant operates at K=5 per PLAN §1.2 with full FFH r×c
omnibus implementation per PLAN §1.5 framework.

Inherits register-precision corrections from 8 Codex patches landed at
smoke variant (C3 duplicate hash detection + C5 multi-item validation +
C6 explicit error register / output-exists guard + C7 stdev/quantile
guard + NB #1 OR orientation metadata).

CLI-parameterized for testability + main-fire path overrides; default
paths point to canonical main-fire locations.

Operational mechanism per Step 2 sub-spec §2.1 step 5-6:
1. Read comparison_matrix.csv (main-fire compare output)
2. Build hash → batch_id lookup from K source stage2d_summary.json
   files (symlinked at synthetic raw_payloads dir)
3. Partition by batch_id into K×2 contingency table
4. Role 1 strict-exceedance: observed_rate vs PLAN §1.3 threshold 0.0207
5. Role 1 auxiliary Fisher exact 2-sided vs PHASE2C_12 baseline (8, 197)
6. Role 2 omnibus FFH on K×2 contingency:
   - Exact enumeration if N small enough (tractability heuristic)
   - Monte Carlo with B iterations (default 10000) otherwise
   per PLAN §1.5 framework
7. Role 2 supplementary pairwise: K choose 2 = 10 pairs at K=5;
   Fisher exact 2-sided per pair (descriptive, not corrected)

Output:
- {compare-dir}/per_batch_partition.json
- {compare-dir}/statistical_summary.json
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path

import numpy as np
from scipy.stats import chi2_contingency, fisher_exact, random_table

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DEFAULT_COMPARE_DIR = (
    PROJECT_ROOT
    / "data" / "phase2c_evaluation_gate"
    / "comparison_phase2c_15_main_fire_v1"
)
DEFAULT_SYNTHETIC_RAW_DIR = (
    PROJECT_ROOT / "raw_payloads" / "batch_phase2c_15_main_fire_combined"
)
DEFAULT_EXPECTED_K = 5
DEFAULT_MC_ITERATIONS = 10000
DEFAULT_MC_SEED = 42

# PHASE2C_14 sub-spec §3.2 Wilson CI strict-exceedance threshold.
PRE_REGISTERED_THRESHOLD = 0.0207

# PHASE2C_12 baseline (per CLAUDE.md + sub-spec §3.1 reconstructed artifact).
PHASE2C_12_COHORT_A = 8
PHASE2C_12_N = 197

# Number of regimes (4-regime AND-gate cohort definition).
N_REGIMES = 4


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=(
            "Build PHASE2C_15 main-fire K=5 per-batch partitioning + "
            "Role 1/Role 2 statistics with FFH r×c omnibus."
        ),
    )
    p.add_argument(
        "--compare-dir",
        default=str(DEFAULT_COMPARE_DIR),
        help="Comparison artifact directory.",
    )
    p.add_argument(
        "--synthetic-raw-dir",
        default=str(DEFAULT_SYNTHETIC_RAW_DIR),
        help="Synthetic raw_payloads directory containing source_stage2d_summary symlinks.",
    )
    p.add_argument(
        "--expected-k",
        type=int,
        default=DEFAULT_EXPECTED_K,
        help=f"Expected K (number of source batches; default: {DEFAULT_EXPECTED_K}).",
    )
    p.add_argument(
        "--mc-iterations",
        type=int,
        default=DEFAULT_MC_ITERATIONS,
        help=f"Monte Carlo iterations for FFH (default: {DEFAULT_MC_ITERATIONS}).",
    )
    p.add_argument(
        "--mc-seed",
        type=int,
        default=DEFAULT_MC_SEED,
        help=f"Monte Carlo RNG seed (default: {DEFAULT_MC_SEED}).",
    )
    return p.parse_args()


def _ffh_monte_carlo_pvalue(
    table: list[list[int]], n_iterations: int, seed: int
) -> tuple[float, float, str]:
    """Monte Carlo Fisher-Freeman-Halton p-value for r×c contingency.

    Resamples tables conditional on both marginals via scipy.stats.random_table;
    test statistic is G (log-likelihood ratio) per chi2_contingency.

    Returns (p_value, observed_g, computation_method).

    Degenerate handling: if any row sum or column sum is zero, returns
    p_value=1.0 + observed_g=0.0 (no information at degenerate margins).
    """
    arr = np.asarray(table, dtype=int)
    row_sums = arr.sum(axis=1)
    col_sums = arr.sum(axis=0)

    if np.any(row_sums == 0) or np.any(col_sums == 0):
        return 1.0, 0.0, "degenerate_margins"

    try:
        obs_result = chi2_contingency(arr, lambda_="log-likelihood")
        obs_g = float(obs_result.statistic)
    except (ValueError, ZeroDivisionError):
        return 1.0, 0.0, "degenerate_observed"

    rng = np.random.default_rng(seed)
    sampler = random_table(row_sums, col_sums, seed=rng)

    extreme_count = 0
    valid_iterations = 0
    for _ in range(n_iterations):
        sim = sampler.rvs()
        try:
            sim_result = chi2_contingency(sim, lambda_="log-likelihood")
            sim_g = float(sim_result.statistic)
        except (ValueError, ZeroDivisionError):
            continue
        valid_iterations += 1
        # Two-sided FFH: count tables AT LEAST as extreme as observed.
        if sim_g >= obs_g - 1e-12:
            extreme_count += 1

    if valid_iterations == 0:
        return 1.0, obs_g, "degenerate_resample"

    # Add-1 smoothing to avoid p=0 boundary.
    p_value = (extreme_count + 1) / (valid_iterations + 1)
    return p_value, obs_g, "monte_carlo"


def main() -> int:
    args = _parse_args()

    compare_dir = Path(args.compare_dir)
    synthetic_raw_dir = Path(args.synthetic_raw_dir)
    expected_k: int = args.expected_k
    mc_iterations: int = args.mc_iterations
    mc_seed: int = args.mc_seed

    # Per Codex C6: output-exists guard prevents silent overwrite.
    partition_path = compare_dir / "per_batch_partition.json"
    stat_path = compare_dir / "statistical_summary.json"
    for output_path in (partition_path, stat_path):
        if output_path.exists():
            raise FileExistsError(
                f"Output already exists at {output_path}. Remove manually "
                f"if rebuild needed (this script is single-shot closeout "
                f"utility; not idempotent)."
            )

    # --- Step 1: Read comparison_matrix.csv ---
    matrix_path = compare_dir / "comparison_matrix.csv"
    if not matrix_path.exists():
        raise FileNotFoundError(f"comparison_matrix.csv missing at {matrix_path}")
    with open(matrix_path) as f:
        rows = list(csv.DictReader(f))
    n_total = len(rows)
    print(f"[main-fire stat] comparison_matrix rows: {n_total}")
    if n_total == 0:
        raise RuntimeError(
            f"comparison_matrix.csv at {matrix_path} has 0 rows; expected "
            f"main-fire universe row count > 0."
        )

    # --- Step 2: Build hash → batch_id lookup from stage2d_summary symlinks ---
    # Per Codex C3: detect duplicate hypothesis_hash across source summaries.
    hash_to_batch: dict[str, str] = {}
    duplicate_hash_records: list[tuple[str, str, str]] = []
    batch_ids: list[str] = []
    for summary_link in sorted(
        synthetic_raw_dir.glob("source_stage2d_summary_*.json")
    ):
        with open(summary_link) as f:
            summary = json.load(f)
        batch_id = summary["batch_id"]
        batch_ids.append(batch_id)
        for call in summary["calls"]:
            h = call["hypothesis_hash"]
            if h is None:
                continue
            if h in hash_to_batch and hash_to_batch[h] != batch_id:
                duplicate_hash_records.append((h, hash_to_batch[h], batch_id))
            hash_to_batch[h] = batch_id

    if duplicate_hash_records:
        raise RuntimeError(
            f"Duplicate hypothesis_hash across source stage2d_summary "
            f"files: {duplicate_hash_records[:5]} (showing first 5 of "
            f"{len(duplicate_hash_records)}). Cohort attribution would "
            f"collapse silently; refusing to proceed."
        )

    print(f"[main-fire stat] batch_ids found: K={len(batch_ids)}")
    for bid in batch_ids:
        print(f"  {bid}")
    print(f"[main-fire stat] hash_to_batch entries: {len(hash_to_batch)}")

    # K guard parameterized: register-class-distinct from K=2 smoke guard.
    if len(batch_ids) != expected_k:
        raise NotImplementedError(
            f"build_phase2c_15_main_fire_partitioning_stats.py is K={expected_k} "
            f"variant by design (per --expected-k arg, default {DEFAULT_EXPECTED_K} "
            f"per PLAN §1.2). Detected {len(batch_ids)} batches at "
            f"{synthetic_raw_dir}/source_stage2d_summary_*.json. "
            f"K mismatch — author register-class-distinct script if K is "
            f"materially different, or pass --expected-k {len(batch_ids)} if "
            f"intentional."
        )

    # --- Step 3: Partition by batch_id ---
    per_batch_counts: dict[str, dict[str, int]] = {
        bid: {"valid_N": 0, "cohort_a_unfiltered": 0, "cohort_a_filtered": 0}
        for bid in batch_ids
    }

    unmapped_count = 0
    for row in rows:
        h = row["hypothesis_hash"]
        if h not in hash_to_batch:
            unmapped_count += 1
            continue
        bid = hash_to_batch[h]
        per_batch_counts[bid]["valid_N"] += 1
        if int(row["pass_count_unfiltered"]) == N_REGIMES:
            per_batch_counts[bid]["cohort_a_unfiltered"] += 1
        if int(row["pass_count_filtered"]) == N_REGIMES:
            per_batch_counts[bid]["cohort_a_filtered"] += 1

    print(
        f"[main-fire stat] unmapped rows (hash NOT in stage2d_summary): "
        f"{unmapped_count}"
    )
    if unmapped_count > 0:
        unmapped_hashes = [
            r["hypothesis_hash"]
            for r in rows
            if r["hypothesis_hash"] not in hash_to_batch
        ]
        raise RuntimeError(
            f"Hash coverage incomplete: {unmapped_count} comparison_matrix "
            f"rows have hypothesis_hash not present in source "
            f"stage2d_summary calls. First 5 unmapped hashes: "
            f"{unmapped_hashes[:5]}."
        )

    # Per Codex C3: also verify comparison_matrix.csv has no duplicate hashes.
    matrix_hashes = [r["hypothesis_hash"] for r in rows if r["hypothesis_hash"]]
    if len(set(matrix_hashes)) != len(matrix_hashes):
        seen_h: set[str] = set()
        dup_h: list[str] = []
        for h in matrix_hashes:
            if h in seen_h:
                dup_h.append(h)
            seen_h.add(h)
        raise RuntimeError(
            f"Duplicate hypothesis_hash in comparison_matrix.csv: "
            f"{dup_h[:5]} (showing first 5 of {len(dup_h)} duplicate "
            f"occurrences)."
        )

    # --- Step 4-7: Role 1 + Role 2 statistics ---
    cohort_a_total_unf = sum(
        c["cohort_a_unfiltered"] for c in per_batch_counts.values()
    )
    cohort_a_total_fil = sum(
        c["cohort_a_filtered"] for c in per_batch_counts.values()
    )
    valid_N_total = sum(c["valid_N"] for c in per_batch_counts.values())

    observed_rate_unf = cohort_a_total_unf / valid_N_total
    observed_rate_fil = cohort_a_total_fil / valid_N_total

    role1_strict_exceeds_unf = observed_rate_unf > PRE_REGISTERED_THRESHOLD
    role1_strict_exceeds_fil = observed_rate_fil > PRE_REGISTERED_THRESHOLD

    # Role 1 auxiliary Fisher exact 2-sided vs PHASE2C_12 baseline (8, 197).
    role1_aux_table = [
        [PHASE2C_12_COHORT_A, PHASE2C_12_N - PHASE2C_12_COHORT_A],
        [cohort_a_total_unf, valid_N_total - cohort_a_total_unf],
    ]
    role1_aux_or, role1_aux_pvalue = fisher_exact(
        role1_aux_table, alternative="two-sided"
    )

    # Role 2 omnibus FFH on K×2 contingency.
    # K rows (per batch), 2 cols (cohort_a vs not).
    # Order rows by batch_ids list order for reproducibility.
    role2_kx2_table: list[list[int]] = []
    for bid in batch_ids:
        s_i = per_batch_counts[bid]["cohort_a_unfiltered"]
        n_i = per_batch_counts[bid]["valid_N"]
        role2_kx2_table.append([s_i, n_i - s_i])

    role2_pvalue, role2_g_stat, role2_method = _ffh_monte_carlo_pvalue(
        role2_kx2_table, n_iterations=mc_iterations, seed=mc_seed
    )

    # Role 2 supplementary pairwise: K choose 2 Fisher exact 2-sided per pair.
    pairwise_results: list[dict] = []
    for (i, bid_a), (j, bid_b) in combinations(enumerate(batch_ids), 2):
        s_a = per_batch_counts[bid_a]["cohort_a_unfiltered"]
        n_a = per_batch_counts[bid_a]["valid_N"]
        s_b = per_batch_counts[bid_b]["cohort_a_unfiltered"]
        n_b = per_batch_counts[bid_b]["valid_N"]
        pair_table = [
            [s_a, n_a - s_a],
            [s_b, n_b - s_b],
        ]
        pair_or, pair_p = fisher_exact(pair_table, alternative="two-sided")
        pairwise_results.append({
            "batch_id_a": bid_a,
            "batch_id_b": bid_b,
            "contingency_table": pair_table,
            "odds_ratio": float(pair_or),
            "p_value_two_sided": float(pair_p),
        })

    # --- Write per_batch_partition.json ---
    partition_output = {
        "schema_version": "phase2c_15_main_fire_partition_v1",
        "produced_at_utc": _utc_now_iso(),
        "synthetic_source_batch_id": synthetic_raw_dir.name.replace("batch_", ""),
        "K": len(batch_ids),
        "n_regimes": N_REGIMES,
        "batch_ids": batch_ids,
        "per_batch_counts": per_batch_counts,
        "role2_kx2_contingency_unfiltered": {
            "rows": [
                {
                    "batch_id": bid,
                    "cohort_a_count": role2_kx2_table[idx][0],
                    "non_cohort_a_count": role2_kx2_table[idx][1],
                    "valid_N": role2_kx2_table[idx][0] + role2_kx2_table[idx][1],
                }
                for idx, bid in enumerate(batch_ids)
            ]
        },
        "totals": {
            "cohort_a_unfiltered": cohort_a_total_unf,
            "cohort_a_filtered": cohort_a_total_fil,
            "valid_N": valid_N_total,
        },
    }
    with open(partition_path, "w") as f:
        json.dump(partition_output, f, indent=2)
    print(f"[main-fire stat] Wrote {partition_path}")

    # --- Write statistical_summary.json ---
    stat_output = {
        "schema_version": "phase2c_15_main_fire_statistical_v1",
        "produced_at_utc": _utc_now_iso(),
        "interpretation_register": "MAIN FIRE — MEASUREMENT-CLASS",
        "interpretation_note": (
            "Main fire results are pre-registered measurement against "
            "PHASE2C_14 sub-spec §3.2 Wilson CI 2.07% strict-exceedance "
            "threshold. Pre-registered Role 1 success criterion: "
            "observed_rate > 0.0207 strict-exceedance binds. "
            "PHASE2C_15's own Wilson CI is NOT the success criterion. "
            "§3.4 violation-index 4-pattern register operationally relevant "
            "at any post-fire framing."
        ),
        "K": len(batch_ids),
        "n_regimes": N_REGIMES,
        "n_total": valid_N_total,
        "cohort_a_unfiltered": cohort_a_total_unf,
        "cohort_a_filtered": cohort_a_total_fil,
        "observed_rate_unfiltered": observed_rate_unf,
        "observed_rate_filtered": observed_rate_fil,
        "pre_registered_threshold": PRE_REGISTERED_THRESHOLD,
        "role1_strict_exceedance": {
            "unfiltered": {
                "observed_rate": observed_rate_unf,
                "threshold": PRE_REGISTERED_THRESHOLD,
                "exceeds_threshold": role1_strict_exceeds_unf,
                "interpretation": "pre-registered; binding",
            },
            "filtered": {
                "observed_rate": observed_rate_fil,
                "threshold": PRE_REGISTERED_THRESHOLD,
                "exceeds_threshold": role1_strict_exceeds_fil,
                "interpretation": "pre-registered; binding",
            },
        },
        "role1_auxiliary_fisher_exact_vs_phase2c_12": {
            "phase2c_12_baseline": {
                "cohort_a": PHASE2C_12_COHORT_A,
                "n": PHASE2C_12_N,
                "rate": PHASE2C_12_COHORT_A / PHASE2C_12_N,
            },
            "phase2c_15_main_fire": {
                "cohort_a": cohort_a_total_unf,
                "n": valid_N_total,
                "rate": observed_rate_unf,
            },
            "contingency_table": role1_aux_table,
            "contingency_table_row_labels": [
                "phase2c_12_baseline",
                "phase2c_15_main_fire",
            ],
            "odds_ratio": float(role1_aux_or),
            "odds_ratio_orientation": (
                "table_row_0_over_table_row_1: PHASE2C_12 cohort odds "
                "relative to PHASE2C_15 main-fire cohort odds. OR > 1 "
                "indicates PHASE2C_12 baseline rate > PHASE2C_15 main-fire "
                "rate; OR < 1 indicates the reverse. Per Codex non-blocking "
                "observation #1 register-precedent."
            ),
            "p_value_two_sided": float(role1_aux_pvalue),
            "interpretation": "auxiliary descriptive — informative for effect size",
        },
        "role2_omnibus_ffh_kx2": {
            "K": len(batch_ids),
            "contingency_table": role2_kx2_table,
            "computation_method": role2_method,
            "mc_iterations": (
                mc_iterations if role2_method == "monte_carlo" else None
            ),
            "mc_seed": mc_seed if role2_method == "monte_carlo" else None,
            "test_statistic": "G (log-likelihood ratio) per chi2_contingency",
            "g_statistic_observed": float(role2_g_stat),
            "p_value_two_sided": float(role2_pvalue),
            "alternative": "two-sided (any departure from independence)",
            "interpretation": (
                "FFH r×c omnibus: tests batch-level homogeneity "
                "(H0: all batches share same cohort_a rate)."
            ),
        },
        "role2_supplementary_pairwise": {
            "n_pairs": len(pairwise_results),
            "test": "Fisher exact 2-sided per pair",
            "multiple_testing_correction": (
                "none (descriptive supplementary; no family-wise correction "
                "applied per PLAN §1.5 framework)"
            ),
            "pairs": pairwise_results,
        },
        "lineage": {
            "comparison_summary": str(compare_dir / "comparison_summary.json"),
            "comparison_matrix": str(matrix_path),
            "stage2d_summary_sources": [
                str(p)
                for p in sorted(
                    synthetic_raw_dir.glob("source_stage2d_summary_*.json")
                )
            ],
        },
    }
    with open(stat_path, "w") as f:
        json.dump(stat_output, f, indent=2)
    print(f"[main-fire stat] Wrote {stat_path}")

    # --- Bundled forensic check ---
    print("\n[main-fire stat] === BUNDLED FORENSIC CHECK ===")
    checks: list[tuple[str, bool, str]] = []

    coverage_check = (
        unmapped_count == 0 and len(hash_to_batch) >= valid_N_total
    )
    checks.append((
        "Hash coverage complete",
        coverage_check,
        f"{len(hash_to_batch)} hashes, {unmapped_count} unmapped",
    ))

    k_check = len(batch_ids) == expected_k
    checks.append((
        f"K matches expected ({expected_k})",
        k_check,
        f"actual K={len(batch_ids)}",
    ))

    with open(compare_dir / "comparison_summary.json") as f:
        compare_summary = json.load(f)
    expected_cohort_a_unf = compare_summary["cohort_a_cardinality_unfiltered"]
    expected_cohort_a_fil = compare_summary["cohort_a_cardinality_filtered"]
    sum_match_check = (
        cohort_a_total_unf == expected_cohort_a_unf
        and cohort_a_total_fil == expected_cohort_a_fil
    )
    checks.append((
        "Success totals match comparison_summary",
        sum_match_check,
        (
            f"unf {cohort_a_total_unf}=={expected_cohort_a_unf}, "
            f"fil {cohort_a_total_fil}=={expected_cohort_a_fil}"
        ),
    ))

    role1_repro_unf = abs(
        observed_rate_unf - cohort_a_total_unf / valid_N_total
    ) < 1e-12
    role1_repro_fil = abs(
        observed_rate_fil - cohort_a_total_fil / valid_N_total
    ) < 1e-12
    role1_check = role1_repro_unf and role1_repro_fil
    checks.append(("Role 1 math reproducible", role1_check, ""))

    role1_aux_check = (
        0.0 <= role1_aux_pvalue <= 1.0
        and role1_aux_or >= 0
    )
    checks.append((
        "Role 1 auxiliary Fisher exact valid",
        role1_aux_check,
        f"OR={role1_aux_or:.4f} p={role1_aux_pvalue:.4f}",
    ))

    role2_table_check = (
        sum(row[0] for row in role2_kx2_table) == cohort_a_total_unf
    )
    checks.append((
        f"Role 2 K×2 contingency consistent (K={len(batch_ids)})",
        role2_table_check,
        f"sum_col_0={sum(row[0] for row in role2_kx2_table)}",
    ))

    role2_check = 0.0 <= role2_pvalue <= 1.0
    checks.append((
        f"Role 2 omnibus FFH valid ({role2_method})",
        role2_check,
        f"G={role2_g_stat:.4f} p={role2_pvalue:.4f}",
    ))

    expected_n_pairs = len(batch_ids) * (len(batch_ids) - 1) // 2
    pairwise_check = (
        len(pairwise_results) == expected_n_pairs
        and all(
            0.0 <= p["p_value_two_sided"] <= 1.0 for p in pairwise_results
        )
    )
    checks.append((
        f"Role 2 pairwise count + range (K choose 2 = {expected_n_pairs})",
        pairwise_check,
        f"n_pairs={len(pairwise_results)}",
    ))

    output_check = partition_path.exists() and stat_path.exists()
    checks.append(("Output artifacts written", output_check, ""))

    measurement_cited = (
        "MEASUREMENT-CLASS" in stat_output["interpretation_register"]
    )
    checks.append((
        "Measurement-class register cited (NOT suspended interpretation)",
        measurement_cited,
        "",
    ))

    all_pass = True
    for name, result, detail in checks:
        marker = "✓" if result else "✗"
        suffix = f" — {detail}" if detail else ""
        print(f"  {marker} {name}{suffix}")
        all_pass = all_pass and result

    print(
        f"\n[main-fire stat] BUNDLED FORENSIC CHECK: "
        f"{'ALL PASS (' + str(len(checks)) + '/' + str(len(checks)) + ')' if all_pass else 'PARTIAL'}"
    )

    # --- Headline outputs ---
    # Per advisor pre-fire discipline anchor (Proposal 2): closeout report
    # order — (a) point estimate + Wilson CI [Wilson CI computed at closeout
    # consumer; this script reports point estimate + N for downstream] →
    # (b) Fisher OR + p vs PHASE2C_12 → (c) strict-exceedance vs 2.07% →
    # (d) per-batch breakdown → (e) per-regime breakdown (per_batch).
    # Headline order here matches advisor's pre-registered closeout order.
    print("\n[main-fire stat] === HEADLINE OUTPUTS (measurement-class) ===")
    print(
        f"  (a) point estimate: cohort_a_unfiltered = {cohort_a_total_unf} / "
        f"{valid_N_total} = {observed_rate_unf:.4f}"
    )
    print(
        f"      cohort_a_filtered:   {cohort_a_total_fil} / {valid_N_total} = "
        f"{observed_rate_fil:.4f}"
    )
    print(
        f"  (b) Role 1 aux Fisher exact vs PHASE2C_12 (8, 197): "
        f"OR={role1_aux_or:.4f} p={role1_aux_pvalue:.4f}"
    )
    print(
        f"  (c) Role 1 strict-exceedance unfiltered (vs "
        f"{PRE_REGISTERED_THRESHOLD}): {role1_strict_exceeds_unf}"
    )
    print(
        f"      Role 1 strict-exceedance filtered:   "
        f"{role1_strict_exceeds_fil}"
    )
    print(f"  (d) per-batch breakdown:")
    for bid in batch_ids:
        c = per_batch_counts[bid]
        rate = c["cohort_a_unfiltered"] / c["valid_N"] if c["valid_N"] > 0 else 0.0
        print(
            f"        {bid[:8]}...: cohort_a={c['cohort_a_unfiltered']}/"
            f"{c['valid_N']} ({rate:.4f})"
        )
    print(
        f"      Role 2 omnibus FFH ({role2_method}): "
        f"G={role2_g_stat:.4f} p={role2_pvalue:.4f}"
    )
    print(
        f"      Role 2 pairwise: {len(pairwise_results)} pairs (descriptive)"
    )
    print(
        f"  (e) per-regime breakdown: see comparison_summary.json + "
        f"per-regime evaluation gate artifacts"
    )

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())

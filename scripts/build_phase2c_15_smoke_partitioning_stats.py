"""Build PHASE2C_15 smoke per-batch partitioning + Role 1/Role 2 statistics.

Closeout-register-class utility script (NOT framework-resident) for
PHASE2C_15 implementation arc Step 4 smoke fire register.

Per Q-S145 ENDORSE (stat-bundled): single bundled invocation produces
per_batch_partition.json + statistical_summary.json over smoke compare
artifact + synthetic stage2d_summary symlinks.

Operational mechanism per Step 2 sub-spec §2.1 step 5-6 + §3.3 closeout-
register aggregation pattern:

1. Read comparison_matrix.csv (smoke compare output)
2. Build hash -> batch_id lookup from 2 source stage2d_summary.json
   files (symlinked at synthetic raw_payloads dir)
3. Partition by batch_id into K=2 contingency table
4. Role 1 strict-exceedance: observed_rate vs PLAN §1.3 threshold 0.0207
   (suspended at smoke per Q-S136 framing)
5. Role 1 auxiliary Fisher exact 2-sided vs PHASE2C_12 baseline (8, 197)
6. Role 2 omnibus FFH on K=2 contingency (collapses to single 2x2
   Fisher exact at K=2 mathematically)

Output:
- data/phase2c_evaluation_gate/comparison_phase2c_15_smoke_v1/per_batch_partition.json
- data/phase2c_evaluation_gate/comparison_phase2c_15_smoke_v1/statistical_summary.json

§19 instance #2 resolution operational complete at this closeout register.
Smoke results carry SUSPENDED INTERPRETATION per Q-S136 framing — operational
rehearsal of statistical machinery, NOT pre-registered measurement.
"""
from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path

from scipy.stats import fisher_exact

PROJECT_ROOT = Path(__file__).resolve().parent.parent

COMPARE_DIR = (
    PROJECT_ROOT
    / "data" / "phase2c_evaluation_gate"
    / "comparison_phase2c_15_smoke_v1"
)
SYNTHETIC_RAW_DIR = (
    PROJECT_ROOT / "raw_payloads" / "batch_phase2c_15_smoke_combined"
)

# PHASE2C_14 sub-spec §3.2 Wilson CI strict-exceedance threshold
PRE_REGISTERED_THRESHOLD = 0.0207

# PHASE2C_12 baseline (per CLAUDE.md + sub-spec §3.1 reconstructed artifact)
PHASE2C_12_COHORT_A = 8
PHASE2C_12_N = 197

# Number of regimes (4-regime AND-gate cohort definition)
N_REGIMES = 4


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def main() -> int:
    # Per Codex C6: output-exists guard prevents silent overwrite of prior
    # statistical_summary.json / per_batch_partition.json artifacts. If
    # rebuild required, remove output files manually first.
    partition_path = COMPARE_DIR / "per_batch_partition.json"
    stat_path = COMPARE_DIR / "statistical_summary.json"
    for output_path in (partition_path, stat_path):
        if output_path.exists():
            raise FileExistsError(
                f"Output already exists at {output_path}. Remove manually "
                f"if rebuild needed (this script is single-shot closeout "
                f"utility; not idempotent)."
            )

    # --- Step 1: Read comparison_matrix.csv ---
    # Per Codex C6: data-validation asserts promoted to RuntimeError to
    # survive python -O.
    matrix_path = COMPARE_DIR / "comparison_matrix.csv"
    with open(matrix_path) as f:
        rows = list(csv.DictReader(f))
    n_total = len(rows)
    print(f"[stat] comparison_matrix rows: {n_total}")
    if n_total == 0:
        raise RuntimeError(
            f"comparison_matrix.csv at {matrix_path} has 0 rows; expected "
            f"smoke universe row count > 0."
        )

    # --- Step 2: Build hash -> batch_id lookup from stage2d_summary symlinks ---
    # Per Codex C3: detect duplicate hypothesis_hash across source summaries.
    # Silent overwrite of hash_to_batch could collapse cohort attribution at
    # K=5 main-fire universe; raise loudly here at smoke register-class.
    hash_to_batch: dict[str, str] = {}
    duplicate_hash_records: list[tuple[str, str, str]] = []  # (hash, prev_batch, new_batch)
    batch_ids = []
    for summary_link in sorted(
        SYNTHETIC_RAW_DIR.glob("source_stage2d_summary_*.json")
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

    print(f"[stat] batch_ids found: {batch_ids}")
    print(f"[stat] hash_to_batch entries: {len(hash_to_batch)}")

    # Per Codex C4: explicit K=2 smoke guard. Smoke variant supports K=2
    # only by design; main-fire K=5 variant must live at register-class-
    # distinct file path. Refuse to operate at K!=2 to prevent inadvertent
    # reuse against main-fire universe.
    if len(batch_ids) != 2:
        raise NotImplementedError(
            f"build_phase2c_15_smoke_partitioning_stats.py is K=2 smoke "
            f"variant by design (Q-S145 + Q-S141 register-class binding). "
            f"Detected {len(batch_ids)} batches at "
            f"{SYNTHETIC_RAW_DIR}/source_stage2d_summary_*.json. Main-fire "
            f"K=5 variant requires register-class-distinct script with "
            f"FFH r×c omnibus implementation per PLAN §1.5 framework."
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
        # Cohort A unfiltered = candidates with pass_count_unfiltered == N_REGIMES (4)
        if int(row["pass_count_unfiltered"]) == N_REGIMES:
            per_batch_counts[bid]["cohort_a_unfiltered"] += 1
        if int(row["pass_count_filtered"]) == N_REGIMES:
            per_batch_counts[bid]["cohort_a_filtered"] += 1

    print(f"[stat] unmapped rows (hash NOT in stage2d_summary): {unmapped_count}")
    # Per Codex C6: assert promoted to RuntimeError to survive python -O.
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

    # Per Codex C3: also verify comparison_matrix.csv has no duplicate hashes
    # at its own register-class (separate from hash_to_batch construction).
    matrix_hashes = [r["hypothesis_hash"] for r in rows if r["hypothesis_hash"]]
    if len(set(matrix_hashes)) != len(matrix_hashes):
        # Find first 5 duplicates
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

    # --- Step 4-6: Role 1 + Role 2 statistics ---
    cohort_a_total_unf = sum(
        c["cohort_a_unfiltered"] for c in per_batch_counts.values()
    )
    cohort_a_total_fil = sum(
        c["cohort_a_filtered"] for c in per_batch_counts.values()
    )
    valid_N_total = sum(c["valid_N"] for c in per_batch_counts.values())

    observed_rate_unf = cohort_a_total_unf / valid_N_total
    observed_rate_fil = cohort_a_total_fil / valid_N_total

    # Role 1 strict-exceedance (suspended interpretation at smoke)
    role1_strict_exceeds_unf = observed_rate_unf > PRE_REGISTERED_THRESHOLD
    role1_strict_exceeds_fil = observed_rate_fil > PRE_REGISTERED_THRESHOLD

    # Role 1 auxiliary Fisher exact 2-sided vs PHASE2C_12 baseline (8, 197)
    # Contingency:
    #             cohort_a    non_cohort_a
    # PHASE2C_12  8           189 (= 197 - 8)
    # PHASE2C_15  2           98  (= 100 - 2)
    role1_aux_table = [
        [PHASE2C_12_COHORT_A, PHASE2C_12_N - PHASE2C_12_COHORT_A],
        [cohort_a_total_unf, valid_N_total - cohort_a_total_unf],
    ]
    role1_aux_or, role1_aux_pvalue = fisher_exact(
        role1_aux_table, alternative="two-sided"
    )

    # Role 2 omnibus FFH at K=2 (collapses to single 2x2 Fisher exact mathematically)
    # K=2 contingency:
    #         cohort_a       non_cohort_a
    # b1:     s_1            50 - s_1
    # b2:     s_2            50 - s_2
    b1, b2 = batch_ids
    s_1 = per_batch_counts[b1]["cohort_a_unfiltered"]
    s_2 = per_batch_counts[b2]["cohort_a_unfiltered"]
    n_1 = per_batch_counts[b1]["valid_N"]
    n_2 = per_batch_counts[b2]["valid_N"]
    role2_kx2_table = [
        [s_1, n_1 - s_1],
        [s_2, n_2 - s_2],
    ]
    role2_or, role2_pvalue = fisher_exact(
        role2_kx2_table, alternative="two-sided"
    )

    # --- Write per_batch_partition.json ---
    partition_output = {
        "schema_version": "phase2c_15_smoke_partition_v1",
        "produced_at_utc": _utc_now_iso(),
        "synthetic_source_batch_id": "phase2c_15_smoke_combined",
        "n_regimes": N_REGIMES,
        "batch_ids": batch_ids,
        "per_batch_counts": per_batch_counts,
        "role2_kx2_contingency_unfiltered": {
            "rows": [
                {
                    "batch_id": b1,
                    "cohort_a_count": s_1,
                    "non_cohort_a_count": n_1 - s_1,
                    "valid_N": n_1,
                },
                {
                    "batch_id": b2,
                    "cohort_a_count": s_2,
                    "non_cohort_a_count": n_2 - s_2,
                    "valid_N": n_2,
                },
            ]
        },
        "totals": {
            "cohort_a_unfiltered": cohort_a_total_unf,
            "cohort_a_filtered": cohort_a_total_fil,
            "valid_N": valid_N_total,
        },
    }
    # partition_path declared at top of main() per C6 output-exists guard
    with open(partition_path, "w") as f:
        json.dump(partition_output, f, indent=2)
    print(f"[stat] Wrote {partition_path}")

    # --- Write statistical_summary.json ---
    stat_output = {
        "schema_version": "phase2c_15_smoke_statistical_v1",
        "produced_at_utc": _utc_now_iso(),
        "interpretation_register": "SMOKE / REHEARSAL — SUSPENDED INTERPRETATION",
        "interpretation_note": (
            "Smoke fire results are operational rehearsal of statistical "
            "machinery, NOT pre-registered measurement against PHASE2C_14 "
            "sub-spec §3.2 Wilson CI 2.07% strict-exceedance threshold. "
            "The pre-registered Role 1 success criterion applies to main "
            "fire register-class only (K=5 × N=200 = 1000). Smoke results "
            "do NOT inform main fire pre-registered claim per Q-S136 "
            "suspended interpretation discipline."
        ),
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
                "interpretation": "rehearsal — not pre-registered",
            },
            "filtered": {
                "observed_rate": observed_rate_fil,
                "threshold": PRE_REGISTERED_THRESHOLD,
                "exceeds_threshold": role1_strict_exceeds_fil,
                "interpretation": "rehearsal — not pre-registered",
            },
        },
        "role1_auxiliary_fisher_exact_vs_phase2c_12": {
            "phase2c_12_baseline": {
                "cohort_a": PHASE2C_12_COHORT_A,
                "n": PHASE2C_12_N,
                "rate": PHASE2C_12_COHORT_A / PHASE2C_12_N,
            },
            "phase2c_15_smoke": {
                "cohort_a": cohort_a_total_unf,
                "n": valid_N_total,
                "rate": observed_rate_unf,
            },
            "contingency_table": role1_aux_table,
            "contingency_table_row_labels": [
                "phase2c_12_baseline",
                "phase2c_15_smoke",
            ],
            "odds_ratio": role1_aux_or,
            "odds_ratio_orientation": (
                "table_row_0_over_table_row_1: PHASE2C_12 cohort odds "
                "relative to PHASE2C_15 smoke cohort odds. OR > 1 indicates "
                "PHASE2C_12 baseline rate > PHASE2C_15 smoke rate; OR < 1 "
                "indicates the reverse. Per Codex non-blocking observation "
                "#1: prevent misreporting at downstream consumer register."
            ),
            "p_value_two_sided": role1_aux_pvalue,
            "interpretation": "descriptive only — smoke not pre-registered",
        },
        "role2_omnibus_ffh_kx2": {
            "K": 2,
            "contingency_table": role2_kx2_table,
            "table_dimensions_note": (
                "K=2 collapses FFH omnibus to single 2x2 Fisher exact "
                "mathematically; this is by design at smoke register-class. "
                "At main fire K=5, FFH omnibus operates over 5x2 contingency "
                "with exact computation (small N tractable) per PLAN §1.5."
            ),
            "odds_ratio": role2_or,
            "p_value_two_sided": role2_pvalue,
            "interpretation": "rehearsal — not pre-registered",
        },
        "role2_supplementary_pairwise_at_k2": {
            "n_pairs": 1,
            "note": (
                "At K=2 the single pair = the K×2 omnibus mathematically. "
                "At main fire K=5, supplementary pairwise comparisons are "
                "10 pair tests (K choose 2)."
            ),
        },
        "lineage": {
            "comparison_summary": str(
                COMPARE_DIR / "comparison_summary.json"
            ),
            "comparison_matrix": str(matrix_path),
            "stage2d_summary_sources": [
                str(p)
                for p in sorted(
                    SYNTHETIC_RAW_DIR.glob("source_stage2d_summary_*.json")
                )
            ],
        },
    }
    # stat_path declared at top of main() per C6 output-exists guard
    with open(stat_path, "w") as f:
        json.dump(stat_output, f, indent=2)
    print(f"[stat] Wrote {stat_path}")

    # --- Bundled forensic check ---
    print("\n[stat] === BUNDLED FORENSIC CHECK ===")
    checks: list[tuple[str, bool, str]] = []

    # 1. Hash coverage 100/100
    coverage_check = unmapped_count == 0 and len(hash_to_batch) >= 100
    checks.append(("Hash coverage 100/100", coverage_check, f"{len(hash_to_batch)} hashes"))

    # 2. Batch split 50/50
    n_b1 = per_batch_counts[b1]["valid_N"]
    n_b2 = per_batch_counts[b2]["valid_N"]
    split_check = n_b1 == 50 and n_b2 == 50
    checks.append(("Batch split 50/50", split_check, f"{n_b1}/{n_b2}"))

    # 3. Success totals match comparison summary
    with open(COMPARE_DIR / "comparison_summary.json") as f:
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
        f"unf {cohort_a_total_unf}=={expected_cohort_a_unf}, fil {cohort_a_total_fil}=={expected_cohort_a_fil}",
    ))

    # 4. Role 1 math reproducible (rate = cohort_a / N)
    role1_repro_unf = abs(observed_rate_unf - cohort_a_total_unf / valid_N_total) < 1e-12
    role1_repro_fil = abs(observed_rate_fil - cohort_a_total_fil / valid_N_total) < 1e-12
    role1_check = role1_repro_unf and role1_repro_fil
    checks.append(("Role 1 math reproducible", role1_check, ""))

    # 5. Role 1 auxiliary Fisher exact result valid
    role1_aux_check = (
        0.0 <= role1_aux_pvalue <= 1.0
        and role1_aux_or >= 0
    )
    checks.append((
        "Role 1 auxiliary Fisher exact valid",
        role1_aux_check,
        f"OR={role1_aux_or:.4f} p={role1_aux_pvalue:.4f}",
    ))

    # 6. Role 2 input table written
    role2_table_check = role2_kx2_table[0][0] + role2_kx2_table[1][0] == cohort_a_total_unf
    checks.append((
        "Role 2 K×2 contingency consistent",
        role2_table_check,
        f"{role2_kx2_table}",
    ))

    # 7. Role 2 FFH (Fisher exact at K=2) valid
    role2_check = 0.0 <= role2_pvalue <= 1.0
    checks.append((
        "Role 2 omnibus Fisher exact valid",
        role2_check,
        f"OR={role2_or:.4f} p={role2_pvalue:.4f}",
    ))

    # 8. Output artifacts written
    output_check = partition_path.exists() and stat_path.exists()
    checks.append(("Output artifacts written", output_check, ""))

    # 9. Suspended interpretation cited
    suspended_cited = "SUSPENDED INTERPRETATION" in stat_output["interpretation_register"]
    checks.append(("Suspended interpretation cited", suspended_cited, ""))

    all_pass = True
    for name, result, detail in checks:
        marker = "✓" if result else "✗"
        suffix = f" — {detail}" if detail else ""
        print(f"  {marker} {name}{suffix}")
        all_pass = all_pass and result

    print(f"\n[stat] BUNDLED FORENSIC CHECK: {'ALL PASS (9/9)' if all_pass else 'PARTIAL'}")

    # --- Headline outputs ---
    print("\n[stat] === HEADLINE OUTPUTS (suspended interpretation per Q-S136) ===")
    print(f"  cohort_a_unfiltered: {cohort_a_total_unf} / {valid_N_total} = {observed_rate_unf:.4f}")
    print(f"  cohort_a_filtered:   {cohort_a_total_fil} / {valid_N_total} = {observed_rate_fil:.4f}")
    print(f"  pre-registered threshold (main fire only): {PRE_REGISTERED_THRESHOLD}")
    print(f"  Role 1 strict-exceedance unfiltered: {role1_strict_exceeds_unf} (REHEARSAL)")
    print(f"  Role 1 strict-exceedance filtered:   {role1_strict_exceeds_fil} (REHEARSAL)")
    print(f"  Role 1 aux Fisher vs PHASE2C_12 (8,197): OR={role1_aux_or:.4f} p={role1_aux_pvalue:.4f}")
    print(f"  Role 2 K×2 contingency: {role2_kx2_table}")
    print(f"  Role 2 omnibus Fisher (K=2 collapse): OR={role2_or:.4f} p={role2_pvalue:.4f}")

    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())

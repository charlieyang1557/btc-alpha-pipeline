# Task 2C — Stage 1 Self-Audit Report

**Task:** D7 Stage 2d Task 2C — `deep_dive_candidates.json`
**Auditor:** Claude Code (Stage 1 self-audit, per implementation plan §6.5)
**Date:** 2026-04-19

## Deliverable SHA256

| File | SHA256 |
|---|---|
| `docs/d7_stage2d/deep_dive_candidates.json` | `6cdcd1d22d785d6d58317f61cd62fe8b3340bd22f1ec7c7dcb90e5d2b2da7ce7` |
| `scripts/build_d7_stage2d_deep_dive.py` | `93cc0b2359d53e129092823353b6daa56beb0367f15b3b2b1f53d36cbd930e1c` |
| `docs/d7_stage2d/replay_candidates.json` (Task 2B predecessor, committed) | `05706642cbeb5014d5072c172b343b01ee56d0eb8ee45afb2f3ce6e56665907e` |
| `docs/d7_stage2d/label_universe_analysis.json` (Task 2A predecessor, committed) | `ecd52a9e7656d31d13a8e62ec11a7345f8966343172fbfc3f95add2762b3e4a0` |

Note: The output JSON SHA varies across runs only via the `selection_timestamp_utc`
field; the SHA above is from the committed version. Idempotency is byte-identical
modulo that single field, per plan §6.4 line 1471 (gate 2C.27).

## Per-stratum summary

| S# | Name | min | max | sel | fresh_pool_size | selected_positions | fresh-9 hits |
|---|---|---|---|---|---|---|---|
| 1 | RSI-absent volatility_regime | 3 | 5 | **5** | 7 | [68, 128, 173, 188, 198] | {128} |
| 2 | RSI-present volatility_regime | 2 | 4 | **2** | 29 | [8, 13] | {} |
| 3 | MR high-recurrence / high-overlap | 3 | 5 | **5** | null (broadened) | [122, 127, 132, 182, 197] | {122, 127, 132, 182} |
| 4 | Early-position 1-50 fresh | 2 | 4 | **2** | 46 | [1, 2] | {} |
| 5 | Late-position 163-200 fresh | 2 | 4 | **3** | 38 | [172, 178, 187] | {172, 178, 187} |
| 6 | Rare-families themes | 2 | 4 | **3** | null (theme-defined) | [5, 6, 129] | {129} |
| **Total** | | | | **20** | | | **9 / 9** |

Sum check: 5+2+5+2+3+3 = 20 ✓
Fresh-9 inclusion count: 9 (all 9 of `{122, 127, 128, 129, 132, 172, 178, 182, 187}` included).

## Per-item PASS/FAIL

**Prerequisite gates**

| # | Verdict | Evidence |
|---|---|---|
| 2C.1 | PASS | Task 2A committed at `1ce179f8…fd9a`; SHA256 = `ecd52a9e…b3e4a0`. |
| 2C.2 | PASS | Task 2B committed at `2771bef9b79db00ac421728b5f69fd908038ce9d`; SHA256 = `05706642…907e`. |
| 2C.3 | PASS | Output JSON `label_universe_analysis_sha256` = `ecd52a9e7656d31d13a8e62ec11a7345f8966343172fbfc3f95add2762b3e4a0`; matches committed Task 2A. |
| 2C.4 | PASS | Output JSON `replay_candidates_sha256` = `05706642cbeb5014d5072c172b343b01ee56d0eb8ee45afb2f3ce6e56665907e`; matches committed Task 2B. |

**Structural deliverable gates**

| # | Verdict | Evidence |
|---|---|---|
| 2C.5 | PASS | `docs/d7_stage2d/deep_dive_candidates.json` exists, 13560 bytes (post-schema-uniformity fix). |
| 2C.6 | PASS | `scripts/build_d7_stage2d_deep_dive.py` exists, 26057 bytes. |
| 2C.7 | PASS | `git diff -- docs/d7_stage2d/replay_candidates.json docs/d7_stage2d/label_universe_analysis.json scripts/build_d7_stage2d_replay_candidates.py scripts/derive_d7_stage2d_label_universes.py` is empty. |

**Stratum constraint gates**

| # | Verdict | Evidence |
|---|---|---|
| 2C.8 | PASS | All 6 strata defined; names match Lock 4.1; min/max ranges = (3,5),(2,4),(3,5),(2,4),(2,4),(2,4). |
| 2C.9 | PASS | S1 selected = [68, 128, 173, 188, 198]; subset of fresh-RSI-absent pool {3, 43, 68, 128, 173, 188, 198}. selected_count=5 ∈ [3,5]. |
| 2C.10 | PASS | S2 selected = [8, 13]; selected_count=2 ∈ [2,4]. |
| 2C.11 | PASS | S3 selected = [122, 127, 132, 182, 197]; selected_count=5 ∈ [3,5]; uses broadened MR predicate `theme==mean_reversion AND ((factor_set_size==7 AND prior_occurrences>=1) OR max_overlap_with_priors>=5)` (script `in_s3` at scripts/build_d7_stage2d_deep_dive.py:288). |
| 2C.12 | PASS | S4 selected = [1, 2]; both in 1-50; selected_count=2 ∈ [2,4]. |
| 2C.13 | PASS | S5 selected = [172, 178, 187]; all in 163-200; selected_count=3 ∈ [2,4]. |
| 2C.14 | PASS | S6 selected = [5, 6, 129] with themes (calendar_effect, momentum, volume_divergence) ⊂ {momentum, volume_divergence, calendar_effect}; pos 74 NOT in S6. |
| 2C.15 | PASS | 5+2+5+2+3+3 = 20. |

**Exclusion gates**

| # | Verdict | Evidence |
|---|---|---|
| 2C.16 | PASS | `set(positions) ∩ {17,22,27,32,62,72,73,74,77,83,97,102,107,112,117,138,143,147,152,162} == ∅`. |
| 2C.17 | PASS | 116 ∉ positions. |
| 2C.18 | PASS | All 20 positions exist in `replay_candidates.json` with `is_skipped_source: false`. |

**Fresh eligible pool gates**

| # | Verdict | Evidence |
|---|---|---|
| 2C.19 | PASS | 9 ≥ 3. All 9 fresh-9 positions {122, 127, 128, 129, 132, 172, 178, 182, 187} included. |
| 2C.20 | PASS | `fresh_eligible_pool_inclusion_count` = 9; matches actual count of `is_in_fresh_eligible_pool == true` candidates. |
| 2C.21 | PASS | All 9 candidates marked `is_in_fresh_eligible_pool: true` are exactly {122, 127, 128, 129, 132, 172, 178, 182, 187}. |

**Schema gates**

| # | Verdict | Evidence |
|---|---|---|
| 2C.22 | PASS | All 11 top-level fields present: `candidates`, `fresh_eligible_pool_inclusion_count`, `label_universe_analysis_sha256`, `replay_candidates_sha256`, `scope_lock_commit`, `selection_methodology`, `selection_timestamp_utc`, `source_batch_uuid`, `stage`, `strata`, `total_deep_dive_count`. Each stratum has uniform 7-key schema (`fresh_pool_size` is `null` for S3/S6 by design). |
| 2C.23 | PASS | All 20 candidates have the 11 required fields: position, theme, primary_stratum_id, also_fits_strata, is_in_fresh_eligible_pool, universe_a_label, universe_b_label, factor_set_size, factor_set_prior_occurrences, max_overlap_with_priors, selection_rationale. |
| 2C.24 | PASS | Positions strictly ascending: [1, 2, 5, 6, 8, 13, 68, 122, 127, 128, 129, 132, 172, 173, 178, 182, 187, 188, 197, 198]. |
| 2C.25 | PASS | JSON written via `json.dump(..., sort_keys=True, indent=2)` + trailing newline. |

**Invariant gates**

| # | Verdict | Evidence |
|---|---|---|
| 2C.26 | PASS | Builder stdout: "All 21 invariants (C1-C21) PASSED". |

**Determinism gates**

| # | Verdict | Evidence |
|---|---|---|
| 2C.27 | PASS | Two consecutive runs produce byte-identical output excluding `selection_timestamp_utc` (verified via `grep -v selection_timestamp <runs> | diff` empty). |

**Methodology transparency**

| # | Verdict | Evidence |
|---|---|---|
| 2C.28 | PASS | `selection_methodology` (verbatim from JSON) reads: "Sequential greedy assignment in canonical Lock 4.1 stratum order (S1..S6). Each candidate gets exactly one primary stratum (the first eligible in order with an open slot); other qualifying strata are recorded in `also_fits_strata`. Per-stratum ranking: S1 by (is_fresh9 desc, max_overlap desc, pos asc); S2 by pos asc; S3 by pos-197 anchor first then (is_fresh9 desc, max_overlap desc, occurrences desc, pos asc); S4 by pos asc; S5 by (is_fresh9 desc, pos desc); S6 theme-balanced one pick per rare-family theme by (is_fresh9 desc, pos asc). Targets: 5/2/5/2/3/3 = 20. Anti-hindsight: only D6_STAGE2D metadata + signed-off Task 2A/2B labels are consulted; no Stage 2d run data." Explicit deterministic ranking keys per stratum; no randomness; explicit anti-hindsight clause. |
| 2C.29 | PASS | All 20 rationales are unique substantive sentences citing position, stratum, and concrete metadata (e.g., factor_set_size, max_overlap, theme); none are placeholders or boilerplate. After fix, no two share identical text. |

**Reporting gates**

| # | Verdict | Evidence |
|---|---|---|
| 2C.30 | PASS | This document. |
| 2C.31 | PASS | Per-stratum summary table at top of this report. |

## Notes for Codex Stage 2 review

1. **Stratum representativeness:**
   - S1 spans positions 68 → 198 (range 130); spans both early/middle and late zones, not clustered. factor_set_sizes: 6, 5, 6, 6, 5 (mix of 5 and 6); max_overlap values 4–6.
   - S3 spans 122 → 197 (range 75) within 100-200 region; factor_set_sizes 6, 6, 6, 7, 7 (197 is the unique exact-7-factor MR REPEAT, i.e. factor_set_size=7 AND prior_occurrences>=1; 182 also has size=7 but prior_occurrences=0 so it falls under the high-overlap branch).
   - S5 spans 172 → 187 (range 15); all three are fresh-9 late-pos picks. Tighter range is structurally unavoidable since S5's fresh-pool is already constrained by Lock 4.1 to fresh late positions.
   - S6 covers 3 distinct themes (one per pick) at the earliest available position per theme.
2. **Fresh-9 placement:**
   - 122, 127, 132, 182 → S3 (mean_reversion theme matches naturally).
   - 128 → S1 (RSI-absent vol_regime; matches stratum domain naturally).
   - 172, 178, 187 → S5 (late-position; matches stratum domain naturally).
   - 129 → S6 (volume_divergence; only fresh-9 candidate that is rare-family theme).
   - All 9 placed in their natural strata; no count-satisfaction squeezing.
3. **Alternative selection check:**
   - S1 max_count=5 forces full pool consumption from {68, 128, 173, 188, 198} after fresh-9-first sort excludes 3, 43 (which lack fresh-eligible-pool flag). The selection is essentially forced.
   - S3 predicate (literal, from `in_s3` at scripts/build_d7_stage2d_deep_dive.py:288-295): `theme==mean_reversion AND ((factor_set_size==7 AND prior_occurrences>=1) OR max_overlap_with_priors>=5)`. 197 is the unique exact-7-MR-REPEAT anchor specifically called out in the rationale; 122/127/132/182 enter via the high-overlap branch.
   - S4 [1, 2]: earliest two early-position fresh candidates by ascending position. Could have chosen further into [1,50], but Lock 4.1 prefers minimal stratum exposure to allow other strata more headroom.
4. **No-overlap with Stage 2c 20 set:** verified empty intersection.
5. **No pos 116:** verified absent.

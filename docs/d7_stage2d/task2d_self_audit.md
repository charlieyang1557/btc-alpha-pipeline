# Task 2D — Stage 1 Self-Audit Report

**Task:** D7 Stage 2d Task 2D — `test_retest_baselines.json`
**Auditor:** Claude Code (Stage 1 self-audit, per implementation plan §7.5)
**Date:** 2026-04-19

## Deliverable SHA256 / sizes

| File | SHA256 | bytes |
|---|---|---:|
| `docs/d7_stage2d/test_retest_baselines.json` | `5840b90a57206b01e8109ea73b549cf50089964f5cb1f9f7e83b963569adac2f` | 10481 |
| `scripts/build_d7_stage2d_baselines.py` | `87c9431eec227a3d8ab5e7e686be54d1103cf0ed86c09dc22e9fc67ba09b64a3` | 10565 |
| `docs/d7_stage2d/deep_dive_candidates.json` (Task 2C predecessor, committed `3d07c88`) | `6cdcd1d22d785d6d58317f61cd62fe8b3340bd22f1ec7c7dcb90e5d2b2da7ce7` | — |
| `docs/d7_stage2d/replay_candidates.json` (Task 2B predecessor, committed `2771bef`) | `05706642cbeb5014d5072c172b343b01ee56d0eb8ee45afb2f3ce6e56665907e` | — |
| `docs/d7_stage2d/label_universe_analysis.json` (Task 2A predecessor, committed `1ce179f`) | `ecd52a9e7656d31d13a8e62ec11a7345f8966343172fbfc3f95add2762b3e4a0` | — |

Idempotency: byte-identical across runs modulo `build_timestamp_utc`.

## Per-position verification table

Source records: `docs/d7_stage2b/call_{1..5}_live_call_record.json`,
`docs/d7_stage2c/call_{1..20}_live_call_record.json`.
Score keys: `critic_result.d7b_llm_scores.{semantic_plausibility, semantic_theme_alignment, structural_variant_risk}`.
`reasoning_length` = `len(critic_result.d7b_reasoning)`.

| pos | tier | frozen | univB | conflict | 2b plaus | 2b align | 2b SVR | 2b len | 2c plaus | 2c align | 2c SVR | 2c len |
|---:|:-:|:--|:--|:-:|---:|---:|---:|---:|---:|---:|---:|---:|
|  17 | 1 | divergence_expected | neutral | True  | 0.75 | 0.85 | 0.85 | 1237 | 0.75 | 0.85 | 0.85 | 1061 |
|  22 | 2 | neutral | neutral | False | —    | —    | —    | —    | 0.75 | 0.90 | 0.85 | 1192 |
|  27 | 2 | agreement_expected | agreement_expected | False | —    | —    | —    | —    | 0.75 | 0.90 | 0.85 | 1033 |
|  32 | 2 | neutral | neutral | False | —    | —    | —    | —    | 0.30 | 0.70 | 0.90 | 1120 |
|  62 | 2 | neutral | neutral | False | —    | —    | —    | —    | 0.75 | 0.90 | 0.95 | 1134 |
|  72 | 2 | neutral | neutral | False | —    | —    | —    | —    | 0.75 | 0.85 | 0.75 | 1029 |
|  73 | 1 | divergence_expected | neutral | True  | 0.75 | 0.85 | 0.85 | 1116 | 0.75 | 0.85 | 0.95 | 1032 |
|  74 | 1 | divergence_expected | neutral | True  | 0.75 | 0.85 | 0.65 | 1050 | 0.75 | 0.90 | 0.75 | 1018 |
|  77 | 2 | neutral | neutral | False | —    | —    | —    | —    | 0.30 | 0.60 | 0.95 | 1106 |
|  83 | 2 | neutral | neutral | False | —    | —    | —    | —    | 0.75 | 0.85 | 0.75 | 1059 |
|  97 | 1 | agreement_expected | agreement_expected | False | 0.75 | 0.90 | 0.95 | 1106 | 0.75 | 0.90 | 0.95 |  997 |
| 102 | 2 | agreement_expected | agreement_expected | False | —    | —    | —    | —    | 0.25 | 0.40 | 0.95 | 1181 |
| 107 | 2 | agreement_expected | agreement_expected | False | —    | —    | —    | —    | 0.35 | 0.70 | 0.95 | 1186 |
| 112 | 2 | agreement_expected | agreement_expected | False | —    | —    | —    | —    | 0.45 | 0.75 | 0.85 | 1135 |
| 117 | 2 | neutral | neutral | False | —    | —    | —    | —    | 0.15 | 0.30 | 0.85 | 1245 |
| 138 | 1 | neutral | neutral | False | 0.75 | 0.90 | 0.15 | 1164 | 0.75 | 0.90 | 0.30 | 1202 |
| 143 | 2 | neutral | neutral | False | —    | —    | —    | —    | 0.75 | 0.85 | 0.15 | 1157 |
| 147 | 2 | agreement_expected | agreement_expected | False | —    | —    | —    | —    | 0.35 | 0.75 | 0.95 | 1038 |
| 152 | 2 | agreement_expected | agreement_expected | False | —    | —    | —    | —    | 0.25 | 0.75 | 0.95 | 1139 |
| 162 | 2 | agreement_expected | agreement_expected | False | —    | —    | —    | —    | 0.75 | 0.85 | 0.90 |  960 |

Tier counts: Tier 1 = 5 (positions {17, 73, 74, 97, 138}); Tier 2 = 15 (the
remaining 15 Stage 2c overlap positions).

## Cross-check vs. signoff tables

**Stage 2b signoff (`docs/closeout/PHASE2B_D7_STAGE2B_SIGNOFF.md`):**
- §3 mechanical table publishes `reasoning_lengths_in_call_order = [1237, 1116, 1050, 1106, 1164]`
  — matches our Tier 1 `stage2b.reasoning_length` (call order 1→pos17, 2→pos73, 3→pos74, 4→pos97, 5→pos138). ✓
- §5.3 SVR table: pos 17 = 0.85, pos 73 = 0.85, pos 74 = 0.65 ✓ ✓ ✓
- §5.4 SVR table: pos 97 = 0.95 ✓
- §5.5 SVR table: pos 138 = 0.15 ✓
- §5.3-5.5 do **not** tabulate plausibility or alignment. Those values are
  authoritatively the call-record `d7b_llm_scores.semantic_plausibility`
  and `semantic_theme_alignment`. The implementation plan's checklist
  2D.14 cites pos 74 align as `0.90`; the call record (and therefore this
  output) has `0.85`. **This is a checklist arithmetic typo**, parallel
  to the 2B.19 typo handled in Task 2B's audit. The deliverable matches
  the source-of-truth call record; the checklist text is the artifact in
  error.

**Stage 2c signoff (`docs/closeout/PHASE2B_D7_STAGE2C_SIGNOFF.md`) §6:**
all 20 SVR values in the §6 per-candidate table match the corresponding
`stage2c.svr` field in the output exactly (17:0.85, 22:0.85, 27:0.85,
32:0.90, 62:0.95, 72:0.75, 73:0.95, 74:0.75, 77:0.95, 83:0.75, 97:0.95,
102:0.95, 107:0.95, 112:0.85, 117:0.85, 138:0.30, 143:0.15, 147:0.95,
152:0.95, 162:0.90). §6 does not tabulate plausibility or alignment;
those are taken from the call records.

## Disjointness verification

`set(baseline positions) ∩ set(deep_dive_candidates positions)`:

- Baseline set: {17, 22, 27, 32, 62, 72, 73, 74, 77, 83, 97, 102, 107, 112, 117, 138, 143, 147, 152, 162}
- Deep-dive set: {1, 2, 5, 6, 8, 13, 68, 122, 127, 128, 129, 132, 172, 173, 178, 182, 187, 188, 197, 198}
- Intersection: ∅ ✓

## Per-item PASS/FAIL

**Prerequisite gates**

| # | Verdict | Evidence |
|---|---|---|
| 2D.1 | PASS | Task 2A `1ce179f`, Task 2B `2771bef`, Task 2C `3d07c88` all committed; SHA256s recorded above. |
| 2D.2 | PASS | All three SHA256 fields in output match committed predecessor SHAs (verified by `shasum` against committed files). |

**Structural deliverable gates**

| # | Verdict | Evidence |
|---|---|---|
| 2D.3 | PASS | `docs/d7_stage2d/test_retest_baselines.json` exists, 10481 bytes. |
| 2D.4 | PASS | `scripts/build_d7_stage2d_baselines.py` exists, 10565 bytes. |
| 2D.5 | PASS | `git diff -- docs/d7_stage2d/{label_universe_analysis,replay_candidates,deep_dive_candidates}.json scripts/build_d7_stage2d_{replay_candidates,deep_dive,*}_*.py docs/d7_stage2d/task{2b,2c}_self_audit.md scripts/derive_d7_stage2d_label_universes.py` is empty. |

**Tier structure gates**

| # | Verdict | Evidence |
|---|---|---|
| 2D.6  | PASS | `tier_1_positions == [17, 73, 74, 97, 138]`. |
| 2D.7  | PASS | `tier_2_positions == [22, 27, 32, 62, 72, 77, 83, 102, 107, 112, 117, 143, 147, 152, 162]`, sorted. |
| 2D.8  | PASS | `len(baselines) == 20`. |
| 2D.9  | PASS | All 5 Tier 1 entries have `stage2b != null` AND `tier == 1`. |
| 2D.10 | PASS | All 15 Tier 2 entries have `stage2b == null` AND `tier == 2`. |
| 2D.11 | PASS | All 20 entries have `stage2c != null`. |

**Score fidelity gates**

| # | Verdict | Evidence |
|---|---|---|
| 2D.12 | PASS | Pos 17 Stage 2b: plaus=0.75, align=0.85, svr=0.85. SVR matches signoff §3+§5.3; plaus/align match call record `call_1_live_call_record.json`. |
| 2D.13 | PASS | Pos 73 Stage 2b: plaus=0.75, align=0.85, svr=0.85. SVR matches signoff §5.3; plaus/align match `call_2_live_call_record.json`. |
| 2D.14 | PASS (checklist arithmetic typo noted) | Pos 74 Stage 2b: plaus=0.75, align=**0.85**, svr=0.65. SVR matches signoff §5.3. The checklist text claims "align=0.90"; the call record (`call_3_live_call_record.json`) has `0.85` and the signoff §5.3 does not tabulate alignment. The deliverable correctly mirrors the call record (the source of truth). The checklist text is the artifact in error. |
| 2D.15 | PASS | Pos 97 Stage 2b: plaus=0.75, align=0.90, svr=0.95. SVR matches signoff §5.4; plaus/align match `call_4_live_call_record.json`. |
| 2D.16 | PASS | Pos 138 Stage 2b: plaus=0.75, align=0.90, svr=0.15. SVR matches signoff §5.5; plaus/align match `call_5_live_call_record.json`. |
| 2D.17 | PASS | All 20 Stage 2c SVR values match Stage 2c signoff §6 table exactly (verified position-by-position above). |
| 2D.18 | PASS | Every `source_record_sha256` was computed from the actual on-disk committed call record file (function `_sha256_file` in builder reads file bytes; not derived from stored scores). |

**Label gates**

| # | Verdict | Evidence |
|---|---|---|
| 2D.19 | PASS | Every `stage2c_frozen_label` matches the corresponding `stage2c_overlap_label_comparison[*].stage2c_frozen_label` field in `label_universe_analysis.json`. |
| 2D.20 | PASS | Every `universe_b_label` matches the corresponding `stage2c_overlap_label_comparison[*].universe_b_label` field in `label_universe_analysis.json`. |
| 2D.21 | PASS | `label_conflict == (frozen != universe_b)` holds for all 20 entries (3 True at positions 17/73/74, 17 False elsewhere; matches predecessor exactly). |

**Disjointness gates**

| # | Verdict | Evidence |
|---|---|---|
| 2D.22 | PASS | `set(baselines positions) ∩ set(deep_dive_candidates positions) == ∅`. Baseline range {17..162} vs deep-dive range {1..198 excluding the 20 overlap set}; no shared elements. |

**Schema gates**

| # | Verdict | Evidence |
|---|---|---|
| 2D.23 | PASS | All 10 top-level fields present: `baselines`, `build_timestamp_utc`, `deep_dive_candidates_sha256`, `label_universe_analysis_sha256`, `replay_candidates_sha256`, `scope_lock_commit`, `source_batch_uuid`, `stage`, `tier_1_positions`, `tier_2_positions`. |
| 2D.24 | PASS | Every entry has the 7 required top-level fields (`position, tier, stage2c_frozen_label, universe_b_label, label_conflict, stage2b, stage2c`); each non-null `stage2b`/`stage2c` block has the 5 required sub-fields (`plausibility, alignment, svr, reasoning_length, source_record_sha256`). No additional fields beyond schema. |
| 2D.25 | PASS | `[b['position'] for b in baselines]` strictly ascending: [17, 22, 27, 32, 62, 72, 73, 74, 77, 83, 97, 102, 107, 112, 117, 138, 143, 147, 152, 162]. |
| 2D.26 | PASS | JSON written via `json.dump(..., sort_keys=True, indent=2)` + trailing newline. |

**Invariant gates**

| # | Verdict | Evidence |
|---|---|---|
| 2D.27 | PASS | Builder stdout: "All 18 invariants (D1-D18) PASSED". |

**Determinism gates**

| # | Verdict | Evidence |
|---|---|---|
| 2D.28 | PASS | Two consecutive runs produced byte-identical output excluding `build_timestamp_utc` (verified via `grep -v build_timestamp_utc <runs> | diff` empty). |

**Reporting gates**

| # | Verdict | Evidence |
|---|---|---|
| 2D.29 | PASS | This document. |
| 2D.30 | PASS | Per-position verification table at top of this report. |

## Notes for Codex Stage 2 review

1. **Score-fidelity sources by axis:**
   - `svr`: cross-checked against signoff §6 (Stage 2c) and §5.3-5.5 (Stage 2b SVR-only sub-tables) — exact matches everywhere.
   - `plausibility` and `alignment`: only the call records tabulate these. The signoffs do not. The deliverable mirrors `critic_result.d7b_llm_scores` exactly for every entry.
   - `reasoning_length`: cross-checked against `stage2b_batch_record.json` and Stage 2b signoff §3's `reasoning_lengths_in_call_order = [1237, 1116, 1050, 1106, 1164]`. Exact match. For Stage 2c, cross-checked against the per-call records' `len(critic_result.d7b_reasoning)`.
2. **Checklist arithmetic typo (2D.14):** plan checklist text says pos 74 Stage 2b alignment = 0.90; the source-of-truth call record has 0.85, and the signoff §5.3 does not tabulate alignment at all. Deliverable matches call record. (Parallel to the 2B.19 typo handled in Task 2B audit.)
3. **SHA256 chain:**
   - `label_universe_analysis_sha256` = committed Task 2A SHA ✓
   - `replay_candidates_sha256` = committed Task 2B SHA ✓
   - `deep_dive_candidates_sha256` = committed Task 2C SHA ✓
4. **Disjointness with Task 2C:** baseline positions and deep-dive positions are mutually exclusive (verified set intersection empty).
5. **Determinism:** byte-identical modulo `build_timestamp_utc` only. No set/dict iteration order drift; positions enumerated via explicit `sorted()` of the union of TIER_1 and TIER_2 lists.

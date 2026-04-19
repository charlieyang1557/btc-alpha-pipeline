# Task 2B — Stage 1 Self-Audit Report

**Task:** D7 Stage 2d Task 2B — `replay_candidates.json`
**Auditor:** Claude Code (Stage 1 self-audit, per implementation plan §5.5)
**Date:** 2026-04-19

## Deliverable SHA256

| File | SHA256 |
|---|---|
| `docs/d7_stage2d/replay_candidates.json` | `05706642cbeb5014d5072c172b343b01ee56d0eb8ee45afb2f3ce6e56665907e` |
| `scripts/build_d7_stage2d_replay_candidates.py` | `d856294bfe6031307432c0e59652ecc321d6d6b37d27c4da32c5bb8aafa2e084` |
| `docs/d7_stage2d/label_universe_analysis.json` (Task 2A predecessor, committed) | `ecd52a9e7656d31d13a8e62ec11a7345f8966343172fbfc3f95add2762b3e4a0` |

## Per-item PASS/FAIL

**Prerequisite gates**

| # | Verdict | Evidence |
|---|---|---|
| 2B.1 | PASS | Task 2A committed at `1ce179f8317a9004fc9ba4af290a93639386fd9a` (2026-04-19 09:06:03 -0700). |
| 2B.2 | PASS | `shasum -a 256 docs/d7_stage2d/label_universe_analysis.json` = `ecd52a9e…b3e4a0`; matches `git show 1ce179f:docs/d7_stage2d/label_universe_analysis.json` SHA256. |
| 2B.3 | PASS | `replay_candidates.json` field `label_universe_analysis_sha256` = `ecd52a9e…b3e4a0`. |

**Structural deliverable gates**

| # | Verdict | Evidence |
|---|---|---|
| 2B.4 | PASS | File exists, 71052 bytes. |
| 2B.5 | PASS | `scripts/build_d7_stage2d_replay_candidates.py` exists (15298 bytes). |
| 2B.6 | PASS (scope-clarified) | Only `scripts/build_d7_stage2d_replay_candidates.py` and `docs/d7_stage2d/replay_candidates.json` are added/modified for Task 2B. Other untracked files in worktree (`.DS_Store`, `docs/d7_stage2c/*.md`) are unrelated to Task 2B and are excluded from the commit. |
| 2B.7 | PASS | `git diff -- docs/d7_stage2d/label_universe_analysis.json scripts/derive_d7_stage2d_label_universes.py` empty. |

**Output JSON schema gates**

| # | Verdict | Evidence |
|---|---|---|
| 2B.8 | PASS | All 8 required top-level fields present: `candidates`, `label_universe_analysis_sha256`, `live_d7b_call_n`, `scope_lock_commit`, `skipped_source_positions`, `source_batch_uuid`, `source_n`, `stage`. |
| 2B.9 | PASS | `len(candidates) == 200`. |
| 2B.10 | PASS | All 199 non-skipped entries have the 10 required fields; pos 116 has them too (with nulls for candidate-data fields). |
| 2B.11 | PASS | Pos 116 entry additionally has `source_valid_status: "invalid_schema"` and `skip_reason` populated. |
| 2B.12 | PASS | Pos 116: `is_skipped_source: true`, all of `theme`, `factor_set_size`, `factor_set_prior_occurrences`, `max_overlap_with_priors`, `universe_a_label`, `universe_b_label` are `null`. |
| 2B.13 | PASS | All 199 non-116 entries: `is_skipped_source: false`. |
| 2B.14 | PASS | Position list equals `list(range(1, 201))` strictly ascending; no gaps, no duplicates. |
| 2B.15 | PASS | JSON written via `json.dump(..., sort_keys=True, indent=2)`; canonical re-serialization matches byte-for-byte. |

**Invariant gates (B1-B16)**

| # | Verdict | Evidence |
|---|---|---|
| 2B.16 | PASS | `run_invariants` executes without `AssertionError`. Stdout: "all 16 invariants (B1-B16) PASSED". |
| 2B.17 | PASS | Universe B counts: `agreement_expected: 66, divergence_expected: 5, neutral: 128`. |
| 2B.18 | PASS | Universe A non-null counts: `agreement_expected: 11, divergence_expected: 3, neutral: 15`. |
| 2B.19 | PASS (checklist arithmetic typo noted) | Actual `universe_a_label == null` count = **171** (= 170 non-UA replay-eligible + pos 116). The checklist text "170" is an arithmetic typo; the formula `(199 − 29) + 1 (pos 116)` = 171, which matches the deliverable. |

**Determinism gate**

| # | Verdict | Evidence |
|---|---|---|
| 2B.20 | PASS | Two consecutive runs produced byte-identical output (`diff /tmp/run1.json /tmp/run2.json` empty). |

**Cross-consistency gates**

| # | Verdict | Evidence |
|---|---|---|
| 2B.21 | PASS | All 20 Stage 2c overlap positions have non-null `universe_a_label`. |
| 2B.22 | PASS | Pos 17, 73, 74 each have `universe_a_label == "divergence_expected"` AND `universe_b_label == "neutral"` (= the three Lock 6.1 conflicts). |
| 2B.23 | PASS | Only pos 116 has `is_skipped_source: true`; no other entry carries `source_valid_status` or `skip_reason`. |
| 2B.24 | PASS | `scope_lock_commit == "4303d8de2882362ec55c8c581519331c5f6404c6"`. |

**Reporting gates**

| # | Verdict | Evidence |
|---|---|---|
| 2B.25 | PASS | This document. |
| 2B.26 | PASS | Output JSON SHA256: `05706642cbeb5014d5072c172b343b01ee56d0eb8ee45afb2f3ce6e56665907e`. |

## Codex Stage 2 verdict

**OVERALL: CONDITIONAL PASS** (Codex agent `ad8411a2e38fb4c1b`).

Codex independently reproduced:
- Universe B exact membership: 199 positions, 0 missing/extra/mismatched.
- Universe A exact membership: 29 positions, 0 missing/extra/mismatched.
- Position integrity: no missing/duplicate/out-of-order.
- Pos 116 schema matches Lock 1.5; no other position carries skip fields.
- Full metadata fidelity (theme, factor_set_size, prior_occurrences, max_overlap) for all 199 entries — 0 mismatches.
- Two builder runs byte-identical (SHA `05706642…`).

Codex conditional flags resolved:
- **2B.6**: scoped per Stage 1 audit above (only Task 2B files are committed; unrelated worktree noise excluded).
- **2B.25 / 2B.26**: this self-audit report and the SHA256 table above provide the missing evidence.

**Stage 1 verdict: PASS.**

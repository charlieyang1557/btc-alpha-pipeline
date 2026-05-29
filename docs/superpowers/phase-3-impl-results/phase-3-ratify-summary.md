# B-C-narrow Phase 3 — Ratify Summary (re-fire executed; data-recovery COMPLETE)

**Date:** 2026-05-29
**Plan:** [docs/superpowers/plans/2026-05-27-b-c-narrow-phase-3-fire-plan.md](../plans/2026-05-27-b-c-narrow-phase-3-fire-plan.md) (v9.1 SEALED; corrected §V9.4 sequence executed)
**Charlie registers consumed:** #N+19a′ (re-fire) + #N+19b′ (T14b canonical mv) + #N+19c′ (this ratify acknowledgment — pending)

## Outcome — data recovery COMPLETE + zero-regression GREEN

The B-C-narrow Phase 3 fire-plan executed cleanly through the corrected §V9.4 re-fire sequence. The data recovery (R6.1 V_SEAL §10 binding precondition) is complete:

- **39 cohort_a candidates** re-run against the forward_2026 window: **20 holdout_passed / 19 holdout_failed / 0 holdout_error** (deterministic — identical aggregate across both fire attempts).
- **Recovered:** per-bar return series (39 `returns_per_bar.parquet`) + per-candidate **γ3/γ4 moments** + `T_obs` + **registry linkage** (1 parent `batch_summary` + 39 child `regime_holdout` rows at `run_id=phase4_forward_2026_15bps_v1_b_c_narrow`).
- **V4 reproducibility gate: 12/12 GREEN** — ε=1e-6 per-candidate metric diff + total_trades exact + per-bar parquet integrity + γ3/γ4 round-trip + G6 registry parent-child + G7 archive idempotency/cross-FS. The recovered cohort reproduces the original within ε=1e-6.
- **Relocated full-suite zero-regression gate (Step 14b.2.8): 2372 passed, 2 xfailed, 0 failed, 0 errors.**

## Provenance / original preservation (Q2=a + Q1=a + Option A)

- The pre-recovery **original is preserved in two places**: git history (commit `7c8f4a7`) AND a committed archive snapshot at `data/phase2c_evaluation_gate/archive/phase4_forward_2026_15bps_v1_d0b8101/` (commit `6d4bb7f`; **byte-identical to `7c8f4a7`**, confirmed).
- The **recovered canonical** is git-tracked (commit `ff0c576`) per Q2=a.
- `test_t1_4_backward_compat.py` A3/A4/A5 byte-identity **rescoped** (Q1=a + Option A) to verify the archived original vs `7c8f4a7` (git-vs-on-disk-archive, no commit-SHA placeholder). A1/A6/A2 unchanged (validate the recovered canonical's evaluation-semantics — pass).

## Sealed-plan defects resolved (the re-fire patch)

| Gap | Resolution |
|---|---|
| **Gap 1** — canonical dir is git-tracked (not gitignored as v8 assumed); fire deletes/mutates 41 tracked files + breaks t1_4 byte-identity | Q2=a commits recovered canonical + archive; Q1=a + Option A rescopes A3/A4/A5 to the archive |
| **Gap 2** — V4 file's +12 tests break t1_4 pc9 baseline gate | pc9 `BASELINE` 2236 → 2248 |
| **Gap 2b** — Step 13.3 ran V4 in isolation → missed Gap 2 | full-suite RED-verify added at Step 13.3 (pre-fire, canonical present) |
| §V9.6 collection-crash | no full-suite while canonical absent; zero-regression gate relocated to Step 14b.2.8 (post-mv) |

## Full re-fire arc provenance

1. **v8 fire executed** → Step 14.5 full-suite gate surfaced the 3 defects above.
2. **Reverted** to green SEAL `b96d3a8` (Option A): canonical restored, 40 registry rows deleted, Task-13 RED commit reverted (`bccbc47`).
3. **v9 re-fire errata** (`cb59a55`) → **B2 re-review** (Codex + advisor, both APPROVE-WITH-FINDINGS / SOUND) → **v9.1 polish** (`0025afd`; 3 doc-precision ADOPT + Codex-V2 hallucination PUSHBACK) → **Rule-2 SEAL-eve CLEAR** → **re-SEAL** (`38e1291`).
4. **Re-fire** (corrected §V9.4): RED `5e77e63` → T13 fire → V4 gate 12/12 → fixture `9cabc9b` → mv → archive commit `6d4bb7f` → t1_4 rescope + canonical commit `ff0c576` → full-suite gate **2372 GREEN**.

## Re-fire commit chain

| Step | Commit | Contents |
|---|---|---|
| 13.4 RED | `5e77e63` | V4 test file (12 methods) + pc9 BASELINE 2236→2248 |
| 14.6 fixture | `9cabc9b` | `tests/fixtures/b_c_narrow_archived_baseline.json` (N=2) |
| 14b.1.5 archive | `6d4bb7f` | archive snapshot (41 files, byte-identical to `7c8f4a7`) |
| 14b.2.7 canonical | `ff0c576` | recovered canonical (41 modified + 39 new parquet) + t1_4 A3/A4/A5 Option-A rescope |

## Next

- **#N+19c′** — Charlie ratify acknowledgment of this packet (per CM6: this Task-14c commit ALWAYS executes as documentation; #N+19c′ is the post-commit ack, not a gate on the commit).
- **Phase 4** (B-C-narrow cycle SEAL bundle + Phase Marker advance) — SEPARATE register-event (#N+20) per anti-pre-emption discipline; NOT bundled here.
- The cycle's downstream consumer — **R6.1 Tier 6 evaluation application** — is now unblocked: per-bar return series + γ3/γ4 moments + registry linkage for the `phase4_forward_2026_15bps_v1` cohort_a are recovered, V4-verified, and committed.

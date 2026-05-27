# B-C-narrow Phase 1 ratify packet

**Date:** 2026-05-27T16:14:46Z
**HEAD commit:** b8d6523 (plan v3-Phase1 v3 SEAL; code-state equivalent to f112599 — no code changes between)
**Plan version:** v3-Phase1 v3 (sealed at commit `b8d6523`)
**Plan path:** `docs/superpowers/plans/2026-05-27-b-c-narrow-phase-1-pre-impl-gates-plan.md`
**Spec path:** `docs/superpowers/specs/2026-05-26-b-c-narrow-data-recovery-design.md` (sealed at `d6c7fc0`)
**Authorization:** Charlie register `EXEC-SUBAGENT-ALL-PHASE-1` 2026-05-27

## Pre-execution preconditions

| Precondition | Spec ref | Result | Evidence |
|---|---|---|---|
| Clean working tree (PFR R1 LOW NEW-2 fix v2 + PFR R2 HIGH-2/NEW-2 fix v3) | plan §"Phase 1 execution preconditions" | PASS (with NOTE) | `git status --porcelain backtest/ tests/ config/ scripts/ strategies/ factors/` returned only one untracked artifact: `backtest/engine.py,cover` (a coverage tool annotation file from May 22, untracked, NOT a modified-tracked-file). Filtering with `grep -v '^??'` returns no output → zero modified tracked files in the code dirs that affect Phase 1 gate semantics. |
| Writable execution environment (PFR R1 LOW F6 fix v2) | plan §"Phase 1 execution preconditions" | PASS | `python -c "import tempfile; ..."` printed `writable: /var/folders/.../tmp4ga6e6cz` successfully. |

NOTE on the untracked `engine.py,cover` artifact: the precondition's purpose per PFR R2 HIGH-2 fix v3 is to detect "unstaged modifications" to tracked code that would silently affect Phase 1 results while claims reference HEAD `f112599`. A `.cover` companion file (annotation produced by `coverage` tool) is not imported by `g2-validate.py` and not a Python module under any Phase 1 gate; it cannot affect gate results. Reported here for transparency.

Additional verification: `git log --oneline f112599..HEAD -- backtest/ tests/ config/ scripts/ strategies/ factors/` returned empty — zero code changes between Phase 0 SEAL (`f112599`) and current HEAD (`b8d6523`). The 3 commits since `f112599` are all plan documents (`e583e78`, `b1a183f`, `b8d6523`) under `docs/superpowers/plans/`. Therefore, all V4 reproducibility claims referencing HEAD `f112599` remain accurate at HEAD `b8d6523`.

## Gate results

| Gate | Spec ref | Result | Evidence |
|---|---|---|---|
| G1 — Engine-diff audit | §4.1 G1 | **PASS** | `g1-engine-diff-audit.md`: all 3 spec-original-range commits (`ec647dc`, `12dffde`, `44840a3`) classified NON-NUMERICAL-PATH (DOC/TEST-ONLY + API/OPTIONAL-ADDITIVE/BIT-EXACT-PRESERVING + REGISTRY/LINEAGE-ONLY respectively); Phase 0 commits (`8f64712`, `bedc9b4`, `f112599`) pre-classified API/OPTIONAL-ADDITIVE per PFR R1 H1 fix v2 with SEAL evidence. |
| G2 — StrategyDSL backward-compat | §4.1 G2 | **PASS** | `g2-dsl-backward-compat-sample.json`: 39/39 cohort_a candidates validate cleanly via `StrategyDSL.model_validate()` at HEAD `b8d6523`. n_total=39, n_pass=39, n_fail=0, pass_rate=1.0. Step 6.4 OPTIONAL compile-only spot-check SKIPPED per plan guidance — `git log --since=2026-05-08 strategies/dsl.py strategies/dsl_compiler.py factors/registry.py` returned EMPTY (no schema-drift potential since cohort_a fire date). |
| G3 — Raw_payloads inventory | §4.1 G3 | **PASS** | `g3-raw-payloads-inventory.md`: 998 total symlinks (993 attempt_* + 5 source_stage2d_summary_*.json) all resolve; zero broken; zero off-repo / absolute-text. 5 sub-batches each have 200 calls (1000 total; 993 realized as response files). |
| G3.5 — Engine extension smoke | §4.1 G3.5 | **PASS (pre-satisfied)** | Phase 0 SEAL commits `8f64712` (dataclass +equity_curve field) + `f112599` (body populates equity_curve from BacktestResult). Re-ran the 2 smoke tests `test_regime_holdout_result_dataclass_exact_field_set` + `test_run_regime_holdout_returns_result_with_equity_curve_populated` → `2 passed in 0.63s`. |

## Overall verdict

**ALL 4 gates PASS** → Phase 1 ratify gate met.

V4 ε=1e-6 expected achievable at §4.2 post-impl gate (downstream of Phase 2 producer TDD + Phase 3 fire).

Phase 2 producer-TDD sub-plan drafting is a SEPARATE register-event (#N+2) per anti-pre-emption discipline; do NOT bundle into #N+1.

## Next register-event (#N+1) — Phase 1 ratify ONLY

Per PFR R1 F3 fix v2: register-event #N+1 is Phase 1 ratify acknowledgment ONLY. The Phase 2 drafting authorization is a SEPARATE register-event #N+2 (described in plan §"DEFER items"). Do NOT auto-bundle.

- Phase 1 ratify acknowledgment (and per-gate adjudication if any FAIL — none in this run)
- Push decision for Phase 1 evidence artifacts commit

Phase 2 sub-plan drafting authorization is NOT a sub-option of #N+1; it requires its own register-event #N+2 (see plan §"DEFER items").

## Evidence artifact inventory

| Path | Type | Purpose |
|---|---|---|
| `docs/superpowers/phase-1-gate-results/g1-engine-diff-audit.md` | Markdown | G1 commit classification + 4-category framework + Phase 0 pre-classification |
| `docs/superpowers/phase-1-gate-results/g2-validate.py` | Python script | G2 ephemeral validation script (committed for audit trail) |
| `docs/superpowers/phase-1-gate-results/g2-dsl-backward-compat-sample.json` | JSON | G2 per-attempt validation results (39 entries) |
| `docs/superpowers/phase-1-gate-results/g3-raw-payloads-inventory.md` | Markdown | G3 symlink inventory + resolution + confinement check |
| `docs/superpowers/phase-1-gate-results/phase-1-ratify-summary.md` | Markdown | This file — comprehensive Phase 1 ratify packet |

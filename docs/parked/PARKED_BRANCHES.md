# Parked Branches Registry

This file tracks branches containing (or designated to contain) completed work that is intentionally NOT YET merged to `main`. Each entry includes activation trigger condition + pre-merge verification requirements.

## Active parked branches

### `phase2.5/bandit-dedup`

- **Base**: `main` HEAD at the registration commit (= Path 3 methodology consolidation scoping cycle SEAL register-event boundary + this parked-branch registration)
- **Designated contents**: factor bandit (Track A) + semantic dedup (Track B) — full scoping decision + sub-spec + implementation + arc-level closeout artifacts per the combined Option-1 Path-3-style cycle authorized at Charlie register-event boundary on 2026-05-16
- **Status at registration**: scoping cycle entry authorized; session-1 draft pending
- **Activation trigger condition**: any future Charlie register-event boundary establishing active batch cadence resumption — e.g., a "Phase 2D AI loop activation" cycle, a "Phase 2.5 pre-batch infrastructure" cycle, or any explicit Charlie-authorized batch arc that will exercise factor bandit between-batch learning and/or semantic dedup near-duplicate filtering
- **Owner**: Charlie register
- **Created**: 2026-05-16
- **Rationale for parking**: per Concern 1 (orchestrator surface reopening) in the combined scoping plan — Phase 2C arc just closed careful evaluation gate sequence on the current orchestrator + ingest pipeline; physical branch isolation prevents in-flight methodology consolidation (Path 3 / Phase 5.1) from drifting against an actively-modified orchestrator surface

## Pre-merge verification checklist

Before merging any parked branch above to `main`:

1. **Rebase clean**: branch rebases cleanly onto current main; if conflicts touch sealed code paths, sealed-path modification requires separate Charlie register-event authorization (independent of the merge authorization)
2. **Test suite green**: full `python -m pytest -q` passes on the merged HEAD (not just on the branch in isolation)
3. **WF lineage guards intact**: corrected-engine consumption discipline still triggers correctly per [`docs/decisions/WF_TEST_BOUNDARY_SEMANTICS.md`](../decisions/WF_TEST_BOUNDARY_SEMANTICS.md) Section RS
4. **No HARD CONSTRAINT violations**: diff against current main CLAUDE.md HARD CONSTRAINTS reveals no new violations; bandit + dedup discipline locks proposed in the scoping decision must be present in CLAUDE.md HARD CONSTRAINTS after merge
5. **Re-run code review**: python-reviewer + security-reviewer + code-reviewer fired against the merged-state diff
6. **Re-run substantive review**: ChatGPT structural + Claude advisor full-prose dual-reviewer routing on substantive code per [`feedback_codex_review_scope.md`](../../.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_codex_review_scope.md) precedent
7. **Re-run adversarial review**: `codex:codex-rescue` adversarial pass on the merged state
8. **Reproducibility check**: prior Phase 2C artifact consumption (PHASE2C_6, PHASE2C_7.1, PHASE2C_8.1 evaluation runs) still works under the merged HEAD; corrected-engine artifacts at `_corrected/` remain canonical
9. **Charlie register-event authorization** for the merge fire (separate from any prior implementation authorization)
10. **Atomic Phase Marker advance** on merge commit per [`feedback_claude_md_freshness.md`](../../.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_claude_md_freshness.md): CLAUDE.md Phase Marker + `docs/phase_marker_history.md` updated atomically with the merge

## How to add a new parked-branch entry

Open this file. Add a new `### <branch-name>` section under "Active parked branches" using the same field schema (Base / Designated contents / Status / Activation trigger / Owner / Created / Rationale). Reference this registry file from CLAUDE.md if you haven't already.

When a branch is merged (or abandoned), move its entry to a new "## Archived parked branches" section at the bottom with the merge/abandon commit SHA + date.

# D7 Stage 2d — Implementation Plan (v2)

**Document purpose:** Master implementation plan for producing the four
pre-fire artifacts required by D7 Stage 2d scope lock v2. Covers Tasks
2A through 2D in sequential order, with embedded Claude Code prompts,
task-level sign-off checklists, and the two-stage per-task review gate
plus final advisor acceptance.

**Version history:**
- **v1** (superseded): Three-stage per-task gate (Claude Code →
  Codex → Advisor per task). Required advisor stop-and-review between
  every task.
- **v2** (current): Two-stage per-task gate (Claude Code → Codex per
  task) plus ONE final advisor acceptance verdict after all four tasks
  are committed. Reduces round-trip overhead; advisor effort
  concentrated on cross-task integrity. Workflow change requested by
  Charlie on 2026-04-19 after Task 2A successful completion.

**Scope lock anchor:**
- Commit: `4303d8de2882362ec55c8c581519331c5f6404c6`
- Timestamp: `2026-04-19T15:46:43Z`
- SHA256: `b119067ca4ed3dd3ce8a6ee5c29d62f319187160197e5bf0ab1399beece68f7a`
- Path: `docs/d7_stage2d/D7_STAGE2D_SCOPE_LOCK_v2.md`

All Stage 2d artifacts must commit AFTER this anchor timestamp.

**Author:** Charlie Yang (with advisor scaffolding)
**Authority:** Supersedes no prior document. Operates under scope lock v2.

---

## 1. Overview

### 1.1 Implementation phase objective

Produce four committed pre-fire artifacts in strict order:

```
Task 2A  →  Task 2B  →  Task 2C  →  Task 2D  →  [Implementation phase complete]
```

Then enter Expectations Authoring phase (advisor-scaffolded, separate document).

### 1.2 Commit ordering contract

Per Lock 11.5, the four artifacts commit in this exact order:

```
(scope lock v2, already committed)
  <
label_universe_analysis.json commit        ← Task 2A
  <=
replay_candidates.json commit              ← Task 2B
  <=
deep_dive_candidates.json commit           ← Task 2C
  <=
test_retest_baselines.json commit          ← Task 2D
  <
expectations commit                        ← later phase
  <
live fire start                            ← later phase
```

The scope lock allows Tasks 2B/2C/2D commits to share a timestamp
(`<=`), but the **task execution** is strictly sequential: each task
must pass its per-task two-stage review gate (Claude Code self-audit
+ Codex review) before the next task begins.

### 1.3 Task dependency graph

```
Task 2A (label_universe_analysis.json)
   │
   ├──→ Task 2B (replay_candidates.json)
   │      (needs: non_call_positions from 2A)
   │
   ├──→ Task 2C (deep_dive_candidates.json)
   │      (needs: universe_a candidate_positions from 2A;
   │              fresh_eligible_pool_positions from 2A;
   │              stage2c_overlap_label_comparison from 2A)
   │
   └──→ Task 2D (test_retest_baselines.json)
          (needs: stage2c_overlap_label_comparison from 2A for cross-check)
```

All three downstream tasks consume Task 2A output. Therefore Task 2A
is the absolute critical path start.

### 1.4 Explicit non-goals for the implementation phase

The implementation phase does NOT include:
- Writing `scripts/run_d7_stage2d_batch.py` (Task 2E, separate phase)
- Writing `stage2d_expectations.md` (Expectations Authoring phase)
- Writing `stage2d_self_check.py` (Expectations Authoring phase)
- Firing D7b
- Any LLM call
- Any modification to Stage 2a/2b/2c or D6 artifacts
- Any modification to `scripts/select_replay_candidate.py`

---

## 2. The Review Gate Workflow

### 2.1 Workflow overview

Stage 2d implementation uses a **two-stage per-task review gate** for
each of Tasks 2A-2D, followed by a **single final advisor acceptance
verdict** after all four tasks are committed.

```
For each task 2A..2D (sequential):
  Stage 1: Claude Code self-audit
    ↓ PASS
  Stage 2: Codex second-pass review
    ↓ PASS (possibly after round-1 FAIL → fix → round-2 PASS iteration)
  Charlie commits
    ↓
  Next task begins

After ALL four tasks committed:
  FINAL STAGE: Advisor acceptance verdict
    ↓ ACCEPTED
  Expectations Authoring Phase begins
```

### 2.2 Stage 1 — Claude Code self-audit (per task)

**Who:** Claude Code (the task-executing agent)
**Input:** Task-level sign-off checklist (embedded in each task's prompt)
**Output:** Self-audit report covering every checklist item:
- Item number and title
- PASS / FAIL
- Supporting evidence (file path, command output, invariant result,
  diff result, etc.) — concrete, not narrative

**Gating rule:** If ANY checklist item is FAIL or UNVERIFIED, Claude
Code must fix the deliverable in the same session and re-run the
self-audit. Do NOT proceed to Stage 2 with any known FAIL.

### 2.3 Stage 2 — Codex second-pass review (per task)

**Who:** Codex (independent reviewer; NOT the agent that produced the
deliverable)
**Input:**
- All deliverable files from Claude Code
- Claude Code's Stage 1 self-audit report
- The task-level sign-off checklist (for independent re-verification)
- Read-only access to the scope lock v2 and Stage 2c signoff for
  cross-reference

**Mandate:** Codex must independently verify EVERY sign-off checklist
item, plus look for:
- Logic errors Claude Code's self-audit might have missed
- Spec deviations from scope lock v2
- Edge cases not covered by the checklist but material to correctness
- Semantic issues (e.g., label derivation drift, hardcoded value
  mismatches, set-algebra errors)
- Non-determinism sources

**Output:** Codex review report with per-item verdicts AND a final
overall verdict:
- OVERALL: PASS → Charlie commits; proceed to next task
- OVERALL: FAIL → loop back to Claude Code with specific fix items
- OVERALL: CONDITIONAL PASS → Charlie evaluates the conditions; if
  accepted, commit; if not, loop back

**Gating rule:** Only OVERALL: PASS (or CONDITIONAL PASS that Charlie
accepts) unlocks the commit and the start of the next task.

### 2.4 Important clarification on prompt-vs-scope-lock authority

Task 2A Codex round 1 FAILed by incorrectly flagging
**prompt-explicit schema requirements** as **scope-lock violations**.
Specifically, Codex flagged:
- `sort_keys=True` (prompt requirement; scope lock is silent)
- `non_call_position_details` field (prompt schema; scope lock prose
  description less specific)
- `conflict` vs `conflict_bool` field naming (prompt says `conflict`;
  scope lock prose says `conflict_bool`)

All three were resolved in round 2 under this rule:

> **Authority rule:** Scope lock v2 prose schema blocks (e.g., Lock
> 11.2, Lock 4, Lock 6) are **structural descriptions**, not
> **literal field-by-field contracts**. The **task prompt schema is
> authoritative** for fields, types, and naming. When the prompt is
> more specific than the scope lock, the prompt wins.

This rule applies to Tasks 2B, 2C, and 2D as well. If Codex flags
similar prompt-vs-scope-lock naming/field issues on those tasks,
Charlie can invoke Task 2A's precedent to resolve without re-scoping.

Scope lock overrides the prompt ONLY in cases of semantic/scientific
conflict (e.g., a prompt that contradicts a Lock 5 carry-forward
constraint; a prompt that changes Universe A/B counts). Naming and
schema ordering are prompt-authoritative.

### 2.5 Final Advisor Acceptance Verdict (ONCE, after all four tasks)

**Who:** Advisor (me)
**Triggered:** After Tasks 2A, 2B, 2C, 2D have all been committed via
the per-task Stage 1 + Stage 2 gate.

**Input (full package):**
- All four deliverable JSON files (full content)
- All associated build/derivation scripts (full content)
- All four commit hashes, timestamps, and file SHA256s
- All Stage 1 self-audit reports (per task)
- All Stage 2 Codex review reports (per task, including any round-1
  FAIL → round-2 PASS iteration history)

**Mandate:** Cross-task integrity audit. Advisor verifies:

**(a) SHA256 chain integrity**
- Task 2B's `label_universe_analysis_sha256` matches committed 2A
- Task 2C's `label_universe_analysis_sha256` and
  `replay_candidates_sha256` match committed 2A and 2B
- Task 2D's three predecessor SHA256s all match committed 2A, 2B, 2C
- No file was modified between being referenced and being committed

**(b) Scientific counts consistency**
- Universe A (11/3/15) present in 2A and reflected in 2B universe_a_label fields
- Universe B (66/5/128) present in 2A and reflected in 2B universe_b_label fields
- Stage 2c overlap set (20 positions) appears identically in 2A
  overlap_comparison, 2B candidates (as non-null universe_a_label),
  and 2D baselines
- Deep-dive 20 (2C) and Overlap 20 (2D) are strictly disjoint
- Fresh-eligible-pool 9 positions match across 2A and any
  fresh-included 2C candidates

**(c) Label conflict fidelity**
- Positions 17, 73, 74 flagged `conflict: true` in 2A
  overlap_comparison
- Same positions have `label_conflict: true` in 2D baselines
- Universe B labels for 17/73/74 are "neutral" in both 2A and 2D

**(d) Stage 2b/2c score fidelity**
- Task 2D Tier 1 (5 positions) scores match Stage 2b signoff §5.3-5.5
- Task 2D all 20 positions Stage 2c scores match Stage 2c signoff §6
- `source_record_sha256` fields in 2D correspond to actual committed
  Stage 2b/2c call records

**(e) Review quality audit**
- Codex reviews are substantive (concrete findings, not
  rubber-stamp); at least one FAIL→PASS iteration or substantive
  verification trace per task is healthy
- No task shows Codex skipping items
- Round-1 FAIL items were actually addressed, not hand-waved

**(f) Scope lock v2 fidelity**
- All 6 carry-forward constraints from Stage 2c signoff §9 are
  respected in the artifacts
- Lock 1.5 (pos 116 schema) matches 2B deliverable exactly
- Lock 4 strata match 2C stratum definitions
- Lock 6.1 Universe A/B mixing rule respected throughout
- Lock 11.5 commit ordering satisfied

**(g) Ready-to-proceed check**
- All four artifacts committed with correct ordering
- Implementation Log (Section 8) fully populated
- No blocking ambiguities for Expectations Authoring Phase

**Output:** Advisor verdict — one of:
- **✅ FULL ACCEPTED** → proceed to Expectations Authoring Phase
- **⚠️ CONDITIONAL ACCEPTED** → minor fixes required, but does not
  invalidate commits; fix in place, no task re-runs needed
- **❌ REJECTED at task X** → cross-task integrity failure; specific
  task (or tasks) must be re-run; identifies which SHA256/count/field
  failed and how to fix

### 2.6 Loop-back discipline

Within per-task Stage 1 + Stage 2:
- Invariant failure, logic error, missing field → Claude Code
  (Stage 1 restart)
- Review blind spot, incomplete checklist coverage → Codex
  (Stage 2 restart with updated mandate)
- Scope-level ambiguity discovered during review → Advisor resolution
  via clarification or scope lock v2.1 patch before continuing

Between tasks:
- If a downstream task (e.g., 2C) discovers a defect in an upstream
  task (e.g., 2A), halt the downstream task, fix upstream, re-commit
  upstream, then resume. Upstream commit hashes change; downstream
  SHA256 references must be updated.

At final advisor acceptance:
- CONDITIONAL ACCEPTED fixes are applied in-place without task re-run
- REJECTED at task X requires that task to be re-executed through
  Stage 1 + Stage 2 again; subsequent tasks' SHA256 references may
  need updating

---

## 3. Hashes and commit anchoring

After each per-task Stage 1 + Stage 2 review passes and Charlie
commits, record the following in the Implementation Log (Section 8):

- Commit hash (full 40-char SHA1)
- Commit UTC timestamp
- File SHA256(s) for every deliverable
- Codex verdict trace (round 1 FAIL reasons if any; round N PASS)
- Stage 1 self-audit checksum (all items PASS)

Every subsequent task must verify that its predecessor's commit hash
and SHA256 are unchanged before starting. The Final Advisor
Acceptance gate (after all four tasks commit) uses these recorded
hashes to verify the SHA256 chain integrity across tasks.

---

## 4. Task 2A — Label Universe Derivation

### 4.1 Objective

Produce the deterministic label-universe derivation script and its
committed output JSON. This establishes the Stage 2d scientific
ground truth for all aggregate and axis-specific claims.

### 4.2 Deliverables

1. `scripts/derive_d7_stage2d_label_universes.py`
2. `docs/d7_stage2d/label_universe_analysis.json`

### 4.3 Claude Code prompt — Task 2A

```
You are implementing Task 2A of the D7 Stage 2d implementation phase
for the BTC Alpha Pipeline project. This task produces the first of
four pre-fire artifacts required by the signed-off scope lock.

═══════════════════════════════════════════════════════════════════
AUTHORITY AND CONTEXT
═══════════════════════════════════════════════════════════════════

Scope lock (authoritative contract, READ BEFORE CODING):
  File:    docs/d7_stage2d/D7_STAGE2D_SCOPE_LOCK_v2.md
  Commit:  4303d8de2882362ec55c8c581519331c5f6404c6
  SHA256:  b119067ca4ed3dd3ce8a6ee5c29d62f319187160197e5bf0ab1399beece68f7a

Read this entire file first. Pay special attention to:
  - Lock 1 (source counts, position 116 treatment)
  - Lock 6.1 (Universe A vs Universe B definitions)
  - Lock 11.2 (derivation script spec)
  - Lock 11.5 (commit ordering)

This task is Task 2A. Tasks 2B, 2C, 2D, 2E follow in order and all
depend on this artifact. Do NOT start any other Stage 2d task in
this session.

═══════════════════════════════════════════════════════════════════
DELIVERABLES
═══════════════════════════════════════════════════════════════════

Produce exactly two new files:

  1. scripts/derive_d7_stage2d_label_universes.py
  2. docs/d7_stage2d/label_universe_analysis.json

Do NOT commit these files. Charlie commits manually after all three
review stages pass. Create the docs/d7_stage2d/ directory if it does
not exist.

═══════════════════════════════════════════════════════════════════
HARD CONSTRAINTS
═══════════════════════════════════════════════════════════════════

1. READ-ONLY ACCESS to all existing source-of-truth files:
   - raw_payloads/batch_5cf76668-47d1-48d7-bd90-db06d31982ed/
   - docs/d7_stage2b/, docs/d7_stage2c/
   - docs/closeout/PHASE2B_D7_STAGE2{A,B,C}_SIGNOFF.md
   - scripts/select_replay_candidate.py and the agents/critic/ module
   The script must not modify, rename, delete, or rewrite any of
   these. Read and import only.

2. DO NOT overload scripts/select_replay_candidate.py. Do NOT add
   a --full-batch flag to it. That script's Stage 2b/2c semantics
   are frozen. If you need its label derivation logic, import the
   underlying functions or re-implement them in the new script
   with a clear docstring pointer back to the original.

3. DO NOT fire any LLM, do NOT call D7b, do NOT call D6 proposer,
   do NOT trigger any backtest. This is a pure-analysis read-only
   script.

4. DETERMINISTIC AND IDEMPOTENT. Running the script twice must
   produce byte-identical output JSON, excluding the single
   `derivation_timestamp_utc` field. No set ordering drift. No
   floating-point non-determinism. Sort all position lists
   ascending. Sort all dict keys in the output JSON
   (json.dumps(..., sort_keys=True, indent=2)).

5. Script takes NO runtime arguments. It is fully parameterized by
   the committed batch artifacts.

═══════════════════════════════════════════════════════════════════
OUTPUT JSON SCHEMA (EXACT)
═══════════════════════════════════════════════════════════════════

docs/d7_stage2d/label_universe_analysis.json must conform exactly:

{
  "source_batch_uuid": "5cf76668-47d1-48d7-bd90-db06d31982ed",
  "derivation_script_commit": "<git rev-parse HEAD at script run time>",
  "derivation_timestamp_utc": "<ISO 8601, e.g. 2026-04-19T16:00:00.000000Z>",

  "source_n": 200,
  "replay_eligible_n": 199,
  "non_call_positions": [116],
  "non_call_position_details": [
    {
      "position": 116,
      "lifecycle_state": "rejected_complexity",
      "valid_status": "invalid_schema"
    }
  ],

  "universe_a": {
    "definition": "Stage 2b/2c selector eligibility pool, following the exact filters implemented in scripts/select_replay_candidate.py.",
    "size": 29,
    "counts": {
      "agreement_expected": 11,
      "divergence_expected": 3,
      "neutral": 15
    },
    "candidate_positions": {
      "agreement_expected": [<sorted ints, length 11>],
      "divergence_expected": [<sorted ints, length 3>],
      "neutral":             [<sorted ints, length 15>]
    }
  },

  "universe_b": {
    "definition": "Full replay-eligible pending-backtest population: all positions 1..200 with lifecycle_state == pending_backtest, equivalent to the set {1..200} minus {116}.",
    "size": 199,
    "counts": {
      "agreement_expected": 66,
      "divergence_expected": 5,
      "neutral": 128
    },
    "candidate_positions": {
      "agreement_expected": [<sorted ints, length 66>],
      "divergence_expected": [<sorted ints, length 5>],
      "neutral":             [<sorted ints, length 128>]
    }
  },

  "stage2c_overlap_label_comparison": [
    {
      "position": <int>,
      "stage2c_frozen_label": "<agreement_expected|divergence_expected|neutral>",
      "universe_b_label":     "<agreement_expected|divergence_expected|neutral>",
      "conflict": <bool>
    },
    ... exactly 20 entries, sorted by position ascending
  ],

  "fresh_eligible_pool_positions": [122, 127, 128, 129, 132, 172, 178, 182, 187]
}

The Stage 2c 20 positions are:
  [17, 22, 27, 32, 62, 72, 73, 74, 77, 83,
   97, 102, 107, 112, 117, 138, 143, 147, 152, 162]

═══════════════════════════════════════════════════════════════════
INTERNAL INVARIANT ASSERTIONS (the script MUST check before writing)
═══════════════════════════════════════════════════════════════════

The script asserts every one of these before writing output. Any
failure raises a clean error, does not write partial output, and
exits non-zero.

  A1.  source_n == 200
  A2.  len(non_call_positions) == 1 and non_call_positions == [116]
  A3.  replay_eligible_n == 199
  A4.  replay_eligible_n + len(non_call_positions) == source_n

  A5.  universe_a.size == 29
  A6.  sum(universe_a.counts.values()) == universe_a.size == 29
  A7.  Concatenated candidate_positions under universe_a
       (across all three label groups) form a set of exactly 29
       distinct positions.
  A8.  Universe A position set is a subset of Universe B position
       set (every eligible-pool candidate must also be replay-
       eligible).
  A9.  Position 116 does NOT appear in universe_a.candidate_positions.

  A10. universe_b.size == 199
  A11. sum(universe_b.counts.values()) == universe_b.size == 199
  A12. Concatenated candidate_positions under universe_b form a
       set of exactly 199 distinct positions.
  A13. Universe B position set == {1..200} minus {116}.
  A14. Position 116 does NOT appear in universe_b.candidate_positions.

  A15. len(stage2c_overlap_label_comparison) == 20
  A16. The 20 positions listed equal the Stage 2c 20 positions set.
  A17. Every entry's stage2c_frozen_label is one of the three valid
       labels.
  A18. Every entry's conflict boolean equals
       (stage2c_frozen_label != universe_b_label).

  A19. fresh_eligible_pool_positions ==
       sorted(set(universe_a all positions) - set(Stage 2c 20 positions))
  A20. fresh_eligible_pool_positions ==
       [122, 127, 128, 129, 132, 172, 178, 182, 187]
       (expected hardcoded outcome — raise AssertionError if
        inspection differs; do not silently "fix")

  A21. All 20 Stage 2c positions appear in universe_a (combined across
       all labels).
  A22. All position lists are sorted ascending.

If any assertion fails, raise an AssertionError with a precise
message naming which invariant and what the observed vs expected
values are. Do not write output on failure.

═══════════════════════════════════════════════════════════════════
LABEL DERIVATION SEMANTICS (critical — get this exactly right)
═══════════════════════════════════════════════════════════════════

UNIVERSE A:
  Use the Stage 2b/2c selector's exact eligibility filter and
  exact label derivation. Do not reinterpret. Reuse the functions
  from scripts/select_replay_candidate.py or the agents/critic/
  selector module. If the derivation is entangled with selection
  ordering, extract just the eligibility + label parts without
  altering them. Document your reuse strategy in the script's
  module docstring.

UNIVERSE B:
  Apply the same label-relationship rule used by the selector
  (label = function of max_overlap_with_priors and
  factor_set_prior_occurrences computed against the prior position
  history at that position), but over all 199 replay-eligible
  positions, WITHOUT the Stage 2b/2c selector's eligibility
  filters (which restrict to specific replay-suitability
  conditions).

  Two consequences of this unfiltered application must be
  documented in the script docstring:

    (a) Some Stage 2c overlap positions may receive a different
        label in Universe B than under the frozen Stage 2c
        selection. Specifically: positions 17, 73, 74 are expected
        to emerge as neutral in Universe B while they are
        divergence_expected in Stage 2c. This is not a bug; it is
        the central conceptual distinction that Lock 6.1 codifies.
        The stage2c_overlap_label_comparison field exposes these
        conflicts.

    (b) The count triple (66, 5, 128) is expected from batch
        inspection. If the actually-computed Universe B counts
        differ, that is a material finding — the script must
        raise an AssertionError with a clear message, NOT silently
        overwrite the hardcoded expectation. In that case stop and
        flag to Charlie for review.

═══════════════════════════════════════════════════════════════════
SCRIPT STRUCTURE GUIDANCE
═══════════════════════════════════════════════════════════════════

  - Module docstring: state purpose, cite Lock 11.2, list invariants
  - Top of file: typed constants for expected counts and expected
    fresh_eligible_pool (hardcoded per batch inspection)
  - Pure functions:
      load_batch_summary()
      derive_universe_a()
      derive_universe_b()
      build_stage2c_overlap_comparison()
      compute_fresh_eligible_pool()
      run_invariants(result_dict)
  - main():
      1. read batch summary
      2. derive Universe A, Universe B
      3. build stage2c overlap comparison
      4. compute fresh eligible pool
      5. run all invariants
      6. write JSON (sort_keys=True, indent=2)
      7. print summary to stdout:
         - source_n, replay_eligible_n, non_call_positions
         - universe_a.counts
         - universe_b.counts
         - count of conflicts in stage2c_overlap_label_comparison
         - fresh_eligible_pool_positions
      8. exit 0

═══════════════════════════════════════════════════════════════════
IDEMPOTENCY TEST (MUST RUN BEFORE SELF-AUDIT PASSES)
═══════════════════════════════════════════════════════════════════

Before considering the task complete, run the script twice:

  python scripts/derive_d7_stage2d_label_universes.py
  cp docs/d7_stage2d/label_universe_analysis.json /tmp/run1.json
  python scripts/derive_d7_stage2d_label_universes.py
  cp docs/d7_stage2d/label_universe_analysis.json /tmp/run2.json

Diff them excluding the derivation_timestamp_utc line. They MUST
be byte-identical except for that one field:

  diff <(jq 'del(.derivation_timestamp_utc)' /tmp/run1.json) \
       <(jq 'del(.derivation_timestamp_utc)' /tmp/run2.json)

This diff MUST return empty output. If it does not, fix the source
of non-determinism (e.g. set iteration order, dict iteration order)
before considering the task complete.

═══════════════════════════════════════════════════════════════════
SELF-AUDIT (STAGE 1) — CLAUDE CODE MUST COMPLETE BEFORE REPORTING
═══════════════════════════════════════════════════════════════════

After producing the two deliverable files and running the
idempotency test, produce a self-audit report verifying EVERY item
in the Task 2A Sign-Off Checklist (below in the implementation plan
document, section 4.4). Format: numbered list, each item PASS or
FAIL with concrete evidence (file path, command output, line number,
etc.). If ANY item is FAIL, fix and re-run the entire self-audit.
Do not claim PASS on any item without actually verifying it.

═══════════════════════════════════════════════════════════════════
REPORTING BACK TO CHARLIE (SIX-ITEM PACKAGE)
═══════════════════════════════════════════════════════════════════

After self-audit passes, provide Charlie with the complete six-item
acceptance package:

  1. Full contents of docs/d7_stage2d/label_universe_analysis.json
  2. Full contents of scripts/derive_d7_stage2d_label_universes.py
  3. stdout summary from the script run
  4. Output of the idempotency test (diff command result)
  5. Complete Stage 1 self-audit report with PASS/FAIL per item
  6. A brief note on how Universe A label derivation was sourced
     (imported from existing module vs re-implemented, which
     function calls specifically, what module they live in)

Do NOT commit any files. Charlie commits manually after all three
review stages pass.

═══════════════════════════════════════════════════════════════════
OUT OF SCOPE FOR THIS TASK
═══════════════════════════════════════════════════════════════════

Do NOT in this session:
  - Start Task 2B (replay_candidates.json)
  - Start Task 2C (deep_dive_candidates.json)
  - Start Task 2D (test_retest_baselines.json)
  - Write the Stage 2d fire script (Task 2E)
  - Write expectations.md or any self-check script
  - Modify any Stage 2b, 2c, or D6 artifact
  - Commit the output (Charlie commits after review)
  - Modify scripts/select_replay_candidate.py

Stay within the two deliverable files and read-only access to
existing sources.

═══════════════════════════════════════════════════════════════════
FINAL REMINDER
═══════════════════════════════════════════════════════════════════

The Stage 2d scope lock is the authoritative contract. If any
requirement in this prompt conflicts with the scope lock, the
scope lock wins and you should surface the conflict for resolution.
If any observed count during derivation differs from the
expectations encoded above (29 eligibility; 11/3/15 for Universe A;
199 replay-eligible; 66/5/128 for Universe B; 9 fresh-eligible at
positions 122/127/128/129/132/172/178/182/187), stop and report —
do not silently proceed.

Produce a clean, minimal, deterministic implementation. Quality
over verbosity. Good luck.
```

### 4.4 Task 2A Sign-Off Checklist

Used by Claude Code (Stage 1 self-audit) AND Codex (Stage 2 review)
AND Advisor (Stage 3).

**Structural deliverable gates:**

- [ ] **2A.1** — `scripts/derive_d7_stage2d_label_universes.py` exists
- [ ] **2A.2** — `docs/d7_stage2d/label_universe_analysis.json` exists
- [ ] **2A.3** — `docs/d7_stage2d/` directory was created if previously absent
- [ ] **2A.4** — No files modified outside `scripts/` and `docs/d7_stage2d/`
- [ ] **2A.5** — `scripts/select_replay_candidate.py` was NOT modified (git diff clean)
- [ ] **2A.6** — No LLM or backtest call was made

**Output JSON schema gates:**

- [ ] **2A.7** — `source_batch_uuid == "5cf76668-47d1-48d7-bd90-db06d31982ed"`
- [ ] **2A.8** — `derivation_script_commit` populated (valid 40-char git hash)
- [ ] **2A.9** — `derivation_timestamp_utc` populated (ISO 8601)
- [ ] **2A.10** — Top-level field set is exactly the 8 required fields, no extras
- [ ] **2A.11** — `universe_a` has exactly `definition`, `size`, `counts`, `candidate_positions`
- [ ] **2A.12** — `universe_b` has exactly `definition`, `size`, `counts`, `candidate_positions`
- [ ] **2A.13** — `stage2c_overlap_label_comparison` has exactly 20 entries
- [ ] **2A.14** — Each overlap entry has exactly `position`, `stage2c_frozen_label`, `universe_b_label`, `conflict`
- [ ] **2A.15** — All position lists are sorted ascending
- [ ] **2A.16** — JSON is `sort_keys=True, indent=2`

**Invariant gates (A1-A22 from prompt):**

- [ ] **2A.17** — All 22 script-internal invariants (A1-A22) PASS
- [ ] **2A.18** — Invariant A20 specifically verified: `fresh_eligible_pool_positions == [122, 127, 128, 129, 132, 172, 178, 182, 187]`
- [ ] **2A.19** — Universe A / Universe B counts match hardcoded expectations (29 = 11+3+15; 199 = 66+5+128)
- [ ] **2A.20** — Stage 2c 20 overlap positions all appear in Universe A
- [ ] **2A.21** — Positions 17, 73, 74 confirmed as `conflict: true` in overlap comparison (Stage 2c divergence_expected → Universe B neutral expected)
- [ ] **2A.22** — Position 116 does NOT appear in any candidate_positions list under either universe

**Determinism gates:**

- [ ] **2A.23** — Idempotency test executed (two runs, diff excluding timestamp)
- [ ] **2A.24** — Idempotency diff returned empty output
- [ ] **2A.25** — No set-iteration or dict-iteration non-determinism in source code (sorted() applied everywhere set/dict order matters)

**Label derivation gates:**

- [ ] **2A.26** — Universe A derivation reuses frozen Stage 2b/2c selector logic (either imports or faithfully re-implements with documented reference)
- [ ] **2A.27** — Module docstring documents Universe A derivation source explicitly (which file, which functions)
- [ ] **2A.28** — Module docstring documents Universe B unfiltered-label derivation choice
- [ ] **2A.29** — Module docstring documents that 17/73/74 label conflicts are expected, not a bug

**Reporting gates:**

- [ ] **2A.30** — Stage 1 self-audit report produced with PASS/FAIL per item
- [ ] **2A.31** — Six-item acceptance package produced (JSON content, script content, stdout, diff result, self-audit report, derivation-source note)

### 4.5 Task 2A Stage 2 (Codex) Review Mandate

Codex must independently verify every item in the Task 2A Sign-Off
Checklist (4.4 above), AND additionally look for:

**Independent count recomputation:**
- Codex reads the batch summary independently (not by running the
  script) and recomputes the Universe B label counts using only the
  scope lock's label-derivation rule. Counts must match 66/5/128.

**Label-derivation faithfulness:**
- Codex reads `scripts/select_replay_candidate.py` and confirms that
  the new script's Universe A logic does not drift in semantics —
  same filters, same comparison rule, same tiebreaker.

**Edge case inspection:**
- Position 1 (zero prior history) — does the label derivation handle
  the empty-prior case cleanly?
- Position 200 (maximum prior history) — no off-by-one
- Positions immediately adjacent to 116 (positions 115, 117) — no
  data corruption or boundary drift

**Set-algebra verification:**
- `fresh_eligible_pool_positions == set(universe_a_all) - set(stage2c_20)`
  — Codex computes both sides independently and diffs

**Non-determinism audit:**
- Walk the script looking for any iteration over unordered containers
  (dict, set) without explicit sort. Flag any such occurrence.
- Confirm `json.dumps(sort_keys=True)` or equivalent is used

**Scope-lock-drift audit:**
- Cross-check every schema field name against Lock 11.2 spec
- Confirm no extra fields that could mislead downstream consumers

Codex produces:
- Per-item PASS/FAIL against the full sign-off checklist
- Any additional findings
- OVERALL verdict: PASS / CONDITIONAL PASS / FAIL

### 4.6 Task 2A Commit and Log

Task 2A is **COMPLETE** as of 2026-04-19 (see Implementation Log,
Section 8.1). It was executed under v1 three-stage gate (Claude Code
self-audit + Codex + advisor per-task). Completion evidence:

- Codex round 1: FAIL (sort_keys / non_call_position_details /
  conflict field naming — all clarified as prompt-authoritative per
  Section 2.4)
- Codex round 2: PASS after clarification
- Charlie committed: `scripts/derive_d7_stage2d_label_universes.py`
  + `docs/d7_stage2d/label_universe_analysis.json` (2 files, 943
  insertions)
- Observed Universe A: 11 / 3 / 15 (matches hardcoded expectation)
- Observed Universe B: 66 / 5 / 128 (matches hardcoded expectation)
- Fresh pool: `[122, 127, 128, 129, 132, 172, 178, 182, 187]`
  (matches Lock 4.3 expectation)
- Stage 2c overlap conflicts: 3 at positions 17/73/74
  (divergence_expected → neutral under Universe B, per Lock 6.1)
- Idempotency diff: empty
- All 22 internal invariants asserted pre-write

Under v2 workflow (Section 2), per-task advisor review was
retroactively dropped; the advisor final-acceptance verdict (Section
2.5) will cover Task 2A integrity as part of the cross-task audit
after Tasks 2B-2D are committed.

**For future reference, the Task 2A commit template used was:**

```
git add scripts/derive_d7_stage2d_label_universes.py
git add docs/d7_stage2d/label_universe_analysis.json
git commit -m "D7 Stage 2d Task 2A: label universe derivation

- New script scripts/derive_d7_stage2d_label_universes.py
- Committed docs/d7_stage2d/label_universe_analysis.json
- Universe A (eligible pool, 29) and Universe B (replay-eligible, 199)
- Stage 2c overlap label comparison with 17/73/74 conflicts flagged
- Fresh eligible pool positions [122,127,128,129,132,172,178,182,187]
- All 22 script invariants pass; idempotency verified
- Two-stage per-task gate: Claude Code self-audit, Codex review"
```

Record commit hash and SHA256s in Section 8.1 below.

---

## 5. Task 2B — Replay Candidates JSON

### 5.1 Objective

Produce the fire-script-consumed `replay_candidates.json`, enumerating
all 200 source positions with correct skipped-source flagging for
position 116.

### 5.2 Deliverable

- `docs/d7_stage2d/replay_candidates.json`

### 5.3 Prerequisite

Task 2A must be ACCEPTED (Stage 3) and committed. Claude Code must
verify the Task 2A commit hash and `label_universe_analysis.json`
SHA256 are unchanged before starting Task 2B.

### 5.4 Claude Code prompt — Task 2B

```
You are implementing Task 2B of the D7 Stage 2d implementation phase.
Task 2A must already be committed. If it is not committed, stop and
inform Charlie.

═══════════════════════════════════════════════════════════════════
AUTHORITY AND PREREQUISITES
═══════════════════════════════════════════════════════════════════

Scope lock:
  File:    docs/d7_stage2d/D7_STAGE2D_SCOPE_LOCK_v2.md
  Commit:  4303d8de2882362ec55c8c581519331c5f6404c6

Task 2A prerequisite:
  File:    docs/d7_stage2d/label_universe_analysis.json
  (Must be committed; verify git log shows its commit.)
  (Read-only input for this task.)

Verify BEFORE starting this task:
  git log --format="%H %ci %s" -n 1 docs/d7_stage2d/label_universe_analysis.json

If the file has no commit, HALT. Task 2B cannot begin without a
committed Task 2A output.

═══════════════════════════════════════════════════════════════════
OBJECTIVE
═══════════════════════════════════════════════════════════════════

Produce docs/d7_stage2d/replay_candidates.json. This is the file the
Stage 2d fire script will consume at runtime (Task 2E). It must
enumerate every one of the 200 D6_STAGE2D source positions in
firing-order ascending, with the pos 116 skipped-source flag
correctly set.

═══════════════════════════════════════════════════════════════════
DELIVERABLE
═══════════════════════════════════════════════════════════════════

A single file:
  docs/d7_stage2d/replay_candidates.json

Do NOT commit. Charlie commits after Claude Code self-audit PASS
and Codex Stage 2 PASS (per v2 workflow).

═══════════════════════════════════════════════════════════════════
HARD CONSTRAINTS
═══════════════════════════════════════════════════════════════════

1. READ-ONLY ACCESS to:
   - raw_payloads/batch_5cf76668-47d1-48d7-bd90-db06d31982ed/
   - docs/d7_stage2d/label_universe_analysis.json (committed Task 2A
     output)

2. Read-only import access to:
   - scripts/select_replay_candidate.py (for consistent candidate
     metadata derivation; do not modify)
   - agents/critic/ module (for BatchContext reconstruction helper
     if needed)

3. DO NOT fire any LLM. Pure read-only analysis and JSON construction.

4. DETERMINISTIC. Re-running this task must produce byte-identical
   output (this task has no timestamp field; full byte-identity is
   required).

5. Candidate entries sorted by position ascending, 1 through 200, no
   gaps, no duplicates, position 116 present with skip flag.

═══════════════════════════════════════════════════════════════════
OUTPUT JSON SCHEMA (EXACT)
═══════════════════════════════════════════════════════════════════

{
  "source_batch_uuid": "5cf76668-47d1-48d7-bd90-db06d31982ed",
  "stage": "d7_stage2d",
  "scope_lock_commit": "4303d8de2882362ec55c8c581519331c5f6404c6",
  "label_universe_analysis_sha256": "<SHA256 of committed Task 2A JSON>",
  "source_n": 200,
  "live_d7b_call_n": 199,
  "skipped_source_positions": [116],
  "candidates": [
    {
      "position": 1,
      "firing_order": 1,
      "is_skipped_source": false,
      "lifecycle_state": "pending_backtest",
      "theme": "<from D6_STAGE2D summary>",
      "factor_set_size": <int>,
      "factor_set_prior_occurrences": <int>,
      "max_overlap_with_priors": <int>,
      "universe_a_label": "<agreement_expected|divergence_expected|neutral|null if not in Universe A>",
      "universe_b_label": "<agreement_expected|divergence_expected|neutral>"
    },
    ... entries 2 through 115 with analogous schema ...
    {
      "position": 116,
      "firing_order": 116,
      "is_skipped_source": true,
      "lifecycle_state": "rejected_complexity",
      "source_valid_status": "invalid_schema",
      "theme": null,
      "factor_set_size": null,
      "factor_set_prior_occurrences": null,
      "max_overlap_with_priors": null,
      "universe_a_label": null,
      "universe_b_label": null,
      "skip_reason": "source candidate is not pending_backtest and cannot be replayed by BatchContext reconstruction"
    },
    ... entries 117 through 200 with normal schema ...
  ]
}

═══════════════════════════════════════════════════════════════════
INTERNAL INVARIANT ASSERTIONS
═══════════════════════════════════════════════════════════════════

  B1.  len(candidates) == 200
  B2.  [c.position for c in candidates] == list(range(1, 201))
  B3.  [c.firing_order for c in candidates] == list(range(1, 201))
       (i.e., firing_order == position for this task)
  B4.  Exactly one candidate has is_skipped_source == true
  B5.  That candidate's position == 116
  B6.  All other 199 candidates have is_skipped_source == false
  B7.  All 199 non-skipped candidates have lifecycle_state ==
       "pending_backtest"
  B8.  The pos-116 candidate has lifecycle_state ==
       "rejected_complexity" and source_valid_status ==
       "invalid_schema"
  B9.  Universe B labels across all 199 replay-eligible candidates
       match the label distribution in
       label_universe_analysis.json (66 agreement, 5 divergence,
       128 neutral)
  B10. Universe A labels: exactly 29 non-null entries, matching
       Universe A counts in label_universe_analysis.json
  B11. Universe A label set among non-null entries ==
       {11 agreement, 3 divergence, 15 neutral}
  B12. scope_lock_commit == "4303d8de2882362ec55c8c581519331c5f6404c6"
  B13. label_universe_analysis_sha256 matches actual SHA256 of
       committed label_universe_analysis.json
  B14. source_batch_uuid matches batch directory name
  B15. source_n == 200, live_d7b_call_n == 199,
       skipped_source_positions == [116]
  B16. JSON is sort_keys=True, indent=2

Any assertion failure: raise AssertionError, do not write output,
exit non-zero.

═══════════════════════════════════════════════════════════════════
IMPLEMENTATION APPROACH
═══════════════════════════════════════════════════════════════════

Suggestion:
  1. Add a small utility script if helpful, but the primary output
     is the JSON. You may use a one-shot builder script placed under
     scripts/, or you may generate the JSON directly. If you write a
     builder script, commit it too; it falls under deliverables for
     audit.
  2. Read D6_STAGE2D batch summary.
  3. Read committed label_universe_analysis.json.
  4. For each position 1..200:
     - If position == 116: build skipped-source entry per schema.
     - Else: read candidate metadata from batch summary; attach
       Universe A label (or null if not in eligible pool); attach
       Universe B label.
  5. Run all invariants B1-B16.
  6. Write JSON.

If you choose to add a builder script, name it
scripts/build_d7_stage2d_replay_candidates.json.py or similar, and
include it in deliverables.

═══════════════════════════════════════════════════════════════════
SELF-AUDIT (STAGE 1)
═══════════════════════════════════════════════════════════════════

After producing the deliverable, verify EVERY item in the Task 2B
Sign-Off Checklist (implementation plan, section 5.5). PASS/FAIL per
item with concrete evidence.

═══════════════════════════════════════════════════════════════════
REPORTING BACK TO CHARLIE
═══════════════════════════════════════════════════════════════════

Provide:
  1. Full contents of docs/d7_stage2d/replay_candidates.json
     (this will be a large file; consider providing full contents
     plus a truncated preview if size is an issue)
  2. Full contents of any builder script you wrote
  3. stdout summary (count by Universe B label, presence of pos 116
     skip, etc.)
  4. Complete Stage 1 self-audit report with PASS/FAIL per item
  5. SHA256 of the output JSON
  6. Confirmation that label_universe_analysis_sha256 was computed
     from the committed Task 2A file, not from a local uncommitted
     version

═══════════════════════════════════════════════════════════════════
OUT OF SCOPE
═══════════════════════════════════════════════════════════════════

Do NOT:
  - Start Task 2C
  - Write the fire script
  - Write expectations.md
  - Modify Task 2A outputs
  - Modify Stage 2b/2c artifacts
  - Commit

Good luck.
```

### 5.5 Task 2B Sign-Off Checklist

**Prerequisite verification:**

- [ ] **2B.1** — Task 2A was ACCEPTED and committed before this task started
- [ ] **2B.2** — `label_universe_analysis.json` SHA256 matches the committed version
- [ ] **2B.3** — `label_universe_analysis_sha256` field in output correctly reflects the committed Task 2A SHA256

**Structural deliverable gates:**

- [ ] **2B.4** — `docs/d7_stage2d/replay_candidates.json` exists
- [ ] **2B.5** — If a builder script was written, it lives under `scripts/` and is included in deliverables
- [ ] **2B.6** — No files modified outside `scripts/` and `docs/d7_stage2d/`
- [ ] **2B.7** — Task 2A outputs were not modified

**Output JSON schema gates:**

- [ ] **2B.8** — All 6 top-level fields present (`source_batch_uuid`, `stage`, `scope_lock_commit`, `label_universe_analysis_sha256`, `source_n`, `live_d7b_call_n`, `skipped_source_positions`, `candidates`)
- [ ] **2B.9** — `candidates` has exactly 200 entries
- [ ] **2B.10** — Every entry has `position`, `firing_order`, `is_skipped_source`, `lifecycle_state`, `theme`, `factor_set_size`, `factor_set_prior_occurrences`, `max_overlap_with_priors`, `universe_a_label`, `universe_b_label`
- [ ] **2B.11** — Pos 116 entry additionally has `source_valid_status` and `skip_reason` fields
- [ ] **2B.12** — Pos 116 entry has `is_skipped_source: true`, all candidate-data fields `null`
- [ ] **2B.13** — All 199 non-116 entries have `is_skipped_source: false`
- [ ] **2B.14** — Positions array equals `list(range(1, 201))` strictly (no gaps, no duplicates, ascending)
- [ ] **2B.15** — JSON is `sort_keys=True, indent=2`

**Invariant gates (B1-B16 from prompt):**

- [ ] **2B.16** — All 16 script-internal invariants (B1-B16) PASS
- [ ] **2B.17** — Universe B label totals across the 199 replay-eligible entries: 66 agreement, 5 divergence, 128 neutral
- [ ] **2B.18** — Universe A label totals across the 29 non-null entries: 11 agreement, 3 divergence, 15 neutral
- [ ] **2B.19** — 171 entries have `universe_a_label == null` (= 199 replay-eligible minus 29 Universe A, plus pos 116)

**Determinism gate:**

- [ ] **2B.20** — Output is byte-identical across two independent runs (full byte-identity, no timestamp field)

**Cross-consistency gates:**

- [ ] **2B.21** — Every Stage 2c 20 position has a non-null `universe_a_label` in the output
- [ ] **2B.22** — Pos 17, 73, 74 have `universe_a_label == "divergence_expected"`
- [ ] **2B.23** — Pos 116 is the ONLY position with `is_skipped_source: true`
- [ ] **2B.24** — `scope_lock_commit` field matches the v2 commit hash

**Reporting gates:**

- [ ] **2B.25** — Stage 1 self-audit report produced with PASS/FAIL per item
- [ ] **2B.26** — SHA256 of output JSON reported

### 5.6 Task 2B Stage 2 (Codex) Review Mandate

Beyond the checklist, Codex must:

**Cross-reference Task 2A:**
- Independently recompute `label_universe_analysis_sha256` from the
  committed Task 2A file and verify it matches the output field
- Verify every candidate's `universe_b_label` matches the label
  assigned in Task 2A's `candidate_positions` structure

**Position sequence:**
- Confirm no missing positions (exactly 1 through 200)
- Confirm no out-of-order positions
- Confirm no duplicate positions

**Pos 116 isolation:**
- Confirm pos 116's schema is exactly per Lock 1.5 of scope lock
- Confirm NO other position carries any skip-related field
- Confirm pos 116 is excluded from all count aggregates

**Theme and metadata fidelity:**
- Spot-check 5-10 candidates against D6_STAGE2D batch summary to
  confirm theme / factor_set_size / prior_occurrences are not
  drifted or corrupted

### 5.7 Task 2B Commit Instructions

Under v2 workflow, Task 2B commits after Codex Stage 2 PASS. Charlie
evaluates any CONDITIONAL PASS conditions at his discretion. No
per-task advisor gate; the final advisor acceptance verdict (Section
2.5) will audit Task 2B integrity as part of the cross-task review
after all four tasks are committed.

**Key integrity checks Codex must confirm before PASS:**
- Task 2A `label_universe_analysis.json` SHA256 matches the field in
  Task 2B output
- Every candidate's `universe_b_label` matches Task 2A's
  `candidate_positions` assignments
- Pos 116 schema is exactly per Lock 1.5
- All 200 positions present, firing-order ascending, no gaps, no
  duplicates

**Commit template (Codex PASS):**

```
git add docs/d7_stage2d/replay_candidates.json
(if builder script exists:)
git add scripts/build_d7_stage2d_replay_candidates.py
git commit -m "D7 Stage 2d Task 2B: replay candidates JSON

- 200 candidate entries, firing-order ascending
- Position 116 flagged is_skipped_source=true with full skip schema
- Universe A (29) and Universe B (199) labels attached per Task 2A
- Cross-references committed label_universe_analysis.json by SHA256
- Two-stage per-task gate: Claude Code self-audit, Codex review"
```

Record commit hash and SHA256s in Section 8.2 below. Proceed to
Task 2C.

---

## 6. Task 2C — Deep-Dive Candidates JSON

### 6.1 Objective

Select 20 stratified deep-dive candidates per scope lock Lock 4.1,
excluding the 20 Stage 2c candidates and pos 116, with at least 3 of
9 fresh eligible-pool candidates included.

### 6.2 Deliverable

- `docs/d7_stage2d/deep_dive_candidates.json`

### 6.3 Prerequisites

Tasks 2A AND 2B must be ACCEPTED and committed.

### 6.4 Claude Code prompt — Task 2C

```
You are implementing Task 2C of the D7 Stage 2d implementation phase.
Tasks 2A AND 2B must both be committed. If either is not, halt.

═══════════════════════════════════════════════════════════════════
AUTHORITY AND PREREQUISITES
═══════════════════════════════════════════════════════════════════

Scope lock:
  File:    docs/d7_stage2d/D7_STAGE2D_SCOPE_LOCK_v2.md
  Commit:  4303d8de2882362ec55c8c581519331c5f6404c6

Task 2A prerequisite: docs/d7_stage2d/label_universe_analysis.json
  (committed, SHA256 recorded)

Task 2B prerequisite: docs/d7_stage2d/replay_candidates.json
  (committed, SHA256 recorded)

Verify BEFORE starting: both files committed, SHA256s recorded.

═══════════════════════════════════════════════════════════════════
OBJECTIVE
═══════════════════════════════════════════════════════════════════

Produce docs/d7_stage2d/deep_dive_candidates.json. This is a
documentation-layer artifact consumed by the expectations file and
self-check script, NOT by the fire script. It contains exactly 20
stratified deep-dive candidates selected per scope lock Lock 4.

The selection must:
  - Exclude all 20 Stage 2c overlap positions (automatic).
  - Exclude pos 116 (automatic).
  - Satisfy all 6 stratum min/max constraints from Lock 4.1.
  - Include at least 3 of the 9 fresh eligible-pool positions
    (Lock 4.3).
  - Be deterministic and justifiable.

═══════════════════════════════════════════════════════════════════
DELIVERABLES
═══════════════════════════════════════════════════════════════════

Two files:
  1. docs/d7_stage2d/deep_dive_candidates.json
  2. scripts/build_d7_stage2d_deep_dive.py
     (the deterministic selection script; audited as part of
     deliverables)

═══════════════════════════════════════════════════════════════════
STRATUM CONSTRAINTS (from scope lock Lock 4.1)
═══════════════════════════════════════════════════════════════════

Total across strata = 20. Each stratum has a min and max count.

  Stratum 1: RSI-absent volatility_regime
    Fresh pool = 7 at positions {3, 43, 68, 128, 173, 188, 198}
    Min 3, Max 5

  Stratum 2: RSI-present volatility_regime
    Fresh pool = 29 (computed from batch inspection)
    Min 2, Max 4

  Stratum 3: MR high-recurrence / high-overlap (not in Stage 2c)
    Broadened: includes exact 7-factor repeats (pos 197) AND
    high-overlap near-repeats with max_overlap_with_priors >= 5
    Min 3, Max 5

  Stratum 4: Early-position 1-50 fresh
    Fresh pool = 46
    Min 2, Max 4

  Stratum 5: Late-position 163-200 fresh
    Fresh pool = 38
    Min 2, Max 4

  Stratum 6: Rare-families themes (momentum, volume_divergence,
    calendar_effect), excluding pos 74 which is Stage 2c
    Fresh pool ≈ 119
    Min 2, Max 4

Fresh eligible-pool priority: at least 3 of 9 positions from
{122, 127, 128, 129, 132, 172, 178, 182, 187} must be selected.
Natural placements:
  - pos 128 → Stratum 1 (fresh RSI-absent vol_regime)
  - pos 122, 127, 129, 132 → likely Stratum 2 or theme-dependent
  - pos 172, 178, 182, 187 → Stratum 5 (late-position fresh)

A candidate may fit multiple strata; it is counted toward one chosen
stratum (the primary). Record the primary stratum in the output.

═══════════════════════════════════════════════════════════════════
SELECTION METHODOLOGY (MUST BE DETERMINISTIC)
═══════════════════════════════════════════════════════════════════

The selection must be reproducible and justifiable. Do NOT use
random sampling with a seed you invented. Use a deterministic,
rule-based selection:

Option A (recommended): Rank-based within each stratum.
  For each stratum, define a ranking criterion (e.g., "highest
  factor_set_prior_occurrences", or "theme diversity", or
  "position-spread maximum"). Apply deterministically.

Option B: Explicit hand-picked list with justification per pick.
  Document each candidate's inclusion reason. Ensures strata
  constraints satisfied and fresh-9 min-3 satisfied.

Either option must produce a byte-identical output on re-run. Do NOT
rely on hash-based sampling that depends on external state.

Whichever option is chosen, document the methodology clearly in the
selection script's module docstring AND in the output JSON's
`selection_methodology` field.

═══════════════════════════════════════════════════════════════════
OUTPUT JSON SCHEMA
═══════════════════════════════════════════════════════════════════

{
  "source_batch_uuid": "5cf76668-47d1-48d7-bd90-db06d31982ed",
  "stage": "d7_stage2d",
  "scope_lock_commit": "4303d8de2882362ec55c8c581519331c5f6404c6",
  "label_universe_analysis_sha256": "<SHA256 of committed Task 2A JSON>",
  "replay_candidates_sha256": "<SHA256 of committed Task 2B JSON>",
  "selection_timestamp_utc": "<ISO 8601>",
  "selection_methodology": "<prose describing the deterministic selection rule>",
  "total_deep_dive_count": 20,
  "fresh_eligible_pool_inclusion_count": <int, must be >= 3>,
  "strata": [
    {
      "stratum_id": 1,
      "name": "RSI-absent volatility_regime",
      "min_count": 3,
      "max_count": 5,
      "selected_count": <int between 3 and 5>,
      "fresh_pool_size": 7,
      "selected_positions": [<sorted ints>]
    },
    { ... stratum 2 ... },
    { ... stratum 3 ... },
    { ... stratum 4 ... },
    { ... stratum 5 ... },
    { ... stratum 6 ... }
  ],
  "candidates": [
    {
      "position": <int>,
      "theme": "<from D6_STAGE2D summary>",
      "primary_stratum_id": <int 1-6>,
      "also_fits_strata": [<list of other stratum_ids if multiple fits, empty otherwise>],
      "is_in_fresh_eligible_pool": <bool>,
      "universe_a_label": "<label or null>",
      "universe_b_label": "<label>",
      "factor_set_size": <int>,
      "factor_set_prior_occurrences": <int>,
      "max_overlap_with_priors": <int>,
      "selection_rationale": "<one-sentence reason this candidate was chosen>"
    },
    ... exactly 20 entries, sorted by position ascending
  ]
}

═══════════════════════════════════════════════════════════════════
INTERNAL INVARIANT ASSERTIONS
═══════════════════════════════════════════════════════════════════

  C1.  total_deep_dive_count == 20
  C2.  len(candidates) == 20
  C3.  All 20 candidate positions are distinct
  C4.  No candidate position is in the Stage 2c 20 set
       {17, 22, 27, 32, 62, 72, 73, 74, 77, 83,
        97, 102, 107, 112, 117, 138, 143, 147, 152, 162}
  C5.  No candidate position == 116
  C6.  Every candidate's position is in replay_candidates.json's
       non-skipped set (i.e., is replay-eligible)
  C7.  sum([stratum.selected_count for stratum in strata]) == 20
  C8.  Every stratum satisfies min_count <= selected_count <=
       max_count
  C9.  Union of all strata.selected_positions == set of 20
       candidate positions (set equality)
  C10. Every candidate.primary_stratum_id appears in strata list
  C11. fresh_eligible_pool_inclusion_count >= 3
  C12. fresh_eligible_pool_inclusion_count ==
       count of candidates where is_in_fresh_eligible_pool == true
  C13. The candidates where is_in_fresh_eligible_pool == true are
       a subset of {122, 127, 128, 129, 132, 172, 178, 182, 187}
  C14. label_universe_analysis_sha256 matches committed Task 2A
  C15. replay_candidates_sha256 matches committed Task 2B
  C16. scope_lock_commit == v2 hash
  C17. All position lists sorted ascending
  C18. JSON sort_keys=True, indent=2
  C19. Each candidate's universe_b_label consistent with
       replay_candidates.json
  C20. Stratum 1 selected_positions are all fresh-RSI-absent-vol
       (i.e., subset of {3, 43, 68, 128, 173, 188, 198})
  C21. Stratum 6 selected_positions are all in themes
       {momentum, volume_divergence, calendar_effect} AND NOT pos 74

═══════════════════════════════════════════════════════════════════
SELF-AUDIT (STAGE 1)
═══════════════════════════════════════════════════════════════════

After producing deliverables, verify EVERY item in the Task 2C
Sign-Off Checklist (implementation plan, section 6.5). PASS/FAIL per
item with concrete evidence.

═══════════════════════════════════════════════════════════════════
REPORTING BACK TO CHARLIE
═══════════════════════════════════════════════════════════════════

Provide:
  1. Full contents of docs/d7_stage2d/deep_dive_candidates.json
  2. Full contents of scripts/build_d7_stage2d_deep_dive.py
  3. Detailed selection methodology prose (can be the same as the
     selection_methodology field in the JSON, but expanded if helpful)
  4. Per-stratum summary: min/max/selected counts, positions chosen
  5. List of fresh-eligible-pool candidates included (must be >= 3)
  6. Stage 1 self-audit report with PASS/FAIL per item
  7. SHA256 of output JSON
  8. Idempotency test result: re-run the builder script, confirm
     byte-identical output (excluding selection_timestamp_utc)

═══════════════════════════════════════════════════════════════════
IMPORTANT NOTE ON HUMAN OVERSIGHT
═══════════════════════════════════════════════════════════════════

Selection is a scientific decision, not purely mechanical. While the
script must be deterministic, the rationale for each selected
candidate must be legible and defensible. Charlie may request
adjustments during Stage 3 (advisor review); prepare to justify each
pick and be open to re-selection if a candidate is deemed
unrepresentative of its stratum.

═══════════════════════════════════════════════════════════════════
OUT OF SCOPE
═══════════════════════════════════════════════════════════════════

Do NOT:
  - Start Task 2D
  - Modify Task 2A or 2B outputs
  - Modify any Stage 2b/2c artifact
  - Commit

Good luck.
```

### 6.5 Task 2C Sign-Off Checklist

**Prerequisite gates:**

- [ ] **2C.1** — Task 2A committed; SHA256 recorded
- [ ] **2C.2** — Task 2B committed; SHA256 recorded
- [ ] **2C.3** — Output JSON's `label_universe_analysis_sha256` matches committed Task 2A
- [ ] **2C.4** — Output JSON's `replay_candidates_sha256` matches committed Task 2B

**Structural deliverable gates:**

- [ ] **2C.5** — `docs/d7_stage2d/deep_dive_candidates.json` exists
- [ ] **2C.6** — `scripts/build_d7_stage2d_deep_dive.py` exists
- [ ] **2C.7** — No Task 2A/2B files modified

**Stratum constraint gates:**

- [ ] **2C.8** — All 6 strata defined with correct names, min/max per Lock 4.1
- [ ] **2C.9** — Stratum 1 (RSI-absent vol_regime): 3-5 selected, all from fresh pool {3, 43, 68, 128, 173, 188, 198}
- [ ] **2C.10** — Stratum 2 (RSI-present vol_regime): 2-4 selected
- [ ] **2C.11** — Stratum 3 (MR high-recurrence): 3-5 selected, using broadened definition
- [ ] **2C.12** — Stratum 4 (Early-pos 1-50): 2-4 selected
- [ ] **2C.13** — Stratum 5 (Late-pos 163-200): 2-4 selected
- [ ] **2C.14** — Stratum 6 (Rare-families): 2-4 selected, themes in {momentum, volume_divergence, calendar_effect}, NOT pos 74
- [ ] **2C.15** — Sum of selected counts across strata == 20

**Exclusion gates:**

- [ ] **2C.16** — No candidate position in Stage 2c 20 set
- [ ] **2C.17** — No candidate position == 116
- [ ] **2C.18** — All 20 candidate positions are in replay_candidates.json replay-eligible set

**Fresh eligible pool gates:**

- [ ] **2C.19** — At least 3 of 9 fresh eligible-pool positions included ({122, 127, 128, 129, 132, 172, 178, 182, 187})
- [ ] **2C.20** — `fresh_eligible_pool_inclusion_count` field accurately reflects actual count
- [ ] **2C.21** — Candidates marked `is_in_fresh_eligible_pool: true` are all in the expected 9-position set

**Schema gates:**

- [ ] **2C.22** — All top-level schema fields present
- [ ] **2C.23** — Every candidate has required fields: position, theme, primary_stratum_id, also_fits_strata, is_in_fresh_eligible_pool, universe_a_label, universe_b_label, factor_set_size, factor_set_prior_occurrences, max_overlap_with_priors, selection_rationale
- [ ] **2C.24** — Candidates sorted by position ascending
- [ ] **2C.25** — JSON is `sort_keys=True, indent=2`

**Invariant gates:**

- [ ] **2C.26** — All 21 script-internal invariants (C1-C21) PASS

**Determinism gates:**

- [ ] **2C.27** — Re-run builder script; output byte-identical (excluding selection_timestamp_utc)

**Methodology transparency:**

- [ ] **2C.28** — `selection_methodology` field describes deterministic rule (not "random seed")
- [ ] **2C.29** — Every candidate has a concrete selection_rationale (not placeholder text)

**Reporting gates:**

- [ ] **2C.30** — Stage 1 self-audit report produced
- [ ] **2C.31** — Per-stratum summary table provided

### 6.6 Task 2C Stage 2 (Codex) Review Mandate

Codex must beyond the checklist:

**Selection representativeness:**
- For each stratum, verify the selected candidates genuinely span
  the stratum's intent. E.g., Stratum 1 should not all cluster at
  late positions; Stratum 5 should not all have identical
  factor_set_size.
- Flag any stratum where selection appears skewed toward a narrow
  sub-pattern within the stratum.

**Selection rationale quality:**
- Each candidate's `selection_rationale` must be a substantive
  sentence, not boilerplate. Flag any rationale that is generic or
  unsubstantiated.

**Fresh-pool placement:**
- Verify that fresh-pool candidates are placed in natural strata
  (e.g., 128 → Stratum 1, 187 → Stratum 5) rather than squeezed in
  for count-satisfaction reasons.

**Alternative selection check:**
- Could a different deterministic rule produce a materially
  different set of 20? If yes, is the chosen rule defensibly better?
  Flag if the selection appears arbitrary.

**Anti-hindsight:**
- Confirm no Stage 2d simulation or dry-run evidence was used in
  selection (script should not reference any Stage 2d
  post-fire data).

### 6.7 Task 2C Commit Instructions

Under v2 workflow, Task 2C commits after Codex Stage 2 PASS. Task 2C
is the only task requiring a scientific-judgment step (candidate
selection), so Codex should apply more rigor here than on purely
mechanical tasks. Charlie should also personally eyeball the 20
selected candidates before accepting Codex PASS — if any pick feels
unrepresentative of its stratum, Charlie can request resubmission
without waiting for the final advisor stage. The final advisor
acceptance verdict (Section 2.5) will re-examine selection quality
as part of cross-task review.

**Key scientific-quality checks Codex must confirm before PASS:**
- Each of the 20 selected candidates has a substantive, concrete
  `selection_rationale` (not boilerplate)
- Strata are not skewed toward a narrow sub-pattern within their
  scope
- Fresh-pool candidates are placed in natural strata (not squeezed
  in for count-satisfaction only)
- Selection methodology is deterministic (no undocumented random seed)

**Key integrity checks:**
- Task 2A and 2B SHA256s match the fields in Task 2C output
- No overlap with Stage 2c 20 positions
- Pos 116 not selected
- Stratum min/max constraints all satisfied; sum == 20
- At least 3/9 fresh-eligible-pool positions included

**Commit template (Codex PASS):**

```
git add docs/d7_stage2d/deep_dive_candidates.json
git add scripts/build_d7_stage2d_deep_dive.py
git commit -m "D7 Stage 2d Task 2C: deep-dive candidates JSON

- 20 stratified candidates across 6 strata per scope lock Lock 4
- At least 3/9 fresh eligible-pool candidates included
- Excludes Stage 2c 20 overlap set; excludes pos 116
- Cross-references Task 2A and 2B by SHA256
- Selection methodology: <brief>
- Two-stage per-task gate: Claude Code self-audit, Codex review"
```

Record commit hash and SHA256s in Section 8.3 below. Proceed to
Task 2D.

---

## 7. Task 2D — Test-Retest Baselines JSON

### 7.1 Objective

Assemble Stage 2b and Stage 2c baseline scores for all 20 Stage 2c
overlap candidates, indexed by position, for consumption by Stage 2d
expectations and sign-off.

### 7.2 Deliverable

- `docs/d7_stage2d/test_retest_baselines.json`

### 7.3 Prerequisites

Tasks 2A, 2B, 2C all ACCEPTED and committed.

### 7.4 Claude Code prompt — Task 2D

```
You are implementing Task 2D of the D7 Stage 2d implementation phase.
Tasks 2A, 2B, 2C must all be committed. Verify before starting.

═══════════════════════════════════════════════════════════════════
AUTHORITY AND PREREQUISITES
═══════════════════════════════════════════════════════════════════

Scope lock:
  File:    docs/d7_stage2d/D7_STAGE2D_SCOPE_LOCK_v2.md
  Commit:  4303d8de2882362ec55c8c581519331c5f6404c6

Prerequisites:
  Task 2A: label_universe_analysis.json (committed)
  Task 2B: replay_candidates.json (committed)
  Task 2C: deep_dive_candidates.json (committed)

Stage 2b / Stage 2c source-of-truth:
  docs/d7_stage2b/stage2b_batch_record.json (committed)
  docs/d7_stage2c/stage2c_batch_record.json (committed)
  docs/d7_stage2b/call_*_live_call_record.json (committed)
  docs/d7_stage2c/call_*_live_call_record.json (committed)
  docs/closeout/PHASE2B_D7_STAGE2B_SIGNOFF.md (committed)
  docs/closeout/PHASE2B_D7_STAGE2C_SIGNOFF.md (committed)

═══════════════════════════════════════════════════════════════════
OBJECTIVE
═══════════════════════════════════════════════════════════════════

Produce docs/d7_stage2d/test_retest_baselines.json. This file
consolidates Stage 2b and Stage 2c baseline scores for all 20
Stage 2c overlap candidates, used by Stage 2d expectations (test-
retest rubric) and sign-off (drift adjudication).

This file is consumed by the expectations file and self-check
script, NOT the fire script.

═══════════════════════════════════════════════════════════════════
DELIVERABLES
═══════════════════════════════════════════════════════════════════

Two files:
  1. docs/d7_stage2d/test_retest_baselines.json
  2. scripts/build_d7_stage2d_baselines.py
     (deterministic builder script)

═══════════════════════════════════════════════════════════════════
DATA SOURCES AND MAPPING
═══════════════════════════════════════════════════════════════════

For each of the 20 Stage 2c overlap positions, gather:

From Stage 2b (if position was in Stage 2b's 5-candidate batch, i.e.,
positions {17, 73, 74, 97, 138}):
  - Stage 2b D7b plausibility score
  - Stage 2b D7b alignment score
  - Stage 2b D7b SVR score
  - Source: docs/d7_stage2b/call_*_live_call_record.json
  - Reasoning length (char count)

From Stage 2c (ALL 20 positions were in Stage 2c):
  - Stage 2c D7b plausibility score
  - Stage 2c D7b alignment score
  - Stage 2c D7b SVR score
  - Source: docs/d7_stage2c/call_*_live_call_record.json
  - Reasoning length (char count)

From label_universe_analysis.json:
  - Stage 2c frozen label (Universe A)
  - Universe B label
  - Conflict bool

═══════════════════════════════════════════════════════════════════
OUTPUT JSON SCHEMA
═══════════════════════════════════════════════════════════════════

{
  "source_batch_uuid": "5cf76668-47d1-48d7-bd90-db06d31982ed",
  "stage": "d7_stage2d",
  "scope_lock_commit": "4303d8de2882362ec55c8c581519331c5f6404c6",
  "label_universe_analysis_sha256": "<SHA256 of committed Task 2A JSON>",
  "replay_candidates_sha256": "<SHA256 of committed Task 2B JSON>",
  "deep_dive_candidates_sha256": "<SHA256 of committed Task 2C JSON>",
  "build_timestamp_utc": "<ISO 8601>",
  "tier_1_positions": [17, 73, 74, 97, 138],
  "tier_2_positions": [22, 27, 32, 62, 72, 77, 83, 102, 107, 112,
                       117, 143, 147, 152, 162],
  "baselines": [
    {
      "position": 17,
      "tier": 1,
      "stage2c_frozen_label": "divergence_expected",
      "universe_b_label": "neutral",
      "label_conflict": true,
      "stage2b": {
        "plausibility": 0.75,
        "alignment": 0.85,
        "svr": 0.85,
        "reasoning_length": 1237,
        "source_record_sha256": "<SHA256 of committed call record>"
      },
      "stage2c": {
        "plausibility": 0.75,
        "alignment": 0.85,
        "svr": 0.85,
        "reasoning_length": <from call_1_live_call_record>,
        "source_record_sha256": "<SHA256 of committed call record>"
      }
    },
    ... entries for all 20 positions, Tier 1 entries have stage2b
        populated; Tier 2 entries have stage2b == null ...
    {
      "position": 22,
      "tier": 2,
      "stage2c_frozen_label": "neutral",
      "universe_b_label": "<from label_universe_analysis>",
      "label_conflict": <bool>,
      "stage2b": null,
      "stage2c": {
        "plausibility": 0.75,
        "alignment": 0.90,
        "svr": 0.85,
        "reasoning_length": <>,
        "source_record_sha256": "<>"
      }
    },
    ...
  ]
}

Entries sorted by position ascending.

═══════════════════════════════════════════════════════════════════
INTERNAL INVARIANT ASSERTIONS
═══════════════════════════════════════════════════════════════════

  D1.  len(baselines) == 20
  D2.  tier_1_positions == [17, 73, 74, 97, 138]
  D3.  tier_2_positions has exactly 15 entries, sorted
  D4.  Union of tier_1 and tier_2 == set of 20 baseline positions
  D5.  No overlap between tier_1 and tier_2 (disjoint sets)
  D6.  All 5 Tier 1 entries have stage2b != null
  D7.  All 15 Tier 2 entries have stage2b == null
  D8.  All 20 entries have stage2c != null
  D9.  Every stage2c.svr value falls in [0.0, 1.0]
  D10. Every stage2c value matches the Stage 2c signoff score table
       (Stage 2c signoff has authoritative score table in §6)
  D11. Every stage2b value matches the Stage 2b signoff score table
       (Stage 2b signoff §5.3-5.5)
  D12. label_universe_analysis_sha256 matches committed Task 2A
  D13. replay_candidates_sha256 matches committed Task 2B
  D14. deep_dive_candidates_sha256 matches committed Task 2C
  D15. No deep_dive_candidates position is in baselines position set
       (strict disjointness: deep-dive and overlap are mutually
        exclusive)
  D16. JSON sort_keys=True, indent=2
  D17. All position lists sorted ascending
  D18. source_record_sha256 values are computed from the committed
       call record files

═══════════════════════════════════════════════════════════════════
SELF-AUDIT (STAGE 1)
═══════════════════════════════════════════════════════════════════

After producing deliverables, verify EVERY item in the Task 2D
Sign-Off Checklist (implementation plan, section 7.5).

═══════════════════════════════════════════════════════════════════
REPORTING BACK TO CHARLIE
═══════════════════════════════════════════════════════════════════

Provide:
  1. Full contents of docs/d7_stage2d/test_retest_baselines.json
  2. Full contents of scripts/build_d7_stage2d_baselines.py
  3. Per-position verification table: position, tier, 2b scores,
     2c scores, source record SHA256s
  4. Cross-check output: Stage 2b and Stage 2c signoff score tables
     reproduced and compared to this output
  5. Stage 1 self-audit report with PASS/FAIL per item
  6. SHA256 of output JSON
  7. Idempotency test result (excluding build_timestamp_utc)

═══════════════════════════════════════════════════════════════════
OUT OF SCOPE
═══════════════════════════════════════════════════════════════════

Do NOT:
  - Start expectations authoring
  - Write fire script
  - Modify Tasks 2A/2B/2C outputs
  - Modify Stage 2b/2c artifacts
  - Commit

Good luck.
```

### 7.5 Task 2D Sign-Off Checklist

**Prerequisite gates:**

- [ ] **2D.1** — Tasks 2A, 2B, 2C all committed; SHA256s recorded
- [ ] **2D.2** — All three SHA256 fields in output match committed predecessors

**Structural deliverable gates:**

- [ ] **2D.3** — `docs/d7_stage2d/test_retest_baselines.json` exists
- [ ] **2D.4** — `scripts/build_d7_stage2d_baselines.py` exists
- [ ] **2D.5** — No predecessor outputs modified

**Tier structure gates:**

- [ ] **2D.6** — `tier_1_positions == [17, 73, 74, 97, 138]`
- [ ] **2D.7** — `tier_2_positions == [22, 27, 32, 62, 72, 77, 83, 102, 107, 112, 117, 143, 147, 152, 162]` (sorted)
- [ ] **2D.8** — `len(baselines) == 20`
- [ ] **2D.9** — All Tier 1 entries have `stage2b != null` and `tier: 1`
- [ ] **2D.10** — All Tier 2 entries have `stage2b == null` and `tier: 2`
- [ ] **2D.11** — All 20 entries have `stage2c != null`

**Score fidelity gates (cross-check against signoffs):**

- [ ] **2D.12** — Pos 17 Stage 2b (plaus=0.75, align=0.85, svr=0.85) matches signoff §3
- [ ] **2D.13** — Pos 73 Stage 2b (plaus=0.75, align=0.85, svr=0.85) matches signoff §5.3
- [ ] **2D.14** — Pos 74 Stage 2b (plaus=0.75, align=0.85, svr=0.65) matches signoff §5.3 (alignment value sourced from call record; Stage 2b signoff §5.3–5.5 does not tabulate alignment)
- [ ] **2D.15** — Pos 97 Stage 2b (plaus=0.75, align=0.90, svr=0.95) matches signoff §5.4
- [ ] **2D.16** — Pos 138 Stage 2b (plaus=0.75, align=0.90, svr=0.15) matches signoff §5.5
- [ ] **2D.17** — All 20 Stage 2c scores match Stage 2c signoff §6 table exactly
- [ ] **2D.18** — Every `source_record_sha256` is computed from the committed call record file

**Label gates:**

- [ ] **2D.19** — Every `stage2c_frozen_label` matches the Stage 2c selection label
- [ ] **2D.20** — Every `universe_b_label` matches Task 2A's `stage2c_overlap_label_comparison`
- [ ] **2D.21** — Every `label_conflict` bool correctly = `(frozen != universe_b)`

**Disjointness gates:**

- [ ] **2D.22** — Baseline position set and deep_dive_candidates position set are disjoint (no overlap between 20 overlaps and 20 deep-dives)

**Schema gates:**

- [ ] **2D.23** — Top-level fields all present
- [ ] **2D.24** — Each baseline entry has required fields
- [ ] **2D.25** — All positions sorted ascending
- [ ] **2D.26** — JSON `sort_keys=True, indent=2`

**Invariant gates:**

- [ ] **2D.27** — All 18 script-internal invariants (D1-D18) PASS

**Determinism gates:**

- [ ] **2D.28** — Re-run builder; byte-identical (excluding build_timestamp_utc)

**Reporting gates:**

- [ ] **2D.29** — Stage 1 self-audit report produced
- [ ] **2D.30** — Per-position verification table provided

### 7.6 Task 2D Stage 2 (Codex) Review Mandate

Beyond checklist, Codex must:

**Independent signoff cross-check:**
- Read PHASE2B_D7_STAGE2B_SIGNOFF.md §5.3-5.5 and PHASE2B_D7_STAGE2C_SIGNOFF.md §6; independently compare every score to the output. Any mismatch is a FAIL.

**Call record content verification:**
- Open 5-10 randomly selected committed call record JSONs and confirm the scores match the baselines output. Rotate selection across Tier 1 and Tier 2.

**SHA256 integrity:**
- Independently compute SHA256 of 3-5 call records and verify they match the output's `source_record_sha256` fields.

**Disjointness verification:**
- Compute: set(baselines positions) ∩ set(deep_dive_candidates positions); must be empty.

### 7.7 Task 2D Commit Instructions and Final Advisor Trigger

Under v2 workflow, Task 2D commits after Codex Stage 2 PASS. **Task
2D commit is the trigger for the Final Advisor Acceptance Verdict
(Section 2.5).**

**Key score-fidelity checks Codex must confirm before PASS:**
- Pos 17, 73, 74, 97, 138 Stage 2b scores exactly match signoff §3
  and §5.3-5.5 (no rounding, no approximation)
- All 20 Stage 2c scores exactly match Stage 2c signoff §6 score
  table
- Every `source_record_sha256` is computed from the actual committed
  Stage 2b or Stage 2c call record file (not recomputed from stored
  scores)

**Key integrity checks:**
- All three predecessor SHA256s (Task 2A, 2B, 2C) match committed
  files
- Tier 1 = {17, 73, 74, 97, 138} exactly
- Tier 2 = the 15 remaining Stage 2c positions, sorted
- Baseline position set and Task 2C deep-dive position set are
  strictly disjoint (no overlap between the 20 overlaps and the 20
  deep-dives)

**Commit template (Codex PASS):**

```
git add docs/d7_stage2d/test_retest_baselines.json
git add scripts/build_d7_stage2d_baselines.py
git commit -m "D7 Stage 2d Task 2D: test-retest baselines JSON

- 20 baseline entries (5 Tier 1 + 15 Tier 2) for Stage 2c overlap
  positions
- Stage 2b scores for Tier 1 positions {17, 73, 74, 97, 138}
- Stage 2c scores for all 20 positions
- Cross-references Tasks 2A/2B/2C by SHA256
- All scores verified against Stage 2b/2c signoff tables
- Two-stage per-task gate: Claude Code self-audit, Codex review"
```

Record commit hash and SHA256s in Section 8.4 below.

**After Task 2D commit, trigger Final Advisor Acceptance Verdict:**

Package the following and send to advisor:

1. All four commit hashes (2A, 2B, 2C, 2D) with UTC timestamps
2. All deliverable file SHA256s (8-10 files total)
3. All four Stage 1 self-audit reports (per task, full PASS/FAIL)
4. All four Stage 2 Codex review reports (per task, including any
   round-1 FAIL → round-N PASS iteration history)
5. Full content of all four JSON deliverables (or summaries +
   representative sections if size is prohibitive)
6. Full content of all build/derivation scripts
7. Completed Section 8 Implementation Log

Advisor runs the 7-category cross-task integrity audit from Section
2.5 and returns one of:

- **✅ FULL ACCEPTED** → Expectations Authoring Phase unlocked
- **⚠️ CONDITIONAL ACCEPTED** → fix in place, no re-run needed
- **❌ REJECTED at task X** → specific re-work required

---

## 8. Implementation Log

Populate this section as each task is committed (after Codex Stage 2
PASS). Section 8.5 is populated after the Final Advisor Acceptance
Verdict (Section 2.5) is rendered.

### 8.1 Task 2A — Label Universe Derivation

| Field | Value |
|---|---|
| Status | ✅ COMMITTED (2026-04-19) |
| Claude Code Stage 1 date | 2026-04-19 (PASS, all 31 checklist items + 22 invariants) |
| Codex round 1 verdict | FAIL — flagged `sort_keys=True`, `non_call_position_details` field, `conflict` vs `conflict_bool` field naming as scope-lock conflicts |
| Clarification rationale | All three items were explicit task-prompt requirements; Lock 11.2 schema block is a key/type description, not a literal key-order contract; prompt is authoritative (see Section 2.4) |
| Codex round 2 verdict | PASS — Charlie cleared to commit |
| Branch | `claude/setup-structure-validators-JNqoI` |
| Commit hash (short) | `1ce179f` |
| Commit hash (full 40-char) | *TO BE FILLED — run `git log --format="%H" -n 1 docs/d7_stage2d/label_universe_analysis.json`* |
| Commit UTC timestamp | *TO BE FILLED — run `git log --format="%ci" -n 1 docs/d7_stage2d/label_universe_analysis.json`* |
| Files committed | `scripts/derive_d7_stage2d_label_universes.py` + `docs/d7_stage2d/label_universe_analysis.json` (2 files, 943 insertions) |
| `scripts/derive_d7_stage2d_label_universes.py` SHA256 | *TO BE FILLED — `sha256sum` output* |
| `docs/d7_stage2d/label_universe_analysis.json` SHA256 | *TO BE FILLED — `sha256sum` output* |
| Observed Universe A | 11 / 3 / 15 ✓ (matches hardcoded expectation) |
| Observed Universe B | 66 / 5 / 128 ✓ (matches hardcoded expectation) |
| Fresh pool positions | `[122, 127, 128, 129, 132, 172, 178, 182, 187]` ✓ (matches Lock 4.3 expectation) |
| Stage 2c overlap conflicts | 3 (positions 17, 73, 74); all `divergence_expected → neutral` under Universe B per Lock 6.1 ✓ |
| Idempotency diff | empty ✓ |
| Invariants asserted pre-write | all 22 (A1-A22) ✓ |
| Final advisor verdict | PENDING (deferred to Section 8.5 after all four tasks committed) |

### 8.2 Task 2B — Replay Candidates JSON

| Field | Value |
|---|---|
| Status | BLOCKED (awaiting Task 2A full hash backfill; then UNBLOCKED) |
| Claude Code Stage 1 date | |
| Codex round 1 verdict | |
| Codex round N verdict | |
| Commit hash (full 40-char) | |
| Commit UTC timestamp | |
| Files committed | |
| `docs/d7_stage2d/replay_candidates.json` SHA256 | |
| Builder script path (if any) | |
| Builder script SHA256 (if any) | |
| Observed Universe B totals in output | |
| Observed Universe A totals in output | |
| Pos 116 `is_skipped_source=true` verified | |
| Label universe analysis SHA256 reference matches 2A | |
| Final advisor verdict | PENDING (deferred to Section 8.5) |

### 8.3 Task 2C — Deep-Dive Candidates JSON

| Field | Value |
|---|---|
| Status | BLOCKED (awaiting 2B) |
| Claude Code Stage 1 date | |
| Codex round 1 verdict | |
| Codex round N verdict | |
| Commit hash (full 40-char) | |
| Commit UTC timestamp | |
| Files committed | |
| `docs/d7_stage2d/deep_dive_candidates.json` SHA256 | |
| `scripts/build_d7_stage2d_deep_dive.py` SHA256 | |
| Per-stratum selected counts | |
| Fresh-pool inclusion count (must be ≥ 3) | |
| Selection methodology (brief) | |
| Task 2A/2B SHA256 references match committed | |
| Final advisor verdict | PENDING (deferred to Section 8.5) |

### 8.4 Task 2D — Test-Retest Baselines JSON

| Field | Value |
|---|---|
| Status | BLOCKED (awaiting 2C) |
| Claude Code Stage 1 date | |
| Codex round 1 verdict | |
| Codex round N verdict | |
| Commit hash (full 40-char) | |
| Commit UTC timestamp | |
| Files committed | |
| `docs/d7_stage2d/test_retest_baselines.json` SHA256 | |
| `scripts/build_d7_stage2d_baselines.py` SHA256 | |
| Tier 1 positions verified | `{17, 73, 74, 97, 138}` |
| Tier 2 positions verified | 15 positions |
| Stage 2b score match to signoff | |
| Stage 2c score match to signoff | |
| Deep-dive / baseline disjointness | |
| Task 2A/2B/2C SHA256 references match committed | |
| Final advisor verdict | PENDING (deferred to Section 8.5) |

### 8.5 Final Advisor Acceptance Verdict (cross-task)

**Triggered:** after Task 2D commits.
**Advisor input package:** see Section 7.7 "After Task 2D commit" for
the 7-item package required.
**Audit categories:** see Section 2.5 for the 7-category audit
(a: SHA256 chain; b: count consistency; c: label conflict fidelity;
d: Stage 2b/2c score fidelity; e: review quality; f: scope lock
fidelity; g: ready-to-proceed).

| Field | Value |
|---|---|
| Status | BLOCKED (awaiting all four task commits) |
| Full package received date | |
| SHA256 chain integrity (a) | |
| Scientific counts consistency (b) | |
| Label conflict fidelity (c) | |
| Stage 2b/2c score fidelity (d) | |
| Review quality audit (e) | |
| Scope lock v2 fidelity (f) | |
| Ready-to-proceed check (g) | |
| **Overall verdict** | FULL ACCEPTED / CONDITIONAL ACCEPTED / REJECTED |
| Fix items (if any) | |
| Expectations Authoring Phase unlocked | YES / NO |
| Verdict date | |

---

## 9. Post-Implementation-Phase Next Steps

**Stage 2d Implementation Phase status: ✅ FULL ACCEPTED
(Final Advisor Verdict, 2026-04-19)**

**Outstanding follow-up items:** see Section 10.

Once all four tasks are committed AND the Final Advisor Acceptance
Verdict is FULL ACCEPTED (or CONDITIONAL ACCEPTED with fixes applied):

1. **Expectations Authoring Phase** begins (separate session, advisor-scaffolded).
   - 20 deep-dive candidates receive Stage 2c-style per-candidate prose
   - 20 test-retest candidates receive compact structured rubric
   - TBD-A1, TBD-A2, TBD-DIST resolved to numeric values
   - Aggregate claims finalized (Lock 6)

2. **Self-Check Script Creation** (Task 2E-prerequisite).
   - `scripts/stage2d_self_check.py` covering all 17 gates (Lock 12)

3. **Fire Script Creation** (Task 2E proper).
   - `scripts/run_d7_stage2d_batch.py` per Lock 10
   - New parallel script, not a parameterized extension of Stage 2c

4. **Expectations Commit** (per Lock 11.5 ordering).

5. **Live Fire** (`--confirm-live`).

6. **Sign-Off Adjudication** (Lock 13).

7. **D7 track closes; Phase 2B → D8 (policy gate)**.

---

## 10. Post-D7 Follow-Up Items

These are tracked here because they were surfaced during Stage 2c /
Stage 2d Codex reviews but are out-of-scope for Stage 2d itself.
They are **binding work items, not wishlist.** Each must be
addressed (or explicitly re-deferred with recorded rationale)
before Phase 2B advances to D8.

### 10.1 Stub Fixture Isolation Retrofit

**Origin:** Codex Stage 2c HIGH observation (substantive design
finding, not false positive); reconfirmed during Stage 2d review.

**Issue:** All three D7 fire scripts
(`scripts/run_d7_stage2b_batch.py`,
`scripts/run_d7_stage2c_batch.py`, future
`scripts/run_d7_stage2d_batch.py`) pass
`stage2d_artifacts_root=RAW_PAYLOAD_ROOT` into their replay
reconstruction in BOTH live and stub modes. Lock 10.2 specifies
write-side stub/live isolation but is silent on read-side. Stub
mode therefore indirectly depends on the live-mode artifact root,
so "clean replay from a fixture" is not actually validated by the
shipped command path.

**Why deferred from Stage 2d implementation phase:**

- Scope Lock v2 Lock 10.2 does not require read-side isolation;
  Task 2E implementing it would be a scope-lock deviation, which
  the Stage 2c patch report §5 adjudication explicitly prohibits.
- Stage 2b and 2c are already signed off; retrofitting their fire
  scripts now provides no Stage 2d benefit.
- Asymmetric retrofit (only Stage 2d) would create an
  operational-identity variance across the three fire scripts,
  exactly the kind of inconsistency Lock 5 carry-forward
  discipline warns against.

**Resolution path (post-D7 sign-off, pre-D8 entry):**

1. **Step 1 — Mini scope lock v2.1** (1–2 advisor turns, design only)
   - Defines stub fixture root path
   - Defines fixture materialize strategy (copy / symlink /
     git-fixtures / generated; pick exactly one)
   - Defines fixture SHA256 anchoring (fixture data IS
     contract-binding)
   - Defines CI fixture-availability requirement
   - Lock 10.2 amended with explicit read-side isolation clause

2. **Step 2 — Symmetric retrofit PR** (Claude Code, implementation only)
   - All three fire scripts (2b, 2c, 2d) updated together to
     read from the fixture root in stub mode
   - Live mode read behavior unchanged
   - Fire-script tests updated; a clean-checkout `--stub` exit-0
     transcript captured for each

**Sequencing:** D7 sign-off → mini scope lock v2.1 → retrofit PR →
D8. The mini scope lock and the retrofit PR MUST be two separate
reviewable units; do not merge design + implementation.

**Required audit-trail entry in the D7 sign-off document:**

```
Codex Stage 2c HIGH observation: stub read-side isolation
  Status:    DEFERRED to post-D7 stub fixture retrofit
  Rationale: scope lock v2.1 patch + symmetric retrofit across 2b/2c/2d
  Owner:     pre-D8 phase entry
  Tracking:  docs/d7_stage2d/D7_STAGE2D_IMPLEMENTATION_PLAN.md §10.1
```

This Codex finding MUST be recorded as **DEFERRED, not RESOLVED**,
in the D7 sign-off audit trail. "Resolved" would read as dismissed
to a future auditor; this finding is a real design debt being
consciously rolled forward.

### 10.2 Implementation-Plan Text Typos (Applied)

Two checklist text typos surfaced during cross-artifact review.
Deliverables (the committed JSONs) are correct; only the plan
text in this document was wrong. Both have been applied in-place
to this document so the plan text agrees with the shipped data.

- **2B.19 (§5 checklist):** previously "170 entries"; correct
  count is **171** (= 200 total − 29 Universe A non-null entries,
  which includes pos 116). Verified directly against
  `docs/d7_stage2d/replay_candidates.json`. The plan's own
  parenthetical arithmetic (`199 replay-eligible − 29 + pos 116`)
  also resolves to 171, not 170.
- **2D.14 (§7 checklist):** previously `align=0.90` for pos 74
  Stage 2b; correct value is **0.85**. Verified directly against
  `docs/d7_stage2d/test_retest_baselines.json` (pos 74
  `stage2b.alignment`). Stage 2b signoff §5.3–5.5 does not
  tabulate alignment, so the frozen call record is the
  authoritative source.

These fixes are documentation-only; no code, test, or JSON
artifact is affected.

---

**End of Stage 2d Implementation Plan (v2).**

**Commit this document at:**
`docs/d7_stage2d/D7_STAGE2D_IMPLEMENTATION_PLAN.md`

Upon commit, this plan becomes the authoritative playbook for
executing Tasks 2A through 2D under the two-stage per-task review
gate (Claude Code self-audit + Codex review) followed by a single
Final Advisor Acceptance Verdict covering cross-task integrity.

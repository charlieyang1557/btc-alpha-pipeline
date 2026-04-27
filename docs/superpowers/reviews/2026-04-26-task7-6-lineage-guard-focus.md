# Codex Adversarial Re-Review Focus — Task 7.6 Lineage Guard

## What changed since the last review

This re-review covers a contract-closure expansion of Task 7.6. The
original Task 7.6 (commit 5f53ee5) added the production-time guard but
left the consumption-time contract as convention-only. Dual-reviewer
adjudication (ChatGPT + Claude advisor) concluded that closing the
consumption-time contract in this task — rather than deferring to
first-consumer-write time — was the right scope. The new artifacts
under review are:

- `backtest/wf_lineage.py` — shared module containing both
  `enforce_corrected_engine_lineage()` (producer-side, moved from the
  Phase 2C script) and the new `check_wf_semantics_or_raise()`
  (consumer-side helper).
- `tests/test_wf_lineage_guard.py` — now contains 7 tests (3
  producer-side, 4 consumer-side).
- `scripts/run_phase2c_batch_walkforward.py` — refactored to import
  the shared helper + constants from `backtest/wf_lineage.py`.

Review whether the two-sided guard (producer + consumer) closes the
RS hole that the prior review flagged.

## Out of scope (do NOT re-litigate)

- `backtest/engine.py:725-792` (`_TestStartGatedStrategy` class) and
  `backtest/engine.py:902-987` (modified per-window loop). The prior
  Codex review found these TRUSTED across all six attack surfaces.
  This re-review covers only the lineage helpers and refactor.
- T1-T10 regression suite (`tests/test_walk_forward_boundary_semantics.py`,
  T10 in `tests/test_regime_holdout.py`). 10/10 PASS, prior review
  validated coverage adequacy.
- Fixture code under `tests/fixtures/wf_boundary/`. Sealed.

**Context:** Task 7.5 returned NOT_TRUSTED because
`scripts/run_phase2c_batch_walkforward.py` recorded the current HEAD SHA
into `walk_forward_summary.json` but never checked that HEAD contained
the corrected WF engine commit `eb1c87f` (`fix(engine): WF gated wrapper
implements Q2 (iii)`). Two pre-correction Phase 2C summaries
(`git_sha=0531741`) were already on disk reporting `runtime_status=ok`
for 198 candidates, indistinguishable at the artifact layer from
corrected reruns. Section RS of
`docs/decisions/WF_TEST_BOUNDARY_SEMANTICS.md` says no DSR / PBO / CPCV /
MDS / shortlist decision may consume pre-correction WF outputs.

Task 7.6 adds the minimum mechanical guard. The contract-closure
expansion (this re-review) adds the matching consumer-side helper and
relocates both helpers + constants into a shared module. This review is
to determine whether the two-sided guard (producer + consumer) closes
the hole.

---

## What was implemented (concrete enumeration)

**File: `backtest/wf_lineage.py` (new)**

- Module-level constants `CORRECTED_WF_ENGINE_COMMIT = "eb1c87f"` and
  `WF_SEMANTICS_TAG = "corrected_test_boundary_v1"` — single source of
  truth.
- `enforce_corrected_engine_lineage()` — producer-side helper, moved
  unchanged from `scripts/run_phase2c_batch_walkforward.py` (sans the
  leading underscore — now a public API on the shared module). Resolves
  `git rev-parse HEAD`, then runs `git merge-base --is-ancestor eb1c87f
  HEAD`. Non-zero rc → `sys.exit()` with a Section-RS-tagged error;
  success → return the SHA.
- `check_wf_semantics_or_raise(summary, *, artifact_path=None)` —
  NEW consumer-side helper. Validates that `summary["wf_semantics"]
  == WF_SEMANTICS_TAG` and `summary["corrected_wf_semantics_commit"]
  == CORRECTED_WF_ENGINE_COMMIT`. Three failure branches (missing
  tag, wrong tag, wrong commit), each raising ValueError with a
  Section-RS reference plus expected and actual values. Does NOT gate
  on `lineage_check` (auditor breadcrumb only).

**File: `scripts/run_phase2c_batch_walkforward.py` (modified)**

- Local `CORRECTED_WF_ENGINE_COMMIT`, `WF_SEMANTICS_TAG`, and
  `_enforce_corrected_engine_lineage()` definitions REMOVED. Imports
  the shared module instead:
  `from backtest.wf_lineage import enforce_corrected_engine_lineage,
  CORRECTED_WF_ENGINE_COMMIT, WF_SEMANTICS_TAG`.
- `main()` now calls `head_sha = enforce_corrected_engine_lineage()`
  (public API; underscore dropped).
- Lines 977-991 (modified `_resolve_output_dir`): default output dir is
  now `data/phase2c_walkforward/<batch_id>_corrected/` (was
  `data/phase2c_walkforward/batch_<batch_id>/`). The `--output-dir`
  override is unchanged (caller takes full responsibility).
- Lines 700-792 (modified `_build_summary`): added a required
  `head_sha: str` keyword argument. Summary dict now additionally
  contains four lineage fields:
  - `wf_semantics`: `"corrected_test_boundary_v1"` — load-bearing,
    downstream consumers MUST check this before ingestion via
    `backtest.wf_lineage.check_wf_semantics_or_raise`.
  - `corrected_wf_semantics_commit`: `"eb1c87f"` — auditor-facing.
  - `current_git_sha`: HEAD SHA captured by the guard — auditor-facing.
  - `lineage_check`: `"passed"` — auditor-facing.

**File: `tests/test_wf_lineage_guard.py` (modified, 7 tests)**

- 3 producer-side tests (renamed to import from
  `backtest.wf_lineage`; `subprocess` mock targets updated to
  `backtest.wf_lineage.subprocess.*`):
  - `test_guard_accepts_descendant_head` — mocks `subprocess.call`
    rc=0, asserts the SHA is returned.
  - `test_guard_rejects_pre_correction_head` — mocks rc=1, asserts
    `SystemExit` with both `eb1c87f` and "Section RS" in the message.
  - `test_guard_rejects_outside_git_repo` — mocks `check_output` to
    raise `CalledProcessError`, asserts `SystemExit` with
    "cannot resolve HEAD".
- 4 consumer-side tests (NEW):
  - `test_check_wf_semantics_passes_on_correct_summary` — well-formed
    summary passes silently.
  - `test_check_wf_semantics_raises_on_missing_tag` — missing
    `wf_semantics` field raises ValueError, message contains
    "missing", "Section RS", and the artifact_path.
  - `test_check_wf_semantics_raises_on_wrong_tag` — wrong
    `wf_semantics` value raises ValueError, message contains both
    actual and expected tags plus "Section RS".
  - `test_check_wf_semantics_raises_on_wrong_commit` — mismatched
    `corrected_wf_semantics_commit` raises ValueError, message
    contains both commits plus "Section RS".

**Quarantine (carried over from original Task 7.6):**
- `data/phase2c_walkforward/batch_b6fcbf86-4d57-4d1f-ae41-1778296b1ae9/`
  → moved to
  `data/quarantine/pre_correction_wf/batch_b6fcbf86-4d57-4d1f-ae41-1778296b1ae9_STALE_PRE_CORRECTION/`.
- `data/phase2c_walkforward/batch_b6fcbf86-4d57-4d1f-ae41-1778296b1ae9_tier3_snapshot/`
  → moved to
  `data/quarantine/pre_correction_wf/batch_b6fcbf86-4d57-4d1f-ae41-1778296b1ae9_tier3_snapshot_STALE_PRE_CORRECTION/`.
- `data/quarantine/pre_correction_wf/README.md` written, citing Section RS.

---

## Step 5a classification result (full)

The classifier ran against `data/phase2c_walkforward/batch_*/`:

```
PRE-CORRECTION (quarantine): data/phase2c_walkforward/batch_b6fcbf86-4d57-4d1f-ae41-1778296b1ae9/ (sha=0531741)
PRE-CORRECTION (quarantine): data/phase2c_walkforward/batch_b6fcbf86-4d57-4d1f-ae41-1778296b1ae9_tier3_snapshot/ (sha=0531741)
```

No NO-SHA entries. No POST-CORRECTION entries (the corrected re-run has
not been executed yet — it is Task 8's responsibility). Both
pre-correction directories have been quarantined.

---

## Attack surface (a) — Bypass paths

Concrete things to verify a hostile / careless invocation cannot do:

1. **Env var bypass.** The guard takes no env-var off switch. Confirm
   no `os.environ.get("SKIP_LINEAGE_CHECK")` or similar early-return is
   present.
2. **`--force` flag.** The pre-existing `--force` flag controls only
   CSV overwrite protection, not the lineage guard. Verify it does NOT
   short-circuit `enforce_corrected_engine_lineage()`.
3. **Monkey-patching.** A user could override
   `enforce_corrected_engine_lineage` from a sibling shell, but that
   requires deliberate code modification (not a "happy-path bypass").
   Confirm the helper is called inside `main()` and not behind a
   conditional that can be skipped.
4. **Alternate entrypoint.** The script's only `if __name__ == "__main__"`
   path goes through `main()`. Verify that no other module imports
   `_run_walk_forward_loop` or `_build_summary` directly to write a
   summary JSON without first calling the guard. Check by `grep`:
   `rg "_run_walk_forward_loop|_build_summary" --type py` — should
   show only intra-script self-reference.
5. **Inner-function direct call.** A consumer notebook or test could
   call `run_walk_forward()` directly (the engine function) and write
   its own summary. The guard cannot prevent that — it lives in the
   batch script, not the engine. **This is by design** (the engine is
   sealed under Task 7.6 — sealed-files list). The mitigation is
   downstream: every consumer MUST call
   `check_wf_semantics_or_raise()` before ingesting the summary
   (Attack Surface c3). With this re-review's expansion, the helper
   is now importable; it is no longer convention-only.
6. **Order-of-operations.** Guard runs *before* `parse_args()`. A user
   passing `--help` will currently still hit the guard. Decide whether
   that is acceptable (it is — the guard is cheap, and reading help on
   a pre-correction tree without warning would be misleading).

## Attack surface (b) — Edge cases

1. **Detached HEAD.** `git rev-parse HEAD` works in detached state and
   `merge-base --is-ancestor` works against any commit-ish. Confirm a
   detached HEAD pointing at a descendant of `eb1c87f` passes; one
   pointing at an ancestor fails. The guard does not assume a branch.
2. **Worktrees.** `git rev-parse HEAD` and `merge-base` are
   per-worktree. A worktree on a stale branch will fail the guard
   correctly. Confirm CWD is not assumed to be the project root —
   `subprocess.call(["git", "merge-base", ...])` runs in the script's
   CWD; if the user runs the script from `/tmp` it will fail. Check
   whether this is a real concern or whether the script's existing
   `PROJECT_ROOT = Path(__file__).resolve().parent.parent` makes CWD
   irrelevant.
3. **Shallow clones.** `git merge-base --is-ancestor eb1c87f HEAD` on
   a shallow clone that does not contain `eb1c87f` will error (commit
   not found) → rc != 0 → guard rejects. **This is correct behavior.**
   But: would a CI environment with a shallow clone be falsely
   rejected even when the corrected commit IS in HEAD's ancestry?
   The fetch depth needed to include `eb1c87f` is the depth from HEAD
   to that commit. Verify the prompt notes this as a CI deployment
   consideration.
4. **Uncommitted changes.** `git rev-parse HEAD` reports the committed
   SHA, ignoring working-tree edits. So a user with local edits to
   `backtest/engine.py` (e.g., reverting the fix) on a HEAD descended
   from `eb1c87f` will pass the guard but produce pre-correction
   results. **The guard cannot detect this.** Mitigation: this is what
   the regression test suite (Task 6) is for. Verify the prompt notes
   this as an out-of-scope gap.
5. **`git rev-parse HEAD` returning empty.** Theoretically impossible
   on a healthy repo, but `subprocess.check_output` would return ""
   which `.strip()` keeps as "". The guard's `merge-base --is-ancestor`
   call would then receive an empty HEAD argument and fail. Verify the
   prompt asks whether this case should be explicitly rejected.
6. **CI vs local execution.** Identical mechanism. CI must clone with
   sufficient depth; otherwise behaves identically.

## Attack surface (c1) — Producer-side guard

(Findings carried over from original Task 7.6 review.)

1. **Helper presence and call site.** The producer-side guard is now
   defined in `backtest/wf_lineage.py` as
   `enforce_corrected_engine_lineage()` (public API; the leading
   underscore was dropped on the move). The Phase 2C script calls
   it once at the top of `main()` before `parse_args()`. Verify no
   alternate code path skips this call.
2. **Constant bindings.** `CORRECTED_WF_ENGINE_COMMIT` and
   `WF_SEMANTICS_TAG` are defined at module-level in
   `backtest/wf_lineage.py` and imported by the producer. Verify the
   script does not redefine or shadow these names locally.
3. **Subprocess invocation.** `subprocess.call(["git", "merge-base",
   "--is-ancestor", CORRECTED_WF_ENGINE_COMMIT, "HEAD"])` is the
   actual ancestry check. Verify this command is correct (note: the
   command form `git merge-base --is-ancestor <ancestor> <descendant>`
   returns 0 iff the first arg is an ancestor of the second).

## Attack surface (c2) — Artifact metadata + registry gap

(Findings carried over from original Task 7.6 review.)

The four lineage fields stamped into `walk_forward_summary.json`
(`wf_semantics`, `corrected_wf_semantics_commit`, `current_git_sha`,
`lineage_check`) are the only metadata produced by the script. The
SQLite experiment registry (`backtest/experiments.db`) has no
`wf_semantics` column; runs from this batch script are not currently
registered there.

**Implications:**

- A future shortlist tool that joins the WF summary with experiment
  registry rows can rely on `wf_semantics` from the JSON, but cannot
  rely on a registry-side guard.
- If Task 8 introduces a registry-write path for these batches, the
  registry schema needs a parallel `wf_semantics` column AND a parallel
  consumer-side check. Verify the prompt asks whether this should be
  flagged with a CONTRACT GAP marker at the producer's `wf_semantics`
  field site, with trigger condition: "when WF batch results are
  written to `experiments.db`, the registry schema MUST add a
  `wf_semantics` column and `check_wf_semantics_or_raise` MUST be
  exercised against registry rows before consumption."

## Attack surface (c3) — Consumer-side helper (NEW)

This is the new surface. Verify:

1. **Helper signature.** `check_wf_semantics_or_raise(summary: dict, *, artifact_path: str | Path | None = None) -> None` — does the kwargs-only artifact_path provide enough flexibility for both file-loaded and inline-dict callers?

2. **Field coverage.** The helper checks `wf_semantics` AND `corrected_wf_semantics_commit`. Could a malformed artifact bypass both checks (e.g., one field correct, the other missing)? Trace the three branches.

3. **Error diagnostics.** Each error message contains: the offending field's actual value (or "missing"), the expected value, the artifact path (if provided), and a Section RS reference. Verify all three branches include all four pieces.

4. **Exception type choice.** ValueError (not SystemExit, not RuntimeError). Why ValueError? Because the failure mode is "input data violates a contract" — that's semantically ValueError. SystemExit would be rude inside notebooks/test harnesses; RuntimeError is for runtime-state failures. Verify this choice is consistent with how the helper would be called from a future DSR/PBO/CPCV/MDS/shortlist consumer.

5. **No load-bearing behavior on `lineage_check` field.** The auditor metadata field `lineage_check: "passed"` is intentionally NOT gated. Verify this is the right call (it should be — the field is breadcrumb only, not contract).

6. **Bypass paths to the helper.** Could a future consumer skip the helper entirely (just `json.load` and use the dict)? The helper is convention to call; the contract is "consumers MUST call it." Is there a way to make it harder to skip? (Note: full enforcement is impossible in Python without type-checking infrastructure; the goal here is to make skipping VISIBLE, not impossible.)

## Attack surface (d) — Quarantine completeness

**Step 5a inventory (run for original Task 7.6):** only the two known
directories under `data/phase2c_walkforward/batch_*/` carried
pre-correction artifacts. Both are now quarantined. After quarantine,
`data/phase2c_walkforward/` is empty.

**Concerns to verify:**

1. **Glob-pattern bypass.** Does any code glob
   `data/phase2c_walkforward/**` rather than `batch_*_corrected/`?
   `grep -rn 'phase2c_walkforward' --include="*.py" --include="*.ipynb"`
   shows only the producer script (which writes new corrected paths)
   and doc references. No consumer globs the directory. But: a future
   consumer could blindly glob `data/phase2c_walkforward/batch_*/` and
   silently include any pre-correction artifact that escapes
   quarantine. **The new consumer-side helper mitigates this:** any
   such consumer calling `check_wf_semantics_or_raise()` will reject
   the stale artifact at load time.
2. **Other pre-correction artifact locations.** Are there WF artifacts
   outside `data/phase2c_walkforward/`? Check
   `data/results/`, `backtest/experiments.db`, anywhere else.
   `data/results/` holds per-run trade CSVs (single-run engine output,
   not WF aggregates). `backtest/experiments.db` holds the run
   registry — it has rows for `walk_forward_summary` runs, but those
   are SQLite rows with no `wf_semantics` column. (See Attack
   Surface c2.)
3. **Pre-correction artifacts re-introduced via git history.** The
   `git log` shows commits prior to `eb1c87f` that may have touched
   the engine. If anyone runs the corrected script from a worktree on
   an old branch (Attack Surface b.2), the guard catches it. Confirmed.
4. **Phase 1B rerun script (Step 4a).** Discovery returned no Phase 1B
   rerun script. The Task 7.6 commit message documents this and defers
   the guard to Task 8. Verify the prompt asks whether this deferral
   is acceptable or whether a stub script should be created now to
   carry the guard.

---

## Verdict bar

- **TRUSTED** if the production-time guard, artifact metadata, AND
  consumption-time helper TOGETHER close the RS failure mode. All
  three sides must hold:
  - Production guard: cannot bypass via env var, --force, alternate
    CLI flag, or monkey-patch in main().
  - Artifact metadata: every walk_forward_summary.json produced by
    main() includes `wf_semantics`, `corrected_wf_semantics_commit`,
    `current_git_sha`, `lineage_check`.
  - Consumption helper: `check_wf_semantics_or_raise()` correctly
    rejects (a) missing wf_semantics, (b) wrong wf_semantics, (c)
    wrong corrected_wf_semantics_commit. Each error message includes
    Section RS reference + expected + actual.
  - Stale artifacts: the two pre-correction directories are physically
    moved to `data/quarantine/pre_correction_wf/...STALE_PRE_CORRECTION`.
  - Tests: 7/7 pass (3 producer + 4 consumer); each test asserts
    message content (not just exception type).

- **ITERATE_REQUIRED** if any of:
  - A concrete bypass path exists in the production guard (specific
    env var, flag, function, or refactor that lets pre-correction
    artifacts be produced).
  - A future consumer can plausibly ingest a stale artifact without
    a code-level enforcement helper available to call (the helper
    must exist, be importable, and be the obvious call to make).
  - The consumption helper has a concrete bypass that defeats its
    purpose (a malformed artifact passes all three checks; the
    helper raises the wrong exception type for the use case; the
    error message lacks diagnostic content).
  - Quarantine is incomplete (a pre-correction artifact remains
    discoverable under `data/phase2c_walkforward/`).

- **NOT_TRUSTED** only if stale artifact production OR consumption
  remains concretely reproducible after the fix. Provide a specific
  reproducer (commands or code).

---

## Attack surface (e) — Regression coverage of the helpers

The 7 unit tests for the helpers mock at the subprocess and dict
level. They verify CURRENT correctness but may not catch FUTURE
regression where the guard is silently bypassed (e.g., a future PR
adds a `--skip-guard` flag, or a refactor moves the guard call into
a conditional branch). Verify:

- Are the 7 unit tests sufficient to catch a silent-bypass regression?
- Is there an integration test (or could there be one, cheaply) that
  actually runs the script under a simulated pre-correction HEAD and
  verifies the guard fires?
- Same question for the consumer helper: should there be an
  integration test that loads a real summary file and verifies
  the helper rejects it correctly?

## Attack surface (f) — Quarantine artifact tracked status

Subagent moved the pre-correction directories via plain `mv` (because
the source directories were untracked in git, marked `??` in `git status`).
The moved files are now committed under `data/quarantine/`. Verify:

- Run `git ls-files data/quarantine/` to confirm the artifact files
  themselves (the JSONs and CSVs) are tracked, not just the README.
- If `data/phase2c_walkforward/**` is gitignored (per project
  convention that WF artifacts are regenerable), check whether
  `data/quarantine/pre_correction_wf/**` is also gitignored. If yes,
  the quarantine commit's audit value depends on the README alone —
  is that sufficient?
- Could a fresh clone reconstruct the quarantine state from the
  current commit, or only see the README without the actual artifacts?

## Attack surface (g) — Engine.py docstring confirmation (carryover from Task 2)

The Task 2 classification table identified `backtest/engine.py:740-741`
(now shifted to `engine.py:820-852` after Task 5's wrapper insertion)
as the only "needs update after patch" item — the `run_walk_forward`
docstring that aspirationally said "metrics are computed only on the
test portion" was technically false under the pre-correction engine.
The Task 5 wrapper-implementer updated this docstring in commit
eb1c87f. Verify:

- Does the current `run_walk_forward` docstring (engine.py:820-852)
  accurately describe the corrected (iii) semantic, with no stale
  references to the pre-correction behavior?
- Per spec Q3a, the docstring update closes the only "needs update
  after patch" item from the classification table. Confirm no
  follow-up is required.

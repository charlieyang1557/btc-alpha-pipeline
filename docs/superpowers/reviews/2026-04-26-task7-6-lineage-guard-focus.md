# Codex Adversarial Re-Review Focus — Task 7.6 Lineage Guard

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

Task 7.6 adds the minimum mechanical guard. This review is to determine
whether that guard actually closes the hole.

---

## What was implemented (concrete enumeration)

**File: `scripts/run_phase2c_batch_walkforward.py`**

- Lines 100-167 (new): module-level constants
  `CORRECTED_WF_ENGINE_COMMIT = "eb1c87f"` and
  `WF_SEMANTICS_TAG = "corrected_test_boundary_v1"`, plus
  `_enforce_corrected_engine_lineage()` helper. The helper resolves
  `git rev-parse HEAD`, then runs `git merge-base --is-ancestor eb1c87f
  HEAD`. Non-zero rc → `sys.exit()` with a Section-RS-tagged error;
  success → return the SHA.
- Lines 977-991 (modified `_resolve_output_dir`): default output dir is
  now `data/phase2c_walkforward/<batch_id>_corrected/` (was
  `data/phase2c_walkforward/batch_<batch_id>/`). The `--output-dir`
  override is unchanged (caller takes full responsibility).
- Lines 700-792 (modified `_build_summary`): added a required
  `head_sha: str` keyword argument. Summary dict now additionally
  contains four lineage fields:
  - `wf_semantics`: `"corrected_test_boundary_v1"` — load-bearing,
    downstream consumers MUST check this before ingestion.
  - `corrected_wf_semantics_commit`: `"eb1c87f"` — auditor-facing.
  - `current_git_sha`: HEAD SHA captured by the guard — auditor-facing.
  - `lineage_check`: `"passed"` — auditor-facing.
- Lines 1093-1103 (modified `main()`): calls
  `head_sha = _enforce_corrected_engine_lineage()` before `parse_args()`,
  threads it into `_build_summary(..., head_sha=head_sha)`.

**File: `tests/test_wf_lineage_guard.py` (new, 39 lines)**
- `test_guard_accepts_descendant_head` — mocks `subprocess.call` rc=0,
  asserts the SHA is returned.
- `test_guard_rejects_pre_correction_head` — mocks rc=1, asserts
  `SystemExit` with both `eb1c87f` and "Section RS" in the message.
- `test_guard_rejects_outside_git_repo` — mocks `check_output` to raise
  `CalledProcessError`, asserts `SystemExit` with "cannot resolve HEAD".

**Quarantine:**
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
   short-circuit `_enforce_corrected_engine_lineage()`.
3. **Monkey-patching.** A user could override
   `_enforce_corrected_engine_lineage` from a sibling shell, but that
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
   downstream: every consumer MUST gate on `wf_semantics ==
   "corrected_test_boundary_v1"` (Attack Surface c). Verify the prompt
   raises this as a CONTRACT GAP, not a bypass.
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

## Attack surface (c) — Verification gap (downstream consumption)

**Programmatic consumers of `walk_forward_summary.json` enumeration:**

`grep -rn 'walk_forward_summary.json|walk_forward_results.csv|wf_total_return|wf_sharpe' --include="*.py" --include="*.ipynb"` returns only:

- `scripts/run_phase2c_batch_walkforward.py` — the producer itself.
- `docs/closeout/PHASE2C_5_PHASE1_RESULTS.md` — narrative doc, references
  the now-quarantined paths (lines 237-240); **stale references that
  Task 7.6 did NOT update**.
- `docs/superpowers/plans/2026-04-26-wf-test-boundary-semantics-plan.md`
  and `docs/superpowers/specs/...-design.md` — planning docs, not code.
- `docs/phase2c/PHASE2C_4_PHASE1_PLAN.md` — phase contract doc.

**Finding:** no Python script or notebook currently reads
`walk_forward_summary.json` programmatically. The artifacts are
consumed by humans (closeout report writers) and by the producer
itself.

**Implication for the review:** the load-bearing
`wf_semantics: corrected_test_boundary_v1` field is currently a
**convention only**, not enforced by any consumer code. As soon as
Task 8+ writes the first programmatic consumer (DSR / PBO / CPCV /
MDS / shortlist), that consumer MUST gate on this field. Verify the
prompt asks whether this should be tracked with a `CONTRACT GAP`
marker at the producer's `wf_semantics` field site, with a trigger
condition like "when the first programmatic consumer of
walk_forward_summary.json is added, that consumer MUST refuse to
ingest payloads where `wf_semantics != WF_SEMANTICS_TAG`."

**Stale documentation:** `docs/closeout/PHASE2C_5_PHASE1_RESULTS.md`
references the now-quarantined paths at lines 237-240. Task 7.6 did
not modify that file (it is a historical closeout doc and the spec
is silent on whether to amend it). Verify the prompt asks whether
that doc needs an erratum banner pointing to the quarantine.

## Attack surface (d) — Quarantine completeness

**Step 5a inventory (run today):** only the two known directories
under `data/phase2c_walkforward/batch_*/` carried pre-correction
artifacts. Both are now quarantined. After quarantine,
`data/phase2c_walkforward/` is empty.

**Concerns to verify:**

1. **Glob-pattern bypass.** Does any code glob
   `data/phase2c_walkforward/**` rather than `batch_*_corrected/`?
   `grep -rn 'phase2c_walkforward' --include="*.py" --include="*.ipynb"`
   shows only the producer script (which writes new corrected paths)
   and doc references. No consumer globs the directory. But: a future
   consumer could blindly glob `data/phase2c_walkforward/batch_*/` and
   silently include any pre-correction artifact that escapes
   quarantine.
2. **Other pre-correction artifact locations.** Are there WF artifacts
   outside `data/phase2c_walkforward/`? Check
   `data/results/`, `backtest/experiments.db`, anywhere else.
   `data/results/` holds per-run trade CSVs (single-run engine output,
   not WF aggregates). `backtest/experiments.db` holds the run
   registry — it has rows for `walk_forward_summary` runs, but those
   are SQLite rows with no `wf_semantics` column. **This is a real
   gap:** the lineage guard does not stamp anything into the SQLite
   experiment registry. Verify the prompt asks whether registry rows
   need a parallel guard (Task 8 concern, but should be flagged here).
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

- **TRUSTED** if:
  - The guard cannot be bypassed via env var, `--force`, alternate CLI
    flag, or monkey-patch in `main()`.
  - The `_corrected` suffix path is consistently used (no stale code
    paths writing to `batch_<id>/` without suffix).
  - The four lineage fields are guaranteed to appear in every
    `walk_forward_summary.json` produced by `main()`.
  - The two specific pre-correction directories are physically moved
    to `data/quarantine/pre_correction_wf/...STALE_PRE_CORRECTION` and
    `data/phase2c_walkforward/` is empty of pre-correction artifacts.
  - The unit tests assert message content (`eb1c87f` and "Section RS")
    rather than just `pytest.raises(SystemExit)`.

- **ITERATE_REQUIRED** if any of:
  - A concrete bypass path exists (e.g., a flag I overlooked, an
    importable function that writes a summary without the guard).
  - The guard fires before argparse, breaking `--help` in a way the
    user cannot inspect what flags exist.
  - The four lineage fields can be omitted by an alternate code path.
  - Quarantine is incomplete (a pre-correction artifact remains
    discoverable under `data/phase2c_walkforward/`).
  - The CONTRACT GAP for downstream consumer enforcement is missing
    AND would cause a Section RS violation in Task 8 if not addressed
    before then.
  - Stale `docs/closeout/PHASE2C_5_PHASE1_RESULTS.md` path references
    constitute a real (not nominal) consumption risk that should be
    fixed in this PR.

For each ITERATE_REQUIRED finding, please provide a concrete
reproducer (commands or code) showing the bypass / gap.

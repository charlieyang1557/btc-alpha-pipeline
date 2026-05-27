# G3 — Raw_payloads inventory result

**Verified at:** 2026-05-27T16:14:13Z
**HEAD commit:** b8d6523 (code-state equivalent to f112599)
**Plan reference:** `docs/superpowers/plans/2026-05-27-b-c-narrow-phase-1-pre-impl-gates-plan.md` §"Task 7"
**Spec reference:** `docs/superpowers/specs/2026-05-26-b-c-narrow-data-recovery-design.md` §4.1 G3

## Combined dir symlink counts (Step 7.1)

| Subset | Expected | Actual | Match |
|---|---|---|---|
| `attempt_*` symlinks | 993 | 993 | ✅ |
| `source_stage2d_summary_*.json` symlinks | 5 | 5 | ✅ |
| **TOTAL** | **998** | **998** | ✅ |

Commands used:
- `find raw_payloads/batch_phase2c_15_main_fire_combined -type l | wc -l` → 998
- `find raw_payloads/batch_phase2c_15_main_fire_combined -type l -name "attempt_*" | wc -l` → 993
- `find raw_payloads/batch_phase2c_15_main_fire_combined -type l -name "source_stage2d_summary_*.json" | wc -l` → 5

## Symlink resolution (Step 7.2)

Command: `find raw_payloads/batch_phase2c_15_main_fire_combined -type l ! -exec test -e {} \; -print | head -20`

Output: **empty** — zero broken symlinks.

## Target confinement check (Step 7.2b — PFR R1 LOW F5 fix v2)

Python audit verifying every symlink target resolves under REPO_ROOT and that no symlink uses an absolute-text target:

```
total absolute-text symlinks: 0
off-repo resolved symlinks: 0
```

All 998 symlinks resolve under `/Users/yutianyang/Documents/GitHub/btc-alpha-pipeline/`; all symlink texts are repo-relative (no absolute paths to off-repo / cold-storage mounts).

## 5 cohort_a sub-batch dirs (Step 7.3)

| Batch UUID | Source stage 2d summary symlink | Attempt count (calls field) |
|---|---|---|
| `355a8f9f-2a1f-435d-a1a8-c365b92e185b` | source_stage2d_summary_355a8f9f-2a1f-435d-a1a8-c365b92e185b.json | 200 |
| `4f894318-eb69-48b5-95ef-e22abe3ecdd1` | source_stage2d_summary_4f894318-eb69-48b5-95ef-e22abe3ecdd1.json | 200 |
| `71d42a07-d88f-431a-a653-601010cf1921` | source_stage2d_summary_71d42a07-d88f-431a-a653-601010cf1921.json | 200 |
| `91ad68ed-6470-45a7-8735-171c39ff25c3` | source_stage2d_summary_91ad68ed-6470-45a7-8735-171c39ff25c3.json | 200 |
| `a12c2a65-4314-4dde-be6e-968a0c70ee6e` | source_stage2d_summary_a12c2a65-4314-4dde-be6e-968a0c70ee6e.json | 200 |
| **TOTAL** | 5 summaries | **1000 calls** (993 realized as attempt symlinks; 7 calls did not produce response files — expected for refused/parse-fail entries) |

## Verdict

All 3 sub-checks pass:
- Counts match (998 = 993 + 5).
- Zero broken symlinks.
- Zero off-repo / absolute-text symlinks.

**G3 = PASS** → proceed to Task 8.

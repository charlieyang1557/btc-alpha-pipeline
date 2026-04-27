# D7 Stage 2d — Patch 3e Acceptance Note (Pre-Live Readiness)

**Purpose:** seal the 3e arc and confirm the fire script is live-fire
safe at HEAD `0a72bfd`. This note supersedes the 3d.4 acceptance note
for pre-fire readiness; the hard contracts ratified there are preserved
and re-verified here.

**Scope:** acceptance verification only. 3e.3 was intentionally skipped
after a targeted blocker check (see §"3e.3 disposition" below). No new
feature work in 3e.4.

---

## HEAD state at acceptance

```
0a72bfd D7 Stage 2d: 3e.2 fire-script test coverage (21 pytest cases)
91c949f D7 Stage 2d: 3e.1 assert→Stage2dStartupError + stale-reference cleanup
e1cf27e D7 Stage 2d: 3d.4 acceptance verification (3d arc closed)
6ef6aa6 D7 Stage 2d: 3d.3 stage2c_archive_sha256_by_file (final Stage 2d aggregate addition)
dc289fa D7 Stage 2d: 3d.2 checkpoint_log aggregate field (§10.3 amendment + script)
4d107d4 D7 Stage 2d: 3d.1 HG20 input-drift guard (Path II builder-owned finalization)
0b9b28c D7 Stage 2d: 3d.0 spec amendment — §10.1/§10.2 Direction B resolution
9b598a6 D7 Stage 2d: 3c fix-forward — startup audit envelope (§13.3 conformance)
9a4ad0e feat(stage2d): expand fire-script aggregate to 49-key 3c target
```

Working tree at acceptance time: clean against tracked files (apart
from `.DS_Store` noise and two untracked `docs/d7_stage2c/*.md` audit
scratches, both out of 3e scope — same as at 3d.4 acceptance).

---

## Pre-live readiness verification

### Three-leg acceptance run

```
rm -rf dryrun_payloads/dryrun_stage2d
python scripts/run_d7_stage2d_batch.py --stub            # EXIT 0
python -m pytest tests/test_run_d7_stage2d_batch.py -q   # 21 passed in 0.55s
python scripts/stage2d_self_check.py                     # EXIT 0, 28/28 PASS
```

### Stub artifact shape (all contracts hit)

| # | Invariant | Observed | Verdict |
|---|---|---|---|
| 1 | Aggregate key count (non-drift) | 51 | PASS |
| 2 | `write_completed_at` is literal last key (Lock 11 tail) | ✓ | PASS |
| 3 | Startup audit key count (Lock 13 envelope) | 9 | PASS |
| 4 | `per_call_records` length | 200 | PASS |
| 5 | `critic_status_counts` | `{"ok": 199, "d7b_error": 0, "skipped_source_invalid": 1}` | PASS |
| 6 | `checkpoint_log` trigger indices | `[50, 100, 150]` | PASS |
| 7 | `stage2c_archive_sha256_by_file` present (stub value None) | True | PASS |
| 8 | HG20 fields absent on non-drift path | `hg20_drift_detected` False, `selection_json_sha256_end` False | PASS |
| 9 | `scripts/stage2d_self_check.py` 28 counted gates | 28 PASS, 0 WARN, 0 FAIL, 0 SKIP | PASS |
| 10 | `tests/test_run_d7_stage2d_batch.py` | 21/21 PASS (0.55s) | PASS |

Drift-path coverage (53 keys; `hg20_drift_detected` and
`selection_json_sha256_end` appended): ratified at 3d.4 against HEAD
`6ef6aa6`, preserved through 3e.1 (no builder changes) and covered by
`test_build_aggregate_record_drift_writes_53_keys_on_disk` in 3e.2.
Not re-executed in this note.

---

## 3e arc disposition

### 3e.1 — committed (`91c949f`, 16th Stage 2d commit)

Scope:
- Line 1981: bare `assert len(candidates) == STAGE2D_SOURCE_N` → structured
  `raise Stage2dStartupError("HG1b: candidate count drift after startup gates. Expected 200, got … from …")`.
- Four stale future-tense / past-plan references cleaned up (module
  docstring line 20, dataclass comment line 299, `_build_normal_per_call_record`
  docstring line 906, `run_stage2d` docstring line 1960).

Invariant preserved: same drift condition still fails the run; diagnostic
envelope upgraded from `AssertionError` to `Stage2dStartupError`.

### 3e.2 — committed (`0a72bfd`, 17th Stage 2d commit)

Scope: new `tests/test_run_d7_stage2d_batch.py` (605 LOC, 21 pytest
cases, 0.55s). **F1 coverage gap** identified in 3c review and deferred
through the entire 3d arc — **now closed.**

Coverage map:
- `_synthesize_pos116_record` (Lock 1.5 17-key shape + position guard)
- `_build_checkpoint_log` (empty / below-first / partial-149 / full-200)
- `_compute_stage2c_archive_sha256_by_file` (stub no-FS + live sorted-SHA
  dict with synthetic 60-file fixture)
- `build_aggregate_record` non-drift 51 / drift 53 + HG20 coupled-kwargs
  guards (both halves)
- `should_abort` Lock 7 vocab (rules a/b/c/d/e + pos-116 bypass + rule-g)
- HG1b reload drift (the 3e.1 Stage2dStartupError raise site)
- `--stub` subprocess integration smoke

Discipline held: test-only patch; real tempdir files; real builder
invocations; direct `pytest.raises(..., match=...)`; no mocks of units
under test.

### 3e.3 — skipped (disposition)

Per 3e.0 polish inventory, three items were candidates:

- Q1 `inter_call_sleep_seconds` field rename — polish, not blocker.
- Q2 `_classify_d7b_error` tuning vs Stage 2c precedent — polish, not blocker.
- Q3 `raw_payload_paths` stricter verification — **targeted blocker check below.**

**Q3 blocker check (required before skipping 3e.3):** can
`raw_payload_paths` ever claim a path not actually written, in a way
that would matter for live adjudication?

```
# scripts/run_d7_stage2d_batch.py
1045:    prompt_path = critic_dir / f"call_{position:04d}_prompt.txt"
1046:    prompt_path.write_text(prompt_text, encoding="utf-8")     # written before claim
…
1084:    result_path = critic_dir / f"call_{position:04d}_critic_result.json"
1085:    result_path.write_text(…)                                  # written before claim
1092:    raw_payload_paths = {
1093:        "prompt": str(prompt_path),
1094:        "response":  str(response_path)  if response_path.exists()  else None,
1095:        "traceback": str(traceback_path) if traceback_path.exists() else None,
1096:        "critic_result": str(result_path),
1097:    }
```

- `prompt` and `critic_result`: unconditional claims, but both files
  are physically written immediately before the dict is constructed.
- `response` and `traceback`: already guarded by `.exists()` — only
  claimed when present on disk.

**Conclusion:** no path in `raw_payload_paths` can be claimed for a file
that was not actually written. Live-adjudication integrity is intact.
Q3 is harmless polish. All three 3e.3 candidates are polish — **3e.3
dropped.**

Non-blocking polish explicitly waived (may return in a later phase, not
gating live fire):
- `inter_call_sleep_seconds` rename
- `_classify_d7b_error` tuning vs Stage 2c classifier
- `# Patch 3:` annotation final sweep
- Q2 `stratum_breakdown` deep-dive-only code comment
- four remaining pre-startup bare asserts (lines 1835, 1842, 1857, 1867
  — classified "keep" at 3e.0 because they guard plumbing preconditions
  that cannot realistically trip in practice)

### 3e.4 — this note

No code changes. Acceptance verification only.

---

## Live-fire readiness checklist (summary)

| Item | Status |
|---|---|
| Current HEAD | `0a72bfd` |
| Working tree | clean vs tracked files |
| Stub acceptance (fresh slate) | GREEN |
| pytest `tests/test_run_d7_stage2d_batch.py` | 21/21 PASS |
| `scripts/stage2d_self_check.py` | 28/28 PASS, EXIT 0 |
| Aggregate schema — non-drift | 51 keys, Lock 11 tail-append holds |
| Aggregate schema — drift | 53 keys (ratified at 3d.4, builder-direct) |
| Startup audit envelope | 9 keys (Lock 13) |
| Normal per-call record | 32 keys |
| Pos 116 synthetic record | 17 keys (Lock 1.5 + Layer B) |
| Checkpoint trigger tuple | `(50, 100, 150)` |
| HG20 symmetric guards | asserted in tests (both halves raise) |
| HG1b reload drift raise site | structured `Stage2dStartupError` + covered by test |
| `raw_payload_paths` integrity | no path claimed without being written |
| Remaining polish items | explicitly waived (non-blocking) |
| Production ledger `agents/spend_ledger.db` | untouched (stub isolation) |
| Production `raw_payloads/batch_5cf76668-.../critic/` | zero `stage2d_*` contamination |

The fire script is ready for the §16 pre-fire checklist and live-fire
authorization. No further polish is planned before that.

---

## Out of scope for 3e.4 (confirmed not touched)

- `config/environments.yaml`, `config/execution.yaml`, `config/schemas.yaml` — unchanged.
- `backtest/experiments.db` — unchanged.
- `agents/spend_ledger.db` — unchanged.
- Production `raw_payloads/batch_5cf76668-.../critic/` — zero `stage2d_*` contamination.
- `strategies/`, `factors/`, `ingestion/`, `backtest/` engine code — unchanged.
- No code changes to `scripts/run_d7_stage2d_batch.py` in 3e.4.
- No changes to the design spec in 3e.4.

---

## Next: §16 pre-fire checklist → live-fire authorization

After this note commits, the 3e arc is sealed. The next sessions are:

1. Stub dry-run acceptance session walking the §16 pre-fire checklist.
2. Live fire (requires explicit `--confirm-live` from Charlie).

No further implementation or polish is expected before live fire.

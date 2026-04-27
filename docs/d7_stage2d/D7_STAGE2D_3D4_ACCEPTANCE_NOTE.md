# D7 Stage 2d — Patch 3d.4 Acceptance Note

**Purpose:** seal the 3d arc by proving the fire script matches the
ratified aggregate contract at HEAD (`6ef6aa6`, 3d.3 shipped).

**Scope:** acceptance verification only. No new feature work. No polish.
No new tests. 3e begins after this note is committed.

---

## HEAD state at acceptance

```
6ef6aa6 D7 Stage 2d: 3d.3 stage2c_archive_sha256_by_file (final Stage 2d aggregate addition)
dc289fa D7 Stage 2d: 3d.2 checkpoint_log aggregate field (§10.3 amendment + script)
4d107d4 D7 Stage 2d: 3d.1 HG20 input-drift guard (Path II builder-owned finalization)
0b9b28c D7 Stage 2d: 3d.0 spec amendment — §10.1/§10.2 Direction B resolution
9b598a6 D7 Stage 2d: 3c fix-forward — startup audit envelope (§13.3 conformance)
9a4ad0e feat(stage2d): expand fire-script aggregate to 49-key 3c target
```

Working tree at acceptance time: clean against tracked files (apart
from `.DS_Store` noise and two untracked `docs/d7_stage2c/*.md` audit
scratches, both out of 3d.4 scope).

---

## Stub acceptance run

Fresh invocation after clean slate:

```
rm -rf dryrun_payloads/dryrun_stage2d
python scripts/run_d7_stage2d_batch.py --stub     # EXIT 0
```

### Stub-path verification bundle (all PASS)

| # | Check | Observed | Verdict |
|---|---|---|---|
| 1 | Aggregate key count | 51 | PASS |
| 2 | `write_completed_at` is literal last key | ✓ | PASS |
| 3 | Startup audit key count | 9 | PASS |
| 4 | `per_call_records` length | 200 | PASS |
| 5 | `critic_status_counts` | `{"ok": 199, "d7b_error": 0, "skipped_source_invalid": 1}` | PASS |
| 6 | `checkpoint_log` exists | True | PASS |
| 7 | `checkpoint_log` call indices | `[50, 100, 150]` | PASS |
| 8 | `stage2c_archive_sha256_by_file` present | True | PASS |
| 9 | `stage2c_archive_sha256_by_file` value (stub) | `None` | PASS |
| 10 | HG20 fields absent on non-drift | `hg20_drift_detected` False, `selection_json_sha256_end` False | PASS |
| 11 | Pos 116 record key count | 17 | PASS |
| 12 | Pos 116 record `critic_status` | `skipped_source_invalid` | PASS |
| 13 | Normal record key count (sampled pos 115 → record[114]) | 32 | PASS |
| 14 | Normal record `critic_status` (sampled) | `ok` | PASS |
| 15 | Production ledger `agents/spend_ledger.db` untouched | mtime unchanged (Apr 19 07:30) | PASS |
| 16 | Production `raw_payloads/batch_5cf76668-.../critic/` has no `stage2d_*` entries | 0 matches | PASS |
| 17 | `scripts/stage2d_self_check.py` | `SUMMARY (28 counted gates): 28 PASS, 0 WARN, 0 FAIL, 0 SKIP | EXIT 0` | PASS |

Startup audit top-level keys confirmed as the 9-key Lock 13 envelope:

```
['stage_label', 'batch_uuid', 'mode', 'startup_gates_passed',
 'startup_completed_at_utc', 'git_head', 'python_version',
 'os_platform', 'startup_audit']
```

---

## Drift-path acceptance rerun

Rerun of the 3d.3 Round 1 builder-direct drift execution (not a
runtime fire — the main loop has no drift-injection hook; this is a
direct `build_aggregate_record(…, hg20_drift_detected=True,
selection_json_sha256_end=…)` invocation against the stub run's
`per_call_records` + `replay_candidates.json`).

Stub-mode `Stage2dConfig` redirected to a tempdir so the drift
aggregate is atomic-written without clobbering the canonical stub
artifact. SHA fields normally filled by startup gates were backfilled
from the stub audit.

### Drift-path verification bundle (all PASS)

| # | Check | Observed | Verdict |
|---|---|---|---|
| 1 | Drift aggregate on-disk key count | 53 | PASS |
| 2 | `write_completed_at` is literal last key | ✓ | PASS |
| 3 | `hg20_drift_detected` present exactly once, value `True` | count=1 | PASS |
| 4 | `selection_json_sha256_end` present exactly once | count=1 | PASS |
| 5 | `stage2c_archive_sha256_by_file` present on drift path | True | PASS |
| 6 | `stage2c_archive_sha256_by_file` value unchanged vs stub | `None` == `None` | PASS |

The stub/drift invariance of `stage2c_archive_sha256_by_file` is
empirical (same `None` observed on both paths under stub-mode
config), not merely structural — this is the verification elevation
ChatGPT mandated during the 3d.3 Round 1 review.

---

## 3d arc closure

Aggregate target reached at HEAD:

- **Non-drift base**: 51 keys
- **Drift total**: 53 keys
- **10 Stage 2d additions** shipped across 3d.0–3d.3:
  1. `critic_status_counts`
  2. `stratum_breakdown`
  3. `deep_dive_candidates_sha256`
  4. `test_retest_baselines_sha256`
  5. `label_universe_analysis_sha256`
  6. `checkpoint_log` (3d.2)
  7. `stage2c_archive_sha256_by_file` (3d.3)
  8. `stage2d_skipped_positions`
  9. `stage2d_live_d7b_call_n`
  10. `stage2d_source_n`

HG20 conditional additions (`selection_json_sha256_end`,
`hg20_drift_detected`) shipped in 3d.1 via Path II
builder-owned finalization.

No spec amendment is required from 3d.4 — every ratified behavior is
already captured by the post-3d.3 state of
`docs/d7_stage2d/run_d7_stage2d_batch_design_spec.md`.

---

## Out of scope for 3d.4 (confirmed not touched)

- `config/environments.yaml`, `config/execution.yaml`, `config/schemas.yaml` — unchanged.
- `backtest/experiments.db` — unchanged.
- `agents/spend_ledger.db` — unchanged (pre-acceptance mtime Apr 19 07:30 preserved).
- Production `raw_payloads/batch_5cf76668-.../critic/` — zero `stage2d_*` contamination.
- `strategies/`, `factors/`, `ingestion/`, `backtest/` engine code — unchanged.
- No new tests (F1 test infrastructure deferred to 3e).
- No code changes to `scripts/run_d7_stage2d_batch.py` or the design spec.

---

## Next: 3e polish begins

Deferred items tracked for 3e, out of scope here:

- Bare `assert` → `Stage2dStartupError` migration.
- `inter_call_sleep_seconds` field rename (if still desired).
- `_classify_d7b_error` tuning vs Stage 2c precedent.
- `raw_payload_paths` stricter verification.
- `# Patch 3:` annotation cleanup.
- Q2 `stratum_breakdown` deep-dive-only code comment.
- **F1 mandatory**: stand up `tests/test_run_d7_stage2d_batch.py` with
  ~30 tests porting the scattered inline verifications (should_abort,
  HG20 drift, checkpoint_log, stage2c_archive_sha256_by_file, stub
  smoke, aggregate field-count + schema assertions).

After 3e: stub dry-run acceptance session → live fire (explicit
`--confirm-live` from Charlie required).

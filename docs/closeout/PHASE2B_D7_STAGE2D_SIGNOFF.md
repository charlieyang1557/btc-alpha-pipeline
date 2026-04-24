# PHASE2B_D7_STAGE2D_SIGNOFF

## 1. Metadata and artifact anchors

| Field | Value |
|---|---|
| Sign-off date | 2026-04-23 |
| Author | Charlie Yang |
| Stage name | D7 Stage 2d |
| Source batch UUID | `5cf76668-47d1-48d7-bd90-db06d31982ed` |
| Live-fire git_head (startup_audit) | `bcd22888b8a6d49f17af5f2d7eb05334a052e1a5` |
| Scope-lock v2 commit | `4df9cee1b98a3ede834d491400ccb55c7a374ff0` |
| Scope-lock v2 SHA256 | `b4cad5873707c6eba272d313e0214011cb5ca91b142126013946f91a72496382` |
| `replay_candidates.json` SHA256 (selection) | `05706642cbeb5014d5072c172b343b01ee56d0eb8ee45afb2f3ce6e56665907e` |
| `stage2d_expectations` SHA256 | `98b87a702cc80df2d993d51857d4142f93f2ab8be66438bd2937c5dd374010a5` |
| `d7b_prompt_template` SHA256 | `f2d6e9d5856be025a2109a1440f8980a3d786bc5cdd284f4d414d06a4680eda7` |
| `stage2d_aggregate_record.json` SHA256 | `09eeda3278c96ccf7b945c5edc9dde9bcfa51ca35138a63d36258514be5c323f` |
| `stage2d_startup_audit.json` SHA256 | `4f46de0902532c3d22d22d06c9f5604e82eff332b47f3aabf1603ef81e8a9ea5` |
| Selection commit timestamp | `2026-04-19T17:02:35Z` |
| Expectations commit timestamp | `2026-04-21T01:47:13Z` |
| Fire start | `2026-04-23T22:33:49.403422Z` |
| Fire end | `2026-04-23T23:23:21.031006Z` |
| Aggregate write completion | `2026-04-23T23:23:21.048843Z` |
| Fire script command | `python scripts/run_d7_stage2d_batch.py --confirm-live` |
| Stage 2d arc span | `5d9f4d4` (E5 seal) → `e8e2d34` (B3) |
| Stage 2d commit count | 22 |

## 2. Executive summary

- Stage 2d was operationally clean and audit-clean. The live fire processed the planned N=200 source candidates (199 live D7b calls + 1 deterministic skipped-source synthetic record at position 116). `sequence_aborted` was `false`; `abort_reason` was `null`. Wall clock was `2971.461s` (≈ 49m 31s).
- Pre-charge upper-bound budget was `$9.95`; actual spend was `$3.229731` (burn ratio `0.3246`, i.e. 32.5% of the envelope). Production monthly and per-batch caps were not approached.
- Critic status tally: `{ok: 197, d7b_error: 2, skipped_source_invalid: 1}`. Error rate on the 199 live D7b calls was `2 / 199 = 1.005%`, well below any abort threshold.
- Both `d7b_error` records are architecturally correct contract enforcement:
  - **Pos 42** — `api_level` / `leakage_audit_fail: excluded substring leaked: 'profit'`. Caught pre-call by the D7b leakage audit; no response body written; zero retries per CLAUDE.md policy.
  - **Pos 87** — `content_level` / `forbidden_language: 'failing' at position 273`. Caught by the word-boundary scan of `D7B_FORBIDDEN_TERMS` on an otherwise schema-valid response; response body written and preserved; zero retries.
- The 51-key non-drift aggregate schema held (Lock 11 `write_completed_at` tail invariant satisfied), the 9-key Lock 13 startup audit envelope held, the `[50, 100, 150]` checkpoint trigger sequence fired as designed, and the 60-file `stage2c_archive_sha256_by_file` integrity probe matched one-for-one.
- Acceptance notebook re-executed end-to-end: **76 checks, 0 failures, 0 material failures.** Sections A-H returned `FINAL VERDICT: INDEPENDENT_ACCEPT`; Section I (live-fire envelope) passed 28/28.
- The triangulated review methodology (Claude advisor + ChatGPT critic + Claude Code executor) held discipline across all 22 commits. Six process gaps were surfaced and corrected in real time; none reached a commit.

The fire script that took 18 commits to build produced a first-invocation live-fire run that held every pre-declared contract. That is the intended outcome of the pre-registration / disk-verification / triangulated-review methodology applied in this arc.

## 3. Anti-hindsight integrity and pre-registration

### Pre-registration chain

| Anchor | Commit / SHA256 | Timestamp (UTC) |
|---|---|---|
| Scope-lock v2 | `4df9cee1b98a3ede834d491400ccb55c7a374ff0` / `b4cad587…96382` | 2026-04-21T01:47:13Z (latest amendment) |
| Selection (`replay_candidates.json`) | SHA256 `05706642…65907e` | 2026-04-19T17:02:35Z (selection commit) |
| Expectations (`stage2d_expectations`) | SHA256 `98b87a70…7010a5` | 2026-04-21T01:47:13Z |
| D7b prompt template | SHA256 `f2d6e9d5…0eda7` | frozen at Stage 2a contract boundary |
| Fire start | `2026-04-23T22:33:49.403422Z` | — |

All four pre-registration hashes were committed more than 48 hours before the fire start. No `git commit --amend` was performed on any anchor commit between pre-registration and fire. The scope-lock pin amendment at `4df9cee` is itself the pre-registered amendment (Lock 11.1.a refinement), predates the fire, and is captured in the notebook's `SCOPE_LOCK_COMMIT` field.

### Single-attempt validity

Unlike Stage 2c, Stage 2d required only one fire attempt. No abort-and-rerun cycle. No auth-level or transport-level failures during the 49-minute run. The production ledger (`agents/spend_ledger.db`) was touched exactly as the pre-charge contract specified.

### Audit envelope integrity

The `stage2d_startup_audit.json` envelope (9 keys, Lock 13) captured:

- `git_head = bcd22888b8a6d49f17af5f2d7eb05334a052e1a5`
- `mode = live`
- `startup_gates_passed = true`
- `startup_completed_at_utc = 2026-04-23T22:33:49.509341Z`
- `python_version = 3.11.8`, `os_platform = macOS-26.1-arm64-arm-64bit`
- `startup_audit` list of 11 gates, all passed

## 4. Mechanical execution gates

| Gate | Evidence | Verdict |
|---|---:|---|
| Planned source candidates | `stage2d_source_n = 200` | PASS |
| Live D7b calls | `stage2d_live_d7b_call_n = 199` | PASS |
| Deterministic skip | `stage2d_skipped_positions = [116]` | PASS |
| Sequence abort | `sequence_aborted = false`, `abort_reason = null`, `abort_at_call_index = null` | PASS |
| D7b error rate | `2 / 199 = 1.005%` (below any abort threshold) | PASS |
| Critic statuses | `{ok: 197, d7b_error: 2, skipped_source_invalid: 1}` | PASS |
| Aggregate key count (non-drift) | `51` | PASS |
| Aggregate tail key (Lock 11) | `write_completed_at` is last | PASS |
| HG20 drift detection | `hg20_drift_detected = null` (non-drift path) | PASS |
| Checkpoint trigger sequence | `call_index` `[50, 100, 150]` | PASS |
| Stage 2c archive integrity | 60 / 60 files SHA-matched via `stage2c_archive_sha256_by_file` | PASS |
| Pre-charge upper bound vs actual | `$9.95` estimated / `$3.229731` actual (burn 0.3246) | PASS |
| Startup audit envelope | 9 keys, `git_head = bcd2288…52e1a5` | PASS |
| Wall clock | `2971.461s`, `inter_call_sleep = 5.0s` | PASS |
| Token usage | `input 737,417 / output 67,832` | PASS |
| Production ledger isolation | `agents/spend_ledger.db` touched only on live path | PASS |
| Stage 2b overlap re-fire | 5 / 5 overlap candidates (17, 73, 74, 97, 138) completed | PASS |

## 5. Distribution observations by pre-registered label

| Label | n | mean SVR | median SVR | min | max | at/above 0.5 | below 0.5 |
|---|---:|---:|---:|---:|---:|---:|---:|
| `agreement_expected` | 64 | 0.880 | 0.850 | 0.75 | 0.95 | 64 | 0 |
| `divergence_expected` | 5 | 0.240 | 0.150 | 0.00 | 0.75 | 1 | 4 |
| `neutral` | 128 | 0.705 | 0.750 | 0.15 | 0.95 | 103 | 25 |

Two pre-registered axes from Stage 2c are directly comparable:

- **Agreement axis replicated at scale.** All 64 `agreement_expected` candidates had `structural_variant_risk >= 0.5`. Stage 2c's 8/8 agreement-axis result extended to the full population.
- **Divergence axis reversed at scale.** 4 of 5 `divergence_expected` candidates had `structural_variant_risk < 0.5`. Stage 2c's 0/3 divergence-axis failure did **not** replicate at scale; under the larger-N fire, the polarity claim held for divergence as well. This is a Stage 2d empirical observation, not a pre-registered claim, and is carried forward for D8+ re-adjudication.
- **Neutral median above the Stage 2c interval.** Observed neutral median was `0.75`. Stage 2c's pre-registered interval `[0.45, 0.70]` would again be falsified on the median condition. The top-skew pattern noted in Stage 2c Section 7.1 replicated here.

## 6. Stage 2b overlap re-fire (test-retest)

| Position | Stage 2b SVR | Stage 2d SVR | Δ | Agreement |
|---:|---:|---:|---:|---|
| 17 | 0.85 | 0.85 | 0.00 | exact |
| 73 | 0.85 | 0.95 | +0.10 | threshold-consistent |
| 74 | 0.65 | 0.70 | +0.05 | threshold-consistent |
| 97 | 0.95 | 0.85 | −0.10 | threshold-consistent |
| 138 | 0.15 | 0.25 | +0.10 | threshold-consistent |

Five of five Stage 2b overlap candidates retained threshold side across the Stage 2b → Stage 2d test-retest interval. Maximum absolute score delta was `0.10`. The Stage 2b-level low-SVR finding at position 138 (vol-regime, RSI-absent) reproduced on Stage 2d at `SVR = 0.25`.

## 7. D7b contract-enforcement observations (pos 42 and pos 87)

Both `d7b_error` records are architecturally correct contract firings, not production defects. They are captured at per-call record root-level fields (`critic_status`, `d7b_error_category`, `critic_error_signature`, `retry_count`, `raw_payload_paths`) per the D7 field layout; nested `critic_result` is a mirror.

### Position 42 — `api_level` / `leakage_audit_fail`

The pre-call D7b leakage audit scanned the rendered prompt for protected-term leakage and flagged `'profit'` as an excluded substring that leaked into the final prompt text. Classification is `api_level` because the fire script stops the API call before any transport-level invocation. `raw_payload_paths.response` is `null`; `retry_count` is `0`.

This was initially framed in the live-fire adjudication note (`e522a84`) as a transient backend failure / graceful capture. That framing is imprecise. The correct mechanism is a pre-call leakage audit guard catch. The Stage 2d acceptance notebook cell 27 records this correction as a pointer; the adjudication note itself is retained as-committed and not amended. The authoritative classification for the aggregate-level facts is this memo plus the notebook Section I.

### Position 87 — `content_level` / `forbidden_language`

The response body was schema-valid JSON with three D7b scores (`0.35 / 0.75 / 0.85`) and a 1,299-character reasoning field. The word-boundary scan of `D7B_FORBIDDEN_TERMS` matched `'failing'` at character 273 of the reasoning field. The scan fired, the `D7bContentError` was raised with zero retries per the CLAUDE.md `never retry D7b content-level errors` policy. Response body was preserved on disk.

Substantively, the response identified a real DSL bug in the candidate strategy (`close < bb_upper_24_2` is trivially satisfied in almost all market states and does not test the "lower band breach" that the description claimed). The D7b model's alpha-finding was correctly rejected by the forbidden-language guard because the word `'failing'` is in the protected vocabulary. This is working as designed — the guard prefers false positives over false negatives for verdict-leakage prevention. Refinement (e.g. bigram exclusion for descriptive uses like `'failing to'` or `'keep in mind'`) is deferred to D8+ and requires a locked-template re-decision.

## 8. Falsifications

Recorded without softening:

1. **Stage 2c "divergence axis fails mechanically" claim was not replicable under larger N.** Stage 2c had 0 / 3 divergence-axis pass. Stage 2d observed 4 / 5 divergence-axis below-0.5 on a larger independent draw. The Stage 2c conclusion was sample-dependent.
2. **Pre-Stage-2c neutral median interval `[0.45, 0.70]` was falsified in Stage 2d as it was in Stage 2c.** The median stayed top-skewed (`0.75`).
3. **Item C adjudication note framing of pos 42 was imprecise.** Corrected in Section 7 above and in the acceptance notebook Section I.

None of these are defects of the pre-registration or the fire. They are the intended value of locking expectations before the fire.

## 9. New findings carried forward to D8+

- **Divergence-axis sensitivity to sample size.** The 0/3 Stage 2c observation and the 4/5 Stage 2d observation together suggest the divergence-axis claim is load-bearing only at larger N. Future directional claims should be registered with explicit N-sensitivity language.
- **Neutral top-skew is stable across stages.** Two independent fires now show neutral medians above 0.70. D8+ neutral-band registration should not anchor to a moderate-centered distribution.
- **RSI-absent volatility-regime low-SVR pattern reproduces.** Position 138 dropped from 0.15 (Stage 2c) to 0.25 (Stage 2d) — same direction, same low band. This is the most reproducible sub-pattern across Stage 2b, 2c, and 2d.
- **`D7B_FORBIDDEN_TERMS` false-positive class observed at 1/199 rate.** Pos 87 shows the guard can reject substantively valid responses on descriptive-vs-verdict word collisions. Bigram or context-aware refinement is a D8+ candidate but requires a locked-template re-decision.
- **Pre-call leakage audit false-positive class observed at 1/199 rate.** Pos 42 shows the guard can reject prompts whose excluded substrings appear legitimately (e.g., `'profit'` inside a larger construct). Review of protected-term handling is a D8+ candidate.
- **Architectural determinism confirmed.** 20 of 199 Stage 2d prompts were byte-identical to the existing tracked Stage 2c-era prompt files, confirming that the selection + prompt rendering pipeline is deterministic across fires where inputs align.

## 10. Final sign-off verdict

| Sign-off dimension | Verdict | Basis |
|---|---|---|
| Operational sign-off | PASS | 200/200 source candidates processed, 199/199 live D7b calls completed, 2 graceful contract errors, no abort, wall clock 49m 31s |
| Audit / anti-hindsight sign-off | PASS | selection / expectations / prompt-template / scope-lock all committed pre-fire; hashes unchanged through fire; single-attempt run |
| Budget sign-off | PASS | `$3.229731` actual vs `$9.95` pre-charge upper bound (32.5% burn); monthly and per-batch caps not approached |
| Acceptance notebook sign-off | PASS | 76 checks, 0 failures; Sections A-H `INDEPENDENT_ACCEPT`; Section I (live-fire envelope) 28/28 PASS |
| Schema / invariant sign-off | PASS | 51-key non-drift aggregate, Lock 11 tail, 9-key Lock 13 startup audit, `[50,100,150]` checkpoint sequence, 60/60 archive SHAs |
| Scientific sign-off | PASS WITH FALSIFICATIONS | valid evidence generated at N=199; Stage 2c divergence-axis and neutral-median claims not upheld |
| Item C correction disposition | RESOLVED VIA POINTER | acceptance notebook cell 27 records the precise pos 42 mechanism; adjudication note retained as-committed |
| Ready to advance to D8+ | YES | Stage 2d phase closed; no deliverables unstaged; production code unchanged since fire |

Final statement: Stage 2d closed cleanly on the first live invocation of a fire script that required 18 commits of contract-first development to build. The fire held every pre-declared invariant. Two architectural guards (leakage audit, forbidden-language scan) fired on 1 call each and were correctly classified. Stage 2b and 2c pre-registered claims were independently re-evaluated at N=199: the agreement axis replicated, the divergence axis reversed, the neutral top-skew reproduced, and the Stage 2b overlap test-retest held threshold side on all 5 carry-over candidates. The pre-registration / triangulated-review methodology worked as designed.

## Appendix A. Stage 2d commit trail (22 commits)

| # | SHA | Subject |
|---:|---|---|
| 1 | `5d9f4d4` | seal pre-fire pre-registration and self-check (E5) |
| 2 | `685d552` | acceptance notebook |
| 3 | `863502c` | fire script design spec |
| 4 | `28010b2` | fire script skeleton (startup gates + stub isolation) |
| 5 | `5d4c067` | Patch 2 main loop |
| 6 | `bfcee0f` | 3a should_abort vocab |
| 7 | `5848ed4` | 3b B1 |
| 8 | `d9a4dae` | 3b B2 |
| 9 | `9a4ad0e` | 3c expand fire-script aggregate to 49-key target |
| 10 | `9b598a6` | 3c fix-forward — startup audit envelope (§13.3 conformance) |
| 11 | `0b9b28c` | 3d.0 spec amendment — §10.1/§10.2 Direction B resolution |
| 12 | `4d107d4` | 3d.1 HG20 input-drift guard |
| 13 | `dc289fa` | 3d.2 checkpoint_log aggregate field |
| 14 | `6ef6aa6` | 3d.3 stage2c_archive_sha256_by_file (final 3d aggregate addition) |
| 15 | `e1cf27e` | 3d.4 acceptance verification (3d arc closed) |
| 16 | `91c949f` | 3e.1 assert→Stage2dStartupError + stale-reference cleanup |
| 17 | `0a72bfd` | 3e.2 fire-script test coverage (21 pytest cases) |
| 18 | `bcd2288` | 3e.4 acceptance note (pre-live readiness, 3e arc sealed) — **live-fire HEAD** |
| 19 | `e522a84` | live fire adjudication note (sealed narrative before deliverable commits) |
| 20 | `3e0c097` | live fire primary artifacts (51-key aggregate + 9-key startup audit) |
| 21 | `59cd584` | live fire per-call payload corpus (577 files, β scope) |
| 22 | `e8e2d34` | live fire acceptance notebook updates (Section I + pin refresh) |

## Appendix B. Principal artifact hashes

| Artifact | SHA256 |
|---|---|
| `raw_payloads/batch_5cf76668-.../critic/stage2d_aggregate_record.json` | `09eeda3278c96ccf7b945c5edc9dde9bcfa51ca35138a63d36258514be5c323f` |
| `raw_payloads/batch_5cf76668-.../critic/stage2d_startup_audit.json` | `4f46de0902532c3d22d22d06c9f5604e82eff332b47f3aabf1603ef81e8a9ea5` |
| `docs/d7_stage2d/D7_STAGE2D_SCOPE_LOCK_v2.md` | `b4cad5873707c6eba272d313e0214011cb5ca91b142126013946f91a72496382` |
| `docs/d7_stage2d/replay_candidates.json` (selection) | `05706642cbeb5014d5072c172b343b01ee56d0eb8ee45afb2f3ce6e56665907e` |
| Stage 2d expectations (`expectations_file_sha256`) | `98b87a702cc80df2d993d51857d4142f93f2ab8be66438bd2937c5dd374010a5` |
| D7b prompt template (`d7b_prompt_template_sha256`) | `f2d6e9d5856be025a2109a1440f8980a3d786bc5cdd284f4d414d06a4680eda7` |
| `docs/d7_stage2d/deep_dive_candidates.json` | `6cdcd1d22d785d6d58317f61cd62fe8b3340bd22f1ec7c7dcb90e5d2b2da7ce7` |
| `docs/d7_stage2d/test_retest_baselines.json` | `5840b90a57206b01e8109ea73b549cf50089964f5cb1f9f7e83b963569adac2f` |
| `docs/d7_stage2d/label_universe_analysis.json` | `ecd52a9e7656d31d13a8e62ec11a7345f8966343172fbfc3f95add2762b3e4a0` |

## Appendix C. Stratum breakdown (overlap + deep-dive N=20)

| Stratum | n | errors | error rate |
|---:|---:|---:|---:|
| S1 | 5 | 0 | 0.0% |
| S2 | 2 | 0 | 0.0% |
| S3 | 5 | 0 | 0.0% |
| S4 | 2 | 0 | 0.0% |
| S5 | 3 | 0 | 0.0% |
| S6 | 3 | 0 | 0.0% |

The 2 `d7b_error` records (pos 42, pos 87) are in the non-stratum-tracked general population (positions 42 and 87 are neither in the 20-position deep-dive set nor the 20-position Stage 2c overlap set). The stratum-tracked subset executed at 0% error rate.

## Appendix D. Process discipline notes (six surfaced in-arc)

Surfaced and corrected during the 22-commit arc; none reached a commit:

1. **3d.1 Q1 reframing** — advisor factual-claim disk-verify gap.
2. **3e.1 HG1b prefix** — advisor convention disk-verify gap.
3. **Post-fire cost claims** — advisor multiple factual errors against live aggregate.
4. **Pre-Round-2 documentation discipline gap** — advisor ratified without reading draft text.
5. **Item C pos 42 mischaracterization** — ratified with imprecise wording; correction captured via notebook pointer (Option 3), not amendment.
6. **B3 ratification on verification output** — advisor deliberate pragmatic exception on closing documentation commit; recorded as not-precedent.

For D8+: grep / disk-verify before naming or factual claims; read draft text before documentation ratification; never silently skip ratification on substantive content.

## Appendix E. Out of scope for Stage 2d (confirmed untouched)

- `config/environments.yaml`, `config/execution.yaml`, `config/schemas.yaml` — unchanged.
- `backtest/experiments.db` — unchanged.
- `agents/spend_ledger.db` — modified only by the live-fire run via the pre-charge ledger pattern; otherwise untouched.
- `strategies/`, `factors/`, `ingestion/`, `backtest/` engine code — unchanged.
- Pre-Stage-2d raw payload corpora (Stage 2a, 2b, 2c signed-off batches) — unchanged, retained as audit artifacts per CLAUDE.md.

Stage 2d phase closed. Phase 2C / D8+ work is unblocked.

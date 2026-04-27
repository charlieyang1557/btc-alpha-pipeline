# D7 Stage 2d — Live Fire Adjudication Note

**Purpose:** seal the narrative of the Stage 2d live fire while the
evidence is fresh. Adjudicates execution, integrity, and cost outcomes
and catalogs the two tolerated d7b_error cases. Pre-dates the
primary-artifact commit (Item A1) and the bulk-payload commit (Item A2)
per ruling C → A1 → A2 → B.

**Scope:** adjudication only. No code changes. No deep-dive forensic
resolution of the content-level error at pos 87 — explicitly deferred
to the acceptance notebook (Item B).

---

## 1. Live fire execution summary

| Field | Value |
|---|---|
| Fire command | `python scripts/run_d7_stage2d_batch.py --confirm-live` |
| HEAD at fire | `bcd2288` (3e.4 acceptance note commit) |
| `startup_audit.git_head` | `bcd22888b8a6d49f17af5f2d7eb05334a052e1a5` (matches HEAD) |
| `startup_audit.mode` | `live` |
| `startup_audit.python_version` | `3.11.8` |
| `startup_audit.os_platform` | `macOS-26.1-arm64-arm-64bit` |
| `startup_audit.startup_gates_passed` | `True` (all 11) |
| `startup_audit.startup_completed_at_utc` | `2026-04-23T22:33:49.509341Z` |
| `fire_timestamp_utc_start` | `2026-04-23T22:33:49.403422Z` |
| `fire_timestamp_utc_end` | `2026-04-23T23:23:21.031006Z` |
| `write_completed_at` | `2026-04-23T23:23:21.048843Z` |
| `total_wall_clock_seconds` | `2971.461` (≈ 49 min 31 sec) |
| `inter_call_sleep_seconds` | `5.0` |
| Process exit code | `0` |

---

## 2. Completion metrics

| Field | Value |
|---|---|
| `completed_call_count` | `200` |
| `critic_status_counts` | `{"ok": 197, "d7b_error": 2, "skipped_source_invalid": 1}` |
| `sequence_aborted` | `False` |
| `abort_reason` | `None` |
| `abort_at_call_index` | `None` |
| Checkpoint trigger log | `[50, 100, 150]` (all three fired) |
| `hg20_drift_detected` (aggregate) | `None` (non-drift path) |
| `selection_json_sha256_end` | absent (non-drift path) |
| Aggregate key count | `51` (Lock 11 non-drift envelope) |
| Aggregate tail key | `write_completed_at` (Lock 11 tail-append invariant held) |
| Startup audit key count | `9` (Lock 13 envelope) |
| Error rate | `2 d7b_error / 199 live D7b calls = 1.01%` |

No abort rule fired:

- Rule (a) two consecutive api errors — pos 42 and pos 87 are 45 calls apart
- Rule (b) error rate > 40% after K ≥ 3 non-skipped — observed 1.01%
- Rule (c) 4+ content-level errors — observed 1 content-level error
- Rules (d) per-call cost / (e) cumulative cost cap — not exceeded
- Rule (g) unexpected skip at unexpected position — only skip was at pos 116 (Lock 1.5 expected)

---

## 3. Adjudication verifications (three legs, all green)

### 3.1 Stage 2c archive integrity — PASS

Post-fire byte-level SHA comparison of every file listed in the
aggregate's `stage2c_archive_sha256_by_file` dict against its on-disk
counterpart at
`raw_payloads/batch_5cf76668-…/critic/stage2c_archive/`:

```
archive_dir_exists:   True
disk_file_count:      60
recorded_sha_count:   60
PASS: all 60 stage2c archive files byte-identical to recorded SHAs
```

The frozen-input contract held through live fire. Stage 2d's 199 live
`call_*` writes were confined to `critic/`; the `critic/stage2c_archive/`
subdirectory was byte-untouched. This validates the architectural
investment in Patch 3d.3 (`stage2c_archive_sha256_by_file`) — the
aggregate carries a verifiable fingerprint of the Stage 2c archive at
fire time, and that fingerprint reconciles against disk post-fire.

### 3.2 Cost envelope — actual well under the recorded pre-charge upper bound

| Field | Value |
|---|---|
| `total_actual_cost_usd` | `$3.229731` |
| `total_estimated_cost_usd` (aggregate's recorded pre-charge upper bound) | `$9.95` |
| `total_input_tokens` | `737,417` |
| `total_output_tokens` | `67,832` |
| Pre-fire session forecast (reference only, not an aggregate field) | `$3.60 – $4.40` |

`total_estimated_cost_usd` in this aggregate is the sum of per-call
conservative pre-charge upper bounds written to `spend_ledger.db`
BEFORE each API call (per the CLAUDE.md pre-flight charge pattern). It
is **not** a model-generated forecast — it is the aggregate's own
recorded estimate/pre-charge upper bound.

Against that recorded upper bound:

- **Actual $3.229731 was 32.5% of the $9.95 pre-charge upper bound.**
  The conservative pre-charge pattern worked as designed — the ledger
  never pre-committed to a number that would have tripped rule (e)
  cumulative cost cap.
- The pre-fire session-forecast envelope ($3.60–$4.40) is external to
  the aggregate and is cited only for operational context; actual spend
  landed ~10% below its low end.

Empirical per-call cost: $3.229731 ÷ 199 live D7b calls ≈ $0.01623 /
call, which can calibrate future pre-fire forecasts. Budget discipline
held throughout; rules (d) and (e) never fired.

### 3.3 Production ledger delta — CONSISTENT

| Item | Pre-fire | Post-fire |
|---|---|---|
| `agents/spend_ledger.db` SHA-256 | `458c8a0f…5218ffee27b27ab98821551b` | `442b97a8…a04c` |
| Size (bytes) | `147,456` | `241,664` |
| mtime | `Apr 19 07:30` | `Apr 23 16:23` |

Delta: **+94,208 bytes**, consistent with 199 live-fire pre-charge +
finalize row pairs written to the ledger.

---

## 4. Two d7b errors cataloged (defer depth)

### 4.1 Pos 42 — api_level, graceful capture

- `critic/call_0042_critic_result.json`: EXISTS (`critic_status =
  d7b_error`, all d7b-specific fields `None`)
- `critic/call_0042_response.json`: ABSENT (by design — api_level means
  no parseable response body was received)
- `critic/call_0042_traceback.txt`: ABSENT — the api_level failure was
  handled inside the live backend's own retry/classification loop, so
  no Python exception reached the fire script's `except BaseException:`
  traceback-writer
- Aggregate's per-call record for pos 42 carries
  `d7b_error_category = api_level` (the category survives on the
  aggregate record even though the per-call `CriticResult` JSON on disk
  has all d7b fields nulled out — this is a design property of the
  two-layer write, not a regression)

**Disposition:** accepted as a non-systemic, tolerated live-fire loss.
The backend's graceful handling limits post-hoc forensic depth; the
specific API failure mode (rate limit / timeout / 5xx / parse fail) is
not recoverable from disk artifacts alone. No code action implied.

### 4.2 Pos 87 — content_level, full forensic bundle preserved

- `critic/call_0087_critic_result.json`: EXISTS
- `critic/call_0087_response.json`: EXISTS (full LLM body preserved)
- `critic/call_0087_traceback.txt`: EXISTS
  (`error_type: D7bContentError`)
- `call_0087` metadata: `d7b_input_tokens = 3535`,
  `d7b_output_tokens = 356`, `d7b_cost_actual_usd = 0.015945`

The traceback tail confirms the LLM produced substantive reasoning
content (~1.2 KB coherent text assessing the candidate strategy),
which means the `D7bContentError` did not fire on empty/malformed
output but on a schema- or language-contract violation inside an
otherwise well-formed response.

**Disposition:** **investigation target, deferred to the acceptance
notebook (Item B).** This adjudication note does not resolve the exact
schema/language-contract violation. Item B will inspect
`call_0087_response.json` alongside the D7b parser's forbidden-language
scan and schema validator to identify the precise cause.

---

## 5. Architectural validations earned by this fire

| Patch | Validation |
|---|---|
| 3a / 3b / 3c (51-key aggregate) | Lock 11 tail invariant held in live mode |
| 3c fix-forward (§13.3 startup audit) | 9-key envelope produced, git_head captured, matches HEAD |
| 3d.1 (HG20 input-drift guard) | Non-drift path exercised cleanly — no false positive, no drift during fire |
| 3d.2 (`checkpoint_log`) | All three triggers fired at call_index 50, 100, 150 |
| 3d.3 (`stage2c_archive_sha256_by_file`) | 60-entry dict materialized in live mode; post-fire byte-reconciliation PASSED |
| 3e.1 (HG1b reload guard → `Stage2dStartupError`) | Did not fire (`selection.json` stable through fire) |
| 3e.2 (21 pytest cases) | Same invariants covered by the test file held under live execution |

Every sub-patch that shipped in the 3a → 3e arc carried its weight in
this fire. The one architectural investment with the most empirical
payoff: Patch 3d.3 (`stage2c_archive_sha256_by_file`) — without it, the
§3.1 post-fire archive integrity verification would have required an
ad-hoc external SHA reference. With it, the aggregate is
self-verifying.

---

## 6. File-system reconciliation

The live fire produced, under
`raw_payloads/batch_5cf76668-…/critic/`, exactly:

- **199** `call_*_prompt.txt` — one per live D7b call (all 200 source
  positions minus the 1 pos-116 skip)
- **199** `call_*_critic_result.json` — one per live D7b call, including
  the two `d7b_error` records at pos 42 and pos 87
- **198** `call_*_response.json` — one per live D7b call *that returned
  a parseable response body*; pos 42's api_level error produced no
  response body (see §4.1), which accounts for the 199 → 198 gap
- **2** `stage2d_*` primary artifacts — `stage2d_aggregate_record.json`
  (51 keys, Lock 11 tail held) and `stage2d_startup_audit.json` (9-key
  Lock 13 envelope)
- **60** files under `critic/stage2c_archive/` — preserved byte-for-byte
  and SHA-verified against `stage2c_archive_sha256_by_file` (§3.1)

The git `status --short` at adjudication time shows 40 entries of the
form `M raw_payloads/…/critic/call_*_{critic_result,response}.json` for
**20 Stage 2c-origin positions**. These are **distinct from** the 5
`stage2b_overlap_positions = [17, 73, 74, 97, 138]`. They were
pre-existing Stage 2c `call_*` files at the original `critic/` path
that Stage 2d's live writes overwrote in place. Their archived copies
under `critic/stage2c_archive/` remained byte-untouched and
SHA-verified per §3.1.

All of that bulk is staged for Item A2. Item A1 commits only the 2
`stage2d_*` primary artifacts.

---

## 7. Sequence lineage

```
Phase 2b D7 Stage 2d implementation (18 commits, E5 seal → 3e.4 acceptance)
5d9f4d4  D7 Stage 2d: seal pre-fire pre-registration and self-check
…
bcd2288  D7 Stage 2d: 3e.4 acceptance note (pre-live readiness, 3e arc sealed)  ← HEAD at fire

Stage 2d live fire              2026-04-23T22:33:49Z → 2026-04-23T23:23:21Z
                                EXIT 0, 200/200 completed, 197/2/1 status mix

Post-fire sequence              C  → A1 → A2 → B
  Item C  (this note)           <pending commit after Round 1/2 review>
  Item A1 primary artifacts     <authorized, scope β leg 1>
  Item A2 bulk per-call files   <authorized, scope β leg 2>
  Item B  acceptance notebook   <runs against committed canonical aggregate>
```

---

## 8. Next-phase recommendations

1. **Item A1** — commit `stage2d_aggregate_record.json` and
   `stage2d_startup_audit.json` only. Small, high-value, atomic.
2. **Item A2** — commit the 199 `call_*_prompt.txt`, 199
   `call_*_critic_result.json`, 198 `call_*_response.json`, plus the
   in-place overwrites of the 20 Stage 2c-origin positions' `call_*`
   files. This commit is bulk but tree-scoped; revertible independently
   of A1.
3. **Item B** — run the acceptance notebook (from commit `685d552`)
   against the committed canonical live aggregate. Includes the pos 87
   D7bContentError deep-dive per §4.2 deferral.
4. **Deferred polish observations** (non-blocking, may be picked up in
   D8+ if prioritized):
   - `inter_call_sleep_seconds` field naming (Q1 from 3e.0, waived pre-fire)
   - `_classify_d7b_error` tuning vs Stage 2c precedent (Q2, waived)
   - `# Patch 3:` annotation final sweep
   - `stratum_breakdown` deep-dive-only code comment

No code changes planned before Item B runs cleanly.

---

## 9. Sign-off recommendation

**Execution:** pass. Exit 0, 200/200 completion, no abort rule fired.
**Integrity:** pass. Stage 2c archive 60/60 SHA-matched post-fire;
Lock 11 tail held; startup audit 9-key envelope landed with
`git_head` = HEAD.
**Cost:** pass. `total_actual_cost_usd = $3.229731` vs aggregate's
recorded `total_estimated_cost_usd = $9.95` pre-charge upper bound
(32.5%); well within budget rules (d) and (e).
**Abort-logic correctness:** pass. All five rules evaluated against
two real-world errors at 1.01% error rate without false-positive
abort.
**Result quality:** acceptable with two tolerated live-fire errors
catalogued — pos 42 (api_level, graceful capture, accepted as
non-systemic) and pos 87 (content_level, full forensic bundle
preserved, deferred to Item B deep-dive).

**Stage 2d live fire is accepted** — with two non-fatal error records
cataloged for downstream review in Item B. Recommend proceeding to
Item A1 → A2 → B per the ratified ordering.

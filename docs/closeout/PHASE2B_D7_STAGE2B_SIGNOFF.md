# PHASE2B D7 Stage 2b Sign-off

## 1. Scope of Stage 2b

D7 Stage 2b was intended to test:

- Five live D7b critic calls against replayed candidates from signed-off Stage 2d batch `5cf76668-47d1-48d7-bd90-db06d31982ed`.
- Replay-only critic execution; no live D6 proposer calls were fired.
- A locked candidate list selected from Stage 2d artifacts and committed before expectations.
- Sequential execution in the locked firing order, with inter-call spacing and no overlapping live calls.
- Per-call forensic records with prompt, response, critic result, ledger row, scan results, and candidate linkage.
- A self-contained aggregate batch artifact for ordered sequence evidence.
- Pre-registered expectations committed before live fire, enforcing anti-hindsight ordering.
- Ledger/cost accumulation across a five-call critic sequence.
- Preservation of Stage 2a raw `call_0073_*` artifacts before reusing position `73` in Stage 2b.

D7 Stage 2b explicitly did not test:

- Rate-limit characterization.
- Large-N statistical behavior.
- Stage 2c or Stage 2d design questions.

## 2. Inputs and locked preconditions

Locked inputs and preconditions before live fire:

- Selection JSON: `docs/d7_stage2b/replay_candidates.json`
- Selection commit anchor: `2026-04-18T12:24:47Z`
- Expectations file: `docs/d7_stage2b/stage2b_expectations.md`
- Expectations commit anchor: `2026-04-18T13:11:31Z`
- Live fire start: `2026-04-18T13:12:21.588302Z`
- Ordering condition: `selection commit < expectations commit < live fire start`
- Selection tier: `0`
- Selection warnings count: `0`
- Stage 2a prerequisite: `PHASE2B_D7_STAGE2A_SIGNOFF.md` recorded Stage 2a as PASS and Stage 2b prerequisite infrastructure as signed off.

| firing_order | position | theme | pre_registered_label |
|---:|---:|---|---|
| 1 | 17 | `mean_reversion` | `divergence_expected` |
| 2 | 73 | `volatility_regime` | `divergence_expected` |
| 3 | 74 | `volume_divergence` | `divergence_expected` |
| 4 | 97 | `mean_reversion` | `agreement_expected` |
| 5 | 138 | `volatility_regime` | `neutral` |

## 3. Mechanical execution result

Live fire command recorded in the aggregate artifact:

```text
python scripts/run_d7_stage2b_batch.py --confirm-live
```

Mechanical result:

| Field | Value |
|---|---|
| `completed_call_count` | `5` |
| `sequence_aborted` | `false` |
| `abort_reason` | `null` |
| `abort_at_call_index` | `null` |
| `total_actual_cost_usd` | `0.076725` |
| `total_estimated_cost_usd` | `0.25` |
| `total_input_tokens` | `16560` |
| `total_output_tokens` | `1803` |
| `critic_statuses_in_call_order` | `["ok", "ok", "ok", "ok", "ok"]` |
| `d7b_error_categories_in_call_order` | `[null, null, null, null, null]` |
| `reasoning_lengths_in_call_order` | `[1237, 1116, 1050, 1106, 1164]` |
| `actual_costs_in_call_order` | `[0.011937, 0.014526, 0.015027, 0.01647, 0.018765]` |
| `input_tokens_in_call_order` | `[1909, 3192, 3204, 3780, 4475]` |
| `output_tokens_in_call_order` | `[414, 330, 361, 342, 356]` |

All five calls returned `critic_status = "ok"`. No abort rule fired. All five raw payload sets, per-call live-call records, and critic-result artifacts were written.

## 4. Acceptance verdict

PASS

| Gate family | Result | Evidence |
|---|---|---|
| pre-fire integrity | PASS | Selection tier `0`, zero warnings, five candidates, exact expectation headers, and commit ordering `2026-04-18T12:24:47Z < 2026-04-18T13:11:31Z < 2026-04-18T13:12:21.588302Z`. |
| per-call parser / schema compliance | PASS | All five calls returned `critic_status="ok"` with score dicts, reasoning strings, no D7b error category, and reasoning lengths `[1237, 1116, 1050, 1106, 1164]`. |
| ledger / cost accounting | PASS | Five Stage 2b live ledger rows, all `completed`, all tagged `backend_kind='d7b_critic'` and `call_role='critique'`, with actual cost sum `0.076725`. |
| aggregate artifact integrity | PASS | Aggregate ordered sequences match per-call records for costs, input tokens, output tokens, statuses, and reasoning lengths; `write_completed_at` is after `fire_timestamp_utc_end`. |
| expectations ordering | PASS | Selection commit precedes expectations commit, and expectations commit precedes live fire. |
| Stage 2a artifact preservation | PASS | Stage 2a `call_0073_*` artifacts were archived under `raw_payloads/batch_5cf76668-47d1-48d7-bd90-db06d31982ed/critic/stage2a_archive/`. |
| Stage 2c readiness criteria | PASS | Actual cost is below estimate; all five reasonings are below 1500 chars; no recurring error class exists; a Stage 2c-relevant divergence signal was observed. |

## 5. Core empirical findings

### 5.1 D7b produced contract-compliant outputs on all 5 calls

All five live D7b calls produced contract-compliant critic outputs:

- No refusal was recorded.
- No forbidden language was recorded.
- No schema failure was recorded.
- All five calls had `critic_status="ok"`.
- All five reasoning lengths were below the 1500-character cap: `1237`, `1116`, `1050`, `1106`, `1164`.
- All three scan-result fields were populated as pass records in each per-call record: `leakage_audit_result`, `forbidden_language_scan_result`, and `refusal_scan_result`.

### 5.2 Cost stayed well below cap and scaled with replay position

Actual per-call costs were:

```text
[0.011937, 0.014526, 0.015027, 0.01647, 0.018765]
```

Input tokens were:

```text
[1909, 3192, 3204, 3780, 4475]
```

Across this ordered five-call sequence, both input tokens and actual cost increased monotonically with later replay positions. Total actual cost was `0.076725`, below the Stage 2b total cap of `0.10` and below the aggregate estimate of `0.25`. The actual/estimated ratio was approximately `0.3069`.

### 5.3 The strongest Stage 2b scientific result: divergence_expected labels were contradicted in 3/3 cases

Calls 1, 2, and 3 were pre-registered as `divergence_expected`.

| call | position | pre_registered_label | D7b `structural_variant_risk` | observed direction | result |
|---:|---:|---|---:|---|---|
| 1 | 17 | `divergence_expected` | `0.85` | high | contradicted |
| 2 | 73 | `divergence_expected` | `0.85` | high | contradicted |
| 3 | 74 | `divergence_expected` | `0.65` | high | contradicted |

For `divergence_expected`, the pre-registered expectation was `structural_variant_risk < 0.5`. D7b returned high structural-variant risk on all three tested divergence candidates. Therefore, the pre-registered divergence expectation was contradicted in all three tested divergence candidates.

### 5.4 agreement_expected was supported in 1/1 tested case

Call 4 was pre-registered as `agreement_expected`.

| call | position | pre_registered_label | D7b `structural_variant_risk` | observed direction | result |
|---:|---:|---|---:|---|---|
| 4 | 97 | `agreement_expected` | `0.95` | high | supported |

For `agreement_expected`, the pre-registered expectation was `structural_variant_risk >= 0.5`. Call 4 supported its label.

### 5.5 neutral remained non-diagnostic

Call 5 was pre-registered as `neutral`.

| call | position | pre_registered_label | D7b `structural_variant_risk` | observed direction | result |
|---:|---:|---|---:|---|---|
| 5 | 138 | `neutral` | `0.15` | low | not reconciled |

The neutral label had no directional pre-registration. It is non-diagnostic for the agreement/divergence rule.

### 5.6 Net interpretation of Stage 2b

Stage 2b does not prove D7b is wrong.

Stage 2b proves that D7b's structural-variant judgment does not track the Stage 2b mechanical divergence label the way expected at `N=5`.

The result is interpretable critic behavior under a mechanically clean live sequence, not a model failure.

## 6. What Stage 2b did NOT establish

Stage 2b did not establish:

- Statistical generalization beyond this five-call probe.
- Rate-limit behavior or throughput limits.
- Calibration claims for thresholds beyond this probe.
- Proof that D7a is right and D7b is wrong.
- Proof that D7b is right and D7a is wrong.
- Any D8 policy decision.
- Any Stage 2c or Stage 2d design decision.

## 7. Artifacts produced

Stage 2b evidence artifacts:

- Aggregate record: `docs/d7_stage2b/stage2b_batch_record.json`
- Per-call records:
  - `docs/d7_stage2b/call_1_live_call_record.json`
  - `docs/d7_stage2b/call_2_live_call_record.json`
  - `docs/d7_stage2b/call_3_live_call_record.json`
  - `docs/d7_stage2b/call_4_live_call_record.json`
  - `docs/d7_stage2b/call_5_live_call_record.json`
- Raw payload directory: `raw_payloads/batch_5cf76668-47d1-48d7-bd90-db06d31982ed/critic/`
- Expectations file: `docs/d7_stage2b/stage2b_expectations.md`
- Selection JSON: `docs/d7_stage2b/replay_candidates.json`
- Acceptance notebook: `docs/test notebooks/D7 Stage 2b acceptance notebook.ipynb`
- Existing Phase 2B deliverable notebook context: `docs/test notebooks/phase2B deliverable test.ipynb`
- Stage 2a sign-off prerequisite: `docs/closeout/PHASE2B_D7_STAGE2A_SIGNOFF.md`

Stage 2a `call_0073_*` artifacts were archived under:

```text
raw_payloads/batch_5cf76668-47d1-48d7-bd90-db06d31982ed/critic/stage2a_archive/
```

## 8. Known defects / residual risks

No blocker-level Stage 2b defect is recorded from the live fire.

Residual risks:

- The D7a/D7b divergence interpretation remains unresolved at `N=5`.
- Stage 2b is sequence-valid but not large enough for stable pattern claims.
- The observed `3/3` contradiction of `divergence_expected` is a central research input for Stage 2c, not a statistical conclusion.

## 9. Stage 2c handoff constraints

- Stage 2c must preserve the successful Stage 2b parser and prompt contract.
- Stage 2c must keep cost tracking split and explicit across estimate, actual cost, input tokens, and output tokens.
- Stage 2c must expand `N` to determine whether the `3/3` contradiction pattern persists.
- Stage 2c must continue using pre-registered expectations with commit-ordering evidence.
- Stage 2c must treat D7a/D7b disagreement as a first-class observation axis.
- Stage 2c must preserve per-call forensic records and aggregate ordered-sequence rebuildability.
- Stage 2c must continue recording scan results directly in per-call and aggregate evidence paths.
- Stage 2c must avoid treating the Stage 2b neutral candidate as directional evidence.
- Stage 2c must not collapse D7a exact/structural recurrence and D7b semantic variant risk into one undifferentiated novelty signal.

## 10. Final sign-off statement

Verdict: PASS

Live fire window: `2026-04-18T13:12:21.588302Z` to `2026-04-18T13:13:34.346987Z`

D7 Stage 2b is signed off as PASS. The implementation and live-fire evidence are mechanically clean: five live critic calls completed sequentially, all returned `critic_status="ok"`, ledger/cost accounting reconciled, raw payloads and per-call records were written, and the aggregate record rebuilt from per-call evidence. The dominant empirical result is the `3/3` contradiction of `divergence_expected` by D7b `structural_variant_risk`, which becomes the central question carried into Stage 2c.

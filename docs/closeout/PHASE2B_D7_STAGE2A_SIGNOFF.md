# Phase 2B D7 Stage 2a — Sign-Off Notes

**Scope:** D7b live Sonnet single-call forensic probe  
**Replay candidate:** batch `5cf76668-47d1-48d7-bd90-db06d31982ed`,
position `73`, theme `volatility_regime`  
**Anti-hindsight anchor:** commit `37e9634`
(`2026-04-18 01:21:16 -0700`)  
**Status at writing:** First live call reached Sonnet, produced a
high-quality response, then failed strict parser validation because
`reasoning` exceeded the 400-character cap.

---

## 1. Purpose

This document records the D7 Stage 2a live-call evidence and the
accounting caveat from the first live D7b forensic probe.

Stage 2a is not a quality gate for the critic as a production policy.
It is a single-call integration probe whose purpose is to verify that:

- pre-live qualitative expectations were committed before the call,
- D7b prompt construction can elicit structured model scores,
- raw response artifacts are preserved,
- strict parser failures are surfaced rather than silently accepted,
- ledger and cost accounting gaps are explicitly tracked.

---

## 2. Archived Failure Record

The failed live response is preserved as forensic evidence because it
shows that the D7b prompt successfully elicited DSL-specific reasoning,
factor references, and reverse-polarity scoring behavior even though the
strict parser rejected the overlong `reasoning` field.

Archived files:

- `docs/d7_stage2a/reasoning_cap_failure_record/call_0073_response.json`
- `docs/d7_stage2a/reasoning_cap_failure_record/call_0073_traceback.txt`

Source files:

- `raw_payloads/batch_5cf76668-47d1-48d7-bd90-db06d31982ed/critic/call_0073_response.json`
- `raw_payloads/batch_5cf76668-47d1-48d7-bd90-db06d31982ed/critic/call_0073_traceback.txt`

Failure signature:

```text
schema_reasoning_length: reasoning: String should have at most 400 characters
```

The response body was approximately 722 characters of reasoning, above
the 400-character schema cap.

---

## 3. Qualitative Read Of The Failed Response

The response is useful evidence, not just an error artifact.

Positive signals:

- It referenced `realized_vol_24h`, `sma_50`, and `macd_hist`.
- It described the entry as volatility-regime expansion plus trend
  confirmation.
- It described exits in relation to volatility normalization, trend
  reversal, and profit target logic.
- It assigned `structural_variant_risk = 0.85`, consistent with
  reverse-polarity semantics for a shallow structural variant.

Parser failure:

- The response exceeded the strict `reasoning` length cap.
- The correct system behavior was to classify this as a D7b content
  error rather than accepting a schema-violating response.

This is informative for the re-fire patch: the next attempt should
preserve the prompt's semantic quality while tightening or enforcing the
reasoning-length budget.

---

## 4. Ledger Reconciliation Note

Ledger showed `actual_cost=0.0` on the `08:43:11 UTC` live call due to
`D7-S2A-5`.

Actual Anthropic spend is estimated at approximately `$0.01` based on
about `2050` input tokens plus about `300` output tokens at Sonnet 4.5
pricing.

The re-fire after patching should close the accounting gap.

Cumulative Phase 2B after Stage 2a:

```text
approximately $2.51 actual
$2.50 per ledger
< $0.01 discrepancy
```

This discrepancy is within estimator tolerance, but it is explicitly
recorded so that budget history does not silently understate live spend.

---

## 5. Anti-Hindsight Anchor

Do not modify
`docs/d7_stage2a/replay_candidate_expectations.md` for the re-fire.

Commit `37e9634` at `2026-04-18 01:21:16 -0700` remains the pre-live
expectation anchor for the replay candidate.

The patch window should remain short and within the same calendar day,
so the re-fire remains tied to the same anti-hindsight commitment.


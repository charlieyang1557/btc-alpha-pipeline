# Phase 2B D7 Stage 2a Sign-Off Note

**Phase 2B D7 Stage 2a sign-off:** 2026-04-18  
**Branch:** `claude/setup-structure-validators-JNqoI`  
**Replay batch:** `5cf76668-47d1-48d7-bd90-db06d31982ed`  
**Replay position:** `73`  
**Replay theme:** `volatility_regime`  
**Anti-hindsight anchor:** `37e9634` at `2026-04-18 01:21:16 -0700`  
**Acceptance notebook:** `docs/test notebooks/phase2B deliverable test.ipynb`, cells `136`-`161`  
**Final notebook verdict:** `D7 Stage 2a final verdict: PASS`  

---

## A. Purpose

This document records the signed-off outcome of Phase 2B D7 Stage 2a: a single-call forensic probe of the live Sonnet D7b critic against one replayed candidate from the signed-off Stage 2d batch. It is the authoritative bridge into D7 Stage 2b. It states what Stage 2a proved under live API conditions, what was patched during the calibration loop, which constraints are now frozen for Stage 2b, and which non-obvious semantics future maintainers must preserve.

---

## B. Scope and Deliverables

Stage 2a was deliberately narrow. It was not a quality gate for a production critic policy and not a multi-call benchmark. It was a live-integration probe designed to prove end-to-end infrastructure before spending on Stage 2b and beyond.

| # | Deliverable | Evidence | Status | Landing / Evidence Commit |
|---|-------------|----------|--------|---------------------------|
| 1 | Live Sonnet D7b backend | `agents/critic/d7b_live.py` | Signed off | `e185873`, `f153a49` |
| 2 | D7b prompt template | `agents/critic/d7b_prompt.py` | Signed off | `e185873`; calibrated cap in final Stage 2a patch |
| 3 | D7b parser | `agents/critic/d7b_parser.py` | Signed off | `e185873`, `368ebf7`; final `1500` cap in Stage 2a sign-off bundle |
| 4 | Fail-open orchestrator integration | `agents/critic/orchestrator.py` | Signed off | `e185873`, `f153a49` |
| 5 | Replay candidate selection script | `scripts/select_replay_candidate.py` | Signed off | `7b0e909`, `a389aff`, output committed in `f233a2f` |
| 6 | BatchContext reconstruction | `agents/critic/replay.py` | Signed off | `e185873`, verified by notebook `BK` |
| 7 | Dry-run script | Stage 2a dry-run artifacts in `dryrun_payloads/` | Signed off | `e185873`, verified by notebook `BL` |
| 8 | Live-fire script | Stage 2a live records and raw payloads | Signed off | `e185873`, `f153a49` |
| 9 | Budget ledger dual-tagging | `backend_kind='d7b_critic'`, `call_role='critique'` | Signed off | `e185873`, `f153a49` |
| 10 | Raw payload subdirectory convention | `raw_payloads/batch_<uuid>/critic/` | Signed off | `e185873`, `f153a49`, archive reshape in `e407835` |
| 11 | Live call record | `docs/d7_stage2a/stage2a_live_call_record.json` | Signed off | `f153a49`; successful record archived in Stage 2a sign-off bundle |

All eleven scoped deliverables are signed off.

Stage 2a only changed contracts in response to observed evidence. The final parser cap is not an aesthetic choice; it is the result of two empirical cap failures and an output-token-budget calculation.

---

## C. The 12-Gate Acceptance

The mechanical acceptance record is the Phase 2B deliverable notebook, cells `136`-`161`, sections `BF`-`BR`.

| Gate | Notebook Section | Acceptance Evidence | Status |
|------|------------------|---------------------|--------|
| G1 | `BF` | Real Stage 2d summary exists; replay target position `73` exists and is `pending_backtest` | PASS |
| G2 | `BG` | Live backend mode, model, max tokens, temperature, retry semantics, and no caching verified | PASS |
| G3 | `BH` | Built live prompt passes leakage audit and excludes protected batch/performance context | PASS |
| G4 | `BI` | Parser accepts wrappers but enforces exact schema, score range, forbidden-language, refusal, and `100`-`1500` reasoning length | PASS |
| G5 | `BJ` | Selection JSON exists; selection script reselects position `73`; all seven candidate criteria recompute true | PASS |
| G6 | `BK` | BatchContext reconstruction matches independent notebook rebuild: theme, prior factor sets, prior hashes, hints, defaults | PASS |
| G7 | `BL` | Dry-run path uses replay source, isolated ledger, stub D7b result, no production-ledger pollution | PASS |
| G8 | `BM` | Current live call produced `critic_status='ok'` and completed D7b ledger row | PASS |
| G9 | `BN` | Raw response independently parsed; exactly four keys; scores in `[0, 1]`; no forbidden/refusal language; reasoning length within cap | PASS |
| G10 | `BO` | Live prompt/response/result retained; successful archive complete; `400` and `800` calibration failure archives complete | PASS |
| G11 | `BP` | Ledger row is tagged `d7b_critic` / `critique`; actual cost and token counts captured | PASS |
| G12 | `BQ` | Anti-hindsight expectations reconciled without editing `replay_candidate_expectations.md` | PASS |

Notebook final verdict:

```text
D7 Stage 2a final verdict: PASS
```

Headline result: Stage 2a passes acceptance.

---

## D. The Three Live Calls — Calibration Journey

Stage 2a fired three live D7b calls against the same replay candidate. The first two calls are failures by design: they are preserved as calibration evidence. The third is the accepted Stage 2a live result.

| Call | Timestamp UTC | Cap | Result | Parser-Measured Reasoning Chars | Scores | Cost | Tokens | Evidence |
|------|---------------|-----|--------|----------------------------------|--------|------|--------|----------|
| 1 | `2026-04-18 08:43:11` | `400` | `d7b_error` | `716` (reported during review as approx. `722`) | `0.75 / 0.85 / 0.85` | Ledger recorded `$0.0`; API was billed | Not captured | `docs/d7_stage2a/calibration_failures/reasoning_cap_0400/` |
| 2 | `2026-04-18 09:21:56` | `800` | `d7b_error` | `876` (reported during review as approx. `975`) | `0.75 / 0.90 / 0.95` | `$0.013983` | `3191` in / `294` out | `docs/d7_stage2a/calibration_failures/reasoning_cap_0800/` |
| 3 | `2026-04-18 09:46:59` | `1500` | `ok` | `1241` (reported during review as approx. `1280`) | `0.65 / 0.85 / 0.95` | `$0.015006` | `3192` in / `362` out | `docs/d7_stage2a/successful_live_call_record/` |

Successful-call receipt:

| Field | Value |
|-------|-------|
| `critic_status` | `ok` |
| `semantic_plausibility` | `0.65` |
| `semantic_theme_alignment` | `0.85` |
| `structural_variant_risk` | `0.95` |
| `actual_cost` | `$0.015006` |
| `input_tokens` | `3192` |
| `output_tokens` | `362` |
| `wall_clock_seconds` | `11.612` |
| `raw_prompt` | `raw_payloads/batch_5cf76668-47d1-48d7-bd90-db06d31982ed/critic/call_0073_prompt.txt` |
| `raw_response` | `raw_payloads/batch_5cf76668-47d1-48d7-bd90-db06d31982ed/critic/call_0073_response.json` |
| `critic_result` | `raw_payloads/batch_5cf76668-47d1-48d7-bd90-db06d31982ed/critic/call_0073_critic_result.json` |

### Reasoning Length Calibration

| Cap | Basis | Outcome |
|-----|-------|---------|
| `400` | A priori estimation | Sonnet produced a response above cap; parser rejected; failure archived |
| `800` | First observation plus margin | Sonnet produced a response above cap; parser rejected; cost and tokens captured |
| `1500` | `500 output tokens × 3.3 chars/token × 0.9 safety` | Sonnet response fit within cap; parser accepted; Stage 2a passed |

Meta-lesson: reasoning length for a substantive critic task cannot be guessed a priori. Triangulation required two empirical observations. The principled ceiling is tied to the model output token budget, not to the latest observed length.

If a later response exceeds `1500`, the next action is prompt redesign, not another cap increase. A `1500+` response means the model is using more than about 90% of its output budget on reasoning for a single hypothesis. That is a different failure mode than "cap too tight."

---

## E. Defects Recorded

| ID | Defect | Status | Fix / Disposition |
|----|--------|--------|-------------------|
| D7-S2A-1 | Reasoning cap `400` too tight; empirical evidence supports `1500` | Closed | `368ebf7` raised `400 -> 800`; final Stage 2a patch raises `800 -> 1500` |
| D7-S2A-2 | `CriticResult` not written on `d7b_error` path | Closed | `f153a49` |
| D7-S2A-3 | `stage2a_live_call_record.json` meta-record not built | Closed | `f153a49` |
| D7-S2A-4 | Live script did not load `.env` | Closed | `f153a49` |
| D7-S2A-5 | `actual_cost`, `input_tokens`, `output_tokens` not captured on error path when API succeeded | Closed | `f153a49`; verified by call 2 and call 3 |
| D7-S2A-6 | Apparent double-fire at `08:38` / `08:43` | Not a defect | Auth-retry pattern after local env sourcing |
| D7-S2A-7 | Stub-path writes to production ledger | Not a defect | Intentional design for the live script; dry-run script uses isolated ledger |
| D7-S2A-8 | `leakage_audit_result`, `forbidden_language_scan_result`, `refusal_scan_result` fields are null in `live_call_record` | Pending | Stage 2b patch scope |

D7-S2A-8 is non-blocking for Stage 2a. The scans did run: notebook gates `G3` and `G9` pass. The missing piece is durable self-contained recording in `stage2a_live_call_record.json`. Stage 2b's 5-call batch should not require readers to infer scan results from raw files and notebook cells; these fields must be populated before Stage 2b live calls.

---

## F. Ledger Accounting

The sign-off reconciliation table tracks the five Stage 2a ledger rows that define the live/dry-run accounting surface after the pre-live local stub probe. A sixth row, `52dbca79` at `08:38:25`, is a local `d7b_critic_stub` probe with zero cost; it is visible in the ledger query but excluded from the five-row sign-off reconciliation below.

| Row ID | Timestamp UTC | `api_call_kind` | Status | Estimated | Actual | Input Tokens | Output Tokens |
|--------|---------------|-----------------|--------|-----------|--------|--------------|---------------|
| `88c22cc3` | `08:38:38` | `d7b_critic_live` | `completed` | `$0.050000` | `$0.000000` | `null` | `null` |
| `93b01514` | `08:43:11` | `d7b_critic_live` | `completed` | `$0.050000` | `$0.000000` | `null` | `null` |
| `a485b3f9` | `09:21:39` | `d7b_critic_stub` | `completed` | `$0.000000` | `$0.000000` | `0` | `0` |
| `7826c8c7` | `09:21:56` | `d7b_critic_live` | `completed` | `$0.050000` | `$0.013983` | `3191` | `294` |
| `89205a34` | `09:46:59` | `d7b_critic_live` | `completed` | `$0.050000` | `$0.015006` | `3192` | `362` |

Full verification query:

```sql
SELECT id, api_call_kind, status, estimated_cost, actual_cost,
       input_tokens, output_tokens, backend_kind, call_role, created_at_utc
FROM ledger
WHERE backend_kind='d7b_critic'
ORDER BY created_at_utc;
```

Accounting reconciliation:

| Metric | Value |
|--------|-------|
| Ledger-recorded actual spend | `$0.028989` |
| Estimated true Anthropic spend | approximately `$0.041` |
| One-time discrepancy | approximately `$0.012` |
| Cumulative Phase 2B after Stage 2a | approximately `$2.54` actual / `$2.53` per ledger |
| Budget utilization | about `8.5%` of `$30` cap |

Attribution: the first live call at `08:43:11 UTC` reached the API, produced the first over-cap response, and was billed by Anthropic. Because that call happened before D7-S2A-5 was fixed, the error-path persistence code recorded `actual_cost=0.0` and did not persist token counts. `f153a49` closed the gap. Calls 2 and 3 prove cost and token capture on both content-error and success paths.

This is a one-time calibration gap, not a systemic accounting leak.

---

## G. What Stage 2a Proved

### Infrastructure, Live-Verified

- `LiveSonnetD7bBackend` uses an independent Anthropic client, `max_tokens=500`, explicit `temperature=1.0`, one API-level retry, and zero content-level retries.
- The D7b prompt template produced parseable, fence-strippable JSON-shaped output across three independent live calls.
- The parser handles fence stripping, wrapper extraction, schema validation, forbidden-language scanning, and refusal detection.
- The error taxonomy covers content errors and preserves fail-open behavior without losing forensic evidence.
- Ledger dual-tagging is present on every D7b row: `backend_kind='d7b_critic'` and `call_role='critique'`.
- Raw payload convention is stable: `raw_payloads/batch_<uuid>/critic/` holds prompt, response, traceback-if-present, and `critic_result`.
- Dry-run artifact isolation is verified: dry-run writes to `dryrun_payloads/` and `ledger_dryrun.db`; no dry-run rows appear in the production ledger for the Stage 2a replay.
- BatchContext reconstruction from signed-off Stage 2d artifacts matches independent notebook rebuild at position `73`: `60` prior factor sets, `72` prior hashes, theme hints, and default momentum factors all match.
- Cost and token capture work on both `ok` and content-error paths after `f153a49`.

### Sonnet Behavior, Three-Call Convergence

- Output was schema-shaped in all three calls: exactly four top-level keys, no extras, no missing fields after fence extraction.
- Descriptive-not-directive framing was respected: zero forbidden-language hits across the banned term set.
- Reverse polarity of `structural_variant_risk` was interpreted correctly: high score when the candidate is a shallow variant of prior factor sets.
- No refusal patterns appeared in any call.
- The theme anchor `realized_vol_24h` was identified in all three reasonings.
- The model referenced concrete DSL factors and structures: `realized_vol_24h`, `sma_50`, `macd_hist`, `return_168h`, `close`, threshold values, and dual exit paths.
- The model independently identified prior factor set #3 as the overlap source across the live calls.

Stage 2a proved integration correctness and produced useful semantic-critic evidence. It did not attempt to prove that D7b scores are predictive of backtest outcomes.

---

## H. Design Invariants and Architectural Observations Discovered

### D7a And D7b Must Be Allowed To Disagree On Structural Novelty

| Signal | Value | Meaning |
|--------|-------|---------|
| D7a `structural_novelty` | `1.0` | Exact factor-set match count is zero; the set is exactly new |
| D7b `structural_variant_risk` | `0.95` | Semantically shallow variant of prior #3 because the factor set nearly overlaps |

Both are correct. D7a measures exact structural recurrence. D7b measures semantic variant distance. D8 policy must preserve both axes as orthogonal signals rather than collapsing them into one novelty score.

### Context Bloat From Prior Factor Sets Scales With Replay Position

At position `73`, the prompt contained `60` prior factor sets and used about `3192` input tokens. A linear extrapolation to position `200` implies roughly `9000` input tokens. At Sonnet pricing, D7b input cost would dominate D7b output cost by roughly `7:1` in a fully live 200-call batch.

This is a Stage 2d design concern, not a Stage 2a blocker.

Before Stage 2d, evaluate one of:

- top-N most frequent prior factor sets,
- recency-weighted prior sets,
- prompt caching,
- tiered prior representation,
- hash/factor-set summary compression.

### Temperature 1.0 Produces Bounded Variance At Fixed Candidate

Across three live calls on the same candidate:

| Axis | Observed Range | Interpretation |
|------|----------------|----------------|
| `semantic_plausibility` | `0.65`-`0.75` | bounded variation, stable mid/high plausibility |
| `semantic_theme_alignment` | `0.85`-`0.90` | stable high alignment |
| `structural_variant_risk` | `0.85`-`0.95` | stable high reverse-polarity risk |

The relative ordering is preserved. Single-call scoring has meaningful but bounded noise. Stage 2b should interpret score patterns across candidates with this variance in mind.

---

## I. Hard Constraints Preserved Going Into Stage 2b

These are project-level constraints going forward.

- **No prompt mutation without evidence.** Stage 2a demonstrates the rule: prompt and parser contract changes must be driven by observed failures, not speculative tuning. The parser cap changed; the prompt semantics did not.
- **Expectations files are anti-hindsight anchors.** `docs/d7_stage2a/replay_candidate_expectations.md` at commit `37e9634` is permanent evidence. Future stages must commit expectations before firing live calls and reconcile after; never edit the committed expectations after the fact.
- **Ledger integrity on error paths is mandatory.** Post-`f153a49`, any D7b code path that receives an API response must persist `actual_cost`, `input_tokens`, and `output_tokens`, even if parser validation later fails.
- **Dry-run artifacts remain physically isolated.** Dry-run writes go to `dryrun_payloads/` and `ledger_dryrun.db`, never to production paths.
- **D7b scan results must be captured in live records.** D7-S2A-8 is not a Stage 2a blocker, but it is a Stage 2b prerequisite. `leakage_audit_result`, `forbidden_language_scan_result`, and `refusal_scan_result` must be self-contained fields in the live-call record.
- **Historical calibration artifacts are immutable.** Do not rewrite or overwrite `docs/d7_stage2a/calibration_failures/` or `docs/d7_stage2a/successful_live_call_record/`.
- **D7a exact novelty and D7b semantic variant risk remain separate.** Do not collapse exact factor-set novelty into semantic near-neighbor risk.

---

## J. Evidence Summary

| Evidence | Path / Identifier | Role |
|----------|-------------------|------|
| Acceptance notebook | `docs/test notebooks/phase2B deliverable test.ipynb`, cells `136`-`161` | Mechanical 12-gate acceptance |
| Notebook verdict | `D7 Stage 2a final verdict: PASS` | Headline acceptance result |
| Candidate selection | `docs/d7_stage2a/replay_candidate_selection.json` | Script-chosen replay candidate |
| Anti-hindsight expectations | `docs/d7_stage2a/replay_candidate_expectations.md` | Committed before live call at `37e9634` |
| First cap failure | `docs/d7_stage2a/calibration_failures/reasoning_cap_0400/` | 400-cap failure evidence |
| Second cap failure | `docs/d7_stage2a/calibration_failures/reasoning_cap_0800/` | 800-cap failure evidence |
| Successful live call | `docs/d7_stage2a/successful_live_call_record/` | 1500-cap success evidence |
| Current raw payloads | `raw_payloads/batch_5cf76668-47d1-48d7-bd90-db06d31982ed/critic/` | Prompt, response, result, stale traceback |
| Spend ledger | `agents/spend_ledger.db` | Dual-tagged D7b accounting rows |
| Test suite | `1000` passing, `0` regressions | Stage 2a closeout signal |

Commit trail:

| Commit | Purpose |
|--------|---------|
| `78fdf88` | WIP D7b live backend, prompt, parser, replay, ledger split |
| `e185873` | Complete D7b live backend, scripts, tests, docs |
| `7b0e909` | Canonicalize thin-theme momentum-bleed predicate; harden selection script |
| `37e9634` | Commit replay-candidate qualitative expectations before live fire |
| `a389aff` | Replace `dsl.factors_used()` with `extract_factors(dsl)` |
| `368ebf7` | Raise D7b reasoning cap `400 -> 800` after first live evidence |
| `f153a49` | Error-path persistence, token capture, live-call record, dotenv |
| `f233a2f` | Commit replay candidate selection output for position `73` |
| `7cd107e` | Archive first live-call evidence and sign-off scaffold |
| `e407835` | Reshape calibration failure archive into versioned subdirectories |

---

## K. Phase 2B Stage 2b Readiness

Stage 2a is complete. Stage 2b may begin after D7-S2A-8 is closed.

Stage 2b scope:

- Five live D7b calls.
- Five different replayed candidates.
- Same signed-off Stage 2d batch: `5cf76668-47d1-48d7-bd90-db06d31982ed`.
- Exercise cross-call cost accumulation.
- Exercise rate limiting and wall-clock behavior.
- Measure reasoning-length variance across candidates.
- Inspect D7a/D7b divergence systematicity.
- Measure input-token scaling with replay position.

Expected cost:

| Item | Estimate |
|------|----------|
| Stage 2b live D7b cost | about `$0.08` |
| Cumulative Phase 2B after Stage 2b | about `$2.62` |
| Budget utilization after Stage 2b | about `8.7%` of `$30` cap |

Prerequisite:

| Prerequisite | Status |
|--------------|--------|
| D7-S2A-8 closed: live-call records persist leakage, forbidden-language, and refusal scan results | Required before Stage 2b live calls |

Stage 2b launch prompt should be drafted separately. It should incorporate the Section H design inputs without expanding this sign-off into a Stage 2b design document.

---

## L. What Not To Do

- Do not modify `docs/d7_stage2a/replay_candidate_expectations.md`. Commit `37e9634` is the permanent anti-hindsight anchor.
- Do not modify artifacts under `docs/d7_stage2a/calibration_failures/`.
- Do not modify artifacts under `docs/d7_stage2a/successful_live_call_record/`.
- Do not re-run any D7b live call for Stage 2a. The three live calls on record are the complete Stage 2a evidence base.
- Do not edit `docs/test notebooks/phase2B deliverable test.ipynb` for Stage 2a unless a new artifact changes and a reviewer explicitly requests a notebook correction.
- Do not extend this sign-off into Stage 2b design. Section K is readiness framing only.

---

## M. Verification Checklist

| Check | Result |
|-------|--------|
| Every table value traces to an artifact in Section J or to `agents/spend_ledger.db` | Verified |
| Defect IDs D7-S2A-1 through D7-S2A-8 are recorded | Verified |
| Ledger rows verified with `sqlite3 agents/spend_ledger.db` query | Verified |
| Notebook final verdict quote matches cell `161` output | Verified |
| `replay_candidate_expectations.md` remains unmodified after live calls | Verified |
| Calibration failures archived by cap value | Verified |
| Successful live-call artifacts archived separately | Verified |

Final verdict:

```text
Phase 2B D7 Stage 2a is signed off.
```

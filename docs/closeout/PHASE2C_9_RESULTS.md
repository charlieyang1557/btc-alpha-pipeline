# PHASE2C_9 — Mining-process retrospective (light-touch) — Results

**Status: WORKING DRAFT — Step 1 deliverable only.**

This document is being assembled incrementally per
[`docs/phase2c/PHASE2C_9_PLAN.md`](../phase2c/PHASE2C_9_PLAN.md) §5
six-step sequential gating. Sections marked `(deferred)` are
populated by their respective implementation step's closeout
authoring. Step 1 deliverable populates §3 only.

| section | step | status |
|---|---|---|
| §1 Verdict | Step 6 | (deferred) |
| §2 Scope and methodology | Step 6 | (deferred) |
| §3 Mining-process source review | **Step 1** | **drafted (this commit)** |
| §4 Artifact-distribution audit | Step 2 | (deferred) |
| §5 Theme × pass-count cross-tab | Step 3 | (deferred) |
| §6 Lone-survivor walkthrough | Step 4 | (deferred) |
| §7 Mechanism-vs-observation comparison | Step 5 | (deferred) |
| §8 Case determination | Step 6 | (deferred) |
| §9 Cross-references and verification | Step 6 | (deferred) |

---


## 1. Verdict

*(deferred — Step 6 deliverable per
[`PHASE2C_9_PLAN.md`](../phase2c/PHASE2C_9_PLAN.md) §5.6 and §8.
Case determination (A / B / C with sub-register) emerges from §7
mechanism-vs-observation comparison applied to §4 §5 §6 evidence
maps. Per spec §4.4 one-and-only-one rule, exactly one case
determination produced; multi-case findings prohibited.)*


## 2. Scope and methodology

*(deferred — Step 6 deliverable. Mirrors
[`PHASE2C_9_PLAN.md`](../phase2c/PHASE2C_9_PLAN.md) §2 input
universe + §3 hard scope boundaries + §4 pre-registered exit
conditions + §6 verification framework.)*


---


## 3. Mining-process source review (Step 1 deliverable)

This section reconstructs the Phase 2B Proposer + Critic + theme-
rotation mechanism that produced the 198-candidate batch
`b6fcbf86-4d57-4d1f-ae41-1778296b1ae9`. Output register is
"what the code does" at file:line citation; per spec §3.1.1 / §3.1.2
/ §3.1.3 operational disambiguation, this is **documentation review
+ logic review + mechanism documentation**, NOT critique, redesign
proposal, threshold optimization, or rotation-strategy redesign.

Mechanism interpretation (relating mechanism to observation
evidence) is deferred to §7 (Step 5 deliverable). This section
produces only factual mechanism descriptions.

All file paths are repository-relative; line numbers reference the
canonical batch's runtime code as of session-entry anchor `e59cbda`
on `origin/main`. Code state at the time the canonical batch fired
(2026-04-25) may differ; cross-cycle drift is itself a §3 finding to
be cross-checked at Step 2 artifact-distribution audit (lifecycle-
state distribution provides indirect check on mining-time vs current
mechanism alignment).


### 3.1 Proposer prompt mechanism

**3.1.1 Backend interface contract.**

The Proposer subsystem operates through a backend-agnostic Protocol
defined at [`agents/proposer/interface.py:161-180`](../../agents/proposer/interface.py#L161-L180):

```python
class ProposerBackend(Protocol):
    def generate(self, context: BatchContext) -> ProposerOutput: ...
```

Inputs and outputs are frozen dataclasses:

- `BatchContext` at [`agents/proposer/interface.py:48-84`](../../agents/proposer/interface.py#L48-L84)
  carries `batch_id`, `position` (1-indexed within batch), `batch_size`,
  `allowed_factors` (frozen factor registry tuple at batch start),
  `allowed_operators` (frozen DSL operator grammar tuple), `theme_slot`
  (integer index into `agents.themes.THEMES`), `budget_remaining`
  snapshot dict, and `batch_metadata` free-form dict.
- `ProposerOutput` at [`agents/proposer/interface.py:140-153`](../../agents/proposer/interface.py#L140-L153)
  carries a tuple of `DSLCandidate` (union of `ValidCandidate` + `InvalidCandidate`),
  `cost_estimate_usd`, `cost_actual_usd`, `backend_name`, and
  `telemetry` dict.
- `ValidCandidate` at [`agents/proposer/interface.py:92-104`](../../agents/proposer/interface.py#L92-L104)
  wraps a validated `StrategyDSL` plus `provenance` dict.
- `InvalidCandidate` at [`agents/proposer/interface.py:107-129`](../../agents/proposer/interface.py#L107-L129)
  wraps `raw_json` (exact backend output preserved for audit),
  `parse_error` string, optional `error_kind` tag, and `provenance`.

The interface module documents two contract anchors:

1. **CONTRACT BOUNDARY** at [`agents/proposer/interface.py:18-23`](../../agents/proposer/interface.py#L18-L23):
   the orchestrator and budget ledger MUST NOT branch on backend type
   or import any Sonnet-specific library. Integration code that needs
   to distinguish stub from Sonnet belongs in the backend itself.
2. **DESIGN INVARIANT** at [`agents/proposer/interface.py:24-32`](../../agents/proposer/interface.py#L24-L32):
   `allowed_factors` and `allowed_operators` are the frozen research
   substrate. A backend MUST NOT propose a factor or operator outside
   the allowed lists. Registry/grammar growth is a D1/D2 contract
   change requiring human review outside the batch loop.

The Protocol's `generate()` method's docstring at
[`agents/proposer/interface.py:170-180`](../../agents/proposer/interface.py#L170-L180)
specifies that ordinary parse/validation failures must NOT raise —
they are represented as `InvalidCandidate` entries. Exceptions are
reserved for infrastructure failures, handled via the orchestrator's
crash-safe pre-charge ledger pattern.

**3.1.2 Live Sonnet backend implementation.**

The live Sonnet backend that produced the canonical batch is
`SonnetProposerBackend` at [`agents/proposer/sonnet_backend.py:150-184`](../../agents/proposer/sonnet_backend.py#L150-L184).
Module-level constants:

- `SONNET_MODEL = "claude-sonnet-4-5"` at [`agents/proposer/sonnet_backend.py:59`](../../agents/proposer/sonnet_backend.py#L59)
- `SONNET_INPUT_PRICE_PER_MTOK = 3.0` at [`agents/proposer/sonnet_backend.py:60`](../../agents/proposer/sonnet_backend.py#L60)
- `SONNET_OUTPUT_PRICE_PER_MTOK = 15.0` at [`agents/proposer/sonnet_backend.py:61`](../../agents/proposer/sonnet_backend.py#L61)

CONTRACT BOUNDARY at [`agents/proposer/sonnet_backend.py:25-30`](../../agents/proposer/sonnet_backend.py#L25-L30):
this module is the ONLY file in the codebase that imports the
`anthropic` SDK; the orchestrator and ingest modules depend only on
the `ProposerBackend` Protocol. Mechanical grep test at
`tests/test_orchestrator_ingest.py` enforces the boundary.

Cost computation:

- `compute_cost_usd(input_tokens, output_tokens)` at [`agents/proposer/sonnet_backend.py:64-69`](../../agents/proposer/sonnet_backend.py#L64-L69)
  is the canonical Sonnet pricing function (also imported by Stage 2c
  for cumulative-spend pre-call check).
- `estimate_cost_usd(estimated_input_tokens=4000, max_output_tokens=2000)`
  at [`agents/proposer/sonnet_backend.py:72-78`](../../agents/proposer/sonnet_backend.py#L72-L78)
  is the upper-bound estimator for pre-charge ledger.

Two-tier API exception classification at
[`agents/proposer/sonnet_backend.py:88-105`](../../agents/proposer/sonnet_backend.py#L88-L105):

- `"infrastructure"` → `RateLimitError` / `InternalServerError` /
  `APIConnectionError` / `APITimeoutError` / `APIStatusError` with
  status_code in `{429, 529}` → exponential backoff retry
- `"model"` → all other API exceptions → no retry, terminal routing

Raw payload logging at
[`agents/proposer/sonnet_backend.py:113-142`](../../agents/proposer/sonnet_backend.py#L113-L142):
every API call writes `attempt_NNNN_prompt.txt` and
`attempt_NNNN_response.txt` (or `attempt_NNNN_retry_K_response.txt`
for retries) under `raw_payloads/batch_{batch_id}/` for forensic
replay. Directory creation is idempotent at
[`agents/proposer/sonnet_backend.py:113-116`](../../agents/proposer/sonnet_backend.py#L113-L116).

The `generate()` method at
[`agents/proposer/sonnet_backend.py:203-346`](../../agents/proposer/sonnet_backend.py#L203-L346)
operates as follows:

1. Build the prompt via `_build_prompt()` (line 193-201) which
   delegates to `prompt_builder.build_prompt()` (see §3.1.3 below)
2. Write prompt payload (lines 219-223)
3. Construct user message + system+factor_menu concatenation (lines 225-227)
4. Retry loop (lines 230-282):
   - API call via `client.messages.create()` (lines 233-238) with
     `model`, `max_tokens` (default 2000), `system`, `messages`
   - On exception: classify infrastructure-vs-model (line 241);
     write error payload (lines 244-249); model errors return empty
     ProposerOutput with `error_category="model"` (lines 252-263);
     infrastructure errors retry with exponential backoff
     `delay = base * 2^attempt` (lines 265-268); after retries
     exhausted, return empty output with `retries_exhausted=True`
     (lines 270-282)
5. On successful response: extract text from `response.content[0].text`
   (line 284); write response payload (lines 286-291); compute
   `actual_cost` from `response.usage.input_tokens` +
   `output_tokens` (lines 293-299)
6. Construct provenance dict (lines 301-310): includes backend name,
   model, position, batch_id, input/output tokens, actual cost,
   stop reason
7. Empty-response-body short-circuit at lines 312-323: returns empty
   ProposerOutput with `error="empty_response_body"` /
   `error_category="model"`
8. Otherwise, classify raw text via `classify_raw_json()` (imported
   from `stub_backend` at [`agents/proposer/sonnet_backend.py:51`](../../agents/proposer/sonnet_backend.py#L51))
   and return ProposerOutput with single candidate (lines 325-338)

The `_get_client()` method at
[`agents/proposer/sonnet_backend.py:188-191`](../../agents/proposer/sonnet_backend.py#L188-L191)
lazy-instantiates `anthropic.Anthropic()`. Per CONTRACT BOUNDARY at
[`agents/critic/d7b_live.py:11-14`](../../agents/critic/d7b_live.py#L11-L14)
(see §3.2.4 below), the D7b Critic backend instantiates its OWN
client; the two clients are independent.

**3.1.3 Prompt builder + leakage audit.**

The prompt construction lives at
[`agents/proposer/prompt_builder.py`](../../agents/proposer/prompt_builder.py).
Top-of-module documentation at lines 1-22 specifies the leakage
contract: no constructed prompt may contain (a) the 2022 regime-
holdout year or any 2022 date substring; (b) validation (2024) or
test (2025) date substrings; (c) regime label `"bear_2022"` or
`"regime_holdout"`; (d) holdout/validation/test metric names; (e)
leaderboard entries / rankings / aggregate downstream results.

The forbidden-patterns list at
[`agents/proposer/prompt_builder.py:42-76`](../../agents/proposer/prompt_builder.py#L42-L76)
enumerates 24 regex patterns covering year markers, regime labels,
metric names, OOS aliases, and downstream artifacts. Patterns are
compiled once at import time (line 78-80) for performance.

The `ProposerPrompt` dataclass at
[`agents/proposer/prompt_builder.py:86-101`](../../agents/proposer/prompt_builder.py#L86-L101)
is structured as `(system, user, factor_menu)` triple with
`all_text()` concatenation method for leakage auditing.

The `_theme_for_slot()` helper at
[`agents/proposer/prompt_builder.py:104-107`](../../agents/proposer/prompt_builder.py#L104-L107)
maps `theme_slot` (integer or None) to theme string by indexing
`THEMES` modulo `len(THEMES)`. **Note**: this differs from the
Stage 2c batch's `_theme_for_position()` (see §3.3 below) which
uses `THEME_CYCLE_LEN = 5` (the 6th canonical theme is excluded
from operational rotation). Per
[`agents/proposer/prompt_builder.py:107`](../../agents/proposer/prompt_builder.py#L107),
this helper falls back to `"unspecified"` when slot is None.

The `build_prompt()` function at
[`agents/proposer/prompt_builder.py:110-231`](../../agents/proposer/prompt_builder.py#L110-L231)
constructs the prompt from frozen-substrate inputs:

- `factor_menu` from `registry.menu_for_prompt()` (line 132)
- System prompt block at lines 134-194:
  - Role assignment: "quantitative researcher proposing BTC trading
    hypotheses" (line 135)
  - Output format constraint: "valid JSON matching the StrategyDSL
    schema" (line 136)
  - Constraint enumeration (lines 137-149): factors-from-menu-only;
    operators-from-allowed-list-only; one-sentence economic
    rationale; long/flat positions only (`position_sizing:
    "full_equity"`); complexity budget (entry/exit groups ≤ 3,
    conditions per group ≤ 4, max_hold_bars ≤ 720)
  - Factor/operator addition prohibition with explicit "frozen for
    this batch" framing (lines 146-149)
  - Schema-shape positive block at lines 156-179: shows EXACT JSON
    structure with field names (`name`, `description`, `entry`,
    `exit`, `position_sizing`, `max_hold_bars`)
  - Synonym-rejection negative block at lines 181-189: explicitly
    rejects `hypothesis_id`, `entry_conditions`/`exit_conditions`,
    `left_factor`/`right_value`, `operator`, `condition_group_id`,
    `join_operator`. Comment at lines 151-155 attributes this block
    to "Stage 2a calibration finding"
  - Markdown-fence prohibition at lines 191-192
- User prompt block at lines 214-228:
  - Batch context: `batch_id`, `position/batch_size`, `theme`
    (rotating)
  - Recent batch signal block: `dedup rate so far`, `top factors by
    frequency`, `critic rejections in last 50`, up-to-3 approved
    examples (DSL-only, no metrics)
  - Final directive: "Propose hypothesis #{position}."

The `audit_prompt_for_leakage()` function at
[`agents/proposer/prompt_builder.py:234-253`](../../agents/proposer/prompt_builder.py#L234-L253)
returns a list of forbidden patterns that match anywhere in the
prompt text. Empty list means clean.

**3.1.4 Stage 2d batch orchestration (canonical batch); Stage 2c shared mechanism.**

Per §4.2 register-precision finding (post-Step-1-seal correction):
the canonical batch `b6fcbf86-...` was produced by Stage 2d
orchestration (`STAGE_LABEL = "D6_STAGE2D"` per
[`agents/proposer/stage2d_batch.py:103`](../../agents/proposer/stage2d_batch.py#L103);
`STAGE2D_BATCH_SIZE = 200` per
[`agents/proposer/stage2d_batch.py:106`](../../agents/proposer/stage2d_batch.py#L106)),
NOT Stage 2c (which has `STAGE2C_BATCH_SIZE = 20` per
[`agents/proposer/stage2c_batch.py:87`](../../agents/proposer/stage2c_batch.py#L87)
and could not have produced 200 attempts in a single batch). This
sub-section was originally drafted referencing Stage 2c (sealed at
commit `13be4ff`); the §4.2 finding corrected the stage attribution.

Stage 2c and Stage 2d share rotation logic, prompt builder, Sonnet
backend, Critic gate, and theme list — the mechanism descriptions
in §3.1.1 / §3.1.2 / §3.1.3 / §3.2.* / §3.3 apply identically to
both stages. Stage-2d-specific differences (batch size 200 vs 20;
budget cap $20 vs $6; block structure with `BLOCK_SIZE` /
`BLOCK_COUNT` per
[`agents/proposer/stage2d_batch.py:145`](../../agents/proposer/stage2d_batch.py#L145);
stop conditions) are documented at §4.2 cross-reference.

The Stage 2d orchestration code that produced the canonical batch
is at [`agents/proposer/stage2d_batch.py`](../../agents/proposer/stage2d_batch.py).
The remainder of this sub-section documents the **Stage 2c
batch orchestration** at [`agents/proposer/stage2c_batch.py`](../../agents/proposer/stage2c_batch.py)
as the closest-precedent published code structure that Stage 2d
extends; constants, helpers, and orchestration patterns described
below are shared between the two stages (with Stage 2d adjusting
batch size + budget cap + block structure).

Stage 2c module docstring at lines 1-34 documents (these properties
are inherited by Stage 2d with the noted batch-size/budget
adjustments):

- Batch size: 20 hypotheses per Stage 2c batch / 200 per Stage 2d
  batch (the canonical 198-candidate population is one Stage 2d
  batch with 2 candidates rejected at `rejected_complexity`; see
  §4 Step 2 audit for the lifecycle-state distribution)
- Budget cap: $6 per Stage 2c batch / $20 per Stage 2d batch
- Prompt caching: DISABLED (both stages)
- Sequential ordering: call k+1 only after call k fully completes
  (API → payload write → classify → ingest → ledger finalize →
  approved_so_far update)
- Leakage audit MUST pass before each call
- approved_examples cap = 3 (most recent first, pending_backtest only)

Module-level constants relevant to mining-process retrospective:

- `STAGE_LABEL = "D6_STAGE2C"` at [`agents/proposer/stage2c_batch.py:84`](../../agents/proposer/stage2c_batch.py#L84)
- `MODEL_NAME = "claude-sonnet-4-5"` at [`agents/proposer/stage2c_batch.py:85`](../../agents/proposer/stage2c_batch.py#L85)
- `PROMPT_CACHING_ENABLED = False` at [`agents/proposer/stage2c_batch.py:86`](../../agents/proposer/stage2c_batch.py#L86)
- `STAGE2C_BATCH_SIZE = 20` at [`agents/proposer/stage2c_batch.py:87`](../../agents/proposer/stage2c_batch.py#L87)
- `STAGE2C_BATCH_CAP_USD = 6.0` at [`agents/proposer/stage2c_batch.py:88`](../../agents/proposer/stage2c_batch.py#L88)
- `STAGE2C_MONTHLY_CAP_USD = 100.0` at [`agents/proposer/stage2c_batch.py:89`](../../agents/proposer/stage2c_batch.py#L89)
- `STAGE2C_CUMULATIVE_CAP_USD = 30.0` at [`agents/proposer/stage2c_batch.py:90`](../../agents/proposer/stage2c_batch.py#L90)
  (catastrophic stop threshold)
- `APPROVED_EXAMPLES_CAP = 3` at [`agents/proposer/stage2c_batch.py:91`](../../agents/proposer/stage2c_batch.py#L91)
- `THEME_ROTATION_MODE = "interleaved_cyclic"` at [`agents/proposer/stage2c_batch.py:92`](../../agents/proposer/stage2c_batch.py#L92)
- `THEME_CYCLE_LEN = 5` at [`agents/proposer/stage2c_batch.py:93`](../../agents/proposer/stage2c_batch.py#L93)

Allowed-operators tuple at
[`agents/proposer/stage2c_batch.py:110-112`](../../agents/proposer/stage2c_batch.py#L110-L112)
is `("<", "<=", ">", ">=", "==", "crosses_above", "crosses_below")`.

The `THEME_HINTS` dict at
[`agents/proposer/stage2c_batch.py:117-129`](../../agents/proposer/stage2c_batch.py#L117-L129)
is documented at lines 27-30 as **CONTRACT BOUNDARY**: post-hoc
telemetry only. It MUST NOT be referenced in prompt construction,
candidate validation, lifecycle classification, ingest rules, or any
acceptance logic. The dict maps each of the 5 operational themes to
a frozenset of factor names:

- `"momentum"` → `{return_1h, return_24h, return_168h, rsi_14, macd_hist}`
- `"mean_reversion"` → `{zscore_48, bb_upper_24_2, sma_20, sma_50, close}`
- `"volatility_regime"` → `{atr_14, realized_vol_24h, bb_upper_24_2}`
- `"volume_divergence"` → `{volume_zscore_24h}` (single factor)
- `"calendar_effect"` → `{day_of_week, hour_of_day}`

`DEFAULT_MOMENTUM_FACTORS` at
[`agents/proposer/stage2c_batch.py:131-133`](../../agents/proposer/stage2c_batch.py#L131-L133)
is `{rsi_14, return_1h, return_24h, macd_hist}` — used by the D7a
Critic's `default_momentum_fallback` rule (see §3.2.2 below).

The `_theme_for_position()` function at
[`agents/proposer/stage2c_batch.py:156-158`](../../agents/proposer/stage2c_batch.py#L156-L158)
implements the rotation:

```python
def _theme_for_position(k: int) -> str:
    """Interleaved cyclic theme rotation: theme_slot = (k - 1) % 5."""
    return THEMES[(k - 1) % THEME_CYCLE_LEN]
```

Note: with `THEMES` ordering `(momentum, mean_reversion,
volatility_regime, volume_divergence, calendar_effect,
multi_factor_combination)` from
[`agents/themes.py:22-29`](../../agents/themes.py#L22-L29) and
`THEME_CYCLE_LEN = 5`, position k=1 maps to `momentum`; k=2 to
`mean_reversion`; k=3 to `volatility_regime`; k=4 to
`volume_divergence`; k=5 to `calendar_effect`; k=6 wraps back to
`momentum`. The 6th canonical theme `multi_factor_combination` is
unreachable through this rotation.

The main batch loop is `run_stage2c()` at
[`agents/proposer/stage2c_batch.py:483-...`](../../agents/proposer/stage2c_batch.py#L483).
Sequential call loop initiates at line 554:

```python
for k in range(1, STAGE2C_BATCH_SIZE + 1):
    theme = _theme_for_position(k)
```

Per-call procedure (lines 555-...):

1. Build `examples_for_prompt` from last up-to-3 `approved_so_far`
   (lines 559-562); reverse so most recent appears first
2. Sync `backend.approved_examples` (Sonnet only) at lines 571-573
3. Construct `BatchContext` at lines 576-590 with:
   - `batch_id`, `position=k`, `batch_size=STAGE2C_BATCH_SIZE`
   - `allowed_factors=tuple(registry.list_names())`
   - `allowed_operators=ALLOWED_OPERATORS`
   - `theme_slot=(k - 1) % THEME_CYCLE_LEN`
   - `budget_remaining` snapshot
4. Build prompt for leakage audit + token estimation at lines 593-595
5. Run `audit_prompt_for_leakage(prompt)` at line 596; if findings,
   abort batch via `sys.exit(1)` at lines 597-600
6. Estimate input tokens dynamically at line 605; estimate cost at
   line 606
7. Cumulative Stage-2 monthly-spend pre-call check at lines 609-640
   (catastrophic stop if exceeded)
8. Budget pre-call check via `ledger.can_afford()` at lines 643-672
   (truncate batch if exceeded)
9. Pre-charge ledger via `ledger.write_pending()` at lines 675-682
   with `api_call_kind="proposer"`, `backend_kind="d6_proposer"`,
   `call_role="propose"`, estimated cost
10. API call via `backend.generate(ctx)` at line 687; crash routes
    to `ledger.mark_crashed()` at lines 689-693
11. Finalize ledger with actual cost at line 698+ (continues past
    line 700 in source)

Catastrophic stop conditions (post-finalize for each call) per
module docstring at lines 20-26:

- Early parse-rate stop: valid/issued < 0.5 for k ≥ 5
- Per-theme single-mode failure: theme has 4 issued calls all with
  identical (error_category, error_signature)
- Cardinality violation count > 2
- Cumulative Stage-2 monthly spend > $30

Cardinality classification at
[`agents/proposer/stage2c_batch.py:198-213`](../../agents/proposer/stage2c_batch.py#L198-L213)
distinguishes `"single_object"` (valid) from violation patterns
(`"zero_objects"`, `"prose_plus_object"`, `"json_array_N"`).

Error classification at
[`agents/proposer/stage2c_batch.py:244-286`](../../agents/proposer/stage2c_batch.py#L244-L286)
maps `(lifecycle_state, parse_error)` to
`(error_category, error_signature)` over 8 categories: `duplicate_condition`,
`complexity_rejection`, `backend_empty`, `json_parse`,
`frozen_registry_violation`, `grammar_violation`,
`non_finite_threshold`, `schema_field_mismatch`.

Per-theme aggregation at
[`agents/proposer/stage2c_batch.py:361-441`](../../agents/proposer/stage2c_batch.py#L361-L441)
computes valid_count, lifecycle_mix, factor-overlap averages,
contains-rsi14 count, contains-momentum-default count, dominant
factors top-3 — all as post-hoc telemetry per the CONTRACT BOUNDARY
at lines 27-30.

Single-mode failure check at
[`agents/proposer/stage2c_batch.py:444-475`](../../agents/proposer/stage2c_batch.py#L444-L475)
fires only when a theme has exactly 4 non-truncated calls AND all 4
share identical `(error_category, error_signature)`.


### 3.2 Critic gate logic

**3.2.1 Critic orchestrator entry point.**

The Critic subsystem operates through a single entry point
`run_critic()` at
[`agents/critic/orchestrator.py:95-203`](../../agents/critic/orchestrator.py#L95-L203).
Critical property documented at module top
[`agents/critic/orchestrator.py:1-9`](../../agents/critic/orchestrator.py#L1-L9):
`run_critic` NEVER raises. Every failure becomes a status code in
`CriticResult`. This makes fail-open enforceable at the API level,
not just at the policy level. The caller is responsible for
persisting `CriticResult` alongside the candidate; `run_critic` does
no ledger writes, no disk writes, no network access.

`CRITIC_VERSION = "d7_v1"` at
[`agents/critic/orchestrator.py:23`](../../agents/critic/orchestrator.py#L23).

Reliability fuse configuration at
[`agents/critic/orchestrator.py:29-33`](../../agents/critic/orchestrator.py#L29-L33):

- `CRITIC_RELIABILITY_TIER1_MIN_K = 20`
- `CRITIC_RELIABILITY_TIER1_FAILURE_RATE = 0.50`
- `CRITIC_RELIABILITY_TIER2_MIN_K = 50`
- `CRITIC_RELIABILITY_TIER2_FAILURE_RATE = 0.20`
- `CRITIC_RELIABILITY_FUSE_ENFORCED = False`

Per CLAUDE.md hard constraint "NEVER enforce the reliability fuse in
Stage 1 — `CRITIC_RELIABILITY_FUSE_ENFORCED` must remain `False` until
Stage 2", the fuse is currently scaffolded but not enforced.
`should_fuse_halt()` at
[`agents/critic/orchestrator.py:71-87`](../../agents/critic/orchestrator.py#L71-L87)
returns `False` unconditionally when `CRITIC_RELIABILITY_FUSE_ENFORCED`
is `False`.

`compute_reliability_stats()` at
[`agents/critic/orchestrator.py:36-68`](../../agents/critic/orchestrator.py#L36-L68)
computes failure rate from raw counts of `(critic_ok, critic_d7a_error,
critic_d7b_error, critic_both_error)`; returns dict for inclusion in
batch summary under `critic_reliability` key.

The `run_critic()` orchestration contract at
[`agents/critic/orchestrator.py:105-113`](../../agents/critic/orchestrator.py#L105-L113):

1. Run all D7a rules. If ANY rule raises, all D7a output is None and
   `critic_status ∈ {d7a_error, both_error}`.
2. Call `d7b_backend.score()`. If backend raises, all D7b output is
   None and `critic_status ∈ {d7b_error, both_error}`.
3. Record timing: `d7a_ms` and `d7b_ms` separately.
4. Assemble `CriticResult` with `d7b_mode = d7b_backend.mode`.
5. Return. Never raise.

D7a try block at
[`agents/critic/orchestrator.py:132-140`](../../agents/critic/orchestrator.py#L132-L140):
calls `score_d7a(dsl, theme, batch_context)`; on any exception, sets
`d7a_error = True` and leaves `d7a_scores=None`,
`d7a_measures={}`, `d7a_flags=[]`.

D7b try block at
[`agents/critic/orchestrator.py:142-172`](../../agents/critic/orchestrator.py#L142-L172):
calls `d7b_backend.score(dsl, theme, batch_context)`; on any
exception, sets `d7b_error = True`. Forensic signature recovery at
lines 150-155: if exception has `sanitized_signature()` callable
(e.g., `D7bLiveError` subclasses), captures it. Traceback path
recovery at lines 156-163. Cost/token metadata recovery from
`backend._last_api_metadata` at lines 164-171 — billed-but-failed
calls are reconciled to ledger via this recovery path.

Status assignment at
[`agents/critic/orchestrator.py:174-183`](../../agents/critic/orchestrator.py#L174-L183):

- Both errors → `"both_error"`
- Only D7a → `"d7a_error"`
- Only D7b → `"d7b_error"`
- Neither → `"ok"`

`CriticResult` assembly at
[`agents/critic/orchestrator.py:185-203`](../../agents/critic/orchestrator.py#L185-L203):
writes scores conditionally on error state (None if errored),
forensic fields, and timing dict.

**3.2.2 D7a rule scoring.**

D7a comprises four pure deterministic rules, each bounded to
`[0.0, 1.0]` with `None` reserved for unrecoverable degenerate
inputs. Module top doc at
[`agents/critic/d7a_rules.py:1-10`](../../agents/critic/d7a_rules.py#L1-L10)
specifies all rules are pure (no randomness, no wall-clock, no disk
state, no network), deterministic (same input → same output),
bounded, rounded to 4 decimal places.

**Rule 1 — `theme_coherence`** at
[`agents/critic/d7a_rules.py:24-36`](../../agents/critic/d7a_rules.py#L24-L36):

```python
factors = set(extract_factors(dsl))
hints = batch_context.theme_hints.get(theme, frozenset())
if not factors:
    return 0.0
overlap = factors & hints
return round(len(overlap) / len(factors), 4)
```

Returns 0.0 for empty factor set. `theme_hints` is supplied via
`BatchContext` (see §3.2.5 below); the dict maps each theme to its
hint factor set.

**Rule 2 — `structural_novelty`** at
[`agents/critic/d7a_rules.py:44-55`](../../agents/critic/d7a_rules.py#L44-L55):

```python
factor_set = factor_set_tuple(dsl)
if not factor_set:
    return None
prior_occurrences = batch_context.prior_factor_sets.count(factor_set)
return round(1.0 / (1.0 + prior_occurrences), 4)
```

Returns None for empty factor set (degenerate; concept undefined).
For non-empty: inverse exponential decay with prior occurrence count.

**Rule 3 — `default_momentum_fallback`** at
[`agents/critic/d7a_rules.py:63-87`](../../agents/critic/d7a_rules.py#L63-L87):

```python
default_momentum = batch_context.default_momentum_factors
factors = set(extract_factors(dsl))
if not factors:
    return 0.0
momentum_count = len(factors & default_momentum)

if theme == "momentum":
    return 1.0
if momentum_count == 0:
    return 1.0
elif momentum_count == 1:
    return 0.8
elif momentum_count == 2:
    return 0.5
else:
    return round(max(0.0, 0.5 - 0.15 * (momentum_count - 2)), 4)
```

Penalized only when `theme != "momentum"`. Tiered scoring at
0/1/2/3+ default-momentum-factor counts.

**Rule 4 — `complexity_appropriateness`** at
[`agents/critic/d7a_rules.py:95-122`](../../agents/critic/d7a_rules.py#L95-L122)
(LOCKED formula per docstring at line 96):

```python
n_factors = len(set(extract_factors(dsl)))
n_conditions = count_conditions(dsl)
desc_len = get_description_length(dsl)

if n_conditions == 0: return 0.0
if n_factors == 0: return 0.0

if n_conditions == 1:
    base = 0.7
elif 2 <= n_conditions <= 4:
    base = 1.0
else:
    base = max(0.0, 1.0 - 0.15 * (n_conditions - 4))

if n_factors > 7:
    base *= 0.85
if desc_len > 500:
    base *= 0.9

return round(base, 4)
```

Step boundaries are intentional (auditable cliffs, not smoothed) per
docstring at line 98.

**Supporting measures** at
[`agents/critic/d7a_rules.py:130-151`](../../agents/critic/d7a_rules.py#L130-L151)
return 7 raw counts: `factor_set_prior_occurrences`, `n_factors`,
`n_conditions`, `description_length`, `max_hold_bars`,
`n_entry_groups`, `n_exit_groups`. These are NOT scores; they are
inputs for D8 policy.

**Rule flags** (observation tags, NOT gate signals) at
[`agents/critic/d7a_rules.py:159-212`](../../agents/critic/d7a_rules.py#L159-L212):

- `empty_factor_set` (line 169-170) — fires when DSL has no factors
- `thin_theme_momentum_bleed` (line 173-176) — routes through
  canonical predicate `is_thin_theme_momentum_bleed()` at
  [`agents/critic/d7a_feature_extraction.py:33-55`](../../agents/critic/d7a_feature_extraction.py#L33-L55).
  Per CONTRACT BOUNDARY at lines 18-24: this predicate defines the
  ONLY condition under which the flag fires; all other modules MUST
  route through `is_thin_theme_momentum_bleed` rather than
  reimplementing.
- `factor_set_in_top3_repeated` (lines 179-197) — fires when current
  factor set is among the top 3 most-repeated factor sets (count ≥ 2)
  in `prior_factor_sets`
- `theme_anchor_missing` (lines 199-202) — fires when theme has
  anchor factors and current DSL uses none of them
- `description_length_near_limit` (lines 204-206) — fires when
  `400 <= desc_len < 500`
- `n_conditions_heavy` (lines 208-210) — fires when `n_conditions >= 6`

Thin themes per
[`agents/critic/d7a_feature_extraction.py:26-30`](../../agents/critic/d7a_feature_extraction.py#L26-L30):
`{volume_divergence, calendar_effect, volatility_regime}`. The
`thin_theme_momentum_bleed` flag fires when theme is in `THIN_THEMES`
AND `n_default_momentum_factors_used >= 2`.

The `score_d7a()` aggregate at
[`agents/critic/d7a_rules.py:220-245`](../../agents/critic/d7a_rules.py#L220-L245)
returns `(scores, supporting_measures, flags)` tuple. Returns
`(None, measures, flags)` only on unrecoverable rule-computation
error. Individual None scores (e.g., `structural_novelty` on empty
factor set) are kept in the dict; the dict itself is None only on
error.

**3.2.3 D7a feature extraction primitives.**

All D7a rules consume DSL features through the primitives at
[`agents/critic/d7a_feature_extraction.py`](../../agents/critic/d7a_feature_extraction.py).
Module top doc at lines 1-8 specifies the separation rationale:
"If feature extraction is wrong, every rule is wrong downstream,
even if the rule formulas match the spec bit-for-bit."

Key primitives:

- `extract_factors(dsl)` at
  [`agents/critic/d7a_feature_extraction.py:86-100`](../../agents/critic/d7a_feature_extraction.py#L86-L100):
  scans `dsl.entry` + `dsl.exit` condition groups; collects
  `cond.factor` (LHS) and string-typed `cond.value` (RHS factor-vs-
  factor); returns sorted list for determinism
- `count_conditions(dsl)` at
  [`agents/critic/d7a_feature_extraction.py:103-108`](../../agents/critic/d7a_feature_extraction.py#L103-L108):
  total conditions across all groups
- `count_entry_groups(dsl)` / `count_exit_groups(dsl)` at lines
  111-118: OR-connected group counts
- `get_description_length(dsl)` at lines 121-123
- `get_max_hold_bars(dsl)` at lines 126-128
- `factor_set_tuple(dsl)` at
  [`agents/critic/d7a_feature_extraction.py:131-136`](../../agents/critic/d7a_feature_extraction.py#L131-L136):
  canonical sorted factor-set tuple for dedup/saturation; empty
  tuple for DSLs with no factors
- `compute_max_overlap(f_current, f_priors)` at
  [`agents/critic/d7a_feature_extraction.py:58-83`](../../agents/critic/d7a_feature_extraction.py#L58-L83):
  per DESIGN INVARIANT at line 65, returns integer count (NOT
  Jaccard ratio)

**3.2.4 D7b live Sonnet backend.**

The live D7b backend is `LiveSonnetD7bBackend` at
[`agents/critic/d7b_live.py:136-...`](../../agents/critic/d7b_live.py#L136).
Module docstring at
[`agents/critic/d7b_live.py:1-21`](../../agents/critic/d7b_live.py#L1-L21)
specifies:

- Single-call forensic probe implementation
- Fail-open: any content-level error raises; orchestrator converts
  raise to `critic_status='d7b_error'`
- CONTRACT BOUNDARY: prompt caching disabled for all D7b Stage 2
  calls (do not enable without new locked decision)
- CONTRACT BOUNDARY: instantiates its OWN `anthropic.Anthropic()`
  client — independent of D6 Proposer's client (lines 11-14)
- Retry discipline LOCKED at lines 16-21:
  - API-level errors only → one retry with exponential backoff
    (base 1s, max 4s)
  - Content-level errors → ZERO retries (forensic signals preserved)

Cost constants (must remain in sync with D6 Proposer):

- `SONNET_MODEL = "claude-sonnet-4-5"` at
  [`agents/critic/d7b_live.py:45`](../../agents/critic/d7b_live.py#L45)
- `SONNET_INPUT_PRICE_PER_MTOK = 3.0` at line 46
- `SONNET_OUTPUT_PRICE_PER_MTOK = 15.0` at line 47
- `D7B_STAGE2A_COST_CEILING_USD = 0.05` at
  [`agents/critic/d7b_live.py:50`](../../agents/critic/d7b_live.py#L50)
  (single-call cost ceiling, LOCKED)

Exception hierarchy at
[`agents/critic/d7b_live.py:66-106`](../../agents/critic/d7b_live.py#L66-L106):

- `D7bLiveError` (base, has `error_code` + `sanitized_signature()`)
- `D7bLiveAPIError` — API-level failure after retry exhaustion
- `D7bLiveContentError` — content-level failure (parse, schema,
  forbidden language, refusal)
- `D7bLiveLeakageAuditError` — leakage audit failed BEFORE send
- `D7bLiveCostCeilingError` — measured cost exceeded ceiling

API-level exceptions at
[`agents/critic/d7b_live.py:110-115`](../../agents/critic/d7b_live.py#L110-L115):
`(APIConnectionError, APITimeoutError, RateLimitError,
InternalServerError)`.

The `_api_call()` method at
[`agents/critic/d7b_live.py:223-254`](../../agents/critic/d7b_live.py#L223-L254)
implements one-retry semantics: attempt 0 = first, attempt 1 =
retry; on second failure raises `D7bLiveAPIError` with classified
code via `_classify_api_exception()` at lines 118-128.

The `score()` method at
[`agents/critic/d7b_live.py:256-323`](../../agents/critic/d7b_live.py#L256-L323):

1. Reset `self._last_api_metadata = None` at line 272
2. Build prompt via `build_d7b_prompt(dsl, theme, batch_context)`
   at line 274 (see §3.2.5 below)
3. Run leakage audit via `run_leakage_audit(prompt_text)` at
   lines 277-279; raises `D7bLiveLeakageAuditError` on hit
4. Write prompt file BEFORE calling API (lines 281-283; forensic
   preservation on crash)
5. Call API via `_api_call()` at line 286; on raise, write
   traceback at line 288
6. Persist raw response BEFORE parsing at lines 291-293
7. Compute actual cost from `response.usage.input_tokens +
   output_tokens` at lines 295-297
8. Capture metadata BEFORE downstream check at lines 299-308:
   `_last_api_metadata` includes `raw_response_path`,
   `cost_actual_usd`, `input_tokens`, `output_tokens`,
   `retry_count`. This recovery path lets orchestrator reconcile
   billed-but-failed calls.
9. Cost ceiling check at lines 310-313: raises
   `D7bLiveCostCeilingError` if exceeded
10. Parse response via `parse_d7b_response()` at lines 315-319;
    on `D7bContentError`, write traceback and raise
    `D7bLiveContentError`

**3.2.5 D7b prompt template + parser.**

The D7b prompt template at
[`agents/critic/d7b_prompt.py:45-151`](../../agents/critic/d7b_prompt.py#L45-L151)
is documented as **CONTRACT** at lines 6-8: frozen within a run; no
post-hoc patching after inspecting a response; prompt changes are a
new-stage decision, not a cleanup.

Forbidden terms at
[`agents/critic/d7b_prompt.py:31-38`](../../agents/critic/d7b_prompt.py#L31-L38):
22 directive terms (`accept`, `reject`, `approve`, `approved`,
`veto`, `pass`, `fail`, `passing`, `failing`, `recommend`,
`recommended`, `recommendation`, `should be used`, `should not be
used`, `do not use`, `keep`, `discard`, `green light`, `red flag`,
`go-ahead`, `go ahead`).

The prompt instructs the Critic to score on three semantic
dimensions producing JSON with exactly 4 top-level keys
(`semantic_plausibility`, `semantic_theme_alignment`,
`structural_variant_risk`, `reasoning`). Score definitions at
[`agents/critic/d7b_prompt.py:75-89`](../../agents/critic/d7b_prompt.py#L75-L89):

- `semantic_plausibility` (0.0=low, 1.0=high): internal coherence
- `semantic_theme_alignment` (0.0=low, 1.0=high): factor/description
  alignment with theme
- `structural_variant_risk` (0.0=LOW risk, 1.0=HIGH risk):
  REVERSED axis — does this look like a threshold/operator tweak of
  a prior factor set? Documented at lines 84-88 with explicit
  warning about axis reversal.

Reasoning contract at
[`agents/critic/d7b_prompt.py:90-95`](../../agents/critic/d7b_prompt.py#L90-L95):
must describe logic per score; analytical and descriptive; reference
specific factors/operators/structural choices. Length: 100-1500
characters.

Forbidden-language enumeration block at
[`agents/critic/d7b_prompt.py:97-101`](../../agents/critic/d7b_prompt.py#L97-L101):
prompt explicitly enumerates the forbidden terms; reasoning MUST
NOT use them.

Output contract at
[`agents/critic/d7b_prompt.py:106-114`](../../agents/critic/d7b_prompt.py#L106-L114):
single JSON object; no markdown code fences; no preamble; no
postamble; exactly four top-level keys.

Refusal preemption at
[`agents/critic/d7b_prompt.py:116-121`](../../agents/critic/d7b_prompt.py#L116-L121):
"I cannot evaluate this" is NOT valid; refusal is contract violation.

The `build_d7b_prompt()` function at
[`agents/critic/d7b_prompt.py:225-247`](../../agents/critic/d7b_prompt.py#L225-L247)
formats the template with pretty-printed DSL, theme, theme hint
factors (alphabetical bulleted), prior factor sets (deduped, first-
seen order, alphabetical within set), and forbidden language list
(alphabetical bulleted).

Prior factor set serialization is LOCKED per module top doc at
[`agents/critic/d7b_prompt.py:10-16`](../../agents/critic/d7b_prompt.py#L10-L16):
deduplicated, alphabetical within each set, first-seen order across
list, no occurrence counts, no call indices, no theme labels; empty
list renders as exactly `_(none)_`.

Leakage audit at
[`agents/critic/d7b_prompt.py:324-356`](../../agents/critic/d7b_prompt.py#L324-L356)
checks four exclusion classes:

1. UUIDs anywhere in prompt (regex at line 292-295)
2. Year-prefixed dates (regex at line 298: `2022|2023|2024|2025|2026`
   followed by `-DD-DD`)
3. Substring exclusions from `D7B_PROTECTED_TERMS` at lines 256-287
   (32 protected terms including all metric names, batch_id,
   batch_position, holdout, validation/test fields, equity_curve,
   pnl, profit, approved_examples, all D7a score key names, all D7a
   flag names)
4. Directive words outside the enumeration block via regex at lines
   303-307; the enumeration block itself is stripped by
   `_strip_forbidden_language_block()` at lines 310-321 to avoid
   self-flagging

The parser at
[`agents/critic/d7b_parser.py:178-280`](../../agents/critic/d7b_parser.py#L178-L280)
implements strict schema validation:

1. Strip wrapping fences (`_strip_fences` at lines 71-82); strip
   prose preamble/postamble (`_strip_prose` at lines 85-104; finds
   first `{` and matching `}`)
2. JSON decode → raises `D7bContentError("json_decode", ...)` on
   failure
3. Top-level type check → must be dict
4. Extra keys check → raises `schema_extra_keys` if any
5. Missing keys check → raises `schema_missing_keys` if any
6. Pydantic validation via `StrictD7bResponse` at lines 51-63
   (extra='forbid'; scores in `[0.0, 1.0]`; reasoning length
   `[100, 1500]`)
7. Forbidden-term scan on reasoning at lines 247-253; raises
   `forbidden_language` on hit
8. Refusal-pattern scan at lines 255-261; raises `refusal_detected`
   on hit. Refusal patterns at
   [`agents/critic/d7b_parser.py:131-139`](../../agents/critic/d7b_parser.py#L131-L139):
   `(\bi cannot\b, \bi can't\b, \bunable to\b, \brefuse to\b,
   \bdecline to\b, \bcannot evaluate\b, \bcan not evaluate\b)`

Error code taxonomy LOCKED at
[`agents/critic/d7b_parser.py:7-16`](../../agents/critic/d7b_parser.py#L7-L16):
`json_decode`, `schema_extra_keys`, `schema_missing_keys`,
`schema_out_of_range`, `schema_reasoning_length`,
`forbidden_language`, `refusal_detected`.

**3.2.6 Critic acceptance semantics — note for §7.**

Per spec §3.1.2 operational disambiguation, this section's output
register is "what the gate accepts/rejects and on what criteria,"
not "what the gate should accept/reject." The Critic produces:

- D7a 4 rule scores (`theme_coherence`, `structural_novelty`,
  `default_momentum_fallback`, `complexity_appropriateness`) each in
  `[0.0, 1.0]`
- D7a 7 supporting measures (raw counts)
- D7a rule flags (observation tags, NOT gate signals)
- D7b 3 LLM scores (`semantic_plausibility`,
  `semantic_theme_alignment`, `structural_variant_risk`)
- D7b reasoning string (100-1500 chars)
- `critic_status` ∈ `{ok, d7a_error, d7b_error, both_error}`

The D7a rule flags are explicitly documented as "observation tags,
NOT gate signals" at
[`agents/critic/d7a_rules.py:155-156`](../../agents/critic/d7a_rules.py#L155-L156).
Whether and how these scores/flags translate into a candidate-
passing decision is logic outside this Critic module — the Critic
annotates only, never filters. Per CLAUDE.md hard constraint:
"NEVER let the critic influence `approved_examples` window — critic
annotates only, never filters."

The actual lifecycle-state assignment (`pending_backtest`,
`critic_rejected`, etc.) is performed by the orchestrator's ingest
layer (`agents/orchestrator/ingest.py`, referenced as import at
[`agents/proposer/stage2c_batch.py:48-58`](../../agents/proposer/stage2c_batch.py#L48-L58)),
not by `run_critic()` itself. Mechanism reconstruction of that
ingest layer's gate semantics is in scope for §7 mechanism-vs-
observation comparison (Step 5 deliverable) but deferred from §3
per spec §5.5 / §5.6 sequential gating.


### 3.3 Theme rotation mechanism

**3.3.1 Canonical theme list.**

The canonical theme list lives at
[`agents/themes.py`](../../agents/themes.py) and is documented as
**CONTRACT BOUNDARY** at lines 3-7:

> This is the single source of truth for the theme list. Both
> `agents.proposer.prompt_builder` and the orchestrator's future
> theme-rotation logic MUST import from here. The list must not be
> duplicated in any other module; if a second copy is introduced
> the rotation strategy can silently diverge from the prompt text.

The `THEMES` tuple at
[`agents/themes.py:22-29`](../../agents/themes.py#L22-L29):

```python
THEMES: tuple[str, ...] = (
    "momentum",
    "mean_reversion",
    "volatility_regime",
    "volume_divergence",
    "calendar_effect",
    "multi_factor_combination",
)
```

Tuple has 6 entries. Operational note at
[`agents/themes.py:17-21`](../../agents/themes.py#L17-L21):

> Stage 2c/2d operational rotation currently uses the first 5
> themes only (THEME_CYCLE_LEN = 5 in stage2c_batch.py and
> stage2d_batch.py). multi_factor_combination remains canonical but
> is not in current operational rotation pending separate validation.
> See CLAUDE.md "Theme rotation operational boundary" for rationale.

**3.3.2 Operational rotation in Stage 2c/2d (shared mechanism).**

The operational rotation cycle length is `THEME_CYCLE_LEN = 5` —
identical constant in both Stage 2c at
[`agents/proposer/stage2c_batch.py:93`](../../agents/proposer/stage2c_batch.py#L93)
and Stage 2d at
[`agents/proposer/stage2d_batch.py:112`](../../agents/proposer/stage2d_batch.py#L112).
The canonical batch was produced by Stage 2d (per §4.2 finding);
Stage 2c is the closest published precedent.
Adjacent comment at lines 94-99 documents:

> multi_factor_combination excluded from rotation; canonical THEMES
> tuple in agents/themes.py retains all 6 themes. The 6th theme
> (multi_factor_combination) remains canonical/theoretical but is
> not included in current Stage 2c/2d operational rotation pending
> separate validation. See CLAUDE.md "Theme rotation" note for
> rationale and Issue 6 of D8.4 (commit 03112aa) for the diagnostic
> context.

The rotation function `_theme_for_position(k)` at
[`agents/proposer/stage2c_batch.py:156-158`](../../agents/proposer/stage2c_batch.py#L156-L158)
maps batch position `k` (1-indexed) to theme:

```python
def _theme_for_position(k: int) -> str:
    """Interleaved cyclic theme rotation: theme_slot = (k - 1) % 5."""
    return THEMES[(k - 1) % THEME_CYCLE_LEN]
```

The `BatchContext.theme_slot` is also computed via the same modulo
formula at
[`agents/proposer/stage2c_batch.py:583`](../../agents/proposer/stage2c_batch.py#L583):

```python
theme_slot=(k - 1) % THEME_CYCLE_LEN
```

The `BatchContext.theme_slot` is forwarded to the prompt builder via
`prompt_builder._theme_for_slot()` at
[`agents/proposer/prompt_builder.py:104-107`](../../agents/proposer/prompt_builder.py#L104-L107):

```python
def _theme_for_slot(slot: int | None) -> str:
    if slot is None:
        return "unspecified"
    return THEMES[slot % len(THEMES)]
```

**Note**: `_theme_for_slot()` uses `len(THEMES)` (which is 6) as
modulus, while `_theme_for_position()` uses `THEME_CYCLE_LEN` (which
is 5). For the canonical batch, `theme_slot` was always passed as
`(k-1) % 5` from Stage 2c, so the prompt builder never received a
slot value of 5 (which would have mapped to `multi_factor_combination`).
This means even though the prompt builder's modulus would
mechanically support all 6 themes, the operational rotation
constrained inputs to slots `{0, 1, 2, 3, 4}`.

**3.3.3 Resulting position-to-theme mapping.**

For Stage 2c batch positions `k = 1..N` with `THEME_CYCLE_LEN = 5`:

| k | (k-1) % 5 | theme |
|---|---|---|
| 1, 6, 11, 16, ... | 0 | `momentum` |
| 2, 7, 12, 17, ... | 1 | `mean_reversion` |
| 3, 8, 13, 18, ... | 2 | `volatility_regime` |
| 4, 9, 14, 19, ... | 3 | `volume_divergence` |
| 5, 10, 15, 20, ... | 4 | `calendar_effect` |

For a 20-call Stage 2c batch, each theme receives exactly 4 calls.
Cross-batch totals across the canonical 198-candidate population
yield approximately equal per-theme cardinalities; the canonical
anchor per
[`PHASE2C_9_PLAN.md`](../phase2c/PHASE2C_9_PLAN.md) §2.4 is
`~40/40/40/39/39` distribution across the 5 operational themes. The
exact per-theme cardinalities + their relationship to lifecycle-
state distribution are Step 2 / Step 3 deliverables (§4 / §5
working drafts) and are not in §3 scope.

**3.3.4 THEME_HINTS and DEFAULT_MOMENTUM_FACTORS — telemetry vs gate.**

Two theme-related dicts in Stage 2c:

- `THEME_HINTS` at
  [`agents/proposer/stage2c_batch.py:117-129`](../../agents/proposer/stage2c_batch.py#L117-L129)
  — CONTRACT BOUNDARY at lines 27-30: post-hoc telemetry only;
  MUST NOT be referenced in prompt construction, candidate
  validation, lifecycle classification, ingest rules, or any
  acceptance logic
- `DEFAULT_MOMENTUM_FACTORS` at
  [`agents/proposer/stage2c_batch.py:131-133`](../../agents/proposer/stage2c_batch.py#L131-L133)
  — used for D7a `default_momentum_fallback` rule scoring (see
  §3.2.2) and `thin_theme_momentum_bleed` flag (see §3.2.2)

The Stage 2c THEME_HINTS dict (used for telemetry) and the D7b prompt
builder's `batch_context.theme_hints` (used in D7b prompt
construction at
[`agents/critic/d7b_prompt.py:169-174`](../../agents/critic/d7b_prompt.py#L169-L174)
and in D7a `theme_coherence` rule at
[`agents/critic/d7a_rules.py:32`](../../agents/critic/d7a_rules.py#L32))
are structurally independent surfaces that may or may not contain
identical content depending on `BatchContext` construction at
ingest-layer call site. Cross-reference between Stage 2c telemetry
THEME_HINTS and Critic-side `batch_context.theme_hints` is a §7
mechanism-vs-observation deliverable (Step 5).


### 3.4 Step 1 deliverable summary + gating-criterion check

Per spec §5.1 gating criterion: **"§3 working draft has documented
mechanism descriptions at file:line citation register for all of
(Proposer prompt; Critic gate; theme rotation)"**.

Status:

- **§3.1 Proposer prompt mechanism**: documented across 4 sub-
  sections (interface contract; live Sonnet backend; prompt builder
  + leakage audit; Stage 2d batch orchestration with Stage 2c
  shared-mechanism reference per §4.2 stage-attribution correction)
  with file:line citations to `agents/proposer/{interface,
  sonnet_backend,prompt_builder,stage2c_batch,stage2d_batch}.py` ✓
- **§3.2 Critic gate logic**: documented across 6 sub-sections
  (orchestrator entry point; D7a rule scoring; D7a feature
  extraction; D7b live Sonnet backend; D7b prompt template +
  parser; Critic acceptance semantics note) with file:line
  citations to `agents/critic/{orchestrator,d7a_rules,
  d7a_feature_extraction,d7b_prompt,d7b_live,d7b_parser}.py` ✓
- **§3.3 Theme rotation mechanism**: documented across 4 sub-
  sections (canonical theme list; operational rotation in Stage 2c;
  resulting position-to-theme mapping; THEME_HINTS vs
  DEFAULT_MOMENTUM_FACTORS) with file:line citations to
  `agents/themes.py` and Stage 2c rotation logic ✓

Step 1 gating criterion satisfied. Step 2 (artifact-distribution
audit per §5.2) authorized to proceed in subsequent session per
discrete-session-boundary register.

Per spec §6 verification framework + §7 cycle-boundary preservation:

- **§6.1 Evidence-mapping discipline**: every claim in §3 cites
  specific file:line; no narrative-mode prose without artifact
  reference. ✓
- **§6.4 Cycle-boundary-preservation language audit**: §3 contains
  no forbidden forward-pointer language ("next we will run X" /
  "this confirms Y is the next arc" / etc.); mechanism description
  register only. ✓
- **§6.3 Canonical-number cross-checks**: §3.3.3 cross-checks the
  ~40/40/40/39/39 anchor per
  [`PHASE2C_9_PLAN.md`](../phase2c/PHASE2C_9_PLAN.md) §2.4; exact
  per-theme cardinalities deferred to Step 2/Step 3. ✓


---


## 4. Artifact-distribution audit (Step 2 deliverable)

This section reports artifact-distribution data for the canonical
batch `b6fcbf86-4d57-4d1f-ae41-1778296b1ae9` from three
measurement points: (1) `agents/spend_ledger.db` ledger table; (2)
`raw_payloads/batch_b6fcbf86-.../stage2d_summary.json` summary
artifact; (3) `data/compiled_strategies/` manifest directory
count. Per spec §3.1.4 operational disambiguation, this is
**distribution characterization**, not lifecycle-state redesign.
Output register: factual cardinalities at file:line citation;
canonical-number cross-checks against PHASE2C_8.1 closeout
anchors. Mechanism interpretation deferred to §7 (Step 5).


### 4.0 Lifecycle-state distribution

**Source artifact**: `raw_payloads/batch_b6fcbf86-4d57-4d1f-ae41-1778296b1ae9/stage2d_summary.json`
(canonical batch summary; produced by Stage 2d batch orchestration
at batch close per
[`agents/proposer/stage2d_batch.py`](../../agents/proposer/stage2d_batch.py)).

**Top-level batch metadata** (from `stage2d_summary.json`):

| field | value | source key |
|---|---|---|
| `batch_id` | `b6fcbf86-4d57-4d1f-ae41-1778296b1ae9` | `batch_id` |
| `stage_label` | `D6_STAGE2D` | `config.stage_label` |
| `model_name` | `claude-sonnet-4-5` | `config.model_name` |
| `prompt_caching_enabled` | `False` | `config.prompt_caching_enabled` |
| `batch_size` (configured) | 200 | `config.batch_size` |
| `batch_cap_usd` | 20.0 | `config.batch_cap_usd` |
| `theme_rotation_mode` | `interleaved_cyclic` | `config.theme_rotation_mode` |
| `git_commit` (mining-time) | `8d29a6e` | `config.git_commit` |
| `run_timestamp_utc` | `2026-04-26T04:56:25.376871+00:00` | `config.run_timestamp_utc` |
| `batch_status` | `completed` | `batch_status` |
| `batch_duration_seconds` | 1219.56 | `batch_duration_seconds` |
| `hypotheses_attempted` | 200 | `hypotheses_attempted` |
| `unissued_slots` | 0 | `unissued_slots` |
| `truncated` | `False` | `truncated` |
| `lifecycle_invariant_ok` | `True` | `lifecycle_invariant_ok` |
| `parse_rate` | 0.99 | `parse_rate` |
| `total_valid_count` | 198 | `total_valid_count` |
| `distinct_hash_count` | 198 | `distinct_hash_count` |
| `total_estimated_cost_usd` | 2.770076999999999 | `total_estimated_cost_usd` |
| `total_actual_cost_usd` | 2.3021940000000005 | `total_actual_cost_usd` |
| `cumulative_monthly_spend_usd` | 8.653602 | `cumulative_monthly_spend_usd` |

**Lifecycle-state count distribution** (from `lifecycle_counts`
key):

| lifecycle state | count |
|---|---|
| `pending_backtest` | 198 |
| `rejected_complexity` | 2 |
| **TOTAL** | **200** |

All other terminal lifecycle states (`proposer_invalid_dsl`,
`duplicate`, `critic_rejected`, `train_failed`, `holdout_failed`,
`dsr_failed`, `shortlisted`, `budget_exhausted`,
`backend_empty_output`) have count 0 at batch close. The two
`rejected_complexity` candidates correspond to DSL outputs whose
`description` field exceeded the 300-character schema limit per
the StrategyDSL pydantic schema; the `error_breakdown` array
records both with `error_signature="over_complex"` and
`parse_error_prefix` indicating "String should have at most 300
characters" pydantic validation error.

**Per-theme call distribution** (from `per_theme` array):

| theme | n_calls | valid_count | lifecycle_mix |
|---|---|---|---|
| `momentum` | 40 | 39 | `pending_backtest=39, rejected_complexity=1` |
| `mean_reversion` | 40 | 39 | `pending_backtest=39, rejected_complexity=1` |
| `volatility_regime` | 40 | 40 | `pending_backtest=40` |
| `volume_divergence` | 40 | 40 | `pending_backtest=40` |
| `calendar_effect` | 40 | 40 | `pending_backtest=40` |
| **TOTAL** | **200** | **198** | |

Each of the 5 operational themes received exactly 40 call slots
(200 / 5 = 40 per spec §3.3 rotation mechanism). Both
`rejected_complexity` candidates landed in `momentum` and
`mean_reversion` themes (one each); the three other themes
produced 40-of-40 valid candidates.

**Cardinality distribution** (from `cardinality_distribution`
key): 200 of 200 attempts produced `single_object` cardinality;
0 violations across the batch (`cardinality_violation_count = 0`).

**Anomaly flags** (from `anomaly_flags` array): 1 flag fired —
`rsi_14_dominance` at scope `first_50_valid_calls` with
count=46 / total=50 / ratio=0.92 / threshold=0.80. Documents that
46 of the first 50 valid calls referenced `rsi_14` factor,
exceeding the 0.80 threshold for first-block factor dominance.

**Factor-set diversity** (from `valid_with_empty_factor_set_count`
+ `distinct_factor_set_count` + `unique_factor_set_ratio`):

| metric | value |
|---|---|
| valid candidates with empty factor set | 0 |
| distinct factor sets across 198 valid candidates | 141 |
| unique factor set ratio | 0.7121 |

57 of 198 valid candidates use a factor set that is structurally
identical to at least one other valid candidate in the batch
(198 - 141 = 57 with shared factor sets). The remaining 141 are
either unique or first-occurrence-of-shared.

### 4.1 Compiled-strategy manifest count

**Source**: `data/compiled_strategies/*.json` directory.

Manifest count (mechanical `ls *.json | wc -l` at session-entry
state `13be4ff` on `origin/main`): **198**.

Each manifest filename is the candidate's `hypothesis_hash`
(64-character SHA-256 hex per
[`agents/hypothesis_hash.py`](../../agents/hypothesis_hash.py)).
Manifest cardinality matches `lifecycle_counts.pending_backtest = 198`
and `total_valid_count = 198` from §4.0.

### 4.2 Canonical-number cross-check

Cross-checks against canonical anchors per
[`PHASE2C_9_PLAN.md`](../phase2c/PHASE2C_9_PLAN.md) §2.4:

| anchor | spec value | empirical value | source | status |
|---|---|---|---|---|
| Total candidates entering PHASE2C_6 evaluation | 198 | 198 | `total_valid_count` from `stage2d_summary.json` | ✓ |
| Compiled-strategy manifest count | 198 | 198 | `data/compiled_strategies/*.json` directory count | ✓ |
| Distinct hypothesis-hash count | 198 | 198 | `distinct_hash_count` from `stage2d_summary.json` | ✓ |
| Theme distribution `~40/40/40/39/39` | matches | 40/40/40/39/39 (volatility_regime/volume_divergence/calendar_effect/momentum/mean_reversion at valid_count register) | `per_theme` array from `stage2d_summary.json` | ✓ |
| Distinct themes | 5 | 5 | `per_theme` array length | ✓ |
| `multi_factor_combination` excluded from operational rotation | yes | yes (absent from `per_theme` array; absent from lifecycle_counts) | spec §2.5 + canonical theme list at [`agents/themes.py:22-29`](../../agents/themes.py#L22-L29) + `THEME_CYCLE_LEN = 5` at [`agents/proposer/stage2d_batch.py:112`](../../agents/proposer/stage2d_batch.py#L112) | ✓ |

Three additional cross-checks for spend register
(per CLAUDE.md Phase Marker `Current UTC-month spend` field of
`~$8.65`):

| metric | spec/CLAUDE.md value | empirical value | status |
|---|---|---|---|
| Canonical batch actual cost | ~$2.30 (Phase 2C Batch-1 component) | $2.30 (`total_actual_cost_usd`) | ✓ |
| April 2026 cumulative monthly spend | ~$8.65 | $8.65 (`cumulative_monthly_spend_usd`) | ✓ |
| Cost ratio (actual / estimated) | not explicitly anchored | 0.83 (2.30 / 2.77) | (informational) |

All required canonical-number cross-checks pass.

**Register-precision finding (canonical-number-adjacent)**: The
canonical batch was produced by **Stage 2d** orchestration
(`STAGE_LABEL = "D6_STAGE2D"`, `STAGE2D_BATCH_SIZE = 200` per
[`agents/proposer/stage2d_batch.py:103-106`](../../agents/proposer/stage2d_batch.py#L103-L106)),
NOT Stage 2c orchestration as referenced at
[`PHASE2C_9_PLAN.md`](../phase2c/PHASE2C_9_PLAN.md) §2.1 +
PHASE2C_9_RESULTS.md §3.1.4. Stage 2c batch size is 20 per
[`agents/proposer/stage2c_batch.py:87`](../../agents/proposer/stage2c_batch.py#L87);
the canonical batch has 200 attempts, which Stage 2c could not
produce. The §3 mechanism reconstruction prose at §3.1.4
referenced `stage2c_batch.py` but the canonical batch was actually
produced by `stage2d_batch.py`.

The substantive impact on §3 mechanism reconstruction is bounded:
both stages share theme rotation logic
(`THEMES[(k - 1) % THEME_CYCLE_LEN]` with `THEME_CYCLE_LEN = 5`
at both
[`agents/proposer/stage2c_batch.py:93,156-158`](../../agents/proposer/stage2c_batch.py#L93-L158)
and
[`agents/proposer/stage2d_batch.py:112,198-200`](../../agents/proposer/stage2d_batch.py#L112-L200)),
prompt builder
([`agents/proposer/prompt_builder.py:110-231`](../../agents/proposer/prompt_builder.py#L110-L231)),
Sonnet backend
([`agents/proposer/sonnet_backend.py:150-346`](../../agents/proposer/sonnet_backend.py#L150-L346)),
and Critic gate (all of `agents/critic/`). The mechanism
reconstruction in §3.1.1 / §3.1.2 / §3.1.3 / §3.2.* / §3.3 applies
identically to Stage 2d. The orchestration-specific differences
(batch size 20 vs 200; per-batch budget cap $6 vs $20; stop
conditions; block structure with `BLOCK_COUNT = STAGE2D_BATCH_SIZE
// BLOCK_SIZE` at
[`agents/proposer/stage2d_batch.py:145`](../../agents/proposer/stage2d_batch.py#L145))
matter for reproducibility but do not invalidate the mechanism
descriptions surfaced at §3.

**Resolution applied at §3.1.4**: per ChatGPT first-pass
dual-reviewer adjudication (§3 mechanism doc must align with
artifact reality), §3.1.4 was amended in this same commit to:
(a) retitle "Stage 2d batch orchestration (canonical batch); Stage
2c shared mechanism"; (b) add a clarifying paragraph documenting
the stage attribution correction with file:line citations to both
`stage2c_batch.py` and `stage2d_batch.py`; (c) preserve the
existing Stage 2c mechanism documentation as the closest-precedent
published code structure that Stage 2d extends. §3.3.2 also
amended to "Operational rotation in Stage 2c/2d (shared mechanism)"
with cross-citation to both stage files. The post-Step-1-seal
correction is structurally bounded — mechanism descriptions in
§3.1.1-§3.1.3, §3.2.*, §3.3 apply identically to both stages and
are unchanged. Stage-2d-specific differences (batch size 200 vs 20;
budget cap $20 vs $6; block structure) cross-referenced at §4.2.

### 4.3 Step 2 deliverable summary + gating-criterion check

Per spec §5.2 gating criterion: **"§4 working draft has documented
lifecycle-state cardinalities; total candidates entering PHASE2C_6
evaluation matches canonical anchor (198)"**.

Status:

- **Lifecycle-state cardinalities documented** (§4.0): 198
  pending_backtest + 2 rejected_complexity = 200 total; per-theme
  distribution 40/40/40/39/39 (valid_count) ✓
- **Total entering PHASE2C_6 evaluation = 198** (§4.0 +
  §4.1 + §4.2): canonical anchor matches; cross-checks pass at
  three independent measurement points (lifecycle_counts;
  total_valid_count; manifest count) ✓

Step 2 gating criterion satisfied. Step 3 (theme × pass-count
cross-tab per spec §5.3) authorized to proceed in subsequent
session per discrete-session-boundary register.

Per spec §6 verification framework + §7 cycle-boundary preservation:

- **§6.1 Evidence-mapping discipline**: every cardinality cited at
  source key from `stage2d_summary.json` or directory listing
  result; canonical-number cross-checks at file:line register; no
  narrative claims without artifact reference ✓
- **§6.4 Cycle-boundary-preservation language audit**: §4 contains
  no forbidden forward-pointer language (no "next we will run X" /
  "this confirms Y is the next arc" / "Case Z determination") ✓
- **§6.3 Canonical-number cross-checks**: 198-anchor verified at
  three independent measurement points; per-theme anchor verified;
  spend-register anchors verified ✓

**Three substantive observations surfaced for §7 (Step 5)
mechanism-vs-observation comparison register**:

1. **Two rejected_complexity candidates** at description-length
   boundary (>300 chars per StrategyDSL pydantic schema) — affects
   2 of 200 attempts; canonical anchor 198 reflects the
   post-rejection survival count. Both fell in `momentum` and
   `mean_reversion` themes. This is a §3.1 / §3.2 mechanism
   intersection (Proposer DSL output + DSL schema validation at
   ingest layer rejecting before lifecycle-state assignment).
2. **`rsi_14_dominance` first-50-block anomaly** at 92% (46/50
   valid calls) exceeding 0.80 threshold — surfaced as anomaly
   flag at batch close. Per §3.1.3 prompt-builder mechanism, the
   prompt does not explicitly encode rsi_14 in any block; the 92%
   first-50 dominance is an emergent Proposer-side pattern. §7
   mechanism-vs-observation comparison register may invoke this
   for Case A.1 (Proposer prompt defect) evidence.
3. **Factor-set repetition rate of ~28.79%** (57 of 198 valid
   candidates with shared factor sets; 1 - 0.7121 = 0.2879). §3.2.2
   D7a `structural_novelty` rule at
   [`agents/critic/d7a_rules.py:44-55`](../../agents/critic/d7a_rules.py#L44-L55)
   computes per-candidate novelty; aggregate batch-level
   repetition rate (28.79%) provides per-batch context. §7 may
   invoke for Case A.2 (Critic gate calibration) evidence.

These observations are surfaced at register-precision register
without §7 adjudication; substantive interpretation deferred to
Step 5 per spec §5.5 sequential gating.

**§3 register-precision correction applied** (this commit, per
ChatGPT first-pass dual-reviewer adjudication): §3.1.4 retitled
"Stage 2d batch orchestration (canonical batch); Stage 2c shared
mechanism" + amended lead paragraph documenting stage attribution
correction with citations to both `stage2c_batch.py` and
`stage2d_batch.py`; §3.3.2 retitled "Operational rotation in Stage
2c/2d (shared mechanism)"; §3.4 deliverable summary updated to
reflect both stage-file citations. Mechanism descriptions in §3.1.1-
§3.1.3, §3.2.*, §3.3 unchanged (apply identically to both stages).




## 5. Theme × pass-count cross-tab (Step 3 deliverable)

*(deferred — Step 3 deliverable per
[`PHASE2C_9_PLAN.md`](../phase2c/PHASE2C_9_PLAN.md) §5.3.
Inputs: PHASE2C_8.1 closeout §7 theme-level cross-regime pattern
table. Outputs: theme × regime × pass-count cross-tab + per-theme
asymmetry observations + canonical-number cross-checks.)*


## 6. Lone-survivor walkthrough (Step 4 deliverable)

*(deferred — Step 4 deliverable per
[`PHASE2C_9_PLAN.md`](../phase2c/PHASE2C_9_PLAN.md) §5.4. Inputs:
`raw_payloads/batch_b6fcbf86-.../attempt_NNNN_*.txt` +
`data/compiled_strategies/0845d1d7898412f2.json` + PHASE2C_8.1
closeout §6. Outputs: end-to-end mining-process trace for hash
`0845d1d7898412f2` (theme `volume_divergence`,
`volume_surge_momentum_entry`).)*


## 7. Mechanism-vs-observation comparison (Step 5 deliverable)

*(deferred — Step 5 deliverable per
[`PHASE2C_9_PLAN.md`](../phase2c/PHASE2C_9_PLAN.md) §5.5. Cross-
references §3 mechanism descriptions with §4 / §5 / §6 observation
evidence; produces structured evidence map for each Case A.1-A.4 /
B.1-B.3 / C.1-C.3 sub-register.)*


## 8. Case determination (Step 6 deliverable)

*(deferred — Step 6 deliverable per
[`PHASE2C_9_PLAN.md`](../phase2c/PHASE2C_9_PLAN.md) §5.6 + §8
canonical structure. Applies §4.4 one-and-only-one rule to §7
evidence maps; produces single Case A / B / C determination with
sub-register; surfaces tracked-fix register entries +
methodology-codification candidates.)*


## 9. Cross-references and verification

*(deferred — Step 6 deliverable. PHASE2C_9_PLAN.md cross-references
+ PHASE2C_8.1 canonical anchor cross-references + verification
framework audit, per
[`PHASE2C_9_PLAN.md`](../phase2c/PHASE2C_9_PLAN.md) §8.)*

---

**Working-draft cross-references**:

- Spec: [`docs/phase2c/PHASE2C_9_PLAN.md`](../phase2c/PHASE2C_9_PLAN.md)
  (commit `8aa1c66`)
- Scoping decision: [`docs/phase2c/PHASE2C_9_SCOPING_DECISION.md`](../phase2c/PHASE2C_9_SCOPING_DECISION.md)
  (commit `3e0c99d`)
- Primary empirical anchor: [`docs/closeout/PHASE2C_8_1_RESULTS.md`](PHASE2C_8_1_RESULTS.md)
  (commit `69e9af9`; tag `phase2c-8-1-multi-regime-extended-v1`)
- Methodology corpus: [`docs/discipline/METHODOLOGY_NOTES.md`](../discipline/METHODOLOGY_NOTES.md)
  (commit `8154e99`)

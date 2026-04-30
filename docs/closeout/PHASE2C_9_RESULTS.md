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

### 1.0 Case determination

**Case C — sub-registers C.1 + C.2 + C.3 applicable; light-touch
retrospective produced direct qualifying evidence at all three
Case C sub-registers under spec §4.3 evidence-pattern register;
§4.4 one-and-only-one rule applied to §7 evidence map outputs
Case C with sub-register documentation per §8.0 derivation chain
+ §8.1 sub-register documentation.**

§1.0 Case determination is the §8.0 mechanical-procedure output
under sub-spec §1.1 framing decision (§4.4 applied as mechanical
decision rule over threshold evaluations) + sub-spec §1.5
evidence-comparison rule (rule 3 ambiguity-routing). §1 verdict
reports §8 output; §1 does not perform the procedure (per sub-spec
§2.1 + §1.2 verbatim-inheritance discipline).

### 1.1 Per-case evidence summary

Per sub-spec §2.2: §1.1 cites §7 evidence map per sub-register at
descriptive register; reports qualifying-evidence + disqualifying-
counter-evidence at descriptive register; cross-references §7.X.X
for full evidence detail.

**Case A evidence-base summary** (§7.0.5 cross-sub-register
summary inherited verbatim per sub-spec §1.2): A.1 weak qualifying
+ comparable disqualifying; A.2 weak qualifying + strong
disqualifying (Critic annotates only per §3.2.6 + CLAUDE.md hard
rule; 0 critic_rejected lifecycle state at §4.0; ingest-layer-as-
actual-gate out-of-scope per §3.1 reconstruction enumeration);
A.3 weak qualifying + strong disqualifying (uniform 40/40/40/39/39
generation distribution per §4.0; no budget exhaustion;
CONTRACT BOUNDARY documents `multi_factor_combination` exclusion);
A.4 direct qualifying (Observations 9 + 10 + composite hybrid
quality observation align with spec §4.1 A.4 qualifying-evidence
text per §7.0.4) + direct disqualifying (canonical AND-gate
deliberately permissive at generation-cycle register; ingest-layer
out-of-scope; one-of-198 cardinality consistent with B.3
interpretation) + qualifying-vs-disqualifying balance interpretively
ambiguous at light-touch register.

**Case B evidence-base summary** (§7.1.4 cross-sub-register
summary inherited verbatim): B.1 partial qualification (3 of 4
Case A sub-registers satisfy "weaker-than-disqualifying"; A.4 sits
at qualifying-vs-disqualifying boundary); B.2 + B.3 partial
qualification at descriptive register (cohort_a_filtered = 0
consistent with noise floor at descriptive register;
volume_divergence theme distribution consistent with random
allocation) + moderate disqualifying counter-evidence (lone-
survivor specificity traces to specific mining-process inputs
per §6.3 + §7.0.4 A.4 Observations 9 + 10 + 11; rigorous null-
distribution comparison Q-9.A territory out-of-scope per §3.2.5).

**Case C evidence-base summary** (§7.2.4 cross-sub-register
summary inherited verbatim): C.1 direct qualifying (A.4
qualifying-vs-disqualifying balance ambiguous at §7.0 register
matching spec §4.3 C.1 "partial qualifying evidence for Case A
... without clean Case A.x qualification"); C.2 direct qualifying
(B.2 + B.3 mixed qualifying / counter-qualifying for lone-survivor
specificity register at §7.1 register matching spec §4.3 C.2
"mixed qualifying / counter-qualifying evidence for Case B");
C.3 direct qualifying (multiple light-touch-register limitations
across §7.0 + §7.1 cross-cutting register matching spec §4.3 C.3
"light-touch register insufficient for discrimination").

### 1.2 Falsifiability statement

Per sub-spec §1.6 chain-falsifiability per-link-point structure +
spec §6.2 falsifiability-statement discipline: PHASE2C_9 Case C
determination would be falsified by changes to the §7 evidence
map characterization that, when fed mechanically through §4.1 /
§4.2 / §4.3 + §4.4 + §1.5 evidence-comparison rule, produce a
different case determination. Three link-point counterfactuals
applicable to Case C determination:

**Link-point 1 — §7 characterization layer counterfactual**:
structured re-examination of §3-§6 register at depth greater than
light-touch that would, when fed into §7 evidence-map construction,
produce a different §7 sub-register qualifying-vs-disqualifying
characterization. Specifically: ingest-layer mechanism reconstruction
(currently out-of-§3-scope per Q-9-01 tracked-fix register at
§8.3) that would resolve the §7.0.4 A.4 sub-register
"INTERPRETIVELY AMBIGUOUS" balance to either (a) "qualifying
stronger than disqualifying" (Case A.4 clean qualification) or
(b) "disqualifying stronger than qualifying" (Case B-direction at
A.4); and resolve the §7.1.2 B.2 + §7.1.3 B.3 "mixed qualifying /
counter-qualifying" pattern at lone-survivor specificity register
to either (a) "tail-event consistent" (Case B.3 clean qualification)
or (b) "mining-time-vs-evaluation-time gate misalignment" (Case
A.4 clean qualification at structured re-examination depth).

**Link-point 2 — §4.1 / §4.2 / §4.3 threshold layer
counterfactual**: counterfactual change in threshold-criterion
satisfaction at the §1.5 evidence-comparison rule application
register. Specifically: §1.5 rule 3 ambiguity-routing canonical
resolution (Reading (i) at §4.1 "stronger than" hard case per
sub-spec §1.5) is the load-bearing rule pathway producing Case A
NOT-cleanly-satisfied at A.4. If Reading (ii) were canonical
instead of Reading (i), §1.5 rule 3 would route ambiguity to
"NOT cleanly satisfied" symmetrically at Case B "weaker than"
register but might route differently at §4.1 "stronger than"
register; rigorous adjudication requires deeper retrospective
register that would, when fed through §4.4, produce a different
mechanical-rule output.

**Link-point 3 — §4.4 multi-case-findings rule layer
counterfactual**: counterfactual change in multi-case-findings
determination. Specifically: if exactly one Case (A or B) were
cleanly satisfied at §1 + §2 link-points, the §4.4 multi-case-
findings rule would not trigger Case C; instead the cleanly-
satisfied single Case would be the determination. The
counterfactual requires Case A or Case B to satisfy clean
qualification at all sub-registers (per §4.1 "at least ONE" or
§4.2 "ALL" criterion respectively) without disqualifying counter-
evidence stronger than qualifying.

Per spec §6.2 specificity discipline + sub-spec §1.6 specificity
requirement: each link-point counterfactual is specific (cites
specific §7.X.X sub-register + specific counter-evidence /
pattern / resolution mechanism + specific mechanical-rule
pathway producing different determination), not gestural.

### 1.3 Forward-pointer register

Per sub-spec §3.3 + spec §4.4 Case C row allowed-register: §1.3
forward-pointer register (cross-reference §8.2 for expanded
register).

Light-touch retrospective produced ambiguous evidence at
sub-registers C.1 + C.2 + C.3. Post-Q-9.B scoping cycle's
deliberation surface includes (a) structured re-examination at
depth greater than light-touch (specifically: ingest-layer
mechanism reconstruction per Q-9-01 tracked-fix register at §8.3;
A.4 deliberate-staged-tightening-vs-defect adjudication; lone-
survivor specificity register adjudication at A.4-vs-B.3
register), (b) statistical-significance machinery to disambiguate
noise-floor vs systematic-pattern at Q-9.A register (specifically:
B.2 cohort_a_filtered = 0 noise-floor null-distribution test; B.3
one-of-N tail-event-vs-systematic-pattern null-distribution test),
(c) calibration-variation at Q-9.C register (specifically: A.4
canonical AND-gate calibration variation; lone-survivor permissive
AND-gate-acceptance-of--10.2%-return calibration variation), (d)
other paths surfaced at scoping cycle.

Per spec §4.4 + §7.2 cycle-boundary preservation: this
forward-pointer register does NOT pre-name the successor scoping
cycle's substantive direction; it surfaces the deliberation surface
that the successor scoping cycle will adjudicate. Specific
direction selection is not pre-committed at PHASE2C_9 closeout.

### 1.4 Verdict register

Per sub-spec §2.5: explicit "what this arc establishes" + "what
this arc does not establish" framing per spec §3.2 hard scope
boundaries + §9 risks-and-out-of-scope items.

**What PHASE2C_9 establishes**:

- §3 mechanism reconstruction at file:line citation register
  (Proposer prompt + Critic gate + theme rotation; ingest-layer
  out-of-scope)
- §4 artifact-distribution audit at canonical-anchor cross-check
  register (198 valid candidates verified at three independent
  measurement points; per-theme valid_count distribution
  40/40/40/39/39; total_actual_cost_usd = $2.30; lifecycle-state
  distribution table)
- §5 theme × pass-count cross-tab reproducing PHASE2C_8.1 §7.1
  byte-for-byte across 5 themes × 4 regimes (theme totals
  40/40/40/39/39 + per-regime totals 13/87/74/38; 4-axis
  canonical-number cross-checks pass)
- §6 lone-survivor walkthrough at end-to-end mining-process trace
  register (hash `0845d1d7898412f2`; theme `volume_divergence`;
  batch position 39; audit-only partition origin verified at
  `wf_test_period_sharpe = -0.072 < 0.5`; engine lineage
  `eb1c87f` / `wf-corrected-v1` cross-checked across 4 regimes)
- §7 evidence maps for Case A.1-A.4 / B.1-B.3 / C.1-C.3
  sub-registers (cumulative-11 carry-forward observations all
  explicitly cited at §7.0.0 inventory + §7.0-§7.2 prose)
- §8 case determination per §4.4 mechanical-procedure application
  (Case C with sub-registers C.1 + C.2 + C.3 documented;
  derivation chain at §8.0; sub-register documentation at §8.1)
- §8.3 tracked-fix register entries surfaced (Q-9-01 ingest-layer
  mechanism reconstruction; Q-9-02 evidence asymmetry that
  produced Case C determination)
- §8.4 methodology-codification candidates surfaced (5 entries;
  4 mandatory cumulative + 1 emergent from Step 6 cycle; each
  at status-register precision per Concern L disposition)

**What PHASE2C_9 does not establish**:

- New candidate generation or evaluation outputs (per §3.2.1 +
  §3.2.2 hard scope boundaries)
- Statistical-significance discrimination of noise-floor-vs-
  systematic-pattern (Q-9.A territory; out-of-scope per §3.2.5)
- Calibration-variation grid outputs (Q-9.C territory; out-of-scope
  per §3.2.6)
- Phase 3 progression scoping (Q-9.D territory; out-of-scope per
  §3.2.7)
- Mining-process redesign proposals (out-of-scope per §3.2.4)
- Successor scoping cycle direction (per §4.4 + §7.2 + §7.4
  anti-pre-naming discipline)
- Ingest-layer mechanism reconstruction (out-of-scope per §3 +
  §7.4 register-precision Obs 2 + Q-9-01 tracked-fix register;
  structured re-examination scope)
- Resolution of A.4 qualifying-vs-disqualifying balance ambiguity
  at deeper register than light-touch (deferred per §1.2
  link-point 1 falsifiability counterfactual)


## 2. Scope and methodology

Per sub-spec §3 + §4 + spec §8 canonical structure §2 sub-section
enumeration: §2.0 arc setup + §2.1 input universe + §2.2 hard
scope boundaries + §2.3 pre-registered exit conditions + §2.4
verification framework. Mirror of PHASE2C_9_PLAN.md §2 + §3 + §4
+ §6 at canonical anchor register; cross-references at §9.0.

### 2.0 Arc setup

PHASE2C_9 implementation arc per
[`PHASE2C_9_PLAN.md`](../phase2c/PHASE2C_9_PLAN.md) (commit
`8aa1c66`) + Step 6 sub-spec
[`PHASE2C_9_STEP6_SUBSPEC.md`](../phase2c/PHASE2C_9_STEP6_SUBSPEC.md)
(commit `d1657bd`). Six-step sequential gating: Step 1 mechanism
reconstruction (sealed `13be4ff`) → Step 2 artifact-distribution
audit (sealed `777ea3c`) → Step 3 theme × pass-count cross-tab
(sealed `c3a2f20`) → Step 4 lone-survivor walkthrough (sealed
`1d069ba`) → Step 5 §7 evidence maps (sealed `d548ea2`) → Step 6
case determination + closeout assembly (this commit cycle).
Pre-fire Concern N audit CLEAN at session-close (5 sequencing
checks pass against verbatim sub-spec §5.2 prose).

### 2.1 Input universe

Per
[`PHASE2C_9_PLAN.md`](../phase2c/PHASE2C_9_PLAN.md) §2 input
universe enumeration: §2.1 code artifacts (Proposer + Critic + theme
rotation source); §2.2 batch artifact files (canonical batch
`b6fcbf86-4d57-4d1f-ae41-1778296b1ae9`); §2.3 evaluation artifact
files (PHASE2C_6 / PHASE2C_7.1 / PHASE2C_8.1 outputs); §2.4
canonical-number anchors (PHASE2C_8.1 closeout-derived); §2.5
operational themes (5 themes in operational rotation;
`multi_factor_combination` excluded per CONTRACT BOUNDARY).

### 2.2 Hard scope boundaries

Per
[`PHASE2C_9_PLAN.md`](../phase2c/PHASE2C_9_PLAN.md) §3 in-scope
✔ + out-of-scope ❌ enumeration. Bright-line summary table at
§3.3.

### 2.3 Pre-registered exit conditions

Per
[`PHASE2C_9_PLAN.md`](../phase2c/PHASE2C_9_PLAN.md) §4 Case A.1-A.4
/ §4.2 B.1-B.3 / §4.3 C.1-C.3 sub-register evidence-pattern
register + §4.4 one-and-only-one rule. §4 case definitions frozen
at spec commit; mid-arc rewrite forbidden per spec §4
pre-registration discipline.

### 2.4 Verification framework

Per
[`PHASE2C_9_PLAN.md`](../phase2c/PHASE2C_9_PLAN.md) §6
verification framework: §6.1 evidence-mapping discipline; §6.2
falsifiability-statement discipline; §6.3 canonical-number
cross-checks; §6.4 cycle-boundary-preservation language audit;
§6.5 independent-recompute gate (light-touch register; no new
canonical numbers; no new test required). §9.2 §9 verification
framework audit checklist at final-commit register.


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

This section constructs the theme × regime × pass-count cross-tab
from two canonical inputs: (1) PHASE2C_8.1 closeout §7.1 per-theme
AND-gate pass counts at unfiltered tier across the 4 evaluation
regimes; (2) §4.0 generation-side per-theme distribution (40/40/40/39/39
valid_count). Per spec §3.1.5 operational disambiguation, this is
**factual cross-tab description + asymmetry observation surfacing**,
not statistical-significance testing. Output register: cross-tab
cardinalities + mechanical asymmetry observations + canonical-number
cross-checks. Mechanism interpretation deferred to §7 (Step 5);
lone-survivor walkthrough deferred to §6 (Step 4); case adjudication
deferred to §8 (Step 6).


### 5.0 Cross-tab construction

**Source artifacts**:
- PHASE2C_8.1 closeout §7.1 (per-theme AND-gate pass counts at
  unfiltered tier) at
  [`docs/closeout/PHASE2C_8_1_RESULTS.md:941-947`](PHASE2C_8_1_RESULTS.md#L941-L947)
- §4.0 generation-side per-theme distribution (`per_theme` array
  from `stage2d_summary.json`)

**Cross-tab: theme × regime × unfiltered AND-gate pass count**:

| Theme | Generation (n_calls) | Generation (valid_count) | bear_2022 | validation_2024 | eval_2020_v1 | eval_2021_v1 | Sum across regimes |
|---|---|---|---|---|---|---|---|
| calendar_effect | 40 | 40 | 6 | 24 | 26 | 10 | 66 |
| volume_divergence | 40 | 40 | 4 | 25 | 23 | 12 | 64 |
| volatility_regime | 40 | 40 | 0 | 4 | 10 | 2 | 16 |
| momentum | 40 | 39 | 3 | 21 | 12 | 6 | 42 |
| mean_reversion | 40 | 39 | 0 | 13 | 3 | 8 | 24 |
| **Column total** | **200** | **198** | **13** | **87** | **74** | **38** | **212** |

**Cross-tab cell semantics**:
- Each cell at row `theme` × column `regime` is the count of
  candidates of that theme that passed the unfiltered 4-criterion
  AND-gate in that regime
- "Sum across regimes" column: per-theme cumulative pass count
  (each candidate counted once per regime where it passed; a
  candidate passing 4 regimes contributes 4)
- "Column total" row: per-regime overall pass count (matches
  PHASE2C_8.1 closeout §3.3 per-regime AND-gate cardinalities)
- Cross-tab cell-sum total (212) is per-regime-pass total; it is
  NOT the joint-pass cardinality (the 21-vs-8 in-sample-caveat
  asymmetry at PHASE2C_8.1 §5.2 is joint-pass cardinality across
  category; this cross-tab is independent-per-cell pass count)

### 5.1 Per-theme pass-count asymmetry observations

Mechanical asymmetry observations from the cross-tab cells. Each
observation is a factual cardinality report; mechanism
interpretation deferred to §7.

**Observation 1 — `volatility_regime` shows lowest pass rates
across all regimes**: pass counts of 0/40, 4/40, 10/40, 2/40 in
bear_2022 / validation_2024 / eval_2020_v1 / eval_2021_v1
respectively. Sum-across-regimes total of 16 is lowest among the
5 themes; per-regime maxima are also among the lowest.

**Observation 2 — `mean_reversion` shows zero-pass in bear_2022
plus mid-range elsewhere**: pass counts of 0/39, 13/39, 3/39, 8/39
in the four regimes. The 0/39 bear_2022 cell matches PHASE2C_8.1
§7.2 Observation A "volatility_regime and mean_reversion show 0/40
and 0/39 zero-pass counts" in bear_2022.

**Observation 3 — `calendar_effect` shows highest concentration in
eval_2020_v1**: 26/40 = 65% pass rate, the highest single cell in
the cross-tab. The validation_2024 pass count is also high at
24/40 = 60%; eval_2021_v1 pass count is 10/40 = 25%; bear_2022
pass count is 6/40 = 15%.

**Observation 4 — `volume_divergence` shows highest validation_2024
pass count**: 25/40 = 62.5%, the highest validation_2024 cell.
This matches PHASE2C_8.1 §7.2 Observation B "maximum theme pass
count in validation_2024 is 25/40 (volume_divergence)."

**Observation 5 — `momentum` shows lowest concentration in
bear_2022**: 3/39 = 7.7% pass rate. The remaining three regimes
show 21/39 = 53.8% (validation_2024), 12/39 = 30.8% (eval_2020_v1),
6/39 = 15.4% (eval_2021_v1).

**Observation 6 — bear_2022 column shows uniformly low pass counts**:
maximum cell is 6/40 (calendar_effect); 2 themes show zero passes
(volatility_regime + mean_reversion). The bear_2022 column total
of 13/198 = 6.6% is the lowest per-regime pass rate across the 4
evaluation regimes.

**Observation 7 — validation_2024 column shows highest pass counts
overall**: column total 87/198 = 43.9%. Per-theme distribution at
this column: calendar_effect 24, volume_divergence 25, momentum 21,
mean_reversion 13, volatility_regime 4. Spread across themes
ranges 4-25.

**Observation 8 — eval_2020_v1 vs eval_2021_v1 train-overlap
divergence**: column totals are 74/198 (eval_2020_v1) and 38/198
(eval_2021_v1). Per-theme distribution diverges substantially:
calendar_effect 26/10; volume_divergence 23/12; volatility_regime
10/2; momentum 12/6; mean_reversion 3/8. eval_2020_v1 column total
is roughly 2x eval_2021_v1 column total. This matches PHASE2C_8.1
§7.2 Observation C "within-train-overlap pass-rate heterogeneity
is observed at theme-level cross-tab."

**Observation 9 — train-overlap regime sum vs fully-OOS regime
sum (per-regime cell totals)**: train-overlap regimes
(eval_2020_v1 + eval_2021_v1) sum to 74 + 38 = 112 cell-passes;
fully-OOS regimes (bear_2022 + validation_2024) sum to 13 + 87 =
100 cell-passes. The cell-pass-total parity is approximate (112 vs
100); per-cell distribution is asymmetric across themes. This is
the per-regime-pass cell-total comparison; it is NOT the
21-vs-8 joint-pass cardinality at PHASE2C_8.1 §5.2 (which counts
candidates passing both regimes within a category).

### 5.2 Canonical-number cross-checks

Cross-checks at four axes:

**Axis 1 — Theme totals match §4.0 generation-side distribution**:

| Theme | §4.0 valid_count | §5.0 cross-tab Generation valid_count | match |
|---|---|---|---|
| calendar_effect | 40 | 40 | ✓ |
| volume_divergence | 40 | 40 | ✓ |
| volatility_regime | 40 | 40 | ✓ |
| momentum | 39 | 39 | ✓ |
| mean_reversion | 39 | 39 | ✓ |
| **Total** | **198** | **198** | ✓ |

**Axis 2 — Per-regime totals match PHASE2C_8.1 closeout §3.3 + §7.1**:

| Regime | §5.0 column total | PHASE2C_8.1 §3.3 anchor | match |
|---|---|---|---|
| bear_2022 | 13 | 13 | ✓ |
| validation_2024 | 87 | 87 | ✓ |
| eval_2020_v1 | 74 | 74 | ✓ |
| eval_2021_v1 | 38 | 38 | ✓ |

**Axis 3 — Cell-by-cell match against PHASE2C_8.1 §7.1 source
table**: All 20 cells (5 themes × 4 regimes) reproduce
PHASE2C_8.1 closeout §7.1 byte-for-byte at
[`docs/closeout/PHASE2C_8_1_RESULTS.md:941-947`](PHASE2C_8_1_RESULTS.md#L941-L947).
No cell drift detected; cross-tab construction inherits canonical
numbers exactly.

**Axis 4 — Generation-side `n_calls` to `valid_count` reconciliation**:
calendar_effect / volume_divergence / volatility_regime show
n_calls=40 = valid_count=40 (zero rejected_complexity). momentum +
mean_reversion show n_calls=40 + 1 rejected_complexity each =
valid_count=39. §4.0 lifecycle distribution + per-theme
distribution are internally consistent with §5.0 cross-tab
Generation columns. ✓

All canonical-number cross-checks pass.

### 5.3 Step 3 deliverable summary + gating-criterion check

Per spec §5.3 gating criterion: **"§5 working draft has the
cross-tab with all canonical anchor cross-checks satisfied"**.

Status:

- **Cross-tab constructed** (§5.0): 5 themes × 4 regimes + Generation
  + Sum-across-regimes columns + Column-total row; 20 cells
  reproduce PHASE2C_8.1 §7.1 byte-for-byte ✓
- **Per-theme asymmetry observations documented** (§5.1): 9
  observations at mechanical-cardinality register; cross-references
  to PHASE2C_8.1 §7.2 observations where applicable ✓
- **Canonical-number cross-checks pass** (§5.2): 4 axes — theme
  totals match §4.0; per-regime totals match PHASE2C_8.1 §3.3 +
  §7.1; cell-by-cell match against PHASE2C_8.1 §7.1; generation-
  side n_calls/valid_count internally consistent ✓

Step 3 gating criterion satisfied. Step 4 (lone-survivor walkthrough
per spec §5.4) authorized to proceed in subsequent session per
discrete-session-boundary register.

Per spec §6 verification framework + §7 cycle-boundary preservation:

- **§6.1 Evidence-mapping discipline**: every cross-tab cell cited
  at PHASE2C_8.1 §7.1 source; canonical-number cross-checks at
  file:line register; no narrative claims without artifact reference ✓
- **§6.4 Cycle-boundary-preservation language audit**: §5 contains
  no forbidden forward-pointer language; no "this suggests" / "this
  implies" / "this may indicate Case X" interpretation language;
  observations are mechanical cardinality reports only ✓
- **§6.3 Canonical-number cross-checks**: 4-axis cross-check passes
  including byte-for-byte 20-cell reproduction of PHASE2C_8.1 §7.1 ✓

Scope-completeness audit per Claude advisor's Consideration 3
carry-forward (necessary-and-sufficient register; no §6 / §7-§8
deliverable leakage):

- **§5 does NOT include lone-survivor walkthrough** (Step 4 §6
  territory). The lone-survivor reference at PHASE2C_8.1 §7.3
  ("`0845d1d7898412f2` is one of 4 volume_divergence candidates
  passing in bear_2022") is mentioned only in cross-tab cell
  context (`volume_divergence × bear_2022 = 4`); detailed trace
  deferred to §6.
- **§5 does NOT include Case A/B/C adjudication** (Step 6 §8
  territory). Asymmetry observations at §5.1 are mechanical
  cardinality reports; mechanism-vs-observation comparison + case
  determination deferred to §7 + §8.
- **§5 does NOT include statistical-significance testing**
  (Q-9.A territory; out-of-scope per spec §3.2.5). Cross-tab cells
  are factual cardinalities; pass-rate asymmetries are described at
  cardinality register without significance claims.

**Two register-precision observations surfaced for §7 (Step 5)
mechanism-vs-observation comparison register**:

1. **Train-overlap regime divergence** (§5.1 Observation 8):
   eval_2020_v1 column total (74) is roughly 2x eval_2021_v1
   column total (38) at per-theme level; the divergence is
   theme-distributional, not uniform. Mechanism intersection at
   §3 (Proposer/Critic produces candidate population) × §7
   (mechanism comparison may invoke this for Case A.X / B.X /
   C.X evidence at register).
2. **Per-regime pass-rate range across themes**: bear_2022 cells
   span 0-6 (range 6); validation_2024 cells span 4-25 (range 21);
   eval_2020_v1 cells span 3-26 (range 23); eval_2021_v1 cells
   span 2-12 (range 10). The validation_2024 + eval_2020_v1 ranges
   are roughly 2-3x bear_2022 + eval_2021_v1 ranges; the per-regime
   spread itself is asymmetric. §7 may invoke for evidence-base
   register.

Observations are mechanism observations for §7 carry-forward, NOT
§5 evidence claims pre-empting §7 adjudication.




## 6. Lone-survivor walkthrough (Step 4 deliverable)

This section traces the lone unfiltered cross-regime survivor
`0845d1d7898412f2` (`volume_surge_momentum_entry`, theme
`volume_divergence`) end-to-end through the mining-process
pipeline: generation-side prompt + response → compilation manifest
→ Critic gate trace → per-regime evaluation summaries (all 4
PHASE2C regimes) → audit-only partition origin + single-trade-
margin filter exclusion in bear_2022. Per spec §3.1.6 operational
disambiguation, this is **single-candidate trace** for the
empirically-distinguished cohort_a_unfiltered=1 case, not generic
walkthrough; mechanism interpretation deferred to §7 (Step 5).
Output register: factual end-to-end trace at file:line citation.


### 6.0 Generation-side trace

**Canonical batch position**: 39 (out of 200 attempts in canonical
batch `b6fcbf86-...`).

**Theme rotation cross-check**: per §3.3.2 rotation formula
`THEMES[(k - 1) % THEME_CYCLE_LEN]` with `THEME_CYCLE_LEN = 5` at
[`agents/proposer/stage2d_batch.py:112`](../../agents/proposer/stage2d_batch.py#L112)
+ canonical THEMES tuple at
[`agents/themes.py:22-29`](../../agents/themes.py#L22-L29):
`(39 - 1) % 5 = 3`; `THEMES[3] = "volume_divergence"`. Matches the
candidate's theme assignment. ✓

**Source artifact**: `raw_payloads/batch_b6fcbf86-4d57-4d1f-ae41-1778296b1ae9/attempt_0039_prompt.txt`
(77 lines).

**Prompt structure** (per §3.1.3 prompt builder mechanism):

- System prompt at lines 1-42 inherits the canonical structure
  documented at §3.1.3: schema-shape positive block (lines 12-33);
  synonym-rejection negative block (lines 35-40); markdown-fence
  prohibition (line 42). Mechanism reproduction matches
  [`agents/proposer/prompt_builder.py:134-194`](../../agents/proposer/prompt_builder.py#L134-L194)
  exactly.
- User prompt block at lines 43-57:
  - `batch_id: b6fcbf86-4d57-4d1f-ae41-1778296b1ae9` (line 44)
  - `position: 39/200` (line 45)
  - `theme (rotating): volume_divergence` (line 46)
  - Recent batch signal (lines 48-51): `dedup rate so far: n/a`;
    `top factors by frequency: (no signal yet)`; `critic rejections
    in last 50: n/a` (these "n/a" / "no signal yet" defaults
    indicate position 39 within first 50 of the batch; aggregate
    signals reset at each batch start)
  - 3 approved-example DSL strings at lines 53-55 (themes
    `volatility_regime` / `mean_reversion` / `momentum`; provided
    as DSL-only examples per §3.1.3 contract; no metrics)
  - Final directive: `Propose hypothesis #39.` (line 57)
- Factor menu at lines 58-77 inherits factor list at
  [`factors/registry.py`](../../factors/registry.py) mechanism
  (per §3.1.3 `factor_menu = reg.menu_for_prompt()` at
  [`agents/proposer/prompt_builder.py:132`](../../agents/proposer/prompt_builder.py#L132));
  18 factors across categories (volatility / volume / momentum /
  moving_averages / returns / structural / price)

**Source artifact**: `raw_payloads/batch_b6fcbf86-4d57-4d1f-ae41-1778296b1ae9/attempt_0039_response.txt`
(32 lines).

**Response structure**: markdown-fenced JSON object (line 1
` ```json ` opening fence and line 32 ` ``` ` closing fence). Per
§3.1.2 generate() mechanism, the markdown fence is stripped by
`classify_raw_json` in
[`agents/proposer/sonnet_backend.py:325-330`](../../agents/proposer/sonnet_backend.py#L325-L330)
before classification.

**DSL content** (post-fence-strip):

- `name`: `volume_surge_momentum_entry`
- `description`: 1-sentence economic rationale citing volume
  divergence + momentum continuation + institutional flow narrative
- `entry`: 1 group with 4 conditions (`volume_zscore_24h > 2.0`;
  `return_24h > 0.01`; `macd_hist crosses_above 0.0`;
  `close > sma_20`)
- `exit`: 2 groups (group 1: `return_24h > 0.04` AND
  `volume_zscore_24h < 0.0`; group 2: `macd_hist crosses_below 0.0`
  AND `return_1h < -0.015`)
- `position_sizing`: `full_equity`
- `max_hold_bars`: 168

**Theme alignment at generation register**: prompt theme is
`volume_divergence`; response uses `volume_zscore_24h` (which is
the single factor in `THEME_HINTS["volume_divergence"]` per
[`agents/proposer/stage2d_batch.py:117-129`](../../agents/proposer/stage2d_batch.py#L117-L129)
shared mechanism with Stage 2c). The DSL also uses 3 non-theme-
hint factors (`return_24h`, `macd_hist`, `close`) and 1 non-theme-
hint factor in entry's `value` field (`sma_20`).


### 6.1 Compilation manifest

**Source artifact**: `data/compiled_strategies/9928d031d6d19eb0af8aa929e077fe62f3e15af386aeccf16e205bc377306f25.json`
(located by `grep -l "volume_surge_momentum_entry" data/compiled_strategies/*.json`).

**Manifest filename note + spec-vs-empirical-reality finding**:
compiled-strategy manifest filename is the 64-character SHA-256 of
the canonical-DSL-string at
[`agents/hypothesis_hash.py`](../../agents/hypothesis_hash.py)
register (full hash for this candidate:
`9928d031d6d19eb0af8aa929e077fe62f3e15af386aeccf16e205bc377306f25`);
this is structurally distinct from the 16-character
`hypothesis_hash` field used in evaluation outputs and PHASE2C_8.1
closeout (`0845d1d7898412f2`). Both hashes refer to the same
candidate; the 16-char form is the truncation pattern used
downstream of compilation in evaluation outputs.

The spec at
[`PHASE2C_9_PLAN.md`](../phase2c/PHASE2C_9_PLAN.md) §2.2 +
§5.4 references the manifest as
`data/compiled_strategies/0845d1d7898412f2.json` (using the 16-char
form); this path does NOT exist on disk. The actual manifest is
located at the 64-char SHA-256 path above. This is the third spec-
vs-empirical-reality register-precision finding in PHASE2C_9 cycle
(after PHASE2C_10 pre-naming at spec drafting + Stage 2c → Stage
2d at Step 2 §4.2). Located in this section by content cross-
reference: `grep -l "volume_surge_momentum_entry"
data/compiled_strategies/*.json` returns the canonical manifest
file. Spec amendment to the 64-char form is out-of-scope for §6
(spec amendment is a separate cycle); finding documented here at
register-precision register for downstream awareness.

**Manifest fields** (per spec §10 compilation manifest contract):

| field | value | source line |
|---|---|---|
| `canonical_dsl.name` | `volume_surge_momentum_entry` | line 61 |
| `compiler_sha` | `b0acd515ee2cf1b0cc549b3d1c4a93c6fc64187523104ee4226ada80a5e71303` | line 65 |
| `feature_version` | `14e725c9845d95d0ca3a1c54b77582e34921b8ed7cf928445e4ae3c4764127c7` | line 140 |
| `factor_snapshot` length | 18 factors with warmup_bars | lines 66-139 |
| `written_at_utc` | `2026-04-26T06:50:52.991246Z` | line 142 |

**Pseudo-code** (line 141): documents the strategy at human-
readable register:

```
strategy 'volume_surge_momentum_entry' (...)
  position_sizing: full_equity
  max_hold_bars: 168
  ENTRY when (any of):
    [1] volume_zscore_24h > 2 AND return_24h > 0.01
        AND macd_hist crosses_above 0 AND close > sma_20
  EXIT when (any of):
    [1] return_24h > 0.04 AND volume_zscore_24h < 0
    [2] macd_hist crosses_below 0 AND return_1h < -0.015
```

**Compilation invariant cross-check** (per §3.1.4 / §3.3
mechanism): the manifest `canonical_dsl` block at lines 2-63 is
structurally identical to the response payload at
attempt_0039_response.txt post-fence-strip. The compiler's
canonical-DSL ordering (alphabetical-by-key serialization at line
64 `canonical_dsl_string`) matches the
[`agents/hypothesis_hash.py`](../../agents/hypothesis_hash.py)
canonicalization contract. The lone-survivor's 4 conditions in
entry + 2 exit groups (with 2 conditions each) satisfy DSL
complexity budget per §3.1 (entry/exit ≤ 3 groups; ≤ 4 conditions
per group).


### 6.2 Critic gate trace

**Critic operational at canonical batch (descriptive)**: the
canonical batch `b6fcbf86-...` was Stage 2d (per §4.2 stage
attribution + §3.1.4 shared-mechanism reference). Stage 2d
mechanism inherits the same Critic invocation pattern as Stage 2c
(per §3.3.2 shared-mechanism documentation): `run_critic()` is
invoked per candidate at the orchestrator ingest layer,
post-Proposer + pre-walk-forward. Critic mode at batch
`b6fcbf86-...` was canonical (D7 v1; per
[`agents/critic/orchestrator.py:23`](../../agents/critic/orchestrator.py#L23)
`CRITIC_VERSION = "d7_v1"`).

**Lifecycle path checkpoint verification**: lone-survivor's
lifecycle path (from §4 + §6 evidence):

| stage | lifecycle state | source |
|---|---|---|
| post-Proposer / post-Critic / post-ingest | `pending_backtest` | §4.0 lifecycle_counts (198 candidates including this one) |
| post-walk-forward / per-regime evaluation | `holdout_passed` (4×; per regime) | 4 holdout_summary.json artifacts at evaluation paths |

The candidate advanced through every checkpoint of the mining-
process pipeline: Proposer emitted valid DSL (verified by
manifest cross-check at §6.1); ingest layer assigned
`pending_backtest` (verified by §4.0 lifecycle distribution
membership in the 198 count); walk-forward + per-regime
evaluation produced `holdout_passed` in all 4 regimes (verified
by 4 holdout_summary.json artifacts at §6.3).

Per §3.2 mechanism reconstruction, `run_critic()` at
[`agents/critic/orchestrator.py:95-203`](../../agents/critic/orchestrator.py#L95-L203)
annotates only — it does not assign lifecycle states. Lifecycle-
state assignment is performed by the orchestrator ingest layer
(per §3.2.6). The candidate's `pending_backtest` assignment by
ingest layer is the load-bearing signal that Critic gate did not
reject this candidate (D7a rule scores + D7b semantic scores
collectively did not trigger ingest-layer rejection).

**Per-regime evaluation summary `lifecycle_state` field**: all 4
holdout_summary.json artifacts (audit_v1 / audit_2024_v1 /
eval_2020_v1 / eval_2021_v1) report `lifecycle_state =
"holdout_passed"`. This is the post-evaluation lifecycle register
(distinct from mining-time `pending_backtest` register at §4.0).

The lone-survivor's path through the Critic gate is therefore:

1. Proposer emits valid DSL → ingest layer assigns
   `pending_backtest` (mining-time terminal state)
2. Walk-forward evaluation runs (PHASE2C_5)
3. Per-regime evaluation evaluates against 4-criterion AND-gate
   per regime
4. holdout_summary.json records `lifecycle_state =
   "holdout_passed"` per regime if AND-gate satisfied

The detailed Critic annotation (D7a rule scores, D7b semantic
scores, reasoning, scan_results) is not surfaced in
holdout_summary.json artifacts. Detailed Critic-output trace would
require reading
[`agents/critic/replay.py`](../../agents/critic/replay.py)
reconstruction artifacts which are out-of-scope for §6 single-
candidate end-to-end trace at spec §3.1.6 register. Surfaced as
carry-forward to §7 if mechanism-vs-observation comparison invokes
Critic-output mechanism for evidence interpretation.


### 6.3 Evaluation-side trace cross-reference

**Per-regime AND-gate evaluation results** (from 4
`holdout_summary.json` artifacts at
`data/phase2c_evaluation_gate/{run_id}/0845d1d7898412f2/holdout_summary.json`):

| Regime | run_id | Sharpe | Total Return | Max DD | Trades | AND-gate | trade ≥ 20 filter | Filtered cohort |
|---|---|---|---|---|---|---|---|---|
| bear_2022 | `audit_v1` | 0.508 | +6.80% | 0.095 | 19 | PASS | **FAIL (19<20)** | **EXCLUDED** |
| validation_2024 | `audit_2024_v1` | 1.053 | +18.3% | 0.172 | 23 | PASS | PASS (23≥20) | PRESENT |
| eval_2020_v1 | `eval_2020_v1` | 0.813 | +18.6% | 0.245 | 27 | PASS | PASS (27≥20) | PRESENT |
| eval_2021_v1 | `eval_2021_v1` | -0.358 | -10.2% | 0.232 | 29 | PASS | PASS (29≥20) | PRESENT |

**Precision note**: numeric precision in the table above matches
PHASE2C_8.1 closeout §6.1 anchor precision (Sharpe 3-decimal; Max
DD 3-decimal; Return 1-decimal except bear_2022 at 2-decimal per
anchor). Underlying canonical values from holdout_summary.json
artifacts have additional precision (e.g.,
bear_2022 Sharpe = 0.5081590272487263; full precision retrievable
at source-artifact register). Table-level precision matches
upstream-anchor per anchor-list discipline at METHODOLOGY_NOTES §15.

All 4 cells reproduce per-regime metrics from the corresponding
holdout_summary.json artifacts at
`data/phase2c_evaluation_gate/{audit_v1, audit_2024_v1, eval_2020_v1, eval_2021_v1}/0845d1d7898412f2/holdout_summary.json`.

**AND-gate criteria** (from `passing_criteria` field, identical
across all 4 summaries):
- `min_sharpe`: -0.5
- `min_total_return`: -0.15
- `max_drawdown`: 0.25
- `min_total_trades`: 5

**`gate_pass_per_criterion` field** (4 booleans per regime): all
four criteria pass simultaneously in all 4 regimes —
`drawdown_passed`, `return_passed`, `sharpe_passed`,
`trades_passed` all `true` per regime.

**Filter-exclusion verification** (cardinality check):
`data/phase2c_evaluation_gate/audit_v1_filtered/0845d1d7898412f2/`
does NOT exist on disk (mechanically verified by `ls`); the
lone-survivor is absent from `audit_v1_filtered` directory (148
members; lone-survivor not among them). This empirically confirms
the single-trade-margin filter exclusion in bear_2022 (19 trades
< 20-trade threshold per the trade-count filter sub-pass at
PHASE2C_7.1 §5).

The candidate IS present in `audit_2024_v1_filtered`,
`eval_2020_v1_filtered`, `eval_2021_v1_filtered` directories
(verified by `ls`); filter cohort membership confirmed in 3 of 4
regimes. Filter exclusion exclusively in bear_2022 by single-
trade-margin.

**Audit-only partition origin verification**: all 4
holdout_summary.json artifacts report `wf_test_period_sharpe =
-0.071638` (identical value across regimes, since this is the
PHASE2C_5 walk-forward test-period Sharpe fixed at PHASE2C_5
generation cycle). Per PHASE2C_8.1 closeout §6.3 audit-only
partition origin documentation: -0.072 < 0.5 primary threshold
relegated this candidate to audit partition during PHASE2C_6
arc. Audit partition origin verified at file:line register.

**Engine lineage cross-check**: all 4 summaries report
`engine_commit = "eb1c87f"` and `engine_corrected_lineage =
"wf-corrected-v1"`; `lineage_check = "passed"`. The corrected WF
engine (post-correction) is the engine that produced these
evaluation outputs.

**Per-regime artifact schema discriminator**:
- audit_v1 (PHASE2C_6): no `artifact_schema_version` field
  (PHASE2C_6 pre-dates schema versioning); evaluation_semantics =
  "single_run_holdout_v1"
- audit_2024_v1 (PHASE2C_7.1): `artifact_schema_version =
  "phase2c_7_1"`
- eval_2020_v1 / eval_2021_v1 (PHASE2C_8.1):
  `artifact_schema_version = "phase2c_8_1"` (train-overlap regime
  discriminator)


### 6.4 Step 4 deliverable summary + gating-criterion check

Per spec §5.4 gating criterion: **"§6 working draft has end-to-end
trace with all relevant artifacts cited at file:line citation
register"**.

Status:

- **Generation-side trace** (§6.0): batch position 39; theme
  rotation cross-check verified; prompt + response artifacts cited
  at file:line; theme alignment documented (1 theme-hint factor +
  3 non-theme-hint factors in entry); mechanism cross-references
  to §3.1.3 prompt builder ✓
- **Compilation manifest** (§6.1): manifest located by name
  cross-reference; canonical_dsl + compiler_sha + feature_version
  + factor_snapshot + pseudo_code documented at field-level
  citation; canonical-DSL-string structural identity to response
  payload verified ✓
- **Critic gate trace** (§6.2): lifecycle-state path documented
  (Proposer → ingest → pending_backtest → walk-forward →
  holdout_passed); Critic annotation (D7a/D7b) deferred to §7 if
  mechanism-vs-observation comparison invokes Critic-output
  mechanism ✓
- **Evaluation-side trace** (§6.3): all 4 per-regime
  holdout_summary.json artifacts cited at file:line; per-regime
  metrics + AND-gate criteria + filter cohort membership verified
  across 4 regimes; single-trade-margin filter exclusion in
  bear_2022 verified by `audit_v1_filtered` directory absence;
  audit-only partition origin verified by wf_test_period_sharpe =
  -0.072 < 0.5; engine lineage verified ✓

Step 4 gating criterion satisfied. Step 5 (mechanism-vs-observation
comparison per spec §5.5) authorized to proceed in subsequent
session per discrete-session-boundary register.

Per spec §6 verification framework + §7 cycle-boundary preservation:

- **§6.1 Evidence-mapping discipline**: every cited fact at
  file:line or source-key register; no narrative claims without
  artifact reference ✓
- **§6.4 Cycle-boundary-preservation language audit**: §6 contains
  no forbidden forward-pointer language; no Case A/B/C
  adjudication; no "this suggests / implies / may indicate"
  interpretation language; trace-only register ✓
- **§6.3 Canonical-number cross-checks**: hash + theme + name +
  position + audit-only partition origin all cross-checked at
  source-artifact register; per-regime metrics all cited from
  holdout_summary.json artifacts ✓

Scope-completeness audit per Claude advisor's Consideration 3
carry-forward (necessary-and-sufficient register; no §7-§8
deliverable leakage):

- **§6 does NOT include 198-candidate full re-analysis** (per spec
  §3.2.3); single-candidate trace only ✓
- **§6 does NOT include illustrative non-survivor traces** (spec
  §3.2.3 caveat allows up to 1-2 illustrative non-survivors if
  exemplifying population pattern; §6 chose single-candidate
  bounded scope; non-survivor traces are out-of-scope at this
  register) ✓
- **§6 does NOT include Case A/B/C adjudication** (Step 6 §8
  territory) ✓
- **§6 does NOT include §7 mechanism interpretation** — the
  observed pattern (passed unfiltered AND-gate in 4/4 regimes;
  excluded from filtered cohort_a in bear_2022 by single-trade
  margin; eval_2021_v1 AND-gate-passing despite -10.2% return) is
  factual trace; mechanism-vs-evidence comparison deferred to §7 ✓

**Three substantive observations surfaced for §7 (Step 5)
mechanism-vs-observation comparison register**:

1. **Single-trade-margin filter exclusion in bear_2022**: lone-
   survivor's 19 trades vs ≥20-trade filter threshold = 1-trade
   margin. The filter-exclusion-by-single-trade-margin pattern
   bears on §7 evidence register (whether mining-time → filter-
   time alignment is part of mining-process design vs whether the
   trade-count filter threshold itself is calibration-register
   concern). Cross-arc carry-forward also relevant: PHASE2C_8.1
   closeout §6.2 surfaced this as the load-bearing exclusion mode.
2. **eval_2021_v1 AND-gate-passing with -10.2% total_return**:
   gate criteria Sharpe ≥ -0.5 (actual: -0.358) AND total_return
   ≥ -0.15 (actual: -0.102) AND max_dd ≤ 0.25 (actual: 0.231)
   AND trades ≥ 5 (actual: 29) all satisfied. The permissive AND-
   gate accepting negative-Sharpe + negative-double-digit-return
   as "holdout_passed" bears on §7 evidence register (whether this
   reflects gate calibration vs mining-process candidate-quality
   register). Cross-arc carry-forward: PHASE2C_8.1 closeout §6.0
   surfaced this as the "permissive AND-gate accepts -10.2%
   return" finding.
3. **Theme alignment at generation register**: per §3.2.3 D7a
   `extract_factors()` at
   [`agents/critic/d7a_feature_extraction.py:86-100`](../../agents/critic/d7a_feature_extraction.py#L86-L100),
   the factor set scans both entry AND exit condition groups +
   includes string-typed `cond.value` (RHS factor-vs-factor). For
   the lone-survivor's DSL: entry factors `{volume_zscore_24h,
   return_24h, macd_hist, close, sma_20}` (5 distinct, including
   `sma_20` from `close > sma_20`); exit factors `{return_24h,
   volume_zscore_24h, macd_hist, return_1h}` (4 distinct, with
   3 already in entry). Union: `{volume_zscore_24h, return_24h,
   macd_hist, close, sma_20, return_1h}` = 6 distinct factors.
   `THEME_HINTS["volume_divergence"] = {volume_zscore_24h}` per
   [`agents/proposer/stage2d_batch.py:117-129`](../../agents/proposer/stage2d_batch.py#L117-L129)
   (1 factor; thin-theme register per §3.2.3 `THIN_THEMES`).
   Per §3.2.2 D7a `theme_coherence` rule formula at
   [`agents/critic/d7a_rules.py:24-36`](../../agents/critic/d7a_rules.py#L24-L36)
   (`len(overlap) / len(factors)`): overlap = 1; total = 6;
   theme_coherence = 1/6 ≈ 0.1667 (rounded to 4 decimals: 0.1667).
   The ratio at the entry-only register (1/5 = 0.2 for entry
   factors; 1/4 = 0.25 if `sma_20` excluded) differs from the
   D7a-defined whole-DSL register (1/6) — this is a §7
   mechanism-vs-observation cross-section worth surfacing.
   Cross-arc carry-forward: PHASE2C_8.1 closeout §6.2 hybrid-
   narration register. §7 mechanism comparison may invoke for
   evidence-base register.

Cumulative §7 carry-forward register now at 11 observations across
Steps 1-4 (3 from Step 1 + 3 from Step 2 + 2 from Step 3 + 3 from
Step 4). Substantial substantive interpretation surface for §7
mechanism-vs-evidence comparison; ingest-layer scoping question
(per session-entry handoff carry-forward) compounds at Step 5 §7
scoping cycle.




## 7. Mechanism-vs-observation comparison (Step 5 deliverable)

This section produces structured evidence maps for the three
pre-registered case definitions (Case A.1-A.4 / Case B.1-B.3 /
Case C.1-C.3 per [`PHASE2C_9_PLAN.md`](../phase2c/PHASE2C_9_PLAN.md)
§4) by cross-referencing §3 mechanism descriptions with §4 / §5 /
§6 observation evidence. Per spec §5.5 deliverable definition:
**output register** is per-case qualifying-evidence summary +
per-case disqualifying-counter-evidence summary. NOT case
determination (Step 6 §8 territory per spec §5.6 + §4.4
one-and-only-one rule); NOT new mechanism description (Step 1 §3
territory; §7 maps existing mechanism to evidence only); NOT
PHASE2C_10 / successor-arc pre-naming (per spec §7.2 forbidden-
language register).

The evidence base for §7 cross-reference comprises the cumulative
**11 observations** surfaced across Steps 1-4 §7-carry-forward
registers (3 from Step 1 §3 mechanism reconstruction; 3 from Step
2 §4.3 artifact-distribution audit; 2 from Step 3 §5.3 cross-tab;
3 from Step 4 §6.4 lone-survivor walkthrough), plus the §3-§6
cited mechanism descriptions and observation cardinalities at
file:line citation register. §7.0 / §7.1 / §7.2 below construct the
per-case evidence maps by mapping each observation to its
applicable Case sub-register(s) and summarizing
qualifying-vs-disqualifying-counter-evidence at the register
required by spec §4.

**Selection criterion pre-registration** (per session-entry
handoff): all 11 carry-forward observations enter §7 evidence
maps. The 11 are not uniform in evidentiary class — some are
population-level (cross-tab asymmetries, train-overlap divergence,
factor-set repetition rate); some are candidate-level (single-
trade-margin filter exclusion, permissive AND-gate at -10.2%
return, theme_coherence = 1/6); some are mechanism-level (modulus
mismatch between `_theme_for_slot` and `_theme_for_position`,
Critic-annotates-only / lifecycle-state assignment at orchestrator
ingest layer, THEME_HINTS Stage 2c-vs-Critic dual surface,
rejected_complexity at description-length boundary,
rsi_14_dominance first-50-block anomaly at 92%). Different
observation classes map to different sub-registers with different
evidentiary weights; the per-case maps below cite each observation
at the sub-register where it most plausibly bears, with
cross-references where the same observation bears on multiple
sub-registers.

**Ingest-layer mechanism scoping** (per session-entry handoff
carry-forward): Steps 1-4 mechanism reconstruction (§3) covers
Proposer prompt + Critic gate + theme rotation at code register;
ingest-layer mechanism (`agents/orchestrator/ingest.py`, which
performs the actual lifecycle-state assignment per §3.2.6
"Critic annotates only — lifecycle-state assignment is the
orchestrator ingest layer's responsibility") is NOT in Step 1
§3 reconstruction scope. §7 maps existing mechanism evidence; it
does NOT construct new mechanism descriptions for the ingest
layer. Where Observations 2 (Critic annotates only), 4
(rejected_complexity at boundary), 5 (rsi_14_dominance — touches
ingest-layer's anomaly flag), and 6 (factor-set repetition —
could plausibly be a Critic vs ingest-layer distinction) bear on
sub-registers requiring full ingest-layer mechanism for
interpretation, §7 surfaces the sub-register applicability with
explicit interpretive-register caveat. Full ingest-layer
mechanism reconstruction is out-of-scope per spec §3.1 in-scope
enumeration (Proposer + Critic + theme rotation only) + spec
§3.2.4 NO mining-process redesign; tracked-fix register entry at
§8 (Step 6 territory) surfaces the scoping limitation.

**Evidence-mapping discipline** (per spec §6.1): every claim in
§7 cites a specific source — file:line citation for code claims;
PHASE2C_8.1 closeout section anchor for canonical-number claims;
§3-§6 cross-reference for mechanism / observation claims; explicit
"this is interpretation, not observation" framing where evidence
mapping reaches the qualifying-vs-disqualifying-counter-evidence
adjudication boundary.

**Forbidden-language audit** (per spec §6.4 + §7.2): §7 contains
no PHASE2C_10 / successor-arc pre-naming; no "this confirms",
"this requires", or "this means we proceed to" forward-pointer
language; no Case A/B/C single-case adjudication (§7.X
qualifying-vs-disqualifying summaries are per-sub-register
evidence summaries, not case determinations). The §6.4 closeout-
document language audit at Step 6 verifies these constraints at
final-commit register.

**Cumulative-11 selection-criterion documentation** (per
session-entry handoff carry-forward + Step 4 advisor pass register-
precision concern): all 11 carry-forward observations enter §7
evidence maps. Spec §4.1 / §4.2 / §4.3 do NOT define exclusion
criteria for "out-of-scope-context observations"; the §7 inclusion
discipline is therefore "every Step 1-4 carry-forward observation
maps to at least one Case sub-register at the qualifying-evidence
or disqualifying-counter-evidence register." The 11 are not
uniform in evidentiary class (population-level / candidate-level /
mechanism-level); the per-Case sub-register maps below cite each
observation at the sub-register where it most plausibly bears,
with cross-references where the same observation bears on multiple
sub-registers. Selection criterion is "all-11-enter" by spec-silence
+ "all-observations-must-map" inclusion discipline. §8 (Step 6
territory) inherits this scoping decision documented here at §7.0
introduction.

#### 7.0.0 Carry-forward observation inventory

Compact reference for §7-internal cross-references. Per Claude
advisor's "cumulative-11 selection-criterion documentation"
concern + ChatGPT first-pass strong-minor "§7.0 inventory table"
patch suggestion. The Obs ID column uses §7-internal indexing 1-11
in Step-1 → Step-4 sequence; "Source step" + "Evidence anchor"
columns trace each to its underlying step working-draft register;
"Case sub-register(s) touched" column lists where the observation
maps as qualifying-evidence (Q) or disqualifying-counter-evidence
(D) at §7.0 / §7.1 / §7.2 below.

| Obs ID | Source step | Evidence anchor | Case sub-register(s) touched |
|---|---|---|---|
| 1 | Step 1 §3.3.2 | `_theme_for_slot` len(THEMES)=6 vs `_theme_for_position` THEME_CYCLE_LEN=5 modulus mismatch | A.3 (Q-weak) |
| 2 | Step 1 §3.2.6 | Critic annotates only / lifecycle-state assignment at orchestrator ingest layer | A.2 (D-strong); A.4 (D) |
| 3 | Step 1 §3.1.4 + §3.2.2 + §3.2.3 | THEME_HINTS dual surface (proposer-side vs Critic-side `batch_context.theme_hints`) | A.1 (Q-weak); A.2 (interpretive caveat) |
| 4 | Step 2 §4.3 | rejected_complexity at description-length boundary (2/200) | A.1 (Q-weak) |
| 5 | Step 2 §4.3 | rsi_14_dominance first-50-block anomaly at 92% (46/50) | A.1 (Q-weak) |
| 6 | Step 2 §4.3 | Factor-set repetition rate ~28.79% (57/198) | A.2 (Q-weak) |
| 7 | Step 3 §5.1 + §5.3 | Train-overlap regime divergence at per-theme level (eval_2020_v1 ≈ 2× eval_2021_v1) | A.3 (Q-weak); B.2 (Q) |
| 8 | Step 3 §5.1 + §5.3 | Per-regime pass-rate range asymmetry across themes (bear_2022 range 6 vs validation_2024 range 21 etc.) | A.3 (Q-weak); B.2 (Q) |
| 9 | Step 4 §6.4 | Single-trade-margin filter exclusion in bear_2022 (19 trades vs ≥20 threshold) | A.4 (Q); B.3 (D) |
| 10 | Step 4 §6.4 | Permissive AND-gate accepts -10.2% return in eval_2021_v1 for lone-survivor | A.4 (Q); A.2 (interpretive caveat) |
| 11 | Step 4 §6.4 | Theme alignment at D7a whole-DSL register / theme_coherence = 1/6 ≈ 0.1667 | A.4 (Q); A.1 (Q-weak); A.2 (D); B.2 (D); B.3 (D) |

Q = qualifying evidence; D = disqualifying counter-evidence;
parenthetical strength label per §7.0 / §7.1 / §7.2 prose detail.
Observations marked at multiple sub-registers are cited in each
case-sub-register prose with cross-references.

### 7.0 Case A evidence map

Case A definition (per spec §4.1): retrospective surfaces at
least one identifiable structural defect in mining-process inputs
that, if addressed, would plausibly improve candidate-population
quality at register relevant to deployment-quality strategy
generation. Sub-registers A.1 / A.2 / A.3 / A.4. The four
sub-registers map to: A.1 Proposer prompt defect; A.2 Critic gate
defect; A.3 theme rotation defect; A.4 mining-time vs
evaluation-time gate misalignment.

#### 7.0.1 Sub-register A.1 — Proposer prompt defect

Spec §4.1 A.1 qualifying-evidence categories: prompt language
steers toward overfitting-prone DSL patterns; theme-injection
asymmetry across themes; few-shot example selection bias;
DSL-schema-vs-evaluation-gate misalignment.

**Qualifying evidence (cited from §3-§6 register)**:

- **Observation 5 (Step 2 §4.3) — `rsi_14_dominance` first-50-block
  anomaly at 92%** (46/50 valid calls): per §3.1.3 prompt-builder
  mechanism at
  [`agents/proposer/prompt_builder.py`](../../agents/proposer/prompt_builder.py)
  the prompt does NOT explicitly encode `rsi_14` in any block; the
  92% first-50 dominance is therefore an **emergent Proposer-side
  pattern**, not a prompt-encoded directive. Cross-reference: §3.2.2
  D7a `factor_diversity` rule scoring at
  [`agents/critic/d7a_rules.py`](../../agents/critic/d7a_rules.py)
  computes per-batch factor-set diversity; the rsi_14 dominance
  surfaces at the batch-level factor-set distribution. **Evidentiary
  weight at A.1**: weak qualifying evidence — the dominance is
  emergent (not prompt-encoded) but the prompt-side factor surface
  per §3.1.3 may still systematically steer LLM toward `rsi_14` via
  factor-set documentation register. Whether the steering is
  prompt-language defect (A.1) or LLM-side property independent of
  prompt design (which would not be Case A territory) is interpretive
  ambiguity.
- **Observation 3 (Step 1 §3) — THEME_HINTS dual surface (Stage
  2c/2d proposer-side vs Critic-side `batch_context.theme_hints`)**:
  per §3.1.4 Stage 2c/2d batch orchestration at
  [`agents/proposer/stage2d_batch.py:117-129`](../../agents/proposer/stage2d_batch.py#L117-L129),
  the THEME_HINTS dictionary surfaces at the proposer-side at
  prompt-construction time (Stage 2c/2d batches consume THEME_HINTS
  to construct theme-injected prompts). Per §3.2.3 D7a feature
  extraction at
  [`agents/critic/d7a_feature_extraction.py:86-100`](../../agents/critic/d7a_feature_extraction.py#L86-L100)
  + §3.2.2 D7a `theme_coherence` rule consuming `BatchContext.theme_hints`,
  the same conceptual hint surface (theme → expected factor set)
  is consumed at the Critic-side at evaluation time. The two
  surfaces are architecturally separate but conceptually parallel:
  proposer-side uses THEME_HINTS to steer LLM generation toward
  theme-aligned factors; Critic-side uses `batch_context.theme_hints`
  to score theme alignment of generated DSL. **Evidentiary weight
  at A.1**: the dual-surface architecture is the structural
  substrate underlying Observation 11's register-asymmetric outcome
  (proposer surfaces 1 hint factor at thin-theme register; Critic
  evaluates across whole-DSL register). Whether the dual-surface
  architecture is prompt-side defect (A.1: prompt-side hint surface
  too thin for thin-themes), Critic-side defect (A.2: Critic-side
  scoring formula too whole-DSL for thin-theme alignment), or
  design-as-intended at CONTRACT BOUNDARY register requires
  ingest-layer mechanism reconstruction outside light-touch scope.
  **Interpretive ambiguity**: the dual-surface architecture is
  structural to design, not unambiguously defect at A.1 register.
- **Observation 11 (Step 4 §6.4) — theme alignment at D7a register
  for lone-survivor**: `theme_coherence = len(overlap) / len(factors)
  = 1/6 ≈ 0.1667` per §3.2.2 D7a rule at
  [`agents/critic/d7a_rules.py:24-36`](../../agents/critic/d7a_rules.py#L24-L36).
  THEME_HINTS at
  [`agents/proposer/stage2d_batch.py:117-129`](../../agents/proposer/stage2d_batch.py#L117-L129)
  defines `volume_divergence` as a THIN_THEME with single hint factor
  `{volume_zscore_24h}`. Per-§3.2.3 `extract_factors()` at
  [`agents/critic/d7a_feature_extraction.py:86-100`](../../agents/critic/d7a_feature_extraction.py#L86-L100)
  scans both entry AND exit groups + includes string-typed RHS
  `cond.value`. The thin-theme-register × whole-DSL-register
  interaction produces structurally low theme_coherence scores
  (1/6 = 0.1667) for thin-theme candidates regardless of candidate
  quality. Per Observation 3 above: the underlying dual-surface
  architecture (proposer-side THEME_HINTS at thin-theme register;
  Critic-side scoring at whole-DSL register) is the structural
  substrate of this asymmetric outcome. **Evidentiary weight at A.1**: prompt-side theme
  injection (THEME_HINTS) interacts with Critic-side
  theme_coherence formula in a register-asymmetric way (prompt
  surfaces 1 hint factor at thin-theme register; D7a evaluates
  across whole-DSL register including string-typed RHS). The
  asymmetry is structural to the THIN_THEMES design at
  `stage2d_batch.py`. **Interpretive caveat**: whether this
  asymmetry is prompt-side defect (A.1) or Critic-gate-side defect
  (A.2) depends on which side of the prompt-Critic interaction
  is treated as load-bearing; D7a `theme_coherence` is documented
  as observation-tag not gate signal at
  [`agents/critic/d7a_rules.py:155-156`](../../agents/critic/d7a_rules.py#L155-L156)
  per §3.2.2, which weakens A.1 qualifying weight.
- **Observation 4 (Step 2 §4.3) — rejected_complexity at description-
  length boundary** (2/200 attempts; both in `momentum` and
  `mean_reversion` themes per §4.0): per §3.1.1 Proposer interface
  at
  [`agents/proposer/interface.py`](../../agents/proposer/interface.py),
  the DSL pydantic schema enforces `description ≤ 300 chars`; the 2
  rejections occur at the schema-validation boundary, not at the
  Proposer prompt design layer. The cohort is too small (2/200) to
  demonstrate systematic prompt-language steering toward over-length
  descriptions. **Evidentiary weight at A.1**: weak — the cohort
  is small and the rejection is at schema validation, not at
  prompt-design register.

**Disqualifying counter-evidence**:

- §3.1.3 prompt builder at
  [`agents/proposer/prompt_builder.py`](../../agents/proposer/prompt_builder.py)
  documents leakage-audit guarantees (the prompt does NOT include
  validation-2024 / test-2025 / regime-holdout-2022 metrics or
  data); per CLAUDE.md hard rule, leakage audit is enforced at
  prompt-builder register. No prompt-side leakage defect surfaces
  at §3 mechanism reconstruction.
- §3.1.4 Stage 2d batch orchestration at
  [`agents/proposer/stage2d_batch.py`](../../agents/proposer/stage2d_batch.py)
  + Stage 2c shared-mechanism per §3.4 stage-attribution correction:
  theme injection follows uniform pattern across themes
  (THEME_HINTS dictionary indexed by theme key; rotation per
  `_theme_for_position` formula). No theme-asymmetric prompt-content
  pattern surfaces at §3 mechanism reconstruction.
- §3.1 Proposer prompt mechanism documents no few-shot example
  pattern at the Stage 2c/2d batches (the `approved_examples`
  window is critic-annotated only per §3.2.6 Critic acceptance
  semantics; not used as few-shot example selection at
  prompt-builder register per §3.1.3).
- DSL schema constraints at §3.1.1 (entry/exit groups ≤ 3,
  conditions per group ≤ 4, max_hold_bars ≤ 720) align with the
  CLAUDE.md "DSL complexity budget" hard constraint; no DSL-schema-
  vs-evaluation-gate misalignment surfaces at §3.

**Sub-register A.1 summary**: weak qualifying evidence (Observations
5 + 11 + 4) interacts with disqualifying counter-evidence at register
strength comparable to qualifying. The A.1 evidence base does NOT
unambiguously satisfy the spec §4.1 A.1 qualification criterion
("identifiable" + "concretely demonstrable" + "plausibly addressable").
Specific evidentiary asymmetry: Observations 5 + 11 surface emergent
patterns whose mechanism (prompt-side defect vs LLM-property-
independent-of-prompt vs prompt-Critic-interaction-defect) is
interpretively ambiguous at light-touch register.

#### 7.0.2 Sub-register A.2 — Critic gate defect

Spec §4.1 A.2 qualifying-evidence categories: D7a rule formula
threshold-edge artifacts; D7a → D7b routing systematic exclusion;
D7b verdict-vs-evaluation-outcome correlation defect; forbidden-
language scan over-trigger.

**Qualifying evidence**:

- **Observation 6 (Step 2 §4.3) — factor-set repetition rate of
  ~28.79%** (57 of 198 valid candidates with shared factor sets):
  per §3.2.2 D7a `structural_novelty` rule at
  [`agents/critic/d7a_rules.py:44-55`](../../agents/critic/d7a_rules.py#L44-L55)
  computes per-candidate novelty against a corpus baseline. The
  28.79% aggregate batch-level repetition rate provides per-batch
  context. **Evidentiary weight at A.2**: weak — the rate is a
  batch-level statistic; whether the rate exceeds noise-floor
  expectation under uniform factor-set sampling, and whether the
  D7a `structural_novelty` rule's per-candidate threshold produces
  edge artifacts at the rate threshold, requires structured
  re-examination at depth greater than light-touch register. Per
  spec §3.2.5 NO statistical-significance machinery, this
  evidentiary direction is bounded.
- **Observation 10 (Step 4 §6.4) — permissive AND-gate accepts
  -10.2% return in eval_2021_v1 for lone-survivor**: per §6.3
  evaluation-side trace, gate criteria are Sharpe ≥ -0.5
  (actual: -0.358) AND total_return ≥ -0.15 (actual: -0.102) AND
  max_dd ≤ 0.25 (actual: 0.231) AND trades ≥ 5 (actual: 29) per
  `passing_criteria` field at `holdout_summary.json` artifact. All
  4 criteria pass simultaneously — the gate **is permissive**
  in the sense that negative-Sharpe + negative-double-digit-return
  candidates can satisfy the gate. **Evidentiary weight at A.2**:
  this is evaluation-time-gate calibration, not Critic-gate (D7a /
  D7b) calibration; the permissive AND-gate at evaluation-time is
  at PHASE2C_6 / PHASE2C_7.1 / PHASE2C_8.1 register, not at Phase
  2B Critic gate register. **The qualifying-evidence path at A.2
  is therefore NOT primary** — Observation 10 maps more directly
  to A.4 (mining-time vs evaluation-time gate misalignment) than
  to A.2 (Critic gate defect at mining-time register). Per spec
  §3.2.6 NO calibration-variation grid, evaluation-time gate
  threshold variation is out-of-scope.
- **Observation 11 (Step 4 §6.4) — theme_coherence = 1/6 ≈ 0.1667
  for lone-survivor**: as analyzed at A.1 above — the THIN_THEMES
  × whole-DSL-register interaction produces structurally low
  theme_coherence scores. **Evidentiary weight at A.2**: D7a
  `theme_coherence` is documented as observation-tag NOT gate
  signal per §3.2.2 + CLAUDE.md hard rule "Critic annotates only";
  the score is reported but does not influence approval. This
  weakens A.2 qualifying weight at the Critic-gate-as-defect
  register, since D7a is annotation-only.

**Disqualifying counter-evidence**:

- §3.2 Critic gate logic + §3.2.6 Critic acceptance semantics + §3.2.5
  CLAUDE.md hard constraint "NEVER let the critic influence
  approved_examples window — critic annotates only, never filters":
  the Critic at PHASE2C generation cycle **does not gate** at
  approval-or-rejection register. All 198 valid candidates passed
  through to lifecycle state `pending_backtest`; lifecycle-state
  assignment is the **orchestrator ingest-layer**'s responsibility,
  not Critic's, per §3.2.6. Whether the ingest layer's gate
  semantics constitute a defect is an **ingest-layer mechanism
  question** outside Step 1 §3 reconstruction scope (per
  session-entry handoff scoping); ingest-layer mechanism is
  NOT in §3 reconstruction.
- §4.0 lifecycle-state distribution: 198 `pending_backtest` + 2
  `rejected_complexity` + 0 across all other terminal states
  (`critic_rejected`, `proposer_invalid_dsl`, `duplicate`,
  `train_failed`, `holdout_failed`, `dsr_failed`, `shortlisted`,
  `budget_exhausted`, `backend_empty_output`). The 0 count for
  `critic_rejected` lifecycle state confirms per §3.2.6 that the
  Critic does not gate; there is no D7a → D7b → reject pathway
  active at PHASE2C_5 generation cycle.
- §3.2.4 D7b reliability fuse: `CRITIC_RELIABILITY_FUSE_ENFORCED =
  False` per CLAUDE.md hard rule (locked at Stage 2 contract
  boundary); D7b backend errors are captured in `critic_status`
  field for forensic register, not used to reject candidates. No
  D7b-side gate defect can have produced candidate exclusion at
  PHASE2C_5 generation cycle.

**Sub-register A.2 summary**: qualifying evidence is **weak** —
Observations 6 / 8 / 11 surface batch-level / candidate-level
patterns that touch on Critic register but are **not gate-mechanism
defects at PHASE2C_5 generation cycle**, since the Critic does not
gate (annotation-only per CLAUDE.md hard rule + §3.2.6). The
mining-time gate that **does** assign lifecycle states is the
orchestrator ingest layer (out of Step 1 §3 reconstruction scope).
Disqualifying counter-evidence at A.2 register is strong: 0
`critic_rejected` candidates at §4.0 confirms Critic non-gating;
the gate-as-defect interpretation requires ingest-layer mechanism
reconstruction outside light-touch register.

**Interpretive caveat**: A.2 sub-register's "Critic gate defect"
language assumes a Critic-as-gate model. The empirical mining-
process at PHASE2C_5 has Critic-as-annotator (per §3.2.6 + CLAUDE.md
hard rule); the actual gate is the ingest layer, which is
out-of-§3-scope. A.2 qualifying-evidence weighting at light-touch
register is therefore interpretively bounded.

#### 7.0.3 Sub-register A.3 — Theme rotation defect

Spec §4.1 A.3 qualifying-evidence categories: operational-rotation
exclusion (5-of-6 themes) bias; theme-assignment formula
order-of-cycle dependencies; theme-rotation × budget-exhaustion
adversarial interaction.

**Qualifying evidence**:

- **Observation 1 (Step 1 §3) — modulus mismatch between
  `_theme_for_slot` and `_theme_for_position`**: per §3.3.2
  operational rotation mechanism — `_theme_for_position` at Stage
  2c/2d batches uses `THEMES[(k - 1) % THEME_CYCLE_LEN]` with
  `THEME_CYCLE_LEN = 5` (operational rotation excludes
  `multi_factor_combination`); `_theme_for_slot` at agents/themes.py
  uses `THEMES[(k - 1) % len(THEMES)]` with `len(THEMES) = 6`
  (canonical rotation includes `multi_factor_combination`). The two
  modulus formulas can produce divergent theme assignments for the
  same slot index k. **Evidentiary weight at A.3**: per §3.3.2
  CONTRACT BOUNDARY documentation, the operational rotation
  exclusion is **deliberate**, not accidental — the
  `multi_factor_combination` theme is documented at
  [`agents/themes.py`](../../agents/themes.py) as canonical-but-not-
  operational pending separate validation. The dual-formula
  surface is therefore design-as-intended, not defect; whether the
  6-vs-5 modulus interaction at edge cases (e.g., concurrent
  invocation of both formulas) produces wrong-theme assignment is
  a separate question requiring code-level inspection beyond §3
  light-touch reconstruction. **Interpretive ambiguity**: if both
  formulas are consumed by different code paths, the dual-surface
  is design-as-intended; if only one path is canonical and the other
  is dead code, the dual surface is a maintenance hazard. §3 §3.3.2
  reconstruction does not resolve which.
- **Observation 7 (Step 3 §5.3) — train-overlap regime divergence
  at per-theme level**: eval_2020_v1 column total (74) ≈ 2× eval_2021_v1
  column total (38); per-theme distribution diverges substantially
  across train-overlap regimes (e.g., calendar_effect 26/10 — train
  2020 vs 2021; volume_divergence 23/12; mean_reversion 3/8 — note
  the 2021 > 2020 reversal direction relative to other themes). The
  theme-distributional divergence across train-overlap regimes is
  cross-tab fact at §5.1 Observation 8. **Evidentiary weight at
  A.3**: this is a per-regime evaluation-outcome divergence, NOT a
  generation-side theme rotation pattern. The 40/40/40/39/39
  generation-side theme distribution per §4.0 is approximately
  uniform; the per-regime evaluation pass-count divergence is
  consistent with per-theme × per-regime statistical pattern
  variance, not with theme-rotation-mechanism defect at generation
  side. **Mapping at A.3 is therefore weak** — the divergence bears
  more directly on Case B.2 (population properties consistent with
  noise floor) than on A.3.
- **Observation 8 (Step 3 §5.3) — per-regime pass-rate range
  asymmetry across themes**: bear_2022 spans 0-6 (range 6);
  validation_2024 spans 4-25 (range 21); eval_2020_v1 spans 3-26
  (range 23); eval_2021_v1 spans 2-12 (range 10). **Evidentiary
  weight at A.3**: as Observation 7 — this is per-regime
  evaluation-outcome variance, not generation-side theme-rotation
  defect. Maps more directly to Case B.2 than to A.3.

**Disqualifying counter-evidence**:

- §4.0 generation-side theme distribution: 40/40/40/39/39 across
  the 5 operational themes per `stage2d_summary.json:lifecycle_counts`
  (§3.3.3 + §4.0 cross-reference). The 40-per-theme uniform
  distribution is consistent with `THEMES[(k - 1) % 5]` cyclic
  rotation outcome at 200 attempts (200 / 5 = 40 attempts per theme;
  40 × 5 = 200; 198 valid candidates after 2 schema rejections at
  description-length boundary distribute as 40/40/40/39/39). No
  theme-distributional asymmetry surfaces at generation-side
  register.
- §3.3 theme rotation mechanism documents no order-of-cycle
  dependency: rotation is strictly `THEMES[(k - 1) % 5]` indexed
  by attempt position k; no early-cycle vs late-cycle attempt
  budget asymmetry surfaces at §3.3 mechanism reconstruction.
- §4.0 budget-exhaustion register: `unissued_slots = 0` and
  `total_actual_cost_usd = $2.30` < `batch_cap_usd = $20.0` per
  `stage2d_summary.json` config + spend register. No budget
  exhaustion occurred at PHASE2C_5 generation cycle; no
  theme-rotation × budget-exhaustion adversarial interaction can
  have produced theme-asymmetric exclusions.
- §3.3.2 CONTRACT BOUNDARY at
  [`agents/themes.py`](../../agents/themes.py):17–21 + CLAUDE.md
  "Theme rotation operational boundary": the 5-theme operational
  rotation excluding `multi_factor_combination` is documented at
  CONTRACT BOUNDARY register; the exclusion is operational practice,
  not canonical specification. Per spec §3.2.4 NO mining-process
  redesign, the operational-vs-canonical theme list register is
  not retrospective scope; it is fixed empirical fact at light-touch
  register.

**Sub-register A.3 summary**: qualifying evidence is **weak** —
Observation 1 (modulus mismatch) is design-as-intended at CONTRACT
BOUNDARY register; Observations 7 + 8 (theme-level pass-count
divergence across regimes) are per-regime evaluation-outcome
patterns mapping more directly to Case B.2 than to A.3.
Disqualifying counter-evidence at A.3 register is strong:
generation-side theme distribution is approximately uniform per
mechanism specification; no order-of-cycle dependency or
budget-exhaustion adversarial interaction surfaces at §3 + §4.

#### 7.0.4 Sub-register A.4 — Mining-time vs evaluation-time gate misalignment

Spec §4.1 A.4 qualifying-evidence categories: mining-time gate
(Critic + lifecycle-state filter) systematically passes candidates
that mining-time evaluation (train + holdout) approves but those
candidates fail evaluation-time gate (PHASE2C_6 4-criterion AND-gate);
lone-survivor's hybrid quality profile reflects mining-time /
evaluation-time gate misalignment.

**Qualifying evidence**:

- **Observation 9 (Step 4 §6.4) — single-trade-margin filter
  exclusion in bear_2022**: per §6.3 evaluation-side trace,
  `audit_v1_filtered/0845d1d7898412f2/` directory does NOT exist
  on disk (mechanically verified by `ls`); the lone-survivor is
  excluded from the bear_2022 filtered cohort at the trade-count
  filter (19 trades vs ≥20 threshold = 1-trade margin). The trade-
  count filter is at evaluation-time register (PHASE2C_7.1 §5
  threshold), separate from mining-time AND-gate. **Evidentiary
  weight at A.4**: this **is** a mining-time vs evaluation-time
  gate misalignment instance — the candidate passed mining-time
  walk-forward + holdout (lifecycle-state `holdout_passed` per
  §6.2 trace) AND passed the 4-criterion AND-gate at evaluation
  time in bear_2022 (Sharpe 0.508, return +6.80%, max_dd 0.095, 19
  trades — all 4 AND-gate criteria pass per §6.3 table) but was
  EXCLUDED from the filtered cohort by trade-count threshold. The
  AND-gate (mining-time canonical) and the trade-count filter
  (PHASE2C_7.1 evaluation-time) are at different gate registers;
  the candidate's exclusion-by-1-trade-margin demonstrates the
  inter-gate boundary. **Interpretive bound**: whether this
  demonstrates **defect** at mining-process design (mining gate
  doesn't anticipate evaluation-time filter) or **deliberate
  separation** (evaluation-time filter is intentionally stricter
  than mining-time gate) is not resolvable at light-touch register.
- **Observation 10 (Step 4 §6.4) — permissive AND-gate accepts
  -10.2% return in eval_2021_v1 for lone-survivor**: per §6.3
  evaluation-side trace, all 4 AND-gate criteria pass simultaneously
  (Sharpe -0.358 ≥ -0.5; return -0.102 ≥ -0.15; max_dd 0.231 ≤ 0.25;
  trades 29 ≥ 5). **Evidentiary weight at A.4**: this **is** a
  mining-time vs evaluation-time gate calibration question at
  AND-gate register — the AND-gate accepts negative-Sharpe +
  negative-double-digit-return candidates, which may be
  inconsistent with deployment-quality strategy generation register.
  Whether this is mining-time gate (Critic + lifecycle) calibration
  defect, evaluation-time gate calibration defect, or absence-of-
  defect at noise-floor variance is interpretively bounded at
  light-touch register. Per spec §3.2.6 NO calibration-variation
  grid, evaluation-time gate threshold variation is out-of-scope.
- **Composite hybrid quality observation (composite of Obs 9 + Obs
  10 + audit-only partition origin per §6.3 + Obs 11)**: composite
  comprises audit-only partition origin (`wf_test_period_sharpe =
  -0.072 < 0.5` primary threshold per §6.3; this is a §6.3 fact,
  not a §7-internal observation) + filter exclusion in bear_2022 by
  1-trade margin (Observation 9) + permissive AND-gate accepting
  -10.2% return in eval_2021_v1 (Observation 10) + theme alignment
  at thin-theme register (theme_coherence = 1/6 ≈ 0.1667 per §6.4;
  Observation 11 narrowly). The composite matches spec §4.1 A.4
  qualifying-evidence text: "lone-survivor's hybrid quality profile
  (audit-only origin + filter exclusion by single-trade margin +
  permissive AND-gate accepting -10.2% return) reflects mining-time
  / evaluation-time gate misalignment more than candidate-population
  coherence." **Evidentiary weight at A.4**: the composite hybrid
  quality observation matches the spec §4.1 A.4 qualifying-evidence
  text directly at descriptive register.

**Disqualifying counter-evidence**:

- The 4-criterion AND-gate at PHASE2C_6 / PHASE2C_7.1 / PHASE2C_8.1
  evaluation register is the **canonical** gate per
  `config/environments.yaml:splits.regime_holdout.passing_criteria`
  (CLAUDE.md hard constraint: "NEVER mark
  `regime_holdout_passed = True` unless ALL four criteria are met"
  with thresholds Sharpe ≥ -0.5, return ≥ -0.15, max_dd ≤ 0.25,
  trades ≥ 5). The thresholds are **deliberately permissive** at
  generation-cycle register to admit candidates for downstream
  evaluation; whether downstream evaluation-time tightening
  (e.g., trade-count filter ≥ 20 at PHASE2C_7.1) reflects
  mining-time-vs-evaluation-time gate misalignment **defect** or
  **intentional staged tightening** is interpretively ambiguous.
- One-of-198 lone-survivor cardinality is consistent with both
  Case A.4 interpretation (hybrid quality reflects gate
  misalignment) AND Case B.3 interpretation (hybrid quality is
  one-of-N tail event under noise-floor distribution); the
  evidence is consistent with either interpretation at light-touch
  register, which is itself a Case C.1 / C.3 ambiguity sub-register
  pattern.
- Per §3.2.6 + §3.4 ingest-layer-mechanism out-of-scope:
  mining-time gate semantics (the orchestrator ingest layer's
  lifecycle-state assignment) are NOT in §3 reconstruction scope;
  whether the ingest-layer gate has an internal calibration that
  could be aligned with evaluation-time gate is unresolvable at
  light-touch register.

**Sub-register A.4 summary**: qualifying evidence at A.4 is
**direct** at descriptive register — Observations 9 + 10 + the
composite hybrid quality observation (composite of Obs 9 + Obs 10
+ audit-only origin per §6.3 + Obs 11) match spec §4.1 A.4
qualifying-evidence text (hybrid quality profile of lone-survivor;
single-trade-margin exclusion; permissive AND-gate at -10.2%
return). Disqualifying counter-evidence at A.4 is **also direct**
at descriptive register: the 4-criterion AND-gate is canonical at
deliberately-permissive register at generation-cycle; ingest-layer
mechanism is out-of-light-touch-scope; one-of-198 cardinality is
consistent with both Case A.4 and Case B.3 interpretations.
**Qualifying-vs-disqualifying balance at A.4 sub-register**:
whether the gate-misalignment register matches "defect" or
"deliberate staged tightening" is not resolvable at light-touch
register; the balance sits at the spec §4.3 C.1 evidence-pattern
boundary register descriptively, with §8 (Step 6 territory)
applying §4.4 one-and-only-one rule for case determination.

#### 7.0.5 Case A evidence-base summary

Per spec §4.1 Case A determination criterion: "at least ONE of
A.1 / A.2 / A.3 / A.4 satisfied with concrete evidence ... that
meets the qualifying criteria; AND no disqualifying counter-evidence
surfaces stronger than the qualifying evidence; AND the identified
defect is plausibly addressable."

Cross-sub-register summary (this is evidence-map summary, NOT case
determination):

| sub-register | qualifying evidence weight | disqualifying counter-evidence weight | net qualification at light-touch register |
|---|---|---|---|
| A.1 | weak | comparable to weak qualifying | NOT cleanly satisfied |
| A.2 | weak (Observations 6 / 10 / 11 map weakly) | strong (Critic annotates only; 0 critic_rejected; ingest-layer-as-actual-gate out-of-scope) | NOT cleanly satisfied |
| A.3 | weak (modulus mismatch is design-as-intended; per-regime divergence maps more to B.2) | strong (uniform generation-side distribution; no budget exhaustion; CONTRACT BOUNDARY documents exclusion) | NOT cleanly satisfied |
| A.4 | direct (Observations 9 + 10 + 11 align with spec §4.1 A.4 text) | direct (canonical AND-gate is deliberately permissive; ingest-layer out-of-scope; one-of-198 consistent with B.3) | INTERPRETIVELY AMBIGUOUS at light-touch |

Net Case A evidence-base register at light-touch retrospective:
A.4 sub-register has direct qualifying evidence and direct
disqualifying counter-evidence; the qualifying-vs-disqualifying
balance at A.4 sits at the spec §4.3 C.1 boundary register
("partial qualifying evidence for Case A ... without clean Case A.x
qualification"). A.1, A.2, A.3 sub-registers have qualifying
evidence weaker than their disqualifying counter-evidence.
Case determination at §8 (Step 6 territory) applies the §4.4
one-and-only-one rule to this evidence base; §7 does not pre-empt
that determination.

### 7.1 Case B evidence map

Case B definition (per spec §4.2): retrospective surfaces no
identifiable structural defect in mining-process inputs; observed
candidate-population properties are consistent with the candidate
population being structurally weak independent of mining-process
inputs. Sub-registers B.1 / B.2 / B.3.

#### 7.1.1 Sub-register B.1 — Mining-process inputs review surfaces no Case A defect

Spec §4.2 B.1: all four Case A categories' qualifying evidence
absent OR present-but-weaker-than-disqualifying-counter-evidence.

**B.1 evidence-base summary** (cross-reference §7.0.5):

- A.1 qualifying evidence weak; disqualifying counter-evidence
  comparable → NOT cleanly satisfied as Case A.1 defect.
- A.2 qualifying evidence weak; disqualifying counter-evidence
  strong → A.2 NOT cleanly satisfied as Case A.2 defect.
- A.3 qualifying evidence weak; disqualifying counter-evidence
  strong → A.3 NOT cleanly satisfied as Case A.3 defect.
- A.4 qualifying evidence direct (Observations 9 + 10 + 11);
  disqualifying counter-evidence also direct → A.4 NOT cleanly
  satisfied as Case A.4 defect, but qualifying evidence is **not
  weaker than** disqualifying counter-evidence (qualifying-vs-
  disqualifying balance is interpretively ambiguous at light-touch
  register).

**Sub-register B.1 partial-satisfaction register**: A.1 / A.2 / A.3
satisfy B.1 ("present-but-weaker-than-disqualifying-counter-
evidence"); A.4 does NOT cleanly satisfy B.1 (qualifying evidence
is **not weaker than** disqualifying at light-touch register;
balance is ambiguous). B.1 is therefore **partially satisfied** —
3 of 4 sub-registers satisfy; A.4 register sits at the
qualifying-vs-disqualifying boundary.

#### 7.1.2 Sub-register B.2 — Population properties consistent with noise floor

Spec §4.2 B.2 qualifying-evidence categories: cohort_a_filtered=0
outcome plausibly one-of-198 sample-size artifact; theme-level
pass-count distribution shows no systematic theme-property
correlation; pass-count distribution histogram consistent with
near-uniform random-pass distribution.

**Qualifying evidence**:

- **PHASE2C_8.1 closeout §3.1 — `cohort_a_filtered` = 0 outcome**
  (per spec §2.4 canonical anchor): zero candidates pass the
  4-regime filtered-cohort intersection at PHASE2C_8.1 evaluation.
  **Evidentiary weight at B.2**: this is the spec §4.2 B.2 first
  qualifying-evidence example directly; the 0-of-198 outcome
  matches a plausible noise-floor expectation under multi-regime
  AND-intersection at the marginal-pass-rate register documented
  by §5 cross-tab (per-regime pass rates 6.6% / 43.9% / 37.4% /
  19.2% for bear_2022 / validation_2024 / eval_2020_v1 /
  eval_2021_v1). Per spec §3.2.5 NO statistical-significance
  machinery, the noise-floor consistency is at descriptive register
  only; rigorous quantification (e.g., expected intersection
  cardinality under independence assumption) is out-of-scope.
- **Observation 7 (Step 3 §5.3) + Observation 8 (Step 3 §5.3) —
  cross-tab patterns are theme-distributional but not systematically
  theme-property-correlated**: per §5.1 cross-tab Observations 1-9,
  per-theme pass-count asymmetries exist at cardinality register but
  no single theme uniformly outperforms or underperforms across all
  4 regimes. `volatility_regime` is lowest in 3 of 4 regimes (range
  ranking) but `volume_divergence` is highest in 1 regime
  (validation_2024 at 25/40); `calendar_effect` is highest in 1
  regime (eval_2020_v1 at 26/40); `mean_reversion` is highest in 1
  regime (validation_2024 at 13/39 absolute, but 8/39 in
  eval_2021_v1 reverses). The lack of monotonic theme-quality
  ranking across regimes is consistent with random-pass distribution
  more than with systematic theme-property correlation.
  **Evidentiary weight at B.2**: moderate; the patterns are
  consistent with noise-floor-variance interpretation at descriptive
  register, but rigorous noise-floor null-distribution comparison
  is out-of-scope per §3.2.5.
- **PHASE2C_8.1 closeout §4.1 — pass-count distribution histogram**
  (per spec §4.2 B.2 third qualifying-evidence example): per
  PHASE2C_8.1 §4.1 the per-candidate pass-count distribution across
  4 regimes is consistent with a near-uniform random-pass
  distribution rather than a structural bimodal pattern (no clear
  separation between "deployment-quality" candidates passing all
  4 regimes and "noise-floor" candidates passing 0-1 regimes; the
  21-vs-8 train-overlap-vs-fully-OOS asymmetry per PHASE2C_8.1 §5.2
  is descriptive, not structural).
  **Evidentiary weight at B.2**: moderate; consistent with
  noise-floor distribution at descriptive register.

**Disqualifying counter-evidence**:

- Observations 9 + 10 + 11 (Step 4 §6.4 lone-survivor walkthrough):
  the lone-survivor's hybrid quality profile (audit-only origin +
  single-trade-margin filter exclusion + permissive AND-gate at
  -10.2% return + theme_coherence at 1/6 thin-theme register) is
  **specific** to mining-process input design (THIN_THEMES at
  THEME_HINTS register; trade-count filter threshold at
  PHASE2C_7.1 register). Whether this specificity is interpretable
  as Case A.4 mining-time-vs-evaluation-time gate misalignment
  (§7.0.4 above) or as Case B.3 tail-event consistent with
  noise-floor distribution at hybrid-quality register is
  interpretively ambiguous; cited as disqualifying counter-evidence
  at B.2 register since the lone-survivor characterization shows
  mining-process-specific pattern not consistent with pure
  noise-floor interpretation.
- Per spec §3.2.5 NO statistical-significance machinery: rigorous
  noise-floor null-distribution comparison (DSR / PBO / CPCV) is
  Q-9.A territory, out-of-scope. The "consistent with noise floor"
  claim at B.2 register is therefore at descriptive-register only,
  not at significance-test register; this **is** a light-touch
  retrospective limit on B.2 qualifying weight.

**Sub-register B.2 summary**: qualifying evidence is **moderate**
at descriptive register — `cohort_a_filtered = 0` directly satisfies
spec §4.2 B.2 first qualifying-evidence text; cross-tab patterns +
pass-count distribution are consistent with near-uniform random-pass
distribution at descriptive register. Disqualifying counter-evidence
is moderate: lone-survivor hybrid quality profile shows
mining-process-specific pattern not consistent with pure noise-floor
interpretation; rigorous noise-floor null-distribution comparison is
out-of-scope. **Interpretive caveat**: B.2 qualifying weight is
bounded at descriptive register at light-touch retrospective; full
B.2 qualification at significance-test register requires Q-9.A
machinery.

#### 7.1.3 Sub-register B.3 — Lone-survivor characterization is tail-event consistent

Spec §4.2 B.3 qualifying-evidence categories: lone-survivor's hybrid
quality is plausibly one-of-N tail event under noise-floor
distribution; volume-divergence theme behavior consistent with
random theme-allocation rather than systematic theme-quality
asymmetry.

**Qualifying evidence**:

- **One-of-198 cardinality of lone-survivor** (per spec §2.4
  canonical anchor `cohort_a_unfiltered` cardinality = 1): the
  one-of-N cardinality is consistent with tail-event interpretation
  under noise-floor distribution at marginal-pass-rate register.
  Per the per-regime marginal pass rates (6.6% / 43.9% / 37.4% /
  19.2%), the multiplicative independence-assumption expected
  cardinality of all-4-regime AND-pass under marginal rates is
  approximately `0.066 × 0.439 × 0.374 × 0.192 × 198 ≈ 0.4`
  candidates (descriptive register only; rigorous independence-
  assumption testing is out-of-scope per §3.2.5). The empirical 1
  vs descriptive-register expected ~0.4 is consistent with
  one-of-N tail event at descriptive register.
  **Evidentiary weight at B.3**: moderate; consistent with
  tail-event interpretation at descriptive register but rigorous
  null-distribution comparison out-of-scope.
- **Observation 4 (Step 3 §5.1) — `volume_divergence` theme
  cross-regime distribution**: pass counts of 4 / 25 / 23 / 12 in
  bear_2022 / validation_2024 / eval_2020_v1 / eval_2021_v1
  respectively. The distribution is asymmetric but not monotonic
  in any regime ranking; volume_divergence is highest-pass in
  validation_2024 (25/40 = 62.5%) but third-highest in eval_2020_v1
  (23/40) and second-lowest in bear_2022 (4/40). The asymmetry
  pattern is consistent with random theme-allocation × per-regime
  variance, not with systematic volume_divergence-as-tail-quality
  asymmetry.
  **Evidentiary weight at B.3**: moderate; consistent with random
  theme-allocation interpretation at descriptive register.

**Disqualifying counter-evidence**:

- Lone-survivor hybrid quality profile **specificity** (per §7.0.4
  A.4 above): audit-only origin + single-trade-margin filter
  exclusion in bear_2022 + permissive AND-gate at -10.2% return in
  eval_2021_v1 + theme_coherence = 1/6 at thin-theme register. The
  specificity is **not random** — each component traces to a
  specific mining-process input (audit partition origin from
  PHASE2C_6 wf_test_period_sharpe threshold; trade-count filter
  threshold at PHASE2C_7.1; AND-gate criteria at canonical evaluation
  register; THIN_THEMES at THEME_HINTS). Whether the specificity is
  consistent with tail-event interpretation (B.3 qualifying) or
  with mining-time-vs-evaluation-time gate misalignment (A.4
  qualifying) is interpretively ambiguous.
- Per §3.2.5 NO statistical-significance machinery: the
  "tail-event consistent" claim at B.3 register is at descriptive-
  register only, not at significance-test register.
- Sample-size limitation: N=1 lone-survivor sample is too small to
  rigorously discriminate tail-event vs systematic-pattern at
  light-touch register.

**Sub-register B.3 summary**: qualifying evidence is **moderate**
at descriptive register — one-of-198 cardinality consistent with
tail-event interpretation; volume_divergence theme distribution
consistent with random allocation. Disqualifying counter-evidence
is moderate: lone-survivor hybrid quality specificity traces to
specific mining-process inputs, which is not random pattern;
rigorous tail-event-vs-systematic discrimination out-of-scope.

#### 7.1.4 Case B evidence-base summary

Per spec §4.2 Case B determination criterion: ALL of B.1, B.2, B.3
satisfied with concrete evidence; AND no disqualifying counter-
evidence surfaces.

Cross-sub-register summary (this is evidence-map summary, NOT case
determination):

| sub-register | qualifying evidence weight | disqualifying counter-evidence weight | net qualification at light-touch register |
|---|---|---|---|
| B.1 | partial (3 of 4 Case A sub-registers satisfy weaker-than-disqualifying; A.4 sits at boundary) | strong at A.4 register | PARTIALLY satisfied (3 of 4 sub-registers) |
| B.2 | moderate at descriptive register | moderate (lone-survivor specificity; rigorous null-test out-of-scope) | NOT cleanly satisfied at significance-test register; partially at descriptive |
| B.3 | moderate at descriptive register | moderate (lone-survivor specificity; rigorous tail-event-vs-systematic out-of-scope) | NOT cleanly satisfied at significance-test register; partially at descriptive |

Net Case B evidence-base register at light-touch retrospective:
no sub-register cleanly satisfies the spec §4.2 "ALL of B.1, B.2,
B.3 satisfied with concrete evidence; AND no disqualifying counter-
evidence surfaces" criterion. B.1 partial qualification (A.4
qualifying-vs-disqualifying balance ambiguous); B.2 + B.3 partial
qualification at descriptive register (full qualification requires
Q-9.A statistical-significance machinery out-of-scope).

### 7.2 Case C evidence map

Case C definition (per spec §4.3): retrospective surfaces evidence
consistent with neither Case A nor Case B fully. Sub-registers
C.1 / C.2 / C.3.

#### 7.2.1 Sub-register C.1 — Partial qualifying evidence for Case A

Spec §4.3 C.1: one or more Case A categories show "weak qualifying
evidence" (suggestive but not concretely demonstrable defect) without
clean Case A.x qualification.

**Qualifying evidence at C.1 register**:

- §7.0 Case A evidence-base summary documents weak qualifying
  evidence at A.1 (Observations 5 + 11 + 4); weak at A.2
  (Observations 6 / 8 / 11 — but mapping to Critic-as-gate model
  problematic since Critic is annotation-only per §3.2.6); weak
  at A.3 (Observation 1 design-as-intended; Observations 7 + 8
  map more to B.2); direct-but-balanced at A.4 (Observations 9 +
  10 + 11 align with spec §4.1 A.4 qualifying-evidence text;
  disqualifying counter-evidence also direct).
- §7.0.5 net Case A evidence-base register at light-touch:
  qualifying-vs-disqualifying balance at A.4 is interpretively
  ambiguous at light-touch register. The A.4 sub-register evidence
  pattern matches spec §4.3 C.1 "partial qualifying evidence for
  Case A" register text descriptively — at A.4 sub-register the
  qualifying-vs-disqualifying balance sits at the spec §4.3 C.1
  boundary (qualification ambiguous, not absent).

**Boundary disqualifying counter-evidence at C.1 register**:

- A.4 qualifying-vs-disqualifying balance is unresolved at
  light-touch register; structured re-examination depth would be
  required to discriminate between clean A.x qualification and
  partial-qualification interpretations. Whether such depth would
  resolve toward A.4 qualifying or disqualifying is out-of-light-
  touch-scope.
- The C.1 register is therefore conditional on light-touch-register
  limitation; whether A.4 satisfies clean Case A.x qualification at
  deeper register is the §8 (Step 6 territory) question.

**Sub-register C.1 evidence-base summary**: qualifying evidence is
**direct** at descriptive register — §7.0 A.4 sub-register
evidence-base shows the spec §4.3 C.1 evidence-pattern register
("partial qualifying evidence for Case A ... without clean Case
A.x qualification") at the qualifying-vs-disqualifying boundary.
Boundary disqualifying counter-evidence is conditional on
structured re-examination depth resolution, which is
out-of-light-touch-scope. §8 (Step 6 territory) applies the §4.4
one-and-only-one rule to this evidence base.

#### 7.2.2 Sub-register C.2 — Mixed qualifying / counter-qualifying evidence for Case B

Spec §4.3 C.2: evidence consistent with Case B at population-
property register but inconsistent at lone-survivor or theme-level
register (or vice versa).

**Qualifying evidence at C.2 register**:

- §7.1 Case B evidence-base summary documents:
  - B.1 partial (3 of 4 Case A sub-registers satisfy
    weaker-than-disqualifying; A.4 sits at boundary)
  - B.2 partial at descriptive register (cohort_a_filtered = 0
    consistent with noise floor at descriptive; rigorous null-test
    out-of-scope; lone-survivor specificity disqualifying-counter
    at B.2)
  - B.3 partial at descriptive register (one-of-198 + theme
    distribution consistent with random allocation; lone-survivor
    specificity disqualifying-counter at B.3)
- The pattern is exactly the spec §4.3 C.2 "mixed qualifying /
  counter-qualifying evidence for Case B" register: B.2 qualifying
  at population-property cardinality register (cohort_a_filtered =
  0; per-regime pass rates 6.6%-43.9%) but disqualifying-counter at
  lone-survivor specificity register (Observations 9 + 10 + 11
  trace to specific mining-process inputs).

**Boundary disqualifying counter-evidence at C.2 register**:

- The lone-survivor specificity register's interpretive direction
  (tail-event-consistent at B.3 register vs mining-time-vs-
  evaluation-time gate misalignment at A.4 register) is unresolved
  at light-touch register; structured re-examination depth would be
  required to discriminate.
- The C.2 register is therefore conditional on light-touch-register
  limitation at the lone-survivor specificity register
  qualifying-vs-disqualifying boundary; §8 (Step 6 territory)
  question.

**Sub-register C.2 evidence-base summary**: qualifying evidence is
**direct** at descriptive register — §7.1 Case B evidence-base
shows the spec §4.3 C.2 evidence-pattern register ("mixed
qualifying / counter-qualifying evidence for Case B"). Boundary
disqualifying counter-evidence is conditional on structured
re-examination depth resolution, out-of-light-touch-scope. §8
(Step 6 territory) applies the §4.4 one-and-only-one rule to this
evidence base.

#### 7.2.3 Sub-register C.3 — Light-touch register insufficient for discrimination

Spec §4.3 C.3: light-touch retrospective produces evidence that
suggests Case A or Case B but at strength below the qualification
threshold; the honest read is "structured re-examination would be
needed to discriminate."

**Qualifying evidence at C.3 register**:

- §7.0 + §7.1 evidence-base summaries document multiple
  light-touch-register limitations:
  - A.1 prompt-side defect vs LLM-property-independent-of-prompt
    interpretation (Observations 5 + 11) requires structured
    re-examination at depth greater than light-touch
  - A.2 Critic-gate-as-defect interpretation requires ingest-layer
    mechanism reconstruction outside Step 1 §3 scope (per
    §7.0.2 A.2 interpretive caveat)
  - A.4 mining-time-vs-evaluation-time gate misalignment
    interpretation (Observations 9 + 10 + 11) hinges on
    "deliberate-staged-tightening vs defect" adjudication at
    structured re-examination depth
  - B.2 + B.3 noise-floor consistency claims at descriptive
    register only; rigorous null-distribution comparison is Q-9.A
    territory out-of-scope per §3.2.5
  - One-of-198 sample size insufficient for rigorous tail-event
    -vs-systematic-pattern discrimination at light-touch register
- The cross-cutting pattern is exactly the spec §4.3 C.3 register:
  evidence at descriptive register suggests Case A or Case B but
  rigorous discrimination requires structured re-examination at
  depth greater than light-touch + statistical-significance
  machinery + ingest-layer mechanism reconstruction.

**Boundary disqualifying counter-evidence at C.3 register**:

- The §7 evidence base is not unambiguous at light-touch register
  (per §7.0 + §7.1 + §7.2.1 + §7.2.2 above); the qualification
  ambiguity is the C.3-applicability trigger pattern, not the
  absence of evidence. Whether structured re-examination depth
  would resolve this ambiguity is out-of-light-touch-scope; §8
  (Step 6 territory) question.

**Sub-register C.3 evidence-base summary**: qualifying evidence is
**direct** at descriptive register — §7.0 + §7.1 evidence-base
summaries explicitly document light-touch-register limitations at
multiple sub-registers; the cross-cutting pattern of "evidence at
descriptive register; rigorous discrimination out-of-scope" matches
spec §4.3 C.3 evidence-pattern register descriptively. §8 (Step 6
territory) applies the §4.4 one-and-only-one rule to this evidence
base.

#### 7.2.4 Case C cross-sub-register evidence-base summary

Cross-sub-register summary (this is evidence-map summary, NOT case
determination per spec §5.5 + §4.4 + §5.6 — §8 territory):

| sub-register | qualifying evidence at descriptive register | applicable to §7 evidence base? |
|---|---|---|
| C.1 | direct (A.4 qualifying-vs-disqualifying balance ambiguous) | YES — §7.0 A.4 register |
| C.2 | direct (B.2 + B.3 mixed qualifying / counter-qualifying for lone-survivor specificity register) | YES — §7.1 B.2 + B.3 register |
| C.3 | direct (multiple light-touch-register limitations across §7.0 + §7.1) | YES — cross-cutting |

§8 (Step 6 territory) applies the spec §4.3 Case C determination
criterion ("any ONE of C.1 / C.2 / C.3 applicable" + sub-register
documentation requirement) and the spec §4.4 one-and-only-one rule
to this evidence base; §7 does not pre-empt that determination.

### 7.3 Cross-case evidence-base summary

This sub-section consolidates §7.0 + §7.1 + §7.2 evidence-base
summaries at a register suitable for §8 (Step 6 territory) case
determination. **NOT case determination at §7** (per spec §4.4
+ §5.6 Step 6 territory); §7.3 is evidence-map consolidation only.

| case | evidence-base register at light-touch |
|---|---|
| Case A | A.1 / A.2 / A.3 sub-registers: qualifying evidence weaker than disqualifying counter-evidence (NOT cleanly satisfied as Case A.x defect at any sub-register). A.4 sub-register: qualifying evidence direct; disqualifying counter-evidence direct; balance interpretively ambiguous at light-touch register. |
| Case B | B.1: 3 of 4 Case A sub-registers satisfy "weaker-than-disqualifying"; A.4 sits at qualifying-vs-disqualifying boundary. B.2 + B.3: partial qualifying at descriptive register; rigorous null-test out-of-scope per §3.2.5. |
| Case C | C.1 / C.2 / C.3 sub-registers: each shows direct qualifying evidence at descriptive register matching the corresponding spec §4.3 evidence-pattern text. |

§8 (Step 6 territory) must adjudicate this evidence base under spec
§4.4 one-and-only-one rule. §7 surfaces evidence tensions only —
specifically:

1. **A.4 sub-register tension**: direct qualifying evidence
   (Observations 9 + 10 + 11 align with spec §4.1 A.4 text) AND
   direct disqualifying counter-evidence (canonical AND-gate is
   deliberately permissive; ingest-layer out-of-scope; one-of-198
   consistent with B.3); §8 must adjudicate whether the qualifying-
   vs-disqualifying balance maps to Case A.4 (clean qualification),
   to Case B (qualifying weaker than disqualifying), or to Case
   C.1 (qualifying-vs-disqualifying balance ambiguous register).
2. **Lone-survivor specificity tension**: lone-survivor's hybrid
   quality profile (audit-only origin + single-trade-margin
   exclusion + permissive AND-gate at -10.2% return + theme
   alignment at thin-theme register) traces to specific
   mining-process inputs rather than purely random pattern; §8
   must adjudicate whether this specificity register maps to
   tail-event-consistent (B.3 register) or to mining-time-vs-
   evaluation-time gate misalignment (A.4 register) or to mixed-
   register ambiguity (C.2 register).
3. **Cross-cutting light-touch-register limitation tension**: B.2
   + B.3 noise-floor consistency at descriptive register only
   (Q-9.A territory out-of-scope per §3.2.5); A.2 sub-register
   evidence-mapping requires the Critic-as-gate precondition that
   does not hold at this batch (Critic operates as annotator per
   §3.2.6 + CLAUDE.md hard rule "Critic annotates only, never
   filters"); A.4 deliberate-staged-tightening-vs-defect
   adjudication unresolved at light-touch register; §8 must
   adjudicate whether the evidence base is sufficient for clean
   Case A or Case B determination at light-touch register or
   whether C.3 register applies.

§7 does NOT enumerate forward-pointer options at §7.3; per spec
§4.4 Case A / Case B / Case C rows, the forward-pointer register
is §8 closeout-§1-verdict territory at Step 6. §7.3 surfaces
evidence tensions only; §8 maps the determination + applicable
forward-pointer per spec §4.4 register.

### 7.4 Step 5 deliverable summary + gating-criterion check

Per spec §5.5 gating criterion: **"§7 working draft has structured
evidence maps for all three cases"**.

Status:

- **§7.0 Case A evidence map** (A.1 / A.2 / A.3 / A.4): documented
  across 4 sub-sections + §7.0.5 cross-sub-register summary; per-
  sub-register qualifying-evidence summary + disqualifying-counter-
  evidence summary at register required by spec §4.1 ✓
- **§7.1 Case B evidence map** (B.1 / B.2 / B.3): documented across
  3 sub-sections + §7.1.4 cross-sub-register summary; per-sub-
  register qualifying-evidence summary + disqualifying-counter-
  evidence summary at register required by spec §4.2 ✓
- **§7.2 Case C evidence map** (C.1 / C.2 / C.3): documented across
  3 sub-sections + §7.2.4 cross-sub-register summary; per-sub-
  register qualifying-evidence summary at register required by
  spec §4.3 ✓
- **§7.3 cross-case evidence-base summary**: cross-case
  consolidation table at register suitable for §8 (Step 6) case
  determination; forward-pointer register documented at allowed-
  register only per spec §4.4 + §7.1 cycle-boundary preservation ✓

Step 5 gating criterion satisfied. Step 6 (case determination +
closeout assembly per spec §5.6) authorized to proceed in
subsequent session per discrete-session-boundary register.

Per spec §6 verification framework + §7 cycle-boundary preservation:

- **§6.1 Evidence-mapping discipline**: every §7 claim cites a
  specific source — file:line citation for code claims; PHASE2C_8.1
  closeout section anchor for canonical-number claims; §3-§6
  cross-reference for mechanism / observation claims; explicit
  "this is interpretation, not observation" framing where evidence
  mapping reaches qualifying-vs-disqualifying-counter-evidence
  adjudication boundary ✓
- **§6.4 Cycle-boundary-preservation language audit**: §7 contains
  no PHASE2C_10 / successor-arc pre-naming; no "this confirms",
  "this requires", "this means we proceed to" forward-pointer
  language; no Case A/B/C single-case adjudication (§7.X
  qualifying-vs-disqualifying summaries are per-sub-register
  evidence summaries, not case determinations); §7.3 forward-
  pointer register restricted to allowed-register per spec §4.4 +
  §7.1 ✓
- **§6.3 Canonical-number cross-checks**: §7 references PHASE2C_8.1
  canonical anchors (cohort_a_filtered = 0; per-regime pass rates;
  one-of-198 cardinality) at PHASE2C_8.1 closeout anchor register;
  §7 references §3-§6 internal canonical numbers (40/40/40/39/39
  generation distribution; 198 valid candidate count;
  theme_coherence formula at D7a register; lone-survivor metrics
  per §6.3) at internal-anchor register ✓

Scope-completeness audit per Claude advisor's prior carry-forward
(necessary-and-sufficient register; no §8 deliverable leakage):

- **§7 does NOT include single-case Case determination** (Step 6
  §8 territory per spec §5.6 + §4.4 one-and-only-one rule). §7.3
  cross-case summary is evidence-base consolidation at register
  suitable for §8 application of one-and-only-one rule, NOT
  application of one-and-only-one rule itself. ✓
- **§7 does NOT include new mechanism descriptions** (Step 1 §3
  territory). All §7 mechanism references trace to §3 reconstruction
  + file:line citations to existing code; no new mechanism
  reconstruction surfaces at §7. ✓
- **§7 does NOT include 198-candidate full re-analysis** (per spec
  §3.2.3); evidence base draws on §3-§6 working-draft register
  (mechanism + artifact-distribution + cross-tab + lone-survivor
  trace) only. ✓
- **§7 does NOT include statistical-significance machinery** (Q-9.A
  territory; out-of-scope per spec §3.2.5). Noise-floor-consistency
  claims are at descriptive-register only; rigorous null-distribution
  comparison surfaces as spec §3.2.5 out-of-scope flag at multiple
  sub-registers (B.2, B.3, C.3). ✓
- **§7 does NOT include calibration-variation grid** (Q-9.C territory;
  out-of-scope per spec §3.2.6). AND-gate calibration question
  surfaces at A.4 + B.3 sub-registers as light-touch-register
  limitation, not as variation grid. ✓
- **§7 does NOT include ingest-layer mechanism reconstruction**
  (per session-entry handoff scoping + spec §3 in-scope enumeration
  for Proposer + Critic + theme rotation only). Ingest-layer
  mechanism surfaces as out-of-scope flag at A.2 + A.4 + tracked-
  fix register at §8 (Step 6 territory). ✓

**Two register-precision observations surfaced for §8 (Step 6)
case-determination structuring** (NOT case determination; §8
territory):

1. **A.4 qualifying-vs-disqualifying balance is the primary §8
   adjudication boundary surfaced at §7**: A.4 qualifying evidence
   at descriptive register (Observations 9 + 10 + 11 align with
   spec §4.1 A.4 qualifying-evidence text) and A.4 disqualifying
   counter-evidence at descriptive register (canonical AND-gate
   is deliberately permissive; ingest-layer out-of-scope;
   one-of-198 consistent with B.3) are both direct at light-touch
   register. The §7 evidence base does not pre-empt §8 adjudication
   on whether the qualifying-vs-disqualifying balance maps to clean
   Case A.x qualification, to qualifying-weaker-than-disqualifying
   (Case B-direction at A.4), or to qualifying-vs-disqualifying
   balance ambiguity (Case C.1 register).
2. **Ingest-layer mechanism out-of-scope is the cross-cutting
   light-touch-register limitation surfaced at §7**: A.2
   sub-register evidence-mapping assumes Critic-as-gate
   precondition; Critic operates as annotator per §3.2.6 +
   CLAUDE.md hard rule "Critic annotates only, never filters", so
   the gate-mode precondition does not hold and the actual gate
   is the orchestrator ingest layer (out of Step 1 §3 reconstruction
   scope). A.4 (deliberate-staged-tightening-vs-defect
   adjudication) similarly references ingest-layer mechanism
   reconstruction outside Step 1 §3 scope. The cross-cutting
   pattern surfaces at C.3 sub-register's spec-§4.3-C.3 evidence-
   pattern register. §8 (Step 6 territory) tracked-fix register
   entry candidate: ingest-layer mechanism reconstruction as
   structured re-examination scope, with explicit "this is
   tracked-fix register, not pre-named successor-arc" framing per
   spec §7.2 anti-pre-naming discipline.

These observations are at register-precision register for §8
case-determination structuring per spec §5.6 sequential gating;
case determination per §4.4 one-and-only-one rule is §8 (Step 6
territory) deliverable.


## 8. Case determination (Step 6 deliverable)

This section produces the PHASE2C_9 case determination per spec
§4.4 one-and-only-one rule applied to the §7 evidence maps
(sealed at `d548ea2` Step 5 final state) under the locked Step 6
sub-spec §1.5 evidence-comparison rule (sub-spec sealed at
`d1657bd`). Per sub-spec §1.1 framing decision: §4.4 is applied
as **mechanical decision rule over threshold evaluations** with
no discretionary synthesis at case-selection layer; bounded
comparison only against §7's already-characterized
qualifying-vs-disqualifying register. §8 author inherits §7
characterization verbatim per sub-spec §1.2; does NOT
re-characterize.

### 8.0 Determination

**Case determination: Case C with sub-registers C.1 + C.2 + C.3
documented.**

Derivation chain (per sub-spec §3.1 §8.0 format requirement: §7.X
cross-sub-register summary tables + §4.1/§4.2/§4.3 determination
criteria + §4.4 mechanical rule application + determination
output):

**Step 1 — §7 cross-sub-register summary tables (verbatim
inheritance per sub-spec §1.2)**:

§7.0.5 Case A cross-sub-register summary (verbatim):

| sub-register | qualifying evidence weight | disqualifying counter-evidence weight | net qualification at light-touch register |
|---|---|---|---|
| A.1 | weak | comparable to weak qualifying | NOT cleanly satisfied |
| A.2 | weak (Observations 6 / 10 / 11 map weakly) | strong (Critic annotates only; 0 critic_rejected; ingest-layer-as-actual-gate out-of-scope) | NOT cleanly satisfied |
| A.3 | weak (modulus mismatch is design-as-intended; per-regime divergence maps more to B.2) | strong (uniform generation-side distribution; no budget exhaustion; CONTRACT BOUNDARY documents exclusion) | NOT cleanly satisfied |
| A.4 | direct (Observations 9 + 10 + 11 align with spec §4.1 A.4 text) | direct (canonical AND-gate is deliberately permissive; ingest-layer out-of-scope; one-of-198 consistent with B.3) | INTERPRETIVELY AMBIGUOUS at light-touch |

§7.1.4 Case B cross-sub-register summary (verbatim):

| sub-register | qualifying evidence weight | disqualifying counter-evidence weight | net qualification at light-touch register |
|---|---|---|---|
| B.1 | partial (3 of 4 Case A sub-registers satisfy weaker-than-disqualifying; A.4 sits at boundary) | strong at A.4 register | PARTIALLY satisfied (3 of 4 sub-registers) |
| B.2 | moderate at descriptive register | moderate (lone-survivor specificity; rigorous null-test out-of-scope) | NOT cleanly satisfied at significance-test register; partially at descriptive |
| B.3 | moderate at descriptive register | moderate (lone-survivor specificity; rigorous tail-event-vs-systematic out-of-scope) | NOT cleanly satisfied at significance-test register; partially at descriptive |

§7.2.4 Case C cross-sub-register summary (verbatim):

| sub-register | qualifying evidence at descriptive register | applicable to §7 evidence base? |
|---|---|---|
| C.1 | direct (A.4 qualifying-vs-disqualifying balance ambiguous) | YES — §7.0 A.4 register |
| C.2 | direct (B.2 + B.3 mixed qualifying / counter-qualifying for lone-survivor specificity register) | YES — §7.1 B.2 + B.3 register |
| C.3 | direct (multiple light-touch-register limitations across §7.0 + §7.1) | YES — cross-cutting |

**Step 2 — §4.1 / §4.2 / §4.3 determination criteria (verbatim)**:

§4.1 Case A determination criterion (verbatim from
[`PHASE2C_9_PLAN.md`](../phase2c/PHASE2C_9_PLAN.md) §4.1): *"at
least ONE of A.1 / A.2 / A.3 / A.4 satisfied with concrete evidence
... that meets the qualifying criteria; AND no disqualifying
counter-evidence surfaces stronger than the qualifying evidence;
AND the identified defect is plausibly addressable."*

§4.2 Case B determination criterion (verbatim): *"ALL of B.1, B.2,
B.3 satisfied with concrete evidence; AND no disqualifying
counter-evidence surfaces."*

§4.3 Case C determination criterion (verbatim): *"any ONE of C.1
/ C.2 / C.3 applicable; AND closeout document explicitly identifies
which sub-register (C.1 / C.2 / C.3) the determination falls in;
AND tracked-fix register entry surfaces the specific evidence
asymmetry that produced the Case C determination."*

**Step 3 — §1.5 evidence-comparison rule application (per sub-spec
§1.5)**:

Per sub-spec §1.5 rule 1 (use ONLY §7 evidence) + rule 2 (NO new
analysis beyond §7 descriptions) + rule 3 (ambiguity → NOT clean
qualification):

Case A application:
- A.1: qualifying weak; disqualifying comparable (per §7.0.5
  table). §1.5 rule 3 ambiguity-routing applies: comparable
  qualifying-vs-disqualifying → ambiguity at threshold register
  → NOT cleanly satisfied. §4.1 "satisfied with concrete evidence
  ... that meets the qualifying criteria" not met (qualifying is
  weak, not concrete-and-meeting-criteria). **A.1 NOT cleanly
  satisfied.**
- A.2: qualifying weak; disqualifying strong (per §7.0.5 table).
  Disqualifying stronger than qualifying → §4.1 "no disqualifying
  counter-evidence stronger than qualifying" criterion FAILS.
  **A.2 NOT cleanly satisfied.**
- A.3: qualifying weak; disqualifying strong (per §7.0.5 table).
  §4.1 FAILS at "stronger than" register. **A.3 NOT cleanly
  satisfied.**
- A.4: qualifying direct; disqualifying direct; balance
  INTERPRETIVELY AMBIGUOUS (per §7.0.5 table). §1.5 rule 3
  ambiguity-routing applies: balance ambiguity → §4.1 "stronger
  than" register cannot be established directionally → NOT clean
  qualification. **A.4 NOT cleanly satisfied per §1.5 rule 3.**

→ **Case A NOT satisfied** per §4.1 "at least ONE of A.1 / A.2 /
A.3 / A.4 satisfied" criterion (no A.x cleanly satisfied at §7
evidence base under §1.5 rule application).

Case B application:
- B.1: requires "All four Case A categories' qualifying evidence
  absent OR present-but-weaker-than-disqualifying-counter-evidence."
  A.1 / A.2 / A.3 satisfy "weaker-than-disqualifying" (per §7.0.5
  table). A.4 qualifying is direct (not weaker); balance
  INTERPRETIVELY AMBIGUOUS → §1.5 rule 3 routes ambiguity to NOT
  satisfying clean qualification at "weaker-than" register
  symmetrically. **B.1 NOT cleanly satisfied** because A.4 ambiguity
  does not establish weaker-than-disqualifying.
- B.2: §7.1.4 table reports moderate qualifying + moderate
  disqualifying (lone-survivor specificity; rigorous null-test
  out-of-scope). §4.2 requires "no disqualifying counter-evidence
  surfaces" — disqualifying counter-evidence surfaces at B.2.
  **B.2 NOT cleanly satisfied.**
- B.3: §7.1.4 table reports moderate qualifying + moderate
  disqualifying (lone-survivor specificity; rigorous
  tail-event-vs-systematic out-of-scope). §4.2 "no disqualifying"
  fails. **B.3 NOT cleanly satisfied.**

→ **Case B NOT satisfied** per §4.2 "ALL of B.1, B.2, B.3
satisfied with concrete evidence; AND no disqualifying
counter-evidence surfaces" criterion. B.1 NOT cleanly satisfied
alone is sufficient for Case B failure (per §4.2 "ALL satisfied"
criterion: any single sub-register failure produces Case B
failure). B.2 and B.3 derivation above included for completeness
of derivation chain (each independently fails the §4.2 "no
disqualifying counter-evidence surfaces" criterion); completeness
is auditing register, not necessity register.

Case C application:
- C.1: §7.2.4 table reports direct qualifying matching spec §4.3
  C.1 evidence-pattern text ("Partial qualifying evidence for
  Case A. One or more Case A categories show 'weak qualifying
  evidence' (suggestive but not concretely demonstrable defect)
  without clean Case A.x qualification"). §7.0.5 documents A.4
  qualifying-vs-disqualifying balance interpretively ambiguous
  → matches "without clean Case A.x qualification" pattern.
  **C.1 applicable.**
- C.2: §7.2.4 table reports direct qualifying matching spec §4.3
  C.2 evidence-pattern text ("Mixed qualifying / counter-qualifying
  evidence for Case B. Evidence is consistent with Case B at
  population-property register but inconsistent at lone-survivor
  or theme-level register"). §7.1.2 + §7.1.3 prose surfaces
  exactly this pattern (B.2 + B.3 partial qualifying at descriptive
  register; lone-survivor specificity at disqualifying-counter
  register). **C.2 applicable.**
- C.3: §7.2.4 table reports direct qualifying matching spec §4.3
  C.3 evidence-pattern text ("Light-touch register insufficient
  for discrimination"). §7.2.3 prose documents multiple
  light-touch-register limitations (A.1 / A.2 / A.4 / B.2 / B.3 /
  one-of-198 sample size) at cross-cutting register.
  **C.3 applicable.**

→ **Case C satisfied** at all three sub-registers C.1 + C.2 + C.3
per §4.3 "any ONE of C.1 / C.2 / C.3 applicable" criterion.

**Step 4 — §4.4 one-and-only-one rule application**:

§4.4 verbatim: *"PHASE2C_9 closeout produces exactly one case
determination (A, B, or C). Multi-case findings (e.g., 'Case A for
Proposer prompts; Case B for theme rotation') are explicitly
prohibited at closeout register; if the evidence base supports
multi-case findings, the determination is Case C with sub-registers
documented."*

Mechanical-rule input:
- Case A: NOT satisfied (no A.x cleanly satisfied)
- Case B: NOT satisfied (B.1/B.2/B.3 each fail)
- Case C: satisfied at C.1 + C.2 + C.3 sub-registers

Mechanical-rule output: **Case C with sub-registers C.1 + C.2 +
C.3 documented**. §4.4 one-and-only-one rule satisfied (exactly
ONE case determination = Case C). §4.3 sub-register documentation
requirement satisfied (closeout document explicitly identifies
applicable C.x sub-registers). §4.3 tracked-fix register requirement
satisfied (per §8.3 below: Q-9-02 evidence-asymmetry entry).

### 8.1 Sub-register documentation

Per sub-spec §3.2: §8.1 sub-register documentation required for
Case C; format = cite §7 sub-register evidence map directly +
report qualifying-vs-disqualifying register summary verbatim from
§7.X.X prose; per sub-spec §1.2 verbatim-inheritance scope, ≤2
sentences per sub-register characterization with explicit
attribution.

**C.1 sub-register documentation** (per §7.2.1 evidence-base
summary):

Per §7.2.1 C.1 sub-register evidence-base summary (verbatim
quoted, ≤2 sentences): *"qualifying evidence is **direct** at
descriptive register — §7.0 A.4 sub-register evidence-base shows
the spec §4.3 C.1 evidence-pattern register ('partial qualifying
evidence for Case A ... without clean Case A.x qualification') at
the qualifying-vs-disqualifying boundary. Boundary disqualifying
counter-evidence is conditional on structured re-examination depth
resolution, which is out-of-light-touch-scope."* C.1 applies at
PHASE2C_9 evidence base because §7.0.5 A.4 sub-register
qualifying-vs-disqualifying balance is interpretively ambiguous at
light-touch register, matching spec §4.3 C.1 "partial qualifying
evidence for Case A" register.

**C.2 sub-register documentation** (per §7.2.2 evidence-base
summary):

Per §7.2.2 C.2 sub-register evidence-base summary (verbatim
quoted, ≤2 sentences): *"qualifying evidence is **direct** at
descriptive register — §7.1 Case B evidence-base shows the spec
§4.3 C.2 evidence-pattern register ('mixed qualifying /
counter-qualifying evidence for Case B'). Boundary disqualifying
counter-evidence is conditional on structured re-examination depth
resolution, out-of-light-touch-scope."* C.2 applies at PHASE2C_9
evidence base because §7.1.2 B.2 + §7.1.3 B.3 sub-register
evidence shows mixed qualifying / counter-qualifying at
population-property vs lone-survivor-specificity register pattern,
matching spec §4.3 C.2 evidence-pattern text.

**C.3 sub-register documentation** (per §7.2.3 evidence-base
summary):

Per §7.2.3 C.3 sub-register evidence-base summary (verbatim
quoted, ≤2 sentences): *"qualifying evidence is **direct** at
descriptive register — §7.0 + §7.1 evidence-base summaries
explicitly document light-touch-register limitations at multiple
sub-registers; the cross-cutting pattern of 'evidence at descriptive
register; rigorous discrimination out-of-scope' matches spec §4.3
C.3 evidence-pattern register descriptively."* C.3 applies at
PHASE2C_9 evidence base because §7.0 + §7.1 evidence-base summaries
document multiple light-touch-register limitations (A.1 prompt-side
defect vs LLM-property-independent-of-prompt; A.2 Critic-as-gate
precondition does not hold; A.4 deliberate-staged-tightening-vs-defect
adjudication unresolved; B.2 + B.3 noise-floor consistency at
descriptive register only; one-of-198 sample-size limitation),
cross-cutting pattern matches spec §4.3 C.3 register.

### 8.2 Forward-pointer register

Per sub-spec §3.3 + spec §4.4 Case C row allowed-register: *"Light-
touch retrospective produced ambiguous evidence at sub-register
C.X; post-Q-9.B scoping cycle's deliberation surface includes (a)
structured re-examination at depth greater than light-touch, (b)
statistical-significance machinery to disambiguate noise-floor vs
systematic-pattern at Q-9.A register, (c) calibration-variation at
Q-9.C register, (d) other paths surfaced at scoping cycle."*

Forward-pointer register at PHASE2C_9 closeout:

Light-touch retrospective produced ambiguous evidence at
sub-registers C.1 + C.2 + C.3 (per §8.0 derivation chain + §8.1
sub-register documentation). Post-Q-9.B scoping cycle's
deliberation surface includes (a) structured re-examination at
depth greater than light-touch (specifically: ingest-layer
mechanism reconstruction surfaced at Q-9-01 tracked-fix register
per §8.3; A.4 deliberate-staged-tightening-vs-defect adjudication;
lone-survivor specificity register adjudication at A.4-vs-B.3
register), (b) statistical-significance machinery to disambiguate
noise-floor vs systematic-pattern at Q-9.A register (specifically:
B.2 cohort_a_filtered = 0 noise-floor null-distribution test; B.3
one-of-N tail-event-vs-systematic-pattern null-distribution test),
(c) calibration-variation at Q-9.C register (specifically: A.4
canonical AND-gate calibration variation; lone-survivor permissive
AND-gate-acceptance-of--10.2%-return calibration variation), (d)
other paths surfaced at scoping cycle.

Per spec §4.4 + §7.2 cycle-boundary preservation: this
forward-pointer register does NOT pre-name the successor scoping
cycle's substantive direction; it surfaces the deliberation surface
that the successor scoping cycle will adjudicate. Specific
direction selection is not pre-committed at PHASE2C_9 closeout.

### 8.3 Tracked-fix register entries surfaced

Per sub-spec §3.4: §8.3 tracked-fix register entries with Q-9-N
numbering convention (PHASE2C_9 arc, sequential N starting from
1). Default §8.3 enumerated list register; PHASE2C_8.1 §10
separate-section precedent not invoked at PHASE2C_9 closeout
(entry count + register at §8.3 sub-section scope).

**Q-9-01 — Ingest-layer mechanism reconstruction as structured
re-examination scope**.

Description: orchestrator ingest layer (`agents/orchestrator/ingest.py`,
which performs the actual lifecycle-state assignment per §3.2.6
"Critic annotates only — lifecycle-state assignment is the
orchestrator ingest layer's responsibility") is NOT in Step 1 §3
reconstruction scope. PHASE2C_9 §3 reconstruction covers Proposer
prompt + Critic gate + theme rotation at code register; ingest-
layer mechanism reconstruction is out-of-scope per spec §3.1
in-scope enumeration + spec §3.2.4 NO mining-process redesign.
The cross-cutting light-touch-register limitation surfaces at A.2
(Critic-as-gate precondition does not hold; actual gate is ingest
layer) + A.4 (deliberate-staged-tightening-vs-defect adjudication
references ingest-layer mechanism) + C.3 sub-register
(cross-cutting limitation register).

Surface origin: §7.4 register-precision Obs 2 (Step 5 §7.4
deliverable summary) + §7.0.2 A.2 sub-register evidence base +
§7.0.4 A.4 sub-register evidence base + §7.2.3 C.3 sub-register
evidence base.

Resolution disposition: deferred to follow-up structured
re-examination arc (NOT pre-named per spec §7.2 anti-pre-naming
discipline; "this is tracked-fix register, not pre-named
successor-arc"). The successor scoping cycle's deliberation surface
includes ingest-layer mechanism reconstruction as one of multiple
paths per §8.2 forward-pointer register; specific path selection
is not pre-committed at PHASE2C_9 closeout.

**Q-9-02 — Evidence asymmetry that produced Case C determination**.

Description (per spec §4.3 *"tracked-fix register entry surfaces
the specific evidence asymmetry that produced the Case C
determination"* requirement; content authored against §8 fresh per
sub-spec §3.4 Concern K slot-vs-content discipline):

The specific evidence asymmetry that produced the Case C
determination at PHASE2C_9 §8.0 derivation chain operates at three
sub-register pathways per §8.1 documentation:

- **C.1 evidence asymmetry**: §7.0.4 A.4 sub-register direct
  qualifying evidence (Observations 9 + 10 + the composite hybrid
  quality observation per §7.0.4 matching spec §4.1 A.4 qualifying-
  evidence text) interacts with §7.0.4 A.4 direct disqualifying
  counter-evidence (canonical AND-gate deliberately permissive at
  generation-cycle register; ingest-layer out-of-scope; one-of-198
  cardinality consistent with B.3 interpretation). Asymmetry: §7
  evidence map characterizes the qualifying-vs-disqualifying balance
  as "INTERPRETIVELY AMBIGUOUS at light-touch register" — neither
  qualifying nor disqualifying directionally established stronger
  at light-touch register. Per §1.5 evidence-comparison rule 3
  (ambiguity-routing): ambiguity NOT cleanly satisfying §4.1
  "stronger than" comparison register; §4.1 fails at A.4 → Case A
  not satisfied at A.4 sub-register. The ambiguity is the C.1
  evidence-pattern surface.
- **C.2 evidence asymmetry**: §7.1.2 B.2 + §7.1.3 B.3 sub-register
  evidence base shows lone-survivor specificity at disqualifying-
  counter register (audit-only origin per §6.3 + single-trade-margin
  filter exclusion per §7.0.4 A.4 Obs 9 + permissive AND-gate
  acceptance of -10.2% return per §7.0.4 A.4 Obs 10 + theme
  alignment at thin-theme register per §7.0.4 A.4 Obs 11). The
  specificity register interacts with §7.1 Case B population-property
  register (cohort_a_filtered = 0 + per-regime pass-rate cross-tab
  + theme-distributional 40/40/40/39/39 per §7.1.2 B.2). Asymmetry:
  evidence is consistent with Case B at population-property register
  but inconsistent at lone-survivor specificity register — the
  specificity is mining-process-input-specific (THIN_THEMES at
  THEME_HINTS; trade-count filter threshold; AND-gate criteria),
  not random-pattern-consistent. The asymmetry is the C.2 evidence-
  pattern surface.
- **C.3 evidence asymmetry**: cross-cutting light-touch-register
  limitation at A.1 (prompt-side defect vs LLM-property-
  independent-of-prompt interpretation requires structured
  re-examination at depth greater than light-touch) + A.2
  (Critic-as-gate precondition does not hold; actual gate is
  ingest layer per §3.2.6 + CLAUDE.md hard rule, out of §3
  reconstruction scope) + A.4 (deliberate-staged-tightening-vs-
  defect adjudication unresolved at light-touch) + B.2 + B.3
  (noise-floor consistency at descriptive register only; rigorous
  null-distribution comparison Q-9.A territory out-of-scope per
  §3.2.5) + one-of-198 sample-size limitation. Asymmetry: per
  spec §4.3 C.3 evidence-pattern text (verbatim quoted): *"Light-
  touch retrospective produces evidence that suggests Case A or
  Case B but at strength below the qualification threshold; the
  honest read is 'structured re-examination would be needed to
  discriminate.'"* — at PHASE2C_9 §7 evidence base, evidence at
  descriptive register matches Case A or Case B sub-register
  patterns at descriptive-register-only level; rigorous
  discrimination requires structured re-examination at depth
  greater than light-touch + statistical-significance machinery +
  ingest-layer mechanism reconstruction. The descriptive-vs-
  rigorous-discrimination asymmetry is the C.3 evidence-pattern
  surface.

Surface origin: §8.0 derivation chain + §8.1 sub-register
documentation + §1.5 evidence-comparison rule application produced
Case C output via three independent sub-register pathways
(C.1 + C.2 + C.3); the asymmetry per sub-register is the spec §4.3
required asymmetry documentation.

Resolution disposition: documentation-register; closeout-of-arc
completion. Cross-reference §8.2 forward-pointer register for
deliberation-surface options at successor scoping cycle.

### 8.4 Methodology-codification candidates surfaced

Per sub-spec §3.5 + §3.5 status-register precision per Concern L
disposition: four mandatory cumulative entries from Step 5 close
carry-forward + optional emergent entries from Step 6 cycle.
Format: description + surface origin + codification register +
status per Concern L precision.

**Mandatory methodology-codification candidate entries (4
cumulative; NOT tracked-fix entries — distinct from §8.3 register
per ChatGPT round-3 §3.5 disambiguation patch)**:

1. **Procedural-confirmation defect class instance #2** at advisor
   register.

   Description: Step 5 first-commit pattern with "verified on
   record" against own self-resolution surfaced procedural-
   confirmation defect class at advisor register; corrected via
   anchor-prose-access discipline standing instruction codification
   at Step 5 close.

   Surface origin: Step 5 dual-reviewer cycle + advisor substantive
   prose-access pass at Step 5 close + advisor process-pushback
   register.

   Codification register: §16+ METHODOLOGY_NOTES section candidate
   (procedural-confirmation defect class identification +
   corrective standing instruction codification pattern).

   **Status**: operationalized (correction operating throughout
   Step 5 follow-up patch + Step 6 sub-spec drafting cycle + Step
   6 fire authoring cycle) + codification-pending (canonical
   METHODOLOGY_NOTES update arc).

2. **Spec-vs-empirical-reality within-cycle count at 3**.

   Description: PHASE2C_10 pre-naming caught at PHASE2C_9 spec
   drafting + Stage 2c→Stage 2d attribution patched at Step 2 +
   16-char-vs-64-char hash spec divergence — three within-cycle
   spec-vs-empirical-reality findings during PHASE2C_9 arc.
   Cross-cycle accumulation pending.

   Surface origin: cross-arc carry-forward observation at advisor
   register from Step 4 → Step 5 → Step 6 sub-spec drafting cycles.

   Codification register: §16+ METHODOLOGY_NOTES section candidate
   (spec-vs-empirical-reality finding pattern; cross-cycle
   threshold for codification).

   **Status**: observation-only + cross-cycle-pending (within-cycle
   count alone below codification threshold; cross-cycle
   accumulation register required to reach threshold).

3. **Cumulative §7 carry-forward register at 11 observations
   stress-tested §7 scope at Step 5**.

   Description: Step 5 §7 evidence-mapping deliverable consumed
   11 cumulative carry-forward observations from Steps 1-4;
   selection-criterion question (do all 11 enter §7 evidence
   maps?) resolved as "all 11 enter" by spec-silence +
   inclusion-discipline reasoning. Documentation pattern (§7.0
   selection-criterion documentation + §7.0.0 inventory table
   with per-observation source-step + evidence-anchor + applicable
   sub-register columns) reusable for future N-observation
   evidence-mapping deliverables.

   Surface origin: Step 5 §7 working draft authoring cycle +
   advisor register-precision flag at Step 5 close.

   Codification register: §16+ METHODOLOGY_NOTES section candidate
   (N-observation evidence-mapping deliverable selection-criterion
   + inventory-table documentation pattern).

   **Status**: observation-only + codification-candidate
   (selection-criterion documentation pattern operationalized at
   §7.0 introduction + §7.0.0 inventory table; reusable pattern
   surfaced; codification candidate within-cycle).

4. **Anchor-prose-access discipline at multi-hundred-line
   interpretive deliverables**.

   Description: standing instruction codified at Step 5 close —
   when advisor flags substantive concerns from a structural
   summary, the next operational step is paste relevant prose
   excerpts (load-bearing sub-registers + §X.0 introductions +
   §X.3-equivalent cross-case summaries + §X.4-equivalent
   deliverable summaries + any sub-register named specifically),
   advisor does substantive pass, THEN commit. Cheap on
   documentation register; expensive when an unfound defect ships
   sealed. The "verified on record" labeling against Claude Code's
   own self-resolution (Step 5 first-commit pattern) is the
   procedural-confirmation defect class at advisor register;
   discipline does not regress.

   Surface origin: Step 5 close advisor process-pushback register
   + Step 5 follow-up patch cycle + Step 6 sub-spec drafting cycle
   (instance #2 of standing instruction) + Step 6 fire dual-reviewer
   pass cycle (instance #3 of standing instruction).

   Codification register: §16+ METHODOLOGY_NOTES section candidate
   (anchor-prose-access discipline standing instruction at
   multi-hundred-line interpretive deliverables).

   **Status**: operationalized (standing instruction operating at
   Step 5 follow-up + Step 6 sub-spec drafting cycle + Step 6 fire
   authoring + dual-reviewer pass cycle; instance #1 + instance #2
   + instance #3 corrections completed) + codification-pending
   (canonical METHODOLOGY_NOTES §16+ section candidate).

**Optional emergent entries from Step 6 cycle**:

Per Concern M acknowledgment carry-forward at sub-spec §3.5: format
matches the four mandatory entries (description + surface origin +
codification register + status); emergent entries authored at §8
closeout-cycle by §8 author; no pre-staging.

5. **Pre-fire-audit pattern at session-close-of-prior-session**.

   Description: when next operational fire is interpretive-load-
   bearing, doing pre-fire advisor audit at session-close-of-prior-
   session (rather than fire-start-of-fire-session) precludes
   mid-fire sequencing pauses. Step 5 close → Step 6 sub-spec
   drafting cycle demonstrated this pattern (Concern N §5.2
   sequencing audit at session-close took 5 checks against ~90
   lines of prose; ~5 minutes of work; precluded fire-time pause
   if any of the five had been off). Pattern reusable when bandwidth
   at session-close allows; not applicable when session-close hits
   resource limits.

   Surface origin: Step 6 sub-spec drafting cycle session-close
   close + advisor pre-fire-audit-pattern observation at
   session-close-of-prior-session register.

   Codification register: §16+ METHODOLOGY_NOTES section candidate
   (pre-fire-audit-pattern at session-close discipline; conditional
   on bandwidth availability).

   **Status**: observation-only + cross-cycle-pending (pattern
   operationalized once at Step 5 close → Step 6 sub-spec;
   reusable but bandwidth-conditional; codification candidate
   pending cross-cycle replication; status aligns with mandatory
   entry #2 register precedent — within-cycle observation alone
   below codification threshold; cross-cycle accumulation register
   required).


## 9. Cross-references and verification

Per sub-spec §4 §9 sub-section enumeration: §9.0 PHASE2C_9_PLAN.md
cross-references + §9.1 PHASE2C_8.1 canonical anchor cross-references
+ §9.2 verification framework audit (evidence-mapping; falsifiability;
canonical-number; cycle-boundary language).

### 9.0 PHASE2C_9_PLAN.md cross-references

PHASE2C_9_RESULTS.md mirrors / applies the following PHASE2C_9_PLAN.md
sections (commit `8aa1c66`):

| PHASE2C_9_PLAN.md section | PHASE2C_9_RESULTS.md mirror / application |
|---|---|
| §1 Scope and verdict | §1 Verdict |
| §2 Input universe | §2.1 Input universe |
| §3 Hard scope boundaries | §2.2 Hard scope boundaries |
| §4 Pre-registered exit conditions | §2.3 Pre-registered exit conditions; §4.1-§4.4 case-determination criteria applied at §8.0 derivation chain |
| §5.1-§5.5 Steps 1-5 implementation | §3 Mining-process source review; §4 Artifact-distribution audit; §5 Theme × pass-count cross-tab; §6 Lone-survivor walkthrough; §7 Mechanism-vs-observation comparison |
| §5.6 Step 6 implementation | §8 Case determination (this section) + §1 Verdict + §9 Cross-references and verification |
| §6 Verification framework | §2.4 Verification framework; §9.2 Verification framework audit |
| §7 Cycle-boundary preservation | §6.4 cycle-boundary-preservation language audit at closeout-document scope (Activity 10 of Step 6 fire) |
| §8 Closeout document structure | This document's §1-§9 structure (canonical compliance) |
| §9 Risks and out-of-scope items | §1.4 Verdict register (what PHASE2C_9 does not establish); §3.2 hard scope boundaries cross-references |
| §10 Cross-references | §9.0 (this section) |

PHASE2C_9 Step 6 sub-spec
[`PHASE2C_9_STEP6_SUBSPEC.md`](../phase2c/PHASE2C_9_STEP6_SUBSPEC.md)
(commit `d1657bd`) cross-references:

| PHASE2C_9_STEP6_SUBSPEC.md section | PHASE2C_9_RESULTS.md application |
|---|---|
| §1.1 Framing decision | §8.0 derivation chain (mechanical-procedure framing applied) |
| §1.2 §8 author responsibilities (verbatim-inheritance scope) | §8.1 sub-register documentation (verbatim quotes ≤2 sentences + cite-only); §1.1 per-case evidence summary (verbatim §7 inheritance) |
| §1.3 §8 author residual discretion | §8.2 forward-pointer composition; §8.3 tracked-fix entries; §8.4 methodology-codification candidates; §1.4 verdict register |
| §1.4 Framing falsifiability | §8.0 derivation chain (framing application register) |
| §1.5 Evidence-comparison rule | §8.0 Step 3 §1.5 evidence-comparison rule application; §1.2 falsifiability link-point 2 |
| §1.6 §4.4 application falsifiability (chain-falsifiability) | §1.2 falsifiability statement (3 link-points per Case C) |
| §3.1 §8.0 Determination | §8.0 (this section's derivation chain narration) |
| §3.2 §8.1 Sub-register documentation | §8.1 (C.1 + C.2 + C.3 sub-register documentation) |
| §3.3 §8.2 Forward-pointer register | §8.2 (this document's forward-pointer register) |
| §3.4 §8.3 Tracked-fix register entries | §8.3 (Q-9-01 + Q-9-02 entries; Q-9-N numbering convention) |
| §3.5 §8.4 Methodology-codification candidates | §8.4 (5 entries; 4 mandatory + 1 emergent; status-register precision per Concern L) |
| §5.2 14-step Step 6 fire activity sequence | This commit cycle (Activities 1-14; Activities 1-12 in this commit cycle; Activities 13-14 at subsequent commit cycles) |
| §5.3 Step 6 fire gating criteria | §9.2 verification framework audit checklist |

### 9.1 PHASE2C_8.1 canonical anchor cross-references

Canonical-number anchors consumed at PHASE2C_9 evidence base
(per spec §2.4):

| PHASE2C_8.1 canonical anchor | value | PHASE2C_8.1 source | PHASE2C_9 application |
|---|---|---|---|
| Total candidates | 198 | [`PHASE2C_8_1_RESULTS.md`](PHASE2C_8_1_RESULTS.md) §3.0 | §4.0 (verified at three independent measurement points) |
| Theme distribution | ~40/40/40/39/39 | PHASE2C_8.1 §7.1 | §4.0 + §5.0 |
| `cohort_a_unfiltered` cardinality | 1 | PHASE2C_8.1 §3.1 | §6.0 (lone-survivor `0845d1d7898412f2`) |
| `cohort_a_filtered` cardinality | 0 | PHASE2C_8.1 §3.1 | §7.1.2 B.2 sub-register evidence base |
| `cohort_c` cardinality | 76 | PHASE2C_8.1 §3.1 | §7.1 Case B evidence base context |
| Lone-survivor hypothesis hash | `0845d1d7898412f2` | PHASE2C_8.1 §3.1 + §6.0 | §6.0 + §7.0.4 A.4 evidence base |
| Lone-survivor theme | `volume_divergence` | PHASE2C_8.1 §7.0 + §6.0 | §6.0 + §7.0.4 A.4 evidence base |
| Lone-survivor name | `volume_surge_momentum_entry` | PHASE2C_8.1 §6.0 | §6.0 |
| Lone-survivor partition origin | audit (PHASE2C_6 audit_v1) | PHASE2C_8.1 §6.3 | §6.3 |
| In-sample-caveat asymmetry | 21 vs 8 (train-overlap pass / fully-OOS pass jointly) | PHASE2C_8.1 §5.2 | §5.1 Observation 9 + §7.1.2 B.2 evidence base context |

PHASE2C_8.1 closeout sealed at commit `69e9af9`; tag
`phase2c-8-1-multi-regime-extended-v1`. PHASE2C_9 retrospective
produces no new canonical numbers (light-touch register per spec
§6.5 independent-recompute gate; no new test required).

### 9.2 Verification framework audit

Per sub-spec §4.3 verification framework audit checklist at
final-commit register:

- [x] **§6.1 Evidence-mapping discipline**: every claim cited at
  file:line / canonical-anchor / §X-cross-reference register;
  explicit "interpretation, not observation" framing at qualifying-
  vs-disqualifying boundary register where applicable. ✓
  (§3 file:line citations to `agents/proposer/*.py` +
  `agents/critic/*.py` + `agents/themes.py`; §4 source-key citations
  to `stage2d_summary.json` + `lifecycle_counts`; §5 cross-tab
  cell citations to PHASE2C_8.1 §7.1; §6 file:line citations to
  `holdout_summary.json` artifacts + `audit_v1_filtered/`
  directory absence; §7 cross-references to §3-§6 + spec §4.1-§4.3
  evidence-pattern text; §8 derivation chain quotes spec §4.1-§4.4
  + §7.X cross-sub-register summary tables verbatim per sub-spec
  §1.2 verbatim-inheritance.)

- [x] **§6.2 Falsifiability-statement discipline**: case-determination
  assertion includes "what would falsify this conclusion" language;
  per sub-spec §1.6 chain-falsifiability per-link-point structure
  (3 link-points per Case C). ✓ (§1.2 falsifiability statement
  enumerates link-point 1 §7 characterization layer + link-point 2
  §4.1/§4.2/§4.3 threshold layer + link-point 3 §4.4 multi-case-
  findings rule layer counterfactuals applicable to Case C
  determination.)

- [x] **§6.3 Canonical-number cross-checks**: §7 / §8 references
  reproduce PHASE2C_8.1 canonical anchors. ✓ (PHASE2C_8.1 anchors
  cohort_a_filtered = 0; per-regime pass rates; one-of-198
  cardinality; lone-survivor hash + theme + name + partition
  origin; 21-vs-8 in-sample-caveat asymmetry — all reproduced at
  PHASE2C_9 §3-§7 + §8 register; no cross-check failures surfaced;
  no new canonical numbers required at light-touch register per
  §6.5.)

- [x] **§6.4 Cycle-boundary-preservation language audit at
  closeout-document scope** (Activity 10 of Step 6 fire): no
  PHASE2C_10 / successor-arc pre-naming at §1 verdict + §8 case
  determination + §9; no "next we will run X" / "this confirms Y
  is the next arc" / "this requires Z" forward-pointer language;
  no Case A/B/C single-case adjudication beyond the §8.0
  mechanical-procedure-output one Case (Case C); §1.3 + §8.2
  forward-pointer register stays at allowed-register only per
  spec §4.4 Case C row. Forbidden-language hits at meta-audit
  register / spec §7.2 historical-defect-by-descriptor-name
  register / forbidden-language scope discipline register only;
  no actual forward-pointer assertions. ✓

- [x] **§6.5 Independent-recompute gate**: light-touch register;
  no new canonical numbers requiring test. PHASE2C_9 inherits
  PHASE2C_8.1 anchors; canonical-number cross-checks at §9.1
  + §6.3 verify reproduction without new test infrastructure.
  ✓ (PHASE2C_9 produces no new numbers per spec §6.5; existing
  `tests/test_phase2c_8_1_independent_recompute.py` covers
  PHASE2C_8.1 anchors at independent-recompute register.)

Verification framework audit complete. Step 6 fire gating
criteria per sub-spec §5.3 satisfied:

- [x] Case determination per §4.4 mechanical procedure (Case C
  with sub-registers C.1 + C.2 + C.3 documented per §8.0)
- [x] §1 / §8 / §9 sub-section structure per spec §8 canonical
  structure
- [x] §6 verification framework checklist (this section)
- [x] §7 cycle-boundary preservation language audit at closeout-
  document scope (verified clean at §6.4 audit above)
- [x] Tracked-fix register entries surface §7.4 register-precision
  observations (Q-9-01 ingest-layer mechanism reconstruction
  mandatory minimum 1 entry; Q-9-02 evidence-asymmetry mandatory
  minimum 2 entries per §4.3 Case C requirement; both surfaced at
  §8.3)
- [x] Methodology-codification candidates surface 4 cumulative
  carry-forward observations from Step 5 close (mandatory minimum
  + 1 emergent entry from Step 6 cycle = 5 total; surfaced at §8.4)

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

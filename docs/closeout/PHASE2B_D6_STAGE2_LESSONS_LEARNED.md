# Phase 2B D6 Stage 2 — Lessons Learned

**Scope:** D6 Proposer, Stage 2 (Stages 2a → 2d, live Sonnet)
**Branch:** `claude/setup-structure-validators-JNqoI`
**Status at writing:** D6 Stage 2d signed off; D6 overall signed off; D7 Critic not yet started.
**Active blueprint:** `blueprint/PHASE2_BLUEPRINT.md` (v2)

---

## 1. Purpose

This document records the key decisions, observations, rejected
alternatives, and downstream implications from D6 Stage 2 (Stages 2a–2d)
and serves as the canonical bridge into D7 Critic design. It is not a
notebook summary, not a changelog, and not a restatement of the prompt
ladder. Its job is to preserve the rationale — especially the rejected
options and the non-obvious contracts — while it is still fresh, so
that D7 and D8 work can cite a single source rather than reconstruct
intent from batch artifacts.

---

## 2. What Stage 2 Established

Stage 2 proved a specific and bounded set of things. The list is
deliberately conservative.

- **Live Proposer integration is contract-stable.** The full pipeline —
  prompt build → leakage audit → pre-charge ledger → API call → raw
  payload log → classify → ingest → ledger finalize → approved-examples
  update — runs sequentially for 1-, 5-, 20-, and 200-call live batches
  with no contract violations and no mid-batch corruption.
- **Schema-valid output stabilized after the Stage 2a patch.** The
  single-call 2a forensic audit exposed schema-wording under-specification
  that allowed confabulated field shapes. After the patch (exact JSON
  example plus robust code-fence handling), valid-rate became the
  dominant outcome in 2b, 2c, and 2d.
- **Sequential approved-example accumulation works at production shape.**
  The sliding-window cap of 3, most-recent-first, pending_backtest only,
  held under 5-call, 20-call, and 200-call live batches without drift
  between ingest state and prompt context.
- **Cost accounting and partial-summary durability held at 200-call
  scale.** The pre-charge ledger pattern, the atomic-write incremental
  summary, and the crash-state recording all operated as specified
  through Stage 2d's full 200-call execution.
- **Theme-as-hint behavior produced systematic cross-theme momentum
  fallback rather than strict theme adherence.** Proposer calls biased
  toward a shared core of momentum factors across all five themes
  rather than respecting theme boundaries as filters; this is an
  observed behavior pattern, not a bug, and its interpretation is
  deferred to the Critic.

Stage 2 did **not** prove that the Proposer is production-ready for
research mining. It proved that the loop harness, accounting, and
telemetry are trustworthy enough to begin evaluating Proposer output
under a Critic.

---

## 3. Key Design Decisions and Why They Were Made

Each entry is a decision and its rationale, not an implementation note.

**3.1 Four-stage ladder (2a smoke → 2b 5-call → 2c 20-call → 2d 200-call).**
The ladder exists because live Proposer behavior is not linearly
extrapolable from stub runs. 2a was a single-call forensic probe of
schema adherence and pipeline wiring. 2b was the smallest batch that
exercises approved-examples accumulation and theme rotation across
multiple calls. 2c was the smallest batch that produces a
statistically interpretable parse-rate and a minimum of 4 calls per
theme. 2d was the first production-shape batch, at 200 calls, that
both freezes per-theme statistics at N=40 and characterizes
long-horizon mode-collapse signals. Skipping any rung would have
either hidden a class of failure or committed budget before the loop
was known-good.

**3.2 Prompt caching explicitly disabled for all of Stage 2.** Caching
was disabled to keep the cost estimator calibrated against a single
code path and to prevent inadvertent context coupling between calls
when the approved-examples window was changing. Re-enabling caching
is a legitimate optimization, but not during observation stages whose
purpose is measurement.

**3.3 Interleaved cyclic theme rotation, not block-wise.** Rotation
uses `theme_slot = (k - 1) % 5`. Interleaving ensures every theme
accumulates evenly over batch time and that any mode-collapse trend
can be attributed to batch position rather than to a theme block's
local history. Block-wise rotation would have made per-theme
statistics inseparable from time-in-batch drift.

**3.4 approved_examples cap fixed at 3, kept constant across 2a–2d.**
The cap was frozen so that prompt shape did not drift across stages
and so that approved-example accumulation behavior was comparable
across batch sizes. Changing the cap mid-ladder would have conflated
Proposer-behavior change with prompt-shape change. Tuning the cap is
an option for later phases; it was off-limits during observation.

**3.5 No prompt tuning inside observation / production batches.** The
prompt template was frozen at the start of each batch and not
adjusted based on intermediate results. The purpose of 2c and 2d was
to observe, not to iterate; prompt tuning mid-batch would have made
per-theme and per-block aggregates meaningless.

**3.6 No mid-batch pause or human review in Stage 2d.** 2d was
designed to produce a clean 200-call record of Proposer behavior
under the live harness. Pausing for review would have violated the
"production-shape" property that 2d exists to establish and would have
made the cost / execution profile non-representative. Review happens
post-batch, in the acceptance notebook.

**3.7 Notebook auditing is separated from implementation authoring.**
Acceptance notebooks recompute aggregates independently from the
orchestrator's own summary rather than consuming it. The separation
is a correctness property: if the notebook were derived from the same
author's code path, a silent aggregation bug would never surface.

**3.8 Crash-preserving partial summary made mandatory in 2d.** 2d is
the first batch where a crash at call 180 would be expensive to
re-run. The atomic-write incremental summary pattern (write `.tmp`,
`os.replace`) makes every finalized call durable and turns a crash
into a recoverable audit artifact rather than lost state. The
`batch_status` field (`in_progress` / `completed` / `crashed_at_call_N`)
is the contract that lets downstream tooling recognize a partial
summary without misreading it as complete.

**3.9 Theme-hint mapping is telemetry-only, never validation.** The
`THEME_HINTS` map is used in post-hoc per-theme telemetry
(overlap-with-hint counts, dominant-factor identification) and
nowhere else. It is not read by the prompt builder, the ingest path,
the validator, or any acceptance rule. A `CONTRACT BOUNDARY` in the
batch modules records this and must not be merged away.

### 3.9.1 Why theme-as-hint was preserved through Stage 2

By Stage 2c it was clear that themes were functioning as *hints*
rather than as *filters*: the Proposer fell back onto a shared core
of momentum-like factors across all five themes rather than
respecting theme boundaries strictly. The team intentionally did not
promote theme to a hard filter before Stage 2d for three reasons.
First, the purpose of Stage 2 was to *observe* Proposer behavior
under a single stable prompt contract; changing theme semantics
mid-ladder would have invalidated the per-theme statistics that 2d
exists to freeze. Second, converting theme to a filter would couple
D6 to a research-space decision that properly belongs to D7 (Critic)
or to D8 (orchestrator): if thin themes are systematically
under-served by the current factor registry, the correct response is
either for the Critic to score theme coherence, or for the registry
to grow — not for the Proposer prompt to silently enforce coverage.
Third, the observed cross-theme momentum fallback is itself a signal
that a future Critic should be able to see; masking it with a filter
would destroy evidence.

**3.10 Distinct factor-set tracking added in 2d.** Hash uniqueness
alone was insufficient to characterize semantic exploration: two
hypotheses with the same factor set but different thresholds or
operators hash distinctly yet represent the same structural bet.
Stage 2d therefore tracks `distinct_hash_count`,
`distinct_factor_set_count`, `unique_factor_set_ratio`, and
`repeated_factor_sets`, with empty factor-sets excluded from
saturation because they carry no structural information. This is a
correctness decision about what "novelty" means in this project, not
a reporting nicety.

---

## 4. Rejected Alternatives

These are options that were seriously considered and deliberately
rejected. They are recorded here so that future work does not
re-litigate them without re-reading the rationale.

**4.1 Enabling prompt caching in 2c / 2d.** Rejected. Caching would
have reduced nominal cost, but Stage 2 was the first live harness
where the estimator's calibration and the per-call charge path were
being observed. Introducing caching mid-ladder would have coupled
cost changes to a code-path change, destroying the estimator
calibration trajectory that is one of Stage 2's primary observables.
Caching is a post-D6 concern.

**4.2 Block-wise theme rotation.** Rejected. Grouping all calls for a
theme together would have made per-theme aggregates inseparable from
batch-position effects (warmup of the approved-examples window,
mode-collapse drift within a block). Interleaved cyclic rotation is
the only design under which per-theme statistics are comparable.

**4.3 Hard parse-rate gate in 2b.** Rejected. At N=5 a parse-rate
figure carries effectively no signal; a gate there would either
never fire or fire spuriously. The gate was held for 2c (k≥5 at 50%)
and expanded in 2d (tier-1 at k=5, tier-2 at k=20 at 75%) where
enough calls exist to separate a structural bug from noise.

**4.4 Mid-batch review or pause in Stage 2d.** Rejected. 2d's role is
to produce a contract-stable 200-call record of Proposer behavior
under a single frozen prompt. Pausing would have invalidated the
block-trend and interim-snapshot methodology (which assumes the
prompt contract is constant across the run) and would have made the
cost / execution profile non-representative of D8's future production
loop. Review is a post-batch activity in the acceptance notebook.

**4.5 Prompt structure rework during Stage 2.** Rejected except for
the one surgical 2a patch (exact JSON example + fence robustness),
which was scoped narrowly to close a schema-wording bug exposed by
the forensic audit. Beyond that single patch, reworking the prompt
inside Stage 2 was rejected because prompt changes are the largest
confounder in behavior observation; they belong either to D6 stage-1
(pre-live) or to a later dedicated prompt-iteration pass after D7
exists to score output quality.

**4.6 Replacing the stub backend rather than preserving it.**
Rejected. The stub backend is a deterministic harness for all
plumbing tests — lifecycle invariants, ingest state, ledger
semantics, cardinality stops, parse-rate gates, anomaly detectors.
Replacing it with a live-only test path would have made every test
either flaky, network-dependent, or budget-consuming. The stub is a
permanent artifact, not scaffolding.

**4.7 Tuning proposer prompts mid-batch after observing partial
results.** Rejected for the same reason as 4.5, and separately because
it would have violated the acceptance-batch contract: once a batch
begins, its prompt contract is immutable, and its raw payloads are
retained as an audit artifact. Tuning mid-batch would mean retaining
audit artifacts under inconsistent contracts, which is worse than no
tuning at all.

### 4.8 Why Stage 2 was not turned into a cost-optimization exercise

By the end of Stage 2c it was obvious that absolute spend was far
below the $20 per-batch and $100 per-month caps (Stage 2a–2c combined
were well under a dollar, and Stage 2d itself was well inside its
cap). Several legitimate cost-optimization moves were available —
enabling caching, shortening the prompt, cutting approved_examples
from 3 to 2, reducing output-token budget. All were rejected. The
reason is not that cost does not matter; it is that Stage 2's purpose
was to measure, and each of those changes would have altered the
measurement surface. Optimizing cost at that point would have
produced a cheaper but less interpretable record of Proposer
behavior. Cost optimization is a D8 concern — once the orchestrator,
the Critic, and the research loop are in place, cost knobs can be
tuned against a stable behavioral baseline. Stage 2 was the baseline;
it is not where the knobs get turned.

---

## 5. Observed Proposer Behavior

These are empirical behavior patterns that emerged across Stage 2.
They are observations, not conclusions. Interpreting them — deciding
which are acceptable, which should be scored, and which should gate
acceptance — is D7 Critic's responsibility, not D6's.

- **Stage 2a schema confabulation under under-specified schema
  wording.** The first live call produced a structurally plausible
  but schema-invalid payload whose shape was consistent with a
  reasonable misreading of the prompt's field specification. This
  was a behavior pattern driven by prompt under-specification, not a
  model capability gap.
- **Stage 2a patch effect.** Adding an exact JSON example plus
  robust code-fence handling materially changed output quality in
  subsequent stages. This is evidence that schema adherence under
  this prompt is sensitive to surface-level prompt structure; it
  also means future prompt edits should be treated as behavior-
  changing, not cosmetic.
- **Theme-as-hint rather than theme-as-filter.** Across 2b, 2c, and
  2d, the Proposer treated theme as a soft signal. Hypotheses
  nominally assigned to non-momentum themes still drew on a core
  momentum-factor vocabulary with high frequency.
- **Systematic default-factor fallback in thin themes.** Themes
  backed by a small factor subset (volume_divergence,
  calendar_effect, and to a lesser extent volatility_regime) showed
  the strongest pull toward shared momentum-like factors, consistent
  with the Proposer falling back to high-familiarity factors when
  the theme-specific vocabulary is thin.
- **Repeated factor-set reuse without hash collision.** Distinct
  hashes were produced routinely while the underlying factor set
  repeated; threshold and operator variation was the dominant source
  of structural-level duplication. This is exactly what motivated the
  2d factor-set saturation metrics.
- **Growing output-token length as approved-example history
  accumulates.** Once the approved-examples window saturates at 3,
  output length stabilizes but sits higher than in earlier calls; the
  dynamic input-token estimator tracks this reasonably but not
  tightly.
- **Stable but conservative estimator ratio by the end of Stage 2.**
  The cost estimator remains on the conservative side of actual
  spend across 2c and 2d; this is acceptable (the pre-charge pattern
  requires an upper bound) but is worth recording because a future
  cost-optimization pass will want to recalibrate rather than assume
  the ratio is tight.

---

## 6. D7 Critic Design Inputs

These are the concrete inputs Stage 2 provides to D7 Critic design.
They are written as a numbered list so they can be cited directly in
the D7 blueprint.

1. **Hash uniqueness is not semantic novelty.** The Critic must not
   treat distinct `hypothesis_hash` as evidence of distinct research
   bets. Stage 2d routinely produced distinct hashes over a repeated
   factor set.
2. **Repeated factor-set reuse with threshold / operator variation
   is a possible overfitting signal.** The Critic should be able to
   see the factor set, not just the full DSL, and to weigh repeated
   factor-set appearances with varied thresholds as a distinct risk
   category from genuinely new structural bets.
3. **Theme coherence should be scored, especially for thin themes.**
   The Critic should distinguish hypotheses that use theme-consistent
   factors from hypotheses that default to cross-theme momentum
   fallback. Theme-coherence scoring is the right place to address
   the behavior that theme-as-filter would have masked.
4. **Default momentum-factor fallback should be visible to the
   Critic.** The Critic's view of a proposal should include whether
   its factor set sits inside the theme's hint vocabulary or defaults
   to a shared fallback set. This is a feature of the review surface,
   not a filter on acceptance.
5. **Schema-valid output is necessary but not sufficient.** Stage 2's
   acceptance path stopped at schema validity + complexity + dedup.
   The Critic is the first mechanism that evaluates research
   plausibility, and it must not implicitly treat
   `lifecycle_state == pending_backtest` as any kind of positive
   signal.
6. **Factor-set saturation and `unique_factor_set_ratio` are useful
   reviewer signals even before full backtest results.** These
   aggregates let the Critic reason about a batch's structural
   diversity without needing to wait on the training window
   evaluation. They are cheap, available pre-backtest, and robust to
   threshold-only variation.
7. **"Theme hint respected weakly" is distinct from "theme entirely
   ignored".** The Critic should preserve this distinction rather
   than collapsing both into a single theme-violation category;
   Stage 2 showed that the mid state (uses some theme factors plus
   some momentum fallback) is the dominant case and it is the one
   most worth characterizing.
8. **Structural novelty likely matters more than name or hash
   uniqueness.** The combination of factor set, operator pattern,
   and direction of comparison is the right unit of novelty. The
   Critic's dedup-like logic (if any) should operate at this level,
   not at the hash level, which D3 already covers for strict
   equivalence.
9. **Empty or degenerate factor sets should not count as diversity.**
   Stage 2d explicitly excludes empty factor sets from saturation
   aggregates; the Critic should apply the same exclusion rule so
   that degenerate hypotheses do not inflate apparent novelty.
10. **The anomaly log is pre-digested evidence, not a verdict.** 2d
    emits an anomaly log with six detectors (factor-set ratio,
    output-tokens, RSI14 concentration, repeated factor-sets, etc.).
    These flags are useful inputs to a Critic or reviewer but are
    not themselves reject signals; the Critic should weigh them in
    context rather than treat any single flag as dispositive.

---

## 7. Cost and Execution Profile

Stage 2 spend progressed from sub-dollar at 2a (single call) to
low-single-digit dollars across 2b and 2c (5- and 20-call batches)
to well inside its $20 per-batch cap at 2d (200 calls). The aggregate
Stage-2 spend sits far below both the per-batch cap and the
$100-per-UTC-month cap. The pre-charge estimator ran consistently on
the conservative side of actual spend — a ratio that tightened as
calibration improved across stages but never inverted. Caching was
deferred despite the obvious cost upside because Stage 2's purpose
was to produce a clean behavioral record under one stable code path,
not to minimize cost; caching would have changed both the cost-path
and the prompt-path surface simultaneously. Execution time per call
was dominated by the API round trip; the local plumbing (ledger
write, classify, ingest, approved-examples update, atomic summary
write) was not a bottleneck at 200-call scale and is expected to
remain off the critical path at D8's target batch sizes. The
operational conclusion is that D6's loop has headroom on both cost
and time; D8 can plan its production loop around a generously-sized
research space rather than a cost-constrained one.

---

## 8. Audit / Notebook Methodology Evolution

The audit methodology was deliberately scaled up stage by stage. Each
scale-up was motivated by a change in what a single reviewer could
verify by eye.

- **2a — single live-call forensic audit.** The entire prompt, the
  entire response payload, every ledger row, and every lifecycle
  transition were read end-to-end by a human. This was tractable
  because N=1 and necessary because it was the first live call.
- **2b — 5-call full live audit.** Every call was still reviewed in
  full, and the approved-examples accumulation trajectory was the
  new verification surface relative to 2a. The audit was still
  exhaustive.
- **2c — independent aggregate recomputation and per-theme rebuild.**
  At N=20 per-call exhaustive review remained possible, but aggregate
  metrics (parse-rate, per-theme distribution, cardinality, overlap
  with theme hints) were recomputed in the notebook from raw payloads
  independently of the orchestrator's own summary. This is the first
  stage where "the notebook agrees with the summary" becomes a
  meaningful cross-check rather than a tautology.
- **2d — key-position full audit + structural audit + sampling + full
  aggregate recomputation.** At N=200 exhaustive review is no longer
  practical, so the audit split into (a) full review of
  contract-critical positions (first call, last call, snapshot
  positions at 50/100/150/200, any anomaly-flagged calls),
  (b) structural audit of invariants (monotonic call index,
  lifecycle-state terminal coverage, ledger pending/completed
  balance, crash-state absence), (c) sampling of remaining calls,
  and (d) full notebook recomputation of every aggregate the
  orchestrator reports, from per-call state alone.

The other structural shift, visible across all four stages, was
**separation of notebook authoring from implementation authoring**.
Acceptance notebooks recompute aggregates from raw payloads and
per-call records rather than consuming the orchestrator's own summary.
Any convergence on a single author would turn the notebook into a
mirror of the implementation and silently erase the correctness check
that "two independent derivations of the same aggregate agree." At
N=20 this mattered. At N=200 it was non-negotiable.

### 8.1 Multi-model review surfaced non-overlapping concerns

The Stage 2 acceptance pipeline was reviewed under a three-way
(multi-model) review process. The reviews did not converge on the
same findings — which was the point. They surfaced non-overlapping
concerns across three axes: **process semantics** (e.g., "what does
`hypotheses_attempted` count when a Proposer call returns empty?",
"when is the lifecycle invariant legitimately allowed to fail?"),
**engineering robustness** (e.g., atomic-write semantics on partial
summaries, crash-state recording, estimator upper-bound discipline),
and **reviewer methodology** (e.g., the separation of notebook
author from implementation author, the scope of sampling vs full
audit at N=200, what counts as an independent recomputation). Each
axis produced findings the others missed, and collectively they
tightened Stage 2 decisions materially — particularly around
lifecycle invariant placement at batch close, factor-set saturation
semantics, and the 2d atomic-write checkpointing contract. The
lesson, recorded here because it applies beyond Stage 2, is that
review diversity across those three axes matters more than review
depth along any one axis.

---

## 9. What Must Not Be Forgotten If D6 Is Revisited

Short, practical. Future refactors of D6 must preserve each of these
contracts.

- **Raw-payload retention for signed-off acceptance batches.** The
  `raw_payloads/batch_<uuid>/` directories for Stage 2a, Stage 2a
  post-patch re-smoke, Stage 2b, Stage 2c, and Stage 2d are audit
  artifacts and must not be deleted or bulk-cleaned without explicit
  human approval. This is enforced in `CLAUDE.md`; refactors must not
  relax it.
- **Partial-summary checkpointing in long live batches.** The
  atomic-write pattern and the `batch_status` field
  (`in_progress` / `completed` / `crashed_at_call_N`) are contract,
  not convenience. Any refactor of the orchestrator must preserve
  both the atomicity and the status field's semantics.
- **approved_examples sliding-window semantics.** Cap = 3,
  most-recent-first, `pending_backtest`-only. A refactor that
  accidentally widens the pool to include terminal non-pending
  states, changes ordering, or changes the cap is a behavior change,
  not a cleanup.
- **Frozen grammar and frozen factor registry during batches.** The
  Proposer may not propose new factors or new operators inside a
  batch; the orchestrator may not grow either mid-batch. This is
  already a Phase 2A hard constraint and remains the invariant that
  makes `hypotheses_attempted` comparable across a batch.
- **Theme mapping remains telemetry-only.** `THEME_HINTS` is a
  reporting artifact and must never be read by the prompt builder,
  validator, ingest path, or any acceptance rule. The `CONTRACT
  BOUNDARY` in the batch modules records this.
- **Invalid-path robustness must remain even if valid-rate is high.**
  `invalid_dsl`, `rejected_complexity`, `duplicate`, and
  `backend_empty_output` are terminal lifecycle states. A refactor
  that treats them as rare edge cases and drops their test coverage
  will re-open classes of silent failure that Stage 2 was designed
  to close.
- **Distinct factor-set tracking in long batches.** Saturation
  aggregates (`distinct_factor_set_count`, `unique_factor_set_ratio`,
  `repeated_factor_sets`, empty-set exclusion) are load-bearing for
  mode-collapse detection at N≥100. They are not reporting sugar and
  must not be removed during cleanup.

---

## 10. Final Position at D6 Close

D6 Stage 2 is complete. D6 overall is signed off. The Proposer loop,
its accounting, its telemetry, its crash-preserving checkpointing,
and its audit methodology are trustworthy enough to support the
work that comes next. The next phase is D7 Critic, and D7 should
treat this document as one of its input references — particularly
Section 6 (D7 Critic Design Inputs) and the observed-behavior
patterns in Section 5. This document, together with
`PHASE2A_SIGNOFF.md`, constitutes the canonical bridge into D7.

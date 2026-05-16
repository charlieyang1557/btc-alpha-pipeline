# Phase 2.5 — Combined Factor Bandit + Semantic Dedup Scoping Decision

**Cycle classification**: process/spec deliverable register-class (NOT substantive empirical research register-class). Parallel-class to Path 3 methodology consolidation scoping cycle (entry `697c26b` → SEAL `6750274` + Phase Marker advance `578df13`) and Phase 5 entry scoping cycle (`697c26b`).

**Cycle authorization**: Charlie register-event boundary 2026-05-16 — Option-1 combined-cycle pick from the three-option deliberation in this conversation. Branch isolation strategy authorized at the same register-event boundary (parked-branch registration commit `15f2108`).

**Branch**: `phase2.5/bandit-dedup` (base `15f2108`). Parked per [`docs/parked/PARKED_BRANCHES.md`](../parked/PARKED_BRANCHES.md). Activation trigger: future batch cadence resumption (e.g., Phase 2D AI loop activation, Phase 2.5 pre-batch infrastructure cycle, or any Charlie-authorized batch arc exercising between-batch learning or near-duplicate filtering).

---

## §1 Cycle scope

### §1.1 What this scoping cycle IS

- Enumeration of design candidates for **(A) Factor Bandit** and **(B) Semantic Dedup** as a combined deliverable
- Classification of candidates by track (A / B / cross-track X) with proposed defaults
- Proposal of HARD CONSTRAINT additions (discipline locks) to be merged into CLAUDE.md at the future merge register-event
- Bar criteria + filter framework for sub-spec cycle's per-decision disposition
- V# self-checklist for SEAL register
- Anti-pre-emption invariant statement

### §1.2 What this scoping cycle IS NOT

- Per-decision DEFAULT-vs-ALTERNATIVE adjudication (reserved for sub-spec drafting cycle)
- Drafting of implementation code or pseudocode (reserved for implementation arc)
- Authorization of sub-spec drafting cycle entry (separate Charlie register-event required)
- Authorization of implementation arc entry (separate Charlie register-event required)
- Authorization of merge to main (separate Charlie register-event + pre-merge verification required)
- Modification of CLAUDE.md HARD CONSTRAINTS on main (deferred to merge time)
- Push to remote (parked branch stays local until activation or explicit user push authorization)

### §1.3 Three-session pacing (authorized 2026-05-16)

- **Session 1**: scoping decision doc draft (commit `97f7774` on parked branch; 18 design candidates + 12 discipline locks + 13 V# anchors at draft register)
- **Session 2**: parallel reviewer routing — 2 internal Claude Code subagents fired independently (architect + planner per Charlie register-event 2026-05-16), per-fix adjudication thereafter (no bulk-accept per [`feedback_reviewer_suggestion_adjudication.md`](../../.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_reviewer_suggestion_adjudication.md))
- **Session 3 (SEAL register)**: apply 15 adjudicated dispositions (8 ADOPT + 6 ADOPT-LIGHT + 1 PUSHBACK) + V# self-check + SEAL fire commit. Post-SEAL deliverable: **23 design candidates** (Track A: 11 / Track B: 8 / cross-track X: 4) + **14 discipline locks** proposed (7 per track) + **15 V# anchors**.

### §1.4 Activation trigger reaffirmation

Parked branch `phase2.5/bandit-dedup` activates when Charlie register-event boundary establishes active batch cadence resumption. Until then: no merge, no remote push (unless explicit user authorization). Pre-merge verification 10-item checklist per [`docs/parked/PARKED_BRANCHES.md`](../parked/PARKED_BRANCHES.md) applies at merge time.

### §1.5 Sub-spec cycle decomposition (open question, default-recommended posture stated)

The sub-spec drafting cycle that succeeds this scoping cycle may be:

- **(α) Combined single cycle** producing a shared `BatchIngestState` lock (per X-1) as its first deliverable, then per-track refinement of all 23 decisions
- **(β) Per-track split** with Track A and Track B sub-spec cycles running independently; in this branch the shared `BatchIngestState` lock would either (β1) come from whichever cycle enters first, or (β2) be elevated to a separate Charlie register-event pre-sub-spec lock

**Default-recommended posture (NOT pre-authorized)**: (α) combined first cycle. Rationale: X-1 cross-track coordination is load-bearing and benefits from atomic adjudication. Per-track refinement can still happen within a combined cycle's pacing.

This question is surfaced (not resolved) at this scoping SEAL, modeled on Path 3 SEAL §6 #9 "surface, do not resolve at this scoping SEAL" precedent. The (α/β) decision is itself reserved for the sub-spec drafting cycle entry register-event boundary.

---

## §2 Candidate enumeration

### §2.1 Track A — Factor Bandit (11 open decisions, A-1..A-11)

Architectural sketch locked at scoping (subject to sub-spec refinement): new module `agents/orchestrator/factor_bandit.py`. State persistence via new tables `factor_posterior` + `factor_bandit_observations` either in `agents/spend_ledger.db` (extend schema) or new `factor_bandit.db` (sub-spec decides). Update timing: at batch close, after `assert_lifecycle_invariant_at_batch_close()` passes. Factor extraction reuses [`agents/critic/d7a_feature_extraction.py`](../../agents/critic/d7a_feature_extraction.py)::`extract_factors(dsl)` — already deterministic, no new code path. Curation: Thompson sampling between batches; top-K factor menu injected via existing-but-unused `top_factors` parameter at [`agents/proposer/prompt_builder.py:117`](../../agents/proposer/prompt_builder.py) (injection site lines 212–213 currently emits "(no signal yet)").

**A-1: Cold-start prior**
- Scope: initial Beta(α, β) per factor before any regime-holdout feedback accumulates
- **Proposed default**: Beta(1, 1) uniform (uninformed)
- Alternatives: Beta(0.5, 0.5) Jeffreys prior, Beta(2, 2) conservative, empirical prior bootstrapped from Phase 1B walk-forward results
- Sub-spec disposition: TBD at sub-spec drafting cycle (eligible-not-named)
- Risk: too-flat prior delays exploitation; too-strong prior risks anchoring on small-sample noise

**A-2: Demotion policy**
- Scope: when (if ever) to remove a factor from the curated menu permanently
- **Proposed default**: keep factor in registry forever; never remove from menu; the Thompson posterior naturally down-samples low-performing factors
- Alternatives: hard removal threshold (e.g., β > 50α), soft tier (rare-sample factors get separate exploration bucket)
- Sub-spec disposition: TBD
- Risk: hard removal = strong implicit signal that could be reverse-engineered if leaked; default policy avoids that surface

**A-3: K size (top-K curation)**
- Scope: how many factors appear in the curated menu per batch
- **Proposed default**: K=5 (matches existing `stage2b_batch.py` theme_factors size)
- Alternatives: K=3 aggressive, K=7 moderate, K=10 permissive, adaptive K based on Beta posterior variance
- Sub-spec disposition: TBD
- Risk: too small = under-exploration; too large = no real guidance signal

**A-4: Decay / forgetting**
- Scope: whether old regime-feedback observations decay in influence over time
- **Proposed default**: no decay for MVP (Bayesian posterior accumulates indefinitely)
- Alternatives: exponential decay with half-life, sliding window (last N batches only), regime-change-detection-based reset
- Sub-spec disposition: TBD; calibration test needed if decay is adopted
- **Risk (revised, observable-failure-mode template)**: if no-decay default is wrong (regime non-stationary), posterior anchors to pre-regime-change winners and Thompson sampling under-explores new conditions. **Detectable as**: monotonic decline in regime-holdout pass rate across N batches following a candidate regime shift; cross-batch factor pass-rate correlation > threshold when batches span the shift.

**A-5: Thompson sampling seed / reproducibility**
- Scope: determinism of the sampling for replay / debugging
- **Proposed default**: `hash(batch_id)` deterministic seed; same batch_id → same top-K factors
- Alternatives: fresh RNG per batch (non-reproducible), session-level seed, no determinism guarantee
- Sub-spec disposition: TBD; affects test pattern shape
- **Risk (revised, observable-failure-mode template)**: if non-determinism is adopted instead, leakage audits and replay artifacts become non-reproducible across re-runs. **Detectable as**: two replay runs of the same `batch_id` producing different `top_factors` blocks; failure of golden-file tests against curation snapshots.

**A-6: Signal axes**
- Scope: what `regime_holdout_passed` is the bandit's reward; does it learn from other axes?
- **Proposed default**: `regime_holdout_passed` only (binary)
- Alternatives: multi-axis (validity rate, novelty score, D7a complexity, D7b motivation quality)
- Sub-spec disposition: TBD; multi-axis adds dimensionality + hyperparameters
- Risk: single axis may miss "good ideas that fail for unrelated reasons" (DSL invalidity, dedup, etc.); but adding axes = scope creep

**A-7: Menu phrasing in Proposer prompt**
- Scope: how the curated factors are presented without leaking regime-pass information
- **Proposed default**: "Available factors (recommended)" — neutral
- Alternatives: "Available factors (curated for today's batch)", "Available factors (top selections)", "Recommended factors for hypothesis generation"
- Sub-spec disposition: TBD; subject to leakage-audit extension (see §4 A-Lock-4)
- Risk: any phrasing that hints at "why" leaks regime info; default is most neutral

**A-8: Per-batch vs per-call curation cadence**
- Scope: does the top-K menu update mid-batch (per Proposer call) or only between batches
- **Proposed default**: per-batch (frozen for batch duration; sampled once at batch open)
- Alternatives: per-call (re-sample per Proposer API call within batch), hybrid
- Sub-spec disposition: TBD
- Risk: per-call introduces in-batch variability that's hard to audit; per-batch is cleaner

**A-9 (added Session 3 per P-F1)**: **Bandit observation forensic schema**
- Scope: column shape and granularity of the `factor_bandit_observations` ledger
- **Proposed default**: `(batch_id TEXT, factor_id TEXT, regime_holdout_passed INTEGER, observed_utc TEXT, hypothesis_hash TEXT, posterior_alpha_pre REAL, posterior_beta_pre REAL)` — append-only, one row per (batch_id, factor_id, hypothesis) tuple where the factor appeared in a regime-terminal hypothesis
- Alternatives: aggregated per-batch (one row per factor per batch), denormalized with curation rank, dual ledger (observation + posterior snapshot table)
- Sub-spec disposition: TBD; interacts with A-Lock-5 append-only constraint and A-Lock-7 non-prompt leakage scope
- Risk: too coarse loses forensic replay; too fine bloats SQLite and increases leakage surface

**A-10 (added Session 3 per P-F1)**: **Error path on `extract_factors(dsl)`**
- Scope: behavior when `extract_factors` returns empty set or raises during bandit observation pass
- **Proposed default**: skip observation for that hypothesis; log to orchestrator-internal log; do not count in posterior update; do not block batch close
- Alternatives: hard-fail batch close (treat as discipline violation), fall-through-to-no-update (silent skip without log), treat as null factor (anti-pattern)
- Sub-spec disposition: TBD; interacts with `assert_lifecycle_invariant_at_batch_close()` semantics
- Risk: silent skip without log creates forensic gap; hard-fail creates fragility against legitimate edge cases (e.g., DSL with no factor references)

**A-11 (added Session 3 per P-F1)**: **Batch-summary visibility scope for curated menu**
- Scope: does the per-batch curated factor menu (top-K) appear in batch summary exports / leaderboards / reports
- **Proposed default**: orchestrator-internal log only; NOT in batch summary, leaderboard, or report
- Alternatives: visible in batch summary (counts only, no posterior values), visible in operator-only debug report, visible in human-readable batch report
- Sub-spec disposition: TBD; tightly bound to A-Lock-7 (non-prompt leakage surfaces)
- Risk: any visibility outside orchestrator-internal logs creates additional leakage surface; future LLM context construction (e.g., approved_examples assembly) may inadvertently include batch summary content

### §2.2 Track B — Semantic Dedup (8 open decisions, B-1..B-8)

Architectural sketch locked at scoping (subject to sub-spec refinement): new module `agents/orchestrator/semantic_dedup.py` (NOT inside `agents/hypothesis_hash.py` — preserves D2/D3 CONTRACT BOUNDARY). Pipeline: D3 byte-identical hash check first → if pass, run embedding similarity vs in-batch cache → if cosine ≥ τ, route to new lifecycle state `near_duplicate`. New lifecycle state `near_duplicate` added to [`agents/orchestrator/ingest.py`](../../agents/orchestrator/ingest.py) state machine. Counts toward `hypotheses_attempted` (DSR denominator) like `DUPLICATE`. Skips backtest. Embedding model: `sentence-transformers` `all-MiniLM-L6-v2` local CPU (~60 MB model, ~50–200 ms per embedding, $0 API cost). Added to `pyproject.toml` under optional extra `phase2_5 = ["sentence-transformers>=2.0.0"]`.

**B-1: Cosine similarity threshold τ**
- Scope: cutoff above which two embeddings are treated as near-duplicates
- **Proposed default**: τ = 0.82 starting point; calibrate via parameterized sweep over fixture corpus + Phase 2C Stage 1 batch DSL pairs
- Alternatives: 0.70 / 0.75 / 0.80 / 0.85 / 0.88 / 0.90 (sweep)
- Sub-spec disposition: TBD; **empirical τ calibration is a Track B sub-spec drafting cycle deliverable per [`docs/discipline/METHODOLOGY_NOTES.md`](../discipline/METHODOLOGY_NOTES.md) §1 (empirical verification) + §4 (scale-step discipline)** — this scoping cycle is process/spec deliverable register-class and cannot produce that calibration; sub-task B-T7 is eligible-not-named per §5 #3
- Risk: too low = false-positive (legit ideas wrongly merged); too high = false-negative (near-duplicates pass)

**B-2: Within-batch vs cross-batch dedup window**
- Scope: do we compare embeddings only within the current batch, or also against recent N hypotheses from prior batches
- **Proposed default**: within-batch only for MVP
- Alternatives: sliding window (last 100 hypotheses across batches), full historical
- Sub-spec disposition: TBD; cross-batch defers to V2 unless empirical false-negatives prove problematic
- Risk: within-batch misses cross-batch repetition; cross-batch adds SQLite BLOB storage + cleanup policy

**B-3: Quarantine vs reject**
- Scope: what happens to a hypothesis flagged as near-duplicate
- **Proposed default**: quarantine — new `near_duplicate` lifecycle state; counts for budget audit; skips backtest; surfaces in batch report; Critic / human can override
- Alternatives: hard reject (treat like `DUPLICATE` lifecycle state), allow-with-warning
- Sub-spec disposition: TBD
- Risk: quarantine preserves adjudication agency at the cost of more lifecycle complexity; hard reject is simpler but irreversible

**B-4: Embed input**
- Scope: what text gets fed to the sentence-transformer for each hypothesis
- **Proposed default**: D3-canonical DSL JSON (the exact canonicalization output from `agents/hypothesis_hash.py::canonicalize_for_hash`)
- Alternatives: DSL features projection (factor names set + operator counts + max_hold_bars quantized), full DSL JSON pre-canonicalization (with name/description), motivation text only
- Sub-spec disposition: TBD
- **Risk (revised, observable-failure-mode template)**: if canonical-JSON input is wrong (schema-token weight overwhelms semantic content), embedding similarity correlates with DSL-shape rather than DSL-semantics, causing false-positives between structurally-similar but semantically-distinct strategies. **Detectable as**: cosine similarity > τ between two DSLs with disjoint factor sets but overlapping operator structure; manual review of top-K cosine pairs in B-T7 calibration corpus.

**B-5: Parameter bucketing strategy**
- Scope: should "SMA(20)" and "SMA(21)" be canonicalized to a common form before embedding (e.g., bucket parameters to nearest 5)
- **Proposed default**: none at canonicalization (keep parameters as-is); let the embedding's cosine similarity decide semantic closeness
- Alternatives: round parameters to nearest 5 / 10 / decade, snap thresholds to standard values (30, 50, 70 for RSI)
- Sub-spec disposition: TBD; bucketing risks breaking D3 hash contract — must remain CONTRACT BOUNDARY isolated per B-Lock-2 call-graph rule
- Risk: aggressive bucketing changes hash semantics → CONTRACT BOUNDARY violation

**B-6: Compound gate (cosine + structural overlap)**
- Scope: whether near-duplicate detection requires BOTH high cosine similarity AND structural overlap (same factor set, same operator counts)
- **Proposed default**: cosine-only for MVP
- Alternatives: AND-gate (cosine ≥ τ_c AND structural_overlap ≥ τ_s), OR-gate, weighted score
- Sub-spec disposition: TBD; AND-gate reduces false-positives but adds hyperparameter
- Risk: cosine-only may catch unrelated DSLs with overlapping factor mentions; AND-gate is safer but more complex

**B-7 (added Session 3 per P-F2)**: **Embedding model load-failure + version-pin policy**
- Scope: runtime behavior when `sentence-transformers` import fails, model file is missing / corrupted, or version drift produces different embeddings vs the version used at calibration
- **Proposed default**: hard-fail at orchestrator startup (refuse to begin batch if embedding stack is unhealthy); version pin via SHA in `pyproject.toml` extra + project-local model cache directory per B-Lock-7
- Alternatives: degrade-to-D3-only (silently skip semantic dedup with prominent log), warn-and-continue (degrade with retry), block batch but allow `--no-semantic-dedup` override flag
- Sub-spec disposition: TBD
- Risk: silent degradation means a batch could go through with semantic-dedup-disabled and we wouldn't know; hard-fail couples Track B health to orchestrator startup (acceptable per parking-strategy isolation, but worth surfacing)

**B-8 (added Session 3 per P-F2)**: **In-batch embedding cache cap + eviction policy**
- Scope: maximum number of embeddings retained in `BatchIngestState.embedding_cache` within a single batch before eviction or cap-enforcement
- **Proposed default**: unbounded within batch; rely on per-batch clear at finalize (per B-Lock-5) for memory bound
- Alternatives: cap at 500 / 1000 / 2000 with LRU eviction, cap at 2× batch_size with random eviction, no cap and rely on operator monitoring
- Sub-spec disposition: TBD; interacts with batch size (default 200) and cross-batch dedup decision B-2
- Risk: unbounded growth could exhaust memory at large batch sizes (e.g., 2000-hypothesis batches); but eviction creates false-negatives where evicted embeddings would have caught later near-duplicates

### §2.3 Cross-track architectural decisions (4 X-class)

**X-1: Shared BatchIngestState shape (field enumeration)**
- Scope: both tracks add (or do not add) fields to `BatchIngestState` in `agents/orchestrator/ingest.py`; coordinate to avoid conflicts
- **Proposed default (Session 3 added field enumeration per A-F6)**:
  - **Track A fields**: NONE. Bandit state lives in `factor_posterior` table; Thompson-sampled posterior is materialized into a separate `BatchBanditSelection` dataclass passed to prompt builder. The shared lock confirms Track A adds zero `BatchIngestState` fields.
  - **Track B fields**: `embedding_cache: dict[str, np.ndarray]` — per-batch, cleared at finalize per B-Lock-5. Mutable dict consistent with existing `BatchIngestState` pattern (currently `@dataclass`, not `@dataclass(frozen=True)`).
- Sub-spec drafting cycle's first deliverable locks this shape before either track's implementation begins
- Risk: out-of-order implementation creates merge conflict between tracks; mutable `embedding_cache` continues existing pattern but worth flagging if project moves toward `frozen=True` discipline

**X-2: Integration ordering in `ingest_candidate()` (with lifecycle state-machine clarification)**
- Scope: the exact pipeline order for a new hypothesis
- **Proposed default**: (1) DSL validation → (2) D3 byte-identical hash check → (3) embedding-based near-duplicate check (Track B) → (4) critic gating → (5) backtest → (6) lifecycle terminal state. Track A's bandit operates at batch close (after step 6) for all hypotheses
- **Sub-spec drafting cycle MUST decide (Session 3 added per A-F4)**:
  - (i) whether `near_duplicate` is **terminal** at batch close (joins `DUPLICATE` / `INVALID_DSL` / etc. in the terminal set) or **transient** (resolves to e.g. `DUPLICATE` post-finalize)
  - (ii) which constants tuple it joins — `D6_STAGE1_LIFECYCLE_STATES` vs the D7/D8 successor set per current main `agents/orchestrator/ingest.py`
  - (iii) whether the `assert_lifecycle_invariant_at_batch_close()` assertion in `ingest.py` is extended in-place or paralleled in a new helper to preserve the existing D6 ripgrep contract noted at `ingest.py` line 42–43
- Risk: ordering changes affect lifecycle invariant; must be locked before implementation; ripgrep contract is a separate boundary that the integration must not silently break

**X-3: Dependency surface delta**
- Scope: which dependencies enter `pyproject.toml`
- **Proposed default**: Track A adds none (pure stdlib + existing numpy / sqlite). Track B adds `sentence-transformers` under optional extra `phase2_5` per B-Lock-7 SHA-pin discipline
- Risk: dependency creep; supply-chain audit required at implementation arc review (Wave B-3 R2 security-reviewer + B-Lock-7 SHA verification)

**X-4: Test surface allocation (with required test-type enumeration)**
- Scope: where new tests live and what kinds of tests are required
- **Proposed default (location)**: Track A extends `tests/test_orchestrator_ingest.py` + `tests/test_d6_prompt_builder.py` + new `tests/test_factor_bandit.py`. Track B extends `tests/test_hypothesis_hash.py` + `tests/test_orchestrator_ingest.py` + new `tests/test_semantic_dedup.py`. Shared `tests/test_bandit_dedup_e2e.py` for integration after both implementations land
- **Required test types per track (Session 3 added per A-F7)**:
  - **Track A**: (a) leakage-regression positive (clean curation passes audit) + negative (synthetic contaminated `top_factors` triggers audit failure); (b) deterministic-seed replay (same `batch_id` → same top-K); (c) posterior-update isolation from in-batch state (mid-batch state changes do not perturb posterior); (d) `factor_bandit_observations` append-only contract test
  - **Track B**: (a) lifecycle-invariant extension parametrized (new `near_duplicate` state honored by `assert_lifecycle_invariant_at_batch_close()`); (b) `semantic_dedup.py` import-isolation ripgrep test (must not import from `agents/hypothesis_hash.py` internals beyond the public `canonicalize_for_hash` API); (c) embedding cache cleared-at-finalize; (d) cosine-threshold sweep coverage on calibration fixture
  - **Cross-track**: `BatchIngestState` field-additions match X-1 lock (test that Track A adds zero fields)
- Risk: test colocation could mix concerns; default keeps clean separation; test-type enumeration prevents implementation arc satisfying the letter while missing the discipline

---

## §3 Bar criteria + filter framework

Standard 4-criterion AND-conjunction per [`docs/discipline/METHODOLOGY_NOTES.md`](../discipline/METHODOLOGY_NOTES.md) §20.6 applies at sub-spec drafting cycle per-decision disposition:

1. **Empirical verifiability**: is there a concrete test or measurement that distinguishes "this default is correct" from "this default is wrong" — per-decision "Risk" lines should follow observable-failure-mode template (see A-4 / A-5 / B-4 as exemplars)
2. **Sealed-class boundary respect**: does this default preserve all existing HARD CONSTRAINTS and proposed §4 discipline locks
3. **Reviewer-routing convergence**: do both Session 2 reviewers (or future sub-spec reviewers) agree on the disposition, or is there explicit per-fix adjudication
4. **Anti-momentum-binding**: does this default avoid pre-committing to alternatives at downstream cycles

Filter buckets per per-fix adjudication ([`feedback_reviewer_suggestion_adjudication.md`](../../.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_reviewer_suggestion_adjudication.md)):

- **ADOPT**: passes all 4 criteria; merge as-stated
- **ADOPT-LIGHT**: passes with light reworking (typically wording); merge after minor edit
- **DEFER**: out of this cycle's scope; explicitly marked for sub-spec or implementation cycle
- **PUSHBACK**: reviewer's framing is wrong; explain rationale in commit / adjudication note
- **PASS**: reviewer's finding doesn't apply (e.g., based on stale assumption)

---

## §4 Discipline locks proposed for HARD CONSTRAINTS addition at merge time (14)

These are NOT added to CLAUDE.md HARD CONSTRAINTS at scoping SEAL — they are PROPOSED additions, to be merged into CLAUDE.md atomically with the eventual merge of `phase2.5/bandit-dedup` to main per pre-merge verification checklist item 4. Until merge, they govern the parked-branch implementation arc's design space.

### Track A discipline locks (7)

- **A-Lock-1**: NEVER pass `factor_posterior.alpha` or `factor_posterior.beta` values into any Proposer or Critic LLM context (orchestrator-internal only)
- **A-Lock-2**: NEVER expose factor pass-rate counts, regime-pass counts, or any per-factor metric in any LLM-visible artifact (prompt, example, motivation, batch summary excerpt)
- **A-Lock-3**: NEVER curate the menu using validation (2024), test (2025), or regime-holdout (2022) per-hypothesis numeric metrics — only the binary `regime_holdout_passed` boolean from the registry
- **A-Lock-4**: NEVER let `audit_prompt_for_leakage()` skip the `top_factors_block` scoped scan for the extended forbidden-language list (regime / holdout / pass / fail / score / quality / signal / performance). **Sub-spec note (Session 3 added per A-F1)**: sub-spec drafting cycle MUST decide whether `top_factors_block` becomes a separately addressable `ProposerPrompt` field (preferred for surface isolation) or remains inlined in the `user` segment with a scoped substring scan; either choice MUST preserve `ProposerPrompt.all_text()` as the canonical concatenation the audit reads.
- **A-Lock-5**: NEVER decay or rewrite bandit observations retroactively — the `factor_bandit_observations` ledger is append-only
- **A-Lock-6**: NEVER update bandit posterior mid-batch — only at batch close after `assert_lifecycle_invariant_at_batch_close()` passes
- **A-Lock-7 (added Session 3 per A-F2)**: NEVER write factor posterior values, regime-pass counts, top-K curation rank, or any per-factor metric to **non-prompt LLM-visible surfaces**: (i) batch summary exports / leaderboards / `batch_report.py` output; (ii) commit messages or Phase Marker history; (iii) error logs that may flow into future prompt context; (iv) `HypothesisRecord.provenance` dict that propagates to downstream LLM-context-assembly paths. Bandit posterior lives only in the `factor_posterior` table and the structured orchestrator-internal log.

### Track B discipline locks (7)

- **B-Lock-1**: NEVER merge embedding-based dedup into D3 byte-identical canonicalization — separate code paths preserve the D2/D3 CONTRACT BOUNDARY
- **B-Lock-2**: NEVER change D2 manifest canonicalization or D3 hash canonicalization to accommodate embedding-friendly representation — bucketing (if any) lives in the embedding layer, not in canonicalization. **Call-graph rule (Session 3 added per A-F3)**: specifically, if B-5 parameter bucketing is adopted at sub-spec, the bucketing transform MUST be implemented in `agents/orchestrator/semantic_dedup.py` and MUST construct its input string by traversing the `StrategyDSL` object directly — it MUST NOT call `canonicalize_for_hash()` and post-process the result, and it MUST NOT introduce a shared helper between `hypothesis_hash.py` and `semantic_dedup.py`.
- **B-Lock-3**: NEVER count `near_duplicate` against the budget pre-charge — `near_duplicate` is a post-hash, post-charge classification; budget is already pre-charged at the API call boundary
- **B-Lock-4**: NEVER write embedding vectors to LLM-visible artifacts — embeddings are orchestrator-internal
- **B-Lock-5**: NEVER cache embeddings across batches in MVP — `BatchIngestState.embedding_cache` is per-batch and cleared at finalize (cross-batch dedup is V2 work, requires separate Charlie register-event)
- **B-Lock-6**: NEVER use a remote embedding API — sentence-transformers must remain local CPU; no new network egress surface; supply-chain audit verifies at Wave B-3 R2
- **B-Lock-7 (added Session 3 per A-F5)**: `sentence-transformers` model + tokenizer artifacts MUST be SHA-pinned in `pyproject.toml` extras AND mirrored to a project-local cache directory. Embedding determinism across CPU architectures MUST be verified at sub-spec calibration sub-task B-T7. Network egress for model download is permitted at install-time only; runtime embedding MUST NOT touch the network.

---

## §5 Eligible-not-named successor cycles

Per anti-pre-emption invariant (§6), this scoping cycle does NOT authorize any successor cycle. The following are eligible-not-named (requires separate Charlie register-event boundary at each entry):

1. **Sub-spec drafting cycle entry** — combined (α) or per-track-split (β); per §1.5 default-recommended posture is (α), not pre-authorized
2. **Implementation arc entry** — Wave A-1 + Wave B-1 parallel; preceded by shared `BatchIngestState` lock per X-1
3. **Empirical calibration sub-task B-T7** — eligible as either (a) a sub-task within the Track B sub-spec drafting cycle, or (b) a standalone successor cycle. The (a/b) decision is itself a sub-spec drafting cycle scoping question and is NOT pre-authorized here (Session 3 reframed per A-F8 + P-F6).
4. **Arc-level closeout SEAL** — after both implementation arcs complete; separate per-track or combined SEAL decision is open
5. **Pre-merge verification entry** — 10-item checklist per [`docs/parked/PARKED_BRANCHES.md`](../parked/PARKED_BRANCHES.md)
6. **Merge to main register-event** — after verification clean; atomic Phase Marker advance + CLAUDE.md HARD CONSTRAINT additions per §4
7. **Post-merge tag** — e.g., `phase2.5-bandit-v1` + `phase2.5-dedup-v1`, separate or combined; tag scheme open
8. **V2 successor work** — cross-batch dedup window, multi-axis bandit signals, decay policy — all eligible

---

## §6 Anti-pre-emption invariant

This scoping cycle's authorization scope is narrow. Specifically, this scoping cycle SEAL does **NOT**:

**Framing note (Session 3 added per P-F7)**: items 1–3 + 7 below are *cycle-entry non-authorizations* (negations of §5 successor cycle entries — anti-momentum-binding for cycle entry register-event boundaries). Items 4–6 + 8 are *decision-class non-authorizations* (additional discipline beyond §5 — reserved decisions that this scoping cycle does not pre-commit). Path 3 §7 distinguishes these two classes; this framing preserves that distinction.

- Pre-authorize sub-spec drafting cycle entry — separate Charlie register-event required *(cycle-entry)*
- Pre-authorize implementation arc entry — separate Charlie register-event required after sub-spec SEAL *(cycle-entry)*
- Pre-authorize merge to main — separate Charlie register-event + pre-merge verification clean required *(cycle-entry)*
- Pre-commit any proposed default in §2 as "final" — sub-spec drafting cycle re-adjudicates per-decision with bar criteria §3 *(decision-class)*
- Pre-authorize subagent dispatch for code writing — implementation arc cycle scope only *(decision-class)*
- Modify CLAUDE.md HARD CONSTRAINTS on main — deferred to merge atomic update *(decision-class)*
- Push the parked branch to remote — separate user authorization required *(cycle-entry)*
- Authorize pulling validation / test / 2022-regime data into any LLM context at any cycle stage — HARD CONSTRAINT §"AI Agent & Prompt Integrity" remains in force *(decision-class — invariant; not subject to sub-spec re-adjudication)*

Each successor register-event boundary stands on its own authorization per [`feedback_authorization_routing.md`](../../.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_authorization_routing.md) hard rule.

---

## §7 V# self-checklist (15 anchors)

Evaluated at pre-SEAL register at Session 3. SEAL fire requires all 15 CLEAN.

- **V1**: Cycle scope precisely defined (§1.1 IS / §1.2 IS NOT)
- **V2**: Track A 11 open decisions enumerated with proposed default + alternatives + risk + sub-spec disposition placeholder (§2.1 A-1..A-11)
- **V3**: Track B 8 open decisions enumerated with proposed default + alternatives + risk + sub-spec disposition placeholder (§2.2 B-1..B-8)
- **V4**: Cross-track architectural decisions enumerated (§2.3, 4 X-class, with field enumeration + lifecycle state-machine note + test-type enumeration added per Session 3 adjudication)
- **V5**: Bar criteria 4-criterion AND-conjunction stated; filter buckets defined (§3); observable-failure-mode template referenced for criterion #1 with A-4 / A-5 / B-4 as exemplars
- **V6**: 14 discipline locks enumerated, 7 per track (§4, including A-Lock-7 non-prompt leakage + B-Lock-7 SHA-pin added at Session 3)
- **V7**: Eligible-not-named successor cycles enumerated, 8 items (§5, with B-T7 reframed)
- **V8**: Anti-pre-emption invariant stated, 8 non-pre-authorizations across cycle-entry + decision-class framing (§6)
- **V9**: Reviewer routing plan for Session 2 specified (2 parallel internal Claude Code subagents — architect + planner per Charlie 2026-05-16; Codex SKIPPED at process/spec deliverable register-class); both reviewers fired at Session 2 and returned (architect 8 findings + planner 8 findings)
- **V10**: Per-fix adjudication discipline (no bulk-accept) executed at Session 3; 15 dispositions across 16 findings (1 merged): 8 ADOPT + 6 ADOPT-LIGHT + 1 PUSHBACK + 0 DEFER + 0 PASS
- **V11**: HARD CONSTRAINT additions deferred to merge time (NOT applied at scoping SEAL) per §4 framing
- **V12**: Phase placement reaffirmed — parked branch, no Phase Marker advance until merge per §1.4 + parked-branch registration design; main remains at `15f2108` view
- **V13**: Activation trigger reaffirmed at §1.4 — pre-merge verification checklist applies at merge time
- **V14 (added Session 3 per P-F4)**: Discipline-lock-vs-proposed-default coherence check — no §2 proposed default conflicts with any §4 discipline lock. Specifically verified at SEAL: A-3 K=5 ≤ |factors| compatible with A-Lock-2 no-per-factor-metric; B-1 τ=0.82 compatible with B-Lock-3 no-near_duplicate-pre-charge; A-Lock-5 append-only + A-4 no-decay are mutually consistent (no decay reads observations; append-only forbids retroactive write — both compatible); B-Lock-5 within-batch-only + B-8 in-batch-cache-cap are consistent (cap is within-batch).
- **V15 (added Session 3 per P-F4)**: Authorization-source citation accuracy — the Charlie register quote "for session 2 we launch 2 separate agents for review independently, and adjudicate and integrate their findings" appears in the user message immediately preceding Session 1 commit `97f7774`; Option-1 authorization quote "option 1, and for re-run Phase 2C-style evaluation against the same artifacts concern, let's only develop this on its own git branch for now..." precedes parked-branch registration commit `15f2108`. Both authorization-source citations are accurate.

---

## §8 Push / tagging / Phase Marker discipline at scoping cycle SEAL

- **NO tag** at this scoping cycle SEAL per process/spec deliverable register-class precedent (Path 3 scoping cycle SEAL `6750274`, Phase 5 entry scoping cycle SEAL `697c26b`, PHASE2C_10-15 + Phase 4 reassessment closeout)
- **NO push to remote** at this scoping cycle SEAL — parked branch stays local until activation or explicit user authorization
- **NO Phase Marker advance on main** at this scoping cycle SEAL — main's Phase Marker is frozen at Path 3 scoping cycle SEAL state (`578df13`); the parked-branch's internal cycle progression is recorded in this doc + branch git history, not in main's CLAUDE.md
- **Session 3 SEAL commit** lands on `phase2.5/bandit-dedup` only; the branch has two commits at this scoping cycle SEAL:
  - Commit 1 `97f7774`: Session 1 draft of scoping decision doc
  - Commit 2 (this commit): Session 3 SEAL — adjudicated + V# CLEAN final version (15 dispositions applied; 23 decisions / 14 locks / 15 V# anchors)
- At eventual merge time, atomic Phase Marker advance + history file update happens per [`feedback_claude_md_freshness.md`](../../.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_claude_md_freshness.md) Option 1A binding

---

## Appendix A — review routing for Session 2

Per Charlie register-event boundary 2026-05-16: "for session 2 we launch 2 separate agents for review independently, and adjudicate and integrate their findings."

**Reviewer 1 — `architect` subagent**: full architectural critique of integration points, leakage surfaces, CONTRACT BOUNDARY integrity, dependency surface, lifecycle state machine impact. Read scoping doc + CLAUDE.md HARD CONSTRAINTS + relevant code files (`prompt_builder.py`, `ingest.py`, `hypothesis_hash.py`, `d7a_feature_extraction.py`). Returned 8 findings (2 high LEAKAGE, 1 medium BOUNDARY, 1 high STRUCTURAL, 1 medium DEPENDENCY, 1 medium STRUCTURAL, 1 medium TESTING, 1 low DISCIPLINE).

**Reviewer 2 — `planner` subagent**: full plan critique of decision enumeration completeness, dependency graph, risk identification, V# self-check coverage, anti-pre-emption tightness, eligible-not-named completeness, bar criteria applicability. Read scoping doc + Path 3 precedent + Phase 5 entry precedent + METHODOLOGY_NOTES §20.6 + CLAUDE.md + PARKED_BRANCHES.md. Returned 8 findings (2 high COMPLETENESS, 1 medium RISK, 1 medium V#, 1 medium STRUCTURE, 1 high METHODOLOGY, 1 low AUTHORIZATION, 1 low CITATION).

Each reviewer reported independently — no shared context across subagent calls — maximizing independence per the dual-reviewer routing discipline. Per-fix adjudication thereafter; ADOPT / ADOPT-LIGHT / DEFER / PUSHBACK / PASS bucket per finding.

**Codex SKIPPED** per process/spec deliverable register-class hard rule ([`feedback_codex_review_scope.md`](../../.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_codex_review_scope.md)). **python-reviewer + security-reviewer SKIPPED** at scoping cycle (no code; both apply at implementation arc review Waves A-3 / B-3).

---

## Appendix B — Session 3 adjudication dispositions table (15 dispositions on 16 findings; F8+P-F6 merged)

| # | Source | Severity | Disposition | Action applied |
|---|---|---|---|---|
| 1 | A-F1 | high | ADOPT-LIGHT | Sub-spec field-split note added to A-Lock-4 |
| 2 | A-F2 | high | ADOPT | A-Lock-7 added (non-prompt leakage surfaces: batch summaries, commit msgs, error logs, `HypothesisRecord.provenance`) |
| 3 | A-F3 | medium | ADOPT | Bucketing call-graph rule added to B-Lock-2 |
| 4 | A-F4 | high | ADOPT-LIGHT | Lifecycle-state decision note added to X-2 (terminal vs transient; tuple naming; assertion extension) |
| 5 | A-F5 | medium | ADOPT | B-Lock-7 added (SHA pin + determinism verification + no runtime network) |
| 6 | A-F6 | medium | ADOPT | Field enumeration added to X-1 (Track A: zero fields; Track B: `embedding_cache`) |
| 7 | A-F7 | medium | ADOPT | Test-type enumeration added to X-4 (leakage-regression, deterministic-seed, lifecycle-invariant, import-isolation) |
| 8 | A-F8 + P-F6 | high (merged) | ADOPT | "required before SEAL" struck from B-1; reframed in §5 #3 as (a) sub-task within Track B sub-spec cycle vs (b) standalone successor (sub-spec adjudicates) |
| 9 | P-F1 | high | ADOPT | A-9 (observation schema), A-10 (extract_factors error path), A-11 (batch-summary visibility scope) added to §2.1 |
| 10 | P-F2 | high | ADOPT | B-7 (model load-failure policy), B-8 (in-batch cache cap) added to §2.2 |
| 11 | P-F3 | medium | ADOPT-LIGHT | A-4 / A-5 / B-4 Risk lines reworked to observable-failure-mode template ("Detectable as: ...") |
| 12 | P-F4 | medium | ADOPT | V14 (lock-vs-default coherence check) + V15 (authorization-citation accuracy) added to §7 |
| 13 | P-F5 | medium | ADOPT | §1.5 added (sub-spec cycle decomposition open question; default-recommended posture α stated, not pre-authorized) |
| 14 | P-F7 | low | ADOPT-LIGHT | §6 framing note added distinguishing cycle-entry non-authorizations from decision-class non-authorizations |
| 15 | P-F8 | low | **PUSHBACK** | Worktree-relative memory-file path convention is consistent with Path 3 precedent and established project convention; not a per-cycle issue. If problematic in practice, raise as a Path 3 errata register-event at separate Charlie register-event boundary. |

**ADOPT-LIGHT framing pattern**: all 6 ADOPT-LIGHT dispositions take the form of *sub-spec deferral notes inline in the relevant §2 decision or §4 lock* — they do not pre-commit the sub-spec choice; they surface that a sub-spec choice is required at the location where it will be made.

**Reviewer convergence**: architect F8 (B-T7 ambiguity) and planner F6 (B-T7 register-class confusion) addressed the same underlying issue at different severities; merged into one disposition (#8 above) at high severity per the more conservative reading.

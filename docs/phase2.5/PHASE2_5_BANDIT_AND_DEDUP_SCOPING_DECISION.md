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

- **Session 1**: scoping decision doc draft (this commit's deliverable; 14 + 4 = 18 design candidates enumerated + 12 discipline locks proposed + bar criteria framework defined + 13 V# anchors)
- **Session 2**: parallel reviewer routing — 2 internal Claude Code subagents fired independently (architect + planner per Charlie's specification 2026-05-16), per-fix adjudication thereafter (no bulk-accept per [`feedback_reviewer_suggestion_adjudication.md`](../../.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_reviewer_suggestion_adjudication.md))
- **Session 3**: apply adjudicated edits + V# self-check at pre-SEAL register + SEAL fire commit on parked branch

### §1.4 Activation trigger reaffirmation

Parked branch `phase2.5/bandit-dedup` activates when Charlie register-event boundary establishes active batch cadence resumption. Until then: no merge, no remote push (unless explicit user authorization). Pre-merge verification 10-item checklist per [`docs/parked/PARKED_BRANCHES.md`](../parked/PARKED_BRANCHES.md) applies at merge time.

---

## §2 Candidate enumeration

### §2.1 Track A — Factor Bandit (8 open decisions, A-1..A-8)

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
- Risk: stale priors when market regime shifts; but decay introduces hyperparameter

**A-5: Thompson sampling seed / reproducibility**
- Scope: determinism of the sampling for replay / debugging
- **Proposed default**: `hash(batch_id)` deterministic seed; same batch_id → same top-K factors
- Alternatives: fresh RNG per batch (non-reproducible), session-level seed, no determinism guarantee
- Sub-spec disposition: TBD; affects test pattern shape
- Risk: deterministic seed means same hypothesis sample paths if re-run — desirable for reproducibility

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
- Sub-spec disposition: TBD; subject to leakage-audit extension (see §4 Lock A-Lock-4)
- Risk: any phrasing that hints at "why" leaks regime info; default is most neutral

**A-8: Per-batch vs per-call curation cadence**
- Scope: does the top-K menu update mid-batch (per Proposer call) or only between batches
- **Proposed default**: per-batch (frozen for batch duration; sampled once at batch open)
- Alternatives: per-call (re-sample per Proposer API call within batch), hybrid
- Sub-spec disposition: TBD
- Risk: per-call introduces in-batch variability that's hard to audit; per-batch is cleaner

### §2.2 Track B — Semantic Dedup (6 open decisions, B-1..B-6)

Architectural sketch locked at scoping (subject to sub-spec refinement): new module `agents/orchestrator/semantic_dedup.py` (NOT inside `agents/hypothesis_hash.py` — preserves D2/D3 CONTRACT BOUNDARY). Pipeline: D3 byte-identical hash check first → if pass, run embedding similarity vs in-batch cache → if cosine ≥ τ, route to new lifecycle state `near_duplicate`. New lifecycle state `near_duplicate` added to [`agents/orchestrator/ingest.py`](../../agents/orchestrator/ingest.py) state machine. Counts toward `hypotheses_attempted` (DSR denominator) like `DUPLICATE`. Skips backtest. Embedding model: `sentence-transformers` `all-MiniLM-L6-v2` local CPU (~60 MB model, ~50–200 ms per embedding, $0 API cost). Added to `pyproject.toml` under optional extra `phase2_5 = ["sentence-transformers>=2.0.0"]`.

**B-1: Cosine similarity threshold τ**
- Scope: cutoff above which two embeddings are treated as near-duplicates
- **Proposed default**: τ = 0.82 starting point; calibrate via parameterized sweep over fixture corpus + Phase 2C Stage 1 batch DSL pairs
- Alternatives: 0.70 / 0.75 / 0.80 / 0.85 / 0.88 / 0.90 (sweep)
- Sub-spec disposition: TBD; **empirical calibration sub-task (B-T7) required before SEAL** per [`docs/discipline/METHODOLOGY_NOTES.md`](../discipline/METHODOLOGY_NOTES.md) §1 empirical verification
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
- Risk: canonical JSON preserves structure but may overweight schema noise; projection loses operator nuance

**B-5: Parameter bucketing strategy**
- Scope: should "SMA(20)" and "SMA(21)" be canonicalized to a common form before embedding (e.g., bucket parameters to nearest 5)
- **Proposed default**: none at canonicalization (keep parameters as-is); let the embedding's cosine similarity decide semantic closeness
- Alternatives: round parameters to nearest 5 / 10 / decade, snap thresholds to standard values (30, 50, 70 for RSI)
- Sub-spec disposition: TBD; bucketing risks breaking D3 hash contract — must remain CONTRACT BOUNDARY isolated
- Risk: aggressive bucketing changes hash semantics → CONTRACT BOUNDARY violation

**B-6: Compound gate (cosine + structural overlap)**
- Scope: whether near-duplicate detection requires BOTH high cosine similarity AND structural overlap (same factor set, same operator counts)
- **Proposed default**: cosine-only for MVP
- Alternatives: AND-gate (cosine ≥ τ_c AND structural_overlap ≥ τ_s), OR-gate, weighted score
- Sub-spec disposition: TBD; AND-gate reduces false-positives but adds hyperparameter
- Risk: cosine-only may catch unrelated DSLs with overlapping factor mentions; AND-gate is safer but more complex

### §2.3 Cross-track architectural decisions (4 X-class)

**X-1: Shared BatchIngestState shape**
- Scope: both tracks add fields to `BatchIngestState` in `agents/orchestrator/ingest.py`; coordinate to avoid conflicts
- **Proposed default**: sub-spec drafting cycle's first deliverable locks the shared dataclass shape before either track's implementation begins
- Risk: out-of-order implementation creates merge conflict between tracks

**X-2: Integration ordering in `ingest_candidate()`**
- Scope: the exact pipeline order for a new hypothesis
- **Proposed default**: (1) DSL validation → (2) D3 byte-identical hash check → (3) embedding-based near-duplicate check (Track B) → (4) critic gating → (5) backtest → (6) lifecycle terminal state. Track A's bandit operates at batch close (after step 6) for all hypotheses
- Risk: ordering changes affect lifecycle invariant; must be locked before implementation

**X-3: Dependency surface delta**
- Scope: which dependencies enter `pyproject.toml`
- **Proposed default**: Track A adds none (pure stdlib + existing numpy / sqlite). Track B adds `sentence-transformers` under optional extra `phase2_5`
- Risk: dependency creep; supply-chain audit required at implementation arc review (Wave B-3 R2 security-reviewer)

**X-4: Test surface allocation**
- Scope: where new tests live
- **Proposed default**: Track A extends `tests/test_orchestrator_ingest.py` + `tests/test_d6_prompt_builder.py` + new `tests/test_factor_bandit.py`. Track B extends `tests/test_hypothesis_hash.py` + `tests/test_orchestrator_ingest.py` + new `tests/test_semantic_dedup.py`. Shared `tests/test_bandit_dedup_e2e.py` for integration after both implementations land
- Risk: test colocation could mix concerns; default keeps clean separation

---

## §3 Bar criteria + filter framework

Standard 4-criterion AND-conjunction per [`docs/discipline/METHODOLOGY_NOTES.md`](../discipline/METHODOLOGY_NOTES.md) §20.6 applies at sub-spec drafting cycle per-decision disposition:

1. **Empirical verifiability**: is there a concrete test or measurement that distinguishes "this default is correct" from "this default is wrong"
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

## §4 Discipline locks proposed for HARD CONSTRAINTS addition at merge time (12)

These are NOT added to CLAUDE.md HARD CONSTRAINTS at scoping SEAL — they are PROPOSED additions, to be merged into CLAUDE.md atomically with the eventual merge of `phase2.5/bandit-dedup` to main per pre-merge verification checklist item 4. Until merge, they govern the parked-branch implementation arc's design space.

### Track A discipline locks (6)

- **A-Lock-1**: NEVER pass `factor_posterior.alpha` or `factor_posterior.beta` values into any Proposer or Critic LLM context (orchestrator-internal only)
- **A-Lock-2**: NEVER expose factor pass-rate counts, regime-pass counts, or any per-factor metric in any LLM-visible artifact (prompt, example, motivation, batch summary excerpt)
- **A-Lock-3**: NEVER curate the menu using validation (2024), test (2025), or regime-holdout (2022) per-hypothesis numeric metrics — only the binary `regime_holdout_passed` boolean from the registry
- **A-Lock-4**: NEVER let `audit_prompt_for_leakage()` skip the `top_factors_block` scoped scan for the extended forbidden-language list (regime / holdout / pass / fail / score / quality / signal / performance)
- **A-Lock-5**: NEVER decay or rewrite bandit observations retroactively — the `factor_bandit_observations` ledger is append-only
- **A-Lock-6**: NEVER update bandit posterior mid-batch — only at batch close after `assert_lifecycle_invariant_at_batch_close()` passes

### Track B discipline locks (6)

- **B-Lock-1**: NEVER merge embedding-based dedup into D3 byte-identical canonicalization — separate code paths preserve the D2/D3 CONTRACT BOUNDARY
- **B-Lock-2**: NEVER change D2 manifest canonicalization or D3 hash canonicalization to accommodate embedding-friendly representation — bucketing (if any) lives in the embedding layer, not in canonicalization
- **B-Lock-3**: NEVER count `near_duplicate` against the budget pre-charge — `near_duplicate` is a post-hash, post-charge classification; budget is already pre-charged at the API call boundary
- **B-Lock-4**: NEVER write embedding vectors to LLM-visible artifacts — embeddings are orchestrator-internal
- **B-Lock-5**: NEVER cache embeddings across batches in MVP — `BatchIngestState.embedding_cache` is per-batch and cleared at finalize (cross-batch dedup is V2 work, requires separate Charlie register-event)
- **B-Lock-6**: NEVER use a remote embedding API — sentence-transformers must remain local CPU; no new network egress surface; supply-chain audit verifies at Wave B-3 R2

---

## §5 Eligible-not-named successor cycles

Per anti-pre-emption invariant (§6), this scoping cycle does NOT authorize any successor cycle. The following are eligible-not-named (requires separate Charlie register-event boundary at each entry):

1. **Sub-spec drafting cycle entry** (combined Track A + Track B, or per-track split — sub-spec cycle entry decision itself is open)
2. **Implementation arc entry** (Wave A-1 + Wave B-1 parallel; preceded by shared `BatchIngestState` lock per X-1)
3. **Empirical calibration sub-task entry** (B-T7 — required before Track B sub-spec disposition of B-1 τ)
4. **Arc-level closeout SEAL** (after both implementation arcs complete; separate per-track or combined SEAL decision is open)
5. **Pre-merge verification entry** (10-item checklist per [`docs/parked/PARKED_BRANCHES.md`](../parked/PARKED_BRANCHES.md))
6. **Merge to main register-event** (after verification clean; atomic Phase Marker advance + CLAUDE.md HARD CONSTRAINT additions per §4)
7. **Post-merge tag** (e.g., `phase2.5-bandit-v1` + `phase2.5-dedup-v1`, separate or combined; tag scheme open)
8. **V2 successor work** (cross-batch dedup window, multi-axis bandit signals, decay policy — all eligible)

---

## §6 Anti-pre-emption invariant

This scoping cycle's authorization scope is narrow. Specifically, this scoping cycle SEAL does **NOT**:

- Pre-authorize sub-spec drafting cycle entry (separate Charlie register-event required)
- Pre-authorize implementation arc entry (separate Charlie register-event required after sub-spec SEAL)
- Pre-authorize merge to main (separate Charlie register-event + pre-merge verification clean required)
- Pre-commit any proposed default in §2 as "final" (sub-spec drafting cycle re-adjudicates per-decision with bar criteria §3)
- Pre-authorize subagent dispatch for code writing (implementation arc cycle scope only)
- Modify CLAUDE.md HARD CONSTRAINTS on main (deferred to merge atomic update)
- Push the parked branch to remote (separate user authorization required)
- Authorize pulling validation / test / 2022-regime data into any LLM context at any cycle stage — HARD CONSTRAINT §"AI Agent & Prompt Integrity" remains in force

Each successor register-event boundary stands on its own authorization per [`feedback_authorization_routing.md`](../../.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_authorization_routing.md) hard rule.

---

## §7 V# self-checklist (13 anchors)

To be evaluated at pre-SEAL register at Session 3. SEAL fire requires all 13 CLEAN.

- **V1**: Cycle scope precisely defined (§1.1 IS / §1.2 IS NOT)
- **V2**: Track A 8 open decisions enumerated with proposed default + alternatives + risk + sub-spec disposition placeholder (§2.1)
- **V3**: Track B 6 open decisions enumerated with proposed default + alternatives + risk + sub-spec disposition placeholder (§2.2)
- **V4**: Cross-track architectural decisions enumerated (§2.3, 4 X-class)
- **V5**: Bar criteria 4-criterion AND-conjunction stated; filter buckets defined (§3)
- **V6**: 12 discipline locks enumerated, 6 per track (§4)
- **V7**: Eligible-not-named successor cycles enumerated, 8 items (§5)
- **V8**: Anti-pre-emption invariant stated, 8 explicit non-pre-authorizations (§6)
- **V9**: Reviewer routing plan for Session 2 specified (2 parallel internal Claude Code subagents — architect + planner per Charlie 2026-05-16; Codex SKIPPED at process/spec deliverable register-class)
- **V10**: Per-fix adjudication discipline (no bulk-accept) referenced at §3 + Session 3 plan
- **V11**: HARD CONSTRAINT additions deferred to merge time (NOT applied at scoping SEAL) per §4 framing
- **V12**: Phase placement reaffirmed — parked branch, no Phase Marker advance until merge per §1.4 + parked-branch registration design
- **V13**: Activation trigger reaffirmed at §1.4 — pre-merge verification checklist applies at merge time

---

## §8 Push / tagging / Phase Marker discipline at scoping cycle SEAL

- **NO tag** at this scoping cycle SEAL per process/spec deliverable register-class precedent (Path 3 scoping cycle SEAL `6750274`, Phase 5 entry scoping cycle SEAL `697c26b`, PHASE2C_10-15 + Phase 4 reassessment closeout)
- **NO push to remote** at this scoping cycle SEAL — parked branch stays local until activation or explicit user authorization
- **NO Phase Marker advance on main** at this scoping cycle SEAL — main's Phase Marker is frozen at Path 3 scoping cycle SEAL state (`578df13`); the parked-branch's internal cycle progression is recorded in this doc + branch git history, not in main's CLAUDE.md
- **Session 3 SEAL commit** lands on `phase2.5/bandit-dedup` only; commits build a forward chain on the branch:
  - Commit 1 (this commit): Session 1 draft of scoping decision doc
  - Commit 2 (Session 3 SEAL): adjudicated + V# CLEAN final version of scoping decision doc
- At eventual merge time, atomic Phase Marker advance + history file update happens per [`feedback_claude_md_freshness.md`](../../.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_claude_md_freshness.md) Option 1A binding

---

## Appendix: review routing for Session 2

Per Charlie register-event boundary 2026-05-16: "for session 2 we launch 2 separate agents for review independently, and adjudicate and integrate their findings."

**Reviewer 1 — `architect` subagent**: full architectural critique of integration points, leakage surfaces, CONTRACT BOUNDARY integrity, dependency surface, lifecycle state machine impact. Reads scoping doc + CLAUDE.md HARD CONSTRAINTS + relevant code files (`prompt_builder.py`, `ingest.py`, `hypothesis_hash.py`, `d7a_feature_extraction.py`).

**Reviewer 2 — `planner` subagent**: full plan critique of decision enumeration completeness, dependency graph, risk identification, V# self-check anchors coverage, anti-pre-emption invariant tightness, eligible-not-named successor enumeration completeness, bar criteria framework applicability.

Each reviewer reports independently — no shared context across subagent calls — to maximize independence per the dual-reviewer routing discipline. Per-fix adjudication thereafter; ADOPT / ADOPT-LIGHT / DEFER / PUSHBACK / PASS bucket per finding.

**Codex SKIPPED** per process/spec deliverable register-class hard rule ([`feedback_codex_review_scope.md`](../../.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_codex_review_scope.md)). **python-reviewer + security-reviewer SKIPPED** at scoping cycle (no code; both apply at implementation arc review wave A-3 / B-3).

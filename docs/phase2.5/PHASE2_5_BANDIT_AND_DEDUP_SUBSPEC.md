# Phase 2.5 — Combined Bandit + Dedup Sub-Spec Drafting

**Cycle classification**: process/spec deliverable register-class (NOT substantive empirical research; B-T7 empirical calibration sub-task is registered as a separate eligible-not-named sub-task per §6 below). Combined (α) posture per scoping decision §1.5 default-recommended.

**Cycle authorization**: Charlie register-event boundary at "authorized" reply 2026-05-16 (post-scoping-SEAL `f63b316`). Entry authorization only at the time of this Session 1 draft commit; Sessions 2 + 3 require separate Charlie register-event boundaries per scoping decision §6.

**Base**: parked branch `phase2.5/bandit-dedup` at `f63b316` (combined scoping cycle SEAL).

**Predecessor**: [`docs/phase2.5/PHASE2_5_BANDIT_AND_DEDUP_SCOPING_DECISION.md`](PHASE2_5_BANDIT_AND_DEDUP_SCOPING_DECISION.md) — 23 design candidates / 14 discipline locks / 15 V# anchors.

**Cycle scope deliverable**: per-decision adjudication (one default per of 23 decisions) + shared `BatchIngestState` shape lock + resolution of 2 ADOPT-LIGHT sub-spec choices inherited from scoping (A-Lock-4 field-split + B-T7 placement) + lifecycle-state-machine concrete decisions (X-2 (i)/(ii)/(iii)) + implementation arc Wave preview (NOT implementation itself).

---

## §1 Shared `BatchIngestState` shape lock (X-1 first deliverable)

Per scoping X-1, the sub-spec's first deliverable locks the shared dataclass shape before either implementation arc begins. **Adjudicated default per Session 1**:

```python
# agents/orchestrator/ingest.py — post-merge target shape
@dataclass  # NOT frozen=True; existing project pattern for BatchIngestState
class BatchIngestState:
    batch_id: str
    seen_hashes: set[str]
    # ... (existing fields preserved verbatim from current main) ...
    embedding_cache: dict[str, "np.ndarray"]  # NEW for Track B; cleared at finalize per B-Lock-5
    # NO Track A fields — bandit state lives in `factor_posterior` table
```

**Lock rationale**:
- Track A adds **zero** `BatchIngestState` fields. Posterior state lives in `factor_posterior` table; Thompson-sampled selection is materialized into a separate `BatchBanditSelection` dataclass (defined in `agents/orchestrator/factor_bandit.py`) passed into `build_prompt()`. Confirmed via `BatchIngestState` field-additions test (X-4 cross-track) which asserts Track A field-count delta = 0.
- Track B adds **one** field: `embedding_cache: dict[str, np.ndarray]`. Mutable dict matches existing `BatchIngestState` mutability pattern. Cleared at `finalize_batch()` per B-Lock-5.

**Implementation order constraint**: this dataclass shape MUST be merged to the parked branch (NOT main) as the first commit of the implementation arc, before either Wave A-1 or Wave B-1 fires. This ensures both Wave A-1 and Wave B-1 test fixtures share a stable dataclass surface.

**Test contract (per X-4 cross-track)**:
```python
def test_batchingeststate_field_count_track_a_zero_delta():
    """Track A implementation must add zero fields to BatchIngestState."""
    expected_pre_track_a = {<existing fields>, "embedding_cache"}  # post-Track-B
    actual = {f.name for f in fields(BatchIngestState)}
    assert actual == expected_pre_track_a, f"Track A added fields: {actual - expected_pre_track_a}"
```

---

## §2 Lifecycle state machine extension (X-2 (i)/(ii)/(iii) adjudication)

Per scoping X-2, sub-spec MUST decide three sub-questions. **Adjudicated defaults per Session 1**:

**X-2 (i): `near_duplicate` is TERMINAL at batch close.**
- Rationale: matches `DUPLICATE` semantics (already terminal); avoids state-machine complexity of transient → terminal resolution; Critic / human override is performed by re-submission with mutation (a new hypothesis), not by mutating the existing record's state
- Alternative considered: transient with post-finalize resolution to `DUPLICATE` — REJECTED for state-machine complexity and ambiguity around DSR denominator counting timing

**X-2 (ii): `near_duplicate` joins the current main's D7/D8 successor lifecycle constants tuple.**
- Specifically: joins the same tuple that `DUPLICATE`, `INVALID_DSL`, `REJECTED_COMPLEXITY`, `BACKEND_EMPTY_OUTPUT` belong to in `agents/orchestrator/ingest.py` (as of `phase2.5/bandit-dedup` branch base `15f2108` ≡ main HEAD)
- Rationale: parallel semantics; preserves D6 ripgrep contract by keeping all terminal-non-backtest states in one tuple
- Alternative considered: separate `EMBEDDING_TERMINAL_STATES` tuple — REJECTED; the ripgrep contract at `ingest.py:42–43` would need two-tuple discovery, increasing surface

**X-2 (iii): `assert_lifecycle_invariant_at_batch_close()` is EXTENDED IN-PLACE.**
- Specifically: the existing assertion adds `near_duplicate` to its known-terminal set; no parallel helper introduced
- Rationale: in-place extension preserves the single-assertion contract that's audited by the ripgrep test; parallel helper would split the invariant surface and weaken auditing
- Alternative considered: parallel `assert_lifecycle_invariant_track_b_extended()` — REJECTED; CONTRACT BOUNDARY argument doesn't apply (this is not a D2/D3-class separation; it's a within-orchestrator extension)

---

## §3 Track A per-decision adjudication (11 decisions, A-1..A-11)

Each decision: **chosen default** + **rationale** + **bar-criteria check** (§3 of scoping decision: empirical verifiability / sealed-class boundary respect / reviewer-routing convergence / anti-momentum-binding).

### A-1: Cold-start prior → **Beta(1, 1) uniform**
- **Rationale**: no informed prior available; Phase 1B walk-forward results would leak regime-2022 if used as bootstrap (HARD CONSTRAINT). Uniform Beta(1, 1) is the standard "no information" prior. Jeffreys Beta(0.5, 0.5) introduces theoretical complexity without empirical benefit at this scale.
- **Bar criteria**: empirical-verifiable (posterior trajectory testable from synthetic ledger); sealed-class-respecting (Beta(1,1) is independent of any held-out data); reviewer-convergent (architect+planner did not contest the proposed default); anti-momentum (V2 may add empirical prior without re-litigating the MVP choice).

### A-2: Demotion policy → **Keep all factors in registry forever; no menu removal**
- **Rationale**: removal creates a strong implicit signal (factor X is "bad") that propagates to anyone with menu-history access; per A-Lock-7 menu history is orchestrator-internal but defense in depth prefers no removal at all. Thompson sampling naturally down-samples low-performing factors via Beta posterior — no policy override needed.
- **Bar criteria**: empirical-verifiable (test that low-α/high-β factors still appear in candidate pool, just at lower probability); sealed-class-respecting (no leakage surface); reviewer-convergent; anti-momentum (V2 demotion policy is an additive change, not a default override).

### A-3: K size → **K = 5**
- **Rationale**: matches existing `agents/stage2b_batch.py` theme_factors size precedent. Provides meaningful guidance without over-anchoring. K=3 risks Proposer over-fitting to top-3 stale priors; K=10 dilutes signal.
- **Bar criteria**: empirical-verifiable (curation rank stability test with K sweep on synthetic ledger); sealed-class-respecting; reviewer-convergent; anti-momentum.

### A-4: Decay / forgetting → **No decay for MVP**
- **Rationale**: regime-shift detection requires a baseline; we need observation data first before deciding decay parameters. No-decay is the simplest, mostauditable starting point. V2 can add decay if observation reveals slow posterior adaptation post-regime-shift.
- **Bar criteria**: empirical-verifiable (the observable-failure-mode in scoping A-4 Risk line provides the detection mechanism); sealed-class-respecting (no-decay = simplest implementation); reviewer-convergent; anti-momentum (V2 decay decision uses MVP observation data).

### A-5: Thompson seed → **`hash(batch_id)` deterministic seed**
- **Rationale**: reproducibility for leakage-audit replay + golden-file test pattern. Non-determinism would make every audit and every replay tool produce different artifacts.
- **Bar criteria**: empirical-verifiable (replay-test = same batch_id → same top-K); sealed-class-respecting; reviewer-convergent; anti-momentum.

### A-6: Signal axes → **`regime_holdout_passed` only (binary)**
- **Rationale**: single-axis is simplest. Adding validity rate, novelty, complexity scores expands the bandit's signal surface and adds hyperparameter complexity. V2 may extend if regime-pass-only proves insufficient.
- **Bar criteria**: empirical-verifiable (posterior update test on synthetic ledger with known pass/fail pattern); sealed-class-respecting (binary outcome is the registry's existing field); reviewer-convergent; anti-momentum.

### A-7: Menu phrasing → **"Available factors (recommended)"**
- **Rationale**: most neutral phrasing in the alternatives set. Avoids "curated", "top", "regime", "holdout", "performance", "quality" — all of which leak information about *why* the factors are presented. The audit (A-Lock-4) scans for these forbidden tokens.
- **Bar criteria**: empirical-verifiable (audit test); sealed-class-respecting (passes audit); reviewer-convergent; anti-momentum.

### A-8: Curation cadence → **Per-batch (frozen for batch duration)**
- **Rationale**: per-call introduces in-batch posterior drift that's hard to audit and replay. Per-batch is the only choice that's reproducible from a single `batch_id` seed (per A-5).
- **Bar criteria**: empirical-verifiable; sealed-class-respecting; reviewer-convergent; anti-momentum.

### A-9: Observation forensic schema → **7-column ledger per scoping default**
- **Chosen schema**: `factor_bandit_observations(batch_id TEXT, factor_id TEXT, regime_holdout_passed INTEGER, observed_utc TEXT, hypothesis_hash TEXT, posterior_alpha_pre REAL, posterior_beta_pre REAL)` — append-only, one row per (batch_id, factor_id, hypothesis) where factor appeared in a regime-terminal hypothesis
- **Rationale**: minimum granularity that supports replay + posterior-update audit. Posterior pre-snapshot enables before/after comparison. Aggregated-per-batch loses replay fidelity; denormalized-with-curation-rank adds leakage surface (curation rank ≠ raw signal).
- **Bar criteria**: empirical-verifiable (append-only contract test); sealed-class-respecting (no per-factor metric exposed to LLM context); reviewer-convergent; anti-momentum.

### A-10: `extract_factors(dsl)` error path → **Skip + log; do not block batch close**
- **Rationale**: hard-fail introduces fragility against legitimate edge cases (DSL with literal-only conditions, novel factor patterns). Silent skip without log creates forensic gap. Logged-skip is the discipline-respecting middle path: observable, non-blocking.
- **Bar criteria**: empirical-verifiable (test with mock `extract_factors` raising); sealed-class-respecting; reviewer-convergent; anti-momentum.

### A-11: Batch-summary visibility → **Orchestrator-internal log only**
- **Rationale**: tightest A-Lock-7 compliance. Any visibility outside orchestrator-internal logs creates additional leakage surfaces that may flow into future LLM context construction.
- **Bar criteria**: empirical-verifiable (batch_report.py output content test asserts no curated-menu fields); sealed-class-respecting; reviewer-convergent; anti-momentum.

---

## §4 Track B per-decision adjudication (8 decisions, B-1..B-8)

### B-1: Cosine threshold τ → **0.82 starting; calibrate at sub-task B-T7 (placed as (a) sub-task within this sub-spec cycle per §6 below)**
- **Rationale**: 0.82 is the literature-supported starting point for short-text near-duplicate detection. Empirical calibration sub-task B-T7 sweeps τ ∈ {0.70, 0.75, 0.80, 0.82, 0.85, 0.88, 0.90} against fixture corpus + (when available) Phase 2C Stage 1 DSL pairs to choose production τ.
- **Bar criteria**: empirical-verifiable (B-T7 sweep IS the verification); sealed-class-respecting; reviewer-convergent; anti-momentum.

### B-2: Window → **Within-batch only for MVP**
- **Rationale**: cross-batch dedup requires persistent embedding storage (SQLite BLOB or similar) + cleanup policy + cross-batch determinism guarantees. MVP-simple is within-batch.
- **Bar criteria**: empirical-verifiable; sealed-class-respecting; reviewer-convergent; anti-momentum (V2 cross-batch is an additive change).

### B-3: Quarantine vs reject → **Quarantine via `near_duplicate` lifecycle state**
- **Rationale**: preserves Critic / human adjudication agency. Hard reject is irreversible if the system later decides the rejection was wrong (e.g., near-but-distinct strategies). `near_duplicate` counts for DSR denominator like `DUPLICATE`.
- **Bar criteria**: empirical-verifiable (lifecycle invariant test); sealed-class-respecting; reviewer-convergent; anti-momentum.

### B-4: Embed input → **D3-canonical DSL JSON**
- **Rationale**: structured text well-handled by sentence-transformers `all-MiniLM-L6-v2`. Features-projection alternative loses operator semantics. Pre-canonicalization JSON includes name/description noise (cosmetic fields excluded by D3 canonicalization for hash stability — same exclusions benefit embeddings).
- **Bar criteria**: empirical-verifiable (cosine on B-T7 fixture pairs); sealed-class-respecting; reviewer-convergent; anti-momentum.

### B-5: Parameter bucketing → **None at canonicalization**
- **Rationale**: bucketing at canonicalization would violate B-Lock-2 (no change to D3 hash canonicalization). Letting cosine similarity decide semantic closeness preserves the CONTRACT BOUNDARY. If bucketing proves needed at V2, it lives in `semantic_dedup.py` per the B-Lock-2 call-graph rule.
- **Bar criteria**: empirical-verifiable (B-T7 false-positive rate on SMA(20) vs SMA(25) test pairs); sealed-class-respecting (CONTRACT BOUNDARY preserved); reviewer-convergent; anti-momentum.

### B-6: Compound gate → **Cosine-only for MVP**
- **Rationale**: simplest. AND-gate adds one more hyperparameter (structural overlap threshold) without empirical justification at MVP scale. V2 can add structural-overlap gate if B-T7 reveals false-positive rate above tolerance.
- **Bar criteria**: empirical-verifiable; sealed-class-respecting; reviewer-convergent; anti-momentum.

### B-7: Model load-failure policy → **Hard-fail at orchestrator startup**
- **Rationale**: silent degradation means a batch could go through with semantic-dedup-disabled without operator awareness — that's a discipline violation in the "orchestrator state matches its declared capabilities" sense. Hard-fail couples Track B health to orchestrator startup (acceptable per parking-strategy isolation; the parked branch is only activated when batch cadence resumes).
- **Bar criteria**: empirical-verifiable (mocked sentence-transformers import-failure test); sealed-class-respecting; reviewer-convergent; anti-momentum.

### B-8: Cache cap → **Unbounded within batch; per-batch clear bounds memory**
- **Rationale**: typical batch size is 200; embedding cache at 200×384-dim float32 ≈ 300 KB — trivial. Cap-with-eviction creates false-negatives where evicted embeddings would have caught later near-duplicates. Per-batch clear (per B-Lock-5) is the memory bound.
- **Bar criteria**: empirical-verifiable (memory-footprint test with synthetic 2000-hypothesis batch); sealed-class-respecting (no cross-batch state); reviewer-convergent; anti-momentum (V2 can add cap if 2000+ batches become normal).

---

## §5 Cross-track X-3, X-4 adjudication

### X-3: Dependency surface delta → **As specified in scoping**
- Track A: zero new dependencies (stdlib + numpy + sqlite already in pyproject.toml)
- Track B: `sentence-transformers>=2.0.0` under `[project.optional-dependencies]` extras `phase2_5`, with SHA pin + project-local cache directory per B-Lock-7
- **Implementation arc Wave B-1 sub-task**: SHA-pinning logic in pyproject.toml + integrity check at startup

### X-4: Test surface allocation → **As specified in scoping with one addition**
- All test types per scoping X-4 enumerated
- **Addition**: a top-level integration test `tests/test_bandit_dedup_e2e.py` MUST exercise a full 2-batch synthetic flow: batch 1 produces regime-passing + regime-failing hypotheses; bandit updates posterior; batch 2 receives curated menu; semantic dedup quarantines a near-duplicate within batch 2.

---

## §6 ADOPT-LIGHT sub-spec resolutions inherited from scoping

### A-Lock-4: `top_factors_block` field-split vs inline scan → **SPLIT into separately addressable `ProposerPrompt` field**
- **Rationale**: matches the architect's preference (F1 Proposed edit). Surface isolation makes the audit mechanically simple. The shared `ProposerPrompt.all_text()` continues to concatenate `system + user + factor_menu + top_factors_block`; `audit_prompt_for_leakage()` reads the same concatenation but with a *scoped* check on `top_factors_block` substring boundaries.
- **Sub-spec contract**:
  - `ProposerPrompt` dataclass adds field `top_factors_block: str = ""`
  - `ProposerPrompt.all_text()` concatenates: `system + "\n\n" + user + "\n\n" + factor_menu + "\n\n" + top_factors_block`
  - `audit_prompt_for_leakage()` runs the existing forbidden-token scan over `all_text()` AND a scoped scan over `top_factors_block` for the extended forbidden-language list (regime / holdout / pass / fail / score / quality / signal / performance)

### B-T7 placement → **(a) sub-task within Track B sub-spec drafting cycle**
- **Rationale**: B-T7 is sized for a single deliverable (sweep + corpus + decision); standalone cycle bureaucracy would be heavier than the work itself. As a Track-B-sub-spec-internal sub-task, B-T7 runs alongside Track B per-decision adjudication and its output (chosen τ) feeds B-1's final default.
- **Sub-task placement in this sub-spec arc**:
  - Sub-spec cycle Session 1: B-T7 sub-task entry register-event (this draft commit)
  - Sub-spec cycle Session 2: B-T7 calibration runs (parameterized sweep on fixture corpus); Session 2 reviewers may critique B-T7 methodology in parallel with the rest of the sub-spec doc
  - Sub-spec cycle Session 3 (SEAL): B-T7 chosen-τ output integrated into B-1 default; sub-spec SEAL fires only when B-T7 produces a calibrated τ value

**Note**: Path 3's PHASE2C_6 evaluation gate arc precedent of "calibration as scope-internal sub-task" supports this placement.

---

## §7 Implementation arc Wave preview (NOT authorization)

This section is informational only — implementation arc entry is a separate register-event boundary per scoping §6.

**Anticipated Wave structure (post-sub-spec-SEAL, NOT pre-authorized)**:

**Wave 0 (precondition)**: shared `BatchIngestState` shape commit on parked branch (single commit, both tracks depend on it).

**Wave A-1 (parallel internal — Track A TDD)**:
- A-T1: tests for `factor_bandit.observe_batch()` posterior update
- A-T2: tests for `factor_bandit.curate_top_k()` Thompson sampling
- A-T3: tests for `audit_prompt_for_leakage()` extended scoped scan
- A-T4: database-reviewer review of proposed schema (A-9 7-column)

**Wave A-2 (sequential after A-1)**:
- A-T5: implement `factor_bandit.py`
- A-T6: extend `prompt_builder.py` (`top_factors_block` field split)
- A-T7: orchestrator wiring (batch-close observation, next-batch curation)

**Wave A-3 (parallel reviewers)**: python-reviewer + security-reviewer + code-reviewer + (deferred dual-reviewer + Codex)

**Wave B-1 / B-2 / B-3**: mirror structure for Track B (semantic_dedup.py + ingest extension + sentence-transformers pinning)

**Wave Cross**: integration test `test_bandit_dedup_e2e.py` after both arcs land

**Arc-level closeout SEAL**: bundles all Wave commits, V# self-check, atomic acceptance note. Combined or per-track is a separate decision at arc-level closeout register-event.

---

## §8 V# self-checklist for sub-spec SEAL (12 anchors)

Evaluated at pre-SEAL register at Session 3. SEAL fire requires all 12 CLEAN.

- **V1**: Sub-spec cycle scope precisely defined (intro + §1.4-equivalent)
- **V2**: `BatchIngestState` shape locked with Track-A-zero + Track-B-one-field discipline (§1)
- **V3**: Lifecycle state machine (X-2) all 3 sub-questions adjudicated (§2)
- **V4**: Track A 11 decisions each have chosen default + rationale + bar-criteria check (§3)
- **V5**: Track B 8 decisions each have chosen default + rationale + bar-criteria check (§4)
- **V6**: Cross-track X-3, X-4 adjudication explicit (§5)
- **V7**: A-Lock-4 field-split decision resolved with sub-spec contract (§6)
- **V8**: B-T7 placement decided as (a) sub-task within this sub-spec cycle (§6)
- **V9**: Implementation arc Wave preview included WITHOUT authorizing implementation arc entry (§7)
- **V10**: B-T7 calibration output produced at Session 2; integrated into B-1 default at Session 3 SEAL
- **V11**: 2 parallel reviewers fired at Session 2 (architect + planner per scoping precedent, or alternative mix per Charlie register-event Session 2 authorization)
- **V12**: Per-fix adjudication discipline at Session 3 (no bulk-accept); dispositions table in Appendix B

---

## §9 Push / tagging / Phase Marker discipline at sub-spec SEAL

- **NO tag** at sub-spec SEAL (process/spec deliverable register-class precedent — same as scoping SEAL)
- **NO push to remote** at sub-spec SEAL — parked branch stays local until activation
- **NO Phase Marker advance on main** at sub-spec SEAL — parked branch internal
- Sub-spec SEAL commit is commit 3 on `phase2.5/bandit-dedup` (after `97f7774` scoping draft, `f63b316` scoping SEAL)
- At eventual merge time, atomic Phase Marker advance + history file update per `feedback_claude_md_freshness.md` Option 1A binding

---

## §10 Anti-pre-emption invariant at sub-spec SEAL

This sub-spec SEAL does NOT:

- Pre-authorize implementation arc entry — separate Charlie register-event required (cycle-entry)
- Pre-authorize Wave 0 `BatchIngestState` shape commit — Wave 0 commit IS an implementation arc commit (decision-class)
- Pre-authorize subagent dispatch for code writing (decision-class)
- Modify CLAUDE.md HARD CONSTRAINTS on main — 14 proposed locks remain deferred to merge time (decision-class)
- Push the parked branch to remote (cycle-entry)
- Pre-commit any sub-spec choice as immune from re-adjudication at implementation arc — if implementation reveals a sub-spec choice is incorrect, an explicit "sub-spec amendment register-event" is the path back (decision-class)

---

## Appendix A — review routing plan for Session 2 (NOT executed at this Session 1 commit)

Per scoping cycle precedent: 2 parallel internal Claude Code subagents fired independently.

**Reviewer 1 — `architect` subagent**: architectural critique of sub-spec choices for implementation soundness. Read sub-spec + scoping decision + relevant code (`prompt_builder.py`, `ingest.py`, `hypothesis_hash.py`).

**Reviewer 2 — `planner` subagent**: plan-completeness critique. Read sub-spec + scoping decision + Path 3 / Phase 5 sub-spec precedents (when available) + METHODOLOGY_NOTES.

Alternative reviewer mix (subject to Charlie register-event Session 2 authorization): `database-reviewer` (for A-9 schema + `factor_posterior` table) + `security-reviewer` (for B-Lock-7 SHA pinning + supply-chain audit framing). The database+security mix is more substantive for sub-spec adjudication than architect+planner; the latter were better-fit for scoping (no concrete adjudications).

**Codex**: skipped at sub-spec cycle per process/spec deliverable register-class hard rule.

**python-reviewer + security-reviewer**: skipped at sub-spec cycle (no code; both apply at implementation arc Wave A-3 / B-3).

---

## Appendix B — Session 3 adjudication dispositions table (PLACEHOLDER for SEAL)

To be populated at Session 3 after Session 2 reviewer routing returns findings. Same disposition buckets as scoping: ADOPT / ADOPT-LIGHT / DEFER / PUSHBACK / PASS.

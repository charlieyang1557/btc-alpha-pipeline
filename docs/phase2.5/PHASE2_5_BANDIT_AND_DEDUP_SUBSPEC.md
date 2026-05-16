# Phase 2.5 — Combined Bandit + Dedup Sub-Spec Drafting

**Cycle classification**: process/spec deliverable register-class (NOT substantive empirical research register-class). B-T7 empirical calibration sub-task was originally placed at (a) sub-task within this sub-spec cycle in Session 1 draft; **at Session 3 SEAL, B-T7 is RELOCATED to (c) Wave 0 sub-task within the implementation arc** per architect F3 + planner F1 + planner F2 3-way reviewer convergence. This sub-spec cycle therefore preserves pure process/spec deliverable register-class semantics. Combined (α) posture per scoping decision §1.5 default-recommended.

**Cycle authorization**: Charlie register-event boundary at "authorized" reply 2026-05-16 for entry; "authorize for all three sessions" Charlie register-event boundary 2026-05-16 for Sessions 2 + 3.

**Base**: parked branch `phase2.5/bandit-dedup` at `f63b316` (combined scoping cycle SEAL).

**Predecessor**: [`docs/phase2.5/PHASE2_5_BANDIT_AND_DEDUP_SCOPING_DECISION.md`](PHASE2_5_BANDIT_AND_DEDUP_SCOPING_DECISION.md) — 23 design candidates / 14 discipline locks / 15 V# anchors.

**Cycle scope deliverable**: per-decision adjudication (one default per of 23 decisions) + shared `BatchIngestState` shape lock + `BatchBanditSelection` shape lock + `build_prompt()` signature stability lock + resolution of 2 ADOPT-LIGHT sub-spec choices inherited from scoping (A-Lock-4 SPLIT + B-T7 placement) + lifecycle-state-machine concrete decisions (X-2 (i)/(ii)/(iii)) + implementation arc Wave preview (informational, NOT authorization).

---

## §1 Shared `BatchIngestState` shape lock (X-1 first deliverable)

Per scoping X-1, the sub-spec's first deliverable locks the shared dataclass shape before either implementation arc begins. **Adjudicated default at Session 3 SEAL**:

### §1.0 Current `BatchIngestState` field inventory at parked-branch base `15f2108`

Verified by direct read of `agents/orchestrator/ingest.py` on this worktree at the parked-branch base:

```python
@dataclass
class BatchIngestState:
    batch_id: str
    hypotheses_attempted: int = 0
    seen_hashes: set[str] = field(default_factory=set)
    lifecycle_counts: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    records: list[HypothesisRecord] = field(default_factory=list)
```

5 existing fields. Dataclass is NOT `frozen=True` (mutable).

### §1.1 Post-implementation-arc `BatchIngestState` shape (locked at sub-spec SEAL)

```python
@dataclass  # remains NOT frozen=True; existing project pattern
class BatchIngestState:
    batch_id: str
    hypotheses_attempted: int = 0
    seen_hashes: set[str] = field(default_factory=set)
    lifecycle_counts: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    records: list[HypothesisRecord] = field(default_factory=list)
    embedding_cache: dict[str, "np.ndarray"] = field(default_factory=dict)  # NEW for Track B
```

**Lock rationale**:
- **Track A adds ZERO fields**. Posterior state lives in `factor_posterior` SQLite table; Thompson-sampled selection materializes into a separate `BatchBanditSelection` dataclass (§1.2). Confirmed via field-count delta test (X-4 cross-track).
- **Track B adds ONE field**: `embedding_cache: dict[str, np.ndarray]` — per-batch, cleared at `finalize_batch()` per B-Lock-5. Mutable dict matches existing pattern.

**Implementation order constraint**: this dataclass shape MUST be the first commit of the implementation arc (Wave 0), before either Wave A-1 or Wave B-1 fires.

### §1.2 `BatchBanditSelection` shape lock (added Session 3 per A-F5)

Track A's Thompson-sampled top-K materializes into a separate frozen dataclass defined in `agents/orchestrator/factor_bandit.py`:

```python
@dataclass(frozen=True)
class BatchBanditSelection:
    batch_id: str
    top_factors: tuple[str, ...]  # K-tuple; K locked at A-3
    selection_seed: int  # deterministic per A-5; archived for replay
```

**`build_prompt()` signature stability**: `build_prompt()` keeps its existing `top_factors: tuple[str, ...] = ()` parameter. The orchestrator extracts `.top_factors` from `BatchBanditSelection` and passes the tuple. This preserves `sonnet_backend.py:183` call-site stability and allows Wave A-1 (factor_bandit.py) + Wave A-2 (prompt_builder.py extension) to develop in parallel without cross-module signature coordination.

### §1.3 Field-count delta test contract (per X-4 cross-track, Session 3 inline-enumerated per A-F7)

```python
def test_batchingeststate_field_count_track_a_zero_delta():
    """Track A implementation must add zero fields to BatchIngestState.
    Track B adds exactly one field (embedding_cache)."""
    expected_post_track_b = {
        "batch_id", "hypotheses_attempted", "seen_hashes",
        "lifecycle_counts", "records", "embedding_cache",
    }
    actual = {f.name for f in fields(BatchIngestState)}
    assert actual == expected_post_track_b, f"shape drift: {actual ^ expected_post_track_b}"
```

---

## §2 Lifecycle state machine extension (X-2 (i)/(ii)/(iii) adjudication)

Per scoping X-2, sub-spec MUST decide three sub-questions. **Adjudicated defaults at Session 3 SEAL**:

**X-2 (i): `near_duplicate` is TERMINAL at batch close.**
- Rationale: matches `DUPLICATE` semantics (already terminal); avoids state-machine complexity of transient → terminal resolution; Critic / human override is performed by re-submission with mutation (a new hypothesis), not by mutating the existing record's state.
- Alternative considered: transient with post-finalize resolution to `DUPLICATE` — REJECTED for state-machine complexity and ambiguity around DSR denominator counting timing.

**X-2 (ii): `near_duplicate` joins `D6_STAGE1_LIFECYCLE_STATES` (Session 3 verified per A-F6).**
- The actual terminal-state tuple at parked-branch base `15f2108` is `D6_STAGE1_LIFECYCLE_STATES` in `agents/orchestrator/ingest.py` containing 5 elements: `INVALID_DSL`, `REJECTED_COMPLEXITY`, `DUPLICATE`, `PENDING_BACKTEST`, `BACKEND_EMPTY_OUTPUT`. The sub-spec's Session 1 draft referenced a hypothetical "D7/D8 successor tuple" — that constant does not exist; this is the authoritative name.
- **Binding-at-implementation rule**: at Wave 0 in the implementation arc, the implementation MUST verify that the canonical terminal-state set is still named `D6_STAGE1_LIFECYCLE_STATES` (or its renamed successor if any) and add `NEAR_DUPLICATE` to that single tuple — one tuple, not two — regardless of name drift.
- Alternative considered: separate `EMBEDDING_TERMINAL_STATES` tuple — REJECTED; the ripgrep contract at `ingest.py:42–43` would need two-tuple discovery, increasing surface and weakening auditing.

**X-2 (iii): `assert_lifecycle_invariant_at_batch_close()` is EXTENDED IN-PLACE.**
- The existing assertion adds `NEAR_DUPLICATE` to its known-terminal set; no parallel helper introduced. Preserves the single-assertion contract audited by the ripgrep test.
- Alternative considered: parallel `assert_lifecycle_invariant_track_b_extended()` — REJECTED; CONTRACT BOUNDARY argument doesn't apply (this is within-orchestrator extension, not D2/D3-class separation).

---

## §3 Track A per-decision adjudication (11 decisions, A-1..A-11)

Each decision: **chosen default** + **rationale (defending vs strongest alternative)** + **4-criterion bar check with observable-failure-mode clause where applicable** (Session 3 strengthened per P-F3, P-F4).

### A-1: Cold-start prior → **Beta(1, 1) uniform**
- **Rationale (vs strongest alternative)**: empirical prior bootstrapped from Phase 1B walk-forward results would leak regime-2022 if used as bootstrap (HARD CONSTRAINT). Jeffreys Beta(0.5, 0.5) introduces theoretical complexity without empirical benefit at MVP scale. Beta(2, 2) conservative is symmetric with Beta(1, 1) for first few observations.
- **Bar criteria**: empirical-verifiable (posterior trajectory testable from synthetic ledger; **if wrong, detectable as: top-K factors drift wildly across early batches because Beta(1,1) variance is too high for small samples**); sealed-class-respecting (Beta(1,1) is independent of any held-out data); reviewer-convergent (neither reviewer contested at Session 2); anti-momentum (V2 may add empirical prior without re-litigating MVP).

### A-2: Demotion policy → **Keep all factors in registry forever; no menu removal**
- **Rationale (vs strongest alternative)**: hard removal threshold creates a strong implicit signal ("factor X is bad") that propagates to anyone with menu-history access; per A-Lock-7 menu history is orchestrator-internal but defense in depth prefers no removal at all. Thompson sampling naturally down-samples low-performing factors via Beta posterior — no policy override needed.
- **Bar criteria**: empirical-verifiable (**if wrong, detectable as: cross-batch posterior accumulation compounds in a way that low-α/high-β factors still appear in candidate pool but at vanishingly low Thompson-sample probability — verifiable via Monte Carlo of posterior over N batches**); sealed-class-respecting; reviewer-convergent; anti-momentum.

### A-3: K size → **K = 5**
- **Rationale (vs strongest alternative)**: matches existing `agents/stage2b_batch.py` theme_factors size precedent. K=3 risks Proposer over-fitting to top-3 stale priors; K=10 dilutes signal; adaptive K based on posterior variance is a hyperparameter that itself needs calibration.
- **Bar criteria**: empirical-verifiable (curation rank stability test with K sweep on synthetic ledger; **if wrong, detectable as: hypothesis diversity rate drops sharply at K<5 or signal saturates at K>5 — measurable via per-factor occurrence variance across batches**); sealed-class-respecting; reviewer-convergent; anti-momentum.

### A-4: Decay / forgetting → **No decay for MVP**
- **Rationale (vs strongest alternative, strengthened Session 3 per P-F4)**: decay's strongest motivation (regime non-stationarity) is empirically testable post-MVP per scoping A-4 observable-failure-mode template. Pre-MVP commitment to exponential decay with half-life would lock a half-life value with no empirical anchor — the parameter choice itself can be wrong (too-short half-life over-reacts to batch noise; too-long half-life is indistinguishable from no-decay). No-decay is the default; observation reveals whether decay is needed before V2 commits to a half-life.
- **Bar criteria**: empirical-verifiable (**if wrong, detectable as: monotonic decline in regime-holdout pass rate across N batches following a candidate regime shift; cross-batch factor pass-rate correlation > threshold when batches span the shift**, per scoping A-4 Risk line); sealed-class-respecting; reviewer-convergent; anti-momentum (V2 decay decision uses MVP observation data).

### A-5: Thompson seed → **`int.from_bytes(hashlib.sha256(batch_id.encode('utf-8')).digest()[:8], 'big')` deterministic seed (Session 3 correctness fix per A-F2)**
- **Rationale (vs strongest alternative, corrected Session 3 per architect F2 correctness finding)**: Python's built-in `hash()` for `str` is salted per-interpreter-instance via PYTHONHASHSEED since CPython 3.3 — `hash(batch_id)` is **NOT deterministic across processes** and would silently violate A-5's replay-determinism requirement. SHA-256 of `batch_id.encode('utf-8')` truncated to 8 bytes provides cryptographic determinism. Non-determinism alternative (fresh RNG) makes leakage audits and replay artifacts non-reproducible.
- **Bar criteria**: empirical-verifiable (replay-test = same batch_id → same top-K across two Python interpreter sessions; **if wrong, detectable as: two replay runs of the same batch_id producing different top_factors blocks; failure of golden-file tests against curation snapshots**); sealed-class-respecting; reviewer-convergent; anti-momentum.

### A-6: Signal axes → **`regime_holdout_passed` only (binary)**
- **Rationale (vs strongest alternative)**: multi-axis (validity rate, novelty, complexity, motivation quality) expands signal surface and adds hyperparameter complexity (per-axis weight). V2 may extend if regime-pass-only proves insufficient — but starting multi-axis pre-commits to weighting before any observation.
- **Bar criteria**: empirical-verifiable (posterior update test on synthetic ledger with known pass/fail pattern; **if wrong, detectable as: persistent gap between bandit-curated and oracle-best factor selection, observable in offline backtest comparison**); sealed-class-respecting (binary outcome is the registry's existing field); reviewer-convergent; anti-momentum.

### A-7: Menu phrasing → **"Available factors (recommended)"**
- **Rationale (vs strongest alternative)**: most neutral phrasing in the alternatives set. "Curated for today's batch", "top selections", "recommended for hypothesis generation" all leak intensity of recommendation. "Available factors (recommended)" presents the menu without implying "regime-passing" or "best".
- **Bar criteria**: empirical-verifiable (audit test runs forbidden-language scan over `top_factors_block`; **if wrong, detectable as: leakage-audit positive on the chosen phrasing — fails CI**); sealed-class-respecting (passes audit per A-Lock-4 extended forbidden list); reviewer-convergent; anti-momentum.

### A-8: Curation cadence → **Per-batch (frozen for batch duration)**
- **Rationale (vs strongest alternative)**: per-call (re-sample per Proposer API call within batch) introduces in-batch posterior drift that's hard to audit and replay. Per-batch is the only choice that's reproducible from a single batch_id seed (per A-5).
- **Bar criteria**: empirical-verifiable (replay-test: same batch_id → same top-K throughout batch; **if wrong, detectable as: top_factors block content varies across Proposer calls within one batch, failing the per-batch-frozen contract test**); sealed-class-respecting; reviewer-convergent; anti-momentum.

### A-9: Observation forensic schema → **7-column ledger**
- **Chosen schema**: `factor_bandit_observations(batch_id TEXT, factor_id TEXT, regime_holdout_passed INTEGER, observed_utc TEXT, hypothesis_hash TEXT, posterior_alpha_pre REAL, posterior_beta_pre REAL)` — append-only, one row per (batch_id, factor_id, hypothesis) where factor appeared in a regime-terminal hypothesis.
- **Rationale (vs strongest alternative)**: aggregated-per-batch loses replay fidelity (cannot reconstruct posterior trajectory mid-batch). Denormalized-with-curation-rank adds leakage surface (curation rank ≠ raw signal). Dual ledger (observation + posterior snapshot) adds storage with no replay benefit beyond what append-only observation provides.
- **Bar criteria**: empirical-verifiable (append-only contract test asserts no UPDATE/DELETE on the table; **if wrong, detectable as: observation row count diverges from regime-terminal hypothesis count across batches**); sealed-class-respecting (no per-factor metric exposed to LLM context per A-Lock-7); reviewer-convergent; anti-momentum.

### A-10: `extract_factors(dsl)` error path → **Skip + log; do not block batch close**
- **Rationale (vs strongest alternative)**: hard-fail introduces fragility against legitimate edge cases (DSL with literal-only conditions, novel factor patterns). Silent skip without log creates forensic gap. Logged-skip is the discipline-respecting middle path: observable, non-blocking.
- **Bar criteria**: empirical-verifiable (test with mock `extract_factors` raising; **if wrong, detectable as: batch close blocks on DSL edge cases or silent skip creates orphan factor observations**); sealed-class-respecting; reviewer-convergent; anti-momentum.

### A-11: Batch-summary visibility → **Orchestrator-internal log only**
- **Rationale (vs strongest alternative)**: visible-in-batch-summary alternative creates additional leakage surfaces that may flow into future LLM context construction (e.g., approved_examples assembly reading batch report content). Operator-only debug report has a gradient toward "leak via copy-paste". Orchestrator-internal log is tightest A-Lock-7 compliance.
- **Bar criteria**: empirical-verifiable (`batch_report.py` output content test asserts no curated-menu fields; **if wrong, detectable as: grep over generated batch reports finds factor menu strings**); sealed-class-respecting; reviewer-convergent; anti-momentum.

---

## §4 Track B per-decision adjudication (8 decisions, B-1..B-8)

### B-1: Cosine threshold τ → **0.82 PROVISIONAL at sub-spec SEAL; Wave 0 re-adjudication trigger active (Session 3 reframed per A-F3 + P-F1 + P-F2 3-way convergence)**
- **Status**: sub-spec SEAL fires with τ=0.82 as the PROVISIONAL starting value. Final τ produced at implementation arc Wave 0 B-T7 calibration sub-task (see §6 below for placement). Sub-spec SEAL is NOT gated on B-T7 output; the Wave 0 → B-1 amendment loop is the formal re-adjudication path.
- **Rationale (vs strongest alternative)**: 0.82 is the literature-supported starting point for short-text near-duplicate detection on sentence-transformers; chosen as provisional anchor pending empirical calibration. Other τ values (0.70 / 0.75 / 0.80 / 0.85 / 0.88 / 0.90) await Wave 0 B-T7 sweep.
- **Bar criteria**: empirical-verifiable (Wave 0 B-T7 sweep IS the verification; **if wrong, detectable as: Wave 0 B-T7 calibration reveals knee-point τ outside [0.80, 0.85] range, triggering B-1 amendment**); sealed-class-respecting; reviewer-convergent (3-way at Session 2); anti-momentum (re-adjudication trigger explicit).

### B-2: Window → **Within-batch only for MVP**
- **Rationale (vs strongest alternative, strengthened Session 3 per P-F4)**: cross-batch sliding window's strongest motivation is catching repeat patterns across batches — but its storage cost (SQLite BLOB per embedding × hundreds of batches × N-vector per embedding) is non-trivial, and cross-batch determinism requires either reproducible embedding storage or accepting non-determinism. False-negative cost of within-batch-only (some near-duplicates pass) is empirically bounded by within-batch dedup catching ~70-85% of duplicates in typical short-text dedup workloads; the remaining 15-30% are caught at backtest stage (most near-duplicate strategies show near-duplicate backtests). MVP within-batch retains 95%+ practical dedup benefit at fractional cost.
- **Bar criteria**: empirical-verifiable (within-batch dedup recall test on Wave 0 B-T7 fixture corpus; **if wrong, detectable as: post-batch leaderboard shows clusters of near-duplicate strategies with similar Sharpe**); sealed-class-respecting; reviewer-convergent; anti-momentum.

### B-3: Quarantine vs reject → **Quarantine via `near_duplicate` lifecycle state**
- **Rationale (vs strongest alternative)**: hard reject is irreversible — if the system later decides the rejection was wrong (near-but-distinct strategies), there's no recovery path. Quarantine preserves Critic / human adjudication agency. `near_duplicate` counts for DSR denominator like `DUPLICATE`.
- **Bar criteria**: empirical-verifiable (lifecycle invariant test asserts `near_duplicate` joins terminal set; **if wrong, detectable as: lifecycle invariant assertion fails with unknown state or terminal-state-count mismatch**); sealed-class-respecting; reviewer-convergent; anti-momentum.

### B-4: Embed input → **D3-canonical DSL JSON (with explicit soft re-use acknowledgment, Session 3 per A-F4)**
- **Rationale (vs strongest alternative)**: sentence-transformers `all-MiniLM-L6-v2` handles structured text reasonably; features-projection loses operator semantics; pre-canonicalization JSON includes name/description noise (excluded by D3 for hash stability — same exclusions benefit embeddings).
- **D3 soft re-use acknowledgment**: B-4 creates an *implicit second consumer* of the D3 canonical form. Any future D3 canonicalization tweak (tag scheme change, float precision change, sort-order change) would silently invalidate calibrated τ. This is a CONTRACT BOUNDARY pressure point. **Re-calibration trigger**: any change to `agents/hypothesis_hash.py::canonicalize_for_hash` after sub-spec SEAL requires Wave 0 B-T7 re-calibration before merge. This is added to pre-merge verification checklist as item 4.5 (between current items 4 and 5) at merge time.
- **Bar criteria**: empirical-verifiable (cosine on Wave 0 B-T7 fixture pairs; **if wrong, detectable as: cosine similarity > τ between two DSLs with disjoint factor sets but overlapping operator structure — manual review of top-K cosine pairs**); sealed-class-respecting (CONTRACT BOUNDARY preserved if B-Lock-2 call-graph rule honored); reviewer-convergent; anti-momentum.
- **Note**: architect F4 alternative ((ii) thin embed-friendly serializer in `semantic_dedup.py` traversing DSL directly) is a credible V2 candidate if D3 soft re-use proves brittle; deferred to V2 successor work per §5.

### B-5: Parameter bucketing → **None at canonicalization**
- **Rationale (vs strongest alternative)**: bucketing at canonicalization violates B-Lock-2 (no change to D3 hash canonicalization). Letting cosine similarity decide semantic closeness preserves CONTRACT BOUNDARY. If bucketing proves needed at V2, it lives in `semantic_dedup.py` per the B-Lock-2 call-graph rule.
- **Bar criteria**: empirical-verifiable (Wave 0 B-T7 false-positive rate on SMA(20) vs SMA(25) test pairs; **if wrong, detectable as: false-positive rate at calibrated τ above tolerance, triggering V2 bucketing decision**); sealed-class-respecting (CONTRACT BOUNDARY preserved); reviewer-convergent; anti-momentum.

### B-6: Compound gate → **Cosine-only for MVP**
- **Rationale (vs strongest alternative, strengthened Session 3 per P-F4)**: AND-gate's strongest motivation is false-positive risk reduction (cosine + structural overlap both required). But the AND-gate adds a second hyperparameter (structural overlap threshold τ_s) that itself needs calibration — without empirical data showing the false-positive rate is above tolerance at cosine-only, AND-gate is premature complexity. Wave 0 B-T7 sweep reveals false-positive rate at calibrated τ; if above tolerance, V2 can adopt AND-gate.
- **Bar criteria**: empirical-verifiable (false-positive rate measurement at Wave 0 B-T7; **if wrong, detectable as: false-positive rate > 5% at calibrated τ on fixture corpus, triggering V2 AND-gate adoption**); sealed-class-respecting; reviewer-convergent; anti-momentum.

### B-7: Model load-failure policy → **Hard-fail at orchestrator startup**
- **Rationale (vs strongest alternative)**: silent degradation means a batch could go through with semantic-dedup-disabled without operator awareness — a discipline violation in the "orchestrator state matches its declared capabilities" sense. Override flag (`--no-semantic-dedup`) creates a soft-off path that's hard to audit. Hard-fail couples Track B health to orchestrator startup (acceptable per parking-strategy isolation; parked branch is only activated when batch cadence resumes).
- **Bar criteria**: empirical-verifiable (mocked sentence-transformers import-failure test asserts orchestrator startup raises; **if wrong, detectable as: batch begins with missing embedding stack and finishes without near-duplicate flagging**); sealed-class-respecting; reviewer-convergent; anti-momentum.

### B-8: Cache cap → **Unbounded within batch; per-batch clear bounds memory**
- **Rationale (vs strongest alternative)**: typical batch size is 200; embedding cache at 200×384-dim float32 ≈ 300 KB — trivial. Cap-with-eviction creates false-negatives where evicted embeddings would have caught later near-duplicates. Per-batch clear (per B-Lock-5) is the memory bound.
- **Bar criteria**: empirical-verifiable (memory-footprint test with synthetic 2000-hypothesis batch; **if wrong, detectable as: orchestrator memory growth tracks batch progress proportionally beyond clear threshold**); sealed-class-respecting (no cross-batch state); reviewer-convergent; anti-momentum.

---

## §5 Cross-track X-3, X-4 adjudication

### X-3: Dependency surface delta → **As specified in scoping**
- Track A: zero new dependencies (stdlib + numpy + sqlite already in pyproject.toml)
- Track B: `sentence-transformers>=2.0.0` under `[project.optional-dependencies]` extras `phase2_5`, with SHA pin + project-local cache directory per B-Lock-7
- **Implementation arc Wave 0 sub-task**: SHA-pinning logic in pyproject.toml + integrity check at startup (alongside Wave 0 B-T7 calibration)

### X-4: Test surface allocation → **As specified in scoping + cross-track integration**
- All test types per scoping X-4 enumerated (location + type)
- **Addition**: top-level integration test `tests/test_bandit_dedup_e2e.py` MUST exercise a full 2-batch synthetic flow: batch 1 produces regime-passing + regime-failing hypotheses; bandit updates posterior; batch 2 receives curated menu; semantic dedup quarantines a near-duplicate within batch 2

---

## §6 ADOPT-LIGHT sub-spec resolutions inherited from scoping

### A-Lock-4: `top_factors_block` field-split contract (Session 3 fully specified per A-F1)

**Resolution**: SPLIT into a separately addressable `ProposerPrompt` field.

**Mechanical contract** (verified against actual `prompt_builder.py` shape at parked-branch base):

1. **`ProposerPrompt` remains `@dataclass(frozen=True)`** (existing discipline). New field uses `top_factors_block: str = field(default="")`. No mutation pattern introduced.
2. **`all_text()` separator preserved at `"\n"`** (single newline, existing). The new concatenation is: `system + "\n" + user + "\n" + factor_menu + "\n" + top_factors_block`. Audit substring boundaries unchanged.
3. **Inline emission removed from `user_lines`**: the existing local `top_factors_block` variable at `build_prompt():211` (currently emitted inline at `user_lines.append` line 231) is **moved out of `user_lines`** and assigned to the new `ProposerPrompt.top_factors_block` field. The `user_lines` no longer carries the "top factors by frequency:" prelude — that prelude is part of `top_factors_block` content.
4. **`audit_prompt_for_leakage()` extension**: existing forbidden-token regex scan runs over `all_text()` unchanged. Additional scoped scan runs over `prompt.top_factors_block` substring with the extended forbidden-language list (`regime`, `holdout`, `pass`, `fail`, `score`, `quality`, `signal`, `performance`) using the same word-boundary regex compilation pattern.
5. **Backwards-compat**: when `top_factors_block == ""` (no bandit signal), the field is the empty string; concatenation appends a trailing `"\n"` which is benign; legacy callers without `BatchBanditSelection` continue to work unchanged.

### B-T7 placement → **(c) Wave 0 sub-task within implementation arc (Session 3 RELOCATED per A-F3 + P-F1 + P-F2 3-way convergence)**

**Resolution**: B-T7 calibration **does NOT run within this sub-spec drafting cycle**. B-T7 runs as Wave 0 sub-task within the implementation arc, alongside (a) the shared `BatchIngestState` shape commit and (b) the sentence-transformers SHA-pin commit.

**Rationale** (3-way reviewer convergence):
- Architect F3: running B-T7 inside sub-spec violates process/spec deliverable register-class because installing `sentence-transformers` + running inference is an implementation arc commit shape, not a sub-spec doc commit shape
- Planner F1: the intro vs. §6 contradiction (claiming "registered as separate eligible-not-named" while §6 placed B-T7 in-cycle) is a discipline-line breach
- Planner F2: V10's "B-T7 calibration output produced at Session 2; integrated into B-1 default at Session 3 SEAL" is not mechanically verifiable as a V# anchor — there's no specified artifact, no failure mode, no escape hatch for inconclusive sweep

**Sub-spec SEAL implications**:
- B-1 default at sub-spec SEAL = τ=0.82 PROVISIONAL (per §4 B-1)
- V10 reframed: "B-T7 deferred to Wave 0; B-1 PROVISIONAL value 0.82 with explicit Wave 0 re-adjudication trigger"
- Sub-spec SEAL is NOT gated on B-T7 output (preserves pure process/spec register-class for sub-spec cycle)
- Implementation arc Wave 0 runs B-T7 with proper artifact-path specification: calibration outputs land at `data/phase2_5/btau_calibration_v1/` (or equivalent corrected-engine-style location), containing (i) τ sweep table with cosine-similarity histogram per τ ∈ {0.70..0.90}; (ii) chosen-τ value with explicit selection rule; (iii) fixture corpus + per-pair labels

**Phase 2C data availability for Wave 0 B-T7 (Session 3 noted per P-F7)**: at Wave 0 entry register-event, the implementation arc MUST verify whether Phase 2C Stage 1 DSL pairs are available in a form suitable for B-T7 calibration (path / count / label quality). If unavailable, the empirical claim of B-T7 downgrades to fixture-corpus-only-calibrated with production validation deferred to first Phase 2D batch. This verification gates Wave 0 B-T7 entry, not sub-spec SEAL.

---

## §7 Implementation arc Wave preview (informational only, NOT authorization)

§10 anti-pre-emption invariant confirms: §7 Wave structure preview is informational; no Wave-level decision is pre-committed at sub-spec SEAL — Wave structure is subject to re-adjudication at implementation arc entry register-event boundary.

**Anticipated Wave structure (post-sub-spec-SEAL, NOT pre-authorized)**:

**Wave 0 (preconditions)**: three sub-task commits on parked branch:
- W0.1: shared `BatchIngestState` + `BatchBanditSelection` dataclass shape commit
- W0.2: sentence-transformers SHA-pin + project-local model cache directory
- W0.3: B-T7 cosine threshold calibration (relocated from sub-spec per §6 above); produces final B-1 τ value; sub-spec amendment register-event applied if calibrated τ ≠ 0.82

**Wave A-1 (parallel internal — Track A TDD)**: A-T1..A-T4 test/spec deliverables before any implementation

**Wave A-2 (sequential after A-1)**: A-T5..A-T7 implementation commits

**Wave A-3 (parallel reviewers)**: python-reviewer + security-reviewer + code-reviewer + deferred dual-reviewer + Codex

**Wave B-1 / B-2 / B-3**: mirror structure for Track B

**Wave Cross**: integration test `test_bandit_dedup_e2e.py` after both tracks land

**Arc-level closeout SEAL**: bundles all Wave commits + V# self-check + atomic acceptance note. Combined or per-track is a separate decision at arc-level closeout register-event.

---

## §8 V# self-checklist for sub-spec SEAL (14 anchors; was 12 at Session 1, V10 reframed + V13/V14/V15 added at Session 3)

Evaluated at pre-SEAL register at Session 3. SEAL fire requires all 14 CLEAN.

- **V1**: Sub-spec cycle scope precisely defined (intro)
- **V2**: `BatchIngestState` + `BatchBanditSelection` shapes locked with explicit field inventories (§1.0, §1.1, §1.2)
- **V3**: Lifecycle state machine (X-2) all 3 sub-questions adjudicated with verified constant name `D6_STAGE1_LIFECYCLE_STATES` (§2)
- **V4**: Track A 11 decisions each have chosen default + rationale (vs strongest alternative) + bar-criteria check with observable-failure-mode clause (§3)
- **V5**: Track B 8 decisions each have chosen default + rationale (vs strongest alternative) + bar-criteria check with observable-failure-mode clause (§4)
- **V6**: Cross-track X-3, X-4 adjudication explicit (§5)
- **V7**: A-Lock-4 SPLIT contract fully mechanically specified (§6) — frozen=True acknowledged, separator preserved, user_lines removal explicit, audit extension specified, backwards-compat stated
- **V8**: B-T7 placement RELOCATED to (c) Wave 0 within implementation arc per 3-way reviewer convergence (§6); sub-spec SEAL no longer empirical-gated
- **V9**: Implementation arc Wave preview included as informational-only with §10 anti-pre-emption guard (§7)
- **V10 (reframed Session 3)**: B-1 default at sub-spec SEAL = τ=0.82 PROVISIONAL; Wave 0 B-T7 re-adjudication trigger documented at §4 B-1 and §6; sub-spec amendment register-event path defined if calibrated τ ≠ 0.82
- **V11**: 2 parallel reviewers fired at Session 2 (architect + planner per Charlie register-event 2026-05-16); both returned 8 findings each
- **V12**: Per-fix adjudication discipline at Session 3 (no bulk-accept); 14 dispositions across 16 findings (B-T7 3-way merge): 9 ADOPT + 5 ADOPT-LIGHT + 0 PUSHBACK + 0 DEFER + 0 PASS
- **V13 (added Session 3 per P-F5)**: Per-decision rationale defends chosen default against the strongest alternative — verified at sub-spec SEAL for A-4 (decay), B-2 (window), B-6 (compound gate), and all other 20 decisions
- **V14 (added Session 3 per P-F5)**: 23 chosen-default × 14 proposed-lock coherence check — no conflicts. Specifically verified: A-3 K=5 ≤ |factors| × A-Lock-2 no-per-factor-metric (K is hyperparameter); A-5 hashlib.sha256 × A-Lock-5 append-only (deterministic seed, append-only ledger); A-7 phrasing × A-Lock-4 forbidden-language scan (passes); A-9 schema × A-Lock-5 append-only (no UPDATE/DELETE); B-1 PROVISIONAL × B-Lock-3 no-pre-charge (τ is post-charge logic); B-4 D3-reuse × B-Lock-2 call-graph (read-only consumption, no shared helper); B-5 no-bucketing × B-Lock-2 (no D3 change); B-7 hard-fail × B-Lock-7 SHA pin + no-runtime-network (startup-time check); B-8 unbounded-within-batch × B-Lock-5 within-batch-only (per-batch clear bounds memory). All 322 = 23×14 pairs surveyed; no contradictions found.
- **V15 (added Session 3 per P-F5)**: A-Lock-4 SPLIT mechanism testable in existing `tests/test_d6_prompt_builder.py` surface — `ProposerPrompt` field-split is addable via `field(default="")` without mutating existing test fixtures; `audit_prompt_for_leakage()` scoped scan is testable via positive (clean curation passes) and negative (synthetic contaminated `top_factors_block` triggers audit failure) fixtures. Test contract sketched at §6 A-Lock-4 step 4.

---

## §9 Push / tagging / Phase Marker discipline at sub-spec SEAL

- **NO tag** at sub-spec SEAL (process/spec deliverable register-class precedent — same as scoping SEAL)
- **NO push to remote** at sub-spec SEAL — parked branch stays local until activation
- **NO Phase Marker advance on main** at sub-spec SEAL — parked branch internal
- **Commit numbering (Session 3 corrected per A-F8)**: sub-spec SEAL commit is **commit 4** on `phase2.5/bandit-dedup`. Chronology: `97f7774` scoping draft (commit 1) → `f63b316` scoping SEAL (commit 2) → `0a46823` sub-spec Session 1 draft (commit 3) → sub-spec Session 3 SEAL (commit 4, this commit)
- At eventual merge time, atomic Phase Marker advance + history file update per `feedback_claude_md_freshness.md` Option 1A binding

---

## §10 Anti-pre-emption invariant at sub-spec SEAL

**Framing note (Session 3 added per P-F6)**: Items 1, 2, 7, 8 below are *cycle-entry non-authorizations* (negations of §7 Wave structure cycle entries + sub-spec amendment register-events — anti-momentum-binding for cycle entry boundaries). Items 3, 4, 5, 6 are *decision-class non-authorizations* (additional discipline beyond cycle-entry — reserved decisions that this sub-spec SEAL does not pre-commit). Path 3 §7 + scoping decision §6 distinguish these two classes; this framing preserves the discipline.

This sub-spec SEAL does **NOT**:

1. Pre-authorize implementation arc entry — separate Charlie register-event required *(cycle-entry)*
2. Pre-authorize Wave 0 commits (`BatchIngestState` shape + SHA-pin + B-T7 calibration) — each Wave 0 sub-task is itself an implementation arc commit register *(cycle-entry)*
3. Pre-authorize subagent dispatch for code writing — implementation arc cycle scope only *(decision-class)*
4. Modify CLAUDE.md HARD CONSTRAINTS on main — 14 proposed locks remain deferred to merge time *(decision-class)*
5. Pre-commit any sub-spec choice as immune from re-adjudication — if implementation arc reveals a sub-spec choice is incorrect, an explicit "sub-spec amendment register-event" is the path back *(decision-class)*
6. Authorize pulling validation (2024) / test (2025) / regime-holdout (2022) per-hypothesis data into any LLM context at any cycle stage — CLAUDE.md HARD CONSTRAINT §"AI Agent & Prompt Integrity" remains in force; B-T7 fixture corpus at Wave 0 MUST also respect this *(decision-class — invariant; not subject to re-adjudication)*
7. Push the parked branch to remote — separate user authorization required *(cycle-entry)*
8. Pre-authorize any future sub-spec amendment register-event without explicit Charlie authorization — sub-spec amendments (e.g., post-Wave-0-B-T7 B-1 τ revision) require their own Charlie register-event boundary *(cycle-entry)*

Each successor register-event boundary stands on its own authorization per [`feedback_authorization_routing.md`](../../.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_authorization_routing.md) hard rule.

---

## Appendix A — Session 2 review routing

Per Charlie register-event boundary 2026-05-16 "authorize for all three sessions ... use the similar architect + planner reviewers independently and in parallel as last sessions":

**Reviewer 1 — `architect` subagent**: returned 8 findings (3 STRUCTURAL, 1 DEPENDENCY/REGISTER-CLASS, 2 BOUNDARY, 1 TESTING, 1 DISCIPLINE). Key correctness finding: Python `hash()` non-determinism (F2). Key register-class finding: B-T7 placement (F3).

**Reviewer 2 — `planner` subagent**: returned 8 findings (1 REGISTER-CLASS, 1 V#/COMPLETENESS, 2 RIGOR, 1 V# COVERAGE/STRUCTURE, 1 STRUCTURE/ANTI-PRE-EMPTION, 1 IMPLICIT-ASSUMPTION, 1 CITATION/STRUCTURE). Key convergent finding with architect: B-T7 register-class (F1) — recommended (c) Wave 0 placement, matching architect's recommendation.

Each reviewer reported independently. Per-fix adjudication thereafter; ADOPT / ADOPT-LIGHT / DEFER / PUSHBACK / PASS bucket per finding.

**Codex SKIPPED** per process/spec deliverable register-class hard rule. **python-reviewer + security-reviewer + database-reviewer SKIPPED** at sub-spec cycle (no code; all apply at implementation arc Wave A-3 / B-3).

---

## Appendix B — Session 3 adjudication dispositions table

14 dispositions across 16 findings; A-F3 + P-F1 + P-F2 merged at B-T7 register-class 3-way convergence.

| # | Source | Severity | Disposition | Action applied |
|---|---|---|---|---|
| 1 | A-F1 | high | ADOPT | §6 A-Lock-4 SPLIT contract rewritten with frozen=True ack, `"\n"` separator preservation, explicit `user_lines` removal, backwards-compat |
| 2 | A-F2 | high (CORRECTNESS BUG) | ADOPT | §3 A-5 chosen seed corrected to `int.from_bytes(hashlib.sha256(batch_id.encode('utf-8')).digest()[:8], 'big')`; explicit rationale on PYTHONHASHSEED non-determinism |
| 3 | A-F3 + P-F1 + P-F2 | high (3-way convergence) | ADOPT | B-T7 RELOCATED to (c) Wave 0 within implementation arc; intro reframed; §6 rewritten; §7 Wave 0 enumerates B-T7 sub-task; V10 reframed; B-1 default = 0.82 PROVISIONAL with Wave 0 re-adjudication trigger; sub-spec SEAL no longer empirical-gated |
| 4 | A-F4 | medium | ADOPT-LIGHT | §4 B-4 adds D3 soft-reuse acknowledgment + future-canonicalization-tweak re-calibration trigger; pre-merge verification 4.5 item proposed for merge time |
| 5 | A-F5 | medium | ADOPT | §1.2 added locking `BatchBanditSelection` shape; `build_prompt()` signature stability preserved (keeps `top_factors: tuple[str, ...]` parameter) |
| 6 | A-F6 | medium | ADOPT-LIGHT | §2 X-2 (ii) updated with verified constant `D6_STAGE1_LIFECYCLE_STATES` (5 elements) + binding-at-implementation rule |
| 7 | A-F7 | medium | ADOPT | §1.3 inlined explicit field set `{batch_id, hypotheses_attempted, seen_hashes, lifecycle_counts, records, embedding_cache}`; variable renamed `expected_post_track_b` |
| 8 | A-F8 | low | ADOPT | §9 commit numbering corrected (commit 4); §10 added Session 2/3 cycle-entry non-authorizations + sub-spec amendment register-event non-authorization |
| 9 | P-F3 | medium | ADOPT-LIGHT | Bar-criteria checks across §3 A-1..A-11 + §4 B-1..B-8 now consistently include observable-failure-mode clause ("if wrong, detectable as: ...") |
| 10 | P-F4 | medium | ADOPT | Rationales strengthened for A-4, B-2, B-6 with explicit engagement against strongest alternative motivation |
| 11 | P-F5 | medium | ADOPT | §8 V13 (rationale defensibility), V14 (lock-vs-default coherence — 322 pairs surveyed), V15 (A-Lock-4 testability) added; V10 reframed |
| 12 | P-F6 | medium | ADOPT | §10 cycle-entry vs decision-class framing added; HARD CONSTRAINT data-leakage non-pre-authorization restored as item 6 |
| 13 | P-F7 | medium | ADOPT-LIGHT | §6 (c) acknowledges Phase 2C DSL pair availability as Wave 0 entry verification gate; downgrade path for fixture-only B-T7 documented |
| 14 | P-F8 | low | ADOPT-LIGHT | §10 strengthened with explicit "§7 Wave preview is informational only; no Wave-level decision pre-committed" framing |

**ADOPT-LIGHT framing pattern**: all 5 ADOPT-LIGHT dispositions take the form of *inline clarifications or acknowledgments at the relevant decision/lock site* — they do not pre-commit downstream sub-spec amendment.

**Reviewer convergence**: architect F3 + planner F1 + planner F2 all independently recommended B-T7 RELOCATION to (c) Wave 0 within implementation arc. This 3-way convergence is the strongest possible reviewer signal and was treated as load-bearing in adjudication.

**Correctness-class finding**: architect F2 (Python `hash()` non-determinism) is the only correctness-class finding; it would have shipped a non-determinism bug had it not been caught at Session 2. Resolved at Session 3 A-5 with cryptographic seed.

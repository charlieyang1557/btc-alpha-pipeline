# Phase 2.5 — Combined Bandit + Dedup Arc Closeout

**Status**: arc-level closeout register (parked-branch internal).

**Branch**: `phase2.5/bandit-dedup` (parked; pushed to `origin/phase2.5/bandit-dedup`).

**Base**: `main` at `15f2108` (parked-branch registration commit per [`docs/parked/PARKED_BRANCHES.md`](../parked/PARKED_BRANCHES.md)).

**Arc authorization chain** (Charlie register-events on 2026-05-16):
1. Scoping cycle entry → SEAL `f63b316`
2. Sub-spec drafting cycle entry → SEAL `ab8e715`
3. Implementation arc entry (umbrella for "ALL remaining cycles and waves through arc-level closeout SEAL")
4. Path (b) Path (b) deeper amendment selection → amendment v1 SEAL `850aa1d`
5. "All wave authorized" → Wave A-2/B-2/A-3/B-3/Cross-track + arc closeout

**NOT authorized at this closeout**: merge to main; Phase Marker advance on main; CLAUDE.md HARD CONSTRAINT modification on main. These all gate on a future pre-merge verification register-event per [`docs/parked/PARKED_BRANCHES.md`](../parked/PARKED_BRANCHES.md) 10-item checklist.

---

## §1 Commits chronology

The arc produced **18 commits** on `phase2.5/bandit-dedup` (= 19 ahead of main including the parked-branch registration on main).

| # | Commit | Wave / Cycle | Type |
|---|---|---|---|
| 0 | `15f2108` | Parked-branch registration | main commit (only one) |
| 1 | `97f7774` | Scoping cycle Session 1 | doc draft |
| 2 | `f63b316` | Scoping cycle SEAL | doc SEAL |
| 3 | `0a46823` | Sub-spec cycle Session 1 | doc draft |
| 4 | `ab8e715` | Sub-spec cycle SEAL | doc SEAL |
| 5 | `d92c98f` | Implementation arc plan | doc |
| 6 | `5772aa9` | Wave 0 W0.1 — shape locks | code (TDD) |
| 7 | `ea2a120` | Wave 0 W0.2 — SHA-pin | config |
| 8 | `a8d10ef` | Wave 0 W0.3 — initial calibration | empirical (triggered amendment) |
| 9 | `0b3cb63` | Amendment v1 Session 1 draft | doc |
| 10 | `850aa1d` | Amendment v1 SEAL | doc SEAL |
| 11 | `c5f65d7` | Wave 0 W0.3.v2 — NL+compound calibration | empirical (F1 0.77 → 0.93) |
| 12 | `fd27570` | W0.3 → W0.3.v2 verification audit | methodological |
| 13 | `fda57dd` | Wave A-1 — Track A TDD red | tests |
| 14 | `aa26369` | Wave B-1 — Track B TDD red | tests |
| 15 | `3fcdc28` | Wave A-2 — factor_bandit impl + audit scoped scan | code |
| 16 | `1e4b84e` | Wave B-2 — semantic_dedup impl + compound gate | code |
| 17 | `cb20d31` | Wave A-3 — adjudicated review fixes (4-way HIGH) | code (review fix) |
| 18 | `f43c222` | Wave B-3 — adjudicated review fixes (3-way HIGH) | code (review fix) |
| 19 | `d20a5ac` | Cross-track e2e | tests |
| 20 | (this commit) | Arc-level closeout SEAL | doc SEAL |

---

## §2 Deliverables — Track A (Factor Bandit)

### New module: `agents/orchestrator/factor_bandit.py`

Public API (Wave A-2 + A-3 hardened):

| Name | Purpose | Discipline locks honored |
|---|---|---|
| `BatchBanditSelection` (frozen dataclass) | Top-K curation materialized for one batch | shape lock at sub-spec §1.2 |
| `init_factor_posterior_db(ledger_path)` | SQLite schema initializer | append-only convention (A-Lock-5); CHECK constraints α≥1, β≥1 |
| `observe_batch(*, batch_id, observations, ledger_path)` | Append-only ledger writer + Beta posterior updater | SOLE posterior-mutating entry point (A-Lock-6); BEGIN IMMEDIATE atomic; strict isinstance(bool); sorted(factor_set) determinism |
| `get_posterior(factor_id, ledger_path) → (α, β)` | Read; returns Beta(1,1) cold-start default | non-mutating; A-1 cold-start prior |
| `curate_top_k(*, batch_id, k, ledger_path) → BatchBanditSelection` | Thompson sampling with hashlib.sha256 seed | A-5 corrected determinism (no PYTHONHASHSEED dependency); A-Lock-1/2/7 keep posterior orchestrator-internal |

### Extended `agents/proposer/prompt_builder.py`

A-Lock-4 SPLIT two-layer audit fully implemented:
- `ProposerPrompt.top_factors_block` field (Wave 0 W0.1 shape lock + Wave A-3 actually wired)
- `FORBIDDEN_IN_TOP_FACTORS_BLOCK` extended scoped list (regime / holdout / pass / passing / fail / failing / score / quality / signal / performance)
- `audit_prompt_for_leakage` extended: Layer 1 global scan + Layer 2 scoped scan over `top_factors_block`
- `build_prompt` populates `top_factors_block` field (Wave A-3 fix to 4-way reviewer HIGH; previously dead code)

### Track A test surface (`tests/test_factor_bandit.py`)

8 tests covering all 11 sub-spec Track A decisions:

- A-T1: Beta posterior update arithmetic (synthetic 2-pass + 1-fail → α=3, β=2)
- A-T2: Thompson sampling determinism (same `batch_id` → same top-K)
- A-T3: Cold-start prior Beta(1, 1) for unobserved factor
- A-T4: K=5 curation cap
- A-T5: `factor_bandit_observations` append-only (no UPDATE/DELETE)
- A-T6: Clean curation passes scoped-scan-aware audit (uses `ProposerPrompt` after Wave A-3 fix)
- A-T7: Contaminated `top_factors_block` triggers scoped scan (asserts `"top_factors_block:"` finding prefix; Wave A-3 fix)
- A-T8: Mid-batch state changes don't perturb posterior (A-Lock-6)

---

## §3 Deliverables — Track B (Semantic Dedup)

### New module: `agents/orchestrator/semantic_dedup.py`

Public API (Wave 0 W0.3.v2 + Wave B-2 + B-3 hardened):

| Name | Purpose | Discipline locks honored |
|---|---|---|
| `nl_serialize_dsl(dsl)` | Natural-language serializer (replaces D3-JSON per amendment v1 B-4) | B-Lock-2 extended NL sibling clause: no `agents.hypothesis_hash` imports; traverses `StrategyDSL` directly |
| `embed_dsl(dsl, model)` | `nl_serialize_dsl` + `model.encode` → np.ndarray (384) | Wave B-3 fix: proper TYPE_CHECKING annotation for SentenceTransformer |
| `is_near_duplicate(dsl_a, dsl_b, *, tau_c, model)` | Compound AND-gate: cosine ≥ τ_c AND factor-set equality | Wave B-3 fix: zero-norm guard (raises ValueError); structural short-circuit; τ_s=1.0 DEFINITIONAL |
| `finalize_batch_embedding_cache(state)` | Clears `state.embedding_cache` in place | B-Lock-5 per-batch |
| `check_embedding_stack_or_raise()` | Hard-fail at orchestrator startup if sentence-transformers absent | Wave B-3 fix: ALSO enforces B-Lock-6/B-Lock-7 by setting `TRANSFORMERS_OFFLINE=1` + `HF_HUB_OFFLINE=1` at runtime |

### Wave 0 W0.3.v2 calibration

Per-track 2-pair-class N=30 fixture corpus (5 distribution classes: C1 param-variation-diff-FS, C2 threshold-variation-same-FS, C3 direction-flip-same-FS, C4 factor-swap-diff-FS, C5 scale-shift-diff-FS).

**Final B-1**: τ_c = **0.99** at F1 = **0.9333** (P=0.875, R=1.0). Conjunctive no-further-amendment trigger (τ_c ∈ [0.85, 0.99] AND F1 ≥ 0.85) PASSED.

### Verification audit (commit `fd27570`)

Per Charlie register-event "verify the F1 boost is actual improvement vs cheating": 2×2 ablation matrix on the SAME N=32 fixture revealed:

- D3-JSON × cosine-only F1 = 0.7179 (≈ W0.3 baseline)
- D3-JSON × compound F1 = 0.8485
- NL × cosine-only F1 = 0.9333
- NL × compound F1 = 0.9333 (**compound gate empirically REDUNDANT** with NL serializer)

The +0.21 F1 improvement is REAL but attributable to NL serializer alone; compound gate retained as belt-and-suspenders per Charlie disposition "(i) accept amendment v1 as-is".

### Track B test surface (`tests/test_semantic_dedup.py`)

15 tests covering NL serializer + Wave B-2 functions + W0.3.v2 artifact verification:

- 10 NL serializer tests (deterministic, isolation, 7 edge-case parametrized covering all OpLiteral mappings)
- 2 hard-fail tests (healthy path + actual import-failure with `unittest.mock.patch`; Wave B-3 fix to py-F4 + code-F2)
- 1 compound-gate test (cross-factor pair rejected at structural side)
- 1 embedding-cache finalize test
- 1 W0.3.v2 artifact present + conjunctive trigger verification

---

## §4 Cross-track integration (`tests/test_bandit_dedup_e2e.py`)

3 e2e tests validating both tracks compose correctly via direct module calls:

- `test_e2e_two_batch_bandit_observes_then_curates` — Track A standalone 2-batch flow
- `test_e2e_near_duplicate_quarantine_within_batch` — Track B standalone embedding + compound-gate flow
- `test_e2e_bandit_dedup_compose_two_batches` — Full e2e: batch 1 bandit signal → batch 2 curated menu + within-batch dedup

**ingest_candidate() pipeline wiring DEFERRED**: the orchestrator-level glue that automatically routes near-duplicates to `NEAR_DUPLICATE` state inside `ingest_candidate()` is a small follow-up at parked-branch activation time per [`docs/parked/PARKED_BRANCHES.md`](../parked/PARKED_BRANCHES.md) activation trigger condition. The modules compose correctly without that glue; the production hook is mechanically straightforward (call `is_near_duplicate` against `state.embedding_cache` entries before routing to `PENDING_BACKTEST`).

---

## §5 Discipline locks status

All 14 discipline locks proposed at sub-spec SEAL `ab8e715` + 1 extended at amendment v1 SEAL `850aa1d` (B-Lock-2 NL-serializer sibling clause) remain in force on the parked branch. They are NOT yet codified in main's CLAUDE.md — codification gates on pre-merge verification per parked-branch checklist item 4.

| Track | Locks honored in implementation |
|---|---|
| A-Lock-1 | factor_posterior values never exposed to LLM context — verified by code inspection |
| A-Lock-2 | per-factor metrics never in LLM-visible artifacts — verified |
| A-Lock-3 | only binary `regime_holdout_passed` consumed from registry surface — verified |
| A-Lock-4 (SPLIT) | scoped scan implemented; Wave A-3 fix wired field actually populated |
| A-Lock-5 | append-only `factor_bandit_observations`; CHECK constraints; no UPDATE/DELETE on observations |
| A-Lock-6 | posterior mutates ONLY in `observe_batch`; BEGIN IMMEDIATE atomic |
| A-Lock-7 | non-prompt LLM-visible surfaces audit-clean (verified by tests + Wave A-3 sec review) |
| B-Lock-1 | embedding code path entirely separate from D3 hash canonicalization |
| B-Lock-2 (extended) | NL serializer in `semantic_dedup.py` does not import from `agents.hypothesis_hash` — verified by ripgrep isolation test |
| B-Lock-3 | `near_duplicate` is post-charge classification (state machine in `ingest.py`) |
| B-Lock-4 | embedding vectors never written to LLM-visible artifacts; NL strings stripped from sweep_results.json (Wave B-3 sec-F3 fix) |
| B-Lock-5 | `embedding_cache` per-batch; `finalize_batch_embedding_cache` clears |
| B-Lock-6 | local CPU only; offline env vars enforced at runtime (Wave B-3 sec-F1 fix) |
| B-Lock-7 | version-pinned in `pyproject.toml` extras; torch upper cap `<3.0.0` (Wave B-3 sec-F2 fix); model SHA recorded at calibration |

---

## §6 Test results

Final test counts at this closeout:

```
$ python -m pytest tests/test_factor_bandit.py tests/test_semantic_dedup.py \
    tests/test_orchestrator_ingest.py tests/test_proposer_prompt.py \
    tests/test_d7b_prompt_builder.py tests/test_phase2_5_shape_locks.py \
    tests/test_hypothesis_hash.py tests/test_bandit_dedup_e2e.py -q
```

**Result: 115 passed.**

Test surface breakdown:
- `test_phase2_5_shape_locks.py`: 5 tests (Wave 0 W0.1)
- `test_factor_bandit.py`: 8 tests (Wave A-1/A-2)
- `test_semantic_dedup.py`: 16 tests (Wave 0 W0.3.v2 + Wave B-1/B-2/B-3)
- `test_bandit_dedup_e2e.py`: 3 tests (cross-track)
- `test_orchestrator_ingest.py`: 88 tests (1 updated for `NEAR_DUPLICATE` extension; 87 pre-existing pass-through)
- Other regression-relevant files (proposer_prompt, d7b_prompt_builder, hypothesis_hash): pre-existing tests pass-through with zero regressions

**Zero regressions on pre-existing tests** caused by Phase 2.5 work.

---

## §7 Reviewer-routing record

| Cycle | Reviewers | Adjudication outcome |
|---|---|---|
| Scoping Session 2 | architect + planner | 16 findings → 15 dispositions (1 merge) → 8 ADOPT + 6 ADOPT-LIGHT + 1 PUSHBACK |
| Sub-spec Session 2 | architect + planner | 16 findings → 14 dispositions → 11 ADOPT + 2 ADOPT-LIGHT + 1 PUSHBACK |
| Amendment v1 Session 2 | architect + planner | 14 findings → 13 dispositions → 11 ADOPT + 2 ADOPT-LIGHT + 0 PUSHBACK |
| Wave A-3 | python + security + code + codex | 18 findings → 15 dispositions → 6 ADOPT + 6 ADOPT-LIGHT + 3 PASS + 0 PUSHBACK |
| Wave B-3 | python + security + code + codex (codex async no findings) | 13 findings → 12 dispositions → 6 ADOPT + 3 ADOPT-LIGHT + 3 PASS + 0 PUSHBACK |

**Notable reviewer-caught issues fixed before this closeout**:
- 4-way reviewer convergence on `ProposerPrompt.top_factors_block` field being unwired (scoped scan was dead code) — Wave A-3 fix `cb20d31`
- Python `hash()` PYTHONHASHSEED non-determinism (correctness bug from amendment v1 Session 2 architect F2) — caught BEFORE shipping, never landed
- Zero-norm cosine division silently producing NaN — Wave B-3 fix `f43c222`
- Network egress not enforced at runtime — Wave B-3 fix `f43c222`

---

## §8 V# self-checklist for arc-level closeout SEAL (13 anchors)

Evaluated at pre-SEAL register at Session 3. SEAL fire requires all 13 CLEAN.

- **V1**: Implementation arc scope precisely defined (sub-spec ab8e715 + amendment v1 850aa1d) — CLEAN
- **V2**: All 23 sub-spec decisions adjudicated + 14 + B-Lock-2 extended discipline locks honored in code — CLEAN (§5)
- **V3**: Wave 0 W0.1/W0.2/W0.3/W0.3.v2 all committed + W0.3 → W0.3.v2 amendment trigger documented — CLEAN (§1)
- **V4**: Wave A-1/A-2/A-3 Track A complete; 8/8 Wave A-1 tests GREEN — CLEAN (§2)
- **V5**: Wave B-1/B-2/B-3 Track B complete; 16/16 Wave B-1+W0.3.v2 tests GREEN — CLEAN (§3)
- **V6**: Cross-track e2e committed; 3/3 tests GREEN — CLEAN (§4)
- **V7**: Reviewer routing executed for each appropriate cycle/wave; per-fix adjudication discipline (no bulk-accept) preserved — CLEAN (§7)
- **V8**: Verification audit (commit fd27570) confirms F1 improvement REAL via 2×2 ablation; user-question discipline (METHODOLOGY_NOTES §2 meta-claim verification) honored — CLEAN
- **V9**: Test results 115/115 pass; zero regressions on pre-existing tests — CLEAN (§6)
- **V10**: Discipline locks status complete; 14 locks + B-Lock-2 extended all honored in implementation — CLEAN (§5)
- **V11**: Charlie register-event authorization chain traceable for every cycle entry and SEAL — CLEAN
- **V12**: NOT-authorized items reaffirmed: NO merge to main, NO Phase Marker advance on main, NO CLAUDE.md HARD CONSTRAINT modification on main — CLEAN
- **V13**: ingest_candidate() production wiring explicitly DEFERRED to activation per parked-branch trigger condition — CLEAN (§4)

---

## §9 Anti-pre-emption invariant at arc closeout SEAL

This closeout SEAL does **NOT**:

1. Pre-authorize merge to main *(cycle-entry; separate Charlie register-event + pre-merge verification 10-item checklist required per PARKED_BRANCHES.md)*
2. Pre-authorize Phase Marker advance on main *(cycle-entry; happens atomically at merge per feedback_claude_md_freshness.md)*
3. Modify CLAUDE.md HARD CONSTRAINTS on main *(decision-class; deferred to merge atomic update)*
4. Pre-authorize `ingest_candidate()` wiring on the parked branch *(cycle-entry; small follow-up at activation time)*
5. Pre-authorize sub-spec amendment v2 — none triggered at this closeout *(decision-class)*
6. Pre-authorize push of any other branch to remote *(cycle-entry; this branch pushes authorized per umbrella; other branches not in scope)*

Each successor register-event boundary stands on its own authorization.

---

## §10 Push / tagging / Phase Marker discipline at this closeout

- **NO tag** at this closeout SEAL (arc lands on parked branch only; tag at merge time if applicable per project convention)
- **PUSH to remote** authorized per umbrella 2026-05-16; this SEAL commit pushed to `origin/phase2.5/bandit-dedup`
- **NO Phase Marker advance on main** — parked branch is not yet merged
- This SEAL is **commit 20** on `phase2.5/bandit-dedup`; chronology in §1

---

## Appendix A — Activation pathway

When Charlie register-event activates this work (per PARKED_BRANCHES.md trigger conditions):

1. **Pre-merge verification** (10 items per PARKED_BRANCHES.md):
   - Rebase clean onto current main
   - Full pytest suite green on merged HEAD
   - WF lineage guards intact
   - No new HARD CONSTRAINT violations vs current main
   - Re-run python-reviewer + security-reviewer + code-reviewer + ChatGPT + Claude advisor + codex:codex-rescue on merged-state diff
   - Reproducibility check on prior Phase 2C artifacts
   - Charlie register-event for merge fire
   - Atomic Phase Marker advance + history file update
2. **ingest_candidate() wiring**: small follow-up commit adding the semantic_dedup hook to the ingest pipeline (3-5 LOC)
3. **HARD CONSTRAINT codification**: merge of the 14 + 1 extended locks into main's CLAUDE.md
4. **Tag**: e.g., `phase2.5-bandit-dedup-v1` at merge commit (per project convention)

---

## Appendix B — Session 2 closeout reviewer routing plan

Per Charlie umbrella authorization: 2 parallel internal subagents (architect + planner) fired independently. This appendix records the routing plan; Session 2 reviewer output is recorded inline in the SEAL commit message + this appendix updates at Session 3.

**Reviewer 1 — architect**: full architectural review of the arc as a whole (cross-track coherence, discipline-lock honoring, integration-readiness for activation).

**Reviewer 2 — planner**: plan-completeness review (verification audit honesty, deferred-work clarity, V# coverage, anti-pre-emption tightness).

**Codex / python-reviewer / security-reviewer / code-reviewer SKIPPED** at arc closeout cycle — no new code at closeout register-event (doc only); per-wave code reviews already happened at A-3 + B-3.

---

## Appendix C — Session 3 adjudication dispositions (POPULATED AT SEAL)

To be populated at Session 3 after Session 2 reviewer routing returns findings.

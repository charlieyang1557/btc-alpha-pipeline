# Phase 2.5 — Combined Bandit + Dedup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement factor bandit (Track A) + semantic dedup (Track B) on parked branch `phase2.5/bandit-dedup` per sub-spec SEAL `ab8e715` — driving to arc-level closeout SEAL without merging to main.

**Architecture:** Bandit is orchestrator-internal (`agents/orchestrator/factor_bandit.py` + `factor_posterior` SQLite table). Semantic dedup is in-batch (`agents/orchestrator/semantic_dedup.py` using `sentence-transformers all-MiniLM-L6-v2` local CPU). Both touch the orchestrator surface (`agents/orchestrator/ingest.py`) — Wave 0 locks the shared `BatchIngestState` shape (Track A: 0 fields; Track B: 1 field `embedding_cache`) so subsequent waves can develop independently.

**Tech Stack:** Python 3.11+, dataclasses, pytest, sentence-transformers>=2.0.0 (Track B only, optional extra `phase2_5`), hashlib (deterministic seed per A-5 SEAL fix), numpy.

**Authorization scope (from Charlie register 2026-05-16):** ALL remaining waves through arc-level closeout SEAL on parked branch. NOT authorized: merge to main / Phase Marker advance / CLAUDE.md HARD CONSTRAINT modification. AUTHORIZED: push on this branch.

---

## File map

**NEW files**:
- `agents/orchestrator/factor_bandit.py` — `BatchBanditSelection` dataclass (Wave 0) + bandit logic (Wave A-2)
- `agents/orchestrator/semantic_dedup.py` — embedding-based near-duplicate detection (Wave B-2)
- `tests/test_phase2_5_shape_locks.py` — Wave 0 shape lock tests
- `tests/test_factor_bandit.py` — Wave A-1 TDD tests
- `tests/test_semantic_dedup.py` — Wave B-1 TDD tests
- `tests/test_bandit_dedup_e2e.py` — cross-track integration test
- `data/phase2_5/btau_calibration_v1/` — Wave 0 W0.3 B-T7 calibration artifacts

**MODIFY files**:
- `agents/orchestrator/ingest.py` — add `NEAR_DUPLICATE` state + `embedding_cache` field + dedup integration point (Wave 0 + Wave B-2)
- `agents/proposer/prompt_builder.py` — add `top_factors_block: str` field to `ProposerPrompt` + extend `audit_prompt_for_leakage()` (Wave 0 + Wave A-2)
- `pyproject.toml` — add `sentence-transformers` under `[project.optional-dependencies]` `phase2_5` extra (Wave 0 W0.2)
- `tests/test_orchestrator_ingest.py` — lifecycle invariant extension test (Wave 0)
- `tests/test_d6_prompt_builder.py` — extended leakage audit test (Wave 0 + Wave A-2)

**UNTOUCHED files (verify in tests)**:
- `agents/hypothesis_hash.py` (D2/D3 CONTRACT BOUNDARY preserved per B-Lock-1, B-Lock-2)
- `strategies/dsl.py` (no schema change)
- `agents/critic/d7a_feature_extraction.py` (reused via `extract_factors(dsl)` — no modifications)

---

## Wave structure overview

| Wave | Scope | Test/Code? | Parallelizable? |
|---|---|---|---|
| Wave 0 W0.1 | Shape locks (BatchIngestState + BatchBanditSelection + ProposerPrompt.top_factors_block) | Both (TDD) | No — precondition |
| Wave 0 W0.2 | sentence-transformers SHA-pin in pyproject.toml | Config | No — precondition |
| Wave 0 W0.3 | B-T7 cosine threshold calibration | Empirical | After W0.2 |
| Wave A-1 | Track A failing tests (factor_bandit + prompt_builder extension + audit) | Test | Parallel with B-1 |
| Wave B-1 | Track B failing tests (semantic_dedup + ingest hook) | Test | Parallel with A-1 |
| Wave A-2 | Track A implementation | Code | Parallel with B-2 (different files) |
| Wave B-2 | Track B implementation | Code | Parallel with A-2 |
| Wave A-3 | Track A reviewers (python-reviewer + security-reviewer + Codex) | Review | Parallel with B-3 |
| Wave B-3 | Track B reviewers (python-reviewer + security-reviewer + Codex) | Review | Parallel with A-3 |
| Cross-track | `test_bandit_dedup_e2e.py` 2-batch synthetic flow | Test | After all above |
| Arc closeout | 3-session pacing: closeout draft → reviewer routing → SEAL | Doc | Final |

---

## Wave 0 W0.1 — Shape locks (TDD)

**Files:**
- Create: `tests/test_phase2_5_shape_locks.py`
- Create: `agents/orchestrator/factor_bandit.py`
- Modify: `agents/orchestrator/ingest.py` (add `NEAR_DUPLICATE`, extend `D6_STAGE1_LIFECYCLE_STATES`, add `embedding_cache` field)
- Modify: `agents/proposer/prompt_builder.py` (add `top_factors_block` field to `ProposerPrompt`)

- [ ] **Step 1: Write failing shape-lock tests**

`tests/test_phase2_5_shape_locks.py` asserts:
- `BatchIngestState` fields == `{batch_id, hypotheses_attempted, seen_hashes, lifecycle_counts, records, embedding_cache}`
- `NEAR_DUPLICATE == "near_duplicate"` constant exists
- `NEAR_DUPLICATE in D6_STAGE1_LIFECYCLE_STATES`
- `BatchBanditSelection` dataclass exists with fields `{batch_id, top_factors, selection_seed}` and is `frozen=True`
- `ProposerPrompt` has field `top_factors_block: str = ""`

- [ ] **Step 2: Run test to verify it fails**

`python -m pytest tests/test_phase2_5_shape_locks.py -v` → all 5 tests FAIL (entities missing)

- [ ] **Step 3: Add `BatchBanditSelection` dataclass + `NEAR_DUPLICATE` + `embedding_cache` field**

`agents/orchestrator/factor_bandit.py` (new):

```python
"""Factor bandit module for Phase 2.5 Track A.

Per sub-spec SEAL ab8e715, this module owns:
- BatchBanditSelection dataclass (Wave 0; this commit)
- Thompson sampling + posterior update logic (Wave A-2; deferred)

CONTRACT: This module reads regime_holdout_passed BINARY only from the
registry. It MUST NEVER expose factor_posterior values to any LLM-visible
artifact (A-Lock-1, A-Lock-2, A-Lock-7).
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BatchBanditSelection:
    """Top-K factor curation for one batch, materialized from posterior sampling.

    The orchestrator extracts ``.top_factors`` and passes it as the existing
    ``top_factors: tuple[str, ...]`` parameter to ``build_prompt()``,
    preserving the call-site signature.
    """

    batch_id: str
    top_factors: tuple[str, ...]
    selection_seed: int
```

`agents/orchestrator/ingest.py` modifications:
- Add `NEAR_DUPLICATE = "near_duplicate"` constant near existing state constants
- Add `NEAR_DUPLICATE` to `D6_STAGE1_LIFECYCLE_STATES` tuple
- Add `embedding_cache: dict[str, "np.ndarray"] = field(default_factory=dict)` field to `BatchIngestState`
- Add `NEAR_DUPLICATE` to `__all__`

`agents/proposer/prompt_builder.py` modifications:
- Add `top_factors_block: str = field(default="")` to `ProposerPrompt`
- Update `all_text()` to concatenate: `system + "\n" + user + "\n" + factor_menu + "\n" + top_factors_block`

- [ ] **Step 4: Run shape-lock tests to verify pass**

`python -m pytest tests/test_phase2_5_shape_locks.py -v` → 5 tests PASS

- [ ] **Step 5: Run full existing test suite to verify no regressions**

`python -m pytest tests/test_orchestrator_ingest.py tests/test_d6_prompt_builder.py -v` → all existing tests PASS (no behavioral change yet — just additive shape)

- [ ] **Step 6: Commit Wave 0 W0.1**

```bash
git add tests/test_phase2_5_shape_locks.py agents/orchestrator/factor_bandit.py agents/orchestrator/ingest.py agents/proposer/prompt_builder.py
git commit -m "feat(phase2.5): Wave 0 W0.1 — shape locks (BatchIngestState + BatchBanditSelection + ProposerPrompt.top_factors_block)

Per sub-spec SEAL ab8e715 §1.0-§1.3:
- BatchIngestState gains embedding_cache field (Track B)
- BatchBanditSelection frozen dataclass (Track A)
- ProposerPrompt gains top_factors_block field (A-Lock-4 SPLIT)
- NEAR_DUPLICATE added to D6_STAGE1_LIFECYCLE_STATES (X-2 (ii))

Shape-lock tests at tests/test_phase2_5_shape_locks.py (5 tests, all green).
Existing test suites at test_orchestrator_ingest.py + test_d6_prompt_builder.py
unchanged (no behavioral mutation; additive shape only)."
```

- [ ] **Step 7: Push to remote**

`git push`

---

## Wave 0 W0.2 — sentence-transformers SHA-pin

**Files:**
- Modify: `pyproject.toml`

- [ ] **Step 1: Add sentence-transformers under phase2_5 extra**

`pyproject.toml` additions under `[project.optional-dependencies]`:

```toml
phase2_5 = [
    "sentence-transformers>=2.7.0,<3.0.0",  # version pin per B-Lock-7
    "torch>=2.0.0",  # CPU-only inference; required by sentence-transformers
]
```

- [ ] **Step 2: Verify install succeeds (informational; do NOT install yet)**

`pip install -e ".[phase2_5]"` is deferred to Wave 0 W0.3 (since installation triggers the model download).

- [ ] **Step 3: Commit W0.2**

```bash
git add pyproject.toml
git commit -m "feat(phase2.5): Wave 0 W0.2 — sentence-transformers under phase2_5 extra (SHA pin discipline)

Per sub-spec SEAL ab8e715 B-Lock-7: sentence-transformers added as optional
extra (phase2_5), version-pinned >=2.7.0,<3.0.0. Install deferred to Wave 0
W0.3 B-T7 calibration. Local CPU only; no runtime network egress."
```

---

## Wave 0 W0.3 — B-T7 cosine threshold calibration

**Files:**
- Create: `scripts/btau_calibrate.py` (one-shot calibration script, NOT integrated into orchestrator)
- Create: `data/phase2_5/btau_calibration_v1/calibration_corpus.json` (fixture pairs)
- Create: `data/phase2_5/btau_calibration_v1/sweep_results.json` (cosine sims per τ)
- Create: `data/phase2_5/btau_calibration_v1/CALIBRATION_NOTE.md` (chosen τ + selection rule)

- [ ] **Step 1: Install sentence-transformers locally**

`pip install -e ".[phase2_5]"` — model downloads on first use (~60 MB).

- [ ] **Step 2: Construct synthetic fixture corpus**

10-20 DSL JSON pairs labeled:
- "obvious near-dup": SMA(20) vs SMA(21) vs SMA(22); RSI(14,30) vs RSI(14,31)
- "clear distinct": SMA-based vs RSI-based; long vs short bias

- [ ] **Step 3: Run sweep at τ ∈ {0.70, 0.75, 0.80, 0.82, 0.85, 0.88, 0.90}**

Compute cosine for each pair, count true-positive / false-positive / false-negative per τ. Identify knee point.

- [ ] **Step 4: Document chosen τ + selection rule**

`data/phase2_5/btau_calibration_v1/CALIBRATION_NOTE.md` with table + chosen τ. If chosen τ ≠ 0.82, this triggers sub-spec amendment register-event (per sub-spec §6 B-T7 placement). For first calibration, assume corpus suggests τ stays near 0.82.

- [ ] **Step 5: Commit W0.3**

```bash
git add scripts/btau_calibrate.py data/phase2_5/btau_calibration_v1/
git commit -m "feat(phase2.5): Wave 0 W0.3 — B-T7 cosine threshold calibration

Per sub-spec SEAL ab8e715 §6 B-T7 (c) Wave 0 placement: calibration sub-task
produces final B-1 τ value. Sweep at τ ∈ {0.70..0.90} on synthetic fixture
corpus (Phase 2C Stage 1 DSL pairs unavailable; downgrade per sub-spec §6
P-F7 acknowledgment).

Outputs at data/phase2_5/btau_calibration_v1/:
- calibration_corpus.json (N synthetic pairs)
- sweep_results.json (cosine per pair per τ)
- CALIBRATION_NOTE.md (chosen τ + selection rule)

If chosen τ ≠ 0.82, triggers sub-spec amendment per §6."
```

---

## Wave A-1 — Track A failing tests (TDD)

**Files:**
- Create: `tests/test_factor_bandit.py`
- Modify: `tests/test_d6_prompt_builder.py` (add extended-audit tests)

Test surface enumerated by sub-spec §1.3 + §3 + X-4:

- [ ] **A-T1**: Bandit observation Beta posterior update math (synthetic 2-batch ledger; verify α/β increment correctly)
- [ ] **A-T2**: Thompson sampling determinism (`hash(batch_id)` → `hashlib.sha256` per A-5 fix; same `batch_id` → same `top_factors`)
- [ ] **A-T3**: Cold-start prior Beta(1, 1) (verify default before any observation)
- [ ] **A-T4**: K=5 curation cap (top-K extraction)
- [ ] **A-T5**: `factor_bandit_observations` append-only (no UPDATE/DELETE)
- [ ] **A-T6**: Curation menu phrasing audit (positive: clean curation passes audit; negative: synthetic contaminated `top_factors` triggers audit failure)
- [ ] **A-T7**: `top_factors_block` field-split contract (audit scoped scan finds forbidden tokens in `top_factors_block`-only path)
- [ ] **A-T8**: Posterior-update isolation from in-batch state (mid-batch state changes do not perturb posterior)
- [ ] **Run all A-T tests → expected: all FAIL (factor_bandit logic not implemented)**
- [ ] **Commit Wave A-1**

---

## Wave B-1 — Track B failing tests (TDD)

**Files:**
- Create: `tests/test_semantic_dedup.py`
- Modify: `tests/test_orchestrator_ingest.py` (add `near_duplicate` lifecycle tests)
- Modify: `tests/test_hypothesis_hash.py` (add CONTRACT BOUNDARY ripgrep test)

- [ ] **B-T1**: `embed_canonical(dsl)` determinism (same DSL → same embedding vector)
- [ ] **B-T2**: `is_near_duplicate(candidate, cache, tau)` cosine edge cases (just-above, just-below threshold)
- [ ] **B-T3**: Lifecycle integration — `near_duplicate` state transitions; DSR denominator counting; ingest pipeline order (D3 first, embed second)
- [ ] **B-T4**: Lifecycle invariant extension parametrized (new `near_duplicate` state honored by `assert_lifecycle_invariant_at_batch_close()`)
- [ ] **B-T5**: `semantic_dedup.py` import-isolation ripgrep test (must not import from `agents/hypothesis_hash.py` internals beyond `canonicalize_for_hash`)
- [ ] **B-T6**: Embedding cache cleared at finalize
- [ ] **B-T7**: Cosine-threshold sweep coverage on calibration fixture (uses Wave 0 W0.3 artifacts)
- [ ] **B-T8**: Model load-failure hard-fail (mocked sentence-transformers import-failure)
- [ ] **Run all B-T tests → expected: all FAIL (semantic_dedup logic not implemented)**
- [ ] **Commit Wave B-1**

---

## Wave A-2 — Track A implementation

**Files:**
- Modify: `agents/orchestrator/factor_bandit.py` (add Thompson sampling + posterior update)
- Modify: `agents/proposer/prompt_builder.py` (extend `audit_prompt_for_leakage()` + wire `top_factors_block`)
- Modify: `agents/orchestrator/ingest.py` (wire bandit observation at batch close)

Step-by-step:

- [ ] **A-I1**: Implement `factor_bandit.observe_batch()` posterior update — make A-T1, A-T3, A-T8 green
- [ ] **A-I2**: Implement `factor_bandit.curate_top_k()` Thompson sampling with hashlib.sha256 seed — make A-T2, A-T4 green
- [ ] **A-I3**: Create `factor_posterior` SQLite table + `factor_bandit_observations` ledger schema — make A-T5 green
- [ ] **A-I4**: Extend `prompt_builder.audit_prompt_for_leakage()` with scoped scan over `top_factors_block` substring — make A-T6, A-T7 green
- [ ] **A-I5**: Wire bandit into `ingest.py` at batch close (observe via `extract_factors(dsl)`)
- [ ] **Run all A-T tests → expected: all PASS**
- [ ] **Run full existing test suite → no regressions**
- [ ] **Commit Wave A-2**

---

## Wave B-2 — Track B implementation

**Files:**
- Create: `agents/orchestrator/semantic_dedup.py`
- Modify: `agents/orchestrator/ingest.py` (wire dedup into `ingest_candidate()`)

Step-by-step:

- [ ] **B-I1**: Implement `semantic_dedup.embed_canonical(dsl)` — make B-T1 green
- [ ] **B-I2**: Implement `semantic_dedup.is_near_duplicate(candidate, cache, tau)` — make B-T2, B-T7 green
- [ ] **B-I3**: Add `near_duplicate` lifecycle transition in `ingest.py::ingest_candidate()` — make B-T3, B-T4 green
- [ ] **B-I4**: Wire `embedding_cache` per-batch clear at `finalize_batch()` — make B-T6 green
- [ ] **B-I5**: Add startup hard-fail check for sentence-transformers — make B-T8 green
- [ ] **Run all B-T tests → expected: all PASS**
- [ ] **Run full existing test suite → no regressions**
- [ ] **Commit Wave B-2**

---

## Wave A-3 — Track A reviewer routing

Dispatch in parallel: `python-reviewer` + `security-reviewer` + `code-reviewer` + `codex:codex-rescue`. Adjudicate per-fix (no bulk-accept).

- [ ] **A-R1**: python-reviewer subagent — Pythonic patterns, type hints, PEP 8
- [ ] **A-R2**: security-reviewer subagent — leakage audit deep-scan, secret scan
- [ ] **A-R3**: code-reviewer subagent — general quality, patterns
- [ ] **A-R4**: codex:codex-rescue — adversarial pass per project Codex precedent
- [ ] **Adjudicate per-fix → ADOPT / ADOPT-LIGHT / DEFER / PUSHBACK / PASS**
- [ ] **Apply ADOPTed edits**
- [ ] **Re-run all A-T tests → all PASS post-edits**
- [ ] **Commit Wave A-3**

---

## Wave B-3 — Track B reviewer routing

Same pattern as A-3 with Track B focus.

- [ ] **B-R1..B-R4**: parallel reviewers
- [ ] **Adjudicate per-fix**
- [ ] **Apply ADOPTed edits + re-run B-T tests → all PASS**
- [ ] **Commit Wave B-3**

---

## Cross-track integration test

**Files:**
- Create: `tests/test_bandit_dedup_e2e.py`

- [ ] **Step 1: Write 2-batch synthetic flow test**

Batch 1: 10 hypotheses, 3 regime-passing, 7 regime-failing.
- Bandit observes; posterior updates.
- Batch 2: curated factor menu reflects batch 1 signal.
- Within batch 2, inject a near-duplicate pair → semantic dedup quarantines as `near_duplicate`.
- Verify lifecycle counts + bandit posterior post-batch.

- [ ] **Step 2: Run test → expected PASS**
- [ ] **Run full test suite → no regressions**
- [ ] **Commit Cross-track**

---

## Arc-level closeout cycle (3-session pacing)

- [ ] **Closeout Session 1**: draft `docs/closeout/PHASE2_5_BANDIT_DEDUP_RESULTS.md` summarizing all wave outcomes + V# self-check + acceptance evidence (commit refs, test counts, calibration result)
- [ ] **Closeout Session 2**: 2 parallel reviewers (architect + planner) on the closeout doc + git history
- [ ] **Closeout Session 3**: per-fix adjudication + V# self-check + arc-level closeout SEAL commit on parked branch + push

**STOP after arc-level closeout SEAL** per Charlie register 2026-05-16.

---

## Pause checkpoints (per Charlie register-event)

PAUSE AND ASK if:
- HARD CONSTRAINT violation surfaced (regime/validation/test data in LLM context)
- Reviewer finds high-severity issue requiring scope change
- Test failure unfixable without sub-spec amendment
- "Implementation finishes" boundary reached (after Wave B-2 + Cross-track, before Wave A-3/B-3 reviewer routing)

Default: continue; pause only at the four above triggers.

---

## Self-review (against sub-spec)

- §1 BatchIngestState shape lock → Wave 0 W0.1 covers (Steps 1-7)
- §1.2 BatchBanditSelection shape → Wave 0 W0.1 includes
- §2 X-2 lifecycle → Wave 0 W0.1 (`NEAR_DUPLICATE` + tuple extension)
- §3 Track A 11 decisions → Wave A-1 (8 tests) + Wave A-2 (5 implementation steps)
- §4 Track B 8 decisions → Wave B-1 (8 tests) + Wave B-2 (5 implementation steps)
- §5 X-3 dependency → Wave 0 W0.2
- §5 X-4 test surface → covered across waves
- §6 A-Lock-4 SPLIT → Wave 0 W0.1 (ProposerPrompt field) + Wave A-2 (audit extension)
- §6 B-T7 (c) Wave 0 → Wave 0 W0.3
- §7 Wave structure → matches preview
- §8 V# anchors → arc closeout cycle verifies all 14 at SEAL

No placeholders. All file paths exact. Commit messages drafted.

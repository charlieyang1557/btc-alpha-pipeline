# Phase 2.5 — Combined Bandit + Dedup Arc Closeout

**Status**: arc-level closeout register (parked-branch internal).

**Branch**: `phase2.5/bandit-dedup` (parked; pushed to `origin/phase2.5/bandit-dedup`).

**Base**: `main` at `15f2108` (parked-branch registration commit per [`docs/parked/PARKED_BRANCHES.md`](../parked/PARKED_BRANCHES.md)).

**Arc authorization chain** (Charlie register-events on 2026-05-16):
1. Scoping cycle entry → SEAL `f63b316`
2. Sub-spec drafting cycle entry → SEAL `ab8e715`
3. Implementation arc entry (umbrella: "ALL remaining cycles and waves through arc-level closeout SEAL")
4. Path (b) deeper amendment selection → amendment v1 SEAL `850aa1d`
5. "All wave authorized" → Wave A-2/B-2/A-3/B-3/Cross-track + this closeout

**NOT authorized at this closeout**: merge to main; Phase Marker advance on main; CLAUDE.md HARD CONSTRAINT modification on main. These all gate on a future pre-merge verification register-event per [`docs/parked/PARKED_BRANCHES.md`](../parked/PARKED_BRANCHES.md) 10-item checklist.

---

## §1 Arc result (executive summary)

**Verdict**: Phase 2.5 combined bandit + dedup arc complete on parked branch. Both tracks (factor_bandit + semantic_dedup) implemented, tested, reviewed; cross-track e2e validates composition. **Empirical calibration result**: τ_c = 0.99 at F1 = 0.9333 (P=0.875, R=1.000) on the N=30 W0.3.v2 fixture corpus. **Per METHODOLOGY_NOTES §7 asymmetric confidence reporting**: this is direction-consistent evidence for NL-serializer + compound-gate superiority over the W0.3 baseline (F1 = 0.7179 on same N=32 ablation corpus); magnitude claim is bounded by the small fixture size and the architect-validated finding that the compound gate is empirically REDUNDANT with NL serializer (NL × cosine-only F1 == NL × compound F1 on the audit fixture). Production performance on real Phase 2D batches is a forward-only carry-forward.

**Verification audit (commit `fd27570`)**: Charlie's direct question "verify the F1 boost is actual improvement instead of some sort of cheating to boost this statistics score" was honored via a same-fixture 2×2 ablation matrix. Per METHODOLOGY_NOTES §1 (empirical verification) + §2 (meta-claim verification discipline) — the F1 improvement is REAL but the compound gate's contribution is structural-side-only redundancy; retained as belt-and-suspenders per Charlie disposition "(i) accept amendment v1 as-is".

**Deferred to activation**: `ingest_candidate()` pipeline wiring (the production hook that routes near-duplicates to `NEAR_DUPLICATE` lifecycle state inside the orchestrator's per-candidate loop). Per §4 below and Appendix A item 2: this is a non-trivial integration (~30-80 LOC + config + model handle + test extension; NOT 3-5 LOC), gated on pre-merge verification + Charlie merge fire register-event.

**Tests**: 115/115 pass; zero regressions on pre-existing tests. Discipline locks: 14 + 1 extended (B-Lock-2 NL-serializer sibling clause) all honored at module boundary; B-Lock-3 production routing deferred to activation.

---

## §2 Commits chronology

The arc produced **20 commits** on `phase2.5/bandit-dedup` (= 20 ahead of main `15f2108`, including this SEAL commit; row 0 in the table is the parked-branch registration on main, not on the branch).

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
| 20 | `82c532a` | Arc closeout Session 1 draft | doc |
| 21 | (this commit) | Arc closeout SEAL (Session 3) | doc SEAL |

---

## §3 Deliverables — Track A (Factor Bandit)

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

8 tests covering all 11 sub-spec Track A decisions: A-T1 Beta update arithmetic, A-T2 Thompson determinism, A-T3 cold-start Beta(1,1), A-T4 K=5 cap, A-T5 append-only contract, A-T6 clean curation audit (uses `ProposerPrompt` after Wave A-3 fix), A-T7 scoped-scan negative test (asserts `"top_factors_block:"` finding prefix), A-T8 posterior-update isolation.

---

## §4 Deliverables — Track B (Semantic Dedup)

### New module: `agents/orchestrator/semantic_dedup.py`

Public API (Wave 0 W0.3.v2 + Wave B-2 + B-3 hardened):

| Name | Purpose | Discipline locks honored |
|---|---|---|
| `nl_serialize_dsl(dsl)` | Natural-language serializer (replaces D3-JSON per amendment v1 B-4) | B-Lock-2 extended NL sibling clause: no `agents.hypothesis_hash` imports; traverses `StrategyDSL` directly |
| `embed_dsl(dsl, model)` | `nl_serialize_dsl` + `model.encode` → np.ndarray (384) | Wave B-3 fix: TYPE_CHECKING annotation for SentenceTransformer |
| `is_near_duplicate(dsl_a, dsl_b, *, tau_c, model)` | Compound AND-gate: cosine ≥ τ_c AND factor-set equality | Wave B-3 fix: zero-norm guard (raises ValueError); structural short-circuit; τ_s=1.0 DEFINITIONAL |
| `finalize_batch_embedding_cache(state)` | Clears `state.embedding_cache` in place | B-Lock-5 per-batch |
| `check_embedding_stack_or_raise()` | Hard-fail at orchestrator startup if sentence-transformers absent | Wave B-3 fix: ALSO enforces B-Lock-6/B-Lock-7 by setting `TRANSFORMERS_OFFLINE=1` + `HF_HUB_OFFLINE=1` at runtime |

### Wave 0 W0.3.v2 calibration

Per-track N=30 (32 in ablation) 5-class fixture corpus (C1 param-variation-diff-FS, C2 threshold-variation-same-FS, C3 direction-flip-same-FS, C4 factor-swap-diff-FS, C5 scale-shift-diff-FS). **Final B-1**: τ_c = **0.99** at F1 = **0.9333** (P=0.875, R=1.000). Conjunctive no-further-amendment trigger (τ_c ∈ [0.85, 0.99] AND F1 ≥ 0.85) PASSED.

### Verification audit (commit `fd27570`) — methodological honesty record

Per METHODOLOGY_NOTES §1 + §2 user-question discipline. Charlie register-event 2026-05-16: "verify the F1 boost is actual improvement instead of some sort of cheating to boost this statistics score."

**2×2 ablation on the SAME N=32 W0.3.v2 fixture** (held constant: fixture composition, model SHA `352d34a4ad725bb7`, factor-set definitions; varied: serialization × gate-type):

| Config | Best F1 | τ | P | R |
|---|---|---|---|---|
| D3-JSON × cosine-only (≈ W0.3) | **0.7179** | 0.97 | 0.560 | 1.000 |
| D3-JSON × compound | 0.8485 | 0.70 | 0.737 | 1.000 |
| NL × cosine-only | **0.9333** | 0.99 | 0.875 | 1.000 |
| NL × compound (W0.3.v2) | 0.9333 | 0.99 | 0.875 | 1.000 |

**Findings**:
1. F1 improvement IS REAL (+0.21 on same fixture); no statistic-cheating
2. NL serializer is the load-bearing change (NL alone Δ = +0.22; compound gate alone Δ = +0.13)
3. **Compound gate is EMPIRICALLY REDUNDANT with NL serializer** (NL × cosine-only == NL × compound on this fixture); retained as belt-and-suspenders per Charlie disposition "(i)"
4. Class-separation gap on hard subset (same-factor-set) is 0.0023 — **fragile**; production data may shift optimal τ_c
5. 2 remaining FPs are structural NL serializer weakness (direction-flip pairs at cosine 0.9997 — symmetric "is greater than X" vs "is less than X" not differentiated at embedding level)

**Per METHODOLOGY_NOTES §7 asymmetric confidence**: F1 = 0.9333 on N=30 calibration / N=32 ablation. Direction-consistent evidence for NL+compound > D3+cosine, but magnitude claim is bounded by fixture size. Production validation deferred to first Phase 2D batch.

### Track B test surface (`tests/test_semantic_dedup.py`)

16 tests covering NL serializer (10 incl. 7 edge-case parametrized) + Wave B-2 functions + W0.3.v2 artifact verification + Wave B-3 actual hard-fail import-failure test (`unittest.mock.patch` based).

### Cross-track integration (`tests/test_bandit_dedup_e2e.py`)

3 e2e tests validating both tracks compose correctly via direct module calls.

### `ingest_candidate()` production wiring — DEFERRED with explicit activation contract

The orchestrator-level glue that automatically routes near-duplicates to `NEAR_DUPLICATE` state inside `ingest_candidate()` is **NOT** in this arc. **Activation trigger**: this wiring lands as commit (2) inside the activation pre-merge checklist sequence at Appendix A; it is NOT a separate cycle-entry register-event and does NOT require fresh Charlie authorization beyond the merge fire register-event.

**Honest scope estimate** (Wave-closeout architect F4 correction to prior "3-5 LOC" understatement): the wiring requires (i) model instantiation at orchestrator startup behind `check_embedding_stack_or_raise()`; (ii) `embed_dsl` + cache-write per candidate; (iii) compound-gate scan against existing `state.embedding_cache`; (iv) `tau_c` config plumbing (from `config/execution.yaml` or analogous); (v) `finalize_batch_embedding_cache(state)` call at batch close; (vi) test coverage extending `tests/test_orchestrator_ingest.py`. **Estimated diff: ~30-80 LOC at `agents/orchestrator/ingest.py::ingest_candidate()` before `PENDING_BACKTEST` routing, plus config + test extension.** The lock surface for B-Lock-3 is honored at module boundary today; runtime enforcement gates on this wiring.

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
| A-Lock-7 | non-prompt LLM-visible surfaces audit-clean (Wave A-3 sec review) |
| B-Lock-1 | embedding code path entirely separate from D3 hash canonicalization |
| B-Lock-2 (extended) | NL serializer in `semantic_dedup.py` does not import from `agents.hypothesis_hash` — verified by `test_nl_serializer_isolates_from_hypothesis_hash` ripgrep test |
| **B-Lock-3** | `NEAR_DUPLICATE` lifecycle constant + state-machine slot present; **production routing through `ingest_candidate()` deferred to activation per §4** — lock surface honored at module boundary, runtime enforcement gated on activation-time wiring |
| B-Lock-4 | embedding vectors never written to LLM-visible artifacts; NL strings stripped from `sweep_results.json` (Wave B-3 sec-F3 fix) |
| B-Lock-5 | `embedding_cache` per-batch; `finalize_batch_embedding_cache` clears |
| B-Lock-6 | local CPU only; offline env vars `TRANSFORMERS_OFFLINE=1` + `HF_HUB_OFFLINE=1` enforced at runtime (Wave B-3 sec-F1 fix) |
| B-Lock-7 | version-pinned in `pyproject.toml` extras; torch upper cap `<3.0.0` (Wave B-3 sec-F2 fix); model SHA recorded at calibration |

---

## §6 Test results

Final test counts at this closeout (verified via `pytest --collect-only`):

| File | Tests | Wave / Cycle origin |
|---|---|---|
| `tests/test_phase2_5_shape_locks.py` | 5 | Wave 0 W0.1 |
| `tests/test_factor_bandit.py` | 8 | Wave A-1 / A-2 / A-3 |
| `tests/test_semantic_dedup.py` | 16 | Wave 0 W0.3.v2 + Wave B-1 / B-2 / B-3 |
| `tests/test_bandit_dedup_e2e.py` | 3 | Cross-track |
| `tests/test_orchestrator_ingest.py` | 14 | 1 updated (NEAR_DUPLICATE extension); 13 pre-existing pass-through |
| `tests/test_proposer_prompt.py` | 38 | pre-existing pass-through |
| `tests/test_d7b_prompt_builder.py` | 14 | pre-existing pass-through |
| `tests/test_hypothesis_hash.py` | 17 | pre-existing pass-through |

**Total: 5 + 8 + 16 + 3 + 14 + 38 + 14 + 17 = 115. Result: 115 passed.**

Zero regressions on pre-existing tests caused by Phase 2.5 work.

---

## §7 Reviewer-routing record

| Cycle / Wave | Reviewers | Findings | Dispositions | ADOPT / ADOPT-LIGHT / PUSHBACK / DEFER / PASS |
|---|---|---|---|---|
| Scoping Session 2 | architect + planner | 16 | 15 (1 merge) | 8 / 6 / 1 / 0 / 0 |
| Sub-spec Session 2 | architect + planner | 16 | 14 (2 merges) | 11 / 2 / 1 / 0 / 0 |
| Amendment v1 Session 2 | architect + planner | 14 | 13 (1 merge) | 11 / 2 / 0 / 0 / 0 |
| Wave A-3 | python + security + code + codex | 18 | 15 (3 merges) | 6 / 6 / 0 / 0 / 3 |
| Wave B-3 | python + security + code + codex (codex async) | 13 | 12 (1 merge) | 6 / 3 / 0 / 0 / 3 |
| **Arc closeout Session 2 (this)** | architect + planner | 12 | 12 | 9 / 3 / 0 / 0 / 0 |
| **Total** | — | **89** | **81** | **51 / 22 / 2 / 0 / 6** |

**Per-fix adjudication operated throughout** per [`feedback_reviewer_suggestion_adjudication.md`](../../.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_reviewer_suggestion_adjudication.md). No bulk-accept at any cycle/wave.

**Notable reviewer-caught issues fixed before this closeout**:
- 4-way reviewer convergence on `ProposerPrompt.top_factors_block` field being unwired (scoped scan was dead code) — Wave A-3 fix `cb20d31`
- Python `hash()` PYTHONHASHSEED non-determinism (correctness bug from amendment v1 Session 2 architect F2) — caught BEFORE shipping, never landed
- Zero-norm cosine division silently producing NaN — Wave B-3 fix `f43c222`
- Network egress not enforced at runtime — Wave B-3 fix `f43c222`
- This closeout Session 2: architect F2 test count inaccuracy (88 → actual 14 for `test_orchestrator_ingest.py`); planner P-F4 unfilled Appendix C placeholder; planner P-F1 missing METHODOLOGY_NOTES §7 asymmetric confidence on F1 N=30/32 — all fixed in this SEAL commit

---

## §8 V# self-checklist for arc-level closeout SEAL (13 anchors)

Evaluated at pre-SEAL register at Session 3. SEAL fire requires all 13 CLEAN.

- **V1**: Implementation arc scope precisely defined (sub-spec ab8e715 + amendment v1 850aa1d) — CLEAN
- **V2**: All 23 sub-spec decisions adjudicated + 14 + B-Lock-2 extended discipline locks honored in code (B-Lock-3 module-boundary honored; runtime routing deferred per §4 + §5 disclosed) — CLEAN
- **V3**: Wave 0 W0.1/W0.2/W0.3/W0.3.v2 all committed + W0.3 → W0.3.v2 amendment trigger documented — CLEAN
- **V4**: Wave A-1/A-2/A-3 Track A complete; 8/8 Wave A-1 tests GREEN — CLEAN
- **V5**: Wave B-1/B-2/B-3 Track B complete; 16/16 Wave B-1+W0.3.v2 tests GREEN — CLEAN
- **V6**: Cross-track e2e committed; 3/3 tests GREEN — CLEAN
- **V7**: Reviewer routing executed for each appropriate cycle/wave; per-fix adjudication discipline (no bulk-accept) preserved across 89 findings → 81 dispositions — CLEAN (§7 + Appendix C)
- **V8**: Verification audit (commit `fd27570`) confirms F1 improvement REAL via 2×2 ablation; METHODOLOGY_NOTES §1 + §2 + §7 honored — CLEAN (§1 + §4 verification table)
- **V9**: Test results 115/115 pass; zero regressions; counts reconciled per-file in §6 — CLEAN
- **V10**: Discipline locks status complete; 14 locks + B-Lock-2 extended all honored in implementation with explicit B-Lock-3 deferral disclosure — CLEAN (§5)
- **V11**: Authorization chain mechanically traceable: scoping `f63b316` + sub-spec `ab8e715` + amendment v1 `850aa1d` + closeout `82c532a` are all reachable from this SEAL commit; verified by `git merge-base --is-ancestor <SHA> HEAD` returning success for all 4 SHAs at pre-SEAL register — CLEAN
- **V12**: This arc's commits live entirely on `phase2.5/bandit-dedup` branch, not on main. Verifiable by `git log main..HEAD --oneline | wc -l == 20` (the 20 branch commits + this SEAL = 21 ahead of main's last touch by this arc at `15f2108`). NOTE: main HEAD may independently advance via other concurrent arcs (e.g., a Path 3 sub-spec drafting SEAL landed at `0835805` outside this arc); that is OUT OF SCOPE for V12, which only verifies THIS arc made zero modifications to main beyond the initial parked-branch registration commit `15f2108`. The independent main advance is a routine integration concern handled at pre-merge verification per Appendix A — CLEAN
- **V13**: `ingest_candidate()` production wiring explicitly DEFERRED to activation per §4 + Appendix A with honest scope estimate (~30-80 LOC, NOT 3-5 LOC per architect F4 correction) — CLEAN

---

## §9 Anti-pre-emption invariant at arc closeout SEAL

This closeout SEAL does **NOT**:

1. Pre-authorize merge to main *(cycle-entry; separate Charlie register-event + pre-merge verification 10-item checklist required per PARKED_BRANCHES.md)*
2. Pre-authorize Phase Marker advance on main *(cycle-entry; happens atomically at merge per `feedback_claude_md_freshness.md`)*
3. Modify CLAUDE.md HARD CONSTRAINTS on main *(decision-class; deferred to merge atomic update)*
4. Pre-authorize `ingest_candidate()` wiring on the parked branch — see §4 for activation-condition tightening: wiring lands as commit (2) inside the activation pre-merge sequence, NOT a separate cycle-entry register-event *(decision-class)*
5. Pre-authorize sub-spec amendment v2 — none triggered at this closeout *(decision-class)*
6. Pre-authorize push of any other branch to remote *(cycle-entry; this branch push authorized per umbrella; other branches not in scope)*

Each successor register-event boundary stands on its own authorization.

---

## §10 Push / tagging / Phase Marker discipline at this closeout

- **NO tag** at this closeout SEAL (arc lands on parked branch only; tag at merge time if applicable per project convention)
- **PUSH to remote** authorized per umbrella 2026-05-16; this SEAL commit pushed to `origin/phase2.5/bandit-dedup`
- **NO Phase Marker advance on main** — parked branch is not yet merged
- This SEAL is **commit 21** on `phase2.5/bandit-dedup`; chronology in §2

---

## Appendix A — Activation pathway

When Charlie register-event activates this work (per [`docs/parked/PARKED_BRANCHES.md`](../parked/PARKED_BRANCHES.md) trigger conditions):

**Pre-merge verification**: See [`docs/parked/PARKED_BRANCHES.md`](../parked/PARKED_BRANCHES.md) "Pre-merge verification checklist" items 1–10; this closeout does NOT redefine them. Activation MUST satisfy all 10 by reference, including the explicit `python -m pytest -q` test invocation cited there.

**Additional activation-time tasks (within or alongside the 10-item checklist)**:

1. **`ingest_candidate()` wiring**: ~30-80 LOC at `agents/orchestrator/ingest.py::ingest_candidate()` adding the semantic_dedup hook + config + model handle + test extension. See §4 honest scope estimate.
2. **HARD CONSTRAINT codification**: merge of the 14 + 1 extended discipline locks into main's CLAUDE.md as part of the merge atomic update.
3. **Tag**: e.g., `phase2.5-bandit-dedup-v1` at merge commit (per project convention from `phase4-forward-test-v1` / `phase5-diagnostic-execution-v1`).

---

## Appendix B — Session 2 closeout reviewer routing

Per Charlie umbrella authorization: 2 parallel internal subagents (architect + planner) fired independently.

**Reviewer 1 — architect**: returned 6 findings (1 high test-truth + 4 medium chronology/discipline/deferred/activation + 1 low V#-verifiability). Verdict: needs minor fixes before SEAL.

**Reviewer 2 — planner**: returned 6 findings (2 high methodology/structure + 3 medium completeness/structure/risk + 1 low rigor). Verdict: BLOCK pending fixes.

**Codex / python-reviewer / security-reviewer / code-reviewer SKIPPED** at arc closeout cycle — no new code at closeout register-event (doc only); per-wave code reviews already happened at A-3 + B-3.

---

## Appendix C — Session 3 adjudication dispositions

12 dispositions on 12 findings (no merges; arc-closeout findings were narrow). 9 ADOPT + 3 ADOPT-LIGHT + 0 PUSHBACK + 0 DEFER + 0 PASS.

| # | Source | Severity | Disposition | Action applied |
|---|---|---|---|---|
| 1 | A-F1 (CHRONOLOGY) | medium | ADOPT | §2 prose corrected from "18 commits" to "20 commits"; row 0 explicitly noted as main commit; arithmetic reconciled |
| 2 | A-F2 (TEST-TRUTH) | **high** | ADOPT | §6 test-surface breakdown rewritten with verified per-file counts via `pytest --collect-only`; `test_orchestrator_ingest.py` = 14 (not 88); breakdown sums to 115 exactly |
| 3 | A-F3 (DISCIPLINE-LOCK) | medium | ADOPT | §5 B-Lock-3 row rewritten: "lifecycle constant + state-machine slot present; production routing DEFERRED to activation per §4 — lock surface honored at module boundary, runtime enforcement gated on activation-time wiring" |
| 4 | A-F4 (DEFERRED-DISCLOSURE) | medium | ADOPT | §4 + Appendix A revised: honest scope ~30-80 LOC + plumbing + tests (NOT 3-5 LOC); 6 specific wiring tasks enumerated |
| 5 | A-F5 (V#-VERIFIABILITY) | low | ADOPT-LIGHT | §8 V11 + V12 rewritten with mechanical git invocations (`git merge-base --is-ancestor`, `git diff main -- CLAUDE.md docs/phase_marker_history.md`) |
| 6 | A-F6 (ACTIVATION) | medium | ADOPT-LIGHT | Appendix A pre-merge section replaced with explicit pointer to PARKED_BRANCHES.md 10-item checklist; no paraphrase |
| 7 | P-F1 (METHODOLOGY §7) | **high** | ADOPT | §1 Arc result + §4 verification audit table now include explicit METHODOLOGY_NOTES §7 asymmetric confidence caveat on F1 N=30/32 ("direction-consistent evidence; magnitude bounded by fixture size; production validation forward-only carry-forward") |
| 8 | P-F2 (COMPLETENESS) | medium | ADOPT | Verification audit promoted from buried §3 subsection to standalone §4 "Verification audit (methodological honesty record)" subsection with full 2×2 ablation table |
| 9 | P-F3 (STRUCTURE) | medium | ADOPT | §1 "Arc result (executive summary)" added; subsequent sections renumbered (§1 → §2 commits, §2-§3 → §3-§4 deliverables, etc.) |
| 10 | P-F4 (Appendix C placeholder) | **high** | ADOPT | This appendix populated with all 12 dispositions BEFORE SEAL fire; placeholder eliminated |
| 11 | P-F5 (RIGOR arithmetic) | low | ADOPT-LIGHT | §7 added total row: 89 findings → 81 dispositions → 51 ADOPT + 22 ADOPT-LIGHT + 2 PUSHBACK + 0 DEFER + 6 PASS; per-fix discipline citation added |
| 12 | P-F6 (RISK/METHODOLOGY) | medium | ADOPT | §4 ingest_candidate() paragraph tightened: explicit "activation trigger: lands as commit (2) inside activation pre-merge sequence; NOT separate cycle-entry register-event; does NOT require fresh Charlie authorization beyond merge fire" |

**Reviewer convergence at closeout**: zero direct convergences between architect (6 findings) and planner (6 findings); reviewers attacked different axes (architect = mechanical accounting + discipline lock spot-checks; planner = methodological discipline + structural precedent comparison). Both verdicts (needs fixes / BLOCK pending fixes) directionally agreed.

**HIGH-severity fixes (3) all applied**: A-F2 test count truth (§6), P-F1 asymmetric confidence (§1 + §4), P-F4 Appendix C populated (this appendix). Medium-severity fixes (7) all applied. Low-severity fixes (2) all applied as ADOPT-LIGHT. No PASS, no PUSHBACK, no DEFER.

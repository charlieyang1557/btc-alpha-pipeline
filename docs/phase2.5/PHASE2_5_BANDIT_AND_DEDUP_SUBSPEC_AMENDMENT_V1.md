# Phase 2.5 — Combined Bandit + Dedup Sub-Spec Amendment v1

**Cycle classification**: process/spec deliverable register-class — **sub-spec amendment register-event** per predecessor sub-spec SEAL `ab8e715` §10 #5.

**Cycle authorization**: Charlie register-event 2026-05-16 "b authorized" reply (Path (b) explicit selection). Umbrella authorization same turn: "ALL remaining cycles and waves through arc-level closeout SEAL on the parked branch" + 3-session pacing per cycle.

**Base**: parked branch `phase2.5/bandit-dedup` at `a8d10ef` (W0.3 calibration commit).

**Predecessor**: [`docs/phase2.5/PHASE2_5_BANDIT_AND_DEDUP_SUBSPEC.md`](PHASE2_5_BANDIT_AND_DEDUP_SUBSPEC.md) at SEAL `ab8e715` (23 decisions + 14 discipline locks + 15 V# anchors). The 23 decisions + 14 locks + 15 V# anchors stand unless explicitly revised below.

**Cycle scope deliverable**: targeted revision of **3 decisions** (B-1, B-4, B-6) + **1 extended discipline lock** (B-Lock-2 with NL serializer sibling clause) + **0 new locks** (count stays at 14, just one extended) + amendment-specific 11 V# anchors + W0.3.v2 Wave 0 sub-task definition.

---

## §1 Trigger — empirical finding from W0.3 calibration

Sub-spec SEAL `ab8e715` §6 B-T7 (c) explicit clause: "If chosen τ ≠ 0.82, this triggers sub-spec amendment register-event."

Wave 0 W0.3 calibration commit `a8d10ef` produced **chosen τ = 0.90 (F1 = 0.7692, P = 0.625, R = 1.000)**. Cosine distribution on the N=10 synthetic fixture corpus:

| Label | n | Cosine range | Mean |
|---|---|---|---|
| near_dup | 5 | 0.9990 – 0.9997 | 0.9993 |
| distinct | 5 | 0.8700 – 0.9957 | 0.9411 |

Both classes occupy a narrow band 0.87–1.00 with significant overlap. At τ ≤ 0.85, F1 plateaus at 0.667. **Root cause** (validates architect F4 + planner Session-2 concerns): D3-canonical DSL JSON contains heavy structural noise that the embedding model weights against semantic content. The embedding space measures "how JSON-shaped is this text" more than "what strategy does this describe".

## §1.5 Alternative responses considered (Session 3 added per P-F5)

Three paths were surfaced after W0.3 commit `a8d10ef`. Charlie chose Path (b).

- **Path (a) — light τ-only amendment**: revise B-1 PROVISIONAL 0.82 → 0.90 with re-calibration trigger; keep B-4 (D3-JSON) + B-6 (cosine-only) unchanged. **Why rejected**: at τ=0.90 on W0.3 fixture, 3 of 5 distinct pairs are false-positive-dedupped → production quarantine queue would be ≈60% noise. The Critic / human override capacity (per B-3 quarantine semantics) is finite; 60% noise turns the quarantine state from "rare exception" into "default outcome". The substantive problem (D3-JSON dominates noise → all DSLs look alike) is unaddressed — only the cutoff shifts.
- **Path (b) — chosen**: revise B-1 + B-4 + B-6 with NL serializer + compound gate. **Why chosen**: addresses the substantive root cause (embed input format + gate composition), not just the cutoff. Higher scope-creep cost balanced against actually-useful Track B.
- **Path (c) — Track B drop**: remove semantic dedup from MVP; defer to Phase 2.6. **Why rejected**: Track B is in-scope per Phase 2.5 scoping SEAL `6750274`; dropping requires scoping-cycle re-adjudication. Empirical evidence supports MVP-tier alternatives (NL serializer + compound gate) being tried before declaring Track B infeasible.

---

## §2 Revised decisions (3)

### B-4 (REVISED): Embed input → **Natural-language serializer in `agents/orchestrator/semantic_dedup.py`**

**Original B-4 (SEAL `ab8e715`)**: D3-canonical DSL JSON.

**Revised default**: thin natural-language serializer in `semantic_dedup.py` that traverses `StrategyDSL` directly and produces embedding-friendly text. Reference shape:

```
entry when sma(20) crosses above close; exit after 10 bars
```

**Rationale (vs strongest alternative — original D3-JSON)**:
- Empirical: W0.3 demonstrated D3-JSON produces F1 = 0.77 at best τ on N=10 fixture (load-bearing rejection; see P-F2 fixture-expansion caveat at §3 W0.3.v2 scope)
- Architectural: D3-JSON re-use creates implicit second consumer of D3 form → CONTRACT BOUNDARY pressure. NL serializer in `semantic_dedup.py` traverses `StrategyDSL` directly, matching extended B-Lock-2 call-graph rule (see §4 below)
- Semantic: NL text is what sentence-transformers training was optimized for

**Sub-spec contract for NL serializer** (binding at this amendment SEAL; revised per architect F2 + planner P-F6 + A-F7):

- Implemented in `agents/orchestrator/semantic_dedup.py`. MUST NOT import or call `agents.hypothesis_hash.canonicalize_for_hash` per extended B-Lock-2 (§4 below)
- Traverses `StrategyDSL` object via attribute access (not via dict serialization)
- Produces lowercased natural-language text
- **Operator mapping** (Session 3 corrected per architect F2 — one row per `OpLiteral`, no context-dependent branching):
  - `>` → `"is greater than"`
  - `>=` → `"is at least"`
  - `<` → `"is less than"`
  - `<=` → `"is at most"`
  - `==` → `"equals"`
  - `crosses_above` → `"crosses above"`
  - `crosses_below` → `"crosses below"`
- **Factor vs scalar distinction lives in RHS rendering, NOT in operator**: numeric `value` renders as number; string `value` (factor name) renders verbatim with parametrization. Operator is pure function of `OpLiteral`.
- AND-conjunction within group: `; and ;`
- OR-conjunction across groups: `; or ;`
- Deterministic: same `StrategyDSL` → same NL string (sort within commutative groups identical to D3 canonicalization, but separate code path)
- **Test surface** (Session 3 expanded per architect F7):
  - `tests/test_semantic_dedup.py::test_nl_serializer_deterministic`
  - `tests/test_semantic_dedup.py::test_nl_serializer_isolates_from_hypothesis_hash`
  - `tests/test_semantic_dedup.py::test_nl_serializer_edge_cases_parametrized` covering: (a) multi-parameter factors (e.g., `bbands(20, 2)`); (b) `max_hold_bars=None` vs finite; (c) `position_sizing` field; (d) `crosses_above` with numeric RHS (schema-valid edge case); (e) entry/exit with multiple OR groups; (f) AND-conjunction within group; (g) empty optional fields

### B-6 (REVISED): Compound gate → **AND-gate: cosine ≥ τ_c AND factor-set match**

**Original B-6 (SEAL `ab8e715`)**: cosine-only for MVP.

**Revised default**: compound AND-gate combining cosine similarity with **exact factor-set match**.

**Mechanics block** (Session 3 added per architect F4):

For two DSLs A and B with factor sets `factors(A) = frozenset(extract_factors(A))` and `factors(B) = frozenset(extract_factors(B))` (via existing `agents.critic.d7a_feature_extraction.extract_factors`):

```
near_duplicate(A, B) ⟺ cosine(emb(A), emb(B)) ≥ τ_c  AND  factors(A) == factors(B)
```

The structural gate is **set equality** — equivalent to Jaccard ≥ 1.0 but cleaner to implement and reason about. The Jaccard generalization is reserved for V2 if production data later motivates τ_s < 1.0.

**Edge cases enumerated**:
- Both DSLs single-factor identical (e.g., both `{sma}`): set-equality TRUE → cosine gate decides
- One DSL strict subset of other (e.g., `{sma}` vs `{sma, volume}`): set-equality FALSE → NOT flagged (per amendment definition of "near-duplicate")
- Both DSLs multi-factor identical (e.g., both `{sma, volume}`): set-equality TRUE → cosine gate decides
- Empty factor sets: impossible per DSL schema (every condition references a registered factor via `cond.factor`)

**Rationale vs strongest alternatives**:
- vs cosine-only (original B-6): empirical W0.3 shows cosine-only struggles with cross-factor false positives. Set-equality eliminates the cross-factor failure mode entirely
- vs Jaccard < 1.0: amendment treats "near-duplicate" as a **definitional choice** — strategies with different factor sets are categorically different, not "kinda similar" (see §2 B-6 status below for definitional immunity)

### B-1 (REVISED): Cosine threshold τ_c → **FULL PROVISIONAL pending W0.3.v2 (no numeric anchor at amendment SEAL)**

**Original B-1 (SEAL `ab8e715`)**: τ = 0.82 PROVISIONAL.

**Revised default (Session 3 reframed per A-F3 + P-F1 high-severity convergence)**: **τ_c value DEFERRED to W0.3.v2 sweep**. No numeric anchor committed at amendment SEAL.

**Selection rule for W0.3.v2** (Session 3 added per A-F3 + P-F4):
- Sweep τ_c over `{0.80, 0.82, 0.85, 0.88, 0.90, 0.92, 0.95, 0.97, 0.99}`
- Compute F1 / precision / recall per τ_c against expanded fixture corpus (per P-F2 — N ≥ 30 fixture; see §3 W0.3.v2 scope)
- Chosen τ_c = highest F1; tie-break prefers LOWER τ_c (more aggressive dedup; B-3 quarantine semantics support Critic override on FPs)

**No-further-amendment trigger (conjunctive, Session 3 reframed per P-F4)**:
- (i) chosen τ_c ∈ [0.85, 0.99] — bounded range (rejects pathological extremes only)
- AND (ii) F1 ≥ 0.85 on expanded fixture
- If EITHER (i) OR (ii) fails, sub-spec amendment v2 register-event is triggered (subject to amendment-cadence guard at §6 below)

**τ_s status (Session 3 clarified per P-F3)**: τ_s is **NOT** a hyperparameter. The compound gate's structural side is **definitional set-equality** (τ_s = 1.0 ≡ exact factor-set match). The amendment SEAL declares this as a definitional choice **immune from re-litigation at W0.3.v2**. If empirical data later supports a Jaccard generalization (τ_s < 1.0), that is a separate sub-spec amendment v2 register-event with its own Charlie authorization — not a W0.3.v2 sweep parameter.

---

## §3 Implementation arc Wave structure impact

Original sub-spec §7 Wave preview anticipated W0.3 calibration as a single sub-task within Wave 0. This amendment adds **W0.3.v2** as a follow-up calibration with expanded scope.

| Wave | Status as of amendment v1 SEAL |
|---|---|
| Wave 0 W0.1 (shape locks) | DONE at `5772aa9` (unaffected) |
| Wave 0 W0.2 (SHA-pin) | DONE at `ea2a120` (unaffected) |
| Wave 0 W0.3 (initial calibration) | DONE at `a8d10ef` — empirical forensic record; superseded by W0.3.v2 |
| **Wave 0 W0.3.v2 (re-calibration with new code + expanded fixture)** | NEW per amendment; expanded scope per architect F6 + planner P-F2 |
| Wave A-1 / B-1 (TDD) | Unblocked once W0.3.v2 produces final τ_c |
| Wave A-2 / B-2 / A-3 / B-3 / Cross-track | No structural change |
| Arc-level closeout cycle | Closeout SEAL deliverable now references this amendment v1 alongside sub-spec SEAL `ab8e715` |

### W0.3.v2 scope (Session 3 expanded per A-F6 + P-F2)

W0.3.v2 is NOT a simple "re-run sweep" — it includes **new implementation code** + **fixture expansion**:

**(a) NL serializer implementation** in `agents/orchestrator/semantic_dedup.py`:
- Function `nl_serialize_dsl(dsl: StrategyDSL) -> str` per §2 B-4 contract
- TDD: 3 test files per §2 B-4 test surface enumeration
- Triggers normal pre-commit checks (python-reviewer, etc.) — Wave 0 sub-task, not a docs-only commit

**(b) Calibration script** in `scripts/btau_calibrate_v2.py`:
- Imports `nl_serialize_dsl` from `agents.orchestrator.semantic_dedup`
- Imports `extract_factors` from `agents.critic.d7a_feature_extraction` (shared single-source-of-truth helper; see §4 cross-module note below)
- Computes both cosine AND factor-set equality per pair
- Sweep τ_c per §2 B-1 selection rule; compound gate per §2 B-6 mechanics

**(c) Fixture expansion** to **N ≥ 30** pairs (15 near-dup + 15 distinct) with **per-class distribution labels** per P-F2:
- Class 1: parameter variation (SMA(20) vs SMA(25))
- Class 2: threshold value variation (RSI cutoff 30 vs 31)
- Class 3: direction-flip (long vs short bias, same factor)
- Class 4: factor-swap (SMA vs RSI)
- Class 5: scale-shift (SMA(5) vs SMA(200))
- Output reports per-class precision/recall in addition to aggregate F1
- Fixture located at `data/phase2_5/btau_calibration_v2/fixture_corpus.json`

**(d) Outputs**: same shape as W0.3 — `sweep_results.json` + `CALIBRATION_NOTE_V2.md`, located at `data/phase2_5/btau_calibration_v2/`

**Implementation arc Wave 0 entry order**: W0.3.v2 (a) → (b) → (c) → (d). (a) is a code commit gated by TDD; (b) and (c) are data + script commits; (d) is the empirical output. Wave A-1 / B-1 unblocked when (d) produces final τ_c.

---

## §4 Discipline locks status (Session 3 corrected per architect F1)

**14 existing locks remain in force** at sub-spec SEAL `ab8e715` §4.

**B-Lock-2 EXTENDED** at this amendment SEAL with a sibling clause for the NL serializer case (Session 3 added per A-F1; the prior amendment v1 draft incorrectly claimed B-Lock-2 covered NL serializer "naturally" — A-F1 correctly identified that the original B-Lock-2 wording was scoped explicitly to *the bucketing transform*, conditioned on B-5 bucketing adoption; since B-5 = None, the call-graph rule was effectively dormant. Re-using a dormant narrow lock by editorial fiat is the silent-scope-creep failure mode that lock discipline exists to prevent. Hence the explicit extension):

**B-Lock-2 (amendment-v1 extended text)**:

> NEVER change D2 manifest canonicalization or D3 hash canonicalization to accommodate embedding-friendly representation — bucketing (if any) lives in the embedding layer, not in canonicalization.
>
> **Call-graph rule for bucketing (original)**: if B-5 parameter bucketing is adopted at sub-spec, the bucketing transform MUST be implemented in `agents/orchestrator/semantic_dedup.py` and MUST construct its input string by traversing the `StrategyDSL` object directly — it MUST NOT call `canonicalize_for_hash()` and post-process the result, and it MUST NOT introduce a shared helper between `hypothesis_hash.py` and `semantic_dedup.py`.
>
> **Call-graph rule for NL serializer (amendment-v1 extension)**: the natural-language DSL serializer (adopted at amendment v1 per B-4 revised) MUST also be implemented in `agents/orchestrator/semantic_dedup.py` and MUST traverse `StrategyDSL` via attribute access. It MUST NOT call `canonicalize_for_hash()` or any other function in `agents/hypothesis_hash.py`. It MUST NOT introduce a shared serializer helper between `hypothesis_hash.py` and `semantic_dedup.py`. This sibling clause is parallel to the bucketing clause; the two transforms (bucketing + NL serializer) live as separate functions in `semantic_dedup.py`, both honoring the same CONTRACT BOUNDARY.

**Cross-module re-use note (Session 3 added per A-F5)**: `agents.critic.d7a_feature_extraction.extract_factors` is now shared between Track A (factor_bandit) and Track B (semantic_dedup compound gate) as a deliberate single-source-of-truth pattern. `extract_factors` is a pure DSL traversal function with no critic-specific state. **If a future change to `extract_factors` semantics is proposed, it MUST re-calibrate W0.3.v3 (analogous to the D3-canonicalization re-calibration trigger noted in original sub-spec §4 B-4)**. This is not a new lock, but a documented dependency surface.

---

## §5 V# self-check anchors for amendment SEAL (11 anchors; was 8 at Session 1 draft, +V9/V10/V11 added at Session 3 per P-F6)

Evaluated at pre-SEAL register. SEAL fire requires all 11 CLEAN.

- **V1**: Amendment cycle scope precisely defined as revision of 3 decisions (B-1, B-4, B-6) + 1 extended discipline lock (B-Lock-2 NL serializer sibling clause) + W0.3.v2 sub-task. No other sub-spec content modified
- **V2**: B-4 revised — NL serializer contract fully specified; operator mapping is 7-row pure function of `OpLiteral` (no context branching); 3 test surfaces enumerated with 7 edge-case categories
- **V3**: B-6 revised — compound AND-gate with cosine + factor-set equality; τ_s = 1.0 declared **definitional** (not empirical hyperparameter); edge cases enumerated; Jaccard generalization reserved for V2
- **V4**: B-1 revised — τ_c FULL PROVISIONAL pending W0.3.v2 sweep with explicit selection rule; conjunctive no-further-amendment trigger (τ_c ∈ [0.85, 0.99] AND F1 ≥ 0.85)
- **V5**: W0.3.v2 Wave sub-task scope expanded with 4 components (NL serializer code + calibration script + fixture expansion to N≥30 + outputs); same register-class as W0.3 (Wave 0 implementation-arc empirical work)
- **V6**: 14 existing discipline locks unchanged; B-Lock-2 extended in-place with sibling clause for NL serializer; cross-module `extract_factors` re-use documented as dependency surface (not new lock)
- **V7**: Trigger citation accuracy — W0.3 commit `a8d10ef` produces τ=0.90 ≠ PROVISIONAL 0.82; amendment trigger clause (sub-spec §6 B-T7 (c)) cited; Charlie register "b authorized" reply traced to this amendment cycle entry
- **V8**: Anti-pre-emption invariant at amendment SEAL — see §6 below; cycle-entry vs decision-class framing preserved from sub-spec precedent
- **V9 (added Session 3 per P-F6)**: Aspirational-flag audit — each revised decision rationale distinguishes empirical claims (W0.3-anchored: F1=0.77, cosine distribution data) from aspirational claims (NL serializer "should" produce better cosines). V9 verifies that for each aspirational claim there is a W0.3.v2 empirical-verification mechanism (sweep + F1 floor)
- **V10 (added Session 3 per P-F6)**: Range justification — the conjunctive no-further-amendment trigger ([0.85, 0.99] τ_c bounds AND F1 ≥ 0.85) is explicitly anchored: 0.85 lower bound rejects pathologically low cutoffs that would FP-flag almost all pairs; 0.99 upper bound rejects pathologically high cutoffs that would FN-miss near-duplicates; F1 ≥ 0.85 is "substantively better than W0.3's 0.77 while leaving MVP-tolerance margin below 0.90"
- **V11 (added Session 3 per P-F6)**: Scope-creep guard — amendment cycle introduces zero new module dependencies (sentence-transformers + torch already declared at W0.2; `extract_factors` shared with Track A, not new). No decision is promoted to permanently-binding (all revised decisions remain PROVISIONAL or have re-adjudication paths via sub-spec amendment v2+)

---

## §6 Amendment-specific anti-pre-emption + cadence guard

This amendment SEAL does **NOT**:

1. Pre-authorize Wave 0 W0.3.v2 execution — separate Charlie register-event required at implementation arc resumption *(cycle-entry)*
2. Pre-authorize implementation arc entry — separate Charlie register-event required (unchanged from sub-spec §10 #1) *(cycle-entry)*
3. Pre-authorize a future sub-spec amendment v2 register-event without explicit Charlie authorization *(cycle-entry)*
4. Modify any sub-spec decision other than B-1 / B-4 / B-6 — A-1..A-11 / B-2 / B-3 / B-5 / B-7 / B-8 / X-1..X-4 remain at SEAL `ab8e715` adjudication *(decision-class — invariant)*
5. Re-litigate τ_s = 1.0 (definitional immunity per §2 B-1 status; only sub-spec amendment v2 register-event with explicit Charlie authorization can change this) *(decision-class — invariant)*
6. Modify CLAUDE.md HARD CONSTRAINTS on main *(decision-class)*
7. Push to remote without explicit user authorization (umbrella authorization 2026-05-16 covers this branch only) *(cycle-entry)*

### §6.1 Amendment-cadence guard (Session 3 added per P-F7)

This is **amendment v1**. The amendment-cycle cadence is bounded as follows to prevent moving-target failure:

- If W0.3.v2 triggers another amendment (v2), the v2 cycle MUST include explicit Path (c) Track B drop deliberation as a first-class alternative — not just incremental decision revision
- v2 SEAL may produce v3 only with explicit Charlie register-event approving the depth (no implicit cascade)
- **Beyond v3, Track B drop becomes default** unless Charlie register-event explicitly overrides with substantive evidence for further amendment cycle

This guard caps cascading-amendment depth at 3 and forces Path (c) deliberation re-entry at v2. The bound is empirically justified by the cycle cost: each amendment is ~3 sessions + ~1 Wave 0 sub-task; 3 cycles = ~12 sessions, materially delaying arc closeout.

Each successor register-event boundary stands on its own authorization per [`feedback_authorization_routing.md`](../../.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_authorization_routing.md) hard rule.

---

## §7 Push / tagging / Phase Marker discipline at amendment SEAL

- **NO tag** at amendment SEAL (process/spec deliverable register-class precedent)
- **PUSH to remote** authorized per Charlie umbrella 2026-05-16
- **NO Phase Marker advance on main** — parked branch internal
- Amendment Session 3 SEAL = commit on `phase2.5/bandit-dedup`; chronology: `97f7774` scoping draft → `f63b316` scoping SEAL → `0a46823` sub-spec draft → `ab8e715` sub-spec SEAL → `d92c98f` impl plan → `5772aa9` W0.1 → `ea2a120` W0.2 → `a8d10ef` W0.3 → `0b3cb63` amendment Session 1 draft → this SEAL commit

---

## §8 Session 2 reviewer routing (executed; this section records outcomes)

Per umbrella authorization 2026-05-16: 2 internal Claude Code subagents fired independently and in parallel.

**Reviewer 1 — `architect` subagent**: returned 7 findings (3 high, 4 medium). Convergent with planner on τ_c anchor weakness (F3); unique high findings: B-Lock-2 scope-extension claim incorrect (F1), NL serializer operator-mapping table conflates contexts (F2 — correctness).

**Reviewer 2 — `planner` subagent**: returned 7 findings (3 high, 4 medium). Convergent with architect on τ_c anchor weakness (P-F1) and τ_s asymmetric treatment (P-F3 ≈ A-F4); unique high finding: N=10 fixture insufficient → fixture expansion (P-F2).

Codex / python-reviewer / security-reviewer SKIPPED at amendment cycle (no code; process/spec deliverable register-class).

---

## §9 Appendix — Session 3 adjudication dispositions table

13 dispositions across 14 findings (A-F3 + P-F1 merged at τ_c anchor convergence).

| # | Source | Severity | Disposition | Action applied |
|---|---|---|---|---|
| 1 | A-F1 | high | ADOPT | §4 B-Lock-2 extended with NL-serializer sibling clause (parallel to bucketing clause); silent-scope-creep concern resolved |
| 2 | A-F2 | high (CORRECTNESS) | ADOPT | §2 B-4 operator mapping restated as 7-row pure function of `OpLiteral`; factor-vs-scalar distinction moved to RHS rendering |
| 3 | A-F3 + P-F1 | high (merged) | ADOPT | §2 B-1 τ_c reframed as FULL PROVISIONAL (no numeric anchor); W0.3.v2 sweep + explicit selection rule; conjunctive no-further-amendment trigger |
| 4 | A-F4 | medium | ADOPT-LIGHT | §2 B-6 mechanics block added; τ_s=1.0 reduced to set-equality formulation; edge cases enumerated |
| 5 | A-F5 | medium | ADOPT-LIGHT | §4 `extract_factors` cross-module re-use documented as dependency surface with future-change re-calibration trigger (W0.3.v3 analog) |
| 6 | A-F6 | medium | ADOPT | §3 W0.3.v2 scope expanded to 4 components: NL serializer code + script + fixture + outputs |
| 7 | A-F7 | medium | ADOPT | §2 B-4 test surface expanded to 3 tests + 7 edge-case categories parametrized |
| 8 | P-F2 | high | ADOPT | §3 W0.3.v2 fixture expanded to N≥30 with 5-class distribution labels + per-class P/R reporting |
| 9 | P-F3 + A-F4 | high (merged) | ADOPT | §2 B-1 τ_s reframed as DEFINITIONAL (immune from re-litigation at W0.3.v2); §6 #5 anti-pre-emption clause locks the definitional choice |
| 10 | P-F4 | medium | ADOPT | §2 B-1 no-further-amendment trigger reframed as conjunctive (τ_c ∈ [0.85, 0.99] AND F1 ≥ 0.85) |
| 11 | P-F5 | medium | ADOPT-LIGHT | §1.5 added enumerating Paths (a)/(b)/(c) with explicit defense of (b) chosen |
| 12 | P-F6 | medium | ADOPT | §5 V# count 8 → 11 (V9 aspirational-flag, V10 range-justification, V11 scope-creep-guard) |
| 13 | P-F7 | medium | ADOPT | §6.1 amendment-cadence guard added; depth capped at v3; Track B drop default at v3+ |

**Reviewer convergence summary**: architect F3 + planner P-F1 (τ_c anchor) and architect F4 + planner P-F3 (τ_s treatment) are 2 reviewer-pair convergences. Both merged into the τ_c PROVISIONAL + τ_s DEFINITIONAL resolutions at items 3 and 9 respectively.

**Correctness-class finding**: architect F2 (operator mapping context conflation) is the only correctness-class finding; would have produced wrong NL serializer behavior had it shipped. Resolved at item 2.

**ADOPT-LIGHT framing pattern**: 2 ADOPT-LIGHT dispositions take the form of inline clarifications at the relevant decision/lock site.

# Phase 2.5 — Combined Bandit + Dedup Sub-Spec Amendment v1

**Cycle classification**: process/spec deliverable register-class — **sub-spec amendment register-event** per predecessor sub-spec SEAL `ab8e715` §10 #5: "Pre-commit any sub-spec choice as immune from re-adjudication — if implementation arc reveals a sub-spec choice is incorrect, an explicit 'sub-spec amendment register-event' is the path back."

**Cycle authorization**: Charlie register-event 2026-05-16 "b authorized" reply (Path (b) explicit selection from the three-path deliberation surfaced after Wave 0 W0.3 calibration commit `a8d10ef`). Umbrella authorization from earlier in same turn: "ALL remaining cycles and waves through arc-level closeout SEAL on the parked branch" + "Cycle structure for each remaining cycle: 3-session pacing".

**Base**: parked branch `phase2.5/bandit-dedup` at `a8d10ef` (W0.3 calibration commit).

**Predecessor**: [`docs/phase2.5/PHASE2_5_BANDIT_AND_DEDUP_SUBSPEC.md`](PHASE2_5_BANDIT_AND_DEDUP_SUBSPEC.md) at SEAL `ab8e715`. The original 23 decisions + 14 discipline locks + 15 V# anchors stand unless explicitly revised below.

**Cycle scope deliverable**: targeted revision of **3 decisions** (B-1, B-4, B-6) + 1 new compound-gate hyperparameter (τ_s) + 0 new discipline locks (existing 14 unchanged) + amendment-specific V# self-check + impact on implementation arc Wave structure (adds W0.3.v2 re-calibration sub-task).

---

## §1 Trigger — empirical finding from W0.3 calibration

Sub-spec SEAL `ab8e715` §6 B-T7 (c) explicit clause: "If chosen τ ≠ 0.82, this triggers sub-spec amendment register-event."

Wave 0 W0.3 calibration commit `a8d10ef` produced **chosen τ = 0.90 (F1 = 0.7692, P = 0.625, R = 1.000)**, with cosine distribution as follows on the 10-pair synthetic fixture corpus:

| Label | n | Cosine range | Mean |
|---|---|---|---|
| near_dup | 5 | 0.9990 – 0.9997 | 0.9993 |
| distinct | 5 | 0.8700 – 0.9957 | 0.9411 |

**The cosine distribution is heavily compressed** — both classes occupy a narrow band 0.87–1.00, with significant class overlap. At every τ ≤ 0.85, F1 = 0.667 (all 5 distinct pairs misclassified as near-dup; the cosine-only gate cannot separate the classes). At chosen τ = 0.90, 3 of 5 distinct pairs are still false-positive-dedupped — production quarantine queue would be 60% noise.

**Root cause** (validates Session-2 architect F4 + planner concerns): D3-canonical DSL JSON contains heavy structural noise (`{"entry":[...],"exit":[...]}`-level boilerplate, tag scheme `"num:30.000000"`, sorted keys) that the sentence-transformer `all-MiniLM-L6-v2` weights heavily against semantic content. The embedding space measures "how JSON-shaped is this text" more than "what strategy does this describe".

---

## §2 Revised decisions (3)

### B-4 (REVISED): Embed input → **Natural-language serializer in `semantic_dedup.py` (NOT D3-canonical JSON)**

**Original B-4 default (SEAL `ab8e715` §4)**: D3-canonical DSL JSON.

**Revised default (this amendment)**: thin natural-language serializer in `agents/orchestrator/semantic_dedup.py` that traverses `StrategyDSL` directly and produces an embedding-friendly NL string. Reference shape:

```
entry when sma(20) crosses above close; exit after 10 bars
```

vs the D3-canonical form:
```
{"entry":[{"factor":"sma","op":"crosses_above","param":"num:20.000000","value":"close"}],"exit":[{"bars":"num:10.000000"}],...}
```

**Rationale (vs strongest alternative, the original D3-JSON default)**:
- Empirical: W0.3 demonstrated D3-JSON produces F1 = 0.77 at best τ
- Architectural: D3-JSON re-use creates implicit second consumer of D3 form → CONTRACT BOUNDARY pressure (already flagged at scoping F3 / sub-spec §4 B-4 D3 soft re-use acknowledgment + future-canonicalization-tweak re-calibration trigger). NL serializer in `semantic_dedup.py` traverses `StrategyDSL` directly, matching B-Lock-2 call-graph rule for the bucketing case.
- Semantic: NL text is what sentence-transformers training was optimized for (sentence pairs from natural-language corpora). The model should better discriminate semantic content from syntactic shell.

**Sub-spec contract for NL serializer** (binding at this amendment SEAL):
- Implemented in `agents/orchestrator/semantic_dedup.py`. MUST NOT import or call `agents.hypothesis_hash.canonicalize_for_hash` per B-Lock-2 call-graph rule
- Traverses `StrategyDSL` object directly via attribute access (not via dict serialization)
- Produces lowercased natural-language text using a small fixed vocabulary: `entry when ...; exit ...; max-hold N bars; position-size method ...`
- Comparison operators rendered as words: `>` → "crosses above" (for indicators) or "is greater than" (for scalars), `<` → "crosses below" / "is less than", `>=` → "at least", `<=` → "at most"
- Factor names lowercased verbatim (e.g., `sma(20)`, `rsi(14)`, `bbands(20, 2)`)
- AND-conjunction within group: `; and ;`
- OR-conjunction across groups: `; or ;`
- Deterministic: same DSL → same NL string (sort within commutative groups identical to D3 canonicalization, but separate code path)
- Test surface: `tests/test_semantic_dedup.py::test_nl_serializer_deterministic` + `::test_nl_serializer_isolates_from_hypothesis_hash`

### B-6 (REVISED): Compound gate → **AND-gate (cosine ≥ τ_c) AND (factor-set Jaccard ≥ τ_s)**

**Original B-6 default (SEAL `ab8e715` §4)**: cosine-only for MVP.

**Revised default (this amendment)**: compound AND-gate combining cosine similarity with **factor-set Jaccard structural overlap**.

**Definition**: for two DSLs A and B with extracted factor sets `factors(A)` and `factors(B)` (via existing `agents.critic.d7a_feature_extraction.extract_factors`):

```
jaccard(A, B) = |factors(A) ∩ factors(B)| / |factors(A) ∪ factors(B)|
```

A pair is flagged `near_duplicate` iff: `cosine(emb(A), emb(B)) ≥ τ_c  AND  jaccard(A, B) ≥ τ_s`.

**Default τ_s = 1.0** (exact factor-set match required for near-duplicate flagging).

**Rationale**:
- Empirical: in W0.3 fixture, the 5 "distinct" pairs split into:
  - Same-factor / different-strategy: `distinct_long_vs_short_bias` (both use `sma`), `distinct_short_vs_long_window` (both use `sma`) — these LOOK like parameter variation but encode opposite direction or vastly different timescales
  - Different-factor: `distinct_sma_vs_rsi`, `distinct_macd_vs_bbands`, `distinct_single_vs_multi_factor` (different factor sets)
- Cosine-only struggles with both. Compound gate with τ_s = 1.0:
  - Different-factor pairs (4 of 5 distinct): fail Jaccard gate (Jaccard < 1.0) → NOT flagged as near-duplicate regardless of cosine
  - Same-factor / different-strategy pairs (2 of 5 distinct): pass Jaccard (factor sets match), so still rely on cosine gate. Among these:
    - `distinct_long_vs_short_bias` cosine 0.9957 — would be FP at τ_c ≤ 0.99
    - `distinct_short_vs_long_window` cosine 0.9898 — would be FP at τ_c ≤ 0.99
    - These remain a hard case for cosine-only; require NL serializer (B-4 revised) to differentiate
- Combined effect (revised B-4 + revised B-6): NL serializer should produce more discriminative cosines for same-factor / different-strategy pairs; Jaccard gate eliminates different-factor false positives entirely. F1 should improve substantially over D3-JSON + cosine-only baseline.

**τ_s alternatives considered**:
- τ_s = 0.5 (at least half overlap): admits pairs with one shared factor + one unique each; risks false positives where strategies share a common indicator but differ on other axes
- τ_s = 0.0 (degenerate to cosine-only): re-introduces the W0.3 failure mode
- τ_s = 1.0 (exact match): chosen — conservative; matches the intuition "near-duplicate = same factor set, only parameters / thresholds differ"

### B-1 (REVISED): Cosine threshold τ_c → **PROVISIONAL 0.95; final value at W0.3.v2 re-calibration**

**Original B-1 default (SEAL `ab8e715` §4)**: τ = 0.82 PROVISIONAL.

**Revised default (this amendment)**: **τ_c = 0.95** PROVISIONAL pending W0.3.v2 re-calibration with NL serializer (revised B-4) + compound gate (revised B-6). The provisional value is higher than the original 0.82 because:
- NL serializer should produce more discriminative cosines (lower noise floor)
- Compound gate filters cross-factor pairs at Jaccard level; cosine gate only needs to discriminate within same-factor-set pairs, where finer cosine differences matter

**Wave 0 W0.3.v2 trigger**: same re-adjudication mechanism as in original sub-spec — if W0.3.v2 calibration knee ≠ 0.95, another sub-spec amendment register-event is triggered. If knee ∈ [0.93, 0.97], adoption proceeds without further amendment.

---

## §3 Implementation arc Wave structure impact

Original sub-spec §7 Wave preview anticipated W0.3 calibration as a single sub-task within Wave 0. This amendment adds **W0.3.v2** as a follow-up calibration:

| Wave | Status as of amendment v1 SEAL |
|---|---|
| Wave 0 W0.1 (shape locks) | DONE at `5772aa9` (unaffected by amendment) |
| Wave 0 W0.2 (SHA-pin) | DONE at `ea2a120` (unaffected) |
| Wave 0 W0.3 (initial calibration) | DONE at `a8d10ef` — empirical trigger preserved as forensic record; superseded by W0.3.v2 |
| **Wave 0 W0.3.v2 (re-calibration)** | NEW sub-task per this amendment: implement NL serializer in `scripts/btau_calibrate_v2.py` + re-run sweep + produce final τ_c |
| Wave A-1 / B-1 (TDD) | Unblocked once W0.3.v2 produces final τ_c; can begin before W0.3.v2 if Track A is run independently of Track B |
| Wave A-2 / B-2 / A-3 / B-3 / Cross-track | No structural change |
| Arc-level closeout cycle | Closeout SEAL deliverable now references this amendment v1 alongside original sub-spec SEAL `ab8e715` |

W0.3.v2 is a Wave 0 sub-task per amendment design — not a separate amendment cycle. Same register-class as W0.3 (empirical, implementation arc Wave 0).

---

## §4 Discipline locks status

**No new discipline locks added** by this amendment. The 14 existing locks at sub-spec SEAL `ab8e715` §4 remain in force.

**Lock implications of revised decisions**:
- B-Lock-2 (call-graph rule): the NL serializer in `semantic_dedup.py` MUST construct its input string by traversing the `StrategyDSL` object directly — it MUST NOT call `canonicalize_for_hash()` and post-process the result. This was already a B-Lock-2 contract for the bucketing case; this amendment extends the contract scope to the NL-serializer case. No new lock text required — the existing B-Lock-2 wording covers this naturally
- B-Lock-7 (model SHA pin): unchanged; same model artifact governs W0.3.v2 calibration

---

## §5 V# self-check anchors for amendment SEAL (8 anchors)

Evaluated at pre-SEAL register at amendment Session 3. SEAL fire requires all 8 CLEAN.

- **V1**: Amendment cycle scope precisely defined as revision of 3 decisions (B-1, B-4, B-6) + addition of τ_s hyperparameter + W0.3.v2 Wave sub-task. No other sub-spec content modified
- **V2**: B-4 revised — NL serializer in `semantic_dedup.py` with full contract specification (binding rules + test surface)
- **V3**: B-6 revised — compound AND-gate with cosine + Jaccard structural overlap; τ_s default = 1.0 (exact factor-set match); alternatives explicitly considered
- **V4**: B-1 revised — τ_c = 0.95 PROVISIONAL; W0.3.v2 trigger defined with knee range [0.93, 0.97] for no-further-amendment
- **V5**: W0.3.v2 Wave sub-task added to implementation arc Wave structure; does NOT introduce a new register-class boundary (remains within Wave 0)
- **V6**: 14 existing discipline locks unchanged; B-Lock-2 call-graph rule scope acknowledged as extending naturally to NL-serializer case
- **V7**: Trigger citation accuracy — W0.3 commit `a8d10ef` produces τ=0.90 ≠ PROVISIONAL 0.82; amendment trigger clause (sub-spec §6 B-T7 (c)) explicitly cited; Charlie register "b authorized" reply traced to this amendment cycle entry
- **V8**: Anti-pre-emption invariant for amendment SEAL — see §7 below

---

## §6 Amendment-specific anti-pre-emption

This amendment SEAL does **NOT**:

- Pre-authorize Wave 0 W0.3.v2 execution — separate Charlie register-event required at implementation arc resumption *(cycle-entry)*
- Pre-authorize implementation arc entry — separate Charlie register-event required (unchanged from original sub-spec §10 #1) *(cycle-entry)*
- Pre-authorize a future sub-spec amendment register-event without explicit Charlie authorization (e.g., if W0.3.v2 knee ∉ [0.93, 0.97]) *(cycle-entry)*
- Modify any sub-spec decision other than B-1 / B-4 / B-6 — A-1..A-11 / B-2 / B-3 / B-5 / B-7 / B-8 / X-1..X-4 remain at SEAL `ab8e715` adjudication *(decision-class — invariant)*
- Modify CLAUDE.md HARD CONSTRAINTS on main *(decision-class)*
- Push to remote without explicit user authorization (umbrella authorization 2026-05-16 covers this branch only) *(cycle-entry)*

---

## §7 Push / tagging / Phase Marker discipline at amendment SEAL

- **NO tag** at amendment SEAL (process/spec deliverable register-class precedent)
- **PUSH to remote** authorized per Charlie umbrella 2026-05-16 ("authorized: push on this branch")
- **NO Phase Marker advance on main** — parked branch internal
- **Commit numbering**: amendment SEAL is commit 7 on `phase2.5/bandit-dedup` (chronology: `97f7774` scoping draft → `f63b316` scoping SEAL → `0a46823` sub-spec draft → `ab8e715` sub-spec SEAL → `d92c98f` impl plan → `5772aa9` W0.1 → `ea2a120` W0.2 → `a8d10ef` W0.3 → ... → amendment Session 1 draft + Session 3 SEAL)

---

## §8 Session 2 reviewer routing plan

Per umbrella authorization 2026-05-16: "Use agents independently and in parallel as architect + planner reviewer."

**Reviewer 1 — `architect` subagent**: architectural critique of (i) NL serializer design + B-Lock-2 call-graph rule compliance, (ii) compound AND-gate mechanics, (iii) W0.3.v2 sub-task placement.

**Reviewer 2 — `planner` subagent**: plan-completeness critique of (i) revised decision rationales' defensibility, (ii) τ_s default selection rigor, (iii) τ_c PROVISIONAL choice + W0.3.v2 trigger range, (iv) coherence with original sub-spec discipline locks.

Codex / python-reviewer / security-reviewer SKIPPED at amendment (no code; same as sub-spec cycle precedent).

---

## §9 Appendix — Session 3 adjudication dispositions table (PLACEHOLDER for SEAL)

To be populated at Session 3 after Session 2 reviewer routing returns findings.

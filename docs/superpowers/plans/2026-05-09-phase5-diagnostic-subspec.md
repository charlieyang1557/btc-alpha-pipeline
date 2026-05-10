# Phase 5 Diagnostic Sub-Spec Authoring Plan

> **Status:** WORKING DRAFT (session-1 ToC; pending Charlie register adjudication at session-1 SEAL)
> **Cycle:** Phase 5 sub-spec drafting cycle (Path 1 per Phase 5 entry scoping decision §6 successor cycle eligible-not-named slot)
> **Authorization:** Charlie register at 2026-05-09 fresh-session entry ("also authorize path 1" + "confirm" on 3 follow-up items: assessment-procedure wording refinement / session-1 ToC-only sub-scope / diagnostic ambiguity sub-section inclusion)
> **Reviewer pass routing at meta-plan register:** ChatGPT structural overlay + Claude advisor full-prose-access at session-1 (PASS WITH PATCHES from both; 12 patches landed inline; 1 minor finding deferred to §8 authoring)

**Goal:** Author Phase 5 diagnostic sub-spec at `docs/phase5/PHASE5_DIAGNOSTIC_SUBSPEC.md` operationalizing the sealed Phase 5 scoping decision §2.1-§2.5 + §2.2 operationalization-freeze lock.

**Architecture:** Multi-session sub-spec drafting cycle per PHASE2C_10/11/12/13/14/15 register precedent. Session-1 (this file) produces meta-plan with ToC structure + per-section descriptions + register-class tags + line budgets + sequencing dependencies. Session-2+ authors each section's content per per-fix adjudication discipline. Sub-spec drafting cycle SEAL at fresh-session boundary post-content authoring + reviewer pass cycle + final full-file prose-access pass per METHODOLOGY_NOTES §17 sub-rule 4.

**Spec source:** [`docs/phase5/PHASE5_SCOPING_DECISION.md`](../../phase5/PHASE5_SCOPING_DECISION.md) (sealed at `697c26b` 2026-05-10T01:29:10Z; 148 lines / 6 main §§ + 11 sub-§§).

**Tech stack:** Markdown only; no code; no API spend. Reviewer routing: ChatGPT structural overlay + Claude advisor full-prose-access pass. Codex skipped per [`feedback_codex_review_scope.md`](../../../.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_codex_review_scope.md) (sub-spec drafting register; scoping cycle register-class match precedent).

---

## Path 1 binding scope (Charlie register confirmed 2026-05-09)

**In scope:**
- Operationalize sealed Phase 5 diagnostic taxonomy + interpretation framework
- Define indicator-extraction procedure for each of 6 modes per scoping §2.1
- Pre-register continuous-or-binned cutoffs per indicator (or rule-based constraints where threshold-based does not apply)
- Pre-register multi-mode coexistence rules per scoping §2.x advisor Refinement 2
- Pre-register diagnostic ambiguity handling rules (distinct from multi-mode coexistence per ChatGPT addition Charlie-confirmed at session-1)
- Pre-register terminal-conclusion fire-criterion per scoping §2.5
- Pre-register framing-question (1)/(2)/(3)/(4) resolution-pressure **assessment procedure** at Phase 5 SEAL boundary per scoping §2.4 (procedure ≠ resolution; advisor wording refinement adopted at session-1)
- Pre-register attribution report deliverable structure per scoping §2.x

**Explicit exclusions (per Path 1 scope):**
- ❌ No implementation (no diagnostic execution at sub-spec drafting register)
- ❌ No new fires / no new data acquisition per scoping §4.1
- ❌ No methodology codification (METHODOLOGY_NOTES additions out of scope)
- ❌ No framing-question *resolution* at this register (resolution happens at Phase 5 SEAL based on diagnostic findings; sub-spec only pre-registers procedure)
- ❌ No §31 P1 CAVEAT engagement at this register (register-class-distinct)

**Discipline locks binding throughout cycle:**
- §2.2 operationalization-freeze: thresholds frozen before any diagnostic execution can fire (Mod-pass-2 C1 lock)
- Anti-pre-naming (§4.2): successor cycle scope eligible-not-named at this register; option (ii) preservation
- Anti-momentum-binding (§4.3): sub-spec SEAL ≠ implementation arc authorization
- **ToC SEAL at session-1 ≠ content authoring authorization at session-2** (advisor Finding 8): anti-momentum-binding at sub-spec drafting register requires fresh Charlie-register authorization at each session-N entry; session-1 SEAL does not by itself authorize session-2+ content authoring.
- Per-fix adjudication (§4.4): no bulk-accept at any reviewer cycle per [`feedback_reviewer_suggestion_adjudication.md`](../../../.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_reviewer_suggestion_adjudication.md)
- Pacing discipline (§4.5): section-level Charlie register-event boundaries; multi-session
- Sealed-content invariance (§4.6): scoping decision + Phase 4 corpus + METHODOLOGY_NOTES sealed corpus invariant

---

## Sub-spec File Structure (ToC)

**Target file:** `docs/phase5/PHASE5_DIAGNOSTIC_SUBSPEC.md`

**Total target line budget:** ~315-415 lines (subject to revision at session-2+ if content scope reveals different sizing per advisor approach (a))

Per-section: scope description + register-class tag (binding vs descriptive; irreversible-interpretation-constraint flag; constraint-type expected) + line budget + sequencing dependency.

### §0 — Scope + structure

- **Covers:** sub-spec scope statement (operationalize Phase 5 diagnostic procedure; constrained by §2.2 lock); section-by-section overview; pointer to §7 verification register
- **Locks produced:** none (descriptive section)
- **Register-class tag:** descriptive
- **Constraint type expected:** none
- **Line budget:** ~20-30 lines
- **Sequencing:** ships first

### §1 — Locked inputs

- **Covers:**
  - Phase 4 null result anchor (sealed at `e8f62f1`; tag `phase4-forward-test-v1`; result frozen)
  - PHASE2C_15 `cohort_a` 39 candidates frozen reference at `data/phase4_scoping/cohort_a_candidate_reference.csv` (sealed at `11b39f2`)
  - Engine `eb1c87f` (corrected `wf-corrected-v1` lineage; frozen)
  - Existing sealed artifacts ALLOWED for derived statistics (re-aggregations, alternative metric profiles, statistical decompositions, regime-conditioning) per scoping §4.1
  - No new fires / no new data acquisition
- **Locks produced:** which existing artifacts the sub-spec can consume; what counts as "derived" vs "new data"
- **Register-class tag:** binding (constraint declaration; not threshold)
- **Constraint type expected:** rule-based (constraint declarations)
- **Line budget:** ~15-25 lines
- **Sequencing:** ships after §0; constrains §2 indicator extraction

### §2 — Per-mode operationalization (load-bearing section)

- **Covers:** 6 sub-sections per failure mode. Per sub-section authors: indicator-extraction procedure + cutoffs + binning rules + data source classification (on-disk vs derived per §1 binding) + register-class tag.

**Per-mode data source + complexity tier (pre-considered at meta-plan per advisor Finding 2):**

| Mode | Data source | Complexity tier |
|---|---|---|
| §2.a Signal decay | On-disk (forward Sharpe + per-candidate trade returns from PHASE2C_15 cohort_a + Phase 4 forward windows) | Light |
| §2.b Cost drag | Derived (gross-vs-realistic cost decomposition from existing trade data; 7/13/15/17 bps sweep already at PHASE4 closeout) | Medium |
| §2.c Cohort weakness | Derived (cohort-level economic-weakness analysis from existing artifacts) | Light |
| §2.d Overfit AND-gate | Derived (gate-construction decomposition; AND-gate pass-pattern analysis from PHASE2C_12/15 artifacts) | Medium |
| §2.e Bad success metric | Derived (alternative success-criterion profiles per scoping §4.1 derived-statistics allowance) | Medium |
| §2.f Regime change | Derived (market-structure metrics from BTC OHLCV; may require derived-statistics work above Light tier) | Heavy |

**Provisional classification, not binding lock** (per ChatGPT + advisor convergence at session-1 reviewer pass). This pre-classification informs session-3 sequencing decisions (e.g., whether §2.f Heavy tier warrants its own session split) but does not lock interpretation. The complexity table is sequencing-informative, NOT irreversible-interpretation-constraint per §2.2 lock. Subject to revision at §2 authoring if substantive content reveals different tier classification per advisor approach (a) flexibility — particularly §2.f, where complexity depends on whether procedure operationalizes "regime change" as simple market-structure metrics (Medium) vs hidden Markov / change-point analysis (Heavy).

- **Sub-sections:**
  - §2.a Signal decay (candidate-level temporal deterioration)
  - §2.b Cost drag (realistic-cost-model differential)
  - §2.c Cohort weakness (population-level economic weakness)
  - §2.d Overfit AND-gate (gate-construction flaw)
  - §2.e Bad success metric (success-criterion misalignment)
  - §2.f Regime change (external market-structure shift)
- **Locks produced:** quantitative thresholds (or rule-based constraints) per mode; binning structure; data source per mode
- **Register-class tag:** binding (each cutoff/rule is irreversible-interpretation-constraint per §2.2 lock)
- **Constraint type expected:** quantitative (per-mode cutoffs) — though specific modes may use rule-based constraints where thresholds do not apply
- **Line budget:** ~120-160 lines (6 modes × ~20-25 lines each)
- **Sequencing:** ships after §1; load-bearing; §3+ depends on §2

### §3 — Multi-mode rules + diagnostic ambiguity handling

Two register-class-distinct sub-sections per ChatGPT substantive distinction (Charlie-confirmed at session-1):

#### §3.1 Multi-mode coexistence rules

- **Covers:** how procedure handles multiple modes simultaneously firing per advisor Refinement 2. E.g., (a) signal decay + (e) bad success metric co-occurrence; (b) cost drag + (c) cohort weakness co-occurrence
- **Locks produced:** combination-handling logic when 2+ modes positively detected
- **Register-class tag:** binding
- **Constraint type expected:** Quantitative or categorical interpretation constraints may be required (combination logic rules; per ChatGPT P1)
- **Line budget:** ~20-30 lines

#### §3.2 Diagnostic ambiguity handling

- **Covers:** how procedure handles cases where reliable separation between modes fails:
  - Insufficient evidence (no mode positively detected at indicator threshold)
  - Conflicting indicators (mode-A and mode-B mutually exclusive but both register positive)
  - Weak-signal / noisy-indicator cases
  - "Cannot distinguish between X and Y" outcomes
- **Distinction from §3.1:** coexistence = multiple modes ARE active; ambiguity = procedure FAILS to reliably separate. NOT collapsed at register-class.
- **Locks produced:** rules for unresolvable cases; whether ambiguity → terminal availability
- **Register-class tag:** binding
- **Constraint type expected:** Quantitative or categorical interpretation constraints may be required (ambiguity rules; may be rule-based not threshold-based per ChatGPT P1)
- **Line budget:** ~25-35 lines

- **§3 combined line budget:** ~45-65 lines
- **Sequencing:** ships after §2

### §4a — Successor-cycle-class mapping operationalization

- **Covers:** how diagnostic findings map to successor-cycle classes per scoping §2.3 (ChatGPT lock). Mapping table from finding-pattern → successor-cycle-class.
- **Locks produced:** pre-registered mapping table
- **Register-class tag:** binding
- **Constraint type expected:** rule-based (mapping logic, not thresholds)
- **Line budget:** ~20-30 lines
- **Sequencing:** ships after §3

### §4b — Framing-question resolution-pressure assessment procedure

- **Covers:** how Phase 5 SEAL will conduct framing-question (1)/(2)/(3)/(4) resolution-pressure **assessment procedure** per scoping §2.4 (advisor Refinement 1; load-bearing).
- **Critical distinction:** procedure ≠ resolution. Sub-spec pre-registers the *assessment procedure* (how Phase 5 SEAL evaluates pressure on each framing question); framing-question resolution itself happens (or doesn't) at Phase 5 SEAL based on diagnostic findings. Sub-spec does NOT resolve framing question.
- **Locks produced:** pre-registered assessment procedure
- **Register-class tag:** binding (procedure is irreversible-interpretation-constraint at SEAL boundary)
- **Constraint type expected:** Quantitative or categorical interpretation constraints may be required (pressure assessment criteria; per ChatGPT P1)
- **Line budget:** ~20-30 lines
- **Sequencing:** ships after §4a at sub-section register-event boundary; §4b may reference §4a mapping outputs (advisor Finding 3: sequential not parallel given §4a mechanical and §4b methodologically novel)

### §5 — Terminal-conclusion criteria

- **Covers:** criteria for terminal-conclusion availability per scoping §2.5 + Mod-pass-2 F1 disambiguation. Two register-class-distinct outcomes:
  - **Substantive availability:** paradigm exhaustion (research line evidence-based concluded)
  - **Operational availability:** no-successor-cycle-currently-justified (research line not currently warranting next cycle, but not paradigm-exhausted)
- **Distinction preserved per F1:** these are NOT the same outcome; sub-spec keeps them distinct at register-precision
- **Locks produced:** criteria for each terminal outcome; trigger conditions; relationship to diagnostic ambiguity (§3.2)
- **Register-class tag:** binding (criteria are irreversible-interpretation-constraints at SEAL boundary)
- **Constraint type expected:** quantitative (terminal criteria)

**Anti-circularity guard (ChatGPT P2):** Terminal-conclusion criteria may consume per-mode outputs but may not retroactively redefine per-mode indicator thresholds established in §2.

**Sequencing lock (ChatGPT P3):** §5 terminal criteria are downstream consumers of §2 outputs and may not alter §2 operationalization once frozen.

- **Line budget:** ~20-30 lines
- **Sequencing:** ships after §4

### §6 — Attribution report deliverable structure

- **Covers:** structure of Phase 5 closeout deliverable. Pre-registers:
  - Per-mode finding section structure
  - Multi-mode disposition section
  - Diagnostic ambiguity disposition section
  - Successor-class mapping disposition (per §4a)
  - Framing-resolution-pressure assessment disposition (per §4b)
  - Terminal-conclusion fire-or-not section

**Substantive dependency on §5 (advisor Finding 4):** §6's "Terminal-conclusion fire-or-not section" structure depends on §5's substantive vs operational availability distinction. §6 cannot be authored without §5's distinction firmly locked.

- **Locks produced:** deliverable structural framework for Phase 5 closeout
- **Register-class tag:** binding (deliverable structure)
- **Constraint type expected:** none (structural)
- **Line budget:** ~30-50 lines
- **Sequencing:** ships after §5

### §7 — Verification + reviewer disposition

- **Covers:**
  - V# verification chain at sub-spec SEAL pre-fire (anchor verification per cycle precedent)
  - Reviewer pass routing: ChatGPT structural overlay + Claude advisor full-prose-access pass; Codex skipped per scoping cycle register precedent
  - Final full-file prose-access pass per METHODOLOGY_NOTES §17 sub-rule 4 cycle-terminus
- **Locks produced:** verification + review process for sub-spec SEAL
- **Register-class tag:** descriptive (procedural)
- **Constraint type expected:** none
- **Line budget:** ~20-30 lines
- **Sequencing:** ships after §6

### §8 — Cross-references

- **Covers:** cross-references to:
  - Phase 5 scoping decision §2.x source language anchors (verbatim citations)
  - PHASE4_RESULTS.md anchor commits + tag
  - METHODOLOGY_NOTES sections actually referenced in sub-spec content (advisor Finding 7 deferred: prune aspirational cross-references at §8 authoring; cross-reference only sections substantively engaged)
  - This meta-plan path
- **Register-class tag:** descriptive
- **Constraint type expected:** none
- **Line budget:** ~10-15 lines
- **Sequencing:** ships last

---

## Per-Section Register-Class Summary

| Section | Register-class | Irreversible interpretation | Constraint type expected | Sequencing |
|---|---|---|---|---|
| §0 | descriptive | no | none | first |
| §1 | binding (constraint) | no | rule-based | after §0 |
| §2.a-§2.f | binding | yes | quantitative (per-mode cutoffs) | after §1 |
| §3.1 | binding | yes (rules at SEAL) | rule-based or quantitative (combination logic) | after §2 |
| §3.2 | binding | yes (rules at SEAL) | rule-based or quantitative (ambiguity rules) | after §2 |
| §4a | binding | yes (mapping) | rule-based | after §3 |
| §4b | binding | yes (procedure) | rule-based or quantitative (pressure assessment) | after §4a |
| §5 | binding | yes (terminal criteria) | quantitative | after §4 |
| §6 | binding | yes (deliverable structure) | none | after §5 |
| §7 | descriptive | no | none | after §6 |
| §8 | descriptive | no | none | last |

**Anti-creep guard at structural register (per ChatGPT addition Charlie-confirmed):** sections tagged "descriptive" must NOT silently harden into binding/operational criteria during content authoring. Section content that produces locks should be moved to a binding section. Reviewer pass cycle audits this distinction at sub-spec SEAL pre-fire.

---

## Per-Session Task Breakdown (Multi-Session; Estimated Scope Only)

**Session count adapts per per-fix adjudication discipline + Charlie register-event boundaries (advisor Finding 5).** Predictions below are estimated scope for planning visibility, NOT session-1 commitments. Whether sessions split, combine, or sequence differently is Charlie register adjudication at each session-N entry based on actual content density at that register-event boundary.

**Session compression for convenience is not itself sufficient justification to merge register-event boundaries** (ChatGPT P4 — aligns with pacing discipline history).

### Session-1 (this session) — Meta-plan + ToC authoring

- [x] Plan file authored at `docs/superpowers/plans/2026-05-09-phase5-diagnostic-subspec.md`
- [x] Reviewer pass cycle (ChatGPT + advisor); 12 patches landed inline
- [ ] Surface for Charlie register adjudication on ToC structure + per-session breakdown + commit scope
- [ ] Charlie register approval before commit fires
- [ ] Single-atomic commit per §0.4 (this meta-plan only; sub-spec file `PHASE5_DIAGNOSTIC_SUBSPEC.md` NOT created until session-2)

### Session-2 — estimated scope: §0 + §1 authoring (lightweight; sub-spec file creation)

- Estimated: create `docs/phase5/PHASE5_DIAGNOSTIC_SUBSPEC.md`; author §0 + §1 content
- Whether session-2 covers §0 + §1 only or extends into §2.a is Charlie register adjudication at session-2 entry

### Session-3 — estimated scope: §2 per-mode operationalization (load-bearing)

- Estimated: §2.a through §2.f sub-sections
- Whether session-3 splits (e.g., for §2.f Heavy tier per the data source + complexity table above) or completes in one session is Charlie register adjudication at session-3 entry based on §2's actual content density
- Whether reviewer pass cycle fires at session-3 SEAL (interim review for load-bearing section) vs deferred to session-N SEAL is Charlie register adjudication at session-3 SEAL boundary

### Session-4 — estimated scope: §3 + §4 authoring

- Estimated: §3.1 multi-mode coexistence + §3.2 diagnostic ambiguity (distinct sub-sections per ChatGPT distinction); §4a successor-class mapping → register-event → §4b framing-resolution-pressure assessment procedure
- Sub-section sequencing decisions adjudicated at session-4 register-event boundaries

### Session-5 — estimated scope: §5 + §6 authoring

- Estimated: §5 terminal-conclusion criteria (substantive + operational availability distinct per F1; anti-circularity + sequencing locks at §5); §6 attribution report deliverable structure (with §5 substantive dependency lock)

### Session-N — estimated scope: §7 + §8 + reviewer pass cycle + final prose-access pass + SEAL

- Estimated: §7 verification + reviewer disposition section; §8 cross-references (with pruning per advisor Finding 7 deferred to this register)
- Reviewer pass cycle (ChatGPT structural overlay + Claude advisor full-prose-access)
- Per-fix adjudication of all reviewer findings
- Final full-file prose-access pass per §17 sub-rule 4 cycle-terminus
- V# verification chain CLEAN
- Sub-spec drafting cycle SEAL commit + Phase Marker advance commit + push
- NO tag at sub-spec drafting cycle SEAL per scoping cycle precedent (PHASE2C_10/11/12/13/14/15 all NO-tag at sub-spec drafting cycle SEAL)

**Note on session count:** N is estimated at 6 sessions based on PHASE2C_13 sub-spec drafting cycle precedent (3+ sessions for substantively heavier scope) + Phase 5 sub-spec content scope (6-mode operationalization + dual mappings + terminal-conclusion + ambiguity handling + report structure). Actual count adapts per pacing discipline.

---

## Self-Review Checklist (session-1 close)

- [x] Spec coverage: Phase 5 scoping decision §2.1 (taxonomy) → §2 / §2.2 (operationalization-freeze) → all binding sections / §2.3 (successor-class) → §4a / §2.4 (framing-resolution-pressure) → §4b / §2.5 (terminal-conclusion) → §5 / §4.1 (existing artifacts allowed; derived statistics allowed; no new data) → §1 / §4.5 operationalization-freeze → all binding sections
- [x] All 6 modes mapped to sub-sections (§2.a-§2.f)
- [x] Per-mode complexity table at meta-plan level (advisor Finding 2)
- [x] Multi-mode coexistence (§3.1) distinct from diagnostic ambiguity (§3.2) per ChatGPT addition Charlie-confirmed at session-1
- [x] §3 budget split: §3.1 ~20-30 + §3.2 ~25-35 (advisor Finding 1)
- [x] §4 split into §4a/§4b for register distinction (successor-class vs framing-resolution-pressure); §4a→§4b sequential at sub-section boundary (advisor Finding 3)
- [x] §5 covers both substantive + operational availability per Mod-pass-2 F1 disambiguation
- [x] §5 anti-circularity + sequencing locks (ChatGPT P2 + P3)
- [x] §6 substantive dependency on §5 explicit (advisor Finding 4)
- [x] Per-section register-class tags applied (anti-creep guard at structural register per ChatGPT addition Charlie-confirmed)
- [x] Constraint type column accommodates rule-based vs quantitative (ChatGPT P1)
- [x] Line budgets sum to ~315-415 line target
- [x] Sequencing dependencies validate
- [x] No placeholders / TBDs / stub content
- [x] Cross-references to scoping decision anchored
- [x] Wording refinement adopted: "assessment procedure" not "resolution operationalization" at §4b
- [x] Anti-momentum-binding sentence at discipline locks (advisor Finding 8)
- [x] Session-3+ task breakdown softened to estimated scope (advisor Finding 5)
- [x] Session compression discipline note (ChatGPT P4)
- [x] Timestamp corrected to git canonical: 2026-05-10T01:29:10Z (advisor Finding 6)
- [x] Advisor Finding 7 deferred to §8 authoring (carry-forward note added)

---

## Charlie register adjudication points at session-1 SEAL

Items requiring Charlie register before commit fires:

1. **ToC structure approval:** does the §0-§8 structure match scope intent? Any sections missing or scope-misframed?
2. **§2 sub-section count:** confirm 6 sub-sections under §2 (§2.a-§2.f) for navigability
3. **§2 complexity table:** confirm pre-classification (Light/Medium/Medium/Medium/Medium/Heavy) is accurate at register-precision, or hold for session-3 §2 authoring re-classification
4. **§3 sub-section split + budget:** confirm §3.1 coexistence + §3.2 ambiguity as distinct sub-sections at ~20-30 + ~25-35 lines
5. **§4 split + sequencing:** confirm §4a → §4b sequential at sub-section register-event boundary
6. **Line budget targets:** confirm per-section budgets + ~315-415 total target
7. **Per-session task breakdown:** confirm soft-estimated 6-session structure (session count adapts per per-fix discipline + Charlie register-event boundaries)
8. **Commit scope at session-1 SEAL:** single-atomic-commit per §0.4 (this meta-plan only; sub-spec file `PHASE5_DIAGNOSTIC_SUBSPEC.md` not created until session-2 §0 authoring)
9. **Phase Marker advance at session-1:** PHASE2C_13/15 precedent suggests NO Phase Marker advance at meta-plan commit; advance only at sub-spec drafting cycle SEAL at session-N. Confirm or override.

After Charlie register adjudication: commit at session-1 SEAL register-event boundary.

---

**Status at session-1 close:** WORKING DRAFT post-reviewer-pass with 12 patches landed inline; pending Charlie register adjudication on 9 items above + commit fire.

# PHASE2C_12 Successor Scoping Cycle Plan

> **For agentic workers:** This plan drives a documentation/scoping arc, not a code/TDD arc. Steps are authoring milestones + reviewer-cycle gates + Charlie-register authorization fires. Tracked via TodoWrite per `feedback_use_planning_skills_for_complex_tasks.md`.

**Goal:** Author + seal `docs/phase2c/PHASE2C_12_SCOPING_DECISION.md` adjudicating §6.4 register-class-eligible successor paths, with arc designation committed only at §4.4 SEAL register per anti-pre-naming option (ii).

**Architecture:** Single-deliverable scoping cycle following PHASE2C_10/PHASE2C_11 precedent (8-section skeleton + 6-question evaluation framework + sub-spec pre-registration paragraph). Reviewer routing: ChatGPT first-pass + Claude advisor full-prose-access pass; Codex skipped per `feedback_codex_review_scope.md`. Phase Marker advance is SEPARATE COMMIT after scoping-doc seal per §7.4-precedent. No tag at scoping cycle SEAL.

**Tech stack:** Markdown authoring; git for seal + advance + push; pytest for baseline regression; curl for Discord webhook ping.

**Anti-pre-naming option (ii) binding:** specific successor arc direction NOT pre-committed at this plan, NOT pre-committed at session entry, NOT pre-committed until §4.4 SEAL register. The plan describes HOW the scoping cycle adjudicates; it does NOT pre-decide WHICH path wins.

---

## Anchors (load-bearing for the cycle)

- **HEAD baseline:** `bd72639` at `origin/main` (PHASE2C_11 SEALED; verified at session entry)
- **Pytest baseline:** `tests/test_evaluate_dsr.py tests/test_wf_lineage_guard.py` = 174 passed (~2.3s)
- **Canonical successor-cycle path register:** [docs/closeout/PHASE2C_11_RESULTS.md](docs/closeout/PHASE2C_11_RESULTS.md) §6.4 + §12 (verbatim read at session entry)
- **Structural skeleton precedent:** [docs/phase2c/PHASE2C_11_SCOPING_DECISION.md](docs/phase2c/PHASE2C_11_SCOPING_DECISION.md) (637 lines / 9 sections §0-§8)
- **6-question framework precedent:** PHASE2C_11_SCOPING_DECISION §3 (uncertainty attacked / evidence load-bearing / proves-or-falsifies / what remains unresolved / why outrank others / MVD)
- **Discipline anchors:** [METHODOLOGY_NOTES.md](docs/discipline/METHODOLOGY_NOTES.md) §16 anchor-prose-access + §17 anti-momentum-binding + §10 anti-pre-naming + §19 spec-vs-empirical-reality drift

## Path register (verbatim from §6.4; arc designation deferred to §4.4 SEAL)

| Path | Register-class | Status |
|---|---|---|
| (a) Mechanism deeper investigation | post-PHASE2C_9 register at depth >light-touch | register-class-eligible (free-standing path) |
| (c) Calibration variation | mining-batch calibration probe | register-class-eligible (free-standing path) |
| (g) Breadth expansion | new candidate basis at different mining configuration | register-class-eligible (free-standing path) |
| Dependent path: canonical-DSR scope expansion | §4.7 deferred prerequisite (Path A DSL-canonical-hash mapping OR Path B audit_v1 --persist-trades engine re-run) | register-class-eligible **infrastructure-gated dependent path** (unlikely to overturn artifact-evidence per §6.4) |
| (f) Phase 3 trajectory | not authorized at current candidate set | foreclosed for current survivor set unless later cycle identifies different validated candidate basis |

**Dependent-path framing (per ChatGPT M3 refinement):** canonical-DSR is infrastructure-gated, NOT a free-standing peer of (a)/(c)/(g). It sits downstream of PHASE2C_11_PLAN v3.2 §4.7 prerequisite paths. Evaluated as dependent path requires two specific tests (see §3.4 below) rather than the standard free-standing 6-question framework alone.

## Pre-commit verification gate (binding throughout cycle)

Per advisor §5 prevention discipline + §19 spec-vs-empirical-reality finding pattern (10 cumulative within PHASE2C_11 arc; 1 instance already surfaced at this session entry — handoff "15 sections" vs canonical 17):

- **Every numerical/textual reference** to PHASE2C_8.1 / PHASE2C_9 / PHASE2C_10 / PHASE2C_11 substance MUST be empirically verified against current canonical artifact (file:line citation, content match) BEFORE citing in §1 locked inputs / §3 per-path evaluation / §4 selection / §6 / §8 cross-references.
- **Cumulative count claims** (§19 instance count, advisor §5 instance count, etc.) MUST be empirically verified against METHODOLOGY_NOTES §19 + closeout MD §14 + canonical seal commit messages BEFORE citing.
- **Pre-commit verification gate** fires immediately before any commit at this cycle (scoping-doc seal + Phase Marker advance). Drift caught at this gate triggers patch + re-verify, NOT silent proceed.
- **Carry-forward** any §19 instance surfaced at this cycle to next methodology consolidation cycle as codification candidate.

---

## Milestone 1: Read upstream canonical references

**Files (read-only):**
- `docs/phase2c/PHASE2C_10_SCOPING_DECISION.md` (full)
- `docs/phase2c/PHASE2C_11_SCOPING_DECISION.md` (full; structural skeleton precedent)
- `docs/closeout/PHASE2C_11_RESULTS.md` §0 + §6.4 + §12 + §14 (carry-forwards)
- `docs/phase2c/PHASE2C_11_PLAN.md` v3.2 §4.7 (canonical-DSR Path A / Path B prerequisite anchors)
- `docs/closeout/PHASE2C_8_1_RESULTS.md` (n=4 baseline composition reference for path (g) evaluation)
- `docs/closeout/PHASE2C_9_RESULTS.md` §3 + §6 + §7 + §8 (mechanism-side context for path (a) evaluation)
- `docs/discipline/METHODOLOGY_NOTES.md` §10 + §16 + §17 + §19

- [ ] **Step 1: Read PHASE2C_10 + PHASE2C_11 scoping decision MDs end-to-end**

Lock: 8-section skeleton (§0-§8); 6-question framework at §3; §4.4 anti-pre-naming option (ii) wording precedent; §4.5 anti-momentum-binding transparency note; sub-spec pre-registration paragraph at §6 / §7 carry-forward register.

- [ ] **Step 2: Read closeout MD §6.4 + §12 + §14 + PHASE2C_11_PLAN v3.2 §4.7 verbatim**

Lock: register-class-eligible path table verbatim; §4.7 Path A (DSL-canonical-hash mapping infrastructure) + Path B (audit_v1 --persist-trades engine re-run) wording; carry-forward inventory at §14.

- [ ] **Step 3: Read PHASE2C_8.1_RESULTS + PHASE2C_9_RESULTS for path-context grounding**

Lock: PHASE2C_8.1 n=4 baseline composition (relevant for (g) evaluation — what "different mining configuration" means relative to b6fcbf86); PHASE2C_9 light-touch mechanism reconstruction depth (relevant for (a) evaluation — what "depth greater than light-touch" means).

- [ ] **Step 4: Read METHODOLOGY_NOTES §10 + §16 + §17 + §19**

Lock: §10 anti-pre-naming standing discipline at scoping-cycle register; §16 anchor-prose-access at multi-hundred-line interpretive deliverable register; §17 procedural-confirmation at first-commit-before-prose-access; §19 spec-vs-empirical-reality drift monitoring.

**Success:** structural + path-context + discipline anchors loaded. No commit at this milestone.

---

## Milestone 2: Author §0 + §1 + §2 of scoping decision MD

**Files:**
- Create: `docs/phase2c/PHASE2C_12_SCOPING_DECISION.md` (working draft)

**§0 Document scope and structure:** filename + doc-type lock; engagement mode (reviewer-input-assisted authoring; Charlie-register authorization gate); structural reference to PHASE2C_10 / PHASE2C_11 precedent; anti-pre-naming option (ii) binding language; document-version register (v1 working draft → seal at convergence).

**§1 Locked scoping inputs:**
- §1.1 Decision goal: adjudicate next empirical path after PHASE2C_11 artifact_evidence at simplified DSR-style register
- §1.2 Dominant-uncertainty entry framing (descriptive at scoping-doc entry; not pre-committed — emerges from §3 substantive comparison register)
- §1.3 Cycle budget (light-to-medium-bandwidth; ~6-10 milestones; ~60-120 min)
- §1.4 Constraint compliance (8-constraint set per PHASE2C_10/PHASE2C_11 precedent: anti-pre-naming, anti-momentum-binding, sub-spec pre-registration discipline, register-class-bounded scope, etc.)

**§2 Path enumeration:** verbatim path register from §6.4 (table reproduced); path (f) status preserved; canonical-DSR scope expansion explicitly listed.

- [ ] **Step 1: Draft §0 + §1 + §2 prose**

Author into working draft file. Anti-pre-naming discipline: prose throughout §0-§2 must use "the selected path" / "the successor arc" framing, NEVER pre-commit to a specific path letter.

- [ ] **Step 2: Verify against PHASE2C_11_SCOPING_DECISION precedent**

Cross-check section structure + locked-input enumeration + path register table format match precedent.

- [ ] **Step 3: Save working draft (no commit yet)**

```bash
ls -la docs/phase2c/PHASE2C_12_SCOPING_DECISION.md
```

Expected: file exists, ~150-250 lines (§0-§2 only at this milestone).

**Success:** §0-§2 authored with anti-pre-naming framing preserved.

---

## Milestone 3: Author §3 per-path evaluation (per-path serialized; 7-question framework)

**Files:**
- Modify: `docs/phase2c/PHASE2C_12_SCOPING_DECISION.md` (extend with §3)

**§3 structure (per PHASE2C_11_SCOPING_DECISION §3 precedent: per-path serialized, NOT interleaved 4×7 matrix):**

**Seven-question framework** for free-standing paths (per path: 6 base + 1 kill criterion per ChatGPT refinement):
1. What uncertainty does this path attack?
2. What evidence says this uncertainty is load-bearing?
3. What would this path prove or falsify?
4. What would remain unresolved after this path?
5. Why should this path outrank the others now?
6. What is the minimum viable deliverable?
7. **Kill criterion (per ChatGPT M3 refinement):** Can this path falsify the current PHASE2C_11 artifact_evidence within one cycle? (yes / no / conditional with bridge-condition specification)

**Kill criterion binding:** "no" answer triggers automatic downgrade with explicit reasoning at register-precision. "Conditional" requires bridge-condition specification at register-precision. "Yes" passes the floor but does NOT auto-promote — selection still emerges from §4 dominant-uncertainty comparison.

**Dependent-path framework** for §3.4 canonical-DSR (per ChatGPT M3 refinement; replaces standard 7-question for this section):
- D1: Does it unlock a strictly stronger test than PHASE2C_11 simplified register? (unlock-strength test)
- D2: Is the prerequisite cost (Path A DSL-canonical-hash mapping infrastructure OR Path B audit_v1 --persist-trades engine re-run) justified vs alternative paths achieving comparable disambiguation? (cost-justification test)
- Both tests at affirmative register required for register-class-eligible promotion at §4 selection register.

Paths to evaluate at §3 (per-path serialized; one path's full evaluation per Step before moving to next):
- §3.1 Path (a) — Mechanism deeper investigation (free-standing; 7 questions)
- §3.2 Path (c) — Calibration variation (free-standing; 7 questions)
- §3.3 Path (g) — Breadth expansion (free-standing; 7 questions)
- §3.4 Dependent path: canonical-DSR scope expansion (D1 + D2 dependent-path framework)
- §3.5 Path (f) status disposition (brief; not register-class-eligible at this scoping cycle)

- [ ] **Step 1: Author §3.1 path (a) evaluation (full 7 questions; serialized; checkpoint at completion)**

Anchor on PHASE2C_9 §3 light-touch mechanism reconstruction (verify line/citation counts against canonical at pre-commit gate); PHASE2C_9 §6 lone-survivor walkthrough; PHASE2C_9 §7 Case C sub-registers; what "depth greater than light-touch" means at register-precision. Q7 kill criterion: can mechanism deeper investigation falsify PHASE2C_11 artifact_evidence within one cycle? Reason at register-precision (mechanism findings → could shift candidate population → could shift artifact/signal disambiguation? OR mechanism findings → orthogonal to existence question?).

Pre-commit verification gate: every PHASE2C_9 §3 / §6 / §7 numerical or textual citation empirically verified against canonical before §3.1 finalize.

**Checkpoint at §3.1 completion:** surface to Charlie for visibility before §3.2 fires.

- [ ] **Step 2: Author §3.2 path (c) evaluation (full 7 questions; serialized; checkpoint at completion)**

Anchor on PHASE2C_8.1 batch b6fcbf86 mining configuration (verify against canonical at pre-commit gate); what "calibration variation" means relative to current mining-batch calibration; whether calibration probe at different parameters would address dominant uncertainty class. Q7 kill criterion: can calibration variation at one cycle falsify artifact_evidence? (e.g., do calibration-shifted candidates produce signal at simplified DSR-style register?)

Pre-commit verification gate: every PHASE2C_8.1 batch reference + mining-config detail empirically verified.

**Checkpoint at §3.2 completion:** surface to Charlie before §3.3 fires.

- [ ] **Step 3: Author §3.3 path (g) evaluation (full 7 questions; serialized; checkpoint at completion)**

Anchor on PHASE2C_8.1 n=4 baseline composition (verify against canonical); what "different mining configuration" means relative to b6fcbf86; whether breadth expansion at new candidate basis addresses dominant uncertainty class OR defers signal-vs-artifact disambiguation. Q7 kill criterion: can a new candidate basis at different mining configuration produce signal at simplified register, falsifying the "no signal at this candidate population" artifact reading? Note: "different candidate basis MAY produce different result" wording at closeout MD §6.7 directly speaks to this.

Pre-commit verification gate: every PHASE2C_8.1 n=4 baseline reference empirically verified.

**Checkpoint at §3.3 completion:** surface to Charlie before §3.4 fires.

- [ ] **Step 4: Author §3.4 dependent path canonical-DSR evaluation (D1 + D2 framework; serialized; checkpoint)**

Per ChatGPT M3 refinement — dependent-path framing replaces standard 7-question for this section.

Anchor on PHASE2C_11_PLAN v3.2 §4.7 Path A (DSL-canonical-hash mapping infrastructure) + Path B (audit_v1 --persist-trades engine re-run) prerequisite specifications (verify against canonical at pre-commit gate). Closeout MD §6.4 explicit wording: "unlikely to overturn artifact-evidence per §6.4".

D1 unlock-strength test: would canonical Bailey-López de Prado DSR (with skewness/kurtosis/autocorrelation correction) at the same candidate population produce result *strictly stronger* than PHASE2C_11 simplified register? Or would it merely confirm at canonical register what simplified register already established?

D2 cost-justification test: is Path A or Path B prerequisite cost (engineering work to either build canonical-hash mapping infrastructure OR re-run audit_v1 with --persist-trades + re-build per-trade-CSV pipeline) justified relative to alternative paths (a)/(c)/(g) achieving comparable disambiguation at lower cost?

Pre-commit verification gate: every PHASE2C_11_PLAN v3.2 §4.7 reference empirically verified.

**Checkpoint at §3.4 completion:** surface to Charlie before §3.5 fires.

- [ ] **Step 5: Author §3.5 path (f) status disposition (brief)**

Brief disposition reproducing closeout MD §6.4 status verbatim: foreclosed for current survivor set unless later cycle identifies different validated candidate basis.

- [ ] **Step 6: Verify §3 anti-pre-naming discipline + cross-section consistency**

Throughout §3.1-§3.4, framing must be at register-class evaluation, NOT pre-committed selection. "Why outrank others now" question must be answered at register-class comparison register, NOT at predetermined-winner register. Cross-section consistency check: Q7 kill criterion answers across (a)/(c)/(g) consistent at logical register; D1/D2 dependent-path framing at §3.4 distinct from but compatible with free-standing framing at §3.1-§3.3.

**Success:** §3 evaluated per-path-serialized with 7-question framework on free-standing paths + D1/D2 dependent-path framework on canonical-DSR; per-path checkpoints surfaced to Charlie; pre-commit verification gates fired at each path; no pre-naming leak; cross-section consistency CLEAN.

---

## Milestone 4: Author §4 + §5 + §6 + §7 + §8

**Files:**
- Modify: `docs/phase2c/PHASE2C_12_SCOPING_DECISION.md` (extend with §4-§8)

**§4 Selection adjudication and arc designation:**
- §4.1 Dominant uncertainty finding — emerges from §3 substantive comparison register
- §4.2 Selected path — selected per §4.1 dominant uncertainty
- §4.3 Rejected alternatives — grounded in dominant-uncertainty-class reasoning per rejected path
- §4.4 Arc designation — anti-pre-naming option (ii) commits at THIS section, NOT before; arc named per selected path-class
- §4.5 Adjudication transparency note — anti-momentum-binding discipline; reviewer-lean (if any) registered as input not selection

**§5 Scoping-cycle guardrails:** ChatGPT scoping-doc skeleton guardrails (do-not patterns) + anti-momentum-binding discipline at §3 per-path evaluation register-precision + **one-cycle-falsifiability is selection floor (per ChatGPT M3 refinement; binding guardrail, not optional warning): any path that cannot falsify PHASE2C_11 artifact_evidence within one cycle is downgraded automatically; sub-spec drafting cycle preserves this discipline at MVD register-precision**.

**§6 Carry-forward to sub-spec drafting cycle:**
- **§6.1 Scope register:** sub-spec scope per selected path (path-specific; sub-spec drafting cycle is separate fresh session post-scoping-cycle SEAL)
- **§6.2 Sub-spec pre-registration paragraph framework (per PHASE2C_11_SCOPING_DECISION §4.2 + §6.2 precedent; §19 alignment patch):** **anti-p-hacking guardrail at selection register** — sub-spec MUST define candidate population + trial count + return metric + Sharpe estimation method (or path-equivalent metric formulation) + null/deflation assumptions BEFORE any result is computed. Pre-registration locks at sub-spec drafting cycle; post-results parameter adjustment forbidden at register-precision register.
- **§6.3 Methodology candidate carry-forward register:** §19 instances surfaced this scoping cycle (handoff §19 instances; cumulative count register at next methodology consolidation cycle); other carry-forward items per scoping cycle

**§7 Verification chain and dual-reviewer disposition (per PHASE2C_11_SCOPING_DECISION §7 precedent; §19 alignment patch):**
- §7.1 Verification anchor chain (PHASE2C_11 SEALED at bd72639 + tag at 5dba0df; closeout MD §6.4 + §12 + §14; PHASE2C_11_PLAN v3.2 §4.7; METHODOLOGY_NOTES §10/§16/§17; PHASE2C_8.1/9 RESULTS path-context anchors)
- §7.2 Dual-reviewer disposition (ChatGPT first-pass + Claude advisor full-prose-access pass per §16; Codex skipped per `feedback_codex_review_scope.md`; both reviewers authorize commit; patches surfaced applied; THEN seal)
- §7.3 Pre-fire audit pattern observation (per METHODOLOGY_NOTES §16 ### Failure-mode signal §3.5 fold-in)

**§8 Cross-references (per PHASE2C_11_SCOPING_DECISION §8 precedent; §19 alignment patch):**
- §8.1 PHASE2C_11 cross-references (closeout MD §6.4 + §12 + §14; plan v3.2 §4.7; scoping decision precedent)
- §8.2 PHASE2C_10 + earlier cross-references (PHASE2C_10_SCOPING_DECISION precedent; PHASE2C_8.1/9 RESULTS path-context)
- §8.3 METHODOLOGY_NOTES cross-references (§10 anti-pre-naming + §16 anchor-prose-access + §17 procedural-confirmation + §19 spec-vs-empirical-reality)
- §8.4 CLAUDE.md cross-references (Phase Marker PHASE2C_11 SEALED entry)

**§19 alignment patch note:** plan v1 had §7 = "Sub-spec pre-registration paragraph standalone" + §8 = "Forward-pointer register"; canonical PHASE2C_11_SCOPING_DECISION precedent has §7 = Verification chain + §8 = Cross-references with sub-spec pre-registration integrated at §4.2 (selected path wording) + §6.2 (sub-spec carry-forward framing). Patch applied at this register pre-M2-fire per Charlie-register authorization. Symmetric to v3.2 §5.4 spec patch precedent (descriptive-register correction fired before downstream deliverable that cites the corrected anchor).

- [ ] **Step 1: Adjudicate §4.1 dominant uncertainty finding**

Substantive: emerges from §3 comparison; NOT predetermined. The §3 evaluations across (a)/(c)/(g)/(canonical-DSR) collectively identify which uncertainty class is dominant. This adjudication is the load-bearing decision; downstream §4.2-§4.4 follow.

- [ ] **Step 2: Author §4.2 selection + §4.3 rejected alternatives**

Each rejection grounded in dominant-uncertainty-class reasoning relative to selection (per PHASE2C_11_SCOPING_DECISION §4.3 precedent: "downstream of dominant uncertainty class" wording; "would defer disambiguation" wording).

- [ ] **Step 3: Author §4.4 arc designation**

Filename `PHASE2C_12_SCOPING_DECISION.md` selects sequential numbering at scoping doc draft fire (NOT pre-commitment of arc *content*; just the arc *number*). Arc designation that THIS scoping decision selects: e.g., "PHASE2C_12 = <selected-path-class> arc". Designation committed at §4.4 SEAL, NOT before.

- [ ] **Step 4: Author §4.5 adjudication transparency note**

Anti-momentum-binding discipline: any reviewer lean registered as scoping-cycle input not selection. §3 per-path evaluation against locked decision goal + constraints produced the selected path independently of reviewer lean. Selection grounded in §3 substantive comparison register.

- [ ] **Step 5: Author §5 + §6 + §7 + §8**

§5 guardrails per scoping-doc skeleton; §6 sub-spec carry-forward (scope sketch only — sub-spec drafting cycle is separate session); §7 sub-spec pre-registration paragraph (binding); §8 cross-references.

- [ ] **Step 6: Verify draft completeness**

```bash
wc -l docs/phase2c/PHASE2C_12_SCOPING_DECISION.md
grep -n "^## " docs/phase2c/PHASE2C_12_SCOPING_DECISION.md
```

Expected: ~400-700 lines (within PHASE2C_10/PHASE2C_11 precedent envelope); 9 section headers (§0-§8).

- [ ] **Step 7: §16 anchor-prose-access full-file pass (self)**

Re-read full file end-to-end. Surface any: anti-pre-naming leaks; cross-section consistency drift; numerical-anchor errors; framing-discipline residuals. Apply patches before reviewer cycle.

**Success:** complete v1 working draft with anti-pre-naming + anti-momentum-binding discipline preserved end-to-end.

---

## Reviewer routing pattern (locked sequential per advisor refinement)

Per advisor Observation 2 + PHASE2C_11_SCOPING_DECISION precedent: **sequential** ChatGPT first-pass → apply ChatGPT-approved patches → advisor full-prose-access pass on **patched** draft (NOT parallel; NOT raw v1 to advisor).

Rationale: scoping cycle is structural-register-heavy. ChatGPT structural-overlay pass first establishes stable structural foundation; advisor prose-access pass then operates on stable post-structural draft, surfacing wording-precision and cross-section-consistency residuals (φ-Refine class) that pre-patch advisor pass might miss since structural patches reshape wording landscape.

## Milestone 5: Surface to ChatGPT first-pass (structural overlay)

**Files (read-only at this milestone):**
- `docs/phase2c/PHASE2C_12_SCOPING_DECISION.md` v1 working draft

ChatGPT pass scope:
- Structural completeness (§0-§8 all present + section coverage adequate)
- 6-question framework consistency (each path scored against same 6 questions)
- Cross-reference precision against canonical anchors (PHASE2C_11_RESULTS §6.4 / §12 verbatim quote checks)
- §4.4 anti-pre-naming option (ii) wording precedent compliance
- §7 sub-spec pre-registration paragraph completeness (5 mandatory components: candidate population + trial count + return metric + Sharpe estimation + null/deflation)
- Path enumeration coverage (4 register-class-eligible paths + path (f) status)

- [ ] **Step 1: Surface draft to ChatGPT**

Provide PHASE2C_12_SCOPING_DECISION.md v1 + scoping-doc skeleton context + ChatGPT structural-overlay pass focus.

- [ ] **Step 2: Receive ChatGPT findings**

Categorize: structural-completeness / framework-consistency / cross-reference-precision / anti-pre-naming / pre-registration / coverage.

**Success:** ChatGPT findings registered for Milestone 7 adjudication.

---

## Milestone 6: Surface to Claude advisor (full-prose-access pass on patched draft)

**Files (read-only at this milestone):**
- `docs/phase2c/PHASE2C_12_SCOPING_DECISION.md` **post-ChatGPT-patch** version (sequential pattern locked per reviewer routing section above; ChatGPT-approved patches MUST be applied before advisor pass fires)

Advisor pass scope per METHODOLOGY_NOTES §16:
- Wording precision at register-class lockpoints
- §3 per-path evaluation register-precision (each path evaluated at register-class, not at predetermined-winner register)
- §4.1 dominant uncertainty finding emerging from §3 comparison (not from §4.1 declaration)
- §4.5 anti-momentum-binding transparency note soundness
- §6 sub-spec carry-forward scope (sketch only, no sub-spec drafting at scoping cycle)
- §7 sub-spec pre-registration anti-p-hacking guardrail soundness
- Anchor cross-section consistency (e.g., §3.4 canonical-DSR anchors match §4.7 plan v3.2 wording)

- [ ] **Step 1: Surface draft to Claude advisor**

Full prose access; substantive register pass.

- [ ] **Step 2: Receive advisor findings**

Categorize per reviewer-suggestion-adjudication memory (`feedback_reviewer_suggestion_adjudication.md`): per-finding articulation + approve/pushback rationale.

**Success:** advisor findings registered for Milestone 7 adjudication.

---

## Milestone 7: Adjudicate findings + apply patches + convergence verify

**Files:**
- Modify: `docs/phase2c/PHASE2C_12_SCOPING_DECISION.md` (apply patches)

Per `feedback_reviewer_suggestion_adjudication.md`: each ChatGPT + advisor finding receives:
1. What the suggestion claims
2. Is it factually correct + applicable in this context
3. Approve with rationale OR push back with rationale

Per `feedback_codex_review_scope.md`: when dual-reviewer fires, BOTH reviewer registers adjudicated. Codex skipped at scoping-doc register per scoping-doc precedent.

- [ ] **Step 1: Per-finding adjudication (ChatGPT + advisor combined)**

Enumerate each finding; categorize approve / pushback / observation-only-no-patch.

- [ ] **Step 2: Apply approved patches**

Edit PHASE2C_12_SCOPING_DECISION.md per approved findings.

- [ ] **Step 3: Fresh-register full-file pass per §17 sub-rule 4**

Section-targeted patches don't preclude full-file final pass. Re-read entire file end-to-end after patches applied; surface any cross-section consistency drift / framing-discipline residuals introduced by patch ripple.

- [ ] **Step 4: If full-file pass surfaces residuals → patch + re-verify**

Iterate until full-file pass returns CLEAN.

- [ ] **Step 5: Surface convergence summary to Charlie**

| Reviewer | Findings | Approved | Pushed back | Status |
|---|---|---|---|---|
| ChatGPT | N | N_a | N_p | converged / outstanding |
| Advisor | M | M_a | M_p | converged / outstanding |

**Success:** dual-reviewer convergence reached at substantive register; full-file pass CLEAN.

---

## Milestone 8: Charlie-register authorization → seal + advance + push + ping

**Files:**
- Final: `docs/phase2c/PHASE2C_12_SCOPING_DECISION.md` (sealed)
- Modify: `CLAUDE.md` (Phase Marker advance — separate commit)

Per `feedback_authorization_routing.md`: Charlie-register authorization required at:
1. Scoping-doc seal commit fire
2. Phase Marker advance commit fire
3. Push to origin

Per §7.4 / Path A.2 register-event boundary discipline: scoping-doc seal + Phase Marker advance = SEPARATE COMMITS (NEVER bundled). NO tag at scoping cycle SEAL (tag fires only at arc-level SEAL per PHASE2C_10/PHASE2C_11 precedent).

- [ ] **Step 1: Surface convergence + readiness to Charlie**

Surface: convergence summary; section-by-section readiness; commit message drafts (scoping-doc seal + Phase Marker advance); push timing preference (P1 bundled vs P2 separate).

- [ ] **Step 2: On Charlie authorization — seal scoping-doc commit**

```bash
git add docs/phase2c/PHASE2C_12_SCOPING_DECISION.md
git commit -m "$(cat <<'EOF'
docs(phase2c-12): scoping decision seal — <selected path class> arc designation per anti-pre-naming option (ii) + sub-spec pre-registration paragraph

<short body: §3 per-path evaluation across 4 register-class-eligible paths + §4.1 dominant uncertainty + §4.4 arc designation + §7 sub-spec pre-registration anti-p-hacking guardrail; reviewer convergence at ChatGPT + Claude advisor>
EOF
)"
```

- [ ] **Step 3: Verify scoping-doc seal commit**

```bash
git log --oneline -3
git diff HEAD~1 HEAD --stat
```

Expected: most recent commit = scoping-doc seal; touched file = `docs/phase2c/PHASE2C_12_SCOPING_DECISION.md` only.

- [ ] **Step 4: Author Phase Marker advance + commit (SEPARATE)**

Edit CLAUDE.md Phase Marker section:
- New "Current phase" entry: PHASE2C_12 scoping cycle SEALED + path register entry + arc designation
- Demote prior PHASE2C_11 SEALED entry to "Prior phase" (or consolidate per consolidation precedent)
- Add scoping decision to "Completed" list

```bash
git add CLAUDE.md
git commit -m "$(cat <<'EOF'
docs(phase2c-12): CLAUDE.md Phase Marker advance — PHASE2C_12 scoping cycle SEALED + arc designation per §4.4
EOF
)"
```

- [ ] **Step 5: Verify Phase Marker advance commit**

```bash
git log --oneline -3
git diff HEAD~1 HEAD --stat
```

Expected: most recent commit = Phase Marker advance; touched file = `CLAUDE.md` only; scoping-doc seal commit NOT modified.

- [ ] **Step 6: Push to origin**

```bash
git push origin main
```

- [ ] **Step 7: Post-push verification**

```bash
git rev-parse HEAD
git rev-parse origin/main
git status --short
python -m pytest tests/test_evaluate_dsr.py tests/test_wf_lineage_guard.py -q
```

Expected: HEAD === origin/main; working tree clean modulo carry-forward; 174 passed.

- [ ] **Step 8: Dual-channel ping per `feedback_long_task_pings.md`**

PushNotification (terminal) + Discord webhook (phone). Status line under 200 chars; lead with actionable bit; include commit SHAs + test verdict.

```bash
curl -s -H 'Content-Type: application/json' \
  -d '{"content":"PHASE2C_12 scoping cycle SEALED + pushed: <selected path class> arc; <SHA scoping-seal> + <SHA marker-advance>; pytest 174 GREEN"}' \
  'https://discord.com/api/webhooks/1500286755562193019/0r6qRvlXj6uON-qDXPPW6VmPQKnbkrCrVZj1yROOHEKu96mPO1AbtOzYvkvvq9FzwfDR' \
  > /dev/null
```

**Success:** PHASE2C_12 scoping cycle SEALED + pushed; HEAD synced; pytest GREEN; dual-channel ping fired.

---

## What NOT to do (binding from session entry forward)

- DO NOT pre-commit specific successor arc direction at any forward-pointer register before §4.4 SEAL
- DO NOT bundle scoping-doc seal commit with Phase Marker advance commit
- DO NOT tag at scoping cycle SEAL (tag fires only at arc-level SEAL per PHASE2C_10/PHASE2C_11 precedent)
- DO NOT skip Charlie-register authorization at any operational fire boundary per `feedback_authorization_routing.md`
- DO NOT modify any sealed PHASE2C_11 substance (PHASE2C_11_PLAN v3.2, PHASE2C_11_STEP3_DELIVERABLE, PHASE2C_11_RESULTS, _step3_result.json)
- DO NOT mutate §3 PHASE2C_11 lockpoints retroactively
- DO NOT bulk-accept reviewer findings; per-finding adjudication required
- DO NOT skip dual-channel ping at session close natural fire boundary
- DO NOT inherit reviewer lean from PHASE2C_11 arc; selection emerges from §3 substantive comparison register independent of upstream lean
- DO NOT fold methodology consolidation cycle into this scoping cycle (separate fresh session per pacing discipline)
- DO NOT use Codex review at this scoping-doc register (per `feedback_codex_review_scope.md`)
- DO NOT paraphrase any anchor; empirically verify against canonical state at every commit boundary per advisor §5 discipline

---

## Success criteria (cycle-level)

- §6.4 path register evaluated at 6-question framework across (a)/(c)/(g)/(canonical-DSR) with (f) status preserved
- §4.4 arc designation committed at SEAL register, NOT before
- §7 sub-spec pre-registration paragraph (5 mandatory components) present + binding
- ChatGPT + advisor reviewer convergence reached at substantive register
- Per-finding adjudication discipline applied (`feedback_reviewer_suggestion_adjudication.md`)
- Charlie-register authorization at every operational fire boundary
- Scoping-doc seal commit + Phase Marker advance commit = SEPARATE
- No tag at scoping cycle SEAL
- HEAD synced with origin/main post-push
- pytest 174 GREEN preserved
- Dual-channel ping fired at session close natural fire boundary
- Working tree clean modulo carry-forward (.claude/, docs/d7_stage2c/*) at session close

---

## Estimated bandwidth

| Milestone | Effort | Cumulative |
|---|---|---|
| M1 Read references | 1 turn | ~10 min |
| M2 §0-§2 author | 1 turn | ~25 min |
| M3 §3 4×6 evaluation | 2-3 turns | ~50-70 min |
| M4 §4-§8 author | 1-2 turns | ~70-90 min |
| M5 ChatGPT pass | 1 turn (Charlie surface) | ~80-100 min |
| M6 Advisor pass | 1 turn (Charlie surface) | ~90-110 min |
| M7 Adjudicate + patch | 1 turn | ~100-120 min |
| M8 Seal + advance + push + ping | 1 turn | ~110-130 min |

Total: 8-10 turns; ~110-130 min. Within handoff estimate (~60-120 min light-to-medium-bandwidth).

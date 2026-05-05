# PHASE2C_13 Sub-Spec Drafting Cycle Execution Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
>
> **Adaptation note:** This is a methodology documentation cycle (process / spec only; no code; no tests). The skill template's TDD framing is replaced with: section draft → self-review against scoping decision §6 binding scope → checkpoint. Code-test gates are replaced with anchor-prose-access verification gates per METHODOLOGY_NOTES §16. Each task = one § OR one cycle phase (reviewer pass / verification / SEAL).

**Goal:** Author canonical sub-spec [`docs/phase2c/PHASE2C_13_PLAN.md`](../../phase2c/PHASE2C_13_PLAN.md) covering Items 1-7 codification + §9.0c register-class taxonomy 3-class sub-rule + Carry-forwards A/B/C, with full sub-spec drafting cycle pattern (draft → triple-reviewer pass → pre-fire empirical verify → Charlie SEAL bundle) per PHASE2C_10/11/12 precedent.

**Architecture:** Bite-sized § authoring against scoping decision §6 binding scope → triple-reviewer convergence (ChatGPT structural overlay + Claude advisor full-prose-access + Claude Code register-precision) with reasoned per-fix adjudication → pre-fire V#-chain verification → Charlie-authorized SEAL bundle. Item 7 anti-meta-pattern discipline operating REAL-TIME during all tasks (real-time §9.0c instance handling; mitigation TIMING-only mutation per ChatGPT-load-bearing boundary clause).

**Tech Stack:** Markdown authoring; git for commit + tag + push; Bash for file/grep verification; Read for prose-access; Edit for surgical patches; planning skill for cycle pacing. NO API spend (process / spec only). NO new code, NO new tests, NO batch fire.

---

## Inputs (read before any task)

- [`docs/phase2c/PHASE2C_13_SCOPING_DECISION.md`](../../phase2c/PHASE2C_13_SCOPING_DECISION.md) — full 422-line scoping decision SEAL artifact (binding scope source)
- [`docs/closeout/PHASE2C_12_RESULTS.md`](../../closeout/PHASE2C_12_RESULTS.md) §10 — original methodology consolidation list source (consume; do NOT re-derive per scoping decision §1.4 constraint 6)
- [`docs/discipline/METHODOLOGY_NOTES.md`](../../discipline/METHODOLOGY_NOTES.md) §13-§20 — existing tier framework (refinement target for Carry-forward C; V#10 verified at scoping decision)
- [`docs/phase2c/PHASE2C_10_PLAN.md`](../../phase2c/PHASE2C_10_PLAN.md) — methodology consolidation cycle sub-spec drafting precedent (PHASE2C_10 = 467 lines; PHASE2C_13 estimated 600-900 lines)
- [`docs/phase2c/PHASE2C_11_PLAN.md`](../../phase2c/PHASE2C_11_PLAN.md) + [`docs/phase2c/PHASE2C_12_PLAN.md`](../../phase2c/PHASE2C_12_PLAN.md) — full sub-spec drafting cycle pattern precedents
- [`CLAUDE.md`](../../../CLAUDE.md) Phase Marker — PHASE2C_13 entry scoping cycle SEALED entry (canonical state)
- Memory: [`feedback_authorization_routing.md`](../../../.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_authorization_routing.md), [`feedback_reviewer_suggestion_adjudication.md`](../../../.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_reviewer_suggestion_adjudication.md), [`feedback_codex_review_scope.md`](../../../.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_codex_review_scope.md), [`feedback_claude_md_freshness.md`](../../../.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_claude_md_freshness.md), [`feedback_long_task_pings.md`](../../../.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_long_task_pings.md)

---

## File Structure

**Create (one file):**
- `docs/phase2c/PHASE2C_13_PLAN.md` — canonical sub-spec; ~600-900 lines / 10-15 § + sub-§

**No other files modified at sub-spec drafting cycle.** Implementation arc (PHASE2C_13_PLAN.md §5 specifies Steps 1-N) appends to `docs/discipline/METHODOLOGY_NOTES.md`; Phase Marker advances at `CLAUDE.md` happen at SEAL; both are POST sub-spec SEAL register and out of this plan's scope.

**Sub-spec section structure (10 §; per scoping decision §6 + handoff §3.2):**

| §   | Content                                                     | Est. lines |
| --- | ----------------------------------------------------------- | ---------- |
| §0  | Status / anchor / discipline anchors                        | 30-50      |
| §1  | Goal + immediate context (PHASE2C_13 cycle scope summary)   | 40-60      |
| §2  | Items 1-7 codification (7 sub-§)                            | 250-350    |
| §3  | §9.0c register-class taxonomy 3-class sub-rule              | 60-90      |
| §4  | Carry-forwards A/B/C (3 sub-§; C has C-1 + C-2 sub-deliv)   | 150-220    |
| §5  | Implementation arc Steps 1-N specification                  | 60-90      |
| §6  | Closeout deliverable scope specification                    | 30-50      |
| §7  | Verification chain V#1-V#N                                  | 40-60      |
| §8  | Reviewer pass cycle disposition                             | 20-40      |
| §9  | Cross-references                                            | 30-50      |
|     | **Total**                                                   | 710-1060   |

Sub-spec writes in section order §0 → §9; reviewer pass cycle fires after full draft (handoff §4 step 4 ordering).

---

## Discipline anchors operating during all tasks

These apply to EVERY task below; not repeated per-task.

1. **Charlie-register-only authorization** ([feedback_authorization_routing.md](../../../.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_authorization_routing.md)) — only operational fires (commits to repo, pushes, METHODOLOGY_NOTES.md modification) require Charlie auth. Authoring/editing the sub-spec working draft is in-scope under Q-S26 already-granted auth; SEAL commit needs separate Charlie auth at Task 22.
2. **Anti-momentum-binding** — every executable-basis HEAD change requires explicit Charlie re-confirmation; auth boundaries register-class-distinct, never implicitly carried.
3. **Reasoned reviewer adjudication** ([feedback_reviewer_suggestion_adjudication.md](../../../.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_reviewer_suggestion_adjudication.md)) — never bulk-accept reviewer edits; per-fix verification before convergence.
4. **Item 7 anti-meta-pattern discipline (REAL-TIME during all tasks)** — surface §9.0c instances at occurrence; mitigate immediately per (a) lightweight tracking + (c) boundary-fire mitigation review combined; (b) recursive mini-codification REJECTED. **Boundary clause (binding):** TIMING-only mutation, NOT taxonomy/counting. Maintain running §9.0c instance log during cycle.
5. **§19 spec-vs-empirical-reality finding pattern (REAL-TIME during all tasks)** — surface §19 instances at finding register; cumulative count tracked at sub-spec deliverable §-cumulative-count register. Open question for sub-spec to codify (per advisor pre-drafting Obs 4): does Item 7 broaden from §9.0c-only to also include §19? Advisor lean: include §19 (spirit applies broadly); sub-spec drafting cycle codifies. PHASE2C_13 entry §19 instance #1 (tag-push divergence, closed real-time at Q-S25 (A)) is a concrete case-study for this codification.
6. **Codex skip at sub-spec drafting cycle register** ([feedback_codex_review_scope.md](../../../.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_codex_review_scope.md)) — sub-spec is process / spec scope, not code; Codex MAY fire at implementation arc Step boundaries if Carry-forward B evaluation indicates code change at later cycle.
7. **§17 sub-rule 4 recursive operating rule** — full-file prose-access pass at sealed-commit register; section-targeted patches do NOT preclude need for full-file final pass.
8. **CLAUDE.md freshness discipline** ([feedback_claude_md_freshness.md](../../../.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_claude_md_freshness.md)) — Phase Marker advance happens at sub-spec SEAL bundle (Task 22).
9. **PushNotification + Discord** ([feedback_long_task_pings.md](../../../.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_long_task_pings.md)) — fire on long task completion (full draft completion + SEAL).
10. **Bilingual concept explanation** when surfacing difficult methodology concepts (e.g., Item 7 boundary clause; Strong-tier bar criteria) for Charlie comprehension.

---

## §9.0c + §19 log mechanics specification (pre-Task-1)

**Charlie auth Q-S29 APPROVED:** §9.0c + §19 cycle-internal running log mechanics codified pre-Task-1 to prevent implementer-time mechanics decision (which is itself a §9.0c instance candidate at sub-spec drafting register).

### Format

Markdown table per advisor Obs 2 + Claude Code refinement (Item 7 boundary compliance column added).

**5-column schema:**

| Col # | Field name | Allowed values |
| ----- | ---------- | -------------- |
| 1     | Instance # | Cycle-internal monotonic counter starting at 1 (e.g., `§9.0c #1`, `§19 #1`); register-class taxonomy preserved per Item 7 boundary clause (3 classes for §9.0c: sub-spec drafting / authorization / reviewer) |
| 2     | Register-class | For §9.0c: `sub-spec drafting` / `authorization` / `reviewer`. For §19: `spec-vs-empirical-reality` (single-class per METHODOLOGY_NOTES §19) |
| 3     | Surface task+step | E.g., `Task 9 Step 9.3` — pinpoints where instance surfaced in cycle execution |
| 4     | Mitigation note (per Item 7 (a)+(c)) | Brief mitigation description per Item 7 operationalization mechanism: (a) lightweight tracking entry + (c) boundary-fire mitigation review note |
| 5     | Item 7 boundary compliance + closure status | Compliance: `Y=BOUNDARY VIOLATION` (mitigation altered §9.0c taxonomy or counting logic) / `N=clean` (mitigation altered TIMING only). Closure: `open` / `closed` / `carry-forward to PHASE2C_14+` |

### Location

**Refined location per Claude Code Obs 2 refinement (vs advisor original §3 placement):**

- **§A1 Cycle-internal §9.0c instance log** — appendix sub-§ at end of sub-spec deliverable (after §9 Cross-references)
- **§A2 Cycle-internal §19 instance log** — appendix sub-§ adjacent to §A1

**Rationale for §A1 + §A2 appendix vs §3 inline:**
- §3 = cross-cycle codification scope (3-class taxonomy sub-rule = invariant cross-cycle content)
- §A1 / §A2 = PHASE2C_13-cycle-internal operational state (cycle-bound)
- Mixing collapses register-class distinction at sub-spec deliverable structural register
- Mirrors PHASE2C_12 cycle precedent of running registers within cycle-bound deliverables

### Schema enforcement at log entry register

Every log entry MUST populate ALL 5 columns. Missing column = §9.0c instance candidate at sub-spec drafting register (recursive). Item 7 boundary compliance column specifically catches boundary-violation candidates AT log register itself (not just at sub-spec SEAL pre-fire V#-chain).

### Initial state at sub-spec scaffolding (Task 1.4)

Both §A1 + §A2 initialized as empty tables with header row + caption "PHASE2C_13 cycle-internal running log; appended at occurrence per Item 7 (a) lightweight tracking; reviewed at cycle boundary fires per Item 7 (c)". Instances accumulate across Tasks 1-21; final review + closure status fires at Task 19 Step 19.3 (full-draft self-review pass) + Task 21 Step 21.4 (post-advisor pass §9.0c instance log update).

### Pre-Task-1 entries (carry-forward from cycle entry register)

Two instances ALREADY accumulated before Task 1 fires (recorded at sub-spec scaffolding):

| # | Register-class | Surface task+step | Mitigation note | Boundary compliance + closure |
| - | -------------- | ----------------- | --------------- | ----------------------------- |
| §19 #1 | spec-vs-empirical-reality | PHASE2C_13 entry session, Q-S25 surface | Tag-push divergence (CLAUDE.md prior-cycle Phase Marker doc'd "(P1) bundled push" but `push.followTags=false` default left tag local-only); mitigation = explicit `git push origin phase2c-12-breadth-expansion-v1` per Q-S25 (A) | N=clean (mitigation = real-time tag push; §19 cumulative count register preserved); closed |
| §9.0c #1 | reviewer | PHASE2C_13 sub-spec drafting cycle entry, advisor Obs 2 surface | Meta-plan absent §9.0c log mechanics specification → sub-spec drafting register-class confusion candidate at implementer-time; mitigation = §9.0c + §19 log mechanics specification folded pre-Task-1 per Q-S29 auth | N=clean (mitigation alters meta-plan structure, NOT §9.0c taxonomy or counting); closed |

---

## Task 1: §0 Status / anchor / discipline anchors

**Files:**
- Create (start): `docs/phase2c/PHASE2C_13_PLAN.md`

- [ ] **Step 1.1: Initialize file with §0 scope and structure block**

Pattern source: PHASE2C_12_PLAN.md §0 + PHASE2C_11_PLAN.md §0. Include:
- Title line: `# PHASE2C_13 Sub-Spec — Methodology Consolidation Cycle (Items 1-7 + §9.0c sub-rule + Carry-forwards A/B/C)`
- Status line: `Status: WORKING DRAFT — pending triple-reviewer pass and Charlie SEAL`
- Anchor line: HEAD commit at sub-spec drafting cycle entry (`git rev-parse HEAD` at start)
- Anti-pre-naming clarification (PHASE2C_14/15 NOT pre-named per option (ii); references arc-designation-deferred forward-pointers only)
- §0.1 Scope (1 paragraph: bind to scoping decision §6 + handoff §3 binding)
- §0.2 Structure (10-§ enumeration matching File Structure table)
- §0.3 Discipline anchors operating at this cycle (anchor-prose-access §16, anti-momentum-binding, anti-pre-naming, empirical verification §1, procedural-confirmation §17 sub-rule 4, §19 finding pattern, Item 7 anti-meta-pattern REAL-TIME)

- [ ] **Step 1.2: Self-review §0 against scoping decision §0**

Read scoping decision §0 verbatim. Verify §0 of new sub-spec mirrors the discipline-anchor enumeration with sub-spec-cycle-specific bindings (e.g., scoping decision had instance #5+ at scoping cycle accumulation; sub-spec has instance #N+ at sub-spec drafting cycle).

- [ ] **Step 1.3: Checkpoint — log §0 line count**

Run: `wc -l docs/phase2c/PHASE2C_13_PLAN.md`
Expected: 30-50 lines (within §0 budget). If >70 lines, prune; §0 is meta-scaffolding, not substantive content.

- [ ] **Step 1.4: Initialize §A1 + §A2 empty log scaffolding (per pre-Task-1 §9.0c + §19 log mechanics specification)**

Append to sub-spec scaffolding (placed after where §9 will land; reserve appendix slot now even though body §§ not yet authored):

```markdown
---

## §A1 Cycle-internal §9.0c instance log

PHASE2C_13 cycle-internal running log; appended at occurrence per Item 7 (a) lightweight tracking; reviewed at cycle boundary fires per Item 7 (c).

| #     | Register-class | Surface task+step | Mitigation note | Boundary compliance + closure |
| ----- | -------------- | ----------------- | --------------- | ----------------------------- |
| #1    | reviewer       | PHASE2C_13 sub-spec drafting cycle entry, advisor Obs 2 surface | Meta-plan absent §9.0c log mechanics specification → sub-spec drafting register-class confusion candidate at implementer-time; mitigation = §9.0c + §19 log mechanics specification folded pre-Task-1 per Q-S29 auth | N=clean (mitigation alters meta-plan structure, NOT §9.0c taxonomy or counting); closed |

## §A2 Cycle-internal §19 instance log

PHASE2C_13 cycle-internal running log; appended at occurrence per Item 7 (a) lightweight tracking; reviewed at cycle boundary fires per Item 7 (c).

| #     | Register-class | Surface task+step | Mitigation note | Boundary compliance + closure |
| ----- | -------------- | ----------------- | --------------- | ----------------------------- |
| #1    | spec-vs-empirical-reality | PHASE2C_13 entry session, Q-S25 surface | Tag-push divergence (CLAUDE.md prior-cycle Phase Marker doc'd "(P1) bundled push" but `push.followTags=false` default left tag local-only); mitigation = explicit `git push origin phase2c-12-breadth-expansion-v1` per Q-S25 (A) | N=clean (mitigation = real-time tag push; §19 cumulative count register preserved); closed |
```

Per pre-Task-1 §9.0c + §19 log mechanics specification: §A1 + §A2 initialized with the 2 pre-Task-1 accumulated instances (1 §19 + 1 §9.0c) carried forward at sub-spec scaffolding register. Empty rows below header for accumulating cycle-internal instances during Tasks 2-21 execution.

---

## Task 2: §1 Goal + immediate context

**Files:**
- Modify: `docs/phase2c/PHASE2C_13_PLAN.md` (append §1 after §0)

- [ ] **Step 2.1: Author §1.1 Goal**

State the cycle Goal verbatim from scoping decision §1.2: "Methodology consolidation cycle (Step 9 §10.1 ratified split scope)." Add 1-2 sentences contextualizing PHASE2C_13 sub-spec drafting cycle position within the consolidation arc (post-scoping-SEAL; pre-implementation-arc).

- [ ] **Step 2.2: Author §1.2 Immediate context (PHASE2C_13 cycle scope summary)**

Reproduce scoping decision §4.2 selected scope binding (Path (ii)). Cite scoping decision §6 as binding source. List the 7 Items + §9.0c sub-rule + Carry-forwards A/B/C inputs. Do NOT re-derive content — this is a context/orientation §, not codification.

- [ ] **Step 2.3: Author §1.3 Cycle-scope budget**

Reproduce scoping decision §1.3 short-to-medium register; expected commit count for sub-spec drafting cycle alone (not implementation arc): ~5-10 commits (working draft + reviewer iterations + SEAL bundle), based on PHASE2C_10/11/12 precedent. Anchor: "PHASE2C_13 sub-spec drafting cycle = ~5-10 commits at sub-spec drafting register; implementation arc (Steps 1-N per §5) commit count separate and authored at sub-spec §5 register."

- [ ] **Step 2.4: Author §1.4 Constraints (8 items inherited from scoping decision §1.4)**

Reproduce scoping decision §1.4's 8 constraints VERBATIM with PHASE2C_13 sub-spec drafting cycle bindings. Constraints 1-8 enumerated; constraint 4 (Carry-forward B = evaluation only) and constraint 6 (no re-derivation of PHASE2C_12 §8.2) are LOAD-BEARING for sub-spec content.

- [ ] **Step 2.5: Self-review §1 against scoping decision §1**

Cross-check VERBATIM reproductions: §1.2 Goal verbatim + §1.4 8 constraints verbatim. Any drift = §19 instance candidate.

- [ ] **Step 2.6: Checkpoint — log §1 line count**

Run: `wc -l docs/phase2c/PHASE2C_13_PLAN.md`
Expected: §1 adds 40-60 lines (cumulative ~70-110).

---

## Task 3: §2.1 Item 1 — Fire-prep precondition checklist codification

**Files:**
- Modify: `docs/phase2c/PHASE2C_13_PLAN.md` (append §2.1)

- [ ] **Step 3.1: Pull Item 1 verbatim from PHASE2C_12 closeout §10.2**

Read [`docs/closeout/PHASE2C_12_RESULTS.md`](../../closeout/PHASE2C_12_RESULTS.md) §10.2 Item 1. Verbatim quote into §2.1 working draft as evidence basis. Cite line numbers from closeout (e.g., `closeout §10.2 lines NN-NN`).

- [ ] **Step 3.2: Author Item 1 codification mechanism**

Specify HOW Item 1 will be codified at METHODOLOGY_NOTES append (per §16+ append convention). Sub-§ structure for new METHODOLOGY_NOTES § (per PHASE2C_10 §13-§17 precedent: Principle / Trigger context / Application checklist / Failure-mode signal). Anchor at 4 evidence instances from PHASE2C_12 (Step 6.5 WF lineage + framework N mismatch + sensitivity table N_eff + ALLOWED_DUAL_GATE_PAIRS asymmetry).

- [ ] **Step 3.3: Specify METHODOLOGY_NOTES § slot**

Per scoping decision §5.4 + §6.7 + PHASE2C_10 precedent at §16-§20: identify candidate § number for Item 1 (e.g., new §21 if next sequential append; OR fold-in to existing § if topical fit). Cite tier disposition rationale (Strong/Medium/Weak based on instance count + cross-cycle accumulation).

- [ ] **Step 3.4: Author tier disposition + Strong-tier bar applicability check**

For each Item 1-7, document tier disposition (Strong / Medium / Weak / fold-in) WITHIN sub-spec. Item 1 has 4 evidence instances at PHASE2C_12 alone (1-cycle); cross-cycle count = TBD per PHASE2C_8-PHASE2C_11 backfill if Strong-tier candidate. **CRITICAL:** Carry-forward C (C-2) Strong-tier bar codification is its own sub-deliverable at §4.3; sub-spec authors §2.1-§2.7 tier dispositions PROVISIONALLY then re-checks against Strong-tier bar at §4.3 sub-deliverable register.

- [ ] **Step 3.5: Self-review §2.1 against scoping decision §6.2 Item 1**

Verify Item 1 codification mechanism matches scoping decision §6.2 Item 1 anchored at "4 fire-time precondition gaps as evidence basis". No drift.

- [ ] **Step 3.6: Checkpoint — §9.0c instance log update**

If §9.0c instance surfaced during §2.1 authoring (e.g., reviewer over-interpretation, register-class confusion), log to running §9.0c instance log (sub-spec maintains running register per Item 7 (a) lightweight tracking). Mitigate immediately per (c) boundary-fire mitigation review.

---

## Task 4: §2.2 Item 2 — Framework parameter pre-lock at sub-spec drafting cycle terminus

**Files:**
- Modify: `docs/phase2c/PHASE2C_13_PLAN.md` (append §2.2)

- [ ] **Step 4.1: Pull Item 2 verbatim from PHASE2C_12 closeout §10.2**

Read closeout §10.2 Item 2. Verbatim quote into §2.2. Anchor at §19 instances #5/#6/#8/#10 from PHASE2C_12 cycle as root cause evidence (handoff-noise propagation prevention).

- [ ] **Step 4.2: Author Item 2 codification mechanism**

Specify "framework parameter pre-lock" mechanism at sub-spec drafting cycle terminus: list of framework parameters (N values, threshold constants, frozenset literals) MUST be enumerated + locked at sub-spec drafting cycle SEAL boundary; modifications post-SEAL require explicit cycle-scope amendment.

- [ ] **Step 4.3: Specify METHODOLOGY_NOTES § slot + tier disposition (provisional)**

Same pattern as §2.1 Step 3.3 + 3.4.

- [ ] **Step 4.4: Self-review + §9.0c instance log update**

Same pattern as §2.1 Step 3.5 + 3.6.

---

## Task 5: §2.3 Item 3 — Step 7/8 contract standardization

**Files:**
- Modify: `docs/phase2c/PHASE2C_13_PLAN.md` (append §2.3)

- [ ] **Step 5.1: Pull Item 3 verbatim from PHASE2C_12 closeout §10.2**

Read closeout §10.2 Item 3. Verbatim quote.

- [ ] **Step 5.2: Author Item 3 codification mechanism**

Specify inter-step interface contract: Step 7 evaluation gate runner output schema → Step 8 mechanical disposition fire input schema. Standardization mechanism (e.g., schema-versioned JSON; explicit contract field enumeration). Anchor at PHASE2C_12 Step 7→Step 8 transition register-class confound surfacing as evidence basis if applicable.

- [ ] **Step 5.3: Specify METHODOLOGY_NOTES § slot + tier disposition (provisional)**
- [ ] **Step 5.4: Self-review + §9.0c instance log update**

---

## Task 6: §2.4 Item 4 — LOCKED items → executable verification function checklist

**Files:**
- Modify: `docs/phase2c/PHASE2C_13_PLAN.md` (append §2.4)

- [ ] **Step 6.1: Pull Item 4 verbatim from PHASE2C_12 closeout §10.2**

Read closeout §10.2 Item 4. Verbatim quote.

- [ ] **Step 6.2: Author Item 4 codification mechanism**

Specify the mapping: each Q-LOCKED item at sub-spec → 1 executable verification function fired at fire-prep boundary. Pattern: `def verify_Q_<n>() -> bool` returning True if LOCKED constraint preserved at fire-time. Anchor at PHASE2C_12 Q3 LOCKED 198 vs 197 actual divergence as evidence basis.

- [ ] **Step 6.3: Specify METHODOLOGY_NOTES § slot + tier disposition (provisional)**
- [ ] **Step 6.4: Self-review + §9.0c instance log update**

---

## Task 7: §2.5 Item 5 — Reviewer over-interpretation prevention

**Files:**
- Modify: `docs/phase2c/PHASE2C_13_PLAN.md` (append §2.5)

- [ ] **Step 7.1: Pull Item 5 verbatim from PHASE2C_12 closeout §10.2**

Read closeout §10.2 Item 5. Verbatim quote.

- [ ] **Step 7.2: Author Item 5 codification mechanism**

Specify "register-class explicit declaration in each Step deliverable" mechanism: every Step deliverable opens with explicit register-class declaration block (e.g., "This deliverable operates at <register-class> register; mitigation strategies for <register-class> instances apply"). Anchor at §9.0c instance #8 (advisor pre-fire prediction wrong) from PHASE2C_12 as concrete example.

- [ ] **Step 7.3: Specify METHODOLOGY_NOTES § slot + tier disposition (provisional)**
- [ ] **Step 7.4: Self-review + §9.0c instance log update**

---

## Task 8: §2.6 Item 6 — §9.0c instance density mechanism + register-class taxonomy sub-rule

**Files:**
- Modify: `docs/phase2c/PHASE2C_13_PLAN.md` (append §2.6)

- [ ] **Step 8.1: Pull Item 6 verbatim from PHASE2C_12 closeout §10.2**

Read closeout §10.2 Item 6. Verbatim quote. Note that Item 6 contains the §9.0c register-class taxonomy 3-class sub-rule that is operationalized in detail at §3.

- [ ] **Step 8.2: Author Item 6 codification mechanism**

Specify "continuous improvement vs batch improvement register choice" mechanism. This is the parent of Item 7 (which applies the continuous-improvement choice recursively to PHASE2C_13 itself). Cross-reference §3 (§9.0c sub-rule operationalization) and §2.7 (Item 7 real-time mitigation operationalization).

- [ ] **Step 8.3: Specify METHODOLOGY_NOTES § slot + tier disposition (provisional)**
- [ ] **Step 8.4: Self-review + §9.0c instance log update**

---

## Task 9: §2.7 Item 7 — Real-time §9.0c instance handling (CRITICAL: boundary clause preservation)

**Files:**
- Modify: `docs/phase2c/PHASE2C_13_PLAN.md` (append §2.7)

**This is the MOST critical task in the cycle. Item 7 boundary clause is ChatGPT-load-bearing binding. Errors here propagate to cross-cycle §9.0c measurement integrity.**

- [ ] **Step 9.1: Pull Item 7 + boundary clause VERBATIM from scoping decision §6.2**

Read scoping decision §6.2 Item 7 entry (lines 272-278 per scoping decision file). Quote VERBATIM:

> **Item 7** — Real-time §9.0c instance handling at PHASE2C_13 cycle internal. Operationalization of Item 6's continuous-vs-batch register choice applied recursively to PHASE2C_13 itself (anti-meta-pattern discipline; mitigate as surfaced, not carry-forward to next consolidation cycle).
>
> **Boundary clause (binding):** Item 7 changes mitigation TIMING only, NOT taxonomy or counting logic. §9.0c register-class taxonomy (sub-spec drafting / authorization / reviewer) stays invariant across cycles; counting logic stays invariant; only WHEN mitigation is applied changes (real-time vs carry-forward-batch). Cross-cycle comparability preserved.

- [ ] **Step 9.2: Author operationalization mechanism (per scoping decision §6.2 advisor lean)**

Specify the (a)+(c) combined mechanism:
- **(a) Lightweight tracking** — sub-spec maintains running §9.0c instance log within cycle internal; each instance surface triggers immediate mitigation note.
- **(c) Boundary-fire mitigation review** — §9.0c instances reviewed at cycle boundary fires (scoping SEAL / sub-spec SEAL / closeout SEAL).
- **(b) Recursive mini-codification REJECTED** — infinite recursion risk; explicitly excluded.

- [ ] **Step 9.3: Author Item 7 scope question (open for sub-spec to codify)**

Per advisor pre-drafting Obs 4 + PHASE2C_13 entry §19 instance #1 case study: does Item 7 scope = §9.0c only (strict scoping decision wording) OR include §19 (anti-meta-pattern spirit)? Author this as explicit sub-question with: (i) options enumeration; (ii) advisor lean = include §19; (iii) Charlie register adjudication required at sub-spec SEAL boundary OR explicit deferral to implementation arc § codification.

- [ ] **Step 9.4: Author boundary clause preservation verification (binding at sub-spec SEAL)**

Specify pre-SEAL verification check: V#-chain anchor verification fires "Item 7 operationalization mechanism preserves boundary clause invariant" check. Specifically: verify operationalization does NOT modify §9.0c taxonomy (3 register classes preserved) and does NOT modify counting logic (cumulative count register preserved).

- [ ] **Step 9.5: Specify METHODOLOGY_NOTES § slot + tier disposition (provisional)**

Note: Item 7 is advisor-added (NOT in PHASE2C_12 closeout §10.2 verbatim 1-6). Tier disposition needs explicit advisor-attribution + cross-cycle accumulation pending. Likely Weak tier observation-only initially, Medium-tier promotion conditional on PHASE2C_14+ instance accumulation.

- [ ] **Step 9.6: Self-review §2.7 + boundary clause preservation check**

Read §2.7 verbatim. Verify NO drift from boundary clause. Verify operationalization mechanism strictly within (a)+(c) combined per scoping decision.

- [ ] **Step 9.7: §9.0c instance log update**

If §9.0c instance surfaces at this critical authoring step, log + mitigate per §2.7 own mechanism (recursive operationalization at sub-spec drafting register).

---

## Task 10: §3 §9.0c register-class taxonomy 3-class sub-rule operationalization

**Files:**
- Modify: `docs/phase2c/PHASE2C_13_PLAN.md` (append §3)

- [ ] **Step 10.1: Author 3-class enumeration with PHASE2C_12 instance examples**

Per scoping decision §6.3:
- **Sub-spec drafting register** — instances surfacing at sub-spec authoring (PHASE2C_12 examples: instances #1, #2, #6)
- **Authorization register** — instances surfacing at Charlie register authorization boundary (PHASE2C_12 examples: instance #3)
- **Reviewer register** — instances surfacing at reviewer pass cycle (PHASE2C_12 examples: instances #4, #5, #7, #8)

- [ ] **Step 10.2: Author register-class-distinct mitigation strategies**

For each register-class, specify mitigation strategy. Bulk-mitigation (single "process failure" bucket) explicitly REJECTED per scoping decision §6.3.

- [ ] **Step 10.3: Author cross-cycle comparability requirement**

Per Item 7 boundary clause: 3-class taxonomy stays invariant across PHASE2C cycles. Specify how cross-cycle comparability is preserved (e.g., consistent register-class labels; no taxonomy mutations).

- [ ] **Step 10.4: Self-review against scoping decision §6.3**

Verbatim cross-check.

- [ ] **Step 10.5: §9.0c instance log update**

---

## Task 11: §4.1 Carry-forward A — Cycle-complexity scaling diagnosis

**Files:**
- Modify: `docs/phase2c/PHASE2C_13_PLAN.md` (append §4.1)

- [ ] **Step 11.1: Author (a) Quantitative metric tracking specification**

Per scoping decision §6.4: historical analysis covering auth boundaries / commits / §19 instances / §9.0c instances per cycle across PHASE2C_8 through PHASE2C_12. Specific metric set:
- Auth boundaries per cycle (PHASE2C_8 = ?, PHASE2C_9 = ?, ..., PHASE2C_12 = 16)
- Commit count per cycle
- §19 instance count per cycle (PHASE2C_9 = 3, PHASE2C_10 scoping = 2, PHASE2C_10 plan = 1, PHASE2C_11 = 10, PHASE2C_12 = 10)
- §9.0c instance count per cycle (PHASE2C_12 = 8; other cycles TBD via backfill from closeout deliverables)

Specify whether backfill is in-scope for PHASE2C_13 sub-spec or carry-forward to implementation arc.

- [ ] **Step 11.2: Author (c) Forward observation framing for PHASE2C_14+**

Specify monitoring mechanism: "what to monitor in PHASE2C_14+" anchor. E.g., per-cycle metric tracking continues; threshold for "scaling concern" surface; alert mechanism. Do NOT pre-name PHASE2C_14 scope (anti-pre-naming preserved).

- [ ] **Step 11.3: (b) Qualitative root cause analysis DEFER explicit statement**

Per scoping decision §6.4: defer (b) until (a) data observed. State this explicitly in §4.1; provide forward-pointer to implementation arc Step or PHASE2C_14+ register.

- [ ] **Step 11.4: Cross-reference §6.9 methodology candidate**

Per scoping decision §6.9: scoping cycle iteration-count register-class taxonomy is sub-component of Carry-forward A operationalization. Cross-reference and integrate as §4.1 sub-component.

- [ ] **Step 11.5: Self-review + §9.0c instance log update**

---

## Task 12: §4.2 Carry-forward B — Framework architectural refactor evaluation (analysis register only)

**Files:**
- Modify: `docs/phase2c/PHASE2C_13_PLAN.md` (append §4.2)

- [ ] **Step 12.1: Author register-class clarification (binding) explicit statement**

Per scoping decision §6.5: Carry-forward B = framework architectural refactor **evaluation only** (analysis register; NOT implementation). Implementation defers to PHASE2C_14 or later cycle if evaluation indicates need.

- [ ] **Step 12.2: Author evidence basis from PHASE2C_12**

Per scoping decision §6.5 evidence basis: 7 commits to `backtest/evaluate_dsr.py` at PHASE2C_12 cycle (`8887651`, `2a5c63a`, `605dfc6`, `995fdb2`, `3e1ee89`, `08e1488` + intermediate); cycle-specific framework patches at lines 92/124/129/153 (`PHASE2C_12_N_RAW`, `PHASE2C_12_N_ELIGIBLE_OBSERVED`, `ALLOWED_DUAL_GATE_PAIRS`, `_resolve_n_eff_set()`).

- [ ] **Step 12.3: Author evaluation methodology specification**

Specify HOW evaluation will be performed at PHASE2C_13 implementation arc (or carry-forward to PHASE2C_14):
- Sustainability question framing (cycle-specific hardcoded constants vs alternative architectural patterns)
- Alternative architectural patterns considered without false-binary framing (config injection, cycle-state-machine, abstract base class for cycle parameters, etc.)
- Evaluation criteria for "needed refactor"

- [ ] **Step 12.4: Anti-implementation guardrail**

Specify explicit guardrail: implementation arc § for Carry-forward B authors evaluation outcome ONLY (e.g., "evaluation indicates refactor needed; deferred to PHASE2C_14 or later" OR "evaluation indicates current pattern sustainable through PHASE2C_15"); does NOT modify `backtest/evaluate_dsr.py` or other framework code.

- [ ] **Step 12.5: Self-review + §9.0c instance log update**

---

## Task 13: §4.3 Carry-forward C — Strong-tier promotion candidates + Strong-tier bar codification

**Files:**
- Modify: `docs/phase2c/PHASE2C_13_PLAN.md` (append §4.3)

- [ ] **Step 13.1: Author (C-1) Strong-tier promotion candidates enumeration**

Per scoping decision §6.6 (C-1):
- §19 cross-cycle = 20 instances (enumeration with cycle-by-cycle breakdown verified at scoping decision)
- §9.0c cross-cycle ≥ 8 instances (PHASE2C_12 alone)
- M7 register-class-compromise = 2 instances cross-cycle
- Q10/M6-F2 healthy reasoned-adjudication cycle pattern = 2 PHASE2C_12 instances + cross-cycle accumulation

For each candidate, document current tier disposition (likely Weak/Medium per METHODOLOGY_NOTES §13-§20 status) + Strong-tier promotion evaluation rationale.

- [ ] **Step 13.2: Author (C-2) Strong-tier bar codification (sub-deliverable)**

This is a substantive sub-deliverable (~50-100 lines). Per scoping decision §6.6 (C-2) advisor Observation 4:

Specify Strong-tier bar criteria at register-precision:
- **Minimum cross-cycle instance count threshold** — e.g., ≥N instances across ≥M cycles. Specific N + M values authored (advisor lean: N=10, M=3; sub-spec adjudicates).
- **Mitigation-strategy-specifiable necessary condition** — Strong-tier promotion requires concrete operating rule articulation, not observation-only framing.
- **Cross-cycle register-class consistency requirement** — Strong-tier candidates exhibit consistent register-class behavior across cycles.
- **Exit criteria from Weak/Medium tier register** — explicit criteria for promoting Weak → Medium → Strong.

- [ ] **Step 13.3: Tier framework refinement framing (NOT new framework creation)**

CRITICAL: per scoping decision §6.6 + V#10 verification: Carry-forward C (C-2) is REFINEMENT of EXISTING METHODOLOGY_NOTES §13-§20 tier framework, NOT new framework creation. Reproduce V#10 verification anchors:
- Medium tier at §18 line 2349
- Weak tier at §19 line 2481 (with Medium-tier promotion available at line 2515)
- Strong tier at §20 line 2551 (binding operating rule)

State explicitly: "Strong-tier bar codification at PHASE2C_13 implementation arc appends to existing §20 OR creates new sub-section under §20 register; does NOT replace existing tier framework."

- [ ] **Step 13.4: Re-check §2.1-§2.7 provisional tier dispositions against codified bar**

After Strong-tier bar codified at §4.3, REVISIT §2.1-§2.7 Items 1-7 provisional tier dispositions and confirm/adjust per the codified bar. Document any adjustments.

- [ ] **Step 13.5: Strong-tier promotion explicit sub-spec scope guardrail**

Per scoping decision §1.4 + Carry-forward C scope binding: PHASE2C_13 sub-spec defines Strong-tier promotion CRITERIA only; does NOT promote any candidate to Strong-tier inside the sub-spec. Promotions happen at implementation arc § seal or later cycle.

- [ ] **Step 13.6: Self-review + §9.0c instance log update**

---

## Task 14: §5 Implementation arc Steps 1-N specification

**Files:**
- Modify: `docs/phase2c/PHASE2C_13_PLAN.md` (append §5)

- [ ] **Step 14.1: Map Items 1-7 + sub-rule + carry-forwards to METHODOLOGY_NOTES § slots**

Per scoping decision §5.4 + §6.7 + PHASE2C_10 precedent. For each Item/sub-rule/carry-forward, specify candidate METHODOLOGY_NOTES § number for append (e.g., new §21 for Item 1; §22 for Item 2; ...). Some items may fold into existing §§ (e.g., Item 6 folds into §16 ### Failure-mode signal as PHASE2C_10 precedent did with §3.5/§3.6).

**Fold-in vs new-§ decision criteria (Charlie auth Q-S30 APPROVED; AND-conjoined 4-criteria block):**

A candidate Item / sub-rule / carry-forward is fold-in eligible iff ALL FOUR criteria below hold (AND-conjunction; strict reading). Otherwise: new-§ register.

- **(a) Topical match to existing § scope** — candidate's principle / domain aligns with existing § parent principle (e.g., PHASE2C_10 §3.5 pre-fire audit pattern aligned topically with §16 anchor-prose-access discipline as failure-mode signal sub-class)
- **(b) Sub-§ depth appropriate (NOT diluting parent § principle)** — candidate codifies as natural sub-§ within parent § structure (typically Failure-mode signal slot or short watch-for paragraph); does NOT require its own 4-subsection (Principle/Trigger/Application/Failure-mode signal) full structure
- **(c) Cross-cycle accumulation insufficient for new-§ register** — candidate has limited cross-cycle instance accumulation (typically Weak tier observation-only, 1-2 cycle instances); a new-§ at full 4-subsection structure would be over-codification at the candidate's evidence basis register
- **(d) Item 7 boundary clause compliance — fold-in MUST NOT collide cross-cycle invariant content with cycle-internal state** — fold-in candidate at METHODOLOGY_NOTES § slot must NOT mix cross-cycle codification scope (e.g., 3-class taxonomy invariant content) with cycle-internal operational state (e.g., per-cycle running log). This mirrors the §A1/§A2 vs §3 placement decision at sub-spec deliverable register: fold-in candidates inherit cross-cycle codification scope from parent §; cycle-internal state is register-class-distinct

**Worked example (PHASE2C_10 §3.5/§3.6 fold-in to §16 ### Failure-mode signal):**
- (a) Topical match: §3.5 pre-fire audit + §3.6 self-first-then-reviewer both align with §16 anchor-prose-access discipline as failure-mode signal sub-class ✓
- (b) Sub-§ depth: codified as short watch-for paragraphs, NOT full 4-subsection ✓
- (c) Cross-cycle accumulation: each had 1 PHASE2C-cycle instance at codification time; insufficient for new-§ ✓
- (d) Boundary compliance: §16 host slot citing §11/§14 as parent disciplines via cross-reference register; no cross-cycle vs cycle-internal collision ✓
- All 4 criteria hold AND-conjoined → fold-in (NOT new-§) per PHASE2C_10 precedent

Total new §§ + fold-in count: estimated 7-10 new §§ + 0-3 fold-ins (7 Items + sub-rule potentially fold-in + 3 carry-forwards potentially fold-in or new §). Final mapping with per-candidate criteria check authored at this Task.

- [ ] **Step 14.2: Author per-§ seal pattern (from PHASE2C_10 precedent)**

Per PHASE2C_10 precedent at §16/§17/§18/§19/§20 + §3.5/§3.6 fold-in, each new METHODOLOGY_NOTES § ships with:
- Working draft authoring (temp file or in-place per cycle preference)
- Reviewer pass cycle (advisor + ChatGPT structural; Codex skip per §5.3)
- § seal commit (per §0.4 single-atomic-commit discipline if temp file)
- CLAUDE.md Phase Marker advance per [feedback_claude_md_freshness.md](../../../.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_claude_md_freshness.md)

- [ ] **Step 14.3: Specify implementation arc Step count + sequencing**

Final Step count: 1 Step per new METHODOLOGY_NOTES § + closeout deliverable Step. Sequencing: Items 1-7 codification Steps 1-7 OR consolidated Steps if topical fit; Carry-forwards A/B/C Steps 8-10 (or fold-in); closeout Step N.

Anti-pre-naming preserved: Step ordering authored at sub-spec; specific commit count per Step authored at implementation arc Step entry register.

- [ ] **Step 14.4: Self-review + §9.0c instance log update**

---

## Task 15: §6 Closeout deliverable scope specification

**Files:**
- Modify: `docs/phase2c/PHASE2C_13_PLAN.md` (append §6)

- [ ] **Step 15.1: Author closeout deliverable filename + scope**

Per scoping decision §6.8 + PHASE2C_10/11/12 precedent: closeout deliverable at `docs/closeout/PHASE2C_13_RESULTS.md` (or equivalent). Scope: §1-§N narrative covering Items 1-7 + sub-rule + 3 carry-forwards completion + §8-§N PHASE2C_14 entry recommendation forward-pointer + anchor commits + tag at PHASE2C_13 SEAL bundle.

- [ ] **Step 15.2: Author tag naming convention**

Per PHASE2C_10/11/12 precedent: annotated tag at deliverable seal commit per Path A.2 register-event boundary discipline. Candidate tag name: `phase2c-13-methodology-consolidation-v1` (matching PHASE2C_10 `phase2c-10-methodology-consolidation-v1` precedent for methodology consolidation arcs).

- [ ] **Step 15.3: Author successor scoping cycle forward-pointer**

Per scoping decision §1.4 constraint 8: PHASE2C_14 entry scoping cycle is separate at fresh session post-PHASE2C_13 SEAL. Closeout MD §-N forward-pointer to PHASE2C_14 entry without pre-naming PHASE2C_14 scope (anti-pre-naming).

- [ ] **Step 15.4: Self-review + §9.0c instance log update**

---

## Task 16: §7 Verification chain V#1-V#N

**Files:**
- Modify: `docs/phase2c/PHASE2C_13_PLAN.md` (append §7)

- [ ] **Step 16.1: Author V#1-V#N enumeration**

Verification chain anchors for sub-spec SEAL pre-fire (per §17 sub-rule 4 recursive operating rule):
- **V#1** — HEAD commit at sub-spec authoring (`git rev-parse HEAD`)
- **V#2** — Tag `phase2c-12-breadth-expansion-v1` at remote (verified pushed real-time at Q-S25 (A); empirically confirmed at this sub-spec drafting cycle entry)
- **V#3** — Scoping decision §6 Items 1-7 binding scope verbatim reproduced at §2.1-§2.7
- **V#4** — Scoping decision §6.3 §9.0c register-class taxonomy 3-class sub-rule verbatim reproduced at §3
- **V#5** — Scoping decision §6.4-§6.6 Carry-forwards A/B/C verbatim reproduced at §4.1-§4.3
- **V#6** — Item 7 boundary clause preservation verified (TIMING-only mutation; taxonomy + counting logic invariant)
- **V#7** — Carry-forward B register-class clarification preserved (evaluation only; NOT implementation)
- **V#8** — Carry-forward C tier framework refinement framing preserved (NOT new framework creation; V#10 anchors reproduced)
- **V#9** — METHODOLOGY_NOTES.md §13-§20 tier framework existence empirically re-verified (line numbers may have drifted from V#10 anchor; re-verify with grep)
- **V#10** — Sub-spec section count + cumulative line count within budget (10 §; ~600-900 lines; ±20% tolerance)
- **V#11** — §9.0c instance log integrated into sub-spec deliverable §-cumulative-count register
- **V#12** — §19 instance log integrated; PHASE2C_13 entry §19 instance #1 (tag-push, closed real-time) recorded

Add additional V# anchors as authoring surfaces them.

- [ ] **Step 16.2: Author V#-fire-time anchor for sub-spec SEAL**

Specify V#-chain fires at sub-spec SEAL pre-fire (Task 21 Step 21.1). All V# anchors must be CLEAN before Task 22 Charlie SEAL auth fire.

- [ ] **Step 16.3: Self-review + §9.0c instance log update**

---

## Task 17: §8 Reviewer pass cycle disposition

**Files:**
- Modify: `docs/phase2c/PHASE2C_13_PLAN.md` (append §8)

- [ ] **Step 17.1: Author triple-reviewer disposition**

Per scoping decision §7.2 + handoff §4 step 4:
- **ChatGPT first-pass** — structural overlay
- **Claude advisor full-prose-access pass** — substantive register per METHODOLOGY_NOTES §16 anchor-prose-access discipline
- **Claude Code register-precision verification** — post-reviewer-pass + pre-Charlie-SEAL (full-file prose-access pass per §17 sub-rule 4)
- **Codex skip** at sub-spec drafting cycle register per §5.3 + [feedback_codex_review_scope.md](../../../.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_codex_review_scope.md)

- [ ] **Step 17.2: Author per-fix adjudication discipline (no bulk-accept)**

Per [feedback_reviewer_suggestion_adjudication.md](../../../.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_reviewer_suggestion_adjudication.md): per-fix verification before convergence. Document at §8 with explicit adjudication discipline + Charlie register involvement at substantive divergence boundaries.

- [ ] **Step 17.3: Catch density expectation**

Per advisor pre-drafting Obs 1 (Q-S26 advisor evaluation): scoping decision had ~1.66% catch density (8 patches / 421 lines); sub-spec is substantively larger (600-900 lines); predicted catch density 1.5-2.5% → 9-22 patches at reviewer pass cycle. Plan reviewer pass cycle iteration count accordingly.

- [ ] **Step 17.4: Self-review + §9.0c instance log update**

---

## Task 18: §9 Cross-references

**Files:**
- Modify: `docs/phase2c/PHASE2C_13_PLAN.md` (append §9)

- [ ] **Step 18.1: Enumerate cross-references**

Per scoping decision §8 pattern:
- §9.1 PHASE2C_12 cross-references (closeout, scoping, sub-spec)
- §9.2 PHASE2C_10 + PHASE2C_11 cross-references (sub-spec drafting cycle precedents)
- §9.3 METHODOLOGY_NOTES cross-references (§13-§20 + new §§ to be appended at implementation arc)
- §9.4 CLAUDE.md cross-references (Phase Marker)
- §9.5 Feedback memory cross-references

- [ ] **Step 18.2: Verify all cross-reference paths exist + render**

Run: `ls -la <each-cited-path>` for each cross-reference. If path drift, fix.

- [ ] **Step 18.3: Self-review + §9.0c instance log update**

---

## Task 19: Full-draft self-review (Claude Code register-precision pass)

**Files:**
- Read: `docs/phase2c/PHASE2C_13_PLAN.md` (full file)

**M7 register-class-compromise scope declaration (Charlie auth Q-S30 APPROVED):** This task is a same-agent (Claude Code) fresh-register full-file pass = M7 register-class-compromise instance per scoping decision §6.6 (C-1) cumulative count register. M7 register-class-compromise discipline structurally limits substantive register-class catch capacity; explicit catch scope cap below prevents implicit Task 19 over-claim that would weaken Tasks 20-21 reviewer pass cycle vigilance.

**Catch scope cap:**
- **IN-SCOPE for Task 19:** trivial register-precision drifts (line numbers / cross-references / verbatim-quote drift from scoping decision); §A1/§A2 log entry schema integrity; cumulative line/§ count vs budget; explicit forbidden-anchor scan (anti-pre-naming PHASE2C_14/15 scope leakage)
- **OUT-OF-SCOPE for Task 19** (these fire at reviewer pass cycle Tasks 20-21 register, NOT here): substantive register-class issues; Item 7 boundary clause preservation defects (catch register-class = reviewer); Strong-tier bar coherence; Carry-forward B evaluation-only register preservation defects; cross-§ structural inconsistency at substantive register

If Task 19 surfaces an OUT-OF-SCOPE candidate defect, log to §A1 reviewer register (advisor pass would have caught at correct register-class) and DEFER to Task 20-21 for substantive resolution. Do NOT silently fix substantive register-class issues at Task 19 register — that collapses register-class precision and weakens reviewer pass cycle catch-class accuracy at cross-cycle methodology measurement register.

- [ ] **Step 19.1: Full-file prose-access pass per §17 sub-rule 4**

Read entire sub-spec working draft start-to-end. Verify:
- Scoping decision §6 binding scope reproduced at register-precision (Items 1-7 verbatim where required; sub-rule + carry-forwards faithfully captured)
- Item 7 boundary clause preserved at §2.7 + §10 (taxonomy + counting logic invariant)
- Carry-forward B preserved at evaluation-register only
- Carry-forward C preserved at tier framework refinement framing
- Anti-pre-naming preserved (no PHASE2C_14/15 scope pre-commitment)
- §9.0c instance log integrated; §19 instance log integrated
- Cross-references valid

- [ ] **Step 19.2: §19 instance scan**

Search for any spec-vs-empirical-reality drifts within sub-spec content (e.g., line numbers cited but actual file differs, anchors named but actual artifact differs). Surface as §19 instance + mitigate.

- [ ] **Step 19.3: §9.0c instance log final review**

Read running §9.0c instance log; verify all instances have mitigation notes per Item 7 (a)+(c) operationalization. Total count fed into V#11.

- [ ] **Step 19.4: Patch any defects found at self-review**

Apply surgical Edit patches. Re-read patched sections to verify clean.

- [ ] **Step 19.5: Checkpoint — total line count + § count**

Run: `wc -l docs/phase2c/PHASE2C_13_PLAN.md && grep -c '^##' docs/phase2c/PHASE2C_13_PLAN.md`
Expected: ~600-900 lines; 10-15 §+sub-§ headings.

---

## Task 20: ChatGPT first-pass + per-fix adjudication

**Files:**
- Read (input to ChatGPT): `docs/phase2c/PHASE2C_13_PLAN.md`
- Modify (post-adjudication patches): `docs/phase2c/PHASE2C_13_PLAN.md`

**Note: this task is fired in CHARLIE'S WORKFLOW, not Claude Code's. Charlie copies sub-spec content to ChatGPT and surfaces ChatGPT findings back to Claude Code for adjudication. Claude Code does not directly invoke ChatGPT.**

- [ ] **Step 20.1: Charlie surfaces ChatGPT first-pass findings to Claude Code**

Charlie pastes ChatGPT structural-overlay output into chat. Claude Code receives finding list.

- [ ] **Step 20.2: Per-finding adjudication (ALL findings, no bulk-accept)**

For each ChatGPT finding:
- Read finding rationale verbatim
- Verify against actual sub-spec text
- Reason: APPROVE-as-stated / APPROVE-with-refinement / REJECT-with-rationale / DEFER-to-Charlie
- Document adjudication decision in chat
- If APPROVE: apply patch with Edit tool
- If REJECT: document rationale for Charlie register
- If DEFER: surface to Charlie for register decision

- [ ] **Step 20.3: Re-read patched sections post-patch**

After patch application, re-read patched sections to verify defect closure.

- [ ] **Step 20.4: §9.0c instance log update**

Reviewer-register §9.0c instances logged + mitigated.

---

## Task 21: Claude advisor full-prose-access pass + per-fix adjudication + V#-chain pre-fire empirical verification

**Files:**
- Read (input to advisor): `docs/phase2c/PHASE2C_13_PLAN.md`
- Modify (post-adjudication patches): `docs/phase2c/PHASE2C_13_PLAN.md`

- [ ] **Step 21.1: Charlie surfaces Claude advisor full-prose-access findings to Claude Code**

Charlie pastes Claude advisor (separate session / instance) substantive prose-access findings into chat.

- [ ] **Step 21.2: Per-finding adjudication (ALL findings, no bulk-accept)**

Same pattern as Task 20.2. Advisor findings often catch register-precision defects that ChatGPT structural overlay misses (per PHASE2C_12 cycle empirical pattern).

- [ ] **Step 21.3: Re-read patched sections post-patch**

- [ ] **Step 21.4: §9.0c instance log update**

- [ ] **Step 21.5: Pre-fire V#-chain fire (per §7 V#1-V#N)**

Run V#-chain anchor verification:
- V#1 HEAD: `git rev-parse HEAD`
- V#2 Tag: `git ls-remote --tags origin phase2c-12-breadth-expansion-v1`
- V#3-V#5: grep verbatim reproductions
- V#6: Item 7 boundary clause preservation grep
- V#7: Carry-forward B evaluation-register preservation grep
- V#8: Carry-forward C tier framework refinement framing grep
- V#9: METHODOLOGY_NOTES.md §13-§20 line number re-verify (`grep -n "^## §" docs/discipline/METHODOLOGY_NOTES.md`)
- V#10: line + § count
- V#11: §9.0c log integration grep
- V#12: §19 log integration grep

ALL V# CLEAN before Task 22.

- [ ] **Step 21.6: Final full-file prose-access pass per §17 sub-rule 4**

Re-read entire sub-spec start-to-end after all patches. Verify no regressions from patch application; verify boundary clause + register-class clarifications STILL preserved.

- [ ] **Step 21.7: Notification fire**

PushNotification + Discord webhook on full draft + V#-chain CLEAN per [feedback_long_task_pings.md](../../../.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_long_task_pings.md).

---

## Task 22: SEAL bundle (Charlie auth required)

**Files:**
- Modify: `CLAUDE.md` (Phase Marker advance)
- Commit: `docs/phase2c/PHASE2C_13_PLAN.md` + `CLAUDE.md`

- [ ] **Step 22.1: Surface Charlie SEAL authorization request**

Surface to Charlie register:
> Q-S27 — Authorize PHASE2C_13 sub-spec drafting cycle SEAL bundle?
> - SEAL commit 1: `docs/phase2c/PHASE2C_13_PLAN.md` (final SEALed working draft)
> - SEAL commit 2: `CLAUDE.md` Phase Marker advance to PHASE2C_13 sub-spec drafting cycle SEALED
> - NO tag at sub-spec drafting cycle SEAL per PHASE2C_10/11/12 sub-spec drafting cycle SEAL precedent (tags reserved for arc-level closeout SEAL)
> - Push: bundled commits per (P1) bundled push reviewer convergence

WAIT for explicit Charlie register message. NO operational fire until message received.

- [ ] **Step 22.2: On Charlie auth — apply final Status update**

Edit sub-spec §0 Status line: `Status: WORKING DRAFT` → `Status: SEALED — Charlie SEAL authorization at convergence boundary message; reviewer pass clean post-adjudication; full-file prose-access pass per §17 sub-rule 4 recursive operating rule.`

- [ ] **Step 22.3: SEAL commit 1 — sub-spec MD**

```bash
git add docs/phase2c/PHASE2C_13_PLAN.md
git commit -m "$(cat <<'EOF'
docs(phase2c-13): sub-spec drafting cycle SEAL — methodology consolidation cycle

Items 1-7 codification + §9.0c register-class taxonomy 3-class sub-rule +
Carry-forwards A/B/C operationalization (A quantitative+forward; B evaluation-only;
C Strong-tier candidates + bar codification sub-deliverable).

Triple-reviewer convergence (ChatGPT structural + advisor full-prose + Claude Code
register-precision); Codex skip per scoping decision §5.3.

Charlie SEAL authorization at convergence boundary message.
EOF
)"
```

- [ ] **Step 22.4a: Pre-Phase-Marker anchor enumeration (Charlie auth Q-S30 APPROVED)**

Before authoring Phase Marker prose at Step 22.4: enumerate canonical anchors to be cited at the new Phase Marker entry. Output as a bullet list checkpoint; Step 22.4 prose-authors against the enumerated list, NOT free-author. Defensive discipline against register-precision drift at SEAL bundle stress-time.

Required canonical anchor enumeration (output as checkpoint before writing Phase Marker prose):

1. **V#-chain anchors** (V#1-V#N from sub-spec §7) — verified CLEAN at Task 21 Step 21.5; reproduce verbatim
2. **Cumulative §19 instance count** at PHASE2C_13 sub-spec drafting cycle close — pull from sub-spec §A2 final state (count per register-class + closure status breakdown)
3. **Cumulative §9.0c instance count** at PHASE2C_13 sub-spec drafting cycle close — pull from sub-spec §A1 final state (count per register-class + closure status breakdown)
4. **Scoping decision §6 binding-scope anchors** (Items 1-7 + §9.0c sub-rule + Carry-forwards A/B/C) — cite scoping decision §6 verbatim
5. **Sub-spec SEAL commit anchor** — output of Step 22.3 (`git rev-parse HEAD` after sub-spec commit)
6. **Triple-reviewer convergence record** — Tasks 20+21 adjudication summary (ChatGPT findings count, advisor findings count, per-finding adjudication outcomes table)
7. **Implementation arc forward-pointer** (per sub-spec §5 Steps 1-N specification) — explicit Step count + METHODOLOGY_NOTES § slot mapping
8. **Active next action** — implementation arc Step 1 fires at fresh session post-SEAL per pacing discipline

Surface enumerated anchor list to Charlie register as part of Q-S27 pre-fire context. Phase Marker prose at Step 22.4 references this list as authoritative anchor source.

- [ ] **Step 22.4: SEAL commit 2 — CLAUDE.md Phase Marker advance**

Edit `CLAUDE.md` Phase Marker section. Advance current phase entry to `PHASE2C_13 sub-spec drafting cycle SEALED at sub-spec drafting cycle SEAL register`. Add comprehensive Phase Marker entry per PHASE2C_10/11/12 precedent (cycle scope + scoping decision binding + Items 1-7 + sub-rule + carry-forwards + reviewer pass adjudication + V#-chain + cumulative §19/§9.0c counts + carry-forwards to implementation arc + active next action).

```bash
git add CLAUDE.md
git commit -m "docs(phase2c-13): CLAUDE.md Phase Marker advance — PHASE2C_13 sub-spec drafting cycle SEALED at sub-spec drafting cycle SEAL register"
```

- [ ] **Step 22.5: Verify both commits clean before push**

Run: `git log -2 --stat`
Expected: 2 commits visible; sub-spec MD + CLAUDE.md modifications.

- [ ] **Step 22.6: Push SEAL bundle (separate Charlie auth boundary)**

Surface to Charlie register:
> Q-S28 — Authorize SEAL bundle push fire (`git push origin main`)?

WAIT for explicit Charlie register message. NO push until message received.

On Charlie auth:
```bash
git push origin main
```

Verify push success: `git status` shows "up to date with origin/main".

- [ ] **Step 22.7: Notification fire**

PushNotification + Discord webhook on SEAL bundle push CLEAN per [feedback_long_task_pings.md](../../../.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_long_task_pings.md).

- [ ] **Step 22.8: Generate fresh-session handoff for implementation arc Step 1**

Per PHASE2C_10/11/12 precedent: pacing discipline pause confirmed at sub-spec SEAL; implementation arc Step 1 fires at fresh session. Generate `/tmp/PHASE2C_13_IMPL_STEP1_HANDOFF.md` covering:
- Sub-spec SEAL register summary (anchor commits + Charlie auth boundaries)
- Implementation arc Step 1 scope (per sub-spec §5)
- §9.0c + §19 cumulative count carry-forward
- Active next action

---

## Self-Review Checklist (run AFTER plan complete; this section is for the plan author, not the executor)

**1. Spec coverage:** Each scoping decision §6.2-§6.8 binding scope item has at least one task above:
- [x] Items 1-7 codification → Tasks 3-9 (one task per item)
- [x] §9.0c register-class taxonomy 3-class sub-rule → Task 10 (§3)
- [x] Carry-forward A → Task 11 (§4.1)
- [x] Carry-forward B → Task 12 (§4.2)
- [x] Carry-forward C (C-1 + C-2 sub-deliverable) → Task 13 (§4.3)
- [x] Implementation arc Steps 1-N specification → Task 14 (§5)
- [x] Closeout deliverable scope specification → Task 15 (§6)
- [x] Verification chain → Task 16 (§7)
- [x] Reviewer pass cycle disposition → Task 17 (§8)
- [x] Cross-references → Task 18 (§9)
- [x] §0 + §1 scaffolding → Tasks 1-2

**2. Placeholder scan:** No "TBD" / "implement later" / "appropriate handling" / "similar to Task N" in step bodies. Each step has actual content.

**3. Type/path consistency:** Sub-spec filename `docs/phase2c/PHASE2C_13_PLAN.md` consistent across all tasks. METHODOLOGY_NOTES.md path consistent. Cross-references checked at Task 18.

**4. Discipline anchor coverage:** All 10 discipline anchors enumerated in cross-cutting section above; not repeated per-task to avoid bloat.

**5. Charlie auth boundaries explicit:** Q-S27 (SEAL commit auth) + Q-S28 (push auth) at Task 22 — both surfaced as explicit Charlie register messages with WAIT semantics.

**6. Notification fire:** PushNotification + Discord at Task 21.7 (full draft + V#-clean) + Task 22.7 (SEAL bundle push).

---

## Execution Handoff

**Plan complete and saved to** [`docs/superpowers/plans/2026-05-05-phase2c-13-sub-spec-drafting.md`](2026-05-05-phase2c-13-sub-spec-drafting.md).

**Two execution options:**

**1. Subagent-Driven (recommended for typical TDD/code work)** — fresh subagent per task; reviewer between tasks; fast iteration.

**2. Inline Execution (recommended HERE)** — execute tasks in this session using superpowers:executing-plans, batch execution with checkpoints. **Rationale for inline preference:** sub-spec drafting is sequential prose authoring with cumulative anchor dependencies (each § builds on prior §s); Item 7 anti-meta-pattern discipline operates real-time during all tasks (§9.0c log + §19 log accumulate within cycle); Charlie auth boundaries surface naturally inline; subagent dispatch for prose-authoring would lose §9.0c/§19 log continuity and fragment Item 7 real-time discipline.

**Awaiting Charlie register selection: subagent-driven or inline.** Default lean: inline.

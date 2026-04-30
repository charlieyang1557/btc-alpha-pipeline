# PHASE2C_10 Plan — Methodology Consolidation Drafting Framework

**Status: WORKING DRAFT — pre-seal; anchor-prose-access discipline instance #5 fires at dual-reviewer pass before seal.**

**Anchor:** PHASE2C_10 scoping decision sealed at commit `1053c73` ([`docs/phase2c/PHASE2C_10_SCOPING_DECISION.md`](PHASE2C_10_SCOPING_DECISION.md)). This document operationalizes the scoping decision's §5 pre-registered framing decisions for the methodology consolidation arc, executes the Option A tier-precision-per-candidate adjudication (§6.1 Option A flag), and locks the deliverable structure for the Step 2 implementation arc that performs the actual METHODOLOGY_NOTES.md §16+ updates.

---

## §0 Document scope and structure

### §0.1 Scope

This plan covers PHASE2C_10's single implementation step: the METHODOLOGY_NOTES update arc that consolidates PHASE2C_9 + PHASE2C_10 scoping carry-forward methodology candidates into per-principle sections appended at §16+ of [`docs/discipline/METHODOLOGY_NOTES.md`](../discipline/METHODOLOGY_NOTES.md). PHASE2C_10's hard scope per scoping doc §1.4 — no new generation, no new evaluation, no strategy redesign, no DSR / PBO / CPCV implementation, no Phase 3 progression decision, no API spend — fixes the implementation register at documentation discipline only.

The plan locks: filename + document-type framing (§1); section numbering and placement decisions for §16+ append (§2); per-candidate codification text + tier precision per Option A flag adjudication (§3); emergent-vs-folded adjudication for the advisor-register sub-pattern surfaced at PHASE2C_10 scoping cycle (§4); Step 2 fire procedure for the implementation arc (§5); sub-spec verification framework including anchor-prose-access discipline instance #5 disposition (§6); cross-references (§7).

The plan does NOT cover successor scoping cycle direction, candidate cross-cycle accumulation thresholds beyond PHASE2C_10's own register, or any Phase 2D / Phase 3 trajectory decisions. Per anti-pre-naming option (ii), successor scoping fires post-PHASE2C_10 implementation arc seal, not from this plan.

### §0.2 Structure

§1 resolves the filename + document-type framing decision per anti-pre-naming option (ii). §2 locks section numbering and placement decisions, reaffirming the §1-§15 stable + §16+ append convention with explicit per-section number assignments. §3 carries the substantive per-candidate codification text and tier precision adjudication; one sub-section per candidate, plus §3.7 tier-precision summary table. §4 adjudicates the advisor-register sub-pattern that surfaced at scoping cycle as either emergent (separate observation) or folded (instance of candidate (3) spec-vs-empirical-reality). §5 specifies the Step 2 fire procedure including pre-fire prerequisites, sequenced activities, Codex routing, and gating criteria. §6 specifies the sub-spec verification framework. §7 documents cross-references.

### §0.3 Discipline anchors operating at this drafting cycle

Five disciplines operate at this plan's drafting cycle and at the Step 2 implementation arc that follows:

- **Anchor-prose-access discipline** (METHODOLOGY_NOTES §15; PHASE2C_9 §8.4 mandatory entry #4 standing instruction; instance count: 4 cumulative as of scoping cycle seal): operationalized at instance #5 fire at this plan's dual-reviewer pass before seal.
- **Anti-momentum-binding discipline** (PHASE2C_10 scoping §6.1 Option A flag): provisional tier labels at scoping doc §5.2 are inputs to per-candidate evidence review at §3, not constraints. Tier patches per evidence count are explicit and reasoned.
- **Anti-pre-naming discipline** (METHODOLOGY_NOTES §10; PHASE2C_10 scoping §5.3): plan's filename + sub-section structure committed at this plan's seal cycle; successor cycle direction NOT pre-committed.
- **Empirical verification discipline** (METHODOLOGY_NOTES §1; PHASE2C_10 scoping cycle's §1-§7 / §16-single-section catches operationalized the lesson): file-structure citations verified before use; advisor-supplied anchors verified at receiving cycle.
- **Self-first-then-reviewer adjudication discipline** (PHASE2C_10 scoping §6.4 emergent candidate; observation-only register): Claude advisor's own substantive review fires before reviewer-suggestion adjudication, not as substitute.

### §0.4 Process note — working-draft commit / dual-reviewer pass / patch-commit-seal sequencing

This plan's working draft was first committed at `d0222c7` before instance #5 dual-reviewer pass fired. Per Claude advisor + ChatGPT instance #5 substantive adjudication, the working-draft-commit-before-prose-pass pattern is itself a **third instance** of candidate (2) procedural-confirmation defect class (operating during this very session): the working-draft commit fired at procedural register (commit landed; tree clean) while substantive register (dual-reviewer prose-access pass) had not yet fired. Defect ι (§3.7 internal-consistency violation between summary table rows 3/5/6 and §2.2 placement decisions) landed at `d0222c7` precisely because pre-commit substantive prose-access pass had not fired; defect ι operationally validated the procedural-confirmation defect class at instance #3.

**Resolution path (per ChatGPT instance #5 disposition)**: follow-up patch commit (this commit's patch register) rather than amending `d0222c7` history. Audit-trail rationale — local history preservation makes the procedural-confirmation defect class operationally observable at the commit chain, which is itself instructive content for candidate (2) §17 codification at Step 2 implementation arc. Amend would erase the empirical evidence of instance #3.

**Instance count update for candidate (2)**: 3 instances cumulative (PHASE2C_9 Step 5 working-draft commit `e11e806`; PHASE2C_9 Step 6 closeout assembly first commit; PHASE2C_10 plan working-draft commit `d0222c7`). §3.2 evidence count and §17 codification scope at Step 2 implementation arc reflect 3-instance count, not the 2-instance count cited at §3.2 prose pre-instance-#5-pass.

**Discipline correction**: future PHASE2C_10 commits at this plan's seal register fire AFTER dual-reviewer pass clears, not before. Working-draft-commit-before-prose-pass pattern flagged as defect class instance, not legitimized as variant pattern.

---

## §1 Filename and document-type lock (anti-pre-naming option (ii) resolution)

### §1.1 Filename decision

**Filename: `docs/phase2c/PHASE2C_10_PLAN.md`** (this document).

Resolution per anti-pre-naming option (ii) at this plan's draft fire. Two filename candidates were available per PHASE2C_10 scoping §5.3: `PHASE2C_10_PLAN.md` and `PHASE2C_10_SUBSPEC.md`. The selection rationale:

- **Convention precedent**: PHASE2C_6 / PHASE2C_7 / PHASE2C_8 / PHASE2C_9 each used `_PLAN.md` as the canonical implementation-arc spec filename. The pattern is stable across four arcs.
- **Single-step scope collapse**: PHASE2C_10 has one implementation step (the METHODOLOGY_NOTES update arc). The "spec" and "sub-spec" distinction that operated at PHASE2C_9 (parent `PHASE2C_9_PLAN.md` for arc-level spec + `PHASE2C_9_STEP6_SUBSPEC.md` for Step 6 application framing) does not apply at PHASE2C_10. There is no parent spec; this plan IS the spec for the single implementation step.
- **Cross-reference grep stability**: future commits referencing the spec resolve to `PHASE2C_10_PLAN.md` consistent with the four-arc convention; deviation to `_SUBSPEC.md` would introduce inconsistency across `docs/phase2c/PHASE2C_*_PLAN.md` patterns.

The document-type framing distinguishes from PHASE2C_9_STEP6_SUBSPEC.md: this plan is arc-level (covers the entire PHASE2C_10 implementation arc), not step-level (covers a sub-deliverable within a multi-step arc).

### §1.2 Document-type framing

This plan's deliverable register is **arc-level implementation spec**. Authorship register is canonical-spec (load-bearing structural commitments that the Step 2 implementation arc consumes as authoritative). Verification register is dual-reviewer pass (ChatGPT structural + Claude advisor substantive prose-access; both must fire before seal per METHODOLOGY_NOTES §14 bidirectional dual-reviewer register-precision).

Discipline alignment: §10 anti-pre-naming applies to filename and sub-section structure. §15 anchor-list empirical-verification applies to advisor-supplied anchors at this drafting cycle (handoff prompt anchors verified at scoping doc cross-check during Fire 3 pre-drafting reads). §14 bidirectional dual-reviewer register-precision applies at instance #5 dual-reviewer pass before this plan's seal.

---

## §2 Section numbering and placement decisions

### §2.1 Per-principle append convention reaffirmation

Per scoping doc §5.1 + §5.4 ChatGPT guardrail 4: METHODOLOGY_NOTES.md §1-§15 are stable; §16+ append only. Existing sections are NOT modified by PHASE2C_10. The §1-§15 stability constraint is structural — modifications to existing sections would require separate change cycle with its own dual-reviewer pass; PHASE2C_10's hard scope precludes any §1-§15 edits.

The per-principle append convention (rather than arc-grouped single-section pattern) was confirmed at scoping cycle's §16-single-section catch (scoping §6.2 entry 5). Each codified candidate becomes its own §N section following the existing §1-§15 four-subsection structure: ### Principle / ### Trigger context / ### Application checklist / ### Failure-mode signal.

### §2.2 §16+ section-number assignment

Section numbers assigned to each tier-strong-or-medium candidate per Step 2 implementation arc; weak-tier candidates either fold into existing observation registers OR receive brief observation-only entries without dedicated sections, per ChatGPT guardrail 2 ("weak candidates visibly weak").

**Pre-registered section-number assignment** (subject to tier adjudication at §3):

| Candidate | Provisional tier (scoping §5.2) | §3 adjudicated tier | §16+ section assignment |
|---|---|---|---|
| (1) Anchor-prose-access discipline | Strong | Strong (confirmed §3.1) | §16 dedicated section |
| (2) Procedural-confirmation defect class | Strong | Strong (confirmed §3.2) | §17 dedicated section |
| (4) §7 carry-forward density | Medium | Strong (patch §3.4) | §18 dedicated section |
| (3) Spec-vs-empirical-reality finding pattern | Weak | Weak (confirmed §3.3) | brief §19 dedicated section (observation-only + cross-cycle-pending status-register) |
| (5) Pre-fire audit pattern | Weak | Weak (confirmed §3.5) | folded into §16 ### Failure-mode signal (topical adjacency: session-boundary register precision) OR brief §20 |
| (6) Self-first-then-reviewer | Weak | Weak (confirmed §3.6) | folded into §16 ### Failure-mode signal (topical adjacency: reviewer-engagement register) OR brief §20 |

**§1-§15 stable constraint operating**: candidate placements are restricted to §16+ scope per §5.4 ChatGPT guardrail 4. Folding into existing §1 / §6 / §11 / §14 / §15 sections would modify §1-§15 stable range and is out of PHASE2C_10 scope; folding into NEW §16 / §17 / §18 sections being authored at PHASE2C_10 OR brief dedicated §19 / §20 is in scope.

**Section-number ordering rationale**: candidates promoted to dedicated sections (§16, §17, §18) ordered by closest topical adjacency to the existing §13-§15 cluster (parallel-implementation verification / bidirectional dual-reviewer / anchor-list empirical-verification — all PHASE2C_8.1-codified disciplines on closeout-cycle quality). Anchor-prose-access discipline (§16) is the closest topical successor to §15 anchor-list empirical-verification — it extends §15's pre-drafting anchor verification to the section-seal dual-reviewer pass register. Procedural-confirmation defect class (§17) is the closest topical successor to §6 commit messages are not canonical result layers — both concern procedural-fact-vs-substantive-claim register precision. §7 carry-forward density (§18) is the closest topical successor to §11 closeout-assembly checklist as running drafting-cycle pattern — both concern interpretive arc closeout convention.

The section-number assignment is provisional at this plan's seal; Step 2 implementation arc may patch ordering if dual-reviewer pass surfaces topical-adjacency concerns. Section numbers are NOT pre-committed at this plan's draft fire beyond the §16-§17-§18 cluster commitment.

### §2.3 Cross-reference policy

New §16-§18 sections cross-reference existing §1-§15 sections at four loci:

1. **Trigger context cross-reference**: each new section's ### Trigger context names the originating arc (PHASE2C_9 / PHASE2C_8.1 / cumulative cross-arc) and cross-references the closeout document(s) that operationalized the principle. Pattern follows §13-§15 trigger-context style (concrete arc + commit chain).
2. **Conditional-boundary cross-reference**: where a new section's principle interacts with an existing section's scope, the conditional boundary is explicit. Example: §16 anchor-prose-access discipline references §15 anchor-list empirical-verification's pre-drafting register, distinguishing §16's section-seal-register from §15's pre-drafting-register.
3. **Application-checklist cross-reference**: where a checklist item depends on an existing discipline's mechanism, the dependency is named. Example: §16 application checklist item referencing dual-reviewer pass operationally depends on §14 bidirectional dual-reviewer register-precision.
4. **Failure-mode signal cross-reference**: where a failure mode is the inverse of an existing discipline's success mode, the inverse is explicit. Example: §17 procedural-confirmation defect class failure-mode signal references §6 commit messages are not canonical result layers as the orthogonal discipline at the same defect surface.

Existing §1-§15 sections are NOT modified to add back-references to new §16-§18 sections within this PHASE2C_10 arc. Back-reference inclusion is deferred — successor cycle decision per anti-pre-naming option (ii). The asymmetry preserves §1-§15 stability constraint.

---

## §3 Per-candidate codification text and tier precision

This section adjudicates Option A flag (scoping §6.1) per-candidate and produces the codification text framework for Step 2 implementation arc consumption. Each sub-section: candidate framing → evidence count → tier adjudication → codification scope → cross-reference targets.

### §3.1 Candidate (1) — Anchor-prose-access discipline at multi-hundred-line interpretive deliverables

**Candidate framing**: at multi-hundred-line interpretive deliverables (closeout sections, sub-spec drafts, scoping decisions), dual-reviewer pass requires reviewer access to actual prose, not summary or structural overview alone. Reviewer adjudication against summary-substituted-for-prose under-protects substantive register-precision; reviewer adjudication against actual prose surfaces defects that summary-only review misses by construction.

**Evidence count**: 4 instances cumulative as of PHASE2C_10 scoping cycle seal:

1. PHASE2C_9 Step 5 follow-up dual-reviewer round (advisor substantive prose-access pass at §7 evidence-map closeout; surfaced Concerns A residual / C internal-consistency / D "hampered" interpretive register / verified B framing scope + F Path B operationalization clean)
2. PHASE2C_9 Step 6 sub-spec drafting cycle (instance #2 throughout sub-spec drafting; surfaced Concerns G/H/I/J at Round 1 + Flags 1/2/3 at Round 2 + Concerns K/L at Round 3)
3. PHASE2C_9 Step 6 fire dual-reviewer pass (instance #3 at closeout assembly final; advisor substantive prose-access pass surfaced 8 Concerns O-V; 3 patches applied; 5 verified clean on prose access)
4. PHASE2C_10 scoping cycle dual-reviewer pass (instance #4 at scoping doc seal; surfaced §1-§7 / §16-single-section / spec-vs-empirical-reality count increments)

**Tier adjudication**: **Strong** (confirms scoping doc §5.2 provisional tier).

Each instance surfaced real defects via prose access that structural-summary review missed by construction. The discipline's catch rate against summary-substituted-for-prose is non-zero across 4 instances; cumulative across instances reaches strong-tier codification threshold. Per anti-momentum-binding, the strong tier is supported by evidence count (4 instances) + defect catch rate (real catches at every instance) + structural inevitability (summary review cannot surface prose-precision defects by construction).

**Codification scope**: full §16 codification with all four standard subsections.

- ### Principle: at multi-hundred-line interpretive deliverables, dual-reviewer pass requires reviewer access to actual prose rather than summary or structural overview. Summary-only review covers structural-defect axis; substantive register-precision requires prose-access overlay.
- ### Trigger context: PHASE2C_9 Step 5 / Step 6 sub-spec drafting / Step 6 fire (3 instances, March-April 2026); PHASE2C_10 scoping cycle (instance #4, April 2026). Cumulative 4 instances at distinct defect classes (interpretive-register precision; framing-scope verification; closeout-assembly section-author discipline; advisor-register-anchor verification).
- ### Application checklist: (a) for deliverables ≥200 lines OR with interpretive-register content, schedule dual-reviewer pass with prose-access prerequisite; (b) reviewer-supplied summary OR structural overview is necessary input but not sufficient for substantive adjudication; (c) prose-access fire surfaces defects that summary-only review cannot reach; (d) instance count tracking: each fire records the instance number for cross-arc accumulation visibility; (e) discipline operates as standing instruction once codified (no per-cycle re-authorization).
- ### Failure-mode signal: watch for summary-substituted-for-prose at high-load reviewer cycles; watch for "the structural overview is sufficient" framing at multi-hundred-line interpretive deliverables; watch for instance-count tracking absence (instances surface but accumulation register not maintained); watch for prose-access deferred-to-next-cycle when fire register is current cycle's seal.

**Cross-reference targets**: §15 anchor-list empirical-verification (distinguishing register: §15 pre-drafting anchor verification at receiving cycle; §16 section-seal prose-access verification at reviewer register); §14 bidirectional dual-reviewer register-precision (operational dependency: §16 fires the prose-access at the §14 reviewer register).

### §3.2 Candidate (2) — Procedural-confirmation defect class at first-commit-before-prose-access

**Candidate framing**: a procedural-confirmation defect class operates at the first-commit-before-prose-access register. The defect class surfaces when a deliverable's first-commit fire is procedurally complete (commit lands; CI passes; reviewer sees commit notification) but the substantive prose has not yet received reviewer prose-access. Reviewer's procedural-confirmation ("commit landed") may be misread as substantive-confirmation ("prose reviewed clean"); the misread substitutes procedure for substance at the seal register.

**Evidence count**: **3 instances cumulative** (2 PHASE2C_9 + 1 PHASE2C_10):

1. PHASE2C_9 Step 5 §7 working-draft commit (first-commit at `e11e806` before advisor substantive prose-access pass; advisor follow-up surfaced Concerns A residual / C internal-consistency / D "hampered" register requiring patches at `d548ea2`)
2. PHASE2C_9 Step 6 closeout assembly first commit (first-commit fire before advisor substantive prose-access; advisor pass surfaced 8 Concerns O-V at instance #3; 3 patches applied)
3. PHASE2C_10 plan working-draft commit `d0222c7` (first-commit fire before instance #5 dual-reviewer prose-access pass; defect ι — §3.7 internal-consistency violation between summary table rows 3/5/6 and §2.2 placement decisions — landed at `d0222c7`; instance #5 substantive prose-access pass surfaced ι; patches applied at follow-up patch commit per §0.4 disposition). Instance #3 surfaced during this very session; operationally observable at the commit chain `d0222c7` → instance #5 dual-reviewer pass → patch commit (this commit).

**Tier adjudication**: **Strong** (confirms scoping doc §5.2 provisional tier; instance count incremented per §0.4).

Three instances at structurally distinct defect surfaces (PHASE2C_9 Step 5 interpretive-register at §7 evidence map; PHASE2C_9 Step 6 closeout-assembly at §8 + cross-cutting at §1 / §2 / §9; PHASE2C_10 plan summary-table internal-consistency at §3.7). Each instance demonstrated the defect class operationally — procedural-confirmation cleared while substantive defects remained; prose-access fire was the structural complement that surfaced the defects. The discipline's structural payoff: prose-access-before-seal preserves substantive register-precision at deliverables where procedural-confirmation alone under-protects.

**Codification scope**: full §17 codification with all four standard subsections.

- ### Principle: at high-load deliverable registers (closeout sections, sub-spec drafts), procedural-confirmation (commit landed; CI passed; reviewer notified) is necessary but not sufficient for seal authorization. Substantive prose-access by both reviewers is the complement; seal authorization requires both procedural and substantive confirmation.
- ### Trigger context: PHASE2C_9 Step 5 working-draft commit `e11e806` → advisor substantive pass → patches at `d548ea2` (April 2026); PHASE2C_9 Step 6 closeout assembly first commit → advisor instance #3 substantive pass → 3 patches applied (April 2026). Both instances demonstrated the defect class at structurally distinct surfaces.
- ### Application checklist: (a) distinguish procedural-confirmation register (commit landed, CI clean, reviewer notified) from substantive-confirmation register (prose reviewed, defects surfaced and adjudicated, seal authorized); (b) seal authorization requires both registers cleared, not procedural alone; (c) when first-commit fires before substantive prose-access, mark deliverable status "working draft" until substantive pass clears; (d) reviewer notifications of commits are NOT seal authorizations; reviewer authorization at substantive register is the seal authorization.
- ### Failure-mode signal: watch for "commit landed, we're done" at multi-hundred-line interpretive deliverables; watch for reviewer-notification-as-seal-authorization framing; watch for first-commit-cleared-CI substituted-for-substantive-clean; watch for patches-after-first-commit framed as scope creep rather than structural completion of the seal cycle.

**Cross-reference targets**: §6 commit messages are not canonical result layers (orthogonal discipline at related defect surface: §6 covers commit-message-as-result-claim defect; §17 covers commit-as-seal-authorization defect; both concern procedural-substantive register precision at distinct registers); §16 anchor-prose-access discipline (operational dependency: §17's substantive-confirmation fire requires §16's prose-access).

### §3.3 Candidate (3) — Spec-vs-empirical-reality finding pattern

**Candidate framing**: spec / scoping / sub-spec documents may contain references to file structure, content, or state that diverges from empirical reality. The divergence pattern operates at receiving cycles when authors / reviewers cite remembered structure rather than verified structure. Pattern instances accumulate across cycles where the discipline of empirical verification (METHODOLOGY_NOTES §1) is operationalized; per-cycle within-cycle counts plus cumulative cross-cycle counts are the evidence registers.

**Evidence count**: **6 cumulative across 3 cycles** (PHASE2C_9 = 3; PHASE2C_10 scoping = 2; PHASE2C_10 plan drafting = 1):

- PHASE2C_9 within-arc count = 3 (entries 1-3 per scoping doc §6.2 reference to PHASE2C_9 §8.4 mandatory entry #2)
- PHASE2C_10 scoping cycle within-cycle count = 2 (entry 4: §1-§7 stale anchor; entry 5: §16-as-single-section framing)
- PHASE2C_10 plan drafting cycle within-cycle count = 1 (entry 6: CLAUDE.md project-discipline notes section staleness, observed at this plan's Fire 3(ii) METHODOLOGY_NOTES.md prose-reading; CLAUDE.md line 459 lists "§1 empirical verification...§7 asymmetric confidence reporting" as codified principles when actual file state is §1-§15)

Instance #6 included per dual-reviewer pass instance #5 disposition: both reviewers (Claude advisor + ChatGPT) adjudicated entry 6 as same defect class as entries 1-5 (cite remembered structure rather than verified structure; same source defect; same correction path of empirical verification of file state). Defect class boundary is the citation-without-verification register, regardless of which document carries the stale anchor.

**Tier adjudication**: **Weak** with **medium-pending** status note (confirms scoping doc §5.2 provisional tier; potential medium-tier promotion deferred to successor cycle).

Per scoping doc §6.2 cross-cycle accumulation framing: cumulative count of 6 demonstrates pattern operational across 3 distinct cycles, but per-cycle within-cycle counts (3 PHASE2C_9; 2 PHASE2C_10 scoping; 1 PHASE2C_10 plan drafting) are each within the within-cycle-count register that the existing §1 empirical-verification discipline already covers structurally. The pattern is observed; the codification value beyond §1 is incremental.

Operating-rule articulation question (per Claude advisor instance #5 substantive pass): the operating rule this candidate would codify — "verify file structure citations before drafting prose" — is structurally already covered by §15 anchor-list empirical-verification discipline applied to file-structure-anchors register. Candidate (3) may be a sub-class of §15 rather than a distinct discipline; the structural relationship adjudicated at Step 2 implementation arc when §19 authoring fires. Either §19 cross-references §15 as parent discipline (sub-class register), OR §19 stands as standalone observation-only register if structurally distinct.

Promotion to medium tier is structurally available if cross-cycle accumulation reaches a threshold where the cross-cycle pattern itself becomes a load-bearing claim distinct from per-cycle empirical verification AND operating-rule articulation crystallizes beyond §15's existing coverage. At cumulative 6 instances across 3 cycles, the threshold is plausibly reachable but operating-rule articulation incomplete. Per anti-momentum-binding + ChatGPT guardrail 2 ("weak candidates visibly weak"), tier holds at weak; codification register is observation-only with cross-cycle-pending status.

**Codification scope**: brief §19 dedicated section with status-precision register (observation-only + cross-cycle-pending). The folding-into-existing-§1 option is structurally precluded by §5.4 ChatGPT guardrail 4 (§1-§15 stable; only §16+ append) — modifying §1's ### Failure-mode signal would be a §1-§15 edit out of PHASE2C_10 scope. Brief §19 dedicated section is the only in-scope placement.

§19 structure: a short section (~30-50 lines, not the full 4-subsection structure) labeled clearly as observation-only + cross-cycle-pending, distinct from full-codification §1-§18 register. Per ChatGPT guardrail 2 ("weak candidates visibly weak"), the brevity register itself signals weak-tier status; introducing observation-only register at §19 establishes the convention slot for future weak-tier candidates that surface at successor cycles.

Step 2 implementation arc dual-reviewer pass adjudicates the §19 prose register: whether full Principle / Trigger context / Observation summary / Status-precision subsections (lighter than §1-§18's 4-subsection register) align with METHODOLOGY_NOTES convention OR whether a single ## §19 section without subsection breakdown serves the observation-only register better. Selection deferred to Step 2 implementation arc per anti-pre-naming option (ii) at this plan's seal.

**Cross-reference targets**: §1 empirical verification for factual claims (parent discipline at the broader empirical-verification surface; §19 is a per-cycle pattern observation register under §1's general principle, not a §1-modifying entry); §15 anchor-list empirical-verification discipline (covers advisor-register anchor catch mechanism that intersects this candidate's evidence base; cross-reference at §19 trigger context).

### §3.4 Candidate (4) — §7 carry-forward density at interpretive arc closeouts

**Candidate framing**: interpretive arc closeouts (closeouts that synthesize empirical findings into observations for downstream cross-cycle consumption) accumulate observations across implementation steps and surface them in dedicated registers. The convention has emerged across PHASE2C_6 / PHASE2C_7.1 / PHASE2C_8.1 / PHASE2C_9 closeouts at increasing density.

**Evidence count**: 4 PHASE2C interpretive arc closeouts with §7-equivalent carry-forward observation registers; density increasing 2 → 5 → 10+3 → 11:

| Closeout | Section | Register type | Observation count |
|---|---|---|---|
| PHASE2C_6_EVALUATION_GATE_RESULTS.md | §10 Methodology-discipline observation | Methodology lessons synthesis | 2 |
| PHASE2C_7_1_RESULTS.md | §10 Methodology-discipline observations | Numbered observation register | 5 |
| PHASE2C_8_1_RESULTS.md | §10 Tracked-fix register | Q-S4-N register table with codification candidates flagged + §7.2 cross-regime observations | 10 register entries (4 codification candidates) + 3 §7.2 observations |
| PHASE2C_9_RESULTS.md | §7 Mechanism-vs-observation comparison | Cumulative-11 carry-forward register at §7.0.0 inventory table | 11 cumulative |

Empirical findings from this plan's Fire 3(i) verification: §7-style carry-forward observation registers are present at 4 of 4 PHASE2C interpretive arc closeouts; density increasing across cycles; structural pattern stable (dedicated section near closeout end; observation enumeration; codification-candidate flagging where applicable).

**Tier adjudication**: **Medium** (confirms scoping doc §5.2 provisional tier; operating-rule-pending status note attached).

Initial draft of this section adjudicated Strong tier upward from scoping doc §5.2 provisional Medium based on Fire 3(i) 4/4 instance saturation + density growth (2 → 5 → 10+3 → 11). Both reviewers (Claude advisor + ChatGPT) at instance #5 dual-reviewer pass adjudicated Strong-tier promotion as premature on operating-rule-articulation grounds:

- 4/4 instance saturation + density growth establishes the **observation pattern** is real (4 PHASE2C interpretive closeouts each maintain a §7-equivalent carry-forward register; density grew across cycles)
- Strong-tier codification per existing §13/§14/§15 precedent requires an **operating rule** the discipline codifies — what to *do* when the discipline applies. §13's operating rule: "build at least one permanent in-repo parallel-implementation gate for canonical findings at high-load closeout register." §14's operating rule: "fire both reviewer overlays at section-seal." §15's operating rule: "verify advisor-supplied anchors before drafting initiates."
- §3.4's Application checklist as authored is observation-framing ("watch for omission of carry-forward register at interpretive closeouts"; "watch for missing codification-candidate status precision"), not operating-rule-codification. The framing aligns with weak/medium-tier observation register, not strong-tier discipline codification

Per anti-momentum-binding (PHASE2C_10 scoping §6.1 Option A flag): provisional tier labels are inputs to per-candidate evidence review, not constraints. The reverse direction also operates — initial sub-spec adjudication (Strong) is also an input to dual-reviewer pass, not a constraint. Both reviewers' substantive pushback at operating-rule-articulation grounds carries; tier reverts to Medium.

**Operating-rule-pending status note**: Step 2 implementation arc may promote tier to Strong if §18 authoring articulates a concrete operating rule (e.g., "for interpretive arc closeouts at multi-step-arc register, maintain a dedicated §N carry-forward observation register near closeout end with explicit codification-candidate status flagging"). If operating rule does not crystallize at Step 2 dual-reviewer pass, tier holds at Medium with observation-strengthening status note rather than full discipline codification. Tier-promotion authority resides at Step 2 implementation arc dual-reviewer pass, not at this plan's seal.

**Codification scope**: full §18 codification with all four standard subsections.

- ### Principle: interpretive arc closeouts (closeouts whose load-bearing register includes synthesis of empirical findings into observations for downstream cycles) accumulate observations across implementation steps and surface them in dedicated registers. The register format may be lessons-synthesis (PHASE2C_6 §10), numbered observations (PHASE2C_7.1 §10), tracked-fix register with codification-candidate flagging (PHASE2C_8.1 §10), or cumulative-observation inventory at §N.0.0 anchor (PHASE2C_9 §7). Per-closeout register format may vary; the convention is the dedicated register itself.
- ### Trigger context: PHASE2C_6 (October 2026) seeded the methodology-discipline observation register with 2 observations that codified METHODOLOGY_NOTES §4-§7 via commit `536f737`. PHASE2C_7.1 (March 2026) extended to 5 numbered observations at §10. PHASE2C_8.1 (April 2026) introduced tracked-fix register table at §10 with 10 entries + 4 codification candidates that codified METHODOLOGY_NOTES §13 / §14 / §15. PHASE2C_9 (April 2026) consolidated cumulative-observation register at §7 with 11 carry-forward observations across Steps 1-4 feeding §7 evidence map at Step 5.
- ### Application checklist: (a) interpretive arc closeouts (load-bearing for cross-cycle synthesis) include a dedicated carry-forward observation register section; (b) register format aligns with closeout structure (lessons-synthesis OR numbered observations OR tracked-fix register OR cumulative inventory); (c) codification candidates within the register are explicitly flagged with status precision (codification candidate vs operationalized vs purely-observation); (d) cross-cycle consumption is enabled by the register — successor cycles consume the register as scoping input; (e) the register is positioned near closeout end (after substantive findings; before cross-references), consistent with the four PHASE2C closeout pattern.
- ### Failure-mode signal: watch for interpretive arc closeouts that omit the carry-forward observation register; watch for observations buried within substantive sections without dedicated register surface (cross-cycle visibility reduced); watch for codification-candidate status absent (status precision missing → register entries indistinguishable from in-section observations); watch for register format misalignment with closeout structure (e.g., tracked-fix register without table format; cumulative observations without inventory anchor).

**Cross-reference targets**: §11 closeout-assembly checklist as running drafting-cycle pattern (parent discipline at the closeout-assembly register; §18 specifies the carry-forward observation register sub-discipline within §11's broader closeout-assembly framework); §10 anti-pre-naming as standing discipline (cross-cycle consumption at §18 must avoid pre-naming successor cycle's codification thresholds; observations enter register with status-precision pending successor cycle adjudication).

### §3.5 Candidate (5) — Pre-fire audit pattern at session-close-of-prior-session

**Candidate framing**: at session-close of a session that authored a sub-spec or scoping doc, a pre-fire audit pattern operationalizes a final substantive read of the deliverable before next-session fire. The audit catches sequencing defects (cross-section terminology drift; section-author-discipline check misalignment; commit-sequence violations) that are structurally between drafting cycle and fire cycle.

**Evidence count**: 1 instance at PHASE2C_9 Step 5 → Step 6 sub-spec drafting cycle.

Specifically: PHASE2C_9 Step 6 sub-spec at commit `d1657bd` had a pre-fire audit at session-close (described in CLAUDE.md as: "pre-fire Concern N audit CLEAN at session-close 5 sequencing checks"). The audit cleared 5 sequencing checks before next-session Step 6 fire.

**Tier adjudication**: **Weak** (confirms scoping doc §5.2 provisional tier).

Single instance is below codification threshold for full-section register. The pattern was operationally validated at PHASE2C_9 Step 5 → Step 6 transition but has not yet recurred at structurally distinct surfaces. Per ChatGPT guardrail 2 ("weak candidates visibly weak"), tier holds at weak; codification register is observation-only.

**Codification scope**: folded observation-only entry at §16 ### Failure-mode signal (recommended) OR brief §20 dedicated section. The folding-into-existing-§11 option is structurally precluded by §5.4 ChatGPT guardrail 4 (§1-§15 stable; only §16+ append) — modifying §11's existing content would be a §1-§15 edit out of PHASE2C_10 scope.

Recommended placement: append a "Watch for absence of pre-fire audit at session-close-of-prior-session for sub-spec / scoping deliverables; one PHASE2C_9 instance operationally validated the discipline at distinct surface (session-close 5 sequencing checks); cross-cycle accumulation pending; status observation-only + cross-cycle-pending" paragraph at §16 anchor-prose-access discipline ### Failure-mode signal. The pre-fire audit pattern is structurally adjacent to anchor-prose-access discipline (both concern session-boundary register precision); folding into §16 (newly authored at PHASE2C_10; in §16+ scope) preserves §1-§15 stability while surfacing the observation at topical-adjacency register.

Alternative: brief §20 dedicated section with status-precision register (observation-only + cross-cycle-pending), parallel to §19 candidate (3) brief dedicated section. Visibility advantage; convention alignment register depends on Step 2 implementation arc dual-reviewer pass.

Selection deferred to Step 2 implementation arc dual-reviewer pass per anti-pre-naming option (ii) at this plan's seal.

**Cross-reference targets**: §11 closeout-assembly checklist (parent discipline at the drafting-cycle pattern register; cross-reference target at §16 ### Failure-mode signal entry OR §20 trigger context); §16 anchor-prose-access discipline (operational adjacency at session-boundary register).

### §3.6 Candidate (6) — Self-first-then-reviewer adjudication discipline

**Candidate framing**: at adjudication of reviewer-supplied suggestions, the substantive review fires first from the receiving cycle's own substantive overlay, then engages reviewer-suggestion adjudication. The discipline is structurally distinct from the existing reasoned-reviewer-suggestion adjudication (memory rule `feedback_reviewer_suggestion_adjudication.md`) which addresses reviewer-suggestion processing once reviewer suggestions are available; self-first-then-reviewer addresses the sequencing of the receiving cycle's own substantive review relative to reviewer engagement.

**Evidence count**: 1 instance at PHASE2C_10 scoping cycle (Q1 engagement mode reflection).

Specifically: at scoping inputs lock cycle Q1 (engagement mode reflection), the discipline emerged as a structural observation about how the receiving cycle's own substantive overlay should fire before reviewer-suggestion adjudication, not after.

**Tier adjudication**: **Weak** (confirms scoping doc §5.2 provisional tier).

Single instance, observation emerged at scoping cycle itself; pattern has not yet recurred at structurally distinct surfaces. Per scoping doc §5.5: "Emergent candidate from this scoping cycle (Q1 engagement mode reflection) is NOT codified as operating rule at this cycle. Status: observation-only + cross-cycle-pending. One instance (this scoping cycle); insufficient evidence for operating-rule codification."

**Codification scope**: folded observation-only entry at §16 ### Failure-mode signal (recommended; topical adjacency: reviewer-engagement register) OR brief §20 dedicated section. The folding-into-existing-§14 option is structurally precluded by §5.4 ChatGPT guardrail 4 (§1-§15 stable; only §16+ append) — modifying §14's existing content would be a §1-§15 edit out of PHASE2C_10 scope.

Recommended placement: append a "Watch for reviewer-engagement-cycle absence of receiving-cycle's own substantive overlay before reviewer-suggestion adjudication; one PHASE2C_10 scoping cycle instance (Q1 engagement mode reflection); discipline structurally distinct from reasoned-reviewer-suggestion adjudication (which addresses post-engagement processing) — self-first-then-reviewer addresses pre-engagement sequencing; cross-cycle accumulation pending; status observation-only + cross-cycle-pending" paragraph at §16 ### Failure-mode signal. Topical adjacency at §16 captures the reviewer-engagement register slot; folding aligns convention.

Alternative: brief §20 dedicated section with status-precision register (observation-only + cross-cycle-pending), potentially co-located with candidate (5) at §20 if Step 2 implementation arc surfaces preference for combined weak-tier observation register at §20.

Selection deferred to Step 2 implementation arc dual-reviewer pass.

**Cross-reference targets**: §14 bidirectional dual-reviewer register-precision (parent discipline at the reviewer-engagement register; cross-reference target — this candidate is a sub-discipline within §14's broader framework); reasoned-reviewer-suggestion adjudication discipline (`feedback_reviewer_suggestion_adjudication.md` user-memory; orthogonal discipline at reviewer-suggestion processing once reviewer suggestions are available).

### §3.7 Tier precision summary table

Final tier adjudication for the six candidates after §3.1-§3.6 evidence review:

| # | Candidate | Scoping §5.2 provisional | §3 adjudicated | Adjudication basis | §16+ placement |
|---|---|---|---|---|---|
| 1 | Anchor-prose-access discipline | Strong | **Strong** (confirmed) | 4 instances; real catches each instance; structural inevitability | §16 dedicated section |
| 2 | Procedural-confirmation defect class | Strong | **Strong** (confirmed) | 3 instances at distinct surfaces (2 PHASE2C_9 + 1 PHASE2C_10 plan working-draft commit `d0222c7`; instance #3 operationally validated at this very session per §0.4); defect class operationally validated | §17 dedicated section |
| 3 | Spec-vs-empirical-reality finding pattern | Weak | **Weak** (confirmed; medium-pending) | Cumulative 6 across 3 cycles (PHASE2C_9 = 3; scoping = 2; PHASE2C_10 plan drafting = 1); pattern observed but increment over §1 incremental | Brief §19 dedicated section (observation-only + cross-cycle-pending status-register) |
| 4 | §7 carry-forward density at interpretive arc closeouts | Medium | **Medium** (confirmed; operating-rule-pending) | 4/4 instance saturation + density growth supports observation-strengthening, but operating-rule articulation incomplete (Application checklist as authored is observation-framing not operating-rule-codification per §13/§14/§15 precedent); strong-tier promotion deferred to Step 2 implementation arc if operating rule articulated | §18 dedicated section at Medium codification scope (full 4-subsection structure with operating-rule status note) |
| 5 | Pre-fire audit pattern | Weak | **Weak** (confirmed) | 1 instance; below codification threshold | Folded into §16 ### Failure-mode signal OR brief §20 |
| 6 | Self-first-then-reviewer | Weak | **Weak** (confirmed) | 1 instance; emerged at scoping cycle itself | Folded into §16 ### Failure-mode signal OR brief §20 |

**Patches applied vs scoping doc §5.2**: candidate (4) §7 carry-forward density patched upward Medium → Strong per Fire 3(i) 4/4 instance saturation finding. All other tier labels confirmed.

**Per anti-momentum-binding flag operating**: provisional tier labels were inputs to per-candidate evidence review, not constraints. Patch on candidate (4) is reasoned via Fire 3(i) empirical evidence count; no other patches applied.

---

## §4 Emergent-vs-folded adjudication for advisor-register sub-pattern

### §4.1 Adjudication question

A sub-pattern observation surfaced at PHASE2C_10 scoping cycle: reviewer-register anchors (advisor-supplied numerical or structural anchors that operate as drafting-cycle inputs) are themselves susceptible to the spec-vs-empirical-reality pattern when the advisor cycle's verification context and receiving cycle's verification context differ. Specifically: scoping cycle's §1-§7 stale anchor (entry 4) and §16-as-single-section framing (entry 5) both originated from advisor-supplied framings that referenced non-current file state.

The adjudication question: does this sub-pattern fold into candidate (3) spec-vs-empirical-reality (which would treat advisor-register anchors as another instance of the general pattern), OR surface as a separate emergent observation distinct from candidate (3)?

### §4.2 Evidence enumeration

Evidence supporting **fold into candidate (3)**:

- Both entries 4 and 5 fit the spec-vs-empirical-reality definition (cite remembered structure rather than verified structure)
- METHODOLOGY_NOTES §15 anchor-list empirical-verification discipline already covers advisor-supplied anchor verification at receiving cycle as principle; entries 4 and 5 are operational instances of the §15 principle's failure mode, which feeds the candidate (3) spec-vs-empirical-reality observation register
- Cumulative count register at scoping doc §6.2 explicitly counts entries 4 and 5 as instances of the candidate (3) pattern (cumulative 5; per-cycle 3+2)

Evidence supporting **separate emergent observation**:

- Advisor-register anchors operate at a structurally distinct register from author-cycle anchors (advisor's mental model carries implicit drift risk that author's own structural memory does not, per §15's discipline framing)
- The catch mechanism differs: advisor-register anchor catches require receiving-cycle verification at pre-drafting fire (per §15's pre-drafting register); author-cycle anchor catches may surface at section-seal or post-commit (per §1's broader empirical-verification surface)
- If treated as emergent, the sub-pattern could surface as a §15 ### Failure-mode signal extension distinct from §1's failure modes

### §4.3 Disposition

**Disposition: fold into candidate (3) at scoping cycle's existing register; do NOT surface as separate emergent observation at PHASE2C_10.**

Rationale: scoping doc §6.2 already counts entries 4 and 5 within candidate (3)'s cumulative register at the scoping cycle's adjudication. Treating the same instances as separate emergent observation at sub-spec drafting cycle would either (a) double-count the instances across two candidates (artificial inflation of evidence base), or (b) require unfolding the scoping doc §6.2 count from candidate (3) which would patch the scoping doc post-seal (out of scope; scoping doc is sealed at `1053c73`).

The advisor-register anchor sub-pattern is observed within candidate (3); its specific catch mechanism is covered by §15 anchor-list empirical-verification discipline's pre-drafting register. The sub-pattern does NOT require separate codification at PHASE2C_10 because:

- Candidate (3) at observation-only + cross-cycle-pending status preserves the sub-pattern's observation status
- §15's existing principle covers the catch mechanism structurally
- Cross-cycle accumulation pattern operating; if advisor-register anchor sub-pattern's catch rate exceeds general spec-vs-empirical-reality pattern's catch rate at a future cycle, separate emergence may surface at successor cycle scoping; not pre-staged at PHASE2C_10

A 6th instance of candidate (3) was observed at this plan's Fire 3(ii): CLAUDE.md project-discipline notes section (line 459) cites METHODOLOGY_NOTES §1-§7 / §8 synthesis only, when actual file state is §1-§15. The instance fits candidate (3)'s pattern definition (cite remembered structure rather than verified structure) at the CLAUDE.md project-discipline notes register. **Disposition for the 6th instance**: registered within candidate (3) cumulative count per dual-reviewer pass instance #5 adjudication (Claude advisor + ChatGPT both confirmed: same defect class regardless of source document). Cumulative count = 6 as locked at §3.3 evidence count. The CLAUDE.md staleness counts as a within-cycle PHASE2C_10 plan drafting instance (surfaces at PHASE2C_10's drafting cycle via Fire 3(ii)) regardless of when the staleness was originally introduced into CLAUDE.md. Tier holds at weak per §3.3 adjudication.

CLAUDE.md project-discipline notes section update is NOT in PHASE2C_10 scope per §1.4 hard scope ("scope limited to METHODOLOGY_NOTES update from PHASE2C_9 + PHASE2C_10 scoping carry-forward candidates"); the CLAUDE.md staleness fix carries forward as a tracked observation for either successor cycle scoping consideration OR a separate one-line CLAUDE.md project-discipline notes refresh outside PHASE2C_10's implementation register.

---

## §5 Step 2 fire procedure (METHODOLOGY_NOTES.md update arc)

### §5.1 Pre-fire prerequisites

Before Step 2 implementation arc fires:

1. **This plan sealed**: dual-reviewer pass complete (anchor-prose-access discipline instance #5); both reviewers authorize Step 2 fire; patches surfaced applied; this plan committed at sealed register.
2. **Candidate codification text reviewed**: §3.1-§3.6 codification scopes adjudicated against METHODOLOGY_NOTES.md §13-§15 prose style and §10 anti-pre-naming + §14 bidirectional dual-reviewer register-precision conventions.
3. **§16+ section-number assignment verified**: §2.2 pre-registered assignment table reviewed against existing §1-§15 numbering chain; no number-collision; topical-adjacency rationale clean.
4. **§4 emergent-vs-folded adjudication sealed**: candidate (3) sub-pattern disposition (fold) carries to Step 2 implementation arc; no candidate-boundary ambiguity at fire register.
5. **CLAUDE.md Phase Marker reflects active plan**: Phase Marker entry from Fire 2 commit `eeffaa2` accurately describes Step 1 sub-spec drafting active state; Step 2 fire requires Phase Marker advance to "Step 2 implementation arc active" before Step 2 commit fires.

### §5.2 Step 2 fire activities (sequenced)

**Activity A — Step 2 entry pre-fire audit**: at session start, run pre-fire audit pattern (candidate (5) observation operationalized): verify clean state; verify this plan sealed; verify Phase Marker accurately describes pre-Step-2 state; verify no in-flight changes from prior session.

**Activity B — CLAUDE.md Phase Marker advance to "Step 2 active"** (standalone commit): update Phase Marker per project pattern; commit message format `docs(phase2c-10): CLAUDE.md Phase Marker — PHASE2C_10 Step 2 implementation arc active`.

**Activity C — METHODOLOGY_NOTES.md §16 authoring** (anchor-prose-access discipline candidate): author §16 with all four standard subsections per §3.1 codification scope; commit as working draft with status note in commit message; submit to dual-reviewer pass.

**Activity D — Apply Activity C patches; seal §16 commit**: apply any patches surfaced at Activity C dual-reviewer pass; commit sealed §16; re-fire dual-reviewer if patches surface new concerns.

**Activity E — METHODOLOGY_NOTES.md §17 authoring** (procedural-confirmation defect class): per §3.2 codification scope; same pattern as Activity C-D.

**Activity F — Apply Activity E patches; seal §17 commit**: same pattern as Activity D.

**Activity G — METHODOLOGY_NOTES.md §18 authoring** (§7 carry-forward density at interpretive arc closeouts): per §3.4 codification scope; same pattern as Activity C-D.

**Activity H — Apply Activity G patches; seal §18 commit**: same pattern as Activity D.

**Activity I — Weak-tier observation-only entries**: append observation-only entries per §3.3 candidate (3), §3.5 candidate (5), §3.6 candidate (6) at the placement adjudicated by Step 2 dual-reviewer pass (folded into existing sections OR brief §19/§20 dedicated sections); commit as working draft; dual-reviewer pass; apply patches; seal.

**Activity J — Final-assembly verification**: run METHODOLOGY_NOTES.md full-assembly verification per §11 closeout-assembly checklist as running drafting-cycle pattern; verify §1-§15 unmodified; verify §16+ numbering chain clean; verify cross-references resolve; commit final-assembly verification record.

**Activity K — CLAUDE.md project-discipline notes refresh** (optional, pending §4.3 disposition): if Step 2 dual-reviewer pass adjudicates that CLAUDE.md project-discipline notes section staleness fix is in PHASE2C_10 implementation scope (rather than carried forward to successor cycle), refresh the section to reflect §1-§15 + §16+ codified principles; otherwise defer.

**Activity L — Step 2 closeout assembly**: author Step 2 closeout summary documenting per-candidate codification commits, dual-reviewer pass disposition per section, and CLAUDE.md staleness disposition; commit at `docs/closeout/PHASE2C_10_RESULTS.md` (or equivalent path per Step 2 implementation arc adjudication).

**Activity M — CLAUDE.md Phase Marker advance to "PHASE2C_10 SEALED"**: update Phase Marker per project pattern; commit message `docs(phase2c-10): CLAUDE.md Phase Marker — PHASE2C_10 SEALED`.

**Activity N — Tag commit at Step 2 seal**: candidate tag `phase2c-10-methodology-consolidation-v1` at sealed register; user authorization required before push.

### §5.3 Codex routing for Step 2 substantive content

Per `feedback_codex_review_scope.md` user-memory rule: Codex adversarial review runs only on substantive code/work (closeouts, implementations); skip for scoping/deliberation docs.

**Activity C / E / G — METHODOLOGY_NOTES.md §16 / §17 / §18 authoring**: substantive content. **Codex review fires** at sealed register before Activity D / F / H seal commits, per the dual-reviewer + adversarial-review composition pattern (METHODOLOGY_NOTES §14 application checklist item 5).

**Activity I — Weak-tier observation-only entries**: substantive content but lighter register. Codex routing adjudicated at Step 2 dual-reviewer pass; if folded into existing sections, lighter-touch review may suffice; if dedicated §19/§20 sections, full Codex pass.

**Activity J — Final-assembly verification**: substantive verification at the assembly register; Codex routing fires per §11 closeout-assembly checklist's verification framework.

**Activity L — Step 2 closeout**: substantive synthesis at the closeout register; Codex review fires per project convention.

**Activity B / K / M — CLAUDE.md updates**: state-field updates at the project-discipline register; lighter-touch review (project convention; CLAUDE.md updates do not require full Codex pass).

### §5.4 Step 2 fire gating criteria

Step 2 implementation arc seals when:

1. All activities A-N (or A-M with K omitted per §4.3 deferral) complete with sealed commits.
2. METHODOLOGY_NOTES.md §16 / §17 / §18 dedicated sections each pass dual-reviewer + Codex review; all surfaced patches applied; reviewer authorization at sealed register.
3. Weak-tier observation-only entries at §3.3 / §3.5 / §3.6 placed and reviewed at lighter-touch register; placement disposition documented in Step 2 closeout.
4. Final-assembly verification clean: §1-§15 unmodified; §16+ chain clean; cross-references resolve; no section-number collisions.
5. Step 2 closeout authored, dual-reviewer pass clean, sealed at closeout register.
6. CLAUDE.md Phase Marker advanced to "PHASE2C_10 SEALED"; tag commit candidate `phase2c-10-methodology-consolidation-v1` at sealed register; user authorization for tag + push.

---

## §6 Sub-spec verification framework

### §6.1 Anchor-prose-access discipline at sub-spec dual-reviewer pass (instance #5)

This plan's seal requires anchor-prose-access discipline instance #5 dual-reviewer pass:

- Paste relevant prose excerpts from this plan (§1 filename lock + §2 section numbering + §3 per-candidate codification text + §4 emergent-vs-folded adjudication + §5 Step 2 fire procedure)
- ChatGPT first-pass at substantive register against actual prose
- Claude advisor substantive prose-access pass at instance #5 register against actual prose
- Both reviewers authorize commit; patches surfaced applied; THEN seal

Instance #5 fires as next operational step post-this-draft-commit. Commit authorization at both reviewer registers required before this plan seals.

Per the discipline's structural payoff: each of instances #1-#4 surfaced real defects via prose access that summary-only review missed by construction. Instance #5 expectation: prose-access pass at this plan's substantive register may surface defects in (a) per-candidate codification text precision, (b) tier adjudication rationale, (c) cross-reference target accuracy, (d) Step 2 fire procedure sequencing — defects that summary-only review would not surface.

### §6.2 Per-candidate evidence count cross-checks

Evidence counts cited in §3.1-§3.6 are anchored at:

- Candidate (1) anchor-prose-access discipline 4 instances: PHASE2C_9 §8.4 mandatory entry #4 standing instruction record + scoping doc §6.3 instance #4 disposition (verified at Fire 3 pre-drafting against scoping doc actual prose)
- Candidate (2) procedural-confirmation defect class **3 instances**: PHASE2C_9 Step 5 working-draft commit `e11e806` + PHASE2C_9 Step 6 closeout assembly first commit (verified at scoping doc §5.2 strong-tier pairing) + PHASE2C_10 plan working-draft commit `d0222c7` (instance #3 surfaced at instance #5 dual-reviewer pass per §0.4)
- Candidate (3) spec-vs-empirical-reality **6 cumulative across 3 cycles**: PHASE2C_9 §8.4 mandatory entry #2 (3 within-arc) + scoping doc §6.2 entries 4-5 (2 within-cycle) + Fire 3(ii) CLAUDE.md project-discipline notes staleness observation (1 within-cycle, dispositioned at instance #5 dual-reviewer pass per §4.3)
- Candidate (4) §7 carry-forward density 4 instances: Fire 3(i) verification across PHASE2C_6 §10 + PHASE2C_7.1 §10 + PHASE2C_8.1 §10 + PHASE2C_9 §7 (verified at Fire 3(i) against actual closeout structure)
- Candidate (5) pre-fire audit pattern 1 instance: PHASE2C_9 Step 6 sub-spec session-close 5 sequencing checks (verified at scoping doc §6.4 and CLAUDE.md Phase Marker entry for Step 6 sub-spec)
- Candidate (6) self-first-then-reviewer 1 instance: PHASE2C_10 scoping cycle Q1 engagement mode reflection (verified at scoping doc §5.5 + §6.4)

Cross-checks at instance #5 dual-reviewer pass: each evidence count traced to the sourcing artifact; if reviewer surfaces count drift between this plan's citation and actual artifact, patch citation pre-seal.

### §6.3 Section-numbering verification

Section-number assignments at §2.2 verified at instance #5 dual-reviewer pass against:

- METHODOLOGY_NOTES.md current state §1-§15 (no collision at §16-§20)
- Topical-adjacency rationale (§16 adjacent to §15; §17 adjacent to §6; §18 adjacent to §11)
- Cross-reference target accuracy (each cross-reference at §3.1-§3.6 resolves to the cited existing section)

If reviewer surfaces section-numbering concerns (collision, topical-adjacency objection, cross-reference miss), patch §2.2 + §3.x cross-reference targets pre-seal.

---

## §7 Cross-references

### §7.1 Verification anchor chain

- PHASE2C_10 scoping decision sealed: `1053c73` on origin/main; locked scoping inputs at §1, deliberation surface at §2, path-by-path evaluation at §3, selection adjudication at §4, pre-registered framing at §5, carry-forward at §6, verification + dual-reviewer disposition at §7
- PHASE2C_9 sealed: `5442e6b` on origin/main; tag `phase2c-9-mining-retrospective-v1`; methodology-codification candidates surfaced at §8.4 mandatory entries #1-#4 + emergent #5
- METHODOLOGY_NOTES.md current state: §1-§15 (verified at this plan's Fire 3(ii) pre-drafting reads); §16+ append target for PHASE2C_10 implementation arc
- PHASE2C_10 Phase Marker advance commit: `eeffaa2` on main (Step 1 sub-spec drafting active state)
- Fire 3(i) §7 carry-forward density verification: 4 PHASE2C interpretive closeouts (PHASE2C_6 §10 / PHASE2C_7.1 §10 / PHASE2C_8.1 §10 / PHASE2C_9 §7) with §7-equivalent observation registers
- Fire 3(ii) METHODOLOGY_NOTES.md prose-reading: §13-§15 detailed read; §1-§15 structural survey; CLAUDE.md project-discipline notes staleness observation

### §7.2 Dual-reviewer disposition

This plan's seal requires anchor-prose-access discipline instance #5 dual-reviewer pass per §6.1. Status at this draft register: pre-seal; dual-reviewer pass next operational step.

Reviewer registers carrying forward from PHASE2C_10 scoping cycle:

- ChatGPT: scoping cycle adjudication on record (path (e) selected; Phase Marker defer; Codex skip). Available for sub-spec scope-lock + dual-reviewer pass instance #5.
- Claude advisor: scoping cycle adjudication on record (anti-momentum-binding flags; empirical verification on framing patches; instance #4 prose-access pass). Available for sub-spec scope-lock + dual-reviewer pass instance #5 + per-candidate tier review.

### §7.3 Successor cycle deferral

PHASE2C_10 implementation arc covers METHODOLOGY_NOTES update only per §1.4 hard scope. Post-PHASE2C_10 successor cycle scoping fires after Step 2 seal; scoping cycle direction NOT pre-committed at this plan's draft fire per anti-pre-naming option (ii).

Cross-cycle accumulation registers carrying forward from PHASE2C_10:

- Candidate (3) spec-vs-empirical-reality cumulative count = 6 across 3 cycles (locked at instance #5 dual-reviewer pass per §3.3 + §4.3 + §0.4): cross-cycle accumulation pattern operating; future-cycle adjudication of medium-tier promotion threshold per Option A flag preserved; operating-rule articulation question (whether candidate (3) is sub-class of §15 anchor-list empirical-verification) carries to Step 2 implementation arc
- Candidate (5) pre-fire audit pattern (1 instance): cross-cycle accumulation pending; future-cycle recurrence at distinct surface raises codification candidacy
- Candidate (6) self-first-then-reviewer (1 instance): cross-cycle accumulation pending; same pattern
- CLAUDE.md project-discipline notes staleness fix: pending §4.3 disposition (PHASE2C_10 implementation scope inclusion vs successor cycle carry-forward)

---

**End of PHASE2C_10 Plan working draft. Status: pre-seal; instance #5 dual-reviewer pass next operational step.**

# PHASE 5 SCOPING DECISION — Diagnostic Attribution Cycle

**Status:** SEALED at 2026-05-10T01:28:15Z

**Cycle anchor:** Phase 5 entry scoping cycle at fresh-session boundary post-Phase-4 SEAL. Phase 4 closed at `afc0bf4` (Task 7 reassessment close at NO-codification) + `e8f62f1` (Task 5 closeout deliverable seal — null result at PLAN §1.5) + tag `phase4-forward-test-v1` at deliverable seal commit per Path A.2 register-event boundary discipline.

**Authorship register:** Adjudication trail at Q-1 framing question entry → Q-2 synthesis adjudication → Q-3 advisor refinements 1+2 → Q-4 ChatGPT terminal-conclusion availability lock → Q-5 lock set ratification → Q-6 4-modification ratification → Q-7 SEAL bundle authorization (pending).

---

## §1 Cycle scope

Phase 5 = pre-fire diagnostic analysis cycle. Attribution of Phase 4 null result against pre-registered failure-mode taxonomy. Existing sealed artifacts only.

**Phase 5 is not an attempt to rescue Phase 4; it is an attribution cycle to determine what Phase 4's null result means.**

Cycle motivation: Phase 4 sealed at "no forward persistence detected at PLAN §1.5 success criterion." Stratum A 11/22 (binom p=0.5841), Stratum B 7/17 (binom p=0.8338); both fail to reject H_0 at well-below-threshold register. Substantive question for any successor cycle is what the null result means before another fire — which failure mode (or combination) is operating, and what successor experiments are eligible given the diagnostic finding.

## §2 Pre-registered content

### §2.1 Failure-mode taxonomy

Six modes pre-registered with sharper distinguishing axes to prevent post-fire interpretation drift toward multi-mode rationalization (per ChatGPT Mod 1 tightening):

- **(a) signal decay** = candidate-level temporal deterioration despite training/test validity. Alpha existed at training period; deteriorated at forward period; the *candidate* is the subject of the deterioration.
- **(b) cost drag** = realistic-cost-model differential. Alpha exists at gross level (low/zero bps); killed by realistic 15bps round-trip costs.
- **(c) cohort weakness** = population-level economic weakness even when statistical gate passes. Statistical AND-gate criterion is satisfied but the underlying *candidate population* is economically weak in aggregate.
- **(d) overfit AND-gate** = gate-construction flaw causing unstable selection logic. The *gate criterion itself* overfits regime-pair statistical noise; the selection mechanism is the subject of the flaw.
- **(e) bad success metric** = success-criterion misalignment. Positive forward Sharpe fraction (PLAN §1.5) is too coarse / wrong metric for "deployable alpha."
- **(f) regime change** = external market-structure shift invalidating historical transferability. 2026 BTC market structure fundamentally differs from 2020-2025 training universe; the *market context* is the subject of the change.

Distinguishing axes: (a) candidate-level vs (c) population-level; (d) gate-construction vs (f) external-market.

The taxonomy is classificatory, not ordinal; no failure mode is pre-registered as inherently more severe or more continuation-eligible than another. (ChatGPT Mod-pass-2 C2 anti-implicit-ranking lock.)

### §2.2 Multi-mode coexistence rules

Modes are NOT fully mutually exclusive. (a) signal decay can co-occur with (e) bad metric; (b) cost drag can co-occur with (c) cohort weakness; etc.

Diagnostic procedure produces continuous-or-binned indicator per mode. Pre-registered interpretation framework includes multi-mode handling — which combinations imply which successor classes; explicit handling rules for co-occurrences pre-registered before fire to avoid post-fire interpretation drift.

Specific operationalization (statistical tests, decision thresholds, indicator cutoffs, multi-mode combination rules) deferred to Phase 5 sub-spec drafting cycle for diagnostic procedure operationalization. **Phase 5 implementation work may not begin until the operationalization sub-spec exists OR Charlie explicitly authorizes a no-sub-spec direct implementation path. Interpretation thresholds must be frozen before any diagnostic execution.** (ChatGPT Mod-pass-2 C1 operationalization-freeze lock; anti-creep guard parallel to PLAN §1.5 interpretation guard discipline.) Aligned with §1.5 interpretation guard discipline (pre-register interpretation framework before fire).

### §2.3 Diagnostic findings → successor-cycle class mapping

Pre-registered mapping per ChatGPT lock:

- **(a) signal decay** → empirical-continuation eligible (extended forward window, additional regime testing)
- **(b) cost drag** → cost-model investigation eligible (gross-vs-realistic decomposition)
- **(c) cohort weakness** → cohort-paradigm pivot required (alternative cohort sourcing)
- **(d) overfit AND-gate** → gate-criterion pivot required (alternative gate design)
- **(e) bad success metric** → metric-redefinition cycle eligible (alternative success criteria)
- **(f) regime change** → meta-paradigm pivot eligible (different research framing or universe)
- **Multi-mode findings** → composite mapping per §2.2 rules
- **Terminal-conclusion finding** (per §2.5) → meta-paradigm pivot OR project pause / declared-research-line-exhausted close

### §2.4 Diagnostic findings → framing-question resolution-pressure mapping

This mapping (advisor Refinement 1; load-bearing) makes the framing question — (1) research-for-deployment / (2) research-for-framework / (3) research-for-rigor / (4) indeterminate — a substantive output of Phase 5 rather than indefinitely-deferred meta-decision:

- **(a) or (b)** → framing question can stay deferred under (4) indeterminate; empirically-conditioned continuation defensible under any framing
- **(c) or (d)** → framing question becomes load-bearing at Phase 5 SEAL; pivot direction depends on framing; Charlie register engagement required at successor cycle entry
- **(e)** → ambiguous; Phase 5 SEAL surfaces framing engagement explicitly
- **(f)** → framing question becomes load-bearing; pivot direction substantively determined by framing
- **Terminal-conclusion finding** (per §2.5) → framing question becomes load-bearing immediately; engages directly with project-identity question

Note: §2.4 groupings (e.g., (a)+(b) paired) are register-distinct from §2.3/§6 successor-cycle-class mappings (which separate (a) into empirical-continuation cycle vs (b) into cost-model investigation cycle). Both mappings are correct at their respective registers — §2.4 binds framing-resolution-pressure register; §2.3/§6 bind successor-cycle-class register. (Mod-pass-2 advisor F2 register-distinguishing clarification.)

### §2.5 Terminal-conclusion availability

A diagnostic finding is allowed to conclude that the AND-gate paradigm is likely exhausted for deployable BTC alpha under realistic costs. Pre-registered to prevent post-fire rationalization pressure toward "inconclusive, continue exploration" when substantive answer is paradigm exhaustion. Terminal conclusion is admissible regardless of which specific failure mode(s) emerge or whether multiple modes co-occur ambiguously. (Substantive-register availability — about paradigm-state.)

**Phase 5 is permitted to conclude that no successor empirical cycle is currently justified.** (Operational-register availability — about Phase 5 SEAL output authorizing or not authorizing a next cycle; ChatGPT Mod 2 explicit anti-rationalization sentence.)

These two availabilities operate independently — terminal substantive conclusion about paradigm exhaustion is one path; operational conclusion of no-successor-cycle-currently-justified is another; either or both can be Phase 5's output. (Mod-pass-2 advisor F1 paragraph-disambiguation lock — substantive degree-of-freedom preservation.) Terminal findings do not implicitly create another exploratory branch; "stop here" is a first-class admissible cycle outcome. Terminal conclusions are register-class-valid outcomes within Phase 5 and do not require ambiguity resolution in favor of continuation. (Mod-pass-2 ChatGPT C3 mechanical-precision closing.)

## §3 Deliverable

Phase 5 deliverable = **attribution report** at `docs/closeout/PHASE5_RESULTS.md` (sealed at Phase 5 SEAL register-event boundary per closeout SEAL precedent + Path A.2 register-event boundary discipline).

Report contents:
- Diagnostic procedure executed per §2.1 taxonomy + §2.2 multi-mode rules
- Per-mode indicator results (continuous-or-binned)
- Multi-mode interpretation per §2.2
- Successor-cycle class implication per §2.3
- Framing-question resolution-pressure assessment per §2.4
- Terminal-conclusion assessment per §2.5 (admit, reject, or surface paradigm-exhaustion conclusion)

NOT a rescue attempt. NOT pre-commitment to successor cycle scope.

## §4 Discipline locks

### §4.1 Hard scope binding

NO new fires, NO new hypotheses, NO new candidate generation, NO new methodology codification.

Source data limited to existing sealed artifacts on disk at Phase 5 cycle entry. **Derived statistics and diagnostic computations from existing sealed artifacts ARE allowed** (re-aggregations, alternative metric profiles on existing per-candidate trade data, statistical decomposition of existing forward Sharpe distributions, regime-conditioning of existing cohort indicators, etc.). **Acquisition of new empirical data is NOT allowed** — including additional BTC OHLCV history beyond what is already on disk, additional candidate generation, additional regime data, additional Critic/Proposer API calls. (ChatGPT Mod 3 derived-vs-new clarification.)

### §4.2 Anti-pre-naming

Phase 5.1+ successor scope eligible-not-named at this register per option (ii) preservation. PHASE2C_10-15 + PHASE4 scoping cycle precedent.

### §4.3 Anti-momentum-binding

Phase 5 SEAL register-event boundary does NOT authorize successor cycle entry. Explicit Charlie register authorization required at successor cycle entry per `feedback_authorization_routing.md` hard rule. SEAL register-event boundary at any prior arc does NOT imply Phase 5 sub-spec drafting cycle authorization or Phase 5+ successor authorization.

### §4.4 Per-fix adjudication

Applies at any reviewer cycle within Phase 5 per `feedback_reviewer_suggestion_adjudication.md`. No bulk-accept of reviewer findings; reasoned per-finding ADOPT/PUSHBACK per substantive merit at register-precision.

### §4.5 Pacing discipline

Phase 5 cycle entry occurs at this SEAL fire (the canonical artifact at this commit becomes binding spec for Phase 5; cycle-internal work begins post-SEAL). Phase 5 sub-spec drafting cycle (default-required per §2.2 operationalization-freeze lock; no-sub-spec direct implementation path requires explicit Charlie register authorization) is register-class-distinct successor cycle at fresh-session boundary per PHASE2C_10-15 + PHASE4 scoping cycle precedent; Charlie register authorization required at sub-spec drafting cycle entry. (Mod-pass-2 advisor F3 cycle-boundary sharpening.)

### §4.6 Sealed-content invariance

Phase 4 sealed corpus invariant. PHASE4_RESULTS.md at `e8f62f1`, METHODOLOGY_NOTES.md sealed corpus, CLAUDE.md Phase Marker prior entries are demoted-prior-state and shall not be modified. Diagnostic analysis reads from sealed corpus, never modifies.

## §5 Adjudication register at Phase 5 entry scoping cycle SEAL

Charlie register authorization boundaries cumulative through Phase 5 entry scoping cycle SEAL register-event boundary:
- Q-1 framing question entry → reviewer divergence routed (ChatGPT (1)-primary lean; Claude advisor (4)-indeterminacy framing)
- Q-2 synthesis adjudication → reviewer convergence on Approach A (diagnostic-first cycle)
- Q-3 advisor refinements 1+2 (multi-mode rules + framing-question mapping) → both ADOPTED at adjudicate-now boundary
- Q-4 ChatGPT terminal-conclusion availability lock → ADOPTED at convergence
- Q-5 consolidated lock set ratification → "Authorized 1" ratify-as-stated (advisor optional (g) entry NOT folded; substantively covered by §2.5)
- Q-6 ChatGPT 4-modification ratification (sharpened §2.1 / §2.5 explicit sentence / §4.1 derived-vs-new clarification / §6 breadth reduction) → ALL 4 ADOPTED per per-fix substantive merit at register-precision
- Q-7 SEAL bundle authorization → ADOPTED at 2026-05-10T01:28:15Z (Charlie register convergence at "Authorized seal" post-V#-chain pre-SEAL verification CLEAN; ChatGPT + Claude advisor concurrence at SEAL register-event boundary)

Reviewer pass cycle status: ChatGPT structural overlay + Claude advisor full-prose-access pass operated at substantive register during framing/synthesis/lock-set/modification-set adjudication. Pre-SEAL re-pass on written MD per project pattern. Codex skipped at scoping cycle register-class per `feedback_codex_review_scope.md` (process/spec deliverable register-class-distinct from substantive code/work register-class).

## §6 Successor cycle eligible-not-named

Per anti-pre-naming option (ii) preservation: Phase 5 SEAL register-event boundary does NOT pre-commit Phase 5.1+ successor cycle scope. Register-class-eligible successor paths directly implied by §2.3 taxonomy mapping (NOT pre-committed at this register; ChatGPT Mod 4 narrowed to taxonomy-direct successors only):

- Empirical-continuation cycle — eligible under (a) findings
- Cost-model investigation cycle — eligible under (b) findings
- Cohort-paradigm pivot cycle — eligible under (c) findings
- Gate-criterion pivot cycle — eligible under (d) findings
- Metric-redefinition cycle — eligible under (e) findings
- Meta-paradigm pivot cycle — eligible under (f) or terminal-conclusion findings
- Project pause / declared-research-line-exhausted close — eligible under terminal-conclusion findings (per §2.5 explicit no-successor-cycle availability)

Charlie register authorization required at successor cycle entry register-event boundary per `feedback_authorization_routing.md` hard rule.

---

**End of PHASE 5 SCOPING DECISION (working draft pre-SEAL).**

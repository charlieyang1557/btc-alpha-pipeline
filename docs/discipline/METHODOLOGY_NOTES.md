# Project-Discipline Methodology Notes

**First-codified:** 2026-04-26 (during corrected-engine project arc closeout)
**Scope:** standing project-discipline principles that apply across all work cycles, not bound to a specific phase or task.

---

## §1 Empirical verification for factual claims

### Principle

Any specific quantitative or referential claim — in dispatch text,
prose, table cells, code comments, file paths, JSON structure
references, anywhere that lands in committed artifacts — must be
empirically verified against canonical data before the artifact is
committed. Plausible reasoning is not a substitute for empirical
query.

The discipline operates on two axes: **when** verification happens
within a drafting cycle (stage-specificity), and **how** the
verification is structurally auditable by future readers (operational
specificity). The PHASE2C_7.1 arc surfaced operational refinements on
both axes — recompute-before-prose at framing-summary stage as the
stage-specific catch-window for precision-overshoot defects, and V7
grep-able citation as the operational-specific structure that makes
each claim's canonical-artifact back-pointer auditable.

### Trigger context

This discipline was first codified during Task 8b ("calibration bands
need empirical grounding") and generalized during Tasks 9 and 11.
Across the corrected-engine project arc, the following factual-claim
defects were caught by empirical verification before they shipped:

- **Task 8a:** Original calibration band `[-2.0, 0.5]` was empirically
  wrong relative to the strategy authors' own design intent
  (mean_reversion's docstring set [-1.5, 1.0]). Caught when
  mean_reversion's +1.077 Sharpe required calibration audit.
- **Task 9 §3:** Initial outlier-identity claim was `0bf34de1`
  (rank-1 candidate); empirical query showed actual outlier was
  `ca5b4c3a` (delta -1.146 candidate). Caught mid-draft.
- **Task 9 §5:** Initial RSI section reference was `§2.3`; grep
  against original closeout showed actual section is `§2.1`.
- **Task 9 §7:** Initial rank-position claim for `95bf56e7` was
  `#11`; empirical query showed actual rank is `#16` (5 candidates
  between corrected #10 and #16).
- **Task 9 §8:** Initial canonical-artifacts list included
  `PHASE2C_CORRECTED_DELTA_REPORT.md` before the file was actually
  written.
- **Task 11 review-response §I:** Initial JSON-path reference was
  `summary_stats.p25/p75`; structure inspection showed actual path
  is `wf_test_period_sharpe_distribution.p25/p75`.
- **Task 11 review-response (in-fix):** Long-precision JSON values
  were quoted from Codex's report rather than directly verified
  against the canonical JSON; gap closed post-commit by direct query.
- **Codex Task 11 (3 medium findings):** Erratum §3 Q1/Q3, delta
  report §C Q1/Q3, delta report §E delta Q1, delta report §I
  per-candidate-artifacts reference — all unverified factual claims
  in committed canonical prose.

Eight instances of this defect class across two tasks confirm the
pattern is robust.

The PHASE2C_7.1 multi-regime evaluation gate arc (April 2026)
surfaced two operational refinements to the canonical principle:

**Recompute-before-prose at framing-summary stage (stage-specificity).**
Three precision-overshoot defects caught at framing-summary stage,
**before any prose drafted** — the catch-window the strengthening
operationalizes:

- **Pre-prose framing-stage catch (§7 cohort enumeration):** §7
  framing summary's "7 of 8 cohort (a) candidates carry WF≤0"
  recomputed to actual "6 of 8" against `comparison.csv` — a
  1-of-8 precision-overshoot caught at framing summary, before §7
  prose draft began.
- **Pre-prose framing-stage surfacing (§8 by-theme):** §8 framing
  summary lacked the calendar_effect within-theme inversion
  observation; recompute against per-theme partition data surfaced
  it as a load-bearing structural observation that became §8 closing
  synthesis bullet 1. The observation surfaced at framing-summary
  stage and entered the prose draft at first writing, rather than
  being added at prose-review stage.
- **Pre-prose framing-stage tightening (§8 universal-claim):** §8
  framing summary's "all candidates engaged-and-lost" universalized
  past the data; recompute confirmed 35/39 engaged-and-lost + 4/39
  fired <5 trades, tightening the framing at framing-summary stage
  before the universalizing language reached §8 prose.

Each catch is structurally a pre-prose, framing-stage catch — not a
prose-review catch and not a post-commit adversarial-review catch.
The catch-window shifts earlier in the drafting cycle relative to
prose-review or post-commit catches. Cost: one canonical-artifact-
recompute per data-density section at framing-summary stage. Payoff:
precision-overshoot defects surface before they harden into prose,
where revising them carries higher re-seal cost.

**V7 grep-able citation discipline (operational specificity).**
Every numerical claim in PHASE2C_7.1 closeout prose carries a
back-pointer to a canonical artifact field path, grep-able by a
future reader investigating the claim. Specific examples:
`comparison.json .filter_survivor_cross_tab.audit_only.passed_2022_passed_2024=8`;
`comparison.csv` row `bf83ffec97485f47.holdout_2024_sharpe = -0.6327...`.
Grep-ability operationalizes "future reader can reproduce the
query" — the back-pointer names the artifact + field directly
rather than narrating the derivation.

V7 enforcement at section-seal turns caught zero precision-overshoot
defects post-enforcement within PHASE2C_7.1's drafting cycles. The
discipline catches the defect class structurally rather than relying
on adversarial review to surface it.

### Application checklist

Before committing any artifact (code, prose, dispatch text, sign-off,
erratum), walk through the following questions:

1. **Quantitative claims:** Does every specific number (count, rank,
   threshold, percentage, magnitude) trace to an empirical query
   against the canonical data source? If yes, the query is
   reproducible (a future reader can run it). If no, run the query
   before commit.
2. **Referential claims:** Does every specific reference (file path,
   section number, function name, JSON key, line number, commit SHA,
   rank position) verify against the actual artifact? If the
   file/section/key/SHA might not exist or might be at a different
   location, verify.
3. **Identity claims:** Does every specific entity reference
   (candidate hash, batch UUID, strategy name, theme name) match the
   canonical record? If derived from memory or plausible inference,
   verify against the data.
4. **Existence claims:** Does every artifact referenced in the
   committed prose actually exist on disk at the cited path? If the
   artifact is "to be created" or "expected to exist," verify it
   landed before referencing as canonical.
5. **Framing-summary recompute checkpoint (stage-specificity):** For
   data-density sections (cohort enumerations, by-partition tables,
   statistical aggregates, derived-arithmetic claims), has the
   framing summary recomputed each canonical numerical claim against
   artifact data before prose drafting begins? Recompute at
   framing-summary stage catches precision-overshoot defects before
   they harden into prose, where revising them carries higher re-seal
   cost.
6. **Grep-able artifact-field back-pointer (operational specificity,
   V7):** For every numerical claim in committed prose, does the
   surrounding prose, drafting notes, or citation block name the
   canonical artifact + field path that produced the value? A future
   reader reproducing the claim should be able to grep the closeout
   for the artifact name and find the field path; if the
   artifact-field back-pointer is implicit or derivable but not
   literally named, the V7 discipline is not yet operational.

### Failure-mode signal

Watch for prose phrases that assert specific facts without preceding
query evidence in the conversation or commit history. Phrases like
"the outlier is `<hash>`," "the rank is `#N`," "the section is
`§X.Y`," "the path is `<dotted.path>`" — each is a specific-fact
claim that should have a verifying query or grep nearby. If the prose
has the claim but the conversation/commit doesn't have the verifying
query, the claim is unverified.

In dispatch text, watch for "the answer should be X" or "expect Y"
claims that imply specific numerical thresholds without consulting
the actual evaluation context. These often turn out to be
plausible-reasoning artifacts that don't survive empirical
verification.

In data-density section drafting, watch for precision-overshoot at
prose stage — claims like "7 of 8" / "all candidates" / "two-thirds"
that read clean in framing summaries but don't survive recompute
against the underlying artifact. The catch-window for this defect
class is at framing-summary stage; if the precision-overshoot
surfaces only at prose review or only at adversarial review, the
recompute-before-prose discipline was not yet operational.

In committed canonical prose, watch for numerical claims that lack
a grep-able back-pointer to a canonical artifact field. A claim
like "the carry-forward rate was 66.7%" without a citation block
naming `comparison.csv` row + field is structurally unauditable —
a future reader cannot reproduce the value without re-deriving the
claim's provenance from surrounding context. The V7 discipline
catches this gap structurally; if it surfaces only at adversarial
review, V7 enforcement was not yet operational at section-seal.

---

## §2 Meta-claim verification discipline

### Principle

Confident-sounding meta-claims about process state — "we've verified X," "the framing is pinned," "re-dispatch is low-value," "every step has been checked" — need the same empirical-verification discipline as artifact-level claims. Plausible reasoning at the meta layer can fail in the same way as plausible reasoning at the artifact layer.

### Trigger context

This discipline was codified during the Task 11 skip-vs-redispatch adjudication. The in-conversation argument "every number in the fix is empirically grounded in fresh queries against canonical artifacts" was made as a confident process claim, but empirical inspection of the fix showed that:

- The JSON-precision values cited in the §I rewrite were quoted from Codex's report, not from a fresh query against the canonical JSON.
- The "verified at every step" claim itself was not the result of walking through every number in the fix and tracing each to a query — it was an inferred claim from "you applied fixes via pandas.quantile() and self-caught the summary_stats path error, therefore the fix is fully verified."

The first inference (verification was thorough) was plausible. The second inference (therefore every number is grounded) didn't follow rigorously from the first. The defect class is the same as the artifact-level claims: confident assertion without empirical walk-through.

### Application checklist

Before making a confident process claim ("we've verified," "the framing is pinned," "this is low-value," "every step is checked"), walk through:

1. **What does "verified" specifically mean here?** Did I run queries against every specific claim, or did I reason that the verification was thorough?
2. **Where did I trace each claim to a query?** If I can't point to specific verifying evidence in the conversation/commit history for each load-bearing component, the claim is inferred, not empirical.
3. **What specifically would change my assertion?** If the answer is "if any of these specific things were wrong" but I haven't checked those specific things, the assertion is provisional, not robust.

### Failure-mode signal

The reasoner has a built-in incentive to assert confidence — confident claims close discussions, end loops, and reduce review surface. The discipline is to be suspicious of one's own confident process claims, especially when they happen to favor the path of less work (skip the review, no need to re-verify, the fix is done).

When reviewing a meta-claim during dual-reviewer adjudication, ask: "is this claim empirically grounded, or is it inferred from plausible reasoning?" If the latter, push back even when it's the more convenient path.

---

## §3 Regime-aware calibration bands

### Principle

Calibration bands for strategy expected behavior must account for what regime, sample size, and evaluation scope the actual evaluation is running on, not what feels intuitively right. Before setting a calibration band, query: "what does the actual evaluation look like — single-regime or multi-regime, what sample sizes, what time scope?" — and calibrate against that.

### Trigger context

This discipline was first surfaced during Task 8a Phase 1B corrected baseline calibration. The original Task 8a dispatch set a generic `[-2.0, 0.5]` calibration band assuming "naive baselines should produce negative-or-near-zero walk-forward Sharpe." The band was empirically wrong because:

- The strategy authors' own docstrings explicitly stated higher upper expected bounds (e.g., mean_reversion's [-1.5, 1.0] in `strategies/baseline/mean_reversion.py`).
- The actual evaluation regime was single-regime 2021 sub-windows (the v2 walk-forward generator's quarterly windows from the 2020-2021 disjoint train range), where mean-reversion-style baselines have a documented design-intent fit.
- The band was implicitly assuming multi-regime evaluation when the actual evaluation was single-regime.

When mean_reversion's corrected Sharpe came in at +1.077 (above the generic 0.5 band but well within the strategy author's [-1.5, 1.0] band), the resolution was to switch to per-strategy author-band calibration plus add the FP9 forward-pointer documenting that multi-regime canonical baselines are deferred work.

### Application checklist

Before setting a calibration band for any expected-behavior assertion (Sharpe range, return range, drawdown range, etc.):

1. **Regime check:** Does the evaluation cover one regime (e.g., single time period, single market environment) or multiple regimes? A band calibrated for multi-regime evaluation will be wrong if the actual evaluation is single-regime.
2. **Sample-size check:** Does the evaluation have enough sample size to support the band's implied confidence? A tight band with n=4 windows is implicitly wider than the same band with n=40 windows.
3. **Author-stated expectation check:** If the artifact under evaluation has documented expected behavior (strategy docstring, methodology document, prior closeout), consult that source before setting a generic band.
4. **Scope check:** Is the band trying to assert "this is canonical multi-regime production behavior" or "this is engine-correctness sanity for one regime"? Different scopes warrant different bands; generic-sounding bands that elide scope are usually wrong for the actual scope.

### Failure-mode signal

Watch for calibration-band statements in dispatch text that read as universal expected-behavior claims ("naive baselines should produce X," "good strategies should fall in [Y, Z]"). If the band doesn't reference the actual evaluation regime, the actual sample size, or the actual artifact's documented expected behavior, it's a generic band — and generic bands are usually empirically wrong for the specific evaluation they're being applied to.

If the band is set without consulting the strategy authors' own documented expectations (when those exist), that's a methodology defect even if the band happens to land in the right range by accident.

---

## §4 Scale-step discipline for empirical evaluations

### Principle

When an empirical evaluation can be run at multiple sample sizes (smoke / partial / full), each scaling step adds information that earlier steps cannot provide. Do not draw load-bearing conclusions from intermediate steps before the data the later steps will provide is available. Treating smoke or partial-sample results as decision-quality evidence over-weights the data and produces under-supported conclusions.

### Trigger context

This discipline was codified during the PHASE2C_6 evaluation gate arc (April 2026). The arc executed three runs against the same 198-candidate batch:

- **Smoke (4 candidates):** plumbing verification — script correctness, lineage stamping, failure handling. Produced no universe-level claim.
- **Primary universe (44 candidates):** within-batch result (1 of 44 winners passed the 2022 regime holdout). Established the within-population finding but did not yet enable the comparative claim.
- **Audit universe (198 candidates):** comparative finding (audit-only pass rate 12/154 = 7.79% > primary pass rate 1/44 = 2.27%). The audit-only-exceeds-primary comparison is the closeout's load-bearing finding and was not derivable from earlier steps.

If smoke alone (0/4 passed) had been treated as decision-quality evidence, the closeout's framing would have been "all winners fail 2022" — under-supported because 4 deliberately-selected candidates can't establish a universe-level claim. If the primary alone (1/44) had been treated as decision-quality evidence, the framing would have been "WF gate has weak selection power" — also under-supported because there's no comparison population. The comparative claim required all three runs.

### Application checklist

Before treating any sample-size result as decision-quality evidence:

1. **What scope of claim does this sample size support?** A 4-candidate smoke supports plumbing claims and existence claims (the script ran, this candidate type is observable) but not population claims. A within-population sample supports within-population claims but not comparative claims.
2. **What information would the next scaling step add?** If the next step would change the framing materially, the current step's data is intermediate, not load-bearing.
3. **What is the cost-information ratio of running the next step?** If the next step is cheap (minutes, not days), running it before drawing load-bearing conclusions is the right discipline.
4. **What would I write in the closeout if I had to commit now?** If the answer changes once the next step's data is in, current data is not closeout-quality.

### Failure-mode signal

Watch for "the smoke shows X, so we can conclude Y" reasoning where Y is a population-level or comparative claim. Smoke results are plumbing evidence; population claims need population samples; comparative claims need comparison populations. Conflating the layers produces over-confident closeouts that future evidence may invalidate.

The complementary failure mode is over-engineering — running every possible sample size before drawing any conclusion. The discipline is to run the sample size that supports the load-bearing claim, not every sample size that's logically possible.

---

## §5 Precondition verification for structural and organizational principles

### Principle

Before applying a structural or organizational principle to a specific case (e.g., "verify before interpret," "group similar items together," "section-scope separation," "name the most important thing for clarity"), verify the principle's preconditions hold for that specific case. The principle's correctness in the abstract does not transfer automatically — preconditions need to be checked against the specific situation. Generic appeals to clarity, structure, or readability tend to bypass precondition verification and produce recommendations that are right in the abstract but wrong in the specific.

### Trigger context

This discipline was codified during the PHASE2C_6 evaluation gate closeout drafting. Across one drafting cycle, six instances of the same meta-error pattern surfaced:

1. **§3/§4-first drafting order recommendation:** Applied "verify before interpret" without checking whether §3/§4's empirical content was already pinned by prior commits (it was, in `d6f481a` and `e6cecb9`). The protective discipline was redundant for the specific case.
2. **Footnote on near-miss cluster size discrepancy:** Applied "acknowledge corrections to prior published claims" without verifying whether commit messages count as "published claims" (they don't — they are development artifacts, not load-bearing audit-trail consumers).
3. **§8 grouping recommendation:** Applied "group similar themes together for narrative efficiency" without verifying whether mean_reversion and volatility_regime actually shared failure-mode structure (they didn't — mean_reversion engages-and-loses; volatility_regime doesn't engage at all).
4. **§7/§8 cross-section terminology:** Applied "section-scope separation discipline" without verifying whether referring to a named finding violates that scope (it doesn't — named-finding references are navigation aids, not interpretive overreach).
5. **AND-gate prioritization claim recommendation:** Applied "name the most important thing for clarity" without verifying whether the closeout's discipline tolerates prioritization claims (it doesn't — the closeout's pattern is enumerate-not-decide).
6. **Fifth-defect addition to §10:** Applied "name consequential defects in the defect list" without verifying whether the audit-survivor count discrepancy was actually a defect about to ship (it wasn't — the empirical query produced the verified value before any prose was written).

In each case, the recommended principle was correct in the abstract. The defect was applying the principle to a case whose preconditions did not hold. Six instances across one drafting cycle is a robust pattern worth its own discipline section.

### Application checklist

Before offering or accepting a structural or organizational recommendation:

1. **What are the principle's preconditions?** State explicitly what conditions need to hold for the principle to apply usefully.
2. **Do those preconditions hold for this specific case?** Walk through each precondition and check against the specific situation.
3. **Could the principle be wrong here even if it's right in general?** If the case has unusual structural properties (e.g., the empirical content is already pinned elsewhere; the entities being grouped don't actually share structure), the principle's protection might not apply.
4. **What specific evidence would I need to verify the preconditions?** If I can't articulate what would falsify the recommendation, the recommendation is faith-based rather than evidence-based.

### Failure-mode signal

Watch for recommendations that appeal to general principles ("for clarity," "for narrative efficiency," "to preserve discipline X," "by convention") without naming the specific case-level evidence that justifies the application. Generic appeals are a tell that precondition verification has been bypassed.

The reasoner has a pattern of generalizing principles confidently when the principle is correct in the abstract. The discipline is to be suspicious of one's own structural recommendations specifically — empirical claims have higher reliability than organizational recommendations because empirical claims are grounded in queries against canonical data, while organizational recommendations are grounded in plausible inference about what serves clarity.

This is a sub-pattern under §2 (meta-claim verification) — the meta-claim is "this principle applies here" rather than "this fact is true." Same epistemic structure, same defense.

---

## §6 Commit messages are not canonical result layers

### Principle

Commit messages are development artifacts that document work-in-progress state. They are not the canonical result layer that downstream consumers cite. When a closeout, sign-off, or other published artifact reports findings derived from work documented in commits, the closeout is the canonical layer; the commit messages are supporting history. Discrepancies between commit-message characterizations and closeout claims should be resolved by silent correction in the closeout, not by erratum-style acknowledgment of the commit-message version.

### Trigger context

This discipline was codified during the PHASE2C_6 closeout drafting. The PHASE2C_6.4 commit message (commit `d6f481a`) named 3 candidates in the "near-miss cluster" (positive holdout Sharpe but failed only on trades<5). Pre-§3 empirical verification against the canonical CSV showed the strict criterion was satisfied by 4 candidates, not 3 — the missed candidate was `e12477c9`.

The reviewer-divergence question was whether to acknowledge the discrepancy explicitly in the closeout (Phase 2C erratum-style footnote) or correct silently. The structural distinction that resolved the divergence:

- **The Phase 2C erratum** acknowledged corrections to claims in `PHASE2C_5_PHASE1_RESULTS.md`, a published closeout that downstream consumers cite. The acknowledgment served a real audit-trail purpose because the original published numbers were now known to be incorrect.
- **The PHASE2C_6.4 commit message** is a development artifact during the work, not a published result. No downstream consumer cites the commit message as load-bearing input. The closeout (`PHASE2C_6_EVALUATION_GATE_RESULTS.md`) is the first authoritative reference point for these results.

Treating commit messages as canonical layers requiring erratum-style acknowledgment would conflate two structurally different artifact types.

### Application checklist

When a closeout or sign-off documents work also captured in commit messages, and a discrepancy is found between commit-message characterizations and the empirically-verified content:

1. **Is the commit message a published result layer?** Test: do downstream consumers cite the commit message as load-bearing input? If yes, treat as canonical. If no, treat as development artifact.
2. **Is the closeout the first authoritative reference for the work?** If yes, the closeout's verified content is canonical; the commit message is supporting history.
3. **Would acknowledgment serve a future reader?** If a future reader could be misled by the commit-message characterization, brief acknowledgment may be warranted. If the closeout supersedes the commit message in any reader's natural reading order, acknowledgment is process-narration.
4. **Default: silent correction in the canonical layer.** Commits are immutable history; the closeout is the authoritative present.

### Failure-mode signal

Watch for "we should acknowledge this discrepancy" reasoning when the discrepancy is between a development artifact and a not-yet-published authoritative artifact. The acknowledgment-discipline pattern (from the corrected-engine arc's erratum work) only applies when the prior characterization is itself a published result layer. Generalizing the pattern to all discrepancies dilutes the discipline by treating every history change as requiring meta-commentary.

The complementary failure mode is silent correction of actual published-result discrepancies. If a prior closeout cited a number and the current closeout's empirical query produces a different number, that's an erratum case, not a silent-correction case.

---

## §7 Asymmetric confidence reporting on multi-sample claims

### Principle

When a finding is supported by multiple sub-samples of different sizes, calibrate the claim's strength to the smallest supporting sample, not the strongest. Smoothing to a uniform claim across asymmetric sample sizes either over-claims (reporting the strong-sample confidence on the weak-sample sub-claim) or under-claims (reporting the weak-sample caveat on the strong-sample sub-claim). Per-sub-claim calibration preserves epistemic precision.

### Trigger context

This discipline was codified during the PHASE2C_6 closeout's §8 by-theme interpretation drafting. The "within-theme inversion" finding — the corrected WF gate's anti-selection observable within a single theme — was supported by two themes:

- **volume_divergence:** primary 0/12, audit-only 4/28. The n=12 primary universe is large enough to support a within-theme anti-selection claim with limited small-sample caveat.
- **momentum:** primary 0/3, audit-only 3/36. The n=3 primary universe is small enough that the 0/3 outcome is consistent with both "anti-selection" and "by-chance absence of regime-robust candidates."

Reporting both findings with the same confidence ("the WF gate anti-selects within these themes") would over-claim for momentum. Reporting both with the same caveat ("with small-sample caveats") would under-claim for volume_divergence. The §8 draft instead reported each sub-claim with its empirically-grounded confidence level: volume_divergence as a within-theme anti-selection claim with reduced caveat; momentum as a within-theme inversion direction-consistent-with-§5 but with the strength bounded by the small primary n.

### Application checklist

When drafting findings that span multiple sub-samples of different sizes:

1. **Identify each sub-claim's supporting sample size.** Walk through each component finding and name the n that supports it.
2. **Calibrate confidence per sub-claim.** Stronger samples support stronger claims; weaker samples warrant explicit small-sample caveats. Resist the urge to smooth to uniform confidence.
3. **Distinguish direction-consistent from strength-supporting evidence.** Small-sample evidence may be direction-consistent with a finding (the sign of the effect) without supporting the magnitude claim. Report what the sample supports, not what it suggests.
4. **Use explicit asymmetric language.** Phrases like "with reduced caveat" or "the direction is consistent but the strength is limited by n=X" communicate the calibration directly. Avoid generic "with caveats" that obscures which caveats apply where.

### Failure-mode signal

Watch for findings stated with uniform confidence across asymmetric samples. If two sub-findings have n=3 and n=30, and both are reported with identical confidence language, one is mis-calibrated. The discipline is to make the asymmetry visible in the prose, not smooth it away.

The complementary failure mode is over-asymmetry — adding so many caveats to small-sample claims that they're effectively retracted. Direction-consistent small-sample evidence is real evidence; the discipline is to report what it supports (direction) without claiming what it doesn't (magnitude).


---

## §8 How to apply these principles

The fourteen specific principles plus §1's two-axis strengthening
plus §11's two-item operational refinement are mutually reinforcing.
§1 (empirical verification, with WHEN/HOW axes — recompute-before-prose
at framing-summary stage and V7 grep-able citation operational
specificity) prevents specific factual defects in artifacts. §2
(meta-claim verification) prevents the same defect class one layer
up, in claims about the verification itself. §3 (regime-aware
calibration) is a specific application of §1 to calibration decisions.
§4 (scale-step discipline) prevents over-claiming from intermediate
evidence. §5 (precondition verification for structural principles) is
a sub-pattern of §2 specific to structural and organizational
recommendations. §6 (commit messages not canonical) prevents
over-applying acknowledgment discipline. §7 (asymmetric confidence
on multi-sample claims) prevents smoothing-induced over- or under-
claiming. §9 (Path-2 outline-first drafting) prevents evidence-section
drift relative to load-bearing-section framing in multi-direction
closeouts. §10 (anti-pre-naming as standing discipline) prevents
implicit commitments to scoping decisions not yet made. §11
(closeout-assembly checklist as running drafting-cycle pattern, with
PHASE2C_8.1 operational refinements adding per-section cross-reference
grep and register-cardinality verification) preserves drafting-cycle
forward momentum without re-opening sealed sections for non-blocking
fixes and catches cross-section + register-cardinality drift at
full-assembly stage. §12 (internal verification and adversarial
review as complementary defect-class coverage) covers the
structurally distinct defect surface that internal verification
cannot reach by construction. §13 (parallel-implementation
verification for canonical findings) preserves epistemic distance
between production code path and verification code path through
permanent in-repo independent-implementation gates. §14 (bidirectional
dual-reviewer register-precision) operates as the structural quality
check at high-load drafting cycles where both reviewer overlays
must fire because each covers a defect axis the other does not.
§15 (anchor-list empirical-verification discipline) catches
advisor-supplied anchor inaccuracy at the receiving cycle's pre-
drafting stage, before incorrect anchors harden into prose.

§12 is structurally distinct from §1-§11 + §13-§15. §1-§11 + §13-§15
codify specific-defect-prevention disciplines — each principle
prevents a specific class of defect at a specific operational moment
(pre-drafting / drafting / framing / section-seal / assembly /
post-assembly). §12 is a **meta-discipline** that combines two
protocols (V1-V7 internal verification + adversarial review) into
complementary coverage of the full defect surface. The distinction
matters operationally: §12 doesn't replace V1-V7 or substitute for
any §1-§11 + §13-§15 principle; it composes with them. A high-load
closeout commit applies §1-§11 + §13-§15 individually + §12 as the
meta-protocol that ensures aggregate coverage.

§14 carries a sub-meta-discipline character that distinguishes it
within the §1-§11 + §13-§15 group. Where §1-§11 + §13 + §15 each
address a specific defect class at a specific operational moment, §14
addresses the protocol structure of register-precision verification
itself — bidirectional dual-reviewer firing as opposed to directive
arbitration. The distinction is structurally similar to §12's meta-
discipline character but operates at the register-precision verification
layer rather than the V1-V7-plus-adversarial composition layer. §14
composes with §12: §12's three-protocol composition (V1-V7 + dual-
reviewer + adversarial review) inherits §14's bidirectional firing
discipline at the dual-reviewer layer.

In practice:

- **Before writing dispatch text:** apply §3 to any expected-
  behavior bands; apply §1 to any specific facts (counts,
  identities, paths) cited as input.
- **Before drafting closeout sections (pre-drafting stage):** apply
  §15 — verify advisor-supplied numerical or structural anchors
  empirically against canonical artifacts at receiving cycle, before
  drafting initiates. Apply §9 — does the load-bearing interpretive
  section have multi-direction findings? If yes, draft it first as
  a standalone cycle.
- **In §9-style follow-up-question sections:** apply §10 — body
  prose uses generic "follow-up scoping" phrasing, not specific
  arc names; illustrative examples avoid pre-characterization.
- **During data-density section drafting:** apply §1's WHEN axis —
  recompute canonical numerical claims at framing-summary stage,
  before prose drafts. Apply §1's HOW axis — every numerical claim
  carries a grep-able back-pointer to a canonical artifact field.
- **Before committing prose artifacts:** apply §1 to every specific
  claim in the prose; apply §7 to any finding that spans multiple
  sub-samples.
- **Before drawing closeout-tier conclusions from intermediate
  evidence:** apply §4 — does this sample size support the scope
  of claim being made?
- **During section-drafting cycles in multi-cycle closeouts:**
  apply §11 — non-blocking fixes accumulate in a running closeout-
  assembly checklist; do not re-open sealed sections mid-cycle for
  small cross-reference fixes. Distinguish tracked fixes (mechanical,
  batched at assembly) from blocking defects (re-open framing,
  return to drafting cycle).
- **During dual-reviewer adjudication (register-precision register):**
  apply §14 — both reviewers' register-precision overlays must fire
  before section-seal; single-reviewer clean is partial signal, not
  complete. Treat each overlay's catch as canonical in its defect
  class; do not aggregate or merge.
- **During dual-reviewer adjudication (non-register decisions):**
  apply §2 to confident meta-claims about process state ("verified,"
  "pinned," "low-value"); apply §5 to structural and organizational
  recommendations from any source (including from oneself).
- **When discrepancies surface between development artifacts and
  authoritative artifacts:** apply §6 — is the development artifact
  a published result layer, or supporting history?
- **At closeout-assembly stage:** apply §11's at-assembly verification
  + §11's per-section cross-reference grep + §11's register-cardinality
  verification + §10's at-assembly meta-attestation grep + §1's
  recompute-before-prose audit + the closeout-assembly checklist
  deterministic application.
- **For canonical findings at high-load closeout register:** apply
  §13 — at least one permanent in-repo parallel-implementation
  verification gate must exist for canonical findings. Stdlib-only
  or minimum-dependency code path; byte-identical reproduction across
  layers required.
- **Before merging closeout commits:** apply §12 — run mandatory
  adversarial review (Codex or equivalent); fold findings as a
  separate review-response commit; re-run V1-V7 post-fold.
  Adversarial review is structural gate, not discretionary
  overhead; cost is bounded; catch rate is non-zero across
  precedent arcs.
- **Final pass on canonical artifacts:** "What's the highest-
  leverage unverified claim in this artifact?" — verify it.

These principles are not a checklist that completes during a single
work cycle; they are standing discipline that applies to every cycle.
New work cycles inherit them.

The discipline portfolio's per-closeout-type cost varies by closeout
load. **High-load closeouts** (load-bearing finding sections,
numerical claims at body-prose resolution, cross-section
adjudication register) apply the full discipline portfolio: §1-§7
specific-defect prevention + §9-§11 drafting/assembly disciplines +
§12 mandatory adversarial-review meta-protocol + §13 parallel-
implementation verification + §14 bidirectional dual-reviewer
register-precision + §15 anchor-list empirical-verification
discipline. **Administrative documents** (scoping decisions, plans,
dispatch texts with no empirical claims and no load-bearing findings)
apply only the directly-applicable subset: §1 + §2 + §6 typically;
§9-§15 do not apply by their respective conditional boundaries. The
conditional-boundary structure of §9-§15 prevents the discipline
portfolio from generating overhead disproportionate to defect-
surface coverage.

§9-§15 surface conditional boundaries explicitly because PHASE2C_7.1's
and PHASE2C_8.1's drafting cycles surfaced the boundary distinctions
empirically. §1-§7 do not carry explicit conditional boundaries in
their existing prose; this is not a claim that §1-§7 are universal-
application principles. PHASE2C_6.6's drafting cycles did not surface
the need to name implicit conditional boundaries for §1-§7 (e.g.,
§6's commit-messages-not-canonical principle has an implicit
boundary — applies to projects with closeout documents as canonical
result layer). The cost-portfolio observation is structural across
the full portfolio, not a generation-distinguishing claim about
pre-2026 vs post-2026 principle drafting.

### When new lessons surface

When a future work cycle surfaces a discipline lesson that doesn't
fit any existing section, append it as §13, §14, etc. The structure
(Principle / Trigger context / Application checklist / Failure-mode
signal) is the canonical shape for new lesson entries. Keep the
document a flat list of standing principles, not a narrative —
future readers should be able to scan section headers and read just
the relevant principle without reconstructing context.

When a future work cycle strengthens an existing principle rather
than introducing a new one, absorb the strengthening inside the
existing section's 4-part structure — Trigger context expanded
with new evidence, Application checklist gaining new items,
Failure-mode signal extended — rather than promoting the
strengthening to a new section. Sub-structure within an existing
section is acceptable when the strengthening is operational
refinement rather than new principle. **Empirical case studies
(strengthening):** §1's WHEN/HOW operational refinements added
during the PHASE2C_7.1 update absorbed inside §1's existing 4-part
structure rather than becoming standalone sections. §11's per-section
cross-reference grep + register-cardinality verification operational
refinements added during the PHASE2C_8.1 update absorbed inside §11's
existing 4-part structure for the same structural reason — both are
operational refinements of §11's running closeout-assembly checklist
discipline, not distinct standing principles. **Empirical case
studies (new sections):** §9 / §10 / §11 / §12 added during the
PHASE2C_7.1 update + §13 / §14 / §15 added during the PHASE2C_8.1
update each became new sections per existing convention because each
codified a distinct standing principle not derivable from prior
sections.

When updating §8's "How to apply" synthesis after adding a new
section or strengthening an existing one, integrate the new
content into the practice list rather than appending it to the
end. The synthesis should reflect the current state of standing
discipline, not the chronological order in which lessons were
codified.

### Cross-reference register: arc identifiers to canonical documents

The arc identifiers cited throughout §1-§15 trace to canonical
project documents at the following locations:

- **PHASE2C_5** (Phase 2C Phase 1 walk-forward closeout): `docs/closeout/PHASE2C_5_PHASE1_RESULTS.md` + corrected-engine erratum at `docs/closeout/PHASE2C_5_PHASE1_RESULTS_ERRATUM.md`
- **PHASE2C_6** (Phase 2C single-regime evaluation gate): `docs/closeout/PHASE2C_6_EVALUATION_GATE_RESULTS.md` (PHASE2C_6.6 final closeout commit; PHASE2C_6.7 Codex review-response commit)
- **PHASE2C_7.0** (Phase 2C scoping decision): `docs/phase2c/PHASE2C_7_SCOPING_DECISION.md`
- **PHASE2C_7.1** (Phase 2C multi-regime evaluation gate): `docs/closeout/PHASE2C_7_1_RESULTS.md` + plan at `docs/phase2c/PHASE2C_7_1_PLAN.md` (PHASE2C_7.1.7 Codex review-response commit; tag `phase2c-7-1-multi-regime-v1`)
- **PHASE2C_8.0** (Phase 2C extended-evaluation scoping decision): `docs/phase2c/PHASE2C_8_SCOPING_DECISION.md` (Q-B1 selection over Q-B2/Q-B3.a/Q-B3.b/Q-B4; established the n=4 baseline composition + Option A engine-version invariance + in-sample caveat (Concern A) framework)
- **PHASE2C_8.1** (Phase 2C multi-regime evaluation gate, extended): `docs/closeout/PHASE2C_8_1_RESULTS.md` + plan at `docs/phase2c/PHASE2C_8_1_PLAN.md` (closeout commit at `69e9af9`; tag `phase2c-8-1-multi-regime-extended-v1`; permanent in-repo recompute gate at `tests/test_phase2c_8_1_independent_recompute.py`)
- **Corrected WF Engine Project Arc** (engine fix establishing wf-corrected lineage): `docs/closeout/CORRECTED_WF_ENGINE_SIGNOFF.md` + lineage discipline at `backtest/wf_lineage.py` (tag `wf-corrected-v1`)
- **PHASE1B_WF Corrected Baseline Supplement** (baseline re-validation under corrected engine): `docs/closeout/PHASE1B_WF_CORRECTED_BASELINE_SUPPLEMENT.md`
- **PHASE2A signoff**: `docs/closeout/PHASE2A_SIGNOFF.md`

Future arcs append entries to this register as they ship. The
register makes arc-identifier-to-document mapping grep-able for
future readers cross-referencing METHODOLOGY_NOTES principles back
to specific closeout evidence.

---

## §9 Path-2 outline-first drafting for load-bearing interpretive sections

### Principle

When a closeout's load-bearing interpretive section carries
multi-direction findings — characterized by **any of** multiple
internally-consistent readings, multi-regime adjudications, or
multi-cut estimand distinctions (any one condition suffices; the
three are disjunctive criteria) — draft the load-bearing
interpretive section FIRST as a standalone cycle, before evidence-
and-bounds sections that depend on its framing. Path-2 outline-first lets the load-bearing interpretive section
stabilize its framing before evidence sections that read forward
from it commit to specific framings of their own. Drafting evidence
sections ahead of headline framing introduces pre-commit risk: each
evidence section commits to a framing that may not align with the
eventual headline.

Single-direction findings (single regime, single direction, single
estimand) do not structurally require Path-2 outline-first. The
canonical drafting cycle (§3 input universe → §4 gate spec → §5
headline → §6 bounds → §7 cohorts → §8 by-partition → §9 forward-
pointers) drafts cleanly when §5's framing is stable as soon as §4
seals. Multi-direction findings break this assumption — §5's framing
may have multiple internally-consistent shapes that depend on
adjudication across the full evidence base, not just the gate spec.

### Trigger context

This discipline was codified during the PHASE2C_7.1 multi-regime
evaluation gate arc (April 2026). PHASE2C_7.1's §5 carried three §5
cuts:

- **Within-2024 cut:** primary 22/44 = 50.0% > audit-only 65/154 =
  42.2%, an inversion relative to PHASE2C_6's 2022 anti-selection
  direction.
- **Cross-regime intersection cut:** audit-only 8/154 = 5.2% >
  primary 0/44 = 0.0%, mirroring the 2022 anti-selection direction.
- **PHASE2C_6 carry-forward cut:** audit-only 8/12 = 66.7% > primary
  0/1, asymmetric carry-forward where the sole 2022 primary survivor
  failed 2024.

The headline ("selection power is regime-dependent and not robustly
preserved across the two tested regimes") had to read forward
consistently across §3 (input universe), §4 (regime configuration +
Path B failure-mode taxonomy), §6 (bounded claims), §7 (cohort
enumeration), §8 (by-theme), §9 (mechanism implications). Drafting
§3-§9 ahead of §5 framing would have forced re-litigation of the
three-cut adjudication across each section: §7 cohort definitions
depend on §5's adjudication of which cut anchors cohort membership;
§8 by-theme stratification depends on §5's framing for whether
within-theme inversions read as headline-supportive or headline-
qualifying; §9 mechanism implications depend on §5's bounded
conclusion register.

PHASE2C_7.1 drafted §5 first as a standalone cycle. The §5 framing
sealed the three-cut adjudication ("regime-dependent and not robustly
preserved across the two tested regimes"); §3 + §4 + §6 + §7 + §8 +
§9 then drafted as evidence-and-bounds sections that read forward
from §5's sealed framing without re-litigating the adjudication.

PHASE2C_6.6 by contrast was single-regime with single-direction
headline (anti-selection against 2022, audit-only > primary within
the 2022 batch); §5 framing was simpler, the canonical drafting
cycle worked cleanly, and Path-2 outline-first wasn't structurally
necessary. PHASE2C_6.6 drafted §3 → §4 → §5 → §6 → §7 → §8 → §9 in
sequence; each section's framing read forward from the prior
section's seal without revisiting the headline.

The discipline pattern: multi-direction findings warrant Path-2
outline-first; single-direction findings draft cleanly under the
canonical cycle. The decision is structural — based on whether the
load-bearing interpretive section carries multi-direction findings — not
based on closeout size or section count.

### Application checklist

Before beginning closeout drafting cycles, walk through the following
questions:

1. **Load-bearing-section classification:** Does the closeout's
   load-bearing interpretive section (typically §5) carry **any of
   the following** multi-direction findings — multiple internally-
   consistent readings, multi-regime adjudications, or multi-cut
   estimand distinctions? Any one suffices to warrant Path-2
   outline-first; conditions are disjunctive, not conjunctive.
2. **Drafting order under Path-2:** If Path-2 applies, draft the
   load-bearing interpretive section first as a standalone cycle.
   Evidence-and-bounds sections (input universe, gate spec, bounded
   claims, cohort enumeration, by-partition, mechanism implications)
   draft after the load-bearing section's framing seals. Do not
   draft evidence sections in parallel with the load-bearing section
   under Path-2.
3. **Standalone cycle scope:** The Path-2 standalone cycle drafts the
   load-bearing section against artifact data + framing summary
   alone, not against draft evidence sections. The evidence sections
   then read forward from the sealed framing without re-litigating
   the adjudication.
4. **Section-seal verification:** Before evidence-and-bounds sections
   begin drafting, verify the load-bearing section's framing is
   sealed (seal directive issued, V1-V7 forbidden-phrase scan
   applied, anti-pre-naming compliance checked). Drafting evidence
   sections against an unsealed load-bearing section re-introduces
   pre-commit risk.

### Failure-mode signal

Watch for evidence-section drafts that carry framing claims at odds
with the eventual load-bearing section's framing. Symptoms (each
empirically anchored to a real PHASE2C_7.1 drafting-cycle moment):

- **Interpretive drift in §3/§4** — §3 or §4 prose making
  interpretive claims the §5 framing doesn't support ("the gate
  failed in 2024" vs §5's "selection power is regime-dependent").
  The evidence section framed before the load-bearing section
  sealed. Counterfactual anchor: under canonical drafting cycle
  ordering, PHASE2C_7.1 §4 would have drafted the Path B failure-
  mode taxonomy before §5 sealed the three-cut adjudication; §4's
  taxonomy (mirror / invert / null) read forward cleanly only
  because §5 sealed first.
- **Cohort-definition misalignment with §7** — §7 cohort enumeration
  adopting cohort-definition criteria that don't align with the §5
  adjudication (e.g., defining cohort (a) as "passed 2022" when §5
  adjudicates cross-regime intersection as a distinct estimand from
  within-regime). Cohort definitions derive from §5's adjudication,
  not from the gate spec alone. Empirical anchor: PHASE2C_7.1's
  cohort (a) was defined as "passed both 2022 AND
  validation_2024" specifically because §5 sealed cross-regime
  intersection as a distinct estimand; defining cohort (a) on either
  regime alone would have collapsed the cross-regime cut.
- **Within-partition framing contradiction in §8** — §8 by-partition
  prose making within-partition framing claims that contradict §5's
  bounded conclusion (e.g., "primary partition shows WF gate works
  in 2024" when §5 adjudicates the within-2024 cut as one of three
  estimands, not as a standalone gate verdict). Empirical anchor:
  PHASE2C_7.1 §8 by-theme analysis stratified theme-level
  inversions as supportive vs qualifying evidence relative to §5's
  three-cut framing; without §5 sealed, §8's stratification register
  would have defaulted to single-cut interpretation.
- **Mechanism pre-naming in §9** — §9 forward-pointer prose pre-
  naming mechanism conclusions that §5's bounded conclusion
  explicitly leaves undetermined ("the mechanism is regime-mismatch"
  when §5's bounded conclusion names mechanism adjudication as
  undetermined within the batch). Empirical anchor: PHASE2C_7.1 §9
  Q-B1 named "additional regimes" generically because §5's bounded
  conclusion explicitly left mechanism adjudication undetermined;
  §9 prose drafted under the sealed §5 register without pre-naming
  regime-mismatch as the operating mechanism.

In closeouts with multi-direction findings, watch for first-pass
evidence-section drafts that hedge or under-commit. Evidence sections
cannot commit without load-bearing-section framing; if first-pass
drafts read tentative or forward-pointing in places they shouldn't,
the load-bearing section may not have sealed yet — the drafting
cycle needs to seal §5 before §3-§9 continue.

The PHASE2C_6.6 contrast is informative: with single-direction
findings, evidence-section drafts read forward cleanly from gate
spec to cohort enumeration to by-partition to forward-pointers
without revisiting load-bearing-section framing. If a closeout's evidence-section
drafts carry this clean forward-read pattern under canonical
ordering, Path-2 outline-first wasn't necessary. If they carry
hedging, re-litigation, or framing drift, Path-2 outline-first
applies and the cycle should reset to draft the headline first.

---

## §10 Anti-pre-naming as standing discipline

### Principle

Forward-pointers in closeout sections (especially §9-style follow-up-
question sections) reference future work generically — "follow-up
scoping," "a follow-up arc," "subsequent arc closeouts" — and do
NOT pre-name specific future arc identifiers ("PHASE2C_8" /
"PHASE3" / "Q-B5+ scoping") or pre-characterize future-arc subject
matter ("the bull-regime evaluation arc" / "the deployment-readiness
phase"). Pre-naming creates implicit commitments to specific scoping
decisions that have not been made; it constrains future arc design
before the next scoping cycle begins.

The conditional boundary is structural: anti-pre-naming applies to
**forward-pointing prose** — sections that reference work yet to
happen, future arcs, or subsequent scoping decisions. It does **not**
apply to backward-referencing prose — sections that legitimately
name shipped arcs (PHASE2C_5, PHASE2C_6, PHASE2C_7.1) as canonical
references in the project's discipline history. Backward references
to shipped artifacts are factual citations, not pre-commitments.

Meta-attestations about forward-pointer hygiene (e.g., a §10 grep
claim "zero PHASE2C_8 references in body prose") may quote the
prohibited phrase as the negative claim itself; that quotation is
not a pre-naming violation but a verification artifact.

### Trigger context

This discipline was codified across the PHASE2C_7.0 → PHASE2C_7.1 →
PHASE2C_7.1.7 arc sequence (April 2026). The pattern strengthened
incrementally through three precedent arcs:

**PHASE2C_6.6 (precedent baseline, March-April 2026 boundary).** §9
forward-pointers used "PHASE2C_7+ scoping" phrasing — mild pre-
naming via the "+" suffix. The "+" suffix gestured at multiple
possible follow-up arcs but anchored on PHASE2C_7 specifically; the
naming committed implicitly to PHASE2C_7 as the next-arc identifier
before scoping had decided so.

**PHASE2C_7.0 (scoping decision, April 2026).** The PHASE2C_7.0
scoping decision document tightened forward-pointer phrasing to
generic register: forward-pointers reference "follow-up scoping"
without pre-naming the specific future arc. This was the first
arc to apply anti-pre-naming explicitly as a discipline directive.

**PHASE2C_7.1 (multi-regime closeout, April 2026).** §9 carried
the discipline forward consistently. The closeout's body-prose grep
returned zero "PHASE2C_8" references after assembly — but Codex
adversarial review (`bznjgs9rz`) caught one residual at §7 closing
line 870 (`PHASE2C_8+ scoping`); the fix landed at PHASE2C_7.1.7
commit. Post-fold body-prose grep confirmed zero non-meta references.

A second PHASE2C_7.1 instance: §9 subsection 9.B Q-B1 originally
named specific historical regimes ("2018 bear / 2020 COVID drawdown
/ 2021 bull peak") as illustrative examples; both reviewers
(ChatGPT + Claude advisor) caught the pre-naming + pre-
characterization risk simultaneously, and the directive replaced
with "additional historical regimes selected by a future scoping
document." This instance demonstrates that anti-pre-naming applies
not only to arc identifiers but also to subject-matter pre-
characterization (regime-character-typing in illustrative examples).

The discipline pattern strengthens with each arc:

- **PHASE2C_6.6:** mild pre-naming (`PHASE2C_7+ scoping`)
- **PHASE2C_7.0:** generic-phrasing carryforward established
- **PHASE2C_7.1:** generic-phrasing maintained through closeout
  drafting; one residual caught at adversarial review; fix landed
- **§10 surfacing:** anti-pre-naming as standing discipline,
  explicit for future arcs rather than relying on per-arc
  rediscovery

The §10 codification makes the discipline operational beyond the
PHASE2C_7.x arc sequence. Future closeouts inherit anti-pre-naming
as standing discipline rather than re-deriving it during each
drafting cycle.

### Application checklist

Before sealing any section that contains forward-pointers (§9-style
follow-up-question sections, §10 methodology forward-pointers,
closing-paragraph forward references):

1. **Scope classification:** Is the section forward-pointing
   (referencing work yet to happen) or backward-referencing
   (citing shipped arcs)? Anti-pre-naming applies to forward-
   pointing prose only; backward references to shipped arcs
   (PHASE2C_5 / PHASE2C_6 / PHASE2C_7.1) are factual citations
   and remain as-is.
2. **Body-prose grep (forward-pointing sections):** For sections
   classified as forward-pointing, does body-prose grep return
   zero specific arc identifiers (e.g., `grep -E
   'PHASE2C_[0-9]+|PHASE3|PHASE4'`)? If any specific identifiers
   surface in forward-pointer context, replace with generic
   "follow-up scoping" / "a follow-up arc" / "subsequent arc
   closeouts" / "a subsequent scoping document" phrasing.
3. **Pre-characterization risk in illustrative examples:** When
   forward-pointer subsections name illustrative examples (e.g.,
   "additional regimes like X, Y, Z"), do those examples carry
   pre-characterization risk — regime-character-typing, mechanism-
   typing, scope-typing? If yes, replace with generic phrasing
   ("additional regimes selected by a future scoping document"
   / "additional cohorts identified by follow-up scoping" /
   "additional questions surfaced in subsequent scoping cycles").
4. **Meta-attestation verification (at-assembly, not at-section-
   seal):** Items 1-3 above are during-drafting prevention disciplines
   — applied as forward-pointer prose drafts to prevent pre-naming
   from entering the closeout in the first place. Item 4 is a
   structurally distinct operational moment: at-assembly verification
   that meta-claims about anti-pre-naming compliance are accurate
   across the assembled document. When a section asserts a meta-
   claim about forward-pointer hygiene (e.g., "§10 attests body-
   prose contains zero PHASE2C_8 references" / "no specific arc
   identifiers in §9 prose"), grep the assembled document at full-
   closeout-assembly to verify the meta-claim. Residual references
   missed during drafting cycles falsify the meta-claim if not
   caught at assembly. The PHASE2C_7.1.7 precedent: §10 attested
   "zero PHASE2C_8 references" — true within §10's prose at section-
   seal — but §7 closing line 870 carried one residual that adversarial
   review caught. Assembly-time verification catches this defect
   class structurally; section-seal-time verification does not, by
   construction.

### Failure-mode signal

Watch for forward-pointers that read specifically rather than
generically:

- "PHASE2C_8 will address X" vs "follow-up scoping will address X"
- "the next arc evaluates Y" vs "a subsequent arc evaluates Y"
- "Q-B5+ scoping" vs "follow-up question Q-Bk for some k > 4"

Watch for illustrative examples that carry mechanism, character, or
scope typing alongside pre-naming:

- "the 2018 bear regime" pre-characterizes the regime as bear
- "the post-halving period" pre-characterizes the period by macro
  event
- "the deployment-readiness arc" pre-characterizes follow-up scope
  as deployment-promotion-oriented

Generic phrasing avoids both pre-naming and pre-characterization
risk simultaneously: "additional historical regimes selected by a
future scoping document" / "subsequent arc closeouts as scoped" /
"follow-up arc design decisions."

Watch for meta-attestations that pass at section-seal but fail at
assembly. The PHASE2C_7.1 precedent demonstrates this defect
class: §10's grep claim was true within §10's prose at section-
seal, but not true across the full closeout body at assembly. The
gap surfaces only when meta-attestation is verified against the
assembled document, not against the section in isolation.

In dispatch text and reviewer adjudication, watch for arguments
that "specific identifiers are clearer" or "generic phrasing is
vague." The anti-pre-naming discipline trades a small clarity
cost (generic phrasing requires the reader to navigate to scoping
documents for specifics) for a structural benefit (forward-pointers
do not constrain future scoping decisions before they're made).
The clarity cost is bounded; the structural benefit compounds
across arcs.

---

## §11 Closeout-assembly checklist as running drafting-cycle pattern

### Principle

When a closeout drafts across multiple section-drafting cycles, non-
blocking fixes that surface mid-cycle accumulate in a running
**closeout-assembly checklist** rather than triggering immediate
re-opening of sealed sections. The unified closeout-assembly stage
applies all tracked fixes deterministically. Tracked fixes are
operational completion items, not unresolved defects deferred —
each has a known location and a known shape; the assembly
application is mechanical. The pattern lets drafting cycles
preserve forward momentum without re-opening sealed sections for
small cross-reference fixes that accumulate naturally across
cycles.

The conditional boundary is structural: §11 applies to closeouts
with **multiple drafting cycles** (typically: §-by-§ section-drafting
across 8-11 sections). It does NOT apply to single-session closeouts
or administrative documents (scoping decisions, plans, dispatch
texts) where no fix accumulation occurs and assembly is co-extensive
with single-pass drafting. The discipline is operationally bounded
to multi-cycle drafting contexts.

A tracked fix is distinct from a blocking defect. **Tracked fix:**
a non-blocking item with a known location and known shape that does
not require re-litigating sealed framing or empirical claims (e.g.,
a cross-reference target update, a stripped drafting-notes appendix,
a parenthetical inline caveat addition, a per-row table population
from already-existing per-candidate JSON files). **Blocking defect:**
an item that requires re-opening sealed sections because the fix
changes empirical content, framing register, or canonical claims
(e.g., a discovered numerical inaccuracy, a forbidden-phrase scan
violation, a structural register inconsistency). Blocking defects
are not tracked-checklist material — they require immediate cycle
return to the affected section.

### Trigger context

This pattern was codified across the PHASE2C_6.6 → PHASE2C_7.1 arc
sequence (April 2026). The pattern strengthened from implicit ad-hoc
treatment to operational running checklist:

**PHASE2C_6.6 (implicit treatment, March-April 2026 boundary).**
Mid-cycle fixes surfaced during drafting (e.g., minor cross-reference
adjustments, assembly-stage table populations, drafting-notes
stripping) and got mixed mid-cycle and at assembly-time ad-hoc.
There was no explicit running checklist; reviewer adjudication
addressed each fix as it surfaced, in either re-opening-the-section
mode or batching-for-assembly mode depending on cycle context. The
pattern worked but lacked explicit operational structure; the
batch-for-assembly intuition existed but wasn't codified.

**PHASE2C_7.1 (operational running checklist, April 2026).** Six
fixes accumulated explicitly across §3-§9 drafting cycles:

- §5 line 29 §3 → §4 cross-reference fix (the §5 prose initially
  named §3 as the Path B failure-mode taxonomy section; §4 is the
  actual section)
- All section drafting-notes appendices stripped uniformly at
  assembly (each draft included a drafting-notes appendix; the
  canonical closeout strips them)
- §7 per-candidate row population from per-candidate JSON files
  (§7 cohort tables had placeholder rows during drafting; assembly
  populates from `audit_2024_v1/<hash>/holdout_summary.json`)
- §7 cohort (b) full 22-row table population at assembly (cohort
  (b) had 22 candidates; only top-10 rows populated during §7
  drafting; assembly populates remaining 12)
- §7 cohort population scripts produce byte-identical output across
  runs (the population script's determinism verified at assembly,
  ensuring closeout's tables don't drift between reviewer copies
  and committed canonical)
- §5 line 56-57 audit-only "two-thirds" framing parenthetical
  inline caveat addition (the parenthetical "(n=12; magnitude
  bounded in §6)" added at assembly to preempt §5 reader confusion
  about the carry-forward rate's small-N basis)

Each fix had a specific location (file + line range or section)
and a specific shape (replace X with Y; populate from artifact;
strip per pattern). Closeout-assembly applied all six fixes
deterministically; the assembly commit produced a byte-identical
closeout md5 reproducible across runs (`6a95a13d41832254e0a5a47f983ec0b7`
for the PHASE2C_7.1 closeout assembly).

The discipline pattern's progression: PHASE2C_6.6 ad-hoc → PHASE2C_7.1
explicit running checklist with deterministic assembly-stage
application. The §11 codification makes the operational structure
explicit beyond the PHASE2C_7.1 arc; future multi-cycle closeouts
inherit the running-checklist pattern rather than re-deriving it.

**PHASE2C_8.1 (operational refinement: per-section cross-reference
grep + register-cardinality verification, April 2026).** The
running-checklist pattern operated at PHASE2C_8.1 closeout assembly
without breakdown, but two operational gaps surfaced empirically:

- **Per-section cross-reference grep gap.** Eleven cross-section
  observations (VVVV through FFFFF in the assembly checklist)
  accumulated across §3-§9 drafting cycles where a top-level
  numerical-claim grep cleared but cross-section reference drift
  remained. The pattern: a section's prose used a number that
  matched the canonical artifact, but a different section's
  reference to the same number used a different rounding or a
  different scope. Top-level grep against the canonical artifact
  cleared each section in isolation; per-section cross-reference
  grep would have caught the cross-section drift at section-seal.
- **Register-cardinality verification gap.** Codex adversarial
  review's MAJOR finding at PHASE2C_8.1 §1.4 caught register-count
  enumeration drift: §1.4's verdict-section summary said "seven
  tracked-fix register entries... plus eighth entry Q-S4-14" while
  canonical §10 had ten entries (Q-S4-15/16 emerged after §1 was
  drafted; §1.4 not retroactively updated at full-assembly). V1-V7
  internal verification cleared §1.4's prose at section-seal;
  register-cardinality cross-check between §1.4's summary and §10's
  canonical table would have caught the seven-vs-ten enumeration
  drift before commit. The defect class generalizes: any section
  that summarizes a register must match the canonical register's
  cardinality at full-assembly verification.

The PHASE2C_8.1 evidence operates as operational refinement rather
than new principle: §11's running closeout-assembly checklist is the
correct discipline, with two enrichments at the application checklist
register. Per-section cross-reference grep enriches V7's grep-able
back-pointer discipline (§1's HOW axis) at full-assembly stage, where
the cross-section register surfaces. Register-cardinality verification
enriches the assembly-stage uniform application item with a specific
sub-rule: register-summary sections must verify cardinality against
the canonical register table.

### Application checklist

During section-drafting cycles in multi-cycle closeouts, when a
non-blocking fix surfaces:

1. **Capture immediately:** Record the fix in the closeout-assembly
   checklist with a specific location (file path + line range +
   section reference) and a specific fix shape (replace X with Y;
   add inline caveat at line N; populate table rows from artifact
   path P + field F; strip drafting-notes appendix per uniform
   pattern). Capture the fix the same drafting cycle it surfaces;
   deferring capture loses location-specificity.
2. **Do not re-open sealed sections mid-cycle:** Section-seal carries
   forward momentum. Re-opening a sealed section for a small fix
   re-introduces drift risk: the section may pick up unrelated
   tweaks beyond the tracked fix's scope. Tracked fixes apply at
   unified assembly. (Exception: blocking defects — empirical
   inaccuracies, forbidden-phrase scan violations, structural
   register inconsistencies — require immediate cycle return to
   the affected section regardless of cycle position.)
3. **Assembly-stage uniform application:** At closeout-assembly stage,
   apply all tracked fixes deterministically. Verify each fix lands
   at its specified location before the assembly commit. Use
   automated assembly scripts (e.g., Python) where the fix shape
   is mechanical; manual application only when the fix requires
   judgment that scripts can't capture.
4. **Reproducibility check:** Closeout-assembly scripts (cohort
   population scripts, table generation scripts, drafting-notes
   stripping scripts) should produce byte-identical output across
   runs. Verify via md5 comparison or equivalent. Non-deterministic
   assembly introduces drift between reviewer copies and committed
   canonical, which is itself a defect class.
5. **Per-section cross-reference grep (operational refinement,
   PHASE2C_8.1):** At full-assembly verification stage, run cross-
   reference grep at per-section resolution, not just top-level
   numerical-claim grep. For each canonical numerical claim or
   register entry, verify every section that references the claim
   uses identical scope, rounding, and cardinality. The discipline
   catches cross-section reference drift that clears at top-level
   grep (each section's claim independently matches the canonical
   artifact) but fails at cross-section grep (different sections
   reference the same canonical claim at different precision or
   scope). Top-level grep is necessary but not sufficient at
   full-assembly register.
6. **Register-cardinality verification (operational refinement,
   PHASE2C_8.1):** Any section that summarizes or enumerates a
   register (e.g., a verdict-section recap of the tracked-fix
   register, a forward-signals recap of codification candidates)
   must match the canonical register table's cardinality at
   full-assembly stage. Verify each register-summary section's
   enumeration count and entry list against the canonical register
   table. The defect class is structurally distinct from per-section
   cross-reference grep: register-summaries can drift because the
   canonical register continues to grow after the summary section
   was drafted (e.g., register entries added at later drafting
   cycles after the verdict section was sealed).

### Failure-mode signal

Watch for drafting-cycle patterns that indicate the running-checklist
discipline is not operational:

- **Mid-cycle re-opening of sealed sections for small fixes.** If
  a drafting cycle pattern repeatedly returns to sealed sections to
  apply minor cross-reference adjustments or table populations, the
  cumulative re-seal cost compounds and cycle pace slows. The fixes
  belong on the running checklist for assembly-stage application,
  not in section re-openings.
- **Non-deterministic assembly output.** If closeout-assembly
  produces different byte-content across runs (e.g., different
  table row orderings, different drafting-notes-stripped boundaries,
  different placeholder text), the assembly is not reproducible.
  Reviewer copies and committed canonical will drift; subsequent
  reviewers will see a different document than the committer
  intended.
- **Tracked fixes applied at wrong moment.** If a tracked fix on
  the checklist gets applied mid-cycle (re-opening a sealed section
  for the fix) or post-commit (after the assembly commit lands), the
  discipline misfires in opposite directions. Mid-cycle application
  re-introduces drift risk; post-commit application requires a
  follow-on commit that breaks the closeout's intended single-commit
  scope.
- **Blocking defects misclassified as tracked fixes.** If an item
  on the running checklist turns out to require re-opening a sealed
  section (e.g., a numerical claim that needs framing revisitation,
  not just artifact-population), the item was misclassified.
  Reclassify and return to the affected section's drafting cycle
  immediately; do not apply at assembly.

In review cycles, watch for "should we fix this now or at assembly?"
questions. The answer is **at assembly** unless the fix is blocking
(empirical inaccuracy, forbidden-phrase violation, structural
register inconsistency, or anything that re-opens framing).
Non-blocking fixes accumulate on the running checklist; blocking
defects return to the affected section's drafting cycle.

In assembly-commit verification, watch for closeout-assembly outputs
that fail the byte-identical reproducibility check. The check is
operationally bounded (md5 comparison or equivalent) and catches
non-determinism structurally.

In full-assembly cross-reference verification, watch for the
top-level-grep-clears-per-section-grep-fails pattern. Each section's
prose can match the canonical artifact at top-level grep while
cross-section drift remains: §A says "67% / 33%" and §B says
"two-thirds / one-third" referencing the same finding, both clear
top-level grep but disagree on rounding precision. Per-section
cross-reference grep at full-assembly catches this structurally;
absent it, defects ship.

In register-summary section verification, watch for cardinality drift
between section-summary and canonical-register table. A verdict
section drafted at section N with seven register entries cited remains
correct at section-N seal; if the canonical register grows to ten
entries by full-assembly stage, the verdict section's enumeration is
stale. Register-cardinality verification at full-assembly stage
catches the drift class structurally; section-seal verification does
not because section-seal predates later register growth.

---

## §12 Internal verification and adversarial review as complementary defect-class coverage

### Principle

Internal verification protocols (V1-V7: forbidden-phrase scans,
headline-register checks, cross-section consistency, cross-reference
resolution, bounded-claims firewalls, schema-name verification,
evidence-reference back-pointers) cover a specific defect surface but
not the complete defect surface of closeout-tier prose. Adversarial
review (Codex `codex review`, or equivalent adversarial-mode review
protocol) covers a structurally distinct defect surface that internal
verification does not reach. **Neither protocol substitutes for the
other.** V1-V7 is necessary but not sufficient for high-load closeout
commits; adversarial review covers complementary defect classes that
internal verification cannot reach by construction. Both are required
for high-load closeout-tier publication.

The complementarity is operational, not just stylistic:

- **V1-V7 catches:** body-prose forbidden phrases at line resolution
  (regime-character-typing in declarative claims); numerical claim
  back-pointers (every numerical claim cites a canonical artifact
  field); cross-section ordering (referenced sections exist before
  references are made); schema-name consistency (canonical names
  match across sections); evidence-reference back-pointers (each
  cited artifact is grep-able).
- **V1-V7 does NOT catch (by construction):** parenthetical character-
  typing inside bounded clauses (forbidden phrases embedded in
  parentheticals where surrounding clause is otherwise-bounded);
  empirical cohort-claim accuracy (claims about not-evaluated-against
  scope when the cohort definition empirically contradicts the claim);
  meta-attestation consistency (a section's grep-claim is true within
  the section but false across the assembled document); numerical
  precision-overshoot in derived-arithmetic claims (sensitivity-
  arithmetic shorthand that loses precision under inspection).

Adversarial review covers the second list. The defect classes are
empirically catalogued — see Trigger context — not theoretically
enumerated. The catalogue is a living inventory of what internal
verification cannot reach by construction.

The conditional boundary is structural: §12 applies to **high-load
closeouts** — closeouts with load-bearing finding sections, numerical
claims at body-prose resolution, and cross-section adjudication
register. It does NOT apply to administrative documents (scoping
decisions, plans, dispatch texts) with no empirical claims and no
load-bearing findings; for these, the cost-vs-catch-rate ratio is
unfavorable.

### Trigger context

This principle was codified across the PHASE2C_6.7 → PHASE2C_7.1.7 arc
sequence (March-April 2026 boundary through April 2026). The empirical
pattern recurred and broadened across two arcs — the structural payoff
is single-instance-to-multi-instance, not implicit-to-operational.

**PHASE2C_6.7 (precedent: single-defect-class catch).** PHASE2C_6
evaluation gate closeout passed V1-V7 internal verification clean
before adversarial review. Codex `codex review` caught one
"bit-identical" defect — a numerical claim where the simple stated
values were technically wrong despite V1-V7 reporting clean. The fix
landed as PHASE2C_6.7 commit. The methodology lesson: V1-V7 plus
internal recompute did not catch the bit-precision defect class. A
single-arc precedent established the existence of the
complementary-coverage gap; whether the gap was a one-time incident
or a recurring pattern remained open.

**PHASE2C_7.1.7 (recurrence and broadening: four-defect-class catch).**
PHASE2C_7.1 multi-regime closeout passed V1-V7 internal verification
clean before adversarial review. Codex review (`bznjgs9rz`) caught
four defects across four distinct defect classes simultaneously:

- **Parenthetical character-typing inside bounded clauses (P2):**
  §5 bounded conclusion contained "(2022 bear, 2024 post-halving /
  ETF-approval)" — exactly the regime-character-typing pattern V1
  prohibitions block, embedded in a parenthetical within an
  otherwise-bounded clause where surrounding language ("bounded
  conclusion (asymmetric confidence)") suggested the claim was
  bounded. V1's body-line grep missed the parenthetical embedding
  because V1 scans declarative-claim register; parenthetical
  embedding is structurally outside V1's scan scope.
- **Empirical inaccuracy in cohort-evaluation claim (P2):** §7.5
  cohort (a) caveat read "have not been evaluated against
  validation, test, or forward live data" — but cohort (a)
  candidates ARE evaluated against `validation_2024` by definition
  (passed both 2022 and 2024 holdouts; cohort (a) IS the cross-
  regime intersection cohort). Catching this required cohort-
  definition awareness across §7's structure; V1-V7 doesn't cross-
  check empirical accuracy of bound claims against upstream cohort
  definitions.
- **Meta-attestation falsification by residual reference (P2):**
  §10 attested "body-prose grep returned zero PHASE2C_8 references"
  — but §7 closing line 870 contained one residual `PHASE2C_8+
  scoping`, making the meta-claim false. V1-V7 doesn't cross-check
  meta-attestations against the rest of the document at assembly
  time; section-seal verification clears each section in isolation.
- **Numerical precision-overshoot in sensitivity arithmetic (P3):**
  §8 momentum theme stated "single primary candidate flipping
  outcome would shift the gap to 67% / 33%" — actual arithmetic:
  3/3 → 2/3 = 66.7% for primary; audit_only doesn't change (still
  18/36 = 50.0%). V7's grep-able citation discipline catches
  identity claims, not derived-arithmetic claims; the precision-
  overshoot is in derived computation, not in the cited claim.

Each defect class is a different failure mode of internal
verification. V1 catches body-prose forbidden phrases at declarative
resolution; V7 catches numerical claim back-pointers at identity
resolution; neither catches semantic empirical accuracy or meta-
attestation consistency or derived-arithmetic precision.

Together, the two arcs demonstrate that the complementary-coverage
gap is structural, not incidental. PHASE2C_6.7's single-class catch
established existence; PHASE2C_7.1.7's four-class catch broadened
the catalogue. The empirical pattern: adversarial review's catch
rate is non-zero across both arcs; the defect-class surface is
structurally broader than V1-V7 covers.

### Application checklist

Before merging any closeout-tier commit:

1. **Mandatory adversarial review:** Run `codex review` (or
   equivalent adversarial review tool) on the closeout commit
   before merge/tag. Adversarial review is a structural gate, not
   a discretionary addition. The cost (one Codex invocation, ~1-2
   hour fold cycle) is small relative to the cost of shipping a
   closeout with an unfolded defect.
2. **Findings adjudication discipline:** Per the reasoned-reviewer-
   suggestion-adjudication discipline, walk through each finding
   individually — accept with reason, or push back with reason. Do
   not bulk-accept or bulk-reject. Each finding's defect class
   informs the adjudication: parenthetical character-typing is
   typically accept-with-edit; empirical cohort-claim inaccuracy is
   accept-with-edit; meta-attestation falsification is accept-with-
   verification-update; precision-overshoot is accept-with-
   recompute.
3. **Review-response commit isolation:** Fold accepted findings as
   a separate review-response commit (e.g., `PHASE2C_X.Y` →
   `PHASE2C_X.Y+1` pattern). Keep the closeout commit and the
   review-response commit distinct so the review-response audit
   trail is grep-able. Mixing the review-response with the closeout
   commit obscures the adjudication trail.
4. **Defect-class catalogue extension:** When adversarial review
   surfaces a defect class not represented in this section's
   enumeration, append it to the catalogue. The catalogue is a
   living inventory of what internal verification cannot reach by
   construction. Each new defect class establishes additional
   structural coverage gap.
5. **Re-run V1-V7 post-fold:** After folding adversarial-review
   findings, re-run V1-V7 internal verification on the post-fold
   prose. The fold should not introduce new V1-V7 violations. If
   it does, the fold itself introduced a defect that needs cycle
   return — V1-V7 + adversarial review are complementary at fold
   time too, not just at original drafting time.

### Failure-mode signal

Watch for closeout commits that pass V1-V7 internal verification
without adversarial review:

- Internal verification clearing is necessary but not sufficient —
  the four-defect-class enumeration above demonstrates the
  empirical insufficiency. A "clean V1-V7 report" is not equivalent
  to "ready to merge"; it's equivalent to "ready for adversarial
  review."
- Adversarial-review skip rationales reading "internal verification
  was thorough" or "no time for adversarial review before merge"
  misrepresent the empirical evidence. PHASE2C_6.7 + PHASE2C_7.1.7
  precedents demonstrate that adversarial review consistently
  surfaces substantive defects that internal verification missed.
  The cost (one Codex invocation, ~1-2 hour fold cycle) is bounded;
  the structural payoff (catching defects internal verification
  cannot reach by construction) compounds across arcs.

In adjudication review, watch for arguments that any of the four
catalogued defect classes is "covered by" V1-V7. They are
demonstrably not. The defect classes are catalogued empirically,
not theoretically — each cited from a specific PHASE2C_6.7 or
PHASE2C_7.1.7 finding with grep-able evidence. Pattern-matching
arguments ("V1's grep should catch this") fail because V1's grep
operates at body-line declarative-claim resolution; parenthetical
embedding, meta-attestation falsification, empirical cohort-claim
accuracy, and derived-arithmetic precision are all structurally
outside V1's scan scope.

In future closeout cycles, watch for catch-rate degradation. If
adversarial review starts surfacing zero findings consistently
across multiple high-load closeouts, two interpretations are
possible: (a) drafting cycles improved; V1-V7 + framing-summary
recompute (§1) caught defects pre-adversarial-review, or (b) the
catch is happening at a defect class not yet catalogued and the
catalogue needs extension. Either interpretation requires the
adversarial review to have actually run; skipping the review
forecloses the diagnosis.

The cost-vs-catch-rate tradeoff is empirically grounded across
the PHASE2C_6.7 + PHASE2C_7.1.7 precedents:

- **Cost:** one Codex invocation (~$0-2 depending on review scope;
  PHASE2C_7.1.7 review cost was $0 because Codex's ChatGPT-account
  auth was the protocol used); 1-2 hours of fold cycle (review +
  adjudication + fold commit + V1-V7 re-run).
- **Catch rate:** PHASE2C_6.7 = 1 substantive defect (precision-
  overshoot class); PHASE2C_7.1.7 = 4 substantive defects across 4
  distinct classes. Both arcs' V1-V7 reported clean before
  adversarial review.

The catch rate is non-zero across both arcs. Until a future
high-load closeout demonstrates zero adversarial-review catch
rate post-rigorous-V1-V7 internal-verification, the empirical
evidence supports adversarial review as mandatory for high-load
closeout commits, not as discretionary overhead.

---

## §13 Parallel-implementation verification for canonical findings

### Principle

Independent-implementation verification tests have different epistemic
standing than snapshot tests against the same code path. When a
verification mechanism re-derives a canonical claim from raw artifacts
via an independent code path — different language constructs, minimum-
dependency stdlib-only imports, different algorithm structure, no
shared module imports with the production pipeline — the verification
provides structurally distinct epistemic coverage compared to a
snapshot test that pins the same code path's output. Both have value
and neither substitutes for the other; snapshot regression tests catch
unintended output change in the production code path, while parallel-
implementation tests catch defects that the production code path
itself encodes.

For canonical findings at high-load closeout register, at least one
permanent in-repo parallel-implementation verification gate should
exist. The discipline preserves epistemic distance between the
production code path and the verification code path; if the production
code path has a defect that yields the canonical claim, a snapshot
test pins the defect rather than catching it. The parallel-
implementation gate's independent code path catches the defect class
that snapshot tests cannot reach by construction.

The conditional boundary is structural: §13 applies to **canonical
findings at high-load closeout register** — findings that ship as
load-bearing claims in committed closeout artifacts and that
downstream work consumes as authoritative. It does NOT apply to
intermediate working artifacts, exploratory analyses, or findings
without committed-closeout consumption.

### Trigger context

This principle was codified during the PHASE2C_8.1 multi-regime
evaluation gate arc closeout (April 2026). PHASE2C_8.1's verification
chain operationally instantiated the principle at three independent
layers:

- **Layer 1 (production):** `scripts/compare_multi_regime.py` with
  full integration test coverage at `tests/test_compare_multi_regime.py`
  (32 tests including loader strictness, expected-count helpers, and
  apply-multi-regime failure paths). The production pipeline produces
  the canonical comparison artifacts (`comparison.csv`,
  `comparison_summary.json`).
- **Layer 2 (one-time external):** Codex adversarial review's
  independent recomputation from source CSVs at the `018d876`
  resolution cycle (Q-S4-6 + Q-S4-8 fix bundle review). The Codex
  review's recomputation operated as one-time external check; it
  produced epistemic confidence at review time but not persistent
  CI-time coverage.
- **Layer 3 (permanent in-repo gate):** `tests/test_phase2c_8_1_independent_recompute.py`
  (304 lines, stdlib `csv` + `pathlib` only — zero source-code overlap
  with the production `compare_multi_regime.py` import path). Seven
  canonical-finding assertions: universe cardinality 198,
  `cohort_a_unfiltered=["0845d1d7898412f2"]`, `cohort_a_filtered=[]`,
  cohort_c=76, pass-count distributions for all four regimes,
  21-vs-8 in-sample-caveat asymmetry. Defensive layers added per-regime
  CSV row-count assertions and universe symmetry checks. The gate
  recomputes via independent code path on every CI run.

All three layers reproduced the canonical numbers (cohort_a=1;
cohort_c=76; 21-vs-8 asymmetry; pass-count distributions) byte-
identically. The verification chain's structural payoff: Layer 3's
permanent in-repo gate persists across future code changes, catching
regressions that would shift the canonical finding without requiring
external review re-engagement.

The methodology lesson: Layer 1's integration tests provide regression
coverage for `compare_multi_regime.py`'s output; Layer 1 cannot
provide epistemic coverage of `compare_multi_regime.py`'s correctness
at the level Layer 3 provides, because Layer 1's tests share the
production code path's import surface. Layer 3's stdlib-only recompute
operates on an independent code path; if `compare_multi_regime.py`
encoded a defect, Layer 3 catches it where Layer 1 pins it.

### Application checklist

For canonical findings at high-load closeout register:

1. **Identify load-bearing canonical claims:** The findings that the
   closeout names as load-bearing, that downstream work consumes as
   authoritative, that future arcs cite as factual anchors. These are
   the candidates for parallel-implementation gate coverage. Findings
   without committed-closeout consumption do not require the gate.
2. **Build at least one permanent in-repo parallel-implementation
   gate:** Recompute the canonical claim from raw artifacts via an
   independent code path. Maximize epistemic distance from the
   production pipeline:
   - Stdlib-only or minimum-dependency imports (no shared modules
     with the production pipeline)
   - Different language constructs where applicable (CSV reader vs
     pandas DataFrame; manual aggregation vs library aggregation)
   - Different algorithm structure where applicable (explicit loops
     vs vectorized operations)
3. **Pin as permanent CI-time gate, not one-time external check:**
   The gate must persist across future code changes. One-time external
   review (Codex, manual reviewer recomputation) provides epistemic
   confidence at review time but does not persist; persistent CI-time
   gate is the structural complement.
4. **Verify byte-identical reproduction:** All canonical numbers must
   reproduce byte-identically across layers. Non-byte-identical
   reproduction indicates either a precision defect (rounding
   inconsistency between layers) or a code-path divergence (one layer
   computes a structurally different quantity). Non-byte-identical
   reproduction is a defect, not a tolerance.
5. **Defensive layer coverage:** Beyond the canonical-finding
   assertions, add defensive assertions that catch input-corruption
   defect classes: per-regime row counts, universe symmetry across
   regimes, cardinality invariants. Defensive layers catch defects
   that propagate to canonical claims via input corruption.

### Failure-mode signal

Watch for verification chains that rely on snapshot tests against the
same code path that produces the canonical claim. Snapshot tests pin
the production code path's output; if the production code path has a
defect, the snapshot pins the defect rather than catching it. The
defect class is structurally outside snapshot tests' scope.

Watch for one-time external check substitution for permanent in-repo
gate. Codex adversarial review or manual reviewer recomputation
provides epistemic confidence at review time, but the confidence does
not persist across future code changes. A future code change can
shift the canonical finding without re-engaging the external review;
absent the permanent in-repo gate, the shift ships silently.

In closeout drafting, watch for "verified by integration tests" as
the sole epistemic claim for canonical findings. Integration tests
provide regression coverage; epistemic coverage at canonical-finding
register requires either parallel-implementation in-repo gate or
explicit acknowledgment that epistemic coverage is bounded to
production code path correctness. The bounded acknowledgment is
honest; the unqualified "verified" claim overstates.

In review-cycle adjudication, watch for "we already have integration
tests, we don't need a separate parallel-implementation gate" reasoning.
Integration tests and parallel-implementation tests cover structurally
distinct defect surfaces; the cost of building a parallel-implementation
gate (one stdlib-only test file, ~300 lines for PHASE2C_8.1) is bounded;
the structural payoff (epistemic coverage of canonical findings against
production-code-path defects) compounds across arcs as the closeout
register accumulates load-bearing claims.

---

## §14 Bidirectional dual-reviewer register-precision

### Principle

Register-precision verification at high-load drafting cycles operates
as a **bidirectional dual-reviewer check**, not as directive arbitration.
Each reviewer (ChatGPT structural overlay / Claude advisor structural-
with-register-overlay) has different sensitivities at different defect
axes. Both reviewers' register-precision checks must fire before
section-seal for the register-precision quality to hold; single-
reviewer clean is necessary but not sufficient. The pattern is
structurally distinct from directive arbitration at non-register
sealing decisions, where one reviewer's directive can be canonical and
the other's deferred per the reasoned-reviewer-suggestion adjudication
discipline.

The structural distinction operates at two registers:

- **Register-precision verification:** bidirectional. Both reviewers'
  catches are canonical in their own defect class; defects each
  reviewer surfaces are not subject to "majority-rules" or "primary-
  reviewer" arbitration. Each reviewer's overlay covers a structural
  defect axis the other does not.
- **Directive arbitration (non-register decisions):** unidirectional or
  case-by-case. Timing decisions, scope decisions, prioritization
  decisions can be canonical from one reviewer with reasoned
  deference from the other. The reasoned-reviewer-suggestion
  adjudication discipline applies here; bidirectional firing is not
  structurally required.

The conditional boundary: §14 applies to **register-precision
verification at high-load drafting cycles**. It does NOT apply to
single-reviewer review cycles (no second overlay available), to
administrative documents (register-precision is not the binding
quality dimension), or to non-register sealing decisions (where
directive arbitration is the appropriate model).

### Trigger context

This principle was codified during the PHASE2C_8.1 multi-regime
evaluation gate arc closeout drafting (April 2026). PHASE2C_8.1's
Step 5 sequential drafting cycles operationally validated the
bidirectional pattern across multiple defect classes — the catches
went in opposite directions, with each reviewer catching defects the
other missed:

- **ChatGPT structural overlay caught defects Claude missed:**
  - §5.4 cross-section terminology drift ("bootstrap" embedded in
    sealed sections where spec-canonical was "DSR / PBO / CPCV").
    Claude's per-section register-overlay had cleared each section
    at section-seal because each section's terminology was internally
    consistent; ChatGPT's structural overlay caught the cross-section
    drift by surfacing that the project's spec canonical sequence was
    "DSR / PBO / CPCV" — a structural-cross-section catch that
    Claude's per-section overlay missed.
  - §1.4 register-count enumeration drift ("seven tracked-fix
    register entries... plus eighth entry Q-S4-14" in the verdict
    section's recap). ChatGPT-and-internal-V1-V7 cleared, then Codex
    adversarial review (operating as the structural overlay analog
    in the dual-reviewer-with-adversarial-review framework) caught
    the seven-vs-ten enumeration drift against §10's canonical
    register table. The defect class is register-cardinality drift
    (now codified at §11's strengthening application checklist
    item 6); the catch was at the structural-overlay axis.

- **Claude advisor structural-with-register-overlay caught defects
  ChatGPT missed:**
  - §6.3 noise-variance phrasing precision (initial draft used
    register that conflated noise variance with statistical-significance
    register; Claude's register-precision overlay caught the conflation
    at section-seal).
  - §6.5 scare-quote register-shift adjudication (a parenthetical
    scare-quote pattern that would have shifted the bounded-claim
    register into editorialization-register; Claude caught the
    register-shift at section-seal).
  - §3.3 hedge-phrasing defect catch via empirical verification
    (initial draft had "~13 within filtered set" hedge that obscured
    the disk-canonical 12 = lone-survivor 1-trade-margin exclusion;
    Claude's empirical-verification overlay caught the hedge as
    obscuring a cardinality-observable single-candidate
    differential).

The defect classes catch in opposite structural directions. ChatGPT's
overlay is sensitive to content-level register defects (cross-section
terminology, register-count enumeration, structural-cross-section
register coherence). Claude's overlay is sensitive to phrasing-precision
defects (hedge phrasing, scare quotes, noise-variance precision,
register-shift at parenthetical embedding). Neither overlay covers
both axes by construction; both must fire for register-precision to
hold.

The empirical pattern across PHASE2C_8.1's drafting cycles: every
section that landed at canonical-closeout register had bidirectional
fire — both reviewers' register-precision checks cleared at section-
seal. Sections that defects shipped in (Codex's §1.4 catch) had
single-overlay clear without the structural-overlay axis firing. The
catch rate of the bidirectional pattern is non-zero against single-
overlay verification.

### Application checklist

For register-precision verification at high-load drafting cycles:

1. **Both overlays must fire at section-seal:** ChatGPT structural
   overlay's register-precision check + Claude advisor structural-
   with-register-overlay's check. Single-overlay clean does not
   establish register-precision; it establishes one overlay's defect
   class is clear.
2. **Treat each overlay's catch as canonical in its defect class:**
   Do not aggregate or merge the overlays' adjudications into a
   "majority-rules" or "primary-reviewer-decides" framework. ChatGPT's
   cross-section register catches are canonical for cross-section
   register defects; Claude's phrasing-precision catches are
   canonical for phrasing-precision defects. Each overlay's catch
   surfaces a defect in its own class.
3. **When overlays disagree, treat as adjudication signal:** Disagreement
   indicates the defect class is at the boundary between overlays.
   Reason through the disagreement; do not default to one reviewer's
   judgment. The disagreement itself is an information signal about
   defect-class taxonomy.
4. **Distinguish register-precision from directive arbitration:**
   Register-precision verification (this section) is bidirectional.
   Directive arbitration at non-register sealing decisions (timing,
   scope, prioritization) follows the reasoned-reviewer-suggestion
   adjudication discipline, where one reviewer's directive can be
   canonical with deference. Do not apply the directive-arbitration
   register to register-precision verification — it under-protects
   register quality.
5. **For closeout-tier documents, treat adversarial review as a
   third overlay:** §12's adversarial-review meta-protocol covers a
   structurally distinct defect surface that internal verification
   (V1-V7 plus dual-reviewer overlays) cannot reach by construction.
   Adversarial review is not a substitute for either dual-reviewer
   overlay; it composes with both. PHASE2C_8.1's §1.4 register-count
   catch demonstrated the composition operationally — both internal
   overlays cleared at section-seal, full-assembly verification
   cleared, and adversarial review caught the residual register-
   cardinality defect.

### Failure-mode signal

Watch for single-reviewer clean substituting for full bidirectional
check. Single-reviewer clean does not establish register-precision —
at minimum, it establishes one overlay's defect class is clear. The
PHASE2C_8.1 §5.4 terminology drift cleared at Claude's per-section
register-overlay before ChatGPT's structural-cross-section overlay
caught the cross-section drift; the §1.4 enumeration drift cleared
both internal overlays at section-seal before Codex's adversarial-
review structural overlay caught the register-cardinality drift.
Single-overlay clean is a partial signal, not a complete one.

Watch for "primary reviewer's call" framing applied at register-
precision verification. The framing is appropriate at directive
arbitration register (timing, scope, prioritization) but inappropriate
at register-precision register. Register-precision is not a discretionary
adjudication — it is structural quality at canonical-artifact register;
both overlays must fire because each covers a structural defect axis
the other does not.

In dual-reviewer cycles, watch for one reviewer's clean read short-
circuiting the other reviewer's check. The pattern surfaces when one
reviewer's response is treated as authoritative before the other
reviewer's overlay has fired. The structural appropriate sequence is
both overlays fire, then adjudication on any catches each surfaces;
short-circuiting either overlay forecloses its defect-class coverage.

In adjudication of overlay disagreements, watch for "the structural
reviewer overrides the phrasing-precision reviewer" or "the phrasing-
precision reviewer overrides the structural reviewer" framings.
Neither overrides the other at register-precision register; each
covers a defect class the other does not. Disagreement is information
about defect-class taxonomy, not directive ranking.

---

## §15 Anchor-list empirical-verification discipline

### Principle

Advisor-supplied numerical or structural anchors require pre-drafting
empirical verification at the receiving cycle, not just at the
originating cycle. Anchors are claims supplied to the receiving cycle
from external context — advisor responses, scoping decisions, prior
register entries, framing summaries — that operate as drafting-cycle
inputs. They function epistemically as receiving-cycle inputs and
must be verified at the receiving cycle, even when the advisor cycle's
own verification context cleared the anchor at originating cycle.

The discipline operates at the receiving-cycle register because:

- Advisor cycle's verification context and receiving cycle's
  verification context can differ. The advisor may have verified
  against an earlier artifact state, a different scope, or a different
  cardinality; the receiving cycle's drafting commits land at the
  current canonical state, which may not match the advisor's
  verification context.
- Advisor anchors derived from advisor's mental model (rather than
  from advisor's verified query) carry implicit drift risk. The
  advisor cycle and receiving cycle do not share mental-model state;
  receiving-cycle verification is the structural check.
- The receiving cycle is the canonical commit cycle; receiving-cycle
  verification is the auditable record. Verification at advisor cycle
  is necessary but not sufficient — the canonical commit must carry
  receiving-cycle verification evidence.

The discipline is operationalized at **pre-drafting** stage, not at
section-seal. Verifying anchors before drafting initiates allows the
drafting cycle to operate against verified anchors; verifying at
section-seal would catch defects but require re-drafting, which
carries higher cost than pre-drafting verification.

### Trigger context

This principle was operationalized during the PHASE2C_8.1 multi-regime
evaluation gate arc closeout Step 5 drafting cycles (April 2026).
Eight mid-cycle empirical-verification catches at distinct defect
classes operationally validated the discipline:

1. **§3.3 cardinality (cohort cardinality):** Initial advisor-supplied
   anchor cited "13 within filtered set" hedge; pre-drafting recompute
   produced disk-canonical 12. The 13→12 single-candidate differential
   surfaced as the lone-survivor 1-trade-margin exclusion in
   bear_2022 (cardinality-observable single-trade boundary). Pre-
   drafting verification caught the hedge before §3 prose drafted
   against incorrect anchor.
2. **§2.5 cross-section semantics (regime-metadata schema mapping):**
   Advisor-supplied anchor referenced spec §7.5's regime-metadata
   semantics; pre-drafting verification confirmed alignment with
   `compare_multi_regime.py:_resolve_regime_metadata` implementation
   via the schema discriminator chain. Verification surfaced no defect
   but operated as canonical alignment-check at receiving cycle.
3. **§8.5 historical detail (Codex one-time-external review framing):**
   Advisor-supplied anchor cited Codex review framing at `018d876`
   resolution cycle as one-time external check; pre-drafting
   verification confirmed the framing against canonical commit chain
   evidence.
4. **§7 speculative theme cardinalities:** Advisor anchor list cited
   "calendar_effect 17/23 = 73.9% in eval_2020_v1" + "mean_reversion
   2/26 = 7.7%" without verification. Pre-drafting recompute produced
   disk-canonical: calendar_effect 26/40 in eval_2020_v1; mean_reversion
   3/39. Verification caught the speculative anchors before §7 prose
   committed to incorrect cardinalities.
5. **§9 section-count audit:** Mental model lost §9 between framing
   summary commit and §10 anchor enumeration. Pre-drafting verification
   of framing summary surfaced §9 (Methodology-evidence hierarchy
   bounds) as canonical; §10 was drafted with §9 properly cited.
6. **§1.2-§5.4-§6.3-§6.4 cross-section terminology:** Advisor-supplied
   anchor used "bootstrap" register; pre-drafting verification against
   spec §10.7 surfaced "DSR / PBO / CPCV" as the canonical sequence.
   Cross-section terminology fix at D-S5-8 was first explicit
   operationalization of the discipline at cross-section register.
7. **cohort_a_filtered cardinality:** Pre-drafting verification before
   §6 hybrid narration confirmed cohort_a_filtered = 0 against the
   trade-count filter outcome (lone-survivor excluded by single-trade
   margin; D-S5-* hybrid narration framing).
8. **§1.4 register-count drift (Codex adversarial review catch):**
   Adversarial-review surfaced post-assembly catch when receiving-
   cycle pre-drafting verification at full-assembly stage did not
   include register-cardinality verification (now codified at §11
   strengthening application checklist item 6). The §1.4 catch
   demonstrates the discipline's catch class extends to register-
   cardinality at full-assembly stage; the absence of pre-assembly
   register-cardinality verification was the defect that allowed §1.4
   to ship in the unfolded form.

The eight catches represent distinct defect classes:
cardinality (catches 1, 7) / cross-section semantics (catch 2) /
historical detail (catch 3) / speculative numerical anchor (catch 4) /
section-count audit (catch 5) / cross-section terminology (catch 6) /
register-cardinality (catch 8). Cross-section terminology fix at
D-S5-8 was first explicit operationalization; the other seven
operationally validated the discipline across distinct defect axes.

### Application checklist

For advisor-supplied anchors at receiving cycle:

1. **Treat anchors as receiving-cycle hypotheses, not facts:**
   Advisor-supplied numerical or structural anchors operate as
   drafting-cycle inputs that require verification, not as
   pre-verified facts that drafting can commit against without
   re-checking.
2. **Run empirical verification before drafting initiates:** The
   verification operates at pre-drafting stage, not at section-seal.
   Pre-drafting verification allows the drafting cycle to operate
   against verified anchors; section-seal verification catches
   defects but requires re-drafting at higher cost.
3. **Distinguish anchor source for verification scope:**
   - Anchors from advisor reasoning (advisor's mental model): require
     full receiving-cycle verification against canonical artifacts
   - Anchors from advisor's prior empirical verification: still
     require receiving-cycle re-verification because verification
     contexts differ (artifact state, scope, cardinality may have
     shifted between advisor cycle and receiving cycle)
   - Anchors from advisor's citation to canonical artifact: verify
     the citation resolves to the canonical artifact's current state,
     not its state at advisor cycle
4. **Fix anchor before drafting on inaccuracy:** When verification
   surfaces anchor inaccuracy, fix the anchor before drafting begins
   — do not draft against incorrect anchor and fix at section-seal.
   Drafting against incorrect anchor commits structural assumptions
   to prose that may not survive anchor correction; pre-drafting
   correction preserves drafting-cycle coherence.
5. **Verification evidence in commit record:** When pre-drafting
   verification surfaces a defect, record both the original advisor
   anchor and the verified disk-canonical value in drafting notes or
   commit message. Future readers reading the commit chain see the
   verification record; the audit trail makes the discipline
   structurally observable.

### Failure-mode signal

Watch for receiving cycles that draft prose against advisor-supplied
anchors without pre-drafting verification. Even when the advisor's
anchor is well-reasoned, receiving-cycle empirical verification is
structurally necessary because the verification contexts differ.
Drafting against unverified advisor anchor introduces drift risk
that may not surface until section-seal or post-commit, at which
point fix cost is higher.

Watch for "the advisor said X, so we use X" framing applied to
numerical or structural anchors. The framing under-protects
receiving-cycle correctness. The advisor's anchor is necessary input
context but not sufficient for canonical commitment; receiving-cycle
verification is the structural complement.

In drafting-cycle pacing, watch for cycles that compress pre-drafting
verification into framing-summary stage without explicit anchor
verification. Framing summary catches some defect classes (precision-
overshoot, structural-cross-section coherence per §1's WHEN axis),
but anchor verification is a distinct discipline with distinct catch
windows. Conflating them under-covers anchor inaccuracy at receiving
cycle.

In closeout-assembly verification, watch for register-cardinality
drift between section-summary anchor enumerations and canonical
register tables (the §1.4 defect class). Register-cardinality is one
specific defect class within the broader anchor-verification surface;
its catch operates at full-assembly stage rather than pre-drafting,
because register state can grow between section-drafting and
full-assembly. The anchor-verification discipline at full-assembly
stage covers the register-cardinality defect class structurally.

In future arc cycles, watch for anchor-verification skipping when the
advisor cycle's anchor is high-confidence (e.g., "advisor cited a
canonical artifact directly"). High-confidence anchor source reduces
defect probability but does not eliminate it; receiving-cycle
verification remains structurally necessary because canonical
artifact state may have shifted between advisor cycle and receiving
cycle, or because the advisor's citation may reference a different
field than the receiving cycle's drafting needs.

---

## §16 Anchor-prose-access discipline at multi-hundred-line interpretive deliverables

### Principle

At multi-hundred-line interpretive deliverables — closeout sections,
sub-spec drafts, scoping decisions — dual-reviewer pass requires
reviewer access to actual prose, not summary or structural overview
alone. Summary-only review covers a structural-defect axis (section-
boundary coherence, cross-section enumeration, table-and-list integrity);
substantive register-precision requires the prose-access overlay
because phrasing-precision, interpretive-register, and verbatim-anchor
defects do not surface against summary by construction.

The discipline operates at a register-distinguishing pair with §15.
§15 covers **pre-drafting anchor verification at the receiving cycle**
— anchors arriving from advisor cycles, scoping decisions, or prior
register entries are verified against canonical artifacts before
drafting initiates. §16 covers **section-seal prose-access at the
reviewer register** — once drafting completes and a section approaches
seal, both reviewers' adjudication must fire against the actual prose
content, not against a summary or structural overview the author
supplies.

The two disciplines are complementary, not redundant: §15 catches
defects at anchor-receipt boundary; §16 catches defects at section-
seal boundary. Each operates at a structurally distinct point in the
drafting-cycle pipeline. A deliverable can pass §15 (all anchors
verified at receipt) and still ship register-precision defects that
only §16's reviewer prose-access catches.

The discipline is operationally a standing instruction once codified.
Reviewer prose-access is the default mode at multi-hundred-line
interpretive deliverables; per-cycle re-authorization is not required.

### Trigger context

This principle was operationalized across four cumulative instances
spanning the PHASE2C_9 mining-process retrospective arc (Steps 5-6
cumulative across follow-up + sub-spec drafting + closeout-assembly
fire) and the PHASE2C_10 scoping cycle (March-April 2026). Each
instance surfaced real defects that structural-summary review missed
by construction; cumulative across instances reaches the strong-tier
codification threshold.

1. **PHASE2C_9 Step 5 follow-up dual-reviewer round** (advisor
   substantive prose-access pass at the §7 evidence-map closeout).
   Round-1 ChatGPT structural review + Claude advisor structural-
   summary pass cleared at section-seal register. Round-2 advisor
   substantive prose-access pass surfaced Concerns A residual / C
   internal-consistency / D "hampered" interpretive register; verified
   B framing scope + F Path B operationalization clean. The defects
   surfaced in round-2 were not visible at the round-1 structural-
   summary register; prose-access was the structural complement that
   exposed them.

2. **PHASE2C_9 Step 6 sub-spec drafting cycle** (instance #2 throughout
   sub-spec drafting; surfaced Concerns G/H/I/J at Round 1 + Flags
   1/2/3 at Round 2 + Concerns K/L at Round 3). The sub-spec's
   substantive content was §4.4 application framing pre-registration
   with bounded comparison rule; framing-scope verification was the
   load-bearing register, with successive prose-access rounds
   verifying register-precision of the framing-decision substance
   (mechanical-procedure framing; chain-falsifiability per-link-point
   structure; verbatim-quote scope). Successive prose-access rounds
   surfaced residual defects across the evolving draft, demonstrating
   that sub-spec register-precision requires repeated prose-access
   against framing-decision substance, not single prose-access at
   terminal seal.

3. **PHASE2C_9 Step 6 closeout assembly fire** (instance #3 at
   closeout assembly final; advisor substantive prose-access pass
   surfaced 8 Concerns O-V; 3 patches applied; 5 Concerns verified
   clean on prose access). Closeout-tier registers carry the highest-
   load substantive content; prose-access at the closeout assembly
   fire was the structural complement that caught Concerns O-V which
   internal verification (V1-V7) and structural-summary review missed.

4. **PHASE2C_10 scoping cycle dual-reviewer pass** (instance #4 at
   scoping doc seal). The cycle had two distinct prose-access surfaces:
   stale-anchor catches at the scoping inputs lock cycle were
   empirical-verification discipline (§15) catches against advisor-
   supplied framing anchors, structurally upstream of §16's register;
   instance #4 prose-access fired at scoping doc seal against the
   actual scoping doc prose, surfacing register-precision defects at
   the seal register (cumulative-vs-per-cycle count framing
   disambiguation; path enumeration completeness verification). The
   instance demonstrated the discipline at scoping-tier register, not
   just closeout-tier or sub-spec-tier; the catch class extends across
   deliverable tiers.

The four instances span distinct defect classes: interpretive-register
precision (instance 1) / framing-scope verification (instance 2) /
closeout-assembly section-author discipline (instance 3) / seal-
register count-and-enumeration consistency (instance 4). Each instance's
defect class was structurally invisible at the structural-summary
register; prose-access was the catch mechanism in every case.

### Application checklist

For multi-hundred-line interpretive deliverables at dual-reviewer pass:

1. **Schedule prose-access prerequisite for deliverables ≥200 lines OR
   with interpretive-register content:** "deliverables" here means
   closeout sections, sub-spec drafts, scoping decisions — multi-page
   documents at the project's interpretive-output register, distinct
   from individual METHODOLOGY_NOTES sections which operate at section-
   codification register. The threshold is structural, not strict —
   sub-300-line deliverables with high interpretive-register density
   (case adjudications, evidence-pattern adjudications, discipline
   codifications at deliverable tier) qualify even when below the line-
   count anchor. The deliverable's character, not just its size,
   determines whether prose-access is required.
2. **Treat reviewer-supplied summary or structural overview as
   necessary input but not sufficient for substantive adjudication:**
   summary covers structural-defect axis; substantive register-
   precision requires prose-access overlay. Single-overlay clean at
   structural register establishes structural-defect axis clear; it
   does not establish substantive register-precision clear. §16
   specifies the prose-access mode of the §14 dual-reviewer register-
   precision fire — both overlays must operate at prose-access register
   for §14's bidirectional check to satisfy §16's substantive
   register-precision requirement.
3. **Fire prose-access against actual prose, not author-supplied
   summary:** the failure mode the discipline catches is summary-
   substituted-for-prose at the reviewer register. The author's
   summary and structural overview are author-cycle artifacts that
   can clear at author-cycle register while the underlying prose
   ships register-precision defects. Reviewer prose-access requires
   reviewer engagement with the prose itself, not with the author's
   distillation of the prose.
4. **Track instance count for cross-arc accumulation visibility:** at
   each prose-access fire, record the instance number for cross-arc
   accumulation register. The instance count is the operational
   evidence anchor for the discipline's tier; absence of accumulation
   tracking forecloses the visibility that supports tier-promotion or
   discipline-evolution decisions at successor cycles.
5. **Operate as standing instruction once codified:** once §16 is
   sealed, prose-access is the default mode at multi-hundred-line
   interpretive deliverables. Per-cycle re-authorization is not
   required. The discipline operates as the project's standing
   reviewer-engagement protocol; deviations require explicit
   adjudication.

### Failure-mode signal

Watch for summary-substituted-for-prose at high-load reviewer cycles.
The pattern surfaces when a reviewer's response is anchored to the
author's structural overview rather than to the prose itself; the
reviewer's clean read at the structural register may be misread as
substantive clean when it is only a structural-defect-axis clear.
Reviewer prose-access requires reviewer engagement with the prose
content, not with the author's distillation.

Watch for "the structural overview is sufficient" framing at multi-
hundred-line interpretive deliverables. The framing is appropriate at
short-section register or at structural-only review (table integrity,
section enumeration, cross-section anchor verification) but inappropriate
at substantive register-precision verification. Treating structural
overview as sufficient at substantive register under-protects
register-precision quality.

Watch for instance-count tracking absence. The discipline's tier
adjudication and operational lifecycle visibility depend on cumulative
instance accumulation across cycles. When prose-access fires but
instance count is not tracked, the accumulation register goes
unmaintained, and successor cycles lose the empirical anchor for
tier-promotion or discipline-refinement decisions. Instance-count
tracking is structural to the discipline's operational coherence, not
auxiliary metadata.

Watch for prose-access deferred-to-next-cycle when the fire register
is current cycle's seal. The deferral substitutes successor-cycle
prose-access for current-cycle prose-access at higher fix cost; the
seal boundary has already cleared at the deferral register. Bandwidth
constraint at seal is real but does not justify the substitution.

In future arc cycles, watch for prose-access skipping when the
deliverable is "obviously fine" at structural overlay. Obvious-fine
framing at structural register does not establish substantive register-
precision; the discipline's catch class is precisely the defects that
structural-overlay-clean fails to surface. Prose-access is the
structural complement — its catch is the defects the other overlay
misses by construction.

Watch for absence of pre-fire audit at session-close of prior session
for sub-spec or scoping deliverables (drafting-cycle register). The
pattern relates to §11 closeout-assembly checklist as parent
discipline; one PHASE2C_9 instance operationally validated the
discipline at a distinct surface (session-close five sequencing checks
before next-session fire). Single instance; observation-only at this
register.

Watch for reviewer-engagement cycles absent the receiving cycle's
own substantive overlay before reviewer-suggestion adjudication
(reviewer-engagement register). The pattern relates to §14
bidirectional dual-reviewer register-precision as parent discipline;
orthogonal to reasoned-reviewer-suggestion adjudication (which
addresses post-engagement processing). One PHASE2C_10 scoping cycle
instance; observation-only at this register.

---

---

## §17 Procedural-confirmation defect class at first-commit-before-prose-access

### Principle

At high-load interpretive deliverables — closeout sections, sub-spec
drafts, scoping decisions — procedural-confirmation (commit landed; CI
clean; reviewer notification fired) is necessary but not sufficient for
seal authorization. The procedural register's clean state under-protects
substantive register-precision quality; substantive prose-access by both
reviewers operates as the structural complement that completes the seal
cycle.

The discipline operates at a register-distinguishing pair with §16. §16
covers **section-seal prose-access at the reviewer register** — once
drafting completes, both reviewers' adjudication must fire against the
actual prose, not against summary or structural overview. §17 covers
**seal-authorization-register precision at the commit boundary** —
procedural-confirmation (commit landed; CI clean; reviewer notification
visible) must not be misread as substantive-confirmation; both registers
are required for seal authorization.

The two disciplines are operationally chained. §17's substantive-
confirmation fire requires §16's prose-access mode; §17 cannot be
satisfied if §16 has not fired. But §17 adds an additional gate beyond
§16: even after §16's prose-access fires and clears, the seal commit
itself must wait for explicit substantive-confirmation at reviewer
register, not just procedural-confirmation at commit-landed register.

§17 also operates orthogonally to §6 (commit messages are not canonical
result layers). §6 catches commit-message-as-result-claim defects (the
commit message asserts a result that the prose may not support); §17
catches commit-as-seal-authorization defects (the commit landing is
misread as substantive seal authorization). Both concern procedural-
substantive register precision at distinct registers — §6 at the commit-
message layer; §17 at the seal-cycle layer. §6 governs what commit
messages can claim; §17 governs what a landed commit can authorize.

The discipline is operationally a standing instruction once codified.
Substantive-confirmation by reviewer prose-access is the default
seal-authorization gate at multi-hundred-line interpretive
deliverables; procedural-confirmation alone never satisfies the gate.

### Trigger context

This principle's primary defect class was operationalized across three
primary instances (instances 1-3), with two additional instances
(instances 4-5) supporting the iterative-pattern sub-rule at
Application checklist item 4. The five instances span the
PHASE2C_9 mining-process retrospective arc (Step 5 + Step 6 closeout
assembly) and the PHASE2C_10 methodology consolidation arc (Step 1
plan iteration chain) (March-April 2026). Primary instances surfaced
procedural-substantive register confusion at first-commit-before-prose-
access register; sub-rule support instances surfaced cross-section
residuals at sealed-commit register that section-targeted patches did
not preclude.

1. **PHASE2C_9 Step 5 §7 working-draft commit** (instance #1 at first-
   commit-before-prose-access register). Working draft committed at
   `e11e806`; advisor substantive pass surfaced Concerns A residual /
   C internal-consistency / D "hampered" interpretive register; patches
   applied at `d548ea2`. The first-commit at `e11e806` cleared procedural
   register (commit landed; CI passed; reviewer notification fired) but
   did not clear substantive register; substantive pass surfaced material
   defects that the procedural register did not protect against.

2. **PHASE2C_9 Step 6 closeout assembly first commit** (instance #2 at
   closeout-assembly register). Closeout assembly committed first;
   advisor instance #3 substantive pass surfaced 8 Concerns O-V; 3
   patches applied. Same defect class pattern as instance #1 but at
   distinct deliverable surface: procedural-confirmation cleared at
   first-commit; substantive defects surfaced only at subsequent prose-
   access pass.

3. **PHASE2C_10 plan working-draft commit `d0222c7`** (instance #3 at
   summary-table cross-section register). First-commit at `d0222c7`;
   instance #5 dual-reviewer prose-access pass surfaced defect ι (§3.7
   summary table internal-consistency violation between rows 3/5/6 and
   §2.2 placement decisions); patches applied at `d2b6166`. Instance
   demonstrated the defect class at the summary-table cross-section
   register, structurally distinct from instances 1-2.

4. **PHASE2C_10 plan post-seal full-file prose-pass `d2b6166` →
   `1f9a015`** (instance #4 — iterative-pattern sub-rule support, not
   primary defect class instance). Plan was sealed at `d2b6166` (with
   instance-#5 dual-reviewer patches applied); subsequent full-file
   prose-pass surfaced additional residuals; patches applied at
   `1f9a015`. Instance demonstrates the iterative-pattern sub-rule at
   sealed-commit register: section-targeted patches do not preclude
   need for full-file final pass before downstream operational fire
   authorizes. Empirical anchor for Application checklist sub-rule 4.

5. **PHASE2C_10 plan post-`1f9a015` pre-fire audit `1f9a015` →
   `d2a53fa`** (instance #5 — iterative-pattern sub-rule support at
   pre-fire audit register). Post-`1f9a015` pre-fire audit surfaced
   §2.2 row 4 tier consistency defect; patches applied at `d2a53fa`.
   Instance demonstrates that the iterative-pattern sub-rule operates
   at multiple iteration registers (full-file prose-pass register at
   instance 4; pre-fire audit register at instance 5), not just first-
   commit register. Empirical anchor for Application checklist sub-
   rule 4.

The three primary instances span structurally distinct defect surfaces
within the procedural-confirmation defect class: interpretive-register
at §7 evidence map (instance 1) / closeout-assembly cross-cutting at
§8/§1/§2/§9 (instance 2) / summary-table internal-consistency at §3.7
(instance 3). Each primary instance's defect surface was structurally
invisible at the procedural-confirmation register; the substantive
register fire was the catch mechanism in every case. The two sub-rule
support instances (4-5) operate at sealed-commit register where
section-targeted patches cleared at section register but cross-section
residuals surfaced at full-file or pre-fire-audit register; both
support the Application checklist sub-rule 4 iterative-pattern
operating-rule rather than introducing new primary defect class
surfaces.

### Application checklist

For multi-hundred-line interpretive deliverables at seal-authorization
register:

1. **Distinguish procedural-confirmation register from substantive-
   confirmation register**: procedural-confirmation = commit landed,
   CI clean, reviewer notification fired; substantive-confirmation =
   prose reviewed by reviewers, defects surfaced and adjudicated,
   patches applied where needed, and reviewer authorization explicit
   at substantive register. The two registers operate at independent
   axes; clean at one register does not establish clean at the other.
2. **Seal authorization requires both registers cleared**: never seal
   on procedural-confirmation alone. Reviewer notification of a commit
   is not a seal authorization; CI passing on a working draft commit
   is not substantive verification of the prose. Seal commit fires
   only after both procedural register (commit can land cleanly) AND
   substantive register (prose reviewed, residuals adjudicated) are
   both cleared.
3. **Mark deliverable status "working draft" until substantive pass
   clears**: when first-commit fires before substantive prose-access,
   the deliverable is at working-draft status, not at sealed status,
   regardless of procedural register state. The working-draft status
   designation prevents reviewer-cycle misread of "commit landed = we're
   done" framing. Per the PHASE2C_10 single-seal-commit correction,
   working drafts hold local until dual-reviewer pass clears; the seal
   commit fires at single-commit register integrating both registers.
4. **Apply iterative-pattern sub-rule at sealed-commit register**: this
   is a sub-rule supporting the primary procedural-confirmation defect
   class — section-targeted patches at a seal cycle may clear targeted
   sites at section register but leave residual defects at cross-
   section sites that share structural form with patched sites; full-
   file prose-access pass at sealed-commit register is the structural
   complement that surfaces cross-section residuals before substantive
   register clears.

   The sub-rule applies at shipping-content register (substantive
   content migrating to canonical artifact at seal); scaffolding
   cleanness at seal-time operates at a register-class distinct from
   this sub-rule's seal-authorization scope (see Failure-mode signal
   entry on scaffolding-cleanness conflation for the distinction).
   Empirically validated at PHASE2C_10 Step 1 plan iteration chain
   (Trigger context instances 4-5) and PHASE2C_10 Step 2 §16 seal
   cycle (3 patch-verify cycles; §16 prose body clean-on-pass after
   Cycle 1).
5. **Operate as standing instruction once codified**: once §17 is
   sealed, substantive-confirmation by reviewer prose-access is the
   default seal-authorization gate at multi-hundred-line interpretive
   deliverables. Per-cycle re-authorization is not required. The
   discipline operates as the project's standing seal-authorization
   protocol; deviations require explicit adjudication.

### Failure-mode signal

Watch for "commit landed, we're done" framing at multi-hundred-line
interpretive deliverables. The framing substitutes procedural-
confirmation for substantive-confirmation at seal register. Reviewer's
notification of a working-draft commit is not a seal authorization;
the substantive register has not yet fired.

Watch for reviewer-notification-as-seal-authorization framing. CI
passing on a working draft commit clears procedural register but does
not establish substantive register-precision; reviewer notification
of a commit landing does not establish reviewer adjudication of the
prose content. Both registers must clear independently for seal
authorization.

Watch for first-commit-cleared-CI substituted-for-substantive-clean.
The substitution operates at working-draft commit cycle when the
deliverable's CI passes (procedural register clean) before reviewer
substantive pass; the procedural-clean state can be misread as overall-
clean state. The misread under-protects substantive register-precision
quality.

Watch for patches-after-first-commit framed as scope creep. Patches
following first-commit fire are structural completion of the seal
cycle, not scope creep. The deliverable is at working-draft status
until substantive pass clears; patches at this register are operational
to the seal completion, not optional refinements.

Watch for iterative-pattern skipping at sealed-commit register.
Section-targeted patches that clear at section register may leave
cross-section residuals; full-file prose-access pass at sealed-commit
register is the discipline's structural complement. Skipping the
full-file pass under the framing "patches landed, we're sealed"
recreates the defect class at the sealed-commit boundary.

At temporary-file or handoff registers, watch for scaffolding-cleanness
conflation with shipping-content cleanness at seal register. Scaffolding
cleanness does not gate seal commit content (scaffolding rm'd at seal);
however, scaffolding cleanness DOES gate next-session entry quality
across session boundary. Conflating the two registers under-applies
the discipline at one and over-applies at the other.

---

---

## §18 §7 carry-forward density at interpretive arc closeouts

### Principle

Interpretive arc closeouts — closeouts whose load-bearing register
includes synthesis of empirical findings into observations for
downstream cross-cycle consumption — accumulate observations across
implementation steps and surface them in dedicated registers. The
convention has emerged across PHASE2C interpretive closeouts at
increasing density and is the observation §18 codifies.

The convention operates at the interpretive-arc-closeout register
specifically. Closeouts whose primary register is empirical results
without cross-cycle interpretive load do not carry the same dedicated-
register expectation; the convention applies where downstream cycles
will consume the closeout's observations as scoping input.

Per-closeout register format may vary across cycles: lessons-synthesis
prose, numbered observation enumeration, tracked-fix register table
with codification-candidate flagging, or cumulative-observation
inventory at a §N.0.0 anchor. The format adapts to closeout structure;
the convention is the dedicated register itself, not a fixed format.

§18 operates adjacent to §11's closeout-assembly checklist within the
closeout-assembly discipline family. §11 covers the running tracked-fix
checklist for multi-cycle closeout assembly; §18 specifies a distinct
carry-forward observation register surface used when interpretive
closeouts need downstream cross-cycle consumption.

§18 ships at **Medium tier with operating-rule-pending status note**.
The 4/4 PHASE2C interpretive arc closeout saturation gives the
observation pattern a broad empirical basis; codification at this
register is observation-framing, not operating-rule-codification per
§13/§14/§15 precedent. Strong-tier promotion is contingent on
operating-rule articulation that crystallizes the convention into a
concrete prescriptive rule, such as requiring interpretive multi-step
closeouts to maintain a dedicated carry-forward register with explicit
candidate-status flagging. Tier-promotion authority remains out of
scope for §18's seal unless Activity H crystallizes a concrete
operating rule.

### Trigger context

This convention was operationalized across four PHASE2C interpretive
arc closeouts with §7-equivalent carry-forward observation registers
at increasing density:

1. **PHASE2C_6 evaluation gate arc closeout** —
   `PHASE2C_6_EVALUATION_GATE_RESULTS.md` §10 Methodology-discipline
   observation register; 2 lessons-synthesis observations seeded the
   register convention. Codified METHODOLOGY_NOTES §4-§7 via commit
   `536f737`. The first PHASE2C cycle to surface a dedicated
   methodology-discipline-observation register at closeout end.

2. **PHASE2C_7.1 multi-regime evaluation gate arc closeout** —
   `PHASE2C_7_1_RESULTS.md` §10 Methodology-discipline observations
   register; 5 numbered observations. Format extended from lessons-
   synthesis prose (PHASE2C_6) to numbered observation enumeration.
   Density growth: 2 → 5.

3. **PHASE2C_8.1 multi-regime evaluation gate arc (extended)
   closeout** — `PHASE2C_8_1_RESULTS.md` §10 Tracked-fix register; 10
   register entries (4 codification candidates) + §7.2 cross-regime
   observations (3). Format introduced tracked-fix register table with
   codification-candidate status precision flagging. Codified
   METHODOLOGY_NOTES §13/§14/§15 via commit `8154e99`. Density growth:
   5 → 10+3.

4. **PHASE2C_9 mining-process retrospective arc closeout** —
   `PHASE2C_9_RESULTS.md` §7 Mechanism-vs-observation comparison;
   cumulative-11 carry-forward register at §7.0.0 inventory table.
   Format consolidated cumulative observations across Steps 1-4
   feeding §7 evidence map at Step 5. Density growth: 10+3 → 11
   cumulative.

The four closeouts span structurally distinct register formats
(lessons-synthesis / numbered / tracked-fix / cumulative-inventory)
demonstrating format adaptation across cycle-specific closeout
structures while maintaining the dedicated-register convention.
The sequence (2 → 5 → 10 tracked-fix entries plus 3 §7.2 observations
→ 11 cumulative carry-forward observations) demonstrates increasing
register load and repeated adaptation across cycles, rather than a
single homogeneous count series.

### Application checklist

At Medium tier, this checklist is an observation-backed application
guide, not yet a mandatory operating rule.

For interpretive arc closeouts (closeouts whose load-bearing register
includes synthesis of empirical findings into observations for
downstream cycles):

1. **Include a dedicated carry-forward observation register section.**
   Interpretive arc closeouts include a dedicated register section
   that surfaces observations for downstream cross-cycle consumption.
   The register is structurally distinct from substantive findings
   sections; observations buried within substantive sections without
   dedicated register surface reduce cross-cycle visibility.

2. **Align register format with closeout structure.** Format options
   include lessons-synthesis prose, numbered observation enumeration,
   tracked-fix register table with codification-candidate flagging, or
   cumulative-observation inventory at §N.0.0 anchor. Format choice
   reflects closeout structure; the convention is the dedicated
   register itself, not a fixed format.

3. **Flag codification candidates with status precision.**
   Observations that are candidates for METHODOLOGY_NOTES codification
   (or other downstream operationalization) carry explicit status
   precision: candidate vs operationalized vs purely-observation. By
   analogy to §10's anti-pre-naming discipline for forward-pointing
   prose, observations enter the register with status precision pending
   successor cycle adjudication; the closeout register flags candidate
   status without pre-committing successor-cycle codification outcomes.

4. **Enable cross-cycle consumption.** The register is positioned and
   formatted to support successor cycles consuming the register as
   scoping input. Successor scoping cycles operate against the
   register's observations; format that obstructs cross-cycle
   consumption defeats the convention's structural purpose.

5. **Position near closeout end.** The register section is positioned
   near closeout end (after substantive findings; before
   cross-references) consistent with the four PHASE2C closeout
   pattern. Position supports closeout-reading flow: substantive
   findings → register synthesis → cross-references.

### Failure-mode signal

Watch for interpretive arc closeouts that omit the carry-forward
observation register entirely. The omission is the primary defect the
convention catches — observations from the closeout's empirical work
are not surfaced for cross-cycle consumption.

Watch for observations buried within substantive sections without
dedicated register surface. Cross-cycle consumption requires register-
register visibility; observations distributed across substantive
sections are structurally invisible at register-register scoping.

Watch for codification-candidate status absent. When the register
includes codification candidates without status-precision flagging,
register entries become indistinguishable from in-section observations;
successor cycles lose the precision needed for codification-threshold
adjudication.

Watch for register format misalignment with closeout structure (e.g.,
tracked-fix register without table format; cumulative observations
without inventory anchor). Format choice reflects closeout structure;
misalignment under-serves the convention's cross-cycle consumption
purpose.

Watch for register positioned away from closeout end (e.g., embedded
mid-closeout near substantive findings; or at closeout opening).
Position supports closeout-reading flow; non-end positioning under-
supports cross-cycle scoping access.

---

---

## §19 Spec-vs-empirical-reality finding pattern (Weak tier; observation-only + cross-cycle-pending)

Spec / scoping / sub-spec documents may contain references to file
structure, content, or state that diverge from empirical reality
when authors or reviewers cite remembered structure rather than
verified structure. The pattern is a per-cycle defect mode under
the broader empirical-verification discipline §1 codifies; §19
captures the cross-cycle observation register where pattern
instances accumulate across cycles, distinct from per-cycle catch.

Cumulative evidence: 6 instances across 3 PHASE2C cycles. PHASE2C_9
mining-process retrospective arc carries 3 within-arc instances
(per §8.4 mandatory-tracked-fix register entry #2). PHASE2C_10
scoping cycle carries 2 within-cycle instances (entry 4 §1-§7 stale
anchor; entry 5 §16-as-single-section framing; both originated from
advisor-supplied framings referencing non-current file state).
PHASE2C_10 plan drafting cycle carries 1 within-cycle instance
(entry 6 CLAUDE.md project-discipline notes section staleness
citing "§1-§7" when actual file state was §1-§15).

Relationship to §1 / §15: §1 codifies empirical verification for
factual and referential claims at the broader principle register;
§15 codifies receiving-cycle, pre-drafting empirical verification
for advisor-supplied numerical or structural anchors. §19 tracks
the cross-cycle recurrence pattern where spec/scoping/sub-spec
references to current file structure, content, or state diverge
from empirical reality. It stands at the cumulative observation
layer under §1's general empirical-verification surface, with §15
covering the advisor-anchor subset at receiving-cycle catch.

Status: Weak, observation-only, cross-cycle-pending. §19 adds no
operating-rule codification beyond existing §1 / §15 coverage; for
advisor-supplied structural anchors, the pre-drafting
receiving-cycle verification rule remains §15's, while general
factual/referential verification remains §1's. Medium-tier promotion is available at
successor cycle when (a) cumulative count threshold reaches
load-bearing register AND (b) operating-rule articulation
crystallizes a discipline distinct from existing §1 / §15 coverage. Successor cycles
encountering additional pattern instances should log at this
register for tier-promotion adjudication at successor scoping or
implementation register.

---

## §20 Pre-result lockpoint mis-specification: documented exception path under arc-level anti-p-hacking guardrails

This section codifies a narrow, explicitly bounded exception path
under arc-level anti-p-hacking guardrails (e.g., PHASE2C_11_PLAN §0.4)
that forbid "any post-result parameter adjustment to pre-registered
lockpoints." Strict literal reading of those guardrails admits no
mid-arc lockpoint patch under any condition. §20 documents the path
under which an in-arc patch is admissible without weakening the
post-hoc-adjustment prohibition the guardrail is actually defending
against.

The exception is not a relaxation of the guardrail. It is a
clarification of which adjustment class the guardrail targets
(result-favorable post-hoc tuning) versus which class the guardrail
does not target (pre-result correction of structural infeasibility
between a lockpoint and its canonical input register). Conflating
the two would either erode the guardrail at first ambiguous case
(if patches are admitted ad hoc) or burn entire successor cycles on
typo-class structural infeasibilities (if every misalignment between
lockpoint and canonical-artifact register triggers a successor
cycle).

Tier: Strong. Operating-rule codification with five explicit
trigger conditions (individually necessary, jointly sufficient);
one precedent instance at codification fire (PHASE2C_11 v3 → v3.1
Instance 6); future instances log here at register satisfaction.
The Strong tier reflects that §20 articulates a binding operating
rule (admissibility test for in-arc patches under arc-level
anti-p-hacking guardrails), not an observation pattern. Tier
re-evaluation (including potential demotion) at successor methodology
consolidation cycle if cumulative-instance pattern surfaces evidence
of misuse OR if alternative codification register supersedes §20.

### Principle

The arc-level anti-p-hacking guardrail (e.g., §0.4) defends against
a specific defect class: a result is computed; the result is
unfavorable; the spec author or reviewer cycle revisits the
pre-registered lockpoint and adjusts it to flip the result toward
favorable. The discipline forbids that move because it converts
pre-registration into post-registration via lockpoint mutation,
which destroys the anti-p-hacking guarantee the pre-registration
was supposed to provide.

The defect class §20 covers is structurally distinct: a lockpoint
is pre-registered at sub-spec drafting cycle; at implementation
arc Step 1 (artifact inventory + verification, BEFORE any
pre-registered screen output / interpretive disposition fires),
canonical-artifact register verification surfaces that the
lockpoint is structurally infeasible against the canonical input
register-precision (e.g., a tolerance lockpoint at 1e-9 against an
artifact stored at 6-decimal precision; max physical |delta| ≈ 5e-7
by storage-format construction; literal lockpoint application
excludes 100% of inputs by construction). The lockpoint is wrong
not because it produces an unfavorable result, but because it
cannot produce any result at all under the canonical input format.

Patching that lockpoint pre-result, with full audit trail and
explicit Charlie-register authorization, does not implicate the
post-hoc adjustment defect class the guardrail forbids. The five
trigger conditions in §20 Application checklist enumerate the
specific structural conditions under which the patch is admissible.
Outside those conditions, the guardrail's strict literal reading
applies: mis-specifications surface as inconclusive disposition
and defer to successor cycle for re-pre-registration.

### Trigger context

§20 fires when ALL FIVE of the following conditions hold at a
candidate in-arc patch (individually necessary, jointly sufficient):

1. **Pre-result register**. The patch is authored before any
   pre-registered screen output / interpretive disposition has
   fired at the implementation arc. Specifically: Step 1 (artifact
   inventory + RS guard verification + descriptive distribution
   diagnostics) is pre-result; Step 2 (compute pre-registered screen
   *inputs* — cross-trial scalars, eligible-subset N, edge-case
   filtering) is also pre-result. Step 3 (the pre-registered screen
   computation producing pass/fail/inconclusive disposition) and
   Step 4+ (result interpretation) are post-result. The boundary is
   placed at "before any pre-registered screen output observed at
   register-bearing register"; descriptive diagnostics that don't
   bear on pass/fail (e.g., Sharpe distribution percentiles,
   forward-traceability descriptors) do not constitute pre-registered
   screen output.

   **Trade-off acknowledged at this trigger boundary:** placing the
   boundary at end-of-Step-2 admits the case where input statistics
   are observed before patch (e.g., cross-trial Sharpe variance
   already computed). This trade-off is mitigated by Trigger 3 +
   Trigger 5: Trigger 3 forbids any pass/fail criterion change
   (so post-input-observation patches cannot change disposition
   threshold), and Trigger 5 forbids loosening parameters beyond
   the canonical-artifact register-precision floor (so
   post-input-observation patches cannot cherry-pick a
   result-favorable parameter). The boundary is liberal enough to
   admit canonical-artifact-precision corrections that surface at
   Step 2 input loading; conservative enough to forbid
   result-favorable tuning. See Failure-mode signal §20 for
   explicit warning on input-observation-before-patch caution.

2. **Structural infeasibility at canonical-artifact register**.
   The lockpoint cannot be satisfied by the canonical input register
   under literal application due to format / precision / encoding
   incompatibility verified at canonical-artifact register
   (filesystem inventory, schema introspection, format inspection).
   The infeasibility must be physical (storage-format-induced) or
   structural (schema-induced), not a judgment call about whether
   the lockpoint is "too strict." A lockpoint that is satisfiable
   by some canonical inputs but not others is NOT structurally
   infeasible — it produces an eligibility filter, not a
   by-construction exclusion of all inputs.

3. **No substantive pass/fail criterion changes**. The patch must
   not change any of: the canonical formula(s) at the spec; the
   pass/fail thresholds at sub-spec lockpoints; the AND-gate /
   OR-gate logic at result interpretation; the **substantive
   eligible-subset definition** (i.e., filters that produce a
   non-degenerate eligible subset under canonical-artifact register;
   e.g., trade-count filter `T_c < 5`); the canonical input
   source(s) at the primary computation register.

   **Boundary clarification (resolves Trigger 2 / Trigger 3
   non-contradiction):** when Trigger 2 is satisfied, the original
   lockpoint produces a *structurally degenerate* (100%-exclusion)
   eligibility filter — by construction it does not define a
   substantive eligible subset, so changing its binding action
   (e.g., from auto-exclude to reviewer-route) does not change the
   substantive eligible-subset definition. The patch operates at
   the binding-action register (what to do when a discrepancy
   surfaces under a structurally degenerate filter) or at the
   descriptive-register reframe layer, not at the substantive
   lockpoint layer. Trigger 3 protects substantive filters
   (non-degenerate; e.g., `T_c < 5`); Trigger 2 + Trigger 3 together
   guarantee that admissible patches operate only on the structurally
   degenerate subset.

4. **Full audit trail v* → v*.1**. The pre-patch lockpoint reading
   is preserved at canonical record. The "labeled commit pair" is
   defined as: (a) the v* sub-spec seal commit (canonical pre-patch
   reading); (b) the v*.1 patch commit (post-patch reading with
   inline `(v*.1 patch per §19 Instance N + §20 trigger
   verification)` annotations at every patch site). Deliverable
   records (Step deliverables citing v* and v*.1) preserve the
   adjudication trail at register-precision. The audit trail must
   allow a reader to reconstruct the v* canonical reading without
   recourse to git archaeology beyond the labeled commit pair.

5. **Patch parameter calibrated to canonical-artifact register-precision floor (parameter calibration discipline)**. The replacement parameter value (e.g., the new tolerance, the new precision threshold) is calibrated to the minimum register-precision required to address the structural infeasibility — i.e., empirically grounded in the canonical-artifact register-precision floor (storage-format precision, schema-encoded precision, or equivalent canonical-artifact-derived bound), NOT loosened beyond that floor for "more reasonable" or "future-flexibility" reasons.

   The calibration must be independently verifiable: a reader
   examining the canonical-artifact register and the patched
   parameter value should be able to confirm that the parameter
   value is the tightest bound that satisfies the infeasibility
   correction at the canonical register. Looser values (e.g., one
   or more orders of magnitude beyond the empirical floor) are
   forbidden under §20 — they implicate post-hoc result-favorable
   tuning even when Triggers 1-4 are satisfied. Successor cycle
   re-pre-registration is the path for parameter values that
   require justification beyond canonical-artifact-precision-floor
   matching.

### Application checklist

When a candidate in-arc patch surfaces:

1. Verify ALL FIVE trigger conditions hold at canonical-artifact
   register; if any fails, §20 does not apply; route to strict
   §0.4-style inconclusive disposition + successor cycle.
2. Surface the candidate patch + the five-trigger verification at
   reviewer-routing register. Both reviewers (ChatGPT structural +
   advisor substantive) must adversarially scrutinize all five
   triggers; reviewer convergence is necessary, not sufficient.
3. **Reviewer divergence path:** if reviewers do not converge after
   one or more substantive passes, §20 does NOT fire. Charlie-register
   adjudicates the divergence; only Charlie-register adjudication on
   the divergence (selecting reviewer position OR custom resolution)
   re-opens §20 fire eligibility. Without reviewer convergence
   achieved, the candidate patch defers to strict §0.4-style path.
4. Charlie-register authorization is canonical for operational
   fire per `feedback_authorization_routing.md`. Reviewer
   convergence alone does NOT authorize the patch.
5. **One patch per pre-registered lockpoint per arc** (binding
   constraint, not heuristic). Subsequent patches on the same
   lockpoint within the same arc defer to successor cycle
   re-pre-registration; §20 cannot be invoked for repeat patches
   at the same lockpoint within an arc. Multiple distinct lockpoints
   may each take one §20 patch within an arc; the constraint is
   per-lockpoint, not per-arc.
6. Patch sites carry explicit `(v*.1 patch per §19 Instance N + §20
   trigger verification)` annotations preserving v* canonical
   reading. Annotations cite the §19 instance number AND the
   §20 trigger satisfaction fact at register-precision.
7. Bundle: sub-spec patch commit + deliverable v2 commit + (if
   first instance under §20 register) METHODOLOGY_NOTES §20
   codification commit. The codification fires at first instance;
   subsequent instances log at §20.5 cumulative-instance register
   without re-codification.
8. Step gating: subsequent operational fires (Step 2 / Step 3 /
   etc.) AUTHORIZED POST-SEAL ONLY. The patch landing does not
   authorize the next step; Charlie-register seal authorization on
   the bundle does.

### Failure-mode signal

Watch for any of the following, which indicate misuse of §20:

- "The lockpoint is too strict; the result would be inconclusive
  if we applied it strictly" — this is the post-hoc adjustment
  defect class §0.4 forbids; §20 does not admit pragmatic-strictness
  arguments. Trigger 2 (structural infeasibility) requires
  by-construction exclusion of all inputs, not "more candidates
  excluded than the spec author intended."
- "Reviewers ratified the patch" without Charlie-register
  authorization — reviewer convergence is advisory only per
  `feedback_authorization_routing.md`. Application checklist item 4
  is the operational-fire gate.
- "We can patch this and document later" — the audit trail must
  be authored at the same arc as the patch (Trigger 4); deferring
  the audit annotation to a successor cycle erodes the
  reconstructability the trigger guarantees.
- "Step 3 has already partially fired; Step 1 verification surfaced
  the defect" — partial Step 3 firing implicates the post-result
  register; Trigger 1 fails. §20 does not apply; route to strict
  inconclusive disposition. (Trigger 1 boundary is end-of-Step-2;
  any Step 3+ output observed = post-result.)
- **"We saw the input statistics at Step 2 and that motivated the
  patch direction"** — even though Trigger 1 admits Step 2 as
  pre-result, Trigger 3 + Trigger 5 must be satisfied
  *independently of input observation*. Specifically: the patch
  must be derivable from canonical-artifact register-precision
  alone (Trigger 5), not from input-statistic-favorable selection.
  If a reviewer asks "would you have authored the same patch
  without seeing the Step 2 input statistics?" and the honest
  answer is no, the patch implicates the post-hoc-tuning defect
  class even if Trigger 1 surface-passes. Charlie-register
  adjudication required at this boundary case.
- "The new tolerance is more reasonable / industry-standard / a
  cleaner round number" — Trigger 5 forbids parameter calibration
  beyond canonical-artifact register-precision floor.
  "Reasonableness" arguments not grounded in the canonical-artifact
  register are post-hoc tuning. Successor cycle re-pre-registration
  is the path for parameter substance debates.
- "This is the second time we've patched this lockpoint" —
  Application checklist item 5 forbids repeat patches on the same
  lockpoint within an arc. Multiple in-arc patches suggest the
  lockpoint substance is unstable, which strict §0.4 covers via
  successor-cycle re-pre-registration.

### §20.5 Cumulative instance register

**Instance entry template (mandatory fields for each entry):**

(a) **Anchor citation:** arc + cycle + canonical-artifact register
    citation locating the lockpoint and the structural infeasibility.
(b) **Per-trigger verification:** explicit per-trigger
    verification at register-precision (T1 + T2 + T3 + T4 + T5;
    each trigger's satisfaction grounded in canonical-artifact
    register).
(c) **Reviewer convergence record:** ChatGPT lean + Claude advisor
    lean + convergence path (direct convergence / divergence
    adjudicated by Charlie-register).
(d) **Charlie-register authorization citation:** the canonical
    Charlie-register message authorizing the operational fire.
(e) **Patch-substance adjudication notes:** any substantive
    parameter / wording adjudication at register-precision (e.g.,
    parameter value selection rationale citing canonical-artifact
    register-precision floor).

---

**Instance 1 (this codification fire):** PHASE2C_11 v3 → v3.1 patch
slate, Instance 6 of §19 enumeration.

(a) **Anchor citation:** PHASE2C_11 implementation arc Step 1
    inventory cycle. Lockpoint: JSON-vs-CSV cross-validation
    tolerance at v3 §3.4 + §4.4(5) set at `|delta| > 1e-9`.
    Canonical-artifact register: `holdout_results.csv` at
    `data/phase2c_evaluation_gate/audit_v1/` stored at 6-decimal
    precision; physical max |delta| ≈ 5e-7 between CSV and JSON
    full-precision floats by CSV format construction.

(b) **Per-trigger verification:**
    - **T1 (pre-result):** Step 1 inventory only fired at patch
      author cycle; no Step 2 input loading, no Step 3 screen
      output, no Step 4 interpretation. Pre-result at strict
      end-of-Step-1 boundary (more conservative than the §20 T1
      end-of-Step-2 boundary). Anti-rationalization audit per §20
      Failure-mode signal honest test: a forward-traceability
      descriptor (Bonferroni threshold = 3.2522 + max observed
      Sharpe = 1.262) was computed and observed at Step 1
      verification cycle, but did NOT bear on patch direction —
      Instance 6 patch is canonical-artifact-precision-derived
      (CSV 6-decimal storage floor → 1e-6 calibration), not
      Sharpe-distribution-derived. The honest test "would the same
      patch have been authored without observing Step 1 descriptors?"
      passes at register-precision: yes, the structural infeasibility
      surfaces from CSV format inspection alone.
    - **T2 (structural infeasibility):** by-construction 100%
      exclusion of all 198 candidates under literal 1e-9
      application — every JSON-vs-CSV scalar pair has |delta| in
      [~0, ~5e-7] range due to CSV 6-decimal storage; literal 1e-9
      tolerance excludes every pair. Verified empirically at
      `/tmp/phase2c_11_step1_verify.py` cycle: 488 disagreements
      at 1e-9 register / 0 at 1e-6 register.
    - **T3 (no substantive pass/fail criterion changes):** formula
      lockpoints (Bonferroni `sqrt(2*ln(N))`; DSR-style p-value;
      Gumbel approximation), pass/fail thresholds (p < 0.05;
      Bonferroni at N=198), conservative AND-gate at §3.6,
      substantive eligible-subset filter (`T_c < 5` per §4.4(1)),
      JSON canonical scalar source per §3.3 — all unchanged. Patch
      operates at binding-action register (auto-exclude →
      reviewer-route) on a structurally degenerate filter
      (Trigger 2 satisfied), not on the substantive eligible-subset
      definition.
    - **T4 (full audit trail):** v3 seal commit `c5b740c` preserved
      as pre-patch canonical reading; v3.1 patch sites at §3.4
      line 224 + §4.4(5) line 350 carry inline annotations with
      §19 Instance N + §20 trigger verification citation.
      Step 1 deliverable v2 records adjudication trail at
      register-precision.
    - **T5 (canonical-artifact-precision-floor calibration):**
      replacement tolerance value 1e-6 selected as one order of
      magnitude above the empirical CSV 6-decimal storage floor
      (~5e-7). Independently verifiable: 1e-6 catches CSV storage
      rounding cleanly (max physical delta < 1e-6) without
      permitting genuine engine-output divergence (≥1e-6 surfaces
      for adjudication). Looser candidates (1e-5, 1e-3, "any
      reasonable tolerance") rejected at register-precision per
      `feedback_reviewer_suggestion_adjudication.md` — 1e-5 admits
      20× the empirical floor without justification at canonical
      register; 1e-3 admits 2000× and is post-hoc by construction.

(c) **Reviewer convergence record:**
    - Initial ChatGPT lean: option (b) reframing; tolerance "1e-6
      or 1e-5"; "would be too rigid; would waste the cycle".
    - Initial Claude advisor lean: R1 verify-first; option (b) lean
      if scenario A confirmed; substantive objection at register-
      precision — bare P2 weakens §0.4 anti-p-hacking guardrail at
      first ambiguous case; precedent doc bundle required for §0.4
      integrity.
    - Divergence path: ChatGPT → bare P2 (skip codification);
      Claude advisor → P2 + precedent doc (codify with explicit
      triggers); Claude Code substantive read converged with
      advisor on §0.4-integrity grounds.
    - Convergence achieved at second adjudication round: ChatGPT +
      Claude advisor + Claude Code aligned on P2 + precedent doc
      path.
    - §20 wording itself: ChatGPT structural pass + Claude advisor
      substantive pass on §20 v1 wording surfaced 5 substantive
      concerns (L1: T3/T2 internal contradiction; L2: T1 boundary
      placement; L3: missing T5 parameter calibration; L4:
      one-patch-per-lockpoint promotion to checklist; L5: 4 polish
      items). All 5 incorporated at §20 v2 (this codification).

(d) **Charlie-register authorization citation:** Charlie-register
    message ratified P2 + precedent doc path after advisor objection
    surfaced trichotomy P1 / P2+precedent-doc / bare-P2. Subsequent
    Charlie-register message ratified β path (final advisor pass
    on §20 wording + ChatGPT structural pass on full bundle, then
    seal). Subsequent Charlie-register message ratified incorporating
    advisor L1+L2+L3+L4+L5 fixes at §20 v2 ("approved on both
    reviewer synthesis β").

(e) **Patch-substance adjudication notes:** tolerance 1e-6 selected
    over 1e-5 per `feedback_reviewer_suggestion_adjudication.md`
    adjudication: empirical CSV storage floor ~5e-7 → 1e-6 sits one
    order of magnitude above (Trigger 5 satisfied); 1e-5 would sit
    20× above (Trigger 5 violated); 1e-9 (the v3 lockpoint) sits
    below empirical floor (Trigger 2 satisfied). §20 v2 incorporates
    advisor L1-L5 fixes per second-pass adjudication: T3 boundary
    clarification (resolves T2/T3 internal contradiction); T1
    boundary at end-of-Step-2 with explicit input-observation
    trade-off acknowledgment; T5 parameter calibration discipline
    added; one-patch-per-lockpoint promoted to Application checklist
    item 5; §20.5 instance template + tier-re-evaluation honesty +
    labeled commit pair definition + reviewer-divergence-path all
    polished.

---

Future instances log here at register satisfaction following the
mandatory entry template; tier re-evaluation (including potential
demotion if cumulative misuse pattern emerges, OR supersession if
alternative codification register supersedes §20) at successor
methodology consolidation cycle.

---

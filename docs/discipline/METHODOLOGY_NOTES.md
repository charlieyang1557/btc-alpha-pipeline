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

### §20.6 Strong-tier promotion bar criteria

This sub-§ codifies the Strong-tier promotion bar criteria refinement of EXISTING METHODOLOGY_NOTES §13-§20 tier framework per V#10 verification at scoping decision register; bar criteria specification at register-precision register-class binding for Strong-tier promotion from §13-§20 EXISTING tier hierarchy at refinement register-class binding (NOT new tier framework creation per sub-spec §4.3.5 anti-pattern explicit rejection). The discipline operates at refinement register-class scope binding distinct from per-instance / per-cycle catch-boundary cluster (§1 / §15 / §21 / §22 / §23 / §25 / §27) AND from cross-cycle accumulation observation cluster (§26 / §18 / §19 / §28 / §29) at content scope axis register-precision register-class binding — §20.6 is register-class-orthogonal to both clusters at content scope axis at register-precision register-class binding parallel to §29 register-class-orthogonality framing register precedent at register-class match register.

§20.6 operates at sub-§ register-class binding within parent §20 Strong-tier host slot per V#10 anchor binding; sub-§ register-class binding inherits parent §20 Strong-tier register-class precedent at register-class match register binding by construction at sub-spec §4.3.5 + F5 patch register binding. §20.6 codification at PHASE2C_13 implementation arc Step 9 register-event boundary = **bar criteria specification at refinement register only** at register-class match register binding NOT promotion executions per sub-spec §4.3.4 explicit guardrail at cycle-class-specific scope binding ("NO Strong-tier promotions authorized AT PHASE2C_13 cycle register"). §20.6 cross-references §28 + §29 sealed prose forward-references at "§20.2" sub-spec §5.4 disposition canonical binding source language at register-class match register binding (canonical artifact slot lands at §20.6 per (β) adjudication at Step 9 entry register-event boundary; sealed §§ prose preserved invariant per anti-momentum-binding).

§20.6 sub-§ register-class binding internal structure register-class-distinct from §21-§29 standalone-§ 4+1-subsection register precedent (Principle / Trigger context / Application checklist / Failure-mode signal / Tier disposition) at register-precision register-class binding; appendix-style sub-§ scope per §20.5 sub-§ register precedent at register-class match register binding admits register-class flexibility at internal structure register-class binding scope by construction at sub-spec §4.3.5 + (β) adjudication binding. §20.6 internal structure (Bilingual concept anchor + Bar criteria 1-4 enumeration + (C-1) candidates enumeration framework + §4.3.3 re-check application reference + §4.3.4 cycle-class-specific scope binding + Tier disposition + Forward+Backward references) register-class-coherent under appendix-style sub-§ register-class binding scope at register-class match register binding to §20.5 sibling sub-§ register precedent.

**Bilingual concept anchor (per discipline anchor #10 — Strong-tier bar codification IS difficult methodology concept):**

- **English:** Carry-forward C does TWO things. (C-1) lists candidate observations from cross-cycle accumulation that MIGHT deserve Strong-tier status (the highest tier in METHODOLOGY_NOTES at §20-style register reflecting binding operating rule). (C-2) codifies the BAR for Strong-tier promotion — what specific criteria a candidate must meet. PHASE2C_13 sub-spec defines the bar criteria; does NOT promote candidates to Strong-tier (promotion executions happen at implementation arc § seal or later cycle). The bar codification is REFINEMENT of EXISTING tier framework (Weak/Medium/Strong tiers at METHODOLOGY_NOTES §13-§20 already exist per V#10), NOT new framework creation.
- **中文:** Carry-forward C 做两件事。(C-1) 列出 cross-cycle 累积的 candidate observations 可能 deserve Strong-tier (METHODOLOGY_NOTES §20 风格的最高 tier, 反映 binding operating rule)。(C-2) codify Strong-tier promotion 的 bar (具体 criteria 一个 candidate 必须满足)。PHASE2C_13 sub-spec 定义 bar criteria; 不 promote candidates 到 Strong-tier (promotion execution 在 implementation arc § seal 或 later cycle)。Bar codification 是 REFINEMENT of EXISTING tier framework (Weak/Medium/Strong tiers at METHODOLOGY_NOTES §13-§20 已存在 per V#10), 不是 new framework 创造。

(Bilingual anchor cited verbatim from sub-spec §4.3 source artifact register lines 514-517 per §22 Failure-mode signal item 7 description-drift discipline binding; canonical binding source preserved at sub-spec source register-class match register.)

#### Strong-tier promotion bar criteria 1-4 (AND-conjoined necessary conditions)

ALL FOUR criteria below must hold AND-conjoined for Strong-tier promotion at successor methodology consolidation cycle scoping cycle register-event boundary. Single-criterion failure = candidate stays at Medium tier (per §18 register-class precedent) OR Weak tier (per §19 register-class precedent if criterion 2 operating-rule-articulation fails).

**Criterion 1 — Minimum cross-cycle instance count threshold (necessary).** Strong-tier promotion requires ≥10 instances accumulated across ≥3 PHASE2C cycles (cycle-class register-class-distinct from sub-cycle-phase register; e.g., PHASE2C_12 sub-spec drafting + Step 1 + Step 2 + closeout = 1 cycle for cross-cycle counting purposes at register-class match register binding). Rationale anchor at register-precision register-class binding: Medium-tier at METHODOLOGY_NOTES §18 ships at 4/4 PHASE2C interpretive arc closeout saturation register per §18 codification register binding — Medium tier requires saturation evidence at observation pattern register-class binding; Strong tier at §20 ships at single binding operating rule register per §20 Tier Strong line 2547 codification register binding (one precedent instance at PHASE2C_11 v3 → v3.1 Instance 6 register-class binding). Bar at "≥10 instances + ≥3 cycles" sets register-class-distinct threshold reflecting cross-cycle operating-rule-articulating pattern beyond observation saturation at register-class match register binding. **Threshold values locked at Q-S81 Charlie register adjudication at § seal pre-fire register-event boundary (Option (i) APPROVE-as-stated):** instance count threshold = ≥10 (anchor: PHASE2C_12 §19 = 10 single-cycle baseline at canonical-artifact register-precision register; cross-cycle pattern at 10+ cumulative across cycles implies saturation across cycles at register-class match register binding); cycle count threshold = ≥3 (anchor: minimum cross-cycle for "pattern" vs "single-cycle anomaly" register-class distinction at register-precision register-class binding).

**Criterion 2 — Mitigation-strategy-specifiable as necessary condition (necessary).** Strong-tier promotion requires concrete operating rule articulation at register-precision register-class binding (NOT observation-only framing). Operating rule must specify at register-class match register binding: WHEN the rule applies (Trigger context register-class); WHAT the rule prescribes (Application checklist register-class); HOW to recognize rule violation (Failure-mode signal register-class). Rationale anchor at register-precision register-class binding: METHODOLOGY_NOTES §20 codification of pre-result lockpoint mis-specification exception path is concrete operating rule at register-class binding (5 trigger conditions individually necessary jointly sufficient + Application checklist 8 items + Failure-mode signal 7 watch-for paragraphs at register-precision register); METHODOLOGY_NOTES §19 codification of §19 finding pattern is observation-only at Weak tier register-class binding (no operating rule articulation at register-class match register binding). Distinction at operating-rule-articulating vs observation-only register-class is the bar criterion 2 anchor at register-precision register-class binding. **Application:** candidate observation that has cross-cycle saturation evidence (criterion 1 ✓) but NO operating rule articulation = Medium tier (per §18 register-class precedent at register-class match register binding), NOT Strong tier at register-class binding.

**Criterion 3 — Cross-cycle register-class consistency requirement (necessary).** Strong-tier promotion requires register-class consistency at observation pattern across cycles at register-class match register binding (e.g., §19 spec-vs-empirical-reality consistently surfaces at sub-spec drafting register vs. inconsistent register-class assignment across cycles). Cross-cycle register-class consistency anchors the operating-rule-articulating disposition (criterion 2) at register-class match register binding. Rationale anchor at register-precision register-class binding: Item 6 §9.0c register-class taxonomy 3-class sub-rule explicitly requires register-class-distinct counting + register-class-distinct mitigation at register-class binding per §26 codification register binding; same discipline applies to Strong-tier candidate evaluation at register-class match register binding. **Application:** candidate with 20 cumulative cross-cycle instances but 10 at sub-spec drafting register + 5 at authorization register + 5 at reviewer register may NOT satisfy criterion 3 at register-class match register binding (heterogeneous register-class distribution at register-precision register-class binding); single-register-class concentration (e.g., 18 at sub-spec drafting + 2 at others) satisfies criterion 3 at register-class match register binding.

**Criterion 4 — Exit criteria from Weak/Medium tier register (necessary).** Strong-tier promotion requires the candidate observation has been at Weak or Medium tier for ≥1 prior consolidation cycle at register-class match register binding (NOT direct Weak→Strong promotion at single cycle). Maturation through tier hierarchy ensures cross-cycle pattern stability at register-class match register binding. Rationale anchor at register-precision register-class binding: METHODOLOGY_NOTES §13-§20 tier hierarchy reflects maturation register at register-class binding (Weak observation-only → Medium operating-rule-pending → Strong operating-rule-articulated); bypass of intermediate tier corrupts maturation evidence at promotion register at register-class match register binding. **Application:** candidate first observed at PHASE2C_13 cycle (e.g., Item 7 anti-meta-pattern discipline at §27 codification register-class binding) cannot promote to Strong tier at PHASE2C_13 at register-class match register binding; candidate must enter at Weak tier observation-only initially + accumulate cross-cycle evidence at criterion 1 register binding + promote to Medium at later cycle at register-class match register binding + eventually Strong if criteria 1-3 met at register-class match register binding. **Threshold value locked at Q-S81 Charlie register adjudication at § seal pre-fire register-event boundary (Option (i) APPROVE-as-stated):** maturation cycle count threshold = ≥1 prior consolidation cycle (anchor: minimum maturation register-event boundary for cross-cycle pattern stability evidence at register-precision register-class binding).

**Criterion 1 + Criterion 4 threshold values lock at Q-S81 § seal pre-fire register-event boundary at register-class match register binding:** values cited above (C1 ≥10 instances + ≥3 cycles; C4 ≥1 prior consolidation cycle) locked at Q-S81 Charlie register adjudication at § seal pre-fire boundary parallel to §28 Q-S71 threshold values + §29 Q-S76 disposition register precedent at register-class match register binding (Option (i) APPROVE-as-stated); locked values bind §20.6 as canonical bar criteria at register-precision register-class binding scope. Criteria 2 + Criterion 3 register-class-distinct from numeric threshold register binding (Criterion 2 = operating-rule-articulation requirement at qualitative register-class binding; Criterion 3 = cross-cycle register-class consistency requirement at qualitative register-class binding) — not subject to Q-S81 numeric threshold adjudication at register-class match register binding.

**Strong-tier bar AND-conjunction at register-precision register-class binding:** ALL FOUR criteria must hold AND-conjoined for Strong-tier promotion at successor methodology consolidation cycle scoping cycle register-event boundary at register-class match register binding. Single criterion failure = candidate stays at Medium tier (per §18 register-class precedent at register-class match register binding) OR Weak tier (per §19 register-class precedent at register-class match register binding if criterion 2 fails — operating rule articulation absent at register-precision register-class).

#### (C-1) Strong-tier promotion candidates enumeration framework

Per sub-spec §4.3.1 + scoping decision §6.6 verbatim source binding (cited verbatim from canonical source artifact register per §22 description-drift discipline binding), 4 candidates surfaced from cross-cycle accumulation register at PHASE2C_13 sub-spec drafting cycle entry register-event boundary at register-precision register-class binding:

**Candidate 1 — §19 spec-vs-empirical-reality finding pattern broad anti-meta-pattern application.**
- Current tier per METHODOLOGY_NOTES §19 codification register binding: Weak tier observation-only with cross-cycle-pending status note at register-class match register binding.
- Cross-cycle accumulation evidence at register-precision register-class binding: 20 instances cumulative cross-cycle since PHASE2C_9 per CLAUDE.md PHASE2C_12 SEAL entry verbatim (canonical-artifact register-precision register).
- Strong-tier promotion rationale at register-class match register binding: 20-instance cumulative across 4+ cycles (PHASE2C_9 + PHASE2C_10 + PHASE2C_11 + PHASE2C_12) demonstrates pattern saturation at register-precision register-class binding (criterion 1 ✓ at provisional threshold); mitigation strategy specifiable at register-class binding (real-time logging + boundary-fire mitigation review per Item 7 (a)+(c) operationalization broadened to §19 per Q-S27a Reading (iii) advisor lean per scoping decision §6.6 + sub-spec §2.7 codification at §27 register-class binding).
- Strong-tier promotion blocker at register-class match register binding: **Even where Criterion 1 appears satisfied at provisional threshold register binding (20-instance cumulative ≥ 10 + 4 cycles ≥ 3 ✓), Criterion 4 maturation requirement (≥1 prior consolidation cycle) blocks PHASE2C_13 promotion by construction at register-class match register binding** — PHASE2C_13 IS first consolidation cycle codifying §19 broad anti-meta-pattern application at register-class match register binding so candidate fails criterion 4 at PHASE2C_13 register by construction at register-class binding scope; Q-S27a Charlie register adjudication required at register-event boundary for Reading (iii) §19 inclusion in Item 7 broadening at register-class binding scope; PHASE2C_14+ consolidation cycle adjudication boundary at register-class match register binding for Strong-tier promotion candidacy.

**Candidate 2 — §9.0c process-design observation density pattern.**
- Current tier per METHODOLOGY_NOTES § codification at PHASE2C_13 implementation arc register binding: Item 6 § slot at §26 codification register-class binding (sealed at `6e80950` Step 5 SEAL register); Item 7 § slot at §27 codification register-class binding (sealed at `0453a31` Step 6 SEAL register).
- Cross-cycle accumulation evidence at register-precision register-class binding: 8 instances at PHASE2C_12 cycle alone per canonical-artifact register; cross-cycle backfill at §28 codification register binding 5-cycle table at PHASE2C_8.1=n/a / PHASE2C_9=n/a / PHASE2C_10=n/a / PHASE2C_11=n/a / PHASE2C_12=8 register-precision (§9.0c register first-surface at PHASE2C_12 cycle per §28 5-cycle backfill register-class binding).
- Strong-tier promotion rationale at register-class match register binding: pattern is direct subject of Item 6 + Item 7 codification at PHASE2C_13 implementation arc at register-class binding; Item 6 + Item 7 codification operating-rule-articulating at register-class match register binding (criterion 2 ✓ at register-precision register-class binding); 3-class register-class taxonomy sub-rule operationalized at §26 + §3 fold-in register-class binding (criterion 3 ✓ at register-class match register binding).
- Strong-tier promotion blocker at register-class match register binding: cross-cycle accumulation evidence at §28 5-cycle backfill register binds 8 instances at single PHASE2C_12 cycle only (criterion 1 ✗ at < 10 instances + < 3 cycles register-precision); criterion 4 maturation requirement (≥1 prior consolidation cycle) — PHASE2C_13 IS first consolidation cycle codifying §26 + §27 register-class binding so candidate fails criterion 4 at PHASE2C_13 register; PHASE2C_14+ consolidation cycle adjudication boundary at register-class match register binding for Strong-tier promotion candidacy.

**Candidate 3 — M7 register-class-compromise (same-agent fresh-register full-file pass) cross-cycle pattern.**
- Current tier per METHODOLOGY_NOTES §17 codification register binding: §17 sub-rule 4 has Strong-tier-like operational force at register-class match register binding (recursive operating rule pattern empirically validated cross-cycle at 12 consecutive cycles register binding per §17 codification register); Candidate 3's empirical pattern (same-agent fresh-register full-file pass cross-cycle observation) is NOT itself promoted by implication at register-class match register binding — Candidate 3 register-class-distinct from §17 sub-rule 4 codification register at content scope axis register-precision register-class binding (§17 sub-rule 4 = recursive operating rule at full-file pass discipline register-class binding; Candidate 3 = cross-cycle empirical observation pattern at register-class-compromise register-class binding); cross-cycle empirical operation pattern observation-only at scoping cycle register-class binding.
- Cross-cycle accumulation evidence at register-precision register-class binding: 2 instances cross-cycle (PHASE2C_12 sub-spec drafting cycle + PHASE2C_12 scoping cycle at register-class match register binding); §A1 instance #1 at PHASE2C_13 sub-spec drafting cycle entry register-class-similar at register-precision register-class binding.
- Strong-tier promotion rationale at register-class match register binding: §17 sub-rule 4 already codified at Strong-tier-class register-class binding (12 consecutive cycles of recursive operating rule pattern empirically validated cross-cycle per §17 codification register binding); cross-cycle empirical pattern observation may codify as additional sub-rule or §-entry at successor methodology consolidation cycle.
- Strong-tier promotion blocker at register-class match register binding: 2-instance cross-cycle accumulation thin at register-precision register-class binding (criterion 1 ✗ at < 10 instances register-precision); promotion candidate is observation pattern register-class binding vs new operating rule register-class binding; fold-in to existing §17 register-class likely over new-§ creation at register-class match register binding.

**Candidate 4 — Q10/M6-F2 healthy reasoned-adjudication cycle pattern.**
- Current tier: not codified at canonical artifact register; cross-cycle observation only at register-class match register binding.
- Cross-cycle accumulation evidence at register-precision register-class binding: 2 PHASE2C_12 instances per CLAUDE.md PHASE2C_12 SEAL entry verbatim + cumulative across cycles at register-class match register binding (Step 1 Q-S40 + Step 5 Adv F3 + Step 6 C1 + Step 7 C4 + Step 9 entry §20-scope-overreach correction + Step 9.4a mixed-disposition register-class incoherence = 6 PHASE2C_13 cycle internal instances at register-precision register-class binding through Step 9.4a closure register-event boundary).
- Strong-tier promotion rationale at register-class match register binding: pattern reflects substantive reviewer divergence → per-ground substantive verify → adjudicated convergence at Charlie register binding (NOT bulk-accept register-class binding).
- Strong-tier promotion blocker at register-class match register binding: codification overlaps with `feedback_reviewer_suggestion_adjudication.md` memory at register-class binding; redundant codification at METHODOLOGY_NOTES register if memory already binds at register-class match register binding; promotion is not register-class-distinct from existing memory binding at register-precision register-class binding.

**Candidate enumeration summary at register-class match register binding:** 4 candidates surfaced at register-precision register-class binding; promotion to Strong-tier requires (C-2) bar criteria 1-4 AND-conjoined check + Charlie register adjudication at promotion register-event boundary (post-PHASE2C_13 implementation arc § seal for each candidate at successor methodology consolidation cycle scoping cycle register-event boundary). PHASE2C_13 sub-spec scope = enumeration only at register-class binding; promotion executions OUT-OF-SCOPE per scoping decision §1.4 + sub-spec §4.3.4 binding (cycle-class-specific scope at register-class match register binding).

#### §4.3.3 §2.1-§2.7 + sub-rule + Carry-forwards re-check application reference

Per sub-spec §4.3.3 binding at register-class match register, §2.1-§2.7 Items 1-7 + sub-rule + Carry-forwards A/B/C provisional tier dispositions re-checked against §4.3.2 bar codification at register-precision register-class binding. **Re-check pass at PHASE2C_13 cycle empirical evidence basis register-class binding:**

| Item | §2.x provisional | Criteria check at register-precision | Final tier at PHASE2C_13 cycle register |
| ---- | --------------- | ------------------------------------ | -------------------------------------- |
| Item 1 (§2.1) | Medium tier | C1: 4 PHASE2C_12 instances (single-cycle); cross-cycle accumulation pending Carry-forward A backfill at register-precision; C4: 0 prior consolidation cycle FAILS C4 at register-class match register binding | Medium tier (cross-cycle accumulation pending; promotion path Medium → Strong contingent on PHASE2C_14+ at register-class match register binding) |
| Item 2 (§2.2) | Strong candidate | C1: 4 PHASE2C_12 instances at single-cycle; cross-cycle pending. C2: operating rule articulating (framework parameter audit) ✓. C3: pending backfill. C4: 0 prior consolidation cycle FAILS C4 at register-class match register binding | Medium tier (FAILS C4 maturation criterion at first codification cycle register binding; promotion path Medium → Strong contingent on PHASE2C_14+ cross-cycle accumulation + maturation cycle at register-class match register binding) |
| Item 3 (§2.3) | Medium tier | C1: 1 PHASE2C_12 instance only (sparse); cross-cycle very thin at register-precision register-class binding | Weak tier observation-only with cross-cycle-pending status note (sparse evidence at PHASE2C_12 single-instance register fails C1 ≥10 instances threshold at register-class match register binding; aligns with METHODOLOGY_NOTES §19 Weak-tier register precedent for thin-evidence-basis observation patterns at register-class match register binding) |
| Item 4 (§2.4) | Medium-to-Strong | C1: pending; C2: operating rule articulating (executable verification function) ✓. C3: Item 4 register-class likely fold-in to Item 2 § scope per §5 fold-in 4-criteria; promotion via Item 2 § path at register-class match register binding | Medium tier candidate via Item 2 fold-in path at register-class match register binding (final disposition at §22 codification register binding) |
| Item 5 (§2.5) | Strong candidate | C1: 1 PHASE2C_12 instance; cross-cycle reviewer over-interpretation pattern likely accumulates per scoping decision §10.6. C4: 0 prior cycle — FAILS C4 at register-class match register binding | Medium tier (FAILS C4 maturation criterion at first codification cycle register binding; promotion path Medium → Strong contingent on PHASE2C_14+ at register-class match register binding) |
| Item 6 (§2.6) | Strong candidate | C1: 8 PHASE2C_12 instances (single-cycle baseline); cross-cycle pending. C2: operating rule articulating (continuous-vs-batch + 3-class taxonomy) ✓. C3: 3-class taxonomy already operationalized; cross-cycle pending. C4: 0 prior cycle — FAILS C4 at register-class match register binding | Medium tier (FAILS C4 maturation criterion at first codification cycle register binding; promotion path Medium → Strong contingent on PHASE2C_14+ at register-class match register binding) |
| Item 7 (§2.7) | Weak observation-only | C1: 1 PHASE2C_13 instance (initial); cross-cycle pending. C4: 0 prior cycle — FAILS C4 at register-class match register binding | Weak tier observation-only (per §2.7 initial disposition at register-class match register binding; bar criteria confirm Weak placement at register-precision register-class binding; promotion path Weak → Medium at PHASE2C_14 + Medium → Strong at PHASE2C_15+ at register-class match register binding) |
| Carry-forward A (§28) | Medium-tier with cross-cycle-pending | C1: 5-cycle backfill empirical fire register; C2: operating rule articulating ✓ at canonical metric set + threshold specification; C3: cross-cycle register-class consistency pending; C4: 0 prior consolidation cycle FAILS C4 at register-class match register binding | Medium tier with cross-cycle-pending status note (per §28 Tier disposition register-class binding sealed at `906e398` Step 7 SEAL register at register-class match register binding) |
| Carry-forward B (§29) | Medium-tier with cross-cycle-pending | C1: single-cycle empirical at PHASE2C_12 cycle 4 framework-code commits + §28 5-cycle backfill data feed at criteria (i)+(iv); C2: operating rule articulating ✓ at evaluation methodology + 4-pattern enumeration + 4-criteria + 3-disposition outcome; C3: cross-cycle register-class consistency pending; C4: 0 prior consolidation cycle FAILS C4 at register-class match register binding | Medium tier with cross-cycle-pending status note (per §29 Tier disposition register-class binding sealed at `af6fa7b` Step 8 SEAL register at register-class match register binding) |
| Carry-forward C (§20.6) | bar criteria specification at refinement register | (Carry-forward C codifies bar criteria at this §20.6 register; not subject to re-check at this register since §20.6 IS the bar codification register-class binding by construction at register-class match register binding) | bar criteria specification at refinement register-class binding at register-precision register-class binding (sub-§ register-class binding inherits parent §20 Strong-tier register-class precedent; §20.6 itself is bar specification register-class NOT promotion candidate register-class at register-class match register binding) |

**Re-check summary at register-class match register binding:** All 7 Items + sub-rule + Carry-forwards A/B downgrade to Medium tier or lower at PHASE2C_13 sub-spec register binding (none meet Criterion 4 maturation requirement at first codification cycle register binding at register-precision register-class binding). Strong-tier promotions OUT-OF-SCOPE for PHASE2C_13 per sub-spec §4.3.4 cycle-class-specific scope binding + criterion 4 maturation requirement failure by construction at first codification cycle register binding. Promotion path Medium → Strong established for each Item via PHASE2C_14+ cross-cycle accumulation evidence at Carry-forward A backfill feeding promotion candidate review at successor methodology consolidation cycle at register-class match register binding.

#### §4.3.4 cycle-class-specific scope binding (NO Strong-tier promotions at PHASE2C_13 register)

Per sub-spec §4.3.4 binding explicit at register-class match register binding: PHASE2C_13 sub-spec defines Strong-tier promotion CRITERIA only at register-precision register-class binding; does NOT promote any candidate to Strong-tier inside the sub-spec at register-class binding. Promotion executions are OUT-OF-SCOPE at PHASE2C_13 register entirely at register-class match register binding.

**No Strong-tier promotions authorized AT PHASE2C_13 cycle register (binding; cycle-class-specific scope at register-class match register binding):** §4.3.3 re-check pass empirically validates ALL 7 Items + sub-rule + Carry-forwards downgrade to Medium tier or lower per criterion 4 maturation requirement failure (every candidate has 0 prior consolidation cycle at PHASE2C_13 first codification register at register-precision register-class binding); criterion 4 failure by construction at first codification cycle precludes any Strong-tier promotion at PHASE2C_13 implementation arc § seal register at register-class match register binding.

**Implementation arc § seal scope for bar criteria checks (PHASE2C_13 cycle scope only at register-class match register binding):** at each PHASE2C_13 implementation arc § seal authoring (Items 1-7 + sub-rule + Carry-forwards A/B/C), record bar criteria check outcome at register-precision register-class binding (which criteria pass / fail; cross-cycle accumulation pending state at register-class match register binding); RECORD ONLY at register-class binding — no promotion execution authorized at PHASE2C_13 register at register-class match register binding. Promotion register-event boundary fires at PHASE2C_14+ consolidation cycle if cross-cycle accumulation evidence + maturation cycle satisfies all 4 criteria for any candidate at register-class match register binding.

**Out-of-scope register binding (cycle-class-specific at register-class match register binding):** Strong-tier promotion executions register-class-distinct from PHASE2C_13 sub-spec drafting cycle SEAL boundary AND from PHASE2C_13 implementation arc § seal boundaries at register-precision register-class binding.

**Anti-momentum-binding cross-cycle scope preservation per sub-spec §4.3.4 F3 patch register binding (cycle-class-distinct authorization preservation at register-class match register binding):** the no-Strong-tier-promotions binding above scopes EXPLICITLY to PHASE2C_13 cycle register only at register-class match register binding. PHASE2C_14+ consolidation cycle register-class-distinct authorization decision is NOT pre-bound at PHASE2C_13 register at register-precision register-class binding — at PHASE2C_14 cycle entry register-event boundary, candidates codified at PHASE2C_13 satisfy criterion 4 (PHASE2C_13 = prior consolidation cycle for cross-cycle counting purposes at register-class match register binding); PHASE2C_14 may authorize Strong-tier promotion for any candidate satisfying all 4 bar criteria 1-4 AND-conjoined per Charlie register adjudication at PHASE2C_14 promotion register-event boundary at register-class match register binding. Promotion authorization at future cycles is register-class-distinct decision per cycle scoping cycle adjudication at register-precision register-class binding; PHASE2C_13 cycle binding does NOT carry forward as blanket future-cycle bind at register-class match register binding. Anti-momentum-binding strict reading: PHASE2C_13 cycle binding is cycle-class-specific register-class boundary at register-class match register binding, NOT cross-cycle authorization sealing at register-precision register-class binding. Anti-pre-naming preserved (no PHASE2C_14 specific scope pre-commitment at PHASE2C_13 register at register-class match register binding; only authorization-class boundary preservation at register-class-distinct cross-cycle decision register at register-precision register-class binding).

#### Tier disposition

§20.6 ships at **sub-§ register-class binding within parent §20 Strong-tier host slot per V#10 anchor binding** at register-precision register-class binding. §20.6 sub-§ register-class binding inherits parent §20 Strong-tier register-class precedent at register-class match register binding by construction at sub-spec §4.3.5 + F5 patch register binding; §20.6 itself = bar criteria specification at refinement register-class binding NOT a new-§ Tier disposition (sub-§ register-class binding distinct from new-§ Tier disposition register at Steps 1-8 register precedent at register-class match register binding).

§20.6 register-class-precedent-coupling with §20.5 sub-§ register-class binding at appendix-style sub-§ register precedent at register-class match register binding (§20.5 = Cumulative instance register at appendix register-class binding; §20.6 = Strong-tier promotion bar criteria at appendix register-class binding); both §20.5 + §20.6 register-class-coherent under parent §20 principle "Strong tier register" at register-class match register binding by construction at sub-§ register-class binding scope. §20 EXISTING 4-subsection content body (Principle / Trigger context / Application checklist / Failure-mode signal at lines 2558-2772 register-precision register) + §20.5 Cumulative instance register at line 2774 + Instance 1 PHASE2C_11 v3 → v3.1 codification fire register-class binding at register-precision register-class — all preserved invariant per V#10 anchor binding at register-class match register binding by construction at (β) adjudication at Step 9 entry register-event boundary (corrects sub-spec §4.3.5 prescribed §20.1 + §20.2 split structure at register-precision register-class binding; canonical artifact slot lands at §20.6 preserving §20 EXISTING content invariant at register-class match register binding).

§20.6 register-class-orthogonal to §1 / §15 / §21 / §22 / §23 / §25 / §27 per-instance / per-cycle catch-boundary cluster + §26 / §18 / §19 / §28 / §29 cross-cycle accumulation observation cluster at content scope axis register-precision register-class binding — refinement-of-existing-tier-framework register at §13-§20 tier hierarchy refinement scope per V#10 anchor at register-class match register binding (parallel to §29 register-class-orthogonality framing register precedent at register-class match register binding).

**Promotion path framing (anti-pre-naming preserved at canonical-artifact register binding per §28 + §29 register precedent at register-class match register binding):** specific future-cycle scope (cycle name + count from PHASE2C_13 forward) NOT pre-committed at canonical-artifact register binding at register-class match register binding; "successor methodology consolidation cycles after sufficient accumulation" framing preserves anti-pre-naming discipline binding at register-class match register binding. Bar criteria 1-4 AND-conjoined check + Charlie register adjudication at promotion register-event boundary at successor methodology consolidation cycle scoping cycle register-event boundary at register-class match register binding for any candidate at register-class binding.

#### Forward-references + backward-references at register-precision register-class binding

**Forward-references at register-precision register-class binding** (cite sub-spec §5.4 disposition canonical binding source language per Step 1 §21 F2 patch + Step 2 §22 + Step 3 §23 + Step 4 §25 + Step 5 §26 + Step 6 §27 + Step 7 §28 + Step 8 §29 register precedent at register-class match register binding): future cycle promotion executions at successor methodology consolidation cycle scoping cycle register-event boundary cite §20.6 bar criteria 1-4 AND-conjoined check + §4.3.3 re-check application + §4.3.4 cycle-class-specific scope binding at register-class match register binding.

**Backward-references at register-precision register-class binding cite sealed §§ at register-class match register binding:** §13-§20 EXISTING tier framework per V#10 anchor at register-precision register-class binding (§13-§17 + §18 Medium tier + §19 Weak tier + §20 Strong tier register at register-precision register-class binding); §16 (anchor-prose-access discipline) + §17 (procedural-confirmation defect class with sub-rule 4 recursive operating rule at 12 consecutive cycles register binding) + §18 (§7 carry-forward density at interpretive arc closeout register at Medium tier register-class precedent register binding) + §19 (spec-vs-empirical-reality drift register at Weak tier register-class precedent register binding) + §20 (Strong-tier register precedent at parent § register-class binding; §20.6 sub-§ register-class binding inherits parent §20 Strong-tier register-class precedent at register-class match register binding) + §20.5 (Cumulative instance register sub-§ at appendix register-class precedent register binding) + §21 (fire-prep precondition checklist) + §22 (framework parameter pre-lock at sub-spec terminus + Item 4 fold-in sub-rule 4a/4b/4c) + §23 (inter-step contract standardization) + §25 (register-class explicit declaration at Step deliverable) + §26 (§9.0c instance density + register-class taxonomy preservation + §3 sub-rule fold-in items 2+3+4) + §27 (Item 7 anti-meta-pattern discipline at methodology consolidation cycles with boundary clause invariance) + §28 (multi-metric cycle-complexity scaling diagnosis at canonical metric set scope register + 5-cycle backfill data feed) + §29 (framework architectural refactor evaluation at analysis register + 4-pattern enumeration + 4-criteria + 3-disposition outcome). Sealed §§ available at register-precision register-class binding at PHASE2C_13 implementation arc Step 9 entry register-event boundary; backward-reference language at register-class match register precedent at PHASE2C_13 implementation arc register-class binding.

---

---

## §21 Fire-prep precondition checklist discipline at multi-step implementation arc Step boundaries

### Principle

Multi-step implementation arc fire boundaries — Step 5 main fire, Step
6.5 walk-forward backtest, Step 7 evaluation gate, Step 8 mechanical
disposition fire, and other Step boundaries that exercise sub-spec
Q-LOCKED parameters against framework code at runtime — require
mechanical pre-fire precondition checklist verification before fire
authorization. The checklist traces each Q-LOCKED parameter at the
sub-spec lock register against the framework code site at fire-time
and against fire-time empirical state. Without an explicit precondition
checklist, divergence between sub-spec lock and framework code state
surfaces late, typically at ad hoc fire-prep, fire-time, or post-fire
empirical observation register, where it manifests as §19 spec-vs-
empirical-reality instance class plus auth-iteration overhead.

The discipline operates at a register distinct from §1 empirical
verification for factual claims and §15 anchor-list empirical
verification at the receiving cycle. §1 covers general empirical
verification of factual claims at any drafting register. §15 covers
pre-drafting anchor verification at the receiving cycle — anchors
arriving from advisor cycles, scoping decisions, or prior register
entries verified against canonical artifacts before drafting initiates.
§21 covers **pre-fire mechanical verification at the implementation
arc Step boundary** — once a sub-spec Q-LOCKED parameter set is sealed
and a Step is about to fire against framework code, each Q-LOCKED
parameter is mechanically traced from sub-spec lock to framework code
site to fire-time runtime state, and the trace passes before fire
authorization. The three disciplines are complementary: §1 catches
defects at any drafting register; §15 catches defects at anchor receipt
boundary; §21 catches defects at fire-prep boundary specifically.

### Trigger context

This discipline was operationalized across four PHASE2C_12 cycle
instances per closeout §10.2 enumeration ("Step 6.5 WF lineage +
framework N mismatch + sensitivity table N_eff + ALLOWED_DUAL_GATE_PAIRS
asymmetry"); each instance exhibited Q-LOCKED-vs-framework-code
divergence resolved through ad hoc rather than systematic mechanical
verification:

1. **Step 6.5 walk-forward lineage gap.** PHASE2C_12 Step 6.5 WF
   backtest fired against 197 candidates corrected-engine walk-forward
   (artifacts at `data/phase2c_12_wf/_corrected/`; per closeout §11.2).
   The WF lineage attestation guards (`check_wf_semantics_or_raise()` /
   `check_evaluation_semantics_or_raise()` in `backtest/wf_lineage.py`;
   per closeout §11.4) are present at framework code. PHASE2C_12
   closeout §10.2 enumerates "Step 6.5 WF lineage" as a fire-time
   precondition gap class; a systematic pre-fire mechanical trace of
   the WF lineage attestation domain at the Step 6.5 fire-prep boundary
   would have substituted procedural verification for ad hoc detection.

2. **Framework N mismatch (Q3 LOCKED 198 vs actual 197 valid).**
   PHASE2C_12 sub-spec Q3 locked N=198 (canonical baseline `b6fcbf86`
   total_valid_count). At Step 8 fire-prep boundary, eligible-count
   resolved to N=197 (one candidate dropped at `rejected_complexity` at
   position 75; per closeout §8.1 §19 instance #7). Resolution was ad
   hoc: `PHASE2C_12_N_RAW = 197` constant + paired-pair allowlist at
   commit `8887651`. A pre-fire trace of Q3 → eligibility filter
   resolution → fire-time N-count would have substituted procedural
   verification for ad hoc detection.

3. **Sensitivity table N_eff parameterization gap.** PHASE2C_12
   sub-spec Q15 [REVISED] specified N_eff `{198, 80, 40, 6}` at "number
   of operational themes" register. Framework hardcoded
   `{198, 80, 40, 5}` at the prior 5-themes anchor. The 6-vs-5
   divergence surfaced at Auth #6.x extension fire-prep iteration (per
   closeout §8.1 §19 instance #8); resolution was the cycle-conditional
   `_resolve_n_eff_set()` resolver at commit `995fdb2`. Like instance 2,
   caught at fire-prep through ad hoc patching rather than systematic
   verification.

4. **ALLOWED_DUAL_GATE_PAIRS parallel-structure incompleteness.**
   PHASE2C_12 Auth #6.x β1 narrow added (197, 197) to the
   `ALLOWED_DUAL_GATE_PAIRS` frozenset at `backtest/evaluate_dsr.py`
   but missed (197, 139) parallel to PHASE2C_11's (198, 154). The
   asymmetry surfaced at Step 8 fire-time (post-fire detection; per
   closeout §8.1 §19 instance #10); resolution was Auth #6.y
   `(PHASE2C_12_N_RAW, PHASE2C_12_N_ELIGIBLE_OBSERVED)` allowlist at
   commit `08e1488` plus baseline re-fire. A pre-fire trace enumerating
   `ALLOWED_DUAL_GATE_PAIRS` against PHASE2C_11 register-class-parallel
   structure would have caught the asymmetry before fire-time
   resolution cost.

The four instances span the fire-prep / fire-time boundary at distinct
surfacing points (instance 1 at Step 6.5 fire boundary as precondition
gap class; instances 2-3 at fire-prep with ad hoc patches at commits
`8887651` / `995fdb2`; instance 4 at fire-time with auth re-fire at
commit `08e1488`) and span distinct Q-LOCKED parameter classes (WF
lineage attestation binding / framework N count / framework N_eff set /
framework frozenset parametric structure). The discipline operates
across surfacing-points and parameter classes; the trigger condition
is the fire-prep boundary itself, not a specific surfacing-point or
parameter form.

### Application checklist

At each multi-step implementation arc Step boundary fire-prep:

1. **Enumerate all Q-LOCKED parameters at sub-spec relevant to this
   Step.** Q-LOCKED parameters are sub-spec lockpoints (Q-numbered
   summary table entries; explicit `Q<N> LOCKED` annotations; framework
   parameter set entries cited at sub-spec body) whose runtime
   resolution at this Step exercises framework code. Enumeration
   precision requires reading the sub-spec at register-precision, not
   summary register; Q-LOCKED parameters cited only indirectly (e.g.,
   "per sub-spec §X" without explicit lock value) require resolution
   to canonical lock value before enumeration completes.

2. **For each Q-LOCKED parameter: trace to framework code site
   (file:line); verify fire-time framework state matches sub-spec lock
   value.** The trace produces three artifacts at register-precision:
   (a) the canonical sub-spec lock value with explicit Q-number anchor;
   (b) the framework code site at file:line citation level; (c) the
   fire-time runtime resolution (state of the parameter at the moment
   the Step fires). All three must agree for the trace to pass. A
   trace that resolves canonical lock and framework code site but
   defers fire-time runtime resolution to post-fire register has not
   passed; the discipline's catch class is precisely the divergence
   between sub-spec lock and fire-time runtime state.

3. **For framework N + threshold + frozenset + similar parametric
   values: verify fire-time runtime parameter resolution matches
   sub-spec lock.** Parametric values bound at framework code
   (constants, frozenset literals, functional resolver outputs like
   `_resolve_n_eff_set()`) are fire-time-resolved at runtime; the
   verification step requires reading the runtime resolution, not the
   constant declaration alone. §21 specifies the checklist trace at
   fire-prep boundary; the broader executable verification function
   discipline operationalizing this trace as a callable runtime check
   is codified separately at PHASE2C_13 implementation arc Step 2 per
   sub-spec §5.4 disposition (Item 4 fold-in to Item 2 framework
   parameter pre-lock new-§ slot).

4. **For inter-step interface contracts (Step N output → Step N+1
   input): verify schema + sample compatibility before fire.** Inter-
   step interfaces operate as a register-class-distinct sub-class of
   parametric values: the Step N+1 fire register consumes the Step N
   output schema; schema-vs-input-contract divergence surfaces only at
   Step N+1 fire-time empirical observation. The verification step
   requires explicit schema + sample compatibility check at fire-prep
   register before Step N+1 fire authorization. The broader inter-step
   contract standardization discipline is codified separately at
   PHASE2C_13 implementation arc Step 3 per sub-spec §5.4 disposition
   (Item 3 new-§ slot).

5. **Surface any drift detected as a §19 instance candidate; annotate
   the cycle-internal §19 instance log entry with fire-prep boundary
   register-class.** Drift detected at fire-prep boundary logs at the
   cycle-internal §19 instance register (under §19 single-class
   register-class invariance per V#10 anchor); the log entry's
   mitigation-note column carries the fire-prep boundary register-
   class annotation as metadata. Sub-register-class formalization at
   §19 itself is deferred to a future cycle when cross-cycle
   accumulation supports formalization at the §19 register; §21's
   checklist contributes log entries at the existing §19 register
   without mutating §19's register-class taxonomy. Pre-fire-detected
   drift is the catch the discipline targets; post-fire-detected drift
   is the failure mode the discipline prevents.

The five-item checklist is structurally designed for mechanical
execution at fire-prep register: enumeration → per-parameter trace →
parametric runtime resolution → inter-step interface contract check →
drift surface routing. Mechanical execution does not require
interpretive judgment at any step; the discipline operates as a
procedural gate at the fire-prep boundary, distinct from interpretive-
register checks operating at drafting or reviewer register.

### Failure-mode signal

Watch for ad hoc resolution at fire-prep or fire-time boundaries
substituting for systematic pre-fire mechanical verification. The
pattern is the canonical failure mode the discipline catches:
PHASE2C_12 cycle's four instances (Step 6.5 walk-forward lineage gap
class / framework N mismatch caught at Step 8 fire-prep / sensitivity
table N_eff parameterization gap caught at Auth #6.x extension /
ALLOWED_DUAL_GATE_PAIRS asymmetry caught at Step 8 fire-time) are
concrete evidence basis spanning both fire-prep ad hoc patching
(instances 2 and 3) and fire-time post-fire resolution (instance 4).
Pattern recognition: ad hoc fire-prep parameter patches or fire-time
auth re-fires resolving sub-spec → framework code drift indicate
retroactive §19 instance accumulation plus auth-iteration overhead
that systematic pre-fire mechanical verification would prevent at
register-class register-precision.

Watch for Q-LOCKED parameter enumeration at summary register rather
than register-precision register. The pattern surfaces when the
fire-prep checklist enumerates Q-LOCKED parameters by reading the
sub-spec summary table without resolving each Q-numbered entry to its
canonical lock value. Summary-level enumeration covers the structural
parameter set but does not resolve canonical lock values; fire-time
runtime resolution against an unresolved canonical lock cannot detect
divergence by construction. Q-LOCKED parameter enumeration requires
register-precision read at the sub-spec body, not summary read.

Watch for trace completion at canonical lock + framework code site
without fire-time runtime resolution. The pattern surfaces when the
trace completes the (a) canonical lock and (b) framework code site
artifacts but defers (c) fire-time runtime resolution to post-fire
register. The deferral substitutes post-fire discovery for pre-fire
verification; the discipline's catch class — divergence between
sub-spec lock and fire-time runtime state — is the divergence the
deferral cannot detect by construction.

Watch for inter-step interface contract verification absent at fire-
prep register. Inter-step interfaces operate at register-class-distinct
register from per-parameter Q-LOCKED traces; verification absence at
fire-prep register surfaces the contract-divergence defect class only
at Step N+1 fire-time empirical observation. The deferral pattern
mirrors the parameter-trace deferral pattern at register-class-distinct
register; both substitutions cost the same retroactive §19 instance
accumulation plus auth-iteration overhead.

Watch for fire-prep checklist treated as interpretive judgment rather
than mechanical procedure. The pattern surfaces when the checklist
fires at high-level overview register ("looks aligned with sub-spec";
"framework appears to match the lock") rather than at mechanical trace
register (canonical lock value + file:line citation + fire-time
runtime resolution explicit). Interpretive-judgment execution covers
the structural-defect axis at low cost but does not establish the
register-precision the discipline requires; mechanical execution is
load-bearing for the discipline's catch class.

Watch for fire-prep checklist skipping when the Step boundary is
"obviously aligned" at sub-spec → framework register. Obvious-alignment
framing at structural register does not establish fire-time runtime
resolution alignment; the discipline's catch class is precisely the
divergence that obvious-alignment-clean fails to surface. Fire-prep
checklist is the mechanical complement — its catch is the divergence
that interpretive-judgment alignment misses by construction.

### Tier disposition

§21 ships at **Medium tier**. The four PHASE2C_12 cycle instances
enumerated at Trigger context give the discipline single-cycle empirical
basis. Cross-cycle accumulation register is fed by historical
PHASE2C_8.1 / PHASE2C_9 / PHASE2C_10 / PHASE2C_11 instance backfill at
the cycle-complexity scaling diagnosis discipline (codified separately
at PHASE2C_13 implementation arc Step 7 per sub-spec §5.4 disposition,
Carry-forward A new-§ slot). Strong-tier promotion is contingent on
(i) Strong-tier promotion bar criteria codified at the existing §13-§20
tier framework refinement (codified at PHASE2C_13 implementation arc
Step 9 per sub-spec §5.4 disposition, Carry-forward C fold-in to §20
appendix-style sub-§) and (ii) cross-cycle accumulation evidence
threshold met per the Strong-tier bar; tier re-evaluation at successor
methodology consolidation cycle once both contingencies resolve.
Medium tier preserves the discipline at observation-backed application
register without claiming Strong-tier prescriptive force prematurely.

---

## §22 Framework parameter pre-lock audit at sub-spec drafting cycle terminus

### Principle

Sub-spec drafting cycle SEAL pre-fire boundary requires a mechanical
framework parameter pre-lock audit step that enumerates each Q-LOCKED
parameter at the sub-spec and traces it to the framework code site
where the parameter is bound at fire-time. The audit produces, for
each Q-LOCKED parameter, a register-precision triple: (a) the
canonical sub-spec lock value with explicit Q-number anchor; (b) the
framework code site at file:line citation level; (c) the canonical
framework value at the code site. Sub-spec lock vs framework code
divergence at the audit register surfaces handoff-noise propagation
before the sub-spec seals, rather than after — preventing the canonical
divergence pattern from propagating into implementation arc fire-prep
and fire-time registers where the same drift surfaces as §19 spec-vs-
empirical-reality instance class downstream.

The discipline operates at a register distinct from §1 empirical
verification for factual claims, §15 anchor-list empirical verification
at the receiving cycle, and §21 fire-prep precondition checklist
discipline at multi-step implementation arc Step boundaries. §1 covers
general empirical verification of factual claims at any drafting
register. §15 covers pre-drafting anchor verification at the receiving
cycle — anchors arriving from advisor cycles, scoping decisions, or
prior register entries verified against canonical artifacts before
drafting initiates. §21 covers pre-fire mechanical verification at the
implementation arc Step boundary — Q-LOCKED parameters mechanically
traced from sub-spec lock to framework code site to fire-time runtime
state at the Step fire-prep boundary. §22 covers **pre-lock mechanical
verification at the sub-spec drafting cycle terminus** — Q-LOCKED
parameters mechanically traced from sub-spec lock to framework code
site at the sub-spec SEAL pre-fire boundary, before the lock is sealed
and before any implementation arc Step fires. The four disciplines
form a complementary chain: §1 catches defects at any drafting
register; §15 catches defects at anchor receipt boundary; §22 catches
defects at sub-spec SEAL pre-fire boundary; §21 catches defects at
implementation arc fire-prep boundary.

The chain's structural value is register-class-distinct catch points.
A defect that escapes one register catches at the next; absence of any
one register increases retroactive §19 instance accumulation plus auth-
iteration overhead at the next register. §22's specific catch class is
sub-spec → framework drift detectable at sub-spec SEAL pre-fire — the
class of drift that, absent §22, propagates through SEAL and surfaces
as fire-prep ad hoc patching or fire-time post-fire detection.

The audit operates at mechanical register, not interpretive register.
Mechanical execution does not require interpretive judgment at any
step; the audit is a procedural gate at the sub-spec SEAL boundary,
distinct from interpretive-register reviewer pass cycle activities
operating at substantive content register. The procedural gate's catch
class is canonical lock value vs framework code value divergence;
substantive content quality is reviewer pass cycle scope, register-
class-distinct from §22 audit scope.

### Trigger context

This discipline's empirical basis is four PHASE2C_12 cycle §19
instances (canonical numbering per closeout
[`docs/closeout/PHASE2C_12_RESULTS.md`](../closeout/PHASE2C_12_RESULTS.md)
§8.1 row register; instance descriptions cited verbatim from §8.1
canonical source artifact, not from sub-spec parenthetical labels).
The four instances are bound by Item 2 verbatim source at PHASE2C_12
closeout §10.2 lines 509-513 ("Prevents handoff-noise propagation that
produced §19 instances #5, #6, #8, #10"):

1. **§19 instance #5 — Batch size config-driven Step 2 blocker.**
   PHASE2C_12 sub-spec Q3 LOCKED main batch N=198 candidates at
   canonical baseline `b6fcbf86` total_valid_count anchor. At Step 2
   fire-prep boundary, the framework `STAGE2D_BATCH_SIZE` constant
   was hardcoded at 200 (engine-side config-driven cap) while sub-spec
   semantics required 198 at runtime; the 200-vs-198 divergence
   surfaced at Step 2 fire-prep as a Step-2-blocker. Resolution at
   commit `7c682fd`: Surface (1) `_resolve_batch_size()` env-var-
   driven resolver introduced. A pre-lock audit at sub-spec SEAL
   terminus enumerating Q3 → framework code (`stage2d_batch.py`
   batch-size constant) would have surfaced the 200-vs-198 drift at
   sub-spec SEAL pre-fire register; absent the audit, drift surfaced
   one register downstream at Step 2 fire-prep with auth-iteration
   overhead.

2. **§19 instance #6 — Ledger pre-charge coupling at Critic cost
   (PHASE2C_3 + PHASE2C_5 carry-forward).** PHASE2C_3 + PHASE2C_5
   closeouts surfaced a ledger pre-charge constraint coupling to
   `--live-critic` operational fire register; the coupling required a
   3-surface coupled patch (`PHASE2C_BATCH_SIZE` env-var + `--live-
   critic` CLI flag + ledger pre-charge wrap around `run_critic`) at
   Step 2 fire-prep. Resolution at commit `30d3bfd`. **The instance
   is register-class-distinct from instances #5/#8/#10 at coupling-
   discovery vs parameter-drift register; §22 audit discipline
   accommodates both register-classes at Trigger context evidence
   basis register, per Item 2 verbatim source binding that includes
   #6 at evidence basis citation.** Application checklist item 1's
   "Q-LOCKED parameter" enumeration register binds parameter-drift
   register-class strictly per Item 2 verbatim source ("framework
   parameter audit"); coupling-discovery register-class at instance
   #6 surfaces at audit metadata register adjacent to Application
   checklist item 1 enumeration, per Q-LOCKED items broader binding
   at sub-spec drafting cycle SEAL pre-fire boundary. Pre-lock audit
   at sub-spec SEAL terminus enumerating Q-LOCKED items and tracing
   each to operational coupling at framework code (e.g., ledger
   pre-charge call site at `run_critic` integration register) would
   have surfaced the coupling-discovery as a Q-LOCKED audit metadata
   entry at sub-spec SEAL register-precision rather than at Step 2
   fire-prep ad hoc patch register.

3. **§19 instance #8 — Sub-spec Q15 [REVISED] N_eff `{198, 80, 40,
   6}` vs framework hardcoded `{198, 80, 40, 5}` (5 themes anchor).**
   PHASE2C_12 sub-spec Q15 [REVISED] specified N_eff at "number of
   operational themes" register at PHASE2C_12 6-theme cycle. Framework
   hardcoded the prior 5-themes anchor at `evaluate_dsr.py` N_eff
   set; the 6-vs-5 divergence surfaced at Auth #6.x extension fire-
   prep iteration. Resolution at commit `995fdb2`: cycle-conditional
   `_resolve_n_eff_set()` resolver. A pre-lock audit at sub-spec SEAL
   enumerating Q15 → framework code N_eff set canonical value would
   have caught the 6-vs-5 drift at sub-spec SEAL pre-fire register;
   absent the audit, drift surfaced at Auth #6.x extension with auth
   re-fire overhead.

4. **§19 instance #10 — ALLOWED_DUAL_GATE_PAIRS parallel-structure
   incompleteness.** PHASE2C_12 Auth #6.x β1 narrow added (197, 197)
   to the `ALLOWED_DUAL_GATE_PAIRS` frozenset at
   `backtest/evaluate_dsr.py` but missed (197, 139) parallel to
   PHASE2C_11's (198, 154). The asymmetry surfaced at Step 8 fire-
   time (post-fire detection). Resolution at commit `08e1488`: Auth
   #6.y `(PHASE2C_12_N_RAW, PHASE2C_12_N_ELIGIBLE_OBSERVED)` allowlist
   plus baseline re-fire. A pre-lock audit at sub-spec SEAL enumerating
   the dual-gate frozenset structure and tracing PHASE2C_11 register-
   class-parallel completeness would have caught the asymmetry at
   sub-spec SEAL pre-fire register; absent the audit, asymmetry
   surfaced one register-pair downstream at Step 8 fire-time with
   post-fire detection overhead and baseline re-fire cost.

The four instances span sub-spec → framework drift at distinct
parameter classes (canonical batch size constant / operational
coupling discovery / parametric N_eff set / frozenset parametric
structure) and at distinct downstream surfacing registers (Step 2
fire-prep / Step 2 fire-prep / Auth #6.x extension fire-prep / Step 8
fire-time). The discipline operates across parameter classes and
downstream surfacing registers; the trigger condition is the sub-spec
SEAL pre-fire boundary itself, not a specific parameter class or
downstream surfacing register. Each instance, absent §22 audit,
cost auth-iteration overhead at its downstream catch register;
audit at sub-spec SEAL pre-fire register-class avoids the auth-
iteration overhead by mechanical pre-lock catch.

### Application checklist

At sub-spec drafting cycle SEAL pre-fire boundary:

1. **Enumerate all Q-LOCKED parameters at sub-spec.** Q-LOCKED
   parameters are sub-spec lockpoints (Q-numbered summary table
   entries; explicit `Q<N> LOCKED` annotations; framework parameter
   set entries cited at sub-spec body) whose runtime resolution at
   any implementation arc Step exercises framework code. Enumeration
   precision requires reading the sub-spec at register-precision, not
   summary register; Q-LOCKED parameters cited only indirectly
   (e.g., "per sub-spec §X" without explicit lock value) require
   resolution to canonical lock value before enumeration completes.
   Mirrors §21 Application checklist item 1 register-class precision
   discipline; the two enumerations operate at the same Q-LOCKED
   parameter set but at distinct fire-prep boundaries (§22 sub-spec
   SEAL terminus vs §21 implementation arc Step fire-prep).

2. **For each Q-LOCKED parameter: cite framework code site (file:line)
   where the parameter is bound at fire-time.** The citation produces
   the framework code anchor at register-precision: file path + line
   number + the parametric construct (constant declaration, frozenset
   literal, functional resolver definition site, configuration default,
   etc.) at the cited line. Citation precision requires reading the
   framework code, not framework documentation alone; documentation
   may diverge from code state at the audit register-event boundary.

3. **For each Q-LOCKED parameter: confirm sub-spec lock value =
   framework code canonical value (no drift at audit register).** The
   confirmation produces a binary outcome at register-precision: PASS
   (canonical lock value matches framework code value at the cited
   site) or DRIFT (canonical lock value diverges from framework code
   value, with diverged-pair recorded as `<Q-number, sub-spec value,
   framework code value, divergence-class>`). DRIFT outcome routes to
   item 5 below for §19 instance candidate surfacing at register-
   class-distinct register before SEAL fire.

4. **For framework parameters that are runtime-resolved (functional
   resolvers, cycle-conditional state, dual-gate frozenset structure,
   parametric value sets): MUST author corresponding executable
   verification function spec at sub-spec.** This sub-rule operationalizes
   Item 4 (LOCKED items → executable verification function checklist)
   as fold-in to §22 at parent-operationalization coupling register:
   §22 codifies the sub-spec terminus mechanical audit; Item 4 codifies
   the runtime executable verification function discipline that the
   audit produces as a sub-spec specification deliverable. Per Item 4
   fold-in mechanism:

   - **(4a) Executable verification function spec authoring.** For
     each Q-LOCKED item at sub-spec whose runtime resolution exercises
     framework code (constants, frozenset literals, functional
     resolvers, cycle-conditional resolvers, parametric value sets),
     author a corresponding executable verification function spec at
     sub-spec drafting cycle. The spec format: function signature
     (`def verify_Q_<n>() -> bool` or
     `def verify_Q_<n>(framework_state: <type>) -> tuple[bool, str]`
     for diagnostic-return register); return semantics (True iff
     fire-time framework state preserves the Q-LOCKED constraint;
     False otherwise with diagnostic tuple at extended-return register
     if applicable); invocation surface annotation at the
     implementation arc fire-prep boundary (which Step's fire-prep
     checklist register provides the canonical invocation surface
     per §21 Application checklist item 3 register-class binding;
     invocation surface annotation at sub-spec authoring register
     declares the intended fire-prep boundary for downstream §21
     fire-prep register reference, register-class-distinct from
     invocation-binding at implementation register).

   - **(4b) Pattern reference at register-precision.**
     `_resolve_n_eff_set()` at PHASE2C_12 Auth #6.x-extension commit
     `995fdb2` is the concrete pattern reference for the executable
     verification function discipline. The resolver was authored
     post-fire-prep as ad hoc resolution to §19 instance #8 (canonical
     §8.1 numbering); Item 4 codifies the discipline that the resolver
     should have been authored pre-fire at sub-spec drafting cycle as
     part of the Q15 [REVISED] LOCKED specification. The pattern
     extends to other Q-LOCKED items at PHASE2C_12 + future cycles:
     each Q-LOCKED item with framework runtime resolution produces
     one verification function spec at sub-spec drafting register.

   - **(4c) Coupling with §21 Application checklist item 3.** §21
     Application checklist item 3 covers fire-prep mechanical
     verification of framework parametric values at implementation
     arc Step boundary; §22 Application checklist item 4 (this fold-
     in) covers sub-spec drafting cycle authoring of executable
     verification function specs. §21 fire-prep checklist register
     provides the canonical invocation surface for verification
     functions authored per this sub-rule, per §21 Application
     checklist item 3 register-class binding ("codified separately
     at PHASE2C_13 implementation arc Step 2 per sub-spec §5.4
     disposition"). The two items operate at register-class-distinct
     boundaries (sub-spec SEAL terminus vs implementation arc Step
     fire-prep) but reference the same Q-LOCKED parameter set at
     register-precision; cross-reference at Application checklist
     item 4 preserves the chain's load-bearing structural coupling
     at codification register, register-class-distinct from
     invocation-binding register at implementation register.

5. **Surface any drift detected as §19 instance candidate at register-
   class-distinct register before SEAL fire.** Drift detected at
   sub-spec SEAL pre-fire boundary logs at the cycle-internal §19
   instance register; the log entry's mitigation-note column carries
   the sub-spec SEAL pre-fire boundary register-class annotation as
   metadata. The drift may be resolved before SEAL (e.g., framework
   code patch + sub-spec lock value re-confirmation) or surfaced as
   carry-forward to next-cycle register if framework code change is
   out-of-scope; either disposition requires explicit register-class
   logging at sub-spec SEAL pre-fire boundary, not implicit
   propagation through SEAL. Mirrors §21 Application checklist item 5
   register-class-distinct surfacing pattern at companion fire-prep
   boundary.

The five-item checklist (with item 4 internally structured at three
sub-rules per Item 4 fold-in mechanism) is structurally designed for
mechanical execution at sub-spec SEAL pre-fire register: enumeration
→ per-parameter framework code site citation → canonical value
divergence check → executable verification function spec authoring
(fold-in) → drift surface routing. Mechanical execution does not
require interpretive judgment at any item; the audit operates as a
procedural gate at the sub-spec SEAL boundary, register-class-distinct
from interpretive-register reviewer pass cycle activities operating at
substantive content register.

### Failure-mode signal

Watch for sub-spec SEAL fires without explicit framework parameter
audit at sub-spec drafting cycle terminus. The omission is the primary
defect §22 catches: absent the audit, sub-spec → framework drift
propagates through SEAL and surfaces at downstream fire-prep or fire-
time register. PHASE2C_12 cycle's four §19 instances (canonical §8.1
numbering #5 + #6 + #8 + #10) are concrete evidence basis: each
instance, absent §22 audit at sub-spec SEAL pre-fire register, cost
auth-iteration overhead at its downstream catch register (Step 2 fire-
prep / Step 2 fire-prep / Auth #6.x extension / Step 8 fire-time).

Watch for Q-LOCKED parameter enumeration at summary register rather
than register-precision register. The pattern surfaces when the audit
enumerates Q-LOCKED parameters by reading the sub-spec summary table
without resolving each Q-numbered entry to its canonical lock value.
Summary-level enumeration covers the structural parameter set but
does not resolve canonical lock values; framework code value
comparison against an unresolved canonical lock cannot detect
divergence by construction. Inherits the register-precision discipline
codified at §21 Failure-mode signal item 2.

Watch for framework code site citation absent or imprecise. The
pattern surfaces when the audit cites framework code at module
register ("at `evaluate_dsr.py`") rather than at file:line register
("at `evaluate_dsr.py:153` `_resolve_n_eff_set()`"). Module-level
citation covers structural framework anchor but does not establish
register-precision needed for canonical value comparison; framework
code may contain multiple parametric sites for related Q-LOCKED items
where divergence-class distinction requires line-precision register.

Watch for canonical value comparison treated as interpretive judgment
rather than mechanical procedure. The pattern surfaces when the
comparison fires at high-level overview register ("looks aligned with
sub-spec"; "framework appears to match the lock") rather than at
mechanical comparison register (canonical lock value + framework code
value at cited line + binary PASS / DRIFT outcome explicit).
Interpretive-judgment execution covers the structural-defect axis at
low cost but does not establish the register-precision the discipline
requires; mechanical execution is load-bearing for the discipline's
catch class.

Watch for runtime-resolved parameter audit deferred to fire-prep
without executable verification function spec at sub-spec. The
pattern surfaces when the audit covers static Q-LOCKED items
(constants, configuration defaults) at canonical value comparison
register but defers runtime-resolved Q-LOCKED items (functional
resolvers, cycle-conditional state, dual-gate frozenset structure)
to fire-prep mechanical verification (§21) without authoring the
corresponding executable verification function spec at sub-spec.
The deferral substitutes runtime catch (§21) for sub-spec drafting
register catch (§22 item 4 fold-in); each substitution leaves the
runtime-resolved parameter without an executable verification anchor
at fire-prep boundary, recreating the ad hoc resolution pattern that
PHASE2C_12 §19 instance #8 (canonical §8.1 numbering) exemplifies.

Watch for description drift between sub-spec parenthetical labels
and source artifact canonical descriptions. The pattern surfaces
when sub-spec body cites source-artifact register entries by number
plus parenthetical description, where the parenthetical description
diverges from the canonical source-artifact entry at the cited number.
The drift is a sub-class of the §22 canonical failure mode pattern at
sub-spec drafting register-class itself: handoff-noise propagation
between authoring register and source artifact, undetected at
sub-spec SEAL pre-fire absent register-precision empirical
verification per §1 + §15 disciplines. PHASE2C_13 sub-spec §2.2
codification mechanism prose contains a concrete instance:
parenthetical descriptions for §19 instances #5 + #6 + #8 inverted
relative to canonical PHASE2C_12 closeout §8.1 row register; the
inverted descriptions did not block sub-spec SEAL because §22 audit
discipline did not yet exist at the sub-spec SEAL register-event
boundary. Future sub-spec drafting cycles operating §22 audit
discipline at SEAL pre-fire register catch this drift class at the
audit register itself.

Watch for sub-spec SEAL fires under time pressure without §22 audit
completed. The pattern surfaces when sub-spec SEAL pre-fire register
elides §22 audit on the framing that "framework code looks aligned"
or "audit can fire at implementation arc Step 1 instead." The
elision substitutes downstream register catch (§21 fire-prep) for
the sub-spec SEAL pre-fire register catch (§22 audit); the
substitution cost is auth-iteration overhead at the downstream
register relative to the same Q-LOCKED parameter audit at sub-spec
SEAL pre-fire register. The pattern is the canonical failure mode
the discipline catches.

### Tier disposition

§22 ships at **Medium tier with cross-cycle-pending status note**.
The four PHASE2C_12 cycle §19 instances enumerated at Trigger
context (canonical §8.1 numbering #5 + #6 + #8 + #10) give the
discipline single-cycle empirical basis at sub-spec drafting →
framework code drift register-class. Cross-cycle accumulation
register is fed by historical PHASE2C_8.1 / PHASE2C_9 / PHASE2C_10 /
PHASE2C_11 instance backfill at the cycle-complexity scaling
diagnosis discipline (codified separately at PHASE2C_13
implementation arc Step 7 per sub-spec §5.4 disposition, Carry-
forward A new-§ slot). Strong-tier promotion is contingent on (i)
Strong-tier promotion bar criteria codified at the existing §13-§20
tier framework refinement (codified at PHASE2C_13 implementation arc
Step 9 per sub-spec §5.4 disposition, Carry-forward C fold-in to §20
appendix-style sub-§) and (ii) cross-cycle accumulation evidence
threshold met per the Strong-tier bar; tier re-evaluation at
successor methodology consolidation cycle once both contingencies
resolve. Medium tier preserves the discipline at observation-backed
application register without claiming Strong-tier prescriptive force
prematurely.

The Item 4 fold-in (Application checklist item 4 sub-rules 4a/4b/4c)
inherits §22's tier disposition at register-precision: the executable
verification function discipline operates at register-class-coupled
register with §22's framework parameter pre-lock audit; tier-class
parallel preserves the parent-operationalization coupling per sub-
spec §5.4 fold-in 4-criteria check. Independent tier evaluation of
the Item 4 fold-in is register-class-distinct concern: the fold-in
ships under §22 Medium tier disposition at codification register; the
Item 4 evidence basis (one concrete pattern reference at
`_resolve_n_eff_set()` plus indirect evidence via §22's four §19
instances) supports the parent §22 tier disposition at fold-in
register without requiring separate Item 4 tier evaluation.

---

## §23 Inter-step contract standardization at multi-step implementation arc Step boundaries

### Principle

Multi-step implementation arc Step boundaries (Step N output → Step N+1
input) require explicit interface contract specification at sub-spec
authoring time. The interface contract specification produces three
artifacts at register-precision per Step boundary: (a) schema (field
enumeration + type + constraint at the Step N output / Step N+1 input
boundary; explicit declarative specification, not narrative
description); (b) sample (canonical example of the Step N output
artifact at field-by-field instantiation; concrete instance, not
abstract template); (c) validation (consumer-side check function
specification or schema-validator invocation surface at Step N+1
fire-prep register). Absent the contract specification at sub-spec
authoring register, the Step N+1 fire register consumes the Step N
output at implicit-contract register, with schema-vs-input divergence
surfacing only at Step N+1 fire-time integration debugging or post-
fire empirical observation.

The discipline operates at a register distinct from §1 empirical
verification for factual claims, §15 anchor-list empirical verification
at the receiving cycle, §22 framework parameter pre-lock audit at
sub-spec drafting cycle terminus, and §21 fire-prep precondition
checklist discipline at multi-step implementation arc Step boundaries.
§1 covers general empirical verification of factual claims at any
drafting register. §15 covers pre-drafting anchor verification at the
receiving cycle — anchors arriving from advisor cycles, scoping
decisions, or prior register entries verified against canonical
artifacts before drafting initiates. §23 covers **sub-spec authoring of
inter-step interface contracts** — the explicit schema + sample +
validation triple authored at sub-spec body for each Step N → Step N+1
boundary, register-class-distinct from per-parameter Q-LOCKED audit
content scope. §22 covers pre-lock mechanical verification at the
sub-spec drafting cycle terminus — Q-LOCKED parameters mechanically
traced from sub-spec lock to framework code site at the sub-spec SEAL
pre-fire boundary. §21 covers pre-fire mechanical verification at the
implementation arc Step fire-prep boundary — Q-LOCKED parameters and
inter-step interface contracts mechanically verified at fire-prep
boundary, with the inter-step interface verification authored per §23
providing the canonical contract reference at §21 Application checklist
item 4 register.

The five disciplines form a complementary chain ordered by register-
class catch boundary tracking workflow time: §1 catches defects at any
drafting register; §15 catches defects at anchor receipt boundary
(drafting cycle start); §23 catches defects at sub-spec authoring of
inter-step interface contracts (drafting cycle mid); §22 catches
defects at sub-spec SEAL pre-fire boundary (drafting cycle terminus);
§21 catches defects at implementation arc Step fire-prep boundary
(post-SEAL). §23 is ordered before §22 in the chain because §23 fires
at sub-spec authoring time per sub-spec §2.3 binding, while §22 fires
at sub-spec drafting cycle terminus per §22 binding. The chain's
structural value is register-class-distinct catch points across
discipline scope. A defect that escapes one register catches at the
next; absence of any one register increases retroactive defect
propagation overhead at downstream registers. §23's specific catch
class is sub-spec → inter-step interface specification absence
detectable at sub-spec authoring register — the class of interface-
specification gap that, absent §23, propagates through sub-spec SEAL
and surfaces as Step N+1 fire-time integration debugging or post-fire
empirical observation.

§23 operates at register distinct from §22 and §21 at coupled but
distinct register-class scopes. §22's catch class is canonical
Q-LOCKED parameter value vs framework code value divergence at
sub-spec SEAL pre-fire register; §23's catch class is inter-step
interface contract specification absence at sub-spec authoring register
— register-class-coupled at sub-spec drafting cycle but register-
class-distinct at content scope (per-parameter values vs per-Step-
boundary interfaces). §21's catch class is fire-time runtime resolution
at implementation arc Step fire-prep boundary; §23's catch class is
sub-spec authoring at sub-spec body register — register-class-coupled
at inter-step interface verification (the contract authored per §23
provides the canonical reference for §21 Application checklist item 4
fire-prep verification) but register-class-distinct at temporal scope
(sub-spec authoring vs implementation arc fire-prep). Cross-§ register-
class collision is avoided in both cases by content-scope or temporal-
scope distinction at register-precision.

### Trigger context

This discipline's empirical basis is one PHASE2C_12 cycle instance
per Item 3 verbatim source at PHASE2C_12 closeout
[`docs/closeout/PHASE2C_12_RESULTS.md`](../closeout/PHASE2C_12_RESULTS.md)
§10.2 lines 515-518:

> Item 3 — Step 7/8 contract standardization. Codify inter-step
> contract test (schema + sample + validation) at each Step boundary.
> Step 7 evaluation gate output schema → Step 8 input contract had no
> explicit interface spec at PHASE2C_12 fire-time.

PHASE2C_12 cycle Step 7 evaluation gate output → Step 8 mechanical
disposition fire input boundary fired at PHASE2C_12 cycle without
explicit interface contract specification at sub-spec body. Step 7
produced evaluation gate output artifacts at
`data/phase2c_evaluation_gate/phase2c_12_*` (audit_v1 + audit_2024_v1
+ eval_2020_v1 + eval_2021_v1 per CLAUDE.md PHASE2C_12 cycle
implementation arc commit register); Step 8 consumed these artifacts
at fire-time without an explicit schema + sample + validation triple
authored at sub-spec body. The interface gap surfaced at fire-time
integration debugging register-precision rather than at sub-spec
authoring register; absent §23 audit at sub-spec authoring boundary,
the gap propagated through sub-spec SEAL to Step 8 fire-prep with
downstream integration overhead at register-class-distinct register
from per-parameter §22 audit class.

The single PHASE2C_12 instance represents the canonical fire-time
contract gap evidence basis at the Step N → Step N+1 boundary register-
class. Single-instance basis per cycle is sufficient for Medium-tier
codification per sub-spec §4.3.4 binding; the register-class-distinction
from §19 finding pattern accumulation density and the Strong-tier
promotion contingency framing are anchored at Tier disposition
register-class-canonical anchor below.

The pattern generalizes from the PHASE2C_12 Step 7 → Step 8 boundary
to any multi-step implementation arc Step N → Step N+1 boundary with
chained output → input dependencies. Generalization scope: any Step
pair where Step N produces an artifact (file path + format + schema)
consumed at Step N+1 register; the trigger condition is the inter-step
boundary itself, not the specific Step pair or specific output / input
semantics. The discipline's Application checklist (items 1-5 below)
operates uniformly across Step pair instances; the per-Step-pair
instantiation produces register-class-specific schema + sample +
validation triple at register-precision but the Application checklist
procedural structure is invariant.

### Application checklist

At sub-spec drafting cycle for each multi-step implementation arc Step
boundary:

1. **Identify Step N output artifact(s).** For each Step N → Step N+1
   boundary at sub-spec, enumerate the canonical output artifact set
   produced at Step N register. The enumeration produces three sub-
   artifacts at register-precision per output: (a) file path at
   canonical project structure register (e.g.,
   `data/phase2c_evaluation_gate/audit_v1/`); (b) format at file-
   format register (e.g., JSON, Parquet, CSV); (c) schema at field-
   enumeration register (field name + type + constraint per field).
   Enumeration precision requires reading sub-spec Step N description
   at register-precision, not summary register; output artifacts cited
   only indirectly (e.g., "per Step N output") require resolution to
   canonical artifact path + format + schema before enumeration
   completes. Mirrors §21 Application checklist item 1 register-
   precision discipline at the parallel Q-LOCKED parameter enumeration
   register-class.

2. **Identify Step N+1 input requirement(s).** For each Step N → Step
   N+1 boundary at sub-spec, enumerate the consumed input artifact
   set required at Step N+1 register. The enumeration produces three
   sub-artifacts at register-precision per input: (a) consumed file
   path at the Step N+1 fire-time register; (b) expected schema at
   field-enumeration register (field name + type + constraint per
   field); (c) validation rules (consumer-side check function or
   schema-validator invocation surface at Step N+1 fire-prep register).
   Enumeration precision matches item 1 register precision; input
   artifacts cited only indirectly require resolution to canonical
   consumed-path + expected-schema + validation-rule before
   enumeration completes.

3. **Author explicit interface spec triple at sub-spec body.** For
   each Step N → Step N+1 boundary at sub-spec, author the schema +
   sample + validation triple at sub-spec body register. The triple
   format at register-precision: schema (field enumeration + type +
   constraint at the Step N output / Step N+1 input boundary; explicit
   declarative specification, not narrative description); sample
   (canonical example of the Step N output artifact at field-by-field
   instantiation; concrete instance, not abstract template); validation
   (consumer-side check function specification or schema-validator
   invocation surface at Step N+1 fire-prep register; specifies the
   validation function signature, return semantics, and invocation
   surface annotation at sub-spec authoring register, register-class-
   distinct from invocation-binding at implementation register per §22
   Application checklist item 4 sub-rule 4a precedent). All three
   artifacts of the triple must be authored explicitly at sub-spec
   body; partial authoring (schema-only or sample-only) leaves the
   consumer-side validation surface unspecified, recreating the
   implicit-contract gap pattern that §23 catches.

4. **Bind interface spec at sub-spec § for the Step boundary.** Each
   interface spec triple binds at a sub-spec § (sub-§ or content
   paragraph cluster at register-precision) referenced by both Step N
   and Step N+1 sub-spec content. The binding produces a register-
   class-canonical anchor for the interface spec; sub-spec content at
   Step N register cross-references the binding § for Step N output
   specification; sub-spec content at Step N+1 register cross-
   references the binding § for Step N+1 input requirement. Mutual
   cross-reference at the binding § preserves the inter-step contract
   at register-class-coherent canonical anchor; partial cross-reference
   (Step N references only or Step N+1 references only) recreates the
   asymmetric specification pattern that the contract standardization
   discipline catches.

5. **Implementation arc Step N+1 fire-prep boundary invokes the
   interface validation function authored per item 3 as fire-prep
   precondition (cross-reference §21 fire-prep precondition checklist
   Application checklist item 4).** §21 Application checklist item 4
   ("For inter-step interface contracts (Step N output → Step N+1
   input): verify schema + sample compatibility before fire") covers
   the fire-prep verification register-class; §23 Application checklist
   item 5 (this item) covers the sub-spec authoring → implementation
   arc fire-prep handoff register-class. The two items operate at
   register-class-distinct boundaries (§23 sub-spec authoring vs §21
   implementation arc fire-prep) but reference the same inter-step
   interface contract at register-precision; cross-reference at item 5
   preserves the chain's load-bearing structural coupling at
   codification register, register-class-distinct from invocation-
   binding register at implementation register.

The five-item checklist is structurally designed for mechanical
execution at sub-spec authoring register: Step N output enumeration →
Step N+1 input enumeration → interface spec triple authoring → sub-
spec § binding → implementation arc fire-prep handoff annotation.
Mechanical execution does not require interpretive judgment at any
item; the discipline operates as a procedural gate at the sub-spec
authoring boundary, register-class-distinct from interpretive-register
reviewer pass cycle activities operating at substantive content
register and register-class-distinct from interpretive-register Step
description authoring at narrative content register.

### Failure-mode signal

Watch for inter-step interface contracts left implicit at sub-spec
body. The omission is the primary defect §23 catches: absent the
explicit schema + sample + validation triple at sub-spec body
register, the Step N+1 fire register consumes the Step N output at
implicit-contract register with schema-vs-input divergence surfacing
only at Step N+1 fire-time empirical observation. PHASE2C_12 cycle
Step 7 evaluation gate output → Step 8 mechanical disposition fire
input boundary is concrete evidence basis: absent §23 audit at sub-
spec authoring register, the boundary fired with implicit-contract
specification and consumed Step 7 output at fire-time integration
debugging register-precision rather than at sub-spec authoring
register-precision.

Watch for Step N output schema documented at descriptive register but
not at validation-checkable register. The pattern surfaces when sub-
spec Step N description includes prose narrative of output artifacts
("Step N produces evaluation gate output at `data/.../`") without
explicit field enumeration + type + constraint at schema register.
Descriptive narrative covers structural output existence at low cost
but does not establish schema register-precision needed for consumer-
side validation; Step N+1 fire register cannot construct schema-
validator invocation against descriptive narrative by construction.
Schema authoring requires explicit field enumeration at sub-spec body,
not narrative inference.

Watch for interface validation deferred to fire-time without explicit
pre-fire spec at sub-spec body. The pattern surfaces when sub-spec
Step N+1 description includes ad hoc validation language ("Step N+1
verifies Step N output before consuming") without authoring the
validation function spec at sub-spec body register. Fire-time deferral
substitutes fire-prep ad hoc check for sub-spec authoring-register
catch; the discipline's catch class — interface-specification absence
at sub-spec authoring register — is the absence the deferral cannot
detect by construction. Validation function spec authoring at sub-spec
body is the load-bearing artifact at sub-spec authoring register;
fire-time invocation register is downstream from authoring register at
temporal sequence.

Watch for asymmetric inter-step interface specification at the binding
§. The pattern surfaces in two register-class-distinct forms: (i)
**asymmetric cross-reference at the binding §** — sub-spec content at
one Step register cross-references the binding § but the other Step
register does not, leaving the binding § anchoring only one side of
the contract while the other side consumes or produces the artifact
at implicit-contract register; (ii) **asymmetric content specification
at the binding §** — sub-spec content covers Step N output
specification at register-precision but does not cover Step N+1 input
expectations at register-precision (or vice versa), leaving consumer-
side validation surface implicitly inferred from producer-side
specification. Mutual cross-reference plus bidirectional content
specification at the binding § preserves both producer and consumer
register-class explicitly; either asymmetry fails the contract
structure by construction at the consumer-side validation register.

Watch for interface contract verification treated as interpretive
judgment rather than mechanical procedure at sub-spec authoring
register. The pattern surfaces when sub-spec authoring fires at high-
level overview register ("Step N output looks compatible with Step
N+1 input"; "interface spec is implicit but obvious") rather than at
mechanical specification register (schema + sample + validation triple
authored at sub-spec body explicitly). Interpretive-judgment authoring
covers the structural-defect axis at low cost but does not establish
the register-precision the discipline requires; mechanical authoring
is load-bearing for the discipline's catch class.

Watch for sub-spec SEAL fires under time pressure without §23 audit
completed for all multi-step Step boundaries. The pattern surfaces
when sub-spec SEAL pre-fire register elides §23 audit on the framing
that "Step boundaries can be specified at implementation arc Step
entry instead." The elision substitutes downstream register catch
(implementation arc Step entry register or §21 fire-prep register)
for the sub-spec authoring register catch (§23 audit); the
substitution cost is downstream integration overhead at the catch
register relative to the same inter-step interface specification at
sub-spec authoring register. The pattern is the canonical failure mode the
discipline catches at sub-spec authoring register-precision register-
class.

### Tier disposition

§23 ships at **Medium tier with cross-cycle-pending status note**.
The single PHASE2C_12 cycle instance enumerated at Trigger context
(Step 7 evaluation gate output → Step 8 mechanical disposition fire
input boundary) gives the discipline single-cycle empirical basis at
inter-step interface contract gap register-class. Single-instance
basis per cycle is typical given implementation arc Step boundaries
are register-class-distinct from §19 finding register-class: §19
finding pattern accumulates per-cycle multiple instances at framework
parameter divergence register; §23 inter-step interface contract gap
pattern accumulates at most one or two instances per cycle at Step
boundary register. Cross-cycle accumulation register is fed by
historical PHASE2C_8.1 / PHASE2C_9 / PHASE2C_10 / PHASE2C_11 instance
backfill at the cycle-complexity scaling diagnosis discipline
(codified separately at PHASE2C_13 implementation arc Step 7 per
sub-spec §5.4 disposition, Carry-forward A new-§ slot). Strong-tier
promotion is contingent on (i) Strong-tier promotion bar criteria
codified at the existing §13-§20 tier framework refinement (codified
at PHASE2C_13 implementation arc Step 9 per sub-spec §5.4 disposition,
Carry-forward C fold-in to §20 appendix-style sub-§) and (ii) cross-
cycle accumulation evidence threshold met per the Strong-tier bar;
tier re-evaluation at successor methodology consolidation cycle once
both contingencies resolve. Medium tier preserves the discipline at
observation-backed application register without claiming Strong-tier
prescriptive force prematurely.

The single-instance basis at PHASE2C_12 cycle is sufficient for
codification at Medium tier per sub-spec §4.3.4 binding. Cross-cycle
accumulation register at §23-relevant Step boundary class may
accumulate sparse instances per cycle due to register-class-
distinction from §19 finding pattern. The cross-cycle accumulation
evidence threshold for §23 Strong-tier promotion at §20.6 register may
bind at lower cumulative instance count than disciplines accumulating
at §19 finding register-class; the bar criteria specification at Step
9 §20.6 register operates at register-precision per cross-cycle
observation pattern, register-class-distinct from §19 finding pattern
accumulation. Tier evaluation at successor cycle resolves the bar
criteria interaction at register-precision once §20.6 sub-§ codifies
bar criteria 1-4.

---

## §25 Register-class explicit declaration at Step deliverable authoring

### Principle

Multi-step implementation arc Step deliverables that contain metrics
and outputs at multiple register-classes — mechanical-output / inter-
pretive-overlay / intermediate / final / sensitivity — require an
explicit register-class declaration block at the deliverable §-opening
that states which register-class(es) each metric or output operates
at, plus inline register-class context preserved at each first-
reference site within the deliverable body. Reviewer pass cycle then
receives the deliverable with explicit register-class context;
reviewers operate at register-precision matching the declared
register-class, and reviewer prompt template includes a register-
class match verification annotation. Without the explicit declaration,
reviewer over-interpretation at the wrong register-class is the
canonical defect class — a §9.0c reviewer-register instance class
where interpretive-overlay framing is applied to a mechanical-output
register-class metric (or vice versa) at reviewer engagement time.
Reviewer prompt template verification is part of the deliverable-
authoring contract scope, not a separate reviewer-process discipline:
the prompt template is authored at sub-spec specification register
as a sub-component of the deliverable-authoring discipline, with
invocation at reviewer pass cycle runtime register downstream of
deliverable authoring boundary.

The discipline operates at a register distinct from §1 empirical
verification for factual claims, §15 anchor-list empirical verification
at the receiving cycle, §23 inter-step contract standardization at
multi-step implementation arc Step boundaries, §22 framework parameter
pre-lock audit at sub-spec drafting cycle terminus, and §21 fire-prep
precondition checklist discipline at multi-step implementation arc
Step boundaries. The six disciplines form a complementary chain
ordered by register-class catch boundary tracking workflow time: §1
catches defects at any drafting register; §15 catches defects at
anchor receipt boundary (drafting cycle start); §23 catches defects
at sub-spec authoring of inter-step interface contracts (drafting
cycle mid); §22 catches defects at sub-spec SEAL pre-fire boundary
(drafting cycle terminus); §21 catches defects at implementation arc
Step fire-prep boundary (post-SEAL, pre-Step-execution); §25 catches
defects at Step deliverable authoring boundary (post-Step-execution,
pre-reviewer-pass). §25 is ordered after §21 in the chain because
§21 fires before the Step executes (mechanical pre-fire verification)
while §25 fires after the Step's metrics and outputs are produced
(register-class declaration binding output semantics for downstream
reviewer engagement). The chain's structural value is register-class-
distinct catch points across discipline scope; absence of any one
register increases retroactive defect propagation overhead at the
downstream registers, including the reviewer pass cycle register
where §25's specific catch class operates. The chain ordering is at
workflow catch-boundary register, not at numeric § register: §25
ships at numeric §-slot 25 sequential to §21-§23 codification slots
at PHASE2C_13 implementation arc but operates at the latest catch
boundary in the workflow time chain, post-§21 fire-prep boundary.

§25 operates at register-class-distinct content scope from §21-§23
cluster (per-parameter values vs per-Step-boundary interfaces vs
metric / output register-class semantics) and at register-class-
coupled content scope with §16 anchor-prose-access discipline at
multi-hundred-line interpretive deliverables. §16 covers the prose-
access mode at section-seal reviewer engagement (reviewer adjudication
fires against actual prose, not summary or structural overview); §25
covers the register-class declaration mode at deliverable §-opening
(reviewer engagement receives explicit register-class context for
metrics and outputs). §16 + §25 both operate at reviewer-engagement
register-class but register-class-distinct at content scope: §16
ensures reviewers engage the actual content; §25 ensures reviewers
engage at register-precision matching the metric / output register-
class semantics. Cross-§ register-class collision is avoided by
content-scope distinction at register-precision — prose-access mode
(engagement fidelity) vs register-class declaration (engagement
register-class semantics).

### Trigger context

This discipline's empirical basis is one PHASE2C_12 cycle §9.0c
instance per Item 5 verbatim source at PHASE2C_12 closeout
[`docs/closeout/PHASE2C_12_RESULTS.md`](../closeout/PHASE2C_12_RESULTS.md)
§10.2 lines 525-530:

> Item 5 — Reviewer over-interpretation prevention. Codify register-
> class explicit declaration in each Step deliverable: "Before
> interpreting metric X, declare which register-class (intermediate /
> final / sensitivity)". §9.0c instance #8 (advisor pre-fire prediction
> wrong) is concrete instance of this defect class. Add reviewer prompt
> template: "Does this metric belong to mechanical-output register or
> interpretive-overlay register?"

The single instance is canonical §8.2 row register entry #8 at
PHASE2C_12 closeout enumeration:

1. **§9.0c instance #8 — Advisor pre-fire interpretive overlay on
   mechanical Q22 LOCKED compute output (predicted artifact_evidence;
   actual inconclusive at fire-time).** PHASE2C_12 Step 8 mechanical
   disposition fire executed Q22 LOCKED routing at deterministic
   mechanical compute register — a 4-region routing structure mapping
   `(argmax_sharpe vs Bonferroni_threshold, argmax_p_value)` to one of
   `signal_evidence` / `inconclusive` / `artifact_evidence` / etc.
   without interpretive judgment at any routing step — producing
   disposition output at mechanical-output register-class semantics.
   Pre-fire at Step 8 fire-prep boundary, an advisor cycle produced a
   prediction at interpretive-overlay register-class semantics
   (`artifact_evidence`) based on substantive interpretive framing of
   the cross-regime AND-gate evidence and cross-cycle directional
   improvement pattern. At Step 8 fire-time, Q22 LOCKED mechanical
   compute produced disposition `inconclusive` at primary anchor
   n_eff=197 (argmax sharpe 2.798 above null 2.487 with z=0.881
   positive but argmax p-value 0.189 in intermediate region 0.05 <
   p < 0.5 → Region 5 routing). The interpretive-overlay prediction
   and the mechanical-output disposition diverged at fire-time; the
   divergence surfaced as a §9.0c reviewer-register instance per
   closeout §8.2 row register #8 with explicit register-class label
   "Reviewer register" and codification candidate "§10 Item 5 reviewer
   over-interpretation prevention". The defect class is precisely
   interpretive-overlay register prediction applied to mechanical-
   output register output at reviewer engagement time without explicit
   register-class declaration distinguishing the two semantics.

The single PHASE2C_12 cycle instance represents the canonical
reviewer-register §9.0c defect class evidence basis at the metric /
output register-class declaration register; single-instance basis per
cycle is sufficient for Medium-tier codification per sub-spec §4.3.4
binding (register-class-distinction from §19 finding pattern density
and Strong-tier promotion contingency framing anchored at Tier
disposition register below). The pattern generalizes from the
PHASE2C_12 Step 8 instance to any Step deliverable containing metrics
and outputs at multiple register-classes; the trigger condition is
the deliverable authoring boundary itself. The register-class taxonomy
at the declaration block aligns with PHASE2C_13 sub-spec §3 §9.0c
register-class taxonomy 3-class sub-rule (sub-spec drafting / author-
ization / reviewer registers) at the reviewer-register class — the
§3 sub-rule operationalization detail codified separately at PHASE2C_13
implementation arc Step 5 per sub-spec §5.4 disposition (Item 6 §26
new-§ slot with §3 sub-rule fold-in at Application checklist).

### Application checklist

At each multi-step implementation arc Step deliverable authoring:

1. **Enumerate metric and output register-classes present in the
   deliverable.** The enumeration produces, for each metric and output
   cited in the deliverable, an explicit register-class label at
   register-precision: `mechanical-output` (deterministic compute
   output from Q-LOCKED routing or framework runtime resolution);
   `interpretive-overlay` (advisor pre-fire prediction, post-fire
   substantive interpretation, cross-cycle pattern observation, or
   other interpretive-judgment content layered over mechanical
   output); `intermediate` (compute output at intermediate register
   not yet routed to final disposition); `final` (terminal compute
   output bound at the deliverable as canonical disposition);
   `sensitivity` (parametric variation output at sensitivity axis).
   Enumeration precision requires reading the deliverable at register-
   precision, not summary register; metrics and outputs cited only
   indirectly require resolution to canonical register-class label
   before enumeration completes. Mirrors §21 + §22 + §23 Application
   checklist item 1 register-precision discipline at the parallel
   parameter / interface enumeration register-class.

2. **Author explicit register-class declaration block at deliverable
   §-opening.** The declaration block is a structurally-marked
   paragraph or table at the deliverable §-opening that enumerates
   register-class assignment per metric / output: "This deliverable
   operates at <register-class A> register for metrics <list>;
   <register-class B> register for metrics <list>; <register-class C>
   register for outputs <list>." The declaration may use prose
   register or table register at register-precision; what is load-
   bearing is that each metric / output enumerated at item 1 receives
   an explicit register-class label at the §-opening, and that the
   labels collectively cover the full enumerated set. Partial coverage
   (some metrics labeled, others left implicit) recreates the
   implicit-register-class gap that §25 catches at the reviewer
   engagement surface; full coverage at the §-opening preserves
   register-class semantics across the deliverable for downstream
   reviewer engagement.

3. **For each metric and output: bind register-class context inline
   at first reference site.** Beyond the §-opening declaration block,
   each metric and output receives an inline register-class binding
   at its first reference site within the deliverable body. The
   binding may be parenthetical ("disposition `inconclusive` at
   mechanical-output register"), prose-anchored ("at the mechanical-
   compute register the routing produced ..."), or annotation-
   anchored at the metric / output mention; what is load-bearing is
   that the first-reference site preserves the register-class context
   the §-opening declaration block established. Repeated mentions
   inherit the first-reference register-class binding by construction
   unless an explicit register-class transition is annotated;
   transitions across register-classes within the deliverable body
   are explicitly annotated at the transition site to preserve
   register-class semantics across the transition.

4. **Reviewer pass cycle prompt template includes register-class
   match verification annotation.** The reviewer prompt template
   authored at sub-spec specification register includes an explicit
   verification annotation: "For each metric and output cited in the
   deliverable, verify register-class declaration matches actual
   register-class semantics; flag any register-class mismatch as
   §9.0c reviewer-register instance candidate." The annotation
   applies uniformly across the active reviewer pass cycle
   invocations under scoping decision routing (advisor full-prose-
   access pass + ChatGPT structural overlay routinely; Codex
   adversarial pass when in scope per `feedback_codex_review_scope.md`
   substantive-deliverable routing). Reviewer prompt template
   specification authored at sub-spec specification register declares
   the intended reviewer pass cycle register-class for downstream
   reviewer-engagement reference; specification register at sub-spec
   register-class-distinct from invocation-binding at reviewer pass
   cycle register at runtime.

5. **Surface any register-class mismatch detected as §9.0c reviewer-
   register instance candidate at register-class-distinct register
   before deliverable SEAL fire.** Mismatch detected at reviewer pass
   cycle register (per item 4 verification annotation) or at
   deliverable authoring self-pass register logs at the cycle-
   internal §9.0c reviewer-register class log per PHASE2C_13 sub-spec
   §3 register-class taxonomy 3-class sub-rule operationalization
   register; the log entry's mitigation-note column carries the Step
   deliverable authoring boundary register-class annotation as
   metadata. Mismatch may be resolved before deliverable SEAL
   (declaration block patch + inline binding patch + reviewer pass
   cycle re-fire) or surfaced as carry-forward to next-cycle register
   if resolution is out-of-scope; either disposition requires explicit
   register-class logging at deliverable SEAL pre-fire boundary, not
   implicit propagation through SEAL. Mirrors §21 + §22 Application
   checklist item 5 register-class-distinct surfacing pattern at
   companion catch boundaries; routing target is §9.0c reviewer-
   register class log register (codified at PHASE2C_13 implementation
   arc Step 5 per sub-spec §5.4 disposition, Item 6 §26 new-§ slot
   with §3 sub-rule fold-in) rather than §19 finding register-class
   log register per §9.0c vs §19 register-class distinction at sub-
   spec §3 + §A1 register precedent.

The five-item checklist is structurally designed for mechanical
execution at Step deliverable authoring register: register-class
enumeration → §-opening declaration block authoring → inline first-
reference binding → reviewer prompt template specification with
verification annotation → mismatch surface routing. Mechanical
execution does not require interpretive judgment at any item; the
discipline operates as a procedural gate at the deliverable authoring
boundary, register-class-distinct from interpretive-register reviewer
pass cycle activities operating at substantive content register and
register-class-distinct from interpretive-register Step description
authoring at narrative content register.

### Failure-mode signal

Watch for Step deliverables authored without register-class
declaration block at the deliverable §-opening. The omission is the
primary defect §25 catches: absent the declaration block, reviewer
engagement at the deliverable surface operates at implicit-register-
class register, with metric / output register-class context inferred
from prose register rather than declared at register-precision.
PHASE2C_12 §9.0c instance #8 (canonical §8.2 row register) is concrete
evidence basis: absent §25 audit at Step 8 deliverable authoring
register, the interpretive-overlay register prediction (advisor pre-
fire `artifact_evidence` prediction) operated at the same deliverable
surface as the mechanical-output register disposition (Q22 LOCKED
`inconclusive` at primary anchor n_eff=197) without register-class
context distinguishing the two semantics, and the over-interpretation
defect surfaced at fire-time empirical observation register rather
than at deliverable authoring register-precision register.

Watch for register-class enumeration at summary register rather than
register-precision register. The pattern surfaces when the §-opening
declaration block enumerates register-classes by structural overlay
("the deliverable contains mechanical and interpretive content")
without resolving each metric / output to its canonical register-
class label. Summary-level enumeration covers the structural axis
but does not establish per-metric register-class precision; reviewer
pass cycle verifying register-class match against an unresolved
canonical assignment cannot detect mismatch by construction. Inherits
the register-precision discipline codified at §21 + §22 + §23
Failure-mode signal precedent at parallel enumeration register-class.

Watch for §-opening declaration block authored at structural register
without inline binding at first reference site. The pattern surfaces
when the declaration block lists register-class assignments at the
deliverable §-opening but the body content references metrics and
outputs without inline register-class context, leaving the §-opening
declaration disconnected from the body's register-class semantics.
Reviewer engagement at the body register-class then defaults to
implicit-register-class register for body content; the §-opening
declaration covers the structural-defect axis but does not establish
register-precision at the body register where the substantive
reviewer engagement occurs. Inline first-reference binding is load-
bearing for register-class semantics propagation across the
deliverable; declaration-only authoring (item 2 without item 3)
recreates the implicit-register-class gap pattern at the body
register.

Watch for reviewer pass cycle prompt template absent register-class
match verification annotation. The pattern surfaces when the reviewer
prompt template authored at sub-spec specification register includes
substantive content adjudication scope ("verify substantive content
quality") without the register-class match verification annotation
("verify register-class declaration matches actual register-class
semantics"). Substantive-only reviewer engagement covers the
substantive-defect axis at low cost but does not establish register-
class match precision; the reviewer cannot detect register-class
mismatch by construction without the verification annotation firing
at the engagement surface. Reviewer prompt template authoring
requires explicit register-class match verification annotation at
sub-spec specification register, not implicit reliance on reviewer
substantive overlay.

Watch for advisor pre-fire interpretive overlay applied to deter-
ministic mechanical compute output without explicit register-class
declaration distinguishing the two semantics. The pattern is the
canonical PHASE2C_12 §9.0c instance #8 defect class: a Q-LOCKED
mechanical compute (Q22 LOCKED routing producing disposition output)
fires at deterministic mechanical-output register-class semantics
with no interpretive judgment at any compute step; an advisor cycle
produces a pre-fire prediction at interpretive-overlay register-class
semantics layered over the same metric / output. Absent explicit
register-class declaration, prediction and compute output operate at
the same deliverable surface without register-class context; the
divergence between interpretive prediction and mechanical output
surfaces at fire-time empirical observation register rather than at
deliverable authoring register-precision register. Pattern recognition:
any pre-fire prediction over a deterministic mechanical compute
output requires explicit register-class declaration ("advisor pre-
fire prediction at interpretive-overlay register; Q-LOCKED compute
output at mechanical-output register") at deliverable §-opening to
preserve register-class semantics at adjudication surface; absent
declaration, the register-classes operate at conflated register
without distinguishing semantics, recreating the §9.0c reviewer-
register instance #8 defect class pattern.

Watch for deliverable SEAL fires under time pressure without §25
audit completed at the §-opening declaration block + inline binding
register. The pattern surfaces when SEAL pre-fire register elides
§25 audit on the framing that "register-class is obvious from prose
context" or "audit can fire at reviewer pass cycle instead." The
elision substitutes downstream register catch (reviewer pass cycle)
for the deliverable authoring register catch (§25 audit at §-opening
register); the substitution cost is reviewer over-interpretation
overhead at the downstream register relative to the same register-
class declaration audit at deliverable authoring register-precision.
The pattern is the canonical failure mode the discipline catches.

### Tier disposition

§25 ships at **Medium tier with cross-cycle-pending status note**.
The single PHASE2C_12 cycle §9.0c instance enumerated at Trigger
context (canonical §8.2 row register #8: advisor pre-fire interpretive
overlay on mechanical Q22 LOCKED compute output) gives the discipline
single-cycle empirical basis at reviewer-register §9.0c defect class
register. Single-instance basis per cycle is sufficient for Medium-
tier codification per sub-spec §4.3.4 binding. The provisional
Strong-tier candidate framing at sub-spec §2.5 codification mechanism
downgrades to Medium-tier-with-cross-cycle-pending at this Step 4
codification register per §4.3.4 binding (NO Strong-tier promotions
authorized at PHASE2C_13 cycle register; criterion 4 maturation
requirement fails by construction at first codification cycle); the
downgrade aligns with §21 + §22 + §23 tier disposition register
precedent at the same PHASE2C_13 implementation arc cycle.

Cross-cycle accumulation register is fed by historical PHASE2C_8.1 /
PHASE2C_9 / PHASE2C_10 / PHASE2C_11 instance backfill at the cycle-
complexity scaling diagnosis discipline (codified separately at
PHASE2C_13 implementation arc Step 7 per sub-spec §5.4 disposition,
Carry-forward A new-§ slot). §25 reviewer-register class scope
(interpretive-overlay vs mechanical-output mismatch at any deliverable
authoring boundary) is broader than §23 inter-step interface contract
gap class scope (Step N → Step N+1 boundary specifically); cross-cycle
accumulation density at §25 may accumulate at a denser register-class
than §23 sparse register, register-class-distinct from §19 finding
pattern accumulation at sub-spec → empirical reality drift boundary
per sub-spec §3 + closeout §8.2 register-class taxonomy precedent.
Strong-tier promotion is contingent on (i) Strong-tier promotion bar
criteria codified at the existing §13-§20 tier framework refinement
(codified at PHASE2C_13 implementation arc Step 9 per sub-spec §5.4
disposition, Carry-forward C fold-in to §20 appendix-style sub-§) and
(ii) cross-cycle accumulation evidence threshold met per the Strong-
tier bar; tier re-evaluation at successor methodology consolidation
cycle once both contingencies resolve. Medium tier preserves the
discipline at observation-backed application register without claiming
Strong-tier prescriptive force prematurely.

---

## §26 §9.0c instance density continuous-vs-batch improvement choice + register-class taxonomy preservation

### Principle

Methodology consolidation cycles accumulating §9.0c process-design observation
instances at cross-cycle measurement register require an explicit choice
between continuous improvement register (each instance triggers immediate
process patch at occurrence) and batch improvement register (instances
accumulate within cycle and mitigate at next consolidation cycle SEAL),
plus preservation of a register-class taxonomy for instance enumeration
that stays invariant across cycles. The continuous-vs-batch choice fires
at cycle-class register (which improvement register applies to the cycle);
the taxonomy preservation fires at instance-class register (each instance
receives a register-class label at the 3-class taxonomy: sub-spec drafting
/ authorization / reviewer). Bulk-mitigation against a single "process
failure" bucket collapses the taxonomy's register-class precision and is
explicitly rejected at this codification register; cross-cycle methodology
measurement of §9.0c density requires register-class-distinct counting,
not single-bucket counting, to preserve cross-cycle comparability anchor.

The discipline operates at register-class-distinct content scope from
§1 / §15 / §21 / §22 / §23 / §25 cluster, which catches per-instance
defects at workflow time boundaries (any drafting register / anchor receipt
/ sub-spec authoring of inter-step contracts / sub-spec SEAL pre-fire /
Step fire-prep / Step deliverable authoring). §26 catches defects at
cross-cycle observation density measurement register-class — how §9.0c
instances accumulate across cycles and which register-class taxonomy
applies to that accumulation register — rather than at a specific workflow
time boundary catch-class. The workflow catch-boundary chain ordering
established across §1 / §15 / §21 / §22 / §23 / §25 does not directly
govern §26's cross-cycle accumulation register-class; §26 is register-
class-orthogonal to the cluster at content scope axis.

§26 operates at register-class-coupled content scope with §18 §7 carry-
forward density at interpretive arc closeouts and §19 spec-vs-empirical-
reality finding pattern (all three at cross-cycle accumulation observation
register-class) but at register-class-distinct catch class: §18 catches
§7 carry-forward density at PHASE2C interpretive arc closeouts; §19
catches spec-vs-empirical-reality drift class; §26 catches §9.0c process-
design observation class. The pattern of register-class-distinct cross-
cycle accumulation observations across §18 / §19 / §26 preserves cross-
cycle comparability anchor at each register-class independently per Item 7
boundary clause invariance binding (taxonomy + counting invariant; only
mitigation TIMING varies per cycle-class binding). §26 operates at
register-class-distinct content scope from §16 anchor-prose-access
discipline (engagement fidelity register vs cross-cycle density mechanism
register) and from §17 procedural-confirmation defect class at first-
commit-before-prose-access (single-cycle implementer register vs cross-
cycle meta-measurement register). Cross-§ register-class collision is
avoided by content-scope distinction at register-precision across the
cluster.

The §3 sub-rule of PHASE2C_13 sub-spec operationalizes the 3-class
register-class taxonomy at register-precision register with mitigation
strategy enumeration per register-class + cross-cycle comparability
requirement per Item 7 boundary clause invariant. §3 folds into §26
Application checklist items 2 + 3 + 4 with internal sub-rule structure
per item; item 5 cross-references back to §3 of the sub-spec for full
sub-rule scope. The fold-in mechanism is register-class-parallel to §22
Item 4 fold-in at parent-operationalization coupling principle but
register-class-distinct at fold-in scope: both §22 and §26 fold-ins
operate at sub-rule level within Application checklist items (§22 has
sub-rules 4a/4b/4c at item 4; §26 has sub-rules 2a/2b/2c at item 2 +
3a/3b at item 3 + 4a/4b/4c/4d at item 4); the distinction is at scope
of items containing fold-in content — §22 fold-in is single-item
(item 4 only); §26 fold-in is multi-item (items 2 + 3 + 4) plus
cross-reference at item 5. Cross-§ collision at §22 ↔ §26 fold-in
mechanism is avoided by fold-in scope register-class distinction at
register-precision; the two fold-in mechanisms share parent-§ tier
disposition inheritance pattern at codification register.

### Trigger context

This discipline's empirical basis is eight PHASE2C_12 cycle §9.0c
process-design observation instances enumerated at canonical §8.2 row
register at PHASE2C_12 closeout
[`docs/closeout/PHASE2C_12_RESULTS.md`](../closeout/PHASE2C_12_RESULTS.md)
§8.2 (instance descriptions cited verbatim from §8.2 canonical source
artifact, not from sub-spec parenthetical labels per §22 Failure-mode
signal item 7 description-drift discipline). The eight instances span
heterogeneous register-classes; per Item 6 verbatim source at PHASE2C_12
closeout §10.2 lines 532-545, the 3-class register-class taxonomy
collapses the §8.2 canonical entries to clean register-class assignment.
The collapse operation functions as a canonicalization rule for cross-
cycle comparability measurement, not as a claim that the source event
was single-register in empirical reality:

> **Item 6 — §9.0c instance density mechanism + register-class taxonomy
> sub-rule.** PHASE2C_12 cycle accumulated 8 §9.0c instances (substantively
> higher than PHASE2C_10 + PHASE2C_11 at comparable cycle stages). Codify
> **continuous improvement vs batch improvement** register choice:
> - Each §9.0c instance should trigger immediate process patch (continuous)
> - vs current pattern of carry-forward to next consolidation cycle (batch)
> - **Sub-rule: §9.0c register-class taxonomy.** Single "process failure"
>   bucket collapses register-class distinctions. Codify taxonomy with
>   separate register-class enumeration:
>   - Sub-spec drafting register (instances #1, #2, #6)
>   - Authorization register (instance #3)
>   - Reviewer register (instances #4, #5, #7, #8)
> - Mitigation strategies are register-class-distinct; bulk-mitigation
>   collapses register-class precision.

The eight §8.2 row register entries enumerated at register-precision
register (instance description verbatim from §8.2 row register column 2;
register-class assignment per §10.2 Item 6 codification mechanism
collapsing §8.2 multi-class hybrid entries to 3-class taxonomy):

1. **§9.0c instance #1 — Sub-spec drafting cycle structural-overlay
   reviewer pass operating without empirical verification fire.** Sub-spec
   drafting register. Surfaced at PHASE2C_12 sub-spec drafting cycle
   authoring register where reviewer pass operated at structural-overlay
   register-class without empirical verification fire at canonical-
   artifact register; §22 framework parameter pre-lock audit discipline
   (codified at PHASE2C_13 implementation arc Step 2) addresses this
   defect class at sub-spec drafting cycle terminus catch-boundary.

2. **§9.0c instance #2 — Same-agent fresh-register full-file pass at
   sub-spec drafting cycle.** Sub-spec drafting register. Surfaced at
   PHASE2C_12 sub-spec drafting cycle reviewer pass operation register-
   class as carry-forward observation; cross-cycle accumulation register-
   class candidate per §17 sub-rule 4 recursive operating rule (full-file
   prose-access pass at sealed-commit register).

3. **§9.0c instance #3 — Authorization-routing momentum (auth #1
   implicit-cover Step 2 fire-prep).** Authorization register. Surfaced
   at PHASE2C_12 implementation arc register where authorization-routing
   momentum at auth #1 register implicit-covered Step 2 fire-prep
   operational fire boundary; anti-momentum-binding strict reading at
   Auth #6 + #6.y register addresses this defect class at authorization
   register-event boundary.

4. **§9.0c instance #4 — Reviewer divergence on Q10 operationalization
   site (entry vs config-driven).** Reviewer register. Surfaced at
   PHASE2C_12 sub-spec drafting cycle Q10 reviewer pass register where
   ChatGPT and Claude advisor diverged on Q10 operationalization site;
   resolved at Charlie register adjudication per reviewer-divergence-
   adjudication discipline at register-class-distinct register from bulk-
   accept anti-pattern.

5. **§9.0c instance #5 — Pre-fire structure validation gap (β1 narrow
   scope didn't audit allowlist parallel-structure with PHASE2C_11).**
   Reviewer register per §10.2 Item 6 codification (canonical §8.2 row
   register column lists "Multi-reviewer convergence"; collapse to
   reviewer register at 3-class taxonomy). Surfaced at PHASE2C_12 Step 8
   fire-prep boundary; folded into §16 Failure-mode signal at PHASE2C_12
   cycle close.

6. **§9.0c instance #6 — Fire-time discovery handoff-noise propagation
   (eligible≈154 PHASE2C_11 anchor → PHASE2C_12 actual 139).** Sub-spec
   drafting register per §10.2 Item 6 codification (canonical §8.2 row
   register column lists "Sub-spec drafting → fire-time"; collapse to
   sub-spec drafting register at 3-class taxonomy). Surfaced at PHASE2C_12
   Step 8 fire-time empirical register; §22 framework parameter pre-lock
   audit discipline addresses this defect class at sub-spec drafting
   cycle SEAL pre-fire boundary.

7. **§9.0c instance #7 — Multi-reviewer convergence on β1 narrow scope at
   auth #6.x didn't audit ALLOWED_DUAL_GATE_PAIRS for parallel-structure
   completeness with PHASE2C_11.** Reviewer register per §10.2 Item 6
   codification (canonical §8.2 row register column lists "Multi-reviewer
   + Charlie register convergence"; collapse to reviewer register at
   3-class taxonomy). Surfaced at PHASE2C_12 Auth #6.x register; resolution
   at Auth #6.y allowlist extension + baseline re-fire register.

8. **§9.0c instance #8 — Advisor pre-fire interpretive overlay on
   mechanical Q22 LOCKED compute output (predicted artifact_evidence;
   actual inconclusive at fire-time).** Reviewer register. Surfaced at
   PHASE2C_12 Step 8 fire-prep boundary where advisor cycle produced
   pre-fire prediction at interpretive-overlay register-class semantics
   layered over Q22 LOCKED mechanical compute output; §25 register-class
   explicit declaration discipline (codified at PHASE2C_13 implementation
   arc Step 4) addresses this defect class at deliverable authoring
   register.

Cross-cycle cumulative §9.0c count is not authoritatively established at
PHASE2C_10 + PHASE2C_11 register precedent (per PHASE2C_12 closeout §8.2
note "Cross-cycle cumulative §9.0c count: not authoritatively established
at this register"); cross-cycle accumulation register at the cycle-
complexity scaling diagnosis discipline (codified separately at PHASE2C_13
implementation arc Step 7 per sub-spec §5.4 disposition, Carry-forward A
new-§ slot) backfills PHASE2C_10 + PHASE2C_11 instance counts at canonical
register-class taxonomy. The eight PHASE2C_12 instances at canonical §8.2
row register establish single-cycle empirical basis at 3-class taxonomy
distribution (3 sub-spec drafting + 1 authorization + 4 reviewer)
sufficient for Medium-tier codification per sub-spec §4.3.4 binding.

### Application checklist

At each PHASE2C methodology consolidation cycle accumulating §9.0c process-
design observation instances:

1. **At cycle-entry: declare continuous-vs-batch improvement register
   choice for §9.0c instance handling at this cycle.** The declaration
   produces an explicit register-class label at register-precision:
   `continuous` (each §9.0c instance triggers immediate process patch at
   occurrence; mitigation fires real-time at instance surface event) or
   `batch` (instances accumulate within cycle and mitigate at next
   consolidation cycle SEAL register-event boundary). Default disposition
   is `batch` at consolidation cycle terminus register; `continuous`
   applies recursively when cycle scope binds Item 7 anti-meta-pattern
   discipline (codified at PHASE2C_13 implementation arc Step 6 per
   sub-spec §5.4 disposition, Item 7 §27 new-§ slot) — Item 7 boundary
   clause invariant: TIMING-only mutation; taxonomy + counting logic
   invariant per cross-cycle comparability requirement (sub-rule fold-in
   from PHASE2C_13 sub-spec §3.3 #3 mitigation timing variance allowed).
   The choice declaration ships at cycle scoping decision or sub-spec
   drafting cycle terminus register; absent the declaration, the cycle
   defaults to `batch` register at register-class-distinct outcome from
   explicit `continuous` binding under Item 7.

2. **At each §9.0c instance surface: assign register-class label per
   3-class taxonomy.** Sub-rule fold-in from PHASE2C_13 sub-spec §3.1
   3-class enumeration at operationalization-detail coupling register:

   - **(2a) Sub-spec drafting register.** §9.0c instances surfacing at
     sub-spec authoring activity register-class (implementer-time mechanics
     decision absent from sub-spec specification; sub-spec section
     structural choice ambiguity surfacing at authoring register; pre-
     empirical-verification structural-overlay reviewer pass register-
     class). PHASE2C_12 examples per §10.2 Item 6 codification: instances
     #1, #2, #6.

   - **(2b) Authorization register.** §9.0c instances surfacing at Charlie
     register authorization boundary register-class (authorization-routing
     ambiguity at register-event boundary; authorization scope ambiguity
     at adjudication register; authorization momentum at implicit-cover
     register-class violating anti-momentum-binding strict reading).
     PHASE2C_12 example per §10.2 Item 6 codification: instance #3.

   - **(2c) Reviewer register.** §9.0c instances surfacing at reviewer
     pass cycle register-class (reviewer over-interpretation at register-
     class divergence with mechanical compute output per §25; reviewer
     suggestion bulk-accept candidate; reviewer pass surface absent from
     sub-spec specification register; reviewer divergence on operationaliz-
     ation site at substantive-content register; pre-fire structure
     validation gap at multi-reviewer convergence register-class). PHASE2C_12
     examples per §10.2 Item 6 codification: instances #4, #5, #7, #8.

   Register-class label assignment precision requires reading the instance
   surface event at register-precision register, not summary register;
   multi-class hybrid entries at canonical §8.2 row register column collapse
   to single dominant register-class per Item 6 codification mechanism at
   3-class taxonomy invariant.

3. **At cycle-internal log: track cumulative count per register-class
   distinct.** Cross-cycle methodology measurement requires register-
   class-distinct counting, NOT single-bucket "process failure" counting;
   cumulative count register per cycle reads three register-class-distinct
   counts (sub-spec drafting + authorization + reviewer) plus single-
   bucket sum for cross-cycle comparison register. Item 7 boundary clause
   invariance binds two register-class-distinct invariants at this register
   (per sub-spec §3.3 #1 + #2 operational requirements): **taxonomy
   invariant** (3-class enumeration + register-class assignment rules
   stay fixed across cycles; new register-classes added only under
   cross-cycle comparability anchor preservation conditions per §3.3 #1)
   and **counting invariant** (instances NEVER removed or re-scoped
   retroactively from cumulative count; closure status changes preserve
   count register; cross-cycle cumulative comparison reads canonical register-
   class-distinct counts at cumulative register at canonical taxonomy
   invariant). Both invariants operate at register-class-distinct scope:
   taxonomy invariant binds register-class assignment rule stability;
   counting invariant binds instance enumeration register stability.
   Sub-rules at register-precision:

   - **(3a) Cluster-format log entries cross-cycle parse register-precision.**
     Cluster log entries at cycle-internal log MUST enumerate sub-defect
     count explicitly at mitigation note register (e.g., "#4-#10 cluster
     representing 7 distinct sub-defects per cluster surface event") for
     cross-cycle parse register-precision. Cumulative count register
     integrity requires per-defect numbering preserved across cluster;
     cross-cycle reader (PHASE2C_14+) parsing cluster format MUST sum
     per-defect numbers at cumulative count comparability anchor
     preservation. Cluster format is acceptable register-class for multi-
     defect single-surface-event logging when per-defect register-precision
     content enumerated at mitigation note + cumulative count clarification
     at closure status register (sub-rule fold-in from sub-spec §3.3 #6).

   - **(3b) Row-level mapping methodology for V#-anchor verification.**
     Cycle-internal log V#-anchor verification at cycle SEAL register-event
     boundary applies row-level 1:1 mapping methodology between log entries
     and boundary assessments at register-precision register, NOT string-
     count grep proxy. Verification methodology at register-precision:
     bounded-section awk extraction (e.g., `awk '/^## §A1/,/^## §A2/'`
     for §A1 + `awk '/^## §A2/,EOF'` for §A2) + row-grep at column-1
     instance-numbering pattern (e.g., `^\| #[0-9]+`) + closure-column
     N=clean count cross-check. Row count matches boundary assessment
     count at register-precision; cluster row at single boundary assessment
     = 1 mitigation entry per cluster surface event per Item 6 sub-rule
     register-class-distinct counting; cluster format does NOT violate
     1:1 row-to-boundary-assessment mapping at register-precision.
     **String-count "N=clean" grep proxy method is unreliable and discarded
     at PHASE2C_13 sub-spec drafting cycle SEAL boundary register-event
     per ChatGPT advisor SEAL pre-fire pushback** (sub-rule fold-in from
     sub-spec §3.3 #7).

4. **At mitigation: apply register-class-distinct mitigation strategy.**
   Mitigation strategies are register-class-distinct per sub-rule fold-in
   from PHASE2C_13 sub-spec §3.2; bulk-mitigation against single "process
   failure" bucket explicitly REJECTED at codification register. Each
   mitigation entry at cycle-internal log MUST include boundary compliance
   assessment (Y=BOUNDARY VIOLATION if mitigation altered taxonomy or
   counting; N=clean if mitigation altered TIMING or structure only) per
   sub-spec §3.3 #4 operational requirement; the boundary compliance column
   at log register itself catches violations at register-precision distinct
   from cycle SEAL pre-fire V#-chain register (the V#-chain anchor is a
   backup, not primary). Sub-rule fold-in at register-precision:

   - **(4a) Sub-spec drafting register mitigation strategies.** Pre-Task
     specification of mechanics decisions that would otherwise surface at
     implementer-time register; sub-spec section structural choice anchored
     at scoping decision binding scope; Items 1-N codification mechanism
     specified at register-precision per §13-§17 4-subsection precedent or
     fold-in slot per §5 fold-in 4-criteria check; §22 framework parameter
     pre-lock audit at sub-spec SEAL pre-fire register. Mitigation timing:
     at occurrence per Item 7 (a) lightweight tracking OR at sub-spec
     drafting cycle SEAL pre-fire per Item 7 (c) boundary-fire mitigation
     review.

   - **(4b) Authorization register mitigation strategies.** Authorization-
     routing discipline operating per
     [`feedback_authorization_routing.md`](../../.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_authorization_routing.md)
     hard rule (Charlie-register-only authorization for operational fires;
     reviewer convergence is advisory only); anti-momentum-binding strict
     reading at every authorization boundary; authorization sub-question
     surfacing at register-event boundary detection. Mitigation timing:
     at register-event boundary occurrence per Item 7 (a) lightweight
     tracking — authorization-class instances are typically real-time
     mitigation per anti-momentum-binding discipline (carry-forward
     batching of authorization decisions violates anti-momentum-binding
     strict reading register).

   - **(4c) Reviewer register mitigation strategies.** Reasoned reviewer-
     suggestion adjudication per
     [`feedback_reviewer_suggestion_adjudication.md`](../../.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_reviewer_suggestion_adjudication.md)
     (no bulk-accept; per-fix verification at register-precision register);
     reviewer scope clarification at sub-spec specification register (e.g.,
     Codex skip per scoping decision §5.3 +
     [`feedback_codex_review_scope.md`](../../.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_codex_review_scope.md);
     ChatGPT structural overlay vs Claude advisor full-prose-access pass
     register-class distinction); reviewer over-interpretation prevention
     per §25 register-class explicit declaration discipline at deliverable
     authoring register-class. Mitigation timing: at reviewer pass cycle
     iteration per Item 7 (a) OR at sub-spec drafting cycle SEAL pre-fire
     per Item 7 (c) when reviewer-pass-aggregated mitigation is appropriate.

   - **(4d) Mitigation-note text register-precision discipline at log
     entry register.** Mitigation-note text correction at log entry register
     (e.g., correcting self-contradictory claim that fails empirical
     verification against canonical anchor) preserves cycle-internal log
     boundary compliance N=clean at register-precision IF cumulative count
     register integrity preserved (instance still present at log; instance
     # preserved; closure status preserved; taxonomy register-class label
     preserved). Mitigation-note text register-precision discipline operates
     at register-class-distinct register from taxonomy/counting invariance
     (Item 7 boundary clause core); text correction at log register-class
     = register-precision-discipline-application register, NOT taxonomy/
     counting mutation (sub-rule fold-in from sub-spec §3.3 #5).

5. **Cross-reference §3 of PHASE2C_13 sub-spec
   [`docs/phase2c/PHASE2C_13_PLAN.md`](../phase2c/PHASE2C_13_PLAN.md)
   for full operationalization detail of register-class taxonomy 3-class
   sub-rule.** §3 of sub-spec contains the full sub-rule operationalization
   at register-precision register: §3.1 3-class enumeration with PHASE2C_12
   instance examples; §3.2 register-class-distinct mitigation strategies
   per register-class; §3.3 cross-cycle comparability requirement at Item 7
   boundary clause anchor with 7 operational requirements (3-class
   enumeration invariance / counting logic invariance / mitigation timing
   variance allowed / boundary compliance check / mitigation-note text
   register-precision / cluster-format log entries / row-level mapping
   methodology). Cross-reference register-class-distinct from items 1-4
   above — items 1-4 contain operationalization detail folded into §26
   Application checklist register; item 5 routes downstream readers to §3
   of sub-spec for full sub-rule scope at canonical artifact register.
   §3 of the sub-spec remains the authoritative operationalization source
   artifact for the sub-rule at drafting-cycle register; the Application
   checklist items 1-4 fold-in is operationalization-detail register-
   class derivative of §3, register-class-distinct from authoritative-
   source register binding at sub-spec §3.

The five-item checklist (with items 2 + 3 + 4 internally structured at
sub-rules per §3 fold-in mechanism; item 5 cross-references §3 of sub-spec
for full sub-rule scope) is structurally designed for mechanical execution
at cycle-class register (continuous-vs-batch choice + cycle-internal log
discipline) and at instance-class register (label assignment + mitigation
strategy application). Mechanical execution does not require interpretive
judgment at any item; the discipline operates as a procedural gate at
both registers, register-class-distinct from interpretive-register
reviewer pass cycle activities operating at substantive content register.

### Failure-mode signal

Watch for §9.0c instance enumeration at single "process failure" bucket
register without 3-class register-class taxonomy assignment. The omission
is the primary enumeration-collapse defect §26 catches: absent the
taxonomy, cross-cycle methodology measurement at cumulative count register
operates at single-bucket comparison register-class with register-class
precision collapsed across instance-class boundaries. PHASE2C_12 cycle 8
instances at canonical §8.2 row register with explicit register-class
column per §10.2 Item 6 codification register (3 sub-spec drafting + 1
authorization + 4 reviewer) is concrete evidence basis: absent §26
codification, cross-cycle comparability at PHASE2C_14+ measurement
register operates at register-class-collapsed comparison register,
recreating the register-class precision collapse pattern that Item 6
sub-rule explicitly rejects at enumeration register-class.

Watch for bulk-mitigation strategy applied across heterogeneous register-
class instances. The pattern surfaces when mitigation execution at cycle
SEAL register fires at single-strategy register-class (e.g., "improve
reviewer pass discipline" applied to instances spanning sub-spec drafting
+ authorization + reviewer register-classes) without register-class-
distinct mitigation strategy enumeration per §3.2 codification register.
Bulk-mitigation conflates the mitigation register-classes (sub-spec
drafting strategies = pre-Task specification + Items codification
mechanism; authorization strategies = anti-momentum-binding strict reading
+ register-event boundary detection; reviewer strategies = reasoned
reviewer-suggestion adjudication + reviewer scope clarification + reviewer
over-interpretation prevention) and recreates the register-class precision
collapse pattern at mitigation register-class — register-class-distinct
catch class from the enumeration-collapse pattern above; both patterns
share the meta-pattern of register-class precision collapse but operate
at register-class-distinct catch registers (enumeration vs mitigation).

Watch for cross-cycle methodology measurement comparison absent register-
class-distinct counting. The pattern surfaces when cross-cycle accumulation
register at consolidation cycle accumulation reads single-bucket cumulative
count comparison ("PHASE2C_12 had 8 instances; PHASE2C_11 had fewer")
without register-class-distinct counting at 3-class taxonomy register.
Single-bucket comparison covers structural axis at high-level overview
register but does not establish register-class precision at cumulative
count register; register-class distribution heterogeneity (e.g., 3 sub-
spec drafting + 1 authorization + 4 reviewer at PHASE2C_12 vs different
distribution at PHASE2C_11) is observable only at register-class-distinct
counting register. Cross-cycle comparability anchor preservation per Item
7 boundary clause invariant requires register-class-distinct counting at
cumulative count register; single-bucket counting corrupts the
comparability anchor by construction.

Watch for register-class label assignment at summary register rather than
register-precision register. The pattern surfaces when §9.0c instance
register-class assignment at cycle-internal log fires at structural overlay
register-class ("the instance is process-related" without 3-class taxonomy
label) rather than at register-precision register-class label per §3.1
canonical taxonomy. Multi-class hybrid entries at canonical §8.2 row
register column ("Multi-reviewer convergence" at #5; "Sub-spec drafting →
fire-time" at #6; "Multi-reviewer + Charlie register convergence" at #7)
require resolution to single dominant register-class per Item 6
codification mechanism collapse rule before instance enumeration completes
at register-precision register. Inherits the register-precision discipline
codified at §21 + §22 + §23 + §25 Failure-mode signal precedent at
parallel enumeration register-class.

Watch for cluster-format log entries authored without per-defect numbering
or sub-defect count enumeration at mitigation note register, plus V#-
anchor verification at cycle-internal log applied via string-count grep
proxy method at full-file register rather than row-level 1:1 mapping
methodology at bounded-section register. Both patterns conflate register-
class-distinct counting registers: cluster entries without per-defect
numbering recreate register-class precision collapse at cumulative count
register (cross-cycle reader unable to distinguish single-instance cluster
vs multi-instance cluster at register-precision); string-count grep proxy
method conflates row-level instance entries with prose summary mentions
at register-class-distinct registers (e.g., "N=clean" in prose summary
text counts as string match identical to row-level closure-column N=clean
at instance entry register), producing register-class precision collapse
at verification register-class. Row-level 1:1 mapping methodology at
bounded-section register-precision is the binding verification methodology
per §3.3 #7 operational requirement; string-count grep proxy method is
unreliable and discarded at PHASE2C_13 sub-spec drafting cycle SEAL
boundary register-event per ChatGPT advisor SEAL pre-fire pushback.

Watch for mitigation-note text correction without explicit boundary
compliance check against cumulative count register integrity. The pattern
surfaces when mitigation-note text correction at log entry register fires
without explicit verification that cumulative count register integrity
preserved (instance presence at log; instance # preservation; closure
status preservation; taxonomy register-class label preservation).
Mitigation-note text register-precision discipline operates at register-
class-distinct register from Item 7 boundary clause core (taxonomy +
counting invariance); text correction may introduce taxonomy mutation or
counting mutation by mistake if boundary compliance check elided at
correction register. Boundary compliance check at every mitigation per
§3.3 #4 operational requirement catches both text correction and core
mitigation alterations at cycle-internal log register itself, register-
class-distinct from cycle SEAL pre-fire V#-chain verification register.

Watch for continuous-vs-batch choice elided at cycle-entry register without
explicit declaration. The pattern surfaces when methodology consolidation
cycle entry fires without explicit `continuous` or `batch` register-class
declaration, defaulting to `batch` register at register-class-distinct
outcome from explicit `continuous` binding under Item 7 anti-meta-pattern
discipline (codified at §27 codification register at PHASE2C_13 implementation
arc Step 6 per sub-spec §5.4 disposition). Cycles binding Item 7 require
explicit `continuous` declaration with Item 7 boundary clause invariant
preservation (TIMING-only mutation; taxonomy + counting logic invariant);
absent declaration, cycles default to `batch` register-class without Item
7 binding, recreating the carry-forward to next-consolidation-cycle pattern
that Item 6 codification mechanism explicitly identifies as the discipline's
trigger context.

Watch for description drift between sub-spec parenthetical labels and
canonical §8.2 row register descriptions. The pattern surfaces when sub-
spec body cites §9.0c instance entries by number plus parenthetical
description, where the parenthetical description diverges from the
canonical §8.2 source-artifact entry at the cited number. Inherits the
description-drift discipline codified at §22 Failure-mode signal item 7
register-class precedent applied to §9.0c register-class taxonomy
enumeration register; the drift is a sub-class of handoff-noise propagation
between sub-spec authoring register and canonical source artifact register,
undetected at sub-spec SEAL pre-fire absent register-precision empirical
verification per §1 + §15 disciplines. §26 Trigger context citation
discipline binds verbatim citation from canonical §8.2 row register, not
sub-spec §3.1 parenthetical labels, at codification register precedent.

### Tier disposition

§26 ships at **Medium tier with cross-cycle-pending status note**. The
eight PHASE2C_12 cycle §9.0c instances enumerated at Trigger context
(canonical §8.2 row register #1-#8 with register-class assignment per
§10.2 Item 6 codification mechanism: 3 sub-spec drafting + 1 authorization
+ 4 reviewer at 3-class taxonomy distribution) give the discipline single-
cycle empirical basis at cross-cycle observation density measurement
register-class, sufficient for Medium-tier codification per sub-spec §4.3.4
binding. The provisional Strong-tier candidate framing at sub-spec §2.6
codification mechanism downgrades to Medium-tier-with-cross-cycle-pending
at this Step 5 codification register per §4.3.4 binding (NO Strong-tier
promotions authorized at PHASE2C_13 cycle register; criterion 4 maturation
requirement fails by construction at first codification cycle); the
downgrade aligns with §21 + §22 + §23 + §25 tier disposition register
precedent at the same PHASE2C_13 implementation arc cycle.

Cross-cycle accumulation register is fed by historical PHASE2C_8.1 /
PHASE2C_9 / PHASE2C_10 / PHASE2C_11 instance backfill at the cycle-
complexity scaling diagnosis discipline (codified separately at PHASE2C_13
implementation arc Step 7 per sub-spec §5.4 disposition, Carry-forward A
new-§ slot). The backfill ships register-class-distinct counting at 3-class
taxonomy invariant per §3.3 #1 operational requirement; cross-cycle
distribution comparison reads register-class-distinct counts at cumulative
register at canonical taxonomy invariant. Strong-tier promotion is
contingent on (i) Strong-tier promotion bar criteria codified at the
existing §13-§20 tier framework refinement (codified at PHASE2C_13
implementation arc Step 9 per sub-spec §5.4 disposition, Carry-forward C
fold-in to §20 appendix-style sub-§) and (ii) cross-cycle accumulation
evidence threshold met per the Strong-tier bar; tier re-evaluation at
successor methodology consolidation cycle once both contingencies resolve.
Medium tier preserves the discipline at observation-backed application
register without claiming Strong-tier prescriptive force prematurely.

The §3 sub-rule fold-in at Application checklist items 2 + 3 + 4 + cross-
reference at item 5 inherits §26's tier disposition at register-precision
per §22 Item 4 fold-in tier inheritance precedent; fold-in scope register-
class-distinct between §22 single-item vs §26 multi-item scope per
Principle ¶4 framing. The §3 evidence basis (3-class taxonomy
operationalization at PHASE2C_13 sub-spec drafting cycle register + 7
operational requirements at §3.3 + canonical PHASE2C_12 instance examples
at §3.1) supports the parent §26 tier disposition at fold-in register
without requiring separate §3 sub-rule tier evaluation.

---

## §27 Item 7 anti-meta-pattern discipline at methodology consolidation cycles (real-time §9.0c instance handling with boundary clause)

### Principle

Methodology consolidation cycles that codify §26's continuous-vs-batch
improvement choice for §9.0c process-design observation instance handling
AND simultaneously accumulate new §9.0c instances internal to the cycle
require recursive operationalization of the same continuous-vs-batch
choice applied to the cycle that is itself codifying §26. The recursion
trigger fires at cycle scope register: a cycle codifying §9.0c discipline
while violating §9.0c discipline within the cycle that ships the
codification produces an anti-meta-pattern register-class precision
collapse — the codification artifact ships at canonical-artifact register
while the cycle that ships it carries unmitigated §9.0c instances at
cycle-internal register, recreating the carry-forward to next-consolidation-
cycle pattern that §26 explicitly identifies as the discipline's trigger
context. §27 binds the cycle to mitigate accumulated §9.0c instances at
real-time per Item 7's continuous register choice rather than carry-
forward to next consolidation cycle per default batch register, when the
cycle is itself codifying §9.0c-related discipline.

The discipline operates under a load-bearing boundary clause invariant:
TIMING-only mutation. Item 7 changes WHEN mitigation fires (real-time
at instance occurrence vs batch at next consolidation cycle SEAL); Item 7
does NOT change §9.0c register-class taxonomy (3-class enumeration —
sub-spec drafting / authorization / reviewer — at instance-class register
per §26 Application checklist item 2 + sub-rules 2a/2b/2c) and does NOT
change §9.0c counting logic (cumulative count register integrity at cycle-
internal log + cross-cycle accumulation register per §26 Application
checklist item 3 + sub-rules 3a/3b). The TIMING-only invariant preserves
cross-cycle comparability of §9.0c measurement at register-class-distinct
counting register — the binding cross-cycle anchor codified at §26 Trigger
context cumulative count register binding and at §3.3 #1 + #2 operational
requirements. Mitigation that alters taxonomy (e.g., reclassifying instance
to a different register-class to "fix" it) or alters counting (e.g.,
removing instance from cumulative count to "close" it) corrupts cross-cycle
comparability by construction at register-class-distinct catch class from
the timing register; the boundary clause binds both invariants at every
mitigation register as a load-bearing necessary condition.

§27 operates at register-class-distinct content scope from §26 at recursion
scope register but at register-class-coupled content scope with §26 at
parent-recursive register. §26 codifies §9.0c instance density mechanism +
3-class register-class taxonomy preservation discipline at base register —
the cross-cycle observation density measurement register-class. §27 codifies
recursive operationalization of §26's continuous-vs-batch register choice +
boundary clause invariance discipline at meta-recursion register-class —
the cycle-class register at which the continuous-vs-batch choice applies
to the cycle that codifies §26. The parent-recursive coupling binds cross-
cycle comparability anchor through both registers: §26 binds taxonomy +
counting invariance at instance-class register per Application checklist
item 3 sub-rules 3a/3b; §27 binds TIMING-only-mutation invariance at cycle-
class register per Application checklist item 4 sub-rules 4a/4b/4c. Cross-§
register-class collision at §26 ↔ §27 framing is avoided by content-scope
distinction at register-precision: §26 = base codification at instance-
class register; §27 = recursive operationalization at cycle-class register.
The §27 codification ships immediately after §26 in the PHASE2C_13
implementation arc § append sequence per sub-spec §5.4 disposition (Item 7
row), preserving register-class precision against fold-in to §26 host slot
which would have collided with §26's base register at register-class
assignment register.

§27 is register-class-orthogonal to the §1 / §15 / §21 / §22 / §23 / §25
per-instance catch-boundary cluster at content scope axis, parallel to §26's
register-class-orthogonal framing at §26 Principle ¶2. The cluster catches
defects at workflow time boundaries (any drafting register / anchor receipt /
sub-spec authoring of inter-step contracts / sub-spec SEAL pre-fire /
Step fire-prep / Step deliverable authoring); §27's specific catch class is
recursive operationalization of §26's continuous-vs-batch register choice +
boundary clause invariance preservation rather than a workflow time boundary
catch-class. §27 register-class-coupled content scope with §26 at parent-
recursive register-precision register; §27 register-class-coupled content
scope with §18 §7 carry-forward density at interpretive arc closeouts and
§19 spec-vs-empirical-reality finding pattern at cross-cycle accumulation
observation register-class but at register-class-distinct catch class:
§18 catches §7 carry-forward density; §19 catches spec-vs-empirical-reality
drift; §27 catches anti-meta-pattern discipline at methodology consolidation
cycles binding §26-related codification.

The Item 7 scope binding at canonical-artifact register operationalizes
Reading (iii) per PHASE2C_13 sub-spec §2.7 Q-S27a Charlie register
adjudication outcome (RESOLVED at sub-spec SEAL `92d8c45`): Item 7 scope =
§9.0c instances + §19 spec-vs-empirical-reality instances + future-pattern
register-class-distinct logs (3 pattern register-classes accommodated;
specific future patterns NOT pre-committed per anti-pre-naming discipline).
PHASE2C_13 sub-spec operationalizes Reading (iii) with §A1 (§9.0c) + §A2
(§19) cycle-internal logs at full Item 7 mechanism (5-column schema +
boundary compliance column + cumulative count register preservation per
Item 7 boundary clause invariant). Future methodology consolidation cycles
binding §27 anti-meta-pattern discipline MAY add new pattern register-class
logs (e.g., a new §A_N register-class-distinct log for emergent process-
finding patterns surfaced at future cycle internal) per the same Item 7
discipline at future scoping cycle adjudication register-event boundary;
the scope codification breadth at Reading (iii) does NOT mutate Item 7
boundary clause invariant per §2.7 specification register binding —
taxonomy + counting register-class-distinct from scope register-class
at Item 7 boundary clause register-precision register. Anti-pre-naming
preserved at canonical-artifact register: specific future-pattern register-
class additions are register-class-distinct future-cycle scoping decision
register, NOT pre-committed at PHASE2C_13 §27 codification register.

### Trigger context

This discipline's empirical basis is one PHASE2C_13 cycle instance per
Item 7 verbatim source at PHASE2C_13 scoping decision
[`docs/phase2c/PHASE2C_13_SCOPING_DECISION.md`](../phase2c/PHASE2C_13_SCOPING_DECISION.md)
§6.2 lines 272-278 (instance description cited verbatim from canonical
scoping decision source artifact, not from sub-spec §2.7 parenthetical
labels per §22 Failure-mode signal item 7 description-drift discipline
applied to Item 7 verbatim source register):

> **Item 7** — Real-time §9.0c instance handling at PHASE2C_13 cycle
> internal. Operationalization of Item 6's continuous-vs-batch register
> choice applied recursively to PHASE2C_13 itself (anti-meta-pattern
> discipline; mitigate as surfaced, not carry-forward to next consolidation
> cycle).
>
> **Boundary clause (binding):** Item 7 changes mitigation TIMING only,
> NOT taxonomy or counting logic. §9.0c register-class taxonomy (sub-spec
> drafting / authorization / reviewer) stays invariant across cycles;
> counting logic stays invariant; only WHEN mitigation is applied changes
> (real-time vs carry-forward-batch). Cross-cycle comparability preserved.
>
> **Operationalization mechanism (defer to sub-spec):** advisor lean =
> (a) lightweight tracking (PHASE2C_13 cycle maintains running §9.0c
> instance log; each instance surface triggers immediate mitigation note
> in sub-spec drafting cycle internal) + (c) boundary-fire mitigation
> review (§9.0c instances reviewed at cycle boundary fires: scoping SEAL /
> sub-spec SEAL / closeout SEAL); (b) recursive mini-codification REJECTED
> (infinite recursion risk). Specific mechanism authored at sub-spec
> drafting cycle.

The Item 7 codification is a difficult methodology concept at register-
precision register — recursive operationalization of Item 6 applied to
the cycle that codifies Item 6 + boundary clause TIMING-only mutation
invariant + (b) recursive mini-codification REJECTED at infinite recursion
risk. The bilingual concept anchor below operationalizes the discipline
anchor at PHASE2C_13 sub-spec §0.3 register (bilingual explanation for
difficult methodology concepts) at the canonical-artifact register where
the discipline is codified for cross-cycle reading:

**Bilingual concept anchor:**

- **English:** Item 7 applies Item 6's continuous-improvement register
  choice recursively to the methodology consolidation cycle that is
  itself authoring §26 codification. The cycle codifies §9.0c discipline
  at canonical-artifact register while ALSO accumulating new §9.0c
  instances at cycle-internal register; Item 7 binds the cycle to mitigate
  as surfaced (real-time per (a)+(c) operationalization) rather than
  carry-forward to the next consolidation cycle. **Boundary clause:**
  TIMING-only mutation. Don't change taxonomy (3-class register-class
  enumeration: sub-spec drafting / authorization / reviewer); don't
  change counting (cumulative count register integrity). Only change WHEN
  mitigation fires (real-time at occurrence vs batch at next-cycle SEAL).
  This protects cross-cycle comparability of §9.0c measurement at
  register-class-distinct counting register. **(b) recursive mini-
  codification REJECTED:** infinite recursion risk. Codifying methodology
  for §9.0c instances accumulated at the cycle that codifies §9.0c
  instance handling = infinite recursion. Stop at (a) lightweight tracking
  + (c) boundary-fire mitigation review combined.

- **中文:** Item 7 把 Item 6 的连续改进 (continuous improvement) register
  选择递归地应用到正在 author §26 codification 的 methodology
  consolidation cycle 自身。该 cycle 在 canonical-artifact register codify
  §9.0c discipline 的同时也在 cycle-internal register 积累新的 §9.0c
  instances; Item 7 binds the cycle 实时 mitigate (出现就处理 — 通过
  (a)+(c) operationalization) 而不是 carry-forward 到下一 consolidation
  cycle。**Boundary clause (边界条款):** 只能改 TIMING (时机), 不能改
  taxonomy (分类: 3-class register-class 枚举 — sub-spec drafting /
  authorization / reviewer) 或 counting (cumulative count register 完整性)。
  只改 WHEN mitigation fires (occurrence 时实时 vs next-cycle SEAL 时 batch)。
  这是为了保护 §9.0c measurement 在 register-class-distinct counting register
  的 cross-cycle comparability (跨 cycle 可比性)。**(b) recursive mini-
  codification 明确 REJECTED:** 无限递归风险。为 cycle 内 §9.0c instances
  专门 codify methodology, 而该 cycle 自身正在 codify §9.0c instance handling
  = 无限递归。停在 (a) lightweight tracking + (c) boundary-fire mitigation
  review 的组合。

PHASE2C_13 cycle is the first concrete instance binding §27 anti-meta-
pattern discipline. The cycle codifies Item 6 (§26) at PHASE2C_13
implementation arc Step 5 + Item 7 (§27) at this Step 6 + accumulates
§A1 §9.0c instances at sub-spec drafting cycle internal register (6
instances cumulative at sub-spec SEAL `92d8c45` per §A1 cumulative count
register) + §A2 §19 instances at cycle-internal register under Reading
(iii) scope binding (15 instances cumulative at sub-spec SEAL per §A2
cumulative count register). Each instance was logged at occurrence per
Item 7 (a) lightweight tracking with boundary compliance column at
register-precision; each instance was reviewed at cycle boundary fires
per Item 7 (c) (sub-spec SEAL pre-fire V#-chain anchor at sub-spec §7.1
register; implementation arc Step SEAL pre-fire register at each of Steps
1-5 that completed before this Step 6); each mitigation preserved Item 7
boundary clause invariant per boundary compliance column N=clean register
across all logged instances at sub-spec SEAL register. The pattern recurs
at any future methodology consolidation cycle that ships §9.0c-related or
§19-related codification under Reading (iii) scope binding; future cycles
binding §27 inherit the same discipline at register-class-distinct cycle
register, with PHASE2C_13 sub-spec §A1 + §A2 5-column schema as canonical
instance log template per Application checklist item 1 below.

### Application checklist

At each methodology consolidation cycle binding §27 anti-meta-pattern
discipline at cycle-class register:

1. **At cycle-entry: initialize cycle-internal pattern-class register-class-
   distinct log(s) at register-precision schema.** The log schema is a
   five-column register at the cycle-internal artifact: instance # /
   register-class / surface task+step / mitigation note (per Item 7
   (a)+(c) operationalization) / Item 7 boundary compliance + closure
   status. Per Reading (iii) scope binding, additional pattern-class
   register-class-distinct logs MAY be initialized in parallel: §9.0c
   instance log per §26 codification scope; §19 instance log per §19
   codification scope; emergent future-pattern logs per future-cycle
   scoping decision adjudication register-event boundary. PHASE2C_13
   sub-spec §A1 (§9.0c) + §A2 (§19) at canonical artifact register are
   the canonical instance-log templates; cross-cycle readers (PHASE2C_14+)
   inherit the 5-column schema register-class-distinct from prose summary
   register at sub-spec body. Log initialization at cycle-entry register
   precedes any instance surface event at cycle-internal register; absent
   log initialization at cycle-entry, instances surface without register-
   class assignment register-precision and the §27 discipline operates
   at fallback batch register rather than continuous register.

2. **At each instance surface during cycle: log to cycle-internal register
   at occurrence per Item 7 (a) lightweight tracking.** Each instance
   surface event at cycle-internal register triggers a log row at register-
   precision register: instance # at next-sequential register (or cluster-
   range register per §26 Application checklist sub-rule 3a if multi-
   defect single-surface-event); register-class assignment per §26
   Application checklist item 2 + sub-rules 2a/2b/2c (sub-spec drafting /
   authorization / reviewer) for §9.0c logs, or per §19 Trigger context
   register binding for §19 logs, or per future-pattern register-class
   binding for emergent pattern logs; surface task+step at register-
   precision (cycle-internal session + task identifier); mitigation note
   placeholder pending Item 7 (c) boundary-fire mitigation review at next
   cycle boundary fire. Real-time logging at occurrence preserves cross-
   cycle comparability anchor at cumulative count register per §26
   Application checklist item 3 + sub-rules 3a/3b counting invariant
   binding.

3. **Apply mitigation per cycle-internal context: (a) lightweight tracking
   + (c) boundary-fire mitigation review combined.** Some instances
   mitigate at occurrence at register-event boundary detection register
   (e.g., authorization-class instances per §26 Application checklist
   sub-rule 4b register; structural patches at sub-spec drafting register
   that surface at register-event boundary detection); some instances
   mitigate at cycle-boundary fire register per (c) boundary-fire mitigation
   review at scoping SEAL / sub-spec SEAL / closeout SEAL register-event
   boundary. Both timing choices preserve cross-cycle comparability anchor
   at cumulative count register per Item 7 boundary clause invariant
   binding (per §3.3 #3 mitigation timing variance allowed operational
   requirement). Mitigation strategy register-class-distinct per §26
   Application checklist item 4 + sub-rules 4a/4b/4c at register-class-
   distinct mitigation strategy enumeration; bulk-mitigation against single
   "process failure" bucket at cross-class scope explicitly REJECTED at
   §26 codification register.

4. **At every mitigation: BOUNDARY CLAUSE COMPLIANCE CHECK.** The
   compliance check is the load-bearing mechanical execution gate at
   §27 codification register. Each mitigation entry at cycle-internal
   log MUST include boundary compliance assessment at register-precision
   register: Y=BOUNDARY VIOLATION if mitigation altered taxonomy (register-
   class assignment rule mutation per §26 Application checklist items 2 +
   3 + §3.3 #1 taxonomy invariant — item 2 binds 3-class enumeration
   operationalization at instance-class register; item 3 binds taxonomy
   invariance at cumulative count register) or altered counting (cumulative
   count register mutation per §26 Application checklist item 3 + §3.3 #2
   counting invariant); N=clean if mitigation altered TIMING (when
   mitigation fires) or structure (sub-spec text patches at register-
   precision; mitigation-note text correction at register-precision per
   §26 Application checklist sub-rule 4d) only. The boundary compliance
   column at log register itself catches violations at register-precision
   register-class-distinct from cycle SEAL pre-fire V#-chain register
   (the V#-chain anchor at SEAL is a backup, not primary). Sub-rules at
   register-precision:

   - **(4a) TIMING mutation at register-precision.** Mitigation that
     alters WHEN mitigation fires — real-time at occurrence (Item 7 (a)
     lightweight tracking immediate mitigation) vs batch at SEAL (Item 7
     (c) boundary-fire mitigation review) vs default-batch at next-cycle
     SEAL (absent Item 7 binding) — is TIMING-only mutation. TIMING
     mutation preserves taxonomy invariant + counting invariant per §27
     Principle ¶2 boundary clause core; N=clean register-class at
     boundary compliance column per construction.

   - **(4b) Taxonomy mutation prohibited.** Mitigation that alters
     register-class assignment rules at §9.0c 3-class enumeration (e.g.,
     reclassifying instance from reviewer-register to sub-spec-drafting-
     register at log entry register to "fix" it; renaming register-class
     labels retroactively across log entries; collapsing multiple
     register-classes to single bucket at mitigation register) violates
     taxonomy invariant per §26 Application checklist items 2 + 3 + §3.3
     #1 operational requirement (item 2 = 3-class enumeration operationaliz-
     ation register; item 3 = taxonomy invariance binding register at
     cumulative count register). Y=BOUNDARY VIOLATION register-class at
     boundary compliance column; corrupts cross-cycle comparability
     anchor at register-class-distinct counting register by construction.

   - **(4c) Counting mutation prohibited.** Mitigation that alters
     cumulative count register at cycle-internal log (e.g., removing
     instance from cumulative count to "close" it; renumbering instances
     retroactively at log entry register; collapsing cluster-format
     entries to single-count without per-defect numbering preservation
     per §26 Application checklist sub-rule 3a) violates counting
     invariant per §26 Application checklist item 3 + §3.3 #2 operational
     requirement. Y=BOUNDARY VIOLATION register-class at boundary
     compliance column; corrupts cross-cycle cumulative count comparison
     register at canonical-artifact register by construction.

5. **(b) recursive mini-codification REJECTED at codification register.**
   The (b) operationalization option from PHASE2C_13 scoping decision
   §6.2 Item 7 source artifact register — codifying methodology
   specifically for §9.0c instances accumulated at the cycle that
   codifies §9.0c instance handling discipline — produces infinite
   recursion at codification register-class: codifying-the-cycle-that-
   codifies-the-codification opens a new codification scope that itself
   becomes subject to §27 anti-meta-pattern discipline at the next
   codification register, ad infinitum. The discipline binds (a) +
   (c) combined at operationalization register without (b) recursive
   register-class-distinct codification per scoping decision §6.2 +
   sub-spec §2.7 verbatim binding. Reviewer pass cycle authoring + Failure-
   mode signal authoring at §27 codification register MUST preserve
   the (b) explicit REJECTION at register-precision register-class;
   recursive mini-codification framing surfacing at reviewer pass cycle
   register (e.g., "we should codify methodology for §9.0c instances
   accumulated at this cycle" framing applied to §27 itself) is explicitly
   rejected at §27 codification scope register.

6. **At cycle SEAL pre-fire: V#-chain anchor verifies Item 7 boundary
   clause preservation across cycle-internal log register.** The
   verification methodology operates at row-level 1:1 mapping register
   per §26 Application checklist item 3 + sub-rule 3b (bounded-section
   awk extraction + row-grep at column-1 instance-numbering pattern +
   closure-column N=clean count cross-check). String-count grep proxy
   method at full-file register is unreliable and discarded per ChatGPT
   advisor SEAL pre-fire pushback at PHASE2C_13 sub-spec drafting cycle
   SEAL boundary register-event (codified at §26 sub-rule 3b register).
   V#-chain anchor at cycle SEAL register-event boundary catches Item 7
   boundary clause violations as backup register-class-distinct from log-
   register boundary compliance column primary catch; both registers
   binding the boundary clause invariant per Item 7 codification register
   binding at parallel-register-class catch points per §27 Principle ¶2
   register-class-distinct catch class structure.

The six-item checklist (with sub-rules at item 4 register-class-distinct
TIMING / taxonomy / counting mutation framework + item 5 explicit (b)
REJECTION binding) is structurally designed for mechanical execution
at cycle-class register (Item 7 (a)+(c) operationalization choice + cycle-
internal log discipline + boundary compliance check) at register-class-
distinct catch points across cycle scope. Mechanical execution does not
require interpretive judgment at any item; the discipline operates as a
procedural gate at cycle-class register, register-class-distinct from
interpretive-register reviewer pass cycle activities operating at
substantive content register and register-class-distinct from §26's
instance-class register Application checklist mechanical execution scope.

### Failure-mode signal

Watch for cycle codifying §26 (or other §9.0c-related discipline) at
canonical-artifact register while violating §26 internally at cycle-
internal register. The pattern surfaces when a methodology consolidation
cycle ships §9.0c-related codification at SEAL register while accumulating
new §9.0c instances at cycle-internal register without mitigation per
Item 7 (a)+(c) operationalization. Anti-meta-pattern register-class
precision collapse: codification artifact ships at canonical-artifact
register while cycle-internal register carries unmitigated instances at
batch register, recreating the carry-forward to next-consolidation-cycle
pattern that §26 Trigger context explicitly identifies as the discipline's
trigger context. Absent §27 binding, the cycle defaults to batch register
without explicit `continuous` declaration per §26 Application checklist
item 1 register; the absence is the failure mode at cycle-class register.

Watch for mitigation altering taxonomy or counting at cycle-internal log
register. The pattern surfaces in two register-class-distinct sub-classes:
register-class assignment mutation (mitigation reclassifies instance from
register-class A to register-class B at log entry register to "fix" the
instance; renames register-class labels across log entries retroactively;
collapses multi-register-class instances to single bucket at mitigation
register); cumulative count register mutation (mitigation removes instance
from cumulative count to "close" it; renumbers instances retroactively
disrupting cross-cycle comparison anchor; collapses cluster-format entries
to single-count without per-defect numbering preservation per §26
Application checklist sub-rule 3a). Both sub-classes corrupt cross-cycle
comparability of §9.0c measurement at register-class-distinct catch class
from the timing register; the boundary clause binds both invariants at
every mitigation register as a load-bearing necessary condition per
§27 Application checklist item 4 sub-rules 4b/4c register-class-distinct
prohibitions.

Watch for (b) recursive mini-codification temptation surfacing at reviewer
pass cycle authoring or Failure-mode signal authoring register. The
pattern surfaces when reviewer pass cycle iteration on §27 codification
register-class authoring framing concrete content register-class-distinct
from §27 codification scope, drifting toward "we should codify methodology
specifically for §9.0c instances accumulated at this codification cycle"
framing applied recursively to §27's own codification scope. The framing
recreates the infinite recursion risk that scoping decision §6.2 + sub-
spec §2.7 verbatim binding explicitly REJECTS at (b) operationalization
option register; (a) lightweight tracking + (c) boundary-fire mitigation
review combined is the binding operationalization scope at §27 codification
register without (b) recursive register-class-distinct codification.
Reviewer pass cycle authoring + Failure-mode signal authoring register
MUST preserve the (b) explicit REJECTION at register-precision register-
class per §27 Application checklist item 5 binding.

Watch for cycle-entry continuous-vs-batch register choice declaration
elided at §26 Application checklist item 1 register binding. The pattern
surfaces when methodology consolidation cycle entry fires without explicit
`continuous` register declaration under Item 7 binding scope; the cycle
defaults to `batch` register at register-class-distinct outcome from
explicit `continuous` binding per §26 Application checklist item 1 register
binding. Cycles binding §27 anti-meta-pattern discipline require explicit
`continuous` declaration with Item 7 boundary clause invariant preservation
(TIMING-only mutation; taxonomy + counting logic invariant); absent
declaration, cycles default to `batch` register-class without §27 binding,
recreating the failure mode at cycle-class register catch class.

Watch for register-class-distinct pattern logs missing under Reading (iii)
scope binding at cycle entry register. The pattern surfaces when a cycle
binds §27 anti-meta-pattern discipline at Reading (iii) scope (Item 7 scope
= §9.0c + §19 + future-pattern register-class-distinct logs per sub-spec
§2.7 Q-S27a Charlie register adjudication outcome) but fails to initialize
all relevant pattern-class register-class-distinct logs at cycle-entry
register per §27 Application checklist item 1 binding. Absent §A2 (§19) log
under Reading (iii) scope leaves §19 instances at carry-forward batch
register without Reading (iii) binding; absent emergent future-pattern
log (when such a future-pattern log has been explicitly authorized at
that future-cycle scoping register per anti-pre-naming discipline; absent
authorization, no log obligation at canonical-artifact register) under
Reading (iii) scope leaves emergent pattern instances unlogged at cycle-
internal register. Reading (iii) scope binding at canonical-
artifact register requires parallel log initialization at cycle-entry
register per §27 Application checklist item 1 binding for all relevant
pattern register-classes; partial log initialization at cycle-entry
recreates the implicit-binding gap at register-class-distinct pattern
register-class.

Watch for verbatim source description-drift between sub-spec parenthetical
labels and canonical PHASE2C_13 scoping decision §6.2 lines 272-278 source
artifact register. The pattern surfaces when §27 codification body cites
Item 7 verbatim source by paraphrase or parenthetical reference at sub-spec
§2.7 register rather than verbatim citation from canonical scoping decision
§6.2 source artifact register. Inherits the description-drift discipline
codified at §22 Failure-mode signal item 7 register-class precedent applied
to Item 7 verbatim source register at §27 codification scope; the drift is
a sub-class of handoff-noise propagation between sub-spec authoring register
and canonical source artifact register, undetected at §27 codification
SEAL pre-fire absent register-precision empirical verification per §1 +
§15 disciplines. §27 Trigger context citation discipline binds verbatim
citation from canonical PHASE2C_13 scoping decision §6.2 source artifact
register, not sub-spec §2.7 parenthetical labels, at codification register
precedent.

Watch for V#-chain anchor verification at cycle SEAL pre-fire elided per
§27 Application checklist item 6 register binding. The pattern surfaces
when cycle SEAL fires without V#-chain anchor verifying Item 7 boundary
clause preservation across cycle-internal log register; boundary clause
violations at cycle-internal log entries propagate through SEAL undetected
absent V#-chain anchor at SEAL pre-fire register. The V#-chain anchor at
cycle SEAL register-event boundary is the binding backup catch register-
class-distinct from log-register boundary compliance column primary catch
per §27 Application checklist item 4 register binding; both registers
binding the boundary clause invariant at parallel-register-class catch
points. Verification methodology at row-level 1:1 mapping register per
§26 Application checklist sub-rule 3b binding (NOT string-count grep proxy
method discarded at PHASE2C_13 sub-spec drafting cycle SEAL boundary
register-event per ChatGPT advisor pushback).

### Tier disposition

§27 ships at **Weak tier observation-only with cross-cycle-pending status
note**. The single PHASE2C_13 cycle instance evidence basis (this sub-spec
is the first concrete Item 7 cycle binding §27 anti-meta-pattern discipline)
gives the discipline single-cycle empirical basis at cycle-class register
without cross-cycle accumulation evidence at PHASE2C_14+ register; the
provisional Weak-tier candidate framing at sub-spec §2.7 codification
mechanism stays at Weak-tier-observation-only-with-cross-cycle-pending at
this Step 6 codification register per §4.3.4 binding (NO Strong-tier
promotions authorized at PHASE2C_13 cycle register; criterion 4 maturation
requirement fails by construction at first codification cycle) + §4.3.3
re-check binding (Item 7 row final disposition = "Weak tier observation-only
with cross-cycle-pending" per criterion 1 single-cycle evidence basis
register fail of ≥10 instances threshold). The Weak-tier disposition
inherits §19 spec-vs-empirical-reality finding pattern Weak-tier register-
class precedent at codification register at **parallel disposition framing
register-class** — §27's single-cycle binding-scope evidence-basis register
(1 PHASE2C_13 cycle instance at cycle-class binding register) is register-
class-distinct from §19's cross-cycle observation-pattern evidence-basis
register (6 instances cumulative across 3 PHASE2C cycles at cross-cycle
finding pattern register per §19 codification register binding); the
parallel framing preserves Weak-tier-observation-only-with-cross-cycle-
pending disposition register without claiming evidence-basis register
match. §19 ships at Weak tier observation-only with cross-cycle-pending
status note at single-§ register precedent; register-class-precedent-
coupling at Weak-tier disposition register binds §27 codification register
at parallel disposition framing register-class.

§27 differs from §21 + §22 + §23 + §25 + §26 Medium-tier register-class
precedent at tier disposition register — those §§ ship at Medium tier
with cross-cycle-pending status note per single-cycle PHASE2C_12 instance
evidence basis (4 instances at §21 / 4 instances at §22 / 1 instance at
§23 / 1 instance at §25 / 8 instances at §26) sufficient for Medium-tier
codification per sub-spec §4.3.4 binding. §27 single-instance evidence
basis at PHASE2C_13 cycle register at single-cycle register fails the
Medium-tier criterion 1 threshold of ≥10 cross-cycle instances per current
sub-spec §4.3.2 + §4.3.3 + §4.3.4 provisional tier check (final Strong-
tier bar codification at METHODOLOGY_NOTES register pending PHASE2C_13
implementation arc Step 9 per sub-spec §5.4 disposition, Carry-forward C
fold-in to §20 appendix-style sub-§ at §20.6 register; the threshold values
at §4.3.2 are sub-spec-authored provisional values pending Charlie register
adjudication at sub-spec SEAL boundary register-event); Weak-tier disposition
register-class-distinct from Medium-tier register-class at tier register-
precision register preserves cross-cycle measurement integrity at canonical-
artifact register per §19 Weak-tier register-class precedent at parallel
disposition framing.

Cross-cycle accumulation register is fed by future methodology consolidation
cycles binding §27 anti-meta-pattern discipline at cycle scope (PHASE2C_14+
cycles if such cycles bind §9.0c-related or §19-related codification under
Reading (iii) scope binding); the cross-cycle accumulation register at
register-precision register reads instance count per cycle at canonical
register-class-distinct counting per §26 Application checklist item 3
sub-rules 3a/3b counting invariant binding. Promotion path: Weak→Medium
at successor methodology consolidation cycle if instance accumulates per
§4.3.2 criterion 1 threshold of ≥10 cross-cycle instances; Medium→Strong
at later methodology consolidation cycle if cross-cycle accumulation
evidence threshold met per §4.3 bar AND Strong-tier promotion bar criteria
codified at the existing §13-§20 tier framework refinement (codified
separately at PHASE2C_13 implementation arc Step 9 per sub-spec §5.4
disposition, Carry-forward C fold-in to §20 appendix-style sub-§).

Anti-momentum-binding cross-cycle scope preservation per §4.3.4 register
binding: PHASE2C_13 cycle Weak-tier-observation-only-with-cross-cycle-
pending disposition is cycle-class-specific register-class boundary, NOT
cross-cycle authorization sealing for future cycles. Future consolidation
cycle authorization decisions at register-class-distinct cycle scoping
cycle register-precision register; PHASE2C_13 §27 codification register
binding does NOT carry forward as blanket future-cycle promotion bind per
anti-momentum-binding strict reading register binding. Anti-pre-naming
preserved at canonical-artifact register: specific future-cycle scope
register-class additions (e.g., new pattern register-class logs surfaced
at future cycle internal) at register-class-distinct future-cycle scoping
decision register, NOT pre-committed at PHASE2C_13 §27 codification
register. Tier preservation at observation-backed application register
without claiming Strong-tier prescriptive force prematurely, parallel to
§19 + §26 cross-cycle-pending disposition framing at Weak-tier and
Medium-tier register-class-distinct registers.

---

---

## §28 Cycle-complexity scaling diagnosis at PHASE2C consolidation cycles (canonical metric set + cross-cycle backfill + forward observation framing)

### Principle

Methodology consolidation cycles accumulate complexity at register-class-distinct
measurement registers across cycle iterations. PHASE2C_8.1 through PHASE2C_12
cycle empirical evidence demonstrates that single-axis complexity descriptors
("commits per cycle" or "auth events per cycle" alone) collapse register-class
precision at cross-cycle scaling diagnosis register: cycles vary along
multiple register-class-distinct axes (Charlie register authorization
boundary count + git commit count + §19 spec-vs-empirical-reality finding
pattern instance count + §9.0c process-design observation instance count) and
single-axis summary at cross-cycle comparison register obscures register-
class-distinct scaling patterns. §28 codifies a canonical metric set at
register-class-distinct measurement register-class binding cross-cycle scaling
diagnosis discipline; cross-cycle scaling diagnosis at register-class-distinct
metric register-precision register-class is the discipline's catch class.

The discipline operates at cycle-cumulative measurement register-class
distinct from §26 cross-cycle observation density measurement register-class,
distinct from §18 §7 carry-forward density at interpretive arc closeouts
register-class, and distinct from §19 cross-cycle spec-vs-empirical-reality
finding pattern accumulation register-class. §26 catches cross-cycle
accumulation at §9.0c-specific instance density register at register-class
taxonomy preservation scope; §18 catches §7 carry-forward observation density
at interpretive arc closeouts register; §19 catches cross-cycle accumulation
of spec-vs-empirical-reality finding pattern at single-pattern-class register.
§28 catches cross-cycle accumulation at canonical metric set scope register-
class — multi-metric cycle-complexity scaling diagnosis at register-class-
distinct canonical metric set register-precision binding. §28 register-class-
coupled with §26 + §18 + §19 cluster at cross-cycle accumulation observation
register-class but register-class-distinct catch class at content scope
register-precision: §26 = §9.0c-specific accumulation register at instance-
density register-class; §18 = §7 carry-forward density register at interpretive
arc closeout register-class; §19 = spec-vs-empirical-reality drift register
at single-pattern-class register-class; §28 = multi-metric cycle-complexity
scaling register at canonical metric set register-class.

§28 is register-class-orthogonal to the §1 / §15 / §21 / §22 / §23 / §25 / §27
per-instance / per-cycle catch-boundary cluster at content scope axis. The
cluster catches defects at workflow time boundaries (any drafting register /
anchor receipt / sub-spec authoring of inter-step contracts / sub-spec SEAL
pre-fire / Step fire-prep / Step deliverable authoring / cycle-class anti-
meta-pattern); §28's specific catch class is multi-metric cycle-complexity
scaling diagnosis at canonical metric set scope rather than a workflow time
boundary catch-class or per-instance catch register-class. Cross-§ register-
class collision at §28 ↔ §26 / §18 / §19 framing is avoided by content-scope
distinction at register-precision: §28 operates at canonical metric set scope
register binding multi-metric register-class-distinct measurement registers
together at single cross-cycle scaling diagnosis register-class; §26 / §18 /
§19 each operate at single-pattern-class register at their own register-class-
distinct content scope.

The canonical metric set codified at §28 binds cross-cycle scaling diagnosis
at four register-class-distinct measurement registers per scoping decision
§6.4 advisor-lean (a) quantitative metric tracking specification: (1) Charlie
register authorization boundaries per cycle at authorization register-class;
(2) git commit count per cycle at commit register-class; (3) §19 spec-vs-
empirical-reality finding pattern instance count per cycle at §19 register-
class; (4) §9.0c process-design observation instance count per cycle at §9.0c
register-class. The four metrics are register-class-distinct measurement
registers at cross-cycle scaling diagnosis register; collapsing to single-
axis composite at cross-cycle comparison register corrupts register-class
precision by construction at canonical metric set discipline binding.

Forward observation framing at §28 binds the discipline at PHASE2C_14+
cross-cycle scaling diagnosis register-class through cycle SEAL closeout
deliverable cycle-cumulative metric reporting requirement at canonical metric
set scope + cross-cycle delta tracking at register-precision register-class
+ scaling-concern threshold check at register-class-distinct provisional
threshold register + scaling-concern surface line at closeout deliverable
register-class binding. Anti-pre-naming preserved at §28 codification register:
specific future-cycle scope (PHASE2C_14 / PHASE2C_15 / etc.) NOT pre-committed
at canonical-artifact register; §28 specifies WHAT each future cycle's closeout
MUST report on (canonical metric set + delta + threshold check) without naming
specific future cycles per anti-pre-naming discipline binding.

### Trigger context

This discipline's empirical basis is five PHASE2C consolidation cycle instances
per Carry-forward A verbatim source at PHASE2C_13 scoping decision
[`docs/phase2c/PHASE2C_13_SCOPING_DECISION.md`](../phase2c/PHASE2C_13_SCOPING_DECISION.md)
§6.4 lines 290-298 (verbatim source citation per §22 Failure-mode signal item 7
description-drift discipline applied to Carry-forward A verbatim source register;
instance descriptions cited verbatim from canonical scoping decision source
artifact, NOT from sub-spec §4.1 parenthetical labels):

> ### §6.4 Carry-forward A — cycle-complexity scaling diagnosis
>
> **Scope:** PHASE2C_13 sub-spec drafting cycle authors deliverable framing
> for cycle-complexity scaling observation per Step 9 §10.6.
>
> **Deliverable framing direction (advisor lean; binding at scoping):**
>
> - **(a) Quantitative metric tracking** — historical analysis output covering
>   auth boundaries / commits / §19 instances / §9.0c instances per cycle
>   across PHASE2C_8 through PHASE2C_12 register. Specific metric set authored
>   at sub-spec.
> - **(c) Forward observation framing** — "what to monitor in PHASE2C_14+"
>   anchor; specific monitoring mechanism authored at sub-spec.
> - **(b) Qualitative root cause analysis** DEFER until (a) data observed.
>   Pure diagnosis without action recommendation is limited value at scoping
>   register; (a) data observation may inform whether (b) is in-scope at
>   PHASE2C_13 or carry-forward to PHASE2C_14+.

Empirical backfill at canonical-artifact register-precision register-class
across PHASE2C_8.1 through PHASE2C_12 cycles + PHASE2C_13 in-progress through
implementation arc Step 6 SEAL boundary (data sources cited per §4.1.1 metric
definition: cycle closeout deliverable §-cumulative-count register reads +
git log empirical fire for commit count + canonical METHODOLOGY_NOTES §19
codification register where applicable):

| Cycle | Auth boundaries | Commit count | §19 instance count | §9.0c instance count |
| ----- | --------------- | ------------ | ------------------ | -------------------- |
| PHASE2C_8.1 | not enumerated at canonical-artifact register at PHASE2C_8.1 closeout deliverable | 11 (empirical: `git log f223316..69e9af9`; range: PHASE2C_8.0 scoping SEAL → PHASE2C_8.1 closeout SEAL) | n/a (register post-codified at PHASE2C_10 §19 seal `0c6831f`) | n/a (register post-surfaced at PHASE2C_12 §8.2 cycle SEAL register-class register) |
| PHASE2C_9 | not enumerated at canonical-artifact register at PHASE2C_9 closeout deliverable | 18 (empirical: `git log 69e9af9..2c96889`; range: PHASE2C_8.1 SEAL → PHASE2C_9 closeout SEAL) | 3 (canonical: PHASE2C_9 closeout §8.4 mandatory-tracked-fix entry #2 + METHODOLOGY_NOTES §19 codification register at `0c6831f`) | n/a (register post-surfaced at PHASE2C_12) |
| PHASE2C_10 | ~6 (canonical: PHASE2C_12 closeout §2.2 retrospective at "~" qualifier register-precision) | 19 (empirical: `git log 2c96889..ff3e4ca`; range: PHASE2C_9 SEAL → PHASE2C_10 closeout SEAL) | 3 cycle-local at METHODOLOGY_NOTES §19 codification register (2 scoping + 1 plan drafting) / 4 at PHASE2C_12 closeout §8.1 cross-cycle accounting (cross-register description-drift surfaced as §A2 finding pattern instance during this Step 7 backfill empirical fire register) | n/a (register post-surfaced at PHASE2C_12) |
| PHASE2C_11 | ~10 (canonical: PHASE2C_12 closeout §2.2 retrospective at "~" qualifier register-precision) | 22 (empirical: `git log ff3e4ca..5dba0df`; range: PHASE2C_10 SEAL → PHASE2C_11 closeout SEAL) | 6 at PHASE2C_12 closeout §8.1 cross-cycle accounting (3 sub-spec drafting + 3 implementation/closeout) / 10 at CLAUDE.md PHASE2C_11 SEAL prose summary register (4 sub-spec drafting + 3 Step 1 implementation + 3 Step 4 closeout); cross-register description-drift surfaced as §A2 finding pattern instance during this Step 7 backfill empirical fire register | n/a (register post-surfaced at PHASE2C_12) |
| PHASE2C_12 | 16 (canonical: PHASE2C_12 closeout §2.2 explicit enumeration "15 explicit Charlie auth boundaries... Auth #7 = 16th = this deliverable seal") | 25 at PHASE2C_12 closeout §2.2 register / 26 at empirical git log fire `5dba0df..1989c85` register (boundary-inclusive convention off-by-one description-drift surfaced as §A2 finding pattern instance during this Step 7 backfill empirical fire register) | 10 (canonical: PHASE2C_12 closeout §8.1 explicit enumeration with 10-row table register) | 8 (canonical: PHASE2C_12 closeout §8.2 explicit enumeration with 8-row table; 3 sub-spec drafting + 1 authorization + 4 reviewer per §8.2 register-class taxonomy) |
| PHASE2C_13 (in progress through implementation arc Step 6 SEAL boundary) | counting-convention drift surfaced cross-cycle: ~52 Q-S register events at fine-grained register-precision register / ~38 explicit Charlie auth events at coarse-grained register-precision register (PHASE2C_12 used Auth-# coarse register; PHASE2C_13 uses Q-S fine register) — surfaced as §A2 finding pattern instance during this Step 7 backfill empirical fire register | 17 (empirical: `git log 1989c85..4735503`; range: PHASE2C_12 SEAL → Step 6 SEAL bundle) | 15 (canonical: §A2 sealed at sub-spec SEAL `92d8c45`; implementation arc Steps 1-6 cycle-internal log at WORKING DRAFT register only per Q-S46 sub-question 2 OPTION (a) precedent; cumulative count finalized at Step 12 closeout deliverable §6 cumulative count register at register-event boundary) | 6 (canonical: §A1 sealed at sub-spec SEAL `92d8c45`; same WORKING DRAFT register caveat) |

The 5-cycle empirical basis (PHASE2C_8.1 / PHASE2C_9 / PHASE2C_10 / PHASE2C_11
/ PHASE2C_12) at canonical-artifact register reads exposes register-class-
distinct scaling patterns across the four canonical metrics: commit count
exhibits monotone increase (11 → 18 → 19 → 22 → 25-26) at modest growth rate;
auth boundary count exhibits non-monotone variability (— → — → ~6 → ~10 → 16)
with PHASE2C_12 step-change to 16 at breadth-expansion arc complexity register;
§19 instance count exhibits PHASE2C_12 step-change to 10 from 3-6 baseline at
PHASE2C_9-PHASE2C_11 register; §9.0c instance count exhibits register first
surface at PHASE2C_12 = 8. PHASE2C_13 in-progress cycle through Step 6 SEAL
boundary already exhibits §19 = 15 (sub-spec drafting cycle alone at sealed
register) — exceeds PHASE2C_12 cycle-cumulative §19 = 10 at register-precision
register-class — and §9.0c = 6 at sub-spec drafting register; cross-cycle
scaling diagnosis at register-precision register-class is the discipline's
substantive trigger context binding §28 codification.

The §28 codification is a difficult methodology concept at register-precision
register — multi-metric cycle-cumulative measurement discipline + cross-cycle
scaling diagnosis at canonical metric set scope register binding + provisional
threshold values at scaling-concern surface register + cross-register
description-drift discipline applied to empirical backfill register-precision
register. The bilingual concept anchor below operationalizes the discipline
anchor at PHASE2C_13 sub-spec §0.3 register (bilingual explanation for
difficult methodology concepts) at the canonical-artifact register where the
discipline is codified for cross-cycle reading per §27 bilingual anchor
register precedent at register-class match register:

**Bilingual concept anchor:**

- **English:** §28 binds cross-cycle scaling diagnosis at a canonical metric
  set of four register-class-distinct measurement registers (auth boundaries
  + commit count + §19 instances + §9.0c instances per cycle). Each cycle's
  closeout deliverable reports cumulative metrics per the canonical set; each
  cycle's closeout reports cross-cycle delta vs the prior cycle's metrics;
  each cycle checks scaling-concern threshold per provisional values (auth
  > 20 / §9.0c > 12 / §19 > 15); if any threshold is crossed, the closeout
  surfaces a "scaling-concern" line + forward-pointer to the next consolidation
  cycle for codification of mitigation if the cross-cycle pattern persists.
  **Why a canonical metric set rather than single-axis composite:** cycles
  vary along multiple register-class-distinct axes; collapsing to single-axis
  summary obscures register-class-distinct scaling patterns at cross-cycle
  comparison register. The canonical set preserves register-class precision
  by construction at scaling diagnosis discipline. **Why provisional thresholds:**
  the threshold values are calibrated against PHASE2C_12 baseline + 50%
  growth rule of thumb at scaling-concern surface register; they are
  provisional pending Charlie register adjudication at §28 codification register
  + future-cycle empirical recalibration as additional cycles accumulate at
  cross-cycle comparison register-precision register-class.

- **中文:** §28 把 cross-cycle scaling diagnosis (跨 cycle 复杂度增长诊断) bind
  在一个 canonical metric set (规范度量集合) 上, 由四个 register-class-distinct
  measurement registers 组成: auth boundaries (Charlie register 授权边界数) +
  commit count (git commit 数) + §19 instances (spec-vs-empirical-reality 不匹配
  发现模式实例数) + §9.0c instances (process-design 观察实例数) per cycle。
  每个 cycle 的 closeout deliverable 在 canonical metric set scope 上 report
  cumulative metrics; 每个 cycle 的 closeout report 与上一 cycle 的 cross-cycle
  delta; 每个 cycle 按 provisional 阈值 (auth > 20 / §9.0c > 12 / §19 > 15)
  check scaling-concern threshold; 如果任何阈值被穿过, closeout surface 出
  "scaling-concern" 行 + forward-pointer 到下一 consolidation cycle 在
  cross-cycle 模式持续时 codify mitigation。**为什么用 canonical metric set
  而不是 single-axis composite:** cycle 在多个 register-class-distinct axis
  上 vary; collapse 到 single-axis summary 在 cross-cycle 比较 register
  obscure 掉 register-class-distinct 的 scaling pattern。canonical set 通过
  构造保留 register-class precision (类别精度)。**为什么阈值是 provisional:**
  阈值是用 PHASE2C_12 baseline + 50% 增长 rule of thumb 校准在 scaling-concern
  surface register; 它们 pending Charlie register 在 §28 codification register
  上的 adjudication, 同时 pending 未来 cycle 经验重新校准 (随着更多 cycle
  在 cross-cycle 比较 register-precision register-class 上 accumulate)。

The PHASE2C_13 row at the backfill table register is interim diagnostic
context only at register-precision register-class binding, NOT a finalized
cycle-closeout row at register-class match register. PHASE2C_13 cycle is
in-progress through implementation arc Step 6 SEAL boundary at register-
event boundary register; cycle-cumulative metrics through Step 12 closeout
register-event boundary will substantively exceed Step 6 SEAL register
snapshot at register-class match register-precision register binding
(PHASE2C_13 §A2 = 15 at sub-spec drafting cycle terminus snapshot register
already exceeds PHASE2C_12 cycle-cumulative §19 = 10 at register-precision
register-class binding; cycle-cumulative count at PHASE2C_13 closeout register
will further accumulate through Steps 7-12 implementation arc cycle-internal
log register binding at working-draft register-class binding per Q-S46 sub-
question 2 OPTION (a) precedent).

PHASE2C_13 cycle is the first concrete instance binding §28 cross-cycle
scaling diagnosis discipline. The cycle's empirical backfill empirical fire
at this implementation arc Step 7 boundary surfaced 4 cross-register
description-drift instances at canonical-artifact register-precision register
during the backfill empirical fire register (observed at working-draft
register at backfill empirical fire register-event boundary per Q-S46 sub-
question 2 OPTION (a) precedent; working-draft register is rm'd at § seal
commit per single-atomic-commit per §0.4 binding; intended for Step 12
closeout §6 cumulative count register at register-event boundary at finalized
durable register-class binding):
PHASE2C_10 §19 cumulative cross-register +1 drift between METHODOLOGY_NOTES
§19 register and PHASE2C_12 closeout §8.1 register; PHASE2C_11 §19 cumulative
cross-register 6-vs-10 drift between PHASE2C_12 closeout §8.1 register and
CLAUDE.md SEAL prose summary register; PHASE2C_12 commit count off-by-one
drift between closeout §2.2 register-prose ("25 commits") and empirical git
log fire (26 commits at boundary-inclusive convention); PHASE2C_13 auth
boundary counting-convention drift between PHASE2C_12 Auth-# coarse register
and PHASE2C_13 Q-S fine register at cross-cycle counting-convention register-
class. These cross-register description-drift instances are themselves §19
spec-vs-empirical-reality finding pattern instances at register-class match
register; their surfacing during this Step 7 backfill empirical fire is
substantive evidence that single-axis canonical metric registers without
cross-register reconciliation discipline accumulate register-class-distinct
description-drift across cycles at canonical-artifact register-precision
register-class — exactly the discipline failure mode §28 codification binds
the canonical metric set against by construction at cycle SEAL closeout
deliverable register-class binding.

### Application checklist

At each PHASE2C consolidation cycle SEAL closeout deliverable register:

1. **Report cycle-cumulative metrics per canonical metric set at closeout
   deliverable §-cumulative-count register.** The canonical metric set is
   four register-class-distinct measurement registers per scoping decision
   §6.4 (a) operationalization: (1) Charlie register authorization boundaries
   per cycle at authorization register-class (count of explicit Charlie
   register auth events fired during cycle scope inclusive of scoping + sub-
   spec drafting + implementation arc + SEAL bundle); (2) git commit count
   per cycle at commit register-class (count of git commits within cycle
   scope range = prior-cycle-SEAL → this-cycle-SEAL inclusive at upper
   boundary, exclusive at lower boundary; data source: `git log <prior-SEAL>..
   <this-SEAL>`); (3) §19 spec-vs-empirical-reality finding pattern instance
   count per cycle at §19 register-class (cumulative count at cycle-internal
   log + §19 codification register reads); (4) §9.0c process-design observation
   instance count per cycle at §9.0c register-class (cumulative count at
   cycle-internal log + §A1 / §26 codification register reads). Closeout
   deliverable §-cumulative-count register includes all four metrics at
   register-class-distinct measurement register; single-axis summary at
   collapsed canonical metric set register is forbidden by construction at
   §28 codification register binding.

   The commit count metric data source convention at §28 register-class-
   precision register binding: `git log <prior-cycle-SEAL>..<this-cycle-SEAL>`
   empirical fire register IS the canonical convention at §28 cross-cycle
   scaling diagnosis register binding; closeout-declared count at register-
   prose summary register may differ at off-by-one register-precision
   register-class binding (e.g., PHASE2C_12 closeout §2.2 cited 25 vs
   empirical fire 26 at boundary-inclusive convention register-precision
   register-class). Canonical convention for §28 cross-cycle scaling
   diagnosis register binding = git-range empirical fire register at
   canonical-artifact register-class binding; closeout-declared count
   surfaced at register-prose summary register at register-class-distinct
   register from canonical empirical fire register; cross-register
   discrepancy surfaced as §A2 §19 finding pattern instance at register-
   class match register per §22 description-drift discipline binding.

   1d. **Sub-rule: scoping cycle iteration count metric (sub-spec §4.1.4
       §6.9 methodology candidate fold-in).** Per sub-spec §4.1.4 binding
       (operationalization-detail coupling at canonical metric set sub-rule
       register-class, parallel to §26 §3 sub-rule fold-in register precedent):
       scoping cycle iteration count per cycle is a register-class-distinct
       sub-metric at canonical metric set register-precision register. The
       sub-metric tracks scoping cycle iteration count per cycle (PHASE2C_10
       / PHASE2C_11 / PHASE2C_12 baseline = 1-cycle scoping; PHASE2C_13 =
       2-cycle scoping per scoping decision §4.5 verbatim) + iteration cause
       summary line (substantive divergence on which sub-questions, at which
       reviewer register). Cycle scoping decision SEAL register includes
       scoping cycle iteration count + iteration cause summary line per sub-
       rule 1d operationalization. Sub-rule 1d disposition at PHASE2C_13
       codification register inherits §28 Medium-tier disposition at sub-rule
       fold-in register (sub-rule evidence basis supports parent §28 tier
       disposition without separate sub-rule tier evaluation per §26 §3 fold-in
       register precedent at register-class match register; the Weak-tier
       observation-only with cross-cycle-accumulation-pending framing at sub-
       spec §4.1.4 register applies at sub-spec scope register, distinct from
       sub-rule fold-in register at this codification register).

2. **Compute cross-cycle delta per canonical metric set at closeout
   deliverable register.** Each cycle SEAL closeout deliverable reports cycle
   metrics + delta vs prior cycle's metrics per canonical metric set: PHASE2C_<N>
   metric vs PHASE2C_<N-1> metric at each of the four register-class-distinct
   measurement registers + sub-rule 1d scoping cycle iteration count register.
   Cross-cycle delta tracking at register-precision register-class operates
   at register-class-distinct level per metric (NOT collapsed to composite
   delta); register-class-distinct delta-per-metric reporting preserves
   register-class precision by construction at cross-cycle comparison
   register-class binding. Delta sign + magnitude reported at register-
   precision register-class without interpretation at this register; threshold
   check + scaling-concern surface operates at item 3 register at register-
   class-distinct binding from delta computation register.

3. **Check scaling-concern threshold per provisional threshold values at
   register-class-distinct measurement register.** Provisional threshold
   values per scoping decision §6.4 (c) operationalization + sub-spec §4.1.2
   binding at register-class-distinct measurement register: auth boundaries
   per cycle > 20 (~+25% above PHASE2C_12 baseline 16 at conservative
   calibration register; below uniform +50% calibration which would yield
   24 at register-class-distinct sensitivity register binding); §9.0c
   instance count per cycle > 12 (+50% above PHASE2C_12 baseline 8 at
   uniform calibration register); §19 instance count per cycle > 15 (+50%
   above PHASE2C_12 baseline 10 at uniform calibration register). Threshold
   calibration is asymmetric across the four register-class-distinct
   measurement registers per sub-spec §4.1.2 PROVISIONAL values register
   binding: §9.0c + §19 metrics calibrated at uniform +50% growth rule of
   thumb register-precision register; auth metric calibrated at conservative
   register-precision register (lower threshold than uniform +50% would
   yield) to surface complexity-scaling concerns earlier at auth-metric-
   specific sensitivity register-class binding. Threshold values are
   PROVISIONAL at §28 codification register-precision register-class —
   final threshold values pending Charlie register adjudication at PHASE2C_13
   implementation arc Step 7 § seal pre-fire register-event boundary per
   Step 7 entry handoff threshold values forward-binding-strength binding
   register-precision register-class at this codification register +
   future-cycle empirical recalibration as additional cycles accumulate at
   cross-cycle comparison register-precision register-class. Threshold
   check operates at register-class-distinct level per metric (NOT aggregated
   to single-axis composite threshold); register-class-distinct threshold-
   per-metric checking preserves register-class precision by construction at
   scaling-concern surface register-class binding.

   Threshold values at item 3 register are **diagnostic surface thresholds**
   at scaling-concern observation register-class binding, NOT pass/fail gates
   at cycle SEAL register-event boundary AND NOT mitigation mandates at
   cycle-class register binding. Threshold-crossing event triggers cycle
   SEAL closeout deliverable scaling-concern surface line at item 4 register-
   class binding; threshold-crossing event does NOT block cycle SEAL register-
   event boundary at SEAL pre-fire register-class binding; threshold-crossing
   event does NOT mandate mitigation at cycle-class register binding
   (mitigation strategy selection at successor methodology consolidation
   cycle scoping cycle adjudication register-event boundary per item 5
   register-class binding). The discipline operates at observation register
   binding cross-cycle scaling diagnosis register-precision register-class,
   NOT at gating register binding cycle SEAL register-event boundary register-
   class.

4. **Surface scaling-concern line at closeout deliverable §-cumulative-count
   register if any threshold crossed.** If item 3 threshold check surfaces
   any threshold crossing at any of the four register-class-distinct measurement
   registers (or sub-rule 1d scoping cycle iteration count register), closeout
   deliverable §-cumulative-count register includes a "scaling-concern surface"
   line at register-precision register-class identifying which register-class-
   distinct metric crossed which threshold + magnitude of crossing + cycle-
   cumulative count vs threshold register. The scaling-concern surface line
   is register-class-distinct from the metric reporting line at item 1
   register; surface line operates at threshold-crossing notification
   register-class binding. Closeout deliverable additionally fires a
   forward-pointer to the next consolidation cycle for codification of
   mitigation if the cross-cycle pattern persists at multi-cycle accumulation
   register-class binding.

5. **Recognize cross-cycle pattern at multi-cycle accumulation register if
   3+ consecutive cycles cross same threshold.** Single-cycle threshold
   crossing at register-class-distinct measurement register is single-cycle
   anomaly register-class; 3+ consecutive cycles crossing the same register-
   class-distinct threshold register at cross-cycle accumulation register-
   class is cross-cycle pattern register at register-class-distinct catch
   class binding. Cross-cycle pattern register binding triggers forward-
   pointer to next consolidation cycle for codification of mitigation at
   register-class-distinct mitigation register-class (mitigation strategy
   selection at next consolidation cycle scoping cycle adjudication register-
   event boundary per anti-pre-naming discipline binding; specific mitigation
   strategies NOT pre-committed at §28 codification register). Single-cycle
   anomaly register-class vs cross-cycle pattern register-class register-
   class-distinction at register-precision register binds threshold-crossing
   register-class binding from mitigation register-class binding by
   construction.

### Failure-mode signal

Watch for cycle SEAL closeout deliverable absent cycle-cumulative metric
reporting at canonical metric set scope. If a closeout deliverable does NOT
include the four register-class-distinct metrics at §-cumulative-count
register, the discipline is operating at single-axis collapsed register-class
register (or absent register-class register) at cross-cycle scaling diagnosis
register-class binding. Per item 1 application register binding, all four
metrics + sub-rule 1d scoping cycle iteration count register are mandatory
at register-precision register-class at every cycle SEAL closeout deliverable
register; absence at any metric register-class signals discipline failure
at canonical metric set binding register-precision register.

Watch for cross-cycle delta tracking elided at closeout register. If a
closeout deliverable reports cycle-cumulative metrics per canonical metric
set but does NOT report cross-cycle delta vs prior cycle metrics per register-
class-distinct measurement register, the discipline is operating at single-
cycle measurement register-class register only (without cross-cycle scaling
diagnosis register-class register binding). Per item 2 application register
binding, cross-cycle delta tracking at register-class-distinct level per
metric is mandatory at register-precision register-class; collapsed single-
axis composite delta at cross-cycle comparison register corrupts register-
class precision by construction at cross-cycle scaling diagnosis discipline
binding.

Watch for scaling-concern threshold check elided at SEAL pre-fire register.
If a closeout deliverable reports cycle metrics + delta but does NOT include
threshold check at register-class-distinct measurement register per item 3
application register binding, the discipline is operating at descriptive
register-class register only (without scaling-concern surface register-class
register binding). Threshold check at register-class-distinct level per metric
is mandatory at SEAL pre-fire register-event boundary per item 3 binding.
Threshold values may shift at future-cycle empirical recalibration register,
but the threshold check itself is mandatory at every cycle SEAL closeout
deliverable register-precision register-class.

Watch for "scaling-concern surface" line elided at threshold-crossing register.
If item 3 threshold check surfaces a threshold crossing at any register-
class-distinct measurement register (or sub-rule 1d scoping cycle iteration
count register), but the closeout deliverable §-cumulative-count register
does NOT include a "scaling-concern surface" line at register-precision
register-class identifying which register-class-distinct metric crossed which
threshold + magnitude of crossing, the discipline is operating at threshold-
check-without-surface register-class binding (which collapses scaling-concern
notification register by construction). Per item 4 application register
binding, scaling-concern surface line at threshold-crossing register is
mandatory at register-precision register-class; absence at any threshold-
crossing event signals discipline failure at scaling-concern notification
binding register-precision register.

Watch for register-class-collapsed metric reporting at single-bucket scope
without canonical metric set decomposition. If a closeout deliverable reports
cycle complexity at single-axis composite scope ("cycle complexity = N
cumulative events per cycle") without decomposition to canonical metric set's
four register-class-distinct measurement registers, the discipline is operating
at register-class-collapsed scope at cross-cycle scaling diagnosis register-
class binding (which corrupts register-class precision by construction). Per
item 1 application register binding, canonical metric set decomposition is
mandatory at register-precision register-class; single-axis composite reporting
at cross-cycle scaling diagnosis register collapses register-class precision
at canonical metric set discipline binding.

Watch for description-drift between §28 cite of canonical metric set and
PHASE2C_13 sub-spec §4.1.1 source artifact register per §22 Failure-mode
item 7 description-drift register-class precedent. If §28 codification at
canonical-artifact register cites canonical metric set descriptions
(authorization boundary definition / commit count definition / §19 instance
definition / §9.0c instance definition) at non-verbatim paraphrase register
of sub-spec §4.1.1 source artifact descriptions, description-drift
accumulates at register-class match register-precision register cross-cycle.
Per §22 Failure-mode item 7 register-class precedent established at PHASE2C_13
implementation arc Step 2 + reinforced at Steps 3 / 4 / 5 / 6 register
precedent: cite verbatim from canonical source artifact at register-precision
register-class binding to preserve cross-cycle source artifact authority at
register-class match register.

Watch for cross-register description-drift surfaced during empirical backfill
fire WITHOUT observation at cycle-internal §A2 §19 instance log register at
register-precision register-class binding. The Step 7 backfill empirical fire
surfaced 4 cross-register description-drift instances at canonical-artifact
register-precision register (PHASE2C_10 §19 +1 drift / PHASE2C_11 §19 6-vs-10
drift / PHASE2C_12 commit count off-by-one drift / PHASE2C_13 auth counting-
convention drift); each is a §19 spec-vs-empirical-reality finding pattern
instance at register-class match register. Observation at cycle-internal §A2
§19 instance log register at working-draft register per Q-S46 sub-question 2
OPTION (a) precedent is mandatory at register-precision register-class binding
(working-draft register is rm'd at § seal commit per single-atomic-commit
per §0.4 binding; intended for Step 12 closeout §6 cumulative count register
at register-event boundary at finalized durable register-class binding).
Absence of cycle-internal §A2 observation at empirical backfill fire surface
register would collapse cross-cycle comparability anchor by construction at
§A2 cumulative count register register-class binding.

### Tier disposition

§28 ships at **Medium tier with cross-cycle-pending status note** per sub-spec
§4.3.3 re-check binding (Carry-forward A row final disposition = "Medium tier"
per criterion 1 first-cycle codification ✓ + criterion 2 operating rule
articulating ✓ at canonical metric set + threshold specification + Application
checklist 5-item structure + criterion 3 cross-cycle register-class consistency
pending + criterion 4 0 prior consolidation cycle FAILS C4 at first-cycle
codification register-precision register). The criterion 4 maturation
requirement fails by construction at PHASE2C_13 first-cycle codification
register; Medium-tier disposition at cross-cycle-pending status preserves
register-class precision by construction at first-cycle codification + future-
cycle accumulation register-class binding. §28 register-class-precedent-
coupling with §21 / §22 / §23 / §25 / §26 Medium-tier register-class precedent
at first-cycle Medium-tier codification register at tier disposition framing
register-class match; §28 differs from §27 Weak-tier register-class precedent
at tier disposition register at register-class-distinct register binding —
§28 evidence basis is 5-cycle empirical backfill at canonical-artifact
register reads + 1 PHASE2C_13 in-progress cycle row, register-class-distinct
from §27 single-cycle Weak-tier basis at register-class match register.

Promotion path Medium → Strong at successor methodology consolidation cycles
after sufficient cross-cycle accumulation evidence at register-class match
register binding per §4.3 bar criteria codified at PHASE2C_13 implementation
arc Step 9 per sub-spec §5.4 disposition (Carry-forward C fold-in to §20.6).
The Strong-tier promotion bar register-class-distinct from §28 base
codification register at register-class match register; the specific bar
criteria authored at Step 9 §20.6 codification register, NOT pre-committed
at §28 codification register per anti-pre-naming discipline binding. Future
cycles binding §28 cross-cycle scaling diagnosis discipline log additional
cycle rows at canonical metric set register at register-precision register-
class binding; cross-cycle accumulation evidence at 3+ cycles at register-
class match accumulates at promotion-eligible register-class binding for
Strong-tier promotion adjudication at successor methodology consolidation
cycle scoping cycle register-event boundary per §4.3 codification register
binding. Anti-pre-naming preserved at canonical-artifact register: specific
future-cycle scope (cycle name + count from PHASE2C_13 forward) NOT pre-
committed at promotion path register; "successor methodology consolidation
cycles after sufficient accumulation" framing preserves anti-pre-naming
discipline binding at register-class match register.

Forward-references to §29 (Carry-forward B framework architectural refactor
evaluation; codified at PHASE2C_13 implementation arc Step 8 per sub-spec
§5.4 disposition (Carry-forward B row new-§ slot)) and §20.6 (Carry-forward C
Strong-tier promotion bar criteria sub-§ host-slot accommodation framing;
codified at PHASE2C_13 implementation arc Step 9 per sub-spec §5.4 disposition
(Carry-forward C row §20 sub-§ fold-in)) cite sub-spec §5.4 disposition table
as canonical binding source per Step 1 §21 F2 patch + Step 2 §22 + Step 3
§23 + Step 4 §25 + Step 5 §26 + Step 6 §27 register precedent at register-
class match register binding. §29 + §20.6 were unsealed at PHASE2C_13
implementation arc Step 7 entry register-event boundary; forward-reference
language at sub-spec §5.4 disposition canonical anchoring is appropriate
at register-precision register-class binding parallel to Steps 1-6 register
precedent at register-class match register.

---

## §29 Framework architectural refactor evaluation at analysis register (alternative pattern enumeration + evaluation criteria + disposition)

### Principle

Framework code architectural pattern sustainability evaluation operates at
meta-evaluation register-class — evaluation of framework code architectural
pattern sustainability vs alternative architectural patterns under per-cycle
code change accretion register binding. The discipline catches a register-
class-distinct defect class from per-instance / per-cycle catch-boundary
cluster (§1 / §15 / §21 / §22 / §23 / §25 / §27) AND from cross-cycle
accumulation observation cluster (§26 / §18 / §19 / §28); §29 is register-
class-orthogonal to both clusters at content scope axis at register-precision
register-class binding.

The cluster register-class-orthogonality at §29 codification register-
precision register-class operates at content scope axis: the per-instance /
per-cycle catch-boundary cluster catches defects at workflow time boundaries
(any drafting register / anchor receipt / sub-spec authoring of inter-step
contracts / sub-spec SEAL pre-fire / Step fire-prep / Step deliverable
authoring / cycle-class anti-meta-pattern); the cross-cycle accumulation
observation cluster catches cross-cycle accumulation at single-pattern-class
register (§19 = spec-vs-empirical-reality drift register at single-pattern-
class register-class; §26 = §9.0c-specific accumulation register at instance-
density register-class; §18 = §7 carry-forward density register at
interpretive arc closeout register-class) or at canonical metric set scope
(§28 = multi-metric cycle-complexity scaling register at canonical metric
set scope register-class). §29's specific catch class is framework code
architectural pattern sustainability evaluation at meta-evaluation register-
class — register-class-distinct catch class at content scope register-
precision register-class binding from both clusters.

The discipline operates at framework code structural register-class binding
distinct from methodology rule codification register-class binding. §29
codifies the evaluation methodology + alternative pattern enumeration + 4-
criteria evaluation + disposition outcome at analysis register; §29 does NOT
codify a methodology rule for application at workflow boundaries (parallel
to §13-§28 codification register-class). The evaluation methodology operates
at meta-evaluation register binding — evaluating whether framework code
architectural pattern (cycle-specific hardcoded constants + per-cycle helper
functions added per cycle at framework code site) is a sustainable
architectural pattern across consolidation cycles; the methodology output is
a disposition (refactor-needed / sustainable-through-next-cycle / inconclusive)
at register-precision register-class binding cycle SEAL register-event
boundary at register-class match register.

**Anti-implementation guardrail explicit at §29 codification register binding
per sub-spec §4.2.1 binding:** §29 codifies evaluation methodology + outcome
ONLY at analysis register; §29 codification at PHASE2C_13 implementation arc
Step 8 register-event boundary does NOT modify framework code at
[`backtest/evaluate_dsr.py`](../../backtest/evaluate_dsr.py) site. Framework
code refactor implementation (if disposition is "refactor-needed" or
"inconclusive" at register-class match register) defers to PHASE2C_14 sub-
spec drafting cycle or later cycle per anti-pre-naming discipline binding.
The discipline catch class is meta-evaluation register-class; the discipline
output is disposition outcome register-class binding cycle SEAL register-
event boundary register-precision register-class — NOT framework code
mutation at implementation register-class binding by construction at §4.2.1
register binding. **Final disposition outcome (refactor-needed / sustainable-
through-next-cycle / inconclusive) at register-precision register-class
binding adjudicated at § seal pre-fire register-event boundary at Charlie
register adjudication boundary parallel to §28 threshold value option (α)
at Q-S71 register precedent at register-class match register binding;** the
3-option survey at the cycle-evaluation block (folded under Trigger context)
is option weighing at adjudication-pending register-class binding, NOT final
disposition at register-class match register.

§29 register-class-precedent-coupling with §21 / §22 / §23 / §25 / §26 / §28
Medium-tier register-class precedent at first-cycle Medium-tier codification
register at tier disposition framing register-class match. §29 differs from
§27 Weak-tier register-class precedent at tier disposition register at
register-class-distinct register binding (§29 evidence basis is single-cycle
empirical at PHASE2C_12 cycle 4 commits to evaluate_dsr.py + §28 5-cycle
backfill data feed at criteria (i)+(iv) register; §27 evidence basis is
single-cycle Weak-tier basis at register-class match register). §29 + §28 +
§26 + §19 + §18 cluster at content scope axis register-class-distinct
catch classes per content scope register-precision register-class binding —
each register catches defects at register-class-distinct content scope by
construction at register-precision register-class.

### Trigger context

This discipline's empirical basis is the PHASE2C_12 cycle framework code
patching pattern at Carry-forward B verbatim source at PHASE2C_13 scoping
decision
[`docs/phase2c/PHASE2C_13_SCOPING_DECISION.md`](../phase2c/PHASE2C_13_SCOPING_DECISION.md)
§6.5 lines 300-309 (verbatim source citation per §22 Failure-mode signal item 7
description-drift discipline applied to Carry-forward B verbatim source register;
instance descriptions cited verbatim from canonical scoping decision source
artifact, NOT from sub-spec §4.2 parenthetical labels):

> ### §6.5 Carry-forward B — framework architectural refactor evaluation
>
> **Scope:** PHASE2C_13 sub-spec drafting cycle authors framework architectural
> refactor evaluation at **analysis register only** (NOT implementation).
>
> **Register-class clarification (binding at scoping per advisor Observation 3):**
> Carry-forward B is process / spec scope. Implementation defers to PHASE2C_14
> sub-spec drafting cycle or later cycle if PHASE2C_13 evaluation indicates
> need. PHASE2C_13 sub-spec authors evaluation methodology (e.g., what counts
> as "needed refactor" criteria, evidence basis from PHASE2C_12 7 commits to
> evaluate_dsr.py at lines 92/124/129/153, alternative architectural patterns
> considered) but not refactor implementation.
>
> **Evidence basis (from Step 9 §11.3):**
> - 7 commits to `backtest/evaluate_dsr.py` at PHASE2C_12 cycle (`8887651`,
>   `2a5c63a`, `605dfc6`, `995fdb2`, `3e1ee89`, `08e1488` + intermediate
>   commits)
> - Cycle-specific framework patches: `PHASE2C_12_N_RAW = 197` at line 92;
>   `PHASE2C_12_N_ELIGIBLE_OBSERVED = 139` at line 124; `ALLOWED_DUAL_GATE_PAIRS`
>   4-pair frozenset at line 129; `_resolve_n_eff_set()` at line 153
> - Sustainability question: PHASE2C_13 evaluation methodology assesses whether
>   cycle-specific hardcoded constants are sustainable architectural pattern;
>   alternative architectural patterns (config injection, cycle-state-machine,
>   abstract base class for cycle parameters, etc.) considered at evaluation
>   register without false-binary framing; specific evaluation criteria
>   authored at sub-spec drafting cycle

Empirical fire at framework code site at register-precision register-class
binding (data sources cited per §22 Failure-mode signal item 7 description-
drift discipline applied to canonical-artifact register reads):

| Cycle | Range | Commits to evaluate_dsr.py | + lines | − lines | Net |
| ----- | ----- | -------------------------- | ------- | ------- | --- |
| PHASE2C_8.1 | `f223316..69e9af9` | 0 | 0 | 0 | 0 |
| PHASE2C_9 | `69e9af9..2c96889` | 0 | 0 | 0 | 0 |
| PHASE2C_10 | `2c96889..ff3e4ca` | 0 | 0 | 0 | 0 |
| PHASE2C_11 | `ff3e4ca..5dba0df` | 4 (creation cycle: input loader + simplified DSR + Codex first-fire + Hotfix-3) | +1224 | −45 | +1179 |
| PHASE2C_12 | `5dba0df..1989c85` | 4 (patching cycle: cycle-specific constants + cycle-conditional helper) | +193 | −54 | +139 |
| PHASE2C_13 (in-progress through Step 7 SEAL) | `1989c85..788198c` | 0 (analysis register only per §4.2.1 binding) | 0 | 0 | 0 |

Framework code site read at canonical-artifact register-precision register-class
binding (current HEAD `788198c` at PHASE2C_13 implementation arc Step 7 SEAL
boundary; line numbers verified empirically against source artifact register
per §22 description-drift discipline binding):

- `PHASE2C_12_N_RAW = 197` at line 92 (sub-spec §4.2.2 cite at line 92 verified
  empirically)
- `PHASE2C_12_N_ELIGIBLE_OBSERVED = 139` at line 123 (sub-spec §4.2.2 cite at
  line 124 differs from empirical at line 123 — cross-register description-
  drift instance at canonical-artifact register-precision register-class match
  register; §A2 §19 finding pattern instance at register-class match register
  per §22 + §28 description-drift discipline precedent at register-class match
  register binding; **observed at non-final cycle-internal observation register
  only at working-draft register** at backfill empirical fire register-event
  boundary per Q-S46 sub-question 2 OPTION (a) precedent + §28 Step 7 backfill
  empirical fire register precedent at register-class match register; closeout
  §6 cumulative count register at Step 12 register-event boundary at finalized
  durable register-class binding)
- `ALLOWED_DUAL_GATE_PAIRS` at line 129 (sub-spec §4.2.2 cite at line 129
  verified empirically)
- `_resolve_n_eff_set()` at line 155 (sub-spec §4.2.2 cite at line 153 differs
  from empirical at line 155 — cross-register description-drift instance at
  canonical-artifact register-precision register-class match register; §A2
  §19 finding pattern instance at register-class match register binding +
  same Q-S46 OPTION (a) precedent + §28 Step 7 register precedent at register-
  class match register)

Empirical commit count register: PHASE2C_12 cycle commits to evaluate_dsr.py
= 4 at canonical-artifact register-precision register-class (`8887651` +
`2a5c63a` + `995fdb2` + `08e1488`); sub-spec §4.2.2 + scoping decision §6.5
prose framing of "7 commits to `backtest/evaluate_dsr.py`" at PHASE2C_12 cycle
includes 2 TDD-RED test commits (`605dfc6` + `3e1ee89`) at test-file register-
class binding distinct from framework-code register-class binding + 1
implicit "intermediate commits" framing at scoping prose register-class
binding; cross-register description-drift between scoping prose framing
register and framework-code empirical fire register at register-precision
register-class match register; §A2 §19 finding pattern instance at register-
class match register binding + Q-S46 OPTION (a) precedent at working-draft
register. The PHASE2C_12 cycle framework-code patching pattern at
evaluate_dsr.py site is canonically documented at 4 framework-code commits
register; the "7 commits" framing operates at PHASE2C_12 cycle Step 8 fire-
prep total commit count register-class binding (4 framework-code commits +
2 TDD-RED test commits + 1 intermediate commit) at register-class-distinct
content scope register binding from framework-code register-class.

§28 canonical metric set 5-cycle backfill data feeds §29 evaluation criteria
(i) framework code accretion rate per cycle + (iv) cross-cycle implementation
arc § seal cumulative effort per sub-spec §4.2.4 sequencing dependency
register binding. The §28 5-cycle backfill table at METHODOLOGY_NOTES line
5511-5516 surfaces register-class-distinct cross-cycle scaling patterns per
canonical metric set: PHASE2C_8.1 / PHASE2C_9 / PHASE2C_10 = methodology-
consolidation cycles without framework code mutation register; PHASE2C_11 =
implementation cycle creating framework code register at +1179 net lines;
PHASE2C_12 = patching cycle adding cycle-specific constants register at +139
net lines; PHASE2C_13 = analysis-register-only cycle without framework code
mutation register per §4.2.1 binding. Cross-cycle pattern at framework-code
register-class binding is bursty (creation + patching cycle pairs) rather
than steady accretion across all cycles at register-class match register.

§29 codification at PHASE2C_13 implementation arc Step 8 register-event
boundary fires the evaluation methodology + alternative pattern enumeration
+ 4-criteria evaluation + disposition outcome at analysis register only per
sub-spec §4.2.1 binding. Charlie register adjudication required at § seal
pre-fire register-event boundary (Q-S76) per §4.2.1 disposition adjudication
binding parallel to §28 threshold value option (α) at Q-S71 § seal pre-fire
precedent at register-class match register binding; final disposition
selected from 3-option register-class binding (refactor-needed / sustainable-
through-next-cycle / inconclusive) at Charlie register-event boundary.

§29 codification at register-precision register-class binding requires
bilingual concept anchor at Trigger context register per sub-spec §0.3
discipline anchor #10 binding (bilingual explanation for difficult methodology
concepts) at register-class match register parallel to §27 + §28 register
precedent at register-class match register binding. Carry-forward B IS
difficult methodology concept at register-precision register-class binding —
analysis-vs-implementation distinction at meta-evaluation register-class +
4-pattern enumeration without false-binary framing at register-precision
register + 4-criteria evaluation methodology at empirical evidence basis
register + 3-disposition outcome scope at adjudication register-class
binding. The bilingual concept anchor below operationalizes discipline
anchor #10 at canonical-artifact register where the discipline is codified
for cross-cycle reading at register-precision register-class:

**Bilingual concept anchor:**

- **English:** §29 binds framework code architectural pattern sustainability
  evaluation at meta-evaluation register-class. Carry-forward B operates at
  analysis-only register at PHASE2C_13 cycle (NOT framework code modification
  at implementation register); refactor implementation defers to a successor
  consolidation cycle if disposition surfaces "refactor-needed" at register-
  precision register-class binding. The discipline enumerates 4 alternative
  architectural patterns at register-class-distinct content scope register
  (status quo + config injection + cycle-state-machine + hybrid) without
  false-binary framing at register-precision register; applies 4 evaluation
  criteria (i)-(iv) at empirical evidence basis register binding (framework
  code accretion rate per cycle + cross-cycle confusion frequency at framework
  code site + per-cycle change surface area + cross-cycle implementation arc
  § seal cumulative effort); ships disposition outcome at 3-option register-
  class binding (refactor-needed / sustainable-through-next-cycle /
  inconclusive). **Why analysis-only at first cycle:** Carry-forward B is
  meta-evaluation about framework code architectural pattern, NOT a methodology
  rule for application at workflow boundaries; pre-mature refactor
  implementation at single-cycle empirical evidence basis register would risk
  over-correction at register-class match register (if pattern is sustainable
  cross-cycle, refactor implementation incurs unnecessary code churn cost;
  if pattern is unsustainable but refactor target architectural pattern is
  poorly chosen at single-cycle evidence basis, refactor implementation
  surfaces a worse pattern at successor cycle register). Analysis-only
  register at first cycle defers refactor implementation to a successor cycle
  with sufficient cross-cycle evidence basis at register-class match register
  binding. **Why 4-pattern enumeration without false-binary framing:** collapse
  to refactor-vs-status-quo binary at evaluation register obscures
  intermediate architectural patterns at register-precision register-class
  binding (config injection + hybrid frequently-changed-vs-rarely-changed
  patterns surface as substantive intermediate candidates at register-class
  match register); 4-pattern enumeration preserves register-class precision
  by construction at evaluation methodology register binding.

- **中文:** §29 把 framework code (框架代码) 架构 pattern sustainability
  (架构模式可持续性) 评估 bind 在 meta-evaluation register-class (元评估类别)
  上。Carry-forward B 在 PHASE2C_13 cycle 上仅 operate 在 analysis-only
  register (仅分析层) — 不在 implementation register (实施层) 上 modify
  framework code; refactor 实施 defer (推迟) 到下一 consolidation cycle 如果
  disposition surface 出 "refactor-needed" 在 register-precision register-
  class binding 上。Discipline enumerate 4 个 alternative architectural
  patterns 在 register-class-distinct content scope register 上 (status quo
  + config injection + cycle-state-machine + hybrid) 不用 false-binary
  framing (二元化框架) 在 register-precision register 上;apply 4 个 evaluation
  criteria (i)-(iv) 在 empirical evidence basis register 上 (framework code
  accretion rate per cycle + cross-cycle confusion frequency at framework
  code site + per-cycle change surface area + cross-cycle implementation arc
  § seal cumulative effort);ship disposition outcome 在 3-option register-
  class binding 上 (refactor-needed / sustainable-through-next-cycle /
  inconclusive)。**为什么 first cycle 仅 analysis-only:** Carry-forward B 是
  关于 framework code 架构 pattern 的 meta-evaluation, 不是 workflow
  boundary 上 application 的 methodology rule;在 single-cycle empirical
  evidence basis register 上 pre-mature refactor 实施在 register-class match
  register 会冒险 over-correction (过度纠正) — 如果 pattern 在 cross-cycle
  上 sustainable, refactor 实施会 incur 不必要的 code churn cost;如果
  pattern 在 single-cycle evidence basis 上 unsustainable 但 refactor target
  架构 pattern 选择不好, refactor 实施会在 successor cycle register 上
  surface 出更糟糕的 pattern。analysis-only register 在 first cycle defer
  refactor 实施到有足够 cross-cycle evidence basis 的 successor cycle 在
  register-class match register binding 上。**为什么 4-pattern enumeration
  不用 false-binary framing:** collapse 到 refactor-vs-status-quo binary
  在 evaluation register 上在 register-precision register-class binding
  obscure 中间架构 patterns (config injection + hybrid frequently-changed-
  vs-rarely-changed patterns 在 register-class match register 上 surface 为
  substantive 中间 candidates);4-pattern enumeration 通过构造在 evaluation
  methodology register 上保留 register-class precision (类别精度)。

**Cycle-evaluation against criteria (i)-(iv) (PHASE2C_13 first-cycle binding):**

This block codifies the PHASE2C_13 cycle's evaluation against criteria
(i)-(iv) at empirical evidence basis register-precision register-class binding
per Application checklist item 3 register binding (folded under Trigger
context per evidence-basis register-class match register binding; preserves
4+1-subsection register-class precedent at §21-§28 cluster). Disposition
adjudication operates at § seal pre-fire register-event boundary (Q-S76)
per Application checklist item 4 register binding parallel to §28 threshold
value option (α) at Q-S71 register precedent at register-class match register
binding.

**Criterion (i) — Framework code accretion rate per cycle:** PHASE2C_8.1 /
PHASE2C_9 / PHASE2C_10 / PHASE2C_11 / PHASE2C_12 / PHASE2C_13 (in-progress) =
0 / 0 / 0 / +1179 (creation cycle) / +139 (patching cycle) / 0 (analysis
register only per §4.2.1 binding) net lines at framework code site register
per cycle. Pattern at register-class match register binding: bursty creation
+ patching cycle pairs at framework code site register-class, with
methodology-consolidation cycles holding framework code site stable at
register-class match register binding. Single empirical cycle of "cycle-
specific patching" pattern (PHASE2C_12 alone with 4 commits + 4 named
constants + 1 cycle-conditional helper); cross-cycle pattern recognition at
register-precision register-class binding insufficient at single-cycle
evidence basis register.

**Criterion (ii) — Cross-cycle confusion frequency at framework code site:**
PHASE2C_12 cycle-specific constants visible at same code site as PHASE2C_11
constants at register-class match register binding (`EXPECTED_N_RAW` = 198
PHASE2C_11 + `PHASE2C_12_N_RAW` = 197 PHASE2C_12 visible at same module-
scope register; `EXPECTED_N_ELIGIBLE_AT_CANONICAL` = 154 PHASE2C_11 +
`PHASE2C_12_N_ELIGIBLE_OBSERVED` = 139 PHASE2C_12 visible at same module-
scope register; `ALLOWED_DUAL_GATE_PAIRS` 4-pair frozenset with 4 cycle-
pairs at register-class match register). Concrete confusion frequency
empirical surface at register-class match register: §19 Step 8 fire-prep
instances #7-#10 at PHASE2C_12 cycle (4 instances of cycle-specific patching
surface at framework code site register-class; cross-register confusion
between sub-spec lockpoint register and framework code register at register-
precision register-class binding); 4 §19 finding pattern instances at single
cycle binding cross-cycle confusion frequency register at register-class
match register. Cross-cycle confusion frequency register-precision register-
class single-cycle evidence basis at register-class match register binding;
cross-cycle pattern recognition at register-precision register-class binding
insufficient at single-cycle evidence basis register.

**Criterion (iii) — Per-cycle change surface area:** PHASE2C_12 cycle = 5
framework code mutations at framework code site register-class (`PHASE2C_12_N_RAW`
constant + `PHASE2C_12_N_ELIGIBLE_OBSERVED` constant + `ALLOWED_DUAL_GATE_PAIRS`
extension + `_resolve_n_eff_set()` helper + sensitivity table N_eff
parameterization at register-class match register binding); PHASE2C_13 cycle
= 0 framework code mutations at framework code site register-class binding
per §4.2.1 analysis-only binding. Cross-cycle change surface area projection
at register-precision register-class binding insufficient at single-cycle
patching evidence basis register (PHASE2C_13 = 0 surface added does NOT
project successor cycle change surface area at register-class match register
binding).

**Criterion (iv) — Cross-cycle implementation arc § seal cumulative effort:**
§28 canonical metric set 5-cycle backfill data feed at register-class match
register binding (PHASE2C_8.1 / PHASE2C_9 / PHASE2C_10 / PHASE2C_11 /
PHASE2C_12 commit count = 11 / 18 / 19 / 22 / 25-26 + auth boundary count =
not enumerated / not enumerated / ~6 / ~10 / 16 + §19 instance count = n/a /
3 / 3-4 / 6-10 / 10 + §9.0c instance count = n/a / n/a / n/a / n/a / 8 per
§28 register binding). PHASE2C_12 cycle complexity step-change at multiple
register-class-distinct measurement registers (auth = 16 / commits = 25-26 /
§19 = 10 / §9.0c = 8); 4 of 25-26 PHASE2C_12 commits at framework code site
register-class binding (≈ 16% of cycle commits at framework code register-
class binding). PHASE2C_12 framework code register cycle effort
register-class match register binding: 4 commits + 4 named constants + 1
cycle-conditional helper + 5 framework code mutations register at register-
class match register; cycle effort accretion at framework code register-
class single-cycle evidence basis register. Cross-cycle implementation arc
§ seal cumulative effort at register-precision register-class binding
insufficient at single-cycle evidence basis register.

**Cross-criterion synthesis at PHASE2C_13 evaluation register-precision
register-class binding:** all 4 criteria at single-cycle evidence basis
register binding (PHASE2C_12 alone for "cycle-specific patching" pattern;
PHASE2C_13 = 0 framework patches at analysis-only binding). Cross-cycle
pattern recognition at register-precision register-class binding insufficient
at single-cycle evidence basis register; cycle-specific patching pattern is
empirically observed at PHASE2C_12 register-class match register but
cross-cycle sustainability assessment at register-precision register-class
binding requires multi-cycle empirical fire register to surface either
recurrent-pattern register (sustainability concern at register-class match
register) or single-cycle-anomaly register (sustainability OK at register-
class match register).

**Disposition adjudication at Q-S76 § seal pre-fire register-event boundary
per §4.2.1 binding (Charlie register adjudication required):** three options
register-class binding per §4.2.1 disposition adjudication binding:

- **Option (i) — refactor-needed** — evaluation surfaces architectural
  refactor candidate at register-precision register-class binding; this
  option requires cross-cycle pattern recognition at register-class match
  register binding (single-cycle evidence basis insufficient); evidence
  weighing at register-class match register binding: PHASE2C_12 single-cycle
  patching pattern + 4 §19 instances at fire-prep register + framework code
  site cycle-specific constants visible at same module-scope register +
  step-change at PHASE2C_12 cycle complexity multi-axis register insufficient
  at register-precision register-class binding for definitive refactor-needed
  call at register-class match register binding.

- **Option (ii) — sustainable-through-next-cycle** — evaluation does NOT
  surface refactor candidate at this-cycle empirical evidence basis register;
  evidence weighing at register-class match register binding: PHASE2C_12
  patching pattern with 4 commits + 5 framework code mutations integrated at
  register-class match register without surfacing definitive sustainability
  concern at register-precision register-class binding; PHASE2C_13 =
  0 framework patches at register-class match register binding (analysis-
  only); pattern functioning at single-cycle evidence basis register at
  register-class match register; sustainability through next consolidation
  cycle not ruled out at this-cycle empirical evidence basis register but
  not established as definitive disposition at single-cycle evidence basis
  register at register-class match register binding.

- **Option (iii) — inconclusive** — evidence basis at this-cycle register-
  precision register insufficient for definitive refactor-needed / sustainable
  disposition adjudication at register-class match register binding; carry-
  forward observation to successor consolidation cycle for additional
  evidence basis accumulation at register-class match register binding;
  evidence weighing at register-class match register binding: single-cycle
  evidence basis (PHASE2C_12 alone) insufficient for cross-cycle pattern
  recognition at register-precision register-class binding; PHASE2C_13 =
  analysis-only-cycle without framework code mutation register at register-
  class match register binding does not contribute incremental cross-cycle
  evidence at criterion (i) framework code accretion rate register or
  criterion (iii) per-cycle change surface area register; cross-cycle
  pattern register-precision register-class binding requires successor cycle
  framework code activity register at register-class match register binding
  for definitive disposition adjudication at register-class match register.

**Locked disposition outcome at PHASE2C_13 implementation arc Step 8 § seal
pre-fire register-event boundary (Q-S76 Charlie register adjudication; cross-
reviewer convergence at advisor F4 + ChatGPT + Claude Code preliminary lean
all converged at option (iii) per cross-criterion synthesis at register-class
match register binding):** **option (iii) inconclusive** at register-precision
register-class binding per §4.2.1 disposition adjudication binding.

Locked disposition rationale at register-precision register-class binding:
all 4 criteria (i)-(iv) at single-cycle evidence basis register binding
converge on "single-cycle evidence basis insufficient for cross-cycle
pattern recognition at register-precision register-class binding" per
cross-criterion synthesis at register-class match register; PHASE2C_13
analysis-only-cycle does not contribute incremental cross-cycle evidence at
criterion (i) framework code accretion rate register or criterion (iii)
per-cycle change surface area register per §4.2.1 anti-implementation
guardrail binding; option (i) refactor-needed rejected per insufficient
cross-cycle evidence basis at register-class match register binding (pre-
mature refactor implementation risks over-correction at single-cycle evidence
basis per Trigger context bilingual concept anchor framing register-class
match register binding); option (ii) sustainable-through-next-cycle rejected
per "not ruled out at this-cycle empirical evidence basis register but not
established as definitive disposition at single-cycle evidence basis register
at register-class match register binding" framing register at register-class
match register (substantively NOT positively endorsed at single-cycle
evidence basis register binding).

**Forward-pointer at locked disposition register-class binding:** carry-
forward observation to successor consolidation cycle for additional evidence
basis accumulation at register-class match register binding per §4.2.1
inconclusive disposition forward-binding register-class precedent + anti-pre-
naming discipline binding ("successor consolidation cycle" framing register-
class without specific future-cycle name pre-commitment at canonical-artifact
register-precision register-class binding; "PHASE2C_14 sub-spec drafting
cycle or later cycle" framing per scoping decision §6.5 verbatim register
precedent at register-class match register binding). Successor consolidation
cycle binding §29 framework architectural refactor evaluation discipline at
register-precision register-class binding logs additional cycle disposition
outcome at register-class match register binding; cross-cycle accumulation
evidence at successor cycle empirical fire register binds future-cycle §29
codification register at register-class match register binding (specific
successor-cycle disposition NOT pre-committed at canonical-artifact register-
precision register-class binding per anti-pre-naming discipline binding).

Locked disposition register-class binding parallel to §28 threshold value
option (α) at Q-S71 § seal pre-fire register-event boundary register precedent
at register-class match register binding; Charlie register adjudication
register-event boundary at Q-S76 register-class match register binding
fires § seal commit at single-atomic per §0.4 binding (METHODOLOGY_NOTES.md
§29 append + working draft rm; NO tag per §6.2 binding parallel to Steps
1-7 register precedent at register-class match register binding).

### Application checklist

At each PHASE2C consolidation cycle binding §29 framework architectural
refactor evaluation discipline at register-precision register-class:

1. **Read framework code site at register-precision register-class binding.**
   Cycle-specific patches at framework code site register (e.g.,
   [`backtest/evaluate_dsr.py`](../../backtest/evaluate_dsr.py) at PHASE2C_12
   cycle: `PHASE2C_12_N_RAW`, `PHASE2C_12_N_ELIGIBLE_OBSERVED`,
   `ALLOWED_DUAL_GATE_PAIRS`, `_resolve_n_eff_set()`); line accretion empirical
   fire register per cycle (canonical convention: `git log <prior-cycle-SEAL>..
   <this-cycle-SEAL>` empirical fire range per §28 sub-rule 1 commit count
   metric register-class binding); cross-cycle accretion pattern at framework
   code site register-class binding (creation cycles vs patching cycles vs
   methodology-consolidation-only cycles at register-class match register).
   Empirical line numbers verified at canonical-artifact register against
   sub-spec source artifact register per §22 description-drift discipline
   binding; cross-register description-drift instances surfaced at
   working-draft register per Q-S46 OPTION (a) precedent + §28 Step 7
   backfill empirical fire register precedent at register-class match register.

2. **Enumerate alternative architectural patterns at register-class-distinct
   register-class binding.** Per sub-spec §4.2.3 4-pattern enumeration without
   false-binary framing at register-precision register-class binding:
   (1) **status quo** — per-cycle hardcoded constants at framework code site;
   cycle-specific helper functions added per cycle at framework code site
   register; (2) **config injection** — cycle parameters externalized to per-
   cycle YAML / JSON config file register; framework code reads config at
   runtime register-class; (3) **cycle-state-machine** — abstract base class
   for cycle parameters with per-cycle subclass register; framework code
   instantiates per-cycle subclass at runtime register-class; (4) **hybrid** —
   frequently-changed parameters externalized to config + rarely-changed
   structure stays inline at framework code site register-class. Each pattern
   has substantive pros + cons at register-precision register-class binding
   per sub-spec §4.2.3 enumeration register; collapse to refactor-vs-status-
   quo binary at evaluation register would obscure intermediate patterns at
   register-class match register binding.

3. **Apply 4 evaluation criteria (i)-(iv) at empirical evidence basis register-
   precision register-class binding.** The 4 criteria per sub-spec §4.2.3:
   (i) framework code accretion rate at framework code site per cycle (lines
   added per cycle for cycle-specific constants + helper functions; data
   source = git log per-cycle range with `--numstat` flag at canonical-
   artifact register-precision register binding); (ii) cross-cycle confusion
   frequency at framework code site register-class binding (count of cycle-
   specific constants visible at same code site as prior-cycle constants =
   potential reviewer / implementer confusion register at register-class
   match register); (iii) per-cycle change surface area register-class binding
   (count of new framework code mutations at framework code site per cycle —
   constants + helpers + sub-rules); (iv) cross-cycle implementation arc § seal
   cumulative effort register-class binding (per §28 canonical metric set
   data feed register: per-cycle commit count + auth boundary count + §19
   instance count + §9.0c instance count register-class match register;
   cross-cycle delta per metric register-precision register-class binding).
   Each criterion at empirical evidence basis register binding cycle-cumulative
   data at canonical-artifact register-precision register-class; criteria
   evaluation operates at register-class-distinct level per criterion (NOT
   collapsed to single-axis composite assessment register at register-class
   match register binding by construction at register-precision register).

4. **Ship disposition outcome at 3-option register-class binding.** Per sub-
   spec §4.2.1 binding: (i) **refactor-needed** disposition register-class —
   evaluation surfaces architectural refactor candidate at register-precision
   register-class binding; forward-pointer to successor consolidation cycle
   for refactor implementation per anti-pre-naming discipline binding;
   (ii) **sustainable-through-next-cycle** disposition register-class —
   evaluation does NOT surface refactor candidate at this-cycle empirical
   evidence basis register; status quo pattern continues at framework code
   site register-class binding; re-evaluation at successor consolidation
   cycle register per §28 cross-cycle scaling diagnosis discipline binding;
   (iii) **inconclusive** disposition register-class — evidence basis at
   this-cycle register-precision register insufficient for definitive
   refactor-needed / sustainable disposition adjudication at register-class
   match register binding; carry-forward observation to successor consolidation
   cycle for additional evidence basis accumulation at register-class match
   register binding. Charlie register adjudication required at § seal pre-fire
   register-event boundary per §4.2.1 disposition adjudication binding parallel
   to §28 threshold value option (α) at Q-S71 § seal pre-fire precedent at
   register-class match register binding.

5. **Forward-pointer to successor consolidation cycle.** If disposition is
   "refactor-needed" at register-class match register binding, forward-pointer
   to successor consolidation cycle for refactor implementation at register-
   class match register binding (anti-pre-naming discipline binding —
   specific successor cycle name NOT pre-committed at canonical-artifact
   register-precision register-class binding; "PHASE2C_14 sub-spec drafting
   cycle or later cycle" framing per scoping decision §6.5 verbatim register
   precedent at register-class match register). If disposition is
   "inconclusive" at register-class match register binding, forward-pointer
   to successor consolidation cycle for additional evidence basis
   accumulation at register-class match register binding (anti-pre-naming
   discipline preserved at register-precision register-class). If disposition
   is "sustainable-through-next-cycle" at register-class match register
   binding, no forward-pointer at successor cycle register-class binding;
   re-evaluation at successor consolidation cycle per §28 cross-cycle scaling
   diagnosis discipline binding fires next cycle's §29 codification at
   register-class match register at register-class match register binding.

### Failure-mode signal

Watch for evaluation operating at false-binary framing (refactor-vs-status-
quo binary) without 4-pattern enumeration at register-precision register-
class binding per sub-spec §4.2.3 binding. If §29 evaluation collapses to
refactor-vs-status-quo binary at register-precision register-class binding,
intermediate architectural patterns (config injection + hybrid frequently-
changed-vs-rarely-changed patterns) at register-class match register would
be obscured by construction at evaluation methodology register binding;
cross-cycle pattern recognition at register-precision register-class binding
would suffer collapse at register-class match register. Per Application
checklist item 2 register binding, 4-pattern enumeration at register-class-
distinct register-class binding is mandatory at every cycle binding §29
discipline at register-precision register-class.

Watch for evaluation operating at implementation register (modifying
framework code at analysis-cycle register-class) violating anti-implementation
guardrail per §4.2.1 binding. If §29 codification fires framework code
mutation at framework code site register-class binding (e.g., refactor
implementation at analysis-cycle register binding by mistake), the discipline
catch class collapses at register-class match register binding; analysis-
only register at first cycle defers refactor implementation per §4.2.1
binding by construction. Per Application checklist item 1 register binding +
§4.2.1 anti-implementation guardrail register binding, framework code
mutation at analysis-cycle register-class is forbidden at register-precision
register-class binding; framework code mutation at successor consolidation
cycle register-class only at register-class match register binding (if
disposition is "refactor-needed" at register-class match register binding).

Watch for criteria (i)-(iv) elided at empirical evidence basis register-
precision register-class binding. If §29 evaluation reports disposition
without enumerating evaluation against criteria (i)-(iv) at register-class
match register binding, the discipline catch class collapses at register-
class match register binding; criteria-grounded disposition register
collapses to ungrounded-judgment register at register-precision register-
class binding by construction. Per Application checklist item 3 register
binding, criteria (i)-(iv) evaluation at empirical evidence basis register-
precision register-class binding is mandatory at every cycle binding §29
discipline at register-precision register-class binding; absence at any
criterion register signals discipline failure at canonical 4-criteria
register-precision register-class binding.

Watch for disposition outcome elided at 3-option register-class binding. If
§29 codification ships disposition without explicit reference to 3-option
register-class binding (refactor-needed / sustainable-through-next-cycle /
inconclusive), the discipline catch class collapses at register-class match
register binding; disposition adjudication register collapses to ad-hoc-
disposition register at register-precision register-class binding. Per
Application checklist item 4 register binding, disposition outcome at 3-
option register-class binding is mandatory at register-precision register-
class; Charlie register adjudication required at § seal pre-fire register-
event boundary per §4.2.1 disposition adjudication binding parallel to §28
threshold value option (α) at Q-S71 § seal pre-fire precedent at register-
class match register binding.

Watch for description-drift between §29 cite of canonical evidence basis and
PHASE2C_13 sub-spec §4.2.2 source artifact register per §22 Failure-mode
item 7 description-drift register-class precedent. If §29 codification at
canonical-artifact register cites canonical evidence basis (PHASE2C_12
commit count + framework code site line numbers + cycle-specific constant
names) at non-verbatim paraphrase register of sub-spec §4.2.2 source
artifact descriptions or scoping decision §6.5 register, description-drift
accumulates at register-class match register-precision register cross-cycle.
Per §22 Failure-mode item 7 register-class precedent established at
PHASE2C_13 implementation arc Step 2 + reinforced at Steps 3 / 4 / 5 / 6 / 7
register precedent: cite verbatim from canonical source artifact at register-
precision register-class binding to preserve cross-cycle source artifact
authority at register-class match register; cross-register description-drift
between sub-spec §4.2.2 source artifact register and framework code empirical
fire register at register-precision register-class match register surfaces
as §A2 §19 finding pattern instance at register-class match register
binding (working-draft register per Q-S46 sub-question 2 OPTION (a) precedent
+ §28 Step 7 backfill empirical fire register precedent at register-class
match register binding).

Watch for forward-pointer pre-naming violation at successor consolidation
cycle scope register-class binding. If §29 codification at register-precision
register-class binding ships forward-pointer language with specific cycle
name pre-commitment ("PHASE2C_14 will implement refactor" rather than
"PHASE2C_14 sub-spec drafting cycle or later cycle if disposition indicates
need" framing per scoping decision §6.5 verbatim register), anti-pre-naming
discipline binding at canonical-artifact register-precision register-class
binding collapses at register-class match register binding. Per §29
Application checklist item 5 register binding, forward-pointer at successor
consolidation cycle scope register-class binding operates at "successor
consolidation cycle" framing register-class without specific future-cycle
name pre-commitment at canonical-artifact register-precision register-class
binding parallel to §28 anti-pre-naming framing register precedent at
register-class match register binding.

Watch for cross-§ register-class collision at §29 ↔ §28 / §27 / §26 / §18 /
§19 framing at register-precision register-class binding. §29 register-class-
orthogonal content scope from §28 + §27 + §26 + §18 + §19 cluster at meta-
evaluation register-class binding (§28 = multi-metric cycle-complexity
scaling at canonical metric set scope; §27 = anti-meta-pattern at cycle-
class register; §26 = §9.0c-specific accumulation at instance-density
register; §18 = §7 carry-forward density at interpretive arc closeout
register; §19 = spec-vs-empirical-reality drift at single-pattern-class
register; §29 = framework code architectural pattern sustainability evaluation
at meta-evaluation register-class). If §29 codification framing at register-
class collision with §28's canonical metric set scope register or with
cross-cycle accumulation observation cluster register, cross-section
consistency at §29 vs §28 + §27 + §26 + §18 + §19 framing register-precision
register-class binding collapses at register-class match register binding.
Per Principle ¶3 register binding, cross-§ register-class collision avoided
by content-scope distinction at register-precision register-class binding;
cross-section consistency check at §29 vs §28 + §27 + §26 + §18 + §19 framing
mandatory at codification + reviewer pass cycle register-class binding.

### Tier disposition

§29 ships at **Medium tier with cross-cycle-pending status note** per sub-spec
§4.3.3 re-check binding (Carry-forward B row final disposition = "Medium tier"
per criterion 1 first-cycle codification ✓ + criterion 2 operating rule
articulating ✓ at evaluation methodology + 4-pattern enumeration + 4-criteria
+ 3-disposition outcome + Application checklist 5-item structure + criterion
3 cross-cycle register-class consistency pending + criterion 4 0 prior
consolidation cycle FAILS C4 at first-cycle codification register-precision
register). The criterion 4 maturation requirement fails by construction at
PHASE2C_13 first-cycle codification register; Medium-tier disposition at
cross-cycle-pending status preserves register-class precision by construction
at first-cycle codification + future-cycle accumulation register-class
binding.

§29 register-class-precedent-coupling with §21 / §22 / §23 / §25 / §26 / §28
Medium-tier register-class precedent at first-cycle Medium-tier codification
register at tier disposition framing register-class match. §29 differs from
§27 Weak-tier register-class precedent at tier disposition register at
register-class-distinct register binding — §29 evidence basis is single-cycle
empirical at PHASE2C_12 cycle 4 framework-code commits register + §28
5-cycle backfill data feed at criteria (i)+(iv) register-class binding,
register-class-distinct from §27 single-cycle Weak-tier basis at register-
class match register at content scope register-precision register-class.

Promotion path Medium → Strong at successor methodology consolidation cycles
after sufficient cross-cycle accumulation evidence at register-class match
register binding per §4.3 bar criteria codified at PHASE2C_13 implementation
arc Step 9 per sub-spec §5.4 disposition (Carry-forward C fold-in to §20.6).
The Strong-tier promotion bar register-class-distinct from §29 base
codification register at register-class match register; specific bar criteria
authored at Step 9 §20.6 codification register, NOT pre-committed at §29
codification register per anti-pre-naming discipline binding. Future cycles
binding §29 framework architectural refactor evaluation discipline log
additional cycle disposition outcomes at register-precision register-class
binding; cross-cycle accumulation evidence at 3+ cycles at register-class
match register binding accumulates at promotion-eligible register-class
binding for Strong-tier promotion adjudication at successor methodology
consolidation cycle scoping cycle register-event boundary per §4.3
codification register binding. Anti-pre-naming preserved at canonical-
artifact register: specific future-cycle scope (cycle name + count from
PHASE2C_13 forward) NOT pre-committed at promotion path register; "successor
methodology consolidation cycles after sufficient accumulation" framing
preserves anti-pre-naming discipline binding at register-class match register
parallel to §28 promotion path framing register precedent at register-class
match register binding.

Forward-references to §20.6 (Carry-forward C Strong-tier promotion bar
criteria sub-§ host-slot accommodation framing; codified at PHASE2C_13
implementation arc Step 9 per sub-spec §5.4 disposition (Carry-forward C
row §20 sub-§ fold-in)) cite sub-spec §5.4 disposition table as canonical
binding source per Step 1 §21 F2 patch + Step 2 §22 + Step 3 §23 + Step 4
§25 + Step 5 §26 + Step 6 §27 + Step 7 §28 register precedent at register-
class match register binding. §20.6 was unsealed at PHASE2C_13 implementation
arc Step 8 entry register-event boundary; forward-reference language at sub-
spec §5.4 disposition canonical anchoring is appropriate at register-precision
register-class binding parallel to Steps 1-7 register precedent at register-
class match register.

Backward-references at §29 register-precision register-class binding cite
sealed §§ at register-class match register: §16 (anchor-prose-access discipline)
+ §17 (procedural-confirmation defect class with sub-rule 4 recursive
operating rule register binding) + §18 (§7 carry-forward density at
interpretive arc closeout register) + §19 (spec-vs-empirical-reality drift
register) + §20 (Strong-tier register precedent; §20.6 was unsealed at register-
class match register) + §21 (fire-prep precondition checklist) + §22
(framework parameter pre-lock at sub-spec terminus + Item 4 fold-in sub-rule
4a/4b/4c) + §23 (inter-step contract standardization) + §25 (register-class
explicit declaration at Step deliverable) + §26 (§9.0c instance density +
register-class taxonomy preservation + §3 sub-rule fold-in items 2+3+4) +
§27 (Item 7 anti-meta-pattern discipline at methodology consolidation cycles
with boundary clause invariance) + §28 (multi-metric cycle-complexity scaling
diagnosis at canonical metric set scope register + 5-cycle backfill data
feed at §29 criteria (i)+(iv) register-class binding). Sealed §§ available
at register-precision register-class binding at PHASE2C_13 implementation
arc Step 8 entry register-event boundary; backward-reference language at
register-class match register precedent at PHASE2C_13 implementation arc
register-class binding.

---

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

The eleven specific principles plus §1's two-axis strengthening are
mutually reinforcing. §1 (empirical verification, with WHEN/HOW
axes — recompute-before-prose at framing-summary stage and V7
grep-able citation operational specificity) prevents specific
factual defects in artifacts. §2 (meta-claim verification) prevents
the same defect class one layer up, in claims about the verification
itself. §3 (regime-aware calibration) is a specific application of
§1 to calibration decisions. §4 (scale-step discipline) prevents
over-claiming from intermediate evidence. §5 (precondition
verification for structural principles) is a sub-pattern of §2
specific to structural and organizational recommendations. §6
(commit messages not canonical) prevents over-applying acknowledgment
discipline. §7 (asymmetric confidence on multi-sample claims)
prevents smoothing-induced over- or under-claiming. §9 (Path-2
outline-first drafting) prevents evidence-section drift relative to
load-bearing-section framing in multi-direction closeouts. §10
(anti-pre-naming as standing discipline) prevents implicit
commitments to scoping decisions not yet made. §11 (closeout-
assembly checklist as running drafting-cycle pattern) preserves
drafting-cycle forward momentum without re-opening sealed sections
for non-blocking fixes. §12 (internal verification and adversarial
review as complementary defect-class coverage) covers the
structurally distinct defect surface that internal verification
cannot reach by construction.

§12 is structurally distinct from §1-§11. §1-§11 codify specific-
defect-prevention disciplines — each principle prevents a specific
class of defect at a specific operational moment (drafting / framing /
section-seal / assembly). §12 is a **meta-discipline** that combines
two protocols (V1-V7 internal verification + adversarial review)
into complementary coverage of the full defect surface. The
distinction matters operationally: §12 doesn't replace V1-V7 or
substitute for any §1-§11 principle; it composes with them. A
high-load closeout commit applies §1-§11 individually + §12 as the
meta-protocol that ensures aggregate coverage.

In practice:

- **Before writing dispatch text:** apply §3 to any expected-
  behavior bands; apply §1 to any specific facts (counts,
  identities, paths) cited as input.
- **Before drafting closeout sections:** apply §9 — does the load-
  bearing interpretive section have multi-direction findings? If
  yes, draft it first as a standalone cycle.
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
- **During dual-reviewer adjudication:** apply §2 to confident
  meta-claims about process state ("verified," "pinned," "low-
  value"); apply §5 to structural and organizational
  recommendations from any source (including from oneself).
- **When discrepancies surface between development artifacts and
  authoritative artifacts:** apply §6 — is the development artifact
  a published result layer, or supporting history?
- **At closeout-assembly stage:** apply §11's at-assembly verification
  + §10's at-assembly meta-attestation grep + §1's recompute-before-
  prose audit + the closeout-assembly checklist deterministic
  application.
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
§12 mandatory adversarial-review meta-protocol. **Administrative
documents** (scoping decisions, plans, dispatch texts with no
empirical claims and no load-bearing findings) apply only the
directly-applicable subset: §1 + §2 + §6 typically; §9-§12 do not
apply by their respective conditional boundaries. The conditional-
boundary structure of §9-§12 prevents the discipline portfolio from
generating overhead disproportionate to defect-surface coverage.

§9-§12 surface conditional boundaries explicitly because PHASE2C_7.1's
drafting cycles surfaced the boundary distinctions empirically. §1-§7
do not carry explicit conditional boundaries in their existing prose;
this is not a claim that §1-§7 are universal-application principles.
PHASE2C_6.6's drafting cycles did not surface the need to name implicit
conditional boundaries for §1-§7 (e.g., §6's commit-messages-not-
canonical principle has an implicit boundary — applies to projects with
closeout documents as canonical result layer). The cost-portfolio
observation is structural across the full portfolio, not a generation-
distinguishing claim about pre-2026 vs post-2026 principle drafting.

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
refinement rather than new principle. **Empirical case study
(strengthening):** §1's WHEN/HOW operational refinements added
during the PHASE2C_7.1 update absorbed inside §1's existing 4-part
structure rather than becoming standalone sections. **Empirical
case studies (new sections):** §9 / §10 / §11 / §12 added during
the PHASE2C_7.1 update each became new sections per existing
convention because each codified a distinct standing principle
not derivable from §1-§7.

When updating §8's "How to apply" synthesis after adding a new
section or strengthening an existing one, integrate the new
content into the practice list rather than appending it to the
end. The synthesis should reflect the current state of standing
discipline, not the chronological order in which lessons were
codified.

### Cross-reference register: arc identifiers to canonical documents

The arc identifiers cited throughout §1-§12 trace to canonical
project documents at the following locations:

- **PHASE2C_5** (Phase 2C Phase 1 walk-forward closeout): `docs/closeout/PHASE2C_5_PHASE1_RESULTS.md` + corrected-engine erratum at `docs/closeout/PHASE2C_5_PHASE1_RESULTS_ERRATUM.md`
- **PHASE2C_6** (Phase 2C single-regime evaluation gate): `docs/closeout/PHASE2C_6_EVALUATION_GATE_RESULTS.md` (PHASE2C_6.6 final closeout commit; PHASE2C_6.7 Codex review-response commit)
- **PHASE2C_7.0** (Phase 2C scoping decision): `docs/phase2c/PHASE2C_7_SCOPING_DECISION.md`
- **PHASE2C_7.1** (Phase 2C multi-regime evaluation gate): `docs/closeout/PHASE2C_7_1_RESULTS.md` + plan at `docs/phase2c/PHASE2C_7_1_PLAN.md` (PHASE2C_7.1.7 Codex review-response commit; tag `phase2c-7-1-multi-regime-v1`)
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

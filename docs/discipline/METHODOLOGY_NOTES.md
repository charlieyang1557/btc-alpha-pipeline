# Project-Discipline Methodology Notes

**First-codified:** 2026-04-26 (during corrected-engine project arc closeout)
**Scope:** standing project-discipline principles that apply across all work cycles, not bound to a specific phase or task.

---

## §1 Empirical verification for factual claims

### Principle

Any specific quantitative or referential claim — in dispatch text, prose, table cells, code comments, file paths, JSON structure references, anywhere that lands in committed artifacts — must be empirically verified against canonical data before the artifact is committed. Plausible reasoning is not a substitute for empirical query.

### Trigger context

This discipline was first codified during Task 8b ("calibration bands need empirical grounding") and generalized during Tasks 9 and 11. Across the corrected-engine project arc, the following factual-claim defects were caught by empirical verification before they shipped:

- **Task 8a:** Original calibration band `[-2.0, 0.5]` was empirically wrong relative to the strategy authors' own design intent (mean_reversion's docstring set [-1.5, 1.0]). Caught when mean_reversion's +1.077 Sharpe required calibration audit.
- **Task 9 §3:** Initial outlier-identity claim was `0bf34de1` (rank-1 candidate); empirical query showed actual outlier was `ca5b4c3a` (delta -1.146 candidate). Caught mid-draft.
- **Task 9 §5:** Initial RSI section reference was `§2.3`; grep against original closeout showed actual section is `§2.1`.
- **Task 9 §7:** Initial rank-position claim for `95bf56e7` was `#11`; empirical query showed actual rank is `#16` (5 candidates between corrected #10 and #16).
- **Task 9 §8:** Initial canonical-artifacts list included `PHASE2C_CORRECTED_DELTA_REPORT.md` before the file was actually written.
- **Task 11 review-response §I:** Initial JSON-path reference was `summary_stats.p25/p75`; structure inspection showed actual path is `wf_test_period_sharpe_distribution.p25/p75`.
- **Task 11 review-response (in-fix):** Long-precision JSON values were quoted from Codex's report rather than directly verified against the canonical JSON; gap closed post-commit by direct query.
- **Codex Task 11 (3 medium findings):** Erratum §3 Q1/Q3, delta report §C Q1/Q3, delta report §E delta Q1, delta report §I per-candidate-artifacts reference — all unverified factual claims in committed canonical prose.

Eight instances of this defect class across two tasks confirm the pattern is robust.

### Application checklist

Before committing any artifact (code, prose, dispatch text, sign-off, erratum), walk through the following questions:

1. **Quantitative claims:** Does every specific number (count, rank, threshold, percentage, magnitude) trace to an empirical query against the canonical data source? If yes, the query is reproducible (a future reader can run it). If no, run the query before commit.
2. **Referential claims:** Does every specific reference (file path, section number, function name, JSON key, line number, commit SHA, rank position) verify against the actual artifact? If the file/section/key/SHA might not exist or might be at a different location, verify.
3. **Identity claims:** Does every specific entity reference (candidate hash, batch UUID, strategy name, theme name) match the canonical record? If derived from memory or plausible inference, verify against the data.
4. **Existence claims:** Does every artifact referenced in the committed prose actually exist on disk at the cited path? If the artifact is "to be created" or "expected to exist," verify it landed before referencing as canonical.

### Failure-mode signal

Watch for prose phrases that assert specific facts without preceding query evidence in the conversation or commit history. Phrases like "the outlier is `<hash>`," "the rank is `#N`," "the section is `§X.Y`," "the path is `<dotted.path>`" — each is a specific-fact claim that should have a verifying query or grep nearby. If the prose has the claim but the conversation/commit doesn't have the verifying query, the claim is unverified.

In dispatch text, watch for "the answer should be X" or "expect Y" claims that imply specific numerical thresholds without consulting the actual evaluation context. These often turn out to be plausible-reasoning artifacts that don't survive empirical verification.

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

The seven principles are mutually reinforcing. §1 (empirical verification) prevents specific factual defects in artifacts. §2 (meta-claim verification) prevents the same defect class one layer up, in claims about the verification itself. §3 (regime-aware calibration) is a specific application of §1 to calibration decisions. §4 (scale-step discipline) prevents over-claiming from intermediate evidence. §5 (precondition verification for structural principles) is a sub-pattern of §2 specific to structural/organizational recommendations. §6 (commit messages not canonical) prevents over-applying acknowledgment discipline. §7 (asymmetric confidence on multi-sample claims) prevents smoothing-induced over- or under-claiming.

In practice:

- **Before writing dispatch text:** apply §3 to any expected-behavior bands; apply §1 to any specific facts (counts, identities, paths) cited as input.
- **Before committing prose artifacts:** apply §1 to every specific claim in the prose; apply §7 to any finding that spans multiple sub-samples.
- **Before drawing closeout-tier conclusions from intermediate evidence:** apply §4 — does this sample size support the scope of claim being made?
- **During dual-reviewer adjudication:** apply §2 to confident meta-claims about process state ("verified," "pinned," "low-value"); apply §5 to structural and organizational recommendations from any source (including from oneself).
- **When discrepancies surface between development artifacts and authoritative artifacts:** apply §6 — is the development artifact a published result layer, or supporting history?
- **Before merging or pushing canonical artifacts:** run a final pass — "what's the highest-leverage unverified claim in this artifact?" — and verify it.

These principles are not a checklist that completes during a single work cycle; they are standing discipline that applies to every cycle. New work cycles inherit them.

### When new lessons surface

When a future work cycle surfaces a discipline lesson that doesn't fit any existing section, append it as §9, §10, etc. The structure (Principle / Trigger context / Application checklist / Failure-mode signal) is the canonical shape for new lesson entries. Keep the document a flat list of standing principles, not a narrative — future readers should be able to scan section headers and read just the relevant principle without reconstructing context.

When updating §8's "How to apply" synthesis after adding a new section, integrate the new principle into the practice list rather than appending it to the end. The synthesis should reflect the current state of standing discipline, not the chronological order in which lessons were codified.

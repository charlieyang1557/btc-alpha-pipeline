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

## §4 How to apply these principles

These three principles are mutually reinforcing. The first (empirical verification for factual claims) prevents specific factual defects in artifacts. The second (meta-claim verification) prevents the same defect class one layer up, in claims about the verification itself. The third (regime-aware calibration bands) is a specific application of the first principle to the calibration-decision discipline.

In practice:

- **Before writing dispatch text:** apply §3 to any expected-behavior bands; apply §1 to any specific facts (counts, identities, paths) cited as input.
- **Before committing prose artifacts:** apply §1 to every specific claim in the prose.
- **During dual-reviewer adjudication:** apply §2 to confident meta-claims about process state ("verified," "pinned," "low-value").
- **Before merging or pushing canonical artifacts:** run a final pass — "what's the highest-leverage unverified claim in this artifact?" — and verify it.

These principles are not a checklist that completes during a single work cycle; they are standing discipline that applies to every cycle. New work cycles inherit them.

### When new lessons surface

When a future work cycle surfaces a discipline lesson that doesn't fit one of the three above, append it to this document as §5, §6, etc. The structure (Principle / Trigger context / Application checklist / Failure-mode signal) is the canonical shape for new lesson entries. Keep the document a flat list of standing principles, not a narrative — future readers should be able to scan section headers and read just the relevant principle without reconstructing context.

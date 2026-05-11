# Phase 5 Diagnostic Sub-Spec

> **Status:** WORKING DRAFT (session-3; §0–§2.c authoring; §2.d–§8 pending)
> **Cycle:** Phase 5 sub-spec drafting cycle (Path 1 per scoping decision §6 successor cycle eligible-not-named slot)
> **Meta-plan:** [`docs/superpowers/plans/2026-05-09-phase5-diagnostic-subspec.md`](../superpowers/plans/2026-05-09-phase5-diagnostic-subspec.md) (sealed at `0e305bc`)
> **Spec source:** [`PHASE5_SCOPING_DECISION.md`](PHASE5_SCOPING_DECISION.md) (sealed at `697c26b` 2026-05-10T01:29:10Z)

---

## §0 — Scope + structure

This sub-spec operationalizes the Phase 5 diagnostic-attribution procedure pre-registered at [`PHASE5_SCOPING_DECISION.md`](PHASE5_SCOPING_DECISION.md) §2.1–§2.5. Its purpose is to lock — before any diagnostic execution fires — the indicator-extraction procedures, cutoffs, multi-mode coexistence rules, ambiguity-handling rules, successor-cycle-class mapping, framing-question resolution-pressure assessment procedure, terminal-conclusion criteria, and attribution-report structure that Phase 5 will operate under.

Scope is constrained by scoping decision §2.2 operationalization-freeze: thresholds must be frozen before any diagnostic execution can fire. This sub-spec does NOT execute the diagnostic; this sub-spec does NOT resolve framing-question (1)/(2)/(3)/(4); this sub-spec is the procedural lockpoint upstream of the diagnostic fire.

Section-by-section:

- **§1 Locked inputs** — existing sealed artifacts the diagnostic consumes; derived-vs-new-data boundary per scoping §4.1.
- **§2 Per-mode operationalization (§2.a–§2.f)** — indicator extraction + cutoffs per failure mode in scoping §2.1 taxonomy. Load-bearing.
- **§3 Multi-mode rules + diagnostic ambiguity** — §3.1 coexistence (multiple modes positively detected) + §3.2 ambiguity (procedure fails to reliably separate).
- **§4a Successor-cycle-class mapping** — operationalization of scoping §2.3 mapping.
- **§4b Framing-question resolution-pressure assessment procedure** — operationalization of scoping §2.4. Procedure ≠ resolution; resolution happens at Phase 5 SEAL based on diagnostic findings.
- **§5 Terminal-conclusion criteria** — operationalization of scoping §2.5; preserves substantive-availability + operational-availability distinction per scoping §2.5 / Mod-pass-2 F1 disambiguation.
- **§6 Attribution report deliverable structure** — Phase 5 closeout deliverable framework; substantively depends on §5.
- **§7 Verification + reviewer disposition** — V# verification chain to be fired at sub-spec SEAL pre-fire boundary; reviewer pass routing at sub-spec SEAL.
- **§8 Cross-references** — anchored references to sealed corpus.

---

## §1 — Locked inputs

Phase 5 diagnostic procedure consumes only sealed artifacts at Phase 5 cycle entry. Source set is frozen; acquisition of new empirical data is prohibited per scoping §4.1.

**Sealed inputs binding the diagnostic procedure:**

- **Phase 4 null result anchor** — closeout deliverable at [`docs/closeout/PHASE4_RESULTS.md`](../closeout/PHASE4_RESULTS.md) sealed at `e8f62f1`; tag `phase4-forward-test-v1` at seal commit; finding content + per-stratum statistics consumed by §2 / §6 from this sealed source.
- **Candidate-cohort reference** — `data/phase4_scoping/cohort_a_candidate_reference.csv` sealed at `11b39f2`; 39 candidates from PHASE2C_15 `cohort_a` with Phase 4 analysis partition per PHASE4_PLAN §1.3 (calendar_effect n=22, non-calendar n=17).
- **Engine + WF lineage anchor** — engine commit `eb1c87f` (corrected walk-forward implementation); lineage chain anchor at tag `wf-corrected-v1` (commit `3d24fcb`; anchors engine fix `eb1c87f` + lineage guard `5f53ee5`).
- **Phase 4 forward-test artifacts** — `data/phase2c_evaluation_gate/phase4_forward_2026_{07,13,15,17}bps_v1/` cost-sweep + `data/phase2c_evaluation_gate/phase4_smoke_15bps_v0/` smoke; parquet anchor `db4ce1d2a2e5e7b556975837260f7aaa29ee4fd5ddc603690d1bc57912aa7035` invariant across artifacts; forward window `[2026-01-01T00:00:00Z, 2026-04-16T07:00:00Z]`; 2528 forward bars.
- **PHASE2C_15 main-fire artifacts** — sealed per-regime evaluation-gate artifacts at `data/phase2c_evaluation_gate/phase2c_15_main_fire_{bear_2022,audit_2024,eval_2020,eval_2021}_v1[_filtered]/` + walk-forward at `data/phase2c_walkforward/batch_phase2c_15_main_fire_combined_corrected/`.
- **Sealed prior-cycle corpus** — closeout MDs (PHASE2C_10/11/12/13/15) + PHASE2C_14 sub-spec MDs at `docs/phase2c/PHASE2C_14_{PLAN,SCOPING_DECISION}.md` + METHODOLOGY_NOTES.md sealed sections + CLAUDE.md Phase Marker entries through Phase 5 entry SEAL. Treated as read-only within the Phase 5 diagnostic cycle per scoping §4.6.

**Derived-vs-new-data boundary** (per scoping §4.1; §8 will anchor the verbatim source quote):

- **ALLOWED**: derived statistics + diagnostic computations from sealed artifacts (re-aggregations, alternative metric profiles on existing per-candidate trade data, statistical decomposition of existing forward Sharpe distributions, regime-conditioning of existing cohort indicators, etc.).
- **NOT ALLOWED**: additional BTC OHLCV history beyond what is already on disk, additional candidate generation, additional regime data, additional Critic/Proposer API calls, new methodology codification.

**Scope binding:** All downstream sections (§2–§6) shall consume only the inputs declared in this section; classification of "derived" vs "new" per the boundary above is binding throughout.

---

## §2 — Per-mode operationalization

Phase 5 diagnostic procedure comprises six per-mode indicator computations corresponding to the failure-mode taxonomy at scoping §2.1. Each sub-section pre-registers: (i) indicator-extraction procedure, (ii) judgment rule producing the per-mode judgment outcome, (iii) descriptive supplementary statistics for §6 attribution-report nuance, (iv) data source classification per §1 binding, (v) register-class tag.

Judgment rules and any pre-registered thresholds are §2.2-frozen at sub-spec SEAL register-event boundary; subsequent modification requires errata register-event at separate Charlie register-event boundary.

### §2.a Signal decay

Operationalizes scoping §2.1(a): "candidate-level temporal deterioration despite training/test validity." Diagnostic question: did each cohort_a candidate's alpha decay between training/test period and the 2026 forward window, holding cost basis constant at the PHASE2C-research 7bps-per-side effective cost?

**Indicator construction.** For each candidate i ∈ cohort_a (n=39):

- `training_test_sharpe[i]` = arithmetic mean of `holdout_bear_2022_sharpe` and `holdout_validation_2024_sharpe` columns from [`data/phase4_scoping/cohort_a_candidate_reference.csv`](../../data/phase4_scoping/cohort_a_candidate_reference.csv) (sealed at `11b39f2`). These are PHASE2C_15 selection-stage per-regime holdout Sharpes (OOS by regime classification), NOT walk-forward test-period Sharpes (`wf_test_period_sharpe` column; not used as baseline). OOS-only baseline; `eval_2020_v1` and `eval_2021_v1` excluded from the primary baseline to avoid train-overlap inflating the decay reference point (PHASE2C_8.1 train-overlap regime classification per CLAUDE.md; `eval_2020_v1` and `eval_2021_v1` evaluation windows fall entirely within v2 train_windows).
- `forward_sharpe[i]` = `holdout_sharpe` column from [`data/phase2c_evaluation_gate/phase4_forward_2026_07bps_v1/holdout_results.csv`](../../data/phase2c_evaluation_gate/phase4_forward_2026_07bps_v1/holdout_results.csv). Phase 4 07bps descriptive-supplement cost-run was authored at PHASE2C_15-comparability cost basis per Phase 4 closeout §3 — same 7bps-per-side effective cost as PHASE2C_15 training/test, enabling clean temporal-isolation per D1 lock.
- `delta[i] = forward_sharpe[i] − training_test_sharpe[i]`. Non-finite / NaN / missing values in either leg drop that candidate pair from the §2.a Wilcoxon input; any such drop must be enumerated in §6 with hypothesis_hash, regime, and original raw value.

**Judgment rule.** Wilcoxon signed-rank one-sided test on the paired deltas at α = 0.05; H_0: median(delta) = 0, H_1: median(delta) < 0. Zero deltas use SciPy `wilcoxon(..., zero_method="wilcox", alternative="less")`; zero-delta pairs are excluded from the signed-rank statistic. If all deltas are zero after zero-method exclusion (degenerate edge), §2.a outcome is `not detected` and §6 must enumerate the zero-delta condition. Canonical §2.a outcome is binary: **signal decay detected** if p ≤ 0.05; **not detected** otherwise. Computed at cohort-aggregate level (effective n ≤ 39 after non-finite-pair exclusions); per-stratum tests on Stratum A (calendar_effect, n ≤ 22) and Stratum B (non-calendar, n ≤ 17) at α = 0.05 each are supplementary indicators and do not modify the cohort-aggregate canonical outcome.

**Descriptive supplements** (for §6 attribution-report nuance; not judgment inputs): `mean(delta)`, `median(delta)`, `prop(delta < 0)` over valid paired deltas after non-finite-pair exclusions, paired Cohen's d = mean(delta) / sample standard deviation(delta), per-stratum decomposition; and a **mean-of-4 supplementary baseline**: `training_test_sharpe[i]` = mean of all 4 PHASE2C_15 regime holdout Sharpes (bear_2022 + validation_2024 + eval_2020_v1 + eval_2021_v1), including the two train-overlap regimes excluded from the primary baseline; surfaces the train-overlap-inflation differential vs OOS-only primary baseline.

**Data source per §1:** on-disk (both legs read directly from sealed CSV artifacts); paired-delta + Wilcoxon + supplements are §1-ALLOWED derived statistics on existing per-candidate Sharpe data.

**Register-class:** binding | quantitative (α = 0.05) | irreversible-interpretation-constraint per §2.2.

**Phase 4 verdict invariance.** §2.a output operates at 7bps temporal-isolation register; it does NOT modify the Phase 4 closeout verdict at 15bps (no forward persistence detected at PLAN §1.5 success criterion). §6 attribution-report wording is forward-bound to make this invariance explicit (forward-binding obligation tracked at sub-spec drafting cycle register).

### §2.b Cost drag

Operationalizes scoping §2.1(b): "realistic-cost-model differential. Alpha exists at gross level (low/zero bps); killed by realistic 15bps round-trip costs." Diagnostic question: does the cost-induced deterioration mechanism operate at per-candidate level across the Phase 4 cost-sweep range?

**Indicator construction.** For each candidate i ∈ cohort_a (n=39):

- Read `holdout_sharpe` per cost level k ∈ {7, 13, 15, 17} bps from `data/phase2c_evaluation_gate/phase4_forward_2026_{07,13,15,17}bps_v1/holdout_results.csv` (Phase 4 forward-test cost-sweep; all 4 cost-runs evaluated on the identical 2026 forward-test candidate set and time window per Phase 4 closeout §4 anchor invariance).
- `ρ_i = scipy.stats.spearmanr([7, 13, 15, 17], [Sharpe_i[7bps], Sharpe_i[13bps], Sharpe_i[15bps], Sharpe_i[17bps]]).correlation`. Cost-vector convention: ascending [7, 13, 15, 17] (locked). SciPy `spearmanr` average-rank tie handling is accepted implicitly via library-default semantics; no custom tie correction is applied. Negative ρ indicates monotonic Sharpe deterioration as transaction cost increases.
- Constant per-candidate Sharpe across all 4 cost levels produces undefined Spearman correlation (ρ = nan) due to zero variance in the Sharpe vector: drop that candidate from the §2.b Wilcoxon input; enumerate in §6 with hypothesis_hash and per-cost Sharpe values (parallel to §2.a NaN protocol).

**Judgment rule.** Wilcoxon signed-rank one-sided test on the per-candidate ρ values at α = 0.05; H_0: median(ρ) = 0, H_1: median(ρ) < 0. SciPy semantics: `wilcoxon(..., zero_method="wilcox", alternative="less")`; zero-ρ candidates excluded from the signed-rank statistic. If all ρ values are zero after zero-method exclusion (degenerate edge), §2.b outcome is `not detected` and §6 must enumerate the zero-ρ condition. Canonical §2.b outcome is binary: **cost drag detected** if p ≤ 0.05; **not detected** otherwise. Computed at cohort-aggregate level (effective n ≤ 39 after nan/zero-variance exclusions); per-stratum tests on Stratum A (calendar_effect, n ≤ 22) and Stratum B (non-calendar, n ≤ 17) at α = 0.05 each are supplementary indicators (inherits §2.a stratification pattern) and do not modify the cohort-aggregate canonical outcome.

**Orthogonal-axis decomposition with §2.a.** §2.a measures the temporal-isolation axis at fixed 7bps cost basis; §2.b measures the cost-isolation axis across the 7-vs-17 bps range at fixed forward 2026 window. The algebraic decomposition identity is reserved for §6 attribution-synthesis register.

**Descriptive supplements** (for §6 attribution-report nuance; not judgment inputs): `mean(ρ)`, `median(ρ)`, `prop(ρ < 0)` over valid candidates after nan/zero-variance exclusions, paired Cohen's d on the ρ distribution = mean(ρ) / sample standard deviation(ρ), per-stratum decomposition; multi-pair magnitude supplements: paired delta `forward_sharpe[i, a bps] − forward_sharpe[i, b bps]` for `(a, b) ∈ {(7, 13), (7, 15), (7, 17), (13, 15)}` (cohort-level mean and Wilcoxon per pair) at descriptive register only — feeds §6 magnitude narrative, not §2.b judgment.

**Data source per §1:** on-disk (4 cost-sweep CSVs read directly from sealed Phase 4 cost-sweep artifacts); per-candidate Spearman + cohort Wilcoxon + supplements are §1-ALLOWED derived statistics on existing per-candidate Sharpe data.

**Register-class:** binding | quantitative (α = 0.05) | irreversible-interpretation-constraint per §2.2.

**Phase 4 verdict invariance (inherited from §2.a discipline).** §2.b output operates at the cost-axis-decomposition register; combined with §2.a output, it does NOT modify the Phase 4 closeout verdict at 15bps. §6 attribution-report wording is forward-bound to preserve this invariance.

### §2.c Cohort weakness

Operationalizes scoping §2.1(c): "population-level economic weakness even when statistical gate passes. Statistical AND-gate criterion is satisfied but the underlying candidate population is economically weak in aggregate." Diagnostic question: did the PHASE2C_15 AND-gate produce materially distinct candidate selection from the broader generation pool, or is cohort_a a thin-margin selection from an economically shallow universe? §2.c evaluates selection-time cohort separation only; it does not evaluate subsequent forward persistence, temporal decay, or transaction-cost robustness. Per D3'' lock: §2.c assumes AND-gate evaluation criterion is reliable and tests cohort substrate strength under that assumption; §2.d (future authoring) tests AND-gate's own validity.

**Indicator construction.**

- **Target cohort:** 39 cohort_a candidates per [`data/phase4_scoping/cohort_a_candidate_reference.csv`](../../data/phase4_scoping/cohort_a_candidate_reference.csv) (sealed at `11b39f2`).
- **Broader-universe baseline:** 993 PHASE2C_15 main fire candidates (the broader generated/evaluated universe referenced by CLAUDE.md PHASE2C_15 SEAL); per-candidate per-regime artifacts at `data/phase2c_evaluation_gate/phase2c_15_main_fire_{bear_2022,audit_2024,eval_2020,eval_2021}_v1/<hash>/holdout_summary.json`. cohort_a ⊂ broader-universe (cohort_a is the AND-gate-passing subset); cohort_a candidates remain included in `broader_universe_score` — the comparison anchor is the full generated/evaluated universe (993), not the cohort_a-excluded subset (954).
- **Selection-time score (primary, OOS-only):** `score_i = arithmetic mean of (sharpe_bear_2022_i, sharpe_validation_2024_i)` per candidate, where each regime Sharpe is the `holdout_metrics.sharpe_ratio` field in the candidate's per-regime `holdout_summary.json`. OOS-only baseline (sub-spec internally consistent with §2.a primary baseline); `eval_2020_v1` and `eval_2021_v1` train-overlap regimes excluded from primary score to avoid train-overlap-differential-inflation contamination of percentile-rank test (selection pressure on train-overlap regimes preferentially picks high-inflation candidates → asymmetric inflation between cohort_a and broader-universe → under-detection bias). Computed for all 993 broader-universe candidates AND the 39 cohort_a candidates on the same OOS gate-evidence surface.
- **Selection-time score (supplementary, mean-of-4):** `score_4regime_i = arithmetic mean of all 4 PHASE2C_15 regime holdout Sharpes (bear_2022 + validation_2024 + eval_2020_v1 + eval_2021_v1)`. Gate-metric-faithful aggregation including train-overlap regimes; recomputed identical percentile-rank structure for §2.c supplementary descriptive register; surfaces train-overlap-differential-inflation magnitude vs OOS-only primary.
- **Non-finite handling:** any candidate with non-finite / missing `sharpe_ratio` in any required regime (2 regimes for primary; 4 regimes for supplementary) drops that candidate from the respective §2.c computation; enumerate in §6 (parallel to §2.a / §2.b NaN protocols).

**Selection-bias caveat (binding interpretation constraint).** cohort_a passed the PHASE2C_15 AND-gate; broader-universe candidates outside cohort_a (954 candidates) did not. The AND-gate criterion is a conjunction of per-regime sub-criteria (per regime: min_sharpe = −0.5, max_drawdown = 0.25, min_total_return = −0.15, min_total_trades = 5 per CLAUDE.md PHASE2C v2 split definition; per-candidate per-regime pass/fail recorded via cohort_a CSV `holdout_*_passed` columns). cohort_a's score distribution is structurally conditioned by gate passage; broader-universe distribution is unrestricted. **The §2.c percentile-rank test discriminates whether cohort_a achieves material separation from the broader-universe distribution (top-quartile-strict median + top-decile-strict upper-quartile), not whether cohort_a is statistically distinct from the broader-universe, which is not the diagnostic target under this mode.** §6 attribution-report wording is forward-bound to preserve this interpretive distinction explicitly.

**Judgment rule.** Two-condition AND on cohort_a's OOS-only score distribution against the broader-universe OOS-only score distribution. **Percentile-rank convention:** `percentile_rank(x, broader_universe_score) = share of broader-universe candidates with score ≤ x`; computed via `scipy.stats.percentileofscore(broader_universe_score, x, kind='weak')`. Under `kind='weak'`, candidates exactly equal to the comparison score are counted in the percentile rank numerator. **Quantile convention:** `p75(cohort_a_score)` computed via `numpy.quantile(cohort_a_score, 0.75, method='linear')`.

- Condition (1): `percentile_rank(median(cohort_a_score), broader_universe_score) < 0.75` — cohort_a median fails to exceed the broader-universe third quartile.
- Condition (2): `percentile_rank(p75(cohort_a_score), broader_universe_score) < 0.90` — cohort_a's upper quartile fails to exceed the broader-universe top decile.
- Detection: **cohort weakness detected** iff both Condition (1) AND Condition (2) hold; **not detected** otherwise.

**Substantive prior justification for 75th / 90th cutoffs (pre-registered per §2.2 freeze).** Under meaningful gate-pass selection from a healthy candidate pool, cohort_a median should exceed the broader-universe third quartile — selection should produce strict upper-half dominance against the broader-universe. Under meaningful elite selection at cohort's upper tail, cohort_a's own third quartile (p75) should exceed the broader-universe top decile — cohort's upper tier should reach the broader-universe top tier. Cutoffs are IQR-derived economic-separation priors at "material gate-pass selection" register; not standard statistical priors (e.g., α = 0.05); locked at this §2.c register-event boundary per §2.2 freeze; alternative cutoff values would shift §2.c sensitivity calibration.

**Descriptive supplements** (for §6 attribution-report nuance; not judgment inputs): `mean(cohort_a_score)`, `median(cohort_a_score)`, percentile-rank values at additional positions (cohort p25, cohort p90); mean-of-4 supplementary score distribution + percentile ranks (train-overlap-inclusive view; surfaces inflation differential vs OOS-only primary); cohort_a (39) vs broader-universe (993) `wf_test_period_sharpe` distribution comparison via `walk_forward_results.csv` at `data/phase2c_walkforward/batch_phase2c_15_main_fire_combined_corrected/` (§1 sealed walk-forward output; cohort_a subset filtered by hypothesis_hash list from cohort_a reference CSV) — upstream cross-check not directly conditioned on AND-gate passage, while still upstream-correlated with gate passage; per-regime cohort_a vs broader-universe holdout Sharpe distributions (4 regimes × cohort/broader split).

**Data source per §1:** on-disk (993-candidate broader-universe per-regime artifacts + cohort_a CSV + walk_forward_results.csv); selection-time score + percentile-rank + supplements are §1-ALLOWED derived statistics on existing per-candidate Sharpe data.

**Register-class:** binding | quantitative (OOS-only primary score; 75th + 90th percentile-rank cutoffs; `kind='weak'` percentile convention; linear quantile interpolation) | irreversible-interpretation-constraint per §2.2.

**Phase 4 verdict invariance (inherited from §2.a discipline).** §2.c output operates at the selection-time cohort-substrate register; combined with §2.a/§2.b outputs, it does NOT modify the Phase 4 closeout verdict at 15bps. §6 attribution-report wording is forward-bound to preserve this invariance.

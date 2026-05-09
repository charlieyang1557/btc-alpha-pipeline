# PHASE2C_15 — Step 4 main fire results

**Date sealed:** 2026-05-08 · **Engine commit:** `eb1c87f` (`wf-corrected-v1`) · **Closeout tag:** `phase2c-15-main-fire-v1` (this seal commit)

**Cycle scope:** Pre-registered K=5 × N=200 = 1000 universe nominal (993 actual after stage2d `rejected_complexity` attrition) at 5-theme rotation excluding `multi_factor_combination`. Strict-exceedance test of empirical AND-gate rate vs PHASE2C_14 sub-spec §3.2 Wilson CI 2.07% threshold. Cost: $11.69. Wall: ~4-5h. Synthetic merge produced post-fix at `0a7da75` (handles `rejected_complexity` gaps in source positions; pre-fix code at `ffc138e` would not).

## §1 Headline (pre-registered report order)

| # | Element | Value |
|---|---|---|
| (a) | Point estimate + Wilson 95% CI (unfiltered) | **39 / 993 = 3.93%** [2.89%, 5.33%] |
| (a') | Point estimate + Wilson 95% CI (filtered, ≥20 trades) | 24 / 993 = 2.42% [1.63%, 3.57%] |
| (b) | Role 1 aux Fisher exact vs PHASE2C_12 (8, 197) | **OR = 1.0354, p = 0.8436** |
| (c) | Role 1 strict-exceedance vs 0.0207 (unfiltered) | **MET** (point estimate AND Wilson lower bound > 2.07%) |
| (c') | Role 1 strict-exceedance vs 0.0207 (filtered) | MET at point estimate; Wilson lower bound below threshold (informational) |
| (d) | Role 2 omnibus FFH (Monte Carlo, K×2 = 5×2) | G = 4.00, p = 0.42 (cannot reject batch homogeneity) |
| (d') | Per-batch breakdown | b1=12/197 (6.09%), b2=6/198 (3.03%), b3=9/200 (4.50%), b4=5/198 (2.53% — below threshold individually; included per strict-inclusion §3 #2), b5=7/200 (3.50%) |
| (e) | Per-regime cohort_a sources | bear_2022 + audit_2024 + eval_2020_v1 + eval_2021_v1 ([artifact dirs](../../data/phase2c_evaluation_gate/)) |

## §2 Substantive interpretation

The 8/197 = 4.06% AND-gate rate from [PHASE2C_12](PHASE2C_12_RESULTS.md) **empirically replicates** at 5× larger universe (39/993 = 3.93%). The auxiliary Fisher exact (OR=1.04, p=0.84) is consistent with the PHASE2C_12 baseline rate; failure to reject at this sample size does not by itself establish equivalence. If PHASE2C_12 had been an artifact, regression toward 0–1% would be expected at this N — at true rate 1%, observing 39+ in 993 has p ≈ 0 by exact binomial test, so the observed 3.93% is incompatible with a 1%-or-lower underlying rate. Instead the rate held.

**Scope of the claim, narrowly stated:** the *generation pipeline's hit rate* on the 4-regime AND-gate is stable under scale-up from 197 → 993 candidates and survives process hardening (theme rotation lock, K=5 cross-batch independence, corrected-engine WF lineage) without regression to noise-floor levels. Replication is at the **population-level rate**, not at the strategy-level register: the 39 cohort_a candidates from PHASE2C_15 are a different set of hypotheses than PHASE2C_12's, and this analysis does not establish which (if any) survive durably out-of-sample. Of the 39 unfiltered cohort_a candidates, **37 use distinct factor signatures** (one signature `day_of_week;hour_of_day;return_1h;return_24h;rsi_14` re-discovered ×3; remaining 36 candidates use 36 distinct combinations); cohort spans all 5 themes. Phase 4 has genuine candidate diversity to test, not a small number of underlying patterns rediscovered. Whether any individual candidate is a durable signal vs sample-period luck is a different empirical question, scoped to Phase 4+.

**Filtered tier (≥20 trades) honest read:** point-estimate criterion holds (2.42% > 2.07%), but Wilson lower bound 1.63% falls below 2.07%. The pre-fire statistical-power asymmetry flag did bite at this register; reported here so it is not buried. Unfiltered Wilson lower bound 2.89% clears 2.07% comfortably, so the headline result is robust on both axes at the unfiltered tier.

**Per-batch range** 2.53%–6.09% looks visually wide but has limited power to detect heterogeneity at N=200 per batch (single-batch 95% binomial CI half-width ~2.7% at true rate 4%). FFH p=0.42 correctly cannot reject homogeneity. The spread is sampling variation around a common rate, not evidence of meaningful per-batch differences.

## §3 §3.4 violation-index clearance audit

All 4 anti-rationalization patterns clear at this framing:

1. **Success-criterion expansion** — not invoked. Pre-registered criterion is point-estimate strict-exceedance; criterion met at both unfiltered and filtered tiers. Wilson CI reporting at §1 / §2 is informational disclosure of statistical-power asymmetry, not criterion modification.
2. **Selective batch interpretation** — not invoked (all 5 batches included per Step 2 sub-spec §3.2 strict-inclusion; b4 alone would fail strict-exceedance, but selective exclusion forbidden)
3. **Fire-boundary re-scoping** — not invoked (K=5 × N=200 fired as pre-committed; 993 reflects expected stage2d attrition)
4. **Comparison-axis reframing** — not invoked (compared against pre-registered PHASE2C_12 baseline (8, 197) per PLAN §1.4)

## §4 Carry-forwards (forward-only at next phase scoping)

1. **Population-rate vs strategy-level alpha distinction.** This closeout establishes the former; the latter is Phase 4+ territory. Worth codifying as a discipline anchor so future closeouts don't conflate.
2. **Wilson CI not in `build_phase2c_15_main_fire_partitioning_stats.py` output.** Substantively bit at the filtered tier (lower bound 1.63% < 2.07% is the load-bearing disclosure). Worth adding ~6 lines hand-rolled Wilson to the `role1_strict_exceedance` JSON block before next fire.
3. **FFH "exact" branch dead-spec.** Docstring + test assertion claim `("monte_carlo", "exact")` but only Monte Carlo + degenerate paths implemented. Drop "exact" or implement tractability guard.
4. **Smoke + main variants ~85% identical at substantive level.** Collapse candidate: single K-parameterized script, smoke = K=2 invocation, main = K=5 invocation. Pre-fire authoring revealed the smoke→main duplication is structurally process-driven not engineering-driven.
5. **Pre-flight checklist must include data-file presence on runner machine.** Mini fresh-clone bit hit `data/raw/btcusdt_1h.parquet` + `data/features/btcusdt_1h_features.parquet` (gitignored, ~12MB combined). Mid-fire recovery cost ~10 min.
6. **`metrics.py:229` PF=None logging error.** Pre-existing cosmetic bug; surfaced more often at K=5 universe size due to single-trade-margin windows. Format string `PF=%.2f` chokes on None when no losing trades. Cosmetic only — metric values written to CSV are correct.
7. **Synthetic_batch source-position contiguity bug** (fixed mid-fire at `0a7da75`). Smoke fixture had no `rejected_complexity` gaps; main fire's 7 cumulative gaps surfaced the false assumption. Unit test fixture upgraded to inject gaps; bug class won't recur.
8. **Strong-tier methodology consolidation candidate.** Convergence-after-divergence pattern, suspended-interpretation register-class machinery, empirical-before-prose discipline have all earned their keep across this arc. Candidate for §20.6 Strong-tier promotion at next methodology consolidation cycle (separate cycle from Phase 4 scoping).

## §5 Forward link

PHASE2C_15 is the substantive throughput register transition the PHASE2C_8.1 → PHASE2C_15 arc was working toward. **PHASE2C_15 empirical fire concludes here.**

The natural next step is **Phase 4+ scoping** — individual-candidate-persistence testing (longitudinal re-test / non-overlapping windows / multi-asset extension are register-class-eligible candidates; specific path TBD at scoping cycle entry). The 39 cohort_a candidates from this fire are the natural input universe to whatever Phase 4 examines.

Phase 4 scoping is **not bundled with this closeout** per anti-momentum-binding strict reading. Charlie register authorization required at fresh cycle boundary post-this-SEAL.

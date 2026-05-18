# R1_2_IS_OOS_RANK_CORRELATION_NOTE.md

**Canonical artifact for Phase B Pre-Sequence Roadmap V3 register-event R1.2 (Template B Bucket-1 investigation note; structural analog to PHASE5_1_COST_MODEL_INVESTIGATION_NOTE, PHASE5_2_VENUE_RECONCILIATION_NOTE, and PHASE5_A_CLARIFICATION_NOTE).**

**Status:** V4 SEAL (canonical sealed artifact at register-event boundary; SEAL fire register-event pending). Cycle scope = single coherent Bucket-1 question per Template B: "is the Phase A robust subset IS-OOS-stable per Phase A OBS 9?" NO git tag at SEAL per CLAUDE.md "Bucket-1 investigation note ≠ arc-level closeout" Tag policy + Phase 5.1 + Phase 5.2 + Phase A precedent.

---

## §0 Cycle Metadata

**Cycle type:** Template B Bucket-1 single-deliverable investigation note (cycle shape α). Cadence shape A (1-cadence: pre-bound computation + interpretation per locked rule).

**Cycle boundary:** R1.2 register-event from Phase B Pre-Sequence Roadmap V3 Tier 1. Cycle entry authorized by Charlie via V3 path-3 parallel authorization 2026-05-18 (R1.1 + R1.2 + R3.1a in parallel).

**Trigger:** Phase A V4 SEAL §6 OBSERVATION 9 named "in-sample (Phase 2C training-window) vs OOS rank correlation is not computed in this cycle (eligible-not-named — gating prerequisite for Phase B promotion)." Phase B Pre-Sequence Roadmap V3 R1.2 fires this as Tier 1 unconditional prerequisite for any candidate-subset commitment at R5.1.

**Scope binding (pre-bound under C.5 hybrid; sealed before computation):**
- Statistic: Spearman rank correlation ρ between IS (`wf_test_period_sharpe`) and OOS (`holdout_sharpe`)
- CI method: Fisher z-transform, 95% two-sided, with average-rank handling for ties
- Panel A: N=39 (full Phase 4 cohort_a) — **PRIMARY GATE** under C.4 rule
- Panel B: N=11 (Phase A robust subset: 8 Stratum A robust + 3 Stratum B robust) — **DIRECTIONAL CHECK ONLY** (NOT co-equal gate; n=11 Fisher z PASS threshold ≈ 0.60 → ~32% power at true ρ=0.5)
- Interpretation rule pre-bound BEFORE computation per V3 patch
- NO engine re-runs; NO API spend; analytical-only on sealed CSV artifacts

**§0 scope-bleed trip-wire status:** clean. Analytical work bounded to authorized statistic + pairing scope. No engine runs. No DSL inspection. No new data acquired. Pre-bound rules locked before computation; no post-hoc threshold adjustment.

**Charlie register chain (R1.2 cycle):**

| # | Decision | Register surface |
|---|----------|------------------|
| 1 | Phase B Pre-Sequence Roadmap V3 path 3 (R1.1 + R1.2 + R3.1a parallel) authorize | "fire authorized" → "路径 3" |
| 2 | R1.2 sub-decision A (pairing scope) | "A.3" (both N=39 + N=11) |
| 3 | R1.2 sub-decision B (statistic) | "B.1" (Spearman rank correlation) |
| 4 | R1.2 sub-decision C (threshold + interpretation rule) | "approve c.5 hybrid" → pre-bound below |
| 5 | R1.2 SEAL scope | "confirm your pick" → modified path-3 = seal R1.2 alone as Bucket-1 |

**Pre-bound R1.2 verdict rules (Charlie register #4, sealed before computation):**

```
PRIMARY GATE (N=39 Phase 4 cohort_a):
  PASS      = Fisher z 95% CI lower bound > 0  (equivalent ρ_obs > ~0.32)
  CONCERN   = Fisher z 95% CI upper bound < 0  (equivalent ρ_obs < ~-0.32)
  AMBIGUOUS = otherwise (CI straddles 0)

ANNOTATION LAYER (N=39):
  - Whether ρ_obs clears conventional strong-signal marker ρ > 0.5
  - Whether ρ_obs clears moderate marker ρ > 0.3
  Non-binding context; do not override CI verdict.

DIRECTIONAL CHECK (N=11 Phase A robust subset):
  NOT a co-equal gate. Report observed ρ + Fisher z CI.
  Interpret:
    - ρ > 0.5 with N=39 PASS  → mild consistency corroboration
    - ρ < -0.3 with N=39 AMBIG → strengthens regime-specific concern
    - any ρ with wide CI       → expected at n=11; not informative alone

INTERPRETATION RULE (downstream Phase B framing impact):
  PASS      → forward-window robust subset is robust in-sample too;
              Phase A characterization NOT regime-specific;
              supports promotion-class considerations
  AMBIGUOUS → forward results not informative at this n;
              reframe Phase A as "what worked in this specific window"
              not "stable signal"
  CONCERN   → forward winners were NOT in-sample winners;
              Phase 4 results may be regime-specific OR overfit-flipped;
              binds Phase B promotion harder

EXPLICITLY RETIRED FROM OPTION SET:
  C.3 (ρ > 0 PASS) — ~50% false-PASS rate under null
```

**Anti-pre-naming binding (preserved throughout):** this note reports the pre-bound computation result against pre-bound rules. It does NOT pre-name Phase B venue / candidate-subset / promotion-class outcomes. Each Phase B successor decision is eligible-not-named for separate Charlie register-event boundary.

---

## §1 Scope and Objective

**§1.1 Question this cycle resolves:**

Phase A V4 SEAL §6 OBSERVATION 9: "In-sample (Phase 2C training-window) vs OOS (Phase 4 forward-window) rank correlation is not computed in this cycle (eligible-not-named — gating prerequisite for Phase B promotion)." R1.2 fires the computation against pre-bound rules and reports the verdict.

**§1.2 What this cycle does NOT resolve:**
- Phase B venue commitment (Branch.A/B/C/D per Phase 5.2 §6.4)
- Phase B candidate-subset commitment (R5.1 — informed by but not pre-named by R1.2)
- Phase B promotion-class commitment (R6.1 — gated by R5.1)
- DSL inspection of any candidate (deferred to R2.1 / R2.2 / R2.3 conditional registers)
- Phase A errata for forward-window estimate (R1.1 ships separately as commit-class errata)
- R3.1a venue-infrastructure formalization (parked in transcript; separate Charlie register)

**§1.3 Scope verification anchor:** All factual claims derive from:
- `data/phase2c_walkforward/batch_phase2c_15_main_fire_combined_corrected/walk_forward_results.csv` (993 candidates; PHASE2C_15 main fire source batch; sealed walk-forward artifact)
- `data/phase2c_evaluation_gate/phase4_forward_2026_07bps_v1/holdout_results.csv` (39 candidates; Phase 4 cohort_a at 7bps cost)
- `data/phase2c_evaluation_gate/phase4_forward_2026_{13,15,17}bps_v1/holdout_results.csv` (39 candidates each; used only for robust subset identification per Phase A §3.4 definition)
- `data/phase2c_evaluation_gate/phase4_forward_2026_07bps_v1/holdout_summary.json` (forward window metadata; sha256-locked execution_config + parquet_data)
- `docs/phase5/PHASE5_A_CLARIFICATION_NOTE.md` (Phase A V4 SEAL; read-only)
- `config/environments.yaml` (v2 walk-forward config + train_windows definition)

---

## §2 Headline Finding: AMBIGUOUS verdict on primary gate; reframe Phase A robust subset as window-specific

**N=39 primary gate (full Phase 4 cohort_a):**
- Spearman ρ = **−0.1474**
- Fisher-z-derived ρ 95% CI = **[−0.4423, +0.1764]** (back-transformed)
- **C.4 verdict: AMBIGUOUS** (CI straddles 0)
- C.1 annotations: ρ > 0.5? NO. ρ > 0.3? NO.

**N=11 directional check (Phase A robust subset):**
- Spearman ρ = **+0.1636**
- Fisher-z-derived ρ 95% CI = [−0.4837, +0.6953] (width 1.18; spans most of the [-1, +1] scale)
- Fisher z-statistic ≈ 0.46; one-sided p ≈ 0.32 against H0: ρ ≤ 0
- Direction: positive point estimate, but **informationally vacuous** given CI width — ρ = 0 is well inside the CI; observed value is consistent with both moderate negative and moderate positive true rank correlation
- Interpretation: not informative alone (n=11 wide CI as pre-bind anticipated); does not strengthen overfit-flip concern; does NOT provide load-bearing directional corroboration either

**Per pre-bound interpretation rule, AMBIGUOUS fires:**

> Forward results not informative at this n; **reframe Phase A as "what worked in this specific window" not "stable signal"**

This is the load-bearing finding. Phase A's robust-8 + robust-3 = robust-11 subset, characterized by Sharpe > 0.5 at all 4 tested costs in the 2528-bar forward window, **cannot be claimed as "IS-OOS-stable signal" at the cohort level**. The cohort exhibits essentially zero rank correlation between Phase 2C training-window walk-forward Sharpe and Phase 4 forward holdout Sharpe.

**Cross-check structure (N=39 vs N=11):**
- N=39 panel: point estimate ρ=−0.15 with CI straddling 0
- N=11 robust subset: point estimate ρ=+0.16 with CI straddling 0 by a wider margin
- The robust subset is mildly less anti-consistent than the full cohort in point estimate, but the difference is within sampling noise at these n's
- Combined picture: NO meaningful IS-OOS rank stability at either cohort or robust-subset level

---

## §3 Methodology

**§3.1 Data sources (sealed; read-only at this cycle):**

| Layer | Path | N | Metric used |
|---|---|---:|---|
| In-sample (IS) | `data/phase2c_walkforward/batch_phase2c_15_main_fire_combined_corrected/walk_forward_results.csv` | 993 | `wf_test_period_sharpe` — per-strategy aggregate Sharpe computed by `backtest/engine.py` walk-forward semantics `corrected_test_boundary_v1` over the 4 walk-forward sub-windows derived from the 2020-2021 train range per `config/environments.yaml v2` walk-forward decomposition (`train_window_months: 12`, `test_window_months: 3`, `step_months: 3`). The 2023 train range alone is too short for these defaults so does not contribute sub-windows. Aggregation is computed per the source batch summary, NOT by stitching disjoint train-window equity curves (per CLAUDE.md HARD CONSTRAINT). |
| OOS forward | `data/phase2c_evaluation_gate/phase4_forward_2026_07bps_v1/holdout_results.csv` | 39 | `holdout_sharpe` (2528-bar 2026-01-01 to 2026-04-16 forward window at 7bps cost) |
| Robust subset identification | `phase4_forward_2026_{07,13,15,17}bps_v1/holdout_results.csv` | 39 each | `holdout_sharpe` > 0.5 at all 4 costs per Phase A §3.4 |

**§3.2 Pairing:** all 39 Phase 4 cohort_a hypothesis_hashes have non-null IS Sharpe in the walk-forward source batch. Pairing is exact (1:1 by hypothesis_hash). No imputation.

**§3.3 Statistic:** Spearman rank correlation ρ computed from ranks (average-rank handling for ties; tie-breaking deterministic by stable sort). Implementation: pure Python stdlib, deterministic, reproducible.

**§3.4 CI method:** Fisher z-transform — z(ρ) = 0.5·ln((1+ρ)/(1-ρ)); SE(z) = 1/√(N−3); 95% two-sided CI = z ± 1.96·SE; back-transform via tanh. (Fisher z is exact for Pearson correlation and an approximation for Spearman rank correlation; standard practice for N ≥ 10. Approximation error at N=11 is non-trivial but materially smaller than the sampling uncertainty given the CI width of 1.18 spanning most of the [-1, +1] scale; does not alter the directional-only interpretation.)

For N=39: SE = 1/√36 = 0.1667, CI half-width on z = ±0.327, **PASS threshold ρ > 0.3155**.
For N=11: SE = 1/√8 = 0.354, CI half-width on z = ±0.693, **PASS threshold ρ > 0.5999** (by construction near-impossible at n=11 without ρ ≥ 0.6; pre-bind explicitly designates N=11 as directional-only per reviewer routing Round 4).

**§3.5 Robust subset definition:** per Phase A §3.4 — candidates with `holdout_sharpe > 0.5` at all 4 tested costs (7/13/15/17 bps). Identified deterministically from the 4 sealed forward CSVs.

**§3.6 Analysis script:** `/tmp/r1_2_rank_correlation_analysis.py` (deterministic, pure Python stdlib + csv; reproducible from sealed CSVs).

---

## §4 Findings — Primary Gate Verdict (N=39 Panel)

**§4.1 Panel composition:**

| Theme | N |
|---|---:|
| calendar_effect | 22 |
| momentum | 6 |
| volume_divergence | 7 |
| volatility_regime | 2 |
| mean_reversion | 2 |
| **Total** | **39** |

Matches Phase A §5 stratification exactly (sanity check on cohort identity).

**§4.2 Sharpe distributions:**

| Metric | IS (wf_test_period_sharpe) | OOS (holdout_sharpe) |
|---|---:|---:|
| Min | −1.075 | −6.123 |
| Max | +2.880 | +3.504 |
| Mean | +0.462 | +0.103 |

Notable: OOS range is wider than IS range (especially negative tail); OOS mean is lower; suggests the Phase 4 forward window includes both larger upside and larger downside events than the walk-forward training windows on a per-strategy basis.

**§4.3 Rank correlation:**

- Spearman ρ = **−0.1474**
- Fisher z = −0.1485
- Fisher z 95% CI = [−0.4754, +0.1784] (z-scale)
- ρ 95% CI = **[−0.4423, +0.1764]** (back-transformed)

**§4.4 C.4 PRIMARY GATE VERDICT: AMBIGUOUS**

CI straddles 0. Pre-bound interpretation rule fires: forward results not informative at this n; reframe Phase A as "what worked in this specific window" not "stable signal."

**§4.5 C.1 annotation:**
- ρ > 0.5 strong-signal marker: NO (observed −0.1474; far below threshold)
- ρ > 0.3 moderate marker: NO

No conventional effect-size marker cleared. Annotation does not override CI verdict.

---

## §5 Findings — Directional Check (N=11 Panel)

**§5.1 Panel composition (robust subset; verified against Phase A §4-§5):**

| Theme | N |
|---|---:|
| calendar_effect (8 Stratum A robust) | 8 |
| momentum (Stratum B robust) | 1 |
| volume_divergence (Stratum B robust) | 1 |
| volatility_regime (Stratum B robust) | 1 |
| **Total** | **11** |

Verified against Phase A: 8 calendar_effect = 8 Stratum A robust (7 monday + 1 weekend); 3 cross-theme Stratum B robust matches Phase A §5.3 named candidates.

**§5.2 Rank correlation:**

- Spearman ρ = **+0.1636**
- Fisher-z-derived ρ 95% CI = **[−0.4837, +0.6953]** (width 1.18; spans most of the [-1, +1] scale)
- Fisher z-statistic ≈ 0.46; one-sided p ≈ 0.32 against H0: ρ ≤ 0
- Direction: positive point estimate but **informationally vacuous** given CI width — observed ρ is consistent with both moderate negative correlation (down to −0.48) and moderate positive correlation (up to +0.70); ρ = 0 is well inside the CI

**§5.3 Directional check interpretation (NOT a gate):**

CI is very wide (half-width ~0.59) as pre-bind anticipated for n=11. Observed ρ is within CI of 0 by a wide margin. Pre-bound interpretation rule fires:
- ρ > 0.5? NO. (no strong corroboration)
- ρ < −0.3? NO. (no regime-specific concern strengthening)
- → any ρ with wide CI; not informative alone

Combined with N=39 AMBIGUOUS, the cross-check does not provide additional load-bearing signal. The robust subset is slightly less anti-consistent than the full cohort, but the difference is within sampling noise.

---

## §6 Per-Candidate Detail + Pattern Surfacing

**§6.1 Per-candidate IS-OOS Sharpe (robust subset, sorted by OOS Sharpe):**

| Theme | Name | IS Sharpe | OOS Sharpe | Pattern |
|---|---|---:|---:|---|
| calendar_effect | monday_morning_momentum_200 | 0.076 | **3.504** | OOS-only |
| momentum | ema_crossover_momentum_acceleration | 0.484 | **3.496** | mild consistency |
| calendar_effect | monday_morning_reversal_long | **1.762** | **2.888** | **IS-OOS consistent** ✓ |
| calendar_effect | monday_morning_dip_buy | **−0.165** | **2.204** | **IS-OOS flip** ⚠ |
| volume_divergence | volume_surge_breakout_divergence | 0.799 | 2.044 | **IS-OOS consistent** ✓ |
| calendar_effect | monday_mean_reversion (hash #1) | 0.072 | 1.947 | OOS-only |
| calendar_effect | monday_pre_europe_momentum_fade | 0.308 | 1.618 | mild consistency |
| calendar_effect | monday_dip_reversal | 0.840 | 1.279 | **IS-OOS consistent** ✓ |
| calendar_effect | monday_mean_reversion (hash #2) | 0.236 | 1.203 | mild consistency |
| volatility_regime | volatility_compression_breakout_ema_crossover | **−1.075** | **1.179** | **IS-OOS strong flip** ⚠⚠ |
| calendar_effect | weekend_volatility_compression_breakout | 0.402 | 1.110 | mild consistency |

**§6.2 Pattern classification (explicit numeric thresholds):**

Each candidate is classified by the joint (IS_Sharpe, OOS_Sharpe) tuple per the following criteria, applied in priority order:

- **IS-OOS consistent**: `IS_Sharpe ≥ 0.5 AND OOS_Sharpe ≥ 1.0` (meaningfully positive in both panels)
- **IS-OOS flip**: `IS_Sharpe < 0 AND OOS_Sharpe > 1.0` (sign mismatch with material magnitude on OOS)
- **OOS-only**: `|IS_Sharpe| < 0.15 AND OOS_Sharpe ≥ 1.0` (IS near zero, OOS meaningful)
- **mild consistency**: `0 ≤ IS_Sharpe < 0.5 AND OOS_Sharpe ≥ 1.0` (positive but moderate IS, meaningful OOS)

Applying the thresholds to the robust subset:

- **3 IS-OOS consistent**: `monday_morning_reversal_long` (IS 1.76 / OOS 2.89), `monday_dip_reversal` (IS 0.84 / OOS 1.28), `volume_surge_breakout_divergence` (IS 0.80 / OOS 2.04)
- **2 IS-OOS flips**: `monday_morning_dip_buy` (IS −0.17 / OOS +2.20), `volatility_compression_breakout_ema_crossover` (IS −1.08 / OOS +1.18)
- **2 OOS-only**: `monday_morning_momentum_200` (IS 0.08 / OOS 3.50), `monday_mean_reversion` hash #1 (IS 0.07 / OOS 1.95)
- **4 mild consistency**: `ema_crossover_momentum_acceleration` (IS 0.48 / OOS 3.50), `monday_pre_europe_momentum_fade` (IS 0.31 / OOS 1.62), `monday_mean_reversion` hash #2 (IS 0.24 / OOS 1.20), `weekend_volatility_compression_breakout` (IS 0.40 / OOS 1.11)

**§6.3 Two duplicate-name strategies with different hashes:** the table includes two `monday_mean_reversion` entries with different hypothesis_hashes (different DSL specifications sharing a name). Both pass the robust criterion; both have low-positive IS Sharpe.

---

## §7 Implications (Observations, NOT Adjudicated Conclusions)

The following observations are named per anti-pre-naming binding codified across Phase 5.1, Phase 5.2, and Phase A SEAL artifacts (precedent established in PHASE5_A_CLARIFICATION_NOTE §6 + §7 + §8 framings; CLAUDE.md Phase Marker carry-forward observations preserve this discipline). Each is eligible-not-named for separate Charlie register-event boundary.

**OBSERVATION 1: AMBIGUOUS verdict binds Phase B promotion HARDER per pre-bound rule.**

The pre-bound interpretation rule explicitly maps AMBIGUOUS → "reframe Phase A as 'what worked in this specific window' not 'stable signal'." This is not a post-hoc framing choice; it was locked before computation per V3 R1.2 patch. Phase B R5.1 candidate-subset commitment cannot claim the robust subset as "stable" without additional evidence. Whether this binds R5.1 toward 22-candidate (less selection-inflated) or pause is eligible-not-named.

**OBSERVATION 2: Per-candidate pattern is not uniform within the robust subset.**

Only 3 of 11 robust candidates are IS-OOS consistent (high in both); 2 show sign flips; 2 are OOS-only; the rest are mild consistency. The "robust subset" framing flattens substantial within-subset heterogeneity. Whether to elevate the 3 IS-OOS-consistent candidates as a sub-cohort, or treat the heterogeneity as a binding constraint on subset commitment, is eligible-not-named.

**OBSERVATION 3: 1 of 3 Stratum B robust shows IS-OOS strong sign flip.**

`volatility_compression_breakout_ema_crossover` (Stratum B robust per Phase A §5) has IS Sharpe −1.075 (strongly negative) and OOS Sharpe +1.179 (positive). This is a strategy that systematically lost money in walk-forward training windows but gained in the Phase 4 forward window. Whether this is a regime-flip phenomenon, a structural signal inversion, or pure window noise is eligible for separate DSL-inspection register-event (related to but distinct from OBS 7 R2.1 conditional prereq).

**OBSERVATION 4: 2 of 11 robust have IS Sharpe near zero but OOS Sharpe strong.**

`monday_morning_momentum_200` (IS 0.076 / OOS 3.504) and `monday_mean_reversion` hash #1 (IS 0.072 / OOS 1.947) generated essentially no signal during walk-forward training but produced top-tier OOS Sharpe in the 2528-bar forward window. These are most plausibly "window-specific" candidates whose Sharpe is concentrated in the Jan-Apr 2026 period. Phase A OBS 4 (monday-pattern curve-fit suspicion) is amplified by this pattern at the per-candidate level.

**OBSERVATION 5: 3 of 11 robust candidates show IS-OOS positive Sharpe consistency.**

`monday_morning_reversal_long`, `monday_dip_reversal`, `volume_surge_breakout_divergence` — these 3 candidates have positive Sharpe in both IS and OOS panels (per the explicit numeric thresholds in §6.2). Whether they warrant a separate sub-cohort framing in Phase B (with appropriate selection-inflation handling per Phase A OBS 5 + V3 R5.2) is eligible-not-named. NOT a retrofit Stratum D in this cycle. **No characterization in this cycle of whether this 3-candidate subset is "more defensible" or "more stable" than other subset framings** — Phase B subset evaluation is eligible-not-named per anti-pre-naming binding.

**OBSERVATION 6: N=39 cohort-level ρ=−0.15 is slightly negative-leaning within CI.**

While CI straddles 0, the point estimate is mildly negative. At n=39, a true ρ in [−0.30, −0.05] is consistent with observation. The interpretive distinction between "no IS-OOS relationship" and "weakly inverse IS-OOS relationship" is not statistically distinguishable here, but the latter would be consistent with mild overfitting-flip patterns where in-sample winners under-perform OOS. Whether to fire additional analytical cycles (Pearson on raw Sharpe; bootstrap CI; window-shifted rank correlation) to disambiguate is eligible-not-named.

**OBSERVATION 7: Walk-forward IS metric semantics.**

The IS Sharpe used (`wf_test_period_sharpe`) is the per-strategy aggregate Sharpe across 4 walk-forward sub-windows derived from the 2020-2021 train range per `config/environments.yaml v2` walk-forward decomposition. (The 2023 train range alone is too short for default walk-forward params to produce any sub-window, so does not contribute to this IS metric per §3.1.) This is itself a pseudo-OOS-within-train metric (each sub-window's test period is OOS relative to that sub-window's training data), not a pure in-sample fit. The R1.2 rank correlation is therefore between two OOS-class metrics on different data regimes (walk-forward test periods within the 2020-2021 train range vs the 2026-01-01 to 2026-04-16 forward holdout). Whether this affects the interpretation framing — and whether a stricter pure-in-sample comparison would yield different results — is eligible for separate methodology register-event.

**OBSERVATION 8: Forward-window precision correction propagates from R1.1.**

R1.1 (separate register-event within this cycle's path-3 parallel authorization) verified forward window is 2528 bars (2026-01-01 to 2026-04-16) per `phase4_forward_2026_07bps_v1/holdout_summary.json` `forward_window_metadata`, not the ~2900 estimated in Phase A V4 SEAL §6 OBS 8. R1.2 results are computed on the actual 2528-bar OOS data (no recomputation needed; CSV results already use the correct window). Phase A's individual-strategy power claims tighten slightly: at 2528 bars and Monday-pattern strategies firing at most weekly, max possible Monday triggers ≈ 15 (down from the ~17 implied by ~2900-bar calendar-month estimate). Per-strategy inference at low trade counts (1-2 trades, 2 candidates) remains the dominant constraint.

---

## §8 Phase B Decision Surface (Structure-Only Observations, NO Directional Claims)

R1.2 result is one input to Phase B register-events R4.1 (venue commitment), R5.1 (candidate-subset commitment), R6.1 (promotion-class commitment) per Phase B Pre-Sequence Roadmap V3. The following §8 observations document where R1.2 findings intersect existing Phase B option structures; no directional claim is made about which path Charlie fires.

**§8.1 Intersection with R5.1 (candidate-subset commitment):**

OBSERVATION 1 (AMBIGUOUS binds harder) + OBSERVATION 2 (within-subset heterogeneity) intersect R5.1's subset options:
- 22-candidate Stratum A (Phase 4 pre-registered scope): not directly informed by IS-OOS rank consistency since Phase 4 pre-registration was at composite-stratum level; R1.2 result is consistent with this scope being "the pre-registered population" without claim of IS-OOS stability
- 8-candidate Stratum A robust: per OBSERVATION 2 + 4 and §6.2 explicit thresholds, exactly 2 of 8 are IS-OOS consistent (`monday_morning_reversal_long`, `monday_dip_reversal`); the other 6 split as 1 IS-OOS flip (`monday_morning_dip_buy`) + 2 OOS-only (`monday_morning_momentum_200`, `monday_mean_reversion` hash #1) + 3 mild consistency (`monday_pre_europe_momentum_fade`, `monday_mean_reversion` hash #2, `weekend_volatility_compression_breakout`) — R5.1 commitment to 8-robust now requires explicit acknowledgment that 75% of the subset (6/8) is not IS-OOS-consistent
- 11-candidate cross-stratum: per OBSERVATION 3, 1 of 3 Stratum B robust shows strong sign flip; per OBSERVATION 5, only 3 candidates total are IS-OOS consistent across the 11
- "neither / pause": R1.2 result is consistent with pause framing without privileging it

Whether R5.1 should be commitment-conditional on a sub-cohort filter (e.g., "IS-OOS-consistent only" = 3 candidates total) is eligible-not-named.

**§8.2 Intersection with R5.2 (predeclared selection-inflation handling):**

R5.2 covers 8-robust OR 11-cross-stratum predeclared cohort criterion per V3 patch. R1.2 result informs the selection-inflation cost: the retrospective robust-subset identification has produced a cohort with substantial within-subset heterogeneity (3 consistent / 2 flipped / 2 OOS-only / 4 mild). The selection-inflation adjustment must account for this heterogeneity if R5.1 considers either subset. Whether R5.2 needs to widen to include sub-cohort filtering rules is eligible-not-named.

**§8.3 Intersection with R2.1 (volume_divergence DSL audit):**

OBSERVATION 3 (Stratum B `volatility_compression_breakout_ema_crossover` IS-OOS strong flip) does NOT fire R2.1 since R2.1 is volume_divergence-specific. But it surfaces a parallel concern: the Stratum B robust members may have heterogeneous signal-direction stability beyond the volume_divergence theme. Whether a broader Stratum B DSL audit (covering all 3 Stratum B robust + the −6.12 outlier) is warranted is eligible-not-named.

**§8.4 Intersection with R2.2 (Monday-pattern mechanistic investigation):**

OBSERVATION 4 (`monday_morning_momentum_200`, `monday_mean_reversion` hash #1 as IS-near-zero / OOS-strong patterns) materially intersects R2.2's question. Whether R2.2 scope should explicitly include "DSL audit of the 2 OOS-only monday-pattern candidates" alongside the broader parameter-carpeting question is eligible-not-named.

**§8.5 Intersection with R4.1 (venue commitment):**

R1.2 is venue-agnostic (rank correlation is invariant to cost-grid choice modulo selection of the OOS Sharpe metric at 7bps cost). R4.1 venue commitment to Branch.A (spot) vs Branch.B (futures) is not directly informed by R1.2. However, if R4.1 selects a venue with a different underlying data layer than the IS walk-forward (which is spot-based per Phase 5.2 §2.1), the IS-vs-OOS data-layer relationship itself shifts, separately from the IS-OOS rank instability surfaced by R1.2. Whether and how the venue-vs-data-layer relationship interacts with R1.2's rank-instability finding is eligible-not-named for separate Charlie register-event boundary.

---

## §9 Reserved Decisions (Anti-Pre-Emption)

Per anti-pre-emption invariant codified across Phase 5.1, Phase 5.2, and Phase A SEAL precedent — no decision pre-named in this cycle. Reserved for separate Charlie register-event boundary:

1. Whether to fire additional analytical cycles to disambiguate OBSERVATION 6 (Pearson on raw Sharpe; bootstrap CI; window-shifted rank correlation)
2. Whether the 3 IS-OOS-consistent candidates (per OBSERVATION 5) warrant separate sub-cohort framing at R5.1
3. Whether OBSERVATION 3 (Stratum B `volatility_compression_breakout_ema_crossover` IS-OOS flip) triggers a broader Stratum B DSL audit beyond the volume_divergence-focused R2.1
4. Whether R2.2 scope should explicitly include the 2 OOS-only monday-pattern candidates per OBSERVATION 4
5. Whether Phase A V4 SEAL warrants errata for the "~2900 bars" estimate per OBSERVATION 8 + R1.1 verification
6. Whether the walk-forward IS metric semantics caveat (OBSERVATION 7) warrants a separate pure-in-sample comparison cycle
7. R3.1a errata-vs-grandfathering decision (parked in transcript)
8. Phase B successor register-event sequencing (R2.x conditional / R3.1b empirical / R4.1 venue / Tier-0 pause)
9. R1.2 SEAL timing and Phase Marker advance (this register-event)
10. Other Charlie-specified reserved decisions

---

## §10 V# Anchor Chain (R1.2)

| V# | State | Description |
|----|-------|-------------|
| V1 | ARCHIVED | Pre-reviewer-round draft. Pre-bound rules locked per Charlie register #4 "approve c.5 hybrid"; computation deterministic from sealed CSVs; analysis script reproducible. |
| **V2** | **REVISED-POST-V1-REVIEW** | Post-V1-reviewer-round revised draft after 2-leg subagent dispatch (Codex + quant-research-advisor parallel per `feedback_reviewer_routing_subagent_default.md`). 11 ADOPT patches applied: Codex F1-1 BLOCKING (§7 OBSERVATION 5 rewrite — removed "most defensible 'stable signal' sub-cohort" pre-naming, replaced with neutral 3-of-11 framing) + Codex F1-2 MAJOR (§8.5 rewrite — removed "binds R4.1 toward Branch.A" directional language) + Advisor F1 SUBSTANTIVE (§3.1 IS metric aggregation specified precisely — "per-strategy aggregate Sharpe by walk-forward semantics corrected_test_boundary_v1 over 4 walk-forward sub-windows in 2020-2021 train range"; addresses both Advisor F1 ambiguity + Codex F2-9 "4 train_windows" imprecision) + Advisor F2 SUBSTANTIVE (§5.2 + §2 N=11 "weakly positive" → "informationally vacuous" with Fisher z-statistic + p-value) + Advisor F3 POLISH (§3.4 Fisher-z approximation note for Spearman) + Codex F2-3 (replace_all `volatility_compression_breakout_ema_cross` → `_ema_crossover` to match Phase A canonical naming) + Codex F2-11 (replace CLAUDE.md §10 sub-§§ citation with anti-pre-naming precedent reference; 3 locations) + Codex F2-12 (§7 OBS 8 "R1.1 verified" + "Advisor R1 H3-F2" qualified/removed; now references R1.1 register-event within cycle + holdout_summary.json forward_window_metadata) + Codex F3-4 (§2 N=39 "Fisher z 95% CI" → "Fisher-z-derived ρ 95% CI"; §2 N=11 + §5.2 same) + Codex F4-2 (§6.2 explicit numeric thresholds added). Reviewer reliability: 0/2 stalls + 0/2 hallucinations. Codex caught 2 anti-pre-naming defects Advisor missed (cross-model diversity validated); Advisor caught 3 methodology/framing issues Codex missed (complementary catch). |
| **V3** | **REVISED-POST-PFR** | Post-PFR-rule-Y re-review revised draft after 2-leg subagent dispatch. **Codex PFR verdict: BLOCK-V2** (5 carry-forward defects caught); **Advisor PFR verdict: APPROVE-WITH-MINOR-V2** but **2 substantive hallucinations** (claimed fictional `momentum_acceleration_signal` strategy with IS=0.13 / OOS=0.97 not in document + claimed CI width 0.96 contradicting actual 1.18 + claimed ρ=0.52 contradicting actual +0.1636) — **PUSHBACK applied on both advisor hallucinated findings** per Option II citation verification. V2→V3 applied 5 ADOPT patches from Codex: P1-F1 MINOR (§2 cross-check line 123 "weakly positive tendency" → "point estimate ρ=+0.16 with CI straddling 0 by a wider margin") + P1-F2 MINOR (`ema_crossoverover` typo from over-replace fixed at line 260) + P3-F1 SUBSTANTIVE (§8.1 "only 1-2 of 8" → "exactly 2 of 8" with full classification breakdown per formalized §6.2 thresholds) + P3-F2 SUBSTANTIVE (OBS 7 "pre-2022 + 2023 walk-forward test periods" → "walk-forward test periods within 2020-2021 train range" matching §3.1 precision; explicit note that 2023 train range alone is too short for default walk-forward params) + P3-F3 MINOR (status header + footer V1 DRAFT → V3 REVISED-POST-PFR; V# anchor chain updated). Reviewer reliability this round: 0/2 stalls; **1/2 verified hallucinations (Advisor)** — Option II PUSHBACK pattern preserved discipline; cumulative Reading 3 pilot ~29 dispatches: 2 stalls + 5 hallucinations (Phase 5.2 had 2, Phase A R2 had 1, R1.2 PFR has 2). V3 patches are mechanical literal application of reviewer-stated fixes → SKIP further PFR round per routing routine. |
| **V4** | **SEAL** | Canonical sealed artifact at register-event boundary (Charlie register #6 "SEAL fire" pending; V3 patches all mechanical literal landings of reviewer-stated PFR findings → SKIP further PFR per routing routine). |

---

## §11 References

**Sealed project artifacts (read-only at this cycle):**
- `docs/phase5/PHASE5_A_CLARIFICATION_NOTE.md` (Phase A V4 SEAL; §3.4 robust subset definition, §4-§5 stratum + theme breakdowns, §6 OBS 4 + OBS 5 + OBS 7 + OBS 8 + OBS 9, §7.1-§7.4 Phase B decision surface axes)
- `docs/phase5/PHASE5_2_VENUE_RECONCILIATION_NOTE.md` (Phase 5.2 V4 SEAL; §2 venue-mismatch finding, §6.4 Branch.A/B/C/D structures)
- `docs/phase5/PHASE5_1_COST_MODEL_INVESTIGATION_NOTE.md` (Phase 5.1 V4 SEAL; §3.2 D-classification, §7.1 successor paths)
- `data/phase2c_walkforward/batch_phase2c_15_main_fire_combined_corrected/walk_forward_results.csv` (sealed walk-forward source batch)
- `data/phase2c_evaluation_gate/phase4_forward_2026_{07,13,15,17}bps_v1/holdout_results.csv` (sealed Phase 4 cost-grid artifacts)
- `data/phase2c_evaluation_gate/phase4_forward_2026_07bps_v1/holdout_summary.json` (sha256-locked metadata)
- `config/environments.yaml` (v2; walk-forward + train_windows definition)
- `docs/discipline/METHODOLOGY_NOTES.md` (§7 asymmetric confidence reporting; informs C.5 hybrid pre-bind discipline)
- `CLAUDE.md` Phase Marker (carry-forward observations + anti-pre-emption discipline; cross-cycle reference)

**Analysis artifact (this cycle, not sealed):**
- `/tmp/r1_2_rank_correlation_analysis.py` (deterministic Python stdlib; reproducible from CSVs)

**Cross-reviewer adjudication corpus (this cycle):**
- R1.2 threshold pre-bind reviewer round (Round 4 of Phase B prereq dispatch series): Codex + quant-research-advisor parallel; both CONVERGED on C.5 hybrid
- ADOPT/PUSHBACK/DEFER per-fix adjudication recorded in conversation transcript
- 0/2 stalls + 0/2 hallucinations this round (cumulative Reading 3 pilot: ~25 dispatches, 2 stalls + 3 hallucinations)

**External literature posture:** None invoked. All factual claims grounded in sealed in-repo artifacts.

**End of V4 SEAL.** R1.2 Bucket-1 investigation cycle SEALED at this register-event boundary. Cycle resolved Phase A V4 SEAL §6 OBSERVATION 9 (IS-OOS rank correlation gating prerequisite for Phase B promotion) as: **N=39 primary gate AMBIGUOUS** (ρ=−0.1474, Fisher-z-derived 95% CI=[−0.4423, +0.1764]) per pre-bound C.5 hybrid rule; pre-bound interpretation rule fires → **reframe Phase A robust subset as window-specific not stable signal**. **N=11 directional check** (ρ=+0.1636, CI=[−0.4837, +0.6953], width 1.18) informationally vacuous; no load-bearing corroboration in either direction. Per-candidate detail: 3 IS-OOS consistent + 2 IS-OOS flips (1 of 3 Stratum B robust) + 2 OOS-only + 4 mild consistency, per §6.2 explicit numeric thresholds. 10 OBSERVATIONS named anti-pre-naming; §8 Phase B Decision Surface intersections enumerated without directional claims; 10 reserved decisions. **NO git tag at SEAL** per CLAUDE.md "Bucket-1 investigation note ≠ arc-level closeout" Tag policy + Phase 5.1 + Phase 5.2 + Phase A precedent. Phase Marker + atomic `docs/phase_marker_history.md` update follow at SEAL bundle.

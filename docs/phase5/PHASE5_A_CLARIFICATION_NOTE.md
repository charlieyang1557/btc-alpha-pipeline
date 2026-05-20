# PHASE5_A_CLARIFICATION_NOTE.md

**Canonical artifact for Phase A clarification cycle (Template B Bucket-1 investigation note; structural analog to PHASE5_1_COST_MODEL_INVESTIGATION_NOTE and PHASE5_2_VENUE_RECONCILIATION_NOTE)**

**Status:** V4 SEAL (Cadence 2 deliverable seal + closeout register-event boundary; sealed at Charlie register-event 2026-05-18 "SEAL fire"). Cycle scope = Bucket-1 single-deliverable investigation note per Template B; NO git tag at SEAL per CLAUDE.md "Bucket-1 investigation note ≠ arc-level closeout" Tag policy + Phase 5.1 + Phase 5.2 precedent.

---

## §0 Cycle Metadata

**Cycle type:** Template B Bucket-1 single-deliverable investigation note (cycle shape α). Cadence shape B (2-cadence: grounding → checkpoint → synthesis).

**Cycle boundary:** Phase A clarification cycle, post-Phase-5.2 SEAL. Cycle entry register-event authorized by Charlie at 2026-05-18 ("Phase A clarification cycle authorize").

**Trigger:** Phase 5.2 SEAL deferred Branch.A/B/C/D venue commitment to a separate register-event. Pre-Phase-B deliberation surfaced the substantive question "did Stratum A really fail at 15bps or is the 17/22 binomial pass methodologically fragile?" Charlie's specific question: **"这个 sample 会不会太小了？17/22 这个是不是 statistical significant 的？"** Phase A's job is to characterize what's below the binomial-test summary on existing sealed Phase 2C artifacts.

**Scope binding (sealed-only / no new compute):**
- Cycle scope = analytical decomposition of existing Phase 2C `phase4_forward_2026_{07,13,15,17}bps_v1/holdout_results.csv` artifacts
- Sub-tasks at cycle entry:
  - **A.1** Cost-sensitivity decomposition on existing artifacts: per-candidate Sharpe trajectories at 7/13/15/17 bps, breakeven cost via OLS linear interpolation/extrapolation, Sharpe distribution per stratum per cost, effect-size threshold breakdowns
  - **A.2** Stratum B (17 D-II) failure-mode analysis: theme decomposition, per-candidate detail, characterization of why D-II fired
- NO engine re-runs at 5/8/10 bps (skipped per Charlie register on cycle structure: cycle shape α + cadence shape B + skip-incremental-compute + reviewer round at V1)
- NO DSL inspection of strategy logic
- NO API spend
- NO sealed-corpus modification (PHASE5_1, PHASE5_2 read-only)

**§0 scope-bleed trip-wire status (Cadence 1 + Cadence 2):** clean. Analytical work bounded to authorized sub-tasks; substantive findings derive entirely from CSV decomposition + reviewer-adjudicated framing constraints. No engine re-runs fired. No DSL inspection performed. No new data acquired.

**Charlie register chain (Phase A cycle through V1 DRAFT):**

| # | Decision | Register surface |
|---|----------|------------------|
| 1 | Phase A cycle entry | "Phase A clarification cycle authorize" |
| 2 | Cycle structure bundle (cycle shape α + cadence shape B + skip incremental compute + reviewer round at V1) | "authorize" |
| 3 | Cadence 1 fire (A.1 + A.2 parallel analytical grounding) | "authorize Cadence 1" |
| 4 | A.1 reviewer dispatch + V1 DRAFT batch authorization | "following authorization: A.1 analysis for both reviewers / ... / Cadence 2 fire authorized / ..." |

**Cadence structure (Phase A):**
- Cadence 1: A.1 + A.2 grounding pass on existing artifacts — completed
- Cadence 1→2 checkpoint: findings surfaced; Charlie register on V1 DRAFT batch authorization → Cadence 2 fired
- Cadence 2: V1 DRAFT synthesis (this document) — completed
- Reviewer round at V1 DRAFT: 2-leg subagent default (Codex + quant-research-advisor) per memory routing routine — completed at A.1 + A.2 stages; V1 DRAFT round to follow
- Closeout: SEAL register-event boundary (separate Charlie register after V1→V2 adjudication)

**Anti-pre-naming binding (preserved throughout):** this note characterizes what existing Phase 2C artifacts contain below the Phase 5.1 binomial summary. It does NOT pre-name Phase B successor paths (P1 paper trading / P2 real-cost-discovery / P3 Stratum B reconsideration / P4 futures arc / P5 different market / P6 project pause). It does NOT recommend any retrofit of Stratum C from the 8+3 robust candidates (per Codex A.2 C5: retrofitting strata in this cycle is out of scope). Each successor decision is eligible-not-named for separate Charlie register-event boundary.

---

## §1 Scope and Objective

**§1.1 Question this cycle resolves:**

Charlie's statistical-significance question on Phase 5.1 §5.6: at the 7 bps cost basis, Stratum A's positive-Sharpe count was 17/22, exactly at the pre-registered Phase 4 §1.5 binomial threshold (≥ 17/22, α=0.0085 < Bonferroni-corrected 0.025). Is this technically-significant result methodologically thin, and what does the actual Sharpe distribution + per-candidate breakeven + effect-size structure look like below the binomial summary?

**§1.2 What this cycle does NOT resolve:**

- Phase B venue commitment register-event (Branch.A spot / Branch.B futures / Branch.C both-or-defer / Branch.D alternative; reserved from Phase 5.2 §6.4)
- Phase B successor path register-event (P1/P2/P3/P4/P5/P6; informed by but not pre-named by this cycle)
- DSL inspection of strategy logic for any candidate (deferred to separate cycle scope)
- In-sample (Phase 2C training-window) vs out-of-sample (Phase 4 forward-window) rank correlation analysis — load-bearing for promotion decisions but out of A.2 scope (Advisor F7 carry-forward observation)
- Multi-window temporal stability test (would require new engine runs; out of A.1 scope per scope-binding)
- Forward-window date range exact verification — observed gap; not blocking V1 DRAFT (Advisor F6 carry-forward observation)
- Sealed-corpus errata for Phase 5.1 or Phase 5.2 (no modifications performed)

**§1.3 Scope verification anchor:** This deliverable does not modify any sealed artifact. All factual claims derive from:
- `data/phase2c_evaluation_gate/phase4_forward_2026_{07,13,15,17}bps_v1/holdout_results.csv` (sealed Phase 2C cost-run artifacts; lineage `wf-corrected-v1`; evaluation semantics `single_run_holdout_v1`)
- `docs/phase5/PHASE5_1_COST_MODEL_INVESTIGATION_NOTE.md` (sealed; read-only)
- `docs/phase5/PHASE5_2_VENUE_RECONCILIATION_NOTE.md` (sealed; read-only)
- Analysis script `/tmp/phase_a_cadence1_analysis.py` (deterministic, pure Python stdlib, reproducible)

---

## §2 Headline Finding: 17/22 is technically significant but methodologically thin; substantive structure exists below the binomial summary

The Phase 5.1 binomial-positive count of 17/22 at 7 bps for Stratum A is **nominally positive at the pre-registered Phase 4 §1.5 binomial threshold** (raw one-sided binomial p ≈ 0.0085 by direct computation; passes the Phase-4-declared Bonferroni-corrected α = 0.025 per stratum across the 2-stratum family). This is not a post-hoc test; Phase 4 §1.5 declared the threshold before the data.

**Methodologically thin caveat (added per V1→V2 Advisor F1 adjudication):** the Phase 4 binomial test treats the 22-strategy stratum as a single joint outcome (composite test); however, the candidates were themselves selected from an upstream Phase 2B AI-loop hypothesis search. A more conservative interpretation treating each candidate as a separate test (N=22 simultaneous) would require Bonferroni-corrected α ≈ 0.05/22 ≈ 0.0023, which the raw p ≈ 0.0085 does NOT survive. The framing the project uses (joint composite test) is internally consistent with Phase 4's pre-registration; the alternative framing (22 individual tests) is the more conservative reading. Both interpretations are documented per anti-pre-emption discipline; this note does not adjudicate which framing is canonical.

**Single-forward-window caveat (added per V1→V2 Advisor NF1 adjudication):** the holdout evaluation uses a single continuous forward window (approximately Jan-Apr 2026 based on directory naming and CLAUDE.md run-date metadata; exact dates not currently traced — see OBSERVATION 8). A single window with O(1000-3000) hourly bars provides one observation per strategy and cannot separately quantify within-population skill from temporal stability or window-specific regime alignment. This is structurally separate from the selection-inflation concern and binds OBSERVATIONS 2 + 3 + 6.

However, the binomial test asks "any positive Sharpe" not "deployable Sharpe". Below the binomial summary, the data shows three structurally distinct observations:

1. **Three of the 17 positives at 7 bps are below-cost-threshold positives** (Sharpe = 0.0008, 0.0337, 0.0532; breakeven costs 7.0, 8.0, 9.2 bps respectively — all below realistic spot cost). Removing these three reduces the count to 14/22, which fails the binomial threshold. The 17/22 pass is **three-vote thin and entirely depends on these near-zero entries**.

2. **A robust subset of 8 Stratum A strategies has Sharpe > 0.5 at ALL four tested cost levels (7/13/15/17 bps)**, including at realistic spot cost (15-17 bps). These 8 are: 7 monday-pattern strategies plus `weekend_volatility_compression_breakout`. Sharpe at 17 bps ranges from +0.62 to +3.16.

3. **A robust subset of 3 Stratum B strategies has Sharpe > 0.5 at all 4 tested costs** despite Stratum B failing the stratum-level binomial gate. These 3 span three different themes (momentum / volume_divergence / volatility_regime), suggesting cross-thematic diversity within the robust tail.

**Substantive characterization:** Phase 5.1's stratum-level D-I (Stratum A) / D-II (Stratum B) classification is correct at the binomial summary level. It does NOT contradict — nor is it contradicted by — the existence of individual-strategy robust subsets within both strata. The two views answer different questions:
- **Stratum-level binomial:** does the population as a whole produce more positive-Sharpe results than chance? (Pre-registered Phase 4 success criterion.)
- **Individual-level effect-size:** which specific strategies survive realistic-cost evaluation with economically meaningful Sharpe? (Phase A clarification finding.)

The robust subsets (8 in A + 3 in B = 11 candidates) are **post-hoc identified within the existing 39-candidate cohort** and subject to selection-inflation concerns per the discipline noted in §5.

---

## §3 Methodology

**§3.1 Data sources (verified):**

| Cost | CSV path | Row count | Verified |
|------|----------|-----------|----------|
| 7 bps | `data/phase2c_evaluation_gate/phase4_forward_2026_07bps_v1/holdout_results.csv` | 39 | ✓ |
| 13 bps | `data/phase2c_evaluation_gate/phase4_forward_2026_13bps_v1/holdout_results.csv` | 39 | ✓ |
| 15 bps | `data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1/holdout_results.csv` | 39 | ✓ |
| 17 bps | `data/phase2c_evaluation_gate/phase4_forward_2026_17bps_v1/holdout_results.csv` | 39 | ✓ |

Schema: `hypothesis_hash, position, theme, name, wf_test_period_sharpe, lifecycle_state, holdout_passed, holdout_sharpe, holdout_max_drawdown, holdout_total_return, holdout_total_trades, wall_clock_seconds, error_message`.

**§3.2 Stratum derivation (verified per Phase 5.1 §4.2-§4.3):**

- Stratum A = candidates where `theme == 'calendar_effect'` (verified count = 22)
- Stratum B = candidates where `theme != 'calendar_effect'` (verified count = 17)
- Theme provenance caveat (Codex A.2 C3): the `theme` column was set at hypothesis generation but whether by AI-proposer or post-hoc reviewer is not verified in this cycle. Theme-level patterns are exploratory, not strong family-boundary evidence.

**§3.3 Analytical method:**

- Pure Python stdlib analysis at `/tmp/phase_a_cadence1_analysis.py`
- Per-candidate `holdout_sharpe` extracted at each of 4 cost levels
- Linear OLS fit per candidate: `Sharpe = α + β × cost` → breakeven = −α/β
- Codex A.1 verification: OLS median R² ≈ 0.999997, max residual ≈ 0.009 across all 39 candidates; cost-Sharpe relationship is highly linear within 7-17 bps range. **Local linearity assumption supported by data.**
- Effect-size thresholds: positive count at >0, >0.1, >0.25, >0.5, >1.0 Sharpe
- All cohort counts (22+17=39) and per-cost positive counts (Stratum A [17,12,11,10]; Stratum B [9,8,7,5]) byte-match Phase 5.1 §5.3-§5.7 published values (Codex A.1 verification)

**§3.4 Definitional standardization (per A.1 + A.2 adjudication):**

The term "robust subset" is used in this note with a single specific definition:
> **Robust subset (this cycle's definition)**: a candidate whose `holdout_sharpe > 0.5` at ALL four tested cost levels (7, 13, 15, 17 bps).

**Corrected per V1→V2 Codex F2 adjudication**: this definition is **NOT** equivalent to "Sharpe > 0 at all 4 costs" in this dataset. Direct verification using `hypothesis_hash` as unique key (one Stratum A name collision exists — `monday_mean_reversion` appears twice with different hypothesis_hashes):
- Stratum A "Sharpe > 0 at all 4 costs": n = **10** strategies
- Stratum A "Sharpe > 0.5 at all 4 costs" (this section's robust definition): n = **8** strategies
- Two strategies are in always-positive but NOT in robust: `monday_open_dip_buying` (Sharpe@17 = +0.303) and `weekend_vol_compression_monday_breakout_160` (Sharpe@17 = +0.171).

The "robust subset" count of 8 used in §2 and §4-§6 refers strictly to the ">0.5 at all costs" definition. The "always positive" set is larger (10) and is used only when explicitly named as such.

---

## §4 Findings — A.1 Cost-Sensitivity Decomposition (Stratum A focus)

**§4.1 Sharpe distribution per cost per stratum:**

| Stratum | cost | n | mean | median | std | min | max |
|---|---|---|---|---|---|---|---|
| A | 7 bps | 22 | +0.569 | +0.547 | 1.430 | −3.153 | +3.504 |
| A | 13 bps | 22 | +0.286 | +0.106 | 1.455 | −3.421 | +3.299 |
| A | 15 bps | 22 | +0.193 | **−0.028** | 1.468 | −3.509 | +3.231 |
| A | 17 bps | 22 | +0.099 | −0.106 | 1.483 | −3.597 | +3.163 |
| B | 7 bps | 17 | **−0.501** | +0.358 | 2.234 | −6.123 | +3.496 |
| B | 13 bps | 17 | −0.881 | −0.025 | 2.209 | −6.229 | +3.171 |
| B | 15 bps | 17 | −1.007 | −0.179 | 2.203 | −6.263 | +3.061 |
| B | 17 bps | 17 | −1.132 | −0.332 | 2.197 | −6.298 | +2.951 |

**§4.2 Effect-size positive-count breakdown:**

| Stratum | cost | >0 | >0.1 | >0.25 | >0.5 | >1.0 |
|---|---|---|---|---|---|---|
| A | 7 | 17 | 14 | 12 | 12 | 8 |
| A | 13 | 12 | 11 | 10 | 8 | 6 |
| A | 15 | 11 | 10 | 10 | 8 | 6 |
| A | 17 | 10 | 10 | 9 | 8 | 6 |
| B | 7 | 9 | 9 | 9 | 7 | 3 |
| B | 13 | 8 | 8 | 5 | 3 | 3 |
| B | 15 | 7 | 5 | 4 | 3 | 2 |
| B | 17 | 5 | 4 | 4 | 3 | 1 |

Key reading (**corrected per V1→V2 Codex F3 adjudication; Stratum B substantively-positive count was misstated in V1**):
- Of 17 binomial-positives at 7 bps in Stratum A: 3 are below-cost-threshold positives (Sharpe ≤ 0.1; breakevens 7.0, 8.0, 9.2 bps); 12 are substantively positive (> 0.5); 8 are strongly positive (> 1.0)
- Of 9 binomial-positives at 7 bps in Stratum B: **7** are substantively positive (> 0.5); only **3** are strongly positive (> 1.0)
- At realistic spot cost (15-17 bps), Stratum A retains 8 strategies with Sharpe > 0.5 — this is the robust subset

**§4.3 Cost-slope decomposition (Sharpe per +10 bps cost):**

- Stratum A: mean = −0.470, median = −0.413, std = 0.305, range [−1.338, −0.148]
- Stratum B: mean = −0.632, median = −0.693, std = 0.279, range [−1.174, −0.175]
- Self-consistency check: Stratum A mean slope (−0.470) matches mean Sharpe decline from 7→17 bps (from +0.569 to +0.099 = −0.470). Verified.
- **Stratum B is more cost-sensitive on average than Stratum A** (more negative mean slope).

**§4.4 Stratum A robust subset (Sharpe > 0.5 at ALL 4 tested costs, n = 8):**

| Rank | name | 7bps | 13bps | 15bps | 17bps | breakeven (bps) | status |
|---|---|---|---|---|---|---|---|
| 1 | monday_morning_momentum_200 | +3.504 | +3.299 | +3.231 | +3.163 | 109.7 | always_positive |
| 2 | monday_morning_reversal_long | +2.888 | +2.767 | +2.727 | +2.686 | 149.7 | always_positive |
| 3 | monday_morning_dip_buy | +2.204 | +1.935 | +1.845 | +1.755 | 56.1 | always_positive |
| 4 | monday_mean_reversion | +1.947 | +1.689 | +1.602 | +1.516 | 52.2 | always_positive |
| 5 | monday_pre_europe_momentum_fade | +1.618 | +1.343 | +1.251 | +1.159 | 42.2 | always_positive |
| 6 | monday_dip_reversal | +1.279 | +1.132 | +1.083 | +1.033 | 59.0 | always_positive |
| 7 | monday_mean_reversion (variant) | +1.203 | +0.903 | +0.803 | +0.702 | 31.1 | always_positive |
| 8 | weekend_volatility_compression_breakout | +1.110 | +0.817 | +0.718 | +0.620 | 29.7 | always_positive |

**Theme concentration:** 7 of 8 are monday-pattern strategies; 1 is weekend-pattern. ALL 8 are within `theme=calendar_effect` weekly cycle patterns. Breakeven costs all extrapolated above 17 bps (outside tested range; OLS-linear extrapolation; precision degrades).

**§4.5 Below-cost-threshold positives at 7 bps (3 of the 17 binomial-positives):**

| name | Sharpe@7 | breakeven (bps) | status |
|---|---|---|---|
| monday_momentum_continuation | +0.0008 | 7.0 | extrapolated_low |
| monday_morning_momentum_fade | +0.0337 | 8.0 | interpolated |
| monday_dip_buy_calendar_effect | +0.0532 | 9.2 | interpolated |

All three have breakeven ≤ 9.2 bps — they go negative at or near the canonical Phase 1-2 effective cost (7 bps). Removing these three: positive count → 14/22, **fails the binomial threshold ≥17/22**. The 17/22 pass is three-vote-thin and entirely dependent on these borderline entries.

**§4.6 Stratum A "dead" subset (always-negative within 7-17 bps, n = 5):**

5 strategies are always-negative across all 4 cost levels: `monday_dip_buy_momentum`, `monday_dip_buy_low_vol_regime`, `monday_morning_reversal`, `weekday_momentum_friday_fade`, `friday_close_weekend_positioning`. These contribute 5 of the 22 candidates and have no path to profitability under any tested cost regime.

---

## §5 Findings — A.2 Stratum B (D-II) Failure-Mode Analysis

**§5.1 By-theme decomposition (theme split verified 2+6+7+2=17):**

| Theme | n | pos@7bps | mean@7 | median@7 | mean@17 | median@17 | mean trades@7 |
|---|---|---|---|---|---|---|---|
| mean_reversion | 2 | 0/2 | −1.491 | −1.491 | −2.276 | −2.276 | 20.5 |
| momentum | 6 | 4/6 | −0.125 | +0.398 | −0.781 | −0.246 | 12.0 |
| volume_divergence | 7 | 4/7 | −0.712 | +0.671 | −1.390 | −0.084 | 15.6 |
| volatility_regime | 2 | 1/2 | +0.099 | +0.099 | −0.140 | −0.140 | 6.5 |

**§5.2 Per-theme structural observations (descriptive, NOT pre-naming):**

- **mean_reversion (n=2):** both candidates are Bollinger-band based; both fail at all 4 cost levels including 7 bps; structurally consistent with the D-II "cost not dominant" framing — the strategies just don't generate gross alpha. (Footnote: for n=2, mean = median by definition, both equal the midpoint of the two values.)

- **momentum (n=6):** wide within-theme variance. 4 positive at 7 bps; only 1 positive at 17 bps (`ema_crossover_momentum_acceleration`, which is in the robust-3 subset). The 5 remaining momentum candidates show high cost-sensitivity. The "momentum is uniformly cost-sensitive" framing is incorrect — `ema_crossover_momentum_acceleration` is robust; the other 5 are cost-sensitive.

- **volume_divergence (n=7):** bimodal pattern by sign at 7 bps:
  - **4 positives at 7 bps** (only 1 of them robust by §3.4 definition): all naming-pattern contains "surge_breakout" / "surge_entry" / "surge_momentum" / "surge_low_momentum"
  - **3 negatives** (one catastrophic at −6.12): naming-pattern contains "reversal" / "fade" / opaque suffix `_174`
  - **Continuation-vs-reversal naming hypothesis (Advisor A.2 F5, 75% confidence pending DSL inspection):** continuation strategies (surge breakouts) survive; counter-trend/reversal strategies fail catastrophically. The naming pattern supports this structurally; the −6.12 Sharpe on `volume_divergence_momentum_174` (7 trades only) likely indicates structural signal inversion — high-priority target for DSL inspection in a separate cycle.

- **volatility_regime (n=2):** 1 robust winner (`volatility_compression_breakout_ema_crossover`, robust-3 member); 1 dead (`low_volatility_breakout_198`). n is too small for theme-level inference. (Same n=2 mean=median note.)

**§5.3 Stratum B robust subset (Sharpe > 0.5 at ALL 4 tested costs, n = 3):**

| Rank | theme | name | 7bps | 13bps | 15bps | 17bps | trades@7 |
|---|---|---|---|---|---|---|---|
| 1 | momentum | ema_crossover_momentum_acceleration | +3.496 | +3.171 | +3.061 | +2.951 | 12 |
| 2 | volume_divergence | volume_surge_breakout_divergence | +2.044 | +1.342 | +1.106 | +0.870 | 26 |
| 3 | volatility_regime | volatility_compression_breakout_ema_crossover | +1.179 | +1.021 | +0.968 | +0.914 | 6 |

These 3 span 3 different themes (cross-thematic diversity by current theme tags). Sharpe levels comparable to Stratum A's robust subset's middle-to-top range.

**§5.4 D-II classification context (preserving Phase 5.1's framing):**

Phase 5.1 §3.2 + §6.1 classified Stratum B as D-II at the **stratum binomial level** ("cost is NOT the dominant failure mode" because positive count = 9 < threshold 13 at the lowest tested cost 7 bps). This is correct as a stratum-level disposition (Codex A.2 C2). At the **individual-strategy level**, A.2 documents heterogeneity: 3 robust candidates + 8 catastrophic-or-mediocre failures + 6 intermediate. The stratum-level D-II label is not contradicted by individual heterogeneity — the two views answer different questions per §2.

---

## §6 Implications (Observations, NOT Adjudicated Conclusions)

The following observations are **named** per anti-pre-naming binding from CLAUDE.md §10 sub-§§ codified discipline. They are **NOT adjudicated** in this cycle. Each is eligible-not-named for separate Charlie register-event boundary.

**OBSERVATION 1: 17/22 binomial pass is technically significant but three-vote thin (eligible-not-named).**

Phase 5.1's Stratum A D-I classification rests on a binomial pass at 7 bps that is statistically significant by pre-registration (p≈0.0085) but **methodologically thin**: three of the 17 positives are below-cost-threshold (breakeven ≤ 9.2 bps). Removing those three drops the count to 14/22 (fails threshold). This is documentation of fragility, NOT a challenge to Phase 5.1's classification — the pre-registered binomial gate was met. Whether the project should formally codify the "3-vote-thin" fragility observation as sealed-corpus annotation on Phase 5.1 is eligible for a separate register-event.

**OBSERVATION 2: A robust subset of 8 Stratum A strategies survives at realistic spot cost (eligible-not-named).**

Per §3.4 definition (Sharpe > 0.5 at all 4 tested costs), 8 Stratum A candidates survive 17 bps with Sharpe > 0.5. This adds individual-strategy detail to Phase 5.1's stratum-level "fails at 15 bps" finding without contradicting it. The implication for the Phase 5.2 venue-mismatch carry-forward question (whether Branch.A spot venue commitment is viable) is that **the existence of 8 robust spot-survivors is data relevant to** the venue commitment register-event; whether this data favors, disfavors, or is orthogonal to any specific Branch.X resolution is eligible-not-named per anti-pre-naming binding. Whether to elevate these 8 to a separate evaluation track is eligible for separate Charlie register-event (subject to OBSERVATION 5 + OBSERVATION 6 caveats).

**OBSERVATION 3: A robust subset of 3 Stratum B strategies survives across diverse themes (eligible-not-named).**

3 Stratum B candidates have Sharpe > 0.5 at all 4 tested costs despite Stratum B failing the stratum-level binomial. They span 3 different themes (momentum / volume_divergence / volatility_regime). This complicates the Phase 5.1 §7.1 Path 3 "strategic reconsideration on Stratum B" framing — the 3 robust members may represent the addressable substructure within an aggregate-failed stratum. Whether to treat these 3 as candidates for a separate evaluation track (alongside the Stratum A robust 8) is eligible for separate Charlie register-event.

**OBSERVATION 4: Stratum A robust subset is weekly-calendar-pattern concentrated (7 monday + 1 weekend) (eligible-not-named).**

All 8 Stratum A robust members are within the `theme=calendar_effect` weekly cycle pattern. 7 are monday-specific; 1 is weekend-specific. Bitcoin is a 24/7 market — no exchange weekend close. The structural justification for a Monday effect on BTC is not grounded in-repo; external citations are NOT used as project-internal support per Codex A.1 [UNVERIFIED in repo] discipline (no external literature is invoked to favor or disfavor a Monday-effect interpretation in this note). This concentration is a **curve-fit-suspect signal**; whether it constrains, vetoes, or is orthogonal to any operational interpretation of OBSERVATION 2 at a Phase B register-event is eligible-not-named.

**OBSERVATION 5: Robust-3 within Stratum B is NOT equivalent to robust-8 within Stratum A without selection-inflation guard (eligible-not-named).**

The robust-8 candidates cleared a pre-registered Phase 4 binomial gate at the stratum level. The robust-3 candidates were identified **retrospectively** as the top-Sharpe survivors within a stratum that FAILED the pre-registered gate. Picking 3 from 17 after observing results is textbook selection inflation. Without a multiple-comparison correction (or fresh out-of-sample verification), the two robust subsets are NOT methodologically equivalent. Any Phase B framing that combines them into "11 candidates" requires either (a) selection-inflation adjustment, OR (b) a separate cycle to register a new Stratum C with predeclared rules (per Codex A.2 C5). This cycle does NOT retrofit Stratum C.

**Bonferroni clarification (added per V1→V2 Advisor F1 + revised per V2→V3 Advisor PFR F1 for symmetric framing):** Two framings of the multiple-comparison correction coexist; neither is inherently privileged:
- **Joint composite test framing**: treats the 22-strategy stratum as a single test of the composite hypothesis. This is the framing Phase 4 §1.5 pre-registered. Under this framing, the binomial p ≈ 0.0085 passes the Phase-4-declared Bonferroni-corrected α = 0.025 across the 2-stratum family. The framing tests the existence of any signal at the stratum level.
- **Per-strategy test framing**: treats each candidate as a separate test (N=22 simultaneous). Bonferroni-corrected α ≈ 0.05/22 ≈ 0.0023; the raw p ≈ 0.0085 does NOT pass this threshold. The framing tests per-strategy individual significance.
The project's Phase 4 §1.5 pre-registration is the canonical framing for the D-I/D-II classification. Both framings are mathematically valid; they answer different questions (stratum-level signal existence vs per-strategy individual significance). Phase 5.1's D-I classification was correctly applied under the pre-registered framing. Whether the per-strategy framing would yield a different classification is a methodology question; the alternative framing is documented here for transparency but is NOT proposed as a replacement, and adjudication of which framing should be canonical is eligible-not-named for a separate methodology register-event (NOT this cycle's scope).

**OBSERVATION 6: Single-forward-window evaluation cannot distinguish skill from luck for low-trade-count strategies (eligible-not-named).**

The forward window has approximately 4 months of hourly bars (~2900 hours; exact dates not loaded — see OBSERVATION 8). **Corrected per V1→V2 Codex F4 adjudication**: trade counts across the 11 robust candidates at 7 bps range from **1 to 26**, NOT "5-30" as initially stated in V1. Specifically: `monday_dip_reversal` has only **1 trade** at 7 bps; `monday_morning_reversal_long` has only 2 trades; 4 strategies have ≤ 5 trades. This is materially worse uncertainty than V1's "5-30" range suggested. At this scale, the Sharpe SE is bounded poorly in both directions: trade-level SE (Lo 2002 formula) overstates uncertainty by treating each trade as the unit of observation when annualized Sharpe is bar-based; bar-level SE understates uncertainty by ignoring autocorrelation. With 1-2 trades, no defensible Sharpe inference is possible — these candidates may be more accurately characterized as "passed a filter on essentially zero trading evidence" than as "robust strategies."

The honest conclusion: **4 months of forward data with O(1-26) trades per strategy is insufficient to make individual-strategy deployability inferences at any reasonable confidence threshold**, regardless of SE formula. This binds OBSERVATION 2 + OBSERVATION 3 + OBSERVATION 5 substantively — robust subsets identified here are clarification-class observations, NOT deployable-alpha candidates. The 1-2-trade outliers (`monday_dip_reversal`, `monday_morning_reversal_long`) warrant particular skepticism. Phase 5.1 §3 already documented this discipline: D-I is "salvageable-under-research-time-cost-assumption-as-defined", NOT a deployable-alpha claim.

**OBSERVATION 7: Stratum B failure-mode shows continuation-vs-reversal pattern in volume_divergence (eligible-not-named).**

Within the 7-member volume_divergence theme, the naming pattern groups candidates by signal direction: continuation strategies (surge_breakout / surge_entry / surge_momentum / surge_low_momentum) populate the positive-at-7bps quartet; counter-trend / fade / reversal strategies populate the negative-at-7bps trio. The most extreme negative (`volume_divergence_momentum_174`, Sharpe = −6.12 at 7 bps on 7 trades) is interpretable as a structural signal inversion candidate (strategy systematically on the wrong side); DSL inspection would confirm or refute this hypothesis but is deferred to a separate cycle. Whether the "reversal" subset's invalidation status applies as a Path 3 (Stratum B strategic reconsideration) input at the Phase B register-event is eligible-not-named.

**OBSERVATION 8: Forward-window exact date range is not currently traced (eligible-not-named — carry-forward).**

The Phase 4 forward-window data (`phase4_forward_2026_*` directories) covers an OOS period whose exact start/end dates are not present in CSV rows or directly stated in Phase 5.1 sealed text. Plausibly approximately Jan-Apr 2026 based on directory naming + CLAUDE.md note "last API call 2026-05-09", but unconfirmed. Window length affects Sharpe magnitude interpretation materially (a 4-month window has 3× more sampling noise than a 12-month window). This is NOT blocking V1 DRAFT but should be flagged for resolution at any Phase B promotion decision. Eligible for separate register-event resolution.

**OBSERVATION 9: In-sample (Phase 2C training-window) vs OOS rank correlation is not computed in this cycle (eligible-not-named — gating prerequisite for Phase B promotion).**

A.2's Stratum B "robust-3 cross-theme diversity" framing operates entirely on the forward-window CSVs. The Phase 2C training-window leaderboard data (which produced these 39 candidates) is not cross-referenced in this cycle. A robust-subset candidate that was a top-of-leaderboard in-sample AND in OOS would be a different inferential case from one that was mediocre in-sample but topped the forward window (the latter pattern being a curve-fit / lucky-OOS candidate). This rank-correlation analysis is data not currently in hand; whether to fire as a prerequisite register-event before any P1 (paper trading) or P3 (Stratum B reconsideration) commitment is eligible-not-named at the Phase B register-event boundary.

**OBSERVATION 10: Theme tag provenance is unverified in this cycle (eligible-not-named).**

The `theme` column derives Stratum A vs B per Phase 5.1 §4.2-§4.3. Whether themes were assigned by AI-proposer at hypothesis generation OR post-hoc by reviewers is not verified in this cycle. Theme-level patterns (Codex A.2 C3) are exploratory, not strong family-boundary evidence. This caveat binds any theme-based framing in OBSERVATIONS 4 + 7.

---

## §7 Phase B Decision Surface (Structure-Only Observations, NO Directional Claims)

**Rewritten per V1→V2 Codex F1 BLOCKING + Advisor F2 SUBSTANTIVE adjudication** to remove directional/prescriptive language and conform to anti-pre-naming binding per Phase 5.1 §7.1 + Phase 5.2 §6.4 precedent.

Phase B successor paths inherit from Phase 5.1 §7.1 + Phase 5.2 §6.4. A.1+A.2 findings (per §6 OBSERVATIONS) restructure the decision surface **without pre-naming which path Charlie fires at the Phase B register-event**. The following §7 observations document where A.1+A.2 findings intersect existing Phase B option structures; no directional claim is made about whether they favor or disfavor any specific path.

**§7.1 Intersection with Phase 5.2 §6.4 Branch.A/B/C/D venue commitment:**

OBSERVATION 2 (robust-8 in Stratum A under §3.4 definition) intersects the Branch.A spot framing: the existence of 8 candidates with Sharpe > 0.5 at all 4 tested costs is data that informs — without pre-naming the resolution of — the Branch.A viability question. Phase 5.2 §6.4 Branch.A described "fee-schedule-anchored at 10 bps spot taker per §3.1 plus heuristic slippage component" as the cost basis; A.1 §4 shows this stratum-binomial-pass cost basis (15 bps) corresponds to 8/22 substantively-positive candidates. Whether this is "sufficient" for Branch.A commitment is eligible-not-named for the Phase B register-event.

OBSERVATION 4 (calendar-pattern concentration of robust-8) intersects ALL of Branch.A/B/C/D: the structural concern about curve-fit on weekly cycle patterns is **orthogonal** to the venue commitment question — it does not favor or disfavor any specific Branch.X resolution; it applies to all venue commitments that would deploy these specific strategies.

OBSERVATIONS 6 + 8 + 9 (window-length uncertainty + opacity + in-sample OOS rank gap) intersect ALL of Branch.A/B/C/D: these are prerequisite-class observations that apply regardless of venue resolution.

**§7.2 Intersection with Phase 5.1 §7.1 successor paths:**

- **Path 1 (Phase 5.1 §7.1 paper trading Stratum A subset at 7bps W4-scoped):** A.1's per-candidate decomposition surfaces a distinction between "22-candidate Stratum A under binomial-pass" and "8-candidate robust subset under §3.4 definition." Whether Path 1 targets the 22-candidate or 8-candidate set is eligible-not-named for the Phase B register-event. Both targeting choices have specific methodological consequences (the 22-candidate target inherits the Phase 4 pre-registered scope; the 8-candidate target requires selection-inflation adjustment per OBSERVATION 5).
- **Path 2 (Phase 5.1 §7.1 extended real-cost-discovery):** A.1+A.2 findings provide additional cost-sensitivity decomposition that was not available at Phase 5.1 SEAL. Whether the additional decomposition reduces, increases, or leaves unchanged the marginal value of Path 2 is eligible-not-named for the Phase B register-event.
- **Path 3 (Phase 5.1 §7.1 Stratum B strategic reconsideration):** A.2's per-candidate breakdown + OBSERVATION 7 (continuation-vs-reversal naming hypothesis) provide additional substance not available at Phase 5.1 SEAL. Whether Path 3 is entered, deferred, or scoped differently is eligible-not-named.

**§7.3 Potential new structural option not in Phase 5.1 §7.1 or Phase 5.2 §6.4:**

- **Path 1' (paper trading on 11-candidate cross-stratum robust subset):** a hypothetical refinement of Path 1 targeting the union of Stratum A robust-8 + Stratum B robust-3. Per OBSERVATION 5 and Codex A.2 C5, this would require either a selection-inflation adjustment OR a separate register-event with predeclared rules to constitute a new evaluation cohort (Stratum C). Whether Path 1' is considered, modified, or rejected as a Phase B option is eligible-not-named.

**§7.4 Phase B decision surface inventory (axes, NOT recommendations):**

A.1+A.2 findings expose at least four decision axes potentially relevant at the Phase B register-event:
1. Venue commitment axis (Phase 5.2 §6.4 Branch.A/B/C/D)
2. Candidate-subset axis (22-candidate Stratum A OR 8-candidate robust subset OR 11-candidate cross-stratum OR neither)
3. Promotion-class axis (Phase 5.1 §7.1 Path 1/2/3 OR variants OR pause OR other)
4. Prerequisite axis (OBSERVATIONS 6/8/9 — window date verification + in-sample OOS rank correlation + DSL inspection per OBSERVATION 7 — potentially as gating sub-register-events)

The inventory is presented as available decision surfaces; no claim is made about which axes are load-bearing, which fire first, or which resolutions are favored. All sequencing and resolution decisions are eligible-not-named for Charlie register-event boundaries at Phase B entry.

---

## §8 Reserved Decisions (Anti-Pre-Emption)

Per CLAUDE.md §10 sub-§§ anti-pre-emption invariant — no decision pre-named in this cycle. Reserved for separate Charlie register-event boundary:

1. Phase B venue commitment (Branch.A spot / Branch.B futures / Branch.C both-or-defer / Branch.D alternative; deferred from Phase 5.2 §6.4)
2. Phase B successor path among P1/P1'/P2/P3/P4/P5/P6 (informed by §7 but not pre-named)
3. Whether to formally codify "3-vote-thin" binomial-pass fragility as sealed-corpus annotation on Phase 5.1 (per OBSERVATION 1)
4. Whether to elevate the 11-candidate robust subset (8+3) as a separate evaluation track via new register with predeclared rules (per OBSERVATION 5 + Codex A.2 C5)
5. Whether to fire OBSERVATION 9 (in-sample/OOS rank correlation analysis) as gating prerequisite for any Phase B promotion
6. Whether to fire OBSERVATION 7 (DSL inspection of volume_divergence continuation-vs-reversal hypothesis + `volume_divergence_momentum_174` structural inversion check) as a separate analytical cycle
7. Whether to resolve OBSERVATION 8 (forward-window exact dates) before or alongside Phase B register-event
8. Whether to resolve OBSERVATION 10 (theme provenance verification) before any theme-based Phase B framing
9. Whether OBSERVATION 4 (monday-pattern concentration / curve-fit concern) constrains, vetoes, or is treated as orthogonal to any Phase B Branch.A promotion of the robust-8 subset
10. Phase A SEAL timing and Phase Marker update (deferred to closeout register-event)
11. Other Charlie-specified reserved decisions

---

## §9 V# Anchor Chain (Phase A)

| V# | State | Description |
|----|-------|-------------|
| V1 | ARCHIVED | DRAFT (pre-V1-DRAFT-reviewer-round). Cadence 2 synthesis output; ADOPT findings from A.1 + A.2 stage-1 reviewer rounds incorporated |
| V2 | ARCHIVED | Post-V1-DRAFT-reviewer-round revised draft. V1→V2 adjudication applied 11 fixes: Codex F1 BLOCKING (§7 rewrite removing directional language) + Codex F2 SUBSTANTIVE (§3.4 always-positive vs robust definitional fix: 10 vs 8) + Codex F3 SUBSTANTIVE (§4.2 Stratum B >0.5 count corrected from 3 to 7) + Codex F4 SUBSTANTIVE (§6 OBS 6 trade-count range corrected from 5-30 to 1-26 + flagged 1-2-trade outliers) + Codex F5 SUBSTANTIVE (§7.1 unsourced "~3 cycles minimum" removed) + Codex F6 MINOR (§1.1 p-value citation precision) + Advisor F1 SUBSTANTIVE (OBS 5 Bonferroni clarification with both framings documented) + Advisor F2 SUBSTANTIVE (same as Codex F1 anti-pre-naming) + Advisor F3 MINOR + Advisor F4 MINOR + Advisor NF1 MINOR (§2 single-window caveat). |
| V3 | ARCHIVED | Post-PFR-rule-Y-re-review revised draft. PFR fired per rule-Y trigger: BLOCKING fix region + new content introduced in V2 + closeout-class artifact. V2→V3 adjudication applied 5 PFR fixes: Codex PFR NF1 SUBSTANTIVE (§7 "should X" → Phase-5.2-precedent "Whether X" pattern at 4 sentence locations) + Codex PFR §6/§7 contradiction SUBSTANTIVE (§6 OBS 2/4/7/9 residual directional language neutralized) + Codex PFR §9 count fix (V2 adjudication actually applied 11 fixes, not 9 as initially stated) + Codex PFR NF2 MINOR (§10 external literature names removed entirely; OBSERVATION 4 grounding now purely in-repo) + Advisor PFR F1 SUBSTANTIVE (§6 OBS 5 Bonferroni framing made symmetric — both framings presented without ranking labels). Advisor PFR F2 MINOR (§7 "consistent with" phrasing borderline directional) DEFERRED with reviewer's self-acknowledged over-engineering risk. |
| **V4** | **SEAL** | **Canonical sealed artifact** (Cadence 2 deliverable seal + closeout register-event boundary; SEAL-only authorization per Charlie register 2026-05-18 "SEAL fire"; venue commitment + Phase B path decisions are SEPARATE future Charlie register-events; not bundled into this SEAL). |

V# anchor chain for Phase A follows Phase 5.2 precedent structure (V1 DRAFT → V2 post-reviewer → V3 post-PFR → V4 SEAL).

---

## §10 References

**Sealed project artifacts (read-only at this cycle):**
- `data/phase2c_evaluation_gate/phase4_forward_2026_{07,13,15,17}bps_v1/holdout_results.csv` (Phase 2C sealed cost-run artifacts)
- `docs/phase5/PHASE5_1_COST_MODEL_INVESTIGATION_NOTE.md` (Phase 5.1 SEAL; §3.2 D-classification framework, §5.3-§5.7 stratum count sequences + binomial p-values, §6.1 D-I/D-II classification, §7.1 successor paths)
- `docs/phase5/PHASE5_2_VENUE_RECONCILIATION_NOTE.md` (Phase 5.2 SEAL; §2 venue-mismatch finding, §6.4 Branch.A/B/C/D structures)
- `docs/phase4/PHASE4_PLAN.md` §1.5 (Phase 4 binomial-stratum success criterion; pre-registered thresholds)
- `config/execution.yaml` (canonical cost model; futures-labeled 7 bps)
- `CLAUDE.md` Phase Marker + §10 sub-§§ codified discipline
- `docs/discipline/METHODOLOGY_NOTES.md` (§1 empirical verification, §3 regime-aware calibration, §7 asymmetric confidence reporting)

**Analysis artifact (this cycle, not sealed):**
- `/tmp/phase_a_cadence1_analysis.py` (deterministic, pure Python stdlib, reproducible from CSVs)

**Cross-reviewer adjudication corpus (this cycle):**
- A.1 reviewer round: Advisor F1-F6 + Codex 6-question diagnostic (responses persisted to subagent tool-result archive)
- A.2 reviewer round: Advisor F1-F7 + Codex C1-C6 (responses persisted to subagent tool-result archive)
- ADOPT/PUSHBACK/DEFER per-fix adjudication recorded in conversation transcript (this cycle)

**External literature posture (removed per V2→V3 Codex PFR NF2 adjudication):**
- No external literature citations are invoked in this note as project-internal support. OBSERVATION 4's structural concern (curve-fit suspect on weekly cycle patterns) rests **entirely on the in-repo data pattern** (8 of 8 robust Stratum A candidates being calendar_effect themed, with Bitcoin's 24/7 market structure providing no exchange-weekend-close justification). The earlier V2 enumeration of external authors has been removed to prevent partial-citation hallucination risk per project's Option II citation verification discipline.

**End of V4 SEAL.** Phase A clarification cycle SEALED at this register-event boundary (Charlie register 2026-05-18 "SEAL fire"). Cycle resolved Charlie's statistical-significance question on Phase 5.1's 17/22 binomial pass as **technically significant by pre-registration (p≈0.0085) but methodologically thin** (3-vote thin; below-cost-threshold near-zero positives drive the pass). Below the binomial summary: 8 Stratum A robust candidates (Sharpe > 0.5 at all 4 tested costs) + 3 Stratum B robust candidates (analogous criterion despite stratum-level binomial failure) = 11-candidate cross-stratum robust subset surfaced for eligible-not-named Phase B framing. 10 §6 OBSERVATIONS named anti-pre-naming + eligible-not-named for separate Charlie register-event boundaries. §7 Phase B decision surface inventory enumerated without directional claims (4 axes: venue commitment / candidate-subset / promotion-class / prerequisite). 11 §8 reserved decisions. **NO git tag at SEAL** per Bucket-1 investigation note ≠ arc-level closeout per CLAUDE.md Tag policy + Phase 5.1 + Phase 5.2 precedent.

**Reviewer routing empirical observations from this cycle**: 4 reviewer rounds fired (A.1 dispatch + A.2 dispatch + V1 DRAFT dispatch + PFR rule-Y) with 2-leg subagent default each (Advisor + Codex parallel). Zero Codex stalls across 8 dispatches. Zero verified advisor hallucinations across 8 dispatches (citation verification discipline operationally enforced per Option II codification). Cross-model diversity routine continues to validate per [[feedback_reviewer_routing_subagent_default.md]] B2 pilot sample. Codex caught critical V1 BLOCKING (§7 directional language) + V2→V3 carry-forward defects (§6 directional language) that Advisor did not surface; Advisor caught critical V1 SUBSTANTIVE (selection-inflation guard + Bonferroni framing + multi-confound isolation) that Codex did not surface. Bilateral cross-model diversity validated again on this 4-round Phase A pilot extension.

---

## §11 Errata (appended post-SEAL per sealed-content invariance discipline)

**Errata E1 (2026-05-18; R1.1 register-event within Phase B Pre-Sequence Roadmap V3 path-3 parallel authorization):**

§6 OBSERVATION 8 estimate "**approximately Jan-Apr 2026 ≈ 2900 hourly bars**" is superseded by R1.1 verification of `data/phase2c_evaluation_gate/phase4_forward_2026_07bps_v1/holdout_summary.json` `forward_window_metadata` block (sha256-locked execution_config + parquet_data):

| Field | Verified value |
|---|---|
| Forward window start (UTC) | **2026-01-01T00:00:00Z** |
| Forward window end (UTC) | **2026-04-16T07:00:00Z** |
| Forward bar count | **2528** hourly bars (NOT ~2900; Phase A estimate was high by ~14.7%) |
| Parquet data sha256 | `db4ce1d2a2e5e7b556975837260f7aaa29ee4fd5ddc603690d1bc57912aa7035` |

**Errata scope**: estimate-correction only. The corrected 2528-bar value tightens Phase A per-strategy power claims slightly (e.g., max possible Monday triggers ≈ 15 not ~17; ~4 months instead of "Jan-Apr" implied length). All Phase A factual findings (Stratum count sequences, robust subset definitions, Sharpe distributions, cost-slope decomposition) remain unchanged because they were computed on the actual 2528-bar `holdout_results.csv` data, not on the estimate. The estimate appeared in interpretive prose only.

**Canonical reference for the corrected value**: [`docs/phase5/R1_2_IS_OOS_RANK_CORRELATION_NOTE.md`](R1_2_IS_OOS_RANK_CORRELATION_NOTE.md) §7 OBSERVATION 8 + §3.1 IS-OOS data source metadata (R1.2 V4 SEAL'd at commit `de158e8` + Phase Marker advance `5b7fd7e`).

**Sealed-content invariance preserved**: §6 OBSERVATION 8 main text remains as originally sealed; this errata note is the canonical correction reference. Future readers encountering "~2900 hourly bars" in §6 OBS 8 should consult this errata note + the canonical R1.2 SEAL reference.

---

**Errata E2 (2026-05-20; R2.3 register-event within Phase B Pre-Sequence Roadmap V3 Tier 2 substantive cycle pair):**

§6 OBSERVATION 10 theme tag provenance binary question ("AI-proposer at hypothesis generation OR post-hoc by reviewers") is RESOLVED via R2.3 V_SEAL substantive cycle. The verified mechanism is a three-layer characterization (NOT binary):

- **Layer 1 (timing):** themes assigned at GENERATION TIME at BatchContext construction, BEFORE Proposer LLM call — closer to OBS 10's option (a) than (b)
- **Layer 2 (authorship):** programmatic ROTATION LOGIC in `agents/proposer/stage2c_batch.py:213` (formula `THEMES[(k - 1) % THEME_CYCLE_LEN]`) — NOT Proposer-LLM-chosen
- **Layer 3 (constraint):** Proposer LLM receives theme as prompt directive (`agents/proposer/prompt_builder.py:227`); LLM constrained to assigned theme, NOT choosing

**OBS 10 caveat scope refinement:** theme-level patterns in §6 OBSERVATIONS 4 + 7 are legitimate family-boundary evidence for the PRE-REGISTERED family labels (Layer 1+2) but NOT for content-aware family clustering (Layer 3 + R2.3 §8.2 telemetry caveat: theme tags are prompt-rotation provenance labels, not validated content-aware classifications). Calendar-concentration in cohort_a (22/39) reflects SELECTION pattern at AND-gate-passing terminus, NOT generation-time family-boundary signal.

**Canonical reference for resolution**: [`docs/phase5/R2_3_THEME_TAG_PROVENANCE_NOTE.md`](R2_3_THEME_TAG_PROVENANCE_NOTE.md) §2.2 three-layer reshape + §3-§5 4-dimensional audit + §6 dim (d) INDETERMINATE-DSL-UNAVAILABLE per Sub-1 η1-C + §7 §34 first-empirical-test codification + §8 surfaced observations (R2.3 V_SEAL'd at register-event boundary 2026-05-20).

**Sealed-content invariance preserved**: §6 OBSERVATION 10 main text remains as originally sealed; this errata note + R2.3 V_SEAL canonical artifact provide the resolution reference. Future readers encountering OBS 10 "unverified" + "exploratory, not strong family-boundary evidence" language should consult this errata + R2.3 V_SEAL.

**Tier 2 SEAL completion**: R2.3 V_SEAL completes Tier 2 SEAL per R2.0 SD-B B2 lock (R2.1 ✓ + R2.3 ✓). R5.1 cycle entry now unlocked at separate Charlie register-event boundary per anti-pre-emption.

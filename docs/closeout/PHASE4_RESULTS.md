# PHASE 4 — Forward Persistence Test Results

**Status:** SEALED · Date: 2026-05-09T13:17:40Z · Tag: phase4-forward-test-v1 pending Task 6

**Cycle scope:** forward persistence test of PHASE2C_15 cohort_a candidates over 2026-01-01 forward window per PHASE4_PLAN §1.1-§1.5. Re-derives per-stratum forward-Sharpe positivity counts from the 4 cost-run artifacts (07/13/15/17 bps) and applies the pre-registered §1.5 binomial test at 15bps to the success-criterion register.

## §1 Phase 4 result

Per PHASE4_PLAN §1.5 interpretation guard, applied mechanically to the observed disjunction at 15bps:

> no forward persistence detected at PLAN §1.5 success criterion.

## §2 Success-criterion register at 15bps (PHASE4_PLAN §1.5 basis)

- Stratum A (calendar_effect): 11/22 positive forward Sharpe at 15bps; threshold ≥17/22; binomial p=0.5841 (one-sided vs p₀=0.5); **FAIL TO REJECT H_0**.
- Stratum B (non-calendar): 7/17 positive forward Sharpe at 15bps; threshold ≥13/17; binomial p=0.8338 (one-sided vs p₀=0.5); **FAIL TO REJECT H_0**.
- Bonferroni-adjusted α=0.025 per stratum; family-wise α≈0.033 (conservative under nominal 0.05 due to binomial discreteness).

## §3 Per-cost dual-report (descriptive supplement per PHASE4_PLAN §1.4)

Per PHASE4_PLAN §1.5, the success criterion is evaluated at 15bps only. The 7/13/17bps registers are descriptive supplements: 7bps for PHASE2C_15-comparability (research-time cost basis), 13/17bps for sensitivity bands ±2bps around the 15bps base. These rows do NOT enter the §1 success/failure determination.

| Cost | Stratum A positive | Stratum B positive | Note |
|---|---|---|---|
| 07bps | 17/22 | 9/17 | descriptive |
| 13bps | 12/22 | 8/17 | descriptive |
| 15bps | 11/22 | 7/17 | **success-criterion basis** |
| 17bps | 10/22 | 5/17 | descriptive |

The 7bps threshold hit (Stratum A 17/22 at the research-time cost basis) is descriptive only and cannot be used to satisfy, weaken, rescue, or reinterpret the Phase 4 success criterion, which is evaluated only at the realistic 15bps basis per PLAN §1.4 + §1.5.

## §4 Locked anchors

- Forward window: `2026-01-01T00:00:00Z` → `2026-04-16T07:00:00Z`
- Forward bar count: 2528
- Parquet sha256 (cross-artifact-invariant across all 4 fires): `db4ce1d2a2e5e7b556975837260f7aaa29ee4fd5ddc603690d1bc57912aa7035`
- Engine lineage: `eb1c87f` (`wf-corrected-v1`)
- HEAD at closeout authoring: `d0b8101df61531ff3e055727e492295a1bb0591b`
- Cohort_a stratification (sealed at PHASE4_PLAN §1.3 register; reference CSV at `data/phase4_scoping/cohort_a_candidate_reference.csv` committed at `11b39f2`): A=22 (calendar_effect), B=17 (non-calendar).
- Per-stratum-cost-fire artifacts share identical parquet sha256, identical forward window, identical bar count; only `execution_config_*` differs across fires (verified at production fire register-event boundary cross-artifact consistency check).
- Stratum denominators locked at PLAN §1.3 (n_A=22, n_B=17); candidates with non-finite, missing, zero, or negative forward Sharpe are classified as non-positive and remain in the denominator (the locked n is total cohort_a members in stratum, not total candidates with usable Sharpe data).

## §5 Run artifacts

- 07bps: [data/phase2c_evaluation_gate/phase4_forward_2026_07bps_v1/](../../data/phase2c_evaluation_gate/phase4_forward_2026_07bps_v1/)
- 13bps: [data/phase2c_evaluation_gate/phase4_forward_2026_13bps_v1/](../../data/phase2c_evaluation_gate/phase4_forward_2026_13bps_v1/)
- 15bps: [data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1/](../../data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1/)
- 17bps: [data/phase2c_evaluation_gate/phase4_forward_2026_17bps_v1/](../../data/phase2c_evaluation_gate/phase4_forward_2026_17bps_v1/)

Each contains `holdout_summary.json` (aggregate + lineage + forward_window_metadata + execution_config sha256) and `holdout_results.csv` (39 rows; one per cohort_a candidate). The 4 fires were verified end-to-end via [scripts/verify_phase4_smoke.py](../../scripts/verify_phase4_smoke.py) at fire register; 9/9 assertions PASS at every fire.

## §6 Carry-forwards (forward-only log; finalize at successor methodology consolidation cycle)

- §31 P1 (convergence-reinforces-convergent-errors pattern): 5 instances cumulative across PHASE4 implementation arc. #1: ≥17/22 PLAN threshold convergence; #2: `holdout_sharpe` field-name convergence; #3: `end:null` engine consumer crash (structural-assumption); #4: `verify_phase4_smoke.py committed in 7dd3b7a` overclaim (commit-contents); #5: `--universe audit` returns 39 vs actually 993 (structural-assumption ×2). Sub-class accumulation through #5: 1 numerical / 1 identifier / 2 structural-assumption / 1 commit-contents. Task 7 reassessment candidate (NOT pre-committed at this register per anti-pre-naming discipline; reassessment at successor cycle adjudication boundary). Logged forward-only at carry-forward register.
- Six-dimension machine-residency discipline empirically validated at MacBook ↔ Mac Mini transition: (1) `raw_payloads/` directory state, (2) HTTPS credential availability, (3) test fixture artifact state, (4) Python environment composition, (5) parquet sha256 anchor state, (6) geo-restriction fingerprint. Forward arc planning should pre-check all six at session entry rather than mid-sequence-resolve.
- Pre-registered §1.5 wording authored at PLAN drafting cycle held under closeout pressure. Trim-direction discipline at PLAN drafting was substantively expensive at the time but produced clean closeout wording at the register-event boundary where it bound.

## §7 Anti-pre-naming preserved

Phase 5+ trajectory NOT pre-committed at this register. Successor scoping is its own register-event boundary per anti-pre-naming. Task 7 §32 codification reassessment: default = NO codification per asymmetric framing; reassess at fresh-cycle boundary post-this-SEAL.

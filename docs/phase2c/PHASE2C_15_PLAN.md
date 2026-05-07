# PHASE2C_15 sub-spec: parameter lock

**Status:** SEALED at sub-spec drafting cycle SEAL register-event boundary.

**Cycle scope:** parameter specification within PHASE2C_14 sub-spec §3.1-§3.4 framework lock. Selects coordinates inside the sealed semantic framework; does not redefine framework. Z4 minimal-governance-surface discipline binding.

## §1 Parameter values

### §1.1 Stopping rule + sample structure (Q-S119 ratified)

- Stopping rule: **Fixed N pre-committed**. No interim analysis.
- K = **5** batches; N_per_batch = **200**; total nominal N = **1000**.
- Estimated cost: ~$10-15 within May 2026 monthly cap (per-batch ~$2-3 at PHASE2C_12 baseline rate).

Justification: K=5 provides Role 2 within-batch homogeneity adequate df (=4 on K×2 table); N_per_batch=200 preserves PHASE2C_12 baseline scale comparability.

### §1.2 Theme rotation (Q-S120 ratified)

- Inclusion: 5 themes — `volume_divergence`, `volatility_regime`, `calendar_effect`, `momentum`, `mean_reversion`.
- Exclusion: `multi_factor_combination` (structured-combination encoding surface deferred per scoping decision).
- Weighting: uniform 1/5 → 200 candidates per theme across K=5 batches.

Justification: register-class match to PHASE2C_12 5-theme rotation; preserves `volatility_regime` per PHASE2C_14 sub-spec §3.3 M1-vs-M2 multi-batch evidence requirement.

### §1.3 Role 1 success criterion (Q-S121 ratified)

Per PHASE2C_14 sub-spec §3.2 verbatim binding `observed_rate > 2.07%`:

- valid_N = generated candidates with valid terminal evaluation outcome
- success_count = valid candidates passing AND-gate
- observed_rate = success_count / valid_N
- **Success iff observed_rate > 0.0207** (strict inequality; equality at 0.0207 does NOT pass)

Derived integer-threshold compact check at fire time: success iff success_count > floor(0.0207 × valid_N).

Sole pre-registered success criterion. PHASE2C_15's own Wilson CI is NOT the success criterion.

### §1.4 Role 1 auxiliary descriptive (Q-S121 ratified)

- Test: two-sided Fisher exact at α=0.05.
- Comparison: PHASE2C_15 (success_count, valid_N) vs PHASE2C_12 baseline (8, 197).
- Status: descriptive supplement only; NOT pre-committed as success criterion.

### §1.5 Role 2 within-batch homogeneity (Q-S121 ratified)

- Test: Fisher-Freeman-Halton (FFH) exact omnibus on K×2 contingency table (5 batches × 2 outcomes).
- Implementation: exact FFH if computationally tractable; Monte Carlo FFH with B=10000 simulations as fallback at implementation arc.
- Pairwise Fisher exact (10 pairs at K=5) with Bonferroni: supplementary descriptive only; NOT omnibus replacement.

### §1.6 Test-family structure

Role 1 success criterion (§1.3) and Role 2 omnibus homogeneity (§1.5) are **independent inferential roles at α=0.05 each**. Auxiliary tests (§1.4 Fisher exact vs baseline; §1.5 pairwise Fisher) are descriptive supplements, NOT formal hypothesis tests. No multi-test correction across Role 1 + Role 2.

## §2 Cycle-scope binding

Framework class at PHASE2C_14 sub-spec §3.1-§3.4 continues to bind through PHASE2C_15 fire register-event boundary per t2-t5 immutability + PHASE2C_15 entry scoping decision §6 binding. Sealed corpus invariance preserved per scoping decision §6.4 (METHODOLOGY_NOTES §27/§28/§29 + PHASE2C_13 sub-spec §2.7/§4.3 + §20.6 §A2 instances #26-#31 not modified).

## §3 Anchors

- HEAD at sub-spec WORKING DRAFT register: `a78905d`
- PHASE2C_15 entry scoping decision SEAL: `14183e6` ([`PHASE2C_15_SCOPING_DECISION.md`](PHASE2C_15_SCOPING_DECISION.md), 31 lines)
- PHASE2C_14 sub-spec SEAL: `18fa2a1` ([`PHASE2C_14_PLAN.md`](PHASE2C_14_PLAN.md), 352 lines)
- METHODOLOGY_NOTES.md: 6785 lines invariant per PHASE2C_14 H-1 (d) carry-forward

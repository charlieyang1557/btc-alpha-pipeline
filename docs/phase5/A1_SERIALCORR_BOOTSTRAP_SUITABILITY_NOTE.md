# A-1 — SD-E-γ Stationary-Bootstrap Suitability Diagnostic (Path 2) — Closeout NOTE

- **Date:** 2026-05-30 (UTC)
- **Cycle:** A-1 (first of the Charlie-registered `A-1 → A-2` methodology-successor sequence; **A-2 now deferred** — see §6)
- **Branch:** `a1-stationary-bootstrap-overlay`
- **Spec:** [`docs/superpowers/specs/2026-05-30-a1-sd-e-gamma-stationary-bootstrap-overlay-design.md`](../superpowers/specs/2026-05-30-a1-sd-e-gamma-stationary-bootstrap-overlay-design.md) (v2 + §12 Path-2 Erratum E1)
- **Plan:** [`docs/superpowers/plans/2026-05-30-a1-sd-e-gamma-stationary-bootstrap-overlay.md`](../superpowers/plans/2026-05-30-a1-sd-e-gamma-stationary-bootstrap-overlay.md) (PFR-patched)

## §1. Outcome (one line)
A-1 attempted to *measure* the disclosed R6.1 §6.1 within-candidate serial-correlation gap via a stationary-bootstrap (Politis–Romano 1994) SE of the per-bar Sharpe. **The measurement is not feasible on this cohort** — the `phase4_forward_2026_15bps_v1` strategies are low-trade-frequency / sparse-return, so the per-bar-Sharpe bootstrap is partly ill-posed: its **effective sample is the nonzero-bar count (54–758), not the ~2500 bars**, with long-block resample degeneracy as the acute symptom at the sparsest candidates. A-1 delivers the **reusable tested primitive** (standing capability for future *denser* cohorts) + a **verdict-invariance attestation** + an **evidence-grounded suitability diagnostic** demonstrating the unsuitability. **The Tier 6 verdict (0/18) is unaffected** (SE-independent).

## §2. What was built
- **The primitive (standing capability):** `backtest/tier6_bootstrap.py` — `stationary_bootstrap_indices`, vectorized `bootstrap_sharpe_se`, `bootstrap_skip_fraction` (degeneracy probe), `mertens_se`, entropy-keyed `substream_rng`. TDD; 32 tests.
- **Verdict-invariance attestation:** per-candidate `excess = SR̂ − sr_star(N*, T, "B")` (moment-independent; no bootstrap). All 18 < 0 → 0/18, SE-independent.
- **Suitability diagnostic (the evidence):** per-candidate `nonzero_count`, `zero_fraction`, and the bootstrap `skip_fraction` per block length L ∈ {1,6,12,24,48,96}.
- `tier6_dsr.py` + the sealed `tier6_dsr_v1/` are **byte-untouched** (import-only; sha256 immutability gate + numerical tie-back enforced in tests).
- **Known limitation (standing primitive; SEAL-eve Codex):** the diagnostic assumes each candidate has ≥1 nonzero return (finite per-bar Sharpe). A hypothetical all-zero-return candidate would yield a non-finite `excess` (not guarded — eligible future hardening). Cannot occur on this cohort (every candidate has nonzero bars; min nonzero_count 27), and future denser cohorts make it even less likely.

## §3. Empirical findings (5000 replicates, seed 20260529)
- **Verdict invariant:** `all_excess_negative = True`, `max_excess = −0.004436` (`ema_crossover_momentum_acceleration`, R2.1-indeterminate). 0/18 — no SE estimate (bootstrap, i.i.d., or otherwise) can flip a negative numerator to a pass.
- **Sparsity (full 39-cohort, matching the attestation):** `zero_fraction` 0.635 / 0.909 / 0.989 (min/median/max); `nonzero_count` 27 / 227 / 913. The **authoritative-18** effective sample is `nonzero_count` **54–758** — far below T ≈ 2358–2503, the binding reason the per-bar-Sharpe bootstrap is ill-posed here.
- **Degeneracy** (fraction of all-zero/zero-variance resamples): authoritative-18 `skip_L96` max **0.62%** (mild — but the *effective-sample* deficit, not degeneracy, is the binding problem); companion-21 `skip_L96` up to **26.4%** (`monday_dip_reversal`, zero_fraction 0.989).
- **B2-verified (advisor + Codex):** dropping degenerate replicates is anti-conservative (negligible at low skip, ~+12% at 27%); the `serialcorr_increment` decomposition is **not** cleanly sparsity-robust (similar-sparsity candidates give opposite increment directions). Hence no inflation-ratio measurement is reported.

## §4. Conclusion
The §6.1 within-candidate serial-correlation gap is **not empirically quantifiable on this sparse cohort** via a per-bar-Sharpe stationary bootstrap: the effective sample is the nonzero-bar count (54–758), not the bar count, so the bootstrap SE is dominated by sampling noise and (at long blocks) outright degeneracy. The diagnostic *demonstrates* this rather than asserting it. The primitive stands for any future cohort with denser returns. The §6.1 gap remains empirically-unquantified-on-this-cohort and is handed forward. **0/18 stands, untouched.**

## §5. Process trail (B2 2-leg throughout)
- Spec: advisor + Codex (16 findings adopted → v2).
- Plan (PFR): advisor + Codex (13 findings patched, incl. Codex CRITICAL degenerate-path restructure + the leading-NaN catch).
- Sparse-returns escalation: advisor + Codex (the spec §3.2 "vanishingly rare" premise was empirically false; Codex refined the advisor's thresholds + refuted the `serialcorr_increment`-as-robust claim). **Charlie registered Path 2 (scope-down).**
- Path-2 implementation: implementer + 2-stage review (spec-compliance + code-quality; 1 spec deviation + 3 IMPORTANT + minors adjudicated and fixed).
- (Final whole-module B2 + Rule-2 SEAL-eve recorded at the SEAL boundary.)

## §6. Forward linkage (NOT pre-emptive — separate Charlie register)
The sparsity finding is a symptom of the project's binding constraint identified this cycle (B2-convergent): **the alpha source, not data or methodology** — the Tier 6 0/18 + low-trade-frequency strategies both say the mined DSL strategies lack edge surviving realistic 15 bps costs (best candidate 1.89 z-units short; funnel **993→39→18** (PHASE2C_15 ~5-batch universe → cohort_a AND-gate → Tier-6 Monday/R2.1 exclusion; the sealed eval NOTE frames it 198→39→18) makes N\*=18 lenient, not strict). **A-2 (RW/WY) and further SD-E-γ measurement are deferred** — rigor on a verdict-invariant negative, load-bearing only for a future near-threshold winner. **Registered next direction:** a bounded one-cycle alpha-source rethink (funding/OI/basis + mechanism-first mining) as a falsification test (its own register/scoping cycle). See memory `project_alpha_source_binding_constraint`.

## §7. Artifacts
- Module + tests: `backtest/tier6_bootstrap.py`, `tests/test_tier6_bootstrap.py` (32 tests).
- Results: `data/phase2c_evaluation_gate/tier6_serialcorr_robustness_v1/` — `suitability_diagnostic.csv` (18), `suitability_companion.csv` (21), `suitability_attestation.json`. Banner: "diagnostic; NON-AUTHORITATIVE; measurement inconclusive on sparse cohort; verdict invariant (0/18, SE-independent)."
- Commit chain (branch `a1-stationary-bootstrap-overlay`): foundation `ecae241` (spec + plan); Chunk-1 `ed94374` (primitives); Path-2 impl + artifacts + this NOTE (SEAL boundary).

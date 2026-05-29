# Tier 6 DSR Evaluation Application — Design Spec

**Date:** 2026-05-29
**Cycle:** post-V_SEAL Tier 6 evaluation application (R6.1 Path α invariant; the eligible-not-named successor unblocked by the B-C-narrow data-recovery cycle SEAL `e208193`).
**Status:** DESIGN — awaiting Charlie review (User Review Gate) before transition to `writing-plans`.
**Charlie register (cycle entry):** "path 1 authorized" 2026-05-29 + D1/D2/N1–N6 lock register 2026-05-29.

> This spec applies the **already-locked** R6.1 Tier 6 promotion-class methodology (`docs/phase5/R6_1_TIER_6_PROMOTION_CLASS_NOTE.md` §1–§11 + §12 Errata) to the **recovered** `phase4_forward_2026_15bps_v1` cohort. The methodology is NOT re-litigated. Only the two §12-Errata-deferred application decisions (D1, D2) + the application-layer specification points (N1–N6) surfaced by the B2 review are in scope.

---

## §1 Purpose, driver, scope

**Driver.** R6.1 V_SEAL locked the Tier 6 promotion-class methodology but fired methodology-only (Path α); §11.4 explicitly deferred the *computational application*. The B-C-narrow cycle then recovered the per-bar return series + γ3/γ4 + registry linkage that were the binding precondition. This cycle performs the deferred computation: per-candidate Deflated Sharpe Ratio + threshold check + promotion list over the locked cohort.

**In scope.**
1. Compute per-candidate DSR for the locked-18 cohort using the R6.1-locked BLdP closed-form methodology.
2. Apply the D1/D2/N1–N6 decisions locked at this register.
3. Produce the authoritative promotion list + a quarantined non-authoritative companion (the other 21).
4. Robustness disclosure + MC expected-max validation companion.
5. A Tier 6 evaluation NOTE (results + selection-inflation residual-risk disclosure + R6.1 T_obs errata).

**Out of scope (anti-pre-emption; eligible-not-named successors).** SD-E-γ stationary-bootstrap variance overlay; RW/WY framework-family reopening; N\* estimator refinement (MP/Cattell/trace/bootstrap); SD-A-ε Hybrid upgrade; supplementary IS-OOS analytical cycle; R2.2 Monday-pattern mechanism investigation; empirical-ρ̄ N\* refinement (the (a1) lock fixes ρ̄=0/N\*=18); any cohort-scope change; any methodology re-lock; paper-trading deployment; §36 METHODOLOGY_NOTES codification. Each is a separate Charlie register-event.

---

## §2 Locked inputs (recap — NOT decisions here)

Per R6.1 V_SEAL §11.3 + §12 Errata:

| Dim | Lock |
|---|---|
| SD-A-α | BLdP 2014 closed-form analytical DSR |
| N\*-ε / (a1) | **ρ̄ = 0 → N\* = N = 18** (i.i.d. flip; §12.1 E1 + §12.3 E3) |
| SD-B-α | DSR ≥ 0 (canonical haircut-passing) — operational equivalence pinned in §5.3 below |
| SD-C-α | All-18 cohort |
| SD-D-α | α = 0.05 FWER |
| SD-E-α | within-candidate i.i.d. (Mertens 2002 asymptotic Sharpe variance; no bootstrap overlay) |
| SD-F Path 1 | per-bar full-holdout moments |

Core formula (locked, §2.1 + §12.2): `Var(SR) = (1 − γ₃·SR + ((γ₄−1)/4)·SR²)/(T−1)` (Mertens 2002); `PSR(SR*) = Φ( (SR̂ − SR*)·√(T−1) / √(1 − γ₃·SR̂ + ((γ₄−1)/4)·SR̂²) )`.

---

## §3 The two locked application decisions (D1, D2)

### §3.1 D1 — SR\* expected-max form: **(iii) Form B authoritative + Form A conservative companion**

- **Form B (AUTHORITATIVE)** — genuine BLdP-2014 closed-form expected-max (Euler–Mascheroni):
  `SR* = √Var(SR_null) · [ (1−g)·Φ⁻¹(1 − 1/N*) + g·Φ⁻¹(1 − 1/(N*·e)) ]`, g = 0.5772156649…, N\* = 18. Normalized ratio ≈ 1.85.
- **Form A (COMPANION, non-authoritative)** — asymptotic heuristic (CLAUDE.md line 268 "interim screen only"):
  `SR* = √Var(SR_null) · √(2·ln N*)`. Normalized ratio ≈ 2.40.
- **Anti-threshold-shopping binding (advisor + Codex convergent):** Form B is locked as authoritative **before** any per-candidate DSR is computed; Form A is a labeled non-authoritative column; the authoritative designation MUST NOT be revisited after seeing which candidates pass under either form. This binding is restated in the cycle plan + NOTE.

Convergence: advisor (medium) + Codex (high) independently → (iii). Rationale: Form B *is* the SD-A-α locked instrument; Form A is the project's own interim heuristic and cannot be the authoritative capital-adjacent gate without contradicting the lock. Form A is retained for first-fire transparency (the two disagree non-trivially at small N\*).

### §3.2 D2 — Cohort scope: **(ii) locked-18 authoritative + 21 quarantined companion**

**Quarantine conditions (binding):**
1. The companion 21 (= 2 R2.1-excluded + 19 Monday-pattern) are computed at the **same Form B formula** for apples-to-apples comparison.
2. Companion rows MUST NOT affect the authoritative pass/fail set, N\*, ranking, or any promotion narrative.
3. Companion output is physically + labelled separate ("non-authoritative fragility audit; NOT pre-registered for promotion").

Convergence: advisor (medium) + Codex (med-high) → (ii). The 18 are the pre-registered V_SEAL-locked family; the 21 belong in a quarantined audit that makes the selection boundary inspectable.

---

## §4 Cohort membership (verified deterministic derivation)

Derivation: **39 cohort_a − 19 Monday-pattern (name matches `/monday/i`) − 2 R2.1-excluded = 18** (no overlap; verified 2026-05-29 against `data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1/holdout_results.csv`).

- **2 R2.1-excluded:** `35dcfcfbee4cfafc` (volume_divergence_momentum_174), `38a1bb228f103c26` (volatility_compression_breakout_ema_cross). Per R5.1 §188.
- **19 Monday-pattern:** 18 `monday_*`-prefixed + 1 `weekend_vol_compression_monday_breakout_160` — name-substring heuristic (DSL content unavailable).

**Locked-18 composition:** 6 volume_divergence + 6 momentum + 3 calendar_effect + 2 mean_reversion + 1 volatility_regime (matches R6.1 §8.1).

**Disclosure flags carried into the NOTE (from verification + advisor):**
- The 3 retained calendar candidates are `friday_close_weekend_positioning`, `weekday_momentum_friday_fade`, `weekend_volatility_compression_breakout` — day-of-week names that escaped the `monday` substring filter and were NOT subjected to the same Monday curve-fit scrutiny. **Residual risk; disclose.**
- 2 of the 18 carry R2.1 INDETERMINATE-overall flags: `7abff29fc2f117a1` (momentum; likely the highest-Sharpe candidate) + `2433a38b2f9a7211` (volume_divergence). **Disclose alongside their DSR.**

The cohort derivation is implemented as a pure function with a dedicated test (no hardcoded 18-list drift); the hardcoded R2.1-excluded set + the Monday predicate are the only inputs.

---

## §5 DSR computation specification

### §5.1 Per-candidate inputs (N1, N2 — locked)

For each candidate, from its `returns_per_bar.parquet` (the `return` column):
- **T** = count of finite per-bar returns = recovered `T_obs` (~2358–2503). **Total finite bars, NOT active/non-zero bars** (N2 lock). Rationale: the object deflated is the Sharpe of the full strategy return stream (flat bars are real 0-returns); consistent with how the engine computed `T_obs` and how the holdout Sharpe was computed. **Never the sealed "≈6000"** (N1 lock).
- **SR̂** = per-bar Sharpe = mean(r)/std(r) over the full finite series (per-period units, matching T and the moments). Recomputed from the parquet for internal consistency; cross-checked against stored `holdout_sharpe` (note any annualization-factor relationship as a sanity check, not a substitute).
- **γ₃** = skew, **γ₄** = kurtosis — consumed from the engine-stored values, with an **independent recompute-from-parquet verification gate** (ε check). **Kurtosis convention MUST be RAW (γ₄ = 3 for Gaussian), not excess** — the Mertens term `(γ₄−1)/4` requires raw kurtosis. A dedicated test pins the convention (scipy/pandas default to *excess*; the engine's stored convention is verified and the consumer matched to it).

### §5.2 SR\* (expected-max benchmark) + per-candidate variance objects (N3 — pinned)

- **SR\* benchmark**, per candidate i: `SR*_i = √(1/(T_i − 1)) · ER`, where `Var(SR_null) = 1/(T_i−1)` is the Mertens variance **at the null** (SR=0 ⇒ skew/kurt terms vanish; Gaussian null), and `ER` is the expected-max ratio: `ER_B` (Form B, authoritative) or `ER_A` (Form A, companion), N\*=18.
- **Per-candidate PSR/DSR denominator** uses the candidate's **own** Mertens variance with its observed γ₃/γ₄/SR̂ (the full non-normal term).
- These two variance objects are **deliberately different** (null benchmark vs candidate-specific estimator SE) — this is the standard PSR/DSR construction, NOT an inconsistency. The spec + NOTE state both explicitly (resolves the advisor's "mixing" flag by pinning, not by changing).
- **Reconciliation with R6.1 §12.2 line 599** ("Var(SR_null) candidate-specific per Mertens non-normality correction"): the non-normality (γ₃/γ₄) terms carry a factor of SR̂, so at the null (SR=0) they vanish and the Mertens variance reduces to `1/(T−1)`. Thus the SR\* benchmark's `Var(SR_null)` is candidate-specific **only via T_i** (not via the candidate's moments); the γ₃/γ₄ non-normality correction enters only the per-candidate PSR denominator at the candidate's own SR̂≠0. This is the coherent, non-circular reading of §12.2 and is faithful to the lock.

### §5.3 Pass rule (SD-B-α operational equivalence — pinned)

Per R6.1 §3.1 locked disambiguation: **"DSR ≥ 0" ⇔ PSR(SR\*) ≥ 1−α ⇔ deflated-z ≥ z(1−α)**, one-sided, α = 0.05.

Operational implementation:
- `DSR_i = PSR(SR*_i) = Φ( deflated_z_i )`, `deflated_z_i = (SR̂_i − SR*_i)·√(T_i−1) / √(1 − γ₃_i·SR̂_i + ((γ₄_i−1)/4)·SR̂_i²)`.
- **Candidate passes iff `DSR_i ≥ 1−α = 0.95`** (equivalently `deflated_z_i ≥ z(0.95) = 1.6449`).
- No Bonferroni layering on top (§3.1 anti-double-count): α enters once via the 0.95 confidence; N\* enters once via SR\*.
- One-sided throughout (selection-of-maximum is an upper-tail object).

> **Spec-review flag (high priority):** the sealed R6.1 §3.1 labels this "DSR ≥ 0 strict-positive," whose locked operational meaning (line 115) is "PSR ≥ 1−α." The spec implements `PSR(SR*) ≥ 0.95` (NOT `SR̂ ≥ SR*` / `PSR ≥ 0.5`). This is the single most outcome-determining interpretation; it is pinned here and re-verified at the plan reviewer round.

### §5.4 Reported per-candidate fields (authoritative 18 + companion 21)

`hypothesis_hash, name, theme, T, SR_per_bar, gamma3, gamma4, trades, var_null, ER_B, ER_A, SR_star_B, SR_star_A, deflated_z_B, deflated_z_A, DSR_B, DSR_A, pass_B, pass_A, g4_high_flag, provisional_flag, r21_indeterminate_flag` (+ `monday_flag` on the companion).

---

## §6 Robustness, disclosure, validation

### §6.1 N4 — robustness disclosure (locked)
- Report trade-count + γ₃/γ₄ next to every DSR.
- **`g4_high_flag`**: flag candidates whose closed-form asymptotic is shaky (heavy tails over few active bars; e.g. γ₄ above a stated threshold). Their DSR is reported but labelled **low-confidence**.
- **`provisional_flag`**: any pass whose margin is smaller than a plausible serial-correlation variance inflation is labelled **PROVISIONAL pending SD-E-γ** (the known anti-conservative i.i.d. limitation). Threshold for "small margin" stated in the plan.

### §6.2 N6 — MC expected-max validation companion (locked, non-authoritative)
Simulate max-of-18 standard-Gaussian Sharpe estimates at the cohort's T to (a) bound Form A/B closed-form approximation error at the moderate N\*=18 regime, and (b) sanity-check the Gaussian-extreme-value assumption (a heavy-tailed-null variant may also be simulated). Output `tier6_mc_validation.json` with the empirical expected-max ratio + Form A/B deviations. Explicitly non-authoritative (does not change pass/fail).

### §6.3 N5 — selection-inflation residual-risk disclosure (locked, must-disclose)
The NOTE states plainly: **DSR-at-N\*=18 controls FWER over the sealed All-18 family only; it is necessary-not-sufficient and does NOT correct the upstream 198→39→18 winnowing.** Passing Tier 6 ≠ surviving the full multiple-testing burden of the broader search. Neither R5.2 nor R6.1 installed a funnel correction; the (a1) ρ̄=0 conservatism partially/accidentally offsets but does not address it. Handed to RW/WY-reopen + supplementary-evidence + paper-trading successors (eligible-not-named). N\* is NOT changed (locked at 18).

### §6.4 N1 — R6.1 T_obs errata (locked)
The recovered data shows T_obs ≈ 2358–2503 over the **forward_2026** window, contradicting the sealed R6.1 prose "T_obs ≈ 6000 (2025 holdout)" at lines 207, 259, 277, 450. Append an errata entry to R6.1 §12 (the designated post-seal errata layer; consistent with the §12.1–§12.4 append precedent) documenting the application-input correction. **This is a factual prose correction, NOT a methodology change** — the formulas always used per-candidate T; the lock holds. Included in this cycle's SEAL bundle + Rule-2 SEAL-eve.

---

## §7 Architecture

- **New module `backtest/tier6_dsr.py`** — pure functions: cohort loader/derivation; per-bar moment loader + verification; `var_null`, `expected_max_ratio_formB`, `expected_max_ratio_formA`, `psr`, `dsr`, pass rule; MC expected-max; CSV/JSON emitters. `evaluate_dsr.py` (the heuristic screen) is left **untouched**.
- **Reuse:** `scipy.stats.norm` (Φ, Φ⁻¹); `backtest.wf_lineage.check_evaluation_semantics_or_raise()` consumption guard before reading the recovered artifacts (per CLAUDE.md evaluation-semantics hard rule).
- **CLI:** `python -m backtest.tier6_dsr --cohort phase4_forward_2026_15bps_v1` (+ `--dry-run`), ISO-8601 UTC stdout logging, non-zero exit on validation failure (per Coding Standards).
- **Artifacts (under `data/phase2c_evaluation_gate/tier6_dsr_v1/`):** `tier6_dsr_results.csv` (18 authoritative) + `tier6_dsr_companion.csv` (21 quarantined) + `tier6_promotion_list.json` (authoritative Form B passes) + `tier6_mc_validation.json`.
- **Registry:** NO new `experiments.db` run rows — Tier 6 DSR is post-hoc analysis (like `evaluate_dsr.py`), and the `run_type` enum does not include it. Provenance recorded in the artifacts + NOTE. *(Flag for review — see §10.)*
- **NOTE:** `docs/phase5/R6_1_TIER_6_EVALUATION_APPLICATION_NOTE.md`. *(Name flagged for review — §10.)*

---

## §8 Testing (TDD)

RED-first, per the project testing rules. Test groups:
1. **DSR/PSR math** vs hand-computed / literature reference values (known SR/γ₃/γ₄/T → known PSR).
2. **Form A & Form B expected-max ratios** at N\*=18 reproduce ≈2.40 / ≈1.85; monotonic in N\*; Form B degenerate guard at N\*≤1.
3. **Kurtosis convention** test (raw vs excess) — the correctness checkpoint.
4. **Cohort derivation** test — 39→18 deterministic; composition assertion; no Monday/R2.1 overlap double-count.
5. **T = total-bars convention** test (not active-bars); moment recompute ε-verification vs stored.
6. **Pass rule** test — `DSR ≥ 0.95` boundary (NOT 0.5); one-sided; no Bonferroni layering.
7. **Edge cases** — extreme γ₄ (numerical stability of the Mertens denominator; non-negative variance guard); near-zero-margin provisional flag; high-γ₄ flag.
8. **MC validation** determinism (seeded) + bounds sanity.
9. **Full-suite zero-regression** gate at every RED/GREEN boundary (CLAUDE.md "NEVER commit code that doesn't pass existing tests").

---

## §9 Deliverables + cycle shape

**Deliverables:** `backtest/tier6_dsr.py` + tests; the 4 artifacts (§7); `R6_1_TIER_6_EVALUATION_APPLICATION_NOTE.md`; R6.1 §12 errata append; CLAUDE.md Phase Marker advance + `docs/phase_marker_history.md` atomic update (Option 1A — this is an arc/cycle closeout).

**Cycle shape:** **single-plan** (`writing-plans`). No engine surgery; pure analytical module on recovered data. TDD; B2 PFR per plan draft (Codex + quant-research-advisor); Rule-2 SEAL-eve before SEAL; arc tag candidate at seal.

---

## §10 Open spec sub-decisions (defaults chosen; confirm or override at review)

1. **Module name** `backtest/tier6_dsr.py` — default; alt `backtest/deflated_sharpe.py`.
2. **NOTE name** `R6_1_TIER_6_EVALUATION_APPLICATION_NOTE.md` — default (distinct from the R6.1 methodology-lock NOTE).
3. **Registry rows** — default NO (analysis layer, no matching run_type). Alt: add a lightweight provenance row.
4. **R6.1 errata placement** — default: append `§12.5` errata entry to the sealed R6.1 NOTE (in this cycle's SEAL bundle). Alt: document only in the new NOTE + cross-reference.
5. **g4_high_flag threshold** + **provisional-margin threshold** — exact values set in the plan (with reviewer input), not hardcoded here.
6. **MC variant** — Gaussian-null only (default) vs Gaussian + heavy-tailed-null sensitivity.

---

## §11 Anti-pre-emption / discipline anchors

Reviewer convergence is advisory only; every fire requires Charlie register. The locked methodology is not re-opened. All §1 out-of-scope items remain eligible-not-named at separate register-events. The T_obs errata is the only edit to a sealed artifact and is a factual prose correction within the designated §12 errata layer.

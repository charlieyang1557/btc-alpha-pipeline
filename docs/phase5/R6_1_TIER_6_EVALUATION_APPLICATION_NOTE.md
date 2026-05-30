# R6.1 Tier 6 Evaluation Application — Cycle SEAL Note

**Cycle:** post-V_SEAL Tier 6 evaluation application — apply the R6.1-locked closed-form Bailey–López de Prado Deflated Sharpe Ratio methodology (+ §12 Errata (a1) lock) to the B-C-narrow-recovered `phase4_forward_2026_15bps_v1` cohort, producing per-candidate DSR + the authoritative promotion list. The eligible-not-named successor (R6.1 §10.1) unblocked by the B-C-narrow data-recovery cycle SEAL `e208193`.

**SEAL status:** **SEALED** at the post-V_SEAL Tier 6 evaluation application cycle SEAL register-event boundary 2026-05-30 UTC (Charlie "Authorize the SEAL" register), after Rule-2 SEAL-eve CLEAR-post-correction. Atomic SEAL bundle (Option 1A, 21st trigger): this NOTE + R6.1 §12.8 errata + CLAUDE.md Phase Marker advance + `docs/phase_marker_history.md` + merge `tier6-dsr-evaluation` → `main` + arc tag `tier6-dsr-evaluation-v1`.

**Path framing:** R6.1 Path α invariant (methodology was locked at R6.1 V_SEAL; this is its computational application as a separate Charlie register-event). Single-plan execution (no engine work). Branch `tier6-dsr-evaluation` → merge to `main` at SEAL (Charlie register disposition 2026-05-29).

**HARD CONSTRAINT compliance anchors:** Tier 6 promotion basis is the **15 bps/side spot anchor** (CLAUDE.md §Conservative-Anchor Gate Integrity (Phase B Tier 5/6) — the 15bps-spot promotion-basis rule; the canonical anchor file named there is `config/execution_phaseb_spot_15bps.yaml` / `spot_realistic_15bps_v1`) — verified via the cost-anchor preflight that the cohort's `execution_config_path` (`config/execution_phase4_15bps.yaml`, body 10+5=15 bps/side, **functionally identical 15bps-spot body** to the canonical `phaseb_spot_15bps` file — differ only in header + `cost_model.name` + SHA by design) is a 15bps-spot anchor, NOT the prohibited 7bps effective model. FWER-style multiplicity correction via the DSR-family (same CLAUDE.md section — the FWER/DSR-family-preferred rule). No `effective_7bps_per_side` results used. The recovered cohort consumed read-only (raw data + recovered artifacts untouched).

**Discipline anchors:** B2 standing rule (Codex + advisor) throughout; 3-layer safety architecture operational; anti-pre-emption (only Charlie register authorizes fires); Rule-2 SEAL-eve OPERATIONALLY REQUIRED before SEAL.

---

## §0 — Charlie register chain

| # | Register (Charlie) | Decision class |
|---|---|---|
| 1 | "path 1 authorized" 2026-05-29 | Cycle entry (post-V_SEAL Tier 6 evaluation application) |
| 2 | D1-(iii) + D2-(ii) + N1–N6 confirm 2026-05-29 | Application-decision lock (after B2 advisor review of D1/D2) |
| 3 | "approve" (design spec) 2026-05-29 | Spec User-Review-Gate pass |
| 4 | "dispatch B2 PFR … you ratify … subagent execution Tasks 1-9 … gated fire/seal — authorized" | Plan PFR + execution authorization |
| 5 | "Authorize to proceed to subagent-driven execution of Tasks 1–9" | Implementation authorization |
| 6 | "Authorize Task 11 FIRE / Branch disposition: merge main" (2026-05-29 PT = 2026-05-30 UTC; FIRE commit `4374ae0` landed 2026-05-30 UTC) | Fire authorization + branch disposition |
| 7 | "Authorize … the SEAL — starting with the Rule-2 SEAL-eve" (2026-05-29 PT / 2026-05-30 UTC) | SEAL authorization (this note) |

---

## §1 — Substantive scope

**Driver:** R6.1 V_SEAL fired methodology-only (Path α); §11.4 deferred the computational application; the B-C-narrow cycle recovered the per-bar return series + γ3/γ4 + registry linkage that were the binding precondition. This cycle performs the deferred computation.

**In scope:** per-candidate closed-form BLdP DSR for the locked-18 cohort; the locked pass rule; the authoritative promotion list + a quarantined non-authoritative companion (the other 21); robustness disclosure + MC validation; this NOTE + the R6.1 §12.8 T_obs errata.

**Out of scope (anti-pre-emption; eligible-not-named successors — see §9):** SD-E-γ stationary-bootstrap overlay; RW/WY framework reopening; N\* estimator refinement; SD-A-ε Hybrid; supplementary IS-OOS; R2.2 Monday mechanism; empirical-ρ̄ refinement; §36 METHODOLOGY_NOTES codification; any cohort/methodology re-lock.

---

## §2 — Locked methodology recap (NOT re-litigated)

Per R6.1 V_SEAL §11.3 + §12 Errata: SD-A-α BLdP 2014 closed-form DSR; N\*-ε with **(a1) ρ̄=0 → N\*=N=18**; SD-B-α DSR ≥ 0 ⇔ **PSR ≥ 1−α** (R6.1 §3.1 — the operative rule is the strong confidence-level rule, not `SR̂ ≥ SR*`); SD-C-α All-18; SD-D-α α=0.05 FWER; SD-E-α within-candidate i.i.d. (Mertens 2002); SD-F Path 1 per-bar full-holdout moments.

## §3 — Application decisions (D1/D2 + N1–N6)

- **D1-(iii):** Form B (Euler–Mascheroni closed-form expected-max, ratio 1.8539 at N\*=18) **authoritative**; Form A (`√(2·ln N*)`=2.4043, the CLAUDE.md-268 interim heuristic) reported as a **conservative companion only**. Anti-threshold-shopping binding: Form B locked authoritative before any DSR computed; not revisited post-result.
- **D2-(ii):** the locked-18 are **authoritative**; the other 21 (2 R2.1-excluded + 19 Monday-pattern) computed at the same Form B formula as a **quarantined non-authoritative companion** (never fed into the pass-set / N\* / promotion narrative).
- **N1:** real per-candidate `T_obs` (~2358–2503), NOT the sealed prose "≈6000" (see §7 / R6.1 §12.8 errata).
- **N2:** T = total finite per-bar count (consistent with the deflated holdout Sharpe). **N3:** SR\* uses null variance 1/(T−1); per-candidate PSR uses the candidate's own Mertens variance. **N4:** γ₄-high + provisional + R2.1-indeterminate flags reported. **N5:** selection-inflation residual-risk disclosed (§6). **N6:** MC expected-max validation companion.

## §4 — Cohort (deterministic, verified)

39 cohort_a − 19 Monday-pattern (name ~ /monday/i) − 2 R2.1-excluded (`35dcfcfbee4cfafc`, `38a1bb228f103c26`; no overlap) = **18**. Composition: 6 volume_divergence + 6 momentum + 3 calendar_effect + 2 mean_reversion + 1 volatility_regime (matches R6.1 §8.1).

---

## §5 — Canonical result (FIRE: commit `4374ae0`, 2026-05-30 UTC)

`python -m backtest.tier6_dsr --cohort phase4_forward_2026_15bps_v1` → **authoritative=18, companion=21, promoted=0, degenerate=0**.

**Authoritative-18 (Form B, DSR ≥ 0.95): 0 promoted.** The promotion list is empty.

| Top by deflated_z_B | theme | per-bar SR | deflated_z_B | PSR_B | flags |
|---|---|---|---|---|---|
| `ema_crossover_momentum_acceleration` | momentum | 0.0327 | −0.2404 | 0.4050 | γ₄-high, R2.1-indeterminate |
| `volume_surge_breakout_divergence` | volume_divergence | 0.0118 | −1.3012 | 0.0966 | γ₄-high, R2.1-indeterminate |
| `weekend_volatility_compression_breakout` | calendar_effect | 0.0077 | −1.4813 | 0.0693 | γ₄-high |
| … (15 more, deflated_z_B down to −4.30) | | | | →0.00 | |

- Threshold z(0.95)=1.6449 / PSR 0.95. **Max observed deflated_z_B = −0.2404 / PSR 0.405** — the best candidate's per-bar Sharpe does not even exceed its own expected-max benchmark (below the weak rule too). No candidate is close.
- **14/18 carry `g4_high_flag`** (within the authoritative-18: g4_high subset γ₄ ∈ [50.49, 351.96]; full-18 γ₄ ∈ [28.11, 351.96]; closed-form asymptotic low-confidence for the heaviest-tailed). **2/18 `r21_indeterminate_flag`** — and they are the top two by deflated_z.
- **Companion-21: 0/21** (non-authoritative). **0 degenerate.**

**MC validation companion** (`tier6_mc_validation.json`, seed 20260529, 100k sims): empirical expected-max ratio at N\*=18 = **1.8205**; Form B = 1.8539 (|Δ|=0.0334); Form A = 2.4043 (|Δ|=0.5838). Form B is the far better Gaussian-extreme-value approximation — **empirically validates the D1 authoritative-Form-B choice**. Even at the (slightly lower) empirical ratio, the best candidate's deflated_z (−0.24) is nowhere near passing.

**Substantive conclusion:** **No candidate in the locked-18 survives the Tier 6 closed-form DSR multiple-testing haircut** at N\*=18 / α=0.05 / Form B. A zero-capital conservative-first-fire outcome (R6.1 §11.4) — no promotion, no capital implication. Given the (a1) FP-conservative lock + the §6 selection-inflation caveat, 0/18 is if anything a generous read.

Artifacts: `data/phase2c_evaluation_gate/tier6_dsr_v1/{tier6_dsr_results.csv (18), tier6_dsr_companion.csv (21), tier6_promotion_list.json (empty), tier6_mc_validation.json}`.

## §6 — Disclosures (binding)

- **N5 selection-inflation residual risk (load-bearing):** DSR-at-N\*=18 controls FWER over the sealed **All-18 family only**; it is **necessary-not-sufficient** and does **NOT** correct the upstream **198→39→18** winnowing. Neither R5.2 nor R6.1 installed a funnel correction; the (a1) ρ̄=0 conservatism partially/accidentally offsets but does not address it. Passing Tier 6 ≠ surviving the full search's multiple-testing burden. (Here the gate produced 0 passers, so the funnel concern is moot for promotion this cycle — but it remains the governing framing for any future cohort.) Handed to RW/WY-reopen + supplementary-evidence + paper-trading successors (eligible-not-named).
- **γ₄-high (14/18):** the closed-form DSR rests on asymptotic normality of the Sharpe estimator; at γ₄ up to ~352 (authoritative-18 max 351.96) over ~2500 bars (~70–98% of which are flat 0-return bars across the cohort, median ~89%), the asymptotic is least trustworthy for the heaviest-tailed candidates. Their DSR is reported but γ₄-high-flagged as low-confidence. (Moot for promotion given 0 passers.)
- **R2.1-INDETERMINATE (2/18):** `7abff29fc2f117a1` (ema_crossover, the top performer) + `2433a38b2f9a7211` carry R2.1 INDETERMINATE-overall flags — disclosed so the top candidate is not over-interpreted.
- **Day-of-week calendar caveat:** the 3 retained calendar candidates (`friday_close_weekend_positioning`, `weekday_momentum_friday_fade`, `weekend_volatility_compression_breakout`) carry day-of-week names that escaped the `monday` substring exclusion filter and were NOT subjected to the same Monday curve-fit scrutiny. Name-substring is a heuristic proxy (DSL content unavailable).
- **Within-candidate serial correlation (SD-E-α i.i.d.):** the known anti-conservative limitation; SD-E-γ stationary-bootstrap is a named successor. (No borderline passes here to mark provisional.)

## §7 — R6.1 T_obs errata (R6.1 §12.8)

The recovered data shows per-candidate `T_obs` ≈ 2358–2503 over the **forward_2026** window (2026-01-01 → 2026-04-16), contradicting the sealed R6.1 prose "T_obs ≈ 6000 (2025 holdout)" at lines 207/259/277/450. This is an **application-input factual correction, NOT a methodology change** — the DSR formulas always used per-candidate T; the lock holds. Documented as **R6.1 §12.8 (Errata E8)** appended to the R6.1 NOTE errata layer (sealed body byte-identical).

## §8 — Review trail

- **B2 advisor review of D1/D2** (workflow `wlwio6m8l`): both legs convergent on D1-(iii) + D2-(ii); surfaced the verified T_obs/kurtosis/zero-fraction findings → N1–N6.
- **B2 plan PFR** (workflow `w1w0w3rph`): both legs confirmed the `PSR ≥ 0.95` pass rule; 14 binding amendments (A1–A14) adjudicated + applied (all Layer-3 citation-verified, incl. 2 bugs in the plan's own test code).
- **Subagent-driven execution** (Tasks 1–9): 3 chunks × (spec + code-quality review) + final whole-module review; **23 review fixes** adjudicated/applied (incl. data-integrity-crash, yaml.YAMLError, guard-before-CSV-read, degenerate-row NaN fields). Full suite **2452 passed / 2 xfailed / 0 failed** (independently re-run twice by orchestrator; pc9 baseline advanced 2248→2328 additive per its documented protocol).
- **Rule-2 SEAL-eve** (workflow `wjpnc5h08`): both legs recomputed the DSR pipeline + grep-verified every §5 number against the artifacts — core result (0/18, deflated_z, MC, flag counts), §12.8 append byte-identity, T-independence math, and 15bps cost-anchor all VERIFY CLEAN. Caught **5 doc-precision defects in this NOTE** (1 HIGH/BLOCKING: §5/§6 γ₄ range cross-cohort mislabel — companion/all-39 `[20.3, 357.5]` attributed to the authoritative-18, true `[50.49, 351.96]`; + fabricated "HARD CONSTRAINT 270/268" numeric IDs; + γ₄-max 357→352; + zero-fraction band; + §0 UTC-boundary date) — all orchestrator-Layer-3-verified against the artifacts and corrected here. **Prose-only; no recomputation / no re-fire** (the 0/18 result + DSR math + merge decision unchanged).

## §9 — Eligible-not-named successors (NOT bound)

RW/WY framework reopening; SD-E-γ stationary-bootstrap upgrade; N\* estimator refinement; SD-A-ε Hybrid; supplementary IS-OOS analytical cycle; R2.2 Monday-pattern mechanism investigation; empirical-ρ̄ refinement; Bonferroni eligibility re-eval; §36 METHODOLOGY_NOTES codification batch (from this cycle + B-C-narrow); R6.1-A/B/C + R5.2 memory codification; Phase 4 paper-trading deployment; project pause / strategic absorption. All eligible at separate Charlie register-events per anti-pre-emption.

## §10 — Artifact signature

- Path: `docs/phase5/R6_1_TIER_6_EVALUATION_APPLICATION_NOTE.md`
- Cycle: post-V_SEAL Tier 6 evaluation application (R6.1 Path α successor; B-C-narrow precondition satisfied)
- Module: `backtest/tier6_dsr.py` (+ `tests/test_tier6_dsr.py`, 80 tests); `evaluate_dsr.py` heuristic screen untouched
- FIRE: commit `4374ae0` — 0/18 promoted (Form B, N\*=18, α=0.05), 0 degenerate
- Branch: `tier6-dsr-evaluation` → merge `main` at SEAL (Charlie register disposition)
- SEAL bundle (atomic): this NOTE (SEALED) + R6.1 §12.8 errata + CLAUDE.md Phase Marker advance + `docs/phase_marker_history.md` (Option 1A, 21st trigger) + merge `tier6-dsr-evaluation` → `main` + arc tag `tier6-dsr-evaluation-v1`
- Sealed by: Charlie SEAL register 2026-05-30 UTC ("Authorize the SEAL")

**End of SEAL NOTE.**

# A-1 Design Spec — SD-E-γ Stationary-Bootstrap Variance Overlay

- **Date:** 2026-05-30 (UTC)
- **Status:** v2 — post-B2-review (advisor + Codex adjudicated; see §11). Pending Charlie review gate, then writing-plans.
- **Cycle:** A-1 (first of the Charlie-registered `A-1 → A-2` methodology-successor sequence, 2026-05-30)
- **Lineage:** R6.1 §6.1 line 191 explicitly-disclosed eligible-not-named successor ("SD-E-γ stationary bootstrap variance overlay (Politis–Romano 1994)"); unblocked by the B-C-narrow data-recovery SEAL (`e208193`) which produced the per-candidate `returns_per_bar.parquet` inputs; entered after the Tier 6 evaluation application SEAL (`8375fce`).
- **Registered decisions:** D1 = Option 1+ (lean diagnostic + mandatory inflation-ratio column + numerator-negative attestation); D2 = Approach A (fixed motivated block-length band, no Politis–White automatic); D3 = cohort 18 authoritative + 21 companion.

---

## §1. Purpose & Scope

### 1.1 Purpose
Close the disclosed R6.1 §6.1 (line 191) **within-candidate serial-correlation** gap of the sealed closed-form Tier 6 Deflated Sharpe Ratio (DSR) by replacing the Mertens (2002) i.i.d. Sharpe-estimator standard error with a serial-correlation-robust **stationary-bootstrap** SE (Politis–Romano 1994), and **measuring** the resulting variance-inflation on the recovered `phase4_forward_2026_15bps_v1` cohort.

The sealed Tier 6 result is **0/18 promoted**, and the verdict is **mathematically invariant** to the SE estimate on this cohort (§2.2). A-1 is therefore a **diagnostic overlay + standing primitive**, NOT a re-evaluation and NOT a re-seal. Its value is (a) the first empirical *measurement* of the §6.1 gap's magnitude on real data, and (b) a reusable, tested serial-correlation-robust SE capability for future cohorts where a candidate *is* near the threshold (`provisional_flag ≥ 1`).

### 1.2 In scope
- A reusable stationary-bootstrap Sharpe-estimator SE primitive.
- A per-candidate inflation-ratio measurement (`SE_boot / SE_mertens`) over a fixed block-length grid, on 18 authoritative + 21 companion candidates.
- A robustness attestation establishing verdict-invariance.
- New, physically + label-isolated diagnostic artifacts.

### 1.3 Out of scope (explicit — see §8)
- No change to `N*`, `α`, the pass rule, the `SR*` benchmark null, or cohort selection.
- No bootstrap of the `SR*` benchmark variance/scale (that is the *cross-candidate* axis = A-2 / RW–WY, a separate registered successor; and a fully scale-consistent robust DSR is a larger deferred refinement — §8.2).
- No Politis–White (2004) automatic block-length (D2 = Approach A).
- No re-seal of the Tier 6 evaluation; **0/18 stands**.
- No edit to `backtest/tier6_dsr.py` or `data/.../tier6_dsr_v1/` sealed artifacts.

---

## §2. Background

### 2.1 The disclosed gap (R6.1 §6.1 line 191; documented-limitations line 194)
The sealed methodology documents that positive within-candidate autocorrelation (BTC hourly volatility clustering / ARCH effects) **inflates** the Sharpe-estimator variance versus the i.i.d. baseline; the Mertens 2002 i.i.d. variance therefore **under-states** the true variance → true Type-I error ≥ nominal (an **anti-conservative** direction). The named mitigation (line 191) is "SD-E-γ stationary bootstrap variance overlay (Politis–Romano 1994)," preserved as an eligible-not-named successor under anti-pre-emption (§6.1 line 197).

### 2.2 The verdict-invariance finding (load-bearing)
The sealed per-candidate pass statistic (`tier6_dsr.py`, with the A10 `√(T−1)` cancellation) reduces exactly to:

```
deflated_z = (SR̂ − SR*) / SE_mertens
pass  ⇔  deflated_z ≥ z(1−α) = 1.6449  >  0
```

Passing therefore **requires** `SR̂ − SR* > 0`. On the recovered cohort, **all 18 authoritative candidates have `SR̂ − SR* < 0`** (verified: max excess `−0.004436` for `ema_crossover_momentum_acceleration`; worst `−0.075069`). Because `SE > 0` for any estimator, no SE — bootstrap, i.i.d., or adversarially small — can flip a negative numerator to a pass. The N4 `provisional_flag` (an authoritative pass whose margin is within the plausible serial-correlation inflation band; `tier6_dsr.py::annotate_flags`) is consequently `False` for all 18.

Directionally: a serial-correlation-robust SE is typically **larger** than i.i.d. (positive autocorrelation inflates it). A larger `SE` shrinks `|deflated_z|` *toward* zero; since the numerator stays negative, `deflated_z` stays below `0 < 1.6449` and **never reaches the pass threshold**. (It moves numerically toward — never across — the threshold; it does not move "away," but it cannot pass.)

**Consequence:** A-1 cannot change the 0/18 verdict on this cohort. Its honest deliverable is to *measure* the inflation the gap describes, and to *exhibit* (not merely assert) the numerator-negative fact that discharges it.

---

## §3. Statistical Method

### 3.1 Quantities
- `SR̂ = mean(r) / std(r, ddof=0)` over the **finite** per-bar return series (sealed convention; `tier6_dsr.py::load_candidate_moments`).
- `SE_mertens = √(mertens_variance(SR̂, γ3, γ4, T))`, where `mertens_variance = (1 − γ3·SR̂ + ((γ4−1)/4)·SR̂²) / (T−1)` (`tier6_dsr.py::mertens_variance`). This is the i.i.d. baseline SE of the Sharpe estimator. (The *literal* code denominator is `√(term) = SE_mertens·√(T−1)`; it equals `SE_mertens` only as the **effective** denominator after the A10 `√(T−1)` cancellation against the numerator, hence `deflated_z = (SR̂ − SR*)/SE_mertens`.)
- `SE_boot` = standard deviation (`ddof=1`) of the bootstrap distribution `{SR̂_b}` of the per-bar Sharpe, under the stationary bootstrap.
- **`inflation_ratio = SE_boot / SE_mertens`** (the primary deliverable).
- `robust_se_z_context = (SR̂ − SR*) / SE_boot` (informative context only; **renamed away from `deflated_z_*` to avoid any pass-statistic reading**; no `pass_boot` column is emitted).
- `excess = SR̂ − SR*_B` (the numerator; exhibited per candidate for the invariance attestation).

**Identity precondition (made explicit):** `inflation_ratio = SE_boot/SE_mertens = deflated_z / robust_se_z_context` holds **only because A-1 holds `SR̂` and `SR*` fixed** across both forms — only the SE denominator differs. A future variant that also adjusts `SR*` (cross-candidate axis / scale-consistent DSR, §8.2) would break this identity; it is not part of A-1.

`SR*` is **unchanged** — it remains `√(1/(T−1)) · ER` on the i.i.d. Gaussian null (`tier6_dsr.py::sr_star`); see §8.2.

### 3.2 Stationary bootstrap (Politis–Romano 1994)
**Input contract (load-bearing — see §11 review CRITICAL-1):** the bootstrap operates on the **finite-filtered per-bar return array of length `T = cm.T`**, sourced identically to `load_candidate_moments`'s `rf = r[np.isfinite(r)]`. Every candidate's parquet has a **leading-NaN first bar** (verified cohort-wide: `raw_len = T + 1`); passing the raw column would silently NaN-corrupt every `SR̂_b`. `bootstrap_sharpe_se` MUST assert `len(returns) == cm.T` and that `returns` is all-finite (or itself apply the finite filter).

For an expected (mean) block length `L`, set `p = 1/L`. Construct a resample of length `T`: pick a uniform start index in `[0, T)`; at each subsequent position, with probability `(1−p)` advance to the next index (circular, mod `T`), and with probability `p` jump to a fresh uniform start. This yields geometric-length, circularly-wrapped blocks preserving local serial dependence of expected length `L`. For each of `n_replicates` resamples compute `SR̂_b = mean(resampled) / std(resampled, ddof=0)` (repeated indices are intended observations, not de-duplicated). `SE_boot(L) = std({SR̂_b}, ddof=1)`. A bootstrap replicate with zero resample variance (`std == 0`, possible but vanishingly rare for T≈2500) is skipped and counted; if >0.1% of replicates are skipped the run raises (signals a degenerate input).

### 3.3 Block-length band (D2 = Approach A)
Report `SE_boot(L)` and `inflation_ratio(L)` at the fixed grid `BLOCK_LEN_GRID = (1, 6, 12, 24, 48, 96)` hours:
- `L = 1` h → degenerate near-i.i.d. resample (sanity anchor: `inflation_ratio ≈ 1`; also the **heavy-tail baseline**, §8.3).
- `L ∈ {6, 12, 24, 48, 96}` h → intraday → 4-day spans of plausible BTC hourly vol-clustering memory. Upper anchor capped at 96 h: at `T ≈ 2500`, `L = 96` gives ~26 effective blocks, beyond which the stationary-bootstrap SE itself becomes noisy (measuring estimator noise rather than dependence).

Per-candidate inflation is reported as the band `[min, max]` across the grid plus each grid point. No single "optimal" L is selected (a single fixed L under-reports the uncertainty the band exists to characterize; verdict-invariance frees us to report a band with no pass/fail consequence).

### 3.4 Determinism (fully reproducible from this spec)
Base seed `20260529` (matching `tier6_dsr.py`'s MC convention, L467). Each `(candidate, block_len)` draws from an **independent** substream constructed from stable entropy so that reordering the cohort or extending `BLOCK_LEN_GRID` never perturbs an existing result:

```
stable_hash_int = int.from_bytes(hashlib.sha256(hypothesis_hash.encode()).digest()[:8], "big")
rng = np.random.default_rng(np.random.SeedSequence([base_seed, stable_hash_int, block_len]))
```

The Python builtin `hash()` is **banned** (per-process salted). `SeedSequence.spawn()` order-dependence is **banned** — substreams are keyed by explicit entropy `(base_seed, stable_hash_int, block_len)`, not spawn order. The base seed and `n_replicates` are recorded in the output artifact.

### 3.5 Replicate count
`n_replicates` default `5000` (configurable via CLI; one-time local computation, no API cost). The target is a *stable SE point estimate* (≈3 significant figures), not tail-quantile precision. A replicate-doubling stability test at the **largest** block length (`L = 96`, where SE is highest-variance) is part of the test contract (§7).

---

## §4. Module Architecture

New module `backtest/tier6_bootstrap.py` + test file `tests/test_tier6_bootstrap.py`. It **imports from** (does not modify) `backtest/tier6_dsr.py`: `load_candidate_moments`, `mertens_variance`, `sr_star`, `evaluate_candidate`, `derive_cohort`, and the constants `N_STAR`, `ALPHA`, `MOMENT_RECOMPUTE_EPS`, `EVALUATION_GATE_DIR`, `DEFAULT_COHORT`, `HOLDOUT_DIR`. (`tier6_dsr.py` is 1037 lines — at the >800-line ceiling — so additive-in-place is disallowed.)

Units (each small, single-purpose, independently testable):

1. `stationary_bootstrap_indices(T: int, expected_block_len: float, rng) -> np.ndarray` — one length-`T` resample index array (Politis–Romano geometric blocks, circular). Pure; deterministic given `rng`.
2. `bootstrap_sharpe_se(returns: np.ndarray, expected_block_len: float, n_replicates: int, rng) -> float` — `SE_boot(L)`; asserts `returns` finite and length matches the candidate's `T`.
3. `mertens_se(sr, gamma3, gamma4, T) -> float` = `√(mertens_variance(...))` (i.i.d. baseline SE; thin reuse of the sealed function).
4. `evaluate_candidate_bootstrap(cm, returns, *, block_grid=BLOCK_LEN_GRID, n_replicates, base_seed) -> dict` — assembles the per-candidate record: `excess = SR̂ − SR*_B`, `SE_mertens`, and for each `L`: `SE_boot(L)`, `inflation_ratio(L)`; plus the band `[min,max]`, the `serialcorr_increment = inflation(L)/inflation(L=1)` per L (§8.3), `robust_se_z_context_L24`, and the sealed `deflated_z_B` recomputed for tie-back. **Degenerate-term parity (§11 MEDIUM-1):** if `mertens_se` raises (non-positive Mertens term, possible on extreme-kurtosis future cohorts), emit `inflation_ratio = NaN` + `mertens_degenerate_flag = True` (parity with the sealed `_degenerate_fail_row` pattern) rather than crashing; `SE_boot` is still reported (the bootstrap needs no positivity of the asymptotic term).
5. `run_cohort_bootstrap(cohort=DEFAULT_COHORT, *, n_replicates, base_seed) -> CohortBootstrapResult` — derive (locked-18, companion-21) via `derive_cohort`; for each candidate load returns through the existing sha256 + `single_run_holdout_v1` lineage gates (`load_candidate_moments`); evaluate; build records + the cohort attestation (`all_excess_negative`, `max_excess`, `verdict_invariant`, inflation summary). **Before writing**, capture sha256 of the sealed `tier6_dsr_v1/` artifacts and re-check them unchanged after (§7 immutability gate); A-1 writes ONLY under its own dir.
6. Emitters: `write_results_csv`, `write_companion_csv`, `write_attestation_json` → the isolated artifact dir (§6).
7. `main()` CLI (`python -m backtest.tier6_bootstrap`): flags `--cohort`, `--n-replicates`, `--seed`, `--dry-run`; ISO-8601 UTC stdout logging; non-zero exit on any validation failure. **No cost-anchor preflight** (A-1 makes no promotion decision; the sealed `_assert_cost_anchor_15bps_spot` is a private promotion-path helper and is deliberately not reused — the lineage + sha256 integrity gates in `load_candidate_moments` are the relevant consumption discipline).

**Data flow:** `holdout_results.csv` → `derive_cohort` → per candidate {`load_candidate_moments` (sha256 + lineage gate) → finite-filtered `return` array → `evaluate_candidate_bootstrap`} → records → emit CSVs + attestation JSON (after the sealed-artifact immutability re-check).

---

## §5. Inputs & Data Conventions

- **Per-candidate per-bar returns:** `data/phase2c_evaluation_gate/<cohort>/<hash>/returns_per_bar.parquet`, `return` column, consumed through the existing integrity gates in `load_candidate_moments` (A2 lineage guard on `holdout_summary.json` under `single_run_holdout_v1`; A8 sha256 of the parquet vs the registry `returns_per_bar_sha256`; independent moment recompute-verify). **The series carries a leading-NaN first bar** (verified cohort-wide; `raw_len = T + 1`); A-1 consumes the **finite-filtered length-`T` array** identically to the sealed moment path. A-1 adds **no** new ingestion path.
- **Moment conventions (inherited, unchanged):** `γ3` population skew (`scipy.stats.skew(bias=True)`); `γ4` RAW kurtosis (`kurtosis(fisher=False, bias=True)`, Gaussian = 3); `T` = count of finite per-bar returns; `SR̂ = mean/std(ddof=0)`.
- **Cohort:** `derive_cohort` partitions `cohort_a` into locked-18 (authoritative) + companion-21 (non-authoritative). A-1 runs on **both** (D3), companion clearly labeled.

---

## §6. Outputs & Artifacts

New, isolated directory `data/phase2c_evaluation_gate/tier6_serialcorr_robustness_v1/` (sibling to, physically separate from, the sealed `tier6_dsr_v1/`):

- `serialcorr_results.csv` (18 authoritative rows) — columns: `hypothesis_hash, name, theme, T, sr_per_bar, gamma3, gamma4, sr_star_B, excess, deflated_z_B, se_mertens, se_boot_{L1,L6,L12,L24,L48,L96}, inflation_{L1,L6,L12,L24,L48,L96}, serialcorr_increment_{L6,L12,L24,L48,L96}, inflation_band_min, inflation_band_max, robust_se_z_context_L24, g4_high_flag, mertens_degenerate_flag`.
- `serialcorr_companion.csv` (21 companion rows) — same schema, NON-AUTHORITATIVE.
- `serialcorr_attestation.json` — `{cohort, base_seed, n_replicates, block_len_grid, hash_to_int_rule, n_authoritative, n_companion, all_excess_negative: true, max_excess, verdict_invariant: true, inflation_ratio_summary: {min, median, max, by_block_len}, serialcorr_increment_summary, sealed_tier6_dsr_v1_sha256: {<file>: <sha>}, generated_at_utc, source_commit}`.

Every artifact carries a self-describing header / top-level field: **"diagnostic; NON-AUTHORITATIVE; no parallel pass/fail track; verdict invariant (all SR̂ < SR*)."**

---

## §7. Testing Strategy (TDD — tests precede implementation)

- **`stationary_bootstrap_indices`:** output length `T`; all indices in `[0, T)`; determinism under fixed `rng`; `L = 1` ⇒ ~all jumps (near-i.i.d.); large `L` ⇒ long consecutive (circular) runs; edge `T = 2`.
- **`bootstrap_sharpe_se`:**
  - i.i.d. standard-Gaussian input → `SE_boot(L=1) ≈ 1/√(T−1) ≈ SE_mertens` (within MC tolerance).
  - **L=1 plain-bootstrap equivalence:** `SE_boot(L=1)` matches an independent plain i.i.d.-with-replacement bootstrap SE (catches wrong jump/continue logic).
  - positive AR(1) series → `SE_boot(L>1) > SE_boot(L=1)`.
  - determinism under fixed seed; **NaN-leading-bar input**: raw-column-with-leading-NaN vs finite-array must be rejected by the length/finite assertion (no silent contamination).
  - flat zero-variance input raises (contract parity with `mertens_variance`).
- **`inflation_ratio`:** ≈ 1.0 on i.i.d.; > 1.0 on positive AR(1); `serialcorr_increment` (vs L=1 baseline) increases with `L` on a strongly autocorrelated series (directional). **Identity regression:** `inflation_ratio == deflated_z / robust_se_z_context` on a fixture with nonzero excess.
- **Replicate-stability:** doubling `n_replicates` changes `SE_boot` at `L = 96` (largest, highest-variance) by < tolerance.
- **Degenerate parity:** a synthetic extreme-kurtosis candidate where `mertens_se` raises → record has `inflation_ratio = NaN` + `mertens_degenerate_flag = True`, `SE_boot` present, cohort run does not crash.
- **Tie-back regression (numerical):** recomputed sealed `deflated_z_B` for each candidate matches `tier6_dsr_v1/tier6_dsr_results.csv` within `MOMENT_RECOMPUTE_EPS` — proves the overlay sits on the identical base.
- **Sealed-artifact immutability (byte-level):** after a cohort run, sha256 of every file under `tier6_dsr_v1/` is unchanged, `git status` shows `backtest/tier6_dsr.py` clean, and A-1 wrote only under `tier6_serialcorr_robustness_v1/`. (The numerical tie-back proves same-base; this proves nothing sealed was overwritten.)
- **Cohort run:** 18 + 21 counts; attestation `all_excess_negative` / `max_excess` correct; artifacts land in the isolated dir with the NON-AUTHORITATIVE header.
- **CLI:** `--dry-run` performs no writes; bad cohort → non-zero exit.
- **The existing full suite must remain green at its current baseline** (Phase-Marker-stated 2452 passed / 2 xfailed — re-run as the gate, not assumed); no edit to `tier6_dsr.py` or its tests.

---

## §8. Out-of-Scope & Governance Statements

### 8.1 No re-seal; sealed artifacts immutable
A-1 does not re-open or re-evaluate Tier 6. `tier6_dsr.py`, `tier6_dsr_v1/`, and the sealed NOTEs are byte-untouched; the §7 immutability gate (sha256 + git-clean) enforces it, complementing the numerical tie-back.

### 8.2 `SR*` stays on the i.i.d. null — deliberately (denominator-only diagnostic)
A-1 refines **only** the per-candidate *estimator* SE (the `deflated_z` denominator); it is a **denominator-only / fixed-`SR*` diagnostic**. `SR*` remains `√(1/(T−1))·ER` on the i.i.d. Gaussian null. Two layered reasons:
1. **Axis scoping (advisor):** `SR*` is an expected-max-of-`N*`-independent-Gaussians benchmark living on the **cross-candidate independence axis**; serial-correlation-adjusting it conflates with **A-2 / RW–WY** (a separate registered successor) and would reopen the (a1) ρ̄=0 / `N*`=18 lock — an anti-pre-emption violation.
2. **Scale-consistency disclosure (Codex):** a *fully* scale-consistent serial-correlation-robust DSR would also robustify the **null SE feeding `SR*`** (not merely substitute `SE_boot`, which is the alternative-hypothesis SE, not the null SE — so the naive `SR*_boot = SE_boot·ER` is itself only an approximation). That is a strictly larger refinement requiring a defensible serially-correlated joint null; it is **deferred** and, critically, **verdict-irrelevant here** (no scale adjustment can flip a negative numerator). A-1 therefore explicitly reports `robust_se_z_context` as a *denominator-only*-robust statistic, not a fully scale-consistent robust DSR.

The asymmetry is thus recognized and scoped-on-purpose, not missed.

### 8.3 Inflation-ratio attribution — L=1 baseline decomposition
14/18 authoritative candidates carry `g4_high_flag` (RAW kurtosis ≥ 50). The bootstrap resamples the empirical (heavy-tailed) marginal, so even at `L = 1` (no serial structure) `inflation_ratio(L=1)` differs from 1.0 by a **heavy-tail / finite-sample SE component**. A-1 therefore reports:
- `inflation_ratio(L)` = total SE difference vs Mertens i.i.d. (serial-correlation **+** heavy-tail).
- `inflation_ratio(L=1)` = the **heavy-tail / finite-sample baseline**.
- `serialcorr_increment(L) = inflation_ratio(L) / inflation_ratio(L=1)` = the **serial-correlation-specific** signal.

This turns the §6.1 attribution caveat into an actual decomposition; the ratio is not over-attributed to the serial-correlation mechanism alone.

### 8.4 Artifact isolation
Physically + label-isolated from the sealed authoritative artifacts, mirroring the companion-21 quarantine and the D2 "physically + labelled separate" binding — so no future reader mistakes the diagnostic for a second gate.

---

## §9. Locked Decisions Log
- **D1 (Charlie 2026-05-30):** Option 1+ — lean diagnostic; mandatory per-candidate `inflation_ratio` CSV column; numerator-negative attestation with the concrete `max_excess`. No parallel pass/fail track.
- **D2 (Charlie 2026-05-30):** Approach A — fixed motivated block-length band; no Politis–White automatic; no new dependency. (Grid finalized at `(1,6,12,24,48,96)` h post-review.)
- **D3 (Charlie 2026-05-30):** Cohort = 18 authoritative + 21 companion.
- **Adopted from B2 review (§11):** SR* i.i.d. denominator-only framing (§8.2); finite-filtered length-T bootstrap input (§3.2); pinned hash→int + entropy-keyed substreams (§3.4); 96 h upper anchor + L=1 heavy-tail baseline decomposition (§3.3, §8.3); degenerate-term parity (§4.4); byte-level sealed-artifact immutability gate (§7, §8.1); identity shared-numerator precondition (§3.1); `robust_se_z_context` rename (§3.1); cost-anchor preflight dropped (§4.7).

## §10. Open Questions for Charlie / Reviewers (residual)
All B2-review findings adjudicated in §11 are resolved in-spec. Residual judgment calls left visible:
1. `n_replicates` default `5000` (vs 2000) — confirm (cheap, local; bumped on advisor's "no API cost" point).
2. Block grid upper anchor `96 h` — confirm (advisor lean; could stop at 48 h).
3. Keep the single `robust_se_z_context_L24` context column (renamed away from `deflated_z_*`), or omit any robust-z column entirely.

## §11. B2 Review Adjudication Log (advisor + Codex, 2026-05-30)
Both legs convergent; no hallucinations (all load-bearing numbers/claims independently grep-verified before adoption). Dispositions:

| # | Finding (leg) | Severity | Disposition |
|---|---|---|---|
| CRITICAL-1 | Bootstrap input must be finite-filtered length-T; parquet has leading-NaN first bar (advisor HIGH-1; **verified cohort-wide 6/6**) | CRITICAL | **ADOPTED** §3.2/§5 input contract + assert + NaN test |
| HIGH-2 | State shared-numerator precondition for the inflation_ratio identity (advisor) | HIGH | **ADOPTED** §3.1 |
| HIGH-asym | `SR*` i.i.d. + robust denominator = denominator-only diagnostic; disclose explicitly; fully-robust DSR would robustify null SE (Codex HIGH + advisor §8.2) | HIGH | **ADOPTED** §8.2 reframed (kept SR* i.i.d. per scoping; added scale-consistency disclosure; did NOT add SR*_boot deliverable) |
| MED-1 | Degenerate-term parity when `mertens_se` raises (advisor + Codex) | MEDIUM | **ADOPTED** §4.4 |
| MED-2 | Pin hash→int + ban spawn-order / Python hash(); key substream by (seed, hash_int, block_len) (advisor + Codex) | MEDIUM | **ADOPTED** §3.4 |
| MED-3 | Tie-back overclaims byte-immutability; add sha256/git-clean gate (advisor + Codex) | MEDIUM | **ADOPTED** §7, §8.1 |
| MED-4 | Add L=1 plain-bootstrap equivalence + nonzero-excess identity test (Codex) | MEDIUM | **ADOPTED** §7 |
| LOW-1 | Tighten §6.1 citation to line 191 (+194) (advisor; **verified**) | LOW | **ADOPTED** §2.1 |
| LOW-2 | Upgrade g4 caveat to L=1-baseline decomposition (advisor) | LOW | **ADOPTED** §8.3 + `serialcorr_increment` column |
| LOW-3 | §2.2 "away from passing" wording backwards (Codex) | LOW | **ADOPTED** §2.2 corrected |
| LOW-4 | Add `MOMENT_RECOMPUTE_EPS` to import list; cost-preflight is private (Codex; **verified L718**) | LOW | **ADOPTED** §4 (added EPS; dropped cost-preflight — no promotion) |
| LOW-5 | State `SR_b = mean/std(ddof=0)` + zero-variance-replicate handling (Codex) | LOW | **ADOPTED** §3.2 |
| LOW-6 | Block grid: add 96 h anchor (advisor Q2) | LOW | **ADOPTED** §3.3 |
| LOW-7 | n_replicates → 5000 (advisor Q3) | LOW | **ADOPTED** §3.5 |
| LOW-8 | Rename `deflated_z_boot_*` → non-gate name (Codex Q4) | LOW | **ADOPTED** `robust_se_z_context` §3.1/§6 |
| LOW-9 | 2452 baseline phrased as target, not verified claim (Codex) | LOW | **ADOPTED** §7 |

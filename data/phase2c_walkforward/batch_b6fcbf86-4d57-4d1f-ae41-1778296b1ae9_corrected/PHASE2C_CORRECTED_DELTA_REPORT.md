# Phase 2C Phase 1 — Corrected vs Pre-Correction Delta Report

**Generated:** 2026-04-26
**Engine:** `wf-corrected-v1` (tag target `3d24fcb`; engine-fix commit `eb1c87f`; re-run HEAD `9d1c722`)
**Pre-correction artifact:** `data/quarantine/pre_correction_wf/batch_b6fcbf86-4d57-4d1f-ae41-1778296b1ae9_STALE_PRE_CORRECTION/walk_forward_results.csv`
**Corrected artifact:** `data/phase2c_walkforward/batch_b6fcbf86-4d57-4d1f-ae41-1778296b1ae9_corrected/walk_forward_results.csv`
**Companion erratum:** `docs/closeout/PHASE2C_5_PHASE1_RESULTS_ERRATUM.md`

---

## Scope

This report is the per-candidate audit detail for the Phase 2C Phase 1 corrected re-run. It is the canonical reference for any forensic-level inspection of how individual candidates' walk-forward Sharpe values, ranks, or theme aggregates changed under the corrected engine. The summarized findings live in the erratum (`PHASE2C_5_PHASE1_RESULTS_ERRATUM.md`); this report is for downstream auditors, future erratum-readers needing per-candidate detail, and any subsequent technique consumer that wants to verify specific candidate-level claims against the data.

**Section RS hard prohibition applies:** the pre-correction CSV is quarantined and may not be consumed by DSR / PBO / CPCV / MDS / strategy-shortlist tooling. This report cites it for audit context only.

---

## §A. Lineage and field-rename verification

| Field | Value |
|---|---|
| `wf_semantics` | `corrected_test_boundary_v1` |
| `corrected_wf_semantics_commit` | `eb1c87f` |
| `current_git_sha` (HEAD at re-run) | `9d1c722131a2...` |
| `lineage_check` | `passed` |
| `check_wf_semantics_or_raise()` round-trip | PASS |
| Corrected CSV uses `wf_test_period_*` fields | YES |
| Corrected CSV bare `wf_*` residue | NONE (clean rename) |

The corrected re-run carries the full producer-consumer contract metadata (Task 7.6) and uses the renamed metric fields (Task 10b commit `a22051e`).

---

## §B. Mechanical claims (bug-independent — should and do survive)

| Metric | Pre-correction | Corrected |
|---|---:|---:|
| n candidates | 198 | 198 |
| `compile_status='ok'` | 198 | 198 |
| `runtime_status='ok'` | 198 | 198 |
| Unique hypothesis hashes | 198 | 198 |
| Hash JOIN overlap (pre ∩ corr) | 198 | 198 |

Candidate identity is fully preserved end-to-end.

---

## §C. Sharpe distribution shape

| Statistic | Pre-correction | Corrected | Δ |
|---|---:|---:|---:|
| n | 198 | 198 | 0 |
| mean | +0.0035 | -0.0400 | -0.0435 |
| median | 0.0000 | 0.0000 | 0.0000 |
| Q1 | -0.4736 | -0.5169 | -0.0433 |
| Q3 | +0.4565 | +0.4330 | -0.0235 |
| min | -2.1912 | -2.1931 | -0.0019 |
| max | +2.7891 | +2.7891 | 0.0000 |
| count > +0.5 | 48 | 44 | -4 |
| count > 0.0 | 85 | 82 | -3 |
| count > -0.3 | 139 | 135 | -4 |

---

## §D. Binary-winner survivorship (pre Sharpe > 0.5 → corrected status)

| Cohort | Count |
|---|---:|
| Pre-correction binary winners (`wf_sharpe > 0.5`) | 48 |
| Pre-correction binary winners with corrected metric available | 48 |
| Pre-correction winners that pass corrected `wf_test_period_sharpe > 0.5` | 44 |
| Survival rate | 91.7% (44/48) |
| Flipped candidates (winner → non-winner under correction) | 4 |

### §D.1 The four flipped candidates

| Hash | Theme | Name | Pre Sharpe | Corr Sharpe | Δ |
|---|---|---|---:|---:|---:|
| `ca5b4c3a` | momentum | ema_crossover_momentum_surge | +0.7539 | -0.3921 | -1.1461 |
| `9e6ad910` | volume_divergence | volume_divergence_breakout_139 | +0.6690 | +0.4915 | -0.1776 |
| `938e135c` | momentum | macd_momentum_continuation_141 | +0.5245 | +0.3239 | -0.2006 |
| `e135fc0d` | volatility_regime | volatility_compression_breakout_158 | +0.5158 | +0.4934 | -0.0224 |

`ca5b4c3a` is the substantive flip (pre-correction Sharpe was unambiguously above the 0.5 threshold; corrected Sharpe is clearly negative). The other three flips are near-threshold: pre-correction Sharpes were 0.5158, 0.5245, and 0.6690 — all close enough to 0.5 that small drops sufficed to flip them.

---

## §E. Per-candidate Sharpe delta distribution

| Bucket | Count |
|---|---:|
| Numerically unchanged (Δ = 0) | 115 / 198 |
| Dropped under correction (Δ < 0) | 58 / 198 |
| Rose under correction (Δ > 0) | 25 / 198 |
| \|Δ\| > 1.0 (single outlier) | 1 / 198 |

| Statistic | Value |
|---|---:|
| Δ mean | -0.0435 |
| Δ median | 0.0000 |
| Δ Q1 | -0.0134 |
| Δ Q3 | 0.0000 |
| Δ min (largest drop) | -1.1461 (`ca5b4c3a`) |
| Δ max (largest rise) | +0.1014 |

The directional asymmetry (more drops than rises, larger drops than rises) is consistent with the bug's mechanism: pre-test equity was entering the denominator and the reported test-period path, so correction can lower or raise reported Sharpe depending on the sign and timing of pre-test contamination. Inferred from the directional pattern, not directly observed.

### §E.1 Top-5 largest \|Δ\| candidates (forensic detail)

| Hash | Theme | Name | Pre | Corr | Δ |
|---|---|---|---:|---:|---:|
| `ca5b4c3a` | momentum | ema_crossover_momentum_surge | +0.7539 | -0.3921 | -1.1461 |
| `9c18b832` | volume_divergence | volume_divergence_momentum_fade | -1.6334 | -2.0453 | -0.4119 |
| `301d74bc` | volatility_regime | volatility_compression_breakout | +1.2558 | +0.8617 | -0.3942 |
| `95bf56e7` | momentum | macd_momentum_reversal | +1.4902 | +1.1040 | -0.3862 |
| `1848161d` | calendar_effect | monday_mean_reversion | +0.2589 | -0.0940 | -0.3529 |

`95bf56e7` here is the top-10-displaced candidate (see §G).

---

## §F. RSI hypothesis re-test

| Statistic | Pre-correction | Corrected | Δ |
|---|---:|---:|---:|
| Pearson(rsi_factor_count, Sharpe) | +0.024 | +0.0153 | -0.009 |
| Spearman naive (no tie correction) | +0.043 | +0.0241 | -0.019 |
| Spearman scipy (tie-corrected) | +0.043 | +0.0205 | -0.022 |
| with-RSI mean Sharpe (n=180) | +0.010 | -0.036 | -0.046 |
| without-RSI mean Sharpe (n=18) | -0.058 | -0.079 | -0.021 |

Both correlation magnitudes are close enough to zero that they should be treated as no detectable linear or rank relationship in this batch. The corrected wording for the original §2.1 claim is "null result, not supported" (canonical wording in `PHASE2C_5_PHASE1_RESULTS_ERRATUM.md` §5.2). The n=18 without-RSI subgroup is too small to support generalizable directional claims.

---

## §G. Per-theme aggregates

| Theme | n | Pre mean | Corr mean | Δ mean | Pre median | Corr median | Pre >0.5 | Corr >0.5 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| mean_reversion | 39 | +0.376 | +0.376 | 0.000 | +0.290 | +0.290 | 14 | 14 |
| volume_divergence | 40 | +0.081 | +0.042 | -0.039 | -0.055 | -0.099 | 13 | 12 |
| volatility_regime | 40 | +0.022 | -0.030 | -0.052 | 0.000 | 0.000 | 9 | 8 |
| calendar_effect | 40 | -0.004 | -0.033 | -0.029 | 0.000 | -0.005 | 7 | 7 |
| momentum | 39 | -0.459 | -0.558 | -0.099 | -0.481 | -0.682 | 5 | 3 |

| Aggregate | Pre | Corr |
|---|---:|---:|
| Best-vs-worst gap (mean_reversion - momentum, mean) | 0.834 | 0.934 |
| Total >0.5 across all themes | 48 | 44 |

Rank ordering preserved 1-for-1 (mean_reversion → volume_divergence → volatility_regime → calendar_effect → momentum). Gap widens slightly under correction. mean_reversion's mean is bit-identical pre-vs-corrected; momentum took the largest hit (Δ -0.099).

---

## §H. Top-20 ranking comparison

| Rank | Pre-correction (hash, name, Sharpe) | Corrected (hash, name, Sharpe) |
|---:|---|---|
| 1 | `0bf34de1` volume_divergence_momentum_194 +2.789 | `0bf34de1` volume_divergence_momentum_194 +2.789 |
| 2 | `b5e798dc` volume_divergence_accumulation +1.903 | `cc295177` volume_divergence_reversal +1.633 |
| 3 | `cc295177` volume_divergence_reversal +1.801 | `6059c88e` bollinger_lower_breach_reversion +1.604 |
| 4 | `6059c88e` bollinger_lower_breach_reversion +1.604 | `b5e798dc` volume_divergence_accumulation +1.578 |
| 5 | `95bf56e7` macd_momentum_reversal +1.490 | `e12477c9` bb_squeeze_oversold_reversion_132 +1.490 |
| 6 | `e12477c9` bb_squeeze_oversold_reversion_132 +1.490 | `212dd310` monday_morning_contrarian_fade +1.443 |
| 7 | `212dd310` monday_morning_contrarian_fade +1.443 | `b4dbd6c5` vol_regime_breakout_148 +1.394 |
| 8 | `b4dbd6c5` vol_regime_breakout_148 +1.394 | `fa1cac01` volume_divergence_reversal +1.391 |
| 9 | `fa1cac01` volume_divergence_reversal +1.391 | `80d0d983` bb_zscore_reversion_192 +1.342 |
| 10 | `80d0d983` bb_zscore_reversion_192 +1.342 | `f8e9655e` momentum_acceleration_rsi_181 +1.335 |
| 11 | (rank #11 pre — not tracked here) | `4f3eb681` volume_divergence_reversal +1.279 |
| 12 | — | `31416afa` bb_mean_reversion_oversold +1.279 |
| 13 | — | `06c3b4a2` oversold_bb_mean_reversion +1.144 |
| 14 | — | (rank #14 corrected — not tracked here) |
| 15 | — | (rank #15 corrected — not tracked here) |
| 16 | — | `95bf56e7` macd_momentum_reversal +1.104 |

**Key:**
- Top-10 set overlap: 9/10
- Out: `95bf56e7` (pre #5 +1.490 → corr #16 +1.104) — falls 11 ranks; still well above binary-criterion threshold
- In: `f8e9655e` (corr #10 +1.335)
- Rank #1 (`0bf34de1`) bit-identical pre vs corrected
- Internal reordering within surviving 9: `cc295177` ↑#2, `6059c88e` ↑#3, `b5e798dc` ↓#4; pre #6-#10 mostly shift up one slot

---

## §I. Reproducibility

The numbers in this report were computed by `/tmp/phase2c_delta_compute.py` against the pre-correction CSV (in quarantine) and the corrected CSV (in this directory). The script reads both CSVs, JOINs on `hypothesis_hash`, and computes the deltas. The script itself is not committed (one-shot computation), but the input artifacts are committed and the JOIN logic is straightforward (any consumer can reproduce these numbers from the two CSVs).

For deeper audit (e.g., per-candidate trade list comparison, per-window comparison), the corrected batch's per-candidate trade artifacts and the per-window walk_forward results are preserved alongside the CSV; consult the corrected batch directory.

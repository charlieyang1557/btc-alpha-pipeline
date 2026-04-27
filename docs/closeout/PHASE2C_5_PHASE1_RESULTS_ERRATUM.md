# Phase 2C Phase 1 Results — Erratum under Corrected Walk-Forward Semantics

**Erratum date:** 2026-04-26
**Original closeout:** [`docs/closeout/PHASE2C_5_PHASE1_RESULTS.md`](PHASE2C_5_PHASE1_RESULTS.md) (commit `861d186`, 2026-04-26)
**Corrected batch:** `data/phase2c_walkforward/batch_b6fcbf86-4d57-4d1f-ae41-1778296b1ae9_corrected/`
**Corrected delta report:** `data/phase2c_walkforward/batch_b6fcbf86-4d57-4d1f-ae41-1778296b1ae9_corrected/PHASE2C_CORRECTED_DELTA_REPORT.md`
**Corrected-engine tag:** `wf-corrected-v1` (tag target `3d24fcb`; engine-fix commit `eb1c87f`; corrected re-run HEAD `9d1c722`)
**Pre-correction artifacts:** quarantined at `data/quarantine/pre_correction_wf/batch_b6fcbf86-..._STALE_PRE_CORRECTION/` per Section RS

---

## §1 Correction notice and scope

This erratum amends the Phase 2C Phase 1 closeout (`PHASE2C_5_PHASE1_RESULTS.md`) following discovery of a walk-forward test-boundary semantics bug in `backtest/engine.py`. The bug carried train-period equity into reported test-period metrics, contaminating every walk-forward result the engine produced before commit `eb1c87f`. The full bug analysis, corrected semantic, and consumption rules are in [`docs/decisions/WF_TEST_BOUNDARY_SEMANTICS.md`](../decisions/WF_TEST_BOUNDARY_SEMANTICS.md). The pre-correction Phase 2C artifacts referenced in the original closeout fall under the Section RS hard prohibition: no DSR, PBO, CPCV, MDS, or strategy-shortlist decision may consume them.

This erratum makes two kinds of corrections.

**First, numerical corrections** to the load-bearing claims, based on re-running the same 198 batch-1 candidates under the corrected engine (corrected-engine batch directory cited above; lineage-validated via `backtest.wf_lineage.check_wf_semantics_or_raise()`). The corrected numbers show modest aggregate shifts and preserve the main qualitative findings: the binary criterion still strongly clears, the theme-quality differential survives directionally, and the top-10 ranking is 9/10 stable.

**Second, an epistemic correction** to one specific piece of the original prose: the "RSI hypothesis FALSIFIED" wording in the original closeout was over-claiming relative to the n=198 evidence at the time of writing, independent of the engine bug. The corrected analysis surfaces this distinction more sharply (Pearson correlation went from +0.024 to +0.015, even closer to zero), but the over-claim was present in the original closeout's wording choice, not introduced by the corrected metrics. The corrected wording is "null result, hypothesis not supported" rather than "falsified."

**Scope of this erratum:**
- All load-bearing numerical claims from the original closeout are re-stated with corrected values.
- One specific piece of original prose ("FALSIFIED") is amended to "null result, not supported."
- Phase 2C Phase 1's overall acceptance verdict (binary criterion strongly met) is preserved; the corrected count is 44/198, an amendment from the original closeout's 48/198.
- Downstream consumers must read corrected artifacts only and pass them through the lineage guard (Section §8).

**Out of scope:**
- This erratum does not re-adjudicate the original closeout's structural claims (data integrity, candidate identity, compile/runtime success rates) — those are mechanical and survive unchanged (Section §2).
- This erratum does not provide a full per-candidate forensic review beyond the corrected walk-forward metric comparisons summarized here; detailed per-candidate deltas are preserved in the corrected delta report.

The original closeout file is preserved unmodified for historical reproducibility; this erratum sits alongside it as the canonical reference for corrected Phase 2C Phase 1 numbers.

---

## §2 Mechanical claims survive unchanged

The corrected re-run of the same 198 batch-1 candidates preserves all of the original closeout's mechanical claims. Candidate identity is intact: the 198 hypothesis hashes in the corrected batch JOIN 198/198 against the pre-correction batch on `hypothesis_hash`, with no duplicates and no skipped rows. Candidate-extraction, compilation, and runtime status are unchanged: 198/198 `compile_status='ok'` in both pre and corrected runs, and 198/198 `runtime_status='ok'` in both. The corrected re-run did not introduce new compile failures, runtime errors, or candidate-set drift; it operated on the identical input set under the corrected engine.

The corrected `walk_forward_summary.json` records `wf_semantics='corrected_test_boundary_v1'`, `corrected_wf_semantics_commit='eb1c87f'`, `current_git_sha='9d1c722...'` (HEAD at re-run), and `lineage_check='passed'`. After re-loading from disk, the corrected summary passes round-trip validation through `backtest.wf_lineage.check_wf_semantics_or_raise()`. This is the same producer-consumer contract that gates downstream consumption of corrected-engine artifacts (Section §8); the corrected Phase 2C batch satisfies it end-to-end.

The corrected re-run uses the renamed metric fields (`wf_test_period_sharpe`, `wf_test_period_return`, `wf_test_period_max_drawdown`, `wf_test_period_total_trades`, `wf_test_period_win_rate`, `wf_test_period_window_count`) introduced by the Task 10b refactor (commit `a22051e`). The corrected CSV contains no bare `wf_*` field residue; the rename is clean. Pre-correction CSVs retain the original `wf_*` field names for historical reproducibility but live in the quarantine directory and must not be consumed.

---

## §3 Distribution shape correction

Across the 198 corrected candidates, the walk-forward Sharpe distribution shifts modestly downward relative to the pre-correction distribution. The aggregate shape is summarized below; the binary-criterion consequence (§4) is mechanically derived from where the 0.5 threshold falls on the shifted distribution.

| Statistic | Pre-correction | Corrected | Δ |
|---|---:|---:|---:|
| n | 198 | 198 | 0 |
| mean | +0.0035 | -0.0400 | -0.0435 |
| median | 0.0000 | 0.0000 | 0.0000 |
| Q1 | -0.4691 | -0.5136 | -0.0444 |
| Q3 | +0.4504 | +0.4268 | -0.0236 |
| min | -2.1912 | -2.1931 | -0.0019 |
| max | +2.7891 | +2.7891 | 0.0000 |
| count > 0.5 | 48 | 44 | -4 |
| count > 0.0 | 85 | 82 | -3 |
| count > -0.3 | 139 | 135 | -4 |

The aggregate shifts are small in absolute terms — mean -0.044, Q1 shifted by -0.04 and Q3 by -0.02, median unchanged. This batch's aggregate shift being modest does not imply the bug's general severity is modest; the bug's mechanism (carrying train-period equity into reported test-period metrics) still required correction, and future batches or future engine corrections may produce larger shifts. The "modest" descriptor here is a fact about *this* batch's pre-vs-corrected delta, not a claim about engine-correction impact in general.

At the candidate level, most rows were stable: 115/198 candidates had numerically unchanged Sharpe after correction, meaning the corrected test-period boundary did not change their aggregate reported Sharpe despite the full re-run; 58 dropped under correction; 25 rose; and only one candidate moved by more than 1.0 Sharpe (the maximum drop was -1.146; the maximum rise was +0.101). The directional asymmetry — more candidates dropped than rose, and the largest drops are larger than the largest rises — is consistent with the bug's mechanism: pre-test equity was entering the denominator and the reported test-period path, so correction can lower or raise reported Sharpe depending on the sign and timing of pre-test contamination. We infer the mechanism from the directional pattern rather than directly demonstrate it. Full per-candidate deltas are preserved in the corrected delta report rather than duplicated here.

The single outlier candidate that moved by more than 1.0 Sharpe is hash `ca5b4c3a` (`ema_crossover_momentum_surge`, theme `momentum`), which dropped from a pre-correction Sharpe of +0.7539 to a corrected Sharpe of -0.3921 — a delta of -1.146. This candidate is one of the four pre-correction binary winners (`wf_sharpe > 0.5`) that fall below the 0.5 threshold under correction. The other three flips were marginal: pre-correction Sharpes of +0.5158, +0.5245, and +0.6690 — all close enough to the threshold that small drops (Δ between -0.02 and -0.20) were sufficient to flip them. `ca5b4c3a` is the only flip with a substantively different classification: pre-correction +0.7539 was unambiguously above 0.5, corrected -0.3921 is clearly below. The four flips together produce the binary-criterion shift discussed in §4. Per-candidate analysis beyond identity-surfacing is out of scope for this erratum and lives in the corrected delta report.

---

## §4 Headline binary criterion amended

The original closeout's headline finding — "binary criterion strongly met" — survives under corrected walk-forward semantics with a small magnitude amendment. Under the original `wf_sharpe > 0.5` criterion, 48 of 198 candidates passed; under the corrected `wf_test_period_sharpe > 0.5` criterion, 44 of 198 pass. Of the 48 pre-correction binary winners, 44 (91.7%) remain above the 0.5 threshold under correction; 4 fall below, including the §3 outlier `ca5b4c3a` (the only one of the four with a substantively above-threshold pre-correction Sharpe; the other three were near-threshold).

The Phase 2C Phase 1 binary success criterion required at least 10 candidates with `wf_sharpe > 0.5`. The original closeout reported this as "STRONGLY MET" with 48 candidates clearing the threshold (4.8x the contractual minimum). Under correction, the criterion is **still strongly met** with 44 candidates clearing the threshold (4.4x the minimum). The qualitative claim survives: Phase 2C Phase 1 produced more than enough above-threshold candidates to satisfy the gate by a wide margin, both pre-correction and post-correction. The corrected count is the canonical figure going forward.

| Criterion | Pre-correction | Corrected | Status |
|---|---:|---:|---|
| Candidates with WF test-period Sharpe > 0.5 | 48 | 44 | survives |
| Threshold (≥10 required) | met (4.8x) | met (4.4x) | strongly cleared |
| Pre-correction winners retained | — | 44/48 (91.7%) | retained |
| Flipped candidates | — | 4 (3 near-threshold, 1 substantive: `ca5b4c3a`) | identified |

No re-adjudication of the Phase 2C Phase 1 acceptance verdict is required. The phase remains accepted; the corrected count is `44/198`.

---

## §5 RSI hypothesis re-test: null result, not falsification

The original closeout's §2.1 RSI-conditioning analysis argued that the proposer-level concern about RSI overuse was not supported by strategy-level walk-forward evidence, and characterized the hypothesis as "FALSIFIED." Under corrected walk-forward semantics, this claim requires both a numerical correction (the underlying correlation values shift slightly) and an epistemic correction (the "FALSIFIED" wording was over-claiming relative to the n=198 evidence at the time of writing, independent of the engine bug).

### §5.1 Numerical correction

The corrected correlation values move slightly closer to zero relative to the pre-correction values:

| Statistic | Pre-correction | Corrected | Δ |
|---|---:|---:|---:|
| Pearson(rsi_factor_count, Sharpe) | +0.024 | +0.0153 | -0.009 |
| Spearman (scipy, tie-corrected) | +0.043 | +0.0205 | -0.022 |
| with-RSI mean Sharpe (n=180) | +0.010 | -0.036 | -0.046 |
| without-RSI mean Sharpe (n=18) | -0.058 | -0.079 | -0.021 |

Both corrected correlation magnitudes are close enough to zero that they should be treated as no detectable linear or rank relationship in this batch. The with-RSI vs without-RSI mean Sharpe difference (-0.036 vs -0.079) describes this batch's split: the n=18 without-RSI subgroup is too small to support generalizable claims about RSI's effect on strategy performance, and the difference itself is well within the noise band for this batch's overall Sharpe distribution.

### §5.2 Epistemic correction

The original closeout's "RSI hypothesis FALSIFIED" wording was over-claiming at the time it was written. "Falsified" implies the data actively reject a hypothesis — that the evidence is inconsistent with the proposed effect to a degree that warrants rejecting it. The pre-correction Pearson +0.024 across n=198 did not support that strength of claim; what it supported was the weaker statement "no detectable relationship between RSI factor presence and walk-forward Sharpe at this sample size."

The corrected analysis surfaces this distinction more sharply (the corrected correlation is even closer to zero, reinforcing rather than weakening the null-result reading), but the over-claim was present in the original closeout's wording choice independent of the engine bug. Two distinct corrections are needed simultaneously: the engine produced contaminated metrics (corrected by the engine fix), and the original prose chose strong language for what was actually a null-evidence finding (corrected by the wording amendment).

The corrected wording for the load-bearing claim is:

> **Canonical wording (supersedes "FALSIFIED" in original §2.1):**
>
> The RSI hypothesis is not supported by this batch's evidence. The data show no meaningful correlation between RSI factor presence and walk-forward Sharpe at n=198. This is a null result, not a falsification: the absence of evidence for the hypothesis does not constitute evidence against it at this sample size.

This wording supersedes the "FALSIFIED" formulation in any future reference or downstream consumption. The amended claim does not change Phase 2C Phase 1's acceptance verdict (the RSI analysis was a hypothesis-conditioning sub-finding, not a load-bearing input to the acceptance gate).

---

## §6 Theme-quality differential survives directionally

The original closeout's §2.2 reported clear per-theme variation in walk-forward Sharpe, with mean_reversion strongest and momentum weakest. Under corrected walk-forward semantics, the rank ordering across the five themes is preserved 1-for-1, and the magnitude of the best-vs-worst gap widens slightly (0.834 pre-correction → 0.934 corrected, both in Sharpe units). Per-theme sample sizes are roughly balanced (39-40 candidates per theme), so cross-theme comparisons within this batch are not confounded by sample-size asymmetry.

| Theme | n | Pre-corr mean | Corrected mean | Δ mean | Pre >0.5 | Corr >0.5 |
|---|---:|---:|---:|---:|---:|---:|
| mean_reversion | 39 | +0.376 | +0.376 | 0.000 | 14 | 14 |
| volume_divergence | 40 | +0.081 | +0.042 | -0.039 | 13 | 12 |
| volatility_regime | 40 | +0.022 | -0.030 | -0.052 | 9 | 8 |
| calendar_effect | 40 | -0.004 | -0.033 | -0.029 | 7 | 7 |
| momentum | 39 | -0.459 | -0.558 | -0.099 | 5 | 3 |

Under corrected metrics, the gap and the rank ordering preserve the original closeout's directional finding. The phrase "large and consistent" should be read as a within-batch description of this specific candidate set, not as a generalizable property of the themes themselves; a different evaluation period, candidate set, or proposer batch could plausibly produce a different rank ordering or different magnitude.

The original closeout's §2.2 directional finding survives the correction; the momentum theme produces 3/39 above-threshold candidates under corrected metrics (vs the per-theme median of 8-12 above-threshold), reproducing the pattern that motivated the original §2.1+§2.2 combined inference about momentum-theme prompts being structurally degenerate. Whether that combined inference's policy implication (methodology iteration on momentum-theme prompts) is the right next move is a Phase 2 decision, not an erratum decision.

Unlike the RSI section, this finding needs a numerical refresh but not a wording downgrade: the corrected re-run supports the same within-batch directional interpretation as the original closeout.

---

## §7 Top-10 ranking stability

The top-10 candidates ranked by walk-forward Sharpe are stable under correction at the set level: 9 of the original top-10 candidates remain in the corrected top-10. The single substitution swaps one candidate out and one in:

- **Out:** `95bf56e7` (`macd_momentum_reversal`, theme `momentum`) — pre-correction rank #5 with Sharpe +1.490 → corrected Sharpe +1.104, falls to rank #16. The dropped candidate remains strong under correction (still well above the 0.5 binary criterion) but no longer ranks in the top-10, so this is a ranking-boundary change rather than a failure of the original top-tail signal.
- **In:** `f8e9655e` (`momentum_acceleration_rsi_181`, theme `momentum`) — pre-correction Sharpe just below the top-10 threshold → corrected Sharpe +1.335, enters at rank #10.

The table below is included for auditability; the load-bearing fact is the 9/10 overlap, not the exact within-top-10 ordering.

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

Internal reordering within the surviving 9 candidates is limited: rank #1 is unchanged; `cc295177` and `6059c88e` move up to #2 and #3; `b5e798dc` drops from #2 to #4; and pre-correction ranks #6-#10 mostly shift up one slot after `95bf56e7` exits.

The 9/10 overlap means that any future review that uses the original closeout's top-10 set as audit context will, with one specific exception (`95bf56e7` dropped, replaced by `f8e9655e`), find the same candidates in the corrected top-10. Internal rank ordering within the surviving 9 candidates shifts slightly (per the table above); downstream consumers that depend on specific rank positions, not just set membership, should consult the corrected rankings directly. Whether the corrected top-10 is the right input set for Phase 2 strategy-shortlist work is a Phase 2 decision, not an erratum decision. The corrected ranking is the canonical figure going forward; the pre-correction top-10 is preserved in the quarantined artifacts for historical reference only and must not be consumed.

---

## §8 Final amended conclusion and downstream consumption rules

### Amended conclusion

Phase 2C Phase 1 remains accepted under corrected walk-forward semantics. The synthesis across §3-§7:

- **§3 Distribution shape:** modest downward shift in aggregate Sharpe; median unchanged.
- **§4 Binary criterion:** amended from 48/198 to 44/198; still strongly clears the contractual ≥10 minimum.
- **§5 RSI hypothesis:** numerical correction plus epistemic correction (canonical wording: "null result, not supported" supersedes "FALSIFIED" in original §2.1).
- **§6 Theme-quality differential:** rank ordering across five themes preserved 1-for-1; mean_reversion strongest, momentum weakest.
- **§7 Top-10 ranking:** 9/10 set overlap; one specific candidate (`95bf56e7`) drops out, replaced by `f8e9655e` at rank #10.

The headline acceptance verdict from the original closeout — Phase 2C Phase 1 binary criterion strongly met, theme-quality differential a real signal, RSI overuse not supported as the actionable explanation in this batch — survives under correction with the specific amendments listed above. No re-adjudication of the phase's acceptance is required.

### Downstream consumption rules

All future consumption of Phase 2C Phase 1 walk-forward artifacts must follow these rules:

**Canonical artifacts (consume these):**
- `data/phase2c_walkforward/batch_b6fcbf86-4d57-4d1f-ae41-1778296b1ae9_corrected/walk_forward_results.csv`
- `data/phase2c_walkforward/batch_b6fcbf86-4d57-4d1f-ae41-1778296b1ae9_corrected/walk_forward_summary.json`
- `data/phase2c_walkforward/batch_b6fcbf86-4d57-4d1f-ae41-1778296b1ae9_corrected/PHASE2C_CORRECTED_DELTA_REPORT.md`

**Quarantined artifacts (must not be consumed):**
- `data/quarantine/pre_correction_wf/batch_b6fcbf86-4d57-4d1f-ae41-1778296b1ae9_STALE_PRE_CORRECTION/`
- Any walk-forward artifact whose producing commit is not descended from `eb1c87f`, or whose summary lacks `wf_semantics='corrected_test_boundary_v1'` (per Section RS hard prohibition in `docs/decisions/WF_TEST_BOUNDARY_SEMANTICS.md`).

**Consumer-side enforcement:**
- All code that consumes corrected-engine walk-forward summaries must call `backtest.wf_lineage.check_wf_semantics_or_raise()` against the loaded summary dict before computing any derived metrics.
- The expected enforcement pattern is: load `walk_forward_summary.json` → call `check_wf_semantics_or_raise()` → only then load or join the corresponding CSV. Validating the summary while consuming an adjacent stale CSV defeats the contract.
- The four downstream techniques flagged in `strategies/TECHNIQUE_BACKLOG.md` — PBO §2.2.2, DSR §2.2.3, CPCV §2.2.4, MDS §2.4.1 — already cross-reference this enforcement helper per Task 10a (commit `0e368a8`); any new technique consuming Phase 2C corrected artifacts must do the same.

**Citation discipline:** any future reference to Phase 2C Phase 1 numbers (in plans, blueprints, technique-backlog entries, or new closeouts) must cite the corrected figures from this erratum, not the pre-correction figures from the original closeout. Citations should reference the corrected figure directly with the erratum as source — for example, "Phase 2C Phase 1 binary criterion: 44/198 corrected (per `docs/closeout/PHASE2C_5_PHASE1_RESULTS_ERRATUM.md` §4)" rather than citing only the document path. The original closeout file is preserved unmodified for historical reproducibility but is no longer the canonical reference for Phase 2C Phase 1 numerical claims.

### Closing note

A process-level lesson from this erratum is that closeout language should distinguish "not supported" from "falsification" unless the evidence directly supports rejection. The §5.2 epistemic correction was needed independently of the engine bug; the bug surfaced it more sharply but did not introduce it.

---

## §9 References

### Documents

- Original closeout (preserved unmodified): [`docs/closeout/PHASE2C_5_PHASE1_RESULTS.md`](PHASE2C_5_PHASE1_RESULTS.md) (commit `861d186`, 2026-04-26)
- Decision document: [`docs/decisions/WF_TEST_BOUNDARY_SEMANTICS.md`](../decisions/WF_TEST_BOUNDARY_SEMANTICS.md) — full bug analysis, corrected semantic, Section RS hard prohibition
- Phase 1B canonical baselines: [`data/phase1b_corrected/phase1b_corrected_v1/BASELINE_NUMBERS.md`](../../data/phase1b_corrected/phase1b_corrected_v1/BASELINE_NUMBERS.md)
- Phase 1B corrected baseline supplement: [`docs/closeout/PHASE1B_WF_CORRECTED_BASELINE_SUPPLEMENT.md`](PHASE1B_WF_CORRECTED_BASELINE_SUPPLEMENT.md) (commit `9d1c722`)
- Technique backlog (with corrected-engine dependency lines): [`strategies/TECHNIQUE_BACKLOG.md`](../../strategies/TECHNIQUE_BACKLOG.md) — PBO §2.2.2, DSR §2.2.3, CPCV §2.2.4, MDS §2.4.1

### Artifacts

- **Corrected batch (canonical):** `data/phase2c_walkforward/batch_b6fcbf86-4d57-4d1f-ae41-1778296b1ae9_corrected/`
  - `walk_forward_results.csv`
  - `walk_forward_summary.json`
  - `PHASE2C_CORRECTED_DELTA_REPORT.md`
- **Quarantined batch (must not be consumed):** `data/quarantine/pre_correction_wf/batch_b6fcbf86-4d57-4d1f-ae41-1778296b1ae9_STALE_PRE_CORRECTION/`

### Code modules

- Lineage guard: [`backtest/wf_lineage.py`](../../backtest/wf_lineage.py) — `enforce_corrected_engine_lineage()` (producer-side), `check_wf_semantics_or_raise()` (consumer-side), canonical constants `CORRECTED_WF_ENGINE_COMMIT='eb1c87f'`, `WF_SEMANTICS_TAG='corrected_test_boundary_v1'`
- Engine: [`backtest/engine.py`](../../backtest/engine.py) — `run_walk_forward()` with corrected test-boundary semantic
- Phase 2C runner: [`scripts/run_phase2c_batch_walkforward.py`](../../scripts/run_phase2c_batch_walkforward.py) — lineage-guard-anchored, uses `wf_test_period_*` field names
- Lineage tests: [`tests/test_wf_lineage_guard.py`](../../tests/test_wf_lineage_guard.py) — 9 tests covering producer guard, CWD anchor, consumer helper

### Git commits

- `eb1c87f` — engine fix (corrected test-boundary semantic in `backtest/engine.py`)
- `3d24fcb` — corrected-engine tag anchor (`wf-corrected-v1` tag target; CWD-anchor reliability fix in lineage guard)
- `a22051e` — Task 10b refactor: `wf_*` → `wf_test_period_*` field rename in Phase 2C runner
- `0e368a8` — Task 10a: corrected-engine dependency lines added to PBO/DSR/CPCV/MDS backlog entries
- `e93bffd` — Task 8a: Phase 1B corrected canonical baselines
- `9d1c722` — Task 8b: Phase 1B WF corrected baseline supplement
- `861d186` — original Phase 2C Phase 1 closeout (preserved unmodified)

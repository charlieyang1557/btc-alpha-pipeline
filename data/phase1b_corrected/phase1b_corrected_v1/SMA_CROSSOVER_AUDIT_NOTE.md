# sma_crossover Pre-Correction Registry Rows — Audit Context Only

`backtest/experiments.db` contains historical `walk_forward_summary` rows for `sma_crossover` under `split_version='v2'` that pre-date the corrected WF engine commit `eb1c87f`. These rows are NOT treated as sealed canonical baselines — the original Phase 1 closeout (`docs/closeout/PHASE1_SIGNOFF.md`) only published single-run 2024 H1 Sharpe numbers, not v2 walk-forward aggregates. The pre-correction v2 WF rows below are listed only for audit completeness; they are NOT used as delta anchors against the corrected canonical numbers in `BASELINE_NUMBERS.md` (this directory).

The other three Phase 1B baselines (`momentum`, `mean_reversion`, `volatility_breakout`) have NO pre-correction v2 WF rows in the registry, so no audit note is needed for them — the corrected runs in this batch are their first authoritative v2 WF publications.

## Pre-correction rows (audit context only — NOT canonical)

| run_id | git_commit | created_at_utc | total_return | sharpe_ratio | total_trades |
|---|---|---|---|---|---|
| `434c1298-336c-4df1-a966-34d455386145` | `503c9c3` | 2026-04-18T03:29:20Z | 1.5711 | 0.1763 | 95 |
| `1e312f0a-d85b-4205-845d-fa2b926fd974` | `0531741` | 2026-04-26T06:46:43Z | 1.5711 | 0.1763 | 95 |
| `dbac6fcd-08a0-464a-a45f-8b38362d160c` | `6a9b78f` | 2026-04-26T12:44:23Z | 0.0022 | -0.1147 | 95 |

## Corrected canonical rows (this batch — these ARE the canonical numbers)

| run_id | git_commit | created_at_utc | total_return | sharpe_ratio | total_trades |
|---|---|---|---|---|---|
| `e403270c-d1b5-460b-ad6e-a298dd1a4a53` | `a22051e` | 2026-04-27T01:26:00Z | 0.0022 | -0.1147 | 95 |
| `926b2641-1db3-4f0b-91a7-c5c9896a3e37` | `a22051e` | 2026-04-27T01:27:22Z | 0.0022 | -0.1147 | 95 |

(The two `a22051e` rows are the Task 8a primary run and the determinism-check rerun; both reproduce the same numbers bit-identically.)

## Provenance notes (no overclaiming)

These rows pre-date the corrected WF semantics commit `eb1c87f` and are not lineage-valid under tag `wf-corrected-v1`. Therefore they are not valid canonical baselines under Section RS of `docs/decisions/WF_TEST_BOUNDARY_SEMANTICS.md`.

The first two pre-correction rows (`503c9c3` and `0531741`) report identical numbers (Sharpe 0.1763, return 1.5711). Engine code in `backtest/engine.py` was unchanged between these two commits — they reflect the same engine state run at different times.

The third pre-correction row (`6a9b78f`) reports different numbers (Sharpe -0.1147, return 0.0022). Verification via `git diff 0531741 6a9b78f -- backtest/` confirms `backtest/engine.py` was NOT modified between `0531741` and `6a9b78f` (only `scripts/run_phase2c_batch_walkforward.py` changed substantially during Phase 2C Phase 1 work). The differing Sharpe values therefore do not reflect an engine change; they likely reflect different run parameters (different `--force` overwrite state, different cash, different `overall_start`/`overall_end`, or different walk-forward config) at run time. The exact run-parameter delta is not preserved in the registry. **No directional claim is made here about which row is "more correct" or whether the broken engine "inflated" or "deflated" Sharpe** — the evidence does not support such a claim, since both 0.1763 and -0.1147 were produced by the same engine code under different run conditions.

The corrected canonical sma_crossover v2 WF Sharpe (Task 8a primary run + determinism check, both at commit `a22051e`) is **-0.1147**, identical to the third pre-correction row. This identity is informative: it suggests the third pre-correction row was produced under the corrected-by-coincidence run parameters (specifically, parameters that happened to produce post-correction-equivalent output even though the engine itself was pre-correction). Without preserved run-parameter context, this remains a hypothesis rather than a proven claim.

## Why this audit note exists

A future engineer running

```sql
SELECT * FROM runs WHERE strategy_name = 'sma_crossover' AND run_type = 'walk_forward_summary';
```

against `backtest/experiments.db` will see five rows for `sma_crossover` v2 walk-forward: three pre-correction, two post-correction. Without this audit note, they would have no way to distinguish which rows are canonical (the post-correction `a22051e` rows) vs which are historical artifacts (the three earlier rows). The note disambiguates.

This audit note does NOT modify the registry — pre-correction rows are preserved in place for reproducibility of historical runs. The canonical reference for which rows are valid baselines is this document plus `BASELINE_NUMBERS.md` in the same batch directory.

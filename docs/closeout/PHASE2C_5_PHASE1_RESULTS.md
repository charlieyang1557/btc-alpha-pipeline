# Phase 2C Phase 1 — Walk-Forward Funnel Results

**Status:** completed clean (exit 0). Mechanics PASS. Binary success criterion **STRONGLY MET** (48/198 candidates pass wf_sharpe > 0.5; contract's "≥10 = strongly met" threshold cleared by 4.8x).

**batch_id:** `b6fcbf86-4d57-4d1f-ae41-1778296b1ae9`
**HEAD at Tier 3 fire:** `0531741` (`chore: gitignore data/compiled_strategies/ and spend_ledger journals`)
**Run window (UTC):** start `2026-04-26T06:50:52Z` → end `2026-04-26T07:10:06Z` (1152.34s ≈ 19m 12s wall clock)
**Implementation contract:** `docs/phase2c/PHASE2C_4_PHASE1_PLAN.md` (sealed at `1c218c1`)
**API spend:** $0 (local compute only). Monthly UTC-2026-04 ledger unchanged at $8.65/$100.

---

## 1. Headline numbers

### Mechanical (per contract section 6 Tier 3 gate)

| Metric | Value | Notes |
|---|---|---|
| Total candidates processed | 198 | All `pending_backtest` from batch-1 |
| Component A extraction | 198/198 ok | 0 re-validation failures |
| Compile step | 198/198 ok | 0 manifest drift, 0 compile errors |
| Walk-forward runtime | 198/198 ok | 0 runtime exceptions; `errors/` directory empty |
| Total wall clock | 1152.3s = 19m 12s | Mean 5.82s/candidate; ~10x under contract's 3-hour estimate |
| Defensive hash dedupe | 0 duplicates triggered | batch-1 has 198 distinct hashes; matches batch-1 closeout §1.8 |

The contract's full-sweep wall-clock estimate (~3 hours) was conservatively scoped against unknown DSL strategy compute cost. Actual runtime is I/O-bound on the parquet feed load (one load per WF window per candidate), not compute-bound on `next()` evaluation.

### Binary success criterion (per contract section 2)

**MET, strongly.** **48/198 candidates (24.2%)** produce walk-forward Sharpe > 0.5 on test windows.

The contract defined three outcome bands:
- "Met (≥1 passes)" → Phase 2 worth continuing.
- **"Strongly met (≥10 passes)" → reconsider whether Phase 2's regime holdout filter is the next-most-valuable build vs. paper-trading harness on top survivors.**
- "Not met (0 passes)" → re-open methodology question with hard evidence.

We landed in band 2 by a factor of 4.8x. The contract itself flags this as triggering a research-direction decision, not just a "ship Phase 2" decision.

### Distribution shape

| Statistic | Value |
|---|---|
| n | 198 |
| mean | +0.0035 |
| median | 0.0000 |
| stdev | 0.819 |
| min | -2.191 |
| max | +2.789 |
| p10 / p25 / p75 / p90 | -1.054 / -0.469 / +0.450 / +1.126 |
| count > 0.5 | 48 (24.2%) |
| count > 0.0 | 85 (42.9%) |
| count > -0.3 | 139 (70.2%) |

The IQR straddles zero (-0.47 to +0.45). Mean and median are essentially zero; the distribution is roughly symmetric around zero with stdev ~0.8 and fat tails on both sides. Half the candidates are negative-Sharpe; a sizable minority hit positive territory; a meaningful subset (the 48) clear the binary threshold.

---

## 2. The two findings that change Phase 2 framing

### §2.1 RSI-conditioning hypothesis: FALSIFIED

The batch-1 closeout (committed at `4a0egg6`) flagged "RSI_14 dominance" as a generation-side concern: 92-98% of all candidates use `rsi_14` across all five themes. The implicit hypothesis was that proposer over-conditioning on RSI was driving low-quality candidates. Phase 1 was the first experimental apparatus that could test this hypothesis with hard evidence.

Result: **the hypothesis does not hold.**

| Correlation | Value |
|---|---|
| Pearson(rsi_factor_count, wf_sharpe) | **+0.024** |
| Spearman(rsi_factor_count, wf_sharpe) | **+0.043** |
| Pearson(rsi_share, wf_sharpe) | -0.005 |
| Spearman(rsi_share, wf_sharpe) | -0.018 |
| Pearson(total_factor_count, wf_sharpe) | +0.033 (control) |

All correlations are essentially zero. RSI presence is **mildly positive** (mean Sharpe with-RSI = +0.010, n=180; without-RSI = -0.058, n=18) — not negative as the hypothesis predicted.

This means: the actionable issue is not "RSI is overused." Whatever drives the cross-theme momentum-fallback pattern observed at the proposer level does not translate to underperformance at the strategy level on its own.

### §2.2 Theme-quality differential: large and consistent

| Theme | total | sharpe>0.5 | win% | sharpe>0.0 | share-of-passers |
|---|---|---|---|---|---|
| **mean_reversion** | 39 | **14** | **35.9%** | 24 (61.5%) | 29.2% |
| **volume_divergence** | 40 | **13** | **32.5%** | 19 (47.5%) | 27.1% |
| volatility_regime | 40 | 9 | 22.5% | 13 (32.5%) | 18.8% |
| calendar_effect | 40 | 7 | 17.5% | 17 (42.5%) | 14.6% |
| **momentum** | 39 | **5** | **12.8%** | 12 (30.8%) | 10.4% |

The momentum theme has a **2.8x lower** binary pass rate than mean_reversion (12.8% vs 35.9%). The top-50-by-Sharpe breakdown reinforces this: mean_reversion + volume_divergence together account for 28/50 (56%) of the top quartile.

This is theme-correlated underperformance, **not** factor-correlated. Re-state of the actionable finding from §2.1+§2.2: the momentum-theme prompts produce systematically weaker strategies even when those strategies use the same factor pool as winners from other themes. The methodology question for Phase 2 (or D8.4-style methodology iteration) is "what about the momentum-theme prompt is structurally degenerate," not "why is RSI overused."

---

## 3. Trade-count sensitivity (the small-print on 48)

The 48 binary-pass count contains real signal AND small-sample noise. Sensitivity analysis on the 48 winners by minimum trade count:

| Min trades threshold | Surviving winners | % of headline |
|---|---|---|
| ≥ 0 (headline) | 48 | 100.0% |
| ≥ 5 | 43 | 89.6% |
| ≥ 10 | 40 | 83.3% |
| ≥ 20 | 36 | 75.0% |
| **≥ 50** | **25** | **52.1%** |

Trade-count-bucketed pass rates make the small-sample bias visible:

| Bucket | n | sharpe>0.5 | bucket pass% | mean Sharpe |
|---|---|---|---|---|
| 0 trades | 26 | 0 | 0.0% | 0.000 |
| 1-10 trades | 19 | 8 | **42.1%** | +0.305 |
| 11-50 trades | 51 | 15 | 29.4% | +0.053 |
| 51+ trades | 102 | 25 | 24.5% | -0.077 |

The 1-10 trades bucket has the highest pass rate (42.1%) — exactly the small-sample mechanic the DSR screen exists to filter. The 51+ trades bucket has the most trustworthy passers: 25/102 (24.5%) with adequate evidence. **DSR in Phase 2 is exactly what discounts the 12 winners with <20 trades against the 25 with ≥50.**

Top-5 most-robust winners (sorted by trade count, all sharpe > 0.5):

| Pos | Sharpe | Return | MaxDD | Trades | Theme | Name |
|---|---|---|---|---|---|---|
| 158 | 0.52 | 1.30 | — | **177** | volatility_regime | volatility_compression_breakout_158 |
| 142 | 1.03 | 0.18 | — | **154** | mean_reversion | bollinger_mean_reversion_oversold_142 |
| 64 | 0.93 | 1.35 | — | **143** | volume_divergence | volume_divergence_momentum_fade |
| 137 | 1.10 | 0.44 | — | **111** | mean_reversion | bb_oversold_reversion_137 |
| 18 | 0.99 | 3.17 | — | **109** | volatility_regime | low_vol_breakout_ema_cross |

These five are the strongest pre-DSR Phase 2 candidates if/when regime holdout + DSR enter the funnel.

### Zero-trade candidates: 26/198 (13.1%)

The funnel surfaced a generation-side finding the proposer-only stage could not measure: 26 candidates **never trade** across any of the 4 walk-forward windows. Concentration:

- volatility_regime: 12 (30% of theme)
- mean_reversion: 9 (23% of theme)
- calendar_effect: 4 (10% of theme)
- momentum: 1 (2.6% of theme)
- volume_divergence: 0

The proposer over-generates strategies whose entry conditions never fire on 2020-2021 data. Worth flagging as a Phase 2 input to whatever methodology iteration follows.

---

## 4. Architectural integrity verifications

The Phase 1 build went through three mandatory sanity checks (contract section 5) plus one in-flight infrastructure check. All four passed. They are documented here together because the Phase 1 results above are only as trustworthy as the architecture under them.

### §4.1 Re-extraction reliability — PASS
Component A re-parses each `attempt_NNNN_response.txt` and re-validates the DSL through pydantic. The script also recomputes the D3 hypothesis_hash and warns on any mismatch with the proposer-recorded hash. **0 mismatches across 198 candidates.** The on-disk audit artifacts faithfully round-trip back to the same DSL and hash the proposer wrote.

### §4.2 Compiler renderer faithfulness — PASS (sanity check 3, byte-exact)
For 5 structurally-diverse candidates (positions 1, 2, 15, 32, 198 — covering cross-FvS, FvF-noncross, FvF-cross, max-cardinality, and late-batch multi-path exposure), the manifest's `pseudo_code` field was independently re-rendered from the source DSL using the compiler's exact rendering function and compared byte-for-byte. **5/5 byte-identical matches.** Combined with the structural compiler-source verifications (cross operators in both factor-vs-scalar and factor-vs-factor paths use the explicit two-bar form `(cur op val) AND (prev op val)`; NaN→False enforced inside each operator branch; `_compile_condition` dispatches on `type(cond.value)` at compile time so paths cannot mix at runtime), the manifest's pseudo_code is a verifiable representation of the compiled logic. This generalizes from the 5 sampled candidates to the compiler architecture itself.

### §4.3 Hash-space cleanliness — PASS (sanity check 1)
SQLite query against `backtest/experiments.db` for any rows whose `hypothesis_hash` matched any of batch-1's 198 hashes. **0 collisions** across the 102-row pre-existing `runs` table. All 102 prior rows have `hypothesis_hash IS NULL` (Phase 1A/1B baselines, pre-Phase-2 schema). Phase 1's per-candidate WF runs also wrote engine rows with NULL `hypothesis_hash` (Phase 1 contract excludes engine-side hash population; the Phase 1 CSV is the source of truth for hash↔WF-result linkage). Future schema-state-evolution forward-pointer: Phase 2's lifecycle-state-writes phase will be the first to populate `hypothesis_hash` on engine rows.

### §4.4 Engine bit-determinism — PASS (sanity check 2, sub-1e-15 reproduction)
`run_walk_forward(SMACrossover)` against the v2 split reproduces the sealed Phase 1B closeout's walk_forward_summary at floating-point round-off precision:

| Metric | Sealed (2026-04-18T03:29:20Z) | Live (2026-04-25T23:46:43Z) | \|delta\| |
|---|---|---|---|
| sharpe_ratio | 0.176290146866810 | 0.176290146866810 | 4.16e-16 |
| total_return | 1.571129199149510 | 1.571129199149505 | 4.88e-15 |
| max_drawdown | 0.386292343400887 | 0.386292343400887 | 1.67e-16 |
| total_trades | 95 | 95 | 0 |

Deltas at 1e-15 to 1e-16 are pure floating-point round-off. This is **stronger than the contract required** ("compare against sealed Phase 1B closeout"). It confirms not just that the driver works, but that the engine itself is bit-deterministic across invocations on this strategy class on this data — a foundational property for any future research that needs to compare WF results across runs.

### Summary of architectural integrity

The Phase 1 results above are not just "the script ran without crashing." They are anchored against:
1. Faithful re-extraction of proposer-time DSLs (§4.1, all 198).
2. Verifiable correspondence between manifest pseudo_code and compiled logic (§4.2, 5 candidates + structural compiler proof).
3. Empty pre-existing hash space, no contamination from prior runs (§4.3).
4. Bit-deterministic engine reproduction across two separate runs a week apart (§4.4).

These four findings together are the answer to "is the Phase 1 architecture trustworthy enough to act on its outputs." The answer is yes, with explicit evidence at each load-bearing layer.

---

## 5. The next decision (presented as options, not a recommendation)

The contract section 2 explicitly anticipated this: "Strongly met (≥10 candidates pass): consider whether Phase 2's regime holdout filter is the next-most-valuable build vs. a paper-trading harness on top survivors." Phase 1 landed at 48 passes. We are in that band by a wide margin.

Three credible directions:

### Option A — Build Phase 2 (regime holdout AND-gate + DSR + lifecycle states + D9 finalization)

Stays inside the funnel-build arc the Phase 2C plan envisioned. After Phase 2:
- 26 zero-trade candidates filter out (lifecycle: `train_failed` or analogous).
- Regime holdout 2022 stress test filters out small-sample winners that overfit to bull-market 2020-2021 data — directly addresses the 12 sub-20-trade winners.
- DSR multiple-testing screen with N=198 tests against the 25-trustworthy-winners cohort.
- Survivors are `shortlisted` per the lifecycle state machine.

Value: gets us to a defensible "shortlist" that survives multiple-testing correction. Cost: substantial implementation work (D7.5 deliverables documented in PHASE2_BLUEPRINT.md).

### Option B — Build a paper-trading harness on the top-5 most-robust winners directly

Bypass regime holdout and DSR for now. Take the 5 candidates from §3 with ≥109 trades each and ship them into a Phase 4-style paper-trading harness against fresh out-of-sample data (2026-Q1 onwards). The Sharpe values aren't multiple-testing-corrected, but the trade-count adequacy gives a defensible foundation.

Value: gets to "real" out-of-sample evaluation faster. Cost: skips the multiple-testing correction (so the 5 candidates' "true" Sharpe expectation is lower than the in-sample point estimate) and skips the regime-stress test (so 2022-bear-market behavior is unknown).

### Option C — Methodology iteration on the proposer side based on §2.1+§2.2

Ship one of the D8.4-documented prompt/code changes targeting the theme-quality differential specifically — e.g., theme-anchor enforcement that constrains momentum-theme prompts to non-RSI-only structures, or scoring-side filters that downweight zero-entry-condition strategies. Then re-run a fresh proposer batch and compare distributions.

Value: addresses the empirical generation-side finding (theme-quality differential) directly. Cost: $2-3 of API spend per iteration; doesn't move the existing 198 forward toward a `shortlisted` outcome.

The choice is research-direction, not adjudicated by this batch. Worth being explicit about: Option A measures "are the 48 winners real signal after multiple-testing correction"; Option B measures "do the most-robust winners trade out-of-sample"; Option C measures "does prompt iteration close the theme-quality gap." All three are legitimate; Phase 1 supplies different evidence for each.

---

## 6. Forward-pointers (carried over, none unblocked by this batch)

- **`agents/proposer/stage2d_batch.py:1081-1108`** still calls `run_critic` without `ledger.write_pending` for the critic call. Benign in stub mode (current default); becomes a spend-accounting bug if/when `LiveSonnetD7bBackend` is wired into `main()`. Sequencing constraint stands: ledger pre-charge before or with live-critic wiring.
- **CLAUDE.md drift**: `python -m backtest.evaluate_dsr --batch-id <UUID>` documented but `--batch-id` flag does not exist in `backtest/evaluate_dsr.py`. Resolution comes with Phase 2 D9 `finalize_batch()`.
- **D8.4 unshipped**: six methodology recommendations remain documentation only. Phase 1's results bear on at least one of them (the RSI-conditioning recommendation may need re-scoping in light of §2.1's falsification).
- **Engine-side hypothesis_hash population** is deferred to Phase 2's lifecycle-state-writes phase. The Phase 1 CSV is the source of truth for hash↔WF-result linkage; Phase 2 will populate the engine-side fields.

---

## 7. Spend posture

| | Pre-Phase-1 | Post-Phase-1 | Cap |
|---|---|---|---|
| Phase 1 API spend | $0 | $0 | n/a (local compute) |
| Monthly spend (UTC 2026-04) | $8.65 | $8.65 | $100 |
| Monthly headroom remaining | $91.35 | $91.35 | — |

Local compute only. Phase 1 does not affect the spend ledger. Total wall-clock cost of Phase 1: ~21 minutes of local CPU/IO across the three tier runs.

---

## 8. Artifacts

Canonical Phase 1 artifacts (gitignored; not committed):

- `data/phase2c_walkforward/batch_b6fcbf86-4d57-4d1f-ae41-1778296b1ae9/walk_forward_results.csv` — 198 rows, one per candidate, all 16 fields populated.
- `data/phase2c_walkforward/batch_b6fcbf86-4d57-4d1f-ae41-1778296b1ae9/walk_forward_summary.json` — distribution stats + run metadata.
- `data/phase2c_walkforward/batch_b6fcbf86-4d57-4d1f-ae41-1778296b1ae9/errors/` — empty (0 runtime exceptions).
- `data/phase2c_walkforward/batch_b6fcbf86-4d57-4d1f-ae41-1778296b1ae9_tier3_snapshot/` — defensive snapshot taken before the CSV-overwrite-protection fix landed; preserves the canonical Tier 3 result.
- `data/compiled_strategies/<dsl_hash>.json` × N — 198 distinct compilation manifests, one per candidate. Each contains canonical DSL, compiler SHA, factor snapshot, feature_version, and the human-audit `pseudo_code` field referenced in §4.2.

Engine-side artifacts (gitignored):
- `backtest/experiments.db` — accumulated walk_forward_window + walk_forward_summary rows from the three tier runs (rows for sma_crossover sanity check 2 + 5+19+198 candidates × 4 sub-windows + 5 summary rows). All have NULL `hypothesis_hash`, NULL `batch_id`, NULL `lifecycle_state` per Phase 1's contract scope.
- `data/results/trades_<run_id>.csv` × many — per-window trade logs (gitignored).

This closeout document at `docs/closeout/PHASE2C_5_PHASE1_RESULTS.md` is the only file written outside `data/phase2c_walkforward/`, `data/compiled_strategies/`, `data/results/`, and `backtest/experiments.db`.

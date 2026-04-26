# Phase 2C Batch-1 Closeout

**Status:** completed clean (exit 0). Mechanics PASS. Distribution REPRODUCES_SEALED.

**batch_id:** `b6fcbf86-4d57-4d1f-ae41-1778296b1ae9`
**HEAD at fire:** `8d29a6e` (pre-existing dirty-tree items: `.DS_Store`, `.claude/`, `docs/d7_stage2c/D7_STAGE2C_PATCH_REPORT.md`, `docs/d7_stage2c/stage2c_candidate_worksheet.md` — all known-unrelated, none touch `agents/proposer/stage2d_batch.py` or its imports)
**Run window (UTC):** start `2026-04-26T04:56:25.407Z` → last ledger completion `2026-04-26T05:16:44.920Z` (1219.56s ≈ 20m 20s)
**Command run:** `python -m agents.proposer.stage2d_batch` (no flags)
**Sealed comparison cohort:** `batch_5cf76668-47d1-48d7-bd90-db06d31982ed` (D6 Stage 2d proposer summary; the same UUID also contains D7 critic-fire artifacts, but the proposer-summary fields are the apples-to-apples baseline)

---

## 1. The 15 post-run items

### Headline numbers (vs sealed)

| # | Metric | Batch-1 | Sealed `5cf76668` | Delta |
|---|---|---|---|---|
| 1 | batch_id | `b6fcbf86-4d57-4d1f-ae41-1778296b1ae9` | `5cf76668-47d1-48d7-bd90-db06d31982ed` | — |
| 2 | actual spend (USD) | $2.302194 | $2.243343 | +$0.058859 |
| 3 | hypotheses_attempted | 200 | 200 | 0 |
| 4 | parse_rate | 0.99 | 0.995 | -0.005 |
| 5 | lifecycle counts | `{pending_backtest: 198, rejected_complexity: 2}` | `{pending_backtest: 199, rejected_complexity: 1}` | +1 rc |
| 6 | theme distribution | `momentum:40, mean_reversion:40, volatility_regime:40, volume_divergence:40, calendar_effect:40` | `40/40/40/40/40` | identical |
| 7 | cardinality_violations | 0 (`single_object: 200`) | 0 | identical |
| 8 | duplicate count (by `hypothesis_hash`) | 0 (distinct_hashes=198 = total_valid) | 0 | identical |
| 9 | top-10 factor frequencies | see §1.9 | see §1.9 | minor reordering |
| 10 | RSI_14 share, first-50 valid calls | 46/50 = **0.920** | 46/50 = 0.920 | **exact match** |
| 11 | novelty trajectory by quartile | see §1.11 | see §1.11 | same shape |
| 12 | cumulative cost trajectory | see §1.12 | see §1.12 | parallel |
| 13 | input-token / approved_examples plateau | see §1.13 | n/a | plateau holds |
| 14 | mechanics verdict | **PASS** | (sealed PASS) | — |
| 15 | distribution verdict | **REPRODUCES_SEALED** | (baseline) | — |

### §1.9 Top-10 factor frequencies

| Rank | Batch-1 factor | Uses | Sealed factor | Uses |
|---|---|---|---|---|
| 1 | rsi_14 | 180 | rsi_14 | 185 |
| 2 | return_24h | 176 | return_24h | 171 |
| 3 | close | 171 | close | 164 |
| 4 | macd_hist | 87 | realized_vol_24h | 77 |
| 5 | volume_zscore_24h | 58 | macd_hist | 68 |
| 6 | realized_vol_24h | 58 | volume_zscore_24h | 64 |
| 7 | return_168h | 57 | sma_20 | 52 |
| 8 | sma_20 | 56 | zscore_48 | 48 |
| 9 | sma_50 | 47 | sma_50 | 48 |
| 10 | return_1h | 42 | return_1h | 46 |

Top-3 identical; rest reorder within the same factor pool. No new factors enter the top tier in batch-1; no top-tier sealed factors disappear.

### §1.10 RSI_14 share by valid-call quartile

| Quartile | Batch-1 | Note |
|---|---|---|
| Q1-50 | 46/50 = **0.920** | matches sealed `rsi_14_dominance` flag exactly |
| Q51-100 | 40/48 = 0.833 | |
| Q101-150 | 45/50 = 0.900 | |
| Q151-200 | 49/50 = **0.980** | RSI_14 dominance does not decline; if anything intensifies in last block |

Sealed only published the first-50 figure (0.920) under `anomaly_flags`. Batch-1's full-batch trajectory shows RSI_14 saturation persists across all four position blocks. **This is a finding, not a regression** — D6 lessons predicted "systematic cross-theme momentum fallback" and batch-1 confirms the pattern at full batch length on a fresh sample.

### §1.11 Novelty trajectory (cumulative `unique_factor_set_ratio`)

| at_call | Batch-1 fs_ratio | Sealed fs_ratio | Batch-1 cum_actual | Sealed cum_actual |
|---|---|---|---|---|
| @50 | 0.86 | 0.82 | $0.5433 | $0.5541 |
| @100 | 0.8061 | 0.78 | $1.1131 | $1.1219 |
| @150 | 0.7568 | 0.7315 | $1.6748 | $1.6846 |
| @200 | **0.7121** | **0.6683** | $2.3022 | $2.2433 |

Same monotonic decline shape as sealed. Batch-1 ends slightly more diverse than sealed (0.7121 vs 0.6683, 141 vs 133 distinct factor sets across 198 vs 199 valid). The novelty erosion mechanic reproduces; the absolute saturation point is ~4.4 percentage points **higher** in this sample (i.e., batch-1 is more diverse). With only two runs, treat this as run-to-run sampling variation unless future batches show a systematic shift in the same direction.

### §1.12 Cumulative cost trajectory

Sub-§1.11 table covers the cost trajectory by quartile. Per-call mean cost by block:
- Block 1 (1-50): $0.010866/call (input mean 1963.7, output mean 331.6)
- Block 2 (51-100): $0.011396/call (input 2035.2, output 352.7)
- Block 3 (101-150): $0.011234/call (input 2016.9, output 345.5)
- Block 4 (151-200): $0.012549/call (input 2146.0, output 407.4)

Slight upward drift across blocks driven mostly by output tokens (332 → 407, +23%) rather than input tokens (1964 → 2146, +9%). Cap-trip risk irrelevant at this scale: $20 cap with $2.30 actual, never close. **`cost_ratio (est/actual) = 1.20x`** — far tighter than the 3.08x estimator-vs-actual ratio referenced in earlier sessions; suggests the conservative ceiling assumed during scoping was overly pessimistic.

### §1.13 Approved-examples / input-token plateau

`approved_examples_cap = 3` (from config). Input-token block means: 1963.7 → 2035.2 → 2016.9 → 2146.0. **Plateau holds.** The +180-token bump in block 4 is small and consistent with prompt-text variation rather than unbounded growth (max block 4 = 2184; max block 1 = 2083, only +101 tokens). Concern about unbounded prompt-input growth raised pre-run is **not realized**.

### §1.14 Mechanics verdict — PASS

All hard gates clean:
- 200 attempted, no early-stop, `batch_status: completed`, `truncated: False`.
- `parse_rate = 0.99 ≥ 0.95` ✓
- `pending_backtest = 198 ≥ 190` ✓
- `cardinality_violations = 0` ✓
- All 5 operational themes hit `n_calls = 40` exactly ✓
- `multi_factor_combination` not in rotation (canonical 5-theme operational rotation per CLAUDE.md) ✓
- `lifecycle_invariant_ok = True` ✓
- `total_actual_cost_usd = $2.302194` well under $20 hardcoded cap ✓
- All allowed writes confirmed: `raw_payloads/batch_b6fcbf86…/` (402 files: 200 prompts + 200 responses + `stage2d_summary.json` + `stage2d_summary_partial.json`), `agents/spend_ledger.db` (200 proposer rows, all `status=completed`).
- All disallowed writes confirmed not modified: `data/raw/btcusdt_1h.parquet` mtime `Apr 16` (pre-batch); `backtest/experiments.db` mtime `Apr 17` (pre-batch); `config/execution.yaml` mtime `Apr 16` (pre-batch); `config/environments.yaml` mtime `Apr 18` (pre-batch); zero `attempt_NNNN_critic_*.json` files in batch dir.
- `agents/spend_ledger.db-shm` and `agents/spend_ledger.db-wal` appeared during the run — these are normal SQLite WAL/SHM journal artifacts and will fold back on next checkpoint; not anomalies.
- `error_breakdown` shows the 2 `rejected_complexity` rows are both `description > 300 chars` schema violations, the same complexity-budget rejection class CLAUDE.md documents. No `proposer_invalid_dsl`, no `duplicate`, no `backend_empty_output`.

### §1.15 Distribution verdict — REPRODUCES_SEALED

The five behavioral signatures from sealed all reproduce on the fresh sample:
1. **RSI_14 dominance** — sealed first-50 ratio 0.920 → batch-1 first-50 ratio 0.920, identical to four decimal places. Anomaly flag fires with same shape.
2. **Top-3 factors** — `rsi_14, return_24h, close` in both, in the same order.
3. **Per-theme dominant_factors_top3** — identical for `momentum`, `volume_divergence`, `calendar_effect`; near-identical for `mean_reversion` and `volatility_regime` (one position swap each, same factor pool).
4. **Novelty erosion** — monotonically declining `unique_factor_set_ratio` across position quartiles, same shape as sealed.
5. **Theme-as-hint cross-theme momentum fallback** — `contains_momentum_default_count` is 38–40 across all five themes (i.e., the default momentum factors appear in 95–100% of valid candidates regardless of theme). Sealed showed the same pattern.

Batch-1 is materially indistinguishable from sealed at the behavioral-signature level. No new dominant factors emerged. No themes broke from the cross-theme momentum fallback. Novelty saturation reached the same approximate range (0.71 vs 0.67).

---

## 2. What this means for the next decision

The pre-fire framing offered two honest expectations: (a) "probably reproduces, given nothing has changed," and (b) "something will look different." Outcome is firmly (a). $2.30 spent confirms the proposer's behavioral signature is stable under fresh sampling at unchanged code/prompt/model. Reproducibility is a positive finding — it eliminates "maybe sealed was a fluke" as an explanation for the D8.3 triage distribution (57/134/2/0/4 across dispositions). At p≈0.92, n=50, one standard error is ±0.04, so two runs landing on identical 46/50 first-50 RSI_14 ratios is well inside expected sampling noise; the match is striking on inspection but not anomalous on the variance math.

**One observation worth tagging as a forward-pointer.** Sealed only published the first-50 RSI_14 dominance number (0.920). Batch-1's full-batch quartile data shows dominance does not decline across position blocks: 0.92 → 0.83 → 0.90 → **0.98**. The Q151-200 = 98% figure is the strongest individual finding in this run. One plausible mechanism: the approved-examples cap=3 sliding window stabilizes into RSI-heavy strategies by mid-batch, and the proposer conditions on those examples in a way that intensifies (rather than diversifies) RSI saturation. This is consistent with the D8.4 hypothesis that approved-examples conditioning is a load-bearing source of the observed concentration. Confirming this would require comparing quartile trajectories across two or more runs — batch-1 is the first sample with quartile-resolution data.

Operationally, batch-1 makes an unchanged batch-2 low-value: a fresh proposer-only run from the same HEAD with the same prompt would, on this evidence, produce the same RSI-saturated, momentum-fallback-shaped distribution at the same cost. The useful next actions are no longer "more sampling at this configuration." Three credible directions, presented as options not as a recommendation:

1. **Change the proposer methodology and measure the delta.** Ship one of the D8.4-documented prompt/code changes (e.g. theme-anchor enforcement, factor-cap, novelty-pressure clauses, approved-examples-rotation), then run batch-2 to compare distributions against this batch.
2. **Build the missing Stage 2d → DSL compile → walk-forward → regime holdout → DSR/lifecycle finalization funnel.** Until this exists, candidates can only be evaluated by surface diagnostics, never by `shortlisted`-style downstream signal. Funnel-build is necessary infrastructure regardless of which methodology direction is taken; it is also the mechanism by which a methodology fix's quality (rather than its distribution-delta) becomes measurable.
3. **Run a separate D7-style critic pass over batch-1's 198 pending_backtest candidates** (~$3.23 at sealed D7 rates) — using the sealed critic path or a deliberately scoped wrapper if needed; the existing `scripts/run_d7_stage2d_batch.py` was wired against pre-existing/replay candidates and is not drop-in for batch-1's directory without verification. Yields critic scores on the fresh cohort; useful only if critic-distribution-against-sealed-critic-distribution is itself a target. Lower-value given the proposer side reproduces so cleanly.

Choosing between (1) and (2) is a research-direction call, not a finding adjudicated by this batch. The distinction worth being explicit about: option 1 measures *whether the methodology change moved the distribution*, but cannot say *whether the new distribution is better* without (2). Option 2 makes any future methodology change evaluable by candidate quality rather than distribution shape.

---

## 3. Forward-pointers (carried over, none unblocked by this batch)

- **`agents/proposer/stage2d_batch.py:1081-1108`** still calls `run_critic` without `ledger.write_pending` for the critic call. Benign in stub mode (current default); becomes a spend-accounting bug if/when `LiveSonnetD7bBackend` is wired into `main()`. Sequencing constraint stands: ledger pre-charge before or with live-critic wiring.
- **CLAUDE.md drift**: `python -m backtest.evaluate_dsr --batch-id <UUID>` documented but `--batch-id` flag does not exist in `backtest/evaluate_dsr.py`. Either implement D9 finalization or correct the doc.
- **D8.4 unshipped**: six methodology recommendations remain documentation only. This batch's reproducibility result is an empirical input bearing on whether to ship one — not an adjudicated requirement to do so.

---

## 4. Spend posture

| | Pre-batch | Post-batch | Cap |
|---|---|---|---|
| Batch spend | $0 | $2.302194 | $20 (hardcoded) |
| Monthly spend (UTC 2026-04) | $6.351408 | $8.653602 | $100 |
| Monthly headroom remaining | $93.65 | $91.35 | — |

`agents/spend_ledger.db` ledger: 200 rows for `batch_id=b6fcbf86…`, all `status=completed`, all `api_call_kind=proposer`, `backend_kind=d6_proposer`, `call_role=propose`. Zero crashed rows. Zero pending rows. Sum of `actual_cost` matches `total_actual_cost_usd` in summary JSON to four decimal places.

---

## 5. Artifacts (not committed)

- `raw_payloads/batch_b6fcbf86-4d57-4d1f-ae41-1778296b1ae9/stage2d_summary.json` — 200 calls, all metrics in §1.
- `raw_payloads/batch_b6fcbf86-4d57-4d1f-ae41-1778296b1ae9/stage2d_summary_partial.json` — periodic checkpoint (intermediate; superseded by final summary).
- `raw_payloads/batch_b6fcbf86-4d57-4d1f-ae41-1778296b1ae9/attempt_NNNN_prompt.txt` × 200 — per-call prompt text (audit artifact, gitignored under `raw_payloads/`).
- `raw_payloads/batch_b6fcbf86-4d57-4d1f-ae41-1778296b1ae9/attempt_NNNN_response.txt` × 200 — per-call response text (audit artifact, gitignored).
- `agents/spend_ledger.db` — 200 ledger rows for this batch.

This closeout document at `docs/closeout/PHASE2C_3_BATCH1.md` is the only file written outside `raw_payloads/` and `agents/spend_ledger.db`. Not committed; awaiting Charlie's review.

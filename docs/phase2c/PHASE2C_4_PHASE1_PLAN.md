# Phase 2C Phase 1 Funnel — Implementation Contract

**Status:** approved as implementation contract by Charlie 2026-04-26.
**Predecessor closeout:** `docs/closeout/PHASE2C_3_BATCH1.md` (committed at `4a0868d`).
**Decision basis:** Batch-1 reproduced sealed D6 Stage 2d distribution at high fidelity (mechanics PASS, distribution REPRODUCES_SEALED). Generation is stable; the next bottleneck is candidate-quality evaluation. Funnel-build was chosen over methodology-fix-first because methodology fixes optimize surface metrics without an ability to measure whether the resulting candidates trade better.

---

## 1. Scope

**Phase 1 builds:** a thin local evaluation bridge from batch-1's 198 `pending_backtest` candidates → DSL compile → `run_walk_forward` → per-candidate results CSV + leaderboard.

**Phase 1 does NOT build:**
- Regime holdout AND-gate integration (`run_regime_holdout` exists; not called).
- DSR multiple-testing screen integration (`evaluate_dsr.py` exists; not called).
- Lifecycle state writes (`pending_backtest` → `train_failed` / `holdout_failed` / `dsr_failed` / `shortlisted`).
- `evaluate_dsr.py --batch-id` flag implementation.
- D9 `finalize_batch()`.
- Any critic invocation, live or stub.
- Per-candidate `data/compiled_strategies/<hash>.json` manifest writes.

**Phase 1 does NOT spend:**
- Zero Anthropic API calls. No proposer, no critic.
- Local compute only. ~3 hours background for full 198-candidate sweep.

---

## 2. Phase 1 success criterion

**Binary (decision gate for Phase 2):**
≥1 of batch-1's 198 candidates produces walk-forward Sharpe > 0.5 on its test windows.

**Research-interpretation reporting (alongside binary):**
Full distribution shape — median, mean, max, count > 0.5, count > 0.0, count > -0.3, count of compile failures, count of runtime errors. The binary verdict and the distribution shape are reported together, since "1 candidate at 0.55 with median -0.3" and "50 candidates clustered around 0.4 with one at 0.55" both pass the binary but carry very different research signal.

**Outcome routing:**
- **Met (≥1 passes Sharpe > 0.5):** Phase 2 (regime holdout + DSR + lifecycle) is clearly worth continuing.
- **Not met (0 candidates pass):** re-open methodology question with hard evidence — proposer outputs are diverse-enough but don't trade.
- **Strongly met (≥10 candidates pass):** consider whether Phase 2's regime holdout filter is the next-most-valuable build vs. a paper-trading harness on top survivors.

---

## 3. What's already in place (Phase 1 inherits, does not rebuild)

Discoveries from the read-only scoping pass:

- `strategies/dsl_compiler.py:585` `compile_dsl_to_strategy(dsl)` returns a Backtrader strategy class. The integration pattern is shown in `backtest/engine.py:1326-1336` (used by `run_regime_holdout`):
  ```python
  strategy_cls = compile_dsl_to_strategy(dsl, **compile_kwargs)
  hypothesis_hash = compute_dsl_hash(dsl)
  ```
- `backtest/engine.py:725` `run_walk_forward(strategy_cls, ...)` accepts a compiled class directly. Phase 1 needs ~5 lines of glue (compile, then call), not a bridge build.
- `backtest/engine.py:330` `run_backtest` already writes per-run trade CSV + experiments.db row. Phase 1 inherits this for free per candidate × per WF window.
- `backtest/experiment_registry.py` schema already includes `batch_id`, `hypothesis_hash`, `lifecycle_state`, `feature_version` columns. No migration needed for Phase 1.
- v2 split (disjoint train ranges 2020-2021 + 2023, validation 2024) is already wired into `run_walk_forward`. Phase 1 inherits aggregation rules per CLAUDE.md (mean Sharpe/return, max DD, summed trade count across disjoint train windows; never stitched into a single equity curve).

---

## 4. What Phase 1 builds

### Component A — Candidate extraction script

Read `raw_payloads/batch_<batch-id>/stage2d_summary.json`, filter `calls[]` to `lifecycle_state == "pending_backtest"`, for each:
1. Read `attempt_NNNN_response.txt`.
2. Strip code fences (the response is a JSON object wrapped in triple-backtick `json` blocks).
3. JSON-parse.
4. Validate via `StrategyDSL` pydantic schema (re-validation; cheap).

Output: in-memory list of `(position, hypothesis_hash, name, theme, factors_used, dsl)` tuples.

**Edge cases:**
- Re-validation failure (should not happen — proposer already validated; record as `compile_status=re_validation_failed` if it does).
- Code-fence stripping handles both ```` ```json ```` and bare ``` ``` ``` ``` opener variants.

**Estimated LOC:** 50–80.

### Component B — Per-candidate WF driver

For each `(position, hash, dsl)`:
1. Call `compile_dsl_to_strategy(dsl)`. Catch `ManifestDriftError` and any other compile-time exceptions; record `compile_status` accordingly.
2. Call `run_walk_forward(strategy_cls, ...)`. Catch runtime exceptions (cerebro internals, data issues, division by zero); record `runtime_status` and full traceback.
3. Extract per-candidate metrics from `WalkForwardResult.summary_metrics` using **the engine's actual field names** — verified at implementation time by reading `_aggregate_walk_forward_metrics` (`engine.py:1003`), not assumed here.

**Implementation rule:** every candidate produces a CSV row, including failures. Failure rate is itself research signal.

**Edge cases:**
- Compile succeeds, WF window has zero trades → record metrics (Sharpe NaN, drawdown 0, trade-count 0); not a failure.
- Compile succeeds, runtime exception → log full traceback to `data/phase2c_walkforward/batch_<uuid>/errors/<hash>_traceback.txt`, record `runtime_status=error: <one-line message>`, continue.
- Insufficient-data WF window → already handled inside `run_walk_forward` per its docstring; inherits.
- Duplicate `hypothesis_hash` → batch-1 has 0 by hash, but dedupe defensively.

**Estimated LOC:** 80–120.

### Component C — Aggregation report

Sort by WF Sharpe descending; emit:
1. `data/phase2c_walkforward/batch_<batch-id>/walk_forward_results.csv` — one row per candidate.
2. `data/phase2c_walkforward/batch_<batch-id>/walk_forward_summary.json` — distribution stats (median/mean/max/percentiles) + run metadata (script git SHA, run timestamp UTC, total elapsed wall clock, per-candidate mean elapsed).
3. Stdout: top-10 leaderboard + distribution stats + binary verdict ("Phase 1 success criterion: MET / NOT MET — N candidates passed Sharpe > 0.5 threshold").

**CSV columns (final list determined at implementation by inspecting `_aggregate_walk_forward_metrics`; this is the proposed schema, subject to engine-field-name verification):**
```
batch_id
position
hypothesis_hash
name
theme
factors_used               (semicolon-joined list)
compile_status             (ok | manifest_drift | re_validation_failed | compile_error)
runtime_status             (ok | error)
wf_sharpe                  (engine field: train_sharpe or aggregated_sharpe — verify at impl)
wf_return                  (engine field: train_return or aggregated_return — verify at impl)
wf_max_drawdown            (engine field: train_max_dd — verify at impl)
wf_total_trades            (engine field: train_total_trades)
wf_window_count            (number of WF sub-windows that produced metrics)
elapsed_seconds
error_message              (one line; empty for ok runs)
```

**Naming caveat (from ChatGPT review):** do not call any column `validation_sharpe` unless the engine clearly distinguishes train/test in `WalkForwardResult.summary_metrics`. If the engine returns aggregated WF metrics under one name, use that name; if it separates train/validation, use both. Verified at impl time, not assumed.

**Output location:** `data/phase2c_walkforward/batch_<batch-id>/`. Outside `raw_payloads/` (proposer artifacts) per separation discipline.

**Estimated LOC:** 60–100.

### Total Phase 1 net new code

~190–300 lines, in `scripts/run_phase2c_batch_walkforward.py`.

---

## 5. Pre-sweep sanity-check trio (mandatory before any 198-sweep)

These are the load-bearing risk mitigations. Each is read-only or local-compute, $0 API spend, and runs before the full sweep.

### Sanity check 1 — pre-existing hash check

Query `backtest/experiments.db` for any rows whose `hypothesis_hash` matches any of batch-1's 198 hashes.

**Expected:** zero hits (the funnel doesn't exist yet, so they shouldn't be there).
**Findings to investigate:** any non-zero count. Possibilities: leftover row from prior testing (benign; dedupe), hash collision with unrelated strategy (worth knowing), or registry being written by an untraced path (load-bearing, investigate before continuing).

**Time:** 5 minutes. **Spend:** $0.

### Sanity check 2 — driver calibration

Run one sealed Phase 1B baseline strategy (e.g., `sma_crossover` from `strategies/baseline/`) through the Component B driver, **bypassing Components A and C** (use `strategy_cls` directly, not `compile_dsl_to_strategy`).

Compare the resulting WF summary metrics against the sealed Phase 1B closeout numbers for `sma_crossover`.

**Expected:** identical metrics within floating-point tolerance.
**Findings to investigate:** material divergence. Almost certainly a driver bug, not a candidate issue. Stop and fix before continuing.

**Time:** 30 minutes. **Spend:** $0.

### Sanity check 3 — compiler manual verification on 5 diverse candidates

Pick 5 candidates from batch-1's 198 with structurally diverse DSL shapes:
1. One with `crosses_above` or `crosses_below` operator (CONTRACT GAP per CLAUDE.md — must compile to two-bar form, not naive single-bar).
2. One with factor-vs-factor comparison (separate compiler code path from factor-vs-scalar).
3. One with multiple condition groups in entry or exit.
4. One with the largest factor count among the 198.
5. One with the simplest DSL (smallest condition count).

For each: run Component A's extraction → call `compile_dsl_to_strategy` → manually read the generated `next()` method against the DSL spec.

**Verify:**
- `crosses_above`/`crosses_below` compiles to `bt.indicators.CrossOver` or explicit two-bar form, not a single-bar comparison.
- NaN in any comparison evaluates to `False`, not `True`.
- Factor-vs-scalar and factor-vs-factor paths produce distinct generated code.
- Negative shifts, intrabar reads of close, or `shift(-k)` are absent from generated code.

**Expected:** all 5 compile cleanly and the `next()` logic matches DSL semantics.
**Findings to investigate:** any silent miscompilation (compiles successfully but logic is wrong). This is the highest-risk failure mode for Phase 1 because the WF results would look plausible but be wrong. Stop and surface before continuing.

**Time:** 30 minutes. **Spend:** $0.

---

## 6. Three-tier sweep gating

After all three sanity checks pass, the actual sweep runs in three tiers, each gating the next:

### Tier 1 — Smoke (5 candidates)

Run the driver on a hand-picked 5 candidates (overlap with sanity check 3 acceptable). Report:
- Per-candidate compile_status, runtime_status.
- Top-line WF metrics for any that passed compile + runtime.
- Total elapsed time.
- Any unexpected behavior (warnings, log errors, suspicious metric values).

**Gate to Tier 2:** all 5 produce valid CSV rows (failures included with status codes, not crashes); driver elapsed time projects to a reasonable full-sweep wall clock (~3 hours expected).

### Tier 2 — Pilot (20 candidates)

Run the driver on 20 candidates (positions 1, 11, 21, …, 191 — every 10th from batch). Report:
- Compile success rate, runtime success rate.
- Top-3 WF Sharpe candidates.
- Distribution shape preview (median, max, count > 0.5).
- Total elapsed time and projected full-sweep time.

**Gate to Tier 3:** compile + runtime success rate ≥ 90%; no systemic failure pattern surfaces (e.g., all `crosses_above` candidates failing).

### Tier 3 — Full sweep (198 candidates)

Run the driver on all 198 `pending_backtest` candidates. Background-launchable. Report on completion per Component C.

---

## 7. CLI interface

`scripts/run_phase2c_batch_walkforward.py`

**Required flags:**
- `--batch-id <UUID>` — identifies the batch directory under `raw_payloads/`.

**Optional flags:**
- `--limit <N>` — process at most N `pending_backtest` candidates (default: 5; this is deliberate so accidental no-flag runs don't burn 3 hours of compute).
- `--positions <comma-list>` — process specific positions by 1-indexed position (overrides `--limit`).
- `--dry-run` — extract candidates, compile, but do not run walk-forward. Use to verify Components A+B compile-side without spending compute on Component B's WF runs.
- `--output-dir <path>` — override default `data/phase2c_walkforward/batch_<batch-id>/`.

**Example invocations:**
```bash
# Smoke (Tier 1)
python scripts/run_phase2c_batch_walkforward.py \
    --batch-id b6fcbf86-4d57-4d1f-ae41-1778296b1ae9 \
    --limit 5

# Pilot (Tier 2)
python scripts/run_phase2c_batch_walkforward.py \
    --batch-id b6fcbf86-4d57-4d1f-ae41-1778296b1ae9 \
    --positions 1,11,21,31,41,51,61,71,81,91,101,111,121,131,141,151,161,171,181,191

# Full sweep (Tier 3)
python scripts/run_phase2c_batch_walkforward.py \
    --batch-id b6fcbf86-4d57-4d1f-ae41-1778296b1ae9 \
    --limit 200
```

---

## 8. Risks (acknowledged, mitigated)

- **AI-generated DSLs may exercise compiler paths not previously hit by hand-coded baselines.** Mitigation: sanity check 3 (compiler manual verification on 5 diverse candidates).
- **WF results may surface latent execution-model bugs.** Mitigation: sanity check 2 (driver calibration against sealed Phase 1B baseline).
- **Phase 1 may find zero candidates with WF Sharpe > 0.5.** This is a valid outcome — the binary signal we're paying compute to learn. Triggers methodology-question re-open with hard evidence.
- **Compile success but silently wrong logic.** Mitigation: sanity check 3 reads compiled output by hand for 5 diverse cases; if those pass, the prior on remaining 193 is high.
- **Engine field-name assumptions in CSV schema (§4 Component C).** Mitigation: verified at implementation time against `_aggregate_walk_forward_metrics` source, not assumed from this plan.

---

## 9. Forward-pointers (Phase 2/3, not in scope here)

After Phase 1 completion, the next decisions:
- **Phase 2:** regime holdout AND-gate integration + DSR multiple-testing screen + lifecycle state writes (`pending_backtest` → terminal states). Builds on Phase 1's WF results.
- **Phase 3:** D9 `finalize_batch()` + `evaluate_dsr.py --batch-id` + batch-level leaderboard + `shortlisted` lifecycle state. Builds on Phase 2.

CLAUDE.md drift item: `python -m backtest.evaluate_dsr --batch-id <UUID>` documented but flag does not exist. Resolution comes with Phase 3.

Live-critic ledger gap (`stage2d_batch.py:1081-1108` calls `run_critic` without `ledger.write_pending`) remains tracked but not unblocked by Phase 1 work.

---

## 10. Done criteria for this plan

This document is approved as Phase 1's implementation contract. Component A starts in the same session this plan is committed. Components B and C may span subsequent sessions. Phase 1 closeout written to `docs/closeout/PHASE2C_5_PHASE1_RESULTS.md` after the full sweep completes, anchored against the binary success criterion + distribution-shape research signal.

No further plan elaboration. The plan is the contract; deviation requires explicit chat-protocol amendment and re-commit.

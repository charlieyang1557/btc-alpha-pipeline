# Phase-specific execution rules

Phase-specific execution rules extracted from CLAUDE.md for compactness. Canonical hard constraints remain inline at [CLAUDE.md HARD CONSTRAINTS section](../../CLAUDE.md). For sealed Phase Marker history, see [phase_marker_history.md](../phase_marker_history.md).

## Backtrader-Specific Rules

### Cerebro Configuration (MUST be set for every backtest run)
- `cerebro.broker.set_coc(False)` — disable cheat-on-close
- `cerebro.broker.set_coo(False)` — disable cheat-on-open
- `cerebro.broker.setcommission(commission=0.0007)` — 7bps per side effective cost
- `cerebro.broker.setcash(10000)` — default starting capital

### Common Pitfalls (Claude Code MUST avoid these)
- `self.data.close[0]` is the CURRENT bar's close — NOT the next bar's
- `self.buy()` submits a market order that fills at the NEXT bar's open — this is correct behavior, do not try to "fix" it
- `self.data.datetime.datetime(0)` returns a **naive** datetime — always convert to UTC when comparing with our data
- Backtrader's `PandasData` feed expects the DataFrame index to be datetime — set index before passing
- If `fromdate`/`todate` are timezone-naive, Backtrader may misalign with our UTC data — always use timezone-aware datetime objects
- Backtrader indicators (SMA, etc.) are **bar-based, not time-based** — a 24-period SMA averages the last 24 rows regardless of time gaps between them. This is acceptable (31 gaps in 55K bars is negligible) but must be documented.

### Warmup Handling
- Each strategy declares `WARMUP_BARS` (number of bars before signals are valid)
- The engine loads data from `start_date` but only begins recording metrics after warmup
- **No trades are allowed during the warmup period**
- Strategies must only emit signals inside Backtrader's `next()` method, NEVER in `prenext()`
- `prenext()` runs while indicators are still warming up — it must remain empty or contain only logging
- The first eligible signal bar is the first bar where `next()` is called
- The first eligible fill is the bar after that signal
- Metrics (Sharpe, drawdown, etc.) are computed ONLY on the post-warmup period
- If a strategy attempts to trade during warmup, the engine must block it
- **Phase 2 DSL compiler**: `WARMUP_BARS` is auto-set to `registry.max_warmup(factors_used)` — see D2 in `PHASE2_BLUEPRINT.md`

## Factor Parquet Rules (Phase 2)

- `data/features/btcusdt_1h_features.parquet` is the canonical factor dataset.
- `build_features.py` computes factors over the **full available OHLCV range**. Never build for a subset; subsetting happens at the consumption layer (engine `fromdate`/`todate`).
- The parquet's pyarrow metadata stores `feature_version` and `built_at_utc`.
- `feature_version` = SHA256 of canonical registry metadata, including per-factor: name, category, warmup_bars, inputs, output_dtype, and SHA256 of compute function source (via `inspect.getsource`).
- On any downstream read, if stored `feature_version` ≠ live `compute_feature_version(registry)`, the parquet MUST be force-rebuilt. No silent "use stale data" fallback.
- Registered factor compute functions MUST be top-level named callables. Lambdas, nested functions, and dynamically-generated callables are prohibited (breaks `inspect.getsource` stability).

## Phase 2 DSL Rules

- All AI-generated strategies are expressed in a pydantic-validated DSL (`strategies/dsl.py`) and compiled to Backtrader via `strategies/dsl_compiler.py`. Raw Backtrader code from agents is not accepted in Phase 2.
- **DSL complexity budget (schema-enforced):** entry/exit groups ≤ 3, conditions per group ≤ 4, `max_hold_bars` ≤ 720, `name` ≤ 64 chars, `description` ≤ 300 chars.
- **Comparison operator semantics:** `crosses_above` / `crosses_below` MUST compile to `bt.indicators.CrossOver` or an explicit two-bar form `(a[0] > b[0]) AND (a[-1] <= b[-1])`. A naive single-bar comparison is a compiler bug.
- **NaN in comparisons:** NaN on either side of a comparison evaluates to `False`. Never `True`.
- **Factor-vs-scalar and factor-vs-factor are separate compiler code paths** with independent unit tests for each operator.
- **Compilation manifest:** each compiled strategy writes `data/compiled_strategies/<hypothesis_hash>.json` with canonical DSL, compiler git SHA, factor list snapshot, and feature_version. Drift in any of these fields raises `ManifestDriftError`.

## Phase 2 Agent & Budget Rules

- **Budget caps (hard-enforced in code):** $20 per batch, $100 per UTC calendar month. Enforcement happens PRE-call (before each API invocation), not post-call.
- **Spend ledger uses pre-flight charge pattern:** write `status="pending"` row with upper-bound cost estimate BEFORE the API call; update to `status="completed"` with actual cost after. Pending rows count as spent. Crashed batches are not resumed.
- **Hypothesis lifecycle states** (8 terminal, 1 transient):
  - Terminal: `proposer_invalid_dsl`, `duplicate`, `critic_rejected`, `train_failed`, `holdout_failed`, `dsr_failed`, `shortlisted`, `budget_exhausted`
  - Transient: `pending_dsr` (orchestrator-time; resolved by D9 at batch close)
- **Invariant:** `sum(terminal_lifecycle_counts) == hypotheses_attempted`. Checked at batch close ONLY, never mid-batch.
- **`hypotheses_attempted` counting rule:** increments immediately after each Proposer call returns, regardless of validity, duplication, or Critic outcome. Unissued slots (budget exhausted before proposing) are tracked separately in `batch_summary.unissued_slots`.
- **Theme rotation:** `theme = THEMES[(k - 1) % len(THEMES)]` where k is 1-indexed batch position and THEMES is the canonical 6-theme list defined in D6.
- **Theme rotation operational boundary (Stage 2c/2d):** Current Stage 2c/2d operational rotation uses the first 5 canonical themes (`THEME_CYCLE_LEN = 5` in `agents/proposer/stage2c_batch.py` and `stage2d_batch.py`). `multi_factor_combination` remains part of the canonical theme list but is not included in the current operational rotation until separately validated. **The exclusion is operational practice, not canonical specification; canonical anchors (`THEMES` tuple in `agents/themes.py`, `expectations.md`, `blueprint/PHASE2_BLUEPRINT.md`) retain the 6-theme list.** Resolves Issue 6 of D8.4 methodology refinement (sub-arc sealed at commit `767d0e5`) as documentation-completeness + methodology-acceptance per Issue 6 candidate-resolution-layer enumeration. Option to flip to 6 themes preserved for future decision when there's a specific Phase 2C reason to want multi-factor combination strategies; flip would require small 6th-theme-only smoke batch to verify candidate quality first.
- **Train-summary aggregation for disjoint train windows (v2):** `train_sharpe` = mean of per-window Sharpes; `train_return` = mean of per-window returns; `train_max_dd` = max of per-window drawdowns; `train_total_trades` = sum. NEVER stitch disjoint train-window equity curves into a continuous series.
- **Leaderboard ranking:** after filtering to `lifecycle_state == "shortlisted"`, rank by `min(train_sharpe, holdout_sharpe)` descending. Ties broken by `train_return` descending.
- **DSR N:** always `hypotheses_attempted` from the `batch_summary` row. NEVER use `hypotheses_approved` or survivor count.
- **D9 finalization authority:** `shortlisted` and `dsr_failed` terminal states are written ONLY by D9's `finalize_batch()`. The orchestrator writes `pending_dsr` and stops.

## Raw payload audit artifact retention (permanent)

`raw_payloads/` directories referenced by signed-off Stage 2 acceptance
notebooks are audit artifacts and must not be deleted or bulk-cleaned
without explicit human approval. Currently protected batches:

- Stage 2a signed-off:              raw_payloads/batch_03d62937-dbe8-46f2-a91b-50fa5696b14e/
- Stage 2a post-patch re-smoke:     raw_payloads/batch_74a52dae-7a2e-4555-b773-c95f2211ad9f/
- Stage 2b signed-off:              raw_payloads/batch_cd2f32ba-1984-4461-8216-1a9ac4ca2c17/
- Stage 2c signed-off:              raw_payloads/batch_e07f34a2-b532-4f35-a9f3-af97a5a96f1f/

New acceptance batches are added here as they sign off. Claude Code
must not include these paths in any cleanup operation.

### Library Policy
**Approved core libraries (Phase 0-1):** pandas, numpy, pyarrow, ccxt, requests, pyyaml, backtrader, scipy, matplotlib, and Python stdlib modules (sqlite3, pathlib, argparse, logging, hashlib, datetime, json, zipfile, io, uuid, typing, inspect).

**Approved Phase 2 additions:** `anthropic` (Claude API), `pydantic ~= 2.0` (DSL schema validation).

Any library not listed above requires explicit human approval before use. Standard typing/testing utilities (e.g., `dataclasses`, `typing_extensions`, `pytest`) are allowed without approval.

---

For canonical hard constraints, see [CLAUDE.md HARD CONSTRAINTS section](../../CLAUDE.md). For sealed Phase Marker history, see [phase_marker_history.md](../phase_marker_history.md).

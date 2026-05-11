# Spike A — vectorbt ↔ Backtrader Byte-Equivalent Validation

**Date:** 2026-05-11
**Authorization:** Charlie register Spike A "1 authorized" + "4 approved" extension
**Purpose:** Hands-on empirical verification of vectorbt's ability to reproduce Backtrader N+1 fill semantics + 24-bar zero-volume deferral under the same OHLCV data and strategy signals. Used as input to the build-own BTC engine path analysis at `docs/discussion/2026-05-11_external_repos_survey.md` §F.
**Scope binding:** §29 analysis register only. These artifacts do NOT authorize implementation of any engine work.

## Environment

Throwaway venv at `/tmp/vectorbt_spike/venv` (now gone after session). To reproduce:

```bash
python3 -m venv venv
./venv/bin/pip install "pandas~=2.2.0" "numpy~=1.26.0" "pyarrow~=15.0.0" \
    "backtrader~=1.9.78" "vectorbt~=0.26.0" "plotly<5.20" pyyaml
```

**Known compatibility patch:** `vectorbt 0.26.x` crashes on `plotly >= 5.20` (`heatmapgl` removed in plotly 5.20). Pin `plotly < 5.20`. If a long-term fork is eventually built, patch `vectorbt/_settings.py` template at first commit.

## Scripts

| Script | Test | Result |
|---|---|---|
| `spike_compare.py` | A.1 — SMA crossover (fast=20, slow=50), 2024-01 to 2024-04, 3-way Oracle / Backtrader / vectorbt | ✅ 30 vs 30 vs 30 byte-equivalent; max abs diff 0.0000000000 |
| `spike_sizing_diagnostic.py` | A.1 follow-up — isolate $23 equity diff to sizing convention (99% vs ∞) | Per-trade gross return max diff = 5.68e-7 (float precision noise) |
| `spike_a2_operators.py` | A.2 — momentum (PctChange threshold) + mean_reversion (z-score) | momentum 36/36 ✅; mean_reversion 23+1 ⚠️ (see A.2b) |
| `spike_a2b_mean_rev_diagnostic.py` | A.2b — investigate mean_reversion 23-vs-24 mismatch | Cause: end-of-window force-close convention (vectorbt auto-closes at last bar; Backtrader leaves open). Configurable, not a semantic bug. |
| `spike_a3_zero_volume.py` | A.3 — SMA crossover on window containing 2023-03-24 zero-volume bar | 10/10 byte-equivalent; preprocessing no-op (signals didn't hit zero-vol path) |
| `spike_a3b_forced_defer.py` | A.3b — synthetic forced entry at zero-volume bar, AlphaBroker vs preprocessing | ✅ Both deferred to 2023-03-24 14:00 @ $28079.99, byte-identical. 24-bar preprocessing approach validated against project's AlphaBroker. |

## Empirical claims established (cite from this directory)

1. **`vbt.Portfolio.from_signals(close=close, entries=entries.shift(1), exits=exits.shift(1), price=open, fees=0.0007)` reproduces Backtrader's `set_coc(False) + set_coo(False) + setcommission(0.0007) + default-fill-on-next-open` within float precision** on three strategy classes (crossover / threshold / composite z-score).
2. **24-bar zero-volume deferral can be implemented as preprocessing on shifted entries/exits arrays**; semantically equivalent to project's `backtest/execution_model.py::AlphaBroker` (verified on synthetic forced case).
3. **End-of-window position handling is a configurable convention**, not an engine semantic. Either engine can match the other via explicit wrapper-level policy.

## NOT yet tested (deliberate deferrals for future spike work)

- Walk-forward multi-window stitching + corrected-WF lineage discipline
- AND/OR composite entry conditions
- Short trades
- Multi-asset cross-sectional portfolio
- Full PHASE2C SEALED candidate regression (Spike C scope, 3-4 weeks)

## Bundled discussion artifact

These scripts are evidence cited by `docs/discussion/2026-05-11_external_repos_survey.md` §F. Read that document first; treat these scripts as the falsifiable evidence layer behind the engine path analysis.

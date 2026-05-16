# B-T7 Cosine Threshold Calibration — v1

**Calibration timestamp (UTC)**: 2026-05-16T15:42:33Z
**Model**: `all-MiniLM-L6-v2` (embedding dim 384)
**Model first-param SHA-256[:16]**: `352d34a4ad725bb7`
**Fixture corpus**: synthetic; Phase 2C Stage 1 DSL pairs unavailable per sub-spec SEAL ab8e715 §6 P-F7 acknowledgment.
**Pair count**: 10 (5 near-dup + 5 distinct)

## Sweep results

| τ | TP | FP | FN | TN | Precision | Recall | F1 |
|---|---|---|---|---|---|---|---|
| 0.70 | 5 | 5 | 0 | 0 | 0.500 | 1.000 | 0.667 |
| 0.75 | 5 | 5 | 0 | 0 | 0.500 | 1.000 | 0.667 |
| 0.80 | 5 | 5 | 0 | 0 | 0.500 | 1.000 | 0.667 |
| 0.82 | 5 | 5 | 0 | 0 | 0.500 | 1.000 | 0.667 |
| 0.85 | 5 | 5 | 0 | 0 | 0.500 | 1.000 | 0.667 |
| 0.88 | 5 | 4 | 0 | 1 | 0.556 | 1.000 | 0.714 |
| 0.90 | 5 | 3 | 0 | 2 | 0.625 | 1.000 | 0.769 |

## Chosen τ

**τ = 0.9** (F1 = 0.7692, precision = 0.625, recall = 1.000)

**Selection rule**: highest F1 score across the τ sweep; tie-break prefers LOWER τ (more aggressive dedup at MVP since near-duplicates skip backtest and save compute; false-positives are Critic-overridable per B-3 quarantine semantics).

## Per-pair cosine similarity

| Pair ID | Label | Cosine | Description |
|---|---|---|---|
| `near_dup_sma_20_vs_21` | near_dup | 0.9995 | SMA(20) vs SMA(21) — parameter variation |
| `near_dup_sma_20_vs_22` | near_dup | 0.9992 | SMA(20) vs SMA(22) — wider parameter variation |
| `near_dup_rsi_14_30_vs_31` | near_dup | 0.9990 | RSI(14,30) vs RSI(14,31) — threshold value variation |
| `near_dup_rsi_window_14_vs_15` | near_dup | 0.9990 | RSI(14,30) vs RSI(15,30) — window variation |
| `near_dup_holdbars_10_vs_11` | near_dup | 0.9997 | Same entry, 10-bar vs 11-bar hold |
| `distinct_sma_vs_rsi` | distinct | 0.8931 | SMA-based momentum vs RSI-based mean-reversion |
| `distinct_long_vs_short_bias` | distinct | 0.9957 | Long SMA crossover vs short SMA crossover (opposite direction) |
| `distinct_single_vs_multi_factor` | distinct | 0.9570 | Single-factor SMA vs SMA + volume confirmation |
| `distinct_macd_vs_bbands` | distinct | 0.8700 | MACD signal cross vs Bollinger Bands squeeze |
| `distinct_short_vs_long_window` | distinct | 0.9898 | SMA(5) short-term vs SMA(200) long-term — same factor, drastically different timeframes |

## Sub-spec impact

Sub-spec SEAL `ab8e715` §4 B-1 carried τ=0.82 PROVISIONAL with Wave 0 re-adjudication trigger if calibration knee ≠ 0.82.

**Calibration result**: chosen τ = **0.9**.

Chosen τ (0.9) ≠ PROVISIONAL 0.82 — **sub-spec amendment register-event triggered** per sub-spec §6 B-T7 (c) re-adjudication clause. B-1 default to be updated to τ=0.9 at sub-spec amendment cycle entry register-event boundary (separate Charlie authorization required).

## Discipline locks honored

- B-Lock-6: sentence-transformers local CPU; no remote embedding API
- B-Lock-7: model artifact SHA recorded above; install-time-only network egress
- HARD CONSTRAINT: fixture corpus is synthetic; no Phase 2C / validation / test / 2022-regime data ingested
- §6 P-F7 (Phase 2C data availability): unavailable → fixture-corpus-only-calibrated; production validation deferred to first Phase 2D batch

## Reproducibility

Run: `python scripts/btau_calibrate.py` (deterministic; same model file → same cosines → same chosen τ).
Outputs at `data/phase2_5/btau_calibration_v1/`: this file + `calibration_corpus.json` + `sweep_results.json`.

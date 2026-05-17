# B-T7 Cosine Threshold Re-Calibration — v2 (compound gate)

**Calibration timestamp (UTC)**: 2026-05-17T01:20:41Z
**Model**: `all-MiniLM-L6-v2` (embedding dim 384)
**Model first-param SHA-256[:16]**: `352d34a4ad725bb7`
**Embed input**: natural-language serializer (`nl_serialize_dsl` per amendment §2 B-4)
**Gate**: compound AND — `cosine ≥ τ_c AND factor_set_equal` (τ_s = 1.0 DEFINITIONAL per amendment §2 B-1)
**Pair count**: 32 (14 near-dup + 18 distinct)
**Distribution classes**: 5 per amendment §3 W0.3.v2 P-F2 expansion

## Distribution-class breakdown

| Class | n | near_dup | distinct | factor_set_equal | factor_set_neq |
|---|---|---|---|---|---|
| C1_param_variation_diff_factor_set | 4 | 0 | 4 | 0 | 4 |
| C2_threshold_variation_same_factor_set | 14 | 14 | 0 | 14 | 0 |
| C3_direction_flip_same_factor_set | 5 | 0 | 5 | 5 | 0 |
| C4_factor_swap_diff_factor_set | 7 | 0 | 7 | 0 | 7 |
| C5_scale_shift_diff_factor_set | 2 | 0 | 2 | 0 | 2 |

## Sweep results (compound AND-gate)

| τ_c | TP | FP | FN | TN | Precision | Recall | F1 |
|---|---|---|---|---|---|---|---|
| 0.80 | 14 | 5 | 0 | 13 | 0.737 | 1.000 | 0.849 |
| 0.82 | 14 | 5 | 0 | 13 | 0.737 | 1.000 | 0.849 |
| 0.85 | 14 | 5 | 0 | 13 | 0.737 | 1.000 | 0.849 |
| 0.88 | 14 | 5 | 0 | 13 | 0.737 | 1.000 | 0.849 |
| 0.90 | 14 | 5 | 0 | 13 | 0.737 | 1.000 | 0.849 |
| 0.92 | 14 | 5 | 0 | 13 | 0.737 | 1.000 | 0.849 |
| 0.95 | 14 | 5 | 0 | 13 | 0.737 | 1.000 | 0.849 |
| 0.97 | 14 | 5 | 0 | 13 | 0.737 | 1.000 | 0.849 |
| 0.99 | 14 | 2 | 0 | 16 | 0.875 | 1.000 | 0.933 |

## Chosen τ_c

**τ_c = 0.99** (F1 = 0.9333, precision = 0.875, recall = 1.000)

**Selection rule**: highest F1 across compound-gate sweep; tie-break prefers LOWER τ_c.

## Conjunctive no-further-amendment trigger

- (i) τ_c ∈ [0.85, 0.99]: **True** (chosen 0.99)
- (ii) F1 ≥ 0.85: **True** (F1 = 0.9333)

**Both conditions met → NO further amendment required. B-1 default confirmed at τ_c = 0.99**, F1 = 0.9333.

## Per-pair details (sorted by cosine)

| Pair ID | Class | Label | Cosine | FS Equal | Description |
|---|---|---|---|---|---|
| `C3_sma_above_vs_below` | C3_direction_flip_same_factor_set | distinct | 0.9997 | ✓ | SMA above close vs SMA below close — opposite direction |
| `C3_macd_pos_vs_neg` | C3_direction_flip_same_factor_set | distinct | 0.9997 | ✓ | MACD histogram positive vs negative — opposite direction |
| `C2_volume_exit_var` | C2_threshold_variation_same_factor_set | near_dup | 0.9986 | ✓ | Volume z-score same entry, exit 0.5 vs 0.8 — same factor set |
| `C2_sma_close_v_threshold_var` | C2_threshold_variation_same_factor_set | near_dup | 0.9981 | ✓ | Return 24h threshold 0.02 vs 0.025 — same factor set |
| `C2_multi_cond_threshold` | C2_threshold_variation_same_factor_set | near_dup | 0.9970 | ✓ | RSI<30+vol vs RSI<31+vol — same factor set {rsi_14, volume_zscore_24h}, RSI threshold differs |
| `C2_hold_bars_var` | C2_threshold_variation_same_factor_set | near_dup | 0.9968 | ✓ | Same factor set + same conditions, only max_hold_bars differs |
| `C2_volume_threshold_var` | C2_threshold_variation_same_factor_set | near_dup | 0.9961 | ✓ | Volume z-score threshold 1.5 vs 1.8 — same factor set |
| `C2_returns_threshold_var` | C2_threshold_variation_same_factor_set | near_dup | 0.9958 | ✓ | Return 168h threshold 0.05 vs 0.06 — same factor set |
| `C2_ema_threshold_var` | C2_threshold_variation_same_factor_set | near_dup | 0.9955 | ✓ | EMA(12) breakout, max_hold 8 vs 12 — same factor set, only hold differs |
| `C2_zscore_threshold_var` | C2_threshold_variation_same_factor_set | near_dup | 0.9949 | ✓ | Z-score threshold 2.0 vs 2.5 — same factor set, threshold differs |
| `C2_rsi_30_vs_31` | C2_threshold_variation_same_factor_set | near_dup | 0.9949 | ✓ | RSI threshold 30 vs 31 — same factor set, threshold differs |
| `C2_rsi_exit_50_vs_55` | C2_threshold_variation_same_factor_set | near_dup | 0.9948 | ✓ | RSI exit threshold 50 vs 55 — same factor set, exit threshold differs |
| `C2_atr_op_var` | C2_threshold_variation_same_factor_set | near_dup | 0.9924 | ✓ | ATR > 100 vs ATR >= 100 — same factor set, edge case for operator boundary |
| `C2_zscore_exit_var` | C2_threshold_variation_same_factor_set | near_dup | 0.9921 | ✓ | Z-score same entry, exit threshold 0.5 vs 1.0 — same factor set |
| `C2_atr_threshold_var` | C2_threshold_variation_same_factor_set | near_dup | 0.9910 | ✓ | ATR threshold 100 vs 110 — same factor set, threshold differs |
| `C2_rsi_30_vs_32` | C2_threshold_variation_same_factor_set | near_dup | 0.9905 | ✓ | RSI threshold 30 vs 32 — same factor set, wider threshold gap |
| `C3_volume_high_vs_low` | C3_direction_flip_same_factor_set | distinct | 0.9886 | ✓ | Volume z-score high vs low — opposite direction |
| `C3_rsi_long_vs_short` | C3_direction_flip_same_factor_set | distinct | 0.9878 | ✓ | RSI oversold long vs overbought short — same factor, opposite direction |
| `C3_zscore_above_vs_below` | C3_direction_flip_same_factor_set | distinct | 0.9874 | ✓ | Z-score extreme high vs extreme low — opposite direction |
| `C1_sma_20_vs_24` | C1_param_variation_diff_factor_set | distinct | 0.9756 | ✗ | SMA(20) vs SMA(24) — different factor names; structural gate filters |
| `C1_sma_20_vs_50` | C1_param_variation_diff_factor_set | distinct | 0.9683 | ✗ | SMA(20) vs SMA(50) — different factor names |
| `C1_ema_12_vs_26` | C1_param_variation_diff_factor_set | distinct | 0.9592 | ✗ | EMA(12) vs EMA(26) — different factor names |
| `C5_sma_20_vs_sma_50_short` | C5_scale_shift_diff_factor_set | distinct | 0.9549 | ✗ | SMA(20) fast 5-bar hold vs SMA(50) slow 100-bar hold |
| `C1_return_1h_vs_24h` | C1_param_variation_diff_factor_set | distinct | 0.9434 | ✗ | return_1h vs return_24h — different factor names |
| `C5_return_1h_vs_168h` | C5_scale_shift_diff_factor_set | distinct | 0.9321 | ✗ | Return 1h vs 168h — different timescales (168x scale shift) |
| `C4_sma_vs_rsi` | C4_factor_swap_diff_factor_set | distinct | 0.8022 | ✗ | SMA momentum vs RSI mean-reversion — different families |
| `C4_atr_vs_zscore` | C4_factor_swap_diff_factor_set | distinct | 0.7993 | ✗ | ATR vs Z-score — different volatility measures |
| `C4_volatility_vs_return` | C4_factor_swap_diff_factor_set | distinct | 0.7919 | ✗ | Realized vol low-filter vs return momentum — different families |
| `C4_volume_vs_volatility` | C4_factor_swap_diff_factor_set | distinct | 0.7412 | ✗ | Volume z-score vs realized vol — different factor families |
| `C4_time_vs_price` | C4_factor_swap_diff_factor_set | distinct | 0.7385 | ✗ | Time-of-day vs price momentum — totally different concepts |
| `C4_macd_vs_bb` | C4_factor_swap_diff_factor_set | distinct | 0.7358 | ✗ | MACD vs Bollinger Bands — different families |
| `C4_dayofweek_vs_macd` | C4_factor_swap_diff_factor_set | distinct | 0.7012 | ✗ | Day-of-week filter vs MACD histogram — different factor families |

## Discipline locks honored

- B-Lock-1: separate code path from D3 canonicalization (semantic_dedup.py distinct from hypothesis_hash.py)
- B-Lock-2 (extended sibling clause): NL serializer traverses StrategyDSL directly; no import of hypothesis_hash
- B-Lock-6: sentence-transformers local CPU; no remote embedding API
- B-Lock-7: model artifact SHA recorded above; install-time-only network egress
- HARD CONSTRAINT: fixture corpus is synthetic; no Phase 2C / validation / test / 2022-regime data ingested

## Compared to W0.3 (predecessor calibration)

- W0.3 (commit `a8d10ef`): D3-canonical JSON input, cosine-only gate, N=10 fixture, F1 = 0.7692 at chosen τ = 0.90
- W0.3.v2 (this calibration): NL serializer input, compound AND-gate, N=32 fixture (5-class), F1 = 0.9333 at chosen τ_c = 0.99

## Reproducibility

Run: `python scripts/btau_calibrate_v2.py`. Deterministic given same model file.
Outputs at `data/phase2_5/btau_calibration_v2/`: this file + `fixture_corpus.json` + `sweep_results.json`.

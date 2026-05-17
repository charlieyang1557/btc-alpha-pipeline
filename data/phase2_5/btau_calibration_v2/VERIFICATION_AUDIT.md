# B-T7 Verification Audit — Is the W0.3 → W0.3.v2 F1 Improvement Real?

**Charlie register-event question**: "verify the F1 boost is actual improvement instead of some sort of cheating to boost this statistics score".

**Methodology**: 2×2 ablation matrix on the SAME N=32 W0.3.v2 fixture corpus. Holds fixture composition + model + factor-set definitions constant; varies ONLY (serialization, gate-type).

Model: `all-MiniLM-L6-v2` first-param SHA `352d34a4ad725bb7` (matches W0.3 + W0.3.v2)

## 2×2 ablation results — best F1 per config (sweep over τ)

| Config | Best F1 | τ | P | R | TP | FP | FN | TN |
|---|---|---|---|---|---|---|---|---|
| D3-JSON × cosine-only (≈W0.3) | **0.7179** | 0.97 | 0.560 | 1.000 | 14 | 11 | 0 | 7 |
| D3-JSON × compound | **0.8485** | 0.70 | 0.737 | 1.000 | 14 | 5 | 0 | 13 |
| NL × cosine-only | **0.9333** | 0.99 | 0.875 | 1.000 | 14 | 2 | 0 | 16 |
| NL × compound (W0.3.v2) | **0.9333** | 0.99 | 0.875 | 1.000 | 14 | 2 | 0 | 16 |

## Marginal contribution analysis

- Baseline (D3-JSON × cosine-only): F1 = **0.7179**
- Adding compound gate alone (D3-JSON × compound): F1 = **0.8485** (Δ = +0.1306)
- Adding NL serializer alone (NL × cosine-only): F1 = **0.9333** (Δ = +0.2154)
- Adding both (NL × compound = W0.3.v2): F1 = **0.9333** (Δ = +0.2154)

**Interpretation**: if compound gate alone or NL alone accounts for most of Δ, the other lever is doing little additional work. If both contribute, the combined config is a real composition gain.

## Same-factor-set SUBSET ('hard' pairs only)

When restricted to pairs where compound gate's structural side is TRUE for both, the compound gate degenerates to cosine-only. This subset measures the cosine gate's TRUE discrimination power — no 'auto-wins' from cross-factor structural rejection.

| Config | Best F1 | τ | P | R | TP | FP | FN | TN |
|---|---|---|---|---|---|---|---|---|
| D3-JSON cosine on hard subset | **0.8485** | 0.70 | 0.737 | 1.000 | 14 | 5 | 0 | 0 |
| NL cosine on hard subset | **0.9333** | 0.99 | 0.875 | 1.000 | 14 | 2 | 0 | 3 |

## Cosine distribution audit

| Slice | n | min | mean | max |
|---|---|---|---|---|
| Near-dup, D3-JSON | 14 | 0.9974 | 0.9989 | 0.9993 |
| Near-dup, NL | 14 | 0.9905 | 0.9949 | 0.9986 |
| Distinct (all), D3-JSON | 18 | 0.9106 | 0.9768 | 0.9996 |
| Distinct (all), NL | 18 | 0.7012 | 0.8893 | 0.9997 |
| Distinct same-FS, D3-JSON | 5 | 0.9957 | 0.9979 | 0.9996 |
| Distinct same-FS, NL | 5 | 0.9874 | 0.9926 | 0.9997 |

**Class-separation gap** (mean distinct minus mean near-dup; more negative = better separation):
- D3-JSON gap on hard subset: -0.0010
- NL gap on hard subset: -0.0023

## Per-class breakdown at W0.3.v2 chosen τ_c=0.99

| Class | n | TP | FP | FN | TN |
|---|---|---|---|---|---|
| C1_param_variation_diff_factor_set | 4 | 0 | 0 | 0 | 4 |
| C2_threshold_variation_same_factor_set | 14 | 14 | 0 | 0 | 0 |
| C3_direction_flip_same_factor_set | 5 | 0 | 2 | 0 | 3 |
| C4_factor_swap_diff_factor_set | 7 | 0 | 0 | 0 | 7 |
| C5_scale_shift_diff_factor_set | 2 | 0 | 0 | 0 | 2 |

## Per-pair: D3-JSON vs NL cosine (same-factor-set subset, sorted by NL cosine)

| Pair ID | Class | Label | cos D3-JSON | cos NL | NL-D3 Δ |
|---|---|---|---|---|---|
| `C3_sma_above_vs_below` | C3_direction_flip_same_factor_set | distinct | 0.9996 | 0.9997 | +0.0001 |
| `C3_macd_pos_vs_neg` | C3_direction_flip_same_factor_set | distinct | 0.9978 | 0.9997 | +0.0020 |
| `C2_volume_exit_var` | C2_threshold_variation_same_factor_set | near_dup | 0.9989 | 0.9986 | -0.0003 |
| `C2_sma_close_v_threshold_var` | C2_threshold_variation_same_factor_set | near_dup | 0.9974 | 0.9981 | +0.0006 |
| `C2_multi_cond_threshold` | C2_threshold_variation_same_factor_set | near_dup | 0.9992 | 0.9970 | -0.0022 |
| `C2_hold_bars_var` | C2_threshold_variation_same_factor_set | near_dup | 0.9988 | 0.9968 | -0.0020 |
| `C2_volume_threshold_var` | C2_threshold_variation_same_factor_set | near_dup | 0.9993 | 0.9961 | -0.0031 |
| `C2_returns_threshold_var` | C2_threshold_variation_same_factor_set | near_dup | 0.9988 | 0.9958 | -0.0031 |
| `C2_ema_threshold_var` | C2_threshold_variation_same_factor_set | near_dup | 0.9992 | 0.9955 | -0.0037 |
| `C2_zscore_threshold_var` | C2_threshold_variation_same_factor_set | near_dup | 0.9986 | 0.9949 | -0.0037 |
| `C2_rsi_30_vs_31` | C2_threshold_variation_same_factor_set | near_dup | 0.9991 | 0.9949 | -0.0043 |
| `C2_rsi_exit_50_vs_55` | C2_threshold_variation_same_factor_set | near_dup | 0.9993 | 0.9948 | -0.0044 |
| `C2_atr_op_var` | C2_threshold_variation_same_factor_set | near_dup | 0.9983 | 0.9924 | -0.0058 |
| `C2_zscore_exit_var` | C2_threshold_variation_same_factor_set | near_dup | 0.9990 | 0.9921 | -0.0069 |
| `C2_atr_threshold_var` | C2_threshold_variation_same_factor_set | near_dup | 0.9986 | 0.9910 | -0.0076 |
| `C2_rsi_30_vs_32` | C2_threshold_variation_same_factor_set | near_dup | 0.9993 | 0.9905 | -0.0087 |
| `C3_volume_high_vs_low` | C3_direction_flip_same_factor_set | distinct | 0.9980 | 0.9886 | -0.0093 |
| `C3_rsi_long_vs_short` | C3_direction_flip_same_factor_set | distinct | 0.9957 | 0.9878 | -0.0080 |
| `C3_zscore_above_vs_below` | C3_direction_flip_same_factor_set | distinct | 0.9982 | 0.9874 | -0.0108 |

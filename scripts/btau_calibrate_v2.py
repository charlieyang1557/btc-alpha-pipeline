"""Wave 0 W0.3.v2 — B-T7 cosine threshold re-calibration for Phase 2.5 Track B.

Per sub-spec amendment v1 SEAL `850aa1d` §3 W0.3.v2 scope:

- Uses NL serializer ``nl_serialize_dsl`` from semantic_dedup.py (B-4 revised)
- Compound AND-gate: cosine ≥ τ_c AND factor-set equality (B-6 revised)
- Expanded fixture N=30 with 5-class distribution labels per planner P-F2
- Sweep τ_c per amendment §2 B-1 selection rule (highest F1; tie-break LOWER τ)
- Conjunctive no-further-amendment trigger: τ_c ∈ [0.85, 0.99] AND F1 ≥ 0.85

Outputs at ``data/phase2_5/btau_calibration_v2/``:
- ``fixture_corpus.json``
- ``sweep_results.json``
- ``CALIBRATION_NOTE_V2.md``

Discipline:
- B-Lock-6 honored (local CPU; no remote API)
- B-Lock-7 honored (model SHA recorded; install-time-only network)
- HARD CONSTRAINT honored (fixture corpus synthetic; no validation/test/2022 data)
"""
from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

import numpy as np
from sentence_transformers import SentenceTransformer

from agents.critic.d7a_feature_extraction import extract_factors
from agents.orchestrator.semantic_dedup import nl_serialize_dsl
from strategies.dsl import StrategyDSL


REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = REPO_ROOT / "data" / "phase2_5" / "btau_calibration_v2"
SWEEP_TAUS = (0.80, 0.82, 0.85, 0.88, 0.90, 0.92, 0.95, 0.97, 0.99)
MODEL_NAME = "all-MiniLM-L6-v2"


PairLabel = Literal["near_dup", "distinct"]
DistributionClass = Literal[
    "C1_param_variation_diff_factor_set",
    "C2_threshold_variation_same_factor_set",
    "C3_direction_flip_same_factor_set",
    "C4_factor_swap_diff_factor_set",
    "C5_scale_shift_diff_factor_set",
]


@dataclass(frozen=True)
class CalibrationPair:
    pair_id: str
    label: PairLabel
    distribution_class: DistributionClass
    dsl_a: dict
    dsl_b: dict
    description: str


def _make_dsl_dict(
    *,
    name: str,
    entry_conds: list[dict],
    exit_conds: list[dict],
    max_hold_bars: int | None = 10,
) -> dict:
    """Build a validated-able DSL dict with a single entry group + single exit group."""
    return {
        "name": name,
        "description": "calibration fixture",
        "entry": [{"conditions": entry_conds}],
        "exit": [{"conditions": exit_conds}],
        "position_sizing": "full_equity",
        "max_hold_bars": max_hold_bars,
    }


def build_fixture_corpus() -> list[CalibrationPair]:
    """Construct N=30 calibration pairs across 5 distribution classes.

    Classes per sub-spec amendment §3 W0.3.v2 scope (P-F2 expansion):
    - C1: parameter variation (different factor names with same family;
      different factor sets per compound gate)
    - C2: threshold value variation (same factor set; only value differs)
    - C3: direction-flip (same factor set; opposite direction)
    - C4: factor-swap (different factor sets across families)
    - C5: scale-shift (different factor names; different scales)
    """
    pairs: list[CalibrationPair] = []

    # ---- Class C2: threshold-value variation — SAME factor set; near-dup ----
    # Same single factor, only value differs. These should pass structural
    # gate (factor-set equal) and be flagged as near-dup IF cosine high.
    pairs.append(CalibrationPair(
        pair_id="C2_rsi_30_vs_31",
        label="near_dup",
        distribution_class="C2_threshold_variation_same_factor_set",
        dsl_a=_make_dsl_dict(
            name="rsi_oversold_a",
            entry_conds=[{"factor": "rsi_14", "op": "<", "value": 30}],
            exit_conds=[{"factor": "rsi_14", "op": ">", "value": 50}],
        ),
        dsl_b=_make_dsl_dict(
            name="rsi_oversold_b",
            entry_conds=[{"factor": "rsi_14", "op": "<", "value": 31}],
            exit_conds=[{"factor": "rsi_14", "op": ">", "value": 50}],
        ),
        description="RSI threshold 30 vs 31 — same factor set, threshold differs",
    ))
    pairs.append(CalibrationPair(
        pair_id="C2_rsi_30_vs_32",
        label="near_dup",
        distribution_class="C2_threshold_variation_same_factor_set",
        dsl_a=_make_dsl_dict(
            name="rsi_oversold_a",
            entry_conds=[{"factor": "rsi_14", "op": "<", "value": 30}],
            exit_conds=[{"factor": "rsi_14", "op": ">", "value": 50}],
        ),
        dsl_b=_make_dsl_dict(
            name="rsi_oversold_c",
            entry_conds=[{"factor": "rsi_14", "op": "<", "value": 32}],
            exit_conds=[{"factor": "rsi_14", "op": ">", "value": 50}],
        ),
        description="RSI threshold 30 vs 32 — same factor set, wider threshold gap",
    ))
    pairs.append(CalibrationPair(
        pair_id="C2_rsi_exit_50_vs_55",
        label="near_dup",
        distribution_class="C2_threshold_variation_same_factor_set",
        dsl_a=_make_dsl_dict(
            name="rsi_oversold_a",
            entry_conds=[{"factor": "rsi_14", "op": "<", "value": 30}],
            exit_conds=[{"factor": "rsi_14", "op": ">", "value": 50}],
        ),
        dsl_b=_make_dsl_dict(
            name="rsi_oversold_d",
            entry_conds=[{"factor": "rsi_14", "op": "<", "value": 30}],
            exit_conds=[{"factor": "rsi_14", "op": ">", "value": 55}],
        ),
        description="RSI exit threshold 50 vs 55 — same factor set, exit threshold differs",
    ))
    pairs.append(CalibrationPair(
        pair_id="C2_atr_threshold_var",
        label="near_dup",
        distribution_class="C2_threshold_variation_same_factor_set",
        dsl_a=_make_dsl_dict(
            name="atr_high_vol_a",
            entry_conds=[{"factor": "atr_14", "op": ">", "value": 100}],
            exit_conds=[{"factor": "atr_14", "op": "<", "value": 80}],
        ),
        dsl_b=_make_dsl_dict(
            name="atr_high_vol_b",
            entry_conds=[{"factor": "atr_14", "op": ">", "value": 110}],
            exit_conds=[{"factor": "atr_14", "op": "<", "value": 80}],
        ),
        description="ATR threshold 100 vs 110 — same factor set, threshold differs",
    ))
    pairs.append(CalibrationPair(
        pair_id="C2_zscore_threshold_var",
        label="near_dup",
        distribution_class="C2_threshold_variation_same_factor_set",
        dsl_a=_make_dsl_dict(
            name="zscore_extreme_a",
            entry_conds=[{"factor": "zscore_48", "op": ">", "value": 2.0}],
            exit_conds=[{"factor": "zscore_48", "op": "<", "value": 0.5}],
        ),
        dsl_b=_make_dsl_dict(
            name="zscore_extreme_b",
            entry_conds=[{"factor": "zscore_48", "op": ">", "value": 2.5}],
            exit_conds=[{"factor": "zscore_48", "op": "<", "value": 0.5}],
        ),
        description="Z-score threshold 2.0 vs 2.5 — same factor set, threshold differs",
    ))
    pairs.append(CalibrationPair(
        pair_id="C2_volume_threshold_var",
        label="near_dup",
        distribution_class="C2_threshold_variation_same_factor_set",
        dsl_a=_make_dsl_dict(
            name="vol_surge_a",
            entry_conds=[{"factor": "volume_zscore_24h", "op": ">", "value": 1.5}],
            exit_conds=[{"factor": "volume_zscore_24h", "op": "<", "value": 0.5}],
        ),
        dsl_b=_make_dsl_dict(
            name="vol_surge_b",
            entry_conds=[{"factor": "volume_zscore_24h", "op": ">", "value": 1.8}],
            exit_conds=[{"factor": "volume_zscore_24h", "op": "<", "value": 0.5}],
        ),
        description="Volume z-score threshold 1.5 vs 1.8 — same factor set",
    ))
    pairs.append(CalibrationPair(
        pair_id="C2_hold_bars_var",
        label="near_dup",
        distribution_class="C2_threshold_variation_same_factor_set",
        dsl_a=_make_dsl_dict(
            name="rsi_a_10bar",
            entry_conds=[{"factor": "rsi_14", "op": "<", "value": 30}],
            exit_conds=[{"factor": "rsi_14", "op": ">", "value": 50}],
            max_hold_bars=10,
        ),
        dsl_b=_make_dsl_dict(
            name="rsi_b_12bar",
            entry_conds=[{"factor": "rsi_14", "op": "<", "value": 30}],
            exit_conds=[{"factor": "rsi_14", "op": ">", "value": 50}],
            max_hold_bars=12,
        ),
        description="Same factor set + same conditions, only max_hold_bars differs",
    ))

    # ---- Class C3: direction-flip — SAME factor set; distinct ----
    # Same single factor, opposite direction. Pass structural gate
    # (factor-set equal) but should be flagged as DISTINCT by cosine
    # because NL serializer renders direction distinctly.
    pairs.append(CalibrationPair(
        pair_id="C3_rsi_long_vs_short",
        label="distinct",
        distribution_class="C3_direction_flip_same_factor_set",
        dsl_a=_make_dsl_dict(
            name="rsi_oversold",
            entry_conds=[{"factor": "rsi_14", "op": "<", "value": 30}],
            exit_conds=[{"factor": "rsi_14", "op": ">", "value": 50}],
        ),
        dsl_b=_make_dsl_dict(
            name="rsi_overbought",
            entry_conds=[{"factor": "rsi_14", "op": ">", "value": 70}],
            exit_conds=[{"factor": "rsi_14", "op": "<", "value": 50}],
        ),
        description="RSI oversold long vs overbought short — same factor, opposite direction",
    ))
    pairs.append(CalibrationPair(
        pair_id="C3_sma_above_vs_below",
        label="distinct",
        distribution_class="C3_direction_flip_same_factor_set",
        dsl_a=_make_dsl_dict(
            name="sma_above",
            entry_conds=[{"factor": "sma_20", "op": ">", "value": "close"}],
            exit_conds=[{"factor": "sma_20", "op": "<", "value": "close"}],
        ),
        dsl_b=_make_dsl_dict(
            name="sma_below",
            entry_conds=[{"factor": "sma_20", "op": "<", "value": "close"}],
            exit_conds=[{"factor": "sma_20", "op": ">", "value": "close"}],
        ),
        description="SMA above close vs SMA below close — opposite direction",
    ))
    pairs.append(CalibrationPair(
        pair_id="C3_volume_high_vs_low",
        label="distinct",
        distribution_class="C3_direction_flip_same_factor_set",
        dsl_a=_make_dsl_dict(
            name="vol_high",
            entry_conds=[{"factor": "volume_zscore_24h", "op": ">", "value": 1.5}],
            exit_conds=[{"factor": "volume_zscore_24h", "op": "<", "value": 0.5}],
        ),
        dsl_b=_make_dsl_dict(
            name="vol_low",
            entry_conds=[{"factor": "volume_zscore_24h", "op": "<", "value": -1.5}],
            exit_conds=[{"factor": "volume_zscore_24h", "op": ">", "value": -0.5}],
        ),
        description="Volume z-score high vs low — opposite direction",
    ))
    pairs.append(CalibrationPair(
        pair_id="C3_zscore_above_vs_below",
        label="distinct",
        distribution_class="C3_direction_flip_same_factor_set",
        dsl_a=_make_dsl_dict(
            name="zscore_extreme_high",
            entry_conds=[{"factor": "zscore_48", "op": ">", "value": 2.0}],
            exit_conds=[{"factor": "zscore_48", "op": "<", "value": 0.5}],
        ),
        dsl_b=_make_dsl_dict(
            name="zscore_extreme_low",
            entry_conds=[{"factor": "zscore_48", "op": "<", "value": -2.0}],
            exit_conds=[{"factor": "zscore_48", "op": ">", "value": -0.5}],
        ),
        description="Z-score extreme high vs extreme low — opposite direction",
    ))
    pairs.append(CalibrationPair(
        pair_id="C3_macd_pos_vs_neg",
        label="distinct",
        distribution_class="C3_direction_flip_same_factor_set",
        dsl_a=_make_dsl_dict(
            name="macd_pos",
            entry_conds=[{"factor": "macd_hist", "op": ">", "value": 0}],
            exit_conds=[{"factor": "macd_hist", "op": "<", "value": 0}],
        ),
        dsl_b=_make_dsl_dict(
            name="macd_neg",
            entry_conds=[{"factor": "macd_hist", "op": "<", "value": 0}],
            exit_conds=[{"factor": "macd_hist", "op": ">", "value": 0}],
        ),
        description="MACD histogram positive vs negative — opposite direction",
    ))

    # ---- Class C1: parameter variation — DIFFERENT factor sets ----
    # Different SMA windows; treated as different factors by the registry.
    # Compound gate FAILS at structural side → NOT flagged → CORRECT distinct.
    pairs.append(CalibrationPair(
        pair_id="C1_sma_20_vs_24",
        label="distinct",
        distribution_class="C1_param_variation_diff_factor_set",
        dsl_a=_make_dsl_dict(
            name="sma_20_long",
            entry_conds=[{"factor": "sma_20", "op": ">", "value": "close"}],
            exit_conds=[{"factor": "sma_20", "op": "<", "value": "close"}],
        ),
        dsl_b=_make_dsl_dict(
            name="sma_24_long",
            entry_conds=[{"factor": "sma_24", "op": ">", "value": "close"}],
            exit_conds=[{"factor": "sma_24", "op": "<", "value": "close"}],
        ),
        description="SMA(20) vs SMA(24) — different factor names; structural gate filters",
    ))
    pairs.append(CalibrationPair(
        pair_id="C1_sma_20_vs_50",
        label="distinct",
        distribution_class="C1_param_variation_diff_factor_set",
        dsl_a=_make_dsl_dict(
            name="sma_20_long",
            entry_conds=[{"factor": "sma_20", "op": ">", "value": "close"}],
            exit_conds=[{"factor": "sma_20", "op": "<", "value": "close"}],
        ),
        dsl_b=_make_dsl_dict(
            name="sma_50_long",
            entry_conds=[{"factor": "sma_50", "op": ">", "value": "close"}],
            exit_conds=[{"factor": "sma_50", "op": "<", "value": "close"}],
        ),
        description="SMA(20) vs SMA(50) — different factor names",
    ))
    pairs.append(CalibrationPair(
        pair_id="C1_ema_12_vs_26",
        label="distinct",
        distribution_class="C1_param_variation_diff_factor_set",
        dsl_a=_make_dsl_dict(
            name="ema_12_long",
            entry_conds=[{"factor": "ema_12", "op": ">", "value": "close"}],
            exit_conds=[{"factor": "ema_12", "op": "<", "value": "close"}],
        ),
        dsl_b=_make_dsl_dict(
            name="ema_26_long",
            entry_conds=[{"factor": "ema_26", "op": ">", "value": "close"}],
            exit_conds=[{"factor": "ema_26", "op": "<", "value": "close"}],
        ),
        description="EMA(12) vs EMA(26) — different factor names",
    ))
    pairs.append(CalibrationPair(
        pair_id="C1_return_1h_vs_24h",
        label="distinct",
        distribution_class="C1_param_variation_diff_factor_set",
        dsl_a=_make_dsl_dict(
            name="ret_1h_pos",
            entry_conds=[{"factor": "return_1h", "op": ">", "value": 0.01}],
            exit_conds=[{"factor": "return_1h", "op": "<", "value": 0}],
        ),
        dsl_b=_make_dsl_dict(
            name="ret_24h_pos",
            entry_conds=[{"factor": "return_24h", "op": ">", "value": 0.01}],
            exit_conds=[{"factor": "return_24h", "op": "<", "value": 0}],
        ),
        description="return_1h vs return_24h — different factor names",
    ))

    # ---- Class C4: factor-swap (different families) — distinct ----
    pairs.append(CalibrationPair(
        pair_id="C4_sma_vs_rsi",
        label="distinct",
        distribution_class="C4_factor_swap_diff_factor_set",
        dsl_a=_make_dsl_dict(
            name="sma_long",
            entry_conds=[{"factor": "sma_20", "op": ">", "value": "close"}],
            exit_conds=[{"factor": "sma_20", "op": "<", "value": "close"}],
        ),
        dsl_b=_make_dsl_dict(
            name="rsi_oversold",
            entry_conds=[{"factor": "rsi_14", "op": "<", "value": 30}],
            exit_conds=[{"factor": "rsi_14", "op": ">", "value": 50}],
        ),
        description="SMA momentum vs RSI mean-reversion — different families",
    ))
    pairs.append(CalibrationPair(
        pair_id="C4_macd_vs_bb",
        label="distinct",
        distribution_class="C4_factor_swap_diff_factor_set",
        dsl_a=_make_dsl_dict(
            name="macd_signal",
            entry_conds=[{"factor": "macd_hist", "op": ">", "value": 0}],
            exit_conds=[{"factor": "macd_hist", "op": "<", "value": 0}],
        ),
        dsl_b=_make_dsl_dict(
            name="bb_squeeze",
            entry_conds=[{"factor": "bb_upper_24_2", "op": "<", "value": "close"}],
            exit_conds=[{"factor": "bb_upper_24_2", "op": ">", "value": "close"}],
        ),
        description="MACD vs Bollinger Bands — different families",
    ))
    pairs.append(CalibrationPair(
        pair_id="C4_volume_vs_volatility",
        label="distinct",
        distribution_class="C4_factor_swap_diff_factor_set",
        dsl_a=_make_dsl_dict(
            name="vol_surge",
            entry_conds=[{"factor": "volume_zscore_24h", "op": ">", "value": 1.5}],
            exit_conds=[{"factor": "volume_zscore_24h", "op": "<", "value": 0.5}],
        ),
        dsl_b=_make_dsl_dict(
            name="vol_spike",
            entry_conds=[{"factor": "realized_vol_24h", "op": ">", "value": 0.02}],
            exit_conds=[{"factor": "realized_vol_24h", "op": "<", "value": 0.01}],
        ),
        description="Volume z-score vs realized vol — different factor families",
    ))
    pairs.append(CalibrationPair(
        pair_id="C4_atr_vs_zscore",
        label="distinct",
        distribution_class="C4_factor_swap_diff_factor_set",
        dsl_a=_make_dsl_dict(
            name="atr_high",
            entry_conds=[{"factor": "atr_14", "op": ">", "value": 100}],
            exit_conds=[{"factor": "atr_14", "op": "<", "value": 80}],
        ),
        dsl_b=_make_dsl_dict(
            name="zscore_extreme",
            entry_conds=[{"factor": "zscore_48", "op": ">", "value": 2.0}],
            exit_conds=[{"factor": "zscore_48", "op": "<", "value": 0.5}],
        ),
        description="ATR vs Z-score — different volatility measures",
    ))
    pairs.append(CalibrationPair(
        pair_id="C4_time_vs_price",
        label="distinct",
        distribution_class="C4_factor_swap_diff_factor_set",
        dsl_a=_make_dsl_dict(
            name="time_feature",
            entry_conds=[{"factor": "hour_of_day", "op": "==", "value": 9}],
            exit_conds=[{"factor": "hour_of_day", "op": "==", "value": 16}],
        ),
        dsl_b=_make_dsl_dict(
            name="price_momentum",
            entry_conds=[{"factor": "sma_20", "op": ">", "value": "close"}],
            exit_conds=[{"factor": "sma_20", "op": "<", "value": "close"}],
        ),
        description="Time-of-day vs price momentum — totally different concepts",
    ))

    # ---- Class C5: scale-shift (different timescales of same family) — distinct ----
    pairs.append(CalibrationPair(
        pair_id="C5_return_1h_vs_168h",
        label="distinct",
        distribution_class="C5_scale_shift_diff_factor_set",
        dsl_a=_make_dsl_dict(
            name="ret_1h_pos",
            entry_conds=[{"factor": "return_1h", "op": ">", "value": 0.01}],
            exit_conds=[{"factor": "return_1h", "op": "<", "value": 0}],
        ),
        dsl_b=_make_dsl_dict(
            name="ret_168h_pos",
            entry_conds=[{"factor": "return_168h", "op": ">", "value": 0.01}],
            exit_conds=[{"factor": "return_168h", "op": "<", "value": 0}],
        ),
        description="Return 1h vs 168h — different timescales (168x scale shift)",
    ))
    pairs.append(CalibrationPair(
        pair_id="C5_sma_20_vs_sma_50_short",
        label="distinct",
        distribution_class="C5_scale_shift_diff_factor_set",
        dsl_a=_make_dsl_dict(
            name="sma_20_fast",
            entry_conds=[{"factor": "sma_20", "op": ">", "value": "close"}],
            exit_conds=[{"factor": "sma_20", "op": "<", "value": "close"}],
            max_hold_bars=5,
        ),
        dsl_b=_make_dsl_dict(
            name="sma_50_slow",
            entry_conds=[{"factor": "sma_50", "op": ">", "value": "close"}],
            exit_conds=[{"factor": "sma_50", "op": "<", "value": "close"}],
            max_hold_bars=100,
        ),
        description="SMA(20) fast 5-bar hold vs SMA(50) slow 100-bar hold",
    ))

    # More C2 threshold-variation near-dups to balance counts
    pairs.append(CalibrationPair(
        pair_id="C2_sma_close_v_threshold_var",
        label="near_dup",
        distribution_class="C2_threshold_variation_same_factor_set",
        dsl_a=_make_dsl_dict(
            name="ret_var_a",
            entry_conds=[{"factor": "return_24h", "op": ">", "value": 0.02}],
            exit_conds=[{"factor": "return_24h", "op": "<", "value": 0}],
        ),
        dsl_b=_make_dsl_dict(
            name="ret_var_b",
            entry_conds=[{"factor": "return_24h", "op": ">", "value": 0.025}],
            exit_conds=[{"factor": "return_24h", "op": "<", "value": 0}],
        ),
        description="Return 24h threshold 0.02 vs 0.025 — same factor set",
    ))
    pairs.append(CalibrationPair(
        pair_id="C2_ema_threshold_var",
        label="near_dup",
        distribution_class="C2_threshold_variation_same_factor_set",
        dsl_a=_make_dsl_dict(
            name="ema_12_breakout_a",
            entry_conds=[{"factor": "ema_12", "op": ">", "value": "close"}],
            exit_conds=[{"factor": "ema_12", "op": "<", "value": "close"}],
            max_hold_bars=8,
        ),
        dsl_b=_make_dsl_dict(
            name="ema_12_breakout_b",
            entry_conds=[{"factor": "ema_12", "op": ">", "value": "close"}],
            exit_conds=[{"factor": "ema_12", "op": "<", "value": "close"}],
            max_hold_bars=12,
        ),
        description="EMA(12) breakout, max_hold 8 vs 12 — same factor set, only hold differs",
    ))
    pairs.append(CalibrationPair(
        pair_id="C2_multi_cond_threshold",
        label="near_dup",
        distribution_class="C2_threshold_variation_same_factor_set",
        dsl_a=_make_dsl_dict(
            name="rsi_vol_a",
            entry_conds=[
                {"factor": "rsi_14", "op": "<", "value": 30},
                {"factor": "volume_zscore_24h", "op": ">", "value": 1.5},
            ],
            exit_conds=[{"factor": "rsi_14", "op": ">", "value": 50}],
        ),
        dsl_b=_make_dsl_dict(
            name="rsi_vol_b",
            entry_conds=[
                {"factor": "rsi_14", "op": "<", "value": 31},
                {"factor": "volume_zscore_24h", "op": ">", "value": 1.5},
            ],
            exit_conds=[{"factor": "rsi_14", "op": ">", "value": 50}],
        ),
        description="RSI<30+vol vs RSI<31+vol — same factor set {rsi_14, volume_zscore_24h}, RSI threshold differs",
    ))
    pairs.append(CalibrationPair(
        pair_id="C2_zscore_exit_var",
        label="near_dup",
        distribution_class="C2_threshold_variation_same_factor_set",
        dsl_a=_make_dsl_dict(
            name="zscore_a",
            entry_conds=[{"factor": "zscore_48", "op": ">", "value": 2.0}],
            exit_conds=[{"factor": "zscore_48", "op": "<", "value": 0.5}],
        ),
        dsl_b=_make_dsl_dict(
            name="zscore_b",
            entry_conds=[{"factor": "zscore_48", "op": ">", "value": 2.0}],
            exit_conds=[{"factor": "zscore_48", "op": "<", "value": 1.0}],
        ),
        description="Z-score same entry, exit threshold 0.5 vs 1.0 — same factor set",
    ))
    pairs.append(CalibrationPair(
        pair_id="C2_atr_op_var",
        label="near_dup",
        distribution_class="C2_threshold_variation_same_factor_set",
        dsl_a=_make_dsl_dict(
            name="atr_a",
            entry_conds=[{"factor": "atr_14", "op": ">", "value": 100}],
            exit_conds=[{"factor": "atr_14", "op": "<=", "value": 80}],
        ),
        dsl_b=_make_dsl_dict(
            name="atr_b",
            entry_conds=[{"factor": "atr_14", "op": ">=", "value": 100}],
            exit_conds=[{"factor": "atr_14", "op": "<=", "value": 80}],
        ),
        description="ATR > 100 vs ATR >= 100 — same factor set, edge case for operator boundary",
    ))
    pairs.append(CalibrationPair(
        pair_id="C2_volume_exit_var",
        label="near_dup",
        distribution_class="C2_threshold_variation_same_factor_set",
        dsl_a=_make_dsl_dict(
            name="vol_a",
            entry_conds=[{"factor": "volume_zscore_24h", "op": ">", "value": 1.5}],
            exit_conds=[{"factor": "volume_zscore_24h", "op": "<", "value": 0.5}],
        ),
        dsl_b=_make_dsl_dict(
            name="vol_b",
            entry_conds=[{"factor": "volume_zscore_24h", "op": ">", "value": 1.5}],
            exit_conds=[{"factor": "volume_zscore_24h", "op": "<", "value": 0.8}],
        ),
        description="Volume z-score same entry, exit 0.5 vs 0.8 — same factor set",
    ))
    pairs.append(CalibrationPair(
        pair_id="C2_returns_threshold_var",
        label="near_dup",
        distribution_class="C2_threshold_variation_same_factor_set",
        dsl_a=_make_dsl_dict(
            name="ret168_a",
            entry_conds=[{"factor": "return_168h", "op": ">", "value": 0.05}],
            exit_conds=[{"factor": "return_168h", "op": "<", "value": 0}],
        ),
        dsl_b=_make_dsl_dict(
            name="ret168_b",
            entry_conds=[{"factor": "return_168h", "op": ">", "value": 0.06}],
            exit_conds=[{"factor": "return_168h", "op": "<", "value": 0}],
        ),
        description="Return 168h threshold 0.05 vs 0.06 — same factor set",
    ))

    # More C4 factor-swap distincts
    pairs.append(CalibrationPair(
        pair_id="C4_volatility_vs_return",
        label="distinct",
        distribution_class="C4_factor_swap_diff_factor_set",
        dsl_a=_make_dsl_dict(
            name="vol_filter",
            entry_conds=[{"factor": "realized_vol_24h", "op": "<", "value": 0.01}],
            exit_conds=[{"factor": "realized_vol_24h", "op": ">", "value": 0.02}],
        ),
        dsl_b=_make_dsl_dict(
            name="ret_filter",
            entry_conds=[{"factor": "return_24h", "op": ">", "value": 0.01}],
            exit_conds=[{"factor": "return_24h", "op": "<", "value": 0}],
        ),
        description="Realized vol low-filter vs return momentum — different families",
    ))
    pairs.append(CalibrationPair(
        pair_id="C4_dayofweek_vs_macd",
        label="distinct",
        distribution_class="C4_factor_swap_diff_factor_set",
        dsl_a=_make_dsl_dict(
            name="dow_filter",
            entry_conds=[{"factor": "day_of_week", "op": "==", "value": 1}],
            exit_conds=[{"factor": "day_of_week", "op": "==", "value": 5}],
        ),
        dsl_b=_make_dsl_dict(
            name="macd_signal",
            entry_conds=[{"factor": "macd_hist", "op": ">", "value": 0}],
            exit_conds=[{"factor": "macd_hist", "op": "<", "value": 0}],
        ),
        description="Day-of-week filter vs MACD histogram — different factor families",
    ))

    return pairs


def factor_set_equal(dsl_a: StrategyDSL, dsl_b: StrategyDSL) -> bool:
    """Compound gate structural side per amendment §2 B-6: exact factor-set match."""
    fa = frozenset(extract_factors(dsl_a))
    fb = frozenset(extract_factors(dsl_b))
    return fa == fb


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Cosine similarity between two embedding vectors."""
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def model_artifact_sha(model: SentenceTransformer) -> str:
    """Compute SHA-256 of model's first parameter tensor for artifact identification."""
    first_param = next(iter(model.named_parameters()))[1].detach().cpu().numpy()
    return hashlib.sha256(first_param.tobytes()).hexdigest()[:16]


def run_calibration() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    pair_specs = build_fixture_corpus()
    print(f"[calibrate-v2] loading model: {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME)
    model_sha = model_artifact_sha(model)
    embed_dim = model.get_sentence_embedding_dimension()
    print(f"[calibrate-v2] model loaded, dim={embed_dim}, first-param SHA={model_sha}")

    # Validate DSL dicts into StrategyDSL instances + compute NL + cosine + factor-set
    print(f"[calibrate-v2] computing NL + embeddings for {2 * len(pair_specs)} DSLs")
    pair_records: list[dict] = []
    for p in pair_specs:
        dsl_a = StrategyDSL.model_validate(p.dsl_a)
        dsl_b = StrategyDSL.model_validate(p.dsl_b)
        nl_a = nl_serialize_dsl(dsl_a)
        nl_b = nl_serialize_dsl(dsl_b)
        emb_a = model.encode(nl_a, convert_to_numpy=True, show_progress_bar=False)
        emb_b = model.encode(nl_b, convert_to_numpy=True, show_progress_bar=False)
        cos = cosine_similarity(emb_a, emb_b)
        fs_equal = factor_set_equal(dsl_a, dsl_b)
        pair_records.append({
            "pair_id": p.pair_id,
            "label": p.label,
            "distribution_class": p.distribution_class,
            "description": p.description,
            "cosine": round(cos, 6),
            "factor_set_equal": fs_equal,
            "nl_a": nl_a,
            "nl_b": nl_b,
        })
        gate_status = "PASS_FS" if fs_equal else "FAIL_FS"
        print(
            f"  {p.pair_id} [{p.label}/{p.distribution_class}] "
            f"cosine={cos:.4f} fs={gate_status}"
        )

    # Sweep τ_c — compound gate: cosine ≥ τ_c AND factor_set_equal
    print(f"[calibrate-v2] sweeping τ_c ∈ {SWEEP_TAUS} (compound AND-gate)")
    sweep: list[dict] = []
    for tau in SWEEP_TAUS:
        tp = sum(
            1 for r in pair_records
            if r["label"] == "near_dup"
            and r["cosine"] >= tau
            and r["factor_set_equal"]
        )
        fn = sum(
            1 for r in pair_records
            if r["label"] == "near_dup"
            and not (r["cosine"] >= tau and r["factor_set_equal"])
        )
        fp = sum(
            1 for r in pair_records
            if r["label"] == "distinct"
            and r["cosine"] >= tau
            and r["factor_set_equal"]
        )
        tn = sum(
            1 for r in pair_records
            if r["label"] == "distinct"
            and not (r["cosine"] >= tau and r["factor_set_equal"])
        )
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
        sweep.append({
            "tau_c": tau, "tp": tp, "fp": fp, "fn": fn, "tn": tn,
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
        })
        print(f"  τ_c={tau:.2f} TP={tp} FP={fp} FN={fn} TN={tn} P={precision:.3f} R={recall:.3f} F1={f1:.3f}")

    # Choose τ_c per amendment §2 B-1 selection rule
    best_idx = max(
        range(len(sweep)),
        key=lambda i: (sweep[i]["f1"], -sweep[i]["tau_c"]),
    )
    chosen_tau = sweep[best_idx]["tau_c"]
    chosen_metrics = sweep[best_idx]

    # Conjunctive no-further-amendment trigger
    trigger_amendment = not (
        0.85 <= chosen_tau <= 0.99 and chosen_metrics["f1"] >= 0.85
    )

    print(f"[calibrate-v2] chosen τ_c = {chosen_tau} (F1={chosen_metrics['f1']:.4f})")
    if trigger_amendment:
        print(
            "[calibrate-v2] !! TRIGGERS sub-spec amendment v2 register-event "
            "(conjunctive trigger failed)"
        )
    else:
        print("[calibrate-v2] no-further-amendment criteria met")

    # Per-class breakdown
    by_class: dict[str, dict] = {}
    for r in pair_records:
        cls = r["distribution_class"]
        by_class.setdefault(cls, {"near_dup": 0, "distinct": 0, "fs_eq": 0, "fs_neq": 0})
        by_class[cls][r["label"]] += 1
        by_class[cls]["fs_eq" if r["factor_set_equal"] else "fs_neq"] += 1

    timestamp_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Build corpus archive
    corpus_records = [
        {
            "pair_id": p.pair_id,
            "label": p.label,
            "distribution_class": p.distribution_class,
            "description": p.description,
            "dsl_a": p.dsl_a,
            "dsl_b": p.dsl_b,
        }
        for p in pair_specs
    ]

    (OUTPUT_DIR / "fixture_corpus.json").write_text(
        json.dumps(corpus_records, indent=2),
        encoding="utf-8",
    )

    (OUTPUT_DIR / "sweep_results.json").write_text(
        json.dumps({
            "model_name": MODEL_NAME,
            "model_first_param_sha": model_sha,
            "embedding_dim": embed_dim,
            "n_pairs": len(pair_specs),
            "n_near_dup": sum(1 for p in pair_specs if p.label == "near_dup"),
            "n_distinct": sum(1 for p in pair_specs if p.label == "distinct"),
            "calibration_utc": timestamp_utc,
            "sweep_taus": list(SWEEP_TAUS),
            "compound_gate": "cosine ≥ τ_c AND factor_set_equal",
            "tau_s": 1.0,
            "tau_s_status": "DEFINITIONAL (immune from sweep per amendment §2 B-1)",
            "pair_records": pair_records,
            "sweep": sweep,
            "chosen_tau_c": chosen_tau,
            "trigger_amendment_v2": trigger_amendment,
            "no_further_amendment_criteria": {
                "tau_c_in_range": 0.85 <= chosen_tau <= 0.99,
                "f1_floor": chosen_metrics["f1"] >= 0.85,
            },
            "per_class_breakdown": by_class,
            "selection_rule": (
                "Highest F1 across compound-gate sweep (cosine + factor-set equality). "
                "Tie-break: LOWER τ_c (more aggressive dedup; FPs are Critic-overridable "
                "per B-3 quarantine). Conjunctive no-further-amendment trigger: "
                "τ_c ∈ [0.85, 0.99] AND F1 ≥ 0.85."
            ),
        }, indent=2),
        encoding="utf-8",
    )

    note_lines = [
        "# B-T7 Cosine Threshold Re-Calibration — v2 (compound gate)",
        "",
        f"**Calibration timestamp (UTC)**: {timestamp_utc}",
        f"**Model**: `{MODEL_NAME}` (embedding dim {embed_dim})",
        f"**Model first-param SHA-256[:16]**: `{model_sha}`",
        f"**Embed input**: natural-language serializer (`nl_serialize_dsl` per amendment §2 B-4)",
        f"**Gate**: compound AND — `cosine ≥ τ_c AND factor_set_equal` (τ_s = 1.0 DEFINITIONAL per amendment §2 B-1)",
        f"**Pair count**: {len(pair_specs)} ({sum(1 for p in pair_specs if p.label == 'near_dup')} near-dup + {sum(1 for p in pair_specs if p.label == 'distinct')} distinct)",
        f"**Distribution classes**: 5 per amendment §3 W0.3.v2 P-F2 expansion",
        "",
        "## Distribution-class breakdown",
        "",
        "| Class | n | near_dup | distinct | factor_set_equal | factor_set_neq |",
        "|---|---|---|---|---|---|",
    ]
    for cls in sorted(by_class.keys()):
        n_total = by_class[cls]["near_dup"] + by_class[cls]["distinct"]
        note_lines.append(
            f"| {cls} | {n_total} | {by_class[cls]['near_dup']} | {by_class[cls]['distinct']} | "
            f"{by_class[cls]['fs_eq']} | {by_class[cls]['fs_neq']} |"
        )

    note_lines.extend([
        "",
        "## Sweep results (compound AND-gate)",
        "",
        "| τ_c | TP | FP | FN | TN | Precision | Recall | F1 |",
        "|---|---|---|---|---|---|---|---|",
    ])
    for row in sweep:
        note_lines.append(
            f"| {row['tau_c']:.2f} | {row['tp']} | {row['fp']} | {row['fn']} | {row['tn']} | "
            f"{row['precision']:.3f} | {row['recall']:.3f} | {row['f1']:.3f} |"
        )

    note_lines.extend([
        "",
        "## Chosen τ_c",
        "",
        f"**τ_c = {chosen_tau}** (F1 = {chosen_metrics['f1']:.4f}, "
        f"precision = {chosen_metrics['precision']:.3f}, recall = {chosen_metrics['recall']:.3f})",
        "",
        "**Selection rule**: highest F1 across compound-gate sweep; tie-break prefers LOWER τ_c.",
        "",
        "## Conjunctive no-further-amendment trigger",
        "",
        f"- (i) τ_c ∈ [0.85, 0.99]: **{0.85 <= chosen_tau <= 0.99}** (chosen {chosen_tau})",
        f"- (ii) F1 ≥ 0.85: **{chosen_metrics['f1'] >= 0.85}** (F1 = {chosen_metrics['f1']:.4f})",
        "",
    ])
    if not trigger_amendment:
        note_lines.append(
            "**Both conditions met → NO further amendment required. B-1 default confirmed at τ_c = "
            f"{chosen_tau}**, F1 = {chosen_metrics['f1']:.4f}."
        )
    else:
        note_lines.append(
            "**At least one condition FAILED → SUB-SPEC AMENDMENT v2 register-event TRIGGERED** "
            "per amendment §6.1 cadence guard. Charlie register-event authorization required for v2 entry; "
            "Path (c) Track B drop deliberation MUST be a first-class alternative at v2."
        )

    note_lines.extend([
        "",
        "## Per-pair details (sorted by cosine)",
        "",
        "| Pair ID | Class | Label | Cosine | FS Equal | Description |",
        "|---|---|---|---|---|---|",
    ])
    for r in sorted(pair_records, key=lambda x: -x["cosine"]):
        fs_str = "✓" if r["factor_set_equal"] else "✗"
        note_lines.append(
            f"| `{r['pair_id']}` | {r['distribution_class']} | {r['label']} | "
            f"{r['cosine']:.4f} | {fs_str} | {r['description']} |"
        )

    note_lines.extend([
        "",
        "## Discipline locks honored",
        "",
        "- B-Lock-1: separate code path from D3 canonicalization (semantic_dedup.py distinct from hypothesis_hash.py)",
        "- B-Lock-2 (extended sibling clause): NL serializer traverses StrategyDSL directly; no import of hypothesis_hash",
        "- B-Lock-6: sentence-transformers local CPU; no remote embedding API",
        "- B-Lock-7: model artifact SHA recorded above; install-time-only network egress",
        "- HARD CONSTRAINT: fixture corpus is synthetic; no Phase 2C / validation / test / 2022-regime data ingested",
        "",
        "## Compared to W0.3 (predecessor calibration)",
        "",
        "- W0.3 (commit `a8d10ef`): D3-canonical JSON input, cosine-only gate, N=10 fixture, F1 = 0.7692 at chosen τ = 0.90",
        f"- W0.3.v2 (this calibration): NL serializer input, compound AND-gate, N={len(pair_specs)} fixture (5-class), F1 = {chosen_metrics['f1']:.4f} at chosen τ_c = {chosen_tau}",
        "",
        "## Reproducibility",
        "",
        f"Run: `python scripts/btau_calibrate_v2.py`. Deterministic given same model file.",
        f"Outputs at `{OUTPUT_DIR.relative_to(REPO_ROOT)}/`: this file + `fixture_corpus.json` + `sweep_results.json`.",
    ])

    (OUTPUT_DIR / "CALIBRATION_NOTE_V2.md").write_text(
        "\n".join(note_lines) + "\n",
        encoding="utf-8",
    )

    print(f"[calibrate-v2] outputs written to {OUTPUT_DIR.relative_to(REPO_ROOT)}/")
    print(f"[calibrate-v2] CHOSEN τ_c = {chosen_tau}, F1 = {chosen_metrics['f1']:.4f}")


if __name__ == "__main__":
    sys.exit(run_calibration() or 0)

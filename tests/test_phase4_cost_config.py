"""Tests for Phase 4 sealed execution-config YAML files + plumbing.

Per docs/superpowers/plans/2026-05-09-phase4-implementation-arc.md Task 3.

The 4 sealed YAML files at config/execution_phase4_*bps.yaml lock the
4 cost configurations PHASE4_PLAN §1.4 specifies:
- 07bps: PHASE2C_15-comparability research-time (dual-report)
- 13bps: sensitivity low (slippage -2 from 15 base)
- 15bps: realistic base (Binance VIP 0 taker 10 + slippage 5) — §1.5 basis
- 17bps: sensitivity high (slippage +2 from 15 base)

Tests assert PLAN §1.4 anchors at file-load + ConstantSlippage register;
catches any future cycle that mutates the sealed values.
"""
from __future__ import annotations

import inspect
from pathlib import Path

import pytest

from backtest.slippage import ConstantSlippage, load_execution_config

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PHASE4_CONFIGS = {
    7: PROJECT_ROOT / "config" / "execution_phase4_07bps.yaml",
    13: PROJECT_ROOT / "config" / "execution_phase4_13bps.yaml",
    15: PROJECT_ROOT / "config" / "execution_phase4_15bps.yaml",
    17: PROJECT_ROOT / "config" / "execution_phase4_17bps.yaml",
}


# ---------------------------------------------------------------------------
# Sealed YAML existence + total_bps integrity (PHASE4_PLAN §1.4 anchors).
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("expected_bps,config_path", PHASE4_CONFIGS.items())
def test_phase4_config_file_exists(expected_bps, config_path):
    """Each Phase 4 cost-config YAML file must exist."""
    assert config_path.exists(), (
        f"Missing: {config_path.relative_to(PROJECT_ROOT)} "
        f"(PHASE4_PLAN §1.4 requires sealed cost config at {expected_bps}bps)"
    )


@pytest.mark.parametrize("expected_bps,config_path", PHASE4_CONFIGS.items())
def test_phase4_config_total_bps_matches_phase4_plan(expected_bps, config_path):
    """ConstantSlippage.from_config must yield PLAN §1.4 anchor values."""
    config = load_execution_config(config_path)
    model = ConstantSlippage.from_config(config)
    assert model.total_bps == float(expected_bps), (
        f"Config {config_path.name}: expected {expected_bps}bps "
        f"per PHASE4_PLAN §1.4 but got {model.total_bps}"
    )


# ---------------------------------------------------------------------------
# Per-config decomposition tests (lock the fee + slippage split per PLAN §1.4).
# ---------------------------------------------------------------------------


def test_phase4_15bps_realistic_base_decomposition():
    """PHASE4_PLAN §1.4 base: 10bps taker + 5bps slippage = 15bps per side.

    THIS CONFIG IS THE BASIS FOR PHASE 4 §1.5 SUCCESS CRITERION.
    """
    config = load_execution_config(PHASE4_CONFIGS[15])
    assert config["cost_model"]["default_fee_bps"] == 10.0
    assert config["cost_model"]["slippage_bps"] == 5.0
    model = ConstantSlippage.from_config(config)
    assert model.fee_bps == 10.0
    assert model.slippage_bps == 5.0
    assert model.effective_commission == 0.0015  # 15bps as decimal


def test_phase4_07bps_research_time_decomposition():
    """PHASE4_PLAN §1.4 research-time: 4bps fee + 3bps slip = 7bps (PHASE2C_15-comparability).

    Dual-reporting only — NOT the Phase 4 §1.5 success criterion basis.
    """
    config = load_execution_config(PHASE4_CONFIGS[7])
    assert config["cost_model"]["default_fee_bps"] == 4.0
    assert config["cost_model"]["slippage_bps"] == 3.0


def test_phase4_13bps_sensitivity_low_decomposition():
    """PHASE4_PLAN §1.4 sensitivity low: 10bps fee + 3bps slip = 13bps (slippage -2 from base)."""
    config = load_execution_config(PHASE4_CONFIGS[13])
    assert config["cost_model"]["default_fee_bps"] == 10.0
    assert config["cost_model"]["slippage_bps"] == 3.0


def test_phase4_17bps_sensitivity_high_decomposition():
    """PHASE4_PLAN §1.4 sensitivity high: 10bps fee + 7bps slip = 17bps (slippage +2 from base)."""
    config = load_execution_config(PHASE4_CONFIGS[17])
    assert config["cost_model"]["default_fee_bps"] == 10.0
    assert config["cost_model"]["slippage_bps"] == 7.0


# ---------------------------------------------------------------------------
# Plumbing: --execution-config flag + run_regime_holdout signature.
# ---------------------------------------------------------------------------


def test_run_regime_holdout_accepts_execution_config_path():
    """run_regime_holdout must accept execution_config_path kwarg with default None.

    Default None preserves backward compat: existing callers (PHASE2C_6 +
    PHASE2C_7.1 + PHASE2C_8.1 + PHASE2C_15) continue using the default
    execution.yaml path; Phase 4 callers pass an override path.
    """
    from backtest.engine import run_regime_holdout

    sig = inspect.signature(run_regime_holdout)
    assert "execution_config_path" in sig.parameters, (
        "run_regime_holdout must accept execution_config_path parameter "
        "to support Phase 4 cost-config override."
    )
    # Default must be None so existing callers are unaffected.
    assert sig.parameters["execution_config_path"].default is None

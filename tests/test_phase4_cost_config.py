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


# ---------------------------------------------------------------------------
# b2 integration test: cost-override value-flow (Phase 4 implementation arc
# Task 3 Step A; per advisor reviewer cycle adjudication 2026-05-09).
# ---------------------------------------------------------------------------
#
# This test catches the "signature plumbed but value silently dropped"
# failure mode that the signature-shape tests above DO NOT cover. The
# 13 tests above verify:
#   - 4 sealed YAMLs exist + decompose correctly
#   - run_regime_holdout signature accepts execution_config_path kwarg
# But none verify that passing a non-default execution_config_path
# actually changes the cost applied to the backtest. That is the
# substantively load-bearing concern at fire-time: if the override
# value is silently dropped at any link in the chain (CLI → kwarg →
# kwarg → load_execution_config → ConstantSlippage), both 7bps and
# 17bps configs would silently produce identical default-cost runs.
#
# The test fires real backtests against tiny synthetic fixtures and
# asserts the override changes the actual broker commission applied.
# Cost ~1-2 seconds for 4 backtest runs at 30 bars each. Catches the
# entire chain end-to-end without subprocess overhead.


def _make_b2_test_parquet(tmp_path: Path, n_hours: int = 30) -> Path:
    """Create a tiny synthetic parquet for cost-override value-flow tests."""
    import numpy as np
    import pandas as pd

    tmp_path.mkdir(parents=True, exist_ok=True)
    timestamps = pd.date_range(
        start="2024-01-01", periods=n_hours, freq="h", tz="UTC"
    )
    df = pd.DataFrame({
        "open_time_utc": timestamps.astype("datetime64[ms, UTC]"),
        "open": [100.0 + i for i in range(n_hours)],
        "high": [110.0 + i for i in range(n_hours)],
        "low": [90.0 + i for i in range(n_hours)],
        "close": [105.0 + i for i in range(n_hours)],
        "volume": [1000.0] * n_hours,
        "quote_volume": [100_000.0] * n_hours,
        "trade_count": np.arange(5000, 5000 + n_hours, dtype="int64"),
        "ingested_at_utc": pd.Timestamp.now(tz="UTC").floor("ms"),
        "source": pd.array(["binance_vision"] * n_hours, dtype="string"),
    })
    df["ingested_at_utc"] = df["ingested_at_utc"].astype("datetime64[ms, UTC]")
    path = tmp_path / "b2_test.parquet"
    df.to_parquet(path, engine="pyarrow", index=False)
    return path


def _run_b2_backtest_with_config(
    tmp_path: Path,
    execution_config_path: Path | None,
):
    """Fire a tiny backtest with the given execution config; return result.

    Uses a minimal _BuyOnBar5-style strategy + 30-bar synthetic parquet.
    All runs use IDENTICAL fixtures except for the execution_config
    override — any difference in trade pnl reflects cost-override
    application (not market data variation).
    """
    from datetime import datetime, timezone

    from backtest.engine import run_backtest
    from strategies.template import BaseStrategy

    class _B2BuyOnBar5(BaseStrategy):
        """Simple deterministic strategy: buy bar 5, close bar 15."""
        STRATEGY_NAME = "b2_test_buy_bar5"
        WARMUP_BARS = 0
        params = (("buy_bar", 5), ("sell_bar", 15))

        def __init__(self):
            self.bar_idx = 0

        def next(self):
            if self.bar_idx == self.p.buy_bar and not self.position:
                self.buy()
            elif self.bar_idx == self.p.sell_bar and self.position:
                self.close()
            self.bar_idx += 1

    parquet_path = _make_b2_test_parquet(tmp_path, n_hours=30)
    return run_backtest(
        strategy_cls=_B2BuyOnBar5,
        start_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
        end_date=datetime(2024, 1, 2, 5, 0, tzinfo=timezone.utc),
        parquet_path=parquet_path,
        write_registry=False,
        execution_config_path=execution_config_path,
    )


def test_b2_cost_override_changes_actual_trade_pnl(tmp_path):
    """b2 integration test: --execution-config actually changes the cost
    applied to the backtest broker.

    Catches the 'signature plumbed but value silently dropped'
    failure class. If the override is silently dropped at any link
    (CLI -> kwarg -> kwarg -> load_execution_config -> ConstantSlippage),
    both runs produce identical default-cost trade pnls and the
    assertion fails.

    Asymmetric assertions:
      - 7bps and 15bps must produce DIFFERENT trade pnls (cost differs)
      - 7bps and 17bps must produce DIFFERENT trade pnls (cost differs)
      - 7bps run with override config must equal 7bps run with no
        override (research-time config IS the default 7bps shape;
        verifies override is applied identically when paths are
        functionally equivalent — value-flow check, not just signature).
    """
    cfg_07 = PHASE4_CONFIGS[7]
    cfg_15 = PHASE4_CONFIGS[15]
    cfg_17 = PHASE4_CONFIGS[17]

    # Fire same backtest fixture with 4 different cost configurations.
    result_default = _run_b2_backtest_with_config(
        tmp_path / "default", execution_config_path=None
    )
    result_07 = _run_b2_backtest_with_config(
        tmp_path / "p07", execution_config_path=cfg_07
    )
    result_15 = _run_b2_backtest_with_config(
        tmp_path / "p15", execution_config_path=cfg_15
    )
    result_17 = _run_b2_backtest_with_config(
        tmp_path / "p17", execution_config_path=cfg_17
    )

    # Each run must produce exactly one trade (deterministic strategy).
    assert len(result_default.trades) == 1
    assert len(result_07.trades) == 1
    assert len(result_15.trades) == 1
    assert len(result_17.trades) == 1

    pnl_default = result_default.trades[0]["pnl"]
    pnl_07 = result_07.trades[0]["pnl"]
    pnl_15 = result_15.trades[0]["pnl"]
    pnl_17 = result_17.trades[0]["pnl"]

    # Value-flow check 1: 7bps override produces same pnl as default
    # (both are 7bps total). Tests that override IS applied (not silently
    # dropped) and IS being read correctly when functionally equivalent.
    assert pnl_default == pytest.approx(pnl_07, rel=1e-6), (
        f"7bps override should match default 7bps; "
        f"override={pnl_07}, default={pnl_default} "
        f"(if these differ, override path may not be reaching broker)"
    )

    # Value-flow check 2: 15bps must produce strictly worse pnl than 7bps
    # (higher cost = worse pnl on a winning trade).
    assert pnl_15 < pnl_07, (
        f"15bps override should produce lower pnl than 7bps default; "
        f"15bps={pnl_15}, 7bps={pnl_07} "
        f"(if 15bps == 7bps, override is NOT being applied at broker — "
        f"silent value-drop failure mode)"
    )

    # Value-flow check 3: 17bps must produce strictly worse pnl than
    # 15bps (sensitivity ordering).
    assert pnl_17 < pnl_15, (
        f"17bps override should produce lower pnl than 15bps; "
        f"17bps={pnl_17}, 15bps={pnl_15}"
    )

    # Value-flow check 4: numerical magnitude of pnl difference reflects
    # the cost difference. For a single round-trip trade with notional N:
    #   cost_difference_per_side = (15 - 7) bps = 8 bps = 0.0008
    #   round_trip_cost_difference = 2 * 0.0008 = 0.0016 of notional
    # The pnl difference 7bps -> 15bps should be roughly proportional
    # to the trade notional. We don't pin exact values (notional varies
    # with sizer + fixture); we just assert the difference is non-trivial
    # and in the right direction.
    pnl_diff_7_to_15 = pnl_07 - pnl_15
    pnl_diff_15_to_17 = pnl_15 - pnl_17
    assert pnl_diff_7_to_15 > 0, "7bps must be better than 15bps"
    assert pnl_diff_15_to_17 > 0, "15bps must be better than 17bps"
    # 8bps gap (7 -> 15) should be ~4x the 2bps gap (15 -> 17).
    # Loose tolerance because of rounding + size effects.
    ratio = pnl_diff_7_to_15 / pnl_diff_15_to_17
    assert 2.0 < ratio < 8.0, (
        f"pnl difference ratio (7->15 vs 15->17) should be ~4 "
        f"(8bps gap vs 2bps gap); got {ratio:.2f} — suggests cost "
        f"override may not be linear in bps as expected"
    )

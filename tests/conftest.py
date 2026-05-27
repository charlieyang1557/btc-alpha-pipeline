# tests/conftest.py — CREATE or APPEND
"""Shared pytest fixtures for B-C-narrow tests + other repo tests."""
import json
from pathlib import Path

import pandas as pd
import pytest

# DEFECT-N2 fix per PFR R2: single source of truth — import from producer.
# Producer's `_strip_markdown_fence` at scripts/run_phase2c_evaluation_gate.py:242
# uses regex-based fence match (_FENCE_RE); conftest must NOT diverge with a
# parallel implementation.
# PFR R3 LOW L2 + PFR R4 MEDIUM N2b + PFR R4 MEDIUM M2 fix (v3.5): module
# import is safe in practice — scripts/run_phase2c_evaluation_gate.py top-of-
# module (lines 75-130) has only import statements + top-level constant
# assignments + ONE benign side-effecting call: line 90's
# `sys.path.insert(0, str(PROJECT_ROOT))` (PROJECT_ROOT resolves to repo root
# via Path(__file__).resolve().parent.parent). The sys.path mutation is
# idempotent (re-running prepends a duplicate but doesn't break import
# resolution) AND the pytest test runner already includes the repo root in
# sys.path by default, so the call is functionally a no-op when imported from
# tests/. No network/disk I/O at import; no `if __name__ == "__main__":`
# block runs at module load. Pre-existing safe-import precedent at
# tests/test_t1_4_backward_compat.py:1323-1326 already exercises this path.
from scripts.run_phase2c_evaluation_gate import _strip_markdown_fence


REPO_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def btc_parquet_path() -> Path:
    """Canonical BTC OHLCV parquet path used by engine tests."""
    return REPO_ROOT / "data" / "raw" / "btcusdt_1h.parquet"


@pytest.fixture
def dsl_bollinger_zscore_reversion():
    """Load cohort_a candidate 18d92ce5d0b40cc7 (mean_reversion strategy
    'bollinger_zscore_reversion') DSL from recovered raw_payloads.

    Used by Phase 0 engine tests as the canonical exemplar.
    """
    from strategies.dsl import StrategyDSL

    response_path = (
        REPO_ROOT
        / "raw_payloads"
        / "batch_4f894318-eb69-48b5-95ef-e22abe3ecdd1"
        / "attempt_0032_response.txt"
    )
    raw_text = response_path.read_text(encoding="utf-8")
    payload = json.loads(_strip_markdown_fence(raw_text))
    return StrategyDSL.model_validate(payload)


@pytest.fixture
def dsl_monday_dip_buy():
    """Load cohort_a candidate 8a2a8f73f71a835e (calendar_effect strategy
    'monday_dip_buy_calendar_effect') DSL from combined synthetic dir at
    position 873. Used as second exemplar for boundary-case tests."""
    from scripts.run_phase2c_evaluation_gate import _load_dsl_from_response
    return _load_dsl_from_response("phase2c_15_main_fire_combined", 873)


@pytest.fixture
def env_config_override_forward_2026() -> dict:
    """B-C-narrow Phase 0 F1 fix: env_config override for forward_2026 regime.

    Required because environments.yaml line 127 declares
    `evaluation_regimes.forward_2026.end: null` (captured at fire-time per
    PHASE4_PLAN §1.2). Engine at backtest/engine.py:2371 calls
    `date.fromisoformat(block["end"])` which crashes with TypeError when None.

    Producer at scripts/run_phase2c_evaluation_gate.py:187-233 (_build_phase4_env_config_override)
    uses identical workaround pattern: pre-fills `forward_2026.end` with
    captured fire-time value before calling run_regime_holdout(..., env_config=<override>, ...).

    Tests adopt same pattern: pass `env_config=env_config_override_forward_2026`
    to every run_regime_holdout(regime_key="evaluation_regimes.forward_2026", ...)
    call. Canonical fire-time `end` value matches original artifact's
    forward_window_end_utc: 2026-04-16T07:00:00Z.
    """
    import yaml
    env_config_path = REPO_ROOT / "config" / "environments.yaml"
    env_config = yaml.safe_load(env_config_path.read_text())
    er = env_config.get("evaluation_regimes", {})
    fwd = er.get("forward_2026")
    if fwd is None:
        raise RuntimeError(
            "forward_2026 block missing from environments.yaml — "
            "expected at config/environments.yaml evaluation_regimes.forward_2026"
        )
    # Fill the null end with canonical fire-time value (matches original
    # artifact's forward_window_end_utc: 2026-04-16T07:00:00Z).
    fwd["end"] = "2026-04-16"
    return env_config

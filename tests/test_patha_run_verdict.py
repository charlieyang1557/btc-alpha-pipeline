"""Tests for the Path A verdict RUN wiring (scripts/patha_run_verdict).

PHASE-D GATING (CRITICAL): the real forward_2026 RUN is a separate Charlie
register (Phase D). ``main()`` MUST refuse to execute unless an explicit
not-yet-set authorization flag is passed; building the orchestrator + unit tests
(mocked engine) is the C4-C7 scope. These tests never run a real backtest:
``_run_backtest`` is mocked so run_verdict exercises the real DSL compile + the
producer + the load_candidate_moments integrity gate + the orchestrator + the
sealed-sha256 invariant — but no real engine / forward_2026 / 6852-row data.
"""
from __future__ import annotations

import itertools
import json

import numpy as np
import pandas as pd
import pytest

import scripts.patha_run_verdict as rv


_counter = itertools.count()


def _fake_backtest_result(**kwargs):
    """A non-degenerate BacktestResult stand-in (varied per call)."""
    rng = np.random.default_rng(next(_counter) + 1)
    n = 320
    idx = pd.date_range("2026-01-01", periods=n, freq="h", tz="UTC")
    rets = rng.normal(0.0001, 0.012, n)
    eq = pd.Series(10_000.0 * np.cumprod(1.0 + rets), index=idx)

    class _R:
        pass

    r = _R()
    r.run_id = f"run_{rng.integers(1_000_000)}"
    r.equity_curve = eq
    r.metrics = {
        "sharpe_ratio": float(rng.normal(0.0, 0.3)),
        "total_trades": int(rng.integers(5, 60)),
        "max_drawdown": 0.1,
        "total_return": 0.02,
    }
    r.start_date = idx[0].to_pydatetime()
    r.end_date = idx[-1].to_pydatetime()
    return r


def _tiny_features(tmp_path) -> str:
    """A train-window (2020) funding-factor frame the per-leg tiers can consume."""
    n = 800
    idx = pd.date_range("2020-01-01", periods=n, freq="h", tz="UTC")
    rng = np.random.default_rng(7)
    df = pd.DataFrame({
        "open_time_utc": idx,
        "return_1h": rng.normal(0, 0.01, n),
        "funding_pct_rank_270": rng.uniform(0, 1, n),
        "funding_sign": rng.choice([-1.0, 0.0, 1.0], n),
        "funding_ewm_60": rng.normal(0, 0.0001, n),
        "funding_ewm_30_pctrank_270": rng.uniform(0, 1, n),
        "decay_linear_close_48": rng.normal(100, 5, n),
        "decay_linear_close_168": rng.normal(100, 5, n),
        "cdf_realized_vol_720": rng.uniform(0, 1, n),
    })
    p = tmp_path / "feat.parquet"
    df.to_parquet(p)
    return str(p)


# ---------------------------------------------------------------------------
# PHASE-D GATE
# ---------------------------------------------------------------------------


def test_main_is_phase_d_gated_and_refuses_to_run():
    # main() must NOT execute the real RUN without explicit Phase-D authorization;
    # it returns a non-zero gate code (the __main__ wrapper turns it into SystemExit).
    rc = rv.main([])
    assert rc != 0


def test_main_does_not_invoke_run_verdict_while_gated(monkeypatch):
    # Hard proof the gate short-circuits BEFORE any run_verdict / engine touch.
    def _boom(*a, **k):
        raise AssertionError("run_verdict must NOT be reached while Phase-D gated")

    monkeypatch.setattr(rv, "run_verdict", _boom)
    assert rv.main([]) != 0  # gate fires; run_verdict never called


def test_phase_d_authorized_flag_default_is_false():
    assert rv.PHASE_D_AUTHORIZED is False


# ---------------------------------------------------------------------------
# build_train_frame: two forward horizons (24h + 72h), train-only
# ---------------------------------------------------------------------------


def test_build_train_frame_has_both_forward_horizons(tmp_path):
    train = rv.build_train_frame(rv.load_train_windows(), features_path=_tiny_features(tmp_path))
    assert "fwd_ret_24h" in train.columns
    assert "fwd_ret_72h" in train.columns
    assert len(train) > 0
    # train-only: no 2024/2025/2022 rows leaked.
    assert (train["open_time_utc"].dt.year == 2020).all()


# ---------------------------------------------------------------------------
# run_verdict: sealed-dir refusal + mocked-engine integration + sealed invariant
# ---------------------------------------------------------------------------


def test_run_verdict_refuses_sealed_out_dir():
    with pytest.raises(ValueError, match="sealed"):
        rv.run_verdict(rv.SEALED_DIRS[0])


def test_run_verdict_integration_mocked_engine(tmp_path):
    out = tmp_path / "patha_verdict_v1"
    bundle = rv.run_verdict(
        out,
        features_path=_tiny_features(tmp_path),
        _run_backtest=_fake_backtest_result,
    )
    assert bundle["taxonomy"]["advisory_taxonomy"] in (
        "mechanism_refuted", "process_refuted_for_this_grid", "b_positive",
    )
    assert "approximation_tempers" in bundle["taxonomy"]
    assert "verdict_rests_on_weak_sane_only" in bundle["taxonomy"]
    assert bundle["escalation"]["authority"] == "charlie_register"
    assert 0 <= bundle["n_tier5_pass"] <= 3
    assert len(bundle["holdouts"]) == 3
    # fenced funding-marginal diagnostic rode along, fenced.
    assert bundle["funding_marginal"] is None or all(
        m["promotion_affecting"] is False and m["in_n_star"] is False
        for m in bundle["funding_marginal"].values()
    )
    # sealed-artifact invariant recorded + the advisory json written.
    assert "sealed_sha256_invariant" in bundle["meta"]
    assert (out / "patha_verdict_advisory.json").exists()
    written = json.loads((out / "patha_verdict_advisory.json").read_text())
    assert written["taxonomy"]["advisory_taxonomy"] == bundle["taxonomy"]["advisory_taxonomy"]


# ---------------------------------------------------------------------------
# Sealed tier6_dsr_v1/ byte-invariance (4/4) — the reuse must NOT touch it.
# ---------------------------------------------------------------------------

# Frozen baseline sha256 of the 4 sealed tier6_dsr_v1 artifacts (LOCK §baseline).
_SEALED_TIER6_SHA256 = {
    "tier6_dsr_companion.csv": "0a7d98acfb5791c52c6a6d15bd6285a5a4450a4b6ccc113ac165035616666612",
    "tier6_dsr_results.csv": "8eecc6cd50344e32b25880ac16db3489b24ef65e0095f249039841fbf801acac",
    "tier6_mc_validation.json": "49646c303c9329ad2a9b15be819d5cf8a1101fc1e09b3997aa693c4c06ea2acd",
    "tier6_promotion_list.json": "1803eb44812ba89e7c881e7dfec110d8403e08a232aa4e07acf4881b0093e699",
}


def test_sealed_tier6_dsr_v1_sha256_is_4_of_4_unchanged():
    """The Path A harness reuses tier6_dsr but must NEVER mutate the sealed cohort.
    Assert all 4 sealed tier6_dsr_v1 artifacts are byte-identical to the LOCK baseline."""
    import hashlib

    sealed = rv.PROJECT_ROOT / "data/phase2c_evaluation_gate/tier6_dsr_v1"
    if not sealed.exists():
        pytest.skip("sealed tier6_dsr_v1 dir not present in this checkout")
    for fn, expected in _SEALED_TIER6_SHA256.items():
        got = hashlib.sha256((sealed / fn).read_bytes()).hexdigest()
        assert got == expected, f"sealed {fn} sha256 drifted: {got} != {expected}"

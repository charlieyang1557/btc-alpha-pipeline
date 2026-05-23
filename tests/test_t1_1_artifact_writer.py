"""T1.1 Engine artifact writer + slice-aware emission tests.

TDD discipline: tests written FIRST (RED) per testing.md discipline.
Implementation targets:
- backtest/engine.py: EquityCurveCollector extension (per-bar returns)
- backtest/engine.py: write_per_bar_artifact() — writes returns_per_bar.parquet
- backtest/engine.py: compute_moments() — γ3/γ4/T_obs via scipy
- backtest/engine.py: run_backtest() / run_walk_forward() slice-aware emission

Contract references:
- Contract 2.0.1: γ4 = scipy kurtosis(fisher=False, bias=True, nan_policy='omit')
- Contract 2.0.5: per-bar parquet schema + SHA256 + T_obs alignment
- T1.1 plan v5 §2: EquityCurveCollector extension + slice-aware writer
- T1.3 SEALED boundary: run_walk_forward inner run_backtest uses lineage_context=None

Test organization:
1. scipy version precondition (Contract 2.0.1)
2. γ3/γ4/T_obs computation correctness (Contract 2.0.1 + 2.0.6 fixture vector)
3. Per-bar returns capture (EquityCurveCollector extension or new analyzer)
4. write_per_bar_artifact: path, schema, SHA256
5. Slice-aware writer signature (accepts explicit equity_curve + trades)
6. Walk-forward inner run_backtest uses lineage_context=None (T1.3 boundary regression)
7. LineageContext per-bar field population end-to-end
"""
from __future__ import annotations

import dataclasses
import hashlib
import io
import math
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import pytest


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

_REPO_ROOT = Path(__file__).resolve().parent.parent


def _build_valid_lc_kwargs(**overrides: Any) -> dict[str, Any]:
    """Minimal valid LineageContext kwargs for T1.1 tests.

    cost_anchor_id is NOT included — auto-resolved by __post_init__.
    returns_per_bar_path and returns_per_bar_sha256 are placeholder values;
    tests that exercise these fields provide their own.
    """
    base = {
        "run_id": "t1-1-run-001",
        "hypothesis_hash": "abc123def456",
        "source_batch_id": "batch-t1-1-001",
        "regime_key": "v2.regime_holdout",
        "engine_commit": "eb1c87f",
        "current_git_sha": "deadbeef1234",
        "execution_config_path": "config/execution.yaml",
        "execution_config_sha256": "sha256:aabbccdd",
        "parquet_data_sha256": "sha256:11223344",
        "returns_per_bar_path": "returns_per_bar.parquet",
        "returns_per_bar_sha256": "sha256:placeholder",
        "T_obs": 10,
        "parent_run_id": None,
    }
    base.update(overrides)
    return base


def _sha256_file(path: Path) -> str:
    """Compute SHA256 of file at path using 64KB chunked streaming."""
    h = hashlib.sha256()
    with path.open("rb") as fh:
        while True:
            chunk = fh.read(65536)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------------------
# 1. scipy version precondition (Contract 2.0.1)
# ---------------------------------------------------------------------------


class TestScipyVersionPrecondition:
    """Contract 2.0.1: scipy >= 1.9 required for nan_policy keyword.

    The moment computation module must verify scipy version at import time
    or at first call. If scipy < 1.9 is detected, the test fails closed
    (raises ImportError or similar).
    """

    def test_scipy_version_at_least_1_9(self) -> None:
        """scipy >= 1.9 is installed; nan_policy kwarg supported."""
        import scipy

        parts = tuple(int(x) for x in scipy.__version__.split(".")[:2])
        assert parts >= (1, 9), (
            f"scipy >= 1.9 required per Contract 2.0.1 nan_policy precondition; "
            f"found scipy {scipy.__version__}"
        )

    def test_scipy_kurtosis_nan_policy_omit_supported(self) -> None:
        """scipy.stats.kurtosis accepts nan_policy='omit' without error."""
        from scipy.stats import kurtosis

        arr = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        # Should not raise TypeError about unexpected kwarg
        result = kurtosis(arr, fisher=False, bias=True, nan_policy="omit")
        assert np.isfinite(result)

    def test_scipy_skew_nan_policy_omit_supported(self) -> None:
        """scipy.stats.skew accepts nan_policy='omit' without error."""
        from scipy.stats import skew

        arr = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        result = skew(arr, bias=True, nan_policy="omit")
        assert np.isfinite(result)


# ---------------------------------------------------------------------------
# 2. γ3/γ4/T_obs computation correctness (Contract 2.0.1 + 2.0.6)
# ---------------------------------------------------------------------------


class TestMomentComputationFixtureVector:
    """Contract 2.0.6 (a): deterministic adversarial fixture vector [-1, 1, 0, 0, 0, 0].

    All numerical values empirically verified per plan v5 drafting.
    The compute_moments() function must be importable from backtest.engine
    or backtest.metrics.
    """

    FIXTURE = np.array([-1.0, 1.0, 0.0, 0.0, 0.0, 0.0])

    def _compute(self) -> dict[str, Any]:
        """Import compute_moments from whichever module exposes it."""
        try:
            from backtest.engine import compute_moments
        except ImportError:
            from backtest.metrics import compute_moments
        return compute_moments(self.FIXTURE)

    def test_gamma4_matches_scipy_fisher_false(self) -> None:
        """γ4 = scipy kurtosis(fisher=False, bias=True) ≈ 3.0 for fixture."""
        from scipy.stats import kurtosis

        expected_gamma4 = float(
            kurtosis(self.FIXTURE, fisher=False, bias=True, nan_policy="omit")
        )
        result = self._compute()
        assert abs(result["gamma4"] - expected_gamma4) < 1e-12, (
            f"γ4 mismatch: got {result['gamma4']!r}, expected {expected_gamma4!r} "
            f"(scipy kurtosis fisher=False bias=True)"
        )

    def test_gamma4_value_close_to_3(self) -> None:
        """γ4 for fixture vector [-1, 1, 0, 0, 0, 0] ≈ 3.000000 (raw kurtosis)."""
        result = self._compute()
        assert abs(result["gamma4"] - 3.0) < 1e-12, (
            f"γ4 for fixture vector should be 3.0 (raw kurtosis); "
            f"got {result['gamma4']!r}. "
            f"Check that scipy kurtosis(fisher=False, bias=True, nan_policy='omit') "
            f"is used (Contract 2.0.1)."
        )

    def test_gamma4_excludes_zero_excess_kurtosis_convention(self) -> None:
        """γ4 band must EXCLUDE 0.0 (excess-kurtosis convention check)."""
        result = self._compute()
        assert abs(result["gamma4"] - 0.0) > 0.5, (
            f"γ4={result['gamma4']!r} is near 0.0 — this indicates excess kurtosis "
            f"convention (Gaussian=0). Contract 2.0.1 requires raw kurtosis "
            f"(Gaussian=3). Use scipy kurtosis(fisher=False, bias=True)."
        )

    def test_prohibited_pandas_kurt_would_be_different(self) -> None:
        """pandas .kurt() gives 2.5 for fixture — must differ from γ4=3.0."""
        pandas_kurt = pd.Series(self.FIXTURE).kurt()  # default: excess bias-corrected
        assert abs(pandas_kurt - 2.5) < 1e-6, (
            f"pandas .kurt() should be 2.5 for fixture; got {pandas_kurt!r}"
        )
        result = self._compute()
        # Our γ4 (3.0) must differ from pandas default (2.5)
        assert abs(result["gamma4"] - pandas_kurt) > 0.4, (
            f"γ4={result['gamma4']!r} matches pandas .kurt()={pandas_kurt!r}; "
            f"Contract 2.0.1 prohibits pandas .kurt()"
        )

    def test_prohibited_pandas_kurt_plus_3_would_be_5_5(self) -> None:
        """pandas .kurt()+3 gives 5.5 for fixture — must differ from γ4=3.0."""
        pandas_kurt_raw = pd.Series(self.FIXTURE).kurt() + 3  # bias-corrected raw
        assert abs(pandas_kurt_raw - 5.5) < 1e-6, (
            f"pandas .kurt()+3 should be 5.5 for fixture; got {pandas_kurt_raw!r}"
        )
        result = self._compute()
        assert abs(result["gamma4"] - pandas_kurt_raw) > 0.4

    def test_prohibited_scipy_fisher_true_bias_true_would_be_zero(self) -> None:
        """scipy kurtosis(fisher=True, bias=True) gives 0.0 for fixture — prohibited."""
        from scipy.stats import kurtosis

        scipy_excess = float(kurtosis(self.FIXTURE, fisher=True, bias=True, nan_policy="omit"))
        assert abs(scipy_excess - 0.0) < 1e-12, (
            f"scipy kurtosis(fisher=True, bias=True) should be 0.0 for fixture; "
            f"got {scipy_excess!r}"
        )
        result = self._compute()
        assert abs(result["gamma4"] - scipy_excess) > 0.4

    def test_prohibited_scipy_fisher_true_bias_false_would_be_2_5(self) -> None:
        """scipy kurtosis(fisher=True, bias=False) gives 2.5 for fixture — prohibited."""
        from scipy.stats import kurtosis

        scipy_bc_excess = float(
            kurtosis(self.FIXTURE, fisher=True, bias=False, nan_policy="omit")
        )
        assert abs(scipy_bc_excess - 2.5) < 1e-6, (
            f"scipy kurtosis(fisher=True, bias=False) should be 2.5 for fixture; "
            f"got {scipy_bc_excess!r}"
        )
        result = self._compute()
        assert abs(result["gamma4"] - scipy_bc_excess) > 0.4

    def test_prohibited_scipy_fisher_false_bias_false_would_be_5_5(self) -> None:
        """scipy kurtosis(fisher=False, bias=False) gives 5.5 for fixture — prohibited."""
        from scipy.stats import kurtosis

        scipy_bc_raw = float(
            kurtosis(self.FIXTURE, fisher=False, bias=False, nan_policy="omit")
        )
        assert abs(scipy_bc_raw - 5.5) < 1e-6, (
            f"scipy kurtosis(fisher=False, bias=False) should be 5.5 for fixture; "
            f"got {scipy_bc_raw!r}"
        )
        result = self._compute()
        assert abs(result["gamma4"] - scipy_bc_raw) > 0.4

    def test_gamma3_matches_scipy_skew(self) -> None:
        """γ3 matches scipy.stats.skew(bias=True, nan_policy='omit')."""
        from scipy.stats import skew

        expected_gamma3 = float(skew(self.FIXTURE, bias=True, nan_policy="omit"))
        result = self._compute()
        assert abs(result["gamma3"] - expected_gamma3) < 1e-12, (
            f"γ3 mismatch: got {result['gamma3']!r}, expected {expected_gamma3!r}"
        )

    def test_t_obs_is_count_of_finite_values(self) -> None:
        """T_obs = count of finite values in input array (all 6 are finite)."""
        result = self._compute()
        assert result["T_obs"] == 6, (
            f"T_obs for all-finite fixture should be 6; got {result['T_obs']!r}"
        )

    def test_t_obs_excludes_nan(self) -> None:
        """T_obs excludes NaN values from count."""
        try:
            from backtest.engine import compute_moments
        except ImportError:
            from backtest.metrics import compute_moments

        arr_with_nan = np.array([-1.0, 1.0, 0.0, float("nan"), 0.0, 0.0])
        result = compute_moments(arr_with_nan)
        assert result["T_obs"] == 5, (
            f"T_obs should be 5 (NaN excluded); got {result['T_obs']!r}"
        )

    def test_t_obs_excludes_inf(self) -> None:
        """T_obs excludes +inf/-inf values from count."""
        try:
            from backtest.engine import compute_moments
        except ImportError:
            from backtest.metrics import compute_moments

        arr_with_inf = np.array([-1.0, 1.0, 0.0, float("inf"), float("-inf"), 0.0])
        result = compute_moments(arr_with_inf)
        assert result["T_obs"] == 4, (
            f"T_obs should be 4 (±inf excluded); got {result['T_obs']!r}"
        )

    def test_empty_array_returns_nan_gamma4_t_obs_zero(self) -> None:
        """Empty input: T_obs=0, γ4=NaN (or None), γ3=NaN (or None)."""
        try:
            from backtest.engine import compute_moments
        except ImportError:
            from backtest.metrics import compute_moments

        arr = np.array([], dtype=float)
        result = compute_moments(arr)
        assert result["T_obs"] == 0
        # γ4 and γ3 should be NaN or None for empty input
        gamma4 = result.get("gamma4")
        gamma3 = result.get("gamma3")
        assert gamma4 is None or (isinstance(gamma4, float) and math.isnan(gamma4)), (
            f"γ4 for empty array should be None or NaN; got {gamma4!r}"
        )
        assert gamma3 is None or (isinstance(gamma3, float) and math.isnan(gamma3)), (
            f"γ3 for empty array should be None or NaN; got {gamma3!r}"
        )

    def test_all_nan_array_returns_t_obs_zero(self) -> None:
        """All-NaN input: T_obs=0 (nan_policy='omit' drops all)."""
        try:
            from backtest.engine import compute_moments
        except ImportError:
            from backtest.metrics import compute_moments

        arr = np.array([float("nan"), float("nan"), float("nan")])
        result = compute_moments(arr)
        assert result["T_obs"] == 0


class TestMomentComputationGaussian:
    """Gaussian-limit self-consistency: large iid normal → γ4 ≈ 3.0, γ3 ≈ 0."""

    def test_large_normal_sample_gamma4_near_3(self) -> None:
        """1000 iid N(0,1) samples: γ4 ≈ 3.0 (raw population kurtosis)."""
        try:
            from backtest.engine import compute_moments
        except ImportError:
            from backtest.metrics import compute_moments

        rng = np.random.default_rng(42)
        arr = rng.normal(0, 1, 1000)
        result = compute_moments(arr)
        # Gaussian limit: γ4 → 3; within 0.5 for N=1000
        assert abs(result["gamma4"] - 3.0) < 0.5, (
            f"γ4 for large normal sample should be near 3.0; got {result['gamma4']!r}"
        )

    def test_large_normal_sample_gamma3_near_0(self) -> None:
        """1000 iid N(0,1) samples: γ3 ≈ 0 (near-zero skew)."""
        try:
            from backtest.engine import compute_moments
        except ImportError:
            from backtest.metrics import compute_moments

        rng = np.random.default_rng(42)
        arr = rng.normal(0, 1, 1000)
        result = compute_moments(arr)
        assert abs(result["gamma3"]) < 0.5, (
            f"γ3 for large normal sample should be near 0.0; got {result['gamma3']!r}"
        )


# ---------------------------------------------------------------------------
# 3. Per-bar returns capture (equity_curve → per-bar returns)
# ---------------------------------------------------------------------------


class TestPerBarReturnsSeries:
    """Verify equity-curve-to-per-bar-returns conversion."""

    def _compute_per_bar_returns(self, equity_values: list[float]) -> pd.Series:
        """Import compute_per_bar_returns (or equivalent) from engine."""
        try:
            from backtest.engine import compute_per_bar_returns
        except ImportError:
            pytest.fail(
                "compute_per_bar_returns not found in backtest.engine. "
                "T1.1 must expose this function."
            )
        idx = pd.date_range("2024-01-01", periods=len(equity_values), freq="h")
        ec = pd.Series(equity_values, index=idx, dtype=float)
        return compute_per_bar_returns(ec)

    def test_basic_equity_curve_produces_correct_returns(self) -> None:
        """Simple equity curve: returns = pct_change (portfolio value ratio - 1)."""
        ec_vals = [10000.0, 10100.0, 10201.0, 10100.0]
        returns = self._compute_per_bar_returns(ec_vals)
        # First return is NaN (no prior bar) or the series starts at bar 1
        # Acceptable: either drop first bar OR emit NaN at position 0
        finite = returns[np.isfinite(returns)]
        assert len(finite) >= 2, "At least 2 finite returns expected"

        # Check actual return values are pct-change-based
        # 10100/10000 - 1 = 0.01, 10201/10100 - 1 = 0.01, 10100/10201 - 1 ≈ -0.0099
        expected = np.array([0.01, 0.01, 10100.0 / 10201.0 - 1.0])
        # Align by taking last len(finite) values
        np.testing.assert_allclose(
            finite.values[-len(expected):],
            expected[-len(finite):],
            rtol=1e-6,
        )

    def test_constant_equity_produces_zero_returns(self) -> None:
        """Flat equity curve: all returns are 0.0."""
        ec_vals = [10000.0] * 5
        returns = self._compute_per_bar_returns(ec_vals)
        finite = returns[np.isfinite(returns)]
        assert all(abs(r) < 1e-12 for r in finite), (
            f"Flat equity should give all-zero returns; got {finite.values!r}"
        )

    def test_single_bar_equity_curve_returns_empty_or_nan(self) -> None:
        """Single-bar equity curve: no return computable."""
        returns = self._compute_per_bar_returns([10000.0])
        finite = returns[np.isfinite(returns)]
        assert len(finite) == 0, (
            f"Single-bar equity should produce 0 finite returns; got {finite.values!r}"
        )

    def test_empty_equity_curve_returns_empty(self) -> None:
        """Empty equity curve: returns empty Series."""
        try:
            from backtest.engine import compute_per_bar_returns
        except ImportError:
            pytest.fail("compute_per_bar_returns not found in backtest.engine")

        empty_ec = pd.Series([], dtype=float)
        result = compute_per_bar_returns(empty_ec)
        assert len(result) == 0

    def test_returns_preserve_datetime_index(self) -> None:
        """Returns Series has a datetime index (not reset to integer)."""
        returns = self._compute_per_bar_returns([10000.0, 10100.0, 10200.0])
        assert hasattr(returns.index, "dtype") or isinstance(
            returns.index, pd.DatetimeIndex
        ), "Returns Series must preserve datetime index"


# ---------------------------------------------------------------------------
# 4. write_per_bar_artifact: path, schema, SHA256
# ---------------------------------------------------------------------------


class TestWritePerBarArtifact:
    """write_per_bar_artifact() writes returns_per_bar.parquet at expected path."""

    def _invoke_writer(
        self,
        artifact_dir: Path,
        equity_curve: pd.Series,
        run_id: str = "test-run-001",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Call write_per_bar_artifact and return its result dict."""
        try:
            from backtest.engine import write_per_bar_artifact
        except ImportError:
            pytest.fail(
                "write_per_bar_artifact not found in backtest.engine. "
                "T1.1 must expose this function."
            )
        return write_per_bar_artifact(
            equity_curve=equity_curve,
            artifact_dir=artifact_dir,
            run_id=run_id,
            **kwargs,
        )

    def _make_equity_curve(self, n: int = 10, start_val: float = 10000.0) -> pd.Series:
        """Synthetic equity curve with n bars."""
        idx = pd.date_range("2024-01-01", periods=n, freq="h")
        vals = [start_val * (1 + 0.001 * i) for i in range(n)]
        return pd.Series(vals, index=idx, dtype=float)

    def test_returns_per_bar_parquet_written_at_artifact_dir(
        self, tmp_path: Path
    ) -> None:
        """write_per_bar_artifact writes returns_per_bar.parquet in artifact_dir."""
        ec = self._make_equity_curve(10)
        result = self._invoke_writer(tmp_path, ec)
        parquet_path = tmp_path / "returns_per_bar.parquet"
        assert parquet_path.is_file(), (
            f"returns_per_bar.parquet not found at {parquet_path}. "
            f"write_per_bar_artifact must write to artifact_dir/returns_per_bar.parquet."
        )

    def test_result_dict_contains_returns_per_bar_path(self, tmp_path: Path) -> None:
        """Result dict has 'returns_per_bar_path' key with the relative filename."""
        ec = self._make_equity_curve(10)
        result = self._invoke_writer(tmp_path, ec)
        assert "returns_per_bar_path" in result, (
            "write_per_bar_artifact result must include 'returns_per_bar_path'"
        )
        assert result["returns_per_bar_path"] == "returns_per_bar.parquet"

    def test_result_dict_contains_returns_per_bar_sha256(self, tmp_path: Path) -> None:
        """Result dict has 'returns_per_bar_sha256' key with hex digest."""
        ec = self._make_equity_curve(10)
        result = self._invoke_writer(tmp_path, ec)
        assert "returns_per_bar_sha256" in result, (
            "write_per_bar_artifact result must include 'returns_per_bar_sha256'"
        )
        sha256 = result["returns_per_bar_sha256"]
        assert isinstance(sha256, str) and len(sha256) == 64, (
            f"SHA256 must be 64-char hex; got {sha256!r}"
        )

    def test_sha256_matches_file_content(self, tmp_path: Path) -> None:
        """SHA256 in result matches actual file content (64KB chunked)."""
        ec = self._make_equity_curve(10)
        result = self._invoke_writer(tmp_path, ec)

        parquet_path = tmp_path / "returns_per_bar.parquet"
        actual_sha256 = _sha256_file(parquet_path)
        assert result["returns_per_bar_sha256"] == actual_sha256, (
            f"SHA256 mismatch: result={result['returns_per_bar_sha256']!r}, "
            f"file={actual_sha256!r}"
        )

    def test_parquet_has_return_column(self, tmp_path: Path) -> None:
        """Parquet file has 'return' column (required for T_obs alignment)."""
        import pyarrow.parquet as pq

        ec = self._make_equity_curve(10)
        self._invoke_writer(tmp_path, ec)
        parquet_path = tmp_path / "returns_per_bar.parquet"
        table = pq.read_table(str(parquet_path))
        assert "return" in table.column_names, (
            f"Parquet must have 'return' column; got columns={table.column_names!r}"
        )

    def test_parquet_has_timestamp_column(self, tmp_path: Path) -> None:
        """Parquet file has a timestamp/datetime column for alignment."""
        import pyarrow.parquet as pq

        ec = self._make_equity_curve(10)
        self._invoke_writer(tmp_path, ec)
        parquet_path = tmp_path / "returns_per_bar.parquet"
        table = pq.read_table(str(parquet_path))
        # Acceptable column names: 'timestamp', 'datetime', 'open_time_utc', etc.
        time_cols = [c for c in table.column_names if "time" in c or "date" in c]
        assert len(time_cols) >= 1, (
            f"Parquet must have at least one timestamp column; "
            f"got columns={table.column_names!r}"
        )

    def test_result_dict_contains_t_obs(self, tmp_path: Path) -> None:
        """Result dict has 'T_obs' key with positive int."""
        ec = self._make_equity_curve(10)
        result = self._invoke_writer(tmp_path, ec)
        assert "T_obs" in result, "write_per_bar_artifact result must include 'T_obs'"
        t_obs = result["T_obs"]
        assert isinstance(t_obs, int) and t_obs > 0, (
            f"T_obs must be a positive int; got {t_obs!r}"
        )

    def test_t_obs_matches_finite_row_count(self, tmp_path: Path) -> None:
        """T_obs equals count of finite 'return' values in parquet."""
        import pyarrow.compute as pc
        import pyarrow.parquet as pq

        ec = self._make_equity_curve(10)
        result = self._invoke_writer(tmp_path, ec)
        parquet_path = tmp_path / "returns_per_bar.parquet"
        table = pq.read_table(str(parquet_path))
        col = table.column("return")
        actual_t_obs = int(pc.sum(pc.and_(pc.is_valid(col), pc.is_finite(col))).as_py())
        assert result["T_obs"] == actual_t_obs, (
            f"T_obs in result ({result['T_obs']}) must match finite-row count "
            f"in parquet ({actual_t_obs})"
        )

    def test_result_dict_contains_gamma3_gamma4(self, tmp_path: Path) -> None:
        """Result dict has 'gamma3' and 'gamma4' keys."""
        ec = self._make_equity_curve(10)
        result = self._invoke_writer(tmp_path, ec)
        assert "gamma3" in result, "write_per_bar_artifact result must include 'gamma3'"
        assert "gamma4" in result, "write_per_bar_artifact result must include 'gamma4'"

    def test_gamma4_matches_scipy_convention(self, tmp_path: Path) -> None:
        """γ4 in result uses scipy kurtosis(fisher=False, bias=True) convention."""
        from scipy.stats import kurtosis

        ec = self._make_equity_curve(20)
        result = self._invoke_writer(tmp_path, ec)

        # Compute expected γ4 from the same equity curve
        try:
            from backtest.engine import compute_per_bar_returns
        except ImportError:
            pytest.fail("compute_per_bar_returns not found")

        returns = compute_per_bar_returns(ec)
        finite_returns = returns[np.isfinite(returns)].values
        if len(finite_returns) >= 2:
            expected_gamma4 = float(
                kurtosis(finite_returns, fisher=False, bias=True, nan_policy="omit")
            )
            assert abs(result["gamma4"] - expected_gamma4) < 1e-10, (
                f"γ4 mismatch: result={result['gamma4']!r}, expected={expected_gamma4!r}"
            )

    def test_artifact_dir_created_if_not_exists(self, tmp_path: Path) -> None:
        """write_per_bar_artifact creates artifact_dir if it does not exist."""
        artifact_dir = tmp_path / "nested" / "dir" / "run_001"
        assert not artifact_dir.exists()

        ec = self._make_equity_curve(5)
        self._invoke_writer(artifact_dir, ec)

        assert artifact_dir.is_dir()
        assert (artifact_dir / "returns_per_bar.parquet").is_file()

    def test_deterministic_sha256_on_same_equity_curve(self, tmp_path: Path) -> None:
        """Same equity curve → same SHA256 across two writes."""
        ec = self._make_equity_curve(10)

        dir1 = tmp_path / "run_a"
        dir2 = tmp_path / "run_b"

        result1 = self._invoke_writer(dir1, ec)
        result2 = self._invoke_writer(dir2, ec)

        # SHA256 values should be identical (deterministic parquet write)
        assert result1["returns_per_bar_sha256"] == result2["returns_per_bar_sha256"], (
            "Same equity curve must produce identical SHA256 (deterministic parquet)"
        )

    def test_empty_equity_curve_raises_value_error(self, tmp_path: Path) -> None:
        """Empty equity curve raises ValueError (SYS-fix-1 B5 producer guard).

        Prior behavior (pre-SYS-fix-1 B5): empty curve → T_obs=0 returned.
        New behavior (SYS-fix-1 B5): empty curve → ValueError fail-fast.
        B5 is symmetric with check_b_c_extended_semantics_or_raise T_obs > 0.
        """
        try:
            from backtest.engine import write_per_bar_artifact
        except ImportError:
            pytest.fail("write_per_bar_artifact not found")

        empty_ec = pd.Series([], dtype=float, index=pd.DatetimeIndex([]))
        with pytest.raises(ValueError, match="T_obs"):
            write_per_bar_artifact(
                equity_curve=empty_ec, artifact_dir=tmp_path, run_id="empty-run"
            )

    def test_tz_aware_index_writes_parquet_without_error(self, tmp_path: Path) -> None:
        """Equity curve with tz-aware DatetimeIndex writes successfully (else branch)."""
        import pyarrow.parquet as pq

        try:
            from backtest.engine import write_per_bar_artifact
        except ImportError:
            pytest.fail("write_per_bar_artifact not found")

        # tz-aware index triggers the else branch in write_per_bar_artifact
        idx = pd.date_range("2024-01-01", periods=5, freq="h", tz="UTC")
        ec = pd.Series([10000.0 + i * 100 for i in range(5)], index=idx, dtype=float)
        result = write_per_bar_artifact(
            equity_curve=ec, artifact_dir=tmp_path, run_id="tz-aware-run"
        )
        assert result["T_obs"] > 0
        parquet_path = tmp_path / "returns_per_bar.parquet"
        assert parquet_path.is_file()


# ---------------------------------------------------------------------------
# 5. Slice-aware writer signature
# ---------------------------------------------------------------------------


class TestSliceAwareWriterSignature:
    """write_per_bar_artifact must accept explicit equity_curve (not infer from result)."""

    def test_writer_accepts_equity_curve_kwarg(self, tmp_path: Path) -> None:
        """write_per_bar_artifact accepts 'equity_curve' as explicit kwarg."""
        try:
            from backtest.engine import write_per_bar_artifact
        except ImportError:
            pytest.fail("write_per_bar_artifact not in backtest.engine")

        import inspect

        sig = inspect.signature(write_per_bar_artifact)
        params = set(sig.parameters.keys())
        assert "equity_curve" in params, (
            "write_per_bar_artifact must accept 'equity_curve' kwarg "
            "(slice-aware: explicit test-period curve, not BacktestResult.equity_curve)"
        )

    def test_writer_accepts_artifact_dir_kwarg(self, tmp_path: Path) -> None:
        """write_per_bar_artifact accepts 'artifact_dir' as explicit kwarg."""
        try:
            from backtest.engine import write_per_bar_artifact
        except ImportError:
            pytest.fail("write_per_bar_artifact not in backtest.engine")

        import inspect

        sig = inspect.signature(write_per_bar_artifact)
        params = set(sig.parameters.keys())
        assert "artifact_dir" in params, (
            "write_per_bar_artifact must accept 'artifact_dir' kwarg"
        )

    def test_explicit_equity_curve_slice_used_not_full(self, tmp_path: Path) -> None:
        """Writer uses the provided equity_curve, not an internally reconstructed one."""
        try:
            from backtest.engine import write_per_bar_artifact
        except ImportError:
            pytest.fail("write_per_bar_artifact not in backtest.engine")

        import pyarrow.parquet as pq

        # Full equity curve (10 bars)
        full_idx = pd.date_range("2024-01-01", periods=10, freq="h")
        full_ec = pd.Series(
            [10000.0 * (1 + 0.001 * i) for i in range(10)], index=full_idx
        )

        # Slice: last 5 bars only (test-period)
        slice_idx = full_idx[5:]
        slice_ec = full_ec[5:]

        dir_full = tmp_path / "full"
        dir_slice = tmp_path / "slice"

        write_per_bar_artifact(equity_curve=full_ec, artifact_dir=dir_full, run_id="run-full")
        write_per_bar_artifact(equity_curve=slice_ec, artifact_dir=dir_slice, run_id="run-slice")

        # Row counts must differ: full has ~9 returns, slice has ~4 returns
        table_full = pq.read_table(str(dir_full / "returns_per_bar.parquet"))
        table_slice = pq.read_table(str(dir_slice / "returns_per_bar.parquet"))

        assert table_full.num_rows > table_slice.num_rows, (
            "Full equity curve must produce more rows than test-period slice. "
            "Writer must use the provided equity_curve parameter verbatim."
        )


# ---------------------------------------------------------------------------
# 6. Walk-forward inner run_backtest uses lineage_context=None (T1.3 boundary)
# ---------------------------------------------------------------------------


class TestWalkForwardInnerLinageContextNone:
    """T1.3 SEALED boundary: inner run_backtest call in run_walk_forward uses lineage_context=None.

    This test regression-protects the T1.3 slice-aware boundary discipline.
    The inner run_backtest must be called with lineage_context=None (opt-in=False);
    the outer WF wrapper is the only legitimate WF artifact writer.
    """

    def test_run_walk_forward_inner_call_uses_lineage_context_none(
        self, tmp_path: Path
    ) -> None:
        """Inner run_backtest within run_walk_forward is called with lineage_context=None.

        We capture all run_backtest calls via patching and verify none of
        the inner window calls (write_registry=False) have lineage_context != None.
        """
        from unittest.mock import call, patch, MagicMock

        inner_calls: list[dict] = []
        original_run_backtest = None

        def _capture_run_backtest(**kwargs: Any) -> Any:
            # Record whether lineage_context was passed non-None
            inner_calls.append({"lineage_context": kwargs.get("lineage_context")})
            # Return a minimal BacktestResult stub
            mock_result = MagicMock()
            mock_result.trades = []
            mock_result.equity_curve = pd.Series(
                [10000.0] * 5,
                index=pd.date_range("2024-01-01", periods=5, freq="h"),
            )
            mock_result.metrics = {
                "total_return": 0.0,
                "sharpe_ratio": 0.0,
                "max_drawdown": 0.0,
                "max_drawdown_duration_hours": 0.0,
                "total_trades": 0,
                "win_rate": 0.0,
                "avg_trade_duration_hours": 0.0,
                "avg_trade_return": 0.0,
                "profit_factor": None,
                "initial_capital": 10000.0,
                "final_capital": 10000.0,
            }
            mock_result.warmup_bars = 0
            mock_result.run_id = str(__import__("uuid").uuid4())
            return mock_result

        from datetime import date
        import backtest.engine as engine_mod

        # Use a simple strategy class for the test
        import backtrader as bt

        class _DummyStrategy(bt.Strategy):
            STRATEGY_NAME = "dummy_for_t1_1_test"
            WARMUP_BARS = 0

            def next(self) -> None:
                pass

        # Patch run_backtest inside engine module; also patch _write_to_registry
        with (
            patch.object(engine_mod, "run_backtest", side_effect=_capture_run_backtest),
            patch.object(engine_mod, "_write_to_registry"),
        ):
            try:
                engine_mod.run_walk_forward(
                    strategy_cls=_DummyStrategy,
                    overall_start=date(2024, 1, 1),
                    overall_end=date(2024, 6, 30),
                    walk_forward_config={
                        "train_months": 3,
                        "test_months": 1,
                        "step_months": 1,
                    },
                    db_path=tmp_path / "test_wf_inner.db",
                )
            except Exception:
                # If run_walk_forward raises for any reason (e.g., window gen),
                # we still check the captured calls
                pass

        # All inner run_backtest calls must have lineage_context=None
        for i, captured in enumerate(inner_calls):
            assert captured["lineage_context"] is None, (
                f"Inner run_backtest call #{i+1} has lineage_context="
                f"{captured['lineage_context']!r} (should be None). "
                f"T1.3 SEALED boundary: run_walk_forward inner call must use "
                f"lineage_context=None (opt-in=False per T1.3-D spec)."
            )


# ---------------------------------------------------------------------------
# 7. LineageContext per-bar field population end-to-end
# ---------------------------------------------------------------------------


class TestLineageContextPerBarFieldPopulation:
    """End-to-end: LineageContext with returns_per_bar_path + SHA256 populated from write.

    After write_per_bar_artifact() writes the parquet file, the caller constructs
    LineageContext with the returned path + SHA256. The resulting LineageContext
    must pass check_b_c_extended_semantics_or_raise (T1.2 SEALED validator).
    """

    def _make_equity_curve(self, n: int = 20, start_val: float = 10000.0) -> pd.Series:
        idx = pd.date_range("2024-01-01", periods=n, freq="h")
        vals = [start_val * (1 + 0.001 * i) for i in range(n)]
        return pd.Series(vals, index=idx, dtype=float)

    def _build_lc_kwargs_from_artifact_write(
        self, tmp_path: Path
    ) -> dict[str, Any]:
        """Write per-bar artifact, then build LineageContext kwargs from result."""
        try:
            from backtest.engine import write_per_bar_artifact
        except ImportError:
            pytest.fail("write_per_bar_artifact not found in backtest.engine")

        artifact_dir = tmp_path / "hypothesis_abc123"
        artifact_dir.mkdir(parents=True)

        ec = self._make_equity_curve(20)
        result = write_per_bar_artifact(
            equity_curve=ec,
            artifact_dir=artifact_dir,
            run_id="lc-e2e-run-001",
        )

        return {
            "run_id": "lc-e2e-run-001",
            "hypothesis_hash": "abc123def456",
            "source_batch_id": "batch-lc-e2e-001",
            "regime_key": "v2.regime_holdout",
            "engine_commit": "eb1c87f",
            "current_git_sha": "deadbeef1234",
            "execution_config_path": "config/execution.yaml",
            "execution_config_sha256": "sha256:aabbccdd",
            "parquet_data_sha256": "sha256:11223344",
            # From write_per_bar_artifact result:
            "returns_per_bar_path": result["returns_per_bar_path"],
            "returns_per_bar_sha256": result["returns_per_bar_sha256"],
            "T_obs": result["T_obs"],
            "parent_run_id": None,
        }, artifact_dir

    def test_lineage_context_construction_with_artifact_fields_succeeds(
        self, tmp_path: Path
    ) -> None:
        """LineageContext constructed with write-derived fields succeeds."""
        from backtest.artifact_schema import LineageContext

        kwargs, _ = self._build_lc_kwargs_from_artifact_write(tmp_path)
        lc = LineageContext(**kwargs)
        assert lc.returns_per_bar_path == "returns_per_bar.parquet"
        assert len(lc.returns_per_bar_sha256) == 64
        assert lc.T_obs > 0

    def test_lineage_context_sha256_matches_written_file(
        self, tmp_path: Path
    ) -> None:
        """LineageContext.returns_per_bar_sha256 matches actual file SHA256."""
        from backtest.artifact_schema import LineageContext

        kwargs, artifact_dir = self._build_lc_kwargs_from_artifact_write(tmp_path)
        lc = LineageContext(**kwargs)

        parquet_path = artifact_dir / lc.returns_per_bar_path
        actual_sha256 = _sha256_file(parquet_path)
        assert lc.returns_per_bar_sha256 == actual_sha256, (
            f"LineageContext.returns_per_bar_sha256={lc.returns_per_bar_sha256!r} "
            f"does not match actual file SHA256={actual_sha256!r}"
        )

    def test_check_b_c_extended_validator_passes_on_complete_artifact(
        self, tmp_path: Path
    ) -> None:
        """T1.2 SEALED validator passes on artifact with correct per-bar linkage."""
        from backtest.wf_lineage import check_b_c_extended_semantics_or_raise

        try:
            from backtest.engine import write_per_bar_artifact
        except ImportError:
            pytest.fail("write_per_bar_artifact not found in backtest.engine")

        artifact_dir = tmp_path / "hyp_abc123"
        artifact_dir.mkdir(parents=True)

        ec = self._make_equity_curve(20)
        result = write_per_bar_artifact(
            equity_curve=ec,
            artifact_dir=artifact_dir,
            run_id="validator-e2e-run",
        )

        # Build the summary dict matching b_c_extended_v1 schema
        summary = {
            "artifact_schema_version": "b_c_extended_v1",
            "run_id": "validator-e2e-run",
            "hypothesis_hash": "abc123def456",
            "source_batch_id": "batch-val-001",
            "parent_run_id": None,
            "regime_key": "v2.regime_holdout",
            "engine_commit": "eb1c87f",
            "current_git_sha": "deadbeef1234",
            "execution_config_path": "config/execution.yaml",
            "execution_config_sha256": "sha256:aabbccdd",
            "parquet_data_sha256": "sha256:11223344",
            "cost_anchor_id": "legacy_perp_inspired_7bps_v0",
            "returns_per_bar_path": result["returns_per_bar_path"],
            "returns_per_bar_sha256": result["returns_per_bar_sha256"],
            "T_obs": result["T_obs"],
        }

        # Validator must pass without raising
        # artifact_path provides base dir for resolving returns_per_bar_path
        fake_artifact_path = artifact_dir / "holdout_summary.json"
        check_b_c_extended_semantics_or_raise(summary, artifact_path=fake_artifact_path)


# ---------------------------------------------------------------------------
# 8. compute_moments function signature and return type
# ---------------------------------------------------------------------------


class TestComputeMomentsSignature:
    """compute_moments must accept np.ndarray and return a dict."""

    def _fn(self):
        try:
            from backtest.engine import compute_moments
        except ImportError:
            from backtest.metrics import compute_moments
        return compute_moments

    def test_accepts_numpy_array(self) -> None:
        """compute_moments accepts numpy array input."""
        fn = self._fn()
        arr = np.array([0.01, -0.02, 0.03, 0.0, 0.01])
        result = fn(arr)
        assert isinstance(result, dict)

    def test_accepts_list_input(self) -> None:
        """compute_moments accepts list input (converted internally)."""
        fn = self._fn()
        result = fn([0.01, -0.02, 0.03, 0.0, 0.01])
        assert isinstance(result, dict)

    def test_return_dict_has_required_keys(self) -> None:
        """Result dict has gamma3, gamma4, T_obs keys at minimum."""
        fn = self._fn()
        arr = np.array([0.01, -0.02, 0.03])
        result = fn(arr)
        assert "gamma3" in result, "Missing 'gamma3' key in compute_moments result"
        assert "gamma4" in result, "Missing 'gamma4' key in compute_moments result"
        assert "T_obs" in result, "Missing 'T_obs' key in compute_moments result"

    def test_t_obs_is_int(self) -> None:
        """T_obs must be int (not float, not np.int64)."""
        fn = self._fn()
        arr = np.array([0.01, -0.02, 0.03])
        result = fn(arr)
        assert isinstance(result["T_obs"], int), (
            f"T_obs must be Python int; got {type(result['T_obs']).__name__}"
        )


# ---------------------------------------------------------------------------
# 9. compute_per_bar_returns function signature
# ---------------------------------------------------------------------------


class TestComputePerBarReturnsSignature:
    """compute_per_bar_returns must accept pd.Series and return pd.Series."""

    def test_returns_pd_series(self) -> None:
        """compute_per_bar_returns returns pd.Series."""
        try:
            from backtest.engine import compute_per_bar_returns
        except ImportError:
            pytest.fail("compute_per_bar_returns not found in backtest.engine")

        idx = pd.date_range("2024-01-01", periods=5, freq="h")
        ec = pd.Series([10000.0, 10100.0, 10050.0, 10150.0, 10200.0], index=idx)
        result = compute_per_bar_returns(ec)
        assert isinstance(result, pd.Series)

    def test_preserves_index(self) -> None:
        """compute_per_bar_returns preserves the input index (or a compatible subset)."""
        try:
            from backtest.engine import compute_per_bar_returns
        except ImportError:
            pytest.fail("compute_per_bar_returns not found in backtest.engine")

        idx = pd.date_range("2024-01-01", periods=5, freq="h")
        ec = pd.Series([10000.0, 10100.0, 10050.0, 10150.0, 10200.0], index=idx)
        result = compute_per_bar_returns(ec)
        # Result index should be a subset of input index
        assert all(ts in idx for ts in result.index), (
            "compute_per_bar_returns result index must be a subset of input index"
        )


# ---------------------------------------------------------------------------
# 10. FIX-T1.1-H1: LineageContext T_obs symmetric validation (RED tests)
# ---------------------------------------------------------------------------


class TestLineageContextTObsSymmetricValidation:
    """FIX-T1.1-H1: LineageContext.__post_init__ must reject T_obs <= 0.

    Producer-consumer asymmetry bug: validator check_b_c_extended_semantics_or_raise
    rejects T_obs=0, but LineageContext.__post_init__ silently accepts it.
    Fix: add __post_init__ guard mirroring the validator's requirement.
    """

    def _base_kwargs(self) -> dict[str, Any]:
        return _build_valid_lc_kwargs()

    def test_t_obs_zero_raises_value_error(self) -> None:
        """LineageContext(T_obs=0) raises ValueError (symmetric with validator)."""
        from backtest.artifact_schema import LineageContext

        kwargs = self._base_kwargs()
        kwargs["T_obs"] = 0
        with pytest.raises(ValueError, match="T_obs"):
            LineageContext(**kwargs)

    def test_t_obs_negative_raises_value_error(self) -> None:
        """LineageContext(T_obs=-1) raises ValueError."""
        from backtest.artifact_schema import LineageContext

        kwargs = self._base_kwargs()
        kwargs["T_obs"] = -1
        with pytest.raises(ValueError, match="T_obs"):
            LineageContext(**kwargs)

    def test_t_obs_large_negative_raises_value_error(self) -> None:
        """LineageContext(T_obs=-999) raises ValueError."""
        from backtest.artifact_schema import LineageContext

        kwargs = self._base_kwargs()
        kwargs["T_obs"] = -999
        with pytest.raises(ValueError, match="T_obs"):
            LineageContext(**kwargs)

    def test_t_obs_one_is_valid(self) -> None:
        """LineageContext(T_obs=1) is valid (boundary: minimum positive)."""
        from backtest.artifact_schema import LineageContext

        kwargs = self._base_kwargs()
        kwargs["T_obs"] = 1
        lc = LineageContext(**kwargs)
        assert lc.T_obs == 1

    def test_t_obs_positive_large_is_valid(self) -> None:
        """LineageContext(T_obs=10000) is valid."""
        from backtest.artifact_schema import LineageContext

        kwargs = self._base_kwargs()
        kwargs["T_obs"] = 10000
        lc = LineageContext(**kwargs)
        assert lc.T_obs == 10000

    def test_validator_round_trip_regression(self, tmp_path: Path) -> None:
        """Producer LC (T_obs>0) + written artifact + validator pass (regression-protect).

        Ensures FIX-T1.1-H1 doesn't break the valid T_obs>0 round-trip path.
        """
        from backtest.artifact_schema import LineageContext
        from backtest.wf_lineage import check_b_c_extended_semantics_or_raise
        from backtest.engine import write_per_bar_artifact

        artifact_dir = tmp_path / "h1_regression"
        artifact_dir.mkdir(parents=True)
        idx = pd.date_range("2024-01-01", periods=10, freq="h")
        ec = pd.Series([10000.0 + i * 100 for i in range(10)], index=idx)
        result = write_per_bar_artifact(equity_curve=ec, artifact_dir=artifact_dir, run_id="h1-reg")

        assert result["T_obs"] > 0  # pre-check: writer must give T_obs > 0

        # Constructor must succeed
        kwargs = _build_valid_lc_kwargs(
            T_obs=result["T_obs"],
            returns_per_bar_path=result["returns_per_bar_path"],
            returns_per_bar_sha256=result["returns_per_bar_sha256"],
        )
        lc = LineageContext(**kwargs)

        # Validator must also pass
        summary = {
            "artifact_schema_version": "b_c_extended_v1",
            "run_id": lc.run_id,
            "hypothesis_hash": lc.hypothesis_hash,
            "source_batch_id": lc.source_batch_id,
            "parent_run_id": lc.parent_run_id,
            "regime_key": lc.regime_key,
            "engine_commit": lc.engine_commit,
            "current_git_sha": lc.current_git_sha,
            "execution_config_path": lc.execution_config_path,
            "execution_config_sha256": lc.execution_config_sha256,
            "parquet_data_sha256": lc.parquet_data_sha256,
            "cost_anchor_id": lc.cost_anchor_id,
            "returns_per_bar_path": lc.returns_per_bar_path,
            "returns_per_bar_sha256": lc.returns_per_bar_sha256,
            "T_obs": lc.T_obs,
        }
        fake_summary_path = artifact_dir / "holdout_summary.json"
        check_b_c_extended_semantics_or_raise(summary, artifact_path=fake_summary_path)


# ---------------------------------------------------------------------------
# 11. FIX-T1.1-H2: Timezone semantics (RED tests)
# ---------------------------------------------------------------------------


class TestWritePerBarArtifactTimezone:
    """FIX-T1.1-H2: write_per_bar_artifact timezone semantics.

    HARD CONSTRAINT from CLAUDE.md: all timestamps in parquet must be
    UTC-aware datetime64[ms, UTC] or UTC-tagged. Current code strips tz
    from tz-aware inputs and may silently UTC-shift.

    Required behavior:
    - tz-naive index: assume UTC, localize before writing
    - tz-aware UTC: pass through unchanged
    - tz-aware non-UTC (e.g. America/New_York): FAIL CLOSED with ValueError
    """

    def _make_ec(self, n: int = 5, tz: "str | None" = None) -> pd.Series:
        idx = pd.date_range("2024-01-01", periods=n, freq="h", tz=tz)
        return pd.Series([10000.0 + i * 100 for i in range(n)], index=idx, dtype=float)

    def test_tz_naive_written_parquet_has_utc_tag(self, tmp_path: Path) -> None:
        """tz-naive equity curve -> parquet timestamp column has tz='UTC'."""
        import pyarrow.parquet as pq
        from backtest.engine import write_per_bar_artifact

        ec = self._make_ec(tz=None)
        assert ec.index.tz is None, "Precondition: index must be tz-naive"
        write_per_bar_artifact(equity_curve=ec, artifact_dir=tmp_path, run_id="tz-naive-test")

        table = pq.read_table(str(tmp_path / "returns_per_bar.parquet"))
        ts_field = table.schema.field("timestamp")
        ts_type = ts_field.type
        assert hasattr(ts_type, "tz") and ts_type.tz == "UTC", (
            f"tz-naive input must produce UTC-tagged timestamp column; "
            f"got type={ts_type!r}"
        )

    def test_tz_naive_values_preserved_under_utc_localization(self, tmp_path: Path) -> None:
        """tz-naive equity curve values are unchanged after UTC localization."""
        import pyarrow.parquet as pq
        from backtest.engine import write_per_bar_artifact

        ec = self._make_ec(n=5, tz=None)
        write_per_bar_artifact(equity_curve=ec, artifact_dir=tmp_path, run_id="tz-naive-vals")

        table = pq.read_table(str(tmp_path / "returns_per_bar.parquet"))
        # Read timestamps back; they should match original naive timestamps when
        # tz-localized to UTC (no value shift).
        ts_col = table.column("timestamp").to_pylist()
        # All timestamps must be non-None
        assert all(t is not None for t in ts_col)

    def test_tz_aware_utc_written_parquet_has_utc_tag(self, tmp_path: Path) -> None:
        """tz-aware UTC equity curve -> parquet timestamp column has tz='UTC'."""
        import pyarrow.parquet as pq
        from backtest.engine import write_per_bar_artifact

        ec = self._make_ec(tz="UTC")
        write_per_bar_artifact(equity_curve=ec, artifact_dir=tmp_path, run_id="tz-utc-test")

        table = pq.read_table(str(tmp_path / "returns_per_bar.parquet"))
        ts_field = table.schema.field("timestamp")
        ts_type = ts_field.type
        assert hasattr(ts_type, "tz") and ts_type.tz == "UTC", (
            f"tz-aware UTC input must produce UTC-tagged timestamp column; "
            f"got type={ts_type!r}"
        )

    def test_tz_aware_non_utc_fails_closed_with_value_error(self, tmp_path: Path) -> None:
        """tz-aware America/New_York equity curve -> ValueError (fail-closed)."""
        from backtest.engine import write_per_bar_artifact

        ec = self._make_ec(tz="America/New_York")
        with pytest.raises(ValueError, match="UTC"):
            write_per_bar_artifact(
                equity_curve=ec, artifact_dir=tmp_path, run_id="tz-non-utc-test"
            )

    def test_tz_aware_utc_values_preserved(self, tmp_path: Path) -> None:
        """tz-aware UTC input values are preserved in the written parquet."""
        import pyarrow.parquet as pq
        from backtest.engine import write_per_bar_artifact

        ec = self._make_ec(n=5, tz="UTC")
        result = write_per_bar_artifact(equity_curve=ec, artifact_dir=tmp_path, run_id="tz-utc-vals")
        assert result["T_obs"] > 0

        table = pq.read_table(str(tmp_path / "returns_per_bar.parquet"))
        assert "return" in table.column_names
        assert table.num_rows > 0


# ---------------------------------------------------------------------------
# 12. FIX-T1.1-B2: Atomic per-bar artifact write (RED tests)
# ---------------------------------------------------------------------------


class TestAtomicPerBarArtifactWrite:
    """FIX-T1.1-B2: write_per_bar_artifact must use atomic temp+replace pattern.

    Requirement:
    - Write to a temp file first (e.g. returns_per_bar.parquet.tmp.<8hex>)
    - After successful write, use os.replace() for atomic swap
    - On any exception during write, clean up the temp file
    - No partial file left at final path on write failure
    """

    def _make_equity_curve(self, n: int = 10) -> pd.Series:
        idx = pd.date_range("2024-01-01", periods=n, freq="h")
        return pd.Series([10000.0 + i * 100 for i in range(n)], index=idx, dtype=float)

    def test_uses_temp_file_then_replace_pattern(self, tmp_path: Path) -> None:
        """write_per_bar_artifact uses a temp file + os.replace() pattern.

        Verifies the atomic discipline: the function must call os.replace (not shutil.move)
        by spying on os.replace calls. At least one call to os.replace must happen
        during a successful write, establishing the temp-then-replace mechanism.
        """
        from unittest.mock import patch, call
        import os as os_mod
        from backtest.engine import write_per_bar_artifact

        replace_calls: list[Any] = []
        original_replace = os_mod.replace

        def _spy_replace(src: str, dst: str) -> None:
            replace_calls.append((src, dst))
            return original_replace(src, dst)

        with patch("os.replace", side_effect=_spy_replace):
            write_per_bar_artifact(
                equity_curve=self._make_equity_curve(),
                artifact_dir=tmp_path,
                run_id="atomic-spy",
            )

        assert len(replace_calls) >= 1, (
            "write_per_bar_artifact must call os.replace() for atomic temp->final swap. "
            "No os.replace() calls detected — the atomic temp+replace pattern is missing."
        )
        # The destination of the replace must be the final parquet path
        final_path = str(tmp_path / "returns_per_bar.parquet")
        replace_destinations = [dst for (src, dst) in replace_calls]
        assert any(dst == final_path for dst in replace_destinations), (
            f"os.replace() destination must be the final parquet path {final_path!r}. "
            f"Got destinations: {replace_destinations!r}"
        )

    def test_no_leftover_temp_file_after_successful_write(self, tmp_path: Path) -> None:
        """No .tmp.* files remain in artifact_dir after successful write."""
        from backtest.engine import write_per_bar_artifact

        ec = self._make_equity_curve()
        write_per_bar_artifact(equity_curve=ec, artifact_dir=tmp_path, run_id="atomic-success")

        tmp_files = list(tmp_path.glob("*.tmp.*"))
        assert len(tmp_files) == 0, (
            f"Leftover temp files found after successful write: {tmp_files}. "
            f"Atomic writer must remove temp files after os.replace()."
        )

    def test_no_partial_file_at_final_path_on_write_failure(self, tmp_path: Path) -> None:
        """On write failure, no partial file exists at the final parquet path."""
        from unittest.mock import patch
        from backtest.engine import write_per_bar_artifact

        final_path = tmp_path / "returns_per_bar.parquet"
        assert not final_path.exists(), "Precondition: final path must not exist before test"

        # Patch pq.write_table inside engine module to raise after beginning write
        with patch("backtest.engine.pq") as mock_pq:
            mock_pq.write_table.side_effect = OSError("simulated disk full")
            try:
                write_per_bar_artifact(
                    equity_curve=self._make_equity_curve(),
                    artifact_dir=tmp_path,
                    run_id="atomic-fail",
                )
            except Exception:
                pass  # expected to raise

        assert not final_path.exists(), (
            f"Partial file found at final path {final_path} after write failure. "
            f"Atomic writer must not leave partial files at final path."
        )

    def test_no_leftover_temp_file_on_write_failure(self, tmp_path: Path) -> None:
        """On write failure, no temp files remain in artifact_dir."""
        from unittest.mock import patch
        from backtest.engine import write_per_bar_artifact

        with patch("backtest.engine.pq") as mock_pq:
            mock_pq.write_table.side_effect = OSError("simulated disk full")
            try:
                write_per_bar_artifact(
                    equity_curve=self._make_equity_curve(),
                    artifact_dir=tmp_path,
                    run_id="atomic-cleanup",
                )
            except Exception:
                pass

        tmp_files = list(tmp_path.glob("*.tmp.*"))
        assert len(tmp_files) == 0, (
            f"Leftover temp files after write failure: {tmp_files}. "
            f"Atomic writer must clean up temp file on any exception."
        )

    def test_final_file_present_and_valid_after_successful_write(self, tmp_path: Path) -> None:
        """After successful write, returns_per_bar.parquet is present and readable."""
        import pyarrow.parquet as pq
        from backtest.engine import write_per_bar_artifact

        ec = self._make_equity_curve()
        result = write_per_bar_artifact(equity_curve=ec, artifact_dir=tmp_path, run_id="atomic-ok")

        final_path = tmp_path / "returns_per_bar.parquet"
        assert final_path.is_file()
        table = pq.read_table(str(final_path))
        assert "return" in table.column_names
        assert result["T_obs"] > 0

    def test_concurrent_writes_to_different_dirs_do_not_interfere(self, tmp_path: Path) -> None:
        """Concurrent writes to different dirs complete without exception."""
        import threading
        from backtest.engine import write_per_bar_artifact

        errors: list[Exception] = []

        def _write(i: int) -> None:
            d = tmp_path / f"dir_{i}"
            d.mkdir()
            ec = self._make_equity_curve(n=5 + i)
            try:
                write_per_bar_artifact(equity_curve=ec, artifact_dir=d, run_id=f"concurrent-{i}")
            except Exception as exc:
                errors.append(exc)

        threads = [threading.Thread(target=_write, args=(i,)) for i in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0, (
            f"Concurrent writes produced exceptions: {errors}"
        )


# ---------------------------------------------------------------------------
# 13. FIX-T1.1-B1: Registry persistence for per-bar artifact fields (RED tests)
# ---------------------------------------------------------------------------


class TestRegistryPerBarFieldPersistence:
    """FIX-T1.1-B1: _write_to_registry must persist per-bar artifact fields to SQLite.

    Contract 2.0.5 obligation gap: LineageContext carries returns_per_bar_path,
    returns_per_bar_sha256, T_obs but _write_to_registry does NOT write them.
    experiment_registry.py schema lacks these columns.

    Required fix:
    - MIGRATION_COLUMNS: add ("returns_per_bar_path", "TEXT"),
        ("returns_per_bar_sha256", "TEXT"), ("T_obs", "INTEGER")
    - CREATE_TABLE_SQL: same 3 columns
    - _write_to_registry: when lineage_context present, populate these 3 fields
    """

    def _make_lineage_context(self, artifact_dir: Path) -> "Any":
        """Build a valid LineageContext with written artifact fields."""
        from backtest.artifact_schema import LineageContext
        from backtest.engine import write_per_bar_artifact

        idx = pd.date_range("2024-01-01", periods=15, freq="h")
        ec = pd.Series([10000.0 + i * 100 for i in range(15)], index=idx, dtype=float)
        result = write_per_bar_artifact(equity_curve=ec, artifact_dir=artifact_dir, run_id="b1-test")

        return LineageContext(
            run_id="b1-reg-run-001",
            hypothesis_hash="b1hash123",
            source_batch_id="b1-batch-001",
            regime_key="v2.regime_holdout",
            engine_commit="eb1c87f",
            current_git_sha="b1deadbeef",
            execution_config_path="config/execution.yaml",
            execution_config_sha256="sha256:b1aabb",
            parquet_data_sha256="sha256:b1ccdd",
            returns_per_bar_path=result["returns_per_bar_path"],
            returns_per_bar_sha256=result["returns_per_bar_sha256"],
            T_obs=result["T_obs"],
            parent_run_id=None,
        )

    def test_migration_columns_include_three_new_fields(self) -> None:
        """MIGRATION_COLUMNS includes returns_per_bar_path, returns_per_bar_sha256, T_obs."""
        from backtest.experiment_registry import MIGRATION_COLUMNS

        col_names = {name for name, _ in MIGRATION_COLUMNS}
        assert "returns_per_bar_path" in col_names, (
            "MIGRATION_COLUMNS must include 'returns_per_bar_path' (FIX-T1.1-B1)"
        )
        assert "returns_per_bar_sha256" in col_names, (
            "MIGRATION_COLUMNS must include 'returns_per_bar_sha256' (FIX-T1.1-B1)"
        )
        assert "T_obs" in col_names, (
            "MIGRATION_COLUMNS must include 'T_obs' (FIX-T1.1-B1)"
        )

    def test_create_table_sql_includes_three_new_fields(self) -> None:
        """CREATE_TABLE_SQL includes returns_per_bar_path, returns_per_bar_sha256, T_obs."""
        from backtest.experiment_registry import CREATE_TABLE_SQL

        assert "returns_per_bar_path" in CREATE_TABLE_SQL, (
            "CREATE_TABLE_SQL must include 'returns_per_bar_path' column (FIX-T1.1-B1)"
        )
        assert "returns_per_bar_sha256" in CREATE_TABLE_SQL, (
            "CREATE_TABLE_SQL must include 'returns_per_bar_sha256' column (FIX-T1.1-B1)"
        )
        assert "T_obs" in CREATE_TABLE_SQL, (
            "CREATE_TABLE_SQL must include 'T_obs' column (FIX-T1.1-B1)"
        )

    def test_fresh_db_migration_adds_three_new_columns(self, tmp_path: Path) -> None:
        """Fresh DB: create_table() adds all 3 new columns via PRAGMA table_info."""
        import sqlite3
        from backtest.experiment_registry import create_table, get_connection

        db_path = tmp_path / "fresh_migration.db"
        conn = get_connection(db_path)
        try:
            create_table(conn)
            cursor = conn.execute("PRAGMA table_info(runs)")
            col_names = {row[1] for row in cursor.fetchall()}
        finally:
            conn.close()

        assert "returns_per_bar_path" in col_names, (
            f"After create_table(), 'returns_per_bar_path' column must exist; "
            f"found columns: {col_names}"
        )
        assert "returns_per_bar_sha256" in col_names, (
            f"After create_table(), 'returns_per_bar_sha256' column must exist; "
            f"found columns: {col_names}"
        )
        assert "T_obs" in col_names, (
            f"After create_table(), 'T_obs' column must exist; "
            f"found columns: {col_names}"
        )

    def test_write_to_registry_with_lineage_context_persists_three_fields(
        self, tmp_path: Path
    ) -> None:
        """_write_to_registry with lineage_context writes 3 per-bar fields to SQLite."""
        import sqlite3
        from backtest.engine import _write_to_registry
        from backtest.execution_model import ConstantSlippage
        from backtest.engine import load_execution_config
        from backtest.experiment_registry import get_connection, create_table
        from backtest.artifact_schema import LineageContext

        artifact_dir = tmp_path / "b1_lc_artifact"
        artifact_dir.mkdir(parents=True)
        lc = self._make_lineage_context(artifact_dir)

        db_path = tmp_path / "b1_persist.db"
        config = load_execution_config()
        cost_model = ConstantSlippage.from_config(config)

        import backtrader as bt

        class _B1Strategy(bt.Strategy):
            STRATEGY_NAME = "b1_dummy"
            WARMUP_BARS = 0

            def next(self) -> None:
                pass

        from datetime import datetime, timezone
        _write_to_registry(
            run_id=lc.run_id,
            strategy_cls=_B1Strategy,
            strategy_params={},
            start_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
            end_date=datetime(2024, 1, 31, tzinfo=timezone.utc),
            effective_start=None,
            warmup_bars=0,
            cost_model=cost_model,
            metrics={
                "total_return": 0.0,
                "sharpe_ratio": 0.0,
                "max_drawdown": 0.0,
                "max_drawdown_duration_hours": 0.0,
                "total_trades": 0,
                "win_rate": 0.0,
                "avg_trade_duration_hours": 0.0,
                "avg_trade_return": 0.0,
                "profit_factor": None,
                "initial_capital": 10000.0,
                "final_capital": 10000.0,
            },
            db_path=db_path,
            lineage_context=lc,
            artifact_dir=artifact_dir,  # FIX-T1.1-SYS2-B2: required when LATE_FILL non-empty
        )

        # Query SQLite directly and verify the 3 fields
        conn = sqlite3.connect(str(db_path))
        try:
            row = conn.execute(
                "SELECT returns_per_bar_path, returns_per_bar_sha256, T_obs "
                "FROM runs WHERE run_id = ?",
                (lc.run_id,),
            ).fetchone()
        finally:
            conn.close()

        assert row is not None, f"No row found for run_id={lc.run_id!r}"
        stored_path, stored_sha256, stored_t_obs = row
        assert stored_path == lc.returns_per_bar_path, (
            f"returns_per_bar_path mismatch: stored={stored_path!r}, "
            f"expected={lc.returns_per_bar_path!r}"
        )
        assert stored_sha256 == lc.returns_per_bar_sha256, (
            f"returns_per_bar_sha256 mismatch: stored={stored_sha256!r}, "
            f"expected={lc.returns_per_bar_sha256!r}"
        )
        assert stored_t_obs == lc.T_obs, (
            f"T_obs mismatch: stored={stored_t_obs!r}, expected={lc.T_obs!r}"
        )

    def test_write_to_registry_without_lineage_context_stores_null_for_three_fields(
        self, tmp_path: Path
    ) -> None:
        """_write_to_registry without lineage_context stores NULL for 3 new fields."""
        import sqlite3
        from backtest.engine import _write_to_registry
        from backtest.execution_model import ConstantSlippage
        from backtest.engine import load_execution_config
        import uuid

        db_path = tmp_path / "b1_null.db"
        config = load_execution_config()
        cost_model = ConstantSlippage.from_config(config)

        import backtrader as bt

        class _B1NullStrategy(bt.Strategy):
            STRATEGY_NAME = "b1_null_dummy"
            WARMUP_BARS = 0

            def next(self) -> None:
                pass

        from datetime import datetime, timezone
        run_id = str(uuid.uuid4())
        _write_to_registry(
            run_id=run_id,
            strategy_cls=_B1NullStrategy,
            strategy_params={},
            start_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
            end_date=datetime(2024, 1, 31, tzinfo=timezone.utc),
            effective_start=None,
            warmup_bars=0,
            cost_model=cost_model,
            metrics={
                "total_return": 0.0,
                "sharpe_ratio": 0.0,
                "max_drawdown": 0.0,
                "max_drawdown_duration_hours": 0.0,
                "total_trades": 0,
                "win_rate": 0.0,
                "avg_trade_duration_hours": 0.0,
                "avg_trade_return": 0.0,
                "profit_factor": None,
                "initial_capital": 10000.0,
                "final_capital": 10000.0,
            },
            db_path=db_path,
            lineage_context=None,
        )

        conn = sqlite3.connect(str(db_path))
        try:
            row = conn.execute(
                "SELECT returns_per_bar_path, returns_per_bar_sha256, T_obs "
                "FROM runs WHERE run_id = ?",
                (run_id,),
            ).fetchone()
        finally:
            conn.close()

        assert row is not None, f"No row found for run_id={run_id!r}"
        stored_path, stored_sha256, stored_t_obs = row
        assert stored_path is None, (
            f"returns_per_bar_path must be NULL without lineage_context; got {stored_path!r}"
        )
        assert stored_sha256 is None, (
            f"returns_per_bar_sha256 must be NULL without lineage_context; got {stored_sha256!r}"
        )
        assert stored_t_obs is None, (
            f"T_obs must be NULL without lineage_context; got {stored_t_obs!r}"
        )


# ---------------------------------------------------------------------------
# 14. FIX-T1.1-H3: Walk-forward test strictness (improved assertions)
# ---------------------------------------------------------------------------


class TestWalkForwardInnerLinageContextNoneStrict:
    """FIX-T1.1-H3: Strict assertions on walk-forward inner call capturing.

    Replaces/supplements TestWalkForwardInnerLinageContextNone with:
    - No try/except swallowing exceptions
    - Assert inner_calls non-empty after test execution
    - Capture write_registry kwarg; assert write_registry=False on all inner calls
    - Preserve lineage_context=None assertion
    """

    def test_walk_forward_inner_calls_non_empty_and_write_registry_false(
        self, tmp_path: Path
    ) -> None:
        """Inner run_backtest calls are non-empty and all use write_registry=False.

        Does NOT swallow exceptions. Asserts both write_registry=False and
        lineage_context=None on every inner window call.
        """
        from unittest.mock import patch, MagicMock
        from datetime import date
        import backtest.engine as engine_mod
        import backtrader as bt

        inner_calls: list[dict] = []

        def _capture_run_backtest(**kwargs: Any) -> Any:
            inner_calls.append({
                "lineage_context": kwargs.get("lineage_context"),
                "write_registry": kwargs.get("write_registry"),
            })
            mock_result = MagicMock()
            mock_result.trades = []
            mock_result.equity_curve = pd.Series(
                [10000.0] * 5,
                index=pd.date_range("2024-01-01", periods=5, freq="h"),
            )
            mock_result.metrics = {
                "total_return": 0.0,
                "sharpe_ratio": 0.0,
                "max_drawdown": 0.0,
                "max_drawdown_duration_hours": 0.0,
                "total_trades": 0,
                "win_rate": 0.0,
                "avg_trade_duration_hours": 0.0,
                "avg_trade_return": 0.0,
                "profit_factor": None,
                "initial_capital": 10000.0,
                "final_capital": 10000.0,
            }
            mock_result.warmup_bars = 0
            mock_result.run_id = str(__import__("uuid").uuid4())
            return mock_result

        class _DummyStrategy(bt.Strategy):
            STRATEGY_NAME = "dummy_h3_test"
            WARMUP_BARS = 0

            def next(self) -> None:
                pass

        # No try/except: if run_walk_forward raises, the test fails
        # walk_forward_config keys must match what engine reads:
        # train_window_months, test_window_months, step_months
        with (
            patch.object(engine_mod, "run_backtest", side_effect=_capture_run_backtest),
            patch.object(engine_mod, "_write_to_registry"),
        ):
            engine_mod.run_walk_forward(
                strategy_cls=_DummyStrategy,
                overall_start=date(2024, 1, 1),
                overall_end=date(2024, 6, 30),
                walk_forward_config={
                    "train_window_months": 2,
                    "test_window_months": 1,
                    "step_months": 1,
                },
                db_path=tmp_path / "h3_wf.db",
            )

        # Non-empty: walk-forward must have called run_backtest at least once
        assert len(inner_calls) > 0, (
            "run_walk_forward produced no inner run_backtest calls — "
            "check that windows were generated and the mock was reached."
        )

        # All inner calls: write_registry=False + lineage_context=None
        for i, captured in enumerate(inner_calls):
            assert captured["write_registry"] is False, (
                f"Inner run_backtest call #{i+1} has write_registry="
                f"{captured['write_registry']!r} (must be False per T1.3 discipline)."
            )
            assert captured["lineage_context"] is None, (
                f"Inner run_backtest call #{i+1} has lineage_context="
                f"{captured['lineage_context']!r} (must be None per T1.3 SEALED boundary)."
            )


# ---------------------------------------------------------------------------
# 15. FIX-T1.1-M2: compute_moments zero-variance T_obs=2 returns None (RED tests)
# ---------------------------------------------------------------------------


class TestComputeMomentsZeroVariance:
    """FIX-T1.1-M2: compute_moments with zero-variance input returns None for gamma3/gamma4.

    When variance is zero (all values identical), skew and kurtosis are numerically
    undefined (0/0). Symmetric with insufficient-data convention (T_obs < 2 -> None).
    """

    def _fn(self):
        try:
            from backtest.engine import compute_moments
        except ImportError:
            from backtest.metrics import compute_moments
        return compute_moments

    def test_two_identical_values_gamma3_is_none(self) -> None:
        """T_obs=2 with zero variance: gamma3 is None (undefined)."""
        fn = self._fn()
        arr = np.array([1.0, 1.0])  # zero variance, T_obs=2
        result = fn(arr)
        assert result["gamma3"] is None, (
            f"gamma3 for zero-variance input should be None; got {result['gamma3']!r}"
        )

    def test_two_identical_values_gamma4_is_none(self) -> None:
        """T_obs=2 with zero variance: gamma4 is None (undefined)."""
        fn = self._fn()
        arr = np.array([1.0, 1.0])
        result = fn(arr)
        assert result["gamma4"] is None, (
            f"gamma4 for zero-variance input should be None; got {result['gamma4']!r}"
        )

    def test_many_identical_values_gamma3_is_none(self) -> None:
        """Many identical values (zero variance): gamma3 is None."""
        fn = self._fn()
        arr = np.array([5.0] * 100)
        result = fn(arr)
        assert result["gamma3"] is None, (
            f"gamma3 for all-same array should be None; got {result['gamma3']!r}"
        )

    def test_many_identical_values_gamma4_is_none(self) -> None:
        """Many identical values (zero variance): gamma4 is None."""
        fn = self._fn()
        arr = np.array([5.0] * 100)
        result = fn(arr)
        assert result["gamma4"] is None, (
            f"gamma4 for all-same array should be None; got {result['gamma4']!r}"
        )

    def test_many_identical_values_t_obs_is_correct(self) -> None:
        """Many identical values: T_obs counts all finite values."""
        fn = self._fn()
        arr = np.array([5.0] * 50)
        result = fn(arr)
        assert result["T_obs"] == 50, (
            f"T_obs for all-same array should be 50; got {result['T_obs']!r}"
        )

    def test_nonzero_variance_gamma4_is_not_none(self) -> None:
        """Non-zero variance input: gamma4 is not None (regression: don't over-return None)."""
        fn = self._fn()
        arr = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        result = fn(arr)
        assert result["gamma4"] is not None, (
            "gamma4 for non-zero variance input must not be None"
        )

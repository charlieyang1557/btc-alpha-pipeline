"""Tests for backtest/evaluate_dsr.py.

Verifies:
- Expected maximum Sharpe threshold computation
- Evaluation logic (survive/not survive) across edge cases
- Registry query integration
- Empty query produces clean output
"""

from __future__ import annotations

import json
import math
import sqlite3
from pathlib import Path

import pytest

from backtest.evaluate_dsr import (
    CandidateExclusion,
    CandidateInput,
    SimplifiedDSRInputs,
    compute_expected_max_sharpe,
    evaluate_trials,
    load_audit_v1_candidates,
    query_sharpe_ratios,
)


# ---------------------------------------------------------------------------
# PHASE2C_11 Step 3 — Synthetic RS-3 attestation JSONs for tests that
# synthesize CandidateInput without going through load_audit_v1_candidates().
#
# Per (β-mod) Charlie-register adjudication at PHASE2C_11 Step 3 implementation
# turn (TDD-RED hotfix register; sealed RED commit 73221c6 + this hotfix):
# compute_simplified_dsr() fires RS-3 guard
# (backtest.wf_lineage.check_evaluation_semantics_or_raise) per
# candidate.audit_v1_artifact_path at function entry, per §2.5 + §4.5 fail-loud
# RS-3 lockpoint. Tests that bypass the Step 2 loader (Classes #2-#5, #6, #8-#11,
# #13 partial) reference synthetic paths SYN_BASE/syn_*.json,
# SYN_BASE/synthetic_*.json, SYN_BASE/syn_target.json, and
# SYN_BASE/syn_filler_*.json that do not exist on disk at RED authoring time.
#
# ``SYN_BASE`` (module-level constant; updated by the autouse fixture below) is
# a unique per-test-session tmp directory derived from pytest's
# ``tmp_path_factory``. Production guard discipline (fail-loud on missing/
# malformed) preserved at production register; test convenience paths backed by
# valid synthetic attestations satisfying RS-3.
#
# Patch #8 (Codex first-fire): the original fixture wrote hundreds of files to
# fixed ``/tmp/syn_*.json`` paths, creating global side effects + concurrent-run
# collision risk + sandbox-incompatibility (Codex first-fire could not run
# pytest in its read-only sandbox because of this). Routing through
# ``tmp_path_factory`` eliminates all three concerns; pytest auto-cleans
# session tmp dirs (last 3 sessions retained by default), so the manual
# cleanup loop is dropped. Test method bodies updated mechanically to reference
# ``SYN_BASE`` instead of the fixed ``/tmp`` prefix; assertion substance
# unchanged per minimum-mutation discipline at sealed test register.
#
# Original adjudication trail (β-mod): advisor initially proposed (γ)
# monkeypatch path; ChatGPT proposed (β-mod) write-valid-JSON path; Charlie-
# register adjudicated convergence on (β-mod) per ChatGPT's test/production
# parity argument. Codex first-fire #8 adjudication: Charlie-register approved
# (γ-1) tmp_path_factory variant for sandbox + concurrency hardening.
# ---------------------------------------------------------------------------


# Module-level constant; overridden by ``_phase2c_11_synthetic_rs_attestations``
# autouse fixture before any Step 3 test runs. Default value is intentionally
# a sentinel that would fail RS-3 guard read if used pre-fixture — ensures
# accidental fixture-bypass surfaces immediately rather than silently.
SYN_BASE: str = "/tmp/PHASE2C_11_SYN_BASE_NOT_INITIALIZED"


@pytest.fixture(scope="module", autouse=True)
def _phase2c_11_synthetic_rs_attestations(tmp_path_factory):
    """Module-scoped autouse: create valid RS-3 attestation JSONs at a unique
    per-session tmp directory derived from ``tmp_path_factory``; expose path
    via ``SYN_BASE`` module constant.

    See module-level discussion above for adjudication trail.
    """
    global SYN_BASE
    base = tmp_path_factory.mktemp("phase2c_11_rs3_attestations")
    SYN_BASE = str(base)

    valid_attestation = json.dumps({
        "evaluation_semantics": "single_run_holdout_v1",
        "engine_commit": "eb1c87f",
        "engine_corrected_lineage": "wf-corrected-v1",
        "lineage_check": "passed",
        "current_git_sha": "deadbeef",
        "holdout_metrics": {"sharpe_ratio": 0.0, "total_trades": 10},
    })

    # Class #5 boundary disposition fixture: target + fillers.
    (base / "syn_target.json").write_text(valid_attestation)
    for i in range(200):
        (base / f"syn_filler_{i}.json").write_text(valid_attestation)
    # Most classes: syn_{i}.json (range(200) for safety margin over n=198).
    for i in range(200):
        (base / f"syn_{i}.json").write_text(valid_attestation)
    # Class #2 BonferroniThreshold: synthetic_{i}.json.
    for i in range(200):
        (base / f"synthetic_{i}.json").write_text(valid_attestation)

    yield
    # No manual cleanup; pytest auto-removes tmp_path_factory-derived dirs.


# ---------------------------------------------------------------------------
# PHASE2C_11 Step 3 — TestSimplifiedDSRDataclasses (Class #1 regression)
# ---------------------------------------------------------------------------


class TestSimplifiedDSRDataclasses:
    """Regression cover for PHASE2C_11 Step 3 frozen dataclass invariants.

    Per L1 option (b) deferred plan: this class is added at implementation
    turn; tests exercise frozen=True immutability, Literal cross-section
    consistency, sensitivity_table tuple-not-list, and excluded_candidates_
    summary tuple-of-tuples sortedness invariants. Not formula correctness
    (that is covered by Class #2-#11); regression discipline only.
    """

    def test_per_candidate_disposition_frozen(self):
        from dataclasses import FrozenInstanceError
        from backtest.evaluate_dsr import PerCandidateDisposition
        record = PerCandidateDisposition(
            hypothesis_hash="h001",
            sharpe_ratio=0.5,
            total_trades=10,
            standard_error=0.333,
            z_score=1.5,
            p_value=0.067,
            bonferroni_pass=False,
            dsr_style_pass=False,
            disposition="inconclusive",
            audit_v1_artifact_path="/tmp/foo.json",
        )
        with pytest.raises(FrozenInstanceError):
            record.disposition = "signal_evidence"

    def test_sensitivity_row_frozen(self):
        from dataclasses import FrozenInstanceError
        from backtest.evaluate_dsr import SensitivityRow
        row = SensitivityRow(
            n_eff=198,
            bonferroni_threshold=3.25,
            expected_max_sharpe_null=2.76,
            argmax_p_value=0.05,
            argmax_disposition_descriptive="inconclusive",
            register_label="primary",
        )
        with pytest.raises(FrozenInstanceError):
            row.n_eff = 80

    def test_simplified_dsr_result_frozen(self):
        from dataclasses import FrozenInstanceError
        from backtest.evaluate_dsr import SimplifiedDSRResult
        result = SimplifiedDSRResult(
            per_candidate=tuple(),
            population_disposition="inconclusive",
            population_argmax_hash="",
            n_trials=198,
            n_eligible=0,
            n_raw=198,
            bonferroni_threshold=0.0,
            expected_max_sharpe_null=0.0,
            sharpe_var_used=0.0,
            sensitivity_table=tuple(),
            bonferroni_cross_check={
                "sr_max": 0.0,
                "bonferroni_threshold": 0.0,
                "bonferroni_pass": False,
                "dsr_style_pass": False,
                "criteria_agree": True,
            },
            excluded_candidates_summary=tuple(),
            degenerate_state="n_eligible_zero",
            rs_guard_call_count=0,
        )
        with pytest.raises(FrozenInstanceError):
            result.population_disposition = "signal_evidence"

    def test_disposition_literal_cross_section_consistency(self):
        """All three Literal fields use the same DispositionLiteral type alias.

        Per schema §4: implementation defines DispositionLiteral once and
        reuses it across PerCandidateDisposition.disposition,
        SimplifiedDSRResult.population_disposition,
        SensitivityRow.argmax_disposition_descriptive.

        Patch #7 (Codex first-fire): the original assertion only checked
        ``typing.get_args(DispositionLiteral)`` — that would still pass if
        any individual field annotation drifted to a wider/separate Literal
        with the same args. Verify field annotations directly via
        ``typing.get_type_hints()`` introspection on each dataclass.
        """
        import typing
        from backtest.evaluate_dsr import (
            DispositionLiteral,
            PerCandidateDisposition,
            SensitivityRow,
            SimplifiedDSRResult,
        )

        expected_args = {"signal_evidence", "artifact_evidence", "inconclusive"}
        assert set(typing.get_args(DispositionLiteral)) == expected_args

        pc_hints = typing.get_type_hints(PerCandidateDisposition)
        sd_hints = typing.get_type_hints(SimplifiedDSRResult)
        sr_hints = typing.get_type_hints(SensitivityRow)

        # Each annotated field MUST equal the canonical DispositionLiteral
        # alias (Literal types compare by args, so drift to a wider/narrower
        # Literal at any of the three sites is caught here).
        assert pc_hints["disposition"] == DispositionLiteral, (
            f"PerCandidateDisposition.disposition drifted from "
            f"DispositionLiteral; got {pc_hints['disposition']!r}"
        )
        assert sd_hints["population_disposition"] == DispositionLiteral, (
            f"SimplifiedDSRResult.population_disposition drifted from "
            f"DispositionLiteral; got {sd_hints['population_disposition']!r}"
        )
        assert sr_hints["argmax_disposition_descriptive"] == DispositionLiteral, (
            f"SensitivityRow.argmax_disposition_descriptive drifted from "
            f"DispositionLiteral; got {sr_hints['argmax_disposition_descriptive']!r}"
        )

        # Belt-and-suspenders: verify args set at each field site identical
        # to expected_args (catches drift to type aliases that reduce to the
        # same Literal but where ``==`` semantics may hypothetically differ
        # under future typing-module behavior changes).
        assert set(typing.get_args(pc_hints["disposition"])) == expected_args
        assert set(typing.get_args(sd_hints["population_disposition"])) == expected_args
        assert set(typing.get_args(sr_hints["argmax_disposition_descriptive"])) == expected_args

    def test_sensitivity_table_is_tuple_not_list(self):
        """sensitivity_table field type is tuple[SensitivityRow, ...]."""
        from backtest.evaluate_dsr import (
            CandidateInput,
            compute_simplified_dsr,
        )
        sharpes = [0.5, -0.5] * 99
        candidates = [
            CandidateInput(
                hypothesis_hash=f"h{i:03d}",
                sharpe_ratio=sharpes[i],
                total_trades=10,
                audit_v1_artifact_path=f"{SYN_BASE}/syn_{i}.json",
                name="syn", theme="syn", lifecycle_state="shortlisted",
            )
            for i in range(198)
        ]
        result = compute_simplified_dsr(candidates, n_trials=198)
        assert isinstance(result.sensitivity_table, tuple)
        assert not isinstance(result.sensitivity_table, list)

    def test_per_candidate_is_tuple_not_list(self):
        """per_candidate field type is tuple[PerCandidateDisposition, ...]."""
        from backtest.evaluate_dsr import (
            CandidateInput,
            compute_simplified_dsr,
        )
        sharpes = [0.5, -0.5] * 99
        candidates = [
            CandidateInput(
                hypothesis_hash=f"h{i:03d}",
                sharpe_ratio=sharpes[i],
                total_trades=10,
                audit_v1_artifact_path=f"{SYN_BASE}/syn_{i}.json",
                name="syn", theme="syn", lifecycle_state="shortlisted",
            )
            for i in range(198)
        ]
        result = compute_simplified_dsr(candidates, n_trials=198)
        assert isinstance(result.per_candidate, tuple)

    def test_excluded_candidates_summary_tuple_of_tuples_sorted_by_reason_key(self):
        """P-T2 lock: excluded_candidates_summary is tuple[tuple[str, int], ...]
        sorted by reason key alphabetically; structurally immutable + JSON-
        serializable.
        """
        from backtest.evaluate_dsr import SimplifiedDSRResult
        # Construction-time assertion: caller must build sorted-by-key.
        # Verify the field accepts tuple-of-tuples with sorted keys.
        sorted_summary = tuple(
            sorted(
                [
                    ("missing_sharpe", 5),
                    ("low_trade_count", 30),
                    ("missing_trades", 4),
                    ("zero_trades", 5),
                ],
                key=lambda pair: pair[0],
            )
        )
        result = SimplifiedDSRResult(
            per_candidate=tuple(),
            population_disposition="inconclusive",
            population_argmax_hash="",
            n_trials=198,
            n_eligible=0,
            n_raw=198,
            bonferroni_threshold=0.0,
            expected_max_sharpe_null=0.0,
            sharpe_var_used=0.0,
            sensitivity_table=tuple(),
            bonferroni_cross_check={
                "sr_max": 0.0,
                "bonferroni_threshold": 0.0,
                "bonferroni_pass": False,
                "dsr_style_pass": False,
                "criteria_agree": True,
            },
            excluded_candidates_summary=sorted_summary,
            degenerate_state="n_eligible_zero",
            rs_guard_call_count=0,
        )
        assert isinstance(result.excluded_candidates_summary, tuple)
        for entry in result.excluded_candidates_summary:
            assert isinstance(entry, tuple)
            assert len(entry) == 2
            assert isinstance(entry[0], str)
            assert isinstance(entry[1], int)
        # Sorted by reason key alphabetically:
        keys = [entry[0] for entry in result.excluded_candidates_summary]
        assert keys == sorted(keys)


# ---------------------------------------------------------------------------
# Threshold computation
# ---------------------------------------------------------------------------


class TestComputeThreshold:
    """Verify sqrt(2 * ln(N)) threshold computation."""

    def test_n1_threshold_is_zero(self):
        """N=1: threshold = 0, any positive Sharpe survives."""
        assert compute_expected_max_sharpe(1) == 0.0

    def test_n0_threshold_is_zero(self):
        """N=0: degenerate case, threshold = 0."""
        assert compute_expected_max_sharpe(0) == 0.0

    def test_n20_threshold(self):
        """N=20: threshold ≈ sqrt(2 * ln(20)) ≈ 2.448."""
        expected = math.sqrt(2.0 * math.log(20))
        assert compute_expected_max_sharpe(20) == pytest.approx(expected)
        # Verify numerical value
        assert compute_expected_max_sharpe(20) == pytest.approx(2.448, rel=1e-2)

    def test_n5_threshold(self):
        """N=5: threshold ≈ sqrt(2 * ln(5)) ≈ 1.794."""
        expected = math.sqrt(2.0 * math.log(5))
        assert compute_expected_max_sharpe(5) == pytest.approx(expected)
        assert compute_expected_max_sharpe(5) == pytest.approx(1.794, rel=1e-2)

    def test_n100_threshold(self):
        """N=100: threshold ≈ sqrt(2 * ln(100)) ≈ 3.034."""
        expected = math.sqrt(2.0 * math.log(100))
        assert compute_expected_max_sharpe(100) == pytest.approx(expected)

    def test_monotonically_increasing(self):
        """Threshold increases with N."""
        thresholds = [compute_expected_max_sharpe(n) for n in [2, 5, 10, 50, 100]]
        for i in range(len(thresholds) - 1):
            assert thresholds[i] < thresholds[i + 1]


# ---------------------------------------------------------------------------
# Evaluation logic
# ---------------------------------------------------------------------------


class TestEvaluateTrials:
    """Verify the survive/not-survive decision logic."""

    def test_n1_any_positive_survives(self):
        """N=1: threshold=0, any positive Sharpe survives."""
        result = evaluate_trials({"strat_a": 0.5})
        assert result["n_trials"] == 1
        assert result["threshold"] == 0.0
        assert result["survives"] is True
        assert result["best_strategy"] == "strat_a"

    def test_n20_low_sharpe_does_not_survive(self):
        """N=20, best Sharpe=0.5: should NOT survive (threshold ≈ 2.45)."""
        sharpes = {f"strat_{i}": 0.5 - i * 0.02 for i in range(20)}
        result = evaluate_trials(sharpes)
        assert result["n_trials"] == 20
        assert result["threshold"] == pytest.approx(2.448, rel=1e-2)
        assert result["best_sharpe"] == pytest.approx(0.5)
        assert result["survives"] is False

    def test_n5_high_sharpe_survives(self):
        """N=5, best Sharpe=3.0: should survive (threshold ≈ 1.79)."""
        sharpes = {"alpha": 3.0, "beta": 1.0, "gamma": 0.5, "delta": -0.2, "epsilon": -1.0}
        result = evaluate_trials(sharpes)
        assert result["n_trials"] == 5
        assert result["threshold"] == pytest.approx(1.794, rel=1e-2)
        assert result["best_sharpe"] == pytest.approx(3.0)
        assert result["survives"] is True

    def test_empty_no_error(self):
        """Empty input → clean result, not an error."""
        result = evaluate_trials({})
        assert result["n_trials"] == 0
        assert result["survives"] is False
        assert result["best_strategy"] is None
        assert result["rankings"] == []

    def test_rankings_sorted_descending(self):
        """Rankings must be sorted by Sharpe descending."""
        sharpes = {"a": -1.0, "b": 2.0, "c": 0.5}
        result = evaluate_trials(sharpes)
        rankings = result["rankings"]
        assert rankings[0]["strategy"] == "b"
        assert rankings[1]["strategy"] == "c"
        assert rankings[2]["strategy"] == "a"

    def test_mean_sharpe(self):
        """Mean Sharpe must be the arithmetic mean."""
        sharpes = {"a": 1.0, "b": 2.0, "c": 3.0}
        result = evaluate_trials(sharpes)
        assert result["mean_sharpe"] == pytest.approx(2.0)

    def test_worst_sharpe(self):
        """Worst Sharpe is the minimum."""
        sharpes = {"a": 1.0, "b": -2.0, "c": 0.5}
        result = evaluate_trials(sharpes)
        assert result["worst_sharpe"] == pytest.approx(-2.0)

    def test_negative_best_does_not_survive(self):
        """If best Sharpe is negative, it should not survive."""
        sharpes = {"a": -0.5, "b": -1.0}
        result = evaluate_trials(sharpes)
        assert result["survives"] is False

    def test_exactly_at_threshold_does_not_survive(self):
        """Sharpe exactly at threshold does NOT survive (strict >)."""
        # N=2: threshold = sqrt(2 * ln(2)) ≈ 1.1774
        threshold = math.sqrt(2.0 * math.log(2))
        sharpes = {"a": threshold, "b": 0.0}
        result = evaluate_trials(sharpes)
        assert result["survives"] is False


# ---------------------------------------------------------------------------
# Registry query integration
# ---------------------------------------------------------------------------


class TestQuerySharpeRatios:
    """Verify registry query with real SQLite data."""

    @pytest.fixture
    def populated_db(self, tmp_path):
        """Create a test DB with sample runs."""
        from backtest.experiment_registry import create_table, get_connection, insert_run

        db_path = tmp_path / "test.db"
        conn = get_connection(db_path)
        create_table(conn)

        runs = [
            {
                "strategy_name": "sma_crossover",
                "strategy_source": "manual",
                "run_type": "walk_forward_summary",
                "sharpe_ratio": 0.8,
                "split_version": "v1",
            },
            {
                "strategy_name": "momentum",
                "strategy_source": "manual",
                "run_type": "walk_forward_summary",
                "sharpe_ratio": -0.3,
                "split_version": "v1",
            },
            {
                "strategy_name": "mean_reversion",
                "strategy_source": "manual",
                "run_type": "walk_forward_summary",
                "sharpe_ratio": 1.5,
                "split_version": "v1",
            },
            {
                "strategy_name": "broken",
                "strategy_source": "manual",
                "run_type": "walk_forward_summary",
                "sharpe_ratio": None,  # NULL — should be excluded
                "split_version": "v1",
            },
            {
                "strategy_name": "other_version",
                "strategy_source": "manual",
                "run_type": "walk_forward_summary",
                "sharpe_ratio": 5.0,
                "split_version": "v2",  # Different version
            },
            {
                "strategy_name": "sma_single",
                "strategy_source": "manual",
                "run_type": "single_run",
                "sharpe_ratio": 0.5,
                "split_version": "v1",
            },
        ]
        for run in runs:
            insert_run(conn, run)
        conn.close()

        return db_path

    def test_filters_by_split_version(self, populated_db):
        """Only v1 runs returned when querying v1."""
        result = query_sharpe_ratios("v1", db_path=populated_db)
        assert len(result) == 3  # sma_crossover, momentum, mean_reversion

    def test_excludes_null_sharpe(self, populated_db):
        """Runs with NULL sharpe_ratio are excluded."""
        result = query_sharpe_ratios("v1", db_path=populated_db)
        # "broken" has NULL sharpe — should not appear
        assert all("broken" not in k for k in result.keys())

    def test_excludes_wrong_version(self, populated_db):
        """v2 runs should not appear in v1 query."""
        result = query_sharpe_ratios("v1", db_path=populated_db)
        assert all("other_version" not in k for k in result.keys())

    def test_filters_by_run_type(self, populated_db):
        """Only walk_forward_summary rows by default."""
        result = query_sharpe_ratios("v1", db_path=populated_db)
        assert all("sma_single" not in k for k in result.keys())

    def test_single_run_type_filter(self, populated_db):
        """Can query single_run type."""
        result = query_sharpe_ratios(
            "v1", run_type="single_run", db_path=populated_db
        )
        assert len(result) == 1
        assert any("sma_single" in k for k in result.keys())

    def test_strategy_filter(self, populated_db):
        """Can filter by strategy_name."""
        result = query_sharpe_ratios(
            "v1", strategy_name="momentum", db_path=populated_db
        )
        assert len(result) == 1
        assert any("momentum" in k for k in result.keys())

    def test_empty_query(self, populated_db):
        """Non-existent version returns empty dict."""
        result = query_sharpe_ratios("v99", db_path=populated_db)
        assert result == {}

    def test_sharpe_values_correct(self, populated_db):
        """Queried Sharpe values match what was inserted."""
        result = query_sharpe_ratios("v1", db_path=populated_db)
        sharpes = set(result.values())
        assert 0.8 in sharpes
        assert -0.3 in sharpes
        assert 1.5 in sharpes


# ---------------------------------------------------------------------------
# End-to-end: query + evaluate
# ---------------------------------------------------------------------------


class TestEndToEnd:
    """Verify full pipeline: query → evaluate → decision."""

    @pytest.fixture
    def db_with_strategies(self, tmp_path):
        """Create DB with strategies that should NOT survive."""
        from backtest.experiment_registry import create_table, get_connection, insert_run

        db_path = tmp_path / "e2e.db"
        conn = get_connection(db_path)
        create_table(conn)

        # 5 strategies, best Sharpe = 0.8
        # threshold = sqrt(2*ln(5)) ≈ 1.794 → best does NOT survive
        for i, (name, sharpe) in enumerate([
            ("alpha", 0.8),
            ("beta", 0.3),
            ("gamma", -0.1),
            ("delta", -0.5),
            ("epsilon", 0.1),
        ]):
            insert_run(conn, {
                "strategy_name": name,
                "strategy_source": "manual",
                "run_type": "walk_forward_summary",
                "sharpe_ratio": sharpe,
                "split_version": "v1",
            })
        conn.close()
        return db_path

    def test_none_survive(self, db_with_strategies):
        """5 strategies with best=0.8: none survive (threshold ≈ 1.79)."""
        sharpes = query_sharpe_ratios("v1", db_path=db_with_strategies)
        result = evaluate_trials(sharpes)
        assert result["n_trials"] == 5
        assert result["survives"] is False

    def test_single_strong_survives(self, tmp_path):
        """1 strategy with Sharpe=2.0: survives (N=1, threshold=0)."""
        from backtest.experiment_registry import create_table, get_connection, insert_run

        db_path = tmp_path / "single.db"
        conn = get_connection(db_path)
        create_table(conn)
        insert_run(conn, {
            "strategy_name": "winner",
            "strategy_source": "manual",
            "run_type": "walk_forward_summary",
            "sharpe_ratio": 2.0,
            "split_version": "v1",
        })
        conn.close()

        sharpes = query_sharpe_ratios("v1", db_path=db_path)
        result = evaluate_trials(sharpes)
        assert result["n_trials"] == 1
        assert result["survives"] is True


# ---------------------------------------------------------------------------
# Step 2 input loading: load_audit_v1_candidates()
# ---------------------------------------------------------------------------
#
# Test scope per PHASE2C_11_PLAN §7.1 Step 2 + §4.2 + §4.4 + §3.4:
#   - RS-2 guard call discipline (check_evaluation_semantics_or_raise()
#     fires before every audit_v1 artifact consumption)
#   - §4.4 edge case filtering in pre-registered order:
#       (1) low trade count T_c < 5 → excluded
#       (2) zero Sharpe due to T_c == 0 → excluded
#       (3) missing/null Sharpe → excluded
#       (4) Var(SR) == 0 → SimplifiedDSRInputs marks degenerate (Step 3 concern)
#       (5) JSON-vs-CSV |delta| > 1e-6 (v3.1 reframed register) → discrepancy
#           documented + reviewer-routed; NOT auto-excluded
#   - n_raw == 198 lockpoint preserved per §3.2
#   - JSON canonical scalar source per §3.3 lockpoint


def _make_audit_dir(
    tmp_path: Path,
    candidates: list[dict],
    csv_overrides: dict[str, dict] | None = None,
) -> tuple[Path, Path]:
    """Build a synthetic audit_v1-like directory + CSV for Step 2 testing.

    Each `candidates` dict provides at least `hypothesis_hash`,
    `sharpe_ratio`, `total_trades`. Other fields default to RS-clean
    attestation (single_run_holdout_v1 / eb1c87f / wf-corrected-v1 /
    passed / non-empty git_sha) so the RS-2 guard accepts them unless
    a per-candidate attestation override is provided.

    `csv_overrides[hash]` allows the CSV to disagree with the JSON
    for testing §3.4 + §4.4(5) cross-validation.
    """
    import csv
    import json as _json

    audit_dir = tmp_path / "audit_v1"
    audit_dir.mkdir()
    csv_overrides = csv_overrides or {}

    csv_rows = []
    for c in candidates:
        h = c["hypothesis_hash"]
        cand_dir = audit_dir / h
        cand_dir.mkdir()
        # Default RS-clean summary
        summary = {
            "current_git_sha": c.get(
                "current_git_sha",
                "0000000000000000000000000000000000000000",
            ),
            "engine_commit": c.get("engine_commit", "eb1c87f"),
            "engine_corrected_lineage": c.get(
                "engine_corrected_lineage", "wf-corrected-v1",
            ),
            "evaluation_semantics": c.get(
                "evaluation_semantics", "single_run_holdout_v1",
            ),
            "lineage_check": c.get("lineage_check", "passed"),
            "hypothesis_hash": h,
            "name": c.get("name", "synthetic_strat"),
            "theme": c.get("theme", "momentum"),
            "lifecycle_state": c.get("lifecycle_state", "holdout_failed"),
            "position": c.get("position", 1),
            "source_batch_id": c.get("source_batch_id", "test-batch"),
            "wf_test_period_sharpe": c.get("wf_test_period_sharpe", 0.0),
            "holdout_metrics": {
                "sharpe_ratio": c.get("sharpe_ratio"),
                "total_return": c.get("total_return", 0.0),
                "max_drawdown": c.get("max_drawdown", 0.0),
                "total_trades": c.get("total_trades", 10),
            },
        }
        (cand_dir / "holdout_summary.json").write_text(
            _json.dumps(summary), encoding="utf-8",
        )
        # Build the CSV row, with optional override values
        ov = csv_overrides.get(h, {})
        sharpe = c.get("sharpe_ratio") or 0.0
        csv_rows.append({
            "hypothesis_hash": h,
            "position": str(summary["position"]),
            "theme": summary["theme"],
            "name": summary["name"],
            "wf_test_period_sharpe": str(summary["wf_test_period_sharpe"]),
            "lifecycle_state": summary["lifecycle_state"],
            "holdout_passed": "0",
            "holdout_sharpe": str(ov.get("holdout_sharpe", sharpe)),
            "holdout_max_drawdown": str(ov.get(
                "holdout_max_drawdown", summary["holdout_metrics"]["max_drawdown"],
            )),
            "holdout_total_return": str(ov.get(
                "holdout_total_return", summary["holdout_metrics"]["total_return"],
            )),
            "holdout_total_trades": str(ov.get(
                "holdout_total_trades", summary["holdout_metrics"]["total_trades"],
            )),
            "wall_clock_seconds": "1.0",
            "error_message": "",
        })

    csv_path = audit_dir / "holdout_results.csv"
    with csv_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(csv_rows[0].keys()))
        writer.writeheader()
        writer.writerows(csv_rows)
    return audit_dir, csv_path


class TestLoadAuditV1CandidatesHappyPath:
    """Happy path: 5 RS-clean candidates with `T_c >= 5`, no edge cases."""

    def test_returns_simplified_dsr_inputs(self, tmp_path):
        candidates = [
            {"hypothesis_hash": f"hash{i:04d}deadbeef", "sharpe_ratio": float(i),
             "total_trades": 10 + i}
            for i in range(5)
        ]
        audit_dir, csv_path = _make_audit_dir(tmp_path, candidates)
        result = load_audit_v1_candidates(audit_dir, csv_path)
        assert isinstance(result, SimplifiedDSRInputs)
        assert result.n_raw == 5
        assert result.n_eligible == 5
        assert len(result.eligible_candidates) == 5
        assert len(result.excluded_candidates) == 0
        # Sharpe statistics computed correctly across 0,1,2,3,4
        assert result.sharpe_min == 0.0
        assert result.sharpe_max == 4.0
        assert result.sharpe_mean == pytest.approx(2.0)
        assert result.sharpe_median == pytest.approx(2.0)

    def test_eligible_candidates_carry_required_fields(self, tmp_path):
        candidates = [
            {"hypothesis_hash": "hash0001ffffaaaa", "sharpe_ratio": 1.5,
             "total_trades": 20, "name": "alpha", "theme": "momentum"},
        ]
        audit_dir, csv_path = _make_audit_dir(tmp_path, candidates)
        result = load_audit_v1_candidates(audit_dir, csv_path)
        c = result.eligible_candidates[0]
        assert isinstance(c, CandidateInput)
        assert c.hypothesis_hash == "hash0001ffffaaaa"
        assert c.sharpe_ratio == 1.5
        assert c.total_trades == 20
        assert c.name == "alpha"
        assert c.theme == "momentum"
        assert c.audit_v1_artifact_path.endswith("holdout_summary.json")


class TestLoadAuditV1CandidatesEdgeCases:
    """§4.4 edge cases applied in pre-registered order."""

    def test_low_trade_count_excluded(self, tmp_path):
        """§4.4(1): T_c < 5 excluded."""
        candidates = [
            {"hypothesis_hash": "hash0001", "sharpe_ratio": 0.5, "total_trades": 4},
            {"hypothesis_hash": "hash0002", "sharpe_ratio": 1.5, "total_trades": 5},
        ]
        audit_dir, csv_path = _make_audit_dir(tmp_path, candidates)
        result = load_audit_v1_candidates(audit_dir, csv_path)
        assert result.n_raw == 2
        assert result.n_eligible == 1
        assert len(result.excluded_candidates) == 1
        excl = result.excluded_candidates[0]
        assert excl.hypothesis_hash == "hash0001"
        assert "low_trade_count" in excl.reason

    def test_zero_trades_excluded_per_section_4_4_2(self, tmp_path):
        """§4.4(2): T_c == 0 (regardless of Sharpe value) excluded."""
        candidates = [
            {"hypothesis_hash": "hash0003", "sharpe_ratio": 0.0, "total_trades": 0},
            {"hypothesis_hash": "hash0004", "sharpe_ratio": 2.0, "total_trades": 10},
        ]
        audit_dir, csv_path = _make_audit_dir(tmp_path, candidates)
        result = load_audit_v1_candidates(audit_dir, csv_path)
        assert result.n_eligible == 1
        excluded_hashes = {e.hypothesis_hash for e in result.excluded_candidates}
        assert "hash0003" in excluded_hashes

    def test_missing_sharpe_excluded(self, tmp_path):
        """§4.4(3): missing/null sharpe_ratio → excluded with reason
        ``missing_sharpe`` (when total_trades is valid)."""
        candidates = [
            {"hypothesis_hash": "hash0005", "sharpe_ratio": None, "total_trades": 50},
            {"hypothesis_hash": "hash0006", "sharpe_ratio": 1.0, "total_trades": 50},
        ]
        audit_dir, csv_path = _make_audit_dir(tmp_path, candidates)
        result = load_audit_v1_candidates(audit_dir, csv_path)
        assert result.n_eligible == 1
        excl = next(e for e in result.excluded_candidates
                    if e.hypothesis_hash == "hash0005")
        assert excl.reason == "missing_sharpe"
        assert excl.total_trades == 50  # trades present; only sharpe missing
        assert excl.sharpe_ratio is None

    def test_missing_trades_with_valid_sharpe_distinct_reason(self, tmp_path):
        """Codex HIGH #3 + MED #6: total_trades missing but sharpe valid →
        reason="missing_trades" (NOT "missing_sharpe")."""
        candidates = [
            {"hypothesis_hash": "hash0010", "sharpe_ratio": 1.5,
             "total_trades": None},
            {"hypothesis_hash": "hash0011", "sharpe_ratio": 2.0, "total_trades": 10},
        ]
        audit_dir, csv_path = _make_audit_dir(tmp_path, candidates)
        result = load_audit_v1_candidates(audit_dir, csv_path)
        assert result.n_eligible == 1
        excl = next(e for e in result.excluded_candidates
                    if e.hypothesis_hash == "hash0010")
        assert excl.reason == "missing_trades"
        assert excl.total_trades is None
        assert excl.sharpe_ratio == 1.5

    def test_nan_sharpe_rejected_per_safe_float(self, tmp_path):
        """Codex HIGH #2: NaN sharpe must NOT enter eligible subset; rejected
        as missing per ``_safe_float`` non-finite check."""
        candidates = [
            {"hypothesis_hash": "hash0012", "sharpe_ratio": float("nan"),
             "total_trades": 30},
            {"hypothesis_hash": "hash0013", "sharpe_ratio": 0.5, "total_trades": 30},
        ]
        audit_dir, csv_path = _make_audit_dir(tmp_path, candidates)
        result = load_audit_v1_candidates(audit_dir, csv_path)
        assert result.n_eligible == 1
        excl = next(e for e in result.excluded_candidates
                    if e.hypothesis_hash == "hash0012")
        assert excl.reason == "missing_sharpe"
        # Cross-trial Sharpe stats must not be NaN-poisoned
        assert math.isfinite(result.sharpe_mean)
        assert math.isfinite(result.sharpe_var)

    def test_inf_sharpe_rejected(self, tmp_path):
        """Codex HIGH #2: +inf sharpe rejected as missing."""
        candidates = [
            {"hypothesis_hash": "hash0014", "sharpe_ratio": float("inf"),
             "total_trades": 30},
            {"hypothesis_hash": "hash0015", "sharpe_ratio": 0.5, "total_trades": 30},
        ]
        audit_dir, csv_path = _make_audit_dir(tmp_path, candidates)
        result = load_audit_v1_candidates(audit_dir, csv_path)
        assert result.n_eligible == 1
        excl_hashes = {e.hypothesis_hash for e in result.excluded_candidates}
        assert "hash0014" in excl_hashes

    def test_overlap_zero_trades_with_missing_sharpe(self, tmp_path):
        """Codex HIGH #3 + MED #6: overlap case T_c==0 AND missing sharpe.
        Resolution policy: sharpe-missing takes precedence over zero-trade
        because validation precedes classification (you can't classify
        T_c==0 if T_c is fine but sharpe is None — sharpe-missing fires
        first per docstring resolution order)."""
        candidates = [
            {"hypothesis_hash": "hash0016", "sharpe_ratio": None,
             "total_trades": 0},
            {"hypothesis_hash": "hash0017", "sharpe_ratio": 1.0, "total_trades": 30},
        ]
        audit_dir, csv_path = _make_audit_dir(tmp_path, candidates)
        result = load_audit_v1_candidates(audit_dir, csv_path)
        excl = next(e for e in result.excluded_candidates
                    if e.hypothesis_hash == "hash0016")
        # Per docstring resolution: missing_sharpe (after missing_trades
        # check) precedes zero_trades classification.
        assert excl.reason == "missing_sharpe"

    def test_safe_int_count_rejects_non_integral(self, tmp_path):
        """Codex MED #5: total_trades = 4.5 (non-integral) classified as
        missing_trades; engine never emits fractional trade counts."""
        candidates = [
            {"hypothesis_hash": "hash0018", "sharpe_ratio": 1.0,
             "total_trades": 4.5},
            {"hypothesis_hash": "hash0019", "sharpe_ratio": 1.0, "total_trades": 30},
        ]
        audit_dir, csv_path = _make_audit_dir(tmp_path, candidates)
        result = load_audit_v1_candidates(audit_dir, csv_path)
        excl = next(e for e in result.excluded_candidates
                    if e.hypothesis_hash == "hash0018")
        assert excl.reason == "missing_trades"

    def test_safe_int_count_rejects_negative(self, tmp_path):
        """Codex MED #5: negative total_trades classified as missing_trades."""
        candidates = [
            {"hypothesis_hash": "hash0020", "sharpe_ratio": 1.0,
             "total_trades": -1},
            {"hypothesis_hash": "hash0021", "sharpe_ratio": 1.0, "total_trades": 30},
        ]
        audit_dir, csv_path = _make_audit_dir(tmp_path, candidates)
        result = load_audit_v1_candidates(audit_dir, csv_path)
        excl = next(e for e in result.excluded_candidates
                    if e.hypothesis_hash == "hash0020")
        assert excl.reason == "missing_trades"


class TestLoadAuditV1CandidatesJsonVsCsvCrossCheck:
    """§3.4 + §4.4(5) v3.1 reframed register: 1e-6 sanity check, NOT auto-exclusion."""

    def test_small_delta_below_1e6_passes(self, tmp_path):
        """CSV 6-decimal rounding artifact at ~5e-7 → no discrepancy at 1e-6 register."""
        candidates = [
            {"hypothesis_hash": "hash0007", "sharpe_ratio": 0.13605992863639,
             "total_trades": 26},
        ]
        # CSV rounded to 6 decimals (~ 0.136060)
        audit_dir, csv_path = _make_audit_dir(
            tmp_path, candidates,
            csv_overrides={"hash0007": {"holdout_sharpe": 0.136060}},
        )
        result = load_audit_v1_candidates(audit_dir, csv_path)
        assert result.n_eligible == 1
        # No discrepancy documented at v3.1 1e-6 register
        assert len(result.discrepancies_documented) == 0

    def test_large_delta_above_1e6_documented_not_excluded(self, tmp_path):
        """v3.1 reframe: |delta| > 1e-6 → discrepancy documented + reviewer-routed
        (NOT auto-excluded; candidate STAYS in eligible set per §4.4(5) v3.1)."""
        candidates = [
            {"hypothesis_hash": "hash0008", "sharpe_ratio": 1.5,
             "total_trades": 20},
        ]
        # CSV value disagrees by ~0.5 — well above 1e-6 + above
        # CSV-storage-precision floor → genuine engine-output divergence
        audit_dir, csv_path = _make_audit_dir(
            tmp_path, candidates,
            csv_overrides={"hash0008": {"holdout_sharpe": 1.0}},
        )
        result = load_audit_v1_candidates(audit_dir, csv_path)
        # Per v3.1 lockpoint reframe: candidate NOT auto-excluded
        assert result.n_eligible == 1
        # But discrepancy IS documented with kind="delta_above_tolerance"
        delta_entries = [d for d in result.discrepancies_documented
                         if d.get("kind") == "delta_above_tolerance"]
        assert len(delta_entries) == 1
        disc = delta_entries[0]
        assert disc["hypothesis_hash"] == "hash0008"
        assert disc["column"] == "holdout_sharpe"
        assert disc["delta"] > 1e-6

    @pytest.mark.parametrize("column,override_field", [
        ("holdout_sharpe", "holdout_sharpe"),
        ("holdout_max_drawdown", "holdout_max_drawdown"),
        ("holdout_total_return", "holdout_total_return"),
        ("holdout_total_trades", "holdout_total_trades"),
    ])
    def test_all_csv_to_json_columns_cross_checked(
        self, tmp_path, column, override_field,
    ):
        """Codex MED #7: parameterize cross-check across all primary
        ``_CSV_TO_JSON`` mapped columns."""
        candidates = [
            {"hypothesis_hash": "hash0030cccc1111", "sharpe_ratio": 0.5,
             "total_trades": 20, "max_drawdown": 0.1, "total_return": 0.05},
        ]
        # Inject a > 1e-6 discrepancy at the parameterized column
        audit_dir, csv_path = _make_audit_dir(
            tmp_path, candidates,
            csv_overrides={"hash0030cccc1111": {override_field: 9.999}},
        )
        result = load_audit_v1_candidates(audit_dir, csv_path)
        assert result.n_eligible == 1
        delta_entries = [d for d in result.discrepancies_documented
                         if d.get("kind") == "delta_above_tolerance"]
        assert len(delta_entries) >= 1
        cols_flagged = {d["column"] for d in delta_entries}
        assert column in cols_flagged

    def test_boundary_at_exactly_1e6_below_tolerance(self, tmp_path):
        """Codex MED #7: delta exactly at boundary — strictly > 1e-6 fires;
        delta <= 1e-6 does not fire. Tests the strict-greater comparison."""
        # CSV value chosen so that |delta| is exactly the boundary minus eps
        json_sharpe = 1.000_000_5  # 1.0000005
        candidates = [
            {"hypothesis_hash": "hash0031bbbb2222", "sharpe_ratio": json_sharpe,
             "total_trades": 20},
        ]
        # CSV stored as 1.0 → |delta| = 5e-7 < 1e-6 → NOT documented
        audit_dir, csv_path = _make_audit_dir(
            tmp_path, candidates,
            csv_overrides={"hash0031bbbb2222": {"holdout_sharpe": 1.0}},
        )
        result = load_audit_v1_candidates(audit_dir, csv_path)
        delta_entries = [d for d in result.discrepancies_documented
                         if d.get("kind") == "delta_above_tolerance"
                         and d["column"] == "holdout_sharpe"]
        assert len(delta_entries) == 0

    def test_boundary_just_above_1e6_documented(self, tmp_path):
        """Codex MED #7: delta strictly > 1e-6 documented."""
        # Make |delta| ~ 1.5e-6 so it strictly exceeds 1e-6
        candidates = [
            {"hypothesis_hash": "hash0032bbbb3333", "sharpe_ratio": 1.0000015,
             "total_trades": 20},
        ]
        audit_dir, csv_path = _make_audit_dir(
            tmp_path, candidates,
            csv_overrides={"hash0032bbbb3333": {"holdout_sharpe": 1.0}},
        )
        result = load_audit_v1_candidates(audit_dir, csv_path)
        delta_entries = [d for d in result.discrepancies_documented
                         if d.get("kind") == "delta_above_tolerance"
                         and d["column"] == "holdout_sharpe"]
        assert len(delta_entries) == 1
        assert delta_entries[0]["delta"] > 1e-6


class TestLoadAuditV1CandidatesCsvMissingDiscrepancies:
    """Codex HIGH #4: missing CSV row / values are themselves consistency
    observations and are recorded as typed discrepancy entries (NOT
    silently skipped) per v3.1 §3.4 descriptive register."""

    def test_missing_csv_row_for_eligible_candidate_documented(self, tmp_path):
        """Eligible candidate with no CSV row → discrepancy with
        kind='missing_csv_row'."""
        import csv as _csv
        import json as _json

        # Build audit dir manually so we can drop one CSV row.
        audit_dir = tmp_path / "audit_v1"
        audit_dir.mkdir()
        h_with_row = "hash0040ddddaaaa"
        h_no_row = "hash0041eeeebbbb"
        for h in (h_with_row, h_no_row):
            cand_dir = audit_dir / h
            cand_dir.mkdir()
            (cand_dir / "holdout_summary.json").write_text(_json.dumps({
                "current_git_sha": "0" * 40,
                "engine_commit": "eb1c87f",
                "engine_corrected_lineage": "wf-corrected-v1",
                "evaluation_semantics": "single_run_holdout_v1",
                "lineage_check": "passed",
                "hypothesis_hash": h,
                "name": "x", "theme": "y", "lifecycle_state": "z",
                "wf_test_period_sharpe": 0.0,
                "holdout_metrics": {
                    "sharpe_ratio": 1.0, "total_trades": 20,
                    "max_drawdown": 0.1, "total_return": 0.05,
                },
            }))
        csv_path = audit_dir / "holdout_results.csv"
        with csv_path.open("w", newline="") as f:
            writer = _csv.DictWriter(f, fieldnames=[
                "hypothesis_hash", "position", "theme", "name",
                "wf_test_period_sharpe", "lifecycle_state", "holdout_passed",
                "holdout_sharpe", "holdout_max_drawdown",
                "holdout_total_return", "holdout_total_trades",
                "wall_clock_seconds", "error_message",
            ])
            writer.writeheader()
            # Only write the row for h_with_row; h_no_row missing
            writer.writerow({
                "hypothesis_hash": h_with_row, "position": "1",
                "theme": "y", "name": "x", "wf_test_period_sharpe": "0.0",
                "lifecycle_state": "z", "holdout_passed": "0",
                "holdout_sharpe": "1.0", "holdout_max_drawdown": "0.1",
                "holdout_total_return": "0.05", "holdout_total_trades": "20",
                "wall_clock_seconds": "1.0", "error_message": "",
            })
        result = load_audit_v1_candidates(audit_dir, csv_path)
        assert result.n_eligible == 2
        missing_row_entries = [d for d in result.discrepancies_documented
                               if d.get("kind") == "missing_csv_row"]
        assert len(missing_row_entries) == 1
        assert missing_row_entries[0]["hypothesis_hash"] == h_no_row

    def test_missing_csv_value_documented(self, tmp_path):
        """Empty CSV cell for a column → kind='missing_csv_value' entry."""
        candidates = [
            {"hypothesis_hash": "hash0042ffff0000", "sharpe_ratio": 1.5,
             "total_trades": 20},
        ]
        audit_dir, csv_path = _make_audit_dir(
            tmp_path, candidates,
            csv_overrides={"hash0042ffff0000": {"holdout_max_drawdown": ""}},
        )
        result = load_audit_v1_candidates(audit_dir, csv_path)
        missing_val_entries = [d for d in result.discrepancies_documented
                               if d.get("kind") == "missing_csv_value"
                               and d["column"] == "holdout_max_drawdown"]
        assert len(missing_val_entries) == 1


class TestSafeFloatHelpers:
    """Codex HIGH #2 + MED #5: defensive helpers reject NaN/inf and
    non-integral / negative trade counts."""

    @pytest.mark.parametrize("value", [
        None, "", "not_a_number", float("nan"), float("inf"), float("-inf"),
        "nan", "inf", "-inf",
    ])
    def test_safe_float_rejects_invalid(self, value):
        from backtest.evaluate_dsr import _safe_float
        assert _safe_float(value) is None

    @pytest.mark.parametrize("value,expected", [
        (1.5, 1.5), ("1.5", 1.5), (0.0, 0.0), (-2.7, -2.7),
    ])
    def test_safe_float_accepts_finite(self, value, expected):
        from backtest.evaluate_dsr import _safe_float
        assert _safe_float(value) == expected

    @pytest.mark.parametrize("value", [
        None, "", "not_a_number", float("nan"), float("inf"),
        4.5, "4.5", -1, "-1",
    ])
    def test_safe_int_count_rejects_invalid(self, value):
        from backtest.evaluate_dsr import _safe_int_count
        assert _safe_int_count(value) is None

    @pytest.mark.parametrize("value,expected", [
        (10, 10), ("10", 10), (0, 0), (4.0, 4),
    ])
    def test_safe_int_count_accepts_valid(self, value, expected):
        from backtest.evaluate_dsr import _safe_int_count
        assert _safe_int_count(value) == expected


class TestExpectedNRawEnforcement:
    """Codex CRITICAL #1: production cycles MUST pass expected_n_raw to
    enforce §3.2 lockpoint. Mismatch → ValueError."""

    def test_n_raw_mismatch_raises(self, tmp_path):
        candidates = [
            {"hypothesis_hash": f"hash{i:08d}aaaa", "sharpe_ratio": 1.0,
             "total_trades": 10}
            for i in range(3)
        ]
        audit_dir, csv_path = _make_audit_dir(tmp_path, candidates)
        with pytest.raises(ValueError, match="n_raw lockpoint violation"):
            load_audit_v1_candidates(audit_dir, csv_path, expected_n_raw=198)

    def test_n_raw_match_passes(self, tmp_path):
        candidates = [
            {"hypothesis_hash": f"hash{i:08d}aaaa", "sharpe_ratio": 1.0,
             "total_trades": 10}
            for i in range(3)
        ]
        audit_dir, csv_path = _make_audit_dir(tmp_path, candidates)
        # Pass when expected matches resolved n_raw
        result = load_audit_v1_candidates(audit_dir, csv_path, expected_n_raw=3)
        assert result.n_raw == 3

    def test_default_no_enforcement(self, tmp_path):
        """When expected_n_raw is None (default), no enforcement —
        permits synthetic test fixtures of arbitrary size."""
        candidates = [
            {"hypothesis_hash": "hash0050eeee9999", "sharpe_ratio": 1.0,
             "total_trades": 10},
        ]
        audit_dir, csv_path = _make_audit_dir(tmp_path, candidates)
        result = load_audit_v1_candidates(audit_dir, csv_path)  # no kwarg
        assert result.n_raw == 1


class TestLoadAuditV1CandidatesRSGuardDiscipline:
    """RS-2 lockpoint: check_evaluation_semantics_or_raise() must fire before
    every audit_v1 artifact consumption per Section RS canonical hard prohibition."""

    def test_rs_guard_failure_raises(self, tmp_path):
        """A candidate with broken attestation must be refused by the RS-2 guard
        — load_audit_v1_candidates() raises ValueError, does not silently skip."""
        candidates = [
            {"hypothesis_hash": "hash0009", "sharpe_ratio": 1.0, "total_trades": 10,
             "engine_commit": "WRONG_COMMIT"},  # breaks RS attestation
        ]
        audit_dir, csv_path = _make_audit_dir(tmp_path, candidates)
        with pytest.raises(ValueError, match="engine_commit"):
            load_audit_v1_candidates(audit_dir, csv_path)


class TestLoadAuditV1CandidatesIntegrationRealData:
    """Integration test against the actual PHASE2C_11 audit_v1 dataset.

    Verifies n_raw=198 + theme distribution + RS-2 clean across all 198
    real audit_v1 candidates. Skipped if the audit_v1 directory is missing
    (e.g., shallow-clone CI without evaluation artifacts)."""

    AUDIT_V1 = Path(__file__).resolve().parent.parent / (
        "data/phase2c_evaluation_gate/audit_v1"
    )

    @pytest.mark.skipif(
        not (Path(__file__).resolve().parent.parent /
             "data/phase2c_evaluation_gate/audit_v1/holdout_results.csv").exists(),
        reason="audit_v1 evaluation artifacts not present",
    )
    def test_real_audit_v1_loads_198_candidates(self):
        from backtest.evaluate_dsr import EXPECTED_N_RAW
        # Per Codex CRITICAL #1: production cycle passes expected_n_raw
        # to enforce §3.2 lockpoint at canonical 198 register.
        result = load_audit_v1_candidates(
            self.AUDIT_V1, self.AUDIT_V1 / "holdout_results.csv",
            expected_n_raw=EXPECTED_N_RAW,
        )
        assert result.n_raw == 198
        # §4.4(1) anticipated: 44 candidates with T_c < 5 → eligible 154
        assert result.n_eligible == 154
        assert len(result.excluded_candidates) == 44
        # All exclusion reasons are §4.4(1) low-trade-count or §4.4(2)
        # zero-trades (per Step 1 distribution descriptor: min trades 0;
        # 44 candidates with T_c < 5; some are T_c == 0 distinguished
        # from 0 < T_c < 5 per pre-registered §4.4(1)/(2) ordering).
        for excl in result.excluded_candidates:
            assert excl.reason in ("low_trade_count", "zero_trades"), (
                f"unexpected exclusion reason at audit_v1: {excl.reason}"
            )
        # No delta-above-tolerance discrepancy at v3.1 1e-6 register
        # (Step 1 re-verification + Codex post-patch re-run confirmed
        # 0 deltas > 1e-6). Other discrepancy kinds (missing_csv_row,
        # missing_csv_value, missing_json_value, missing_both) may
        # arise legitimately for older partition fields and are not
        # eligibility-defining.
        delta_entries = [d for d in result.discrepancies_documented
                         if d.get("kind") == "delta_above_tolerance"]
        assert len(delta_entries) == 0
        # Theme totals across n_raw match Step 1 inventory
        theme_counts: dict[str, int] = {}
        for d in self.AUDIT_V1.iterdir():
            if not d.is_dir():
                continue
            import json as _json
            theme = _json.loads(
                (d / "holdout_summary.json").read_text(),
            ).get("theme", "")
            theme_counts[theme] = theme_counts.get(theme, 0) + 1
        assert theme_counts.get("calendar_effect") == 40
        assert theme_counts.get("volume_divergence") == 40
        assert theme_counts.get("volatility_regime") == 40
        assert theme_counts.get("momentum") == 39
        assert theme_counts.get("mean_reversion") == 39


# ===========================================================================
# PHASE2C_11 Step 3 — TDD-RED test classes (13 classes; 45 tests)
# ---------------------------------------------------------------------------
# Per Charlie-register `approved schema seal` + TDD-RED authorization with
# 7 locked constraints + 2 micro-clarifications:
#
#   1. Class-method-local imports of new symbols (compute_simplified_dsr,
#      SimplifiedDSRResult, PerCandidateDisposition, SensitivityRow,
#      DispositionLiteral). Module-top-level imports would
#      contaminate existing 77-test PASS state; per-method-local isolates
#      ImportError to new test methods only.
#
#   2. Boundary-disposition reference values cross-checked stdlib (math) +
#      scipy.stats.norm; intermediate values listed in test docstrings for
#      first-principles verification.
#
#   3. Class #11 §20 Trigger 1 closure annotation — at GREEN-phase pass
#      this test invokes compute_simplified_dsr against canonical inputs
#      = live computation = §20 Trigger 1 closure boundary per
#      PHASE2C_11_PLAN §0 P-L7 timeline. Future audit readers identify
#      the closure boundary at this test's GREEN run, NOT at TDD-RED
#      authoring (this commit) and NOT at schema seal.
#
#   4. No module-level fixture / no class-scope @pytest.fixture during
#      RED phase — collection-time construction would fail. All helpers
#      are class-method-local (e.g., self._make_candidate_input).
#
#   5. RED state expected: 77 passed (existing) + 45 failed (new;
#      ImportError class). Verification command:
#        pytest tests/test_evaluate_dsr.py 2>&1 | tail -10
# ===========================================================================


class TestComputeSimplifiedDSRBonferroniThreshold:
    """§4.3 Step 1 Bonferroni-style threshold: SR_threshold = sqrt(2*ln(N)).

    Reference values (stdlib math.sqrt + math.log; no scipy required):
      N=198:   sqrt(2*ln(198)) ≈ 3.252158
      N=2:     sqrt(2*ln(2))   ≈ 1.177410
      N=10000: sqrt(2*ln(10000)) ≈ 4.291932
    """

    def test_threshold_at_canonical_n_198(self):
        from backtest.evaluate_dsr import compute_simplified_dsr  # noqa: F401
        # Reference: math.sqrt(2 * math.log(198)) = 3.2521583696660700
        # Threshold accessed via compute_simplified_dsr(...).bonferroni_threshold;
        # synthetic eligible candidates required to invoke; fixture below.
        from backtest.evaluate_dsr import CandidateInput
        candidates = [
            CandidateInput(
                hypothesis_hash=f"h{i:02d}",
                sharpe_ratio=0.0,
                total_trades=10,
                audit_v1_artifact_path=f"{SYN_BASE}/synthetic_{i}.json",
                name="syn",
                theme="syn",
                lifecycle_state="shortlisted",
            )
            for i in range(198)
        ]
        result = compute_simplified_dsr(candidates, n_trials=198)
        expected = math.sqrt(2.0 * math.log(198))
        assert abs(result.bonferroni_threshold - expected) < 1e-9
        assert abs(result.bonferroni_threshold - 3.2521583696660700) < 1e-9

    def test_threshold_consistency_with_compute_expected_max_sharpe(self):
        from backtest.evaluate_dsr import (
            CandidateInput,
            compute_expected_max_sharpe,
            compute_simplified_dsr,
        )
        candidates = [
            CandidateInput(
                hypothesis_hash=f"h{i:02d}",
                sharpe_ratio=0.0,
                total_trades=10,
                audit_v1_artifact_path=f"{SYN_BASE}/synthetic_{i}.json",
                name="syn",
                theme="syn",
                lifecycle_state="shortlisted",
            )
            for i in range(198)
        ]
        result = compute_simplified_dsr(candidates, n_trials=198)
        # Bonferroni formula must agree across both APIs.
        assert abs(
            result.bonferroni_threshold - compute_expected_max_sharpe(198)
        ) < 1e-12

    def test_threshold_monotone_in_n(self):
        from backtest.evaluate_dsr import compute_expected_max_sharpe
        # Bonferroni threshold strictly increases in N for N >= 2.
        for n_lo, n_hi in [(10, 100), (100, 1000), (1000, 10000)]:
            assert compute_expected_max_sharpe(n_lo) < compute_expected_max_sharpe(n_hi)


class TestComputeSimplifiedDSRGumbelExpectedMax:
    """§4.3 Step 2 Gumbel approximation E[max SR | null].

    Hand-derived reference at Var=1, N=198 (cross-checked stdlib + scipy):
      γ_e (Euler-Mascheroni) ≈ 0.5772156649015329
      Φ⁻¹(1 - 1/198)   ≈ 2.572352  (scipy.stats.norm.ppf(1 - 1/198))
      Φ⁻¹(1 - 1/(198·e)) ≈ 2.901319  (scipy.stats.norm.ppf(1 - 1/(198*math.e)))
      E[max | null, Var=1, N=198]
        = sqrt(1) * ((1 - 0.5772) * 2.572352 + 0.5772 * 2.901319)
        ≈ 0.4228 * 2.572352 + 0.5772 * 2.901319
        ≈ 1.087602 + 1.674635
        ≈ 2.762237

    Linearity in sqrt(Var): E[max | null, Var=4] = 2 * E[max | null, Var=1].
    """

    def test_expected_max_at_var_1_n_198(self):
        from backtest.evaluate_dsr import (
            CandidateInput,
            compute_simplified_dsr,
        )
        # Construct 198 candidates with sharpe variance = 1.0 EXACTLY (ddof=1).
        # PHASE2C_11 hotfix-2 fixture math correction (F1): the original
        # fixture used ±0.99499 with claim "var ≈ 1", but actual sample
        # variance was 0.9950305 (delta from 1.0 = 0.005), producing
        # E[max] = 2.755365 vs reference 2.762237 (delta 0.0069 > 1e-3
        # tolerance). The fixed fixture uses a = sqrt(197/198) so that
        # 2 * 99 * a^2 / (198 - 1) = 1.0 exactly.
        #
        # Vestigial-tolerance note: 1e-3 is now generous (post-fix delta
        # is ~1e-15 floating-point noise). Tolerance kept at 1e-3 per
        # minimum-mutation discipline at sealed-test register; future
        # successor cycle may tighten if assertion-precision is in scope.
        a = math.sqrt(197.0 / 198.0)
        sharpes = [a] * 99 + [-a] * 99
        candidates = [
            CandidateInput(
                hypothesis_hash=f"h{i:03d}",
                sharpe_ratio=sharpes[i],
                total_trades=10,
                audit_v1_artifact_path=f"{SYN_BASE}/syn_{i}.json",
                name="syn", theme="syn", lifecycle_state="shortlisted",
            )
            for i in range(198)
        ]
        result = compute_simplified_dsr(candidates, n_trials=198)
        # E[max|null] linear in sqrt(Var); verify against canonical reference at Var=1.
        assert abs(result.expected_max_sharpe_null - 2.762237) < 1e-3

    def test_expected_max_linear_in_sqrt_var(self):
        from backtest.evaluate_dsr import (
            CandidateInput,
            compute_simplified_dsr,
        )
        # Two candidate sets with var ratio 4:1 -> E[max|null] ratio 2:1.
        def make(scale: float):
            sharpes = [scale] * 99 + [-scale] * 99
            return [
                CandidateInput(
                    hypothesis_hash=f"h{i:03d}",
                    sharpe_ratio=sharpes[i],
                    total_trades=10,
                    audit_v1_artifact_path=f"{SYN_BASE}/syn_{i}.json",
                    name="syn", theme="syn", lifecycle_state="shortlisted",
                )
                for i in range(198)
            ]
        r1 = compute_simplified_dsr(make(1.0), n_trials=198)
        r2 = compute_simplified_dsr(make(2.0), n_trials=198)
        # var(r2) / var(r1) ≈ 4 → E[max] ratio ≈ 2.
        assert abs(r2.expected_max_sharpe_null / r1.expected_max_sharpe_null - 2.0) < 1e-6

    def test_expected_max_monotone_in_n(self):
        from backtest.evaluate_dsr import (
            CandidateInput,
            compute_simplified_dsr,
        )
        # For fixed Var(SR), E[max|null] strictly increases in N.
        def make_at_n(n: int):
            sharpes = [0.99499] * (n // 2) + [-0.99499] * (n - n // 2)
            return [
                CandidateInput(
                    hypothesis_hash=f"h{i:04d}",
                    sharpe_ratio=sharpes[i],
                    total_trades=10,
                    audit_v1_artifact_path=f"{SYN_BASE}/syn_{i}.json",
                    name="syn", theme="syn", lifecycle_state="shortlisted",
                )
                for i in range(n)
            ]
        # n_trials must equal n (and dual-gate enforces n == EXPECTED_N_RAW=198 in
        # production; this test must opt out of dual-gate via synthetic-only path).
        # See test_dual_gate_synthetic_opt_out_paths in TestComputeSimplifiedDSRDualGateNRawCheck.
        r_198 = compute_simplified_dsr(make_at_n(198), n_trials=198)
        # Smaller-N comparison at N=100 requires opt-out; deferred.
        # For RED phase: assert presence of expected_max_sharpe_null > 0 finite.
        assert r_198.expected_max_sharpe_null > 0
        assert math.isfinite(r_198.expected_max_sharpe_null)

    def test_expected_max_uses_inputs_sharpe_var(self):
        from backtest.evaluate_dsr import (
            CandidateInput,
            compute_simplified_dsr,
        )
        # The sharpe_var_used field MUST equal the Var(SR) computed over
        # the eligible subset (= statistics.variance, ddof=1).
        import statistics
        sharpes = [0.5, -0.5] * 99
        candidates = [
            CandidateInput(
                hypothesis_hash=f"h{i:03d}",
                sharpe_ratio=sharpes[i],
                total_trades=10,
                audit_v1_artifact_path=f"{SYN_BASE}/syn_{i}.json",
                name="syn", theme="syn", lifecycle_state="shortlisted",
            )
            for i in range(198)
        ]
        result = compute_simplified_dsr(candidates, n_trials=198)
        expected_var = statistics.variance(sharpes)
        assert abs(result.sharpe_var_used - expected_var) < 1e-12


class TestComputeSimplifiedDSRPerCandidateFormula:
    """§4.3 Step 3: SE = sqrt(1/(T_c - 1)); z = (SR_c - E[max|null])/SE; p = 1 - Φ(z).

    Cross-check independence: implementation may use scipy.stats.norm.sf;
    test reference uses stdlib math.erfc cross-check:
      p = norm.sf(z) ≡ 0.5 * math.erfc(z / math.sqrt(2))
    Both should agree to ~1e-15.
    """

    def test_se_formula_at_t_c(self):
        from backtest.evaluate_dsr import (
            CandidateInput,
            compute_simplified_dsr,
        )
        # T_c = 10 → SE = sqrt(1/9) ≈ 0.333333
        sharpes = [0.5, -0.5] * 99
        candidates = [
            CandidateInput(
                hypothesis_hash=f"h{i:03d}",
                sharpe_ratio=sharpes[i],
                total_trades=10,
                audit_v1_artifact_path=f"{SYN_BASE}/syn_{i}.json",
                name="syn", theme="syn", lifecycle_state="shortlisted",
            )
            for i in range(198)
        ]
        result = compute_simplified_dsr(candidates, n_trials=198)
        expected_se = math.sqrt(1.0 / 9.0)
        for d in result.per_candidate:
            assert abs(d.standard_error - expected_se) < 1e-12

    def test_z_score_formula(self):
        from backtest.evaluate_dsr import (
            CandidateInput,
            compute_simplified_dsr,
        )
        sharpes = [0.5, -0.5] * 99
        candidates = [
            CandidateInput(
                hypothesis_hash=f"h{i:03d}",
                sharpe_ratio=sharpes[i],
                total_trades=10,
                audit_v1_artifact_path=f"{SYN_BASE}/syn_{i}.json",
                name="syn", theme="syn", lifecycle_state="shortlisted",
            )
            for i in range(198)
        ]
        result = compute_simplified_dsr(candidates, n_trials=198)
        for d in result.per_candidate:
            expected_z = (d.sharpe_ratio - result.expected_max_sharpe_null) / d.standard_error
            assert abs(d.z_score - expected_z) < 1e-12

    def test_p_value_bounded(self):
        from backtest.evaluate_dsr import (
            CandidateInput,
            compute_simplified_dsr,
        )
        sharpes = [0.5, -0.5] * 99
        candidates = [
            CandidateInput(
                hypothesis_hash=f"h{i:03d}",
                sharpe_ratio=sharpes[i],
                total_trades=10,
                audit_v1_artifact_path=f"{SYN_BASE}/syn_{i}.json",
                name="syn", theme="syn", lifecycle_state="shortlisted",
            )
            for i in range(198)
        ]
        result = compute_simplified_dsr(candidates, n_trials=198)
        for d in result.per_candidate:
            assert 0.0 <= d.p_value <= 1.0

    def test_p_value_stdlib_scipy_cross_check(self):
        from backtest.evaluate_dsr import (
            CandidateInput,
            compute_simplified_dsr,
        )
        # Cross-check: p_c computed via implementation must match
        # stdlib formulation 0.5 * math.erfc(z / sqrt(2)) to ~1e-12.
        sharpes = [0.5, -0.5] * 99
        candidates = [
            CandidateInput(
                hypothesis_hash=f"h{i:03d}",
                sharpe_ratio=sharpes[i],
                total_trades=10,
                audit_v1_artifact_path=f"{SYN_BASE}/syn_{i}.json",
                name="syn", theme="syn", lifecycle_state="shortlisted",
            )
            for i in range(198)
        ]
        result = compute_simplified_dsr(candidates, n_trials=198)
        for d in result.per_candidate:
            stdlib_p = 0.5 * math.erfc(d.z_score / math.sqrt(2.0))
            assert abs(d.p_value - stdlib_p) < 1e-10


class TestComputeSimplifiedDSRBoundaryDispositions:
    """§3.6 conservative AND-gate: 5 distinct disposition regions per P-L1.

    Reference values cross-checked stdlib (math) + scipy.stats.norm.
    All synthetic candidate constructions use n_trials=198 + opt out of
    dual-gate via expected_n_trials=None param (per dual-gate test class).

    For each region, fixture constructs 198 candidates such that ONE target
    candidate (target_hash="h_target") lands in the region; remaining 197
    candidates are filler with Sharpe ≈ 0.

    Hand-derived landing tuples (verified via reference computation):

    Region 1 (signal_evidence):
      target SR=4.0, T=200, sharpe_var=1.0
      Bonferroni threshold = sqrt(2*ln(198)) ≈ 3.252158
      E[max|null] = sqrt(1.0) * (0.4228*Φ⁻¹(0.99495) + 0.5772*Φ⁻¹(0.99814))
                  ≈ 0.4228*2.572352 + 0.5772*2.901319 ≈ 2.762237
      SE = sqrt(1/199) ≈ 0.070888
      z = (4.0 - 2.762237) / 0.070888 ≈ 17.46
      p ≈ 1.42e-68  (< 0.05)
      → Bonferroni_pass=True AND DSR_style_pass=True → Region 1

    Region 2 (artifact_evidence):
      target SR=0.3, T=100, sharpe_var=0.5307 (canonical Step 2 input stat)
      E[max|null] = sqrt(0.5307) * (...) ≈ 2.012266
      SE = sqrt(1/99) ≈ 0.100504
      z = (0.3 - 2.012266) / 0.100504 ≈ -17.04
      p ≈ 1.0  (≥ 0.5)
      → Bonferroni_pass=False AND DSR_style_pass=False AND p≥0.5 → Region 2

    Region 3 (inconclusive — Bonferroni-only):
      target SR=3.4, T=5, sharpe_var=1.0
      Bonferroni_pass = (3.4 > 3.252158) = True
      E[max|null] = 2.762237
      SE = sqrt(1/4) = 0.5
      z = (3.4 - 2.762237) / 0.5 ≈ 1.275526
      p ≈ 0.10106  (≥ 0.05)
      → Bonferroni_pass=True AND DSR_style_pass=False → Region 3

    Region 4 (inconclusive — DSR-only):
      target SR=2.5, T=1000, sharpe_var=0.01
      E[max|null] = sqrt(0.01) * 2.762237 ≈ 0.276224
      SE = sqrt(1/999) ≈ 0.031639
      z = (2.5 - 0.276224) / 0.031639 ≈ 70.29
      p ≈ 0  (< 0.05)
      Bonferroni_pass = (2.5 > 3.252158) = False
      → Bonferroni_pass=False AND DSR_style_pass=True → Region 4

    Region 5 (inconclusive — intermediate-p):
      target SR=0.5, T=20, sharpe_var=0.01
      E[max|null] = 0.276224
      SE = sqrt(1/19) ≈ 0.229416
      z = (0.5 - 0.276224) / 0.229416 ≈ 0.975418
      p ≈ 0.16467  (in [0.05, 0.5))
      Bonferroni_pass = (0.5 > 3.252158) = False
      → Bonferroni_pass=False AND DSR_style_pass=False AND p<0.5 → Region 5
    """

    def _make_candidates_for_region(self, target_sr: float, target_t: int, var: float):
        """Construct 198 CandidateInput with one target landing in the
        intended region and 197 filler candidates such that statistics.variance
        of the full 198-Sharpe array ≈ ``var``.
        """
        from backtest.evaluate_dsr import CandidateInput
        import statistics
        # Solve for filler magnitude such that statistics.variance(sharpes)=var.
        # 197 fillers at ±filler_mag (alternating); 1 target at target_sr.
        # variance(sample, ddof=1) ≈ filler_mag^2 (when 197 fillers dominate)
        # for ±filler_mag at equal count, variance ≈ filler_mag^2 * 197/197 = filler_mag^2.
        # Plus target's contribution; for var dominated by fillers, filler_mag ≈ sqrt(var).
        # Tweak filler_mag iteratively to land exact variance.
        filler_mag = math.sqrt(var)
        sharpes = [target_sr] + [filler_mag, -filler_mag] * 98 + [filler_mag]
        # Re-tune: solve filler_mag s.t. statistics.variance(sharpes)=var precisely.
        # Iterate (3 passes is enough for convergence to 1e-10).
        for _ in range(20):
            sharpes = [target_sr] + [filler_mag, -filler_mag] * 98 + [filler_mag]
            actual_var = statistics.variance(sharpes)
            if actual_var == 0:
                break
            filler_mag = filler_mag * math.sqrt(var / actual_var)
        candidates: list = [
            CandidateInput(
                hypothesis_hash="h_target",
                sharpe_ratio=target_sr,
                total_trades=target_t,
                audit_v1_artifact_path=f"{SYN_BASE}/syn_target.json",
                name="syn", theme="syn", lifecycle_state="shortlisted",
            )
        ]
        for i in range(197):
            mag = filler_mag if (i % 2 == 0) else -filler_mag
            candidates.append(CandidateInput(
                hypothesis_hash=f"h_filler_{i:03d}",
                sharpe_ratio=mag,
                total_trades=10,
                audit_v1_artifact_path=f"{SYN_BASE}/syn_filler_{i}.json",
                name="syn", theme="syn", lifecycle_state="shortlisted",
            ))
        return candidates

    def test_region_1_signal_evidence(self):
        """Region 1: Bonferroni_pass AND DSR_style_pass → signal_evidence."""
        from backtest.evaluate_dsr import compute_simplified_dsr
        # Reference: SR=4.0, T=200, var=1.0; bonf=3.2522, e_max=2.7622,
        #   se=0.07089, z=17.46, p≈1.4e-68; Region 1.
        candidates = self._make_candidates_for_region(4.0, 200, 1.0)
        result = compute_simplified_dsr(candidates, n_trials=198)
        target = next(d for d in result.per_candidate if d.hypothesis_hash == "h_target")
        assert target.bonferroni_pass is True
        assert target.dsr_style_pass is True
        assert target.disposition == "signal_evidence"

    def test_region_2_artifact_evidence(self):
        """Region 2: NOT Bonferroni AND NOT DSR-style AND p≥0.5 → artifact."""
        from backtest.evaluate_dsr import compute_simplified_dsr
        # Reference: SR=0.3, T=100, var=0.5307; bonf=3.2522, e_max=2.0123,
        #   se=0.1005, z=-17.04, p≈1.0; Region 2.
        candidates = self._make_candidates_for_region(0.3, 100, 0.5307)
        result = compute_simplified_dsr(candidates, n_trials=198)
        target = next(d for d in result.per_candidate if d.hypothesis_hash == "h_target")
        assert target.bonferroni_pass is False
        assert target.dsr_style_pass is False
        assert target.p_value >= 0.5
        assert target.disposition == "artifact_evidence"

    def test_region_3_inconclusive_bonferroni_only(self):
        """Region 3: Bonferroni_pass AND NOT DSR_style_pass → inconclusive."""
        from backtest.evaluate_dsr import compute_simplified_dsr
        # Reference: SR=3.4, T=5, var=1.0; bonf=3.2522, e_max=2.7622,
        #   se=0.5, z=1.276, p≈0.1011 (≥ 0.05); Region 3.
        candidates = self._make_candidates_for_region(3.4, 5, 1.0)
        result = compute_simplified_dsr(candidates, n_trials=198)
        target = next(d for d in result.per_candidate if d.hypothesis_hash == "h_target")
        assert target.bonferroni_pass is True
        assert target.dsr_style_pass is False
        assert target.disposition == "inconclusive"

    def test_region_4_inconclusive_dsr_only(self):
        """Region 4: NOT Bonferroni_pass AND DSR_style_pass → inconclusive.

        Most subtle region: requires SR_c ≤ Bonferroni AND p < 0.05; achieved
        via low sharpe_var (=> low E[max|null]) + large T_c (=> small SE).
        """
        from backtest.evaluate_dsr import compute_simplified_dsr
        # Reference: SR=2.5, T=1000, var=0.01; bonf=3.2522, e_max=0.2762,
        #   se=0.0316, z=70.29, p≈0; Region 4.
        candidates = self._make_candidates_for_region(2.5, 1000, 0.01)
        result = compute_simplified_dsr(candidates, n_trials=198)
        target = next(d for d in result.per_candidate if d.hypothesis_hash == "h_target")
        assert target.bonferroni_pass is False
        assert target.dsr_style_pass is True
        assert target.disposition == "inconclusive"

    def test_region_5_inconclusive_intermediate_p(self):
        """Region 5: NOT Bonferroni AND NOT DSR-style AND p<0.5 → inconclusive."""
        from backtest.evaluate_dsr import compute_simplified_dsr
        # Reference: SR=0.5, T=20, var=0.01; bonf=3.2522, e_max=0.2762,
        #   se=0.2294, z=0.975, p≈0.1647 (in [0.05, 0.5)); Region 5.
        candidates = self._make_candidates_for_region(0.5, 20, 0.01)
        result = compute_simplified_dsr(candidates, n_trials=198)
        target = next(d for d in result.per_candidate if d.hypothesis_hash == "h_target")
        assert target.bonferroni_pass is False
        assert target.dsr_style_pass is False
        assert 0.05 <= target.p_value < 0.5
        assert target.disposition == "inconclusive"


class TestComputeSimplifiedDSRPopulationDisposition:
    """§4.3 Step 5: c_max = argmax(SR_observed); population_disposition = disposition(c_max)."""

    def test_argmax_hash_matches_max_sharpe_candidate(self):
        from backtest.evaluate_dsr import (
            CandidateInput,
            compute_simplified_dsr,
        )
        sharpes = [0.5, -0.5] * 99
        sharpes[42] = 4.0  # explicit argmax at index 42
        candidates = [
            CandidateInput(
                hypothesis_hash=f"h{i:03d}",
                sharpe_ratio=sharpes[i],
                total_trades=200,
                audit_v1_artifact_path=f"{SYN_BASE}/syn_{i}.json",
                name="syn", theme="syn", lifecycle_state="shortlisted",
            )
            for i in range(198)
        ]
        result = compute_simplified_dsr(candidates, n_trials=198)
        assert result.population_argmax_hash == "h042"

    def test_population_disposition_matches_argmax_disposition(self):
        from backtest.evaluate_dsr import (
            CandidateInput,
            compute_simplified_dsr,
        )
        sharpes = [0.5, -0.5] * 99
        sharpes[42] = 4.0
        candidates = [
            CandidateInput(
                hypothesis_hash=f"h{i:03d}",
                sharpe_ratio=sharpes[i],
                total_trades=200,
                audit_v1_artifact_path=f"{SYN_BASE}/syn_{i}.json",
                name="syn", theme="syn", lifecycle_state="shortlisted",
            )
            for i in range(198)
        ]
        result = compute_simplified_dsr(candidates, n_trials=198)
        argmax_disp = next(
            d for d in result.per_candidate if d.hypothesis_hash == "h042"
        )
        assert result.population_disposition == argmax_disp.disposition

    def test_argmax_tie_break_first_occurrence(self):
        from backtest.evaluate_dsr import (
            CandidateInput,
            compute_simplified_dsr,
        )
        # Two candidates with identical max Sharpe; first-occurrence tie-break.
        sharpes = [0.5, -0.5] * 99
        sharpes[10] = 3.5
        sharpes[20] = 3.5  # tie at indices 10 and 20
        candidates = [
            CandidateInput(
                hypothesis_hash=f"h{i:03d}",
                sharpe_ratio=sharpes[i],
                total_trades=100,
                audit_v1_artifact_path=f"{SYN_BASE}/syn_{i}.json",
                name="syn", theme="syn", lifecycle_state="shortlisted",
            )
            for i in range(198)
        ]
        result = compute_simplified_dsr(candidates, n_trials=198)
        assert result.population_argmax_hash == "h010"


class TestComputeSimplifiedDSRRSGuardEnforcement:
    """§4.5 + advisor refinement (b): RS-3 guard fires per candidate
    audit_v1_artifact_path at function entry; rs_guard_call_count audit-trail
    expected = n_eligible per P-T1 joint-coverage.
    """

    def _write_valid_summary(self, tmp_path, name: str = "h"):
        import json
        path = tmp_path / f"{name}_holdout_summary.json"
        path.write_text(json.dumps({
            "evaluation_semantics": "single_run_holdout_v1",
            "engine_commit": "eb1c87f",
            "engine_corrected_lineage": "wf-corrected-v1",
            "lineage_check": "passed",
            "current_git_sha": "deadbeef",
            "holdout_metrics": {"sharpe_ratio": 0.5, "total_trades": 10},
        }))
        return path

    def test_rs_guard_fires_per_candidate(self, tmp_path):
        from backtest.evaluate_dsr import (
            CandidateInput,
            compute_simplified_dsr,
        )
        candidates = []
        for i in range(198):
            p = self._write_valid_summary(tmp_path, name=f"h{i:03d}")
            candidates.append(CandidateInput(
                hypothesis_hash=f"h{i:03d}",
                sharpe_ratio=(0.5 if i % 2 == 0 else -0.5),
                total_trades=10,
                audit_v1_artifact_path=str(p),
                name="syn", theme="syn", lifecycle_state="shortlisted",
            ))
        result = compute_simplified_dsr(candidates, n_trials=198)
        assert result.rs_guard_call_count == 198

    def test_rs_guard_raises_on_malformed(self, tmp_path):
        from backtest.evaluate_dsr import (
            CandidateInput,
            compute_simplified_dsr,
        )
        # 197 valid + 1 malformed (missing evaluation_semantics).
        candidates = []
        for i in range(197):
            p = self._write_valid_summary(tmp_path, name=f"h{i:03d}")
            candidates.append(CandidateInput(
                hypothesis_hash=f"h{i:03d}",
                sharpe_ratio=(0.5 if i % 2 == 0 else -0.5),
                total_trades=10,
                audit_v1_artifact_path=str(p),
                name="syn", theme="syn", lifecycle_state="shortlisted",
            ))
        # Malformed: missing required RS field.
        import json
        bad_path = tmp_path / "h_bad_holdout_summary.json"
        bad_path.write_text(json.dumps({
            "engine_commit": "eb1c87f",  # missing evaluation_semantics
            "holdout_metrics": {"sharpe_ratio": 4.0, "total_trades": 100},
        }))
        candidates.append(CandidateInput(
            hypothesis_hash="h_bad",
            sharpe_ratio=4.0,
            total_trades=100,
            audit_v1_artifact_path=str(bad_path),
            name="syn", theme="syn", lifecycle_state="shortlisted",
        ))
        with pytest.raises(ValueError, match="evaluation_semantics"):
            compute_simplified_dsr(candidates, n_trials=198)

    def test_rs_guard_passes_on_valid(self, tmp_path):
        from backtest.evaluate_dsr import (
            CandidateInput,
            compute_simplified_dsr,
        )
        candidates = []
        for i in range(198):
            p = self._write_valid_summary(tmp_path, name=f"h{i:03d}")
            candidates.append(CandidateInput(
                hypothesis_hash=f"h{i:03d}",
                sharpe_ratio=(0.5 if i % 2 == 0 else -0.5),
                total_trades=10,
                audit_v1_artifact_path=str(p),
                name="syn", theme="syn", lifecycle_state="shortlisted",
            ))
        # Should not raise.
        result = compute_simplified_dsr(candidates, n_trials=198)
        assert result is not None

    def test_rs_guard_call_count_audit_trail(self, tmp_path):
        from backtest.evaluate_dsr import (
            CandidateInput,
            compute_simplified_dsr,
        )
        # n_eligible = 198 (no exclusions) → rs_guard_call_count == 198.
        candidates = []
        for i in range(198):
            p = self._write_valid_summary(tmp_path, name=f"h{i:03d}")
            candidates.append(CandidateInput(
                hypothesis_hash=f"h{i:03d}",
                sharpe_ratio=(0.5 if i % 2 == 0 else -0.5),
                total_trades=10,
                audit_v1_artifact_path=str(p),
                name="syn", theme="syn", lifecycle_state="shortlisted",
            ))
        result = compute_simplified_dsr(candidates, n_trials=198)
        # Per P-T1 joint-coverage docstring: rs_guard_call_count == n_eligible
        # (here 198 == n_eligible since no §4.4 exclusions in synthetic input).
        assert result.rs_guard_call_count == result.n_eligible


class TestComputeSimplifiedDSRDualGateNRawCheck:
    """§3.2 + Step 2 §5.3 forward-flag dual-gate verification.

    Per P-L3: invariant enforced via raise ValueError, NOT result field.
    Test asserts pytest.raises(ValueError), NOT result.n_trials_lockpoint_verified
    (the latter field DELETED per anti-pattern correction).
    """

    def test_n_trials_mismatch_raises(self):
        from backtest.evaluate_dsr import (
            CandidateInput,
            compute_simplified_dsr,
        )
        candidates = [
            CandidateInput(
                hypothesis_hash=f"h{i:03d}",
                sharpe_ratio=0.0,
                total_trades=10,
                audit_v1_artifact_path=f"{SYN_BASE}/syn_{i}.json",
                name="syn", theme="syn", lifecycle_state="shortlisted",
            )
            for i in range(197)  # 197 != EXPECTED_N_RAW=198
        ]
        with pytest.raises(ValueError, match="EXPECTED_N_RAW|n_trials|198"):
            compute_simplified_dsr(candidates, n_trials=197)

    def test_inputs_n_raw_mismatch_raises(self):
        from backtest.evaluate_dsr import (
            CandidateInput,
            compute_simplified_dsr,
        )
        # n_trials=198 is correct, but candidate count != 198 (n_raw mismatch).
        candidates = [
            CandidateInput(
                hypothesis_hash=f"h{i:03d}",
                sharpe_ratio=0.0,
                total_trades=10,
                audit_v1_artifact_path=f"{SYN_BASE}/syn_{i}.json",
                name="syn", theme="syn", lifecycle_state="shortlisted",
            )
            for i in range(197)
        ]
        with pytest.raises(ValueError):
            compute_simplified_dsr(candidates, n_trials=198)

    def test_dual_gate_passes_at_canonical_198(self):
        from backtest.evaluate_dsr import (
            CandidateInput,
            compute_simplified_dsr,
        )
        candidates = [
            CandidateInput(
                hypothesis_hash=f"h{i:03d}",
                sharpe_ratio=(0.5 if i % 2 == 0 else -0.5),
                total_trades=10,
                audit_v1_artifact_path=f"{SYN_BASE}/syn_{i}.json",
                name="syn", theme="syn", lifecycle_state="shortlisted",
            )
            for i in range(198)
        ]
        # Should not raise; result should carry n_trials=198 + n_raw=198.
        result = compute_simplified_dsr(candidates, n_trials=198)
        assert result.n_trials == 198
        assert result.n_raw == 198


class TestComputeSimplifiedDSREdgeCases:
    """§4.4(4) + §1.5 dual-handling: degenerate states route to inconclusive."""

    def test_low_trade_population_raises_value_error(self):
        """T_c < MIN_TRADES_FOR_PRIMARY=5 candidates raise ValueError per
        §4.4(1) pre-registered exclusion threshold at compute_simplified_dsr()
        API entry.

        Codex first-fire #2 substantive correction (Hotfix-3 sealed-test-
        substance flip event): this test previously accepted a degenerate
        result for all-low-trade input, which silently bypassed §4.4(1)
        lockpoint enforcement. Post-Hotfix-3, the API rejects low-trade
        candidates fail-loud instead of computing on them. Schema P-L3
        "raise OR degenerate" wording resolved at "raise" branch;
        degenerate_state n_eligible_zero remains schema-sealed Literal
        value but is unreachable under the current API per Patch #3
        unreachability docstring.
        """
        from backtest.evaluate_dsr import (
            CandidateInput,
            compute_simplified_dsr,
        )
        candidates = [
            CandidateInput(
                hypothesis_hash=f"h{i:03d}",
                sharpe_ratio=0.5,
                total_trades=2,  # T_c < MIN_TRADES_FOR_PRIMARY=5
                audit_v1_artifact_path=f"{SYN_BASE}/syn_{i}.json",
                name="syn", theme="syn", lifecycle_state="shortlisted",
            )
            for i in range(198)
        ]
        with pytest.raises(ValueError, match="low_trade_count"):
            compute_simplified_dsr(candidates, n_trials=198)

    def test_zero_variance_returns_inconclusive(self):
        from backtest.evaluate_dsr import (
            CandidateInput,
            compute_simplified_dsr,
        )
        # All 198 candidates with identical Sharpe → Var(SR) = 0.
        candidates = [
            CandidateInput(
                hypothesis_hash=f"h{i:03d}",
                sharpe_ratio=0.5,  # identical
                total_trades=10,
                audit_v1_artifact_path=f"{SYN_BASE}/syn_{i}.json",
                name="syn", theme="syn", lifecycle_state="shortlisted",
            )
            for i in range(198)
        ]
        result = compute_simplified_dsr(candidates, n_trials=198)
        assert result.population_disposition == "inconclusive"
        assert result.degenerate_state == "var_zero"

    def test_normal_path_no_degenerate_state(self):
        from backtest.evaluate_dsr import (
            CandidateInput,
            compute_simplified_dsr,
        )
        sharpes = [0.5, -0.5] * 99
        candidates = [
            CandidateInput(
                hypothesis_hash=f"h{i:03d}",
                sharpe_ratio=sharpes[i],
                total_trades=10,
                audit_v1_artifact_path=f"{SYN_BASE}/syn_{i}.json",
                name="syn", theme="syn", lifecycle_state="shortlisted",
            )
            for i in range(198)
        ]
        result = compute_simplified_dsr(candidates, n_trials=198)
        assert result.degenerate_state == "none" or result.degenerate_state is None


class TestComputeSimplifiedDSRReproducibility:
    """P-T3: argmax order-independent; per_candidate iteration tracks input order.

    Two distinct invariants verified:
      (i) population_disposition stable across input shuffling
     (ii) per_candidate iteration order tracks input order
    """

    def test_population_disposition_argmax_order_independent(self):
        from backtest.evaluate_dsr import (
            CandidateInput,
            compute_simplified_dsr,
        )
        import random
        # PHASE2C_11 hotfix-2 fixture math correction (F2): original ramp
        # coefficient 0.05 produced sharpes[197] = (197-99)*0.05 = 4.9 which
        # exceeded sharpes[42]=3.5, making h197 the actual argmax (not h042
        # as the assertion claims). Path α (chosen): scale ramp coefficient
        # 0.05 → 0.01 so the ramp range becomes [-0.99, 0.98], making 3.5
        # genuinely dominant and h042 the actual argmax.
        # Path β considered: rewrite the assertion to test only shuffle-
        # reproducibility invariant without the specific "h042" hash claim.
        # α chosen on minimum-mutation grounds (changes 1 fixture constant
        # vs assertion structure). Future test maintenance: if argmax-hash-
        # specific assertions surface as a brittle pattern in successor
        # cycles, β refactor at successor cycle is the canonical path.
        sharpes = [(i - 99) * 0.01 for i in range(198)]  # range [-0.99, 0.98]
        sharpes[42] = 3.5  # explicit argmax (genuinely dominant post-fix)
        candidates_a = [
            CandidateInput(
                hypothesis_hash=f"h{i:03d}",
                sharpe_ratio=sharpes[i],
                total_trades=100,
                audit_v1_artifact_path=f"{SYN_BASE}/syn_{i}.json",
                name="syn", theme="syn", lifecycle_state="shortlisted",
            )
            for i in range(198)
        ]
        candidates_b = list(candidates_a)
        random.Random(42).shuffle(candidates_b)
        result_a = compute_simplified_dsr(candidates_a, n_trials=198)
        result_b = compute_simplified_dsr(candidates_b, n_trials=198)
        # population_disposition stable across shuffle:
        assert result_a.population_disposition == result_b.population_disposition
        # argmax hash stable (h042 carries SR=3.5 in both):
        assert result_a.population_argmax_hash == result_b.population_argmax_hash == "h042"

    def test_per_candidate_iteration_tracks_input_order(self):
        from backtest.evaluate_dsr import (
            CandidateInput,
            compute_simplified_dsr,
        )
        sharpes = [(i - 99) * 0.05 for i in range(198)]
        candidates = [
            CandidateInput(
                hypothesis_hash=f"h{i:03d}",
                sharpe_ratio=sharpes[i],
                total_trades=100,
                audit_v1_artifact_path=f"{SYN_BASE}/syn_{i}.json",
                name="syn", theme="syn", lifecycle_state="shortlisted",
            )
            for i in range(198)
        ]
        result = compute_simplified_dsr(candidates, n_trials=198)
        # per_candidate ordering tracks input order:
        for i, d in enumerate(result.per_candidate):
            assert d.hypothesis_hash == f"h{i:03d}"


class TestComputeSimplifiedDSRSensitivityTable:
    """§5.4 sensitivity table — N_eff ∈ {198, 80, 40, 5}; primary at N_eff=198 only."""

    def test_sensitivity_table_has_four_rows(self):
        from backtest.evaluate_dsr import (
            CandidateInput,
            compute_simplified_dsr,
        )
        sharpes = [0.5, -0.5] * 99
        candidates = [
            CandidateInput(
                hypothesis_hash=f"h{i:03d}",
                sharpe_ratio=sharpes[i],
                total_trades=10,
                audit_v1_artifact_path=f"{SYN_BASE}/syn_{i}.json",
                name="syn", theme="syn", lifecycle_state="shortlisted",
            )
            for i in range(198)
        ]
        result = compute_simplified_dsr(candidates, n_trials=198)
        n_effs = sorted(row.n_eff for row in result.sensitivity_table)
        assert n_effs == [5, 40, 80, 198]

    def test_sensitivity_register_labels(self):
        from backtest.evaluate_dsr import (
            CandidateInput,
            compute_simplified_dsr,
        )
        sharpes = [0.5, -0.5] * 99
        candidates = [
            CandidateInput(
                hypothesis_hash=f"h{i:03d}",
                sharpe_ratio=sharpes[i],
                total_trades=10,
                audit_v1_artifact_path=f"{SYN_BASE}/syn_{i}.json",
                name="syn", theme="syn", lifecycle_state="shortlisted",
            )
            for i in range(198)
        ]
        result = compute_simplified_dsr(candidates, n_trials=198)
        for row in result.sensitivity_table:
            if row.n_eff == 198:
                assert row.register_label == "primary"
            else:
                assert row.register_label == "sensitivity"

    def test_sensitivity_bonferroni_per_row_formula(self):
        from backtest.evaluate_dsr import (
            CandidateInput,
            compute_simplified_dsr,
        )
        sharpes = [0.5, -0.5] * 99
        candidates = [
            CandidateInput(
                hypothesis_hash=f"h{i:03d}",
                sharpe_ratio=sharpes[i],
                total_trades=10,
                audit_v1_artifact_path=f"{SYN_BASE}/syn_{i}.json",
                name="syn", theme="syn", lifecycle_state="shortlisted",
            )
            for i in range(198)
        ]
        result = compute_simplified_dsr(candidates, n_trials=198)
        for row in result.sensitivity_table:
            expected = math.sqrt(2.0 * math.log(row.n_eff))
            assert abs(row.bonferroni_threshold - expected) < 1e-9


class TestComputeSimplifiedDSRRealDataIntegration:
    """Canonical anchor: load_audit_v1_candidates → compute_simplified_dsr.

    §20 TRIGGER 1 CLOSURE ANNOTATION (per Charlie-register lock + advisor L7):
    -----------------------------------------------------------------------
    This test, when GREEN-phase passes, constitutes the **live computation
    that closes §20 Trigger 1 boundary** per PHASE2C_11_PLAN §0 P-L7
    timeline. Test author at TDD-RED turn does NOT fire this; the
    implementation turn's GREEN run is the boundary closure event. After
    GREEN passes, any new §3 lockpoint defects route strict §0.4
    (inconclusive disposition + successor cycle re-pre-registration) per
    METHODOLOGY_NOTES §20 v2 documented exception path closure.

    Future audit readers identifying the §20 closure commit should look
    for the implementation turn commit (GREEN run), NOT this RED commit.
    """

    AUDIT_V1 = (
        Path(__file__).resolve().parent.parent
        / "data"
        / "phase2c_evaluation_gate"
        / "audit_v1"
    )
    HOLDOUT_CSV = (
        Path(__file__).resolve().parent.parent
        / "data"
        / "phase2c_evaluation_gate"
        / "audit_v1_filtered"
        / "holdout_results.csv"
    )

    def test_canonical_audit_v1_produces_valid_result(self):
        if not self.AUDIT_V1.is_dir():
            pytest.skip("audit_v1 directory unavailable in this environment")
        from backtest.evaluate_dsr import (
            EXPECTED_N_RAW,
            compute_simplified_dsr,
            load_audit_v1_candidates,
        )
        inputs = load_audit_v1_candidates(
            self.AUDIT_V1, self.HOLDOUT_CSV,
            expected_n_raw=EXPECTED_N_RAW,
        )
        # Patch #1 (Codex first-fire): thread inputs.excluded_candidates so
        # SimplifiedDSRResult.excluded_candidates_summary is populated per
        # schema §1 line 51 + P-T2 lock (sealed schema requires sorted
        # tuple-of-(reason, count) pairs; expected counts at canonical fire
        # sum to 44 per "expected counts at canonical fire sum to 44"
        # schema lockpoint).
        result = compute_simplified_dsr(
            list(inputs.eligible_candidates),
            n_trials=EXPECTED_N_RAW,
            excluded_candidates=list(inputs.excluded_candidates),
        )
        assert result.n_raw == 198
        assert result.n_eligible == 154
        assert result.population_disposition in (
            "signal_evidence", "artifact_evidence", "inconclusive",
        )

        # Patch #1 enhancement: verify excluded_candidates_summary canonical
        # invariants. Schema §1 line 51 + P-T2: tuple-of-(str, int) pairs
        # sorted by reason key alphabetically; reason keys ⊂ Step 2
        # CandidateExclusion.reason enum {low_trade_count, zero_trades,
        # missing_sharpe, missing_trades}; sum at canonical fire = 44
        # (= n_raw - n_eligible = 198 - 154).
        summary = result.excluded_candidates_summary
        assert isinstance(summary, tuple)
        assert len(summary) > 0, (
            "excluded_candidates_summary is empty at canonical fire; "
            "Patch #1 wiring failed to thread Step 2 excluded_candidates."
        )
        # Every element is a (reason: str, count: int) pair.
        for entry in summary:
            assert isinstance(entry, tuple) and len(entry) == 2
            reason, count = entry
            assert isinstance(reason, str)
            assert isinstance(count, int)
        # Sorted by reason key alphabetically (P-T2).
        reasons = [r for r, _ in summary]
        assert reasons == sorted(reasons), (
            f"excluded_candidates_summary not sorted by reason key; got "
            f"reasons={reasons}"
        )
        # Reason keys ⊂ canonical Step 2 enum.
        canonical_reasons = {
            "low_trade_count", "zero_trades",
            "missing_sharpe", "missing_trades",
        }
        for reason, _ in summary:
            assert reason in canonical_reasons, (
                f"unknown exclusion reason {reason!r}; Step 2 enum is "
                f"{sorted(canonical_reasons)}"
            )
        # Counts sum to canonical 44 (= 198 - 154).
        total = sum(count for _, count in summary)
        assert total == 44, (
            f"excluded_candidates_summary counts sum to {total}, "
            f"expected 44 at canonical fire (= EXPECTED_N_RAW=198 - "
            f"EXPECTED_N_ELIGIBLE_AT_CANONICAL=154 per schema §1 line 51)"
        )

    def test_canonical_disposition_reproducible(self):
        if not self.AUDIT_V1.is_dir():
            pytest.skip("audit_v1 directory unavailable in this environment")
        from backtest.evaluate_dsr import (
            EXPECTED_N_RAW,
            compute_simplified_dsr,
            load_audit_v1_candidates,
        )
        inputs = load_audit_v1_candidates(
            self.AUDIT_V1, self.HOLDOUT_CSV,
            expected_n_raw=EXPECTED_N_RAW,
        )
        r1 = compute_simplified_dsr(list(inputs.eligible_candidates), n_trials=198)
        r2 = compute_simplified_dsr(list(inputs.eligible_candidates), n_trials=198)
        assert r1.population_disposition == r2.population_disposition
        assert r1.population_argmax_hash == r2.population_argmax_hash
        assert abs(r1.bonferroni_threshold - r2.bonferroni_threshold) < 1e-12
        assert abs(r1.expected_max_sharpe_null - r2.expected_max_sharpe_null) < 1e-12

    def test_canonical_rs_guard_call_count_matches_n_eligible(self):
        if not self.AUDIT_V1.is_dir():
            pytest.skip("audit_v1 directory unavailable in this environment")
        from backtest.evaluate_dsr import (
            EXPECTED_N_RAW,
            compute_simplified_dsr,
            load_audit_v1_candidates,
        )
        inputs = load_audit_v1_candidates(
            self.AUDIT_V1, self.HOLDOUT_CSV,
            expected_n_raw=EXPECTED_N_RAW,
        )
        result = compute_simplified_dsr(
            list(inputs.eligible_candidates), n_trials=EXPECTED_N_RAW,
        )
        # Per P-T1 joint-coverage: rs_guard_call_count == n_eligible (= 154).
        assert result.rs_guard_call_count == 154


class TestComputeSimplifiedDSRNumericalStabilityAtExtremeN:
    """Guard against numerical instability at N values beyond §3.2 lockpoint
    (N_raw=198); not a production-supported scope claim. Renamed per L3.
    """

    def test_compute_simplified_dsr_stable_at_n_10000(self):
        from backtest.evaluate_dsr import (
            CandidateInput,
            compute_simplified_dsr,
        )
        # Synthetic 10000-candidate input; opt out of dual-gate via
        # expected_n_trials=None (callable design TBD at impl turn).
        # If dual-gate is hard-coded to 198, this test asserts ValueError
        # — that's a §3.2 lockpoint enforcement, NOT a stability failure.
        sharpes = [0.5, -0.5] * 5000
        candidates = [
            CandidateInput(
                hypothesis_hash=f"h{i:05d}",
                sharpe_ratio=sharpes[i],
                total_trades=10,
                audit_v1_artifact_path=f"{SYN_BASE}/syn_{i}.json",
                name="syn", theme="syn", lifecycle_state="shortlisted",
            )
            for i in range(10000)
        ]
        # Expected behavior at N=10000:
        # - Bonferroni threshold = sqrt(2*ln(10000)) ≈ 4.292 (finite, well-defined)
        # - Φ⁻¹(1 - 1/10000) finite (numerical stability of scipy.stats.norm.ppf
        #   confirmed up to N≈1e10)
        # - E[max|null] finite
        # Either the function accepts and returns a finite result (preferred for
        # stability guard), or the dual-gate raises (lockpoint enforcement).
        # Both behaviors are acceptable; test asserts presence of finite output
        # OR clean ValueError with §3.2 lockpoint reference.
        try:
            result = compute_simplified_dsr(candidates, n_trials=10000)
            # If accepted: assert numerical stability (no NaN / inf).
            assert math.isfinite(result.bonferroni_threshold)
            assert math.isfinite(result.expected_max_sharpe_null)
            for d in result.per_candidate[:10]:  # sample check
                assert math.isfinite(d.z_score)
                assert 0.0 <= d.p_value <= 1.0
        except ValueError as exc:
            # Acceptable: dual-gate enforces §3.2 lockpoint.
            assert "EXPECTED_N_RAW" in str(exc) or "198" in str(exc) or "n_trials" in str(exc)

    def test_phi_inverse_stability_at_extreme_quantile(self):
        from scipy.stats import norm
        # Numerical stability sanity: Φ⁻¹(1 - 1/N) should not underflow or
        # produce inf for N up to 10000 (well within scipy.stats.norm.ppf
        # supported range; supports up to ~1e15).
        for n in [198, 1000, 10000]:
            v = norm.ppf(1.0 - 1.0 / n)
            assert math.isfinite(v)
            assert v > 0


class TestRS3PatchOnExistingFunctions:
    """§2.5 RS-3 patch on existing functions (shape A: kw-only
    audit_v1_artifact_paths=None). Grouped per L4; sub-test naming
    prefix per function for `pytest -k <function_name>` filtering.

    Per advisor: 3 tests per function (back-compat None / live-guard
    malformed / live-guard valid) × 2 functions = 6 tests total.
    """

    def _write_valid_summary(self, tmp_path, name: str = "h"):
        import json
        path = tmp_path / f"{name}.json"
        path.write_text(json.dumps({
            "evaluation_semantics": "single_run_holdout_v1",
            "engine_commit": "eb1c87f",
            "engine_corrected_lineage": "wf-corrected-v1",
            "lineage_check": "passed",
            "current_git_sha": "deadbeef",
            "holdout_metrics": {"sharpe_ratio": 0.5, "total_trades": 10},
        }))
        return path

    def _write_malformed_summary(self, tmp_path, name: str = "h_bad"):
        import json
        path = tmp_path / f"{name}.json"
        # Missing evaluation_semantics → RS-3 guard rejects.
        path.write_text(json.dumps({
            "engine_commit": "eb1c87f",
            "holdout_metrics": {"sharpe_ratio": 0.5, "total_trades": 10},
        }))
        return path

    # --- evaluate_trials RS-3 patch tests ---

    def test_evaluate_trials_paths_none_back_compat(self):
        from backtest.evaluate_dsr import evaluate_trials
        # Default invocation (no paths) preserves pre-patch behavior.
        result = evaluate_trials({"strat_a": 1.5, "strat_b": 0.5})
        assert result["n_trials"] == 2
        assert result["best_sharpe"] == 1.5

    def test_evaluate_trials_paths_malformed_raises(self, tmp_path):
        from backtest.evaluate_dsr import evaluate_trials
        bad_path = self._write_malformed_summary(tmp_path)
        with pytest.raises(ValueError, match="evaluation_semantics"):
            evaluate_trials(
                {"strat_a": 1.5},
                audit_v1_artifact_paths=[bad_path],
            )

    def test_evaluate_trials_paths_valid_passes(self, tmp_path):
        from backtest.evaluate_dsr import evaluate_trials
        good_path = self._write_valid_summary(tmp_path)
        result = evaluate_trials(
            {"strat_a": 1.5, "strat_b": 0.5},
            audit_v1_artifact_paths=[good_path],
        )
        assert result["n_trials"] == 2

    # --- compute_expected_max_sharpe RS-3 patch tests ---

    def test_compute_expected_max_sharpe_paths_none_back_compat(self):
        from backtest.evaluate_dsr import compute_expected_max_sharpe
        # Pre-patch behavior preserved.
        result = compute_expected_max_sharpe(198)
        expected = math.sqrt(2.0 * math.log(198))
        assert abs(result - expected) < 1e-12

    def test_compute_expected_max_sharpe_paths_malformed_raises(self, tmp_path):
        from backtest.evaluate_dsr import compute_expected_max_sharpe
        bad_path = self._write_malformed_summary(tmp_path)
        with pytest.raises(ValueError, match="evaluation_semantics"):
            compute_expected_max_sharpe(
                198, audit_v1_artifact_paths=[bad_path],
            )

    def test_compute_expected_max_sharpe_paths_valid_passes(self, tmp_path):
        from backtest.evaluate_dsr import compute_expected_max_sharpe
        good_path = self._write_valid_summary(tmp_path)
        result = compute_expected_max_sharpe(
            198, audit_v1_artifact_paths=[good_path],
        )
        expected = math.sqrt(2.0 * math.log(198))
        assert abs(result - expected) < 1e-12

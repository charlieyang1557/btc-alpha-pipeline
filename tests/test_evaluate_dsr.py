"""Tests for backtest/evaluate_dsr.py.

Verifies:
- Expected maximum Sharpe threshold computation
- Evaluation logic (survive/not survive) across edge cases
- Registry query integration
- Empty query produces clean output
"""

from __future__ import annotations

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

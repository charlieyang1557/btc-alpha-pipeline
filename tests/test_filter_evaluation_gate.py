"""Tests for scripts/filter_evaluation_gate.py (PHASE2C_7.1 §5 / Step 3).

The filter script reads a primary evaluation_gate run's per-candidate
artifacts and produces a derived analytical artifact set under a sibling
namespace (e.g., audit_2024_v1 -> audit_2024_v1_filtered) by applying
the trade-count filter ``holdout_metrics.total_trades >= 20``.

Per §5.1 / §5.3:
- Per-candidate JSONs in the filtered set are byte-identical to primary.
- Aggregate JSON is recomputed over the included subset.
- Lineage attestation is inherited by reference from primary (no new
  engine run, no new git resolution).
- Threshold pinned at MIN_TOTAL_TRADES = 20 module-level constant
  (§5.3 Rule 1: "implementation does not expose the threshold as a
  runtime parameter").
"""
from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backtest.wf_lineage import (  # noqa: E402
    ARTIFACT_SCHEMA_VERSION_PHASE2C_7_1,
    CORRECTED_WF_ENGINE_COMMIT,
    ENGINE_CORRECTED_LINEAGE_TAG,
    EVALUATION_SEMANTICS_TAG,
    check_evaluation_semantics_or_raise,
)

filter_module = importlib.import_module("scripts.filter_evaluation_gate")


# ---------------------------------------------------------------------------
# Stub fixtures
# ---------------------------------------------------------------------------


def _stub_per_candidate(
    hash_prefix: str,
    position: int,
    theme: str,
    name: str,
    wf_sharpe: float,
    *,
    lifecycle_state: str,
    holdout_passed: bool | None,
    total_trades: int | None,
) -> dict:
    """Build a stub per-candidate summary mirroring the producer's schema.

    Centralized so all tests speak the same fixture format. Carries the
    full PHASE2C_7.1 Q3(a) field set so the schema-validation tests
    don't need separate fixtures.
    """
    summary = {
        "source_batch_id": "stub-source",
        "run_id": "audit_2024_v1",
        "hypothesis_hash": hash_prefix.ljust(16, "0"),
        "position": position,
        "theme": theme,
        "name": name,
        "wf_test_period_sharpe": wf_sharpe,
        "lifecycle_state": lifecycle_state,
        "error_message": None,
        "wall_clock_seconds": 1.18,
        # PHASE2C_7.1 §7 lineage fields
        "evaluation_semantics": EVALUATION_SEMANTICS_TAG,
        "engine_commit": CORRECTED_WF_ENGINE_COMMIT,
        "engine_corrected_lineage": ENGINE_CORRECTED_LINEAGE_TAG,
        "lineage_check": "passed",
        "current_git_sha": "abcd1234567890",
        "artifact_schema_version": ARTIFACT_SCHEMA_VERSION_PHASE2C_7_1,
        "regime_key": "v2.validation",
        "regime_label": "validation_2024",
    }
    if holdout_passed is None:
        # holdout_error path
        summary["holdout_metrics"] = None
        summary["passing_criteria"] = None
        summary["gate_pass_per_criterion"] = None
        summary["holdout_passed"] = None
    else:
        summary["holdout_metrics"] = {
            "sharpe_ratio": 0.5 if holdout_passed else -0.4,
            "max_drawdown": 0.10 if holdout_passed else 0.30,
            "total_return": 0.05 if holdout_passed else -0.20,
            "total_trades": total_trades,
        }
        summary["passing_criteria"] = {
            "min_sharpe": -0.5,
            "max_drawdown": 0.25,
            "min_total_return": -0.15,
            "min_total_trades": 5,
        }
        summary["gate_pass_per_criterion"] = {
            "sharpe_passed": holdout_passed,
            "drawdown_passed": holdout_passed,
            "return_passed": holdout_passed,
            "trades_passed": holdout_passed,
        }
        summary["holdout_passed"] = holdout_passed
    return summary


def _stub_primary_run(tmp_path: Path) -> Path:
    """Materialize a 6-candidate primary run for filter testing.

    Coverage:
      - Above threshold + passed     (included, contributes to passed count)
      - Above threshold + failed     (included, contributes to failed count)
      - At threshold (=20) + passed  (included, boundary inclusive)
      - Below threshold + passed     (excluded by filter)
      - Below threshold + failed     (excluded by filter)
      - holdout_error (None trades)  (excluded by filter)

    Mix primary/audit-only via wf_test_period_sharpe so the partition
    breakdown recomputes meaningfully.
    """
    run_dir = tmp_path / "audit_2024_v1"
    run_dir.mkdir(parents=True)
    cands = [
        # (hash_prefix, position, theme, name, wf_sharpe, lifecycle, passed, trades)
        ("aaaa1111", 1, "volume_divergence", "above_thr_pass_primary", 2.5,
         "holdout_passed", True, 50),
        ("bbbb2222", 2, "momentum", "above_thr_fail_primary", 1.8,
         "holdout_failed", False, 100),
        ("cccc3333", 3, "calendar_effect", "at_thr_pass_audit", 0.3,
         "holdout_passed", True, 20),
        ("dddd4444", 4, "mean_reversion", "below_thr_pass_audit", 0.2,
         "holdout_passed", True, 19),
        ("eeee5555", 5, "volatility_regime", "below_thr_fail_audit", 0.1,
         "holdout_failed", False, 5),
        ("ffff6666", 6, "volume_divergence", "error_audit", 0.4,
         "holdout_error", None, None),
    ]
    summaries = []
    for hp, pos, theme, name, wfs, ls, passed, trades in cands:
        s = _stub_per_candidate(
            hp, pos, theme, name, wfs,
            lifecycle_state=ls, holdout_passed=passed, total_trades=trades,
        )
        cand_dir = run_dir / s["hypothesis_hash"]
        cand_dir.mkdir()
        (cand_dir / "holdout_summary.json").write_text(
            json.dumps(s, indent=2, sort_keys=True)
        )
        summaries.append(s)

    # Aggregate JSON (mirrors run_phase2c_evaluation_gate aggregate shape).
    primary_aggregate = {
        "run_id": "audit_2024_v1",
        "source_batch_id": "stub-source",
        "universe": "audit",
        "explicit_candidate_hashes": None,
        "run_started_utc": "2026-04-27T00:00:00Z",
        "run_finished_utc": "2026-04-27T00:05:00Z",
        "counts": {"total": 6, "holdout_passed": 3, "holdout_failed": 2,
                   "holdout_error": 1},
        "primary_universe_holdout_passed": 1,  # aaaa1111 passes wf>0.5 + holdout
        "primary_universe_total": 2,  # aaaa1111, bbbb2222
        "audit_only_holdout_passed": 2,  # cccc3333, dddd4444
        "audit_only_total": 4,  # cccc3333, dddd4444, eeee5555, ffff6666
        "by_theme": {
            "volume_divergence": {"total": 2, "holdout_passed": 1},
            "momentum": {"total": 1, "holdout_passed": 0},
            "calendar_effect": {"total": 1, "holdout_passed": 1},
            "mean_reversion": {"total": 1, "holdout_passed": 1},
            "volatility_regime": {"total": 1, "holdout_passed": 0},
        },
        "evaluation_semantics": EVALUATION_SEMANTICS_TAG,
        "engine_commit": CORRECTED_WF_ENGINE_COMMIT,
        "engine_corrected_lineage": ENGINE_CORRECTED_LINEAGE_TAG,
        "lineage_check": "passed",
        "current_git_sha": "abcd1234567890",
        "artifact_schema_version": ARTIFACT_SCHEMA_VERSION_PHASE2C_7_1,
        "regime_key": "v2.validation",
        "regime_label": "validation_2024",
    }
    (run_dir / "holdout_summary.json").write_text(
        json.dumps(primary_aggregate, indent=2, sort_keys=True)
    )

    # Aggregate CSV (minimal — script only reuses for row subsetting).
    csv_lines = [
        "hypothesis_hash,position,theme,name,wf_test_period_sharpe,"
        "lifecycle_state,holdout_passed,holdout_sharpe,holdout_max_drawdown,"
        "holdout_total_return,holdout_total_trades,wall_clock_seconds,"
        "error_message",
    ]
    for s in summaries:
        m = s.get("holdout_metrics") or {}
        row = [
            s["hypothesis_hash"], str(s["position"]), s["theme"], s["name"],
            f"{s['wf_test_period_sharpe']:.6f}",
            s["lifecycle_state"],
            ("" if s["holdout_passed"] is None
             else ("1" if s["holdout_passed"] else "0")),
            f"{m['sharpe_ratio']:.6f}" if m else "",
            f"{m['max_drawdown']:.6f}" if m else "",
            f"{m['total_return']:.6f}" if m else "",
            str(m["total_trades"]) if m else "",
            str(s["wall_clock_seconds"]),
            "",
        ]
        csv_lines.append(",".join(row))
    (run_dir / "holdout_results.csv").write_text("\n".join(csv_lines) + "\n")
    return run_dir


# ---------------------------------------------------------------------------
# Filter predicate (T1, T2)
# ---------------------------------------------------------------------------


class TestFilterPredicateSemantics:
    """``_passes_filter`` boundary + holdout_error semantics (§5.1 / §5.3)."""

    def test_threshold_pinned_at_module_constant(self):
        """§5.3 Rule 1: threshold lives in module-level constant, not CLI flag."""
        assert filter_module.MIN_TOTAL_TRADES == 20

    def test_above_threshold_included(self):
        s = _stub_per_candidate(
            "h", 1, "t", "n", 1.0,
            lifecycle_state="holdout_passed",
            holdout_passed=True, total_trades=50,
        )
        assert filter_module._passes_filter(s) is True

    def test_at_threshold_inclusive(self):
        """Inclusive >= boundary: total_trades == 20 passes."""
        s = _stub_per_candidate(
            "h", 1, "t", "n", 1.0,
            lifecycle_state="holdout_passed",
            holdout_passed=True, total_trades=20,
        )
        assert filter_module._passes_filter(s) is True

    def test_just_below_threshold_excluded(self):
        s = _stub_per_candidate(
            "h", 1, "t", "n", 1.0,
            lifecycle_state="holdout_passed",
            holdout_passed=True, total_trades=19,
        )
        assert filter_module._passes_filter(s) is False

    def test_holdout_error_excluded(self):
        """holdout_error candidates have None holdout_metrics; must not pass."""
        s = _stub_per_candidate(
            "h", 1, "t", "n", 1.0,
            lifecycle_state="holdout_error",
            holdout_passed=None, total_trades=None,
        )
        assert filter_module._passes_filter(s) is False

    def test_holdout_failed_above_threshold_included(self):
        """Filter is on trade count, NOT on pass/fail. Failed-but-traded passes filter."""
        s = _stub_per_candidate(
            "h", 1, "t", "n", 1.0,
            lifecycle_state="holdout_failed",
            holdout_passed=False, total_trades=100,
        )
        assert filter_module._passes_filter(s) is True


# ---------------------------------------------------------------------------
# Filter execution end-to-end (T3-T6)
# ---------------------------------------------------------------------------


class TestApplyFilter:
    """``apply_trade_count_filter`` end-to-end."""

    def test_filtered_set_size_matches_predicate(self, tmp_path):
        """T3: number of filtered per-candidate JSONs equals predicate-true count."""
        primary = _stub_primary_run(tmp_path)
        output = tmp_path / "audit_2024_v1_filtered"
        result = filter_module.apply_trade_count_filter(
            primary_dir=primary, output_dir=output,
        )
        # 3 of 6 stubs satisfy >= 20: aaaa(50), bbbb(100), cccc(20).
        assert result.included_count == 3
        assert result.excluded_count == 3
        # Output dir contains exactly 3 candidate dirs.
        cand_dirs = sorted(p for p in output.iterdir() if p.is_dir())
        assert len(cand_dirs) == 3
        assert {p.name for p in cand_dirs} == {
            "aaaa111100000000",
            "bbbb222200000000",
            "cccc333300000000",
        }

    def test_per_candidate_jsons_byte_identical_to_primary(self, tmp_path):
        """T4 / §5.1: filtered JSONs are byte-identical to primary."""
        primary = _stub_primary_run(tmp_path)
        output = tmp_path / "audit_2024_v1_filtered"
        filter_module.apply_trade_count_filter(
            primary_dir=primary, output_dir=output,
        )
        for cand_dir in output.iterdir():
            if not cand_dir.is_dir():
                continue
            filtered_json = cand_dir / "holdout_summary.json"
            primary_json = primary / cand_dir.name / "holdout_summary.json"
            assert filtered_json.read_bytes() == primary_json.read_bytes(), (
                f"byte-identity broken for {cand_dir.name}"
            )

    def test_aggregate_recomputed_over_filtered_subset(self, tmp_path):
        """T5: filtered aggregate counts derive from included subset only."""
        primary = _stub_primary_run(tmp_path)
        output = tmp_path / "audit_2024_v1_filtered"
        filter_module.apply_trade_count_filter(
            primary_dir=primary, output_dir=output,
        )
        agg = json.loads((output / "holdout_summary.json").read_text())
        assert agg["counts"]["total"] == 3
        # aaaa passed, bbbb failed, cccc passed.
        assert agg["counts"]["holdout_passed"] == 2
        assert agg["counts"]["holdout_failed"] == 1
        assert agg["counts"]["holdout_error"] == 0
        # Partition: aaaa(2.5)+bbbb(1.8) primary; cccc(0.3) audit-only.
        assert agg["primary_universe_total"] == 2
        assert agg["primary_universe_holdout_passed"] == 1  # aaaa
        assert agg["audit_only_total"] == 1
        assert agg["audit_only_holdout_passed"] == 1  # cccc

    def test_aggregate_by_theme_recomputed(self, tmp_path):
        """T5b: by_theme buckets reflect ONLY filtered candidates."""
        primary = _stub_primary_run(tmp_path)
        output = tmp_path / "audit_2024_v1_filtered"
        filter_module.apply_trade_count_filter(
            primary_dir=primary, output_dir=output,
        )
        agg = json.loads((output / "holdout_summary.json").read_text())
        # Filtered themes: aaaa volume_divergence(passed),
        # bbbb momentum(failed), cccc calendar_effect(passed).
        # Primary's mean_reversion + volatility_regime + (one of)
        # volume_divergence are all excluded.
        assert agg["by_theme"] == {
            "volume_divergence": {"total": 1, "holdout_passed": 1},
            "momentum": {"total": 1, "holdout_passed": 0},
            "calendar_effect": {"total": 1, "holdout_passed": 1},
        }

    def test_filtered_aggregate_validates_via_new_schema_branch(self, tmp_path):
        """F5: filtered aggregate passes the consumer guard's new branch.

        Lineage attestation inherits primary's fields verbatim per §5.1.
        The aggregate is a recomputation, not a re-attestation.
        """
        primary = _stub_primary_run(tmp_path)
        output = tmp_path / "audit_2024_v1_filtered"
        filter_module.apply_trade_count_filter(
            primary_dir=primary, output_dir=output,
        )
        agg = json.loads((output / "holdout_summary.json").read_text())
        check_evaluation_semantics_or_raise(
            agg, artifact_path=str(output / "holdout_summary.json"),
        )
        # Schema fields inherited verbatim.
        assert agg["artifact_schema_version"] == (
            ARTIFACT_SCHEMA_VERSION_PHASE2C_7_1
        )
        assert agg["regime_key"] == "v2.validation"
        assert agg["regime_label"] == "validation_2024"

    def test_filtered_aggregate_records_filter_provenance(self, tmp_path):
        """T7: filtered aggregate must record the filter parameters.

        Without provenance fields the filtered artifact looks identical
        to a primary artifact, and a future maintainer can't tell which
        threshold produced which subset. Add minimal provenance:
        derived_from_run_id, filter_predicate, filter_threshold,
        primary_total, filter_excluded_count.
        """
        primary = _stub_primary_run(tmp_path)
        output = tmp_path / "audit_2024_v1_filtered"
        filter_module.apply_trade_count_filter(
            primary_dir=primary, output_dir=output,
        )
        agg = json.loads((output / "holdout_summary.json").read_text())
        assert agg["derived_from_run_id"] == "audit_2024_v1"
        assert agg["filter_predicate"] == "holdout_metrics.total_trades >= N"
        assert agg["filter_threshold"] == 20
        assert agg["filter_primary_total"] == 6
        assert agg["filter_excluded_count"] == 3


class TestOverwriteProtection:
    """Mirror producer convention: refuse to overwrite non-empty output dir."""

    def test_refuse_overwrite_without_force(self, tmp_path):
        primary = _stub_primary_run(tmp_path)
        output = tmp_path / "audit_2024_v1_filtered"
        output.mkdir()
        (output / "leftover.txt").write_text("existing")
        with pytest.raises(FileExistsError):
            filter_module.apply_trade_count_filter(
                primary_dir=primary, output_dir=output, force=False,
            )

    def test_force_allows_overwrite(self, tmp_path):
        primary = _stub_primary_run(tmp_path)
        output = tmp_path / "audit_2024_v1_filtered"
        output.mkdir()
        (output / "leftover.txt").write_text("existing")
        # Should not raise.
        filter_module.apply_trade_count_filter(
            primary_dir=primary, output_dir=output, force=True,
        )


# ---------------------------------------------------------------------------
# CLI surface (T8)
# ---------------------------------------------------------------------------


class TestCli:
    """Thin CLI wrapper — no --threshold flag per §5.3 Rule 1."""

    def test_no_threshold_flag(self):
        """The CLI must NOT expose --threshold; threshold is code-pinned."""
        parser = filter_module._build_argparser()
        flat = {f for a in parser._actions for f in a.option_strings}
        assert "--threshold" not in flat
        assert "--min-trades" not in flat
        assert "--filter-threshold" not in flat

    def test_main_smoke(self, tmp_path, monkeypatch):
        primary = _stub_primary_run(tmp_path)
        monkeypatch.setattr(
            sys, "argv",
            ["filter_evaluation_gate.py",
             "--primary-run-id", "audit_2024_v1",
             "--output-run-id", "audit_2024_v1_filtered",
             "--output-root", str(tmp_path)],
        )
        rc = filter_module.main()
        assert rc == 0
        out = tmp_path / "audit_2024_v1_filtered"
        assert (out / "holdout_summary.json").exists()
        assert (out / "holdout_results.csv").exists()
        agg = json.loads((out / "holdout_summary.json").read_text())
        assert agg["counts"]["total"] == 3

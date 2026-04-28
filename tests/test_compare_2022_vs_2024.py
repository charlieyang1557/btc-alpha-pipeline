"""Tests for scripts/compare_2022_vs_2024.py (PHASE2C_7.1 §8 Step 4).

The comparison script reads three artifact sets:
  - PHASE2C_6 audit_v1            (2022 evaluation)
  - PHASE2C_7.1 audit_2024_v1     (2024 evaluation)
  - PHASE2C_7.1 audit_2024_v1_filtered (2024 evaluation, total_trades >= 20)

It produces a candidate-aligned diff matrix at
data/phase2c_evaluation_gate/comparison_2022_vs_2024_v1/ with:
  - comparison.csv: 198 rows, one per candidate, with both regimes' outcomes
  - comparison.json: stratified cross-tab (filter_survivor + filter_excluded)
                      x partition (primary/audit_only) x 2x2 (2022 x 2024).

Per §8 Step 4 + Step 2 review note: candidates are matched by per-candidate
JSON's hypothesis_hash field (NOT registry-row hypothesis_hash, which differs
due to engine-side post-compile compute_dsl_hash recomputation).

Per Step 4 review M1: comparison_schema_version = "comparison_schema_v1"
(comparison-shape identity; not phase-arc-instance identity).

Per Step 4 review M2: apply_2022_vs_2024_comparison must assert that the
198 hashes in audit_v1 exactly match the 198 hashes in audit_2024_v1 BEFORE
computing the cross-tab. Mismatched universes invalidate the comparison.

This is a derived analysis artifact, NOT an evaluation_gate producer
artifact. check_evaluation_semantics_or_raise is NOT invoked on comparison
outputs (different domain).
"""
from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backtest.wf_lineage import (  # noqa: E402
    ARTIFACT_SCHEMA_VERSION_PHASE2C_7_1,
    CORRECTED_WF_ENGINE_COMMIT,
    ENGINE_CORRECTED_LINEAGE_TAG,
    EVALUATION_SEMANTICS_TAG,
)

compare_module = importlib.import_module("scripts.compare_2022_vs_2024")


# ---------------------------------------------------------------------------
# Stub fixtures — synthesize small audit_v1 / audit_2024_v1 / filtered runs.
# ---------------------------------------------------------------------------


def _stub_per_candidate(
    *,
    hypothesis_hash: str,
    position: int,
    theme: str,
    name: str,
    wf_sharpe: float,
    lifecycle_state: str,
    holdout_passed: bool | None,
    sharpe: float | None,
    total_trades: int | None,
    schema_version: str | None,
    regime_key: str,
    regime_label: str,
) -> dict:
    """Build a per-candidate summary mirroring the producer's schema."""
    summary = {
        "source_batch_id": "stub-source",
        "run_id": "stub_run",
        "hypothesis_hash": hypothesis_hash,
        "position": position,
        "theme": theme,
        "name": name,
        "wf_test_period_sharpe": wf_sharpe,
        "lifecycle_state": lifecycle_state,
        "error_message": None,
        "wall_clock_seconds": 1.0,
        "evaluation_semantics": EVALUATION_SEMANTICS_TAG,
        "engine_commit": CORRECTED_WF_ENGINE_COMMIT,
        "engine_corrected_lineage": ENGINE_CORRECTED_LINEAGE_TAG,
        "lineage_check": "passed",
        "current_git_sha": "abcd1234567890",
        "regime_key": regime_key,
        "regime_label": regime_label,
    }
    if schema_version is not None:
        summary["artifact_schema_version"] = schema_version
    if holdout_passed is None:
        summary["holdout_metrics"] = None
        summary["passing_criteria"] = None
        summary["gate_pass_per_criterion"] = None
        summary["holdout_passed"] = None
    else:
        summary["holdout_metrics"] = {
            "sharpe_ratio": sharpe,
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


def _write_candidate(run_dir: Path, summary: dict) -> None:
    cand_dir = run_dir / summary["hypothesis_hash"]
    cand_dir.mkdir(parents=True, exist_ok=True)
    (cand_dir / "holdout_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True)
    )


def _make_three_run_set(tmp_path: Path) -> tuple[Path, Path, Path]:
    """Synthesize a 6-candidate population spanning the comparison cells.

    Population layout (designed so every cross-tab cell has at least one
    candidate, including the filter-excluded cells):

      hash  partition   wf       2022 outcome   2024 outcome   trades_2024  filter_state
      a1    primary     +2.5    pass            pass             50         survivor
      b2    primary     +1.8    pass            fail             30         survivor
      c3    primary     +1.2    fail            pass             25         survivor
      d4    primary     +0.7    fail            fail             40         survivor
      e5    audit_only  +0.4    pass            pass             10         excluded
      f6    audit_only  +0.3    fail            fail              5         excluded

    Note: e5 (passed 2022, low 2024 trade count) lands in the excluded
    bucket so we have at least one non-trivial filter_excluded cell.
    """
    audit_v1 = tmp_path / "audit_v1"
    audit_2024 = tmp_path / "audit_2024_v1"
    audit_2024_filt = tmp_path / "audit_2024_v1_filtered"
    audit_v1.mkdir()
    audit_2024.mkdir()
    audit_2024_filt.mkdir()

    pop = [
        # (hash, pos, theme, name, wf, p22, p24, sh22, sh24, t22, t24)
        ("a1aaaaaaaaaaaaaa", 1, "volume_divergence", "a1", 2.5, True, True, 0.7, 0.6, 80, 50),
        ("b2bbbbbbbbbbbbbb", 2, "momentum", "b2", 1.8, True, False, 0.5, -0.6, 60, 30),
        ("c3cccccccccccccc", 3, "calendar_effect", "c3", 1.2, False, True, -0.7, 0.4, 30, 25),
        ("d4dddddddddddddd", 4, "mean_reversion", "d4", 0.7, False, False, -0.4, -0.3, 50, 40),
        ("e5eeeeeeeeeeeeee", 5, "volume_divergence", "e5", 0.4, True, True, 0.6, 0.5, 12, 10),
        ("f6ffffffffffffff", 6, "volatility_regime", "f6", 0.3, False, False, -0.5, -0.4, 8, 5),
    ]
    for h, pos, theme, name, wf, p22, p24, sh22, sh24, t22, t24 in pop:
        # 2022 audit_v1 — legacy schema (no artifact_schema_version)
        _write_candidate(audit_v1, _stub_per_candidate(
            hypothesis_hash=h, position=pos, theme=theme, name=name,
            wf_sharpe=wf,
            lifecycle_state="holdout_passed" if p22 else "holdout_failed",
            holdout_passed=p22, sharpe=sh22, total_trades=t22,
            schema_version=None,  # PHASE2C_6 legacy
            regime_key="v2.regime_holdout", regime_label="bear_2022",
        ))
        # 2024 audit_2024_v1 — phase2c_7_1 schema
        _write_candidate(audit_2024, _stub_per_candidate(
            hypothesis_hash=h, position=pos, theme=theme, name=name,
            wf_sharpe=wf,
            lifecycle_state="holdout_passed" if p24 else "holdout_failed",
            holdout_passed=p24, sharpe=sh24, total_trades=t24,
            schema_version=ARTIFACT_SCHEMA_VERSION_PHASE2C_7_1,
            regime_key="v2.validation", regime_label="validation_2024",
        ))
        # filtered subset: only candidates with t24 >= 20
        if t24 >= 20:
            _write_candidate(audit_2024_filt, _stub_per_candidate(
                hypothesis_hash=h, position=pos, theme=theme, name=name,
                wf_sharpe=wf,
                lifecycle_state="holdout_passed" if p24 else "holdout_failed",
                holdout_passed=p24, sharpe=sh24, total_trades=t24,
                schema_version=ARTIFACT_SCHEMA_VERSION_PHASE2C_7_1,
                regime_key="v2.validation", regime_label="validation_2024",
            ))
    return audit_v1, audit_2024, audit_2024_filt


# ---------------------------------------------------------------------------
# T1 — Hash-axis matching uses per-candidate JSON field, not registry.
# ---------------------------------------------------------------------------


class TestHashAxisMatching:
    def test_loads_hashes_from_per_candidate_json_field(self, tmp_path):
        """T1: _load_run_artifacts keys by per-candidate JSON's hypothesis_hash."""
        a22, a24, _ = _make_three_run_set(tmp_path)
        loaded_22 = compare_module._load_run_artifacts(a22)
        loaded_24 = compare_module._load_run_artifacts(a24)
        # Keys are hypothesis_hash strings from per-candidate JSON.
        expected_hashes = {
            "a1aaaaaaaaaaaaaa", "b2bbbbbbbbbbbbbb", "c3cccccccccccccc",
            "d4dddddddddddddd", "e5eeeeeeeeeeeeee", "f6ffffffffffffff",
        }
        assert set(loaded_22) == expected_hashes
        assert set(loaded_24) == expected_hashes
        # The dict's value is the per-candidate summary dict.
        assert loaded_22["a1aaaaaaaaaaaaaa"]["hypothesis_hash"] == "a1aaaaaaaaaaaaaa"


# ---------------------------------------------------------------------------
# T2 / T5 — cross-tab cell counts + partition assignment.
# ---------------------------------------------------------------------------


class TestCrossTabCellCounts:
    def test_cross_tab_cells_derive_from_input_artifacts(self, tmp_path):
        """T2 + T5: each of the 4 (2022 x 2024) cells is correctly populated.

        Population mapping per the stub design:
          a1 [primary, survivor]: pass-22, pass-24
          b2 [primary, survivor]: pass-22, fail-24
          c3 [primary, survivor]: fail-22, pass-24
          d4 [primary, survivor]: fail-22, fail-24
          e5 [audit_only, excluded]: pass-22, pass-24
          f6 [audit_only, excluded]: fail-22, fail-24
        """
        a22, a24, a24f = _make_three_run_set(tmp_path)
        out_dir = tmp_path / "comparison"
        result = compare_module.apply_2022_vs_2024_comparison(
            audit_v1_dir=a22,
            audit_2024_v1_dir=a24,
            audit_2024_v1_filtered_dir=a24f,
            output_dir=out_dir,
        )
        assert result.n_candidates == 6
        cmp = json.loads((out_dir / "comparison.json").read_text())

        # filter_survivor cross-tab.
        s = cmp["filter_survivor_cross_tab"]
        assert s["primary"] == {
            "passed_2022_passed_2024": 1,  # a1
            "passed_2022_failed_2024": 1,  # b2
            "failed_2022_passed_2024": 1,  # c3
            "failed_2022_failed_2024": 1,  # d4
        }
        # No audit_only candidates in the survivor partition.
        assert s["audit_only"] == {
            "passed_2022_passed_2024": 0,
            "passed_2022_failed_2024": 0,
            "failed_2022_passed_2024": 0,
            "failed_2022_failed_2024": 0,
        }

        # filter_excluded cross-tab.
        x = cmp["filter_excluded_cross_tab"]
        # No primary candidates in the excluded partition.
        assert x["primary"] == {
            "passed_2022_passed_2024": 0,
            "passed_2022_failed_2024": 0,
            "failed_2022_passed_2024": 0,
            "failed_2022_failed_2024": 0,
        }
        assert x["audit_only"] == {
            "passed_2022_passed_2024": 1,  # e5
            "passed_2022_failed_2024": 0,
            "failed_2022_passed_2024": 0,
            "failed_2022_failed_2024": 1,  # f6
        }

        # Totals
        assert cmp["totals"]["n_candidates"] == 6
        assert cmp["totals"]["n_filter_survivor"] == 4
        assert cmp["totals"]["n_filter_excluded"] == 2

    def test_partition_assignment_threshold_inclusive(self, tmp_path):
        """T5: partition split uses wf_test_period_sharpe > 0.5 (strict)."""
        a22, a24, a24f = _make_three_run_set(tmp_path)
        out_dir = tmp_path / "comparison"
        compare_module.apply_2022_vs_2024_comparison(
            audit_v1_dir=a22, audit_2024_v1_dir=a24,
            audit_2024_v1_filtered_dir=a24f, output_dir=out_dir,
        )
        # Per-candidate CSV must label e5 (wf=0.4) and f6 (wf=0.3) as audit_only.
        import csv as _csv
        rows = list(_csv.DictReader(
            (out_dir / "comparison.csv").open()
        ))
        partition = {r["hypothesis_hash"]: r["partition"] for r in rows}
        # > 0.5 strict: a1=2.5, b2=1.8, c3=1.2, d4=0.7 → primary
        assert partition["a1aaaaaaaaaaaaaa"] == "primary"
        assert partition["d4dddddddddddddd"] == "primary"
        # <= 0.5 → audit_only: e5=0.4, f6=0.3
        assert partition["e5eeeeeeeeeeeeee"] == "audit_only"
        assert partition["f6ffffffffffffff"] == "audit_only"


# ---------------------------------------------------------------------------
# T3 — filter_state enum tri-value.
# ---------------------------------------------------------------------------


class TestFilterStateEnum:
    def test_filter_state_is_tri_valued_enum(self, tmp_path):
        """T3: holdout_2024_filter_state is one of three enum values, never null."""
        a22, a24, a24f = _make_three_run_set(tmp_path)
        out_dir = tmp_path / "comparison"
        compare_module.apply_2022_vs_2024_comparison(
            audit_v1_dir=a22, audit_2024_v1_dir=a24,
            audit_2024_v1_filtered_dir=a24f, output_dir=out_dir,
        )
        import csv as _csv
        rows = list(_csv.DictReader((out_dir / "comparison.csv").open()))
        fs = {r["hypothesis_hash"]: r["holdout_2024_filter_state"] for r in rows}
        assert fs["a1aaaaaaaaaaaaaa"] == "survivor_passed"  # in filtered, p24=True
        assert fs["b2bbbbbbbbbbbbbb"] == "survivor_failed"  # in filtered, p24=False
        assert fs["c3cccccccccccccc"] == "survivor_passed"  # in filtered, p24=True
        assert fs["d4dddddddddddddd"] == "survivor_failed"  # in filtered, p24=False
        assert fs["e5eeeeeeeeeeeeee"] == "excluded"          # not in filtered
        assert fs["f6ffffffffffffff"] == "excluded"          # not in filtered
        # No null/empty values.
        for r in rows:
            assert r["holdout_2024_filter_state"] in {
                "survivor_passed", "survivor_failed", "excluded",
            }


# ---------------------------------------------------------------------------
# T4 — missing-hash + universe-mismatch error path (M2).
# ---------------------------------------------------------------------------


class TestUniverseSymmetry:
    def test_mismatched_universes_raise(self, tmp_path):
        """T4 / M2: universe mismatch between audit_v1 and audit_2024_v1 raises.

        Per Step 4 review M2: silent comparison over a partial intersection
        is a class of drift defect. Fail-fast with the offending hashes
        before computing the cross-tab.
        """
        a22, a24, a24f = _make_three_run_set(tmp_path)
        # Drop one candidate from audit_v1 to break universe symmetry.
        import shutil
        shutil.rmtree(a22 / "f6ffffffffffffff")
        with pytest.raises(ValueError) as exc_info:
            compare_module.apply_2022_vs_2024_comparison(
                audit_v1_dir=a22, audit_2024_v1_dir=a24,
                audit_2024_v1_filtered_dir=a24f,
                output_dir=tmp_path / "comparison",
            )
        msg = str(exc_info.value)
        assert "universe" in msg.lower() or "symmetric" in msg.lower() or "mismatch" in msg.lower()
        assert "f6ffffffffffffff" in msg

    def test_filtered_subset_must_be_subset_of_2024(self, tmp_path):
        """T4b: filtered set having a hash not in audit_2024_v1 raises.

        Defensive — the filter is post-evaluation, so by construction
        filtered hashes ⊆ audit_2024_v1 hashes. Catch if a future filter
        run produces inconsistent inputs.
        """
        a22, a24, a24f = _make_three_run_set(tmp_path)
        # Inject an extra hash into the filtered dir that isn't in audit_2024.
        rogue_dir = a24f / "ffffffffffffffff"
        rogue_dir.mkdir()
        (rogue_dir / "holdout_summary.json").write_text(
            json.dumps(_stub_per_candidate(
                hypothesis_hash="ffffffffffffffff", position=99,
                theme="test", name="rogue", wf_sharpe=0.0,
                lifecycle_state="holdout_passed", holdout_passed=True,
                sharpe=0.5, total_trades=50,
                schema_version=ARTIFACT_SCHEMA_VERSION_PHASE2C_7_1,
                regime_key="v2.validation", regime_label="validation_2024",
            ))
        )
        with pytest.raises(ValueError) as exc_info:
            compare_module.apply_2022_vs_2024_comparison(
                audit_v1_dir=a22, audit_2024_v1_dir=a24,
                audit_2024_v1_filtered_dir=a24f,
                output_dir=tmp_path / "comparison",
            )
        assert "filtered" in str(exc_info.value).lower()
        assert "ffffffffffffffff" in str(exc_info.value)


# ---------------------------------------------------------------------------
# T6 — comparison.json schema.
# ---------------------------------------------------------------------------


class TestComparisonJsonSchema:
    def test_top_level_keys_present(self, tmp_path):
        """T6: comparison.json carries all required top-level keys."""
        a22, a24, a24f = _make_three_run_set(tmp_path)
        out_dir = tmp_path / "comparison"
        compare_module.apply_2022_vs_2024_comparison(
            audit_v1_dir=a22, audit_2024_v1_dir=a24,
            audit_2024_v1_filtered_dir=a24f, output_dir=out_dir,
        )
        cmp = json.loads((out_dir / "comparison.json").read_text())
        for key in (
            "filter_survivor_cross_tab",
            "filter_excluded_cross_tab",
            "totals",
            "lineage_inputs",
            "comparison_schema_version",
            "produced_at_utc",
        ):
            assert key in cmp, f"missing top-level key: {key}"

    def test_schema_version_is_comparison_v1(self, tmp_path):
        """M1: comparison_schema_version is shape-identity, not arc-instance."""
        a22, a24, a24f = _make_three_run_set(tmp_path)
        out_dir = tmp_path / "comparison"
        compare_module.apply_2022_vs_2024_comparison(
            audit_v1_dir=a22, audit_2024_v1_dir=a24,
            audit_2024_v1_filtered_dir=a24f, output_dir=out_dir,
        )
        cmp = json.loads((out_dir / "comparison.json").read_text())
        assert cmp["comparison_schema_version"] == "comparison_schema_v1"


# ---------------------------------------------------------------------------
# T7 — lineage_inputs paths recorded.
# ---------------------------------------------------------------------------


class TestLineageInputs:
    def test_lineage_inputs_record_source_paths(self, tmp_path):
        """T7: comparison.json records source artifact dir paths.

        Comparison artifact is a derived analysis — its lineage
        attestation is the set of input artifact dirs, not an
        evaluation_semantics + engine_commit pair.
        """
        a22, a24, a24f = _make_three_run_set(tmp_path)
        out_dir = tmp_path / "comparison"
        compare_module.apply_2022_vs_2024_comparison(
            audit_v1_dir=a22, audit_2024_v1_dir=a24,
            audit_2024_v1_filtered_dir=a24f, output_dir=out_dir,
        )
        cmp = json.loads((out_dir / "comparison.json").read_text())
        li = cmp["lineage_inputs"]
        assert li["audit_v1_path"] == str(a22)
        assert li["audit_2024_v1_path"] == str(a24)
        assert li["audit_2024_v1_filtered_path"] == str(a24f)


# ---------------------------------------------------------------------------
# T8 — overwrite protection.
# ---------------------------------------------------------------------------


class TestOverwriteProtection:
    def test_refuse_overwrite_without_force(self, tmp_path):
        a22, a24, a24f = _make_three_run_set(tmp_path)
        out_dir = tmp_path / "comparison"
        out_dir.mkdir()
        (out_dir / "leftover.txt").write_text("existing")
        with pytest.raises(FileExistsError):
            compare_module.apply_2022_vs_2024_comparison(
                audit_v1_dir=a22, audit_2024_v1_dir=a24,
                audit_2024_v1_filtered_dir=a24f, output_dir=out_dir,
                force=False,
            )

    def test_force_allows_overwrite(self, tmp_path):
        a22, a24, a24f = _make_three_run_set(tmp_path)
        out_dir = tmp_path / "comparison"
        out_dir.mkdir()
        (out_dir / "leftover.txt").write_text("existing")
        compare_module.apply_2022_vs_2024_comparison(
            audit_v1_dir=a22, audit_2024_v1_dir=a24,
            audit_2024_v1_filtered_dir=a24f, output_dir=out_dir,
            force=True,
        )


# ---------------------------------------------------------------------------
# T9 — CLI smoke.
# ---------------------------------------------------------------------------


class TestCli:
    def test_main_smoke(self, tmp_path, monkeypatch):
        a22, a24, a24f = _make_three_run_set(tmp_path)
        monkeypatch.setattr(
            sys, "argv",
            ["compare_2022_vs_2024.py",
             "--audit-v1-dir", str(a22),
             "--audit-2024-v1-dir", str(a24),
             "--audit-2024-v1-filtered-dir", str(a24f),
             "--output-dir", str(tmp_path / "comparison")],
        )
        rc = compare_module.main()
        assert rc == 0
        assert (tmp_path / "comparison" / "comparison.csv").exists()
        assert (tmp_path / "comparison" / "comparison.json").exists()

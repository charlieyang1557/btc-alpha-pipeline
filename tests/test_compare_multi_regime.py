"""Tests for scripts/compare_multi_regime.py — PHASE2C_8.1 §8 Step 4.

N-way candidate-aligned comparison generalizing PHASE2C_7.1's
compare_2022_vs_2024.py to n=4 (or arbitrary n>=2). Tests cover:

- Pure-logic layer (mock data; no I/O):
  * Regime metadata resolution from REGIME_KEY_LABEL_MAPPING
  * Mixed-schema dispatch (absent / phase2c_7_1 / phase2c_8_1)
  * Per-candidate row construction for n regimes
  * Pass-count derivation (0..N per candidate per tier)
  * Cohort categorization (a/c plus per-regime cross-tab)
  * In_sample_caveat stratification per regime
  * Universe symmetry + filtered-subset assertions
  * CLI key=dir flag parsing
  * Empty-cohort handling

- Integration layer (real artifacts on disk):
  * 4-regime end-to-end against canonical paths
  * Output structure per spec §6.6 (CSV + JSON)
  * Hypothesis_hash join correctness; 198-row preservation
  * Lineage provenance recorded; per-regime metadata stamped
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
    ARTIFACT_SCHEMA_VERSION_PHASE2C_8_1,
)

cmp_mod = importlib.import_module("scripts.compare_multi_regime")


# ---------------------------------------------------------------------------
# Stub fixtures
# ---------------------------------------------------------------------------


def _stub_per_candidate_summary(
    hypothesis_hash: str,
    *,
    holdout_passed: bool | None,
    total_trades: int = 50,
    sharpe: float = 1.0,
    wf_sharpe: float = 0.6,
    theme: str = "calendar_effect",
) -> dict:
    """Construct a minimal per-candidate holdout_summary stub."""
    return {
        "hypothesis_hash": hypothesis_hash,
        "theme": theme,
        "wf_test_period_sharpe": wf_sharpe,
        "holdout_passed": holdout_passed,
        "holdout_metrics": {
            "sharpe_ratio": sharpe,
            "max_drawdown": 0.10,
            "total_return": 0.05,
            "total_trades": total_trades,
        },
    }


def _stub_regime_input_unfiltered(
    regime_key: str,
    artifacts: dict[str, dict],
) -> dict[str, dict]:
    """Returns the artifacts dict for an unfiltered regime tier (mock)."""
    return artifacts


# ---------------------------------------------------------------------------
# Regime metadata resolution
# ---------------------------------------------------------------------------


class TestResolveRegimeMetadata:
    """`_resolve_regime_metadata` derives label / schema_version / caveat."""

    def test_inherited_v2_regime_holdout_no_caveat(self):
        meta = cmp_mod._resolve_regime_metadata("v2.regime_holdout")
        assert meta["regime_key"] == "v2.regime_holdout"
        assert meta["label"] == "bear_2022"
        assert meta["schema_version"] == ARTIFACT_SCHEMA_VERSION_PHASE2C_7_1
        assert meta["in_sample_caveat_applies"] is False

    def test_inherited_v2_validation_no_caveat(self):
        meta = cmp_mod._resolve_regime_metadata("v2.validation")
        assert meta["label"] == "validation_2024"
        assert meta["schema_version"] == ARTIFACT_SCHEMA_VERSION_PHASE2C_7_1
        assert meta["in_sample_caveat_applies"] is False

    def test_novel_eval_2020_v1_caveat_applies(self):
        meta = cmp_mod._resolve_regime_metadata(
            "evaluation_regimes.eval_2020_v1"
        )
        assert meta["label"] == "eval_2020_v1"
        assert meta["schema_version"] == ARTIFACT_SCHEMA_VERSION_PHASE2C_8_1
        assert meta["in_sample_caveat_applies"] is True

    def test_novel_eval_2021_v1_caveat_applies(self):
        meta = cmp_mod._resolve_regime_metadata(
            "evaluation_regimes.eval_2021_v1"
        )
        assert meta["label"] == "eval_2021_v1"
        assert meta["schema_version"] == ARTIFACT_SCHEMA_VERSION_PHASE2C_8_1
        assert meta["in_sample_caveat_applies"] is True

    def test_unknown_regime_key_raises(self):
        with pytest.raises(ValueError) as exc_info:
            cmp_mod._resolve_regime_metadata("v2.does_not_exist")
        assert "regime_key" in str(exc_info.value)


# ---------------------------------------------------------------------------
# Per-candidate row construction (n-way)
# ---------------------------------------------------------------------------


class TestPerCandidateRowNWay:
    """`_build_per_candidate_row` joins N regime summaries correctly."""

    def test_4_regimes_all_pass_unfiltered_in_filtered_3of4(self):
        h = "abc123"
        regime_inputs = [
            ("v2.regime_holdout", "bear_2022"),
            ("v2.validation", "validation_2024"),
            ("evaluation_regimes.eval_2020_v1", "eval_2020_v1"),
            ("evaluation_regimes.eval_2021_v1", "eval_2021_v1"),
        ]
        unfiltered_arts = {
            label: {h: _stub_per_candidate_summary(h, holdout_passed=True, total_trades=50)}
            for _, label in regime_inputs
        }
        # Candidate is in 3 of 4 filtered tiers (trade-count >= 20)
        filtered_arts = {
            "bear_2022": {h: _stub_per_candidate_summary(h, holdout_passed=True, total_trades=50)},
            "validation_2024": {h: _stub_per_candidate_summary(h, holdout_passed=True, total_trades=50)},
            "eval_2020_v1": {h: _stub_per_candidate_summary(h, holdout_passed=True, total_trades=50)},
            # eval_2021_v1: missing from filtered → excluded
        }
        row = cmp_mod._build_per_candidate_row(
            hypothesis_hash=h,
            regime_keys=[k for k, _ in regime_inputs],
            unfiltered_artifacts_by_label=unfiltered_arts,
            filtered_artifacts_by_label=filtered_arts,
        )
        assert row["hypothesis_hash"] == h
        assert row["pass_count_unfiltered"] == 4
        assert row["pass_count_filtered"] == 3
        # Per-regime fields stamped
        assert row["holdout_bear_2022_passed"] is True
        assert row["holdout_validation_2024_passed"] is True
        assert row["holdout_eval_2020_v1_passed"] is True
        assert row["holdout_eval_2021_v1_passed"] is True
        assert row["holdout_eval_2021_v1_filter_state"] == "excluded"
        assert row["holdout_bear_2022_filter_state"] == "survivor_passed"

    def test_2_regimes_mixed_pass_filter(self):
        h = "def456"
        regime_keys = ["v2.regime_holdout", "v2.validation"]
        unfiltered_arts = {
            "bear_2022": {h: _stub_per_candidate_summary(h, holdout_passed=False, total_trades=15)},
            "validation_2024": {h: _stub_per_candidate_summary(h, holdout_passed=True, total_trades=50)},
        }
        filtered_arts = {
            # bear_2022 candidate excluded (trade < 20)
            "validation_2024": {h: _stub_per_candidate_summary(h, holdout_passed=True, total_trades=50)},
        }
        row = cmp_mod._build_per_candidate_row(
            hypothesis_hash=h,
            regime_keys=regime_keys,
            unfiltered_artifacts_by_label=unfiltered_arts,
            filtered_artifacts_by_label=filtered_arts,
        )
        assert row["pass_count_unfiltered"] == 1  # only validation_2024 passes
        assert row["pass_count_filtered"] == 1  # bear_2022 excluded; validation_2024 passes
        assert row["holdout_bear_2022_filter_state"] == "excluded"
        assert row["holdout_validation_2024_filter_state"] == "survivor_passed"

    def test_holdout_error_state_pass_count_excludes_none(self):
        """holdout_passed=None (error) does not count toward pass-count."""
        h = "err789"
        regime_keys = ["v2.regime_holdout", "v2.validation"]
        unfiltered_arts = {
            "bear_2022": {h: _stub_per_candidate_summary(h, holdout_passed=None)},
            "validation_2024": {h: _stub_per_candidate_summary(h, holdout_passed=True)},
        }
        filtered_arts = {
            "bear_2022": {h: _stub_per_candidate_summary(h, holdout_passed=None)},
            "validation_2024": {h: _stub_per_candidate_summary(h, holdout_passed=True)},
        }
        row = cmp_mod._build_per_candidate_row(
            hypothesis_hash=h,
            regime_keys=regime_keys,
            unfiltered_artifacts_by_label=unfiltered_arts,
            filtered_artifacts_by_label=filtered_arts,
        )
        # None is not counted as pass; only validation_2024 contributes
        assert row["pass_count_unfiltered"] == 1
        assert row["pass_count_filtered"] == 1


# ---------------------------------------------------------------------------
# Cohort categorization
# ---------------------------------------------------------------------------


class TestCohortCategorization:
    """Cohort (a) cross-regime survivors + cohort (c) failures."""

    def test_cohort_a_unfiltered_cardinality_at_n4(self):
        """Cohort (a) unfiltered = candidates passing all 4 regimes."""
        rows = [
            {"hypothesis_hash": "h1", "pass_count_unfiltered": 4, "pass_count_filtered": 4},
            {"hypothesis_hash": "h2", "pass_count_unfiltered": 4, "pass_count_filtered": 3},
            {"hypothesis_hash": "h3", "pass_count_unfiltered": 3, "pass_count_filtered": 3},
            {"hypothesis_hash": "h4", "pass_count_unfiltered": 0, "pass_count_filtered": 0},
        ]
        result = cmp_mod._build_cohort_categorization(rows, n_regimes=4)
        assert set(result["cohort_a_unfiltered"]) == {"h1", "h2"}
        assert set(result["cohort_a_filtered"]) == {"h1"}

    def test_cohort_c_failures_passes_zero(self):
        """Cohort (c) = candidates passing 0 regimes."""
        rows = [
            {"hypothesis_hash": "h1", "pass_count_unfiltered": 4, "pass_count_filtered": 4},
            {"hypothesis_hash": "h2", "pass_count_unfiltered": 0, "pass_count_filtered": 0},
            {"hypothesis_hash": "h3", "pass_count_unfiltered": 0, "pass_count_filtered": 0},
        ]
        result = cmp_mod._build_cohort_categorization(rows, n_regimes=4)
        assert set(result["cohort_c_unfiltered"]) == {"h2", "h3"}

    def test_empty_cohort_a_handling(self):
        """If no candidate passes all n regimes, cohort_a is empty list."""
        rows = [
            {"hypothesis_hash": "h1", "pass_count_unfiltered": 3, "pass_count_filtered": 2},
        ]
        result = cmp_mod._build_cohort_categorization(rows, n_regimes=4)
        assert result["cohort_a_unfiltered"] == []
        assert result["cohort_a_filtered"] == []

    def test_pass_count_distribution(self):
        """Per-regime cross-tab: distribution of pass-counts."""
        rows = [
            {"pass_count_unfiltered": 4, "pass_count_filtered": 4},
            {"pass_count_unfiltered": 3, "pass_count_filtered": 3},
            {"pass_count_unfiltered": 3, "pass_count_filtered": 2},
            {"pass_count_unfiltered": 0, "pass_count_filtered": 0},
        ]
        dist = cmp_mod._build_pass_count_distribution(rows, n_regimes=4)
        assert dist["unfiltered"] == {0: 1, 1: 0, 2: 0, 3: 2, 4: 1}
        assert dist["filtered"] == {0: 1, 1: 0, 2: 1, 3: 1, 4: 1}


# ---------------------------------------------------------------------------
# In-sample caveat stratification
# ---------------------------------------------------------------------------


class TestInSampleCaveatStratification:
    """In_sample_caveat partitioning for spec §7.4 evidentiary categories."""

    def test_fully_out_of_sample_pass_count(self):
        """Caveat=false regimes (bear_2022, validation_2024) — pass count."""
        regime_keys = [
            "v2.regime_holdout",
            "v2.validation",
            "evaluation_regimes.eval_2020_v1",
            "evaluation_regimes.eval_2021_v1",
        ]
        # Candidate passes only fully-out-of-sample regimes
        per_regime_passes = {
            "bear_2022": True,
            "validation_2024": True,
            "eval_2020_v1": False,
            "eval_2021_v1": False,
        }
        result = cmp_mod._stratify_in_sample_caveat(
            per_regime_passes, regime_keys
        )
        assert result["fully_out_of_sample_pass_count"] == 2
        assert result["train_overlap_pass_count"] == 0

    def test_train_overlap_only_pass(self):
        """Candidate passes only train-overlap (caveat=true) regimes."""
        regime_keys = [
            "v2.regime_holdout",
            "v2.validation",
            "evaluation_regimes.eval_2020_v1",
            "evaluation_regimes.eval_2021_v1",
        ]
        per_regime_passes = {
            "bear_2022": False,
            "validation_2024": False,
            "eval_2020_v1": True,
            "eval_2021_v1": True,
        }
        result = cmp_mod._stratify_in_sample_caveat(
            per_regime_passes, regime_keys
        )
        assert result["fully_out_of_sample_pass_count"] == 0
        assert result["train_overlap_pass_count"] == 2


# ---------------------------------------------------------------------------
# CLI parsing
# ---------------------------------------------------------------------------


class TestCliFlagParsing:
    """`--regime-input key=dir` and `--filtered-input key=dir` parsing."""

    def test_single_regime_input_parsed(self):
        args = cmp_mod._build_argparser().parse_args([
            "--regime-input", "v2.regime_holdout=path/to/audit_v1",
            "--filtered-input", "v2.regime_holdout=path/to/audit_v1_filtered",
            "--output-dir", "out/",
        ])
        assert args.regime_input == ["v2.regime_holdout=path/to/audit_v1"]
        assert args.filtered_input == [
            "v2.regime_holdout=path/to/audit_v1_filtered"
        ]
        assert args.output_dir == "out/"

    def test_multiple_regime_inputs_parsed(self):
        args = cmp_mod._build_argparser().parse_args([
            "--regime-input", "v2.regime_holdout=p1",
            "--regime-input", "v2.validation=p2",
            "--regime-input", "evaluation_regimes.eval_2020_v1=p3",
            "--regime-input", "evaluation_regimes.eval_2021_v1=p4",
            "--filtered-input", "v2.regime_holdout=p1f",
            "--filtered-input", "v2.validation=p2f",
            "--filtered-input", "evaluation_regimes.eval_2020_v1=p3f",
            "--filtered-input", "evaluation_regimes.eval_2021_v1=p4f",
            "--output-dir", "out/",
        ])
        assert len(args.regime_input) == 4
        assert len(args.filtered_input) == 4

    def test_parse_key_dir_pair(self):
        """`_parse_key_dir_pair` splits 'key=dir' tokens."""
        key, path = cmp_mod._parse_key_dir_pair("v2.validation=path/to/dir")
        assert key == "v2.validation"
        assert path == Path("path/to/dir")

    def test_parse_key_dir_pair_malformed_raises(self):
        with pytest.raises(ValueError) as exc_info:
            cmp_mod._parse_key_dir_pair("missing_separator")
        assert "key=dir" in str(exc_info.value)


# ---------------------------------------------------------------------------
# Integration smoke (real artifacts on disk)
# ---------------------------------------------------------------------------


class TestIntegrationN4OnDisk:
    """End-to-end with the 4 real regime artifact sets at canonical paths.

    These tests exercise the full pipeline: CLI parsing → artifact loading →
    universe symmetry check → row construction → cohort categorization →
    output emission. Skipped if any of the canonical paths are absent
    (e.g., on CI without the data fixtures).
    """

    @pytest.fixture
    def regime_paths(self):
        root = PROJECT_ROOT / "data" / "phase2c_evaluation_gate"
        paths = {
            "v2.regime_holdout": (root / "audit_v1", root / "audit_v1_filtered"),
            "v2.validation": (root / "audit_2024_v1", root / "audit_2024_v1_filtered"),
            "evaluation_regimes.eval_2020_v1": (
                root / "eval_2020_v1", root / "eval_2020_v1_filtered"
            ),
            "evaluation_regimes.eval_2021_v1": (
                root / "eval_2021_v1", root / "eval_2021_v1_filtered"
            ),
        }
        for key, (unf, filt) in paths.items():
            if not unf.exists() or not filt.exists():
                pytest.skip(
                    f"canonical paths missing for {key}: "
                    f"unf={unf.exists()} filt={filt.exists()}"
                )
        return paths

    def test_4_regime_e2e_produces_198_rows(self, tmp_path, regime_paths):
        """End-to-end at n=4 against canonical artifacts.

        Pinned canonical numbers reflect the artifact snapshot at
        commit `da1859d` (PHASE2C_8.1 Step 4 commit). Any regeneration
        of the underlying audit_v1 / audit_2024_v1 / eval_2020_v1 /
        eval_2021_v1 artifact sets requires re-pinning here with an
        explicit commit-message acknowledgment of the canonical-number
        change. This is the deliberate coupling: pinned numbers surface
        canonical-finding drift; non-pinned would silently absorb it.
        """
        output_dir = tmp_path / "comparison_test"
        regime_inputs = [
            cmp_mod.RegimeInput(
                regime_key=key,
                unfiltered_dir=unf,
                filtered_dir=filt,
            )
            for key, (unf, filt) in regime_paths.items()
        ]
        result = cmp_mod.apply_multi_regime_comparison(
            regime_inputs=regime_inputs,
            output_dir=output_dir,
        )
        assert result.n_candidates == 198
        assert result.n_regimes == 4

        # CSV file exists and has 199 rows (1 header + 198 data)
        csv_path = output_dir / "comparison_matrix.csv"
        assert csv_path.exists()
        line_count = len(csv_path.read_text().splitlines())
        assert line_count == 199

        # JSON summary exists with required fields
        json_path = output_dir / "comparison_summary.json"
        assert json_path.exists()
        summary = json.loads(json_path.read_text())
        assert summary["totals"]["n_candidates"] == 198
        assert summary["totals"]["n_regimes"] == 4
        assert len(summary["regime_metadata"]) == 4

        # Per-regime metadata stamped correctly
        labels = {m["label"] for m in summary["regime_metadata"]}
        assert labels == {
            "bear_2022", "validation_2024", "eval_2020_v1", "eval_2021_v1"
        }

        # Mixed-schema reconciliation: schema_version field per regime
        schemas = {m["schema_version"] for m in summary["regime_metadata"]}
        # legacy bear_2022 = absent (None); others = phase2c_7_1 or phase2c_8_1
        assert None in schemas
        assert ARTIFACT_SCHEMA_VERSION_PHASE2C_7_1 in schemas
        assert ARTIFACT_SCHEMA_VERSION_PHASE2C_8_1 in schemas

        # --- CANONICAL-NUMBER PINS (Q-S4-8) ---
        # Cohort (a) cross-regime survivors at n=4
        assert summary["cohort_a_cardinality_unfiltered"] == 1
        assert summary["cohort_a_cardinality_filtered"] == 0
        assert summary["cohort_a_unfiltered"] == ["0845d1d7898412f2"]
        assert summary["cohort_a_filtered"] == []

        # Cohort (c) failures
        assert summary["cohort_c_cardinality_unfiltered"] == 76

        # Pass-count distribution (JSON keys are strings)
        assert summary["pass_count_distribution"]["unfiltered"] == {
            "0": 76, "1": 55, "2": 45, "3": 21, "4": 1
        }
        assert summary["pass_count_distribution"]["filtered"] == {
            "0": 87, "1": 58, "2": 38, "3": 15, "4": 0
        }

        # In-sample caveat stratification: 21 vs 8 asymmetry (load-bearing)
        strat = summary["in_sample_caveat_stratification"]
        assert strat["fully_out_of_sample_regimes"] == [
            "bear_2022", "validation_2024"
        ]
        assert strat["train_overlap_regimes"] == [
            "eval_2020_v1", "eval_2021_v1"
        ]
        assert strat["n_passing_all_fully_out_of_sample"] == 8
        assert strat["n_passing_all_train_overlap"] == 21

        # Filtered cohort necessarily subset of unfiltered
        assert set(summary["cohort_a_filtered"]).issubset(
            set(summary["cohort_a_unfiltered"])
        )


# ---------------------------------------------------------------------------
# Synthetic failure-path tests (Q-S4-8 strictness validation)
# ---------------------------------------------------------------------------


def _write_candidate_summary(
    cand_dir: Path,
    *,
    summary: dict,
) -> None:
    """Helper: write a per-candidate holdout_summary.json under cand_dir."""
    cand_dir.mkdir(parents=True, exist_ok=True)
    (cand_dir / "holdout_summary.json").write_text(json.dumps(summary))


def _write_results_csv(run_dir: Path, hashes: list[str]) -> None:
    """Helper: write a minimal holdout_results.csv asserting universe size."""
    run_dir.mkdir(parents=True, exist_ok=True)
    lines = ["hypothesis_hash,holdout_passed"]
    for h in hashes:
        lines.append(f"{h},0")
    (run_dir / "holdout_results.csv").write_text("\n".join(lines) + "\n")


class TestLoaderStrictness:
    """`_load_run_artifacts` strictness on malformed / missing inputs."""

    def test_skips_underscore_prefixed_dirs(self, tmp_path):
        """Convention `_smoke/`, `_filtered/` dirs are skipped silently."""
        run_dir = tmp_path / "regime"
        run_dir.mkdir()
        # Convention dir without per-candidate JSON: must be skipped.
        (run_dir / "_smoke").mkdir()
        # Real candidate dir.
        _write_candidate_summary(
            run_dir / "abc123",
            summary=_stub_per_candidate_summary("abc123", holdout_passed=True),
        )
        loaded = cmp_mod._load_run_artifacts(run_dir)
        assert set(loaded) == {"abc123"}

    def test_raises_on_missing_holdout_summary_json(self, tmp_path):
        """Non-convention candidate dir without summary file → raise."""
        run_dir = tmp_path / "regime"
        run_dir.mkdir()
        (run_dir / "abc123").mkdir()  # No holdout_summary.json inside.
        with pytest.raises(FileNotFoundError) as exc_info:
            cmp_mod._load_run_artifacts(run_dir)
        assert "holdout_summary.json" in str(exc_info.value)

    def test_raises_on_missing_hypothesis_hash_field(self, tmp_path):
        """Per-candidate JSON missing hypothesis_hash field → ValueError."""
        run_dir = tmp_path / "regime"
        run_dir.mkdir()
        bad = {"theme": "calendar_effect", "holdout_passed": True}
        _write_candidate_summary(run_dir / "abc123", summary=bad)
        with pytest.raises(ValueError) as exc_info:
            cmp_mod._load_run_artifacts(run_dir)
        assert "hypothesis_hash" in str(exc_info.value)

    def test_raises_on_duplicate_hypothesis_hash(self, tmp_path):
        """Two dirs with the same hypothesis_hash → raise."""
        run_dir = tmp_path / "regime"
        run_dir.mkdir()
        _write_candidate_summary(
            run_dir / "dir_one",
            summary=_stub_per_candidate_summary("collision", holdout_passed=True),
        )
        _write_candidate_summary(
            run_dir / "dir_two",
            summary=_stub_per_candidate_summary("collision", holdout_passed=False),
        )
        with pytest.raises(ValueError) as exc_info:
            cmp_mod._load_run_artifacts(run_dir)
        assert "Duplicate" in str(exc_info.value)

    def test_raises_on_expected_count_mismatch(self, tmp_path):
        """Loaded count != expected_count → ValueError surfaced."""
        run_dir = tmp_path / "regime"
        run_dir.mkdir()
        _write_candidate_summary(
            run_dir / "abc123",
            summary=_stub_per_candidate_summary("abc123", holdout_passed=True),
        )
        # Only 1 candidate dir; declare expected_count=2 to force mismatch.
        with pytest.raises(ValueError) as exc_info:
            cmp_mod._load_run_artifacts(run_dir, expected_count=2)
        assert "Cardinality mismatch" in str(exc_info.value) or \
               "expected 2" in str(exc_info.value)

    def test_expected_count_match_succeeds(self, tmp_path):
        """Loaded count == expected_count → no raise."""
        run_dir = tmp_path / "regime"
        run_dir.mkdir()
        _write_candidate_summary(
            run_dir / "abc",
            summary=_stub_per_candidate_summary("abc", holdout_passed=True),
        )
        _write_candidate_summary(
            run_dir / "def",
            summary=_stub_per_candidate_summary("def", holdout_passed=False),
        )
        loaded = cmp_mod._load_run_artifacts(run_dir, expected_count=2)
        assert set(loaded) == {"abc", "def"}


class TestExpectedCountFromResultsCsv:
    """`_expected_count_from_results_csv` derives universe size from CSV."""

    def test_returns_row_count_excluding_header(self, tmp_path):
        run_dir = tmp_path / "regime"
        _write_results_csv(run_dir, hashes=["h1", "h2", "h3"])
        assert cmp_mod._expected_count_from_results_csv(run_dir) == 3

    def test_returns_none_when_csv_absent(self, tmp_path):
        run_dir = tmp_path / "regime"
        run_dir.mkdir()
        assert cmp_mod._expected_count_from_results_csv(run_dir) is None

    def test_returns_zero_for_empty_csv(self, tmp_path):
        run_dir = tmp_path / "regime"
        run_dir.mkdir()
        (run_dir / "holdout_results.csv").write_text("")
        assert cmp_mod._expected_count_from_results_csv(run_dir) == 0


class TestApplyMultiRegimeFailurePaths:
    """`apply_multi_regime_comparison` raises on structural inconsistencies."""

    def _build_minimal_regime(
        self,
        root: Path,
        *,
        regime_dir_name: str,
        hashes: list[str],
        all_pass: bool = True,
    ) -> Path:
        """Helper: build a regime+tier dir with N candidate dirs + CSV."""
        run_dir = root / regime_dir_name
        for h in hashes:
            _write_candidate_summary(
                run_dir / h,
                summary=_stub_per_candidate_summary(
                    h, holdout_passed=all_pass, total_trades=50
                ),
            )
        _write_results_csv(run_dir, hashes=hashes)
        return run_dir

    def test_raises_on_universe_mismatch_between_regimes(self, tmp_path):
        """Two regimes with non-overlapping hash sets → universe symmetry raises."""
        unf_a = self._build_minimal_regime(
            tmp_path, regime_dir_name="bear_unf", hashes=["h1", "h2"]
        )
        filt_a = self._build_minimal_regime(
            tmp_path, regime_dir_name="bear_filt", hashes=["h1"]
        )
        unf_b = self._build_minimal_regime(
            tmp_path, regime_dir_name="val_unf", hashes=["h3", "h4"]
        )
        filt_b = self._build_minimal_regime(
            tmp_path, regime_dir_name="val_filt", hashes=["h3"]
        )
        regime_inputs = [
            cmp_mod.RegimeInput(
                regime_key="v2.regime_holdout",
                unfiltered_dir=unf_a,
                filtered_dir=filt_a,
            ),
            cmp_mod.RegimeInput(
                regime_key="v2.validation",
                unfiltered_dir=unf_b,
                filtered_dir=filt_b,
            ),
        ]
        with pytest.raises(ValueError) as exc_info:
            cmp_mod.apply_multi_regime_comparison(
                regime_inputs=regime_inputs,
                output_dir=tmp_path / "out",
            )
        assert "Universe mismatch" in str(exc_info.value)

    def test_raises_on_filtered_subset_violation(self, tmp_path):
        """Filtered regime with hashes absent from unfiltered → raise."""
        unf_a = self._build_minimal_regime(
            tmp_path, regime_dir_name="bear_unf", hashes=["h1", "h2"]
        )
        # Filtered tier contains a hash NOT in unfiltered (h3) → violation.
        filt_a = self._build_minimal_regime(
            tmp_path, regime_dir_name="bear_filt", hashes=["h1", "h3"]
        )
        unf_b = self._build_minimal_regime(
            tmp_path, regime_dir_name="val_unf", hashes=["h1", "h2"]
        )
        filt_b = self._build_minimal_regime(
            tmp_path, regime_dir_name="val_filt", hashes=["h1"]
        )
        regime_inputs = [
            cmp_mod.RegimeInput(
                regime_key="v2.regime_holdout",
                unfiltered_dir=unf_a,
                filtered_dir=filt_a,
            ),
            cmp_mod.RegimeInput(
                regime_key="v2.validation",
                unfiltered_dir=unf_b,
                filtered_dir=filt_b,
            ),
        ]
        with pytest.raises(ValueError) as exc_info:
            cmp_mod.apply_multi_regime_comparison(
                regime_inputs=regime_inputs,
                output_dir=tmp_path / "out",
            )
        msg = str(exc_info.value)
        assert "filtered" in msg.lower() or "absent" in msg.lower()

    def test_raises_on_per_regime_cardinality_mismatch(self, tmp_path):
        """CSV declares N rows but candidate dir count is N-1 → raise."""
        run_dir = tmp_path / "bear_unf"
        # Only 1 per-candidate dir.
        _write_candidate_summary(
            run_dir / "h1",
            summary=_stub_per_candidate_summary("h1", holdout_passed=True),
        )
        # CSV declares 2 hashes (cardinality mismatch).
        _write_results_csv(run_dir, hashes=["h1", "h2"])

        unf_b = self._build_minimal_regime(
            tmp_path, regime_dir_name="val_unf", hashes=["h1", "h2"]
        )
        filt_a = self._build_minimal_regime(
            tmp_path, regime_dir_name="bear_filt", hashes=["h1"]
        )
        filt_b = self._build_minimal_regime(
            tmp_path, regime_dir_name="val_filt", hashes=["h1"]
        )
        regime_inputs = [
            cmp_mod.RegimeInput(
                regime_key="v2.regime_holdout",
                unfiltered_dir=run_dir,
                filtered_dir=filt_a,
            ),
            cmp_mod.RegimeInput(
                regime_key="v2.validation",
                unfiltered_dir=unf_b,
                filtered_dir=filt_b,
            ),
        ]
        with pytest.raises(ValueError) as exc_info:
            cmp_mod.apply_multi_regime_comparison(
                regime_inputs=regime_inputs,
                output_dir=tmp_path / "out",
            )
        msg = str(exc_info.value)
        assert "Cardinality" in msg or "expected" in msg

    def test_raises_on_malformed_candidate_json(self, tmp_path):
        """Candidate JSON missing hypothesis_hash → loader raises."""
        run_dir = tmp_path / "bear_unf"
        run_dir.mkdir()
        # Malformed candidate: no hypothesis_hash field.
        (run_dir / "bad").mkdir()
        (run_dir / "bad" / "holdout_summary.json").write_text(
            json.dumps({"theme": "calendar_effect"})
        )
        _write_results_csv(run_dir, hashes=["bad_hash"])

        unf_b = self._build_minimal_regime(
            tmp_path, regime_dir_name="val_unf", hashes=["bad_hash"]
        )
        filt_a = run_dir  # reuse to satisfy CLI symmetry; will fail before
        filt_b = self._build_minimal_regime(
            tmp_path, regime_dir_name="val_filt", hashes=["bad_hash"]
        )
        regime_inputs = [
            cmp_mod.RegimeInput(
                regime_key="v2.regime_holdout",
                unfiltered_dir=run_dir,
                filtered_dir=filt_a,
            ),
            cmp_mod.RegimeInput(
                regime_key="v2.validation",
                unfiltered_dir=unf_b,
                filtered_dir=filt_b,
            ),
        ]
        with pytest.raises(ValueError) as exc_info:
            cmp_mod.apply_multi_regime_comparison(
                regime_inputs=regime_inputs,
                output_dir=tmp_path / "out",
            )
        assert "hypothesis_hash" in str(exc_info.value)

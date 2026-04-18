"""Tests for the D7 Stage 2b extension of the replay-candidate selector.

Stage 2b extends the Stage 2a N=1 selector with:

* An ``--n 5`` mode that chooses five replay candidates up front.
* Mechanical relationship labels (``agreement_expected`` /
  ``divergence_expected`` / ``neutral``) driven by prior factor-set
  occurrences and maximum factor overlap.
* Hard diversity constraints (>=3 themes, all three position buckets,
  unique hypothesis hashes) that are never relaxed.
* A three-tier soft-constraint ladder for agreement/divergence coverage
  that degrades in a fixed order with machine-readable warnings.
* Explicit rejection accounting surfaced as ``rejection_breakdown``.

The tests here exercise the tier-0 / tier-1 / tier-2 success paths, the
three hard-fail paths, output invariants, deterministic tie-break, and
regression coverage for the Stage 2a N=1 default.

Fixtures under ``tests/fixtures/stage2b_selection/`` are intentionally
minimal; each fixture embodies a single scenario and the test harness
materializes the batch directory + response files at runtime.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts import select_replay_candidate as sel


_REPO_ROOT = Path(__file__).resolve().parent.parent
_FIXTURE_DIR = Path(__file__).parent / "fixtures" / "stage2b_selection"


# ---------------------------------------------------------------------------
# Fixture helpers
# ---------------------------------------------------------------------------


def _response_with_cross(factors: list[str]) -> str:
    """Build a minimal DSL response string containing a cross operator."""
    first = factors[0] if factors else "rsi_14"
    return json.dumps({
        "entry": [{"conditions": [
            {"factor": first, "op": "crosses_above", "value": 30.0},
        ]}],
        "exit": [{"conditions": [
            {"factor": first, "op": "crosses_below", "value": 70.0},
        ]}],
    })


def _materialize_batch(
    tmp_path: Path,
    fixture_path: Path,
    *,
    batch_uuid: str = "stage2b-fixture",
) -> tuple[Path, dict]:
    """Write a Stage 2d batch dir from a fixture JSON.

    Returns (artifacts_root, fixture_payload). The batch dir contains a
    ``stage2d_summary.json`` built from the fixture's ``calls`` list plus
    one ``attempt_<pos>_response.txt`` file per call whose lifecycle
    state is not ``"momentum"``-rejected. Every call gets a response
    file — per-candidate filtering is the script's job.
    """
    fixture_payload = json.loads(fixture_path.read_text(encoding="utf-8"))
    calls = list(fixture_payload["calls"])

    artifacts_root = tmp_path
    batch_dir = artifacts_root / f"batch_{batch_uuid}"
    batch_dir.mkdir(parents=True, exist_ok=True)

    summary_path = batch_dir / "stage2d_summary.json"
    summary_path.write_text(json.dumps({"calls": calls}), encoding="utf-8")

    for call in calls:
        pos = call["position"]
        response_path = batch_dir / f"attempt_{pos:04d}_response.txt"
        response_path.write_text(
            _response_with_cross(call["factors_used"]),
            encoding="utf-8",
        )

    return artifacts_root, fixture_payload


def _run_stage2b(
    tmp_path: Path,
    fixture_path: Path,
    *,
    batch_uuid: str = "stage2b-fixture",
    output_name: str = "replay_candidates.json",
) -> tuple[int, Path, str, str]:
    """Invoke the script with --n=5 against the fixture.

    Returns (returncode, output_path, stdout, stderr).
    """
    artifacts_root, _ = _materialize_batch(
        tmp_path, fixture_path, batch_uuid=batch_uuid,
    )
    output_path = tmp_path / output_name

    proc = subprocess.run(
        [
            sys.executable,
            str(_REPO_ROOT / "scripts" / "select_replay_candidate.py"),
            batch_uuid,
            "--artifacts-root", str(artifacts_root),
            "--n", "5",
            "--output", str(output_path),
        ],
        capture_output=True,
        text=True,
        cwd=_REPO_ROOT,
    )
    return proc.returncode, output_path, proc.stdout, proc.stderr


def _load_output(output_path: Path) -> dict:
    return json.loads(output_path.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Tier 0 — ideal selection
# ---------------------------------------------------------------------------


class TestTier0IdealSelection:
    def test_tier_0_success(self, tmp_path):
        rc, output_path, _, stderr = _run_stage2b(
            tmp_path, _FIXTURE_DIR / "fixture_tier_0_ideal.json",
        )
        assert rc == 0, stderr
        assert output_path.exists()

        out = _load_output(output_path)
        assert out["selection_tier"] == 0
        assert out["selection_warnings"] == []
        assert len(out["candidates"]) == 5

    def test_tier_0_output_invariants(self, tmp_path):
        rc, output_path, _, _ = _run_stage2b(
            tmp_path, _FIXTURE_DIR / "fixture_tier_0_ideal.json",
        )
        assert rc == 0

        out = _load_output(output_path)
        cands = out["candidates"]
        positions = [c["position"] for c in cands]
        assert positions == sorted(positions)
        assert [c["firing_order"] for c in cands] == [1, 2, 3, 4, 5]

        themes = {c["theme"] for c in cands}
        assert len(themes) >= 3

        buckets = {c["position_bucket"] for c in cands}
        assert buckets == {"early", "mid", "late"}

        hashes = {c["hypothesis_hash"] for c in cands}
        assert len(hashes) == 5

        labels = [c["d7a_b_relationship_label"] for c in cands]
        assert any(lb == "agreement_expected" for lb in labels)
        assert any(lb == "divergence_expected" for lb in labels)

    def test_tier_0_stage_label_and_version(self, tmp_path):
        rc, output_path, _, _ = _run_stage2b(
            tmp_path, _FIXTURE_DIR / "fixture_tier_0_ideal.json",
        )
        assert rc == 0
        out = _load_output(output_path)
        assert out["stage_label"] == "d7_stage2b"
        assert out["record_version"] == "1.0"
        assert out["batch_uuid"] == "stage2b-fixture"
        assert out["selection_timestamp_utc"].endswith("Z")

    def test_tier_0_rejection_breakdown_populated(self, tmp_path):
        rc, output_path, _, _ = _run_stage2b(
            tmp_path, _FIXTURE_DIR / "fixture_tier_0_ideal.json",
        )
        assert rc == 0
        out = _load_output(output_path)
        rb = out["rejection_breakdown"]
        # All 7 canonical keys must always be present.
        expected_keys = {
            "lifecycle_not_pending_backtest",
            "theme_is_momentum",
            "factor_count_out_of_range",
            "no_cross_operator",
            "rsi14_is_sole_factor",
            "position_out_of_range",
            "thin_theme_momentum_bleed",
        }
        assert set(rb.keys()) == expected_keys
        # Fixture intentionally includes a momentum-theme call, a
        # proposer_invalid_dsl lifecycle, and one out-of-range position.
        assert rb["theme_is_momentum"] >= 1
        assert rb["lifecycle_not_pending_backtest"] >= 1
        assert rb["position_out_of_range"] >= 1

    def test_tier_0_pool_sizes_reflect_fixture(self, tmp_path):
        rc, output_path, _, _ = _run_stage2b(
            tmp_path, _FIXTURE_DIR / "fixture_tier_0_ideal.json",
        )
        assert rc == 0
        out = _load_output(output_path)
        fixture_payload = json.loads(
            (_FIXTURE_DIR / "fixture_tier_0_ideal.json").read_text(
                encoding="utf-8",
            ),
        )
        assert out["pool_size_total"] == len(fixture_payload["calls"])
        assert out["pool_size_passing_per_candidate_criteria"] >= 5

    def test_tier_0_mechanical_rationale(self, tmp_path):
        rc, output_path, _, _ = _run_stage2b(
            tmp_path, _FIXTURE_DIR / "fixture_tier_0_ideal.json",
        )
        assert rc == 0
        out = _load_output(output_path)
        for c in out["candidates"]:
            expected = (
                f"fills {c['position_bucket']} bucket; "
                f"adds theme {c['theme']}; "
                f"label={c['d7a_b_relationship_label']}"
            )
            assert c["selection_rationale"] == expected


# ---------------------------------------------------------------------------
# Tier 1 — same-theme agreement/divergence pair
# ---------------------------------------------------------------------------


class TestTier1SameThemePair:
    def test_tier_1_success(self, tmp_path):
        rc, output_path, _, stderr = _run_stage2b(
            tmp_path, _FIXTURE_DIR / "fixture_tier_1_same_theme_pair.json",
        )
        assert rc == 0, stderr
        out = _load_output(output_path)
        assert out["selection_tier"] == 1
        assert len(out["selection_warnings"]) >= 1
        w = out["selection_warnings"][0]
        assert w["tier"] == 1
        assert w["constraint_relaxed"] == (
            "divergence_pair_different_themes_preference"
        )
        assert "pool_size_searched" in w
        assert "pool_breakdown_by_label" in w
        assert set(w["pool_breakdown_by_label"].keys()) == {
            "agreement_expected", "divergence_expected", "neutral",
        }

    def test_tier_1_hard_constraints_still_satisfied(self, tmp_path):
        rc, output_path, _, _ = _run_stage2b(
            tmp_path, _FIXTURE_DIR / "fixture_tier_1_same_theme_pair.json",
        )
        assert rc == 0
        out = _load_output(output_path)
        cands = out["candidates"]
        assert len(cands) == 5
        assert len({c["theme"] for c in cands}) >= 3
        assert {c["position_bucket"] for c in cands} == {
            "early", "mid", "late",
        }

    def test_tier_1_has_agreement_and_divergence(self, tmp_path):
        rc, output_path, _, _ = _run_stage2b(
            tmp_path, _FIXTURE_DIR / "fixture_tier_1_same_theme_pair.json",
        )
        assert rc == 0
        out = _load_output(output_path)
        labels = [c["d7a_b_relationship_label"] for c in out["candidates"]]
        assert any(lb == "agreement_expected" for lb in labels)
        assert any(lb == "divergence_expected" for lb in labels)


# ---------------------------------------------------------------------------
# Tier 2 — divergence coverage dropped
# ---------------------------------------------------------------------------


class TestTier2NoDivergence:
    def test_tier_2_success(self, tmp_path):
        rc, output_path, _, stderr = _run_stage2b(
            tmp_path, _FIXTURE_DIR / "fixture_tier_2_no_divergence.json",
        )
        assert rc == 0, stderr
        out = _load_output(output_path)
        assert out["selection_tier"] == 2
        assert len(out["selection_warnings"]) >= 1

    def test_tier_2_warning_payload(self, tmp_path):
        rc, output_path, _, _ = _run_stage2b(
            tmp_path, _FIXTURE_DIR / "fixture_tier_2_no_divergence.json",
        )
        assert rc == 0
        out = _load_output(output_path)
        assert any(
            w["constraint_relaxed"] == "divergence_coverage"
            for w in out["selection_warnings"]
        )
        w = [
            w for w in out["selection_warnings"]
            if w["constraint_relaxed"] == "divergence_coverage"
        ][0]
        assert w["tier"] == 2
        assert w["hard_constraint_constrained"] is True
        assert set(w["pool_breakdown_by_label"].keys()) == {
            "agreement_expected", "divergence_expected", "neutral",
        }


# ---------------------------------------------------------------------------
# Hard fails
# ---------------------------------------------------------------------------


class TestHardFailPoolTooSmall:
    def test_hard_fail_pool_too_small_exits_nonzero(self, tmp_path):
        rc, output_path, _, stderr = _run_stage2b(
            tmp_path,
            _FIXTURE_DIR / "fixture_hard_fail_pool_too_small.json",
        )
        assert rc == 1
        assert not output_path.exists()
        assert (
            "only" in stderr
            and "pass per-candidate criteria" in stderr
        )
        assert "need >= 5" in stderr
        assert "Breakdown" in stderr


class TestHardFailEmptyLateBucket:
    def test_hard_fail_empty_late_bucket_exits_nonzero(self, tmp_path):
        rc, output_path, _, stderr = _run_stage2b(
            tmp_path,
            _FIXTURE_DIR / "fixture_hard_fail_empty_late_bucket.json",
        )
        assert rc == 1
        assert not output_path.exists()
        assert "position bucket late is empty" in stderr
        assert "Pool counts" in stderr


class TestHardFailFewThemes:
    def test_hard_fail_few_themes_exits_nonzero(self, tmp_path):
        rc, output_path, _, stderr = _run_stage2b(
            tmp_path,
            _FIXTURE_DIR / "fixture_hard_fail_few_themes.json",
        )
        assert rc == 1
        assert not output_path.exists()
        assert "distinct themes" in stderr
        assert ">= 3 themes" in stderr


# ---------------------------------------------------------------------------
# N=1 regression guard
# ---------------------------------------------------------------------------


class TestStage2aRegressionGuard:
    def test_n1_default_unchanged(self, tmp_path):
        """Stage 2a N=1 behavior must remain byte-identical."""
        batch_uuid = "stage2a-regression"
        artifacts_root, _ = _materialize_batch(
            tmp_path,
            _FIXTURE_DIR / "fixture_tier_0_ideal.json",
            batch_uuid=batch_uuid,
        )

        proc = subprocess.run(
            [
                sys.executable,
                str(_REPO_ROOT / "scripts" / "select_replay_candidate.py"),
                batch_uuid,
                "--artifacts-root", str(artifacts_root),
            ],
            capture_output=True,
            text=True,
            cwd=_REPO_ROOT,
        )
        assert proc.returncode == 0, proc.stderr
        # Stage 2a prints a single JSON blob to stdout.
        result = json.loads(proc.stdout)
        # Deterministic scan order (position asc, hash lexicographic)
        # surfaces the lowest-position passing candidate. Fixture's
        # lowest passing position is 15.
        assert result["position"] == 15
        # No Stage 2b output should be written in N=1 mode.
        assert not (tmp_path / "replay_candidates.json").exists()

    def test_n1_explicit_same_as_default(self, tmp_path):
        batch_uuid = "stage2a-explicit"
        artifacts_root, _ = _materialize_batch(
            tmp_path,
            _FIXTURE_DIR / "fixture_tier_0_ideal.json",
            batch_uuid=batch_uuid,
        )

        proc_default = subprocess.run(
            [
                sys.executable,
                str(_REPO_ROOT / "scripts" / "select_replay_candidate.py"),
                batch_uuid,
                "--artifacts-root", str(artifacts_root),
            ],
            capture_output=True,
            text=True,
            cwd=_REPO_ROOT,
        )
        proc_explicit = subprocess.run(
            [
                sys.executable,
                str(_REPO_ROOT / "scripts" / "select_replay_candidate.py"),
                batch_uuid,
                "--artifacts-root", str(artifacts_root),
                "--n", "1",
            ],
            capture_output=True,
            text=True,
            cwd=_REPO_ROOT,
        )
        assert proc_default.returncode == proc_explicit.returncode == 0
        assert proc_default.stdout == proc_explicit.stdout

    def test_invalid_n_rejected(self, tmp_path):
        proc = subprocess.run(
            [
                sys.executable,
                str(_REPO_ROOT / "scripts" / "select_replay_candidate.py"),
                "00000000-0000-0000-0000-000000000000",
                "--n", "3",
            ],
            capture_output=True,
            text=True,
            cwd=_REPO_ROOT,
        )
        assert proc.returncode != 0
        assert "invalid choice" in proc.stderr or "choose from" in proc.stderr


# ---------------------------------------------------------------------------
# Deterministic tie-break
# ---------------------------------------------------------------------------


class TestDeterministicTieBreak:
    def test_same_fixture_same_selection(self, tmp_path):
        """Two invocations on the same fixture return identical candidates."""
        fixture = _FIXTURE_DIR / "fixture_tier_0_ideal.json"

        rc1, out1, _, _ = _run_stage2b(
            tmp_path / "run1", fixture, output_name="r1.json",
        )
        rc2, out2, _, _ = _run_stage2b(
            tmp_path / "run2", fixture, output_name="r2.json",
        )
        assert rc1 == rc2 == 0
        a = _load_output(out1)
        b = _load_output(out2)
        # Timestamps may differ; compare the deterministic content.
        assert a["selection_tier"] == b["selection_tier"]
        assert a["candidates"] == b["candidates"]
        assert a["rejection_breakdown"] == b["rejection_breakdown"]


# ---------------------------------------------------------------------------
# Invariant: tier/warnings relationship
# ---------------------------------------------------------------------------


class TestTierWarningInvariants:
    def test_tier_0_has_empty_warnings(self, tmp_path):
        rc, output_path, _, _ = _run_stage2b(
            tmp_path, _FIXTURE_DIR / "fixture_tier_0_ideal.json",
        )
        assert rc == 0
        out = _load_output(output_path)
        if out["selection_tier"] == 0:
            assert out["selection_warnings"] == []

    def test_tier_gt_0_has_nonempty_warnings(self, tmp_path):
        rc, output_path, _, _ = _run_stage2b(
            tmp_path, _FIXTURE_DIR / "fixture_tier_1_same_theme_pair.json",
        )
        assert rc == 0
        out = _load_output(output_path)
        if out["selection_tier"] in (1, 2):
            assert len(out["selection_warnings"]) >= 1

    def test_tier_2_warning_mentions_divergence_coverage(self, tmp_path):
        rc, output_path, _, _ = _run_stage2b(
            tmp_path, _FIXTURE_DIR / "fixture_tier_2_no_divergence.json",
        )
        assert rc == 0
        out = _load_output(output_path)
        if out["selection_tier"] == 2:
            relaxed = [
                w["constraint_relaxed"] for w in out["selection_warnings"]
            ]
            assert "divergence_coverage" in relaxed


# ---------------------------------------------------------------------------
# Unit tests for the mechanical label logic
# ---------------------------------------------------------------------------


class TestRelationshipLabel:
    def test_prior_occurrences_returns_agreement(self):
        assert sel.compute_relationship_label(
            factor_set_prior_occurrences=1,
            f_current={"a", "b", "c"},
            f_priors=[{"a", "b", "c"}],
        ) == "agreement_expected"

    def test_zero_occurrences_zero_overlap_returns_divergence(self):
        assert sel.compute_relationship_label(
            factor_set_prior_occurrences=0,
            f_current={"a", "b", "c"},
            f_priors=[{"d", "e", "f"}],
        ) == "divergence_expected"

    def test_zero_occurrences_overlap_two_returns_divergence(self):
        assert sel.compute_relationship_label(
            factor_set_prior_occurrences=0,
            f_current={"a", "b", "c"},
            f_priors=[{"a", "b", "d"}],
        ) == "divergence_expected"

    def test_zero_occurrences_overlap_three_returns_neutral(self):
        assert sel.compute_relationship_label(
            factor_set_prior_occurrences=0,
            f_current={"a", "b", "c", "d"},
            f_priors=[{"a", "b", "c", "e"}],
        ) == "neutral"

    def test_zero_occurrences_large_overlap_returns_neutral(self):
        assert sel.compute_relationship_label(
            factor_set_prior_occurrences=0,
            f_current={"a", "b", "c", "d", "e"},
            f_priors=[{"a", "b", "c", "d", "f"}],
        ) == "neutral"

    def test_no_priors_and_zero_occurrences_is_divergence(self):
        assert sel.compute_relationship_label(
            factor_set_prior_occurrences=0,
            f_current={"a", "b", "c"},
            f_priors=[],
        ) == "divergence_expected"


# ---------------------------------------------------------------------------
# Unit tests for position bucketing
# ---------------------------------------------------------------------------


class TestPositionBucket:
    @pytest.mark.parametrize(
        "pos,bucket",
        [
            (10, "early"),
            (66, "early"),
            (67, "mid"),
            (100, "mid"),
            (133, "mid"),
            (134, "late"),
            (190, "late"),
        ],
    )
    def test_valid_buckets(self, pos, bucket):
        assert sel._position_bucket(pos) == bucket

    @pytest.mark.parametrize("pos", [-1, 0, 9, 191, 250, None])
    def test_out_of_range_returns_none(self, pos):
        assert sel._position_bucket(pos) is None

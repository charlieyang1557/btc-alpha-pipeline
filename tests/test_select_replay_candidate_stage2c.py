"""Tests for the D7 Stage 2c extension of the replay-candidate selector.

Stage 2c extends Stage 2b's N=5 path to select 20 replay candidates for
the full forensic sweep. Per-candidate criteria (the seven rules in
``passes_selection``) and ``STAGE2B_N_FACTORS_RANGE`` are inherited
verbatim. Stage 2c scales the cross-candidate layer:

* Hard constraints at all tiers: unique hashes, >=3 themes,
  >=5 per bucket, >=4 ``agreement_expected`` candidates.
* Soft tier ladder: Tier 0 (>=2 cross-theme divergences), Tier 1
  (single divergence OR same-theme-divergence pair), Tier 2
  (zero divergence; agreement floor still enforced).

Backward compatibility with N=1 and N=5 is asserted via smoke tests.
Tier 2 is exercised through an in-memory pool (with label overrides)
because the natural labelling rule always labels the pioneer
``divergence_expected``, making a zero-divergence pool unreachable from
any passing fixture.
"""

from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts import select_replay_candidate as sel


_REPO_ROOT = Path(__file__).resolve().parent.parent
_FIXTURE_DIR = Path(__file__).parent / "fixtures" / "stage2c_selection"
_STAGE2B_FIXTURE_DIR = Path(__file__).parent / "fixtures" / "stage2b_selection"


# ---------------------------------------------------------------------------
# Fixture helpers
# ---------------------------------------------------------------------------


def _response_with_cross(factors: list[str]) -> str:
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
    batch_uuid: str = "stage2c-fixture",
) -> tuple[Path, dict]:
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


def _run_stage2c(
    tmp_path: Path,
    fixture_path: Path,
    *,
    batch_uuid: str = "stage2c-fixture",
    output_name: str = "replay_candidates.json",
    stage2b_reference: Path | None = None,
) -> tuple[int, Path, str, str]:
    artifacts_root, _ = _materialize_batch(
        tmp_path, fixture_path, batch_uuid=batch_uuid,
    )
    output_path = tmp_path / output_name

    cmd = [
        sys.executable,
        str(_REPO_ROOT / "scripts" / "select_replay_candidate.py"),
        batch_uuid,
        "--artifacts-root", str(artifacts_root),
        "--n", "20",
        "--output", str(output_path),
    ]
    if stage2b_reference is not None:
        cmd += ["--stage2b-reference", str(stage2b_reference)]

    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=_REPO_ROOT,
    )
    return proc.returncode, output_path, proc.stdout, proc.stderr


def _load_output(output_path: Path) -> dict:
    return json.loads(output_path.read_text(encoding="utf-8"))


def _build_pool_from_fixture(fixture_path: Path, tmp_path: Path) -> dict:
    """Run build_eligible_pool against a fixture's materialized batch."""
    batch_uuid = "stage2c-pool-build"
    artifacts_root, payload = _materialize_batch(
        tmp_path, fixture_path, batch_uuid=batch_uuid,
    )
    batch_dir = artifacts_root / f"batch_{batch_uuid}"
    summary = {"calls": payload["calls"]}
    return sel.build_eligible_pool(
        summary, batch_dir=batch_dir, batch_uuid=batch_uuid,
    )


# ---------------------------------------------------------------------------
# Constants are pinned — widening any of these would invalidate downstream
# artifacts, so we assert the exact values here.
# ---------------------------------------------------------------------------


class TestStage2cConstants:
    def test_n_candidates_is_20(self):
        assert sel.STAGE2C_N_CANDIDATES == 20

    def test_themes_min_is_3(self):
        assert sel.STAGE2C_THEMES_MIN == 3

    def test_bucket_min_is_5(self):
        assert sel.STAGE2C_BUCKET_MIN == 5

    def test_agreement_floor_is_4(self):
        assert sel.STAGE2C_AGREEMENT_FLOOR == 4

    def test_tier_0_divergence_min_is_2(self):
        assert sel.STAGE2C_TIER_0_DIVERGENCE_MIN == 2

    def test_tier_1_divergence_min_is_1(self):
        assert sel.STAGE2C_TIER_1_DIVERGENCE_MIN == 1

    def test_stage2b_n_factors_range_reused_not_renamed(self):
        # CONTRACT BOUNDARY: Stage 2c shares Stage 2b's factor-count range.
        assert sel.STAGE2B_N_FACTORS_RANGE == (3, 7)
        # No parallel STAGE2C_N_FACTORS_RANGE should exist.
        assert not hasattr(sel, "STAGE2C_N_FACTORS_RANGE")

    def test_stage2c_default_output_path(self):
        assert sel.STAGE2C_DEFAULT_OUTPUT == Path(
            "docs/d7_stage2c/replay_candidates.json"
        )

    def test_stage2c_stage_label_and_version(self):
        assert sel.STAGE2C_STAGE_LABEL == "d7_stage2c"
        assert sel.STAGE2C_RECORD_VERSION == "1.0"


# ---------------------------------------------------------------------------
# Tier 0 — ideal selection
# ---------------------------------------------------------------------------


class TestTier0IdealSelection:
    def test_tier_0_success(self, tmp_path):
        rc, output_path, _, stderr = _run_stage2c(
            tmp_path, _FIXTURE_DIR / "fixture_tier_0_ideal.json",
        )
        assert rc == 0, stderr
        assert output_path.exists()

        out = _load_output(output_path)
        assert out["selection_tier"] == 0
        assert out["selection_warnings"] == []
        assert len(out["candidates"]) == 20

    def test_tier_0_output_invariants(self, tmp_path):
        rc, output_path, _, _ = _run_stage2c(
            tmp_path, _FIXTURE_DIR / "fixture_tier_0_ideal.json",
        )
        assert rc == 0

        out = _load_output(output_path)
        cands = out["candidates"]
        positions = [c["position"] for c in cands]
        assert positions == sorted(positions)
        assert [c["firing_order"] for c in cands] == list(range(1, 21))

        hashes = {c["hypothesis_hash"] for c in cands}
        assert len(hashes) == 20

        themes = {c["theme"] for c in cands}
        assert len(themes) >= 3

        buckets = {c["position_bucket"] for c in cands}
        assert buckets == {"early", "mid", "late"}

        bucket_counts = {b: 0 for b in ("early", "mid", "late")}
        for c in cands:
            bucket_counts[c["position_bucket"]] += 1
        for name in ("early", "mid", "late"):
            assert bucket_counts[name] >= 5

        labels = [c["d7a_b_relationship_label"] for c in cands]
        assert sum(lb == "agreement_expected" for lb in labels) >= 4
        assert sum(lb == "divergence_expected" for lb in labels) >= 2

    def test_tier_0_stage_label_and_version(self, tmp_path):
        rc, output_path, _, _ = _run_stage2c(
            tmp_path, _FIXTURE_DIR / "fixture_tier_0_ideal.json",
        )
        assert rc == 0
        out = _load_output(output_path)
        assert out["stage_label"] == "d7_stage2c"
        assert out["record_version"] == "1.0"
        assert out["batch_uuid"] == "stage2c-fixture"
        assert out["selection_timestamp_utc"].endswith("Z")

    def test_tier_0_cross_theme_divergence_seed(self, tmp_path):
        rc, output_path, _, _ = _run_stage2c(
            tmp_path, _FIXTURE_DIR / "fixture_tier_0_ideal.json",
        )
        assert rc == 0
        out = _load_output(output_path)
        divs = [
            c for c in out["candidates"]
            if c["d7a_b_relationship_label"] == "divergence_expected"
        ]
        assert len(divs) >= 2
        themes_in_divs = {c["theme"] for c in divs}
        assert len(themes_in_divs) >= 2


# ---------------------------------------------------------------------------
# Tier 1 — single divergence
# ---------------------------------------------------------------------------


class TestTier1SingleDivergence:
    def test_tier_1_single_divergence_success(self, tmp_path):
        rc, output_path, _, stderr = _run_stage2c(
            tmp_path,
            _FIXTURE_DIR / "fixture_tier_1_single_divergence.json",
        )
        assert rc == 0, stderr
        out = _load_output(output_path)
        assert out["selection_tier"] == 1
        assert len(out["candidates"]) == 20

    def test_tier_1_warning_attached(self, tmp_path):
        rc, output_path, _, _ = _run_stage2c(
            tmp_path,
            _FIXTURE_DIR / "fixture_tier_1_single_divergence.json",
        )
        assert rc == 0
        out = _load_output(output_path)
        warnings = out["selection_warnings"]
        assert len(warnings) == 1
        w = warnings[0]
        assert w["tier"] == 1
        assert w["constraint_relaxed"] == "cross_theme_divergence_coverage"
        assert "pool_breakdown_by_label" in w
        assert "pool_size_searched" in w

    def test_tier_1_exactly_one_divergence_seed(self, tmp_path):
        rc, output_path, _, _ = _run_stage2c(
            tmp_path,
            _FIXTURE_DIR / "fixture_tier_1_single_divergence.json",
        )
        assert rc == 0
        out = _load_output(output_path)
        divs = [
            c for c in out["candidates"]
            if c["d7a_b_relationship_label"] == "divergence_expected"
        ]
        assert len(divs) == 1


# ---------------------------------------------------------------------------
# Tier 1 — same-theme divergence pair
# ---------------------------------------------------------------------------


class TestTier1SameThemeDivergence:
    def test_tier_1_same_theme_divergence_success(self, tmp_path):
        rc, output_path, _, stderr = _run_stage2c(
            tmp_path,
            _FIXTURE_DIR / "fixture_tier_1_same_theme_divergence.json",
        )
        assert rc == 0, stderr
        out = _load_output(output_path)
        assert out["selection_tier"] == 1
        assert len(out["candidates"]) == 20

    def test_tier_1_same_theme_two_divergences_same_theme(self, tmp_path):
        rc, output_path, _, _ = _run_stage2c(
            tmp_path,
            _FIXTURE_DIR / "fixture_tier_1_same_theme_divergence.json",
        )
        assert rc == 0
        out = _load_output(output_path)
        divs = [
            c for c in out["candidates"]
            if c["d7a_b_relationship_label"] == "divergence_expected"
        ]
        assert len(divs) == 2
        assert divs[0]["theme"] == divs[1]["theme"]

    def test_tier_1_same_theme_warning_shape(self, tmp_path):
        rc, output_path, _, _ = _run_stage2c(
            tmp_path,
            _FIXTURE_DIR / "fixture_tier_1_same_theme_divergence.json",
        )
        assert rc == 0
        out = _load_output(output_path)
        w = out["selection_warnings"][0]
        assert w["tier"] == 1
        assert w["constraint_relaxed"] == "cross_theme_divergence_coverage"


# ---------------------------------------------------------------------------
# Tier 2 — via in-memory label override (natural pools cannot produce 0
# divergences because the pioneer is always labelled divergence_expected).
# ---------------------------------------------------------------------------


class TestTier2NoDivergence:
    @staticmethod
    def _neutralize_divergences(pool: list[dict]) -> list[dict]:
        """Override divergence labels to agreement to exercise Tier 2."""
        out = []
        for c in pool:
            c2 = copy.deepcopy(c)
            if c2["d7a_b_relationship_label"] == "divergence_expected":
                c2["d7a_b_relationship_label"] = "agreement_expected"
            out.append(c2)
        return out

    def test_tier_2_select_stage2c_success(self, tmp_path):
        eligible = _build_pool_from_fixture(
            _FIXTURE_DIR / "fixture_tier_2_no_divergence.json", tmp_path,
        )
        pool = self._neutralize_divergences(eligible["pool"])
        assert all(
            c["d7a_b_relationship_label"] != "divergence_expected"
            for c in pool
        )
        result = sel.select_stage2c(pool)
        assert result["status"] == "ok"
        assert result["tier"] == 2
        assert len(result["candidates"]) == 20

    def test_tier_2_warning_flags_hard_constraint_constrained(self, tmp_path):
        eligible = _build_pool_from_fixture(
            _FIXTURE_DIR / "fixture_tier_2_no_divergence.json", tmp_path,
        )
        pool = self._neutralize_divergences(eligible["pool"])
        result = sel.select_stage2c(pool)
        assert result["status"] == "ok"
        warnings = result["warnings"]
        assert len(warnings) == 1
        w = warnings[0]
        assert w["tier"] == 2
        assert w["constraint_relaxed"] == "divergence_coverage"
        assert w["hard_constraint_constrained"] is True

    def test_tier_2_zero_divergences_but_agreement_floor_held(self, tmp_path):
        eligible = _build_pool_from_fixture(
            _FIXTURE_DIR / "fixture_tier_2_no_divergence.json", tmp_path,
        )
        pool = self._neutralize_divergences(eligible["pool"])
        result = sel.select_stage2c(pool)
        assert result["status"] == "ok"
        labels = [
            c["d7a_b_relationship_label"] for c in result["candidates"]
        ]
        assert sum(lb == "divergence_expected" for lb in labels) == 0
        assert sum(lb == "agreement_expected" for lb in labels) >= 4


# ---------------------------------------------------------------------------
# Hard-fail paths
# ---------------------------------------------------------------------------


class TestHardFailPaths:
    def test_hard_fail_pool_too_small(self, tmp_path):
        rc, output_path, _, stderr = _run_stage2c(
            tmp_path,
            _FIXTURE_DIR / "fixture_hard_fail_pool_too_small.json",
        )
        assert rc == 1
        assert not output_path.exists()
        assert "candidates pass" in stderr or "per-candidate" in stderr

    def test_hard_fail_bucket_empty(self, tmp_path):
        rc, output_path, _, stderr = _run_stage2c(
            tmp_path,
            _FIXTURE_DIR / "fixture_hard_fail_bucket_empty.json",
        )
        assert rc == 1
        assert not output_path.exists()
        assert "bucket" in stderr.lower()

    def test_hard_fail_few_themes(self, tmp_path):
        rc, output_path, _, stderr = _run_stage2c(
            tmp_path,
            _FIXTURE_DIR / "fixture_hard_fail_few_themes.json",
        )
        assert rc == 1
        assert not output_path.exists()
        assert "themes" in stderr.lower()

    def test_hard_fail_agreement_floor(self, tmp_path):
        rc, output_path, _, stderr = _run_stage2c(
            tmp_path,
            _FIXTURE_DIR / "fixture_hard_fail_agreement_floor.json",
        )
        assert rc == 1
        assert not output_path.exists()
        assert "agreement" in stderr.lower()


# ---------------------------------------------------------------------------
# Backward compatibility — N=1 and N=5 must be byte-identical to pre-2c.
# ---------------------------------------------------------------------------


class TestBackwardCompatibility:
    def test_n1_smoke_against_stage2b_fixture(self, tmp_path):
        artifacts_root, _ = _materialize_batch(
            tmp_path,
            _STAGE2B_FIXTURE_DIR / "fixture_tier_0_ideal.json",
            batch_uuid="stage2c-n1-regression",
        )
        proc = subprocess.run(
            [
                sys.executable,
                str(_REPO_ROOT / "scripts" / "select_replay_candidate.py"),
                "stage2c-n1-regression",
                "--artifacts-root", str(artifacts_root),
                "--n", "1",
            ],
            capture_output=True,
            text=True,
            cwd=_REPO_ROOT,
        )
        assert proc.returncode == 0, proc.stderr
        payload = json.loads(proc.stdout)
        assert "position" in payload
        assert "hypothesis_hash" in payload

    def test_n5_smoke_against_stage2b_fixture(self, tmp_path):
        artifacts_root, _ = _materialize_batch(
            tmp_path,
            _STAGE2B_FIXTURE_DIR / "fixture_tier_0_ideal.json",
            batch_uuid="stage2c-n5-regression",
        )
        output_path = tmp_path / "n5.json"
        proc = subprocess.run(
            [
                sys.executable,
                str(_REPO_ROOT / "scripts" / "select_replay_candidate.py"),
                "stage2c-n5-regression",
                "--artifacts-root", str(artifacts_root),
                "--n", "5",
                "--output", str(output_path),
            ],
            capture_output=True,
            text=True,
            cwd=_REPO_ROOT,
        )
        assert proc.returncode == 0, proc.stderr
        out = json.loads(output_path.read_text(encoding="utf-8"))
        assert out["stage_label"] == "d7_stage2b"
        assert len(out["candidates"]) == 5


# ---------------------------------------------------------------------------
# Argparse --n rejection
# ---------------------------------------------------------------------------


class TestArgparseChoices:
    def test_n10_rejected(self, tmp_path):
        proc = subprocess.run(
            [
                sys.executable,
                str(_REPO_ROOT / "scripts" / "select_replay_candidate.py"),
                "fake-uuid",
                "--n", "10",
            ],
            capture_output=True,
            text=True,
            cwd=_REPO_ROOT,
        )
        assert proc.returncode != 0
        assert "invalid choice" in proc.stderr or "choices" in proc.stderr.lower()

    def test_n100_rejected(self, tmp_path):
        proc = subprocess.run(
            [
                sys.executable,
                str(_REPO_ROOT / "scripts" / "select_replay_candidate.py"),
                "fake-uuid",
                "--n", "100",
            ],
            capture_output=True,
            text=True,
            cwd=_REPO_ROOT,
        )
        assert proc.returncode != 0
        assert "invalid choice" in proc.stderr or "choices" in proc.stderr.lower()


# ---------------------------------------------------------------------------
# Stdout summary format
# ---------------------------------------------------------------------------


class TestStdoutSummary:
    def test_stdout_contains_five_summary_lines(self, tmp_path):
        rc, _, stdout, _ = _run_stage2c(
            tmp_path, _FIXTURE_DIR / "fixture_tier_0_ideal.json",
        )
        assert rc == 0
        assert "[select] wrote" in stdout
        assert "[select] positions:" in stdout
        assert "[select] themes:" in stdout
        assert "[select] labels:" in stdout
        assert "[select] stage2b overlap:" in stdout

    def test_stdout_positions_sorted(self, tmp_path):
        rc, output_path, stdout, _ = _run_stage2c(
            tmp_path, _FIXTURE_DIR / "fixture_tier_0_ideal.json",
        )
        assert rc == 0
        out = _load_output(output_path)
        expected_positions = [c["position"] for c in out["candidates"]]
        for line in stdout.splitlines():
            if line.startswith("[select] positions:"):
                assert str(expected_positions) in line


# ---------------------------------------------------------------------------
# Stage 2b overlap computation
# ---------------------------------------------------------------------------


class TestStage2bOverlap:
    def test_overlap_zero_when_reference_missing(self, tmp_path):
        rc, output_path, stdout, _ = _run_stage2c(
            tmp_path,
            _FIXTURE_DIR / "fixture_tier_0_ideal.json",
            stage2b_reference=tmp_path / "nonexistent.json",
        )
        assert rc == 0
        out = _load_output(output_path)
        assert out["stage2b_overlap_count"] == 0
        assert out["stage2b_overlap_positions"] == []

    def test_overlap_counts_matching_hashes(self, tmp_path):
        stage2b_ref = tmp_path / "stage2b_ref.json"
        stage2b_ref.write_text(json.dumps({
            "candidates": [
                {"hypothesis_hash": "h010", "position": 10},
                {"hypothesis_hash": "h045", "position": 45},
                {"hypothesis_hash": "h_not_in_stage2c", "position": 999},
            ],
        }), encoding="utf-8")
        rc, output_path, _, _ = _run_stage2c(
            tmp_path,
            _FIXTURE_DIR / "fixture_tier_0_ideal.json",
            stage2b_reference=stage2b_ref,
        )
        assert rc == 0
        out = _load_output(output_path)
        # Both h010 (pos 10) and h045 (pos 45) are in the tier-0 pool and
        # are strong candidates; whichever subset the selector picks, any
        # overlap positions must come from the tier-0 fixture's positions.
        valid_positions = {
            10, 15, 20, 25, 30, 35, 40, 45,
            70, 75, 80, 85, 90, 95,
            140, 145, 150, 155, 160, 165,
        }
        for pos in out["stage2b_overlap_positions"]:
            assert pos in valid_positions
        assert out["stage2b_overlap_count"] == len(
            out["stage2b_overlap_positions"]
        )
        assert out["stage2b_overlap_positions"] == sorted(
            out["stage2b_overlap_positions"]
        )

    def test_overlap_robust_to_malformed_reference(self, tmp_path):
        stage2b_ref = tmp_path / "malformed.json"
        stage2b_ref.write_text("{not valid json", encoding="utf-8")
        rc, output_path, _, _ = _run_stage2c(
            tmp_path,
            _FIXTURE_DIR / "fixture_tier_0_ideal.json",
            stage2b_reference=stage2b_ref,
        )
        assert rc == 0
        out = _load_output(output_path)
        assert out["stage2b_overlap_count"] == 0
        assert out["stage2b_overlap_positions"] == []


# ---------------------------------------------------------------------------
# Theme / label counts in selected output
# ---------------------------------------------------------------------------


class TestThemeLabelCounts:
    def test_theme_counts_sum_to_20(self, tmp_path):
        rc, output_path, _, _ = _run_stage2c(
            tmp_path, _FIXTURE_DIR / "fixture_tier_0_ideal.json",
        )
        assert rc == 0
        out = _load_output(output_path)
        tc = out["theme_counts_in_selected"]
        assert sum(tc.values()) == 20
        assert len(tc) >= 3

    def test_label_counts_sum_to_20_and_have_three_keys(self, tmp_path):
        rc, output_path, _, _ = _run_stage2c(
            tmp_path, _FIXTURE_DIR / "fixture_tier_0_ideal.json",
        )
        assert rc == 0
        out = _load_output(output_path)
        lc = out["label_counts_in_selected"]
        assert set(lc.keys()) == {
            "agreement_expected", "divergence_expected", "neutral",
        }
        assert sum(lc.values()) == 20
        assert lc["agreement_expected"] >= 4


# ---------------------------------------------------------------------------
# Rationale rendering — adds theme / retains theme
# ---------------------------------------------------------------------------


class TestRationaleRendering:
    def test_first_occurrence_uses_adds_theme(self, tmp_path):
        rc, output_path, _, _ = _run_stage2c(
            tmp_path, _FIXTURE_DIR / "fixture_tier_0_ideal.json",
        )
        assert rc == 0
        out = _load_output(output_path)
        cands = out["candidates"]
        seen_themes: set[str] = set()
        for c in cands:
            rationale = c["selection_rationale"]
            if c["theme"] in seen_themes:
                assert f"retains theme {c['theme']}" in rationale
            else:
                assert f"adds theme {c['theme']}" in rationale
            seen_themes.add(c["theme"])

    def test_rationale_contains_bucket_and_label(self, tmp_path):
        rc, output_path, _, _ = _run_stage2c(
            tmp_path, _FIXTURE_DIR / "fixture_tier_0_ideal.json",
        )
        assert rc == 0
        out = _load_output(output_path)
        for c in out["candidates"]:
            rationale = c["selection_rationale"]
            assert f"fills {c['position_bucket']} bucket" in rationale
            assert f"label={c['d7a_b_relationship_label']}" in rationale

    def test_rationale_unit_adds_theme(self):
        cand = {
            "theme": "mean_reversion",
            "position_bucket": "early",
            "d7a_b_relationship_label": "divergence_expected",
        }
        rationale = sel._render_rationale_stage2c(cand, candidates_before=[])
        assert rationale == (
            "fills early bucket; adds theme mean_reversion; "
            "label=divergence_expected"
        )

    def test_rationale_unit_retains_theme(self):
        prior = {
            "theme": "mean_reversion",
            "position_bucket": "early",
            "d7a_b_relationship_label": "agreement_expected",
        }
        cand = {
            "theme": "mean_reversion",
            "position_bucket": "mid",
            "d7a_b_relationship_label": "agreement_expected",
        }
        rationale = sel._render_rationale_stage2c(
            cand, candidates_before=[prior],
        )
        assert rationale == (
            "fills mid bucket; retains theme mean_reversion; "
            "label=agreement_expected"
        )


# ---------------------------------------------------------------------------
# Deterministic tie-break
# ---------------------------------------------------------------------------


class TestDeterministicTieBreak:
    def test_two_invocations_produce_identical_output(self, tmp_path):
        fixture = _FIXTURE_DIR / "fixture_tier_0_ideal.json"

        rc1, out1, _, _ = _run_stage2c(
            tmp_path, fixture, batch_uuid="tie-a",
            output_name="a.json",
        )
        assert rc1 == 0
        rc2, out2, _, _ = _run_stage2c(
            tmp_path, fixture, batch_uuid="tie-b",
            output_name="b.json",
        )
        assert rc2 == 0

        a = _load_output(out1)
        b = _load_output(out2)

        # batch_uuid / timestamp differ; everything else should match.
        for k in (
            "batch_uuid",
            "selection_timestamp_utc",
        ):
            a.pop(k)
            b.pop(k)
        assert a == b

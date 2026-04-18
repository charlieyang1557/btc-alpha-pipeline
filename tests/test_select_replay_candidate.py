"""Tests for the D7 Stage 2a replay-candidate selection script.

These tests pin two properties that are easy to drift without noticing:

    1. The script's scan order is deterministic (position asc, then
       hypothesis_hash lexicographic). If this drifts, the replay
       candidate chosen on Charlie's machine may not match the one
       chosen in CI.

    2. A zero-match summary exits non-zero with a rejection-reason
       breakdown on stderr. This is the contract the live-call
       entrypoint relies on to refuse to run.

The script's import-time wiring (sys.path guard + canonical thin-theme
predicate) is exercised indirectly via the test harness's import; a
broken guard would fail collection.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts import select_replay_candidate as sel


_REPO_ROOT = Path(__file__).resolve().parent.parent


def _write_minimal_summary(
    batch_dir: Path,
    calls: list[dict],
    summary_name: str = "stage2d_summary.json",
) -> Path:
    """Write a minimal stage2d-style summary with the given calls."""
    batch_dir.mkdir(parents=True, exist_ok=True)
    summary = {"calls": calls}
    summary_path = batch_dir / summary_name
    summary_path.write_text(json.dumps(summary), encoding="utf-8")
    return summary_path


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


def _make_call(
    *,
    position: int,
    hypothesis_hash: str,
    theme: str = "mean_reversion",
    factors_used: list[str] | None = None,
    default_momentum_factors_used: list[str] | None = None,
    lifecycle_state: str = "pending_backtest",
) -> dict:
    """Build a minimal per-call summary record passing criteria 1-6."""
    return {
        "position": position,
        "hypothesis_hash": hypothesis_hash,
        "theme": theme,
        "lifecycle_state": lifecycle_state,
        "factors_used": factors_used or ["rsi_14", "atr_14", "sma_50"],
        "default_momentum_factors_used": default_momentum_factors_used or [],
        "contains_default_momentum_factor": bool(default_momentum_factors_used),
    }


# ---------------------------------------------------------------------------
# Determinism: scan order is pinned to (position, hypothesis_hash)
# ---------------------------------------------------------------------------


class TestSelectionDeterministicOrder:
    def test_selection_deterministic_order(self, tmp_path):
        """Same summary, two scan orders → same candidate returned.

        Build three candidates that all pass every criterion, write them
        to the summary in shuffled order, and confirm the script picks
        the lowest-position one. Then shuffle the input differently and
        confirm the picked candidate is identical.
        """
        batch_uuid = "det-test-0001"
        batch_dir = tmp_path / f"batch_{batch_uuid}"

        # Three valid candidates at ascending positions.
        candidates = [
            _make_call(position=50, hypothesis_hash="cc"),
            _make_call(position=20, hypothesis_hash="aa"),
            _make_call(position=20, hypothesis_hash="bb"),
        ]

        # Write shuffled order #1.
        _write_minimal_summary(batch_dir, calls=list(reversed(candidates)))
        for call in candidates:
            resp_path = batch_dir / f"attempt_{call['position']:04d}_response.txt"
            resp_path.write_text(
                _response_with_cross(call["factors_used"]), encoding="utf-8",
            )

        pick1 = sel.select_candidate(
            batch_uuid, artifacts_root=tmp_path,
        )
        assert pick1 is not None
        assert pick1["position"] == 20
        assert pick1["hypothesis_hash"] == "aa"

        # Write shuffled order #2 (different permutation).
        _write_minimal_summary(
            batch_dir,
            calls=[candidates[2], candidates[0], candidates[1]],
        )
        pick2 = sel.select_candidate(
            batch_uuid, artifacts_root=tmp_path,
        )
        assert pick2 is not None
        assert pick2["position"] == 20
        assert pick2["hypothesis_hash"] == "aa"

        assert pick1["hypothesis_hash"] == pick2["hypothesis_hash"]


# ---------------------------------------------------------------------------
# Zero-matches exit contract
# ---------------------------------------------------------------------------


class TestSelectionZeroMatchesExitsNonzero:
    def test_selection_zero_matches_exits_nonzero(self, tmp_path):
        """No candidate passes criteria → main() calls sys.exit(1)."""
        batch_uuid = "zero-test-0001"
        batch_dir = tmp_path / f"batch_{batch_uuid}"

        # One call that fails criterion 1 (lifecycle_state != pending_backtest).
        calls = [
            _make_call(
                position=15,
                hypothesis_hash="zz",
                lifecycle_state="proposer_invalid_dsl",
            ),
        ]
        _write_minimal_summary(batch_dir, calls=calls)

        result = sel.select_candidate(batch_uuid, artifacts_root=tmp_path)
        assert result is None

        # End-to-end: invoking main() with a None result calls sys.exit(1).
        proc = subprocess.run(
            [
                sys.executable,
                str(_REPO_ROOT / "scripts" / "select_replay_candidate.py"),
                batch_uuid,
                "--artifacts-root", str(tmp_path),
            ],
            capture_output=True,
            text=True,
            cwd=_REPO_ROOT,
        )
        assert proc.returncode == 1, proc.stderr
        assert "no candidate passed all criteria" in proc.stderr


# ---------------------------------------------------------------------------
# Thin-theme momentum-bleed routing: selection script must agree with
# the canonical predicate for all realistic per-call records.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "theme,momentum_list,expect_triggers",
    [
        ("volume_divergence", [], False),
        ("volume_divergence", ["return_24h"], False),
        ("volume_divergence", ["return_24h", "return_7d"], True),
        ("calendar_effect", ["return_24h", "return_7d", "rsi_14"], True),
        ("volatility_regime", ["return_24h"], False),
        ("momentum", ["return_24h", "return_7d", "roc_14"], False),
        ("mean_reversion", ["return_24h", "return_7d"], False),
    ],
)
def test_selection_thin_theme_routes_through_canonical_predicate(
    theme, momentum_list, expect_triggers,
):
    """Selection wrapper returns identical answer to the canonical predicate."""
    call = _make_call(
        position=10,
        hypothesis_hash="xx",
        theme=theme,
        default_momentum_factors_used=momentum_list,
    )
    actual = sel._call_would_trigger_thin_theme_momentum_bleed(call)
    assert actual is expect_triggers

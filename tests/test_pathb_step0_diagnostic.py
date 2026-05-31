# tests/test_pathb_step0_diagnostic.py
"""Step 0 read-only diagnostic re-score: Path B namespace, guarded, no side effects."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

import scripts.pathb_step0_diagnostic as step0
import backtest.tier6_dsr as t6

COHORT = "phase4_forward_2026_15bps_v1"


def _dir_mtimes(d: Path) -> dict[str, float]:
    return {str(p): p.stat().st_mtime_ns for p in sorted(d.rglob("*")) if p.is_file()}


def test_default_output_is_pathb_namespace_not_cohort_dir():
    # The Path B re-score namespace must NOT be the sealed cohort dir.
    assert step0.DEFAULT_PATHB_STEP0_DIR.name == "pathb_step0_diagnostic_v1"
    assert step0.DEFAULT_PATHB_STEP0_DIR != t6.HOLDOUT_DIR
    assert t6.DEFAULT_COHORT not in step0.DEFAULT_PATHB_STEP0_DIR.parts


def test_run_step0_is_read_only_and_calls_both_guards(tmp_path, monkeypatch):
    calls = {"eval_guard": 0, "cost_anchor": 0, "wf_guard": 0}

    def fake_eval_guard(summary, *, artifact_path=None):
        calls["eval_guard"] += 1

    def fake_wf_guard(summary, *, artifact_path=None):  # must NOT be used
        calls["wf_guard"] += 1

    def fake_cost(summary_dict):
        calls["cost_anchor"] += 1

    # A minimal cohort fixture (single candidate) wired through tier6 internals.
    cohort_dir = tmp_path / "cohort"
    cohort_dir.mkdir()
    (cohort_dir / "holdout_summary.json").write_text(json.dumps({"ok": True}))
    df = pd.DataFrame([{"hypothesis_hash": "abc", "name": "h", "theme": "t"}])

    monkeypatch.setattr(step0, "check_evaluation_semantics_or_raise", fake_eval_guard)
    monkeypatch.setattr(step0, "check_wf_semantics_or_raise", fake_wf_guard)
    monkeypatch.setattr(step0, "_assert_cost_anchor_15bps_spot", fake_cost)
    monkeypatch.setattr(step0, "_read_cohort_csv", lambda holdout_dir=None: df)

    def fake_eval_one(h, frame, n_star, holdout_dir):
        return {"hypothesis_hash": h, "pass_B": False, "dsr_statistic_B": -1.0}

    monkeypatch.setattr(step0, "_evaluate_one", fake_eval_one)

    before = _dir_mtimes(cohort_dir)
    result = step0.run_step0(
        cohort_dir=cohort_dir,
        out_dir=tmp_path / "out",
        n_star=step0.PATHB_N_STAR,
        write=True,
    )
    after = _dir_mtimes(cohort_dir)

    # Forward-holdout single-run guard (NOT the WF guard) fired exactly once.
    assert calls["eval_guard"] == 1
    assert calls["wf_guard"] == 0
    assert calls["cost_anchor"] == 1
    # Read-only: cohort dir bytes + mtimes unchanged; no promotion side effect.
    assert before == after
    assert result["promotion_side_effect"] is False
    assert result["read_only"] is True


def test_pathb_n_star_default_is_3():
    assert step0.PATHB_N_STAR == 3


def test_run_step0_refuses_writing_into_sealed_dir(tmp_path, monkeypatch):
    cohort_dir = tmp_path / "cohort"
    cohort_dir.mkdir()
    (cohort_dir / "holdout_summary.json").write_text(json.dumps({"ok": True}))
    monkeypatch.setattr(step0, "check_evaluation_semantics_or_raise", lambda *a, **k: None)
    monkeypatch.setattr(step0, "_assert_cost_anchor_15bps_spot", lambda *a, **k: None)
    monkeypatch.setattr(step0, "_read_cohort_csv", lambda holdout_dir=None: pd.DataFrame([{"hypothesis_hash": "a"}]))
    monkeypatch.setattr(step0, "_evaluate_one", lambda h, frame, n_star, holdout_dir: {"hypothesis_hash": h})
    # out_dir == the sealed tier6_dsr_v1 dir -> refuse
    with pytest.raises(ValueError, match="REFUSING|sealed"):
        step0.run_step0(cohort_dir=cohort_dir, out_dir=t6.DEFAULT_OUT_DIR, write=True)
    # out_dir == cohort_dir (read-only input) -> refuse
    with pytest.raises(ValueError, match="REFUSING|sealed"):
        step0.run_step0(cohort_dir=cohort_dir, out_dir=cohort_dir, write=True)

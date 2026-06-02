# tests/test_pathd_moments.py
"""Path D moments: cohort CSV assembly and tier6 integrity gate roundtrip.

Adapted from tests/test_pathc_moments.py. Verifies that build_cohort_csv
excludes degenerate rows, and that load_pathd_moments uses the tier6 integrity gate.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from backtest.pathd_moments import build_cohort_csv, load_pathd_moments


def _row(hh: str, degenerate: bool = False) -> dict:
    return {
        "hypothesis_hash": hh,
        "name": hh,
        "theme": "pathd",
        "T_obs": 100,
        "gamma3": None if degenerate else 0.1,
        "gamma4": None if degenerate else 3.0,
        "returns_per_bar_sha256": "abc" * 20,
        "holdout_total_trades": 0 if degenerate else 10,
        "holdout_sharpe": 0.0 if degenerate else 0.3,
        **({"degenerate": True} if degenerate else {}),
    }


def test_build_cohort_csv_excludes_degenerate_rows(tmp_path):
    rows = [_row("h1"), _row("h2_degen", degenerate=True), _row("h3")]
    df = build_cohort_csv(rows, tmp_path)
    # Only non-degenerate rows in the CSV.
    assert len(df) == 2
    assert "h2_degen" not in df["hypothesis_hash"].values


def test_build_cohort_csv_writes_file(tmp_path):
    rows = [_row("h1"), _row("h2")]
    build_cohort_csv(rows, tmp_path)
    csv_path = tmp_path / "holdout_results.csv"
    assert csv_path.exists()
    read_back = pd.read_csv(csv_path)
    assert len(read_back) == 2


def test_build_cohort_csv_all_degenerate_writes_empty(tmp_path):
    rows = [_row("h1", degenerate=True), _row("h2", degenerate=True)]
    df = build_cohort_csv(rows, tmp_path)
    assert df.empty
    csv_path = tmp_path / "holdout_results.csv"
    assert csv_path.exists()


def test_load_pathd_moments_uses_tier6_integrity_gate(tmp_path, monkeypatch):
    """load_pathd_moments must call load_candidate_moments (the integrity-gated loader)."""
    import backtest.pathd_moments as pm

    calls = []

    def _mock_lcm(hypothesis_hash, df, holdout_dir):
        calls.append(hypothesis_hash)
        return object()  # dummy CandidateMoments-like

    monkeypatch.setattr(pm, "load_candidate_moments", _mock_lcm)
    df = pd.DataFrame([{"hypothesis_hash": "h1", "name": "h1", "theme": "pathd"}])
    pm.load_pathd_moments(["h1"], df, tmp_path)
    assert "h1" in calls, "load_pathd_moments must route through load_candidate_moments"

# tests/test_pathb_moments.py
"""Path B moments loader integrity tests."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from backtest.pathb_moments import build_cohort_csv, load_pathb_moments


def _write_candidate(cohort: Path, h: str) -> dict:
    """Write a minimal dead-18-layout candidate dir and return the CSV row dict."""
    cand = cohort / h
    cand.mkdir(parents=True)
    rng = np.random.default_rng(0)
    r = pd.Series(np.r_[np.nan, rng.normal(0, 0.01, 199)])
    pd.DataFrame({"return": r}).to_parquet(cand / "returns_per_bar.parquet")
    sha = hashlib.sha256((cand / "returns_per_bar.parquet").read_bytes()).hexdigest()
    rf = r[np.isfinite(r)]
    from scipy.stats import kurtosis, skew
    (cand / "holdout_summary.json").write_text(json.dumps({
        "evaluation_semantics": "single_run_holdout_v1",
        "engine_commit": "eb1c87f",
        "engine_corrected_lineage": "wf-corrected-v1",
        "lineage_check": "passed",
        "current_git_sha": "x",
        "artifact_schema_version": "phase2c_8_1",
        "regime_key": "evaluation_regimes.eval_2020_v1",
        "regime_label": "eval_2020_v1",
    }))
    return {
        "hypothesis_hash": h,
        "name": "pathb_h1",
        "theme": "pathb",
        "T_obs": int(len(rf)),
        "gamma3": float(skew(rf, bias=True)),
        "gamma4": float(kurtosis(rf, fisher=False, bias=True)),
        "returns_per_bar_sha256": sha,
        "holdout_total_trades": 10,
    }


def test_load_pathb_moments_roundtrip(tmp_path):
    rows = [_write_candidate(tmp_path, "h1aaa")]
    df = build_cohort_csv(rows, tmp_path)
    cms = load_pathb_moments(["h1aaa"], df, tmp_path)
    assert len(cms) == 1 and cms[0].T > 0


def test_integrity_gate_fires_on_tamper(tmp_path):
    rows = [_write_candidate(tmp_path, "h1bbb")]
    df = build_cohort_csv(rows, tmp_path)
    # tamper the parquet after the sha was recorded
    (tmp_path / "h1bbb" / "returns_per_bar.parquet").write_bytes(b"corrupt")
    with pytest.raises(ValueError, match="sha256 integrity mismatch"):
        load_pathb_moments(["h1bbb"], df, tmp_path)

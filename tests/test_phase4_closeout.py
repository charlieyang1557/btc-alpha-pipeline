"""Unit tests for scripts/build_phase4_closeout.py.

Per PHASE4_PLAN §1.5 binomial test machinery + threshold enforcement +
interpretation guard wording assembly.

Sanity-check tests assert hard-coded threshold constants match
scipy.stats.binom.sf(k-1, n, 0.5) ≤ 0.025/stratum. Catches silent
drift in either the constants or the PLAN-derived scipy values
(this is the §31 P1 instance #1 ≥17/22 vs ≥16/22 confusion class —
locks the constants to scipy's authoritative computation, so the
arithmetic identity that justifies the constants is checked at every
test run).
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path
from typing import Any

import pytest
from scipy.stats import binom

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from build_phase4_closeout import (  # noqa: E402  (sys.path hack required)
    ALPHA_PER_STRATUM,
    CALENDAR_THEME,
    COST_BPS_LIST,
    STRATUM_A_N,
    STRATUM_A_THRESHOLD,
    STRATUM_B_N,
    STRATUM_B_THRESHOLD,
    SUCCESS_CRITERION_COST_BPS,
    build_interpretation_guard,
    classify_stratum,
    derive_counts_per_stratum,
    evaluate_stratum,
    load_cohort_a_membership,
)


# ---------------------------------------------------------------------------
# Stratum classification
# ---------------------------------------------------------------------------


def test_classify_calendar_effect_is_stratum_a():
    assert classify_stratum("calendar_effect") == "A"


@pytest.mark.parametrize(
    "theme",
    ["momentum", "mean_reversion", "volume_divergence", "volatility_regime"],
)
def test_classify_non_calendar_is_stratum_b(theme):
    assert classify_stratum(theme) == "B"


def test_calendar_theme_constant_is_calendar_effect():
    assert CALENDAR_THEME == "calendar_effect"


# ---------------------------------------------------------------------------
# Threshold constants ↔ scipy sanity check
# ---------------------------------------------------------------------------


def test_alpha_per_stratum_constant_is_0p025():
    assert ALPHA_PER_STRATUM == 0.025


def test_stratum_a_n_locked_to_22():
    assert STRATUM_A_N == 22


def test_stratum_b_n_locked_to_17():
    assert STRATUM_B_N == 17


def test_stratum_a_threshold_constant_matches_scipy():
    """STRATUM_A_THRESHOLD must be the smallest k where
    binom.sf(k-1, n=22, 0.5) ≤ 0.025."""
    p_at_threshold = float(binom.sf(STRATUM_A_THRESHOLD - 1, STRATUM_A_N, 0.5))
    assert p_at_threshold <= ALPHA_PER_STRATUM, (
        f"binom.sf({STRATUM_A_THRESHOLD - 1}, {STRATUM_A_N}, 0.5)="
        f"{p_at_threshold} > {ALPHA_PER_STRATUM}"
    )
    p_below_threshold = float(
        binom.sf(STRATUM_A_THRESHOLD - 2, STRATUM_A_N, 0.5)
    )
    assert p_below_threshold > ALPHA_PER_STRATUM, (
        f"k={STRATUM_A_THRESHOLD - 1} (one below threshold) should have "
        f"p={p_below_threshold} > {ALPHA_PER_STRATUM} else threshold "
        f"could be lower"
    )


def test_stratum_b_threshold_constant_matches_scipy():
    """STRATUM_B_THRESHOLD must be the smallest k where
    binom.sf(k-1, n=17, 0.5) ≤ 0.025."""
    p_at_threshold = float(binom.sf(STRATUM_B_THRESHOLD - 1, STRATUM_B_N, 0.5))
    assert p_at_threshold <= ALPHA_PER_STRATUM, (
        f"binom.sf({STRATUM_B_THRESHOLD - 1}, {STRATUM_B_N}, 0.5)="
        f"{p_at_threshold} > {ALPHA_PER_STRATUM}"
    )
    p_below_threshold = float(
        binom.sf(STRATUM_B_THRESHOLD - 2, STRATUM_B_N, 0.5)
    )
    assert p_below_threshold > ALPHA_PER_STRATUM, (
        f"k={STRATUM_B_THRESHOLD - 1} (one below threshold) should have "
        f"p={p_below_threshold} > {ALPHA_PER_STRATUM} else threshold "
        f"could be lower"
    )


def test_success_criterion_cost_locked_to_15_bps():
    """PHASE4_PLAN §1.5 binds the success criterion to 15bps only."""
    assert SUCCESS_CRITERION_COST_BPS == 15


def test_cost_bps_list_is_07_13_15_17():
    """Per PHASE4_PLAN §1.4 dual-report; immutable at this PLAN."""
    assert COST_BPS_LIST == (7, 13, 15, 17)


# ---------------------------------------------------------------------------
# evaluate_stratum
# ---------------------------------------------------------------------------


def test_evaluate_stratum_passes_at_threshold():
    res = evaluate_stratum(k=17, n=22, threshold=17)
    assert res["passed"] is True
    assert res["k"] == 17
    assert res["n"] == 22
    assert res["threshold"] == 17
    assert res["p_value"] <= 0.025


def test_evaluate_stratum_passes_above_threshold():
    res = evaluate_stratum(k=20, n=22, threshold=17)
    assert res["passed"] is True


def test_evaluate_stratum_fails_just_below_threshold():
    res = evaluate_stratum(k=16, n=22, threshold=17)
    assert res["passed"] is False


def test_evaluate_stratum_fails_far_below_threshold():
    res = evaluate_stratum(k=11, n=22, threshold=17)
    assert res["passed"] is False
    assert res["p_value"] > 0.025


# ---------------------------------------------------------------------------
# build_interpretation_guard — 4 cases per PLAN §1.5 + brief implicit-4th-case
#
# These tests use strict equality (not substring `in`) per Mac Mini Task 5
# PATCH 2 adjudication: the function is the mechanical verbatim surface;
# wording is locked at PLAN §1.5 + implicit-4th-case from the entry brief.
# Equality assertions catch any future drift that re-introduces structural
# prefixes or framing elaboration into the function output.
# ---------------------------------------------------------------------------


def test_guard_neither_returns_verbatim_implicit_4th_case():
    assert build_interpretation_guard(a_pass=False, b_pass=False) == (
        "no forward persistence detected at PLAN §1.5 success criterion."
    )


def test_guard_a_only_returns_verbatim_plan_15_a_only_case():
    assert build_interpretation_guard(a_pass=True, b_pass=False) == (
        "calendar-effect candidates show forward persistence; "
        "non-calendar candidates do not."
    )


def test_guard_b_only_returns_verbatim_plan_15_b_only_case():
    assert build_interpretation_guard(a_pass=False, b_pass=True) == (
        "non-calendar candidates show forward persistence; "
        "calendar-effect candidates do not."
    )


def test_guard_both_returns_verbatim_plan_15_both_case():
    assert build_interpretation_guard(a_pass=True, b_pass=True) == (
        "two independent stratum-level persistence results, "
        "NOT a strengthened cohort-level claim."
    )


def test_guard_does_not_emit_structural_prefix():
    """No 'Phase 4 result:' / 'Phase 4 claim:' / similar elaboration prefix."""
    for a, b in [(False, False), (True, False), (False, True), (True, True)]:
        out = build_interpretation_guard(a_pass=a, b_pass=b)
        assert not out.startswith("Phase 4 result"), out
        assert not out.startswith("Phase 4 claim"), out
        assert not out.startswith("Stratum"), out


# ---------------------------------------------------------------------------
# Count derivation from synthetic CSV
# ---------------------------------------------------------------------------


_CSV_FIELDS: tuple[str, ...] = (
    "hypothesis_hash",
    "position",
    "theme",
    "name",
    "wf_test_period_sharpe",
    "lifecycle_state",
    "holdout_passed",
    "holdout_sharpe",
    "holdout_max_drawdown",
    "holdout_total_return",
    "holdout_total_trades",
    "wall_clock_seconds",
    "error_message",
)


def _write_synthetic_holdout_csv(
    path: Path, rows: list[dict[str, Any]]
) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=_CSV_FIELDS)
        writer.writeheader()
        for r in rows:
            writer.writerow({k: r.get(k, "") for k in _CSV_FIELDS})
    return path


def test_derive_counts_basic_per_stratum(tmp_path):
    csv_path = _write_synthetic_holdout_csv(
        tmp_path / "holdout_results.csv",
        rows=[
            # Stratum A: 3 rows; 2 positive, 1 negative
            {"hypothesis_hash": "a" * 16, "theme": "calendar_effect",
             "holdout_sharpe": "0.500000", "lifecycle_state": "holdout_passed"},
            {"hypothesis_hash": "b" * 16, "theme": "calendar_effect",
             "holdout_sharpe": "1.200000", "lifecycle_state": "holdout_passed"},
            {"hypothesis_hash": "c" * 16, "theme": "calendar_effect",
             "holdout_sharpe": "-0.300000", "lifecycle_state": "holdout_failed"},
            # Stratum B: 2 rows; 1 positive, 1 zero
            {"hypothesis_hash": "d" * 16, "theme": "momentum",
             "holdout_sharpe": "0.700000", "lifecycle_state": "holdout_passed"},
            {"hypothesis_hash": "e" * 16, "theme": "momentum",
             "holdout_sharpe": "0.000000", "lifecycle_state": "holdout_failed"},
        ],
    )
    membership = {
        "a" * 16: "A", "b" * 16: "A", "c" * 16: "A",
        "d" * 16: "B", "e" * 16: "B",
    }
    counts = derive_counts_per_stratum(csv_path, membership)
    assert counts["A"]["positive"] == 2
    assert counts["A"]["total"] == 3
    assert counts["B"]["positive"] == 1
    assert counts["B"]["total"] == 2


def test_derive_counts_zero_sharpe_is_not_positive(tmp_path):
    """forward_sharpe > 0 is strict; sharpe=0 is NOT positive."""
    csv_path = _write_synthetic_holdout_csv(
        tmp_path / "holdout_results.csv",
        rows=[
            {"hypothesis_hash": "z" * 16, "theme": "momentum",
             "holdout_sharpe": "0.000000",
             "lifecycle_state": "holdout_failed"},
        ],
    )
    membership = {"z" * 16: "B"}
    counts = derive_counts_per_stratum(csv_path, membership)
    assert counts["B"]["positive"] == 0
    assert counts["B"]["total"] == 1


def test_derive_counts_empty_sharpe_counts_in_total_only(tmp_path):
    """Empty holdout_sharpe (e.g. holdout_error) counts in total but not positive."""
    csv_path = _write_synthetic_holdout_csv(
        tmp_path / "holdout_results.csv",
        rows=[
            {"hypothesis_hash": "x" * 16, "theme": "momentum",
             "holdout_sharpe": "",
             "lifecycle_state": "holdout_error",
             "error_message": "synthetic"},
        ],
    )
    membership = {"x" * 16: "B"}
    counts = derive_counts_per_stratum(csv_path, membership)
    assert counts["B"]["positive"] == 0
    assert counts["B"]["total"] == 1


def test_derive_counts_skips_rows_not_in_membership(tmp_path):
    """Defensive: rows whose hash is not in cohort_a reference are skipped."""
    csv_path = _write_synthetic_holdout_csv(
        tmp_path / "holdout_results.csv",
        rows=[
            {"hypothesis_hash": "y" * 16, "theme": "calendar_effect",
             "holdout_sharpe": "1.000000",
             "lifecycle_state": "holdout_passed"},
            {"hypothesis_hash": "stranger" + "0" * 8, "theme": "momentum",
             "holdout_sharpe": "5.000000",
             "lifecycle_state": "holdout_passed"},
        ],
    )
    membership = {"y" * 16: "A"}  # stranger NOT in membership
    counts = derive_counts_per_stratum(csv_path, membership)
    assert counts["A"]["positive"] == 1
    assert counts["A"]["total"] == 1
    assert counts["B"]["positive"] == 0
    assert counts["B"]["total"] == 0


def test_derive_counts_nan_string_is_not_positive(tmp_path):
    """NaN parses as float but NaN > 0 evaluates False."""
    csv_path = _write_synthetic_holdout_csv(
        tmp_path / "holdout_results.csv",
        rows=[
            {"hypothesis_hash": "n" * 16, "theme": "momentum",
             "holdout_sharpe": "nan",
             "lifecycle_state": "holdout_failed"},
        ],
    )
    membership = {"n" * 16: "B"}
    counts = derive_counts_per_stratum(csv_path, membership)
    assert counts["B"]["positive"] == 0
    assert counts["B"]["total"] == 1


# ---------------------------------------------------------------------------
# load_cohort_a_membership against the sealed reference CSV
# ---------------------------------------------------------------------------


def test_load_cohort_a_membership_from_canonical_csv():
    """The sealed reference CSV produces 22 A + 17 B = 39 total per
    PHASE4_PLAN §1.3."""
    ref_csv = (
        PROJECT_ROOT / "data" / "phase4_scoping"
        / "cohort_a_candidate_reference.csv"
    )
    if not ref_csv.exists():
        pytest.skip(f"{ref_csv} not present")
    membership = load_cohort_a_membership(ref_csv)
    assert len(membership) == 39, f"expected 39 entries; got {len(membership)}"
    a_count = sum(1 for v in membership.values() if v == "A")
    b_count = sum(1 for v in membership.values() if v == "B")
    assert a_count == STRATUM_A_N, (
        f"expected {STRATUM_A_N} Stratum A; got {a_count} (PHASE4_PLAN §1.3 invariant)"
    )
    assert b_count == STRATUM_B_N, (
        f"expected {STRATUM_B_N} Stratum B; got {b_count} (PHASE4_PLAN §1.3 invariant)"
    )

"""Tests for backtest.tier6_dsr — Tier 6 closed-form DSR evaluation application.

TDD throughout. Synthetic known-value inputs only for the math layer; the
cohort-derivation tests assert membership/composition (factual, not pass/fail).
No real-cohort PASS/FAIL outcome is asserted here.
"""
from __future__ import annotations

import math
import os

import numpy as np
import pandas as pd
import pytest
from scipy.stats import kurtosis, skew

from backtest import tier6_dsr as t6


# --------------------------------------------------------------------------
# Shared fixtures / helpers
# --------------------------------------------------------------------------
def _cohort_df() -> pd.DataFrame:
    base = t6.HOLDOUT_DIR / "holdout_results.csv"
    return pd.read_csv(base)


def _synthetic_cm(sr: float, g3: float, g4: float, T: int) -> "t6.CandidateMoments":
    return t6.CandidateMoments("synthetic", "synthetic", "test", sr, g3, g4, T, None)


# ==========================================================================
# Task 1: Cohort derivation
# ==========================================================================
def test_derive_cohort_partitions_39_into_18_and_21():
    df = _cohort_df()
    assert len(df) == 39
    locked, companion = t6.derive_cohort(df)
    assert len(locked) == 18
    assert len(companion) == 21
    assert set(locked).isdisjoint(set(companion))
    assert set(locked) | set(companion) == set(df["hypothesis_hash"])


def test_locked_cohort_theme_composition():
    df = _cohort_df()
    locked, _ = t6.derive_cohort(df)
    sub = df[df["hypothesis_hash"].isin(locked)]
    comp = sub["theme"].value_counts().to_dict()
    assert comp == {"volume_divergence": 6, "momentum": 6,
                    "calendar_effect": 3, "mean_reversion": 2, "volatility_regime": 1}


def test_r21_excluded_are_not_monday_and_in_companion():
    df = _cohort_df()
    locked, companion = t6.derive_cohort(df)
    for h in ("35dcfcfbee4cfafc", "38a1bb228f103c26"):
        assert h in companion
        assert h not in locked


def test_is_monday_pattern():
    assert t6.is_monday_pattern("monday_morning_reversal") is True
    assert t6.is_monday_pattern("weekend_vol_compression_monday_breakout_160") is True
    assert t6.is_monday_pattern("MONDAY_DIP") is True
    assert t6.is_monday_pattern("friday_close_weekend_positioning") is False
    assert t6.is_monday_pattern("ema_crossover_momentum_acceleration") is False


def test_constants_locked_values():
    assert t6.ALPHA == 0.05
    assert t6.N_STAR == 18
    assert t6.EULER_GAMMA == 0.5772156649015329
    assert t6.R21_EXCLUDED == frozenset({"35dcfcfbee4cfafc", "38a1bb228f103c26"})


def test_derive_cohort_raises_on_partition_drift():
    df = _cohort_df()
    # Remove one locked candidate -> partition no longer 18/21 -> raise.
    locked, _ = t6.derive_cohort(df)
    dropped = df[df["hypothesis_hash"] != locked[0]]
    with pytest.raises(ValueError, match="cohort partition drift"):
        t6.derive_cohort(dropped)


# ==========================================================================
# Task 2: Moment loader + consume-with-verify (+ A8 sha256 integrity gate)
# ==========================================================================
def test_load_moments_matches_recompute_and_raw_kurtosis():
    df = _cohort_df()
    h = "7abff29fc2f117a1"  # ema_crossover_momentum_acceleration
    cm = t6.load_candidate_moments(h, df)
    # recompute from parquet
    r = pd.read_parquet(t6.HOLDOUT_DIR / h / "returns_per_bar.parquet")["return"]
    rf = r[np.isfinite(r)]
    assert cm.T == len(rf)
    assert abs(cm.gamma3 - float(skew(rf, bias=True))) < t6.MOMENT_RECOMPUTE_EPS
    # RAW kurtosis (3=normal), NOT excess
    assert abs(cm.gamma4 - float(kurtosis(rf, fisher=False, bias=True))) < t6.MOMENT_RECOMPUTE_EPS
    assert abs(cm.gamma4 - float(kurtosis(rf, fisher=True, bias=True))) > 1.0  # != excess
    assert abs(cm.sr_per_bar - rf.mean() / rf.std(ddof=0)) < 1e-12


def test_load_moments_raises_on_stored_recompute_mismatch():
    # if stored gamma deviates from recompute beyond EPS, raise (forensic guard)
    df = _cohort_df()
    h = "7abff29fc2f117a1"
    bad = df.copy()
    bad.loc[bad.hypothesis_hash == h, "gamma4"] = 999.0
    with pytest.raises(ValueError, match="moment mismatch"):
        t6.load_candidate_moments(h, bad)


def test_load_moments_raises_on_t_obs_mismatch():
    df = _cohort_df()
    h = "7abff29fc2f117a1"
    bad = df.copy()
    bad.loc[bad.hypothesis_hash == h, "T_obs"] = 1
    with pytest.raises(ValueError, match="moment mismatch"):
        t6.load_candidate_moments(h, bad)


def test_load_moments_a8_sha256_gate_raises_on_mismatch():
    # A8: verify CSV-stored returns_per_bar_sha256 against on-disk parquet sha256
    # BEFORE recompute; raise on mismatch (artifact-integrity gate).
    df = _cohort_df()
    h = "7abff29fc2f117a1"
    bad = df.copy()
    bad.loc[bad.hypothesis_hash == h, "returns_per_bar_sha256"] = "deadbeef" * 8
    with pytest.raises(ValueError, match="sha256"):
        t6.load_candidate_moments(h, bad)


def test_load_moments_raises_on_missing_hash():
    # FIX 4: an absent hash must raise ValueError (with the hash in the message),
    # not let .iloc[0] raise a bare IndexError.
    df = _cohort_df()
    with pytest.raises(ValueError, match="no_such_hash_xyz"):
        t6.load_candidate_moments("no_such_hash_xyz", df)


def test_load_moments_fields_present():
    df = _cohort_df()
    h = "7abff29fc2f117a1"
    cm = t6.load_candidate_moments(h, df)
    assert cm.hypothesis_hash == h
    assert cm.name == "ema_crossover_momentum_acceleration"
    assert cm.theme == "momentum"
    assert cm.trades == 12  # holdout_total_trades
    # frozen dataclass — cannot mutate
    with pytest.raises(Exception):
        cm.gamma3 = 0.0  # type: ignore[misc]


# ==========================================================================
# Task 3: Expected-max ratios (Form A + Form B) + monotonicity + guard
# ==========================================================================
def test_expected_max_ratios_at_18():
    assert abs(t6.expected_max_ratio_form_a(18) - 2.4043) < 1e-3
    assert abs(t6.expected_max_ratio_form_b(18) - 1.8539) < 1e-3


def test_expected_max_ratios_monotonic_increasing():
    for f in (t6.expected_max_ratio_form_a, t6.expected_max_ratio_form_b):
        vals = [f(n) for n in (2, 5, 10, 18, 30)]
        assert all(b > a for a, b in zip(vals, vals[1:]))


def test_form_degenerate_guard():
    with pytest.raises(ValueError):
        t6.expected_max_ratio_form_b(1)
    with pytest.raises(ValueError):
        t6.expected_max_ratio_form_a(1)
    with pytest.raises(ValueError):
        t6.expected_max_ratio_form_b(0)
    with pytest.raises(ValueError):
        t6.expected_max_ratio_form_a(0)


# ==========================================================================
# Task 4: Mertens variance + SR* + deflated-z + DSR/PSR + pass rule
# ==========================================================================
def test_mertens_variance_reduces_to_null_at_sr_zero():
    # at SR=0 the skew/kurt terms vanish -> 1/(T-1)
    assert abs(t6.mertens_variance(0.0, 5.0, 80.0, 2491) - 1.0 / 2490) < 1e-15


def test_mertens_variance_guard():
    # A4 (Codex HIGH, supersedes original buggy test):
    # term=0.75 > 0 -> positive, NO raise.
    assert t6.mertens_variance(1.0, 0.0, 0.0, 100) > 0
    # term = 1 - 10 + 0 = -9 < 0 -> raise.
    with pytest.raises(ValueError):
        t6.mertens_variance(2.0, 5.0, 1.0, 100)


def test_mertens_variance_degenerate_t_guard():
    # FIX 1: T must be >= 2 (T-1 division). T=1 and T=0 raise BEFORE any division.
    with pytest.raises(ValueError, match="T must be >= 2"):
        t6.mertens_variance(0.08, 0.0, 3.0, 1)
    with pytest.raises(ValueError, match="T must be >= 2"):
        t6.mertens_variance(0.08, 0.0, 3.0, 0)


def test_mertens_variance_non_finite_sr_guard():
    # FIX 2: non-finite sr (e.g. nan from a flat zero-variance series, 0/0=nan)
    # must raise — the `term <= 0` guard does NOT catch nan (nan <= 0 is False).
    with pytest.raises(ValueError, match="non-finite sr"):
        t6.mertens_variance(float("nan"), 0.0, 3.0, 2491)


def test_evaluate_candidate_degenerate_t_guard():
    # FIX 1: synthetic T=1 candidate propagates the T<2 guard through
    # sr_star -> deflated_z -> mertens_variance.
    with pytest.raises(ValueError, match="T must be >= 2"):
        t6.evaluate_candidate(_synthetic_cm(sr=0.08, g3=0.0, g4=3.0, T=1))


def test_evaluate_candidate_non_finite_sr_guard():
    # FIX 2: a nan sr_per_bar (flat zero-variance return series) raises.
    with pytest.raises(ValueError, match="non-finite sr"):
        t6.evaluate_candidate(_synthetic_cm(sr=float("nan"), g3=0.0, g4=3.0, T=2491))


def test_sr_star_null_scaling():
    er = t6.expected_max_ratio_form_b(18)
    assert abs(t6.sr_star(18, 2491, "B") - math.sqrt(1.0 / 2490) * er) < 1e-12
    er_a = t6.expected_max_ratio_form_a(18)
    assert abs(t6.sr_star(18, 2491, "A") - math.sqrt(1.0 / 2490) * er_a) < 1e-12


def test_sr_star_rejects_unknown_form():
    # FIX 3: unknown form must RAISE, not silently fall back to lenient Form A.
    with pytest.raises(ValueError, match="unknown form"):
        t6.sr_star(18, 2491, "C")


def test_sr_star_degenerate_t_guard():
    # FIX 1: sr_star also guards T < 2 (1/(T-1) division).
    with pytest.raises(ValueError, match="T must be >= 2"):
        t6.sr_star(18, 1, "B")
    with pytest.raises(ValueError, match="T must be >= 2"):
        t6.sr_star(18, 0, "B")


def test_deflated_z_denominator_equals_sqrt_term():
    # A10 DESIGN INVARIANT: sqrt(mertens * (T-1)) == sqrt(term) because
    # mertens = term/(T-1). Assert the denominator equals sqrt(term).
    sr, g3, g4, T = 0.08, 0.5, 10.0, 2491
    term = 1.0 - g3 * sr + ((g4 - 1.0) / 4.0) * sr * sr
    denom = math.sqrt(t6.mertens_variance(sr, g3, g4, T) * (T - 1))
    assert abs(denom - math.sqrt(term)) < 1e-15


def test_dsr_statistic_pass_rule_strong_not_weak():
    # A1 (advisor HIGH-1, supersedes original equivalence test):
    # sr_pass: clean STRONG pass (deflated_z ~ 2.13 >= 1.6449)
    rp = t6.evaluate_candidate(_synthetic_cm(sr=0.08, g3=0.0, g4=3.0, T=2491))
    assert rp["pass_B"] is True
    assert (rp["dsr_statistic_B"] >= 0) == (rp["psr_B"] >= 0.95) == rp["pass_B"]
    # sr_fail: SR_hat > SR* (weak rule WOULD pass) but deflated_z ~ 0.39 < 1.6449
    rf = t6.evaluate_candidate(_synthetic_cm(sr=0.045, g3=0.0, g4=3.0, T=2491))
    assert rf["sr_per_bar"] > rf["sr_star_B"]      # weak rule would pass
    assert rf["pass_B"] is False                    # strong rule fails -> pins strong != weak
    assert rf["psr_B"] < 0.95


def test_evaluate_candidate_emits_both_forms_and_equivalence():
    res = t6.evaluate_candidate(_synthetic_cm(sr=0.08, g3=0.0, g4=3.0, T=2491))
    for form in ("B", "A"):
        assert f"sr_star_{form}" in res
        assert f"deflated_z_{form}" in res
        assert f"psr_{form}" in res
        assert f"dsr_statistic_{form}" in res
        assert f"pass_{form}" in res
        # equivalence: pass <=> dsr_statistic >= 0 <=> psr >= 0.95
        assert (res[f"dsr_statistic_{form}"] >= 0) == res[f"pass_{form}"]
        assert (res[f"psr_{form}"] >= 0.95) == res[f"pass_{form}"]
    assert abs(res["z_pass"] - 1.6449) < 1e-3
    assert res["pass_B"] is True
    # FIX 6: expected-max-ratio keys are uppercase (er_B/er_A), consistent with
    # sr_star_B/psr_B/pass_B. Lowercase er_b/er_a no longer exist.
    assert "er_b" not in res and "er_a" not in res
    assert res["er_B"] == t6.expected_max_ratio_form_b(18)
    assert res["er_A"] == t6.expected_max_ratio_form_a(18)


def test_evaluate_candidate_pass_at_z_pass_threshold():
    # pass_B is True exactly when deflated_z_B >= z(0.95)
    res = t6.evaluate_candidate(_synthetic_cm(sr=0.08, g3=0.0, g4=3.0, T=2491))
    assert (res["deflated_z_B"] >= t6.Z_PASS) == res["pass_B"]


# ==========================================================================
# Task 5: Robustness flags (g4-high / provisional / r21-indeterminate)
# ==========================================================================
def _hashed_cm(hypothesis_hash: str, sr: float, g3: float, g4: float, T: int) -> "t6.CandidateMoments":
    return t6.CandidateMoments(hypothesis_hash, "synthetic", "test", sr, g3, g4, T, None)


def test_robustness_g4_high_flag():
    hi = t6.annotate_flags(t6.evaluate_candidate(_synthetic_cm(sr=0.06, g3=5.0, g4=200.0, T=2491)))
    assert hi["g4_high_flag"] is True
    lo = t6.annotate_flags(t6.evaluate_candidate(_synthetic_cm(sr=0.05, g3=0.0, g4=3.0, T=2491)))
    assert lo["g4_high_flag"] is False


def test_robustness_g4_high_flag_boundary():
    # g4_high_flag is True at exactly G4_HIGH (>= comparison).
    at = t6.annotate_flags(t6.evaluate_candidate(
        _synthetic_cm(sr=0.0, g3=0.0, g4=t6.G4_HIGH, T=2491)))
    assert at["g4_high_flag"] is True
    just_below = t6.annotate_flags(t6.evaluate_candidate(
        _synthetic_cm(sr=0.0, g3=0.0, g4=t6.G4_HIGH - 0.001, T=2491)))
    assert just_below["g4_high_flag"] is False


def test_robustness_provisional_flag_present_and_typed():
    lo = t6.annotate_flags(t6.evaluate_candidate(_synthetic_cm(sr=0.05, g3=0.0, g4=3.0, T=2491)))
    assert "provisional_flag" in lo
    assert isinstance(lo["provisional_flag"], bool)


def test_provisional_flag_only_on_passing_with_small_margin():
    # A clear strong pass (large positive dsr_statistic_B) is NOT provisional.
    strong = t6.annotate_flags(t6.evaluate_candidate(_synthetic_cm(sr=0.12, g3=0.0, g4=3.0, T=2491)))
    if strong["pass_B"] and strong["dsr_statistic_B"] >= t6.PROVISIONAL_DSR_MARGIN:
        assert strong["provisional_flag"] is False
    # A fail (dsr_statistic_B < 0) is never provisional.
    fail = t6.annotate_flags(t6.evaluate_candidate(_synthetic_cm(sr=0.02, g3=0.0, g4=3.0, T=2491)))
    assert fail["pass_B"] is False
    assert fail["provisional_flag"] is False


def test_provisional_flag_marks_narrow_pass():
    # FIX HIGH-2: sr=0.07 was vacuous (dsr_statistic_B ~ -0.008 -> pass_B=False,
    # provisional branch never fires). sr=0.08 gives dsr_statistic_B ~ 0.49,
    # squarely in [0, PROVISIONAL_DSR_MARGIN=0.5) -> a REAL narrow pass. Assert
    # non-vacuously (no `if` guard) so the provisional branch is exercised.
    res = t6.annotate_flags(t6.evaluate_candidate(_synthetic_cm(sr=0.08, g3=0.0, g4=3.0, T=2491)))
    assert res["pass_B"] is True
    assert 0 <= res["dsr_statistic_B"] < t6.PROVISIONAL_DSR_MARGIN
    assert res["provisional_flag"] is True


def test_r21_indeterminate_flag():
    # The two R6.1 §8.1 R2.1-INDETERMINATE hashes (DIFFERENT from R21_EXCLUDED).
    for h in ("7abff29fc2f117a1", "2433a38b2f9a7211"):
        res = t6.annotate_flags(t6.evaluate_candidate(
            _hashed_cm(h, sr=0.05, g3=0.0, g4=3.0, T=2491)))
        assert res["r21_indeterminate_flag"] is True
    # A non-flagged hash is False.
    other = t6.annotate_flags(t6.evaluate_candidate(
        _hashed_cm("deadbeefdeadbeef", sr=0.05, g3=0.0, g4=3.0, T=2491)))
    assert other["r21_indeterminate_flag"] is False


def test_r21_indeterminate_distinct_from_r21_excluded():
    # R21_INDETERMINATE (§8.1) is a DIFFERENT set from R21_EXCLUDED (§188).
    assert t6.R21_INDETERMINATE == frozenset({"7abff29fc2f117a1", "2433a38b2f9a7211"})
    assert t6.R21_INDETERMINATE.isdisjoint(t6.R21_EXCLUDED)


def test_annotate_flags_does_not_mutate_input():
    res = t6.evaluate_candidate(_synthetic_cm(sr=0.05, g3=0.0, g4=3.0, T=2491))
    before = set(res.keys())
    t6.annotate_flags(res)
    assert set(res.keys()) == before  # original dict untouched


def test_annotate_flags_constants():
    assert t6.G4_HIGH == 50.0
    assert t6.PROVISIONAL_DSR_MARGIN == 0.5


# ==========================================================================
# Task 6: MC expected-max validation (seeded, non-authoritative)
# ==========================================================================
def test_mc_expected_max_brackets_form_a_and_b():
    out = t6.mc_expected_max_ratio(n_star=18, n_sims=20000, seed=12345)
    # the empirical expected-max-of-18 standard normals is ~1.82-2.0; both
    # closed forms should be in a sane neighborhood, Form B closer for Gaussian
    assert 1.5 < out["empirical_ratio"] < 2.3
    assert out["form_a_ratio"] == pytest.approx(2.4043, abs=1e-3)
    assert out["form_b_ratio"] == pytest.approx(1.8539, abs=1e-3)
    assert "form_a_minus_empirical" in out and "form_b_minus_empirical" in out


def test_mc_difference_fields_consistent():
    out = t6.mc_expected_max_ratio(n_star=18, n_sims=20000, seed=12345)
    assert out["form_a_minus_empirical"] == pytest.approx(
        out["form_a_ratio"] - out["empirical_ratio"], abs=1e-12)
    assert out["form_b_minus_empirical"] == pytest.approx(
        out["form_b_ratio"] - out["empirical_ratio"], abs=1e-12)


def test_mc_form_b_is_better_gaussian_extreme_value_approx():
    # A11: Form B is the better Gaussian-extreme-value approximation at N*=18,
    # i.e. its signed error magnitude is smaller than Form A's.
    out = t6.mc_expected_max_ratio(n_star=18, n_sims=100_000, seed=20260529)
    assert abs(out["form_b_minus_empirical"]) < abs(out["form_a_minus_empirical"])


def test_mc_is_seed_deterministic():
    a = t6.mc_expected_max_ratio(18, n_sims=5000, seed=7)
    b = t6.mc_expected_max_ratio(18, n_sims=5000, seed=7)
    assert a["empirical_ratio"] == b["empirical_ratio"]


def test_mc_default_params():
    out = t6.mc_expected_max_ratio(n_sims=2000)
    assert out["n_star"] == 18
    assert out["seed"] == 20260529
    # n_sims is echoed as passed (we used a small count to keep the test fast).
    assert out["n_sims"] == 2000


# ==========================================================================
# Task 7: Cohort evaluator + artifact emitters
# ==========================================================================
import json  # noqa: E402


def test_evaluate_cohort_structure(tmp_path):
    out = t6.evaluate_cohort(out_dir=tmp_path, n_sims=2000)
    assert len(out["authoritative"]) == 18
    assert len(out["companion"]) == 21
    # promotion list is exactly the authoritative-18 rows that pass Form B
    promoted = {r["hypothesis_hash"] for r in out["promotion_list"]}
    auth_pass = {r["hypothesis_hash"] for r in out["authoritative"] if r["pass_B"] is True}
    assert promoted == auth_pass
    # companion rows carry the same fields but are flagged non-authoritative
    assert all(r["non_authoritative"] is True for r in out["companion"])
    assert all("monday_flag" in r for r in out["companion"])
    # top-level metadata
    assert out["n_star"] == 18
    assert out["alpha"] == 0.05
    assert out["authoritative_form"] == "B"
    assert out["companion_form"] == "B"
    assert out["mc_validation"]["n_sims"] == 2000
    # artifacts written
    for fn in ("tier6_dsr_results.csv", "tier6_dsr_companion.csv",
               "tier6_promotion_list.json", "tier6_mc_validation.json"):
        assert (tmp_path / fn).exists()


def test_companion_never_in_authoritative():
    out = t6.evaluate_cohort(out_dir=None, n_sims=0, write=False)
    auth = {r["hypothesis_hash"] for r in out["authoritative"]}
    comp = {r["hypothesis_hash"] for r in out["companion"]}
    assert auth.isdisjoint(comp)
    assert len(auth) == 18 and len(comp) == 21
    # n_sims=0 -> mc_validation is empty
    assert out["mc_validation"] == {}


def test_evaluate_cohort_promotion_list_subset_of_authoritative():
    out = t6.evaluate_cohort(out_dir=None, n_sims=0, write=False)
    auth_hashes = {r["hypothesis_hash"] for r in out["authoritative"]}
    for r in out["promotion_list"]:
        assert r["hypothesis_hash"] in auth_hashes
        assert r["pass_B"] is True
        assert r["non_authoritative"] is False  # promotion rows are authoritative


def test_evaluate_cohort_authoritative_rows_have_flags():
    out = t6.evaluate_cohort(out_dir=None, n_sims=0, write=False)
    for r in out["authoritative"]:
        for key in ("g4_high_flag", "provisional_flag", "r21_indeterminate_flag",
                    "mertens_degenerate_flag", "non_authoritative"):
            assert key in r
        assert r["non_authoritative"] is False
        assert r["mertens_degenerate_flag"] is False  # real cohort: term in [0.699, 1.114]


def test_promotion_json_schema(tmp_path):
    out = t6.evaluate_cohort(out_dir=tmp_path, n_sims=0)
    promo = json.loads((tmp_path / "tier6_promotion_list.json").read_text())
    assert promo["n_star"] == 18
    assert promo["alpha"] == 0.05
    assert promo["form"] == "B"
    assert isinstance(promo["promoted"], list)
    assert promo["count"] == len(promo["promoted"])
    assert promo["count"] == len(out["promotion_list"])
    assert set(promo["promoted"]) == {r["hypothesis_hash"] for r in out["promotion_list"]}


def test_results_csv_has_reconciled_fields(tmp_path):
    t6.evaluate_cohort(out_dir=tmp_path, n_sims=0)
    res_df = pd.read_csv(tmp_path / "tier6_dsr_results.csv")
    assert len(res_df) == 18
    # A5/A9 reconciliation: real emitted keys (er_B/er_A, var_sr_null, psr/dsr),
    # NOT the old var_null / ER_B / DSR_B inline-draft names.
    for col in ("hypothesis_hash", "name", "theme", "T", "sr_per_bar",
                "gamma3", "gamma4", "trades", "var_sr_null",
                "er_B", "sr_star_B", "deflated_z_B", "psr_B", "dsr_statistic_B", "pass_B",
                "er_A", "sr_star_A", "deflated_z_A", "psr_A", "dsr_statistic_A", "pass_A",
                "g4_high_flag", "provisional_flag", "r21_indeterminate_flag",
                "mertens_degenerate_flag"):
        assert col in res_df.columns, f"missing column {col}"
    assert "var_null" not in res_df.columns
    assert "ER_B" not in res_df.columns and "DSR_B" not in res_df.columns


def test_results_csv_self_describing_includes_n_star_and_z_pass(tmp_path):
    # FIX MINOR-1: n_star and z_pass are emitted per-row by evaluate_candidate;
    # they must be carried into _RESULT_FIELDS so the CSV is self-describing
    # (records the multiplicity N* and the one-sided z(0.95) threshold used).
    t6.evaluate_cohort(out_dir=tmp_path, n_sims=0)
    res_df = pd.read_csv(tmp_path / "tier6_dsr_results.csv")
    assert "n_star" in res_df.columns
    assert "z_pass" in res_df.columns
    assert (res_df["n_star"] == 18).all()
    assert (abs(res_df["z_pass"] - t6.Z_PASS) < 1e-9).all()


def test_result_fields_includes_n_star_and_z_pass():
    # FIX MINOR-1: explicit membership assertion on the field list.
    assert "n_star" in t6._RESULT_FIELDS
    assert "z_pass" in t6._RESULT_FIELDS


def test_degenerate_fail_row_has_all_result_fields_with_nan_numerics():
    # FIX IMPORTANT-1: a degenerate-fail row must populate every _RESULT_FIELDS
    # key. The 11 DSR numeric columns (var_sr_null + er/sr_star/deflated_z/psr/
    # dsr_statistic for both forms) must be float NaN (not absent), so a future
    # df["psr_B"].astype(float) over a cohort containing a degenerate row does
    # not choke on the empty-string restval. FIX MINOR-1: n_star/z_pass carried.
    cm = t6.CandidateMoments(
        "deadbeefdeadbeef", "synthetic_degenerate", "test",
        sr_per_bar=2.0, gamma3=5.0, gamma4=1.0, T=100, trades=None)
    exc = ValueError("non-positive Mertens variance term")
    row = t6._degenerate_fail_row("deadbeefdeadbeef", cm, exc)
    # every reconciled field is present
    for field in t6._RESULT_FIELDS:
        assert field in row, f"degenerate-fail row missing _RESULT_FIELDS key {field}"
    # the 11 DSR numeric columns are float NaN (numeric-parseable, not "")
    numeric_nan_fields = (
        "var_sr_null",
        "er_B", "sr_star_B", "deflated_z_B", "psr_B", "dsr_statistic_B",
        "er_A", "sr_star_A", "deflated_z_A", "psr_A", "dsr_statistic_A",
    )
    for field in numeric_nan_fields:
        assert isinstance(row[field], float), f"{field} must be a float, got {type(row[field])}"
        assert math.isnan(row[field]), f"{field} must be NaN on a degenerate-fail row"
    # n_star / z_pass carried even on degenerate rows (FIX MINOR-1)
    assert row["n_star"] == t6.N_STAR
    assert abs(row["z_pass"] - t6.Z_PASS) < 1e-9
    # identity + fail markers preserved
    assert row["pass_B"] is False and row["pass_A"] is False
    assert row["mertens_degenerate_flag"] is True
    assert row["failure_reason"]


def test_companion_csv_has_extra_columns(tmp_path):
    t6.evaluate_cohort(out_dir=tmp_path, n_sims=0)
    comp_df = pd.read_csv(tmp_path / "tier6_dsr_companion.csv")
    assert len(comp_df) == 21
    assert "non_authoritative" in comp_df.columns
    assert "monday_flag" in comp_df.columns
    assert bool(comp_df["non_authoritative"].all())


def test_evaluate_cohort_degenerate_candidate_flagged_not_crash(monkeypatch):
    # A3: a degenerate candidate (non-positive Mertens term) must NOT abort the
    # batch; the cohort run COMPLETES with that candidate flagged
    # mertens_degenerate_flag=True + pass_B=False (not an exception).
    df = t6._read_cohort_csv()
    locked, _ = t6.derive_cohort(df)
    degenerate_hash = locked[0]
    real_loader = t6.load_candidate_moments

    def fake_loader(hypothesis_hash, frame, **kwargs):
        if hypothesis_hash == degenerate_hash:
            # term = 1 - 5*2 + 0 = -9 < 0 -> mertens_variance raises ValueError
            return t6.CandidateMoments(
                hypothesis_hash, "synthetic_degenerate", "test",
                sr_per_bar=2.0, gamma3=5.0, gamma4=1.0, T=100, trades=None)
        return real_loader(hypothesis_hash, frame)

    monkeypatch.setattr(t6, "load_candidate_moments", fake_loader)
    out = t6.evaluate_cohort(out_dir=None, n_sims=0, write=False)
    assert len(out["authoritative"]) == 18  # batch completed, no abort
    flagged = [r for r in out["authoritative"] if r["hypothesis_hash"] == degenerate_hash]
    assert len(flagged) == 1
    row = flagged[0]
    assert row["mertens_degenerate_flag"] is True
    assert row["pass_B"] is False
    assert row["pass_A"] is False
    assert "failure_reason" in row and row["failure_reason"]
    # degenerate row is excluded from the promotion list
    assert degenerate_hash not in {r["hypothesis_hash"] for r in out["promotion_list"]}


def test_evaluate_cohort_data_integrity_error_propagates(monkeypatch):
    # FIX HIGH-1: a DATA-INTEGRITY ValueError from load_candidate_moments
    # (missing hash, SHA-256 mismatch, stored-vs-recompute moment mismatch) is
    # NOT Mertens math degeneracy — it must PROPAGATE and crash evaluate_cohort,
    # NOT be absorbed as mertens_degenerate_flag=True. Distinct from the
    # degenerate test above, where the loader RETURNS and evaluate_candidate
    # raises.
    def fake_loader(hypothesis_hash, frame, **kwargs):
        raise ValueError("sha mismatch")

    monkeypatch.setattr(t6, "load_candidate_moments", fake_loader)
    with pytest.raises(ValueError, match="sha mismatch"):
        t6.evaluate_cohort(out_dir=None, n_sims=0, write=False)


def test_evaluate_cohort_degenerate_count_zero_on_real_cohort():
    # MED-2: the real cohort has no degenerate candidates (Mertens term in
    # [0.699, 1.114]) -> degenerate_count == 0.
    out = t6.evaluate_cohort(out_dir=None, n_sims=0, write=False)
    assert out["degenerate_count"] == 0


def test_evaluate_cohort_degenerate_count_positive_when_injected(monkeypatch):
    # MED-2: injecting one Mertens-degenerate candidate -> degenerate_count >= 1.
    df = t6._read_cohort_csv()
    locked, _ = t6.derive_cohort(df)
    degenerate_hash = locked[0]
    real_loader = t6.load_candidate_moments

    def fake_loader(hypothesis_hash, frame, **kwargs):
        if hypothesis_hash == degenerate_hash:
            # term = 1 - 5*2 + 0 = -9 < 0 -> mertens_variance raises ValueError
            return t6.CandidateMoments(
                hypothesis_hash, "synthetic_degenerate", "test",
                sr_per_bar=2.0, gamma3=5.0, gamma4=1.0, T=100, trades=None)
        return real_loader(hypothesis_hash, frame)

    monkeypatch.setattr(t6, "load_candidate_moments", fake_loader)
    out = t6.evaluate_cohort(out_dir=None, n_sims=0, write=False)
    assert out["degenerate_count"] >= 1


def test_mc_expected_max_ratio_rejects_non_positive_n_sims():
    # MED-3: direct callers passing n_sims <= 0 get a clear ValueError rather
    # than a nan from an empty-array mean. (evaluate_cohort guards separately
    # via `if n_sims`.)
    with pytest.raises(ValueError, match="n_sims must be positive"):
        t6.mc_expected_max_ratio(n_star=18, n_sims=0)
    with pytest.raises(ValueError, match="n_sims must be positive"):
        t6.mc_expected_max_ratio(n_star=18, n_sims=-5)


def test_results_csv_has_failure_reason_column(tmp_path):
    # MED-1: failure_reason is a persisted column; normal rows emit "" (empty).
    t6.evaluate_cohort(out_dir=tmp_path, n_sims=0)
    res_df = pd.read_csv(tmp_path / "tier6_dsr_results.csv", keep_default_na=False)
    assert "failure_reason" in res_df.columns
    # real cohort has no degenerate rows -> all failure_reason are empty strings
    assert (res_df["failure_reason"] == "").all()


def test_evaluate_cohort_no_write_when_write_false(tmp_path):
    out = t6.evaluate_cohort(out_dir=tmp_path, n_sims=0, write=False)
    assert out["authoritative"]  # computed
    assert not any(tmp_path.iterdir())  # nothing written


# ==========================================================================
# Task 8: CLI + lineage guard (A2) + cost-anchor preflight (A12) +
#         --cohort threading (A6) + UTC logging (A7) + main()
# ==========================================================================
import logging  # noqa: E402
import time  # noqa: E402

from backtest import wf_lineage as _wfl  # noqa: E402


# --- A2: lineage guard on the REAL recovered summary (NON-monkeypatched) ---
def test_real_top_level_summary_passes_lineage_guard():
    # NON-monkeypatched: load the actual recovered aggregate summary and assert
    # the production wf_lineage guard accepts it (no raise). This is the
    # cross-module integration evidence that the recovered artifact is
    # consumable under the single_run_holdout_v1 attestation domain.
    summary = json.loads((t6.HOLDOUT_DIR / "holdout_summary.json").read_text())
    # must not raise
    _wfl.check_evaluation_semantics_or_raise(
        summary, artifact_path=str(t6.HOLDOUT_DIR / "holdout_summary.json")
    )


def test_real_per_candidate_summaries_pass_lineage_guard():
    # Every consumed per-candidate <hash>/holdout_summary.json carries the same
    # single_run_holdout_v1 lineage tags and must pass the guard.
    df = t6._read_cohort_csv()
    for h in df["hypothesis_hash"]:
        path = t6.HOLDOUT_DIR / h / "holdout_summary.json"
        summary = json.loads(path.read_text())
        _wfl.check_evaluation_semantics_or_raise(summary, artifact_path=str(path))


def test_lineage_guard_raises_on_bad_evaluation_semantics():
    # A summary dict with a missing/bad evaluation_semantics must raise.
    bad = {"evaluation_semantics": "not_the_right_tag"}
    with pytest.raises(ValueError):
        _wfl.check_evaluation_semantics_or_raise(bad)
    with pytest.raises(ValueError, match="evaluation_semantics"):
        _wfl.check_evaluation_semantics_or_raise({})


def test_evaluate_cohort_invokes_lineage_guard_before_parquet_read(monkeypatch):
    # A2 call-order: the lineage guard fires on the aggregate summary BEFORE any
    # per-candidate moment/parquet read. We make the guard raise and assert the
    # loader is never reached.
    calls = []

    def boom(summary, **kw):
        calls.append("guard")
        raise ValueError("lineage tripwire")

    def loader_should_not_run(*a, **k):
        calls.append("loader")
        raise AssertionError("load_candidate_moments must not run after guard raise")

    monkeypatch.setattr(t6, "check_evaluation_semantics_or_raise", boom)
    monkeypatch.setattr(t6, "load_candidate_moments", loader_should_not_run)
    with pytest.raises(ValueError, match="lineage tripwire"):
        t6.evaluate_cohort(out_dir=None, n_sims=0, write=False)
    assert calls == ["guard"]  # loader never reached


def test_evaluate_cohort_invokes_lineage_guard_before_csv_read(monkeypatch):
    # FIX IMPORTANT-2 (A2 "before consuming"): the aggregate summary lineage
    # guard must fire BEFORE the cohort CSV is consumed by _read_cohort_csv, not
    # only before the per-candidate parquet read. We make the guard raise and
    # spy on _read_cohort_csv; it must NEVER be called.
    calls = []

    def boom(summary, **kw):
        calls.append("guard")
        raise ValueError("lineage tripwire")

    def csv_should_not_run(*a, **k):
        calls.append("csv")
        raise AssertionError("_read_cohort_csv must not run after guard raise")

    monkeypatch.setattr(t6, "check_evaluation_semantics_or_raise", boom)
    monkeypatch.setattr(t6, "_read_cohort_csv", csv_should_not_run)
    with pytest.raises(ValueError, match="lineage tripwire"):
        t6.evaluate_cohort(out_dir=None, n_sims=0, write=False)
    assert calls == ["guard"]  # CSV read never reached


def test_evaluate_cohort_cost_anchor_preflight_before_csv_read(monkeypatch):
    # FIX IMPORTANT-2: the cost-anchor preflight (A12) likewise fires BEFORE the
    # cohort CSV is consumed. A non-15bps anchor must abort before _read_cohort_csv.
    calls = []

    def boom(summary):
        calls.append("preflight")
        raise ValueError("HARD CONSTRAINT 270: bad anchor")

    def csv_should_not_run(*a, **k):
        calls.append("csv")
        raise AssertionError("_read_cohort_csv must not run after preflight raise")

    monkeypatch.setattr(t6, "_assert_cost_anchor_15bps_spot", boom)
    monkeypatch.setattr(t6, "_read_cohort_csv", csv_should_not_run)
    with pytest.raises(ValueError, match="HARD CONSTRAINT 270"):
        t6.evaluate_cohort(out_dir=None, n_sims=0, write=False)
    assert "csv" not in calls  # CSV read never reached after preflight raise


# --- A12: cost-anchor preflight (HARD CONSTRAINT 270-271) ---
def test_cost_anchor_preflight_passes_on_real_summary():
    summary = json.loads((t6.HOLDOUT_DIR / "holdout_summary.json").read_text())
    # must not raise: real summary points at the 15bps spot anchor
    t6._assert_cost_anchor_15bps_spot(summary)


def test_cost_anchor_preflight_accepts_both_known_15bps_configs(monkeypatch):
    # FIX MINOR-3: airtight — assert the YAML body-check actually ran for each
    # allowlisted config (wrap yaml.safe_load with a counting spy). If someone
    # adds an early-return after the filename allowlist check, the body would
    # never be loaded and this counter assertion fails.
    import yaml as _yaml

    body_loads = []
    real_safe_load = _yaml.safe_load

    def spy_safe_load(stream):
        body_loads.append(stream)
        return real_safe_load(stream)

    monkeypatch.setattr(t6.yaml, "safe_load", spy_safe_load)
    for cfg in ("config/execution_phase4_15bps.yaml",
                "config/execution_phaseb_spot_15bps.yaml"):
        before = len(body_loads)
        t6._assert_cost_anchor_15bps_spot({"execution_config_path": cfg})
        # the body of THIS config must have been loaded (not short-circuited
        # after the filename allowlist check).
        assert len(body_loads) == before + 1, (
            f"yaml body for {cfg} was not loaded — filename-only allowlist "
            f"short-circuit would let a relabelled 7bps body through"
        )


def test_cost_anchor_preflight_rejects_7bps_effective_model():
    # A synthetic summary pointing at the PROHIBITED 7bps effective model raises
    # with the HARD CONSTRAINT message.
    bad = {"execution_config_path": "config/execution.yaml"}
    with pytest.raises(ValueError, match="HARD CONSTRAINT 270"):
        t6._assert_cost_anchor_15bps_spot(bad)


def test_cost_anchor_preflight_rejects_missing_path():
    with pytest.raises(ValueError, match="HARD CONSTRAINT 270"):
        t6._assert_cost_anchor_15bps_spot({})


def test_cost_anchor_preflight_rejects_relabel_with_7bps_body(tmp_path):
    # Defense-in-depth: a config with an allowlisted-looking name but a 7bps
    # body must still be rejected (we verify the loaded body's cost is 15bps).
    sneaky = tmp_path / "execution_phase4_15bps.yaml"
    sneaky.write_text(
        "cost_model:\n"
        "  name: phase4_realistic_base_15bps\n"
        "  default_fee_bps: 4.0\n"
        "  slippage_bps: 3.0\n"
    )
    with pytest.raises(ValueError, match="HARD CONSTRAINT 270"):
        t6._assert_cost_anchor_15bps_spot({"execution_config_path": str(sneaky)})


def test_cost_anchor_preflight_raises_value_error_on_malformed_yaml(tmp_path):
    # FIX HIGH: a malformed/corrupt anchor YAML raises yaml.YAMLError (subclass
    # of Exception, NOT OSError/ValueError). The preflight must catch it and
    # re-raise as a clean ValueError("HARD CONSTRAINT 270 ...") so the
    # capital-adjacent gate fails loud + clean, NOT leak a yaml.YAMLError
    # traceback past main()'s `except (ValueError, OSError)`.
    bad = tmp_path / "execution_phase4_15bps.yaml"
    bad.write_text("a: b: c:\n  - [unterminated")
    with pytest.raises(ValueError, match="HARD CONSTRAINT 270"):
        t6._assert_cost_anchor_15bps_spot({"execution_config_path": str(bad)})


def test_cost_anchor_preflight_accepts_absolute_path_to_valid_15bps_body(tmp_path):
    # FIX MED-1: the absolute-path ACCEPTANCE branch (only the rejection branch
    # was covered via tmp absolute paths). An allowlisted-name config at an
    # ABSOLUTE path whose cost_model body sums to 15.0bps/side
    # (default_fee_bps 10.0 + slippage_bps 5.0, matching the real
    # config/execution_phase4_15bps.yaml schema) must NOT raise.
    cfg = tmp_path / "execution_phase4_15bps.yaml"
    cfg.write_text(
        "cost_model:\n"
        "  name: phase4_realistic_base_15bps\n"
        "  default_fee_bps: 10.0\n"
        "  slippage_bps: 5.0\n"
    )
    assert cfg.is_absolute()
    # must not raise
    t6._assert_cost_anchor_15bps_spot({"execution_config_path": str(cfg)})


def test_cost_anchor_preflight_is_invoked_by_evaluate_cohort(monkeypatch):
    # The preflight is wired into evaluate_cohort before consumption.
    seen = []
    real = t6._assert_cost_anchor_15bps_spot

    def spy(summary):
        seen.append("preflight")
        return real(summary)

    monkeypatch.setattr(t6, "_assert_cost_anchor_15bps_spot", spy)
    t6.evaluate_cohort(out_dir=None, n_sims=0, write=False)
    assert "preflight" in seen


# --- A6: --cohort honored (holdout_dir threading) ---
def test_holdout_dir_param_changes_dir_read(tmp_path, monkeypatch):
    # A non-default holdout_dir must actually be read (not silently ignored).
    # Build a minimal fake cohort dir; assert _read_cohort_csv reads from it.
    (tmp_path / "holdout_results.csv").write_text("hypothesis_hash,name\nx,y\n")
    df = t6._read_cohort_csv(holdout_dir=tmp_path)
    assert list(df["hypothesis_hash"]) == ["x"]


def test_main_cohort_arg_resolves_non_default_dir(monkeypatch):
    # CLI --cohort must change the resolved holdout_dir. We capture the
    # holdout_dir evaluate_cohort is called with.
    captured = {}

    def fake_eval(*, out_dir, n_sims, write, holdout_dir, n_star=t6.N_STAR):
        captured["holdout_dir"] = holdout_dir
        return {"promotion_list": [], "degenerate_count": 0,
                "authoritative": [], "companion": []}

    monkeypatch.setattr(t6, "evaluate_cohort", fake_eval)
    rc = t6.main(["--cohort", "some_other_cohort_v9", "--dry-run", "--n-sims", "0"])
    assert rc == 0
    assert captured["holdout_dir"] == (
        t6.PROJECT_ROOT / "data/phase2c_evaluation_gate" / "some_other_cohort_v9"
    )


# --- A7: UTC logging ---
def test_logging_formatter_uses_utc():
    fmt = t6._build_log_formatter()
    assert fmt.converter is time.gmtime


def test_configure_logging_is_idempotent_no_duplicate_handlers():
    # FIX MINOR-3: pin the existing idempotency guard in _configure_logging().
    # Calling it twice (e.g. two main() invocations in one process) must NOT
    # accumulate duplicate handlers on the module logger.
    t6._configure_logging()
    t6._configure_logging()
    assert len(logging.getLogger("tier6_dsr").handlers) <= 1


# --- CLI main() ---
def test_main_dry_run_writes_nothing_and_returns_zero(tmp_path, monkeypatch):
    # --dry-run must write nothing and return 0.
    out_dir = tmp_path / "tier6_out"
    rc = t6.main([
        "--out-dir", str(out_dir), "--n-sims", "0", "--dry-run",
    ])
    assert rc == 0
    assert not out_dir.exists() or not any(out_dir.iterdir())


def test_main_non_dry_run_writes_to_tmp_out_dir(tmp_path):
    # A real (non-dry) run into a tmp out-dir writes the 4 artifacts and
    # returns 0. (Does NOT touch the production tier6_dsr_v1 dir.)
    out_dir = tmp_path / "tier6_out"
    rc = t6.main(["--out-dir", str(out_dir), "--n-sims", "0"])
    assert rc == 0
    for fn in ("tier6_dsr_results.csv", "tier6_dsr_companion.csv",
               "tier6_promotion_list.json", "tier6_mc_validation.json"):
        assert (out_dir / fn).exists()


def test_main_returns_nonzero_on_validation_failure(monkeypatch):
    # A lineage/validation failure surfaces as a non-zero exit (not a traceback).
    def boom(*a, **k):
        raise ValueError("simulated lineage failure")

    monkeypatch.setattr(t6, "evaluate_cohort", boom)
    rc = t6.main(["--n-sims", "0", "--dry-run"])
    assert rc != 0


# ==========================================================================
# Section D (Tasks 19-22): N* plumbing through evaluate_cohort + CLI
# ==========================================================================
def test_evaluate_cohort_threads_non_default_n_star_into_rows_and_mc():
    # Task 19: a non-default n_star must flow into (a) every per-candidate row's
    # "n_star" field, (b) the MC validation block's "n_star", and (c) the
    # top-level out["n_star"]. Probe value 7 != N_STAR=18 (NOT the Step -1
    # locked PATHB_N_STAR capital value; purely a plumbing probe). Writes to a
    # tmp dir so the sealed tier6_dsr_v1/ is untouched.
    probe = 7
    assert probe != t6.N_STAR
    out = t6.evaluate_cohort(out_dir=None, n_sims=500, write=False, n_star=probe)
    for r in (*out["authoritative"], *out["companion"]):
        assert r["n_star"] == probe, f"row {r['hypothesis_hash']} kept n_star={r['n_star']}"
    assert out["mc_validation"]["n_star"] == probe
    assert out["n_star"] == probe


def test_evaluate_cohort_default_n_star_is_18():
    out = t6.evaluate_cohort(out_dir=None, n_sims=0, write=False)
    assert out["n_star"] == 18
    assert all(r["n_star"] == 18 for r in out["authoritative"])
    assert all(r["n_star"] == 18 for r in out["companion"])


def test_degenerate_fail_row_threads_non_default_n_star(monkeypatch):
    probe = 7
    df = t6._read_cohort_csv()
    locked, _ = t6.derive_cohort(df)
    degenerate_hash = locked[0]
    real_loader = t6.load_candidate_moments

    def fake_loader(hypothesis_hash, frame, **kwargs):
        if hypothesis_hash == degenerate_hash:
            # term = 1 - 5*2 + 0 = -9 < 0 -> mertens_variance raises ValueError
            return t6.CandidateMoments(
                hypothesis_hash, "synthetic_degenerate", "test",
                sr_per_bar=2.0, gamma3=5.0, gamma4=1.0, T=100, trades=None)
        return real_loader(hypothesis_hash, frame)

    monkeypatch.setattr(t6, "load_candidate_moments", fake_loader)
    out = t6.evaluate_cohort(out_dir=None, n_sims=0, write=False, n_star=probe)
    degen_rows = [r for r in out["authoritative"]
                  if r["mertens_degenerate_flag"] is True]
    assert degen_rows, "expected at least one injected degenerate row"
    for r in degen_rows:
        assert r["n_star"] == probe, (
            f"degenerate row kept hardcoded n_star={r['n_star']} (want {probe})")


def test_degenerate_fail_row_helper_accepts_n_star_kwarg():
    cm = t6.CandidateMoments(
        "deadbeefdeadbeef", "synthetic_degenerate", "test",
        sr_per_bar=2.0, gamma3=5.0, gamma4=1.0, T=100, trades=None)
    exc = ValueError("non-positive Mertens variance term")
    row_default = t6._degenerate_fail_row("deadbeefdeadbeef", cm, exc)
    assert row_default["n_star"] == t6.N_STAR
    row_probe = t6._degenerate_fail_row("deadbeefdeadbeef", cm, exc, n_star=7)
    assert row_probe["n_star"] == 7


# ==========================================================================
# Task 20: CSV n_star column carries a non-18 value end-to-end
# ==========================================================================
def test_results_and_companion_csv_carry_non_default_n_star(tmp_path):
    # Task 20: written CSVs must carry the non-default n_star end-to-end
    # (not a hardcoded 18). Probe 7 != N_STAR; writes to tmp (sealed dir safe).
    probe = 7
    assert probe != t6.N_STAR
    t6.evaluate_cohort(out_dir=tmp_path, n_sims=0, n_star=probe)
    res_df = pd.read_csv(tmp_path / "tier6_dsr_results.csv")
    comp_df = pd.read_csv(tmp_path / "tier6_dsr_companion.csv")
    assert len(res_df) == 18
    assert len(comp_df) == 21
    assert "n_star" in res_df.columns
    assert "n_star" in comp_df.columns
    assert (res_df["n_star"] == probe).all()
    assert (comp_df["n_star"] == probe).all()
    promo = json.loads((tmp_path / "tier6_promotion_list.json").read_text())
    assert promo["n_star"] == probe


def test_results_csv_default_n_star_still_18(tmp_path):
    # Task 20: omitting n_star keeps the sealed default in the CSV.
    t6.evaluate_cohort(out_dir=tmp_path, n_sims=0)
    res_df = pd.read_csv(tmp_path / "tier6_dsr_results.csv")
    assert (res_df["n_star"] == 18).all()


# ==========================================================================
# Task 21: CLI --n-star safety guard (sealed-artifact protection)
# ==========================================================================
def test_main_n_star_flag_threads_into_cohort(monkeypatch):
    captured = {}

    def spy(out_dir, n_sims, write, holdout_dir, n_star):
        captured["n_star"] = n_star
        captured["out_dir"] = out_dir
        return {
            "authoritative": [], "companion": [], "promotion_list": [],
            "degenerate_count": 0, "mc_validation": {}, "n_star": n_star,
            "alpha": t6.ALPHA, "authoritative_form": "B", "companion_form": "B",
        }

    monkeypatch.setattr(t6, "evaluate_cohort", spy)
    rc = t6.main(["--n-star", "7", "--out-dir", "/tmp/pathb_probe", "--n-sims", "0"])
    assert rc == 0
    assert captured["n_star"] == 7


def test_main_n_star_default_is_18(monkeypatch):
    captured = {}

    def spy(out_dir, n_sims, write, holdout_dir, n_star):
        captured["n_star"] = n_star
        return {
            "authoritative": [], "companion": [], "promotion_list": [],
            "degenerate_count": 0, "mc_validation": {}, "n_star": n_star,
            "alpha": t6.ALPHA, "authoritative_form": "B", "companion_form": "B",
        }

    monkeypatch.setattr(t6, "evaluate_cohort", spy)
    rc = t6.main(["--out-dir", "/tmp/pathb_probe", "--n-sims", "0"])
    assert rc == 0
    assert captured["n_star"] == 18


def test_main_rejects_non_default_n_star_without_out_dir(monkeypatch):
    def boom(*a, **k):
        raise AssertionError("evaluate_cohort must NOT run when the guard fires")

    monkeypatch.setattr(t6, "evaluate_cohort", boom)
    rc = t6.main(["--n-star", "7", "--n-sims", "0"])
    assert rc == 1


def test_main_non_default_n_star_allowed_with_dry_run(monkeypatch):
    captured = {}

    def spy(out_dir, n_sims, write, holdout_dir, n_star):
        captured["write"] = write
        captured["n_star"] = n_star
        return {
            "authoritative": [], "companion": [], "promotion_list": [],
            "degenerate_count": 0, "mc_validation": {}, "n_star": n_star,
            "alpha": t6.ALPHA, "authoritative_form": "B", "companion_form": "B",
        }

    monkeypatch.setattr(t6, "evaluate_cohort", spy)
    rc = t6.main(["--n-star", "7", "--dry-run", "--n-sims", "0"])
    assert rc == 0
    assert captured["write"] is False
    assert captured["n_star"] == 7


def test_main_default_n_star_without_out_dir_is_allowed(monkeypatch):
    captured = {}

    def spy(out_dir, n_sims, write, holdout_dir, n_star):
        captured["out_dir"] = out_dir
        captured["n_star"] = n_star
        return {
            "authoritative": [], "companion": [], "promotion_list": [],
            "degenerate_count": 0, "mc_validation": {}, "n_star": n_star,
            "alpha": t6.ALPHA, "authoritative_form": "B", "companion_form": "B",
        }

    monkeypatch.setattr(t6, "evaluate_cohort", spy)
    rc = t6.main(["--n-sims", "0"])  # default n_star=18, default out_dir, real write
    assert rc == 0
    assert captured["out_dir"] == t6.DEFAULT_OUT_DIR
    assert captured["n_star"] == 18


def test_main_rejects_non_default_n_star_with_explicit_sealed_out_dir(monkeypatch):
    # Task 21 hardening: even an EXPLICIT --out-dir pointing at the sealed
    # tier6_dsr_v1 directory must be refused for a non-default n_star (the
    # guard resolves out_dir against DEFAULT_OUT_DIR, not just `is None`).
    def boom(*a, **k):
        raise AssertionError("evaluate_cohort must NOT run when the guard fires")

    monkeypatch.setattr(t6, "evaluate_cohort", boom)
    rc = t6.main([
        "--n-star", "7",
        "--out-dir", str(t6.DEFAULT_OUT_DIR),
        "--n-sims", "0",
    ])
    assert rc == 1


def test_main_allows_default_n_star_with_explicit_sealed_out_dir(monkeypatch):
    # The sealed REPRODUCTION path (n_star=18) is still allowed even when the
    # sealed dir is named explicitly — the guard keys on a NON-default n_star.
    captured = {}

    def spy(out_dir, n_sims, write, holdout_dir, n_star):
        captured["n_star"] = n_star
        captured["out_dir"] = out_dir
        return {
            "authoritative": [], "companion": [], "promotion_list": [],
            "degenerate_count": 0, "mc_validation": {}, "n_star": n_star,
            "alpha": t6.ALPHA, "authoritative_form": "B", "companion_form": "B",
        }

    monkeypatch.setattr(t6, "evaluate_cohort", spy)
    rc = t6.main(["--out-dir", str(t6.DEFAULT_OUT_DIR), "--n-sims", "0"])
    assert rc == 0
    assert captured["n_star"] == 18


def test_main_rejects_non_default_n_star_via_symlink_to_sealed_dir(tmp_path, monkeypatch):
    # Task 21 hardening: the guard keys on inode identity (os.path.samefile),
    # not string equality, so a path that is NOT string-equal to DEFAULT_OUT_DIR
    # but points at the same directory (here via a symlink) is still refused.
    def boom(*a, **k):
        raise AssertionError("evaluate_cohort must NOT run when the guard fires")

    monkeypatch.setattr(t6, "evaluate_cohort", boom)
    link = tmp_path / "sealed_link"
    os.symlink(t6.DEFAULT_OUT_DIR, link)
    rc = t6.main(["--n-star", "7", "--out-dir", str(link), "--n-sims", "0"])
    assert rc == 1


# --- Task 22: sealed-artifact byte-regression (n_star=18 reproduces v1) ---
SEALED_V1_DIR = t6.PROJECT_ROOT / "data/phase2c_evaluation_gate/tier6_dsr_v1"


def test_default_n_star_reproduces_sealed_deterministic_artifacts_byte_identical(tmp_path):
    # Task 22: a default-path (n_star=N_STAR=18) re-run must reproduce the three
    # DETERMINISTIC sealed artifacts byte-for-byte. Writes ONLY into tmp_path;
    # the sealed dir is read-only here. Proves the n_star plumbing (Tasks 19-21)
    # did not perturb the sealed numeric output.
    if not SEALED_V1_DIR.exists():
        pytest.skip("sealed tier6_dsr_v1 dir not present in this checkout")

    # MC json depends on (n_sims, seed); reproduce with the sealed default
    # n_sims so all four files match. n_star omitted -> defaults to N_STAR=18.
    t6.evaluate_cohort(out_dir=tmp_path, n_sims=100_000)

    deterministic = (
        "tier6_dsr_results.csv",
        "tier6_dsr_companion.csv",
        "tier6_promotion_list.json",
    )
    for fn in deterministic:
        sealed_bytes = (SEALED_V1_DIR / fn).read_bytes()
        fresh_bytes = (tmp_path / fn).read_bytes()
        assert fresh_bytes == sealed_bytes, (
            f"{fn} differs from sealed tier6_dsr_v1 — the n_star plumbing "
            f"perturbed deterministic output"
        )


def test_default_n_star_reproduces_sealed_mc_validation(tmp_path):
    # Task 22: the seeded MC json (default n_sims=100000, default seed) is also
    # reproduced byte-identical under the default n_star path.
    if not (SEALED_V1_DIR / "tier6_mc_validation.json").exists():
        pytest.skip("sealed tier6_mc_validation.json not present")
    t6.evaluate_cohort(out_dir=tmp_path, n_sims=100_000)
    sealed = (SEALED_V1_DIR / "tier6_mc_validation.json").read_bytes()
    fresh = (tmp_path / "tier6_mc_validation.json").read_bytes()
    assert fresh == sealed, (
        "tier6_mc_validation.json differs — the n_star plumbing perturbed the "
        "seeded Monte-Carlo expected-max output"
    )


def test_sealed_v1_dir_is_not_written_by_default_run(tmp_path):
    # Task 22 (safety): a fresh run targeting tmp_path must NOT mutate the
    # sealed dir. Snapshot sealed mtimes before/after; assert unchanged.
    if not SEALED_V1_DIR.exists():
        pytest.skip("sealed tier6_dsr_v1 dir not present in this checkout")
    before = {p.name: p.stat().st_mtime_ns for p in SEALED_V1_DIR.iterdir()}
    t6.evaluate_cohort(out_dir=tmp_path, n_sims=0)
    after = {p.name: p.stat().st_mtime_ns for p in SEALED_V1_DIR.iterdir()}
    assert before == after, "sealed tier6_dsr_v1 dir was mutated by a tmp-dir run"


# ==========================================================================
# Producer-layer sealed-dir guard (Codex B2 finding)
# ==========================================================================
def test_evaluate_cohort_refuses_non_default_n_star_into_sealed_dir(tmp_path, monkeypatch):
    # Producer-layer guard (Codex B2): a DIRECT evaluate_cohort call with a
    # non-default n_star + write into the SEALED dir must RAISE before any
    # write — the main() CLI guard is not in the call path here.
    #
    # SAFETY: we monkeypatch DEFAULT_OUT_DIR to a tmp directory so this test
    # can NEVER write into the REAL sealed dir — not even if the guard is one
    # day removed by a regression (in which case the write would land in tmp,
    # and the test would fail loudly, instead of clobbering the sealed
    # artifacts). The guard logic (samefile against DEFAULT_OUT_DIR) is
    # identical regardless of which directory DEFAULT_OUT_DIR names.
    fake_sealed = tmp_path / "fake_sealed"
    fake_sealed.mkdir()
    monkeypatch.setattr(t6, "DEFAULT_OUT_DIR", fake_sealed)
    probe = 7
    assert probe != t6.N_STAR
    with pytest.raises(ValueError, match="SEALED|REFUS"):
        t6.evaluate_cohort(out_dir=fake_sealed, n_sims=0, write=True, n_star=probe)


def test_evaluate_cohort_allows_default_n_star_into_sealed_dir(tmp_path, monkeypatch):
    # The sealed REPRODUCTION path (n_star=18, write into the sealed default
    # dir) must NOT be blocked by the producer guard. To avoid actually writing
    # the sealed dir in the test, redirect the writers to tmp by monkeypatching
    # DEFAULT_OUT_DIR is NOT safe (guard compares against it); instead assert the
    # guard does not raise for n_star=18 by calling with write=False targeting
    # the sealed dir (no write happens, guard must still not fire on default).
    t6.evaluate_cohort(out_dir=t6.DEFAULT_OUT_DIR, n_sims=0, write=False, n_star=t6.N_STAR)
    # also: non-default n_star with write=False into sealed dir is allowed
    # (nothing is written, so no clobber risk).
    t6.evaluate_cohort(out_dir=t6.DEFAULT_OUT_DIR, n_sims=0, write=False, n_star=7)


def test_evaluate_cohort_allows_non_default_n_star_into_nonsealed_dir(tmp_path):
    # Non-default n_star into a NON-sealed dir is the intended Path-B use — allowed.
    out = t6.evaluate_cohort(out_dir=tmp_path, n_sims=0, write=True, n_star=7)
    assert out["n_star"] == 7


def test_z_pass_frozen_matches_analytic():
    # Z_PASS is frozen as a literal (not float(norm.ppf(1 - ALPHA))) for
    # scipy-version-independent byte-reproduction of the sealed tier6_dsr_v1/
    # artifacts (it feeds the gate-relevant dsr_statistic/pass columns). Assert
    # the frozen literal still equals the analytic z(1 - ALPHA) within tolerance:
    # tolerates cross-scipy-version ULP drift, but catches a typo in the literal
    # or an ALPHA change that was not reflected here.
    from scipy.stats import norm

    assert t6.Z_PASS == 1.644853626951472
    assert abs(t6.Z_PASS - float(norm.ppf(1.0 - t6.ALPHA))) < 1e-12

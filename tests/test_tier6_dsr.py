"""Tests for backtest.tier6_dsr — Tier 6 closed-form DSR evaluation application.

TDD throughout. Synthetic known-value inputs only for the math layer; the
cohort-derivation tests assert membership/composition (factual, not pass/fail).
No real-cohort PASS/FAIL outcome is asserted here.
"""
from __future__ import annotations

import math

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

    def fake_loader(hypothesis_hash, frame):
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
    def fake_loader(hypothesis_hash, frame):
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

    def fake_loader(hypothesis_hash, frame):
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

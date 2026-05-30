# tests/test_tier6_bootstrap.py
import json
import numpy as np
import pandas as pd
import pytest
from backtest import tier6_bootstrap as tb


def test_module_constants():
    assert tb.BLOCK_LEN_GRID == (1, 6, 12, 24, 48, 96)
    assert tb.BASE_SEED == 20260529
    assert tb.DEFAULT_N_REPLICATES == 5000
    assert tb.OUT_DIR.name == "tier6_serialcorr_robustness_v1"
    assert tb.OUT_DIR.parent.name == "phase2c_evaluation_gate"


def test_bootstrap_indices_shape_and_range():
    rng = np.random.default_rng(0)
    idx = tb.stationary_bootstrap_indices(100, 12, rng)
    assert idx.shape == (100,)
    assert idx.min() >= 0 and idx.max() < 100


def test_bootstrap_indices_deterministic():
    a = tb.stationary_bootstrap_indices(50, 6, np.random.default_rng(7))
    b = tb.stationary_bootstrap_indices(50, 6, np.random.default_rng(7))
    np.testing.assert_array_equal(a, b)


def test_bootstrap_indices_L1_is_all_fresh_draws():
    # L=1 -> p=1 -> every position is an independent fresh start (no runs).
    rng = np.random.default_rng(1)
    idx = tb.stationary_bootstrap_indices(2000, 1, rng)
    # consecutive-increment fraction should be ~ chance (1/T), not block-like.
    inc = np.mean((idx[1:] - idx[:-1]) % 2000 == 1)
    assert inc < 0.05


def test_bootstrap_indices_largeL_has_long_runs():
    rng = np.random.default_rng(2)
    idx = tb.stationary_bootstrap_indices(2000, 200, rng)
    inc = np.mean((idx[1:] - idx[:-1]) % 2000 == 1)
    assert inc > 0.8  # ~ 1 - 1/200


def test_bootstrap_indices_rejects_tiny_T():
    with pytest.raises(ValueError):
        tb.stationary_bootstrap_indices(1, 6, np.random.default_rng(0))


def _ar1(n, phi, seed):
    rng = np.random.default_rng(seed)
    e = rng.standard_normal(n)
    x = np.empty(n)
    x[0] = e[0]
    for i in range(1, n):
        x[i] = phi * x[i - 1] + e[i]
    return x


def test_boot_se_iid_matches_analytic():
    # i.i.d. Gaussian: SE_boot(L=1) ~ 1/sqrt(T-1) (the null Sharpe SE).
    rng_data = np.random.default_rng(42)
    r = rng_data.standard_normal(3000)
    se = tb.bootstrap_sharpe_se(r, 1, 4000, np.random.default_rng(123))
    analytic = 1.0 / np.sqrt(len(r) - 1)
    assert abs(se / analytic - 1.0) < 0.08


def test_boot_se_positive_autocorr_inflates():
    r = _ar1(3000, 0.5, seed=9)
    # same RNG seed for both calls: isolates the block-length effect (lower MC
    # variance). Do NOT "fix" to distinct seeds — that adds noise and can flip
    # the inequality under unlucky draws.
    se1 = tb.bootstrap_sharpe_se(r, 1, 4000, np.random.default_rng(5))
    se24 = tb.bootstrap_sharpe_se(r, 24, 4000, np.random.default_rng(5))
    assert se24 > se1 * 1.10  # positive AR(1) inflates the block-bootstrap SE


def test_boot_se_deterministic():
    r = _ar1(1000, 0.3, seed=3)
    a = tb.bootstrap_sharpe_se(r, 12, 2000, np.random.default_rng(11))
    b = tb.bootstrap_sharpe_se(r, 12, 2000, np.random.default_rng(11))
    assert a == b


def test_boot_se_rejects_nonfinite_input():
    r = np.array([np.nan, 1.0, 2.0, 3.0])  # leading-NaN like the real parquet
    with pytest.raises(ValueError, match="finite"):
        tb.bootstrap_sharpe_se(r, 6, 100, np.random.default_rng(0))


def test_boot_se_rejects_flat_series():
    # flat series -> every bootstrap replicate has zero variance -> all dropped
    # -> degeneracy tripwire fires.
    with pytest.raises(ValueError, match="degenerate"):
        tb.bootstrap_sharpe_se(np.zeros(500), 6, 100, np.random.default_rng(0))


def test_boot_se_stability_doubling_replicates():
    # at the largest L (highest-variance SE); 8k vs 16k for headroom under tol
    # (PFR MEDIUM-1: 4k-vs-8k had only ~2x margin on the deployed seeds).
    r = _ar1(2500, 0.4, seed=8)
    se_a = tb.bootstrap_sharpe_se(r, 96, 8000, np.random.default_rng(1))
    se_b = tb.bootstrap_sharpe_se(r, 96, 16000, np.random.default_rng(2))
    assert abs(se_a / se_b - 1.0) < 0.05


def test_boot_se_L1_matches_plain_iid_bootstrap():
    r = _ar1(2000, 0.0, seed=6)  # phi=0 -> i.i.d.
    rng = np.random.default_rng(20)
    # plain i.i.d. bootstrap SE of the Sharpe
    B, T = 4000, len(r)
    sr_b = []
    for _ in range(B):
        s = r[rng.integers(0, T, T)]
        sr_b.append(s.mean() / s.std(ddof=0))
    plain = float(np.std(sr_b, ddof=1))
    boot = tb.bootstrap_sharpe_se(r, 1, B, np.random.default_rng(21))
    assert abs(boot / plain - 1.0) < 0.10


def test_mertens_se_matches_sqrt_variance():
    from backtest.tier6_dsr import mertens_variance
    sr, g3, g4, T = 0.01, -0.2, 8.0, 2500
    assert tb.mertens_se(sr, g3, g4, T) == np.sqrt(mertens_variance(sr, g3, g4, T))


def test_substream_rng_stable_and_keyed():
    a = tb.substream_rng("abc123", 24)
    b = tb.substream_rng("abc123", 24)
    # same key -> identical stream
    assert a.random() == b.random()
    # different block_len -> different stream
    assert tb.substream_rng("abc123", 24).random() != tb.substream_rng("abc123", 48).random()
    # different hash -> different stream
    assert tb.substream_rng("abc123", 24).random() != tb.substream_rng("def456", 24).random()
    # different base_seed -> different stream (PFR: --seed must not be a no-op)
    assert tb.substream_rng("abc123", 24, 1).random() != tb.substream_rng("abc123", 24, 2).random()


def test_substream_rng_order_independent():
    # building stream for (hashB, 24) does not depend on whether (hashA, 24) was built first
    s1 = tb.substream_rng("hashB", 24).random()
    _ = tb.substream_rng("hashA", 24).random()
    s2 = tb.substream_rng("hashB", 24).random()
    assert s1 == s2


# ==========================================================================
# Path-2 (Erratum E1) — primitive refactor: _bootstrap_sharpe_stats + skip
# ==========================================================================
def test_bootstrap_stats_returns_sr_array_and_skip():
    # dense i.i.d. Gaussian: skip_fraction ~ 0; sr_b array near-full length.
    r = np.random.default_rng(42).standard_normal(2000)
    sr_b, skip = tb._bootstrap_sharpe_stats(r, 6, 1000, np.random.default_rng(1))
    assert isinstance(sr_b, np.ndarray)
    assert 0.0 <= skip < 0.01
    assert sr_b.shape[0] == 1000 - round(skip * 1000)
    assert np.all(np.isfinite(sr_b))


def test_bootstrap_stats_feeds_same_se_as_public_primitive():
    # The sr_b array from _bootstrap_sharpe_stats, on a clean input, must give
    # the SAME SE as bootstrap_sharpe_se when both consume an identical RNG.
    r = _ar1(1500, 0.3, seed=4)
    sr_b, skip = tb._bootstrap_sharpe_stats(r, 12, 2000, np.random.default_rng(11))
    se_stats = float(sr_b.std(ddof=1))
    se_public = tb.bootstrap_sharpe_se(r, 12, 2000, np.random.default_rng(11))
    assert skip == 0.0
    assert se_stats == pytest.approx(se_public, rel=1e-12)


def test_skip_fraction_zero_on_dense_iid():
    # bootstrap_skip_fraction must be 0.0 on a dense i.i.d. Gaussian series.
    r = np.random.default_rng(7).standard_normal(2500)
    skip = tb.bootstrap_skip_fraction(r, 24, 1000, np.random.default_rng(3))
    assert skip == 0.0


def test_skip_fraction_positive_on_sparse_series():
    # Sparse, *clustered* nonzeros (mirrors the real low-trade-frequency cohort:
    # the empirical degeneracy is driven by long contiguous zero stretches, not
    # random scatter). At long blocks (L=96) a circular block can land entirely
    # inside a zero stretch, so a resample can be all-zero -> skip_fraction > 0.
    # The probe does NOT raise (it is the degeneracy MEASUREMENT, per E1.5).
    T = 2400
    r = np.zeros(T)
    # ~20 nonzeros packed into a single short window; the rest is a long zero run.
    r[100:120] = np.random.default_rng(99).standard_normal(20)
    skip = tb.bootstrap_skip_fraction(r, 96, 1000, np.random.default_rng(5))
    assert skip > 0.0


def test_skip_fraction_does_not_raise_on_all_zero():
    # all-zero series: 100% degenerate; bootstrap_sharpe_se RAISES, but
    # bootstrap_skip_fraction must return 1.0 without raising.
    skip = tb.bootstrap_skip_fraction(np.zeros(500), 6, 200, np.random.default_rng(0))
    assert skip == pytest.approx(1.0)


def test_skip_fraction_rejects_nonfinite():
    r = np.array([np.nan, 1.0, 2.0, 3.0])
    with pytest.raises(ValueError, match="finite"):
        tb.bootstrap_skip_fraction(r, 6, 100, np.random.default_rng(0))


def test_public_se_still_raises_on_flat_series():
    # regression: the public strict primitive keeps its raise-on-degenerate.
    with pytest.raises(ValueError, match="degenerate"):
        tb.bootstrap_sharpe_se(np.zeros(500), 6, 100, np.random.default_rng(0))


# ==========================================================================
# Path-2 (Erratum E1) — suitability runner + emitters + CLI
# ==========================================================================
def test_load_finite_returns_drops_leading_nan():
    from backtest.tier6_dsr import _read_cohort_csv, derive_cohort, HOLDOUT_DIR

    df = _read_cohort_csv()
    locked, _ = derive_cohort(df)
    h = locked[0]
    arr = tb._load_finite_returns(h, HOLDOUT_DIR)
    assert isinstance(arr, np.ndarray)
    assert np.all(np.isfinite(arr))
    # finite-filtered length T == sealed T_obs for this candidate
    t_obs = int(df.loc[df["hypothesis_hash"] == h, "T_obs"].iloc[0])
    assert arr.shape[0] == t_obs


def test_sealed_sha256_keys_cover_all_files():
    shas = tb._sealed_tier6_dsr_sha256()
    sealed_dir = tb.SEALED_TIER6_DSR_DIR
    on_disk = {p.name for p in sealed_dir.iterdir() if p.is_file()}
    assert set(shas.keys()) == on_disk
    assert len(shas) == 4
    assert all(len(v) == 64 for v in shas.values())


def test_evaluate_candidate_suitability_record_schema():
    from backtest.tier6_dsr import (
        _read_cohort_csv,
        derive_cohort,
        load_candidate_moments,
        HOLDOUT_DIR,
    )

    df = _read_cohort_csv()
    locked, _ = derive_cohort(df)
    h = locked[0]
    cm = load_candidate_moments(h, df, holdout_dir=HOLDOUT_DIR)
    returns = tb._load_finite_returns(h, HOLDOUT_DIR)
    rec = tb.evaluate_candidate_suitability(
        cm, returns, n_replicates=300, base_seed=tb.BASE_SEED
    )
    for key in (
        "hypothesis_hash", "name", "theme", "T", "nonzero_count",
        "zero_fraction", "sr_per_bar", "sr_star_B", "excess", "deflated_z_B",
        "skip_L1", "skip_L6", "skip_L12", "skip_L24", "skip_L48", "skip_L96",
    ):
        assert key in rec, f"missing {key}"
    assert rec["T"] == cm.T
    assert rec["nonzero_count"] == int(np.count_nonzero(returns))
    assert rec["zero_fraction"] == pytest.approx(1.0 - rec["nonzero_count"] / cm.T)
    # excess is moment-independent of bootstrap and equals sr - sr_star_B
    assert rec["excess"] == pytest.approx(rec["sr_per_bar"] - rec["sr_star_B"])
    for L in tb.BLOCK_LEN_GRID:
        assert 0.0 <= rec[f"skip_L{L}"] <= 1.0


def test_run_cohort_suitability_counts_and_invariance():
    res = tb.run_cohort_suitability(n_replicates=300, base_seed=tb.BASE_SEED)
    assert isinstance(res, tb.CohortSuitabilityResult)
    assert len(res.authoritative) == 18
    assert len(res.companion) == 21
    att = res.attestation
    assert att["all_excess_negative"] is True
    assert att["max_excess"] == pytest.approx(-0.004436, abs=1e-4)
    assert att["verdict_invariant"] is True
    assert att["conclusion"] == "measurement_inconclusive_sparse_cohort"
    # Degeneracy is real on this sparse cohort: at the longest block (L=96) at
    # least one candidate has zero-variance resamples. Empirically the strongest
    # degeneracy on THIS cohort sits in the companion partition (the sparsest
    # candidate, ~27% skip at L96, is a companion), so the demonstration spans
    # the full cohort (authoritative + companion), which is the methodologically
    # honest "bootstrap is unreliable here" evidence per Erratum E1.
    skip96 = [r["skip_L96"] for r in (*res.authoritative, *res.companion)]
    assert max(skip96) > 0.0
    # the degeneracy_summary records the same fact (skip-by-L over the cohort)
    assert att["degeneracy_summary"]["skip_L96"]["max"] > 0.0


def test_tie_back_deflated_z_matches_sealed():
    from backtest.tier6_dsr import MOMENT_RECOMPUTE_EPS

    res = tb.run_cohort_suitability(n_replicates=300, base_seed=tb.BASE_SEED)
    sealed = pd.read_csv(
        tb.SEALED_TIER6_DSR_DIR / "tier6_dsr_results.csv"
    ).set_index("hypothesis_hash")
    for r in res.authoritative:
        sealed_z = float(sealed.loc[r["hypothesis_hash"], "deflated_z_B"])
        assert r["deflated_z_B"] == pytest.approx(sealed_z, abs=MOMENT_RECOMPUTE_EPS)


def test_sealed_artifacts_byte_immutable_across_run():
    before = tb._sealed_tier6_dsr_sha256()
    tb.run_cohort_suitability(n_replicates=200, base_seed=tb.BASE_SEED)
    after = tb._sealed_tier6_dsr_sha256()
    assert before == after


def test_emit_artifacts_schema_no_inflation_columns(tmp_path):
    res = tb.run_cohort_suitability(n_replicates=200, base_seed=tb.BASE_SEED)
    paths = tb.emit_artifacts(res, out_dir=tmp_path)
    diag = tmp_path / "suitability_diagnostic.csv"
    comp = tmp_path / "suitability_companion.csv"
    att = tmp_path / "suitability_attestation.json"
    assert set(paths.values()) == {diag, comp, att}
    assert diag.exists() and comp.exists() and att.exists()
    # banner is the leading commented line; pandas reads past it with comment="#"
    first_line = diag.read_text().splitlines()[0]
    assert first_line.startswith("#")
    assert "NON-AUTHORITATIVE" in first_line
    d = pd.read_csv(diag, comment="#")
    assert len(d) == 18
    expected_cols = [
        "hypothesis_hash", "name", "theme", "T", "nonzero_count",
        "zero_fraction", "sr_per_bar", "sr_star_B", "excess",
        "skip_L1", "skip_L6", "skip_L12", "skip_L24", "skip_L48", "skip_L96",
    ]
    # EXACT on-disk schema — no deflated_z_B / deflated_z_degenerate / inflation leak
    assert set(d.columns) == set(expected_cols)
    for col in d.columns:
        assert "inflation" not in col
        assert "serialcorr" not in col
        assert "degenerate" not in col
        assert col != "deflated_z_B"
        assert not col.startswith("pass_")
    c = pd.read_csv(comp, comment="#")
    assert len(c) == 21
    payload = json.loads(att.read_text())
    assert payload["conclusion"] == "measurement_inconclusive_sparse_cohort"
    assert payload["all_excess_negative"] is True
    assert "inflation_ratio_summary" not in payload


def test_cli_dry_run_writes_nothing(tmp_path):
    out = tmp_path / "out"
    rc = tb.main(["--dry-run", "--n-replicates", "100", "--out-dir", str(out)])
    assert rc == 0
    assert not out.exists() or not any(out.iterdir())


def test_cli_bad_cohort_exits_nonzero(tmp_path):
    rc = tb.main([
        "--cohort", "this_cohort_does_not_exist",
        "--n-replicates", "100",
        "--out-dir", str(tmp_path / "o"),
    ])
    assert rc == 1

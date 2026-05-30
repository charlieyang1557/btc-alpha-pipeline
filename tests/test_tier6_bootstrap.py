# tests/test_tier6_bootstrap.py
import numpy as np
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

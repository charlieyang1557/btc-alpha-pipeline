"""TDD tests for the Evaluation-Gate Power Study (backtest/eval_power.py).

Encodes hand-computed anchors from the design spec
docs/superpowers/specs/2026-06-02-evaluation-gate-power-study-design.md (§4, §5).
All anchors were independently confirmed against backtest/tier6_dsr.py's
sr_star / mertens_variance / Z_PASS primitives before this file was written.

These tests are written FIRST (RED) — backtest.eval_power does not yet exist.
"""
from __future__ import annotations

import math

import pytest

# Module under test (does not exist yet at RED time).
from backtest import eval_power
from backtest.tier6_dsr import Z_PASS, mertens_variance, sr_star

# ---- spec anchors (hand-computed, cross-checked against primitives) ----
SR_STAR_HOURLY = 0.016968084108918483  # sr_star(N*=3, T=2527, form="B")
T_HOURLY = 2527
PPY_HOURLY = 8760
PPY_DAILY = 365
Z_POWER = 0.8416
SQRT_8760 = math.sqrt(8760)  # 93.59487...


# --------------------------------------------------------------------------
# §4.1 just-significant DSR bar (≈50% power) — the bar a book must EXCEED.
# --------------------------------------------------------------------------
def test_hourly_just_significant_bar_gaussian():
    """Hourly gate, Gaussian arm γ3=0, γ4=3 evaluated THROUGH Mertens.

    NOTE the σ_denom subtlety: at γ4=3 the Mertens term is 1 + ((3−1)/4)·sr²
    = 1 + 0.5·sr², so σ_denom is NOT identically 1 — the spec's "Gaussian
    4.653" (§4.1) is this γ4=3-through-Mertens value (4.6531), distinct from
    the pure σ_denom≡1 shortcut (4.6512, asserted separately below). The
    fixed-point solver correctly evaluates the Mertens term at the γ4=3 arm."""
    per_bar = eval_power.just_significant_per_bar(
        SR_STAR_HOURLY, T_HOURLY, gamma3=0.0, gamma4=3.0
    )
    ann = eval_power.annualize(per_bar, PPY_HOURLY)
    assert ann == pytest.approx(4.653, abs=1e-3)  # spec §4.1 "Gaussian 4.653"


def test_hourly_just_significant_pure_sigma1_shortcut():
    """The pure σ_denom≡1 shortcut (term identically 1) gives 4.6512 — the
    reference the spec's §4.2 'σ_denom ≈ 1 shortcut' alludes to, slightly BELOW
    the γ4=3-through-Mertens 4.6531 (the +0.5·sr² kurtosis-term contribution)."""
    root_t = math.sqrt(T_HOURLY - 1)
    pure_sigma1_per_bar = SR_STAR_HOURLY + Z_PASS / root_t
    assert eval_power.annualize(pure_sigma1_per_bar, PPY_HOURLY) == pytest.approx(
        4.6512, abs=1e-3
    )


def test_hourly_just_significant_bar_heavy_tail():
    """With observed moments γ3=0.14036, γ4=11.30944 the heavy-tail
    just-significant bar ≈ 4.650 annualized (barely below the Gaussian 4.651
    — the spec's 'robust to heavy tails' at the hourly significance bar)."""
    per_bar = eval_power.just_significant_per_bar(
        SR_STAR_HOURLY, T_HOURLY, gamma3=0.14036, gamma4=11.30944
    )
    ann = eval_power.annualize(per_bar, PPY_HOURLY)
    assert ann == pytest.approx(4.650, abs=2e-3)


# --------------------------------------------------------------------------
# §4.2 80%-power MDE — the load-bearing number §5 compares against.
# --------------------------------------------------------------------------
def test_hourly_mde_gaussian_load_bearing_distinction():
    """Gaussian hourly 80%-power MDE (γ4=3 through Mertens): the pure σ≡1
    seed is 0.016968 + (1.6449+0.8416)/50.2593 ≈ 0.06644/bar → × 93.5949
    ≈ 6.2185; the γ4=3 fixed point lifts it slightly (+0.5·sr² term) to
    ≈ 6.2236. Both round to the spec's ≈ 6.22 and are strictly ABOVE the
    4.65 significance bar (the load-bearing distinction)."""
    mde = eval_power.mde_per_bar(SR_STAR_HOURLY, T_HOURLY, gamma3=0.0, gamma4=3.0)
    mde_ann = eval_power.annualize(mde, PPY_HOURLY)
    assert mde_ann == pytest.approx(6.22, abs=0.02)
    # The load-bearing distinction: power-MDE strictly exceeds the sig bar.
    sig_ann = eval_power.annualize(
        eval_power.just_significant_per_bar(SR_STAR_HOURLY, T_HOURLY, 0.0, 3.0),
        PPY_HOURLY,
    )
    assert mde_ann > sig_ann + 1.0  # ~6.22 vs ~4.65


def test_hourly_mde_observed_heavy_tail_close_to_gaussian():
    """At the hourly gate the per-bar Sharpe (~0.066) is small so the
    heavy-tail correction is negligible: observed-moment MDE ≈ Gaussian MDE."""
    mde_g = eval_power.mde_per_bar(SR_STAR_HOURLY, T_HOURLY, 0.0, 3.0)
    mde_obs = eval_power.mde_per_bar(SR_STAR_HOURLY, T_HOURLY, 0.14036, 11.30944)
    assert abs(mde_obs - mde_g) / mde_g < 0.01  # < 1% at the hourly gate


# --------------------------------------------------------------------------
# §4.2 fixed-point convergence + daily-arm heavy-tail materiality.
# --------------------------------------------------------------------------
def test_mde_fixed_point_converges_and_returns_iteration_count():
    """The MDE solver iterates sigma_denom evaluated AT the mde (implicit eq)
    and converges; the diagnostic form reports a finite iteration count."""
    mde, iters, converged = eval_power.mde_per_bar_diagnostic(
        SR_STAR_HOURLY, T_HOURLY, gamma3=0.14036, gamma4=11.30944
    )
    assert converged is True
    assert 1 <= iters < 100
    assert math.isfinite(mde) and mde > 0


def test_daily_arm_heavy_tail_mde_exceeds_gaussian_materially():
    """On a daily 1-yr arm at γ4≈60 the per-bar Sharpe is 3-4× larger, so the
    fixed-point heavy-tail MDE EXCEEDS the σ=1 Gaussian value materially
    (spec: +15% to +37% on the daily arms). For T=365 this is ≈ +21%."""
    ss = sr_star(3, PPY_DAILY, "B")
    mde_g = eval_power.mde_per_bar(ss, PPY_DAILY, gamma3=0.0, gamma4=3.0)
    mde_heavy = eval_power.mde_per_bar(ss, PPY_DAILY, gamma3=0.0, gamma4=60.0)
    pct = (mde_heavy / mde_g - 1.0) * 100.0
    assert pct > 15.0  # materially above Gaussian on the daily arm


# --------------------------------------------------------------------------
# Monotonicity sanity (§4.3 sweep directions).
# --------------------------------------------------------------------------
def test_mde_ann_decreases_as_T_grows():
    """Annualized MDE decreases as the OOS window lengthens: 105-day hourly
    (T=2527, ppy=8760) > daily 1-yr > 2-yr > 3-yr."""
    g3, g4 = 0.0, 11.3
    mde_hourly = eval_power.annualize(
        eval_power.mde_per_bar(sr_star(3, 2527, "B"), 2527, g3, g4), 8760
    )
    mdes_daily = [
        eval_power.annualize(
            eval_power.mde_per_bar(sr_star(3, T, "B"), T, g3, g4), PPY_DAILY
        )
        for T in (365, 730, 1095)
    ]
    assert mde_hourly > mdes_daily[0] > mdes_daily[1] > mdes_daily[2]


def test_mde_increases_with_n_star():
    """A larger multiplicity N* (3 → 18) raises sr_star and thus the MDE."""
    mde3 = eval_power.mde_per_bar(sr_star(3, 365, "B"), 365, 0.0, 11.3)
    mde18 = eval_power.mde_per_bar(sr_star(18, 365, "B"), 365, 0.0, 11.3)
    assert mde18 > mde3


def test_mde_increases_with_gamma4():
    """Heavier tails (larger γ4) raise the Mertens denominator → larger MDE."""
    ss = sr_star(3, 365, "B")
    m3 = eval_power.mde_per_bar(ss, 365, 0.0, 3.0)
    m11 = eval_power.mde_per_bar(ss, 365, 0.0, 11.3)
    m60 = eval_power.mde_per_bar(ss, 365, 0.0, 60.0)
    assert m3 < m11 < m60


def test_negative_skew_raises_mde():
    """γ3 < 0 raises σ_denom (Mertens term is 1 − γ3·sr + …) → larger MDE
    than the γ3 = 0 case at the same arm."""
    ss = sr_star(3, 365, "B")
    mde_zero = eval_power.mde_per_bar(ss, 365, gamma3=0.0, gamma4=11.3)
    mde_neg = eval_power.mde_per_bar(ss, 365, gamma3=-2.0, gamma4=11.3)
    assert mde_neg > mde_zero


# --------------------------------------------------------------------------
# §5 mechanical classifier (binding interpretation is the PI's, not ours).
# --------------------------------------------------------------------------
def test_classifier_build_viable():
    assert eval_power.classify_mde(1.5) == "BUILD-viable"
    assert eval_power.classify_mde(1.0) == "BUILD-viable"


def test_classifier_confirmation_limited():
    assert eval_power.classify_mde(3.0) == "confirmation-limited"
    assert eval_power.classify_mde(6.22) == "confirmation-limited"


def test_classifier_indeterminate():
    assert eval_power.classify_mde(2.0) == "INDETERMINATE"
    assert eval_power.classify_mde(1.51) == "INDETERMINATE"
    assert eval_power.classify_mde(2.99) == "INDETERMINATE"


# --------------------------------------------------------------------------
# §4.3 cost drag (net→gross). Documented convention in module docstring.
# --------------------------------------------------------------------------
def test_cost_drag_zero_turnover_is_zero():
    """No turnover → no drag."""
    assert eval_power.annual_cost_drag(
        turnover_one_way=0.0, rebalances_per_year=365, cost_bps_per_side=15.0
    ) == pytest.approx(0.0)


def test_cost_drag_scales_with_turnover_and_frequency():
    """Drag grows with one-way turnover and rebalance frequency. The gross
    Sharpe a net book needs = net MDE (per the spec, MDE reported in net
    terms) PLUS the cost drag expressed in the same annualized-Sharpe units."""
    drag_lo = eval_power.annual_cost_drag(0.3, 365, 15.0)
    drag_hi = eval_power.annual_cost_drag(0.7, 365, 15.0)
    assert drag_hi > drag_lo > 0.0


def test_gross_required_is_net_plus_drag():
    """gross_required_sharpe = net_mde_ann + cost_drag_ann (both annualized)."""
    gross = eval_power.gross_required_sharpe(
        net_mde_ann=2.0, turnover_one_way=0.5, rebalances_per_year=365,
        cost_bps_per_side=15.0,
    )
    drag = eval_power.annual_cost_drag(0.5, 365, 15.0)
    assert gross == pytest.approx(2.0 + drag)


# --------------------------------------------------------------------------
# §4.4 Half B IR ceiling.
# --------------------------------------------------------------------------
def test_n_eff_equicorrelation_primary():
    """Equicorrelation N_eff = N / (1 + (N−1)ρ). At ρ=0.8, N=20 → ≈ 1.23."""
    assert eval_power.n_eff_equicorrelation(20, 0.8) == pytest.approx(1.2346, abs=1e-3)


def test_n_eff_soft_sensitivity():
    """Soft form N_eff = (1−ρ)N + ρ. At ρ=0.8, N=20 → 4.8."""
    assert eval_power.n_eff_soft(20, 0.8) == pytest.approx(4.8, abs=1e-9)


def test_independent_bets_per_year():
    """independent_bets_per_year = rebalances_per_year · (1 − ρ_rank)."""
    assert eval_power.independent_bets_per_year(365, 0.9) == pytest.approx(36.5)
    assert eval_power.independent_bets_per_year(365, 0.5) == pytest.approx(182.5)


def test_ir_ann_fundamental_law_uses_primary_n_eff():
    """IR_ann = IC · sqrt(N_eff · independent_bets_per_year). With IC=0.05,
    N=20, ρ=0.8 (N_eff≈1.2346), daily rebalance, ρ_rank=0.5 (bets=182.5):
    BR ≈ 225.3, sqrt ≈ 15.01, gross IR ≈ 0.75."""
    ir = eval_power.ir_ann_gross(
        ic=0.05, n=20, rho=0.8, rebalances_per_year=365, rho_rank=0.5
    )
    n_eff = eval_power.n_eff_equicorrelation(20, 0.8)
    br = n_eff * eval_power.independent_bets_per_year(365, 0.5)
    assert ir == pytest.approx(0.05 * math.sqrt(br))


def test_ir_ann_net_subtracts_cross_sectional_drag():
    """Net IR = gross IR − cross-sectional turnover × 15bps drag (annualized)."""
    net = eval_power.ir_ann_net(
        ic=0.05, n=20, rho=0.8, rebalances_per_year=365, rho_rank=0.5,
        turnover_one_way=0.5, cost_bps_per_side=15.0,
    )
    gross = eval_power.ir_ann_gross(0.05, 20, 0.8, 365, 0.5)
    drag = eval_power.annual_cost_drag(0.5, 365, 15.0)
    assert net == pytest.approx(gross - drag)


# --------------------------------------------------------------------------
# Result-B2 additions: single-source-of-truth pin, NaN-guard parity,
# achievability correctness, N*=1 no-multiplicity floor.
# --------------------------------------------------------------------------
@pytest.mark.parametrize(
    "g3,g4,sr,T",
    [
        (0.0, 3.0, 0.05, 2527),
        (0.14036, 11.30944, 0.07, 365),
        (-2.0, 11.30944, 0.10, 730),
        (0.0, 60.0, 0.24, 365),
    ],
)
def test_sigma_denom_equivalent_to_mertens_variance(g3, g4, sr, T):
    """SINGLE-SOURCE-OF-TRUTH pin (B2): the inline sigma_denom must equal the
    tier6_dsr Mertens variance × (T−1) to floating-point precision, so any
    drift in tier6_dsr's formula is caught here rather than silently diverging.
    """
    lhs = eval_power.sigma_denom(g3, g4, sr) ** 2
    rhs = mertens_variance(sr, g3, g4, T) * (T - 1)  # NB arg order: sr FIRST
    assert lhs == pytest.approx(rhs, rel=1e-12)


def test_sigma_denom_rejects_non_finite():
    """NaN-guard parity with tier6_dsr.mertens_variance (B2-Codex): non-finite
    input raises rather than silently propagating NaN into the fixed point."""
    with pytest.raises(ValueError):
        eval_power.sigma_denom(0.0, float("nan"), 0.05)


def test_achievability_flags_under_immutable_splits():
    """B2-CORRECTED: only the clean ~105-day forward_2026 arms are achievable;
    any OOS longer than that window reuses a designated (2024 val / 2025 test)
    window → governance-blocked. The daily_1yr=True flag was the B2 bug."""
    flags = {d.name: d.achievable for d in eval_power.OOS_DESIGNS}
    assert flags["hourly_105d"] is True
    assert flags["daily_105d"] is True
    assert flags["daily_1yr"] is False  # was the B2 bug (needs 365 > ~105 bars)
    assert flags["daily_2yr"] is False
    assert flags["daily_3yr"] is False
    assert flags["6h_1yr"] is False


def test_n_star_1_is_no_multiplicity_floor():
    """N*=1 (single pre-registered hypothesis) uses sr_star=0 (no expected-max
    deflation) → the most-favorable MDE; still confirmation-limited at the
    achievable hourly gate (the 1/sqrt(T) increment dominates, not multiplicity).
    """
    rows = {r["arm"]: r for r in eval_power._build_half_a()}
    arm = rows["hourly_105d|N*=1|observed"]
    assert arm["sr_star"] == 0.0
    assert arm["classification"] == "confirmation-limited"

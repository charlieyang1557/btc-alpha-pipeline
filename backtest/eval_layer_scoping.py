"""Bayesian / continuous-evidence eval-layer scoping — read-only analysis.

Implements the SV1-SV7 spot-checks of the design spec
docs/superpowers/specs/2026-06-02-bayesian-eval-layer-scoping-design.md (§4).
Each function verifies ONE load-bearing claim that a mechanism's §5
classification hinges on. Purely analytical / read-only: closed-form checks
plus one tiny Monte-Carlo (SV2). No data is spent, no holdout touched, no
strategy run on held data, no peek.

# CONTRACT BOUNDARY (mirrors eval_power.py / eval_power_mc.py): IMPORT-PRIMITIVES
# -ONLY. Imports Z_PASS + constants from backtest.eval_power and reuses
# eval_power.{sigma_denom, annualize, annual_cost_drag} +
# eval_power_mc.inject_iid_gaussian. It MUST NEVER call evaluate_cohort() or any
# writer into the sealed directory. The only write it ever performs is to its OWN
# non-sealed data/eval_gate_power_study/eval_layer_scoping_v1.json, from __main__.

## The honest framing (spec §1)
A Bayesian / continuous-evidence layer cannot manufacture statistical power on a
fixed window — the ~4.63/6.22 MDE wall is a noise hurdle set by T and N*. These
spot-checks separate genuine value (a different estimand with genuinely different
power; optional-stopping-valid accrual) from illusory value (re-labelling the same
low power as a posterior; pooling that shrinks toward a non-confirming cohort).

## SV3 cohort grounding (read-only)
The 12 Path B/A/C/D forward_2026 holdout Sharpes are read from the sealed verdict
artifacts data/phase2c_evaluation_gate/path{b,a,c,d}_verdict_v1/*advisory.json
(holdouts.H{1,2,3}.holdout_sharpe). They are pinned here as a documented constant
(mean = -2.5467); test_sv3_cohort_mean re-derives the mean.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

# CONTRACT BOUNDARY (see module docstring): primitives ONLY.
from backtest.eval_power import (
    DAYS_PER_YEAR,
    HOURS_PER_YEAR,
    Z_PASS,
    Z_POWER,
    annual_cost_drag,
    annualize,
    sigma_denom,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = PROJECT_ROOT / "data/eval_gate_power_study"
RESULTS_PATH = RESULTS_DIR / "eval_layer_scoping_v1.json"

# The current forward_2026 gate (spec §1): 105-day hourly OOS.
FORWARD_T = 2527
FORWARD_PPY = HOURS_PER_YEAR  # 8760

# The 12 Path B/A/C/D forward_2026 holdout Sharpes (read-only, from the sealed
# verdict artifacts; mean = -2.5467). Used only by SV3's pooling model.
PATH_LEG_SHARPES: tuple[float, ...] = (
    -8.420904550229412, -2.6470149389802504, -2.6148202577212065,   # Path B H1/H2/H3
    -1.7699223702893294, -2.981266187179422, -1.6205971377803847,   # Path A
    -0.8675514207689904, -2.8283736698043427, 0.0,                  # Path C
    -0.7508226746898683, -2.505268495035567, -3.5540893055627825,   # Path D
)

# A modest deployable edge (spec §1 / §5): the ~1.0-1.5 ann-Sharpe band.
DEPLOYABLE_SHARPE = 1.5
DEPLOY_LINE_LOW = 1.0  # the low end of the deploy band; backfire is "below this"
BTC_REALIZED_G4 = 11.30944  # observed-moment anchor (Path D H1); BTC tails ~ this


# --------------------------------------------------------------------------
# Shared helpers.
# --------------------------------------------------------------------------
def _phi(x: float) -> float:
    """Standard-normal CDF via erf."""
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def se_ann(T: int, ppy: int, gamma3: float = 0.0, gamma4: float = 3.0,
           sr_pb: float = 0.0) -> float:
    """Standard error of the ANNUALIZED Sharpe estimator over an OOS window.

    sr_hat (per-bar) ~ Normal(sr, sigma_denom^2/(T-1)); annualized by sqrt(ppy).
    At the Gaussian null (sigma_denom=1) over the forward gate this is
    sqrt(8760/2526) ≈ 1.862 — the candidate's irreducible Sharpe uncertainty.
    """
    return sigma_denom(gamma3, gamma4, sr_pb) * math.sqrt(ppy) / math.sqrt(T - 1)


# --------------------------------------------------------------------------
# SV1 (M1) — posterior-over-Sharpe -> continuous sizing ruin profile.
# --------------------------------------------------------------------------
def full_kelly_fraction(sharpe_ann: float, vol_ann: float) -> float:
    """Full-Kelly leverage for a strategy of annualized Sharpe / vol = mu/sigma^2."""
    return sharpe_ann / vol_ann


def prob_sharpe_le_zero(sharpe_ann: float, se_ann_val: float) -> float:
    """P(true Sharpe <= 0 | observed = sharpe_ann) under a flat prior = Phi(-s/se)."""
    return _phi(-sharpe_ann / se_ann_val)


def sv1_sizing_profile(sharpe_ann: float = DEPLOYABLE_SHARPE,
                       vol_ann: float = 0.60) -> dict:
    """SV1: a posterior-sizing rule does not add power and is capital-dangerous.

    For a single candidate whose posterior straddles zero, fractional-Kelly just
    re-labels the same ~20% gate detection as a sizing choice while exposing real
    capital to a ~1-in-5 sign error.
    """
    se = se_ann(FORWARD_T, FORWARD_PPY)
    p_le0 = prob_sharpe_le_zero(sharpe_ann, se)
    return {
        "full_kelly_fraction": full_kelly_fraction(sharpe_ann, vol_ann),
        "quarter_kelly_fraction": 0.25 * full_kelly_fraction(sharpe_ann, vol_ann),
        "se_ann": se,
        "prob_sharpe_le_zero": p_le0,
        "no_power_gain": True,  # sizing relocates the problem to allocation
        "note": (
            "P(SR<=0)~21% at se_ann~1.86; size-by-evidence on a straddling-zero "
            "posterior puts capital on noise. Decision-value modest-to-negative "
            "for a solo with no candidate book."
        ),
    }


# --------------------------------------------------------------------------
# SV3 (M3) — hierarchical pooling backfires (assumption-disclosed band).
# --------------------------------------------------------------------------
def cohort_mean() -> float:
    """Mean of the 12 Path leg Sharpes (the pooled-prior location)."""
    return sum(PATH_LEG_SHARPES) / len(PATH_LEG_SHARPES)


def _cohort_var() -> float:
    """Observed cross-leg variance (ddof=1) of the 12 Path leg Sharpes."""
    mu = cohort_mean()
    n = len(PATH_LEG_SHARPES)
    return sum((x - mu) ** 2 for x in PATH_LEG_SHARPES) / (n - 1)


def normal_normal_posterior_mean(y: float, prior_mean: float, tau2: float,
                                 se2: float) -> float:
    """Conjugate normal-normal posterior mean = prior + (tau2/(tau2+se2))(y-prior)."""
    w = tau2 / (tau2 + se2)
    return prior_mean + w * (y - prior_mean)


def sv3_shrinkage(y: float = DEPLOYABLE_SHARPE) -> dict:
    """SV3: pooling a +y candidate with the non-confirming cohort shrinks it
    below the deploy line under BOTH hyperprior-variance choices.

    Raw observed cross-leg variance tau2 (less shrinkage) -> ~ -0.26; the standard
    de-noised between-group variance tau2 = obs_var - mean(se^2) (more shrinkage)
    -> ~ -1.6. Both << the 1.0-1.5 deploy line => backfire robust to the choice.
    The only hyperprior wide enough to avoid the backfire makes pooling a no-op of
    the per-candidate test already run (advisor sharpening).
    """
    mu = cohort_mean()
    obs_var = _cohort_var()
    se2 = se_ann(FORWARD_T, FORWARD_PPY) ** 2  # per-leg sampling variance (~3.47)
    tau2_raw = obs_var
    tau2_denoised = max(obs_var - se2, 0.0)
    post_raw = normal_normal_posterior_mean(y, mu, tau2_raw, se2)
    post_denoised = normal_normal_posterior_mean(y, mu, tau2_denoised, se2)
    return {
        "cohort_mean": mu,
        "cohort_obs_var": obs_var,
        "per_leg_se2": se2,
        "tau2_raw": tau2_raw,
        "tau2_denoised": tau2_denoised,
        "posterior_mean_raw": post_raw,
        "posterior_mean_denoised": post_denoised,
        "deploy_line_low": DEPLOY_LINE_LOW,
        "backfires": (post_raw < DEPLOY_LINE_LOW and post_denoised < DEPLOY_LINE_LOW),
        "note": (
            "pooling borrows 'strength' = evidence of no edge; both posteriors are "
            "negative, far below the deploy line. Axis-1 = backfires."
        ),
    }


# --------------------------------------------------------------------------
# SV4 (M4) — a skeptical prior can only tighten confirmation.
# --------------------------------------------------------------------------
def sv4_skeptical_direction(y: float = DEPLOYABLE_SHARPE) -> dict:
    """SV4: a prior whose LOCATION is <= y pulls the posterior below the data
    point y -> only tightens (never loosens) confirmation. Honesty upgrade, not
    a power upgrade. Two skeptical locations checked: 0 (no-edge) and the cohort
    mean (negative)."""
    se2 = se_ann(FORWARD_T, FORWARD_PPY) ** 2
    prior_var = 1.0  # a moderate skeptical scale (location, not scale, is the lever)
    post_at_zero = normal_normal_posterior_mean(y, 0.0, prior_var, se2)
    post_at_cohort = normal_normal_posterior_mean(y, cohort_mean(), prior_var, se2)
    return {
        "posterior_mean": post_at_zero,
        "posterior_mean_skeptical_zero": post_at_zero,
        "posterior_mean_skeptical_cohort": post_at_cohort,
        "data_only_estimate": y,
        "only_tightens": (post_at_zero < y and post_at_cohort < y),
        "raises_power": False,
        "note": "skeptical location lowers the posterior below y; Axis-1=no-power-gain, Axis-2=modest (honesty).",
    }


# --------------------------------------------------------------------------
# SV5 (M5) — always-valid / e-value attainability (only-via-time on power).
# --------------------------------------------------------------------------
def expected_log_lr(sharpe_ann: float, T: int, ppy: int) -> float:
    """Expected log-likelihood-ratio (nats) of H1(Sharpe=delta) vs H0 over T iid
    bars = T * 0.5 * delta_pb^2, with delta_pb = sharpe_ann/sqrt(ppy)."""
    delta_pb = sharpe_ann / math.sqrt(ppy)
    return T * 0.5 * delta_pb * delta_pb


def sv5_attainability(sharpe_ann: float = DEPLOYABLE_SHARPE,
                      alpha: float = 0.05) -> dict:
    """SV5: an e-value for a true 1.5-Sharpe edge needs ~2.7 more years of hourly
    data to cross the alpha=0.05 deploy threshold (e>=1/alpha=20) -> the lever is
    TIME, not the inference framework. Decision-value (optional-stopping-valid
    monitoring) is assessed separately on Axis-2."""
    delta_pb = sharpe_ann / math.sqrt(FORWARD_PPY)
    per_bar_loglr = 0.5 * delta_pb * delta_pb
    log_e_threshold = math.log(1.0 / alpha)
    bars = log_e_threshold / per_bar_loglr
    return {
        "expected_log_lr_over_forward_T": expected_log_lr(
            sharpe_ann, FORWARD_T, FORWARD_PPY
        ),
        "e_value_over_forward_T": math.exp(
            expected_log_lr(sharpe_ann, FORWARD_T, FORWARD_PPY)
        ),
        "log_e_threshold": log_e_threshold,
        "bars_to_threshold": bars,
        "years_to_threshold": bars / FORWARD_PPY,
        "only_via_time": True,
        "note": (
            "e ~ 1.38 over the forward window vs the 20 needed; ~2.7 yr of fresh "
            "hourly tape to cross. Axis-1=only-via-time; Axis-2 (anytime-valid "
            "monitoring) judged in the memo."
        ),
    }


# --------------------------------------------------------------------------
# SV6 (M6) — change-the-estimand power comparison (VERDICT-CRITICAL), cost-gated.
# --------------------------------------------------------------------------
def power_sharpe_test(sharpe_ann: float, T: int, ppy: int,
                      gamma3: float = 0.0, gamma4: float = 3.0,
                      z_alpha: float = Z_PASS) -> float:
    """One-sided Sharpe-test power at a true annualized Sharpe over T bars.

    NCP = delta_pb*sqrt(T-1)/sigma_denom; power = 1 - Phi(z_alpha - NCP).
    At 1.5 ann over the forward gate (Gaussian) this is ~0.20 — matches the MC.
    """
    delta_pb = sharpe_ann / math.sqrt(ppy)
    ncp = delta_pb * math.sqrt(T - 1) / sigma_denom(gamma3, gamma4, delta_pb)
    return 1.0 - _phi(z_alpha - ncp)


def power_sign_test(sharpe_ann: float, T: int, ppy: int,
                    z_alpha: float = Z_PASS) -> float:
    """One-sided directional (sign / hit-rate) test power at a true Sharpe.

    For Gaussian per-bar returns, P(up)=Phi(delta_pb); hits ~ Binomial(T, p).
    NCP_sign = (p-0.5)*2*sqrt(T); power = 1 - Phi(z_alpha - NCP_sign).
    """
    delta_pb = sharpe_ann / math.sqrt(ppy)
    p_up = _phi(delta_pb)
    ncp = (p_up - 0.5) * 2.0 * math.sqrt(T)
    return 1.0 - _phi(z_alpha - ncp)


def sign_test_are(sharpe_ann: float, ppy: int, gamma3: float = 0.0,
                  gamma4: float = 3.0) -> float:
    """Asymptotic relative efficiency of the sign test vs the Sharpe test =
    (NCP_sign/NCP_sharpe)^2. Gaussian -> 2/pi ~ 0.637. Heavy tails raise it
    (the Sharpe SE inflates) but at a modest per-bar Sharpe the inflation is tiny.
    """
    delta_pb = sharpe_ann / math.sqrt(ppy)
    p_up = _phi(delta_pb)
    ncp_sign = (p_up - 0.5) * 2.0  # per sqrt(T)
    ncp_sharpe = delta_pb / sigma_denom(gamma3, gamma4, delta_pb)  # per sqrt(T-1)~
    return (ncp_sign / ncp_sharpe) ** 2


def kurtosis_crossover(sharpe_ann: float, ppy: int) -> float:
    """The raw kurtosis gamma4 at which the sign test's NCP equals the Sharpe
    test's (i.e. the sign test starts to overtake) at this per-bar Sharpe.

    Sign overtakes when (p-0.5)*2 * sigma_denom > delta_pb, i.e. sigma_denom >
    delta_pb / ((p-0.5)*2). Solve sigma_denom^2 = 1 + (gamma4-1)/4 * delta_pb^2
    (gamma3=0) for gamma4.
    """
    delta_pb = sharpe_ann / math.sqrt(ppy)
    p_up = _phi(delta_pb)
    sd_needed = delta_pb / ((p_up - 0.5) * 2.0)
    # sd_needed^2 = 1 + (g4-1)/4 * delta^2  ->  g4 = 1 + 4*(sd^2-1)/delta^2
    return 1.0 + 4.0 * (sd_needed * sd_needed - 1.0) / (delta_pb * delta_pb)


def sv6_estimand_comparison(sharpe_ann: float = DEPLOYABLE_SHARPE) -> dict:
    """SV6 (verdict-critical): does a directional / hit-rate estimand raise power
    over Sharpe for a modest persistent edge?

    Result: NO at the deployable regime. The sign test is ~2/pi (0.637) efficient
    vs the Sharpe test for Gaussian; the heavy-tail rescue requires astronomical
    kurtosis at a modest per-bar Sharpe (BTC realized g4~11-30, crossover ~thousands).
    Even daily + g4=60 it does not overtake. Cost gate is therefore moot (M6
    already fails on power) but reported.
    """
    p_sharpe_h = power_sharpe_test(sharpe_ann, FORWARD_T, FORWARD_PPY,
                                   0.0, BTC_REALIZED_G4)
    p_sign_h = power_sign_test(sharpe_ann, FORWARD_T, FORWARD_PPY)
    are = sign_test_are(sharpe_ann, FORWARD_PPY)
    g4_cross_h = kurtosis_crossover(sharpe_ann, FORWARD_PPY)
    # Daily robustness: T=105 daily bars over the same clean window, g4=60 stress.
    are_daily_g4_60 = sign_test_are(sharpe_ann, DAYS_PER_YEAR, 0.0, 60.0)
    # Illustrative cost gate: the directional edge's per-bar hit-rate excess is
    # tiny (~0.6% at hourly); trading it pays 15bps/side. Reported for completeness.
    delta_pb = sharpe_ann / math.sqrt(FORWARD_PPY)
    hit_excess = _phi(delta_pb) - 0.5
    return {
        "power_sharpe_hourly": p_sharpe_h,
        "power_sign_hourly": p_sign_h,
        "are_sign_vs_sharpe": are,
        "kurtosis_crossover_hourly": g4_cross_h,
        "are_daily_g4_60": are_daily_g4_60,
        "sign_overtakes_daily_g4_60": are_daily_g4_60 > 1.0,
        "hit_rate_excess_hourly": hit_excess,
        "raises_power": p_sign_h > p_sharpe_h,
        "note": (
            "directional estimand is LESS powerful (ARE~0.637) at the modest "
            "hourly edge; heavy-tail rescue needs absurd kurtosis. Axis-1="
            "no-power-gain (mild loss). Cost gate moot."
        ),
    }


# --------------------------------------------------------------------------
# SV2 (M2) — sequential posterior gives no free fixed-horizon power (tiny MC).
# --------------------------------------------------------------------------
def sv2_no_acceleration(sharpe_ann: float = DEPLOYABLE_SHARPE, m: int = 2000,
                        seed: int = 20260602, T: int = FORWARD_T) -> dict:
    """SV2: an anytime-valid (mixture e-process) sequential rule detects a true
    1.5-Sharpe edge over [0, T] no more often than the fixed-horizon test at T
    -> the only power lever is accruing more T (M2 = only-via-time).

    Fixed-horizon: pass iff sr_hat*sqrt(T-1) >= Z_PASS. Sequential: a Gaussian
    mixture e-process e_t = sqrt(1/(1+t*tau2))*exp(S_t^2*tau2/(2(1+t*tau2)))
    (sigma=1), deploy iff e_t crosses 1/alpha=20 at ANY t<=T. tau matched to the
    alternative (generous to the sequential test).
    """
    rng = np.random.default_rng(seed)
    delta_pb = sharpe_ann / math.sqrt(FORWARD_PPY)
    # Population-level injection (same recipe as eval_power_mc.inject_iid_gaussian,
    # vectorized to an (m, T) matrix): y = delta_pb + N(0, 1).
    y = delta_pb + rng.standard_normal((m, T))
    # Fixed-horizon Sharpe test at T.
    sr_hat = y.mean(axis=1) / y.std(axis=1, ddof=0)
    detection_fixed = float((sr_hat * math.sqrt(T - 1) >= Z_PASS).mean())
    # Anytime-valid mixture e-process (sigma=1), tau matched to the alternative.
    tau2 = max(delta_pb * delta_pb, 1e-12)
    s = np.cumsum(y, axis=1)
    t = np.arange(1, T + 1, dtype=float)
    denom = 1.0 + t * tau2
    log_e = -0.5 * np.log(denom) + (s * s) * tau2 / (2.0 * denom)
    crossed = (log_e >= math.log(20.0)).any(axis=1)
    detection_seq = float(crossed.mean())
    return {
        "sharpe_ann": sharpe_ann,
        "T": T,
        "m": m,
        "detection_fixed_T": detection_fixed,
        "detection_sequential": detection_seq,
        "only_via_time": detection_seq <= detection_fixed + 0.05,
        "note": (
            "sequential anytime-valid detection <= fixed-horizon at matched T; "
            "Bayes/e-process adds no fixed-horizon power. Axis-1=only-via-time."
        ),
    }


# --------------------------------------------------------------------------
# SV7 (M7) — within-batch empirical-Bayes winner's curse (conditional).
# --------------------------------------------------------------------------
def sv7_eb_illustration(prior_var: float = 1.0) -> dict:
    """SV7: within a FUTURE exchangeable candidate batch, empirical-Bayes shrinks
    the selected winner's observed Sharpe by tau2/(tau2+se2) (winner's-curse
    correction). Legitimate, but only IN SCOPE if a future batch exists — the
    frozen frame has none. Distinct from M3 (which pools the dead cycles)."""
    se2 = se_ann(FORWARD_T, FORWARD_PPY) ** 2
    shrink = prior_var / (prior_var + se2)
    return {
        "shrinkage_factor": shrink,
        "per_leg_se2": se2,
        "in_scope_now": False,
        "note": (
            "EB winner's-curse correction across a FUTURE batch (not the dead "
            "cycles); conditional on a future candidate batch being registered."
        ),
    }


# --------------------------------------------------------------------------
# Aggregator + non-sealed writer.
# --------------------------------------------------------------------------
def run_analysis(sv2_m: int = 2000, seed: int = 20260602) -> dict:
    """Run all seven spot-checks and assemble the results dict."""
    return {
        "SV1": sv1_sizing_profile(),
        "SV2": sv2_no_acceleration(m=sv2_m, seed=seed),
        "SV3": sv3_shrinkage(),
        "SV4": sv4_skeptical_direction(),
        "SV5": sv5_attainability(),
        "SV6": sv6_estimand_comparison(),
        "SV7": sv7_eb_illustration(),
    }


def main() -> int:
    """Run the analysis and write to the NON-sealed results file."""
    results = {
        "schema": "eval_gate_power_study/eval_layer_scoping_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace(
            "+00:00", "Z"
        ),
        "spec": "docs/superpowers/specs/2026-06-02-bayesian-eval-layer-scoping-design.md",
        "constants": {
            "Z_PASS": Z_PASS,
            "Z_POWER": Z_POWER,
            "forward_T": FORWARD_T,
            "forward_ppy": FORWARD_PPY,
            "deployable_sharpe": DEPLOYABLE_SHARPE,
            "cohort_mean": cohort_mean(),
        },
        "spot_checks": run_analysis(),
    }
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_PATH.write_text(json.dumps(results, indent=2))
    print(f"wrote {RESULTS_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

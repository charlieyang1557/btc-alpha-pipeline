"""Evaluation-Gate Power Study — analytical MDE / IR-ceiling layer.

Implements the design spec
docs/superpowers/specs/2026-06-02-evaluation-gate-power-study-design.md
(§4 method, §5 pre-registered interpretation rule). Purely analytical /
read-only: computes statistical *properties* of the evaluation gate (the
DSR-FWER significance bar and the 80%-power minimum-detectable-Sharpe) as
closed-form functions of (OOS length T, rebalance frequency, N*, per-bar
return moments, cost-driven turnover). No data, no backtest, no signal.

# CONTRACT BOUNDARY (per spec §6, B2-Codex): IMPORT-PRIMITIVES-ONLY.
# This module imports ONLY Z_PASS + sr_star from backtest.tier6_dsr, and
# reimplements the bare (T-independent) Mertens term as sigma_denom() — pinned
# byte-equivalent to tier6_dsr.mertens_variance by a drift-guard test (the
# fixed-point MDE needs the term itself, which mertens_variance exposes only as
# variance/(T-1)). It
# MUST NEVER call evaluate_cohort() (or _read_cohort_csv / _write_csv /
# evaluate_candidate / any wrapper) — evaluate_cohort() defaults write=True /
# out_dir=DEFAULT_OUT_DIR and would WRITE the sealed tier6_dsr_v1/ directory.
# The only write this module ever performs is to its OWN non-sealed results
# file (data/eval_gate_power_study/results_v1.json), and only from the
# __main__ sweep runner — never into any sealed/config path.

## Annualization convention (per spec §4.3, backtest/metrics.py)
HOURS_PER_YEAR = 8760 ⇒ daily crypto uses periods_per_year = 365 (NOT the
equity 252/504 convention). Hourly 105-day OOS: T≈2527, ppy=8760. Daily
1/2/3-yr: T=365/730/1095, ppy=365. Intermediate 6h arm (documented below).

## sigma_denom / fixed-point MDE (spec §4.2, B2-mandated)
Under a true per-bar Sharpe sr_true, sr_hat ≈ Normal(sr_true, σ_denom²/(T−1))
where σ_denom² = mertens_variance(sr,γ3,γ4,T)·(T−1) = the Mertens term
`1 − γ3·sr + ((γ4−1)/4)·sr²` (the (T−1) factors cancel; σ_denom is
T-independent). Because σ_denom depends on the very sr being solved for, the
MDE is an IMPLICIT equation solved as a FIXED POINT:

    mde ← sr_star + (Z_PASS + z_power)·σ_denom(mde) / sqrt(T−1)

to convergence. The σ_denom ≈ 1 Gaussian shortcut is acceptable only at the
hourly gate (per-bar Sharpe ~0.066, kurtosis term negligible); at the daily
arms the per-bar Sharpe is 3-4× larger and the heavy-tail correction is
material (+15% to +37% at γ4≈60) — there the fixed-point heavy-tail MDE is
the load-bearing number, the Gaussian merely a reference.

## Cost net-vs-gross convention (spec §4.3 — flagged AMBIGUOUS; choice DOCUMENTED)
The spec says "report MDE in net terms (the gross edge required so the net
clears the bar at 80% power)" but does not pin the exact net↔gross mechanics.
CHOSEN CONVENTION (cleanest defensible; flagged for PI review):

  * The MDE and IR are computed in NET (after-cost) Sharpe/IR units — they
    are the after-cost edge a book must deliver to clear the gate at 80%
    power. This is what §5 compares against.
  * COST DRAG is modelled as an annualized RETURN give-up converted to
    annualized-Sharpe units by dividing by an assumed annualized return
    volatility σ_ret_ann (default 0.60 = a documented ~60%/yr BTC vol):
        cost_return_ann = turnover_one_way · 2 · (cost_bps/1e4) · rebalances_per_year
            (×2 = round-trip: a one-way turnover fraction τ per rebalance pays
             the per-side cost on BOTH the buy and the offsetting sell leg)
        cost_drag_ann_sharpe = cost_return_ann / σ_ret_ann
  * GROSS required Sharpe = net MDE + cost_drag_ann_sharpe. A gross book must
    out-earn both the noise hurdle (net MDE) AND the frictional give-up.

  Rationale for σ_ret_ann normalization: Sharpe = mean/σ; a return give-up of
  Δμ_ann lowers annualized Sharpe by Δμ_ann/σ_ret_ann. Holding σ fixed (costs
  reduce mean, not vol) is the standard first-order convention. σ_ret_ann is a
  single transparent knob; the sweep reports cost drag at the default and the
  gross-required headline alongside the net MDE. PI: confirm σ_ret_ann=0.60
  and the round-trip ×2 are acceptable, or supply a preferred value.

All functions are pure (no I/O) except the __main__ sweep runner.
"""
from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

# CONTRACT BOUNDARY (see module docstring): primitives ONLY.
from backtest.tier6_dsr import Z_PASS, sr_star

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = PROJECT_ROOT / "data/eval_gate_power_study"
RESULTS_PATH = RESULTS_DIR / "results_v1.json"

# Spec §5 pre-registered constants (FROZEN — Charlie-ratified).
Z_POWER = 0.8416  # z(0.80): the significance-plus-power increment for 80% power
BUILD_THRESHOLD = 1.5  # MDE_ann ≤ 1.5 → BUILD-viable
CONFIRM_THRESHOLD = 3.0  # MDE_ann ≥ 3.0 → confirmation-limited

# Annualization (spec §4.3; matches backtest/metrics.HOURS_PER_YEAR=8760).
HOURS_PER_YEAR = 8760
DAYS_PER_YEAR = 365

# Cost convention (see module docstring): default annualized return vol used to
# convert a return-drag into annualized-Sharpe units. A single transparent knob.
DEFAULT_SIGMA_RET_ANN = 0.60  # ~60%/yr BTC return volatility (documented assumption)
COST_BPS_PER_SIDE = 15.0  # the project's Conservative-Anchor 15bps/side spot cost

# Fixed-point solver controls.
_FP_TOL = 1e-15
_FP_MAXITER = 100


# --------------------------------------------------------------------------
# Mertens denominator (T-independent σ_denom) + significance / power layer.
# --------------------------------------------------------------------------
def sigma_denom(gamma3: float, gamma4: float, sr: float) -> float:
    """Mertens σ_denom = sqrt(1 − γ3·sr + ((γ4−1)/4)·sr²).

    This is the T-independent factor inside the Mertens variance:
    mertens_variance(sr,γ3,γ4,T)·(T−1) = this term (the (T−1) factors cancel).
    γ4 is RAW kurtosis (3.0 = Gaussian). At sr=0 the skew/kurtosis terms vanish
    and σ_denom = 1 (the Gaussian null). γ3 < 0 (negative skew) RAISES σ_denom.

    Args:
        gamma3: Population skew.
        gamma4: RAW kurtosis (3 = Gaussian).
        sr: Per-bar Sharpe at which to evaluate the denominator.

    Returns:
        The Mertens σ_denom (a positive float).

    Raises:
        ValueError: If the term under the root is non-positive (asymptotic
            breakdown under extreme moments × sr).
    """
    term = 1.0 - gamma3 * sr + ((gamma4 - 1.0) / 4.0) * sr * sr
    # NaN-guard PARITY with tier6_dsr.mertens_variance (B2-Codex): non-finite
    # input raises rather than silently propagating NaN into the fixed point.
    if not math.isfinite(term) or term <= 0.0:
        raise ValueError(
            f"non-finite or non-positive Mertens term {term} (γ3={gamma3}, "
            f"γ4={gamma4}, sr={sr}): asymptotic breakdown / invalid input"
        )
    return math.sqrt(term)


def just_significant_per_bar(
    sr_star_val: float, T: int, gamma3: float, gamma4: float
) -> float:
    """The just-significant DSR bar in per-bar Sharpe units (≈50% power).

    Solves (sr − sr_star)·sqrt(T−1)/σ_denom = Z_PASS as a fixed point in
    σ_denom(sr): sr ← sr_star + Z_PASS·σ_denom(sr)/sqrt(T−1). This is the
    Sharpe a book must EXCEED to be declared significant — NOT the §5
    comparison number (that is the 80%-power MDE).

    Args:
        sr_star_val: The expected-max noise hurdle SR* for this (N*, T).
        T: OOS bar count (must be ≥ 2).
        gamma3: Population skew.
        gamma4: RAW kurtosis (3 = Gaussian).

    Returns:
        The just-significant per-bar Sharpe.
    """
    val, _, _ = _fixed_point(sr_star_val, T, gamma3, gamma4, z_increment=Z_PASS)
    return val


def mde_per_bar(
    sr_star_val: float, T: int, gamma3: float, gamma4: float, z_power: float = Z_POWER
) -> float:
    """80%-power minimum-detectable per-bar Sharpe (fixed-point, heavy-tail).

    Solves the implicit equation
        mde = sr_star + (Z_PASS + z_power)·σ_denom(mde) / sqrt(T−1)
    to convergence (spec §4.2). This is the LOAD-BEARING number §5 compares
    against (never the just-significant bar).

    Args:
        sr_star_val: The expected-max noise hurdle SR* (from tier6_dsr.sr_star).
        T: OOS bar count (must be ≥ 2).
        gamma3: Population skew.
        gamma4: RAW kurtosis (3 = Gaussian).
        z_power: Power quantile (default Z_POWER=0.8416 for 80% power).

    Returns:
        The 80%-power MDE in per-bar Sharpe units.
    """
    val, _, _ = _fixed_point(
        sr_star_val, T, gamma3, gamma4, z_increment=Z_PASS + z_power
    )
    return val


def mde_per_bar_diagnostic(
    sr_star_val: float, T: int, gamma3: float, gamma4: float, z_power: float = Z_POWER
) -> tuple[float, int, bool]:
    """Like :func:`mde_per_bar` but returns ``(mde, iterations, converged)``.

    Exposes the fixed-point iteration count and convergence flag for the test
    suite and for sweep-time diagnostics.
    """
    return _fixed_point(sr_star_val, T, gamma3, gamma4, z_increment=Z_PASS + z_power)


def _fixed_point(
    sr_star_val: float, T: int, gamma3: float, gamma4: float, z_increment: float
) -> tuple[float, int, bool]:
    """Solve sr = sr_star + z_increment·σ_denom(sr)/sqrt(T−1) by iteration.

    The Gaussian (σ_denom=1) value seeds the iteration. Converges when the
    successive change is below _FP_TOL. Returns (value, iterations, converged).

    Args:
        sr_star_val: The expected-max noise hurdle SR*.
        T: OOS bar count (must be ≥ 2).
        gamma3: Population skew.
        gamma4: RAW kurtosis (3 = Gaussian).
        z_increment: Z_PASS (significance bar) or Z_PASS + z_power (MDE).

    Returns:
        (sr, iterations, converged).

    Raises:
        ValueError: If T <= 1 (sqrt(T−1) degenerate).
    """
    if T <= 1:
        raise ValueError(f"T must be >= 2; got T={T}")
    root_t = math.sqrt(T - 1)
    sr = sr_star_val + z_increment / root_t  # Gaussian seed (σ_denom=1)
    converged = False
    iters = 0
    for iters in range(1, _FP_MAXITER + 1):
        new = sr_star_val + z_increment * sigma_denom(gamma3, gamma4, sr) / root_t
        if abs(new - sr) < _FP_TOL:
            sr = new
            converged = True
            break
        sr = new
    return sr, iters, converged


def annualize(per_bar: float, periods_per_year: int) -> float:
    """Annualize a per-bar Sharpe by × sqrt(periods_per_year) (spec §4.2)."""
    return per_bar * math.sqrt(periods_per_year)


# --------------------------------------------------------------------------
# §5 mechanical classifier (MECHANICAL ONLY — binding read is the PI's).
# --------------------------------------------------------------------------
def classify_mde(mde_ann: float) -> str:
    """Mechanical §5 bin for an annualized 80%-power MDE.

    BUILD-viable (≤1.5) / confirmation-limited (≥3.0) / INDETERMINATE (between).
    This is a MECHANICAL label only; the binding interpretation is Charlie's.

    Args:
        mde_ann: Annualized 80%-power MDE (net, per spec §5).

    Returns:
        One of "BUILD-viable", "confirmation-limited", "INDETERMINATE".
    """
    if mde_ann <= BUILD_THRESHOLD:
        return "BUILD-viable"
    if mde_ann >= CONFIRM_THRESHOLD:
        return "confirmation-limited"
    return "INDETERMINATE"


# --------------------------------------------------------------------------
# §4.3 cost drag (net→gross). Convention documented in the module docstring.
# --------------------------------------------------------------------------
def annual_cost_drag(
    turnover_one_way: float,
    rebalances_per_year: float,
    cost_bps_per_side: float = COST_BPS_PER_SIDE,
    sigma_ret_ann: float = DEFAULT_SIGMA_RET_ANN,
) -> float:
    """Annualized cost drag in annualized-Sharpe units.

    cost_return_ann = turnover_one_way · 2 · (cost_bps/1e4) · rebalances_per_year
    drag_sharpe     = cost_return_ann / sigma_ret_ann

    The ×2 is the round-trip: a one-way turnover fraction τ per rebalance pays
    the per-side cost on both the buy and the offsetting sell leg. See the
    module docstring for the full net-vs-gross convention (flagged for PI).

    Args:
        turnover_one_way: One-way turnover fraction per rebalance (∈[0,1]).
        rebalances_per_year: Rebalance events per year (= periods_per_year for
            a position re-evaluated every bar).
        cost_bps_per_side: Per-side cost in bps (default 15.0 spot anchor).
        sigma_ret_ann: Annualized return vol used to convert return→Sharpe
            (default DEFAULT_SIGMA_RET_ANN=0.60).

    Returns:
        The annualized cost drag in annualized-Sharpe units (≥ 0).
    """
    cost_return_ann = (
        turnover_one_way * 2.0 * (cost_bps_per_side / 1e4) * rebalances_per_year
    )
    return cost_return_ann / sigma_ret_ann


def gross_required_sharpe(
    net_mde_ann: float,
    turnover_one_way: float,
    rebalances_per_year: float,
    cost_bps_per_side: float = COST_BPS_PER_SIDE,
    sigma_ret_ann: float = DEFAULT_SIGMA_RET_ANN,
) -> float:
    """Gross annualized Sharpe a NET book needs = net MDE + annualized cost drag.

    Args:
        net_mde_ann: The net (after-cost) 80%-power MDE in annualized Sharpe.
        turnover_one_way: One-way turnover fraction per rebalance.
        rebalances_per_year: Rebalance events per year.
        cost_bps_per_side: Per-side cost in bps.
        sigma_ret_ann: Annualized return vol for the return→Sharpe conversion.

    Returns:
        The gross-required annualized Sharpe.
    """
    return net_mde_ann + annual_cost_drag(
        turnover_one_way, rebalances_per_year, cost_bps_per_side, sigma_ret_ann
    )


# --------------------------------------------------------------------------
# §4.4 Half B — fundamental-law IR ceiling.
# --------------------------------------------------------------------------
def n_eff_equicorrelation(n: int, rho: float) -> float:
    """PRIMARY effective-N: equicorrelation haircut N / (1 + (N−1)ρ).

    The conservative standard form. At ρ=0.8, N=20 → ≈ 1.23 (the book is
    ≈ one bet). Spec §4.4 / §5 pinned PRIMARY.
    """
    return n / (1.0 + (n - 1) * rho)


def n_eff_soft(n: int, rho: float) -> float:
    """SENSITIVITY effective-N: soft form (1−ρ)·N + ρ.

    At ρ=0.8, N=20 → 4.8. Spec §4.4 sensitivity; the verdict uses the primary.
    """
    return (1.0 - rho) * n + rho


def independent_bets_per_year(rebalances_per_year: float, rho_rank: float) -> float:
    """Breadth haircut: rebalances_per_year · (1 − ρ_rank) (spec §4.4).

    A slow/sticky cross-sectional rank (high ρ_rank) refreshes far fewer
    independent bets than its nominal cadence — the single biggest IR lever.
    """
    return rebalances_per_year * (1.0 - rho_rank)


def ir_ann_gross(
    ic: float, n: int, rho: float, rebalances_per_year: float, rho_rank: float
) -> float:
    """Gross annualized IR via the fundamental law: IC · sqrt(BR).

    BR = N_eff(primary equicorrelation) · independent_bets_per_year.

    Args:
        ic: Information coefficient.
        n: Nominal cross-section size.
        rho: Average pairwise return correlation (for N_eff).
        rebalances_per_year: Rebalance cadence.
        rho_rank: Cross-sectional rank-autocorrelation (breadth haircut).

    Returns:
        Gross annualized IR (= gross annualized Sharpe of the rank book).
    """
    breadth = n_eff_equicorrelation(n, rho) * independent_bets_per_year(
        rebalances_per_year, rho_rank
    )
    return ic * math.sqrt(breadth)


def ir_ann_net(
    ic: float,
    n: int,
    rho: float,
    rebalances_per_year: float,
    rho_rank: float,
    turnover_one_way: float,
    cost_bps_per_side: float = COST_BPS_PER_SIDE,
    sigma_ret_ann: float = DEFAULT_SIGMA_RET_ANN,
) -> float:
    """Net annualized IR = gross IR − cross-sectional cost drag (spec §4.4)."""
    return ir_ann_gross(ic, n, rho, rebalances_per_year, rho_rank) - annual_cost_drag(
        turnover_one_way, rebalances_per_year, cost_bps_per_side, sigma_ret_ann
    )


# --------------------------------------------------------------------------
# Sweep arm definitions (§4.3 / §4.4) + runner.
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class OOSDesign:
    """An OOS evaluation-gate design arm.

    rebalances_per_year for a position re-evaluated every bar equals ppy; the
    cost arm parameterizes the one-way turnover per rebalance separately.
    """

    name: str
    T: int
    ppy: int
    # Achievable under the immutable splits (2020-21+2023 train / 2022 holdout /
    # 2024 val / 2025 test / forward_2026)? See spec §4.5 governance caveat.
    achievable: bool
    feasibility_note: str


# §4.3 OOS designs. The 6h intermediate arm: a 6h hold over a 1-year window →
# bars = 365·24/6 = 1460, ppy = 8760/6 = 1460 (documented convention).
OOS_DESIGNS: tuple[OOSDesign, ...] = (
    OOSDesign(
        "hourly_105d", 2527, 8760, True,
        "current forward_2026 gate (105-day hourly); fully achievable",
    ),
    OOSDesign(
        "6h_1yr", 1460, 1460, False,
        "6h hold over a 1-yr window; a 1-yr OOS at 6h reuses a designated "
        "window (2024 val or 2025 test) → unresolved-governance design",
    ),
    OOSDesign(
        "daily_105d", 105, 365, True,
        "daily book over the CLEAN 105-day forward_2026 window (T≈105 daily "
        "bars); fully achievable — the only clean DAILY arm (B2-added)",
    ),
    OOSDesign(
        "daily_1yr", 365, 365, False,
        "1-yr daily needs 365 daily bars but forward_2026 supplies only ~105; "
        "a 1-yr daily OOS reaches into the 2025 test window → "
        "unresolved-governance design (B2-CORRECTED: was wrongly achievable)",
    ),
    OOSDesign(
        "daily_2yr", 730, 365, False,
        "2-yr daily spans 2025 test + forward_2026 → reuses the designated "
        "test window → unresolved-governance design",
    ),
    OOSDesign(
        "daily_3yr", 1095, 365, False,
        "3-yr daily spans 2024 val + 2025 test + forward_2026 → reuses two "
        "designated windows → unresolved-governance design",
    ),
)

# §4.3 moment arms (γ3, γ4): Gaussian / observed / γ4-stress / negative-skew.
MOMENT_ARMS: tuple[tuple[str, float, float], ...] = (
    ("gaussian", 0.0, 3.0),
    ("observed", 0.14036, 11.30944),
    ("stress_g4_60", 0.0, 60.0),
    ("neg_skew", -2.0, 11.30944),
)

N_STAR_ARMS: tuple[int, ...] = (1, 3, 18)  # B2-added N*=1 (single pre-registered
# hypothesis, no multiplicity — most-favorable floor) / minimal-grid / dead-cohort
TURNOVER_ARMS: tuple[float, ...] = (0.3, 0.5, 0.7)  # §5 one-way turnover band

# §5 / §4.4 Half-B pre-registered parameter ranges.
IC_ARMS: tuple[float, ...] = (0.02, 0.035, 0.05)
N_ARMS: tuple[int, ...] = (15, 20, 25)
RHO_ARMS: tuple[float, ...] = (0.7, 0.8, 0.9)
RHO_RANK_ARMS: tuple[float, ...] = (0.5, 0.7, 0.9)
HALF_B_TURNOVER_ARMS: tuple[float, ...] = (0.3, 0.5, 0.7)


def _build_half_a() -> list[dict]:
    """Half A sweep: per (OOS design × N* × moments), the just-significant bar
    and the 80%-power MDE (Gaussian-shortcut vs fixed-point heavy-tail), all
    annualized, with the mechanical §5 bin and a cost-drag block.
    """
    rows: list[dict] = []
    for d in OOS_DESIGNS:
        for n_star in N_STAR_ARMS:
            # N*=1 = a single pre-registered hypothesis: no expected-max-of-N
            # deflation, so the DSR reduces to a plain one-sided significance
            # test with sr_star=0 (B2-added most-favorable-multiplicity floor).
            ss = 0.0 if n_star == 1 else sr_star(n_star, d.T, "B")
            for mname, g3, g4 in MOMENT_ARMS:
                sig_pb = just_significant_per_bar(ss, d.T, g3, g4)
                mde_pb, iters, conv = mde_per_bar_diagnostic(ss, d.T, g3, g4)
                # Gaussian reference at the same arm (σ_denom≡1).
                mde_g_pb = mde_per_bar(ss, d.T, 0.0, 3.0)
                mde_ann = annualize(mde_pb, d.ppy)
                # Cost drag at the mid turnover (0.5); gross-required headline.
                drag = annual_cost_drag(0.5, d.ppy, COST_BPS_PER_SIDE)
                rows.append({
                    "arm": f"{d.name}|N*={n_star}|{mname}",
                    "oos_design": d.name,
                    "T": d.T,
                    "ppy": d.ppy,
                    "n_star": n_star,
                    "moments": {"gamma3": g3, "gamma4": g4, "label": mname},
                    "sr_star": ss,
                    "just_significant_ann": annualize(sig_pb, d.ppy),
                    "mde_ann_gaussian": annualize(mde_g_pb, d.ppy),
                    "mde_ann_fixed_point_heavy_tail": mde_ann,
                    "heavy_tail_uplift_pct_vs_gaussian": (
                        (mde_pb / mde_g_pb - 1.0) * 100.0
                    ),
                    "fixed_point_iters": iters,
                    "fixed_point_converged": conv,
                    "classification": classify_mde(mde_ann),
                    "achievable": d.achievable,
                    "feasibility_note": d.feasibility_note,
                    "cost_drag_ann_at_turnover_0p5": drag,
                    "gross_required_ann_at_turnover_0p5": gross_required_sharpe(
                        mde_ann, 0.5, d.ppy, COST_BPS_PER_SIDE
                    ),
                })
    return rows


def _build_half_b() -> dict:
    """Half B sweep: achievable net IR_ann range (primary equicorrelation N_eff)
    over the pre-registered (IC × N × ρ × ρ_rank × turnover) grid at a daily
    rebalance cadence (the densest achievable cross-sectional gate), plus a soft
    N_eff sensitivity, compared against the Half-A daily MDE benchmark.
    """
    rpy = DAYS_PER_YEAR  # daily cross-sectional rebalance
    net_irs: list[float] = []
    gross_irs: list[float] = []
    soft_net_irs: list[float] = []
    best: dict | None = None
    for ic in IC_ARMS:
        for n in N_ARMS:
            for rho in RHO_ARMS:
                for rho_rank in RHO_RANK_ARMS:
                    gross = ir_ann_gross(ic, n, rho, rpy, rho_rank)
                    gross_irs.append(gross)
                    # Soft-form sensitivity gross IR.
                    soft_br = n_eff_soft(n, rho) * independent_bets_per_year(
                        rpy, rho_rank
                    )
                    soft_gross = ic * math.sqrt(soft_br)
                    for to in HALF_B_TURNOVER_ARMS:
                        net = ir_ann_net(ic, n, rho, rpy, rho_rank, to)
                        net_irs.append(net)
                        soft_net = soft_gross - annual_cost_drag(
                            to, rpy, COST_BPS_PER_SIDE
                        )
                        soft_net_irs.append(soft_net)
                        if best is None or net > best["net_ir_ann"]:
                            best = {
                                "ic": ic, "n": n, "rho": rho,
                                "rho_rank": rho_rank, "turnover": to,
                                "n_eff_equicorr": n_eff_equicorrelation(n, rho),
                                "gross_ir_ann": gross,
                                "net_ir_ann": net,
                            }
    # ACHIEVABLE-MDE benchmark (B2-CORRECTED): the cross-sectional fork would
    # be evaluated on a cleanly-achievable gate. The only clean arms are
    # hourly_105d and daily_105d (daily_1yr is governance-blocked). Use the
    # SOFTEST achievable MDE as the most generous bar the best cross-sectional
    # book must clear — if even that is not cleared, the fork is confirmation-
    # limited. (Was wrongly benchmarked against the governance-blocked daily_1yr.)
    mde_bench_hourly = annualize(
        mde_per_bar(sr_star(3, 2527, "B"), 2527, 0.14036, 11.30944), HOURS_PER_YEAR
    )
    mde_bench_daily105 = annualize(
        mde_per_bar(sr_star(3, 105, "B"), 105, 0.14036, 11.30944), DAYS_PER_YEAR
    )
    mde_bench_achievable = min(mde_bench_hourly, mde_bench_daily105)
    best_net_primary = max(net_irs)
    best_net_soft = max(soft_net_irs)
    return {
        "rebalance_cadence": "daily (rpy=365)",
        "n_eff_form_primary": "equicorrelation N/(1+(N-1)rho)",
        "net_ir_ann_range_primary": [min(net_irs), max(net_irs)],
        "best_net_ir_ann_primary": best_net_primary,
        "gross_ir_ann_range_primary": [min(gross_irs), max(gross_irs)],
        "net_ir_ann_range_soft_sensitivity": [min(soft_net_irs), max(soft_net_irs)],
        "best_net_ir_ann_soft_sensitivity": best_net_soft,
        "best_net_design": best,
        "mde_ann_benchmark_achievable": mde_bench_achievable,
        "mde_ann_benchmark_hourly_105d_observed": mde_bench_hourly,
        "mde_ann_benchmark_daily_105d_observed": mde_bench_daily105,
        "achievable_mde_classification": classify_mde(mde_bench_achievable),
        "best_net_ir_clears_achievable_mde_primary": (
            best_net_primary >= mde_bench_achievable
        ),
        "best_net_ir_clears_achievable_mde_soft": (
            best_net_soft >= mde_bench_achievable
        ),
    }


def run_sweep() -> dict:
    """Run the full Half A + Half B sweep and assemble the results dict."""
    return {
        "schema": "eval_gate_power_study/results_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace(
            "+00:00", "Z"
        ),
        "spec": "docs/superpowers/specs/2026-06-02-evaluation-gate-power-study-design.md",
        "constants": {
            "Z_PASS": Z_PASS,
            "Z_POWER": Z_POWER,
            "build_threshold": BUILD_THRESHOLD,
            "confirm_threshold": CONFIRM_THRESHOLD,
            "cost_bps_per_side": COST_BPS_PER_SIDE,
            "sigma_ret_ann_assumed": DEFAULT_SIGMA_RET_ANN,
            "cost_convention": (
                "net-units MDE/IR; drag = turnover*2*(bps/1e4)*rpy / sigma_ret_ann; "
                "gross_required = net_mde + drag (see module docstring; flagged for PI)"
            ),
        },
        "half_a": _build_half_a(),
        "half_b": _build_half_b(),
    }


def main() -> int:
    """Run the sweep and write results to the NON-sealed results_v1.json.

    NEVER touches the sealed tier6_dsr_v1/ directory or any config — only the
    module's own data/eval_gate_power_study/results_v1.json (see CONTRACT
    BOUNDARY in the module docstring).
    """
    results = run_sweep()
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_PATH.write_text(json.dumps(results, indent=2))
    print(f"wrote {RESULTS_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

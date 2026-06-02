"""GATED RUN entry point for the Path D OI verdict (PHASE D — Charlie register).

Wires the real engine-backed stages into backtest.pathd_orchestrator.run_pathd_verdict
on the forward_2026 window at the 15bps spot anchor and writes the ADVISORY evidence
bundle to data/phase2c_evaluation_gate/pathd_verdict_v1/.

PHASE-D GATE (CRITICAL): executing the real forward_2026 RUN is a SEPARATE Charlie
register-event (Phase D), gated downstream of the C4-C7 build. ``main()`` therefore
REFUSES to run unless ``PHASE_D_AUTHORIZED`` is flipped True by an explicit
Charlie-registered Phase-D authorization. The C4-C7 scope is building this
orchestrator + its unit tests (mocked engine) — NOT executing the verdict run. Do
NOT flip the flag without the Phase-D register.

CONTRACT BOUNDARY: PHASE_D_AUTHORIZED must stay False in the committed repo.
Only a Charlie-registered Phase-D authorization may flip it for the actual run.

SCOPE (when Phase D fires): the RUN executes the forward_2026 Tier-5 single-run per
hypothesis (the binding falsification gate) + the train-only tiered per-leg
mechanism sanity + DSR-FWER at N*=3 + the C7 hypothesis-class floors. There is NO
Step-0 (Path D is a fresh OI cohort, not a re-score of a prior dead cohort).
The D1-only OI-marginal diagnostic (vs no-OI baseline) is Task C6 and wired into
``oi_marginal`` in the bundle. D2 is NOT present (OI is an independent axis).

KEY DIVERGENCES from pathc_run_verdict:
  - D1-ONLY diagnostic: only ``oi_marginal_d1`` + ``contamination_correlations``
    from pathd_marginal_diagnostic. NO D2 / redundancy_read / d2_agrees.
  - ``oi_marginal`` (not ``basis_marginal``) in the bundle.
  - ``run_pathd_verdict`` (not ``run_pathc_verdict``).
  - OI feature columns (oi_pct_rank_2160, oi_velocity_ewm_240, etc.) in the
    train frame; features parquet must include the OI factors.
  - OI factors are NaN-heavy in 2024/2025: floor eligibility is computed on the
    non-NaN subset; build_train_frame dropna is restricted to the OI factor columns
    that are present (graceful handling).

Pre-registration discipline: every builder/sizing/exit/threshold is hardcoded
(frozen LOCK). Nothing here is fitted to a result. Sealed tier6_dsr_v1/ sha256 is
verified UNCHANGED before AND after the run.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import pandas as pd

from backtest.pathd_train_sanity import in_train_window, load_train_windows

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PATHD_VERDICT_DIR = PROJECT_ROOT / "data/phase2c_evaluation_gate/pathd_verdict_v1"
FEATURES_PATH = PROJECT_ROOT / "data/features/btcusdt_1h_features.parquet"
FORWARD_WINDOW = (
    datetime(2026, 1, 1, 0, tzinfo=timezone.utc),
    datetime(2026, 4, 16, 7, tzinfo=timezone.utc),
)
ANCHOR = "config/execution_phaseb_spot_15bps.yaml"

# Mechanism-sanity horizons (LOCK Pre-registration 4: 24h AND 72h).
FWD_HORIZON_24H = 24
FWD_HORIZON_72H = 72

# PHASE-D GATE: the forward_2026 RUN is a separate Charlie register-event. This
# flag stays False until that register fires; main() refuses to run while False.
# CONTRACT BOUNDARY: PHASE_D_AUTHORIZED must stay False in the committed repo.
# Only a Charlie-registered Phase-D authorization may flip it for the actual run;
# it is reverted to False before committing the verdict artifacts.
PHASE_D_AUTHORIZED = False

# Sealed dirs that must NEVER be written (inode-identity guard).
SEALED_DIRS = [
    PROJECT_ROOT / "data/phase2c_evaluation_gate/tier6_dsr_v1",
    PROJECT_ROOT / "data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1",
]
# The 4 sealed tier6_dsr_v1 artifacts whose sha256 must be invariant across the run.
_SEALED_TIER6_FILES = [
    SEALED_DIRS[0] / "tier6_dsr_companion.csv",
    SEALED_DIRS[0] / "tier6_dsr_results.csv",
    SEALED_DIRS[0] / "tier6_mc_validation.json",
    SEALED_DIRS[0] / "tier6_promotion_list.json",
]


def assert_not_sealed(out_dir: Path) -> None:
    """Raise if out_dir is (inode-identical to) or a CHILD of any sealed artifact dir.

    Three-layer check: os.path.samefile inode identity (both must exist) + resolved
    path string equality (catches a not-yet-created namespace) + a child-path guard
    (a write into a sub-path UNDER a sealed dir is refused; the sha256 check is the
    backstop). The child check uses the os.sep boundary so a sibling sharing only the
    sealed dir's name PREFIX is not falsely refused.

    Raises:
        ValueError: If ``out_dir`` resolves to / is inode-identical to / is a child of
            a SEALED_DIR.
    """
    out = Path(out_dir)
    for sealed in SEALED_DIRS:
        if sealed.exists() and out.exists():
            try:
                if os.path.samefile(out, sealed):
                    raise ValueError(f"refusing to write sealed dir {sealed}")
            except OSError:
                pass
        if str(out.resolve()) == str(sealed.resolve()):
            raise ValueError(f"refusing to write sealed dir {sealed}")
        # Child-path guard (defense-in-depth): refuse a write into a CHILD of a
        # sealed dir. The os.sep suffix makes this a path-boundary check, so a
        # sibling like ".../tier6_dsr_v1_sibling" is NOT falsely refused.
        if str(out.resolve()).startswith(str(sealed.resolve()) + os.sep):
            raise ValueError(f"refusing to write a child of sealed dir {sealed}")


def _sealed_fingerprint() -> dict[str, str]:
    """Return {filename: sha256} for the 4 sealed tier6_dsr_v1 artifacts."""
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in _SEALED_TIER6_FILES}


def _git_sha() -> str:
    """Return the current git HEAD sha (short), or 'UNKNOWN'."""
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], cwd=str(PROJECT_ROOT)
        ).decode().strip()
    except Exception:
        return "UNKNOWN"


def build_train_frame(
    windows: list[tuple[pd.Timestamp, pd.Timestamp]],
    features_path: Path = FEATURES_PATH,
) -> pd.DataFrame:
    """Load the factor parquet, restrict to TRAIN windows, attach 24h + 72h fwd rets.

    ``fwd_ret_24h`` / ``fwd_ret_72h`` are the cumulative realized returns over the
    next 24 / 72 bars (TRAIN-ONLY diagnostic targets for the tiered mechanism-sanity
    sign test — NOT registered factors, NOT tradeable signals). The forward windows
    are computed WITHIN each contiguous train segment, so no train bar's forward
    target reaches across a segment edge into the held-out 2022 / 2024 validation.

    NOTE: OI factors are heavily NaN in 2024/2025; build_train_frame dropna is
    applied only on return_1h (used for fwd_ret computation) and the two fwd_ret
    columns. The OI factor columns may still contain NaN for early bars — callers
    must handle NaN gracefully (the DSL compiler's NaN-is-False invariant applies;
    floor computations use the non-NaN subset).

    Args:
        windows: Train windows from pathd_train_sanity.load_train_windows.
        features_path: Path to the OI-factor parquet.

    Returns:
        A train-only frame with the OI factors + fwd_ret_24h/72h.
    """
    df = pd.read_parquet(features_path).sort_values("open_time_utc").reset_index(drop=True)
    mask = df["open_time_utc"].apply(lambda t: in_train_window(pd.Timestamp(t), windows))
    train = df.loc[mask].copy()
    seg = (train.index.to_series().diff() != 1).cumsum()

    def _fwd_cum(group: pd.Series, horizon: int) -> pd.Series:
        fwd = (1.0 + group).shift(-1).rolling(window=horizon, min_periods=horizon).apply(
            lambda w: w.prod(), raw=True
        )
        return fwd.shift(-(horizon - 1)) - 1.0

    train["fwd_ret_24h"] = train.groupby(seg)["return_1h"].transform(
        lambda g: _fwd_cum(g, FWD_HORIZON_24H)
    )
    train["fwd_ret_72h"] = train.groupby(seg)["return_1h"].transform(
        lambda g: _fwd_cum(g, FWD_HORIZON_72H)
    )
    train = train.dropna(subset=["fwd_ret_24h", "fwd_ret_72h"]).reset_index(drop=True)
    return train


def compute_train_floors(
    hypotheses: dict[str, Any],
    run_backtest_fn: Callable[..., Any],
    train_windows: list[tuple[pd.Timestamp, pd.Timestamp]],
    *,
    git_sha: str = "PATHD_BUILD",
) -> dict[str, dict]:
    """Per-hypothesis TRAIN-window eligibility floors (LOCK Pre-reg 3).

    For each hypothesis, compile its gated DSL and run it over the TRAIN span via
    the INJECTED engine. Reconstruct the per-bar long/flat position series (from the
    engine's trades over the equity index) restricted to the TRAIN windows (2022
    regime-holdout bars are filtered OUT of the counts), then apply the per-class floor:

      - **H1** (long-biased de-risk overlay): ``h1_floor`` on the flat-exit-episode
        count (>= 200 defensive long->flat transitions over TRAIN).
      - **H2 / H3** (state-class): ``h2h3_floor`` on ``zero_fraction < 0.50`` AND
        ``>= 200`` TRAIN trades.

    NOTE: OI factors are heavily NaN in 2024/2025; the floor computation uses the
    trade-derived position series (which correctly reflects NaN-driven inactive bars)
    and trade counts (which count only actually-executed trades). NaN warmup bars
    produce flat positions — they correctly count toward zero_fraction.

    Args:
        hypotheses: Mapping of hypothesis id ("H1"/"H2"/"H3") -> gated DSL object.
        run_backtest_fn: The injected engine callable (mock in tests; real only
            behind the Phase-D gate).
        train_windows: Train windows from ``load_train_windows`` (2020-2021 + 2023).
        git_sha: Git sha to stamp (unused by the floor math; threaded for parity).

    Returns:
        ``{hyp_id: floor_dict}`` — H1 carries ``n_flat_exit_episodes``; H2/H3 carry
        ``zero_fraction`` + ``n_trades``. Every dict carries ``eligible`` (bool) +
        ``status`` (``ELIGIBLE`` / ``INDETERMINATE``).
    """
    from datetime import timedelta

    from backtest.pathd_orchestrator import (
        count_flat_exit_episodes,
        h1_floor_from_episodes,
        h2h3_floor,
        position_series_from_trades,
        zero_fraction_from_positions,
    )
    from strategies.dsl_compiler import compile_dsl_to_strategy

    _ = git_sha  # reserved for parity (unused by floor math)
    span_start = min(w[0] for w in train_windows)
    span_end = max(w[1] for w in train_windows)
    span_end = pd.Timestamp(span_end) + pd.Timedelta(days=1) - pd.Timedelta(hours=1)

    floors: dict[str, dict] = {}
    for key, dsl in hypotheses.items():
        strat = compile_dsl_to_strategy(dsl, write_manifest=False)
        warmup_bars = int(getattr(strat, "WARMUP_BARS", 0) or 0)
        feed_start = pd.Timestamp(span_start) - timedelta(hours=warmup_bars)
        res = run_backtest_fn(
            strategy_cls=strat,
            start_date=feed_start.to_pydatetime(),
            end_date=pd.Timestamp(span_end).to_pydatetime(),
            execution_config_path=Path(ANCHOR),
            write_registry=False,
        )
        eq_idx = pd.DatetimeIndex(res.equity_curve.index)
        train_mask = eq_idx.to_series().apply(
            lambda t: in_train_window(pd.Timestamp(t), train_windows)
        ).to_numpy()
        train_idx = eq_idx[train_mask]
        trades = list(getattr(res, "trades", []) or [])
        train_trades = [
            t for t in trades
            if t.get("entry_time_utc") is not None
            and in_train_window(pd.Timestamp(t["entry_time_utc"]), train_windows)
        ]
        position = position_series_from_trades(train_idx, train_trades)

        if key == "H1":
            # Count flat-exit episodes PER CONTIGUOUS TRAIN WINDOW to exclude
            # spurious cross-gap transitions (same fix as pathc — verified for a
            # strategy whose trades can span the 2021->2023 boundary).
            episodes = 0
            for w_lo, w_hi in train_windows:
                w_idx = train_idx[train_idx.to_series().apply(
                    lambda t, lo=w_lo, hi=w_hi: in_train_window(pd.Timestamp(t), [(lo, hi)])
                ).to_numpy()]
                w_position = position_series_from_trades(w_idx, train_trades)
                episodes += count_flat_exit_episodes(w_position)
            floor = h1_floor_from_episodes(episodes)
            floors[key] = {
                "eligible": floor["eligible"],
                "n_flat_exit_episodes": floor["flat_exit_episodes"],
                "threshold": floor["threshold"],
                "status": floor["status"],
            }
        else:  # H2 / H3 state-class floor
            zf = zero_fraction_from_positions(position)
            floor = h2h3_floor(zero_fraction=zf, total_trades=len(train_trades))
            floors[key] = {
                "eligible": floor["eligible"],
                "zero_fraction": floor["zero_fraction"],
                "n_trades": floor["total_trades"],
                "max_zero_fraction": floor["max_zero_fraction"],
                "min_trades": floor["min_trades"],
                "status": floor["status"],
            }
    return floors


def compute_oi_marginal(
    hypotheses: dict[str, Any],
    gated_window_equities: dict[str, Any],
    run_backtest_fn: Callable[..., Any],
    *,
    git_sha: str = "PATHD_BUILD",
) -> dict[str, dict]:
    """D1-only OI-marginal diagnostic on the forward bars (fenced).

    For each hypothesis:
      D1 (vs no-OI baseline): ``oi_marginal_d1(key, gated_equity, baseline_equity)``
        where ``baseline_equity`` is the matching no-OI baseline DSL (from
        ``backtest.pathd_eval_gauntlet.build_all_baselines``) run on the SAME forward
        window via the INJECTED engine.

    DESIGN INVARIANT (D2 absence): OI is an independent axis with no derived-from
    relation. There is NO D2 comparator, NO redundancy_read, NO d2_agrees in Path D.
    The §38.3 inheritance is ONLY the fenced-label-read + inert-D1-modal discipline.

    ``contamination_correlations`` is computed on the TRAIN frame (not the forward
    window) and returned as a separate key in the marginal dict. It measures Pearson
    AND Spearman of ``oi_velocity_ewm_240`` vs return and volatility series — never
    in N*/promotion.

    FENCED (DESIGN INVARIANT): every result carries ``promotion_affecting=False`` and
    ``in_n_star=False`` as structural constants — these are never derived from inputs
    and no result can flip them.

    Args:
        hypotheses: The OI-gated hypotheses dict (keys "H1"/"H2"/"H3").
        gated_window_equities: ``{hyp_id: forward-window equity Series}`` from the
            OI gauntlet runs (reused — the gated forward run is NOT re-executed).
        run_backtest_fn: Injected engine callable (mock in tests; real only behind
            the Phase-D gate).
        git_sha: Git sha to stamp the diagnostic holdout artifacts.

    Returns:
        ``{hyp_id: {"d1": d1_dict, "promotion_affecting": False, "in_n_star": False}}``
        NOTE: NO ``d2`` key (OI is independent; D2 dropped).
    """
    import tempfile

    from backtest.pathd_eval_gauntlet import build_all_baselines
    from backtest.pathd_holdout_producer import produce_candidate_holdout
    from backtest.pathd_marginal_diagnostic import oi_marginal_d1
    from strategies.dsl import compute_dsl_hash
    from strategies.dsl_compiler import compile_dsl_to_strategy

    # Build D1 no-OI baselines.
    baselines = build_all_baselines()

    marginal: dict[str, dict] = {}
    # Isolate diagnostic artifacts in a scratch dir — never co-mingled with the
    # gated cohort or any sealed dir.
    with tempfile.TemporaryDirectory(prefix="pathd_marginal_diag_") as scratch:
        scratch_dir = Path(scratch)
        for key in hypotheses:
            gated_eq = gated_window_equities[key]

            # --- D1: run the no-OI baseline ---
            baseline_dsl = baselines[key]
            b_hash = compute_dsl_hash(baseline_dsl)
            b_strat = compile_dsl_to_strategy(baseline_dsl, write_manifest=False)
            b_res = produce_candidate_holdout(
                hypothesis_hash=b_hash,
                name=baseline_dsl.name,
                theme="pathd_d1_baseline",
                strategy_cls=b_strat,
                window=FORWARD_WINDOW,
                cohort_dir=scratch_dir,
                execution_config_path=ANCHOR,
                current_git_sha=git_sha,
                _run_backtest=run_backtest_fn,
            )
            baseline_eq = b_res["window_equity"]
            d1 = oi_marginal_d1(key, gated_eq, baseline_eq)

            marginal[key] = {
                "d1": d1,
                # FENCE (structural constants; never derived from inputs).
                "promotion_affecting": False,
                "in_n_star": False,
                # NOTE: NO d2, NO redundancy_read, NO d2_agrees — OI is independent.
            }
    return marginal


def run_verdict(
    out_dir: Path = PATHD_VERDICT_DIR,
    *,
    features_path: Path = FEATURES_PATH,
    _run_backtest: Callable[..., Any] | None = None,
) -> dict[str, Any]:
    """Execute the Path D verdict RUN and return the ADVISORY evidence bundle.

    Injectable deps (``_run_backtest`` / ``features_path``) make this unit-testable
    with mocks; production (Phase D) passes the real engine. Building + unit-testing
    this is the C4-C7 scope; main() gates the actual Phase-D run.

    DEFENSE-IN-DEPTH: ``run_verdict`` REQUIRES an injected ``_run_backtest``
    callable while Phase D is unauthorized. The ONLY place the real engine is wired
    is behind the ``PHASE_D_AUTHORIZED`` assertion in ``main()``. Calling
    ``run_verdict()`` with ``_run_backtest=None`` while Phase D is unauthorized
    raises rather than reaching the real engine.

    Raises:
        RuntimeError: If ``_run_backtest`` is None and Phase D is not authorized —
            the real-engine path must be reached only through the gated ``main()``.
        ValueError: On a sealed-dir write attempt or a sealed-artifact sha256 change
            across the run.
    """
    # CONTRACT BOUNDARY: the §37.1 gate — refusing the real-engine path unless an
    # engine is injected or Phase D is authorized. This is a CONTRACT BOUNDARY:
    # unit tests pass a MOCK; the real engine is wired only by main() behind
    # PHASE_D_AUTHORIZED. Do NOT weaken this check or add a fallback path here.
    if _run_backtest is None and not PHASE_D_AUTHORIZED:
        raise RuntimeError(
            "pathd_run_verdict.run_verdict: REFUSING — the REAL forward_2026 engine "
            "is Phase-D gated and reachable only via the authorized main() gate. "
            "Pass an injected _run_backtest (a MOCK) for unit testing, or fire the "
            "Phase-D Charlie register (flip PHASE_D_AUTHORIZED) before a real run. "
            "Do NOT bypass the gate by calling run_verdict() directly."
        )

    from backtest.pathd_eval_gauntlet import (
        H2_DERISK_PCTRANK,
        build_all_hypotheses,
        build_h1_dsl,
        build_h3_dsl,
    )
    from backtest.pathd_holdout_producer import produce_candidate_holdout
    from backtest.pathd_moments import build_cohort_csv, load_pathd_moments
    from backtest.pathd_orchestrator import (
        h1_floor_eligible,
        h2_derisk_occupancy_eligible,
        resolve_theta,
        run_pathd_verdict,
    )
    from scripts.pathb_cost_equivalence import assert_cost_equivalence
    from strategies.dsl import compute_dsl_hash
    from strategies.dsl_compiler import compile_dsl_to_strategy

    # When Phase D IS authorized and no mock was injected, main() is responsible for
    # wiring the real engine; resolve it here only on that authorized path.
    if _run_backtest is not None:
        run_backtest_fn = _run_backtest
    else:
        from backtest.engine import run_backtest  # reached only under PHASE_D_AUTHORIZED
        run_backtest_fn = run_backtest

    out_dir = Path(out_dir)
    assert_not_sealed(out_dir)
    cohort_dir = out_dir / "cohort"
    assert_not_sealed(cohort_dir)

    # --- Preflight guards (before any consume) ---
    cost = assert_cost_equivalence()
    sealed_before = _sealed_fingerprint()
    git_sha = _git_sha()

    # --- C7 (GAP 1 CLOSED): θ-resolution + floors at the FROZEN θ ---
    # Step 1: build the default-θ (0.90) hypotheses and run H1 TRAIN to count episodes.
    train_windows = load_train_windows()
    hypotheses_090 = build_all_hypotheses()  # H1/H3 use default θ=0.90
    floors_090 = compute_train_floors(
        hypotheses={"H1": hypotheses_090["H1"]},  # only H1 needed for θ-resolution
        run_backtest_fn=run_backtest_fn,
        train_windows=train_windows,
        git_sha=git_sha,
    )
    episodes_at_090 = int(floors_090["H1"]["n_flat_exit_episodes"])

    # Step 2: resolve θ deterministically (LOCK Pre-registration 1).
    frozen_theta = resolve_theta(episodes_at_090)

    # Step 3: if θ fell to 0.85, REBUILD H1 + H3 at 0.85 (exact-partition joint).
    if frozen_theta != 0.90:
        hypotheses_090["H1"] = build_h1_dsl(theta=frozen_theta)
        hypotheses_090["H3"] = build_h3_dsl(theta=frozen_theta)
        # Recount H1 episodes at the fallen θ for the floor judgment.
        floors_fallback = compute_train_floors(
            hypotheses={"H1": hypotheses_090["H1"]},
            run_backtest_fn=run_backtest_fn,
            train_windows=train_windows,
            git_sha=git_sha,
        )
        episodes_at_frozen = int(floors_fallback["H1"]["n_flat_exit_episodes"])
    else:
        episodes_at_frozen = episodes_at_090

    # Use the frozen-θ hypotheses dict for all downstream evaluation.
    hypotheses = hypotheses_090

    # Step 4: build the complete floors dict at the FROZEN θ (all three hypotheses).
    # H1: judged at frozen-θ episode count (always judged at frozen, not at 0.90).
    # H2: state-class floor (zero_fraction + trades) + de-risk-occupancy prong.
    # H3: state-class floor only.
    floors_h2h3 = compute_train_floors(
        hypotheses={"H2": hypotheses["H2"], "H3": hypotheses["H3"]},
        run_backtest_fn=run_backtest_fn,
        train_windows=train_windows,
        git_sha=git_sha,
    )
    # H1 floor: evaluated at the FROZEN θ episode count.
    h1_floor_eligible_flag = h1_floor_eligible(episodes_at_frozen)
    floors: dict[str, dict] = {
        "H1": {
            "eligible": h1_floor_eligible_flag,
            "n_flat_exit_episodes": episodes_at_frozen,
            "threshold": 200,
            "status": "ELIGIBLE" if h1_floor_eligible_flag else "INDETERMINATE",
            "frozen_theta": frozen_theta,
            "episodes_at_090": episodes_at_090,
        },
    }
    # --- Train feature frame: needed for de-risk occupancy + per-leg sanity ---
    train = build_train_frame(train_windows, features_path=features_path)

    # H2: add the de-risk-occupancy prong to the state-class floor.
    # LOCK Pre-registration 1 H2 row: de-risk-cell occupancy = fraction of evaluated
    # (non-NaN, post-warmup) TRAIN bars where oi_velocity_ewm_240_pctrank_2160 >= H2_DERISK_PCTRANK.
    # Measured directly from the train feature frame; pairwise NaN is dropped.
    # NOTE: OI pctrank columns are heavily NaN in early 2020 (2160-bar warmup);
    # .mean() over the non-NaN subset correctly handles this.
    h2_floor = dict(floors_h2h3["H2"])
    h2_zf_ok = h2_floor.get("zero_fraction", 1.0) < 0.50
    h2_trades_ok = int(h2_floor.get("n_trades", 0)) >= 200
    oi_vel_pctrank_col = "oi_velocity_ewm_240_pctrank_2160"
    if oi_vel_pctrank_col in train.columns:
        # Drop NaN for the pctrank measurement (OI NaN-heavy early in dataset).
        oi_nonnull = train[oi_vel_pctrank_col].dropna()
        derisk_occupancy = float(
            (oi_nonnull >= H2_DERISK_PCTRANK).mean() if len(oi_nonnull) > 0 else 0.0
        )
    else:
        # Column absent (feature parquet doesn't include OI yet); treat as 0 occupancy.
        derisk_occupancy = 0.0
    h2_derisk_ok = h2_derisk_occupancy_eligible(derisk_occupancy)
    h2_eligible = h2_zf_ok and h2_trades_ok and h2_derisk_ok
    h2_floor["eligible"] = h2_eligible
    h2_floor["status"] = "ELIGIBLE" if h2_eligible else "INDETERMINATE"
    h2_floor["derisk_occupancy"] = derisk_occupancy
    h2_floor["derisk_occupancy_eligible"] = h2_derisk_ok
    floors["H2"] = h2_floor
    floors["H3"] = floors_h2h3["H3"]

    try:
        from backtest.pathd_perleg_mechanism import compute_per_leg_tiers  # type: ignore[import]
        per_leg_result = compute_per_leg_tiers(train, theta=frozen_theta)
    except (ImportError, AttributeError):
        # C5 not yet exposed: conservative placeholder (all legs refuted).
        per_leg_result = {}

    # --- Real engine-backed gauntlet stages (forward_2026 Tier-5 per hypothesis) ---
    # Capture gated window equities for the D1 diagnostic.
    gated_window_equities: dict[str, Any] = {}

    def real_run_gauntlet(key: str, dsl) -> dict:
        h = compute_dsl_hash(dsl)
        strat = compile_dsl_to_strategy(dsl, write_manifest=False)
        res = produce_candidate_holdout(
            hypothesis_hash=h, name=dsl.name, theme="pathd",
            strategy_cls=strat, window=FORWARD_WINDOW, cohort_dir=cohort_dir,
            execution_config_path=ANCHOR, current_git_sha=git_sha,
            _run_backtest=run_backtest_fn,
        )
        gated_window_equities[key] = res["window_equity"]
        result = {
            "holdout_sharpe": res["holdout_sharpe"],
            "row": res["row"],
            "hypothesis_hash": h,
            "holdout_total_trades": int(res["row"].get("holdout_total_trades", 0)),
        }
        # Thread degenerate flag through: the orchestrator uses it to exclude the
        # leg from the DSR cohort and record it in degenerate_legs.
        if res.get("degenerate", False):
            result["degenerate"] = True
        return result

    def real_build_moments(holdouts: dict) -> list:
        # The orchestrator already filters degenerate holdouts before calling
        # build_moments, so ``holdouts`` here contains only non-degenerate rows.
        rows = [h["row"] for h in holdouts.values()]
        df = build_cohort_csv(rows, cohort_dir)
        if df.empty:
            return []
        return load_pathd_moments([r["hypothesis_hash"] for r in rows], df, cohort_dir)

    bundle = run_pathd_verdict(
        hypotheses=hypotheses,
        run_gauntlet=real_run_gauntlet,
        build_moments=real_build_moments,
        per_leg=lambda: per_leg_result,
        floors=floors,
        oi_marginal=None,  # filled below after the gauntlet runs
    )

    # --- D1-only OI-marginal diagnostic ---
    # The gated_window_equities are now populated by real_run_gauntlet (called inside
    # run_pathd_verdict above), so compute the fenced D1-only marginal diagnostic.
    # NOTE: NO D2 — OI is independent, D2 is dropped entirely.
    oi_marginal = compute_oi_marginal(
        hypotheses=hypotheses,
        gated_window_equities=gated_window_equities,
        run_backtest_fn=run_backtest_fn,
        git_sha=git_sha,
    )
    bundle["oi_marginal"] = oi_marginal

    # --- F3 headline caveat ---
    under_det = bundle.get("under_determined_legs", {})
    if under_det:
        bundle["earned_negative_power_limited"] = True
        bundle["earned_negative_power_limited_note"] = (
            "One or more legs are UNDER-DETERMINED (floor-ineligible with a thin-sample "
            "non-negative forward Sharpe). The 'is_earned_negative' headline applies to "
            "the eligible legs only; the under-determined legs are power-gap flagged and "
            "NOT counted as substantive negatives. See 'under_determined_legs' for detail."
        )
    else:
        bundle["earned_negative_power_limited"] = False
        bundle["earned_negative_power_limited_note"] = None

    # Mirror verdict_headline at bundle root.
    bundle["verdict_headline"] = bundle["taxonomy"].get("verdict_headline", "")

    # --- Sealed-artifact invariant (after); HARD guard ---
    sealed_after = _sealed_fingerprint()
    if sealed_after != sealed_before:
        raise ValueError(
            f"SEALED ARTIFACT CHANGED during the run: before={sealed_before} "
            f"after={sealed_after}; the run must NEVER mutate tier6_dsr_v1/."
        )

    bundle["meta"] = {
        "git_sha": git_sha,
        "forward_window": [FORWARD_WINDOW[0].isoformat(), FORWARD_WINDOW[1].isoformat()],
        "anchor": ANCHOR,
        "cost_equivalence": cost,
        "sealed_sha256_invariant": sealed_after,
        "frozen_theta": frozen_theta,
        "episodes_at_090": episodes_at_090,
        "episodes_at_frozen_theta": episodes_at_frozen,
        "scope_note": (
            "Path D OI verdict: forward_2026 Tier-5 gate + train-only tiered "
            "mechanism sanity (24h+72h) at FROZEN θ + DSR-FWER(N*=3); NO Step-0 "
            "(fresh OI cohort). C7 TRAIN-window floors applied BEFORE ranking "
            "(under-floor -> INDETERMINATE, excluded from n_tier5_pass); GENERIC F3 "
            "under-determined carve-out (any floor, not zero_fraction-specific); "
            "D1-ONLY OI-marginal diagnostic (no D2 — OI is independent axis); "
            "contamination_correlations fenced diagnostic. OI NaN-power disclosure: "
            "OI factors are NaN-heavy in 2024/2025; floor eligibility on non-NaN subset."
        ),
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "pathd_verdict_advisory.json").write_text(
        json.dumps(bundle, indent=2, default=str)
    )
    return bundle


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="GATED Path D OI verdict RUN (Phase-D Charlie register-event ONLY)."
    )
    ap.add_argument("--out-dir", default=str(PATHD_VERDICT_DIR))
    args = ap.parse_args(argv)

    if not PHASE_D_AUTHORIZED:
        print(
            "pathd_run_verdict: REFUSING — the forward_2026 RUN is Phase-D gated and "
            "NOT authorized. The C4-C7 scope is building + unit-testing this harness "
            "(mocked engine); executing the real verdict run is a SEPARATE Charlie "
            "register-event (Phase D). Do NOT flip PHASE_D_AUTHORIZED without that "
            "register. Aborting.",
            file=sys.stderr,
        )
        return 2

    assert PHASE_D_AUTHORIZED, "unreachable: gate checked above"
    bundle = run_verdict(Path(args.out_dir))
    tax = bundle["taxonomy"]
    esc = bundle["escalation"]
    print(json.dumps({
        "advisory_taxonomy": tax["advisory_taxonomy"],
        "is_earned_negative": tax["is_earned_negative"],
        "d_positive_strength": tax.get("d_positive_strength"),
        "verdict_rests_on_weak_sane_only": tax.get("verdict_rests_on_weak_sane_only"),
        "n_tier5_pass": bundle["n_tier5_pass"],
        "n_dsr_pass": bundle["n_dsr_pass"],
        "approximation_tempers": tax["approximation_tempers"],
        "d_escalation_warranted": esc["d_escalation_warranted"],
        "escalation_reason": esc["reason"],
        "authority": "charlie_register_at_earned_negative_gate",
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

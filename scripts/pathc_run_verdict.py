"""GATED RUN entry point for the Path C basis verdict (PHASE D — Charlie register).

Wires the real engine-backed stages into backtest.pathc_orchestrator.run_pathc_verdict
on the forward_2026 window at the 15bps spot anchor and writes the ADVISORY evidence
bundle to data/phase2c_evaluation_gate/pathc_verdict_v1/.

PHASE-D GATE (CRITICAL): executing the real forward_2026 RUN is a SEPARATE Charlie
register-event (Phase D), gated downstream of the C4-C7 build. ``main()`` therefore
REFUSES to run unless ``PHASE_D_AUTHORIZED`` is flipped True by an explicit
Charlie-registered Phase-D authorization. The C4-C7 scope is building this
orchestrator + its unit tests (mocked engine) — NOT executing the verdict run. Do
NOT flip the flag without the Phase-D register.

SCOPE (when Phase D fires): the RUN executes the forward_2026 Tier-5 single-run per
hypothesis (the binding falsification gate) + the train-only tiered per-leg
mechanism sanity + DSR-FWER at N*=3 + the C7 hypothesis-class floors. There is NO
Step-0 (Path C is a fresh basis cohort, not a re-score of a prior dead cohort).
The dual-orthogonalization diagnostics (D1 vs momentum; D2 vs funding) are Task C6
and wired into ``basis_marginal`` in the bundle.

Pre-registration discipline: every builder/sizing/exit/threshold is hardcoded
(frozen LOCK). Nothing here is fitted to a result. Sealed tier6_dsr_v1/ sha256 is
verified UNCHANGED before AND after the run.

CONTRACT GAP 1 (C7): compute_train_floors — per-hypothesis TRAIN-window eligibility
floors (LOCK Pre-reg 3). When C7 is complete, this function is filled: H1 uses the
flat-exit-episode floor (>= 200 defensive long->flat transitions), H2/H3 use the
state-class floor (zero_fraction < 0.50 AND >= 200 trades). Until then, the stub
returns each hypothesis as ELIGIBLE (floors=None passed to run_pathc_verdict, legacy
positive-Sharpe count).

CONTRACT GAP 2 (C6): compute_basis_marginal — the fenced dual-orthogonalization
diagnostics (D1 vs momentum / D2 vs funding) on the forward bars. When C6 is
complete, this function emits the per-hypothesis marginal dict. Until then, None.
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

from backtest.pathc_train_sanity import in_train_window, load_train_windows

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PATHC_VERDICT_DIR = PROJECT_ROOT / "data/phase2c_evaluation_gate/pathc_verdict_v1"
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

    Args:
        windows: Train windows from pathc_train_sanity.load_train_windows.
        features_path: Path to the basis-factor parquet.

    Returns:
        A train-only frame with the H1/H2/H3 basis factors + fwd_ret_24h/72h.
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
    git_sha: str = "PATHC_BUILD",
) -> dict[str, dict]:
    """CONTRACT GAP 1 (C7): per-hypothesis TRAIN-window eligibility floors (LOCK Pre-reg 3).

    For each hypothesis, compile its gated DSL and run it over the TRAIN span via
    the INJECTED engine. Reconstruct the per-bar long/flat position series (from the
    engine's trades over the equity index) restricted to the TRAIN windows (2022
    regime-holdout bars are filtered OUT of the counts), then apply the per-class floor:

      - **H1** (long-biased de-risk overlay): ``h1_floor`` on the flat-exit-episode
        count (>= 200 defensive long->flat transitions over TRAIN).
      - **H2 / H3** (state-class): ``h2h3_floor`` on ``zero_fraction < 0.50`` AND
        ``>= 200`` TRAIN trades.

    The engine is run over the full contiguous TRAIN span ``[min start, max end]``
    with the compiled strategy's WARMUP_BARS prepended (full-history features so the
    basis factors are warm), then the resulting position/trades are masked to the
    TRAIN windows (``in_train_window``) so no 2022/validation bar enters a floor count.

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

    from backtest.pathc_orchestrator import (
        count_flat_exit_episodes,
        h1_floor_from_episodes,
        h2h3_floor,
        position_series_from_trades,
        zero_fraction_from_positions,
    )
    from strategies.dsl_compiler import compile_dsl_to_strategy

    _ = git_sha  # reserved for parity with compute_basis_marginal (unused by floor math)
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
            # spurious cross-gap transitions (same fix as patha, which verified this
            # is needed for a strategy whose trades can span the 2021->2023 boundary).
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


def run_verdict(
    out_dir: Path = PATHC_VERDICT_DIR,
    *,
    features_path: Path = FEATURES_PATH,
    _run_backtest: Callable[..., Any] | None = None,
) -> dict[str, Any]:
    """Execute the Path C verdict RUN and return the ADVISORY evidence bundle.

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
            "pathc_run_verdict.run_verdict: REFUSING — the REAL forward_2026 engine "
            "is Phase-D gated and reachable only via the authorized main() gate. "
            "Pass an injected _run_backtest (a MOCK) for unit testing, or fire the "
            "Phase-D Charlie register (flip PHASE_D_AUTHORIZED) before a real run. "
            "Do NOT bypass the gate by calling run_verdict() directly."
        )

    from backtest.pathc_eval_gauntlet import build_all_hypotheses
    from backtest.pathc_holdout_producer import produce_candidate_holdout
    from backtest.pathc_moments import build_cohort_csv, load_pathc_moments
    from backtest.pathc_orchestrator import run_pathc_verdict
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

    # --- Train-only tiered per-leg mechanism sanity (mechanism-refuted input) ---
    # C5 (pathc_perleg_mechanism) is a separate task; when it exists, import and
    # call compute_per_leg_tiers(train). For now, build_train_frame is called and
    # the result is passed to the per_leg callable (which C5 will populate).
    # CONTRACT GAP 3 (C5): import backtest.pathc_perleg_mechanism and call
    # compute_per_leg_tiers(train) here once C5 is implemented.
    train = build_train_frame(load_train_windows(), features_path=features_path)

    # C5 integration point: per_leg_result will be produced by compute_per_leg_tiers
    # once backtest.pathc_perleg_mechanism is implemented. For now, use an empty dict
    # (all tiers refuted = the most conservative placeholder; the orchestrator will
    # record mechanism_refuted or process_refuted based on the holdout results).
    try:
        from backtest.pathc_perleg_mechanism import compute_per_leg_tiers  # type: ignore[import]
        per_leg_result = compute_per_leg_tiers(train)
    except ImportError:
        # C5 not yet implemented: conservative placeholder (all legs refuted).
        per_leg_result = {}

    # --- Real engine-backed gauntlet stages (forward_2026 Tier-5 per hypothesis) ---
    hypotheses = build_all_hypotheses()

    def real_run_gauntlet(key: str, dsl) -> dict:
        h = compute_dsl_hash(dsl)
        strat = compile_dsl_to_strategy(dsl, write_manifest=False)
        res = produce_candidate_holdout(
            hypothesis_hash=h, name=dsl.name, theme="pathc",
            strategy_cls=strat, window=FORWARD_WINDOW, cohort_dir=cohort_dir,
            execution_config_path=ANCHOR, current_git_sha=git_sha,
            _run_backtest=run_backtest_fn,
        )
        return {
            "holdout_sharpe": res["holdout_sharpe"],
            "row": res["row"],
            "hypothesis_hash": h,
            "holdout_total_trades": int(res["row"].get("holdout_total_trades", 0)),
        }

    def real_build_moments(holdouts: dict) -> list:
        rows = [h["row"] for h in holdouts.values()]
        df = build_cohort_csv(rows, cohort_dir)
        return load_pathc_moments([r["hypothesis_hash"] for r in rows], df, cohort_dir)

    # CONTRACT GAP 1 (C7 floors): TRAIN-window eligibility floors, computed BEFORE
    # ranking (LOCK Pre-registration 3). Each gated strategy is run over the TRAIN
    # span via the SAME injected engine; under-floor candidates are marked
    # INDETERMINATE + excluded from n_tier5_pass by run_pathc_verdict. C7 will
    # refine the floor semantics (resolve_theta deterministic rule; H2 de-risk
    # occupancy check). The stub compute_train_floors is functional and follows the
    # same per-window H1-episode-count fix as patha.
    train_windows = load_train_windows()
    floors = compute_train_floors(
        hypotheses=hypotheses,
        run_backtest_fn=run_backtest_fn,
        train_windows=train_windows,
        git_sha=git_sha,
    )

    bundle = run_pathc_verdict(
        hypotheses=hypotheses,
        run_gauntlet=real_run_gauntlet,
        build_moments=real_build_moments,
        per_leg=lambda: per_leg_result,
        floors=floors,
        # CONTRACT GAP 2 (C6 basis_marginal): D1/D2 diagnostics filled by C6.
        basis_marginal=None,
    )

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
        "scope_note": (
            "Path C basis verdict: forward_2026 Tier-5 gate + train-only tiered "
            "mechanism sanity (24h+72h) + DSR-FWER(N*=3); NO Step-0 (fresh basis "
            "cohort). C7 TRAIN-window floors applied BEFORE ranking (under-floor -> "
            "INDETERMINATE, excluded from n_tier5_pass); C6 fenced basis diagnostics "
            "(D1/D2) pending (CONTRACT GAP 2)."
        ),
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "pathc_verdict_advisory.json").write_text(
        json.dumps(bundle, indent=2, default=str)
    )
    return bundle


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="GATED Path C basis verdict RUN (Phase-D Charlie register-event ONLY)."
    )
    ap.add_argument("--out-dir", default=str(PATHC_VERDICT_DIR))
    args = ap.parse_args(argv)

    if not PHASE_D_AUTHORIZED:
        print(
            "pathc_run_verdict: REFUSING — the forward_2026 RUN is Phase-D gated and "
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
        "c_positive_strength": tax.get("c_positive_strength"),
        "verdict_rests_on_weak_sane_only": tax.get("verdict_rests_on_weak_sane_only"),
        "n_tier5_pass": bundle["n_tier5_pass"],
        "n_dsr_pass": bundle["n_dsr_pass"],
        "approximation_tempers": tax["approximation_tempers"],
        "c_escalation_warranted": esc["c_escalation_warranted"],
        "escalation_reason": esc["reason"],
        "authority": "charlie_register_at_earned_negative_gate",
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

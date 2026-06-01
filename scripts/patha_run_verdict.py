"""GATED RUN entry point for the Path A funding verdict (PHASE D — Charlie register).

Wires the real engine-backed stages into backtest.patha_orchestrator.run_patha_verdict
on the forward_2026 window at the 15bps spot anchor and writes the ADVISORY evidence
bundle to data/phase2c_evaluation_gate/patha_verdict_v1/.

PHASE-D GATE (CRITICAL): executing the real forward_2026 RUN is a SEPARATE Charlie
register-event (Phase D), gated downstream of the C4-C7 build. ``main()`` therefore
REFUSES to run unless ``PHASE_D_AUTHORIZED`` is flipped True by an explicit
Charlie-registered Phase-D authorization. The C4-C7 scope is building this
orchestrator + its unit tests (mocked engine) — NOT executing the verdict run. Do
NOT flip the flag without the Phase-D register.

SCOPE (when Phase D fires): the RUN executes the forward_2026 Tier-5 single-run per
hypothesis (the binding falsification gate) + the train-only tiered per-leg
mechanism sanity + DSR-FWER at N*=3 + the C7 hypothesis-class floors + the fenced
C6 funding-marginal diagnostic. There is NO Step-0 (Path A is a fresh funding
cohort, not a re-score of the dead-18).

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
from collections.abc import Iterable
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import pandas as pd

from backtest.patha_train_sanity import in_train_window, load_train_windows

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PATHA_VERDICT_DIR = PROJECT_ROOT / "data/phase2c_evaluation_gate/patha_verdict_v1"
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
# (Was transiently flipped True for the Charlie-registered Phase-D run 2026-05-31,
# then reverted here — the committed repo keeps the gate closed.)
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
        windows: Train windows from patha_train_sanity.load_train_windows.
        features_path: Path to the funding-factor parquet.

    Returns:
        A train-only frame with the H1/H2/H3 funding factors + fwd_ret_24h/72h.
    """
    df = pd.read_parquet(features_path).sort_values("open_time_utc").reset_index(drop=True)
    mask = df["open_time_utc"].apply(lambda t: in_train_window(pd.Timestamp(t), windows))
    train = df.loc[mask].copy()
    seg = (train.index.to_series().diff() != 1).cumsum()  # new segment at each index gap

    def _fwd_cum(group: pd.Series, horizon: int) -> pd.Series:
        # cumulative return over the next `horizon` bars, computed within-segment:
        # prod(1+r[i+1..i+horizon]) - 1; the last `horizon` bars get NaN (dropped).
        # use simple shifted rolling product on (1+r) over a forward window.
        fwd = (1.0 + group).shift(-1).rolling(window=horizon, min_periods=horizon).apply(
            lambda w: w.prod(), raw=True
        )
        # rolling is backward-looking; shift it forward so row i sees i+1..i+horizon.
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
    git_sha: str = "PATHA_BUILD",
) -> dict[str, dict]:
    """CONTRACT GAP 1: per-hypothesis TRAIN-window eligibility floors (LOCK Pre-reg 3).

    For each hypothesis, compile its gated DSL and run it over the TRAIN span via
    the INJECTED engine (the SAME ``run_backtest_fn`` threaded through ``run_verdict``
    — unit tests inject a MOCK; the real engine is reachable only behind the
    PHASE_D_AUTHORIZED gate in ``main()``). Reconstruct the per-bar long/flat
    position series (from the engine's trades over the equity index) restricted to
    the TRAIN windows (2022 regime-holdout bars are filtered OUT of the counts),
    then apply the per-class floor:

      - **H1** (long-biased de-risk overlay): ``h1_floor`` on the flat-exit-episode
        count (>= 200 defensive long->flat transitions over TRAIN — NOT occupancy).
      - **H2 / H3** (state-class): ``h2h3_floor`` on ``zero_fraction < 0.50`` AND
        ``>= 200`` TRAIN trades.

    The engine is run over the full contiguous TRAIN span ``[min start, max end]``
    with the compiled strategy's WARMUP_BARS prepended (full-history features so the
    funding factors are warm), then the resulting position/trades are masked to the
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

    from backtest.patha_orchestrator import (
        count_flat_exit_episodes,
        h1_floor_from_episodes,
        h2h3_floor,
        position_series_from_trades,
        zero_fraction_from_positions,
    )
    from strategies.dsl_compiler import compile_dsl_to_strategy

    _ = git_sha  # reserved for parity with compute_funding_marginal (unused by floor math)
    span_start = min(w[0] for w in train_windows)
    span_end = max(w[1] for w in train_windows)
    # end-day inclusive: extend to the end of the last train day.
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
        # Restrict the bar index to TRAIN windows only (drops warmup-prepend +
        # the interleaved 2022 regime-holdout + any post-span bars).
        eq_idx = pd.DatetimeIndex(res.equity_curve.index)
        train_mask = eq_idx.to_series().apply(
            lambda t: in_train_window(pd.Timestamp(t), train_windows)
        ).to_numpy()
        train_idx = eq_idx[train_mask]
        trades = list(getattr(res, "trades", []) or [])
        # Keep only trades whose ENTRY falls in a train window (so a 2022 / pre-span
        # warmup trade does not inflate the floor counts).
        train_trades = [
            t for t in trades
            if t.get("entry_time_utc") is not None
            and in_train_window(pd.Timestamp(t["entry_time_utc"]), train_windows)
        ]
        position = position_series_from_trades(train_idx, train_trades)

        if key == "H1":
            # FIX (2-leg review MEDIUM): count flat-exit episodes PER CONTIGUOUS TRAIN
            # WINDOW separately, never across the 2021->2023 discontinuity. A trade
            # that ENTERS in train (e.g. late 2021) but EXITS in the excluded 2022
            # holdout shows LONG through the last 2021 train bar; the next train bar
            # (2023-01-01) is FLAT, manufacturing a spurious long->flat transition at
            # the window-gap boundary. That flat is a window-gap artifact, NOT a real
            # funding-tail-gate firing, so it must not count toward the H1 >=200 floor.
            # Summing per-window counts (each window's position reconstructed over only
            # its own bars) excludes the boundary transition while preserving every
            # real within-window flat-exit episode.
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


def compute_funding_marginal(
    hypotheses: Iterable[str],
    gated_window_equities: dict[str, Any],
    run_backtest_fn: Callable[..., Any],
    *,
    git_sha: str = "PATHA_BUILD",
) -> dict[str, dict]:
    """CONTRACT GAP 2: the fenced funding-marginal diagnostic on the forward bars.

    For each hypothesis compute ``funding_marginal(hyp_id, gated_equity,
    baseline_equity)`` on the forward_2026 bars, where ``baseline_equity`` is the
    SAME strategy WITHOUT the funding gate (H2/H3 = the price-trend-only book; H1 =
    always-long) run on the SAME forward window via the INJECTED engine. The gated
    equity is reused from the gauntlet (``produce_candidate_holdout`` returns the
    cropped ``window_equity``), so the gated forward run is NOT duplicated.

    FENCED (DESIGN INVARIANT): every result carries ``promotion_affecting=False`` /
    ``in_n_star=False`` (structural constants in ``funding_marginal``); it rides
    along in the evidence bundle but NEVER feeds N* or promotion.

    Args:
        hypotheses: An iterable of hypothesis ids (only the ids are consumed here;
            the baselines are built from ``build_*_baseline_dsl``). A
            ``dict[str, ...]`` still satisfies this since iterating a dict yields keys.
        gated_window_equities: ``{hyp_id: cropped forward-window equity Series}``
            from the gauntlet runs.
        run_backtest_fn: The injected engine callable (mock in tests; real only
            behind the Phase-D gate).
        git_sha: Git sha to stamp the baseline holdout artifacts.

    Returns:
        ``{hyp_id: marginal_dict}`` from ``funding_marginal`` (fenced).
    """
    import tempfile

    from backtest.patha_eval_gauntlet import build_all_baselines
    from backtest.patha_holdout_producer import produce_candidate_holdout
    from backtest.patha_marginal_diagnostic import funding_marginal
    from strategies.dsl import compute_dsl_hash
    from strategies.dsl_compiler import compile_dsl_to_strategy

    baselines = build_all_baselines()
    marginal: dict[str, dict] = {}
    # The baseline holdout artifacts are diagnostic-only; isolate them physically in
    # a scratch dir (NEVER co-mingled with the gated cohort or any sealed dir).
    with tempfile.TemporaryDirectory(prefix="patha_marginal_baseline_") as scratch:
        scratch_dir = Path(scratch)
        for key in hypotheses:
            baseline_dsl = baselines[key]
            h = compute_dsl_hash(baseline_dsl)
            strat = compile_dsl_to_strategy(baseline_dsl, write_manifest=False)
            res = produce_candidate_holdout(
                hypothesis_hash=h, name=baseline_dsl.name, theme="patha_baseline",
                strategy_cls=strat, window=FORWARD_WINDOW, cohort_dir=scratch_dir,
                execution_config_path=ANCHOR, current_git_sha=git_sha,
                _run_backtest=run_backtest_fn,
            )
            baseline_equity = res["window_equity"]
            marginal[key] = funding_marginal(
                hyp_id=key,
                gated_equity=gated_window_equities[key],
                baseline_equity=baseline_equity,
            )
    return marginal


def run_verdict(
    out_dir: Path = PATHA_VERDICT_DIR,
    *,
    features_path: Path = FEATURES_PATH,
    _run_backtest: Callable[..., Any] | None = None,
) -> dict[str, Any]:
    """Execute the Path A verdict RUN and return the ADVISORY evidence bundle.

    Injectable deps (``_run_backtest`` / ``features_path``) make this unit-testable
    with mocks; production (Phase D) passes the real engine. Building + unit-testing
    this is the C4-C7 scope; main() gates the actual Phase-D run.

    DEFENSE-IN-DEPTH (2-leg-review HIGH): ``run_verdict`` is a public function that
    could be called directly (bypassing the ``main()`` Phase-D gate). The REAL
    engine (``backtest.engine.run_backtest``) — which writes per-bar artifacts and
    runs the forward_2026 backtest — is NEVER wired internally here. ``run_verdict``
    REQUIRES an injected ``_run_backtest`` callable: unit tests inject a MOCK, and the
    ONLY place the real engine is wired is behind the ``PHASE_D_AUTHORIZED`` assertion
    in ``main()``. Calling ``run_verdict()`` with ``_run_backtest=None`` while Phase D
    is unauthorized raises rather than reaching the real engine.

    Raises:
        RuntimeError: If ``_run_backtest`` is None and Phase D is not authorized —
            the real-engine path must be reached only through the gated ``main()``.
        ValueError: On a sealed-dir write attempt or a sealed-artifact sha256 change
            across the run.
    """
    # DEFENSE-IN-DEPTH: refuse the real-engine path unless an engine is injected.
    # The real engine is wired only by main() behind PHASE_D_AUTHORIZED; a direct
    # run_verdict() call with no injected engine must NOT reach backtest.engine.
    if _run_backtest is None and not PHASE_D_AUTHORIZED:
        raise RuntimeError(
            "patha_run_verdict.run_verdict: REFUSING — the REAL forward_2026 engine "
            "is Phase-D gated and reachable only via the authorized main() gate. "
            "Pass an injected _run_backtest (a MOCK) for unit testing, or fire the "
            "Phase-D Charlie register (flip PHASE_D_AUTHORIZED) before a real run. "
            "Do NOT bypass the gate by calling run_verdict() directly."
        )

    from backtest.patha_eval_gauntlet import build_all_hypotheses
    from backtest.patha_holdout_producer import produce_candidate_holdout
    from backtest.patha_moments import build_cohort_csv, load_patha_moments
    from backtest.patha_orchestrator import run_patha_verdict
    from backtest.patha_perleg_mechanism import compute_per_leg_tiers
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
    assert_not_sealed(cohort_dir)  # defense-in-depth at the producer write-site

    # --- Preflight guards (before any consume) ---
    cost = assert_cost_equivalence()              # phase4 == 15bps spot anchor
    sealed_before = _sealed_fingerprint()         # sealed-artifact invariant (before)
    git_sha = _git_sha()

    # --- Train-only tiered per-leg mechanism sanity (mechanism-refuted input) ---
    train = build_train_frame(load_train_windows(), features_path=features_path)
    per_leg_result = compute_per_leg_tiers(train)

    # --- Real engine-backed gauntlet stages (forward_2026 Tier-5 per hypothesis) ---
    hypotheses = build_all_hypotheses()
    # Captured for the CONTRACT GAP 2 funding-marginal: the gated strategy's CROPPED
    # forward-window equity per hypothesis (reused so the gated forward run is not
    # re-executed for the diagnostic).
    gated_window_equities: dict[str, Any] = {}

    def real_run_gauntlet(key: str, dsl) -> dict:
        h = compute_dsl_hash(dsl)
        strat = compile_dsl_to_strategy(dsl, write_manifest=False)
        res = produce_candidate_holdout(
            hypothesis_hash=h, name=dsl.name, theme="patha",
            strategy_cls=strat, window=FORWARD_WINDOW, cohort_dir=cohort_dir,
            execution_config_path=ANCHOR, current_git_sha=git_sha,
            _run_backtest=run_backtest_fn,
        )
        gated_window_equities[key] = res["window_equity"]
        return {"holdout_sharpe": res["holdout_sharpe"], "row": res["row"], "hypothesis_hash": h}

    def real_build_moments(holdouts: dict) -> list:
        rows = [h["row"] for h in holdouts.values()]
        df = build_cohort_csv(rows, cohort_dir)
        return load_patha_moments([r["hypothesis_hash"] for r in rows], df, cohort_dir)

    # CONTRACT GAP 1 (closed): TRAIN-window eligibility floors, computed BEFORE
    # ranking (LOCK Pre-registration 3). Each gated strategy is run over the TRAIN
    # span via the SAME injected engine; under-floor candidates are marked
    # INDETERMINATE + excluded from n_tier5_pass by run_patha_verdict.
    train_windows = load_train_windows()
    floors = compute_train_floors(
        hypotheses=hypotheses,
        run_backtest_fn=run_backtest_fn,
        train_windows=train_windows,
        git_sha=git_sha,
    )

    bundle = run_patha_verdict(
        hypotheses=hypotheses,
        run_gauntlet=real_run_gauntlet,
        build_moments=real_build_moments,
        per_leg=lambda: per_leg_result,
        floors=floors,
        # CONTRACT GAP 2 filled below (needs the gated_window_equities populated by
        # the gauntlet inside run_patha_verdict); we recompute the bundle's
        # funding_marginal after the gauntlet has run.
        funding_marginal=None,
    )

    # CONTRACT GAP 2 (closed): the fenced funding-marginal diagnostic on the forward
    # bars — the funding-gated equity (reused from the gauntlet) vs the IDENTICAL
    # no-funding baseline equity (the same strategy minus the funding gate), per
    # backtest.patha_marginal_diagnostic.funding_marginal. FENCED diagnostic-only
    # (promotion_affecting=False, in_n_star=False) — it rides along so a B-result
    # attributes to funding's MARGINAL contribution, and never feeds N*/promotion.
    funding_marginal = compute_funding_marginal(
        hypotheses=hypotheses,
        gated_window_equities=gated_window_equities,
        run_backtest_fn=run_backtest_fn,
        git_sha=git_sha,
    )
    bundle["funding_marginal"] = funding_marginal

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
            "Path A funding verdict: forward_2026 Tier-5 gate + train-only tiered "
            "mechanism sanity (24h+72h) + DSR-FWER(N*=3); NO Step-0 (fresh funding "
            "cohort). C7 TRAIN-window floors applied BEFORE ranking (under-floor -> "
            "INDETERMINATE, excluded from n_tier5_pass); C6 fenced funding-marginal "
            "diagnostic recorded (gated vs no-funding baseline on the forward bars; "
            "NEVER in N*/promotion)."
        ),
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "patha_verdict_advisory.json").write_text(
        json.dumps(bundle, indent=2, default=str)
    )
    return bundle


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="GATED Path A funding verdict RUN (Phase-D Charlie register-event ONLY)."
    )
    ap.add_argument("--out-dir", default=str(PATHA_VERDICT_DIR))
    args = ap.parse_args(argv)

    if not PHASE_D_AUTHORIZED:
        print(
            "patha_run_verdict: REFUSING — the forward_2026 RUN is Phase-D gated and "
            "NOT authorized. The C4-C7 scope is building + unit-testing this harness "
            "(mocked engine); executing the real verdict run is a SEPARATE Charlie "
            "register-event (Phase D). Do NOT flip PHASE_D_AUTHORIZED without that "
            "register. Aborting.",
            file=sys.stderr,
        )
        return 2

    # Real-engine path: authorized ONLY here, behind the PHASE_D_AUTHORIZED gate
    # above. run_verdict(_run_backtest=None) resolves the real engine internally and
    # re-asserts the gate (defense-in-depth) before any real run / artifact write.
    assert PHASE_D_AUTHORIZED, "unreachable: gate checked above"
    bundle = run_verdict(Path(args.out_dir))
    tax = bundle["taxonomy"]
    esc = bundle["escalation"]
    print(json.dumps({
        "advisory_taxonomy": tax["advisory_taxonomy"],
        "is_earned_negative": tax["is_earned_negative"],
        "b_positive_strength": tax.get("b_positive_strength"),
        "verdict_rests_on_weak_sane_only": tax.get("verdict_rests_on_weak_sane_only"),
        "n_tier5_pass": bundle["n_tier5_pass"],
        "n_dsr_pass": bundle["n_dsr_pass"],
        "approximation_tempers": tax["approximation_tempers"],
        "a_escalation_warranted": esc["a_escalation_warranted"],
        "escalation_reason": esc["reason"],
        "authority": "charlie_register_at_earned_negative_gate",
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""T1.5 (b) Smoke end-to-end pipeline tests.

Per ratified T1.5 sub-plan v3.2 (v_final) at
`docs/superpowers/plans/2026-05-23-t1_5-fixture-smoke-registry-test-suite-cycle-execution-plan.md`.

Sub-plan v_final RATIFIED 2026-05-24 per Charlie register chain
(cycle entry + Path B + sub-plan drafting fire + quant-research-advisor +
DS2 Option (i) + G1 + R1 + R2b + R1' + R5b + R6a + R7a) under B-C-extended
Scope-B structural artifact-preservation refactor cycle per R3.1d
sequencing 1→3→4.

Coverage scope (Contract 2.0.5 + 2.0.6 (b) per parent plan v5):
- End-to-end pipeline: engine entry point → moment computation → artifact
  writer → schema validator → registry triple-linkage insertion.
- 1-3 synthetic minimal candidates (recommend N=2 per §2.2.3).
- DS2 LOCKED 2026-05-24 Option (i) canonical OHLCV slice: 176 hourly bars
  from `data/raw/btcusdt_1h.parquet` 2023-08-01T00:00:00Z to
  2023-08-08T07:00:00Z (inclusive both endpoints; 0 zero-volume bars + 0
  NaN closes per orchestrator empirical 2026-05-24).
- Hand-written `strategies.baseline.sma_crossover.SMACrossover` per §2.2.3
  LOCK + CONTRACT GAP marker re warmup convention divergence (§2.2.3 v3.2):
  WARMUP_BARS = slow_period per L51 (hand-written convention); DSL-compiled
  convention `period - 1` per `strategies/dsl_compiler.py` L642+ would
  shift post-warmup count by 1 bar if T1.6 refactors.

DS2 fixture-time SHA256 snapshot (5-col OHLCV; updated per SEAL-eve v1 + v2
producer-consumer asymmetry closure 2026-05-24):
- Slice 5-col OHLCV (open + high + low + close + volume) float64 bytes
  SHA256: `cec2548a35881bd35bbf53e4683fc444c723be5c2e26a6f36bcb09216b3e5727`
- 176 bars × 5 columns over locked window (engine consumes all 5 OHLCV
  columns per CLAUDE.md Execution Convention rules 2/5/6).
- Fixture-time stability check at test setUp; fail closed if canonical
  parquet bytes drift (per §2.2.2 Option (i) SHA256 fixture-time-snapshot
  mitigation for canonical-data-drift risk).
- If SHA256 drifts: investigate (Binance Vision re-curation? reconcile.py
  bug?) + re-run smoke fixture-time empirical + update locked SHA256 if
  drift is legitimate per Q3 cost analysis at sub-plan §11.

Out-of-scope per §2.2.8:
- Per-fixture moment value verification (§2.1 Fixture scope; smoke uses
  defensive bands not equalities).
- Per-failure-case registry coverage (§2.3 Registry-integrity scope; smoke
  only happy-path triple linkage).
- Backward compat verification (T1.4 SEAL `tests/test_t1_4_backward_compat.py`).
- Slice-aware writer signature verification (T1.1 SEAL
  `engine.py:1133-1148` DESIGN INVARIANT marker + 4 mirror sites).
- Walk-forward integration (Contract 2.0.5 + T1.3 opt-out per γ-1 verified
  at T1.4 B3.3 — smoke uses `run_backtest()` single-run path only).
- Regime-holdout integrity (Phase 2A scope).
- Production-data smoke (running smoke against `phase4_forward_2026_15bps_v1`
  candidates) — out of T1.5 Path B narrow.

Hermetic isolation per §2.2.7 (CRITICAL):
- Temp RESULTS_DIR monkeypatch per test (no canonical `data/results/` pollution).
- Temp DEFAULT_DB_PATH monkeypatch per test (no canonical `experiments.db` pollution).
- Tempdir for artifact output (no canonical `data/phase2c_evaluation_gate/`
  pollution).
- Predictable UUID monkeypatch per T1.4 B3.1 pattern (avoids T1.1 SYS2-H2
  conflict-check fail-closed when scalar run_id != LC.run_id).
- Teardown pollution guard verifies no smoke artifacts leaked into canonical
  namespaces.

Per §2.2.6 cost_anchor_id end-to-end: `execution_config_path =
"config/execution.yaml"` → `cost_anchor_id = "legacy_perp_inspired_7bps_v0"`
(default mapping; lowest novelty; avoids Phase B Tier 5/6 anchor naming-
namespace leakage per §2.2.6 discipline).
"""
from __future__ import annotations

import hashlib
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import pytest


# ---------------------------------------------------------------------------
# Module-level constants per §2.2.2-locked DS2 spec
# ---------------------------------------------------------------------------

_REPO_ROOT: Path = Path(__file__).resolve().parent.parent
_PARQUET_PATH: Path = _REPO_ROOT / "data" / "raw" / "btcusdt_1h.parquet"
"""Canonical OHLCV parquet path per CLAUDE.md HARD CONSTRAINT (Data Integrity)."""

_DS2_WINDOW_START: datetime = datetime(2023, 8, 1, 0, 0, tzinfo=timezone.utc)
_DS2_WINDOW_END: datetime = datetime(2023, 8, 8, 7, 0, tzinfo=timezone.utc)
_DS2_EXPECTED_BAR_COUNT: int = 176
"""DS2 LOCKED 2026-05-24 window per §2.2.2-locked + §2.2.4 SMA crossover
post-warmup counts (SMA(5/20) → 156 post-warmup; SMA(10/30) → 146 post-warmup
per CONTRACT GAP marker at §2.2.3 hand-written SMACrossover convention)."""

_DS2_LOCKED_OHLCV_SHA256: str = (
    "cec2548a35881bd35bbf53e4683fc444c723be5c2e26a6f36bcb09216b3e5727"
)
"""Fixture-time SHA256 of DS2 window 5-column OHLCV float64 bytes
(open + high + low + close + volume) computed at HEAD 2026-05-24.

Stability check at test setUp per §2.2.2 Option (i) SHA256 fixture-time-
snapshot discipline. Fail-closed on drift.

Per SEAL-eve CONVERGED MEDIUM finding 2026-05-24 (Codex + Advisor #7
producer-consumer asymmetry per T1.1 9-iteration arc class): hash extended
from close-only to 5-column OHLCV. Engine consumes open/high/low/close/volume
for backtest execution per CLAUDE.md Execution Convention rules 2 (open at
N+1) / 5 (high/low intrabar stop/limit fills) / 6 (volume zero-volume
defer). Prior close-only hash would pass canonical-data integrity check
even if open/high/low/volume drifted silently — producer-consumer
asymmetry. Extended hash at producer layer per
`feedback_invariant_level_vs_enumeration.md` invariant-level-vs-enumeration
discipline."""

_SMOKE_EXECUTION_CONFIG_PATH: str = "config/execution.yaml"
"""Default mapping per §2.2.6 smoke recommendation (avoid Phase B anchor
naming-namespace leakage). Resolves to cost_anchor_id =
`legacy_perp_inspired_7bps_v0` per Contract 2.0.4 mapping table."""

_SMOKE_EXPECTED_COST_ANCHOR_ID: str = "legacy_perp_inspired_7bps_v0"
"""Per Contract 2.0.4 mapping table line 113 + R3.1d §5.2 LOCKED."""

# Smoke candidates per §2.2.3 (N=2; SMA crossover hand-written; locked per
# §2.2.3 CONTRACT GAP)
_SMOKE_CANDIDATES: tuple[dict[str, Any], ...] = (
    {
        "strategy_id": "smoke_sma_5_20",
        "hypothesis_hash": "smoke-hash-sma-5-20",
        "params": {"fast_period": 5, "slow_period": 20},
    },
    {
        "strategy_id": "smoke_sma_10_30",
        "hypothesis_hash": "smoke-hash-sma-10-30",
        "params": {"fast_period": 10, "slow_period": 30},
    },
)


# ---------------------------------------------------------------------------
# Module-level helpers
# ---------------------------------------------------------------------------


def _make_smoke_lineage_context(
    *,
    run_id: str,
    hypothesis_hash: str,
    source_batch_id: str = "smoke-batch-id",
    parquet_data_sha256: str | None = None,
) -> Any:
    """Construct a canonical deferred-state LineageContext for smoke testing.

    Per §2.2.6 + T1.4 B3.1 `_make_canonical_lineage_context` precedent;
    execution_config_path locked to `config/execution.yaml` per smoke
    recommendation (avoids Phase B anchor naming-namespace leakage).

    DEFERRED-STATE LATE_FILL per T1.1 SYS3-B1 pair-completeness: both
    returns_per_bar_path + returns_per_bar_sha256 empty (deferred state)
    so the test does NOT require artifact_dir + parquet write at fixture-
    time. The actual T1.1 writer populates these LATE_FILL fields after
    artifact write at runtime; smoke verifies LC threading contract.

    T_obs=10 placeholder discipline (per IPFR-fix Advisor #6 MEDIUM-1
    2026-05-24): T_obs=10 is a PLACEHOLDER value that does NOT reflect
    actual smoke-run post-warmup bar count (SMA(5/20) → 156 post-warmup;
    SMA(10/30) → 146 post-warmup per §2.2.3 hand-written SMACrossover
    convention). The placeholder is INTENTIONAL — deferred-state
    LATE_FILL convention (returns_per_bar_path="") triggers the
    engine.py:1353 LATE_FILL skip-path so SYS5 revalidate_for_write does
    NOT cross-check T_obs against per-bar returns count when in deferred
    state. Future SYS5 tightening (e.g., T_obs == actual_observed_count
    even in deferred state) would surface this placeholder as a constraint
    violation → require dynamic T_obs computation at LC construction time
    (or refactor smoke to non-deferred state with actual artifact_dir).
    Until then, T_obs=10 placeholder is acceptable per current contract.

    CONTRACT GAP — T_obs placeholder vs actual smoke-run count (per
    v_impl_polish v2 SEAL-eve v2 Codex MEDIUM E 2026-05-24 + CLAUDE.md
    L297-300 Contract Markers discipline): T_obs=10 placeholder is
    unclosed contract obligation. Trigger condition: future cycle
    refactoring smoke to non-deferred state (artifact_dir + actual
    write_per_bar_artifact invocation) MUST replace T_obs=10 placeholder
    with dynamic count computation from equity-curve post-warmup
    finite-row count (SMA(5/20) → 156; SMA(10/30) → 146). Closure
    mechanism: T1.5-followup successor cycle per §8.2 DS-NEW (f); fresh
    Charlie register-event required to fire. Per `feedback_invariant_
    level_vs_enumeration.md` invariant-level closure framework: closure
    deferred to production-chain coverage cycle (Path C 2026-05-24
    register).

    HIGH-F real parquet hash (per SEAL-eve v2 Codex HIGH F 2026-05-24):
    parquet_data_sha256 defaults to real DS2 window OHLCV bytes SHA256
    (computed via _compute_ds2_window_ohlcv_sha256()) — closes prior
    placeholder string `sha256:smoke-parquet-data` producer-consumer
    asymmetry. Production scripts compute real parquet bytes hash;
    smoke now matches semantic.
    """
    from backtest.artifact_schema import LineageContext

    if parquet_data_sha256 is None:
        # HIGH-F closure 2026-05-24: real DS2 window OHLCV bytes SHA256
        # (NOT placeholder string). Reuses _compute_ds2_window_ohlcv_sha256
        # helper for byte-deterministic real-data hash.
        _, hash_hex = _compute_ds2_window_ohlcv_sha256()
        parquet_data_sha256 = f"sha256:{hash_hex}"

    return LineageContext(
        run_id=run_id,
        hypothesis_hash=hypothesis_hash,
        source_batch_id=source_batch_id,
        regime_key="v2.regime_holdout",
        engine_commit="smoke-engine-commit",
        current_git_sha="smoke-git-sha-full",
        execution_config_path=_SMOKE_EXECUTION_CONFIG_PATH,
        execution_config_sha256="sha256:smoke-exec-config",
        parquet_data_sha256=parquet_data_sha256,
        returns_per_bar_path="",  # DEFERRED LATE_FILL
        returns_per_bar_sha256="",  # DEFERRED LATE_FILL
        T_obs=10,
        parent_run_id=None,
    )


def _make_db(tmp_path: Path, name: str = "smoke.db") -> Path:
    """Create a fresh temp experiments.db with create_table schema."""
    from backtest.experiment_registry import create_table

    db_path = tmp_path / name
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    create_table(conn)
    conn.close()
    return db_path


def _compute_ds2_window_ohlcv_sha256() -> tuple[int, str]:
    """Read canonical parquet, extract DS2 window slice, compute 5-column OHLCV SHA256.

    Returns:
        (bar_count, sha256_hex) tuple.

    Per §2.2.2 Option (i) SHA256 fixture-time-snapshot stability check;
    extended to 5-column OHLCV (open/high/low/close/volume) per SEAL-eve
    CONVERGED MEDIUM finding 2026-05-24 producer-consumer asymmetry
    closure (engine consumes all 5 OHLCV columns; close-only hash would
    miss open/high/low/volume drift per CLAUDE.md Execution Convention
    rules 2/5/6).
    """
    df = pd.read_parquet(_PARQUET_PATH)
    df["open_time_utc"] = pd.to_datetime(df["open_time_utc"], utc=True)
    mask = (df["open_time_utc"] >= pd.Timestamp(_DS2_WINDOW_START)) & (
        df["open_time_utc"] <= pd.Timestamp(_DS2_WINDOW_END)
    )
    slice_df = df[mask].sort_values("open_time_utc")
    ohlcv = slice_df[["open", "high", "low", "close", "volume"]].astype(float)
    ohlcv_bytes = ohlcv.values.tobytes()
    return (len(slice_df), hashlib.sha256(ohlcv_bytes).hexdigest())


# ---------------------------------------------------------------------------
# Test class
# ---------------------------------------------------------------------------


class TestT1_5_SmokeEndToEndPipeline:
    """T1.5 (b) Smoke end-to-end pipeline tests per sub-plan v3.2 (v_final) §2.2.

    Test methods:
    - test_AAA_canonical_parquet_exists — hard-asserted precondition (per T1.4
      B3.1 Codex F4 SEAL-eve discipline; skip-on-missing would make pc7
      optional)
    - test_AAB_ds2_window_close_sha256_matches_fixture_time_lock —
      canonical-data-drift detection at setUp per §2.2.2 Option (i)
      SHA256 fixture-time-snapshot mitigation; method name `test_AAB_`
      ensures alphabetical sorting fires after precondition + before
      substantive smoke
    - test_smoke_end_to_end_two_candidates — core smoke test per §2.2.3
      single-test-method-with-loop pattern (N=2 candidates; engine cost
      dominated by data loading not candidate count per §2.2.7)
    - test_pollution_guard_no_canonical_namespace_writes — teardown discipline
      per §2.2.7 (verifies no smoke artifacts leak into
      `data/phase2c_evaluation_gate/` canonical namespace)

    Hermetic isolation per §2.2.7 (CRITICAL):
    - Temp RESULTS_DIR monkeypatch per test
    - Temp DEFAULT_DB_PATH monkeypatch per test
    - Predictable UUID monkeypatch (T1.4 B3.1 SYS2-H2 conflict-check pattern)
    """

    def test_AAA_canonical_parquet_exists(self) -> None:
        """Hard-asserted precondition: canonical parquet at expected path.

        Per T1.4 B3.1 v4-4 Codex F4 SEAL-eve discipline + §5.1 Dependencies:
        skip-on-missing would silently make pc7 (full suite zero-regression)
        criterion optional — hard-assert instead.

        Method name `test_AAA_` ensures alphabetical sorting fires this test
        FIRST so subsequent smoke tests can assume canonical parquet
        availability.
        """
        assert _PARQUET_PATH.exists(), (
            f"Smoke test BLOCKING precondition: canonical parquet REQUIRED at "
            f"{_PARQUET_PATH}. Per CLAUDE.md HARD CONSTRAINT (Data Integrity), "
            f"this file is the canonical OHLCV dataset. If absent, "
            f"`reconcile.py` has not run or repo is partial; smoke test cannot "
            f"execute."
        )

    def test_AAB_ds2_window_ohlcv_sha256_matches_fixture_time_lock(self) -> None:
        """DS2 LOCKED 2026-05-24 window canonical-data-stability check (5-col OHLCV).

        Per §2.2.2 Option (i) SHA256 fixture-time-snapshot mitigation for
        canonical-data-drift risk. Computes SHA256 of 5-column OHLCV
        (open/high/low/close/volume) float64 bytes over DS2 LOCKED window
        (2023-08-01T00:00Z to 2023-08-08T07:00Z inclusive both endpoints
        = 176 bars).

        Compares against _DS2_LOCKED_OHLCV_SHA256 (computed at HEAD
        2026-05-24). Drift in ANY of open/high/low/close/volume bytes
        indicates canonical parquet changed at the DS2 window — investigate
        (Binance Vision re-curation? reconcile bug?) per §11 v_final Q3
        cost analysis.

        Per SEAL-eve CONVERGED MEDIUM 2026-05-24 producer-consumer asymmetry
        closure: hash extended from close-only to 5-col OHLCV. Engine
        backtest reads open (CLAUDE.md execution rule 2 N+1 fill) +
        high/low (rule 5 intrabar stop/limit) + close (rule 1 signal
        compute) + volume (rule 6 zero-volume defer); close-only hash
        would silently miss drift in other 4 columns affecting fills.

        Bonus assertion: bar count matches _DS2_EXPECTED_BAR_COUNT (176)
        per §2.2.2-locked.
        """
        bar_count, actual_sha256 = _compute_ds2_window_ohlcv_sha256()
        assert bar_count == _DS2_EXPECTED_BAR_COUNT, (
            f"DS2 window bar count drift: expected "
            f"{_DS2_EXPECTED_BAR_COUNT} hourly bars (2023-08-01T00:00Z to "
            f"2023-08-08T07:00Z inclusive both endpoints); got {bar_count} "
            f"bars. Canonical parquet may have lost or gained bars in this "
            f"window. Investigate before re-running smoke."
        )
        assert actual_sha256 == _DS2_LOCKED_OHLCV_SHA256, (
            f"DS2 window canonical-data-drift detected per §2.2.2 fixture-"
            f"time-snapshot discipline (5-col OHLCV): expected SHA256(open + "
            f"high + low + close + volume bytes) = {_DS2_LOCKED_OHLCV_SHA256}; "
            f"got {actual_sha256}. Canonical parquet OHLCV columns changed "
            f"at DS2 window. Investigate (Binance Vision re-curation? "
            f"reconcile.py bug? incremental update overlap?) before re-running "
            f"smoke + update fixture-time lock if drift is legitimate per §11 "
            f"Q3 cost analysis. Per SEAL-eve CONVERGED MEDIUM closure, the "
            f"hash covers all 5 columns engine consumes (NOT close-only)."
        )

    def test_smoke_end_to_end_two_candidates(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """End-to-end smoke for N=2 SMA crossover candidates per §2.2.3.

        Single-test-method-with-loop pattern per §2.2.7 (engine cost
        dominated by data loading not candidate count; clearest failure
        attribution).

        Per-candidate verification:
        - run_backtest completes without raising
        - Registry row populated with cost_anchor_id = legacy_perp_inspired_7bps_v0
          per Contract 2.0.4 mapping
        - Triple linkage (hypothesis_hash + batch_id + run_id) resolves to
          exactly one row per Contract 2.0.3
        - Backtest result is BacktestResult-shaped (not None/exception)

        Out-of-scope per §2.2.8: γ4/γ3 band assertion deferred to engine-
        internal moment computation verification (T1.1 SEAL scope); 14
        Contract 2.0.5 header field exhaustive verification deferred to
        T1.3 SEAL `tests/test_t1_3_registry_api.py` coverage; smoke verifies
        engine→writer→registry chain at registry-side resolution boundary.
        """
        # CONTRACT GAP: warmup convention divergence per sub-plan §2.2.3 +
        # v3.2 PFR-rule-Y v5 DEFECT-MICRO-3 re-tag from DESIGN INVARIANT.
        # Trigger condition: if T1.6 or future cycle refactors smoke
        # candidates from hand-written `SMACrossover.WARMUP_BARS =
        # slow_period` (strategies/baseline/sma_crossover.py:51) to
        # DSL-compiled crossover (`factors.registry.max_warmup` per
        # strategies/dsl_compiler.py:L642+ which uses `period - 1`
        # registry convention per factors/moving_averages.py:83/93),
        # post-warmup count would shift by 1 bar (SMA(5/20) → 157 not 156;
        # SMA(10/30) → 147 not 146) → §2.2.4 PASS band recalibration
        # required + new test fixture or assertion mechanism to enforce
        # the locked convention. 1-bar drift risk; fresh Charlie
        # register-event required to authorize DSL refactor. Per CLAUDE.md
        # L297-300 Contract Markers ("CONTRACT GAP = a test or mechanism
        # that should exist but doesn't yet, with a trigger condition")
        # + Advisor #6 IPFR LOW-4 2026-05-24 (formal marker keyword at
        # exact code site).
        import backtest.engine as engine_mod
        import backtest.experiment_registry as registry_mod
        from strategies.baseline.sma_crossover import SMACrossover

        # Hermetic isolation per §2.2.7
        results_dir = tmp_path / "results"
        results_dir.mkdir(exist_ok=True)
        monkeypatch.setattr("backtest.engine.RESULTS_DIR", results_dir)

        db_path = _make_db(tmp_path, name="smoke_end_to_end.db")
        monkeypatch.setattr(registry_mod, "DEFAULT_DB_PATH", db_path)

        # Per-candidate loop (single test method amortizes engine setup)
        for i, candidate in enumerate(_SMOKE_CANDIDATES):
            # Predictable UUID matches LC.run_id (T1.4 B3.1 SYS2-H2 pattern)
            predictable_uuid = f"00000000-0000-0000-0000-{i:012d}"

            import uuid as uuid_mod
            monkeypatch.setattr(
                uuid_mod, "uuid4",
                lambda u=predictable_uuid: uuid_mod.UUID(u),
            )

            lc = _make_smoke_lineage_context(
                run_id=predictable_uuid,
                hypothesis_hash=candidate["hypothesis_hash"],
            )

            # Invoke engine on DS2 LOCKED window
            result = engine_mod.run_backtest(
                strategy_cls=SMACrossover,
                start_date=_DS2_WINDOW_START,
                end_date=_DS2_WINDOW_END,
                strategy_params=candidate["params"],
                parquet_path=_PARQUET_PATH,
                db_path=db_path,
                lineage_context=lc,
            )

            # Verify result shape (not None / not exception)
            assert result is not None, (
                f"Smoke candidate {candidate['strategy_id']!r}: run_backtest "
                f"returned None; expected BacktestResult instance."
            )

            # Verify registry row populated + triple linkage resolves
            conn = sqlite3.connect(str(db_path))
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT * FROM runs WHERE hypothesis_hash = ? AND batch_id = ? "
                "AND run_id = ?",
                (candidate["hypothesis_hash"], "smoke-batch-id",
                 predictable_uuid),
            ).fetchall()
            conn.close()

            assert len(rows) == 1, (
                f"Smoke candidate {candidate['strategy_id']!r}: triple "
                f"linkage query (hypothesis_hash={candidate['hypothesis_hash']!r}, "
                f"batch_id='smoke-batch-id', run_id={predictable_uuid!r}) "
                f"must return exactly 1 row; got {len(rows)}."
            )
            row = rows[0]

            # cost_anchor_id end-to-end check per §2.2.6 + Contract 2.0.4
            assert row["cost_anchor_id"] == _SMOKE_EXPECTED_COST_ANCHOR_ID, (
                f"Smoke candidate {candidate['strategy_id']!r}: "
                f"cost_anchor_id end-to-end mismatch — expected "
                f"{_SMOKE_EXPECTED_COST_ANCHOR_ID!r} per Contract 2.0.4 "
                f"mapping for execution_config_path="
                f"{_SMOKE_EXECUTION_CONFIG_PATH!r}; got "
                f"{row['cost_anchor_id']!r}."
            )

            # Triple linkage field-level verification
            assert row["run_id"] == predictable_uuid
            assert row["hypothesis_hash"] == candidate["hypothesis_hash"]
            assert row["batch_id"] == "smoke-batch-id"

            # Per SEAL-eve HIGH-1 fix 2026-05-24 (Codex): exercise engine→
            # moment-computation chain on actual smoke-run equity curve.
            # Per §2.2.4 PASS criteria + §2.2.8 cross-reference to engine-
            # internal moment computation: smoke must verify γ3/γ4/T_obs
            # in defensive bands per §2.2.4 ("Calibration over 1-3
            # candidates is LOOSE — recommend assert isfinite(γ4) AND γ4 > 0
            # as the durable assertion").
            from backtest.engine import compute_moments, compute_per_bar_returns

            # BacktestResult @dataclass guarantees equity_curve field per
            # engine.py:635-649; per SEAL-eve v2 Advisor #8 LOW dead-code
            # removal 2026-05-24, removed defensive-but-unreachable
            # hasattr/get_equity_curve fallback.
            equity_curve = result.equity_curve
            assert equity_curve is not None and len(equity_curve) > 0, (
                f"Smoke candidate {candidate['strategy_id']!r}: BacktestResult "
                f"equity_curve must be non-empty for moment-computation chain."
            )

            per_bar_returns = compute_per_bar_returns(equity_curve)
            moments = compute_moments(per_bar_returns.values)

            assert moments["T_obs"] is not None and moments["T_obs"] > 0, (
                f"Smoke candidate {candidate['strategy_id']!r}: T_obs must "
                f"be > 0 from actual equity curve; got T_obs={moments['T_obs']}."
            )
            assert moments["gamma3"] is not None, (
                f"Smoke candidate {candidate['strategy_id']!r}: γ3 must be "
                f"finite (T_obs >= 2 + std > 0); got None."
            )
            assert moments["gamma4"] is not None, (
                f"Smoke candidate {candidate['strategy_id']!r}: γ4 must be "
                f"finite (T_obs >= 2 + std > 0); got None."
            )
            import math
            assert math.isfinite(moments["gamma3"]), (
                f"Smoke candidate {candidate['strategy_id']!r}: γ3 must be "
                f"finite; got {moments['gamma3']!r}."
            )
            assert math.isfinite(moments["gamma4"]), (
                f"Smoke candidate {candidate['strategy_id']!r}: γ4 must be "
                f"finite; got {moments['gamma4']!r}."
            )
            # Defensive band per §2.2.4 ("assert isfinite(γ4) AND γ4 > 0")
            assert moments["gamma4"] > 0, (
                f"Smoke candidate {candidate['strategy_id']!r}: γ4 must be "
                f"> 0 (raw kurtosis is non-negative by construction); got "
                f"{moments['gamma4']!r}. Defensive band per §2.2.4 catches "
                f"runaway computational bug."
            )

    def test_pollution_guard_no_canonical_namespace_writes(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Verify no smoke artifacts leak into canonical phase2c_evaluation_gate/.

        Per §2.2.7 pollution guard discipline. If smoke test writes ANY
        artifact under `data/phase2c_evaluation_gate/` (not under tempdir),
        that's a test bug — pytest worker concurrency + future test runs
        would interfere.

        This is a defensive teardown-style check: snapshot canonical gate
        directory entries before + after a smoke run; verify no new
        smoke_*-prefixed entries appeared.
        """
        # Per SEAL-eve MEDIUM B2 (Advisor #7) + LOW B (Codex) fix 2026-05-24:
        # original target was canonical phase2c_evaluation_gate/ but engine
        # writes trade CSVs to RESULTS_DIR (data/results/) per engine.py:830.
        # Fixed target = canonical RESULTS_DIR (the actual leak surface);
        # smoke test monkeypatches RESULTS_DIR to tempdir so NO new
        # trades_*.csv files should appear at canonical path.
        canonical_results_dir = _REPO_ROOT / "data" / "results"
        if not canonical_results_dir.exists():
            pytest.skip(
                "Canonical data/results/ dir absent; pollution guard cannot "
                "evaluate (run any backtest first to create the dir)."
            )

        # Snapshot existing entries (any prior leaked artifacts would already
        # be a defect from prior test runs; baseline = current state).
        # Per SEAL-eve v2 Codex MEDIUM B fix 2026-05-24: recursive rglob
        # (not iterdir) catches subdirectory writes that current engine
        # doesn't make but future engine might (defensive depth).
        before = {
            str(p.relative_to(canonical_results_dir))
            for p in canonical_results_dir.rglob("*") if p.is_file()
        }

        # Re-run smoke (mini version; single candidate)
        import backtest.engine as engine_mod
        import backtest.experiment_registry as registry_mod
        from strategies.baseline.sma_crossover import SMACrossover

        results_dir = tmp_path / "results"
        results_dir.mkdir(exist_ok=True)
        monkeypatch.setattr("backtest.engine.RESULTS_DIR", results_dir)

        db_path = _make_db(tmp_path, name="pollution_guard.db")
        monkeypatch.setattr(registry_mod, "DEFAULT_DB_PATH", db_path)

        predictable_uuid = "00000000-0000-0000-0000-000000000099"
        import uuid as uuid_mod
        monkeypatch.setattr(
            uuid_mod, "uuid4",
            lambda: uuid_mod.UUID(predictable_uuid),
        )

        lc = _make_smoke_lineage_context(
            run_id=predictable_uuid,
            hypothesis_hash="smoke-pollution-guard-hash",
        )

        engine_mod.run_backtest(
            strategy_cls=SMACrossover,
            start_date=_DS2_WINDOW_START,
            end_date=_DS2_WINDOW_END,
            strategy_params={"fast_period": 5, "slow_period": 20},
            parquet_path=_PARQUET_PATH,
            db_path=db_path,
            lineage_context=lc,
        )

        # Verify no NEW entries in canonical RESULTS_DIR (any new entry is
        # leakage from monkeypatch failure). Per SEAL-eve fix 2026-05-24:
        # target corrected from phase2c_evaluation_gate (engine doesn't
        # write there) to RESULTS_DIR (actual engine write surface per
        # engine.py:830 trades_<run_id>.csv).
        after = {
            str(p.relative_to(canonical_results_dir))
            for p in canonical_results_dir.rglob("*") if p.is_file()
        }
        new_entries = after - before
        assert not new_entries, (
            f"Smoke test pollution detected: new files appeared in canonical "
            f"{canonical_results_dir}: {new_entries}. RESULTS_DIR monkeypatch "
            f"should redirect ALL engine writes to tempdir per §2.2.7 "
            f"hermetic isolation; any new file at canonical path indicates "
            f"monkeypatch failure or unexpected engine write path. Per "
            f"SEAL-eve MEDIUM B2 (Advisor #7) + LOW B (Codex) fix 2026-05-24."
        )

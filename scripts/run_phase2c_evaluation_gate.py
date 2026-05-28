"""Phase 2C evaluation gate — regime holdout AND-gate against corrected candidates.

Runs the regime holdout AND-gate (per config/environments.yaml +
backtest.engine._evaluate_regime_holdout_pass) against Phase 2C
corrected candidates. Per docs/phase2c/PHASE2C_6_EVALUATION_GATE_PLAN.md
(2022 single-regime arc) and docs/phase2c/PHASE2C_7_1_PLAN.md
(multi-regime extension introducing --regime-key).

Three reusable engine entry points called by this script:
    - backtest.engine.run_regime_holdout: top-level wrapper
    - backtest.engine._evaluate_regime_holdout_pass: 4-condition AND gate
    - backtest.engine._load_regime_block_config: parameterized env config
      loader (renamed from _load_regime_holdout_config in PHASE2C_7.1
      sub-step 1.2 to support multi-regime evaluation; the
      regime_holdout block remains the default for backward-compat)

Cross-block passing_criteria coupling (PHASE2C_7.1 §3 / Q1).
The `validation` block in environments.yaml has no passing_criteria
field; when --regime-key v2.validation is used, the engine inherits the
4-criterion gate from the canonical regime_holdout block and emits an
INFO log line documenting the inheritance. Producer-side docstring
audience: a future maintainer wondering "what gate thresholds did the
2024 evaluation use?" reads the answer here — the inherited criteria
are the regime_holdout block's verbatim, by design, so all
single-regime holdout evaluations across arcs share one source of
truth for "what does it mean to pass". See backtest/engine.py
_resolve_passing_criteria_with_inheritance() for the resolver.

Two attestation domains kept separate per backtest/wf_lineage.py:
    - WF artifacts: walk_forward_results / walk_forward_summary use
      wf_semantics='corrected_test_boundary_v1' (NOT used here)
    - Single-run holdout artifacts: this script's outputs use
      evaluation_semantics='single_run_holdout_v1' + the 5 legacy
      lineage fields validated by check_evaluation_semantics_or_raise().

PHASE2C_7.1 §7 schema discriminator (Q3(a)).
Every artifact produced by this script under PHASE2C_7.1+ code carries
three additional lineage fields regardless of regime:
    - artifact_schema_version: producer-code identity ("phase2c_7_1")
    - regime_key:              regime identity (--regime-key value)
    - regime_label:            regime label (mapping-derived)
Mental model: schema_version = producer code identity; regime fields =
which regime the artifact attests against. Independent axes — a 2022
re-run produced today carries phase2c_7_1 + v2.regime_holdout +
bear_2022. PHASE2C_6-on-disk artifacts predate this schema and remain
untouched (the consumer guard's absent-field branch handles them).

CLI surface:
    --source-batch-id <phase2c_batch_uuid>  Upstream Phase 2C proposer batch
                                            whose corrected candidates are
                                            evaluated. Default: b6fcbf86-...
    --universe primary|audit                primary=44 corrected winners;
                                            audit=all 198 corrected candidates
    --candidate-hashes <csv>                Comma-separated 8+ char hash
                                            prefixes. Mutually exclusive with
                                            --universe.
    --run-id <id>                           Identifier for THIS evaluation run
                                            (smoke_v1, or auto-UUID4).
    --regime-key <key>                      Regime to evaluate against. Default:
                                            v2.regime_holdout (PHASE2C_6
                                            backward-compat). Use v2.validation
                                            for the PHASE2C_7.1 2024 arc.
                                            Must be a key in
                                            REGIME_KEY_LABEL_MAPPING.
    --output-root <path>                    Default: data/phase2c_evaluation_gate/
    --dry-run                               Verify config + candidate selection
                                            without running backtests.
    --force                                 Allow overwriting non-empty
                                            <output-root>/<run-id>/.

Lineage guard ordering: parse_args() runs first (so --help works
without invoking git), then enforce_corrected_engine_lineage() runs
before any engine execution or artifact write.
"""
from __future__ import annotations

import argparse
import csv
import json
import logging
import re
import shutil  # B-C-narrow Phase 2: archive PRE-flight uses shutil.move
import sys
import traceback
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backtest.engine import run_regime_holdout, RegimeHoldoutResult  # noqa: E402
from backtest.wf_lineage import (  # noqa: E402
    ARTIFACT_SCHEMA_VERSION_PHASE2C_7_1,
    regime_key_to_schema_version,
    CORRECTED_WF_ENGINE_COMMIT,
    ENGINE_CORRECTED_LINEAGE_TAG,
    EVALUATION_SEMANTICS_TAG,
    REGIME_KEY_LABEL_MAPPING,
    check_evaluation_semantics_or_raise,
    enforce_corrected_engine_lineage,
)
from strategies.dsl import StrategyDSL  # noqa: E402

# B-C-narrow Phase 2 v3: producer-side moments compute helpers (Phase 0 SEAL chain f112599).
# v2 per CB6 PFR R1: REMOVED _compute_sha256_file import — producer no longer recomputes
# SHA; queries engine-written child registry row via get_run instead.
# v3 per LR2-1 PFR R2 ADOPT: re-added `# noqa: E402` (lines 89-90 contain non-import code
# `PROJECT_ROOT` + `sys.path.insert` per scripts:89-90; existing imports lines 92-103 use noqa
# for this reason; Ruff at pyproject.toml:61-62 selects E rules).
from backtest.engine import (  # noqa: E402
    compute_moments,
    compute_per_bar_returns,
)
# CB3 PFR R1: fee_model derivation from execution_config — producer reads cost_model.fee_model_label
# (matches engine's children-row stamp at engine.py:1278). NO hardcoded fee_model literal.
from backtest.execution_model import ConstantSlippage, load_execution_config  # noqa: E402
# H2 PFR R1: DEFAULT_DB_PATH explicit import for parent-child co-location regression guard
# (Test 20). Producer's `db_path: Path | None = None` kwarg defaults to None → get_connection's
# default → DEFAULT_DB_PATH; engine's run_regime_holdout's db_path defaults likewise. Importing
# the constant explicitly makes the contract visible to the reader.
from backtest.experiment_registry import (  # noqa: E402
    DEFAULT_DB_PATH,
    create_table,
    get_connection,
    get_run,
    insert_run,
)
# LR3-2 PFR R3 ADOPT (v4): REMOVED `PROJECT_ROOT as REGISTRY_PROJECT_ROOT` alias —
# unused in producer body (Test 20 has its own import per MR2-2 v3 fix). Would
# trigger Ruff F401 unused-import if enforced.

logger = logging.getLogger(__name__)

DEFAULT_SOURCE_BATCH_ID = "b6fcbf86-4d57-4d1f-ae41-1778296b1ae9"
DEFAULT_OUTPUT_ROOT = PROJECT_ROOT / "data" / "phase2c_evaluation_gate"
DEFAULT_CORRECTED_BATCH_ROOT = (
    PROJECT_ROOT / "data" / "phase2c_walkforward"
)
DEFAULT_RAW_PAYLOADS_DIR = PROJECT_ROOT / "raw_payloads"

PRIMARY_THRESHOLD = 0.5  # corrected wf_test_period_sharpe > this = primary winner

# PHASE4 forward-test constants (PHASE4_PLAN §1.2 sealed at 432b2bd).
PHASE4_FORWARD_2026_REGIME_KEY = "evaluation_regimes.forward_2026"
PHASE4_FORWARD_WINDOW_START_UTC = "2026-01-01T00:00:00Z"
PHASE4_FORWARD_WINDOW_START_DATE = "2026-01-01"  # date-only form for date.fromisoformat
DEFAULT_PARQUET_PATH = PROJECT_ROOT / "data" / "raw" / "btcusdt_1h.parquet"

# ---------------------------------------------------------------------------
# B-C-narrow recovery cycle locked identity constants (per Plan v3-Phase2 v2
# PFR R1 ADOPT M5). All B-C-narrow recovery wiring references these constants;
# NO inline literals. Operator misuse is caught at identity guard (CB2) which
# compares CLI args to these locked values.
#
# Source-of-truth locks (DO NOT change without spec amend):
# - BCNARROW_PARENT_RUN_ID:        spec §2 Q4 + §3.2.3
# - BCNARROW_ARCHIVE_BASENAME:     spec §2 Q3 (uses original `current_git_sha`=d0b8101)
# - BCNARROW_SOURCE_BATCH_ID:      spec §1 + G3 inventory (combined synthetic dir)
# - BCNARROW_REGIME_KEY:           spec §1 cohort_a forward_2026
# - BCNARROW_EXECUTION_CONFIG_PATH: spec §2 Q5 cost anchor lock
# ---------------------------------------------------------------------------
BCNARROW_PARENT_RUN_ID: str = "phase4_forward_2026_15bps_v1_b_c_narrow"
BCNARROW_ARCHIVE_BASENAME: str = "phase4_forward_2026_15bps_v1_d0b8101"
BCNARROW_SOURCE_BATCH_ID: str = "phase2c_15_main_fire_combined"
BCNARROW_REGIME_KEY: str = PHASE4_FORWARD_2026_REGIME_KEY  # alias for clarity at recovery sites
BCNARROW_EXECUTION_CONFIG_PATH: str = "config/execution_phase4_15bps.yaml"
# AR-SE-R2-M4 SEAL-eve R2 ADOPT v10: canonical artifact basename — extracted from
# hardcoded literals at 5 sites (W3 producer call + 4 test fixtures). M5 PFR R1
# ADOPT extracted other BCNARROW_* constants but missed this one; v10 closes
# constant-extraction discipline gap.
BCNARROW_CANONICAL_BASENAME: str = "phase4_forward_2026_15bps_v1"


def _capture_phase4_forward_window_metadata(
    parquet_path: Path = DEFAULT_PARQUET_PATH,
) -> dict[str, Any]:
    """Capture PHASE4 forward-window metadata at fire-time.

    Per PHASE4_PLAN §1.2: pre-fire data refresh permitted (extends
    T_end forward); post-fire freezes T_end at fire register-event
    boundary. This helper reads the parquet ONCE at fire-time and
    returns the immutable metadata block embedded into the run's
    holdout_summary.json. The same captured T_end is also injected
    into the env_config override per R2 (the engine consumer at
    backtest/engine.py:1564 calls date.fromisoformat(block["end"])
    which crashes on None — this fix produces a YYYY-MM-DD string).

    Returns dict with:
        forward_window_start_utc: PLAN-locked "2026-01-01T00:00:00Z"
        forward_window_end_utc: ISO timestamp of last forward bar
            (e.g., "2026-04-16T07:00:00Z")
        forward_bar_count: count of bars in [2026-01-01, T_end]
        parquet_data_sha256: SHA256 of parquet file content (locks
            input data state for reproducibility)
        forward_end_date_iso: date-only form for engine consumer
            (e.g., "2026-04-16"); engine widens to <date>T23:00:00Z
            internally per backtest/engine.py:1571-1574
    """
    import hashlib

    import pandas as pd
    import pyarrow.parquet as pq

    if not parquet_path.exists():
        raise FileNotFoundError(
            f"PHASE4 forward-window capture requires parquet at "
            f"{parquet_path}; not found. Run "
            f"`python -m ingestion.incremental_update` first."
        )

    df = pq.read_table(parquet_path).to_pandas()
    forward = df[
        df["open_time_utc"]
        >= pd.Timestamp(PHASE4_FORWARD_WINDOW_START_UTC, tz="UTC")
    ]
    if forward.empty:
        raise ValueError(
            f"No forward bars at {parquet_path} after "
            f"{PHASE4_FORWARD_WINDOW_START_UTC}; "
            f"parquet must contain data >= 2026-01-01 UTC for "
            f"PHASE4 forward-test. Run incremental_update."
        )

    last_bar_ts = forward["open_time_utc"].max()
    parquet_sha256 = hashlib.sha256(parquet_path.read_bytes()).hexdigest()

    return {
        "forward_window_start_utc": PHASE4_FORWARD_WINDOW_START_UTC,
        "forward_window_end_utc": last_bar_ts.isoformat().replace(
            "+00:00", "Z"
        ),
        "forward_bar_count": int(len(forward)),
        "parquet_data_sha256": parquet_sha256,
        "forward_end_date_iso": str(last_bar_ts.date()),
    }


def _build_phase4_env_config_override(
    forward_window_metadata: dict[str, Any],
) -> dict[str, Any]:
    """Build env_config override per R2 (PHASE4 implementation arc Task 4
    pre-fire fix for null-end consumer crash).

    The runner provides this override to run_regime_holdout(env_config=...)
    so the engine sees forward_2026.end as a concrete YYYY-MM-DD date
    string instead of YAML null. Engine consumer at
    backtest/engine.py:1564 calls date.fromisoformat(block["end"])
    which would crash on None; this fix injects the captured T_end
    date pre-fire so the consumer receives a valid string.

    Per advisor R2 lean: scope Phase-4-specific logic to runner;
    leverage existing env_config override API at engine.py:1471
    (consumer-side override pattern already supported); no engine
    code change needed.
    """
    import yaml

    env_config_path = PROJECT_ROOT / "config" / "environments.yaml"
    env_config = yaml.safe_load(env_config_path.read_text())

    # Defensive verify — environments.yaml must have forward_2026 block
    # with end:null at this register (Task 2 SEAL invariant).
    er = env_config.get("evaluation_regimes", {})
    fwd = er.get("forward_2026")
    if fwd is None:
        raise RuntimeError(
            "environments.yaml does NOT have evaluation_regimes.forward_2026 "
            "block. PHASE4 forward-test requires Task 2 SEAL (commit a4bd82a "
            "or descendant). Cannot proceed with R2 env_config override."
        )
    if fwd.get("end") is not None:
        raise RuntimeError(
            f"environments.yaml has evaluation_regimes.forward_2026.end="
            f"{fwd.get('end')!r} (expected null per PHASE4_PLAN §1.2 + "
            f"Task 2 SEAL). T_end is captured at fire-time, not config-time. "
            f"Did someone write a date into the YAML file? That violates "
            f"the immutable-imported-artifact invariant."
        )

    # Inject captured T_end as date-only string (engine consumer expects YYYY-MM-DD)
    env_config["evaluation_regimes"]["forward_2026"]["end"] = (
        forward_window_metadata["forward_end_date_iso"]
    )
    return env_config

# Markdown fence regex matching scripts/run_phase2c_batch_walkforward.py
_FENCE_RE = re.compile(
    r"```(?:\s*json)?\s*(.*?)\s*```",
    re.DOTALL | re.IGNORECASE,
)


def _strip_markdown_fence(raw: str) -> str:
    """Strip markdown code fence; return contents if found, else raw."""
    m = _FENCE_RE.search(raw)
    return m.group(1) if m else raw


def _utc_now_iso() -> str:
    """Return current UTC time as ISO-8601 with Z suffix."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# Candidate selection
# ---------------------------------------------------------------------------


def _load_corrected_candidates(source_batch_id: str) -> list[dict[str, Any]]:
    """Load all 198 corrected candidates from the corrected CSV.

    Returns one dict per candidate with: hypothesis_hash, position, theme,
    name, wf_test_period_sharpe.
    """
    corrected_dir = (
        DEFAULT_CORRECTED_BATCH_ROOT
        / f"batch_{source_batch_id}_corrected"
    )
    csv_path = corrected_dir / "walk_forward_results.csv"
    if not csv_path.exists():
        raise FileNotFoundError(
            f"Corrected Phase 2C CSV not found at {csv_path}. "
            f"Verify --source-batch-id is correct."
        )
    candidates: list[dict[str, Any]] = []
    with open(csv_path) as f:
        for row in csv.DictReader(f):
            candidates.append({
                "hypothesis_hash": row["hypothesis_hash"],
                "position": int(row["position"]),
                "theme": row["theme"],
                "name": row["name"],
                "wf_test_period_sharpe": float(
                    row["wf_test_period_sharpe"]
                ) if row["wf_test_period_sharpe"] else 0.0,
            })
    return candidates


def _resolve_candidate_universe(
    args: argparse.Namespace,
    all_candidates: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Apply --universe / --candidate-hashes to the full candidate list."""
    if args.candidate_hashes:
        prefixes = [
            h.strip() for h in args.candidate_hashes.split(",") if h.strip()
        ]
        selected: list[dict[str, Any]] = []
        for prefix in prefixes:
            matches = [
                c for c in all_candidates
                if c["hypothesis_hash"].startswith(prefix)
            ]
            if len(matches) == 0:
                raise ValueError(
                    f"--candidate-hashes prefix {prefix!r} matched no "
                    f"candidate in source batch."
                )
            if len(matches) > 1:
                raise ValueError(
                    f"--candidate-hashes prefix {prefix!r} matched "
                    f"{len(matches)} candidates (ambiguous): "
                    f"{[m['hypothesis_hash'] for m in matches]}"
                )
            selected.append(matches[0])
        return selected
    if args.universe == "primary":
        return [
            c for c in all_candidates
            if c["wf_test_period_sharpe"] > PRIMARY_THRESHOLD
        ]
    # audit: all 198
    return list(all_candidates)


# ---------------------------------------------------------------------------
# DSL re-extraction from raw_payloads
# ---------------------------------------------------------------------------


def _load_dsl_from_response(
    source_batch_id: str, position: int
) -> StrategyDSL:
    """Re-extract a candidate's DSL from raw_payloads/.../attempt_NNNN_response.txt."""
    response_path = (
        DEFAULT_RAW_PAYLOADS_DIR
        / f"batch_{source_batch_id}"
        / f"attempt_{position:04d}_response.txt"
    )
    if not response_path.exists():
        raise FileNotFoundError(
            f"raw_payloads response file not found at {response_path}"
        )
    raw_text = response_path.read_text(encoding="utf-8")
    payload = json.loads(_strip_markdown_fence(raw_text))
    return StrategyDSL.model_validate(payload)


# ---------------------------------------------------------------------------
# Lineage stamping
# ---------------------------------------------------------------------------


def _lineage_metadata(head_sha: str, regime_key: str) -> dict[str, str]:
    """Construct the lineage metadata block stamped on every artifact.

    Returns 5 legacy fields (PHASE2C_6 single-run holdout schema) PLUS
    3 PHASE2C_7.1 §7 fields. Q3(a): every forward artifact stamps all
    8 fields regardless of regime. Mental model: schema_version is
    producer-code identity (which producer wrote this artifact),
    regime_key/regime_label are regime identity (which regime is being
    attested). Independent axes — a v2.regime_holdout artifact produced
    today still carries artifact_schema_version="phase2c_7_1" because
    today's producer code knows the schema, even when the attested
    regime is the original 2022 bear regime.

    Args:
        head_sha: Resolved git HEAD SHA (from enforce_corrected_engine_lineage).
        regime_key: Dotted regime identifier; must be a key in
            REGIME_KEY_LABEL_MAPPING. The corresponding regime_label
            is mapping-derived.

    Raises:
        ValueError: If regime_key is not in REGIME_KEY_LABEL_MAPPING.
            Failing here (vs. discovering at consumer-guard time) keeps
            unknown regime_keys from producing unvalidated artifacts.
    """
    regime_label = REGIME_KEY_LABEL_MAPPING.get(regime_key)
    if regime_label is None:
        raise ValueError(
            f"regime_key={regime_key!r} is not in REGIME_KEY_LABEL_MAPPING "
            f"(known: {sorted(REGIME_KEY_LABEL_MAPPING)}). Cannot derive "
            f"regime_label. Update backtest/wf_lineage.py:REGIME_KEY_LABEL_MAPPING "
            f"if a new regime is being introduced."
        )
    # PHASE2C_8.1 §7 — per-regime schema discriminator selection. Inherited
    # regimes (v2.regime_holdout, v2.validation) stamp phase2c_7_1; novel
    # regimes (evaluation_regimes.eval_2020_v1, evaluation_regimes.eval_2021_v1)
    # stamp phase2c_8_1. Mixed-discriminator metadata reconciliation per
    # spec §6.5 — the consumer guard accepts both versions via
    # ACCEPTED_ARTIFACT_SCHEMA_VERSIONS; the per-regime stamp records
    # arc-of-origin without coupling comparison logic to discriminator value.
    schema_version = regime_key_to_schema_version(regime_key)
    return {
        "evaluation_semantics": EVALUATION_SEMANTICS_TAG,
        "engine_commit": CORRECTED_WF_ENGINE_COMMIT,
        "engine_corrected_lineage": ENGINE_CORRECTED_LINEAGE_TAG,
        "current_git_sha": head_sha,
        "lineage_check": "passed",
        # PHASE2C_7.1 §7 — Q3(a): stamped on every artifact regardless of regime.
        # PHASE2C_8.1 §7 — schema discriminator now per-regime (mapping-derived).
        "artifact_schema_version": schema_version,
        "regime_key": regime_key,
        "regime_label": regime_label,
    }


# ---------------------------------------------------------------------------
# Per-candidate evaluation
# ---------------------------------------------------------------------------


def _per_candidate_summary(
    candidate: dict[str, Any],
    head_sha: str,
    source_batch_id: str,
    run_id: str,
    regime_key: str,
    holdout_result: RegimeHoldoutResult | None,
    lifecycle_state: str,
    error_message: str | None,
    wall_clock_seconds: float,
) -> dict[str, Any]:
    """Build the per-candidate summary dict.

    For lifecycle_state == 'holdout_error', the 4 gate metrics and 4
    pass/fail flags are null per the regime_holdout_passed: bool | None
    pattern in backtest/engine.py:502.
    """
    summary: dict[str, Any] = {
        "source_batch_id": source_batch_id,
        "run_id": run_id,
        "hypothesis_hash": candidate["hypothesis_hash"],
        "position": candidate["position"],
        "theme": candidate["theme"],
        "name": candidate["name"],
        "wf_test_period_sharpe": candidate["wf_test_period_sharpe"],
        "lifecycle_state": lifecycle_state,
        "error_message": error_message,
        "wall_clock_seconds": round(wall_clock_seconds, 4),
    }
    if holdout_result is not None:
        passing_criteria = holdout_result.passing_criteria
        summary["holdout_metrics"] = {
            "sharpe_ratio": holdout_result.sharpe_ratio,
            "max_drawdown": holdout_result.max_drawdown,
            "total_return": holdout_result.total_return,
            "total_trades": holdout_result.total_trades,
        }
        summary["passing_criteria"] = passing_criteria
        summary["gate_pass_per_criterion"] = {
            "sharpe_passed": (
                holdout_result.sharpe_ratio
                >= passing_criteria["min_sharpe"]
            ),
            "drawdown_passed": (
                holdout_result.max_drawdown
                <= passing_criteria["max_drawdown"]
            ),
            "return_passed": (
                holdout_result.total_return
                >= passing_criteria["min_total_return"]
            ),
            "trades_passed": (
                holdout_result.total_trades
                >= passing_criteria["min_total_trades"]
            ),
        }
        summary["holdout_passed"] = holdout_result.regime_holdout_passed
    else:
        # holdout_error: gate didn't run, all gate fields are null
        summary["holdout_metrics"] = None
        summary["passing_criteria"] = None
        summary["gate_pass_per_criterion"] = None
        summary["holdout_passed"] = None
    summary.update(_lineage_metadata(head_sha, regime_key))
    return summary


def _evaluate_one_candidate(
    candidate: dict[str, Any],
    head_sha: str,
    source_batch_id: str,
    run_id: str,
    output_dir: Path,
    regime_key: str = "v2.regime_holdout",
    execution_config_path: Path | None = None,
    env_config_override: dict[str, Any] | None = None,
    # B-C-narrow Phase 2 LC-b kwargs (default None preserves backward-compat):
    artifact_dir_root: Path | None = None,
    parent_run_id_override: str | None = None,
    # B-C-narrow Phase 2 v2 per CB6: db_path threading for registry-query single-source SHA
    # (None → engine + producer both use DEFAULT_DB_PATH; tests pass tmp_path for isolation).
    db_path: Path | None = None,
) -> dict[str, Any]:
    """Evaluate a single candidate through the regime holdout AND-gate.

    Resilient: any exception is caught at the candidate boundary, recorded
    as lifecycle_state='holdout_error' with a full traceback in the
    error_message field. Continues to the next candidate.

    PHASE4 cost-config override: execution_config_path (when provided)
    threads through to run_regime_holdout -> run_backtest's
    load_execution_config(path) call. Default None preserves backward
    compat for all non-Phase-4 callers.

    PHASE4 env_config override (R2): env_config_override (when provided)
    is the runner's pre-built env_config dict with forward_2026.end
    injected at fire-time. Threads through to run_regime_holdout(
    env_config=...) bypassing the default load_environments_config()
    call. Default None preserves backward compat for non-Phase-4 callers.

    B-C-narrow Phase 2 LC-b activation: when artifact_dir_root is provided,
    producer builds 4 LC-b scalars (run_id_override + source_batch_id +
    parent_run_id_override + artifact_dir) and threads them to
    run_regime_holdout. Per CR-SE-M1 v9: producer-side moments compute +
    registry-query for path/SHA happens INSIDE the candidate-level
    try/except boundary, so failures produce `lifecycle_state='holdout_error'`
    per spec R5 contract rather than aborting the whole producer.
    """
    # B-C-narrow Phase 2 LC-b activation: derived from cohort-level artifact_dir_root.
    # When artifact_dir_root is None (legacy callers), LC-b kwargs stay None → engine
    # legacy path. When provided, build per-candidate scalars matching engine's LC-b
    # 4-kwarg contract (Phase 0 SEAL signature).
    lcb_active = artifact_dir_root is not None
    if lcb_active:
        candidate_artifact_dir = artifact_dir_root / candidate["hypothesis_hash"]
        candidate_artifact_dir.mkdir(parents=True, exist_ok=True)
        child_run_id_override = f"{run_id}_{candidate['hypothesis_hash']}"
    else:
        candidate_artifact_dir = None
        child_run_id_override = None

    started = datetime.now(timezone.utc)
    try:
        dsl = _load_dsl_from_response(
            source_batch_id, candidate["position"]
        )
        holdout_result = run_regime_holdout(
            dsl=dsl,
            batch_id=source_batch_id,
            parent_run_id=f"phase2c_eval_gate_{run_id}",
            regime_key=regime_key,
            execution_config_path=execution_config_path,
            env_config=env_config_override,
            db_path=db_path,  # CB6: thread to engine so producer's get_run uses same DB
            # B-C-narrow Phase 2 LC-b 4 kwargs (None when artifact_dir_root is None;
            # engine's single-gate lcb_active = artifact_dir is not None → no LC-b path):
            run_id_override=child_run_id_override,
            source_batch_id=source_batch_id if lcb_active else None,
            parent_run_id_override=parent_run_id_override if lcb_active else None,
            artifact_dir=candidate_artifact_dir,
        )
        # CR-SE-M1 SEAL-eve v9: B-C-narrow merge logic INSIDE try/except — failures
        # in moments compute or registry query → caught as candidate-level
        # 'holdout_error' per spec R5 contract, not whole-producer abort.
        if lcb_active:
            returns = compute_per_bar_returns(holdout_result.equity_curve)
            moments = compute_moments(returns)
            # Query engine-written child registry row for path + SHA (CB5+CB6 single-source).
            # MR2-1 PFR R2 ADOPT (v3): explicit try/finally conn.close() pattern (matches
            # M3 _finalize_batch_registry* pattern; `with get_connection(...) as conn:`
            # commits on success / rolls back on exception but does NOT close the file
            # handle on context exit per sqlite3 semantics).
            _conn = get_connection(db_path)
            try:
                child_row = get_run(_conn, child_run_id_override)
            finally:
                _conn.close()
            if child_row is None:
                raise RuntimeError(
                    f"B-C-narrow CB5+CB6: child registry row missing for "
                    f"run_id={child_run_id_override!r} after run_regime_holdout returned."
                )
            # Hold moments + path + SHA for merge into summary (applied AFTER summary built)
            _bc_narrow_fields = {
                "gamma3": moments.get("gamma3"),
                "gamma4": moments.get("gamma4"),
                "T_obs": moments.get("T_obs"),
                "returns_per_bar_path": child_row.get("returns_per_bar_path"),
                "returns_per_bar_sha256": child_row.get("returns_per_bar_sha256"),
            }
        else:
            _bc_narrow_fields = None
        lifecycle_state = (
            "holdout_passed" if holdout_result.regime_holdout_passed
            else "holdout_failed"
        )
        error_message: str | None = None
    except Exception:
        holdout_result = None
        _bc_narrow_fields = None  # candidate failure → no B-C-narrow merge
        lifecycle_state = "holdout_error"
        error_message = traceback.format_exc()
        logger.warning(
            "%s position=%d: holdout_error\n%s",
            candidate["hypothesis_hash"][:8],
            candidate["position"],
            error_message,
        )
    finished = datetime.now(timezone.utc)
    wall_clock = (finished - started).total_seconds()

    summary = _per_candidate_summary(
        candidate=candidate,
        head_sha=head_sha,
        source_batch_id=source_batch_id,
        run_id=run_id,
        regime_key=regime_key,
        holdout_result=holdout_result,
        lifecycle_state=lifecycle_state,
        error_message=error_message,
        wall_clock_seconds=wall_clock,
    )
    # CR-SE-M1 v9: merge B-C-narrow fields if captured in try block (None if
    # candidate failed → no merge; summary lacks fields → backward-compat-safe
    # per existing None-handling in _write_aggregate_csv at Step 10.7).
    if _bc_narrow_fields is not None:
        summary.update(_bc_narrow_fields)

    candidate_dir = output_dir / candidate["hypothesis_hash"]
    candidate_dir.mkdir(parents=True, exist_ok=True)
    summary_path = candidate_dir / "holdout_summary.json"
    summary_path.write_text(
        json.dumps(summary, indent=2, sort_keys=True, default=str),
        encoding="utf-8",
    )
    # Round-trip validate immediately
    with open(summary_path) as f:
        reloaded = json.load(f)
    check_evaluation_semantics_or_raise(
        reloaded, artifact_path=str(summary_path)
    )

    logger.info(
        "%s position=%d theme=%s name=%s state=%s wall=%.1fs",
        candidate["hypothesis_hash"][:8],
        candidate["position"],
        candidate["theme"],
        candidate["name"][:40],
        lifecycle_state,
        wall_clock,
    )
    return summary


# ---------------------------------------------------------------------------
# Aggregate write
# ---------------------------------------------------------------------------


_CSV_FIELDS: tuple[str, ...] = (
    "hypothesis_hash",
    "position",
    "theme",
    "name",
    "wf_test_period_sharpe",
    "lifecycle_state",
    "holdout_passed",
    "holdout_sharpe",
    "holdout_max_drawdown",
    "holdout_total_return",
    "holdout_total_trades",
    "wall_clock_seconds",
    "error_message",
    # B-C-narrow Phase 2 additions (spec §3.2.5):
    "gamma3",
    "gamma4",
    "T_obs",
    "returns_per_bar_path",
    "returns_per_bar_sha256",
)


def _write_aggregate_csv(
    summaries: list[dict[str, Any]], csv_path: Path
) -> None:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=_CSV_FIELDS)
        writer.writeheader()
        for s in summaries:
            m = s.get("holdout_metrics") or {}
            writer.writerow({
                "hypothesis_hash": s["hypothesis_hash"],
                "position": s["position"],
                "theme": s["theme"],
                "name": s["name"],
                "wf_test_period_sharpe": (
                    f"{s['wf_test_period_sharpe']:.6f}"
                ),
                "lifecycle_state": s["lifecycle_state"],
                "holdout_passed": (
                    "" if s["holdout_passed"] is None
                    else ("1" if s["holdout_passed"] else "0")
                ),
                "holdout_sharpe": (
                    f"{m['sharpe_ratio']:.6f}" if m else ""
                ),
                "holdout_max_drawdown": (
                    f"{m['max_drawdown']:.6f}" if m else ""
                ),
                "holdout_total_return": (
                    f"{m['total_return']:.6f}" if m else ""
                ),
                "holdout_total_trades": (
                    str(m["total_trades"]) if m else ""
                ),
                "wall_clock_seconds": s["wall_clock_seconds"],
                "error_message": (
                    (s.get("error_message") or "").splitlines()[-1]
                    if s.get("error_message") else ""
                ),
                # B-C-narrow Phase 2 additions (spec §3.2.5):
                "gamma3": (
                    f"{s['gamma3']:.6f}" if s.get("gamma3") is not None else ""
                ),
                "gamma4": (
                    f"{s['gamma4']:.6f}" if s.get("gamma4") is not None else ""
                ),
                "T_obs": (
                    str(s["T_obs"]) if s.get("T_obs") is not None else ""
                ),
                "returns_per_bar_path": s.get("returns_per_bar_path") or "",
                "returns_per_bar_sha256": s.get("returns_per_bar_sha256") or "",
            })


def _aggregate_summary_dict(
    summaries: list[dict[str, Any]],
    head_sha: str,
    source_batch_id: str,
    run_id: str,
    universe: str | None,
    explicit_hashes: list[str] | None,
    run_started_utc: str,
    run_finished_utc: str,
    regime_key: str = "v2.regime_holdout",
) -> dict[str, Any]:
    counts = {
        "total": len(summaries),
        "holdout_passed": sum(
            1 for s in summaries if s["lifecycle_state"] == "holdout_passed"
        ),
        "holdout_failed": sum(
            1 for s in summaries if s["lifecycle_state"] == "holdout_failed"
        ),
        "holdout_error": sum(
            1 for s in summaries if s["lifecycle_state"] == "holdout_error"
        ),
    }
    primary_summaries = [
        s for s in summaries
        if s["wf_test_period_sharpe"] > PRIMARY_THRESHOLD
    ]
    audit_only_summaries = [
        s for s in summaries
        if s["wf_test_period_sharpe"] <= PRIMARY_THRESHOLD
    ]
    primary_passed = sum(
        1 for s in primary_summaries
        if s["lifecycle_state"] == "holdout_passed"
    )
    audit_passed = sum(
        1 for s in audit_only_summaries
        if s["lifecycle_state"] == "holdout_passed"
    )
    by_theme: dict[str, dict[str, int]] = {}
    for s in summaries:
        theme = s["theme"]
        bucket = by_theme.setdefault(
            theme, {"total": 0, "holdout_passed": 0}
        )
        bucket["total"] += 1
        if s["lifecycle_state"] == "holdout_passed":
            bucket["holdout_passed"] += 1
    aggregate: dict[str, Any] = {
        "run_id": run_id,
        "source_batch_id": source_batch_id,
        "universe": universe,
        "explicit_candidate_hashes": explicit_hashes,
        "run_started_utc": run_started_utc,
        "run_finished_utc": run_finished_utc,
        "counts": counts,
        "primary_universe_holdout_passed": primary_passed,
        "primary_universe_total": len(primary_summaries),
        "audit_only_holdout_passed": audit_passed,
        "audit_only_total": len(audit_only_summaries),
        "by_theme": by_theme,
    }
    aggregate.update(_lineage_metadata(head_sha, regime_key))
    return aggregate


def _write_aggregate_summary(
    aggregate: dict[str, Any], path: Path
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(aggregate, indent=2, sort_keys=True, default=str),
        encoding="utf-8",
    )
    with open(path) as f:
        reloaded = json.load(f)
    check_evaluation_semantics_or_raise(
        reloaded, artifact_path=str(path)
    )


# ---------------------------------------------------------------------------
# CLI plumbing
# ---------------------------------------------------------------------------


def _build_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Phase 2C evaluation gate: regime holdout AND-gate against "
            "corrected Phase 2C candidates. See "
            "docs/phase2c/PHASE2C_6_EVALUATION_GATE_PLAN.md."
        ),
    )
    parser.add_argument(
        "--source-batch-id",
        type=str,
        default=DEFAULT_SOURCE_BATCH_ID,
        help=(
            "Upstream Phase 2C proposer batch UUID whose corrected "
            f"candidates are evaluated. Default: {DEFAULT_SOURCE_BATCH_ID}."
        ),
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--universe",
        type=str,
        choices=["primary", "audit"],
        default=None,
        help=(
            "primary=44 corrected winners (wf_test_period_sharpe>0.5); "
            "audit=all 198 corrected candidates."
        ),
    )
    group.add_argument(
        "--candidate-hashes",
        type=str,
        default=None,
        help=(
            "Comma-separated 8+ char hash prefixes to evaluate (each "
            "must resolve to exactly one candidate). Mutually exclusive "
            "with --universe."
        ),
    )
    parser.add_argument(
        "--run-id",
        type=str,
        default=None,
        help=(
            "Identifier for THIS evaluation-gate output run. Examples: "
            "'smoke_v1' for smoke runs, auto-generated UUID4 for full "
            "runs. Distinct from --source-batch-id."
        ),
    )
    parser.add_argument(
        "--regime",
        "--regime-key",
        type=str,
        dest="regime_key",
        # FUTURE-DEPRECATION: the "v2.regime_holdout" default preserves
        # PHASE2C_6 reproducibility (2022 single-regime evaluation).
        # Once multi-regime callers are the production norm, this default
        # is a candidate for removal so callers must be explicit about
        # regime identity. Remove only when no implicit-default callers
        # remain. (Engine-side mirror at backtest/engine.py
        # run_regime_holdout signature.)
        default="v2.regime_holdout",
        help=(
            "Regime to evaluate against (PHASE2C_7.1 §6; PHASE2C_8.1 §6 "
            "extended; PHASE4 forward-test §1.2). Default: v2.regime_holdout "
            "(2022 bear regime, PHASE2C_6 backward-compat). Use v2.validation "
            "for the PHASE2C_7.1 2024 arc; evaluation_regimes.eval_2020_v1 "
            "or evaluation_regimes.eval_2021_v1 for the PHASE2C_8.1 novel "
            "regimes; evaluation_regimes.forward_2026 for the PHASE4 forward-"
            "test [2026-01-01, T_end] of PHASE2C_15 cohort_a candidates. "
            "--regime is the canonical PHASE2C_8.1 flag name; --regime-key "
            "is preserved as an alias for backward-compat. Must be a key in "
            "REGIME_KEY_LABEL_MAPPING; unknown values are rejected at "
            "startup before any backtest spend."
        ),
    )
    parser.add_argument(
        "--output-root",
        type=str,
        default=str(DEFAULT_OUTPUT_ROOT),
        help=f"Output root. Default: {DEFAULT_OUTPUT_ROOT}.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help=(
            "Print resolved configuration + candidate selection and "
            "exit before any backtest. Lineage guard IS still invoked."
        ),
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help=(
            "Allow overwriting an existing non-empty <output-root>/<run-id>/"
            " directory. Without --force, the script refuses to overwrite."
        ),
    )
    parser.add_argument(
        "--execution-config",
        type=Path,
        default=None,
        help=(
            "Path to alternate execution.yaml (PHASE4 cost parameterization). "
            "Default: config/execution.yaml. PHASE4 forward-test uses one of: "
            "config/execution_phase4_07bps.yaml | _13bps | _15bps | _17bps. "
            "When provided, the runner threads the path through "
            "run_regime_holdout to override the cost model + logs "
            "execution_config_path + execution_config_sha256 into the "
            "aggregate holdout_summary.json for self-auditing artifacts."
        ),
    )
    # B-C-narrow Phase 2 recovery flags (spec §3.2.3 + §3.2.4; R9-B-guarded lock).
    parser.add_argument(
        "--enable-b-c-narrow-recovery",
        action="store_true",
        default=False,
        help=(
            "Enable B-C-narrow data-recovery flow (3 NEW behaviors): "
            "(1) PRE-flight archive of canonical phase4_forward_2026_15bps_v1/ "
            "to archive/phase4_forward_2026_15bps_v1_d0b8101/ via shutil.move "
            "(refuse-if-exists); (2) PRE-flight parent_run_id idempotency guard "
            "(refuse-if-exists in registry); (3) POST-fire _finalize_batch_registry "
            "writes the parent batch_summary row (children written by engine "
            "per-candidate inside run_regime_holdout). Default False preserves "
            "backward-compat for legacy callers (PHASE2C_15, PHASE2C_8.1, etc.)."
        ),
    )
    parser.add_argument(
        "--force-rerun-existing",
        action="store_true",
        default=False,
        help=(
            "When --enable-b-c-narrow-recovery is set AND parent_run_id already "
            "exists in registry, DELETE all rows WHERE parent_run_id = ... AND "
            "the parent row itself before re-fire. Operator-confirmed clean state "
            "discipline per R9-B-guarded lock. Default False (refuse-if-exists; "
            "manual cleanup required). MUTUALLY EXCLUSIVE with --dry-run per "
            "CR5-B1 PFR R5 ADOPT (v6) — combination rejected at argparse "
            "(operator must consciously choose intent-validation vs destructive cleanup)."
        ),
    )
    return parser


def _resolve_run_id(args: argparse.Namespace) -> str:
    return args.run_id or str(uuid.uuid4())


def _check_overwrite_protection(
    run_dir: Path, force: bool
) -> int | None:
    if not run_dir.exists():
        return None
    try:
        non_empty = any(run_dir.iterdir())
    except OSError:
        non_empty = True
    if non_empty and not force:
        print(
            f"\nERROR: run directory {run_dir} already exists and is "
            f"non-empty. Re-run with --force to overwrite, or pass a "
            f"different --run-id.",
            file=sys.stderr,
        )
        return 1
    return None


def _validate_b_c_narrow_recovery_identity_or_raise(
    run_id: str,
    regime_key: str,
    execution_config_path: Path | None,
    source_batch_id: str,
) -> None:
    """B-C-narrow Phase 2 (CB2 PFR R1 ADOPT): identity guard for recovery flow.

    When --enable-b-c-narrow-recovery is set, this guard validates 4 cohort
    identity fields against locked constants BEFORE any mutation (archive,
    DB write). Fail-fast with explicit per-field rationale.

    Required values (locked at scripts module-level BCNARROW_* constants):
    - run_id == BCNARROW_PARENT_RUN_ID
    - regime_key == BCNARROW_REGIME_KEY
    - execution_config_path canonicalizes to BCNARROW_EXECUTION_CONFIG_PATH
    - source_batch_id == BCNARROW_SOURCE_BATCH_ID

    Order in recovery PRE-flight chain (per CB1 lock + CR-SE-H1 v9 reorder):
    1. W0 — This guard (read-only)
    2. W1a — _finalize_batch_registry_preflight_or_raise (read-only) when
       NOT --force-rerun-existing
    3. (existing) _check_overwrite_protection
    4. W1b — _finalize_batch_registry_preflight_or_raise (DESTRUCTIVE) when
       --force-rerun-existing
    5. (existing) dry-run exit if args.dry_run
    6. W3 — _archive_canonical_pre_flight (destructive — first FS mutation)

    Raises:
        ValueError: with multi-line explicit message listing every wrong field
            and the required value. Operator runs producer with corrected flags.
    """
    errors: list[str] = []
    if run_id != BCNARROW_PARENT_RUN_ID:
        errors.append(
            f"--run-id={run_id!r} must equal {BCNARROW_PARENT_RUN_ID!r} "
            f"(B-C-narrow cohort lock per spec §2 Q4)"
        )
    if regime_key != BCNARROW_REGIME_KEY:
        errors.append(
            f"--regime-key={regime_key!r} must equal {BCNARROW_REGIME_KEY!r} "
            f"(B-C-narrow cohort_a is forward_2026 per spec §1)"
        )
    if execution_config_path is None:
        errors.append(
            f"--execution-config must be {BCNARROW_EXECUTION_CONFIG_PATH!r} "
            f"(cost anchor lock per spec §2 Q5); got None"
        )
    else:
        # Canonicalize: resolve absolute path then take repo-relative form.
        ec_path_obj = Path(execution_config_path).resolve()
        try:
            ec_path_repo_rel = str(ec_path_obj.relative_to(PROJECT_ROOT))
        except ValueError:
            # Path is outside repo root — keep as absolute for the error message
            ec_path_repo_rel = str(ec_path_obj)
        if ec_path_repo_rel != BCNARROW_EXECUTION_CONFIG_PATH:
            errors.append(
                f"--execution-config={ec_path_repo_rel!r} must equal "
                f"{BCNARROW_EXECUTION_CONFIG_PATH!r} (cost anchor lock per spec §2 Q5)"
            )
    if source_batch_id != BCNARROW_SOURCE_BATCH_ID:
        errors.append(
            f"--source-batch-id={source_batch_id!r} must equal "
            f"{BCNARROW_SOURCE_BATCH_ID!r} (combined synthetic dir per "
            f"spec §1 + Phase 1 G3 inventory)"
        )
    if errors:
        raise ValueError(
            "B-C-narrow recovery identity guard (CB2 PFR R1 ADOPT): refusing to "
            "mutate state due to inconsistent cohort identity. The "
            "--enable-b-c-narrow-recovery flag locks the recovery flow to the "
            "specific cohort_a artifact at "
            f"data/phase2c_evaluation_gate/{BCNARROW_ARCHIVE_BASENAME}/ "
            "(per spec §1 + §2 + §3.2.3). All 4 identity fields must match:\n"
            "  - " + "\n  - ".join(errors)
        )


def _archive_canonical_pre_flight(
    canonical_path: Path,
    archive_root: Path,
    archive_basename: str,
) -> None:
    """B-C-narrow Phase 2: PRE-flight archive of canonical artifact dir before recovery fire.

    Per spec §3.2.4 + BLOCKING-1 R9 PRE-flight split:
    - Check archive_root exists; create if absent.
    - Check archive_root / archive_basename does NOT exist (refuse-if-exists per G7).
    - shutil.move canonical_path → archive_root / archive_basename.
    - Verify post-move: canonical_path vacated; archive target populated.

    Args:
        canonical_path: e.g., data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1/
        archive_root:   e.g., data/phase2c_evaluation_gate/archive/
        archive_basename: e.g., "phase4_forward_2026_15bps_v1_d0b8101" (uses original current_git_sha)

    Raises:
        FileNotFoundError: if canonical_path does not exist (nothing to archive).
        FileExistsError: if archive_root / archive_basename already exists
            (operator manual cleanup required per R10 §4.3 G7 strict refuse).
        NotImplementedError: if canonical_path and archive_root are on DIFFERENT
            filesystems (st_dev mismatch); shutil.move falls back to non-atomic
            copy+delete on cross-FS (AR-SE-R2-M3 v10 defensive guard).
    """
    if not canonical_path.exists():
        raise FileNotFoundError(
            f"B-C-narrow archive PRE-flight: canonical path {canonical_path} does not exist. "
            f"Nothing to archive. (Did Phase 3 already run? Or canonical never present?)"
        )
    archive_root.mkdir(parents=True, exist_ok=True)
    # AR-SE-R2-M3 SEAL-eve R2 ADOPT v10 + CR-SE-R3-M2 v11 reconciliation: same-FS
    # pre-check before shutil.move. shutil.move is atomic via os.rename ONLY when
    # source + target are on the same filesystem; falls back to copy + delete on
    # cross-FS, which is NOT atomic. Project's data/phase2c_evaluation_gate/ and
    # sibling data/phase2c_evaluation_gate/archive/ are same-FS by construction
    # (sibling dirs under common parent). v11 uses archive_root.resolve().stat()
    # (NOT .parent.stat()) because destination = archive_root + archive_basename
    # lives WITHIN archive_root; source-destination same-FS check is what
    # shutil.move actually needs. Defensive check guards against operator
    # misconfiguring --output-root to different mount point.
    if canonical_path.stat().st_dev != archive_root.resolve().stat().st_dev:
        raise NotImplementedError(
            f"B-C-narrow archive PRE-flight (AR-SE-R2-M3 v10 cross-FS guard): "
            f"canonical_path {canonical_path} and archive_root {archive_root} are on "
            f"DIFFERENT filesystems (st_dev mismatch). shutil.move falls back to "
            f"non-atomic copy+delete on cross-FS, exposing partial-move failure mode. "
            f"This project's archive convention assumes same-FS (sibling dirs under "
            f"common parent). Operator must ensure --output-root targets same FS as "
            f"the canonical artifact, OR raise spec-amend register for cross-FS support."
        )
    archive_target = archive_root / archive_basename
    if archive_target.exists():
        raise FileExistsError(
            f"B-C-narrow archive PRE-flight: archive target {archive_target} already exists. "
            f"Refusing to overwrite (G7 §4.3 strict). Operator must manually cleanup the "
            f"stale archive (e.g., from a prior aborted attempt) before re-fire. "
            f"Recommended: inspect {archive_target} content before deletion."
        )
    shutil.move(str(canonical_path), str(archive_target))
    if canonical_path.exists():
        raise RuntimeError(
            f"B-C-narrow archive PRE-flight: shutil.move did not vacate canonical_path "
            f"{canonical_path}. Possible cross-filesystem partial move failure."
        )
    if not archive_target.exists():
        raise RuntimeError(
            f"B-C-narrow archive PRE-flight: shutil.move did not populate archive_target "
            f"{archive_target}."
        )


def _finalize_batch_registry_preflight_or_raise(
    parent_run_id: str,
    force_rerun_existing: bool,
    db_path: Path | None = None,
) -> None:
    """B-C-narrow Phase 2: PRE-flight idempotency guard for parent_run_id (R9-B-guarded).

    Per spec §3.2.3 + BLOCKING-1 R9 PRE-flight split + CR2-B2 v3 + CR4-B1 v5 fix:

    TRULY read-only on read path — does NOT call create_table. The function is
    expected to fire BEFORE the existing dry-run exit (per CB1 ordering); a
    create_table call here would commit DDL (CREATE TABLE IF NOT EXISTS + ALTER
    TABLE migrations per experiment_registry.py:207-219), violating the
    "read-only PRE-flight check before dry-run exit" invariant. The 3-path
    early-exit logic uses sqlite_master read-only detection:

    - Path 1 (DB file absent): treat as clean state; return immediately (no I/O).
    - Path 2 (DB present but runs table absent): treat as clean state; return
      (sqlite_master SELECT is purely read-only).
    - Path 3 (runs table present): query parent + child row counts WITHOUT
      calling create_table.
      - If no rows present: clean state; return.
      - If rows present AND force_rerun_existing=False: raise RuntimeError (refuse).
      - If rows present AND force_rerun_existing=True: DELETE all matching rows
        (children + parent) inside a `with conn:` transaction (commits on success;
        rolls back on exception).

    create_table runs ONLY in POST-fire _finalize_batch_registry (which runs AFTER
    dry-run exit per CB1 wiring), so production write path still ensures table
    existence — just not on the preflight read path.

    LR3-3 PFR R3 ADOPT (v4) DEFENSIVE NOTE: Path 3 assumes runs table has
    parent_run_id + run_id columns. True for any DB created via create_table
    (see parent_run_id row in CREATE_TABLE_SQL at experiment_registry.py:58 +
    parent_run_id row in MIGRATION_COLUMNS at :124 + run_id TEXT PRIMARY KEY
    at :56). Theoretical edge case: pre-Phase-1A legacy DB without parent_run_id
    column would raise OperationalError on COUNT query — NO such DB exists in
    this project; defensive note only.

    Args:
        parent_run_id: cohort parent run_id (e.g., "phase4_forward_2026_15bps_v1_b_c_narrow").
        force_rerun_existing: operator opt-in to DELETE pre-existing rows.
        db_path: SQLite registry path. Default None → get_connection's default
            (typically backtest/experiments.db). Default-None co-locates the
            parent row with engine-written children (engine calls get_connection
            with the same default inside _write_to_registry).

    Raises:
        RuntimeError: if pre-existing rows found AND force_rerun_existing=False.
    """
    effective_db_path = db_path if db_path is not None else DEFAULT_DB_PATH

    # Path 1: DB file absent → clean state (no file I/O at all).
    if not effective_db_path.exists():
        return

    # M3 PFR R1 fix: explicit try/finally conn.close() pattern; `with conn:` commits
    # on success / rolls back on exception but does NOT close the file handle.
    conn = get_connection(effective_db_path)
    try:
        # Path 2: DB present but runs table absent → clean state.
        # Use sqlite_master read-only query to detect — does NOT trigger CREATE TABLE.
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='runs'"
        )
        if cursor.fetchone() is None:
            # runs table does not exist; no prior rows possible → clean state.
            return

        # Path 3: runs table present → query counts (read-only) + raise/DELETE.
        with conn:
            n_children = conn.execute(
                "SELECT COUNT(*) FROM runs WHERE parent_run_id = ?", (parent_run_id,)
            ).fetchone()[0]
            n_parent = conn.execute(
                "SELECT COUNT(*) FROM runs WHERE run_id = ?", (parent_run_id,)
            ).fetchone()[0]
            if n_children == 0 and n_parent == 0:
                return  # clean state; proceed
            if not force_rerun_existing:
                raise RuntimeError(
                    f"B-C-narrow finalize PRE-flight: parent_run_id {parent_run_id!r} "
                    f"already exists in registry ({n_parent} parent row, {n_children} "
                    f"child rows). Refusing to re-fire without --force-rerun-existing "
                    f"flag (R9-B-guarded lock). Operator must either (a) inspect "
                    f"+ accept pre-existing state, OR (b) re-run with --force-rerun-existing "
                    f"to DELETE rows and re-fire from clean state."
                )
            # force_rerun_existing=True: DELETE children + parent (single transaction via `with conn:`)
            conn.execute("DELETE FROM runs WHERE parent_run_id = ?", (parent_run_id,))
            conn.execute("DELETE FROM runs WHERE run_id = ?", (parent_run_id,))
    finally:
        conn.close()


def _finalize_batch_registry(
    parent_run_id: str,
    cohort_metadata: dict[str, Any],
    db_path: Path | None = None,
) -> None:
    """B-C-narrow Phase 2: POST-fire parent batch_summary row write (R9 POST-fire half).

    Per spec §3.2.3 + PFR R1 v2 ADOPT (CB3 + CB4 + L3) + LR4-5 v5 contrast:

    DISTINCT FROM PREFLIGHT: POST-fire DOES call create_table(conn) before insert
    (BLOCKING-3 fix), guaranteeing the runs table exists. The companion preflight
    function `_finalize_batch_registry_preflight_or_raise` is TRULY read-only and
    does NOT call create_table (per CR2-B2 v3) — POST-fire runs AFTER dry-run
    exit so create_table mutation here is acceptable. Twin functions; opposite
    create_table behavior; differentiated docstrings.

    - Open db via get_connection(db_path); call create_table(conn) — ensures
      runs table exists (BLOCKING-3 fix); committed DDL is fine here because
      POST-fire path is past the dry-run gate per CB1 wiring.
    - Build parent row dict with cohort-level fields populated + per-candidate
      metric fields NULL.
    - CB4: parent.git_commit = CORRECTED_WF_ENGINE_COMMIT ("eb1c87f") matching
      engine's OVERRIDE pattern at engine.py:1328-1348 (lc.engine_commit OVERRIDE-writes
      to runs.git_commit column). cohort_metadata["current_git_sha"] populates the
      separate current_git_sha column (fire-time HEAD).
    - CB4 forensic: engine_commit ALSO written to `notes` JSON for explicit
      recoverability (registry has no engine_commit column per
      experiment_registry.py:54-103).
    - insert_run(conn, parent_row_dict).

    Child rows (one per evaluated candidate) are written by engine inside
    run_regime_holdout's _write_to_registry call (Phase 0 sequencing per
    spec §3.1.2). This function writes ONLY the 1 parent row.

    Args:
        parent_run_id: e.g., BCNARROW_PARENT_RUN_ID
            ("phase4_forward_2026_15bps_v1_b_c_narrow").
        cohort_metadata: dict with required keys (CB3 PFR R1 lock):
            execution_config_path, execution_config_sha256, parquet_data_sha256,
            regime_key, cost_anchor_id, current_git_sha, effective_start,
            initial_capital, fee_model. initial_capital MUST equal engine's
            cash default (10_000.0 per engine.py:2324); fee_model MUST be
            derived via ConstantSlippage.from_config(...).fee_model_label
            (per slippage.py:94-100; matches child rows' fee_model via engine.py:1278).
        db_path: SQLite registry path. Default None → get_connection's default
            (DEFAULT_DB_PATH = backtest/experiments.db per experiment_registry.py:46).
            Default-None co-locates the parent row with engine-written children
            (engine uses same default inside _write_to_registry).
    """
    required_keys = {
        "execution_config_path", "execution_config_sha256", "parquet_data_sha256",
        "regime_key", "cost_anchor_id", "current_git_sha", "effective_start",
        "initial_capital", "fee_model",
    }
    missing = required_keys - set(cohort_metadata.keys())
    if missing:
        raise ValueError(
            f"B-C-narrow _finalize_batch_registry: cohort_metadata missing required "
            f"keys: {sorted(missing)}. Required: {sorted(required_keys)}."
        )

    # CB4 PFR R1: parent_row notes JSON includes engine_commit for explicit
    # forensic recoverability. Registry has no engine_commit column; the
    # value is OVERRIDE-stamped into git_commit column (mirrors engine pattern).
    notes_payload = {
        "engine_commit": CORRECTED_WF_ENGINE_COMMIT,
        "cohort": "b_c_narrow_recovery",
        "spec_reference": "docs/superpowers/specs/2026-05-26-b-c-narrow-data-recovery-design.md (sealed at d6c7fc0)",
    }

    parent_row = {
        "run_id": parent_run_id,
        "run_type": "batch_summary",
        "parent_run_id": None,
        "strategy_name": "cohort_summary",
        "strategy_source": "b_c_narrow_recovery",
        # CB4 PFR R1: git_commit = engine_commit (matches engine OVERRIDE at engine.py:1328-1348).
        # current_git_sha is the separate fire-time HEAD per spec §2 disambiguation table.
        "git_commit": CORRECTED_WF_ENGINE_COMMIT,
        "created_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "effective_start": cohort_metadata["effective_start"],
        "initial_capital": cohort_metadata["initial_capital"],
        "fee_model": cohort_metadata["fee_model"],
        "execution_config_path": cohort_metadata["execution_config_path"],
        "execution_config_sha256": cohort_metadata["execution_config_sha256"],
        "parquet_data_sha256": cohort_metadata["parquet_data_sha256"],
        "regime_key": cohort_metadata["regime_key"],
        "cost_anchor_id": cohort_metadata["cost_anchor_id"],
        "current_git_sha": cohort_metadata["current_git_sha"],
        "notes": json.dumps(notes_payload),
        # Per-candidate metric fields NULL at parent (spec §3.2.3):
        "sharpe_ratio": None,
        "max_drawdown": None,
        "total_return": None,
        "total_trades": None,
        "hypothesis_hash": None,
        "returns_per_bar_path": None,
        "returns_per_bar_sha256": None,
        "T_obs": None,
        # batch_id = parent_run_id per spec §3.2.3 line 117 EXPLICIT LOCK.
        # PFR R1 PUSHBACK (Advisor HIGH-5): plan follows spec verbatim; if downstream
        # Tier 6 queries are confused by parent.batch_id ≠ children.batch_id, that is a
        # spec-level discussion at separate Charlie register, NOT a Phase 2 plan fix.
        "batch_id": parent_run_id,
    }
    # M3 PFR R1 fix: explicit try/finally conn.close() pattern.
    conn = get_connection(db_path)
    try:
        with conn:
            create_table(conn)  # BLOCKING-3: ensure runs table exists before insert
            insert_run(conn, parent_row)
    finally:
        conn.close()


def main() -> int:
    """Entry point.

    Order of operations:
      1. parse_args (so --help works without git).
      2. enforce_corrected_engine_lineage (before any engine run / write).
      3. Load corrected CSV, resolve candidate universe.
      4. Overwrite-protection gate.
      5. (--dry-run) print resolved config and exit.
      6. Per-candidate runs (each writes artifact + round-trip validates).
      7. Aggregate write + round-trip validation.
    """
    logging.basicConfig(
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%SZ",
        level=logging.INFO,
    )
    args = _build_argparser().parse_args()

    # CR5-B1 PFR R5 ADOPT (v6): reject --dry-run + --force-rerun-existing combination.
    # W1 preflight runs BEFORE dry-run exit (per CB1 v3 ordering) and DELETEs registry
    # rows when force_rerun_existing=True; combining with --dry-run would mutate state
    # BEFORE the dry-run exit, violating CB1 read-only invariant. Operator must consciously
    # choose intent-validation (dry-run) vs destructive cleanup (force-rerun-existing).
    if args.dry_run and args.force_rerun_existing:
        parser = _build_argparser()
        parser.error(
            "--dry-run and --force-rerun-existing are MUTUALLY EXCLUSIVE "
            "(CR5-B1 PFR R5 ADOPT v6). Combining them would DELETE registry rows "
            "BEFORE dry-run exits — violating the CB1 read-only invariant. "
            "Choose ONE: --dry-run (intent-validation, no mutation) OR "
            "--force-rerun-existing (destructive cleanup of prior partial state)."
        )

    if args.universe is None and args.candidate_hashes is None:
        print(
            "ERROR: one of --universe or --candidate-hashes is required.",
            file=sys.stderr,
        )
        return 2

    # Reject unknown --regime-key BEFORE the lineage guard so a typo
    # doesn't trigger the heavier git checks before failing.
    if args.regime_key not in REGIME_KEY_LABEL_MAPPING:
        print(
            f"ERROR: --regime-key={args.regime_key!r} is not in "
            f"REGIME_KEY_LABEL_MAPPING. Known regimes: "
            f"{sorted(REGIME_KEY_LABEL_MAPPING)}. Update "
            f"backtest/wf_lineage.py:REGIME_KEY_LABEL_MAPPING if "
            f"introducing a new regime.",
            file=sys.stderr,
        )
        return 2

    head_sha = enforce_corrected_engine_lineage()

    # B-C-narrow Phase 2 (v2 PFR R1 ADOPT + v9 CR-SE-H1 REORDER) — read-only
    # PRE-flight chain gated by --enable-b-c-narrow-recovery. Per CB1 lock +
    # CR-SE-H1: identity guard (W0) + idempotency READ-ONLY check (W1a) fire
    # BEFORE existing _check_overwrite_protection (which is read-only refusal
    # on non-empty run_dir without --force). W1b destructive DELETE moves
    # AFTER _check_overwrite_protection per CR-SE-H1 to eliminate state-
    # inconsistency window (DB cleaned + FS dirty if --force-rerun-existing
    # without --force on non-empty run_dir).
    bcnarrow_proposed_run_id: str | None = None
    if args.enable_b_c_narrow_recovery:
        # W0 — CB2: identity guard validates 4 cohort identity fields
        # (run_id, regime_key, execution_config, source_batch_id) against
        # BCNARROW_* constants. Raises ValueError BEFORE any mutation if any
        # field mismatches. Operator misuse caught fast.
        # NOTE: --run-id arg is needed for the identity check; _resolve_run_id
        # is the lookup helper. If --run-id absent, _resolve_run_id mints a
        # UUID4 — identity guard catches that as wrong run_id.
        bcnarrow_proposed_run_id = _resolve_run_id(args)
        _validate_b_c_narrow_recovery_identity_or_raise(
            run_id=bcnarrow_proposed_run_id,
            regime_key=args.regime_key,
            execution_config_path=args.execution_config,
            source_batch_id=args.source_batch_id,
        )
        # W1a (CR-SE-H1 v9; AR-SE-R2-L2 v10 style fix): READ-ONLY idempotency check ONLY.
        # Always pass force_rerun_existing=False here regardless of operator's actual
        # flag value — the destructive DELETE is deferred to W1b which runs AFTER
        # _check_overwrite_protection. W1a's role: refuse fast if parent_run_id pre-
        # exists AND operator did NOT pass --force-rerun-existing. If operator DID
        # pass --force-rerun-existing, skip W1a refusal check (operator has explicitly
        # authorized DELETE; W1b will handle it). If operator did NOT pass --force-
        # rerun-existing AND parent exists, W1a raises RuntimeError below and we never
        # reach _check_overwrite_protection.
        # AR-SE-R2-L2 v10 SEAL-eve R2 ADOPT: replaced ternary-expression-as-statement
        # form with explicit if/else for readability — prior `func(...) if cond else None`
        # pattern was readability-fragile.
        if not args.force_rerun_existing:
            _finalize_batch_registry_preflight_or_raise(
                parent_run_id=bcnarrow_proposed_run_id,
                force_rerun_existing=False,  # W1a is read-only-detection only
                db_path=None,
            )
        # else: operator authorized DELETE via --force-rerun-existing; skip W1a
        # refusal check; W1b below will handle the DELETE.

    all_candidates = _load_corrected_candidates(args.source_batch_id)
    selected = _resolve_candidate_universe(args, all_candidates)
    # Item 1 polish (T10 Bundle a, Charlie register #N+16): in the B-C-narrow
    # recovery path reuse the same run_id minted at W0 (line 1471) so preflight
    # and execute share one UUID. In the legacy non-recovery path call
    # _resolve_run_id(args) as before — behavior unchanged. This makes UUID4
    # divergence between preflight and execute structurally impossible regardless
    # of the W0 identity-guard catch.
    run_id = (
        bcnarrow_proposed_run_id
        if args.enable_b_c_narrow_recovery
        else _resolve_run_id(args)
    )
    run_dir = Path(args.output_root).resolve() / run_id

    explicit_hashes = (
        [c.strip() for c in args.candidate_hashes.split(",") if c.strip()]
        if args.candidate_hashes else None
    )

    print(f"[Phase 2C eval gate] run_id: {run_id}")
    print(f"[Phase 2C eval gate] source_batch_id: {args.source_batch_id}")
    print(f"[Phase 2C eval gate] head_sha: {head_sha}")
    print(f"[Phase 2C eval gate] universe: {args.universe}")
    print(f"[Phase 2C eval gate] explicit_hashes: {explicit_hashes}")
    print(f"[Phase 2C eval gate] candidates_to_run: {len(selected)}")
    print(f"[Phase 2C eval gate] output_dir: {run_dir}")
    print(
        f"[Phase 2C eval gate] regime_key: {args.regime_key} "
        f"(label={REGIME_KEY_LABEL_MAPPING[args.regime_key]})"
    )
    print(f"[Phase 2C eval gate] dry_run: {args.dry_run}")
    print(f"[Phase 2C eval gate] force: {args.force}")

    rc = _check_overwrite_protection(run_dir, args.force)
    if rc is not None:
        return rc

    # W1b (CR-SE-H1 v9): destructive DELETE — runs ONLY when --force-rerun-existing
    # is set AND we've passed the read-only refusal gates (identity guard W0 + W1a
    # idempotency-detect + _check_overwrite_protection). If any prior gate would
    # have refused the request, W1b never executes — no DB mutation occurs.
    # Eliminates Codex SEAL-eve BLOCKING-2 state-inconsistency window where
    # --force-rerun-existing without --force on non-empty run_dir would DELETE
    # registry rows then abort at overwrite gate.
    if args.enable_b_c_narrow_recovery and args.force_rerun_existing:
        _finalize_batch_registry_preflight_or_raise(
            parent_run_id=bcnarrow_proposed_run_id,
            force_rerun_existing=True,  # actual DELETE branch
            db_path=None,
        )

    if args.dry_run:
        print("\n[Phase 2C eval gate] --dry-run: stopping before backtests.")
        for c in selected[:10]:
            print(
                f"  would evaluate: {c['hypothesis_hash'][:8]} "
                f"position={c['position']} theme={c['theme']} "
                f"name={c['name'][:40]} "
                f"wf_sharpe={c['wf_test_period_sharpe']:+.4f}"
            )
        if len(selected) > 10:
            print(f"  ... and {len(selected) - 10} more")
        return 0

    run_dir.mkdir(parents=True, exist_ok=True)
    run_started_utc = _utc_now_iso()

    # B-C-narrow Phase 2 (v2 per CB1 PFR R1 ADOPT) — DESTRUCTIVE archive.
    # Runs AFTER dry-run exit (W2 preserved); operator confirmed by reaching here.
    # Per CB1: archive is LAST step of PRE-flight chain so that any earlier
    # read-only refusal (identity guard W0, idempotency check W1a/W1b, dry-run W2)
    # leaves the canonical artifact in place.
    if args.enable_b_c_narrow_recovery:
        # CR-SE-R3-M1 SEAL-eve R3 ADOPT v11: USE BCNARROW_CANONICAL_BASENAME constant
        # (defined at module-level per AR-SE-R2-M4 v10) instead of hardcoded literal.
        # Closes 8th-cycle CR3-B1 template-vs-inline recurrence — v10 defined constant
        # but didn't rewrite W3 consumer site; v11 closes the consumer-site gap.
        canonical_phase4_path = Path(args.output_root).resolve() / BCNARROW_CANONICAL_BASENAME
        archive_root = Path(args.output_root).resolve() / "archive"
        _archive_canonical_pre_flight(
            canonical_path=canonical_phase4_path,
            archive_root=archive_root,
            archive_basename=BCNARROW_ARCHIVE_BASENAME,  # M5 PFR R1: named constant
        )

    # PHASE4 R2: capture forward_window_metadata + build env_config override
    # at fire-time when regime is forward_2026. Done ONCE before iterating
    # candidates so the same captured T_end applies to all candidates in
    # this run. Per PHASE4_PLAN §1.2 + Task 2 SEAL invariant + advisor R2
    # adjudication 2026-05-09 (runner-side override; no engine code change).
    forward_window_metadata: dict[str, Any] | None = None
    env_config_override: dict[str, Any] | None = None
    if args.regime_key == PHASE4_FORWARD_2026_REGIME_KEY:
        forward_window_metadata = _capture_phase4_forward_window_metadata()
        env_config_override = _build_phase4_env_config_override(
            forward_window_metadata
        )
        logger.info(
            "[Phase 4] forward_window_metadata captured: "
            "start=%s end=%s bar_count=%d parquet_sha256=%s...",
            forward_window_metadata["forward_window_start_utc"],
            forward_window_metadata["forward_window_end_utc"],
            forward_window_metadata["forward_bar_count"],
            forward_window_metadata["parquet_data_sha256"][:12],
        )
        logger.info(
            "[Phase 4] env_config override: "
            "evaluation_regimes.forward_2026.end injected as %r",
            forward_window_metadata["forward_end_date_iso"],
        )

    summaries: list[dict[str, Any]] = []
    for i, candidate in enumerate(selected, start=1):
        logger.info(
            "[%d/%d] evaluating %s ...",
            i, len(selected), candidate["hypothesis_hash"][:8],
        )
        s = _evaluate_one_candidate(
            candidate=candidate,
            head_sha=head_sha,
            source_batch_id=args.source_batch_id,
            run_id=run_id,
            output_dir=run_dir,
            regime_key=args.regime_key,
            execution_config_path=args.execution_config,
            env_config_override=env_config_override,
            # B-C-narrow Phase 2 LC-b kwargs (None on legacy callers preserves backward-compat):
            artifact_dir_root=(run_dir if args.enable_b_c_narrow_recovery else None),
            parent_run_id_override=(run_id if args.enable_b_c_narrow_recovery else None),
            # CB6 v2 PFR R1: db_path threading for registry-query single-source SHA.
            # None → producer + engine both use DEFAULT_DB_PATH (co-located).
            db_path=None,
        )
        summaries.append(s)

    run_finished_utc = _utc_now_iso()

    # Per-row CSV
    _write_aggregate_csv(summaries, run_dir / "holdout_results.csv")

    # Aggregate summary JSON
    aggregate = _aggregate_summary_dict(
        summaries=summaries,
        head_sha=head_sha,
        source_batch_id=args.source_batch_id,
        run_id=run_id,
        universe=args.universe,
        explicit_hashes=explicit_hashes,
        run_started_utc=run_started_utc,
        run_finished_utc=run_finished_utc,
        regime_key=args.regime_key,
    )

    # PHASE4 self-auditing artifact metadata: log the execution config path
    # + sha256 so artifacts are self-auditing (anyone reading the summary
    # can verify which cost config produced this run without inferring
    # from run-id naming). Per Q2 refinement at Phase 4 implementation
    # arc Task 3 (sealed PHASE4_PLAN.md §1.4 cost configurations).
    #
    # Item 2 polish (T10 Bundle a, Charlie register #N+16): load
    # the execution config ONCE here and reuse `_exec_cfg` at the
    # POST-fire B-C-narrow finalize block below (was a second
    # `load_execution_config(args.execution_config)` call → duplicate
    # file read + YAML parse on the same config). The byte payload
    # is also reused for sha256 hashing in both metadata sites.
    import hashlib
    _exec_cfg_path = (
        args.execution_config
        if args.execution_config is not None
        else PROJECT_ROOT / "config" / "execution.yaml"
    )
    _exec_cfg_path_resolved = _exec_cfg_path.resolve()
    _exec_cfg_bytes = _exec_cfg_path_resolved.read_bytes()
    # Pass the resolved path (handles `args.execution_config is None`
    # default → config/execution.yaml) so this call is correct for both
    # the legacy path and the B-C-narrow recovery path. Original site
    # at the POST-fire block passed args.execution_config directly, which
    # was safe only because CB2 identity guard ensured it was non-None
    # in the recovery branch.
    _exec_cfg = load_execution_config(_exec_cfg_path_resolved)
    try:
        _exec_cfg_path_relative = str(
            _exec_cfg_path_resolved.relative_to(PROJECT_ROOT)
        )
    except ValueError:
        # Path outside project root — keep absolute for traceability.
        _exec_cfg_path_relative = str(_exec_cfg_path_resolved)
    aggregate["execution_config_path"] = _exec_cfg_path_relative
    aggregate["execution_config_sha256"] = hashlib.sha256(
        _exec_cfg_bytes
    ).hexdigest()

    # PHASE4 forward_window_metadata block (per Q4 refinement at Task 3
    # planning + advisor R2 implementation 2026-05-09). Embed the
    # fire-time captured T_end + parquet sha256 + bar count so the
    # artifact is self-auditing without inferring from run-id naming.
    # Only emitted for forward_2026 regime; absent for all other regimes
    # (preserves backward compat for PHASE2C_6/7.1/8.1/15 artifacts).
    # Cross-artifact consistency tests at Task 4 Step 7 verify same
    # window/bars/parquet hash across the 4 cost-run artifacts.
    if forward_window_metadata is not None:
        # Strip the date-only convenience field; that's a runner-internal
        # helper for env_config injection, not artifact metadata.
        artifact_fwm = {
            k: v for k, v in forward_window_metadata.items()
            if k != "forward_end_date_iso"
        }
        aggregate["forward_window_metadata"] = artifact_fwm

    # B-C-narrow Phase 2 POST-fire (v2 PFR R1 per CB3 + CB4):
    # Write parent batch_summary row. Children (one per evaluated candidate)
    # already written by engine inside run_regime_holdout's _write_to_registry
    # call (Phase 0 sequencing per spec §3.1.2). This block writes ONLY the parent.
    if args.enable_b_c_narrow_recovery:
        if forward_window_metadata is None:
            # Should be unreachable post-CB2 identity guard (regime_key locked to
            # forward_2026 → forward_window_metadata always captured). Defensive
            # raise per HARD CONSTRAINT — never silently fall through.
            raise RuntimeError(
                "B-C-narrow finalize POST-fire: forward_window_metadata missing "
                "despite passing identity guard. Possible regression in "
                "forward_window_metadata capture at scripts:954-973."
            )
        # CB3 PFR R1 ADOPT: derive fee_model from cost_model.fee_model_label
        # (matches children's fee_model via engine.py:1278). NO hardcoded "phase4_15bps_v1".
        # Item 2 polish (T10 Bundle a): reuse `_exec_cfg` loaded once above at
        # the metadata block — was a second load_execution_config call.
        _cost_model = ConstantSlippage.from_config(_exec_cfg)
        cohort_metadata = {
            "execution_config_path": _exec_cfg_path_relative,
            "execution_config_sha256": hashlib.sha256(_exec_cfg_bytes).hexdigest(),
            "parquet_data_sha256": forward_window_metadata["parquet_data_sha256"],
            "regime_key": args.regime_key,
            # cost_anchor_id locked to phase4_forward_15bps_v1 per spec §2 Q5
            # (B-C-narrow uses phase4_forward_15bps_v1 anchor; Tier 5/6 promotion
            # uses spot_realistic_15bps_v1 anchor at SEPARATE successor cycle).
            "cost_anchor_id": "phase4_forward_15bps_v1",
            "current_git_sha": head_sha,
            "effective_start": forward_window_metadata["forward_window_start_utc"],
            # CB3 PFR R1 ADOPT: initial_capital = engine cash default (engine.py:2324 = 10_000.0).
            # Producer's _evaluate_one_candidate does NOT pass cash override; engine uses default
            # → children rows have initial_capital = 10_000.0. Parent MUST match for consistency.
            "initial_capital": 10_000.0,
            # CB3 PFR R1 ADOPT: derive from cost_model.fee_model_label (slippage.py:94-100).
            # For execution_phase4_15bps.yaml → total_bps = 15 → "effective_15bps_per_side".
            # NO hardcoded literal.
            "fee_model": _cost_model.fee_model_label,
        }
        _finalize_batch_registry(
            parent_run_id=run_id,
            cohort_metadata=cohort_metadata,
            db_path=None,  # DEFAULT_DB_PATH; co-located with engine-written children
        )
        logger.info(
            "[B-C-narrow] _finalize_batch_registry: parent batch_summary row written at "
            "run_id=%s (engine_commit=%s, fee_model=%s, cohort_metadata fields=%d)",
            run_id, CORRECTED_WF_ENGINE_COMMIT, _cost_model.fee_model_label, len(cohort_metadata),
        )

    _write_aggregate_summary(aggregate, run_dir / "holdout_summary.json")

    # Final stdout summary
    print("\n[Phase 2C eval gate] === AGGREGATE ===")
    print(f"  total candidates evaluated: {aggregate['counts']['total']}")
    print(f"  holdout_passed: {aggregate['counts']['holdout_passed']}")
    print(f"  holdout_failed: {aggregate['counts']['holdout_failed']}")
    print(f"  holdout_error:  {aggregate['counts']['holdout_error']}")
    print(
        f"  primary universe (wf>{PRIMARY_THRESHOLD}): "
        f"{aggregate['primary_universe_holdout_passed']}"
        f"/{aggregate['primary_universe_total']} passed holdout"
    )
    print(
        f"  audit-only (wf<={PRIMARY_THRESHOLD}): "
        f"{aggregate['audit_only_holdout_passed']}"
        f"/{aggregate['audit_only_total']} passed holdout"
    )
    print(f"\n[Phase 2C eval gate] run_dir: {run_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

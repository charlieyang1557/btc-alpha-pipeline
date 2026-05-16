"""Sealed-input loaders + sha256 verification gate + canonical constants.

All paths and sha256 anchors per sealed §1 of
docs/phase5/PHASE5_DIAGNOSTIC_SUBSPEC.md (sub-spec drafting cycle SEAL at
commit 49ae7e3). Single source of truth for sealed-input access across
phase5.modes.* and phase5.labels.* consumers.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

import pandas as pd

# ---------------------------------------------------------------------------
# Canonical sealed §1 constants (invariant; sealed at 1b08ece).
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent

EXPECTED_PARQUET_SHA256 = (
    "db4ce1d2a2e5e7b556975837260f7aaa29ee4fd5ddc603690d1bc57912aa7035"
)

BTC_PARQUET_PATH = REPO_ROOT / "data" / "raw" / "btcusdt_1h.parquet"

COHORT_A_CSV_PATH = (
    REPO_ROOT / "data" / "phase4_scoping" / "cohort_a_candidate_reference.csv"
)

PHASE4_FORWARD_ROOT = REPO_ROOT / "data" / "phase2c_evaluation_gate"

PHASE4_FORWARD_COST_LEVELS_BPS = (7, 13, 15, 17)

PHASE2C_15_REGIMES = ("bear_2022", "audit_2024", "eval_2020", "eval_2021")

# Forward window per sealed §1 + §2.f.
FORWARD_WINDOW_START = pd.Timestamp("2026-01-01T00:00:00", tz="UTC")
FORWARD_WINDOW_END_INCLUSIVE = pd.Timestamp("2026-04-16T07:00:00", tz="UTC")
FORWARD_WINDOW_BARS = 2528

# Reference universe per sealed §2.f (2020-01-01 to 2024-12-31 inclusive).
REFERENCE_UNIVERSE_START = pd.Timestamp("2020-01-01T00:00:00", tz="UTC")
REFERENCE_UNIVERSE_END_INCLUSIVE = pd.Timestamp("2024-12-31T23:00:00", tz="UTC")

# Sealed §2.f block construction: 17 non-overlapping 2528-bar blocks.
REFERENCE_BLOCK_COUNT_EXPECTED = 17
REFERENCE_BLOCK_SIZE_BARS = 2528

# Sealed cohort_a cardinality.
COHORT_A_SIZE = 39

# Sealed broader-universe cardinality (per Path A probe; full broader-universe).
BROADER_UNIVERSE_SIZE = 993

# Sealed §2.d AND-gate sub-criterion thresholds (per CLAUDE.md PHASE2C v2 split).
ANDGATE_MIN_SHARPE = -0.5
ANDGATE_MAX_DRAWDOWN = 0.25
ANDGATE_MIN_TOTAL_RETURN = -0.15
ANDGATE_MIN_TOTAL_TRADES = 5

# Sealed §2.e Phase 4 PLAN §1.5 stratification (per cohort_a CSV theme column).
STRATUM_A_THEME = "calendar_effect"
STRATUM_A_SIZE_EXPECTED = 22
STRATUM_B_SIZE_EXPECTED = 17


# ---------------------------------------------------------------------------
# Sealed sha256 verification gate (§1 + §2.f pre-execution check).
# ---------------------------------------------------------------------------


def compute_parquet_sha256(path: Path = BTC_PARQUET_PATH) -> str:
    """Compute sha256 hex digest of the canonical BTC 1h parquet."""
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_parquet_sha256(path: Path = BTC_PARQUET_PATH) -> tuple[bool, str]:
    """Return (matches, actual_digest) verifying sealed §1/§2.f parquet anchor."""
    actual = compute_parquet_sha256(path)
    return actual == EXPECTED_PARQUET_SHA256, actual


# ---------------------------------------------------------------------------
# Sealed-input loaders (read-only; treat all artifacts as immutable).
# ---------------------------------------------------------------------------


def load_cohort_a() -> pd.DataFrame:
    """Load cohort_a candidate reference CSV (sealed at 11b39f2; 39 rows)."""
    df = pd.read_csv(COHORT_A_CSV_PATH)
    if len(df) != COHORT_A_SIZE:
        raise ValueError(
            f"cohort_a expected {COHORT_A_SIZE} rows, got {len(df)} "
            f"(sealed §1 invariant)"
        )
    return df


def forward_test_csv_path(cost_bps: int) -> Path:
    """Path to phase4 forward-test holdout_results.csv at given cost level."""
    return (
        PHASE4_FORWARD_ROOT
        / f"phase4_forward_2026_{cost_bps:02d}bps_v1"
        / "holdout_results.csv"
    )


def load_forward_test(cost_bps: int) -> pd.DataFrame:
    """Load Phase 4 forward-test holdout_results.csv at cost_bps cost level.

    Each row is one of the 39 cohort_a candidates evaluated on the 2026
    forward window at the given cost basis. Schema per sealed §1 lineage.
    """
    if cost_bps not in PHASE4_FORWARD_COST_LEVELS_BPS:
        raise ValueError(
            f"cost_bps {cost_bps} not in sealed §1 cost-sweep "
            f"{PHASE4_FORWARD_COST_LEVELS_BPS}"
        )
    df = pd.read_csv(forward_test_csv_path(cost_bps))
    if len(df) != COHORT_A_SIZE:
        raise ValueError(
            f"forward-test at {cost_bps}bps expected {COHORT_A_SIZE} rows, "
            f"got {len(df)} (sealed §1 invariant)"
        )
    return df


def broader_universe_regime_dir(regime: str) -> Path:
    """Per-regime directory containing 993 per-candidate holdout_summary.json."""
    return PHASE4_FORWARD_ROOT / f"phase2c_15_main_fire_{regime}_v1"


def iter_broader_universe_candidates(regime: str) -> Iterator[dict]:
    """Iterate per-candidate holdout_summary.json under a regime directory.

    Skips the run-level aggregator at depth=1; yields only per-candidate
    summaries at depth>=2 (per sealed §1 broader-universe artifact layout).
    """
    root = broader_universe_regime_dir(regime)
    if not root.exists():
        raise FileNotFoundError(
            f"sealed §1 broader-universe regime dir missing: {root}"
        )
    for sub in sorted(root.iterdir()):
        if not sub.is_dir():
            continue
        summary_path = sub / "holdout_summary.json"
        if not summary_path.exists():
            continue
        try:
            with summary_path.open("r") as fh:
                yield json.load(fh)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"malformed holdout_summary.json at {summary_path} "
                f"(sealed §1 broader-universe candidate); "
                f"JSON decode error: {exc}"
            ) from exc


def load_broader_universe_per_regime(regime: str) -> dict[str, dict]:
    """Load broader-universe per-candidate holdout_summary.json as dict by hash.

    Returns {hypothesis_hash: full_summary_dict}. Sealed §1 invariant: 993
    candidates per regime under current data state.
    """
    out: dict[str, dict] = {}
    for summary in iter_broader_universe_candidates(regime):
        h = summary.get("hypothesis_hash")
        if not h:
            continue
        out[h] = summary
    if len(out) != BROADER_UNIVERSE_SIZE:
        raise ValueError(
            f"broader-universe regime '{regime}' expected "
            f"{BROADER_UNIVERSE_SIZE} candidates, got {len(out)} "
            f"(sealed §1 Path A probe invariant)"
        )
    return out


def load_btc_parquet() -> pd.DataFrame:
    """Load canonical BTC 1h OHLCV parquet (sealed §1/§2.f anchor)."""
    try:
        return pd.read_parquet(BTC_PARQUET_PATH)
    except FileNotFoundError as exc:
        raise FileNotFoundError(
            f"sealed §1/§2.f canonical BTC parquet not found at "
            f"{BTC_PARQUET_PATH} (sealed sha256 anchor "
            f"{EXPECTED_PARQUET_SHA256})"
        ) from exc


# ---------------------------------------------------------------------------
# Derived helper containers.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SealedInputs:
    """Snapshot of all sealed §1 inputs loaded for a single execution run.

    Frozen dataclass per project immutability preference; per-mode procedures
    consume this read-only.
    """

    cohort_a: pd.DataFrame
    forward_per_cost_bps: dict[int, pd.DataFrame]
    broader_universe_per_regime: dict[str, dict[str, dict]]
    btc_parquet: pd.DataFrame
    parquet_sha256: str


def load_all_sealed_inputs(skip_parquet: bool = False) -> SealedInputs:
    """Load and validate every sealed §1 input artifact.

    If skip_parquet=True, defers parquet load to the §2.f consumer (used when
    a caller wants to perform initial schema verification before paying the
    parquet read cost).
    """
    cohort_a = load_cohort_a()
    forward_per_cost_bps = {
        bps: load_forward_test(bps) for bps in PHASE4_FORWARD_COST_LEVELS_BPS
    }
    broader_universe_per_regime = {
        regime: load_broader_universe_per_regime(regime)
        for regime in PHASE2C_15_REGIMES
    }
    if skip_parquet:
        btc_parquet = pd.DataFrame()
        parquet_sha256 = ""
    else:
        btc_parquet = load_btc_parquet()
        matches, parquet_sha256 = verify_parquet_sha256()
        if not matches:
            raise ValueError(
                f"parquet sha256 mismatch: expected "
                f"{EXPECTED_PARQUET_SHA256}, got {parquet_sha256} "
                f"(sealed §1/§2.f pre-execution verification gate failed)"
            )
    return SealedInputs(
        cohort_a=cohort_a,
        forward_per_cost_bps=forward_per_cost_bps,
        broader_universe_per_regime=broader_universe_per_regime,
        btc_parquet=btc_parquet,
        parquet_sha256=parquet_sha256,
    )

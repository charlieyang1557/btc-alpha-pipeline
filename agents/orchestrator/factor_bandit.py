"""Factor bandit module for Phase 2.5 Track A.

Per sub-spec SEAL ``ab8e715`` + amendment v1 SEAL ``850aa1d``, this
module owns:

- ``BatchBanditSelection`` dataclass (Wave 0 W0.1)
- ``init_factor_posterior_db`` — SQLite schema initializer (Wave A-2)
- ``observe_batch`` — append-only ledger writer + posterior updater (A-2)
- ``get_posterior`` — Beta(α, β) reader with Beta(1, 1) cold-start default
- ``curate_top_k`` — Thompson sampling with deterministic SHA-256 seed

DISCIPLINE LOCKS (parked-branch-internal until merge):

- A-Lock-1: NEVER pass ``factor_posterior.alpha`` / ``.beta`` values into
  any Proposer or Critic LLM context. Orchestrator-internal only.
- A-Lock-2: NEVER expose factor pass-rate counts or any per-factor
  metric in any LLM-visible artifact.
- A-Lock-3: NEVER curate the menu using validation (2024) / test (2025) /
  regime-holdout (2022) per-hypothesis numeric metrics — only the binary
  ``regime_holdout_passed`` boolean from the registry.
- A-Lock-5: NEVER decay or rewrite bandit observations retroactively;
  the ``factor_bandit_observations`` ledger is append-only.
- A-Lock-6: NEVER update bandit posterior mid-batch — only at batch
  close after ``assert_lifecycle_invariant_at_batch_close()`` passes.
  ``observe_batch`` is the SINGLE call site that mutates posterior.
- A-Lock-7: NEVER write factor posterior values / regime-pass counts /
  top-K curation rank to non-prompt LLM-visible surfaces.

DETERMINISM:
- A-5 (amendment-corrected): seed derived from
  ``int.from_bytes(hashlib.sha256(batch_id.encode('utf-8')).digest()[:8], 'big')``.
  Python's built-in ``hash()`` is salted per-process via PYTHONHASHSEED
  and is NOT suitable.
"""
from __future__ import annotations

import hashlib
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import numpy as np


# ---------------------------------------------------------------------------
# Shape lock (Wave 0 W0.1)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class BatchBanditSelection:
    """Top-K factor curation for one batch, materialized from posterior sampling.

    Per sub-spec §1.2: the orchestrator extracts ``.top_factors`` and passes
    it as the existing ``top_factors: tuple[str, ...]`` parameter to
    ``build_prompt()``, preserving call-site signature stability.

    Attributes:
        batch_id: UUID of the batch this selection applies to.
        top_factors: K-tuple of factor IDs (K locked at sub-spec A-3, default 5).
            Ordered by Thompson-sampled rank descending.
        selection_seed: Deterministic SHA-256-derived seed used for
            Thompson sampling; archived for replay. Same ``batch_id`` →
            same selection.
    """

    batch_id: str
    top_factors: tuple[str, ...]
    selection_seed: int


# ---------------------------------------------------------------------------
# Determinism helper (A-5 amendment-corrected seed derivation)
# ---------------------------------------------------------------------------


def _seed_from_batch_id(batch_id: str) -> int:
    """Derive a deterministic 64-bit seed from a batch_id string.

    Per amendment v1 §3 A-5 (correctness fix from architect F2 Session 2):
    Python's built-in ``hash()`` is salted per CPython interpreter instance
    via PYTHONHASHSEED and therefore non-deterministic across replay runs.
    SHA-256 truncated to 8 bytes gives cryptographic determinism.
    """
    digest = hashlib.sha256(batch_id.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big")


# ---------------------------------------------------------------------------
# SQLite schema + DB initialization
# ---------------------------------------------------------------------------


_SCHEMA = """
CREATE TABLE IF NOT EXISTS factor_posterior (
    factor_id TEXT PRIMARY KEY,
    alpha INTEGER NOT NULL,
    beta INTEGER NOT NULL,
    last_updated_batch_id TEXT,
    last_updated_utc TEXT
);

CREATE TABLE IF NOT EXISTS factor_bandit_observations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    batch_id TEXT NOT NULL,
    factor_id TEXT NOT NULL,
    regime_holdout_passed INTEGER NOT NULL CHECK (regime_holdout_passed IN (0, 1)),
    observed_utc TEXT NOT NULL,
    hypothesis_hash TEXT NOT NULL,
    posterior_alpha_pre INTEGER NOT NULL,
    posterior_beta_pre INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_observations_batch
    ON factor_bandit_observations (batch_id);

CREATE INDEX IF NOT EXISTS idx_observations_factor
    ON factor_bandit_observations (factor_id);
"""


def init_factor_posterior_db(ledger_path: Path) -> None:
    """Create the ``factor_posterior`` + ``factor_bandit_observations`` tables.

    Idempotent (``CREATE TABLE IF NOT EXISTS``). Per A-Lock-5 the
    observations table is append-only by convention; SQLite does not
    enforce this at schema level, but ``observe_batch`` is the only
    INSERT call site in this module, and there are no UPDATE/DELETE
    statements anywhere in this file.
    """
    with sqlite3.connect(ledger_path) as conn:
        conn.executescript(_SCHEMA)
        conn.commit()


# ---------------------------------------------------------------------------
# Posterior read + observation write
# ---------------------------------------------------------------------------


def get_posterior(factor_id: str, ledger_path: Path) -> tuple[int, int]:
    """Read current Beta(α, β) for a factor; return ``(1, 1)`` cold-start default.

    Per sub-spec A-1: cold-start prior is Beta(1, 1) uniform (uninformed).
    A factor never observed returns the cold-start prior; calling
    ``get_posterior`` does NOT mutate the database.
    """
    with sqlite3.connect(ledger_path) as conn:
        row = conn.execute(
            "SELECT alpha, beta FROM factor_posterior WHERE factor_id = ?",
            (factor_id,),
        ).fetchone()
    if row is None:
        return (1, 1)
    return (int(row[0]), int(row[1]))


# Observation entry: (hypothesis_hash, factor set, regime_holdout_passed bool)
Observation = tuple[str, Iterable[str], bool]


def observe_batch(
    *,
    batch_id: str,
    observations: Iterable[Observation],
    ledger_path: Path,
) -> None:
    """Append observations and increment Beta posterior for each factor.

    Per A-Lock-5 + A-Lock-6: append-only ledger; this is the SOLE
    posterior-mutating entry point in the module. Called exactly once
    per batch, at batch close, after the lifecycle invariant passes.

    For each (hypothesis_hash, factor_set, regime_passed) observation,
    every factor in ``factor_set`` gets:
      - One row in ``factor_bandit_observations`` with the PRE-update
        posterior snapshot (α_pre, β_pre)
      - α += 1 if regime_passed=True, β += 1 if False (Beta posterior
        update for a single Bernoulli trial)

    Args:
        batch_id: UUID of the batch being observed.
        observations: Iterable of ``(hypothesis_hash, factor_set,
            regime_passed)`` tuples.
        ledger_path: Path to the SQLite database (initialized via
            ``init_factor_posterior_db``).
    """
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    with sqlite3.connect(ledger_path) as conn:
        for hypothesis_hash, factor_set, regime_passed in observations:
            outcome = 1 if regime_passed else 0
            for factor_id in factor_set:
                # Read current posterior (Beta(1, 1) cold-start if absent)
                row = conn.execute(
                    "SELECT alpha, beta FROM factor_posterior "
                    "WHERE factor_id = ?",
                    (factor_id,),
                ).fetchone()
                if row is None:
                    alpha_pre, beta_pre = 1, 1
                else:
                    alpha_pre, beta_pre = int(row[0]), int(row[1])

                # Append observation row (PRE-update posterior snapshot)
                conn.execute(
                    "INSERT INTO factor_bandit_observations "
                    "(batch_id, factor_id, regime_holdout_passed, "
                    "observed_utc, hypothesis_hash, "
                    "posterior_alpha_pre, posterior_beta_pre) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (
                        batch_id,
                        factor_id,
                        outcome,
                        timestamp,
                        hypothesis_hash,
                        alpha_pre,
                        beta_pre,
                    ),
                )

                # Update posterior (Beta(α+pass, β+fail))
                alpha_post = alpha_pre + outcome
                beta_post = beta_pre + (1 - outcome)
                conn.execute(
                    "INSERT INTO factor_posterior "
                    "(factor_id, alpha, beta, "
                    "last_updated_batch_id, last_updated_utc) "
                    "VALUES (?, ?, ?, ?, ?) "
                    "ON CONFLICT(factor_id) DO UPDATE SET "
                    "alpha = excluded.alpha, "
                    "beta = excluded.beta, "
                    "last_updated_batch_id = excluded.last_updated_batch_id, "
                    "last_updated_utc = excluded.last_updated_utc",
                    (
                        factor_id,
                        alpha_post,
                        beta_post,
                        batch_id,
                        timestamp,
                    ),
                )
        conn.commit()


# ---------------------------------------------------------------------------
# Thompson sampling curation
# ---------------------------------------------------------------------------


def curate_top_k(
    *,
    batch_id: str,
    k: int,
    ledger_path: Path,
) -> BatchBanditSelection:
    """Thompson-sample K factors with deterministic SHA-256 seed.

    Per sub-spec A-3 (K=5 default at call site), A-5 (deterministic seed),
    A-8 (per-batch frozen curation): sample one Beta(α, β) draw per
    factor; rank descending by sample; return top K.

    If fewer than K factors have observations, returns all observed
    factors (no padding). Cold-start factors (no observations) are NOT
    sampled — they would all draw from Beta(1, 1) at uniform expectation
    0.5, providing no discrimination.

    Args:
        batch_id: UUID of the batch the curation applies to. Used as
            deterministic seed source.
        k: Maximum number of factors to return (sub-spec A-3 default 5;
            caller chooses).
        ledger_path: Path to the SQLite database.

    Returns:
        ``BatchBanditSelection`` with up to K factors, sorted by Thompson
        sample descending. ``selection_seed`` records the deterministic
        seed for replay/audit.
    """
    seed = _seed_from_batch_id(batch_id)
    rng = np.random.default_rng(seed)

    with sqlite3.connect(ledger_path) as conn:
        rows = conn.execute(
            "SELECT factor_id, alpha, beta FROM factor_posterior "
            "ORDER BY factor_id"  # deterministic iteration
        ).fetchall()

    # Thompson sample per factor
    samples: list[tuple[str, float]] = [
        (factor_id, float(rng.beta(int(alpha), int(beta))))
        for factor_id, alpha, beta in rows
    ]

    # Rank descending by sampled draw
    samples.sort(key=lambda x: -x[1])

    top_factors = tuple(factor_id for factor_id, _ in samples[:k])
    return BatchBanditSelection(
        batch_id=batch_id,
        top_factors=top_factors,
        selection_seed=seed,
    )


__all__ = [
    "BatchBanditSelection",
    "curate_top_k",
    "get_posterior",
    "init_factor_posterior_db",
    "observe_batch",
]

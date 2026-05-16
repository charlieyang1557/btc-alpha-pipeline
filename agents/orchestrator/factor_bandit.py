"""Factor bandit module for Phase 2.5 Track A.

Per sub-spec SEAL ab8e715, this module owns:

- ``BatchBanditSelection`` dataclass (Wave 0 W0.1; this commit)
- Thompson sampling + posterior update logic (Wave A-2; deferred)
- ``factor_posterior`` SQLite table + ``factor_bandit_observations``
  append-only ledger (Wave A-2; deferred)

DISCIPLINE LOCKS (proposed HARD CONSTRAINTS — parked-branch-internal
until merge to main per pre-merge verification checklist item 4):

- A-Lock-1: NEVER pass ``factor_posterior.alpha`` / ``.beta`` values
  into any Proposer or Critic LLM context. Orchestrator-internal only.
- A-Lock-2: NEVER expose factor pass-rate counts, regime-pass counts,
  or any per-factor metric in any LLM-visible artifact.
- A-Lock-3: NEVER curate the menu using validation (2024) / test (2025)
  / regime-holdout (2022) per-hypothesis numeric metrics — only the
  binary ``regime_holdout_passed`` boolean from the registry.
- A-Lock-5: NEVER decay or rewrite bandit observations retroactively;
  the ``factor_bandit_observations`` ledger is append-only.
- A-Lock-6: NEVER update bandit posterior mid-batch — only at batch
  close after ``assert_lifecycle_invariant_at_batch_close()`` passes.
- A-Lock-7: NEVER write factor posterior values / regime-pass counts
  / top-K curation rank to non-prompt LLM-visible surfaces (batch
  summary exports, commit messages, error logs flowing to LLM context,
  ``HypothesisRecord.provenance``). Bandit posterior lives only in the
  ``factor_posterior`` table and orchestrator-internal logs.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BatchBanditSelection:
    """Top-K factor curation for one batch, materialized from posterior sampling.

    Per sub-spec §1.2: the orchestrator extracts ``.top_factors`` and passes
    it as the existing ``top_factors: tuple[str, ...]`` parameter to
    ``build_prompt()``, preserving the call-site signature stability. Wave
    A-2 wires the materialization path from the Thompson-sampled posterior;
    this Wave 0 W0.1 commit locks only the shape.

    Attributes:
        batch_id: UUID of the batch this selection applies to.
        top_factors: K-tuple of factor IDs (K=5 per sub-spec A-3).
            Ordered by Thompson-sampled rank descending.
        selection_seed: Deterministic seed used for Thompson sampling,
            per sub-spec A-5 SEAL correction —
            ``int.from_bytes(hashlib.sha256(batch_id.encode('utf-8')).digest()[:8], 'big')``.
            Archived for replay; same ``batch_id`` → same selection.
    """

    batch_id: str
    top_factors: tuple[str, ...]
    selection_seed: int


__all__ = ["BatchBanditSelection"]

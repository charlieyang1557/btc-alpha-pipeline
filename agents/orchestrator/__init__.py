"""Phase 2B orchestrator package.

D6 Stage 1 scope (dry-run plumbing):
    - :mod:`ingest` — validate → hash → dedup → lifecycle state machine
    - :mod:`budget_ledger` — crash-safe pre-charge SQLite ledger

D7, D8, D9 pieces (Critic, full batch loop, DSR finalization) are NOT
yet implemented; this package currently contains only the pieces
needed to prove Proposer plumbing before Sonnet lands in Stage 2.

CONTRACT BOUNDARY: this package MUST NOT import ``anthropic`` anywhere.
Only ``agents.proposer.interface.ProposerBackend`` (a Protocol) is
permitted as the dependency edge between orchestrator and any
model-specific backend. Enforced mechanically by a ripgrep check in
the D6 Stage 1 test suite.
"""

from agents.orchestrator.budget_ledger import (
    BATCH_CAP_USD,
    BudgetLedger,
    LedgerEntry,
    MONTHLY_CAP_USD,
    STATUS_COMPLETED,
    STATUS_CRASHED,
    STATUS_PENDING,
)
from agents.orchestrator.ingest import (
    BatchIngestState,
    D6_STAGE1_LIFECYCLE_STATES,
    DUPLICATE,
    HypothesisRecord,
    INVALID_DSL,
    PENDING_BACKTEST,
    REJECTED_COMPLEXITY,
    assert_lifecycle_invariant_at_batch_close,
    ingest_candidate,
    ingest_output,
    ingest_outputs,
)

__all__ = [
    "BATCH_CAP_USD",
    "BatchIngestState",
    "BudgetLedger",
    "D6_STAGE1_LIFECYCLE_STATES",
    "DUPLICATE",
    "HypothesisRecord",
    "INVALID_DSL",
    "LedgerEntry",
    "MONTHLY_CAP_USD",
    "PENDING_BACKTEST",
    "REJECTED_COMPLEXITY",
    "STATUS_COMPLETED",
    "STATUS_CRASHED",
    "STATUS_PENDING",
    "assert_lifecycle_invariant_at_batch_close",
    "ingest_candidate",
    "ingest_output",
    "ingest_outputs",
]

"""Tests for budget_ledger.py D7-specific write paths (D7 Stage 2a).

Covers:
    - write_pending with d7b_critic/critique succeeds
    - LedgerEntry has backend_kind and call_role fields
    - cost_by_backend_kind returns both keys with defaults 0.0
    - cost_by_backend_kind correctly separates d6 and d7 costs
    - cost_by_backend_kind with batch_id filter works
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from agents.orchestrator.budget_ledger import (
    BACKEND_KIND_D6_PROPOSER,
    BACKEND_KIND_D7B_CRITIC,
    BudgetLedger,
    CALL_ROLE_CRITIQUE,
    CALL_ROLE_PROPOSE,
    LedgerEntry,
    VALID_BACKEND_KINDS,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def ledger(tmp_path):
    return BudgetLedger(tmp_path / "ledger.db")


def _utc(y, m, d, h=0) -> datetime:
    return datetime(y, m, d, h, 0, 0, tzinfo=timezone.utc)


# ---------------------------------------------------------------------------
# D7b critic write
# ---------------------------------------------------------------------------


def test_write_pending_d7b_critic_critique(ledger):
    """write_pending with d7b_critic/critique succeeds."""
    row_id = ledger.write_pending(
        batch_id="b1",
        api_call_kind="d7b_critic",
        backend_kind=BACKEND_KIND_D7B_CRITIC,
        call_role=CALL_ROLE_CRITIQUE,
        estimated_cost_usd=0.03,
    )
    assert row_id is not None
    entries = ledger.list_entries(batch_id="b1")
    assert len(entries) == 1
    assert entries[0].backend_kind == BACKEND_KIND_D7B_CRITIC
    assert entries[0].call_role == CALL_ROLE_CRITIQUE
    assert entries[0].estimated_cost == pytest.approx(0.03)


# ---------------------------------------------------------------------------
# LedgerEntry fields
# ---------------------------------------------------------------------------


def test_ledger_entry_has_backend_kind_field(ledger):
    """LedgerEntry dataclass has backend_kind field."""
    ledger.write_pending(
        batch_id="b1",
        api_call_kind="proposer",
        backend_kind=BACKEND_KIND_D6_PROPOSER,
        call_role=CALL_ROLE_PROPOSE,
        estimated_cost_usd=0.10,
    )
    entry = ledger.list_entries(batch_id="b1")[0]
    assert hasattr(entry, "backend_kind")
    assert entry.backend_kind == BACKEND_KIND_D6_PROPOSER


def test_ledger_entry_has_call_role_field(ledger):
    """LedgerEntry dataclass has call_role field."""
    ledger.write_pending(
        batch_id="b1",
        api_call_kind="proposer",
        backend_kind=BACKEND_KIND_D6_PROPOSER,
        call_role=CALL_ROLE_PROPOSE,
        estimated_cost_usd=0.10,
    )
    entry = ledger.list_entries(batch_id="b1")[0]
    assert hasattr(entry, "call_role")
    assert entry.call_role == CALL_ROLE_PROPOSE


# ---------------------------------------------------------------------------
# cost_by_backend_kind
# ---------------------------------------------------------------------------


def test_cost_by_backend_kind_returns_both_keys_with_defaults(ledger):
    """cost_by_backend_kind returns all VALID_BACKEND_KINDS defaulting to 0.0."""
    result = ledger.cost_by_backend_kind()
    for kind in VALID_BACKEND_KINDS:
        assert kind in result
        assert result[kind] == pytest.approx(0.0)


def test_cost_by_backend_kind_separates_d6_and_d7(ledger):
    """D6 proposer and D7b critic costs are correctly separated."""
    now = _utc(2026, 4, 10, 12)
    ledger.write_pending(
        batch_id="b1",
        api_call_kind="proposer",
        backend_kind=BACKEND_KIND_D6_PROPOSER,
        call_role=CALL_ROLE_PROPOSE,
        estimated_cost_usd=0.50,
        now=now,
    )
    rid = ledger.write_pending(
        batch_id="b1",
        api_call_kind="d7b_critic",
        backend_kind=BACKEND_KIND_D7B_CRITIC,
        call_role=CALL_ROLE_CRITIQUE,
        estimated_cost_usd=0.03,
        now=now,
    )
    ledger.finalize(rid, actual_cost_usd=0.02)

    result = ledger.cost_by_backend_kind()
    assert result[BACKEND_KIND_D6_PROPOSER] == pytest.approx(0.50)
    # Finalized critic uses actual_cost.
    assert result[BACKEND_KIND_D7B_CRITIC] == pytest.approx(0.02)


def test_cost_by_backend_kind_with_batch_id_filter(ledger):
    """cost_by_backend_kind with batch_id filter isolates the batch."""
    now = _utc(2026, 4, 10, 12)
    ledger.write_pending(
        batch_id="b1",
        api_call_kind="proposer",
        backend_kind=BACKEND_KIND_D6_PROPOSER,
        call_role=CALL_ROLE_PROPOSE,
        estimated_cost_usd=1.00,
        now=now,
    )
    ledger.write_pending(
        batch_id="b2",
        api_call_kind="proposer",
        backend_kind=BACKEND_KIND_D6_PROPOSER,
        call_role=CALL_ROLE_PROPOSE,
        estimated_cost_usd=2.00,
        now=now,
    )
    ledger.write_pending(
        batch_id="b1",
        api_call_kind="d7b_critic",
        backend_kind=BACKEND_KIND_D7B_CRITIC,
        call_role=CALL_ROLE_CRITIQUE,
        estimated_cost_usd=0.05,
        now=now,
    )

    result_b1 = ledger.cost_by_backend_kind(batch_id="b1")
    assert result_b1[BACKEND_KIND_D6_PROPOSER] == pytest.approx(1.00)
    assert result_b1[BACKEND_KIND_D7B_CRITIC] == pytest.approx(0.05)

    result_b2 = ledger.cost_by_backend_kind(batch_id="b2")
    assert result_b2[BACKEND_KIND_D6_PROPOSER] == pytest.approx(2.00)
    assert result_b2[BACKEND_KIND_D7B_CRITIC] == pytest.approx(0.0)

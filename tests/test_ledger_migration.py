"""Tests for budget_ledger.py migration — backend_kind/call_role columns (D7 Stage 2a).

Covers:
    - Fresh database has backend_kind and call_role columns
    - Pre-existing database without columns gets migrated
    - Migration backfills existing rows with d6_proposer/propose
    - Migration is idempotent (running twice is safe)
    - Invalid backend_kind raises ValueError
    - Invalid call_role raises ValueError
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone

import pytest

from agents.orchestrator.budget_ledger import (
    BACKEND_KIND_D6_PROPOSER,
    BACKEND_KIND_D7B_CRITIC,
    BudgetLedger,
    CALL_ROLE_CRITIQUE,
    CALL_ROLE_PROPOSE,
    VALID_BACKEND_KINDS,
    VALID_CALL_ROLES,
    _migrate_backend_kind_call_role,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def ledger(tmp_path):
    return BudgetLedger(tmp_path / "ledger.db")


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# Fresh database schema
# ---------------------------------------------------------------------------


def test_fresh_db_has_backend_kind_column(tmp_path):
    """A freshly created database has the backend_kind column."""
    db_path = tmp_path / "fresh.db"
    ledger = BudgetLedger(db_path)
    conn = sqlite3.connect(db_path)
    cols = {row[1] for row in conn.execute("PRAGMA table_info(ledger)")}
    conn.close()
    assert "backend_kind" in cols


def test_fresh_db_has_call_role_column(tmp_path):
    """A freshly created database has the call_role column."""
    db_path = tmp_path / "fresh.db"
    ledger = BudgetLedger(db_path)
    conn = sqlite3.connect(db_path)
    cols = {row[1] for row in conn.execute("PRAGMA table_info(ledger)")}
    conn.close()
    assert "call_role" in cols


# ---------------------------------------------------------------------------
# Pre-existing database migration
# ---------------------------------------------------------------------------


def _create_pre_migration_db(db_path) -> None:
    """Create a ledger database WITHOUT backend_kind/call_role columns."""
    conn = sqlite3.connect(db_path)
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS ledger (
            id                TEXT PRIMARY KEY,
            batch_id          TEXT NOT NULL,
            api_call_kind     TEXT NOT NULL,
            status            TEXT NOT NULL,
            estimated_cost    REAL NOT NULL,
            actual_cost       REAL,
            created_at_utc    TEXT NOT NULL,
            completed_at_utc  TEXT,
            notes             TEXT
        );
    """)
    conn.execute(
        "INSERT INTO ledger (id, batch_id, api_call_kind, status, "
        "estimated_cost, created_at_utc) VALUES (?, ?, ?, ?, ?, ?)",
        ("row_1", "batch_old", "proposer", "completed", 0.50,
         "2026-04-01T12:00:00.000Z"),
    )
    conn.execute(
        "INSERT INTO ledger (id, batch_id, api_call_kind, status, "
        "estimated_cost, created_at_utc) VALUES (?, ?, ?, ?, ?, ?)",
        ("row_2", "batch_old", "proposer", "pending", 0.25,
         "2026-04-01T13:00:00.000Z"),
    )
    conn.commit()
    conn.close()


def test_pre_existing_db_gets_migrated(tmp_path):
    """A database without backend_kind/call_role gets columns added."""
    db_path = tmp_path / "old.db"
    _create_pre_migration_db(db_path)

    # Opening with BudgetLedger triggers migration.
    ledger = BudgetLedger(db_path)

    conn = sqlite3.connect(db_path)
    cols = {row[1] for row in conn.execute("PRAGMA table_info(ledger)")}
    conn.close()
    assert "backend_kind" in cols
    assert "call_role" in cols


def test_migration_backfills_existing_rows(tmp_path):
    """Existing rows get backfilled with d6_proposer/propose."""
    db_path = tmp_path / "old.db"
    _create_pre_migration_db(db_path)

    ledger = BudgetLedger(db_path)
    entries = ledger.list_entries()
    assert len(entries) == 2
    for entry in entries:
        assert entry.backend_kind == BACKEND_KIND_D6_PROPOSER
        assert entry.call_role == CALL_ROLE_PROPOSE


def test_migration_is_idempotent(tmp_path):
    """Running migration twice does not error or corrupt data."""
    db_path = tmp_path / "old.db"
    _create_pre_migration_db(db_path)

    # First migration via constructor.
    ledger1 = BudgetLedger(db_path)
    entries1 = ledger1.list_entries()

    # Second migration (fresh BudgetLedger instance).
    ledger2 = BudgetLedger(db_path)
    entries2 = ledger2.list_entries()

    assert len(entries1) == len(entries2)
    for e1, e2 in zip(entries1, entries2):
        assert e1.backend_kind == e2.backend_kind
        assert e1.call_role == e2.call_role


# ---------------------------------------------------------------------------
# Validation of backend_kind / call_role
# ---------------------------------------------------------------------------


def test_invalid_backend_kind_raises(ledger):
    """Invalid backend_kind raises ValueError."""
    with pytest.raises(ValueError, match="backend_kind"):
        ledger.write_pending(
            batch_id="b1",
            api_call_kind="proposer",
            backend_kind="invalid_backend",
            call_role="propose",
            estimated_cost_usd=0.10,
        )


def test_invalid_call_role_raises(ledger):
    """Invalid call_role raises ValueError."""
    with pytest.raises(ValueError, match="call_role"):
        ledger.write_pending(
            batch_id="b1",
            api_call_kind="proposer",
            backend_kind="d6_proposer",
            call_role="invalid_role",
            estimated_cost_usd=0.10,
        )

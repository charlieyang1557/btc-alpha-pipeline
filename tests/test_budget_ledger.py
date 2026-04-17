"""D6 Stage 1 — crash-safe pre-charge budget ledger.

Pins the pre-charge semantics: pending rows count against budget at
their ``estimated_cost`` upper bound, and remain counted even after a
simulated crash. UTC calendar month semantics are verified directly so
a rolling 30-day misreading is impossible to regress into.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from agents.orchestrator.budget_ledger import (
    BATCH_CAP_USD,
    BudgetLedger,
    LedgerEntry,
    MONTHLY_CAP_USD,
    STATUS_COMPLETED,
    STATUS_CRASHED,
    STATUS_PENDING,
    _month_bounds,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def ledger(tmp_path):
    return BudgetLedger(tmp_path / "spend_ledger.db")


def _utc(y, m, d, h=0) -> datetime:
    return datetime(y, m, d, h, 0, 0, tzinfo=timezone.utc)


# ---------------------------------------------------------------------------
# Basic pre-charge / finalize
# ---------------------------------------------------------------------------


def test_write_pending_is_immediately_counted(ledger):
    rid = ledger.write_pending(
        batch_id="b1", api_call_kind="proposer", estimated_cost_usd=0.50,
    )
    assert ledger.batch_spent_usd("b1") == pytest.approx(0.50)
    entry = ledger.list_entries(batch_id="b1")[0]
    assert entry.id == rid
    assert entry.status == STATUS_PENDING
    assert entry.actual_cost is None


def test_finalize_replaces_estimate_with_actual(ledger):
    rid = ledger.write_pending(
        batch_id="b1", api_call_kind="proposer", estimated_cost_usd=0.50,
    )
    ledger.finalize(rid, actual_cost_usd=0.12)
    assert ledger.batch_spent_usd("b1") == pytest.approx(0.12)
    entry = ledger.list_entries(batch_id="b1")[0]
    assert entry.status == STATUS_COMPLETED
    assert entry.actual_cost == pytest.approx(0.12)
    assert entry.completed_at_utc is not None


def test_finalize_twice_rejected(ledger):
    rid = ledger.write_pending(
        batch_id="b1", api_call_kind="proposer", estimated_cost_usd=0.50,
    )
    ledger.finalize(rid, actual_cost_usd=0.12)
    with pytest.raises(ValueError, match="status is 'completed'"):
        ledger.finalize(rid, actual_cost_usd=0.12)


def test_finalize_unknown_id_raises_keyerror(ledger):
    with pytest.raises(KeyError):
        ledger.finalize("no-such-row", actual_cost_usd=0.01)


def test_negative_cost_rejected(ledger):
    with pytest.raises(ValueError):
        ledger.write_pending(
            batch_id="b1", api_call_kind="proposer", estimated_cost_usd=-0.01,
        )


# ---------------------------------------------------------------------------
# Crash-safety: pending rows keep counting
# ---------------------------------------------------------------------------


def test_simulated_crash_preserves_precharge_in_totals(ledger):
    """Pending row without finalize still counts — the whole point."""
    ledger.write_pending(
        batch_id="b1", api_call_kind="proposer", estimated_cost_usd=2.00,
    )
    # Process "crashes" before finalize is called. Totals unchanged:
    assert ledger.batch_spent_usd("b1") == pytest.approx(2.00)
    assert ledger.monthly_spent_usd() == pytest.approx(2.00)


def test_mark_crashed_keeps_precharge_counted(ledger):
    rid = ledger.write_pending(
        batch_id="b1", api_call_kind="proposer", estimated_cost_usd=3.00,
    )
    ledger.mark_crashed(rid, notes="network timeout")
    assert ledger.batch_spent_usd("b1") == pytest.approx(3.00)
    entry = ledger.list_entries(batch_id="b1")[0]
    assert entry.status == STATUS_CRASHED
    assert entry.notes == "network timeout"
    assert entry.actual_cost is None  # still the estimate that counts


def test_new_instance_sees_existing_pending_rows(tmp_path):
    """Ledger state survives process restart (the crash-recovery path)."""
    db = tmp_path / "s.db"
    ledger_a = BudgetLedger(db)
    ledger_a.write_pending(
        batch_id="b1", api_call_kind="proposer", estimated_cost_usd=1.00,
    )
    del ledger_a  # simulate crash
    ledger_b = BudgetLedger(db)
    assert ledger_b.batch_spent_usd("b1") == pytest.approx(1.00)
    assert len(ledger_b.pending_entries(batch_id="b1")) == 1


# ---------------------------------------------------------------------------
# Budget gating
# ---------------------------------------------------------------------------


def test_can_afford_respects_batch_cap(ledger):
    # Pre-charge most of the batch budget.
    ledger.write_pending(
        batch_id="b1", api_call_kind="proposer",
        estimated_cost_usd=BATCH_CAP_USD - 1.0,
    )
    assert ledger.can_afford(
        batch_id="b1", estimated_cost_usd=1.0,
    ) is True
    assert ledger.can_afford(
        batch_id="b1", estimated_cost_usd=1.01,
    ) is False


def test_can_afford_respects_monthly_cap(ledger):
    # Use small per-batch rows so the batch cap never binds; stress the
    # monthly cap instead.
    remaining = MONTHLY_CAP_USD
    i = 0
    while remaining > 1.0:
        chunk = min(5.0, remaining)
        ledger.write_pending(
            batch_id=f"b{i}", api_call_kind="proposer",
            estimated_cost_usd=chunk,
        )
        remaining -= chunk
        i += 1
    # Now the monthly cap binds.
    assert ledger.monthly_spent_usd() <= MONTHLY_CAP_USD
    assert ledger.can_afford(
        batch_id="b_new", estimated_cost_usd=remaining,
    ) is True
    assert ledger.can_afford(
        batch_id="b_new", estimated_cost_usd=remaining + 0.01,
    ) is False


# ---------------------------------------------------------------------------
# UTC calendar month semantics (not rolling 30-day)
# ---------------------------------------------------------------------------


def test_month_bounds_jan_and_dec():
    jan_start, jan_end = _month_bounds(_utc(2026, 1, 15))
    assert jan_start == "2026-01-01T00:00:00.000Z"
    assert jan_end == "2026-02-01T00:00:00.000Z"
    dec_start, dec_end = _month_bounds(_utc(2026, 12, 31, 23))
    assert dec_start == "2026-12-01T00:00:00.000Z"
    assert dec_end == "2027-01-01T00:00:00.000Z"


def test_monthly_spent_excludes_prior_month(ledger):
    """A row from last month does NOT count toward this month's total."""
    last_month = _utc(2026, 3, 15, 12)
    this_month = _utc(2026, 4, 2, 3)
    ledger.write_pending(
        batch_id="b_old", api_call_kind="proposer",
        estimated_cost_usd=10.0, now=last_month,
    )
    ledger.write_pending(
        batch_id="b_new", api_call_kind="proposer",
        estimated_cost_usd=4.0, now=this_month,
    )
    assert ledger.monthly_spent_usd(now=this_month) == pytest.approx(4.0)
    assert ledger.monthly_spent_usd(now=last_month) == pytest.approx(10.0)


def test_monthly_rollover_at_month_boundary(ledger):
    """29 days ago is still "this month" iff we haven't crossed 1st-of-month."""
    mar_31 = _utc(2026, 3, 31, 23)
    apr_01 = _utc(2026, 4, 1, 0)
    ledger.write_pending(
        batch_id="b1", api_call_kind="proposer",
        estimated_cost_usd=9.0, now=mar_31,
    )
    # From Mar 31's perspective, it counts.
    assert ledger.monthly_spent_usd(now=mar_31) == pytest.approx(9.0)
    # From Apr 1's perspective, it does NOT count.
    assert ledger.monthly_spent_usd(now=apr_01) == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# Cap constants match CLAUDE.md
# ---------------------------------------------------------------------------


def test_cap_constants_match_claude_md():
    """If CLAUDE.md caps change, this test must be updated explicitly."""
    assert BATCH_CAP_USD == 20.0
    assert MONTHLY_CAP_USD == 100.0

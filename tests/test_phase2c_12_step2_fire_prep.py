"""PHASE2C_12 Step 2 fire-prep — 3-surface coupled patch tests.

Covers the three coupled surfaces of the Step 2 fire-prep patch:

    Surface (1) — ``PHASE2C_BATCH_SIZE`` env-var-driven
        ``STAGE2D_BATCH_SIZE`` at module-load register, parallel to Q10
        ``PHASE2C_THEME_CYCLE_LEN``. Default = 200 preserves canonical
        ``b6fcbf86`` baseline; smoke = 40, main = 198.

    Surface (2) — ``--live-critic`` CLI flag at ``main()``; threads
        through ``run_stage2d(live_critic=True)`` and instantiates
        ``LiveSonnetD7bBackend`` instead of ``StubD7bBackend``.

    Surface (3) — Ledger pre-charge wrap around ``run_critic()`` for live
        D7b calls. Closes PHASE2C_3 + PHASE2C_5 carry-forward warning at
        the same fire boundary that wires the live-critic CLI. Stub mode
        skips pre-charge to avoid $0 noise rows.

TDD-RED state: tests fail until 3-surface implementation lands at
``stage2d_batch.py``.

Binding source:
    - ``docs/phase2c/PHASE2C_12_PLAN.md`` §3.2 Q3 LOCKED (N=198 main),
      §3.3 (DSL budget), §4.1 (smoke fire-spec), §8.1 (Step 2 sequence)
    - ``docs/phase2c/PHASE2C_12_STEP1_DELIVERABLE.md`` §9.4 (Step 5 prereq
      carry-forward, re-routed to Step 2 prereq via OPEN-1 adjudication)
    - ``docs/closeout/PHASE2C_3_BATCH1.md`` §135 + ``docs/closeout/
      PHASE2C_5_PHASE1_RESULTS.md`` §214 (ledger pre-charge carry-forward)
    - CLAUDE.md "Spend ledger uses pre-flight charge pattern" + "NEVER
      perform a budget check AFTER an API call (must be pre-call)"
"""

from __future__ import annotations

import importlib
import json
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

import pytest

from agents.critic.batch_context import BatchContext as CriticBatchContext
from agents.critic.d7b_backend import D7bBackend
from agents.critic.d7b_parser import parse_d7b_response
from agents.orchestrator.budget_ledger import (
    BACKEND_KIND_D7B_CRITIC,
    BudgetLedger,
    CALL_ROLE_CRITIQUE,
)
from agents.proposer.interface import (
    BatchContext,
    ProposerOutput,
    ValidCandidate,
)
from agents.proposer.stub_backend import classify_raw_json
from factors.registry import get_registry
from strategies.dsl import StrategyDSL


MODULE_PATH = "agents.proposer.stage2d_batch"
ENV_BATCH_SIZE = "PHASE2C_BATCH_SIZE"
ENV_THEME_CYCLE_LEN = "PHASE2C_THEME_CYCLE_LEN"
ENV_SMOKE_OVERRIDE = "PHASE2C_SMOKE_THEME_OVERRIDE"


# ---------------------------------------------------------------------------
# Surface (1) — PHASE2C_BATCH_SIZE env-var-driven STAGE2D_BATCH_SIZE
# ---------------------------------------------------------------------------


@pytest.fixture
def reload_module(monkeypatch):
    """Reload stage2d_batch after mutating env vars.

    Clears all PHASE2C_* env vars on entry to avoid cross-test
    contamination. Restores canonical state on teardown so downstream
    tests in the same pytest session see ``STAGE2D_BATCH_SIZE = 200``.
    """
    monkeypatch.delenv(ENV_BATCH_SIZE, raising=False)
    monkeypatch.delenv(ENV_THEME_CYCLE_LEN, raising=False)
    monkeypatch.delenv(ENV_SMOKE_OVERRIDE, raising=False)

    def _reload():
        mod = importlib.import_module(MODULE_PATH)
        return importlib.reload(mod)

    yield _reload

    monkeypatch.delenv(ENV_BATCH_SIZE, raising=False)
    monkeypatch.delenv(ENV_THEME_CYCLE_LEN, raising=False)
    monkeypatch.delenv(ENV_SMOKE_OVERRIDE, raising=False)
    importlib.reload(importlib.import_module(MODULE_PATH))


def test_batch_size_default_200_when_unset(reload_module):
    """R3 fall-through: unset env var preserves canonical 200 baseline.

    Default = 200 preserves canonical ``b6fcbf86`` operational invariant
    (parse_rate = 0.99 = 198/200) per PHASE2C_9 Step 2 closeout.
    """
    mod = reload_module()
    assert mod.STAGE2D_BATCH_SIZE == 200


def test_batch_size_smoke_value_40(monkeypatch, reload_module):
    """Q1 LOCKED: smoke batch fire = 40 candidates per ``PHASE2C_12_PLAN.md``
    §4.1 + Step 1 deliverable §9.4 carry-forward."""
    monkeypatch.setenv(ENV_BATCH_SIZE, "40")
    mod = reload_module()
    assert mod.STAGE2D_BATCH_SIZE == 40


def test_batch_size_main_value_198(monkeypatch, reload_module):
    """Q3 LOCKED: main batch fire = 198 candidates per
    ``PHASE2C_12_PLAN.md`` §3.2 + §4.2 + §9.4 Step 5 prereq closure."""
    monkeypatch.setenv(ENV_BATCH_SIZE, "198")
    mod = reload_module()
    assert mod.STAGE2D_BATCH_SIZE == 198


@pytest.mark.parametrize("bad_value", ["0", "-1", "-198", "201", "1000"])
def test_batch_size_range_validation_raises(
    bad_value, monkeypatch, reload_module
):
    """Range validation: ``PHASE2C_BATCH_SIZE`` outside ``[1, 200]``
    raises ``ValueError`` at module-load register.

    Upper bound = 200 = canonical-baseline ``b6fcbf86`` ceiling
    (defensive-but-not-prescriptive bound; NOT hardcoded {40, 198};
    successor cycle may legitimately use other batch sizes within the
    canonical-tested range without re-modifying validation).
    """
    monkeypatch.setenv(ENV_BATCH_SIZE, bad_value)
    with pytest.raises(ValueError, match="out of range"):
        reload_module()


@pytest.mark.parametrize("bad_value", ["forty", "", "1.5", "200_"])
def test_batch_size_non_integer_raises(
    bad_value, monkeypatch, reload_module
):
    """Non-integer ``PHASE2C_BATCH_SIZE`` raises ``ValueError`` at
    module-load (parallel to Q10 ``PHASE2C_THEME_CYCLE_LEN``
    non-integer rejection)."""
    monkeypatch.setenv(ENV_BATCH_SIZE, bad_value)
    with pytest.raises(ValueError, match="not a valid integer"):
        reload_module()


@pytest.mark.parametrize(
    "good_value", ["1", "20", "40", "100", "150", "198", "200"],
)
def test_batch_size_in_bounds_loads(
    good_value, monkeypatch, reload_module
):
    """In-bounds ``PHASE2C_BATCH_SIZE`` loads without raising."""
    monkeypatch.setenv(ENV_BATCH_SIZE, good_value)
    mod = reload_module()
    assert mod.STAGE2D_BATCH_SIZE == int(good_value)


# ---------------------------------------------------------------------------
# Mock backends + helpers for Surface (2) + Surface (3)
# ---------------------------------------------------------------------------


# Use a small batch size for critic integration tests (override at runtime
# via monkeypatch.setattr to avoid full 200-call iterations).
SMALL_BATCH_SIZE = 4


class _SmallVariedProposer:
    """Stub Proposer that emits one valid DSL per call."""

    def __init__(self, registry):
        self._registry = registry
        self._n = 0

    def generate(self, context: BatchContext) -> ProposerOutput:
        self._n += 1
        dsl_dict = {
            "name": f"s_{self._n}",
            "description": f"Step2 fire-prep test variant {self._n}.",
            "entry": [{"conditions": [
                {"factor": "return_24h", "op": ">",
                 "value": round(0.01 * self._n, 4)}
            ]}],
            "exit": [{"conditions": [
                {"factor": "return_24h", "op": "<", "value": 0.0}
            ]}],
            "position_sizing": "full_equity",
            "max_hold_bars": None,
        }
        cand = classify_raw_json(
            json.dumps(dsl_dict), registry=self._registry,
        )
        return ProposerOutput(
            candidates=(cand,),
            cost_estimate_usd=0.01,
            cost_actual_usd=0.01,
            backend_name="test_step2_proposer",
            telemetry={"input_tokens": 500, "output_tokens": 100},
        )


class _FakeLiveD7bBackend(D7bBackend):
    """Fake live D7b backend: ``mode = "live"`` + canned cost data.

    Emulates ``LiveSonnetD7bBackend`` without hitting the API. Returns
    the same shape as ``StubD7bBackend.score()`` plus realistic
    ``cost_actual_usd`` so ledger pre-charge / finalize wiring can be
    exercised end-to-end in tests.
    """

    def __init__(self, *, cost_actual_usd: float = 0.012):
        self._cost = cost_actual_usd
        self.score_call_count = 0

    @property
    def mode(self):
        return "live"

    def score(self, dsl: StrategyDSL, theme: str,
              batch_context: CriticBatchContext):
        self.score_call_count += 1
        scores = {
            "semantic_plausibility": 0.7,
            "semantic_theme_alignment": 0.6,
            "structural_variant_risk": 0.3,
        }
        reasoning_text = (
            "Fake live D7b reasoning text used in unit tests to mimic "
            "the canonical Sonnet response shape and length without "
            "actually calling the Anthropic API. The schema requires at "
            "least 100 characters of reasoning, so this string is padded "
            "to satisfy that contract while remaining clearly synthetic."
        )
        _, _, scan_results = parse_d7b_response(
            json.dumps({**scores, "reasoning": reasoning_text})
        )
        metadata = {
            "raw_response_path": None,
            "cost_actual_usd": self._cost,
            "input_tokens": 800,
            "output_tokens": 200,
            "retry_count": 0,
            "scan_results": scan_results,
        }
        return scores, reasoning_text, metadata


# ---------------------------------------------------------------------------
# Surface (2) — --live-critic CLI flag wiring
# ---------------------------------------------------------------------------


@pytest.fixture
def tmp_ledger(tmp_path):
    return tmp_path / "step2_ledger.db"


@pytest.fixture
def tmp_payloads(tmp_path):
    return tmp_path / "step2_payloads"


@pytest.fixture
def small_batch(monkeypatch):
    """Override STAGE2D_BATCH_SIZE to SMALL_BATCH_SIZE for integration
    tests (avoids full 200-call iterations)."""
    import agents.proposer.stage2d_batch as mod
    monkeypatch.setattr(mod, "STAGE2D_BATCH_SIZE", SMALL_BATCH_SIZE)
    return SMALL_BATCH_SIZE


def test_run_stage2d_live_critic_false_uses_stub(
    small_batch, tmp_ledger, tmp_payloads,
):
    """``run_stage2d(with_critic=True, live_critic=False)`` uses
    StubD7bBackend by default (backward-compat with PHASE2C_3 + Step 1)."""
    from agents.proposer.stage2d_batch import run_stage2d

    registry = get_registry()
    summary = run_stage2d(
        dry_run=True,
        with_critic=True,
        live_critic=False,
        _backend=_SmallVariedProposer(registry),
        _ledger_path=tmp_ledger,
        _payload_dir=tmp_payloads,
    )
    assert summary["critic_enabled"] is True
    assert summary["d7b_mode"] == "stub"


def test_run_stage2d_live_critic_true_uses_live(
    small_batch, tmp_ledger, tmp_payloads,
):
    """``run_stage2d(with_critic=True, live_critic=True)`` instantiates
    LiveSonnetD7bBackend (or test injection) so ``d7b_mode == "live"``."""
    from agents.proposer.stage2d_batch import run_stage2d

    registry = get_registry()
    fake_live = _FakeLiveD7bBackend()
    summary = run_stage2d(
        dry_run=True,
        with_critic=True,
        live_critic=True,
        _backend=_SmallVariedProposer(registry),
        _ledger_path=tmp_ledger,
        _payload_dir=tmp_payloads,
        _d7b_backend=fake_live,
    )
    assert summary["critic_enabled"] is True
    assert summary["d7b_mode"] == "live"


def test_run_stage2d_live_critic_without_with_critic_raises(
    tmp_ledger, tmp_payloads,
):
    """``live_critic=True`` without ``with_critic=True`` is a
    config error: live D7b cannot fire if critic itself is disabled.

    Anti-fishing-license boundary at flag-interaction register-precision:
    user intent must be unambiguous (cannot enable live D7b backend
    while disabling the critic gate that would call it)."""
    from agents.proposer.stage2d_batch import run_stage2d

    with pytest.raises(ValueError, match="live_critic.*requires.*with_critic"):
        run_stage2d(
            dry_run=True,
            with_critic=False,
            live_critic=True,
            _ledger_path=tmp_ledger,
            _payload_dir=tmp_payloads,
        )


def test_main_cli_live_critic_flag_threads_through(monkeypatch):
    """CLI ``--live-critic`` parses to ``args.live_critic = True`` and
    threads through to ``run_stage2d(live_critic=True)``."""
    import sys
    import agents.proposer.stage2d_batch as mod

    captured = {}

    def _fake_run(**kwargs):
        captured.update(kwargs)
        return {"batch_id": "fake"}

    monkeypatch.setattr(mod, "run_stage2d", _fake_run)
    monkeypatch.setattr(
        sys, "argv",
        ["stage2d_batch", "--dry-run", "--with-critic", "--live-critic"],
    )
    mod.main()
    assert captured.get("live_critic") is True
    assert captured.get("with_critic") is True
    assert captured.get("dry_run") is True


# ---------------------------------------------------------------------------
# Surface (3) — Ledger pre-charge wrap around run_critic for live D7b
# ---------------------------------------------------------------------------


def _critic_pending_rows(ledger_path: Path):
    """Return all rows with ``backend_kind = 'd7b_critic'`` from the ledger."""
    import sqlite3
    with sqlite3.connect(ledger_path) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT id, batch_id, api_call_kind, backend_kind, call_role, "
            "status, estimated_cost, actual_cost, "
            "input_tokens, output_tokens, notes "
            "FROM ledger WHERE backend_kind = ? "
            "ORDER BY created_at_utc",
            (BACKEND_KIND_D7B_CRITIC,),
        ).fetchall()
    return [dict(r) for r in rows]


def test_live_critic_writes_pending_before_run_critic(
    small_batch, tmp_ledger, tmp_payloads,
):
    """For live D7b mode, ledger.write_pending MUST be called BEFORE
    run_critic for each Critic call.

    Sequencing constraint per PHASE2C_3 + PHASE2C_5 carry-forward
    warnings + CLAUDE.md "NEVER perform a budget check AFTER an API
    call (must be pre-call)"."""
    from agents.proposer.stage2d_batch import run_stage2d

    registry = get_registry()
    fake_live = _FakeLiveD7bBackend()

    call_order: list[str] = []
    real_write_pending = BudgetLedger.write_pending
    real_run_critic_module = importlib.import_module(
        "agents.critic.orchestrator"
    )
    real_run_critic = real_run_critic_module.run_critic

    def _spy_write_pending(self, *args, **kwargs):
        if kwargs.get("backend_kind") == BACKEND_KIND_D7B_CRITIC:
            call_order.append("write_pending_critic")
        return real_write_pending(self, *args, **kwargs)

    def _spy_run_critic(*args, **kwargs):
        call_order.append("run_critic")
        return real_run_critic(*args, **kwargs)

    # NB: ``run_critic`` is lazy-imported inside ``run_stage2d`` via
    # ``from agents.critic.orchestrator import run_critic``. Patching the
    # source module ``agents.critic.orchestrator.run_critic`` BEFORE the
    # import statement runs ensures the local binding picks up the spy.
    with patch.object(
        BudgetLedger, "write_pending", _spy_write_pending,
    ), patch(
        "agents.critic.orchestrator.run_critic", _spy_run_critic,
    ):
        run_stage2d(
            dry_run=True,
            with_critic=True,
            live_critic=True,
            _backend=_SmallVariedProposer(registry),
            _ledger_path=tmp_ledger,
            _payload_dir=tmp_payloads,
            _d7b_backend=fake_live,
        )

    # Assert at least one critic write_pending fired AND it preceded
    # the corresponding run_critic call (interleaved order: each critic
    # call must have its write_pending strictly before its run_critic).
    pairs = [c for c in call_order if c in (
        "write_pending_critic", "run_critic",
    )]
    assert "write_pending_critic" in pairs
    assert "run_critic" in pairs
    # First write_pending_critic must come before first run_critic.
    first_wp = pairs.index("write_pending_critic")
    first_rc = pairs.index("run_critic")
    assert first_wp < first_rc


def test_live_critic_pending_row_schema(
    small_batch, tmp_ledger, tmp_payloads,
):
    """Each live-critic ledger row carries ``backend_kind='d7b_critic'``,
    ``call_role='critique'``, and a strictly positive ``estimated_cost``
    (upper-bound pre-charge per ``D7B_STAGE2A_COST_CEILING_USD = 0.05``)."""
    from agents.proposer.stage2d_batch import run_stage2d

    registry = get_registry()
    fake_live = _FakeLiveD7bBackend(cost_actual_usd=0.012)
    run_stage2d(
        dry_run=True,
        with_critic=True,
        live_critic=True,
        _backend=_SmallVariedProposer(registry),
        _ledger_path=tmp_ledger,
        _payload_dir=tmp_payloads,
        _d7b_backend=fake_live,
    )
    rows = _critic_pending_rows(tmp_ledger)
    assert len(rows) >= 1
    for row in rows:
        assert row["backend_kind"] == BACKEND_KIND_D7B_CRITIC
        assert row["call_role"] == CALL_ROLE_CRITIQUE
        assert row["estimated_cost"] > 0
        # Upper bound = single-call cost ceiling per d7b_live.py.
        assert row["estimated_cost"] <= 0.05


def test_live_critic_marks_completed_with_actual_cost(
    small_batch, tmp_ledger, tmp_payloads,
):
    """After run_critic returns ok, ledger.finalize updates the row with
    ``status='completed'`` and the actual D7b cost from CriticResult."""
    from agents.proposer.stage2d_batch import run_stage2d

    registry = get_registry()
    fake_live = _FakeLiveD7bBackend(cost_actual_usd=0.012)
    run_stage2d(
        dry_run=True,
        with_critic=True,
        live_critic=True,
        _backend=_SmallVariedProposer(registry),
        _ledger_path=tmp_ledger,
        _payload_dir=tmp_payloads,
        _d7b_backend=fake_live,
    )
    rows = _critic_pending_rows(tmp_ledger)
    completed = [r for r in rows if r["status"] == "completed"]
    assert len(completed) >= 1
    for row in completed:
        # Actual cost from CriticResult.d7b_cost_actual_usd
        # (FakeLiveD7bBackend returns 0.012 per call).
        assert row["actual_cost"] == pytest.approx(0.012, rel=1e-6)
        assert row["input_tokens"] == 800
        assert row["output_tokens"] == 200


def test_live_critic_marks_crashed_on_finalize_exception(
    small_batch, tmp_ledger, tmp_payloads,
):
    """If finalize() raises after a successful run_critic, the pending
    row is marked crashed (best-effort) so the pre-charge accounting
    remains explicit (crashed rows still count as spent)."""
    from agents.proposer.stage2d_batch import run_stage2d

    registry = get_registry()
    fake_live = _FakeLiveD7bBackend(cost_actual_usd=0.012)

    real_finalize = BudgetLedger.finalize
    flaked_critic_count = {"n": 0}

    def _flaky_finalize(self, row_id, *, actual_cost_usd, **kwargs):
        # Only flake the FIRST critic finalize; pass through proposer
        # finalizes and subsequent critic finalizes. Look up the row's
        # backend_kind directly from the ledger to discriminate.
        import sqlite3
        with sqlite3.connect(tmp_ledger) as conn:
            row = conn.execute(
                "SELECT backend_kind FROM ledger WHERE id = ?", (row_id,),
            ).fetchone()
        backend_kind = row[0] if row else None
        if (
            backend_kind == BACKEND_KIND_D7B_CRITIC
            and flaked_critic_count["n"] == 0
        ):
            flaked_critic_count["n"] += 1
            raise RuntimeError("simulated critic finalize failure")
        return real_finalize(
            self, row_id, actual_cost_usd=actual_cost_usd, **kwargs,
        )

    with patch.object(BudgetLedger, "finalize", _flaky_finalize):
        # The wrapper must catch the finalize exception and call
        # mark_crashed; the run continues (per critic fail-open).
        run_stage2d(
            dry_run=True,
            with_critic=True,
            live_critic=True,
            _backend=_SmallVariedProposer(registry),
            _ledger_path=tmp_ledger,
            _payload_dir=tmp_payloads,
            _d7b_backend=fake_live,
        )
    rows = _critic_pending_rows(tmp_ledger)
    crashed = [r for r in rows if r["status"] == "crashed"]
    # At least the first row should be marked crashed.
    assert len(crashed) >= 1
    # Crashed rows still count at estimated_cost (pre-charge invariant).
    for row in crashed:
        assert row["estimated_cost"] > 0


def test_stub_critic_skips_pre_charge(
    small_batch, tmp_ledger, tmp_payloads,
):
    """Stub D7b mode (cost = $0) MUST NOT write critic ledger rows.

    Regression guard: writing $0 pending rows for stub critic would
    pollute the ledger with no-op rows and violate the 'pre-charge for
    real spend' invariant. Only live D7b calls write critic pending rows.
    """
    from agents.proposer.stage2d_batch import run_stage2d

    registry = get_registry()
    run_stage2d(
        dry_run=True,
        with_critic=True,
        live_critic=False,
        _backend=_SmallVariedProposer(registry),
        _ledger_path=tmp_ledger,
        _payload_dir=tmp_payloads,
    )
    rows = _critic_pending_rows(tmp_ledger)
    assert len(rows) == 0, (
        f"Stub critic mode wrote {len(rows)} ledger rows; expected 0"
    )

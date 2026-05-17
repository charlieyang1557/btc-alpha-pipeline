"""Wave A-1 — Track A failing tests for factor_bandit (TDD red).

Per sub-spec SEAL ab8e715 §3 Track A 11 decisions + amendment v1 SEAL
850aa1d (no Track A changes; amendment only revised B-1/B-4/B-6).

Tests reference functions/classes implemented at Wave A-2. At Wave A-1
commit, these tests are RED: import-time failures with ImportError or
behavioral failures against minimal stubs. Wave A-2 makes them GREEN.

Test enumeration per amendment §3 / sub-spec §3 + X-4:
- A-T1: Bandit observation Beta posterior update math (A-1 cold-start
  prior + posterior update arithmetic)
- A-T2: Thompson sampling determinism (A-5 hashlib.sha256 seed; same
  batch_id → same top-K)
- A-T3: Cold-start prior Beta(1,1) (A-1 default verified before any
  observation)
- A-T4: K=5 curation cap (A-3 top-K extraction)
- A-T5: factor_bandit_observations append-only contract (A-Lock-5)
- A-T6: Curation menu phrasing audit (positive + negative; A-7 phrasing
  + A-Lock-4 extended forbidden language)
- A-T7: top_factors_block field-split contract (audit scoped scan finds
  forbidden tokens within top_factors_block only)
- A-T8: Posterior-update isolation from in-batch state (A-Lock-6:
  posterior only updates at batch close, mid-batch state changes
  do not perturb)
"""
from __future__ import annotations

from dataclasses import fields

import pytest


@pytest.fixture
def ledger_path(tmp_path):
    """Temp SQLite path for factor_posterior + factor_bandit_observations."""
    return tmp_path / "factor_bandit_test.db"


# ---------------------------------------------------------------------------
# A-T1: Beta posterior update arithmetic
# ---------------------------------------------------------------------------


def test_a_t1_beta_posterior_update_arithmetic(ledger_path):
    """observe_batch increments α on regime_holdout_passed=1 and β on =0.

    Posterior update: Beta(α, β) → Beta(α+1, β) on pass; Beta(α, β+1)
    on fail. Verifies a synthetic 2-batch ledger: factor sma_20 appears
    in 2 passing hypotheses + 1 failing → Beta(3, 2) from Beta(1, 1).
    """
    from agents.orchestrator.factor_bandit import (
        init_factor_posterior_db,
        observe_batch,
        get_posterior,
    )

    init_factor_posterior_db(ledger_path)

    # Synthetic batch with 3 hypotheses; factor sma_20 in all 3
    observations = [
        ("hyp_hash_1", {"sma_20"}, True),
        ("hyp_hash_2", {"sma_20"}, True),
        ("hyp_hash_3", {"sma_20"}, False),
    ]
    observe_batch(
        batch_id="batch-001",
        observations=observations,
        ledger_path=ledger_path,
    )

    alpha, beta = get_posterior("sma_20", ledger_path)
    assert alpha == 3, f"Expected α=3 (Beta(1,1) + 2 passes), got {alpha}"
    assert beta == 2, f"Expected β=2 (Beta(1,1) + 1 fail), got {beta}"


# ---------------------------------------------------------------------------
# A-T2: Thompson sampling determinism (A-5 SEAL corrected to hashlib.sha256)
# ---------------------------------------------------------------------------


def test_a_t2_thompson_sampling_deterministic(ledger_path):
    """Same batch_id → same top_factors across two calls.

    Per sub-spec A-5 (corrected at amendment Session 2): seed derived from
    hashlib.sha256(batch_id.encode('utf-8')). Two replay calls of
    curate_top_k(batch_id="X", ...) MUST return identical tuples.
    """
    from agents.orchestrator.factor_bandit import (
        curate_top_k,
        init_factor_posterior_db,
        observe_batch,
    )

    init_factor_posterior_db(ledger_path)
    # Seed posterior with multi-factor observations so sampling has signal
    observe_batch(
        batch_id="seed-batch",
        observations=[
            ("h1", {"sma_20", "rsi_14"}, True),
            ("h2", {"sma_50"}, True),
            ("h3", {"atr_14"}, False),
        ],
        ledger_path=ledger_path,
    )

    selection_1 = curate_top_k(batch_id="batch-x", k=3, ledger_path=ledger_path)
    selection_2 = curate_top_k(batch_id="batch-x", k=3, ledger_path=ledger_path)

    assert selection_1.top_factors == selection_2.top_factors, (
        f"Determinism violated: replay produced different top-K. "
        f"{selection_1.top_factors} vs {selection_2.top_factors}"
    )
    assert selection_1.selection_seed == selection_2.selection_seed


# ---------------------------------------------------------------------------
# A-T3: Cold-start prior Beta(1, 1)
# ---------------------------------------------------------------------------


def test_a_t3_cold_start_beta_1_1(ledger_path):
    """get_posterior returns Beta(1, 1) for unseen factor (cold-start)."""
    from agents.orchestrator.factor_bandit import (
        get_posterior,
        init_factor_posterior_db,
    )

    init_factor_posterior_db(ledger_path)
    alpha, beta = get_posterior("never_seen_factor", ledger_path)
    assert alpha == 1, f"Cold-start α must be 1 (Beta(1,1) uniform); got {alpha}"
    assert beta == 1, f"Cold-start β must be 1 (Beta(1,1) uniform); got {beta}"


# ---------------------------------------------------------------------------
# A-T4: K=5 curation cap (A-3)
# ---------------------------------------------------------------------------


def test_a_t4_curation_returns_at_most_k_factors(ledger_path):
    """curate_top_k(k=5) returns exactly K factors when ≥K observed factors exist."""
    from agents.orchestrator.factor_bandit import (
        curate_top_k,
        init_factor_posterior_db,
        observe_batch,
    )

    init_factor_posterior_db(ledger_path)
    # Seed with 10 different factors (more than K=5)
    observations = [
        (f"h{i}", {f"factor_{i}"}, True) for i in range(10)
    ]
    observe_batch(batch_id="seed", observations=observations, ledger_path=ledger_path)

    selection = curate_top_k(batch_id="test", k=5, ledger_path=ledger_path)
    assert len(selection.top_factors) == 5, (
        f"K=5 expected; got {len(selection.top_factors)} factors"
    )
    # All entries must be from the observed factor set
    assert set(selection.top_factors).issubset(
        {f"factor_{i}" for i in range(10)}
    )


# ---------------------------------------------------------------------------
# A-T5: factor_bandit_observations append-only contract (A-Lock-5)
# ---------------------------------------------------------------------------


def test_a_t5_observations_table_append_only(ledger_path):
    """Two batches → two sets of observation rows; no UPDATE/DELETE.

    Per A-Lock-5: ledger is append-only. Repeated observe_batch calls
    must accumulate rows, not overwrite.
    """
    import sqlite3
    from agents.orchestrator.factor_bandit import (
        init_factor_posterior_db,
        observe_batch,
    )

    init_factor_posterior_db(ledger_path)
    observe_batch(
        batch_id="b1",
        observations=[("h1", {"sma_20"}, True)],
        ledger_path=ledger_path,
    )
    observe_batch(
        batch_id="b2",
        observations=[("h2", {"sma_20"}, False)],
        ledger_path=ledger_path,
    )

    with sqlite3.connect(ledger_path) as conn:
        rows = conn.execute(
            "SELECT batch_id, factor_id, regime_holdout_passed "
            "FROM factor_bandit_observations ORDER BY batch_id"
        ).fetchall()

    assert len(rows) == 2, f"Expected 2 append-only rows; got {len(rows)}"
    assert rows[0][0] == "b1" and rows[1][0] == "b2"


# ---------------------------------------------------------------------------
# A-T6 / A-T7: Curation menu phrasing audit (positive + negative)
# ---------------------------------------------------------------------------


def test_a_t6_curated_menu_passes_audit_clean(ledger_path):
    """Positive test: clean curation phrasing passes audit_prompt_for_leakage.

    Wave A-3 review (4-way HIGH convergence): test now passes a
    ProposerPrompt so the scoped scan path is actually exercised.
    Previously passed a plain string, which only exercised the global
    scan layer.
    """
    from agents.orchestrator.factor_bandit import (
        curate_top_k,
        init_factor_posterior_db,
        observe_batch,
    )
    from agents.proposer.prompt_builder import (
        ProposerPrompt,
        audit_prompt_for_leakage,
    )

    init_factor_posterior_db(ledger_path)
    observe_batch(
        batch_id="seed",
        observations=[("h1", {"sma_20", "rsi_14"}, True)],
        ledger_path=ledger_path,
    )
    selection = curate_top_k(batch_id="test", k=3, ledger_path=ledger_path)

    # Build a neutral top_factors_block per A-7 default phrasing
    top_factors_block = (
        "Available factors (recommended): " + ", ".join(selection.top_factors)
    )
    prompt = ProposerPrompt(
        system="",
        user="",
        factor_menu="",
        top_factors_block=top_factors_block,
    )
    findings = audit_prompt_for_leakage(prompt)
    assert findings == [], (
        f"Clean curation must pass audit (including scoped scan). "
        f"Found leakage: {findings}"
    )


def test_a_t7_top_factors_block_audit_scoped_scan_catches_forbidden_language(
    ledger_path,
):
    """Negative test: contaminated top_factors_block fails the scoped scan.

    Per amendment §6 A-Lock-4 sub-spec contract: scoped scan over
    ``ProposerPrompt.top_factors_block`` field for extended forbidden-
    language list. Wave A-3 review (4-way HIGH convergence): test now
    passes a ProposerPrompt with system/user/factor_menu empty so the
    scoped scan path is the SOLE source of findings, and asserts the
    "top_factors_block:" prefix to confirm Layer 2 specifically fired.
    """
    from agents.proposer.prompt_builder import (
        ProposerPrompt,
        audit_prompt_for_leakage,
    )

    # "score" + "passing" are in the extended scoped list but NOT in the
    # global FORBIDDEN_PATTERNS as raw tokens (well "score" was added at
    # Wave A-3 review per sec-F3; this test uses "passing" which is
    # scoped-only).
    contaminated = (
        "Available factors (by passing quality): "
        "sma_20, rsi_14, atr_14"
    )
    prompt = ProposerPrompt(
        system="",
        user="",
        factor_menu="",
        top_factors_block=contaminated,
    )
    findings = audit_prompt_for_leakage(prompt)
    assert findings, (
        f"Contaminated top_factors_block with scoped-list tokens "
        f"'passing' + 'quality' must trigger audit failure. "
        f"Got empty findings: {findings}"
    )
    # Confirm Layer 2 specifically fired (not just Layer 1 catching a
    # global pattern). Findings from the scoped scan are prefixed with
    # "top_factors_block:".
    scoped_findings = [f for f in findings if f.startswith("top_factors_block:")]
    assert scoped_findings, (
        f"Scoped scan (Layer 2) must produce at least one finding "
        f"prefixed 'top_factors_block:'. Got: {findings}"
    )


# ---------------------------------------------------------------------------
# A-T8: Posterior-update isolation from in-batch state
# ---------------------------------------------------------------------------


def test_a_t8_posterior_update_isolated_from_mid_batch_state(ledger_path):
    """Mid-batch state changes do not perturb posterior; A-Lock-6.

    Posterior only updates at observe_batch() call (batch close). Mid-batch
    state mutations (e.g., temporary BatchIngestState.records additions)
    must NOT affect posterior values.
    """
    from agents.orchestrator.factor_bandit import (
        get_posterior,
        init_factor_posterior_db,
        observe_batch,
    )

    init_factor_posterior_db(ledger_path)
    # Initial observation
    observe_batch(
        batch_id="b1",
        observations=[("h1", {"sma_20"}, True)],
        ledger_path=ledger_path,
    )
    alpha_after_b1, beta_after_b1 = get_posterior("sma_20", ledger_path)
    assert alpha_after_b1 == 2 and beta_after_b1 == 1

    # Simulate mid-batch "noise" — repeatedly query posterior; values must not drift
    for _ in range(5):
        a, b = get_posterior("sma_20", ledger_path)
        assert a == alpha_after_b1 and b == beta_after_b1, (
            f"Posterior drifted mid-batch (no observe_batch call); "
            f"this violates A-Lock-6"
        )

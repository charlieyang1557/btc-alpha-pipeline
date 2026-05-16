"""Wave 0 W0.1 shape-lock tests for Phase 2.5 bandit + dedup work.

Per sub-spec SEAL ab8e715 §1.0-§1.3 + §2 + §6 A-Lock-4 SPLIT:
- BatchIngestState gains embedding_cache field (Track B; X-1)
- NEAR_DUPLICATE state + tuple membership (X-2)
- BatchBanditSelection frozen dataclass (Track A; §1.2)
- ProposerPrompt gains top_factors_block field (§6 A-Lock-4 SPLIT)

These tests assert the SHAPE only. Behavioral wiring of A-Lock-4 SPLIT
(audit_prompt_for_leakage scoped scan + build_prompt extraction) is
Wave A-2 work; this Wave 0 W0.1 commit locks the field shape so
downstream waves can develop in parallel.
"""
from __future__ import annotations

from dataclasses import fields, is_dataclass

import pytest


def test_batch_ingest_state_field_set():
    """BatchIngestState has exactly 6 fields after Wave 0 W0.1.

    Track A adds zero fields (bandit state in factor_posterior SQLite table).
    Track B adds one field (embedding_cache per B-Lock-5).
    """
    from agents.orchestrator.ingest import BatchIngestState

    expected_fields = {
        "batch_id",
        "hypotheses_attempted",
        "seen_hashes",
        "lifecycle_counts",
        "records",
        "embedding_cache",
    }
    actual_fields = {f.name for f in fields(BatchIngestState)}
    assert actual_fields == expected_fields, (
        f"BatchIngestState shape drift: "
        f"unexpected={actual_fields - expected_fields}, "
        f"missing={expected_fields - actual_fields}"
    )


def test_near_duplicate_constant_exists():
    """NEAR_DUPLICATE constant defined per sub-spec §2 X-2 (i)/(ii)."""
    from agents.orchestrator import ingest

    assert hasattr(ingest, "NEAR_DUPLICATE"), (
        "NEAR_DUPLICATE constant must be defined in agents.orchestrator.ingest"
    )
    assert ingest.NEAR_DUPLICATE == "near_duplicate", (
        f"NEAR_DUPLICATE must equal 'near_duplicate', got {ingest.NEAR_DUPLICATE!r}"
    )


def test_near_duplicate_in_lifecycle_states():
    """NEAR_DUPLICATE joins D6_STAGE1_LIFECYCLE_STATES per X-2 (ii) SEAL adjudication."""
    from agents.orchestrator.ingest import (
        D6_STAGE1_LIFECYCLE_STATES,
        NEAR_DUPLICATE,
    )

    assert NEAR_DUPLICATE in D6_STAGE1_LIFECYCLE_STATES, (
        f"NEAR_DUPLICATE must be in D6_STAGE1_LIFECYCLE_STATES tuple. "
        f"Current tuple: {D6_STAGE1_LIFECYCLE_STATES}"
    )


def test_batch_bandit_selection_dataclass():
    """BatchBanditSelection frozen dataclass per sub-spec §1.2."""
    from agents.orchestrator.factor_bandit import BatchBanditSelection

    assert is_dataclass(BatchBanditSelection), (
        "BatchBanditSelection must be a dataclass"
    )

    expected_fields = {"batch_id", "top_factors", "selection_seed"}
    actual_fields = {f.name for f in fields(BatchBanditSelection)}
    assert actual_fields == expected_fields, (
        f"BatchBanditSelection fields drift: "
        f"unexpected={actual_fields - expected_fields}, "
        f"missing={expected_fields - actual_fields}"
    )

    # Verify frozen (raises FrozenInstanceError on mutation attempt)
    instance = BatchBanditSelection(
        batch_id="test-batch", top_factors=("sma_20",), selection_seed=42
    )
    with pytest.raises(Exception):  # FrozenInstanceError
        instance.batch_id = "mutated"  # type: ignore[misc]


def test_proposer_prompt_top_factors_block_field():
    """ProposerPrompt has top_factors_block field per sub-spec §6 A-Lock-4 SPLIT.

    Shape only at Wave 0 W0.1; behavioral wiring (build_prompt extraction +
    audit_prompt_for_leakage scoped scan) is Wave A-2.
    """
    from agents.proposer.prompt_builder import ProposerPrompt

    field_names = {f.name for f in fields(ProposerPrompt)}
    assert "top_factors_block" in field_names, (
        f"ProposerPrompt must have top_factors_block field. "
        f"Current fields: {field_names}"
    )

    # Verify default is empty string + frozen-compatible
    prompt = ProposerPrompt(system="sys", user="usr", factor_menu="menu")
    assert prompt.top_factors_block == "", (
        f"top_factors_block default must be empty string, "
        f"got {prompt.top_factors_block!r}"
    )

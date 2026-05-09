"""Tests for Phase 4 forward_2026 regime configuration.

Per docs/superpowers/plans/2026-05-09-phase4-implementation-arc.md Task 2.

TDD-RED state: 4 new-feature tests should FAIL until forward_2026 is
added to environments.yaml + both mappings in wf_lineage.py. 2 regression
sentinel tests should PASS at TDD-RED state (they assert the IMMUTABLE
shape of splits: namespace + cross-mapping invariant — they function as
tripwires for any future cycle attempting to mutate splits or add to one
mapping but not the other).
"""
from __future__ import annotations

from pathlib import Path

import yaml

from backtest.wf_lineage import (
    ARTIFACT_SCHEMA_VERSION_PHASE2C_7_1,
    REGIME_KEY_LABEL_MAPPING,
    REGIME_KEY_TO_SCHEMA_VERSION_MAPPING,
    regime_key_to_schema_version,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENVIRONMENTS_YAML = PROJECT_ROOT / "config" / "environments.yaml"
FORWARD_2026_KEY = "evaluation_regimes.forward_2026"


# ---------------------------------------------------------------------------
# New-feature TDD-RED tests (4): expected to FAIL until Steps 3-4 complete.
# ---------------------------------------------------------------------------


def test_environments_yaml_contains_forward_2026_block():
    """The forward_2026 block must exist in evaluation_regimes namespace."""
    with open(ENVIRONMENTS_YAML) as f:
        config = yaml.safe_load(f)
    assert "evaluation_regimes" in config
    assert "forward_2026" in config["evaluation_regimes"], (
        "PHASE4_PLAN §1.2 requires forward_2026 evaluation regime; "
        "expected additive block under evaluation_regimes namespace."
    )


def test_forward_2026_block_has_required_fields():
    """The forward_2026 block must have start, label, and arc_of_origin.

    end is null at PLAN cycle; T_end captured at fire-time per PHASE4_PLAN §1.2.
    """
    with open(ENVIRONMENTS_YAML) as f:
        config = yaml.safe_load(f)
    block = config["evaluation_regimes"]["forward_2026"]
    assert block["start"] == "2026-01-01"
    assert block["label"] == "forward_2026"
    assert block["arc_of_origin"] == "PHASE4"
    # end is null at PLAN cycle; captured at fire-time per PHASE4_PLAN §1.2
    assert block.get("end") is None


def test_forward_2026_regime_key_in_label_mapping():
    """REGIME_KEY_LABEL_MAPPING must include forward_2026 -> 'forward_2026'."""
    assert FORWARD_2026_KEY in REGIME_KEY_LABEL_MAPPING, (
        "Step 4 of Task 2: add forward_2026 to REGIME_KEY_LABEL_MAPPING "
        "in backtest/wf_lineage.py."
    )
    assert REGIME_KEY_LABEL_MAPPING[FORWARD_2026_KEY] == "forward_2026"


def test_forward_2026_schema_discriminator_is_phase2c_7_1():
    """Fully-out-of-sample register: phase2c_7_1, NOT phase2c_8_1.

    Forward_2026 is parallel to bear_2022 + validation_2024 (training
    windows end 2021-12-31 + 2023-12-31; forward_2026 starts 2026-01-01;
    no overlap). Distinct from eval_2020/2021 train-overlap (phase2c_8_1).
    """
    schema = regime_key_to_schema_version(FORWARD_2026_KEY)
    assert schema == ARTIFACT_SCHEMA_VERSION_PHASE2C_7_1
    # Parallel to bear_2022 + validation_2024 (also fully-out-of-sample)
    assert (
        REGIME_KEY_TO_SCHEMA_VERSION_MAPPING[FORWARD_2026_KEY]
        == REGIME_KEY_TO_SCHEMA_VERSION_MAPPING["v2.regime_holdout"]
    )


# ---------------------------------------------------------------------------
# Regression sentinel tests (2): expected to PASS at TDD-RED state.
# Function as tripwires for any future cycle that mutates splits or
# breaks cross-mapping invariant.
# ---------------------------------------------------------------------------


def test_forward_2026_does_not_alter_immutable_splits():
    """Regression sentinel: the additive modification must NOT touch splits namespace.

    splits: train_windows + regime_holdout + validation + test + live_forward
    are immutable per CLAUDE.md hard rule. Phase 4 modification adds ONLY
    to evaluation_regimes namespace.
    """
    with open(ENVIRONMENTS_YAML) as f:
        config = yaml.safe_load(f)
    splits = config["splits"]
    # train_windows immutable (PHASE2A v2)
    assert splits["train_windows"] == [
        ["2020-01-01", "2021-12-31"],
        ["2023-01-01", "2023-12-31"],
    ]
    # regime_holdout immutable
    assert splits["regime_holdout"]["start"] == "2022-01-01"
    assert splits["regime_holdout"]["end"] == "2022-12-31"
    assert splits["regime_holdout"]["label"] == "bear_2022"
    # validation immutable
    assert splits["validation"]["start"] == "2024-01-01"
    assert splits["validation"]["end"] == "2024-12-31"
    # test window immutable
    assert splits["test"]["start"] == "2025-01-01"
    assert splits["test"]["end"] == "2025-12-31"
    # live_forward placeholder immutable
    assert splits["live_forward"]["start"] == "2026-01-01"
    assert splits["live_forward"]["end"] is None


def test_cross_mapping_invariant_holds():
    """Regression sentinel: every regime_key in label mapping must be in schema mapping.

    Documented at backtest/wf_lineage.py:116-118: 'every regime_key in
    REGIME_KEY_LABEL_MAPPING must also be in REGIME_KEY_TO_SCHEMA_VERSION_MAPPING.
    Future arcs adding new regimes update both mappings together.'

    This sentinel catches any future cycle that adds to one mapping but
    not the other (transient state during sequential mid-implementation
    edits would break this invariant).
    """
    assert set(REGIME_KEY_LABEL_MAPPING.keys()) == set(
        REGIME_KEY_TO_SCHEMA_VERSION_MAPPING.keys()
    )

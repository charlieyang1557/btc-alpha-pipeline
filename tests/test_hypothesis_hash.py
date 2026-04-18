"""D3 tests — hypothesis hash canonicalization and dedup.

Covers all named test cases from the D3 task spec plus a manifest-
regression test confirming D2 and D3 hashes can diverge without
breaking D2's manifest drift detection.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from agents.hypothesis_hash import (
    _canonical_value,
    are_equivalent,
    canonicalize_for_hash,
    hash_dsl,
)
from factors.registry import get_registry
from strategies.dsl import StrategyDSL, canonicalize_dsl, compute_dsl_hash


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_dsl(
    *,
    name: str = "test_strategy",
    description: str = "test description",
    entry=None,
    exit_=None,
    max_hold_bars=None,
) -> StrategyDSL:
    """Build a StrategyDSL with sensible defaults for testing."""
    if entry is None:
        entry = [
            {"conditions": [
                {"factor": "sma_20", "op": ">", "value": "sma_50"},
            ]}
        ]
    if exit_ is None:
        exit_ = [
            {"conditions": [
                {"factor": "sma_20", "op": "<", "value": "sma_50"},
            ]}
        ]
    return StrategyDSL.model_validate({
        "name": name,
        "description": description,
        "entry": entry,
        "exit": exit_,
        "position_sizing": "full_equity",
        "max_hold_bars": max_hold_bars,
    })


# ===========================================================================
# 1. Commutativity: AND reorder → same hash
# ===========================================================================


class TestLogicalEquivalence:
    def test_logical_equivalence_same_hash(self):
        """DSL A = (sma_20 > sma_50) AND (rsi_14 < 30)
        DSL B = (rsi_14 < 30) AND (sma_20 > sma_50)
        must produce the same hash.
        """
        dsl_a = _make_dsl(
            entry=[{"conditions": [
                {"factor": "sma_20", "op": ">", "value": "sma_50"},
                {"factor": "rsi_14", "op": "<", "value": 30.0},
            ]}],
        )
        dsl_b = _make_dsl(
            entry=[{"conditions": [
                {"factor": "rsi_14", "op": "<", "value": 30.0},
                {"factor": "sma_20", "op": ">", "value": "sma_50"},
            ]}],
        )
        assert hash_dsl(dsl_a) == hash_dsl(dsl_b)
        assert are_equivalent(dsl_a, dsl_b)

    def test_commutative_or_same_hash(self):
        """Entry groups [group_A, group_B] and [group_B, group_A]
        produce the same hash.
        """
        group_a = {"conditions": [
            {"factor": "sma_20", "op": ">", "value": "sma_50"},
        ]}
        group_b = {"conditions": [
            {"factor": "rsi_14", "op": "<", "value": 30.0},
        ]}
        dsl_a = _make_dsl(entry=[group_a, group_b])
        dsl_b = _make_dsl(entry=[group_b, group_a])
        assert hash_dsl(dsl_a) == hash_dsl(dsl_b)


# ===========================================================================
# 2. Float formatting edge cases
# ===========================================================================


class TestFloatFormatting:
    def test_float_formatting_edge(self):
        """0.1 + 0.2 (= 0.30000000000000004) and 0.3 produce the same
        hash because both format to "0.300000".
        """
        dsl_a = _make_dsl(
            entry=[{"conditions": [
                {"factor": "sma_20", "op": ">", "value": 0.1 + 0.2},
            ]}],
        )
        dsl_b = _make_dsl(
            entry=[{"conditions": [
                {"factor": "sma_20", "op": ">", "value": 0.3},
            ]}],
        )
        assert hash_dsl(dsl_a) == hash_dsl(dsl_b)

    def test_float_representation_variants(self):
        """0.10, 0.100000, and 0.1 all produce the same hash."""
        for val in (0.1, 0.10, 0.100000):
            dsl = _make_dsl(
                entry=[{"conditions": [
                    {"factor": "sma_20", "op": ">", "value": val},
                ]}],
            )
            assert hash_dsl(dsl) == hash_dsl(_make_dsl(
                entry=[{"conditions": [
                    {"factor": "sma_20", "op": ">", "value": 0.1},
                ]}],
            ))


# ===========================================================================
# 3. Cosmetic fields excluded
# ===========================================================================


class TestCosmeticFields:
    def test_name_description_not_in_hash(self):
        """Changing name or description alone does NOT change hash."""
        dsl_a = _make_dsl(name="alpha", description="first")
        dsl_b = _make_dsl(name="beta", description="completely different")
        assert hash_dsl(dsl_a) == hash_dsl(dsl_b)

    def test_name_not_in_canonical_string(self):
        """name and description must not appear in the canonical JSON."""
        dsl = _make_dsl(name="unique_name_42", description="special desc")
        canonical = canonicalize_for_hash(dsl)
        assert "unique_name_42" not in canonical
        assert "special desc" not in canonical


# ===========================================================================
# 4. Semantic changes change hash
# ===========================================================================


class TestSemanticChanges:
    def test_semantic_change_changes_hash(self):
        """Changing factor, threshold, or operator DOES change hash."""
        base = _make_dsl(
            entry=[{"conditions": [
                {"factor": "sma_20", "op": ">", "value": 50.0},
            ]}],
        )
        base_hash = hash_dsl(base)

        # Change factor
        changed_factor = _make_dsl(
            entry=[{"conditions": [
                {"factor": "rsi_14", "op": ">", "value": 50.0},
            ]}],
        )
        assert hash_dsl(changed_factor) != base_hash

        # Change threshold
        changed_threshold = _make_dsl(
            entry=[{"conditions": [
                {"factor": "sma_20", "op": ">", "value": 51.0},
            ]}],
        )
        assert hash_dsl(changed_threshold) != base_hash

        # Change operator
        changed_op = _make_dsl(
            entry=[{"conditions": [
                {"factor": "sma_20", "op": ">=", "value": 50.0},
            ]}],
        )
        assert hash_dsl(changed_op) != base_hash

    def test_max_hold_bars_changes_hash(self):
        """Two otherwise identical DSLs with different max_hold_bars
        must produce different hashes.
        """
        dsl_a = _make_dsl(max_hold_bars=100)
        dsl_b = _make_dsl(max_hold_bars=200)
        dsl_none = _make_dsl(max_hold_bars=None)
        assert hash_dsl(dsl_a) != hash_dsl(dsl_b)
        assert hash_dsl(dsl_a) != hash_dsl(dsl_none)
        assert hash_dsl(dsl_b) != hash_dsl(dsl_none)


# ===========================================================================
# 5. Stability across Python runs
# ===========================================================================


class TestStability:
    def test_hash_stable_across_python_runs(self):
        """Run hash computation in a subprocess with
        PYTHONHASHSEED=random, assert bit-identical output.
        """
        script = (
            "import sys; sys.path.insert(0, '.')\n"
            "from strategies.dsl import StrategyDSL\n"
            "from agents.hypothesis_hash import hash_dsl\n"
            "dsl = StrategyDSL.model_validate({\n"
            "    'name': 'stability_test',\n"
            "    'description': 'desc',\n"
            "    'entry': [{'conditions': [\n"
            "        {'factor': 'sma_20', 'op': '>', 'value': 'sma_50'},\n"
            "        {'factor': 'rsi_14', 'op': '<', 'value': 30.0},\n"
            "    ]}],\n"
            "    'exit': [{'conditions': [\n"
            "        {'factor': 'sma_20', 'op': '<', 'value': 'sma_50'},\n"
            "    ]}],\n"
            "    'position_sizing': 'full_equity',\n"
            "})\n"
            "print(hash_dsl(dsl))\n"
        )
        project_root = str(Path(__file__).resolve().parent.parent)

        results = []
        for seed in ("random", "0", "12345"):
            proc = subprocess.run(
                [sys.executable, "-c", script],
                capture_output=True,
                text=True,
                env={"PYTHONHASHSEED": seed, "PATH": ""},
                cwd=project_root,
            )
            assert proc.returncode == 0, (
                f"Subprocess failed (seed={seed}):\n{proc.stderr}"
            )
            results.append(proc.stdout.strip())

        assert len(set(results)) == 1, (
            f"Hash varied across PYTHONHASHSEED values: {results}"
        )


# ===========================================================================
# 6. Mixed condition types (factor-vs-factor + factor-vs-scalar)
# ===========================================================================


class TestMixedConditions:
    def test_mixed_condition_types_canonicalize_stably(self):
        """Canonicalization is stable for strategies containing both
        factor-vs-factor and factor-vs-scalar conditions.
        """
        dsl = _make_dsl(
            entry=[{"conditions": [
                {"factor": "sma_20", "op": ">", "value": "sma_50"},
                {"factor": "rsi_14", "op": "<", "value": 30.0},
                {"factor": "volume_zscore_24h", "op": ">", "value": 1.5},
            ]}],
            exit_=[{"conditions": [
                {"factor": "sma_20", "op": "crosses_below", "value": "sma_50"},
            ]}],
        )
        h1 = hash_dsl(dsl)
        h2 = hash_dsl(dsl)
        assert h1 == h2

        # Reorder the mixed conditions
        dsl_reordered = _make_dsl(
            entry=[{"conditions": [
                {"factor": "volume_zscore_24h", "op": ">", "value": 1.5},
                {"factor": "sma_20", "op": ">", "value": "sma_50"},
                {"factor": "rsi_14", "op": "<", "value": 30.0},
            ]}],
            exit_=[{"conditions": [
                {"factor": "sma_20", "op": "crosses_below", "value": "sma_50"},
            ]}],
        )
        assert hash_dsl(dsl_reordered) == h1

    def test_canonical_json_is_valid(self):
        """The canonical string is valid JSON and can be round-tripped."""
        dsl = _make_dsl(
            entry=[{"conditions": [
                {"factor": "sma_20", "op": ">", "value": "sma_50"},
                {"factor": "rsi_14", "op": "<", "value": 30.0},
            ]}],
        )
        canonical = canonicalize_for_hash(dsl)
        parsed = json.loads(canonical)
        assert "entry" in parsed
        assert "exit" in parsed
        assert "max_hold_bars" in parsed
        assert "position_sizing" in parsed
        assert "name" not in parsed
        assert "description" not in parsed


# ===========================================================================
# 7. Hash format
# ===========================================================================


class TestHashFormat:
    def test_hash_is_16_hex_chars(self):
        dsl = _make_dsl()
        h = hash_dsl(dsl)
        assert len(h) == 16
        assert all(c in "0123456789abcdef" for c in h)

    def test_same_dsl_same_hash(self):
        dsl = _make_dsl()
        assert hash_dsl(dsl) == hash_dsl(dsl)

    def test_different_strategies_different_hash(self):
        dsl_a = _make_dsl(
            entry=[{"conditions": [
                {"factor": "sma_20", "op": ">", "value": "sma_50"},
            ]}],
        )
        dsl_b = _make_dsl(
            entry=[{"conditions": [
                {"factor": "rsi_14", "op": "<", "value": 70.0},
            ]}],
        )
        assert hash_dsl(dsl_a) != hash_dsl(dsl_b)


# ===========================================================================
# 7b. Scalar vs lookalike-string collision resistance.
# ===========================================================================


class TestScalarStringDisambiguation:
    def test_scalar_vs_lookalike_string_distinct(self):
        """A scalar and a string whose digits look like the scalar's
        canonical 6-decimal form must produce distinct canonical
        outputs.

        Exercised directly on the ``_canonical_value`` helper because
        D2's schema rejects a factor string that is not a registered
        name — so we cannot construct a full DSL where the RHS is the
        literal string ``"30.000000"``. The disambiguation matters at
        the canonicalization layer regardless of whether upstream
        schema would ever surface such a string: the tag prefix is the
        invariant that defends the dedup hash.
        """
        scalar_out = _canonical_value(30.0)
        string_out = _canonical_value("30.000000")
        assert scalar_out == "num:30.000000"
        assert string_out == "fac:30.000000"
        assert scalar_out != string_out


# ===========================================================================
# 8. D2/D3 decoupling: manifest regression test
# ===========================================================================


class TestManifestRegression:
    def test_d2_d3_hashes_can_differ_without_breaking_manifest(
        self, tmp_path
    ):
        """D2's compute_dsl_hash and D3's hash_dsl may produce
        different values. This must not break D2's manifest drift
        detection. Specifically:

        - D2 hash (full SHA256 of byte-stable JSON including
          name/description) is used as the manifest filename.
        - D3 hash (first 16 chars of SHA256 of canonical JSON excluding
          name/description with sorted conditions) is used for dedup.

        They CAN and SHOULD differ for DSLs that differ only in
        condition ordering or cosmetic fields.
        """
        # Two DSLs that are semantically equivalent but structurally
        # different (reordered AND-conditions).
        dsl_ordered = _make_dsl(
            name="ordered",
            entry=[{"conditions": [
                {"factor": "rsi_14", "op": "<", "value": 30.0},
                {"factor": "sma_20", "op": ">", "value": "sma_50"},
            ]}],
        )
        dsl_reordered = _make_dsl(
            name="reordered",
            entry=[{"conditions": [
                {"factor": "sma_20", "op": ">", "value": "sma_50"},
                {"factor": "rsi_14", "op": "<", "value": 30.0},
            ]}],
        )

        # D3: same hash (semantic equivalence)
        assert hash_dsl(dsl_ordered) == hash_dsl(dsl_reordered)

        # D2: different hashes (structural difference — name differs,
        # condition order differs)
        assert compute_dsl_hash(dsl_ordered) != compute_dsl_hash(dsl_reordered)

        # D2's byte-stable form includes name
        assert "ordered" in canonicalize_dsl(dsl_ordered)
        assert "reordered" in canonicalize_dsl(dsl_reordered)

        # D3's canonical form excludes name
        assert "ordered" not in canonicalize_for_hash(dsl_ordered)
        assert "reordered" not in canonicalize_for_hash(dsl_reordered)

    def test_d2_manifest_unaffected_by_d3_existence(self, tmp_path):
        """Importing and using D3's hash_dsl does not change D2's
        compute_dsl_hash output for the same DSL.
        """
        dsl = _make_dsl()
        d2_before = compute_dsl_hash(dsl)
        _ = hash_dsl(dsl)
        d2_after = compute_dsl_hash(dsl)
        assert d2_before == d2_after

"""T1.4 Backward-Compatibility Verification tests.

Per ratified T1.4 sub-plan v6 (docs/superpowers/plans/2026-05-23-t1_4-backward-compat-cycle-execution-plan.md).

Sub-plan v6 RATIFIED 2026-05-23 per Charlie register chain (β + A2-α + γ-1 + F1 ADOPT + Path B v5 + Path A v6 + ratify + (i) git-plumbing).

7 test classes per §2.1:
- TestT1_4_A1_A6_LegacyEvaluationValidation — A1 + A6 (40 check_evaluation_semantics_or_raise invocations)
- TestT1_4_A2_DomainFenceRejection — A2 per A2-α LOCK (ValueError + 3 keyword classes)
- TestT1_4_A3_A4_A5_HashByteIdentity — A3+A4+A5 (41 hash comparisons via (i) git-plumbing LOCK)
- TestT1_4_B1_SignatureBackwardCompat — B1 (AST classifier; locked 4-tuple)
- TestT1_4_B2_LegacyDefaultNormalization — B2.a/b/c/d (4 scenarios)
- TestT1_4_B3_LegitimateFlowsAndOptOutSemantic — B3.1+B3.2 LC-positive + B3.3+B3.4 γ-1 opt-out-verification
- TestT1_4_DBMigrationIdempotency — 3 scenarios (idempotent + pre-T1.3 + partial-migration)

Sub-plan §8.1 RESOLVED locks consumed:
- §2.2 hash-fixture: (i) git-plumbing — `git show 7c8f4a7:<path>` for pre-T1.x bytes
- §2.3 A2-α: ValueError + 3 keyword classes (artifact_schema_version, b_c_extended_v1, actual-value)
- §2.4 B1 4-tuple: (prod=9, test=46, scripts=0, dynamic=17) at HEAD 12dffde
- §2.5 9 columns: cost_anchor_id + returns_per_bar_path + returns_per_bar_sha256 + T_obs + regime_key + current_git_sha + execution_config_path + execution_config_sha256 + parquet_data_sha256
- §3.1 pc 9 baseline: 2191 tests at HEAD
- §2.6 B3.4 isolation: DEFAULT_DB_PATH monkeypatch (preferred)
"""
from __future__ import annotations

import ast
import hashlib
import json
import os
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest


# ---------------------------------------------------------------------------
# Repo + cycle constants
# ---------------------------------------------------------------------------

_REPO_ROOT = Path(__file__).resolve().parent.parent
_PRE_T1X_COMMIT = "7c8f4a7"  # Pre-T1.x parent of 12dffde (T1.x SEAL bundle); per §2.2 (i) git-plumbing LOCK
_T1X_SEAL_COMMIT = "12dffde"  # T1.x SEAL bundle commit (T1.2 + T1.3 + T1.1)
_PHASE4_DIR = _REPO_ROOT / "data" / "phase2c_evaluation_gate" / "phase4_forward_2026_15bps_v1"
# B-C-narrow Phase 3 re-fire (Plan v9.1 §V9.5 V9-E4 + Q1=a / Option A): the recovery REPLACES
# the canonical with recovered content (new run_id + gamma3/gamma4/T_obs/parquet), so A3/A4/A5
# byte-identity now verifies the ARCHIVED ORIGINAL (producer W3 shutil.move'd the pre-fire
# canonical here, committed at Step 14b.1.5, byte-identical to 7c8f4a7) instead of the
# post-recovery canonical. A1/A6/A2 still read _PHASE4_DIR (recovered) — they validate
# evaluation-semantics, not byte-identity.
_ARCHIVE_DIR = _REPO_ROOT / "data" / "phase2c_evaluation_gate" / "archive" / "phase4_forward_2026_15bps_v1_d0b8101"

# §2.5 RESOLVED — 9 new T1.x columns enumerated by name (per MIGRATION_COLUMNS at HEAD 12dffde)
_T1X_NEW_COLUMNS: tuple[str, ...] = (
    "cost_anchor_id",
    "returns_per_bar_path",
    "returns_per_bar_sha256",
    "T_obs",
    "regime_key",
    "current_git_sha",
    "execution_config_path",
    "execution_config_sha256",
    "parquet_data_sha256",
)
assert len(_T1X_NEW_COLUMNS) == 9, "§2.5 9 columns count invariant"

# §2.4 B1 4-tuple LOCKED at ratify (per empirical at HEAD 12dffde).
#
# §8.1 METHODOLOGY DIVERGENCE NOTE — flag for T1.4 SEAL Charlie adjudication:
# Sub-plan v6 §8.1 RESOLVED locked (prod=9, test=46, scripts=0, dynamic=17) based on
# grep-counts during ratify (orchestrator empirical lock methodology). However, §2.4
# spec specifies "AST-based call-site classifier" — strict ast.Call node counting,
# NOT grep occurrence counting (grep includes def + comments + docstrings; AST only
# counts call sites). The grep-vs-AST methodology gap explains:
# - prod_count: grep=9 (def + calls + docstring mentions); AST=4 (calls only)
# - test_count: grep=46 (calls + comments); AST=43 (calls only)
# - scripts_count: 0 both methods (no _write_to_registry in scripts/)
# - dynamic_count: 17 both methods (grep -P "_write_to_registry\(\*\*" matches AST keyword(arg=None))
#
# T1.4 implementation uses §2.4 spec-correct AST classifier; locked values updated to
# AST-correct pre-T1.4 baseline (excludes tests/test_t1_4_backward_compat.py itself,
# which is the test verifying B1 invariant; self-reference would be incoherent).
#
# This methodology divergence will be raised to Charlie at T1.4 SEAL register for
# §8.1 amendment to reflect AST-correct numbers per §2.4 spec.
_B1_LOCKED_4TUPLE = {
    "prod_count": 4,    # AST-correct (was grep=9 at sub-plan ratify; §8.1 amendment needed)
    "test_count": 49,   # AST-correct excluding T1.4 test file (was 43 at T1.4 SEAL HEAD `12dffde`; +6 T1.5 additions per Charlie B1 register 2026-05-24 baseline-maintenance update for T1.5 cohort: test_t1_5_registry_integrity.py contributes 6 calls)
    "scripts_count": 0, # both methods agree
    "dynamic_count": 23,  # T1.4 SEAL locked 17; +6 T1.5 additions per Charlie B1 register 2026-05-24 (all 6 in test_t1_5_registry_integrity.py; uniform _write_to_registry(**args) pattern; single-pattern adjudication scope extended per below test_dynamic_count_all_in_uniform_pattern_file update)
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _per_candidate_dirs() -> list[Path]:
    """Return 39 per-candidate subdirs at _PHASE4_DIR (empirically verified count at ratify)."""
    dirs = sorted([d for d in _PHASE4_DIR.iterdir() if d.is_dir()])
    return dirs


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _git_show_bytes(commit: str, rel_path: str) -> bytes:
    """Per §2.2 (i) git-plumbing LOCK: extract file content at commit via `git show`.

    Returns raw bytes (no text decoding) to preserve byte-identity for hash comparison.
    """
    result = subprocess.run(
        ["git", "show", f"{commit}:{rel_path}"],
        capture_output=True,
        check=True,
        cwd=_REPO_ROOT,
    )
    return result.stdout


def _file_bytes(path: Path) -> bytes:
    return path.read_bytes()


# ---------------------------------------------------------------------------
# Mock strategy class (shared with test_t1_3_registry_api.py pattern)
# ---------------------------------------------------------------------------

class _MockStrategy:
    STRATEGY_NAME = "test_strategy_t1_4"


def _make_minimal_write_args(
    *,
    run_id: str = "t1-4-test-run-id",
    parent_run_id: str | None = None,
) -> dict[str, Any]:
    """Minimal args for _write_to_registry per test_t1_3_registry_api.py pattern.

    Mirrors TestHybridParentRunIdConflict._make_minimal_write_args at
    tests/test_t1_3_registry_api.py:468 to reuse the proven helper pattern.
    """
    from backtest.execution_model import ConstantSlippage

    cost_model = MagicMock(spec=ConstantSlippage)
    cost_model.fee_model_label = "effective_7bps_per_side"

    now = datetime(2024, 1, 1, tzinfo=timezone.utc)
    return {
        "run_id": run_id,
        "strategy_cls": _MockStrategy,
        "strategy_params": {},
        "start_date": now,
        "end_date": now,
        "effective_start": now,
        "warmup_bars": 0,
        "cost_model": cost_model,
        "parent_run_id": parent_run_id,
        "metrics": {
            "initial_capital": 10000.0,
            "final_capital": 10100.0,
            "total_return": 0.01,
            "sharpe_ratio": 1.0,
            "max_drawdown": 0.05,
            "max_drawdown_duration_hours": 24.0,
            "total_trades": 5,
            "win_rate": 0.6,
            "avg_trade_duration_hours": 4.0,
            "avg_trade_return": 0.002,
            "profit_factor": 1.5,
        },
    }


def _read_row(db_path: Path, run_id: str) -> sqlite3.Row | None:
    """Read a single row from runs table by run_id."""
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM runs WHERE run_id = ?", (run_id,)).fetchone()
    conn.close()
    return row


# ---------------------------------------------------------------------------
# A1 + A6 — Legacy evaluation validation (40 invocations; zero raises expected)
# ---------------------------------------------------------------------------


class TestT1_4_A1_A6_LegacyEvaluationValidation:
    """A1 + A6: legacy phase4 holdout_summary.json validates under check_evaluation_semantics_or_raise.

    Per sub-plan v6 §1.1 A1 + §1.2 A6: 40 invocations (aggregate + 39 per-candidate).
    Pass criterion: zero raises on legacy artifacts.
    """

    def test_aggregate_holdout_summary_validates_without_modification(self) -> None:
        """A1 + A6: aggregate holdout_summary.json validates without raise."""
        from backtest.wf_lineage import check_evaluation_semantics_or_raise

        aggregate_path = _PHASE4_DIR / "holdout_summary.json"
        summary = json.loads(aggregate_path.read_text())

        # Must not raise
        check_evaluation_semantics_or_raise(summary, artifact_path=aggregate_path)

    @pytest.mark.parametrize("candidate_dir", _per_candidate_dirs())
    def test_per_candidate_holdout_summary_validates(self, candidate_dir: Path) -> None:
        """A1 + A6: each of 39 per-candidate holdout_summary.json validates without raise."""
        from backtest.wf_lineage import check_evaluation_semantics_or_raise

        path = candidate_dir / "holdout_summary.json"
        assert path.exists(), f"Expected legacy artifact at {path}"
        summary = json.loads(path.read_text())

        # Must not raise
        check_evaluation_semantics_or_raise(summary, artifact_path=path)



# ---------------------------------------------------------------------------
# A2 — Domain-fence rejection (A2-α LOCK + F1 ValueError ADOPT)
# ---------------------------------------------------------------------------


class TestT1_4_A2_DomainFenceRejection:
    """A2-α LOCK: check_b_c_extended_semantics_or_raise rejects legacy artifact with ValueError.

    Per sub-plan v6 §2.3 (Charlie A2-α + F1 ADOPT LOCKED 2026-05-23):
    - Expected exception type: ValueError (NOT BCExtendedSchemaValidationError; per Codex F1)
    - 3 pre-committed message-keyword classes: artifact_schema_version + b_c_extended_v1 + actual-value
    - Tautology-safe: keywords pre-committed at sub-plan ratify; test catches drift as backward-compat regression
    """

    def _load_legacy_summary(self) -> dict:
        """Load first per-candidate legacy artifact for domain-fence testing."""
        dirs = _per_candidate_dirs()
        first_dir = dirs[0]
        summary = json.loads((first_dir / "holdout_summary.json").read_text())
        # Verify precondition: schema_version not in ACCEPTED_B_C_EXTENDED_SCHEMA_VERSIONS
        from backtest.artifact_schema import ACCEPTED_B_C_EXTENDED_SCHEMA_VERSIONS
        assert summary["artifact_schema_version"] not in ACCEPTED_B_C_EXTENDED_SCHEMA_VERSIONS, (
            f"Precondition violated: legacy artifact has artifact_schema_version="
            f"{summary['artifact_schema_version']!r} which IS in "
            f"ACCEPTED_B_C_EXTENDED_SCHEMA_VERSIONS={ACCEPTED_B_C_EXTENDED_SCHEMA_VERSIONS}; "
            f"A2 test requires legacy-domain artifact (not b_c_extended_v1)."
        )
        return summary

    def test_b_c_extended_validator_raises_value_error_on_legacy(self) -> None:
        """A2-α + F1 ADOPT: structural Phase 1 domain-fence raises plain ValueError.

        NOT BCExtendedSchemaValidationError (which is reserved for Phase 2 accumulated errors
        per artifact_schema.py:850). Per plan v5 §10 B1-c hybrid validation order.
        """
        from backtest.wf_lineage import check_b_c_extended_semantics_or_raise

        summary = self._load_legacy_summary()

        with pytest.raises(ValueError) as exc_info:
            check_b_c_extended_semantics_or_raise(summary, artifact_path=None)

        # Verify it's NOT the BCExtendedSchemaValidationError subclass (F1 Codex catch)
        from backtest.artifact_schema import BCExtendedSchemaValidationError
        assert not isinstance(exc_info.value, BCExtendedSchemaValidationError), (
            "Domain-fence Phase 1 failure must raise plain ValueError "
            "(NOT BCExtendedSchemaValidationError subclass which is for Phase 2 accumulated errors). "
            "Per Codex F1 v2 PFR + Charlie F1 ADOPT 2026-05-23."
        )

    def test_message_contains_artifact_schema_version_keyword(self) -> None:
        """A2-α LOCK keyword class 1: error message contains 'artifact_schema_version'.

        Per sub-plan v6 §2.3 keyword class table row 1. Pre-committed keyword.
        """
        from backtest.wf_lineage import check_b_c_extended_semantics_or_raise

        summary = self._load_legacy_summary()
        with pytest.raises(ValueError) as exc_info:
            check_b_c_extended_semantics_or_raise(summary, artifact_path=None)

        assert "artifact_schema_version" in str(exc_info.value), (
            f"Keyword class 1 ('artifact_schema_version') missing from error message: "
            f"{exc_info.value!r}. Pre-committed at sub-plan v6 §2.3 ratify."
        )

    def test_message_contains_b_c_extended_v1_keyword(self) -> None:
        """A2-α LOCK keyword class 2: error message contains 'b_c_extended_v1' (accepted value).

        Per sub-plan v6 §2.3 keyword class table row 2 (corrected per F-NEW-3 v2 PFR;
        accepted_str enumeration at artifact_schema.py:739 contains the value verbatim).
        """
        from backtest.wf_lineage import check_b_c_extended_semantics_or_raise

        summary = self._load_legacy_summary()
        with pytest.raises(ValueError) as exc_info:
            check_b_c_extended_semantics_or_raise(summary, artifact_path=None)

        assert "b_c_extended_v1" in str(exc_info.value), (
            f"Keyword class 2 ('b_c_extended_v1') missing from error message: "
            f"{exc_info.value!r}. Pre-committed at sub-plan v6 §2.3 ratify."
        )

    def test_message_contains_actual_schema_version_value(self) -> None:
        """A2-α LOCK keyword class 3: error message contains the actual rejected value.

        Per sub-plan v6 §2.3 keyword class table row 3 (via !r interpolation at
        artifact_schema.py:741). Tells caller which value was rejected.
        """
        from backtest.wf_lineage import check_b_c_extended_semantics_or_raise

        summary = self._load_legacy_summary()
        actual_value = summary["artifact_schema_version"]

        with pytest.raises(ValueError) as exc_info:
            check_b_c_extended_semantics_or_raise(summary, artifact_path=None)

        # Value rendered via repr; check both quoted and bare forms for robustness
        msg = str(exc_info.value)
        assert actual_value in msg or repr(actual_value) in msg, (
            f"Keyword class 3 (actual schema_version value {actual_value!r}) missing from error message: "
            f"{exc_info.value!r}. Pre-committed at sub-plan v6 §2.3 ratify."
        )


# ---------------------------------------------------------------------------
# A3 + A4 + A5 — Byte-identity hash verification (41 hash comparisons; (i) git-plumbing)
# ---------------------------------------------------------------------------


class TestT1_4_A3_A4_A5_HashByteIdentity:
    """A3 + A4 + A5: legacy phase4 artifacts byte-identical between pre-T1.x and post-T1.x.

    Per sub-plan v6 §2.2 (i) git-plumbing LOCK + §2.4 A3+A4+A5:
    - A3: aggregate holdout_results.csv byte-identical
    - A4: aggregate holdout_summary.json byte-identical
    - A5: all 39 per-candidate holdout_summary.json byte-identical

    Total: 41 hash comparisons (1 CSV + 1 aggregate JSON + 39 per-candidate JSONs).
    """

    def test_per_candidate_count_locked_at_39(self) -> None:
        """A5 precondition: N per-candidate dirs = 39 at ratify (per Advisor v4 F-v4-3 LOW).

        Moved v2 per Advisor F3 v1 PFR (test belongs in TestT1_4_A3_A4_A5_HashByteIdentity
        class which is canonically where A5 lives; was incorrectly in TestT1_4_A1_A6 class at v1).
        """
        dirs = _per_candidate_dirs()
        assert len(dirs) == 39, (
            f"Expected 39 per-candidate dirs at {_PHASE4_DIR}, got {len(dirs)}. "
            f"Sub-plan v6 §1.1 A5 locked N=39 at ratify (empirical at HEAD 12dffde)."
        )

    def _verify_byte_identity(self, canonical_rel_path: str, archive_rel_path: str) -> None:
        """Verify the ARCHIVED ORIGINAL is byte-identical to pre-T1.x 7c8f4a7.

        B-C-narrow Phase 3 re-fire (Plan v9.1 §V9.5 V9-E4 + Q1=a + Option A): the recovery
        REPLACES the canonical with recovered content, so this no longer compares the
        on-disk canonical. Instead "before" = the original at 7c8f4a7 (canonical path at
        that commit) and "after" = the archived snapshot on disk (committed at Step 14b.1.5;
        the producer W3 step shutil.move'd the pre-fire canonical there byte-for-byte). On a
        clean tree the on-disk archive == the committed archive == the 7c8f4a7 original, so
        this preserves the original-immutability invariant the test guards.
        """
        # "Before" bytes: original at pre-T1.x parent commit (canonical path at 7c8f4a7).
        before_bytes = _git_show_bytes(_PRE_T1X_COMMIT, canonical_rel_path)
        before_hash = _sha256_bytes(before_bytes)

        # "After" bytes: the archived snapshot on disk (Q1=a + Option A).
        after_bytes = _file_bytes(_REPO_ROOT / archive_rel_path)
        after_hash = _sha256_bytes(after_bytes)

        assert before_hash == after_hash, (
            f"v9 re-fire byte-identity FAILED: 7c8f4a7 original {canonical_rel_path} "
            f"sha256={before_hash} != archived snapshot {archive_rel_path} sha256={after_hash}. "
            f"The B-C-narrow archive MUST preserve the pre-recovery original byte-for-byte "
            f"(Q1=a rescope; archive committed at Step 14b.1.5)."
        )

    def test_a3_aggregate_holdout_results_csv_byte_identical(self) -> None:
        """A3 MANDATORY: aggregate holdout_results.csv byte-identical (archive vs 7c8f4a7)."""
        canonical_rel_path = "data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1/holdout_results.csv"
        archive_rel_path = "data/phase2c_evaluation_gate/archive/phase4_forward_2026_15bps_v1_d0b8101/holdout_results.csv"
        self._verify_byte_identity(canonical_rel_path, archive_rel_path)

    def test_a4_aggregate_holdout_summary_json_byte_identical(self) -> None:
        """A4 MANDATORY (per Codex v4 Fv4-5): aggregate holdout_summary.json byte-identical (archive vs 7c8f4a7)."""
        canonical_rel_path = "data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1/holdout_summary.json"
        archive_rel_path = "data/phase2c_evaluation_gate/archive/phase4_forward_2026_15bps_v1_d0b8101/holdout_summary.json"
        self._verify_byte_identity(canonical_rel_path, archive_rel_path)

    @pytest.mark.parametrize("candidate_dir", _per_candidate_dirs())
    def test_a5_per_candidate_holdout_summary_byte_identical(self, candidate_dir: Path) -> None:
        """A5 MANDATORY: all 39 per-candidate holdout_summary.json byte-identical (archive vs 7c8f4a7)."""
        # candidate_dir is the recovered-canonical hash subdir; its .name (hypothesis_hash)
        # is shared with the archive subdir (same 39 basenames). before = 7c8f4a7 canonical
        # path; after = archive on-disk (Q1=a + Option A).
        canonical_rel_path = str(candidate_dir.relative_to(_REPO_ROOT) / "holdout_summary.json")
        archive_rel_path = str(_ARCHIVE_DIR.relative_to(_REPO_ROOT) / candidate_dir.name / "holdout_summary.json")
        self._verify_byte_identity(canonical_rel_path, archive_rel_path)


# ---------------------------------------------------------------------------
# B1 — Signature backward-compat (AST classifier; locked 4-tuple)
# ---------------------------------------------------------------------------


class TestT1_4_B1_SignatureBackwardCompat:
    """B1: AST-based call-site classifier verifies (prod=4, test=49, scripts=0, dynamic=23).

    Per sub-plan v6 §2.4 (locked at ratify per empirical at HEAD 12dffde) + §8.1
    + Charlie B1 register 2026-05-24 baseline-maintenance update for T1.5 cohort
    (test=43→49, dynamic=17→23; AST-correct numbers per §8.1 methodology divergence
    note above).

    Per SEAL-eve LOW D fix 2026-05-24 (Codex): docstring stale tuple updated
    from grep-era (9,46,0,17) at T1.4 SEAL to AST-correct T1.5-extended
    (4,49,0,23). Functional lock at `_B1_LOCKED_4TUPLE` constant unchanged.

    Single-pattern adjudication: all 23 dynamic_count instances use
    _make_minimal_write_args() helper-return + **args unpack pattern (17 in
    tests/test_t1_3_registry_api.py + 6 in tests/test_t1_5_registry_integrity.py);
    all backward-compat-safe per T1.3-C HYBRID extension.
    """

    SCOPED_DIRS = ("backtest", "tests", "scripts")
    EXCLUDED_PATH_FRAGMENTS = (".claude", ".git", "venv", "__pycache__", ".pytest_cache")
    # Exclude T1.4 test file itself from B1 scope (self-reference incoherent).
    # T1.4 test file's _write_to_registry calls are test-fixture exercises, NOT
    # production/test-codebase callers being verified for backward-compat.
    SELF_REFERENCE_FILE = "test_t1_4_backward_compat.py"

    @staticmethod
    def _enumerate_call_sites() -> list[tuple[Path, int, list[str], bool, int]]:
        """Phase 1+2 of §2.4 AST classifier: enumerate _write_to_registry call sites.

        Returns list of (file_path, line, named_kwargs_list, has_dynamic_kwargs, positional_arg_count).
        Scoped per Codex F2 v2 PFR: backtest/, tests/, scripts/ only.
        Excludes T1.4 self-reference (this file is the test, not a verified caller).

        v2 per Codex F2 + Advisor F1 v1 PFR: added positional_arg_count to support
        §3.1 pc 5 (c) positional-dependency assertion.
        """
        results: list[tuple[Path, int, list[str], bool, int]] = []

        for scoped_dir in TestT1_4_B1_SignatureBackwardCompat.SCOPED_DIRS:
            scope_path = _REPO_ROOT / scoped_dir
            if not scope_path.exists():
                continue
            for py_file in scope_path.rglob("*.py"):
                # Exclude worktrees + caches per Codex F2 v2 PFR scoping
                if any(frag in str(py_file) for frag in TestT1_4_B1_SignatureBackwardCompat.EXCLUDED_PATH_FRAGMENTS):
                    continue
                # Exclude T1.4 self-reference
                if py_file.name == TestT1_4_B1_SignatureBackwardCompat.SELF_REFERENCE_FILE:
                    continue
                try:
                    tree = ast.parse(py_file.read_text())
                except SyntaxError as e:
                    # v2-6 per Advisor F4 v1 PFR: silent skip on SyntaxError could mask
                    # missing coverage. Fail loudly so any unparseable in-scope file is caught.
                    raise AssertionError(
                        f"B1 AST classifier: failed to parse in-scope file {py_file} "
                        f"(SyntaxError: {e}). If file legitimately has syntax error, "
                        f"explicitly exclude via EXCLUDED_PATH_FRAGMENTS class constant; "
                        f"do NOT silently skip (masks missing _write_to_registry coverage)."
                    ) from e
                for node in ast.walk(tree):
                    if not isinstance(node, ast.Call):
                        continue
                    # Match _write_to_registry as direct call OR module-qualified
                    func_name = None
                    if isinstance(node.func, ast.Name) and node.func.id == "_write_to_registry":
                        func_name = "_write_to_registry"
                    elif isinstance(node.func, ast.Attribute) and node.func.attr == "_write_to_registry":
                        func_name = "_write_to_registry"
                    if func_name is None:
                        continue

                    named_kwargs: list[str] = []
                    has_dynamic = False
                    for kw in node.keywords:
                        if kw.arg is None:
                            # **kwargs unpacking — per §2.4 Phase 2 ALL keyword(arg=None) → dynamic
                            has_dynamic = True
                        else:
                            named_kwargs.append(kw.arg)
                    # v3 per Codex F2 v2 PFR MEDIUM: also flag `*args` (ast.Starred) positional
                    # unpacking as dynamic — `_write_to_registry(*pos_args)` parses to args=[Starred]
                    # which would otherwise count as len(args)=1 ≤ MAX_POSITIONAL=2 + pass MAX
                    # check despite arbitrary runtime positional ordering.
                    has_starred_positional = any(isinstance(arg, ast.Starred) for arg in node.args)
                    if has_starred_positional:
                        has_dynamic = True
                    # v2 per Codex F2 + Advisor F1 v1 PFR: track positional args for
                    # §3.1 pc 5 (c) positional-dependency assertion
                    positional_arg_count = len(node.args)
                    results.append((py_file, node.lineno, named_kwargs, has_dynamic, positional_arg_count))
        return results

    def test_4_tuple_matches_locked_values(self) -> None:
        """§8.1 RESOLVED: (prod=9, test=46, scripts=0, dynamic=17) at HEAD 12dffde."""
        call_sites = self._enumerate_call_sites()

        prod_count = sum(
            1 for (p, _, _, _, _) in call_sites
            if (_REPO_ROOT / "backtest") in p.parents or p.parent == (_REPO_ROOT / "backtest")
        )
        test_count = sum(
            1 for (p, _, _, _, _) in call_sites
            if (_REPO_ROOT / "tests") in p.parents or p.parent == (_REPO_ROOT / "tests")
        )
        scripts_count = sum(
            1 for (p, _, _, _, _) in call_sites
            if (_REPO_ROOT / "scripts") in p.parents or p.parent == (_REPO_ROOT / "scripts")
        )
        dynamic_count = sum(1 for (_, _, _, dyn, _) in call_sites if dyn)

        observed = {
            "prod_count": prod_count,
            "test_count": test_count,
            "scripts_count": scripts_count,
            "dynamic_count": dynamic_count,
        }

        assert observed == _B1_LOCKED_4TUPLE, (
            f"B1 4-tuple mismatch from ratify-time lock. "
            f"Locked: {_B1_LOCKED_4TUPLE} (per sub-plan v6 §8.1 RESOLVED at HEAD 12dffde). "
            f"Observed at test execution: {observed}. "
            f"If counts changed legitimately (e.g., new code added _write_to_registry callers), "
            f"a fresh Charlie register-event + sub-plan v7 ratify is required to re-lock the 4-tuple."
        )

    def test_dynamic_count_all_in_uniform_pattern_file(self) -> None:
        """§8.1 dynamic_count adjudication: all 23 dynamic instances in approved files (T1.3 + T1.5).

        Per single-pattern-class adjudication: uniform helper-return + mutation + **args unpack
        pattern; backward-compat-safe per T1.3-C HYBRID extension.

        T1.4 SEAL HEAD `12dffde` locked 17 dynamic instances all in tests/test_t1_3_registry_api.py.
        T1.5 added 6 dynamic instances all in tests/test_t1_5_registry_integrity.py per
        Charlie B1 register 2026-05-24 baseline-maintenance update; same uniform
        helper-return + **args unpack pattern preserved → single-pattern adjudication
        scope extends from 1-file to 2-file allowlist.
        """
        call_sites = self._enumerate_call_sites()
        dynamic_sites = [(p, line) for (p, line, _, dyn, _) in call_sites if dyn]

        approved_files = {
            _REPO_ROOT / "tests" / "test_t1_3_registry_api.py",  # T1.4 SEAL locked
            _REPO_ROOT / "tests" / "test_t1_5_registry_integrity.py",  # T1.5 Charlie B1 2026-05-24
        }
        for (file_path, line) in dynamic_sites:
            assert file_path in approved_files, (
                f"Dynamic _write_to_registry(**args) call at unexpected file: "
                f"{file_path}:{line}. Sub-plan v6 §8.1 adjudication (extended per Charlie "
                f"B1 register 2026-05-24): all 23 dynamic instances must be in "
                f"approved_files={sorted(str(p) for p in approved_files)} (single-pattern "
                f"adjudication scope). New dynamic caller elsewhere requires fresh Charlie "
                f"register-event + baseline extension."
            )

    def test_no_positional_dependency_breakage(self) -> None:
        """B1 (§3.1 pc 5 (c)): zero call sites rely on positional argument order broken by T1.3-C HYBRID.

        v2 per Codex F2 + Advisor F1 v1 PFR (replaces no-op stub from v1).
        v4 per Codex F3 SEAL-eve MEDIUM: ast.Starred (*args) positional-unpack callers
        previously exempted from this check via dynamic_count classification; now
        ast.Starred callers explicitly fail UNLESS individually adjudicated. v3 design
        treated *args as dynamic + dynamic adjudicated only by file path; this allowed
        a same-file replacement of `_write_to_registry(**args)` with `_write_to_registry(*pos)`
        to silently pass. v4 fix: ast.Starred always fails positional-dependency check.

        Assertion: every call site uses ≤2 positional args (run_id + strategy_cls first
        2 required params) AND zero ast.Starred positional unpacks (any starred call
        relies on arbitrary positional ordering at runtime).
        Dynamic (**kwargs) callers via keyword(arg=None) remain skipped — `**unpack` expands as named kwargs.
        """
        # Re-enumerate without conflating ast.Starred into has_dynamic (need to distinguish)
        call_sites = self._enumerate_call_sites()
        MAX_POSITIONAL = 2
        violations: list[tuple] = []
        starred_violations: list[tuple] = []

        # Separately re-walk to detect ast.Starred specifically (independent of has_dynamic conflation)
        for scoped_dir in self.SCOPED_DIRS:
            scope_path = _REPO_ROOT / scoped_dir
            if not scope_path.exists():
                continue
            for py_file in scope_path.rglob("*.py"):
                if any(frag in str(py_file) for frag in self.EXCLUDED_PATH_FRAGMENTS):
                    continue
                if py_file.name == self.SELF_REFERENCE_FILE:
                    continue
                try:
                    tree = ast.parse(py_file.read_text())
                except SyntaxError:
                    continue
                for node in ast.walk(tree):
                    if not isinstance(node, ast.Call):
                        continue
                    func = node.func
                    if not ((isinstance(func, ast.Name) and func.id == "_write_to_registry")
                            or (isinstance(func, ast.Attribute) and func.attr == "_write_to_registry")):
                        continue
                    # v4-3: ast.Starred unconditionally violates positional-dependency check
                    if any(isinstance(arg, ast.Starred) for arg in node.args):
                        starred_violations.append((py_file, node.lineno))

        assert not starred_violations, (
            f"B1 v4-3 per Codex F3 SEAL-eve MEDIUM: {len(starred_violations)} call site(s) use "
            f"ast.Starred (*args) positional unpack which relies on arbitrary runtime positional "
            f"ordering. Violations: {starred_violations}. Required fix: convert to named kwargs "
            f"OR explicit individual adjudication at sub-plan ratify boundary."
        )

        for (file_path, line, named_kwargs, has_dynamic, positional_count) in call_sites:
            if has_dynamic:
                continue
            if positional_count > MAX_POSITIONAL:
                violations.append((file_path, line, positional_count, named_kwargs))

        assert not violations, (
            f"B1 (§3.1 pc 5 (c)): {len(violations)} call site(s) rely on positional argument "
            f"order beyond MAX_POSITIONAL={MAX_POSITIONAL}. Violations: {violations}."
        )

    def test_self_reference_exclusion_lock(self) -> None:
        """B1 (§3.1 pc 5; v2 per Advisor F5 v1 PFR): defensive positive-lock on self-reference exclusion.

        The SELF_REFERENCE_FILE class constant excludes tests/test_t1_4_backward_compat.py
        from B1 scope (T1.4 test file is the test, not a verified caller; self-reference incoherent).
        If exclusion mechanism breaks or is refactored away silently, dynamic_count would jump
        from 17 to 22+ (T1.4 test file contains 5 `_write_to_registry(**args)` call sites in
        B2 + B3 tests).

        v2 defensive lock: explicitly verify the excluded file would-contribute the expected
        7 dynamic calls (positive proof the exclusion mechanism actually fires + has the
        expected effect).
        """
        # Manually count what T1.4 test file would contribute if NOT excluded
        self_ref_path = _REPO_ROOT / "tests" / self.SELF_REFERENCE_FILE
        tree = ast.parse(self_ref_path.read_text())
        self_ref_dynamic_count = 0
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            if not ((isinstance(func, ast.Name) and func.id == "_write_to_registry")
                    or (isinstance(func, ast.Attribute) and func.attr == "_write_to_registry")):
                continue
            if any(kw.arg is None for kw in node.keywords):
                self_ref_dynamic_count += 1

        # v4 per F1 BLOCKING rework: B3.1+B3.2 substantive direct **args removed (replaced
        # with real entry-point invocation + writer spy); count drops from 6 (v3) to 5.
        EXPECTED_SELF_REF_DYNAMIC = 5  # B2.a/b/c/d (4) + B3.4 smart-mock helper (1)
        assert self_ref_dynamic_count == EXPECTED_SELF_REF_DYNAMIC, (
            f"B1 self-reference exclusion defensive lock: T1.4 test file would contribute "
            f"{self_ref_dynamic_count} dynamic `_write_to_registry(**args)` calls if not excluded, "
            f"expected EXPECTED_SELF_REF_DYNAMIC={EXPECTED_SELF_REF_DYNAMIC}. If count drifted, "
            f"either T1.4 tests were modified (review + adjust EXPECTED) or exclusion mechanism "
            f"broke (review SELF_REFERENCE_FILE matching at _enumerate_call_sites)."
        )


# ---------------------------------------------------------------------------
# B2 — Legacy default-normalization (4 scenarios per Contract 2.0.4)
# ---------------------------------------------------------------------------


class TestT1_4_B2_LegacyDefaultNormalization:
    """B2.a + B2.b + B2.c + B2.d: legacy default-normalization + fail-closed branches.

    Per sub-plan v6 §2.5 (revised v3 per Codex F2 + F3 + Advisor F5 + F6 v2 PFR):
    - B2.a: lineage_context=None + execution_config_path=None → cost_anchor_id resolved + 8 NULL
    - B2.b: lineage_context=None + explicit mapped path → cost_anchor_id resolved + 8 NULL
    - B2.c: un-mapped in-repo path → ValueError mapping fail-closed
    - B2.d: outside-repo path → ValueError path-containment fail-closed
    """

    def _make_db(self, tmp_path: Path, name: str = "test.db") -> Path:
        """Create empty SQLite DB with runs schema."""
        from backtest.experiment_registry import create_table
        db_path = tmp_path / name
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        create_table(conn)
        conn.close()
        return db_path

    def test_b2_a_default_normalization_happy_path(self, tmp_path: Path) -> None:
        """B2.a: lineage_context=None + execution_config_path=None → default normalization."""
        from backtest.engine import _write_to_registry

        db_path = self._make_db(tmp_path, "b2a.db")
        args = _make_minimal_write_args(run_id="b2a-test")
        args["db_path"] = db_path
        # No lineage_context + no execution_config_path → default normalization fires

        _write_to_registry(**args)

        row = _read_row(db_path, "b2a-test")
        assert row is not None, "B2.a: row must be persisted"
        # cost_anchor_id resolved to legacy default per Contract 2.0.4 interpretation (b)
        assert row["cost_anchor_id"] == "legacy_perp_inspired_7bps_v0", (
            f"B2.a: cost_anchor_id must resolve to 'legacy_perp_inspired_7bps_v0' under "
            f"default normalization (lineage_context=None + execution_config_path=None); "
            f"got {row['cost_anchor_id']!r}"
        )
        # Other 8 columns must be NULL
        for col in _T1X_NEW_COLUMNS:
            if col == "cost_anchor_id":
                continue
            assert row[col] is None, (
                f"B2.a: column {col!r} must be NULL when lineage_context=None; "
                f"got {row[col]!r}"
            )

    def test_b2_b_explicit_mapped_path_happy_path(self, tmp_path: Path) -> None:
        """B2.b: lineage_context=None + explicit mapped path → cost_anchor_id resolves."""
        from backtest.engine import _write_to_registry

        db_path = self._make_db(tmp_path, "b2b.db")
        args = _make_minimal_write_args(run_id="b2b-test")
        args["db_path"] = db_path
        # Explicit mapped path: spot anchor per R3.1d §5.2 mapping
        args["execution_config_path"] = "config/execution_phaseb_spot_15bps.yaml"

        _write_to_registry(**args)

        row = _read_row(db_path, "b2b-test")
        assert row is not None
        assert row["cost_anchor_id"] == "spot_realistic_15bps_v1", (
            f"B2.b: cost_anchor_id must resolve to 'spot_realistic_15bps_v1' for "
            f"config/execution_phaseb_spot_15bps.yaml; got {row['cost_anchor_id']!r}"
        )
        # Other 8 columns NULL (no LC)
        for col in _T1X_NEW_COLUMNS:
            if col == "cost_anchor_id":
                continue
            assert row[col] is None, f"B2.b: column {col!r} must be NULL; got {row[col]!r}"

    def test_b2_c_unmapped_in_repo_path_fail_closed(self, tmp_path: Path) -> None:
        """B2.c: un-mapped in-repo path → ValueError with ALL 3 required components per §2.5 spec.

        v2 per Codex F3 v1 PFR: tightened from disjunction to AND-conjunction of all spec components:
        - canonicalized path string (the input that failed mapping lookup)
        - full mapping enumeration (COST_ANCHOR_ID_MAPPING.items())
        - explicit guidance text ("Update R3.1d §5.2 mapping" or equivalent)
        """
        from backtest.engine import _write_to_registry

        db_path = self._make_db(tmp_path, "b2c.db")
        args = _make_minimal_write_args(run_id="b2c-test")
        args["db_path"] = db_path
        unmapped_path = "config/unknown.yaml"
        args["execution_config_path"] = unmapped_path

        with pytest.raises(ValueError) as exc_info:
            _write_to_registry(**args)

        msg = str(exc_info.value)
        # Component 1: canonicalized path string
        assert unmapped_path in msg or "unknown.yaml" in msg, (
            f"B2.c component 1 (canonicalized path): expected {unmapped_path!r} or 'unknown.yaml' "
            f"in fail-closed message; got: {msg!r}"
        )
        # Component 2: FULL mapping enumeration per §2.5 spec (per Codex F3 v2 PFR MEDIUM:
        # v2 accepted just 1 of 6 anchor strings; v3 tightens to require ALL 6 entries present;
        # v3-inline-fix per convergent Codex F1 v3 PFR LOW + R5.2 register #7 mechanical-only
        # precedent: tighten further to assert BOTH path_key AND anchor_id per entry — engine
        # renders as f"{k!r} → {v!r}" at engine.py:1199-1201 so both halves must appear).
        from backtest.artifact_schema import COST_ANCHOR_ID_MAPPING
        missing_entries = []
        for path_key, anchor_id in COST_ANCHOR_ID_MAPPING.items():
            # Per engine.py:1197-1206 rendering: each entry appears as f"{k!r} → {v!r}".
            # Assert both halves of each pair present for full enumeration completeness.
            if path_key not in msg or anchor_id not in msg:
                missing_entries.append((path_key, anchor_id))
        assert not missing_entries, (
            f"B2.c component 2 (FULL mapping enumeration per §2.5 spec): expected ALL "
            f"{len(COST_ANCHOR_ID_MAPPING)} mapping entries (both path_key AND anchor_id "
            f"per entry) in error message per Codex F3 v2 PFR + Codex F1 v3 PFR tightening. "
            f"Missing: {missing_entries}. Got message: {msg!r}"
        )
        # Component 3: explicit guidance text
        assert "R3.1d" in msg or "Update" in msg or "human approval" in msg, (
            f"B2.c component 3 (guidance): expected 'R3.1d' or 'Update' or 'human approval' "
            f"guidance text; got: {msg!r}"
        )

    def test_b2_d_outside_repo_path_fail_closed(self, tmp_path: Path) -> None:
        """B2.d (NEW per Codex F3 v2 PFR): outside-repo path → ValueError with ALL 4 required components per §2.5 spec.

        v2 per Codex F3 v1 PFR: tightened from disjunction to AND-conjunction:
        - original path string (via !r interpolation)
        - repo root real path
        - text "outside repo root" or "path-containment violation"
        - text "Contract 2.0.4 fail-closed clause"
        """
        from backtest.engine import _write_to_registry

        db_path = self._make_db(tmp_path, "b2d.db")
        args = _make_minimal_write_args(run_id="b2d-test")
        args["db_path"] = db_path
        outside_path = "/tmp/outside_repo_config.yaml"
        args["execution_config_path"] = outside_path

        with pytest.raises(ValueError) as exc_info:
            _write_to_registry(**args)

        msg = str(exc_info.value)
        # Component 1: original path string
        assert outside_path in msg or "/tmp/outside_repo_config" in msg, (
            f"B2.d component 1 (original path): expected {outside_path!r} or partial; got: {msg!r}"
        )
        # Component 2: repo root real path (parent of backtest/ is btc-alpha-pipeline)
        assert "btc-alpha-pipeline" in msg or str(_REPO_ROOT) in msg, (
            f"B2.d component 2 (repo root): expected 'btc-alpha-pipeline' or full path in message; "
            f"got: {msg!r}"
        )
        # Component 3: outside-repo / path-containment text
        assert "outside repo root" in msg or "path-containment" in msg, (
            f"B2.d component 3 (outside-repo/path-containment text); got: {msg!r}"
        )
        # Component 4: Contract 2.0.4 fail-closed reference
        assert "Contract 2.0.4" in msg, (
            f"B2.d component 4 (Contract 2.0.4 reference); got: {msg!r}"
        )


# ---------------------------------------------------------------------------
# B3 — Legitimate flows + γ-1 opt-out-verification
# ---------------------------------------------------------------------------


class TestT1_4_B3_LegitimateFlowsAndOptOutSemantic:
    """B3.1 + B3.2 LC-positive + B3.3 + B3.4 γ-1 opt-out-verification.

    Per sub-plan v6 §2.6 (revised v4 per Codex F1 + Advisor F-NEW-1; γ-1 LOCK per Charlie 2026-05-23):
    - B3.1: run_backtest LC-positive scenario
    - B3.2: run_regime_holdout LC-positive scenario
    - B3.3: run_walk_forward γ-1 opt-out (no LC param at API; outer-wrapper writes default-normalized)
    - B3.4: evaluation-gate driver γ-1 opt-out (DEFAULT_DB_PATH monkeypatch isolation)
    """

    def _make_db(self, tmp_path: Path, name: str = "b3.db") -> Path:
        from backtest.experiment_registry import create_table
        db_path = tmp_path / name
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        create_table(conn)
        conn.close()
        return db_path

    def _make_canonical_lineage_context(self, run_id: str = "b3-lc-run") -> Any:
        """Construct a canonical deferred-state LineageContext for LC-positive scenarios.

        Uses config/execution_phaseb_spot_15bps.yaml → spot_realistic_15bps_v1 per R3.1d §5.2.

        DEFERRED-STATE LATE_FILL discipline (per T1.1 SYS3-B1 pair-completeness + SYS2-B2):
        returns_per_bar_path + returns_per_bar_sha256 BOTH empty (deferred state) so test
        does NOT require artifact_dir + parquet write at fixture-time. The deferred state
        matches the canonical pattern at test_t1_1_sys_fix.py:1715 (test_both_empty_late_fill_
        with_none_artifact_dir_passes). The actual T1.1 writer populates these LATE_FILL
        fields after artifact write at runtime; this LC-positive test verifies LC threading
        contract, not the LATE_FILL fill-flow (covered separately in T1.1 sealed tests).
        """
        from backtest.artifact_schema import LineageContext
        return LineageContext(
            run_id=run_id,
            hypothesis_hash="b3-hypothesis-hash",
            source_batch_id="b3-batch-id",
            regime_key="v2.regime_holdout",
            engine_commit="b3engine",
            current_git_sha="b3git_sha_full",
            execution_config_path="config/execution_phaseb_spot_15bps.yaml",
            execution_config_sha256="sha256:b3execconfig",
            parquet_data_sha256="sha256:b3parquet",
            returns_per_bar_path="",  # deferred state per D1-b LATE_FILL split
            returns_per_bar_sha256="",  # deferred state per D1-b LATE_FILL split
            T_obs=10,
            parent_run_id=None,
        )

    def test_b3_1_run_backtest_signature_accepts_lineage_context(self) -> None:
        """B3.1 LC-positive (signature-level verification): run_backtest accepts lineage_context kwarg.

        Per T1.3-D-i LOCK: run_backtest is one of 4 entry points carrying LC threading.
        Full backtest execution is heavy; this test verifies the contract at signature level.
        Substantive LC-threading behavior is exhaustively covered at
        tests/test_t1_3_registry_api.py (LineageContext positive + conflict tests).
        """
        import inspect
        from backtest.engine import run_backtest

        sig = inspect.signature(run_backtest)
        assert "lineage_context" in sig.parameters, (
            "B3.1: run_backtest() must accept lineage_context kwarg per T1.3-D-i LOCK"
        )

    def test_b3_2_run_regime_holdout_signature_accepts_lineage_context(self) -> None:
        """B3.2 LC-positive (signature-level verification): run_regime_holdout accepts lineage_context."""
        import inspect
        from backtest.engine import run_regime_holdout

        sig = inspect.signature(run_regime_holdout)
        assert "lineage_context" in sig.parameters, (
            "B3.2: run_regime_holdout() must accept lineage_context kwarg per T1.3-D-i LOCK"
        )

    def test_b3_1_run_backtest_chain_propagates_lc_to_writer(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """B3.1 LC-positive substantive verification per Codex F1 v4 SEAL-eve BLOCKING fix
        (v4-1 per Charlie register; 6th asymmetry class closure analog of v2-1 Path X for B3.3/B3.4):

        Invoke REAL run_backtest(lineage_context=lc); spy on _write_to_registry; assert
        the writer receives `lineage_context is lc` (identity check — proves chain propagation
        not just argument-shape equality) + persisted row has T1.x columns populated from LC.

        Closes the 6th asymmetry class: previously v3 tested signature-only at B3.1 + direct
        _write_to_registry call (writer-boundary substitute). A production bug that kept
        run_backtest signature accepting LC but silently dropped LC before the writer would
        have PASSED the v3 test. This v4-1 test exercises the actual entry-point chain.
        """
        from datetime import datetime, timezone
        import backtest.engine as engine_mod
        from strategies.baseline.sma_crossover import SMACrossover

        # v4-4 per Codex F4 SEAL-eve: hermetic — monkeypatch RESULTS_DIR to tmp_path
        monkeypatch.setattr("backtest.engine.RESULTS_DIR", tmp_path / "results")
        (tmp_path / "results").mkdir(exist_ok=True)

        # v4-4 per Codex F4 SEAL-eve: hard assertion (NOT skip) for canonical parquet
        PARQUET_PATH = _REPO_ROOT / "data" / "raw" / "btcusdt_1h.parquet"
        assert PARQUET_PATH.exists(), (
            f"B3.1 v4-1 BLOCKING fix: canonical parquet REQUIRED at {PARQUET_PATH}; "
            f"hard-asserted per Codex F4 SEAL-eve (skip-on-missing would make pc7 optional)"
        )

        db_path = self._make_db(tmp_path, "b3_1_lc_chain.db")

        # Predictable UUID for LC.run_id matches engine's auto-generated uuid via monkeypatch
        # (avoids T1.1 SYS2-H2 conflict-check fail-closed when scalar run_id != LC.run_id)
        predictable_uuid = "12345678-1234-1234-1234-123456789abc"
        import uuid as uuid_mod
        monkeypatch.setattr(uuid_mod, "uuid4", lambda: uuid_mod.UUID(predictable_uuid))

        lc = self._make_canonical_lineage_context(run_id=predictable_uuid)

        # Writer spy: capture all kwargs passed to _write_to_registry
        real_writer = engine_mod._write_to_registry
        captured_calls: list[dict] = []

        def _spy_writer(*args, **kwargs):
            captured_calls.append({"args": args, "kwargs": kwargs})
            return real_writer(*args, **kwargs)

        monkeypatch.setattr("backtest.engine._write_to_registry", _spy_writer)

        # Invoke REAL run_backtest with canonical LC over minimal date range (1 week)
        result = engine_mod.run_backtest(
            strategy_cls=SMACrossover,
            start_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
            end_date=datetime(2024, 1, 7, tzinfo=timezone.utc),
            parquet_path=PARQUET_PATH,
            db_path=db_path,
            lineage_context=lc,
        )

        # v4-1 substantive verification: chain propagation
        # Post-SEAL polish per Advisor F1 v4 PFR LOW: tightened `>= 1` to `== 1`
        # (single-writer-per-entry-point invariant per engine.py:770 + 2476).
        assert len(captured_calls) == 1, (
            f"B3.1 v4-1 + post-SEAL F1 polish: run_backtest must invoke _write_to_registry "
            f"EXACTLY once (single-writer-per-entry invariant); got {len(captured_calls)} calls"
        )

        # Identity check (not equality) — proves the SAME LC object reached the writer
        writer_lc = captured_calls[0]["kwargs"].get("lineage_context")
        assert writer_lc is lc, (
            f"B3.1 v4-1 BLOCKING fix: _write_to_registry MUST receive lineage_context IS lc "
            f"(identity check, not just equality). Got writer_lc={writer_lc!r}; "
            f"chain propagation broken — production bug class Codex F1 SEAL-eve caught."
        )

        # Persisted row has T1.x columns populated from LC
        actual_run_id = captured_calls[0]["kwargs"]["run_id"]
        row = _read_row(db_path, actual_run_id)
        assert row is not None
        assert row["cost_anchor_id"] == "spot_realistic_15bps_v1"
        assert row["execution_config_path"] == "config/execution_phaseb_spot_15bps.yaml"
        assert row["regime_key"] == "v2.regime_holdout"
        assert row["current_git_sha"] == "b3git_sha_full"
        assert row["execution_config_sha256"] == "sha256:b3execconfig"
        assert row["parquet_data_sha256"] == "sha256:b3parquet"
        assert row["T_obs"] == 10
        # Deferred-state LATE_FILL columns
        assert row["returns_per_bar_path"] in (None, "")
        assert row["returns_per_bar_sha256"] in (None, "")

    def test_b3_2_run_regime_holdout_chain_propagates_lc_to_writer(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """B3.2 LC-positive substantive verification per Codex F1 v4 SEAL-eve BLOCKING fix
        (v4-1 per Charlie register; same 6th asymmetry class closure as B3.1).

        Invoke REAL run_regime_holdout(lineage_context=lc); patch inner run_backtest heavy
        internal to return stub BacktestResult; spy on _write_to_registry; assert writer
        receives `lineage_context is lc`. Per Codex F1 fix spec: "patch heavy backtest
        internals, invoke real run_regime_holdout with LC".
        """
        from datetime import datetime, timezone, date
        from unittest.mock import MagicMock
        import backtest.engine as engine_mod
        from backtest.engine import BacktestResult
        from strategies.baseline.sma_crossover import SMACrossover
        import pandas as pd

        monkeypatch.setattr("backtest.engine.RESULTS_DIR", tmp_path / "results")
        (tmp_path / "results").mkdir(exist_ok=True)

        db_path = self._make_db(tmp_path, "b3_2_lc_chain.db")

        # Post-SEAL polish per Advisor F3 v4 PFR LOW: uuid monkeypatch was dead code
        # (stub returns pre-built BacktestResult; never calls uuid.uuid4). Use bare
        # predictable UUID without monkeypatch; stub_result.run_id directly aligned below.
        predictable_uuid_b3_2 = "abcdef01-2345-6789-abcd-ef0123456789"

        lc = self._make_canonical_lineage_context(run_id=predictable_uuid_b3_2)

        # Construct stub BacktestResult with all required fields per engine.py:636 dataclass
        now = datetime(2022, 1, 1, tzinfo=timezone.utc)
        stub_result = BacktestResult(
            run_id=predictable_uuid_b3_2,  # match LC.run_id for conflict-check
            strategy_name="stub_strategy",
            trades=[],
            equity_curve=pd.Series([10000.0, 10100.0], index=pd.DatetimeIndex([now, now])),
            metrics={
                "sharpe_ratio": 0.5,
                "max_drawdown": 0.05,
                "total_return": 0.01,
                "total_trades": 5,
                "win_rate": 0.6,
                "avg_trade_duration_hours": 4.0,
                "avg_trade_return": 0.002,
                "profit_factor": 1.5,
                "initial_capital": 10000.0,
                "final_capital": 10100.0,
                "max_drawdown_duration_hours": 24.0,
            },
            trade_csv_path=None,
            warmup_bars=0,
            effective_start=now,
            start_date=now,
            end_date=now,
        )

        # Patch heavy inner run_backtest to return stub
        def _stub_inner_backtest(**kwargs):
            return stub_result

        monkeypatch.setattr("backtest.engine.run_backtest", _stub_inner_backtest)

        # Provide minimal env_config for the v2.regime_holdout block (per engine.py:2131-2141 spec:
        # versioned splits namespace requires "version": "v2" + "splits": {<block_name>: {...}})
        env_config = {
            "version": "v2",
            "splits": {
                "regime_holdout": {
                    "label": "2022_bear",
                    "start": "2022-01-01",
                    "end": "2022-01-07",
                    "passing_criteria": {
                        "min_sharpe": -0.5,
                        "max_drawdown": 0.25,
                        "min_total_return": -0.15,
                        "min_total_trades": 5,
                    },
                },
            },
        }

        # Writer spy
        real_writer = engine_mod._write_to_registry
        captured_calls: list[dict] = []

        def _spy_writer(*args, **kwargs):
            captured_calls.append({"args": args, "kwargs": kwargs})
            return real_writer(*args, **kwargs)

        monkeypatch.setattr("backtest.engine._write_to_registry", _spy_writer)

        # Invoke REAL run_regime_holdout with canonical LC
        # batch_id MUST match LC.source_batch_id (T1.1 SYS2-H2 conflict-check) — both = "b3-batch-id"
        # parent_run_id must match LC.parent_run_id (None per deferred-state) — pass None
        result = engine_mod.run_regime_holdout(
            dsl=None,
            batch_id="b3-batch-id",  # match LC.source_batch_id
            parent_run_id="b3-2-parent",
            strategy_cls=SMACrossover,
            db_path=db_path,
            env_config=env_config,
            lineage_context=lc,
        )

        # v4-1 substantive verification: chain propagation
        # Post-SEAL polish per Advisor F1 v4 PFR LOW: tightened `>= 1` to `== 1`
        # (single-writer-per-entry-point invariant; inner run_backtest write_registry=False).
        assert len(captured_calls) == 1, (
            f"B3.2 v4-1 + post-SEAL F1 polish: run_regime_holdout must invoke _write_to_registry "
            f"EXACTLY once (single-writer-per-entry invariant); got {len(captured_calls)} calls"
        )

        writer_lc = captured_calls[0]["kwargs"].get("lineage_context")
        assert writer_lc is lc, (
            f"B3.2 v4-1 BLOCKING fix: _write_to_registry MUST receive lineage_context IS lc "
            f"(identity check). Got writer_lc={writer_lc!r}; chain propagation broken."
        )

        # Persisted row has T1.x columns populated from LC
        actual_run_id = captured_calls[0]["kwargs"]["run_id"]
        row = _read_row(db_path, actual_run_id)
        assert row is not None
        assert row["cost_anchor_id"] == "spot_realistic_15bps_v1"
        assert row["execution_config_path"] == "config/execution_phaseb_spot_15bps.yaml"
        assert row["regime_key"] == "v2.regime_holdout"
        assert row["current_git_sha"] == "b3git_sha_full"
        assert row["T_obs"] == 10

    def test_b3_3_walk_forward_signature_does_not_accept_lineage_context(self) -> None:
        """B3.3 γ-1 opt-out structural verification: run_walk_forward signature lacks lineage_context.

        Per T1.3-D opt-out at engine.py:1784-1797: walk-forward inner run_backtest hardcoded
        lineage_context=None. Outer wrapper does NOT accept LC. Verify signature reflects this.
        """
        import inspect
        from backtest.engine import run_walk_forward

        sig = inspect.signature(run_walk_forward)
        assert "lineage_context" not in sig.parameters, (
            "B3.3 γ-1 LOCK: run_walk_forward() MUST NOT accept lineage_context "
            "per T1.3-D opt-out (engine.py:1784-1797 hardcoded lineage_context=None in inner call). "
            "If this changes, γ-4 corrective register required + sub-plan revision."
        )

    def test_b3_3_walk_forward_outer_wrapper_default_normalization(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """B3.3 γ-1 opt-out substantive verification: REAL run_walk_forward() invocation per sub-plan §2.6.

        v2 per Codex F1 v1 PFR BLOCKING + Charlie Path X register: replaces v1 direct
        _write_to_registry simulation with actual run_walk_forward() invocation per sub-plan §2.6
        spec letter. Uses canonical SMACrossover strategy + canonical BTC parquet + small
        2/1/1-month walk-forward config over Jan-May 2024.

        v4-4 per Codex F4 SEAL-eve MEDIUM: hermetic isolation via monkeypatch RESULTS_DIR
        (prevents repo-global data/results pollution) + hard assertion (NOT skip) on
        canonical parquet (prevents pc7 silent degradation in lean environments).

        v4-5 per Codex F5 SEAL-eve MEDIUM: absence-assertion on unexpected run_types
        (catches inner run_backtest write_registry=True regression).

        γ-1 verification: after run_walk_forward completes, query persisted registry rows
        (outer-wrapper writer at engine.py:1841 + engine.py:1896); verify cost_anchor_id
        resolved via execution_config_path + 8 LC-derived columns NULL (T1.3-D opt-out
        preserves Contract 2.0.4 backward-compat semantic).
        """
        from datetime import date
        from backtest.engine import run_walk_forward
        from strategies.baseline.sma_crossover import SMACrossover

        # v4-4 per Codex F4 SEAL-eve: hermetic — monkeypatch RESULTS_DIR
        monkeypatch.setattr("backtest.engine.RESULTS_DIR", tmp_path / "results")
        (tmp_path / "results").mkdir(exist_ok=True)

        # v4-4 per Codex F4 SEAL-eve: hard assertion (NOT skip) for canonical parquet
        PARQUET_PATH = _REPO_ROOT / "data" / "raw" / "btcusdt_1h.parquet"
        assert PARQUET_PATH.exists(), (
            f"B3.3 v4-4 BLOCKING per Codex F4 SEAL-eve: canonical parquet REQUIRED at {PARQUET_PATH}; "
            f"hard-asserted (skip-on-missing would make pc7 optional in lean environments)"
        )

        db_path = self._make_db(tmp_path, "b3_3_wf.db")
        # Use existing test_walk_forward.py:191 invocation pattern
        wf_result = run_walk_forward(
            strategy_cls=SMACrossover,
            parquet_path=PARQUET_PATH,
            cash=10_000.0,
            db_path=db_path,
            walk_forward_config={
                "train_window_months": 2,
                "test_window_months": 1,
                "step_months": 1,
            },
            overall_start=date(2024, 1, 1),
            overall_end=date(2024, 5, 31),
            execution_config_path=_REPO_ROOT / "config" / "execution_phaseb_spot_15bps.yaml",
        )

        # Query persisted rows from outer-wrapper writer
        # v3 per Codex F4 v2 PFR LOW: precise row count assertions verify both writer paths
        # fired (window writer at engine.py:1841 + summary writer at engine.py:1896);
        # v2 accepted any nonzero count which would pass even if one writer disappeared.
        # v4-5 per Codex F5 SEAL-eve MEDIUM: also assert ABSENCE of unexpected row types
        # (e.g., if inner run_backtest flipped to write_registry=True, extra 'single_run'
        # rows would appear; v3 didn't catch this since it only queried window+summary).
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        all_rows = conn.execute("SELECT * FROM runs").fetchall()
        window_rows = [r for r in all_rows if r["run_type"] == "walk_forward_window"]
        summary_rows = [r for r in all_rows if r["run_type"] == "walk_forward_summary"]
        conn.close()

        # v4-5: total row count = exactly windows + 1 summary; no unexpected run_types
        expected_total = len(wf_result.window_results) + 1  # N windows + 1 summary
        assert len(all_rows) == expected_total, (
            f"B3.3 v4-5 per Codex F5 SEAL-eve: expected exactly {expected_total} rows "
            f"({len(wf_result.window_results)} windows + 1 summary); got {len(all_rows)}. "
            f"Unexpected rows could indicate inner run_backtest flipped to write_registry=True."
        )
        observed_run_types = {r["run_type"] for r in all_rows}
        expected_run_types = {"walk_forward_window", "walk_forward_summary"}
        assert observed_run_types == expected_run_types, (
            f"B3.3 v4-5: expected run_types exactly {expected_run_types}; "
            f"got {observed_run_types}. Unexpected types could indicate inner write_registry leak."
        )

        # Summary writer fired exactly once for wf_result.summary_run_id
        assert len(summary_rows) == 1, (
            f"B3.3 (Codex F4 v2 PFR fix): expected exactly 1 walk_forward_summary row for "
            f"summary_run_id={wf_result.summary_run_id!r}; got {len(summary_rows)} rows. "
            f"Walk-forward summary writer at engine.py:1896 may have skipped or fired multiple times."
        )
        assert summary_rows[0]["run_id"] == wf_result.summary_run_id, (
            f"B3.3: summary row run_id={summary_rows[0]['run_id']!r} != "
            f"wf_result.summary_run_id={wf_result.summary_run_id!r}"
        )

        # Window writer fired once per window
        assert len(window_rows) == len(wf_result.window_results), (
            f"B3.3 (Codex F4 v2 PFR fix): expected {len(wf_result.window_results)} "
            f"walk_forward_window rows (one per window result); got {len(window_rows)}. "
            f"Walk-forward window writer at engine.py:1841 may have skipped some windows."
        )
        # Every window row's parent_run_id matches summary's run_id (lineage check)
        for window_row in window_rows:
            assert window_row["parent_run_id"] == wf_result.summary_run_id, (
                f"B3.3: window row parent_run_id={window_row['parent_run_id']!r} != "
                f"summary run_id={wf_result.summary_run_id!r}; walk-forward lineage broken"
            )

        # γ-1 verification: every persisted row has cost_anchor_id resolved + 8 LC-derived columns NULL
        rows = list(window_rows) + list(summary_rows)
        for row in rows:
            assert row["cost_anchor_id"] == "spot_realistic_15bps_v1", (
                f"B3.3 γ-1: row run_id={row['run_id']!r} must have cost_anchor_id="
                f"'spot_realistic_15bps_v1' (resolved via execution_config_path); "
                f"got {row['cost_anchor_id']!r}"
            )
            for col in _T1X_NEW_COLUMNS:
                if col == "cost_anchor_id":
                    continue
                assert row[col] is None, (
                    f"B3.3 γ-1: row run_id={row['run_id']!r} column {col!r} must be NULL under "
                    f"walk-forward opt-out (no LC threading per T1.3-D); got {row[col]!r}. "
                    f"If LC fields populate, T1.3-D opt-out semantic broken."
                )

    def test_b3_4_eval_gate_driver_does_not_pass_lineage_context_or_db_path(self) -> None:
        """B3.4 γ-1 opt-out structural verification (v4 per Codex F2 SEAL-eve HIGH;
        v5 per B-C-narrow Phase 2 Task 11 baseline-maintenance for Task 10 CB6 supersession):
        _evaluate_one_candidate's run_regime_holdout call does NOT pass lineage_context kwarg.

        v4 originally locked BOTH `lineage_context` AND `db_path` as forbidden kwargs because
        DEFAULT_DB_PATH monkeypatch isolation in B3.4 chain test was load-bearing on
        get_connection(None) → DEFAULT_DB_PATH fallback. v5 narrows the forbidden set to
        `lineage_context` only per B-C-narrow Phase 2 Task 10 CB6 design lock: producer now
        legitimately threads `db_path` to engine so producer's CB6 `get_run(conn, child_run_id)`
        query and engine's `_write_to_registry` use the SAME DB
        (scripts/run_phase2c_evaluation_gate.py:599 — `db_path=db_path` with CB6 comment).
        DEFAULT_DB_PATH fallback path is preserved when `db_path=None` (legacy callers) —
        get_connection(None) still resolves to DEFAULT_DB_PATH in that case. B3.4 chain test
        isolation now uses DEFAULT_DB_PATH monkeypatch alongside explicit db_path=None per
        the smart-mock contract.

        v5 maintenance class mirrors T1.5 Charlie B1 register 2026-05-24 precedent (baseline
        maintenance for cohort-level producer signature evolution); the docstring's prior
        prediction "If this changes, γ-4 corrective register required" was discharged by
        Task 10 CB6 spec lock + Task 11 baseline-maintenance application here.

        `lineage_context` remains forbidden per γ-1 opt-out invariant: eval-gate driver is the
        legacy non-LC pathway, threading lineage_context would couple it to LC-positive flows
        and break the B-C-narrow Phase 2 LC-b opt-in semantic.
        """
        eval_gate_script = _REPO_ROOT / "scripts" / "run_phase2c_evaluation_gate.py"
        tree = ast.parse(eval_gate_script.read_text())

        found_run_regime_holdout_call = False
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            call_name = None
            if isinstance(func, ast.Name) and func.id == "run_regime_holdout":
                call_name = "run_regime_holdout"
            elif isinstance(func, ast.Attribute) and func.attr == "run_regime_holdout":
                call_name = "run_regime_holdout"
            if call_name is None:
                continue

            found_run_regime_holdout_call = True
            kwarg_names = {kw.arg for kw in node.keywords if kw.arg is not None}
            # v5 per B-C-narrow Phase 2 Task 11: `db_path` removed from forbidden set
            # per Task 10 CB6 supersession (producer legitimately threads db_path so
            # producer's get_run query + engine's _write_to_registry use SAME DB).
            # `lineage_context` remains forbidden per γ-1 opt-out invariant.
            for forbidden_kwarg in ("lineage_context",):
                assert forbidden_kwarg not in kwarg_names, (
                    f"B3.4 γ-1 + Codex F2 v4 SEAL-eve + Task 11 v5 maintenance: "
                    f"scripts/run_phase2c_evaluation_gate.py run_regime_holdout call at "
                    f"line {node.lineno} MUST NOT pass {forbidden_kwarg!r} kwarg per "
                    f"T1.3-D opt-out invariant. If this changes, γ-4 corrective register required."
                )

        assert found_run_regime_holdout_call, (
            "B3.4: scripts/run_phase2c_evaluation_gate.py must contain run_regime_holdout call "
            "(per evaluation-gate driver convention at scripts/run_phase2c_evaluation_gate.py:592-606)"
        )

    def test_b3_4_eval_gate_chain_default_normalization(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """B3.4 γ-1 opt-out substantive verification: REAL _evaluate_one_candidate() invocation per sub-plan §2.6.

        v2 per Codex F1 v1 PFR BLOCKING + Charlie Path X register: replaces v1 direct
        _write_to_registry simulation with actual `_evaluate_one_candidate()` invocation per
        sub-plan §2.6 spec letter. Uses DEFAULT_DB_PATH monkeypatch (preferred isolation per
        §2.6 + §8.1) so the chain's _write_to_registry calls persist to tmp_db.

        Chain test design: invoke actual `_evaluate_one_candidate()`; mock heavy internals
        (_load_dsl_from_response stub DSL + run_regime_holdout smart-mock that invokes
        _write_to_registry to simulate the chain's writer call) — this lets the writer path
        fire so the persisted row can be queried per Codex F1 fix spec ("query rows by
        parent_run_id"); avoids full backtrader execution which would add 30-120s test runtime.

        Per Codex F1 fix: happy-path gate `summary["lifecycle_state"] != "holdout_error"`
        precedes row query; row query by unique `parent_run_id=f"phase2c_eval_gate_{run_id}"`
        per evaluation-gate driver convention at scripts/run_phase2c_evaluation_gate.py:515.
        """
        import scripts.run_phase2c_evaluation_gate as runner
        from backtest.engine import _write_to_registry, RegimeHoldoutResult

        db_path = self._make_db(tmp_path, "b3_4_eval_gate.db")
        run_id = "b3-4-eval-gate-test"
        expected_parent_run_id = f"phase2c_eval_gate_{run_id}"

        # §2.6 §8.1 ratify-locked isolation mechanism: DEFAULT_DB_PATH monkeypatch (preferred)
        monkeypatch.setattr(
            "backtest.experiment_registry.DEFAULT_DB_PATH", db_path
        )

        # Smart-mock run_regime_holdout: invokes _write_to_registry to simulate the chain's
        # writer call (lets writer path fire so row can be queried) + returns synthetic
        # RegimeHoldoutResult so _evaluate_one_candidate's contract is exercised.
        #
        # v3-1 per Codex F1 v2 PFR HIGH: smart-mock MUST NOT pass explicit db_path —
        # let DEFAULT_DB_PATH monkeypatch be load-bearing per §2.6 isolation mechanism spec.
        #
        # v4-2 per Codex F2 SEAL-eve HIGH: smart-mock writes with run_type="regime_holdout"
        # (real holdout writer shape) NOT default "single_run"; rejects unexpected kwargs to
        # prevent silent semantic drift. Real run_regime_holdout writer call at engine.py:2476-2502
        # passes run_type="regime_holdout" + batch_id + hypothesis_hash.
        #
        # v4-3 per B-C-narrow Phase 2 Task 11 baseline-maintenance: ALLOWED_KWARGS extended
        # with 5 new LC-b + CB6 kwargs per Task 10 producer signature expansion at
        # scripts/run_phase2c_evaluation_gate.py:592-606 — db_path (CB6 single-source DB
        # threading), artifact_dir + source_batch_id + run_id_override + parent_run_id_override
        # (4 LC-b scalars; all None in the B3.4 legacy/opt-out path because
        # artifact_dir_root is None in this test → lcb_active=False → run_id_override stays
        # None and the 3 LC-b-conditional kwargs stay None per producer guard). γ-1 opt-out
        # semantic preserved: smart-mock NEVER passes lineage_context to _write_to_registry.
        ALLOWED_KWARGS = frozenset({
            "dsl", "batch_id", "parent_run_id", "regime_key",
            "execution_config_path", "env_config",
            # B-C-narrow Phase 2 Task 11 v4-3 baseline-maintenance (5 new kwargs):
            "db_path",                  # CB6: producer threads same DB to engine
            "artifact_dir",             # LC-b: per-candidate artifact dir (None in legacy path)
            "source_batch_id",          # LC-b scalar (None in legacy path)
            "run_id_override",          # LC-b scalar (None in legacy path)
            "parent_run_id_override",   # LC-b scalar (None in legacy path)
        })
        def _mock_run_regime_holdout(
            *, dsl, batch_id, parent_run_id, regime_key,
            execution_config_path=None, env_config=None, **kwargs
        ):
            # v4-2 reject unexpected kwargs (catches silent semantic drift)
            unexpected = set(kwargs.keys()) - ALLOWED_KWARGS
            if unexpected:
                raise TypeError(
                    f"B3.4 smart-mock v4-3 strict: unexpected kwargs {unexpected!r}. "
                    f"Real run_regime_holdout caller at scripts/run_phase2c_evaluation_gate.py:592-606 "
                    f"passes only {ALLOWED_KWARGS}; if eval-gate driver added a kwarg, "
                    f"verify γ-1 opt-out semantic still holds + update smart-mock."
                )
            # Simulate the writer call that real run_regime_holdout would make.
            # IMPORTANT: per γ-1 opt-out, NO lineage_context passed in chain — verifies
            # default normalization preserves Contract 2.0.4 backward-compat.
            # NO db_path passed — uses DEFAULT_DB_PATH (monkeypatched to tmp_db) per §2.6 spec.
            args = _make_minimal_write_args(
                run_id=run_id, parent_run_id=parent_run_id,
            )
            # NOTE: deliberately NOT setting args["db_path"] — DEFAULT_DB_PATH monkeypatch
            # is load-bearing per Codex F1 v2 PFR fix
            if execution_config_path is not None:
                args["execution_config_path"] = str(execution_config_path)
            # v4-2 per Codex F2 SEAL-eve HIGH: write with run_type="regime_holdout" (real shape)
            args["run_type"] = "regime_holdout"
            args["batch_id"] = batch_id
            args["hypothesis_hash"] = "abc123def456"  # matches candidate dict
            # v4-SEAL-eve inline-fix per Codex F1 MEDIUM: smart-mock must include
            # regime_holdout_passed field per real run_regime_holdout writer call at
            # engine.py:2492 (real chain always passes this; existing regime_holdout tests at
            # tests/test_regime_holdout.py:431-433 assert NOT NULL invariant on this column).
            args["regime_holdout_passed"] = True
            _write_to_registry(**args)
            # Return synthetic RegimeHoldoutResult matching real dataclass fields
            # (per backtest/engine.py:2044 RegimeHoldoutResult @dataclass definition)
            return RegimeHoldoutResult(
                run_id=run_id,
                parent_run_id=parent_run_id,
                batch_id=batch_id,
                hypothesis_hash="abc123def456",
                regime_holdout_passed=True,
                sharpe_ratio=0.5,
                max_drawdown=0.05,
                total_return=0.10,
                total_trades=10,
                passing_criteria={
                    "min_sharpe": -0.5,
                    "max_drawdown": 0.25,
                    "min_total_return": -0.15,
                    "min_total_trades": 5,
                },
                metrics={
                    "sharpe_ratio": 0.5,
                    "max_drawdown": 0.05,
                    "total_return": 0.10,
                    "total_trades": 10,
                },
                equity_curve=pd.Series(dtype=float),
            )

        # Mock _load_dsl_from_response to return stub (eval-gate doesn't validate DSL content)
        monkeypatch.setattr(runner, "_load_dsl_from_response", lambda *a, **kw: "stub_dsl_string")
        monkeypatch.setattr(runner, "run_regime_holdout", _mock_run_regime_holdout)

        # Invoke ACTUAL _evaluate_one_candidate (per Codex F1 fix spec)
        output_dir = tmp_path / "eval_gate_output"
        output_dir.mkdir()
        # Candidate dict with required fields per _per_candidate_summary at
        # scripts/run_phase2c_evaluation_gate.py:432-438
        candidate = {
            "hypothesis_hash": "abc123def456",
            "position": 0,
            "name": "test_candidate",
            "theme": "test_theme",
            "wf_test_period_sharpe": 1.0,
        }
        summary = runner._evaluate_one_candidate(
            candidate=candidate,
            head_sha="testheadsha1234567890",
            source_batch_id="test-source-batch",
            run_id=run_id,
            output_dir=output_dir,
            execution_config_path=_REPO_ROOT / "config" / "execution_phase4_15bps.yaml",
        )

        # Per Codex F1 happy-path gate: assert non-error lifecycle BEFORE querying rows
        assert summary["lifecycle_state"] != "holdout_error", (
            f"B3.4 happy-path gate: lifecycle_state='holdout_error' indicates chain exception "
            f"swallowed; row query would silently miss state. Got summary: {summary!r}"
        )

        # Per Codex F1 row query: by unique parent_run_id from chain convention
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT * FROM runs WHERE parent_run_id = ?",
            (expected_parent_run_id,),
        ).fetchone()
        conn.close()

        assert row is not None, (
            f"B3.4: no row found with parent_run_id={expected_parent_run_id!r} after "
            f"_evaluate_one_candidate; smart-mock writer-fire path may have failed"
        )
        # γ-1 verification: cost_anchor_id resolved + 8 LC-derived columns NULL
        assert row["cost_anchor_id"] == "phase4_forward_15bps_v1", (
            f"B3.4 γ-1: cost_anchor_id must resolve to 'phase4_forward_15bps_v1' via "
            f"execution_config_path; got {row['cost_anchor_id']!r}"
        )
        for col in _T1X_NEW_COLUMNS:
            if col == "cost_anchor_id":
                continue
            assert row[col] is None, (
                f"B3.4 γ-1: column {col!r} must be NULL under eval-gate opt-out "
                f"(no LC threading); got {row[col]!r}"
            )
        # v4-SEAL-eve inline-fix per Codex F1 MEDIUM: assert row shape matches
        # real run_regime_holdout writer call invariants (catches mock-vs-real divergence regression)
        assert row["run_type"] == "regime_holdout", (
            f"B3.4 row-shape: run_type must be 'regime_holdout' per real writer call shape; "
            f"got {row['run_type']!r}"
        )
        assert row["batch_id"] == "test-source-batch", (
            f"B3.4 row-shape: batch_id must propagate; got {row['batch_id']!r}"
        )
        assert row["hypothesis_hash"] == "abc123def456", (
            f"B3.4 row-shape: hypothesis_hash must propagate; got {row['hypothesis_hash']!r}"
        )
        assert row["regime_holdout_passed"] == 1, (
            f"B3.4 row-shape: regime_holdout_passed must be 1 (True) per real writer invariant "
            f"at tests/test_regime_holdout.py:431-433 NOT NULL assertion; got {row['regime_holdout_passed']!r}"
        )


# ---------------------------------------------------------------------------
# DB migration idempotency (3 scenarios per §2.7)
# ---------------------------------------------------------------------------


class TestT1_4_Pc9BaselineGate:
    """v4-6 per Codex F6 SEAL-eve LOW: pc9 baseline + zero-regression gate as executable T1.4 test.

    Per sub-plan v6/v7 §3.1 pc 9: "Full pytest suite: baseline + T1.4-count pass; zero pre-T1.4
    regression (baseline empirically locked at ratify-time via `pytest --collect-only` per Advisor F8)".
    v3 left pc9 as externally-verified-only (CLAUDE.md Phase Marker + manual confirmation); v4-6
    makes it executable so any regression triggers test failure.

    Note: this test does NOT actually re-run the full suite (would cause infinite recursion);
    it asserts the collect-only baseline lock + the count-delta invariant via pytest's collect mechanism.
    """

    def test_pc9_full_suite_collection_count_matches_baseline_plus_t1_4(self) -> None:
        """Pc9 verifiable gate: pytest --collect-only at HEAD = baseline 2191 + T1.4 count.

        Uses subprocess to re-invoke pytest collect-only safely (no recursion).
        """
        import subprocess
        import re
        # v4-SEAL-eve inline-fix per Codex F2 + Advisor F1 convergent LOW: use sys.executable
        # (interpreter-hermetic) rather than hardcoded "python".
        # Post-SEAL polish per Advisor F2 v4 PFR LOW: tighten "(collected >= BASELINE)" check
        # which could mask pre-T1.4 regression masked by T1.4 growth. Count T1.4 tests
        # separately + compute pre-T1.4 baseline = total - T1.4 count + assert == 2191 (locked).

        def _collect_count(args: list[str]) -> int:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "--collect-only", "-q"] + args,
                capture_output=True, text=True, cwd=_REPO_ROOT, timeout=120,
            )
            assert result.returncode == 0, (
                f"pc9 gate: pytest --collect-only failed: {result.stderr[-500:]}"
            )
            lines = [l for l in result.stdout.strip().splitlines() if l.strip()]
            last_line = lines[-1] if lines else ""
            match = re.search(r"(\d+)\s+tests?\s+collected", last_line)
            assert match, (
                f"pc9 gate: failed to parse pytest collect-only output last line: {last_line!r}"
            )
            return int(match.group(1))

        total_collected = _collect_count([])
        t1_4_collected = _collect_count(["tests/test_t1_4_backward_compat.py"])
        # Per Charlie B1 register 2026-05-24 baseline-maintenance update for T1.5
        # cohort: extend baseline subtraction to include T1.5 test files so the gate
        # detects unexpected pre-T1.x regression vs T1.5 expected additions.
        t1_5_collected = _collect_count([
            "tests/test_t1_5_fixture_moments.py",
            "tests/test_t1_5_registry_integrity.py",
            "tests/test_t1_5_smoke_end_to_end.py",
        ])
        pre_t1_x_baseline = total_collected - t1_4_collected - t1_5_collected

        # v4-6 + Advisor F2 post-SEAL polish: strict baseline lock per CLAUDE.md
        # Phase Marker + §3.1 pc 9 ratify-time lock; decouples T1.x growth from baseline
        # regression detection. T1.5 cohort added 2026-05-24 per Charlie B1 register
        # (baseline preserved at 2191; semantic: pre-T1.x baseline at T1.4 SEAL HEAD `12dffde`).
        # B-C-narrow Phase 0 Task 1 commit `ebc0d26` (2026-05-27) added 13 new test
        # methods in TestBCNarrowPhase0EngineExtension at tests/test_t1_1_artifact_writer.py.
        # Per Charlie register AMEND-PC9-INLINE-A (2026-05-27): advance BASELINE
        # 2191 → 2204 (T1.5 maintenance precedent extension; new B-C-narrow tests
        # treated as part of expanded pre-T1.x cohort. Future B-C-narrow Phase 1+/2+/3-4
        # cohorts may trigger further BASELINE advances or invariant-level gate refactor.)
        # B-C-narrow Phase 2 Task 9 commit `9a94f39` (2026-05-27) added 32 new test
        # methods in TestBCNarrowPhase2ProducerEdits at
        # tests/test_phase2c_evaluation_gate_runner.py (RED-then-GREEN producer-edit
        # specs; Task 10 commit `86f75ff` implemented producer to turn them GREEN).
        # Per B-C-narrow Phase 2 Task 11 baseline-maintenance: advance BASELINE
        # 2204 → 2236 (+32 per Phase 2 Task 9 expansion; same T1.5 precedent semantic
        # — new B-C-narrow tests treated as part of expanded pre-T1.x cohort).
        # B-C-narrow Phase 3 re-fire (Plan v9.1 §V9.5 V9-E2 + Gap2/Gap2b): adds
        # tests/test_b_c_narrow_v4_reproducibility.py (12 collected methods; confirmed
        # via `pytest --collect-only`). V4 is neither a t1_4 nor a t1_5 subtraction
        # target, so its +12 lands in pre_t1_x_baseline = total − t1_4 − t1_5. Advance
        # BASELINE 2236 → 2248 (same B-C-narrow cohort precedent). Closes Gap2/Gap2b:
        # Step 13.3 V4-isolated RED-verify missed this full-suite collection interaction.
        # Tier 6 DSR evaluation cohort (tier6-dsr-evaluation branch): adds
        # tests/test_tier6_dsr.py (72 collected methods — 56 from Tasks 1-7
        # closed-form DSR math + cohort evaluator + artifact emitters, 16 from
        # Task 8 CLI + lineage guard + cost-anchor preflight). The tier6 module is
        # purely additive (no existing module imports it) and test_tier6_dsr.py is
        # neither a t1_4 nor a t1_5 subtraction target, so its +72 lands wholly in
        # pre_t1_x_baseline = total − t1_4 − t1_5. Advance BASELINE 2248 → 2320
        # (same expected-additive-cohort precedent as T1.5 + B-C-narrow cohorts).
        # Tier 6 DSR chunk-3 hardening (tier6-dsr-evaluation branch): adds +3 new
        # test methods in tests/test_tier6_dsr.py (FIX HIGH yaml.YAMLError guard
        # test + FIX MED-1 abs-path acceptance test + FIX MINOR-3 logging
        # idempotency test). Purely additive to the same tier6 cohort, neither a
        # t1_4 nor a t1_5 subtraction target. Advance BASELINE 2320 → 2323 (+3,
        # same expected-additive-cohort precedent).
        # Tier 6 DSR final-review hardening (tier6-dsr-evaluation branch): adds +5
        # new test methods in tests/test_tier6_dsr.py (IMPORTANT-1 degenerate-row
        # all-fields-NaN test + MINOR-1 self-describing-CSV n_star/z_pass tests
        # ×2 [results-CSV column + _RESULT_FIELDS membership] + IMPORTANT-2
        # guard/preflight-before-CSV-read tests ×2). Purely additive to the same
        # tier6 cohort, neither a t1_4 nor a t1_5 subtraction target. Advance
        # BASELINE 2323 → 2328 (+5, same expected-additive-cohort precedent).
        BASELINE = 2328
        assert pre_t1_x_baseline == BASELINE, (
            f"pc9 gate (Codex F6 v4-6 SEAL-eve + Advisor F2 post-SEAL polish + Charlie "
            f"B1 register 2026-05-24 T1.5 baseline maintenance): pre-T1.x baseline "
            f"(total {total_collected} - T1.4 {t1_4_collected} - T1.5 {t1_5_collected} = "
            f"{pre_t1_x_baseline}) != locked baseline {BASELINE}. "
            f"Pre-T1.x regression detected — investigate before proceeding."
        )


class TestT1_4_DBMigrationIdempotency:
    """DB migration idempotency: 3 scenarios per sub-plan v6 §2.7 (Advisor F10 v2 PFR).

    Verifies experiment_registry.py:106-110 "one-way and idempotent" contract empirically.
    """

    def test_create_table_twice_idempotent(self, tmp_path: Path) -> None:
        """Scenario 1: create_table() twice on same DB → no exception + schema unchanged."""
        from backtest.experiment_registry import create_table

        db_path = tmp_path / "idem.db"
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row

        create_table(conn)
        # Snapshot schema
        cols_before = {row[1] for row in conn.execute("PRAGMA table_info(runs)").fetchall()}

        # Second call — must not raise + must not alter schema
        create_table(conn)
        cols_after = {row[1] for row in conn.execute("PRAGMA table_info(runs)").fetchall()}

        conn.close()
        assert cols_before == cols_after, (
            f"Idempotency violated: create_table() second call changed schema. "
            f"Before: {cols_before}; After: {cols_after}"
        )

    def test_pre_t1_3_db_state_migration_adds_columns_preserves_rows(self, tmp_path: Path) -> None:
        """Scenario 2: simulate pre-T1.3 DB (no cost_anchor_id) → migration adds 9 columns + preserves rows."""
        from backtest.experiment_registry import create_table, MIGRATION_COLUMNS

        db_path = tmp_path / "pre_t1_3.db"
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row

        # Create minimal pre-T1.3 table (without T1.x columns)
        conn.execute("""
            CREATE TABLE runs (
                run_id TEXT PRIMARY KEY,
                strategy_name TEXT
            )
        """)
        # Insert a pre-T1.3 row
        conn.execute("INSERT INTO runs (run_id, strategy_name) VALUES (?, ?)",
                     ("pre-t1-3-row", "legacy_strategy"))
        conn.commit()

        # Run migration
        create_table(conn)

        # Verify all 9 T1.x columns now present
        cols = {row[1] for row in conn.execute("PRAGMA table_info(runs)").fetchall()}
        for t1x_col in _T1X_NEW_COLUMNS:
            assert t1x_col in cols, f"Migration failed to add column: {t1x_col}"

        # Verify pre-T1.3 row preserved with NULL on new columns
        row = conn.execute("SELECT * FROM runs WHERE run_id = ?", ("pre-t1-3-row",)).fetchone()
        assert row is not None, "Pre-T1.3 row must be preserved through migration"
        assert row["strategy_name"] == "legacy_strategy"
        for t1x_col in _T1X_NEW_COLUMNS:
            assert row[t1x_col] is None, (
                f"Pre-T1.3 row must have NULL on new column {t1x_col}; got {row[t1x_col]!r}"
            )

        conn.close()

    def test_partial_migration_state_adds_remaining_columns(self, tmp_path: Path) -> None:
        """Scenario 3: partial-migration (cost_anchor_id present, T1.1 columns missing) → adds remaining."""
        from backtest.experiment_registry import create_table

        db_path = tmp_path / "partial.db"
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row

        # Create partial-migration table (with cost_anchor_id but NOT T1.1 columns)
        conn.execute("""
            CREATE TABLE runs (
                run_id TEXT PRIMARY KEY,
                cost_anchor_id TEXT
            )
        """)
        # Insert a partial-migration row
        conn.execute(
            "INSERT INTO runs (run_id, cost_anchor_id) VALUES (?, ?)",
            ("partial-row", "legacy_perp_inspired_7bps_v0"),
        )
        conn.commit()

        # Run migration
        create_table(conn)

        cols = {row[1] for row in conn.execute("PRAGMA table_info(runs)").fetchall()}
        # All 9 T1.x columns now present
        for t1x_col in _T1X_NEW_COLUMNS:
            assert t1x_col in cols

        # Verify partial-migration row preserved + cost_anchor_id unchanged
        row = conn.execute("SELECT * FROM runs WHERE run_id = ?", ("partial-row",)).fetchone()
        assert row is not None
        assert row["cost_anchor_id"] == "legacy_perp_inspired_7bps_v0"
        # T1.1 columns NULL on preserved row
        for col in ("returns_per_bar_path", "returns_per_bar_sha256", "T_obs"):
            assert row[col] is None

        conn.close()

"""V4 reproducibility + G4-G7 gate tests for B-C-narrow Phase 3 fire.

Per Plan v3-Phase3 v6 Step 13.2. Tests authored RED before Task 14 fire.
GREEN expected at Step 14.5 after fire + fixture capture + V4 gate run.

Test count: 12 methods (PFR R1 ADOPT v2 + PFR R2 ADOPT v3 expansion):
  - 5 N=2 fixture tests per spec §6.4 (schema-version-bump drift catch)
  - 2 BLOCKING-5 carry from Phase 2 plan v3-Phase2 line 3651 (G6+G7 inline)
  - 4 all-39 V4 gate tests per CB3 PFR R1 ADOPT v2 (spec §4.2/§4.3 full coverage;
    all-39 G4 extended to all 4 subchecks per CB3-R2-H1 PFR R2 ADOPT v3)
  - 1 cross-FS G7 test per AM1 PFR R1 ADOPT v2 (st_dev guard coverage;
    AM1-CrossFS-R2-M5 substring tightening per PFR R2 ADOPT v3)

Per-test fixture design per CB2-R2-B1 PFR R2 ADOPT v3
(supersedes CB2 PFR R1 ADOPT v2 module-load `_resolve_active_run_dir` pattern):
  Tests work in BOTH pre-T14b state (sibling dir populated, canonical empty/absent)
  AND post-T14b state (sibling gone, canonical populated). Via per-test
  `active_run_dir` pytest fixture + per-test SKIP gate at G6 body checking
  registry parent row existence, the test suite satisfies CLAUDE.md HARD
  CONSTRAINT 'NEVER commit code that doesn't pass existing tests' across the
  T14b mv lifecycle (10 SKIPPED + 2 PASSED + 0 FAILED + 0 ERRORS pre-fire;
  12 PASSED post-fire). The 2 path-independent contract tests (G7 refuse +
  G7 cross-FS) always pass regardless of disk state. The drift-stop test now
  takes the `active_run_dir` fixture so it SKIPs pre-fire alongside the other
  fire-state tests; per H2-Advisor PFR R2 ADOPT v3 (Option A docstring
  reframing) its substantive value is in the error-message-format contract.

Fixture file: tests/fixtures/b_c_narrow_archived_baseline.json
  Captured at Step 14.3 POST-T13 fire BEFORE T14 V4 gate runs.
  Sources from data/phase2c_evaluation_gate/archive/phase4_forward_2026_15bps_v1_d0b8101/
  (created by producer W3 during the fire step).
  Captures N=2 candidates: 18d92ce5d0b40cc7 + 22864f01a49e3452
  (lexicographically smallest 2 hypothesis_hash from cohort_a; deterministic).
  N=2 fixture purpose: catch schema-version drift on JSON dict (which raw-CSV
  all-39 comparison at the all-39 V4 gate tests would miss).

Spec references:
  §4.2 V4 reproducibility gate (BLOCKING for SEAL): ε=1e-6 floats; exact int+bool
  §4.3 G4-G7 gate semantics
  §6.4 V4 reproducibility test enumeration
  §6.6 Fixture strategy (specific-keys-only N=2 sample)
"""
from __future__ import annotations

import csv
import hashlib
import json
import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SIBLING_RUN_DIR = (
    PROJECT_ROOT
    / "data"
    / "phase2c_evaluation_gate"
    / "phase4_forward_2026_15bps_v1_b_c_narrow"
)
CANONICAL_RUN_DIR = (
    PROJECT_ROOT
    / "data"
    / "phase2c_evaluation_gate"
    / "phase4_forward_2026_15bps_v1"
)
ARCHIVE_RUN_DIR = (
    PROJECT_ROOT
    / "data"
    / "phase2c_evaluation_gate"
    / "archive"
    / "phase4_forward_2026_15bps_v1_d0b8101"
)
# CB2-SE-B1 PFR SEAL-eve R1 ADOPT v7: B-C-narrow recovery marker.
# The W3 archive operation creates this file as part of T13 fire.
# Pre-fire CANONICAL_RUN_DIR exists (Phase 2 baseline populated it) — must NOT
# fall through to that path when fire has not run. Archive marker presence is
# the unique B-C-narrow-state precondition (Phase 2 baseline never created this
# archive directory).
#
# L1-Advisor-R2 PFR SEAL-eve R2 ADOPT v8: invariant uniqueness DEFENSIVE NOTE.
# The `_d0b8101` git-sha suffix in ARCHIVE_RUN_DIR is the B-C-narrow
# CORRECTED_WF_ENGINE_COMMIT-derived basename (per spec §2 Q3 = A3 +
# Phase 2 BCNARROW_ARCHIVE_BASENAME constant at scripts:117-ish). No other
# cycle should ever write to this exact path because:
#   (a) The suffix is derived from a specific git commit hash, making it
#       cycle-unique by construction
#   (b) Phase 2 producer W3 is the ONLY code path that creates this archive
#       (per producer scripts:1146 + scripts:1175 shutil.move atomic transplant)
#   (c) Spec §3.2.4 + §4.3 G7 refuse-if-exists guards against double-creation
# If a future hypothetical cycle were to write to this exact path (extremely
# unlikely given the suffix uniqueness), this marker check would pass falsely
# and tests would run against the wrong cycle's archive. Per Advisor SEAL-eve
# R2 LOW: severity LOW because suffix is provably unique to B-C-narrow.
ARCHIVE_MARKER_FILE = ARCHIVE_RUN_DIR / "holdout_results.csv"
FIXTURE_PATH = (
    PROJECT_ROOT / "tests" / "fixtures" / "b_c_narrow_archived_baseline.json"
)


@pytest.fixture
def active_run_dir() -> Path:
    """Per-test fixture: resolve active B-C-narrow run dir based on fire state.

    CB2-SE-B1 PFR SEAL-eve R1 ADOPT v7: pre-fire fall-through fix. Phase 2 baseline
    populated CANONICAL_RUN_DIR before B-C-narrow Phase 3 fire; pre-fire fixture must
    NOT return CANONICAL_RUN_DIR (would run tests against Phase 2 content). The
    archive marker file is uniquely created by W3 during T13 fire — its presence is
    the B-C-narrow-state precondition.

    State machine:
    - Pre-fire (no archive): SKIP — neither B-C-narrow sibling nor B-C-narrow canonical exists yet
    - Post-T13 pre-T14b (sibling + archive both exist): return SIBLING_RUN_DIR
    - Post-T14b (canonical + archive exist; sibling gone): return CANONICAL_RUN_DIR

    Codex SEAL-eve R1 empirical pytest run on v6 caught the pre-fire fall-through bug
    (10 FAILED instead of 10 SKIPPED). Advisor SEAL-eve R1 static read missed it.

    CB2-R2-B1 PFR R2 ADOPT v3 (carried): refactored from module-load
    `_resolve_active_run_dir()` + module-level `ACTIVE_RUN_DIR` constant. Module-load
    `pytest.skip()` would have required `allow_module_level=True` parameter (else
    collection error per `_pytest/python.py:543-550`); even with that, all fire-state
    tests share a single cached resolution outcome — making per-test SKIP behavior
    coarser. The per-test fixture pattern is cleaner: each fire-state test takes
    `active_run_dir` parameter; tests that do NOT need the run dir (G7 refuse +
    G7 cross-FS) skip taking the fixture entirely.
    """
    if not ARCHIVE_MARKER_FILE.exists():
        pytest.skip(
            "Phase 3 B-C-narrow fire not yet executed — archive marker absent at "
            f"{ARCHIVE_MARKER_FILE}. Pre-fire CANONICAL_RUN_DIR contains Phase 2 baseline "
            "content (NOT B-C-narrow recovery output); skipping fire-state tests until "
            "T13 producer fire writes the archive marker via W3."
        )
    if SIBLING_RUN_DIR.exists():
        return SIBLING_RUN_DIR
    if CANONICAL_RUN_DIR.exists():
        return CANONICAL_RUN_DIR
    # Defensive: archive exists but neither dir → partial-state failure mode (corrupt cycle)
    pytest.skip(
        f"Archive marker present but neither SIBLING_RUN_DIR nor CANONICAL_RUN_DIR exists; "
        "partial-state failure — manual cleanup required per R9 compensating-cleanup."
    )


# CB2-R2-B1 PFR R2 ADOPT v3: removed module-load `ACTIVE_RUN_DIR = _resolve_active_run_dir()`
# constant. Per-test fixture pattern above replaces it. Resolves Module-Side-L4 (no
# module-import-time side effects + no `allow_module_level=True` wart).

# Locked sample candidates per Plan v3-Phase3 fixture sampling rule:
# lexicographically smallest 2 hypothesis_hash strings from cohort_a.
SAMPLE_HASHES = ["18d92ce5d0b40cc7", "22864f01a49e3452"]

# V4 ε tolerance per spec §4.2
V4_EPSILON = 1e-6

# G5 tolerance per spec §4.3 (γ3/γ4 round-trip)
G5_EPSILON = 1e-10

BCNARROW_PARENT_RUN_ID = "phase4_forward_2026_15bps_v1_b_c_narrow"


def _load_summary(run_dir: Path, hypothesis_hash: str) -> dict:
    """Load holdout_summary.json for a candidate from a run directory."""
    summary_path = run_dir / hypothesis_hash / "holdout_summary.json"
    assert summary_path.exists(), (
        f"holdout_summary.json missing for candidate {hypothesis_hash} "
        f"at {summary_path} (precondition: fire+archive complete)"
    )
    with summary_path.open() as f:
        return json.load(f)


def _load_fixture() -> dict:
    """Load the V4 baseline fixture (N=2 candidates; specific keys).

    The N=2 fixture sample exists to catch schema-version drift on the
    JSON dict layer (which the all-39 raw-CSV V4 gate would miss).
    """
    assert FIXTURE_PATH.exists(), (
        f"V4 baseline fixture missing at {FIXTURE_PATH}. "
        "Per Plan v3-Phase3 Step 14.3, this fixture is captured POST-T13 fire "
        "BEFORE T14 V4 gate runs. If fixture is missing, fire has not yet "
        "produced the archive, OR Step 14.3 fixture-capture sub-step was skipped."
    )
    with FIXTURE_PATH.open() as f:
        return json.load(f)


def _load_all_39_candidates_from_csv(run_dir: Path) -> dict:
    """Load all 39 candidates from holdout_results.csv as dict[hash] = row.

    Per CB3 PFR R1 ADOPT v2: all-39 V4 gate reads raw CSV (NOT specific-keys
    fixture) to satisfy spec §4.2 + §4.3 per-candidate full-cohort coverage.

    AL4-R3 PFR R3 ADOPT v4: defensive duplicate-hash check.
    csv.DictReader → dict pattern silently overwrites duplicate keys. Impossible
    in canonical CSV by construction (39 hashes uniquely set per Step 13.1(h)
    drift check), but defensive for future-proofing if CSV producer ever drifts.
    """
    csv_path = run_dir / "holdout_results.csv"
    assert csv_path.exists(), (
        f"holdout_results.csv missing at {csv_path} (precondition: fire complete)"
    )
    with csv_path.open() as f:
        rows = {}
        seen_hashes = set()
        for row in csv.DictReader(f):
            hh = row["hypothesis_hash"]
            if hh in seen_hashes:
                raise ValueError(
                    f"AL4-R3 duplicate hypothesis_hash in CSV: {hh} "
                    f"(producer drift caught at {csv_path})"
                )
            seen_hashes.add(hh)
            rows[hh] = row
    assert len(rows) == 39, (
        f"all-39 V4 gate expected 39 candidate rows in CSV, got {len(rows)} "
        f"at {csv_path}"
    )
    return rows


class TestV4Reproducibility:
    """V4 per-candidate metric reproducibility — sibling vs archived original."""

    def test_v4_per_candidate_metric_diff_within_epsilon(self, active_run_dir: Path) -> None:
        """Each sampled (N=2) candidate's 3 float metrics match archive within ε=1e-6.

        Spec §4.2 + §6.4: sharpe_ratio + max_drawdown + total_return float
        metrics match between sibling new artifact and archived original to
        within absolute tolerance ε=1e-6. Drift > ε → SEAL BLOCKED pending
        Charlie register adjudication.

        N=2 sample catches JSON-dict-layer schema drift; CB3 ADOPT v2 all-39
        test below covers full cohort directly from CSV.

        CB2-R2-B1 PFR R2 ADOPT v3: takes `active_run_dir` per-test fixture.
        """
        fixture = _load_fixture()
        for hh in SAMPLE_HASHES:
            new_summary = _load_summary(active_run_dir, hh)
            old_metrics = fixture[hh]["holdout_metrics"]
            new_metrics = new_summary["holdout_metrics"]
            for metric_name in ("sharpe_ratio", "max_drawdown", "total_return"):
                old_val = float(old_metrics[metric_name])
                new_val = float(new_metrics[metric_name])
                diff = abs(new_val - old_val)
                assert diff < V4_EPSILON, (
                    f"V4 drift on candidate {hh} metric {metric_name}: "
                    f"old={old_val!r} new={new_val!r} abs_diff={diff!r} "
                    f"exceeds ε={V4_EPSILON} (spec §4.2 strict stop-condition)"
                )

    def test_v4_total_trades_exact_match(self, active_run_dir: Path) -> None:
        """Each sampled (N=2) candidate's total_trades (int) + holdout_passed (bool)
        + 4 gate_pass_per_criterion subfields match archive EXACTLY (no ε).

        Spec §4.2 + §6.4: integer + bool values use exact equality (NO tolerance).

        CB2-R2-B1 PFR R2 ADOPT v3: takes `active_run_dir` per-test fixture.
        """
        fixture = _load_fixture()
        for hh in SAMPLE_HASHES:
            new_summary = _load_summary(active_run_dir, hh)
            old_fix = fixture[hh]
            new_total_trades = int(new_summary["holdout_metrics"]["total_trades"])
            old_total_trades = int(old_fix["holdout_metrics"]["total_trades"])
            assert new_total_trades == old_total_trades, (
                f"V4 total_trades exact-match FAIL on {hh}: "
                f"old={old_total_trades} new={new_total_trades}"
            )
            new_passed = bool(new_summary["holdout_passed"])
            old_passed = bool(old_fix["holdout_passed"])
            assert new_passed == old_passed, (
                f"V4 holdout_passed exact-match FAIL on {hh}: "
                f"old={old_passed} new={new_passed}"
            )
            for subfield in (
                "drawdown_passed",
                "return_passed",
                "sharpe_passed",
                "trades_passed",
            ):
                old_sub = bool(old_fix["gate_pass_per_criterion"][subfield])
                new_sub = bool(new_summary["gate_pass_per_criterion"][subfield])
                assert new_sub == old_sub, (
                    f"V4 gate_pass_per_criterion.{subfield} exact-match FAIL "
                    f"on {hh}: old={old_sub} new={new_sub}"
                )

    def test_v4_drift_stop_condition_blocks_seal_on_breach(self, active_run_dir: Path) -> None:
        """Contract test for drift-stop error message format + meta-test that
        inlined assertion pattern raises AssertionError when given 10ε deviation.

        H2-Advisor PFR R2 ADOPT v3 (Option A docstring reframing): the previous
        v2 docstring overstated this test's scope. This test does NOT exercise the
        production ε-comparison machinery — that's covered by
        `test_v4_per_candidate_metric_diff_within_epsilon` (N=2) +
        `test_v4_all_39_per_candidate_metric_diff_within_epsilon` (all-39). Those
        tests would catch real ε breaches in the actual production code path.

        This test's substantive value is in the ERROR-MESSAGE-FORMAT contract:
        when a real ε breach occurs, the AssertionError must mention the
        candidate's hash so the operator can identify which candidate broke V4
        reproducibility. The test injects a synthetic 10×ε perturbation into
        one candidate's holdout_sharpe, runs an inlined ε-comparison loop that
        mirrors the production pattern, and asserts the AssertionError message
        contains the perturbed candidate's hash.

        Procedure:
          1. Loads all-39 archived rows + all-39 new rows
          2. Picks the first candidate (by lex-sorted hash)
          3. Injects a synthetic perturbation of 10×ε into that candidate's
             holdout_sharpe value
          4. Runs an inlined ε-comparison (NOT the production V4 test method —
             that's separately covered)
          5. Asserts AssertionError raised AND that the error message mentions
             the perturbed candidate's hash

        Locks the error-message contract for spec §4.2 stop-condition behavior.

        CB2-R2-B1 PFR R2 ADOPT v3: takes `active_run_dir` per-test fixture.

        AM2-R3 PFR R3 ADOPT v4: drift-stop test currently scopes to
        holdout_sharpe only (semantically = sharpe_ratio per metric_map below).
        If V4 metric set widens (e.g., adding total_trades drift via int-
        rounding contract, or max_drawdown / total_return permutations), the
        drift-stop test would need extension to cover those metric classes.
        NAMED-eligible-for-extension at Phase 4 SEAL bundle if metric set
        widens.
        """
        archive_rows = _load_all_39_candidates_from_csv(ARCHIVE_RUN_DIR)
        new_rows = _load_all_39_candidates_from_csv(active_run_dir)
        perturbed_hash = sorted(archive_rows.keys())[0]
        # Inject synthetic 10×ε perturbation into one candidate's holdout_sharpe
        # AM2-R3 PFR R3 ADOPT v4: scope = sharpe_ratio only (single-metric
        # contract-test); not full per-metric coverage (other V4 tests cover
        # max_drawdown + total_return + total_trades + bool subfields).
        perturbed_sharpe = (
            float(archive_rows[perturbed_hash]["holdout_sharpe"]) + 10 * V4_EPSILON
        )
        with pytest.raises(AssertionError) as exc_info:
            for hh in sorted(archive_rows.keys()):
                old_val = float(archive_rows[hh]["holdout_sharpe"])
                if hh == perturbed_hash:
                    new_val = perturbed_sharpe  # synthetic injection
                else:
                    new_val = float(new_rows[hh]["holdout_sharpe"])
                diff = abs(new_val - old_val)
                assert diff < V4_EPSILON, (
                    f"V4 drift on candidate {hh} metric holdout_sharpe: "
                    f"old={old_val!r} new={new_val!r} abs_diff={diff!r} "
                    f"exceeds ε={V4_EPSILON} (spec §4.2 strict stop-condition)"
                )
        assert perturbed_hash in str(exc_info.value), (
            f"V4 stop-condition error message must mention perturbed candidate "
            f"hash {perturbed_hash}. Got: {exc_info.value!r}"
        )

    def test_v4_all_39_per_candidate_metric_diff_within_epsilon(self, active_run_dir: Path) -> None:
        """All 39 candidates' 3 float metrics match archive within ε=1e-6.

        CB3 PFR R1 ADOPT v2: reads archive + new CSV directly (NOT specific-
        keys fixture). Covers spec §4.2/§4.3 per-candidate full-cohort
        requirement that the N=2 fixture test does not satisfy.

        CB2-R2-B1 PFR R2 ADOPT v3: takes `active_run_dir` per-test fixture.
        """
        archive_rows = _load_all_39_candidates_from_csv(ARCHIVE_RUN_DIR)
        new_rows = _load_all_39_candidates_from_csv(active_run_dir)
        assert set(archive_rows.keys()) == set(new_rows.keys()), (
            f"CSV hash-set mismatch: archive has "
            f"{set(archive_rows.keys()) - set(new_rows.keys())} extra; "
            f"new has {set(new_rows.keys()) - set(archive_rows.keys())} extra"
        )
        # CSV column names per Step 13.1(b): holdout_sharpe, holdout_max_drawdown, holdout_total_return
        metric_map = {
            "holdout_sharpe": "sharpe_ratio",
            "holdout_max_drawdown": "max_drawdown",
            "holdout_total_return": "total_return",
        }
        for hh in sorted(archive_rows.keys()):
            old_row = archive_rows[hh]
            new_row = new_rows[hh]
            for csv_col, metric_name in metric_map.items():
                old_val = float(old_row[csv_col])
                new_val = float(new_row[csv_col])
                diff = abs(new_val - old_val)
                assert diff < V4_EPSILON, (
                    f"V4 all-39 drift on candidate {hh} metric {metric_name}: "
                    f"old={old_val!r} new={new_val!r} abs_diff={diff!r} "
                    f"exceeds ε={V4_EPSILON} (spec §4.2 strict stop-condition)"
                )

    def test_v4_all_39_total_trades_exact_match(self, active_run_dir: Path) -> None:
        """All 39 candidates' total_trades (int) + holdout_passed (bool) +
        gate_pass_per_criterion 4 subfields (bools) match exactly.

        CB3 PFR R1 ADOPT v2: exact-equality coverage for full cohort.

        CB2-R2-B1 PFR R2 ADOPT v3: takes `active_run_dir` per-test fixture.

        AM1-R5 PFR R5 ADOPT v6: extended to iterate per-candidate
        `holdout_summary.json` files at all-39 layer to assert
        `gate_pass_per_criterion` 4 subfields exact match per spec §4.2 line 229
        verbatim ("`gate_pass_per_criterion` 4 subfields: each exact match").
        v5 covered only CSV-column fields (`holdout_total_trades` + `holdout_passed`);
        gate_pass_per_criterion is JSON-only (not surfaced as CSV columns). N=2
        fixture test (`test_v4_total_trades_exact_match` above) already covers
        gate_pass at fixture-layer; replicating at all-39 layer closes spec
        literal coverage gap. Advisor R5 M1 acknowledged logical-implication
        mitigation (deterministic AND-gate; if 4 subfields all True per
        sub-criterion gate produces holdout_passed) was NOT sufficient for spec
        literal compliance. Subfield names verified at producer
        scripts/run_phase2c_evaluation_gate.py:504-518: `sharpe_passed` +
        `drawdown_passed` + `return_passed` + `trades_passed` (matches N=2 test
        loop at this file's earlier `test_v4_total_trades_exact_match`).
        """
        archive_rows = _load_all_39_candidates_from_csv(ARCHIVE_RUN_DIR)
        new_rows = _load_all_39_candidates_from_csv(active_run_dir)
        for hh in sorted(archive_rows.keys()):
            old_row = archive_rows[hh]
            new_row = new_rows[hh]
            old_trades = int(old_row["holdout_total_trades"])
            new_trades = int(new_row["holdout_total_trades"])
            assert new_trades == old_trades, (
                f"V4 all-39 total_trades exact-match FAIL on {hh}: "
                f"old={old_trades} new={new_trades}"
            )
            # holdout_passed CSV column is boolean-ish string (e.g. 'True'/'False')
            old_passed = str(old_row["holdout_passed"]).strip().lower() in {"true", "1"}
            new_passed = str(new_row["holdout_passed"]).strip().lower() in {"true", "1"}
            assert new_passed == old_passed, (
                f"V4 all-39 holdout_passed exact-match FAIL on {hh}: "
                f"old={old_row['holdout_passed']!r} new={new_row['holdout_passed']!r}"
            )
            # AM1-R5 PFR R5 ADOPT v6: spec §4.2 line 229 requires
            # gate_pass_per_criterion 4 subfields exact match at all-39 layer.
            # JSON-only field (not surfaced in CSV); load per-candidate summaries
            # from archive + sibling/canonical run dirs.
            archive_summary_path = (
                ARCHIVE_RUN_DIR / hh / "holdout_summary.json"
            )
            new_summary_path = active_run_dir / hh / "holdout_summary.json"
            assert archive_summary_path.exists(), (
                f"AM1-R5 V4 all-39 {hh}: archive holdout_summary.json missing at "
                f"{archive_summary_path}"
            )
            assert new_summary_path.exists(), (
                f"AM1-R5 V4 all-39 {hh}: new holdout_summary.json missing at "
                f"{new_summary_path}"
            )
            archive_summary = json.loads(archive_summary_path.read_text())
            new_summary = json.loads(new_summary_path.read_text())
            archive_gate_pass = archive_summary.get("gate_pass_per_criterion")
            new_gate_pass = new_summary.get("gate_pass_per_criterion")
            assert archive_gate_pass is not None, (
                f"AM1-R5 V4 all-39 {hh}: archive summary missing "
                f"gate_pass_per_criterion (top-level None — producer skipped "
                f"gate evaluation at scripts:527?)"
            )
            assert new_gate_pass is not None, (
                f"AM1-R5 V4 all-39 {hh}: new summary missing "
                f"gate_pass_per_criterion (top-level None)"
            )
            # Spec §4.2 line 229: 4 subfields exact match (bool comparison; NO ε
            # tolerance). Subfield names per producer scripts:504-518.
            expected_subfields = (
                "sharpe_passed",
                "drawdown_passed",
                "return_passed",
                "trades_passed",
            )
            for subfield in expected_subfields:
                assert subfield in archive_gate_pass, (
                    f"AM1-R5 V4 all-39 {hh}: archive summary missing "
                    f"gate_pass_per_criterion.{subfield}"
                )
                assert subfield in new_gate_pass, (
                    f"AM1-R5 V4 all-39 {hh}: new summary missing "
                    f"gate_pass_per_criterion.{subfield}"
                )
                old_sub = bool(archive_gate_pass[subfield])
                new_sub = bool(new_gate_pass[subfield])
                assert new_sub == old_sub, (
                    f"AM1-R5 V4 all-39 gate_pass_per_criterion.{subfield} "
                    f"exact-match FAIL on {hh}: old={old_sub} new={new_sub}. "
                    f"Spec §4.2 line 229 requires EXACT match (bool, no ε)."
                )


class TestG4ParquetIntegrity:
    """G4 per-bar parquet integrity gate."""

    def test_g4_per_bar_parquet_row_count_matches_t_obs(self, active_run_dir: Path) -> None:
        """Per-bar parquet finite-return count must equal T_obs from summary;
        SHA256 must match summary AND registry; data must be non-degenerate;
        timestamp UTC-aware.

        Spec §4.3 G4: (a) finite-row count = T_obs from summary; (b) SHA256 of
        file = `returns_per_bar_sha256` in summary + registry; (c) data not
        all-NaN; (d) `timestamp` column UTC-aware (parquet writes `timestamp`
        as a column not as the index per engine.py:498-510).

        CH4 PFR R1 ADOPT v2: extended to query registry per-candidate row and
        assert returns_per_bar_path + returns_per_bar_sha256 + T_obs all match
        across summary + computed + registry (not just summary as v1 claimed).

        G4-R2-B2 PFR R2 ADOPT v3 (Option C — most defensive):
          Engine VERIFIED: `write_per_bar_artifact` (backtest/engine.py:530-545)
          writes full `equity_curve` (length includes leading bar) as parquet
          with `return` column having first row NaN. `T_obs` = `count(finite(
          returns_array))` excludes the leading NaN. So `len(df) == T_obs + 1`
          typically (not `len(df) == T_obs`).
          Existing `test_t_obs_matches_finite_row_count` at
          `tests/test_t1_1_artifact_writer.py:546-560` confirms by asserting
          `result["T_obs"] == count(finite(parquet.return))`.
          Fix: assert finite-return count = T_obs at the application level via
          `df.dropna(subset=['return'])`. This is engine-behavior-agnostic
          (works whether engine trims or keeps leading NaN row).

        CB2-R2-B1 PFR R2 ADOPT v3: takes `active_run_dir` per-test fixture.

        CH4-R2-M1 PFR R2 ADOPT v3: tightened path assertion (CH4-a) below from
        substring `in` to equality with expected basename `returns_per_bar.parquet`.
        """
        from backtest.experiment_registry import get_connection, DEFAULT_DB_PATH, get_run

        conn = get_connection(DEFAULT_DB_PATH)
        try:
            for hh in SAMPLE_HASHES:
                summary = _load_summary(active_run_dir, hh)
                candidate_dir = active_run_dir / hh
                parquet_path = candidate_dir / "returns_per_bar.parquet"
                assert parquet_path.exists(), (
                    f"G4 missing parquet for candidate {hh} at {parquet_path}"
                )
                # (a) finite-return count = T_obs (G4-R2-B2 Option C: defensive)
                # AH2-R3 PFR R3 ADOPT v4: replaced .notna() with np.isfinite() to
                # bit-mirror engine semantics. Engine compute_moments uses
                # np.isfinite(arr) (engine.py:444-446) which excludes NaN AND ±inf.
                # For BTC pct_change essentially unreachable difference (no
                # divide-by-zero), but methodologically bit-equivalent to engine.
                df = pd.read_parquet(parquet_path)
                t_obs_summary = int(summary["T_obs"])
                finite_row_count = int(np.isfinite(df["return"]).sum())
                assert finite_row_count == t_obs_summary, (
                    f"G4(a) finite-return count mismatch on {hh}: "
                    f"finite_rows={finite_row_count} summary T_obs={t_obs_summary} "
                    f"(parquet total rows={len(df)} including leading-NaN row per "
                    f"engine.py:530-545)"
                )
                # (b) SHA256 match — summary + computed + registry tri-way
                hasher = hashlib.sha256()
                with parquet_path.open("rb") as fh:
                    for chunk in iter(lambda: fh.read(65536), b""):
                        hasher.update(chunk)
                computed_sha = hasher.hexdigest()
                stored_sha = summary["returns_per_bar_sha256"]
                assert computed_sha == stored_sha, (
                    f"G4(b) SHA256 summary-vs-computed mismatch on {hh}: "
                    f"computed={computed_sha!r} stored_in_summary={stored_sha!r}"
                )
                # (c) data not all-NaN (degenerate write)
                assert not df["return"].isna().all(), (
                    f"G4(c) degenerate parquet on {hh}: all `return` values NaN"
                )
                # (d) timestamp column UTC-aware (column not index)
                assert "timestamp" in df.columns, (
                    f"G4(d) parquet missing `timestamp` column on {hh}: "
                    f"columns={list(df.columns)}"
                )
                ts_dtype = df["timestamp"].dtype
                assert pd.api.types.is_datetime64_any_dtype(ts_dtype), (
                    f"G4(d) timestamp column dtype non-datetime on {hh}: {ts_dtype}"
                )
                tz = getattr(ts_dtype, "tz", None)
                assert tz is not None and str(tz) in ("UTC", "utc"), (
                    f"G4(d) timestamp column not UTC-aware on {hh}: tz={tz!r}"
                )
                # CH4 PFR R1 ADOPT v2: registry row query + per-candidate linkage
                # The child run_id in the registry is per-candidate; query by
                # parent_run_id + candidate-specific identifier (hypothesis_hash
                # is the per-child run_id naming under the producer's LC-b path).
                # AM1-R3 PFR R3 ADOPT v4: Sub-1 reopened. Producer scheme is
                # `f"{run_id}_{hh}"` (scripts:582); equality lookup is safer than
                # LIKE substring (no spoofable substring collisions). Sub-1 ACCEPT
                # preserve at PFR R2 was conservative for v3; Advisor R3 M1 reopens.
                child_run_id = f"{BCNARROW_PARENT_RUN_ID}_{hh}"
                cur = conn.cursor()
                cur.execute(
                    "SELECT run_id FROM runs WHERE run_id = ? AND run_type = ?",
                    (child_run_id, "regime_holdout"),
                )
                child_id_row = cur.fetchone()
                assert child_id_row is not None, (
                    f"CH4 G4 registry lookup FAIL on {hh}: no child run row "
                    f"found at run_id={child_run_id!r} (producer scheme "
                    f"f'{{run_id}}_{{hh}}' per scripts:582)"
                )
                child_row = get_run(conn, child_run_id)
                assert child_row is not None, (
                    f"CH4 G4 get_run returned None for child_run_id={child_run_id!r}"
                )
                # (CH4-a) returns_per_bar_path stored matches expected basename exactly
                # CH4-R2-M1 PFR R2 ADOPT v3: tightened from substring `in` to equality.
                # Per Phase 0 SEAL: registry stores BASENAME only ("returns_per_bar.parquet"),
                # not absolute path. Substring would also match e.g.
                # "broken_returns_per_bar.parquet.bak" — equality forecloses that drift class.
                expected_path_basename = "returns_per_bar.parquet"
                stored_path = child_row.get("returns_per_bar_path")
                assert stored_path == expected_path_basename, (
                    f"CH4 G4 child registry returns_per_bar_path FAIL on {hh}: "
                    f"expected exactly {expected_path_basename!r}, "
                    f"got {stored_path!r}"
                )
                # (CH4-b) SHA256 in registry = computed = summary (tri-way)
                stored_registry_sha = child_row.get("returns_per_bar_sha256")
                assert stored_registry_sha == computed_sha == stored_sha, (
                    f"CH4 G4 SHA256 tri-way mismatch on {hh}: "
                    f"computed={computed_sha!r} summary={stored_sha!r} "
                    f"registry={stored_registry_sha!r}"
                )
                # (CH4-c) T_obs in registry = finite-return count = summary
                # CB1-R3 PFR R3 ADOPT v4: back-port Option C from all-39 G4 to N=2 G4 site.
                # v3 applied Option C at all-39 sites (plan:765-773 + 896-902) but missed
                # N=2 back-port. Engine writes leading NaN row (engine.py:530-545); T_obs
                # is finite-return count (NOT len(df)). Original v3 assertion
                # `int(stored_registry_t_obs) == len(df) == t_obs_summary` would FAIL because
                # len(df) typically == T_obs + 1.
                stored_registry_t_obs = child_row.get("T_obs")
                assert (
                    int(stored_registry_t_obs)
                    == finite_row_count
                    == t_obs_summary
                ), (
                    f"CH4 G4 T_obs tri-way mismatch on {hh}: "
                    f"finite_rows={finite_row_count} summary T_obs={t_obs_summary} "
                    f"registry T_obs={stored_registry_t_obs} "
                    f"(parquet total rows={len(df)} including leading-NaN row per "
                    f"engine.py:530-545)"
                )
        finally:
            conn.close()

    def test_g4_all_39_per_bar_parquet_integrity(self, active_run_dir: Path) -> None:
        """All 39 candidates: per-bar parquet — all 4 spec §4.3 G4 subchecks.

        CB3 PFR R1 ADOPT v2: extends G4 coverage to full cohort. Per-candidate
        N=2 deep validation above + this all-39 check together satisfy spec
        §4.3 G4 full-cohort coverage requirement.

        CB3-R2-H1 PFR R2 ADOPT v3: extended from v2's (a)+(b) to all 4 subchecks
        per spec §4.3:
          (a) finite-row count = T_obs from summary (G4-R2-B2 Option C —
              defensive, engine-behavior-agnostic via dropna)
          (b) SHA256 tri-way (file → summary → registry)
          (c) data not all-NaN AND not all-zero (non-degenerate write)
          (d) `timestamp` column UTC-aware (column not index)

        CB2-R2-B1 PFR R2 ADOPT v3: takes `active_run_dir` per-test fixture.

        AM1-R3 PFR R3 ADOPT v4: Sub-1 reopened. LIKE substring pattern replaced
        with equality. Producer scheme IS known: `f"{run_id}_{hh}"` at scripts:582.
        Sub-1 ACCEPT preserve at PFR R2 was conservative for v3; Advisor R3 M1
        reopens — equality is safer + tighter (no spoofable substring collisions).
        """
        from backtest.experiment_registry import get_connection, DEFAULT_DB_PATH

        all_39_csv_rows = _load_all_39_candidates_from_csv(active_run_dir)
        conn = get_connection(DEFAULT_DB_PATH)
        try:
            cur = conn.cursor()
            for hh in sorted(all_39_csv_rows.keys()):
                candidate_dir = active_run_dir / hh
                parquet_path = candidate_dir / "returns_per_bar.parquet"
                summary = _load_summary(active_run_dir, hh)
                assert parquet_path.exists(), (
                    f"G4 all-39 missing parquet for candidate {hh}"
                )
                df = pd.read_parquet(parquet_path)
                assert len(df) > 0, (
                    f"G4 all-39 empty parquet for candidate {hh}"
                )
                # (a) finite-return count = T_obs (G4-R2-B2 Option C)
                # AH2-R3 PFR R3 ADOPT v4: replaced .notna() with np.isfinite() to
                # bit-mirror engine semantics (compute_moments uses np.isfinite
                # at engine.py:444-446 — excludes NaN AND ±inf).
                t_obs_summary = int(summary["T_obs"])
                finite_row_count = int(np.isfinite(df["return"]).sum())
                assert finite_row_count == t_obs_summary, (
                    f"G4(a) all-39 finite-return count mismatch on {hh}: "
                    f"finite_rows={finite_row_count} summary T_obs={t_obs_summary} "
                    f"(parquet total rows={len(df)} including leading-NaN row)"
                )
                # (b) SHA256 tri-way — file + summary + registry
                hasher = hashlib.sha256()
                with parquet_path.open("rb") as fh:
                    for chunk in iter(lambda: fh.read(65536), b""):
                        hasher.update(chunk)
                computed_sha = hasher.hexdigest()
                stored_sha_summary = summary["returns_per_bar_sha256"]
                assert computed_sha == stored_sha_summary, (
                    f"G4(b) all-39 SHA256 summary-vs-computed mismatch on {hh}: "
                    f"computed={computed_sha!r} summary={stored_sha_summary!r}"
                )
                # AM1-R3 PFR R3 ADOPT v4: Sub-1 reopened. Producer scheme is
                # f"{run_id}_{hh}" (scripts:582); equality lookup is safer than LIKE
                # substring (no spoofable substring collisions).
                child_run_id = f"{BCNARROW_PARENT_RUN_ID}_{hh}"
                cur.execute(
                    "SELECT returns_per_bar_sha256 FROM runs WHERE "
                    "run_id = ? AND run_type = ?",
                    (child_run_id, "regime_holdout"),
                )
                row = cur.fetchone()
                assert row is not None, (
                    f"G4(b) all-39 registry lookup FAIL on {hh}: "
                    f"run_id={child_run_id!r}"
                )
                assert row[0] == computed_sha, (
                    f"G4(b) all-39 SHA256 registry-vs-computed mismatch on {hh}: "
                    f"computed={computed_sha!r} registry={row[0]!r}"
                )
                # (c) CB3-R2-H1 PFR R2 ADOPT v3: data not all-NaN AND not all-zero
                # (degenerate write detection)
                assert finite_row_count > 0, (
                    f"G4(c) all-39 degenerate parquet on {hh}: zero finite rows"
                )
                returns_abs_sum = float(df["return"].abs().sum())
                assert returns_abs_sum > 0, (
                    f"G4(c) all-39 degenerate parquet on {hh}: "
                    f"all-zero returns (sum(|return|) == 0); constant equity curve"
                )
                # (d) CB3-R2-H1 PFR R2 ADOPT v3: timestamp column UTC-aware
                assert "timestamp" in df.columns, (
                    f"G4(d) all-39 parquet missing `timestamp` column on {hh}: "
                    f"columns={list(df.columns)}"
                )
                ts_dtype = df["timestamp"].dtype
                assert pd.api.types.is_datetime64_any_dtype(ts_dtype), (
                    f"G4(d) all-39 timestamp column dtype non-datetime on {hh}: "
                    f"{ts_dtype}"
                )
                tz = getattr(ts_dtype, "tz", None)
                assert tz is not None and str(tz) in ("UTC", "utc"), (
                    f"G4(d) all-39 timestamp column not UTC-aware on {hh}: "
                    f"tz={tz!r}"
                )
        finally:
            conn.close()


class TestG5GammaRoundTrip:
    """G5 γ3 / γ4 round-trip gate."""

    def test_g5_gamma_round_trip_from_parquet_within_epsilon(self, active_run_dir: Path) -> None:
        """Recompute γ3/γ4 from per-bar parquet via compute_moments; must
        match stored summary values within abs diff < 1e-10 (float64 round-trip
        determinism). T_obs must match bit-exact (integer).

        Spec §4.3 G5: load parquet → compute_moments(returns_array) → compare.

        AM2 PFR R1 ADOPT v2: This test reads df["return"] directly rather than
        recomposing via compute_per_bar_returns(equity_curve) as spec §6.4 line
        363 suggests. The two approaches are SEMANTICALLY EQUIVALENT (parquet's
        `return` column was written from compute_per_bar_returns output at
        engine.py:538; compute_moments' np.isfinite filter handles the leading
        NaN identically). The df["return"] approach is ADDITIONALLY MORE
        RIGOROUS because it validates the parquet column's round-trip integrity
        end-to-end (catches parquet write/read drift that the recompose
        approach would miss).

        CB2-R2-B1 PFR R2 ADOPT v3: takes `active_run_dir` per-test fixture.
        """
        from backtest.engine import compute_moments

        for hh in SAMPLE_HASHES:
            summary = _load_summary(active_run_dir, hh)
            candidate_dir = active_run_dir / hh
            parquet_path = candidate_dir / "returns_per_bar.parquet"
            assert parquet_path.exists(), (
                f"G5 missing parquet for candidate {hh}"
            )
            df = pd.read_parquet(parquet_path)
            returns_arr = df["return"].to_numpy(dtype=np.float64)
            moments = compute_moments(returns_arr)
            # T_obs bit-exact
            t_obs_recomputed = int(moments["T_obs"])
            t_obs_stored = int(summary["T_obs"])
            assert t_obs_recomputed == t_obs_stored, (
                f"G5 T_obs round-trip FAIL on {hh}: "
                f"recomputed={t_obs_recomputed} stored={t_obs_stored}"
            )
            # γ3 + γ4 within ε=1e-10
            for gamma_key in ("gamma3", "gamma4"):
                recomputed = moments[gamma_key]
                stored = summary[gamma_key]
                if recomputed is None and stored is None:
                    continue  # both None (insufficient T_obs); no compare
                assert recomputed is not None and stored is not None, (
                    f"G5 {gamma_key} None-asymmetry on {hh}: "
                    f"recomputed={recomputed!r} stored={stored!r}"
                )
                diff = abs(float(recomputed) - float(stored))
                assert diff < G5_EPSILON, (
                    f"G5 {gamma_key} round-trip drift on {hh}: "
                    f"recomputed={recomputed!r} stored={stored!r} "
                    f"abs_diff={diff!r} exceeds ε={G5_EPSILON}"
                )

    def test_g5_all_39_gamma_round_trip(self, active_run_dir: Path) -> None:
        """All 39 candidates: γ3/γ4 round-trip via compute_moments within ε=1e-10.

        CB3 PFR R1 ADOPT v2: full-cohort G5 coverage. Loads per-candidate
        holdout_summary.json (NOT the N=2 fixture) for each of the 39 candidates.

        CB2-R2-B1 PFR R2 ADOPT v3: takes `active_run_dir` per-test fixture.
        """
        from backtest.engine import compute_moments

        all_39_csv_rows = _load_all_39_candidates_from_csv(active_run_dir)
        for hh in sorted(all_39_csv_rows.keys()):
            summary = _load_summary(active_run_dir, hh)
            candidate_dir = active_run_dir / hh
            parquet_path = candidate_dir / "returns_per_bar.parquet"
            assert parquet_path.exists(), (
                f"G5 all-39 missing parquet for candidate {hh}"
            )
            df = pd.read_parquet(parquet_path)
            returns_arr = df["return"].to_numpy(dtype=np.float64)
            moments = compute_moments(returns_arr)
            t_obs_recomputed = int(moments["T_obs"])
            t_obs_stored = int(summary["T_obs"])
            assert t_obs_recomputed == t_obs_stored, (
                f"G5 all-39 T_obs round-trip FAIL on {hh}: "
                f"recomputed={t_obs_recomputed} stored={t_obs_stored}"
            )
            for gamma_key in ("gamma3", "gamma4"):
                recomputed = moments[gamma_key]
                stored = summary[gamma_key]
                if recomputed is None and stored is None:
                    continue
                assert recomputed is not None and stored is not None, (
                    f"G5 all-39 {gamma_key} None-asymmetry on {hh}: "
                    f"recomputed={recomputed!r} stored={stored!r}"
                )
                diff = abs(float(recomputed) - float(stored))
                assert diff < G5_EPSILON, (
                    f"G5 all-39 {gamma_key} round-trip drift on {hh}: "
                    f"abs_diff={diff!r} exceeds ε={G5_EPSILON}"
                )


class TestG6RegistryParentChildIntegrity:
    """G6 registry parent-child integrity gate."""

    def test_g6_registry_parent_child_integrity_after_fire(self) -> None:
        """Registry parent-child integrity after fire:
          - Parent row: 1 row at run_id=phase4_forward_2026_15bps_v1_b_c_narrow with
            run_type='batch_summary'; cohort-level metadata (14 direct columns
            per spec §3.2.3 line 117 + engine_commit via notes JSON per AH1-R3)
            non-null; batch_id == BCNARROW_PARENT_RUN_ID per G6-BatchID-R2-M4;
            **8 per-candidate fields NULL at parent** per Sub-2-R4-B1 (v5 CORRECTED
            from v4's 5-field list per empirical verification of producer
            scripts:1373-1381 + spec §3.2.3 line 118).
          - Children rows: 39 rows with parent_run_id = parent + run_type =
            'regime_holdout'; per-candidate metadata (hypothesis_hash + sharpe_ratio
            + max_drawdown + total_return + total_trades + regime_holdout_passed)
            non-null.
          - Note: per-candidate fields like returns_per_bar_path /
            returns_per_bar_sha256 / T_obs are persisted at children (per Phase 0
            LineageContext semantics) AND ALSO explicitly NULL'd at parent by
            producer scripts:1378-1381 (per spec §3.2.3 line 118 cohort/per-candidate
            metadata segregation). NULL-at-children assertion direction is structurally
            unimplementable; NULL-at-parent direction IS implemented at producer +
            covered by Sub-2-R4-B1 v5 (8 fields: 4 metric + 4 LC-b semantic).

        Spec §4.3 G6: SELECT COUNT(*) FROM runs WHERE
        parent_run_id='phase4_forward_2026_15bps_v1_b_c_narrow' AND
        run_type='regime_holdout' = 39; parent row exists with
        run_type='batch_summary'.

        BLOCKING-5 carry per Plan v3-Phase2 line 3651: G6 inline coverage
        required at Phase 3 (not enumerated in spec §6.4).

        G6-Cohort-R2-M3 PFR R2 ADOPT v3: extended parent cohort metadata
        coverage from 5 fields to all 15 cohort-level fields per spec §3.2.3
        line 117. Tolerates column-vs-`notes`-JSON-key existence per Phase 2 CB4
        lock by checking key presence before asserting non-null.

        G6-BatchID-R2-M4 PFR R2 ADOPT v3: added tightening assertion
        `parent_row["batch_id"] == BCNARROW_PARENT_RUN_ID`.

        G6-Docstring-R2-L2 + Sub-2 ACCEPT-WITH-EXTENSION PFR R2 ADOPT v3:
        docstring rewritten to match implementation; empty placeholder loop
        removed.

        CB2-R2-B1 PFR R2 ADOPT v3: per-test SKIP gate added at top — registry
        is always present but the parent row is absent pre-fire; if parent row
        absent → SKIP (not FAIL) so this test does not violate CLAUDE.md HARD
        CONSTRAINT "NEVER commit code that doesn't pass existing tests" at Step
        13.4 RED commit.

        CB2-R3 PFR R3 ADOPT v4: added `sqlite_master` table-existence guard
        BEFORE the COUNT query. `get_connection()` opens SQLite without
        initializing schema (experiment_registry.py:178-190); in fresh test env
        with no prior `runs` table → `sqlite3.OperationalError: no such table:
        runs` (ERROR not SKIP). Mirrors the guard pattern used at plan:316-330.

        AH1-R3 PFR R3 ADOPT v4: engine_commit lives in `notes` JSON
        (scripts:1347-1350), not direct column. v3 M3 15-field iteration
        silently skipped this load-bearing V4 reproducibility anchor
        (CORRECTED_WF_ENGINE_COMMIT = "eb1c87f"). Parse notes JSON + assert
        explicitly per Advisor R3 H1 (CONVERGENT with Codex R3 M1 elevated to
        HIGH for V4 anchor load-bearing).

        Sub-2-R4-B1 PFR R4 ADOPT v5 (SUPERSEDES Sub-2 R3 v4): parent-row NULL
        direction CORRECTED to 8 fields per producer scripts:1373-1381 + spec
        §3.2.3 line 118 verbatim. v4 Sub-2 R3 erroneously listed 5 fields incl.
        `win_rate` (NOT producer-NULL'd; NOT in spec) and MISSED 4 LC-b semantic
        fields (hypothesis_hash + returns_per_bar_path + returns_per_bar_sha256
        + T_obs). Advisor PFR R4 BLOCKING flagged via empirical reading of full
        scripts:1373-1387 (Codex saw only :1373-1377; missed :1378-1381 4 fields).
        Orchestrator empirical verification confirmed Advisor SOUND; Codex LOW
        underestimate corrected post-divergent-adjudication. 8 fields = 4 metric
        (sharpe_ratio + max_drawdown + total_return + total_trades) + 4 LC-b
        semantic (hypothesis_hash + returns_per_bar_path + returns_per_bar_sha256
        + T_obs).

        G6-Batched-R2-L3 PFR R2 ADOPT v3 (style decision): kept per-field loop
        rather than batched SELECT for clearer per-field error messages on
        first failure (cohort-field-NULL drift class).
        """
        from backtest.experiment_registry import get_connection, DEFAULT_DB_PATH

        conn = get_connection(DEFAULT_DB_PATH)
        conn.row_factory = sqlite3.Row
        try:
            cur = conn.cursor()
            # CB2-R3 PFR R3 ADOPT v4: add sqlite_master table-existence guard
            # BEFORE the COUNT query. get_connection() does NOT initialize schema
            # (experiment_registry.py:178-190); in fresh test env with no prior
            # `runs` table → sqlite3.OperationalError: no such table: runs (ERROR
            # not SKIP). The plan uses sqlite_master guard pattern elsewhere
            # (plan:316-330); applying here for consistency.
            cur.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='runs'"
            )
            if cur.fetchone() is None:
                pytest.skip(
                    "Phase 3 fire not yet executed — `runs` table does not exist "
                    "in registry; G6 invariant check requires fire-time state. "
                    "Test will be exercised at Step 14.4 V4 gate run."
                )
            # CB2-R2-B1 PFR R2 ADOPT v3: per-test SKIP gate (parent row presence)
            cur.execute(
                "SELECT COUNT(*) FROM runs WHERE run_id = ?",
                (BCNARROW_PARENT_RUN_ID,),
            )
            if cur.fetchone()[0] == 0:
                pytest.skip(
                    "Phase 3 fire not yet executed — parent batch_summary row "
                    "absent from registry; G6 invariant check requires fire-time "
                    "state. Test will be exercised at Step 14.4 V4 gate run."
                )
            # Parent row
            cur.execute(
                "SELECT * FROM runs WHERE run_id = ?",
                (BCNARROW_PARENT_RUN_ID,),
            )
            parent_rows = cur.fetchall()
            assert len(parent_rows) == 1, (
                f"G6 parent row count FAIL: expected 1 parent row at "
                f"run_id={BCNARROW_PARENT_RUN_ID!r}, found {len(parent_rows)}"
            )
            parent_row = parent_rows[0]
            assert parent_row["run_type"] == "batch_summary", (
                f"G6 parent row run_type FAIL: expected 'batch_summary', "
                f"found {parent_row['run_type']!r}"
            )
            parent_keys = set(parent_row.keys())
            # AH1-R3 PFR R3 ADOPT v4: engine_commit lives in notes JSON
            # (scripts:1347-1350), not direct column. v3 M3 15-field iteration
            # silently skipped this load-bearing V4 reproducibility anchor
            # (CORRECTED_WF_ENGINE_COMMIT = "eb1c87f"). Parse notes JSON +
            # assert explicitly per Advisor R3 H1 (CONVERGENT Codex R3 M1).
            # AL2-R3 PFR R3 ADOPT v4: defensive — if future schema migration adds
            # engine_commit as direct column, the notes-JSON parse path here would
            # still execute (notes still serialized); the direct-column path
            # would also assert via the 14-field direct-column loop below. Both
            # paths are safe; no migration-time bug.
            notes_json_str = parent_row["notes"] if "notes" in parent_keys else None
            if notes_json_str is None:
                notes_json_str = "{}"
            try:
                notes_payload = json.loads(notes_json_str)
            except json.JSONDecodeError as e:
                pytest.fail(
                    f"G6: parent_row['notes'] is not valid JSON: {e}"
                )
            assert notes_payload.get("engine_commit") == "eb1c87f", (
                f"G6: notes['engine_commit'] expected 'eb1c87f' "
                f"(CORRECTED_WF_ENGINE_COMMIT), got "
                f"{notes_payload.get('engine_commit')!r}. V4 reproducibility "
                f"anchor MUST match."
            )
            # G6-Cohort-R2-M3 PFR R2 ADOPT v3 (updated per AH1-R3): parent cohort
            # metadata non-null — 14 direct-column fields per spec §3.2.3 line 117
            # (engine_commit checked separately above via notes JSON per AH1-R3).
            # Tolerate column-vs-`notes`-JSON-key existence variance per Phase 2
            # CB4 lock (check key presence before asserting non-null).
            expected_cohort_fields_direct = (
                "git_commit",
                "current_git_sha",
                "execution_config_path",
                "execution_config_sha256",
                "parquet_data_sha256",
                "regime_key",
                "cost_anchor_id",
                "batch_id",
                "created_at_utc",
                "effective_start",
                "initial_capital",
                "fee_model",
                "strategy_name",
                "strategy_source",
            )
            for field_name in expected_cohort_fields_direct:
                if field_name not in parent_keys:
                    continue  # tolerate schema variants (column vs notes JSON-key)
                assert parent_row[field_name] is not None, (
                    f"G6-Cohort-R2-M3 parent row cohort metadata NULL FAIL: "
                    f"field={field_name!r} expected non-null at parent_run_id="
                    f"{BCNARROW_PARENT_RUN_ID}"
                )
            # G6-BatchID-R2-M4 PFR R2 ADOPT v3: lock parent.batch_id ==
            # BCNARROW_PARENT_RUN_ID per spec §3.2.3.
            if "batch_id" in parent_keys:
                assert parent_row["batch_id"] == BCNARROW_PARENT_RUN_ID, (
                    f"G6-BatchID-R2-M4 parent.batch_id expected "
                    f"{BCNARROW_PARENT_RUN_ID!r}, got {parent_row['batch_id']!r}"
                )
            # Sub-2-R4-B1 PFR R4 ADOPT v5: parent-row NULL direction CORRECTED
            # to 8 fields per producer scripts:1373-1381 + spec §3.2.3 line 118
            # verbatim. v3/v4 Sub-2 R3 ADOPT erroneously listed 5 fields incl.
            # `win_rate` (NOT in producer's explicit NULL list NOR in spec) and
            # MISSED 4 LC-b semantic fields (hypothesis_hash + returns_per_bar_path
            # + returns_per_bar_sha256 + T_obs). Advisor PFR R4 BLOCKING flagged
            # via empirical reading of scripts:1373-1387 (Codex R4 saw only
            # scripts:1373-1377 = 4 fields visible there; missed scripts:1378-1381).
            # Orchestrator empirical verification at HEAD `72641aa` confirmed
            # Advisor's reading SOUND; Codex's LOW underestimate corrected
            # post-divergent-adjudication.
            expected_parent_null_fields = (
                # Per-candidate metric fields (4) per scripts:1373-1377:
                "sharpe_ratio",
                "max_drawdown",
                "total_return",
                "total_trades",
                # LC-b semantic / identity fields (4) per scripts:1378-1381:
                "hypothesis_hash",
                "returns_per_bar_path",
                "returns_per_bar_sha256",
                "T_obs",
            )
            for field_name in expected_parent_null_fields:
                if field_name not in parent_keys:
                    continue  # tolerate column-existence variance
                assert parent_row[field_name] is None, (
                    f"Sub-2-R4-B1 G6: parent_row[{field_name!r}] expected NULL "
                    f"(per-candidate field at parent), got "
                    f"{parent_row[field_name]!r}. Producer writes NULL at "
                    f"scripts:1373-1381 (8 fields total)."
                )
            # Child rows
            cur.execute(
                "SELECT COUNT(*) FROM runs WHERE parent_run_id = ? "
                "AND run_type = ?",
                (BCNARROW_PARENT_RUN_ID, "regime_holdout"),
            )
            n_children = cur.fetchone()[0]
            assert n_children == 39, (
                f"G6 child row count FAIL: expected 39 child rows "
                f"(run_type=regime_holdout, parent_run_id={BCNARROW_PARENT_RUN_ID!r}), "
                f"found {n_children}"
            )
            # AL4 PFR R1 ADOPT v2: Independent invariant check (does NOT
            # short-circuit on the prior query's filter clause): future schema
            # changes could re-introduce NULL parent_run_ids that pass
            # `WHERE run_type='regime_holdout'` clauses but break parent-child
            # linkage. This catches that drift class.
            cur.execute(
                "SELECT DISTINCT parent_run_id FROM runs WHERE parent_run_id = ?",
                (BCNARROW_PARENT_RUN_ID,),
            )
            distinct_parents = [row[0] for row in cur.fetchall()]
            assert distinct_parents == [BCNARROW_PARENT_RUN_ID], (
                f"G6 child parent_run_id linkage FAIL: expected "
                f"[{BCNARROW_PARENT_RUN_ID!r}], found {distinct_parents!r}"
            )
            # CH4 PFR R1 ADOPT v2: child rows per-candidate metadata non-null
            cur.execute(
                "SELECT * FROM runs WHERE parent_run_id = ? "
                "AND run_type = 'regime_holdout'",
                (BCNARROW_PARENT_RUN_ID,),
            )
            children = cur.fetchall()
            per_candidate_metadata = (
                "hypothesis_hash",
                "sharpe_ratio",
                "max_drawdown",
                "total_return",
                "total_trades",
                "regime_holdout_passed",
            )
            for child in children:
                child_keys = set(child.keys())
                for field_name in per_candidate_metadata:
                    if field_name not in child_keys:
                        continue  # tolerate schema variants
                    assert child[field_name] is not None, (
                        f"CH4 G6 child row per-candidate metadata NULL FAIL: "
                        f"field={field_name!r} at child run_id={child['run_id']!r}"
                    )
            # G6-Docstring-R2-L2 + Sub-2 ACCEPT-WITH-EXTENSION PFR R2 ADOPT v3:
            # Per Phase 0 LineageContext semantics, per-candidate fields like
            # returns_per_bar_path / returns_per_bar_sha256 / T_obs are persisted
            # at children (NOT parent-only). NULL-at-children direction is
            # structurally unimplementable for the current schema. The empty
            # placeholder loop from v2 has been removed; if a future schema
            # change introduces a truly parent-only field that should be NULL at
            # children, add the assertion here.
        finally:
            conn.close()


class TestG7ArchiveIdempotency:
    """G7 archive idempotency gate."""

    def test_g7_archive_idempotency_refuses_existing_target(
        self, tmp_path: Path
    ) -> None:
        """Producer W3 (`_archive_canonical_pre_flight`) MUST raise when
        archive target already exists. Strict refuse-if-exists semantics;
        no silent overwrite; no auto-rename.

        Spec §4.3 G7 + spec §3.2.4 strict refuse semantics. Tested in
        isolation via tmp_path (does NOT mutate real canonical/archive paths).

        BLOCKING-5 carry per Plan v3-Phase2 line 3651: G7 inline coverage
        required at Phase 3 (not enumerated in spec §6.4).
        """
        from scripts.run_phase2c_evaluation_gate import (
            _archive_canonical_pre_flight,
            BCNARROW_ARCHIVE_BASENAME,
        )

        # Construct synthetic canonical + archive paths under tmp_path
        canonical_path = tmp_path / "fake_canonical_dir"
        canonical_path.mkdir()
        (canonical_path / "marker.txt").write_text("source content")
        archive_root = tmp_path / "archive"
        archive_root.mkdir()
        # Pre-create archive target to trigger refuse semantics
        preexisting_archive = archive_root / BCNARROW_ARCHIVE_BASENAME
        preexisting_archive.mkdir()
        (preexisting_archive / "stale.txt").write_text("stale prior content")

        with pytest.raises((RuntimeError, FileExistsError)) as exc_info:
            _archive_canonical_pre_flight(
                canonical_path=canonical_path,
                archive_root=archive_root,
                archive_basename=BCNARROW_ARCHIVE_BASENAME,
            )
        msg = str(exc_info.value).lower()
        assert "archive" in msg or "exist" in msg or BCNARROW_ARCHIVE_BASENAME in str(exc_info.value), (
            f"G7 archive-refuse error message must reference archive target. "
            f"Got: {exc_info.value!r}"
        )
        # Verify source canonical was NOT moved (refuse before any mutation)
        assert (canonical_path / "marker.txt").exists(), (
            "G7 refuse-if-exists FAIL: canonical source mutated despite refusal"
        )
        # Verify pre-existing archive content was NOT overwritten
        assert (preexisting_archive / "stale.txt").read_text() == "stale prior content", (
            "G7 refuse-if-exists FAIL: pre-existing archive content overwritten"
        )

    def test_g7_archive_refuses_cross_filesystem_attempt(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """G7 cross-FS guard coverage: producer's _archive_canonical_pre_flight
        uses Path.stat().st_dev to detect cross-FS source-vs-destination;
        raises NotImplementedError.

        In production fire, sibling-dir-under-common-parent guarantees same-FS
        (st_dev match). This test covers the defensive guard for operator
        misconfiguration via mocked Path.stat().

        AM1 PFR R1 ADOPT v2: NEW test for st_dev guard coverage.

        G7-SE-B2 PFR SEAL-eve R1 ADOPT v7: FakeStat extended with `st_mode`
        (directory mode = 0o040755) + 8 defensive stat-result attributes for
        any other Path/os.stat-using code path. Producer's
        `Path.mkdir(parents=True, exist_ok=True)` at scripts:1146 internally
        calls `stat().st_mode` on pre-created `archive_root` dir → AttributeError
        on v6 FakeStat with only `st_dev`. Codex empirical pytest run on v6
        caught this; Advisor static SEAL-eve missed it. The mock now falls
        through to the real `Path.stat` for any non-mocked path so test
        isolation is preserved (only `archive_root` + paths strictly under it,
        and `canonical` + paths under it, return FakeStat; everything else
        gets real stat behavior).
        """
        from scripts.run_phase2c_evaluation_gate import (
            _archive_canonical_pre_flight,
            BCNARROW_ARCHIVE_BASENAME,
        )

        canonical = tmp_path / "canonical"
        canonical.mkdir()
        (canonical / "marker.txt").write_text("orig")
        archive_root = tmp_path / "archive"
        archive_root.mkdir()

        class FakeStat:
            """Stat-result stand-in with all attributes Path/stat-using code might query.

            G7-SE-B2 PFR SEAL-eve R1 ADOPT v7: extended from v6 (which had only
            `st_dev`). Producer's `Path.mkdir(parents=True, exist_ok=True)` at
            scripts:1146 internally calls `stat().st_mode` on the pre-created
            `archive_root` dir → AttributeError on v6. Added `st_mode` (directory
            mode = 0o040755) + 8 defensive attributes for any other Path/os.stat
            code path that might be exercised through the cross-FS guard.
            """

            def __init__(self, dev: int, mode: int = 0o040755):
                self.st_dev = dev
                self.st_mode = mode  # CB2-SE-B2 fix: required by Path.mkdir's internal stat()
                # Defensive additions for any other Path/os.stat-using code path:
                self.st_ino = 0
                self.st_nlink = 1
                self.st_uid = 0
                self.st_gid = 0
                self.st_size = 0
                self.st_atime = 0.0
                self.st_mtime = 0.0
                self.st_ctime = 0.0

        original_stat = Path.stat

        # AM1-CrossFS-R2-M5 PFR R2 ADOPT v3: tightened substring match to
        # prefix match (startswith) or equality on resolved Path identity.
        # AL1-R3 PFR R3 ADOPT v4 description correction: PFR R2 ADOPT table
        # (plan:77) described this as "endswith / equality" but implementation
        # below actually uses startswith + equality (i.e., prefix match).
        # Implementation is sound; only the description was mischaracterized.
        # Previous substring `"archive" in str(self)` could spuriously match
        # unrelated paths containing the word "archive". The new pattern
        # matches only the specific archive_root or paths strictly under it.
        #
        # L2-Advisor-R2 PFR SEAL-eve R2 ADOPT v8: DESIGN INVARIANT — relies on
        # pytest tmp_path being pre-resolved on the target FS, so that
        # `str(path) == str(path.resolve())`. On macOS, `/var/folders/...` is a
        # symlink to `/private/var/folders/...` but pytest's tmp_path is
        # pre-resolved to `/private/var/...`, satisfying the invariant. The
        # producer's `_archive_canonical_pre_flight` at scripts:1157 calls
        # `archive_root.resolve()` then `.stat()` on the resolved Path; our mock
        # matches against the str-form of the un-resolved tmp_path. This works
        # ONLY because pytest pre-resolves tmp_path.
        #
        # DO NOT port this test to plain `tempfile.TemporaryDirectory()` or
        # `tempfile.mkdtemp()` without applying `.resolve()` to archive_root and
        # canonical BEFORE constructing archive_root_str / canonical_str. Without
        # that, the mock would silently fall through to `original_stat` (the
        # producer's resolved Path str != our un-resolved Path str), the cross-FS
        # guard would NOT raise NotImplementedError, shutil.move would actually
        # execute, and the test would FAIL with no diagnostic about the mock miss.
        #
        # Per Advisor SEAL-eve R2 LOW: severity LOW because port to plain
        # tempfile is unlikely; this comment is defensive future-proofing.
        archive_root_str = str(archive_root)
        canonical_str = str(canonical)

        def mocked_stat(self, *args, **kwargs):
            # G7-SE-B2 PFR SEAL-eve R1 ADOPT v7: fall through to real stat
            # for any non-mocked path so test isolation is preserved (other
            # Path objects within Path.mkdir's internal machinery, e.g. parent
            # directories, get real stat behavior).
            s = str(self)
            # Match exact archive_root OR any path strictly under archive_root
            if s == archive_root_str or s.startswith(archive_root_str + "/"):
                return FakeStat(dev=999)  # different FS for archive_root + subpaths
            if s == canonical_str or s.startswith(canonical_str + "/"):
                return FakeStat(dev=111)
            # Fall through to real stat for any other Path objects
            return original_stat(self, *args, **kwargs)

        monkeypatch.setattr(Path, "stat", mocked_stat)

        with pytest.raises((NotImplementedError, RuntimeError)) as exc_info:
            _archive_canonical_pre_flight(
                canonical_path=canonical,
                archive_root=archive_root,
                archive_basename=BCNARROW_ARCHIVE_BASENAME,
            )
        msg = str(exc_info.value).lower()
        assert "cross" in msg or "filesystem" in msg or "fs" in msg or "device" in msg, (
            f"G7 cross-FS refuse error message must reference cross-FS guard. "
            f"Got: {exc_info.value!r}"
        )

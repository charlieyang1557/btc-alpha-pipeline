"""PHASE2C_8.1 §8 Step 4 — independent-recompute verification gate.

This test is structurally a parallel-implementation verification of the
canonical findings narrated in PHASE2C_8.1's Step 5 closeout. It does
NOT import scripts/compare_multi_regime.py or any module that produced
the comparison artifacts on disk. It reads the four producer CSVs
(holdout_results.csv emitted by run_phase2c_evaluation_gate.py +
filter_evaluation_gate.py per regime+tier) and recomputes cohort
categorization + pass-count distribution + in-sample-caveat
stratification via simple set arithmetic.

Purpose: convert Codex's one-time external adversarial-review
recomputation into a permanent in-repo verification gate. If the
production comparison pipeline (scripts/compare_multi_regime.py) ever
drifts in a way that produces self-consistent-but-wrong canonical
numbers, this test catches the drift because it does not share any
source-code with the comparison pipeline.

Verification chain for PHASE2C_8.1's load-bearing findings:
1. Production comparison pipeline produced canonical artifacts.
2. Codex adversarial review independently recomputed canonical numbers
   from source CSVs at adversarial-review time (one-time external check).
3. This test (parallel implementation; stdlib only; ~80 lines) recomputes
   the same canonical numbers from the same source CSVs in CI on every
   change — making the independent recomputation a permanent verification
   gate rather than a one-time snapshot.

Pinned canonical numbers reflect the artifact snapshot at commit
da1859d (PHASE2C_8.1 Step 4). If artifacts ever legitimately
regenerate, update both this test AND tests/test_compare_multi_regime.py
TestIntegrationN4OnDisk's pinned numbers, AND document the canonical-
number change in the commit message that landed the regeneration.
"""
from __future__ import annotations

import csv
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
EVAL_GATE_ROOT = PROJECT_ROOT / "data" / "phase2c_evaluation_gate"

# Canonical regime+tier path mapping. Test skips if any path absent
# (e.g., on CI without the data fixtures).
REGIME_PATHS: dict[str, tuple[Path, Path]] = {
    "bear_2022": (
        EVAL_GATE_ROOT / "audit_v1",
        EVAL_GATE_ROOT / "audit_v1_filtered",
    ),
    "validation_2024": (
        EVAL_GATE_ROOT / "audit_2024_v1",
        EVAL_GATE_ROOT / "audit_2024_v1_filtered",
    ),
    "eval_2020_v1": (
        EVAL_GATE_ROOT / "eval_2020_v1",
        EVAL_GATE_ROOT / "eval_2020_v1_filtered",
    ),
    "eval_2021_v1": (
        EVAL_GATE_ROOT / "eval_2021_v1",
        EVAL_GATE_ROOT / "eval_2021_v1_filtered",
    ),
}

# In-sample caveat classification per spec §7.4.
FULLY_OOS_REGIMES = ("bear_2022", "validation_2024")
TRAIN_OVERLAP_REGIMES = ("eval_2020_v1", "eval_2021_v1")

# Expected CSV row counts (defensive: catches artifact-set regeneration
# that changes universe size before cohort logic even fires).
EXPECTED_UNFILTERED_ROWS = {
    "bear_2022": 198,
    "validation_2024": 198,
    "eval_2020_v1": 198,
    "eval_2021_v1": 198,
}
EXPECTED_FILTERED_ROWS = {
    "bear_2022": 146,
    "validation_2024": 144,
    "eval_2020_v1": 140,
    "eval_2021_v1": 144,
}


def _read_holdout_passed_map(csv_path: Path) -> dict[str, bool]:
    """Read holdout_results.csv → dict mapping hypothesis_hash to holdout_passed.

    holdout_passed in the CSV is "0" or "1"; we coerce to bool. Returns
    empty dict if file absent (caller decides whether absence is fatal).
    """
    if not csv_path.exists():
        return {}
    out: dict[str, bool] = {}
    with open(csv_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            h = row["hypothesis_hash"]
            out[h] = row["holdout_passed"] == "1"
    return out


def _ensure_paths_or_skip() -> None:
    """Skip test if any of the canonical paths are absent."""
    for label, (unf, filt) in REGIME_PATHS.items():
        unf_csv = unf / "holdout_results.csv"
        filt_csv = filt / "holdout_results.csv"
        if not unf_csv.exists() or not filt_csv.exists():
            pytest.skip(
                f"canonical CSV missing for {label}: "
                f"unf={unf_csv.exists()} filt={filt_csv.exists()}"
            )


@pytest.fixture(scope="module")
def canonical_data():
    """Load the 8 CSVs once; recompute cohort categorization."""
    _ensure_paths_or_skip()

    unf_passed: dict[str, dict[str, bool]] = {}
    filt_passed: dict[str, dict[str, bool]] = {}
    for label, (unf, filt) in REGIME_PATHS.items():
        unf_passed[label] = _read_holdout_passed_map(unf / "holdout_results.csv")
        filt_passed[label] = _read_holdout_passed_map(filt / "holdout_results.csv")

    # Defensive CSV row-count checks (catches universe-size drift before
    # cohort recomputation runs).
    for label, expected_n in EXPECTED_UNFILTERED_ROWS.items():
        actual_n = len(unf_passed[label])
        assert actual_n == expected_n, (
            f"Universe-size drift: {label} unfiltered CSV has {actual_n} "
            f"rows; expected {expected_n}. If this is a legitimate "
            f"artifact regeneration, update EXPECTED_UNFILTERED_ROWS + "
            f"document the canonical-number change in commit message."
        )
    for label, expected_n in EXPECTED_FILTERED_ROWS.items():
        actual_n = len(filt_passed[label])
        assert actual_n == expected_n, (
            f"Filtered-tier-size drift: {label} filtered CSV has "
            f"{actual_n} rows; expected {expected_n}. If this is a "
            f"legitimate artifact regeneration, update "
            f"EXPECTED_FILTERED_ROWS + document the canonical-number "
            f"change in commit message."
        )

    # Universe symmetry across all 4 unfiltered regimes (must hold by
    # construction since all 4 evaluations consume the same 198-candidate
    # batch).
    universes = [set(unf_passed[label]) for label in REGIME_PATHS]
    canonical_universe = universes[0]
    for i, u in enumerate(universes[1:], start=1):
        diff = canonical_universe ^ u
        assert not diff, (
            f"Universe asymmetry between regime[0] and regime[{i}]: "
            f"{len(diff)} hashes differ. This breaks the candidate-aligned "
            f"comparison precondition."
        )

    # Per-candidate pass counts (independent of compare_multi_regime).
    pass_count_unfiltered: dict[str, int] = {}
    pass_count_filtered: dict[str, int] = {}
    fos_pass_count: dict[str, int] = {}
    to_pass_count: dict[str, int] = {}
    for h in canonical_universe:
        unf_pc = sum(
            1 for label in REGIME_PATHS if unf_passed[label].get(h) is True
        )
        # Filtered-tier per-candidate pass count: regime contributes iff
        # candidate hash is in filtered set AND holdout_passed=True. Use
        # filtered CSV's holdout_passed (matches production semantic in
        # compare_multi_regime via filter_state="survivor_passed").
        filt_pc = sum(
            1 for label in REGIME_PATHS
            if filt_passed[label].get(h) is True
        )
        pass_count_unfiltered[h] = unf_pc
        pass_count_filtered[h] = filt_pc
        fos_pass_count[h] = sum(
            1 for label in FULLY_OOS_REGIMES if unf_passed[label].get(h) is True
        )
        to_pass_count[h] = sum(
            1 for label in TRAIN_OVERLAP_REGIMES if unf_passed[label].get(h) is True
        )

    return {
        "universe": canonical_universe,
        "pass_count_unfiltered": pass_count_unfiltered,
        "pass_count_filtered": pass_count_filtered,
        "fos_pass_count": fos_pass_count,
        "to_pass_count": to_pass_count,
    }


# ---------------------------------------------------------------------------
# Canonical-finding assertions (load-bearing)
# ---------------------------------------------------------------------------


class TestPhase2c81IndependentRecompute:
    """Independent-implementation verification of PHASE2C_8.1 canonical findings.

    Each test asserts a load-bearing canonical number that will be cited
    in PHASE2C_8.1's Step 5 closeout. Failures emit informative messages
    that name the changed canonical number and the corrective action.
    """

    def test_universe_cardinality_198(self, canonical_data):
        """198-candidate universe (PHASE2C_6 batch) preserved across regimes."""
        n = len(canonical_data["universe"])
        assert n == 198, (
            f"Canonical-finding regression: universe cardinality "
            f"changed from 198 to {n}. The 198-candidate batch is the "
            f"PHASE2C_6 carry-forward universe; any change is a "
            f"foundational shift requiring explicit acknowledgment."
        )

    def test_cohort_a_unfiltered_is_lone_survivor(self, canonical_data):
        """Cohort (a) unfiltered = candidates passing all 4 regimes = ['0845d1d7898412f2']."""
        cohort_a = sorted(
            h for h, pc in canonical_data["pass_count_unfiltered"].items()
            if pc == 4
        )
        assert cohort_a == ["0845d1d7898412f2"], (
            f"Canonical-finding regression: cohort_a_unfiltered changed "
            f"from ['0845d1d7898412f2'] to {cohort_a}. This is the load-"
            f"bearing 'lone cross-regime survivor at n=4' finding for "
            f"PHASE2C_8.1 Step 5 closeout. If artifacts have legitimately "
            f"regenerated, update this assertion AND "
            f"tests/test_compare_multi_regime.py canonical-number pins "
            f"AND document the canonical-number change in commit message."
        )

    def test_cohort_a_filtered_empty(self, canonical_data):
        """Cohort (a) filtered = candidates passing all 4 regimes at filter tier = []."""
        cohort_a_filt = sorted(
            h for h, pc in canonical_data["pass_count_filtered"].items()
            if pc == 4
        )
        assert cohort_a_filt == [], (
            f"Canonical-finding regression: cohort_a_filtered changed "
            f"from [] to {cohort_a_filt}. Empty filtered cohort is the "
            f"'no candidate survives all 4 regimes when trade-count "
            f"filter applied' finding."
        )

    def test_cohort_c_failures_cardinality_76(self, canonical_data):
        """Cohort (c) unfiltered = candidates passing 0 regimes = 76."""
        n_failures = sum(
            1 for pc in canonical_data["pass_count_unfiltered"].values()
            if pc == 0
        )
        assert n_failures == 76, (
            f"Canonical-finding regression: cohort_c_unfiltered "
            f"cardinality changed from 76 to {n_failures}. This is the "
            f"'how many candidates fail all 4 regimes' finding."
        )

    def test_pass_count_distribution_unfiltered(self, canonical_data):
        """Pass-count histogram unfiltered = {0:76, 1:55, 2:45, 3:21, 4:1}."""
        dist = {i: 0 for i in range(5)}
        for pc in canonical_data["pass_count_unfiltered"].values():
            dist[pc] += 1
        expected = {0: 76, 1: 55, 2: 45, 3: 21, 4: 1}
        assert dist == expected, (
            f"Canonical-finding regression: pass_count_distribution "
            f"unfiltered changed from {expected} to {dist}. This is the "
            f"per-regime cross-tab that the cohort findings derive from."
        )

    def test_pass_count_distribution_filtered(self, canonical_data):
        """Pass-count histogram filtered = {0:87, 1:58, 2:38, 3:15, 4:0}."""
        dist = {i: 0 for i in range(5)}
        for pc in canonical_data["pass_count_filtered"].values():
            dist[pc] += 1
        expected = {0: 87, 1: 58, 2: 38, 3: 15, 4: 0}
        assert dist == expected, (
            f"Canonical-finding regression: pass_count_distribution "
            f"filtered changed from {expected} to {dist}."
        )

    def test_in_sample_caveat_asymmetry_21_vs_8(self, canonical_data):
        """The load-bearing PHASE2C_8.1 finding: 21 train-overlap-all-pass vs 8 fully-OOS-all-pass."""
        n_fos_all_pass = sum(
            1 for v in canonical_data["fos_pass_count"].values()
            if v == len(FULLY_OOS_REGIMES)
        )
        n_to_all_pass = sum(
            1 for v in canonical_data["to_pass_count"].values()
            if v == len(TRAIN_OVERLAP_REGIMES)
        )
        assert n_fos_all_pass == 8, (
            f"Canonical-finding regression: n_passing_all_fully_out_of_"
            f"sample changed from 8 to {n_fos_all_pass}. This is half "
            f"of the 21-vs-8 in-sample-caveat asymmetry — the load-"
            f"bearing PHASE2C_8.1 finding. Any change requires explicit "
            f"narration of the asymmetry shift in commit message + "
            f"Step 5 closeout."
        )
        assert n_to_all_pass == 21, (
            f"Canonical-finding regression: n_passing_all_train_overlap "
            f"changed from 21 to {n_to_all_pass}. This is half of the "
            f"21-vs-8 in-sample-caveat asymmetry — the load-bearing "
            f"PHASE2C_8.1 finding. Any change requires explicit narration "
            f"of the asymmetry shift in commit message + Step 5 closeout."
        )

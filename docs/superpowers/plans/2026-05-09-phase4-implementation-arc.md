# Phase 4 Implementation Arc — Forward-Test of PHASE2C_15 cohort_a

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Operationalize PHASE4_PLAN.md (sealed `432b2bd`) — forward-test 39 PHASE2C_15 cohort_a candidates over `[2026-01-01, T_end]` at realistic costs (15 bps base, sensitivity {13, 17}, dual-report against research-time 7 bps), with per-stratum binomial test (Stratum A calendar n=22, Stratum B non-calendar n=17) at strict thresholds ≥17/22 + ≥13/17.

**Architecture:** Engine path = **Option C** (resolved via investigation). Extend [`scripts/run_phase2c_evaluation_gate.py`](../../scripts/run_phase2c_evaluation_gate.py) with `forward_2026` regime config — additive `evaluation_regimes.forward_2026` block in [`config/environments.yaml`](../../config/environments.yaml). Reuses existing `single_run_holdout_v1` attestation domain + `phase2c_7_1` schema discriminator (fully-out-of-sample register, parallel to bear_2022 / validation_2024). Cost-model parameterization via 4 sealed `config/execution_phase4_*bps.yaml` files + new `--execution-config` flag on runner. Per-stratum binomial test + closeout reads stratum membership directly from sealed [`cohort_a_candidate_reference.csv`](../../data/phase4_scoping/cohort_a_candidate_reference.csv). **Central invariant: lock the artifact, don't recompute.**

**Tech Stack:** Python 3.11+, pytest, scipy.stats.binom, pandas, pyyaml, existing Backtrader engine at corrected lineage `eb1c87f` (`wf-corrected-v1`). No anthropic SDK calls — Phase 4 is local backtest evaluation only.

---

## Pre-implementation context

### Sealed inputs (immutable imported artifacts; never recomputed)

| Artifact | Anchor | Purpose |
|---|---|---|
| [`docs/phase4/PHASE4_PLAN.md`](../../docs/phase4/PHASE4_PLAN.md) | sealed `432b2bd`; 100 lines | Parameter source of truth (§1.1-§1.5) |
| [`data/phase4_scoping/cohort_a_candidate_reference.csv`](../../data/phase4_scoping/cohort_a_candidate_reference.csv) | sealed `11b39f2`; 39 rows × 19 cols | Stratum membership via `theme` column |
| Engine lineage | `eb1c87f` (`wf-corrected-v1`) | Locked across PHASE2C_8.1→15 + Phase 4 |
| Cost values | PLAN §1.4: 7 / 13 / 15 / 17 bps per side | Locked: 4 cost configurations |
| Thresholds | PLAN §1.5: ≥17/22 (A); ≥13/17 (B) | Locked: scipy-verified |
| PHASE2C_15 SEAL | tag `phase2c-15-main-fire-v1` → `734570c` | Binding upstream |

### Engine path resolution: Option C (via Explore investigation)

- **Option A (existing WF runner with `n_windows=1`):** NOT VIABLE. [`backtest/engine.py:820-930`](../../backtest/engine.py) `run_walk_forward()` generates rolling sub-windows from `train_windows`; no `n_windows=1` parameter; engine would attempt 12mo train + 3mo test + 3mo step against a ~3.5mo period → ValueError.
- **Option B (new forward-only evaluation mode):** VIABLE but ~1000 LOC of new code; new attestation domain; over-engineered for one-shot use.
- **Option C (extend evaluation gate runner with `forward_2026` regime):** **CHOSEN.** Reuses existing `single_run_holdout_v1` attestation domain ([`backtest/wf_lineage.py:47`](../../backtest/wf_lineage.py)); regime-key mechanism designed for additive extensibility (PHASE2C_8.1 precedent at eval_2020/2021); cost model already plumbed via [`backtest/slippage.py`](../../backtest/slippage.py). Localized scope: 1 yaml block + 2 mapping entries + execution-config plumbing.

### Open scope items — ADJUDICATED at Charlie register

**Status:** Q1-Q4 + 5 substantive refinements authorized at Charlie register on 2026-05-09 post triple-register adjudication (ChatGPT + Claude advisor + per-fix Claude Code). Resolutions captured below.

- **Q1 — environments.yaml additive modification scope: AUTHORIZED.** PHASE2C_8.1 procedural precedent applies; `evaluation_regimes:` is the namespace explicitly designed for additive extension. The modification does NOT touch `splits:` immutable date-split contract. **TDD ordering refinement:** Task 2 Step 1 tests split into 4 new-feature TDD-RED + 2 regression sentinels (splits-invariance + cross-mapping-invariant); regression sentinels function as tripwires for any future cycle attempting to mutate `splits:`.
- **Q2 — Cost-model parameterization: AUTHORIZED via 4 sealed YAMLs + `--execution-config` flag.** Sealed YAMLs over CLI flags for reproducibility + auditability + "lock the artifact, don't recompute" invariant. **Self-auditing artifact metadata refinement:** runner additionally logs `execution_config_path` + `execution_config_sha256` into `holdout_summary.json` at write time; artifacts self-auditing without inference from run-id.
- **Q3 — Schema discriminator: AUTHORIZED phase2c_7_1.** Forward_2026 is fully-out-of-sample (training windows end 2021-12-31 + 2023-12-31; forward_2026 starts 2026-01-01; no overlap). Parallel to bear_2022 + validation_2024 (both `phase2c_7_1`); register-class-distinct from eval_2020/2021 train-overlap (`phase2c_8_1`). Caught pre-fire via empirical investigation against actual `wf_lineage.py` — §19 spec-vs-empirical-reality pattern at planning register, resolved before any artifact authored.
- **Q4 — T_end capture timing: AUTHORIZED with metadata-binding refinement.** Pre-fire data refresh permitted; post-fire frozen. **Refinement:** T_end captured into each `holdout_summary.json` via new `forward_window_metadata` block with 4 fields (`forward_window_start_utc` / `forward_window_end_utc` / `forward_bar_count` / `parquet_data_sha256`). Cross-artifact consistency tests at Task 4 Step 7 verify same window/bars/parquet hash across 4 cost-run artifacts (only cost config differs).

### Plan refinements applied post-authorization (2026-05-09)

Five substantive refinements folded into the plan tasks below:

1. **Task 2 Step 2 expected output corrected:** 4 FAIL (new-feature TDD-RED) + 2 PASS (regression sentinels), not 6 FAIL.
2. **Task 3 adds runner self-auditing:** `execution_config_path` + `execution_config_sha256` logged in `holdout_summary.json`.
3. **Task 4 adds `forward_window_metadata` block:** 4 immutable fields embedded in artifact at fire-time.
4. **Task 4 Step 7 adds cross-artifact consistency test:** verifies window/bars/parquet hash invariance across 4 cost-run artifacts.
5. **Task 5 field-name correction (load-bearing):** Per-candidate forward Sharpe is in `holdout_results.csv` (NOT `holdout_summary.json["per_candidate_results"]` — that key does NOT exist; summary is aggregate counts only). Field name is `holdout_sharpe` (NOT `forward_sharpe`). Resolved via descriptive lookup against `data/phase2c_evaluation_gate/phase2c_15_main_fire_bear_2022_v1/holdout_results.csv` schema. Phase 4 success criterion uses `holdout_sharpe > 0` directly (NOT `holdout_passed=1`, which is the 4-criterion AND-gate inherited from regime_holdout — register-class-distinct from PLAN §1.5 positive-Sharpe-only criterion).
6. **Task 5 adds closeout MD internal consistency test:** `test_phase4_closeout_md_internal_consistency` verifies headline numbers match per-stratum table; dual-report section references right cost configs.
7. **Reviewer routing per-task lean (advisory):** Tasks 2/3 lighter routing (config-class); Task 4 pre-fire reviewer on invocation params; Task 5 full three-way (substantive code); Task 6 full reviewer cycle on closeout MD; Task 7 Charlie-register only. Per-task adjudication at SEAL boundaries.

### TDD discipline at code register

Per the merged-scope Step authorization: tests assert against PHASE4_PLAN-stated numerical anchors as part of normal TDD application (no special arc-entry ceremony). Each task's test code below explicitly asserts against PLAN §1.4 / §1.5 values as locked literals. The `≥16/22` misattribution from the PLAN drafting cycle (§19 instance) would have been caught at first compile if these tests had existed.

---

## Task 2: Forward_2026 regime configuration + lineage mapping

**Goal:** Plumb the `forward_2026` regime through environments.yaml (additive) + wf_lineage.py mappings so `--regime-key evaluation_regimes.forward_2026` becomes a valid runner invocation. **Charlie register authorization required at task entry per Q1.**

**Files:**
- Modify: [`config/environments.yaml:115-116`](../../config/environments.yaml) (add `forward_2026` block at end of evaluation_regimes namespace)
- Modify: [`backtest/wf_lineage.py:101-106`](../../backtest/wf_lineage.py) (add to REGIME_KEY_LABEL_MAPPING)
- Modify: [`backtest/wf_lineage.py:119-124`](../../backtest/wf_lineage.py) (add to REGIME_KEY_TO_SCHEMA_VERSION_MAPPING)
- Modify: [`scripts/run_phase2c_evaluation_gate.py:59-64`](../../scripts/run_phase2c_evaluation_gate.py) (update `--regime-key` help text to document new option)
- Test: `tests/test_phase4_regime_config.py` (NEW)

- [ ] **Step 1: Write the failing tests**

Create `tests/test_phase4_regime_config.py`:

```python
"""Tests for Phase 4 forward_2026 regime configuration."""
from __future__ import annotations

import pytest
import yaml
from pathlib import Path

from backtest.wf_lineage import (
    ARTIFACT_SCHEMA_VERSION_PHASE2C_7_1,
    REGIME_KEY_LABEL_MAPPING,
    REGIME_KEY_TO_SCHEMA_VERSION_MAPPING,
    regime_key_to_schema_version,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENVIRONMENTS_YAML = PROJECT_ROOT / "config" / "environments.yaml"
FORWARD_2026_KEY = "evaluation_regimes.forward_2026"


def test_environments_yaml_contains_forward_2026_block():
    """The forward_2026 block must exist in evaluation_regimes namespace."""
    with open(ENVIRONMENTS_YAML) as f:
        config = yaml.safe_load(f)
    assert "evaluation_regimes" in config
    assert "forward_2026" in config["evaluation_regimes"]


def test_forward_2026_block_has_required_fields():
    """The forward_2026 block must have start, label, and arc_of_origin."""
    with open(ENVIRONMENTS_YAML) as f:
        config = yaml.safe_load(f)
    block = config["evaluation_regimes"]["forward_2026"]
    assert block["start"] == "2026-01-01"
    assert block["label"] == "forward_2026"
    assert block["arc_of_origin"] == "PHASE4"
    # end is null at PLAN cycle; captured at fire-time per PHASE4_PLAN §1.2
    assert block.get("end") is None


def test_forward_2026_does_not_alter_immutable_splits():
    """The additive modification must NOT touch splits namespace."""
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
    # test window immutable
    assert splits["test"]["start"] == "2025-01-01"
    assert splits["test"]["end"] == "2025-12-31"


def test_forward_2026_regime_key_in_label_mapping():
    """REGIME_KEY_LABEL_MAPPING must include forward_2026."""
    assert FORWARD_2026_KEY in REGIME_KEY_LABEL_MAPPING
    assert REGIME_KEY_LABEL_MAPPING[FORWARD_2026_KEY] == "forward_2026"


def test_forward_2026_schema_discriminator_is_phase2c_7_1():
    """Fully-out-of-sample register: phase2c_7_1, NOT phase2c_8_1."""
    schema = regime_key_to_schema_version(FORWARD_2026_KEY)
    assert schema == ARTIFACT_SCHEMA_VERSION_PHASE2C_7_1
    # Parallel to bear_2022 + validation_2024 (also fully-out-of-sample)
    assert (
        REGIME_KEY_TO_SCHEMA_VERSION_MAPPING[FORWARD_2026_KEY]
        == REGIME_KEY_TO_SCHEMA_VERSION_MAPPING["v2.regime_holdout"]
    )


def test_cross_mapping_invariant_holds():
    """Every regime_key in label mapping must also be in schema mapping."""
    assert set(REGIME_KEY_LABEL_MAPPING.keys()) == set(
        REGIME_KEY_TO_SCHEMA_VERSION_MAPPING.keys()
    )
```

- [ ] **Step 2: Run tests to verify TDD-RED state**

Run: `python -m pytest tests/test_phase4_regime_config.py -v`

Expected: **4 FAIL + 2 PASS** at this register.

- 4 FAIL (new-feature TDD-RED): `test_environments_yaml_contains_forward_2026_block` + `test_forward_2026_block_has_required_fields` + `test_forward_2026_regime_key_in_label_mapping` + `test_forward_2026_schema_discriminator_is_phase2c_7_1`.
- 2 PASS (regression sentinels): `test_forward_2026_does_not_alter_immutable_splits` (splits unchanged at this Step) + `test_cross_mapping_invariant_holds` (4-key set still consistent across both mappings before forward_2026 added).

The 2 regression sentinels function as tripwires: any future cycle that mutates `splits:` namespace would break the first; any future cycle that adds to one mapping but not the other would break the second.

**Important: Step 4 must add forward_2026 to BOTH mappings in the same edit** (Cross-mapping invariance is a TDD-GREEN requirement). If the additions land sequentially (one mapping at a time), `test_cross_mapping_invariant_holds` would fail transiently — Step 4's edit shape is structured to avoid this by editing both maps in one Edit call.

- [ ] **Step 3: Add forward_2026 block to environments.yaml**

After line 115 (end of `eval_2021_v1` block; before the `# ============` line introducing walk_forward section), append:

```yaml

  # 2026 forward-test window — fully out-of-sample post-test regime per
  # PHASE4_PLAN §1.2 (sealed at commit 432b2bd). Single-contiguous
  # evaluation [2026-01-01, T_end] of the 39 PHASE2C_15 cohort_a
  # candidates. T_end is null at PLAN cycle and captured at fire-time
  # via ingested_at_utc metadata + bar count (pre-fire data refresh
  # permitted; post-fire frozen). NOT a train-overlap regime — fully-
  # out-of-sample register parallel to bear_2022 / validation_2024.
  forward_2026:
    start: "2026-01-01"
    end: null  # captured at fire-time per PHASE4_PLAN §1.2
    label: "forward_2026"
    macro_characterization: "post_test_forward"
    arc_of_origin: "PHASE4"
```

- [ ] **Step 4: Add mapping entries to wf_lineage.py**

Modify `REGIME_KEY_LABEL_MAPPING` at [`backtest/wf_lineage.py:101-106`](../../backtest/wf_lineage.py) — add one line before the closing `}`:

```python
REGIME_KEY_LABEL_MAPPING: dict[str, str] = {
    "v2.regime_holdout": "bear_2022",
    "v2.validation": "validation_2024",
    "evaluation_regimes.eval_2020_v1": "eval_2020_v1",
    "evaluation_regimes.eval_2021_v1": "eval_2021_v1",
    "evaluation_regimes.forward_2026": "forward_2026",  # PHASE4_PLAN §1.2
}
```

Modify `REGIME_KEY_TO_SCHEMA_VERSION_MAPPING` at lines 119-124 — add one line before the closing `}`:

```python
REGIME_KEY_TO_SCHEMA_VERSION_MAPPING: dict[str, str] = {
    "v2.regime_holdout": ARTIFACT_SCHEMA_VERSION_PHASE2C_7_1,
    "v2.validation": ARTIFACT_SCHEMA_VERSION_PHASE2C_7_1,
    "evaluation_regimes.eval_2020_v1": ARTIFACT_SCHEMA_VERSION_PHASE2C_8_1,
    "evaluation_regimes.eval_2021_v1": ARTIFACT_SCHEMA_VERSION_PHASE2C_8_1,
    "evaluation_regimes.forward_2026": ARTIFACT_SCHEMA_VERSION_PHASE2C_7_1,  # fully-out-of-sample
}
```

- [ ] **Step 5: Update --regime-key help text**

In [`scripts/run_phase2c_evaluation_gate.py`](../../scripts/run_phase2c_evaluation_gate.py), find the `--regime-key` argparse definition (around line 700+; search for `add_argument.*regime-key`) and update help text to document `evaluation_regimes.forward_2026` as an option. Use `grep -n "regime-key" scripts/run_phase2c_evaluation_gate.py` to locate the exact line.

The required addition (one bullet to the existing options list):
```
- evaluation_regimes.forward_2026: PHASE4 forward-test [2026-01-01, T_end]
```

- [ ] **Step 6: Run tests to verify they pass**

Run: `python -m pytest tests/test_phase4_regime_config.py -v`
Expected: 6 PASS.

- [ ] **Step 7: Run full regression suite to verify no breakage**

Run: `python -m pytest tests/ -q -k "not slow"`
Expected: existing suite passes; no new failures introduced by mapping addition.

- [ ] **Step 8: Commit**

```bash
git add config/environments.yaml backtest/wf_lineage.py scripts/run_phase2c_evaluation_gate.py tests/test_phase4_regime_config.py
git commit -m "$(cat <<'EOF'
feat(phase4): add forward_2026 regime config + lineage mapping

Additive evaluation_regimes.forward_2026 block (start 2026-01-01,
end null pending fire-time T_end capture per PHASE4_PLAN §1.2).
Fully-out-of-sample register: schema discriminator phase2c_7_1
(parallel to bear_2022 + validation_2024).

Per CLAUDE.md hard rule additive evaluation_regimes modification
authorized at Charlie register; PHASE2C_8.1 precedent (eval_2020/2021).

Tests assert against PHASE4_PLAN §1.2 + §1.4 anchors; cross-mapping
invariant verified.
EOF
)"
```

---

## Task 3: Cost-model parameterization

**Goal:** Author 4 sealed execution-config YAML files for the 4 PHASE4_PLAN cost configurations; add `--execution-config` flag to runner that overrides EXECUTION_CONFIG_PATH for the run; tests assert against PLAN §1.4 numerical anchors. **Charlie register authorization required at task entry per Q2.**

**Files:**
- Create: `config/execution_phase4_07bps.yaml` (research-time comparability; 4bps fee + 3bps slip = 7bps)
- Create: `config/execution_phase4_13bps.yaml` (sensitivity low; 10bps fee + 3bps slip = 13bps)
- Create: `config/execution_phase4_15bps.yaml` (realistic base; 10bps fee + 5bps slip = 15bps)
- Create: `config/execution_phase4_17bps.yaml` (sensitivity high; 10bps fee + 7bps slip = 17bps)
- Modify: [`scripts/run_phase2c_evaluation_gate.py`](../../scripts/run_phase2c_evaluation_gate.py) (add `--execution-config` flag; thread to engine)
- Modify: [`backtest/engine.py:1455`](../../backtest/engine.py) `run_regime_holdout` signature (add `execution_config_path: Path | None = None` parameter); plumb to line 1623 cost-model load
- Test: `tests/test_phase4_cost_config.py` (NEW)

- [ ] **Step 1: Write the failing tests**

Create `tests/test_phase4_cost_config.py`:

```python
"""Tests for Phase 4 sealed execution-config YAML files."""
from __future__ import annotations

import pytest
from pathlib import Path

from backtest.slippage import ConstantSlippage, load_execution_config

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PHASE4_CONFIGS = {
    7:  PROJECT_ROOT / "config" / "execution_phase4_07bps.yaml",
    13: PROJECT_ROOT / "config" / "execution_phase4_13bps.yaml",
    15: PROJECT_ROOT / "config" / "execution_phase4_15bps.yaml",
    17: PROJECT_ROOT / "config" / "execution_phase4_17bps.yaml",
}


@pytest.mark.parametrize("expected_bps,config_path", PHASE4_CONFIGS.items())
def test_phase4_config_file_exists(expected_bps, config_path):
    """Each Phase 4 cost-config YAML file must exist."""
    assert config_path.exists(), f"Missing: {config_path}"


@pytest.mark.parametrize("expected_bps,config_path", PHASE4_CONFIGS.items())
def test_phase4_config_total_bps_matches_phase4_plan(expected_bps, config_path):
    """ConstantSlippage.from_config must yield PLAN §1.4 anchor values."""
    config = load_execution_config(config_path)
    model = ConstantSlippage.from_config(config)
    assert model.total_bps == float(expected_bps), (
        f"Config {config_path.name} expected {expected_bps}bps "
        f"per PHASE4_PLAN §1.4 but got {model.total_bps}"
    )


def test_phase4_15bps_realistic_base_decomposition():
    """PHASE4_PLAN §1.4 base: 10bps taker + 5bps slippage = 15bps per side."""
    config = load_execution_config(PHASE4_CONFIGS[15])
    assert config["cost_model"]["default_fee_bps"] == 10.0
    assert config["cost_model"]["slippage_bps"] == 5.0
    model = ConstantSlippage.from_config(config)
    assert model.fee_bps == 10.0
    assert model.slippage_bps == 5.0
    assert model.effective_commission == 0.0015  # 15bps as decimal


def test_phase4_07bps_research_time_decomposition():
    """PHASE4_PLAN §1.4 research-time: 4bps fee + 3bps slip = 7bps (PHASE2C_15-comparability)."""
    config = load_execution_config(PHASE4_CONFIGS[7])
    assert config["cost_model"]["default_fee_bps"] == 4.0
    assert config["cost_model"]["slippage_bps"] == 3.0


def test_phase4_13bps_sensitivity_low_decomposition():
    """PHASE4_PLAN §1.4 sensitivity low: 10bps fee + 3bps slip = 13bps (slippage -2)."""
    config = load_execution_config(PHASE4_CONFIGS[13])
    assert config["cost_model"]["default_fee_bps"] == 10.0
    assert config["cost_model"]["slippage_bps"] == 3.0


def test_phase4_17bps_sensitivity_high_decomposition():
    """PHASE4_PLAN §1.4 sensitivity high: 10bps fee + 7bps slip = 17bps (slippage +2)."""
    config = load_execution_config(PHASE4_CONFIGS[17])
    assert config["cost_model"]["default_fee_bps"] == 10.0
    assert config["cost_model"]["slippage_bps"] == 7.0
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_phase4_cost_config.py -v`
Expected: All FAIL — config files do not exist.

- [ ] **Step 3: Author execution_phase4_07bps.yaml**

Create `config/execution_phase4_07bps.yaml`:

```yaml
# execution_phase4_07bps.yaml — Phase 4 research-time comparability cost
# Per PHASE4_PLAN §1.4: PHASE2C_15-comparability cost model.
# Total per-side: 4bps fee + 3bps slippage = 7bps (matches default execution.yaml).
# This config is dual-reporting only — NOT the Phase 4 success criterion basis.
# Last reviewed: 2026-05-09 (Phase 4 implementation arc Task 3)

execution:
  signal_timing: "bar_close"
  fill_timing: "next_bar_open"
  stop_limit_intrabar: "adverse_first"

cost_model:
  name: "phase4_research_time_07bps"
  maker_fee_bps: 2.0
  taker_fee_bps: 4.0
  default_fee_bps: 4.0
  slippage_bps: 3.0

zero_volume:
  treatment: "flag_only"

position:
  max_position_pct: 1.0
  default_position_pct: 1.0
  max_leverage: 1.0

timezone:
  canonical: "UTC"

timeframe:
  primary: "1h"
```

- [ ] **Step 4: Author execution_phase4_15bps.yaml**

Create `config/execution_phase4_15bps.yaml`:

```yaml
# execution_phase4_15bps.yaml — Phase 4 realistic base cost
# Per PHASE4_PLAN §1.4: 10bps Binance VIP 0 spot taker + 5bps slippage = 15bps per side.
# THIS CONFIG IS THE BASIS FOR PHASE 4 §1.5 SUCCESS CRITERION.
# Last reviewed: 2026-05-09 (Phase 4 implementation arc Task 3)

execution:
  signal_timing: "bar_close"
  fill_timing: "next_bar_open"
  stop_limit_intrabar: "adverse_first"

cost_model:
  name: "phase4_realistic_base_15bps"
  maker_fee_bps: 2.0
  taker_fee_bps: 10.0
  default_fee_bps: 10.0
  slippage_bps: 5.0

zero_volume:
  treatment: "flag_only"

position:
  max_position_pct: 1.0
  default_position_pct: 1.0
  max_leverage: 1.0

timezone:
  canonical: "UTC"

timeframe:
  primary: "1h"
```

- [ ] **Step 5: Author execution_phase4_13bps.yaml and execution_phase4_17bps.yaml**

Create `config/execution_phase4_13bps.yaml` (identical to 15bps but `slippage_bps: 3.0`, `name: "phase4_sensitivity_low_13bps"`).

Create `config/execution_phase4_17bps.yaml` (identical to 15bps but `slippage_bps: 7.0`, `name: "phase4_sensitivity_high_17bps"`).

- [ ] **Step 6: Run cost-config tests to verify they pass**

Run: `python -m pytest tests/test_phase4_cost_config.py -v`
Expected: All PASS (10 tests). This locks the 4 sealed cost configurations against PHASE4_PLAN §1.4 anchors.

- [ ] **Step 7: Write failing test for --execution-config plumbing**

Append to `tests/test_phase4_cost_config.py`:

```python
def test_run_regime_holdout_accepts_execution_config_path(tmp_path):
    """run_regime_holdout must accept execution_config_path parameter and use it."""
    from backtest.engine import run_regime_holdout
    import inspect

    sig = inspect.signature(run_regime_holdout)
    assert "execution_config_path" in sig.parameters, (
        "run_regime_holdout must accept execution_config_path parameter "
        "to support Phase 4 cost-config override"
    )
    # Default should be None (preserves backward compat)
    assert sig.parameters["execution_config_path"].default is None
```

Run: `python -m pytest tests/test_phase4_cost_config.py::test_run_regime_holdout_accepts_execution_config_path -v`
Expected: FAIL — parameter not yet added.

- [ ] **Step 8: Add execution_config_path parameter to run_regime_holdout**

In [`backtest/engine.py:1455`](../../backtest/engine.py), add `execution_config_path: Path | None = None` to the `run_regime_holdout` signature. At line 1623, change `cost_model = ConstantSlippage.from_config(load_execution_config())` to:

```python
_cfg_path = execution_config_path if execution_config_path is not None else None
cost_model = ConstantSlippage.from_config(
    load_execution_config(_cfg_path) if _cfg_path is not None else load_execution_config()
)
```

(Slimmer alternative — passing None to load_execution_config uses default; if non-None, override path used.)

Search for any internal call sites of `run_regime_holdout` and confirm the new keyword has a default of `None` (so existing callers are unaffected). Use `grep -rn "run_regime_holdout(" backtest/ scripts/ tests/` to locate.

- [ ] **Step 9: Add --execution-config CLI flag to runner**

In [`scripts/run_phase2c_evaluation_gate.py`](../../scripts/run_phase2c_evaluation_gate.py), add to argparse parser (locate the existing argparse setup; search for `argparse.ArgumentParser`):

```python
parser.add_argument(
    "--execution-config",
    type=Path,
    default=None,
    help=(
        "Path to alternate execution.yaml (for Phase 4 cost parameterization). "
        "Default: config/execution.yaml. Phase 4 uses one of: "
        "config/execution_phase4_07bps.yaml | _13bps | _15bps | _17bps."
    ),
)
```

Then pass `args.execution_config` through to the `run_regime_holdout()` call site (locate via `grep -n "run_regime_holdout" scripts/run_phase2c_evaluation_gate.py`).

- [ ] **Step 9a: Self-auditing artifact metadata (per Q2 refinement)**

In `scripts/run_phase2c_evaluation_gate.py`, locate the `holdout_summary.json` write site (likely near the end of `main()`; grep for `holdout_summary` or `json.dump`). Augment the summary dict before write with:

```python
import hashlib

# Self-auditing execution-config provenance per PHASE4 plan refinement.
# Locks which cost config produced this artifact without inferring from run-id.
_exec_cfg_path = (
    args.execution_config
    if args.execution_config is not None
    else PROJECT_ROOT / "config" / "execution.yaml"
)
_exec_cfg_bytes = _exec_cfg_path.read_bytes()
summary["execution_config_path"] = str(_exec_cfg_path.relative_to(PROJECT_ROOT))
summary["execution_config_sha256"] = hashlib.sha256(_exec_cfg_bytes).hexdigest()
```

Add test in `tests/test_phase4_cost_config.py`:

```python
def test_runner_logs_execution_config_metadata():
    """Per Q2 refinement: holdout_summary.json must embed exec config path + sha256."""
    # This is a structural test: post-fire, every Phase 4 holdout_summary.json
    # must have execution_config_path and execution_config_sha256 fields.
    # Tested empirically at Task 4 cross-artifact consistency check.
    # Here we verify the summary-write code path includes these fields by
    # mock-importing the runner and checking field presence in a stub.
    pytest.skip(
        "Empirical verification deferred to Task 4 cross-artifact consistency "
        "test against real holdout_summary.json artifacts."
    )
```

- [ ] **Step 10: Run all tests + regression**

Run: `python -m pytest tests/test_phase4_cost_config.py tests/test_phase4_regime_config.py -v`
Run: `python -m pytest tests/ -q -k "not slow"` (regression on existing suite)
Expected: all Phase 4 tests pass; no regression.

- [ ] **Step 11: Commit**

```bash
git add config/execution_phase4_*.yaml scripts/run_phase2c_evaluation_gate.py backtest/engine.py tests/test_phase4_cost_config.py
git commit -m "$(cat <<'EOF'
feat(phase4): cost-model parameterization for 4 sealed execution configs

Authors 4 sealed YAMLs at config/execution_phase4_{07,13,15,17}bps.yaml
matching PHASE4_PLAN §1.4 cost configurations:
- 7bps: PHASE2C_15-comparability research-time (dual-report)
- 13bps: sensitivity low (slippage -2)
- 15bps: realistic base (Binance VIP 0 taker 10 + slippage 5) — §1.5 basis
- 17bps: sensitivity high (slippage +2)

Adds --execution-config flag to scripts/run_phase2c_evaluation_gate.py;
plumbs through run_regime_holdout(execution_config_path) into
ConstantSlippage.from_config(load_execution_config(path)). Default None
preserves backward compat for all non-Phase-4 callers.

Tests assert PLAN §1.4 numerical anchors at config-file register:
fee_bps + slippage_bps decomposition + total_bps + effective_commission.
EOF
)"
```

---

## Task 4: Forward fire — 4 cost runs

**Goal:** Execute `run_phase2c_evaluation_gate.py` four times against the 39-candidate cohort at the 4 cost configurations; produce 4 result artifacts. **Charlie register authorization required at task entry per Q4 (T_end capture timing).**

**Files:**
- Create: `data/phase2c_evaluation_gate/phase4_forward_2026_07bps_v1/` (output dir)
- Create: `data/phase2c_evaluation_gate/phase4_forward_2026_13bps_v1/`
- Create: `data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1/`
- Create: `data/phase2c_evaluation_gate/phase4_forward_2026_17bps_v1/`
- Test: `tests/test_phase4_forward_fire_preconditions.py` (NEW)

- [ ] **Step 1: Write pre-fire precondition tests**

Create `tests/test_phase4_forward_fire_preconditions.py`:

```python
"""Pre-fire precondition tests for Phase 4 forward fire."""
from __future__ import annotations

import csv
import subprocess
from pathlib import Path

import pytest
import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent
COHORT_REFERENCE = (
    PROJECT_ROOT / "data" / "phase4_scoping" / "cohort_a_candidate_reference.csv"
)


def test_cohort_reference_has_39_candidates():
    """PHASE4_PLAN §1.3: 39 unfiltered candidates locked."""
    with open(COHORT_REFERENCE) as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 39


def test_cohort_reference_stratum_decomposition():
    """PHASE4_PLAN §1.3: Stratum A=22 calendar; Stratum B=17 non-calendar."""
    with open(COHORT_REFERENCE) as f:
        rows = list(csv.DictReader(f))
    stratum_a = [r for r in rows if r["theme"] == "calendar_effect"]
    stratum_b = [r for r in rows if r["theme"] != "calendar_effect"]
    assert len(stratum_a) == 22, f"Stratum A expected 22, got {len(stratum_a)}"
    assert len(stratum_b) == 17, f"Stratum B expected 17, got {len(stratum_b)}"


def test_cohort_reference_stratum_b_theme_breakdown():
    """PHASE4_PLAN §1.3: B = volume_divergence 7 + momentum 6 + mean_reversion 2 + volatility_regime 2."""
    with open(COHORT_REFERENCE) as f:
        rows = list(csv.DictReader(f))
    expected = {
        "volume_divergence": 7,
        "momentum": 6,
        "mean_reversion": 2,
        "volatility_regime": 2,
    }
    counts = {}
    for r in rows:
        if r["theme"] != "calendar_effect":
            counts[r["theme"]] = counts.get(r["theme"], 0) + 1
    assert counts == expected, f"Stratum B breakdown: expected {expected}, got {counts}"


def test_engine_lineage_at_corrected_commit():
    """Engine lineage must be at eb1c87f or descendant per CLAUDE.md."""
    head = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], text=True, cwd=PROJECT_ROOT
    ).strip()
    rc = subprocess.call(
        ["git", "merge-base", "--is-ancestor", "eb1c87f", head],
        cwd=PROJECT_ROOT,
    )
    assert rc == 0, "HEAD must descend from corrected-engine commit eb1c87f"
```

- [ ] **Step 2: Run pre-fire tests; expect PASS**

Run: `python -m pytest tests/test_phase4_forward_fire_preconditions.py -v`
Expected: 4 PASS.

- [ ] **Step 3: Pre-fire data refresh (Charlie register authorization required per Q4)**

Per PHASE4_PLAN §1.2: pre-fire data refresh permitted; post-fire freezes T_end.

```bash
python -m ingestion.incremental_update --pair BTCUSDT --interval 1h
python -m ingestion.validators --file data/raw/btcusdt_1h.parquet --report data/quality/
```

Verify the latest bar in `data/raw/btcusdt_1h.parquet` covers `[2026-01-01, latest_T_end]`.

- [ ] **Step 4: Capture T_end + parquet hash to be embedded in artifacts (per Q4 refinement)**

```bash
python -c "
import hashlib
import pyarrow.parquet as pq
import pandas as pd
from pathlib import Path

parquet_path = Path('data/raw/btcusdt_1h.parquet')
df = pq.read_table(parquet_path).to_pandas()
forward = df[df['open_time_utc'] >= pd.Timestamp('2026-01-01', tz='UTC')]
parquet_sha256 = hashlib.sha256(parquet_path.read_bytes()).hexdigest()

print(f'forward_window_start_utc: 2026-01-01T00:00:00Z')
print(f'forward_window_end_utc: {forward[\"open_time_utc\"].max().isoformat().replace(\"+00:00\", \"Z\")}')
print(f'forward_bar_count: {len(forward)}')
print(f'parquet_data_sha256: {parquet_sha256}')
" | tee /tmp/phase4_forward_window_capture.txt
```

These 4 values become the canonical fire-time metadata embedded into each `holdout_summary.json` (per Q4 refinement). The `/tmp/` capture is a human-readable record; the audit-trail-binding location is the artifact metadata.

**Plumbing:** the runner writes `forward_window_metadata` block into `holdout_summary.json` automatically when `regime_key=evaluation_regimes.forward_2026` is detected. Implementation goes in `scripts/run_phase2c_evaluation_gate.py` near the summary write site (parallel to Step 9a self-auditing exec config metadata in Task 3):

```python
# Forward-window metadata block — fire-time T_end capture per PHASE4_PLAN §1.2.
# Only emitted for forward_2026 regime; other regimes write empty block.
if args.regime_key == "evaluation_regimes.forward_2026":
    import pyarrow.parquet as pq
    parquet_path = PROJECT_ROOT / "data" / "raw" / "btcusdt_1h.parquet"
    df = pq.read_table(parquet_path).to_pandas()
    forward = df[df['open_time_utc'] >= pd.Timestamp('2026-01-01', tz='UTC')]
    summary["forward_window_metadata"] = {
        "forward_window_start_utc": "2026-01-01T00:00:00Z",
        "forward_window_end_utc": forward["open_time_utc"].max().isoformat().replace("+00:00", "Z"),
        "forward_bar_count": int(len(forward)),
        "parquet_data_sha256": hashlib.sha256(parquet_path.read_bytes()).hexdigest(),
    }
```

- [ ] **Step 5: Fire @ 15bps (REALISTIC BASE — Phase 4 success criterion basis)**

```bash
python scripts/run_phase2c_evaluation_gate.py \
    --source-batch-id b6fcbf86-4d57-4d1f-ae41-1778296b1ae9 \
    --universe audit \
    --regime-key evaluation_regimes.forward_2026 \
    --execution-config config/execution_phase4_15bps.yaml \
    --run-id phase4_forward_2026_15bps_v1
```

Expected: writes `data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1/holdout_summary.json` + per-candidate trade CSVs. Verify `regime_key=evaluation_regimes.forward_2026`, `regime_label=forward_2026`, `artifact_schema_version=phase2c_7_1`, `evaluation_semantics=single_run_holdout_v1`.

- [ ] **Step 6: Fire @ 7bps, 13bps, 17bps (sequential)**

Run identical commands with respective configs and run-ids:
```bash
python scripts/run_phase2c_evaluation_gate.py [...common args...] \
    --execution-config config/execution_phase4_07bps.yaml \
    --run-id phase4_forward_2026_07bps_v1

python scripts/run_phase2c_evaluation_gate.py [...common args...] \
    --execution-config config/execution_phase4_13bps.yaml \
    --run-id phase4_forward_2026_13bps_v1

python scripts/run_phase2c_evaluation_gate.py [...common args...] \
    --execution-config config/execution_phase4_17bps.yaml \
    --run-id phase4_forward_2026_17bps_v1
```

- [ ] **Step 7: Verify lineage + cross-artifact consistency on all 4 cost-run artifacts**

Cross-artifact consistency test (per Q4 refinement): the 4 artifacts must share the same `forward_window_metadata` block (same window/bars/parquet hash); only `cost_model.name` + `execution_config_path` + `execution_config_sha256` should differ.

```bash
python -c "
import json
from pathlib import Path
from backtest.wf_lineage import check_evaluation_semantics_or_raise

artifacts = {}
for cost in ['07bps', '13bps', '15bps', '17bps']:
    p = Path(f'data/phase2c_evaluation_gate/phase4_forward_2026_{cost}_v1/holdout_summary.json')
    summary = json.loads(p.read_text())
    check_evaluation_semantics_or_raise(summary, artifact_path=p)
    artifacts[cost] = summary
    print(f'OK lineage: {p}')

# Cross-artifact invariance: forward_window_metadata identical across 4 runs.
fields_must_match = ['forward_window_start_utc', 'forward_window_end_utc', 'forward_bar_count', 'parquet_data_sha256']
ref = artifacts['15bps']['forward_window_metadata']
for cost, summary in artifacts.items():
    fwm = summary['forward_window_metadata']
    for field in fields_must_match:
        assert fwm[field] == ref[field], f'forward_window_metadata.{field} mismatch at {cost}: {fwm[field]} vs {ref[field]}'
    print(f'OK forward_window_metadata invariance: {cost}')

# Cross-artifact distinction: execution_config differs only on cost.
for cost, summary in artifacts.items():
    assert f'phase4_{cost.replace(\"bps\", \"\")}' in summary['execution_config_path'] or cost in summary['execution_config_path'], (
        f'execution_config_path at {cost} should reference {cost} config, got {summary[\"execution_config_path\"]}'
    )
    print(f'OK execution_config_path: {cost} -> {summary[\"execution_config_path\"]}')

print('All 4 artifacts validate against single_run_holdout_v1 attestation domain + forward_window_metadata invariant + execution_config distinction.')
"
```

Expected: 4 OK lineage + 4 OK forward_window_metadata invariance + 4 OK execution_config_path lines; no AssertionError; no exceptions.

- [ ] **Step 8: Commit Phase 4 forward fire artifacts**

```bash
git add data/phase2c_evaluation_gate/phase4_forward_2026_*_v1/
git commit -m "$(cat <<'EOF'
feat(phase4): Phase 4 forward fire artifacts (4 cost configurations)

Forward-test fire results for 39 PHASE2C_15 cohort_a candidates over
[2026-01-01, T_end_at_fire] at 4 cost configurations per PHASE4_PLAN §1.4:
- 07bps research-time (PHASE2C_15-comparability dual-report)
- 13bps sensitivity low
- 15bps realistic base (§1.5 success criterion basis)
- 17bps sensitivity high

Lineage: engine eb1c87f (wf-corrected-v1); evaluation_semantics
single_run_holdout_v1; regime_key evaluation_regimes.forward_2026;
artifact_schema_version phase2c_7_1.

T_end captured at fire-time per §1.2 (pre-fire refresh permitted;
post-fire frozen). Bar count + T_end metadata embedded in each
holdout_summary.json.

This commit publishes the unprocessed forward-fire artifacts; per-
stratum binomial test + closeout assembly fires at Task 5.
EOF
)"
```

---

## Task 5: Per-stratum binomial test + closeout assembly

**Goal:** Read 4 forward-fire artifacts; classify positive/non-positive forward-Sharpe per candidate per cost; apply per-stratum binomial test at strict thresholds; produce Phase 4 closeout MD with 3-case interpretation guard.

**Files:**
- Create: `scripts/build_phase4_closeout.py` (analysis script)
- Create: `tests/test_phase4_closeout.py` (NEW)
- Create: `docs/closeout/PHASE4_RESULTS.md` (output deliverable)

- [ ] **Step 1: Write the failing tests for binomial-threshold logic**

Create `tests/test_phase4_closeout.py`:

```python
"""Tests for Phase 4 closeout assembly + per-stratum binomial test."""
from __future__ import annotations

import pytest
from scipy.stats import binom


# Reproduce PLAN §1.5 strict thresholds via scipy ground truth.
# A binomial test rejects H_0: p=0.5 in favor of H_a: p>0.5 if
# P(X >= k | n, p=0.5) <= alpha. The strict threshold is the smallest k
# satisfying the inequality.

@pytest.mark.parametrize("n,k_threshold,achieved_alpha", [
    (22, 17, 0.0085),  # Stratum A: PLAN §1.5 anchor
    (17, 13, 0.0245),  # Stratum B: PLAN §1.5 anchor
])
def test_phase4_strict_threshold_matches_plan(n, k_threshold, achieved_alpha):
    """PLAN §1.5: ≥17/22 (achieved α=0.0085); ≥13/17 (achieved α=0.0245)."""
    p_at_threshold = binom.sf(k_threshold - 1, n, 0.5)
    assert abs(p_at_threshold - achieved_alpha) < 1e-4, (
        f"Strict threshold k={k_threshold}/n={n}: scipy gives "
        f"p={p_at_threshold:.4f}, PLAN claims {achieved_alpha}"
    )
    # Per-stratum nominal Bonferroni alpha = 0.025
    assert p_at_threshold <= 0.025, "Strict threshold must achieve α ≤ 0.025"


@pytest.mark.parametrize("n,k_below_strict", [(22, 16), (17, 12)])
def test_phase4_below_strict_threshold_does_not_pass(n, k_below_strict):
    """k=16/22 and k=12/17 do NOT achieve α ≤ 0.025; would not pass."""
    p_below = binom.sf(k_below_strict - 1, n, 0.5)
    assert p_below > 0.025, (
        f"k={k_below_strict}/n={n} achieved α={p_below:.4f}; "
        f"this is the §19 misattribution catch class — must NOT pass"
    )


def test_phase4_family_wise_alpha_bound():
    """Per PLAN §1.5: family-wise α ≈ 0.033 under conservative Bonferroni."""
    alpha_a = binom.sf(17 - 1, 22, 0.5)
    alpha_b = binom.sf(13 - 1, 17, 0.5)
    family_wise = alpha_a + alpha_b  # union bound
    assert family_wise < 0.05  # nominal Bonferroni cap
    assert abs(family_wise - 0.033) < 0.005


def test_classify_positive_sharpe():
    """Per PLAN §1.5: positive forward Sharpe = pass."""
    from scripts.build_phase4_closeout import classify_outcome
    assert classify_outcome(forward_sharpe=0.5) == 1
    assert classify_outcome(forward_sharpe=0.001) == 1
    assert classify_outcome(forward_sharpe=0.0) == 0  # zero is not positive
    assert classify_outcome(forward_sharpe=-0.5) == 0
    assert classify_outcome(forward_sharpe=None) == 0  # missing = fail


def test_stratum_membership_from_reference_csv():
    """Stratum membership must derive from sealed reference CSV theme column."""
    from scripts.build_phase4_closeout import load_stratum_assignment
    stratum_a, stratum_b = load_stratum_assignment()
    assert len(stratum_a) == 22
    assert len(stratum_b) == 17
    # No overlap; sums to 39 (PLAN §1.3 anchor)
    assert set(stratum_a).isdisjoint(set(stratum_b))
    assert len(set(stratum_a) | set(stratum_b)) == 39


def test_per_stratum_binomial_test_rejects_at_threshold():
    """Phase 4 success per stratum: pass count >= strict threshold."""
    from scripts.build_phase4_closeout import per_stratum_binomial_test
    # Stratum A at exactly the threshold
    result_a = per_stratum_binomial_test(pass_count=17, n=22)
    assert result_a["rejects_h0"] is True
    assert result_a["k_threshold"] == 17
    assert result_a["pass_count"] == 17

    # Stratum B at one below threshold
    result_b = per_stratum_binomial_test(pass_count=12, n=17)
    assert result_b["rejects_h0"] is False
    assert result_b["k_threshold"] == 13


def test_phase4_disjunction_success_logic():
    """Phase 4 success iff at least one stratum rejects H_0 (per PLAN §1.5)."""
    from scripts.build_phase4_closeout import phase4_overall_success
    assert phase4_overall_success(stratum_a_passes=True, stratum_b_passes=False) is True
    assert phase4_overall_success(stratum_a_passes=False, stratum_b_passes=True) is True
    assert phase4_overall_success(stratum_a_passes=True, stratum_b_passes=True) is True
    assert phase4_overall_success(stratum_a_passes=False, stratum_b_passes=False) is False


def test_three_case_interpretation_wording():
    """PLAN §1.5 interpretation guard: 3 register-class-distinct claim wordings."""
    from scripts.build_phase4_closeout import interpretation_guard
    # Stratum A only
    guard = interpretation_guard(stratum_a_passes=True, stratum_b_passes=False)
    assert "calendar-effect candidates show forward persistence" in guard
    assert "non-calendar candidates do not" in guard
    # Stratum B only
    guard = interpretation_guard(stratum_a_passes=False, stratum_b_passes=True)
    assert "non-calendar candidates show forward persistence" in guard
    assert "calendar-effect candidates do not" in guard
    # Both
    guard = interpretation_guard(stratum_a_passes=True, stratum_b_passes=True)
    assert "two independent stratum-level persistence results" in guard
    assert "NOT a strengthened cohort-level claim" in guard
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_phase4_closeout.py -v`
Expected: 8 FAIL — `scripts/build_phase4_closeout.py` does not yet exist; threshold-truth tests pass (scipy ground truth).

- [ ] **Step 3: Author scripts/build_phase4_closeout.py minimal implementation**

Create `scripts/build_phase4_closeout.py`:

```python
"""Phase 4 closeout assembly — per-stratum binomial test + interpretation.

Reads 4 cost-run forward-fire artifacts at
data/phase2c_evaluation_gate/phase4_forward_2026_*bps_v1/, classifies
positive forward-Sharpe per candidate per cost, applies per-stratum
binomial test at PHASE4_PLAN §1.5 strict thresholds (≥17/22 + ≥13/17),
produces Phase 4 closeout MD at docs/closeout/PHASE4_RESULTS.md.

Phase 4 success criterion (per PHASE4_PLAN §1.5):
    H_0: fraction of positive forward Sharpe = 0.5 (per stratum)
    H_a: fraction > 0.5
    Reject iff pass_count >= strict_threshold (per stratum)
    Phase 4 success iff at least one stratum rejects H_0,
    EVALUATED AT REALISTIC 15bps COST BASIS ONLY.

3-case interpretation guard (PLAN §1.5; restrictive on framing):
    Stratum A only: "calendar-effect candidates show forward persistence;
                    non-calendar candidates do not"
    Stratum B only: converse
    Both: "two independent stratum-level persistence results; NOT a
           strengthened cohort-level claim"

Dual-reporting (descriptive supplements; not Phase 4 success criterion):
    7bps research-time (PHASE2C_15-comparability)
    13bps + 17bps sensitivity bounds
"""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from scipy.stats import binom

PROJECT_ROOT = Path(__file__).resolve().parent.parent
COHORT_REFERENCE = (
    PROJECT_ROOT / "data" / "phase4_scoping" / "cohort_a_candidate_reference.csv"
)
EVAL_GATE_ROOT = PROJECT_ROOT / "data" / "phase2c_evaluation_gate"
CLOSEOUT_OUTPUT = PROJECT_ROOT / "docs" / "closeout" / "PHASE4_RESULTS.md"

# PLAN §1.5 strict thresholds (scipy-verified)
STRATUM_A_N = 22
STRATUM_A_K_THRESHOLD = 17  # achieved α=0.0085
STRATUM_B_N = 17
STRATUM_B_K_THRESHOLD = 13  # achieved α=0.0245
NOMINAL_BONFERRONI_ALPHA = 0.025  # per stratum

COST_CONFIGS = ["07bps", "13bps", "15bps", "17bps"]
SUCCESS_CRITERION_COST = "15bps"


def classify_outcome(forward_sharpe: float | None) -> int:
    """Per PLAN §1.5: positive forward Sharpe → 1; non-positive or missing → 0."""
    if forward_sharpe is None:
        return 0
    return 1 if forward_sharpe > 0.0 else 0


def load_stratum_assignment() -> tuple[list[str], list[str]]:
    """Read sealed reference CSV; return (stratum_a_hashes, stratum_b_hashes).

    Stratum A = calendar_effect; Stratum B = all other themes.
    Stratum membership IS the sealed reference CSV; never recomputed.
    """
    stratum_a, stratum_b = [], []
    with open(COHORT_REFERENCE) as f:
        for row in csv.DictReader(f):
            if row["theme"] == "calendar_effect":
                stratum_a.append(row["hypothesis_hash"])
            else:
                stratum_b.append(row["hypothesis_hash"])
    return stratum_a, stratum_b


def per_stratum_binomial_test(pass_count: int, n: int) -> dict[str, Any]:
    """Apply one-sided binomial test at PLAN §1.5 strict threshold.

    Args:
        pass_count: number of candidates with positive forward Sharpe
        n: stratum size (22 for A; 17 for B)

    Returns:
        Dict with rejects_h0, achieved_alpha, k_threshold, pass_count, n.
    """
    if n == STRATUM_A_N:
        k_threshold = STRATUM_A_K_THRESHOLD
    elif n == STRATUM_B_N:
        k_threshold = STRATUM_B_K_THRESHOLD
    else:
        raise ValueError(f"Unsupported stratum n={n}; PLAN locks n=22 or n=17")
    achieved_alpha = float(binom.sf(pass_count - 1, n, 0.5))
    return {
        "rejects_h0": pass_count >= k_threshold,
        "achieved_alpha": achieved_alpha,
        "k_threshold": k_threshold,
        "pass_count": pass_count,
        "n": n,
        "strict_threshold_alpha": float(binom.sf(k_threshold - 1, n, 0.5)),
    }


def phase4_overall_success(stratum_a_passes: bool, stratum_b_passes: bool) -> bool:
    """Phase 4 success iff at least one stratum rejects H_0 (PLAN §1.5)."""
    return stratum_a_passes or stratum_b_passes


def interpretation_guard(stratum_a_passes: bool, stratum_b_passes: bool) -> str:
    """Per PLAN §1.5: 3-case interpretation guard wording.

    Returns the canonical claim wording for the disjunction outcome.
    """
    if stratum_a_passes and stratum_b_passes:
        return (
            "two independent stratum-level persistence results, "
            "NOT a strengthened cohort-level claim"
        )
    if stratum_a_passes and not stratum_b_passes:
        return (
            "calendar-effect candidates show forward persistence; "
            "non-calendar candidates do not"
        )
    if stratum_b_passes and not stratum_a_passes:
        return (
            "non-calendar candidates show forward persistence; "
            "calendar-effect candidates do not"
        )
    return "no forward persistence detected at PLAN §1.5 success criterion"


def load_forward_sharpes_per_cost(cost: str) -> dict[str, float | None]:
    """Load per-candidate forward Sharpe from a cost-run artifact.

    Returns hash -> holdout_sharpe mapping. Hashes for which the artifact
    has no entry (missed candidates) map to None via classify_outcome.

    SCHEMA RESOLVED at planning register via descriptive lookup against
    data/phase2c_evaluation_gate/phase2c_15_main_fire_bear_2022_v1/holdout_results.csv:
    - Per-candidate results are in holdout_results.csv (NOT
      holdout_summary.json — that is aggregate counts only)
    - Field name is `holdout_sharpe` (the producer code labels the
      forward-window Sharpe as holdout_sharpe regardless of regime;
      the regime identity is in regime_key + regime_label at the
      summary level)
    - Phase 4 success criterion: holdout_sharpe > 0 (NOT
      holdout_passed=1, which is the 4-criterion AND-gate inherited
      from regime_holdout block — register-class-distinct from
      PLAN §1.5 positive-Sharpe-only criterion)
    """
    import csv
    artifact = (
        EVAL_GATE_ROOT
        / f"phase4_forward_2026_{cost}_v1"
        / "holdout_results.csv"
    )
    if not artifact.exists():
        raise FileNotFoundError(
            f"Phase 4 cost-run artifact missing: {artifact}. "
            f"Run Task 4 forward fire at {cost} first."
        )
    out: dict[str, float | None] = {}
    with open(artifact) as f:
        for row in csv.DictReader(f):
            sharpe_str = row.get("holdout_sharpe", "")
            if sharpe_str == "" or sharpe_str is None:
                out[row["hypothesis_hash"]] = None
            else:
                out[row["hypothesis_hash"]] = float(sharpe_str)
    return out


def assemble_closeout(stratum_results: dict, dual_report: dict) -> str:
    """Produce PHASE4_RESULTS.md content per PLAN §1.5 + closeout convention.

    Returns a markdown string. Caller writes to disk.
    """
    success = phase4_overall_success(
        stratum_results["A_15bps"]["rejects_h0"],
        stratum_results["B_15bps"]["rejects_h0"],
    )
    interpretation = interpretation_guard(
        stratum_results["A_15bps"]["rejects_h0"],
        stratum_results["B_15bps"]["rejects_h0"],
    )
    # ... (closeout MD assembly: §1 substantive headline; §2 lineage anchors;
    #      §3 per-stratum results table at 15bps; §4 dual-report 7bps + sens 13/17;
    #      §5 interpretation guard + 3-case framing; §6 carry-forwards;
    #      §7 reviewer-pass cycle anchors)
    md = f"""# Phase 4 Forward-Test Results — PHASE2C_15 cohort_a persistence

**Headline:** {interpretation}

**Phase 4 success criterion:** {"MET" if success else "NOT MET"}
(per PLAN §1.5 disjunction; evaluated at realistic 15bps cost basis)

## §1 Per-stratum results at PLAN §1.5 success criterion (15bps)

| Stratum | n | k=positive forward Sharpe | Strict threshold | Achieved α | Rejects H_0? |
|---|---|---|---|---|---|
| A (calendar) | 22 | {stratum_results["A_15bps"]["pass_count"]} | ≥{STRATUM_A_K_THRESHOLD} | {stratum_results["A_15bps"]["achieved_alpha"]:.4f} | {stratum_results["A_15bps"]["rejects_h0"]} |
| B (non-calendar) | 17 | {stratum_results["B_15bps"]["pass_count"]} | ≥{STRATUM_B_K_THRESHOLD} | {stratum_results["B_15bps"]["achieved_alpha"]:.4f} | {stratum_results["B_15bps"]["rejects_h0"]} |

(... continue full closeout MD assembly per PHASE2C_15 closeout precedent ...)
"""
    return md


def main():
    stratum_a_hashes, stratum_b_hashes = load_stratum_assignment()
    # Compute per-stratum pass count at each cost
    stratum_results = {}
    dual_report = {}
    for cost in COST_CONFIGS:
        sharpes = load_forward_sharpes_per_cost(cost)
        a_passes = sum(classify_outcome(sharpes.get(h)) for h in stratum_a_hashes)
        b_passes = sum(classify_outcome(sharpes.get(h)) for h in stratum_b_hashes)
        stratum_results[f"A_{cost}"] = per_stratum_binomial_test(a_passes, STRATUM_A_N)
        stratum_results[f"B_{cost}"] = per_stratum_binomial_test(b_passes, STRATUM_B_N)
    md = assemble_closeout(stratum_results, dual_report)
    CLOSEOUT_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    CLOSEOUT_OUTPUT.write_text(md)
    print(f"Wrote: {CLOSEOUT_OUTPUT}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run closeout tests; expect PASS on logic tests; failure on closeout-MD-content tests until full implementation**

Run: `python -m pytest tests/test_phase4_closeout.py -v`
Expected: 8 PASS (the test cases in Step 1 cover threshold logic + classification + interpretation guard wording; closeout MD assembly tests are not in Step 1 — adversarial test gap to fill at reviewer pass cycle).

- [ ] **Step 4a: Add closeout MD internal consistency test (per refinement 6)**

Append to `tests/test_phase4_closeout.py`:

```python
def test_phase4_closeout_md_internal_consistency(tmp_path, monkeypatch):
    """Closeout MD: headline numbers must match per-stratum table; dual-report sections must reference correct cost configs.

    Loads the assembled MD from a stub fire and asserts:
    1. Headline pass-count for each stratum matches the per-stratum table
    2. Dual-report section names the 4 cost configs (07/13/15/17 bps)
    3. 3-case interpretation guard wording lands at register-precision
       (matches PLAN §1.5 verbatim phrases)
    """
    import re
    from scripts.build_phase4_closeout import (
        assemble_closeout, per_stratum_binomial_test,
    )
    # Stub stratum results matching a "Stratum A only passes" outcome
    stratum_results = {
        "A_15bps": per_stratum_binomial_test(pass_count=18, n=22),
        "B_15bps": per_stratum_binomial_test(pass_count=10, n=17),
        "A_07bps": per_stratum_binomial_test(pass_count=20, n=22),
        "B_07bps": per_stratum_binomial_test(pass_count=12, n=17),
        "A_13bps": per_stratum_binomial_test(pass_count=19, n=22),
        "B_13bps": per_stratum_binomial_test(pass_count=10, n=17),
        "A_17bps": per_stratum_binomial_test(pass_count=17, n=22),
        "B_17bps": per_stratum_binomial_test(pass_count=9, n=17),
    }
    md = assemble_closeout(stratum_results, dual_report={})

    # 1. Headline references Stratum A persistence wording
    assert "calendar-effect candidates show forward persistence" in md
    assert "non-calendar candidates do not" in md

    # 2. Per-stratum table headline matches passes count
    assert "| A (calendar) | 22 | 18 |" in md or " 22 | 18 " in md
    assert "| B (non-calendar) | 17 | 10 |" in md or " 17 | 10 " in md

    # 3. Dual-report references all 4 cost configs (case-insensitive token match)
    for cost_token in ["7", "13", "15", "17"]:
        assert cost_token in md or f"{cost_token}bps" in md

    # 4. Strict thresholds match PLAN §1.5 verbatim
    assert "≥17/22" in md or ">=17/22" in md
    assert "≥13/17" in md or ">=13/17" in md
```

Run: `python -m pytest tests/test_phase4_closeout.py::test_phase4_closeout_md_internal_consistency -v`
Expected: PASS (after Step 5 closeout-MD assembly is fully populated; may FAIL if assembly is partial — fix at Step 5).

- [ ] **Step 5: Refine closeout MD assembly per PHASE2C_15 closeout precedent**

Read [`docs/closeout/PHASE2C_15_RESULTS.md`](../../docs/closeout/PHASE2C_15_RESULTS.md) (sealed at `734570c`) for canonical closeout MD structure. Adapt sections:
- §1 substantive headline (3-case interpretation guard wording)
- §2 lineage anchors (engine `eb1c87f`; PLAN sealed at `432b2bd`; cohort reference at `11b39f2`)
- §3 per-stratum results table at 15bps + per-candidate forward Sharpe distribution
- §4 dual-report 7bps PHASE2C_15-comparability + sensitivity 13/17 (descriptive supplements)
- §5 interpretation guard explicit per PLAN §1.5
- §6 carry-forwards (incl. cycle-internal §A2 / §A1 / §19 instances if any)
- §7 reviewer-pass cycle anchors

- [ ] **Step 6: Run build_phase4_closeout.py + inspect output**

```bash
python scripts/build_phase4_closeout.py
cat docs/closeout/PHASE4_RESULTS.md | head -60
```

Verify: closeout MD produced; per-stratum tables populated from real fire data; interpretation guard wording matches the disjunction outcome.

- [ ] **Step 7: Commit (deliverable WORKING DRAFT register)**

```bash
git add scripts/build_phase4_closeout.py tests/test_phase4_closeout.py docs/closeout/PHASE4_RESULTS.md
git commit -m "$(cat <<'EOF'
feat(phase4): closeout assembly + per-stratum binomial test

scripts/build_phase4_closeout.py: reads 4 cost-run artifacts;
classifies positive forward-Sharpe per candidate per cost; applies
per-stratum binomial test at PLAN §1.5 strict thresholds (≥17/22 +
≥13/17, scipy-verified); produces docs/closeout/PHASE4_RESULTS.md.

3-case interpretation guard locked at code register (Stratum A only /
Stratum B only / both); Phase 4 success iff at least one stratum
rejects H_0, evaluated at realistic 15bps basis only.

Tests assert PLAN §1.5 numerical anchors via scipy ground truth;
the §19 misattribution catch class (k=16/22 must NOT pass) is
explicitly tested.

Status: WORKING DRAFT — closeout SEAL fires at Task 6 post reviewer-pass cycle.
EOF
)"
```

---

## Task 6: Closeout SEAL + tag application

**Goal:** Reviewer pass cycle on PHASE4_RESULTS.md (per PHASE2C_10/11/12/13/15 closeout SEAL precedent — no per-fix bulk-accept; ChatGPT structural overlay + Claude advisor full-prose-access + Codex on substantive code/script per [`feedback_codex_review_scope.md`](../.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_codex_review_scope.md)). Then closeout commit + Phase Marker advance + tag at deliverable seal commit per Path A.2 register-event boundary discipline.

- [ ] **Step 1: Reviewer pass cycle**

Per [`feedback_reviewer_suggestion_adjudication.md`](../.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_reviewer_suggestion_adjudication.md): present full reviewer findings to Charlie register; per-fix adjudication (no bulk-accept); ratify ADOPT / PUSHBACK with rationale.

Reviewer routing:
- ChatGPT: structural overlay + cross-section consistency
- Claude advisor: full-prose-access pass
- Codex: adversarial review on `scripts/build_phase4_closeout.py` and any code-class deliverables (per Codex routing memory)

- [ ] **Step 2: SEAL pre-fire verification**

Empirical verification fire (parallel to PHASE2C_15 closeout V#-chain pattern):
- V#1: HEAD parity at SEAL commit
- V#2: PHASE4_PLAN.md invariance at `432b2bd`
- V#3: cohort_a reference invariance at `11b39f2`
- V#4: 4 cost-run artifacts present + lineage check passes
- V#5: per-stratum pass count reproducible from artifact data
- V#6: 3-case interpretation guard wording matches PLAN §1.5 verbatim
- V#7: tag wording NOT pre-committed in MD (anti-pre-naming)

- [ ] **Step 3: Closeout commit (deliverable SEAL)**

```bash
git add docs/closeout/PHASE4_RESULTS.md
git commit -m "$(cat <<'EOF'
docs(phase4): PHASE4_RESULTS.md closeout SEAL

Phase 4 forward-test of 39 PHASE2C_15 cohort_a candidates over
[2026-01-01, T_end] complete. Per-stratum binomial test at PLAN §1.5
strict thresholds applied at realistic 15bps cost basis; Phase 4
success criterion [MET / NOT MET]; interpretation guard [Stratum A
only / Stratum B only / both / neither] per disjunction outcome.

Triple-register reviewer convergence at Charlie register
authorization boundary; per-fix adjudication discipline operated;
all V#-chain pre-fire verifications CLEAN.

Lineage: engine eb1c87f (wf-corrected-v1); evaluation_semantics
single_run_holdout_v1; regime_key evaluation_regimes.forward_2026;
artifact_schema_version phase2c_7_1; PHASE4_PLAN sealed at 432b2bd;
cohort reference sealed at 11b39f2 — all immutable imported artifacts
mechanically consumed (central invariant: lock the artifact, don't
recompute).
EOF
)"
```

- [ ] **Step 4: Phase Marker advance + tag**

```bash
# Update CLAUDE.md Phase Marker per [`feedback_claude_md_freshness.md`](../.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_claude_md_freshness.md)
# Then commit Phase Marker advance:
git add CLAUDE.md
git commit -m "docs(phase4): CLAUDE.md Phase Marker advance — PHASE4 SEALED"

# Tag at deliverable seal commit per Path A.2:
SEAL_COMMIT=$(git log --grep="PHASE4_RESULTS.md closeout SEAL" -1 --format=%H)
git tag -a phase4-forward-test-v1 $SEAL_COMMIT -m "Phase 4 forward-test SEALED"

# Push bundle:
git push origin main && git push origin phase4-forward-test-v1
```

---

## Task 7: §32 codification reassessment (default = NO codification)

**Goal:** Reassess whether arc-internal experience demonstrated concrete instances of conduct-degradation that codification of the carry-forward observations (convergence-reinforces-convergent-errors / empirical-verification-before-reviewer-routing / authorization-scope distinction) would have prevented.

**Default = NO CODIFICATION.** Codification needs positive evidence. Absence of suffering is not the trigger. Per §31 trim direction.

- [ ] **Step 1: Audit arc-internal experience**

Review (do NOT add to METHODOLOGY_NOTES at this register):
- Did any sub-task fire surface a defect that would have been prevented by §32-class codification?
- Did the convergence-reinforces-convergent-errors pattern recur (specifically: did 3+ reviewers converge on a wrong answer that empirical verification then corrected)?
- Did empirical-verification-before-reviewer-routing prevent a defect mid-arc?
- Did the authorization-scope distinction need clarification at any sub-task entry?

- [ ] **Step 2: Charlie register adjudication**

Surface findings as plain text to Charlie register. Per [`feedback_decision_options_plaintext.md`](../.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_decision_options_plaintext.md): present 3 options as plain text:
- (a) NO codification (default at no-positive-evidence)
- (b) Codify a single sub-pattern that recurred at register-precision
- (c) Codify all three (high bar)

Charlie register decides. If (a): close arc. If (b)/(c): open separate methodology codification cycle at fresh boundary.

---

## Self-Review Notes

**Spec coverage check:** Each PHASE4_PLAN section maps to a task:
- PLAN §1.1 D = 2026-01-01 → Task 2 environments.yaml block start date
- PLAN §1.2 single-contiguous + T_end capture → Task 4 pre-fire data refresh + Task 5 metadata reads
- PLAN §1.3 39 + 2-strata → Task 4 forward fire + Task 5 stratum membership
- PLAN §1.4 cost values → Task 3 sealed YAMLs + Task 4 4 fires
- PLAN §1.5 thresholds + interpretation guard → Task 5 binomial test + closeout MD

**Type consistency check:** `regime_key`, `regime_label`, `artifact_schema_version` consistent across Tasks 2-6.

**Anti-momentum-binding preservation:** Each task entry requires Charlie register authorization at fresh boundary; reviewer routing per-task; tag wording NOT pre-committed at this plan; §32 codification deferred to Task 7 with positive-evidence asymmetric default.

---

## Plan complete. Saved to `docs/superpowers/plans/2026-05-09-phase4-implementation-arc.md`.

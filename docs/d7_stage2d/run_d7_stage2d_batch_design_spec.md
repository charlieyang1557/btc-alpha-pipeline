# `run_d7_stage2d_batch.py` — Design Spec v2

Ratified design spec for `scripts/run_d7_stage2d_batch.py`, the 200-position
D7b live-fire orchestrator for Phase 2B D7 Stage 2d. Produced via A-lite
session — design only, no code authoring.

**Authority anchor**: `docs/d7_stage2d/D7_STAGE2D_SCOPE_LOCK_v2.md`
SHA256 `b4cad5873707c6eba272d313e0214011cb5ca91b142126013946f91a72496382`.
Every constant and behavior below cites its scope-lock clause.

---

## Pre-drafting disk verification — C.7 revised

`agents/orchestrator/budget_ledger.py:93-97` strictly enum-validates
`backend_kind` against `VALID_BACKEND_KINDS = ("d6_proposer", "d7b_critic")`.
An audit-only ledger row for pos 116 with `backend_kind="d7b_critic_skipped"`
would require enum widening, schema migration, consumer updates
(`total_by_backend_kind`), and test updates — all outside Stage 2d scope.

**Revised C.7 ruling (adopted)**: **no ledger row for pos 116**. 200 per-call
records; 199 ledger rows max on non-abort completion. The 200-vs-199 delta
is a feature, not an inconsistency — codified explicitly in §11.3.

Stage 2c naming convention confirmed (`scripts/run_d7_stage2c_batch.py:70-118`):
`STAGE2C_*` prefix, `RAW_PAYLOAD_ROOT`, `DRYRUN_ROOT`, `LEDGER_PATH`. Stage 2d
adopts `STAGE2D_*` prefix by symmetry.

---

## §1. Purpose and Scope

**Purpose**: define the architecture of `scripts/run_d7_stage2d_batch.py` — the
200-candidate D7b live-fire orchestrator for Stage 2d pre-fire deep-dive
validation of the D7 critic.

**In-scope**:
- CLI surface and flag semantics
- Startup gates (including `stage2d_self_check.py` subprocess gate)
- Per-position execution loop (199 live calls + 1 synthetic skip at pos 116)
- Abort-rule evaluator (Lock 7 rules a-g)
- Per-call record schema (including synthetic pos 116 record per Lock 1.5)
- Aggregate record schema (three-counter critic_status_counts, stratum
  breakdown, template SHA anchor)
- Stub/live physical isolation contract
- BudgetLedger integration

**Out-of-scope (non-goals)**:
- Semantic evaluation of D7b outputs (acceptance notebook's job)
- Sign-off adjudication (post-fire reviewer workflow)
- Stage 2c → Stage 2d stub-fixture-isolation retrofit (pre-D8 task;
  separate scope lock v2.1)
- Stage 2e or later phases

---

## §2. CLI Specification

**Baseline CLI**: `--stub | --confirm-live`, mutually exclusive, one required.
No additional operator flags. Mirrors Stage 2c (`scripts/run_d7_stage2c_batch.py`)
CLI surface exactly.

**Synopsis**:
```
python scripts/run_d7_stage2d_batch.py (--stub | --confirm-live)
```

**Flag semantics**:

| Flag | Behavior |
|---|---|
| `--stub` | No API calls; `StubD7bBackend` for all 199 live calls; writes to `dryrun_payloads/dryrun_stage2d/`; stub-scoped ledger at `dryrun_payloads/dryrun_stage2d/ledger_dryrun.db`; `api_call_kind_override="d7b_critic_stub"` |
| `--confirm-live` | Live Sonnet calls via `LiveSonnetD7bBackend`; requires `ANTHROPIC_API_KEY`; writes to `raw_payloads/batch_5cf76668-.../`; uses production `agents/spend_ledger.db`; `api_call_kind_override="d7b_critic_live"` |

**Exit codes**:

| Code | Condition |
|---|---|
| 0 | Script completed normally and wrote a valid aggregate record, whether the sequence completed all 200 records or terminated early under Lock 7 abort rules. |
| 1 | `Stage2dStartupError` — any startup gate failed; no ledger rows written, no records written |
| 2 | Uncaught exception mid-fire — partial state may exist; requires human adjudication |

---

## §3. Hard-Coded Constants

Mirrors Stage 2c naming (`STAGE2D_*` prefix). All values trace to scope lock.

```python
# Lock 1.6 / Lock 10.2 — source/call arithmetic
STAGE2D_SOURCE_N: int = 200
STAGE2D_LIVE_D7B_CALL_N: int = 199
STAGE2D_SKIPPED_POSITIONS: tuple[int, ...] = (116,)

# Lock 1.3 — batch identity
STAGE2D_BATCH_UUID: str = "5cf76668-47d1-48d7-bd90-db06d31982ed"

# Lock 9 — cost envelope
STAGE2D_PER_CALL_COST_CEILING_USD: float = 0.08    # Rule (d)
STAGE2D_TOTAL_COST_CAP_USD: float = 8.00           # Rule (e)

# Lock 7 — error thresholds
STAGE2D_CONSECUTIVE_API_ERROR_THRESHOLD: int = 2   # Rule (a)
STAGE2D_ERROR_RATE_K_FLOOR: int = 3                # Rule (b) K
STAGE2D_ERROR_RATE_THRESHOLD: float = 0.40         # Rule (b) > 40%
STAGE2D_CONTENT_ERROR_ABS_THRESHOLD: int = 4       # Rule (c)

# Lock 10 — I/O paths
RAW_PAYLOAD_ROOT: Path = Path("raw_payloads")
LEDGER_PATH: Path = Path("agents/spend_ledger.db")
DRYRUN_ROOT: Path = Path("dryrun_payloads/dryrun_stage2d")
STAGE2D_BATCH_DIR_NAME: str = f"batch_{STAGE2D_BATCH_UUID}"

# Lock 10.5 — Stage 2c preservation
STAGE2C_ARCHIVE_RELATIVE: Path = Path("critic/stage2c_archive")

# HG-series anchors (pre-fire gate inputs) — Lock 11.5
# Anchor commit for replay_candidates.json (Task 2B commit, 2026-04-18)
STAGE2D_REPLAY_CANDIDATES_ANCHOR_COMMIT: str = "2771bef"
STAGE2D_EXPECTATIONS_PATH: Path = Path("docs/d7_stage2d/stage2d_expectations.md")
STAGE2D_REPLAY_CANDIDATES_PATH: Path = Path("docs/d7_stage2d/replay_candidates.json")
STAGE2D_TEST_RETEST_PATH: Path = Path("docs/d7_stage2d/test_retest_baselines.json")
STAGE2D_DEEP_DIVE_PATH: Path = Path("docs/d7_stage2d/deep_dive_candidates.json")
STAGE2D_LABEL_UNIVERSE_PATH: Path = Path("docs/d7_stage2d/label_universe_analysis.json")
STAGE2D_SELF_CHECK_SCRIPT: Path = Path("scripts/stage2d_self_check.py")

# Lock 10.3 — checkpoint cadence
STAGE2D_CHECKPOINT_EVERY_N: int = 50               # Projected-vs-actual log points
```

Every constant commented with `# Lock <N>` citation.

---

## §4. Scope-Lock Clause Carry-Forward Table

| Lock / Clause | Fire-script relevance | Carry-forward? | Stage 2d adaptation | Implementation hook |
|---|---|---|---|---|
| §1.1 — source counts | Constants | Adapted | `STAGE2D_SOURCE_N=200`, `STAGE2D_LIVE_D7B_CALL_N=199` | `__main__` constants |
| §1.2 — fire script constants | Constants | Adapted | All `STAGE2D_*` hardcoded | `__main__` constants |
| §1.3 — execution mode | CLI | As-is | `--stub` / `--confirm-live` | argparse |
| §1.4 — firing order | Loop iteration | As-is | position ascending from `replay_candidates.json` | main loop |
| §1.5 — pos 116 treatment | New in 2d | **New** | Synthetic record, 11 Lock 1.5 fields verbatim | `_synthesize_pos116_record()` |
| §1.6 — 200-record invariant | Aggregate verification | **New** | Aggregate builder asserts 200 entries on non-abort | `build_aggregate_record()` |
| §2.x — expectations scope | Startup gate input | Adapted | Structural checks delegated to `stage2d_self_check.py` | Gate 1 subprocess |
| §3.x — test-retest grid | Input (read-only) | **New** | `test_retest_baselines.json` attached to aggregate | `_load_test_retest()` |
| §4.x — deep-dive sampling | Input (read-only) | **New** | `deep_dive_candidates.json` attached to aggregate | `_load_deep_dive()` |
| §5.x — Stage 2c carry-forward | Inherited (documentation) | As-is | Encoded in self_check | (none in script) |
| §6.x — aggregate claims | Inherited (documentation) | As-is | Encoded in expectations+self_check | (none in script) |
| §7.1-7.5 — rules (a)-(e) | Abort eval | Adapted | Denominator excludes skipped per §7.8 (C.1/C.2 rulings) | `should_abort()` |
| §7.6 — rule (f) | N/A | Deferred | Not implemented | (none) |
| §7.7 — rule (g) NEW | Abort eval | **New** | `skipped_source_invalid` at pos ≠ 116 → abort | `should_abort()` rule g |
| §7.8 — skipped isolation | Abort eval bookkeeping | **New** | Transparent for rule (a); excluded from (b) K/denom and (c) | `_filter_non_skipped()` |
| §8 — narrow-claim (inherited) | Documentation | Inherited | Enforced in expectations; no fire-script code | (none) |
| §9.1-9.4 — cost envelope | Rules (d)/(e) | As-is | `$0.08` / `$8.00` thresholds verbatim | Constants + `should_abort()` |
| §10.1 — new script mandatory | Process | N/A | This spec is the authority | (none) |
| §10.2 — parallels to 2c | Core architecture | **Adapted** | Stage 2c skeleton reused with 2d deltas (pos 116, rule g, self_check, archive gate, 3-counter status) | Whole script |
| §10.2a — three-JSON selection | Startup gate inputs | **New** | Three-JSON selection (read-only inputs): fire script consumes `replay_candidates.json` as the sole firing-order source; `deep_dive_candidates.json` and `test_retest_baselines.json` are read-only auxiliary artifacts for metadata attachment and post-fire audit context, not selection drivers. | `_load_replay_candidates()` |
| §10.2b — fourth artifact | Startup gate input | **New** | `label_universe_analysis.json` attached to aggregate; fire script does not derive | Gate 8 read-only input |
| §10.3 — 2d-specific additions | Multiple | **New** | Three-counter `critic_status_counts`, stratum breakdown, checkpoint logs, pos 116 handling | Aggregate builder + main loop |
| §10.4 — anti-drift | SHA anchor | As-is | Template SHA captured at startup | `_capture_prompt_template_sha()` |
| §10.5 — Stage 2c archival | Live-mode gate | **New** | Gate 11 hard-fail if archive missing | `_gate_stage2c_archival()` |
| §11.1 — required sections | Expectations structural | Inherited | Encoded in self_check Lock 12 gates | (none in fire script) |
| §11.1.a — authoring conventions | Expectations structural | Inherited | Encoded in self_check | (none in fire script) |
| §11.2 — derivation script | Pre-fire artifact | N/A | `derive_d7_stage2d_label_universes.py` runs pre-fire, not in fire script | (none) |
| §11.3 / 11.4 — per-candidate formats | Expectations structural | Inherited | Encoded in self_check | (none in fire script) |
| §11.5 — commit workflow | Pre-fire ordering | Inherited | Fire runs only after E5 seal + self_check subprocess | (none in script; process-level) |

Cells marked "New" require Stage-2d-specific code paths; all "As-is" rows reuse
Stage 2c shape.

---

## §5. Architecture Overview

### Module structure

Single-file script `scripts/run_d7_stage2d_batch.py`, target ~1600 lines
(comparable to `run_d7_stage2c_batch.py`'s 1603). No new modules; uses existing
`agents/critic/*` and `agents/orchestrator/budget_ledger.py`.

### Function call graph

```
main()
├── _load_dotenv()
├── argparse parse
├── build_stage2d_config(confirm_live, stub) -> Stage2dConfig
├── run_stage2d(config)
│   ├── _assert_stub_isolation(config)
│   ├── _startup_gates(config)                        [§6]
│   │   ├── _gate_self_check_subprocess(config)       [C.4]
│   │   ├── _gate_replay_candidates_exists_and_parses [HG1]
│   │   ├── _gate_replay_candidates_sha_anchor        [HG2]
│   │   ├── _gate_replay_candidates_invariants        [§1.3, §1.4, §1.5]
│   │   ├── _gate_expectations_exists                 [HG3]
│   │   ├── _gate_expectations_committed              [HG5]
│   │   ├── _gate_prompt_template_sha                 [HG6 → stored in config]
│   │   ├── _gate_read_only_inputs                    [§3.x, §4.x, §10.2b]
│   │   ├── _gate_aggregate_record_absent             [HG8]
│   │   ├── _gate_partial_prior_run                   [live only]
│   │   └── _gate_stage2c_archival                    [§10.5, live only]
│   ├── candidates = _load_replay_candidates(config)
│   ├── template_sha = _capture_prompt_template_sha()
│   ├── ledger = BudgetLedger(config.ledger_path)
│   ├── backend = _build_d7b_backend(config)          [stub vs live]
│   ├── per_call_records = []
│   ├── for idx, cand in enumerate(candidates, start=1):
│   │     ├── if cand.position in STAGE2D_SKIPPED_POSITIONS:
│   │     │     record = _synthesize_pos116_record(cand, idx)    [C.5 / §9]
│   │     │     NOTE: no ledger write — per C.7 revised ruling
│   │     ├── else:
│   │     │     record = _run_one_call(cand, idx, backend, ledger, config)
│   │     ├── per_call_records.append(record)
│   │     ├── _log_checkpoint_if_due(idx, per_call_records, cumulative_cost)  [§10.3]
│   │     ├── abort, reason = should_abort(idx, per_call_records,
│   │     │                                 per_call_cost, cumulative_cost)  [§7]
│   │     └── if abort: break
│   ├── aggregate = build_aggregate_record(per_call_records, template_sha,
│   │                                       test_retest, deep_dive,
│   │                                       label_universe, abort_reason)
│   ├── _hg20_selection_drift_check(aggregate)        [§10.4]
│   ├── aggregate["write_completed_at"] = iso_utc_now()  [LAST — Lock 11]
│   └── atomic_write_json(aggregate_path, aggregate)
└── sys.exit(0 | 1 | 2)
```

### Dispatch flow invariants

1. Startup gates run in order; first failure raises `Stage2dStartupError` →
   exit 1 before any I/O to output roots.
2. Ledger writes happen only inside `_run_one_call()` (not in
   `_synthesize_pos116_record()`).
3. `per_call_records` is the single source of truth for abort evaluation.
4. Aggregate record is written once, atomically, at the end — success or
   abort path.

---

## §6. Startup Gates Sequence

Executed in order by `_startup_gates(config)`. Any failure raises
`Stage2dStartupError(message)` → exit 1. No I/O to output roots until all
gates pass.

| # | Gate | Mode | Source authority |
|---|---|---|---|
| 1 | `_gate_self_check_subprocess` | both | C.4 ruling + design spec Task 3b.3 |
| 2 | `_gate_replay_candidates_exists_and_parses` | both | HG1 |
| 3 | `_gate_replay_candidates_sha_anchor` | both | HG2 / §11.5 |
| 4 | `_gate_replay_candidates_invariants` | both | §1.3, §1.4, §1.5 |
| 5 | `_gate_expectations_exists` | both | HG3 |
| 6 | `_gate_expectations_committed` | both | HG5 / §11.5 |
| 7 | `_gate_prompt_template_sha` | both | §10.4 / HG6 |
| 8 | `_gate_read_only_inputs` | both | §3.x, §4.x, §10.2b |
| 9 | `_gate_aggregate_record_absent` | both | HG8 |
| 10 | `_gate_partial_prior_run` | live only | Stage 2c pattern |
| 11 | `_gate_stage2c_archival` | live only | §10.5 |

### Gate 1 — `_gate_self_check_subprocess` detail (per C.4)

```python
def _gate_self_check_subprocess(config: Stage2dConfig) -> None:
    result = subprocess.run(
        [sys.executable, str(STAGE2D_SELF_CHECK_SCRIPT)],
        capture_output=True, text=True, timeout=120,
        cwd=REPO_ROOT,
    )
    if result.returncode != 0:
        raise Stage2dStartupError(
            f"HG_SELF_CHECK: stage2d_self_check.py exited {result.returncode}\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    # stdout captured to startup audit section; never swallowed
    config.startup_audit.append({
        "gate": "self_check_subprocess",
        "exit_code": 0,
        "stdout": result.stdout,
        "stderr": result.stderr,
    })
```

Gate placed **first** because its failure implies pre-registration seal is
broken — no other gate is meaningful if 28-gate validator fails.

### Gate 11 — `_gate_stage2c_archival` detail (per C.6 hard-fail)

```python
def _gate_stage2c_archival(config: Stage2dConfig) -> None:
    if config.mode != "live":
        return
    archive_dir = (RAW_PAYLOAD_ROOT / STAGE2D_BATCH_DIR_NAME / STAGE2C_ARCHIVE_RELATIVE)
    if not archive_dir.is_dir():
        raise Stage2dStartupError(
            f"HG_STAGE2C_ARCHIVE: Lock 10.5 preservation contract failed. "
            f"Expected directory missing: {archive_dir}"
        )
    # Per Verification C (Turn 3b): 20 Stage 2c positions × 3 mandatory files
    # {prompt, response, critic_result} each. Optional traceback files accepted.
    stage2c_positions = [
        17, 22, 27, 32, 62, 72, 73, 74, 77, 83,
        97, 102, 107, 112, 117, 138, 143, 147, 152, 162,
    ]
    expected = set()
    for pos in stage2c_positions:
        for suffix in ("prompt.txt", "response.json", "critic_result.json"):
            expected.add(f"call_{pos:04d}_{suffix}")
    missing = expected - {p.name for p in archive_dir.iterdir()}
    if missing:
        raise Stage2dStartupError(
            f"HG_STAGE2C_ARCHIVE: preservation directory missing files: {sorted(missing)}"
        )
```

---

## §7. Abort Rules — Deterministic Pseudocode

`should_abort(idx: int, records: list[dict], per_call_cost: float, cumulative_cost: float) -> tuple[bool, str | None]`

Evaluation order (per C.3 ruling): **g → a → b → c → d → e**. First match
returns.

```python
def should_abort(idx, records, per_call_cost, cumulative_cost):
    # Rule (g) — §7.7 — unexpected skipped_source at position != 116
    last = records[-1]
    if (last["critic_status"] == "skipped_source_invalid"
            and last["position"] not in STAGE2D_SKIPPED_POSITIONS):
        return True, "unexpected_skipped_source"

    # Non-skipped subsequence used by rules (a), (b), (c) — per §7.8
    non_skipped = [r for r in records if r["critic_status"] != "skipped_source_invalid"]

    # Rule (a) — §7.1 — 2 consecutive api_level errors in non-skipped subsequence
    # Per C.1: skipped records are transparent — neither reset nor increment
    if len(non_skipped) >= STAGE2D_CONSECUTIVE_API_ERROR_THRESHOLD:
        tail = non_skipped[-STAGE2D_CONSECUTIVE_API_ERROR_THRESHOLD:]
        if all(r["critic_status"] == "d7b_error"
               and r.get("d7b_error_category") == "api_level"
               for r in tail):
            return True, "consecutive_api_errors"

    # Rule (b) — §7.2 — error rate > 40% at K >= 3 non-skipped
    # Per C.2: K counts non-skipped only
    K = len(non_skipped)
    if K >= STAGE2D_ERROR_RATE_K_FLOOR:
        errors = sum(1 for r in non_skipped if r["critic_status"] == "d7b_error")
        if (errors / K) > STAGE2D_ERROR_RATE_THRESHOLD:
            return True, "error_rate_threshold"

    # Rule (c) — §7.3 — content_level errors >= 4 (absolute, non-skipped)
    content_errors = sum(
        1 for r in non_skipped
        if r["critic_status"] == "d7b_error"
        and r.get("d7b_error_category") == "content_level"
    )
    if content_errors >= STAGE2D_CONTENT_ERROR_ABS_THRESHOLD:
        return True, "content_level_threshold"

    # Rule (d) — §7.4 — per-call cost > $0.08
    if per_call_cost > STAGE2D_PER_CALL_COST_CEILING_USD:
        return True, "per_call_cost_exceeded"

    # Rule (e) — §7.5 — cumulative cost > $8.00
    if cumulative_cost > STAGE2D_TOTAL_COST_CAP_USD:
        return True, "cumulative_cost_cap_exceeded"

    return False, None
```

### Bookkeeping notes

- **Rule (a) transparent-skip semantics** (C.1): skipped records are filtered
  out of the tail walk, so positions 115 and 117 both `api_level`-failing
  across a skipped 116 register as consecutive.
- **Rule (b) K denominator** (C.2): both numerator and denominator exclude
  `skipped_source_invalid` entirely.
- **Rule (c)**: content-error counter ignores skipped records per §7.8.
- **Rule (d)**: evaluated on the *just-completed* call's cost — skipped
  records have `actual_cost_usd=0.0` which cannot trigger.
- **Rule (e)**: cumulative sum over *ledger-written* costs only; skipped
  records contribute 0.

### Reason strings (verbatim scope lock)

| Rule | Reason string | Scope lock source |
|---|---|---|
| g | `"unexpected_skipped_source"` | §7.7 |
| a | `"consecutive_api_errors"` | §7.1 |
| b | `"error_rate_threshold"` | §7.2 |
| c | `"content_level_threshold"` | §7.3 |
| d | `"per_call_cost_exceeded"` | §7.4 |
| e | `"cumulative_cost_cap_exceeded"` | §7.5 |

---

## §8. Per-Call Execution Model

### Mainline (`_run_one_call`) for positions NOT in `STAGE2D_SKIPPED_POSITIONS`

```python
def _run_one_call(candidate, idx, backend, ledger, config) -> dict:
    # 1. BatchContext reconstruction
    batch_ctx = reconstruct_batch_context_at_position(
        batch_uuid=STAGE2D_BATCH_UUID,
        position=candidate.position,
        stage2d_artifacts_root=RAW_PAYLOAD_ROOT,  # same as 2b/2c — parallel discipline
    )

    # 2. Ledger pre-flight charge
    # Inherited per Verification A (Turn 3b): Stage 2c uses
    # D7B_STAGE2A_COST_CEILING_USD ($0.05) as the live pre-flight estimate,
    # not the rule-(d) abort threshold. Stage 2d inherits verbatim for
    # parallel-discipline symmetry across Stage 2a/2b/2c/2d fire scripts.
    if config.stub:
        estimated = 0.0
    else:
        from agents.critic.d7b_live import D7B_STAGE2A_COST_CEILING_USD
        estimated = D7B_STAGE2A_COST_CEILING_USD  # $0.05
    row_id = ledger.write_pending(
        batch_id=STAGE2D_BATCH_UUID,
        api_call_kind=config.api_call_kind_override,  # "d7b_critic_stub" | "d7b_critic_live"
        backend_kind="d7b_critic",
        call_role="critique",
        estimated_cost_usd=estimated,
    )

    # 3. D7a + D7b via run_critic
    critic_result = run_critic(
        source_record=candidate.source_record,
        batch_context=batch_ctx,
        d7b_backend=backend,
        enforce_reliability_fuse=False,   # Lock: stays False for Stage 2d per 2c parity
    )

    # 4. Ledger finalization
    ledger.finalize(row_id, actual_cost_usd=critic_result.actual_cost_usd, ...)

    # 5. Per-call record assembly
    return _assemble_per_call_record(
        candidate=candidate,
        call_index=idx,
        critic_result=critic_result,
        ledger_row_id=row_id,
    )
```

### Skipped-source branch for position 116 (per C.5 / Lock 1.5)

Two-layer structure: Layer A = Lock 1.5 mandated fields (verbatim values);
Layer B = Stage 2d fire-script envelope fields for per-call-record parity with
normal records. Layer B governing principle:

> *"Layer B envelope fields are limited to metadata required by aggregate
> builder paths that expect per-record alignment across all 200 positions;
> envelope fields must not imply a D7b request, response, prompt, ledger
> event, or critic computation."*

```python
def _synthesize_pos116_record(candidate, idx) -> dict:
    assert candidate.position == 116, "pos 116 synthesizer called on wrong position"

    # ─── Layer A: Lock 1.5 mandated top-level fields (verbatim) ───
    lock_15_fields = {
        "call_index": idx,
        "position": 116,
        "critic_status": "skipped_source_invalid",
        "d7b_call_attempted": False,
        "d7b_error_category": "source_invalid",
        "source_lifecycle_state": "rejected_complexity",
        "source_valid_status": "invalid_schema",
        "actual_cost_usd": 0.0,
        "input_tokens": 0,
        "output_tokens": 0,
        "skip_reason": (
            "source candidate is not pending_backtest and "
            "cannot be replayed by BatchContext reconstruction"
        ),
    }

    # ─── Layer B: Stage 2d fire-script envelope fields (6 total) ───
    # Per Layer B governing principle: envelope fields must not imply a
    # D7b request, response, prompt, ledger event, or critic computation.
    envelope_fields = {
        "stratum_id": candidate.stratum_id,
        "record_written_at_utc": iso_utc_now(),
        "firing_order": candidate.firing_order,
        "is_stage2b_overlap": 116 in STAGE2B_OVERLAP_POSITIONS,  # computed → False
        "is_deep_dive_candidate": False,   # pos 116 deterministically excluded (L12-05)
        "test_retest_tier": None,          # pos 116 not in Stage 2c set
    }

    return {**lock_15_fields, **envelope_fields}   # 11 + 6 = 17 keys
```

**Fields deliberately NOT included** (would imply a D7b call was made — violates
Lock 1.5):
- `ledger_row_id` (no ledger write — per C.7 revised)
- `d7b_request` / `d7b_response` (no call attempted)
- `critic_result` (no critic_result produced)
- `d7a_rule_scores` (no D7a run)

**Aggregate builder contract**: `build_aggregate_record()` must tolerate absent
fields in pos 116 record by treating them as `null` for any downstream
aggregation (error-rate numerator excludes pos 116 per §7.8; cost sum excludes
pos 116 automatically since `actual_cost_usd=0.0`). Ordered-list and by-call
contributions are specified in §10.3.

### Checkpoint logging (§10.3)

```python
def _log_checkpoint_if_due(idx, records, cumulative_cost):
    if idx % STAGE2D_CHECKPOINT_EVERY_N != 0:
        return
    non_skipped = [r for r in records if r["critic_status"] != "skipped_source_invalid"]
    K = len(non_skipped)
    errors = sum(1 for r in non_skipped if r["critic_status"] == "d7b_error")
    # Projected (from Lock 9 envelope)
    projected_cost_per_50 = 50 * 0.020   # $0.020 midpoint
    log.info(
        f"[stage2d] checkpoint idx={idx} K={K} errors={errors} "
        f"error_rate={errors/max(K,1):.3f} cumulative_cost=${cumulative_cost:.4f} "
        f"projected_cost_so_far=${(idx/50)*projected_cost_per_50:.4f}"
    )
```

Pure observability; never aborts.

---

## §9. Record Schemas

### §9.1 Normal per-call record (disk-verified from Stage 2c)

Stage 2c `build_per_call_record` produces 28 top-level keys. Stage 2d carries
forward verbatim with Stage-2d-specific mutations noted.

| Field | Source | Stage 2d change? |
|---|---|---|
| `request_timestamp_utc` | Stage 2a | Unchanged |
| `response_timestamp_utc` | Stage 2a | Unchanged |
| `wall_clock_seconds` | Stage 2a | Unchanged |
| `retry_count` | Stage 2a | Unchanged |
| `d7b_mode` | Stage 2a | Unchanged |
| `critic_result` | Stage 2a | Unchanged (full `CriticResult.to_dict()` payload) |
| `ledger_row` | Stage 2a | Unchanged shape; `api_call_kind` = `f"d7b_critic_{backend_label}"` with `backend_label ∈ {"stub", "live"}` |
| `raw_payload_paths` | Stage 2a | Unchanged |
| `cost` | Stage 2a | Unchanged (3 sub-fields: `estimated_usd`, `actual_usd`, `ratio`) |
| `leakage_audit_result` | Stage 2a | Unchanged |
| `forbidden_language_scan_result` | Stage 2a | Unchanged |
| `refusal_scan_result` | Stage 2a | Unchanged |
| `firing_order` | Stage 2b | Unchanged |
| `candidate_position` | Stage 2b | Unchanged |
| `candidate_theme` | Stage 2b | Unchanged |
| `candidate_hypothesis_hash` | Stage 2b | Unchanged |
| `pre_registered_label` | Stage 2b | Unchanged |
| `prior_factor_sets_count` | Stage 2b | Unchanged |
| `theme_hint_factor_count` | Stage 2b | Unchanged |
| `prompt_chars` | Stage 2b | Unchanged |
| `prompt_sha256` | Stage 2b | Unchanged |
| `call_index_in_sequence` | Stage 2b | Unchanged |
| `inter_call_sleep_elapsed_seconds` | Stage 2b | Unchanged |
| `is_stage2b_overlap` | Stage 2c | Semantics carried forward; `STAGE2B_OVERLAP_POSITIONS` unchanged |
| `critic_status` | Stage 2a (abort mirror) | Unchanged |
| `critic_error_signature` | Stage 2a (abort mirror) | Unchanged |
| `actual_cost_usd` | Stage 2a (abort mirror) | Unchanged |
| `d7b_error_category` | Stage 2c (abort mirror) | Unchanged |

**Stage 2d additions to normal per-call record** (per §10.3):

| Field | Source | Purpose |
|---|---|---|
| `stratum_id` | Stage 2d §10.3 | Stratum metadata for aggregate stratum breakdown |
| `is_deep_dive_candidate` | Stage 2d §10.3 | Boolean; True if position ∈ deep-dive candidates (read from `deep_dive_candidates.json`) |
| `test_retest_tier` | Stage 2d §10.3 | Tier 1 / Tier 2 / null per `test_retest_baselines.json` |

Total Stage 2d normal per-call record: **28 carried-forward + 3 new = 31
top-level keys**.

### §9.2 Synthetic pos 116 record (Layer A + Layer B)

**Layer A — Lock 1.5 mandated (11 fields, verbatim values)**:

| Field | Value | Type |
|---|---|---|
| `call_index` | (loop-supplied) | int |
| `position` | `116` | int |
| `critic_status` | `"skipped_source_invalid"` | str |
| `d7b_call_attempted` | `False` | bool |
| `d7b_error_category` | `"source_invalid"` | str |
| `source_lifecycle_state` | `"rejected_complexity"` | str |
| `source_valid_status` | `"invalid_schema"` | str |
| `actual_cost_usd` | `0.0` | float |
| `input_tokens` | `0` | int |
| `output_tokens` | `0` | int |
| `skip_reason` | (verbatim string per Lock 1.5) | str |

**Layer B — Stage 2d fire-script envelope fields (6 total; not in Lock 1.5,
required for operational parity)**:

| Field | Value for pos 116 | Rationale |
|---|---|---|
| `stratum_id` | `candidate.stratum_id` | Aggregate stratum breakdown |
| `record_written_at_utc` | ISO-8601 at synthesis | Audit-trail parity |
| `firing_order` | `candidate.firing_order` (=116) | Aggregate indexing |
| `is_stage2b_overlap` | `116 in STAGE2B_OVERLAP_POSITIONS` → `False` | Computed from constant (parity with §9.1) |
| `is_deep_dive_candidate` | `False` (pos 116 deterministically excluded from deep-dive per L12-05 gate) | Aggregate field parity |
| `test_retest_tier` | `None` (pos 116 not in Stage 2c set, thus not in test-retest baselines) | Aggregate field parity |

**Fields deliberately EXCLUDED** (would imply a D7b call was attempted —
violates Lock 1.5 "no D7b call" framing):
- `critic_result` (no result produced)
- `d7b_mode`, `retry_count` (no call made)
- `request_timestamp_utc`, `response_timestamp_utc`, `wall_clock_seconds`
  (no API round-trip)
- `ledger_row` (per C.7 revised — no ledger write)
- `raw_payload_paths` (no raw payload)
- `cost` dict (zero cost is captured in `actual_cost_usd` only)
- `prompt_chars`, `prompt_sha256` (no prompt rendered)
- `leakage_audit_result`, `forbidden_language_scan_result`,
  `refusal_scan_result` (no response to scan)
- `prior_factor_sets_count`, `theme_hint_factor_count` (no prompt assembly)
- `candidate_theme`, `candidate_hypothesis_hash`, `pre_registered_label`,
  `candidate_position` (redundant with `position`)
- `critic_error_signature` (no critic ran)
- `inter_call_sleep_elapsed_seconds` (no inter-call sleep relevant)
- `call_index_in_sequence` (redundant with `call_index`)

Total synthetic pos 116 record: **Layer A (11) + Layer B (6) = 17 top-level
keys**.

---

## §10. Aggregate Record Schema

### §10.1 Stage 2c aggregate record (disk-verified, 43 top-level keys)

Enumerated from `build_aggregate_record` (lines 990-1113):

| # | Field | Type | Stage 2d carry-forward? |
|---|---|---|---|
| 1 | `stage_label` | str | **Adapted** — `"d7_stage2d"` |
| 2 | `record_version` | str | Adapted — new version string |
| 3 | `batch_uuid` | str | As-is — `STAGE2D_BATCH_UUID` |
| 4 | `fire_script_command` | str | Adapted — `"run_d7_stage2d_batch.py"` name |
| 5 | `fire_timestamp_utc_start` | str | As-is |
| 6 | `fire_timestamp_utc_end` | str | As-is |
| 7 | `write_completed_at` (appended LAST) | str | As-is (Lock 11 invariant) |
| 8 | `d7b_prompt_template_sha256` | str | As-is (§10.4 anchor) |
| 9 | `selection_json_sha256` | str | **Adapted** — hashes `replay_candidates.json` |
| 10 | `expectations_file_sha256` | str | As-is |
| 11 | `selection_commit_timestamp_utc` | str \| null | As-is |
| 12 | `expectations_commit_timestamp_utc` | str \| null | As-is |
| 13 | `selection_tier` | int | As-is |
| 14 | `selection_warnings_count` | int | As-is |
| 15 | `sequence_aborted` | bool | As-is |
| 16 | `abort_reason` | str \| null | **Adapted** — new rule (g) string added to vocabulary |
| 17 | `abort_at_call_index` | int \| null | As-is |
| 18 | `completed_call_count` | int | As-is (200 if unaborted, incl. pos 116) |
| 19 | `total_wall_clock_seconds` | float | As-is |
| 20 | `inter_call_sleep_seconds` | int | As-is — inherit 5s |
| 21 | `total_actual_cost_usd` | float | As-is |
| 22 | `total_estimated_cost_usd` | float | As-is |
| 23 | `total_input_tokens` | int | As-is |
| 24 | `total_output_tokens` | int | As-is |
| 25 | `reasoning_lengths_in_call_order` | list[int] | As-is — pos 116 contributes `None` (see §10.3) |
| 26 | `actual_costs_in_call_order` | list[float] | As-is — pos 116 contributes `0.0` |
| 27 | `estimated_costs_in_call_order` | list[float] | As-is — pos 116 contributes `0.0` |
| 28 | `input_tokens_in_call_order` | list[int] | As-is — pos 116 contributes `0` |
| 29 | `output_tokens_in_call_order` | list[int] | As-is — pos 116 contributes `0` |
| 30 | `wall_clock_seconds_in_call_order` | list[float] | As-is — pos 116 contributes `None` |
| 31 | `critic_statuses_in_call_order` | list[str] | As-is — pos 116 contributes `"skipped_source_invalid"` |
| 32 | `d7b_error_categories_in_call_order` | list[str\|null] | As-is — pos 116 contributes `"source_invalid"` |
| 33 | `is_stage2b_overlap_in_call_order` | list[bool] | As-is — pos 116 contributes `False` |
| 34 | `d7a_scores_by_call` | dict[str, dict\|null] | As-is — pos 116 maps to `null` |
| 35 | `d7b_scores_by_call` | dict[str, dict\|null] | As-is — pos 116 maps to `null` |
| 36 | `agreement_divergence_reconciliation_by_call` | dict[str, dict] | As-is — pos 116 maps to null-value reconciliation |
| 37 | `theme_counts_in_sequence` | dict[str, int] | **Adapted** — computed over 200 candidates |
| 38 | `label_counts_in_sequence` | dict[str, int] | **Adapted** — computed over 200 candidates |
| 39 | `stage2b_overlap_count` | int | As-is (=5) |
| 40 | `stage2b_overlap_positions` | list[int] | As-is `[17,73,74,97,138]` |
| 41 | `stage2b_overlap_completed_count` | int | As-is |
| 42 | `svr_by_label` | dict | As-is |
| 43 | `per_call_records` | list[dict] | As-is — list of 200 (199 normal + 1 synthetic pos 116) |

**Conditional fields** (present only on selection-JSON drift detected by HG20):

- `selection_json_sha256_end: str`
- `hg20_drift_detected: bool`

These are excluded from the 43-key base enumeration above. With drift, the
aggregate has 43 + 2 = 45 base Stage 2c keys (or 53 + 2 = 55 Stage 2d keys).

### §10.2 Stage 2d additions to aggregate record (per Lock 10.3)

| Field | Type | Purpose |
|---|---|---|
| `critic_status_counts` | `dict[str, int]` with exactly 3 keys `{"ok", "d7b_error", "skipped_source_invalid"}` | Three-counter status per §10.3 |
| `stratum_breakdown` | `dict[str, dict]` indexed by stratum_id; each entry has `count`, `error_count`, `error_rate` (excluding skipped) | Post-fire theme-level stats per §10.3 |
| `deep_dive_candidates_sha256` | str | SHA-256 of `deep_dive_candidates.json` at startup |
| `test_retest_baselines_sha256` | str | SHA-256 of `test_retest_baselines.json` at startup |
| `label_universe_analysis_sha256` | str | SHA-256 of `label_universe_analysis.json` at startup |
| `checkpoint_log` | `list[dict]` | Projected-vs-actual at idx=50,100,150 per §10.3 |
| `stage2c_archive_sha256_by_file` | `dict[str, str]` \| null | live-mode only; per-file SHA of `stage2c_archive/` contents for audit trail; null in stub |
| `stage2d_skipped_positions` | list[int] | = `[116]`; explicit for self-documentation |
| `stage2d_live_d7b_call_n` | int | = 199; redundant with completed_call_count - skip_count but explicit |
| `stage2d_source_n` | int | = 200 |

**Stage 2d aggregate total**: 43 carry-forward + 10 additions = **53 top-level
keys (base)**. With HG20 drift conditional: **55 keys**.

### §10.3 Pos 116 contribution to ordered-list and by-call fields

Explicit table for every list/dict field's pos-116 contribution (avoiding
ambiguity in aggregate builder implementation):

| Aggregate field | Pos 116 value | Rationale |
|---|---|---|
| `reasoning_lengths_in_call_order[115]` (0-indexed) | `None` | No reasoning emitted |
| `actual_costs_in_call_order[115]` | `0.0` | Lock 1.5 mandate |
| `estimated_costs_in_call_order[115]` | `0.0` | No ledger row → no estimate |
| `input_tokens_in_call_order[115]` | `0` | Lock 1.5 mandate |
| `output_tokens_in_call_order[115]` | `0` | Lock 1.5 mandate |
| `wall_clock_seconds_in_call_order[115]` | `None` | No API round-trip |
| `critic_statuses_in_call_order[115]` | `"skipped_source_invalid"` | Lock 1.5 mandate |
| `d7b_error_categories_in_call_order[115]` | `"source_invalid"` | Lock 1.5 mandate |
| `is_stage2b_overlap_in_call_order[115]` | `False` | Computed: 116 ∉ overlap set |
| `d7a_scores_by_call["116"]` | `null` | No D7a ran |
| `d7b_scores_by_call["116"]` | `null` | No D7b call |
| `agreement_divergence_reconciliation_by_call["116"]` | `{"pre_registered_label": null, "d7b_structural_variant_risk": null, "observed_consistent_with_label": null, "rationale": "skipped_source_invalid"}` | Structural placeholder |

### §10.4 HG20 — Input (selection JSON) drift guard

Stage 2c's HG20 (per `run_d7_stage2c_batch.py:1527-1536`) re-hashes the **input**
`replay_candidates.json` at sequence end and compares against the startup hash.
This detects mutation of the selection artifact during the fire wall-clock
window.

**Behavior on drift**: WARNING logged to stderr (non-fatal); aggregate record
augmented with two additional fields:

- `selection_json_sha256_end: str` — the end-of-sequence hash
- `hg20_drift_detected: bool = True`

Both fields are **absent** from the aggregate on non-drift (normal case).

**Stage 2d carries HG20 verbatim** targeting `replay_candidates.json`. Optional
extension for Stage 2d: re-hash `test_retest_baselines.json`,
`deep_dive_candidates.json`, and `label_universe_analysis.json` similarly and
log any drift. Authoring-time decision.

**Note**: HG20 is an input-drift guard, not an output-integrity guard.
Stage 2c has no `self_sha256_at_write` field; there is no post-serialization
rehash of the aggregate itself before write. The `write_completed_at` LAST-write
invariant (Lock 11) is the sole aggregate-write ordering discipline.

### §10.5 Abort-reason vocabulary for Stage 2d

Union of Stage 2c's Lock 7 vocabulary + new rule (g) reason. `abort_reason`
field MUST be `None` or a member of this set. Enforce via aggregate builder
assertion.

```python
STAGE2D_ABORT_REASON_VOCAB = frozenset({
    # Inherited from Stage 2c Lock 7
    "consecutive_api_errors",
    "error_rate_threshold",
    "content_level_threshold",
    "per_call_cost_exceeded",
    "cumulative_cost_cap_exceeded",
    # Stage 2d new (Lock 7.7)
    "unexpected_skipped_source",
})
```

HG6b prompt-template drift raises `Stage2dStartupError` (exit 1, aggregate
never written), so template-mutation is **not** an `abort_reason` member —
its handling lives in §6 startup gate context and §8 mid-loop re-check.

---

## §11. Stub / Live Path Architecture

### §11.0 Layer B governing principle

> *"Layer B envelope fields are limited to metadata required by aggregate
> builder paths that expect per-record alignment across all 200 positions;
> envelope fields must not imply a D7b request, response, prompt, ledger
> event, or critic computation."*

### §11.1 Path routing table

| Concern | Stub (`--stub`) | Live (`--confirm-live`) |
|---|---|---|
| Aggregate record path | `dryrun_payloads/dryrun_stage2d/stage2d_aggregate_record.json` | `raw_payloads/batch_5cf76668-.../critic/stage2d_aggregate_record.json` |
| Ledger path | `dryrun_payloads/dryrun_stage2d/ledger_dryrun.db` | `agents/spend_ledger.db` |
| Raw payload dir | `dryrun_payloads/dryrun_stage2d/raw_payloads/` | `raw_payloads/batch_5cf76668-.../critic/` |
| Per-call prompt path | `{raw_payload_dir}/call_{NNNN}_prompt.txt` | `{raw_payload_dir}/call_{NNNN}_prompt.txt` |
| Backend | `StubD7bBackend()` | `LiveSonnetD7bBackend(...)` |
| `api_call_kind` | `"d7b_critic_stub"` | `"d7b_critic_live"` |
| `backend_kind` (ledger enum) | `"d7b_critic"` | `"d7b_critic"` |
| Pre-flight estimate | `0.0` | `D7B_STAGE2A_COST_CEILING_USD` ($0.05) — inherited constant used as parallel-discipline anchor across Stage 2a/2b/2c/2d fire scripts; NOT the rule-(d) abort threshold ($0.08) |
| Gate 10 (partial prior run) | Skipped | Active |
| Gate 11 (Stage 2c archival) | Skipped | Active (hard-fail) |
| Stage 2c archive SHA field | `null` | Populated dict |

### §11.2 `_assert_stub_isolation` contract

Stub mode MUST NOT write to:
- `raw_payloads/` (any subdirectory)
- `agents/spend_ledger.db`
- Any production path

Enforcement: at `run_stage2d()` entry, if `config.stub=True`,
`_assert_stub_isolation(config)` asserts:
- `config.aggregate_output_path` starts with `dryrun_payloads/dryrun_stage2d/`
- `config.ledger_path` starts with `dryrun_payloads/dryrun_stage2d/`
- `config.raw_payload_root` starts with `dryrun_payloads/dryrun_stage2d/`

Any mismatch raises `Stage2dStartupError("stub isolation violated: <detail>")`
→ exit 1.

### §11.3 Ledger-row vs record-count discrepancy (codified)

**Explicit invariant** for Stage 2d:

> *"The number of `per_call_records` in the aggregate MUST equal 200 on
> non-abort completion (199 live-D7b records + 1 synthetic pos 116 record per
> Lock 1.5). The number of ledger rows for `batch_id=STAGE2D_BATCH_UUID` with
> `backend_kind="d7b_critic"` MUST be exactly 199 on non-abort completion. The
> 200-vs-199 delta corresponds to position 116, which per Lock 1.5 and the
> revised C.7 ruling produces a per-call record but no ledger row. This is a
> feature, not an inconsistency."*

Test assertion at aggregate build time (non-abort path):

```python
assert len(per_call_records) == 200, "Lock 1.6: 200-record invariant"
ledger_rows = ledger.count_rows(batch_id=STAGE2D_BATCH_UUID, backend_kind="d7b_critic")
assert ledger_rows == 199, "Lock 1.5: pos 116 is not ledger-tracked"
```

---

## §12. Output Artifact Locations (per Lock 10.2a)

### §12.1 Live-mode artifacts (under `raw_payloads/batch_5cf76668-.../critic/`)

| Artifact | Path |
|---|---|
| Aggregate record | `stage2d_aggregate_record.json` |
| Per-call prompts (199) | `call_{NNNN}_prompt.txt` for N ∈ {001..115, 117..200} |
| Per-call responses (199) | `call_{NNNN}_response.json` for same N set |
| Per-call critic results (199) | `call_{NNNN}_critic_result.json` for same N set |
| Per-call tracebacks (error subset) | `call_{NNNN}_traceback.txt` for any position with `critic_status="d7b_error"` |
| Startup audit log | `stage2d_startup_audit.json` |
| Stage 2c archive (read-only input) | `stage2c_archive/` (inventoried by Gate 11) |

### §12.2 Stub-mode artifacts (under `dryrun_payloads/dryrun_stage2d/`)

Same structure, rooted at `dryrun_payloads/dryrun_stage2d/raw_payloads/`. Plus
stub-only:

- `ledger_dryrun.db`

### §12.3 Pos 116 artifact policy

No `call_0116_prompt.txt`, `call_0116_response.json`, or
`call_0116_critic_result.json` is written. Pos 116's existence is captured
solely in the aggregate record's `per_call_records[115]` entry (synthetic
record). Rationale: Lock 1.5 "no D7b call attempted" → no raw payload to
persist.

---

## §13. `stage2d_self_check.py` Integration

### §13.1 Subprocess invocation contract

Gate 1 invokes the validator as an independent subprocess. Full spec:

```python
def _gate_self_check_subprocess(config: Stage2dConfig) -> None:
    cmd = [sys.executable, str(STAGE2D_SELF_CHECK_SCRIPT)]
    result = subprocess.run(
        cmd,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=120,
    )
    audit_entry = {
        "gate": "self_check_subprocess",
        "cmd": cmd,
        "exit_code": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "invoked_at_utc": iso_utc_now(),
    }
    config.startup_audit.append(audit_entry)

    if result.returncode != 0:
        raise Stage2dStartupError(
            f"HG_SELF_CHECK: stage2d_self_check.py exited {result.returncode}.\n"
            f"Required: 28 PASS + 0 WARN + 0 FAIL, exit 0.\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )
```

### §13.2 Exit-code handling

| Exit code | Validator meaning | Fire script action |
|---|---|---|
| 0 | 28 PASS + 0 FAIL (WARN tolerated if explicitly noted) | Proceed to Gate 2 |
| 1 | Any FAIL, or harness error | `Stage2dStartupError` → exit 1 |
| 2 | Validator internal error (parsing, I/O) | `Stage2dStartupError` → exit 1 |
| other | Unexpected | `Stage2dStartupError` → exit 1 |

**WARN handling**: validator may return 0 with WARN entries (e.g.,
environmental note). Fire script treats exit-0 as authoritative; WARN content
is captured in the audit log for human review but does not block fire.

**Baseline note**: at E5 seal commit `5d9f4d4`, `stage2d_self_check.py`
produced `28 PASS + 0 WARN + 0 FAIL` (exit 0). Any WARN emitted at fire time
indicates environmental change since E5 seal and should be investigated via
the captured audit log before proceeding to live fire.

### §13.3 Audit trail integration

`config.startup_audit` (list of dict entries, one per gate) is written to
`stage2d_startup_audit.json` as part of aggregate record finalization,
alongside the aggregate. Contents include:

- Gate 1: self_check full stdout/stderr
- Gate 2-11: per-gate result + any captured anchor values
- Fire-time environment: git HEAD, python version, OS

This audit file is read-only post-write; signed off alongside the aggregate
record.

---

## §14. Known Non-Goals

Explicit scope boundaries; out-of-scope for this spec and for
`run_d7_stage2d_batch.py`:

1. **Semantic evaluation of D7b outputs** — fire script produces records;
   acceptance notebook (`D7 Stage 2d acceptance notebook.ipynb`) performs
   semantic verification post-fire.
2. **Sign-off adjudication** — fire script exit 0 does not imply sign-off;
   sign-off is a separate advisor review cycle over the acceptance notebook's
   findings.
3. **Stub fixture isolation retrofit** (Implementation Plan §10.1 deferral) —
   Stage 2b/2c/2d stub-fixture isolation symmetry is a **pre-D8** task with
   its own scope lock v2.1. Not in Stage 2d fire script.
4. **Reliability fuse enforcement** (`enforce_reliability_fuse=False`) —
   Stage 2d runs with fuse disabled, matching Stage 2c's Stage 2a/2b parity
   convention. Stage 2e or later may flip this.
5. **Resume / partial-fire recovery** — aborts are terminal. No `--resume`
   flag. Any aborted fire requires human adjudication and either full re-fire
   or explicit partial acceptance (treated as Stage 2e scoping).
6. **Prompt template modification** — template is frozen at fire time
   (§10.4); any wording change requires scope-lock v3 + new expectations
   commit + new fire. Not a fire-script responsibility.
7. **New CLI flags** — `--stub | --confirm-live` is the full CLI surface. No
   `--batch-id`, `--start-pos`, `--end-pos`, `--budget-cap`, `--output-root`.
   Future flags require new scope-lock revision.
8. **Acceptance notebook authoring** — exists separately
   (`docs/test_notebooks/D7 Stage 2d acceptance notebook.ipynb`, committed
   in E5 follow-up); not produced by this fire script.

---

## §15. Open Items / Deferred

| # | Item | Status | Resolution path |
|---|---|---|---|
| 1 | `stage2c_archive/` directory does not yet exist on disk | **Pre-fire operator action required** | Charlie materializes archive (see §16 checklist) before invoking `--confirm-live` |
| 2 | Stub fixture isolation retrofit across 2b/2c/2d | Deferred to pre-D8 | Separate scope lock v2.1 |
| 3 | Exact `stage2d_startup_audit.json` schema | Draft-level in §13.3 | Refined during fire script authoring; not spec-blocking |
| 4 | Acceptance notebook post-fire execution mechanics | Out-of-scope for this spec | Notebook already committed; run independently post-fire |
| 5 | **Confirmed** scope-lock §9.2 typo: line 579 reads `(99 calls average)` — should be `(199 calls average)` per §1.1 / §10.2 source counts. Disk-verified 2026-04-20. | Scope-lock-level correction | Flag to Charlie as a standalone mini-amendment; not design-spec-impacting |
| 6 | `STAGE2D_INTER_CALL_SLEEP_SECONDS` value | Inherited from Stage 2c (=5) | Confirm at authoring time; no reason to diverge |

---

## §16. Pre-Fire Action Checklist

**MUST be completed by Charlie before invoking
`python scripts/run_d7_stage2d_batch.py --confirm-live`.** Ordered; each item
is a hard precondition for the next.

### Step 1 — Stage 2c archival (Lock 10.5)

```bash
# Create archive directory
mkdir -p raw_payloads/batch_5cf76668-47d1-48d7-bd90-db06d31982ed/critic/stage2c_archive/

# Copy Stage 2c 20-position artifacts into archive
# Positions: 17, 22, 27, 32, 62, 72, 73, 74, 77, 83, 97, 102, 107, 112, 117, 138, 143, 147, 152, 162
for pos in 0017 0022 0027 0032 0062 0072 0073 0074 0077 0083 0097 0102 0107 0112 0117 0138 0143 0147 0152 0162; do
    cp raw_payloads/batch_5cf76668-.../critic/call_${pos}_prompt.txt        .../stage2c_archive/
    cp raw_payloads/batch_5cf76668-.../critic/call_${pos}_response.json     .../stage2c_archive/
    cp raw_payloads/batch_5cf76668-.../critic/call_${pos}_critic_result.json .../stage2c_archive/
done
```

**Verify**: `ls stage2c_archive/ | wc -l` ≥ 60 (3 files × 20 positions; plus
optional tracebacks).

### Step 2 — Stub dry-run

```bash
python scripts/run_d7_stage2d_batch.py --stub
```

**Success criteria**:

- Exit 0
- `dryrun_payloads/dryrun_stage2d/stage2d_aggregate_record.json` exists
- Aggregate has `completed_call_count == 200`
- Aggregate has `sequence_aborted == False`
- `critic_status_counts == {"ok": 199, "d7b_error": 0, "skipped_source_invalid": 1}`
- No writes to `raw_payloads/`, no writes to `agents/spend_ledger.db`

**Stub determinism**: `StubD7bBackend` (disk-verified
`agents/critic/d7b_stub.py`) is always-success, always-deterministic (fixed
scores `{0.5, 0.5, 0.5}`, no error injection).
`critic_status_counts == {"ok": 199, "d7b_error": 0, "skipped_source_invalid": 1}`
is the only valid outcome in stub mode; any deviation indicates either (a)
stub implementation drift since Stage 1, (b) pos 116 synthesizer malfunction,
or (c) isolation breach.

### Step 3 — Stub ledger reconciliation

```bash
sqlite3 dryrun_payloads/dryrun_stage2d/ledger_dryrun.db \
    "SELECT COUNT(*) FROM ledger WHERE batch_id='5cf76668-...' AND backend_kind='d7b_critic';"
```

**Expected**: 199 rows (not 200 — per C.7 revised ruling, pos 116 produces no
ledger row).

### Step 4 — Commit state verification

```bash
git log --oneline -5
git status
```

**Expected**:

- 3 E5 commits at HEAD unchanged (Commit A `4df9cee`, Commit B `5d9f4d4`,
  Commit C `685d552`)
- Working tree clean
- No uncommitted changes

### Step 5 — Self-check final pass

```bash
python scripts/stage2d_self_check.py
echo "Exit: $?"
```

**Expected**: Exit 0, "28 PASS + 0 WARN + 0 FAIL" in stdout.

### Step 6 — Environment setup

```bash
# Verify API key
test -n "$ANTHROPIC_API_KEY" && echo "OK" || echo "MISSING"

# Verify Python env
python -c "import anthropic; print(anthropic.__version__)"
```

### Step 7 — Invoke live fire

Only if Steps 1-6 all pass:

```bash
python scripts/run_d7_stage2d_batch.py --confirm-live
```

**Any failure in Steps 1-6 blocks live fire.** Gate 11 (and other startup
gates) will also reject, but the pre-fire checklist exists to catch issues
earlier and with better error context than gate failure.

---

## Authoritative Count Summary (v2)

| Artifact | Count |
|---|---|
| Stage 2d aggregate — base keys | 53 |
| Stage 2d aggregate — with HG20 drift conditional | 55 |
| Stage 2d normal per-call record | 31 |
| Stage 2d synthetic pos 116 record | 17 (Layer A 11 + Layer B 6) |
| Abort-reason vocabulary members | 6 |
| Startup gates | 11 (9 both + 2 live-only) |

---

## C-Rulings + Advisor Precision Items Encoded

- **C.1** (rule (a) transparent): §7
- **C.2** (rule (b) K floor non-skipped): §7
- **C.3** (rule ordering g→a→b→c→d→e): §7
- **C.4** (self_check subprocess): §6 Gate 1, §13
- **C.5** (Lock 1.5 + Layer B): §8, §9.2
- **C.6** (stage2c_archive hard-fail): §6 Gate 11, §16
- **C.7 revised** (no ledger row for pos 116): §8, §11.3, §16 Step 3
- **C.8** (full lock carry-forward): §4
- Advisor Precision 1 (`estimated_cost_usd` = `D7B_STAGE2A_COST_CEILING_USD`,
  not per-call ceiling): §8, §11.1
- Advisor Precision 2 (`is_stage2b_overlap` compute-from-constant): §9.2
  Layer B, §8 pseudocode
- Advisor Precision 3 (Option B — Layer B = 6 fields): §9.2, §10.3
- Turn 5 Fix 5 (HG20 is input-drift guard, not output-integrity): §10.4
- Turn 5 Fix 6 (6-member abort-reason vocabulary): §10.5

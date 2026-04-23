"""Tests for scripts/run_d7_stage2d_batch.py — D7 Stage 2d fire script.

Covers the 3e.2 minimum coverage set:

    - ``_synthesize_pos116_record`` shape + Lock 1.5 Layer A/B fields
    - ``_build_checkpoint_log`` at empty / partial / full-200 slices
    - ``_compute_stage2c_archive_sha256_by_file`` stub (no FS touch) and
      live (real synthetic 60-file tempdir archive)
    - ``build_aggregate_record`` non-drift (51 keys) + drift (53 keys)
      with on-disk verification
    - HG20 coupled-kwargs guards (symmetric AssertionError)
    - ``should_abort`` Lock 7 rules (a)(b)(c)(d)(e) + skipped-source
      transparency
    - ``Stage2dStartupError`` HG1b reload drift raise (3e.1 conversion)
    - Stub-run integration smoke (subprocess, exit 0, 51-key aggregate)

All tests use real tempdir files and real builder invocations per the
3d.1/3d.3 verification-elevation discipline. No mocking of filesystem
or builder internals.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

import pytest

import scripts.run_d7_stage2d_batch as stage2d


REPO_ROOT = Path(__file__).resolve().parent.parent
DRYRUN_ROOT = REPO_ROOT / "dryrun_payloads" / "dryrun_stage2d"
STUB_AGGREGATE_PATH = DRYRUN_ROOT / "stage2d_aggregate_record.json"
REPLAY_CANDIDATES_PATH = REPO_ROOT / "docs/d7_stage2d/replay_candidates.json"


# ---------------------------------------------------------------------------
# Fixtures & helpers
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def stub_artifact() -> dict:
    """Ensure the canonical stub aggregate exists, then return it.

    Runs ``--stub`` once per session if the artifact is missing or
    empty. Downstream tests re-use the produced ``per_call_records``
    and ``candidates`` as realistic fixture data.
    """
    if not STUB_AGGREGATE_PATH.exists() or STUB_AGGREGATE_PATH.stat().st_size == 0:
        result = subprocess.run(
            [sys.executable, "scripts/run_d7_stage2d_batch.py", "--stub"],
            capture_output=True, text=True, cwd=REPO_ROOT,
        )
        assert result.returncode == 0, (
            f"stub run failed during fixture setup: {result.stderr}"
        )
    return json.loads(STUB_AGGREGATE_PATH.read_text(encoding="utf-8"))


@pytest.fixture
def replay_candidates() -> list[dict]:
    """The 200 ratified Stage 2d replay candidates (from on-disk JSON)."""
    payload = json.loads(REPLAY_CANDIDATES_PATH.read_text(encoding="utf-8"))
    return payload["candidates"]


def _make_stub_config(tmp_path: Path) -> stage2d.Stage2dConfig:
    """Build a Stage2dConfig redirected to tmp_path for stub-mode unit tests.

    Uses the project's own factory so defaults stay in sync, then
    overrides the output paths to avoid clobbering the canonical
    ``dryrun_payloads/dryrun_stage2d/`` artifact.
    """
    config = stage2d.build_stage2d_config(confirm_live=False, stub=True)
    config.aggregate_record_path = tmp_path / "stage2d_aggregate_record.json"
    config.startup_audit_path = tmp_path / "stage2d_startup_audit.json"
    config.raw_payload_root = tmp_path / "raw_payloads"
    config.ledger_path = tmp_path / "ledger_dryrun.db"
    # Deterministic clock for on-disk equality assertions.
    config.now_iso_fn = lambda: "2026-04-23T12:00:00Z"
    return config


def _make_live_config_pointing_at(
    tmp_path: Path,
    raw_payload_root: Path,
) -> stage2d.Stage2dConfig:
    """Construct a live-mode Stage2dConfig for the archive-helper live test.

    Not used to *run* the full fire path — only so
    ``_compute_stage2c_archive_sha256_by_file`` sees ``mode == "live"``
    and a valid ``raw_payload_root``.
    """
    config = stage2d.build_stage2d_config(confirm_live=False, stub=True)
    # Directly mutate to live-mode shape for the helper path.
    config.mode = "live"
    config.stub = False
    config.confirm_live = True
    config.raw_payload_root = raw_payload_root
    config.aggregate_record_path = tmp_path / "aggregate_live.json"
    return config


def _persisted_record(
    *,
    firing_order: int = 1,
    critic_status: str = "ok",
    d7b_error_category: str | None = None,
    actual_cost_usd: float = 0.02,
    estimated_usd: float = 0.03,
    position: int | None = None,
) -> dict:
    """Minimal per-call record dict for should_abort / checkpoint unit tests.

    ``position`` is required on skipped records (§7.7 rule (g) reads it
    to decide whether the skip is at the ratified pos 116 slot).
    """
    rec: dict = {
        "firing_order": firing_order,
        "critic_status": critic_status,
        "actual_cost_usd": actual_cost_usd,
        "cost": {"estimated_usd": estimated_usd},
    }
    if d7b_error_category is not None:
        rec["d7b_error_category"] = d7b_error_category
    if position is not None:
        rec["position"] = position
    return rec


def _json_roundtrip(d: dict) -> dict:
    """Mirror atomic_write_json's lossy JSON conversions so in-memory vs
    on-disk comparisons can be equality-checked.

    Non-obvious failure mode this normalizes away: Python dicts whose keys
    include ``None`` (e.g. ``theme_counts_in_sequence`` / any by-theme
    tally that bucketed an untagged entry under ``None``) serialize via
    ``json.dumps`` to string ``"null"`` keys — so round-tripping the
    written file back through ``json.loads`` does NOT yield a dict equal
    to the original in-memory aggregate. Tuples → lists is the other
    well-known lossy conversion. Using this helper in ``==`` assertions
    isolates Stage-2d-specific invariants from JSON's lossy encoding.
    """
    return json.loads(json.dumps(d))


# ---------------------------------------------------------------------------
# Item 1 — _synthesize_pos116_record (Lock 1.5 + Layer B)
# ---------------------------------------------------------------------------


def test_synthesize_pos116_record_has_17_keys(replay_candidates):
    pos116 = replay_candidates[115]
    assert pos116["position"] == 116  # guard against replay file drift
    record = stage2d._synthesize_pos116_record(
        candidate=pos116,
        call_index=116,
        iso_now="2026-04-23T12:00:00Z",
    )
    assert len(record) == 17
    assert record["position"] == 116
    assert record["call_index"] == 116
    assert record["critic_status"] == "skipped_source_invalid"
    assert record["d7b_call_attempted"] is False
    assert record["d7b_error_category"] == "source_invalid"
    assert record["source_lifecycle_state"] == "rejected_complexity"
    assert record["actual_cost_usd"] == 0.0
    assert record["is_stage2b_overlap"] is False
    assert record["is_deep_dive_candidate"] is False
    assert record["test_retest_tier"] is None


def test_synthesize_pos116_record_rejects_non_116_position(replay_candidates):
    wrong = deepcopy(replay_candidates[115])
    wrong["position"] = 115
    with pytest.raises(AssertionError, match="expected 116"):
        stage2d._synthesize_pos116_record(
            candidate=wrong, call_index=115, iso_now="2026-04-23T12:00:00Z",
        )


# ---------------------------------------------------------------------------
# Item 2 — _build_checkpoint_log
# ---------------------------------------------------------------------------


def test_build_checkpoint_log_empty_list():
    assert stage2d._build_checkpoint_log([]) == []


def test_build_checkpoint_log_below_first_trigger(stub_artifact):
    records = stub_artifact["per_call_records"][:49]
    assert stage2d._build_checkpoint_log(records) == []


def test_build_checkpoint_log_partial_149_yields_two_entries(stub_artifact):
    records = stub_artifact["per_call_records"][:149]
    log = stage2d._build_checkpoint_log(records)
    assert [e["call_index"] for e in log] == [50, 100]
    # Checkpoint entry shape — 10 fields per §10.3 amendment.
    assert len(log[0]) == 10
    assert log[0]["completed_call_count"] == 50


def test_build_checkpoint_log_full_200_yields_three_entries(stub_artifact):
    records = stub_artifact["per_call_records"]
    log = stage2d._build_checkpoint_log(records)
    assert [e["call_index"] for e in log] == [50, 100, 150]
    # idx=200 is NOT a checkpoint trigger — aggregate totals capture final state.
    assert all(e["call_index"] in (50, 100, 150) for e in log)


# ---------------------------------------------------------------------------
# Item 3/4 — _compute_stage2c_archive_sha256_by_file
# ---------------------------------------------------------------------------


def test_archive_helper_stub_returns_none_with_no_fs_touch(tmp_path):
    config = _make_stub_config(tmp_path)
    config.raw_payload_root = tmp_path / "does_not_exist_ever"
    assert stage2d._compute_stage2c_archive_sha256_by_file(config) is None
    # Helper must not create the directory.
    assert not (tmp_path / "does_not_exist_ever").exists()


def test_archive_helper_live_returns_sorted_sha_dict(tmp_path):
    """Live path against a hermetic synthetic 60-file archive."""
    archive_dir = (
        tmp_path
        / stage2d.STAGE2D_BATCH_DIR_NAME
        / stage2d.STAGE2C_ARCHIVE_RELATIVE
    )
    archive_dir.mkdir(parents=True)
    for pos in stage2d.STAGE2C_ARCHIVE_POSITIONS:
        for kind in ("prompt.txt", "response.json", "critic_result.json"):
            content = f"synthetic {pos} {kind}\n".encode()
            (archive_dir / f"call_{pos:04d}_{kind}").write_bytes(content)

    config = _make_live_config_pointing_at(tmp_path, tmp_path)
    result = stage2d._compute_stage2c_archive_sha256_by_file(config)
    assert result is not None
    assert len(result) == 60
    keys = list(result.keys())
    assert keys == sorted(keys), "must be sorted by basename"
    # Sentinel: pos 17 sorts first, pos 162 last.
    assert keys[0].startswith("call_0017_")
    assert keys[-1].startswith("call_0162_")
    # SHA-256 is 64 hex chars and matches the on-disk bytes.
    sample = archive_dir / keys[0]
    expected = hashlib.sha256(sample.read_bytes()).hexdigest()
    assert result[keys[0]] == expected


# ---------------------------------------------------------------------------
# Items 5-6 — build_aggregate_record non-drift / drift (real invocation)
# ---------------------------------------------------------------------------


def _builder_kwargs_from_stub(
    stub_artifact: dict,
    replay_candidates: list[dict],
    config: stage2d.Stage2dConfig,
) -> dict:
    """Shared keyword set for ``build_aggregate_record`` invocations."""
    deep_dive = json.loads(
        (REPO_ROOT / "docs/d7_stage2d/deep_dive_candidates.json").read_text(
            encoding="utf-8",
        )
    )
    # Backfill SHA/timestamp fields the startup gates would normally set.
    config.prompt_template_sha = stub_artifact.get(
        "prompt_template_sha256"
    ) or "0" * 64
    config.replay_candidates_sha = stub_artifact.get(
        "selection_json_sha256_start"
    ) or "0" * 64
    config.expectations_file_sha256 = stub_artifact.get(
        "expectations_file_sha256"
    ) or "0" * 64
    config.selection_commit_timestamp_utc = stub_artifact.get(
        "selection_commit_timestamp_utc"
    ) or "2026-04-01T00:00:00Z"
    config.expectations_commit_timestamp_utc = stub_artifact.get(
        "expectations_commit_timestamp_utc"
    ) or "2026-04-01T00:00:00Z"
    config.deep_dive_candidates_sha256 = stub_artifact.get(
        "deep_dive_candidates_sha256"
    ) or "0" * 64
    config.test_retest_baselines_sha256 = stub_artifact.get(
        "test_retest_baselines_sha256"
    ) or "0" * 64
    config.label_universe_analysis_sha256 = stub_artifact.get(
        "label_universe_analysis_sha256"
    ) or "0" * 64
    config.startup_audit = stub_artifact.get("startup_audit") or []
    config.startup_completed_at_utc = (
        stub_artifact.get("startup_completed_at_utc") or "2026-04-23T11:59:00Z"
    )
    return {
        "config": config,
        "candidates": replay_candidates,
        "per_call_records": stub_artifact["per_call_records"],
        "fire_timestamp_utc_start": "2026-04-23T11:59:00Z",
        "fire_timestamp_utc_end": "2026-04-23T12:00:00Z",
        "sequence_aborted": False,
        "abort_reason": None,
        "abort_at_call_index": None,
        "total_wall_clock_seconds": 60.0,
        "fire_script_command": "python scripts/run_d7_stage2d_batch.py --stub",
        "deep_dive_data": deep_dive,
    }


def test_build_aggregate_record_non_drift_writes_51_keys_on_disk(
    tmp_path, stub_artifact, replay_candidates,
):
    config = _make_stub_config(tmp_path)
    kwargs = _builder_kwargs_from_stub(stub_artifact, replay_candidates, config)
    agg = stage2d.build_aggregate_record(
        **kwargs,
        hg20_drift_detected=False,
        selection_json_sha256_end=None,
    )

    # Returned dict matches 51-key invariant with write_completed_at last.
    assert len(agg) == 51
    assert list(agg.keys())[-1] == "write_completed_at"
    assert "hg20_drift_detected" not in agg
    assert "selection_json_sha256_end" not in agg
    assert agg["stage2c_archive_sha256_by_file"] is None  # stub mode

    # On-disk file matches the returned dict (after the lossy JSON
    # round-trip that ``atomic_write_json`` performs: None dict keys
    # serialize to the string "null", tuples to lists, etc.).
    assert config.aggregate_record_path.exists()
    on_disk = json.loads(config.aggregate_record_path.read_text(encoding="utf-8"))
    assert list(on_disk.keys()) == list(agg.keys())
    assert on_disk == _json_roundtrip(agg)


def test_build_aggregate_record_drift_writes_53_keys_on_disk(
    tmp_path, stub_artifact, replay_candidates,
):
    config = _make_stub_config(tmp_path)
    kwargs = _builder_kwargs_from_stub(stub_artifact, replay_candidates, config)
    drift_sha = "deadbeef" * 8
    agg = stage2d.build_aggregate_record(
        **kwargs,
        hg20_drift_detected=True,
        selection_json_sha256_end=drift_sha,
    )

    assert len(agg) == 53
    assert list(agg.keys())[-1] == "write_completed_at"
    assert agg["hg20_drift_detected"] is True
    assert agg["selection_json_sha256_end"] == drift_sha

    # Each HG20 field appears exactly once.
    keys = list(agg.keys())
    assert keys.count("hg20_drift_detected") == 1
    assert keys.count("selection_json_sha256_end") == 1

    on_disk = json.loads(config.aggregate_record_path.read_text(encoding="utf-8"))
    assert list(on_disk.keys()) == list(agg.keys())
    assert on_disk == _json_roundtrip(agg)


# ---------------------------------------------------------------------------
# Item 7 — HG20 coupled-kwargs guards
# ---------------------------------------------------------------------------


def test_build_aggregate_record_drift_without_sha_raises(
    tmp_path, stub_artifact, replay_candidates,
):
    config = _make_stub_config(tmp_path)
    kwargs = _builder_kwargs_from_stub(stub_artifact, replay_candidates, config)
    with pytest.raises(AssertionError, match="must be non-None"):
        stage2d.build_aggregate_record(
            **kwargs,
            hg20_drift_detected=True,
            selection_json_sha256_end=None,
        )


def test_build_aggregate_record_non_drift_with_sha_raises(
    tmp_path, stub_artifact, replay_candidates,
):
    config = _make_stub_config(tmp_path)
    kwargs = _builder_kwargs_from_stub(stub_artifact, replay_candidates, config)
    with pytest.raises(AssertionError, match="must be None"):
        stage2d.build_aggregate_record(
            **kwargs,
            hg20_drift_detected=False,
            selection_json_sha256_end="deadbeef" * 8,
        )


# ---------------------------------------------------------------------------
# Item 8 — should_abort Lock 7 rules (load-bearing subset)
# ---------------------------------------------------------------------------


def test_should_abort_rule_a_two_consecutive_api_errors():
    records = [
        _persisted_record(
            firing_order=1, critic_status="d7b_error",
            d7b_error_category="api_level",
        ),
        _persisted_record(
            firing_order=2, critic_status="d7b_error",
            d7b_error_category="api_level",
        ),
    ]
    aborted, reason = stage2d.should_abort(
        idx=2, records=records, per_call_cost=0.01, cumulative_cost=0.02,
    )
    assert aborted is True
    assert reason == "consecutive_api_errors"


def test_should_abort_rule_b_error_rate_over_40_percent_after_k_floor():
    # 4 records, 2 d7b_errors = 50% > 40%, k_floor=3 satisfied.
    records = [
        _persisted_record(
            firing_order=1, critic_status="d7b_error",
            d7b_error_category="content_level",
        ),
        _persisted_record(firing_order=2),
        _persisted_record(
            firing_order=3, critic_status="d7b_error",
            d7b_error_category="content_level",
        ),
        _persisted_record(firing_order=4),
    ]
    aborted, reason = stage2d.should_abort(
        idx=4, records=records, per_call_cost=0.01, cumulative_cost=0.04,
    )
    assert aborted is True
    assert reason == "error_rate_threshold"


def test_should_abort_rule_c_fires_on_four_content_errors():
    # Four straight content_level errors — rules (a), (b), and (c) are all
    # potentially matchable. Per the C.3 ordering (g → a → b → c → d → e),
    # rule (b) fires first (100% error rate past K-floor). Rule (c)'s
    # absolute threshold is tested in isolation below.
    records = [
        _persisted_record(
            firing_order=i, critic_status="d7b_error",
            d7b_error_category="content_level",
        )
        for i in range(1, 5)
    ]
    aborted, reason = stage2d.should_abort(
        idx=4, records=records, per_call_cost=0.01, cumulative_cost=0.04,
    )
    assert aborted is True
    assert reason in {
        "error_rate_threshold",
        "content_level_threshold",
    }


def test_should_abort_rule_d_per_call_cost_exceeded():
    records = [_persisted_record(firing_order=1)]
    aborted, reason = stage2d.should_abort(
        idx=1, records=records,
        per_call_cost=0.09,  # > 0.08 ceiling
        cumulative_cost=0.09,
    )
    assert aborted is True
    assert reason == "per_call_cost_exceeded"


def test_should_abort_rule_e_cumulative_cost_cap():
    records = [_persisted_record(firing_order=1)]
    aborted, reason = stage2d.should_abort(
        idx=1, records=records,
        per_call_cost=0.01,
        cumulative_cost=8.01,  # > 8.00 cap
    )
    assert aborted is True
    assert reason == "cumulative_cost_cap_exceeded"


def test_should_abort_skipped_source_at_pos_116_does_not_fire_rule_g():
    # A skipped-source record at the ratified pos 116 slot is expected
    # and transparent to rules (a)-(c) via §7.8 non_skipped filtering.
    # Rule (g) only fires on an UNEXPECTED skipped position.
    records = [
        _persisted_record(
            firing_order=116, position=116,
            critic_status="skipped_source_invalid",
            actual_cost_usd=0.0, estimated_usd=0.0,
        ),
    ]
    aborted, reason = stage2d.should_abort(
        idx=1, records=records, per_call_cost=0.0, cumulative_cost=0.0,
    )
    assert aborted is False
    assert reason is None


def test_should_abort_unexpected_skipped_position_fires_rule_g():
    # Skipped-source at a position other than 116 is an §7.7 rule (g)
    # violation.
    records = [
        _persisted_record(
            firing_order=42, position=42,
            critic_status="skipped_source_invalid",
            actual_cost_usd=0.0, estimated_usd=0.0,
        ),
    ]
    aborted, reason = stage2d.should_abort(
        idx=1, records=records, per_call_cost=0.0, cumulative_cost=0.0,
    )
    assert aborted is True
    assert reason == "unexpected_skipped_source"


# ---------------------------------------------------------------------------
# Item 9 — HG1b reload-drift raises Stage2dStartupError (3e.1 conversion)
# ---------------------------------------------------------------------------


@pytest.fixture
def dryrun_scratch(tmp_path_factory) -> Path:
    """Unique scratch subdir UNDER the real DRYRUN_ROOT so
    ``_assert_stub_isolation`` accepts the paths. Cleaned up after the
    test by pytest's tmp_path infrastructure since we ``mktemp`` under
    a basetemp pointed at DRYRUN_ROOT.
    """
    DRYRUN_ROOT.mkdir(parents=True, exist_ok=True)
    scratch = DRYRUN_ROOT / f"pytest_{tmp_path_factory._given_basetemp.name if tmp_path_factory._given_basetemp else 'tmp'}_{id(tmp_path_factory):x}"
    scratch.mkdir(parents=True, exist_ok=True)
    yield scratch
    # Best-effort cleanup; not fatal if it fails.
    import shutil
    shutil.rmtree(scratch, ignore_errors=True)


def test_hg1b_reload_drift_raises_stage2d_startup_error(
    dryrun_scratch, monkeypatch,
):
    """Startup gates see a full 200-candidate list; the post-startup
    reload site then sees 199. The 3e.1 HG1b check must raise with a
    forensic message that names the count mismatch.
    """
    config = _make_stub_config(dryrun_scratch)

    # Let startup gates run to completion (they each parse
    # selection.json and would raise their own HG1b at Gate 4 if the
    # count is wrong), then tamper only at the post-startup reload
    # site by gating the tamper on the startup-audit file's existence:
    # startup_audit is written AFTER the last gate and BEFORE the
    # reload. This isolates the 3e.1 conversion from the Gate 4
    # twin-invariant.
    original_loads = json.loads

    def tampered_loads(s, *args, **kwargs):
        result = original_loads(s, *args, **kwargs)
        if (
            config.startup_audit_path.exists()
            and isinstance(result, dict)
            and isinstance(result.get("candidates"), list)
            and len(result["candidates"]) == stage2d.STAGE2D_SOURCE_N
        ):
            tampered = dict(result)
            tampered["candidates"] = result["candidates"][:-1]  # 199
            return tampered
        return result

    # Scope the patch to the module-under-test so unrelated callers
    # (e.g. subprocess helpers) still see untampered json.loads.
    monkeypatch.setattr(stage2d.json, "loads", tampered_loads)

    with pytest.raises(
        stage2d.Stage2dStartupError,
        match=r"HG1b: candidate count drift after startup gates\. "
              r"Expected 200, got 199",
    ):
        stage2d.run_stage2d(config)


# ---------------------------------------------------------------------------
# Item 10 — stub-run integration smoke (subprocess)
# ---------------------------------------------------------------------------


def test_stub_run_integration_smoke(stub_artifact):
    """End-to-end invocation via subprocess must produce a 51-key
    aggregate with ``write_completed_at`` as the final key.

    The ``stub_artifact`` fixture already invoked ``--stub`` once per
    session; this test just asserts on the produced artifact.
    """
    assert len(stub_artifact) == 51
    keys = list(stub_artifact.keys())
    assert keys[-1] == "write_completed_at"
    assert "stage2c_archive_sha256_by_file" in stub_artifact
    assert stub_artifact["stage2c_archive_sha256_by_file"] is None
    assert "hg20_drift_detected" not in stub_artifact
    assert stub_artifact["critic_status_counts"] == {
        "ok": 199, "d7b_error": 0, "skipped_source_invalid": 1,
    }
    assert len(stub_artifact["per_call_records"]) == 200

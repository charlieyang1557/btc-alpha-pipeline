#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# stage2d_self_check.py
#
# Pre-fire structural integrity check for
# docs/d7_stage2d/stage2d_expectations.md (or the DRAFT pre-rename).
#
# Scope-lock anchor:   docs/d7_stage2d/D7_STAGE2D_SCOPE_LOCK_v2.md  (Lock 12)
# Design spec anchor:  docs/d7_stage2d/stage2d_self_check_design_spec.md
#
# Task 3b.3 complete — 28/28 counted gates active.
#   Lock 12:      L12-01..L12-17 (17 gates)
#   Format:       FMT-01, FMT-02, FMT-02b, FMT-03..FMT-09, FMT-11 (11 gates)
#   Harness:      PATH-01, PATH-02 (advisory WARNs; not counted)
#
# Stdlib only. Exit codes: 0 = all pass (lenient), 1 = counted FAIL,
# 2 = harness error (L12-01 FAIL, path resolution, decode).
# ---------------------------------------------------------------------------

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Literal

# ---------------------------------------------------------------------------
# Repo root resolution (sentinel-guarded per Claude Obs 2)
# ---------------------------------------------------------------------------


def _resolve_repo_root() -> Path:
    root = Path(__file__).resolve().parents[1]
    # Sentinel: pyproject.toml must exist at repo root. Guards against the
    # silent-wrong-path failure mode where a moved script would resolve to a
    # bogus parent directory and then have every downstream gate SKIP on
    # "file not found" rather than emit a clear harness error.
    if not (root / "pyproject.toml").is_file():
        sys.stderr.write(
            f"[harness] pyproject.toml not found at resolved repo root {root}; "
            f"script must live under <repo>/scripts/. Aborting.\n"
        )
        sys.exit(2)
    return root


_REPO_ROOT = _resolve_repo_root()

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

EXPECTATIONS_MD = _REPO_ROOT / "docs/d7_stage2d/stage2d_expectations.md"
EXPECTATIONS_DRAFT = _REPO_ROOT / "docs/d7_stage2d/stage2d_expectations.DRAFT.md"
SCOPE_LOCK = _REPO_ROOT / "docs/d7_stage2d/D7_STAGE2D_SCOPE_LOCK_v2.md"
LABEL_UNIVERSE = _REPO_ROOT / "docs/d7_stage2d/label_universe_analysis.json"
REPLAY_CANDS = _REPO_ROOT / "docs/d7_stage2d/replay_candidates.json"
DEEP_DIVE_CANDS = _REPO_ROOT / "docs/d7_stage2d/deep_dive_candidates.json"
TEST_RETEST = _REPO_ROOT / "docs/d7_stage2d/test_retest_baselines.json"

# ---------------------------------------------------------------------------
# Hard-coded constants (Lock-cited; see design spec §4)
# ---------------------------------------------------------------------------

# Lock 6.4 — hard-coded, no JSON derivation permitted. Validated by L12-13
# (§6.4 structured-claim literal-set + threshold=2 check), not by FMT-11.
FRESH_7_POOL = frozenset({3, 43, 68, 128, 173, 188, 198})

# Lock 4.3 — fresh eligible pool (universe_a \ stage2c_20).
FRESH_9_POOL = frozenset({122, 127, 128, 129, 132, 172, 178, 182, 187})

# Lock 12 Gate 7 — exact position set for the three-run test-retest tier.
TIER_1_POSITIONS = frozenset({17, 73, 74, 97, 138})

# The 20 Stage 2c replay positions; upstream frozen.
STAGE2C_POSITIONS = frozenset(
    {17, 22, 27, 32, 62, 72, 73, 74, 77, 83, 97, 102, 107, 112, 117, 138, 143, 147, 152, 162}
)

POSITION_116_SKIP = 116  # Lock 1.5 — deterministic skipped source.

RSI_ABSENT_THRESHOLD = 2  # Lock 6.4 — ≥ 2/7 with SVR < 0.5.

E3_OR_BUCKET_POSITIONS = frozenset({72, 74, 83, 138})
E3_OR_BUCKET_PAIRS = frozenset({("MODERATE-HIGH", "HIGH"), ("LOW", "MODERATE-LOW")})

SECTION_64_HEADER_RE = re.compile(
    r"^## §6\.4 — Fresh-7 RSI-Absent vol_regime Structured Claim$", re.MULTILINE
)

# Lock 11.1 required canonical top-level headers (10 total).
# "Frozen Pre-Registration Anchors" ≡ "Anti-Hindsight Anchor" (dual-literal).
CANONICAL_HEADERS = [
    {"Frozen Pre-Registration Anchors", "Anti-Hindsight Anchor"},
    {"Label Universes"},
    {"§6.1 — Aggregate Expectations Across All 199 D7b Calls"},
    {"§6.2 — Axis-Specific Label Claims"},
    {"§6.3 — SVR Distribution-Shape Claim (TBD-DIST)"},
    {"§6.4 — Fresh-7 RSI-Absent vol_regime Structured Claim"},
    {"§E3 — Multi-Tier Test-Retest Grid"},
    {"§E4 — Deep-Dive Per-Candidate Expectations (n=20)"},
    {"Remaining Candidates (Schema-Level Only)"},
    {"Position 116 Treatment — brief reference to Lock 1.5"},
]

# §11.1.a-permitted additional canonical headers (not required).
PERMITTED_ADDITIONAL = {
    "§6.5 — Theme-Stratified Sub-Claims",
    "§6.6 — Plausibility / Alignment Observation Axes",
}

# §11.1.a prefix convention: "§<digit>.<digit> — " or "§E<digit> — ".
SECTION_PREFIX_RE = re.compile(r"^(§\d+\.\d+\s—\s|§E\d+\s—\s)")

# FMT-02 sealed 6-label skeleton (numbered + ordered + bolded).
FMT02_LABELS = [
    ("1", "Structural assessment."),
    ("2", "Plausibility expectation."),
    ("3", "Alignment expectation."),
    ("4", "SVR expectation."),
    ("5", "Reconciliation expectation."),
    ("6", "Core judgment."),
]

# FMT-02b conditional label.
FMT02B_LABEL = ("7", "UA metadata.")

# ---------------------------------------------------------------------------
# Harness / gate dataclasses
# ---------------------------------------------------------------------------

GateStatus = Literal["PASS", "FAIL", "WARN", "SKIP"]


@dataclass(frozen=True)
class GateResult:
    gate_id: str
    status: GateStatus
    message: str
    violations: tuple[str, ...] = ()


@dataclass
class HarnessState:
    expectations_path: Path | None = None
    expectations_text: str | None = None
    path_warnings: list[GateResult] = field(default_factory=list)
    gate_results: list[GateResult] = field(default_factory=list)
    failed_upstream: set[str] = field(default_factory=set)
    # Parsed artifacts (populated lazily by gates as needed).
    toplevel_headers: list[tuple[str, int]] | None = None  # (header_text, line_num)
    e4_blocks: dict[int, tuple[str, int, int]] | None = None  # pos → (text, start, end)


# ---------------------------------------------------------------------------
# Path resolution with PATH-01 / PATH-02 harness warnings
# ---------------------------------------------------------------------------


def resolve_expectations_path(state: HarnessState) -> Path | None:
    md_exists = EXPECTATIONS_MD.is_file()
    draft_exists = EXPECTATIONS_DRAFT.is_file()
    if md_exists and draft_exists:
        state.path_warnings.append(
            GateResult(
                "PATH-02",
                "WARN",
                "both .md and .DRAFT.md present; using .md   [harness-level; not counted]",
            )
        )
        return EXPECTATIONS_MD
    if md_exists:
        return EXPECTATIONS_MD
    if draft_exists:
        state.path_warnings.append(
            GateResult(
                "PATH-01",
                "WARN",
                "operating on DRAFT (pre-rename)   [harness-level; not counted]",
            )
        )
        return EXPECTATIONS_DRAFT
    return None


# ---------------------------------------------------------------------------
# Parsers (shared across gates)
# ---------------------------------------------------------------------------


def parse_toplevel_headers(text: str) -> list[tuple[str, int]]:
    """Return list of (header_text_after_'## ', 1-indexed line number)."""
    out: list[tuple[str, int]] = []
    for i, line in enumerate(text.splitlines(), start=1):
        if line.startswith("## ") and not line.startswith("### "):
            out.append((line[3:].rstrip(), i))
    return out


def parse_e4_blocks(text: str) -> dict[int, tuple[str, int, int]]:
    """
    Parse §E4 per-candidate blocks. Returns dict keyed by position number,
    value is (block_text, start_line, end_line). Blocks are bounded by
    '### Position N — <name>' headers inside the §E4 section; block ends
    at the next '### Position' header or the next '## '-level header.

    Raises RuntimeError on duplicate '### Position N' headers within §E4
    — duplicate position headers in sealed content are structural
    corruption, not a gate-level finding. The runner surfaces the error
    and exits 2 via harness-error handling.
    """
    lines = text.splitlines()
    # Locate §E4 section bounds.
    e4_start = None
    e4_end = len(lines)
    for i, line in enumerate(lines):
        if line.startswith("## §E4 "):
            e4_start = i
        elif e4_start is not None and line.startswith("## "):
            e4_end = i
            break
    if e4_start is None:
        return {}
    pos_re = re.compile(r"^### Position (\d+)\s*—")
    block_starts: list[tuple[int, int]] = []  # (line_idx, position)
    for i in range(e4_start, e4_end):
        m = pos_re.match(lines[i])
        if m:
            block_starts.append((i, int(m.group(1))))
    positions = [p for _, p in block_starts]
    if len(positions) != len(set(positions)):
        dups = sorted({p for p in positions if positions.count(p) > 1})
        raise RuntimeError(f"§E4 contains duplicate position headers: {dups}")
    blocks: dict[int, tuple[str, int, int]] = {}
    for idx, (start_line, pos) in enumerate(block_starts):
        end_line = block_starts[idx + 1][0] if idx + 1 < len(block_starts) else e4_end
        block_text = "\n".join(lines[start_line:end_line])
        blocks[pos] = (block_text, start_line + 1, end_line)
    return blocks


def get_e4_blocks(state: HarnessState) -> dict[int, tuple[str, int, int]]:
    """Lazy-populate state.e4_blocks on first access. Decouples §E4 parsing
    from registry ordering — any gate that needs the parsed §E4 blocks
    can call this helper without depending on a prior gate having run."""
    if state.e4_blocks is None:
        assert state.expectations_text is not None, (
            "get_e4_blocks called before L12-01 established expectations_text"
        )
        state.e4_blocks = parse_e4_blocks(state.expectations_text)
    return state.e4_blocks


# ---------------------------------------------------------------------------
# JSON loader (gate-friendly: no exceptions on common failure modes)
# ---------------------------------------------------------------------------


def _load_json_artifact(
    path: Path, gate_id: str
) -> tuple[dict[str, Any] | None, GateResult | None]:
    """Load JSON; on failure return (None, FAIL GateResult). On success (data, None)."""
    if not path.is_file():
        return None, GateResult(gate_id, "FAIL", f"required artifact missing: {path.name}")
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as e:
        return None, GateResult(gate_id, "FAIL", f"{path.name}: UTF-8 decode error: {e}")
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        return None, GateResult(gate_id, "FAIL", f"{path.name}: JSON parse error: {e}")
    if not isinstance(data, dict):
        return None, GateResult(
            gate_id,
            "FAIL",
            f"{path.name}: top-level must be dict, got {type(data).__name__}",
        )
    return data, None


# ---------------------------------------------------------------------------
# §E3 tier-grid parser (shared by L12-07, L12-08, FMT-11)
# ---------------------------------------------------------------------------

_TIER_HEADERS = {1: "### Tier 1 ", 2: "### Tier 2 "}
_GRID_ROW_RE = re.compile(r"^\|\s*(\d+)\s*\|")


def _parse_e3_tier_grid(text: str, tier: int) -> list[int]:
    """
    Return position numbers (in document order) from the §E3 Tier <N> grid.
    Tier section bounded by '### Tier N ' header → next '### ' header (or
    end of §E3). Data rows are pipe-prefixed Markdown table rows whose
    first column is a bare integer; the header row '| Pos | UA label | ...'
    is skipped because 'Pos' is not numeric. The separator row
    '|-----|...' is also skipped (no leading digits).
    """
    lines = text.splitlines()
    in_e3 = False
    in_tier = False
    positions: list[int] = []
    target_header = _TIER_HEADERS[tier]
    for line in lines:
        if line.startswith("## §E3 "):
            in_e3 = True
            in_tier = False
            continue
        if in_e3 and line.startswith("## "):
            break  # left §E3
        if not in_e3:
            continue
        if line.startswith(target_header):
            in_tier = True
            continue
        if in_tier and line.startswith("### "):
            in_tier = False
            continue
        if in_tier:
            m = _GRID_ROW_RE.match(line)
            if m:
                positions.append(int(m.group(1)))
    return positions


# ---------------------------------------------------------------------------
# Live gates (5)
# ---------------------------------------------------------------------------


def gate_L12_01(state: HarnessState) -> GateResult:
    path = resolve_expectations_path(state)
    if path is None:
        state.failed_upstream.add("L12-01")
        return GateResult(
            "L12-01",
            "FAIL",
            f"neither {EXPECTATIONS_MD.name} nor {EXPECTATIONS_DRAFT.name} found under docs/d7_stage2d/",
        )
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as e:
        state.failed_upstream.add("L12-01")
        return GateResult("L12-01", "FAIL", f"UTF-8 decode error on {path.name}: {e}")
    state.expectations_path = path
    state.expectations_text = text
    # Bytes via stat() (true file size); len(text) is char count after UTF-8 decode
    # and would understate the byte count for files containing multi-byte chars
    # (§, ≥, ≤, ─, —, etc.). Reporting bytes keeps consistency with `wc -c`.
    size_bytes = path.stat().st_size
    return GateResult("L12-01", "PASS", f"file exists, UTF-8 valid ({path.name}, {size_bytes} bytes)")


def gate_L12_02(state: HarnessState) -> GateResult:
    assert state.expectations_text is not None
    headers = parse_toplevel_headers(state.expectations_text)
    state.toplevel_headers = headers
    header_texts = [h for h, _ in headers]

    missing_required: list[str] = []
    for required_set in CANONICAL_HEADERS:
        if not any(h in required_set for h in header_texts):
            missing_required.append(" | ".join(sorted(required_set)))

    permitted_present = [h for h in header_texts if h in PERMITTED_ADDITIONAL]

    # Extras = headers that (a) don't satisfy a required canonical set,
    # (b) aren't in permitted-additional. Prefix convention is evaluated
    # against the "§"-prefixed headers only; non-§ headers like
    # "Label Universes" are exempt.
    recognized: set[str] = set()
    for s in CANONICAL_HEADERS:
        recognized |= s
    recognized |= PERMITTED_ADDITIONAL
    extras = [h for h in header_texts if h not in recognized]
    # Prefix-convention violations among extras that start with '§'.
    prefix_violations = [h for h in extras if h.startswith("§") and not SECTION_PREFIX_RE.match(h)]

    if missing_required:
        return GateResult(
            "L12-02",
            "FAIL",
            f"missing required canonical headers: {missing_required}",
        )
    if prefix_violations:
        return GateResult(
            "L12-02",
            "FAIL",
            f"§-prefixed headers violate §11.1.a prefix convention: {prefix_violations}",
        )
    if extras:
        return GateResult(
            "L12-02",
            "WARN",
            (
                f"all 10 required canonical headers present; "
                f"{len(permitted_present)} permitted additional; "
                f"{len(extras)} unexpected extras: {extras}"
            ),
        )
    return GateResult(
        "L12-02",
        "PASS",
        (
            f"all 10 required canonical headers present; "
            f"{len(permitted_present)} permitted additional ({sorted(permitted_present)}); "
            f"0 unexpected extras"
        ),
    )


def gate_L12_03(state: HarnessState) -> GateResult:
    """
    Scan for a SHA256 hex string near the 'label_universe_analysis.json'
    reference. Window = ±2 lines around each filename mention. Rationale:
    the expectations file cites the JSON by filename on one line and the
    SHA on an immediately-adjacent line (common Markdown pattern
    '(SHA256: `<hex>`)'); a ±2 window tolerates minor line-break
    variation from prose rewraps without matching unrelated SHA hex
    strings elsewhere in the document (e.g. scope-lock commit hashes in
    a distant section).
    """
    assert state.expectations_text is not None
    lines = state.expectations_text.splitlines()
    file_re = re.compile(r"label_universe_analysis\.json")
    sha_re = re.compile(r"\b[0-9a-f]{64}\b")
    filename_hits = [i for i, line in enumerate(lines) if file_re.search(line)]
    if not filename_hits:
        return GateResult(
            "L12-03",
            "FAIL",
            "no reference to 'label_universe_analysis.json' found in expectations file",
        )
    for idx in filename_hits:
        lo = max(0, idx - 2)
        hi = min(len(lines), idx + 3)
        for j in range(lo, hi):
            m = sha_re.search(lines[j])
            if m:
                same_line = "same line" if j == idx else f"±{j - idx} line(s) away"
                return GateResult(
                    "L12-03",
                    "PASS",
                    (
                        f"SHA256 found near label_universe_analysis.json reference "
                        f"(filename line {idx + 1}, SHA line {j + 1}, {same_line}): "
                        f"{m.group(0)[:12]}..."
                    ),
                )
    return GateResult(
        "L12-03",
        "FAIL",
        f"label_universe_analysis.json referenced at line(s) {[i + 1 for i in filename_hits]} "
        f"but no SHA256 hex within ±2 lines",
    )


def gate_FMT_02(state: HarnessState) -> GateResult:
    """
    Verify each §E4 block contains the numbered+ordered+bolded 6-label
    skeleton verbatim. Order and numeric prefix enforced.
    """
    blocks = get_e4_blocks(state)
    if not blocks:
        return GateResult("FMT-02", "FAIL", "no §E4 blocks parsed (section missing or empty)")
    violations: list[str] = []
    for pos in sorted(blocks):
        block_text, _, _ = blocks[pos]
        # Scan for each expected '<N>. **<label>**' in sequence; enforce order
        # by tracking last match offset.
        cursor = 0
        for idx, (num, label) in enumerate(FMT02_LABELS, start=1):
            needle = f"{num}. **{label}**"
            hit = block_text.find(needle, cursor)
            if hit == -1:
                # Check whether the label appears out of order (for better msg).
                global_hit = block_text.find(needle)
                shape = "MISSING" if global_hit == -1 else "OUT_OF_ORDER"
                violations.append(
                    f'block pos={pos} label_index={idx} expected="{needle}" found="{shape}"'
                )
                break
            cursor = hit + len(needle)
    if violations:
        return GateResult(
            "FMT-02",
            "FAIL",
            f"{len(violations)} violations in §E4 skeleton check",
            tuple(violations),
        )
    return GateResult("FMT-02", "PASS", f"{len(blocks)}/{len(blocks)} blocks contain numbered+ordered 6-label skeleton")


def gate_FMT_02b(state: HarnessState) -> GateResult:
    """UA metadata line present iff position ∈ FRESH_9_POOL."""
    blocks = get_e4_blocks(state)
    ua_needle = f"{FMT02B_LABEL[0]}. **{FMT02B_LABEL[1]}**"
    violations: list[str] = []
    present_count = 0
    absent_count = 0
    for pos, (block_text, _, _) in sorted(blocks.items()):
        expected_present = pos in FRESH_9_POOL
        actual_present = ua_needle in block_text
        if actual_present:
            present_count += 1
        else:
            absent_count += 1
        if actual_present != expected_present:
            violations.append(
                f"block pos={pos} "
                f"expected={'PRESENT' if expected_present else 'ABSENT'} "
                f"actual={'PRESENT' if actual_present else 'ABSENT'} "
                f"(fresh-9 membership={expected_present})"
            )
    if violations:
        return GateResult(
            "FMT-02b",
            "FAIL",
            f"{len(violations)} UA-metadata presence violations",
            tuple(violations),
        )
    return GateResult(
        "FMT-02b",
        "PASS",
        f"UA metadata: {present_count} present (fresh-9), {absent_count} absent (non-fresh-9)",
    )


# ---------------------------------------------------------------------------
# Live gates (3b.2): L12-04..L12-10, FMT-11
# ---------------------------------------------------------------------------


def gate_L12_04(state: HarnessState) -> GateResult:
    data, err = _load_json_artifact(REPLAY_CANDS, "L12-04")
    if err:
        state.failed_upstream.add("L12-04")
        return err
    cands = data.get("candidates")
    if not isinstance(cands, list):
        state.failed_upstream.add("L12-04")
        return GateResult(
            "L12-04", "FAIL", "replay_candidates.json: 'candidates' missing or not a list"
        )
    if len(cands) != 200:
        return GateResult(
            "L12-04", "FAIL", f"replay_candidates.json: expected 200 entries, got {len(cands)}"
        )
    skipped = [c for c in cands if c.get("is_skipped_source") is True]
    eligible = len(cands) - len(skipped)
    if eligible != 199:
        return GateResult(
            "L12-04",
            "FAIL",
            f"expected 199 replay-eligible, got {eligible} (skipped={len(skipped)})",
        )
    pos_116 = next((c for c in cands if c.get("position") == POSITION_116_SKIP), None)
    if pos_116 is None:
        return GateResult("L12-04", "FAIL", "no position 116 entry in replay_candidates.json")
    if pos_116.get("is_skipped_source") is not True:
        return GateResult(
            "L12-04",
            "FAIL",
            f"pos 116 is_skipped_source={pos_116.get('is_skipped_source')!r}, expected True",
        )
    return GateResult(
        "L12-04",
        "PASS",
        "replay_candidates.json: 200 entries, 199 replay-eligible, pos 116 is_skipped_source=True",
    )


def gate_L12_05(state: HarnessState) -> GateResult:
    data, err = _load_json_artifact(DEEP_DIVE_CANDS, "L12-05")
    if err:
        state.failed_upstream.add("L12-05")
        return err
    cands = data.get("candidates")
    if not isinstance(cands, list):
        state.failed_upstream.add("L12-05")
        return GateResult(
            "L12-05", "FAIL", "deep_dive_candidates.json: 'candidates' missing or not a list"
        )
    if len(cands) != 20:
        return GateResult("L12-05", "FAIL", f"expected 20 deep-dive entries, got {len(cands)}")
    positions = {c.get("position") for c in cands}
    if POSITION_116_SKIP in positions:
        return GateResult("L12-05", "FAIL", "deep-dive includes position 116 (forbidden)")
    overlap = positions & STAGE2C_POSITIONS
    if overlap:
        return GateResult(
            "L12-05", "FAIL", f"deep-dive overlaps Stage 2c positions: {sorted(overlap)}"
        )
    return GateResult(
        "L12-05",
        "PASS",
        "deep_dive_candidates.json: 20 entries, no pos 116, no Stage 2c-20 overlap",
    )


_REQUIRED_BASELINE_SCORES = (
    "plausibility",
    "alignment",
    "svr",
    "reasoning_length",
    "source_record_sha256",
)


def gate_L12_06(state: HarnessState) -> GateResult:
    data, err = _load_json_artifact(TEST_RETEST, "L12-06")
    if err:
        state.failed_upstream.add("L12-06")
        return err
    bls = data.get("baselines")
    if not isinstance(bls, list):
        state.failed_upstream.add("L12-06")
        return GateResult(
            "L12-06", "FAIL", "test_retest_baselines.json: 'baselines' missing or not a list"
        )
    if len(bls) != 20:
        return GateResult("L12-06", "FAIL", f"expected 20 baselines, got {len(bls)}")
    positions = {b.get("position") for b in bls}
    if not positions <= STAGE2C_POSITIONS:
        extras = sorted(positions - STAGE2C_POSITIONS)
        return GateResult(
            "L12-06",
            "FAIL",
            f"baseline positions not ⊆ STAGE2C_POSITIONS; extras: {extras}",
        )
    missing_scores: list[str] = []
    for b in bls:
        s2c = b.get("stage2c") or {}
        for f in _REQUIRED_BASELINE_SCORES:
            if s2c.get(f) is None:
                missing_scores.append(f"pos={b.get('position')} field={f}")
    if missing_scores:
        violations = tuple(missing_scores[:10])
        if len(missing_scores) > 10:
            violations = violations + (f"... ({len(missing_scores) - 10} more)",)
        return GateResult(
            "L12-06",
            "FAIL",
            f"{len(missing_scores)} baseline score fields missing/null",
            violations,
        )
    return GateResult(
        "L12-06",
        "PASS",
        "test_retest_baselines.json: 20 entries, positions ⊆ STAGE2C_POSITIONS, all 5 score fields populated",
    )


def gate_L12_07(state: HarnessState) -> GateResult:
    assert state.expectations_text is not None
    grid_positions = _parse_e3_tier_grid(state.expectations_text, 1)
    if len(grid_positions) != 5:
        return GateResult(
            "L12-07",
            "FAIL",
            f"§E3 Tier 1 grid: expected 5 rows, got {len(grid_positions)}",
        )
    grid_set = set(grid_positions)
    if grid_set != TIER_1_POSITIONS:
        sym_diff = grid_set ^ TIER_1_POSITIONS
        return GateResult(
            "L12-07",
            "FAIL",
            (
                f"§E3 Tier 1 grid positions {sorted(grid_set)} ≠ TIER_1_POSITIONS "
                f"{sorted(TIER_1_POSITIONS)}; sym-diff={sorted(sym_diff)}"
            ),
        )
    return GateResult("L12-07", "PASS", f"§E3 Tier 1 grid: 5 rows, positions {sorted(grid_set)}")


def gate_L12_08(state: HarnessState) -> GateResult:
    """Cross-check §E3 Tier 2 grid positions against test_retest_baselines tier-2 set.

    Per dependency graph, SKIPs if L12-06 failed upstream — L12-08's check is
    meaningful only against valid baselines artifact. Independent re-load
    would otherwise duplicate L12-06's missing/parse error noise.
    """
    if "L12-06" in state.failed_upstream:
        return GateResult("L12-08", "SKIP", "upstream L12-06 failed (test_retest_baselines.json)")
    assert state.expectations_text is not None
    grid_positions = _parse_e3_tier_grid(state.expectations_text, 2)
    if len(grid_positions) != 15:
        return GateResult(
            "L12-08",
            "FAIL",
            f"§E3 Tier 2 grid: expected 15 rows, got {len(grid_positions)}",
        )
    data, err = _load_json_artifact(TEST_RETEST, "L12-08")
    if err:
        return err
    bls = data.get("baselines") or []
    baseline_tier2 = {b.get("position") for b in bls if b.get("tier") == 2}
    grid_set = set(grid_positions)
    if grid_set != baseline_tier2:
        sym_diff = grid_set ^ baseline_tier2
        return GateResult(
            "L12-08",
            "FAIL",
            (
                f"§E3 Tier 2 grid {sorted(grid_set)} ≠ baselines tier-2 "
                f"{sorted(baseline_tier2)}; sym-diff={sorted(sym_diff)}"
            ),
        )
    return GateResult(
        "L12-08", "PASS", "§E3 Tier 2 grid: 15 rows, matches test_retest_baselines tier-2 set"
    )


def gate_L12_09(state: HarnessState) -> GateResult:
    """SKIPs if L12-05 failed (deep_dive_candidates.json unavailable for cross-ref)."""
    if "L12-05" in state.failed_upstream:
        return GateResult("L12-09", "SKIP", "upstream L12-05 failed (deep_dive_candidates.json)")
    blocks = get_e4_blocks(state)
    data, err = _load_json_artifact(DEEP_DIVE_CANDS, "L12-09")
    if err:
        return err
    json_positions = {c.get("position") for c in (data.get("candidates") or [])}
    e4_positions = set(blocks.keys())
    if len(e4_positions) != 20:
        return GateResult(
            "L12-09",
            "FAIL",
            f"§E4 deep-dive: expected 20 blocks, got {len(e4_positions)}",
        )
    if e4_positions != json_positions:
        sym_diff = e4_positions ^ json_positions
        return GateResult(
            "L12-09",
            "FAIL",
            f"§E4 positions ≠ deep_dive_candidates.json positions; sym-diff={sorted(sym_diff)}",
        )
    return GateResult(
        "L12-09", "PASS", "§E4 deep-dive: 20 positions, all in deep_dive_candidates.json"
    )


def gate_L12_10(state: HarnessState) -> GateResult:
    blocks = get_e4_blocks(state)
    e4_positions = set(blocks.keys())
    fresh_in_e4 = e4_positions & FRESH_9_POOL
    if len(fresh_in_e4) < 3:
        return GateResult(
            "L12-10",
            "FAIL",
            (
                f"only {len(fresh_in_e4)} of 9 fresh eligible-pool positions in §E4 deep-dive "
                f"(need ≥3); present={sorted(fresh_in_e4)}"
            ),
        )
    return GateResult(
        "L12-10",
        "PASS",
        (
            f"{len(fresh_in_e4)} of 9 fresh eligible-pool positions present in §E4 deep-dive "
            f"(≥3 required); positions={sorted(fresh_in_e4)}"
        ),
    )


def gate_FMT_11(state: HarnessState) -> GateResult:
    """Cross-consistency (3 sets only); FRESH_7 excluded per Lock 6.4.

    (i)   FRESH_9_POOL == set(label_universe_analysis.json.fresh_eligible_pool_positions)
    (ii)  TIER_1_POSITIONS == _parse_e3_tier_grid(expectations, tier=1)
    (iii) STAGE2C_POSITIONS == {b.position for b in test_retest_baselines.baselines}
    """
    assert state.expectations_text is not None
    violations: list[str] = []

    # (i) FRESH_9_POOL — derived from label_universe_analysis.json's flat list
    # field "fresh_eligible_pool_positions" (disk-verified: list[int], n=9).
    data_lu, err_lu = _load_json_artifact(LABEL_UNIVERSE, "FMT-11")
    if err_lu:
        return err_lu
    raw_fresh = data_lu.get("fresh_eligible_pool_positions")
    if not isinstance(raw_fresh, list):
        violations.append(
            "label_universe_analysis.json: 'fresh_eligible_pool_positions' missing or not a list"
        )
    else:
        derived_fresh_9 = set(raw_fresh)
        if derived_fresh_9 != FRESH_9_POOL:
            sym_diff = derived_fresh_9 ^ FRESH_9_POOL
            violations.append(
                f"FRESH_9 mismatch: hardcoded={sorted(FRESH_9_POOL)} "
                f"derived={sorted(derived_fresh_9)} sym-diff={sorted(sym_diff)}"
            )

    # (ii) TIER_1_POSITIONS — derived from §E3 Tier 1 grid.
    tier_1_derived = set(_parse_e3_tier_grid(state.expectations_text, 1))
    if tier_1_derived != TIER_1_POSITIONS:
        sym_diff = tier_1_derived ^ TIER_1_POSITIONS
        violations.append(
            f"TIER_1 mismatch: hardcoded={sorted(TIER_1_POSITIONS)} "
            f"derived={sorted(tier_1_derived)} sym-diff={sorted(sym_diff)}"
        )

    # (iii) STAGE2C_POSITIONS — derived from test_retest_baselines.json baselines.
    data_tr, err_tr = _load_json_artifact(TEST_RETEST, "FMT-11")
    if err_tr:
        return err_tr
    bls = data_tr.get("baselines") or []
    derived_stage2c = {b.get("position") for b in bls}
    if derived_stage2c != STAGE2C_POSITIONS:
        sym_diff = derived_stage2c ^ STAGE2C_POSITIONS
        violations.append(
            f"STAGE2C mismatch: hardcoded={sorted(STAGE2C_POSITIONS)} "
            f"derived={sorted(derived_stage2c)} sym-diff={sorted(sym_diff)}"
        )

    if violations:
        return GateResult(
            "FMT-11",
            "FAIL",
            f"{len(violations)}/3 cross-consistency check(s) failed",
            tuple(violations),
        )
    return GateResult(
        "FMT-11", "PASS", "3/3 cross-consistency sets match (FRESH_9, TIER_1, STAGE2C)"
    )


# ---------------------------------------------------------------------------
# Live gates (3b.3): L12-11..L12-17, FMT-01, FMT-03..FMT-09
# ---------------------------------------------------------------------------


def _section_body(text: str, header_starts: tuple[str, ...], stop_prefix: str = "## ") -> str:
    """Extract body between any of header_starts (inclusive) and the next
    stop_prefix '## '-level header (or EOF). First match wins."""
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if any(line.startswith(h) for h in header_starts):
            for j in range(i + 1, len(lines)):
                if lines[j].startswith(stop_prefix):
                    return "\n".join(lines[i:j])
            return "\n".join(lines[i:])
    return ""


def gate_L12_11(state: HarnessState) -> GateResult:
    """TBD-A1 / TBD-A2 must be numerically resolved in §6.2.1 / §6.2.2."""
    assert state.expectations_text is not None
    body_a1 = _section_body(state.expectations_text, ("### §6.2.1 Agreement Axis",))
    body_a2 = _section_body(state.expectations_text, ("### §6.2.2 Divergence Axis",))
    missing: list[str] = []
    # TBD-A1: must contain '≥ 52' and 'SVR ≥ 0.5'.
    if not re.search(r"≥\s*52\b", body_a1):
        missing.append("§6.2.1 missing numeric '≥ 52' threshold")
    if not re.search(r"SVR\s*[≥>=]\s*0\.5", body_a1):
        missing.append("§6.2.1 missing 'SVR ≥ 0.5' qualifier")
    # TBD-A2: must contain '≥ 4' and 'SVR ≥ 0.5'.
    if not re.search(r"≥\s*4\b", body_a2):
        missing.append("§6.2.2 missing numeric '≥ 4' threshold")
    if not re.search(r"SVR\s*[≥>=]\s*0\.5", body_a2):
        missing.append("§6.2.2 missing 'SVR ≥ 0.5' qualifier")
    # Reject literal placeholder tokens left unresolved.
    for sec_name, body in (("§6.2.1", body_a1), ("§6.2.2", body_a2)):
        if re.search(r"\bTBD\b(?!-A[12])", body):
            missing.append(f"{sec_name} contains unresolved 'TBD' placeholder")
    if missing:
        return GateResult("L12-11", "FAIL", f"{len(missing)} TBD-A1/A2 resolution issues", tuple(missing))
    return GateResult("L12-11", "PASS", "§6.2.1 TBD-A1 (≥52) and §6.2.2 TBD-A2 (≥4) numerically resolved")


def gate_L12_12(state: HarnessState) -> GateResult:
    """TBD-DIST must resolve to numeric (a) ≥ 90 at SVR ≥ 0.80 and (b) ≥ 30 at SVR ≤ 0.30 in §6.3."""
    assert state.expectations_text is not None
    body = _section_body(state.expectations_text, ("## §6.3 ",))
    missing: list[str] = []
    if not re.search(r"≥\s*90\b.*SVR\s*[≥>=]\s*0\.80", body, re.DOTALL):
        # Try permissive line-by-line check.
        if not (re.search(r"≥\s*90\b", body) and re.search(r"SVR\s*[≥>=]\s*0\.80", body)):
            missing.append("§6.3 (a) upper-tail '≥ 90' / 'SVR ≥ 0.80' not both present")
    if not (re.search(r"≥\s*30\b", body) and re.search(r"SVR\s*[≤<=]\s*0\.30", body)):
        missing.append("§6.3 (b) lower-tail '≥ 30' / 'SVR ≤ 0.30' not both present")
    if re.search(r"\bTBD\b(?!-DIST)", body):
        missing.append("§6.3 contains unresolved 'TBD' placeholder")
    if missing:
        return GateResult("L12-12", "FAIL", f"{len(missing)} TBD-DIST resolution issues", tuple(missing))
    return GateResult("L12-12", "PASS", "§6.3 TBD-DIST resolved: (a) ≥90 at SVR≥0.80, (b) ≥30 at SVR≤0.30")


def gate_L12_13(state: HarnessState) -> GateResult:
    """§6.4 must reference fresh-7 literal set + threshold=2 + 'RSI-absent vol_regime' framing."""
    assert state.expectations_text is not None
    body = _section_body(state.expectations_text, ("## §6.4 ",))
    issues: list[str] = []
    # Literal set membership: confirm all 7 fresh-7 ints appear in §6.4 body
    # (the operational definition line lists them explicitly as a Python set).
    set_re = re.compile(r"\{(?:\s*\d+\s*,?\s*)+\}")
    fresh_set_found = False
    for m in set_re.finditer(body):
        nums = {int(x) for x in re.findall(r"\d+", m.group(0))}
        if nums == set(FRESH_7_POOL):
            fresh_set_found = True
            break
    if not fresh_set_found:
        issues.append(f"§6.4 missing literal fresh-7 set {sorted(FRESH_7_POOL)}")
    # Threshold=2 must appear (e.g. '≥ 2' / '>= 2' / '≥2/7').
    if not re.search(r"(?:≥|>=)\s*" + str(RSI_ABSENT_THRESHOLD) + r"\b", body):
        issues.append(f"§6.4 missing threshold '≥ {RSI_ABSENT_THRESHOLD}'")
    # SVR < 0.5 framing required.
    if not re.search(r"SVR\s*<\s*0\.5", body):
        issues.append("§6.4 missing 'SVR < 0.5' framing")
    if issues:
        return GateResult("L12-13", "FAIL", f"{len(issues)} §6.4 RSI-absent claim issues", tuple(issues))
    return GateResult(
        "L12-13",
        "PASS",
        f"§6.4 cites fresh-7 set, threshold ≥{RSI_ABSENT_THRESHOLD}, SVR<0.5 framing",
    )


# L12-14 detector — see design spec §8 for scope/allowlist semantics.
_L12_14_DENYLIST = (
    r"subgroup",
    r"sub-group",
    r"cluster of candidates",
    r"class of candidates",
    r"candidates of this type",
    r"tend to land",
    r"typically land",
    r"usually land",
    r"as a group",
    r"in this group",
    r"members of this group",
    r"candidates like these",
    r"bimodal",
    r"monotonic subgroup",
)
_L12_14_DENY_RE = re.compile(
    r"\b(" + "|".join(_L12_14_DENYLIST) + r")\b", re.IGNORECASE
)
# Field labels to scan in each §E4 block. Reconciliation expectation
# (field 5) and UA metadata (field 7) are excluded per spec §8.
_L12_14_SCANNED_FIELDS = (
    "Structural assessment.",
    "Plausibility expectation.",
    "Alignment expectation.",
    "SVR expectation.",
    "Core judgment.",
)


def _extract_field_text(block_text: str, field_label: str) -> str:
    """Extract the prose body of a single numbered §E4 field. Body runs from
    'N. **<label>**' until the next 'M. **' label or end of block."""
    pattern = re.compile(
        r"\d+\.\s+\*\*" + re.escape(field_label) + r"\*\*(.*?)(?=\n\d+\.\s+\*\*|\Z)",
        re.DOTALL,
    )
    m = pattern.search(block_text)
    return m.group(1) if m else ""


def gate_L12_14(state: HarnessState) -> GateResult:
    """No sub-group hypothesis language in §E4 prose, scanned per-field.
    Allowlist applies only inside the §6.4 boundary, which is a separate
    `## ` section — so the allowlist is irrelevant inside §E4 blocks."""
    blocks = get_e4_blocks(state)
    violations: list[str] = []
    for pos in sorted(blocks):
        block_text, _, _ = blocks[pos]
        for field_label in _L12_14_SCANNED_FIELDS:
            field_body = _extract_field_text(block_text, field_label)
            if not field_body:
                continue
            for m in _L12_14_DENY_RE.finditer(field_body):
                violations.append(
                    f'block pos={pos} field="{field_label}" phrase="{m.group(0)}"'
                )
    if violations:
        head = tuple(violations[:10])
        if len(violations) > 10:
            head = head + (f"... ({len(violations) - 10} more)",)
        return GateResult(
            "L12-14",
            "FAIL",
            f"{len(violations)} sub-group hypothesis language hit(s) in §E4 prose",
            head,
        )
    return GateResult(
        "L12-14",
        "PASS",
        f"no sub-group hypothesis language in §E4 (scanned 5 fields × {len(blocks)} blocks)",
    )


# L12-15: aggregate-claim threshold expressions are single-line in §6.1-§6.4 + §E3.
_L12_15_BROKEN_RE = re.compile(
    r"(?:SVR|≥|≤|>=|<=|count)\s*\n\s*[0-9]", re.IGNORECASE
)


def gate_L12_15(state: HarnessState) -> GateResult:
    """Threshold expressions must not break across newlines in scoped sections.

    Scope: §6.1 + §6.2 (incl. subsections) + §6.3 + §6.4 + §E3.
    §E4 DSL expressions in backtick-fenced content are NOT in scope.
    """
    assert state.expectations_text is not None
    scoped_headers = (
        "## §6.1 ",
        "## §6.2 ",
        "## §6.3 ",
        "## §6.4 ",
        "## §E3 ",
    )
    violations: list[str] = []
    for header in scoped_headers:
        body = _section_body(state.expectations_text, (header,))
        if not body:
            continue
        for m in _L12_15_BROKEN_RE.finditer(body):
            snippet = m.group(0).replace("\n", "\\n")
            violations.append(f'section="{header.strip()}" snippet="{snippet}"')
    if violations:
        head = tuple(violations[:10])
        if len(violations) > 10:
            head = head + (f"... ({len(violations) - 10} more)",)
        return GateResult(
            "L12-15",
            "FAIL",
            f"{len(violations)} threshold expression(s) broken across newlines",
            head,
        )
    return GateResult(
        "L12-15",
        "PASS",
        "all aggregate-claim threshold expressions single-line in §6.1-§6.4 + §E3",
    )


def gate_L12_16(state: HarnessState) -> GateResult:
    """§Position 116 Treatment must reference call_116_live_call_record.json."""
    assert state.expectations_text is not None
    body = _section_body(state.expectations_text, ("## Position 116 Treatment ",))
    if not body:
        return GateResult("L12-16", "FAIL", "§Position 116 Treatment section not found")
    if "call_116_live_call_record.json" not in body:
        return GateResult(
            "L12-16",
            "FAIL",
            "§Position 116 Treatment section missing 'call_116_live_call_record.json' reference",
        )
    return GateResult("L12-16", "PASS", "§Position 116 Treatment references call_116_live_call_record.json")


def gate_L12_17(state: HarnessState) -> GateResult:
    """Universe A / B references cite label_universe_analysis.json + count consistency."""
    assert state.expectations_text is not None
    text = state.expectations_text
    issues: list[str] = []
    if not re.search(r"Universe A", text):
        issues.append("no 'Universe A' reference found")
    if not re.search(r"Universe B", text):
        issues.append("no 'Universe B' reference found")
    if "label_universe_analysis.json" not in text:
        issues.append("no 'label_universe_analysis.json' reference found")
    # Count drift: hard-coded counts UA n=29 and UB n=199 must appear in
    # the Label Universes section.
    body = _section_body(text, ("## Label Universes",))
    if not re.search(r"n=29\b", body):
        issues.append("Label Universes section missing 'n=29' for Universe A")
    if not re.search(r"n=199\b", body):
        issues.append("Label Universes section missing 'n=199' for Universe B")
    # Cross-check against label_universe_analysis.json universe sizes.
    data, err = _load_json_artifact(LABEL_UNIVERSE, "L12-17")
    if err:
        return err
    ua = data.get("universe_a") or {}
    ub = data.get("universe_b") or {}

    def _size_of(u: Any) -> int | None:
        if isinstance(u, dict):
            for k in ("size", "n", "count"):
                if isinstance(u.get(k), int):
                    return u[k]
            for k in ("positions", "members", "candidates"):
                v = u.get(k)
                if isinstance(v, list):
                    return len(v)
        if isinstance(u, list):
            return len(u)
        return None

    ua_size = _size_of(ua)
    ub_size = _size_of(ub)
    if ua_size is not None and ua_size != 29:
        issues.append(f"label_universe_analysis.json universe_a size={ua_size}, expected 29")
    if ub_size is not None and ub_size != 199:
        issues.append(f"label_universe_analysis.json universe_b size={ub_size}, expected 199")
    if issues:
        return GateResult("L12-17", "FAIL", f"{len(issues)} Universe A/B reference issues", tuple(issues))
    return GateResult(
        "L12-17",
        "PASS",
        "Universe A (n=29) / Universe B (n=199) cite label_universe_analysis.json; no count drift",
    )


def gate_FMT_01(state: HarnessState) -> GateResult:
    blocks = get_e4_blocks(state)
    if len(blocks) != 20:
        return GateResult("FMT-01", "FAIL", f"§E4 per-candidate block count = {len(blocks)}, expected 20")
    return GateResult("FMT-01", "PASS", "§E4 per-candidate block count = 20")


# FMT-03 SVR bucket-label rubric.
_VALID_BUCKETS = ("LOW", "MODERATE-LOW", "MEDIUM", "MODERATE-HIGH", "HIGH")
_BUCKET_TOKEN_RE = re.compile(r"\b(LOW|MODERATE-LOW|MEDIUM|MODERATE-HIGH|HIGH)\b")


def gate_FMT_03(state: HarnessState) -> GateResult:
    """SVR bucket labels in §E3 grid rows + §E4 field 4 match rubric."""
    assert state.expectations_text is not None
    issues: list[str] = []
    # §E3 grids: scan tier 1 + tier 2 grid table-row 'Expected 2d bucket' col.
    e3_body = _section_body(state.expectations_text, ("## §E3 ",))
    for line in e3_body.splitlines():
        if not _GRID_ROW_RE.match(line):
            continue
        # Expected bucket is column 5 (1-indexed) in Tier 1; column 4 in Tier 2.
        # Pull all bucket-token matches; reject any that's outside _VALID_BUCKETS.
        for tok in _BUCKET_TOKEN_RE.findall(line):
            if tok not in _VALID_BUCKETS:
                issues.append(f"§E3 grid row contains non-rubric bucket '{tok}': {line[:80]}")
    # §E4 field 4 (SVR expectation.).
    blocks = get_e4_blocks(state)
    for pos in sorted(blocks):
        block_text, _, _ = blocks[pos]
        body = _extract_field_text(block_text, "SVR expectation.")
        if not body:
            continue
        for tok in _BUCKET_TOKEN_RE.findall(body):
            if tok not in _VALID_BUCKETS:
                issues.append(f"§E4 pos={pos} 'SVR expectation.' has non-rubric bucket '{tok}'")
    if issues:
        head = tuple(issues[:10])
        if len(issues) > 10:
            head = head + (f"... ({len(issues) - 10} more)",)
        return GateResult("FMT-03", "FAIL", f"{len(issues)} SVR bucket-label rubric violations", head)
    return GateResult("FMT-03", "PASS", "SVR bucket labels match rubric in §E3 grids + §E4 field 4")


def gate_FMT_04(state: HarnessState) -> GateResult:
    """OR-bucket syntax: §E3 grid only, positions ⊆ {72,74,83,138}, pairs ⊆ sealed.
    §E4 must contain no OR-bucket disjunctions."""
    assert state.expectations_text is not None
    e3_body = _section_body(state.expectations_text, ("## §E3 ",))
    # Per-line scan of §E3 grid rows for OR-bucket pairs.
    pair_re = re.compile(
        r"\b(LOW|MODERATE-LOW|MODERATE-HIGH|HIGH)\s+or\s+(LOW|MODERATE-LOW|MODERATE-HIGH|HIGH)\b"
    )
    issues: list[str] = []
    e3_or_positions: set[int] = set()
    e3_or_pairs: set[tuple[str, str]] = set()
    for line in e3_body.splitlines():
        m_pos = _GRID_ROW_RE.match(line)
        if not m_pos:
            continue
        pos = int(m_pos.group(1))
        for pair_match in pair_re.finditer(line):
            pair = (pair_match.group(1), pair_match.group(2))
            e3_or_positions.add(pos)
            e3_or_pairs.add(pair)
            if pos not in E3_OR_BUCKET_POSITIONS:
                issues.append(f"§E3 grid pos={pos} has OR-bucket '{pair[0]} or {pair[1]}' (forbidden position)")
            if pair not in E3_OR_BUCKET_PAIRS:
                issues.append(f"§E3 grid pos={pos} has unsealed OR-bucket pair '{pair[0]} or {pair[1]}'")
    # §E4 must contain no OR-buckets in any field.
    blocks = get_e4_blocks(state)
    for pos in sorted(blocks):
        block_text, _, _ = blocks[pos]
        for pair_match in pair_re.finditer(block_text):
            pair = (pair_match.group(1), pair_match.group(2))
            issues.append(f"§E4 pos={pos} contains OR-bucket disjunction '{pair[0]} or {pair[1]}' (forbidden)")
    if issues:
        head = tuple(issues[:10])
        if len(issues) > 10:
            head = head + (f"... ({len(issues) - 10} more)",)
        return GateResult("FMT-04", "FAIL", f"{len(issues)} OR-bucket syntax violations", head)
    return GateResult(
        "FMT-04",
        "PASS",
        f"§E3 OR-buckets confined to positions {sorted(e3_or_positions)} and sealed pairs; §E4 single-bucket throughout",
    )


def gate_FMT_05(state: HarnessState) -> GateResult:
    """§E3 defects subsection present with required substrings + audit trail."""
    assert state.expectations_text is not None
    e3_body = _section_body(state.expectations_text, ("## §E3 ",))
    if "### Known Pre-Fire §E3 Defects (Path A documented)" not in e3_body:
        return GateResult(
            "FMT-05",
            "FAIL",
            "§E3 missing subsection '### Known Pre-Fire §E3 Defects (Path A documented)'",
        )
    # Subsection body bounded by next ### or end of §E3.
    lines = e3_body.splitlines()
    sub_start = next(
        (i for i, ln in enumerate(lines) if ln.startswith("### Known Pre-Fire §E3 Defects")),
        None,
    )
    sub_end = len(lines)
    for j in range(sub_start + 1, len(lines)):
        if lines[j].startswith("### "):
            sub_end = j
            break
    sub_body = "\n".join(lines[sub_start:sub_end])
    missing: list[str] = []
    for needle in ("Issue B", "Issue D", "Path A"):
        if needle not in sub_body:
            missing.append(f"missing literal '{needle}'")
    if not re.search(r"\b2026-04(?:-\d{2})?\b", sub_body):
        missing.append("missing audit-trail date '2026-04(-NN)'")
    if missing:
        return GateResult("FMT-05", "FAIL", f"{len(missing)} §E3 defects subsection issues", tuple(missing))
    return GateResult("FMT-05", "PASS", "§E3 defects subsection present with Issue B, Issue D, Path A, audit trail")


def gate_FMT_06(state: HarnessState) -> GateResult:
    """Verbatim presence of '## Remaining Candidates (Schema-Level Only)' header."""
    assert state.expectations_text is not None
    if "\n## Remaining Candidates (Schema-Level Only)\n" not in state.expectations_text + "\n":
        return GateResult("FMT-06", "FAIL", "header '## Remaining Candidates (Schema-Level Only)' missing or non-verbatim")
    return GateResult("FMT-06", "PASS", "'## Remaining Candidates (Schema-Level Only)' header present verbatim")


def gate_FMT_07(state: HarnessState) -> GateResult:
    """Verbatim presence of '## Position 116 Treatment — brief reference to Lock 1.5' header."""
    assert state.expectations_text is not None
    needle = "## Position 116 Treatment — brief reference to Lock 1.5"
    if needle not in state.expectations_text:
        return GateResult("FMT-07", "FAIL", f"header '{needle}' missing or non-verbatim")
    return GateResult("FMT-07", "PASS", f"'{needle}' header present verbatim")


_FMT_08_FIELDS = (
    "call_index",
    "position",
    "critic_status",
    "d7b_call_attempted",
    "d7b_error_category",
    "source_lifecycle_state",
    "source_valid_status",
    "actual_cost_usd",
    "input_tokens",
    "output_tokens",
    "skip_reason",
)


def gate_FMT_08(state: HarnessState) -> GateResult:
    """Pos 116 schema field-name strings present in §Position 116 Treatment section."""
    assert state.expectations_text is not None
    body = _section_body(state.expectations_text, ("## Position 116 Treatment ",))
    if not body:
        return GateResult("FMT-08", "FAIL", "§Position 116 Treatment section not found")
    missing = [f for f in _FMT_08_FIELDS if f'"{f}"' not in body]
    if missing:
        return GateResult(
            "FMT-08",
            "FAIL",
            f"{len(missing)}/{len(_FMT_08_FIELDS)} Lock 1.5 schema field names missing",
            tuple(missing),
        )
    return GateResult("FMT-08", "PASS", f"all {len(_FMT_08_FIELDS)} Lock 1.5 schema field-name strings present")


# FMT-09: '**three distinct counters**' bolding. The bold span legitimately
# wraps a line break in sealed content (verified: '**three\n  distinct counters**'),
# so the regex must tolerate intervening whitespace incl. \n.
_FMT_09_RE = re.compile(r"\*\*three\s+distinct\s+counters\*\*", re.IGNORECASE)


def gate_FMT_09(state: HarnessState) -> GateResult:
    """'**three distinct counters**' bolding present in §Position 116 Treatment."""
    assert state.expectations_text is not None
    body = _section_body(state.expectations_text, ("## Position 116 Treatment ",))
    if not body:
        return GateResult("FMT-09", "FAIL", "§Position 116 Treatment section not found")
    if not _FMT_09_RE.search(body):
        return GateResult(
            "FMT-09",
            "FAIL",
            "'**three distinct counters**' bolding not present in §Position 116 Treatment taxonomy paragraph",
        )
    return GateResult("FMT-09", "PASS", "'**three distinct counters**' bolding present in §Position 116 Treatment")


# ---------------------------------------------------------------------------
# Stub factory for unimplemented gates
# ---------------------------------------------------------------------------


def _stub(gate_id: str, phase: str) -> Callable[[HarnessState], GateResult]:
    """Factory for SKIP-returning stubs. phase names the target sub-task."""

    def _stub_impl(state: HarnessState) -> GateResult:
        return GateResult(gate_id, "SKIP", f"not yet implemented (deferred to Task {phase})")

    return _stub_impl


# ---------------------------------------------------------------------------
# Gate registry — 28 counted gates
# ---------------------------------------------------------------------------

# Order matches design spec §4 registry. Execution is sequential; L12-01
# FAIL short-circuits the run with exit 2 (see run_all_gates).

GATE_REGISTRY: list[tuple[str, Callable[[HarnessState], GateResult]]] = [
    ("L12-01", gate_L12_01),
    ("L12-02", gate_L12_02),
    ("L12-03", gate_L12_03),
    ("L12-04", gate_L12_04),
    ("L12-05", gate_L12_05),
    ("L12-06", gate_L12_06),
    ("L12-07", gate_L12_07),
    ("L12-08", gate_L12_08),
    ("L12-09", gate_L12_09),
    ("L12-10", gate_L12_10),
    ("L12-11", gate_L12_11),
    ("L12-12", gate_L12_12),
    ("L12-13", gate_L12_13),
    ("L12-14", gate_L12_14),
    ("L12-15", gate_L12_15),
    ("L12-16", gate_L12_16),
    ("L12-17", gate_L12_17),
    ("FMT-01", gate_FMT_01),
    ("FMT-02", gate_FMT_02),
    ("FMT-02b", gate_FMT_02b),
    ("FMT-03", gate_FMT_03),
    ("FMT-04", gate_FMT_04),
    ("FMT-05", gate_FMT_05),
    ("FMT-06", gate_FMT_06),
    ("FMT-07", gate_FMT_07),
    ("FMT-08", gate_FMT_08),
    ("FMT-09", gate_FMT_09),
    ("FMT-11", gate_FMT_11),
]

assert len(GATE_REGISTRY) == 28, f"GATE_REGISTRY must have 28 entries, found {len(GATE_REGISTRY)}"

# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------


def run_all_gates(state: HarnessState) -> None:
    # L12-01 runs first; FAIL cascades to immediate exit 2.
    first_id, first_fn = GATE_REGISTRY[0]
    assert first_id == "L12-01"
    result = first_fn(state)
    state.gate_results.append(result)
    if result.status == "FAIL":
        return  # harness caller detects and exits 2

    for gate_id, fn in GATE_REGISTRY[1:]:
        state.gate_results.append(fn(state))


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------


def format_results(state: HarnessState, runtime_s: float, strict: bool) -> tuple[int, str, str]:
    """
    Return (exit_code, stdout_text, stderr_text).
    stdout: banner, path warnings, PASS/FAIL/counted-WARN lines, summary.
    stderr: SKIP lines.
    """
    target = state.expectations_path.name if state.expectations_path else "<unresolved>"
    banner_lines = [
        "stage2d_self_check (Task 3b.3 complete: 28/28 gates active) | "
        f"target=docs/d7_stage2d/{target}",
        "─" * 78,
    ]

    # Path warnings (harness-level, not counted).
    path_warn_lines = [f"WARN {w.gate_id:<8} {w.message}" for w in state.path_warnings]

    # Tally and line emission.
    pass_n = warn_n = fail_n = skip_n = 0
    stdout_body: list[str] = []
    stderr_body: list[str] = []
    l12_01_failed = False

    for r in state.gate_results:
        if r.gate_id == "L12-01" and r.status == "FAIL":
            l12_01_failed = True
        # In --strict, counted-WARN promotes to FAIL.
        effective_status = r.status
        if strict and r.status == "WARN":
            effective_status = "FAIL"

        if effective_status == "PASS":
            pass_n += 1
            stdout_body.append(f"PASS {r.gate_id:<8} {r.message}")
        elif effective_status == "WARN":
            warn_n += 1
            stdout_body.append(f"WARN {r.gate_id:<8} {r.message}")
        elif effective_status == "FAIL":
            fail_n += 1
            stdout_body.append(f"FAIL {r.gate_id:<8} {r.message}")
            for v in r.violations:
                stdout_body.append(f"     {v}")
        elif effective_status == "SKIP":
            skip_n += 1
            stderr_body.append(f"SKIP {r.gate_id:<8} {r.message}")

    total = pass_n + warn_n + fail_n + skip_n
    harness_warn_n = len(state.path_warnings)
    summary = (
        f"SUMMARY ({total} counted gates): {pass_n} PASS, {warn_n} WARN, "
        f"{fail_n} FAIL, {skip_n} SKIP | {harness_warn_n} harness WARN | "
        f"runtime={runtime_s:.2f}s"
    )

    # Exit code policy:
    #   L12-01 FAIL → 2 (harness error; cascade halts execution).
    #   any other counted FAIL → 1.
    #   else → 0.
    if l12_01_failed:
        exit_code = 2
    elif fail_n > 0:
        exit_code = 1
    else:
        exit_code = 0
    exit_line = f"EXIT {exit_code}"

    stdout_text = "\n".join(
        banner_lines
        + path_warn_lines
        + stdout_body
        + ["─" * 78, summary, exit_line]
    ) + "\n"

    stderr_text = ""
    if stderr_body:
        stderr_text = "\n".join(
            [f"[stderr] {skip_n} gate(s) SKIPPED (upstream-dependent or not yet implemented):"]
            + stderr_body
        ) + "\n"

    return exit_code, stdout_text, stderr_text


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Stage 2d pre-fire self-check (Task 3b.3 complete: 28/28 gates active). "
            "See docs/d7_stage2d/stage2d_self_check_design_spec.md for gate catalog."
        )
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Promote counted-gate WARN to FAIL. Default: lenient.",
    )
    args = parser.parse_args()

    t0 = time.monotonic()
    state = HarnessState()
    run_all_gates(state)
    runtime_s = time.monotonic() - t0

    exit_code, stdout_text, stderr_text = format_results(state, runtime_s, args.strict)
    sys.stdout.write(stdout_text)
    if stderr_text:
        sys.stderr.write(stderr_text)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())

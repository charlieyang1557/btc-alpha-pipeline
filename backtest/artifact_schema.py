"""Per-artifact schema validation for b_c_extended_v1 and future analytical-methodology schema versions.

This module is the heavy-private-impl home for B-C-extended schema validation,
extracted from backtest/wf_lineage.py at T1.2 SEAL ratify per the C1-extract-pre-SEAL
Charlie register (2026-05-22). Public symbols are re-exported via backtest/wf_lineage.py
for consumer backward compatibility (no consumer code changes required at this cycle).

T1.3 additions (B-C-extended Scope-B Registry + API extension):
- canonicalize_execution_config_path(): pure function for path canonicalization
  per Contract 2.0.4 + plan v5 T1.3-B spec.
- LineageContext: frozen dataclass with 14 dataclass fields (13 Contract 2.0.5 + T_obs) per T1.3-D spec.
  Both symbols are co-located with COST_ANCHOR_ID_MAPPING for atomic-maintenance SSOT.

Contract references:
- Contract 2.0.2: schema version string + distinct validation branch
- Contract 2.0.4: cost_anchor_id mapping integrity (R3.1d §5.2)
- Contract 2.0.5: artifact path policy + per-bar linkage validation
- Plan v5 Sub-decision A: heavy-private-impl extraction realized at T1.2 SEAL ratify
  per C1-extract-pre-SEAL Charlie register 2026-05-22
- T1.3-A: registry migration (MIGRATION_COLUMNS entry already present)
- T1.3-B: canonicalize_execution_config_path() pure function spec
- T1.3-C: HYBRID parent_run_id conflict-check at write boundary
- T1.3-D: LineageContext frozen dataclass with 14 dataclass fields (13 Contract 2.0.5 + T_obs)

CONTRACT BOUNDARY: backtest.artifact_schema houses B-C-extended schema validation;
backtest.wf_lineage public surface preserved via re-exports for consumer backward
compat per C1-extract-pre-SEAL Charlie register.
"""
from __future__ import annotations

import dataclasses
import hashlib
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# B-C-extended Scope-B (T1.2): schema version for per-bar return series
# preservation artifacts (Contract 2.0.2 lock).
# CONTRACT GAP: future producer code (per B-C-narrow successor cycle binding per
# CLAUDE.md Phase Marker) will stamp this value on every artifact carrying
# returns_per_bar_path + moment summary fields (γ3, γ4, T_obs) per Contract 2.0.5.
# At T1.6 (infrastructure-only), no production code currently stamps this; see
# docs/decisions/B_C_EXTENDED_V1_SCHEMA_SPEC.md §1.5 for the full producer-chain
# status (validator/dataclass/constants/migration columns shipped; producer-stamp
# obligation deferred to B-C-narrow successor cycle).
ARTIFACT_SCHEMA_VERSION_B_C_EXTENDED_V1 = "b_c_extended_v1"

# B-C-extended analytical-methodology domain (per-bar artifact headers):
ACCEPTED_B_C_EXTENDED_SCHEMA_VERSIONS: tuple[str, ...] = (
    ARTIFACT_SCHEMA_VERSION_B_C_EXTENDED_V1,
)

# ---------------------------------------------------------------------------
# Cost anchor mapping (Contract 2.0.4, R3.1d §5.2).
#
# Maps canonicalized repo-relative POSIX execution_config_path to cost_anchor_id.
# 6-row mapping per R3.1d §5.2 (byte-equivalent against source document;
# verified at plan v5 PFR by both Codex and Advisor legs).
#
# Path canonicalization rule (T1.3 engine responsibility; T1.2 validation
# helper accepts already-canonicalized execution_config_path from artifact header):
#   repo_root_real = os.path.realpath(repo_root)
#   candidate_real = os.path.realpath(os.path.abspath(path))
#   if os.path.commonpath([repo_root_real, candidate_real]) != repo_root_real:
#       raise FailClosedError(...)  # commonpath-based containment check
#   key = os.path.relpath(candidate_real, repo_root_real).replace(os.sep, "/")
#
# Case-sensitivity: mapping keys are lowercase by convention. On case-insensitive
# filesystems (macOS HFS+/APFS default), exact-case match is required.
# Case-only mismatches FAIL CLOSED via mapping miss (intentional per plan v5 Fv5-1).
#
# Do NOT extend mapping at this cycle; future anchors require fresh Charlie
# register per R3.1d §5.2 discipline.
# ---------------------------------------------------------------------------
COST_ANCHOR_ID_MAPPING: dict[str, str] = {
    "config/execution.yaml": "legacy_perp_inspired_7bps_v0",
    "config/execution_phase4_07bps.yaml": "phase4_forward_07bps_v1",
    "config/execution_phase4_13bps.yaml": "phase4_forward_13bps_v1",
    "config/execution_phase4_15bps.yaml": "phase4_forward_15bps_v1",
    "config/execution_phase4_17bps.yaml": "phase4_forward_17bps_v1",
    "config/execution_phaseb_spot_15bps.yaml": "spot_realistic_15bps_v1",
}


# ---------------------------------------------------------------------------
# T1.3-B: Path canonicalization (co-located with COST_ANCHOR_ID_MAPPING SSOT)
# ---------------------------------------------------------------------------

# Default repo root: two parents up from this file (backtest/artifact_schema.py
# → backtest/ → <repo_root>). Matches experiment_registry.py:45 PROJECT_ROOT
# precedent.
_DEFAULT_REPO_ROOT = Path(__file__).resolve().parent.parent


def canonicalize_execution_config_path(
    path: "Path | str",
    *,
    repo_root: "Path | None" = None,
) -> str:
    """Canonicalize an execution config path to a repo-relative POSIX key.

    Implements the T1.3-B canonicalization rule per plan v5 Contract 2.0.4:
      1. Resolve repo root via os.path.realpath.
      2. If path is relative, anchor to repo_root FIRST (NOT os.path.abspath
         which anchors to CWD — that is the T1.3-B critical bug-catch per
         Codex v1 N1).
      3. Compute os.path.realpath of the candidate path.
      4. Containment check via os.path.commonpath (NOT str.startswith — the
         latter falsely admits /repo_rootX/file to /repo_root containment;
         per plan v5 Fv5-1 LOW inline-fix).
      5. Fail closed if path is outside repo root.
      6. Return os.path.relpath(candidate_real, repo_root_real) as POSIX
         string (replace os.sep with '/').
      7. Case-sensitivity: do NOT apply os.path.normcase. Mapping keys are
         lowercase; case-only mismatches FAIL CLOSED via mapping miss
         (intentional per plan v5 Fv5-1).

    This function does NOT perform the COST_ANCHOR_ID_MAPPING lookup itself;
    that is done at LineageContext construction or _write_to_registry.
    The function is a pure path-to-key transformer.

    Args:
        path: Absolute or relative path to the execution config YAML.
            Relative paths are resolved against repo_root (NOT CWD).
        repo_root: Repo root override. Defaults to the repository root
            inferred from this module's location (two directories up).

    Returns:
        POSIX repo-relative string key, e.g. "config/execution.yaml".

    Raises:
        ValueError: If path is outside repo_root (fail closed per Contract 2.0.4).
        TypeError: If path is None or not a str/Path.
    """
    if path is None:
        raise TypeError(
            "canonicalize_execution_config_path: path must be a str or Path, got None"
        )

    # FIX-M2: explicit guard for empty/whitespace-only paths.
    # Empty string passes Path('') → '.' (repo root) but the error message
    # would report '.' not '' (confusing). Guard here to produce a clear error.
    if not str(path).strip():
        raise ValueError(
            f"canonicalize_execution_config_path: empty or whitespace-only path is "
            f"not valid; received {path!r}. Provide a non-empty path to an execution "
            f"config YAML under the repository root."
        )

    # FIX-M2-extension: Path('') produces str '.' (truthy, bypasses the guard above).
    # Path('.') resolves to repo root itself — not a valid execution config path.
    # Detect both via the resolved string representation BEFORE Path() normalisation.
    # Using str(path) after stripping: '' and '.' are both invalid sentinels.
    # Note: str(Path('')) == '.', so we check str(path) == '.' for Path('') too.
    _path_str_raw = str(path)
    if _path_str_raw == "." or (isinstance(path, Path) and str(path) == "."):
        raise ValueError(
            f"canonicalize_execution_config_path: Path('') or Path('.') is not a "
            f"valid execution config path (resolves to repo root or CWD, not a "
            f"config file); received {path!r}. "
            f"Provide a non-empty path such as 'config/execution.yaml' "
            f"(FIX-M2-extension guard)."
        )

    resolved_root = Path(repo_root).resolve() if repo_root is not None else _DEFAULT_REPO_ROOT
    repo_root_real = os.path.realpath(str(resolved_root))

    # T1.3-B critical: resolve relative paths against repo_root BEFORE realpath.
    # os.path.abspath anchors to CWD which is bug-prone (Codex v1 N1).
    path_obj = Path(path)
    if not path_obj.is_absolute():
        path_obj = resolved_root / path_obj

    candidate_real = os.path.realpath(str(path_obj))

    # Containment check via commonpath (NOT str.startswith per plan v5 Fv5-1).
    try:
        common = os.path.commonpath([repo_root_real, candidate_real])
    except ValueError:
        # Windows: different drives raise ValueError in commonpath.
        raise ValueError(
            f"canonicalize_execution_config_path: path={str(path)!r} is outside "
            f"repo root={repo_root_real!r} (different drives; path-containment "
            f"violation, Contract 2.0.4 fail-closed clause)."
        )
    if common != repo_root_real:
        raise ValueError(
            f"canonicalize_execution_config_path: path={str(path)!r} resolves to "
            f"{candidate_real!r}, which is outside repo root={repo_root_real!r}. "
            f"Only paths under the repository root are valid execution config paths "
            f"(Contract 2.0.4 fail-closed clause). "
            f"Hint: pass a path under {repo_root_real!r}."
        )

    # Repo-relative POSIX key.
    rel = os.path.relpath(candidate_real, repo_root_real)
    return rel.replace(os.sep, "/")


# ---------------------------------------------------------------------------
# T1.3-D: LineageContext frozen dataclass (14 dataclass fields (13 Contract 2.0.5 + T_obs))
# ---------------------------------------------------------------------------

@dataclass(frozen=True, kw_only=True)
class LineageContext:
    """Frozen dataclass carrying 13 header/linkage fields plus T_obs (14 total).

    Encapsulates the per-artifact lineage context for new Phase B / Tier 5 /
    Tier 6 public callers. Passed as an opt-in kwarg to run_backtest(),
    run_regime_holdout(), and (indirectly) to _write_to_registry().

    Field count: exactly 14 dataclass fields. **The 14 dataclass fields comprise
    13 of the 14 Contract 2.0.5 header fields (artifact_schema_version is excluded
    per D2-b below) PLUS T_obs (a required-adjacent per-bar-content-shape attribute
    outside the Contract 2.0.5 14-field header table per
    `docs/decisions/B_C_EXTENDED_V1_SCHEMA_SPEC.md` §1.5b).**
    Verified by: ``len(dataclasses.fields(LineageContext)) == 14``.

    D2-b provenance asymmetry (accepted design): ``artifact_schema_version`` is
    NOT a LineageContext field (stays 14 fields). Future writer scripts will
    stamp ``artifact_schema_version`` onto the artifact JSON header from the
    module-level constant ``ARTIFACT_SCHEMA_VERSION_B_C_EXTENDED_V1`` (deferred
    to B-C-narrow successor cycle per CLAUDE.md Phase Marker binding condition;
    T1.6 ships infrastructure-only). The validator
    ``check_b_c_extended_semantics_or_raise`` is ready to read it from the
    artifact header dict at consumer time (T1.6 consumer-side validation fully
    operational; producer-side stamping deferred to B-C-narrow).
    This asymmetry is intentional: LineageContext carries lineage metadata, not
    schema discriminator; schema version is a producer-stamped header field.

    D1-b STRICT/LATE_FILL split:
    - STRICT fields (10): must be non-empty non-whitespace at __post_init__ time.
      Validated by FIX-T1.1-SYS-B1 symmetric validation in __post_init__.
    - LATE_FILL fields (2): returns_per_bar_path + returns_per_bar_sha256.
      Allowed empty at construction; T1.1 writer populates after artifact written.
      Validator (check_b_c_extended_semantics_or_raise) requires ALL 12 non-empty
      at consumption-time; __post_init__ only relaxes its own guard for LATE_FILL.

    13 required fields (str or int); parent_run_id is Optional[str] per B2-b:
    None valid for single-run callers without parent linkage;
    empty-string and whitespace-only FAIL CLOSED.

    __post_init__ discipline:
    - FIX-T1.1-SYS-B1: STRICT required-string validation (8 fields directly;
      execution_config_path via canonicalize_execution_config_path()).
    - FIX-T1.1-H1: T_obs > 0 symmetric validation.
    - B2-b parent_run_id validation: None valid; empty/whitespace FAIL CLOSED.
    - Canonicalize execution_config_path via canonicalize_execution_config_path()
      (T1.3-B function; uses object.__setattr__ since frozen blocks direct mutation).
    - Resolve cost_anchor_id via canonicalized path lookup in COST_ANCHOR_ID_MAPPING
      (fail closed on miss with structured error; object.__setattr__ for frozen set).

    CONTRACT BOUNDARY: LineageContext co-located with COST_ANCHOR_ID_MAPPING and
    canonicalize_execution_config_path for atomic-maintenance SSOT (all three live
    in backtest/artifact_schema.py). Public shim re-exported via backtest/wf_lineage.py.

    Attributes:
        run_id: UUID for this engine run (aliases registry runs.run_id).
        hypothesis_hash: DSL canonical hash per Contract 2.0.3 triple linkage.
        source_batch_id: Phase 2B batch UUID (aliases registry runs.batch_id).
        regime_key: Regime identity key (e.g. "v2.regime_holdout").
        engine_commit: Git SHA at engine-commit level.
        current_git_sha: Git SHA at full-repo level.
        execution_config_path: Canonicalized repo-relative POSIX path per
            Contract 2.0.4. Stored after __post_init__ canonicalization.
        execution_config_sha256: Content-addressable hash of execution config.
        parquet_data_sha256: Content-addressable hash of source data parquet.
        cost_anchor_id: Resolved from execution_config_path via
            COST_ANCHOR_ID_MAPPING. Set by __post_init__.
        returns_per_bar_path: Relative path to per-bar returns parquet
            (relative to artifact's containing directory).
        returns_per_bar_sha256: SHA256 of per-bar artifact for integrity.
        T_obs: Count of finite per-bar return observations (positive int).
        parent_run_id: Optional parent run UUID. None valid for single-run
            callers without parent linkage (B2-b). Empty/whitespace FAIL CLOSED.
    """

    # Contract 2.0.5 field 2 (field 1 is artifact_schema_version, producer-stamped)
    run_id: str
    # Contract 2.0.5 field 3
    hypothesis_hash: str
    # Contract 2.0.5 field 4
    source_batch_id: str
    # Contract 2.0.5 field 6
    regime_key: str
    # Contract 2.0.5 field 7
    engine_commit: str
    # Contract 2.0.5 field 8
    current_git_sha: str
    # Contract 2.0.5 field 9 — stored as canonicalized POSIX string after __post_init__
    execution_config_path: str
    # Contract 2.0.5 field 10
    execution_config_sha256: str
    # Contract 2.0.5 field 11
    parquet_data_sha256: str
    # Contract 2.0.5 field 12 — resolved by __post_init__ via COST_ANCHOR_ID_MAPPING.
    # Default sentinel "" is overwritten by __post_init__ before the instance
    # is returned to the caller (object.__setattr__ on frozen field).
    # Callers MUST NOT pass cost_anchor_id explicitly; it is always derived from
    # execution_config_path at construction time.
    cost_anchor_id: str = dataclasses.field(default="")
    # Contract 2.0.5 field 13
    returns_per_bar_path: str
    # Contract 2.0.5 field 14
    returns_per_bar_sha256: str
    # T_obs is not in the 14-field header table but is required for artifact validation;
    # included here as field 13-equivalent for moment + T_obs linkage.
    T_obs: int
    # Contract 2.0.5 field 5 — Optional[str] per B2-b
    parent_run_id: "str | None"

    def __post_init__(self) -> None:
        """Validate, canonicalize execution_config_path, and resolve cost_anchor_id.

        Called automatically by dataclass __init__. Uses object.__setattr__
        to mutate frozen fields (the only legitimate mutation point for frozen
        dataclasses in __post_init__).

        Validation order:
        1. FIX-T1.1-SYS-B1: STRICT required-string field validation — each of the
           10 STRICT fields (per _BCE_REQUIRED_STRING_FIELDS_STRICT) must be a
           non-empty non-whitespace string. execution_config_path is validated
           indirectly by canonicalize_execution_config_path() which raises on empty.
           cost_anchor_id is set by mapping lookup (not directly validated here).
           LATE_FILL fields (returns_per_bar_path, returns_per_bar_sha256) are
           EXCLUDED from this check — allowed empty at construction per D1-b.
        2. FIX-T1.1-H1: T_obs symmetric validation.
        3. B2-b: parent_run_id Optional[str] validation.
        4. T1.3-B: canonicalize execution_config_path.
        5. COST_ANCHOR_ID_MAPPING lookup to resolve cost_anchor_id.

        Raises:
            ValueError: If any STRICT field is empty/whitespace (FIX-T1.1-SYS-B1),
                if parent_run_id is empty/whitespace (B2-b FAIL CLOSED),
                if T_obs is None or <= 0 (FIX-T1.1-H1 + FIX-T1.1-SYS2-B1: None bypass
                closed; T_obs is strictly-required positive integer),
                or if execution_config_path is not in COST_ANCHOR_ID_MAPPING.
        """
        # FIX-T1.1-SYS-B1 + FIX-T1.1-SYS2-M1: STRICT required-string field validation.
        # Mirrors check_b_c_extended_semantics_or_raise consumption-time validation
        # on the producer side (LineageContext construction). Each STRICT field must
        # be a non-empty non-whitespace string at construction time.
        #
        # FIX-T1.1-SYS2-M1: _strict_direct is now a module-level constant derived from
        # _BCE_REQUIRED_STRING_FIELDS_STRICT minus _INDIRECT_STRICT_FIELDS (SSOT).
        # Previously it was an inline tuple that could drift from the module-level
        # constant. See _INDIRECT_STRICT_FIELDS docstring for the derivation rule.
        #
        # Excludes:
        # - execution_config_path: in _INDIRECT_STRICT_FIELDS; validated below via
        #   canonicalize_execution_config_path() which raises on empty/whitespace.
        # - cost_anchor_id: in _INDIRECT_STRICT_FIELDS; resolved by mapping lookup.
        # - returns_per_bar_path, returns_per_bar_sha256: LATE_FILL per D1-b;
        #   allowed empty at construction.
        # - parent_run_id: Optional[str] per B2-b; handled separately below.
        # - T_obs: int field, not string; handled separately below.
        for _field in _strict_direct:  # module-level constant (FIX-T1.1-SYS2-M1)
            _val = getattr(self, _field)
            if not isinstance(_val, str) or not _val.strip():
                raise ValueError(
                    f"LineageContext.{_field}: must be a non-empty non-whitespace "
                    f"string, got {_val!r}. "
                    f"(FIX-T1.1-SYS-B1: symmetric with "
                    f"check_b_c_extended_semantics_or_raise validator's "
                    f"required-string validation.)"
                )

        # FIX-T1.1-H1 + FIX-T1.1-SYS2-B1: T_obs strictly-required positive int.
        # FIX-T1.1-H1 (prior): validator rejects T_obs=0; LC __post_init__ had `is not None`
        # guard that silently accepted T_obs=None.
        # FIX-T1.1-SYS2-B1: close the None bypass — T_obs is a strictly-required positive
        # integer (not optional). None must raise ValueError at construction time, symmetric
        # with check_b_c_extended_semantics_or_raise which requires T_obs > 0 (positive int).
        t_obs = self.T_obs
        if t_obs is None or not isinstance(t_obs, int) or isinstance(t_obs, bool) or t_obs <= 0:
            raise ValueError(
                f"LineageContext.T_obs: required positive integer (> 0), got {t_obs!r}. "
                f"T_obs represents the count of finite per-bar return observations; "
                f"None, zero, negative values, and booleans are rejected. "
                f"(FIX-T1.1-SYS2-B1: T_obs is strictly-required; None bypass closed; "
                f"symmetric with check_b_c_extended_semantics_or_raise T_obs > 0 requirement.)"
            )

        # FIX-T1.1-SYS4-LATE-FILL: closed-set LATE_FILL pair invariant.
        # Closes the (None, ""), ("", None), ("", non_empty), (non_empty, ""),
        # whitespace-only, and non-string third-state bypasses at producer
        # construction. Symmetric with check_b_c_extended_semantics_or_raise
        # consumption-time requirement that LATE_FILL fields be non-empty
        # non-whitespace strings at consumption.
        #
        # Allowed states are exactly two (closed set):
        #   - Pre-fill (deferred): ("", "")  — both exact empty strings
        #   - Filled:              (non_empty_non_whitespace_str,
        #                           non_empty_non_whitespace_str)
        #
        # Producer must use object.__setattr__ to transition atomically from
        # deferred → filled (frozen dataclass blocks direct assignment).
        #
        # Anti-recurrence rationale: 5-iteration recurrence pattern within
        # T1.1 arc (SYS-fix-1 / SYS2 / SYS3-B1 / SYS3-B2 / this fix) traced
        # to producer-side absence of LATE_FILL invariant — write-boundary mirrors
        # compensated case-by-case rather than closing at producer.
        # This invariant is the structural closure; write-boundary mirrors
        # remain as defense-in-depth (engine.py:1133-1137 doctrine).
        _bar_path = self.returns_per_bar_path
        _bar_sha = self.returns_per_bar_sha256
        if not (isinstance(_bar_path, str) and isinstance(_bar_sha, str)):
            raise ValueError(
                f"LineageContext LATE_FILL pair invariant: "
                f"returns_per_bar_path and returns_per_bar_sha256 must both "
                f"be str; got returns_per_bar_path={_bar_path!r} "
                f"type={type(_bar_path).__name__!r}, "
                f"returns_per_bar_sha256={_bar_sha!r} "
                f"type={type(_bar_sha).__name__!r}. "
                f"(FIX-T1.1-SYS4-LATE-FILL: closed-set string-type invariant.)"
            )
        _deferred = (_bar_path == "" and _bar_sha == "")
        _filled = (_bar_path.strip() != "" and _bar_sha.strip() != "")
        if not (_deferred or _filled):
            raise ValueError(
                f"LineageContext LATE_FILL pair invariant failed: "
                f"valid states are exactly ('', '') (deferred) or "
                f"(non-empty non-whitespace str, non-empty non-whitespace str) "
                f"(filled); got returns_per_bar_path={_bar_path!r}, "
                f"returns_per_bar_sha256={_bar_sha!r}. "
                f"(FIX-T1.1-SYS4-LATE-FILL: closed-set pair-state invariant.)"
            )

        # B2-b: empty-string and whitespace-only FAIL CLOSED.
        pid = self.parent_run_id
        if pid is not None and (not isinstance(pid, str) or not pid.strip()):
            raise ValueError(
                f"LineageContext.parent_run_id: empty or whitespace-only string is "
                f"not valid; use None for callers without parent linkage "
                f"(B2-b: empty-string and whitespace-only FAIL CLOSED). "
                f"Got: {pid!r}"
            )

        # Canonicalize execution_config_path via T1.3-B function.
        # This also validates execution_config_path (raises ValueError on empty/whitespace).
        raw_path = self.execution_config_path
        canonicalized = canonicalize_execution_config_path(raw_path)
        # object.__setattr__ required: frozen dataclass blocks direct assignment.
        object.__setattr__(self, "execution_config_path", canonicalized)

        # Resolve cost_anchor_id from canonicalized path via COST_ANCHOR_ID_MAPPING.
        expected_anchor = COST_ANCHOR_ID_MAPPING.get(canonicalized)
        if expected_anchor is None:
            mapping_table = "; ".join(
                f"{k!r} → {v!r}" for k, v in COST_ANCHOR_ID_MAPPING.items()
            )
            raise ValueError(
                f"LineageContext: execution_config_path={canonicalized!r} is not "
                f"in COST_ANCHOR_ID_MAPPING (R3.1d §5.2). "
                f"Known mappings: {mapping_table}. "
                f"Update R3.1d §5.2 mapping for new anchor or contact human "
                f"approval before extending mapping."
            )
        object.__setattr__(self, "cost_anchor_id", expected_anchor)

    def revalidate_for_write(self) -> None:
        """Re-validate ALL 14 dataclass fields (13 Contract 2.0.5 + T_obs) against post-construction tampering.

        Called by _write_to_registry before copying LC fields into run_data.
        Closes the asymmetry where object.__setattr__(lc, field, bad_value) bypasses
        the frozen-dataclass guard and reaches the registry without revalidation
        (Codex v8 BLOCKING; cycle-pattern observation adjacent to §35).

        This is defense-in-depth at the LC layer — write-boundary mirrors at
        engine.py remain as belt-and-suspenders per project doctrine.

        Raises:
            ValueError: with "revalidate_for_write" tag on any field tampering.
        """
        # 8 direct STRICT fields: re-run isinstance + non-empty + non-whitespace check.
        for _field in _strict_direct:
            _val = getattr(self, _field)
            if not isinstance(_val, str) or not _val.strip():
                raise ValueError(
                    f"LineageContext.revalidate_for_write: STRICT field "
                    f"{_field!r}={_val!r} is invalid (must be non-empty "
                    f"non-whitespace str). Post-construction tampering via "
                    f"object.__setattr__ detected. (FIX-T1.1-SYS5-REVALIDATE: "
                    f"closes 5th asymmetry class — direct STRICT field tamper.)"
                )

        # T_obs: positive int, not bool.
        t_obs = self.T_obs
        if isinstance(t_obs, bool) or not isinstance(t_obs, int) or t_obs <= 0:
            raise ValueError(
                f"LineageContext.revalidate_for_write: T_obs={t_obs!r} invalid "
                f"(must be positive int, not bool). "
                f"(FIX-T1.1-SYS5-REVALIDATE.)"
            )

        # parent_run_id: Optional[str], non-empty non-whitespace if not None.
        pid = self.parent_run_id
        if pid is not None and (not isinstance(pid, str) or not pid.strip()):
            raise ValueError(
                f"LineageContext.revalidate_for_write: parent_run_id={pid!r} "
                f"invalid (must be None or non-empty non-whitespace str). "
                f"(FIX-T1.1-SYS5-REVALIDATE.)"
            )

        # execution_config_path: idempotency check (must equal canonicalized form).
        raw_path = self.execution_config_path
        try:
            canonicalized = canonicalize_execution_config_path(raw_path)
        except (ValueError, TypeError) as e:
            raise ValueError(
                f"LineageContext.revalidate_for_write: execution_config_path="
                f"{raw_path!r} fails canonicalization. {e} "
                f"(FIX-T1.1-SYS5-REVALIDATE.)"
            ) from e
        if canonicalized != raw_path:
            raise ValueError(
                f"LineageContext.revalidate_for_write: execution_config_path="
                f"{raw_path!r} is not in canonical form (expected "
                f"{canonicalized!r}). Post-construction tampering detected. "
                f"(FIX-T1.1-SYS5-REVALIDATE.)"
            )

        # cost_anchor_id: consistency check vs mapping lookup.
        expected_anchor = COST_ANCHOR_ID_MAPPING.get(canonicalized)
        if expected_anchor is None or self.cost_anchor_id != expected_anchor:
            raise ValueError(
                f"LineageContext.revalidate_for_write: cost_anchor_id="
                f"{self.cost_anchor_id!r} does not match "
                f"COST_ANCHOR_ID_MAPPING[{canonicalized!r}]={expected_anchor!r}. "
                f"Post-construction tampering detected. "
                f"(FIX-T1.1-SYS5-REVALIDATE.)"
            )

        # LATE_FILL pair: closed-set invariant (same as SYS4 __post_init__).
        _bar_path = self.returns_per_bar_path
        _bar_sha = self.returns_per_bar_sha256
        if not (isinstance(_bar_path, str) and isinstance(_bar_sha, str)):
            raise ValueError(
                f"LineageContext.revalidate_for_write: LATE_FILL pair type "
                f"invalid (got types {type(_bar_path).__name__!r}, "
                f"{type(_bar_sha).__name__!r}). "
                f"(FIX-T1.1-SYS5-REVALIDATE.)"
            )
        _deferred = (_bar_path == "" and _bar_sha == "")
        _filled = (_bar_path.strip() != "" and _bar_sha.strip() != "")
        if not (_deferred or _filled):
            raise ValueError(
                f"LineageContext.revalidate_for_write: LATE_FILL pair state "
                f"invalid (returns_per_bar_path={_bar_path!r}, "
                f"returns_per_bar_sha256={_bar_sha!r}). "
                f"(FIX-T1.1-SYS5-REVALIDATE.)"
            )


class BCExtendedSchemaValidationError(ValueError):
    """Raised by check_b_c_extended_semantics_or_raise on per-field failures.

    B3-b lock: subclass of ValueError (LSP) so existing 'except ValueError'
    consumers are unaffected. Carries a structured list of failure strings
    as the 'errors' attribute for programmatic inspection.

    Per B1-c hybrid validation order, this exception is raised in Phase 2
    (collect-all on per-field failures). Phase 1 structural failures raise
    plain ValueError immediately before Phase 2 runs.

    Args:
        errors: List of human-readable failure descriptions. Each entry
            identifies the failing field name and the reason for failure.
        artifact_path: Optional artifact path, included in str() for
            diagnostics.
    """

    def __init__(
        self,
        errors: list[str],
        artifact_path: str | Path | None = None,
    ) -> None:
        self.errors = errors
        where = f" at {artifact_path}" if artifact_path else ""
        summary_msg = (
            f"B-C-extended artifact{where} failed schema validation "
            f"({len(errors)} error(s)): " + "; ".join(errors)
        )
        super().__init__(summary_msg)


# Required string fields for b_c_extended_v1 artifacts (12 total per Contract 2.0.5).
# parent_run_id is validated separately via B2-b Optional[string] semantics.
# T_obs is validated as an integer, not a string.
#
# D1-b STRICT/LATE_FILL split (FIX-T1.1-SYS-B1):
#
# STRICT fields (10): required non-empty at LineageContext.__post_init__ construction.
# All 10 must be non-empty non-whitespace strings at construction time.
# Producer fail-fast at LineageContext(**kwargs) time — symmetric with
# check_b_c_extended_semantics_or_raise consumption-time validation.
#
# LATE_FILL fields (2): allowed empty at construction; populated after
# per-bar artifact is written (T1.1 writer sets via object.__setattr__).
# Validator (check_b_c_extended_semantics_or_raise) continues to require
# ALL 12 non-empty at consumption-time. Only the __post_init__ guard is
# relaxed for these two fields.
#
# cost_anchor_id is auto-resolved by __post_init__ from execution_config_path
# via COST_ANCHOR_ID_MAPPING — it is a STRICT field (always non-empty after
# __post_init__) but not validated directly by __post_init__ (it's set by
# the mapping lookup; mapping miss raises ValueError).
_BCE_REQUIRED_STRING_FIELDS_STRICT: tuple[str, ...] = (
    "run_id",
    "hypothesis_hash",
    "source_batch_id",
    "regime_key",
    "engine_commit",
    "current_git_sha",
    "execution_config_path",
    "execution_config_sha256",
    "parquet_data_sha256",
    "cost_anchor_id",
)

# LATE_FILL: allowed empty at LC construction; required non-empty at consumption.
_BCE_REQUIRED_STRING_FIELDS_LATE_FILL: tuple[str, ...] = (
    "returns_per_bar_path",
    "returns_per_bar_sha256",
)

# FIX-T1.1-SYS2-M1: SSOT derivation for _strict_direct.
#
# _INDIRECT_STRICT_FIELDS: STRICT fields NOT validated directly by the inline loop
# in LineageContext.__post_init__. Each of these is handled by a separate mechanism:
#   - execution_config_path: validated indirectly by canonicalize_execution_config_path()
#     which raises ValueError on empty/whitespace paths.
#   - cost_anchor_id: resolved/set by COST_ANCHOR_ID_MAPPING lookup (raises on miss);
#     never passed directly by callers (default="" is overwritten by __post_init__).
#
# CONTRACT BOUNDARY: _INDIRECT_STRICT_FIELDS is the SSOT for the indirect-validation
# exclusion list. _strict_direct (used in __post_init__) is DERIVED from
# _BCE_REQUIRED_STRING_FIELDS_STRICT minus _INDIRECT_STRICT_FIELDS.
# Any future addition to _BCE_REQUIRED_STRING_FIELDS_STRICT automatically propagates
# into _strict_direct UNLESS explicitly placed in _INDIRECT_STRICT_FIELDS.
# Pin-test in tests/test_t1_1_sys_fix.py::TestSys2M1StrictDirectSSOT verifies alignment.
_INDIRECT_STRICT_FIELDS: tuple[str, ...] = (
    "execution_config_path",
    "cost_anchor_id",
)

# Derive _strict_direct from SSOT: STRICT fields minus indirect-validated fields.
# This is computed at module load and used in LineageContext.__post_init__.
# Pin assertion: set(_strict_direct) | set(_INDIRECT_STRICT_FIELDS) == set(_BCE_REQUIRED_STRING_FIELDS_STRICT)
# (enforced by TestSys2M1StrictDirectSSOT.test_ssot_pin_strict_direct_union_indirect_equals_strict)
_strict_direct: tuple[str, ...] = tuple(
    f for f in _BCE_REQUIRED_STRING_FIELDS_STRICT if f not in _INDIRECT_STRICT_FIELDS
)

# Original 12-field constant preserved for consumer backward compat.
# check_b_c_extended_semantics_or_raise uses this at consumption-time (still
# requires ALL 12 non-empty at consumption — LATE_FILL fields are only relaxed
# at construction time in __post_init__).
_BCE_REQUIRED_STRING_FIELDS: tuple[str, ...] = (
    *_BCE_REQUIRED_STRING_FIELDS_STRICT[:-1],  # 9 STRICT fields (excludes cost_anchor_id)
    "cost_anchor_id",
    *_BCE_REQUIRED_STRING_FIELDS_LATE_FILL,  # 2 LATE_FILL fields
)


def check_b_c_extended_semantics_or_raise(
    summary: dict,
    *,
    artifact_path: str | Path | None = None,
) -> None:
    """Consumer-side: validate a b_c_extended_v1 artifact header.

    Implements B1-c hybrid validation order (per plan v5 Sub-decision B lock):

    **Phase 1 (fail-fast on structural failures):** Raises immediately on:
    - artifact_schema_version missing or not in ACCEPTED_B_C_EXTENDED_SCHEMA_VERSIONS
    - returns_per_bar_path path-confinement violations (../escape attacks,
      absolute paths that escape the artifact's containing directory)

    **Phase 2 (collect-all on per-field failures):** Within a successful
    structural pass, accumulates all per-field failures, then raises a
    single BCExtendedSchemaValidationError with the structured failure list.

    Per-field checks (Phase 2):
    - All 12 required string fields: present, string type, non-empty/non-whitespace
    - parent_run_id: key must be present; value must be None, or non-empty
      non-whitespace string (B2-b; FIX-M1: whitespace-only FAIL CLOSED)
    - T_obs: present, integer type, positive (> 0)
    - cost_anchor_id consistency: execution_config_path must be in
      COST_ANCHOR_ID_MAPPING and cost_anchor_id must match the mapped value
    - Per-bar artifact linkage: file-exists (is_file()), SHA256-recompute
      (chunked 64KB streaming), T_obs-alignment (finite-only count)

    Deferred validations (require separate Charlie register-event):

    CONTRACT GAP: regime_key validation against REGIME_KEY_LABEL_MAPPING is
    deferred. This helper accepts any non-empty string for regime_key. The
    sibling helper check_evaluation_semantics_or_raise validates regime_key
    against REGIME_KEY_LABEL_MAPPING; this asymmetry is intentional at T1.2
    and must be resolved at a separate register-event per anti-pre-emption
    discipline. Trigger condition: when regime_key validation is needed for
    b_c_extended_v1 artifacts, add the check here and update this marker.

    CONTRACT GAP: execution_config_path canonicalization is deferred to T1.3
    engine _write_to_registry(). This helper accepts already-canonicalized
    execution_config_path from the artifact header. The canonicalization rule
    (repo_root commonpath containment + relpath + POSIX) belongs to the
    producer side (T1.3 engine). If a non-canonical path is passed here,
    the COST_ANCHOR_ID_MAPPING lookup fails closed (defensive). Trigger
    condition: when T1.3 engine is modified to write execution_config_path,
    add canonicalization there and add a corresponding test in T1.3's test file.

    Raises:
        ValueError: (Phase 1) On structural failures (missing schema_version,
            wrong domain, path-confinement violation).
        BCExtendedSchemaValidationError: (Phase 2) On any per-field failure;
            carries structured 'errors' list attribute. Is a ValueError subclass.

    Args:
        summary: The artifact header dict loaded from holdout_summary.json
            or an equivalent per-bar artifact header.
        artifact_path: Optional path to the source file. Used to resolve
            returns_per_bar_path (relative to artifact_path.parent) and
            included in error messages for diagnostics.
    """
    # Normalize artifact_path for path resolution and diagnostics.
    if artifact_path is not None:
        artifact_path = Path(artifact_path)

    where = f" at {artifact_path}" if artifact_path else ""

    # ------------------------------------------------------------------
    # Phase 1: fail-fast structural checks.
    # ------------------------------------------------------------------

    # Guard against non-dict inputs (type safety).
    if not isinstance(summary, dict):
        raise TypeError(
            f"summary must be a dict, got {type(summary).__name__!r}{where}"
        )

    # 1a. artifact_schema_version presence and domain membership.
    schema_version = summary.get("artifact_schema_version")
    if schema_version is None:
        raise ValueError(
            f"B-C-extended artifact{where}: missing 'artifact_schema_version' "
            f"field. Expected one of {ACCEPTED_B_C_EXTENDED_SCHEMA_VERSIONS!r}. "
            f"Refusing to validate artifact without schema discriminator."
        )
    if schema_version not in ACCEPTED_B_C_EXTENDED_SCHEMA_VERSIONS:
        accepted_str = ", ".join(repr(v) for v in ACCEPTED_B_C_EXTENDED_SCHEMA_VERSIONS)
        raise ValueError(
            f"B-C-extended artifact{where}: unrecognized or wrong-domain "
            f"artifact_schema_version={schema_version!r}. "
            f"Expected one of ({accepted_str}). "
            f"For evaluation-domain artifacts use check_evaluation_semantics_or_raise; "
            f"for WF artifacts use check_wf_semantics_or_raise."
        )

    # 1b. Path-confinement check on returns_per_bar_path (Phase 1 structural).
    # Only check if the key is present (missing key is a Phase 2 collect-all failure).
    raw_bar_path = summary.get("returns_per_bar_path")
    if raw_bar_path is not None:
        _check_returns_path_confinement(raw_bar_path, artifact_path, where)

    # ------------------------------------------------------------------
    # Phase 2: collect-all per-field validation.
    # ------------------------------------------------------------------
    errors: list[str] = []

    # 2a. Required string fields (12 fields; parent_run_id handled separately).
    for field in _BCE_REQUIRED_STRING_FIELDS:
        if field not in summary:
            errors.append(f"{field}: missing key (required for b_c_extended_v1)")
            continue
        val = summary[field]
        if not isinstance(val, str):
            errors.append(
                f"{field}: expected string, got {type(val).__name__!r}"
            )
            continue
        if not val.strip():
            errors.append(
                f"{field}: must be non-empty non-whitespace string, got {val!r}"
            )

    # 2b. parent_run_id: B2-b Optional[string] semantics.
    #   - Key must be present (explicit presence required even if value is None)
    #   - Value None is valid (single-run callers without parent linkage)
    #   - Empty string FAIL CLOSED
    #   - Non-string non-None FAIL CLOSED
    if "parent_run_id" not in summary:
        errors.append(
            "parent_run_id: missing key — explicit presence required "
            "(value may be None for callers without parent linkage; "
            "B2-b lock per plan v5 Sub-decision B)"
        )
    else:
        pid = summary["parent_run_id"]
        if pid is not None:
            if not isinstance(pid, str):
                errors.append(
                    f"parent_run_id: expected string or None, got {type(pid).__name__!r}"
                )
            elif not pid.strip():
                # FIX-M1: whitespace-only strings are semantically empty per B2-b.
                # Empty string ('') and whitespace-only ('   ', '\t\n') both fail closed.
                errors.append(
                    "parent_run_id: empty or whitespace-only string is not valid; "
                    "use None for callers without parent linkage "
                    "(B2-b: empty-string and whitespace-only FAIL CLOSED)"
                )

    # 2c. T_obs: present, integer, positive.
    if "T_obs" not in summary:
        errors.append("T_obs: missing key (required for b_c_extended_v1)")
    else:
        t_obs = summary["T_obs"]
        if not isinstance(t_obs, int) or isinstance(t_obs, bool):
            errors.append(
                f"T_obs: expected positive integer, got {type(t_obs).__name__!r}"
            )
        elif t_obs <= 0:
            errors.append(
                f"T_obs: must be positive (> 0), got {t_obs!r}"
            )

    # 2d. cost_anchor_id mapping integrity (Contract 2.0.4).
    # Only validate if both execution_config_path and cost_anchor_id are present
    # and string-valid (earlier checks may have already flagged missing/non-string).
    exec_path = summary.get("execution_config_path")
    cost_anchor = summary.get("cost_anchor_id")
    if (
        isinstance(exec_path, str)
        and exec_path.strip()
        and isinstance(cost_anchor, str)
        and cost_anchor.strip()
    ):
        _check_cost_anchor_mapping(exec_path, cost_anchor, errors, artifact_path)

    # 2e. Per-bar artifact linkage: file-exists + SHA256 + T_obs-alignment.
    # Only validate if returns_per_bar_path was present and passed Phase 1
    # path-confinement check, and returns_per_bar_sha256 + T_obs passed Phase 2.
    bar_path_str = summary.get("returns_per_bar_path")
    bar_sha256 = summary.get("returns_per_bar_sha256")
    t_obs_val = summary.get("T_obs")
    if (
        isinstance(bar_path_str, str)
        and bar_path_str.strip()
        and isinstance(bar_sha256, str)
        and bar_sha256.strip()
        and isinstance(t_obs_val, int)
        and t_obs_val > 0
    ):
        _check_per_bar_linkage(
            bar_path_str, bar_sha256, t_obs_val,
            artifact_path, errors,
        )

    # Raise once with all accumulated failures.
    if errors:
        raise BCExtendedSchemaValidationError(errors, artifact_path=artifact_path)


def _check_returns_path_confinement(
    raw_bar_path: Any,
    artifact_path: Path | None,
    where: str,
) -> None:
    """Phase 1 structural check: verify returns_per_bar_path is confined.

    Raises ValueError immediately on:
    - Absolute paths (escape artifact directory regardless of traversal)
    - Path containing '../' components (escape via traversal)

    Only called when returns_per_bar_path key is present in summary.
    Missing-key is a Phase 2 collect-all failure, not Phase 1.

    Args:
        raw_bar_path: The raw value of summary['returns_per_bar_path'].
        artifact_path: The artifact source path (for base-directory resolution).
        where: Diagnostic location string (e.g., " at /path/to/summary.json").
    """
    if not isinstance(raw_bar_path, str):
        # Not a string: Phase 2 will catch the type error. Skip confinement.
        return

    # Absolute paths are an immediate structural violation.
    if os.path.isabs(raw_bar_path):
        raise ValueError(
            f"B-C-extended artifact{where}: returns_per_bar_path={raw_bar_path!r} "
            f"is an absolute path. Only paths relative to the artifact's containing "
            f"directory are allowed (path-confinement, Phase 1 structural check)."
        )

    # Resolve against artifact's containing directory (or cwd if no artifact_path).
    base_dir = artifact_path.parent if artifact_path is not None else Path.cwd()
    resolved = (base_dir / raw_bar_path).resolve()
    base_resolved = base_dir.resolve()

    # commonpath-based containment check (not naive string prefix per plan v5 Fv5-1).
    try:
        common = os.path.commonpath([str(base_resolved), str(resolved)])
    except ValueError:
        # Windows: different drives raise ValueError in commonpath.
        raise ValueError(
            f"B-C-extended artifact{where}: returns_per_bar_path={raw_bar_path!r} "
            f"is outside the artifact's containing directory {base_dir!r} "
            f"(path-confinement violation, Phase 1 structural check)."
        )
    if common != str(base_resolved):
        raise ValueError(
            f"B-C-extended artifact{where}: returns_per_bar_path={raw_bar_path!r} "
            f"resolves outside the artifact's containing directory {base_dir!r}. "
            f"Path-confinement violation — potential '../' escape attack "
            f"(Phase 1 structural check)."
        )


def _check_cost_anchor_mapping(
    exec_path: str,
    cost_anchor: str,
    errors: list[str],
    artifact_path: Path | None,
) -> None:
    """Phase 2 collect-all: validate cost_anchor_id against COST_ANCHOR_ID_MAPPING.

    Appends to errors list rather than raising directly (Phase 2 collect-all).

    Args:
        exec_path: The execution_config_path string from the artifact header.
        cost_anchor: The cost_anchor_id string from the artifact header.
        errors: Mutable list to append failure strings into.
        artifact_path: Used for diagnostics only.
    """
    expected_anchor = COST_ANCHOR_ID_MAPPING.get(exec_path)
    if expected_anchor is None:
        mapping_table = "; ".join(
            f"{k!r} → {v!r}" for k, v in COST_ANCHOR_ID_MAPPING.items()
        )
        errors.append(
            f"execution_config_path={exec_path!r} is not in the "
            f"COST_ANCHOR_ID_MAPPING (R3.1d §5.2). "
            f"Known paths: {mapping_table}. "
            f"Update R3.1d §5.2 mapping for new anchor or contact human "
            f"approval before extending mapping."
        )
    elif cost_anchor != expected_anchor:
        errors.append(
            f"cost_anchor_id={cost_anchor!r} does not match the expected "
            f"value {expected_anchor!r} for "
            f"execution_config_path={exec_path!r} "
            f"(COST_ANCHOR_ID_MAPPING, R3.1d §5.2)."
        )


def _check_per_bar_linkage(
    bar_path_str: str,
    bar_sha256: str,
    t_obs: int,
    artifact_path: Path | None,
    errors: list[str],
) -> None:
    """Phase 2 collect-all: file-exists + SHA256-recompute + T_obs-alignment.

    Per Contract 2.0.5 per-bar artifact linkage validation discipline.
    Appends to errors list rather than raising directly (Phase 2 collect-all).

    FIX-M2: uses resolved.is_file() (not resolved.exists()) so that a
    directory at the expected path produces a structured error instead of
    an unhandled IsADirectoryError from read_bytes().

    FIX-H1: SHA256 recomputed via 64KB chunked streaming (BufferedReader loop)
    to avoid loading large parquet files entirely into memory. OSError during
    file read is caught and appended as a structured error.

    FIX-B1: T_obs = count of FINITE values in the 'return' column, not
    count of non-NULL values. Uses pc.and_(pc.is_valid(col), pc.is_finite(col))
    to exclude NULL, NaN, and inf/-inf. If 'return' column is absent,
    fail closed (append error) rather than falling back to row count —
    absence of 'return' column contradicts Contract 2.0.5 "finite per-bar
    return observations" semantics when T_obs > 0 is claimed.

    CONTRACT GAP: execution_config_path canonicalization (T1.3 engine
    _write_to_registry() responsibility) is not performed here. The helper
    accepts already-canonicalized paths from the artifact header; non-canonical
    paths fail closed via mapping miss. See COST_ANCHOR_ID_MAPPING docstring.

    Args:
        bar_path_str: The returns_per_bar_path string (already confirmed relative
            and confined by Phase 1 check_returns_path_confinement).
        bar_sha256: The returns_per_bar_sha256 stored hash.
        t_obs: The T_obs value from the artifact header.
        artifact_path: The artifact source path (for base-directory resolution).
        errors: Mutable list to append failure strings into.
    """
    import pyarrow.parquet as pq  # function-level import (heavy; avoid import-time cost)
    import pyarrow.compute as pc  # function-level import (co-located with pq)

    base_dir = artifact_path.parent if artifact_path is not None else Path.cwd()
    resolved = (base_dir / bar_path_str).resolve()

    # FIX-M2: use is_file() (not exists()) to catch directories explicitly.
    # exists() returns True for directories, leading to unhandled IsADirectoryError
    # from read_bytes(). is_file() is the correct semantic guard.
    if not resolved.is_file():
        errors.append(
            f"returns_per_bar_path={bar_path_str!r} does not exist or is not "
            f"a regular file at resolved path {resolved!r}. "
            f"File-exists check failed (Contract 2.0.5 per-bar artifact linkage)."
        )
        return  # Cannot proceed with SHA256 or T_obs checks

    # FIX-H1: SHA256 recomputed via chunked streaming (64KB chunks).
    # Avoids loading large parquet files entirely into memory.
    # OSError during file read is caught and appended as structured error.
    h = hashlib.sha256()
    try:
        with resolved.open("rb") as fh:
            while True:
                chunk = fh.read(65536)  # 64KB chunks
                if not chunk:
                    break
                h.update(chunk)
    except OSError as exc:
        errors.append(
            f"returns_per_bar_path={bar_path_str!r}: OSError reading file for "
            f"SHA256 recomputation: {exc} (Contract 2.0.5)."
        )
        return  # Cannot proceed with T_obs check
    actual_sha256 = h.hexdigest()

    if actual_sha256 != bar_sha256:
        errors.append(
            f"returns_per_bar_sha256 mismatch for {bar_path_str!r}: "
            f"stored={bar_sha256!r}, recomputed={actual_sha256!r}. "
            f"SHA256 integrity check failed (Contract 2.0.5)."
        )
        # Continue to T_obs check even on hash mismatch (collect-all)

    # T_obs alignment: count finite rows in the parquet file.
    try:
        table = pq.read_table(str(resolved))
    except Exception as exc:  # pyarrow read errors
        errors.append(
            f"returns_per_bar_path={bar_path_str!r}: failed to read parquet "
            f"for T_obs alignment check: {exc} (Contract 2.0.5)."
        )
        return

    # FIX-B1: T_obs = count of FINITE values in the 'return' column.
    # Contract 2.0.5: T_obs = "count of finite per-bar return observations".
    # - pc.is_valid(col) counts non-NULL but includes NaN and inf (BUG).
    # - pc.and_(pc.is_valid(col), pc.is_finite(col)) correctly excludes
    #   NULL, NaN, and inf/-inf from the count.
    #
    # If 'return' column is absent, FAIL CLOSED (append error) rather than
    # falling back to row count. Absence of 'return' column contradicts
    # Contract 2.0.5 semantics when T_obs > 0 is claimed.
    if "return" not in table.column_names:
        errors.append(
            f"returns_per_bar_path={bar_path_str!r}: 'return' column is absent "
            f"from the parquet file. Contract 2.0.5 requires T_obs = count of "
            f"finite per-bar return observations; without a 'return' column "
            f"the finite-observation count cannot be verified "
            f"(stored T_obs={t_obs!r}). Fail closed."
        )
        return

    col = table.column("return")
    # Use pc.and_ to exclude NULL (is_valid) AND NaN/inf (is_finite).
    actual_t_obs = pc.sum(pc.and_(pc.is_valid(col), pc.is_finite(col))).as_py()

    if actual_t_obs != t_obs:
        errors.append(
            f"T_obs mismatch for {bar_path_str!r}: "
            f"stored T_obs={t_obs!r}, actual finite-row count={actual_t_obs!r}. "
            f"T_obs alignment check failed (Contract 2.0.5). "
            f"Hint: T_obs must count only finite (non-NULL, non-NaN, non-inf) "
            f"values in the 'return' column."
        )

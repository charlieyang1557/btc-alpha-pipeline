"""DSL → Backtrader strategy compiler (Phase 2A, D2).

Takes a validated :class:`strategies.dsl.StrategyDSL` and returns a
dynamically-generated :class:`strategies.template.BaseStrategy` subclass
that:

- Reads pre-computed factors from the feature parquet via
  :func:`factors.build_features.load_features_or_rebuild` (never
  re-computes indicators inside ``next()``).
- Evaluates entry/exit conditions per bar: AND within each
  ``ConditionGroup``, OR across groups.
- Emits ``self.buy()`` / ``self.close()`` through the sizer configured
  in :func:`backtest.execution_model.configure_cerebro`, so the
  Phase 1-validated engine runs it unchanged.
- Honors an optional ``max_hold_bars`` cap.

Hard design decisions (see PHASE2_BLUEPRINT_v2.md D2 and CLAUDE.md):

1. **Crosses use the explicit two-bar form**.
   For operand types ``factor-vs-scalar`` and ``factor-vs-factor``,
   ``crosses_above(a, b)`` means ``a[cur] > b[cur] AND a[prev] <= b[prev]``.
   ``crosses_below`` is the inverted pair. A naive single-bar comparison
   is forbidden by explicit test (see ``tests/test_dsl.py``).

2. **Two independent comparison code paths**.
   Factor-vs-scalar is :func:`_compare_factor_vs_scalar`. Factor-vs-factor
   is :func:`_compare_factor_vs_factor`. They do not share an inner helper;
   each operator branch is written out so a bug in one path cannot silently
   affect the other. Each operator has its own unit test for each path.

3. **NaN → False, always**.
   Each comparator checks ``math.isnan`` on every operand it uses and
   returns False if any are NaN. NaN never evaluates to True, never
   short-circuits. This is the interaction point with D1's warmup
   boundary (where factors are NaN) and prevents spurious firing at the
   boundary.

4. **Compiler never edits engine/registry/metrics**.
   The compiled class is a plain :class:`BaseStrategy` subclass with
   ``STRATEGY_NAME`` and ``WARMUP_BARS``. It plugs into the existing
   :func:`backtest.engine.run_backtest` via ``cerebro.addstrategy``.

5. **Manifest drift raises, never silently regenerates**.
   On each compile, :func:`write_compilation_manifest` writes
   ``data/compiled_strategies/<dsl_hash>.json`` with four drift-sensitive
   fields. If the file exists and any field differs,
   :class:`ManifestDriftError` is raised. Human-acknowledged regeneration
   requires deleting the manifest first.

6. **Factor values are loaded once per strategy instance**.
   The parquet is read in the strategy's ``__init__`` and stored as a
   timestamp→tuple dict. In ``next()`` we do one ``dict.get`` per bar.
"""

from __future__ import annotations

import hashlib
import inspect
import json
import logging
import math
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import backtrader as bt
import pandas as pd

from factors.build_features import (
    DEFAULT_FEATURES_PATH,
    DEFAULT_RAW_PATH,
    load_features_or_rebuild,
)
from factors.registry import FactorRegistry, compute_feature_version, get_registry
from strategies.dsl import (
    Condition,
    ConditionGroup,
    StrategyDSL,
    canonicalize_dsl,
    compute_dsl_hash,
)
from strategies.template import BaseStrategy

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MANIFEST_DIR = PROJECT_ROOT / "data" / "compiled_strategies"


# ---------------------------------------------------------------------------
# Warmup-gating indicator
#
# Strategies cannot set ``_minperiod`` directly — it is derived from child
# indicators. Without a child, ``next()`` fires from bar 1, which would
# bypass the WARMUP_BARS gate and make the DSL-compiled strategy record
# equity (and evaluate conditions) during the factor-NaN warmup window.
# This tiny indicator declares a minperiod via ``addminperiod`` so the
# parent strategy adopts it. It produces a trivial constant line; the
# per-bar cost is negligible.
# ---------------------------------------------------------------------------


class _MinperiodGate(bt.Indicator):
    """Dummy indicator whose sole purpose is to set a parent strategy's
    minperiod to a specified value.
    """

    lines = ("gate",)
    params = (("period", 1),)

    def __init__(self) -> None:
        super().__init__()
        self.addminperiod(self.p.period)

    def next(self) -> None:
        self.lines.gate[0] = 0.0


# ---------------------------------------------------------------------------
# Compiler SHA — identifies the compiler code version (drift detection).
# ---------------------------------------------------------------------------


def _compute_compiler_sha() -> str:
    """SHA256 of this module's source text.

    Changes iff the compiler code changes on disk. Used as one of the
    four drift-detection fields in the compilation manifest.
    """
    src = inspect.getsource(sys.modules[__name__])
    return hashlib.sha256(src.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------


class ManifestDriftError(RuntimeError):
    """Raised when a stored compilation manifest disagrees with the live
    compilation context. Fields compared: canonical DSL, compiler SHA,
    factor list snapshot, feature_version.
    """


# ---------------------------------------------------------------------------
# Comparison helpers — deliberately TWO independent functions, one per
# operand type. A shared implementation is a blueprint violation; the
# duplication is load-bearing for bug-isolation.
# ---------------------------------------------------------------------------


def _compare_factor_vs_scalar(
    op: str,
    cur_val: float,
    prev_val: float,
    scalar: float,
) -> bool:
    """Evaluate ``factor <op> scalar`` on the current bar.

    For continuous ops (``<``, ``<=``, ``>``, ``>=``, ``==``), only
    ``cur_val`` is read; ``prev_val`` is ignored. For crosses, both
    ``cur_val`` and ``prev_val`` are required.

    NaN policy: if any operand actually read by the op is NaN, return
    False. Never True.

    This function is deliberately not shared with factor-vs-factor;
    see module docstring.
    """
    if op == "<":
        if math.isnan(cur_val):
            return False
        return cur_val < scalar
    if op == "<=":
        if math.isnan(cur_val):
            return False
        return cur_val <= scalar
    if op == ">":
        if math.isnan(cur_val):
            return False
        return cur_val > scalar
    if op == ">=":
        if math.isnan(cur_val):
            return False
        return cur_val >= scalar
    if op == "==":
        if math.isnan(cur_val):
            return False
        return cur_val == scalar
    if op == "crosses_above":
        if math.isnan(cur_val) or math.isnan(prev_val):
            return False
        # Two-bar form: current above AND previous at-or-below.
        return (cur_val > scalar) and (prev_val <= scalar)
    if op == "crosses_below":
        if math.isnan(cur_val) or math.isnan(prev_val):
            return False
        return (cur_val < scalar) and (prev_val >= scalar)
    raise ValueError(f"_compare_factor_vs_scalar: unknown op {op!r}")


def _compare_factor_vs_factor(
    op: str,
    cur_a: float,
    prev_a: float,
    cur_b: float,
    prev_b: float,
) -> bool:
    """Evaluate ``factor_a <op> factor_b`` on the current bar.

    For continuous ops (``<``, ``<=``, ``>``, ``>=``, ``==``), only
    ``cur_a`` and ``cur_b`` are read. For crosses, both previous values
    are also read.

    NaN policy: if any operand actually read by the op is NaN, return
    False. Never True.

    This function is deliberately not shared with factor-vs-scalar;
    see module docstring.
    """
    if op == "<":
        if math.isnan(cur_a) or math.isnan(cur_b):
            return False
        return cur_a < cur_b
    if op == "<=":
        if math.isnan(cur_a) or math.isnan(cur_b):
            return False
        return cur_a <= cur_b
    if op == ">":
        if math.isnan(cur_a) or math.isnan(cur_b):
            return False
        return cur_a > cur_b
    if op == ">=":
        if math.isnan(cur_a) or math.isnan(cur_b):
            return False
        return cur_a >= cur_b
    if op == "==":
        if math.isnan(cur_a) or math.isnan(cur_b):
            return False
        return cur_a == cur_b
    if op == "crosses_above":
        if (
            math.isnan(cur_a)
            or math.isnan(cur_b)
            or math.isnan(prev_a)
            or math.isnan(prev_b)
        ):
            return False
        return (cur_a > cur_b) and (prev_a <= prev_b)
    if op == "crosses_below":
        if (
            math.isnan(cur_a)
            or math.isnan(cur_b)
            or math.isnan(prev_a)
            or math.isnan(prev_b)
        ):
            return False
        return (cur_a < cur_b) and (prev_a >= prev_b)
    raise ValueError(f"_compare_factor_vs_factor: unknown op {op!r}")


# ---------------------------------------------------------------------------
# Condition compilation — resolves factor names to column indices and
# produces a closure (cur_row, prev_row) -> bool.
# ---------------------------------------------------------------------------


def _extract_factor_names(dsl: StrategyDSL) -> list[str]:
    """Return sorted list of all distinct factor names referenced by the DSL.

    Includes both LHS ``factor`` fields and string-typed RHS ``value``
    fields. Registry validation has already happened at schema time.
    """
    names: set[str] = set()
    for groups in (dsl.entry, dsl.exit):
        for g in groups:
            for c in g.conditions:
                names.add(c.factor)
                if isinstance(c.value, str):
                    names.add(c.value)
    return sorted(names)


def _dsl_uses_cross_op(dsl: StrategyDSL) -> bool:
    """Return True iff any condition uses ``crosses_above`` / ``crosses_below``.

    Cross operators require the previous bar's factor value to be valid,
    which pushes the first-signalable bar one past ``WARMUP_BARS``.
    """
    for groups in (dsl.entry, dsl.exit):
        for g in groups:
            for c in g.conditions:
                if c.op in ("crosses_above", "crosses_below"):
                    return True
    return False


def _compile_condition(
    cond: Condition,
    factor_index: dict[str, int],
) -> Callable[[tuple, tuple], bool]:
    """Compile one condition to a closure over pre-resolved column indices.

    Dispatches explicitly on ``type(cond.value)`` into one of the two
    independent comparison helpers. That dispatch lives here — in
    ``next()`` we only see the closure, so factor-vs-scalar and
    factor-vs-factor are bound at compile time and can never be mixed
    at run time.
    """
    op = cond.op
    idx_a = factor_index[cond.factor]
    value = cond.value

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        scalar = float(value)

        def eval_scalar(cur_row: tuple, prev_row: tuple) -> bool:
            return _compare_factor_vs_scalar(
                op, cur_row[idx_a], prev_row[idx_a], scalar
            )

        return eval_scalar

    if isinstance(value, str):
        idx_b = factor_index[value]

        def eval_factor(cur_row: tuple, prev_row: tuple) -> bool:
            return _compare_factor_vs_factor(
                op,
                cur_row[idx_a],
                prev_row[idx_a],
                cur_row[idx_b],
                prev_row[idx_b],
            )

        return eval_factor

    raise TypeError(
        f"Condition.value has unexpected type {type(value).__name__}; "
        f"schema should have rejected this."
    )


def _compile_group(
    group: ConditionGroup,
    factor_index: dict[str, int],
) -> Callable[[tuple, tuple], bool]:
    """AND-reduce a ConditionGroup's conditions."""
    compiled = [_compile_condition(c, factor_index) for c in group.conditions]

    def eval_group(cur_row: tuple, prev_row: tuple) -> bool:
        for fn in compiled:
            if not fn(cur_row, prev_row):
                return False
        return True

    return eval_group


def _compile_groups(
    groups: list[ConditionGroup],
    factor_index: dict[str, int],
) -> Callable[[tuple, tuple], bool]:
    """OR-reduce top-level ConditionGroups."""
    compiled = [_compile_group(g, factor_index) for g in groups]

    def eval_groups(cur_row: tuple, prev_row: tuple) -> bool:
        for fn in compiled:
            if fn(cur_row, prev_row):
                return True
        return False

    return eval_groups


# ---------------------------------------------------------------------------
# Manifest
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CompilationManifest:
    """The four drift-sensitive fields plus provenance.

    Drift is defined as a mismatch in ANY of ``canonical_dsl``,
    ``compiler_sha``, ``factor_snapshot``, or ``feature_version``.
    """

    canonical_dsl: str  # canonicalize_dsl(dsl) — byte-stable
    compiler_sha: str
    factor_snapshot: list[dict[str, Any]]
    feature_version: str


def _build_manifest(
    dsl: StrategyDSL,
    registry: FactorRegistry,
    compiler_sha: str | None = None,
) -> CompilationManifest:
    """Snapshot the four drift-sensitive fields from the live context."""
    if compiler_sha is None:
        compiler_sha = _compute_compiler_sha()
    factor_snapshot = [
        {"name": n, "warmup_bars": registry.get(n).warmup_bars}
        for n in registry.list_names()
    ]
    return CompilationManifest(
        canonical_dsl=canonicalize_dsl(dsl),
        compiler_sha=compiler_sha,
        factor_snapshot=factor_snapshot,
        feature_version=compute_feature_version(registry),
    )


def _manifest_to_json_dict(
    manifest: CompilationManifest,
    *,
    pseudo_code: str = "",
) -> dict[str, Any]:
    """Serialize manifest + metadata for on-disk JSON."""
    return {
        "canonical_dsl": json.loads(manifest.canonical_dsl),
        "canonical_dsl_string": manifest.canonical_dsl,
        "compiler_sha": manifest.compiler_sha,
        "factor_snapshot": manifest.factor_snapshot,
        "feature_version": manifest.feature_version,
        "pseudo_code": pseudo_code,
        "written_at_utc": datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
    }


def _read_stored_manifest(path: Path) -> dict[str, Any]:
    """Read and parse a manifest JSON file."""
    return json.loads(path.read_text(encoding="utf-8"))


def _drift_report(
    stored: dict[str, Any],
    live: CompilationManifest,
) -> list[str]:
    """Return a list of human-readable drift descriptions (empty == no drift)."""
    issues: list[str] = []
    if stored.get("canonical_dsl_string") != live.canonical_dsl:
        issues.append("canonical_dsl mismatch")
    if stored.get("compiler_sha") != live.compiler_sha:
        issues.append(
            f"compiler_sha mismatch "
            f"(stored={str(stored.get('compiler_sha'))[:12]}..., "
            f"live={live.compiler_sha[:12]}...)"
        )
    if stored.get("factor_snapshot") != live.factor_snapshot:
        issues.append("factor_snapshot mismatch")
    if stored.get("feature_version") != live.feature_version:
        issues.append(
            f"feature_version mismatch "
            f"(stored={str(stored.get('feature_version'))[:12]}..., "
            f"live={live.feature_version[:12]}...)"
        )
    return issues


def write_compilation_manifest(
    dsl: StrategyDSL,
    registry: FactorRegistry,
    *,
    manifest_dir: Path = DEFAULT_MANIFEST_DIR,
    dsl_hash: str | None = None,
    pseudo_code: str = "",
    compiler_sha: str | None = None,
) -> Path:
    """Write (or verify) the compilation manifest for ``dsl``.

    Behavior:
    - If no manifest file exists for this ``dsl_hash``, write it.
    - If a manifest exists and all four drift fields match, leave it
      alone and return its path (idempotent).
    - If a manifest exists and any drift field mismatches, raise
      :class:`ManifestDriftError`. This is intentional: silent
      regeneration is a blueprint violation.

    Args:
        dsl: Validated DSL object.
        registry: Registry to snapshot.
        manifest_dir: Directory for ``data/compiled_strategies/``.
        dsl_hash: Explicit hash to use as filename key. Defaults to
            :func:`compute_dsl_hash`. Callers can inject a higher-level
            ``hypothesis_hash`` once D3 lands.
        pseudo_code: Human-audit rendering of the compiled strategy.
        compiler_sha: Inject a specific compiler SHA (tests only).

    Returns:
        Absolute path to the manifest JSON file.

    Raises:
        ManifestDriftError: On any of the four drift conditions.
    """
    if dsl_hash is None:
        dsl_hash = compute_dsl_hash(dsl)

    manifest_dir.mkdir(parents=True, exist_ok=True)
    path = manifest_dir / f"{dsl_hash}.json"

    live = _build_manifest(dsl, registry, compiler_sha=compiler_sha)

    if path.exists():
        stored = _read_stored_manifest(path)
        issues = _drift_report(stored, live)
        if issues:
            raise ManifestDriftError(
                f"Compilation manifest drift at {path}: "
                + "; ".join(issues)
                + ". Silent regeneration is prohibited. Delete the "
                + "manifest to force explicit regeneration."
            )
        return path

    data = _manifest_to_json_dict(live, pseudo_code=pseudo_code)
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
    logger.info(
        "Wrote compilation manifest %s (compiler_sha=%s, feature_version=%s)",
        path,
        live.compiler_sha[:12],
        live.feature_version[:12],
    )
    return path


# ---------------------------------------------------------------------------
# Pseudo-code rendering (for human audit in the manifest)
# ---------------------------------------------------------------------------


def _render_pseudo_code(dsl: StrategyDSL) -> str:
    """Human-readable rendering of the compiled strategy logic."""
    lines: list[str] = []
    lines.append(f"strategy {dsl.name!r} ({dsl.description})")
    lines.append(f"  position_sizing: {dsl.position_sizing}")
    if dsl.max_hold_bars is not None:
        lines.append(f"  max_hold_bars: {dsl.max_hold_bars}")
    lines.append("  ENTRY when (any of):")
    for i, g in enumerate(dsl.entry):
        clause = " AND ".join(_render_condition(c) for c in g.conditions)
        lines.append(f"    [{i + 1}] {clause}")
    lines.append("  EXIT when (any of):")
    for i, g in enumerate(dsl.exit):
        clause = " AND ".join(_render_condition(c) for c in g.conditions)
        lines.append(f"    [{i + 1}] {clause}")
    return "\n".join(lines)


def _render_condition(cond: Condition) -> str:
    if isinstance(cond.value, str):
        return f"{cond.factor} {cond.op} {cond.value}"
    return f"{cond.factor} {cond.op} {cond.value:g}"


# ---------------------------------------------------------------------------
# Compile entry point
# ---------------------------------------------------------------------------


def compile_dsl_to_strategy(
    dsl: StrategyDSL,
    registry: FactorRegistry | None = None,
    *,
    write_manifest: bool = True,
    manifest_dir: Path = DEFAULT_MANIFEST_DIR,
    dsl_hash: str | None = None,
) -> type[BaseStrategy]:
    """Compile a validated DSL to a Backtrader strategy class.

    The returned class is a :class:`BaseStrategy` subclass ready for
    ``cerebro.addstrategy``. It reads the feature parquet once per
    instance and never recomputes indicators in ``next()``.

    Strategy-level params (override via ``cerebro.addstrategy(cls,
    **kwargs)``):

    - ``features_path``: Path to the factor parquet. Defaults to
      ``data/features/btcusdt_1h_features.parquet``.
    - ``raw_path``: Path to the raw OHLCV parquet (used only if a
      rebuild is needed).
    - ``features_df_override``: Pre-loaded DataFrame (testing). When
      set, bypasses the loader and the freshness check.

    Manifest behavior: on compile, writes
    ``data/compiled_strategies/<dsl_hash>.json`` the first time,
    verifies it on subsequent compiles, and raises
    :class:`ManifestDriftError` on drift. Disable with
    ``write_manifest=False`` (testing only — production must always
    write).

    Args:
        dsl: Validated StrategyDSL instance.
        registry: Factor registry. Defaults to the global registry.
        write_manifest: Whether to emit / verify the on-disk manifest.
        manifest_dir: Where manifests live.
        dsl_hash: Override the manifest filename key.

    Returns:
        A :class:`BaseStrategy` subclass.
    """
    if registry is None:
        registry = get_registry()

    # Collect all factor names referenced (LHS + RHS strings).
    factors_used = _extract_factor_names(dsl)

    # Defense in depth — schema already validates, but avoid KeyError on
    # later max_warmup lookup if a caller hand-built an invalid DSL that
    # bypassed pydantic.
    known = set(registry.list_names())
    unknown = [n for n in factors_used if n not in known]
    if unknown:
        raise ValueError(
            f"DSL references factors not in registry: {unknown}"
        )

    warmup_bars = registry.max_warmup(factors_used) if factors_used else 0

    # Minperiod calculation:
    # - Continuous ops (``<``, ``>``, ``==``, ...) read only ``cur_row``,
    #   so the first firable bar is ``warmup_bars`` (0-indexed), i.e.
    #   ``len(self) == warmup_bars + 1``.
    # - Cross ops additionally read ``prev_row``, so the first firable
    #   bar shifts forward by 1 → ``len(self) == warmup_bars + 2``.
    # We also unconditionally need ``len(self) >= 2`` because ``next()``
    # always calls ``self.data.datetime.datetime(-1)``.
    uses_cross = _dsl_uses_cross_op(dsl)
    effective_minperiod = max(warmup_bars + (2 if uses_cross else 1), 2)

    # Column index map, consistent with the order we'll slice from the
    # feature DataFrame.
    factor_index = {name: i for i, name in enumerate(factors_used)}

    entry_eval = _compile_groups(dsl.entry, factor_index)
    exit_eval = _compile_groups(dsl.exit, factor_index)

    strategy_name = dsl.name
    max_hold_bars = dsl.max_hold_bars

    # Capture the registry for default-arg auto-loading inside the class.
    default_registry = registry

    class CompiledStrategy(BaseStrategy):
        """Dynamically-generated BaseStrategy for a compiled DSL."""

        STRATEGY_NAME = strategy_name
        WARMUP_BARS = warmup_bars
        _DSL = dsl
        _FACTORS_USED = tuple(factors_used)
        _DSL_HASH = compute_dsl_hash(dsl)

        params = (
            ("features_path", DEFAULT_FEATURES_PATH),
            ("raw_path", DEFAULT_RAW_PATH),
            ("features_df_override", None),
            ("registry_override", None),
        )

        def __init__(self) -> None:
            # Strategies inherit minperiod from child indicators, not from
            # self.addminperiod(). Install a dummy gate indicator so
            # next() fires only at len(self) >= effective_minperiod.
            if effective_minperiod > 1:
                self._warmup_gate = _MinperiodGate(
                    self.data, period=effective_minperiod
                )

            reg = self.p.registry_override or default_registry

            if self.p.features_df_override is not None:
                features_df = self.p.features_df_override
            else:
                features_df = load_features_or_rebuild(
                    raw_path=Path(self.p.raw_path),
                    features_path=Path(self.p.features_path),
                    registry=reg,
                )

            self._factor_rows = _features_to_lookup(
                features_df, self._FACTORS_USED
            )
            self._entry_bar: int | None = None

        def next(self) -> None:
            # Current & previous bar timestamps (naive UTC, per
            # ParquetFeed.from_parquet which strips tzinfo).
            cur_ts = self.data.datetime.datetime(0)
            prev_ts = self.data.datetime.datetime(-1)

            cur_row = self._factor_rows.get(cur_ts)
            prev_row = self._factor_rows.get(prev_ts)
            if cur_row is None or prev_row is None:
                # Missing bar in the feature parquet (should not happen
                # for canonical data; guards against partial feeds).
                return

            if not self.position:
                if entry_eval(cur_row, prev_row):
                    self.buy()
                    self._entry_bar = len(self)
                return

            # In position: check exit conditions and max-hold.
            if max_hold_bars is not None and self._entry_bar is not None:
                if len(self) - self._entry_bar >= max_hold_bars:
                    self.close()
                    self._entry_bar = None
                    return
            if exit_eval(cur_row, prev_row):
                self.close()
                self._entry_bar = None

    CompiledStrategy.__name__ = f"Compiled_{_sanitize_for_classname(dsl.name)}"
    CompiledStrategy.__qualname__ = CompiledStrategy.__name__

    if write_manifest:
        write_compilation_manifest(
            dsl,
            registry,
            manifest_dir=manifest_dir,
            dsl_hash=dsl_hash,
            pseudo_code=_render_pseudo_code(dsl),
        )

    return CompiledStrategy


def _sanitize_for_classname(name: str) -> str:
    """Turn a DSL name into a valid Python identifier fragment."""
    out = []
    for ch in name:
        if ch.isalnum() or ch == "_":
            out.append(ch)
        else:
            out.append("_")
    s = "".join(out)
    if s and s[0].isdigit():
        s = "_" + s
    return s or "Unnamed"


def _features_to_lookup(
    features_df: pd.DataFrame,
    factors_used: tuple[str, ...],
) -> dict[datetime, tuple[float, ...]]:
    """Build a timestamp → factor-values lookup dict keyed by naive UTC.

    The feature parquet carries an ``open_time_utc`` column that is
    UTC-aware. Backtrader's feed emits naive datetimes after stripping
    tzinfo. We convert here so ``next()``'s
    ``self.data.datetime.datetime(0)`` can be used directly as a key.
    """
    ts = features_df["open_time_utc"]
    if isinstance(ts.dtype, pd.DatetimeTZDtype):
        ts_naive = ts.dt.tz_convert("UTC").dt.tz_localize(None)
    else:
        ts_naive = ts
    cols = list(factors_used)
    if not cols:
        return {
            t.to_pydatetime(): tuple() for t in ts_naive
        }
    values = features_df[cols].to_numpy()
    return {
        t.to_pydatetime(): tuple(float(v) for v in row)
        for t, row in zip(ts_naive, values)
    }


__all__ = [
    "CompilationManifest",
    "ManifestDriftError",
    "compile_dsl_to_strategy",
    "write_compilation_manifest",
    "_compare_factor_vs_scalar",
    "_compare_factor_vs_factor",
    "_compute_compiler_sha",
    "DEFAULT_MANIFEST_DIR",
]

"""Factor registry with feature_version governance (Phase 2A, D1).

Owns:
- ``FactorSpec``: metadata describing a single factor (name, category,
  warmup, inputs, output dtype, compute callable, docstring, null policy).
- ``FactorRegistry``: holds registered factors, guards against duplicate
  names, enforces the top-level-callable requirement, and can compute all
  factors on a DataFrame.
- ``compute_feature_version(registry)``: deterministic SHA256 of the
  registry's canonical metadata. The compute function's source (via
  ``inspect.getsource``) is part of the hash; docstrings are excluded.

Hard rules enforced here (see PHASE2_BLUEPRINT_v2.md D1):
- Registered compute functions MUST be top-level named callables. Lambdas,
  nested functions, and dynamically-generated callables are rejected at
  registration time because ``inspect.getsource`` is not stable on them.
- Factor outputs MAY be NaN only before their declared ``warmup_bars``.
  After warmup, NaN is a build failure — ``compute_all`` raises rather
  than silently continuing.
- ``null_policy`` only allowed value in D1 is ``"nan_before_warmup_only"``.
"""

from __future__ import annotations

import ast
import hashlib
import inspect
import json
import textwrap
from dataclasses import dataclass, field
from typing import Callable, Literal

import pandas as pd

# ---------------------------------------------------------------------------
# FactorSpec
# ---------------------------------------------------------------------------

NullPolicy = Literal["nan_before_warmup_only"]


@dataclass(frozen=True)
class FactorSpec:
    """Metadata for one registered factor.

    Attributes:
        name: Unique factor name (e.g. ``"rsi_14"``).
        category: Category label (e.g. ``"momentum"``).
        warmup_bars: Number of leading bars that may be NaN. Declared
            explicitly, never inferred from parameters.
        inputs: OHLCV column names the compute function reads (e.g.
            ``["close"]``). Documented for audit; the compute function
            receives the full DataFrame.
        output_dtype: Expected output dtype as a string (e.g.
            ``"float64"``).
        compute: Top-level named callable ``(DataFrame) -> Series``.
            Must be defined at module scope; lambdas and nested functions
            are rejected.
        docstring: Non-empty human docstring. Excluded from feature_version
            hash.
        null_policy: Only ``"nan_before_warmup_only"`` permitted in D1.
    """

    name: str
    category: str
    warmup_bars: int
    inputs: list[str]
    output_dtype: str
    compute: Callable[[pd.DataFrame], pd.Series]
    docstring: str
    null_policy: NullPolicy = "nan_before_warmup_only"

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("FactorSpec.name must be non-empty")
        if not self.category:
            raise ValueError("FactorSpec.category must be non-empty")
        if self.warmup_bars < 0:
            raise ValueError(f"warmup_bars must be >= 0, got {self.warmup_bars}")
        if not self.inputs:
            raise ValueError("FactorSpec.inputs must be non-empty")
        if self.output_dtype not in {"float64", "int64"}:
            raise ValueError(
                f"FactorSpec.output_dtype must be 'float64' or 'int64', "
                f"got {self.output_dtype!r}"
            )
        if not self.docstring or not self.docstring.strip():
            raise ValueError(f"Factor {self.name!r} missing non-empty docstring")
        if self.null_policy != "nan_before_warmup_only":
            raise ValueError(
                f"Factor {self.name!r}: null_policy must be "
                f"'nan_before_warmup_only' in D1, got {self.null_policy!r}"
            )
        _assert_top_level_callable(self.compute, self.name)


def _assert_top_level_callable(fn: Callable, factor_name: str) -> None:
    """Reject lambdas, nested functions, and dynamically-generated callables.

    ``inspect.getsource`` is only reliable for top-level named functions
    across Python versions. Non-top-level callables would make
    ``feature_version`` non-deterministic.
    """
    if not callable(fn):
        raise TypeError(f"Factor {factor_name!r}: compute must be callable")

    qualname = getattr(fn, "__qualname__", "")
    name = getattr(fn, "__name__", "")

    if name == "<lambda>":
        raise TypeError(
            f"Factor {factor_name!r}: lambdas are prohibited. "
            f"Use a top-level `def` in a module."
        )
    # __qualname__ for nested/local functions contains "<locals>".
    if "<locals>" in qualname:
        raise TypeError(
            f"Factor {factor_name!r}: nested/local functions are prohibited. "
            f"Use a top-level `def` in a module (qualname={qualname!r})."
        )
    # Dynamically-generated callables without a real source file.
    module = inspect.getmodule(fn)
    if module is None or not getattr(module, "__file__", None):
        raise TypeError(
            f"Factor {factor_name!r}: compute must be defined in a real "
            f"source module; dynamically-generated callables are prohibited."
        )
    # inspect.getsource must succeed now so registration fails loudly, not
    # at feature_version computation time.
    try:
        inspect.getsource(fn)
    except (OSError, TypeError) as exc:
        raise TypeError(
            f"Factor {factor_name!r}: inspect.getsource failed ({exc}). "
            f"compute must be a top-level named function with retrievable source."
        ) from exc


# ---------------------------------------------------------------------------
# FactorRegistry
# ---------------------------------------------------------------------------


@dataclass
class FactorRegistry:
    """Holds registered factors. Order of registration is preserved but
    outputs of :meth:`canonical_metadata` are sorted by name for
    determinism."""

    _specs: dict[str, FactorSpec] = field(default_factory=dict)

    def register(self, spec: FactorSpec) -> None:
        """Register a factor. Duplicate names are rejected."""
        if spec.name in self._specs:
            raise ValueError(
                f"Factor name collision: {spec.name!r} already registered"
            )
        self._specs[spec.name] = spec

    def get(self, name: str) -> FactorSpec:
        if name not in self._specs:
            raise KeyError(f"Unknown factor: {name!r}")
        return self._specs[name]

    def list_names(self) -> list[str]:
        return sorted(self._specs.keys())

    def max_warmup(self, names: list[str]) -> int:
        """Maximum warmup bars across the given factor names.

        Returns 0 for an empty list. Unknown names raise KeyError.
        """
        if not names:
            return 0
        return max(self.get(n).warmup_bars for n in names)

    def compute_all(
        self,
        df: pd.DataFrame,
        names: list[str] | None = None,
    ) -> pd.DataFrame:
        """Compute the listed factors (or all) on ``df``.

        The input DataFrame is not mutated. The returned DataFrame has the
        same index as ``df`` and one column per factor.

        Post-warmup NaN is a build failure: raises ValueError naming the
        offending factor.
        """
        if names is None:
            names = self.list_names()

        out: dict[str, pd.Series] = {}
        n_rows = len(df)

        for name in names:
            spec = self.get(name)
            series = spec.compute(df)
            if not isinstance(series, pd.Series):
                raise TypeError(
                    f"Factor {name!r} compute returned "
                    f"{type(series).__name__}, expected pd.Series"
                )
            if len(series) != n_rows:
                raise ValueError(
                    f"Factor {name!r} returned {len(series)} rows, "
                    f"expected {n_rows}"
                )
            if not series.index.equals(df.index):
                raise ValueError(
                    f"Factor {name!r} returned a Series with a different "
                    f"index than the input DataFrame"
                )
            series = series.astype(spec.output_dtype)

            # Enforce null policy: NaN only allowed before warmup.
            if spec.warmup_bars < n_rows:
                post_warmup = series.iloc[spec.warmup_bars :]
                if post_warmup.isna().any():
                    first_bad_pos = int(post_warmup.isna().to_numpy().argmax())
                    raise ValueError(
                        f"Factor {name!r} produced NaN after warmup "
                        f"(warmup_bars={spec.warmup_bars}, first bad offset "
                        f"after warmup={first_bad_pos}). "
                        f"Null policy {spec.null_policy!r} forbids this."
                    )
            out[name] = series

        return pd.DataFrame(out, index=df.index)

    def menu_for_prompt(self) -> str:
        """Formatted factor menu string (used by the Phase 2B Proposer).

        Safe to call now — it contains no prompt-contamination material.
        """
        lines = ["# Available factors", ""]
        for name in self.list_names():
            spec = self._specs[name]
            summary = spec.docstring.strip().splitlines()[0]
            lines.append(
                f"- {spec.name} [{spec.category}, warmup={spec.warmup_bars}]: "
                f"{summary}"
            )
        return "\n".join(lines)

    def canonical_metadata(self) -> dict:
        """Deterministic metadata dict used for feature_version hashing.

        Per factor (sorted by name):
            - name
            - category
            - warmup_bars
            - inputs (sorted for determinism)
            - output_dtype
            - null_policy
            - compute_source_sha256 (SHA256 of :func:`_source_without_docstring`
              applied to the compute function)

        The function's embedded docstring is stripped before hashing so
        editing a docstring does NOT bump ``feature_version`` — this
        matches the CLAUDE.md hard constraint. The ``FactorSpec.docstring``
        field is likewise excluded from the metadata.
        """
        meta: dict[str, dict] = {}
        for name in sorted(self._specs.keys()):
            spec = self._specs[name]
            source_stripped = _source_without_docstring(spec.compute)
            source_sha = hashlib.sha256(
                source_stripped.encode("utf-8")
            ).hexdigest()
            meta[name] = {
                "name": spec.name,
                "category": spec.category,
                "warmup_bars": spec.warmup_bars,
                "inputs": sorted(spec.inputs),
                "output_dtype": spec.output_dtype,
                "null_policy": spec.null_policy,
                "compute_source_sha256": source_sha,
            }
        return meta


def _source_without_docstring(fn: Callable) -> str:
    """Return the compute function's source with its embedded docstring stripped.

    Uses :func:`ast.parse` + :func:`ast.unparse` so the output is a canonical
    representation that ignores formatting noise (e.g. re-flowing the
    docstring would otherwise alter the source). ``ast.unparse`` is
    deterministic within a Python minor version, which is sufficient
    for single-machine research reproducibility.

    This function is NOT part of the public registry API; it is an
    implementation detail of :meth:`FactorRegistry.canonical_metadata`.
    """
    raw = inspect.getsource(fn)
    # Dedent in case the function was written with leading indentation
    # (unlikely for our top-level functions, but safe).
    src = textwrap.dedent(raw)
    tree = ast.parse(src)
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # Strip embedded docstring.
            if (
                node.body
                and isinstance(node.body[0], ast.Expr)
                and isinstance(node.body[0].value, ast.Constant)
                and isinstance(node.body[0].value.value, str)
            ):
                node.body = node.body[1:]
                if not node.body:
                    node.body = [ast.Pass()]
            # Normalize function name — factor identity comes from
            # FactorSpec.name, not the def name.
            node.name = "_compute"
    return ast.unparse(tree)


# ---------------------------------------------------------------------------
# feature_version
# ---------------------------------------------------------------------------


def compute_feature_version(registry: FactorRegistry) -> str:
    """SHA256 of the registry's canonical metadata, JSON-serialized.

    JSON is emitted with ``sort_keys=True`` and no whitespace variance so
    the hash is stable across Python runs. Full hex digest is returned;
    callers can truncate if they wish.
    """
    meta = registry.canonical_metadata()
    payload = json.dumps(meta, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# register_factors — singleton bootstrap
# ---------------------------------------------------------------------------


_GLOBAL_REGISTRY: FactorRegistry | None = None


def get_registry() -> FactorRegistry:
    """Return the process-wide registry, lazily bootstrapped with the 18
    core factors on first access.

    Tests that need a fresh registry should construct ``FactorRegistry()``
    directly instead of using this helper.
    """
    global _GLOBAL_REGISTRY
    if _GLOBAL_REGISTRY is None:
        registry = FactorRegistry()
        _bootstrap_core_factors(registry)
        _GLOBAL_REGISTRY = registry
    return _GLOBAL_REGISTRY


def reset_registry() -> None:
    """Force the global registry to re-bootstrap on next ``get_registry``.

    Only used by tests that mutate registered functions.
    """
    global _GLOBAL_REGISTRY
    _GLOBAL_REGISTRY = None


def _bootstrap_core_factors(registry: FactorRegistry) -> None:
    """Register the 18 core factors on the given registry.

    The original D1 set had 14 factors. D5 (Baselines in DSL) promoted 4
    additional factors from the deferred list to support the
    volatility_breakout and mean_reversion baselines:
    ``close``, ``sma_24``, ``bb_upper_24_2``, ``zscore_48``.

    Factor modules are imported here (not at top-level) to avoid import
    cycles with anything that may eventually import ``factors/__init__.py``.
    """
    # Local imports guarded inside the function — see docstring.
    from factors import (  # noqa: PLC0415
        momentum,
        moving_averages,
        price,
        returns,
        structural,
        volatility,
        volume,
    )

    for spec in (
        price.SPEC_CLOSE,
        returns.SPEC_RETURN_1H,
        returns.SPEC_RETURN_24H,
        returns.SPEC_RETURN_168H,
        moving_averages.SPEC_SMA_20,
        moving_averages.SPEC_SMA_24,
        moving_averages.SPEC_SMA_50,
        moving_averages.SPEC_EMA_12,
        moving_averages.SPEC_EMA_26,
        volatility.SPEC_BB_UPPER_24_2,
        volatility.SPEC_ZSCORE_48,
        volatility.SPEC_REALIZED_VOL_24H,
        volatility.SPEC_ATR_14,
        momentum.SPEC_RSI_14,
        momentum.SPEC_MACD_HIST,
        volume.SPEC_VOLUME_ZSCORE_24H,
        structural.SPEC_HOUR_OF_DAY,
        structural.SPEC_DAY_OF_WEEK,
    ):
        registry.register(spec)

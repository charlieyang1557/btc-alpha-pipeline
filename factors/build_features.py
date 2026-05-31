"""Build the canonical factor parquet covering the full OHLCV range.

Usage:
    python -m factors.build_features --pair BTCUSDT --interval 1h
    python -m factors.build_features --force-rebuild

Hard rules (enforced here, see PHASE2_BLUEPRINT.md D1):
- The factor parquet is computed over the **full OHLCV range** of the
  canonical raw parquet. There is no CLI flag that restricts the output
  to a date subset.
- The pyarrow metadata on the output parquet carries ``feature_version``
  (SHA256 of the canonical registry metadata) and ``built_at_utc``.
- On any downstream read, if the stored ``feature_version`` differs
  from the live registry's ``compute_feature_version``, the parquet MUST
  be force-rebuilt. See :func:`load_features_or_rebuild`.
- ``build_features`` never mutates the raw parquet.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from factors.registry import FactorRegistry, compute_feature_version, get_registry

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%SZ",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_RAW_PATH = PROJECT_ROOT / "data" / "raw" / "btcusdt_1h.parquet"
DEFAULT_FEATURES_PATH = PROJECT_ROOT / "data" / "features" / "btcusdt_1h_features.parquet"
DEFAULT_FUNDING_PATH = PROJECT_ROOT / "data" / "raw" / "btcusdt_funding_8h.parquet"

METADATA_KEY_FEATURE_VERSION = b"feature_version"
METADATA_KEY_BUILT_AT = b"built_at_utc"
METADATA_KEY_SOURCE = b"source_parquet"
METADATA_KEY_FACTOR_NAMES = b"factor_names"


# ---------------------------------------------------------------------------
# Core build
# ---------------------------------------------------------------------------


def load_raw_ohlcv(path: Path) -> pd.DataFrame:
    """Load the canonical raw OHLCV parquet.

    The raw parquet uses a RangeIndex and keeps ``open_time_utc`` as a
    UTC-aware datetime column. Strategies and factors rely on this
    layout; callers of ``build_features`` should not reshape it.
    """
    df = pd.read_parquet(path)
    if "open_time_utc" not in df.columns:
        raise ValueError(f"Raw parquet at {path} missing 'open_time_utc' column")
    if not isinstance(df["open_time_utc"].dtype, pd.DatetimeTZDtype):
        raise ValueError(
            f"Raw parquet at {path} has non-timezone-aware 'open_time_utc'"
        )
    df = df.sort_values("open_time_utc").reset_index(drop=True)
    return df


def load_funding(path: Path) -> pd.DataFrame:
    """Load the canonical 8h funding settlement parquet (read-only).

    Returns the funding settlement frame sorted by ``open_time_utc`` ascending,
    with a UTC-aware ``open_time_utc`` column and a ``funding_rate`` column.
    Raises if the file is missing or mis-typed.
    """
    df = pd.read_parquet(path)
    if "open_time_utc" not in df.columns:
        raise ValueError(f"Funding parquet at {path} missing 'open_time_utc' column")
    if "funding_rate" not in df.columns:
        raise ValueError(f"Funding parquet at {path} missing 'funding_rate' column")
    if not isinstance(df["open_time_utc"].dtype, pd.DatetimeTZDtype):
        raise ValueError(
            f"Funding parquet at {path} has non-timezone-aware 'open_time_utc'"
        )
    return df.sort_values("open_time_utc").reset_index(drop=True)


def build_features_df(
    raw_df: pd.DataFrame,
    registry: FactorRegistry,
    funding_df: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Compute all registered factors over the full raw DataFrame.

    Returns a DataFrame indexed the same way as ``raw_df`` with columns:
    ``open_time_utc`` plus one column per factor. The ``open_time_utc``
    column is preserved so downstream consumers can join back to the raw
    feed on the primary key.

    Routing (Path A Phase B): OHLCV factors (``input_source="ohlcv"``) compute
    on ``raw_df``. Funding factors (``input_source="funding"``) do NOT compute
    on ``raw_df`` (it has no ``funding_rate`` column) — they compute on the 8h
    ``funding_df`` settlement frame and are carried onto the 1h grid by a
    backward as-of join (``factors.funding_align.carry_funding_to_bars``). If
    ``funding_df`` is None, funding factors are skipped (no funding columns are
    produced) so callers that only have OHLCV continue to work unchanged.
    """
    ohlcv_names = registry.list_names(input_source="ohlcv")
    funding_names = registry.list_names(input_source="funding")
    logger.info(
        "Computing %d OHLCV factors over %d bars (%s -> %s)",
        len(ohlcv_names),
        len(raw_df),
        raw_df["open_time_utc"].iloc[0].isoformat(),
        raw_df["open_time_utc"].iloc[-1].isoformat(),
    )
    factor_df = registry.compute_all(raw_df, ohlcv_names)
    out = pd.concat([raw_df[["open_time_utc"]], factor_df], axis=1)

    if funding_names:
        if funding_df is None:
            # OHLCV-only consumers (e.g. DSL-compiler unit tests that reference
            # only OHLCV factors) may call without a funding frame. Funding
            # factors are SKIPPED, not computed on the OHLCV frame — they have
            # no funding_rate column. The production build (:func:`build_features`)
            # raises if the funding parquet is missing, so a real build never
            # silently drops funding columns.
            logger.warning(
                "build_features_df: %d funding factor(s) registered (%s) but no "
                "funding_df provided — SKIPPING funding factors (OHLCV-only "
                "frame). The production build requires the funding parquet.",
                len(funding_names),
                funding_names,
            )
            return out
        from factors.funding_align import carry_funding_to_bars  # noqa: PLC0415

        logger.info(
            "Computing %d funding factors over %d settlements then carrying "
            "onto the 1h grid",
            len(funding_names),
            len(funding_df),
        )
        funding_feat = registry.compute_all(
            funding_df, funding_names, input_source="funding"
        )
        funding_feat = pd.concat(
            [funding_df[["open_time_utc"]], funding_feat], axis=1
        )
        out = carry_funding_to_bars(out, funding_feat, funding_names)
    return out


def write_features_parquet(
    features_df: pd.DataFrame,
    output_path: Path,
    feature_version: str,
    source_parquet: Path,
) -> None:
    """Write the factor parquet with feature_version metadata embedded."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    table = pa.Table.from_pandas(features_df, preserve_index=False)

    # Merge our metadata into the existing pandas/schema metadata so we
    # don't lose pyarrow's round-trip hints.
    existing_meta = dict(table.schema.metadata or {})
    built_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    factor_names = [c for c in features_df.columns if c != "open_time_utc"]
    existing_meta[METADATA_KEY_FEATURE_VERSION] = feature_version.encode("utf-8")
    existing_meta[METADATA_KEY_BUILT_AT] = built_at.encode("utf-8")
    existing_meta[METADATA_KEY_SOURCE] = str(source_parquet).encode("utf-8")
    existing_meta[METADATA_KEY_FACTOR_NAMES] = json.dumps(
        factor_names, separators=(",", ":")
    ).encode("utf-8")

    table = table.replace_schema_metadata(existing_meta)
    pq.write_table(table, output_path, compression="snappy")
    logger.info(
        "Wrote %s (feature_version=%s, built_at=%s, factors=%d)",
        output_path,
        feature_version[:12],
        built_at,
        len(factor_names),
    )


def read_feature_version(path: Path) -> str | None:
    """Read the stored ``feature_version`` from a feature parquet.

    Returns ``None`` if the file doesn't exist or the key is missing.
    """
    if not path.exists():
        return None
    meta = pq.read_metadata(path).metadata
    if meta is None or METADATA_KEY_FEATURE_VERSION not in meta:
        return None
    return meta[METADATA_KEY_FEATURE_VERSION].decode("utf-8")


def build_features(
    raw_path: Path = DEFAULT_RAW_PATH,
    output_path: Path = DEFAULT_FEATURES_PATH,
    registry: FactorRegistry | None = None,
    funding_path: Path | None = DEFAULT_FUNDING_PATH,
) -> Path:
    """Build the full-coverage factor parquet. Returns the written path.

    Always computes over the entire raw dataset — no date-range slicing.

    When funding factors are registered, ``funding_path`` (the 8h settlement
    parquet) is loaded and its factors are carried onto the 1h grid. Passing
    ``funding_path=None`` skips the funding load — callers with no funding data
    must also have no funding factors registered, else ``build_features_df``
    raises.
    """
    if registry is None:
        registry = get_registry()

    raw_df = load_raw_ohlcv(raw_path)
    funding_df = None
    if registry.list_names(input_source="funding"):
        # Production build MUST include funding columns when funding factors are
        # registered — never silently drop them.
        if funding_path is None or not Path(funding_path).exists():
            raise ValueError(
                f"Funding factors are registered but the funding parquet "
                f"({funding_path}) is missing; the production build cannot "
                f"silently drop funding columns. Run the funding ingestion "
                f"first or pass an explicit funding_path."
            )
        funding_df = load_funding(funding_path)
    features_df = build_features_df(raw_df, registry, funding_df=funding_df)
    feature_version = compute_feature_version(registry)
    write_features_parquet(features_df, output_path, feature_version, raw_path)
    return output_path


def load_features_or_rebuild(
    raw_path: Path = DEFAULT_RAW_PATH,
    features_path: Path = DEFAULT_FEATURES_PATH,
    registry: FactorRegistry | None = None,
    funding_path: Path | None = DEFAULT_FUNDING_PATH,
) -> pd.DataFrame:
    """Read the feature parquet, rebuilding first if feature_version is stale.

    This is the canonical consumer-side entrypoint. No silent "use stale
    data" fallback is permitted: if the stored version doesn't match the
    live registry hash, we rebuild before returning the DataFrame. ``funding_path``
    is forwarded to :func:`build_features` for the funding-factor routing.
    """
    if registry is None:
        registry = get_registry()

    live_version = compute_feature_version(registry)
    stored_version = read_feature_version(features_path)

    if stored_version != live_version:
        logger.info(
            "Feature parquet missing or stale (stored=%s, live=%s) — rebuilding.",
            (stored_version or "<none>")[:12],
            live_version[:12],
        )
        build_features(raw_path, features_path, registry, funding_path=funding_path)

    return pd.read_parquet(features_path)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build the canonical factor parquet over the FULL raw OHLCV "
            "range. Date-range subsetting is deliberately not supported; "
            "consumers slice at read time."
        ),
    )
    parser.add_argument(
        "--pair",
        type=str,
        default="BTCUSDT",
        help="Trading pair label (metadata only; does not change paths)",
    )
    parser.add_argument(
        "--interval",
        type=str,
        default="1h",
        help="Bar interval label (metadata only; does not change paths)",
    )
    parser.add_argument(
        "--raw",
        type=Path,
        default=DEFAULT_RAW_PATH,
        help="Path to the raw OHLCV parquet",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_FEATURES_PATH,
        help="Path to write the factor parquet",
    )
    parser.add_argument(
        "--funding",
        type=Path,
        default=DEFAULT_FUNDING_PATH,
        help="Path to the 8h funding settlement parquet (carried onto 1h bars "
        "when funding factors are registered)",
    )
    parser.add_argument(
        "--force-rebuild",
        action="store_true",
        help="Rebuild even if the stored feature_version matches the live one",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Compute and report but do not write the parquet",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point. Returns a process exit code (0 on success)."""
    args = _parse_args(argv)

    registry = get_registry()
    live_version = compute_feature_version(registry)
    stored_version = read_feature_version(args.output)

    if not args.force_rebuild and stored_version == live_version:
        logger.info(
            "Feature parquet up to date (feature_version=%s). No action.",
            live_version[:12],
        )
        return 0

    raw_df = load_raw_ohlcv(args.raw)
    funding_df = None
    if args.funding is not None and registry.list_names(input_source="funding"):
        funding_df = load_funding(args.funding)
    features_df = build_features_df(raw_df, registry, funding_df=funding_df)

    if args.dry_run:
        logger.info(
            "Dry run: computed %d factors over %d bars; NOT writing output.",
            len(features_df.columns) - 1,
            len(features_df),
        )
        return 0

    write_features_parquet(features_df, args.output, live_version, args.raw)
    return 0


if __name__ == "__main__":
    sys.exit(main())

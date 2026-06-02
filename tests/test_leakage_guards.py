# tests/test_leakage_guards.py
"""Leakage guards G1-G4 for the Path B factor + sizing extension.

G1 (this file, Task 1): static AST scan banning future-touching ops inside
factor compute functions, wired into FactorRegistry.register().
G2 (Task 2): registry-derived shuffle/reverse/delete sentinel.
G3 (Task 3): per-operator known-value + ternary-sizing causality.
G4a (Task 4a): generic registry<->EXPECTED_FACTORS sync + future-bar invariance.
"""
from __future__ import annotations

import ast
import inspect as _inspect
import textwrap

import numpy as np
import pandas as pd
import pytest

from factors.registry import (
    FactorRegistry,
    FactorSpec,
    _assert_no_future_ops,
    _bootstrap_core_factors,
)
from strategies.dsl import Condition
from strategies.dsl_compiler import _compile_condition
from tests.test_factors import EXPECTED_FACTORS

try:
    from strategies.dsl import SizingSpec
    from strategies.dsl_compiler import _compile_sizing
    _SIZING_AVAILABLE = True
except ImportError:
    _SIZING_AVAILABLE = False


def compute_leaky_shift(df: pd.DataFrame) -> pd.Series:
    """Module-level leaky compute fn (negative shift) for the register() gate test.

    Defined at module scope so its __qualname__ contains no '<locals>' segment,
    allowing FactorSpec construction to succeed (passes _assert_top_level_callable)
    while register() remains the sole G1 gate.
    """
    return df["close"].shift(-1)


@pytest.fixture
def core_registry() -> FactorRegistry:
    reg = FactorRegistry()
    _bootstrap_core_factors(reg)
    return reg


class TestG1ExistingCorpusClean:
    """G1 must NOT false-positive on the already-registered causal factors.

    This is the load-bearing first check: if the scanner rejects any of the
    legitimately-causal existing compute functions, it is unusable as a
    register()-time gate. Run this BEFORE trusting any positive detection.
    """

    def test_all_registered_factors_pass_scanner(self, core_registry):
        names = core_registry.list_names()
        assert len(names) >= 18
        for name in names:
            spec = core_registry.get(name)
            # Must not raise — every shipped factor is causal by construction.
            _assert_no_future_ops(spec.compute, name)


class TestG1BannedOps:
    """G1 must reject each future-touching construct."""

    def test_negative_shift_rejected(self):
        def compute_bad_shift(df: pd.DataFrame) -> pd.Series:
            return df["close"].shift(-1)

        with pytest.raises(ValueError, match="shift"):
            _assert_no_future_ops(compute_bad_shift, "bad_shift")

    def test_bfill_rejected(self):
        def compute_bad_bfill(df: pd.DataFrame) -> pd.Series:
            return df["close"].bfill()

        with pytest.raises(ValueError, match="bfill|backfill"):
            _assert_no_future_ops(compute_bad_bfill, "bad_bfill")

    def test_backfill_rejected(self):
        def compute_bad_backfill(df: pd.DataFrame) -> pd.Series:
            return df["close"].backfill()

        with pytest.raises(ValueError, match="bfill|backfill"):
            _assert_no_future_ops(compute_bad_backfill, "bad_backfill")

    def test_fillna_bfill_method_rejected(self):
        def compute_bad_fillna(df: pd.DataFrame) -> pd.Series:
            return df["close"].fillna(method="bfill")

        with pytest.raises(ValueError, match="bfill|backfill|fillna"):
            _assert_no_future_ops(compute_bad_fillna, "bad_fillna")

    def test_rolling_center_true_rejected(self):
        def compute_bad_center(df: pd.DataFrame) -> pd.Series:
            return df["close"].rolling(24, center=True).mean()

        with pytest.raises(ValueError, match="center"):
            _assert_no_future_ops(compute_bad_center, "bad_center")

    def test_bare_expanding_rejected(self):
        def compute_bad_expanding(df: pd.DataFrame) -> pd.Series:
            return df["close"].expanding().mean()

        with pytest.raises(ValueError, match="expanding"):
            _assert_no_future_ops(compute_bad_expanding, "bad_expanding")

    def test_full_series_mean_rejected(self):
        def compute_bad_globalmean(df: pd.DataFrame) -> pd.Series:
            return df["close"] - df["close"].mean()

        with pytest.raises(ValueError, match="mean|full-series|global"):
            _assert_no_future_ops(compute_bad_globalmean, "bad_globalmean")


class TestG1AllowedOps:
    """G1 must ALLOW legitimate causal constructs."""

    def test_rolling_mean_allowed(self):
        def compute_ok_rolling(df: pd.DataFrame) -> pd.Series:
            return df["close"].rolling(24).mean()

        _assert_no_future_ops(compute_ok_rolling, "ok_rolling")  # no raise

    def test_ewm_adjust_false_allowed(self):
        def compute_ok_ewm(df: pd.DataFrame) -> pd.Series:
            return df["close"].ewm(span=12, adjust=False).mean()

        _assert_no_future_ops(compute_ok_ewm, "ok_ewm")  # no raise

    def test_positive_shift_allowed(self):
        def compute_ok_shift(df: pd.DataFrame) -> pd.Series:
            return df["close"] - df["close"].shift(1)

        _assert_no_future_ops(compute_ok_shift, "ok_shift")  # no raise

    def test_expanding_min_periods_chained_mean_allowed(self):
        def compute_ok_expanding(df: pd.DataFrame) -> pd.Series:
            return df["close"].expanding(min_periods=24).mean()

        _assert_no_future_ops(compute_ok_expanding, "ok_expanding")  # no raise


class TestG1WiredIntoRegister:
    """G1 is wired into register() — a leaky factor cannot be admitted to the registry.

    ``compute_leaky_shift`` is defined at module scope so its ``__qualname__``
    contains no ``<locals>`` segment; this means ``FactorSpec`` construction
    succeeds (passes ``_assert_top_level_callable``).  Only ``reg.register(spec)``
    is inside the ``pytest.raises`` block, proving that ``register()`` is the
    sole G1 gate.
    """

    def test_register_rejects_leaky_factor(self):
        reg = FactorRegistry()

        # Construction must succeed: module-level fn passes _assert_top_level_callable
        # and __post_init__ no longer calls G1.
        spec = FactorSpec(
            name="leaky_demo",
            category="test",
            warmup_bars=0,
            inputs=["close"],
            output_dtype="float64",
            compute=compute_leaky_shift,
            docstring="Leaky demo factor (must be rejected).",
        )

        # register() is the sole G1 gate.
        with pytest.raises(ValueError, match="shift"):
            reg.register(spec)


def _synthetic_ohlcv(n: int = 800, seed: int = 7) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2021-01-01", periods=n, freq="1h", tz="UTC")
    close = 30000.0 + np.cumsum(rng.normal(0, 50, n))
    high = close + np.abs(rng.normal(0, 30, n))
    low = close - np.abs(rng.normal(0, 30, n))
    open_ = close - rng.normal(0, 20, n)
    vol = np.abs(rng.normal(1000, 200, n))
    return pd.DataFrame(
        {
            "open_time_utc": idx,
            "open": open_,
            "high": high,
            "low": low,
            "close": close,
            "volume": vol,
        }
    )


def _synthetic_funding(n: int = 800, seed: int = 7) -> pd.DataFrame:
    """Synthetic 8h funding settlement frame for the funding-source factors.

    Funding factors are tagged ``input_source="funding"`` and read a
    ``funding_rate`` column on the 8h settlement frame, NOT the OHLCV frame.
    The leakage sentinels route a factor to its matching input by this field
    (mirroring the build's routing) — without weakening any invariance check.
    """
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2021-01-01", periods=n, freq="8h", tz="UTC")
    return pd.DataFrame(
        {
            "open_time_utc": idx,
            "funding_rate": rng.normal(0, 1e-4, n),
        }
    )


def _synthetic_basis(n: int = 1500, seed: int = 17) -> pd.DataFrame:
    """Synthetic native-1h basis_rel frame for the basis-source factors.

    Basis factors are tagged ``input_source="basis"`` and read a ``basis_rel``
    column on the 1h grid (derived from markprice + spot inner-join). The leakage
    sentinels route a factor to its matching input by this field.
    """
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2021-01-01", periods=n, freq="h", tz="UTC")
    return pd.DataFrame(
        {
            "open_time_utc": idx,
            "basis_rel": rng.normal(0, 2e-4, n),
        }
    )


def _synthetic_oi(n: int = 3000, seed: int = 23) -> pd.DataFrame:
    """Synthetic native-1h OI (contracts) frame for the OI-source factors.

    OI factors are tagged ``input_source="oi"`` and read a ``sum_open_interest``
    column on the 1h grid (from data/raw/btcusdt_oi_1h.parquet). The leakage
    sentinels route a factor to its matching input by this field.

    All values are strictly > 0 (no zero-poison bars in this helper — zero-poison
    behaviour is tested separately in test_oi_factors.py).
    """
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2021-01-01", periods=n, freq="h", tz="UTC")
    return pd.DataFrame(
        {
            "open_time_utc": idx,
            "sum_open_interest": np.abs(rng.normal(5e6, 5e5, n)) + 1e5,  # strictly > 0
        }
    )


def _synthetic_input_for(spec) -> pd.DataFrame:
    """Return the synthetic input frame matching a factor spec's input_source.

    Routes funding-source factors to the 8h settlement frame, basis-source factors
    to the native-1h basis_rel frame, OI-source factors to the native-1h OI frame,
    and OHLCV-source factors to the OHLCV frame, mirroring ``factors.build_features``
    so the sentinels run each factor against an input it can read.
    """
    n = 3000  # large enough that every factor warms up before any truncation k
    # (basis_pct_rank_2160 and oi_velocity_ewm_240_pctrank_2160 have warmup_bars=2160;
    # need n > 2160 + margin for the truncation k=1200→k=2500 check)
    if getattr(spec, "input_source", "ohlcv") == "funding":
        return _synthetic_funding(n=n)
    if getattr(spec, "input_source", "ohlcv") == "basis":
        return _synthetic_basis(n=n)
    if getattr(spec, "input_source", "ohlcv") == "oi":
        return _synthetic_oi(n=n)
    return _synthetic_ohlcv(n=n)


_SENTINEL_REG = FactorRegistry()
_bootstrap_core_factors(_SENTINEL_REG)
_SENTINEL_NAMES = _SENTINEL_REG.list_names()


# Factors that are legitimately reversal-invariant and therefore exempt from
# the time-reversal sentinel. Their causality is covered in full by
# TestG2FutureBarInvarianceSentinel.test_truncation_invariance (the
# load-bearing future-bar check), so exemption here removes no causality
# coverage. Two classes:
#   (1) pointwise / calendar factors (per-bar, no temporal window) — close,
#       hour_of_day, day_of_week.
#   (2) ORDER-INVARIANT (commutative) window aggregates — this test compares
#       f(window) computed in forward order against f(SAME window) in reversed
#       order, so output is unchanged iff f is commutative over its window.
#       mean/std qualify (a window's mean/std is independent of element order),
#       so sma_20/sma_24/sma_50 and bb_upper_24_2 (=SMA+2*std) are reversal-
#       invariant by arithmetic necessity, NOT a future-bar leak.
#       Do NOT extend this set to ORDER-SENSITIVE rolling factors: EMA (recency-
#       weighted), returns / pct_change (first-vs-last), and z-scores / ATR
#       (current bar enters at the window edge) are direction-sensitive and
#       MUST remain reversal-tested — they correctly stay out of this set.
_REVERSAL_EXEMPT = frozenset(
    {
        # pointwise / calendar factors (per-bar, no temporal window → reversal-
        # invariant by construction; causality covered by truncation-invariance)
        "close",
        "hour_of_day",
        "day_of_week",
        "intrabar_push",  # (close-open)/((high-low)+1e-9) — per-bar/pointwise, warmup=0 -> reversal-invariant
        "funding_sign",  # np.sign(funding_rate) — per-settlement/pointwise, warmup=0 -> reversal-invariant
        "basis_sign",  # np.sign(basis_rel) — per-bar/pointwise, warmup=0 -> reversal-invariant
        # ORDER-INVARIANT (commutative) window aggregates: mean/std over a fixed
        # window are independent of element order, so forward==reversed.
        "sma_20",
        "sma_24",
        "sma_50",
        "bb_upper_24_2",
    }
)
# NOTE: funding_ewm_30/60 (recency-weighted) and funding_pct_rank_270 (current
# value enters at the window edge) are ORDER-SENSITIVE and correctly stay OUT of
# this set — they must remain reversal-tested (routed onto the funding frame).
# Similarly basis_ewm_240/480 (recency-weighted) and basis_pct_rank_2160/
# basis_ewm_240_pctrank_2160 (current bar enters at window edge) are
# ORDER-SENSITIVE and stay OUT of this set (routed onto the basis_rel frame).


class TestG2FutureBarInvarianceSentinel:
    """Truncation-invariance: f(df[:k])[:k] == f(df)[:k] for every factor."""

    @pytest.mark.parametrize("name", _SENTINEL_NAMES)
    def test_truncation_invariance(self, name):
        spec = _SENTINEL_REG.get(name)
        df = _synthetic_input_for(spec)  # route OHLCV vs funding/basis-source factors
        # k must exceed the factor's warmup. Basis pct-rank factors have warmup=2160;
        # all OHLCV factors are <= 743; funding factors are <= 270 settlements.
        # Use warmup + 100 as k (minimum margin = 100 bars/settlements past warmup).
        # _synthetic_input_for provides n=3000 so this is always safe.
        warmup = spec.warmup_bars
        k = max(warmup + 100, 1200)
        full = spec.compute(df).to_numpy()
        truncated = spec.compute(df.iloc[:k].copy()).to_numpy()
        assert k > warmup, (
            f"{name}: truncation test vacuous — k={k} <= warmup={warmup}; "
            f"raise n/k above the factor's warmup."
        )
        np.testing.assert_allclose(
            truncated[warmup:k],
            full[warmup:k],
            rtol=1e-9,
            atol=1e-9,
            err_msg=(
                f"{name}: truncated output diverges from full output on the "
                f"shared prefix — factor reads future bars."
            ),
        )

    @pytest.mark.parametrize("name", _SENTINEL_NAMES)
    def test_reversed_input_changes_output(self, name):
        """Reversing time must change a genuinely time-ordered factor.

        A factor whose value is invariant to a full time-reversal is either
        constant or order-independent; for our OHLCV-derived corpus that is a
        red flag the compute ignores temporal ordering. ``close`` (identity)
        and structural calendar factors are exempt — they are pointwise.
        """
        if name in _REVERSAL_EXEMPT:
            pytest.skip(
                "reversal-invariant by design (pointwise or window-symmetric); "
                "causality covered by test_truncation_invariance"
            )
        spec = _SENTINEL_REG.get(name)
        df = _synthetic_input_for(spec)  # route OHLCV vs funding-source factors
        normal = spec.compute(df).to_numpy()
        rev_df = df.iloc[::-1].reset_index(drop=True).copy()
        reversed_out = spec.compute(rev_df).to_numpy()
        warmup = spec.warmup_bars
        a = normal[warmup:]
        b = reversed_out[warmup:][::-1]
        assert not np.allclose(
            a[np.isfinite(a) & np.isfinite(b)],
            b[np.isfinite(a) & np.isfinite(b)],
            rtol=1e-6,
        ), f"{name}: time-reversal left output unchanged — suspicious."


# ---------------------------------------------------------------------------
# G3 — per-operator known-value checks + ternary-sizing causality contract
# ---------------------------------------------------------------------------


class TestG3OperatorKnownValues:
    """Per-operator firing on the documented bar (cur_row / prev_row)."""

    def test_continuous_gt_reads_cur_row_only(self, core_registry):
        # rsi_14 > 70 ; factor_index places rsi_14 at column 0.
        cond = Condition(factor="rsi_14", op=">", value=70.0)
        fn = _compile_condition(cond, {"rsi_14": 0})
        # cur_row above threshold, prev_row below — continuous op uses cur_row.
        assert fn((75.0,), (10.0,)) is True
        assert fn((65.0,), (99.0,)) is False

    def test_crosses_above_reads_both_rows(self, core_registry):
        # sma_20 crosses_above sma_50 : factor-vs-factor cross.
        cond = Condition(factor="sma_20", op="crosses_above", value="sma_50")
        fn = _compile_condition(cond, {"sma_20": 0, "sma_50": 1})
        # prev: sma_20 below sma_50 ; cur: sma_20 above sma_50 -> cross up.
        assert fn((101.0, 100.0), (99.0, 100.0)) is True
        # Already above on both bars -> no fresh cross.
        assert fn((101.0, 100.0), (101.5, 100.0)) is False


# --- Ternary-sizing causality ------------------------------------------------

# Step -1 human-locked sizing param values referenced symbolically. The
# concrete band edges (THETA_PUSH etc.) are fixed at the hypothesis-lock
# step; this guard only asserts the *causal shape*, not the numeric values.
THETA_PUSH_LOW = -0.5   # symbolic; bound at Step -1 lock
THETA_PUSH_HIGH = 0.5   # symbolic; bound at Step -1 lock
SIZE_IN_BAND = 1.0
SIZE_DEFAULT = 0.25


@pytest.mark.skipif(
    not _SIZING_AVAILABLE,
    reason="SizingSpec / _compile_sizing land in Section C (Tasks 13/16); "
    "this G3 contract self-activates once they exist.",
)
class TestG3TernarySizingCausality:
    """The REAL SizingSpec/_compile_sizing reads ONLY cur_row by index."""

    def _spec(self) -> "SizingSpec":
        # SizingSpec(factor, bands=[{lower,upper,size}], default_size)
        return SizingSpec(
            factor="intrabar_push",
            bands=[
                {
                    "lower": THETA_PUSH_LOW,
                    "upper": THETA_PUSH_HIGH,
                    "size": SIZE_IN_BAND,
                }
            ],
            default_size=SIZE_DEFAULT,
        )

    def test_sizing_closure_returns_band_then_default(self, core_registry):
        spec = self._spec()
        # intrabar_push resolved to column 0 of factors_used.
        sizing = _compile_sizing(spec, {"intrabar_push": 0})
        # In-band cur_row value -> SIZE_IN_BAND ; prev_row irrelevant.
        assert sizing((0.0,), (9.9,)) == pytest.approx(SIZE_IN_BAND)
        # Out-of-band cur_row value -> default ; prev_row irrelevant.
        assert sizing((5.0,), (0.0,)) == pytest.approx(SIZE_DEFAULT)

    def test_sizing_ignores_prev_row(self, core_registry):
        """Changing prev_row alone must not change the sizing fraction."""
        spec = self._spec()
        sizing = _compile_sizing(spec, {"intrabar_push": 0})
        a = sizing((0.0,), (0.0,))
        b = sizing((0.0,), (123.0,))
        assert a == b, "sizing read prev_row — that is a causality leak risk"

    def test_sizing_factory_source_has_no_future_index(self):
        """Static AST scan: the closure factory never reads a future bar.

        It must read sizing inputs only via ``cur_row[idx]`` / ``prev_row[idx]``
        (tuple subscription), never via ``self.data[k]`` with a positive k
        (Backtrader forward index = look-ahead) and never via a negative
        tuple/series ``shift``.
        """
        src = textwrap.dedent(_inspect.getsource(_compile_sizing))
        tree = ast.parse(src)

        offenders: list[str] = []
        for node in ast.walk(tree):
            # Ban self.data[<positive int>] — Backtrader forward read.
            if isinstance(node, ast.Subscript):
                val = node.value
                is_self_data = (
                    isinstance(val, ast.Attribute)
                    and val.attr == "data"
                    and isinstance(val.value, ast.Name)
                    and val.value.id == "self"
                )
                if is_self_data:
                    sl = node.slice
                    if isinstance(sl, ast.Constant) and isinstance(
                        sl.value, int
                    ) and sl.value > 0:
                        offenders.append(f"self.data[{sl.value}]")
            # Ban negative shift() anywhere in the factory.
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "shift"
                and node.args
            ):
                a0 = node.args[0]
                if (
                    isinstance(a0, ast.UnaryOp)
                    and isinstance(a0.op, ast.USub)
                ):
                    offenders.append("shift(<negative>)")

        assert not offenders, (
            f"_compile_sizing reads future bars: {offenders}"
        )

    def test_sizing_factory_reads_only_known_row_names(self):
        """Every Name loaded for subscription is cur_row / prev_row / idx.

        Guards against a refactor that smuggles in `self.data` or a global
        future series as the sizing source. Allowed subscript receivers are
        exactly the closure's row tuples.
        """
        src = textwrap.dedent(_inspect.getsource(_compile_sizing))
        tree = ast.parse(src)
        allowed_receivers = {"cur_row", "prev_row"}
        bad: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Subscript) and isinstance(
                node.value, ast.Name
            ):
                if node.value.id not in allowed_receivers:
                    # Allow indexing the precomputed band list / factor_index
                    # by their local names; only flag obvious data sources.
                    if node.value.id in {"self", "data", "feed"}:
                        bad.append(node.value.id)
        assert not bad, f"_compile_sizing subscripts forbidden source: {bad}"


# ---------------------------------------------------------------------------
# G4a — generic registry<->EXPECTED_FACTORS sync + future-bar invariance
# ---------------------------------------------------------------------------


class TestG4aRegistrySync:
    """Generic registry <-> EXPECTED_FACTORS sync (count-agnostic).

    DESIGN INVARIANT: this guard asserts the registry and the canonical
    EXPECTED_FACTORS list are the SAME SET. It does NOT assert any specific
    Path B factor exists — that is Task 4b's job, authored after Section B.
    Keeping the existence check out of this generic guard means Task 4a can
    be authored and run BEFORE the 5 new factors are implemented (it then
    just re-confirms the 18-factor baseline), and the same test body keeps
    holding after the merge bumps both sides to 23.
    """

    def test_registry_matches_expected_factors_set(self, core_registry):
        assert set(core_registry.list_names()) == set(EXPECTED_FACTORS), (
            "registry.list_names() and tests.test_factors.EXPECTED_FACTORS "
            "have drifted; update EXPECTED_FACTORS in the same change that "
            "registers/removes a factor."
        )

    def test_list_names_is_sorted_alphabetical(self, core_registry):
        # registry.list_names() == sorted(self._specs.keys()); EXPECTED_FACTORS
        # is the alphabetical projection of that.
        names = core_registry.list_names()
        assert names == sorted(names)
        assert EXPECTED_FACTORS == sorted(EXPECTED_FACTORS)


# Auto-derived parametrize: future-bar invariance over the LIVE registry, so
# the 5 Path B factors are covered automatically once registered — no name is
# hardcoded here.
# Separate module-level instance from _SENTINEL_REG: pytest @parametrize lists
# must be built at collection time (before fixtures exist), so the fixture
# cannot be reused here. Holds identical state to _SENTINEL_REG by construction.
_G4_REG = FactorRegistry()
_bootstrap_core_factors(_G4_REG)
_G4_NAMES = _G4_REG.list_names()


class TestG4aFutureBarInvariance:
    """Auto-derived truncation-invariance over registry.list_names().

    Mirrors G2's truncation check but is anchored to the registry/EXPECTED
    sync guard so a newly-registered factor is invariance-checked the moment
    it appears in list_names() — without editing this file.
    """

    @pytest.mark.parametrize("name", _G4_NAMES)
    def test_future_bar_invariance(self, name):
        # Larger sample than G2 so every long-lookback factor warms up well before
        # the truncation boundary k. Basis pct-rank factors have warmup=2160;
        # use warmup+100 as k (min margin 100 past warmup) so the test is always
        # non-vacuous. _synthetic_input_for provides n=3000 (safe for all factors).
        spec = _G4_REG.get(name)
        df = _synthetic_input_for(spec)  # route OHLCV vs funding/basis-source factors
        w = spec.warmup_bars
        k = max(w + 100, 1200)
        full = spec.compute(df).to_numpy()
        trunc = spec.compute(df.iloc[:k].copy()).to_numpy()
        assert k > w, (
            f"{name}: truncation test vacuous — k={k} <= warmup={w}; "
            f"raise n/k above the factor's warmup."
        )
        np.testing.assert_allclose(
            trunc[w:k], full[w:k], rtol=1e-9, atol=1e-9,
            err_msg=f"{name}: prefix output changed when tail was truncated.",
        )

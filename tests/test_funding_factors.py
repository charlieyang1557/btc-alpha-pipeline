"""Tests for Path A funding-rate factors (Phase B, Tasks B1-B5).

The funding factors are computed on the 8h settlement series (causal, rolling
over settlement units). They are carried onto the 1h bar grid downstream by
``factors.funding_align.carry_funding_to_bars`` (Task B4). All factors are
top-level named callables, rolling/causal only (must pass the G1-G4 leakage
guards). All UTC. Mirrors the OHLCV factor test conventions.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from factors.funding import funding_sign


# ---------------------------------------------------------------------------
# Task B1: funding_sign
# ---------------------------------------------------------------------------


def test_funding_sign():
    s = pd.Series([0.0002, -0.0001, 0.0, 0.00005])
    out = funding_sign(pd.DataFrame({"funding_rate": s}))
    assert out.tolist() == [1.0, -1.0, 0.0, 1.0]

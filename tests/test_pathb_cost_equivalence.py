# tests/test_pathb_cost_equivalence.py
"""Path B cohort net-return config must equal the Tier-5 15bps spot anchor."""
from __future__ import annotations

import pytest

import scripts.pathb_cost_equivalence as ce


def test_phase4_and_phaseb_anchors_have_identical_fee_and_slippage():
    res = ce.assert_cost_equivalence()
    assert res["fee_bps"] == res["anchor_fee_bps"]
    assert res["slippage_bps"] == res["anchor_slippage_bps"]
    assert res["per_side_bps"] == pytest.approx(15.0, abs=1e-9)
    assert res["equivalent"] is True


def test_mismatched_fee_raises(monkeypatch):
    real = ce._load_cost_model

    def fake(path):
        cm = dict(real(path))
        if path.name == "execution_phase4_15bps.yaml":
            cm["default_fee_bps"] = cm["default_fee_bps"] + 1.0  # break parity
        return cm

    monkeypatch.setattr(ce, "_load_cost_model", fake)
    with pytest.raises(ValueError, match="cost-equivalence"):
        ce.assert_cost_equivalence()

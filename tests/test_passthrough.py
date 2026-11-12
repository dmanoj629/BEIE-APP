"""Fuel pass-through model tests."""

from beie.model.passthrough import FuelPolicy, compute_pump_delta


def test_zero_shock_gives_zero_delta():
    r = compute_pump_delta(0.0, 96.45, 109.29, FuelPolicy.PARTIAL)
    assert r["diesel_delta"] == 0.0
    assert r["petrol_delta"] == 0.0


def test_full_passthrough_greater_than_partial():
    partial = compute_pump_delta(0.25, 96.45, 109.29, FuelPolicy.PARTIAL)
    full = compute_pump_delta(0.25, 96.45, 109.29, FuelPolicy.FULL)
    assert full["diesel_delta"] > partial["diesel_delta"]


def test_held_policy_zero_passthrough():
    r = compute_pump_delta(0.50, 96.45, 109.29, FuelPolicy.HELD)
    assert r["diesel_delta"] == 0.0
    assert r["passthrough_fraction"] == 0.0


def test_new_price_monotone_in_shock():
    """Larger shock → higher new price under same policy."""
    r10 = compute_pump_delta(0.10, 96.45, 109.29, FuelPolicy.PARTIAL)
    r25 = compute_pump_delta(0.25, 96.45, 109.29, FuelPolicy.PARTIAL)
    assert r25["diesel_new"] > r10["diesel_new"]

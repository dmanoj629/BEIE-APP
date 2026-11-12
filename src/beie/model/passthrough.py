"""Administered fuel price pass-through model.

India's pump prices are set by Oil Marketing Companies (OMCs) under government
guidance — not freely market-determined. This module models three explicit
policy regimes as documented in the BEIE ASSUMPTIONS.md.
"""

from __future__ import annotations

from enum import Enum


class FuelPolicy(str, Enum):
    HELD = "held"  # OMCs absorb under-recovery; zero consumer pass-through
    PARTIAL = "partial"  # 50 % pass-through over 3–4 months (default calibration)
    FULL = "full"  # Full economic cost passed to retail prices


# Pass-through fractions by regime
_PASSTHROUGH_FRACTION: dict[FuelPolicy, float] = {
    FuelPolicy.HELD: 0.0,
    FuelPolicy.PARTIAL: 0.50,
    FuelPolicy.FULL: 1.00,
}

# Months to full transmission by regime
_LAG_MONTHS: dict[FuelPolicy, tuple[int, int]] = {
    FuelPolicy.HELD: (0, 0),
    FuelPolicy.PARTIAL: (2, 4),
    FuelPolicy.FULL: (1, 2),
}


def compute_pump_delta(
    crude_delta_pct: float,
    base_diesel_price: float,
    base_petrol_price: float,
    policy: FuelPolicy = FuelPolicy.PARTIAL,
) -> dict[str, float]:
    """Return retail pump price change under a crude shock and policy regime.

    Parameters
    ----------
    crude_delta_pct : fractional crude price change (0.25 → +25 %).
    base_diesel_price : baseline retail diesel price in ₹/litre.
    base_petrol_price : baseline retail petrol price in ₹/litre.
    policy : FuelPolicy regime (default: PARTIAL — 50 % pass-through).

    Returns
    -------
    Dict with diesel_new, petrol_new, diesel_delta, petrol_delta, lag_min, lag_max.
    """
    pt = _PASSTHROUGH_FRACTION[policy]
    lag_min, lag_max = _LAG_MONTHS[policy]

    # Rough cost component: ~40% of retail pump price is base crude cost (rest taxes/margin)
    # Source: PPAC retail price build-up chart
    crude_cost_fraction = 0.40
    effective_delta = crude_delta_pct * crude_cost_fraction * pt

    diesel_delta = base_diesel_price * effective_delta
    petrol_delta = base_petrol_price * effective_delta

    return {
        "diesel_base": round(base_diesel_price, 2),
        "petrol_base": round(base_petrol_price, 2),
        "diesel_new": round(base_diesel_price + diesel_delta, 2),
        "petrol_new": round(base_petrol_price + petrol_delta, 2),
        "diesel_delta": round(diesel_delta, 2),
        "petrol_delta": round(petrol_delta, 2),
        "policy": policy.value,
        "passthrough_fraction": pt,
        "lag_min_months": lag_min,
        "lag_max_months": lag_max,
        "crude_delta_pct": crude_delta_pct,
    }

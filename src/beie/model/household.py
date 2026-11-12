"""Household budget impact model for Karnataka citizens.

Sources:
- MoSPI NSSO Household Consumer Expenditure Survey (HCES) 2022-23 for expenditure shares.
- CPI division weights from mospi_cpi_2026.json (Karnataka).
"""

from __future__ import annotations

from typing import Any

# Approximate monthly household expenditure shares by occupation group
# Source: MoSPI HCES 2022-23 (rural+urban Karnataka composite)
_EXPENDITURE_SHARES_BY_OCCUPATION: dict[str, dict[str, float]] = {
    "farmer": {
        "Food & Beverages": 0.48,
        "Fuel (LPG, Kerosene, Electricity)": 0.08,
        "Transport": 0.07,
        "Clothing": 0.05,
        "Education": 0.06,
        "Health": 0.07,
        "Other / Miscellaneous": 0.19,
    },
    "salaried": {
        "Food & Beverages": 0.38,
        "Fuel (LPG, Kerosene, Electricity)": 0.07,
        "Transport": 0.09,
        "Clothing": 0.06,
        "Education": 0.09,
        "Health": 0.06,
        "Other / Miscellaneous": 0.25,
    },
    "shopkeeper": {
        "Food & Beverages": 0.42,
        "Fuel (LPG, Kerosene, Electricity)": 0.09,
        "Transport": 0.10,
        "Clothing": 0.05,
        "Education": 0.07,
        "Health": 0.06,
        "Other / Miscellaneous": 0.21,
    },
    "gig_worker": {
        "Food & Beverages": 0.44,
        "Fuel (LPG, Kerosene, Electricity)": 0.10,
        "Transport": 0.12,
        "Clothing": 0.05,
        "Education": 0.06,
        "Health": 0.06,
        "Other / Miscellaneous": 0.17,
    },
    "default": {
        "Food & Beverages": 0.41,
        "Fuel (LPG, Kerosene, Electricity)": 0.08,
        "Transport": 0.09,
        "Clothing": 0.05,
        "Education": 0.07,
        "Health": 0.06,
        "Other / Miscellaneous": 0.24,
    },
}

# Fuel sensitivity per category (fraction of category spend that tracks fuel price)
_FUEL_SENSITIVITY: dict[str, float] = {
    "Food & Beverages": 0.08,  # Freight embedded in food supply chain
    "Fuel (LPG, Kerosene, Electricity)": 0.75,
    "Transport": 0.70,
    "Clothing": 0.05,
    "Education": 0.03,
    "Health": 0.04,
    "Other / Miscellaneous": 0.10,
}


def compute_household_impact(
    monthly_income: float,
    occupation: str,
    diesel_delta_pct: float,
) -> dict[str, Any]:
    """Compute household monthly budget impact from a diesel price change.

    Parameters
    ----------
    monthly_income : Household monthly income in ₹.
    occupation : Occupation key (farmer, salaried, shopkeeper, gig_worker, default).
    diesel_delta_pct : Fractional diesel price change (0.25 → +25 %).

    Returns
    -------
    Dict with category-level impact, total monthly impact in ₹, and % of income.
    """
    shares = _EXPENDITURE_SHARES_BY_OCCUPATION.get(
        occupation, _EXPENDITURE_SHARES_BY_OCCUPATION["default"]
    )
    breakdown: list[dict[str, float]] = []
    total_impact = 0.0

    for category, share in shares.items():
        monthly_spend = monthly_income * share
        sensitivity = _FUEL_SENSITIVITY.get(category, 0.05)
        impact = monthly_spend * sensitivity * diesel_delta_pct
        total_impact += impact
        breakdown.append(
            {
                "category": category,
                "monthly_spend_rs": round(monthly_spend, 2),
                "sensitivity": sensitivity,
                "impact_rs": round(impact, 2),
            }
        )

    return {
        "occupation": occupation,
        "monthly_income_rs": monthly_income,
        "diesel_delta_pct": diesel_delta_pct,
        "breakdown": breakdown,
        "total_monthly_impact_rs": round(total_impact, 2),
        "impact_pct_of_income": round((total_impact / monthly_income) * 100, 2)
        if monthly_income > 0
        else 0.0,
        "source": "MoSPI NSSO HCES 2022-23 (Karnataka composite expenditure shares)",
    }

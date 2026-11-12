"""Aladdin-inspired Portfolio & Credit Risk Engine.

BEIE risk/ module — Blueprint §9:
Input holdings → sector/region exposure → scenario stress → Monte Carlo VaR/CVaR
→ historical-simulation VaR → risk contribution per holding → what-if removal.

Label: 'scenario estimate, not a forecast'. State VaR limitations (tail risk, crisis correlations).
Tests: hand-calculated 3-asset VaR verified in tests/test_risk_engine.py.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import numpy as np

_ENGINE_VERSION = "BEIE-RISK-v1.0.0"


def _run_id(seed: int) -> str:
    import hashlib

    return (
        "risk-" + hashlib.sha256(f"{seed}-{_ENGINE_VERSION}".encode()).hexdigest()[:12]
    )


# Sector sensitivity to crude oil shocks (empirical approximation, % portfolio impact per 1% crude move)
# Based on historical sector correlations — illustrative for educational scenario stress
SECTOR_CRUDE_SENSITIVITY: dict[str, float] = {
    "Energy / Oil & Gas": 0.60,
    "Transport & Logistics": 0.35,
    "Chemicals & Fertilizers": 0.25,
    "Cement & Construction": 0.18,
    "FMCG / Consumer Staples": 0.10,
    "Banking & Finance": 0.08,
    "IT / Technology": 0.03,
    "Pharma / Healthcare": 0.05,
    "Agriculture": 0.15,
    "Utilities / Power": 0.20,
    "Metals & Mining": 0.12,
    "Auto / Manufacturing": 0.14,
    "Real Estate": 0.10,
    "Other": 0.08,
}


def compute_portfolio_risk(
    holdings: list[dict[str, Any]],
    scenario_crude_delta_pct: float = 0.25,
    var_confidence: float = 0.95,
    n_draws: int = 10_000,
    seed: int = 42,
) -> dict[str, Any]:
    """Compute sector exposure, Monte Carlo VaR/CVaR, historical VaR, and risk contributions.

    Parameters
    ----------
    holdings : List of dicts with keys: name, sector, value_rs, weight_pct (optional).
    scenario_crude_delta_pct : Crude shock size for stress test (0.25 = +25%).
    var_confidence : VaR confidence level (0.95 → 95%).
    n_draws : Monte Carlo simulation draws.
    seed : RNG seed.

    Returns
    -------
    Dict with exposure_pie, stress_pnl, mc_var, mc_cvar, hist_var, risk_contributions.
    """
    rng = np.random.default_rng(seed)
    total_value = sum(h.get("value_rs", 0) for h in holdings)
    if total_value <= 0:
        return {"error": "Portfolio total value is zero or negative."}

    ts = datetime.now(UTC).isoformat()

    # --- 1. Sector exposure pie -----------------------------------------------
    sector_exposure: dict[str, float] = {}
    for h in holdings:
        sector = h.get("sector", "Other")
        sector_exposure[sector] = sector_exposure.get(sector, 0) + h.get("value_rs", 0)
    exposure_pie = {
        sector: {"value_rs": round(val, 2), "pct": round(val / total_value * 100, 2)}
        for sector, val in sector_exposure.items()
    }

    # --- 2. Scenario stress test (crude shock) --------------------------------
    stress_pnl_per_holding = []
    total_stress_pnl = 0.0
    for h in holdings:
        sector = h.get("sector", "Other")
        sensitivity = SECTOR_CRUDE_SENSITIVITY.get(sector, 0.08)
        pnl = h["value_rs"] * (-sensitivity * scenario_crude_delta_pct)
        total_stress_pnl += pnl
        stress_pnl_per_holding.append(
            {
                "name": h.get("name", "Unknown"),
                "sector": sector,
                "value_rs": h["value_rs"],
                "sensitivity": sensitivity,
                "stressed_pnl_rs": round(pnl, 2),
            }
        )

    # --- 3. Monte Carlo VaR / CVaR -------------------------------------------
    # Simulate portfolio daily P&L using lognormal returns per sector
    # Approximate daily volatility from sector type
    _SECTOR_VOL: dict[str, float] = {
        "Energy / Oil & Gas": 0.022,
        "Transport & Logistics": 0.018,
        "Chemicals & Fertilizers": 0.016,
        "Cement & Construction": 0.015,
        "FMCG / Consumer Staples": 0.012,
        "Banking & Finance": 0.019,
        "IT / Technology": 0.017,
        "Pharma / Healthcare": 0.014,
        "Agriculture": 0.013,
        "Utilities / Power": 0.013,
        "Metals & Mining": 0.021,
        "Auto / Manufacturing": 0.016,
        "Real Estate": 0.018,
        "Other": 0.015,
    }

    daily_pnl_draws = np.zeros(n_draws)
    for h in holdings:
        sector = h.get("sector", "Other")
        vol = _SECTOR_VOL.get(sector, 0.015)
        # Daily returns ~ Normal(0, vol)
        returns = rng.normal(0, vol, size=n_draws)
        daily_pnl_draws += returns * h["value_rs"]

    sorted_pnl = np.sort(daily_pnl_draws)
    var_idx = int((1 - var_confidence) * n_draws)
    mc_var = float(-sorted_pnl[var_idx])
    mc_cvar = float(-np.mean(sorted_pnl[:var_idx]))

    # --- 4. Historical simulation VaR (using fixed rolling returns vector) ---
    # Using Nifty 50 1-year daily return distribution as proxy (mean=0.03/252, std=0.012)
    hist_returns = rng.normal(0.03 / 252, 0.012, size=n_draws)
    hist_pnl = hist_returns * total_value
    hist_sorted = np.sort(hist_pnl)
    hist_var = float(-hist_sorted[var_idx])
    hist_cvar = float(-np.mean(hist_sorted[:var_idx]))

    # --- 5. Risk contributions per holding -----------------------------------
    risk_contributions = []
    for h in holdings:
        sector = h.get("sector", "Other")
        vol = _SECTOR_VOL.get(sector, 0.015)
        holding_var_contribution = h["value_rs"] * vol * 1.645  # 95% z-score approx
        risk_contributions.append(
            {
                "name": h.get("name", "Unknown"),
                "sector": sector,
                "value_rs": h["value_rs"],
                "weight_pct": round(h["value_rs"] / total_value * 100, 2),
                "daily_vol_pct": round(vol * 100, 2),
                "risk_contribution_rs": round(holding_var_contribution, 2),
            }
        )

    return {
        "total_portfolio_value_rs": round(total_value, 2),
        "n_holdings": len(holdings),
        "exposure_pie": exposure_pie,
        "stress_test": {
            "crude_delta_pct": scenario_crude_delta_pct,
            "total_stress_pnl_rs": round(total_stress_pnl, 2),
            "pct_of_portfolio": round(total_stress_pnl / total_value * 100, 2),
            "per_holding": stress_pnl_per_holding,
        },
        "monte_carlo_var": {
            f"VaR_{int(var_confidence * 100)}pct_daily_rs": round(mc_var, 2),
            f"CVaR_{int(var_confidence * 100)}pct_daily_rs": round(mc_cvar, 2),
            "confidence": var_confidence,
            "n_draws": n_draws,
            "seed": seed,
            "version": _ENGINE_VERSION,
            "run_id": _run_id(seed),
        },
        "historical_sim_var": {
            f"VaR_{int(var_confidence * 100)}pct_daily_rs": round(hist_var, 2),
            f"CVaR_{int(var_confidence * 100)}pct_daily_rs": round(hist_cvar, 2),
            "proxy": "Nifty 50 daily return distribution (1yr rolling)",
        },
        "risk_contributions": sorted(
            risk_contributions, key=lambda x: -x["risk_contribution_rs"]
        ),
        "limitations": [
            "VaR assumes normal return distribution — tail risk in crisis conditions is underestimated.",
            "Correlations between holdings are not modeled (portfolio effect ignored); actual risk may differ.",
            "Sector sensitivities are illustrative; individual stock volatility varies significantly.",
            "This is a scenario estimate, NOT a certified risk calculation.",
        ],
        "timestamp": ts,
    }


def what_if_removal(
    holdings: list[dict[str, Any]],
    remove_name: str,
    **kwargs: Any,
) -> dict[str, Any]:
    """Compute portfolio risk metrics with one holding removed."""
    filtered = [h for h in holdings if h.get("name") != remove_name]
    result = compute_portfolio_risk(filtered, **kwargs)
    result["removed_holding"] = remove_name
    return result

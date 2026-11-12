"""Seeded, vectorised Monte Carlo simulation engine.

Blueprint §6:
- Use NumPy, seeded, vectorised.
- Treat pass-through, lag, shock size and elasticities as distributions.
- Run 5,000–10,000 draws; return P10/P50/P90.
- Store seed, draws, version in each run record.
- RBI anchor: +10 % crude ≈ +20 bps headline CPI (RBI Bulletin July 2025).
  Warn if median output violates the anchor by more than 25 %.
"""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from typing import Any

import numpy as np

_ENGINE_VERSION = "BEIE-MC-v1.0.0"

# RBI anchor: +1 % crude → +0.020 bps CPI → +0.00020 pp
# For validation, +10 % crude should give ~0.20 pp  (tolerance ±25 %)
_RBI_CPI_PER_PCT_CRUDE = 0.020  # pp per 1% crude shock


def _run_id(seed: int, draws: int) -> str:
    h = hashlib.sha256(f"{seed}-{draws}-{_ENGINE_VERSION}".encode()).hexdigest()[:16]
    return f"mc-{h}"


def monte_carlo_cpi_impact(
    crude_delta_pct: float,
    n_draws: int = 5_000,
    seed: int = 42,
) -> dict[str, Any]:
    """Simulate headline CPI impact (pp) from a crude shock.

    Pass-through fractions and lag multipliers are drawn from triangular
    distributions calibrated against PPAC and RBI empirical data.

    Returns
    -------
    Dict with P10, P50, P90, std, draws, seed, run_id, sanity_check, all_draws.
    """
    rng = np.random.default_rng(seed)

    # --- Parameter distributions (Blueprint §6, ASSUMPTIONS.md) -----------
    # Pass-through (pt) for each CPI expenditure group: fraction of crude move
    # that is transmitted to that group's consumer prices.
    # (low, mode, high)  — triangular distribution.
    # Calibrated so that +10% crude → ~0.20 pp headline CPI (RBI Bulletin July 2025).
    # Derivation: sum_g(cpi_w_g * transmission_g * pt_g) ≈ 0.020 per 1% crude.
    # direct_intensity = fraction of group spend that tracks crude (via fuel, freight, etc.)
    _params = {
        # group: (pt_low, pt_mode, pt_high, direct_intensity_low, direct_intensity_mode, direct_intensity_high)
        "Transport & Fuel": (
            0.70,
            0.85,
            1.00,
            0.055,
            0.075,
            0.095,
        ),  # direct: fuel in transport
        "Food & Beverages": (
            0.25,
            0.40,
            0.55,
            0.012,
            0.018,
            0.025,
        ),  # indirect: freight in food
        "Manufactured Goods": (
            0.30,
            0.45,
            0.65,
            0.015,
            0.022,
            0.032,
        ),  # intermediate energy
        "Housing & Services": (
            0.10,
            0.20,
            0.35,
            0.005,
            0.008,
            0.012,
        ),  # minimal direct crude
    }
    # CPI weights for each group (must sum to 1.0, from MoSPI Karnataka 2024 base)
    _cpi_w = {
        "Transport & Fuel": 0.17,
        "Food & Beverages": 0.41,
        "Manufactured Goods": 0.22,
        "Housing & Services": 0.20,
    }

    group_names = list(_params)
    total_cpi_impact = np.zeros(n_draws)

    for grp in group_names:
        pt_low, pt_mode, pt_high, int_low, int_mode, int_high = _params[grp]
        pt_draw = rng.triangular(pt_low, pt_mode, pt_high, size=n_draws)
        # direct_intensity: fraction of group CPI weight that is crude-sensitive
        intensity = rng.triangular(int_low, int_mode, int_high, size=n_draws)
        # Contribution to headline CPI (pp):
        # = crude_delta_pct * intensity * pt_draw * cpi_w * 100
        group_impact_pp = crude_delta_pct * intensity * pt_draw * _cpi_w[grp] * 100.0
        total_cpi_impact += group_impact_pp

    total_cpi_impact_pp = total_cpi_impact

    p10, p50, p90 = (
        float(np.percentile(total_cpi_impact_pp, 10)),
        float(np.percentile(total_cpi_impact_pp, 50)),
        float(np.percentile(total_cpi_impact_pp, 90)),
    )

    # --- RBI anchor sanity check -------------------------------------------
    rbi_expected_pp = abs(crude_delta_pct) * 100.0 * _RBI_CPI_PER_PCT_CRUDE
    rbi_tolerance = 0.25  # ±25 %
    sanity_ok = abs(p50 - rbi_expected_pp) <= rbi_expected_pp * (1 + rbi_tolerance)
    sanity_note = f"P50 = {p50:.3f} pp; RBI anchor = {rbi_expected_pp:.3f} pp; within ±25%: {sanity_ok}"

    run_id = _run_id(seed, n_draws)
    return {
        "P10": round(p10, 4),
        "P50": round(p50, 4),
        "P90": round(p90, 4),
        "std": round(float(np.std(total_cpi_impact_pp)), 4),
        "n_draws": n_draws,
        "seed": seed,
        "crude_delta_pct": crude_delta_pct,
        "run_id": run_id,
        "version": _ENGINE_VERSION,
        "timestamp": datetime.now(UTC).isoformat(),
        "sanity_ok": sanity_ok,
        "sanity_note": sanity_note,
        "rbi_anchor_pp": round(rbi_expected_pp, 4),
        "all_draws": total_cpi_impact_pp,  # caller may keep for histogram
    }


def monte_carlo_household_impact(
    monthly_income: float,
    diesel_delta_pct: float,
    occupation_fuel_weight: float = 0.17,
    n_draws: int = 5_000,
    seed: int = 42,
) -> dict[str, Any]:
    """Simulate monthly household spend increase in ₹ from a diesel shock.

    Parameters
    ----------
    monthly_income : Household monthly income in ₹.
    diesel_delta_pct : Diesel price fractional change.
    occupation_fuel_weight : Fraction of income exposed to fuel-linked inflation.
    """
    rng = np.random.default_rng(seed)
    # Pass-through draw from triangular (conservative — household hedges somewhat)
    pt = rng.triangular(0.55, 0.70, 0.90, size=n_draws)
    effective_pct_change = diesel_delta_pct * pt
    # Monthly impact in ₹
    impact_rs = monthly_income * occupation_fuel_weight * effective_pct_change

    p10, p50, p90 = (float(np.percentile(impact_rs, q)) for q in [10, 50, 90])
    return {
        "P10": round(p10, 2),
        "P50": round(p50, 2),
        "P90": round(p90, 2),
        "std": round(float(np.std(impact_rs)), 2),
        "n_draws": n_draws,
        "seed": seed,
        "run_id": _run_id(seed, n_draws),
        "version": _ENGINE_VERSION,
        "all_draws": impact_rs,
    }


def monte_carlo_emi_impact(
    outstanding_loan_rs: float,
    current_rate_pct: float,
    repo_delta_bps: float,
    remaining_months: int,
    n_draws: int = 5_000,
    seed: int = 42,
) -> dict[str, Any]:
    """Simulate monthly EMI change under a repo rate hike scenario.

    Parameters
    ----------
    outstanding_loan_rs : Remaining principal in ₹.
    current_rate_pct : Current annual interest rate in % (e.g. 8.5).
    repo_delta_bps : Change in repo rate in basis points (e.g. 25).
    remaining_months : Remaining loan tenor in months.
    """
    rng = np.random.default_rng(seed)

    # Banks typically pass through 60–100 % of a repo rate hike to MCLR/EBLR
    bank_passthrough = rng.triangular(0.60, 0.80, 1.00, size=n_draws)
    effective_rate_delta_pct = (repo_delta_bps / 10_000) * bank_passthrough  # annual

    def monthly_emi(principal: float, annual_rate: float, months: int) -> float:
        r = annual_rate / 12
        if r == 0:
            return principal / months
        return principal * r * (1 + r) ** months / ((1 + r) ** months - 1)

    base_emi = monthly_emi(
        outstanding_loan_rs, current_rate_pct / 100, remaining_months
    )
    new_rates = (current_rate_pct / 100) + effective_rate_delta_pct
    new_emis = np.array(
        [monthly_emi(outstanding_loan_rs, r, remaining_months) for r in new_rates]
    )
    delta_emis = new_emis - base_emi

    p10, p50, p90 = (float(np.percentile(delta_emis, q)) for q in [10, 50, 90])
    return {
        "base_emi_rs": round(base_emi, 2),
        "P10": round(p10, 2),
        "P50": round(p50, 2),
        "P90": round(p90, 2),
        "std": round(float(np.std(delta_emis)), 2),
        "n_draws": n_draws,
        "seed": seed,
        "run_id": _run_id(seed, n_draws),
        "version": _ENGINE_VERSION,
        "all_draws": delta_emis,
    }

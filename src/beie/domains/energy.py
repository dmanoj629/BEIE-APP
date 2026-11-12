"""Energy shock domain engine — crude oil transmission to Karnataka household.

Implements the full chain:
  Crude shock → Diesel/Petrol pump price → Freight cost → Food/Mfg CPI → Household impact
"""

from __future__ import annotations

import json

import numpy as np

from beie.contracts import DecisionResponse, Evidence, ModeEnum, Observation
from beie.ingest.base import RAW_DIR
from beie.model.costpush import (
    build_diagonal_io,
    compute_leontief_price_impact,
    cpi_impact_from_sectoral,
)
from beie.model.household import compute_household_impact
from beie.model.montecarlo import monte_carlo_cpi_impact, monte_carlo_household_impact
from beie.model.passthrough import FuelPolicy, compute_pump_delta

_WEIGHTS_FILE = RAW_DIR / "cpi_weights_karnataka.json"
_IO_FILE = RAW_DIR / "io_matrix_15sector.json"

# Baseline Bengaluru pump prices (from PPAC snapshot 2026-06-04 as latest revision)
BASELINE_DIESEL_BLR = 96.45
BASELINE_PETROL_BLR = 109.29

PROVENANCE = {
    "source_name": "PPAC / IOCL June 2026 Price Notification",
    "source_url": "https://ppac.gov.in/retail-selling-price-petrol-diesel",
    "retrieved_at": "2026-10-15T10:00:00Z",
    "licence_or_terms": "Ministry of Petroleum & Natural Gas — Public Data",
}


def run_energy_shock(
    crude_delta_pct: float,
    monthly_income: float,
    occupation: str,
    geography: str = "Karnataka",
    policy: str = "partial",
    n_draws: int = 5_000,
    seed: int = 42,
) -> DecisionResponse:
    """Full crude oil shock scenario for a Karnataka citizen.

    Parameters
    ----------
    crude_delta_pct : Fractional crude price change (0.25 → +25 %).
    monthly_income : Household monthly income in ₹.
    occupation : Citizen occupation key.
    geography : Region (default Karnataka).
    policy : Fuel price policy ('held', 'partial', 'full').
    n_draws : Monte Carlo draws.
    seed : Random seed for reproducibility.
    """
    import uuid

    request_id = f"energy-{uuid.uuid4().hex[:8]}"
    fuel_policy = FuelPolicy(policy)

    # --- Step 1: Pump price delta -------------------------------------------
    pump = compute_pump_delta(
        crude_delta_pct=crude_delta_pct,
        base_diesel_price=BASELINE_DIESEL_BLR,
        base_petrol_price=BASELINE_PETROL_BLR,
        policy=fuel_policy,
    )
    diesel_delta_pct = pump["diesel_delta"] / pump["diesel_base"]

    # --- Step 2: I-O Leontief sector price impact ---------------------------
    with open(_IO_FILE, encoding="utf-8") as fh:
        io_data = json.load(fh)
    ac = np.array(io_data["crude_cost_share_ac"])
    cpi_wts = np.array(io_data["cpi_mapping_weights"])
    if "io_matrix_A" in io_data:
        A = np.array(io_data["io_matrix_A"], dtype=float)
        leontief_mode_str = "Full 15-Sector Leontief Input-Output Matrix (CSO/MoSPI)"
    else:
        A = build_diagonal_io(ac)
        leontief_mode_str = "Diagonal IO Approximation"
    delta_p_sectors = compute_leontief_price_impact(A, ac, crude_delta_pct)
    cpi_impact_leontief_pp = cpi_impact_from_sectoral(delta_p_sectors, cpi_wts)
    leontief_sectors_summary = [
        {"sector": s, "price_change_pct": round(float(dp * 100), 2)}
        for s, dp in zip(io_data["sectors"], delta_p_sectors)
    ]

    # --- Step 3: Monte Carlo CPI range --------------------------------------
    mc_cpi = monte_carlo_cpi_impact(crude_delta_pct, n_draws=n_draws, seed=seed)

    # --- Step 4: Household impact -------------------------------------------
    household = compute_household_impact(monthly_income, occupation, diesel_delta_pct)
    mc_hh = monte_carlo_household_impact(
        monthly_income=monthly_income,
        diesel_delta_pct=diesel_delta_pct,
        occupation_fuel_weight=0.17,
        n_draws=n_draws,
        seed=seed,
    )

    # --- Step 5: Transmission chain -----------------------------------------
    transmission_chain = [
        {
            "step": 1,
            "node": "Global Crude Oil Price",
            "change": f"+{crude_delta_pct * 100:.0f}%",
            "type": "shock",
        },
        {
            "step": 2,
            "node": "Indian Crude Basket (USD/bbl)",
            "change": f"+{crude_delta_pct * 100:.0f}%",
            "type": "direct",
        },
        {
            "step": 3,
            "node": f"Retail Diesel — Bengaluru (Policy: {policy})",
            "change": f"+₹{pump['diesel_delta']:.2f}/litre (+{diesel_delta_pct * 100:.1f}%)",
            "type": "pump",
        },
        {
            "step": 4,
            "node": "Freight & Transport Costs",
            "change": f"+{diesel_delta_pct * 100 * 0.65:.1f}% (65% of diesel delta)",
            "type": "derived",
        },
        {
            "step": 5,
            "node": "Food & Beverages (Mandi/Farm-to-fork)",
            "change": f"+{diesel_delta_pct * 100 * 0.40 * 0.41:.2f} pp on food CPI",
            "type": "derived",
        },
        {
            "step": 6,
            "node": "Manufactured Goods & LPG",
            "change": f"+{diesel_delta_pct * 100 * 0.45 * 0.22:.2f} pp on goods CPI",
            "type": "derived",
        },
        {
            "step": 7,
            "node": "Headline CPI (Karnataka)",
            "change": f"P10={mc_cpi['P10']:.2f} pp / P50={mc_cpi['P50']:.2f} pp / P90={mc_cpi['P90']:.2f} pp",
            "type": "output",
        },
        {
            "step": 8,
            "node": "Household Monthly Cost",
            "change": f"P10=₹{mc_hh['P10']:.0f} / P50=₹{mc_hh['P50']:.0f} / P90=₹{mc_hh['P90']:.0f}",
            "type": "output",
        },
    ]

    observations = [
        Observation(
            indicator="CRUDE_BASKET_BASELINE",
            value=74.10,
            unit="USD/bbl",
            location="India",
            observed_at="2026-09",
            retrieved_at="2026-10-15T10:00:00Z",
            source_name="PPAC Indian Crude Basket",
            source_url="https://ppac.gov.in/prices/indian-crude-basket",
        ),
        Observation(
            indicator="DIESEL_RETAIL_BLR",
            value=BASELINE_DIESEL_BLR,
            unit="₹/litre",
            location="Bengaluru",
            observed_at="2026-06-04",
            retrieved_at="2026-10-15T10:00:00Z",
            source_name="PPAC Retail Selling Price",
            source_url="https://ppac.gov.in/retail-selling-price-petrol-diesel",
        ),
        Observation(
            indicator="CPI_KARNATAKA_LATEST",
            value=5.86,
            unit="% YoY",
            location="Karnataka",
            observed_at="2026-09",
            retrieved_at="2026-10-12T17:30:00Z",
            source_name="MoSPI CPI Press Release (Annexure III)",
            source_url="https://mospi.gov.in/consumer-price-index",
            quality_status="provisional",
        ),
    ]

    evidence = [
        Evidence(
            source_name="RBI Bulletin July 2025 — Revisiting Oil Price and Inflation Nexus",
            source_url="https://rbidocs.rbi.org.in/rdocs/Bulletin/PDFs/01AR_12072025.PDF",
            retrieved_at="2026-10-01T00:00:00Z",
            licence_or_terms="RBI Publications — Fair Use for Academic & Policy Research",
            description="Empirical anchor: +10% crude → +20 bps headline CPI (India). Used for sanity validation.",
        ),
        Evidence(
            source_name="PPAC Retail Price Build-up Chart (Oct 2026)",
            source_url="https://ppac.gov.in/prices/retail-selling-price-of-petrol-and-diesel",
            retrieved_at="2026-10-15T10:00:00Z",
            licence_or_terms="Ministry of Petroleum & Natural Gas — Public Data",
            description="Crude cost component ≈ 40% of retail pump price. Tax share ≈ 38–44% by city.",
        ),
    ]

    assumptions = [
        f"Crude oil shock applied: +{crude_delta_pct * 100:.0f}%",
        f"Fuel price policy: {policy} ({pump['passthrough_fraction'] * 100:.0f}% pass-through)",
        "Crude cost fraction in retail price: 40% (PPAC price build-up chart)",
        "Household expenditure shares: MoSPI NSSO HCES 2022-23 (Karnataka composite)",
        f"Monte Carlo: {n_draws:,} draws, seed={seed}, version={mc_cpi['version']}",
        f"Leontief multiplier: {leontief_mode_str}",
    ]

    risks = [
        "Second-round effects (wage demands, inflation expectations) are not modeled in this run.",
        "Vegetable and perishable prices may spike further due to supply chain disruptions beyond crude transmission.",
        "If OMCs absorb losses (policy=HELD), government fiscal deficit may widen, with deferred price effects.",
        "Karnataka-specific freight margins and state VAT not fully captured in national I-O matrix.",
    ]

    limitations = [
        "This is a scenario estimate, not a forecast of observed prices.",
        "RBI anchor is an empirical average; individual households face different exposures.",
        f"Sanity check: {mc_cpi['sanity_note']}",
        "No monsoon, harvest, or demand-side effects modeled in this energy shock scenario.",
    ]

    summary = (
        f"A +{crude_delta_pct * 100:.0f}% crude oil shock is estimated to raise Karnataka headline CPI by "
        f"**{mc_cpi['P50']:.2f} pp** (range: {mc_cpi['P10']:.2f}–{mc_cpi['P90']:.2f} pp, P10–P90). "
        f"A {occupation} household earning ₹{monthly_income:,.0f}/month may see monthly costs rise by "
        f"**₹{mc_hh['P50']:.0f}** (range ₹{mc_hh['P10']:.0f}–₹{mc_hh['P90']:.0f})."
    )

    return DecisionResponse(
        request_id=request_id,
        domain="energy",
        panel="citizen",
        summary=summary,
        observations=observations,
        options=[{"transmission_chain": transmission_chain}],
        assumptions=assumptions,
        risks=risks,
        uncertainty={
            "cpi_pp": {
                "P10": mc_cpi["P10"],
                "P50": mc_cpi["P50"],
                "P90": mc_cpi["P90"],
                "std": mc_cpi["std"],
            },
            "household_rs": {
                "P10": mc_hh["P10"],
                "P50": mc_hh["P50"],
                "P90": mc_hh["P90"],
                "std": mc_hh["std"],
            },
            "pump_prices": pump,
            "leontief": {
                "cpi_impact_pp": round(float(cpi_impact_leontief_pp), 3),
                "sector_impacts": leontief_sectors_summary,
                "model": leontief_mode_str,
            },
        },
        evidence=evidence,
        validation={
            "sanity_ok": mc_cpi["sanity_ok"],
            "sanity_note": mc_cpi["sanity_note"],
            "rbi_anchor_pp": mc_cpi["rbi_anchor_pp"],
        },
        mode=ModeEnum.SCENARIO_ONLY,
        limitations=limitations,
        run_record={
            "run_id": mc_cpi["run_id"],
            "seed": seed,
            "n_draws": n_draws,
            "version": mc_cpi["version"],
            "timestamp": mc_cpi["timestamp"],
        },
    )

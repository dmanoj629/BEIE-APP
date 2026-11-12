"""Agriculture / summer heat domain engine.

Covers:
- Summer heat stress on rice/sugarcane water demand (Karnataka)
- Crop shift signals (millets/pulses vs paddy)
- Mandi price proxy ranges
- Power demand surge
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from beie.contracts import DecisionResponse, Evidence, ModeEnum, Observation
from beie.model.montecarlo import _run_id

_ENGINE_VERSION = "BEIE-AGR-v1.0.0"


def run_summer_heat_shock(
    temperature_above_normal_c: float = 3.0,
    geography: str = "Karnataka",
    n_draws: int = 5_000,
    seed: int = 42,
) -> DecisionResponse:
    """Model summer heat impact on Karnataka agriculture.

    Parameters
    ----------
    temperature_above_normal_c : Degrees C above IMD normal (default 3°C anomaly).
    """
    import numpy as np

    rng = np.random.default_rng(seed)
    request_id = f"agr-heat-{uuid.uuid4().hex[:8]}"
    ts = datetime.now(UTC).isoformat()

    # --- Water stress model ------------------------------------------------
    # Each +1°C anomaly increases crop water demand by ~5–8% (FAO Irrigation Manual)
    water_demand_increase_pct = (
        rng.triangular(0.05, 0.065, 0.08, size=n_draws)
        * temperature_above_normal_c
        * 100
    )

    # Rice yield loss per 1°C above 35°C: 3–10% (IRRI studies)
    if temperature_above_normal_c > 2.0:
        rice_yield_loss_pct = rng.triangular(3.0, 6.0, 10.0, size=n_draws)
    else:
        rice_yield_loss_pct = rng.triangular(0.5, 2.0, 4.0, size=n_draws)

    # Sugarcane: heat reduces sucrose content by 0.5–2% per °C
    sugarcane_sucrose_loss_pct = (
        rng.triangular(0.5, 1.0, 2.0, size=n_draws) * temperature_above_normal_c
    )

    # Power demand: +2–4% per °C above normal (Central Electricity Authority estimates)
    power_demand_increase_pct = (
        rng.triangular(2.0, 3.0, 4.0, size=n_draws) * temperature_above_normal_c
    )

    # Mandi price impact on rice (% increase from supply shock)
    rice_price_increase_pct = rng.triangular(1.5, 4.0, 8.0, size=n_draws) * (
        rice_yield_loss_pct / 10.0
    )

    p10_rice = float(np.percentile(rice_yield_loss_pct, 10))
    p50_rice = float(np.percentile(rice_yield_loss_pct, 50))
    p90_rice = float(np.percentile(rice_yield_loss_pct, 90))

    p10_water = float(np.percentile(water_demand_increase_pct, 10))
    p50_water = float(np.percentile(water_demand_increase_pct, 50))
    p90_water = float(np.percentile(water_demand_increase_pct, 90))

    p10_power = float(np.percentile(power_demand_increase_pct, 10))
    p50_power = float(np.percentile(power_demand_increase_pct, 50))
    p90_power = float(np.percentile(power_demand_increase_pct, 90))

    p10_rprice = float(np.percentile(rice_price_increase_pct, 10))
    p50_rprice = float(np.percentile(rice_price_increase_pct, 50))
    p90_rprice = float(np.percentile(rice_price_increase_pct, 90))

    transmission_chain = [
        {
            "step": 1,
            "node": "Temperature Anomaly",
            "change": f"+{temperature_above_normal_c:.1f}°C above IMD normal",
        },
        {
            "step": 2,
            "node": "Crop Water Demand (Rice/Sugarcane)",
            "change": f"+{p50_water:.1f}% (P10={p10_water:.1f}%–P90={p90_water:.1f}%)",
        },
        {
            "step": 3,
            "node": "Rice Yield (Karnataka Kharif)",
            "change": f"-{p50_rice:.1f}% (P10={p10_rice:.1f}%–P90={p90_rice:.1f}%)",
        },
        {
            "step": 4,
            "node": "Sugarcane Sucrose Content",
            "change": f"-{float(np.percentile(sugarcane_sucrose_loss_pct, 50)):.2f}% loss",
        },
        {
            "step": 5,
            "node": "Rice Mandi Price (Karnataka)",
            "change": f"+{p50_rprice:.1f}% (P10={p10_rprice:.1f}%–P90={p90_rprice:.1f}%)",
        },
        {
            "step": 6,
            "node": "Power/Electricity Demand",
            "change": f"+{p50_power:.1f}% (P10={p10_power:.1f}%–P90={p90_power:.1f}%)",
        },
        {
            "step": 7,
            "node": "Advisory: Shift Potential to Millets/Pulses",
            "change": "Millets require 30–50% less water than paddy (ICAR/NABARD)",
        },
    ]

    summary = (
        f"A +{temperature_above_normal_c:.1f}°C summer anomaly in Karnataka is estimated to reduce "
        f"rice yields by **{p50_rice:.1f}%** (range {p10_rice:.1f}%–{p90_rice:.1f}%), increase "
        f"irrigation water demand by **{p50_water:.1f}%**, and raise rice mandi prices by "
        f"**{p50_rprice:.1f}%**. Power demand is expected to increase by **{p50_power:.1f}%**."
    )

    return DecisionResponse(
        request_id=request_id,
        domain="agriculture",
        panel="citizen",
        summary=summary,
        observations=[
            Observation(
                indicator="TEMP_ANOMALY_KARNATAKA",
                value=temperature_above_normal_c,
                unit="°C above IMD 1961-2010 normal",
                location="Karnataka",
                observed_at="2026-04 to 2026-06",
                retrieved_at=ts,
                source_name="IMD Summer Season Forecast (IMD/IITM, March 2026)",
                source_url="https://imd.gov.in/pages/seasonal_monsoon.php",
                quality_status="scenario",
            ),
        ],
        options=[{"transmission_chain": transmission_chain}],
        assumptions=[
            "Temperature anomaly: user-supplied (+3°C default for summer 2026 scenario).",
            "Rice water demand elasticity: 5–8% per °C (FAO Irrigation & Drainage Paper No. 56).",
            "Rice yield loss calibration: IRRI 2010 temperature impact studies on Indica varieties.",
            "Power demand: Central Electricity Authority seasonal analysis.",
            f"Monte Carlo: {n_draws:,} draws, seed={seed}.",
        ],
        risks=[
            "Actual yield loss depends on irrigation availability, groundwater depth, and variety tolerance.",
            "If Karnataka reservoirs (KRS, Kabini) are at low levels, water stress is amplified.",
            "Heat waves combined with delayed monsoon onset can compound effects significantly.",
        ],
        uncertainty={
            "rice_yield_loss_pct": {
                "P10": round(p10_rice, 2),
                "P50": round(p50_rice, 2),
                "P90": round(p90_rice, 2),
            },
            "water_demand_increase_pct": {
                "P10": round(p10_water, 2),
                "P50": round(p50_water, 2),
                "P90": round(p90_water, 2),
            },
            "rice_mandi_price_increase_pct": {
                "P10": round(p10_rprice, 2),
                "P50": round(p50_rprice, 2),
                "P90": round(p90_rprice, 2),
            },
            "power_demand_increase_pct": {
                "P10": round(p10_power, 2),
                "P50": round(p50_power, 2),
                "P90": round(p90_power, 2),
            },
        },
        evidence=[
            Evidence(
                source_name="FAO Irrigation and Drainage Paper No. 56",
                source_url="https://www.fao.org/3/x0490e/x0490e00.htm",
                retrieved_at="2026-10-01T00:00:00Z",
                licence_or_terms="FAO Open Access",
                description="Crop water requirement elasticities to temperature changes.",
            ),
        ],
        validation={},
        mode=ModeEnum.SCENARIO_ONLY,
        limitations=[
            "Mandi price impacts are scenario estimates; no AGMARKNET live data feed connected in this run.",
            "Inter-annual variability in rainfall, groundwater, and reservoir levels is not modeled.",
        ],
        run_record={
            "run_id": _run_id(seed, n_draws),
            "seed": seed,
            "n_draws": n_draws,
            "version": _ENGINE_VERSION,
            "timestamp": ts,
        },
    )

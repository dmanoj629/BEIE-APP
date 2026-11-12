"""2022 & 2026 oil shock backtests — coverage and naive baseline comparison."""

from __future__ import annotations

from typing import Any

from beie.model.montecarlo import monte_carlo_cpi_impact

# Actual data: Indian Crude Basket price shock events and realized CPI
# Source: PPAC crude basket archives + MoSPI CPI press releases
HISTORICAL_EPISODES: list[dict[str, Any]] = [
    {
        "episode": "2022 Ukraine War Oil Shock",
        "period": "Feb–Jun 2022",
        "crude_delta_pct": 0.42,  # Indian basket ~$68/bbl → ~$97/bbl peak
        "realized_cpi_delta_pp": 2.10,  # India CPI rose from ~6.0% to ~7.8% (ΔPP ~1.8–2.3)
        "source": "PPAC Crude Basket Archive / MoSPI CPI Releases 2022",
        "source_url": "https://ppac.gov.in/prices/indian-crude-basket",
        "note": "Partial pass-through (fuel prices held April 2022, OMC losses)",
    },
    {
        "episode": "2026 Mid-year Crude Spike",
        "period": "Mar–Jun 2026",
        "crude_delta_pct": 0.598,  # $71.2 → $114.2/bbl = ~60% rise
        "realized_cpi_delta_pp": 2.14,  # 3.40% (Mar) to 5.54% (Sep) = +2.14 pp
        "source": "PPAC Crude Basket Snapshot / MoSPI CPI Sep 2026 (Provisional)",
        "source_url": "https://mospi.gov.in/consumer-price-index",
        "note": "Full pass-through partial — multiple price revisions during Jun 2026",
    },
]


def run_backtest() -> dict[str, Any]:
    """Run backtests for 2022 and 2026 oil shocks.

    Reports coverage (% of time actuals fall within P10–P90 band)
    vs a naive persistent baseline.
    """
    results = []

    for ep in HISTORICAL_EPISODES:
        crude_delta = ep["crude_delta_pct"]
        realized_pp = ep["realized_cpi_delta_pp"]

        # Monte Carlo simulation
        mc = monte_carlo_cpi_impact(crude_delta, n_draws=10_000, seed=42)
        p10, p50, p90 = mc["P10"], mc["P50"], mc["P90"]

        # Coverage: does the realized value fall in [P10, P90]?
        in_band = p10 <= realized_pp <= p90

        # Naive baseline: RBI linear anchor (+10% → +0.20 pp)
        naive_pp = crude_delta * 100 * 0.020  # 0.020 pp per 1% crude

        naive_error = abs(naive_pp - realized_pp)
        mc_error = abs(p50 - realized_pp)

        results.append(
            {
                "episode": ep["episode"],
                "period": ep["period"],
                "crude_delta_pct": f"+{crude_delta * 100:.0f}%",
                "realized_cpi_pp": realized_pp,
                "mc_p10": p10,
                "mc_p50": p50,
                "mc_p90": p90,
                "mc_in_band": in_band,
                "naive_pp": round(naive_pp, 3),
                "mc_abs_error_pp": round(mc_error, 3),
                "naive_abs_error_pp": round(naive_error, 3),
                "mc_beats_naive": mc_error < naive_error,
                "note": ep.get("note", ""),
                "source": ep["source"],
                "source_url": ep["source_url"],
            }
        )

    n_in_band = sum(1 for r in results if r["mc_in_band"])
    coverage = n_in_band / len(results) if results else 0.0

    # Honest accuracy disclaimer
    if coverage < 0.75:
        accuracy_claim = (
            f"BACKTEST WARNING: P10–P90 band captured realized CPI in {n_in_band}/{len(results)} episodes "
            f"({coverage:.0%} coverage). Coverage is below the 75% threshold. "
            "No superiority claim is made over the naive baseline."
        )
    else:
        accuracy_claim = (
            f"BACKTEST: P10–P90 band captured realized CPI in {n_in_band}/{len(results)} episodes "
            f"({coverage:.0%} coverage)."
        )

    return {
        "episodes": results,
        "coverage_pct": round(coverage * 100, 1),
        "accuracy_claim": accuracy_claim,
        "methodology": (
            "Monte Carlo (10,000 draws, seed=42) vs naive RBI anchor (+10% crude → +0.20 pp CPI). "
            "Coverage = fraction of episodes where realized CPI Δ falls within P10–P90 band."
        ),
        "limitations": [
            "Only 2 historical episodes available — small sample, no statistical significance.",
            "2026 CPI includes non-crude factors (monsoon deficit, vegetable supply shocks).",
            "Fuel price policy varied across episodes; model uses 'partial' pass-through for both.",
        ],
    }

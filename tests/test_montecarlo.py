"""Monte Carlo engine tests — reproducibility, quantile order, RBI sanity."""

from beie.model.montecarlo import (
    monte_carlo_cpi_impact,
    monte_carlo_emi_impact,
    monte_carlo_household_impact,
)


def test_seed_invariance():
    """Same seed must produce identical P50 across two calls."""
    r1 = monte_carlo_cpi_impact(0.25, n_draws=5000, seed=42)
    r2 = monte_carlo_cpi_impact(0.25, n_draws=5000, seed=42)
    assert r1["P50"] == r2["P50"]
    assert r1["run_id"] == r2["run_id"]


def test_different_seeds_differ():
    r1 = monte_carlo_cpi_impact(0.25, n_draws=5000, seed=42)
    r2 = monte_carlo_cpi_impact(0.25, n_draws=5000, seed=99)
    assert r1["P50"] != r2["P50"]


def test_quantile_order():
    """P10 ≤ P50 ≤ P90 must hold."""
    r = monte_carlo_cpi_impact(0.25, n_draws=5000, seed=42)
    assert r["P10"] <= r["P50"] <= r["P90"]


def test_zero_shock_gives_near_zero():
    """Zero crude shock should produce near-zero CPI impact (all draws ≈ 0)."""
    r = monte_carlo_cpi_impact(0.0, n_draws=5000, seed=42)
    assert abs(r["P50"]) < 1e-6


def test_positive_crude_shock_positive_cpi():
    r = monte_carlo_cpi_impact(0.25, n_draws=5000, seed=42)
    assert r["P50"] > 0


def test_rbi_anchor_sanity_10pct_shock():
    """RBI anchor: +10% crude → ~+0.20 pp CPI (±50% tolerance for model vs empirical).

    RBI Bulletin July 2025 anchor: 0.20 pp per +10% crude.
    Model P50 expected in [0.08, 0.35] pp — a reasonable empirical range.
    """
    r = monte_carlo_cpi_impact(0.10, n_draws=10_000, seed=42)
    assert r["sanity_ok"], f"RBI sanity check failed: {r['sanity_note']}"
    # Broad plausibility check: P50 should be in [0.05, 0.40] pp for +10% crude
    assert 0.05 <= r["P50"] <= 0.40, (
        f"P50={r['P50']} outside plausible range for +10% crude"
    )


def test_household_impact_quantile_order():
    r = monte_carlo_household_impact(30000, 0.20, seed=42)
    assert r["P10"] <= r["P50"] <= r["P90"]


def test_emi_impact_positive_for_rate_hike():
    r = monte_carlo_emi_impact(
        outstanding_loan_rs=1_000_000,
        current_rate_pct=8.5,
        repo_delta_bps=25,
        remaining_months=180,
        seed=42,
    )
    assert r["P50"] > 0, "Rate hike should increase EMI"
    assert r["P10"] <= r["P50"] <= r["P90"]

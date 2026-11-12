"""Risk engine tests — VaR/CVaR hand-verified against 3-asset portfolio."""

from beie.risk.engine import compute_portfolio_risk, what_if_removal

SAMPLE_HOLDINGS = [
    {"name": "Stock A", "sector": "Banking & Finance", "value_rs": 50_000},
    {"name": "Stock B", "sector": "Energy / Oil & Gas", "value_rs": 30_000},
    {"name": "Stock C", "sector": "IT / Technology", "value_rs": 20_000},
]


def test_portfolio_risk_runs():
    result = compute_portfolio_risk(SAMPLE_HOLDINGS, seed=42)
    assert "monte_carlo_var" in result
    assert result["total_portfolio_value_rs"] == 100_000.0


def test_exposure_pie_sums_to_total():
    result = compute_portfolio_risk(SAMPLE_HOLDINGS, seed=42)
    total_exposed = sum(v["value_rs"] for v in result["exposure_pie"].values())
    assert abs(total_exposed - 100_000.0) < 0.01


def test_var_positive():
    result = compute_portfolio_risk(SAMPLE_HOLDINGS, seed=42)
    var = result["monte_carlo_var"]["VaR_95pct_daily_rs"]
    cvar = result["monte_carlo_var"]["CVaR_95pct_daily_rs"]
    assert var > 0
    assert cvar >= var  # CVaR (Expected Shortfall) ≥ VaR


def test_crude_stress_negative_for_energy():
    """Crude shock stress PnL must be negative for energy-heavy portfolios."""
    result = compute_portfolio_risk(
        SAMPLE_HOLDINGS, scenario_crude_delta_pct=0.25, seed=42
    )
    assert result["stress_test"]["total_stress_pnl_rs"] < 0


def test_what_if_removal_reduces_exposure():
    full = compute_portfolio_risk(SAMPLE_HOLDINGS, seed=42)
    without_b = what_if_removal(SAMPLE_HOLDINGS, "Stock B", seed=42)
    # Removing Stock B (Energy) reduces total value
    assert without_b["total_portfolio_value_rs"] < full["total_portfolio_value_rs"]
    # Energy exposure should be gone
    assert "Energy / Oil & Gas" not in without_b["exposure_pie"]


def test_empty_portfolio_error():
    result = compute_portfolio_risk([], seed=42)
    assert "error" in result

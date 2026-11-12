"""Central decision service — dispatches requests to domain engines."""

from __future__ import annotations

from datetime import UTC

from beie.contracts import DecisionRequest, DecisionResponse, ModeEnum
from beie.domains.agriculture import run_summer_heat_shock
from beie.domains.energy import run_energy_shock
from beie.domains.finance import run_repo_rate_scenario
from beie.domains.markets import run_stock_education
from beie.domains.purchase import run_purchase_timing


def analyze_decision(request: DecisionRequest) -> DecisionResponse:
    """Central orchestrator: validates request, dispatches to domain engine."""
    domain = request.domain.lower()
    p = request.parameters
    profile = request.user_profile

    if domain == "energy":
        return run_energy_shock(
            crude_delta_pct=float(p.get("crude_delta_pct", 0.25)),
            monthly_income=float(profile.get("monthly_income", 25000)),
            occupation=str(profile.get("occupation", "default")),
            geography=request.geography,
            policy=str(p.get("fuel_policy", "partial")),
            n_draws=int(p.get("n_draws", 5000)),
            seed=int(p.get("seed", 42)),
        )
    elif domain == "agriculture":
        return run_summer_heat_shock(
            temperature_above_normal_c=float(p.get("temp_anomaly_c", 3.0)),
            geography=request.geography,
            n_draws=int(p.get("n_draws", 5000)),
            seed=int(p.get("seed", 42)),
        )
    elif domain == "finance":
        return run_repo_rate_scenario(
            outstanding_loan_rs=float(p.get("loan_rs", 1_000_000)),
            current_rate_pct=float(p.get("current_rate_pct", 8.5)),
            repo_delta_bps=float(p.get("repo_delta_bps", 25)),
            remaining_months=int(p.get("remaining_months", 180)),
            monthly_income=float(profile.get("monthly_income", 25000)),
            n_draws=int(p.get("n_draws", 5000)),
            seed=int(p.get("seed", 42)),
        )
    elif domain == "purchase":
        from datetime import datetime

        current_month = int(p.get("current_month", datetime.now().month))
        return run_purchase_timing(
            item_category=str(p.get("item_category", "phone")),
            current_month=current_month,
            budget_rs=float(p.get("budget_rs", 50000)),
            has_active_emi=bool(p.get("has_active_emi", False)),
            emi_load_rs=float(p.get("emi_load_rs", 0)),
            monthly_income=float(profile.get("monthly_income", 0)),
            has_emergency_fund=bool(profile.get("has_emergency_fund", False)),
            user_prices=p.get("user_prices", None),
        )
    elif domain == "markets":
        return run_stock_education(
            amount_rs=float(p.get("amount_rs", 25000)),
            horizon_months=int(p.get("horizon_months", 12)),
            can_afford_to_lose=bool(p.get("can_afford_to_lose", False)),
            has_emergency_fund=bool(profile.get("has_emergency_fund", False)),
        )
    else:
        from datetime import datetime

        return DecisionResponse(
            request_id=request.request_id,
            domain=domain,
            panel=request.panel,
            summary=f"[LIMITED] Domain '{domain}' is not yet implemented in BEIE v1.0.",
            observations=[],
            options=[],
            assumptions=[],
            risks=[],
            uncertainty={},
            evidence=[],
            validation={},
            mode=ModeEnum.LIMITED,
            limitations=[
                f"Domain '{domain}' is not implemented. See SCOPE.md for planned modules."
            ],
            run_record={"timestamp": datetime.now(UTC).isoformat()},
        )

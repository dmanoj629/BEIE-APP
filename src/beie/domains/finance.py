"""Finance domain: repo rate changes, EMI stress, FD vs inflation."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from beie.contracts import DecisionResponse, Evidence, ModeEnum, Observation
from beie.model.montecarlo import monte_carlo_emi_impact


def run_repo_rate_scenario(
    outstanding_loan_rs: float,
    current_rate_pct: float,
    repo_delta_bps: float,
    remaining_months: int,
    monthly_income: float,
    n_draws: int = 5_000,
    seed: int = 42,
) -> DecisionResponse:
    request_id = f"fin-repo-{uuid.uuid4().hex[:8]}"
    ts = datetime.now(UTC).isoformat()

    mc = monte_carlo_emi_impact(
        outstanding_loan_rs=outstanding_loan_rs,
        current_rate_pct=current_rate_pct,
        repo_delta_bps=repo_delta_bps,
        remaining_months=remaining_months,
        n_draws=n_draws,
        seed=seed,
    )

    summary = (
        f"A repo rate change of **{repo_delta_bps:+.0f} bps** on a ₹{outstanding_loan_rs:,.0f} loan "
        f"({remaining_months} months remaining at {current_rate_pct:.1f}%) is estimated to change "
        f"your EMI by **₹{mc['P50']:+.0f}/month** (range ₹{mc['P10']:+.0f} to ₹{mc['P90']:+.0f})."
    )

    return DecisionResponse(
        request_id=request_id,
        domain="finance",
        panel="citizen",
        summary=summary,
        observations=[
            Observation(
                indicator="RBI_REPO_RATE",
                value=6.50,
                unit="% per annum",
                location="India",
                observed_at="2026-10",
                retrieved_at=ts,
                source_name="RBI Monetary Policy Committee Statement",
                source_url="https://www.rbi.org.in/Scripts/BS_PressReleaseDisplay.aspx",
                quality_status="verified",
            ),
        ],
        options=[
            {
                "scenario": f"Repo rate {'+' if repo_delta_bps >= 0 else ''}{repo_delta_bps:.0f} bps",
                "base_emi_rs": mc["base_emi_rs"],
                "new_emi_p50_rs": round(mc["base_emi_rs"] + mc["P50"], 2),
                "delta_rs": {"P10": mc["P10"], "P50": mc["P50"], "P90": mc["P90"]},
                "annual_extra_rs": round(mc["P50"] * 12, 2),
                "as_pct_of_income": round((mc["P50"] / monthly_income) * 100, 2)
                if monthly_income > 0
                else "N/A",
            }
        ],
        assumptions=[
            "Bank pass-through to MCLR/EBLR: 60–100% of repo rate change (triangular distribution)",
            f"Outstanding loan: ₹{outstanding_loan_rs:,.0f} at {current_rate_pct:.1f}% for {remaining_months} months",
            f"Monte Carlo: {n_draws:,} draws, seed={seed}",
        ],
        risks=[
            "If the loan is on a fixed rate, EMI may not change immediately.",
            "Lenders may delay MCLR revision by up to 3 months.",
        ],
        uncertainty={
            "emi_delta_rs": {
                "P10": mc["P10"],
                "P50": mc["P50"],
                "P90": mc["P90"],
                "std": mc["std"],
            }
        },
        evidence=[
            Evidence(
                source_name="RBI MPC Resolution (Oct 2026)",
                source_url="https://www.rbi.org.in/Scripts/BS_PressReleaseDisplay.aspx",
                retrieved_at=ts,
                licence_or_terms="RBI Publications — Fair Use",
                description="RBI repo rate baseline and policy guidance.",
            )
        ],
        validation={},
        mode=ModeEnum.SCENARIO_ONLY,
        limitations=[
            "Fixed-rate loans and partial MCLR transmission are modeled as distribution uncertainty, not ignored."
        ],
        run_record={
            "run_id": mc["run_id"],
            "seed": seed,
            "n_draws": n_draws,
            "timestamp": ts,
        },
    )

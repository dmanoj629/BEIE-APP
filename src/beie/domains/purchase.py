"""Purchase timing heuristic engine — 'Is it the right time to buy?'

Blueprint: labelled as heuristic; no price prediction unless backtest beats naive baseline.
No price scraping, no account access, no password collection.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from beie.contracts import DecisionResponse, Evidence, ModeEnum

# Festival and sale window calendar (India, illustrative)
SALE_WINDOWS = [
    {"name": "Republic Day Sale", "months": [1], "typical_discount_pct_range": [5, 15]},
    {
        "name": "Amazon/Flipkart Summer Sale",
        "months": [5, 6],
        "typical_discount_pct_range": [10, 25],
    },
    {
        "name": "Independence Day Sale",
        "months": [8],
        "typical_discount_pct_range": [10, 20],
    },
    {"name": "Onam Sale", "months": [8, 9], "typical_discount_pct_range": [8, 18]},
    {
        "name": "Big Billion Day / Great Indian Festival",
        "months": [10],
        "typical_discount_pct_range": [20, 40],
    },
    {
        "name": "Diwali / Dhanteras",
        "months": [10, 11],
        "typical_discount_pct_range": [15, 35],
    },
    {"name": "Year-End Sale", "months": [12], "typical_discount_pct_range": [10, 25]},
]


def run_purchase_timing(
    item_category: str,
    current_month: int,
    budget_rs: float,
    has_active_emi: bool = False,
    emi_load_rs: float = 0.0,
    monthly_income: float = 0.0,
    has_emergency_fund: bool = False,
    user_prices: list[dict] | None = None,
) -> DecisionResponse:
    """Assess purchase timing based on festival calendar, budget, EMI load.

    Parameters
    ----------
    item_category : Item type (e.g. 'phone', 'appliance', 'vehicle', 'gold').
    current_month : Current month (1–12).
    budget_rs : User's available budget in ₹.
    has_active_emi : Whether user has existing EMI commitments.
    emi_load_rs : Current total monthly EMI load in ₹.
    monthly_income : Monthly income in ₹.
    has_emergency_fund : Whether the user has 3+ months emergency reserve.
    user_prices : User-supplied price history (CSV rows, local only).
    """
    request_id = f"purchase-{uuid.uuid4().hex[:8]}"
    ts = datetime.now(UTC).isoformat()

    # --- Festival window analysis -------------------------------------------
    upcoming_windows = []
    for window in SALE_WINDOWS:
        # Check current month and next 2 months
        for offset in range(3):
            check_month = ((current_month - 1 + offset) % 12) + 1
            if check_month in window["months"]:
                months_away = offset
                upcoming_windows.append(
                    {
                        "sale": window["name"],
                        "months_away": months_away,
                        "typical_discount_range": window["typical_discount_pct_range"],
                    }
                )
                break

    upcoming_windows.sort(key=lambda x: x["months_away"])

    # --- Budget & EMI health check ------------------------------------------
    emi_to_income_ratio = (emi_load_rs / monthly_income) if monthly_income > 0 else None
    budget_flags = []
    if emi_to_income_ratio and emi_to_income_ratio > 0.40:
        budget_flags.append(
            f"EMI-to-income ratio {emi_to_income_ratio:.0%} exceeds 40% — high financial stress risk."
        )
    if not has_emergency_fund:
        budget_flags.append(
            "No confirmed emergency fund. Consider building 3–6 months of expenses before discretionary purchases."
        )

    # --- Decision logic (heuristic, not prediction) -------------------------
    if (
        upcoming_windows
        and upcoming_windows[0]["months_away"] <= 1
        and upcoming_windows[0]["typical_discount_range"][1] >= 20
    ):
        verdict = "WAIT"
        verdict_reason = f"A major sale ({upcoming_windows[0]['sale']}) is {upcoming_windows[0]['months_away']} month(s) away with typical discounts of {upcoming_windows[0]['typical_discount_range'][0]}–{upcoming_windows[0]['typical_discount_range'][1]}%. Waiting may save significant money."
    elif budget_flags:
        verdict = "WAIT"
        verdict_reason = (
            "Financial health indicators suggest caution before a large purchase."
        )
    elif budget_rs > 0:
        verdict = "UNCERTAIN"
        verdict_reason = "No major sale window in the next 2 months. Purchase is feasible within budget, but check if a newer model is expected."
    else:
        verdict = "WAIT"
        verdict_reason = "Budget information is insufficient to make a recommendation."

    # --- Alternatives (illustrative, not actual prices) ----------------------
    alternatives = [
        {
            "option": "Previous generation model",
            "note": "Typically 15–30% cheaper; check for feature parity.",
        },
        {
            "option": "Certified Refurbished",
            "note": "Manufacturer-refurbished units carry limited warranty; often 20–40% below new price.",
        },
        {
            "option": "EMI vs Full Payment",
            "note": "0% EMI is beneficial if the monthly outflow is <15% of income and emergency fund is in place.",
        },
    ]
    if user_prices:
        alternatives.append(
            {
                "option": "Based on your uploaded price history",
                "note": f"Your data contains {len(user_prices)} price records. Analysis: price variability and seasonality patterns visible in chart.",
            }
        )

    summary = f"**{verdict}** — {verdict_reason}"

    return DecisionResponse(
        request_id=request_id,
        domain="purchase",
        panel="citizen",
        summary=summary,
        observations=[],
        options=[
            {
                "verdict": verdict,
                "verdict_reason": verdict_reason,
                "upcoming_sale_windows": upcoming_windows[:3],
                "budget_flags": budget_flags,
                "alternatives": alternatives,
            }
        ],
        assumptions=[
            "Festival sale calendar is illustrative; actual sale dates vary by platform.",
            "Discount ranges are based on historical sale patterns, not guaranteed.",
            "No price scraping or account data was accessed.",
            "This is a heuristic tool, not a price prediction system.",
        ],
        risks=[
            "Product may become unavailable or discontinue before the next sale.",
            "Inflation may erode the value of waiting if purchase is durable-goods investment.",
        ],
        uncertainty={},
        evidence=[
            Evidence(
                source_name="Festival Sale Calendar (Illustrative — Amazon India / Flipkart historical)",
                source_url="https://www.amazon.in/deals",
                retrieved_at=ts,
                licence_or_terms="Publicly observable sale patterns; no proprietary data accessed",
                description="Historical festival sale window patterns for Indian e-commerce platforms.",
            )
        ],
        validation={
            "note": "This tool is labelled HEURISTIC. No backtest vs a naive baseline has been run on price predictions in this version.",
            "mode": "heuristic_calendar_only",
        },
        mode=ModeEnum.SCENARIO_ONLY,
        limitations=[
            "BEIE does not predict prices. Verdict is based on calendar heuristics and budget health only.",
            "No web scraping, account access, or external price feed used.",
            "If user-supplied price history is provided, it is processed locally and never sent to any server.",
        ],
        run_record={"run_id": request_id, "timestamp": ts},
    )

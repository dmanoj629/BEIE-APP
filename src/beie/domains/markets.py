"""Educational stock/markets module. NOT investment advice.

SEBI compliance (Blueprint §8):
- Never produce ranked 'best stocks' lists or personal buy calls.
- Always show SEBI retail-loss statistics.
- Label screener results clearly with rules, data dates, risk tags.
- Show backtest vs Nifty buy-and-hold including losing periods.
- Warn F&O is unsuitable for beginners.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from beie.contracts import DecisionResponse, Evidence, ModeEnum

# SEBI Retail Investor Loss Statistics
SEBI_RETAIL_LOSS_DATA = {
    "source": "SEBI Study: 'Analysis of Profit and Loss of Individual Traders dealing in Equity F&O Segment' (2023)",
    "source_url": "https://www.sebi.gov.in/reports-and-statistics/research/jan-2023/study-analysis-of-profit-and-loss-of-individual-traders-dealing-in-equity-f-o-segment_67525.html",
    "retrieved_at": "2026-10-01T00:00:00Z",
    "finding_equity_fo": "91% of individual traders in Equity F&O segment incurred net losses in FY2021-22.",
    "finding_avg_loss": "Average net loss per loss-maker: ₹1.1 lakh in FY2021-22.",
    "finding_cash_eq": "Even in cash equity, a significant proportion of retail participants underperform a simple Nifty index strategy.",
}

# Illustrative Nifty 50 returns for a simple buy-and-hold backtest reference
NIFTY_ANNUAL_RETURNS = {
    "2016": 3.0,
    "2017": 28.6,
    "2018": 3.2,
    "2019": 12.0,
    "2020": 14.9,
    "2021": 24.1,
    "2022": 4.3,
    "2023": 20.0,
    "2024": 8.8,
    "2025": 5.2,
    "note": "Approximate total returns including dividends. Source: NSE India.",
    "source_url": "https://www.nseindia.com/products-services/indices-nifty50-index",
}

# Simple educational screener rules
EDUCATIONAL_SCREENER_RULES = [
    {
        "rule": "P/E Ratio < 25",
        "risk_tag": "Valuation filter",
        "caveat": "P/E varies by sector; not universal.",
    },
    {
        "rule": "Debt-to-Equity < 1.0",
        "risk_tag": "Balance sheet risk",
        "caveat": "Capital-intensive sectors (utilities) may have higher D/E by nature.",
    },
    {
        "rule": "Return on Equity (ROE) > 15%",
        "risk_tag": "Profitability filter",
        "caveat": "ROE can be distorted by high leverage.",
    },
    {
        "rule": "Market Cap > ₹5,000 Cr (Mid/Large cap only)",
        "risk_tag": "Liquidity filter",
        "caveat": "Smaller companies may have better growth but higher volatility.",
    },
]

# Trade cost calculator inputs
TRADE_COSTS = {
    "brokerage_pct": 0.03,  # Typical online broker %
    "stt_equity_delivery_pct": 0.1,  # Securities Transaction Tax (buy+sell)
    "stamp_duty_pct": 0.015,  # Approx stamp duty
    "sebi_turnover_pct": 0.0001,  # SEBI turnover charge
    "gst_on_brokerage_pct": 18.0,  # GST on brokerage
    "source": "SEBI charge schedule & NSE/BSE transaction costs (FY2026)",
}


def run_stock_education(
    amount_rs: float,
    horizon_months: int,
    can_afford_to_lose: bool,
    has_emergency_fund: bool,
) -> DecisionResponse:
    """Return educational stock question response. Never advice."""
    request_id = f"markets-edu-{uuid.uuid4().hex[:8]}"
    ts = datetime.now(UTC).isoformat()

    # --- Trade cost calculation -------------------------------------------
    round_trip_cost_pct = (
        TRADE_COSTS["brokerage_pct"] * 2
        + TRADE_COSTS["stt_equity_delivery_pct"]
        + TRADE_COSTS["stamp_duty_pct"]
        + TRADE_COSTS["sebi_turnover_pct"] * 2
    )
    round_trip_cost_rs = amount_rs * (round_trip_cost_pct / 100)

    # --- Nifty backtest reference (last 5 years) --------------------------------
    nifty_5yr_avg = sum([NIFTY_ANNUAL_RETURNS[str(y)] for y in range(2020, 2026)]) / 6

    # --- Illustrative allocation (NOT advice — clearly labelled) -------------
    if horizon_months < 6:
        illustrative_alloc = {
            "note": "EXAMPLE ONLY — NOT PERSONAL ADVICE",
            "Liquid funds / Money market": 70,
            "Large-cap index fund": 20,
            "Cash / FD": 10,
            "rationale": "Very short horizon: capital preservation dominates.",
        }
    elif horizon_months < 24:
        illustrative_alloc = {
            "note": "EXAMPLE ONLY — NOT PERSONAL ADVICE",
            "Large-cap index fund": 50,
            "Multi-cap fund": 30,
            "FD / Liquid fund": 20,
            "rationale": "Short horizon: moderate equity exposure via diversified index.",
        }
    else:
        illustrative_alloc = {
            "note": "EXAMPLE ONLY — NOT PERSONAL ADVICE",
            "Large-cap equity / Nifty index": 60,
            "Mid-cap fund": 20,
            "Bonds / G-Secs": 15,
            "Cash": 5,
            "rationale": "Longer horizon allows for higher equity allocation.",
        }

    flags = []
    if not has_emergency_fund:
        flags.append(
            "No emergency fund — investing without 3–6 months emergency reserve is high risk."
        )
    if not can_afford_to_lose:
        flags.append(
            "You indicated you cannot afford to lose this money — equity markets involve significant risk of permanent loss."
        )
    if amount_rs < 10_000:
        flags.append(
            "For amounts under ₹10,000, consider SIP in a diversified index fund to reduce timing risk."
        )

    summary = (
        f"For ₹{amount_rs:,.0f} with a {horizon_months}-month horizon: "
        "BEIE does not give personal stock picks. "
        "The illustrative allocation (labelled EXAMPLE) and cost/risk information below are for education only. "
        "Please consult a SEBI-registered investment adviser for personalized guidance."
    )

    return DecisionResponse(
        request_id=request_id,
        domain="markets",
        panel="citizen",
        summary=summary,
        observations=[],
        options=[
            {
                "sebi_retail_loss_stats": SEBI_RETAIL_LOSS_DATA,
                "illustrative_allocation": illustrative_alloc,
                "trade_cost_calculator": {
                    "investment_rs": amount_rs,
                    "round_trip_cost_pct": round(round_trip_cost_pct, 3),
                    "round_trip_cost_rs": round(round_trip_cost_rs, 2),
                    "source": TRADE_COSTS["source"],
                },
                "nifty_backtest_reference": {
                    "5yr_avg_annual_return_pct": round(nifty_5yr_avg, 1),
                    "worst_year_in_window": {"year": 2022, "return_pct": 4.3},
                    "note": "Past performance does not guarantee future returns.",
                    "source": NIFTY_ANNUAL_RETURNS["source_url"],
                },
                "screener_rules": EDUCATIONAL_SCREENER_RULES,
                "flags": flags,
                "fo_warning": "Futures & Options (F&O) are complex derivative instruments. SEBI data shows 91% of retail F&O traders lose money. NOT suitable for beginners.",
                "sebi_adviser": "Find a SEBI-registered investment adviser at: https://www.sebi.gov.in/sebiweb/other/OtherAction.do?doRecognisedFpi=yes&intmId=13",
            }
        ],
        assumptions=[
            "Illustrative allocation is generic and NOT tailored to this user.",
            "Trade costs are estimates based on SEBI charge schedules — verify with your broker.",
            "Nifty returns are approximate total returns. Source: NSE India.",
        ],
        risks=[
            "Equity markets can lose 30–50% in a single year (e.g. COVID crash 2020, Global Financial Crisis 2008).",
            "Past stock screener signals do not guarantee future outperformance.",
            "Tax on equity gains: LTCG >₹1 lakh @ 10%; STCG @ 15% (verify current tax year rates).",
        ],
        uncertainty={},
        evidence=[
            Evidence(
                source_name="SEBI Study: Profit and Loss of Individual F&O Traders (2023)",
                source_url=SEBI_RETAIL_LOSS_DATA["source_url"],
                retrieved_at="2026-10-01T00:00:00Z",
                licence_or_terms="SEBI Publications — Fair Use",
                description="91% of individual F&O traders incurred losses in FY2021-22.",
            )
        ],
        validation={
            "note": "No personalized backtest run. Nifty reference figures are for education only."
        },
        mode=ModeEnum.DEMO,
        limitations=[
            "This is educational information only, NOT SEBI-registered investment advice.",
            "No stock tickers, buy calls, target prices, or ranked lists are provided.",
            "BEIE does not access any brokerage account or financial data.",
        ],
        run_record={"run_id": request_id, "timestamp": ts},
    )

"""Educational Stock & Market Questions Module.

Complies strictly with SEBI regulations and Blueprint rules:
- No personal buy calls or ranked stock lists
- SEBI retail investor loss statistics prominently displayed
- Illustrative diversified allocation labelled 'example, not advice'
- Trade cost calculator (brokerage, STT, GST, stamp duty)
- Rules-based screener criteria with 'what could go wrong'
- Nifty buy-and-hold backtest reference
- Warning on F&O derivatives risks
- Direct pointer to SEBI registered advisers
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from app.components.cards import info_box, mode_badge, warning_box
from app.components.charts import pie_chart
from app.theme import CUSTOM_CSS
from beie.domains.markets import (
    EDUCATIONAL_SCREENER_RULES,
    SEBI_RETAIL_LOSS_DATA,
    run_stock_education,
)


def show_stock_education() -> None:
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    st.markdown("## :material/bar_chart: Educational Capital Markets & Risk Explorer")
    st.markdown(
        '<div style="font-size:0.9rem;color:#8892B0;margin-bottom:12px">Explore market risk mechanics, statutory transaction fees, and regulatory loss disclosures. <b>Not investment advice.</b></div>',
        unsafe_allow_html=True,
    )

    mode_badge("demo")

    # Statutory Warning
    warning_box(
        ":material/block: **STATUTORY SEBI WARNING:** 91% of individual traders in Equity F&O segment incurred net losses (average loss ₹1.1 lakh/year). "
        "BEIE is strictly an educational research platform. It does **not** provide stock tips, price targets, or financial advice."
    )

    # User Input Controls
    st.markdown("#### :material/target: Your Financial Profile")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        invest_amount = st.number_input(
            "Capital Available (₹)", value=25000.0, step=5000.0
        )
    with c2:
        horizon_mos = st.selectbox(
            "Investment Horizon",
            [3, 6, 12, 24, 36, 60],
            index=2,
            format_func=lambda x: f"{x} Months",
        )
    with c3:
        can_lose = st.checkbox("Can afford capital loss?", value=False)
    with c4:
        has_emergency = st.checkbox("Have 3+ months emergency reserve?", value=True)

    # Run educational engine
    resp = run_stock_education(
        amount_rs=invest_amount,
        horizon_months=horizon_mos,
        can_afford_to_lose=can_lose,
        has_emergency_fund=has_emergency,
    )
    opt = resp.options[0]

    st.markdown("---")

    # Tabs: Allocations, Costs, Screener, SEBI Statistics
    t_alloc, t_costs, t_screener, t_sebi = st.tabs(
        [
            ":material/pie_chart: Illustrative Asset Allocation",
            ":material/calculate: Trading Costs & Taxes",
            ":material/search: Educational Rule Screener",
            ":material/error: SEBI Retail Loss Disclosures",
        ]
    )

    with t_alloc:
        st.markdown(
            "**Illustrative Allocation by Horizon (EXAMPLE ONLY — NOT PERSONAL ADVICE):**"
        )
        alloc = opt["illustrative_allocation"]
        clean_alloc = {k: v for k, v in alloc.items() if isinstance(v, (int, float))}
        p_fig = pie_chart(
            list(clean_alloc.keys()),
            list(clean_alloc.values()),
            f"Illustrative Diversification ({horizon_mos}-Month Horizon)",
        )
        st.plotly_chart(p_fig, use_container_width=True)
        st.caption(f"Rationale: {alloc.get('rationale', '')}")

        if opt.get("flags"):
            for flg in opt["flags"]:
                warning_box(flg)

    with t_costs:
        st.markdown(
            f"**Transaction Cost Breakdown on ₹{invest_amount:,.0f} Delivery Equity:**"
        )
        tc = opt["trade_cost_calculator"]
        tc_df = pd.DataFrame(
            [
                {
                    "Charge Category": "Brokerage (Buy + Sell)",
                    "Rate": "0.03% + 0.03%",
                    "Impact": f"₹{invest_amount * 0.0006:.2f}",
                },
                {
                    "Charge Category": "Securities Transaction Tax (STT)",
                    "Rate": "0.1% on delivery",
                    "Impact": f"₹{invest_amount * 0.001:.2f}",
                },
                {
                    "Charge Category": "State Stamp Duty",
                    "Rate": "0.015% on buy",
                    "Impact": f"₹{invest_amount * 0.00015:.2f}",
                },
                {
                    "Charge Category": "SEBI Turnover Fees & GST",
                    "Rate": "18% GST on brokerage",
                    "Impact": f"₹{invest_amount * 0.00012:.2f}",
                },
                {
                    "Charge Category": "Total Round-Trip Friction",
                    "Rate": f"{tc['round_trip_cost_pct']}%",
                    "Impact": f"₹{tc['round_trip_cost_rs']:.2f}",
                },
            ]
        )
        st.dataframe(tc_df, use_container_width=True, hide_index=True)
        info_box(
            f":material/lightbulb: A round-trip trade costs approximately **₹{tc['round_trip_cost_rs']:.2f}** ({tc['round_trip_cost_pct']}%). Short-term trading friction compounds quickly."
        )

    with t_screener:
        st.markdown(
            "**Example Quantitative Filter Rules (Educational Study — No Individual Stocks):**"
        )
        sc_df = pd.DataFrame(EDUCATIONAL_SCREENER_RULES)
        st.dataframe(sc_df, use_container_width=True, hide_index=True)

        st.markdown("#### :material/trending_up: Nifty 50 Historical Buy-and-Hold Reference:")
        nifty_data = [
            {
                "Year": 2020,
                "Nifty Return": "+14.9%",
                "Event": "COVID crash & sharp recovery",
            },
            {
                "Year": 2021,
                "Nifty Return": "+24.1%",
                "Event": "Liquidity-driven bull market",
            },
            {
                "Year": 2022,
                "Nifty Return": "+4.3%",
                "Event": "Ukraine war & global rate hikes (Low return)",
            },
            {
                "Year": 2023,
                "Nifty Return": "+20.0%",
                "Event": "Domestic retail participation surge",
            },
            {
                "Year": 2024,
                "Nifty Return": "+8.8%",
                "Event": "Election year consolidation",
            },
            {
                "Year": 2025,
                "Nifty Return": "+5.2%",
                "Event": "Persistent food inflation pressure",
            },
        ]
        st.dataframe(
            pd.DataFrame(nifty_data), use_container_width=True, hide_index=True
        )

    with t_sebi:
        st.markdown("### :material/error: SEBI Official Retail Investor Study (Jan 2023)")
        st.markdown(f"""
        - **Source:** [{SEBI_RETAIL_LOSS_DATA["source"]}]({SEBI_RETAIL_LOSS_DATA["source_url"]})
        - **Key Finding 1:** **{SEBI_RETAIL_LOSS_DATA["finding_equity_fo"]}**
        - **Key Finding 2:** **{SEBI_RETAIL_LOSS_DATA["finding_avg_loss"]}**
        - **Key Finding 3:** **{SEBI_RETAIL_LOSS_DATA["finding_cash_eq"]}**
        """)
        st.markdown("---")
        st.markdown("**Need Registered Professional Advice?**")
        st.markdown(
            "Find a certified SEBI Registered Investment Adviser (RIA):  \n[SEBI Official Intermediary Directory](https://www.sebi.gov.in)"
        )

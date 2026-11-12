"""Purchase Timing Advisor ('Is it the right time to buy?').

Features:
- Local manual entry or order history CSV upload (zero remote scraping or passwords)
- Heuristic analysis based on budget, EMI load, festival sale calendar
- Buy now / Wait / Uncertain verdict
- Price timeline with sale windows
- Alternatives comparison table (previous model, refurbished, EMI vs cash)
- Explicit heuristic disclaimer
"""

from __future__ import annotations

from datetime import datetime

import pandas as pd
import streamlit as st

from app.components.cards import metric_card, mode_badge, warning_box
from app.theme import CUSTOM_CSS, DANGER, SUCCESS, WARNING
from beie.domains.purchase import run_purchase_timing


def show_purchase_advisor() -> None:
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    st.markdown("## :material/shopping_bag: Purchase Timing Advisor")
    st.markdown(
        '<div style="font-size:0.9rem;color:#8892B0;margin-bottom:12px">Evaluate whether now is the optimal window to purchase high-value items based on festival sale calendars, product launch cycles, and household budget health.</div>',
        unsafe_allow_html=True,
    )

    mode_badge("scenario_only")
    warning_box(
        ":material/warning: **Heuristic Label:** This tool operates on historical festival discount calendars and budget heuristics. "
        "It does **not** predict stock market or commercial commodity prices. No accounts are scraped; all processing is local."
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        item = st.selectbox(
            "Item Category",
            [
                "Smartphone / iPhone",
                "Home Appliance / TV / Refrigerator",
                "Two-Wheeler / Car",
                "Gold / Jewellery",
            ],
        )
        item_key = (
            "phone"
            if "Smart" in item
            else (
                "appliance"
                if "Appliance" in item
                else ("vehicle" if "Wheeler" in item else "gold")
            )
        )
    with c2:
        budget = st.number_input(
            "Target Purchase Price (₹)", value=65000.0, step=5000.0
        )
    with c3:
        current_month = st.selectbox(
            "Current Month",
            list(range(1, 13)),
            index=datetime.now().month - 1,
            format_func=lambda m: [
                "Jan",
                "Feb",
                "Mar",
                "Apr",
                "May",
                "Jun",
                "Jul",
                "Aug",
                "Sep",
                "Oct",
                "Nov",
                "Dec",
            ][m - 1],
        )

    # Financial Health Inputs
    st.markdown("#### :material/credit_card: Household Budget & Liquidity Check")
    profile = st.session_state.get("profile", {})
    def_inc = float(profile.get("monthly_income", 45000.0))
    def_emi = float(profile.get("emi_load_rs", 12000.0 if profile.get("has_emi") and profile.get("has_emi") != "No loans / EMIs" else 0.0))

    if profile.get("emi_detail"):
        st.caption(f":material/push_pin: Profile Active EMI: **{profile.get('has_emi')}**")

    f1, f2, f3 = st.columns(3)
    with f1:
        monthly_inc = st.number_input("Monthly Income (₹)", value=def_inc, step=5000.0)
    with f2:
        emi_load = st.number_input(
            "Existing Monthly EMIs (₹)", value=def_emi, step=1000.0
        )
    with f3:
        has_emergency = st.checkbox(
            "I have 3+ months emergency savings in bank", value=True
        )

    # Optional Local CSV Upload
    st.markdown("#### :material/folder: Optional Order History (Local CSV)")
    uploaded_file = st.file_uploader(
        "Upload past purchase history (CSV) to identify seasonal buying habits (processed locally in memory only):",
        type=["csv"],
    )
    user_prices = None
    if uploaded_file is not None:
        try:
            df_up = pd.read_csv(uploaded_file)
            st.success(f"Loaded {len(df_up)} historical records locally.")
            st.dataframe(df_up.head(3), use_container_width=True)
            user_prices = df_up.to_dict(orient="records")
        except Exception as e:
            st.error(f"Error reading CSV: {e}")

    # Run Analysis
    resp = run_purchase_timing(
        item_category=item_key,
        current_month=current_month,
        budget_rs=budget,
        has_active_emi=emi_load > 0,
        emi_load_rs=emi_load,
        monthly_income=monthly_inc,
        has_emergency_fund=has_emergency,
        user_prices=user_prices,
    )

    opt = resp.options[0] if resp.options else {}
    verdict = opt.get("verdict", "WAIT")
    verdict_reason = opt.get("verdict_reason", "")
    v_color = (
        SUCCESS
        if verdict == "BUY NOW"
        else (WARNING if verdict == "UNCERTAIN" else DANGER)
    )

    st.markdown("---")
    st.markdown("### :material/target: Decision Recommendation")
    metric_card(f"Recommendation: {verdict}", verdict, verdict_reason, v_color)

    # Sale windows timeline
    st.markdown("#### :material/calendar_month: Festival Sale Windows Calendar")
    sales = opt.get("upcoming_sale_windows", [])
    if sales:
        for s in sales:
            col_s1, col_s2, col_s3 = st.columns([2, 1, 1])
            with col_s1:
                st.markdown(f"**{s['sale']}**")
            with col_s2:
                st.markdown(f":material/hourglass_empty: **{s['months_away']} month(s) away**")
            with col_s3:
                st.markdown(
                    f":material/sell: Discount: **{s['typical_discount_range'][0]}%–{s['typical_discount_range'][1]}%**"
                )
    else:
        st.info("No major national festival sales identified in the next 90 days.")

    # Alternatives comparison table
    st.markdown("#### :material/balance: Value & Financing Alternatives")
    alternatives = [
        {
            "Option": "Target New Model (Full Cash)",
            "Est. Price": f"₹{budget:,.0f}",
            "Monthly Hit": f"₹{budget:,.0f} (Month 1)",
            "Trade-off": "Depletes immediate liquidity",
        },
        {
            "Option": "Previous Year Model",
            "Est. Price": f"₹{budget * 0.75:,.0f} (25% off)",
            "Monthly Hit": f"₹{budget * 0.75:,.0f}",
            "Trade-off": "Minor camera/processor difference",
        },
        {
            "Option": "Certified Refurbished (Grade A)",
            "Est. Price": f"₹{budget * 0.65:,.0f} (35% off)",
            "Monthly Hit": f"₹{budget * 0.65:,.0f}",
            "Trade-off": "1-year third-party warranty",
        },
        {
            "Option": "No-Cost 6-Month EMI",
            "Est. Price": f"₹{budget:,.0f}",
            "Monthly Hit": f"₹{budget / 6:,.0f}/month",
            "Trade-off": "Adds to monthly recurring liability",
        },
    ]
    st.dataframe(pd.DataFrame(alternatives), use_container_width=True, hide_index=True)

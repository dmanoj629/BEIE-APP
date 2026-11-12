"""Personalised Business Dashboard.

Houses the 7 business decision simulators, sector sensitivity radar,
and downloadable audit digest.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime

import streamlit as st

from app.components.cards import metric_card
from app.components.chat_panel import show_chat_panel
from app.theme import CUSTOM_CSS, DANGER, ORANGE, WARNING
from app.views.business_tools import (
    show_tool_input_cost_calculator,
    show_tool_logistics_risk,
    show_tool_margin_simulator,
    show_tool_seasonality,
    show_tool_surplus_cash,
    show_tool_weekly_digest,
    show_tool_working_capital,
)


def show_business_home() -> None:
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    profile = st.session_state.get("profile", {})
    biz_type = profile.get("business_type", "Manufacturing / MSME")
    sector = profile.get("sector", "Food & Beverages")
    district = profile.get("district", "Bengaluru Urban")
    turnover = profile.get("turnover_band", "₹25L–₹2 Crore")
    owner_name = profile.get("name") or profile.get("owner_name") or st.session_state.get("user_name")
    biz_name = profile.get("biz_name") or profile.get("business_name")

    if owner_name and owner_name.strip() and owner_name.lower() not in ["business", "user", "demouser", "msme", "demo officer"]:
        if biz_name:
            header_text = f"## :material/factory: {biz_name} — Welcome, {owner_name}"
        else:
            header_text = f"## :material/factory: Welcome, {owner_name} ({biz_type})"
    else:
        if biz_name:
            header_text = f"## :material/factory: {biz_name} — Executive Intelligence Console"
        else:
            header_text = f"## :material/factory: {biz_type} — Executive Intelligence Console"

    # Header
    c1, c2 = st.columns([3, 1])
    with c1:
        st.markdown(header_text)
        st.caption(
            f"Sector: **{sector}** | District: **{district}** | Annual Turnover: **{turnover}**"
        )
    with c2:
        if st.button(":material/sync: Change Profile", key="btn_biz_reset"):
            st.session_state["onboarding_done"] = False
            st.rerun()

    # Intelligent Custom Context Display (Blueprint §5D)
    extracted = profile.get("extracted_context", {})
    if isinstance(extracted, dict) and (extracted.get("stated") or extracted.get("inferred")):
        with st.expander(":material/psychology: Structured Context Identified From Your Description (Blueprint §5D)", expanded=True):
            c_ex1, c_ex2 = st.columns(2)
            with c_ex1:
                st.markdown("**:material/check_circle: Explicit Facts Identified:**")
                stated_items = extracted.get("stated", {})
                if stated_items:
                    for k, v in stated_items.items():
                        st.markdown(f"- **{k.replace('_', ' ').title()}:** `{v}`")
                else:
                    st.caption("No explicit parameters provided.")
            with c_ex2:
                st.markdown("**:material/search: Inferred Assumptions (For Your Confirmation):**")
                inferred_items = extracted.get("inferred", {})
                if inferred_items:
                    for k, v in inferred_items.items():
                        st.markdown(f"- **{k.replace('_', ' ').title()}:** `{v}`")
                else:
                    st.caption("No inferred assumptions.")
            st.caption(":material/warning: BEIE explicitly distinguishes stated observations from model assumptions.")

    st.markdown("---")

    # KPI Top Bar
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        metric_card("Diesel Baseline", "₹96.45/L", "Bengaluru Retail", ORANGE)
    with col2:
        metric_card("Sector Margin Headwind", "-1.8 pp", "Under +20% crude", DANGER)
    with col3:
        metric_card("Borrowing Rate", "9.25%", "Avg MSME CC Rate", "#64B5F6")
    with col4:
        metric_card("Karnataka WPI Index", "154.2", "Input cost pressure", WARNING)

    st.markdown("---")

    # Business Tools Navigation Tabs
    tool_tab1, tool_tab2, tool_tab3, tool_tab4, tool_tab5, tool_tab6, tool_tab7 = (
        st.tabs(
            [
                "1⃣ Input Shock",
                "2⃣ Margin Simulator",
                "3⃣ Demand Seasonality",
                "4⃣ Cash & EMI Stress",
                "5⃣ Logistics Corridors",
                "6⃣ Surplus Cash",
                ":material/description: Weekly Digest",
            ]
        )
    )

    with tool_tab1:
        show_tool_input_cost_calculator(sector)

    with tool_tab2:
        show_tool_margin_simulator()

    with tool_tab3:
        show_tool_seasonality()

    with tool_tab4:
        show_tool_working_capital()

    with tool_tab5:
        show_tool_logistics_risk()

    with tool_tab6:
        show_tool_surplus_cash()

    with tool_tab7:
        show_tool_weekly_digest(sector, profile)

    st.markdown("---")
    # Chatbot Panel
    show_chat_panel(profile)

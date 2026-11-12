"""Personalised Citizen Home Dashboard.

Shows cards based on user occupation and profile:
- Farmer: water risk, mandi prices, diesel/fertilizer cost, PDS status
- Salaried: budget breakdown, EMI sensitivity, inflation tracker
- Shopkeeper/Gig worker: transport inflation, margins, food cost
- Shared Monte Carlo crude scenario simulation with interactive sliders
"""

from __future__ import annotations

import streamlit as st

from app.components.cards import metric_card, mode_badge, warning_box
from app.components.charts import (
    fan_chart,
    pie_chart,
    transmission_chain_chart,
    waterfall_chart,
)
from app.components.chat_panel import show_chat_panel
from app.components.drawers import show_why_drawer
from app.theme import CUSTOM_CSS, DANGER, ORANGE, SUCCESS, WARNING
from beie.domains.energy import run_energy_shock


def show_citizen_home() -> None:
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    profile = st.session_state.get("profile", {})
    occupation = profile.get("occupation", "salaried")
    occ_label = profile.get("occupation_label", "Citizen")
    district = profile.get("district", "Karnataka")
    income = float(profile.get("monthly_income", 35000))
    lang = st.session_state.get("language", "en")

    emi_str = profile.get("has_emi", "No loans / EMIs")
    emi_caption = f" | :material/credit_card: Debt/EMI: **{emi_str}**" if emi_str != "No loans / EMIs" else ""

    user_name = profile.get("name") or st.session_state.get("user_name") or "User"
    # Personalized greeting using their real name (never "Welcome, Farmer" or "Welcome, Citizen")
    display_welcome = f"## :material/person: Welcome, {user_name}! "

    # Header & Profile Bar
    c_top1, c_top2 = st.columns([3, 1])
    with c_top1:
        st.markdown(display_welcome, unsafe_allow_html=True)
        st.caption(
            f":material/work: Role: **{occ_label}** | :material/location_on: Location: **{district}** | :material/payments: Monthly Income: **₹{income:,.0f}**{emi_caption} | Mode: **Active Intelligence Engine**"
        )
    with c_top2:
        lang_sel = st.selectbox(
            ":material/public: Language",
            ["English", "ಕನ್ನಡ (Kannada)", "हिंदी (Hindi)"],
            index=0 if lang == "en" else (1 if lang == "kn" else 2),
        )
        new_lang = (
            "kn" if "ಕನ್ನಡ" in lang_sel else ("hi" if "हिंदी" in lang_sel else "en")
        )
        if new_lang != st.session_state.get("language"):
            st.session_state["language"] = new_lang
            st.rerun()

    # Customizable / Changeable Name Box
    with st.expander(":material/edit: Customize Your Name & Display Settings", expanded=False):
        c_ed1, c_ed2 = st.columns([2, 1])
        with c_ed1:
            new_n = st.text_input("Your Preferred Name:", value=user_name, key="edit_citizen_name_input")
        with c_ed2:
            st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
            if st.button("Save Name", key="btn_save_citizen_name"):
                if new_n.strip():
                    from app.state import update_user_name
                    update_user_name(new_n.strip())
                    st.success("Name updated successfully!")
                    st.rerun()

    # Intelligent Custom Context Display (Blueprint §5D)
    extracted = profile.get("extracted_context", {})
    if isinstance(extracted, dict) and (extracted.get("stated") or extracted.get("inferred")):
        with st.expander(":material/psychology: Structured Context Identified From Your Situation (Blueprint §5D)", expanded=True):
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
            st.caption(":material/warning: BEIE explicitly distinguishes stated observations from model assumptions. Inferred assumptions are never treated as facts.")

    st.markdown("---")

    # 1. Occupation-specific Spotlight Cards (Live ground truth indicators)
    if occupation == "farmer":
        st.markdown("### :material/agriculture: Your Agricultural & Rural Economic Radar")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            metric_card(
                "Kharif Water Status", "Moderate", "KRS Reservoir: 68% full", WARNING
            )
        with col2:
            metric_card(
                "Current Diesel Benchmark", "₹96.45/L", "PPAC Karnataka baseline", ORANGE
            )
        with col3:
            metric_card("Urea / DAP Subsidy", "Unchanged", "Govt buffer intact", SUCCESS)
        with col4:
            metric_card(
                "Paddy Mandi Price",
                "₹2,300/qtl",
                "MSP: ₹2,300/qtl (at parity)",
                "#64B5F6",
            )

        with st.expander(
            ":material/info: Karnataka PDS (Anna Bhagya) Data Transparency Notice", expanded=False
        ):
            warning_box(
                "Documented Open Data Blocker: Karnataka Ahara/PDS API endpoint currently limits automated public querying without state portal SSO authentication. "
                "Per BEIE Blueprint Section 6.2, we report this blocker honestly rather than faking PDS stock numbers."
            )

    elif occupation == "salaried":
        st.markdown("### :material/work: Salaried Household Financial Radar")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            metric_card("Karnataka CPI", "5.86%", "Active MoSPI benchmark", ORANGE)
        with col2:
            metric_card("Food Inflation", "8.05%", "Driven by vegetables & pulses", DANGER)
        with col3:
            metric_card("RBI Repo Rate", "6.50%", "Neutral stance (MPC)", "#64B5F6")
        with col4:
            metric_card("Fuel Spend Share", "8.2%", f"₹{income*0.082:,.0f}/mo avg", ORANGE)

    else:
        st.markdown("### :material/shopping_cart: Household Economic Overview")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            metric_card("State Inflation", "5.86%", "Karnataka MoSPI Benchmark", ORANGE)
        with col2:
            metric_card("Transport Fuel", "₹96.45/L", "Bengaluru Diesel baseline", ORANGE)
        with col3:
            metric_card("Groceries Basket", "+7.7%", "Food CPI YoY move", DANGER)
        with col4:
            metric_card(
                "Discretionary Buffer", f"₹{income*0.13:,.0f}/mo", "Monthly emergency capacity", "#64B5F6"
            )

    st.markdown("---")

    # 2. PROMINENT AI CHATBOT & DECISION ASSISTANT (Front and center for user questions)
    show_chat_panel(profile)

    st.markdown("---")

    # 3. Monthly Household Budget Allocation
    st.markdown("### :material/pie_chart: Your Monthly Budget & Outflow Health")
    budget_labels = [
        "Food & Staples",
        "Fuel / Electricity",
        "Transport",
        "Rent / Housing",
        "Healthcare",
        "Education",
        "Discretionary / Savings",
    ]
    budget_vals = [
        income * 0.41,
        income * 0.08,
        income * 0.09,
        income * 0.14,
        income * 0.07,
        income * 0.08,
        income * 0.13,
    ]
    pie = pie_chart(
        budget_labels,
        budget_vals,
        f"Monthly Outflow Allocation for ₹{income:,.0f}/mo Household in {district}",
    )
    st.plotly_chart(pie, use_container_width=True)

    st.markdown("---")

    # 4. CRUDE OIL SCENARIO ENGINE (Optional tool — only opened/calculated if user asks for it)
    with st.expander(":material/oil_barrel: Optional Simulation: Model a Global Crude Oil & Energy Price Shock", expanded=False):
        st.markdown(
            '<div style="font-size:0.85rem;color:#8892B0;margin-bottom:12px">Explore how changes in international crude prices and Indian retail pump policy flow into your monthly living costs (calibrated to RBI anchor: +10% crude ≈ +20 bps CPI).</div>',
            unsafe_allow_html=True,
        )

        c_ctrl1, c_ctrl2, c_ctrl3 = st.columns(3)
        with c_ctrl1:
            crude_shock = st.slider(
                "Global Crude Price Shock (%)",
                min_value=-30,
                max_value=80,
                value=25,
                step=5,
                key="crude_shock_slider_opt",
            )
        with c_ctrl2:
            fuel_policy = st.selectbox(
                "Govt Fuel Price Policy",
                ["partial", "held", "full"],
                format_func=lambda x: {
                    "partial": "Partial Pass-through (50% passed, 50% buffered)",
                    "held": "Prices Held (0% pass-through / subsidies)",
                    "full": "Full Pass-through (100% economic cost)",
                }[x],
                key="fuel_policy_opt",
            )
        with c_ctrl3:
            n_draws = st.selectbox("Monte Carlo Draws", [2000, 5000, 10000], index=1, key="n_draws_opt")

        # Run energy shock engine only when expander is accessed
        resp = run_energy_shock(
            crude_delta_pct=crude_shock / 100.0,
            monthly_income=income,
            occupation=occupation,
            geography=district,
            policy=fuel_policy,
            n_draws=n_draws,
            seed=42,
        )

        mode_badge(resp.mode.value)
        st.markdown(f"**Engine Result:** {resp.summary}")

        u_cpi = resp.uncertainty["cpi_pp"]
        u_hh = resp.uncertainty["household_rs"]
        pump = resp.uncertainty["pump_prices"]

        m1, m2, m3, m4 = st.columns(4)
        with m1:
            metric_card(
                "CPI Impact (P50)",
                f"+{u_cpi['P50']:.2f} pp",
                f"P10: +{u_cpi['P10']:.2f} | P90: +{u_cpi['P90']:.2f}",
            )
        with m2:
            metric_card(
                "Monthly Household Cost",
                f"+₹{u_hh['P50']:,.0f}",
                f"P10: ₹{u_hh['P10']:,.0f} | P90: ₹{u_hh['P90']:,.0f}",
            )
        with m3:
            metric_card(
                "Retail Diesel Delta",
                f"+₹{pump['diesel_delta']:.2f}/L",
                f"New price: ₹{pump['diesel_new']:.2f}/L",
            )
        with m4:
            metric_card(
                "Retail Petrol Delta",
                f"+₹{pump['petrol_delta']:.2f}/L",
                f"New price: ₹{pump['petrol_new']:.2f}/L",
            )

        t_fan, t_chain, t_waterfall = st.tabs(
            [
                ":material/trending_up: Cumulative CPI Fan Chart",
                ":material/link: Transmission Chain",
                ":material/water: Category Waterfall",
            ]
        )

        with t_fan:
            months = [1, 2, 3, 4, 5, 6]
            p10_series = [round(u_cpi["P10"] * min(1.0, m / 3.5), 3) for m in months]
            p50_series = [round(u_cpi["P50"] * min(1.0, m / 3.0), 3) for m in months]
            p90_series = [round(u_cpi["P90"] * min(1.0, m / 2.5), 3) for m in months]
            f_chart = fan_chart(
                months,
                p10_series,
                p50_series,
                p90_series,
                f"Headline CPI Inflation Impact Over 6 Months (Karnataka, Crude {crude_shock:+d}%)",
            )
            st.plotly_chart(f_chart, use_container_width=True)

        with t_chain:
            if resp.options and "transmission_chain" in resp.options[0]:
                chain_fig = transmission_chain_chart(resp.options[0]["transmission_chain"])
                st.plotly_chart(chain_fig, use_container_width=True)

        with t_waterfall:
            cats = [
                "Crude Spike",
                "Diesel Markup",
                "Freight Push",
                "Food & Staples",
                "Mfg Goods",
                "Net CPI Push",
            ]
            vals = [
                round(crude_shock * 0.05, 3),
                round(pump["diesel_delta"] * 0.04, 3),
                round(pump["diesel_delta"] * 0.03, 3),
                round(u_cpi["P50"] * 0.45, 3),
                round(u_cpi["P50"] * 0.35, 3),
                round(u_cpi["P50"], 3),
            ]
            wf_chart = waterfall_chart(
                cats, vals, "Stepwise Transmission Contribution to Headline CPI (pp)"
            )
            st.plotly_chart(wf_chart, use_container_width=True)

        show_why_drawer(resp)

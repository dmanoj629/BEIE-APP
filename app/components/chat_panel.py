"""Persistent AI Chatbot component with rules-first intent router.

Rules (Blueprint §11):
- Rules-first router mapping questions to engine functions.
- Returns structured DecisionResponse.
- Calls LLM adapter with strict regex verification or fallback templates.
- Quick-reply chips and slider triggers.
- Multi-lingual output (English, Kannada, Hindi).
"""

from __future__ import annotations

import re
import uuid

import streamlit as st

from app.components.cards import mode_badge
from app.components.charts import (
    fan_chart,
    pie_chart,
    transmission_chain_chart,
)
from app.components.drawers import show_why_drawer
from beie.contracts import DecisionRequest
from beie.explain.adapter import explain
from beie.service import analyze_decision


def route_query_to_request(
    query: str, profile: dict, lang: str = "en"
) -> DecisionRequest:
    """Rules-first intent router: maps natural language query to DecisionRequest."""
    q = query.lower()
    req_id = f"chat-{uuid.uuid4().hex[:8]}"
    panel = profile.get("panel", "citizen")

    # 1. Stock / investment questions
    if any(
        k in q
        for k in [
            "stock",
            "share",
            "invest",
            "25000",
            "25,000",
            "nifty",
            "f&o",
            "mutual fund",
        ]
    ):
        # Extract amount if present
        amt = 25000.0
        amt_match = re.search(r"(\d+[\d,]*)", q)
        if amt_match:
            try:
                raw_amt = amt_match.group(1).replace(",", "")
                if float(raw_amt) > 500:
                    amt = float(raw_amt)
            except ValueError:
                pass
        return DecisionRequest(
            request_id=req_id,
            domain="markets",
            panel=panel,
            query=query,
            user_profile=profile,
            parameters={"amount_rs": amt, "horizon_months": 12},
        )

    # 2. Purchase timing questions
    if any(
        k in q
        for k in [
            "buy",
            "purchase",
            "right time",
            "iphone",
            "phone",
            "mobile",
            "smartphone",
            "android",
            "car",
            "bike",
            "vehicle",
            "tractor",
            "gold",
            "appliance",
            "tv",
            "fridge",
            "laptop",
        ]
    ):
        item = "phone"
        if "gold" in q:
            item = "gold"
        elif any(v in q for v in ["bike", "car", "vehicle", "tractor", "scooter"]):
            item = "vehicle"
        elif any(a in q for a in ["appliance", "fridge", "tv", "washing", "cooler", "ac"]):
            item = "appliance"
        elif any(p in q for p in ["phone", "mobile", "smartphone", "iphone", "android"]):
            item = "phone"

        budget = float(profile.get("monthly_income", 30000)) * 0.6
        amt_match = re.search(r"(\d+[\d,]*)", q)
        if amt_match:
            try:
                b_cand = float(amt_match.group(1).replace(",", ""))
                if b_cand > 1000:
                    budget = b_cand
            except ValueError:
                pass

        return DecisionRequest(
            request_id=req_id,
            domain="purchase",
            panel=panel,
            query=query,
            user_profile=profile,
            parameters={"item_category": item, "budget_rs": budget},
        )

    # 3. Agriculture / crop / heat / weather questions
    if any(
        k in q
        for k in [
            "heat",
            "summer",
            "crop",
            "rice",
            "sugarcane",
            "water",
            "mandi",
            "farmer",
            "agriculture",
            "monsoon",
        ]
    ):
        return DecisionRequest(
            request_id=req_id,
            domain="agriculture",
            panel=panel,
            query=query,
            user_profile=profile,
            parameters={"temp_anomaly_c": 3.0},
        )

    # 4. Loan / EMI / repo rate questions
    if any(
        k in q
        for k in [
            "emi",
            "loan",
            "repo",
            "interest",
            "rbi hike",
            "bank rate",
            "home loan",
        ]
    ):
        return DecisionRequest(
            request_id=req_id,
            domain="finance",
            panel=panel,
            query=query,
            user_profile=profile,
            parameters={
                "repo_delta_bps": 25.0,
                "loan_rs": 1_200_000.0,
                "current_rate_pct": 8.5,
            },
        )

    # 5. Default: Energy shock (crude oil, fuel, inflation, diesel, prices rising)
    crude_delta = 0.25
    pct_match = re.search(r"(\d+)%", q)
    if pct_match:
        try:
            crude_delta = float(pct_match.group(1)) / 100.0
        except ValueError:
            pass
    return DecisionRequest(
        request_id=req_id,
        domain="energy",
        panel=panel,
        query=query,
        user_profile=profile,
        parameters={"crude_delta_pct": crude_delta, "fuel_policy": "partial"},
    )


def show_chat_panel(profile: dict) -> None:
    """Renders the conversational interface."""
    st.markdown("### :material/chat: Bharat Lens AI Assistant")
    lang = st.session_state.get("language", "en")

    # Quick prompt chips
    st.markdown(
        '<div style="font-size:0.8rem;color:#8892B0;margin-bottom:6px">Quick questions you can ask:</div>',
        unsafe_allow_html=True,
    )
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button(":material/smartphone: Right time to buy a mobile?", key="quick_phone"):
            st.session_state["pending_query"] = (
                "I want to buy a mobile phone, is it the right time now or should I wait for festival sales?"
            )
    with c2:
        if st.button(":material/restaurant: Why are grocery prices high?", key="quick_food"):
            st.session_state["pending_query"] = (
                "Why is food and grocery inflation rising in Karnataka and how will it hit my budget?"
            )
    with c3:
        if st.button(":material/payments: Loan EMI under repo rate hike?", key="quick_emi"):
            st.session_state["pending_query"] = (
                "How will a 50 bps RBI repo rate hike affect my monthly loan EMIs?"
            )
    with c4:
        if st.button(":material/agriculture: Farm diesel & fertilizer cost?", key="quick_farm"):
            st.session_state["pending_query"] = (
                "How will fuel prices and summer heat affect farm input costs and mandi prices in Karnataka?"
            )

    # Chat history display
    chat_hist = st.session_state.get("chat_history", [])
    if chat_hist:
        for entry in chat_hist[-6:]:
            if entry["role"] == "user":
                st.markdown(
                    f'<div class="chat-bubble-user"><i class=ic-user></i> <b>You:</b> {entry["text"]}</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f'<div class="chat-bubble-beie"><i class=ic-bot></i> <b>BEIE:</b> {entry["text"]}</div>',
                    unsafe_allow_html=True,
                )

    # Input field
    default_text = st.session_state.pop("pending_query", "")
    user_input = st.chat_input(
        "Ask about inflation, diesel, buying items, stocks, crop water stress...",
        key="chat_input",
    )
    active_query = user_input or default_text

    if active_query:
        # Add to history
        st.session_state["chat_history"].append({"role": "user", "text": active_query})

        # Process with Engine
        req = route_query_to_request(active_query, profile, lang=lang)
        resp = analyze_decision(req)
        st.session_state["last_response"] = resp

        # Generate explanation
        tmpl_ctx = {
            "crude_delta_pct": int(req.parameters.get("crude_delta_pct", 0.25) * 100),
            "p50": resp.uncertainty.get("cpi_pp", {}).get("P50", 0.52),
            "p10": resp.uncertainty.get("cpi_pp", {}).get("P10", 0.35),
            "p90": resp.uncertainty.get("cpi_pp", {}).get("P90", 0.68),
            "income": profile.get("monthly_income", 25000),
            "hh_p50": resp.uncertainty.get("household_rs", {}).get("P50", 250),
            "hh_p10": resp.uncertainty.get("household_rs", {}).get("P10", 170),
            "hh_p90": resp.uncertainty.get("household_rs", {}).get("P90", 330),
            "diesel_delta": resp.uncertainty.get("pump_prices", {}).get(
                "diesel_delta", 3.2
            ),
            "temp_anomaly": req.parameters.get("temp_anomaly_c", 3.0),
            "rice_p50": resp.uncertainty.get("rice_yield_loss_pct", {}).get("P50", 6.0),
            "rice_p10": resp.uncertainty.get("rice_yield_loss_pct", {}).get("P10", 3.0),
            "rice_p90": resp.uncertainty.get("rice_yield_loss_pct", {}).get(
                "P90", 10.0
            ),
            "water_p50": resp.uncertainty.get("water_demand_increase_pct", {}).get(
                "P50", 19.5
            ),
            "rprice_p50": resp.uncertainty.get("rice_mandi_price_increase_pct", {}).get(
                "P50", 2.4
            ),
            "repo_bps": req.parameters.get("repo_delta_bps", 25),
            "months": req.parameters.get("remaining_months", 180),
            "annual_extra": resp.options[0].get("annual_extra_rs", 1200)
            if resp.options
            else 1200,
        }
        custom_key = st.session_state.get("custom_api_key", "").strip() or None
        custom_model = st.session_state.get("custom_api_model", "gemini-2.5-flash")
        expl = explain(
            resp.domain,
            resp.model_dump(),
            lang=lang,
            template_ctx=tmpl_ctx,
            api_key=custom_key,
            model=custom_model,
        )
        st.session_state["chat_history"].append({"role": "beie", "text": expl["text"]})
        st.rerun()

    # If we have a recent response, show the interactive charts below the chat
    resp = st.session_state.get("last_response")
    if resp:
        st.markdown("---")
        mode_badge(resp.mode.value)
        st.markdown(f"#### :material/target: Summary: {resp.summary}")

        # Render domain-specific charts
        if resp.domain == "energy":
            u_cpi = resp.uncertainty.get("cpi_pp", {})
            u_hh = resp.uncertainty.get("household_rs", {})
            if u_cpi:
                months = [1, 2, 3, 4, 5, 6]
                p10s = [u_cpi["P10"] * (m / 6) for m in months]
                p50s = [u_cpi["P50"] * (m / 6) for m in months]
                p90s = [u_cpi["P90"] * (m / 6) for m in months]
                f_fig = fan_chart(
                    months,
                    p10s,
                    p50s,
                    p90s,
                    "Projected Headline CPI Impact in Karnataka (Cumulative pp)",
                )
                st.plotly_chart(f_fig, use_container_width=True)

            if resp.options and "transmission_chain" in resp.options[0]:
                chain_fig = transmission_chain_chart(
                    resp.options[0]["transmission_chain"]
                )
                st.plotly_chart(chain_fig, use_container_width=True)

        elif resp.domain == "agriculture":
            u = resp.uncertainty
            if u:
                labels = [
                    "Rice Yield Loss",
                    "Water Demand Surge",
                    "Rice Mandi Price",
                    "Power Demand Surge",
                ]
                p10_vals = [
                    u["rice_yield_loss_pct"]["P10"],
                    u["water_demand_increase_pct"]["P10"],
                    u["rice_mandi_price_increase_pct"]["P10"],
                    u["power_demand_increase_pct"]["P10"],
                ]
                p50_vals = [
                    u["rice_yield_loss_pct"]["P50"],
                    u["water_demand_increase_pct"]["P50"],
                    u["rice_mandi_price_increase_pct"]["P50"],
                    u["power_demand_increase_pct"]["P50"],
                ]
                p90_vals = [
                    u["rice_yield_loss_pct"]["P90"],
                    u["water_demand_increase_pct"]["P90"],
                    u["rice_mandi_price_increase_pct"]["P90"],
                    u["power_demand_increase_pct"]["P90"],
                ]
                f_fig = fan_chart(
                    [1, 2, 3, 4],
                    p10_vals,
                    p50_vals,
                    p90_vals,
                    "Karnataka Agricultural Heat Impacts (% change by factor)",
                    y_label="% Change",
                )
                st.plotly_chart(f_fig, use_container_width=True)

        elif resp.domain == "purchase":
            opt = resp.options[0] if resp.options else {}
            verdict = opt.get("timing_verdict", "UNCERTAIN")
            reason = opt.get("verdict_reason", "")
            sales = opt.get("upcoming_sale_windows", [])
            alts = opt.get("alternatives", [])

            # Dynamic Verdict Banner
            v_color = "#34D399" if verdict == "BUY NOW" else ("#F59E0B" if verdict == "WAIT" else "#2DD4BF")
            v_icon = "<i class=ic-shopping-bag></i>" if verdict == "BUY NOW" else ("<i class=ic-hourglass></i>" if verdict == "WAIT" else "<i class=ic-search></i>")
            st.markdown(
                f"""<div style="background:rgba(255,255,255,0.04);border:1px solid {v_color};border-radius:14px;padding:16px;margin:12px 0;">
                  <div style="font-size:1.15rem;font-weight:700;color:{v_color};margin-bottom:6px;">{v_icon} Timing Verdict: {verdict}</div>
                  <div style="font-size:0.88rem;color:#E2E8F0;line-height:1.5;">{reason}</div>
                </div>""",
                unsafe_allow_html=True,
            )

            if sales:
                st.markdown("##### :material/sell: Upcoming Major Festive & Sale Windows")
                for s in sales:
                    st.markdown(
                        f"""<div style="background:rgba(45,212,191,0.06);border-left:4px solid #2DD4BF;padding:10px 14px;border-radius:0 8px 8px 0;margin:6px 0;font-size:0.85rem;">
                          <b>{s['sale']}</b> — ~{s['months_away']} month(s) away | Typical Discounts: <b>{s['typical_discount_range'][0]}%–{s['typical_discount_range'][1]}% off</b>
                        </div>""",
                        unsafe_allow_html=True,
                    )

            if alts:
                st.markdown("##### :material/lightbulb: Budget Smart Alternatives")
                for a in alts:
                    st.markdown(f"- **{a['option']}**: {a['note']}")

        elif resp.domain == "markets":
            opt = resp.options[0] if resp.options else {}
            alloc = opt.get("illustrative_allocation", {})
            if alloc:
                clean_alloc = {
                    k: v for k, v in alloc.items() if isinstance(v, (int, float))
                }
                pie = pie_chart(
                    list(clean_alloc.keys()),
                    list(clean_alloc.values()),
                    "Illustrative Diversified Allocation (EXAMPLE ONLY)",
                )
                st.plotly_chart(pie, use_container_width=True)

        # Why drawer
        show_why_drawer(resp)

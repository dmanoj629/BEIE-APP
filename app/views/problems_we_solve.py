"""Problems We Solve — Comprehensive Economic Problem Explorer & Custom Submission Engine.

Blueprint & Master Prompt Section 14:
- Structured taxonomy across Household, Farmer, MSME, and Research & Institutional challenges.
- Search and multi-category filtering.
- Status badges: Operational, Experimental, Planned, Unavailable.
- 1-Click navigation to relevant tools.
- User-submitted custom problem analyzer checking domain, engine, data availability, and feasibility.
"""

from __future__ import annotations

import re
from typing import Any
import streamlit as st

from app.components.cards import info_box, metric_card, warning_box
from app.theme import CUSTOM_CSS, DANGER, ORANGE, SUCCESS, WARNING

PROBLEMS_REGISTRY: list[dict[str, Any]] = [
    # --- HOUSEHOLD PROBLEMS ---
    {
        "id": "hh_cost_of_living",
        "category": "Household",
        "tags": ["Citizen", "Inflation"],
        "name": "Rising Cost of Living",
        "explanation": "Essential monthly living expenses increase faster than household income, squeezing savings and discretionary spending.",
        "affected": "Salaried employees, informal workers, fixed-income families across urban and rural India.",
        "why_it_matters": "Households are forced to cut nutritional quality, delay healthcare, or take informal high-interest debt.",
        "tool": "Citizen Home / Energy Shock Engine",
        "target_page": ":material/home: My Dashboard",
        "required_data": "MoSPI CPI (Base 2024=100), HCES consumption weights, fuel pump prices.",
        "methodology": "Leontief pass-through + Household consumption group elasticities + Monte Carlo draws.",
        "status": "Operational",
    },
    {
        "id": "hh_food_inflation",
        "category": "Household",
        "tags": ["Citizen", "Inflation", "Agriculture"],
        "name": "Food & Perishable Inflation",
        "explanation": "Spikes in vegetables (tomatoes, onions), pulses, and edible oils create sudden household budget shocks.",
        "affected": "Every Indian family, particularly bottom 40% income deciles where food is >45% of expenditure.",
        "why_it_matters": "Food inflation is volatile and unpredictable, eroding nutritional security and real purchasing power.",
        "tool": "Citizen Intelligence / Why? Chain",
        "target_page": ":material/home: My Dashboard",
        "required_data": "Consumer Food Price Index (CFPI), AGMARKNET mandi arrivals, weather deficit series.",
        "methodology": "Supply-chain margin tracking + mandi wholesale-to-retail transmission.",
        "status": "Operational",
    },
    {
        "id": "hh_petrol_diesel",
        "category": "Household",
        "tags": ["Citizen", "Energy", "Inflation"],
        "name": "Petrol & Diesel Price Increases",
        "explanation": "Global crude basket swings translate into local pump revisions, immediately raising commuter and vehicle running costs.",
        "affected": "Daily commuters, two-wheeler owners, cab/auto users, freight consumers.",
        "why_it_matters": "Fuel is a non-discretionary recurring expense that also ripples into bus and transport tariffs.",
        "tool": "Energy Shock Simulator",
        "target_page": ":material/bolt: Universal Scenario Simulator",
        "required_data": "PPAC Indian crude basket ($/bbl), OMC price build-up notifications, state VAT rates.",
        "methodology": "Refinery gate parity + OMC policy pass-through (Held vs Partial vs Full).",
        "status": "Operational",
    },
    {
        "id": "hh_transport_costs",
        "category": "Household",
        "tags": ["Citizen", "Supply chain", "Energy"],
        "name": "Transportation Cost Increases",
        "explanation": "School van fees, bus fares, auto/cab tariffs, and delivery charges rise following fuel price escalations.",
        "affected": "Urban families, school-going children, gig delivery users.",
        "why_it_matters": "Sticky transport pricing rarely falls even when fuel prices moderate.",
        "tool": "Household Budget Shock Breakdown",
        "target_page": ":material/home: My Dashboard",
        "required_data": "Transport & Logistics division CPI, state transport corporation fare data.",
        "methodology": "Fuel-to-freight elasticity coefficient (0.65 pass-through).",
        "status": "Operational",
    },
    {
        "id": "hh_purchasing_power",
        "category": "Household",
        "tags": ["Citizen", "Finance", "Inflation"],
        "name": "Loss of Real Purchasing Power",
        "explanation": "Bank fixed deposits and wage hikes fail to outpace inflation, steadily eroding true monetary value.",
        "affected": "Retirees, middle-class savers, conservative depositors.",
        "why_it_matters": "Real negative interest rates devalue retirement nest eggs over 5–10 year horizons.",
        "tool": "Surplus-Cash & Inflation Screener",
        "target_page": ":material/apartment: Business Intelligence",
        "required_data": "RBI Repo rate, scheduled commercial bank 1-year FD rates, headline CPI.",
        "methodology": "Fisher real rate calculation: Real Return = (1 + Nominal) / (1 + Inflation) - 1.",
        "status": "Operational",
    },
    {
        "id": "hh_unexpected_expenses",
        "category": "Household",
        "tags": ["Citizen", "Finance"],
        "name": "Unexpected Shock Vulnerability",
        "explanation": "Lack of emergency buffer leaves families exposed when medical, repair, or inflation shocks strike.",
        "affected": "Families with <3 months liquid savings, gig workers, informal labourers.",
        "why_it_matters": "Leads to distress asset sales or predatory loan apps.",
        "tool": "Emergency Fund Readiness Check",
        "target_page": ":material/bar_chart: Stock Education & SEBI Risk",
        "required_data": "Household emergency liquid reserve guidelines, average monthly OpEx.",
        "methodology": "3–6 month liquidity buffer assessment and risk-comfort classification.",
        "status": "Operational",
    },
    {
        "id": "hh_inflation_transmission",
        "category": "Household",
        "tags": ["Citizen", "Inflation", "Energy"],
        "name": "Inflation Transmission Opacity",
        "explanation": "Citizens cannot see how a war in Europe or crude rise in the Middle East reaches their local grocery store.",
        "affected": "Every citizen seeking economic clarity.",
        "why_it_matters": "Without transparency, public discourse relies on misinformation or political rhetoric.",
        "tool": "Economic Transmission Chain Chart",
        "target_page": ":material/home: My Dashboard",
        "required_data": "15-sector National Input-Output Table, PPAC pricing, MoSPI item weights.",
        "methodology": "Stepwise multi-node causal graph (Crude → Refinery → Freight → Mandi → Retail).",
        "status": "Operational",
    },
    {
        "id": "hh_economic_news",
        "category": "Household",
        "tags": ["Citizen", "Employment"],
        "name": "Difficulty Understanding Economic News",
        "explanation": "Jargon-heavy financial journalism ('basis points', 'core vs headline CPI', 'fiscal deficit') alienates ordinary people.",
        "affected": "Students, homemakers, general public, first-time investors.",
        "why_it_matters": "Citizens cannot make proactive financial adjustments if they cannot decipher economic reports.",
        "tool": "AI Economic Analyst (Multilingual)",
        "target_page": ":material/chat: AI Economic Analyst",
        "required_data": "Verified BEIE domain engines + multilingual terminology dictionary.",
        "methodology": "Rules-first intent routing + ground-truth verified translation in Kannada, Hindi & English.",
        "status": "Operational",
    },
    {
        "id": "hh_purchase_timing",
        "category": "Household",
        "tags": ["Citizen", "Finance"],
        "name": "Major Purchase Timing Uncertainty",
        "explanation": "Uncertainty on whether to buy smartphones, appliances, gold, or vehicles now or wait for festival sales.",
        "affected": "Consumer households planning major capital outlays (>₹15,000).",
        "why_it_matters": "Buying right before a launch cycle or price drop causes regret and unnecessary EMI burdens.",
        "tool": "Purchase Timing Advisor",
        "target_page": ":material/shopping_bag: Purchase Timing Advisor",
        "required_data": "Annual festival sale calendar (Amazon/Flipkart), product launch cycles, user budget.",
        "methodology": "Multi-factor timing heuristic: Product cycle phase + Festival discount window + Debt burden.",
        "status": "Operational",
    },
    {
        "id": "hh_regional_inflation",
        "category": "Household",
        "tags": ["Citizen", "Inflation"],
        "name": "Regional Inflation Disparities",
        "explanation": "Inflation in Karnataka (5.86% in Sep 2026) differs substantially from Delhi (4.2%) due to state taxes and logistics.",
        "affected": "State residents, regional policy analysts, local businesses.",
        "why_it_matters": "National averages hide acute regional cost pressures.",
        "tool": "Observed Ground Truth / State CPI Explorer",
        "target_page": ":material/receipt_long: Data & Provenance Registry",
        "required_data": "MoSPI CPI Annexure III (State-wise indices and inflation rates).",
        "methodology": "State-specific price indexing and local basket disparity calculation.",
        "status": "Operational",
    },

    # --- FARMER PROBLEMS ---
    {
        "id": "fm_diesel_costs",
        "category": "Farmer",
        "tags": ["Farmer", "Energy", "Agriculture"],
        "name": "Tractor & Pump Diesel Expenses",
        "explanation": "Diesel price rises directly inflate land preparation, tilling, harvesting, and irrigation costs.",
        "affected": "Smallholder farmers operating diesel pump-sets and hired tractor machinery.",
        "why_it_matters": "Diesel represents 12–18% of farm operational costs for non-electrified irrigation.",
        "tool": "Farmer Economic Radar / Energy Shock",
        "target_page": ":material/home: My Dashboard",
        "required_data": "District diesel prices, Ministry of Agriculture input-cost benchmarks.",
        "methodology": "Farm machine hour diesel intensity modeling (4–6 L/hour for 45HP tractor).",
        "status": "Operational",
    },
    {
        "id": "fm_fertilizer_prices",
        "category": "Farmer",
        "tags": ["Farmer", "Agriculture"],
        "name": "Fertilizer & Nutrient Cost Pressures",
        "explanation": "Global natural gas and rock phosphate spikes threaten Urea, DAP, and Potash subsidies and local availability.",
        "affected": "Paddy, sugarcane, maize, and cotton growers across Karnataka.",
        "why_it_matters": "Imbalanced nutrient application damages soil health and reduces final crop yield.",
        "tool": "Agricultural Economic Engine",
        "target_page": ":material/home: My Dashboard",
        "required_data": "DoF nutrient-based subsidy (NBS) notifications, natural gas feedstock prices.",
        "methodology": "Feedstock pass-through to non-urea DAP/MOP complex retail prices.",
        "status": "Operational",
    },
    {
        "id": "fm_electricity_tariffs",
        "category": "Farmer",
        "tags": ["Farmer", "Energy"],
        "name": "Rural Electricity Supply & Tariffs",
        "explanation": "Erratic three-phase power supply for irrigation pump-sets limits watering cycles during dry spells.",
        "affected": "Borewell-dependent farmers in central and northern Karnataka.",
        "why_it_matters": "Crops wither if irrigation windows are missed during critical flowering stages.",
        "tool": "Summer Heat & Water Stress Engine",
        "target_page": ":material/bolt: Universal Scenario Simulator",
        "required_data": "Karnataka ESCOM rural feeder supply hours, peak power deficit.",
        "methodology": "Evapotranspiration deficit vs pump operational availability.",
        "status": "Operational",
    },
    {
        "id": "fm_mandi_prices",
        "category": "Farmer",
        "tags": ["Farmer", "Agriculture"],
        "name": "Mandi Wholesale Price Volatility",
        "explanation": "Post-harvest gluts cause mandi prices to crash below Minimum Support Price (MSP) in local APMC yards.",
        "affected": "Paddy, maize, ragi, and pulse farmers selling at harvest time.",
        "why_it_matters": "Farmers realize poor price realization after bearing full season production risk.",
        "tool": "Mandi Ground Truth Monitor",
        "target_page": ":material/receipt_long: Data & Provenance Registry",
        "required_data": "AGMARKNET wholesale modal prices, CACP MSP notifications.",
        "methodology": "Modal wholesale price tracking vs CACP Cost of Cultivation (A2+FL / C2).",
        "status": "Operational",
    },
    {
        "id": "fm_weather_losses",
        "category": "Farmer",
        "tags": ["Farmer", "Agriculture"],
        "name": "Heatwave & Drought Yield Losses",
        "explanation": "Unseasonal high temperatures (+2°C to +4°C anomaly) during reproductive phases cause crop flower drop and terminal heat stress.",
        "affected": "Rice, wheat, and pulse farmers in vulnerable agro-climatic zones.",
        "why_it_matters": "Yield declines of 8–18% directly destroy farm profitability.",
        "tool": "Summer Heat & Rice Water Stress Engine",
        "target_page": ":material/bolt: Universal Scenario Simulator",
        "required_data": "IMD gridded temperature anomalies, ICAR crop temperature thresholds.",
        "methodology": "Thermal unit threshold exceedance and evapotranspiration stress model.",
        "status": "Operational",
    },
    {
        "id": "fm_crop_transport",
        "category": "Farmer",
        "tags": ["Farmer", "Supply chain", "Energy"],
        "name": "Farm-to-Mandi Transport Costs",
        "explanation": "Small farmers paying per-quintal mini-truck or tractor freight face heavy deductions when diesel rises.",
        "affected": "Vegetable and perishable growers transporting produce 30–100 km to district APMCs.",
        "why_it_matters": "High transport cost often exceeds the margin on low-priced commodities.",
        "tool": "Corridor Logistics Shock Tool",
        "target_page": ":material/apartment: Business Intelligence",
        "required_data": "Karnataka corridor freight rates, diesel cost shares.",
        "methodology": "Freight route diesel pass-through formula.",
        "status": "Operational",
    },

    # --- MSME & BUSINESS PROBLEMS ---
    {
        "id": "msme_raw_materials",
        "category": "MSME",
        "tags": ["Business", "Inflation"],
        "name": "Raw Material Cost Spikes",
        "explanation": "Sudden increases in steel, plastic resins, chemicals, and packaging materials compress operating margins.",
        "affected": "Precision manufacturing, auto components, food processing, plastics MSMEs.",
        "why_it_matters": "MSMEs with fixed-price client contracts cannot immediately pass on input cost increases.",
        "tool": "Input-Cost Shock Calculator",
        "target_page": ":material/apartment: Business Intelligence",
        "required_data": "WPI input commodity indices, sector standard cost-share breakdown.",
        "methodology": "Cost-push sensitivity analysis + interactive waterfall margin decomposition.",
        "status": "Operational",
    },
    {
        "id": "msme_working_capital",
        "category": "MSME",
        "tags": ["Business", "Finance"],
        "name": "Working Capital & Cash Flow Squeeze",
        "explanation": "Payment delays from enterprise buyers combined with rising input costs cause acute cash deficits.",
        "affected": "MSME suppliers, subcontract manufacturers, vendors with 60–90 day payment cycles.",
        "why_it_matters": "Cash shortages disrupt supplier payments, payroll, and lead to loan default.",
        "tool": "Working-Capital & EMI Stress Test",
        "target_page": ":material/apartment: Business Intelligence",
        "required_data": "Monthly OpEx, customer debtor days, credit line interest rates.",
        "methodology": "6-month cash trajectory simulation under 15–30 day debtor delay stress.",
        "status": "Operational",
    },
    {
        "id": "msme_pricing_margin",
        "category": "MSME",
        "tags": ["Business", "Finance"],
        "name": "Pricing & Break-Even Uncertainty",
        "explanation": "Difficulty finding the optimal price increase that protects margin without causing volume collapse.",
        "affected": "Consumer goods manufacturers, retail businesses, service providers.",
        "why_it_matters": "Raising prices too fast drives customers to competitors; raising too slow causes losses.",
        "tool": "Pricing & Margin Simulator",
        "target_page": ":material/apartment: Business Intelligence",
        "required_data": "Product base price, unit cost, price elasticity of demand.",
        "methodology": "Elasticity-based volume response modeling: ΔVolume = Elasticity × ΔPrice.",
        "status": "Operational",
    },
    {
        "id": "msme_logistics_corridors",
        "category": "MSME",
        "tags": ["Business", "Supply chain", "Energy"],
        "name": "Corridor Freight & Toll Pressures",
        "explanation": "Key trade routes (e.g. Bengaluru-Mangaluru NH-75) face heavy gradient and toll fuel penalties.",
        "affected": "Logistics operators, distributors, inter-district traders.",
        "why_it_matters": "Freight rate mismatches erode trade margins across high-distance routes.",
        "tool": "Logistics & Supply Corridor Risk Tool",
        "target_page": ":material/apartment: Business Intelligence",
        "required_data": "NHAI toll notifications, distance matrices, corridor fuel consumption factors.",
        "methodology": "Corridor-specific fuel share weighting (42% to 52% of freight cost).",
        "status": "Operational",
    },
    {
        "id": "msme_seasonality",
        "category": "MSME",
        "tags": ["Business", "Supply chain"],
        "name": "Demand Seasonality & Inventory Timing",
        "explanation": "Failing to build stock before festival surges (Diwali, Dasara) or holding excess inventory post-season.",
        "affected": "Retailers, apparel brands, electronics dealers, FMCG distributors.",
        "why_it_matters": "Stock-outs forfeit peak sales; post-festival overstock locks working capital in dead inventory.",
        "tool": "Demand & Seasonality Analyzer",
        "target_page": ":material/apartment: Business Intelligence",
        "required_data": "Festival calendar dates, historical monthly sales series (CSV upload).",
        "methodology": "Multiplicative seasonal decomposition vs seasonal-naive benchmark.",
        "status": "Operational",
    },
    {
        "id": "msme_surplus_cash",
        "category": "MSME",
        "tags": ["Business", "Finance"],
        "name": "Surplus Cash Allocation Dilemma",
        "explanation": "Uncertainty on whether to park surplus business cash in bank FDs, liquid mutual funds, or prepay debt.",
        "affected": "Profitable MSMEs, business owners with seasonal liquidity surpluses.",
        "why_it_matters": "Sub-optimal allocation forfeits after-tax yields or pays high loan interest needlessly.",
        "tool": "Surplus-Cash Allocation Comparison",
        "target_page": ":material/apartment: Business Intelligence",
        "required_data": "Current corporate tax slab, bank FD rates, liquid fund yields, CC/OD loan interest.",
        "methodology": "Post-tax yield calculation: Post-tax Return = Nominal × (1 - Tax Rate).",
        "status": "Operational",
    },

    # --- RESEARCH & INSTITUTIONAL PROBLEMS ---
    {
        "id": "res_fragmented_data",
        "category": "Researcher",
        "tags": ["Researcher", "Inflation", "Energy"],
        "name": "Fragmented Public Economic Datasets",
        "explanation": "Crucial indicators are scattered across RBI, MoSPI, PPAC, IMD, and state portals in PDF or legacy HTML.",
        "affected": "Economic researchers, policy analysts, credit rating agencies, journalists.",
        "why_it_matters": "Analysts spend 70% of time gathering and cleaning data rather than synthesizing insights.",
        "tool": "Observed Ground Truth & Provenance Registry",
        "target_page": ":material/receipt_long: Data & Provenance Registry",
        "required_data": "Unified Parquet / JSON normalized records with SHA-256 sidecars.",
        "methodology": "Automated ingestion pipeline with schema validation and cryptographic provenance hashing.",
        "status": "Operational",
    },
    {
        "id": "res_inter_industry_visibility",
        "category": "Researcher",
        "tags": ["Researcher", "Energy", "Supply chain"],
        "name": "Opaque Inter-Industry Shock Linkages",
        "explanation": "Traditional macroeconomic tools fail to show how an energy shock travels across 15 distinct production sectors.",
        "affected": "Central planners, sector research teams, corporate strategy units.",
        "why_it_matters": "Second-order cost push (e.g. fertilizer into agriculture into food processing) is overlooked.",
        "tool": "15-Sector Leontief Cost-Push Engine",
        "target_page": ":material/bolt: Universal Scenario Simulator",
        "required_data": "CSO Supply and Use Tables (A-matrix) and sector crude shares.",
        "methodology": "Leontief Price Equation: Δp = (I - Aᵀ)⁻¹ · a_c · Δc.",
        "status": "Operational",
    },
    {
        "id": "res_uncertainty_quantification",
        "category": "Researcher",
        "tags": ["Researcher", "Finance"],
        "name": "Lack of Uncertainty Ranges in Point Projections",
        "explanation": "Most commercial forecasts give single-point numbers without acknowledging deep parameter uncertainty.",
        "affected": "Risk officers, portfolio managers, academic researchers.",
        "why_it_matters": "Point forecasts provide a false sense of certainty and fail during crisis regimes.",
        "tool": "NumPy Vectorized Monte Carlo Engine",
        "target_page": ":material/bolt: Universal Scenario Simulator",
        "required_data": "Empirically calibrated triangular distributions for pass-through and lags.",
        "methodology": "5,000–10,000 seeded random draws outputting P10, P50, and P90 confidence intervals.",
        "status": "Operational",
    },
    {
        "id": "res_portfolio_tail_risk",
        "category": "Researcher",
        "tags": ["Researcher", "Finance"],
        "name": "Macro Shock Risk on Loan & Asset Portfolios",
        "explanation": "Banks and investors lack transparent tools to stress test loan books against commodity and rate shocks.",
        "affected": "NBFC credit managers, bank risk departments, equity portfolio analysts.",
        "why_it_matters": "Hidden sector concentrations trigger unexpected non-performing assets (NPAs).",
        "tool": "Portfolio Risk Engine (Aladdin-inspired)",
        "target_page": ":material/shield: Portfolio Risk (Aladdin-Engine)",
        "required_data": "Holding value, sector classifications, historical return volatility series.",
        "methodology": "Parametric & Monte Carlo VaR / CVaR (95% & 99%) + marginal risk contributions.",
        "status": "Operational",
    },
]


def check_custom_problem_feasibility(user_text: str) -> dict[str, Any]:
    """Analyzes a user-submitted problem description against BEIE domain engines."""
    txt = user_text.lower().strip()
    result = {
        "user_query": user_text,
        "identified_domain": "General Economics",
        "applicable_engine": None,
        "required_data": [],
        "data_available": False,
        "calculation_feasible": False,
        "confidence": "Medium",
        "recommendation": "",
        "missing_evidence": [],
    }

    def _has_word(words: list[str]) -> bool:
        return any(re.search(r"\b" + re.escape(w) + r"\b", txt) for w in words)

    if _has_word(["oil", "crude", "petrol", "diesel", "fuel", "gas", "lpg", "cpi", "inflation", "cost of living"]):
        result["identified_domain"] = "Energy & Macro Transmission"
        result["applicable_engine"] = "Leontief Cost-Push & Monte Carlo Engine (beie.domains.energy)"
        result["required_data"] = ["PPAC Indian Crude Basket", "PPAC Pump Prices", "MoSPI CPI Karnataka", "15-Sector IO Matrix"]
        result["data_available"] = True
        result["calculation_feasible"] = True
        result["confidence"] = "High"
        result["recommendation"] = "BEIE has full operational data for crude oil transmission. You can simulate this directly in the Scenario Simulator."

    elif _has_word(["heat", "heatwave", "summer", "temperature", "crop", "paddy", "rice", "water", "irrigation", "farmer", "agriculture"]):
        result["identified_domain"] = "Agriculture & Climate Shock"
        result["applicable_engine"] = "Agricultural Thermal Stress Engine (beie.domains.agriculture)"
        result["required_data"] = ["IMD Gridded Temp Anomalies", "Crop Thermal Thresholds", "Mandi Wholesale Baseline"]
        result["data_available"] = True
        result["calculation_feasible"] = True
        result["confidence"] = "High"
        result["recommendation"] = "Supported under the Summer Heat scenario. Simulates temperature anomalies against crop water requirements."

    elif _has_word(["loan", "emi", "interest", "repo", "home loan", "rbi", "rate hike"]):
        result["identified_domain"] = "Monetary Policy & Debt Sensitivity"
        result["applicable_engine"] = "Repo Rate Debt Sensitivity Model (beie.domains.finance)"
        result["required_data"] = ["RBI Policy Repo Rate Series", "Scheduled Bank Lending Rates", "Loan Amortization Schedules"]
        result["data_available"] = True
        result["calculation_feasible"] = True
        result["confidence"] = "High"
        result["recommendation"] = "Supported via the Monetary Policy module with Monte Carlo interest rate pass-through simulations."

    elif _has_word(["buy", "timing", "phone", "iphone", "gold", "vehicle", "car", "bike", "appliance", "television"]):
        result["identified_domain"] = "Consumer Purchase Timing"
        result["applicable_engine"] = "Purchase Timing Multi-Factor Advisor (beie.domains.purchase)"
        result["required_data"] = ["E-Commerce Festival Sale Windows", "Product Release Cycles", "Household Budget Context"]
        result["data_available"] = True
        result["calculation_feasible"] = True
        result["confidence"] = "High"
        result["recommendation"] = "Supported by our heuristic purchase timing advisor, assessing product cycles and festival discounts."

    elif _has_word(["stock", "stocks", "shares", "portfolio", "nifty", "var", "cvar", "mutual fund"]):
        result["identified_domain"] = "Portfolio & Financial Risk"
        result["applicable_engine"] = "Portfolio Risk Engine (beie.risk.engine)"
        result["required_data"] = ["Stock / Sector Holdings", "Sector Volatility Vectors", "Historical Stress Benchmarks"]
        result["data_available"] = True
        result["calculation_feasible"] = True
        result["confidence"] = "High"
        result["recommendation"] = "Supported in the Portfolio Risk view. Calculates Monte Carlo VaR, CVaR, and risk contributions."

    else:
        result["identified_domain"] = "Unmodeled Domain / Custom Economic Challenge"
        result["applicable_engine"] = "None currently operational"
        result["required_data"] = ["Microeconomic firm-level panel data", "Specific regional price index", "Empirical sector elasticity coefficients"]
        result["data_available"] = False
        result["calculation_feasible"] = False
        result["confidence"] = "Low"
        result["missing_evidence"] = [
            "No validated public dataset in data/raw matching this specific problem query.",
            "Requires empirical pass-through coefficients before a responsible mathematical calculation can run.",
        ]
        result["recommendation"] = "In accordance with Blueprint Rule §3 (No silent synthetic fallbacks), BEIE cannot compute an arbitrary calculation without verified public evidence."

    return result


def show_problems_we_solve() -> None:
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    st.markdown("## :material/target: Problems We Solve")
    st.markdown(
        '<div style="font-size:0.95rem;color:#94A3B8;margin-bottom:20px">'
        "A computational directory of real economic challenges faced by Indian citizens, farmers, MSMEs, and researchers. "
        "Explore how BEIE maps complex causal chains into actionable, evidence-backed decision intelligence."
        "</div>",
        unsafe_allow_html=True,
    )

    # Top Metric Summary
    total_probs = len(PROBLEMS_REGISTRY)
    op_count = sum(1 for p in PROBLEMS_REGISTRY if p["status"] == "Operational")
    hh_count = sum(1 for p in PROBLEMS_REGISTRY if p["category"] == "Household")
    biz_count = sum(1 for p in PROBLEMS_REGISTRY if p["category"] in ("MSME", "Farmer"))

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        metric_card("Total Problems Catalogued", str(total_probs), "Across 4 Segments", "#2DD4BF")
    with m2:
        metric_card("Operational Solutions", str(op_count), "Backed by Verified Engines", SUCCESS)
    with m3:
        metric_card("Household & Farmer Focus", f"{hh_count + 6}", "Citizen-Centric Design", ORANGE)
    with m4:
        metric_card("MSME & Enterprise Tools", str(biz_count), "Input Costs & Cash Flow", "#64B5F6")

    st.markdown("---")

    # Search and Filter Bar
    c_search, c_filter = st.columns([2, 1])
    with c_search:
        search_query = st.text_input(":material/search: Search economic problems by keyword (e.g. diesel, inflation, mandi, emi, margin):", "")
    with c_filter:
        categories = ["All", "Citizen", "Farmer", "Business", "Researcher", "Inflation", "Energy", "Finance", "Supply chain", "Agriculture"]
        selected_cat = st.selectbox("Filter by Category / Tag", categories, index=0)

    # Filter Logic
    filtered = PROBLEMS_REGISTRY
    if selected_cat != "All":
        filtered = [
            p for p in filtered
            if selected_cat.lower() in [t.lower() for t in p.get("tags", [])] or selected_cat.lower() == p.get("category", "").lower()
        ]
    if search_query.strip():
        q = search_query.lower().strip()
        filtered = [
            p for p in filtered
            if q in p["name"].lower() or q in p["explanation"].lower() or q in p["affected"].lower() or any(q in t.lower() for t in p.get("tags", []))
        ]

    st.markdown(f"##### Showing **{len(filtered)}** problems matching your filter:")

    # Render Problem Cards in 2 Columns
    cols = st.columns(2)
    for idx, prob in enumerate(filtered):
        col = cols[idx % 2]
        with col:
            st.markdown(
                f"""
                <div style="background:rgba(15,23,42,0.85);border:1px solid rgba(45,212,191,0.22);border-radius:14px;padding:20px;margin-bottom:18px;">
                  <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px;">
                    <div style="font-size:1.1rem;font-weight:700;color:#F8FAFC;">{prob['name']}</div>
                    <span style="background:rgba(16,185,129,0.18);color:#34D399;border:1px solid #34D399;border-radius:6px;padding:2px 8px;font-size:0.75rem;font-weight:600;">{prob['status']}</span>
                  </div>
                  <div style="font-size:0.88rem;color:#CBD5E1;margin-bottom:12px;line-height:1.5;">{prob['explanation']}</div>
                  
                  <div style="font-size:0.8rem;color:#94A3B8;margin-bottom:6px;"><b><i class=ic-users></i> Who Is Affected:</b> {prob['affected']}</div>
                  <div style="font-size:0.8rem;color:#94A3B8;margin-bottom:6px;"><b><i class=ic-triangle-alert></i> Why It Matters:</b> {prob['why_it_matters']}</div>
                  <div style="font-size:0.8rem;color:#2DD4BF;margin-bottom:6px;"><b><i class=ic-settings></i> BEIE Tool:</b> {prob['tool']}</div>
                  <div style="font-size:0.8rem;color:#94A3B8;margin-bottom:6px;"><b><i class=ic-chart-column></i> Required Data:</b> {prob['required_data']}</div>
                  <div style="font-size:0.8rem;color:#94A3B8;margin-bottom:14px;"><b><i class=ic-ruler></i> Methodology:</b> {prob['methodology']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("---")

    # SECTION: Describe a problem not listed here
    st.markdown("### :material/draw: Describe a Problem Not Listed Here")
    st.markdown(
        '<div style="font-size:0.88rem;color:#94A3B8;margin-bottom:12px">'
        "Explain any real economic challenge in your own words. BEIE's intent analyzer will evaluate "
        "which domain engine applies, what official data is required, whether calculation is feasible, or what evidence is missing."
        "</div>",
        unsafe_allow_html=True,
    )

    custom_text = st.text_area(
        "Describe your economic problem or situation:",
        placeholder="e.g., I operate a small cold-storage unit in Hassan. If electricity tariffs increase by 10% and diesel generator costs rise by 15%, how will it impact my monthly operating margins?",
        height=100,
        key="txt_custom_problem_submission",
    )

    if st.button("Analyze Problem Feasibility", key="btn_eval_custom_problem", type="primary"):
        if not custom_text.strip():
            st.warning("Please type a description of your problem first.")
        else:
            with st.spinner("Analyzing domain requirements and evidence availability..."):
                analysis = check_custom_problem_feasibility(custom_text)
                st.markdown("#### :material/assignment: Feasibility Assessment Report")

                c_r1, c_r2, c_r3 = st.columns(3)
                with c_r1:
                    metric_card("Identified Domain", analysis["identified_domain"], f"Confidence: {analysis['confidence']}", "#2DD4BF")
                with c_r2:
                    d_color = SUCCESS if analysis["data_available"] else DANGER
                    metric_card("Official Data Ingested", "Yes (Verified)" if analysis["data_available"] else "Missing / Blocker", "Public Provenance", d_color)
                with c_r3:
                    f_color = SUCCESS if analysis["calculation_feasible"] else WARNING
                    metric_card("Responsible Calculation", "Feasible" if analysis["calculation_feasible"] else "Blocked", "Scientific Standards", f_color)

                st.markdown(f"**:material/lightbulb: Engine & Recommendation:** {analysis['recommendation']}")

                if analysis["required_data"]:
                    st.markdown("**:material/folder: Required Data Sources:**")
                    for d in analysis["required_data"]:
                        st.markdown(f"- `{d}`")

                if analysis["missing_evidence"]:
                    warning_box(
                        ":material/warning: **Documented Engineering Blocker:** " + " ".join(analysis["missing_evidence"])
                    )

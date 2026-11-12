"""Professional Institutional Landing Page & Entry Gateway for BEIE."""

from __future__ import annotations

import streamlit as st
from app.theme import CUSTOM_CSS, ORANGE, CYAN, SUCCESS, asset_data_uri
from app.state import logout_user


def show_landing() -> None:
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    is_auth = st.session_state.get("is_authenticated", False)
    user_name = st.session_state.get("user_name", "")
    api_key_set = bool(st.session_state.get("custom_api_key", "").strip())
    get_started = st.session_state.get("get_started_active", False)

    # 1. Top Global Navigation & Ticker Ribbon
    st.markdown(
        """
        <div class="ticker-wrap">
          <div style="display:flex;align-items:center;gap:12px;overflow-x:auto;">
            <span style="color:#2DD4BF;font-weight:700;letter-spacing:1px;font-size:0.75rem;">LIVE MACRO RADAR:</span>
            <span class="ticker-item">Crude Basket: <span class="ticker-val">$74.10/bbl</span></span>
            <span class="ticker-item">All-India CPI: <span class="ticker-val">5.54%</span></span>
            <span class="ticker-item">Karnataka CPI: <span class="ticker-val">5.86%</span></span>
            <span class="ticker-item">Bengaluru Diesel: <span class="ticker-val">₹96.45/L</span></span>
            <span class="ticker-item">RBI Repo: <span class="ticker-val">6.50%</span></span>
          </div>
          <div style="font-size:0.75rem;color:#94A3B8;font-family:'JetBrains Mono',monospace;">
            OFFICIAL MOSPI & PPAC GROUND TRUTH
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Top Bar: Brand, Identity & AI status
    c_nav1, c_nav2, c_nav3 = st.columns([3, 1, 1])
    with c_nav1:
        st.markdown(
            f"""<div class="brand">
              <img src="{asset_data_uri('logo.png')}" alt="BEIE logo" />
              <span class="brand-name">BEIE</span>
              <span class="brand-sub">Bharat Economic Intelligence Engine</span>
            </div>""",
            unsafe_allow_html=True,
        )
    with c_nav2:
        if is_auth:
            st.markdown(f'<div style="text-align:left;font-size:0.85rem;color:#2DD4BF;margin:6px 0 8px 0;"><i class=ic-user></i> <b>{user_name}</b></div>', unsafe_allow_html=True)
            if st.button("Sign Out", key="btn_top_signout"):
                logout_user()
                st.rerun()
        else:
            if st.button(":material/lock: Sign In / Register", key="btn_top_signin"):
                st.session_state["auth_screen_active"] = True
                st.rerun()
    with c_nav3:
        if api_key_set:
            st.markdown('<div style="text-align:right;font-size:0.8rem;color:#34D399;margin-top:6px;"><i class=ic-bot></i> <b>AI Key: Active</b></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="text-align:right;font-size:0.8rem;color:#94A3B8;margin-top:6px;"><i class=ic-settings></i> AI: Template Mode</div>', unsafe_allow_html=True)

    st.markdown("---")

    # 2. Hero Section
    st.markdown(
        """
        <div class="hero-container">
          <div class="hero-badge"><i class=ic-landmark></i> BHARAT INNOVATION CHALLENGE 2.0 · VIKSIT BHARAT 2047</div>
          <h1 class="hero-title">A Computational Map of India's Economy</h1>
          <p class="hero-subtitle">
            What happens when global crude oil surges 25% or summer heat strains water reservoirs? 
            BEIE traces macroeconomic shocks across sectors and regions to quantify the precise impact on 
            <strong>households, farmers, workers, and MSMEs</strong> with transparent Monte Carlo distributions.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 3. Main Action Buttons Row
    c_cta1, c_cta2, c_cta3 = st.columns([1, 1, 1])
    with c_cta1:
        if st.button("Get Started", key="hero_get_started"):
            st.session_state["get_started_active"] = True
            st.rerun()
    with c_cta2:
        if not is_auth:
            if st.button(":material/person: Sign In / Create Account", key="hero_login"):
                st.session_state["auth_screen_active"] = True
                st.rerun()
        else:
            if st.button(":material/bar_chart: Access My Dashboard", key="hero_my_dashboard"):
                if not st.session_state.get("panel"):
                    st.session_state["panel"] = "citizen"
                st.session_state["onboarding_done"] = True
                st.rerun()
    with c_cta3:
        with st.popover(":material/key: Configure AI Key"):
            st.markdown("##### :material/smart_toy: Set Your Custom AI Key")
            st.caption("Provide an optional Gemini or OpenAI API key to enable dynamic natural language explanations:")
            new_key = st.text_input("API Key", value=st.session_state.get("custom_api_key", ""), type="password", key="popover_key")
            new_model = st.selectbox(
                "Model",
                ["gemini-2.5-flash", "gemini-1.5-pro", "gpt-4o-mini", "gpt-4o"],
                index=0,
                key="popover_model",
            )
            if st.button("Save Key", key="btn_save_popover_key"):
                st.session_state["custom_api_key"] = new_key.strip()
                st.session_state["custom_api_model"] = new_model
                st.success("API configuration saved for this session!")
                st.rerun()

    # 4. GET STARTED PERSONA SELECTION GATE (Shown on Get Started or after registration)
    if get_started or is_auth:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            f"""
            <div style="background:rgba(45,212,191,0.06);border:1px solid rgba(45,212,191,0.3);border-radius:20px;padding:26px;margin:20px 0;">
              <div style="text-align:center;margin-bottom:20px;">
                <span style="font-size:0.85rem;color:{CYAN};font-weight:700;letter-spacing:1.5px;text-transform:uppercase;">Entry Gateway · Get Started</span>
                <h2 style="color:#FFFFFF;margin:6px 0 10px 0;font-size:2rem;">Are you a Citizen or a Business?</h2>
                <p style="color:#94A3B8;max-width:680px;margin:0 auto;font-size:0.95rem;">
                  Select your profile track to start your tailored macroeconomic onboarding and dashboard:
                </p>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        p_col1, p_col2 = st.columns(2)

        with p_col1:
            st.markdown(
                f"""
                <div class="persona-card">
                  <div class="card-icon"><i class=ic-users></i></div>
                  <h3 style="color:#FFFFFF;margin-bottom:6px;">Citizen & Worker Hub</h3>
                  <div style="color:{CYAN};font-size:0.82rem;font-weight:600;margin-bottom:12px;">FARMERS · SALARIED · GIG WORKERS · SHOPKEEPERS</div>
                  <p style="color:#94A3B8;font-size:0.88rem;line-height:1.6;margin-bottom:16px;">
                    Understand how macroeconomic shifts directly impact your household purse:
                  </p>
                  <ul style="color:#CBD5E1;font-size:0.84rem;line-height:1.8;padding-left:18px;margin-bottom:20px;">
                    <li><strong>Crude Oil Shock:</strong> Monthly grocery & transport inflation range</li>
                    <li><strong>Agri-Climate Radar:</strong> Heatwave, rice water stress & crop diversification</li>
                    <li><strong>Repo Rate / EMI:</strong> Floating rate loan stress over 180 months</li>
                    <li><strong>Purchase Timing:</strong> Festival calendar & budget heuristic (iPhone/vehicles)</li>
                    <li><strong>Educational Capital Markets:</strong> SEBI retail loss disclosures & screening</li>
                  </ul>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("Enter as Citizen / Worker →", key="btn_choose_citizen"):
                st.session_state["panel"] = "citizen"
                st.session_state["onboarding_done"] = False
                st.session_state["get_started_active"] = False
                st.rerun()

        with p_col2:
            st.markdown(
                f"""
                <div class="persona-card">
                  <div class="card-icon"><i class=ic-building-2></i></div>
                  <h3 style="color:#FFFFFF;margin-bottom:6px;">Enterprise & Business Console</h3>
                  <div style="color:{ORANGE};font-size:0.82rem;font-weight:600;margin-bottom:12px;">MSMES · MANUFACTURING · LOGISTICS · AGRIBUSINESS</div>
                  <p style="color:#94A3B8;font-size:0.88rem;line-height:1.6;margin-bottom:16px;">
                    Institutional decision simulators for operating executives and risk officers:
                  </p>
                  <ul style="color:#CBD5E1;font-size:0.84rem;line-height:1.8;padding-left:18px;margin-bottom:20px;">
                    <li><strong>Input-Cost Shock:</strong> Multi-input margin compression & waterfall analysis</li>
                    <li><strong>Margin & Break-even:</strong> Pricing elasticity and volume-protection simulator</li>
                    <li><strong>Cash Runway:</strong> 6-month working capital stress under customer delays</li>
                    <li><strong>Logistics Corridors:</strong> Fuel cost pressure across NH-75, NH-48 & ports</li>
                    <li><strong>Aladdin-Engine:</strong> Portfolio & credit loan-book VaR / CVaR stress tests</li>
                  </ul>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("Enter as Business / MSME →", key="btn_choose_business"):
                st.session_state["panel"] = "business"
                st.session_state["onboarding_done"] = False
                st.session_state["get_started_active"] = False
                st.rerun()

    st.markdown("---")

    # 5. Institutional Architectural Pillars
    st.markdown(
        """
        <div style="text-align:center;margin:30px 0 20px 0;">
          <div style="font-size:0.8rem;color:#2DD4BF;letter-spacing:2px;font-weight:600;">RIGOROUS ECONOMICS · TRANSPARENT COMPUTATION</div>
          <h3 style="color:#FFFFFF;margin-top:4px;">Why BEIE Positions Differently</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns(4)
    pillars = [
        ("<i class=ic-link></i> Leontief Cost-Push", "15-Sector Input-Output matrix modeling indirect freight & energy pass-through.", "Exact matrix math"),
        ("<i class=ic-dices></i> Seeded Monte Carlo", "5,000–10,000 draws returning P10/P50/P90 distributions. No single fake points.", "Deterministic RNG"),
        ("<i class=ic-pin></i> Total Provenance", "Every number cites official MoSPI, PPAC, RBI or IMD sources with retrieved dates.", "Zero synthetic data"),
        ("<i class=ic-shield-check></i> Portfolio VaR/CVaR", "Aladdin-inspired multi-asset and credit stress testing with what-if removal.", "Institutional risk layer"),
    ]
    for col, (title, desc, tag) in zip([c1, c2, c3, c4], pillars):
        with col:
            st.markdown(
                f"""
                <div class="beie-card" style="height:100%;padding:20px;text-align:left;">
                  <div style="font-weight:700;color:#F8FAFC;font-size:0.98rem;margin-bottom:8px;">{title}</div>
                  <p style="color:#94A3B8;font-size:0.82rem;line-height:1.5;margin-bottom:12px;">{desc}</p>
                  <span class="source-tag">{tag}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("---")

    # 6. Honest Capabilities & Boundaries (Blueprint Section 1)
    st.markdown(
        """
        <div style="text-align:center;margin:24px 0 16px 0;">
          <h4 style="color:#FFFFFF;">System Capabilities & Operational Guardrails</h4>
        </div>
        """,
        unsafe_allow_html=True,
    )

    b_col1, b_col2 = st.columns(2)
    with b_col1:
        st.markdown(
            """
            <div class="beie-card" style="border-left:4px solid #34D399;">
              <div style="color:#34D399;font-weight:700;font-size:0.95rem;margin-bottom:10px;"><i class=ic-circle-check></i> Validated Platform Capabilities</div>
              <ul style="color:#CBD5E1;font-size:0.85rem;line-height:1.8;padding-left:16px;">
                <li>Traces global oil shocks through administered pump prices and freight to CPI groups</li>
                <li>Provides P10, P50, and P90 uncertainty bands from empirical parameter distributions</li>
                <li>Calibrated against the <strong>RBI Bulletin July 2025 anchor</strong> (+10% crude ≈ +20 bps CPI)</li>
                <li>Multilingual explanations in <strong>English, Kannada and Hindi</strong> with strict number verification</li>
                <li>Honest failure reporting: missing datasets switch to mode <code>limited</code> without fake numbers</li>
              </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with b_col2:
        st.markdown(
            """
            <div class="beie-card" style="border-left:4px solid #F87171;">
              <div style="color:#F87171;font-weight:700;font-size:0.95rem;margin-bottom:10px;"><i class=ic-octagon-x></i> Strict Regulatory & Operational Guardrails</div>
              <ul style="color:#CBD5E1;font-size:0.85rem;line-height:1.8;padding-left:16px;">
                <li><strong>No price predictions:</strong> Does not predict tomorrow's stock price or bullion rate</li>
                <li><strong>No personal investment advice:</strong> Capital market flows adhere strictly to SEBI guidelines</li>
                <li><strong>No account scraping:</strong> Never accesses bank accounts, passwords, Aadhaar or PAN</li>
                <li><strong>Non-oil inflation attribution:</strong> September 2026 vegetable inflation (7.74% food CPI) is explicitly recognized as non-oil</li>
                <li><strong>Local-only session storage:</strong> User profiles can be edited or deleted anytime with 1 click</li>
              </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # 7. Institutional Footer
    st.markdown(
        """
        <div style="text-align:center;margin-top:40px;padding:24px 0;border-top:1px solid rgba(255,255,255,0.08);font-size:0.78rem;color:#64748B;">
          <strong>Bharat Economic Intelligence Engine (BEIE v1.0.0)</strong> · Built for the Bharat Innovation Challenge 2.0 at LPU<br>
          Team: D. Manoj · Dhruva · Suresh Maladhar | Mentor: Varun Sagar D (Shikaripura, Karnataka)<br>
          Official Sources: MoSPI (Annexures I–IV) · PPAC (Ministry of Petroleum) · RBI Research Bulletins · IMD India<br>
          Data Provenance & Cryptographic Run Hashes Stored on Every Calculation
        </div>
        """,
        unsafe_allow_html=True,
    )

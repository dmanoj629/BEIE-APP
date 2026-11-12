"""BEIE — Bharat Economic Intelligence Engine
Main Streamlit Application Entrypoint.

BIC 2.0 Hackathon Prototype.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add src to python path for module imports

# Add project root and src to Python path
project_root = str(Path(__file__).resolve().parents[1])
src_path = str(Path(project_root) / "src")

if project_root not in sys.path:
    sys.path.insert(0, project_root)

if src_path not in sys.path:
    sys.path.insert(0, src_path)


import streamlit as st

from app.components.onboarding import show_business_onboarding, show_citizen_onboarding
from app.components.chat_panel import show_chat_panel
from app.state import clear_profile, init_state, logout_user
from app.theme import CUSTOM_CSS, ORANGE, CYAN, SUCCESS, asset_data_uri
from app.views.ai_settings import show_ai_settings
from app.views.auth import show_auth_screen
from app.views.business_home import show_business_home
from app.views.citizen_home import show_citizen_home
from app.views.landing import show_landing
from app.views.observed_data import show_observed_data
from app.views.problems_we_solve import show_problems_we_solve
from app.views.purchase_advisor import show_purchase_advisor
from app.views.risk_explorer import show_risk_explorer
from app.views.scenario_simulator import show_scenario_simulator
from app.views.stock_education import show_stock_education
from beie.export import generate_project_zip
from beie.i18n import t

# Streamlit Page Config
st.set_page_config(
    page_title="BEIE — Bharat Economic Intelligence Engine",
    page_icon=str(Path(__file__).resolve().parent / "assets" / "favicon.png"),
    layout="wide",
    initial_sidebar_state="expanded",
)


def main() -> None:
    init_state()
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    is_auth = st.session_state.get("is_authenticated", False)

    # 1. STRICT AUTHENTICATION GATEKEEPING:
    # "without sign or register no one should be able to use the app"
    if not is_auth or st.session_state.get("auth_screen_active", False):
        show_auth_screen()
        return

    panel = st.session_state.get("panel")
    onboarding_done = st.session_state.get("onboarding_done", False)

    # 2. Select Gateway / Persona (if not yet chosen)
    if panel is None:
        show_landing()
        return

    # 3. Onboarding Flow (if not yet completed for chosen panel)
    if not onboarding_done:
        if panel == "citizen":
            show_citizen_onboarding()
        else:
            show_business_onboarding()
        return

    # 4. Main Authenticated / Onboarded Dashboard Layout
    user_email = st.session_state.get("user_email")
    user_name = st.session_state.get("user_name", "User")
    custom_key = st.session_state.get("custom_api_key", "").strip()

    # Sidebar Navigation & Settings
    with st.sidebar:
        st.markdown(
            f"""<div class="brand" style="padding:10px 4px 16px;">
              <img src="{asset_data_uri('logo.png')}" alt="BEIE logo" />
              <div>
                <div class="brand-name">BEIE</div>
                <div class="eyebrow" style="font-size:0.62rem;letter-spacing:1.6px;margin-top:4px;">Bharat Economic Engine</div>
              </div>
            </div>""",
            unsafe_allow_html=True,
        )

        # Active User Identity Box (Named greeting, never generic)
        st.markdown(
            f"""<div style="background:rgba(15,23,42,0.85);border:1px solid rgba(45,212,191,0.2);border-radius:12px;padding:12px;margin-bottom:12px;">
              <div style="font-size:0.7rem;color:#2DD4BF;text-transform:uppercase;letter-spacing:0.8px;font-weight:600;">Active User Account</div>
              <div style="font-size:0.96rem;font-weight:700;color:#F8FAFC;margin:3px 0;"><i class=ic-user></i> {user_name}</div>
              <div style="font-size:0.74rem;color:#94A3B8;">{user_email}</div>
            </div>""",
            unsafe_allow_html=True,
        )

        user_type_str = "Citizen & Worker Portal" if panel == "citizen" else "Enterprise & Business Console"
        st.markdown(f"**Track:** `{user_type_str}`")

        nav_options = [
            ":material/home: My Dashboard",
            ":material/bolt: Universal Scenario Simulator",
            ":material/target: Problems We Solve",
            ":material/chat: AI Economic Analyst",
            ":material/shield: Portfolio Risk (Aladdin-Engine)",
            ":material/shopping_bag: Purchase Timing Advisor",
            ":material/bar_chart: Stock Risk (SEBI Education)",
            ":material/receipt_long: Data & Provenance Registry",
            ":material/settings: AI Intelligence Settings",
        ]
        page = st.radio("Navigation", nav_options, index=0)

        st.markdown("---")

        # Settings Expander: Custom Name & AI Model Configuration
        with st.expander(":material/settings: App & AI Settings", expanded=False):
            st.markdown("##### :material/person: Change Display Name")
            new_sb_name = st.text_input("Display Name:", value=user_name, key="sb_edit_name_val")
            if st.button("Update Name", key="sb_btn_update_name"):
                if new_sb_name.strip():
                    from app.state import update_user_name
                    update_user_name(new_sb_name.strip())
                    st.success("Name updated!")
                    st.rerun()

            st.markdown("---")
            st.markdown("##### :material/smart_toy: AI Model & API Key")
            st.caption("Add your Gemini or OpenAI API Key to empower the AI Chatbot with deep generative explanations:")
            side_key = st.text_input(
                "API Key (Gemini or OpenAI)",
                value=custom_key,
                type="password",
                placeholder="AIzaSy... or sk-...",
                key="sb_input_api_key",
            )
            side_model = st.selectbox(
                "Target AI Model",
                ["gemini-2.5-flash", "gemini-1.5-pro", "gpt-4o-mini", "gpt-4o"],
                index=0,
                key="sb_input_model",
            )
            if st.button("Save AI Key & Settings", key="sb_btn_save_key"):
                st.session_state["custom_api_key"] = side_key.strip()
                st.session_state["custom_api_model"] = side_model
                if side_key.strip():
                    st.success(":material/check_circle: AI Key connected & active!")
                else:
                    st.info("Using deterministic verified templates.")
                st.rerun()

            if custom_key:
                st.markdown('<div style="font-size:0.75rem;color:#34D399;margin-top:6px;">● Status: <b>Live AI Key Connected</b></div>', unsafe_allow_html=True)
            else:
                st.markdown('<div style="font-size:0.75rem;color:#94A3B8;margin-top:6px;">○ Status: <b>Verified Multilingual Templates</b></div>', unsafe_allow_html=True)

        st.markdown("---")

        # Switch Track / Reset
        c_p1, c_p2 = st.columns(2)
        with c_p1:
            if st.button(":material/sync: Switch Track", key="btn_side_switch"):
                st.session_state["panel"] = "business" if panel == "citizen" else "citizen"
                st.session_state["onboarding_done"] = False
                st.rerun()
        with c_p2:
            if st.button(":material/logout: Sign Out", key="sb_logout"):
                logout_user()
                st.rerun()

        st.markdown("---")
        st.markdown("### :material/lock: Privacy Controls")
        st.caption(
            "Your profile is stored locally in this browser session. No Aadhaar, PAN, or financial credentials collected."
        )

        c_prof1, c_prof2 = st.columns(2)
        with c_prof1:
            if st.button(":material/edit: Edit Profile", key="btn_side_edit"):
                st.session_state["onboarding_done"] = False
                st.rerun()
        with c_prof2:
            if st.button(":material/delete: Delete Profile", key="btn_side_delete"):
                clear_profile()
                st.rerun()

        st.markdown("---")
        # 1-Click Project ZIP Download Button right in the UI (Portable in-memory generation)
        st.download_button(
            label=":material/inventory_2: Download Clean Project ZIP",
            data=generate_project_zip(),
            file_name="BEIE_Bharat_Economic_Intelligence_Engine.zip",
            mime="application/zip",
            key="btn_download_clean_project_zip",
            use_container_width=True,
        )

        st.caption("BEIE Engine: `v1.0.0` · Seed `42`  \nBIC 2.0 · Viksit Bharat 2047")

    # Render selected view
    profile_data = st.session_state.get("profile", {})
    if page == ":material/home: My Dashboard":
        if panel == "citizen":
            show_citizen_home()
        else:
            show_business_home()
    elif page == ":material/bolt: Universal Scenario Simulator":
        show_scenario_simulator()
    elif page == ":material/target: Problems We Solve":
        show_problems_we_solve()
    elif page == ":material/chat: AI Economic Analyst":
        st.markdown("## :material/chat: Bharat Lens AI Economic Analyst")
        show_chat_panel(profile_data)
    elif page == ":material/shield: Portfolio Risk (Aladdin-Engine)":
        show_risk_explorer()
    elif page == ":material/shopping_bag: Purchase Timing Advisor":
        show_purchase_advisor()
    elif page == ":material/bar_chart: Stock Risk (SEBI Education)":
        show_stock_education()
    elif page == ":material/receipt_long: Data & Provenance Registry":
        show_observed_data()
    elif page == ":material/settings: AI Intelligence Settings":
        show_ai_settings()


if __name__ == "__main__":
    main()

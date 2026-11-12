"""Authentication view: Login and Register with Email and optional AI API Key."""

from __future__ import annotations

import streamlit as st
from app.state import authenticate_user
from app.theme import CUSTOM_CSS, ORANGE, SUCCESS, DANGER


def show_auth_screen() -> None:
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    # Header
    st.markdown(
        """
        <div class="hero-container" style="padding: 24px 10px 16px 10px;">
          <div class="hero-badge"><i class=ic-lock-keyhole></i> Authentication Gate</div>
          <div class="hero-title" style="font-size:2.4rem;">Bharat Economic Intelligence</div>
          <div class="hero-subtitle" style="font-size:0.95rem;max-width:600px;margin:0 auto 16px auto;">
            Please sign in or create an account with your name and email to access your personalised economic command center.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c_left, col, c_right = st.columns([1, 3, 1])

    with col:
        tab_login, tab_register, tab_api = st.tabs([":material/lock: Sign In", ":material/edit_note: Create Account", ":material/smart_toy: AI API Key (Settings)"])

        users_db = st.session_state.get("users_db", {})

        # --- TAB 1: LOGIN ---
        with tab_login:
            st.markdown("##### :material/lock: Sign in with your email")
            login_email = st.text_input("Your Email Address", placeholder="e.g. ramesh@example.com", key="auth_login_email")
            login_pwd = st.text_input("Password", type="password", key="auth_login_pwd")

            st.markdown("<br>", unsafe_allow_html=True)
            c_btn1, c_btn2 = st.columns([1, 1])
            with c_btn1:
                if st.button("Sign In →", key="btn_do_login"):
                    if not login_email or "@" not in login_email:
                        st.error("Please enter a valid email address.")
                    elif not login_pwd:
                        st.error("Please enter your password.")
                    else:
                        user_info = users_db.get(login_email.lower())
                        if user_info and user_info["password"] != login_pwd:
                            st.error("Incorrect password for this email.")
                        else:
                            name = user_info["name"] if user_info else login_email.split("@")[0].capitalize()
                            authenticate_user(login_email.lower(), name)
                            st.session_state["auth_screen_active"] = False
                            st.success(f"Welcome back, {name}!")
                            st.rerun()

            with c_btn2:
                if st.button(":material/bolt: 1-Click Demo Sign In", key="btn_quick_demo"):
                    authenticate_user("judge@bharat.gov.in", "Dr. Sharma")
                    st.session_state["auth_screen_active"] = False
                    st.rerun()

        # --- TAB 2: REGISTER ---
        with tab_register:
            st.markdown("##### :material/edit_note: Create Your Account")
            st.caption("Tell us your name so BEIE can address you personally (changeable anytime):")
            reg_name = st.text_input("Your Full Name (e.g. Ramesh Kumar, Priya Sharma):", placeholder="e.g. Ramesh Kumar", key="auth_reg_name")
            reg_email = st.text_input("Email Address:", placeholder="e.g. ramesh@gmail.com", key="auth_reg_email")
            reg_pwd = st.text_input("Create Password:", type="password", key="auth_reg_pwd")

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Register & Continue →", key="btn_do_register"):
                if not reg_name.strip():
                    st.error("Please provide your name so we know how to address you.")
                elif not reg_email or "@" not in reg_email:
                    st.error("Please enter a valid email address.")
                elif len(reg_pwd) < 3:
                    st.error("Password must be at least 3 characters.")
                else:
                    users_db[reg_email.lower()] = {
                        "name": reg_name.strip(),
                        "password": reg_pwd,
                    }
                    st.session_state["users_db"] = users_db
                    authenticate_user(reg_email.lower(), reg_name.strip())
                    st.session_state["auth_screen_active"] = False
                    st.session_state["panel"] = None
                    st.session_state["get_started_active"] = True
                    st.session_state["onboarding_done"] = False
                    st.success(f"Welcome to BEIE, {reg_name.strip()}!")
                    st.rerun()

        # --- TAB 3: AI API KEY ---
        with tab_api:
            st.markdown("##### Configure AI Model Key (Optional)")
            st.caption(
                "By default, BEIE uses high-accuracy deterministic multilingual templates. "
                "If you wish to enable live AI generated answers in conversational chat, provide your API key below:"
            )

            current_key = st.session_state.get("custom_api_key", "")
            entered_key = st.text_input(
                "Gemini / OpenAI API Key",
                value=current_key,
                type="password",
                placeholder="AIzaSy... or sk-...",
                key="auth_input_api_key",
            )
            selected_model = st.selectbox(
                "AI Model Provider",
                ["gemini-2.5-flash", "gemini-1.5-pro", "gpt-4o-mini", "gpt-4o"],
                index=0,
                key="auth_input_model",
            )

            if st.button("Save API Configuration", key="btn_save_key"):
                st.session_state["custom_api_key"] = entered_key.strip()
                st.session_state["custom_api_model"] = selected_model
                if entered_key.strip():
                    st.success(":material/check_circle: AI API Key saved to local session. Explanations will use live grounded model!")
                else:
                    st.info("AI API Key cleared. System will use deterministic verified templates.")

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("← Return to Landing Page", key="btn_back_home"):
            st.session_state["auth_screen_active"] = False
            st.session_state["get_started_active"] = False
            st.rerun()

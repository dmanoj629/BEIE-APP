"""Session state helpers for BEIE — user profile, authentication, AI keys, consent."""

from __future__ import annotations

from typing import Any
import streamlit as st


def init_state() -> None:
    defaults = {
        # App navigation & role
        "panel": None,  # "citizen" | "business"
        "onboarding_done": False,
        "get_started_active": False,
        "auth_screen_active": False,
        "auth_tab": "login",  # "login" | "register"
        # User Authentication
        "is_authenticated": False,
        "user_email": None,
        "user_name": None,
        # In-session registered users store
        "users_db": {
            "demo@bharat.gov.in": {"password": "demo", "name": "Demo Officer", "role": "citizen"},
            "msme@karnataka.org": {"password": "demo", "name": "Bengaluru MSME", "role": "business"},
        },
        # AI Engine Config
        "custom_api_key": "",
        "custom_api_model": "gemini-2.5-flash",
        # User profile & data
        "profile": {},
        "chat_history": [],  # list of {"role": "user"|"beie", "text": str}
        "last_response": None,
        "language": "en",
        "consent_given": True,
        "portfolio_holdings": [],
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def authenticate_user(email: str, name: str | None = None) -> None:
    """Mark session as authenticated."""
    st.session_state["is_authenticated"] = True
    st.session_state["user_email"] = email
    st.session_state["user_name"] = name or email.split("@")[0].capitalize()
    st.session_state["auth_screen_active"] = False


def logout_user() -> None:
    """Log out current user."""
    st.session_state["is_authenticated"] = False
    st.session_state["user_email"] = None
    st.session_state["user_name"] = None
    st.session_state["panel"] = None
    st.session_state["onboarding_done"] = False
    st.session_state["get_started_active"] = False


def save_profile(profile: dict[str, Any]) -> None:
    """Save profile to session state (local only — no server transmission)."""
    st.session_state["profile"] = profile
    st.session_state["onboarding_done"] = True


def clear_profile() -> None:
    """Delete profile — user-initiated."""
    st.session_state["profile"] = {}
    st.session_state["onboarding_done"] = False
    st.session_state["panel"] = None
    st.session_state["chat_history"] = []
    st.session_state["get_started_active"] = False


def add_chat(role: str, text: str) -> None:
    st.session_state["chat_history"].append({"role": role, "text": text})


def set_language(lang: str) -> None:
    st.session_state["language"] = lang


def update_user_name(new_name: str) -> None:
    """Update user display name in session and profile."""
    name_clean = new_name.strip()
    if name_clean:
        st.session_state["user_name"] = name_clean
        if "profile" in st.session_state and isinstance(st.session_state["profile"], dict):
            st.session_state["profile"]["name"] = name_clean

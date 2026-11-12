"""AI Intelligence Settings Page.

Dedicated configuration portal for external LLM APIs (Gemini & OpenAI)
with live credential testing, status badges, model selection, and key masking.
"""

from __future__ import annotations

import os
import streamlit as st

from app.components.cards import info_box, metric_card, warning_box
from app.theme import CUSTOM_CSS, DANGER, ORANGE, SUCCESS, WARNING
from beie.llm.adapter import mask_api_key, test_connection


def show_ai_settings() -> None:
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    st.markdown("## :material/settings: AI Intelligence Settings & API Gateway")
    st.markdown(
        '<div style="font-size:0.95rem;color:#94A3B8;margin-bottom:20px">'
        "Configure external LLM providers (Google Gemini or OpenAI) to power deep natural language economic explanations. "
        "Strict boundary guarantee: <b>Python economic engines control all calculations; AI only explains validated results.</b>"
        "</div>",
        unsafe_allow_html=True,
    )

    # Current Status Banner
    cur_provider = st.session_state.get("llm_provider", "gemini")
    cur_key = st.session_state.get("custom_api_key", "").strip() or os.environ.get("LLM_API_KEY", "")
    cur_model = st.session_state.get("custom_api_model", "gemini-2.5-flash")
    ai_enabled = st.session_state.get("ai_enabled", True)

    col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
    with col_stat1:
        stat_color = SUCCESS if (cur_key and ai_enabled) else ("#64B5F6" if not ai_enabled else ORANGE)
        stat_text = "Live AI Active" if (cur_key and ai_enabled) else ("Disabled" if not ai_enabled else "Template Fallback")
        metric_card("AI Engine Mode", stat_text, "Verification Guard Active", stat_color)
    with col_stat2:
        metric_card("Selected Provider", cur_provider.title(), f"Model: {cur_model}", "#2DD4BF")
    with col_stat3:
        key_display = mask_api_key(cur_key) if cur_key else "None (Using Templates)"
        metric_card("Key Mask", key_display, "Protected In Session", SUCCESS if cur_key else "#94A3B8")
    with col_stat4:
        conn_res = st.session_state.get("last_conn_test", None)
        if conn_res:
            c_color = SUCCESS if conn_res.get("status") == "CONNECTED" else DANGER
            metric_card("Connection Health", conn_res.get("status", "Unknown"), f"{conn_res.get('latency_ms', 0)} ms", c_color)
        else:
            metric_card("Connection Health", "Not Tested", "Click Test below", "#94A3B8")

    st.markdown("---")

    # Configuration Form
    c_left, c_right = st.columns([3, 2])

    with c_left:
        st.markdown("### :material/key: Provider & Model Credentials")

        # Provider Selector
        prov_options = ["Google Gemini", "OpenAI"]
        prov_idx = 0 if cur_provider.lower() == "gemini" else 1
        selected_prov_label = st.radio("Select AI Provider", prov_options, index=prov_idx, horizontal=True)
        selected_provider = "gemini" if "Gemini" in selected_prov_label else "openai"

        # Model Options
        if selected_provider == "gemini":
            models = ["gemini-2.5-flash", "gemini-1.5-flash", "gemini-1.5-pro"]
        else:
            models = ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"]

        cur_model_idx = 0
        if cur_model in models:
            cur_model_idx = models.index(cur_model)
        chosen_model = st.selectbox("Target Model", models, index=cur_model_idx)

        # Secure API Key Input
        api_input = st.text_input(
            "API Key",
            value=cur_key,
            type="password",
            placeholder="AIzaSy... (Gemini) or sk-... (OpenAI)",
            help="API keys are kept in your private session or server environment. Never committed to version control.",
        )

        # AI Toggle Checkbox
        enable_ai = st.checkbox("Enable AI Generative Explanations", value=ai_enabled)

        # Action Buttons
        btn_col1, btn_col2, btn_col3 = st.columns(3)
        with btn_col1:
            if st.button(":material/science: Test Connection", use_container_width=True, type="secondary"):
                if not api_input.strip():
                    st.error("Please enter an API key to test.")
                else:
                    with st.spinner(f"Pinging {selected_provider.title()}..."):
                        test_res = test_connection(selected_provider, api_input.strip(), chosen_model)
                        st.session_state["last_conn_test"] = test_res
                        if test_res["status"] == "CONNECTED":
                            st.success(f":material/check_circle: {test_res['message']}")
                        elif test_res["status"] == "INVALID_CREDENTIALS":
                            st.error(f":material/cancel: {test_res['message']}")
                        elif test_res["status"] == "RATE_LIMITED":
                            st.warning(f":material/warning: {test_res['message']}")
                        elif test_res["status"] == "NETWORK_FAILURE":
                            st.error(f":material/public: {test_res['message']}")
                        else:
                            st.error(f":material/warning: {test_res['message']}")
                        st.rerun()

        with btn_col2:
            if st.button(":material/save: Save Settings", use_container_width=True, type="primary"):
                st.session_state["llm_provider"] = selected_provider
                st.session_state["custom_api_key"] = api_input.strip()
                st.session_state["custom_api_model"] = chosen_model
                st.session_state["ai_enabled"] = enable_ai
                st.success(":material/check_circle: AI configuration updated successfully!")
                st.rerun()

        with btn_col3:
            if st.button(":material/delete: Remove Key", use_container_width=True):
                st.session_state["custom_api_key"] = ""
                st.session_state["last_conn_test"] = None
                st.info("AI key cleared. BEIE will use verified deterministic templates.")
                st.rerun()

    with c_right:
        st.markdown("### :material/shield: Non-Negotiable AI Principles")
        st.markdown(
            """
            <div style="background:rgba(15,23,42,0.8);border:1px solid rgba(45,212,191,0.25);border-radius:12px;padding:16px;">
              <div style="font-weight:700;color:#2DD4BF;margin-bottom:8px;"><i class=ic-ruler></i> How BEIE Uses AI Safely:</div>
              <ul style="font-size:0.85rem;color:#CBD5E1;line-height:1.6;margin-left:-12px;">
                <li><b>No Fabricated Numbers:</b> Python calculates the economics; the AI only interprets the verified JSON.</li>
                <li><b>Regex Number Guard:</b> Every number emitted by the model is audited. If an unauthorized number appears, the response is discarded.</li>
                <li><b>No Local LLM Required:</b> Fast cloud APIs or offline deterministic templates.</li>
                <li><b>Server-Side Environment Support:</b> Can be loaded automatically via <code>LLM_API_KEY</code>, <code>LLM_PROVIDER</code>, and <code>LLM_MODEL</code>.</li>
              </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        info_box(
            ":material/lightbulb: **Offline / No-Key Readiness:** BEIE works completely without an API key! If no key is set or when an API call fails, BEIE seamlessly falls back to its deterministic multilingual template engine in English, Kannada, and Hindi."
        )

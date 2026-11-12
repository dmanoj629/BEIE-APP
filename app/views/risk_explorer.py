"""Aladdin-inspired Portfolio & Credit Risk Explorer.

Module risk/ interactive UI:
- Input holdings (stocks or loan book by sector/district)
- Sector exposure pie
- Scenario stress using sector sensitivities
- Monte Carlo VaR & CVaR (plus historical-simulation VaR for comparison)
- Risk contribution per holding
- What-if removal
- Prominent disclaimers on VaR limits (tail risk, crisis correlations)
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from app.components.cards import metric_card, mode_badge, warning_box
from app.components.charts import bar_chart, pie_chart
from app.theme import CUSTOM_CSS, DANGER, ORANGE
from beie.risk.engine import (
    compute_portfolio_risk,
    what_if_removal,
)

DEFAULT_HOLDINGS = [
    {
        "name": "HDFC Bank / ICICI Loan Portfolio",
        "sector": "Banking & Finance",
        "value_rs": 250_000.0,
    },
    {
        "name": "Reliance / ONGC Energy Exposure",
        "sector": "Energy / Oil & Gas",
        "value_rs": 180_000.0,
    },
    {
        "name": "VRL / Container Corp Logistics",
        "sector": "Transport & Logistics",
        "value_rs": 120_000.0,
    },
    {
        "name": "Tata Chemicals / Coromandel",
        "sector": "Chemicals & Fertilizers",
        "value_rs": 90_000.0,
    },
    {
        "name": "Ultratech / ACC Cement",
        "sector": "Cement & Construction",
        "value_rs": 80_000.0,
    },
    {
        "name": "ITC / Nestle Consumer",
        "sector": "FMCG / Consumer Staples",
        "value_rs": 150_000.0,
    },
    {
        "name": "Infosys / TCS Tech Exposure",
        "sector": "IT / Technology",
        "value_rs": 130_000.0,
    },
]


def show_risk_explorer() -> None:
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    st.markdown("## :material/shield: Portfolio & Credit Risk Engine")
    st.markdown(
        '<div style="font-size:0.9rem;color:#8892B0;margin-bottom:12px">Aladdin-inspired India-specific risk analysis: sector exposure, Monte Carlo VaR/CVaR, and macro scenario stress testing.</div>',
        unsafe_allow_html=True,
    )

    mode_badge("scenario_only")
    warning_box(
        ":material/warning: **Regulatory Notice:** Scenario estimate, not a certified forecast. Standard VaR models underestimate tail risk and correlation spikes in financial crisis environments."
    )

    # Controls
    c1, c2, c3 = st.columns(3)
    with c1:
        crude_stress = st.slider("Macro Stress: Global Crude Shock (%)", 0, 80, 25, 5)
    with c2:
        confidence = st.selectbox(
            "VaR Confidence Level",
            [0.95, 0.99],
            format_func=lambda x: f"{int(x * 100)}% Confidence",
        )
    with c3:
        n_draws = st.selectbox("Simulation Iterations", [5000, 10000, 20000], index=1)

    # Holdings management table
    st.markdown("### :material/assignment: Portfolio / Loan Book Holdings")
    if "risk_holdings" not in st.session_state:
        st.session_state["risk_holdings"] = list(DEFAULT_HOLDINGS)

    holdings = st.session_state["risk_holdings"]

    # Compute baseline risk
    risk = compute_portfolio_risk(
        holdings=holdings,
        scenario_crude_delta_pct=crude_stress / 100.0,
        var_confidence=confidence,
        n_draws=n_draws,
        seed=42,
    )

    tot_val = risk["total_portfolio_value_rs"]
    stress = risk["stress_test"]
    mc_var = risk["monte_carlo_var"]
    hist_var = risk["historical_sim_var"]

    # Top KPI Metrics
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        metric_card(
            "Portfolio Value",
            f"₹{tot_val:,.0f}",
            f"{len(holdings)} holdings",
            "#64B5F6",
        )
    with m2:
        metric_card(
            f"Daily VaR ({int(confidence * 100)}%)",
            f"₹{mc_var[f'VaR_{int(confidence * 100)}pct_daily_rs']:,.0f}",
            "Monte Carlo 1-day max loss",
            ORANGE,
        )
    with m3:
        metric_card(
            "Daily CVaR (Expected Shortfall)",
            f"₹{mc_var[f'CVaR_{int(confidence * 100)}pct_daily_rs']:,.0f}",
            "Avg loss beyond VaR threshold",
            DANGER,
        )
    with m4:
        metric_card(
            f"Crude +{crude_stress}% Stress PnL",
            f"₹{stress['total_stress_pnl_rs']:,.0f}",
            f"{stress['pct_of_portfolio']:.1f}% portfolio loss",
            DANGER,
        )

    st.markdown("---")

    # Tabs for Visualizations
    t_pie, t_contrib, t_stress, t_whatif = st.tabs(
        [
            ":material/pie_chart: Sector Exposure Pie",
            ":material/bar_chart: Risk Contribution per Holding",
            ":material/bolt: Scenario Stress Breakdown",
            ":material/science: What-If Holding Removal",
        ]
    )

    with t_pie:
        pie_labels = list(risk["exposure_pie"].keys())
        pie_vals = [v["value_rs"] for v in risk["exposure_pie"].values()]
        p_fig = pie_chart(pie_labels, pie_vals, "Portfolio Sector Concentration")
        st.plotly_chart(p_fig, use_container_width=True)

    with t_contrib:
        st.markdown("**Marginal Risk Contribution (VaR Share by Position):**")
        rc_df = pd.DataFrame(risk["risk_contributions"])
        st.dataframe(rc_df, use_container_width=True, hide_index=True)

        rc_names = [r["name"] for r in risk["risk_contributions"]]
        rc_vals = [r["risk_contribution_rs"] for r in risk["risk_contributions"]]
        b_fig = bar_chart(
            rc_names, rc_vals, "Holding VaR Contribution (₹)", "Risk Contribution (₹)"
        )
        st.plotly_chart(b_fig, use_container_width=True)

    with t_stress:
        st.markdown(
            f"**Impact of +{crude_stress}% Crude Spike on Individual Holdings:**"
        )
        stress_df = pd.DataFrame(stress["per_holding"])
        st.dataframe(stress_df, use_container_width=True, hide_index=True)

    with t_whatif:
        st.markdown("**Test removing a holding to observe diversification impact:**")
        holding_names = [h["name"] for h in holdings]
        rem_choice = st.selectbox(
            "Select holding to remove temporarily:", holding_names
        )
        if st.button("Simulate Removal", key="btn_whatif"):
            wi = what_if_removal(
                holdings,
                rem_choice,
                scenario_crude_delta_pct=crude_stress / 100.0,
                var_confidence=confidence,
                n_draws=n_draws,
                seed=42,
            )
            orig_var = mc_var[f"VaR_{int(confidence * 100)}pct_daily_rs"]
            new_var = wi["monte_carlo_var"][f"VaR_{int(confidence * 100)}pct_daily_rs"]
            delta_var = new_var - orig_var

            st.info(
                f"**What-If Result for Removing '{rem_choice}':**  \n"
                f"- New Portfolio Value: **₹{wi['total_portfolio_value_rs']:,.0f}**  \n"
                f"- New Daily VaR: **₹{new_var:,.0f}** ({delta_var:+,.0f} change)  \n"
                f"- New Stress PnL under Crude Shock: **₹{wi['stress_test']['total_stress_pnl_rs']:,.0f}**"
            )

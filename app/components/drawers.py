"""'Why this result?' drawer component.

Mandated by Blueprint:
Exposes method, version, seed, run ID, sources, assumptions, and downloadable run record.
"""

from __future__ import annotations

import json

import streamlit as st

from beie.contracts import DecisionResponse


def show_why_drawer(resp: DecisionResponse) -> None:
    """Renders the transparent auditable 'Why this result?' accordion."""
    with st.expander(
        ":material/search: Why this result? (Methodology, Sources & Run Audit)", expanded=False
    ):
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f"**Mode:** `{resp.mode.value}`")
        with c2:
            st.markdown(f"**Model Version:** `{resp.model_version}`")
        with c3:
            run_id = (
                resp.run_record.get("run_id", resp.request_id)
                if resp.run_record
                else resp.request_id
            )
            st.markdown(f"**Run ID:** `{run_id}`")
        with c4:
            seed = resp.run_record.get("seed", "N/A") if resp.run_record else "N/A"
            st.markdown(f"**RNG Seed:** `{seed}`")

        st.markdown("---")
        t1, t2, t3, t4 = st.tabs(
            [
                ":material/menu_book: Evidence & Citations",
                ":material/settings: Assumptions",
                ":material/warning: Risks & Caveats",
                ":material/download: Audit Record",
            ]
        )

        with t1:
            if resp.evidence:
                for ev in resp.evidence:
                    st.markdown(
                        f"- **[{ev.source_name}]({ev.source_url})**: {ev.description}  \n"
                        f"  *License / Terms:* `{ev.licence_or_terms}` | *Retrieved:* `{ev.retrieved_at}`"
                    )
            else:
                st.caption(
                    "No external formal evidence citations attached to this run."
                )

            if resp.observations:
                st.markdown("**Sourced Historical Baseline Facts:**")
                for obs in resp.observations:
                    st.markdown(
                        f"- `{obs.indicator}`: **{obs.value} {obs.unit}** ({obs.location}, {obs.observed_at})  \n"
                        f"  *Source:* [{obs.source_name}]({obs.source_url}) | *Quality:* `{obs.quality_status}`"
                    )

        with t2:
            if resp.assumptions:
                for asm in resp.assumptions:
                    st.markdown(f"- :material/push_pin: {asm}")
            else:
                st.caption("No assumptions recorded.")

        with t3:
            if resp.risks:
                for rsk in resp.risks:
                    st.markdown(f"- :material/warning: {rsk}")
            if resp.limitations:
                st.markdown("**System Boundaries & Limitations:**")
                for lim in resp.limitations:
                    st.markdown(f"- :material/block: {lim}")

        with t4:
            resp_dict = resp.model_dump()
            st.json(resp_dict, expanded=False)
            st.download_button(
                label=":material/arrow_downward: Download Auditable Run Record (JSON)",
                data=json.dumps(resp_dict, indent=2, default=str),
                file_name=f"beie_run_{resp.request_id}.json",
                mime="application/json",
                key=f"dl_run_{resp.request_id}",
            )

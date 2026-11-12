"""Reusable UI cards, badges and metric components."""

from __future__ import annotations

import streamlit as st

from app.theme import MODE_COLORS, MODE_LABELS


def mode_badge(mode: str) -> None:
    color = MODE_COLORS.get(mode, "#8892B0")
    label = MODE_LABELS.get(mode, mode)
    st.markdown(
        f'<span class="mode-badge" style="background:{color}22;color:{color};border:1px solid {color}">{label}</span>',
        unsafe_allow_html=True,
    )


def metric_card(
    label: str, value: str, delta: str = "", color: str = "#F97316"
) -> None:
    delta_html = (
        f'<div style="font-size:0.8rem;color:#8892B0;margin-top:4px">{delta}</div>'
        if delta
        else ""
    )
    st.markdown(
        f"""<div class="beie-card" style="text-align:center;">
          <div style="font-size:0.8rem;color:#8892B0;text-transform:uppercase;letter-spacing:1px">{label}</div>
          <div style="font-size:1.9rem;font-weight:700;color:{color};margin:6px 0">{value}</div>
          {delta_html}
        </div>""",
        unsafe_allow_html=True,
    )


def source_tag(source_name: str, url: str = "", retrieved_at: str = "") -> None:
    link = (
        f'<a href="{url}" target="_blank" style="color:#64B5F6">{source_name}</a>'
        if url
        else source_name
    )
    ts = f" · {retrieved_at}" if retrieved_at else ""
    st.markdown(
        f'<span class="source-tag"><i class=ic-pin></i> Source: {link}{ts}</span>',
        unsafe_allow_html=True,
    )


def run_id_tag(run_id: str, seed: int = 0, draws: int = 0) -> None:
    st.markdown(
        f'<span class="source-tag"><i class=ic-key-round></i> Run ID: <code>{run_id}</code> · seed={seed} · draws={draws:,}</span>',
        unsafe_allow_html=True,
    )


def warning_box(text: str) -> None:
    st.markdown(f'<div class="beie-warning"><i class=ic-triangle-alert></i> {text}</div>', unsafe_allow_html=True)


def info_box(text: str) -> None:
    st.markdown(f'<div class="beie-info"><i class=ic-info></i> {text}</div>', unsafe_allow_html=True)


def section_header(title: str, icon: str = "") -> None:
    st.markdown(
        f'<h3 style="color:#F97316;border-bottom:1px solid rgba(249,115,22,0.3);padding-bottom:8px;margin-top:24px">{icon} {title}</h3>',
        unsafe_allow_html=True,
    )

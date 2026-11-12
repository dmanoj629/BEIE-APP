"""Reusable Plotly chart components for BEIE.

All figures share one visual language: transparent canvas, Inter typography,
soft gradients, rounded marks, and tooltips styled to match the app cards.
"""

from __future__ import annotations

import numpy as np
import plotly.graph_objects as go

NAVY = "#070B14"
CARD = "#0E1626"
ORANGE = "#F97316"
AMBER = "#F59E0B"
CYAN = "#2DD4BF"
LIGHT_BLUE = "#60A5FA"
SUCCESS = "#34D399"
DANGER = "#F87171"
VIOLET = "#A78BFA"
TEXT = "#E8EDF5"
MUTED = "#94A3B8"
GRID = "rgba(148,163,184,0.10)"
AXIS_LINE = "rgba(148,163,184,0.25)"
BG = "rgba(0,0,0,0)"

FONT_BODY = "Inter, 'Segoe UI', system-ui, sans-serif"
FONT_MONO = "'JetBrains Mono', ui-monospace, monospace"

PALETTE = [ORANGE, CYAN, LIGHT_BLUE, AMBER, VIOLET, SUCCESS, "#F472B6", "#94A3B8"]


def _rgba(hex_color: str, alpha: float) -> str:
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i : i + 2], 16) for i in (0, 2, 4))
    return f"rgba({r},{g},{b},{alpha})"


def _base_layout(
    title: str,
    height: int,
    *,
    x_title: str = "",
    y_title: str = "",
    margin: dict | None = None,
    legend: bool = True,
) -> dict:
    return dict(
        title=dict(
            text=f"<b>{title}</b>",
            font=dict(size=15, color=TEXT, family=FONT_BODY),
            x=0.01,
            xanchor="left",
            y=0.97,
            yanchor="top",
        ),
        paper_bgcolor=BG,
        plot_bgcolor=BG,
        font=dict(color=MUTED, family=FONT_BODY, size=12),
        colorway=PALETTE,
        height=height,
        margin=margin or dict(l=56, r=24, t=64, b=48),
        showlegend=legend,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.0,
            xanchor="right",
            x=1.0,
            bgcolor=BG,
            font=dict(size=11, color=MUTED),
            itemsizing="constant",
        ),
        hoverlabel=dict(
            bgcolor=CARD,
            bordercolor=_rgba(ORANGE, 0.55),
            font=dict(family=FONT_BODY, size=12, color=TEXT),
        ),
        hovermode="x unified",
        transition=dict(duration=500, easing="cubic-in-out"),
        xaxis=dict(
            title=dict(text=x_title, font=dict(size=11, color=MUTED)),
            showgrid=False,
            linecolor=AXIS_LINE,
            tickfont=dict(size=11, color=MUTED),
            zeroline=False,
            ticks="outside",
            tickcolor=AXIS_LINE,
        ),
        yaxis=dict(
            title=dict(text=y_title, font=dict(size=11, color=MUTED)),
            gridcolor=GRID,
            griddash="dot",
            zeroline=True,
            zerolinecolor="rgba(148,163,184,0.35)",
            zerolinewidth=1,
            tickfont=dict(size=11, color=MUTED),
            showline=False,
        ),
    )


def fan_chart(
    months: list[int],
    p10: list[float],
    p50: list[float],
    p90: list[float],
    title: str,
    y_label: str = "CPI Impact (pp)",
    unit: str = "pp",
) -> go.Figure:
    """P10/P50/P90 fan chart with a shaded uncertainty band."""
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=months,
            y=p90,
            mode="lines",
            line=dict(color=_rgba(AMBER, 0.55), width=1.2, dash="dot", shape="spline"),
            name="P90 (High)",
            hovertemplate=f"%{{y:.3f}} {unit}<extra>P90 High</extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=months,
            y=p10,
            mode="lines",
            line=dict(color=_rgba(CYAN, 0.55), width=1.2, dash="dot", shape="spline"),
            fill="tonexty",
            fillcolor=_rgba(ORANGE, 0.14),
            name="P10 (Low)",
            hovertemplate=f"%{{y:.3f}} {unit}<extra>P10 Low</extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=months,
            y=p50,
            mode="lines+markers",
            line=dict(color=ORANGE, width=3.2, shape="spline", smoothing=0.8),
            marker=dict(
                size=8,
                color=NAVY,
                line=dict(color=ORANGE, width=2.2),
            ),
            name="P50 (Median)",
            hovertemplate=f"<b>%{{y:.3f}} {unit}</b><extra>P50 Median</extra>",
        )
    )

    layout = _base_layout(title, 390, x_title="Month", y_title=y_label)
    fig.update_layout(**layout)
    fig.update_xaxes(dtick=max(1, len(months) // 8))
    return fig


def histogram_chart(
    draws: np.ndarray, p10: float, p50: float, p90: float, title: str, x_label: str
) -> go.Figure:
    """Monte Carlo draw histogram with P10/P50/P90 markers."""
    draws = np.asarray(draws)
    fig = go.Figure()
    fig.add_trace(
        go.Histogram(
            x=draws,
            nbinsx=48,
            marker=dict(
                color=_rgba(ORANGE, 0.78),
                line=dict(color=NAVY, width=1.2),
                cornerradius=4,
            ),
            hovertemplate="Range %{x}<br>%{y} simulations<extra></extra>",
            name="Simulated outcomes",
        )
    )

    # P10-P90 confidence window
    fig.add_vrect(
        x0=p10,
        x1=p90,
        fillcolor=_rgba(CYAN, 0.07),
        line_width=0,
        layer="below",
    )
    markers = [
        (p10, "P10", CYAN, "top left"),
        (p50, "Median", SUCCESS, "top"),
        (p90, "P90", AMBER, "top right"),
    ]
    for val, name, color, pos in markers:
        fig.add_vline(
            x=val,
            line=dict(color=color, width=2, dash="dash"),
            annotation=dict(
                text=f"<b>{name}</b> {val:.3f}",
                font=dict(color=color, size=11, family=FONT_MONO),
                bgcolor=_rgba(CARD, 0.9),
                bordercolor=_rgba(color, 0.6),
                borderpad=4,
                yanchor="bottom",
            ),
            annotation_position=pos,
        )

    layout = _base_layout(
        title,
        340,
        x_title=x_label,
        y_title="Simulations",
        legend=False,
        margin=dict(l=56, r=24, t=76, b=48),
    )
    layout["hovermode"] = "closest"
    fig.update_layout(**layout, bargap=0.06)
    return fig


def waterfall_chart(
    categories: list[str], values: list[float], title: str
) -> go.Figure:
    """Waterfall / contribution chart for transmission chains."""
    fig = go.Figure(
        go.Waterfall(
            x=categories,
            y=values,
            measure=["relative"] * len(values),
            text=[f"{v:+.3f}" for v in values],
            textposition="outside",
            textfont=dict(color=TEXT, size=11, family=FONT_MONO),
            connector=dict(line=dict(color="rgba(148,163,184,0.35)", width=1, dash="dot")),
            increasing=dict(marker=dict(color=ORANGE, line=dict(color=NAVY, width=1.5))),
            decreasing=dict(marker=dict(color=CYAN, line=dict(color=NAVY, width=1.5))),
            totals=dict(marker=dict(color=SUCCESS)),
            hovertemplate="<b>%{x}</b><br>%{y:+.3f}<extra></extra>",
        )
    )
    layout = _base_layout(
        title,
        390,
        legend=False,
        margin=dict(l=56, r=24, t=64, b=88),
    )
    layout["hovermode"] = "closest"
    fig.update_layout(**layout, waterfallgap=0.35)
    fig.update_xaxes(tickangle=-20)
    return fig


def pie_chart(labels: list[str], values: list[float], title: str) -> go.Figure:
    """Sector exposure / budget allocation donut chart."""
    total = float(sum(values)) if values else 0.0
    fig = go.Figure(
        go.Pie(
            labels=labels,
            values=values,
            hole=0.62,
            sort=False,
            direction="clockwise",
            textinfo="percent",
            textposition="outside",
            textfont=dict(size=12, color=TEXT, family=FONT_BODY),
            pull=[0.025] * len(labels),
            hovertemplate="<b>%{label}</b><br>%{value:,.0f}<br>%{percent}<extra></extra>",
            marker=dict(
                colors=[PALETTE[i % len(PALETTE)] for i in range(len(labels))],
                line=dict(color=NAVY, width=3),
            ),
        )
    )
    layout = _base_layout(
        title,
        380,
        margin=dict(l=16, r=16, t=64, b=24),
    )
    layout["hovermode"] = "closest"
    layout["legend"] = dict(
        orientation="v",
        yanchor="middle",
        y=0.5,
        xanchor="left",
        x=1.02,
        bgcolor=BG,
        font=dict(size=11, color=MUTED),
    )
    fig.update_layout(**layout)
    fig.add_annotation(
        text=f"<span style='font-size:11px;color:{MUTED}'>TOTAL</span><br>"
        f"<b style='font-size:20px;color:{TEXT}'>{total:,.0f}</b>",
        x=0.5,
        y=0.5,
        xref="paper",
        yref="paper",
        showarrow=False,
        font=dict(family=FONT_BODY),
        align="center",
    )
    return fig


def bar_chart(
    x: list[str], y: list[float], title: str, y_label: str = "", color: str = ORANGE
) -> go.Figure:
    """Rounded bar chart; positive values use `color`, negative use cyan."""
    y = list(y)
    bar_colors = [color if v >= 0 else CYAN for v in y]
    fig = go.Figure(
        go.Bar(
            x=x,
            y=y,
            marker=dict(
                color=[_rgba(c, 0.9) for c in bar_colors],
                line=dict(color=bar_colors, width=1.2),
                cornerradius=8,
            ),
            text=[f"{v:+.2f}" if min(y, default=0) < 0 else f"{v:.2f}" for v in y],
            textposition="outside",
            textfont=dict(size=11, color=TEXT, family=FONT_MONO),
            cliponaxis=False,
            hovertemplate="<b>%{x}</b><br>%{y:.2f}<extra></extra>",
        )
    )
    layout = _base_layout(
        title,
        350,
        y_title=y_label,
        legend=False,
        margin=dict(l=56, r=24, t=64, b=88),
    )
    layout["hovermode"] = "closest"
    fig.update_layout(**layout, bargap=0.38)
    fig.update_xaxes(tickangle=-25)
    return fig


def transmission_chain_chart(chain: list[dict]) -> go.Figure:
    """Horizontal stepwise transmission chain visualization."""
    nodes = [c["node"] for c in chain]
    changes = [c["change"] for c in chain]
    steps = list(range(len(chain)))
    type_colors = {
        "shock": DANGER,
        "output": SUCCESS,
        "pump": ORANGE,
    }
    colors = [type_colors.get(c.get("type", "derived"), LIGHT_BLUE) for c in chain]

    fig = go.Figure()
    # Connecting rail
    fig.add_trace(
        go.Scatter(
            x=steps,
            y=[0] * len(steps),
            mode="lines",
            line=dict(color="rgba(148,163,184,0.35)", width=3),
            hoverinfo="skip",
            showlegend=False,
        )
    )
    # Soft halo behind each node
    fig.add_trace(
        go.Scatter(
            x=steps,
            y=[0] * len(steps),
            mode="markers",
            marker=dict(size=40, color=[_rgba(c, 0.18) for c in colors]),
            hoverinfo="skip",
            showlegend=False,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=steps,
            y=[0] * len(steps),
            mode="markers+text",
            marker=dict(size=22, color=colors, line=dict(color=NAVY, width=3)),
            text=[f"<b>{c['step']}</b>" for c in chain],
            textposition="middle center",
            textfont=dict(size=11, color=NAVY, family=FONT_BODY),
            customdata=list(zip(nodes, changes)),
            hovertemplate="<b>%{customdata[0]}</b><br>%{customdata[1]}<extra></extra>",
            showlegend=False,
        )
    )
    for i, (node, change) in enumerate(zip(nodes, changes)):
        fig.add_annotation(
            x=i,
            y=-0.38,
            text=(
                f"<b>{node[:28]}</b><br>"
                f"<span style='color:{colors[i]}'>{change[:36]}</span>"
            ),
            showarrow=False,
            font=dict(size=10, color=TEXT, family=FONT_BODY),
            align="center",
            yanchor="top",
        )

    layout = _base_layout(
        "Economic Transmission Chain",
        300,
        legend=False,
        margin=dict(l=20, r=20, t=60, b=20),
    )
    layout["hovermode"] = "closest"
    layout["xaxis"] = dict(visible=False, range=[-0.6, len(chain) - 0.4])
    layout["yaxis"] = dict(range=[-1.5, 0.7], visible=False)
    fig.update_layout(**layout)
    return fig

"""Theme, palette and institutional CSS for BEIE Streamlit app."""

from __future__ import annotations

import base64
import re
from functools import lru_cache
from pathlib import Path

from app.icons import icon_css

ASSETS = Path(__file__).resolve().parent / "assets"

NAVY = "#070B14"
CARD_BG = "#0E1626"
BORDER = "rgba(148, 163, 184, 0.16)"
ORANGE = "#F97316"
AMBER = "#F59E0B"
WARNING = "#F59E0B"
CYAN = "#2DD4BF"
SUCCESS = "#34D399"
DANGER = "#F87171"
TEXT_LIGHT = "#E8EDF5"
TEXT_MUTED = "#94A3B8"
LIGHT_NAVY = "#0E1626"
LIGHT_BG = "#F8F9FA"
DARK_BG = "#070B14"

MODE_COLORS = {
    "data_driven": SUCCESS,
    "scenario_only": ORANGE,
    "demo": CYAN,
    "limited": DANGER,
}

MODE_LABELS = {
    "data_driven": "<i class=ic-circle-check></i> Data Driven",
    "scenario_only": "<i class=ic-circle-dot></i> Scenario Only",
    "demo": "<i class=ic-graduation-cap></i> Educational Demo",
    "limited": "<i class=ic-triangle-alert></i> Limited",
}


@lru_cache(maxsize=None)
def asset_data_uri(filename: str) -> str:
    """Embed a bundled image as a data URI so it works inside raw HTML blocks."""
    path = ASSETS / filename
    mime = "image/jpeg" if path.suffix == ".jpg" else "image/png"
    return f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode()}"


@lru_cache(maxsize=1)
def _used_icons() -> frozenset[str]:
    names: set[str] = {"circle-check", "triangle-alert", "info", "circle-x", "arrow-right"}
    for py in Path(__file__).resolve().parent.rglob("*.py"):
        names.update(re.findall(r"ic-([a-z0-9-]+)", py.read_text(encoding="utf8")))
    return frozenset(names)


_BODY_CSS = f"""
  @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

  :root {{
    --ink: {NAVY};
    --surface: {CARD_BG};
    --surface-2: #131E33;
    --line: {BORDER};
    --accent: {ORANGE};
    --accent-2: {CYAN};
    --success: {SUCCESS};
    --danger: {DANGER};
    --text: {TEXT_LIGHT};
    --muted: {TEXT_MUTED};
    --ease: cubic-bezier(.22,.8,.26,1);
    --font-display: 'Fraunces', Georgia, serif;
    --font-body: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    --font-mono: 'JetBrains Mono', ui-monospace, monospace;
  }}

  html, body, [class*="css"], .stApp, button, input, textarea, select {{
    font-family: var(--font-body);
    -webkit-font-smoothing: antialiased;
  }}
  .material-symbols-rounded, [data-testid="stIconMaterial"] {{ font-family: 'Material Symbols Rounded' !important; }}

  h1, h2, h3, .hero-title, .display {{
    font-family: var(--font-display) !important;
    font-weight: 600 !important;
    letter-spacing: -0.015em !important;
    color: #F4F7FB;
  }}
  h4, h5, h6 {{ font-family: var(--font-body) !important; font-weight: 600 !important; letter-spacing: -0.005em; }}
  code, pre, kbd, .mono {{ font-family: var(--font-mono) !important; }}

  .stApp {{
    background:
      radial-gradient(900px 480px at 85% -10%, rgba(249,115,22,0.10), transparent 60%),
      radial-gradient(800px 520px at 5% 0%, rgba(45,212,191,0.09), transparent 60%),
      var(--ink);
    color: var(--text);
  }}
  header[data-testid="stHeader"] {{ background: transparent; }}
  [data-testid="stMainBlockContainer"] {{
    padding-top: 2.2rem; max-width: 1240px;
    animation: pageIn .55s var(--ease) both;
  }}
  hr {{ border: none !important; height: 1px; background: linear-gradient(90deg, transparent, var(--line), transparent) !important; margin: 1.6rem 0 !important; }}

  /* Icons */
  .stApp [class^="ic-"], .stApp [class*=" ic-"] {{ margin-right: .15em; }}

  /* Motion */
  @keyframes pageIn {{ from {{ opacity: 0; transform: translateY(14px); }} to {{ opacity: 1; transform: none; }} }}
  @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: none; }} }}
  @keyframes shimmer {{ from {{ background-position: 0% 50%; }} to {{ background-position: 200% 50%; }} }}
  @keyframes livePulse {{ 0% {{ box-shadow: 0 0 0 0 rgba(52,211,153,.55); }} 70% {{ box-shadow: 0 0 0 8px rgba(52,211,153,0); }} 100% {{ box-shadow: 0 0 0 0 rgba(52,211,153,0); }} }}
  @keyframes floatY {{ 0%,100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-4px); }} }}
  .beie-card, .persona-card, .ticker-wrap, .stat-tile {{ animation: fadeIn .55s var(--ease) both; }}
  [data-testid="stHorizontalBlock"] > div:nth-child(2) .beie-card {{ animation-delay: .06s; }}
  [data-testid="stHorizontalBlock"] > div:nth-child(3) .beie-card {{ animation-delay: .12s; }}
  [data-testid="stHorizontalBlock"] > div:nth-child(4) .beie-card {{ animation-delay: .18s; }}

  /* Ticker */
  .ticker-wrap {{
    background: rgba(14,22,38,.85); backdrop-filter: blur(10px);
    border: 1px solid var(--line); padding: 10px 18px; font-size: .8rem;
    display: flex; justify-content: space-between; align-items: center; gap: 16px;
    border-radius: 12px; margin-bottom: 18px;
  }}
  .ticker-wrap::before {{
    content: ""; width: 8px; height: 8px; border-radius: 50%; background: var(--success);
    animation: livePulse 2s infinite; flex: none;
  }}
  .ticker-item {{ display: inline-flex; align-items: center; gap: 6px; margin-right: 18px; color: var(--muted); white-space: nowrap; }}
  .ticker-val {{ font-family: var(--font-mono); font-weight: 600; color: #F4F7FB; }}

  /* Cards */
  .beie-card {{
    position: relative;
    background: linear-gradient(160deg, rgba(19,30,51,.92) 0%, rgba(11,18,32,.96) 100%);
    border: 1px solid var(--line); border-radius: 16px; padding: 24px; margin: 12px 0;
    box-shadow: 0 1px 0 rgba(255,255,255,.04) inset, 0 18px 40px -22px rgba(0,0,0,.7);
    transition: transform .3s var(--ease), border-color .3s ease, box-shadow .3s ease;
  }}
  .beie-card:hover {{
    transform: translateY(-3px); border-color: rgba(249,115,22,.4);
    box-shadow: 0 1px 0 rgba(255,255,255,.05) inset, 0 24px 44px -22px rgba(249,115,22,.28);
  }}
  .card-icon {{
    display: inline-flex; align-items: center; justify-content: center; width: 40px; height: 40px;
    border-radius: 11px; margin-bottom: 14px; color: var(--accent-2);
    background: rgba(45,212,191,.1); border: 1px solid rgba(45,212,191,.28);
  }}
  .card-icon [class^="ic-"] {{ width: 20px; height: 20px; margin: 0; }}

  /* Hero */
  .hero-container {{
    position: relative; text-align: center; padding: 64px 24px 56px; border-radius: 22px; overflow: hidden;
    border: 1px solid var(--line); margin-bottom: 18px;
    background-size: cover; background-position: center;
    box-shadow: 0 30px 60px -30px rgba(0,0,0,.8);
  }}
  .hero-container > * {{ position: relative; z-index: 1; }}
  .hero-badge {{
    display: inline-flex; align-items: center; gap: 8px; padding: 7px 16px; margin-bottom: 20px;
    background: rgba(45,212,191,.08); border: 1px solid rgba(45,212,191,.35); border-radius: 999px;
    color: var(--accent-2); font-size: .72rem; font-weight: 600; letter-spacing: 1.6px; text-transform: uppercase;
    backdrop-filter: blur(6px);
  }}
  .hero-title {{
    font-size: 3.4rem; line-height: 1.1; margin: 0 auto 16px; max-width: 900px;
    background: linear-gradient(100deg, #FFFFFF 10%, #FDE7CF 45%, {ORANGE} 75%, #FFFFFF 100%);
    background-size: 200% auto; -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent;
    animation: shimmer 9s linear infinite;
  }}
  .hero-subtitle {{ font-size: 1.1rem; color: #B6C2D4; max-width: 780px; margin: 0 auto 8px; line-height: 1.7; }}
  .hero-subtitle strong {{ color: #F4F7FB; font-weight: 600; }}

  .brand {{ display: flex; align-items: center; gap: 12px; }}
  .brand img {{ width: 42px; height: 42px; border-radius: 11px; box-shadow: 0 6px 18px -6px rgba(249,115,22,.6); transition: transform .4s var(--ease); }}
  .brand:hover img {{ transform: rotate(-6deg) scale(1.06); }}
  .brand-name {{ font-family: var(--font-display); font-size: 1.6rem; font-weight: 700; color: #F4F7FB; letter-spacing: -.02em; line-height: 1; }}
  .brand-sub {{ color: var(--muted); font-size: .8rem; border-left: 1px solid var(--line); padding-left: 12px; }}
  .eyebrow {{ font-size: .72rem; color: var(--accent-2); letter-spacing: 2px; font-weight: 600; text-transform: uppercase; }}

  .mode-badge {{
    display: inline-flex; align-items: center; gap: 6px; padding: 4px 12px; border-radius: 999px;
    font-size: .74rem; font-weight: 600; letter-spacing: .4px; margin-bottom: 8px; font-family: var(--font-mono);
  }}

  .persona-card {{
    background: linear-gradient(160deg, rgba(19,30,51,.9), rgba(10,17,30,.96));
    border: 1px solid var(--line); border-radius: 18px; padding: 28px; text-align: left; height: 100%;
    transition: transform .3s var(--ease), border-color .3s ease, box-shadow .3s ease;
  }}
  .persona-card:hover {{ transform: translateY(-5px); border-color: var(--accent); box-shadow: 0 26px 50px -24px rgba(249,115,22,.35); }}
  .persona-card .card-icon {{ animation: floatY 5s ease-in-out infinite; }}

  /* Metrics */
  div[data-testid="stMetric"] {{
    background: rgba(19,30,51,.6); border: 1px solid var(--line); border-radius: 14px; padding: 14px 18px;
    transition: border-color .3s ease, transform .3s var(--ease);
  }}
  div[data-testid="stMetric"]:hover {{ border-color: rgba(249,115,22,.4); transform: translateY(-2px); }}
  div[data-testid="stMetricValue"] {{ color: #F4F7FB !important; font-size: 1.8rem !important; font-weight: 600 !important; font-family: var(--font-mono) !important; }}
  div[data-testid="stMetricLabel"] {{ color: var(--muted) !important; font-size: .74rem !important; text-transform: uppercase; letter-spacing: .9px; }}

  /* Buttons */
  .stButton > button, .stDownloadButton > button, [data-testid="stPopover"] > div > button, .stFormSubmitButton > button {{
    position: relative; overflow: hidden;
    background: linear-gradient(135deg, #FB923C 0%, {ORANGE} 55%, #EA580C 100%);
    color: #0B0F1A !important; border: 0 !important; border-radius: 12px !important;
    padding: 10px 22px !important; font-weight: 600 !important; font-size: .92rem !important; letter-spacing: .01em;
    min-height: 44px !important; box-shadow: 0 10px 24px -10px rgba(249,115,22,.65) !important;
    transition: transform .25s var(--ease), box-shadow .25s ease, filter .25s ease !important;
  }}
  .stButton > button p, .stDownloadButton > button p {{ color: #0B0F1A !important; font-weight: 600; }}
  .stButton > button::after, .stDownloadButton > button::after {{
    content: ""; position: absolute; inset: 0; transform: translateX(-120%);
    background: linear-gradient(105deg, transparent 30%, rgba(255,255,255,.35) 50%, transparent 70%);
    transition: transform .7s var(--ease); pointer-events: none;
  }}
  .stButton > button:hover::after, .stDownloadButton > button:hover::after {{ transform: translateX(120%); }}
  .stButton > button:hover, .stDownloadButton > button:hover, [data-testid="stPopover"] > div > button:hover {{
    transform: translateY(-2px); filter: brightness(1.06); box-shadow: 0 16px 30px -10px rgba(249,115,22,.75) !important;
  }}
  .stButton > button:active, .stDownloadButton > button:active {{ transform: translateY(1px) scale(.99); }}
  .stButton > button:focus-visible, .stDownloadButton > button:focus-visible {{ outline: 2px solid var(--accent-2) !important; outline-offset: 3px; }}

  /* Sidebar */
  [data-testid="stSidebar"] {{
    background: linear-gradient(180deg, #0A111F 0%, #070B14 100%) !important;
    border-right: 1px solid var(--line) !important;
  }}
  [data-testid="stSidebar"] .stButton > button, [data-testid="stSidebar"] .stDownloadButton > button {{
    background: rgba(19,30,51,.8); color: var(--text) !important; border: 1px solid var(--line) !important;
    box-shadow: none !important; min-height: 38px !important; font-size: .82rem !important; padding: 6px 12px !important;
  }}
  [data-testid="stSidebar"] .stButton > button p, [data-testid="stSidebar"] .stDownloadButton > button p {{ color: var(--text) !important; }}
  [data-testid="stSidebar"] .stButton > button:hover, [data-testid="stSidebar"] .stDownloadButton > button:hover {{
    border-color: var(--accent) !important; color: #fff !important; box-shadow: 0 8px 20px -12px rgba(249,115,22,.7) !important;
  }}
  [data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] {{ gap: 4px; }}
  [data-testid="stSidebar"] [data-testid="stRadio"] label {{
    padding: 9px 12px; border-radius: 10px; border: 1px solid transparent; width: 100%;
    transition: background .25s ease, border-color .25s ease, transform .25s var(--ease);
  }}
  [data-testid="stSidebar"] [data-testid="stRadio"] label:hover {{ background: rgba(255,255,255,.04); transform: translateX(3px); }}
  [data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {{
    background: linear-gradient(90deg, rgba(249,115,22,.16), rgba(249,115,22,.03));
    border-color: rgba(249,115,22,.35);
  }}
  [data-testid="stSidebar"] [data-testid="stRadio"] label > div:first-child {{ display: none; }}

  /* Inputs */
  .stTextInput input, .stNumberInput input, .stTextArea textarea, [data-baseweb="select"] > div {{
    background: rgba(14,22,38,.9) !important; color: var(--text) !important;
    border: 1px solid var(--line) !important; border-radius: 10px !important;
    transition: border-color .25s ease, box-shadow .25s ease !important;
  }}
  .stTextInput input:focus, .stNumberInput input:focus, .stTextArea textarea:focus {{
    border-color: var(--accent) !important; box-shadow: 0 0 0 3px rgba(249,115,22,.18) !important;
  }}

  /* Tabs */
  [data-testid="stTabs"] [role="tablist"] {{ gap: 6px; border-bottom: 1px solid var(--line); }}
  [data-testid="stTabs"] button[role="tab"] {{
    border-radius: 10px 10px 0 0; padding: 10px 16px; color: var(--muted); font-weight: 500;
    transition: color .25s ease, background .25s ease;
  }}
  [data-testid="stTabs"] button[role="tab"]:hover {{ color: var(--text); background: rgba(255,255,255,.03); }}
  [data-testid="stTabs"] button[role="tab"][aria-selected="true"] {{ color: #fff; }}
  [data-testid="stTabs"] [data-baseweb="tab-highlight"] {{ background: linear-gradient(90deg, var(--accent), #FBBF24) !important; height: 3px; border-radius: 3px; }}

  /* Expanders, alerts, tables */
  [data-testid="stExpander"] {{ background: rgba(14,22,38,.7); border: 1px solid var(--line) !important; border-radius: 14px !important; transition: border-color .3s ease; }}
  [data-testid="stExpander"]:hover {{ border-color: rgba(45,212,191,.35) !important; }}
  [data-testid="stAlert"] {{ border-radius: 12px; border: 1px solid var(--line); animation: fadeIn .4s var(--ease) both; }}
  [data-testid="stDataFrame"], [data-testid="stTable"] {{ border-radius: 12px; overflow: hidden; border: 1px solid var(--line); }}
  [data-testid="stChatMessage"] {{ background: rgba(19,30,51,.55); border: 1px solid var(--line); border-radius: 14px; animation: fadeIn .4s var(--ease) both; }}
  [data-testid="stSlider"] [role="slider"] {{ box-shadow: 0 0 0 4px rgba(249,115,22,.2); }}

  /* Progress */
  .progress-track {{ background: rgba(255,255,255,.07); border-radius: 10px; height: 7px; margin: 10px 0 20px; overflow: hidden; }}
  .progress-fill {{ background: linear-gradient(90deg, {ORANGE}, #FBBF24); border-radius: 10px; height: 7px; transition: width .6s var(--ease); }}

  .source-tag {{
    display: inline-flex; align-items: center; gap: 6px; font-size: .72rem; color: var(--muted);
    background: rgba(255,255,255,.04); border: 1px solid var(--line); padding: 3px 10px; border-radius: 7px; font-family: var(--font-mono);
  }}
  .beie-warning, .beie-info {{ padding: 14px 18px; border-radius: 0 12px 12px 0; margin: 10px 0; font-size: .9rem; animation: fadeIn .4s var(--ease) both; }}
  .beie-warning {{ background: rgba(245,158,11,.1); border-left: 3px solid {AMBER}; color: #FDE68A; }}
  .beie-info {{ background: rgba(45,212,191,.08); border-left: 3px solid {CYAN}; color: #B7F3EA; }}

  /* Scrollbar */
  ::-webkit-scrollbar {{ width: 10px; height: 10px; }}
  ::-webkit-scrollbar-thumb {{ background: #1E2B45; border-radius: 10px; border: 2px solid var(--ink); }}
  ::-webkit-scrollbar-thumb:hover {{ background: #2B3D61; }}
  ::selection {{ background: rgba(249,115,22,.35); }}

  @media (prefers-reduced-motion: reduce) {{
    *, *::before, *::after {{ animation: none !important; transition: none !important; }}
  }}

  /* Responsive */
  @media (max-width: 992px) {{ .hero-title {{ font-size: 2.6rem; }} .hero-container {{ padding: 44px 18px; }} }}
  @media (max-width: 768px) {{
    .hero-title {{ font-size: 2.1rem; }}
    .hero-subtitle {{ font-size: 1rem; }}
    .beie-card {{ padding: 16px !important; border-radius: 14px !important; }}
    .ticker-wrap {{ display: none !important; }}
    .stButton > button {{ width: 100% !important; min-height: 48px !important; }}
    div[data-testid="column"] {{ min-width: 100% !important; flex: 1 1 100% !important; }}
    .brand-sub {{ display: none; }}
  }}
  @media (max-width: 480px) {{
    .hero-title {{ font-size: 1.7rem; }}
    .hero-badge {{ font-size: .66rem; padding: 5px 12px; }}
    div[data-testid="stMetricValue"] {{ font-size: 1.4rem !important; }}
    .persona-card {{ padding: 18px !important; }}
  }}
"""

_HERO_CSS = f".hero-container {{ background-image: linear-gradient(180deg, rgba(7,11,20,.55), rgba(7,11,20,.88)), url('{asset_data_uri('hero.jpg')}'); }}"

CUSTOM_CSS = "<style>" + _BODY_CSS + _HERO_CSS + icon_css(_used_icons()) + "</style>"

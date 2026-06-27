"""
components/ui.py
----------------
Shared UI helpers: page headers, section headers, stat cards,
badges, dividers, and CSS injection.
"""
from __future__ import annotations
import streamlit as st
import config


def inject_global_css() -> None:
    """Inject global CSS for premium styling."""
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }}

    /* Main background */
    .stApp {{
        background: {config.COLORS['light_bg']};
    }}

    /* Sidebar */
    [data-testid="stSidebar"] {{
        background: {config.COLORS['primary']} !important;
    }}
    /* Streamlit's auto page navigation links (top of sidebar) */
    [data-testid="stSidebarNav"] a,
    [data-testid="stSidebarNav"] a span,
    [data-testid="stSidebarNav"] a p {{
        color: rgba(255,255,255,0.85) !important;
        font-weight: 500 !important;
    }}
    [data-testid="stSidebarNav"] a:hover {{
        background-color: rgba(255,255,255,0.08) !important;
        border-radius: 6px;
    }}
    /* Currently active page — highlight with violet */
    [data-testid="stSidebarNav"] a[aria-current="page"],
    [data-testid="stSidebarNav"] a[aria-current="page"] span,
    [data-testid="stSidebarNav"] a[aria-current="page"] p {{
        color: #FFFFFF !important;
        font-weight: 700 !important;
        background-color: {config.COLORS['secondary']} !important;
        border-radius: 6px;
    }}
    /* Sidebar text — but NOT inside input controls */
    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] .stCaption,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {{
        color: rgba(255,255,255,0.9) !important;
    }}
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stMultiSelect label,
    [data-testid="stSidebar"] .stDateInput label {{
        color: rgba(255,255,255,0.7) !important;
        font-size: 0.78rem !important;
        font-weight: 500 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}
    /* Input boxes — light bg, dark text so placeholders + selections are visible */
    [data-testid="stSidebar"] [data-baseweb="select"] > div,
    [data-testid="stSidebar"] [data-baseweb="input"] > div,
    [data-testid="stSidebar"] .stDateInput input {{
        background-color: #FFFFFF !important;
        color: {config.COLORS['primary']} !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
    }}
    [data-testid="stSidebar"] [data-baseweb="select"] *,
    [data-testid="stSidebar"] [data-baseweb="input"] * {{
        color: {config.COLORS['primary']} !important;
    }}
    /* Placeholder text in selects — slate-grey */
    [data-testid="stSidebar"] [data-baseweb="select"] [class*="placeholder"] {{
        color: #94A3B8 !important;
    }}
    /* Dropdown arrow / clear icons */
    [data-testid="stSidebar"] [data-baseweb="select"] svg {{
        fill: {config.COLORS['primary']} !important;
    }}
    /* Selected tags (pills) inside multiselects */
    [data-testid="stSidebar"] [data-baseweb="tag"] {{
        background-color: {config.COLORS['secondary']} !important;
    }}
    [data-testid="stSidebar"] [data-baseweb="tag"] * {{
        color: #FFFFFF !important;
    }}
    [data-testid="stSidebar"] hr {{
        border-color: rgba(255,255,255,0.15) !important;
    }}
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown h3 {{
        color: rgba(255,255,255,0.5) !important;
        font-size: 0.65rem !important;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        margin-top: 1.2rem;
    }}

    /* Metric cards */
    [data-testid="stMetric"] {{
        background: white;
        border-radius: 12px;
        padding: 16px 20px;
        border: 1px solid {config.COLORS['border']};
        box-shadow: 0 1px 4px rgba(15,31,61,0.06);
        transition: box-shadow 0.2s;
    }}
    [data-testid="stMetric"]:hover {{
        box-shadow: 0 4px 16px rgba(108,63,197,0.12);
    }}
    [data-testid="stMetricLabel"] {{
        font-size: 0.72rem !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: {config.COLORS['text_muted']} !important;
    }}
    [data-testid="stMetricValue"] {{
        font-size: 1.6rem !important;
        font-weight: 700 !important;
        color: {config.COLORS['primary']} !important;
    }}
    [data-testid="stMetricDelta"] {{
        font-size: 0.8rem !important;
    }}

    /* Plotly charts */
    .js-plotly-plot {{
        border-radius: 12px;
        overflow: hidden;
    }}

    /* Expanders */
    .streamlit-expanderHeader {{
        background: white !important;
        border-radius: 8px !important;
        border: 1px solid {config.COLORS['border']} !important;
        font-weight: 600 !important;
        color: {config.COLORS['primary']} !important;
    }}

    /* Dataframe */
    [data-testid="stDataFrame"] {{
        border-radius: 10px;
        overflow: hidden;
        border: 1px solid {config.COLORS['border']};
    }}

    /* Buttons */
    .stDownloadButton button {{
        background: {config.COLORS['secondary']} !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 0.4rem 1.2rem !important;
        transition: opacity 0.2s !important;
    }}
    .stDownloadButton button:hover {{
        opacity: 0.85 !important;
    }}

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        background: white;
        border-radius: 10px;
        padding: 4px;
        border: 1px solid {config.COLORS['border']};
        gap: 4px;
    }}
    .stTabs [data-baseweb="tab"] {{
        border-radius: 7px;
        font-weight: 500;
        color: {config.COLORS['text_muted']};
    }}
    .stTabs [aria-selected="true"] {{
        background: {config.COLORS['secondary']} !important;
        color: white !important;
    }}

    /* Section divider */
    hr {{
        border: none;
        border-top: 1px solid {config.COLORS['border']};
        margin: 1.5rem 0;
    }}

    /* Hide Streamlit branding */
    #MainMenu, footer, header {{ visibility: hidden; }}

    /* Scrollbar */
    ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
    ::-webkit-scrollbar-track {{ background: {config.COLORS['light_bg']}; }}
    ::-webkit-scrollbar-thumb {{ background: {config.COLORS['border']}; border-radius: 3px; }}
    ::-webkit-scrollbar-thumb:hover {{ background: {config.COLORS['secondary']}; }}
    </style>
    """, unsafe_allow_html=True)


def page_header(icon: str, title: str, subtitle: str) -> None:
    """Render a premium gradient page header."""
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, {config.COLORS['primary']} 0%, {config.COLORS['secondary']} 100%);
        border-radius: 14px;
        padding: 28px 36px;
        margin-bottom: 20px;
        box-shadow: 0 4px 20px rgba(108,63,197,0.25);
    ">
        <div style="display:flex; align-items:center; gap:14px;">
            <span style="font-size:2rem;">{icon}</span>
            <div>
                <h1 style="color:white; font-size:1.7rem; font-weight:700;
                           margin:0; line-height:1.2;">{title}</h1>
                <p style="color:rgba(255,255,255,0.75); margin:4px 0 0 0;
                          font-size:0.92rem;">{subtitle}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def section_header(title: str, subtitle: str = "") -> None:
    """Render a section header with optional subtitle."""
    st.markdown(f"""
    <div style="margin: 1.5rem 0 0.75rem 0; border-left: 4px solid {config.COLORS['secondary']};
                padding-left: 12px;">
        <div style="font-size:1.05rem; font-weight:700;
                    color:{config.COLORS['primary']};">{title}</div>
        {"<div style='font-size:0.8rem; color:" + config.COLORS['text_muted'] + "; margin-top:2px;'>" + subtitle + "</div>" if subtitle else ""}
    </div>
    """, unsafe_allow_html=True)


def stat_card(label: str, value: str, delta: str = "", colour: str = "#6C3FC5",
              icon: str = "") -> str:
    """Return HTML for a custom stat card."""
    delta_html = (
        f'<div style="font-size:0.75rem; color:{config.COLORS["success"]}; '
        f'margin-top:4px;">{delta}</div>' if delta else ""
    )
    return f"""
    <div style="
        background: white;
        border-radius: 12px;
        padding: 18px 20px;
        border: 1px solid {config.COLORS['border']};
        border-top: 3px solid {colour};
        box-shadow: 0 2px 8px rgba(15,31,61,0.06);
    ">
        <div style="font-size:0.7rem; font-weight:700; text-transform:uppercase;
                    letter-spacing:0.07em; color:{config.COLORS['text_muted']};">
            {icon + '  ' if icon else ''}{label}
        </div>
        <div style="font-size:1.55rem; font-weight:700; color:{config.COLORS['primary']};
                    margin-top:6px;">{value}</div>
        {delta_html}
    </div>
    """


def badge(text: str, colour: str = "#6C3FC5") -> str:
    """Return HTML for a badge/pill."""
    return (
        f'<span style="background:{colour}20; color:{colour}; border:1px solid {colour}40; '
        f'border-radius:20px; padding:2px 10px; font-size:0.72rem; '
        f'font-weight:600; display:inline-block; margin:2px;">{text}</span>'
    )


def insight_box(text: str, icon: str = "💡") -> None:
    """Render a highlighted insight box."""
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #F5F3FF 0%, #EEF2FF 100%);
        border: 1px solid #C4B5FD;
        border-left: 4px solid {config.COLORS['secondary']};
        border-radius: 10px;
        padding: 14px 18px;
        margin: 8px 0;
        font-size: 0.88rem;
        color: {config.COLORS['primary']};
        line-height: 1.5;
    ">
        {icon} {text}
    </div>
    """, unsafe_allow_html=True)


def window_badge(label: str = "Last 90 Days") -> None:
    """Show the analysis window badge."""
    st.markdown(
        f'<span style="background:#EEF2FF; color:{config.COLORS["secondary"]}; '
        f'border:1px solid #C4B5FD; border-radius:20px; padding:3px 12px; '
        f'font-size:0.75rem; font-weight:600;">📅 {label}</span>',
        unsafe_allow_html=True,
    )

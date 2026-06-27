"""app.py — Landing page (overview)."""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st
import plotly.graph_objects as go

import config
from charts.theme import register_theme
from components.ui import inject_global_css
from components.kpi_cards import KPICard, render_kpi_grid
from components.sidebar import render_sidebar
from utils.data_loader import load_data, get_90d, get_skills_series, get_domain_tags_series
from utils.insights import emerging_skills, accelerating_companies, market_pulse_summary
from utils.formatters import fmt_pct

st.set_page_config(page_title=config.APP_TITLE, page_icon=config.APP_ICON,
                   layout=config.LAYOUT, initial_sidebar_state="expanded")
register_theme()

try:
    df_master = load_data()
    data_ok = True
except FileNotFoundError as exc:
    data_ok = False; data_error = str(exc)

inject_global_css()
if data_ok:
    filters = render_sidebar(df_master)
    df90 = get_90d(df_master)

# Hero
st.markdown(f"""
<div style="background: linear-gradient(135deg, #0F1F3D 0%, #6C3FC5 55%, #00B4D8 100%);
            border-radius: 16px; padding: 38px 44px; margin-bottom: 24px;
            box-shadow: 0 8px 32px rgba(108,63,197,0.3);
            position: relative; overflow: hidden;">
    <div style="position:absolute; top:-50px; right:-50px; width:220px; height:220px;
                background:rgba(255,255,255,0.04); border-radius:50%;"></div>
    <div style="position:absolute; bottom:-70px; right:140px; width:170px; height:170px;
                background:rgba(255,255,255,0.03); border-radius:50%;"></div>
    <div style="position:relative; z-index:1;">
        <div style="display:flex; align-items:center; gap:10px; margin-bottom:6px;">
            <div style="background:rgba(16,185,129,0.18); border-radius:20px;
                        padding:3px 11px; font-size:0.72rem; color:#10B981;
                        font-weight:700; border:1px solid rgba(16,185,129,0.4);">● LIVE</div>
            <div style="color:rgba(255,255,255,0.6); font-size:0.78rem;">
                {len(df_master) if data_ok else '15,069'} postings tracked
            </div>
        </div>
        <h1 style="color:white; font-size:2.3rem; font-weight:800; margin:0 0 8px 0;
                   letter-spacing:-0.02em;">🤖 AI Talent Intelligence Platform</h1>
        <p style="color:rgba(255,255,255,0.82); font-size:1rem; margin:0 0 22px 0;
                  max-width:680px; line-height:1.6;">
            Discover where AI jobs are surging, which skills command premium salaries,
            and find your perfect role — across 25 countries.
        </p>
        <div style="display:flex; gap:10px; flex-wrap:wrap;">
            <span style="background:rgba(255,255,255,0.18); color:white; border-radius:22px;
                         padding:5px 16px; font-size:0.82rem; font-weight:600;">📅 Last 90 Days</span>
            <span style="background:rgba(255,255,255,0.18); color:white; border-radius:22px;
                         padding:5px 16px; font-size:0.82rem; font-weight:600;">🌍 25 Countries</span>
            <span style="background:rgba(255,255,255,0.18); color:white; border-radius:22px;
                         padding:5px 16px; font-size:0.82rem; font-weight:600;">v{config.APP_VERSION}</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

if not data_ok:
    st.error(f"⚠️ {data_error}"); st.stop()

# Pulse strip
pulse = market_pulse_summary(df90, recent_days=7)
wow_pct = pulse["wow_pct"]
wow_colour = config.COLORS["success"] if wow_pct >= 0 else config.COLORS["danger"]
wow_arrow = "▲" if wow_pct >= 0 else "▼"
emerging = emerging_skills(df90, recent_days=30, min_recent=20)
hot_skill = emerging.iloc[0] if not emerging.empty else None
accel = accelerating_companies(df90, recent_days=30, min_prior=5)
hot_co = accel.iloc[0] if not accel.empty else None

st.markdown(f"""<div style="font-size:0.78rem; font-weight:700; text-transform:uppercase;
letter-spacing:0.1em; color:{config.COLORS['text_muted']}; margin-bottom:14px;">
📡 Live Market Pulse</div>""", unsafe_allow_html=True)

ps1, ps2, ps3, ps4 = st.columns(4)
with ps1:
    st.markdown(f"""
    <div style="background:white; border-radius:12px; padding:18px;
                border:1px solid {config.COLORS['border']};
                border-top:3px solid {config.COLORS['secondary']};">
        <div style="font-size:0.7rem; font-weight:700; text-transform:uppercase;
                    letter-spacing:0.07em; color:{config.COLORS['text_muted']};">📋 Last 7 Days</div>
        <div style="font-size:1.6rem; font-weight:700; color:{config.COLORS['primary']};
                    margin-top:6px;">{pulse['recent_postings']:,}</div>
        <div style="font-size:0.85rem; font-weight:600; color:{wow_colour}; margin-top:4px;">
            {wow_arrow} {abs(wow_pct):.1f}% WoW</div>
    </div>
    """, unsafe_allow_html=True)
with ps2:
    if hot_skill is not None:
        st.markdown(f"""
        <div style="background:white; border-radius:12px; padding:18px;
                    border:1px solid {config.COLORS['border']};
                    border-top:3px solid {config.COLORS['accent']};">
            <div style="font-size:0.7rem; font-weight:700; text-transform:uppercase;
                        letter-spacing:0.07em; color:{config.COLORS['text_muted']};">🔥 Hottest Skill</div>
            <div style="font-size:1.3rem; font-weight:700; color:{config.COLORS['primary']};
                        margin-top:6px;">{hot_skill['Skill']}</div>
            <div style="font-size:0.85rem; font-weight:600; color:{config.COLORS['accent']};
                        margin-top:4px;">▲ {hot_skill['Δ %']:+.0f}% (30d)</div>
        </div>
        """, unsafe_allow_html=True)
with ps3:
    if hot_co is not None:
        st.markdown(f"""
        <div style="background:white; border-radius:12px; padding:18px;
                    border:1px solid {config.COLORS['border']};
                    border-top:3px solid {config.COLORS['accent2']};">
            <div style="font-size:0.7rem; font-weight:700; text-transform:uppercase;
                        letter-spacing:0.07em; color:{config.COLORS['text_muted']};">🚀 Top Grower</div>
            <div style="font-size:1.15rem; font-weight:700; color:{config.COLORS['primary']};
                        margin-top:6px; white-space:nowrap; overflow:hidden;
                        text-overflow:ellipsis;">{hot_co[config.COL_COMPANY]}</div>
            <div style="font-size:0.85rem; font-weight:600; color:{config.COLORS['accent2']};
                        margin-top:4px;">▲ {hot_co['Growth %']:+.0f}% · {int(hot_co['Recent'])} new</div>
        </div>
        """, unsafe_allow_html=True)
with ps4:
    st.markdown(f"""
    <div style="background:white; border-radius:12px; padding:18px;
                border:1px solid {config.COLORS['border']};
                border-top:3px solid {config.COLORS['teal']};">
        <div style="font-size:0.7rem; font-weight:700; text-transform:uppercase;
                    letter-spacing:0.07em; color:{config.COLORS['text_muted']};">🌍 Top Market</div>
        <div style="font-size:1.3rem; font-weight:700; color:{config.COLORS['primary']};
                    margin-top:6px;">{pulse['top_country']}</div>
        <div style="font-size:0.85rem; font-weight:600; color:{config.COLORS['teal']};
                    margin-top:4px;">🏢 {pulse['active_companies']:,} active</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

# Weekly trend mini-chart
df90c = df90.copy()
df90c["wk"] = df90c[config.COL_POSTED_DT].dt.to_period("W").astype(str)
wk_data = df90c.groupby("wk").size().reset_index(name="Jobs")
wk_data["Week"] = wk_data["wk"].str[-10:]

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=wk_data["Week"], y=wk_data["Jobs"],
    mode="lines+markers", fill="tozeroy",
    line=dict(color=config.COLORS["secondary"], width=2.5, shape="spline"),
    fillcolor="rgba(108,63,197,0.12)",
    marker=dict(size=7, color=config.COLORS["secondary"],
                line=dict(width=2, color="white")),
    hovertemplate="<b>Week of %{x}</b><br>%{y:,} postings<extra></extra>",
))
fig.update_layout(title=dict(text="📈  Weekly Posting Velocity (Last 90 Days)", x=0.01,
                              font=dict(size=14)),
                  height=240, margin=dict(t=46, b=40, l=10, r=10),
                  showlegend=False, xaxis_tickangle=-30)
st.plotly_chart(fig, width="stretch")

st.divider()

# Page navigation grid
st.markdown(f"""<div style="font-size:0.78rem; font-weight:700; text-transform:uppercase;
letter-spacing:0.1em; color:{config.COLORS['text_muted']}; margin-bottom:16px;">
🗺 Platform Modules</div>""", unsafe_allow_html=True)

PAGES = [
    ("🔥", "Market Pulse",      "KPIs · emerging skills · accelerating companies · weekly trends",     config.COLORS["accent"]),
    ("🎯", "My Match",          "Build your profile · get personalised matches & salary estimate",     config.COLORS["success"]),
    ("🌍", "Geography",         "World map · country drill-down · side-by-side comparison",            config.COLORS["accent2"]),
    ("🏢", "Companies & Roles", "Top employers · titles · seniority · domains · drill-downs",          config.COLORS["secondary"]),
    ("💰", "Skills & Salary",   "Top skills · co-occurrence · salary benchmarks by country/role",      config.COLORS["warning"]),
    ("🔍", "Explore Jobs",      "Full-text search · raw data browser · CSV/Excel export",              "#64748B"),
]

for row_start in range(0, len(PAGES), 3):
    chunk = PAGES[row_start: row_start+3]
    cols = st.columns(3)
    for col, (icon, name, desc, colour) in zip(cols, chunk):
        with col:
            st.markdown(f"""
            <div style="background:white; border-radius:14px; padding:22px;
                        border:1px solid {config.COLORS['border']};
                        border-top:4px solid {colour}; height:150px;
                        box-shadow:0 4px 12px rgba(15,31,61,0.06);">
                <div style="font-size:1.8rem; margin-bottom:8px;">{icon}</div>
                <div style="font-weight:700; color:{config.COLORS['primary']};
                            font-size:1rem; margin-bottom:4px;">{name}</div>
                <div style="color:{config.COLORS['text_muted']}; font-size:0.8rem;
                            line-height:1.4;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)
    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

st.markdown(f"""<div style="text-align:center; color:{config.COLORS['text_muted']};
font-size:0.74rem; padding:24px 0 8px 0;">
{config.APP_TITLE} · v{config.APP_VERSION} · {len(df_master):,} postings · 25 countries
</div>""", unsafe_allow_html=True)

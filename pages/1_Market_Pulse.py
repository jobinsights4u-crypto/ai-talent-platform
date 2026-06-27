"""Page 1 — Market Pulse: KPIs, signals, trends."""
from __future__ import annotations
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import config
from charts.bar_charts import horizontal_bar, diverging_bar
from charts.map_charts import choropleth_jobs
from charts.misc_charts import donut_chart
from charts.theme import register_theme
from components.download import download_csv_button
from components.kpi_cards import KPICard, render_kpi_grid
from components.sidebar import render_sidebar
from components.ui import inject_global_css, page_header, section_header, insight_box, window_badge
from utils.data_loader import filter_dataframe, get_90d, get_skills_series, get_domain_tags_series, load_data
from utils.insights import emerging_skills, accelerating_companies, market_pulse_summary, skill_salary_premium
from utils.formatters import fmt_pct

st.set_page_config(page_title=f"Market Pulse · {config.APP_TITLE}",
                   page_icon="🔥", layout=config.LAYOUT)
register_theme()

try:
    df_master = load_data()
except FileNotFoundError as exc:
    st.error(str(exc)); st.stop()

inject_global_css()
filters = render_sidebar(df_master)
df_all = filter_dataframe(df_master, **filters)
df = get_90d(df_all)
if df.empty:
    st.warning("No records match filters."); st.stop()

page_header("🔥", "Market Pulse",
            f"Real-time signals across {len(df):,} postings · "
            f"{df[config.COL_COUNTRY].nunique()} countries · last 90 days")
window_badge()
st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

# ─── Pulse banner ────────────────────────────────────────────────────────
pulse = market_pulse_summary(df, recent_days=7)
wow_pct = pulse["wow_pct"]
wow_colour = config.COLORS["success"] if wow_pct >= 0 else config.COLORS["danger"]
wow_arrow = "▲" if wow_pct >= 0 else "▼"

st.markdown(f"""
<div style="background:linear-gradient(135deg,#0F1F3D 0%,#6C3FC5 100%);
            border-radius:14px; padding:24px 32px; margin-bottom:20px;
            display:grid; grid-template-columns:repeat(5,1fr); gap:24px;
            box-shadow:0 4px 20px rgba(108,63,197,0.25);">
    <div>
        <div style="color:rgba(255,255,255,0.6); font-size:0.7rem; font-weight:700;
                    text-transform:uppercase; letter-spacing:0.08em;">Last 7 Days</div>
        <div style="color:white; font-size:1.8rem; font-weight:700; margin-top:4px;">{pulse['recent_postings']:,}</div>
        <div style="color:rgba(255,255,255,0.7); font-size:0.78rem;">new postings</div>
    </div>
    <div>
        <div style="color:rgba(255,255,255,0.6); font-size:0.7rem; font-weight:700;
                    text-transform:uppercase; letter-spacing:0.08em;">WoW Change</div>
        <div style="color:{wow_colour}; font-size:1.8rem; font-weight:700; margin-top:4px;">{wow_arrow} {abs(wow_pct)}%</div>
        <div style="color:rgba(255,255,255,0.7); font-size:0.78rem;">vs prior 7 days</div>
    </div>
    <div>
        <div style="color:rgba(255,255,255,0.6); font-size:0.7rem; font-weight:700;
                    text-transform:uppercase; letter-spacing:0.08em;">Active</div>
        <div style="color:white; font-size:1.8rem; font-weight:700; margin-top:4px;">{pulse['active_companies']:,}</div>
        <div style="color:rgba(255,255,255,0.7); font-size:0.78rem;">companies · {pulse['active_countries']} countries</div>
    </div>
    <div>
        <div style="color:rgba(255,255,255,0.6); font-size:0.7rem; font-weight:700;
                    text-transform:uppercase; letter-spacing:0.08em;">Top Skill</div>
        <div style="color:white; font-size:1.4rem; font-weight:700; margin-top:4px;">🥇 {pulse['top_skill']}</div>
        <div style="color:rgba(255,255,255,0.7); font-size:0.78rem;">last 7 days</div>
    </div>
    <div>
        <div style="color:rgba(255,255,255,0.6); font-size:0.7rem; font-weight:700;
                    text-transform:uppercase; letter-spacing:0.08em;">Hot Market</div>
        <div style="color:white; font-size:1.4rem; font-weight:700; margin-top:4px;">🌍 {pulse['top_country']}</div>
        <div style="color:rgba(255,255,255,0.7); font-size:0.78rem;">leading volume</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ─── KPI row ─────────────────────────────────────────────────────────────
sal = df[df[config.COL_SALARY_MID].notna()][config.COL_SALARY_MID]
df["wk"] = df[config.COL_POSTED_DT].dt.to_period("W")
wk_counts = df.groupby("wk").size()
wow_full = (wk_counts.iloc[-1]-wk_counts.iloc[-2])/wk_counts.iloc[-2]*100 if len(wk_counts)>=2 else 0

render_kpi_grid([
    KPICard("Total Postings (90d)", len(df), icon="📋"),
    KPICard("Active Countries", df[config.COL_COUNTRY].nunique(), icon="🌍"),
    KPICard("Unique Companies", df[config.COL_COMPANY].nunique(), icon="🏢"),
    KPICard("Avg Salary", sal.mean() if len(sal) else 0, icon="💰",
            format_fn=lambda v: f"${v:,.0f}" if v else "N/A"),
    KPICard("Median Salary", sal.median() if len(sal) else 0, icon="📊",
            format_fn=lambda v: f"${v:,.0f}" if v else "N/A"),
    KPICard("Remote Share", (df[config.COL_REMOTE]=="Remote").mean(), icon="🏠",
            format_fn=fmt_pct),
    KPICard("Hybrid Share", (df[config.COL_REMOTE]=="Hybrid").mean(), icon="🔀",
            format_fn=fmt_pct),
    KPICard("Weekly Growth", wow_full, icon="📈",
            format_fn=lambda v: f"{v:+.1f}%"),
], cols_per_row=4)
st.divider()

# ─── Tabs for Signals ────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Weekly Trend", "🔥 Emerging Skills",
    "🚀 Top Companies", "💎 Top-Paying Skills",
])

# Tab 1: Trend
with tab1:
    section_header("Weekly Posting Velocity", "Bars: weekly jobs · Line: 4-week rolling average")
    weekly = (df.groupby(config.COL_POSTED_WEEK).size()
              .reset_index(name="Jobs").sort_values(config.COL_POSTED_WEEK))
    weekly["4W Avg"] = weekly["Jobs"].rolling(4, min_periods=1).mean().round(0)
    weekly["Week"]   = weekly[config.COL_POSTED_WEEK].str[-10:]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=weekly["Week"], y=weekly["Jobs"], name="Weekly Jobs",
        marker_color=config.COLORS["secondary"], opacity=0.82,
        hovertemplate="<b>Week of %{x}</b><br>%{y:,} jobs<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=weekly["Week"], y=weekly["4W Avg"], name="4-Week Rolling Avg",
        mode="lines+markers", line=dict(color=config.COLORS["accent"], width=3, shape="spline"),
        marker=dict(size=8, color="white", line=dict(color=config.COLORS["accent"], width=2)),
        hovertemplate="<b>%{x}</b><br>4-week avg: %{y:,.0f}<extra></extra>",
    ))
    fig.update_layout(
        legend=dict(orientation="h", y=1.08, x=0),
        xaxis_title="", yaxis_title="Job Postings",
        margin=dict(t=20, b=70), xaxis_tickangle=-35, height=380,
    )
    st.plotly_chart(fig, width="stretch")

    # Cumulative
    weekly["Cumulative"] = weekly["Jobs"].cumsum()
    fig_c = go.Figure(go.Scatter(
        x=weekly["Week"], y=weekly["Cumulative"], mode="lines", fill="tozeroy",
        line=dict(color=config.COLORS["secondary"], width=2.5, shape="spline"),
        fillcolor="rgba(108,63,197,0.15)",
        hovertemplate="<b>Week of %{x}</b><br>Cumulative: %{y:,}<extra></extra>",
    ))
    fig_c.update_layout(
        title="Cumulative Postings (90-day total to date)",
        xaxis_title="", yaxis_title="Cumulative Jobs",
        margin=dict(t=40, b=60), height=300,
    )
    st.plotly_chart(fig_c, width="stretch")

# Tab 2: Emerging skills
with tab2:
    section_header("Rising vs Cooling Skills",
                   "Comparing posting rate in last 30 days vs prior 60 days")
    emerging = emerging_skills(df, recent_days=30, min_recent=20)

    if not emerging.empty:
        col_h, col_c = st.columns(2)
        rising = emerging[emerging["Δ %"] > 0].head(12)
        cooling = emerging[emerging["Δ %"] < 0].tail(8)

        with col_h:
            st.markdown(f"""<div style="font-weight:700; color:{config.COLORS['accent']};
                        font-size:0.95rem; margin-bottom:6px;">🔥 Rising Fast</div>""",
                        unsafe_allow_html=True)
            st.plotly_chart(diverging_bar(rising, "Skill", "Δ %", height=400),
                            width="stretch")

        with col_c:
            st.markdown(f"""<div style="font-weight:700; color:{config.COLORS['info']};
                        font-size:0.95rem; margin-bottom:6px;">❄ Cooling</div>""",
                        unsafe_allow_html=True)
            if not cooling.empty:
                st.plotly_chart(diverging_bar(cooling, "Skill", "Δ %", height=400),
                                width="stretch")
            else:
                st.info("No cooling skills above the minimum sample threshold.")

        top3 = emerging.head(3)
        hot_msg = " · ".join(f"<strong>{r['Skill']}</strong> ({r['Δ %']:+.0f}%)"
                             for _, r in top3.iterrows())
        insight_box(f"Hottest skills last 30 days: {hot_msg}", icon="🔥")

        with st.expander("📋 Full emerging-skills table"):
            st.dataframe(emerging, width="stretch", column_config={
                "Δ %": st.column_config.NumberColumn(format="%+.1f%%"),
            })

# Tab 3: Companies
with tab3:
    section_header("Fastest-Accelerating Companies",
                   "Companies ramping up hiring fastest in the last 30 days")
    accel = accelerating_companies(df, recent_days=30, min_prior=5)

    if not accel.empty:
        top15 = accel.head(15)
        fig_a = go.Figure(go.Bar(
            x=top15["Growth %"].iloc[::-1], y=top15[config.COL_COMPANY].iloc[::-1],
            orientation="h",
            marker=dict(color=top15["Growth %"].iloc[::-1],
                        colorscale=[[0,"#A78BFA"],[1,"#6C3FC5"]], showscale=False),
            text=[f"+{v:.0f}%   ({r} recent)" for v,r in
                  zip(top15["Growth %"].iloc[::-1], top15["Recent"].iloc[::-1])],
            textposition="outside",
            textfont=dict(size=11, color=config.COLORS["text_primary"]),
            cliponaxis=False,
            hovertemplate=("<b>%{y}</b><br>Growth: +%{x:.0f}%<br>"
                           "Recent: %{customdata[0]:,} · Prior: %{customdata[1]:,}<extra></extra>"),
            customdata=top15[["Recent","Prior"]].iloc[::-1].values,
        ))
        fig_a.update_layout(xaxis_title="Growth %", showlegend=False, height=500,
                            margin=dict(l=10, r=120, t=20, b=30))
        st.plotly_chart(fig_a, width="stretch")

        top_co = accel.iloc[0]
        insight_box(
            f"<strong>{top_co[config.COL_COMPANY]}</strong> is the fastest-accelerating employer "
            f"with <strong>+{top_co['Growth %']:.0f}%</strong> growth — "
            f"{top_co['Recent']:,} postings in last 30 days vs {top_co['Prior']:,} prior.",
            icon="🚀",
        )

# Tab 4: High-paying skills
with tab4:
    section_header("Premium Skills — Salary Leaders",
                   "Skills with the highest median salary (min 30 salaried postings)")
    premium = skill_salary_premium(df, min_count=30)

    if not premium.empty:
        top20 = premium.head(20)
        fig_p = go.Figure(go.Bar(
            x=top20["Median Salary"].iloc[::-1], y=top20["Skill"].iloc[::-1],
            orientation="h",
            marker=dict(color=top20["Premium %"].iloc[::-1],
                        colorscale=[[0,"#10B981"],[0.5,"#6C3FC5"],[1,"#F04E23"]],
                        colorbar=dict(title=dict(text="Premium %"), thickness=12)),
            text=[f"${v:,.0f}  ({p:+.0f}%)" for v,p in
                  zip(top20["Median Salary"].iloc[::-1], top20["Premium %"].iloc[::-1])],
            textposition="outside",
            textfont=dict(size=11, color=config.COLORS["text_primary"]),
            cliponaxis=False,
            hovertemplate=("<b>%{y}</b><br>Median: $%{x:,.0f}<br>"
                           "Sample: %{customdata[0]:,} · Premium: %{customdata[1]:+.0f}%<extra></extra>"),
            customdata=top20[["Postings","Premium %"]].iloc[::-1].values,
        ))
        fig_p.update_layout(xaxis_title="Median Salary (USD)", showlegend=False, height=600,
                            margin=dict(l=10, r=140, t=20, b=30))
        st.plotly_chart(fig_p, width="stretch")

        lead = premium.iloc[0]
        insight_box(
            f"<strong>{lead['Skill']}</strong> commands the highest median at "
            f"<strong>${lead['Median Salary']:,.0f}</strong> "
            f"— {lead['Premium %']:+.0f}% above market median (based on {int(lead['Postings'])} postings).",
            icon="💎",
        )

st.divider()

# ─── Map + Domain side by side ───────────────────────────────────────────
section_header("Geographic & Domain Overview")
col_m, col_d = st.columns([3, 2])

with col_m:
    cc = df.groupby(config.COL_COUNTRY).size().reset_index(name="Job Count")
    st.plotly_chart(choropleth_jobs(cc, height=380), width="stretch")

with col_d:
    dt = get_domain_tags_series(df).value_counts().head(7)
    if not dt.empty:
        st.plotly_chart(donut_chart(dt.index.tolist(), dt.values.tolist(), height=380),
                        width="stretch")

st.divider()
download_csv_button(df, filename="market_pulse_data.csv", key="mp_dl")

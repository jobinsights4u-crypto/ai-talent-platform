"""Page 3 — Geography: world map, country drill-down, side-by-side comparison."""
from __future__ import annotations
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import config
from charts.bar_charts import horizontal_bar, grouped_bar
from charts.map_charts import choropleth_jobs
from charts.misc_charts import donut_chart, heatmap_chart, box_plot
from charts.theme import register_theme
from components.download import download_csv_button
from components.kpi_cards import KPICard, render_kpi_grid
from components.sidebar import render_sidebar
from components.ui import inject_global_css, page_header, section_header, insight_box, window_badge, stat_card
from utils.data_loader import filter_dataframe, get_90d, get_skills_series, load_data
from utils.formatters import fmt_pct

st.set_page_config(page_title=f"Geography · {config.APP_TITLE}",
                   page_icon="🌍", layout=config.LAYOUT)
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

page_header("🌍", "Geography",
            f"{len(df):,} postings across {df[config.COL_COUNTRY].nunique()} countries")
window_badge(); st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

cc = df.groupby(config.COL_COUNTRY).size().reset_index(name="Job Count")
top = cc.nlargest(1, "Job Count").iloc[0]
render_kpi_grid([
    KPICard("Active Countries",  df[config.COL_COUNTRY].nunique(), icon="🌍"),
    KPICard("Total Postings",    len(df),                          icon="📋"),
    KPICard("Top Country",       str(top[config.COL_COUNTRY]),     icon="🥇", format_fn=lambda v: v),
    KPICard("Top Country Jobs",  int(top["Job Count"]),            icon="📊"),
], cols_per_row=4)
st.divider()

# Tabs
tab_map, tab_drill, tab_compare = st.tabs(["🗺 World Map", "🔍 Country Drill-down", "🆚 Compare Countries"])

# Map tab
with tab_map:
    section_header("Global Distribution")
    st.plotly_chart(choropleth_jobs(cc, height=440), width="stretch")

    section_header("Regional Breakdown")
    col_a, col_b = st.columns([2, 3])
    with col_a:
        reg = df["Region"].value_counts().reset_index(); reg.columns = ["Region", "Jobs"]
        st.plotly_chart(donut_chart(reg["Region"].tolist(), reg["Jobs"].tolist(), height=350),
                        width="stretch")
    with col_b:
        st.plotly_chart(horizontal_bar(cc, "Job Count", config.COL_COUNTRY,
                                       colour=config.COLORS["secondary"], top_n=15,
                                       gradient=True, height=350),
                        width="stretch")

    section_header("Work Arrangement by Country", "Top 15 countries — stacked")
    top15 = cc.nlargest(15, "Job Count")[config.COL_COUNTRY].tolist()
    rem = (df[df[config.COL_COUNTRY].isin(top15) & df[config.COL_REMOTE].notna()]
           .groupby([config.COL_COUNTRY, config.COL_REMOTE]).size().reset_index(name="Count"))
    st.plotly_chart(grouped_bar(
        rem, config.COL_COUNTRY, "Count", config.COL_REMOTE,
        barmode="stack",
        palette=[config.COLORS["secondary"], config.COLORS["accent2"], config.COLORS["teal"]],
        height=380,
    ), width="stretch")

# Drill-down tab
with tab_drill:
    section_header("Country Profile")
    sel = st.selectbox("Select country", sorted(df[config.COL_COUNTRY].unique()),
                       key="geo_drill_sel")
    cdf = df[df[config.COL_COUNTRY] == sel]

    sal = cdf[config.COL_SALARY_MID].mean()
    cols = st.columns(4)
    cards = [
        stat_card("Postings", f"{len(cdf):,}", colour=config.COLORS["secondary"], icon="📋"),
        stat_card("Companies", f"{cdf[config.COL_COMPANY].nunique():,}", colour=config.COLORS["accent2"], icon="🏢"),
        stat_card("Remote %", fmt_pct((cdf[config.COL_REMOTE]=="Remote").mean()),
                  colour=config.COLORS["teal"], icon="🏠"),
        stat_card("Avg Salary", f"${sal:,.0f}" if pd.notna(sal) else "N/A",
                  colour=config.COLORS["success"], icon="💰"),
    ]
    for col, html in zip(cols, cards):
        with col: st.markdown(html, unsafe_allow_html=True)
    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    ca, cb = st.columns(2)
    with ca:
        top_co = (cdf[cdf[config.COL_COMPANY].notna()]
                  .groupby(config.COL_COMPANY).size().reset_index(name="Jobs"))
        st.plotly_chart(
            horizontal_bar(top_co, "Jobs", config.COL_COMPANY,
                           title=f"Top Companies — {sel}", top_n=10, height=380,
                           colour=config.COLORS["secondary"]),
            width="stretch")
    with cb:
        dom = cdf["Primary AI Domain"].value_counts()
        st.plotly_chart(
            donut_chart(dom.index.tolist(), dom.values.tolist(),
                        title=f"AI Domain Mix — {sel}", height=380),
            width="stretch")

    section_header("Top Skills in This Country")
    sk = get_skills_series(cdf).value_counts().head(15).reset_index()
    sk.columns = ["Skill", "Mentions"]
    if not sk.empty:
        st.plotly_chart(horizontal_bar(sk, "Mentions", "Skill", top_n=15,
                                       colour=config.COLORS["accent2"], gradient=True, height=400),
                        width="stretch")

# Compare tab
with tab_compare:
    section_header("Side-by-Side Comparison", "Pick 2-4 countries")
    country_options = sorted(df[config.COL_COUNTRY].unique())
    top4 = df[config.COL_COUNTRY].value_counts().head(4).index.tolist()
    sel_compare = st.multiselect("Countries to compare", country_options,
                                 default=top4[:3], max_selections=4, key="geo_cmp")

    if len(sel_compare) < 2:
        st.info("👆 Pick at least 2 countries.")
    else:
        country_dfs = {c: df[df[config.COL_COUNTRY]==c] for c in sel_compare}
        colours = [config.COLORS["secondary"], config.COLORS["accent2"],
                   config.COLORS["accent"], config.COLORS["teal"]]

        # Headline cards
        cols = st.columns(len(sel_compare))
        for col, country, colour in zip(cols, sel_compare, colours):
            cdf2 = country_dfs[country]
            sal = cdf2[config.COL_SALARY_MID].mean()
            with col:
                st.markdown(f"""
                <div style="background:white; border-radius:12px; padding:16px;
                            border:1px solid {config.COLORS['border']};
                            border-top:4px solid {colour};">
                    <div style="font-size:1rem; font-weight:700; color:{colour};
                                margin-bottom:8px;">🌍 {country}</div>
                    <div style="font-size:0.7rem; color:{config.COLORS['text_muted']};
                                text-transform:uppercase; font-weight:600;">Postings</div>
                    <div style="font-size:1.4rem; font-weight:700;
                                color:{config.COLORS['primary']};">{len(cdf2):,}</div>
                    <div style="font-size:0.7rem; color:{config.COLORS['text_muted']};
                                text-transform:uppercase; font-weight:600; margin-top:8px;">Avg Salary</div>
                    <div style="font-size:1.05rem; font-weight:700;
                                color:{config.COLORS['primary']};">
                        {('$' + f'{sal:,.0f}') if pd.notna(sal) else '—'}
                    </div>
                    <div style="font-size:0.7rem; color:{config.COLORS['text_muted']};
                                text-transform:uppercase; font-weight:600; margin-top:8px;">Remote</div>
                    <div style="font-size:1.05rem; font-weight:700;
                                color:{config.COLORS['primary']};">
                        {fmt_pct((cdf2[config.COL_REMOTE]=='Remote').mean())}
                    </div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

        # Radar
        section_header("Multi-Dimensional Profile", "Normalised scores (0-100)")
        raw = {}
        for c in sel_compare:
            cdf2 = country_dfs[c]
            raw[c] = {
                "Volume":     float(len(cdf2)),
                "Salary":     float(cdf2[config.COL_SALARY_MID].mean()
                                    if cdf2[config.COL_SALARY_MID].notna().any() else 0),
                "Remote %":   float((cdf2[config.COL_REMOTE]=="Remote").mean()*100),
                "Diversity":  float(cdf2[config.COL_COMPANY].nunique()),
                "Senior %":   float((cdf2[config.COL_EXP_LEVEL]=="Senior").mean()*100),
            }
        def _norm(values):
            out = {c: {} for c in values}
            for d in next(iter(values.values())).keys():
                vals = [values[c][d] for c in values]
                lo, hi = min(vals), max(vals)
                rng = (hi - lo) or 1
                for c in values:
                    out[c][d] = round((values[c][d]-lo)/rng*100, 1)
            return out
        norm = _norm(raw)

        fig_r = go.Figure()
        for c, col in zip(sel_compare, colours):
            vals = list(norm[c].values()); dims = list(norm[c].keys())
            r_rgb = tuple(int(col.lstrip('#')[i:i+2],16) for i in (0,2,4))
            fig_r.add_trace(go.Scatterpolar(
                r=vals+[vals[0]], theta=dims+[dims[0]], fill="toself", name=c,
                line=dict(color=col, width=2.5),
                fillcolor=f"rgba{r_rgb + (0.2,)}",
                hovertemplate=f"<b>{c}</b><br>%{{theta}}: %{{r:.0f}}<extra></extra>",
            ))
        fig_r.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0,100], gridcolor="#E2E8F0",
                                tickfont=dict(size=10, color=config.COLORS["text_muted"])),
                angularaxis=dict(tickfont=dict(size=12, color=config.COLORS["primary"])),
                bgcolor="#FAFBFF",
            ),
            legend=dict(orientation="h", y=-0.05, x=0.5, xanchor="center"),
            height=460, margin=dict(t=20, b=60),
        )
        st.plotly_chart(fig_r, width="stretch")

        # Side-by-side top skills
        section_header("Top Skills per Country")
        cols2 = st.columns(len(sel_compare))
        for col, country, colour in zip(cols2, sel_compare, colours):
            cdf2 = country_dfs[country]
            sk = get_skills_series(cdf2).value_counts().head(10)
            with col:
                st.markdown(f"<div style='font-weight:700; color:{colour}; "
                            f"text-align:center; margin-bottom:6px;'>🌍 {country}</div>",
                            unsafe_allow_html=True)
                if not sk.empty:
                    fig = go.Figure(go.Bar(
                        x=sk.values[::-1], y=sk.index[::-1], orientation="h",
                        marker_color=colour, opacity=0.88,
                        text=[f"{v:,}" for v in sk.values[::-1]],
                        textposition="outside",
                        textfont=dict(size=10),
                        cliponaxis=False,
                        hovertemplate=f"<b>%{{y}}</b><br>%{{x:,}} mentions<extra></extra>",
                    ))
                    fig.update_layout(margin=dict(t=10, l=0, r=40, b=20),
                                      height=320, showlegend=False,
                                      xaxis_showticklabels=False)
                    st.plotly_chart(fig, width="stretch")

        # Salary box
        section_header("Salary Distribution Overlap")
        fig_box = go.Figure()
        for c, col in zip(sel_compare, colours):
            sd = country_dfs[c][config.COL_SALARY_MID].dropna()
            if len(sd) >= 3:
                fig_box.add_trace(go.Box(y=sd, name=c, marker_color=col,
                                         boxpoints="outliers",
                                         hovertemplate=f"<b>{c}</b><br>%{{y:$,.0f}}<extra></extra>"))
        fig_box.update_layout(yaxis_title="Salary USD (log scale)", yaxis_type="log",
                              showlegend=True, height=400, margin=dict(t=20))
        st.plotly_chart(fig_box, width="stretch")

st.divider()
download_csv_button(df, filename="geography.csv", key="geo_dl")

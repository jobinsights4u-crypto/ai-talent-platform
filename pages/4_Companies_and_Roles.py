"""Page 4 — Companies & Roles."""
from __future__ import annotations
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import config
from charts.bar_charts import horizontal_bar, grouped_bar
from charts.misc_charts import donut_chart, treemap_chart, heatmap_chart
from charts.theme import register_theme
from components.download import download_csv_button
from components.kpi_cards import KPICard, render_kpi_grid
from components.sidebar import render_sidebar
from components.ui import inject_global_css, page_header, section_header, insight_box, window_badge, stat_card
from utils.data_loader import filter_dataframe, get_90d, load_data
from utils.formatters import fmt_pct

st.set_page_config(page_title=f"Companies & Roles · {config.APP_TITLE}",
                   page_icon="🏢", layout=config.LAYOUT)
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

page_header("🏢", "Companies & Roles",
            f"{df[config.COL_COMPANY].nunique():,} employers · {df[config.COL_TITLE].nunique():,} unique titles")
window_badge(); st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

df_co = df[df[config.COL_COMPANY].notna()]
co_summary = (df_co.groupby(config.COL_COMPANY)
              .agg(Jobs=(config.COL_TITLE,"count"), Countries=(config.COL_COUNTRY,"nunique"))
              .reset_index().sort_values("Jobs",ascending=False))

render_kpi_grid([
    KPICard("Unique Companies",   co_summary.shape[0], icon="🏢"),
    KPICard("Unique Job Titles",  df[config.COL_TITLE].nunique(), icon="📝"),
    KPICard("Senior Level %",     (df[config.COL_EXP_LEVEL]=="Senior").mean(), icon="⬆", format_fn=fmt_pct),
    KPICard("Multi-Country Cos",  (co_summary["Countries"]>1).sum(), icon="🌍"),
], cols_per_row=4)
st.divider()

tab_co, tab_role, tab_dom = st.tabs(["🏢 Companies", "👤 Roles", "🤖 Domains"])

# ─── COMPANIES TAB ──────────────────────────────────────────────────────
with tab_co:
    section_header("Top 20 Hiring Companies")
    top20 = co_summary.nlargest(20, "Jobs").sort_values("Jobs")
    colours = [config.COLORS["accent"] if i >= 17 else config.COLORS["secondary"]
               for i in range(len(top20))]
    fig = go.Figure(go.Bar(
        x=top20["Jobs"], y=top20[config.COL_COMPANY], orientation="h",
        marker_color=colours,
        text=[f"{v:,}" for v in top20["Jobs"]],
        textposition="outside",
        textfont=dict(size=11, color=config.COLORS["text_primary"]),
        cliponaxis=False,
        hovertemplate="<b>%{y}</b><br>Jobs: %{x:,}<extra></extra>",
    ))
    fig.update_layout(showlegend=False, height=550,
                      xaxis_title="Postings", margin=dict(l=10,r=60,t=20,b=30))
    st.plotly_chart(fig, width="stretch")

    col_a, col_b = st.columns([2, 3])
    with col_a:
        section_header("Concentration")
        top10_jobs = co_summary.nlargest(10,"Jobs")["Jobs"].sum()
        rest = co_summary["Jobs"].sum() - top10_jobs
        st.plotly_chart(donut_chart(["Top 10","All Others"], [top10_jobs, rest], height=300,
                                    colours=[config.COLORS["accent"], "#CBD5E1"]),
                        width="stretch")
        pct = top10_jobs / co_summary["Jobs"].sum()
        insight_box(f"Top 10 companies = <strong>{fmt_pct(pct)}</strong> of all postings.")

    with col_b:
        section_header("Company × Domain Treemap", "Top 25 companies")
        top25 = co_summary.nlargest(25,"Jobs")[config.COL_COMPANY].tolist()
        tree = (df_co[df_co[config.COL_COMPANY].isin(top25)]
                .groupby([config.COL_COMPANY,"Primary AI Domain"]).size()
                .reset_index(name="Jobs"))
        st.plotly_chart(treemap_chart(tree,
                                       [config.COL_COMPANY,"Primary AI Domain"],
                                       "Jobs", height=400),
                        width="stretch")

    section_header("Company Drill-Down")
    sel_co = st.selectbox("Select company", co_summary[config.COL_COMPANY].tolist(),
                          key="co_drill")
    cdf = df_co[df_co[config.COL_COMPANY]==sel_co]
    sal = cdf[config.COL_SALARY_MID].mean()
    cols_c = st.columns(4)
    cards = [
        stat_card("Postings",  f"{len(cdf):,}", colour=config.COLORS["secondary"], icon="📋"),
        stat_card("Countries", f"{cdf[config.COL_COUNTRY].nunique()}", colour=config.COLORS["accent2"], icon="🌍"),
        stat_card("Remote %",  fmt_pct((cdf[config.COL_REMOTE]=="Remote").mean()),
                  colour=config.COLORS["teal"], icon="🏠"),
        stat_card("Avg Salary",f"${sal:,.0f}" if pd.notna(sal) else "N/A",
                  colour=config.COLORS["success"], icon="💰"),
    ]
    for col, html in zip(cols_c, cards):
        with col: st.markdown(html, unsafe_allow_html=True)
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    ca, cb = st.columns(2)
    with ca:
        c_ctry = cdf.groupby(config.COL_COUNTRY).size().reset_index(name="Jobs")
        st.plotly_chart(horizontal_bar(c_ctry, "Jobs", config.COL_COUNTRY,
                                       title=f"Country Spread", top_n=10, height=360,
                                       gradient=True),
                        width="stretch")
    with cb:
        cs = cdf[config.COL_SENIORITY].value_counts()
        st.plotly_chart(donut_chart(cs.index.tolist(), cs.values.tolist(),
                                    title=f"Seniority Mix", height=360),
                        width="stretch")

# ─── ROLES TAB ──────────────────────────────────────────────────────────
with tab_role:
    section_header("Top 20 Job Titles")
    titles = df.groupby(config.COL_TITLE).size().reset_index(name="Count")
    st.plotly_chart(horizontal_bar(titles, "Count", config.COL_TITLE,
                                   top_n=20, gradient=True, height=500),
                    width="stretch")

    col_l, col_r = st.columns(2)
    with col_l:
        section_header("Seniority Distribution")
        sc = df[config.COL_SENIORITY].value_counts()
        st.plotly_chart(donut_chart(sc.index.tolist(), sc.values.tolist(), height=350),
                        width="stretch")

    with col_r:
        section_header("Experience Level")
        exp = df[config.COL_EXP_LEVEL].dropna().value_counts()
        ordered = [l for l in ["Entry","Mid","Senior","Lead"] if l in exp.index]
        exp = exp.reindex(ordered)
        ec = [config.COLORS["accent2"], config.COLORS["secondary"],
              config.COLORS["accent"], config.COLORS["primary"]]
        fig_e = go.Figure(go.Bar(
            x=exp.index, y=exp.values, marker_color=ec[:len(exp)],
            text=[f"{v:,}" for v in exp.values], textposition="outside",
            textfont=dict(size=11, color=config.COLORS["text_primary"]),
            cliponaxis=False,
            hovertemplate="<b>%{x}</b><br>%{y:,} postings<extra></extra>",
        ))
        fig_e.update_layout(showlegend=False, yaxis_title="Postings",
                            margin=dict(t=10, l=10, r=10, b=30), height=350)
        st.plotly_chart(fig_e, width="stretch")

    section_header("Seniority × Country Heatmap", "Top 15 countries")
    top15 = df[config.COL_COUNTRY].value_counts().nlargest(15).index.tolist()
    pivot = (df[df[config.COL_COUNTRY].isin(top15)]
             .groupby([config.COL_COUNTRY, config.COL_SENIORITY]).size()
             .unstack(fill_value=0))
    st.plotly_chart(heatmap_chart(pivot, height=420), width="stretch")

    col_e, col_e2 = st.columns(2)
    with col_e:
        section_header("Employment Type Mix")
        em = df[config.COL_EMP_NORM].value_counts().head(6)
        st.plotly_chart(donut_chart(em.index.tolist(), em.values.tolist(), height=350),
                        width="stretch")
    with col_e2:
        section_header("Seniority × Domain", "Stacked")
        top10d = df["Primary AI Domain"].value_counts().head(10).index.tolist()
        sd = (df[df["Primary AI Domain"].isin(top10d)]
              .groupby(["Primary AI Domain", config.COL_SENIORITY]).size()
              .reset_index(name="Count"))
        st.plotly_chart(grouped_bar(sd, "Primary AI Domain", "Count",
                                     config.COL_SENIORITY, barmode="stack", height=350),
                        width="stretch")

# ─── DOMAINS TAB ────────────────────────────────────────────────────────
with tab_dom:
    from utils.data_loader import get_domain_tags_series
    domain_tags = get_domain_tags_series(df).value_counts()
    explicit_rows = df[df[config.COL_AI_DOMAIN].notna()]

    render_kpi_grid([
        KPICard("Tag Coverage",  len(explicit_rows)/len(df), icon="🏷", format_fn=fmt_pct),
        KPICard("Unique Tags",   len(domain_tags), icon="🏷"),
        KPICard("Top Domain",    domain_tags.index[0] if len(domain_tags) else "—",
                icon="🥇", format_fn=lambda v: v),
        KPICard("Multi-Tag Posts", int(df[config.COL_AI_DOMAIN].dropna().str.contains(",").sum()),
                icon="🔀"),
    ], cols_per_row=4)
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    col_b, col_d = st.columns([3, 2])
    tag_df = domain_tags.reset_index(); tag_df.columns = ["AI Domain","Mentions"]
    with col_b:
        section_header("AI Domain Tag Frequency")
        st.plotly_chart(horizontal_bar(tag_df, "Mentions", "AI Domain",
                                       gradient=True, height=380),
                        width="stretch")
    with col_d:
        section_header("Domain Share")
        st.plotly_chart(donut_chart(tag_df["AI Domain"].tolist(),
                                    tag_df["Mentions"].tolist(), height=380),
                        width="stretch")

    section_header("Domain × Country Heatmap", "Top 15 countries")
    top15 = df[config.COL_COUNTRY].value_counts().nlargest(15).index.tolist()
    exploded = (explicit_rows[[config.COL_COUNTRY, config.COL_AI_DOMAIN]]
                .assign(**{config.COL_AI_DOMAIN: explicit_rows[config.COL_AI_DOMAIN].str.split(",")})
                .explode(config.COL_AI_DOMAIN))
    exploded[config.COL_AI_DOMAIN] = exploded[config.COL_AI_DOMAIN].str.strip()
    dc = (exploded[exploded[config.COL_COUNTRY].isin(top15)]
          .groupby([config.COL_COUNTRY, config.COL_AI_DOMAIN]).size()
          .unstack(fill_value=0))
    st.plotly_chart(heatmap_chart(dc, height=440, colorscale="Purples"), width="stretch")

st.divider()
download_csv_button(df, filename="companies_roles.csv", key="cr_dl")

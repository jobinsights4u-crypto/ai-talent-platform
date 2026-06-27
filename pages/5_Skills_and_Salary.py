"""Page 5 — Skills & Salary."""
from __future__ import annotations
import itertools
from collections import Counter
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import config
from charts.bar_charts import horizontal_bar, grouped_bar
from charts.misc_charts import box_plot, histogram_chart, heatmap_chart, treemap_chart
from charts.theme import register_theme
from components.download import download_csv_button
from components.kpi_cards import KPICard, render_kpi_grid
from components.sidebar import render_sidebar
from components.ui import inject_global_css, page_header, section_header, insight_box, window_badge
from utils.data_loader import filter_dataframe, get_90d, get_skills_series, load_data
from utils.formatters import fmt_pct

st.set_page_config(page_title=f"Skills & Salary · {config.APP_TITLE}",
                   page_icon="💰", layout=config.LAYOUT)
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

skills = get_skills_series(df)
sal = df[df[config.COL_SALARY_MID].notna()].copy()

page_header("💰", "Skills & Salary",
            f"{len(skills):,} skill mentions · {len(sal):,} salaried postings ({fmt_pct(len(sal)/len(df))} coverage)")
window_badge(); st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

tab_sk, tab_sal = st.tabs(["🛠 Skills", "💰 Salary"])

# ─── SKILLS TAB ─────────────────────────────────────────────────────────
with tab_sk:
    render_kpi_grid([
        KPICard("Skill Mentions",   len(skills),                icon="🛠"),
        KPICard("Unique Skills",    skills.nunique(),           icon="📚"),
        KPICard("#1 Skill",         skills.value_counts().index[0] if len(skills) else "—",
                icon="🥇", format_fn=lambda v: v),
        KPICard("Skills Coverage",  df[config.COL_SKILLS].notna().mean(),
                icon="📋", format_fn=fmt_pct),
    ], cols_per_row=4)
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    top_n = st.slider("How many skills to show", 10, 50, 25, key="sk_n")
    sk_df = skills.value_counts().head(top_n).reset_index()
    sk_df.columns = ["Skill","Mentions"]

    col_l, col_r = st.columns([3, 2])
    with col_l:
        section_header(f"Top {top_n} In-Demand Skills")
        # Tiered colours
        cols_tier = (
            [config.COLORS["accent"]] * min(3, top_n) +
            [config.COLORS["secondary"]] * min(7, max(0, top_n-3)) +
            [config.COLORS["accent2"]] * max(0, top_n-10)
        )[:top_n]
        fig_sk = go.Figure(go.Bar(
            x=sk_df["Mentions"], y=sk_df["Skill"], orientation="h",
            marker_color=cols_tier,
            text=[f"{v:,}" for v in sk_df["Mentions"]],
            textposition="outside",
            textfont=dict(size=11, color=config.COLORS["text_primary"]),
            cliponaxis=False,
            hovertemplate="<b>%{y}</b><br>Mentions: %{x:,}<extra></extra>",
        ))
        fig_sk.update_layout(yaxis=dict(autorange="reversed"),
                             showlegend=False, xaxis_title="Mentions",
                             margin=dict(t=10, l=10, r=60, b=30), height=560)
        st.plotly_chart(fig_sk, width="stretch")
    with col_r:
        section_header("Treemap View")
        st.plotly_chart(treemap_chart(sk_df.head(20), ["Skill"], "Mentions",
                                      height=560),
                        width="stretch")

    insight_box(
        f"The top 3 skills are <strong>{sk_df.iloc[0]['Skill']}</strong> ({sk_df.iloc[0]['Mentions']:,}), "
        f"<strong>{sk_df.iloc[1]['Skill']}</strong> ({sk_df.iloc[1]['Mentions']:,}), and "
        f"<strong>{sk_df.iloc[2]['Skill']}</strong> ({sk_df.iloc[2]['Mentions']:,})."
    )

    # Skills by domain
    section_header("Skills by AI Domain", "Top 5 skills per domain")
    dom_opts = sorted(df["Primary AI Domain"].dropna().unique())
    sel_doms = st.multiselect("Domains", dom_opts,
                              default=[d for d in ["GenAI","Machine Learning","Data Science","NLP","MLOps"]
                                       if d in dom_opts],
                              key="sk_doms")
    if sel_doms:
        rows = []
        for d in sel_doms:
            top5 = get_skills_series(df[df["Primary AI Domain"]==d]).value_counts().head(5)
            for sk,c in top5.items():
                rows.append({"AI Domain":d,"Skill":sk,"Mentions":c})
        if rows:
            ds = pd.DataFrame(rows)
            st.plotly_chart(grouped_bar(ds, "AI Domain", "Mentions", "Skill",
                                        barmode="group", height=400),
                            width="stretch")

    # Co-occurrence
    section_header("Skill Co-Occurrence", "How often top skills appear together")

    @st.cache_data(show_spinner=False)
    def _cooc(n: int = 15) -> pd.DataFrame:
        df2 = load_data(); df2 = get_90d(df2)
        pairs: Counter = Counter()
        for val in df2[config.COL_SKILLS].dropna():
            s = sorted({x.strip() for x in val.split(",") if x.strip()})
            for a,b in itertools.combinations(s, 2):
                pairs[(a,b)] += 1
        all_sk: Counter = Counter()
        for (a,b),c in pairs.items():
            all_sk[a]+=c; all_sk[b]+=c
        top = [s for s,_ in all_sk.most_common(n)]
        mat = pd.DataFrame(0, index=top, columns=top)
        for (a,b),c in pairs.items():
            if a in top and b in top:
                mat.loc[a,b]=c; mat.loc[b,a]=c
        return mat

    with st.spinner("Computing co-occurrence…"):
        co = _cooc(15)
    st.plotly_chart(heatmap_chart(co, colorscale="Purples", height=480), width="stretch")

# ─── SALARY TAB ─────────────────────────────────────────────────────────
with tab_sal:
    if sal.empty:
        st.info("No salary data for current filters."); st.stop()

    avg = sal[config.COL_SALARY_MID].mean()
    med = sal[config.COL_SALARY_MID].median()
    p25 = sal[config.COL_SALARY_MID].quantile(0.25)
    p75 = sal[config.COL_SALARY_MID].quantile(0.75)
    render_kpi_grid([
        KPICard("Average",    avg, icon="💰", format_fn=lambda v: f"${v:,.0f}"),
        KPICard("Median",     med, icon="📊", format_fn=lambda v: f"${v:,.0f}"),
        KPICard("25th Pct",   p25, icon="⬇",  format_fn=lambda v: f"${v:,.0f}"),
        KPICard("75th Pct",   p75, icon="⬆",  format_fn=lambda v: f"${v:,.0f}"),
        KPICard("Max",        sal[config.COL_SALARY_MID].max(), icon="🏆",
                format_fn=lambda v: f"${v:,.0f}"),
        KPICard("Min",        sal[config.COL_SALARY_MID].min(), icon="📉",
                format_fn=lambda v: f"${v:,.0f}"),
        KPICard("Coverage",   len(sal)/len(df), icon="📋", format_fn=fmt_pct),
        KPICard("Records",    len(sal), icon="🗂"),
    ], cols_per_row=4)
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        section_header("Salary Distribution", "USD mid-point")
        st.plotly_chart(histogram_chart(sal, config.COL_SALARY_MID, nbins=40, height=360),
                        width="stretch")
    with col2:
        section_header("Distribution (Log Scale)")
        st.plotly_chart(histogram_chart(sal, config.COL_SALARY_MID, nbins=40,
                                         log_x=True, height=360),
                        width="stretch")

    section_header("Salary by Country")
    cs = (sal.groupby(config.COL_COUNTRY)[config.COL_SALARY_MID]
          .agg(["median","mean","count"]).reset_index()
          .rename(columns={"median":"Median USD","mean":"Mean USD","count":"Sample"})
          .sort_values("Median USD"))
    cca, ccb = st.columns(2)
    with cca:
        st.plotly_chart(horizontal_bar(cs, "Median USD", config.COL_COUNTRY,
                                       colour=config.COLORS["success"], top_n=len(cs),
                                       text_format="${:,}", gradient=True, height=460),
                        width="stretch")
    with ccb:
        st.plotly_chart(box_plot(sal, config.COL_COUNTRY, config.COL_SALARY_MID,
                                 log_y=True, height=460),
                        width="stretch")
    top_c = cs.nlargest(1,"Median USD").iloc[0]
    insight_box(f"<strong>{top_c[config.COL_COUNTRY]}</strong> offers the highest median at "
                f"<strong>${top_c['Median USD']:,.0f}</strong> (sample: {int(top_c['Sample'])} postings).")

    # By seniority
    section_header("Salary by Seniority")
    ssa, ssb = st.columns(2)
    sen_s = (sal.groupby(config.COL_SENIORITY)[config.COL_SALARY_MID].median()
             .reset_index().rename(columns={config.COL_SALARY_MID:"Median USD"})
             .sort_values("Median USD"))
    with ssa:
        st.plotly_chart(horizontal_bar(sen_s, "Median USD", config.COL_SENIORITY,
                                       colour=config.COLORS["secondary"],
                                       text_format="${:,}", height=350),
                        width="stretch")
    with ssb:
        st.plotly_chart(box_plot(sal[sal[config.COL_SENIORITY].notna()],
                                 config.COL_SENIORITY, config.COL_SALARY_MID,
                                 log_y=True, height=350),
                        width="stretch")

    # By domain
    section_header("Salary by AI Domain")
    dsa, dsb = st.columns(2)
    dom_s = (sal[sal["Primary AI Domain"].notna()].groupby("Primary AI Domain")
             [config.COL_SALARY_MID].agg(["median","count"]).reset_index()
             .rename(columns={"median":"Median USD","count":"Sample"})
             .sort_values("Median USD"))
    with dsa:
        st.plotly_chart(horizontal_bar(dom_s, "Median USD", "Primary AI Domain",
                                       colour=config.COLORS["accent"],
                                       text_format="${:,}", height=400),
                        width="stretch")
    with dsb:
        st.plotly_chart(box_plot(sal[sal["Primary AI Domain"].notna()],
                                 "Primary AI Domain", config.COL_SALARY_MID,
                                 log_y=True, height=400),
                        width="stretch")

    # By remote
    section_header("Salary by Work Arrangement")
    rsa, rsb = st.columns(2)
    rs = sal[sal[config.COL_REMOTE].notna()]
    if not rs.empty:
        r_med = (rs.groupby(config.COL_REMOTE)[config.COL_SALARY_MID].median()
                 .reset_index().rename(columns={config.COL_SALARY_MID:"Median USD"})
                 .sort_values("Median USD"))
        with rsa:
            st.plotly_chart(horizontal_bar(r_med, "Median USD", config.COL_REMOTE,
                                           colour=config.COLORS["info"],
                                           text_format="${:,}", height=300),
                            width="stretch")
        with rsb:
            st.plotly_chart(box_plot(rs, config.COL_REMOTE, config.COL_SALARY_MID,
                                     log_y=True, height=300),
                            width="stretch")

    section_header("Salary Benchmark Table")
    st.dataframe(cs.sort_values("Median USD", ascending=False).reset_index(drop=True),
                 column_config={
                     "Median USD": st.column_config.NumberColumn("Median (USD)", format="$%,.0f"),
                     "Mean USD":   st.column_config.NumberColumn("Mean (USD)",   format="$%,.0f"),
                     "Sample":     st.column_config.NumberColumn("Sample Size"),
                 }, width="stretch")

st.divider()
download_csv_button(df, filename="skills_salary.csv", key="ss_dl")

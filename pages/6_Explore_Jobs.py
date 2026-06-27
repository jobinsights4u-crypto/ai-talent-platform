"""Page 6 — Explore Jobs: search and raw data table."""
from __future__ import annotations
import re
import pandas as pd
import streamlit as st

import config
from charts.theme import register_theme
from components.download import download_csv_button, download_excel_button
from components.sidebar import render_sidebar
from components.ui import inject_global_css, page_header, section_header, window_badge
from utils.data_loader import filter_dataframe, get_90d, load_data
from utils.formatters import truncate

st.set_page_config(page_title=f"Explore Jobs · {config.APP_TITLE}",
                   page_icon="🔍", layout=config.LAYOUT)
register_theme()

try:
    df_master = load_data()
except FileNotFoundError as exc:
    st.error(str(exc)); st.stop()

inject_global_css()
filters = render_sidebar(df_master)
df_all = filter_dataframe(df_master, **filters)

# Window toggle
win = st.radio("Data window", ["Last 90 Days (recommended)", "All time"],
               horizontal=True, key="ex_win")
df = get_90d(df_all) if win.startswith("Last") else df_all

page_header("🔍", "Explore Jobs",
            f"{len(df):,} postings · search by keyword or browse raw data")
if win.startswith("Last"): window_badge()
st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

tab_search, tab_data = st.tabs(["🔍 Job Search", "🗂 Data Table"])

# ─── SEARCH TAB ─────────────────────────────────────────────────────────
with tab_search:
    c1, c2 = st.columns([4, 1])
    with c1:
        query = st.text_input("Search query", placeholder='Search by keyword (e.g. "ML Engineer Python")',
                              key="srch_q", label_visibility="collapsed")
    with c2:
        field = st.selectbox("Search in",
                             ["Title + Skills + Desc","Title Only","Skills Only"], key="srch_f")

    fc1, fc2, fc3, fc4 = st.columns(4)
    with fc1:
        country_f = st.selectbox("Country",
                                  ["All"] + sorted(df[config.COL_COUNTRY].unique()), key="srch_co")
    with fc2:
        domain_f = st.selectbox("AI Domain",
                                 ["All"] + sorted(df["Primary AI Domain"].dropna().unique()),
                                 key="srch_dom")
    with fc3:
        remote_f = st.selectbox("Work Type",
                                 ["All"] + sorted(df[config.COL_REMOTE].dropna().unique()),
                                 key="srch_rem")
    with fc4:
        sort_by = st.selectbox("Sort",
                                ["Newest First","Salary High→Low","Company A–Z"], key="srch_sort")
    sal_only = st.checkbox("Only with salary data", key="srch_sal")

    def _search(frame, q, f):
        if not q.strip(): return frame
        pat = re.compile(re.escape(q.strip()), re.IGNORECASE)
        if f == "Title Only":
            return frame[frame[config.COL_TITLE].str.contains(pat, na=False)]
        if f == "Skills Only":
            return frame[frame[config.COL_SKILLS].str.contains(pat, na=False)]
        return frame[
            frame[config.COL_TITLE].str.contains(pat, na=False) |
            frame[config.COL_SKILLS].fillna("").str.contains(pat, na=False) |
            frame[config.COL_DESCRIPTION].str.contains(pat, na=False)
        ]

    results = _search(df, query, field)
    if country_f != "All": results = results[results[config.COL_COUNTRY]==country_f]
    if domain_f != "All":  results = results[results["Primary AI Domain"]==domain_f]
    if remote_f != "All":  results = results[results[config.COL_REMOTE]==remote_f]
    if sal_only:           results = results[results[config.COL_SALARY_MID].notna()]

    if sort_by == "Newest First":
        results = results.sort_values(config.COL_POSTED_DT, ascending=False)
    elif sort_by == "Salary High→Low":
        results = results.sort_values(config.COL_SALARY_MID, ascending=False, na_position="last")
    else:
        results = results.sort_values(config.COL_COMPANY, ascending=True, na_position="last")

    st.markdown(f"""
    <div style="background:white; border-radius:10px; padding:12px 18px;
                border:1px solid {config.COLORS['border']}; margin-bottom:14px;
                display:flex; justify-content:space-between; align-items:center;">
        <span style="font-weight:700; color:{config.COLORS['primary']};">{len(results):,} results</span>
        <span style="color:{config.COLORS['text_muted']}; font-size:0.82rem;">
            Sorted by {sort_by}
        </span>
    </div>
    """, unsafe_allow_html=True)

    if results.empty:
        st.info("No postings match. Try broadening your search.")
    else:
        pp = st.selectbox("Per page", [10, 25, 50], index=1, key="srch_pp")
        total_p = max(1, (len(results)-1)//pp + 1)
        page_n = st.number_input(f"Page (1–{total_p})", 1, total_p, 1, key="srch_pg")
        s = (page_n - 1) * pp
        page_df = results.iloc[s: s+pp]

        for _, row in page_df.iterrows():
            title = str(row.get(config.COL_TITLE,""))
            company = str(row.get(config.COL_COMPANY,"Unknown"))
            country = str(row.get(config.COL_COUNTRY,""))
            loc = str(row.get(config.COL_LOCATION,""))
            dom = str(row.get("Primary AI Domain",""))
            sen = str(row.get(config.COL_SENIORITY,""))
            rem = str(row.get(config.COL_REMOTE,""))
            skills_t = str(row.get(config.COL_SKILLS,""))
            sal = row.get(config.COL_SALARY_MID)
            posted = row.get(config.COL_POSTED_DT)
            desc = str(row.get(config.COL_DESCRIPTION,""))
            sal_s = f"${sal:,.0f}" if pd.notna(sal) else ""
            posted_s = posted.strftime("%d %b %Y") if pd.notna(posted) else ""

            with st.expander(f"**{truncate(title, 70)}**   ·   {company}   ·   {country}"):
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    badges = ""
                    for tag, c in [(dom, config.COLORS["secondary"]),
                                    (sen, config.COLORS["accent2"]),
                                    (rem, config.COLORS["teal"])]:
                        if tag and tag != "nan":
                            badges += f'<span style="background:{c}20; color:{c}; border:1px solid {c}50; border-radius:14px; padding:2px 9px; font-size:0.72rem; font-weight:600; margin-right:5px;">{tag}</span>'
                    if sal_s:
                        badges += f'<span style="background:#10B98120; color:#10B981; border:1px solid #10B98150; border-radius:14px; padding:2px 9px; font-size:0.72rem; font-weight:600;">💰 {sal_s}</span>'
                    if badges:
                        st.markdown(badges, unsafe_allow_html=True)
                        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
                    if skills_t and skills_t != "nan":
                        pills = " ".join(
                            f'<span style="background:#F0F4FF; border:1px solid #E2E8F0; border-radius:6px; padding:2px 8px; margin:2px; font-size:0.72rem; display:inline-block;">{s.strip()}</span>'
                            for s in skills_t.split(",") if s.strip()
                        )
                        st.markdown(f"**Skills:** {pills}", unsafe_allow_html=True)
                    preview = desc[:600].strip()
                    st.markdown(f"""<div style="font-size:0.83rem; color:#444; line-height:1.6;
                                border-left:3px solid {config.COLORS['secondary']}; padding-left:12px;
                                max-height:160px; overflow:auto; margin-top:6px;">{preview}{'…' if len(desc)>600 else ''}</div>""",
                                unsafe_allow_html=True)
                with col_b:
                    st.markdown(f"""
                    <div style="background:#F8FAFF; border-radius:8px; padding:12px;
                                border:1px solid {config.COLORS['border']}; font-size:0.82rem;">
                        <div style="font-weight:700; color:{config.COLORS['primary']};
                                    margin-bottom:8px;">Quick Info</div>
                        {'<div>📍 ' + loc + '</div>' if loc and loc != 'nan' else ''}
                        <div>🌍 {country}</div>
                        {'<div>📅 ' + posted_s + '</div>' if posted_s else ''}
                        {'<div>💰 ' + sal_s + '</div>' if sal_s else ''}
                    </div>
                    """, unsafe_allow_html=True)

        st.caption(f"Showing {s+1}–{min(s+pp, len(results))} of {len(results):,} · Page {page_n}/{total_p}")
        download_csv_button(
            results[[c for c in results.columns if c != config.COL_DESCRIPTION]],
            filename="search_results.csv", key="srch_dl")

# ─── DATA TABLE TAB ─────────────────────────────────────────────────────
with tab_data:
    section_header("Raw Data Browser")
    default_cols = [c for c in df.columns
                    if c not in (config.COL_DESCRIPTION, config.COL_POSTED_DATE)]
    sel_cols = st.multiselect("Columns", df.columns.tolist(),
                              default=default_cols, key="dt_cols")
    if not sel_cols:
        st.warning("Select at least one column."); st.stop()

    with st.expander("🔎 Column-level text filters"):
        text_filters = {}
        filterable = [c for c in sel_cols
                      if df[c].dtype == object or str(df[c].dtype) == "string"][:8]
        cf = st.columns(min(4, max(1, len(filterable))))
        for i, c in enumerate(filterable):
            with cf[i % 4]:
                v = st.text_input(f"`{c}`", key=f"dt_tf_{c}")
                if v: text_filters[c] = v

    fdf = df[sel_cols].copy()
    for c, v in text_filters.items():
        fdf = fdf[fdf[c].astype(str).str.contains(v, case=False, na=False)]

    sc = st.selectbox("Sort by", ["(None)"] + sel_cols, key="dt_sort")
    sa = st.checkbox("Ascending", True, key="dt_asc")
    if sc != "(None)":
        fdf = fdf.sort_values(sc, ascending=sa, na_position="last")

    rpp = st.selectbox("Rows per page", [25, 50, 100, 250], index=1, key="dt_rpp")
    total = len(fdf)
    pages = max(1, (total-1)//rpp + 1)
    page = st.number_input(f"Page (1–{pages})", 1, pages, 1, key="dt_pg")
    s = (page-1) * rpp

    st.markdown(f"Showing **{s+1}–{min(s+rpp, total):,}** of **{total:,}** records · Page {page}/{pages}")

    col_cfg = {}
    if config.COL_SALARY_MID in fdf.columns:
        col_cfg[config.COL_SALARY_MID] = st.column_config.NumberColumn("Salary Mid (USD)", format="$%,.0f")
    if config.COL_POSTED_DT in fdf.columns:
        col_cfg[config.COL_POSTED_DT] = st.column_config.DatetimeColumn("Posted", format="DD MMM YYYY")
    st.dataframe(fdf.iloc[s: s+rpp].reset_index(drop=True),
                 column_config=col_cfg, width="stretch", height=580)

    with st.expander("📊 Summary Statistics"):
        num_cols = fdf.select_dtypes(include="number").columns.tolist()
        if num_cols:
            st.dataframe(fdf[num_cols].describe().T, width="stretch")
        null_df = fdf.isnull().sum().reset_index()
        null_df.columns = ["Column", "Nulls"]
        null_df["Null %"] = (null_df["Nulls"]/len(fdf)*100).round(1)
        st.dataframe(null_df, width="stretch")

    section_header("Export Filtered Data")
    dl1, dl2 = st.columns(2)
    with dl1: download_csv_button(fdf, filename="export.csv", key="dt_csv")
    with dl2: download_excel_button(fdf, filename="export.xlsx", key="dt_xlsx")

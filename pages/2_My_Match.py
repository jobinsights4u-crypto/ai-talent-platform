"""Page 2 — My Match: Personalised job matching."""
from __future__ import annotations
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import config
from charts.theme import register_theme
from components.download import download_csv_button
from components.sidebar import render_sidebar
from components.ui import inject_global_css, page_header, section_header, insight_box, window_badge
from utils.data_loader import filter_dataframe, get_90d, get_skills_series, load_data
from utils.formatters import truncate
from utils.insights import job_match_score, predict_salary_simple

st.set_page_config(page_title=f"My Match · {config.APP_TITLE}",
                   page_icon="🎯", layout=config.LAYOUT)
register_theme()

try:
    df_master = load_data()
except FileNotFoundError as exc:
    st.error(str(exc)); st.stop()

inject_global_css()
filters = render_sidebar(df_master)
df_all = filter_dataframe(df_master, **filters)
df = get_90d(df_all)

page_header("🎯", "My Match",
            "Tell us about yourself — get personalised matches and a salary estimate")
window_badge(); st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

# ─── Profile form ────────────────────────────────────────────────────────
st.markdown(f"""
<div style="background:white; border:1px solid {config.COLORS['border']};
            border-radius:12px; padding:20px 24px; margin-bottom:16px;
            border-top:4px solid {config.COLORS['secondary']};">
    <div style="font-size:1.05rem; font-weight:700; color:{config.COLORS['primary']};
                margin-bottom:4px;">👤 Build Your Profile</div>
    <div style="color:{config.COLORS['text_muted']}; font-size:0.85rem;">
        We'll match you against {len(df):,} active postings and estimate your market salary.
    </div>
</div>
""", unsafe_allow_html=True)

all_skills_counts = get_skills_series(df).value_counts()
all_skills_options = sorted(all_skills_counts.index.tolist())

c1, c2 = st.columns(2)
with c1:
    user_skills = st.multiselect(
        "🛠 Your Skills (up to 15)", options=all_skills_options,
        default=["Python", "SQL"] if "Python" in all_skills_options else [],
        max_selections=15, placeholder="Type to search…", key="ms_skills",
    )
    user_country = st.selectbox(
        "🌍 Preferred Country",
        options=["Any"] + sorted(df[config.COL_COUNTRY].unique()), key="ms_country",
    )
with c2:
    user_seniority = st.selectbox(
        "👤 Seniority Level",
        options=["Any","Individual Contributor","Manager","Lead","Director","Executive"],
        key="ms_seniority",
    )
    user_domain = st.selectbox(
        "🤖 AI Domain Focus",
        options=["Any"] + sorted(df["Primary AI Domain"].dropna().unique()), key="ms_domain",
    )

user_remote = st.radio("🏠 Work Arrangement",
                       options=["Any","Remote","Hybrid","Onsite"],
                       horizontal=True, key="ms_remote")

if st.button("🔍  Find My Matches", type="primary"):
    if not user_skills:
        st.warning("Please add at least one skill.")
        st.stop()
    st.session_state["match_run"] = True

if st.session_state.get("match_run", False):
    st.divider()
    # Salary estimate
    section_header("💰 Your Estimated Market Salary")
    est = predict_salary_simple(df, country=user_country, seniority=user_seniority,
                                skills=user_skills, domain=user_domain)
    if est["median"] is None:
        st.info(f"Not enough data for this combo (sample {est['sample']}). Try broader filters.")
    else:
        cols = st.columns(4)
        labels = [("25th Pct", est["p25"], config.COLORS["info"]),
                  ("Median",   est["median"], config.COLORS["success"]),
                  ("75th Pct", est["p75"], config.COLORS["secondary"]),
                  ("Top 10%",  est["max"], config.COLORS["accent"])]
        for col, (lbl, val, c) in zip(cols, labels):
            with col:
                st.markdown(f"""
                <div style="background:white; border-radius:12px; padding:18px;
                            border:1px solid {config.COLORS['border']};
                            border-top:4px solid {c}; text-align:center;">
                    <div style="font-size:0.7rem; font-weight:700; text-transform:uppercase;
                                letter-spacing:0.07em; color:{config.COLORS['text_muted']};">{lbl}</div>
                    <div style="font-size:1.5rem; font-weight:700;
                                color:{config.COLORS['primary']}; margin-top:6px;">${val:,.0f}</div>
                </div>
                """, unsafe_allow_html=True)
        st.markdown(f"""<div style="font-size:0.78rem; color:{config.COLORS['text_muted']};
        text-align:center; margin-top:10px;">📊 Based on {est['sample']:,} matching salaried postings</div>""",
        unsafe_allow_html=True)

    # Compute matches
    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
    section_header("🎯 Your Top 20 Matches", "Ranked by overall fit")
    pool = df.copy()
    if user_remote != "Any":
        pool = pool[pool[config.COL_REMOTE] == user_remote]

    with st.spinner("Scoring postings…"):
        pool["Match Score"] = pool.apply(
            lambda r: job_match_score(r, user_skills, user_seniority, user_country, user_domain),
            axis=1)
    pool = pool.sort_values("Match Score", ascending=False)
    top_matches = pool.head(20)

    if top_matches.empty or top_matches["Match Score"].max() < 20:
        st.warning("No strong matches. Broaden your skills or filters.")
        st.stop()

    # Histogram
    fig_d = go.Figure(go.Histogram(
        x=pool[pool["Match Score"]>=20]["Match Score"], nbinsx=20,
        marker_color=config.COLORS["secondary"], opacity=0.88,
        hovertemplate="Score range: %{x}<br>Postings: %{y:,}<extra></extra>",
    ))
    fig_d.update_layout(title="📊 Score Distribution Across All Postings",
                        xaxis_title="Match Score", yaxis_title="Number of Postings",
                        height=240, margin=dict(t=44, b=30), bargap=0.05)
    st.plotly_chart(fig_d, width="stretch")

    st.markdown("#### 🌟 Top Matches")
    for rank, (_, row) in enumerate(top_matches.iterrows(), 1):
        score = row["Match Score"]
        title = str(row.get(config.COL_TITLE,""))
        company = str(row.get(config.COL_COMPANY,"Unknown"))
        country = str(row.get(config.COL_COUNTRY,""))
        loc = str(row.get(config.COL_LOCATION,""))
        sen = str(row.get(config.COL_SENIORITY,""))
        dom = str(row.get("Primary AI Domain",""))
        rem = str(row.get(config.COL_REMOTE,""))
        sal = row.get(config.COL_SALARY_MID)
        posted = row.get(config.COL_POSTED_DT)
        skills = str(row.get(config.COL_SKILLS,"") or "")

        score_c = config.COLORS["success"] if score>=70 else config.COLORS["warning"] if score>=50 else config.COLORS["info"]
        sal_s = f"${sal:,.0f}" if pd.notna(sal) else "—"
        posted_s = posted.strftime("%d %b") if pd.notna(posted) else ""

        user_set = {s.lower() for s in user_skills}
        post_skills = [s.strip() for s in skills.split(",") if s.strip()]
        matched = [s for s in post_skills if s.lower() in user_set]
        other = [s for s in post_skills if s.lower() not in user_set]
        matched_pills = " ".join(f'<span style="background:#10B98120; color:#10B981; border:1px solid #10B98150; border-radius:14px; padding:2px 9px; font-size:0.71rem; font-weight:600; margin:2px; display:inline-block;">✓ {s}</span>' for s in matched[:8])
        other_pills = " ".join(f'<span style="background:#F0F4FF; color:#64748B; border:1px solid #E2E8F0; border-radius:14px; padding:2px 9px; font-size:0.71rem; margin:2px; display:inline-block;">{s}</span>' for s in other[:6])

        st.markdown(f"""
        <div style="background:white; border-radius:12px; padding:18px 22px;
                    border:1px solid {config.COLORS['border']}; border-left:5px solid {score_c};
                    margin-bottom:10px; box-shadow:0 2px 6px rgba(15,31,61,0.05);">
            <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                <div style="flex:1;">
                    <div style="display:flex; align-items:center; gap:8px;">
                        <span style="background:{score_c}; color:white; font-weight:700;
                                     font-size:0.75rem; border-radius:20px; padding:3px 10px;">#{rank}</span>
                        <span style="font-weight:700; color:{config.COLORS['primary']};
                                     font-size:1rem;">{truncate(title,75)}</span>
                    </div>
                    <div style="color:{config.COLORS['text_muted']}; font-size:0.85rem; margin-top:4px;">
                        🏢 <strong>{company}</strong> · 📍 {loc}, {country} · 📅 {posted_s}
                    </div>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:2rem; font-weight:800; color:{score_c}; line-height:1;">{score:.0f}</div>
                    <div style="font-size:0.7rem; color:{config.COLORS['text_muted']}; text-transform:uppercase;
                                letter-spacing:0.06em; font-weight:600; margin-top:2px;">Match</div>
                    <div style="font-size:0.95rem; font-weight:700; color:{config.COLORS['primary']};
                                margin-top:6px;">💰 {sal_s}</div>
                </div>
            </div>
            <div style="margin-top:10px; display:flex; flex-wrap:wrap; gap:4px;">
                <span style="background:#6C3FC520; color:#6C3FC5; border:1px solid #6C3FC550;
                             border-radius:14px; padding:2px 9px; font-size:0.71rem; font-weight:600;">{dom}</span>
                <span style="background:#00B4D820; color:#00B4D8; border:1px solid #00B4D850;
                             border-radius:14px; padding:2px 9px; font-size:0.71rem; font-weight:600;">{sen}</span>
                <span style="background:#14B8A620; color:#14B8A6; border:1px solid #14B8A650;
                             border-radius:14px; padding:2px 9px; font-size:0.71rem; font-weight:600;">{rem}</span>
            </div>
            <div style="margin-top:8px;">{matched_pills} {other_pills}</div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()
    download_csv_button(
        top_matches[[config.COL_TITLE, config.COL_COMPANY, config.COL_COUNTRY,
                     "Primary AI Domain", config.COL_SENIORITY, config.COL_REMOTE,
                     config.COL_SALARY_MID, "Match Score", config.COL_POSTED_DT]],
        filename="my_top_matches.csv", key="mm_dl",
    )
else:
    insight_box("👆 Build your profile above and click <strong>Find My Matches</strong>. "
                "We'll score every active posting and estimate your salary.", icon="✨")

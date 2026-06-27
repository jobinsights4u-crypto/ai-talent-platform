"""
components/sidebar.py
---------------------
Dark-themed sidebar filter panel.
"""
from __future__ import annotations
import datetime
from typing import Optional
import pandas as pd
import streamlit as st
import config
from utils.data_loader import load_data
from utils.logger import get_logger

logger = get_logger(__name__)


@st.cache_data(show_spinner=False)
def _get_filter_options(total_rows: int) -> dict:
    df = load_data()
    return {
        "countries":   sorted(df[config.COL_COUNTRY].dropna().unique().tolist()),
        "domains":     sorted(df["Primary AI Domain"].dropna().unique().tolist()),
        "seniorities": sorted(df[config.COL_SENIORITY].dropna().unique().tolist()),
        "remote":      sorted(df[config.COL_REMOTE].dropna().unique().tolist()),
        "exp_levels":  [lv for lv in ["Entry", "Mid", "Senior", "Lead"]
                        if lv in df[config.COL_EXP_LEVEL].values],
        "emp_types":   sorted(df[config.COL_EMP_NORM].dropna().unique().tolist()),
        "date_min":    df[config.COL_POSTED_DT].dt.date.min(),
        "date_max":    df[config.COL_POSTED_DT].dt.date.max(),
    }


def render_sidebar(df: pd.DataFrame) -> dict:
    with st.sidebar:
        # Logo + title
        st.markdown(f"""
        <div style="padding: 8px 0 16px 0; text-align:center;">
            <div style="font-size: 2rem;">🤖</div>
            <div style="color:white; font-weight:700; font-size:1rem;
                        margin-top:6px; line-height:1.3;">
                AI Talent Intelligence
            </div>
            <div style="color:rgba(255,255,255,0.45); font-size:0.72rem;
                        margin-top:2px;">v{config.APP_VERSION}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        opts = _get_filter_options(len(df))

        st.markdown("### 🌍  Geography")
        countries = st.multiselect("Countries", options=opts["countries"],
                                   default=[], placeholder="All countries",
                                   key="sb_countries")

        st.markdown("### 🤖  AI Domain")
        domains = st.multiselect("Domain", options=opts["domains"],
                                 default=[], placeholder="All domains",
                                 key="sb_domains")

        st.markdown("### 👤  Role")
        seniorities = st.multiselect("Seniority", options=opts["seniorities"],
                                     default=[], placeholder="All seniorities",
                                     key="sb_seniority")
        exp_levels = st.multiselect("Experience", options=opts["exp_levels"],
                                    default=[], placeholder="All levels",
                                    key="sb_exp")

        st.markdown("### 🏠  Work Arrangement")
        remote_types = st.multiselect("Remote Type", options=opts["remote"],
                                      default=[], placeholder="All types",
                                      key="sb_remote")
        emp_types = st.multiselect("Employment", options=opts["emp_types"],
                                   default=[], placeholder="All types",
                                   key="sb_emp")

        st.markdown("### 📅  Date Range")
        date_min = opts["date_min"]
        date_max = opts["date_max"]
        date_range = st.date_input("Posting Date",
                                   value=(date_min, date_max),
                                   min_value=date_min, max_value=date_max,
                                   key="sb_dates")

        st.markdown("---")
        st.markdown(f"""
        <div style="text-align:center; color:rgba(255,255,255,0.4);
                    font-size:0.7rem; padding-bottom:8px;">
            {len(df):,} total records<br>
            📅 Last 90 days: primary window
        </div>
        """, unsafe_allow_html=True)

    if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
        dr = (date_range[0], date_range[1])
    else:
        dr = (date_min, date_max)

    return {
        "countries":    countries or None,
        "domains":      domains or None,
        "seniorities":  seniorities or None,
        "remote_types": remote_types or None,
        "exp_levels":   exp_levels or None,
        "emp_types":    emp_types or None,
        "date_range":   dr,
    }

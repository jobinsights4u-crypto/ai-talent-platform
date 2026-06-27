"""
utils/insights.py
-----------------
Higher-level analytical helpers: emerging signals, momentum analysis,
salary modelling, and comparative metrics.
All functions cached via st.cache_data.
"""
from __future__ import annotations
import pandas as pd
import streamlit as st
import config
from utils.data_loader import get_skills_series


@st.cache_data(show_spinner=False)
def emerging_skills(df: pd.DataFrame, recent_days: int = 30, min_recent: int = 30) -> pd.DataFrame:
    """
    Compare skill posting-rate in the recent window vs. the prior window.
    Returns DataFrame with columns: Skill, Recent, Prior, Recent Rate ‰, Prior Rate ‰, Δ %, Status.
    """
    cutoff = df[config.COL_POSTED_DT].max() - pd.Timedelta(days=recent_days)
    recent = df[df[config.COL_POSTED_DT] >= cutoff]
    prior  = df[df[config.COL_POSTED_DT] <  cutoff]

    r_skills = get_skills_series(recent).value_counts()
    p_skills = get_skills_series(prior).value_counts()
    r_total = max(1, len(recent))
    p_total = max(1, len(prior))

    rows = []
    for skill in r_skills.index:
        r_cnt = int(r_skills[skill])
        p_cnt = int(p_skills.get(skill, 0))
        if r_cnt < min_recent: continue
        r_rate = r_cnt / r_total * 1000
        p_rate = p_cnt / p_total * 1000 if p_cnt else 0
        delta = ((r_rate - p_rate) / p_rate * 100) if p_rate else (100 if r_rate else 0)
        rows.append({
            "Skill": skill, "Recent": r_cnt, "Prior": p_cnt,
            "Recent Rate ‰": round(r_rate, 1), "Prior Rate ‰": round(p_rate, 1),
            "Δ %": round(delta, 1),
        })
    out = pd.DataFrame(rows)
    if not out.empty:
        out["Status"] = out["Δ %"].apply(
            lambda v: "🔥 Hot" if v >= 50 else "📈 Rising" if v >= 10
            else "➡ Stable" if v >= -10 else "📉 Cooling"
        )
    return out.sort_values("Δ %", ascending=False).reset_index(drop=True)


@st.cache_data(show_spinner=False)
def accelerating_companies(df: pd.DataFrame, recent_days: int = 30, min_prior: int = 5) -> pd.DataFrame:
    """Find companies whose posting volume is growing the fastest."""
    cutoff = df[config.COL_POSTED_DT].max() - pd.Timedelta(days=recent_days)
    recent = df[df[config.COL_POSTED_DT] >= cutoff]
    prior  = df[df[config.COL_POSTED_DT] <  cutoff]

    r_co = recent.groupby(config.COL_COMPANY).size()
    p_co = prior.groupby(config.COL_COMPANY).size()

    rows = []
    for co in set(r_co.index) & set(p_co.index):
        if p_co[co] < min_prior: continue
        # Normalise prior to same window size as recent
        prior_days = (df[config.COL_POSTED_DT].max() - df[config.COL_POSTED_DT].min()).days - recent_days
        if prior_days <= 0: continue
        p_normalised = p_co[co] * (recent_days / prior_days)
        growth = (r_co[co] - p_normalised) / p_normalised * 100 if p_normalised else 0
        rows.append({
            config.COL_COMPANY: co, "Recent": int(r_co[co]), "Prior": int(p_co[co]),
            "Growth %": round(growth, 1),
        })
    out = pd.DataFrame(rows)
    return out.sort_values("Growth %", ascending=False).reset_index(drop=True)


@st.cache_data(show_spinner=False)
def skill_salary_premium(df: pd.DataFrame, min_count: int = 30) -> pd.DataFrame:
    """Return average salary by skill (only skills with ≥ min_count salaried postings)."""
    sal = df[df[config.COL_SALARY_MID].notna()].copy()
    sal["sk"] = sal[config.COL_SKILLS].fillna("").str.split(",")
    ex = sal.explode("sk")
    ex["sk"] = ex["sk"].str.strip()
    ex = ex[ex["sk"] != ""]
    grouped = ex.groupby("sk")[config.COL_SALARY_MID].agg(["mean", "median", "count"])
    grouped = grouped[grouped["count"] >= min_count].reset_index()
    grouped.columns = ["Skill", "Avg Salary", "Median Salary", "Postings"]

    # Premium vs market median
    market_median = sal[config.COL_SALARY_MID].median()
    grouped["Premium %"] = ((grouped["Median Salary"] - market_median) / market_median * 100).round(1)
    return grouped.sort_values("Avg Salary", ascending=False).reset_index(drop=True)


def predict_salary_simple(
    df: pd.DataFrame,
    country: str | None = None,
    seniority: str | None = None,
    skills: list[str] | None = None,
    domain: str | None = None,
) -> dict:
    """
    Lightweight salary estimator using filter-based segmentation.
    Returns dict with min/median/max/p25/p75/sample.
    """
    s = df[df[config.COL_SALARY_MID].notna()].copy()
    if country and country != "Any":   s = s[s[config.COL_COUNTRY] == country]
    if seniority and seniority != "Any": s = s[s[config.COL_SENIORITY] == seniority]
    if domain and domain != "Any":     s = s[s["Primary AI Domain"] == domain]
    if skills:
        pat = "|".join([f"(?i){sk}" for sk in skills])
        s = s[s[config.COL_SKILLS].fillna("").str.contains(pat, regex=True, na=False)]
    if len(s) < 5:
        return {"sample": len(s), "median": None, "p25": None, "p75": None,
                "min": None, "max": None, "mean": None}
    col = s[config.COL_SALARY_MID]
    return {
        "sample": len(s),
        "median": float(col.median()),
        "p25": float(col.quantile(0.25)),
        "p75": float(col.quantile(0.75)),
        "min": float(col.min()),
        "max": float(col.max()),
        "mean": float(col.mean()),
    }


def job_match_score(row: pd.Series, user_skills: list[str], user_seniority: str | None,
                    user_country: str | None, user_domain: str | None) -> float:
    """
    Compute a 0-100 match score between a job posting and a candidate profile.

    Weights:
        Skills match  : 50 %
        Country match : 15 %
        Domain match  : 15 %
        Seniority match: 20 %
    """
    score = 0.0
    user_skills_clean = {s.strip().lower() for s in user_skills if s.strip()}

    # Skills
    if user_skills_clean:
        post_skills = str(row.get(config.COL_SKILLS, "") or "").lower()
        post_skill_set = {s.strip() for s in post_skills.split(",") if s.strip()}
        if post_skill_set:
            overlap = len(user_skills_clean & post_skill_set)
            score += 50 * (overlap / max(1, len(user_skills_clean)))
        # Also reward keyword matches in title/desc
        title = str(row.get(config.COL_TITLE, "") or "").lower()
        for sk in user_skills_clean:
            if sk in title and sk not in post_skill_set:
                score += 2  # small bonus

    # Country
    if user_country and user_country != "Any":
        if str(row.get(config.COL_COUNTRY, "")) == user_country: score += 15
    else:
        score += 7.5

    # Domain
    if user_domain and user_domain != "Any":
        if str(row.get("Primary AI Domain", "")) == user_domain: score += 15
    else:
        score += 7.5

    # Seniority
    if user_seniority and user_seniority != "Any":
        if str(row.get(config.COL_SENIORITY, "")) == user_seniority: score += 20
    else:
        score += 10

    return min(100.0, round(score, 1))


@st.cache_data(show_spinner=False)
def market_pulse_summary(df: pd.DataFrame, recent_days: int = 7) -> dict:
    """Generate a 'pulse' dictionary of headline market signals."""
    cutoff = df[config.COL_POSTED_DT].max() - pd.Timedelta(days=recent_days)
    recent = df[df[config.COL_POSTED_DT] >= cutoff]
    prior  = df[(df[config.COL_POSTED_DT] >= cutoff - pd.Timedelta(days=recent_days)) &
                (df[config.COL_POSTED_DT] <  cutoff)]
    wow = ((len(recent) - len(prior)) / len(prior) * 100) if len(prior) else 0
    return {
        "recent_postings": len(recent),
        "prior_postings":  len(prior),
        "wow_pct":         round(wow, 1),
        "active_companies": recent[config.COL_COMPANY].nunique(),
        "active_countries": recent[config.COL_COUNTRY].nunique(),
        "top_skill":       get_skills_series(recent).value_counts().index[0] if len(recent) else "—",
        "top_country":     recent[config.COL_COUNTRY].value_counts().index[0] if len(recent) else "—",
        "top_company":     recent[config.COL_COMPANY].value_counts().index[0] if len(recent) else "—",
    }

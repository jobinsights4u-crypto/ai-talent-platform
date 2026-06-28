"""
utils/data_loader.py
--------------------
Data loading, enrichment, caching, and filtering for the platform.
Primary analysis window: last 90 days (where ~80% of data lives).
"""
from __future__ import annotations
import datetime
from pathlib import Path
from typing import Optional

import pandas as pd
import streamlit as st

import config
from utils.logger import get_logger

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

@st.cache_data(show_spinner="Loading dataset …", ttl=3600)
def load_data(filepath: Optional[str | Path] = None) -> pd.DataFrame:
    """
    Load the AI Jobs dataset. Prefers parquet (fast + small), falls back to xlsx.
    Returns memory-optimised DataFrame with categoricals and truncated descriptions.
    """
    parquet_path = config.DATA_DIR / "ai_jobs.parquet"
    xlsx_path    = Path(filepath) if filepath else config.DATA_FILE

    if parquet_path.exists():
        logger.info("Reading dataset from %s", parquet_path)
        df = pd.read_parquet(parquet_path)
    elif xlsx_path.exists():
        logger.info("Reading dataset from %s", xlsx_path)
        df = pd.read_excel(xlsx_path, sheet_name=config.SHEET_NAME, engine="openpyxl")
        # Truncate descriptions to keep memory in check
        if config.COL_DESCRIPTION in df.columns:
            df[config.COL_DESCRIPTION] = (
                df[config.COL_DESCRIPTION].fillna("").astype(str).str.slice(0, 800)
            )
    else:
        raise FileNotFoundError(
            f"Dataset not found at '{parquet_path}' or '{xlsx_path}'.\n"
            "Place 'ai_jobs.parquet' or 'Artificial_Intelligence_Master_Enriched.xlsx' "
            "in the /data folder."
        )

    logger.info("Raw shape: %s rows × %s cols", *df.shape)
    df = _enrich(df)
    df = _optimise_memory(df)
    logger.info("Enriched shape: %s rows × %s cols (%.1f MB)",
                df.shape[0], df.shape[1],
                df.memory_usage(deep=True).sum() / 1024 / 1024)
    return df


def _optimise_memory(df: pd.DataFrame) -> pd.DataFrame:
    """Convert low-cardinality columns to categorical to save memory."""
    cat_cols = [
        config.COL_COUNTRY, config.COL_CURRENCY, config.COL_EMP_TYPE,
        config.COL_EXP_LEVEL, config.COL_SENIORITY, config.COL_REMOTE,
        config.COL_CONFIDENCE, config.COL_EMP_NORM,
        "Primary AI Domain", "Domain Source", "Region", config.COL_POSTED_MONTH,
        config.COL_POSTED_WEEK,
    ]
    for col in cat_cols:
        if col in df.columns and df[col].dtype == "object":
            df[col] = df[col].astype("category")
    return df


def get_90d(df: pd.DataFrame) -> pd.DataFrame:
    """Return the last-90-day slice (primary analysis window)."""
    cutoff = pd.Timestamp(config.ANALYSIS_START_DATE)
    return df[df[config.COL_POSTED_DT] >= cutoff].copy()


# ---------------------------------------------------------------------------
# Enrichment pipeline
# ---------------------------------------------------------------------------

def _enrich(df: pd.DataFrame) -> pd.DataFrame:
    df = _parse_dates(df)
    df = _normalise_employment_type(df)
    df = _add_salary_usd(df)
    df = _clean_strings(df)
    df = _extract_primary_domain(df)
    df = _add_region(df)
    return df


def _parse_dates(df: pd.DataFrame) -> pd.DataFrame:
    df[config.COL_POSTED_DT] = (
        pd.to_datetime(df[config.COL_POSTED_DATE], unit="ms", utc=True)
        .dt.tz_convert(None)
    )
    df[config.COL_POSTED_MONTH] = df[config.COL_POSTED_DT].dt.to_period("M").astype(str)
    df[config.COL_POSTED_WEEK]  = df[config.COL_POSTED_DT].dt.to_period("W").astype(str)
    return df


def _normalise_employment_type(df: pd.DataFrame) -> pd.DataFrame:
    mapping = config.EMPLOYMENT_TYPE_MAP
    def _map(val):
        if pd.isna(val): return "Unknown"
        return mapping.get(str(val).strip().lower(), str(val).strip())
    df[config.COL_EMP_NORM] = df[config.COL_EMP_TYPE].apply(_map)
    return df


def _add_salary_usd(df: pd.DataFrame) -> pd.DataFrame:
    fx = config.FX_TO_USD
    def _mid_usd(row):
        lo, hi, ccy = row[config.COL_SALARY_MIN], row[config.COL_SALARY_MAX], row[config.COL_CURRENCY]
        if pd.isna(lo) or pd.isna(hi) or pd.isna(ccy): return None
        rate = fx.get(str(ccy).strip().upper())
        if rate is None: return None
        usd = ((lo + hi) / 2) * rate
        return round(usd, 2) if 5_000 <= usd <= 1_500_000 else None
    df[config.COL_SALARY_MID] = df.apply(_mid_usd, axis=1)
    return df


def _clean_strings(df: pd.DataFrame) -> pd.DataFrame:
    """Strip whitespace from object columns (skips already-categorical ones)."""
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].str.strip()
    return df


def _extract_primary_domain(df: pd.DataFrame) -> pd.DataFrame:
    _INFER: list[tuple[str, str]] = [
        ("generative", "GenAI"), ("gen ai", "GenAI"), ("genai", "GenAI"),
        ("llm", "GenAI"), ("large language", "GenAI"), ("prompt", "GenAI"), ("gpt", "GenAI"),
        ("machine learning", "Machine Learning"), ("ml engineer", "Machine Learning"),
        ("deep learning", "Machine Learning"),
        ("data scientist", "Data Science"), ("data science", "Data Science"),
        ("analytics", "Data Science"),
        ("computer vision", "Computer Vision"), ("image recogni", "Computer Vision"),
        ("object detect", "Computer Vision"),
        ("nlp", "NLP"), ("natural language", "NLP"), ("text mining", "NLP"),
        ("mlops", "MLOps"), ("model deploy", "MLOps"),
        ("robot", "Robotics"), ("autonom", "Robotics"),
        ("responsible ai", "AI Ethics"), ("ai ethics", "AI Ethics"),
        ("business intellig", "BI / Analytics"), ("bi analyst", "BI / Analytics"),
        ("data engineer", "Data Engineering"), ("data platform", "Data Engineering"),
        ("software engineer", "Software Engineering"), ("backend", "Software Engineering"),
        ("frontend", "Software Engineering"),
        ("devops", "DevOps / Cloud"), ("cloud", "DevOps / Cloud"), ("kubernetes", "DevOps / Cloud"),
        ("product manager", "Product / Strategy"),
        ("project manager", "Project Management"),
        ("sales", "Sales / BD"), ("account execut", "Sales / BD"),
        ("business develop", "Sales / BD"),
    ]
    def _first_tag(val):
        if pd.isna(val): return None
        parts = [p.strip() for p in str(val).split(",")]
        return parts[0] if parts else None
    def _infer(title):
        if pd.isna(title): return "Other"
        t = str(title).lower()
        for kw, dom in _INFER:
            if kw in t: return dom
        return "Other"
    explicit = df[config.COL_AI_DOMAIN].apply(_first_tag)
    df["Primary AI Domain"] = explicit.where(explicit.notna(), df[config.COL_TITLE].apply(_infer))
    df["Domain Source"] = explicit.notna().map({True: "Explicit", False: "Inferred"})
    return df




def _add_region(df: pd.DataFrame) -> pd.DataFrame:
    df["Region"] = df[config.COL_COUNTRY].map(config.COUNTRY_REGION).fillna("Other")
    return df


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------

def get_skills_series(df: pd.DataFrame) -> pd.Series:
    return (
        df[config.COL_SKILLS].dropna()
        .str.split(",").explode().str.strip()
        .loc[lambda s: s != ""]
    )


def get_domain_tags_series(df: pd.DataFrame) -> pd.Series:
    return (
        df[config.COL_AI_DOMAIN].dropna()
        .str.split(",").explode().str.strip()
        .loc[lambda s: s != ""]
    )


def filter_dataframe(
    df: pd.DataFrame,
    countries: list[str] | None = None,
    domains: list[str] | None = None,
    seniorities: list[str] | None = None,
    remote_types: list[str] | None = None,
    exp_levels: list[str] | None = None,
    emp_types: list[str] | None = None,
    date_range: tuple[datetime.date, datetime.date] | None = None,
    domain_source: list[str] | None = None,
) -> pd.DataFrame:
    mask = pd.Series(True, index=df.index)
    if countries:     mask &= df[config.COL_COUNTRY].isin(countries)
    if domains:       mask &= df["Primary AI Domain"].isin(domains)
    if seniorities:   mask &= df[config.COL_SENIORITY].isin(seniorities)
    if remote_types:  mask &= df[config.COL_REMOTE].isin(remote_types)
    if exp_levels:    mask &= df[config.COL_EXP_LEVEL].isin(exp_levels)
    if emp_types:     mask &= df[config.COL_EMP_NORM].isin(emp_types)
    if date_range:
        start, end = date_range
        posted = df[config.COL_POSTED_DT].dt.date
        mask &= (posted >= start) & (posted <= end)
    if domain_source and "Domain Source" in df.columns:
        mask &= df["Domain Source"].isin(domain_source)
    return df[mask].copy()


def safe_divide(n: float, d: float, default: float = 0.0) -> float:
    return n / d if d else default

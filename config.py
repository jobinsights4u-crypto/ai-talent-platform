"""
config.py
---------
Central configuration for the AI Talent Intelligence Platform.
All constants, paths, colour palettes, and thresholds live here.
"""

from __future__ import annotations
import os
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).parent
DATA_DIR  = BASE_DIR / "data"
ASSETS_DIR = BASE_DIR / "assets"

_env_file = os.environ.get("AI_TALENT_DATA_FILE")
DATA_FILE: Path = (
    Path(_env_file) if _env_file
    else DATA_DIR / "Artificial_Intelligence_Master_Enriched.xlsx"
)
SHEET_NAME = "AI Jobs"

# ---------------------------------------------------------------------------
# App metadata
# ---------------------------------------------------------------------------
APP_TITLE   = "AI Talent Intelligence Platform"
APP_ICON    = "🤖"
APP_VERSION = "2.0.0"
LAYOUT      = "wide"

# ---------------------------------------------------------------------------
# Analysis window (most data is last 90 days)
# ---------------------------------------------------------------------------
ANALYSIS_WINDOW_DAYS = 90
ANALYSIS_START_DATE  = "2026-03-29"   # ~90 days before dataset max date

# ---------------------------------------------------------------------------
# Colour palette — premium navy / violet / cyan / coral
# ---------------------------------------------------------------------------
COLORS = {
    "primary":        "#0F1F3D",
    "secondary":      "#6C3FC5",
    "accent":         "#F04E23",
    "accent2":        "#00B4D8",
    "success":        "#10B981",
    "warning":        "#F59E0B",
    "danger":         "#EF4444",
    "info":           "#3B82F6",
    "purple_light":   "#A78BFA",
    "teal":           "#14B8A6",
    "light_bg":       "#F0F4FF",
    "card_bg":        "#FFFFFF",
    "border":         "#E2E8F0",
    "text_primary":   "#0F1F3D",
    "text_muted":     "#64748B",
    "gradient_start": "#0F1F3D",
    "gradient_end":   "#6C3FC5",
}

CHART_PALETTE = [
    "#6C3FC5", "#00B4D8", "#F04E23", "#10B981",
    "#F59E0B", "#3B82F6", "#EF4444", "#14B8A6",
    "#A78BFA", "#0F1F3D", "#FB923C", "#34D399",
    "#60A5FA", "#F472B6", "#FBBF24", "#4ADE80",
]

SEQUENTIAL_PALETTE = ["#E8E0FF", "#C4B0F0", "#A078E0", "#6C3FC5", "#4A2090", "#2D1060"]

PLOTLY_TEMPLATE = "ati_theme"

# ---------------------------------------------------------------------------
# Column names
# ---------------------------------------------------------------------------
COL_COUNTRY      = "Country"
COL_TITLE        = "Job Title"
COL_COMPANY      = "Company"
COL_LOCATION     = "Location"
COL_SALARY_MIN   = "Salary Min"
COL_SALARY_MAX   = "Salary Max"
COL_CURRENCY     = "Currency"
COL_EMP_TYPE     = "Employment Type"
COL_POSTED_DATE  = "Posted Date"
COL_DESCRIPTION  = "Job Description"
COL_SKILLS       = "Skills"
COL_AI_DOMAIN    = "AI Domain"
COL_EXP_LEVEL    = "Experience Level"
COL_SENIORITY    = "Seniority"
COL_REMOTE       = "Remote Type"
COL_CONFIDENCE   = "Extraction Confidence"

# Derived
COL_POSTED_DT    = "Posted DateTime"
COL_POSTED_MONTH = "Posted Month"
COL_POSTED_WEEK  = "Posted Week"
COL_SALARY_MID   = "Salary Mid (USD)"
COL_EMP_NORM     = "Employment Type (Normalised)"

# ---------------------------------------------------------------------------
# Employment-type normalisation map
# ---------------------------------------------------------------------------
EMPLOYMENT_TYPE_MAP: dict[str, str] = {
    "full-time": "Full-time", "fulltime": "Full-time", "permanent": "Full-time",
    "part-time": "Part-time", "parttime": "Part-time",
    "contract": "Contract", "internship": "Internship",
    "freelance": "Freelance", "temporary": "Temporary",
    "apprenticeship": "Apprenticeship",
    "tempo integral": "Full-time", "período integral": "Full-time",
    "efetivo clt": "Full-time", "autônomo / pj": "Freelance",
    "estágio": "Internship", "temporário": "Temporary",
    "meio período": "Part-time", "intermitente (freelance)": "Freelance",
    "tiempo completo": "Full-time", "jornada completa": "Full-time",
    "contrato indefinido": "Full-time", "contrato en prácticas": "Internship",
    "tirocinio formativo/stage": "Internship",
    "temps plein": "Full-time", "cdi": "Full-time", "cdd": "Contract",
    "stage": "Internship", "alternance": "Apprenticeship",
    "temps partiel": "Part-time",
    "vollzeit": "Full-time", "teilzeit": "Part-time",
    "festanstellung": "Full-time", "praktikum": "Internship",
    "pełny etat": "Full-time", "umowa o pracę stałą": "Full-time",
    "tempo pieno": "Full-time", "tempo indeterminato": "Full-time",
    "全职": "Full-time", "兼职": "Part-time", "实习": "Internship",
    "终身制": "Full-time", "临时工": "Temporary", "合同工": "Contract",
    "teljes munkaidő": "Full-time", "heltid": "Full-time",
    "دوام كامل": "Full-time", "100%": "Full-time",
}

# ---------------------------------------------------------------------------
# FX → USD
# ---------------------------------------------------------------------------
FX_TO_USD: dict[str, float] = {
    "USD": 1.00, "GBP": 1.27, "EUR": 1.08, "AUD": 0.65, "CAD": 0.73,
    "CHF": 1.11, "SGD": 0.74, "INR": 0.012, "BRL": 0.18, "CNY": 0.14,
    "JPY": 0.0067, "MXN": 0.058, "PLN": 0.25, "SEK": 0.095, "HUF": 0.0028,
    "MYR": 0.23, "AED": 0.27, "SAR": 0.27, "QAR": 0.27, "KWD": 3.25, "MAD": 0.10,
}

# ---------------------------------------------------------------------------
# Country → ISO-3
# ---------------------------------------------------------------------------
COUNTRY_ISO3: dict[str, str] = {
    "Australia": "AUS", "Brazil": "BRA", "Canada": "CAN", "China": "CHN",
    "France": "FRA", "Germany": "DEU", "Hungary": "HUN", "India": "IND",
    "Italy": "ITA", "Japan": "JPN", "Kuwait": "KWT", "Malaysia": "MYS",
    "Mexico": "MEX", "Morocco": "MAR", "Poland": "POL", "Portugal": "PRT",
    "Qatar": "QAT", "Saudi Arabia": "SAU", "Singapore": "SGP", "Spain": "ESP",
    "Sweden": "SWE", "Switzerland": "CHE", "United Arab Emirates": "ARE",
    "United Kingdom": "GBR", "United States": "USA",
}

# Country regions for grouping
COUNTRY_REGION: dict[str, str] = {
    "Australia": "Asia-Pacific", "Singapore": "Asia-Pacific",
    "China": "Asia-Pacific", "Japan": "Asia-Pacific", "Malaysia": "Asia-Pacific",
    "India": "Asia-Pacific",
    "France": "Europe", "Germany": "Europe", "Hungary": "Europe",
    "Italy": "Europe", "Poland": "Europe", "Portugal": "Europe",
    "Spain": "Europe", "Sweden": "Europe", "Switzerland": "Europe",
    "United Kingdom": "Europe",
    "Brazil": "Americas", "Canada": "Americas", "Mexico": "Americas",
    "United States": "Americas",
    "Kuwait": "Middle East & Africa", "Morocco": "Middle East & Africa",
    "Qatar": "Middle East & Africa", "Saudi Arabia": "Middle East & Africa",
    "United Arab Emirates": "Middle East & Africa",
}

LOG_LEVEL  = "INFO"
LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"

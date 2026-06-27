[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://ai-talent-platform.streamlit.app/)

# 🤖 AI Talent Intelligence Platform

Enterprise-grade Streamlit dashboard for analysing global AI job market dynamics.

---

## Features

| Module | Description |
|---|---|
| 📊 Executive Dashboard | High-level KPIs, geographic overview, domain/seniority mix |
| 🌍 Geographic Intelligence | World map, country drill-down, remote-work breakdown |
| 🏢 Company Intelligence | Top employers, company drill-down, multi-country footprint |
| 👤 Role Intelligence | Job titles, seniority/experience distribution, employment type |
| 🛠 Skills Intelligence | Top skills, domain/country breakdown, co-occurrence matrix |
| 💰 Salary Intelligence | USD-normalised benchmarks by country/domain/seniority |
| 📈 Hiring Trends | Monthly trend, rolling averages, domain/country time-series |
| 🔍 Job Search | Full-text search with ranked, paginated, expandable results |
| 🗂 Data Explorer | Filterable sortable table with CSV/Excel export |

---

## Quick Start

### 1. Clone / copy the project

```bash
git clone <repo-url>
cd ai_talent_platform
```

### 2. Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Add the dataset

Place `Artificial_Intelligence_Master_Enriched.xlsx` inside the `/data` folder:

```
ai_talent_platform/
└── data/
    └── Artificial_Intelligence_Master_Enriched.xlsx
```

### 4. Run

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## Project Structure

```
ai_talent_platform/
├── app.py                          # Main entry point (landing page)
├── config.py                       # All constants, paths, palette, column names
├── requirements.txt
├── README.md
│
├── pages/
│   ├── 1_Executive_Dashboard.py
│   ├── 2_Geographic_Intelligence.py
│   ├── 3_Company_Intelligence.py
│   ├── 4_Role_Intelligence.py
│   ├── 5_Skills_Intelligence.py
│   ├── 6_Salary_Intelligence.py
│   ├── 7_Hiring_Trends.py
│   ├── 8_Job_Search.py
│   └── 9_Data_Explorer.py
│
├── utils/
│   ├── data_loader.py              # Load, enrich, cache, filter helpers
│   ├── formatters.py               # Number/currency/label formatting
│   └── logger.py                   # Logging factory
│
├── components/
│   ├── sidebar.py                  # Global sidebar filter panel
│   ├── kpi_cards.py                # Reusable KPI metric cards
│   └── download.py                 # CSV/Excel download buttons
│
├── charts/
│   ├── theme.py                    # Custom Plotly theme registration
│   ├── bar_charts.py               # Horizontal/vertical/grouped bar factories
│   ├── map_charts.py               # Choropleth and geo scatter factories
│   └── misc_charts.py             # Line, pie, box, treemap, heatmap, scatter
│
├── taxonomy/
│   └── domains.py                  # AI domain taxonomy and keyword mapping
│
├── data/
│   └── Artificial_Intelligence_Master_Enriched.xlsx
│
└── .streamlit/
    └── config.toml                 # Theme and server settings
```

---

## Dataset

- **15,069 rows × 16 columns** of AI job postings
- **25 countries**: Australia, Brazil, Canada, China, France, Germany, Hungary, India, Italy, Japan, Kuwait, Malaysia, Mexico, Morocco, Poland, Portugal, Qatar, Saudi Arabia, Singapore, Spain, Sweden, Switzerland, UAE, UK, USA
- **Key fields**: Country, Job Title, Company, Location, Salary Min/Max, Currency, Employment Type, Posted Date, Job Description, Skills, AI Domain, Experience Level, Seniority, Remote Type

### Data Enrichment Applied

| Field | Transformation |
|---|---|
| Posted Date | Millisecond epoch → UTC datetime |
| Employment Type | Multilingual → canonical English |
| Salary | Min/Max mid-point, FX-converted to USD |
| AI Domain | Multi-tag → primary single tag |
| Skills | Comma-separated → explodable Series |

---

## Configuration

All constants live in `config.py`:

- `DATA_FILE` — path to Excel file (override with `AI_TALENT_DATA_FILE` env var)
- `COLORS` — brand colour palette
- `CHART_PALETTE` — Plotly colour sequence
- `FX_TO_USD` — approximate FX conversion rates
- `COUNTRY_ISO3` — country name → ISO-3 codes for choropleth
- `EMPLOYMENT_TYPE_MAP` — multilingual → English normalisation

---

## Architecture Principles

- **Single source of truth**: all config in `config.py`, all data access through `utils/data_loader.py`
- **Caching**: `@st.cache_data` on data load + filter-option computation (1-hour TTL)
- **Modular charts**: every chart is a pure function in `charts/` returning a `go.Figure`
- **Reusable components**: sidebar, KPI cards, download buttons in `components/`
- **Type hints throughout**: PEP 8 compliant, fully documented with docstrings
- **Error handling**: graceful FileNotFoundError with actionable user message

---

## Extending the Platform

### Add a new page
1. Create `pages/10_My_New_Page.py`
2. Import `load_data`, `filter_dataframe`, `render_sidebar` from the existing utils
3. Use chart factories from `charts/` — no raw Plotly boilerplate needed

### Add a new chart type
Add a factory function to the appropriate module in `charts/` and return a `go.Figure`.

### Change the colour palette
Edit `COLORS` and `CHART_PALETTE` in `config.py` — the theme propagates automatically.

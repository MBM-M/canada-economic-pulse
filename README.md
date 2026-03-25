# Canada's Economic Pulse 📊

An interactive data analysis of wages, housing costs, and employment trends across Canada (2014–2024), using Statistics Canada open data.

**Live app:** [your-app-name.streamlit.app](#) *(add link after deploying)*

---

## Key Findings

- **Wages vs. Housing:** Nationally, wage growth slightly outpaced shelter CPI by 2024 (wage index ~138 vs. shelter ~135), but the gap narrowed sharply after 2020 — and the national average masks significant provincial inequality.
- **Provincial divergence:** Prairie provinces were hit hardest — Manitoba (+10.6 pts), Alberta (+9.7 pts), and Saskatchewan (+5.0 pts) all saw shelter costs outpace wage growth since 2014. Atlantic Canada and Quebec fared better, with wages pulling ahead of shelter costs.
- **Post-COVID labour shift:** The strongest employment growth from 2019→2024 was in Professional, scientific and technical services (+27%), Public administration (+24.8%), and Finance and insurance (+19.3%) — reflecting a structural shift toward knowledge-economy and public-sector work.
- **Sectors still lagging:** Agriculture (-21.1%), Fishing, hunting and trapping (-11.5%), Forestry and logging (-10.1%), and Retail trade (-1.7%) all remain below pre-COVID employment levels as of 2024.

---

## Project Structure

```
CstatCan/
├── 01_analysis.ipynb        # Exploratory analysis + all 3 charts
├── clean_data.py            # Cleans and processes raw StatCan CSVs
├── fetch_data.py            # Downloads raw CSVs from StatCan API
├── processed/               # Clean analysis-ready CSVs (git-ignored)
│   ├── wages_vs_cpi.csv
│   ├── wages_annual.csv
│   ├── wages_monthly.csv
│   ├── cpi_annual.csv
│   ├── cpi_monthly.csv
│   ├── employment_annual.csv
│   └── employment_monthly.csv
├── raw/                     # Raw StatCan CSVs (git-ignored)
│   ├── employment.csv
│   ├── cpi.csv
│   └── wages.csv
├── requirements.txt
└── README.md
```

---

## Data Sources

All data from [Statistics Canada](https://www150.statcan.gc.ca) open data, retrieved via the [StatCan Web Data Service API](https://www.statcan.gc.ca/en/developers).

| Table | Description |
|-------|-------------|
| [14-10-0023-01](https://www150.statcan.gc.ca/t1/tbl1/en/table!downloadTbl/csvDownload/14100023-eng.zip) | Employment by industry, Canada (annual) |
| [18-10-0005-01](https://www150.statcan.gc.ca/t1/tbl1/en/table!downloadTbl/csvDownload/18100005-eng.zip) | Consumer Price Index — All-items & Shelter, by province |
| [14-10-0064-01](https://www150.statcan.gc.ca/t1/tbl1/en/table!downloadTbl/csvDownload/14100064-eng.zip) | Average hourly wage rate, by province |

---

## Setup & Running Locally

```bash
# 1. Clone the repo
git clone https://github.com/yourusername/canada-economic-pulse.git
cd canada-economic-pulse

# 2. Install dependencies
pip install -r requirements.txt

# 3. Download raw data (one-time, ~470MB total)
python fetch_data.py

# 4. Clean and process data
python clean_data.py

# 5. Open the notebook in VS Code
# File → Open → 01_analysis.ipynb → Run All
```

---

## Tools Used

- **Python / Pandas** — data wrangling and analysis
- **Plotly** — interactive charts
- **Jupyter / VS Code** — exploratory analysis
- **Statistics Canada Web Data Service** — open government data
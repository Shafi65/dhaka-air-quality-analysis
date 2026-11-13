# Dhaka Air Quality Analysis (2017–2023)

End-to-end analysis of 7 years of hourly PM2.5 data from the U.S. Embassy in Dhaka, Bangladesh: a Python **ETL pipeline** loading into **DuckDB**, exploratory analysis in Jupyter, and an interactive **Tableau dashboard**.

**[→ View the interactive Tableau dashboard](https://public.tableau.com/views/TableauVisualizations_17343956476190/AverageAQIovertheyears?:showVizHome=no)**

## Key findings

All figures use real readings only (imputed hours excluded). The queries are in [`sql/queries.sql`](sql/queries.sql).

- **Air quality is getting worse:** average AQI rose from **145 in 2017 to 172 in 2023**, into the "Unhealthy" range, and it has risen every year since 2020 (148), the lowest year since 2017, during the COVID-19 lockdowns. Both 2017 and 2023 have almost complete data (2.9% and 0.5% of hours missing). 2018 is not comparable with other years, because most of its monsoon readings are missing (see Limitations).
- **The worst days are getting worse too:** the worst day of each year, by daily average AQI, rose from 339 in 2017 to 404 in 2023, and it has risen every year since 2020. Both values are in the "Hazardous" range.
- **Strong seasonality:** NowCast PM2.5 averages about 174 μg/m³ in December-February, peaking in January (~197), and falls to 31-71 μg/m³ from April to October.
- **"Unhealthy" is the most common category** (37.5% of hours), and 57% of all hours are "Unhealthy" or worse. "Good" is the rarest, at 2.4%.
- **Nights are worse than days:** average AQI is 165 between 18:00 and 06:00, against 151 during the day.

## Architecture

```
raw CSVs (7 years, hourly)  →  sql/etl.py  →  cleaned CSV + DuckDB (air_quality table)  →  sql/queries.sql
                                                      ↓
                              notebooks (EDA, seasonal decomposition, MongoDB demo)
                                                      ↓
                              Tableau dashboard (trends, seasonality, AQI distribution)
```

### ETL pipeline (`sql/etl.py`)

- **Extract**: merges 7 yearly CSVs (58,171 hourly rows; 61,344 once the timeline is made continuous)
- **Transform**: deduplicates timestamps, drops invalid/suspect sensor readings, reindexes to a continuous hourly timeline, replaces `-999` sensor placeholders, imputes gaps using month+hour group means (flagging every imputed hour in `aqi_imputed`), derives AQI categories and a 7-day (168h) rolling average
- **Load**: writes a cleaned CSV and loads an `air_quality` table into DuckDB for SQL querying

### SQL analysis (`sql/queries.sql`)

Six DuckDB queries: data completeness by year, yearly average AQI with year-on-year change (`LAG`), monthly seasonality, AQI category shares, day vs night, and the three worst days of each year (`RANK` over a daily rollup). `sql/run_queries.py` runs them all.

### Notebooks

- **`AIR QUALITY DATASET.ipynb`** — EDA: AQI trends over time, seasonal decomposition, correlation heatmaps, concentration-vs-AQI relationships
- **`AirQualityMongoDB.ipynb`** — the same dataset in MongoDB: CRUD operations, filtered queries, and aggregations

## Dataset

Hourly PM2.5 measurements, 2017–2023. Source: [AirNow — U.S. embassies and consulates](https://www.airnow.gov/international/us-embassies-and-consulates/#Bangladesh$Dhaka) (AirNow, 2024).

| Column | Description |
|---|---|
| DateTime | Hourly timestamp (index) |
| NowCast Conc. | NowCast PM2.5 concentration (μg/m³) |
| AQI | Air Quality Index value |
| AQI Category | Good / Moderate / Unhealthy for Sensitive Groups / Unhealthy / Very Unhealthy / Hazardous |
| Raw Conc. | Unadjusted PM2.5 concentration (μg/m³) |
| QC Name | Sensor quality-control flag (Valid / Invalid / Suspect) |
| aqi_imputed | True where the AQI value was filled in rather than measured |
| AQI_7Day_RollingAvg | 168-hour rolling average of AQI |
| Site, Parameter, Year, Month, Day, Hour, Conc. Unit, Duration | Measurement metadata |

## Project structure

```
dhaka-air-quality-analysis/
├── datasets/          # Raw yearly CSVs + cleaned output
├── notebooks/         # EDA + MongoDB notebooks
├── sql/               # ETL pipeline (pandas → DuckDB) + analysis queries
├── images/            # Reference images
└── requirements.txt
```

## How to run

```bash
git clone https://github.com/Shafi65/dhaka-air-quality-analysis.git
cd dhaka-air-quality-analysis
pip install -r requirements.txt

# 1. Build the cleaned dataset + DuckDB database
python sql/etl.py

# 2. Run the SQL analysis
python sql/run_queries.py

# 3. Explore the notebooks
jupyter notebook "notebooks/AIR QUALITY DATASET.ipynb"
```

## Limitations

- **About 6% of hours are imputed**, using month×hour averages pooled across all seven years. That pulls each year towards the overall average, so the findings use real readings only (`aqi_imputed = false`).
- **2018 is not comparable with other years.** September and October 2018 have no real readings at all, and half of August is missing. These are low-pollution monsoon months, so 2018's real-reading average (163.9) is biased upwards, while the imputed average (154.4) is pulled towards the multi-year mean. Neither is a fair yearly figure.
- **The Tableau dashboard and the EDA notebook include imputed hours.** The notebook does its own cleaning, with the same imputation but no flag, so its yearly averages run from 146 in 2017 to 171 in 2023.
- **`aqi_imputed` covers AQI only.** Gaps in raw concentration are filled the same way but not flagged.
- **The correlation heatmap in the notebook** compares NowCast, raw concentration, AQI and the AQI rolling average. These are calculated from one another, so their high correlation is expected and is not a finding.

## Tech stack

Python · pandas · NumPy · DuckDB (SQL) · MongoDB · statsmodels · seaborn/matplotlib · Tableau

## Contact

Shafi Hussain · [LinkedIn](https://www.linkedin.com/in/shafi-hussain-b03631251/) · shafi.hussain65@gmail.com

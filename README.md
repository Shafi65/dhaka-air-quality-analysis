# Dhaka Air Quality Analysis (2017–2023)

End-to-end analysis of 7 years of hourly PM2.5 data from the U.S. Embassy in Dhaka, Bangladesh: a Python **ETL pipeline** loading into **DuckDB**, exploratory analysis in Jupyter, and an interactive **Tableau dashboard**.

**[→ View the interactive Tableau dashboard](https://public.tableau.com/views/TableauVisualizations_17343956476190/AverageAQIovertheyears?:showVizHome=no)**

## Key findings

- **Air quality is steadily worsening**: average AQI rose from **146 in 2017 to 171 in 2023** — a sustained upward trend into the "Unhealthy" range.
- **Strong seasonality**: PM2.5 concentration peaks in **winter (avg NowCast ~178)**, drops by half or more during the monsoon months (April–October), and climbs again in November–December.
- The majority of all hourly readings from 2017–2023 fall in the **"Unhealthy" AQI category**; "Good" is the rarest category in the entire dataset.
- Pollution is consistently **higher at night** than during the day.

## Architecture

```
raw CSVs (7 years, hourly)  →  sql/etl.py  →  cleaned CSV + DuckDB (air_quality table)
                                                      ↓
                              notebooks (EDA, seasonal decomposition, MongoDB demo)
                                                      ↓
                              Tableau dashboard (trends, seasonality, AQI distribution)
```

### ETL pipeline (`sql/etl.py`)

- **Extract**: merges 7 yearly CSVs (~61k hourly rows)
- **Transform**: deduplicates timestamps, drops invalid/suspect sensor readings, reindexes to a continuous hourly timeline, replaces `-999` sensor placeholders, imputes gaps using month+hour group means, derives AQI categories and a 7-day (168h) rolling average
- **Load**: writes a cleaned CSV and loads an `air_quality` table into DuckDB for SQL querying

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
| AQI_7Day_RollingAvg | 168-hour rolling average of AQI |
| Site, Parameter, Year, Month, Day, Hour, Conc. Unit, Duration | Measurement metadata |

## Project structure

```
dhaka-air-quality-analysis/
├── datasets/          # Raw yearly CSVs + cleaned output
├── notebooks/         # EDA + MongoDB notebooks
├── sql/               # ETL pipeline (pandas → DuckDB)
├── images/            # Reference images
└── requirements.txt
```

## How to run

```bash
git clone https://github.com/Shafi65/dhaka-air-quality-analysis.git
cd dhaka-air-quality-analysis
pip install -r requirements.txt duckdb

# 1. Build the cleaned dataset + DuckDB database
python sql/etl.py

# 2. Explore the analysis
jupyter notebook "notebooks/AIR QUALITY DATASET.ipynb"
```

## Tech stack

Python · pandas · NumPy · DuckDB (SQL) · MongoDB · statsmodels · seaborn/matplotlib · Tableau

## Contact

Shafi Hussain · [LinkedIn](https://www.linkedin.com/in/shafi-hussain-b03631251/) · shafi.hussain65@gmail.com

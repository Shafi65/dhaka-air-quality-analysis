import os
import pandas as pd
import duckdb

DATASETS_DIR = os.path.join(os.path.dirname(__file__), "..", "datasets")
DB_PATH = os.path.join(os.path.dirname(__file__), "air_quality.db")
CLEANED_CSV_PATH = os.path.join(DATASETS_DIR, "cleaned_airqualityDhaka_dataset.csv")

AQI_CATEGORIES = [
    (0,   50,          "Good"),
    (51,  100,         "Moderate"),
    (101, 150,         "Unhealthy for Sensitive Groups"),
    (151, 200,         "Unhealthy"),
    (201, 300,         "Very Unhealthy"),
    (301, float("inf"),"Hazardous"),
]


def extract():
    files = sorted([
        os.path.join(DATASETS_DIR, f)
        for f in os.listdir(DATASETS_DIR)
        if f.startswith("Dhaka_PM2.5_") and f.endswith(".csv")
    ])
    print(f"Found {len(files)} CSV files. Loading...")
    df = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
    print(f"Extracted {len(df):,} rows.")
    return df


def transform(df):
    # 1. Drop duplicate timestamps
    df = df.drop_duplicates(subset="Date (LT)")

    # 2. Remove invalid or suspect sensor readings
    df = df[~df["QC Name"].isin(["Invalid", "Suspect"])]

    # 3. Parse the date string and reindex to a complete hourly timeline
    df["Date (LT)"] = pd.to_datetime(df["Date (LT)"], format="%Y-%m-%d %I:%M %p")
    full_range = pd.date_range(
        start=df["Date (LT)"].min(),
        end=df["Date (LT)"].max(),
        freq="h"
    )
    df = df.set_index("Date (LT)").reindex(full_range)
    df.index.name = "DateTime"

    # 4. Replace -999 sensor placeholder with NaN
    for col in ["NowCast Conc.", "AQI", "Raw Conc."]:
        df[col] = df[col].replace(-999, float("nan"))

    # 5. Fill gaps in categorical columns using neighbouring values
    for col in ["Site", "Parameter", "Conc. Unit", "Duration", "QC Name"]:
        df[col] = df[col].ffill().bfill()

    # 6. Recalculate date parts from the new continuous index
    df["Year"]  = df.index.year
    df["Month"] = df.index.month
    df["Day"]   = df.index.day
    df["Hour"]  = df.index.hour

    # 7. Fill missing concentrations with the mean for that month+hour combination
    for col in ["NowCast Conc.", "AQI", "Raw Conc."]:
        df[col] = df.groupby(["Month", "Hour"])[col].transform(
            lambda x: x.fillna(x.mean())
        )

    # 8. Assign AQI category from AQI value
    def assign_category(aqi):
        if pd.isna(aqi):
            return float("nan")
        for low, high, label in AQI_CATEGORIES:
            if low <= aqi <= high:
                return label
        return float("nan")

    df["AQI Category"] = df["AQI"].apply(assign_category)
    df["AQI Category"] = df.groupby(["Month", "Hour"])["AQI Category"].transform(
        lambda x: x.ffill().bfill()
    )

    # 9. 7-day (168-hour) rolling average of AQI
    df["AQI_7Day_RollingAvg"] = df["AQI"].rolling(window=168, min_periods=1).mean()

    # 10. Reset index so DateTime becomes a column, then rename for SQL
    df = df.reset_index()
    df = df.rename(columns={
        "NowCast Conc.":     "nowcast_conc",
        "AQI Category":      "aqi_category",
        "Raw Conc.":         "raw_conc",
        "Conc. Unit":        "conc_unit",
        "QC Name":           "qc_name",
        "AQI_7Day_RollingAvg": "aqi_7day_rolling_avg",
    })

    print(f"Transformed data: {len(df):,} rows, {len(df.columns)} columns.")
    return df


def load(df):
    df.to_csv(CLEANED_CSV_PATH, index=False)
    print(f"Cleaned CSV saved to: {CLEANED_CSV_PATH}")

    con = duckdb.connect(DB_PATH)
    con.execute("DROP TABLE IF EXISTS air_quality")
    con.execute("CREATE TABLE air_quality AS SELECT * FROM df")
    row_count = con.execute("SELECT COUNT(*) FROM air_quality").fetchone()[0]
    con.close()

    print(f"DuckDB database created at:       {DB_PATH}")
    print(f"Table 'air_quality' loaded with   {row_count:,} rows.")


if __name__ == "__main__":
    df = extract()
    df = transform(df)
    load(df)
    print("\nDone. Run sql/run_queries.py to execute queries.")

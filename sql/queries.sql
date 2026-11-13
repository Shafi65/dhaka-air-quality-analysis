-- Analysis queries over the air_quality table built by sql/etl.py.
-- Run all of them with:  python sql/run_queries.py
--
-- Rule used throughout: compare years, months and hours on REAL readings only
-- (aqi_imputed = false). Imputed hours are filled with multi-year averages, so
-- including them pulls every year towards the overall mean.

-- 1. Data completeness: how much of each year is real readings vs imputed?
SELECT
    Year,
    count(*)                                        AS hours,
    count(*) FILTER (WHERE NOT aqi_imputed)         AS real_hours,
    round(100.0 * avg(aqi_imputed::INT), 1)         AS pct_imputed
FROM air_quality
WHERE Year BETWEEN 2017 AND 2023
GROUP BY Year
ORDER BY Year;

-- 2. Yearly average AQI on real readings, with the change from the year before
SELECT
    Year,
    round(avg(AQI), 1)                                              AS avg_aqi,
    round(avg(AQI) - lag(avg(AQI)) OVER (ORDER BY Year), 1)         AS change_vs_prior_year
FROM air_quality
WHERE NOT aqi_imputed AND Year BETWEEN 2017 AND 2023
GROUP BY Year
ORDER BY Year;

-- 3. Seasonality: average PM2.5 (NowCast) by month across all years
SELECT
    Month,
    round(avg(nowcast_conc), 1)     AS avg_pm25,
    round(avg(AQI), 1)              AS avg_aqi
FROM air_quality
WHERE NOT aqi_imputed AND Year BETWEEN 2017 AND 2023
GROUP BY Month
ORDER BY Month;

-- 4. Share of hours in each AQI category
SELECT
    aqi_category,
    count(*)                                            AS hours,
    round(100.0 * count(*) / sum(count(*)) OVER (), 1)  AS pct_of_hours
FROM air_quality
WHERE NOT aqi_imputed AND Year BETWEEN 2017 AND 2023
GROUP BY aqi_category
ORDER BY hours DESC;

-- 5. Day vs night (night = 18:00 to 05:59)
SELECT
    CASE WHEN Hour BETWEEN 6 AND 17 THEN 'Day (06-18)' ELSE 'Night (18-06)' END AS period,
    round(avg(AQI), 1)  AS avg_aqi
FROM air_quality
WHERE NOT aqi_imputed AND Year BETWEEN 2017 AND 2023
GROUP BY period
ORDER BY period;

-- 6. The three worst days of each year (by average real-reading AQI)
WITH daily AS (
    SELECT
        CAST(DateTime AS DATE)  AS day,
        Year,
        avg(AQI)                AS avg_aqi,
        count(*)                AS real_hours
    FROM air_quality
    WHERE NOT aqi_imputed AND Year BETWEEN 2017 AND 2023
    GROUP BY CAST(DateTime AS DATE), Year
    HAVING count(*) >= 18          -- skip days with too few real readings
),
ranked AS (
    SELECT *, rank() OVER (PARTITION BY Year ORDER BY avg_aqi DESC) AS rnk
    FROM daily
)
SELECT Year, rnk, day, round(avg_aqi, 1) AS avg_aqi, real_hours
FROM ranked
WHERE rnk <= 3
ORDER BY Year, rnk;

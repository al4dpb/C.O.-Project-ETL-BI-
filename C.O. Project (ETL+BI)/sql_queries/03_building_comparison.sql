-- Building A vs B Comparison: Latest Month
-- Compare performance between buildings

SELECT
    building,
    total_sqft AS "Total SqFt",
    occupied_sqft AS "Occupied SqFt",
    ROUND(occupancy_pct, 2) AS "Occupancy %",
    suite_count AS "Total Suites",
    vacant_count AS "Vacant Suites",
    own_use_count AS "Own-Use Suites",
    revenue_sqft AS "Revenue SqFt"
FROM building_kpi_monthly
WHERE month = (
    SELECT MAX(month)
    FROM building_kpi_monthly
    WHERE month IS NOT NULL
)
ORDER BY building;

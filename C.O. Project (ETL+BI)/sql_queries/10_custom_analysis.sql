-- Custom Analysis Template
-- Copy and modify this query for ad-hoc analysis

-- Example 1: Find high-value opportunities
SELECT
    suite_id,
    building,
    sqft,
    sqft * 30.00 AS "Potential Annual Revenue @ $30/SF"
FROM dim_suite
WHERE sqft > 500
ORDER BY sqft DESC;

-- Example 2: Calculate average suite size by building
SELECT
    building,
    COUNT(*) AS "Suite Count",
    ROUND(AVG(sqft), 0) AS "Avg SqFt",
    ROUND(SUM(sqft), 0) AS "Total SqFt"
FROM dim_suite
GROUP BY building
ORDER BY building;

-- Example 3: Year-over-year comparison (when you have historical data)
-- SELECT
--     EXTRACT(YEAR FROM month) AS year,
--     EXTRACT(MONTH FROM month) AS month_num,
--     ROUND(AVG(occupancy_pct), 2) AS "Avg Occupancy %",
--     ROUND(AVG(price_per_sf_yr), 2) AS "Avg $/SF/Year"
-- FROM prop_kpi_monthly
-- WHERE month IS NOT NULL
-- GROUP BY EXTRACT(YEAR FROM month), EXTRACT(MONTH FROM month)
-- ORDER BY year DESC, month_num DESC;

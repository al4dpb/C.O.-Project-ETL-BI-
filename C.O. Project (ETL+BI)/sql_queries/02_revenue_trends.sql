-- Revenue Trends: Monthly Revenue and Collection Performance
-- Shows last 6 months of revenue data

SELECT
    month,
    rent_base AS "Rent Base",
    collected AS "Collected",
    uncollected AS "Uncollected",
    collection_rate_pct AS "Collection %",
    ROUND((collected / rent_base) * 100, 2) AS "Collection Rate (Calc)"
FROM fact_rent_monthly
WHERE month IS NOT NULL
    AND rent_base IS NOT NULL
ORDER BY month DESC
LIMIT 6;

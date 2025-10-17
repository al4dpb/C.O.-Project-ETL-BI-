-- Collection Rate Analysis: Payment Performance
-- Track collection efficiency over time

SELECT
    month,
    rent_base AS "Rent Base",
    collected AS "Collected",
    uncollected AS "Uncollected",
    ROUND(collection_rate_pct, 1) AS "Collection %",
    -- Flag months with issues
    CASE
        WHEN collection_rate_pct < 95 THEN '⚠️ Below Target'
        WHEN collection_rate_pct >= 100 THEN '✅ Perfect'
        ELSE '✓ Good'
    END AS "Status"
FROM fact_rent_monthly
WHERE month IS NOT NULL
    AND rent_base IS NOT NULL
ORDER BY month DESC;

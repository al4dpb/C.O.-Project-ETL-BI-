-- Occupancy History: 12 Month Trend
-- Track occupancy percentage over time

SELECT
    month,
    ROUND(occupancy_pct, 2) AS "Occupancy %",
    leased_sqft AS "Leased SqFt",
    total_property_sqft AS "Total SqFt",
    ROUND(price_per_sf_yr, 2) AS "Avg $/SF/Year"
FROM prop_kpi_monthly
WHERE month IS NOT NULL
    AND occupancy_pct IS NOT NULL
ORDER BY month DESC;

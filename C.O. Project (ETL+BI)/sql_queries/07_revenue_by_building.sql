-- Revenue Distribution by Building
-- Analyze revenue split between Building A and B

WITH building_revenue AS (
    SELECT
        b.building,
        b.month,
        b.occupied_sqft,
        b.revenue_sqft,
        -- Estimate revenue based on sqft ratio
        f.collected * (b.revenue_sqft::FLOAT / p.revenue_sqft) AS estimated_revenue
    FROM building_kpi_monthly b
    JOIN fact_rent_monthly f ON b.month = f.month
    JOIN prop_kpi_monthly p ON b.month = p.month
    WHERE b.month = (
        SELECT MAX(month)
        FROM building_kpi_monthly
        WHERE month IS NOT NULL
    )
    AND f.collected IS NOT NULL
)
SELECT
    building AS "Building",
    ROUND(occupied_sqft, 0) AS "Occupied SqFt",
    ROUND(estimated_revenue, 2) AS "Est. Revenue",
    ROUND(estimated_revenue / occupied_sqft, 2) AS "Revenue per SqFt"
FROM building_revenue
ORDER BY building;

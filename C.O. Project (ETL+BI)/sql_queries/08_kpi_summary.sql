-- Executive KPI Summary: One-Page Dashboard
-- All key metrics in a single view

WITH latest_month AS (
    SELECT MAX(month) as max_month
    FROM prop_kpi_monthly
    WHERE month IS NOT NULL AND collected IS NOT NULL
)
SELECT
    -- Time
    p.month AS "Report Month",

    -- Occupancy Metrics
    ROUND(p.occupancy_pct, 1) AS "Occupancy %",
    p.leased_sqft AS "Leased SqFt",
    p.total_property_sqft AS "Total SqFt",

    -- Revenue Metrics
    p.collected AS "Revenue Collected",
    p.rent_base AS "Rent Base",
    ROUND(p.collection_rate_pct, 1) AS "Collection Rate %",
    p.accounts_receivable AS "AR",

    -- Pricing
    ROUND(p.price_per_sf_yr, 2) AS "Avg $/SF/Year",

    -- Building Split
    (SELECT occupied_sqft FROM building_kpi_monthly
     WHERE building = 'A' AND month = p.month) AS "Building A SqFt",
    (SELECT occupied_sqft FROM building_kpi_monthly
     WHERE building = 'B' AND month = p.month) AS "Building B SqFt",

    -- Suite Counts
    (SELECT SUM(suite_count) FROM building_kpi_monthly
     WHERE month = p.month) AS "Total Suites",
    (SELECT SUM(vacant_count) FROM building_kpi_monthly
     WHERE month = p.month) AS "Vacant Suites"

FROM prop_kpi_monthly p
CROSS JOIN latest_month lm
WHERE p.month = lm.max_month;

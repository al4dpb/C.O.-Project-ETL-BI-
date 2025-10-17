-- Property Overview: Latest Month KPIs
-- Shows current occupancy, revenue, and key metrics

SELECT
    month,
    occupancy_pct AS "Occupancy %",
    leased_sqft AS "Leased SqFt",
    total_property_sqft AS "Total SqFt",
    collected AS "Revenue Collected",
    rent_base AS "Rent Base",
    collection_rate_pct AS "Collection Rate %",
    price_per_sf_yr AS "Price $/SF/Year",
    accounts_receivable AS "AR (Uncollected)"
FROM prop_kpi_monthly
WHERE month IS NOT NULL
    AND collected IS NOT NULL
ORDER BY month DESC
LIMIT 1;

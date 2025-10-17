-- Vacant Suites: Available for Lease
-- Find all vacant suites with details

SELECT
    s.suite_id AS "Suite",
    s.building AS "Building",
    s.sqft AS "SqFt",
    COALESCE(
        (SELECT AVG(rent_psf_yr)
         FROM dim_suite s2
         WHERE s2.building = s.building),
        0
    ) AS "Avg $/SF/Yr (Building)"
FROM dim_suite s
WHERE NOT EXISTS (
    SELECT 1
    FROM dim_tenant t
    WHERE t.tenant_name LIKE '%Vacant%'
    AND t.tenant_id IN (
        SELECT tenant_id
        FROM dim_tenant
        WHERE tenant_name = 'Vacante'
    )
)
ORDER BY s.building, s.suite_id;

-- Alternative: Show all suites with status
SELECT
    suite_id AS "Suite",
    building AS "Building",
    sqft AS "SqFt"
FROM dim_suite
ORDER BY building, suite_id;

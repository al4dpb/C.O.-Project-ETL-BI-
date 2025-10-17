-- Tenant Roster: All Current Tenants
-- List all tenants with suite details

SELECT
    t.tenant_name AS "Tenant",
    CASE
        WHEN t.is_own_use THEN 'Own-Use'
        ELSE 'Leased'
    END AS "Status",
    COUNT(*) AS "# Suites"
FROM dim_tenant t
GROUP BY t.tenant_name, t.is_own_use
ORDER BY
    CASE WHEN t.is_own_use THEN 1 ELSE 0 END,
    t.tenant_name;

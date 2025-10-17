-- Fact: Monthly rent collections
with dashboard as (
    select * from {{ ref('stg_dashboard_monthly') }}
)

select
    month,
    rent_base,
    collected,
    uncollected,
    leased_sqft,
    price_per_sf_yr,
    -- Calculated fields
    case
        when rent_base > 0 then (collected / rent_base) * 100
        else 0
    end as collection_rate_pct,
    collected + uncollected as total_billed
from dashboard
order by month

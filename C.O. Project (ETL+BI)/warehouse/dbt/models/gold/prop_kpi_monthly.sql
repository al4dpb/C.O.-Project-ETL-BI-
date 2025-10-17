{{
    config(
        materialized='table'
    )
}}

-- Gold: Property-level monthly KPIs (V2 with own-use toggle & NOI)
-- Toggle: Set var('exclude_own_use', true/false) in dbt
{% set exclude_own_use = var('exclude_own_use', false) %}

with dashboard_data as (
    select * from {{ ref('stg_dashboard_monthly') }}
),

lease_data as (
    select * from {{ ref('stg_lease_rate') }}
),

-- Calculate sqft metrics with own-use toggle
sqft_calcs as (
    select
        as_of_month,
        9917 as total_property_sqft,
        sum(case
            when {% if exclude_own_use %}not is_own_use{% else %}true{% endif %}
            then sqft
            else 0
        end) as effective_sqft,
        sum(case
            when is_vacant then sqft
            else 0
        end) as vacant_sqft,
        sum(case
            when is_own_use then sqft
            else 0
        end) as own_use_sqft
    from lease_data
    group by as_of_month
),

kpis as (
    select
        d.as_of_month,
        d.month,
        d.rent_base,
        d.collected,
        d.uncollected,
        d.leased_sqft,
        d.price_per_sf_yr,

        -- Collection rate
        case
            when d.rent_base > 0
            then (d.collected / d.rent_base) * 100
            else 0
        end as collection_rate_pct,

        -- Occupancy calculations (with toggle)
        s.total_property_sqft,
        s.effective_sqft,
        s.vacant_sqft,
        s.own_use_sqft,
        case
            when s.total_property_sqft > 0
            then (d.leased_sqft / s.total_property_sqft) * 100
            else 0
        end as occupancy_pct,
        case
            when s.effective_sqft > 0
            then (d.leased_sqft / s.effective_sqft) * 100
            else 0
        end as occupancy_pct_excl_own_use,

        -- Revenue metrics
        case
            when s.effective_sqft > 0
            then (d.collected / s.effective_sqft)
            else 0
        end as collected_per_sf,

        -- AR (Accounts Receivable)
        d.uncollected as accounts_receivable,

        -- Operating expenses (placeholder - expense data not available)
        0 as fixed_expenses,
        0 as variable_expenses,
        0 as total_expenses,

        -- NOI (proto): Collected rent - expenses (expenses = 0 for now)
        d.collected as noi_proto,

        -- NOI margin %
        100.0 as noi_margin_pct

    from dashboard_data d
    left join sqft_calcs s on d.as_of_month = s.as_of_month
)

select * from kpis
order by as_of_month desc, month desc

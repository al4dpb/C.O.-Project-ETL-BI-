{{
    config(
        materialized='table'
    )
}}

-- Gold: Building-level (A vs B) monthly KPIs (V2 with own-use toggle)
{% set exclude_own_use = var('exclude_own_use', false) %}

with lease_data as (
    select * from {{ ref('stg_lease_rate') }}
),

dashboard_data as (
    select * from {{ ref('stg_dashboard_monthly') }}
),

-- Split metrics by building with own-use toggle
building_split as (
    select
        as_of_month,
        building,
        sum(sqft) as total_sqft,
        sum(case when not is_vacant then sqft else 0 end) as occupied_sqft,
        sum(case
            when {% if exclude_own_use %}not is_own_use and not is_vacant{% else %}not is_vacant{% endif %}
            then sqft
            else 0
        end) as effective_occupied_sqft,
        sum(case when is_vacant then sqft else 0 end) as vacant_sqft,
        sum(case when is_own_use then sqft else 0 end) as own_use_sqft,
        count(*) as suite_count,
        sum(case when is_vacant then 1 else 0 end) as vacant_count,
        sum(case when is_own_use then 1 else 0 end) as own_use_count
    from lease_data
    where building in ('A', 'B')
    group by as_of_month, building
),

-- Add time dimension from dashboard
building_kpi as (
    select
        d.as_of_month,
        d.month,
        b.building,
        b.total_sqft,
        b.occupied_sqft,
        b.effective_occupied_sqft,
        b.vacant_sqft,
        b.own_use_sqft,

        -- Occupancy %
        case
            when b.total_sqft > 0
            then (b.occupied_sqft / b.total_sqft) * 100
            else 0
        end as occupancy_pct,

        -- Occupancy % (excluding own-use)
        case
            when b.total_sqft > 0
            then (b.effective_occupied_sqft / b.total_sqft) * 100
            else 0
        end as occupancy_pct_excl_own_use,

        b.suite_count,
        b.vacant_count,
        b.own_use_count
    from dashboard_data d
    inner join building_split b on d.as_of_month = b.as_of_month
)

select * from building_kpi
order by as_of_month desc, month desc, building

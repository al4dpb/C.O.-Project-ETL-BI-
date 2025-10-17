{{
    config(
        materialized='table'
    )
}}

-- Gold: Rolling window KPIs (3/6/9/12 months)
-- Computes trailing averages and sums for each window size
with prop_kpis as (
    select * from {{ ref('prop_kpi_monthly') }}
),

calendar as (
    select * from {{ ref('dim_calendar_month') }}
),

-- Generate all window sizes and months
window_params as (
    select as_of_month, month from prop_kpis
),

windows_3m as (
    select
        p.as_of_month as end_month,
        '3m' as window_size,
        avg(p.occupancy_pct) as avg_occupancy_pct,
        avg(p.collection_rate_pct) as avg_collection_rate_pct,
        avg(p.price_per_sf_yr) as avg_price_per_sf_yr,
        sum(p.collected) as total_collected,
        sum(p.rent_base) as total_rent_base,
        sum(p.uncollected) as total_uncollected,
        avg(p.noi_proto) as avg_noi_proto,
        avg(p.noi_margin_pct) as avg_noi_margin_pct
    from prop_kpis p
    inner join prop_kpis p2
        on p2.as_of_month <= p.as_of_month
        and p2.as_of_month >= (cast(p.as_of_month || '-01' as date) - INTERVAL '3 months')::VARCHAR(10)
    group by p.as_of_month
),

windows_6m as (
    select
        p.as_of_month as end_month,
        '6m' as window_size,
        avg(p.occupancy_pct) as avg_occupancy_pct,
        avg(p.collection_rate_pct) as avg_collection_rate_pct,
        avg(p.price_per_sf_yr) as avg_price_per_sf_yr,
        sum(p.collected) as total_collected,
        sum(p.rent_base) as total_rent_base,
        sum(p.uncollected) as total_uncollected,
        avg(p.noi_proto) as avg_noi_proto,
        avg(p.noi_margin_pct) as avg_noi_margin_pct
    from prop_kpis p
    inner join prop_kpis p2
        on p2.as_of_month <= p.as_of_month
        and p2.as_of_month >= (cast(p.as_of_month || '-01' as date) - INTERVAL '6 months')::VARCHAR(10)
    group by p.as_of_month
),

windows_9m as (
    select
        p.as_of_month as end_month,
        '9m' as window_size,
        avg(p.occupancy_pct) as avg_occupancy_pct,
        avg(p.collection_rate_pct) as avg_collection_rate_pct,
        avg(p.price_per_sf_yr) as avg_price_per_sf_yr,
        sum(p.collected) as total_collected,
        sum(p.rent_base) as total_rent_base,
        sum(p.uncollected) as total_uncollected,
        avg(p.noi_proto) as avg_noi_proto,
        avg(p.noi_margin_pct) as avg_noi_margin_pct
    from prop_kpis p
    inner join prop_kpis p2
        on p2.as_of_month <= p.as_of_month
        and p2.as_of_month >= (cast(p.as_of_month || '-01' as date) - INTERVAL '9 months')::VARCHAR(10)
    group by p.as_of_month
),

windows_12m as (
    select
        p.as_of_month as end_month,
        '12m' as window_size,
        avg(p.occupancy_pct) as avg_occupancy_pct,
        avg(p.collection_rate_pct) as avg_collection_rate_pct,
        avg(p.price_per_sf_yr) as avg_price_per_sf_yr,
        sum(p.collected) as total_collected,
        sum(p.rent_base) as total_rent_base,
        sum(p.uncollected) as total_uncollected,
        avg(p.noi_proto) as avg_noi_proto,
        avg(p.noi_margin_pct) as avg_noi_margin_pct
    from prop_kpis p
    inner join prop_kpis p2
        on p2.as_of_month <= p.as_of_month
        and p2.as_of_month >= (cast(p.as_of_month || '-01' as date) - INTERVAL '12 months')::VARCHAR(10)
    group by p.as_of_month
),

all_windows as (
    select * from windows_3m
    union all
    select * from windows_6m
    union all
    select * from windows_9m
    union all
    select * from windows_12m
)

select * from all_windows
order by end_month desc, window_size

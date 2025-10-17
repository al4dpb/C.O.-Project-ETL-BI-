{{
    config(
        materialized='incremental',
        unique_key=['as_of_month', 'month']
    )
}}

-- Staging: Dashboard monthly KPIs (V2 - partitioned bronze)
with source as (
    select * from read_parquet('../../data/bronze/raw_dashboard_monthly/as_of_month=*/raw_dashboard_monthly_*.parquet', hive_partitioning=1)
),

cleaned as (
    select
        as_of_month,
        cast(month as date) as month,
        cast(rent_base as decimal(12,2)) as rent_base,
        cast(collected as decimal(12,2)) as collected,
        cast(uncollected as decimal(12,2)) as uncollected,
        cast(leased_sqft as integer) as leased_sqft,
        cast(price_per_sf_yr as decimal(10,2)) as price_per_sf_yr,
        _file_md5,
        cast(_ingested_at as timestamp) as ingested_at
    from source
    where as_of_month is not null
      and month is not null
)

select * from cleaned

{% if is_incremental() %}
    -- Only process new partitions
    where as_of_month > (select max(as_of_month) from {{ this }})
{% endif %}

{{
    config(
        materialized='incremental',
        unique_key=['as_of_month', 'suite_id']
    )
}}

-- Staging: Lease/rate snapshot (V2 - partitioned bronze, pre-snapshot prep)
with source as (
    select * from read_parquet('../../data/bronze/raw_lease_rate_snapshot/as_of_month=*/raw_lease_rate_snapshot_*.parquet', hive_partitioning=1)
),

cleaned as (
    select
        as_of_month,
        suite_id,
        building,
        tenant,
        cast(sqft as integer) as sqft,
        cast(rent_monthly as decimal(12,2)) as rent_monthly,
        cast(rent_annual as decimal(12,2)) as rent_annual,
        cast(rent_psf_yr as decimal(10,2)) as rent_psf_yr,
        is_vacant,
        is_own_use,
        _file_md5,
        cast(_ingested_at as timestamp) as ingested_at
    from source
    where as_of_month is not null
      and suite_id is not null
)

select * from cleaned

{% if is_incremental() %}
    -- Only process new partitions
    where as_of_month > (select max(as_of_month) from {{ this }})
{% endif %}

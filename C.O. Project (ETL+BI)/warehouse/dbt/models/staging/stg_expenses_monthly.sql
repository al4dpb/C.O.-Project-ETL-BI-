{{
    config(
        materialized='incremental',
        unique_key=['as_of_month', 'month', 'item']
    )
}}

-- Staging: Expenses monthly (V2 - NEW)
with source as (
    select * from read_parquet('../../data/bronze/raw_expenses_monthly/as_of_month=*/raw_expenses_monthly_*.parquet', hive_partitioning=1)
),

cleaned as (
    select
        as_of_month,
        cast(month as date) as month,
        item,
        cast(actual as decimal(12,2)) as actual,
        expense_category,
        _file_md5,
        cast(_ingested_at as timestamp) as ingested_at
    from source
    where as_of_month is not null
      and item is not null
      and expense_category is not null
)

select * from cleaned

{% if is_incremental() %}
    -- Only process new partitions
    where as_of_month > (select max(as_of_month) from {{ this }})
{% endif %}

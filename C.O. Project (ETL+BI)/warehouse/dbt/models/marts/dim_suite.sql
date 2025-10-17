-- Dimension: Suite attributes
with lease_data as (
    select * from {{ ref('stg_lease_rate') }}
),

suite_dim as (
    select distinct
        suite_id,
        building,
        sqft
    from lease_data
)

select * from suite_dim
order by suite_id

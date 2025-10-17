-- Dimension: Tenant attributes
with lease_data as (
    select * from {{ ref('stg_lease_rate') }}
),

tenant_dim as (
    select distinct
        md5(tenant) as tenant_id,
        tenant as tenant_name,
        is_own_use
    from lease_data
)

select * from tenant_dim
order by tenant_name

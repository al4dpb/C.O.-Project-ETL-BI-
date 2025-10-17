{% snapshot snap_lease_rate_scd2 %}

{{
    config(
      target_schema='snapshots',
      unique_key='suite_id',
      strategy='check',
      check_cols=['tenant', 'rent_monthly', 'rent_annual', 'rent_psf_yr', 'is_vacant', 'is_own_use'],
      invalidate_hard_deletes=True
    )
}}

-- SCD2 snapshot: Track lease changes over time
-- Detects changes in tenant, rent, or status per suite
select
    as_of_month,
    suite_id,
    building,
    tenant,
    sqft,
    rent_monthly,
    rent_annual,
    rent_psf_yr,
    is_vacant,
    is_own_use,
    _file_md5,
    ingested_at
from {{ ref('stg_lease_rate') }}

{% endsnapshot %}

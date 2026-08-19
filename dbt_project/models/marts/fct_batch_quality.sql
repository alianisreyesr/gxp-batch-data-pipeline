with telemetry as (
    select * from {{ ref('stg_batch_telemetry') }}
),
flagged as (
    select
        *,
        temperature_c < 35.0 or temperature_c > 38.0 as temperature_oos,
        ph < 6.8 or ph > 7.4 as ph_oos,
        dissolved_oxygen_pct < 30.0 or dissolved_oxygen_pct > 100.0 as do_oos,
        assay_pct < 90.0 or assay_pct > 105.0 as assay_oos
    from telemetry
)
select
    batch_id,
    count(*) as telemetry_records,
    sum(case when temperature_oos then 1 else 0 end) as temperature_oos_records,
    sum(case when ph_oos then 1 else 0 end) as ph_oos_records,
    sum(case when do_oos then 1 else 0 end) as do_oos_records,
    sum(case when assay_oos then 1 else 0 end) as assay_oos_records,
    sum(case when temperature_oos or ph_oos or do_oos or assay_oos then 1 else 0 end) as total_oos_records
from flagged
group by batch_id

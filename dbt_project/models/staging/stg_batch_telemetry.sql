select
    batch_id || '|' || phase || '|' || cast(timestamp_utc as varchar) as record_key,
    batch_id,
    timestamp_utc,
    phase,
    bioreactor_id,
    temperature_c,
    ph,
    dissolved_oxygen_pct,
    agitation_rpm,
    assay_pct
from {{ source('raw', 'raw_batch_telemetry') }}

select *
from {{ ref('stg_batch_telemetry') }}
where assay_pct < 0 or assay_pct > 150

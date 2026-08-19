# GxP Batch Manufacturing Data Pipeline

[![CI](https://github.com/alianisreyesr/gxp-batch-data-pipeline/actions/workflows/ci.yml/badge.svg)](https://github.com/alianisreyesr/gxp-batch-data-pipeline/actions/workflows/ci.yml)

**Status: Active MVP** · Python · DuckDB · dbt · pytest · GitHub Actions

> **Portfolio safety boundary:** all records, telemetry, identifiers, thresholds, and scenarios in this repository are fictional and synthetically generated. This is educational portfolio software, not validated GxP software, and it must not be used for manufacturing, release, quality, or patient-safety decisions.

## What this implements

A small, reproducible batch-data pipeline that demonstrates the engineering path from raw synthetic process telemetry to tested analytical outputs:

```text
synthetic telemetry
      ↓
Python quality gates
      ↓
accepted rows ─────────────→ rejected rows + explicit reasons
      ↓
DuckDB raw_batch_telemetry
      ↓
dbt staging model
      ↓
fct_batch_quality
      ↓
explainable OOS evidence
```

This MVP intentionally favors traceability and executable evidence over platform complexity.

## Verified evidence

The first full GitHub Actions run passed end to end with:

- **6 Python tests passed**;
- **96 synthetic telemetry rows generated**;
- **96 accepted / 0 rejected** for the deterministic valid dataset;
- **2 dbt models + 8 dbt data tests completed successfully**;
- deterministic OOS evidence produced for `CPP-TEMP-001` and `CQA-ASSAY-001`.

## Implemented controls

- deterministic synthetic telemetry generation with seed support;
- required-field, type, UTC timestamp, duplicate-key, monotonicity, and plausible-range validation;
- explicit quarantine of rejected records with machine-readable reasons;
- DuckDB persistence for accepted telemetry;
- dbt staging and batch-quality mart models;
- rule-based OOS flags that include rule ID, observed value, expected range, batch, phase, and timestamp;
- pytest coverage for generation, quality gates, quarantine behavior, OOS explainability, and DuckDB persistence;
- GitHub Actions gate that runs pytest, the pipeline, `dbt build`, and deterministic OOS evidence generation.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt

python -m src.generate_data --seed 42
python -m src.ingest
dbt build --project-dir dbt_project --profiles-dir dbt_project
python -m src.oos data/synthetic/batch_telemetry.csv
```

Generated runtime files are intentionally ignored by Git.

## Synthetic schema

| Field | Meaning |
|---|---|
| `batch_id` | Fictional batch identifier |
| `timestamp_utc` | Explicit UTC telemetry timestamp |
| `phase` | Synthetic process phase |
| `bioreactor_id` | Fictional equipment identifier |
| `temperature_c` | Synthetic process temperature |
| `ph` | Synthetic pH value |
| `dissolved_oxygen_pct` | Synthetic dissolved oxygen percentage |
| `agitation_rpm` | Synthetic agitation rate |
| `assay_pct` | Synthetic assay/CQA result |

## Quality gate vs. OOS rule

The quality gate checks whether a record is structurally trustworthy enough to enter the analytical pipeline. OOS rules are intentionally narrower process-review rules. A record can therefore be **valid telemetry but still OOS**, which keeps data-integrity validation separate from quality interpretation.

Examples:

```text
invalid timestamp → quarantine
missing pH        → quarantine
999 °C            → quarantine
39.2 °C           → accepted telemetry + CPP-TEMP-001 OOS flag
87.5% assay       → accepted telemetry + CQA-ASSAY-001 OOS flag
```

## Repository structure

```text
src/                     synthetic generation, quality gates, ingestion, OOS rules
tests/                   pytest verification
data/                     generated synthetic and rejected records (ignored)
warehouse/                local DuckDB runtime database (ignored)
dbt_project/              dbt sources, staging, mart, and tests
.github/workflows/ci.yml  automated quality gate
```

## Current limitations

This MVP does **not** include authentication, electronic signatures, governed deployment, validated infrastructure, formal CSV evidence, production data connectors, streaming, ML prediction, or cloud/Kubernetes deployment. Those are deliberately out of scope until the executable baseline is stable.

## Portfolio objective

This repository demonstrates one concise engineering story:

**synthetic telemetry → explicit data-quality decisions → reproducible warehouse → tested transformations → explainable quality signals**.

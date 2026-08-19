# GxP Batch Manufacturing Data Pipeline

[![CI](https://github.com/alianisreyesr/gxp-batch-data-pipeline/actions/workflows/ci.yml/badge.svg)](https://github.com/alianisreyesr/gxp-batch-data-pipeline/actions/workflows/ci.yml)

**Status: Flagship hardening candidate** · Python · DuckDB · dbt · pytest · GitHub Actions

> **Portfolio safety boundary:** all records, telemetry, identifiers, thresholds, and scenarios in this repository are fictional and synthetically generated. This is educational portfolio software, not validated GxP software, and it must not be used for manufacturing, release, quality, or patient-safety decisions.

## What this implements

A traceable batch-data pipeline that produces durable run evidence from deterministic synthetic process telemetry:

```text
synthetic telemetry
      ↓
Python quality gates
      ↓
accepted rows ─────────────→ rejected rows + explicit reasons
      ↓
DuckDB raw_batch_telemetry
      ↓
explainable OOS evaluation ─→ artifacts/oos_evidence.json
      ↓
run manifest ───────────────→ artifacts/run_manifest.json
      ↓
dbt staging + quality mart
```

The implementation intentionally favors traceability and executable evidence over platform complexity.

## Verified CI evidence

GitHub Actions run **#5** completed successfully for this hardening branch with:

- **12 Python tests passed**;
- **80.25% Python statement coverage** with an **80% CI gate**;
- **96 synthetic telemetry rows generated**;
- **96 accepted / 0 rejected** for the deterministic default dataset;
- **2 explainable OOS flags**: one `CPP-TEMP-001` and one `CQA-ASSAY-001`;
- **2 dbt models + 8 dbt data tests**, all successful;
- machine-readable run manifest with source SHA-256, deterministic run ID, configuration, counts, OOS summary, artifact paths, and safety boundary.

For the verified default run, the source CSV SHA-256 was:

```text
b84c6c743b86d018c9ce02d2648049924fee7e607d0f29906c5408d77416cb03
```

and the deterministic run ID was:

```text
run-b84c6c743b86d018
```

## One-command pipeline

After installing dependencies, the canonical execution path is:

```bash
python -m src.pipeline --seed 42
```

This command generates the synthetic source data, validates and quarantines records, loads accepted telemetry into DuckDB, evaluates OOS rules, persists OOS evidence, and writes the run manifest.

To run the analytical transformation layer afterward:

```bash
dbt build --project-dir dbt_project --profiles-dir dbt_project
```

## Run evidence

The pipeline writes runtime evidence under ignored local paths:

```text
data/synthetic/batch_telemetry.csv
      └── SHA-256 recorded in manifest

data/rejected/rejected_rows.csv
      └── quarantined rows + explicit reasons

warehouse/batch.duckdb
      └── accepted telemetry and dbt models

artifacts/oos_evidence.json
      └── structured OOS flags

artifacts/run_manifest.json
      └── configuration, source hash, counts, OOS summary, artifact paths, safety boundary
```

The run ID is derived from the source CSV hash. The repository does **not** claim the DuckDB file itself is cryptographically reproducible.

## Implemented controls

- deterministic synthetic telemetry generation with seed support;
- required-field, type, UTC timestamp, duplicate-key, monotonicity, and plausible-range validation;
- explicit quarantine of rejected records with machine-readable reasons;
- DuckDB persistence for accepted telemetry;
- rule-based OOS flags with rule ID, observed value, expected range, batch, phase, and timestamp;
- structured OOS JSON evidence;
- source CSV SHA-256 evidence and deterministic run ID;
- versioned run-manifest schema;
- dbt staging and batch-quality mart models;
- 12-test Python suite with measured statement coverage;
- GitHub Actions gate using least-privilege `contents: read` permissions;
- deterministic manifest assertions followed by `dbt build`.

## Quality gate vs. OOS rule

The quality gate decides whether a record is structurally trustworthy enough to enter the analytical pipeline. OOS rules are narrower process-review rules. A record can therefore be **valid telemetry but still OOS**, keeping data-integrity validation separate from quality interpretation.

Examples:

```text
invalid timestamp → quarantine
missing pH        → quarantine
999 °C            → quarantine
39.2 °C           → accepted telemetry + CPP-TEMP-001 OOS flag
87.5% assay       → accepted telemetry + CQA-ASSAY-001 OOS flag
```

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

## Repository structure

```text
src/                     generation, quality gates, ingestion, OOS rules, pipeline orchestration
tests/                   pytest verification
data/                     generated synthetic and rejected records (ignored)
warehouse/                local DuckDB runtime database (ignored)
artifacts/                generated manifest and OOS evidence (ignored)
dbt_project/              dbt sources, staging, mart, and tests
.github/workflows/ci.yml  automated quality gate
```

## Current limitations

This project does **not** include authentication, electronic signatures, governed deployment, validated infrastructure, formal CSV evidence, production data connectors, streaming, ML prediction, or cloud/Kubernetes deployment. Those capabilities are deliberately out of scope for this portfolio milestone.

Dependency versions remain bounded by compatible ranges rather than a fully locked environment. CI evidence therefore reflects the versions resolved in the verified run; future release hardening may add tighter dependency locking if needed.

## Portfolio objective

This repository demonstrates one concise engineering story:

**synthetic telemetry → explicit data-quality decisions → traceable source evidence → reproducible analytical run metadata → tested transformations → explainable quality signals**.

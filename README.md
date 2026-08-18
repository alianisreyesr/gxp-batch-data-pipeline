# GxP Batch Manufacturing Data Pipeline

<div align="center">

[![Status](https://img.shields.io/badge/Status-Scaffold-0A66C2?style=flat-square)](https://github.com/alianisreyesr/gxp-batch-data-pipeline)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![DuckDB](https://img.shields.io/badge/DuckDB-OLAP-FFF000?style=flat-square&logo=duckdb&logoColor=black)](https://duckdb.org/)
[![dbt](https://img.shields.io/badge/dbt-Core-FF694B?style=flat-square&logo=dbt&logoColor=white)](https://www.getdbt.com/)
[![Great Expectations](https://img.shields.io/badge/Data_Quality-Great_Expectations-FF5A00?style=flat-square)](https://greatexpectations.io/)
[![Compliance](https://img.shields.io/badge/GxP-21_CFR_Part_11_%2F_ALCOA%2B-2E7D32?style=flat-square)](docs/REGULATORY_CONTEXT.md)

**Pharmaceutical Batch Manufacturing ETL · Data Contracts · Critical Quality Attributes (CQA) · DuckDB & dbt**

*Portfolio-safe engineering prototype — 100% synthetic process telemetry*

[Architecture](#architecture--data-lineage) · [Data Quality Contracts](#data-quality-contracts--great-expectations) · [Regulatory Context](docs/REGULATORY_CONTEXT.md) · [Profile](https://github.com/alianisreyesr)

</div>

---

> **Portfolio Safety Boundary:** All batch records, sensor time-series, bioreactor telemetry, and lab assay values are synthetically generated. This system contains no proprietary or confidential manufacturing data and is built strictly for technical and educational demonstration.

---

## Overview

In pharmaceutical manufacturing, batch release decisions depend directly on data integrity, verifiable lineage, and strict enforcement of **Critical Process Parameters (CPPs)** and **Critical Quality Attributes (CQAs)**.

This repository implements an end-to-end, reproducible modern data pipeline designed for regulated manufacturing analytics:

1. **Synthetic Telemetry Generator:** Simulates multi-stage batch processing (Fermentation, Purification, Formulation, and Release Testing).
2. **Data Contracts & Gateways (Great Expectations):** Enforces strict schema, nullability, range, and statistical distribution checks before loading into raw storage.
3. **Dimensional Data Modeling (dbt + DuckDB):** Transforms raw event streams into medallion architecture layers (`raw` → `stg` → `fct_batch_execution`, `dim_bioreactors`, `dim_assays`).
4. **Out-of-Specification (OOS) Detection Engine:** Automatically flags process drift and parameter violations against validated batch recipe tolerances.
5. **Release-Ready Data Marts:** Serves structured, lineage-traced datasets optimized for analytical reporting and Power BI dashboards.

---

## Architecture & Data Lineage

```text
┌─────────────────────────┐     ┌────────────────────────┐     ┌────────────────────────┐
│  Synthetic Telemetry    │ ──> │   Great Expectations   │ ──> │     Raw DuckDB Lake    │
│ (Sensors, LIMS, Alarms) │     │  (Data Gate & Schema)  │     │   (Immutable Ingest)   │
└─────────────────────────┘     └────────────────────────┘     └───────────┬────────────┘
                                                                           │
                                ┌──────────────────────────────────────────┘
                                ▼
                 ┌─────────────────────────────┐
                 │          dbt Core           │
                 │  Staging & Validation Layer │
                 └──────────────┬──────────────┘
                                │
                                ▼
                 ┌─────────────────────────────┐
                 │      Dimensional Marts      │
                 │   (OOS Flags, CPP Lineage)  │
                 └──────────────┬──────────────┘
                                │
                                ▼
                 ┌─────────────────────────────┐
                 │     Analytical Outputs      │
                 │  (Power BI / Batch Dossier) │
                 └─────────────────────────────┘
```

---

## Data Quality Contracts & Great Expectations

Quality gates prevent invalid or corrupted sensor records from entering downstream analytical models:

- **Attributable:** Enforces valid operator/system ID attribution on all critical intervention timestamps.
- **Accurate:** Bounds temperature, pH, dissolved oxygen (DO), and agitation RPM to validated operating ranges.
- **Contemporaneous:** Validates strict monotonic UTC time increments across sequential batch phases.
- **Complete:** Rejects batch records with missing Critical Quality Attribute assay endpoints.

---

## Regulated Portfolio Ecosystem

| Repository | Domain Focus | Evidence |
|---|---|---|
| [gxp-batch-data-pipeline](https://github.com/alianisreyesr/gxp-batch-data-pipeline) | Batch manufacturing ETL & data contracts | DuckDB · dbt · Great Expectations |
| [gxp-change-control](https://github.com/alianisreyesr/gxp-change-control) | Controlled change lifecycle & approvals | v1.0.0 · 68 tests · CI/CD |
| [quality-deviation-risk-monitor](https://github.com/alianisreyesr/quality-deviation-risk-monitor) | Deviation prioritization & scoring | 57 tests · Append-only audit |
| [csv-evidence-tracker](https://github.com/alianisreyesr/csv-evidence-tracker) | RTM & IQ/OQ/PQ execution patterns | ALCOA+ verified evidence |
| [data-integrity-case-file](https://github.com/alianisreyesr/data-integrity-case-file) | ALCOA+ gap analysis & investigations | Structured investigation ledger |
| [csa-assurance-planner](https://github.com/alianisreyesr/csa-assurance-planner) | Risk-based software assurance planning | FDA CSA guidance alignment |

---

## Tech Stack

- **Pipeline & Processing:** Python 3.11, DuckDB, Polars, pandas
- **Transformations & Modeling:** dbt Core (dbt-duckdb)
- **Data Quality & Contracts:** Great Expectations, Pydantic v2
- **Testing & CI:** pytest, GitHub Actions, CodeQL
- **Packaging:** Docker, docker-compose

---

## Spanish Summary / Resumen

Pipeline de ingeniería de datos para **manufactura farmacéutica y bioprocesos**: ingestión de telemetría de bioprocesos sintética → validación mediante contratos de datos (Great Expectations) → transformaciones dimensionales con dbt y DuckDB → detección de desviaciones fuera de especificación (OOS) → capas de datos listas para analítica y Power BI. Todo construido con datos 100% sintéticos bajo principios GxP y ALCOA+.

---

<div align="center">

Built by [Alianis Reyes-Reyes](https://github.com/alianisreyesr) · [LinkedIn](https://www.linkedin.com/in/alianis-reyes-reyes/) · [Digital Portfolio](https://poplme.co/hash/aJvjFE0Z/1/es)

</div>
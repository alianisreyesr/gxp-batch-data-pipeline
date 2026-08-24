# Case study: traceable batch telemetry pipeline

## Problem

Manufacturing telemetry is only useful when accepted and rejected records, transformations, quality signals, and source lineage can be reproduced.

## Users and outcome

Data engineers run a deterministic pipeline; analysts query curated DuckDB models; quality reviewers inspect quarantine and OOS evidence. One command produces accepted data, explicit rejection reasons, analytical models, and a run manifest tied to source hashes.

## Engineering decisions

- Seeded synthetic generation makes runs repeatable.
- Schema and quality gates separate rejected records before analytical loading.
- SHA-256 source hashes and run manifests preserve technical lineage.
- dbt tests validate transformations, while pytest covers pipeline behavior and failure paths.

## Data contract

The [synthetic telemetry data contract](DATA_CONTRACT.md) documents the row-level grain, input schema, acceptance rules, output artifacts, and the distinction between a rejected record and an explainable OOS signal. It gives reviewers a concise, implementation-independent way to assess the pipeline's data boundaries.

## Evidence

CI runs the Python and dbt checks. The README publishes the expected run output, coverage gate, schema, control points, and repository structure.

## Boundary

Every identifier, threshold, and measurement is synthetic. The project is not connected to manufacturing equipment and cannot support batch release or any regulated decision.

# Data Contract: Synthetic Batch Telemetry

## Purpose

This document defines the input and output expectations for the portfolio pipeline. It is intended to make every data-quality decision understandable, reviewable, and reproducible.

> **Safety boundary:** This contract applies only to the repository's fictional, synthetic demonstration records. It is not a validated specification and must not be used for manufacturing, release, quality, or patient-safety decisions.

## Input grain

One record represents one synthetic telemetry reading for one fictional batch, bioreactor, process phase, and UTC timestamp.

The default generator produces a deterministic dataset when it is run with the same seed.

## Input schema

| Field | Type | Required | Contract |
|---|---:|:---:|---|
| `batch_id` | string | Yes | Non-empty fictional batch identifier. |
| `timestamp_utc` | UTC timestamp | Yes | Parseable timestamp with explicit UTC context. |
| `phase` | string | Yes | Non-empty synthetic process phase. |
| `bioreactor_id` | string | Yes | Non-empty fictional equipment identifier. |
| `temperature_c` | number | Yes | Plausible synthetic temperature value. |
| `ph` | number | Yes | Plausible synthetic pH value. |
| `dissolved_oxygen_pct` | number | Yes | Plausible synthetic dissolved-oxygen percentage. |
| `agitation_rpm` | number | Yes | Plausible synthetic agitation value. |
| `assay_pct` | number | Yes | Plausible synthetic assay result. |

## Acceptance rules

A record is accepted only when it meets the pipeline's structural and quality checks:

- Required values are present and correctly typed.
- `timestamp_utc` is valid and explicitly handled as UTC.
- The record key is unique.
- Readings are monotonic within the pipeline's expected sequence.
- Numeric measurements are inside plausible input ranges.

Records that fail a gate are not silently corrected. They are written to the rejection output with an explicit reason.

## Output contracts

| Output | Purpose | Key review question |
|---|---|---|
| Accepted telemetry in DuckDB | Trusted analytical input | Which records passed the gates? |
| Rejected rows CSV | Quarantine evidence | Which records were excluded, and why? |
| OOS evidence JSON | Explainable rule results | Which accepted records crossed a configured review threshold? |
| Run manifest JSON | Execution lineage | Which source hash, configuration, counts, and artifacts produced this run? |
| dbt models and tests | Curated analytical layer | Did transformed batch-quality data pass its tests? |

## Quality decision versus OOS signal

A quality-gate rejection means a record is not structurally trustworthy enough to enter analysis.

An OOS signal is different: the telemetry record was structurally valid and accepted, but a documented synthetic rule flagged it for review. An OOS flag is an explainable analytical signal, not a release decision.

## Change policy for this portfolio project

Changes to this contract should be accompanied by:

1. A corresponding change in the pipeline, generator, or dbt model.
2. Tests that demonstrate the intended acceptance, rejection, or OOS behavior.
3. A README or case-study update when user-facing behavior changes.
4. Continued use of fictional, synthetic data only.

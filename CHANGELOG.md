# Changelog

All notable changes to this portfolio project are documented in this file.

The project follows semantic versioning for public portfolio releases. Version numbers describe the repository's software baseline; they do not indicate regulatory validation, approval, or fitness for a regulated intended use.

## [1.0.0] — 2026-08-27

### Added

- Deterministic synthetic batch-telemetry generation with seed support
- Schema, type, UTC timestamp, duplicate-key, monotonicity, and plausible-range validation quality gate
- Explicit quarantine of rejected records with machine-readable reasons
- DuckDB persistence for accepted telemetry
- Rule-based out-of-specification (OOS) evaluation with structured JSON evidence
- Machine-readable quality-review summary grouped by batch, phase, and rule
- Source CSV SHA-256 evidence and deterministic run ID
- Versioned run-manifest schema and evidence verifier (`src.verify_evidence`)
- dbt staging and batch-quality mart models with dbt data tests
- One-command pipeline entry point (`python -m src.pipeline`)
- 12-test pytest suite with measured statement coverage
- GitHub Actions CI gate (least-privilege permissions) and CodeQL scanning

### Known limitations

- No authentication, electronic signatures, or governed deployment
- The DuckDB warehouse file itself is not claimed to be cryptographically reproducible
- Synthetic data only; not for manufacturing, release, quality, or patient-safety decisions

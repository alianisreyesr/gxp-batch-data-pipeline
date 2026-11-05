# Security Policy

## Supported versions

| Version | Support status |
|---|---|
| `1.0.x` (latest `main`) | Current portfolio baseline; security fixes considered on a best-effort basis |
| `< 1.0` | Historical development snapshots; not supported |

This is a portfolio and learning project, not a hosted service or validated product. No service-level commitment is provided.

## Reporting a vulnerability

Do **not** open a public issue containing exploit details, credentials, personal data, confidential information, or regulated records.

Preferred reporting path:

1. Use GitHub private vulnerability reporting for this repository when the **Report a vulnerability** option is available under the Security tab.
2. If private reporting is unavailable, contact the repository owner through the LinkedIn link on the GitHub profile and request a private communication channel. Do not include sensitive technical details in the initial message.

A useful report includes:

- affected commit, tag, module, or command;
- reproducible steps using synthetic data only;
- observed and expected behavior;
- potential impact and prerequisite access;
- proposed remediation, if known;
- confirmation that no real, proprietary, personal, or regulated data was used.

Best-effort targets (not a commitment): acknowledgement within 7 days and a remediation plan or decision within 30 days. Public disclosure should occur only after a fix or mitigation is available and sensitive details have been removed.

## In-scope examples

- tampering with or bypassing the evidence verifier (`src.verify_evidence`), including path traversal outside the evidence root;
- ways to alter run evidence (manifest, OOS flags, quality summary) without detection;
- unsafe query construction or data loss in the DuckDB load step;
- unsafe parsing of CSV or JSON inputs;
- dependency or container vulnerabilities affecting the shipped code path;
- leakage of repository or workflow secrets.

## Out-of-scope examples

- missing production features already listed under "Known limitations" in the changelog (authentication, electronic signatures, governed deployment);
- attacks requiring write access to the host file system or the source tree;
- denial-of-service testing against infrastructure not explicitly authorized for testing;
- social engineering, spam, or testing against third-party accounts;
- findings based on real employer, patient, customer, or regulated data;
- requests to certify the software as compliant, validated, or production-ready.

## Secrets and data handling

- Never commit tokens, passwords, private keys, connection strings, or real credentials. `.env` files are git-ignored.
- Use only synthetic records and fictional batches.
- Rotate any secret immediately if it is accidentally exposed, then remove it from history where feasible.
- Treat generated DuckDB files, rejected-row CSVs, and evidence artifacts as disposable demonstration data.

## Security controls in the repository

- Parameterized DuckDB statements; the load step replaces its table inside a transaction and rolls back on failure instead of dropping existing data first.
- Schema, type, UTC-timestamp, duplicate and range validation with quarantine of rejected rows.
- SHA-256 source hashing, deterministic run IDs and an evidence verifier that rejects tampering.
- Pinned runtime and development dependencies, with Dependabot updates for pip and GitHub Actions.
- CI runs `ruff`, `mypy`, `pip-audit`, tests with an 85% coverage gate, and CodeQL; workflows use least-privilege `permissions:`.
- Non-root runtime container with runtime-only dependencies and a `.dockerignore`.

These controls reduce common development risks. They do not provide authentication, electronic signatures, protected audit storage, secure hosting, formal threat modeling, penetration testing, or regulatory validation.

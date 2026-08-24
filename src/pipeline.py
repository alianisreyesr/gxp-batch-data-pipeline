from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.generate_data import generate_rows, write_csv
from src.ingest import ingest
from src.oos import evaluate_oos
from src.quality_summary import build_quality_review_summary
from src.quality_report import write_quality_report

MANIFEST_SCHEMA_VERSION = "1.0"
SAFETY_BOUNDARY = (
    "All records, telemetry, identifiers, thresholds, and scenarios are fictional and "
    "synthetically generated. This is portfolio software, not validated GxP software, "
    "and it must not be used for manufacturing, release, quality, or patient-safety decisions."
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _json_value(value: Any) -> Any:
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    return value


def _load_accepted_rows(database_path: Path) -> list[dict[str, object]]:
    try:
        import duckdb
    except ImportError as exc:
        raise RuntimeError("duckdb is required; install requirements.txt") from exc

    connection = duckdb.connect(str(database_path))
    try:
        cursor = connection.execute("SELECT * FROM raw_batch_telemetry ORDER BY batch_id, phase, timestamp_utc")
        columns = [item[0] for item in cursor.description]
        return [dict(zip(columns, values)) for values in cursor.fetchall()]
    finally:
        connection.close()


def _relative(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run_pipeline(
    *,
    seed: int = 42,
    batches: int = 3,
    rows_per_phase: int = 8,
    root: Path = Path("."),
) -> dict[str, object]:
    root = root.resolve()
    source_path = root / "data" / "synthetic" / "batch_telemetry.csv"
    rejected_path = root / "data" / "rejected" / "rejected_rows.csv"
    database_path = root / "warehouse" / "batch.duckdb"
    oos_path = root / "artifacts" / "oos_evidence.json"
    manifest_path = root / "artifacts" / "run_manifest.json"
    quality_summary_path = root / "artifacts" / "quality_review_summary.json"
    quality_report_path = root / "artifacts" / "quality_review_report.html"

    rows = generate_rows(seed=seed, batches=batches, rows_per_phase=rows_per_phase)
    write_csv(rows, source_path)
    source_sha256 = sha256_file(source_path)

    accepted_count, rejected_count = ingest(source_path, database_path, rejected_path)
    accepted_rows = _load_accepted_rows(database_path)
    raw_flags = evaluate_oos(accepted_rows)
    flags = [
        {key: _json_value(value) for key, value in flag.items()}
        for flag in raw_flags
    ]
    write_json(oos_path, flags)
    quality_summary = build_quality_review_summary(flags)
    write_json(quality_summary_path, quality_summary)
    write_quality_report(quality_summary, quality_report_path)

    oos_by_rule = dict(sorted(Counter(str(flag["rule_id"]) for flag in flags).items()))
    run_id = f"run-{source_sha256[:16]}"
    manifest: dict[str, object] = {
        "manifest_schema_version": MANIFEST_SCHEMA_VERSION,
        "run_id": run_id,
        "generator": {
            "seed": seed,
            "batches": batches,
            "rows_per_phase": rows_per_phase,
        },
        "source_sha256": source_sha256,
        "counts": {
            "generated_rows": len(rows),
            "accepted_rows": accepted_count,
            "rejected_rows": rejected_count,
            "oos_flags": len(flags),
        },
        "oos_by_rule": oos_by_rule,
        "artifacts": {
            "source_csv": _relative(source_path, root),
            "rejected_csv": _relative(rejected_path, root),
            "duckdb": _relative(database_path, root),
            "oos_json": _relative(oos_path, root),
            "manifest_json": _relative(manifest_path, root),
            "quality_summary_json": _relative(quality_summary_path, root),
            "quality_report_html": _relative(quality_report_path, root),
        },
        "safety_boundary": SAFETY_BOUNDARY,
    }
    write_json(manifest_path, manifest)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the synthetic batch pipeline and emit traceable run evidence.")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--batches", type=int, default=3)
    parser.add_argument("--rows-per-phase", type=int, default=8)
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()

    manifest = run_pipeline(
        seed=args.seed,
        batches=args.batches,
        rows_per_phase=args.rows_per_phase,
        root=args.root,
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

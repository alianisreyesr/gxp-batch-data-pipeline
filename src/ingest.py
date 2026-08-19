from __future__ import annotations

import argparse
import csv
from pathlib import Path

from src.generate_data import FIELDNAMES
from src.quality import validate_rows


def read_csv(path: Path) -> list[dict[str, object]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def write_rows(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def ingest(input_path: Path, database_path: Path, rejected_path: Path) -> tuple[int, int]:
    try:
        import duckdb
    except ImportError as exc:
        raise RuntimeError("duckdb is required; install requirements.txt") from exc
    rows = read_csv(input_path)
    accepted, rejected = validate_rows(rows)
    write_rows(rejected_path, rejected, list(FIELDNAMES) + ["rejection_reasons"])
    database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = duckdb.connect(str(database_path))
    try:
        connection.execute("DROP TABLE IF EXISTS raw_batch_telemetry")
        connection.execute("""
            CREATE TABLE raw_batch_telemetry (
                batch_id VARCHAR NOT NULL,
                timestamp_utc TIMESTAMPTZ NOT NULL,
                phase VARCHAR NOT NULL,
                bioreactor_id VARCHAR NOT NULL,
                temperature_c DOUBLE NOT NULL,
                ph DOUBLE NOT NULL,
                dissolved_oxygen_pct DOUBLE NOT NULL,
                agitation_rpm DOUBLE NOT NULL,
                assay_pct DOUBLE NOT NULL
            )
        """)
        connection.executemany(
            "INSERT INTO raw_batch_telemetry VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [tuple(row[field] for field in FIELDNAMES) for row in accepted],
        )
    finally:
        connection.close()
    return len(accepted), len(rejected)


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate telemetry and load accepted rows into DuckDB.")
    parser.add_argument("--input", type=Path, default=Path("data/synthetic/batch_telemetry.csv"))
    parser.add_argument("--database", type=Path, default=Path("warehouse/batch.duckdb"))
    parser.add_argument("--rejected", type=Path, default=Path("data/rejected/rejected_rows.csv"))
    args = parser.parse_args()
    accepted, rejected = ingest(args.input, args.database, args.rejected)
    print(f"accepted_rows={accepted} rejected_rows={rejected} database={args.database}")


if __name__ == "__main__":
    main()

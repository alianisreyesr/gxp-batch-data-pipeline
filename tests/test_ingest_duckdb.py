from pathlib import Path

import pytest

from src.generate_data import generate_rows, write_csv
from src.ingest import ingest


duckdb = pytest.importorskip("duckdb")


def test_ingest_persists_only_accepted_rows(tmp_path: Path) -> None:
    rows = generate_rows(seed=4, batches=1, rows_per_phase=2)
    invalid = dict(rows[0])
    invalid["temperature_c"] = 999
    rows.append(invalid)

    source = tmp_path / "input.csv"
    database = tmp_path / "batch.duckdb"
    rejected = tmp_path / "rejected.csv"
    write_csv(rows, source)

    accepted_count, rejected_count = ingest(source, database, rejected)
    assert accepted_count == len(rows) - 1
    assert rejected_count == 1

    connection = duckdb.connect(str(database))
    try:
        persisted = connection.execute("SELECT COUNT(*) FROM raw_batch_telemetry").fetchone()[0]
    finally:
        connection.close()
    assert persisted == accepted_count
    assert "out_of_plausible_range:temperature_c" in rejected.read_text(encoding="utf-8")

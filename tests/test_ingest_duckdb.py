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


def _count(database: Path) -> int:
    connection = duckdb.connect(str(database))
    try:
        return connection.execute("SELECT COUNT(*) FROM raw_batch_telemetry").fetchone()[0]
    finally:
        connection.close()


def test_reingest_replaces_table_contents(tmp_path: Path) -> None:
    database = tmp_path / "batch.duckdb"
    first = tmp_path / "first.csv"
    second = tmp_path / "second.csv"
    write_csv(generate_rows(seed=4, batches=1, rows_per_phase=2), first)
    write_csv(generate_rows(seed=4, batches=1, rows_per_phase=1), second)

    first_count, _ = ingest(first, database, tmp_path / "r1.csv")
    second_count, _ = ingest(second, database, tmp_path / "r2.csv")

    assert second_count < first_count
    assert _count(database) == second_count


def test_failed_ingest_rolls_back_and_preserves_previous_data(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    database = tmp_path / "batch.duckdb"
    source = tmp_path / "input.csv"
    rows = generate_rows(seed=4, batches=1, rows_per_phase=2)
    write_csv(rows, source)
    loaded, _ = ingest(source, database, tmp_path / "r1.csv")

    broken = dict(rows[0])
    broken["temperature_c"] = "not-a-number"
    monkeypatch.setattr("src.ingest.validate_rows", lambda _rows: ([broken], []))
    with pytest.raises(duckdb.Error):
        ingest(source, database, tmp_path / "r2.csv")

    assert _count(database) == loaded

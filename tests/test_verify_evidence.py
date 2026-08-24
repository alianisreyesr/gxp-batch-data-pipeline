from __future__ import annotations

from pathlib import Path

import pytest

from src.pipeline import run_pipeline
from src.verify_evidence import verify_run_evidence


def test_verify_run_evidence_accepts_a_canonical_run(tmp_path: Path) -> None:
    manifest = run_pipeline(root=tmp_path)

    result = verify_run_evidence(tmp_path)

    assert result["status"] == "verified"
    assert result["run_id"] == manifest["run_id"]
    assert result["source_sha256"] == manifest["source_sha256"]
    assert result["counts"] == manifest["counts"]
    assert result["checked_artifacts"] == [
        "artifacts/oos_evidence.json",
        "artifacts/quality_review_report.html",
        "artifacts/quality_review_summary.json",
        "artifacts/run_manifest.json",
        "data/rejected/rejected_rows.csv",
        "data/synthetic/batch_telemetry.csv",
        "warehouse/batch.duckdb",
    ]


def test_verify_run_evidence_rejects_tampered_source_data(tmp_path: Path) -> None:
    run_pipeline(root=tmp_path)
    source = tmp_path / "data" / "synthetic" / "batch_telemetry.csv"
    source.write_text(source.read_text(encoding="utf-8") + "\n", encoding="utf-8")

    with pytest.raises(ValueError, match="SHA-256"):
        verify_run_evidence(tmp_path)


def test_verify_run_evidence_rejects_missing_artifact(tmp_path: Path) -> None:
    run_pipeline(root=tmp_path)
    (tmp_path / "artifacts" / "oos_evidence.json").unlink()

    with pytest.raises(FileNotFoundError, match="oos_json"):
        verify_run_evidence(tmp_path)

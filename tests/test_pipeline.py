from __future__ import annotations

import hashlib
import json
from pathlib import Path

from src.pipeline import SAFETY_BOUNDARY, run_pipeline, sha256_file


def test_sha256_file_matches_hashlib(tmp_path: Path) -> None:
    payload = b"traceable synthetic evidence\n"
    path = tmp_path / "evidence.txt"
    path.write_bytes(payload)
    assert sha256_file(path) == hashlib.sha256(payload).hexdigest()


def test_default_pipeline_produces_expected_counts(tmp_path: Path) -> None:
    manifest = run_pipeline(root=tmp_path)
    assert manifest["counts"] == {
        "generated_rows": 96,
        "accepted_rows": 96,
        "rejected_rows": 0,
        "oos_flags": 2,
    }
    assert manifest["oos_by_rule"] == {
        "CPP-TEMP-001": 1,
        "CQA-ASSAY-001": 1,
    }


def test_pipeline_persists_manifest_and_oos_evidence(tmp_path: Path) -> None:
    manifest = run_pipeline(root=tmp_path)
    manifest_path = tmp_path / "artifacts" / "run_manifest.json"
    oos_path = tmp_path / "artifacts" / "oos_evidence.json"

    assert manifest_path.exists()
    assert oos_path.exists()
    assert json.loads(manifest_path.read_text(encoding="utf-8")) == manifest

    flags = json.loads(oos_path.read_text(encoding="utf-8"))
    assert len(flags) == 2
    assert {flag["rule_id"] for flag in flags} == {"CPP-TEMP-001", "CQA-ASSAY-001"}
    for flag in flags:
        assert set(flag) >= {
            "rule_id",
            "batch_id",
            "phase",
            "timestamp_utc",
            "parameter",
            "observed_value",
            "expected_range",
        }


def test_manifest_source_hash_matches_generated_csv(tmp_path: Path) -> None:
    manifest = run_pipeline(root=tmp_path)
    source = tmp_path / str(manifest["artifacts"]["source_csv"])
    assert manifest["source_sha256"] == sha256_file(source)
    assert manifest["run_id"] == f"run-{manifest['source_sha256'][:16]}"


def test_pipeline_is_deterministic_for_same_configuration(tmp_path: Path) -> None:
    first = run_pipeline(root=tmp_path / "first", seed=17, batches=2, rows_per_phase=3)
    second = run_pipeline(root=tmp_path / "second", seed=17, batches=2, rows_per_phase=3)

    assert first["source_sha256"] == second["source_sha256"]
    assert first["run_id"] == second["run_id"]
    assert first["counts"] == second["counts"]
    assert first["oos_by_rule"] == second["oos_by_rule"]


def test_manifest_contains_configuration_artifacts_and_safety_boundary(tmp_path: Path) -> None:
    manifest = run_pipeline(root=tmp_path, seed=9, batches=1, rows_per_phase=2)

    assert manifest["manifest_schema_version"] == "1.0"
    assert manifest["generator"] == {"seed": 9, "batches": 1, "rows_per_phase": 2}
    assert manifest["safety_boundary"] == SAFETY_BOUNDARY
    assert manifest["artifacts"] == {
        "source_csv": "data/synthetic/batch_telemetry.csv",
        "rejected_csv": "data/rejected/rejected_rows.csv",
        "duckdb": "warehouse/batch.duckdb",
        "oos_json": "artifacts/oos_evidence.json",
        "manifest_json": "artifacts/run_manifest.json",
        "quality_summary_json": "artifacts/quality_review_summary.json",
        "quality_report_html": "artifacts/quality_review_report.html",
    }

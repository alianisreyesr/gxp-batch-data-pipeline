from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from src.pipeline import run_pipeline
from src.verify_evidence import main as verify_main
from src.verify_evidence import verify_run_evidence


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


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


def test_verify_run_evidence_rejects_missing_manifest(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="run manifest not found"):
        verify_run_evidence(tmp_path)


def test_verify_run_evidence_rejects_non_object_manifest(tmp_path: Path) -> None:
    run_pipeline(root=tmp_path)
    manifest_path = tmp_path / "artifacts" / "run_manifest.json"
    _write_json(manifest_path, [1, 2, 3])

    with pytest.raises(ValueError, match="must be a JSON object"):
        verify_run_evidence(tmp_path)


def test_verify_run_evidence_rejects_missing_artifact_map(tmp_path: Path) -> None:
    run_pipeline(root=tmp_path)
    manifest_path = tmp_path / "artifacts" / "run_manifest.json"
    manifest = _read_json(manifest_path)
    del manifest["artifacts"]
    _write_json(manifest_path, manifest)

    with pytest.raises(ValueError, match="no artifact map"):
        verify_run_evidence(tmp_path)


def test_verify_run_evidence_rejects_missing_counts_map(tmp_path: Path) -> None:
    run_pipeline(root=tmp_path)
    manifest_path = tmp_path / "artifacts" / "run_manifest.json"
    manifest = _read_json(manifest_path)
    del manifest["counts"]
    _write_json(manifest_path, manifest)

    with pytest.raises(ValueError, match="no counts map"):
        verify_run_evidence(tmp_path)


def test_verify_run_evidence_rejects_invalid_source_sha256(tmp_path: Path) -> None:
    run_pipeline(root=tmp_path)
    manifest_path = tmp_path / "artifacts" / "run_manifest.json"
    manifest = _read_json(manifest_path)
    manifest["source_sha256"] = "short"
    _write_json(manifest_path, manifest)

    with pytest.raises(ValueError, match="invalid source SHA-256"):
        verify_run_evidence(tmp_path)


def test_verify_run_evidence_rejects_run_id_mismatch(tmp_path: Path) -> None:
    run_pipeline(root=tmp_path)
    manifest_path = tmp_path / "artifacts" / "run_manifest.json"
    manifest = _read_json(manifest_path)
    manifest["run_id"] = "run-0000000000000000"
    _write_json(manifest_path, manifest)

    with pytest.raises(ValueError, match="run ID does not match"):
        verify_run_evidence(tmp_path)


def test_verify_run_evidence_rejects_non_string_artifact_path(tmp_path: Path) -> None:
    run_pipeline(root=tmp_path)
    manifest_path = tmp_path / "artifacts" / "run_manifest.json"
    manifest = _read_json(manifest_path)
    manifest["artifacts"]["source_csv"] = 123
    _write_json(manifest_path, manifest)

    with pytest.raises(ValueError, match="non-empty strings"):
        verify_run_evidence(tmp_path)


def test_verify_run_evidence_rejects_artifact_path_escape(tmp_path: Path) -> None:
    run_pipeline(root=tmp_path)
    manifest_path = tmp_path / "artifacts" / "run_manifest.json"
    manifest = _read_json(manifest_path)
    manifest["artifacts"]["source_csv"] = "../outside.csv"
    _write_json(manifest_path, manifest)

    with pytest.raises(ValueError, match="escapes the evidence root"):
        verify_run_evidence(tmp_path)


def test_verify_run_evidence_rejects_manifest_json_pointer_mismatch(tmp_path: Path) -> None:
    run_pipeline(root=tmp_path)
    manifest_path = tmp_path / "artifacts" / "run_manifest.json"
    manifest = _read_json(manifest_path)
    manifest["artifacts"]["manifest_json"] = "artifacts/oos_evidence.json"
    _write_json(manifest_path, manifest)

    with pytest.raises(ValueError, match="does not point to the active run manifest"):
        verify_run_evidence(tmp_path)


def test_verify_run_evidence_rejects_non_list_oos_evidence(tmp_path: Path) -> None:
    run_pipeline(root=tmp_path)
    oos_path = tmp_path / "artifacts" / "oos_evidence.json"
    _write_json(oos_path, {"not": "a list"})

    with pytest.raises(ValueError, match="OOS evidence must be a JSON array"):
        verify_run_evidence(tmp_path)


def test_verify_run_evidence_rejects_oos_count_mismatch(tmp_path: Path) -> None:
    run_pipeline(root=tmp_path)
    manifest_path = tmp_path / "artifacts" / "run_manifest.json"
    manifest = _read_json(manifest_path)
    manifest["counts"]["oos_flags"] = manifest["counts"]["oos_flags"] + 1
    _write_json(manifest_path, manifest)

    with pytest.raises(ValueError, match="OOS evidence count does not match"):
        verify_run_evidence(tmp_path)


def test_verify_run_evidence_rejects_non_object_quality_summary(tmp_path: Path) -> None:
    run_pipeline(root=tmp_path)
    summary_path = tmp_path / "artifacts" / "quality_review_summary.json"
    _write_json(summary_path, [1, 2, 3])

    with pytest.raises(ValueError, match="quality review summary must be a JSON object"):
        verify_run_evidence(tmp_path)


def test_verify_run_evidence_rejects_quality_summary_count_mismatch(tmp_path: Path) -> None:
    run_pipeline(root=tmp_path)
    summary_path = tmp_path / "artifacts" / "quality_review_summary.json"
    summary = _read_json(summary_path)
    summary["total_oos_flags"] = summary["total_oos_flags"] + 1
    _write_json(summary_path, summary)

    with pytest.raises(ValueError, match="quality review summary count does not match"):
        verify_run_evidence(tmp_path)


def test_verify_run_evidence_rejects_oos_by_rule_mismatch(tmp_path: Path) -> None:
    run_pipeline(root=tmp_path)
    summary_path = tmp_path / "artifacts" / "quality_review_summary.json"
    summary = _read_json(summary_path)
    summary["oos_by_rule"] = {"UNKNOWN-RULE": 1}
    _write_json(summary_path, summary)

    with pytest.raises(ValueError, match="rule counts do not match"):
        verify_run_evidence(tmp_path)


def test_verify_run_evidence_rejects_review_queue_length_mismatch(tmp_path: Path) -> None:
    run_pipeline(root=tmp_path)
    summary_path = tmp_path / "artifacts" / "quality_review_summary.json"
    summary = _read_json(summary_path)
    summary["review_queue"] = []
    _write_json(summary_path, summary)

    with pytest.raises(ValueError, match="queue does not match"):
        verify_run_evidence(tmp_path)


def test_verify_evidence_main_prints_verified_result(tmp_path: Path, capsys, monkeypatch) -> None:
    run_pipeline(root=tmp_path)
    monkeypatch.setattr(sys, "argv", ["verify_evidence", "--root", str(tmp_path)])

    verify_main()

    output = json.loads(capsys.readouterr().out)
    assert output["status"] == "verified"


def test_verify_evidence_main_exits_on_failure(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(sys, "argv", ["verify_evidence", "--root", str(tmp_path)])

    with pytest.raises(SystemExit, match="evidence verification failed"):
        verify_main()

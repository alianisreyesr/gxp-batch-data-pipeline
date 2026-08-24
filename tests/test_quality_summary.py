from __future__ import annotations

from src.quality_summary import SUMMARY_SCHEMA_VERSION, build_quality_review_summary


def test_quality_review_summary_groups_flags_and_preserves_queue() -> None:
    flags = [
        {
            "rule_id": "CQA-ASSAY-001",
            "batch_id": "BATCH-0003",
            "phase": "release_testing",
            "timestamp_utc": "2026-01-03T09:45:00Z",
            "parameter": "assay_pct",
            "observed_value": 87.5,
            "expected_range": "90.0..105.0",
        },
        {
            "rule_id": "CPP-TEMP-001",
            "batch_id": "BATCH-0002",
            "phase": "fermentation",
            "timestamp_utc": "2026-01-02T08:45:00Z",
            "parameter": "temperature_c",
            "observed_value": 39.2,
            "expected_range": "35.0..38.0",
        },
    ]

    summary = build_quality_review_summary(flags)

    assert summary["summary_schema_version"] == SUMMARY_SCHEMA_VERSION
    assert summary["total_oos_flags"] == 2
    assert summary["oos_by_rule"] == {"CPP-TEMP-001": 1, "CQA-ASSAY-001": 1}
    assert summary["oos_by_batch"] == {"BATCH-0002": 1, "BATCH-0003": 1}
    assert summary["oos_by_phase"] == {"fermentation": 1, "release_testing": 1}
    assert [item["batch_id"] for item in summary["review_queue"]] == ["BATCH-0002", "BATCH-0003"]

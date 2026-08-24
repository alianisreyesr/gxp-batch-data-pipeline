from __future__ import annotations

from src.quality_report import render_quality_report


def test_quality_report_renders_summary_and_escapes_values() -> None:
    summary = {
        "total_oos_flags": 1,
        "oos_by_rule": {"CPP-TEMP-001": 1},
        "oos_by_batch": {"BATCH-0002": 1},
        "review_queue": [{
            "batch_id": "BATCH-0002",
            "phase": "fermentation",
            "rule_id": "CPP-TEMP-001",
            "parameter": "temperature_c",
            "observed_value": 39.2,
            "expected_range": "<38.0",
        }],
    }

    report = render_quality_report(summary)

    assert "Synthetic Batch Quality Review" in report
    assert "Explainable OOS signals requiring review" in report
    assert "BATCH-0002" in report
    assert "&lt;38.0" in report

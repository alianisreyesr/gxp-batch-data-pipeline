from __future__ import annotations

from collections import Counter
from typing import Any


SUMMARY_SCHEMA_VERSION = "1.0"


def _count(flags: list[dict[str, object]], key: str) -> dict[str, int]:
    return dict(sorted(Counter(str(flag[key]) for flag in flags).items()))


def build_quality_review_summary(flags: list[dict[str, object]]) -> dict[str, Any]:
    """Build an explainable, portfolio-safe OOS review summary from pipeline flags."""

    review_queue = sorted(
        [
            {
                "rule_id": str(flag["rule_id"]),
                "batch_id": str(flag["batch_id"]),
                "phase": str(flag["phase"]),
                "timestamp_utc": str(flag["timestamp_utc"]),
                "parameter": str(flag["parameter"]),
                "observed_value": flag["observed_value"],
                "expected_range": str(flag["expected_range"]),
            }
            for flag in flags
        ],
        key=lambda item: (item["batch_id"], item["timestamp_utc"], item["rule_id"]),
    )

    return {
        "summary_schema_version": SUMMARY_SCHEMA_VERSION,
        "total_oos_flags": len(flags),
        "oos_by_rule": _count(flags, "rule_id"),
        "oos_by_batch": _count(flags, "batch_id"),
        "oos_by_phase": _count(flags, "phase"),
        "review_queue": review_queue,
        "safety_boundary": (
            "This summary is generated from fictional synthetic data for portfolio demonstration. "
            "It is not a manufacturing, release, quality, or patient-safety decision record."
        ),
    }

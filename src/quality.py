from __future__ import annotations

from datetime import datetime
from typing import Iterable

REQUIRED_FIELDS = (
    "batch_id", "timestamp_utc", "phase", "bioreactor_id", "temperature_c",
    "ph", "dissolved_oxygen_pct", "agitation_rpm", "assay_pct",
)

PLAUSIBLE_RANGES = {
    "temperature_c": (10.0, 50.0),
    "ph": (4.0, 10.0),
    "dissolved_oxygen_pct": (0.0, 100.0),
    "agitation_rpm": (0.0, 2000.0),
    "assay_pct": (0.0, 150.0),
}


def _parse_utc(value: str) -> datetime:
    if not value or not value.endswith("Z"):
        raise ValueError("timestamp must be explicit UTC with Z suffix")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.utcoffset() is None or parsed.utcoffset().total_seconds() != 0:
        raise ValueError("timestamp must be UTC")
    return parsed


def validate_rows(rows: Iterable[dict[str, object]]) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    accepted: list[dict[str, object]] = []
    rejected: list[dict[str, object]] = []
    seen_keys: set[tuple[str, str, str]] = set()
    last_timestamp: dict[tuple[str, str], datetime] = {}

    for source_row in rows:
        row = dict(source_row)
        reasons: list[str] = []
        for field in REQUIRED_FIELDS:
            if field not in row or row[field] in (None, ""):
                reasons.append(f"missing:{field}")

        parsed_timestamp: datetime | None = None
        if row.get("timestamp_utc") not in (None, ""):
            try:
                parsed_timestamp = _parse_utc(str(row["timestamp_utc"]))
            except (TypeError, ValueError):
                reasons.append("invalid:timestamp_utc")

        for field, (minimum, maximum) in PLAUSIBLE_RANGES.items():
            if row.get(field) in (None, ""):
                continue
            try:
                value = float(row[field])
            except (TypeError, ValueError):
                reasons.append(f"invalid:{field}")
                continue
            if not minimum <= value <= maximum:
                reasons.append(f"out_of_plausible_range:{field}")

        if all(row.get(name) not in (None, "") for name in ("batch_id", "phase", "timestamp_utc")):
            key = (str(row["batch_id"]), str(row["phase"]), str(row["timestamp_utc"]))
            if key in seen_keys:
                reasons.append("duplicate:record_key")
            else:
                seen_keys.add(key)

        if parsed_timestamp is not None and row.get("batch_id") and row.get("phase"):
            stream_key = (str(row["batch_id"]), str(row["phase"]))
            previous = last_timestamp.get(stream_key)
            if previous is not None and parsed_timestamp <= previous:
                reasons.append("non_monotonic:timestamp_utc")
            last_timestamp[stream_key] = parsed_timestamp

        if reasons:
            rejected_row = dict(row)
            rejected_row["rejection_reasons"] = ";".join(sorted(set(reasons)))
            rejected.append(rejected_row)
        else:
            accepted.append(row)
    return accepted, rejected

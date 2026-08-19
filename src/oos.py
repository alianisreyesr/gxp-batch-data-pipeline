from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Iterable

RULES = {
    "temperature_c": (35.0, 38.0, "CPP-TEMP-001"),
    "ph": (6.8, 7.4, "CPP-PH-001"),
    "dissolved_oxygen_pct": (30.0, 100.0, "CPP-DO-001"),
    "assay_pct": (90.0, 105.0, "CQA-ASSAY-001"),
}


def evaluate_oos(rows: Iterable[dict[str, object]]) -> list[dict[str, object]]:
    flags: list[dict[str, object]] = []
    for row in rows:
        for field, (minimum, maximum, rule_id) in RULES.items():
            value = float(row[field])
            if value < minimum or value > maximum:
                flags.append({
                    "rule_id": rule_id,
                    "batch_id": row["batch_id"],
                    "phase": row["phase"],
                    "timestamp_utc": row["timestamp_utc"],
                    "parameter": field,
                    "observed_value": value,
                    "expected_range": f"{minimum}..{maximum}",
                })
    return flags


def main() -> None:
    parser = argparse.ArgumentParser(description="Emit explainable OOS flags from accepted telemetry.")
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    with args.input.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    print(json.dumps(evaluate_oos(rows), indent=2))


if __name__ == "__main__":
    main()

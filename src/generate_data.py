from __future__ import annotations

import argparse
import csv
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

PHASES = ("fermentation", "purification", "formulation", "release_testing")
FIELDNAMES = (
    "batch_id", "timestamp_utc", "phase", "bioreactor_id", "temperature_c",
    "ph", "dissolved_oxygen_pct", "agitation_rpm", "assay_pct",
)


def generate_rows(seed: int = 42, batches: int = 3, rows_per_phase: int = 8) -> list[dict[str, object]]:
    rng = random.Random(seed)
    rows: list[dict[str, object]] = []
    start = datetime(2026, 1, 1, 8, 0, tzinfo=timezone.utc)
    for batch_index in range(1, batches + 1):
        batch_id = f"BATCH-{batch_index:04d}"
        for phase_index, phase in enumerate(PHASES):
            phase_start = start + timedelta(days=batch_index - 1, hours=phase_index * 6)
            for row_index in range(rows_per_phase):
                timestamp = phase_start + timedelta(minutes=row_index * 15)
                temperature = round(rng.uniform(35.5, 37.5), 2)
                ph = round(rng.uniform(6.9, 7.3), 2)
                do = round(rng.uniform(35, 75), 2)
                rpm = round(rng.uniform(250, 850), 1)
                assay = round(rng.uniform(94, 102), 2)
                if batch_index == 2 and phase == "fermentation" and row_index == 3:
                    temperature = 39.2
                if batch_index == 3 and phase == "release_testing" and row_index == rows_per_phase - 1:
                    assay = 87.5
                rows.append({
                    "batch_id": batch_id,
                    "timestamp_utc": timestamp.isoformat().replace("+00:00", "Z"),
                    "phase": phase,
                    "bioreactor_id": f"BR-{(batch_index % 3) + 1:02d}",
                    "temperature_c": temperature,
                    "ph": ph,
                    "dissolved_oxygen_pct": do,
                    "agitation_rpm": rpm,
                    "assay_pct": assay,
                })
    return rows


def write_csv(rows: list[dict[str, object]], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate deterministic synthetic batch telemetry.")
    parser.add_argument("--output", type=Path, default=Path("data/synthetic/batch_telemetry.csv"))
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--batches", type=int, default=3)
    parser.add_argument("--rows-per-phase", type=int, default=8)
    args = parser.parse_args()
    rows = generate_rows(args.seed, args.batches, args.rows_per_phase)
    write_csv(rows, args.output)
    print(f"generated_rows={len(rows)} output={args.output}")


if __name__ == "__main__":
    main()

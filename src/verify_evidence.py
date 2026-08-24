from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from src.pipeline import sha256_file

REQUIRED_ARTIFACTS = (
    "source_csv",
    "rejected_csv",
    "duckdb",
    "oos_json",
    "manifest_json",
)


def _artifact_path(root: Path, value: object) -> Path:
    if not isinstance(value, str) or not value:
        raise ValueError("manifest artifact paths must be non-empty strings")

    candidate = (root / value).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError as exc:
        raise ValueError(f"artifact path escapes the evidence root: {value}") from exc
    return candidate


def verify_run_evidence(root: Path = Path(".")) -> dict[str, Any]:
    """Validate a pipeline run manifest against its local evidence artifacts."""

    root = root.resolve()
    manifest_path = root / "artifacts" / "run_manifest.json"
    if not manifest_path.is_file():
        raise FileNotFoundError(f"run manifest not found: {manifest_path}")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict):
        raise ValueError("run manifest must be a JSON object")

    artifacts = manifest.get("artifacts")
    counts = manifest.get("counts")
    source_sha256 = manifest.get("source_sha256")
    run_id = manifest.get("run_id")

    if not isinstance(artifacts, dict):
        raise ValueError("run manifest has no artifact map")
    if not isinstance(counts, dict):
        raise ValueError("run manifest has no counts map")
    if not isinstance(source_sha256, str) or len(source_sha256) != 64:
        raise ValueError("run manifest has an invalid source SHA-256")
    if run_id != f"run-{source_sha256[:16]}":
        raise ValueError("run ID does not match the source SHA-256")

    resolved = {name: _artifact_path(root, artifacts.get(name)) for name in REQUIRED_ARTIFACTS}
    for name, path in resolved.items():
        if not path.is_file():
            raise FileNotFoundError(f"required {name} artifact not found: {path}")

    if resolved["manifest_json"] != manifest_path.resolve():
        raise ValueError("manifest_json does not point to the active run manifest")
    if sha256_file(resolved["source_csv"]) != source_sha256:
        raise ValueError("source CSV SHA-256 does not match the run manifest")

    flags = json.loads(resolved["oos_json"].read_text(encoding="utf-8"))
    if not isinstance(flags, list):
        raise ValueError("OOS evidence must be a JSON array")
    if counts.get("oos_flags") != len(flags):
        raise ValueError("OOS evidence count does not match the run manifest")

    return {
        "status": "verified",
        "run_id": run_id,
        "source_sha256": source_sha256,
        "counts": counts,
        "checked_artifacts": sorted(str(path.relative_to(root)) for path in resolved.values()),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify local synthetic pipeline run evidence.")
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()

    try:
        result = verify_run_evidence(args.root)
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
        raise SystemExit(f"evidence verification failed: {exc}") from exc

    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

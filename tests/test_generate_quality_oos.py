from src.generate_data import generate_rows
from src.oos import evaluate_oos
from src.quality import validate_rows


def test_generation_is_deterministic() -> None:
    assert generate_rows(seed=7, batches=1, rows_per_phase=2) == generate_rows(seed=7, batches=1, rows_per_phase=2)


def test_generated_rows_pass_quality_gate() -> None:
    rows = generate_rows(seed=42, batches=3, rows_per_phase=8)
    accepted, rejected = validate_rows(rows)
    assert len(accepted) == len(rows)
    assert rejected == []


def test_invalid_row_is_quarantined_with_reason() -> None:
    row = generate_rows(seed=1, batches=1, rows_per_phase=1)[0]
    row["ph"] = ""
    accepted, rejected = validate_rows([row])
    assert accepted == []
    assert "missing:ph" in rejected[0]["rejection_reasons"]


def test_duplicate_record_key_is_rejected() -> None:
    row = generate_rows(seed=1, batches=1, rows_per_phase=1)[0]
    accepted, rejected = validate_rows([row, dict(row)])
    assert len(accepted) == 1
    assert len(rejected) == 1
    assert "duplicate:record_key" in rejected[0]["rejection_reasons"]


def test_oos_flags_are_explainable() -> None:
    rows = generate_rows(seed=42, batches=3, rows_per_phase=8)
    accepted, _ = validate_rows(rows)
    flags = evaluate_oos(accepted)
    assert {flag["rule_id"] for flag in flags} >= {"CPP-TEMP-001", "CQA-ASSAY-001"}
    for flag in flags:
        assert flag["batch_id"]
        assert flag["parameter"]
        assert flag["expected_range"]

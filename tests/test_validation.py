"""Tests fuer tools/validate_data.py gegen die Fixtures unter tests/fixtures/."""

from __future__ import annotations

from pathlib import Path

import pytest
from validate_data import run_validation

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"
VALID_ROOT = FIXTURES_DIR / "valid"
INVALID_ROOT = FIXTURES_DIR / "invalid"


def _run(data_root: Path):
    docs_root = data_root / "docs"
    return run_validation(verbose=False, data_root=data_root, docs_root=docs_root)


def test_valid_fixture_set_has_no_errors():
    report = _run(VALID_ROOT)
    messages = "\n".join(issue.format() for issue in report.issues)
    assert report.error_count == 0, f"unexpected errors:\n{messages}"


INVALID_SCENARIOS = {
    "duplicate_id": "duplicate id",
    "filename_id_mismatch": "does not match filename",
    "missing_source": "no source",
    "unknown_predicate": "not defined in data/vocabularies/predicates.yaml",
    "unknown_entity": "references missing entity",
    "unknown_study": "references missing study",
    "invalid_evidence_category": "is not one of",
    "invalid_certainty": "is not one of",
    "invalid_status": "is not one of",
    "active_claim_without_review": "requires review.last_reviewed_at",
    "merchant_claim_sole_evidence": "merchant_claim must not be the sole active evidence category",
    "claim_multiple_object_variants": "is not valid under any of the given schemas",
    "invalid_source_date": "does not match",
    "retracted_source_reference": "relies exclusively on retracted source",
    "article_missing_claim": "references missing claim",
}


@pytest.mark.parametrize("scenario", sorted(INVALID_SCENARIOS))
def test_invalid_scenario_reports_expected_error(scenario: str):
    data_root = INVALID_ROOT / scenario
    report = _run(data_root)
    assert report.error_count > 0, f"expected at least one error for scenario '{scenario}'"

    expected_substring = INVALID_SCENARIOS[scenario]
    messages = [issue.message for issue in report.issues if issue.level == "ERROR"]
    assert any(expected_substring in message for message in messages), (
        f"scenario '{scenario}': expected an error containing {expected_substring!r}, got:\n"
        + "\n".join(messages)
    )


def test_exit_code_zero_only_when_no_errors():
    valid_report = _run(VALID_ROOT)
    assert valid_report.error_count == 0

    invalid_report = _run(INVALID_ROOT / "unknown_entity")
    assert invalid_report.error_count > 0

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
    "merchant_claim_sole_evidence": "merchant_claim must not back an active, medically relevant claim_type",
    "claim_multiple_object_variants": "is not valid under any of the given schemas",
    "invalid_source_date": "does not match",
    "retracted_source_reference": "relies exclusively on retracted source",
    "article_missing_claim": "references missing claim",
    # --- Hardening pass (Review 2) ---
    "exempt_wrong_claim_type": "can never use source_requirement: exempt",
    "exempt_without_reason": "is not of type 'string'",
    "certainty_rationale_null": "is not of type 'string'",
    "certainty_rationale_empty": "should be non-empty",
    "clinical_evidence_merchant_only": "regardless of the assigned evidence_category or certainty",
    "limited_evidence_personal_only": "regardless of the assigned evidence_category or certainty",
    "certainty_moderate_merchant_only": "regardless of the assigned evidence_category or certainty",
    "merchant_only_wrong_category": "is not classified as evidence_category: merchant_claim",
    "personal_only_wrong_category": "is not classified as evidence_category: personal_experience",
    "unsupported_schema_version": "1.0.0",
    "invalid_calendar_dates": "date",
    "article_missing_frontmatter": "missing YAML frontmatter",
    "active_claim_no_supporting_direction": "no link with direction 'supports' or 'mixed'",
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


def test_valid_exempt_identity_claim_has_no_errors():
    """Positiver Gegentest zu item 1: source_requirement exempt ist fuer claim_type identity zulaessig."""
    report = _run(VALID_ROOT)
    messages = "\n".join(issue.format() for issue in report.issues)
    exempt_errors = [
        issue for issue in report.issues
        if issue.level == "ERROR" and "claim-a0000000-0000-4000-8000-000000000003" in issue.file
    ]
    assert not exempt_errors, f"unexpected errors on the valid exempt claim:\n{messages}"


def test_duplicate_sources_detect_each_identifier_type():
    report = _run(INVALID_ROOT / "duplicate_sources")
    error_messages = [issue.message for issue in report.issues if issue.level == "ERROR"]

    assert any("duplicate DOI" in m for m in error_messages), error_messages
    assert any("duplicate PMID" in m for m in error_messages), error_messages
    assert any("duplicate PMCID" in m for m in error_messages), error_messages
    assert any("duplicate ISBN" in m for m in error_messages), error_messages

    # Identische kanonische URLs sind nur eine Warnung, kein Fehler.
    assert not any("duplicate" in m and "URL" in m for m in error_messages), error_messages
    warning_messages = [issue.message for issue in report.issues if issue.level == "WARNING"]
    assert any("canonical URL" in m for m in warning_messages), warning_messages


def test_partial_retraction_is_a_warning_not_an_error():
    report = _run(INVALID_ROOT / "partial_retraction_warning")
    messages = "\n".join(issue.format() for issue in report.issues)
    assert report.error_count == 0, f"expected no errors, only a warning:\n{messages}"
    assert any(
        issue.level == "WARNING" and "at least one retracted source alongside" in issue.message
        for issue in report.issues
    ), messages

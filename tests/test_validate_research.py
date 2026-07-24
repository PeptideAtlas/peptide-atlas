"""Tests fuer tools/validate_research.py gegen die Fixtures unter tests/fixtures/research/."""

from __future__ import annotations

from pathlib import Path

import pytest
from validate_research import run_validation

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures" / "research"
VALID_ROOT = FIXTURES_DIR / "valid"
INVALID_ROOT = FIXTURES_DIR / "invalid"


def _run(scenario_dir: Path):
    research_root = scenario_dir / "research"
    data_root = scenario_dir / "data"
    return run_validation(verbose=False, research_root=research_root, data_root=data_root)


def test_valid_fixture_set_has_no_errors():
    report = _run(VALID_ROOT)
    messages = "\n".join(issue.format() for issue in report.issues)
    assert report.error_count == 0, f"unexpected errors:\n{messages}"


def test_valid_fixture_set_loads_expected_object_counts():
    report = _run(VALID_ROOT)
    assert report.error_count == 0
    # Kein direkter Zugriff auf die geladenen Objekte ueber Report -- stattdessen erneut laden
    # und die Zaehlung ueber run_validation(verbose=True)-Ausgabe indirekt pruefen: einfacher,
    # load_research_dataset direkt zu importieren und aufzurufen.
    from validate_research import load_research_dataset
    from _datalib import build_schema_registry, Report
    from _researchlib import load_all_research_vocabularies

    registry, schemas = build_schema_registry()
    vocabularies = load_all_research_vocabularies()
    report2 = Report()
    objects = load_research_dataset(VALID_ROOT / "research", report2, registry, schemas, vocabularies)
    assert len(objects["protocol"]) == 1
    assert len(objects["search_run"]) == 1
    assert len(objects["screening_record"]) == 3
    assert len(objects["extraction_record"]) == 1
    decisions = {obj.data["decision"] for obj in objects["screening_record"].values()}
    assert decisions == {"include", "exclude", "duplicate"}


INVALID_SCENARIOS = {
    "missing_protocol": "references missing protocol",
    "missing_search_run": "references missing search run",
    "exclude_without_reason": "is not one of",
    "duplicate_without_target": "is not of type 'string'",
    "self_referencing_duplicate": "cannot mark itself as duplicate_of",
    "cyclical_duplicate": "cyclical duplicate_of chain detected",
    "extraction_for_non_included_candidate": "extraction is only allowed for included candidates",
    "verified_without_verifier": "is not of type 'string'",
    "approved_without_review": "should be non-empty",
    "missing_canonical_source": "does not exist under data/sources/**",
    "missing_canonical_study": "does not exist under data/entities/studies/**",
    "invalid_calendar_date": "is not a 'date'",
    "wrong_schema_version": "was expected",
    "filename_id_mismatch": "does not match filename",
    "unwanted_binary": "unexpected binary file",
    "cross_namespace_leak": "references missing protocol",
    "search_run_missing_query": "should be non-empty",
    "search_run_negative_result_count": "is less than the minimum",
    "candidate_claim_missing_locator": "is not valid under any of the given schemas",
    "candidate_claim_active_flag": "Additional properties are not allowed",
    "long_embedded_passage": "is too long",
}


@pytest.mark.parametrize("scenario", sorted(INVALID_SCENARIOS))
def test_invalid_scenario_reports_expected_error(scenario: str):
    scenario_dir = INVALID_ROOT / scenario
    report = _run(scenario_dir)
    assert report.error_count > 0, f"expected at least one error for scenario '{scenario}'"

    expected_substring = INVALID_SCENARIOS[scenario]
    messages = [issue.message for issue in report.issues if issue.level == "ERROR"]
    assert any(expected_substring in message for message in messages), (
        f"scenario '{scenario}': expected an error containing {expected_substring!r}, got:\n"
        + "\n".join(messages)
    )


def test_cross_namespace_leak_does_not_affect_production_dataset():
    """Der Screening-/Suchlauf-Namensraum von research/examples/ ist eigenstaendig -- ein
    Beispieldatensatz darf nicht unbemerkt auf ein produktives Protokoll verweisen und auch
    nicht umgekehrt in die produktive Validierung durchsickern."""
    scenario_dir = INVALID_ROOT / "cross_namespace_leak"
    report = _run(scenario_dir)
    # Der Fehler muss aus der Beispiel-Datei stammen, nicht aus der produktiven.
    offending = [
        issue for issue in report.issues
        if issue.level == "ERROR" and "examples" in issue.file
    ]
    assert offending, [issue.format() for issue in report.issues]


def test_exit_code_zero_only_when_no_errors():
    valid_report = _run(VALID_ROOT)
    assert valid_report.error_count == 0

    invalid_report = _run(INVALID_ROOT / "missing_protocol")
    assert invalid_report.error_count > 0

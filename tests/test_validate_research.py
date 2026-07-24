"""Tests fuer tools/validate_research.py gegen die Fixtures unter tests/fixtures/research/."""

from __future__ import annotations

from pathlib import Path

import pytest
from validate_research import run_validation

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures" / "research"
VALID_ROOT = FIXTURES_DIR / "valid"
INVALID_ROOT = FIXTURES_DIR / "invalid"
VALID_SCENARIOS_ROOT = FIXTURES_DIR / "valid_scenarios"


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
    # Phase 4A Review-Haertung: Protokollkonsistenz.
    "protocol_version_id_mismatch": "does not match the -v1 suffix",
    "search_run_on_draft_protocol": "with status 'draft'",
    "screening_search_run_different_protocol": "belongs to protocol",
    "extraction_screening_different_protocol": "does not match the referenced screening record's protocol_id",
    "conflicting_canonical_source_id": "conflicts with canonical_source_id",
    "discovery_only_google_scholar_primary": "'discovery_only' was expected",
    "discovery_only_manufacturer_registry_supplementary": "'discovery_only' was expected",
    # Deduplizierung.
    "dedup_doi_duplicate_not_marked": "duplicate doi",
    "dedup_doi_url_and_prefix_form": "duplicate doi",
    "dedup_pmid_duplicate": "duplicate pmid",
    "dedup_pmcid_duplicate": "duplicate pmcid",
    "dedup_nct_duplicate": "duplicate nct_id",
    # Screening-Zustandsmaschine und Zweitpruefung.
    "dual_review_missing": "requires second_review",
    "dual_review_same_reviewer": "reviewer independence",
    "unresolved_contradiction": "must stay 'uncertain'",
    "extraction_for_unconfirmed_screening": "must stay 'uncertain'",
    "final_include_without_full_text": "requires full_text_status",
    # Extraktionsverifikation.
    "verifier_equals_extractor": "verified_by must differ",
    # Screening-Historie.
    "decision_history_missing": "is a required property",
    "decision_history_mismatch": "does not match the top-level fields",
    "duplicate_candidate_working_id": "duplicate value",
    # Claim-Promotion.
    "promotion_missing_extraction": "references missing extraction record",
    "promotion_missing_candidate": "is not present in extraction record",
    "promotion_before_verification": "is not extraction_status: verified",
    "promoted_without_canonical_claim": "is not of type 'string'",
    "rejected_with_canonical_claim": "is not of type 'null'",
    "duplicate_active_promotion": "more than one active",
    # Sonstige Konsistenz.
    "unsafe_export_reference": "must be a relative path",
    "invalid_date_order": "out of order",
    "duplicate_research_question_id": "duplicate value",
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


VALID_SCENARIO_NAMES = sorted(p.name for p in VALID_SCENARIOS_ROOT.iterdir()) if VALID_SCENARIOS_ROOT.exists() else []


@pytest.mark.parametrize("scenario", VALID_SCENARIO_NAMES)
def test_valid_scenario_reports_no_errors(scenario: str):
    """Gezielte positive Gegenstuecke zu einzelnen INVALID_SCENARIOS-Faellen -- stellt sicher,
    dass die jeweilige Regel nicht ueberscharf ist (z. B. dass ein korrekt als duplicate
    markierter Zweitdatensatz oder eine gueltige Adjudikation tatsaechlich akzeptiert wird)."""
    report = _run(VALID_SCENARIOS_ROOT / scenario)
    messages = "\n".join(issue.format() for issue in report.issues)
    assert report.error_count == 0, f"scenario '{scenario}': unexpected errors:\n{messages}"


def test_exit_code_zero_only_when_no_errors():
    valid_report = _run(VALID_ROOT)
    assert valid_report.error_count == 0

    invalid_report = _run(INVALID_ROOT / "missing_protocol")
    assert invalid_report.error_count > 0

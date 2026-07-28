"""Tests fuer Phase 4B-1B-2 (siehe ADR-0058): related_records[]/relationship_metadata,
derive_workflow_state(), die Kollisionsgruppen-Konnektivitaetspruefung in check_deduplication,
die PubMed-publication_types-Ableitung und tools/refresh_candidate_source_types.py.

Wie tests/test_validate_research_candidate_manifests.py baut dieses Modul die Recherche-
Datensaetze programmatisch in ein repo-gebundenes tmp_path-Verzeichnis (tools/_datalib.py::
relative() verlangt Pfade unter REPO_ROOT).
"""

from __future__ import annotations

import shutil
import uuid as uuid_lib
from pathlib import Path

import pytest
import yaml
from _researchlib import (
    RELATIONSHIP_TYPE_INVERSE,
    SYSTEM_SCREENING_INITIALIZER_ACTOR,
    WORKFLOW_STATE_FINALIZED,
    WORKFLOW_STATE_SYSTEM_INITIALIZED,
    WORKFLOW_STATE_UNDER_HUMAN_REVIEW,
    derive_source_type_from_pubmed_publication_types,
    derive_workflow_state,
)
from validate_research import run_validation

import refresh_candidate_source_types as refresh_tool

_SCRATCH_ROOT = Path(__file__).resolve().parent / "fixtures" / "_scratch_deduplication_relationships"


@pytest.fixture
def tmp_path():
    path = _SCRATCH_ROOT / uuid_lib.uuid4().hex
    path.mkdir(parents=True, exist_ok=True)
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)


PROTOCOL_ID = "research-protocol-test-substance-v1"
OTHER_PROTOCOL_ID = "research-protocol-other-substance-v1"
SEARCH_RUN = "search-run-80000000-0000-4000-8000-000000000001"
RESULT_MANIFEST = "search-result-manifest-80000000-0000-4000-8000-000000000001"
CANDIDATE_MANIFEST_ID = "candidate-manifest-80000000-0000-4000-8000-000000000001"
OTHER_CANDIDATE_MANIFEST_ID = "candidate-manifest-80000000-0000-4000-8000-000000000002"

CAND_A = "research-candidate-80000000-0000-4000-8000-000000000001"
CAND_B = "research-candidate-80000000-0000-4000-8000-000000000002"
CAND_C = "research-candidate-80000000-0000-4000-8000-000000000003"

SCREENING_A = "screening-record-80000000-0000-4000-8000-000000000001"
SCREENING_B = "screening-record-80000000-0000-4000-8000-000000000002"
SCREENING_C = "screening-record-80000000-0000-4000-8000-000000000003"

CAND_ID_TO_PMID = {CAND_A: "100", CAND_B: "101", CAND_C: "102"}


def _protocol(protocol_id: str = PROTOCOL_ID) -> dict:
    return {
        "schema_version": "1.0.0",
        "id": protocol_id,
        "title": "Test Research Protocol",
        "subject": {"working_name": "Test Substance"},
        "version": 1,
        "status": "approved",
        "objectives": [{"de": "Testdaten."}],
        "research_questions": [{"id": "rq-1", "topic": "identity", "question": {"de": "Testfrage."}}],
        "scope": {"description": {"de": "Test."}, "in_scope": ["Test"], "out_of_scope": []},
        "planned_information_sources": [{"database": "pubmed", "role": "primary", "notes": None}],
        "planned_search_concepts": ["test substance"],
        "eligibility": {"inclusion_criteria": ["Testkriterium"], "exclusion_criteria": ["Testausschlusskriterium"]},
        "deduplication_policy": {"description": {"de": "Test."}, "identifier_priority": ["doi"], "manual_review_required": True},
        "screening_policy": {
            "description": {"de": "Test."}, "stages": ["deduplication", "title_abstract", "full_text", "final"],
            "dual_reviewer_stages": [],
        },
        "extraction_policy": {"description": {"de": "Test."}, "verification_required": True, "fields_to_extract": ["identity"]},
        "evidence_appraisal_policy": {"description": {"de": "Test."}},
        "claim_promotion_policy": {"description": {"de": "Test."}, "requires_second_review": True},
        "amendment_policy": {"description": {"de": "Test."}},
        "created_at": "2026-01-01",
        "updated_at": "2026-01-01",
        "review": {"last_reviewed_at": "2026-01-01", "reviewers": ["reviewer-1"], "approval_decision": "Freigegeben fuer Testzwecke."},
    }


def _search_run(protocol_id: str = PROTOCOL_ID) -> dict:
    return {
        "schema_version": "1.0.0",
        "id": SEARCH_RUN,
        "protocol_id": protocol_id,
        "database": "pubmed",
        "interface": "NCBI E-utilities ESearch (test)",
        "interface_profile": {"id": "ncbi_eutils_esearch_v1", "rationale": None},
        "executed_at": "2026-01-01T10:00:00Z",
        "executed_by": "reviewer-1",
        "exact_query": "test substance",
        "filters": {},
        "request_parameters": {"db": "pubmed", "retmode": "json", "retmax": 1000, "retstart": 0},
        "result_capture": {"status": "complete", "manifest_id": RESULT_MANIFEST, "rationale": None},
        "date_range": {"from": None, "to": None},
        "result_count": 3,
        "export_reference": "research/raw/test/x.json",
        "notes": None,
        "status": "executed",
        "created_at": "2026-01-01",
        "updated_at": "2026-01-01",
        "review": {"last_reviewed_at": None, "reviewers": []},
    }


def _result_manifest(identifiers: list[str]) -> dict:
    from _researchlib import compute_manifest_sha256

    return {
        "schema_version": "1.0.0",
        "id": RESULT_MANIFEST,
        "search_run_id": SEARCH_RUN,
        "identifier_type": "pmid",
        "identifiers": identifiers,
        "count": len(identifiers),
        "sha256": compute_manifest_sha256(identifiers),
        "source_export_reference": "research/raw/test/x.json",
        "created_at": "2026-01-01",
        "updated_at": "2026-01-01",
        "notes": None,
    }


def _candidate(candidate_id: str, pmid: str, metadata_status: str = "fetched", publication_types=None) -> dict:
    metadata = None
    provenance = None
    if metadata_status == "fetched":
        metadata = {
            "title": "A Test Title", "publication_year": 2024, "journal": "Test Journal",
            "publication_types": publication_types if publication_types is not None else ["Journal Article"],
            "doi": None, "pmcid": None, "authors": ["Doe J"], "abstract_available": True, "language": "en",
        }
        provenance = {
            "source_interface": "NCBI E-utilities ESummary", "retrieved_at": "2026-01-02T00:00:00Z",
            "request_reference": f"NCBI ESummary db=pubmed id={pmid}", "response_locator": None,
        }
    return {
        "candidate_id": candidate_id,
        "primary_identifier": {"namespace": "pmid", "value": pmid},
        "discovered_in_search_run_ids": [SEARCH_RUN],
        "metadata": metadata,
        "metadata_status": metadata_status,
        "metadata_fetch_note": None,
        "metadata_provenance": provenance,
    }


def _candidate_manifest(manifest_id: str, candidates: list[dict], protocol_id: str = PROTOCOL_ID) -> dict:
    return {
        "schema_version": "1.0.0",
        "id": manifest_id,
        "protocol_id": protocol_id,
        "database": "pubmed",
        "identifier_namespace": "pmid",
        "source_search_run_ids": [SEARCH_RUN],
        "source_result_manifest_ids": [RESULT_MANIFEST],
        "candidate_count": len(candidates),
        "candidates": candidates,
        "created_at": "2026-01-01",
        "updated_at": "2026-01-02",
    }


def _relationship(related_manifest_id, related_candidate_id, rel_type, identified_by="reviewer-2", evidence=None):
    return {
        "related_candidate_manifest_id": related_manifest_id,
        "related_candidate_id": related_candidate_id,
        "relationship_type": rel_type,
        "rationale": "Test rationale for the relationship.",
        "relationship_metadata": {
            "identified_by": identified_by,
            "identified_at": "2026-01-02",
            "evidence_source": evidence or ["doi"],
        },
    }


def _screening_record(
    record_id, *, candidate_manifest_id=None, candidate_id=None, doi=None, pmid=None,
    decision="include", decision_stage="title_abstract", decided_by="reviewer-1",
    duplicate_of=None, decision_reason=None, related_records=None, second_review=None,
    full_text_status="not_yet_obtained", protocol_id=PROTOCOL_ID, candidate_title="Test Candidate",
):
    related_records = related_records or []
    if pmid is None and candidate_id is not None:
        pmid = CAND_ID_TO_PMID.get(candidate_id)
    entry = {
        "sequence": 1, "stage": decision_stage, "primary_decision": decision,
        "primary_decision_reason": decision_reason, "decision": decision, "decision_reason": decision_reason,
        "duplicate_of": duplicate_of, "primary_duplicate_of": duplicate_of,
        "decided_by": decided_by, "decided_at": "2026-01-01", "full_text_status": full_text_status,
        "second_review": second_review,
    }
    return {
        "schema_version": "1.0.0", "id": record_id, "protocol_id": protocol_id,
        "search_run_ids": [SEARCH_RUN],
        "candidate_identifiers": {"doi": doi, "pmid": pmid, "pmcid": None, "nct_id": None, "isbn": None, "url": None},
        "candidate_title": candidate_title, "candidate_source_type": "peer_reviewed_publication",
        "decision": decision, "decision_stage": decision_stage, "decision_reason": decision_reason,
        "duplicate_of": duplicate_of, "full_text_status": full_text_status,
        "screened_by": decided_by, "screened_at": "2026-01-01", "second_review": second_review,
        "decision_history": [entry],
        "related_records": related_records,
        "canonical_source_id": None, "candidate_manifest_id": candidate_manifest_id, "candidate_id": candidate_id,
        "created_at": "2026-01-01", "updated_at": "2026-01-01",
    }


def write_tree(root: Path, tree: dict[str, dict]) -> None:
    for relative_path, data in tree.items():
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            yaml.safe_dump(data, handle, sort_keys=False, allow_unicode=True)


def base_tree() -> dict[str, dict]:
    return {
        f"research/protocols/{PROTOCOL_ID}.yaml": _protocol(),
        f"research/search_runs/{SEARCH_RUN}.yaml": _search_run(),
        f"research/search_results/{RESULT_MANIFEST}.yaml": _result_manifest(["100", "101", "102"]),
        f"research/candidates/{CANDIDATE_MANIFEST_ID}.yaml": _candidate_manifest(
            CANDIDATE_MANIFEST_ID,
            [
                _candidate(CAND_A, "100"),
                _candidate(CAND_B, "101"),
                _candidate(CAND_C, "102"),
            ],
        ),
    }


def _run(tmp_path: Path, tree: dict[str, dict]):
    write_tree(tmp_path, tree)
    return run_validation(verbose=False, research_root=tmp_path / "research", data_root=tmp_path / "data")


def _errors(report):
    return [i.message for i in report.issues if i.level == "ERROR"]


def _warnings(report):
    return [i.message for i in report.issues if i.level == "WARNING"]


# ---------------------------------------------------------------------------
# check_screening_related_records
# ---------------------------------------------------------------------------


def test_valid_inverse_relationship_pair(tmp_path: Path):
    tree = base_tree()
    tree[f"research/screening/{SCREENING_A}.yaml"] = _screening_record(
        SCREENING_A, candidate_manifest_id=CANDIDATE_MANIFEST_ID, candidate_id=CAND_A, doi="10.1000/shared",
        related_records=[_relationship(CANDIDATE_MANIFEST_ID, CAND_B, "replies_to")],
    )
    tree[f"research/screening/{SCREENING_B}.yaml"] = _screening_record(
        SCREENING_B, candidate_manifest_id=CANDIDATE_MANIFEST_ID, candidate_id=CAND_B, doi="10.1000/shared",
        related_records=[_relationship(CANDIDATE_MANIFEST_ID, CAND_A, "has_reply")],
    )
    report = _run(tmp_path, tree)
    assert report.error_count == 0, _errors(report) + _warnings(report)


def test_missing_inverse_is_error_when_target_record_exists(tmp_path: Path):
    """CSO-Review Runde 3: sobald fuer den Ziel-Kandidaten bereits ein Screening Record existiert,
    ist eine fehlende Gegenrichtung ein FEHLER, nicht mehr nur eine Warnung."""
    tree = base_tree()
    tree[f"research/screening/{SCREENING_A}.yaml"] = _screening_record(
        SCREENING_A, candidate_manifest_id=CANDIDATE_MANIFEST_ID, candidate_id=CAND_A, doi="10.1000/shared",
        related_records=[_relationship(CANDIDATE_MANIFEST_ID, CAND_B, "replies_to")],
    )
    tree[f"research/screening/{SCREENING_B}.yaml"] = _screening_record(
        SCREENING_B, candidate_manifest_id=CANDIDATE_MANIFEST_ID, candidate_id=CAND_B, doi="10.1000/shared",
    )
    report = _run(tmp_path, tree)
    assert any(
        "this record must document the inverse relationship" in m and "'has_reply'" in m
        for m in _errors(report)
    ), _errors(report)


def test_missing_inverse_is_warning_when_target_has_no_screening_record(tmp_path: Path):
    """Warnung bleibt ausschliesslich dem Fall vorbehalten, dass fuer den Ziel-Kandidaten noch KEIN
    Screening Record existiert -- hier wird bewusst KEIN Screening Record fuer CAND_B angelegt."""
    tree = base_tree()
    tree[f"research/screening/{SCREENING_A}.yaml"] = _screening_record(
        SCREENING_A, candidate_manifest_id=CANDIDATE_MANIFEST_ID, candidate_id=CAND_A, doi="10.1000/shared",
        related_records=[_relationship(CANDIDATE_MANIFEST_ID, CAND_B, "replies_to")],
    )
    report = _run(tmp_path, tree)
    assert report.error_count == 0, _errors(report)
    assert any(
        "does not have a screening record yet" in m for m in _warnings(report)
    ), _warnings(report)


def test_wrong_inverse_type_is_error(tmp_path: Path):
    tree = base_tree()
    tree[f"research/screening/{SCREENING_A}.yaml"] = _screening_record(
        SCREENING_A, candidate_manifest_id=CANDIDATE_MANIFEST_ID, candidate_id=CAND_A, doi="10.1000/shared",
        related_records=[_relationship(CANDIDATE_MANIFEST_ID, CAND_B, "replies_to")],
    )
    tree[f"research/screening/{SCREENING_B}.yaml"] = _screening_record(
        SCREENING_B, candidate_manifest_id=CANDIDATE_MANIFEST_ID, candidate_id=CAND_B, doi="10.1000/shared",
        related_records=[_relationship(CANDIDATE_MANIFEST_ID, CAND_A, "replies_to")],
    )
    report = _run(tmp_path, tree)
    assert any(
        "the inverse entry here must use relationship_type" in m and "'has_reply'" in m for m in _errors(report)
    ), _errors(report)


def test_missing_target_candidate_is_error(tmp_path: Path):
    tree = base_tree()
    tree[f"research/screening/{SCREENING_A}.yaml"] = _screening_record(
        SCREENING_A, candidate_manifest_id=CANDIDATE_MANIFEST_ID, candidate_id=CAND_A, doi="10.1000/shared",
        related_records=[_relationship(
            CANDIDATE_MANIFEST_ID, "research-candidate-80000000-0000-4000-8000-000000000099", "replies_to",
        )],
    )
    report = _run(tmp_path, tree)
    assert any("references missing candidate" in m for m in _errors(report)), _errors(report)


def test_cross_protocol_relationship_is_error(tmp_path: Path):
    tree = base_tree()
    tree[f"research/protocols/{OTHER_PROTOCOL_ID}.yaml"] = _protocol(OTHER_PROTOCOL_ID)
    tree[f"research/candidates/{OTHER_CANDIDATE_MANIFEST_ID}.yaml"] = _candidate_manifest(
        OTHER_CANDIDATE_MANIFEST_ID, [_candidate(CAND_C, "900")], protocol_id=OTHER_PROTOCOL_ID,
    )
    tree[f"research/screening/{SCREENING_A}.yaml"] = _screening_record(
        SCREENING_A, candidate_manifest_id=CANDIDATE_MANIFEST_ID, candidate_id=CAND_A, doi="10.1000/shared",
        related_records=[_relationship(OTHER_CANDIDATE_MANIFEST_ID, CAND_C, "replies_to")],
    )
    report = _run(tmp_path, tree)
    assert any("belongs to a different protocol" in m for m in _errors(report)), _errors(report)


def test_self_reference_is_error(tmp_path: Path):
    tree = base_tree()
    tree[f"research/screening/{SCREENING_A}.yaml"] = _screening_record(
        SCREENING_A, candidate_manifest_id=CANDIDATE_MANIFEST_ID, candidate_id=CAND_A, doi="10.1000/shared",
        related_records=[_relationship(CANDIDATE_MANIFEST_ID, CAND_A, "other_related_to")],
    )
    report = _run(tmp_path, tree)
    assert any("self-reference" in m for m in _errors(report)), _errors(report)


def test_system_actor_as_identified_by_is_error(tmp_path: Path):
    tree = base_tree()
    tree[f"research/screening/{SCREENING_A}.yaml"] = _screening_record(
        SCREENING_A, candidate_manifest_id=CANDIDATE_MANIFEST_ID, candidate_id=CAND_A, doi="10.1000/shared",
        related_records=[_relationship(
            CANDIDATE_MANIFEST_ID, CAND_B, "replies_to", identified_by=SYSTEM_SCREENING_INITIALIZER_ACTOR,
        )],
    )
    tree[f"research/screening/{SCREENING_B}.yaml"] = _screening_record(
        SCREENING_B, candidate_manifest_id=CANDIDATE_MANIFEST_ID, candidate_id=CAND_B, doi="10.1000/shared",
        related_records=[_relationship(CANDIDATE_MANIFEST_ID, CAND_A, "has_reply")],
    )
    report = _run(tmp_path, tree)
    assert any(
        "must never identify a related_records relationship" in m for m in _errors(report)
    ), _errors(report)


def test_missing_relationship_metadata_is_schema_error(tmp_path: Path):
    tree = base_tree()
    record = _screening_record(
        SCREENING_A, candidate_manifest_id=CANDIDATE_MANIFEST_ID, candidate_id=CAND_A, doi="10.1000/shared",
        related_records=[_relationship(CANDIDATE_MANIFEST_ID, CAND_B, "replies_to")],
    )
    del record["related_records"][0]["relationship_metadata"]
    tree[f"research/screening/{SCREENING_A}.yaml"] = record
    report = _run(tmp_path, tree)
    assert report.error_count > 0
    assert any("required property" in m or "relationship_metadata" in m for m in _errors(report)), _errors(report)


def test_multiple_evidence_source_values_are_valid(tmp_path: Path):
    tree = base_tree()
    tree[f"research/screening/{SCREENING_A}.yaml"] = _screening_record(
        SCREENING_A, candidate_manifest_id=CANDIDATE_MANIFEST_ID, candidate_id=CAND_A, doi="10.1000/shared",
        related_records=[_relationship(
            CANDIDATE_MANIFEST_ID, CAND_B, "replies_to", evidence=["doi", "title_similarity", "author_list"],
        )],
    )
    tree[f"research/screening/{SCREENING_B}.yaml"] = _screening_record(
        SCREENING_B, candidate_manifest_id=CANDIDATE_MANIFEST_ID, candidate_id=CAND_B, doi="10.1000/shared",
        related_records=[_relationship(CANDIDATE_MANIFEST_ID, CAND_A, "has_reply")],
    )
    report = _run(tmp_path, tree)
    assert report.error_count == 0, _errors(report)


# ---------------------------------------------------------------------------
# Collision-group connectivity (check_deduplication, ADR-0058 Abschnitt 2.5)
# ---------------------------------------------------------------------------


def test_fully_resolved_two_group_via_duplicate_of(tmp_path: Path):
    tree = base_tree()
    tree[f"research/screening/{SCREENING_A}.yaml"] = _screening_record(
        SCREENING_A, candidate_manifest_id=CANDIDATE_MANIFEST_ID, candidate_id=CAND_A, doi="10.1000/shared",
        decision="duplicate", decision_stage="deduplication", duplicate_of=SCREENING_B,
    )
    tree[f"research/screening/{SCREENING_B}.yaml"] = _screening_record(
        SCREENING_B, candidate_manifest_id=CANDIDATE_MANIFEST_ID, candidate_id=CAND_B, doi="10.1000/shared",
        decision="include", decision_stage="deduplication",
    )
    report = _run(tmp_path, tree)
    assert not any("candidate_identifiers.doi" in i.path for i in report.issues), report.issues


def test_fully_resolved_three_group_transitively_via_related_records(tmp_path: Path):
    """925<->926 per duplicate_of, 926<->927 per replies_to/has_reply -- transitively one component,
    matching the real 3-PMID DOI collision this ADR was written for (see Decision Log ADR-0057)."""
    tree = base_tree()
    tree[f"research/screening/{SCREENING_A}.yaml"] = _screening_record(
        SCREENING_A, candidate_manifest_id=CANDIDATE_MANIFEST_ID, candidate_id=CAND_A, doi="10.1000/shared",
        decision="duplicate", decision_stage="deduplication", duplicate_of=SCREENING_B,
    )
    tree[f"research/screening/{SCREENING_B}.yaml"] = _screening_record(
        SCREENING_B, candidate_manifest_id=CANDIDATE_MANIFEST_ID, candidate_id=CAND_B, doi="10.1000/shared",
        decision="include", decision_stage="deduplication",
        related_records=[_relationship(CANDIDATE_MANIFEST_ID, CAND_C, "has_reply")],
    )
    tree[f"research/screening/{SCREENING_C}.yaml"] = _screening_record(
        SCREENING_C, candidate_manifest_id=CANDIDATE_MANIFEST_ID, candidate_id=CAND_C, doi="10.1000/shared",
        decision="include", decision_stage="deduplication",
        related_records=[_relationship(CANDIDATE_MANIFEST_ID, CAND_B, "replies_to")],
    )
    report = _run(tmp_path, tree)
    assert not any("candidate_identifiers.doi" in i.path for i in report.issues), report.issues


def test_fully_resolved_two_group_via_related_records_only(tmp_path: Path):
    """Ein vollstaendiges inverses Beziehungspaar (ohne jedes duplicate_of) verbindet die
    Kollisionsgruppe -- CSO-Review Runde 3, Punkt 3, erster Fall."""
    tree = base_tree()
    tree[f"research/screening/{SCREENING_A}.yaml"] = _screening_record(
        SCREENING_A, candidate_manifest_id=CANDIDATE_MANIFEST_ID, candidate_id=CAND_A, doi="10.1000/shared",
        decision="include", decision_stage="deduplication",
        related_records=[_relationship(CANDIDATE_MANIFEST_ID, CAND_B, "replies_to")],
    )
    tree[f"research/screening/{SCREENING_B}.yaml"] = _screening_record(
        SCREENING_B, candidate_manifest_id=CANDIDATE_MANIFEST_ID, candidate_id=CAND_B, doi="10.1000/shared",
        decision="include", decision_stage="deduplication",
        related_records=[_relationship(CANDIDATE_MANIFEST_ID, CAND_A, "has_reply")],
    )
    report = _run(tmp_path, tree)
    assert report.error_count == 0, _errors(report)
    assert not any("candidate_identifiers.doi" in i.path for i in report.issues), report.issues


def test_one_sided_relationship_does_not_resolve_collision_group(tmp_path: Path):
    """Eine nur einseitig dokumentierte Beziehung darf die Kollisionsgruppe NICHT verbinden -- der
    urspruengliche Blocker, den CSO-Review Runde 3 identifiziert hat."""
    tree = base_tree()
    tree[f"research/screening/{SCREENING_A}.yaml"] = _screening_record(
        SCREENING_A, candidate_manifest_id=CANDIDATE_MANIFEST_ID, candidate_id=CAND_A, doi="10.1000/shared",
        decision="include", decision_stage="deduplication",
        related_records=[_relationship(CANDIDATE_MANIFEST_ID, CAND_B, "replies_to")],
    )
    tree[f"research/screening/{SCREENING_B}.yaml"] = _screening_record(
        SCREENING_B, candidate_manifest_id=CANDIDATE_MANIFEST_ID, candidate_id=CAND_B, doi="10.1000/shared",
        decision="include", decision_stage="deduplication",
    )
    report = _run(tmp_path, tree)
    # Referenzielle Pruefung meldet die fehlende Gegenrichtung als Fehler (siehe
    # test_missing_inverse_is_error_when_target_record_exists) UND die Kollisionsgruppe bleibt
    # zusaetzlich als nicht verbunden gemeldet -- die einseitige Kante loest sie nicht auf.
    assert any(
        "not fully connected via duplicate_of/related_records" in m and "10.1000/shared" in m
        for m in _errors(report)
    ), _errors(report)


def test_wrong_inverse_type_does_not_resolve_collision_group(tmp_path: Path):
    tree = base_tree()
    tree[f"research/screening/{SCREENING_A}.yaml"] = _screening_record(
        SCREENING_A, candidate_manifest_id=CANDIDATE_MANIFEST_ID, candidate_id=CAND_A, doi="10.1000/shared",
        decision="include", decision_stage="deduplication",
        related_records=[_relationship(CANDIDATE_MANIFEST_ID, CAND_B, "replies_to")],
    )
    tree[f"research/screening/{SCREENING_B}.yaml"] = _screening_record(
        SCREENING_B, candidate_manifest_id=CANDIDATE_MANIFEST_ID, candidate_id=CAND_B, doi="10.1000/shared",
        decision="include", decision_stage="deduplication",
        related_records=[_relationship(CANDIDATE_MANIFEST_ID, CAND_A, "replies_to")],
    )
    report = _run(tmp_path, tree)
    errors = _errors(report)
    assert any("the inverse entry here must use relationship_type" in m for m in errors), errors
    assert any(
        "not fully connected via duplicate_of/related_records" in m and "10.1000/shared" in m for m in errors
    ), errors


def test_target_without_screening_record_does_not_resolve_collision_group(tmp_path: Path):
    """Eine related_records-Kante zu einem Kandidaten ohne eigenen Screening Record kann die
    Kollisionsgruppe strukturell nicht verbinden (es gibt keinen Zielknoten in der Gruppe) --
    bleibt bei den vorhandenen Mitgliedern (A, B) unresolved, ohne Fehler durch die
    Ziel-ohne-Screening-Record-Kante selbst (nur eine Warnung dafuer, siehe oben)."""
    tree = base_tree()
    tree[f"research/screening/{SCREENING_A}.yaml"] = _screening_record(
        SCREENING_A, candidate_manifest_id=CANDIDATE_MANIFEST_ID, candidate_id=CAND_A, doi="10.1000/shared",
        decision="include", decision_stage="deduplication",
        related_records=[_relationship(CANDIDATE_MANIFEST_ID, CAND_C, "other_related_to")],
    )
    tree[f"research/screening/{SCREENING_B}.yaml"] = _screening_record(
        SCREENING_B, candidate_manifest_id=CANDIDATE_MANIFEST_ID, candidate_id=CAND_B, doi="10.1000/shared",
        decision="include", decision_stage="deduplication",
    )
    report = _run(tmp_path, tree)
    assert any(
        "not fully connected via duplicate_of/related_records" in m and "10.1000/shared" in m
        for m in _errors(report)
    ), _errors(report)
    assert any("does not have a screening record yet" in m for m in _warnings(report)), _warnings(report)


def test_three_group_with_one_full_and_one_one_sided_pair_stays_unresolved(tmp_path: Path):
    tree = base_tree()
    tree[f"research/screening/{SCREENING_A}.yaml"] = _screening_record(
        SCREENING_A, candidate_manifest_id=CANDIDATE_MANIFEST_ID, candidate_id=CAND_A, doi="10.1000/shared",
        decision="duplicate", decision_stage="deduplication", duplicate_of=SCREENING_B,
    )
    tree[f"research/screening/{SCREENING_B}.yaml"] = _screening_record(
        SCREENING_B, candidate_manifest_id=CANDIDATE_MANIFEST_ID, candidate_id=CAND_B, doi="10.1000/shared",
        decision="include", decision_stage="deduplication",
    )
    # C -> B one-sided (B does not reference C back) -- must not connect C into the component.
    tree[f"research/screening/{SCREENING_C}.yaml"] = _screening_record(
        SCREENING_C, candidate_manifest_id=CANDIDATE_MANIFEST_ID, candidate_id=CAND_C, doi="10.1000/shared",
        decision="include", decision_stage="deduplication",
        related_records=[_relationship(CANDIDATE_MANIFEST_ID, CAND_B, "replies_to")],
    )
    report = _run(tmp_path, tree)
    assert any(
        "not fully connected via duplicate_of/related_records" in m and "10.1000/shared" in m
        for m in _errors(report)
    ), _errors(report)


def test_three_group_with_two_full_related_records_pairs_is_resolved(tmp_path: Path):
    """Zwei vollstaendige inverse Beziehungspaare (A<->B, B<->C), ohne jedes duplicate_of --
    CSO-Review Runde 3, Punkt 3, letzter Fall."""
    tree = base_tree()
    tree[f"research/screening/{SCREENING_A}.yaml"] = _screening_record(
        SCREENING_A, candidate_manifest_id=CANDIDATE_MANIFEST_ID, candidate_id=CAND_A, doi="10.1000/shared",
        decision="include", decision_stage="deduplication",
        related_records=[_relationship(CANDIDATE_MANIFEST_ID, CAND_B, "replies_to")],
    )
    tree[f"research/screening/{SCREENING_B}.yaml"] = _screening_record(
        SCREENING_B, candidate_manifest_id=CANDIDATE_MANIFEST_ID, candidate_id=CAND_B, doi="10.1000/shared",
        decision="include", decision_stage="deduplication",
        related_records=[
            _relationship(CANDIDATE_MANIFEST_ID, CAND_A, "has_reply"),
            _relationship(CANDIDATE_MANIFEST_ID, CAND_C, "has_reply"),
        ],
    )
    tree[f"research/screening/{SCREENING_C}.yaml"] = _screening_record(
        SCREENING_C, candidate_manifest_id=CANDIDATE_MANIFEST_ID, candidate_id=CAND_C, doi="10.1000/shared",
        decision="include", decision_stage="deduplication",
        related_records=[_relationship(CANDIDATE_MANIFEST_ID, CAND_B, "replies_to")],
    )
    report = _run(tmp_path, tree)
    assert report.error_count == 0, _errors(report)
    assert not any("candidate_identifiers.doi" in i.path for i in report.issues), report.issues


def test_partially_classified_three_group_is_error_once_all_human_reviewed(tmp_path: Path):
    tree = base_tree()
    tree[f"research/screening/{SCREENING_A}.yaml"] = _screening_record(
        SCREENING_A, candidate_manifest_id=CANDIDATE_MANIFEST_ID, candidate_id=CAND_A, doi="10.1000/shared",
        decision="duplicate", decision_stage="deduplication", duplicate_of=SCREENING_B,
    )
    tree[f"research/screening/{SCREENING_B}.yaml"] = _screening_record(
        SCREENING_B, candidate_manifest_id=CANDIDATE_MANIFEST_ID, candidate_id=CAND_B, doi="10.1000/shared",
        decision="include", decision_stage="deduplication",
    )
    tree[f"research/screening/{SCREENING_C}.yaml"] = _screening_record(
        SCREENING_C, candidate_manifest_id=CANDIDATE_MANIFEST_ID, candidate_id=CAND_C, doi="10.1000/shared",
        decision="include", decision_stage="deduplication",
    )
    report = _run(tmp_path, tree)
    errors = _errors(report)
    assert any(
        "not fully connected via duplicate_of/related_records" in m and "10.1000/shared" in m for m in errors
    ), errors


def test_partially_classified_three_group_is_warning_while_system_initialized(tmp_path: Path):
    tree = base_tree()
    tree[f"research/screening/{SCREENING_A}.yaml"] = _screening_record(
        SCREENING_A, candidate_manifest_id=CANDIDATE_MANIFEST_ID, candidate_id=CAND_A, doi="10.1000/shared",
        decision="duplicate", decision_stage="deduplication", duplicate_of=SCREENING_B,
    )
    tree[f"research/screening/{SCREENING_B}.yaml"] = _screening_record(
        SCREENING_B, candidate_manifest_id=CANDIDATE_MANIFEST_ID, candidate_id=CAND_B, doi="10.1000/shared",
        decision="include", decision_stage="deduplication",
    )
    tree[f"research/screening/{SCREENING_C}.yaml"] = _screening_record(
        SCREENING_C, candidate_manifest_id=CANDIDATE_MANIFEST_ID, candidate_id=CAND_C, doi="10.1000/shared",
        decision="pending", decision_stage="deduplication", decided_by=SYSTEM_SCREENING_INITIALIZER_ACTOR,
        candidate_title="A Test Title",
    )
    tree[f"research/reviewers/{SYSTEM_SCREENING_INITIALIZER_ACTOR}.yaml"] = {
        "schema_version": "1.0.0", "id": SYSTEM_SCREENING_INITIALIZER_ACTOR, "actor_type": "automation",
        "display_name": None, "description": "Test fixture actor.", "active": True,
        "created_at": "2026-01-01", "updated_at": "2026-01-01",
    }
    report = _run(tmp_path, tree)
    assert report.error_count == 0, _errors(report)
    assert any(
        "not fully connected via duplicate_of/related_records" in m and "10.1000/shared" in m
        for m in _warnings(report)
    ), _warnings(report)


# ---------------------------------------------------------------------------
# derive_workflow_state()
# ---------------------------------------------------------------------------


def test_workflow_state_system_initialized():
    data = _screening_record(
        SCREENING_A, decision="pending", decision_stage="deduplication",
        decided_by=SYSTEM_SCREENING_INITIALIZER_ACTOR, full_text_status="not_yet_obtained",
    )
    assert derive_workflow_state(data) == WORKFLOW_STATE_SYSTEM_INITIALIZED


def test_workflow_state_under_human_review():
    data = _screening_record(SCREENING_A, decision="include", decision_stage="title_abstract", decided_by="reviewer-1")
    assert derive_workflow_state(data) == WORKFLOW_STATE_UNDER_HUMAN_REVIEW


def test_workflow_state_finalized():
    data = _screening_record(
        SCREENING_A, decision="include", decision_stage="final", decided_by="reviewer-1",
        full_text_status="obtained",
    )
    assert derive_workflow_state(data) == WORKFLOW_STATE_FINALIZED


def test_workflow_state_not_derived_from_screened_by_alone():
    """Zwei Eintraege, beide vom Systemakteur verantwortet: laut Spezifikation (len(history) == 1)
    NICHT mehr system_initialized, obwohl der (hier bewusst inkonsistent gesetzte) Top-Level
    screened_by weiterhin den Systemakteur nennt -- beweist, dass die Ableitung tatsaechlich
    decision_history auswertet, nicht (mehr) den screened_by-String."""
    data = _screening_record(
        SCREENING_A, decision="pending", decision_stage="deduplication",
        decided_by=SYSTEM_SCREENING_INITIALIZER_ACTOR, full_text_status="not_yet_obtained",
    )
    data["decision_history"].append(dict(data["decision_history"][0], sequence=2))
    assert derive_workflow_state(data) == WORKFLOW_STATE_UNDER_HUMAN_REVIEW


# ---------------------------------------------------------------------------
# RELATIONSHIP_TYPE_INVERSE <-> research/vocabularies/screening_relationship_types.yaml
# ---------------------------------------------------------------------------


def test_relationship_type_inverse_matches_vocabulary():
    from _researchlib import RESEARCH_VOCAB_DIR

    with (RESEARCH_VOCAB_DIR / "screening_relationship_types.yaml").open("r", encoding="utf-8") as handle:
        vocab = yaml.safe_load(handle)
    vocab_inverse = {entry["value"]: entry["inverse"] for entry in vocab["values"]}
    assert vocab_inverse == RELATIONSHIP_TYPE_INVERSE


def test_relationship_type_inverse_is_involutive():
    for value, inverse in RELATIONSHIP_TYPE_INVERSE.items():
        assert RELATIONSHIP_TYPE_INVERSE[inverse] == value, f"{value} -> {inverse} is not involutive"


# ---------------------------------------------------------------------------
# derive_source_type_from_pubmed_publication_types()
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "publication_types, expected",
    [
        (["Retraction of Publication"], "retraction_notice"),
        (["Published Erratum"], "corrigendum_or_erratum"),
        (["Expression of Concern"], "expression_of_concern_notice"),
        (["Comment"], "letter_or_comment"),
        (["Letter"], "letter_or_comment"),
        (["Practice Guideline"], "practice_guideline"),
        (["Meta-Analysis"], "meta_analysis"),
        (["Meta-Analysis", "Systematic Review"], "meta_analysis"),
        (["Systematic Review"], "systematic_review"),
        (["Editorial"], "editorial"),
        (["Case Reports"], "case_report"),
        (["Review"], "narrative_review"),
        (["Review", "Systematic Review"], "systematic_review"),
        (["Journal Article"], None),
        ([], None),
        (None, None),
    ],
)
def test_pubmed_source_type_derivation(publication_types, expected):
    assert derive_source_type_from_pubmed_publication_types(publication_types) == expected


def test_reply_or_response_is_never_automatically_derived():
    known_pubmed_tags = [
        "Retraction of Publication", "Published Erratum", "Expression of Concern", "Comment", "Letter",
        "Practice Guideline", "Meta-Analysis", "Systematic Review", "Editorial", "Case Reports", "Review",
        "Journal Article", "Clinical Trial",
    ]
    for tag in known_pubmed_tags:
        assert derive_source_type_from_pubmed_publication_types([tag]) != "reply_or_response"
    assert derive_source_type_from_pubmed_publication_types(known_pubmed_tags) != "reply_or_response"


# ---------------------------------------------------------------------------
# tools/refresh_candidate_source_types.py
# ---------------------------------------------------------------------------


def test_refresh_tool_dry_run_writes_nothing(tmp_path: Path, monkeypatch):
    tree = base_tree()
    manifest = tree[f"research/candidates/{CANDIDATE_MANIFEST_ID}.yaml"]
    manifest["candidates"][0] = _candidate(CAND_A, "100", publication_types=["Meta-Analysis"])
    tree[f"research/screening/{SCREENING_A}.yaml"] = _screening_record(
        SCREENING_A, candidate_manifest_id=CANDIDATE_MANIFEST_ID, candidate_id=CAND_A,
        decision="pending", decision_stage="deduplication", decided_by=SYSTEM_SCREENING_INITIALIZER_ACTOR,
    )
    write_tree(tmp_path, tree)

    monkeypatch.setattr(refresh_tool, "RESEARCH_DIR", tmp_path / "research")
    before = (tmp_path / "research" / "screening" / f"{SCREENING_A}.yaml").read_text(encoding="utf-8")
    outcome = refresh_tool.refresh(PROTOCOL_ID, apply=False)
    after = (tmp_path / "research" / "screening" / f"{SCREENING_A}.yaml").read_text(encoding="utf-8")

    assert before == after
    assert len(outcome.proposed) == 1
    assert outcome.proposed[0] == (SCREENING_A, "peer_reviewed_publication", "meta_analysis")
    assert outcome.applied == []


def test_refresh_tool_apply_writes_only_eligible_records(tmp_path: Path, monkeypatch):
    tree = base_tree()
    manifest = tree[f"research/candidates/{CANDIDATE_MANIFEST_ID}.yaml"]
    manifest["candidates"][0] = _candidate(CAND_A, "100", publication_types=["Meta-Analysis"])
    manifest["candidates"][1] = _candidate(CAND_B, "101", publication_types=["Meta-Analysis"])
    tree[f"research/screening/{SCREENING_A}.yaml"] = _screening_record(
        SCREENING_A, candidate_manifest_id=CANDIDATE_MANIFEST_ID, candidate_id=CAND_A,
        decision="pending", decision_stage="deduplication", decided_by=SYSTEM_SCREENING_INITIALIZER_ACTOR,
    )
    # already human-reviewed -- must never be touched, even though the derivation would apply.
    tree[f"research/screening/{SCREENING_B}.yaml"] = _screening_record(
        SCREENING_B, candidate_manifest_id=CANDIDATE_MANIFEST_ID, candidate_id=CAND_B,
        decision="include", decision_stage="title_abstract", decided_by="reviewer-1",
    )
    write_tree(tmp_path, tree)

    monkeypatch.setattr(refresh_tool, "RESEARCH_DIR", tmp_path / "research")
    outcome = refresh_tool.refresh(PROTOCOL_ID, apply=True)

    assert outcome.applied == [SCREENING_A]
    assert outcome.skipped_human_reviewed == [SCREENING_B]

    updated_a = yaml.safe_load((tmp_path / "research" / "screening" / f"{SCREENING_A}.yaml").read_text(encoding="utf-8"))
    assert updated_a["candidate_source_type"] == "meta_analysis"
    assert updated_a["updated_at"] != "2026-01-01"
    # Nothing else changed -- in particular no decision_history mutation (candidate_source_type is
    # not part of decision_history[], see research_screening_record.schema.json).
    assert updated_a["decision_history"] == tree[f"research/screening/{SCREENING_A}.yaml"]["decision_history"]

    unchanged_b = (tmp_path / "research" / "screening" / f"{SCREENING_B}.yaml").read_text(encoding="utf-8")
    original_b = yaml.safe_dump(
        tree[f"research/screening/{SCREENING_B}.yaml"], sort_keys=False, allow_unicode=True
    )
    assert unchanged_b == original_b


def test_refresh_tool_reports_conflict_without_applying(tmp_path: Path, monkeypatch):
    tree = base_tree()
    manifest = tree[f"research/candidates/{CANDIDATE_MANIFEST_ID}.yaml"]
    manifest["candidates"][0] = _candidate(CAND_A, "100", publication_types=["Meta-Analysis"])
    record = _screening_record(
        SCREENING_A, candidate_manifest_id=CANDIDATE_MANIFEST_ID, candidate_id=CAND_A,
        decision="pending", decision_stage="deduplication", decided_by=SYSTEM_SCREENING_INITIALIZER_ACTOR,
    )
    # Someone/something already set a non-default source_type -- must be treated as a conflict, not
    # silently overwritten, even though workflow_state is still system_initialized.
    record["candidate_source_type"] = "editorial"
    tree[f"research/screening/{SCREENING_A}.yaml"] = record
    write_tree(tmp_path, tree)

    monkeypatch.setattr(refresh_tool, "RESEARCH_DIR", tmp_path / "research")
    before = (tmp_path / "research" / "screening" / f"{SCREENING_A}.yaml").read_text(encoding="utf-8")
    outcome = refresh_tool.refresh(PROTOCOL_ID, apply=True)
    after = (tmp_path / "research" / "screening" / f"{SCREENING_A}.yaml").read_text(encoding="utf-8")

    assert before == after
    assert outcome.conflicts == [(SCREENING_A, "editorial", "meta_analysis")]
    assert outcome.applied == []

"""Tests fuer research_candidate_manifest (siehe ADR-0056): tools/validate_research.py::
check_candidate_manifests und check_screening_candidate_references.

Anders als tests/test_validate_research.py (statische Fixture-Baeume unter tests/fixtures/research/)
baut dieses Modul die Recherche-Datensaetze programmatisch in ein tmp_path-Verzeichnis. Die grosse
Zahl an Positiv-/Negativfaellen aus dem Phase-4B-1B-0-Arbeitsauftrag (Abschnitt 12) teilt sich fast
immer denselben Protokoll-/Suchlauf-/Manifest-Unterbau und unterscheidet sich nur in einem einzigen
Feld des Candidate Manifest (oder Screening Record) -- ein programmatischer Builder vermeidet dafuer
Dutzende nahezu identischer, schwer zu pflegender YAML-Dateien.
"""

from __future__ import annotations

import shutil
import uuid as uuid_lib
from pathlib import Path

import pytest
import yaml
from validate_research import run_validation

# tools/_datalib.py::relative() computes paths relative to the real repo root (REPO_ROOT) for
# error-message formatting -- it raises if a file lives outside the repo. Pytest's built-in
# tmp_path fixture creates directories under the OS temp dir, which is NOT a repo subpath. This
# module-local override shadows the built-in `tmp_path` fixture with one rooted inside the repo
# (cleaned up after each test) so run_validation() can format relative paths normally.
_SCRATCH_ROOT = Path(__file__).resolve().parent / "fixtures" / "_scratch_candidate_manifests"


@pytest.fixture
def tmp_path():
    path = _SCRATCH_ROOT / uuid_lib.uuid4().hex
    path.mkdir(parents=True, exist_ok=True)
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)


PROTOCOL_ID = "research-protocol-test-substance-v1"
RETATRUTIDE_PROTOCOL_ID = "research-protocol-retatrutide-v1"

SEARCH_RUN_A = "search-run-40000000-0000-4000-8000-000000000001"
SEARCH_RUN_B = "search-run-40000000-0000-4000-8000-000000000002"
CTGOV_SEARCH_RUN = "search-run-40000000-0000-4000-8000-000000000003"

MANIFEST_A = "search-result-manifest-90000000-0000-4000-8000-000000000001"
MANIFEST_B = "search-result-manifest-90000000-0000-4000-8000-000000000002"
CTGOV_MANIFEST = "search-result-manifest-90000000-0000-4000-8000-000000000003"

CANDIDATE_MANIFEST_ID = "candidate-manifest-40000000-0000-4000-8000-000000000001"
CTGOV_CANDIDATE_MANIFEST_ID = "candidate-manifest-40000000-0000-4000-8000-000000000002"

CANDIDATE_100 = "research-candidate-40000000-0000-4000-8000-000000000001"  # only in run A
CANDIDATE_200 = "research-candidate-40000000-0000-4000-8000-000000000002"  # in both runs (dual origin)
CANDIDATE_300 = "research-candidate-40000000-0000-4000-8000-000000000003"  # only in run B

CTGOV_CANDIDATE = "research-candidate-40000000-0000-4000-8000-000000000004"


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
        "planned_information_sources": [
            {"database": "pubmed", "role": "primary", "notes": None},
            {"database": "clinicaltrials_gov", "role": "primary", "notes": None},
        ],
        "planned_search_concepts": ["test substance"],
        "eligibility": {"inclusion_criteria": ["Testkriterium"], "exclusion_criteria": ["Testausschlusskriterium"]},
        "deduplication_policy": {"description": {"de": "Test."}, "identifier_priority": ["doi"], "manual_review_required": True},
        "screening_policy": {
            "description": {"de": "Test."}, "stages": ["deduplication", "title_abstract", "full_text"],
            "dual_reviewer_stages": ["full_text"],
        },
        "extraction_policy": {"description": {"de": "Test."}, "verification_required": True, "fields_to_extract": ["identity"]},
        "evidence_appraisal_policy": {"description": {"de": "Test."}},
        "claim_promotion_policy": {"description": {"de": "Test."}, "requires_second_review": True},
        "amendment_policy": {"description": {"de": "Test."}},
        "created_at": "2026-01-01",
        "updated_at": "2026-01-01",
        "review": {"last_reviewed_at": "2026-01-01", "reviewers": ["reviewer-1"], "approval_decision": "Freigegeben fuer Testzwecke."},
    }


def _search_run(run_id: str, database: str, query: str, manifest_id: str, result_count: int, protocol_id: str = PROTOCOL_ID) -> dict:
    if database == "pubmed":
        interface = "NCBI E-utilities ESearch (test)"
        profile = {"id": "ncbi_eutils_esearch_v1", "rationale": None}
        request_parameters = {"db": "pubmed", "retmode": "json", "retmax": 1000, "retstart": 0}
        pagination = None
    else:
        interface = "ClinicalTrials.gov API v2 (test)"
        profile = {"id": "clinicaltrials_gov_api_v2_v1", "rationale": None}
        request_parameters = {
            "query_parameter": "query.term", "countTotal": True, "pageSize": 100, "format": "json", "fields": "NCTId",
        }
        pagination = {"pages_retrieved": 1, "completion_confirmed": True}
    data = {
        "schema_version": "1.0.0",
        "id": run_id,
        "protocol_id": protocol_id,
        "database": database,
        "interface": interface,
        "interface_profile": profile,
        "executed_at": "2026-01-01T10:00:00Z",
        "executed_by": "reviewer-1",
        "exact_query": query,
        "filters": {},
        "request_parameters": request_parameters,
        "result_capture": {"status": "complete", "manifest_id": manifest_id, "rationale": None},
        "date_range": {"from": None, "to": None},
        "result_count": result_count,
        "export_reference": "research/raw/test/x.json",
        "notes": None,
        "status": "executed",
        "created_at": "2026-01-01",
        "updated_at": "2026-01-01",
        "review": {"last_reviewed_at": None, "reviewers": []},
    }
    if pagination is not None:
        data["pagination"] = pagination
    return data


def _manifest(manifest_id: str, search_run_id: str, identifier_type: str, identifiers: list[str]) -> dict:
    from _researchlib import compute_manifest_sha256

    return {
        "schema_version": "1.0.0",
        "id": manifest_id,
        "search_run_id": search_run_id,
        "identifier_type": identifier_type,
        "identifiers": identifiers,
        "count": len(identifiers),
        "sha256": compute_manifest_sha256(identifiers),
        "source_export_reference": "research/raw/test/x.json",
        "created_at": "2026-01-01",
        "updated_at": "2026-01-01",
        "notes": None,
    }


def _pubmed_metadata(**overrides) -> dict:
    metadata = {
        "title": "A Test Title", "publication_year": 2024, "journal": "Test Journal",
        "publication_types": ["Journal Article"], "doi": "10.1000/test", "pmcid": None,
        "authors": ["Doe J"], "abstract_available": True, "language": "en",
    }
    metadata.update(overrides)
    return metadata


def _ctgov_metadata(**overrides) -> dict:
    metadata = {
        "brief_title": "A Test Trial", "official_title": None, "overall_status": "COMPLETED", "phases": ["PHASE1"],
        "sponsor": "Test Sponsor", "interventions": ["Test Drug"], "conditions": ["Test Condition"],
        "study_type": "INTERVENTIONAL", "start_date": "2020-01-01", "primary_completion_date": "2020-06-01",
        "completion_date": "2020-06-01", "has_results": False, "last_update_posted": "2020-07-01",
    }
    metadata.update(overrides)
    return metadata


def _provenance(**overrides) -> dict:
    provenance = {
        "source_interface": "NCBI E-utilities ESummary", "retrieved_at": "2026-01-02T00:00:00Z",
        "request_reference": "NCBI ESummary db=pubmed id=100", "response_locator": None,
    }
    provenance.update(overrides)
    return provenance


def _candidate(candidate_id, namespace, value, discovered, metadata_status="not_fetched", metadata=None,
                metadata_fetch_note=None, metadata_provenance=None) -> dict:
    return {
        "candidate_id": candidate_id,
        "primary_identifier": {"namespace": namespace, "value": value},
        "discovered_in_search_run_ids": sorted(discovered),
        "metadata": metadata,
        "metadata_status": metadata_status,
        "metadata_fetch_note": metadata_fetch_note,
        "metadata_provenance": metadata_provenance,
    }


def base_candidate_manifest() -> dict:
    candidates = [
        _candidate(CANDIDATE_100, "pmid", "100", [SEARCH_RUN_A], "not_fetched"),
        _candidate(
            CANDIDATE_200, "pmid", "200", [SEARCH_RUN_A, SEARCH_RUN_B], "fetched",
            metadata=_pubmed_metadata(), metadata_provenance=_provenance(),
        ),
        _candidate(
            CANDIDATE_300, "pmid", "300", [SEARCH_RUN_B], "not_found",
            metadata_fetch_note="PMID not present in ESummary response (not found)",
            metadata_provenance=_provenance(request_reference="NCBI ESummary db=pubmed id=300"),
        ),
    ]
    return {
        "schema_version": "1.0.0",
        "id": CANDIDATE_MANIFEST_ID,
        "protocol_id": PROTOCOL_ID,
        "database": "pubmed",
        "identifier_namespace": "pmid",
        "source_search_run_ids": sorted([SEARCH_RUN_A, SEARCH_RUN_B]),
        "source_result_manifest_ids": sorted([MANIFEST_A, MANIFEST_B]),
        "candidate_count": len(candidates),
        "candidates": candidates,
        "created_at": "2026-01-01",
        "updated_at": "2026-01-02",
    }


def base_ctgov_candidate_manifest() -> dict:
    candidates = [
        _candidate(
            CTGOV_CANDIDATE, "nct_id", "NCT00000001", [CTGOV_SEARCH_RUN], "fetched",
            metadata=_ctgov_metadata(),
            metadata_provenance=_provenance(source_interface="ClinicalTrials.gov API v2", request_reference="ClinicalTrials.gov API v2 studies/NCT00000001"),
        ),
    ]
    return {
        "schema_version": "1.0.0",
        "id": CTGOV_CANDIDATE_MANIFEST_ID,
        "protocol_id": PROTOCOL_ID,
        "database": "clinicaltrials_gov",
        "identifier_namespace": "nct_id",
        "source_search_run_ids": [CTGOV_SEARCH_RUN],
        "source_result_manifest_ids": [CTGOV_MANIFEST],
        "candidate_count": len(candidates),
        "candidates": candidates,
        "created_at": "2026-01-01",
        "updated_at": "2026-01-02",
    }


def write_tree(root: Path, tree: dict[str, dict | None]) -> None:
    for relative_path, data in tree.items():
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            yaml.safe_dump(data, handle, sort_keys=False, allow_unicode=True)


def base_tree(*, include_ctgov: bool = True) -> dict[str, dict]:
    tree = {
        f"research/protocols/{PROTOCOL_ID}.yaml": _protocol(),
        f"research/search_runs/{SEARCH_RUN_A}.yaml": _search_run(SEARCH_RUN_A, "pubmed", "alias A", MANIFEST_A, 2),
        f"research/search_runs/{SEARCH_RUN_B}.yaml": _search_run(SEARCH_RUN_B, "pubmed", "alias B", MANIFEST_B, 2),
        f"research/search_results/{MANIFEST_A}.yaml": _manifest(MANIFEST_A, SEARCH_RUN_A, "pmid", ["100", "200"]),
        f"research/search_results/{MANIFEST_B}.yaml": _manifest(MANIFEST_B, SEARCH_RUN_B, "pmid", ["200", "300"]),
        f"research/candidates/{CANDIDATE_MANIFEST_ID}.yaml": base_candidate_manifest(),
    }
    if include_ctgov:
        tree[f"research/search_runs/{CTGOV_SEARCH_RUN}.yaml"] = _search_run(
            CTGOV_SEARCH_RUN, "clinicaltrials_gov", "test", CTGOV_MANIFEST, 1
        )
        tree[f"research/search_results/{CTGOV_MANIFEST}.yaml"] = _manifest(
            CTGOV_MANIFEST, CTGOV_SEARCH_RUN, "nct_id", ["NCT00000001"]
        )
        tree[f"research/candidates/{CTGOV_CANDIDATE_MANIFEST_ID}.yaml"] = base_ctgov_candidate_manifest()
    return tree


def _run(tmp_path: Path, tree: dict[str, dict]):
    write_tree(tmp_path, tree)
    return run_validation(verbose=False, research_root=tmp_path / "research", data_root=tmp_path / "data")


def test_base_dataset_is_valid(tmp_path: Path):
    report = _run(tmp_path, base_tree())
    messages = "\n".join(issue.format() for issue in report.issues)
    assert report.error_count == 0, f"unexpected errors:\n{messages}"


def test_partial_metadata_status_is_valid(tmp_path: Path):
    tree = base_tree(include_ctgov=False)
    manifest = tree[f"research/candidates/{CANDIDATE_MANIFEST_ID}.yaml"]
    manifest["candidates"][0]["metadata_status"] = "partial"
    manifest["candidates"][0]["metadata"] = _pubmed_metadata(title=None, doi=None)
    manifest["candidates"][0]["metadata_provenance"] = _provenance()
    report = _run(tmp_path, tree)
    assert report.error_count == 0, "\n".join(issue.format() for issue in report.issues)


@pytest.mark.parametrize(
    "mutate, expected_substring",
    [
        pytest.param(
            lambda m: (m["candidates"].pop(2), m.__setitem__("candidate_count", 2)),
            "are missing from candidates",
            id="missing_identifier_from_manifest",
        ),
        pytest.param(
            lambda m: (
                m["candidates"].append(_candidate(
                    "research-candidate-40000000-0000-4000-8000-000000000099", "pmid", "999", [SEARCH_RUN_A],
                )),
                m.__setitem__("candidate_count", 4),
            ),
            "is not present in any of this manifest's referenced search result manifests",
            id="extra_undiscovered_identifier",
        ),
        pytest.param(
            lambda m: (
                m["candidates"].append(_candidate(
                    "research-candidate-40000000-0000-4000-8000-000000000098", "pmid", "100", [SEARCH_RUN_A],
                )),
                m.__setitem__("candidate_count", 4),
            ),
            "duplicate pmid '100' within this candidate manifest",
            id="duplicate_identifier_within_manifest",
        ),
        pytest.param(
            lambda m: m["candidates"][1].__setitem__("candidate_id", CANDIDATE_100),
            "duplicate candidate_id",
            id="duplicate_candidate_id",
        ),
        pytest.param(
            lambda m: m.__setitem__("source_search_run_ids", [SEARCH_RUN_A, "search-run-00000000-0000-4000-8000-000000000000"]),
            "references missing search run",
            id="missing_search_run",
        ),
        pytest.param(
            lambda m: m.__setitem__(
                "source_result_manifest_ids",
                [MANIFEST_A, "search-result-manifest-00000000-0000-4000-8000-000000000000"],
            ),
            "references missing search result manifest",
            id="missing_result_manifest",
        ),
        pytest.param(
            lambda m: m.__setitem__("candidate_count", 999),
            "does not match the number of candidates",
            id="candidate_count_mismatch",
        ),
        pytest.param(
            lambda m: m["candidates"][1].__setitem__("discovered_in_search_run_ids", [SEARCH_RUN_A]),
            "is missing search run(s) that actually contained this identifier",
            id="incomplete_provenance_missing_run",
        ),
        pytest.param(
            lambda m: m["candidates"][0].__setitem__("discovered_in_search_run_ids", [SEARCH_RUN_A, SEARCH_RUN_B]),
            "lists search run(s) that did not actually contain this identifier",
            id="incomplete_provenance_extra_run",
        ),
        pytest.param(
            lambda m: m["candidates"][1]["metadata"].__setitem__("title", None),
            "requires a non-empty title",
            id="fetched_missing_pubmed_title",
        ),
        pytest.param(
            lambda m: m["candidates"][1]["metadata_provenance"].__setitem__("retrieved_at", "2025-01-01T00:00:00Z"),
            "is before this manifest's created_at",
            id="retrieved_at_before_created_at",
        ),
        pytest.param(
            lambda m: m["candidates"][1]["metadata_provenance"].__setitem__("retrieved_at", "2027-01-01T00:00:00Z"),
            "is after this manifest's updated_at",
            id="retrieved_at_after_updated_at",
        ),
        pytest.param(
            lambda m: m["candidates"][1]["metadata_provenance"].__setitem__(
                "request_reference", "https://eutils.ncbi.nlm.nih.gov/x?api_key=secret"
            ),
            "must not be a full URL",
            id="request_reference_is_url",
        ),
        pytest.param(
            lambda m: m["candidates"][1]["metadata_provenance"].__setitem__("request_reference", "esummary api_key=abc123"),
            "must not contain what looks like a secret parameter",
            id="request_reference_secret_param",
        ),
        pytest.param(
            lambda m: m["candidates"][1]["metadata_provenance"].__setitem__("response_locator", "some/other/path.json"),
            "must point to a path under research/raw/",
            id="response_locator_outside_raw",
        ),
    ],
)
def test_invalid_candidate_manifest_scenario(tmp_path: Path, mutate, expected_substring):
    tree = base_tree(include_ctgov=False)
    manifest = tree[f"research/candidates/{CANDIDATE_MANIFEST_ID}.yaml"]
    mutate(manifest)
    report = _run(tmp_path, tree)
    assert report.error_count > 0, f"expected at least one error for scenario"
    messages = [issue.message for issue in report.issues if issue.level == "ERROR"]
    assert any(expected_substring in message for message in messages), (
        f"expected an error containing {expected_substring!r}, got:\n" + "\n".join(messages)
    )


@pytest.mark.parametrize(
    "mutate",
    [
        pytest.param(lambda m: m["candidates"][0].__setitem__("primary_identifier", {"namespace": "nct_id", "value": "NCT00000099"}), id="wrong_namespace_for_database"),
        pytest.param(lambda m: m.__setitem__("database", "other"), id="unsupported_database"),
        pytest.param(lambda m: m["candidates"][0].__setitem__("metadata_status", "not_found"), id="not_found_without_note"),
        pytest.param(lambda m: m["candidates"][0].__setitem__("metadata", _pubmed_metadata()), id="not_fetched_with_metadata_present"),
        pytest.param(lambda m: m["candidates"][0].update({"decision": "include"}), id="screening_field_present"),
    ],
)
def test_schema_rejects_invalid_candidate_manifest(tmp_path: Path, mutate):
    tree = base_tree(include_ctgov=False)
    manifest = tree[f"research/candidates/{CANDIDATE_MANIFEST_ID}.yaml"]
    mutate(manifest)
    report = _run(tmp_path, tree)
    assert report.error_count > 0


def test_ctgov_candidate_manifest_is_valid(tmp_path: Path):
    report = _run(tmp_path, base_tree(include_ctgov=True))
    assert report.error_count == 0, "\n".join(issue.format() for issue in report.issues)


def test_ctgov_fetched_missing_overall_status(tmp_path: Path):
    tree = base_tree(include_ctgov=True)
    manifest = tree[f"research/candidates/{CTGOV_CANDIDATE_MANIFEST_ID}.yaml"]
    manifest["candidates"][0]["metadata"]["overall_status"] = None
    report = _run(tmp_path, tree)
    messages = [issue.message for issue in report.issues if issue.level == "ERROR"]
    assert any("requires a non-empty overall_status" in message for message in messages), messages


# --- Screening record candidate reference (Migrationsstrategie, siehe ADR-0056) ---------------

SCREENING_RECORD_ID = "screening-record-50000000-0000-4000-8000-000000000001"


def _screening_record(
    protocol_id: str, candidate_manifest_id=None, candidate_id=None, pmid="200", nct_id=None,
    search_run_ids=None,
) -> dict:
    return {
        "schema_version": "1.0.0",
        "id": SCREENING_RECORD_ID,
        "protocol_id": protocol_id,
        "search_run_ids": search_run_ids if search_run_ids is not None else [SEARCH_RUN_A],
        "candidate_identifiers": {"doi": None, "pmid": pmid, "pmcid": None, "nct_id": nct_id, "isbn": None, "url": None},
        "candidate_title": "Test Candidate",
        "candidate_source_type": "peer_reviewed_publication",
        "decision": "pending",
        "decision_stage": "deduplication",
        "decision_reason": None,
        "duplicate_of": None,
        "full_text_status": "not_yet_obtained",
        "screened_by": "reviewer-1",
        "screened_at": "2026-01-03",
        "second_review": None,
        "decision_history": [{
            "sequence": 1, "stage": "deduplication", "primary_decision": "pending", "primary_decision_reason": None,
            "decision": "pending", "decision_reason": None, "duplicate_of": None, "primary_duplicate_of": None,
            "decided_by": "reviewer-1", "decided_at": "2026-01-03", "full_text_status": "not_yet_obtained",
            "second_review": None,
        }],
        "canonical_source_id": None,
        "candidate_manifest_id": candidate_manifest_id,
        "candidate_id": candidate_id,
        "created_at": "2026-01-03",
        "updated_at": "2026-01-03",
    }


def test_valid_screening_candidate_reference(tmp_path: Path):
    tree = base_tree(include_ctgov=False)
    tree[f"research/screening/{SCREENING_RECORD_ID}.yaml"] = _screening_record(
        PROTOCOL_ID, CANDIDATE_MANIFEST_ID, CANDIDATE_200, pmid="200",
        search_run_ids=[SEARCH_RUN_A, SEARCH_RUN_B],  # CANDIDATE_200 is a dual-origin candidate
    )
    report = _run(tmp_path, tree)
    assert report.error_count == 0, "\n".join(issue.format() for issue in report.issues)


def test_screening_candidate_reference_missing_candidate(tmp_path: Path):
    tree = base_tree(include_ctgov=False)
    tree[f"research/screening/{SCREENING_RECORD_ID}.yaml"] = _screening_record(
        PROTOCOL_ID, CANDIDATE_MANIFEST_ID, "research-candidate-00000000-0000-4000-8000-000000000000",
    )
    report = _run(tmp_path, tree)
    messages = [issue.message for issue in report.issues if issue.level == "ERROR"]
    assert any("references missing candidate" in message for message in messages), messages


def test_screening_candidate_reference_cross_protocol(tmp_path: Path):
    tree = base_tree(include_ctgov=False)
    tree[f"research/protocols/research-protocol-other-v1.yaml"] = _protocol("research-protocol-other-v1")
    tree[f"research/screening/{SCREENING_RECORD_ID}.yaml"] = _screening_record(
        "research-protocol-other-v1", CANDIDATE_MANIFEST_ID, CANDIDATE_200,
    )
    report = _run(tmp_path, tree)
    messages = [issue.message for issue in report.issues if issue.level == "ERROR"]
    assert any("belongs to a different protocol" in message for message in messages), messages


def test_screening_candidate_reference_identifier_conflict(tmp_path: Path):
    tree = base_tree(include_ctgov=False)
    tree[f"research/screening/{SCREENING_RECORD_ID}.yaml"] = _screening_record(
        PROTOCOL_ID, CANDIDATE_MANIFEST_ID, CANDIDATE_200, pmid="999",
    )
    report = _run(tmp_path, tree)
    messages = [issue.message for issue in report.issues if issue.level == "ERROR"]
    assert any("conflicts with the referenced candidate's primary_identifier" in message for message in messages), messages


def test_screening_record_for_protocol_with_candidate_manifest_without_reference_is_rejected(tmp_path: Path):
    """CSO-Review-Nachtrag zu ADR-0056: die Referenzpflicht ist datengetrieben -- PROTOCOL_ID hat
    im base_tree bereits ein Candidate Manifest, also ist die Referenz fuer einen neuen Screening
    Record dieses Protokolls verpflichtend, auch ohne eine hartkodierte Protokoll-Allowlist."""
    tree = base_tree(include_ctgov=False)
    tree[f"research/screening/{SCREENING_RECORD_ID}.yaml"] = _screening_record(PROTOCOL_ID)
    report = _run(tmp_path, tree)
    messages = [issue.message for issue in report.issues if issue.level == "ERROR"]
    assert any(
        "has at least one candidate manifest -- new screening records for this protocol must reference"
        in message
        for message in messages
    ), messages


OTHER_PROTOCOL_SEARCH_RUN = "search-run-40000000-0000-4000-8000-000000000005"
OTHER_PROTOCOL_MANIFEST = "search-result-manifest-90000000-0000-4000-8000-000000000005"


def test_screening_record_for_protocol_without_candidate_manifest_is_still_valid(tmp_path: Path):
    """CSO-Review-Nachtrag zu ADR-0056: ein Protokoll ohne jegliches Candidate Manifest bleibt
    migrationskompatibel -- ein Screening Record ohne candidate_manifest_id/candidate_id ist dafuer
    weiterhin gueltig."""
    tree = base_tree(include_ctgov=False)
    tree[f"research/protocols/{RETATRUTIDE_PROTOCOL_ID}.yaml"] = _protocol(RETATRUTIDE_PROTOCOL_ID)
    tree[f"research/search_runs/{OTHER_PROTOCOL_SEARCH_RUN}.yaml"] = _search_run(
        OTHER_PROTOCOL_SEARCH_RUN, "pubmed", "other protocol query", OTHER_PROTOCOL_MANIFEST, 1,
        protocol_id=RETATRUTIDE_PROTOCOL_ID,
    )
    tree[f"research/search_results/{OTHER_PROTOCOL_MANIFEST}.yaml"] = _manifest(
        OTHER_PROTOCOL_MANIFEST, OTHER_PROTOCOL_SEARCH_RUN, "pmid", ["500"],
    )
    tree[f"research/screening/{SCREENING_RECORD_ID}.yaml"] = _screening_record(
        RETATRUTIDE_PROTOCOL_ID, pmid="500", search_run_ids=[OTHER_PROTOCOL_SEARCH_RUN],
    )
    report = _run(tmp_path, tree)
    assert report.error_count == 0, "\n".join(issue.format() for issue in report.issues)


def test_screening_candidate_reference_missing_pmid_is_rejected(tmp_path: Path):
    tree = base_tree(include_ctgov=False)
    tree[f"research/screening/{SCREENING_RECORD_ID}.yaml"] = _screening_record(
        PROTOCOL_ID, CANDIDATE_MANIFEST_ID, CANDIDATE_200, pmid=None,
    )
    report = _run(tmp_path, tree)
    messages = [issue.message for issue in report.issues if issue.level == "ERROR"]
    assert any(
        "candidate_identifiers.pmid must not be null" in message or "must not be null" in message
        for message in messages
    ), messages
    assert any("$.candidate_identifiers.pmid" == issue.path for issue in report.issues if issue.level == "ERROR")


def test_valid_ctgov_screening_candidate_reference(tmp_path: Path):
    tree = base_tree(include_ctgov=True)
    tree[f"research/screening/{SCREENING_RECORD_ID}.yaml"] = _screening_record(
        PROTOCOL_ID, CTGOV_CANDIDATE_MANIFEST_ID, CTGOV_CANDIDATE, pmid=None, nct_id="NCT00000001",
        search_run_ids=[CTGOV_SEARCH_RUN],
    )
    report = _run(tmp_path, tree)
    assert report.error_count == 0, "\n".join(issue.format() for issue in report.issues)


def test_screening_candidate_reference_missing_nct_id_is_rejected(tmp_path: Path):
    tree = base_tree(include_ctgov=True)
    tree[f"research/screening/{SCREENING_RECORD_ID}.yaml"] = _screening_record(
        PROTOCOL_ID, CTGOV_CANDIDATE_MANIFEST_ID, CTGOV_CANDIDATE, pmid=None, nct_id=None,
    )
    report = _run(tmp_path, tree)
    messages = [issue.message for issue in report.issues if issue.level == "ERROR"]
    assert any("must not be null" in message for message in messages), messages
    assert any("$.candidate_identifiers.nct_id" == issue.path for issue in report.issues if issue.level == "ERROR")


def test_ctgov_screening_candidate_reference_identifier_conflict(tmp_path: Path):
    tree = base_tree(include_ctgov=True)
    tree[f"research/screening/{SCREENING_RECORD_ID}.yaml"] = _screening_record(
        PROTOCOL_ID, CTGOV_CANDIDATE_MANIFEST_ID, CTGOV_CANDIDATE, pmid=None, nct_id="NCT99999999",
    )
    report = _run(tmp_path, tree)
    messages = [issue.message for issue in report.issues if issue.level == "ERROR"]
    assert any("conflicts with the referenced candidate's primary_identifier" in message for message in messages), messages

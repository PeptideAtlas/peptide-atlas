"""Tests fuer Phase 4B-1B-1 (siehe ADR-0057): tools/initialize_screening_records.py sowie die
neuen validate_research.py-Pruefungen check_screening_system_actor_invariants,
check_screening_candidate_uniqueness, check_screening_initialization_completeness und die
Deduplizierungs-Herabstufung in check_deduplication.

Wie tests/test_validate_research_candidate_manifests.py baut dieses Modul die Recherche-
Datensaetze programmatisch in ein repo-gebundenes tmp_path-Verzeichnis (tools/_datalib.py::
relative() verlangt Pfade unter REPO_ROOT).
"""

from __future__ import annotations

import shutil
import uuid as uuid_lib
from pathlib import Path

import initialize_screening_records as isr
import pytest
import yaml
from _researchlib import SYSTEM_SCREENING_INITIALIZER_ACTOR, compute_manifest_sha256
from validate_research import run_validation

_SCRATCH_ROOT = Path(__file__).resolve().parent / "fixtures" / "_scratch_screening_initialization"


@pytest.fixture
def tmp_path():
    path = _SCRATCH_ROOT / uuid_lib.uuid4().hex
    path.mkdir(parents=True, exist_ok=True)
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)


PROTOCOL_ID = "research-protocol-test-substance-v1"

SEARCH_RUN_PUBMED = "search-run-60000000-0000-4000-8000-000000000001"
SEARCH_RUN_CTGOV = "search-run-60000000-0000-4000-8000-000000000002"
MANIFEST_PUBMED = "search-result-manifest-70000000-0000-4000-8000-000000000001"
MANIFEST_CTGOV = "search-result-manifest-70000000-0000-4000-8000-000000000002"

CANDIDATE_MANIFEST_PUBMED = "candidate-manifest-60000000-0000-4000-8000-000000000001"
CANDIDATE_MANIFEST_CTGOV = "candidate-manifest-60000000-0000-4000-8000-000000000002"

CAND_PM_1 = "research-candidate-60000000-0000-4000-8000-000000000001"
CAND_PM_2 = "research-candidate-60000000-0000-4000-8000-000000000002"
CAND_PM_3 = "research-candidate-60000000-0000-4000-8000-000000000003"
CAND_CT_1 = "research-candidate-60000000-0000-4000-8000-000000000004"
CAND_CT_2 = "research-candidate-60000000-0000-4000-8000-000000000005"


def _protocol() -> dict:
    return {
        "schema_version": "1.0.0",
        "id": PROTOCOL_ID,
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
            "description": {"de": "Test."}, "stages": ["deduplication", "title_abstract", "full_text", "final"],
            "dual_reviewer_stages": ["full_text", "final"],
        },
        "extraction_policy": {"description": {"de": "Test."}, "verification_required": True, "fields_to_extract": ["identity"]},
        "evidence_appraisal_policy": {"description": {"de": "Test."}},
        "claim_promotion_policy": {"description": {"de": "Test."}, "requires_second_review": True},
        "amendment_policy": {"description": {"de": "Test."}},
        "created_at": "2026-01-01",
        "updated_at": "2026-01-01",
        "review": {"last_reviewed_at": "2026-01-01", "reviewers": ["reviewer-1"], "approval_decision": "Freigegeben fuer Testzwecke."},
    }


def _search_run(run_id: str, database: str, manifest_id: str, result_count: int) -> dict:
    if database == "pubmed":
        profile = {"id": "ncbi_eutils_esearch_v1", "rationale": None}
        request_parameters = {"db": "pubmed", "retmode": "json", "retmax": 1000, "retstart": 0}
        pagination = None
    else:
        profile = {"id": "clinicaltrials_gov_api_v2_v1", "rationale": None}
        request_parameters = {
            "query_parameter": "query.term", "countTotal": True, "pageSize": 100, "format": "json", "fields": "NCTId",
        }
        pagination = {"pages_retrieved": 1, "completion_confirmed": True}
    data = {
        "schema_version": "1.0.0", "id": run_id, "protocol_id": PROTOCOL_ID, "database": database,
        "interface": f"{database} test interface", "interface_profile": profile,
        "executed_at": "2026-01-01T10:00:00Z", "executed_by": "reviewer-1", "exact_query": "test",
        "filters": {}, "request_parameters": request_parameters,
        "result_capture": {"status": "complete", "manifest_id": manifest_id, "rationale": None},
        "date_range": {"from": None, "to": None}, "result_count": result_count,
        "export_reference": "research/raw/test/x.json", "notes": None, "status": "executed",
        "created_at": "2026-01-01", "updated_at": "2026-01-01",
        "review": {"last_reviewed_at": None, "reviewers": []},
    }
    if pagination is not None:
        data["pagination"] = pagination
    return data


def _result_manifest(manifest_id: str, search_run_id: str, identifier_type: str, identifiers: list[str]) -> dict:
    return {
        "schema_version": "1.0.0", "id": manifest_id, "search_run_id": search_run_id,
        "identifier_type": identifier_type, "identifiers": identifiers, "count": len(identifiers),
        "sha256": compute_manifest_sha256(identifiers), "source_export_reference": "research/raw/test/x.json",
        "created_at": "2026-01-01", "updated_at": "2026-01-01", "notes": None,
    }


def _candidate(candidate_id, namespace, value, discovered, metadata) -> dict:
    return {
        "candidate_id": candidate_id,
        "primary_identifier": {"namespace": namespace, "value": value},
        "discovered_in_search_run_ids": sorted(discovered),
        "metadata": metadata,
        "metadata_status": "fetched",
        "metadata_fetch_note": None,
        "metadata_provenance": {
            "source_interface": "test", "retrieved_at": "2026-01-02T00:00:00Z",
            "request_reference": "test", "response_locator": None,
        },
    }


def _pubmed_metadata(title="A Test Title", doi="10.1000/test", pmcid=None) -> dict:
    return {
        "title": title, "publication_year": 2024, "journal": "Test Journal",
        "publication_types": ["Journal Article"], "doi": doi, "pmcid": pmcid,
        "authors": ["Doe J"], "abstract_available": True, "language": "en",
    }


def _ctgov_metadata(brief_title="A Test Trial", official_title=None) -> dict:
    return {
        "brief_title": brief_title, "official_title": official_title, "overall_status": "COMPLETED",
        "phases": ["PHASE1"], "sponsor": "Test Sponsor", "interventions": ["Test Drug"],
        "conditions": ["Test Condition"], "study_type": "INTERVENTIONAL", "start_date": "2020-01-01",
        "primary_completion_date": "2020-06-01", "completion_date": "2020-06-01", "has_results": False,
        "last_update_posted": "2020-07-01",
    }


def base_pubmed_manifest(*, shared_doi: bool = False) -> dict:
    candidates = [
        _candidate(CAND_PM_1, "pmid", "100", [SEARCH_RUN_PUBMED], _pubmed_metadata(title="Study One", doi="10.1000/one")),
        _candidate(
            CAND_PM_2, "pmid", "200", [SEARCH_RUN_PUBMED],
            _pubmed_metadata(title="Study Two", doi="10.1000/shared" if shared_doi else "10.1000/two"),
        ),
        _candidate(
            CAND_PM_3, "pmid", "300", [SEARCH_RUN_PUBMED],
            _pubmed_metadata(title="Study Two Reply", doi="10.1000/shared" if shared_doi else "10.1000/three"),
        ),
    ]
    return {
        "schema_version": "1.0.0", "id": CANDIDATE_MANIFEST_PUBMED, "protocol_id": PROTOCOL_ID,
        "database": "pubmed", "identifier_namespace": "pmid", "source_search_run_ids": [SEARCH_RUN_PUBMED],
        "source_result_manifest_ids": [MANIFEST_PUBMED], "candidate_count": len(candidates),
        "candidates": candidates, "created_at": "2026-01-01", "updated_at": "2026-01-02",
    }


def base_ctgov_manifest() -> dict:
    candidates = [
        _candidate(CAND_CT_1, "nct_id", "NCT00000001", [SEARCH_RUN_CTGOV], _ctgov_metadata(brief_title="Trial One")),
        _candidate(CAND_CT_2, "nct_id", "NCT00000002", [SEARCH_RUN_CTGOV], _ctgov_metadata(brief_title="Trial Two")),
    ]
    return {
        "schema_version": "1.0.0", "id": CANDIDATE_MANIFEST_CTGOV, "protocol_id": PROTOCOL_ID,
        "database": "clinicaltrials_gov", "identifier_namespace": "nct_id",
        "source_search_run_ids": [SEARCH_RUN_CTGOV], "source_result_manifest_ids": [MANIFEST_CTGOV],
        "candidate_count": len(candidates), "candidates": candidates,
        "created_at": "2026-01-01", "updated_at": "2026-01-02",
    }


def write_tree(root: Path, tree: dict[str, dict | None]) -> None:
    for relative_path, data in tree.items():
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            yaml.safe_dump(data, handle, sort_keys=False, allow_unicode=True)


def _system_screening_initializer_reviewer() -> dict:
    """Registriert den technischen Initialisierungsakteur als research_reviewer (ADR-0059) --
    tools/validate_research.py::check_research_reviewers verlangt das ab dem Moment, in dem ein
    Datensatz screened_by/decided_by: system-screening-initializer tatsaechlich verwendet, was
    tools/initialize_screening_records.py fuer jeden erzeugten Record tut."""
    return {
        "schema_version": "1.0.0",
        "id": SYSTEM_SCREENING_INITIALIZER_ACTOR,
        "actor_type": "automation",
        "display_name": None,
        "description": "Testregistrierung fuer die Initialisierungs-Testsuite.",
        "active": True,
        "created_at": "2026-01-01",
        "updated_at": "2026-01-01",
    }


def base_tree(*, shared_doi: bool = False, include_ctgov: bool = True) -> dict[str, dict]:
    tree = {
        f"research/protocols/{PROTOCOL_ID}.yaml": _protocol(),
        f"research/search_runs/{SEARCH_RUN_PUBMED}.yaml": _search_run(SEARCH_RUN_PUBMED, "pubmed", MANIFEST_PUBMED, 3),
        f"research/search_results/{MANIFEST_PUBMED}.yaml": _result_manifest(MANIFEST_PUBMED, SEARCH_RUN_PUBMED, "pmid", ["100", "200", "300"]),
        f"research/candidates/{CANDIDATE_MANIFEST_PUBMED}.yaml": base_pubmed_manifest(shared_doi=shared_doi),
        f"research/reviewers/{SYSTEM_SCREENING_INITIALIZER_ACTOR}.yaml": _system_screening_initializer_reviewer(),
    }
    if include_ctgov:
        tree[f"research/search_runs/{SEARCH_RUN_CTGOV}.yaml"] = _search_run(SEARCH_RUN_CTGOV, "clinicaltrials_gov", MANIFEST_CTGOV, 2)
        tree[f"research/search_results/{MANIFEST_CTGOV}.yaml"] = _result_manifest(MANIFEST_CTGOV, SEARCH_RUN_CTGOV, "nct_id", ["NCT00000001", "NCT00000002"])
        tree[f"research/candidates/{CANDIDATE_MANIFEST_CTGOV}.yaml"] = base_ctgov_manifest()
    return tree


def _run_validation(tmp_path: Path):
    return run_validation(verbose=False, research_root=tmp_path / "research", data_root=tmp_path / "data")


@pytest.fixture
def isr_dirs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    research_root = tmp_path / "research"
    monkeypatch.setattr(isr, "CANDIDATES_DIR", research_root / "candidates")
    monkeypatch.setattr(isr, "SCREENING_DIR", research_root / "screening")
    monkeypatch.setattr(isr, "INITIALIZATION_MANIFEST_PATH", research_root / "screening_status" / "initialization_manifest.yaml")
    return research_root


# --- tools/initialize_screening_records.py -----------------------------------------------------


def test_initializer_creates_one_record_per_candidate_with_correct_split(tmp_path: Path, isr_dirs: Path):
    write_tree(tmp_path, base_tree())
    outcome = isr.initialize_protocol(PROTOCOL_ID)

    assert outcome.total_candidates == 5
    assert outcome.created == 5
    assert outcome.already_present == 0
    assert not outcome.conflicts
    assert not outcome.errors

    records = list((isr_dirs / "screening").glob("*.yaml"))
    assert len(records) == 5
    pmid_count = sum(1 for p in records if yaml.safe_load(p.read_text(encoding="utf-8"))["candidate_identifiers"]["pmid"])
    nct_count = sum(1 for p in records if yaml.safe_load(p.read_text(encoding="utf-8"))["candidate_identifiers"]["nct_id"])
    assert pmid_count == 3
    assert nct_count == 2


def test_initializer_generated_record_matches_mandated_initial_state(tmp_path: Path, isr_dirs: Path):
    write_tree(tmp_path, base_tree(include_ctgov=False))
    isr.initialize_protocol(PROTOCOL_ID)
    records = [yaml.safe_load(p.read_text(encoding="utf-8")) for p in (isr_dirs / "screening").glob("*.yaml")]
    record = next(r for r in records if r["candidate_id"] == CAND_PM_1)

    assert record["decision"] == "pending"
    assert record["decision_stage"] == "deduplication"
    assert record["full_text_status"] == "not_yet_obtained"
    assert record["screened_by"] == SYSTEM_SCREENING_INITIALIZER_ACTOR
    assert record["canonical_source_id"] is None
    assert record["candidate_manifest_id"] == CANDIDATE_MANIFEST_PUBMED
    assert record["candidate_id"] == CAND_PM_1
    assert record["candidate_title"] == "Study One"
    assert record["candidate_source_type"] == "peer_reviewed_publication"
    assert record["search_run_ids"] == [SEARCH_RUN_PUBMED]
    assert record["second_review"] is None
    assert len(record["decision_history"]) == 1
    entry = record["decision_history"][0]
    assert entry["decided_by"] == SYSTEM_SCREENING_INITIALIZER_ACTOR
    assert entry["primary_decision"] == "pending"
    assert entry["stage"] == "deduplication"
    assert entry["full_text_status"] == "not_yet_obtained"
    assert entry["second_review"] is None
    assert entry["duplicate_of"] is None


def test_initializer_ctgov_record_uses_official_title_fallback(tmp_path: Path, isr_dirs: Path):
    tree = base_tree()
    manifest = tree[f"research/candidates/{CANDIDATE_MANIFEST_CTGOV}.yaml"]
    manifest["candidates"][0]["metadata"] = _ctgov_metadata(brief_title=None, official_title="Official Fallback Title")
    write_tree(tmp_path, tree)
    isr.initialize_protocol(PROTOCOL_ID)
    records = [yaml.safe_load(p.read_text(encoding="utf-8")) for p in (isr_dirs / "screening").glob("*.yaml")]
    record = next(r for r in records if r["candidate_id"] == CAND_CT_1)
    assert record["candidate_title"] == "Official Fallback Title"
    assert record["candidate_source_type"] == "trial_registry"


def test_initializer_reports_data_error_when_both_ctgov_titles_missing(tmp_path: Path, isr_dirs: Path):
    tree = base_tree()
    manifest = tree[f"research/candidates/{CANDIDATE_MANIFEST_CTGOV}.yaml"]
    manifest["candidates"][0]["metadata"] = _ctgov_metadata(brief_title=None, official_title=None)
    write_tree(tmp_path, tree)
    outcome = isr.initialize_protocol(PROTOCOL_ID)

    assert outcome.created == 4  # everything except the broken candidate
    assert len(outcome.errors) == 1
    assert CAND_CT_1 in outcome.errors[0]
    # the broken candidate must not silently get a placeholder record
    records = [yaml.safe_load(p.read_text(encoding="utf-8")) for p in (isr_dirs / "screening").glob("*.yaml")]
    assert all(r["candidate_id"] != CAND_CT_1 for r in records)
    # a run with errors must not mark the protocol complete
    init_manifest = yaml.safe_load((isr_dirs / "screening_status" / "initialization_manifest.yaml").read_text(encoding="utf-8"))
    entry = next(p for p in init_manifest["protocols"] if p["protocol_id"] == PROTOCOL_ID)
    assert entry["status"] == "in_progress"
    assert entry["completed_at"] is None


def test_initializer_second_run_is_idempotent_and_keeps_ids_stable(tmp_path: Path, isr_dirs: Path):
    write_tree(tmp_path, base_tree())
    isr.initialize_protocol(PROTOCOL_ID)
    ids_first_run = {p.stem for p in (isr_dirs / "screening").glob("*.yaml")}

    outcome_second = isr.initialize_protocol(PROTOCOL_ID)

    assert outcome_second.created == 0
    assert outcome_second.already_present == 5
    assert not outcome_second.conflicts
    assert not outcome_second.errors
    ids_second_run = {p.stem for p in (isr_dirs / "screening").glob("*.yaml")}
    assert ids_first_run == ids_second_run


def test_initializer_marks_protocol_complete_after_full_clean_run(tmp_path: Path, isr_dirs: Path):
    write_tree(tmp_path, base_tree())
    isr.initialize_protocol(PROTOCOL_ID)
    init_manifest = yaml.safe_load((isr_dirs / "screening_status" / "initialization_manifest.yaml").read_text(encoding="utf-8"))
    entry = next(p for p in init_manifest["protocols"] if p["protocol_id"] == PROTOCOL_ID)
    assert entry["status"] == "complete"
    assert entry["expected_candidate_count"] == 5
    assert entry["initialized_by"] == SYSTEM_SCREENING_INITIALIZER_ACTOR
    assert entry["completed_at"] is not None


def test_initializer_writes_nothing_outside_screening_and_status_dirs(tmp_path: Path, isr_dirs: Path):
    write_tree(tmp_path, base_tree())
    before = {p for p in tmp_path.rglob("*") if p.is_file()}
    isr.initialize_protocol(PROTOCOL_ID)
    after = {p for p in tmp_path.rglob("*") if p.is_file()}
    new_files = after - before
    research_root = tmp_path / "research"
    assert all(
        p.is_relative_to(research_root / "screening") or p.is_relative_to(research_root / "screening_status")
        for p in new_files
    ), new_files
    assert not (research_root / "data").exists()
    assert not (research_root / "extractions").exists()
    assert not (research_root / "promotions").exists()


# --- validate_research.py: new Phase 4B-1B-1 checks ---------------------------------------------


def test_freshly_initialized_dataset_is_valid_with_only_expected_warnings(tmp_path: Path, isr_dirs: Path):
    write_tree(tmp_path, base_tree())
    isr.initialize_protocol(PROTOCOL_ID)
    report = _run_validation(tmp_path)
    assert report.error_count == 0, "\n".join(i.format() for i in report.issues)


def test_system_actor_decision_other_than_pending_is_rejected(tmp_path: Path, isr_dirs: Path):
    write_tree(tmp_path, base_tree(include_ctgov=False))
    isr.initialize_protocol(PROTOCOL_ID)
    record_path = next((isr_dirs / "screening").glob("*.yaml"))
    data = yaml.safe_load(record_path.read_text(encoding="utf-8"))
    data["decision_history"][0]["primary_decision"] = "include"
    data["decision_history"][0]["decision"] = "include"
    record_path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")

    report = _run_validation(tmp_path)
    messages = [i.message for i in report.issues if i.level == "ERROR"]
    assert any("must never record a decision other than 'pending'" in m for m in messages), messages


@pytest.mark.parametrize("decision", ["exclude", "duplicate"])
def test_system_actor_exclude_or_duplicate_is_rejected(tmp_path: Path, isr_dirs: Path, decision: str):
    write_tree(tmp_path, base_tree(include_ctgov=False))
    isr.initialize_protocol(PROTOCOL_ID)
    record_path = next((isr_dirs / "screening").glob("*.yaml"))
    data = yaml.safe_load(record_path.read_text(encoding="utf-8"))
    data["decision_history"][0]["primary_decision"] = decision
    data["decision_history"][0]["decision"] = decision
    if decision == "exclude":
        data["decision_history"][0]["primary_decision_reason"] = "other"
        data["decision_history"][0]["decision_reason"] = "other"
    else:
        data["decision_history"][0]["primary_duplicate_of"] = data["id"]
        data["decision_history"][0]["duplicate_of"] = data["id"]
    record_path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")

    report = _run_validation(tmp_path)
    messages = [i.message for i in report.issues if i.level == "ERROR"]
    assert any("system-screening-initializer" in m for m in messages), messages


def test_system_actor_record_with_nonnull_canonical_source_id_is_rejected(tmp_path: Path, isr_dirs: Path):
    write_tree(tmp_path, base_tree(include_ctgov=False))
    isr.initialize_protocol(PROTOCOL_ID)
    record_path = next((isr_dirs / "screening").glob("*.yaml"))
    data = yaml.safe_load(record_path.read_text(encoding="utf-8"))
    data["canonical_source_id"] = "source-example"
    record_path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")

    report = _run_validation(tmp_path)
    messages = [i.message for i in report.issues if i.level == "ERROR"]
    assert any("canonical_source_id" in i.path and "must stay null" in i.message for i in report.issues), messages


def test_duplicate_screening_record_for_same_candidate_is_rejected(tmp_path: Path, isr_dirs: Path):
    write_tree(tmp_path, base_tree(include_ctgov=False))
    isr.initialize_protocol(PROTOCOL_ID)
    record_path = next((isr_dirs / "screening").glob("*.yaml"))
    data = yaml.safe_load(record_path.read_text(encoding="utf-8"))
    data["id"] = "screening-record-90000000-0000-4000-8000-000000000099"
    (isr_dirs / "screening" / f"{data['id']}.yaml").write_text(
        yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8"
    )

    report = _run_validation(tmp_path)
    messages = [i.message for i in report.issues if i.level == "ERROR"]
    assert any("duplicate screening record for candidate" in m for m in messages), messages


def test_wrong_search_run_provenance_is_rejected(tmp_path: Path, isr_dirs: Path):
    write_tree(tmp_path, base_tree(include_ctgov=False))
    isr.initialize_protocol(PROTOCOL_ID)
    record_path = next((isr_dirs / "screening").glob("*.yaml"))
    data = yaml.safe_load(record_path.read_text(encoding="utf-8"))
    data["search_run_ids"] = ["search-run-00000000-0000-4000-8000-000000000000"]
    record_path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")

    report = _run_validation(tmp_path)
    messages = [i.message for i in report.issues if i.level == "ERROR"]
    assert any("must exactly match the referenced candidate's discovered_in_search_run_ids" in m for m in messages), messages


def test_completeness_check_is_silent_before_protocol_marked_complete(tmp_path: Path, isr_dirs: Path):
    tree = base_tree(include_ctgov=False)
    write_tree(tmp_path, tree)
    isr.initialize_protocol(PROTOCOL_ID)
    # remove one generated record so the protocol is no longer actually fully covered
    records = list((isr_dirs / "screening").glob("*.yaml"))
    records[0].unlink()
    # but downgrade the manifest back to in_progress so the completeness rule does not fire yet
    init_manifest_path = isr_dirs / "screening_status" / "initialization_manifest.yaml"
    init_manifest = yaml.safe_load(init_manifest_path.read_text(encoding="utf-8"))
    init_manifest["protocols"][0]["status"] = "in_progress"
    init_manifest["protocols"][0]["completed_at"] = None
    init_manifest_path.write_text(yaml.safe_dump(init_manifest, sort_keys=False), encoding="utf-8")

    report = _run_validation(tmp_path)
    assert report.error_count == 0, "\n".join(i.format() for i in report.issues)


def test_missing_record_after_marked_complete_is_rejected(tmp_path: Path, isr_dirs: Path):
    write_tree(tmp_path, base_tree(include_ctgov=False))
    isr.initialize_protocol(PROTOCOL_ID)
    records = list((isr_dirs / "screening").glob("*.yaml"))
    records[0].unlink()  # initialization manifest still claims status: complete / count 3

    report = _run_validation(tmp_path)
    messages = [i.message for i in report.issues if i.level == "ERROR"]
    assert any("has no screening record" in m for m in messages), messages


def test_stale_expected_candidate_count_is_rejected(tmp_path: Path, isr_dirs: Path):
    write_tree(tmp_path, base_tree(include_ctgov=False))
    isr.initialize_protocol(PROTOCOL_ID)
    init_manifest_path = isr_dirs / "screening_status" / "initialization_manifest.yaml"
    init_manifest = yaml.safe_load(init_manifest_path.read_text(encoding="utf-8"))
    init_manifest["protocols"][0]["expected_candidate_count"] = 999
    init_manifest_path.write_text(yaml.safe_dump(init_manifest, sort_keys=False), encoding="utf-8")

    report = _run_validation(tmp_path)
    messages = [i.message for i in report.issues if i.level == "ERROR"]
    assert any("currently total" in m for m in messages), messages


def test_shared_identifier_among_pristine_system_records_is_only_a_warning(tmp_path: Path, isr_dirs: Path):
    write_tree(tmp_path, base_tree(include_ctgov=False, shared_doi=True))
    isr.initialize_protocol(PROTOCOL_ID)

    report = _run_validation(tmp_path)
    errors = [i.message for i in report.issues if i.level == "ERROR"]
    warnings = [i.message for i in report.issues if i.level == "WARNING"]
    assert not any("shared" in m and "doi" in m for m in errors), errors
    assert any("potential duplicate doi" in m for m in warnings), warnings


def test_shared_identifier_becomes_error_once_dedup_phase_is_complete_for_all(tmp_path: Path, isr_dirs: Path):
    write_tree(tmp_path, base_tree(include_ctgov=False, shared_doi=True))
    isr.initialize_protocol(PROTOCOL_ID)
    records = list((isr_dirs / "screening").glob("*.yaml"))
    for path in records:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if data["candidate_identifiers"]["doi"] != "10.1000/shared":
            continue
        # a human reviewer takes the record over, still undecided about which is the duplicate
        data["screened_by"] = "reviewer-1"
        data["decision_history"][0]["decided_by"] = "reviewer-1"
        path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")

    report = _run_validation(tmp_path)
    errors = [i.message for i in report.issues if i.level == "ERROR"]
    assert any("duplicate doi" in m and "mark the redundant record(s) as decision: duplicate" in m for m in errors), errors


def test_screening_record_for_protocol_without_candidate_manifest_is_still_migration_compatible(tmp_path: Path, isr_dirs: Path):
    """Ein Protokoll ohne jegliches Candidate Manifest bleibt migrationskompatibel -- die
    Vollstaendigkeitspruefung darf ohne Initialization Manifest nicht greifen."""
    tree = {f"research/protocols/{PROTOCOL_ID}.yaml": _protocol()}
    write_tree(tmp_path, tree)
    report = _run_validation(tmp_path)
    assert report.error_count == 0, "\n".join(i.format() for i in report.issues)

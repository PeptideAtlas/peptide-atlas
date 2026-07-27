"""Tests fuer tools/build_research_candidates.py (siehe ADR-0056).

Die Modulkonstanten SEARCH_RUNS_DIR/SEARCH_RESULTS_DIR/CANDIDATES_DIR werden je Test per
monkeypatch auf ein isoliertes tmp_path-Verzeichnis umgebogen, damit kein Test die echten
research/**-Daten dieses Repos liest oder schreibt. Netzwerkaufrufe (--refresh-metadata) werden
durch einen gefaelschten _http_get_json ersetzt -- dieses Modul prueft die Verarbeitungslogik,
keine echte API-Erreichbarkeit."""

from __future__ import annotations

from pathlib import Path

import build_research_candidates as brc
import pytest
import yaml


def _write_yaml(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(data, handle, sort_keys=False)


@pytest.fixture
def research_dirs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    research_root = tmp_path / "research"
    monkeypatch.setattr(brc, "SEARCH_RUNS_DIR", research_root / "search_runs")
    monkeypatch.setattr(brc, "SEARCH_RESULTS_DIR", research_root / "search_results")
    monkeypatch.setattr(brc, "CANDIDATES_DIR", research_root / "candidates")
    return research_root


def _search_run(database: str, manifest_id: str, protocol_id: str = "research-protocol-test-substance-v1") -> dict:
    return {
        "schema_version": "1.0.0",
        "id": "placeholder",
        "protocol_id": protocol_id,
        "database": database,
        "result_capture": {"status": "complete", "manifest_id": manifest_id, "rationale": None},
    }


def _manifest(search_run_id: str, identifier_type: str, identifiers: list[str]) -> dict:
    return {
        "id": "placeholder",
        "search_run_id": search_run_id,
        "identifier_type": identifier_type,
        "identifiers": identifiers,
    }


def _setup_pubmed_dataset(research_root: Path) -> None:
    run_a = _search_run("pubmed", "search-result-manifest-A")
    run_a["id"] = "search-run-A"
    run_b = _search_run("pubmed", "search-result-manifest-B")
    run_b["id"] = "search-run-B"
    manifest_a = _manifest("search-run-A", "pmid", ["100", "200"])
    manifest_a["id"] = "search-result-manifest-A"
    manifest_b = _manifest("search-run-B", "pmid", ["200", "300"])
    manifest_b["id"] = "search-result-manifest-B"

    _write_yaml(research_root / "search_runs" / "search-run-A.yaml", run_a)
    _write_yaml(research_root / "search_runs" / "search-run-B.yaml", run_b)
    _write_yaml(research_root / "search_results" / "search-result-manifest-A.yaml", manifest_a)
    _write_yaml(research_root / "search_results" / "search-result-manifest-B.yaml", manifest_b)


def test_build_candidate_manifest_unions_and_tracks_provenance(research_dirs: Path):
    _setup_pubmed_dataset(research_dirs)
    manifest, existing_path = brc.build_candidate_manifest("research-protocol-test-substance-v1", "pubmed")

    assert existing_path is None
    assert manifest["candidate_count"] == 3
    assert manifest["identifier_namespace"] == "pmid"
    by_value = {c["primary_identifier"]["value"]: c for c in manifest["candidates"]}
    assert sorted(by_value) == ["100", "200", "300"]
    assert by_value["100"]["discovered_in_search_run_ids"] == ["search-run-A"]
    assert by_value["200"]["discovered_in_search_run_ids"] == ["search-run-A", "search-run-B"]
    assert by_value["300"]["discovered_in_search_run_ids"] == ["search-run-B"]
    for candidate in manifest["candidates"]:
        assert candidate["metadata_status"] == "not_fetched"
        assert candidate["metadata"] is None
        assert candidate["candidate_id"].startswith("research-candidate-")


def test_build_candidate_manifest_is_deterministic_on_rerun(research_dirs: Path):
    _setup_pubmed_dataset(research_dirs)
    manifest_1, _ = brc.build_candidate_manifest("research-protocol-test-substance-v1", "pubmed")
    brc.write_manifest(manifest_1, None)

    manifest_2, existing_path = brc.build_candidate_manifest("research-protocol-test-substance-v1", "pubmed")

    assert existing_path is not None
    assert manifest_2["id"] == manifest_1["id"]
    assert manifest_2["created_at"] == manifest_1["created_at"]
    assert manifest_2["updated_at"] == manifest_1["updated_at"]  # unchanged input -> unchanged updated_at
    assert {c["candidate_id"] for c in manifest_2["candidates"]} == {c["candidate_id"] for c in manifest_1["candidates"]}


def test_build_candidate_manifest_preserves_metadata_and_candidate_id(research_dirs: Path):
    _setup_pubmed_dataset(research_dirs)
    manifest_1, _ = brc.build_candidate_manifest("research-protocol-test-substance-v1", "pubmed")
    for candidate in manifest_1["candidates"]:
        if candidate["primary_identifier"]["value"] == "200":
            candidate["metadata_status"] = "fetched"
            candidate["metadata"] = {"title": "Already Fetched"}
            candidate["metadata_provenance"] = {
                "source_interface": "test", "retrieved_at": "2026-01-01T00:00:00Z",
                "request_reference": "test", "response_locator": None,
            }
    path = brc.write_manifest(manifest_1, None)

    # A new search run/manifest surfaces one more identifier ("400") -- re-running must keep the
    # existing candidate_id/metadata for "100"/"200"/"300" untouched and only add "400" as new.
    run_c = _search_run("pubmed", "search-result-manifest-C")
    run_c["id"] = "search-run-C"
    manifest_c = _manifest("search-run-C", "pmid", ["400"])
    manifest_c["id"] = "search-result-manifest-C"
    _write_yaml(research_dirs / "search_runs" / "search-run-C.yaml", run_c)
    _write_yaml(research_dirs / "search_results" / "search-result-manifest-C.yaml", manifest_c)

    manifest_2, existing_path = brc.build_candidate_manifest("research-protocol-test-substance-v1", "pubmed")
    assert existing_path == path
    assert manifest_2["candidate_count"] == 4
    by_value = {c["primary_identifier"]["value"]: c for c in manifest_2["candidates"]}
    assert by_value["200"]["metadata_status"] == "fetched"
    assert by_value["200"]["metadata"] == {"title": "Already Fetched"}
    original_by_value = {c["primary_identifier"]["value"]: c for c in manifest_1["candidates"]}
    assert by_value["100"]["candidate_id"] == original_by_value["100"]["candidate_id"]
    assert by_value["200"]["candidate_id"] == original_by_value["200"]["candidate_id"]
    assert by_value["300"]["candidate_id"] == original_by_value["300"]["candidate_id"]
    assert by_value["400"]["metadata_status"] == "not_fetched"


def test_build_candidate_manifest_raises_without_any_complete_search_run(research_dirs: Path):
    with pytest.raises(LookupError):
        brc.build_candidate_manifest("research-protocol-test-substance-v1", "pubmed")


def test_refresh_metadata_updates_fetched_candidates(research_dirs: Path, monkeypatch: pytest.MonkeyPatch):
    _setup_pubmed_dataset(research_dirs)
    manifest, _ = brc.build_candidate_manifest("research-protocol-test-substance-v1", "pubmed")
    path = brc.write_manifest(manifest, None)

    fake_esummary_response = {
        "result": {
            "100": {
                "title": "Fake Title", "sortpubdate": "2024/01/01 00:00", "fulljournalname": "Fake Journal",
                "pubtype": ["Journal Article"], "articleids": [{"idtype": "doi", "value": "10.1/fake"}],
                "authors": [{"name": "Doe J"}], "attributes": ["Has Abstract"], "lang": ["eng"],
            },
            "200": {
                "title": "", "sortpubdate": "", "fulljournalname": None, "pubtype": [], "articleids": [],
                "authors": [], "attributes": [], "lang": [],
            },
        }
    }

    def fake_http_get_json(url, params):
        assert url == brc.PUBMED_ESUMMARY_URL
        return fake_esummary_response

    monkeypatch.setattr(brc, "_http_get_json", fake_http_get_json)

    brc.refresh_metadata("research-protocol-test-substance-v1", "pubmed")

    updated = yaml.safe_load(path.read_text(encoding="utf-8"))
    by_value = {c["primary_identifier"]["value"]: c for c in updated["candidates"]}

    assert by_value["100"]["metadata_status"] == "fetched"
    assert by_value["100"]["metadata"]["title"] == "Fake Title"
    assert by_value["100"]["metadata"]["publication_year"] == 2024
    assert by_value["100"]["metadata"]["doi"] == "10.1/fake"
    assert by_value["100"]["metadata"]["abstract_available"] is True
    assert by_value["100"]["metadata"]["language"] == "en"
    assert by_value["100"]["metadata_provenance"]["source_interface"] == "NCBI E-utilities ESummary"

    # "200" got an (empty) record back but has no title/abstract info -> partial, not fetched.
    assert by_value["200"]["metadata_status"] == "partial"

    # "300" was never in the ESummary response at all -> not_found with a technical note, and its
    # discovery identity (candidate_id, primary_identifier) must be completely untouched.
    assert by_value["300"]["metadata_status"] == "not_found"
    assert by_value["300"]["metadata"] is None
    assert by_value["300"]["metadata_fetch_note"]
    original_300 = next(c for c in manifest["candidates"] if c["primary_identifier"]["value"] == "300")
    assert by_value["300"]["candidate_id"] == original_300["candidate_id"]
    assert by_value["300"]["primary_identifier"] == original_300["primary_identifier"]


def test_refresh_metadata_network_failure_does_not_lose_candidates(research_dirs: Path, monkeypatch: pytest.MonkeyPatch):
    _setup_pubmed_dataset(research_dirs)
    manifest, _ = brc.build_candidate_manifest("research-protocol-test-substance-v1", "pubmed")
    path = brc.write_manifest(manifest, None)

    def failing_http_get_json(url, params):
        raise OSError("simulated network failure")

    monkeypatch.setattr(brc, "_http_get_json", failing_http_get_json)

    brc.refresh_metadata("research-protocol-test-substance-v1", "pubmed")

    updated = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert updated["candidate_count"] == 3
    for candidate in updated["candidates"]:
        assert candidate["metadata_status"] == "fetch_error"
        assert candidate["metadata"] is None
        assert candidate["metadata_fetch_note"]
        assert candidate["candidate_id"]
        assert candidate["primary_identifier"]["value"] in ("100", "200", "300")


def test_refresh_metadata_skips_when_nothing_to_refresh(research_dirs: Path, monkeypatch: pytest.MonkeyPatch, capsys):
    _setup_pubmed_dataset(research_dirs)
    manifest, _ = brc.build_candidate_manifest("research-protocol-test-substance-v1", "pubmed")
    for candidate in manifest["candidates"]:
        candidate["metadata_status"] = "fetched"
        candidate["metadata"] = {"title": "x"}
    brc.write_manifest(manifest, None)

    def unexpected_call(*args, **kwargs):
        raise AssertionError("should not perform any HTTP call when nothing needs a refresh")

    monkeypatch.setattr(brc, "_http_get_json", unexpected_call)

    brc.refresh_metadata("research-protocol-test-substance-v1", "pubmed")  # must not raise

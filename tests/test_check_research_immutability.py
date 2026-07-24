"""Tests fuer tools/check_research_immutability.py gegen ein isoliertes temporaeres Git-Repo
(nicht das Peptide-Atlas-Repo selbst) -- vermeidet jede Abhaengigkeit von der tatsaechlichen
Commit-Historie oder einem echten Remote."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
from check_research_immutability import check

SEARCH_RUN_YAML = """schema_version: "1.0.0"
id: search-run-40000000-0000-4000-8000-000000000001
protocol_id: research-protocol-test-substance-v1
database: pubmed
interface: PubMed web interface
executed_at: "2026-01-01T10:00:00Z"
executed_by: reviewer-1
exact_query: '"test substance"[Title/Abstract]'
filters: {{}}
date_range: {{ from: null, to: null }}
result_count: {result_count}
export_reference: null
notes: null
status: {status}
created_at: "2026-01-01"
updated_at: "2026-01-01"
review:
  last_reviewed_at: null
  reviewers: []
"""


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-c", "user.email=test@example.invalid", "-c", "user.name=Test", *args],
        cwd=repo, capture_output=True, text=True, check=True,
    )
    return result.stdout


@pytest.fixture
def base_repo(tmp_path: Path) -> tuple[Path, str, Path]:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    search_run_dir = repo / "research" / "search_runs"
    search_run_dir.mkdir(parents=True)
    file_path = search_run_dir / "search-run-40000000-0000-4000-8000-000000000001.yaml"
    file_path.write_text(SEARCH_RUN_YAML.format(result_count=3, status="executed"), encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-q", "-m", "base: add search run")
    base_sha = _git(repo, "rev-parse", "HEAD").strip()
    return repo, base_sha, file_path


def test_no_changes_reports_no_errors(base_repo):
    repo, base_sha, _ = base_repo
    assert check(repo, base_sha) == []


def test_status_and_metadata_only_change_is_allowed(base_repo):
    repo, base_sha, file_path = base_repo
    file_path.write_text(SEARCH_RUN_YAML.format(result_count=3, status="superseded"), encoding="utf-8")
    assert check(repo, base_sha) == []


def test_execution_field_change_is_flagged(base_repo):
    repo, base_sha, file_path = base_repo
    file_path.write_text(SEARCH_RUN_YAML.format(result_count=99, status="executed"), encoding="utf-8")
    errors = check(repo, base_sha)
    assert len(errors) == 1
    assert "result_count" in errors[0]


def test_deleted_file_is_flagged(base_repo):
    repo, base_sha, file_path = base_repo
    file_path.unlink()
    errors = check(repo, base_sha)
    assert len(errors) == 1
    assert "deleted" in errors[0]


def test_new_search_run_file_is_allowed(base_repo):
    repo, base_sha, _ = base_repo
    new_file = repo / "research" / "search_runs" / "search-run-40000000-0000-4000-8000-000000000002.yaml"
    new_file.write_text(SEARCH_RUN_YAML.format(result_count=1, status="executed"), encoding="utf-8")
    assert check(repo, base_sha) == []


def test_renamed_file_is_flagged_as_deletion(base_repo):
    repo, base_sha, file_path = base_repo
    new_path = file_path.with_name("search-run-40000000-0000-4000-8000-000000000099.yaml")
    file_path.rename(new_path)
    errors = check(repo, base_sha)
    assert any("deleted" in e for e in errors)

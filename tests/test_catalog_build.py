"""Tests fuer tools/build_catalog.py."""

from __future__ import annotations

from pathlib import Path

from build_catalog import build_catalog

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"
VALID_ROOT = FIXTURES_DIR / "valid"

FIXED_TIMESTAMP = "2026-01-01T00:00:00Z"


def test_catalog_contains_all_object_kinds():
    catalog = build_catalog(VALID_ROOT, FIXED_TIMESTAMP)

    assert catalog["schema_version"] == "1.0.0"
    assert catalog["generated_at"] == FIXED_TIMESTAMP
    assert catalog["counts"]["sources"] == 1
    assert catalog["counts"]["claims"] == 3
    assert catalog["counts"]["substances"] == 1
    assert catalog["counts"]["receptors"] == 1
    assert catalog["counts"]["studies"] == 1

    entity_ids = [e["id"] for e in catalog["entities"]]
    assert "substance-test" in entity_ids
    assert "receptor-test" in entity_ids
    assert "study-test" in entity_ids

    assert [s["id"] for s in catalog["studies"]] == ["study-test"]
    assert [s["id"] for s in catalog["sources"]] == ["source-test"]


def test_catalog_is_deterministically_sorted():
    first = build_catalog(VALID_ROOT, FIXED_TIMESTAMP)
    second = build_catalog(VALID_ROOT, FIXED_TIMESTAMP)
    assert first == second

    entity_ids = [e["id"] for e in first["entities"]]
    assert entity_ids == sorted(entity_ids)

    claim_ids = [c["id"] for c in first["claims"]]
    assert claim_ids == sorted(claim_ids)


def test_catalog_has_no_circular_embedding():
    catalog = build_catalog(VALID_ROOT, FIXED_TIMESTAMP)
    for claim in catalog["claims"]:
        obj = claim.get("object") or {}
        if "entity_id" in obj:
            assert isinstance(obj["entity_id"], str)
        assert isinstance(claim["subject_id"], str)

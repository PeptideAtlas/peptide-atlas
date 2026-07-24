"""Tests fuer tools/export_graph.py."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema
from export_graph import build_graph
from _datalib import build_schema_registry

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"
VALID_ROOT = FIXTURES_DIR / "valid"

FIXED_TIMESTAMP = "2026-01-01T00:00:00Z"


def test_graph_contains_expected_nodes_and_edges():
    graph = build_graph(VALID_ROOT, FIXED_TIMESTAMP)

    node_ids = {n["id"] for n in graph["nodes"]}
    assert {"substance-test", "receptor-test", "study-test"} <= node_ids

    # claim-...001 hat ein entity_id-Objekt -> erzeugt eine Edge.
    # claim-...002 hat ein Literalwert-Objekt -> erzeugt KEINE Edge.
    assert len(graph["edges"]) == 1
    edge = graph["edges"][0]
    assert edge["from"] == "substance-test"
    assert edge["to"] == "receptor-test"
    assert edge["predicate"] == "interacts_with"
    assert edge["source_ids"] == ["source-test"]


def test_graph_edges_conform_to_relationship_schema():
    graph = build_graph(VALID_ROOT, FIXED_TIMESTAMP)
    registry, schemas = build_schema_registry()
    schema = schemas["relationship.schema.json"]
    validator_cls = jsonschema.validators.validator_for(schema)
    validator = validator_cls(schema, registry=registry)

    for edge in graph["edges"]:
        errors = list(validator.iter_errors(edge))
        assert not errors, f"edge does not conform to relationship.schema.json: {errors}"


def test_graph_export_is_deterministic():
    first = build_graph(VALID_ROOT, FIXED_TIMESTAMP)
    second = build_graph(VALID_ROOT, FIXED_TIMESTAMP)
    assert first == second

    node_ids = [n["id"] for n in first["nodes"]]
    assert node_ids == sorted(node_ids)

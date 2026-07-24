"""Verhindert stilles Auseinanderlaufen zwischen den in schemas/common.schema.json hart
kodierten Research-Enum-Werten und den kontrollierten YAML-Vokabularen unter
research/vocabularies/. Analog zu tests/test_vocabulary_consistency.py fuer die
kanonische Datenebene.

review_decisions.yaml ist bewusst NICHT hier aufgefuehrt: second_review.decision_confirmed
ist im Schema ein Boolean, kein Enum -- die YAML-Datei dient nur als Anzeigenamen-Referenz
fuer die Redaktion, es besteht kein Drift-Risiko zwischen zwei maschinenlesbaren Werten.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_DIR = REPO_ROOT / "schemas"
RESEARCH_VOCAB_DIR = REPO_ROOT / "research" / "vocabularies"


def _common_schema() -> dict:
    with (SCHEMA_DIR / "common.schema.json").open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _vocab_values(name: str) -> set[str]:
    with (RESEARCH_VOCAB_DIR / f"{name}.yaml").open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    return {entry["value"] for entry in data["values"]}


_COMMON = _common_schema()

DUPLICATED_ENUMS = [
    ("research_database", set(_COMMON["$defs"]["research_database"]["enum"]), "research_databases"),
    ("screening_stage", set(_COMMON["$defs"]["screening_stage"]["enum"]), "screening_stages"),
    ("screening_decision", set(_COMMON["$defs"]["screening_decision"]["enum"]), "screening_decisions"),
    ("exclusion_reason", set(_COMMON["$defs"]["exclusion_reason"]["enum"]), "exclusion_reasons"),
    ("full_text_status", set(_COMMON["$defs"]["full_text_status"]["enum"]), "full_text_statuses"),
    ("extraction_status", set(_COMMON["$defs"]["extraction_status"]["enum"]), "extraction_statuses"),
    ("search_run_status", set(_COMMON["$defs"]["search_run_status"]["enum"]), "search_run_statuses"),
    ("promotion_status", set(_COMMON["$defs"]["promotion_status"]["enum"]), "promotion_statuses"),
]

# research_protocol_statuses.yaml dupliziert das status-Enum, das direkt (nicht ueber
# common.schema.json) in research_protocol.schema.json liegt -- separat behandelt.


def _protocol_status_enum() -> set[str]:
    with (SCHEMA_DIR / "research_protocol.schema.json").open("r", encoding="utf-8") as handle:
        schema = json.load(handle)
    return set(schema["properties"]["status"]["enum"])


@pytest.mark.parametrize("label, schema_values, vocab_name", DUPLICATED_ENUMS, ids=[d[0] for d in DUPLICATED_ENUMS])
def test_schema_enum_matches_research_vocabulary(label: str, schema_values: set[str], vocab_name: str):
    vocab_values = _vocab_values(vocab_name)

    only_in_schema = schema_values - vocab_values
    only_in_vocab = vocab_values - schema_values

    assert not only_in_schema, (
        f"{label}: schemas/common.schema.json has values not present in "
        f"research/vocabularies/{vocab_name}.yaml: {sorted(only_in_schema)}"
    )
    assert not only_in_vocab, (
        f"{label}: research/vocabularies/{vocab_name}.yaml has values not present in the "
        f"schema enum: {sorted(only_in_vocab)}"
    )


def test_research_protocol_status_matches_vocabulary():
    schema_values = _protocol_status_enum()
    vocab_values = _vocab_values("research_protocol_statuses")

    only_in_schema = schema_values - vocab_values
    only_in_vocab = vocab_values - schema_values

    assert not only_in_schema, f"schema has values not in vocabulary: {sorted(only_in_schema)}"
    assert not only_in_vocab, f"vocabulary has values not in schema: {sorted(only_in_vocab)}"

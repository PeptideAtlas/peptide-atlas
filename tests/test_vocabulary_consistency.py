"""Verhindert stilles Auseinanderlaufen zwischen den in JSON Schema hart kodierten
Enum-Werten und den kontrollierten YAML-Vokabularen unter data/vocabularies/.

Bekannte technische Schuld (siehe docs/project/Phase_3_Scientific_Data_Architecture.md,
Abschnitt "Bekannte Grenzen"): die kontrollierten Werte sind aktuell an zwei Stellen
gepflegt (schemas/*.json als Enum, data/vocabularies/*.yaml als kanonisches Vokabular
mit Anzeigenamen). Eine vollstaendige Umstellung auf dynamisch aus den YAML-Dateien
generierte JSON-Schema-Enums ist fuer eine spaetere Phase vorgesehen. Bis dahin
verhindert dieser Test, dass beide Stellen unbemerkt auseinanderlaufen: er schlaegt
fehl, sobald ein Wert in nur einer der beiden Quellen existiert.

predicate ist bewusst NICHT hier aufgefuehrt: claim.schema.json prueft predicate nur
per Regex-Pattern (lower_snake_case), nicht per Enum -- data/vocabularies/predicates.yaml
ist dafuer bereits die alleinige Quelle der Wahrheit, geprueft durch den Validator
(tools/validate_data.py), nicht durch das Schema. Dort besteht daher kein Drift-Risiko.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_DIR = REPO_ROOT / "schemas"
VOCAB_DIR = REPO_ROOT / "data" / "vocabularies"


def _schema(name: str) -> dict:
    with (SCHEMA_DIR / name).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _vocab_values(name: str) -> set[str]:
    with (VOCAB_DIR / f"{name}.yaml").open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    return {entry["value"] for entry in data["values"]}


# (Bezeichnung, Enum-Werte aus dem Schema, zugehoeriges Vokabular)
DUPLICATED_ENUMS = [
    (
        "evidence_category",
        set(_schema("common.schema.json")["$defs"]["evidence_category"]["enum"]),
        "evidence_categories",
    ),
    (
        "certainty_level",
        set(_schema("common.schema.json")["$defs"]["certainty_level"]["enum"]),
        "certainty_levels",
    ),
    (
        "evidence_direction",
        set(_schema("common.schema.json")["$defs"]["evidence_direction"]["enum"]),
        "evidence_directions",
    ),
    (
        "study_design",
        set(_schema("common.schema.json")["$defs"]["study_design"]["enum"]),
        "study_designs",
    ),
    (
        "editorial_status",
        set(_schema("common.schema.json")["$defs"]["editorial_status"]["enum"]),
        "editorial_statuses",
    ),
    (
        "source_type",
        set(_schema("common.schema.json")["$defs"]["source_type"]["enum"]),
        "source_types",
    ),
    (
        "entity_type",
        set(_schema("entity.schema.json")["properties"]["entity_type"]["enum"]),
        "entity_types",
    ),
    (
        "substance_classes",
        set(
            _schema("substance.schema.json")["allOf"][1]["properties"]["substance_classes"]["items"]["enum"]
        ),
        "substance_classes",
    ),
]


@pytest.mark.parametrize("label, schema_values, vocab_name", DUPLICATED_ENUMS, ids=[d[0] for d in DUPLICATED_ENUMS])
def test_schema_enum_matches_vocabulary(label: str, schema_values: set[str], vocab_name: str):
    vocab_values = _vocab_values(vocab_name)

    only_in_schema = schema_values - vocab_values
    only_in_vocab = vocab_values - schema_values

    assert not only_in_schema, (
        f"{label}: schemas/*.json has values not present in data/vocabularies/{vocab_name}.yaml: "
        f"{sorted(only_in_schema)}"
    )
    assert not only_in_vocab, (
        f"{label}: data/vocabularies/{vocab_name}.yaml has values not present in the schema enum: "
        f"{sorted(only_in_vocab)}"
    )

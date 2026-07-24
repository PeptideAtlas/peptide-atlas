"""Interne, gemeinsam genutzte Hilfsfunktionen fuer die Phase-3-Tools.

Nicht Teil der oeffentlichen Tool-Oberflaeche (siehe validate_data.py,
build_catalog.py, export_graph.py, new_id.py) -- dient ausschliesslich der
Vermeidung doppelter Lade-/Registry-Logik zwischen diesen Skripten.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterator
from urllib.parse import urlsplit, urlunsplit

import yaml
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_DIR = REPO_ROOT / "schemas"
DATA_DIR = REPO_ROOT / "data"
DOCS_DIR = REPO_ROOT / "docs"
BUILD_DIR = REPO_ROOT / "build"

ENTITY_FOLDER_TO_TYPE = {
    "substances": "substance",
    "receptors": "receptor",
    "pathways": "pathway",
    "conditions": "condition",
    "adverse_events": "adverse_event",
    "organizations": "organization",
    "studies": "study",
}

ENTITY_TYPE_TO_SCHEMA_ID = {
    "substance": "substance.schema.json",
    "receptor": "receptor.schema.json",
    "pathway": "pathway.schema.json",
    "condition": "condition.schema.json",
    "adverse_event": "adverse_event.schema.json",
    "organization": "organization.schema.json",
    "study": "study.schema.json",
}

SCHEMA_VERSION = "1.0.0"


class DataFileError(Exception):
    """Wird geworfen, wenn eine YAML-Datei nicht sicher geladen werden kann."""


@dataclass
class DataFile:
    path: Path
    relative_path: str
    kind: str  # "entity" | "source" | "claim"
    entity_type: str | None
    data: Any


@dataclass
class Vocabulary:
    name: str
    values: set[str] = field(default_factory=set)
    entries: dict[str, dict] = field(default_factory=dict)


def load_yaml_file(path: Path) -> Any:
    """Laedt eine YAML-Datei ausschliesslich mit yaml.safe_load.

    Es werden bewusst keine anderen Loader verwendet, um die Ausfuehrung von
    beliebigem Python-Code oder Objekten aus Datendateien strukturell
    auszuschliessen (siehe Qualitaetsregeln, Abschnitt Sicherheit).
    """
    try:
        with path.open("r", encoding="utf-8") as handle:
            return yaml.safe_load(handle)
    except yaml.YAMLError as exc:
        raise DataFileError(f"invalid YAML: {exc}") from exc


def relative(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT).as_posix())


def iter_yaml_files(directory: Path) -> Iterator[Path]:
    if not directory.exists():
        return
    for path in sorted(directory.rglob("*.yaml")):
        if path.is_file():
            yield path
    for path in sorted(directory.rglob("*.yml")):
        if path.is_file():
            yield path


def iter_entity_files(root: Path) -> Iterator[tuple[Path, str]]:
    """Liefert (Pfad, entity_type) fuer jede Entitaetsdatei unter root/entities/*."""
    entities_root = root / "entities"
    if not entities_root.exists():
        return
    for folder, entity_type in ENTITY_FOLDER_TO_TYPE.items():
        for path in iter_yaml_files(entities_root / folder):
            yield path, entity_type


def iter_example_entity_files(examples_root: Path) -> Iterator[tuple[Path, str]]:
    """Wie iter_entity_files, aber fuer data/examples/, wo 'studies' bewusst als
    eigenstaendiger Ordner neben 'entities/' liegt statt darunter (siehe Abschnitt 8
    der Phase-3-Spezifikation: data/examples/{entities,studies,sources,claims})."""
    entities_root = examples_root / "entities"
    for folder, entity_type in ENTITY_FOLDER_TO_TYPE.items():
        if folder == "studies":
            continue
        for path in iter_yaml_files(entities_root / folder):
            yield path, entity_type
    for path in iter_yaml_files(examples_root / "studies"):
        yield path, "study"


def iter_source_files(root: Path) -> Iterator[Path]:
    yield from iter_yaml_files(root / "sources")


def iter_claim_files(root: Path) -> Iterator[Path]:
    yield from iter_yaml_files(root / "claims")


def load_vocabulary(name: str) -> Vocabulary:
    path = DATA_DIR / "vocabularies" / f"{name}.yaml"
    raw = load_yaml_file(path)
    vocab = Vocabulary(name=name)
    for entry in raw.get("values", []):
        value = entry["value"]
        vocab.values.add(value)
        vocab.entries[value] = entry
    return vocab


def load_all_vocabularies() -> dict[str, Vocabulary]:
    names = [
        "entity_types",
        "substance_classes",
        "predicates",
        "evidence_categories",
        "certainty_levels",
        "source_types",
        "study_designs",
        "editorial_statuses",
        "evidence_directions",
    ]
    return {name: load_vocabulary(name) for name in names}


def normalize_doi(value: str) -> str:
    """Kanonische, verlustarme DOI-Normalisierung fuer Duplikaterkennung.

    Anders als tools/new_id.py::normalize_doi (das einen ID-Slug erzeugt) wird hier NICHT
    jedes Sonderzeichen durch '-' ersetzt, da das unterschiedliche DOIs faelschlich
    gleichsetzen wuerde (z. B. '10.1000/A.B' vs. '10.1000/A-B'). Nur Groß-/Kleinschreibung
    und die URL-Form werden vereinheitlicht.
    """
    text = value.strip()
    text = re.sub(r"^https?://(dx\.)?doi\.org/", "", text, flags=re.IGNORECASE)
    return text.lower()


def normalize_pmid(value: str) -> str:
    digits = re.sub(r"\D", "", value)
    return digits.lstrip("0") or "0"


def normalize_pmcid(value: str) -> str:
    text = value.strip().upper()
    text = re.sub(r"^PMC", "", text)
    digits = re.sub(r"\D", "", text)
    return f"PMC{digits.lstrip('0') or '0'}"


def normalize_isbn(value: str) -> str:
    text = re.sub(r"[\s-]", "", value.strip())
    return text.upper()


def normalize_url(value: str) -> str:
    """Kanonisiert eine URL fuer den Duplikatvergleich: Schema/Host lowercase, kein
    trailing slash, kein Fragment. Nur als Warnungsgrundlage gedacht (Redirects/Mirrors
    koennen unterschiedliche, aber inhaltlich identische URLs erzeugen -- daher keine
    aggressivere Normalisierung wie Query-Sortierung)."""
    parts = urlsplit(value.strip())
    scheme = parts.scheme.lower()
    netloc = parts.netloc.lower()
    path = parts.path.rstrip("/") or "/"
    return urlunsplit((scheme, netloc, path, parts.query, ""))


def build_schema_registry() -> tuple[Registry, dict[str, dict]]:
    schemas: dict[str, dict] = {}
    for path in sorted(SCHEMA_DIR.glob("*.schema.json")):
        with path.open("r", encoding="utf-8") as handle:
            schema = json.load(handle)
        schema_id = schema["$id"]
        schemas[schema_id] = schema

    resources = [
        (schema_id, Resource.from_contents(schema, default_specification=DRAFT202012))
        for schema_id, schema in schemas.items()
    ]
    registry = Registry().with_resources(resources)
    return registry, schemas

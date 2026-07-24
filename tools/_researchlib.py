"""Interne Hilfsfunktionen fuer tools/validate_research.py.

Analog zu tools/_datalib.py, aber fuer die Recherche-/Provenienzebene (research/**).
Nicht Teil der oeffentlichen Tool-Oberflaeche. Importiert bewusst nur generische
Low-Level-Hilfsfunktionen aus _datalib.py (Dateizugriff, Report/Issue-Infrastruktur,
Schema-Registry) -- keine Business-Logik aus validate_data.py, damit beide Validatoren
unabhaengig voneinander bleiben (siehe Scientific Research Protocol).
"""

from __future__ import annotations

from pathlib import Path

from _datalib import REPO_ROOT, Vocabulary, iter_yaml_files, load_yaml_file  # noqa: F401

RESEARCH_DIR = REPO_ROOT / "research"
RESEARCH_VOCAB_DIR = RESEARCH_DIR / "vocabularies"

RESEARCH_KIND_TO_FOLDER = {
    "protocol": "protocols",
    "search_run": "search_runs",
    "screening_record": "screening",
    "extraction_record": "extractions",
}

RESEARCH_KIND_TO_SCHEMA_ID = {
    "protocol": "research_protocol.schema.json",
    "search_run": "research_search_run.schema.json",
    "screening_record": "research_screening_record.schema.json",
    "extraction_record": "research_extraction_record.schema.json",
}

RESEARCH_KIND_TO_ID_PREFIX = {
    "protocol": "research-protocol-",
    "search_run": "search-run-",
    "screening_record": "screening-record-",
    "extraction_record": "extraction-record-",
}

RESEARCH_VOCABULARY_NAMES = [
    "research_databases",
    "research_protocol_statuses",
    "screening_decisions",
    "screening_stages",
    "exclusion_reasons",
    "full_text_statuses",
    "extraction_statuses",
    "review_decisions",
]


def iter_research_files(root: Path, kind: str):
    """Liefert alle YAML-Dateien fuer eine Research-Objektart unter root (research/ oder
    research/examples/ -- beide haben dieselbe Unterordnerstruktur, anders als data/examples/)."""
    folder = RESEARCH_KIND_TO_FOLDER[kind]
    yield from iter_yaml_files(root / folder)


def load_research_vocabulary(name: str) -> Vocabulary:
    path = RESEARCH_VOCAB_DIR / f"{name}.yaml"
    raw = load_yaml_file(path)
    vocab = Vocabulary(name=name)
    for entry in raw.get("values", []):
        value = entry["value"]
        vocab.values.add(value)
        vocab.entries[value] = entry
    return vocab


def load_all_research_vocabularies() -> dict[str, Vocabulary]:
    return {name: load_research_vocabulary(name) for name in RESEARCH_VOCABULARY_NAMES}

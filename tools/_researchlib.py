"""Interne Hilfsfunktionen fuer tools/validate_research.py.

Analog zu tools/_datalib.py, aber fuer die Recherche-/Provenienzebene (research/**).
Nicht Teil der oeffentlichen Tool-Oberflaeche. Importiert bewusst nur generische
Low-Level-Hilfsfunktionen aus _datalib.py (Dateizugriff, Report/Issue-Infrastruktur,
Schema-Registry) -- keine Business-Logik aus validate_data.py, damit beide Validatoren
unabhaengig voneinander bleiben (siehe Scientific Research Protocol).
"""

from __future__ import annotations

import re
from pathlib import Path

from _datalib import (  # noqa: F401
    REPO_ROOT,
    Vocabulary,
    iter_yaml_files,
    load_yaml_file,
    normalize_doi,
    normalize_isbn,
    normalize_pmcid,
    normalize_pmid,
    normalize_url,
)

RESEARCH_DIR = REPO_ROOT / "research"
RESEARCH_VOCAB_DIR = RESEARCH_DIR / "vocabularies"

RESEARCH_KIND_TO_FOLDER = {
    "protocol": "protocols",
    "search_run": "search_runs",
    "screening_record": "screening",
    "extraction_record": "extractions",
    "promotion_record": "promotions",
}

RESEARCH_KIND_TO_SCHEMA_ID = {
    "protocol": "research_protocol.schema.json",
    "search_run": "research_search_run.schema.json",
    "screening_record": "research_screening_record.schema.json",
    "extraction_record": "research_extraction_record.schema.json",
    "promotion_record": "research_promotion_record.schema.json",
}

RESEARCH_KIND_TO_ID_PREFIX = {
    "protocol": "research-protocol-",
    "search_run": "search-run-",
    "screening_record": "screening-record-",
    "extraction_record": "extraction-record-",
    "promotion_record": "promotion-record-",
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
    "search_run_statuses",
    "promotion_statuses",
]

# Kanonische Reihenfolge der Screening-Stufen, fuer Monotonie-Pruefungen in decision_history
# (siehe validate_research.py). Nicht identisch mit der Vokabular-Datei -- dort ist die
# Reihenfolge nicht semantisch (jede Enum-Menge), hier schon.
SCREENING_STAGE_ORDER = ["deduplication", "title_abstract", "full_text", "final"]

# Screening-Entscheidungen, die einen "aktiven" (noch nicht ausgeschiedenen) Kandidaten
# markieren -- fuer die Identifier-Deduplizierungspruefung (siehe validate_research.py).
ACTIVE_SCREENING_DECISIONS = {"include", "pending", "awaiting_full_text", "uncertain"}

# Identifier-Felder in candidate_identifiers, die fuer die Deduplizierung normalisiert werden --
# Reihenfolge irrelevant hier (im Gegensatz zu deduplication_policy.identifier_priority im
# Protokoll, das nur die redaktionelle Prioritaet bei der Studienzuordnung betrifft).
DEDUPLICATION_IDENTIFIER_FIELDS = ("doi", "pmid", "pmcid", "nct_id", "isbn")

# Zentrale, wiederverwendbare Stage-/Decision-Matrix (siehe ADR-0043 im Decision Log): legt fest,
# welche Screening-Entscheidungen an welcher Stufe fachlich sinnvoll sind. Gilt sowohl fuer
# primary_decision als auch fuer die effektive decision jedes decision_history-Eintrags
# (validate_research.py). Bewusst NICHT protokollabhaengig -- diese Zuordnung ist intrinsisch zum
# Stufenbegriff selbst, nicht redaktionell je Vorhaben konfigurierbar.
#
# - deduplication: der allererste Check auf Mehrfachfund. 'pending' (noch nicht geprueft),
#   'include' (kein Duplikat, weiter zu title_abstract), 'duplicate' (Mehrfachfund, terminal fuer
#   diesen Kandidaten), 'uncertain' (Duplikatstatus unklar). 'exclude' gehoert inhaltlich zum
#   Titel-/Abstract-/Volltext-Screening, nicht zur reinen Duplikaterkennung.
# - title_abstract / full_text: inhaltliche Sichtung. 'include'/'exclude' plus
#   'awaiting_full_text' (Volltext noch nicht beschafft) und 'uncertain'. Kein 'pending'
#   (die Stufe wurde ja bereits begonnen) und kein 'duplicate' (das gehoert zu deduplication).
# - final: die einzige terminale, extraktionsfaehige Stufe (siehe Abschnitt 9b) -- nur noch
#   'include'/'exclude'/'uncertain'. Kein 'awaiting_full_text' (das waere kein finaler Zustand
#   mehr) und kein 'pending'/'duplicate'.
ALLOWED_DECISIONS_BY_STAGE = {
    "deduplication": {"pending", "include", "duplicate", "uncertain"},
    "title_abstract": {"include", "exclude", "awaiting_full_text", "uncertain"},
    "full_text": {"include", "exclude", "awaiting_full_text", "uncertain"},
    "final": {"include", "exclude", "uncertain"},
}


def normalize_nct_id(value: str) -> str:
    """Kanonisiert eine ClinicalTrials.gov-NCT-ID fuer die Duplikaterkennung.

    'NCT01234567', 'nct01234567' und 'NCT 01234567' ergeben denselben Wert. Fuehrende
    Nullen innerhalb der Nummer werden -- anders als bei PMID -- NICHT entfernt, da NCT-IDs
    eine feste Ziffernanzahl mit bedeutungstragenden fuehrenden Nullen haben.
    """
    text = re.sub(r"\s+", "", value.strip()).upper()
    if not text.startswith("NCT"):
        text = f"NCT{text}"
    digits = re.sub(r"\D", "", text)
    return f"NCT{digits}"


NORMALIZERS = {
    "doi": normalize_doi,
    "pmid": normalize_pmid,
    "pmcid": normalize_pmcid,
    "nct_id": normalize_nct_id,
    "isbn": normalize_isbn,
    "url": normalize_url,
}


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

"""Interne Hilfsfunktionen fuer tools/validate_research.py.

Analog zu tools/_datalib.py, aber fuer die Recherche-/Provenienzebene (research/**).
Nicht Teil der oeffentlichen Tool-Oberflaeche. Importiert bewusst nur generische
Low-Level-Hilfsfunktionen aus _datalib.py (Dateizugriff, Report/Issue-Infrastruktur,
Schema-Registry) -- keine Business-Logik aus validate_data.py, damit beide Validatoren
unabhaengig voneinander bleiben (siehe Scientific Research Protocol).
"""

from __future__ import annotations

import hashlib
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
    "search_result_manifest": "search_results",
    "candidate_manifest": "candidates",
    "screening_record": "screening",
    "extraction_record": "extractions",
    "promotion_record": "promotions",
    "reviewer": "reviewers",
}

RESEARCH_KIND_TO_SCHEMA_ID = {
    "protocol": "research_protocol.schema.json",
    "search_run": "research_search_run.schema.json",
    "search_result_manifest": "research_search_result_manifest.schema.json",
    "candidate_manifest": "research_candidate_manifest.schema.json",
    "screening_record": "research_screening_record.schema.json",
    "extraction_record": "research_extraction_record.schema.json",
    "promotion_record": "research_promotion_record.schema.json",
    "reviewer": "research_reviewer.schema.json",
}

# reviewer hat bewusst keinen festen Praefix: die id IST das bereits ueberall verwendete
# research_actor_id-Kuerzel selbst (siehe research/reviewers/README.md, ADR-0059) -- keine
# Indirektionsebene wie bei den uuid4-/Praefix-basierten Objektarten unten.
RESEARCH_KIND_TO_ID_PREFIX = {
    "protocol": "research-protocol-",
    "search_run": "search-run-",
    "search_result_manifest": "search-result-manifest-",
    "candidate_manifest": "candidate-manifest-",
    "screening_record": "screening-record-",
    "extraction_record": "extraction-record-",
    "promotion_record": "promotion-record-",
    "reviewer": "",
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
    "search_interface_profiles",
    "candidate_metadata_statuses",
    "screening_revision_reasons",
    "research_candidate_source_types",
    "screening_relationship_types",
    "screening_relationship_evidence_sources",
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
# welche Screening-Entscheidungen an welcher Stufe fachlich sinnvoll sind. Gilt fuer ALLE DREI
# Entscheidungsebenen eines decision_history-Eintrags (validate_research.py, siehe ADR-0046):
# primary_decision, second_review.reviewer_decision UND die effektive decision. Bewusst NICHT
# protokollabhaengig -- diese Zuordnung ist intrinsisch zum Stufenbegriff selbst, nicht redaktionell
# je Vorhaben konfigurierbar.
#
# - deduplication: der allererste Check auf Mehrfachfund. 'pending' (noch nicht geprueft),
#   'include' (kein Duplikat, weiter zu title_abstract), 'duplicate' (Mehrfachfund, terminal fuer
#   diesen Kandidaten), 'uncertain' (Duplikatstatus unklar). 'exclude' gehoert inhaltlich zum
#   Titel-/Abstract-/Volltext-Screening, nicht zur reinen Duplikaterkennung. WICHTIG: diese Stufe
#   unterstuetzt strukturell KEINE Adjudikation (validate_research.py erzwingt das) -- exclude ist
#   hier nie zulaessig und 'duplicate' ist als adjudication.final_decision (auf include/exclude
#   beschraenkt) nicht abbildbar; ein Dedup-Widerspruch bleibt daher immer 'uncertain' und wird durch
#   einen neuen decision_history-Eintrag geloest, nie durch eine dritte Person an derselben Stufe
#   (siehe ADR-0046). screening_policy.dual_reviewer_stages kann 'deduplication' deshalb schon
#   schema-seitig nicht enthalten (common.schema.json#/$defs/dual_reviewable_screening_stage).
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


# Stabiles Kuerzel des technischen Akteurs, der research_screening_record-Datensaetze rein
# administrativ initialisiert (tools/initialize_screening_records.py). Kein wissenschaftlicher
# Reviewer -- dokumentiert nur die technische Initialisierung, trifft nie eine Relevanzentscheidung
# (validate_research.py::check_screening_system_actor_invariants erzwingt das strukturell).
SYSTEM_SCREENING_INITIALIZER_ACTOR = "system-screening-initializer"

# Kuerzel des KI-basierten Chief Scientific Officer des Projekts (keine menschliche Person, siehe
# Decision Log, Phase-4B-0-Eintrag) -- traegt bereits reale Freigabeverantwortung (z. B.
# Retatrutide-Protokollfreigabe). Zusammen mit SYSTEM_SCREENING_INITIALIZER_ACTOR der zweite real
# bekannte, nicht-menschliche Akteur, dessen Registrierung in research/reviewers/** seit ADR-0059
# (Phase 4B-1B-3) verpflichtend ist (siehe validate_research.py::check_research_reviewers).
CSO_CHATGPT_ACTOR = "cso-chatgpt"

# actor_type-Werte, deren Registrierung in research/reviewers/** verpflichtend ist (ADR-0059) --
# fuer 'human' bleibt sie optional (dieselbe organisatorische Grenze wie ADR-0041). 'external_expert'
# und 'editorial_board' sind vom CSO langfristig reserviert, aber noch nicht Teil des Enums (siehe
# common.schema.json#/$defs/research_actor_type) -- deshalb hier ebenfalls noch nicht gelistet.
MANDATORY_REVIEWER_REGISTRATION_ACTOR_TYPES = frozenset({"ai_assistant", "automation", "service"})

# Datenbank -> passendster neutraler Wert aus common.schema.json#/$defs/source_type fuer einen noch
# nicht wissenschaftlich geprueften Discovery-Kandidaten (siehe ADR-0057). Bewusst je Datenbank EIN
# einzelner, uniform angewandter Wert -- keine Ableitung aus PubMed publication_types (z. B. "Review"),
# da eine feinere Zuordnung selbst eine wissenschaftliche Einordnung waere, die der technischen
# Initialisierung nicht zusteht.
CANDIDATE_SOURCE_TYPE_BY_DATABASE = {
    "pubmed": "peer_reviewed_publication",
    "clinicaltrials_gov": "trial_registry",
}

# Screening-Bearbeitungszustand als reine, NICHT gespeicherte Projektion (ADR-0058, Phase 4B-1B-2,
# Nachtrag CSO-Review Runde 1 -- kein Schemafeld, keine zweite Wahrheitsquelle). Ersetzt die
# vormals redundante screened_by-basierte Herleitung in validate_research.py::
# check_screening_system_actor_invariants/check_deduplication (siehe Phase_4B_1B_2_Deduplication_
# and_Workflow_Architecture.md, Abschnitt 1). Drei Werte, ausschliesslich als Rueckgabewerte dieser
# einen Funktion definiert -- kein eigenes kontrolliertes Vokabular, da nichts Gespeichertes
# existiert, das dagegen zu validieren waere.
WORKFLOW_STATE_SYSTEM_INITIALIZED = "system_initialized"
WORKFLOW_STATE_UNDER_HUMAN_REVIEW = "under_human_review"
WORKFLOW_STATE_FINALIZED = "finalized"


def _has_unresolved_review_conflict(screening_data: dict) -> bool:
    """True, wenn second_review.reviewer_decision der terminal massgeblichen primary_decision
    widerspricht und keine Adjudikation vorliegt. Eigenstaendige Kopie der in validate_research.py
    bereits vorhandenen Kernlogik (_screening_conflict_is_unresolved/_terminal_primary_decision) --
    bewusst hier dupliziert statt importiert, damit _researchlib.py frei von einer Abhaengigkeit auf
    validate_research.py bleibt (siehe Moduldokstring oben: nur Low-Level-Hilfsfunktionen, keine
    Business-Logik-Importe in diese Richtung)."""
    second_review = screening_data.get("second_review")
    if not second_review:
        return False
    history = screening_data.get("decision_history") or []
    primary_decision = history[-1].get("primary_decision") if history else screening_data.get("decision")
    if second_review.get("reviewer_decision") == primary_decision:
        return False
    return second_review.get("adjudication") is None


def derive_workflow_state(screening_data: dict) -> str:
    """Berechnet den Bearbeitungszustand eines research_screening_record AUSSCHLIESSLICH aus
    decision_history (massgeblich) sowie den bereits validierten Top-Level-Projektionen decision/
    decision_stage (guenstige Abkuerzung fuer die 'finalized'-Bedingung -- decision/decision_stage
    sind selbst bereits eine vom Validator geprueft Projektion von decision_history[-1], also keine
    zweite Wahrheitsquelle). Kein Speicherort, kein Cache -- wird bei jedem Bedarf neu berechnet
    (ADR-0058, Phase 4B-1B-2).

    - system_initialized: noch nie von einem Menschen bearbeitet (genau ein Eintrag, verantwortet
      vom technischen Akteur SYSTEM_SCREENING_INITIALIZER_ACTOR).
    - finalized: terminal, widerspruchsfrei abgeschlossen (Stufe 'final', decision include/exclude,
      kein ungeloester Erst-/Zweitpruefungs-Widerspruch).
    - under_human_review: alles dazwischen -- mindestens ein Mensch hat uebernommen, Entscheidung
      noch nicht terminal/widerspruchsfrei."""
    history = screening_data.get("decision_history") or []
    if len(history) == 1 and history[0].get("decided_by") == SYSTEM_SCREENING_INITIALIZER_ACTOR:
        return WORKFLOW_STATE_SYSTEM_INITIALIZED
    if (
        screening_data.get("decision_stage") == "final"
        and screening_data.get("decision") in ("include", "exclude")
        and not _has_unresolved_review_conflict(screening_data)
    ):
        return WORKFLOW_STATE_FINALIZED
    return WORKFLOW_STATE_UNDER_HUMAN_REVIEW


# Gerichtete Beziehungstypen-Inversion (ADR-0058, Phase 4B-1B-2, Abschnitt 2.4/6). 9 Konzeptpaare
# (16 gerichtete Werte) plus 'other_related_to' als einzige bewusst selbstinverse Ausnahme -- 17
# Werte insgesamt. Muss inhaltlich mit research/vocabularies/screening_relationship_types.yaml
# (dessen redaktionell gepflegtes `inverse`-Feld je Eintrag) uebereinstimmen; diese hier ist die vom
# Validator tatsaechlich genutzte Quelle (siehe tests/test_relationship_type_inverse_matches_vocabulary).
RELATIONSHIP_TYPE_INVERSE = {
    "replies_to": "has_reply", "has_reply": "replies_to",
    "updates": "updated_by", "updated_by": "updates",
    "is_preprint_of": "has_published_version", "has_published_version": "is_preprint_of",
    "reports_on_registered_study": "has_publication", "has_publication": "reports_on_registered_study",
    "corrects": "corrected_by", "corrected_by": "corrects",
    "retracts": "retracted_by", "retracted_by": "retracts",
    "raises_concern_about": "has_expression_of_concern",
    "has_expression_of_concern": "raises_concern_about",
    "comments_on": "has_editorial_comment", "has_editorial_comment": "comments_on",
    "other_related_to": "other_related_to",
}

# Rein technische, PRIORISIERTE Ableitung von candidate_source_type aus einem PubMed-
# publication_types-Wert (ADR-0058, Phase 4B-1B-2, Abschnitt 4.5) -- NUR fuer PubMed-Publication-
#-Type-Werte, deren Abbildung im CSO-Review als sicher automatisierbar geprueft wurde. Reihenfolge
# ist bedeutsam: der erste passende Eintrag gewinnt (z. B. Meta-Analysis vor Systematic Review bei
# einem doppelt getaggten Artikel -- Vorschlag aus dem Architektur-Entwurf, CSO-Bestaetigung dieser
# konkreten Prioritaet laut Decision Log noch ausstehend, siehe tools/refresh_candidate_source_types.py).
# Bewusst NICHT enthalten: 'Review' -> narrative_review (nur als Ausschlussregel abbildbar, siehe
# Aufrufer), reply_or_response (nie automatisiert, PubMed unterscheidet Letter/Reply strukturell
# nicht), consensus_statement/technical_report/dataset (Automatisierbarkeit technisch unverifiziert).
PUBMED_PUBLICATION_TYPE_TO_SOURCE_TYPE = [
    ("Retraction of Publication", "retraction_notice"),
    ("Published Erratum", "corrigendum_or_erratum"),
    ("Expression of Concern", "expression_of_concern_notice"),
    ("Comment", "letter_or_comment"),
    ("Letter", "letter_or_comment"),
    ("Practice Guideline", "practice_guideline"),
    ("Meta-Analysis", "meta_analysis"),
    ("Systematic Review", "systematic_review"),
    ("Editorial", "editorial"),
    ("Case Reports", "case_report"),
]

# 'Review' -> narrative_review ist bewusst NICHT Teil der Liste oben (anders als die uebrigen
# Eintraege ist es keine direkte 1:1-Tag-Abbildung, sondern nur als AUSSCHLUSSREGEL abbildbar:
# publication_types enthaelt 'Review', aber weder 'Systematic Review' noch 'Meta-Analysis'). Eigene
# Konstante, damit der Aufrufer (tools/refresh_candidate_source_types.py) diesen Sonderfall separat
# und explizit auswerten muss, statt ihn in der linearen Prioritaetsliste zu verstecken.
NARRATIVE_REVIEW_PUBMED_TAG = "Review"
NARRATIVE_REVIEW_EXCLUDED_TAGS = ("Systematic Review", "Meta-Analysis")


def derive_source_type_from_pubmed_publication_types(publication_types: list[str] | None) -> str | None:
    """Rein technische, deterministische Ableitung eines research_candidate_source_type-Werts aus
    den publication_types-Metadaten eines PubMed-Kandidaten (ADR-0058, Abschnitt 4.5). Liefert None,
    wenn keine der geprueft-automatisierbaren Zuordnungen zutrifft (Aufrufer muss das als
    'keine Aenderung vorschlagen' behandeln, NIEMALS als peer_reviewed_publication erzwingen -- das
    bliebe wie bisher der bestehende Default aus ADR-0057, hier nicht ueberschrieben)."""
    types = publication_types or []
    for pubmed_type, source_type in PUBMED_PUBLICATION_TYPE_TO_SOURCE_TYPE:
        if pubmed_type in types:
            return source_type
    if NARRATIVE_REVIEW_PUBMED_TAG in types and not any(t in types for t in NARRATIVE_REVIEW_EXCLUDED_TAGS):
        return "narrative_review"
    return None


def derive_candidate_title(database: str, metadata: dict) -> str | None:
    """Leitet den technischen Kandidatentitel deterministisch aus den Manifest-Metadaten ab, ohne
    jemals einen Titel zu erfinden (siehe Phase-4B-1B-1-Arbeitsauftrag). PubMed: metadata.title.
    ClinicalTrials.gov: metadata.brief_title, ersatzweise metadata.official_title. Liefert None, wenn
    kein zulaessiger Titel vorhanden ist (Aufrufer muss das als Datenfehler behandeln, nicht mit
    einem Platzhalter kaschieren)."""
    if database == "pubmed":
        title = (metadata or {}).get("title")
        return title if title else None
    if database == "clinicaltrials_gov":
        title = (metadata or {}).get("brief_title") or (metadata or {}).get("official_title")
        return title if title else None
    return None


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


def compute_manifest_sha256(identifiers: list[str]) -> str:
    """Verbindliche Hash-Regel fuer research_search_result_manifest.sha256 (siehe ADR-0055):
    SHA-256 ueber ("\\n".join(identifiers) + "\\n").encode("utf-8"). `identifiers` muss bereits
    in der im Manifest gespeicherten (kanonisch sortierten) Reihenfolge uebergeben werden -- diese
    Funktion sortiert selbst NICHT, damit ein Manifest mit falscher Reihenfolge auch einen
    abweichenden Hash erzeugt (siehe check_search_result_manifests in validate_research.py)."""
    payload = ("\n".join(identifiers) + "\n").encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


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

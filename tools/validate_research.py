#!/usr/bin/env python3
"""Validiert die Recherche-/Provenienzebene von Peptide Atlas (research/**).

Laeuft GETRENNT vom kanonischen Datenvalidator (tools/validate_data.py) -- research/**
ist Provenienz- und Arbeitsebene, kein kanonisches Wissen (siehe ADR-0033 im Decision Log)
und fliesst nicht in build/catalog.json oder build/graph.json ein. Dieser Validator prueft
aber Querverweise auf die kanonische Datenebene, wo Research-Datensaetze `canonical_source_id`,
`canonical_study_id` oder `canonical_claim_id` gesetzt haben.

Prueft (Ueberblick, siehe die einzelnen check_*-Funktionen fuer Details):

- Schemaebene: gueltiges YAML, JSON-Schema-Konformitaet, echte Kalenderdaten, schema_version,
  Dateiname == id.
- Referenzebene: protocol_id, search_run_ids, duplicate_of, canonical_source_id/_study_id/
  _claim_id gegen die jeweilige kanonische Datenebene. Seit ADR-0052 zusaetzlich referenziell
  geprueft (Ziel existiert, gleiches protocol_id, kein Selbstverweis, je EXAKTEM Feldpfad):
  decision_history[].primary_duplicate_of, decision_history[].second_review.reviewer_duplicate_of,
  decision_history[].duplicate_of -- bewusst nur ein einzelner Hop je historischer Momentaufnahme,
  keine Kettenverfolgung (die bleibt der EFFEKTIVEN Top-Level-duplicate_of vorbehalten, siehe unten).
- Protokollkonsistenz: Version/ID-Suffix, Suchlauf nur gegen approved/superseded-Protokolle,
  Suchlauf-Datenbank muss in protocol.planned_information_sources[] freigegeben sein,
  protokoll-uebergreifende Konsistenz zwischen search_run/screening_record/extraction_record,
  duplicate_of bleibt innerhalb desselben Protokolls (inkl. gesamter Kette und Zyklenerkennung --
  ausschliesslich fuer die effektive Top-Level-duplicate_of, siehe ADR-0052).
- Deduplizierung: echte normalisierte DOI/PMID/PMCID/NCT-ID/ISBN-Kollisionserkennung.
- Screening-Workflow: JEDER decision_history-Eintrag (nicht nur der aktuelle Zustand) wird
  gegen dieselben Invarianten geprueft -- Stufe im Protokoll vorgesehen, Stage-/Decision-Matrix
  (ADR-0043) gegen ALLE DREI Entscheidungsebenen (primary_decision, second_review.reviewer_decision,
  effektive decision -- ADR-0046), Dual-Reviewer-Pflicht, Reviewer-/Adjudikator-Unabhaengigkeit,
  konsistente primary_decision/reviewer_decision/decision_confirmed/adjudication-Semantik (ADR-0043),
  vollstaendige, verlustfreie Drei-Ebenen-Entscheidungsprovenienz inkl. eigenstaendiger Gruende/
  Duplikatverweise je Ebene (primary_decision_reason/primary_duplicate_of,
  second_review.reviewer_decision_reason/reviewer_duplicate_of -- ADR-0046), Volltextvollstaendigkeit,
  Datumsreihenfolge (inkl. gegen JEDEN referenzierten Suchlauf). deduplication unterstuetzt
  strukturell KEINE Adjudikation (ADR-0046) -- ein Dedup-Widerspruch bleibt immer 'uncertain'.
  decision_confirmed bei reviewer_decision == primary_decision == 'duplicate' erfordert seit
  ADR-0052 zusaetzlich reviewer_duplicate_of == primary_duplicate_of -- zwei Pruefungen, die beide
  'duplicate' waehlen, aber unterschiedliche Hauptdatensaetze meinen, sind KEINE bestaetigte
  Uebereinstimmung. Seit ADR-0053 ist die EFFEKTIVE duplicate_of zusaetzlich deterministisch an das
  bestaetigte Ziel gebunden: ohne Zweitpruefung muss duplicate_of == primary_duplicate_of gelten; bei
  bestaetigtem Konsens muessen primary_duplicate_of, reviewer_duplicate_of UND die effektive
  duplicate_of identisch sein -- ein davon abweichender, sonst gueltiger dritter Hauptdatensatz ist
  ein Fehler.
  Extraktion ist nur fuer einen screening_record zulaessig, dessen Einschluss terminal
  (decision_stage: final), vollstaendig volltextgeprueft und frei von ungeloesten
  Zweitpruefungskonflikten ist.
- Extraktionsverifikation: verified_by != extracted_by wird IMMER erzwungen, sobald
  extraction_status: verified (siehe ADR-0040) -- keine protokollabhaengige Ausnahme mehr.
- Zeitliche Provenienzkette (ADR-0044): terminale Screening-Entscheidung/-Zweitpruefung/
  -Adjudikation <= extracted_at <= verified_at <= promotion.created_at/review.last_reviewed_at
  <= promotion.updated_at. Zusaetzlich OBJEKTINTERN (ADR-0046): jedes von einem Research-Objekt
  selbst dokumentierte Ereignisdatum liegt innerhalb von dessen eigenem [created_at, updated_at].
- Claim-Promotion: vollstaendige Kettenpruefung inkl. claim_promotion_policy.requires_second_review
  (mindestens zwei unterschiedliche, nicht-leere Reviewer bei approved_for_creation/promoted/
  rejected -- symmetrisch fuer jede endgueltige Entscheidung, ADR-0046; Eindeutigkeit/Nicht-Leerheit
  selbst ist schema-seitig erzwungen, siehe research_promotion_record.schema.json). rejected
  erfordert zusaetzlich dieselbe Mindest-Audit-Spur (Reviewdatum, Reviewer, Begruendung) wie
  approved_for_creation/promoted (schema-seitig erzwungen, ADR-0046).
- Protokollkonsistenz (ADR-0046): screening_policy.dual_reviewer_stages muss eine Teilmenge von
  screening_policy.stages sein; 'deduplication' ist dort bereits schema-seitig ausgeschlossen.
- Stabile Akteurskuerzel (ADR-0046): alle Research-Actor-Felder (screened_by, decided_by,
  second_review.reviewed_by, adjudication.resolved_by, extracted_by, verified_by,
  promotion.review.reviewers[], protocol.review.reviewers[]) folgen einem restriktiven,
  leerzeichen-/grossschreibungsfreien Muster (schema-seitig erzwungen) -- stellt nur syntaktisch
  stabile, unterscheidbare Kuerzel sicher, beweist NICHT, dass zwei Kuerzel zwei unterschiedliche
  MENSCHLICHE Personen sind (organisatorisch kontrolliert, siehe ADR-0041/ADR-0046).
- Sonstige Konsistenz: Eindeutigkeit, Datumsreihenfolge, sichere export_reference.
- Dateiebene: keine unerwuenschten Binaerdateien, research/examples/** als eigener Namensraum.
- Screening-Initialisierung (ADR-0057, Phase 4B-1B-1): der rein technische Akteur
  'system-screening-initializer' (tools/initialize_screening_records.py) darf in JEDEM
  decision_history-Eintrag, den er verantwortet, nur 'pending'/'deduplication'/'not_yet_obtained'
  ohne Duplikatverweis/Zweitpruefung dokumentieren -- nie eine wissenschaftliche Entscheidung.
  Solange er der aktuelle effektive Bearbeiter ist, muss canonical_source_id null bleiben und
  candidate_title (bei aufgeloester Kandidatenreferenz) exakt der aus den Candidate-Manifest-
  Metadaten abgeleitete Titel sein. Jeder Discovery-Kandidat darf hoechstens einen Screening Record
  haben (candidate_manifest_id+candidate_id eindeutig). Bei aufgeloester Kandidatenreferenz muss
  search_run_ids exakt (nicht nur teilweise) den discovered_in_search_run_ids des Kandidaten
  entsprechen. Die Vollstaendigkeitsregel "jeder Candidate eines Protokolls braucht einen Screening
  Record" greift ausschliesslich fuer Protokolle, die im rein technischen Kontrollartefakt
  research/screening_status/initialization_manifest.yaml ausdruecklich als status: complete markiert
  sind (kein RESEARCH_KINDS-Eintrag, kein wissenschaftliches Objekt) -- ein teilweise laufender
  Import macht die CI dadurch nicht zwischenzeitlich rot.

Exitcode 0 bei Erfolg (nur WARNINGs erlaubt), Exitcode 1 bei mindestens einem ERROR. Keine
Netzwerkzugriffe.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _datalib import (  # noqa: E402
    DATA_DIR,
    DataFileError,
    Report,
    build_schema_registry,
    iter_claim_files,
    iter_entity_files,
    iter_source_files,
    load_yaml_file,
    relative,
    validate_against_schema,
)
from _researchlib import (  # noqa: E402
    ACTIVE_SCREENING_DECISIONS,
    ALLOWED_DECISIONS_BY_STAGE,
    CSO_CHATGPT_ACTOR,
    DEDUPLICATION_IDENTIFIER_FIELDS,
    MANDATORY_REVIEWER_REGISTRATION_ACTOR_TYPES,
    NORMALIZERS,
    RELATIONSHIP_TYPE_INVERSE,
    RESEARCH_DIR,
    RESEARCH_KIND_TO_SCHEMA_ID,
    SCREENING_STAGE_ORDER,
    SYSTEM_SCREENING_INITIALIZER_ACTOR,
    WORKFLOW_STATE_SYSTEM_INITIALIZED,
    compute_manifest_sha256,
    derive_candidate_title,
    derive_workflow_state,
    iter_research_files,
    load_all_research_vocabularies,
    normalize_url,
)

SCREENING_INITIALIZATION_MANIFEST_RELATIVE_PATH = Path("screening_status") / "initialization_manifest.yaml"

UNWANTED_BINARY_SUFFIXES = {
    ".exe", ".dll", ".so", ".bin", ".zip", ".7z", ".tar", ".gz",
    ".png", ".jpg", ".jpeg", ".gif", ".pdf", ".doc", ".docx", ".xls", ".xlsx",
    ".ris", ".bib", ".csv",
}

RESEARCH_KINDS = (
    "protocol", "search_run", "search_result_manifest", "candidate_manifest", "screening_record",
    "extraction_record", "promotion_record", "reviewer",
)

DATABASE_TO_IDENTIFIER_TYPE = {
    "pubmed": "pmid",
    "clinicaltrials_gov": "nct_id",
}

ALLOWED_SEARCH_RUN_PROTOCOL_STATUSES = {"approved", "superseded"}

TERMINAL_SCREENING_STAGE = "final"
FULL_TEXT_REQUIRING_STAGES = {"full_text", "final"}


@dataclass
class ResearchObject:
    id: str
    kind: str
    path: Path
    data: dict


def load_research_dataset(
    root: Path, report: Report, registry, schemas, vocabularies
) -> dict[str, dict[str, ResearchObject]]:
    """Laedt und schema-validiert ein Research-Datenset (production oder examples)."""
    objects: dict[str, dict[str, ResearchObject]] = {kind: {} for kind in RESEARCH_KINDS}
    seen_ids: dict[str, str] = {}

    def register(obj: ResearchObject, file_rel: str) -> None:
        if obj.id in seen_ids:
            report.error(file_rel, "$.id", f"duplicate id '{obj.id}', already used in {seen_ids[obj.id]}")
        else:
            seen_ids[obj.id] = file_rel

    for kind in RESEARCH_KINDS:
        schema_id = RESEARCH_KIND_TO_SCHEMA_ID[kind]
        for path in iter_research_files(root, kind):
            file_rel = relative(path)
            try:
                data = load_yaml_file(path)
            except DataFileError as exc:
                report.error(file_rel, "", str(exc))
                continue
            if not data:
                if "examples" not in path.parts:
                    report.error(file_rel, "", "empty placeholder file is not allowed outside research/examples/")
                continue
            if not isinstance(data, dict):
                report.error(file_rel, "", "top-level YAML content must be a mapping")
                continue

            stem = path.stem
            obj_id = data.get("id")
            if obj_id != stem:
                report.error(file_rel, "$.id", f"id '{obj_id}' does not match filename '{stem}'")

            validate_against_schema(report, file_rel, data, schema_id, registry, schemas)

            obj = ResearchObject(id=obj_id or stem, kind=kind, path=path, data=data)
            register(obj, file_rel)
            objects[kind][obj.id] = obj

    return objects


def load_canonical_reference_sets(data_root: Path) -> tuple[set[str], set[str], set[str]]:
    """Laedt nur die IDs aus data/sources/**, data/entities/studies/** und data/claims/**, fuer
    Querverweispruefungen. Validiert diese Objekte NICHT selbst -- das ist Aufgabe von
    tools/validate_data.py."""
    source_ids: set[str] = set()
    for path in iter_source_files(data_root):
        try:
            data = load_yaml_file(path)
        except DataFileError:
            continue
        if isinstance(data, dict) and data.get("id"):
            source_ids.add(data["id"])

    study_ids: set[str] = set()
    for path, entity_type in iter_entity_files(data_root):
        if entity_type != "study":
            continue
        try:
            data = load_yaml_file(path)
        except DataFileError:
            continue
        if isinstance(data, dict) and data.get("id"):
            study_ids.add(data["id"])

    claim_ids: set[str] = set()
    for path in iter_claim_files(data_root):
        try:
            data = load_yaml_file(path)
        except DataFileError:
            continue
        if isinstance(data, dict) and data.get("id"):
            claim_ids.add(data["id"])

    return source_ids, study_ids, claim_ids


def _screening_conflict_is_unresolved(second_review: dict | None, primary_decision: str) -> bool:
    """True, wenn eine Zweitpruefung der PRIMARY-Entscheidung widerspricht (reviewer_decision !=
    primary_decision) UND keine Adjudikation vorliegt. Vergleicht bewusst gegen primary_decision,
    NICHT gegen die effektive decision (das war die in Runde 4 behobene Modellierungsluecke, siehe
    ADR-0043) -- ein Vergleich gegen die effektive decision wuerde einen bereits geloesten
    Widerspruch nie als aufgeloest erkennen koennen, wenn adjudication.final_decision zufaellig
    dem reviewer_decision entspricht."""
    if not second_review:
        return False
    if second_review.get("reviewer_decision") == primary_decision:
        return False
    return second_review.get("adjudication") is None


def _terminal_primary_decision(screening_data: dict) -> str | None:
    history = screening_data.get("decision_history") or []
    if history:
        return history[-1].get("primary_decision")
    return screening_data.get("decision")


def _screening_is_extraction_eligible(screening_obj: ResearchObject, protocol: ResearchObject | None) -> tuple[bool, str]:
    """Eine Extraktion ist nur fuer einen Screening-Datensatz zulaessig, dessen Einschluss
    TERMINAL und vollstaendig gueltig ist (siehe Scientific Research Protocol, Abschnitt 9b):
    decision_stage: final (die einzige extraktionsfaehige Stufe -- full_text dokumentiert nur
    die Volltextbewertung), decision: include, full_text_status: obtained, eine fuer diese
    Stufe konfigurierte Zweitpruefung liegt vor, und es gibt keinen ungeloesten Widerspruch
    zwischen Erst- und Zweitentscheidung."""
    data = screening_obj.data
    if data.get("decision") != "include":
        return False, f"decision is '{data.get('decision')}', not 'include'"
    if data.get("decision_stage") != TERMINAL_SCREENING_STAGE:
        return False, (
            f"decision_stage is '{data.get('decision_stage')}', not the terminal stage "
            f"'{TERMINAL_SCREENING_STAGE}' -- only a final, fully confirmed inclusion is extraction-eligible"
        )
    if data.get("full_text_status") != "obtained":
        return False, f"full_text_status is '{data.get('full_text_status')}', not 'obtained'"

    dual_reviewer_stages: set = set()
    if protocol is not None:
        dual_reviewer_stages = set((protocol.data.get("screening_policy") or {}).get("dual_reviewer_stages") or [])
    second_review = data.get("second_review")
    if TERMINAL_SCREENING_STAGE in dual_reviewer_stages and second_review is None:
        return False, (
            f"stage '{TERMINAL_SCREENING_STAGE}' is a dual-reviewer stage for this protocol, but no "
            "second_review is recorded"
        )
    primary_decision = _terminal_primary_decision(data)
    if _screening_conflict_is_unresolved(second_review, primary_decision):
        return False, (
            "second_review disagrees with the primary decision and the conflict is not resolved via a "
            "valid adjudication"
        )
    return True, ""


def check_research_references(
    report: Report,
    objects: dict[str, dict[str, ResearchObject]],
    source_ids: set[str],
    study_ids: set[str],
) -> None:
    protocols = objects["protocol"]
    search_runs = objects["search_run"]
    screening = objects["screening_record"]
    extractions = objects["extraction_record"]

    for kind in ("search_run", "candidate_manifest", "screening_record", "extraction_record"):
        for obj in objects[kind].values():
            file_rel = relative(obj.path)
            protocol_id = obj.data.get("protocol_id")
            if protocol_id and protocol_id not in protocols:
                report.error(file_rel, "$.protocol_id", f"references missing protocol: {protocol_id}")

    for obj in search_runs.values():
        file_rel = relative(obj.path)
        protocol = protocols.get(obj.data.get("protocol_id"))
        if protocol is not None:
            status = protocol.data.get("status")
            if status not in ALLOWED_SEARCH_RUN_PROTOCOL_STATUSES:
                report.error(
                    file_rel, "$.protocol_id",
                    f"search run references protocol '{protocol.id}' with status '{status}' -- a search run "
                    f"may only be executed against a protocol whose status is one of "
                    f"{sorted(ALLOWED_SEARCH_RUN_PROTOCOL_STATUSES)} at validation time",
                )
            planned_databases = {
                src.get("database") for src in protocol.data.get("planned_information_sources") or []
            }
            database = obj.data.get("database")
            if database not in planned_databases:
                report.error(
                    file_rel, "$.database",
                    f"database '{database}' is not among protocol '{protocol.id}'’s "
                    "planned_information_sources -- a search against a new database requires a protocol "
                    "version that plans it before the search is executed",
                )

    for obj in screening.values():
        file_rel = relative(obj.path)
        data = obj.data

        for search_run_id in data.get("search_run_ids") or []:
            search_run = search_runs.get(search_run_id)
            if search_run is None:
                report.error(file_rel, "$.search_run_ids", f"references missing search run: {search_run_id}")
            elif search_run.data.get("protocol_id") != data.get("protocol_id"):
                report.error(
                    file_rel, "$.search_run_ids",
                    f"search run '{search_run_id}' belongs to protocol '{search_run.data.get('protocol_id')}', "
                    f"not this screening record's protocol '{data.get('protocol_id')}' -- a screening record "
                    "must not mix search runs from different protocol versions",
                )

        duplicate_of = data.get("duplicate_of")
        if duplicate_of:
            if duplicate_of == obj.id:
                report.error(file_rel, "$.duplicate_of", "screening record cannot mark itself as duplicate_of")
            elif duplicate_of not in screening:
                report.error(file_rel, "$.duplicate_of", f"references missing screening record: {duplicate_of}")
            else:
                target = screening[duplicate_of]
                if target.data.get("protocol_id") != data.get("protocol_id"):
                    report.error(
                        file_rel, "$.duplicate_of",
                        f"duplicate_of target '{duplicate_of}' belongs to a different protocol "
                        f"('{target.data.get('protocol_id')}') than this record ('{data.get('protocol_id')}') "
                        "-- a duplicate must stay within the same protocol",
                    )

        canonical_source_id = data.get("canonical_source_id")
        if canonical_source_id and canonical_source_id not in source_ids:
            report.error(
                file_rel, "$.canonical_source_id",
                f"references a canonical source that does not exist under data/sources/**: {canonical_source_id}",
            )

    # Zyklenerkennung und protokoll-uebergreifende Kettenpruefung bei duplicate_of: laeuft die
    # GESAMTE Kette ab, nicht nur den unmittelbaren Verweis (siehe Schleife oben), und prueft
    # jeden Zwischenschritt gegen die protocol_id des Ausgangsdatensatzes.
    for obj_id, obj in screening.items():
        origin_protocol_id = obj.data.get("protocol_id")
        path_seen = {obj_id}
        current = obj.data.get("duplicate_of")
        steps = 0
        while current is not None and current in screening and steps <= len(screening) + 1:
            if current in path_seen:
                chain = " -> ".join([*path_seen, current])
                report.error(
                    relative(obj.path), "$.duplicate_of",
                    f"cyclical duplicate_of chain detected: {chain}",
                )
                break
            target = screening[current]
            if target.data.get("protocol_id") != origin_protocol_id and current != obj.data.get("duplicate_of"):
                # Der unmittelbare Verweis wurde bereits oben gemeldet; hier zusaetzliche Hops
                # der Kette, die erst weiter hinten das Protokoll wechseln.
                report.error(
                    relative(obj.path), "$.duplicate_of",
                    f"duplicate_of chain from '{obj_id}' reaches screening record '{current}' which belongs "
                    f"to a different protocol ('{target.data.get('protocol_id')}') than the origin "
                    f"('{origin_protocol_id}') -- the entire chain must stay within the same protocol",
                )
            path_seen.add(current)
            current = target.data.get("duplicate_of")
            steps += 1

    for obj in extractions.values():
        file_rel = relative(obj.path)
        data = obj.data

        screening_id = data.get("screening_record_id")
        screening_obj = screening.get(screening_id)
        if screening_id and screening_obj is None:
            report.error(file_rel, "$.screening_record_id", f"references missing screening record: {screening_id}")
        elif screening_obj is not None:
            protocol = protocols.get(screening_obj.data.get("protocol_id"))
            eligible, reason = _screening_is_extraction_eligible(screening_obj, protocol)
            if not eligible:
                report.error(
                    file_rel, "$.screening_record_id",
                    f"extraction record created for screening record '{screening_id}' which is not "
                    f"extraction-eligible: {reason}",
                )
            if data.get("protocol_id") != screening_obj.data.get("protocol_id"):
                report.error(
                    file_rel, "$.protocol_id",
                    f"protocol_id does not match the referenced screening record's protocol_id "
                    f"('{screening_obj.data.get('protocol_id')}')",
                )
            extraction_source = data.get("canonical_source_id")
            screening_source = screening_obj.data.get("canonical_source_id")
            if extraction_source and screening_source and extraction_source != screening_source:
                report.error(
                    file_rel, "$.canonical_source_id",
                    f"conflicts with canonical_source_id '{screening_source}' already recorded on screening "
                    f"record '{screening_id}'",
                )

        canonical_source_id = data.get("canonical_source_id")
        if canonical_source_id and canonical_source_id not in source_ids:
            report.error(
                file_rel, "$.canonical_source_id",
                f"references a canonical source that does not exist under data/sources/**: {canonical_source_id}",
            )

        canonical_study_id = data.get("canonical_study_id")
        if canonical_study_id and canonical_study_id not in study_ids:
            report.error(
                file_rel, "$.canonical_study_id",
                f"references a canonical study that does not exist under data/entities/studies/**: {canonical_study_id}",
            )


def _check_duplicate_target_reference(
    report: Report,
    file_rel: str,
    path: str,
    field_label: str,
    own_id: str,
    own_protocol_id: str | None,
    target_id: str | None,
    screening: dict[str, ResearchObject],
) -> None:
    """Prueft EINEN Duplikatverweis (egal auf welcher Entscheidungsebene/an welchem JSON-Pfad)
    referenziell: Ziel existiert als screening_record, Ziel gehoert zum selben protocol_id, Ziel ist
    nicht der eigene Datensatz (siehe ADR-0052). Bewusst NUR ein einzelner Hop -- anders als die
    bestehende Ketten-/Zyklenpruefung fuer die EFFEKTIVE Top-Level-duplicate_of (siehe
    check_research_references) laeuft hier keine Kettenverfolgung: primary_duplicate_of/
    reviewer_duplicate_of/decision_history[].duplicate_of sind historische Momentaufnahmen, keine
    fortlaufend gepflegte Verweiskette (siehe Scientific Research Protocol, Abschnitt 8/9c)."""
    if not target_id:
        return
    if target_id == own_id:
        report.error(file_rel, path, f"{field_label} cannot reference the record's own id (self-reference)")
        return
    target = screening.get(target_id)
    if target is None:
        report.error(file_rel, path, f"{field_label} references missing screening record: {target_id}")
        return
    target_protocol_id = target.data.get("protocol_id")
    if target_protocol_id != own_protocol_id:
        report.error(
            file_rel, path,
            f"{field_label} target '{target_id}' belongs to a different protocol ('{target_protocol_id}') "
            f"than this record ('{own_protocol_id}') -- a duplicate target must stay within the same protocol",
        )


def check_historical_duplicate_targets(report: Report, objects: dict[str, dict[str, ResearchObject]]) -> None:
    """ADR-0052: referenzielle Pruefung der historischen Duplikatverweise -- primary_duplicate_of und
    second_review.reviewer_duplicate_of je decision_history-Eintrag, sowie (zusaetzlich zur bereits
    bestehenden Pruefung der Top-Level-Projektion in check_research_references) der EFFEKTIVE
    decision_history[].duplicate_of je Eintrag selbst. Ergaenzt, ersetzt aber nicht die bestehende
    Ketten-/Zyklenpruefung fuer die effektive Top-Level-duplicate_of."""
    screening = objects["screening_record"]
    for obj in screening.values():
        file_rel = relative(obj.path)
        own_protocol_id = obj.data.get("protocol_id")
        for idx, entry in enumerate(obj.data.get("decision_history") or []):
            if not isinstance(entry, dict):
                continue
            entry_label = f"$.decision_history[{idx}]"
            _check_duplicate_target_reference(
                report, file_rel, f"{entry_label}.primary_duplicate_of", "primary_duplicate_of",
                obj.id, own_protocol_id, entry.get("primary_duplicate_of"), screening,
            )
            _check_duplicate_target_reference(
                report, file_rel, f"{entry_label}.duplicate_of", "duplicate_of",
                obj.id, own_protocol_id, entry.get("duplicate_of"), screening,
            )
            second_review = entry.get("second_review") or {}
            _check_duplicate_target_reference(
                report, file_rel, f"{entry_label}.second_review.reviewer_duplicate_of", "reviewer_duplicate_of",
                obj.id, own_protocol_id, second_review.get("reviewer_duplicate_of"), screening,
            )


_PROTOCOL_ID_VERSION_RE = re.compile(r"-v(\d+)$")


def check_protocol_version_matches_id(report: Report, protocols: dict[str, ResearchObject]) -> None:
    for obj in protocols.values():
        match = _PROTOCOL_ID_VERSION_RE.search(obj.id)
        if not match:
            continue  # id-Muster ist bereits schema-seitig erzwungen, sollte hier nie eintreten
        id_version = int(match.group(1))
        declared_version = obj.data.get("version")
        if declared_version != id_version:
            report.error(
                relative(obj.path), "$.version",
                f"version {declared_version!r} does not match the -v{id_version} suffix of id '{obj.id}'",
            )


def _candidate_to_screening_record_index(records: list[ResearchObject]) -> dict[tuple[str, str], str]:
    """Baut einen Index (candidate_manifest_id, candidate_id) -> screening_record.id fuer alle
    Records mit aufgeloester Kandidatenreferenz. Grundlage sowohl fuer check_screening_related_records
    (Zielaufloesung) als auch fuer die Kollisionsgruppen-Konnektivitaetspruefung in check_deduplication
    (ADR-0058, Phase 4B-1B-2)."""
    index: dict[tuple[str, str], str] = {}
    for obj in records:
        candidate_manifest_id = obj.data.get("candidate_manifest_id")
        candidate_id = obj.data.get("candidate_id")
        if candidate_manifest_id and candidate_id:
            index[(candidate_manifest_id, candidate_id)] = obj.id
    return index


def _validated_inverse_relationship_target(
    obj: ResearchObject,
    rel: dict,
    candidate_index: dict[tuple[str, str], str],
    screening_by_id: dict[str, ResearchObject],
) -> str | None:
    """Liefert die screening_record.id des Ziel-Kandidaten NUR, wenn die gerichtete
    related_records-Beziehung VOLLSTAENDIG validiert ist: Ziel-Kandidat aufgeloest, Ziel-Screening-
    Record existiert bereits, UND dessen eigenes related_records[] traegt einen Gegeneintrag auf
    `obj` mit dem korrekten inversen relationship_type (RELATIONSHIP_TYPE_INVERSE). Liefert sonst
    None -- eine einseitige oder falsch-inverse Beziehung zaehlt NICHT als validiert (CSO-Review
    Runde 3, ADR-0058): weder als Kollisionskante nutzbar (siehe _collision_group_components) noch
    als 'bereits dokumentierte Gegenrichtung' (siehe check_screening_related_records). Zentrale,
    einmalige Implementierung dieser Regel -- beide Aufrufer teilen sich dieselbe Logik, um
    divergierendes Verhalten strukturell auszuschliessen."""
    target_key = (rel.get("related_candidate_manifest_id"), rel.get("related_candidate_id"))
    target_id = candidate_index.get(target_key)
    if target_id is None:
        return None
    target_obj = screening_by_id.get(target_id)
    if target_obj is None:
        return None
    expected_inverse = RELATIONSHIP_TYPE_INVERSE.get(rel.get("relationship_type"))
    back_reference = next(
        (
            r for r in (target_obj.data.get("related_records") or [])
            if r.get("related_candidate_manifest_id") == obj.data.get("candidate_manifest_id")
            and r.get("related_candidate_id") == obj.data.get("candidate_id")
        ),
        None,
    )
    if back_reference is None or back_reference.get("relationship_type") != expected_inverse:
        return None
    return target_id


def _collision_group_components(
    group: list[ResearchObject],
    candidate_index: dict[tuple[str, str], str],
    screening_by_id: dict[str, ResearchObject],
) -> list[set[str]]:
    """Union-Find ueber eine Identifikator-Kollisionsgruppe (ADR-0058, Phase 4B-1B-2, Abschnitt 2.5,
    verschaerft in CSO-Review Runde 3): Kanten aus duplicate_of UND VOLLSTAENDIG VALIDIERTEN
    related_records-Beziehungen (siehe _validated_inverse_relationship_target -- eine einseitige oder
    falsch-inverse Beziehung verbindet die Kollisionsgruppe NICHT) zwischen zwei Mitgliedern DERSELBEN
    Gruppe. Liefert die Zusammenhangskomponenten als Liste von ID-Mengen -- die Gruppe gilt als
    vollstaendig erklaert, wenn genau eine Komponente alle Mitglieder umfasst."""
    ids_in_group = {o.id for o in group}
    parent = {o.id: o.id for o in group}

    def find(x: str) -> str:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: str, b: str) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    for obj in group:
        duplicate_of = obj.data.get("duplicate_of")
        if duplicate_of in ids_in_group:
            union(obj.id, duplicate_of)
        for rel in obj.data.get("related_records") or []:
            target_id = _validated_inverse_relationship_target(obj, rel, candidate_index, screening_by_id)
            if target_id in ids_in_group:
                union(obj.id, target_id)

    components: dict[str, set[str]] = {}
    for obj in group:
        components.setdefault(find(obj.id), set()).add(obj.id)
    return list(components.values())


def check_deduplication(report: Report, objects: dict[str, dict[str, ResearchObject]]) -> None:
    """Erkennt Kandidaten mit identischem normalisiertem stabilem Identifikator innerhalb
    desselben Protokolls, die nicht vollstaendig als zusammengehoerig erklaert sind. Kollisionen
    ueber verschiedene Protokolle hinweg sind erlaubt (dieselbe Publikation kann in mehreren
    Reviews vorkommen). URL-Kollisionen sind nur eine Warnung (Redirects/Mirrors, siehe
    tools/_datalib.py::normalize_url).

    ADR-0058 (Phase 4B-1B-2, Abschnitt 2.5, ersetzt die vormals rein paarweise ADR-0057-Logik):
    eine Identifikator-Kollisionsgruppe (alle Mitglieder, nicht nur die aktuell 'aktiven') gilt erst
    dann als vollstaendig erklaert, wenn sie -- ueber Kanten aus duplicate_of (bibliographische
    Dubletten) UND related_records (eigenstaendige, aber verwandte Publikationen, ADR-0058) -- eine
    EINZIGE Zusammenhangskomponente bildet (Union-Find, siehe _collision_group_components). Das
    erkennt transitive Erklaerung korrekt: braucht eine Dreiergruppe nur 2 Kanten (statt aller 3
    Paare), um vollstaendig verbunden zu sein. Ausgeloest wird die Pruefung weiterhin nur, wenn
    mindestens zwei ACTIVE_SCREENING_DECISIONS-Mitglieder vorhanden sind (ein bereits terminal
    ausgeschiedener/dubletten-markierter Kandidat allein loest keine neue Pruefung aus) -- die
    Konnektivitaetspruefung selbst laeuft dann aber ueber die GESAMTE Gruppe, da duplicate_of-Kanten
    naturgemaess auf ein bereits als duplicate markiertes (also nicht mehr 'aktives') Mitglied zeigen.
    Eine nicht vollstaendig verbundene Gruppe bleibt WARNUNG, solange mindestens ein Mitglied der
    GESAMTEN Gruppe workflow_state 'system_initialized' hat (_researchlib.derive_workflow_state,
    ADR-0058 Abschnitt 1) -- menschliche Dedup-Pruefung steht noch aus -- und wird ERROR, sobald kein
    Mitglied mehr system_initialized ist. Diese Herabstufung gilt gleichermassen fuer jedes Feld aus
    DEDUPLICATION_IDENTIFIER_FIELDS, nicht nur DOI, da die zugrunde liegende Unsicherheit (echtes
    Duplikat vs. z. B. ein Correspondence-Letter+Reply-Paar mit gemeinsamer DOI) identisch ist."""
    screening = objects["screening_record"]
    by_protocol: dict[str, list[ResearchObject]] = {}
    for obj in screening.values():
        by_protocol.setdefault(obj.data.get("protocol_id"), []).append(obj)

    for records in by_protocol.values():
        identifier_map: dict[tuple[str, str], list[ResearchObject]] = {}
        url_map: dict[str, list[ResearchObject]] = {}
        for obj in records:
            identifiers = obj.data.get("candidate_identifiers") or {}
            for field in DEDUPLICATION_IDENTIFIER_FIELDS:
                value = identifiers.get(field)
                if not value:
                    continue
                normalized = NORMALIZERS[field](value)
                identifier_map.setdefault((field, normalized), []).append(obj)
            url = identifiers.get("url")
            if url:
                url_map.setdefault(normalize_url(url), []).append(obj)

        candidate_index = _candidate_to_screening_record_index(records)
        screening_by_id = {o.id: o for o in records}

        for (field, normalized), group in identifier_map.items():
            active = [o for o in group if o.data.get("decision") in ACTIVE_SCREENING_DECISIONS]
            if len(active) < 2:
                continue

            components = _collision_group_components(group, candidate_index, screening_by_id)
            if len(components) <= 1:
                continue  # fully explained as one connected component -- no error, no warning

            dedup_phase_pending = any(
                derive_workflow_state(o.data) == WORKFLOW_STATE_SYSTEM_INITIALIZED for o in group
            )
            component_summaries = ", ".join(
                "{" + ", ".join(sorted(component)) + "}" for component in sorted(components, key=lambda c: sorted(c))
            )
            if dedup_phase_pending:
                message = (
                    f"potential duplicate {field} '{normalized}' shared across screening record(s) under the "
                    f"same protocol, but not fully connected via duplicate_of/related_records: "
                    f"{component_summaries} -- flagged for human deduplication review, not yet an error while "
                    "at least one involved record is still in its pristine system-initialized state "
                    "(see ADR-0057/ADR-0058)"
                )
                emit = report.warning
            else:
                message = (
                    f"duplicate {field} '{normalized}' shared across screening record(s) under the same "
                    f"protocol, and not fully connected via duplicate_of/related_records: "
                    f"{component_summaries} -- either mark the redundant record(s) as decision: duplicate "
                    "with duplicate_of pointing to the primary record, or document the relationship via "
                    "related_records if they are eigenstaendige, but related publications (see ADR-0058)"
                )
                emit = report.error
            for o in group:
                emit(relative(o.path), f"$.candidate_identifiers.{field}", message)

        for normalized, group in url_map.items():
            active = [o for o in group if o.data.get("decision") in ACTIVE_SCREENING_DECISIONS]
            if len(active) >= 2:
                ids = ", ".join(sorted(o.id for o in active))
                for o in active:
                    report.warning(
                        relative(o.path), "$.candidate_identifiers.url",
                        f"candidate URL normalizes the same as other active screening record(s) under the "
                        f"same protocol: {ids} -- verify manually whether these are the same candidate "
                        "(redirects/mirrors can legitimately differ)",
                    )


def _reviewer_actor_type(reviewers: dict[str, "ResearchObject"], actor_id: str | None) -> str | None:
    """Liefert den registrierten actor_type eines research_actor_id-Kuerzels, oder None, wenn das
    Kuerzel nicht in research/reviewers/** registriert ist (siehe ADR-0059). Ein unregistriertes
    Kuerzel wird fuer decided_by/reviewed_by (normale Erst-/Zweitpruefer) wie ein menschlicher Akteur
    behandelt -- dieselbe Grenze wie die fuer 'human' optionale Registrierung; die Behauptung
    'KI-gestuetzt/automatisiert' wird erst durch eine tatsaechliche Registrierung ueberprüfbar, nicht
    automatisch unterstellt. WICHTIG (CSO-Review Runde 2): fuer die beiden hochkritischen Rollen
    adjudication.resolved_by und revision_context.triggered_by gilt diese Kulanz NICHT -- dort wird
    Registrierung als research_reviewer mit actor_type 'human' zwingend verlangt (siehe die
    dedizierten, direkten reviewers.get(...)-Pruefungen in _check_decision_snapshot statt dieser
    Funktion)."""
    if not actor_id:
        return None
    reviewer = reviewers.get(actor_id)
    if reviewer is None:
        return None
    return reviewer.data.get("actor_type")


def _check_decision_snapshot(
    report: Report,
    file_rel: str,
    protocol: ResearchObject | None,
    protocol_id: str | None,
    entry: dict,
    entry_label: str,
    reviewers: dict[str, "ResearchObject"],
    is_reversal: bool,
) -> None:
    """Prueft EINEN Entscheidungs-Snapshot (einen decision_history[]-Eintrag) gegen die
    vollstaendigen Workflow-Invarianten. Da die Top-Level-Felder eine geprueft konsistente
    Projektion der EFFEKTIVEN Werte des LETZTEN decision_history-Eintrags sind (siehe
    check_decision_history), deckt der Aufruf dieser Funktion fuer JEDEN Eintrag automatisch auch
    den aktuellen Zustand ab. Trennt strukturell primary_decision (Erstentscheidung, bleibt bei
    einem ungeloesten Widerspruch als decision: uncertain erhalten) von decision (effektiver,
    ggf. adjudizierter Zustand) -- siehe ADR-0043.

    Seit ADR-0059 (Phase 4B-1B-3, verschaerft in CSO-Review Runde 2) zusaetzlich, ueber `reviewers`
    (research/reviewers/**) und `is_reversal` (von check_decision_history bestimmt): verpflichtendes
    Zweitreview bei jeder nicht-administrativen primaeren wissenschaftlichen Entscheidung eines
    registrierten ai_assistant/automation-Akteurs (nicht mehr nur include/exclude), registrierte-
    Mensch-Pflicht fuer adjudication.resolved_by und revision_context.triggered_by (nicht mehr
    "unregistriert = Mensch"), revision_context bei Umkehrungen -- siehe die jeweiligen Pruefungen
    unten."""
    stage = entry.get("stage")
    primary_decision = entry.get("primary_decision")
    primary_duplicate_of = entry.get("primary_duplicate_of")
    decision = entry.get("decision")
    effective_duplicate_of = entry.get("duplicate_of")
    decided_by = entry.get("decided_by")
    decided_at = entry.get("decided_at")
    full_text_status = entry.get("full_text_status")
    second_review = entry.get("second_review")
    revision_context = entry.get("revision_context")

    configured_stages: set = set()
    dual_reviewer_stages: set = set()
    if protocol is not None:
        screening_policy = protocol.data.get("screening_policy") or {}
        configured_stages = set(screening_policy.get("stages") or [])
        dual_reviewer_stages = set(screening_policy.get("dual_reviewer_stages") or [])

    if protocol is not None and stage not in configured_stages:
        report.error(
            file_rel, f"{entry_label}.stage",
            f"stage '{stage}' is not among screening_policy.stages of protocol '{protocol_id}'",
        )

    allowed_decisions = ALLOWED_DECISIONS_BY_STAGE.get(stage)
    if allowed_decisions is not None:
        if primary_decision not in allowed_decisions:
            report.error(
                file_rel, f"{entry_label}.primary_decision",
                f"'{primary_decision}' is not an allowed decision for stage '{stage}' "
                f"(allowed: {sorted(allowed_decisions)})",
            )
        if decision not in allowed_decisions:
            report.error(
                file_rel, f"{entry_label}.decision",
                f"'{decision}' is not an allowed decision for stage '{stage}' "
                f"(allowed: {sorted(allowed_decisions)})",
            )

    # ADR-0059 (implementation Nachtrag, CSO-Review Runde 2): jede NICHT-administrative primaere
    # wissenschaftliche Entscheidung eines registrierten ai_assistant/automation-Akteurs erfordert
    # ein Zweitreview -- unabhaengig davon, ob screening_policy.dual_reviewer_stages diese Stufe
    # sonst verlangt, UND unabhaengig von der konkreten Entscheidung (include/exclude/
    # awaiting_full_text/uncertain/duplicate, jeweils soweit die Stage-/Decision-Matrix diese
    # Entscheidung an der jeweiligen Stufe ueberhaupt zulaesst). Erweitert den bestehenden
    # dual_reviewer_stages-Mechanismus (der bewusst auf include/exclude beschraenkt bleibt, siehe
    # unten) um eine zweite, unabhaengige Ausloesebedingung, statt einen neuen Mechanismus zu
    # erfinden. Die einzige Ausnahme ist der rein administrative 'pending'-Initialisierungseintrag
    # (strukturell nur an Stufe 'deduplication' zulaessig, siehe ALLOWED_DECISIONS_BY_STAGE, und nur
    # vom technischen Akteur system-screening-initializer erzeugt, siehe
    # check_screening_system_actor_invariants) -- das ist keine "Erstentscheidung" in diesem Sinne.
    decided_by_actor_type = _reviewer_actor_type(reviewers, decided_by)
    non_human_primary = decided_by_actor_type in ("ai_assistant", "automation")
    dual_reviewer_decision = primary_decision in ("include", "exclude")
    is_administrative_pending = primary_decision == "pending"
    if second_review is None:
        if dual_reviewer_decision and stage in dual_reviewer_stages and non_human_primary:
            report.error(
                file_rel, f"{entry_label}.second_review",
                f"stage '{stage}' is a dual-reviewer stage for protocol '{protocol_id}', and decided_by "
                f"'{decided_by}' is additionally registered as actor_type '{decided_by_actor_type}' -- "
                f"either reason alone already requires second_review for a primary '{primary_decision}' "
                "decision",
            )
        elif dual_reviewer_decision and stage in dual_reviewer_stages:
            report.error(
                file_rel, f"{entry_label}.second_review",
                f"stage '{stage}' is a dual-reviewer stage for protocol '{protocol_id}' -- a primary "
                f"'{primary_decision}' decision requires second_review",
            )
        elif non_human_primary and not is_administrative_pending:
            report.error(
                file_rel, f"{entry_label}.second_review",
                f"decided_by '{decided_by}' is registered in research/reviewers/** as actor_type "
                f"'{decided_by_actor_type}' -- every non-administrative primary scientific decision "
                f"('{primary_decision}') by a non-human actor requires second_review, regardless of "
                "screening_policy.dual_reviewer_stages (see ADR-0059)",
            )

    if second_review:
        reviewed_by = second_review.get("reviewed_by")
        if reviewed_by == decided_by:
            report.error(
                file_rel, f"{entry_label}.second_review.reviewed_by",
                "second_review.reviewed_by must differ from the primary reviewer (reviewer independence)",
            )

        reviewer_decision = second_review.get("reviewer_decision")
        if allowed_decisions is not None and reviewer_decision not in allowed_decisions:
            report.error(
                file_rel, f"{entry_label}.second_review.reviewer_decision",
                f"'{reviewer_decision}' is not an allowed decision for stage '{stage}' "
                f"(allowed: {sorted(allowed_decisions)})",
            )

        if stage == "deduplication" and second_review.get("adjudication") is not None:
            report.error(
                file_rel, f"{entry_label}.second_review.adjudication",
                "adjudication is not supported for stage 'deduplication' -- adjudication.final_decision is "
                "restricted to include/exclude, which cannot express a confirmed 'duplicate' outcome and would "
                "leave the stage's decision matrix only half-supported (see ADR-0046); a deduplication "
                "conflict must stay 'uncertain' and be resolved by a subsequent screening decision_history "
                "entry, not by third-party adjudication",
            )

        decision_confirmed = second_review.get("decision_confirmed")
        decisions_agree = reviewer_decision == primary_decision
        if decisions_agree and reviewer_decision == "duplicate":
            # ADR-0052: bei 'duplicate' reicht eine uebereinstimmende Entscheidungskategorie allein
            # nicht aus -- beide Pruefungen muessen zusaetzlich auf DENSELBEN Hauptdatensatz zeigen.
            # 'primary_duplicate_of: A' vs. 'reviewer_duplicate_of: B' ist ein inhaltlicher
            # Widerspruch (unterschiedliche Vorstellungen davon, WESSEN Duplikat der Kandidat ist),
            # auch wenn reviewer_decision == primary_decision == 'duplicate' ist.
            reviewer_duplicate_of = second_review.get("reviewer_duplicate_of")
            decisions_agree = reviewer_duplicate_of == primary_duplicate_of
        if decision_confirmed != decisions_agree:
            report.error(
                file_rel, f"{entry_label}.second_review.decision_confirmed",
                f"decision_confirmed ({decision_confirmed!r}) is inconsistent with whether reviewer_decision "
                f"('{reviewer_decision}') actually agrees with the PRIMARY decision ('{primary_decision}') -- "
                "decision_confirmed must be a validated projection of that comparison (for 'duplicate', "
                "also requiring reviewer_duplicate_of == primary_duplicate_of, see ADR-0052), not of the "
                "effective decision",
            )

        adjudication = second_review.get("adjudication")
        if decisions_agree:
            if adjudication is not None:
                report.error(
                    file_rel, f"{entry_label}.second_review.adjudication",
                    "adjudication is not allowed when reviewer_decision agrees with primary_decision -- there "
                    "is no conflict to resolve",
                )
            if decision != primary_decision:
                report.error(
                    file_rel, f"{entry_label}.decision",
                    f"decision ('{decision}') must equal primary_decision ('{primary_decision}') when "
                    "reviewer_decision agrees with it (no conflict to adjudicate)",
                )
            if primary_decision == "duplicate" and effective_duplicate_of != primary_duplicate_of:
                # ADR-0053: bei bestaetigtem Duplikatkonsens (Erst- und Zweitpruefung stimmen sowohl
                # in der Entscheidung als auch im Ziel ueberein, siehe ADR-0052) muss das effektive
                # duplicate_of GENAU dieses bestaetigte Ziel binden -- ein davon abweichender dritter
                # Hauptdatensatz waere sonst unbemerkt moeglich.
                report.error(
                    file_rel, f"{entry_label}.duplicate_of",
                    "effective duplicate_of must match the duplicate target confirmed by primary and "
                    "second review",
                )
        else:
            if adjudication is None:
                if decision != "uncertain":
                    report.error(
                        file_rel, f"{entry_label}.decision",
                        "second_review.reviewer_decision disagrees with primary_decision and no adjudication "
                        "is recorded -- decision must stay 'uncertain' until the conflict is resolved",
                    )
            else:
                resolved_by = adjudication.get("resolved_by")
                if resolved_by in (decided_by, reviewed_by):
                    report.error(
                        file_rel, f"{entry_label}.second_review.adjudication.resolved_by",
                        "adjudication.resolved_by must be a third person, distinct from the primary reviewer "
                        "and second_review.reviewed_by",
                    )
                # ADR-0059 (CSO-Review Runde 2): anders als decided_by/reviewed_by (siehe
                # _reviewer_actor_type) reicht fuer diese hochkritische Rolle "unregistriert" NICHT
                # mehr als implizite Mensch-Annahme -- ein Adjudikator MUSS als research_reviewer mit
                # actor_type 'human' registriert sein, hart und nicht protokollkonfigurierbar.
                resolved_by_reviewer = reviewers.get(resolved_by) if resolved_by else None
                resolved_by_actor_type = (
                    resolved_by_reviewer.data.get("actor_type") if resolved_by_reviewer is not None else None
                )
                if resolved_by_actor_type != "human":
                    registration_note = (
                        f"is registered in research/reviewers/** as actor_type '{resolved_by_actor_type}'"
                        if resolved_by_reviewer is not None
                        else "is not registered as a research_reviewer in research/reviewers/**"
                    )
                    report.error(
                        file_rel, f"{entry_label}.second_review.adjudication.resolved_by",
                        f"adjudication.resolved_by '{resolved_by}' {registration_note} -- adjudication must "
                        "always be resolved by a registered human actor (research_reviewer with actor_type "
                        "'human'), hard and not protocol-configurable (see ADR-0059)",
                    )
                final_decision = adjudication.get("final_decision")
                if final_decision != decision:
                    report.error(
                        file_rel, f"{entry_label}.second_review.adjudication.final_decision",
                        f"adjudication.final_decision ('{final_decision}') must match this entry's effective "
                        f"decision ('{decision}')",
                    )
                resolved_at = adjudication.get("resolved_at")
                reviewed_at = second_review.get("reviewed_at")
                if reviewed_at and resolved_at and resolved_at < reviewed_at:
                    report.error(
                        file_rel, f"{entry_label}.second_review.adjudication.resolved_at",
                        f"adjudication.resolved_at ('{resolved_at}') is before second_review.reviewed_at "
                        f"('{reviewed_at}')",
                    )

        reviewed_at = second_review.get("reviewed_at")
        if decided_at and reviewed_at and reviewed_at < decided_at:
            report.error(
                file_rel, f"{entry_label}.second_review.reviewed_at",
                f"second_review.reviewed_at ('{reviewed_at}') is before the primary decision date "
                f"('{decided_at}')",
            )
    else:
        if decision != primary_decision:
            report.error(
                file_rel, f"{entry_label}.decision",
                f"without second_review, decision ('{decision}') must equal primary_decision "
                f"('{primary_decision}')",
            )
        if primary_decision == "duplicate" and effective_duplicate_of != primary_duplicate_of:
            # ADR-0053: ohne Zweitpruefung ist die Erstentscheidung die einzige Quelle des effektiven
            # Zustands -- ein effektives duplicate_of, das vom primary_duplicate_of abweicht, ist
            # damit strukturell unbegruendet.
            report.error(
                file_rel, f"{entry_label}.duplicate_of",
                "effective duplicate_of must match the duplicate target confirmed by primary and "
                "second review",
            )

    if stage in FULL_TEXT_REQUIRING_STAGES and decision == "include" and full_text_status != "obtained":
        report.error(
            file_rel, f"{entry_label}.full_text_status",
            f"stage '{stage}' with decision 'include' requires full_text_status 'obtained', got "
            f"'{full_text_status}'",
        )

    # ADR-0059: revision_context ist ein echtes optionales Feld (kein required-aber-nullable Key
    # wie decision_reason) -- Pflicht genau dann, wenn dieser Eintrag eine vorherige Entscheidung
    # an derselben Stufe umkehrt (is_reversal, von check_decision_history bestimmt), sonst muss der
    # Key fehlen. triggered_by muss, sofern registriert, ein human-Akteur sein -- eine Wiederaufnahme
    # ist eine redaktionelle Grundsatzentscheidung, nicht Teil des routinemaessigen
    # KI-gestuetzten Ersttriagierens.
    if is_reversal and revision_context is None:
        report.error(
            file_rel, f"{entry_label}.revision_context",
            "this entry reverses the effective decision of the immediately preceding entry at the same "
            "stage -- revision_context (reason/reference/triggered_by) is required to document why "
            "(see ADR-0059)",
        )
    elif not is_reversal and revision_context is not None:
        report.error(
            file_rel, f"{entry_label}.revision_context",
            "revision_context is only allowed on an entry that actually reverses the effective decision "
            "of the immediately preceding entry at the same stage -- this entry does not reverse anything "
            "(see ADR-0059)",
        )
    if revision_context is not None:
        # ADR-0059 (CSO-Review Runde 2): dieselbe Verschaerfung wie bei adjudication.resolved_by
        # oben -- "unregistriert" reicht fuer diese hochkritische Rolle nicht mehr als implizite
        # Mensch-Annahme, triggered_by MUSS als research_reviewer mit actor_type 'human' registriert
        # sein.
        triggered_by = revision_context.get("triggered_by")
        triggered_by_reviewer = reviewers.get(triggered_by) if triggered_by else None
        triggered_by_actor_type = (
            triggered_by_reviewer.data.get("actor_type") if triggered_by_reviewer is not None else None
        )
        if triggered_by_actor_type != "human":
            registration_note = (
                f"is registered in research/reviewers/** as actor_type '{triggered_by_actor_type}'"
                if triggered_by_reviewer is not None
                else "is not registered as a research_reviewer in research/reviewers/**"
            )
            report.error(
                file_rel, f"{entry_label}.revision_context.triggered_by",
                f"triggered_by '{triggered_by}' {registration_note} -- reopening a prior decision must "
                "always be triggered by a registered human actor (research_reviewer with actor_type "
                "'human'), hard and not protocol-configurable (see ADR-0059)",
            )


def check_decision_history(
    report: Report, objects: dict[str, dict[str, ResearchObject]], search_runs: dict[str, ResearchObject]
) -> None:
    protocols = objects["protocol"]
    reviewers = objects["reviewer"]
    for obj in objects["screening_record"].values():
        file_rel = relative(obj.path)
        history = obj.data.get("decision_history") or []
        if not history:
            continue  # Schema erzwingt minItems: 1 bereits; hier nur defensiv

        protocol_id = obj.data.get("protocol_id")
        protocol = protocols.get(protocol_id)
        search_run_ids = obj.data.get("search_run_ids") or []

        expected_sequence = 1
        prev_stage_index = -1
        prev_decided_at = None
        prev_entry: dict | None = None
        for idx, entry in enumerate(history):
            entry_label = f"$.decision_history[{idx}]"

            sequence = entry.get("sequence")
            if sequence != expected_sequence:
                report.error(
                    file_rel, entry_label + ".sequence",
                    f"decision_history sequence must be contiguous starting at 1, expected {expected_sequence} "
                    f"but got {sequence!r}",
                )
            expected_sequence += 1

            stage = entry.get("stage")
            stage_index = SCREENING_STAGE_ORDER.index(stage) if stage in SCREENING_STAGE_ORDER else -1
            if stage_index < prev_stage_index:
                report.error(
                    file_rel, entry_label + ".stage",
                    f"decision_history stage regresses to '{stage}' after an entry at stage "
                    f"'{SCREENING_STAGE_ORDER[prev_stage_index]}' -- stages must not run backwards",
                )
            prev_stage_index = max(prev_stage_index, stage_index)

            decided_at = entry.get("decided_at")
            if prev_decided_at is not None and decided_at is not None and decided_at < prev_decided_at:
                report.error(
                    file_rel, entry_label + ".decided_at",
                    f"decision_history decided_at regresses from '{prev_decided_at}' to '{decided_at}'",
                )
            if decided_at is not None:
                prev_decided_at = decided_at

            for search_run_id in search_run_ids:
                search_run = search_runs.get(search_run_id)
                if search_run is None:
                    continue
                executed_date = (search_run.data.get("executed_at") or "")[:10]
                if executed_date and decided_at and decided_at < executed_date:
                    report.error(
                        file_rel, entry_label + ".decided_at",
                        f"decided_at ('{decided_at}') is before the executed_at date of referenced search "
                        f"run '{search_run_id}' ('{executed_date}') -- a screening decision cannot predate "
                        "a search run it is supposedly based on; a legitimate later rediscovery should "
                        "create a new screening_record instead of retroactively extending search_run_ids",
                    )

            # ADR-0059: eine "Umkehrung" liegt vor, wenn dieser Eintrag an derselben Stufe wie der
            # UNMITTELBAR vorangegangene Eintrag steht und dessen primary_decision von dessen
            # effektiver decision abweicht. Die bereits bestehende Monotonie-Pruefung oben verbietet
            # jeden echten Rueckwaertslauf (stage_index < prev_stage_index) bereits strukturell --
            # 'an derselben oder einer frueheren Stufe' aus der urspruenglichen Spezifikation
            # reduziert sich damit auf genau diesen einen erreichbaren Fall: Wiederholung derselben,
            # zuletzt erreichten Stufe.
            # Nur eine bereits SETTLED vorherige effektive Entscheidung (weder 'pending' -- noch gar
            # keine echte Entscheidung -- noch 'uncertain' -- ein noch ungeloester Widerspruch, kein
            # bestaetigter Zustand) kann ueberhaupt "umgekehrt" werden. Ein neuer Eintrag, der ein
            # zuvor 'uncertain' erstmals konkret aufloest (z. B. der bereits bestehende
            # Zielkonflikt-Mechanismus aus ADR-0052/ADR-0053), ist die erste tatsaechliche
            # Entscheidung, keine Umkehrung einer vorherigen.
            prev_decision_was_settled = prev_entry is not None and prev_entry.get("decision") not in (
                "pending", "uncertain",
            )
            is_reversal = (
                prev_decision_was_settled
                and prev_entry.get("stage") == stage
                and entry.get("primary_decision") != prev_entry.get("decision")
            )

            _check_decision_snapshot(
                report, file_rel, protocol, protocol_id, entry, entry_label, reviewers, is_reversal,
            )
            prev_entry = entry

        last = history[-1]
        mismatches = []
        if last.get("decision") != obj.data.get("decision"):
            mismatches.append("decision")
        if last.get("stage") != obj.data.get("decision_stage"):
            mismatches.append("decision_stage")
        if last.get("decision_reason") != obj.data.get("decision_reason"):
            mismatches.append("decision_reason")
        if last.get("duplicate_of") != obj.data.get("duplicate_of"):
            mismatches.append("duplicate_of")
        if last.get("decided_by") != obj.data.get("screened_by"):
            mismatches.append("screened_by")
        if last.get("decided_at") != obj.data.get("screened_at"):
            mismatches.append("screened_at")
        if last.get("full_text_status") != obj.data.get("full_text_status"):
            mismatches.append("full_text_status")
        if last.get("second_review") != obj.data.get("second_review"):
            mismatches.append("second_review")
        if mismatches:
            report.error(
                file_rel, "$.decision_history",
                "last decision_history entry does not match the top-level fields it should be a projection "
                "of (" + ", ".join(mismatches) + ")",
            )


def _collect_used_research_actor_ids(objects: dict[str, dict[str, ResearchObject]]) -> set[str]:
    """Every research_actor_id value actually referenced anywhere in this dataset (screening
    decision actors + protocol review reviewers) -- used by check_research_reviewers to scope the
    mandatory-registration rule to actors that are actually USED in the dataset being validated,
    rather than unconditionally demanding a research/reviewers/** registration from every dataset
    (including unrelated test fixtures that never mention these specific kuerzel at all)."""
    used: set[str] = set()
    for obj in objects["screening_record"].values():
        data = obj.data
        if data.get("screened_by"):
            used.add(data["screened_by"])
        for entry in data.get("decision_history") or []:
            if entry.get("decided_by"):
                used.add(entry["decided_by"])
            second_review = entry.get("second_review") or {}
            if second_review.get("reviewed_by"):
                used.add(second_review["reviewed_by"])
            adjudication = second_review.get("adjudication") or {}
            if adjudication.get("resolved_by"):
                used.add(adjudication["resolved_by"])
            revision_context = entry.get("revision_context") or {}
            if revision_context.get("triggered_by"):
                used.add(revision_context["triggered_by"])
    for obj in objects["protocol"].values():
        review = obj.data.get("review") or {}
        used.update(reviewer_id for reviewer_id in review.get("reviewers") or [] if reviewer_id)
    return used


def check_research_reviewers(report: Report, objects: dict[str, dict[str, ResearchObject]]) -> None:
    """ADR-0059 (Phase 4B-1B-3): registry-level consistency for research/reviewers/**, plus the
    mandatory-registration rule for the two non-human actors already established as real, documented
    facts elsewhere in this codebase -- but ONLY when this dataset actually references that actor
    kuerzel somewhere (see _collect_used_research_actor_ids); an unrelated dataset that never
    mentions 'system-screening-initializer'/'cso-chatgpt' at all has nothing to register:

    - 'system-screening-initializer' (ADR-0057, tools/initialize_screening_records.py), when used,
      must be registered with actor_type 'automation'.
    - 'cso-chatgpt' (Decision Log, Phase-4B-0 entry -- "der KI-basierte Chief Scientific Officer des
      Projekts, keine menschliche Person"), when used, must be registered with actor_type
      'ai_assistant'.

    Deliberately does NOT attempt to infer that some OTHER, not-yet-registered research_actor_id
    'should' be ai_assistant/automation/service -- that would require external knowledge this
    validator does not have (see research/reviewers/README.md on 'claude-code-operator', found during
    the Phase 4B-1B-3 inventory but left unregistered on purpose, nothing invented). Registration for
    any other actor is what actually switches on the structural rules in _check_decision_snapshot
    (mandatory second_review, human-only adjudication/triggered_by) -- there is nothing further to
    retroactively enforce beyond the two already-known actors above."""
    reviewers = objects["reviewer"]
    used_actor_ids = _collect_used_research_actor_ids(objects)

    for actor_id, expected_type in (
        (SYSTEM_SCREENING_INITIALIZER_ACTOR, "automation"),
        (CSO_CHATGPT_ACTOR, "ai_assistant"),
    ):
        if actor_id not in used_actor_ids:
            continue
        reviewer = reviewers.get(actor_id)
        if reviewer is None:
            report.error(
                "research/reviewers/", "$",
                f"'{actor_id}' is used as a research actor in this dataset and is a real, "
                f"already-documented non-human actor -- it must be registered in research/reviewers/** "
                f"with actor_type '{expected_type}' (see ADR-0059)",
            )
            continue
        actual_type = reviewer.data.get("actor_type")
        if actual_type != expected_type:
            report.error(
                relative(reviewer.path), "$.actor_type",
                f"'{actor_id}' must be registered with actor_type '{expected_type}', got '{actual_type}'",
            )

    for obj in reviewers.values():
        if obj.data.get("actor_type") not in MANDATORY_REVIEWER_REGISTRATION_ACTOR_TYPES | {"human"}:
            report.error(
                relative(obj.path), "$.actor_type",
                f"unexpected actor_type '{obj.data.get('actor_type')}' -- schema validation should "
                "already have rejected this",
            )  # defensive; unreachable unless the JSON schema enum itself is ever loosened


def check_extraction_verification(report: Report, objects: dict[str, dict[str, ResearchObject]]) -> None:
    """extraction_status: verified bedeutet in Peptide Atlas IMMER durch eine andere Person
    geprueft: verified_by != extracted_by wird unbedingt erzwungen, unabhaengig vom Protokoll
    (siehe ADR-0040 im Decision Log -- loest die vormals protokollabhaengige Ausnahme ab). Ein
    rein technischer Ein-Personen-Durchlauf verwendet stattdessen extraction_status:
    self_checked, das strukturell nie promotion-faehig ist (siehe check_promotion_records)."""
    for obj in objects["extraction_record"].values():
        file_rel = relative(obj.path)
        data = obj.data
        if data.get("extraction_status") != "verified":
            continue
        if data.get("verified_by") == data.get("extracted_by"):
            report.error(
                file_rel, "$.verified_by",
                "extraction_status: verified requires verified_by to differ from extracted_by -- use "
                "extraction_status: self_checked for a single-person technical pass instead (which can "
                "never be promoted)",
            )


def check_temporal_chain(report: Report, objects: dict[str, dict[str, ResearchObject]]) -> None:
    """Prueft die zeitliche Provenienzkette objektuebergreifend (siehe ADR-0044):

    terminale Screening-Entscheidung/-Zweitpruefung/-Adjudikation
        <= extraction.extracted_at <= extraction.verified_at
        <= promotion.created_at <= promotion.updated_at

    Fuer promotion_status approved_for_creation/promoted/rejected zusaetzlich:
        extraction.verified_at <= promotion.review.last_reviewed_at <= promotion.updated_at

    Fuer proposed/in_review gilt diese zweite Regel nicht: review.last_reviewed_at ist in diesen
    Stadien typischerweise noch null (kein Review hat stattgefunden), das ist kein Fehler."""
    screening = objects["screening_record"]
    extractions = objects["extraction_record"]

    for obj in extractions.values():
        file_rel = relative(obj.path)
        data = obj.data
        screening_obj = screening.get(data.get("screening_record_id"))
        if screening_obj is None:
            continue
        s_data = screening_obj.data
        second_review = s_data.get("second_review") or {}
        adjudication = second_review.get("adjudication") or {}
        # Die spaeteste bekannte "Einschlussfreigabe" dieses terminalen Zustands: Adjudikation,
        # sonst Zweitpruefung, sonst die reine Erstentscheidung -- in dieser Prioritaet, weil
        # jede Stufe (wo vorhanden) bereits per Datumsreihenfolge >= der vorherigen sein muss.
        effective_start = adjudication.get("resolved_at") or second_review.get("reviewed_at") or s_data.get("screened_at")
        extracted_at = data.get("extracted_at")
        if effective_start and extracted_at and extracted_at < effective_start:
            report.error(
                file_rel, "$.extracted_at",
                f"extracted_at ('{extracted_at}') is before the terminal screening inclusion for "
                f"'{screening_obj.id}' was completed ('{effective_start}') -- an extraction cannot predate "
                "its own scientific inclusion decision",
            )

    for obj in objects["promotion_record"].values():
        file_rel = relative(obj.path)
        data = obj.data
        extraction_obj = extractions.get(data.get("extraction_record_id"))
        if extraction_obj is None:
            continue
        verified_at = extraction_obj.data.get("verified_at")
        created_at = data.get("created_at")
        updated_at = data.get("updated_at")
        if verified_at and created_at and created_at < verified_at:
            report.error(
                file_rel, "$.created_at",
                f"created_at ('{created_at}') is before the referenced extraction's verified_at "
                f"('{verified_at}')",
            )
        if verified_at and updated_at and updated_at < verified_at:
            report.error(
                file_rel, "$.updated_at",
                f"updated_at ('{updated_at}') is before the referenced extraction's verified_at "
                f"('{verified_at}')",
            )

        if data.get("promotion_status") in ("approved_for_creation", "promoted", "rejected"):
            last_reviewed_at = (data.get("review") or {}).get("last_reviewed_at")
            if verified_at and last_reviewed_at and last_reviewed_at < verified_at:
                report.error(
                    file_rel, "$.review.last_reviewed_at",
                    f"review.last_reviewed_at ('{last_reviewed_at}') is before the referenced extraction's "
                    f"verified_at ('{verified_at}')",
                )
            if last_reviewed_at and updated_at and updated_at < last_reviewed_at:
                report.error(
                    file_rel, "$.updated_at",
                    f"updated_at ('{updated_at}') is before review.last_reviewed_at ('{last_reviewed_at}')",
                )


def check_promotion_records(
    report: Report, objects: dict[str, dict[str, ResearchObject]], claim_ids: set[str]
) -> None:
    extractions = objects["extraction_record"]
    protocols = objects["protocol"]
    active_by_candidate: dict[tuple[str, str], list[ResearchObject]] = {}

    for obj in objects["promotion_record"].values():
        file_rel = relative(obj.path)
        data = obj.data
        extraction_id = data.get("extraction_record_id")
        extraction = extractions.get(extraction_id)
        if extraction is None:
            report.error(
                file_rel, "$.extraction_record_id", f"references missing extraction record: {extraction_id}"
            )
        else:
            if extraction.data.get("extraction_status") != "verified":
                report.error(
                    file_rel, "$.extraction_record_id",
                    f"extraction record '{extraction_id}' is not extraction_status: verified (got "
                    f"'{extraction.data.get('extraction_status')}') -- promotion requires an independently "
                    "verified extraction; self_checked or draft extractions can never be promoted",
                )
            if extraction.data.get("protocol_id") != data.get("protocol_id"):
                report.error(
                    file_rel, "$.protocol_id",
                    f"protocol_id does not match the referenced extraction record's protocol_id "
                    f"('{extraction.data.get('protocol_id')}')",
                )
            candidate_working_id = data.get("candidate_working_id")
            candidate_ids = {c.get("working_id") for c in extraction.data.get("candidate_claims") or []}
            if candidate_working_id not in candidate_ids:
                report.error(
                    file_rel, "$.candidate_working_id",
                    f"candidate_working_id '{candidate_working_id}' is not present in extraction record "
                    f"'{extraction_id}'",
                )
            active_by_candidate.setdefault((extraction_id, candidate_working_id), []).append(obj)

        canonical_claim_id = data.get("canonical_claim_id")
        if canonical_claim_id and canonical_claim_id not in claim_ids:
            report.error(
                file_rel, "$.canonical_claim_id",
                f"references a canonical claim that does not exist under data/claims/**: {canonical_claim_id}",
            )

        promotion_status = data.get("promotion_status")
        if promotion_status in ("approved_for_creation", "promoted", "rejected"):
            # Symmetrisch fuer JEDE endgueltige Promotion-Entscheidung geprueft (siehe ADR-0046) --
            # eine Ablehnung ist wissenschaftlich/redaktionell genauso konsequenzreich wie eine
            # Freigabe und unterliegt daher derselben Zweitreview-Policy.
            protocol = protocols.get(data.get("protocol_id"))
            requires_second_review = bool(
                protocol is not None
                and (protocol.data.get("claim_promotion_policy") or {}).get("requires_second_review")
            )
            if requires_second_review:
                # Eindeutigkeit und Nicht-Leerheit der einzelnen Kuerzel sind bereits
                # schema-seitig erzwungen (uniqueItems + research_actor_id-Pattern, siehe
                # research_promotion_record.schema.json) -- hier wird nur noch die
                # protokollabhaengige Mindestanzahl geprueft.
                reviewers = (data.get("review") or {}).get("reviewers") or []
                if len(reviewers) < 2:
                    report.error(
                        file_rel, "$.review.reviewers",
                        f"protocol '{data.get('protocol_id')}' has claim_promotion_policy."
                        f"requires_second_review: true -- promotion_status '{promotion_status}' requires at "
                        f"least two distinct reviewers, got {reviewers!r}",
                    )

    for (extraction_id, candidate_working_id), records in active_by_candidate.items():
        active = [r for r in records if r.data.get("promotion_status") not in ("rejected", "withdrawn")]
        if len(active) > 1:
            ids = ", ".join(sorted(r.id for r in active))
            for r in active:
                report.error(
                    relative(r.path), "$.candidate_working_id",
                    f"candidate '{candidate_working_id}' from extraction record '{extraction_id}' has more "
                    f"than one active (non-rejected/withdrawn) promotion record at the same time: {ids}",
                )


def _check_unique(report: Report, file_rel: str, path: str, values: list) -> None:
    seen: set = set()
    for value in values:
        if value is None:
            continue
        if value in seen:
            report.error(file_rel, path, f"duplicate value '{value}' -- entries must be unique")
        seen.add(value)


def _check_date_order(report: Report, file_rel: str, label: str, earlier, later) -> None:
    if earlier and later and later < earlier:
        report.error(file_rel, f"$.{label}", f"'{label}' out of order: '{later}' is before '{earlier}'")


def _check_export_reference_safety(
    report: Report, file_rel: str, export_reference: str | None, path: str = "$.export_reference"
) -> None:
    """Prueft ein Feld, das (wie research_search_run.export_reference oder
    research_search_result_manifest.source_export_reference) auf einen lokalen, nicht versionierten
    Export unter research/raw/ verweisen soll -- niemals eine URL, absoluter Pfad oder '..'-Segment.
    `path` parametrisiert den gemeldeten JSON-Pfad, damit dieselbe Pruefung fuer beide Feldnamen
    wiederverwendbar bleibt."""
    if not export_reference:
        return
    if "://" in export_reference:
        report.error(
            file_rel, path,
            "must not be a URL -- only a relative path hint under research/raw/ is allowed",
        )
        return
    if export_reference.startswith("/") or export_reference.startswith("\\") or re.match(r"^[a-zA-Z]:[\\/]", export_reference):
        report.error(file_rel, path, "must be a relative path, not an absolute path")
        return
    normalized = export_reference.replace("\\", "/")
    if ".." in normalized.split("/"):
        report.error(file_rel, path, "must not contain '..' path segments")
        return
    if not normalized.lstrip("./").startswith("research/raw/"):
        report.error(file_rel, path, "must point to a path under research/raw/")


def check_misc_consistency(report: Report, objects: dict[str, dict[str, ResearchObject]]) -> None:
    search_runs = objects["search_run"]

    for obj in objects["protocol"].values():
        file_rel = relative(obj.path)
        data = obj.data
        _check_unique(
            report, file_rel, "$.research_questions",
            [q.get("id") for q in data.get("research_questions") or []],
        )
        dedup_policy = data.get("deduplication_policy") or {}
        _check_unique(
            report, file_rel, "$.deduplication_policy.identifier_priority",
            dedup_policy.get("identifier_priority") or [],
        )
        screening_policy = data.get("screening_policy") or {}
        stages = screening_policy.get("stages") or []
        dual_reviewer_stages = screening_policy.get("dual_reviewer_stages") or []
        _check_unique(report, file_rel, "$.screening_policy.stages", stages)
        _check_unique(report, file_rel, "$.screening_policy.dual_reviewer_stages", dual_reviewer_stages)
        for stage in dual_reviewer_stages:
            if stage not in stages:
                report.error(
                    file_rel, "$.screening_policy.dual_reviewer_stages",
                    f"dual reviewer stage '{stage}' is not among screening_policy.stages {sorted(set(stages))} "
                    "-- a stage must be configured as a screening stage before it can require dual review "
                    "(see ADR-0046)",
                )
        _check_unique(
            report, file_rel, "$.planned_information_sources",
            [s.get("database") for s in data.get("planned_information_sources") or []],
        )
        _check_date_order(report, file_rel, "created_at/updated_at", data.get("created_at"), data.get("updated_at"))

    for obj in search_runs.values():
        file_rel = relative(obj.path)
        data = obj.data
        date_range = data.get("date_range") or {}
        _check_date_order(report, file_rel, "date_range.from/to", date_range.get("from"), date_range.get("to"))
        _check_date_order(report, file_rel, "created_at/updated_at", data.get("created_at"), data.get("updated_at"))
        _check_export_reference_safety(report, file_rel, data.get("export_reference"))

    for obj in objects["screening_record"].values():
        file_rel = relative(obj.path)
        data = obj.data
        _check_unique(report, file_rel, "$.search_run_ids", data.get("search_run_ids") or [])

    for obj in objects["candidate_manifest"].values():
        file_rel = relative(obj.path)
        data = obj.data
        _check_date_order(report, file_rel, "created_at/updated_at", data.get("created_at"), data.get("updated_at"))
        _check_date_order(report, file_rel, "created_at/updated_at", data.get("created_at"), data.get("updated_at"))

    for obj in objects["extraction_record"].values():
        file_rel = relative(obj.path)
        data = obj.data
        _check_unique(
            report, file_rel, "$.candidate_claims",
            [c.get("working_id") for c in data.get("candidate_claims") or []],
        )
        _check_date_order(report, file_rel, "created_at/updated_at", data.get("created_at"), data.get("updated_at"))
        _check_date_order(report, file_rel, "extracted_at/verified_at", data.get("extracted_at"), data.get("verified_at"))

    for obj in objects["promotion_record"].values():
        file_rel = relative(obj.path)
        data = obj.data
        _check_date_order(report, file_rel, "created_at/updated_at", data.get("created_at"), data.get("updated_at"))

    for obj in objects["search_result_manifest"].values():
        file_rel = relative(obj.path)
        data = obj.data
        _check_date_order(report, file_rel, "created_at/updated_at", data.get("created_at"), data.get("updated_at"))
        _check_export_reference_safety(
            report, file_rel, data.get("source_export_reference"), path="$.source_export_reference"
        )


def check_search_result_manifests(report: Report, objects: dict[str, dict[str, ResearchObject]]) -> None:
    """Prueft research_search_result_manifest gegen research_search_run (siehe ADR-0055):
    referenzielle Existenz, gegenseitige Verknuepfung ueber result_capture.manifest_id, hoechstens
    ein Manifest je Suchlauf, Uebereinstimmung von count mit sowohl len(identifiers) als auch dem
    result_count des Suchlaufs, Konsistenz von identifier_type mit der Datenbank des Suchlaufs,
    kanonische Sortierreihenfolge (numerisch fuer pmid, lexikografisch fuer nct_id -- JSON Schema
    allein kann eine Sortierreihenfolge nicht ausdruecken, nur das jeweilige Identifikator-Pattern
    selbst, siehe research_search_result_manifest.schema.json), und den verbindlichen SHA-256 ueber
    die (bereits sortierten) identifiers (siehe _researchlib.compute_manifest_sha256).
    Eindeutigkeit der identifiers selbst ist bereits schema-seitig erzwungen (uniqueItems: true)."""
    search_runs = objects["search_run"]
    manifests = objects["search_result_manifest"]

    manifests_by_search_run: dict[str, list[ResearchObject]] = {}
    for obj in manifests.values():
        search_run_id = obj.data.get("search_run_id")
        if search_run_id:
            manifests_by_search_run.setdefault(search_run_id, []).append(obj)

    for obj in manifests.values():
        file_rel = relative(obj.path)
        data = obj.data
        search_run_id = data.get("search_run_id")
        search_run = search_runs.get(search_run_id)
        if search_run is None:
            report.error(file_rel, "$.search_run_id", f"references missing search run: {search_run_id}")
            continue

        result_capture = search_run.data.get("result_capture") or {}
        if result_capture.get("manifest_id") != obj.id:
            report.error(
                file_rel, "$.search_run_id",
                f"search run '{search_run_id}' does not reference this manifest back via its own "
                f"result_capture.manifest_id (points to {result_capture.get('manifest_id')!r} instead) -- a "
                "manifest and its search run must reference each other, and a manifest must not be left "
                "orphaned or attached to a search run that actually belongs to a different result set",
            )

        identifiers = data.get("identifiers") or []
        count = data.get("count")
        if count != len(identifiers):
            report.error(
                file_rel, "$.count",
                f"count ({count!r}) does not match the number of identifiers ({len(identifiers)})",
            )

        result_count = search_run.data.get("result_count")
        if count != result_count:
            report.error(
                file_rel, "$.count",
                f"count ({count!r}) does not match result_count ({result_count!r}) of referenced search "
                f"run '{search_run_id}'",
            )

        database = search_run.data.get("database")
        identifier_type = data.get("identifier_type")
        expected_type = DATABASE_TO_IDENTIFIER_TYPE.get(database)
        if expected_type and identifier_type != expected_type:
            report.error(
                file_rel, "$.identifier_type",
                f"database '{database}' (of referenced search run '{search_run_id}') requires "
                f"identifier_type '{expected_type}', got '{identifier_type}'",
            )

        if identifier_type == "pmid":
            valid_pmids = [ident for ident in identifiers if re.fullmatch(r"[1-9][0-9]*", ident)]
            if len(valid_pmids) == len(identifiers) and identifiers != sorted(identifiers, key=int):
                report.error(
                    file_rel, "$.identifiers", "PMIDs are not sorted in canonical (numeric ascending) order",
                )
        elif identifier_type == "nct_id":
            if identifiers != sorted(identifiers):
                report.error(
                    file_rel, "$.identifiers",
                    "NCT IDs are not sorted in canonical (lexicographic ascending) order",
                )

        expected_hash = compute_manifest_sha256(identifiers)
        if data.get("sha256") != expected_hash:
            report.error(
                file_rel, "$.sha256",
                "does not match the mandated hash rule sha256(('\\n'.join(identifiers) + '\\n').encode"
                "('utf-8')) over the identifiers exactly as stored in this manifest",
            )

        # R2 -- Punkt 3: zeitliche Provenienz. Ein Manifest ist die Momentaufnahme EINES bereits
        # ausgefuehrten Suchlaufs und kann daher nicht vor dessen Ausfuehrung entstanden sein.
        # executed_at ist ein date-time, created_at ein reines Datum -- Vergleich auf Datumsebene.
        executed_date = (search_run.data.get("executed_at") or "")[:10]
        created_at = data.get("created_at")
        if executed_date and created_at and created_at < executed_date:
            report.error(
                file_rel, "$.created_at",
                f"created_at ('{created_at}') is before the executed_at date of its own search run "
                f"'{search_run_id}' ('{executed_date}') -- a manifest cannot predate the search event "
                "it is a snapshot of",
            )

        # R2 -- Punkt 4: bei result_capture.status: complete muss das Manifest exakt dieselbe lokale
        # Exportreferenz dokumentieren wie sein Suchlauf -- ein Suchlauf darf nicht auf einen anderen
        # lokalen Ursprung verweisen als das Manifest, das er als sein eigenes ausgibt. Deckt implizit
        # auch den Fall search_run.export_reference: null ab (ungleich einem nicht-leeren
        # source_export_reference, das das Manifest-Schema bereits als Pflichtfeld erzwingt).
        if result_capture.get("status") == "complete":
            search_run_export_ref = search_run.data.get("export_reference")
            manifest_export_ref = data.get("source_export_reference")
            if search_run_export_ref != manifest_export_ref:
                report.error(
                    file_rel, "$.source_export_reference",
                    f"does not match export_reference ({search_run_export_ref!r}) of referenced search run "
                    f"'{search_run_id}' -- a complete manifest must document the exact same local export "
                    "source as its search run",
                )

    for search_run_id, group in manifests_by_search_run.items():
        if len(group) > 1:
            ids = ", ".join(sorted(o.id for o in group))
            for o in group:
                report.error(
                    relative(o.path), "$.search_run_id",
                    f"more than one search_result_manifest references search run '{search_run_id}': {ids} -- "
                    "a search run may have at most one active, complete manifest",
                )

    for obj in search_runs.values():
        file_rel = relative(obj.path)
        result_capture = obj.data.get("result_capture") or {}
        if result_capture.get("status") == "complete":
            manifest_id = result_capture.get("manifest_id")
            if manifest_id not in manifests:
                report.error(
                    file_rel, "$.result_capture.manifest_id",
                    f"references missing search_result_manifest: {manifest_id}",
                )


def _is_positive_int(value) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def _is_nonnegative_int(value) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


# database, das ein bestimmtes interface_profile.id strukturell voraussetzt (siehe ADR-0055
# R3-Nachtrag) -- 'unprofiled' erzwingt bewusst KEINE Datenbank.
PROFILE_REQUIRED_DATABASE = {
    "ncbi_eutils_esearch_v1": "pubmed",
    "clinicaltrials_gov_api_v2_v1": "clinicaltrials_gov",
}


def check_search_run_interface_profiles(report: Report, objects: dict[str, dict[str, ResearchObject]]) -> None:
    """R2/R3 (Haertung von ADR-0055): technische Mindestvalidierung fuer die derzeit implementierten
    API-Profile. Dispatch ausschliesslich ueber das kontrollierte, maschinenlesbare
    `interface_profile.id` (siehe research/vocabularies/search_interface_profiles.yaml) -- NICHT mehr
    ueber Textfragmente im frei formulierten `interface`-Feld (das bleibt rein menschenlesbar, siehe
    ADR-0055 R3-Nachtrag). Eine beliebige Umformulierung von `interface` kann diese Regeln damit nicht
    mehr umgehen. `id: unprofiled` unterliegt bewusst KEINEN API-spezifischen Parameterregeln --
    schema-seitig ist dafuer aber eine nicht leere `rationale` erzwungen (kein stiller Verzicht).
    Beweist nicht allein die tatsaechliche API-Antwort, verhindert aber strukturell unmoegliche
    Vollstaendigkeitsangaben (z. B. `retmax` kleiner als `result_count` ohne dokumentierte Pagination)."""
    for obj in objects["search_run"].values():
        file_rel = relative(obj.path)
        data = obj.data
        database = data.get("database")
        interface_profile = data.get("interface_profile") or {}
        profile_id = interface_profile.get("id")
        request_parameters = data.get("request_parameters") or {}
        result_capture = data.get("result_capture") or {}
        pagination = data.get("pagination")
        result_count = data.get("result_count")
        is_complete = result_capture.get("status") == "complete"

        required_database = PROFILE_REQUIRED_DATABASE.get(profile_id)
        if required_database and database != required_database:
            report.error(
                file_rel, "$.interface_profile.id",
                f"interface_profile '{profile_id}' requires database == '{required_database}', got "
                f"'{database}'",
            )

        if profile_id == "ncbi_eutils_esearch_v1":
            if request_parameters.get("db") != "pubmed":
                report.error(
                    file_rel, "$.request_parameters.db",
                    "NCBI E-utilities ESearch profile requires request_parameters.db == 'pubmed'",
                )
            if request_parameters.get("retmode") != "json":
                report.error(
                    file_rel, "$.request_parameters.retmode",
                    "NCBI E-utilities ESearch profile requires request_parameters.retmode == 'json'",
                )
            retmax = request_parameters.get("retmax")
            if not _is_positive_int(retmax):
                report.error(
                    file_rel, "$.request_parameters.retmax",
                    "NCBI E-utilities ESearch profile requires request_parameters.retmax to be a positive "
                    "integer",
                )
            retstart = request_parameters.get("retstart")
            if not _is_nonnegative_int(retstart):
                report.error(
                    file_rel, "$.request_parameters.retstart",
                    "NCBI E-utilities ESearch profile requires request_parameters.retstart to be a "
                    "non-negative integer",
                )
            if (
                is_complete and pagination is None
                and _is_positive_int(retmax) and isinstance(result_count, int)
                and retmax < result_count
            ):
                report.error(
                    file_rel, "$.request_parameters.retmax",
                    f"retmax ({retmax}) is less than result_count ({result_count}) with no pagination "
                    "documented -- the response cannot have contained the full result set",
                )

        elif profile_id == "clinicaltrials_gov_api_v2_v1":
            if request_parameters.get("query_parameter") != "query.term":
                report.error(
                    file_rel, "$.request_parameters.query_parameter",
                    "ClinicalTrials.gov API v2 profile requires request_parameters.query_parameter == "
                    "'query.term'",
                )
            if request_parameters.get("countTotal") is not True:
                report.error(
                    file_rel, "$.request_parameters.countTotal",
                    "ClinicalTrials.gov API v2 profile requires request_parameters.countTotal == true",
                )
            page_size = request_parameters.get("pageSize")
            if not _is_positive_int(page_size):
                report.error(
                    file_rel, "$.request_parameters.pageSize",
                    "ClinicalTrials.gov API v2 profile requires request_parameters.pageSize to be a "
                    "positive integer",
                )
            if request_parameters.get("format") != "json":
                report.error(
                    file_rel, "$.request_parameters.format",
                    "ClinicalTrials.gov API v2 profile requires request_parameters.format == 'json'",
                )
            if request_parameters.get("fields") != "NCTId":
                report.error(
                    file_rel, "$.request_parameters.fields",
                    "ClinicalTrials.gov API v2 profile requires request_parameters.fields == 'NCTId'",
                )

            if is_complete:
                if not isinstance(pagination, dict):
                    report.error(
                        file_rel, "$.pagination",
                        "ClinicalTrials.gov API v2 profile requires pagination to be documented when "
                        "result_capture.status is 'complete'",
                    )
                else:
                    pages_retrieved = pagination.get("pages_retrieved")
                    if pagination.get("completion_confirmed") is not True:
                        report.error(
                            file_rel, "$.pagination.completion_confirmed",
                            "must be true for a complete result capture -- otherwise a further page may "
                            "have been skipped",
                        )
                    if not _is_positive_int(pages_retrieved):
                        report.error(
                            file_rel, "$.pagination.pages_retrieved",
                            "must be a positive integer",
                        )
                    elif (
                        _is_positive_int(page_size) and isinstance(result_count, int)
                        and pages_retrieved * page_size < result_count
                    ):
                        report.error(
                            file_rel, "$.pagination.pages_retrieved",
                            f"pages_retrieved ({pages_retrieved}) x pageSize ({page_size}) = "
                            f"{pages_retrieved * page_size} is less than result_count ({result_count}) -- "
                            "the documented pagination cannot have covered the full result set",
                        )


def _check_candidate_reference_safety(
    report: Report, file_rel: str, path: str, value: str | None, *, require_raw_path: bool
) -> None:
    """Prueft ein Metadaten-Provenienzfeld (request_reference oder response_locator) auf
    Sicherheit (siehe ADR-0056): keine vollstaendige URL, keine offensichtlichen Secret-Parameter
    (api_key/apikey/token/secret), kein absoluter oder '..'-Pfad. `require_raw_path` erzwingt
    zusaetzlich, dass ein gesetzter Wert unter research/raw/ liegt (wie export_reference/
    source_export_reference bei Suchlaeufen/Manifesten) -- fuer response_locator, nicht fuer
    request_reference (das ist eine reine technische Kurzbeschreibung, kein Dateipfad)."""
    if not value:
        return
    lowered = value.lower()
    if "://" in value:
        report.error(file_rel, path, "must not be a full URL -- only a short technical reference is allowed")
        return
    for secret_marker in ("api_key", "apikey", "token", "secret"):
        if secret_marker in lowered:
            report.error(file_rel, path, f"must not contain what looks like a secret parameter ('{secret_marker}')")
            return
    if not require_raw_path:
        return
    if value.startswith("/") or value.startswith("\\") or re.match(r"^[a-zA-Z]:[\\/]", value):
        report.error(file_rel, path, "must be a relative path, not an absolute path")
        return
    normalized = value.replace("\\", "/")
    if ".." in normalized.split("/"):
        report.error(file_rel, path, "must not contain '..' path segments")
        return
    if not normalized.lstrip("./").startswith("research/raw/"):
        report.error(file_rel, path, "must point to a path under research/raw/")


CANDIDATE_METADATA_FETCHED_REQUIRED_FIELDS = {
    "pubmed": (("title", "a non-empty title"), ("abstract_available", "abstract_available to be set")),
    "clinicaltrials_gov": (
        ("brief_title", "a non-empty brief_title"),
        ("overall_status", "a non-empty overall_status"),
        ("has_results", "has_results to be set"),
    ),
}


def check_candidate_manifests(report: Report, objects: dict[str, dict[str, ResearchObject]]) -> None:
    """Prueft research_candidate_manifest (siehe ADR-0056, Phase 4B-1B-0-Arbeitsauftrag Abschnitt 6):

    - source_search_run_ids/source_result_manifest_ids existieren, gehoeren zum selben Protokoll bzw.
      Suchlauf, und database/identifier_namespace stimmen ueberein.
    - Die Kandidatenmenge ist die exakte, bijektive Vereinigung der Identifikatoren aller
      referenzierten Search Result Manifests -- kein fehlender, kein zusaetzlicher Identifikator.
    - candidate_count == len(candidates); candidate_id projektweit eindeutig; primary_identifier
      innerhalb von Protokoll+Namespace eindeutig.
    - discovered_in_search_run_ids ist die vollstaendige, korrekte Herkunftsmenge (weder zu wenig
      noch zu viele Suchlaeufe).
    - metadata_provenance.retrieved_at liegt innerhalb [created_at, updated_at] des Manifests.
    - metadata_status: fetched verlangt die je Datenbank definierten Pflichtmetadaten.
    """
    search_runs = objects["search_run"]
    result_manifests = objects["search_result_manifest"]
    candidate_manifests = objects["candidate_manifest"]

    seen_candidate_ids: dict[str, str] = {}
    seen_primary_identifiers: dict[tuple[str, str, str], str] = {}

    for obj in candidate_manifests.values():
        file_rel = relative(obj.path)
        data = obj.data
        protocol_id = data.get("protocol_id")
        database = data.get("database")
        identifier_namespace = data.get("identifier_namespace")
        expected_namespace = DATABASE_TO_IDENTIFIER_TYPE.get(database)

        if expected_namespace and identifier_namespace != expected_namespace:
            report.error(
                file_rel, "$.identifier_namespace",
                f"database '{database}' requires identifier_namespace '{expected_namespace}', got "
                f"'{identifier_namespace}'",
            )

        run_objs: list[ResearchObject] = []
        for search_run_id in data.get("source_search_run_ids") or []:
            run = search_runs.get(search_run_id)
            if run is None:
                report.error(file_rel, "$.source_search_run_ids", f"references missing search run: {search_run_id}")
                continue
            if run.data.get("protocol_id") != protocol_id:
                report.error(
                    file_rel, "$.source_search_run_ids",
                    f"search run '{search_run_id}' belongs to protocol '{run.data.get('protocol_id')}', not this "
                    f"candidate manifest's protocol '{protocol_id}'",
                )
            if run.data.get("database") != database:
                report.error(
                    file_rel, "$.source_search_run_ids",
                    f"search run '{search_run_id}' uses database '{run.data.get('database')}', not this candidate "
                    f"manifest's database '{database}'",
                )
            run_objs.append(run)

        manifest_objs: list[ResearchObject] = []
        for manifest_id in data.get("source_result_manifest_ids") or []:
            manifest = result_manifests.get(manifest_id)
            if manifest is None:
                report.error(
                    file_rel, "$.source_result_manifest_ids",
                    f"references missing search result manifest: {manifest_id}",
                )
                continue
            if manifest.data.get("identifier_type") != identifier_namespace:
                report.error(
                    file_rel, "$.source_result_manifest_ids",
                    f"search result manifest '{manifest_id}' has identifier_type "
                    f"'{manifest.data.get('identifier_type')}', not this candidate manifest's identifier_namespace "
                    f"'{identifier_namespace}'",
                )
            manifest_objs.append(manifest)

        source_manifest_ids = set(data.get("source_result_manifest_ids") or [])
        for run in run_objs:
            manifest_id = (run.data.get("result_capture") or {}).get("manifest_id")
            if manifest_id and manifest_id not in source_manifest_ids:
                report.error(
                    file_rel, "$.source_result_manifest_ids",
                    f"search run '{run.id}' is referenced via source_search_run_ids, but its manifest "
                    f"'{manifest_id}' is missing from source_result_manifest_ids",
                )
        source_run_ids = set(data.get("source_search_run_ids") or [])
        for manifest in manifest_objs:
            search_run_id = manifest.data.get("search_run_id")
            if search_run_id and search_run_id not in source_run_ids:
                report.error(
                    file_rel, "$.source_search_run_ids",
                    f"search result manifest '{manifest.id}' belongs to search run '{search_run_id}', which is "
                    "missing from source_search_run_ids",
                )

        normalize = NORMALIZERS.get(identifier_namespace)
        discovered: dict[str, set[str]] = {}
        if normalize is not None:
            for manifest in manifest_objs:
                search_run_id = manifest.data.get("search_run_id")
                for raw_identifier in manifest.data.get("identifiers") or []:
                    discovered.setdefault(normalize(raw_identifier), set()).add(search_run_id)

        candidate_list = data.get("candidates") or []
        if data.get("candidate_count") != len(candidate_list):
            report.error(
                file_rel, "$.candidate_count",
                f"candidate_count ({data.get('candidate_count')!r}) does not match the number of candidates "
                f"({len(candidate_list)})",
            )

        seen_in_manifest: dict[str, str] = {}
        for idx, candidate in enumerate(candidate_list):
            entry_label = f"$.candidates[{idx}]"
            candidate_id = candidate.get("candidate_id")
            primary_identifier = candidate.get("primary_identifier") or {}
            namespace = primary_identifier.get("namespace")
            value = primary_identifier.get("value")
            normalized = normalize(value) if (normalize is not None and value) else value

            if candidate_id:
                if candidate_id in seen_candidate_ids:
                    report.error(
                        file_rel, f"{entry_label}.candidate_id",
                        f"duplicate candidate_id '{candidate_id}', already used in "
                        f"{seen_candidate_ids[candidate_id]}",
                    )
                else:
                    seen_candidate_ids[candidate_id] = file_rel

            if normalized:
                key = (protocol_id, namespace, normalized)
                if key in seen_primary_identifiers:
                    report.error(
                        file_rel, f"{entry_label}.primary_identifier",
                        f"duplicate {namespace} '{normalized}' within protocol '{protocol_id}', already used by "
                        f"candidate '{seen_primary_identifiers[key]}'",
                    )
                else:
                    seen_primary_identifiers[key] = candidate_id

            if normalized and normalized not in discovered:
                report.error(
                    file_rel, f"{entry_label}.primary_identifier",
                    f"identifier '{normalized}' is not present in any of this manifest's referenced search result "
                    "manifests -- a candidate manifest may only contain identifiers actually discovered by "
                    "source_result_manifest_ids",
                )
            elif normalized:
                if normalized in seen_in_manifest:
                    report.error(
                        file_rel, f"{entry_label}.primary_identifier",
                        f"duplicate {namespace} '{normalized}' within this candidate manifest, already used by "
                        f"candidate '{seen_in_manifest[normalized]}'",
                    )
                else:
                    seen_in_manifest[normalized] = candidate_id

            declared_runs = set(candidate.get("discovered_in_search_run_ids") or [])
            actual_runs = discovered.get(normalized, set()) if normalized else set()
            missing_runs = actual_runs - declared_runs
            extra_runs = declared_runs - actual_runs
            if missing_runs:
                report.error(
                    file_rel, f"{entry_label}.discovered_in_search_run_ids",
                    f"is missing search run(s) that actually contained this identifier: {sorted(missing_runs)}",
                )
            if extra_runs:
                report.error(
                    file_rel, f"{entry_label}.discovered_in_search_run_ids",
                    f"lists search run(s) that did not actually contain this identifier: {sorted(extra_runs)}",
                )

            provenance = candidate.get("metadata_provenance") or {}
            retrieved_at = provenance.get("retrieved_at")
            if retrieved_at:
                retrieved_date = retrieved_at[:10]
                created_at = data.get("created_at")
                updated_at = data.get("updated_at")
                if created_at and retrieved_date < created_at:
                    report.error(
                        file_rel, f"{entry_label}.metadata_provenance.retrieved_at",
                        f"retrieved_at ('{retrieved_at}') is before this manifest's created_at ('{created_at}')",
                    )
                if updated_at and retrieved_date > updated_at:
                    report.error(
                        file_rel, f"{entry_label}.metadata_provenance.retrieved_at",
                        f"retrieved_at ('{retrieved_at}') is after this manifest's updated_at ('{updated_at}')",
                    )
            _check_candidate_reference_safety(
                report, file_rel, f"{entry_label}.metadata_provenance.request_reference",
                provenance.get("request_reference"), require_raw_path=False,
            )
            _check_candidate_reference_safety(
                report, file_rel, f"{entry_label}.metadata_provenance.response_locator",
                provenance.get("response_locator"), require_raw_path=True,
            )

            metadata_status = candidate.get("metadata_status")
            metadata = candidate.get("metadata") or {}
            if metadata_status == "fetched":
                for field, description in CANDIDATE_METADATA_FETCHED_REQUIRED_FIELDS.get(database, ()):
                    if metadata.get(field) is None or metadata.get(field) == "":
                        report.error(
                            file_rel, f"{entry_label}.metadata.{field}",
                            f"metadata_status 'fetched' requires {description} for a '{database}' candidate",
                        )

        missing_candidates = set(discovered) - set(seen_in_manifest)
        if missing_candidates:
            shown = sorted(missing_candidates)[:10]
            suffix = "..." if len(missing_candidates) > 10 else ""
            report.error(
                file_rel, "$.candidates",
                f"{len(missing_candidates)} identifier(s) discovered by the referenced search result manifest(s) "
                f"are missing from candidates: {shown}{suffix}",
            )


def check_screening_candidate_references(report: Report, objects: dict[str, dict[str, ResearchObject]]) -> None:
    """Prueft die optionale Rueckverknuepfung eines Screening Records auf einen Discovery-
    Kandidaten (candidate_manifest_id/candidate_id, siehe ADR-0056, Migrationsstrategie): Ziel
    existiert, gehoert zum selben Protokoll, und der referenzierte Kandidat ist innerhalb des
    Manifests tatsaechlich vorhanden.

    Die Referenzpflicht ist DATENGETRIEBEN (CSO-Review, siehe Nachtrag zu ADR-0056) statt ueber eine
    hartkodierte Protokoll-Allowlist: existiert mindestens ein research_candidate_manifest mit
    derselben protocol_id, muessen NEUE (nicht unter research/examples/** liegende) Screening
    Records dieses Protokolls candidate_manifest_id/candidate_id setzen. Existiert (noch) kein
    Candidate Manifest fuer ein Protokoll, bleiben dessen Screening Records migrationskompatibel --
    keine Pflicht. research/examples/** ist davon unabhaengig immer ausgenommen.

    Liegt eine aufgeloeste Kandidatenreferenz vor, muss der zum Namespace des Kandidaten passende
    externe Identifikator (candidate_identifiers.pmid fuer pmid, .nct_id fuer nct_id) im Screening
    Record gesetzt sein UND mit dem Kandidaten uebereinstimmen -- ein fehlender Identifikator und ein
    abweichender Identifikator sind zwei getrennte, eigenstaendige Validierungsfehler."""
    candidate_manifests = objects["candidate_manifest"]
    protocols_with_candidate_manifests = {
        manifest.data.get("protocol_id") for manifest in candidate_manifests.values()
    }

    for obj in objects["screening_record"].values():
        file_rel = relative(obj.path)
        data = obj.data
        is_example = "examples" in obj.path.parts
        candidate_manifest_id = data.get("candidate_manifest_id")
        candidate_id = data.get("candidate_id")

        if (
            not is_example
            and data.get("protocol_id") in protocols_with_candidate_manifests
            and not (candidate_manifest_id and candidate_id)
        ):
            report.error(
                file_rel, "$.candidate_manifest_id",
                f"protocol '{data.get('protocol_id')}' has at least one candidate manifest -- new screening "
                "records for this protocol must reference a candidate_manifest_id/candidate_id (see ADR-0056 "
                "migration plan)",
            )

        if not candidate_manifest_id and not candidate_id:
            continue

        manifest = candidate_manifests.get(candidate_manifest_id)
        if manifest is None:
            report.error(
                file_rel, "$.candidate_manifest_id",
                f"references missing candidate manifest: {candidate_manifest_id}",
            )
            continue
        if manifest.data.get("protocol_id") != data.get("protocol_id"):
            report.error(
                file_rel, "$.candidate_manifest_id",
                f"candidate manifest '{candidate_manifest_id}' belongs to a different protocol "
                f"('{manifest.data.get('protocol_id')}') than this screening record ('{data.get('protocol_id')}')",
            )

        candidate_entry = next(
            (c for c in manifest.data.get("candidates") or [] if c.get("candidate_id") == candidate_id), None,
        )
        if candidate_entry is None:
            report.error(
                file_rel, "$.candidate_id",
                f"references missing candidate '{candidate_id}' in candidate manifest '{candidate_manifest_id}'",
            )
            continue

        expected_search_run_ids = set(candidate_entry.get("discovered_in_search_run_ids") or [])
        actual_search_run_ids = set(data.get("search_run_ids") or [])
        if expected_search_run_ids != actual_search_run_ids:
            report.error(
                file_rel, "$.search_run_ids",
                "must exactly match the referenced candidate's discovered_in_search_run_ids "
                f"({sorted(expected_search_run_ids)}), not just partially overlap it",
            )

        primary_identifier = candidate_entry.get("primary_identifier") or {}
        namespace = primary_identifier.get("namespace")
        candidate_value = primary_identifier.get("value")
        field = {"pmid": "pmid", "nct_id": "nct_id"}.get(namespace)
        if field:
            screening_value = (data.get("candidate_identifiers") or {}).get(field)
            normalize = NORMALIZERS.get(field)
            if not screening_value:
                report.error(
                    file_rel, f"$.candidate_identifiers.{field}",
                    f"must not be null -- candidate_id references a '{namespace}' candidate manifest entry, so "
                    f"candidate_identifiers.{field} must be set and match it",
                )
            elif normalize and normalize(screening_value) != normalize(candidate_value):
                report.error(
                    file_rel, f"$.candidate_identifiers.{field}",
                    f"conflicts with the referenced candidate's primary_identifier ('{candidate_value}')",
                )


def check_screening_related_records(report: Report, objects: dict[str, dict[str, ResearchObject]]) -> None:
    """ADR-0058 (Phase 4B-1B-2): referenzielle und gerichtet-symmetrische Pruefung von
    research_screening_record.related_records[] -- strukturell getrennt von duplicate_of, das
    ausschliesslich fuer bibliographische Dubletten (derselbe Text) reserviert bleibt. related_records
    dokumentiert eigenstaendige, aber inhaltlich verwandte Kandidaten (z. B. Letter+Reply).

    Referenziert Kandidaten (related_candidate_manifest_id/related_candidate_id), NICHT Screening
    Records: das Ziel muss als candidates[]-Eintrag innerhalb eines research_candidate_manifest mit
    DEMSELBEN protocol_id wie der referenzierende Screening Record existieren, darf nicht der eigene
    Kandidat sein (kein Selbstverweis), und relationship_metadata.identified_by darf nicht der
    technische Initialisierungsakteur sein -- eine Beziehungsklassifikation ist eine inhaltliche,
    keine technische Entscheidung.

    Gerichtete Symmetrie (Abschnitt 2.4/6 des Architektur-Entwurfs, verschaerft in CSO-Review Runde 3):
    existiert bereits ein Screening Record fuer den Ziel-Kandidaten, muss dessen eigenes
    related_records[] einen Eintrag tragen, der auf den referenzierenden Kandidaten mit dem in
    RELATIONSHIP_TYPE_INVERSE hinterlegten INVERSEN Typ verweist -- eine FEHLENDE Gegenrichtung ist in
    diesem Fall ein FEHLER (nicht mehr nur eine Warnung), ein Eintrag, der stattdessen wieder denselben
    Typ traegt, bleibt ebenfalls ein Fehler. NUR wenn fuer den Ziel-Kandidaten noch KEIN Screening
    Record existiert, ist die fehlende Gegenrichtung (noch) kein Fehler, sondern eine Warnung (wird
    erneut geprueft, sobald der Ziel-Datensatz angelegt wird) -- die Warnung ist damit ausschliesslich
    diesem einen Fall vorbehalten. Dieselbe Vollstaendigkeitsregel (_validated_inverse_relationship_
    target) entscheidet auch, welche related_records-Kanten die Kollisionsgruppen-Konnektivitaetspruefung
    in check_deduplication nutzen darf -- eine einseitige oder falsch-inverse Beziehung verbindet dort
    KEINE Kollisionskomponente."""
    candidate_manifests = objects["candidate_manifest"]
    screening = objects["screening_record"]

    by_protocol: dict[str, list[ResearchObject]] = {}
    for obj in screening.values():
        by_protocol.setdefault(obj.data.get("protocol_id"), []).append(obj)

    for protocol_id, records in by_protocol.items():
        candidate_index = _candidate_to_screening_record_index(records)

        for obj in records:
            file_rel = relative(obj.path)
            data = obj.data
            own_key = (data.get("candidate_manifest_id"), data.get("candidate_id"))

            for idx, rel in enumerate(data.get("related_records") or []):
                path_prefix = f"$.related_records[{idx}]"
                target_manifest_id = rel.get("related_candidate_manifest_id")
                target_candidate_id = rel.get("related_candidate_id")
                relationship_type = rel.get("relationship_type")
                relationship_metadata = rel.get("relationship_metadata") or {}
                target_key = (target_manifest_id, target_candidate_id)

                if target_key == own_key:
                    report.error(
                        file_rel, f"{path_prefix}.related_candidate_id",
                        "cannot reference the record's own candidate (self-reference)",
                    )
                    continue

                manifest = candidate_manifests.get(target_manifest_id)
                if manifest is None:
                    report.error(
                        file_rel, f"{path_prefix}.related_candidate_manifest_id",
                        f"references missing candidate manifest: {target_manifest_id}",
                    )
                    continue
                if manifest.data.get("protocol_id") != protocol_id:
                    report.error(
                        file_rel, f"{path_prefix}.related_candidate_manifest_id",
                        f"candidate manifest '{target_manifest_id}' belongs to a different protocol "
                        f"('{manifest.data.get('protocol_id')}') than this screening record ('{protocol_id}')",
                    )
                    continue
                target_candidate = next(
                    (c for c in manifest.data.get("candidates") or [] if c.get("candidate_id") == target_candidate_id),
                    None,
                )
                if target_candidate is None:
                    report.error(
                        file_rel, f"{path_prefix}.related_candidate_id",
                        f"references missing candidate '{target_candidate_id}' in candidate manifest "
                        f"'{target_manifest_id}'",
                    )
                    continue

                identified_by = relationship_metadata.get("identified_by")
                if identified_by == SYSTEM_SCREENING_INITIALIZER_ACTOR:
                    report.error(
                        file_rel, f"{path_prefix}.relationship_metadata.identified_by",
                        f"'{SYSTEM_SCREENING_INITIALIZER_ACTOR}' is a purely technical actor and must never "
                        "identify a related_records relationship -- classifying two candidates as related is "
                        "an editorial, scientific judgment, not a technical initialization step (see ADR-0058)",
                    )

                expected_inverse = RELATIONSHIP_TYPE_INVERSE.get(relationship_type)
                target_screening_id = candidate_index.get(target_key)
                if target_screening_id is None:
                    report.warning(
                        file_rel, f"{path_prefix}.relationship_type",
                        f"target candidate '{target_candidate_id}' does not have a screening record yet -- "
                        "the inverse relationship cannot be documented until one exists (will be re-checked "
                        "once the target screening record is created, see ADR-0058)",
                    )
                    continue

                # CSO-Review Runde 3: sobald der Ziel-Screening-Record existiert, ist die Gegenrichtung
                # PFLICHT (ERROR), nicht mehr nur eine Warnung -- Warnung bleibt ausschliesslich dem Fall
                # "Ziel-Kandidat hat noch keinen Screening Record" oben vorbehalten. Die Entscheidung
                # "vollstaendig validiert?" laeuft ueber denselben Helper wie die Kollisionsgruppenbildung
                # (_validated_inverse_relationship_target), um eine divergierende Zweitimplementierung
                # auszuschliessen; die konkrete Fehlermeldung unterscheidet weiterhin fehlend vs. falscher Typ.
                if _validated_inverse_relationship_target(obj, rel, candidate_index, screening) is not None:
                    continue

                target_obj = screening[target_screening_id]
                back_reference = next(
                    (
                        r for r in (target_obj.data.get("related_records") or [])
                        if r.get("related_candidate_manifest_id") == data.get("candidate_manifest_id")
                        and r.get("related_candidate_id") == data.get("candidate_id")
                    ),
                    None,
                )
                if back_reference is None:
                    report.error(
                        relative(target_obj.path), "$.related_records",
                        f"screening record '{obj.id}' documents a '{relationship_type}' relationship to this "
                        f"candidate, and a screening record already exists for this target -- this record must "
                        f"document the inverse relationship ('{expected_inverse}') back (see ADR-0058)",
                    )
                elif back_reference.get("relationship_type") != expected_inverse:
                    report.error(
                        relative(target_obj.path), "$.related_records",
                        f"screening record '{obj.id}' documents a '{relationship_type}' relationship to this "
                        f"candidate; the inverse entry here must use relationship_type "
                        f"'{expected_inverse}', got '{back_reference.get('relationship_type')}' (see ADR-0058)",
                    )


def check_screening_system_actor_invariants(
    report: Report, objects: dict[str, dict[str, ResearchObject]]
) -> None:
    """ADR-0057: 'system-screening-initializer' (tools/initialize_screening_records.py) dokumentiert
    ausschliesslich die rein technische Initialisierung eines Screening Records und trifft NIE eine
    wissenschaftliche Entscheidung. Zwei getrennte Invarianten:

    1. JEDER decision_history-Eintrag, den dieser Akteur als decided_by verantwortet, muss
       strukturell neutral bleiben -- primary_decision 'pending', stage 'deduplication',
       full_text_status 'not_yet_obtained', kein Duplikatverweis, keine Zweitpruefung -- unabhaengig
       davon, an welcher Position im Verlauf der Eintrag steht (verhindert nachtraegliche
       Umdeklarierung eines echten Screening-Ergebnisses als System-Eintrag).
    2. Solange der Bearbeitungszustand (seit ADR-0058, Phase 4B-1B-2: _researchlib.
       derive_workflow_state(), NICHT mehr direkt gegen screened_by verglichen -- reine Projektion
       aus decision_history, keine zweite Wahrheitsquelle) noch 'system_initialized' ist (der
       Datensatz also noch nie von einem Menschen bearbeitet wurde), muss canonical_source_id null
       bleiben und -- bei aufgeloester Kandidatenreferenz -- candidate_title exakt der aus den
       Candidate-Manifest-Metadaten abgeleitete technische Titel sein (siehe
       tools/_researchlib.py::derive_candidate_title). Sobald ein Mensch einen weiteren
       decision_history-Eintrag anhaengt, greift diese zweite Invariante nicht mehr fuer diesen
       Datensatz -- die erste bleibt unabhaengig davon fuer den urspruenglichen Eintrag bestehen.
    """
    candidate_manifests = objects["candidate_manifest"]

    for obj in objects["screening_record"].values():
        file_rel = relative(obj.path)
        data = obj.data

        for idx, entry in enumerate(data.get("decision_history") or []):
            if entry.get("decided_by") != SYSTEM_SCREENING_INITIALIZER_ACTOR:
                continue
            path_prefix = f"$.decision_history[{idx}]"
            if entry.get("primary_decision") != "pending":
                report.error(
                    file_rel, f"{path_prefix}.primary_decision",
                    f"'{SYSTEM_SCREENING_INITIALIZER_ACTOR}' is a purely technical actor and must never "
                    "record a decision other than 'pending' -- it has no scientific screening mandate "
                    "(see ADR-0057)",
                )
            if entry.get("stage") != "deduplication":
                report.error(
                    file_rel, f"{path_prefix}.stage",
                    f"'{SYSTEM_SCREENING_INITIALIZER_ACTOR}' may only initialize records at stage "
                    "'deduplication' (see ADR-0057)",
                )
            if entry.get("full_text_status") != "not_yet_obtained":
                report.error(
                    file_rel, f"{path_prefix}.full_text_status",
                    f"'{SYSTEM_SCREENING_INITIALIZER_ACTOR}' entries must use full_text_status "
                    "'not_yet_obtained' (see ADR-0057)",
                )
            if entry.get("duplicate_of") is not None or entry.get("primary_duplicate_of") is not None:
                report.error(
                    file_rel, f"{path_prefix}.duplicate_of",
                    f"'{SYSTEM_SCREENING_INITIALIZER_ACTOR}' must never record a duplicate reference "
                    "(see ADR-0057)",
                )
            if entry.get("second_review") is not None:
                report.error(
                    file_rel, f"{path_prefix}.second_review",
                    f"'{SYSTEM_SCREENING_INITIALIZER_ACTOR}' entries must never carry a second_review "
                    "(see ADR-0057)",
                )

        if derive_workflow_state(data) != WORKFLOW_STATE_SYSTEM_INITIALIZED:
            continue

        if data.get("canonical_source_id") is not None:
            report.error(
                file_rel, "$.canonical_source_id",
                "must stay null while the current effective screener is still the technical system "
                "actor (see ADR-0057)",
            )

        candidate_manifest_id = data.get("candidate_manifest_id")
        candidate_id = data.get("candidate_id")
        if not candidate_manifest_id or not candidate_id:
            continue
        manifest = candidate_manifests.get(candidate_manifest_id)
        if manifest is None:
            continue  # already reported by check_screening_candidate_references
        candidate_entry = next(
            (c for c in manifest.data.get("candidates") or [] if c.get("candidate_id") == candidate_id), None,
        )
        if candidate_entry is None:
            continue  # already reported by check_screening_candidate_references
        expected_title = derive_candidate_title(manifest.data.get("database"), candidate_entry.get("metadata") or {})
        if expected_title is not None and data.get("candidate_title") != expected_title:
            report.error(
                file_rel, "$.candidate_title",
                "does not match the title derived from the referenced candidate manifest metadata, "
                "while the technical system actor is still the current effective screener (see ADR-0057)",
            )


def check_screening_candidate_uniqueness(
    report: Report, objects: dict[str, dict[str, ResearchObject]]
) -> None:
    """ADR-0057: hoechstens ein Screening Record je (candidate_manifest_id, candidate_id)-Paar --
    ein Discovery-Kandidat darf nicht mehrfach als Screening Record repraesentiert werden.
    research/examples/** ist ausgenommen (dort gelten keine realen Kandidatenreferenzen)."""
    seen: dict[tuple[str, str], str] = {}
    for obj in objects["screening_record"].values():
        if "examples" in obj.path.parts:
            continue
        data = obj.data
        candidate_manifest_id = data.get("candidate_manifest_id")
        candidate_id = data.get("candidate_id")
        if not candidate_manifest_id or not candidate_id:
            continue
        key = (candidate_manifest_id, candidate_id)
        file_rel = relative(obj.path)
        if key in seen:
            report.error(
                file_rel, "$.candidate_id",
                f"duplicate screening record for candidate '{candidate_id}' in manifest "
                f"'{candidate_manifest_id}' -- already represented by {seen[key]}",
            )
        else:
            seen[key] = file_rel


def load_screening_initialization_manifest(
    report: Report, research_root: Path, registry, schemas
) -> dict:
    """Laedt und schema-validiert das rein technische Kontrollartefakt
    research/screening_status/initialization_manifest.yaml (siehe ADR-0057) -- KEIN
    RESEARCH_KINDS-Eintrag, KEIN wissenschaftliches Research-Objekt. Liefert {'protocols': []},
    wenn die Datei (noch) nicht existiert -- die Vollstaendigkeitspruefung greift dann fuer kein
    Protokoll (siehe check_screening_initialization_completeness)."""
    path = research_root / SCREENING_INITIALIZATION_MANIFEST_RELATIVE_PATH
    if not path.exists():
        return {"protocols": []}
    file_rel = relative(path)
    try:
        data = load_yaml_file(path)
    except DataFileError as exc:
        report.error(file_rel, "", str(exc))
        return {"protocols": []}
    if not data:
        return {"protocols": []}
    if not isinstance(data, dict):
        report.error(file_rel, "", "top-level YAML content must be a mapping")
        return {"protocols": []}

    validate_against_schema(
        report, file_rel, data, "research_screening_initialization_manifest.schema.json", registry, schemas,
    )

    seen_protocol_ids: dict[str, int] = {}
    for idx, entry in enumerate(data.get("protocols") or []):
        protocol_id = entry.get("protocol_id")
        if protocol_id in seen_protocol_ids:
            report.error(
                file_rel, f"$.protocols[{idx}].protocol_id",
                f"duplicate protocol_id '{protocol_id}' in screening initialization manifest, "
                f"already listed at index {seen_protocol_ids[protocol_id]}",
            )
        else:
            seen_protocol_ids[protocol_id] = idx

    return data


def check_screening_initialization_completeness(
    report: Report, objects: dict[str, dict[str, ResearchObject]], init_manifest: dict, research_root: Path,
) -> None:
    """ADR-0057: die Vollstaendigkeitsregel 'jeder Candidate eines Protokolls braucht einen
    Screening Record' greift ausschliesslich fuer Protokolle, die im Screening Initialization
    Manifest ausdruecklich als status: complete markiert sind -- ein teilweise laufender Import
    macht die CI dadurch nicht zwischenzeitlich rot (siehe Phase-4B-1B-1-Arbeitsauftrag). Prueft
    zusaetzlich, dass expected_candidate_count nicht stillschweigend veraltet ist (schuetzt vor
    einer 'complete'-Markierung, die nicht mehr zum aktuellen Datenbestand passt, z. B. weil
    nachtraeglich ein weiteres Candidate Manifest fuer dasselbe Protokoll hinzukam)."""
    file_rel = relative(research_root / SCREENING_INITIALIZATION_MANIFEST_RELATIVE_PATH)

    covered: set[tuple[str, str]] = set()
    for obj in objects["screening_record"].values():
        if "examples" in obj.path.parts:
            continue
        candidate_manifest_id = obj.data.get("candidate_manifest_id")
        candidate_id = obj.data.get("candidate_id")
        if candidate_manifest_id and candidate_id:
            covered.add((candidate_manifest_id, candidate_id))

    for entry in init_manifest.get("protocols") or []:
        if entry.get("status") != "complete":
            continue
        protocol_id = entry.get("protocol_id")
        manifests = [
            manifest for manifest in objects["candidate_manifest"].values()
            if manifest.data.get("protocol_id") == protocol_id
        ]
        actual_count = sum(manifest.data.get("candidate_count") or 0 for manifest in manifests)
        expected_count = entry.get("expected_candidate_count")
        if expected_count != actual_count:
            report.error(
                file_rel, "$.protocols[].expected_candidate_count",
                f"protocol '{protocol_id}' is marked complete with expected_candidate_count "
                f"{expected_count}, but its candidate manifests currently total {actual_count} "
                "candidates -- re-run tools/initialize_screening_records.py or correct the manifest",
            )
        for manifest in manifests:
            for candidate in manifest.data.get("candidates") or []:
                key = (manifest.id, candidate.get("candidate_id"))
                if key not in covered:
                    report.error(
                        file_rel, "$.protocols[]",
                        f"protocol '{protocol_id}' is marked complete, but candidate "
                        f"'{candidate.get('candidate_id')}' in candidate manifest '{manifest.id}' has no "
                        "screening record",
                    )


def check_object_temporal_bounds(report: Report, objects: dict[str, dict[str, ResearchObject]]) -> None:
    """ADR-0046: jedes von einem Research-Objekt SELBST dokumentierte Ereignisdatum muss innerhalb
    des Intervalls [created_at, updated_at] DIESES Objekts liegen -- ein Datensatz darf nicht
    angeblich vor einem Ereignis zuletzt aktualisiert worden sein, das er selbst speichert. Ergaenzt
    (unabhaengig von) check_misc_consistency (einfache created_at<=updated_at-Reihenfolge) und
    check_temporal_chain (Kette OBJEKTUEBERGREIFEND, ADR-0044) um die objektINTERNE Vollstaendigkeit
    dieser Prüfung.

    Konvention (siehe Scientific Research Protocol, Abschnitt 9d): created_at ist der Zeitpunkt, zu
    dem dieser Recherche-Datensatz (der Fall/Vorgang) angelegt wurde -- typischerweise VOR den darin
    dokumentierten Ereignissen (ein Screening-Datensatz wird angelegt, sobald ein Kandidat gefunden
    wurde, die eigentliche Entscheidung folgt spaeter). updated_at ist der Zeitpunkt der letzten
    Bearbeitung und muss daher mindestens so aktuell sein wie jedes im Datensatz gespeicherte
    Ereignisdatum. Gilt einheitlich fuer alle fuenf Research-Objektarten -- kein objektspezifisches
    abweichendes Datumsmodell."""
    for obj in objects["screening_record"].values():
        file_rel = relative(obj.path)
        data = obj.data
        created_at = data.get("created_at")
        updated_at = data.get("updated_at")
        for idx, entry in enumerate(data.get("decision_history") or []):
            label = f"decision_history[{idx}]"
            decided_at = entry.get("decided_at")
            _check_date_order(report, file_rel, f"created_at/{label}.decided_at", created_at, decided_at)
            _check_date_order(report, file_rel, f"{label}.decided_at/updated_at", decided_at, updated_at)

            second_review = entry.get("second_review") or {}
            reviewed_at = second_review.get("reviewed_at")
            if reviewed_at:
                _check_date_order(
                    report, file_rel, f"created_at/{label}.second_review.reviewed_at", created_at, reviewed_at
                )
                _check_date_order(
                    report, file_rel, f"{label}.second_review.reviewed_at/updated_at", reviewed_at, updated_at
                )

            resolved_at = (second_review.get("adjudication") or {}).get("resolved_at")
            if resolved_at:
                _check_date_order(
                    report, file_rel, f"created_at/{label}.second_review.adjudication.resolved_at",
                    created_at, resolved_at,
                )
                _check_date_order(
                    report, file_rel, f"{label}.second_review.adjudication.resolved_at/updated_at",
                    resolved_at, updated_at,
                )

    for obj in objects["extraction_record"].values():
        file_rel = relative(obj.path)
        data = obj.data
        created_at = data.get("created_at")
        updated_at = data.get("updated_at")
        extracted_at = data.get("extracted_at")
        verified_at = data.get("verified_at")
        _check_date_order(report, file_rel, "created_at/extracted_at", created_at, extracted_at)
        _check_date_order(report, file_rel, "extracted_at/updated_at", extracted_at, updated_at)
        if verified_at:
            _check_date_order(report, file_rel, "verified_at/updated_at", verified_at, updated_at)

    for obj in objects["promotion_record"].values():
        file_rel = relative(obj.path)
        data = obj.data
        created_at = data.get("created_at")
        updated_at = data.get("updated_at")
        last_reviewed_at = (data.get("review") or {}).get("last_reviewed_at")
        if last_reviewed_at:
            _check_date_order(report, file_rel, "created_at/review.last_reviewed_at", created_at, last_reviewed_at)
            _check_date_order(report, file_rel, "review.last_reviewed_at/updated_at", last_reviewed_at, updated_at)

    for obj in objects["search_run"].values():
        file_rel = relative(obj.path)
        data = obj.data
        created_at = data.get("created_at")
        updated_at = data.get("updated_at")
        executed_date = (data.get("executed_at") or "")[:10] or None
        if executed_date:
            _check_date_order(report, file_rel, "created_at/executed_at", created_at, executed_date)
            _check_date_order(report, file_rel, "executed_at/updated_at", executed_date, updated_at)

    for obj in objects["protocol"].values():
        file_rel = relative(obj.path)
        data = obj.data
        created_at = data.get("created_at")
        updated_at = data.get("updated_at")
        last_reviewed_at = (data.get("review") or {}).get("last_reviewed_at")
        if last_reviewed_at:
            _check_date_order(report, file_rel, "created_at/review.last_reviewed_at", created_at, last_reviewed_at)
            _check_date_order(report, file_rel, "review.last_reviewed_at/updated_at", last_reviewed_at, updated_at)


def check_no_unwanted_binaries(report: Report, root: Path) -> None:
    if not root.exists():
        return
    for path in root.rglob("*"):
        rel_parts = path.relative_to(root).parts
        if rel_parts and rel_parts[0] == "raw":
            continue  # research/raw/** ist expliziter, nicht validierter lokaler Arbeitsbereich
        if path.is_file() and path.suffix.lower() in UNWANTED_BINARY_SUFFIXES:
            report.error(relative(path), "", "unexpected binary file inside a versioned research/ directory")


def run_checks(report: Report, objects: dict[str, dict[str, ResearchObject]], source_ids, study_ids, claim_ids) -> None:
    check_research_references(report, objects, source_ids, study_ids)
    check_search_result_manifests(report, objects)
    check_search_run_interface_profiles(report, objects)
    check_candidate_manifests(report, objects)
    check_screening_candidate_references(report, objects)
    check_screening_related_records(report, objects)
    check_screening_system_actor_invariants(report, objects)
    check_screening_candidate_uniqueness(report, objects)
    check_historical_duplicate_targets(report, objects)
    check_protocol_version_matches_id(report, objects["protocol"])
    check_deduplication(report, objects)
    check_decision_history(report, objects, objects["search_run"])
    check_extraction_verification(report, objects)
    check_temporal_chain(report, objects)
    check_object_temporal_bounds(report, objects)
    check_promotion_records(report, objects, claim_ids)
    check_misc_consistency(report, objects)


def run_validation(
    verbose: bool, research_root: Path = RESEARCH_DIR, data_root: Path = DATA_DIR
) -> Report:
    report = Report()
    registry, schemas = build_schema_registry()
    vocabularies = load_all_research_vocabularies()

    check_no_unwanted_binaries(report, research_root)

    source_ids, study_ids, claim_ids = load_canonical_reference_sets(data_root)

    objects = load_research_dataset(research_root, report, registry, schemas, vocabularies)
    run_checks(report, objects, source_ids, study_ids, claim_ids)

    # Wie check_screening_initialization_completeness unten bewusst NICHT Teil von run_checks und
    # daher nur EINMAL fuer die Produktionsdaten aufgerufen, nicht zusaetzlich fuer
    # research/examples/**: die Pflichtregistrierung von system-screening-initializer/cso-chatgpt
    # ist eine Tatsache ueber reale Produktionsakteure, keine allgemeine, auch auf Fixture-/
    # Beispieldaten anwendbare Strukturregel (siehe ADR-0059).
    check_research_reviewers(report, objects)

    init_manifest = load_screening_initialization_manifest(report, research_root, registry, schemas)
    check_screening_initialization_completeness(report, objects, init_manifest, research_root)

    examples_root = research_root / "examples"
    example_objects = load_research_dataset(examples_root, report, registry, schemas, vocabularies)
    run_checks(report, example_objects, source_ids, study_ids, claim_ids)

    if verbose:
        for kind in RESEARCH_KINDS:
            print(
                f"Loaded: {len(objects[kind])} {kind}(s) (production), "
                f"{len(example_objects[kind])} (examples)"
            )

    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--verbose", action="store_true", help="Zusaetzliche Kontextinformationen ausgeben")
    args = parser.parse_args(argv)

    report = run_validation(verbose=args.verbose)

    for issue in report.issues:
        print(issue.format())

    print()
    print(f"{report.error_count} error(s), {report.warning_count} warning(s)")

    return 1 if report.error_count else 0


if __name__ == "__main__":
    raise SystemExit(main())

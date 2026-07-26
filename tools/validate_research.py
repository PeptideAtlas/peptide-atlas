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
  _claim_id gegen die jeweilige kanonische Datenebene.
- Protokollkonsistenz: Version/ID-Suffix, Suchlauf nur gegen approved/superseded-Protokolle,
  Suchlauf-Datenbank muss in protocol.planned_information_sources[] freigegeben sein,
  protokoll-uebergreifende Konsistenz zwischen search_run/screening_record/extraction_record,
  duplicate_of bleibt innerhalb desselben Protokolls (inkl. gesamter Kette).
- Deduplizierung: echte normalisierte DOI/PMID/PMCID/NCT-ID/ISBN-Kollisionserkennung.
- Screening-Workflow: JEDER decision_history-Eintrag (nicht nur der aktuelle Zustand) wird
  gegen dieselben Invarianten geprueft -- Stufe im Protokoll vorgesehen, Stage-/Decision-Matrix
  (ADR-0043), Dual-Reviewer-Pflicht, Reviewer-/Adjudikator-Unabhaengigkeit, konsistente
  primary_decision/reviewer_decision/decision_confirmed/adjudication-Semantik (ADR-0043),
  Volltextvollstaendigkeit, Datumsreihenfolge (inkl. gegen JEDEN referenzierten Suchlauf).
  Extraktion ist nur fuer einen screening_record zulaessig, dessen Einschluss terminal
  (decision_stage: final), vollstaendig volltextgeprueft und frei von ungeloesten
  Zweitpruefungskonflikten ist.
- Extraktionsverifikation: verified_by != extracted_by wird IMMER erzwungen, sobald
  extraction_status: verified (siehe ADR-0040) -- keine protokollabhaengige Ausnahme mehr.
- Zeitliche Provenienzkette (ADR-0044): terminale Screening-Entscheidung/-Zweitpruefung/
  -Adjudikation <= extracted_at <= verified_at <= promotion.created_at/review.last_reviewed_at
  <= promotion.updated_at.
- Claim-Promotion: vollstaendige Kettenpruefung inkl. claim_promotion_policy.requires_second_review
  (mindestens zwei unterschiedliche, nicht-leere Reviewer bei approved_for_creation/promoted;
  Eindeutigkeit/Nicht-Leerheit selbst ist schema-seitig erzwungen, siehe
  research_promotion_record.schema.json).
- Sonstige Konsistenz: Eindeutigkeit, Datumsreihenfolge, sichere export_reference.
- Dateiebene: keine unerwuenschten Binaerdateien, research/examples/** als eigener Namensraum.

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
    DEDUPLICATION_IDENTIFIER_FIELDS,
    NORMALIZERS,
    RESEARCH_DIR,
    RESEARCH_KIND_TO_SCHEMA_ID,
    SCREENING_STAGE_ORDER,
    iter_research_files,
    load_all_research_vocabularies,
    normalize_url,
)

UNWANTED_BINARY_SUFFIXES = {
    ".exe", ".dll", ".so", ".bin", ".zip", ".7z", ".tar", ".gz",
    ".png", ".jpg", ".jpeg", ".gif", ".pdf", ".doc", ".docx", ".xls", ".xlsx",
    ".ris", ".bib", ".csv",
}

RESEARCH_KINDS = ("protocol", "search_run", "screening_record", "extraction_record", "promotion_record")

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

    for kind in ("search_run", "screening_record", "extraction_record"):
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


def check_deduplication(report: Report, objects: dict[str, dict[str, ResearchObject]]) -> None:
    """Erkennt Kandidaten mit identischem normalisiertem stabilem Identifikator innerhalb
    desselben Protokolls, die nicht als decision: duplicate markiert sind. Kollisionen ueber
    verschiedene Protokolle hinweg sind erlaubt (dieselbe Publikation kann in mehreren Reviews
    vorkommen). URL-Kollisionen sind nur eine Warnung (Redirects/Mirrors, siehe
    tools/_datalib.py::normalize_url)."""
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

        for (field, normalized), group in identifier_map.items():
            active = [o for o in group if o.data.get("decision") in ACTIVE_SCREENING_DECISIONS]
            if len(active) >= 2:
                ids = ", ".join(sorted(o.id for o in active))
                for o in active:
                    report.error(
                        relative(o.path), f"$.candidate_identifiers.{field}",
                        f"duplicate {field} '{normalized}' shared with other active (non-duplicate-marked) "
                        f"screening record(s) under the same protocol: {ids} -- mark all but one as "
                        "decision: duplicate with duplicate_of pointing to the primary record",
                    )

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


def _check_decision_snapshot(
    report: Report,
    file_rel: str,
    protocol: ResearchObject | None,
    protocol_id: str | None,
    entry: dict,
    entry_label: str,
) -> None:
    """Prueft EINEN Entscheidungs-Snapshot (einen decision_history[]-Eintrag) gegen die
    vollstaendigen Workflow-Invarianten. Da die Top-Level-Felder eine geprueft konsistente
    Projektion der EFFEKTIVEN Werte des LETZTEN decision_history-Eintrags sind (siehe
    check_decision_history), deckt der Aufruf dieser Funktion fuer JEDEN Eintrag automatisch auch
    den aktuellen Zustand ab. Trennt strukturell primary_decision (Erstentscheidung, bleibt bei
    einem ungeloesten Widerspruch als decision: uncertain erhalten) von decision (effektiver,
    ggf. adjudizierter Zustand) -- siehe ADR-0043."""
    stage = entry.get("stage")
    primary_decision = entry.get("primary_decision")
    decision = entry.get("decision")
    decided_by = entry.get("decided_by")
    decided_at = entry.get("decided_at")
    full_text_status = entry.get("full_text_status")
    second_review = entry.get("second_review")

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

    if stage in dual_reviewer_stages and primary_decision in ("include", "exclude") and second_review is None:
        report.error(
            file_rel, f"{entry_label}.second_review",
            f"stage '{stage}' is a dual-reviewer stage for protocol '{protocol_id}' -- a primary "
            f"'{primary_decision}' decision requires second_review",
        )

    if second_review:
        reviewed_by = second_review.get("reviewed_by")
        if reviewed_by == decided_by:
            report.error(
                file_rel, f"{entry_label}.second_review.reviewed_by",
                "second_review.reviewed_by must differ from the primary reviewer (reviewer independence)",
            )

        reviewer_decision = second_review.get("reviewer_decision")
        decision_confirmed = second_review.get("decision_confirmed")
        decisions_agree = reviewer_decision == primary_decision
        if decision_confirmed != decisions_agree:
            report.error(
                file_rel, f"{entry_label}.second_review.decision_confirmed",
                f"decision_confirmed ({decision_confirmed!r}) is inconsistent with whether reviewer_decision "
                f"('{reviewer_decision}') actually agrees with the PRIMARY decision ('{primary_decision}') -- "
                "decision_confirmed must be a validated projection of that comparison, not of the effective "
                "decision",
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

    if stage in FULL_TEXT_REQUIRING_STAGES and decision == "include" and full_text_status != "obtained":
        report.error(
            file_rel, f"{entry_label}.full_text_status",
            f"stage '{stage}' with decision 'include' requires full_text_status 'obtained', got "
            f"'{full_text_status}'",
        )


def check_decision_history(
    report: Report, objects: dict[str, dict[str, ResearchObject]], search_runs: dict[str, ResearchObject]
) -> None:
    protocols = objects["protocol"]
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

            _check_decision_snapshot(report, file_rel, protocol, protocol_id, entry, entry_label)

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
        if promotion_status in ("approved_for_creation", "promoted"):
            protocol = protocols.get(data.get("protocol_id"))
            requires_second_review = bool(
                protocol is not None
                and (protocol.data.get("claim_promotion_policy") or {}).get("requires_second_review")
            )
            if requires_second_review:
                # Eindeutigkeit und Nicht-Leerheit der einzelnen Kuerzel sind bereits
                # schema-seitig erzwungen (uniqueItems + Nicht-Leerzeichen-Pattern, siehe
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


def _check_export_reference_safety(report: Report, file_rel: str, export_reference: str | None) -> None:
    if not export_reference:
        return
    if "://" in export_reference:
        report.error(
            file_rel, "$.export_reference",
            "must not be a URL -- only a relative path hint under research/raw/ is allowed",
        )
        return
    if export_reference.startswith("/") or export_reference.startswith("\\") or re.match(r"^[a-zA-Z]:[\\/]", export_reference):
        report.error(file_rel, "$.export_reference", "must be a relative path, not an absolute path")
        return
    normalized = export_reference.replace("\\", "/")
    if ".." in normalized.split("/"):
        report.error(file_rel, "$.export_reference", "must not contain '..' path segments")
        return
    if not normalized.lstrip("./").startswith("research/raw/"):
        report.error(file_rel, "$.export_reference", "must point to a path under research/raw/")


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
        _check_unique(report, file_rel, "$.screening_policy.stages", screening_policy.get("stages") or [])
        _check_unique(
            report, file_rel, "$.screening_policy.dual_reviewer_stages",
            screening_policy.get("dual_reviewer_stages") or [],
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
    check_protocol_version_matches_id(report, objects["protocol"])
    check_deduplication(report, objects)
    check_decision_history(report, objects, objects["search_run"])
    check_extraction_verification(report, objects)
    check_temporal_chain(report, objects)
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

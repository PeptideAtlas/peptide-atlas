#!/usr/bin/env python3
"""Deterministisches Initialisierungswerkzeug fuer research_screening_record (siehe ADR-0057,
Phase-4B-1B-1-Arbeitsauftrag).

Erzeugt fuer jeden Discovery-Kandidaten eines research_candidate_manifest genau einen rein
administrativen, noch nicht wissenschaftlich gescreenten research_screening_record -- KEINE
Relevanzentscheidung, KEINE Evidenzbewertung, KEINE Extraktion, KEINE Promotion. Liest
ausschliesslich bereits versionierte Candidate Manifests (research/candidates/**), fuehrt KEINE
Netzwerkzugriffe durch und veraendert bestehende Screening Records niemals still -- ein erneuter
Lauf mit unveraenderten Eingaben erzeugt exakt denselben Output (Idempotenz) und erhaelt
bestehende screening-record-<uuid4>-IDs.

    python tools/initialize_screening_records.py --protocol-id research-protocol-retatrutide-v1

Jeder erzeugte Screening Record dokumentiert nur die technische Initialisierung
(screened_by/decision_history[].decided_by: system-screening-initializer, decision: pending,
decision_stage: deduplication) und trifft NIE eine wissenschaftliche Entscheidung
(validate_research.py::check_screening_system_actor_invariants erzwingt das strukturell). Zwei
Abweichungen vom woertlichen Arbeitsauftrag, beide durch das bestehende, bereits vor Phase 4B-1B-1
etablierte Screening-Schema erzwungen und im Decision Log (ADR-0057) dokumentiert:

- decision_stage ist 'deduplication', nicht das im Arbeitsauftrag genannte 'title_abstract':
  tools/_researchlib.py::ALLOWED_DECISIONS_BY_STAGE erlaubt 'pending' ausschliesslich an Stufe
  'deduplication' (der Ausgangszustand vor jeder inhaltlichen Sichtung); 'title_abstract' verlangt
  bereits eine inhaltliche Entscheidung (include/exclude/awaiting_full_text/uncertain), die die
  rein technische Initialisierung nicht treffen darf und auch fachlich nicht treffen sollte.
- full_text_status ist 'not_yet_obtained', nicht das im Arbeitsauftrag genannte 'not_requested':
  dieser Wert existiert nicht im kontrollierten Vokabular (research/vocabularies/
  full_text_statuses.yaml: not_applicable/not_yet_obtained/obtained/restricted_access/
  unavailable); 'not_yet_obtained' ("Noch nicht beschafft") ist die naechstliegende korrekte
  Entsprechung.

candidate_title wird NIE erfunden: PubMed nutzt metadata.title, ClinicalTrials.gov
metadata.brief_title (ersatzweise metadata.official_title) -- siehe
tools/_researchlib.py::derive_candidate_title. Fehlt der zulaessige Titel (bei ClinicalTrials.gov:
fehlen beide Titelfelder), wird NUR dieser eine Kandidat als Datenfehler in der Zusammenfassung
gemeldet und nicht initialisiert (kein Platzhalter) -- der Lauf wird dafuer nicht insgesamt
abgebrochen, damit ein einzelner defekter Kandidat nicht die Initialisierung aller uebrigen
blockiert.

candidate_source_type ist je Datenbank ein einzelner, neutraler, bereits im kontrollierten
Vokabular vorhandener Wert (tools/_researchlib.py::CANDIDATE_SOURCE_TYPE_BY_DATABASE: pubmed ->
peer_reviewed_publication, clinicaltrials_gov -> trial_registry) -- keine feinere Ableitung aus
PubMed publication_types (z. B. 'Review' -> systematic_review), das waere selbst schon eine
wissenschaftliche Einordnung, die der rein technischen Initialisierung nicht zusteht. Eine
Datenbank ohne Eintrag in dieser Zuordnung ist eine Modellierungsluecke -- der betroffene
Kandidat wird als Fehler gemeldet, nicht mit einem erfundenen source_type initialisiert.

Nach einem vollstaendigen, fehler- und konfliktfreien Lauf aktualisiert das Werkzeug das rein
technische Kontrollartefakt research/screening_status/initialization_manifest.yaml auf
status: complete -- das schaltet die Vollstaendigkeitspruefung in validate_research.py
(check_screening_initialization_completeness) fuer dieses Protokoll erst dann scharf. Ein
partieller oder fehlerhafter Lauf schreibt status: in_progress, damit ein teilweise
durchgelaufener Import die CI nicht zwischenzeitlich rot macht.

Exitcode 0, wenn keine Fehler/Konflikte auftraten, sonst 1.
"""

from __future__ import annotations

import argparse
import sys
import uuid
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _datalib import load_yaml_file  # noqa: E402
from _researchlib import (  # noqa: E402
    CANDIDATE_SOURCE_TYPE_BY_DATABASE,
    RESEARCH_DIR,
    SYSTEM_SCREENING_INITIALIZER_ACTOR,
    derive_candidate_title,
)

CANDIDATES_DIR = RESEARCH_DIR / "candidates"
SCREENING_DIR = RESEARCH_DIR / "screening"
INITIALIZATION_MANIFEST_PATH = RESEARCH_DIR / "screening_status" / "initialization_manifest.yaml"

# Naechstliegender kontrollierter Wert zu "not_requested" (siehe Moduldocstring).
FULL_TEXT_STATUS_AT_INIT = "not_yet_obtained"
# Der Arbeitsauftrag verlangte decision_stage: title_abstract, aber
# _researchlib.py::ALLOWED_DECISIONS_BY_STAGE erlaubt 'pending' AUSSCHLIESSLICH an Stufe
# 'deduplication' ("der allererste Check auf Mehrfachfund ... 'pending' (noch nicht geprueft)") --
# 'title_abstract' verlangt bereits eine inhaltliche Entscheidung (include/exclude/
# awaiting_full_text/uncertain), die die rein technische Initialisierung nicht treffen darf. Diese
# Kombination ist zudem semantisch korrekter: "gerade entdeckt, noch ueberhaupt nicht gesichtet"
# IST der Ausgangszustand vor der Deduplizierung, nicht erst nach ihr. Siehe ADR-0057.
DECISION_STAGE_AT_INIT = "deduplication"

NAMESPACE_TO_IDENTIFIER_FIELD = {"pmid": "pmid", "nct_id": "nct_id"}


def _today() -> str:
    return date.today().isoformat()


def _dump_yaml(data: dict, path: Path) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        yaml.safe_dump(data, handle, sort_keys=False, default_flow_style=False, allow_unicode=True, width=100)


@dataclass
class Outcome:
    total_candidates: int = 0
    already_present: int = 0
    created: int = 0
    conflicts: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


def load_candidate_manifests(protocol_id: str) -> list[dict]:
    """Liest alle Candidate Manifests eines Protokolls (research/candidates/**) -- rein lesend,
    keine Netzwerkzugriffe, keine Aenderung der Discovery-Identitaet."""
    manifests: list[dict] = []
    if not CANDIDATES_DIR.exists():
        return manifests
    for path in sorted(CANDIDATES_DIR.glob("*.yaml")):
        data = load_yaml_file(path)
        if isinstance(data, dict) and data.get("protocol_id") == protocol_id:
            manifests.append(data)
    return manifests


def load_existing_screening_records() -> dict[tuple[str, str], list[tuple[Path, dict]]]:
    """Indiziert vorhandene Screening Records nach (candidate_manifest_id, candidate_id) --
    ausschliesslich fuer Idempotenz-/Konfliktpruefung, nie fuer stille Aenderungen. Mehr als ein
    Eintrag je Schluessel ist bereits selbst ein Konflikt (siehe initialize_protocol)."""
    index: dict[tuple[str, str], list[tuple[Path, dict]]] = {}
    if not SCREENING_DIR.exists():
        return index
    for path in sorted(SCREENING_DIR.glob("*.yaml")):
        data = load_yaml_file(path)
        if not isinstance(data, dict):
            continue
        candidate_manifest_id = data.get("candidate_manifest_id")
        candidate_id = data.get("candidate_id")
        if not candidate_manifest_id or not candidate_id:
            continue
        index.setdefault((candidate_manifest_id, candidate_id), []).append((path, data))
    return index


def build_screening_record(
    manifest: dict, candidate: dict, *, record_id: str, created_at: str,
) -> tuple[dict | None, str | None]:
    """Baut einen neuen Screening Record im administrativen Initialzustand. Liefert (None, Grund),
    statt einen Titel oder candidate_source_type zu erfinden, wenn einer von beiden nicht
    zulaessig ableitbar ist."""
    database = manifest.get("database")
    metadata = candidate.get("metadata") or {}

    title = derive_candidate_title(database, metadata)
    if title is None:
        return None, "no title derivable from candidate manifest metadata without fabricating one"

    source_type = CANDIDATE_SOURCE_TYPE_BY_DATABASE.get(database)
    if source_type is None:
        return None, (
            f"no candidate_source_type mapping exists for database '{database}' -- modelling gap, "
            "needs CSO review before a new mapping is added"
        )

    namespace = (candidate.get("primary_identifier") or {}).get("namespace")
    value = (candidate.get("primary_identifier") or {}).get("value")
    identifier_field = NAMESPACE_TO_IDENTIFIER_FIELD.get(namespace)
    if identifier_field is None:
        return None, f"unsupported primary_identifier namespace '{namespace}'"

    candidate_identifiers = {"doi": None, "pmid": None, "pmcid": None, "nct_id": None, "isbn": None, "url": None}
    candidate_identifiers[identifier_field] = value
    if database == "pubmed":
        candidate_identifiers["doi"] = metadata.get("doi")
        candidate_identifiers["pmcid"] = metadata.get("pmcid")

    search_run_ids = sorted(candidate.get("discovered_in_search_run_ids") or [])

    history_entry = {
        "sequence": 1,
        "stage": DECISION_STAGE_AT_INIT,
        "primary_decision": "pending",
        "primary_decision_reason": None,
        "decision": "pending",
        "decision_reason": None,
        "duplicate_of": None,
        "primary_duplicate_of": None,
        "decided_by": SYSTEM_SCREENING_INITIALIZER_ACTOR,
        "decided_at": created_at,
        "full_text_status": FULL_TEXT_STATUS_AT_INIT,
        "second_review": None,
    }

    record = {
        "schema_version": "1.0.0",
        "id": record_id,
        "protocol_id": manifest.get("protocol_id"),
        "search_run_ids": search_run_ids,
        "candidate_identifiers": candidate_identifiers,
        "candidate_title": title,
        "candidate_source_type": source_type,
        "decision": "pending",
        "decision_stage": DECISION_STAGE_AT_INIT,
        "decision_reason": None,
        "duplicate_of": None,
        "full_text_status": FULL_TEXT_STATUS_AT_INIT,
        "screened_by": SYSTEM_SCREENING_INITIALIZER_ACTOR,
        "screened_at": created_at,
        "second_review": None,
        "decision_history": [history_entry],
        "canonical_source_id": None,
        "candidate_manifest_id": manifest.get("id"),
        "candidate_id": candidate.get("candidate_id"),
        "created_at": created_at,
        "updated_at": created_at,
    }
    return record, None


def _existing_record_conflict(existing_data: dict, manifest: dict, candidate: dict) -> str | None:
    """Vergleicht einen bereits vorhandenen Screening Record gegen den aktuellen Candidate-
    Manifest-Zustand -- NUR die Herkunftsfelder, die sich nie legitim aendern duerfen. Absichtlich
    KEIN Titel-/Entscheidungsvergleich, sobald ein Mensch den Datensatz uebernommen hat
    (screened_by != system-screening-initializer): eine spaetere Titelkorrektur oder ein echtes
    Screening-Ergebnis ist kein Konflikt, sondern der erwartete redaktionelle Fortschritt."""
    expected_search_run_ids = sorted(candidate.get("discovered_in_search_run_ids") or [])
    actual_search_run_ids = sorted(existing_data.get("search_run_ids") or [])
    if expected_search_run_ids != actual_search_run_ids:
        return (
            f"existing screening record's search_run_ids {actual_search_run_ids} no longer matches "
            f"the candidate manifest's discovered_in_search_run_ids {expected_search_run_ids} "
            "(manifest changed after initialization?)"
        )
    if existing_data.get("screened_by") == SYSTEM_SCREENING_INITIALIZER_ACTOR:
        expected_title = derive_candidate_title(manifest.get("database"), candidate.get("metadata") or {})
        if expected_title is not None and existing_data.get("candidate_title") != expected_title:
            return (
                "existing (still pristine, system-initialized) screening record's candidate_title no "
                "longer matches the candidate manifest metadata"
            )
    return None


def load_initialization_manifest() -> dict:
    if not INITIALIZATION_MANIFEST_PATH.exists():
        return {"schema_version": "1.0.0", "protocols": []}
    data = load_yaml_file(INITIALIZATION_MANIFEST_PATH)
    if not isinstance(data, dict):
        return {"schema_version": "1.0.0", "protocols": []}
    data.setdefault("schema_version", "1.0.0")
    data.setdefault("protocols", [])
    return data


def update_initialization_manifest(protocol_id: str, *, status: str, expected_count: int, today: str) -> None:
    manifest = load_initialization_manifest()
    protocols = manifest["protocols"]
    entry = next((p for p in protocols if p.get("protocol_id") == protocol_id), None)
    if entry is None:
        entry = {"protocol_id": protocol_id, "notes": None}
        protocols.append(entry)
    entry["status"] = status
    entry["expected_candidate_count"] = expected_count
    entry["initialized_by"] = SYSTEM_SCREENING_INITIALIZER_ACTOR
    entry["completed_at"] = today if status == "complete" else None
    entry.setdefault("notes", None)
    protocols.sort(key=lambda p: p["protocol_id"])
    INITIALIZATION_MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    _dump_yaml(manifest, INITIALIZATION_MANIFEST_PATH)


def initialize_protocol(protocol_id: str) -> Outcome:
    outcome = Outcome()
    manifests = load_candidate_manifests(protocol_id)
    existing = load_existing_screening_records()
    today = _today()

    for manifest in manifests:
        for candidate in manifest.get("candidates") or []:
            outcome.total_candidates += 1
            key = (manifest["id"], candidate["candidate_id"])
            entries = existing.get(key, [])

            if len(entries) > 1:
                outcome.conflicts.append(
                    f"candidate '{candidate['candidate_id']}' in manifest '{manifest['id']}' is already "
                    f"represented by {len(entries)} screening records: "
                    f"{', '.join(str(p.relative_to(RESEARCH_DIR.parent)) for p, _ in entries)}"
                )
                continue

            if len(entries) == 1:
                _, existing_data = entries[0]
                conflict = _existing_record_conflict(existing_data, manifest, candidate)
                if conflict:
                    outcome.conflicts.append(
                        f"candidate '{candidate['candidate_id']}' in manifest '{manifest['id']}': {conflict}"
                    )
                else:
                    outcome.already_present += 1
                continue

            record, error_reason = build_screening_record(
                manifest, candidate, record_id=f"screening-record-{uuid.uuid4()}", created_at=today,
            )
            if record is None:
                outcome.errors.append(
                    f"candidate '{candidate['candidate_id']}' in manifest '{manifest['id']}': {error_reason}"
                )
                continue

            SCREENING_DIR.mkdir(parents=True, exist_ok=True)
            _dump_yaml(record, SCREENING_DIR / f"{record['id']}.yaml")
            outcome.created += 1

    complete = (
        not outcome.errors
        and not outcome.conflicts
        and (outcome.already_present + outcome.created) == outcome.total_candidates
    )
    update_initialization_manifest(
        protocol_id, status="complete" if complete else "in_progress",
        expected_count=outcome.total_candidates, today=today,
    )
    return outcome


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--protocol-id", required=True, help="z. B. research-protocol-retatrutide-v1")
    args = parser.parse_args(argv)

    outcome = initialize_protocol(args.protocol_id)

    print(f"Kandidaten gesamt: {outcome.total_candidates}")
    print(f"Bereits vorhanden: {outcome.already_present}")
    print(f"Neu erzeugt:       {outcome.created}")
    print(f"Konflikte:         {len(outcome.conflicts)}")
    print(f"Fehler:            {len(outcome.errors)}")
    for message in outcome.conflicts:
        print(f"  KONFLIKT: {message}")
    for message in outcome.errors:
        print(f"  FEHLER:   {message}")

    return 1 if (outcome.errors or outcome.conflicts) else 0


if __name__ == "__main__":
    raise SystemExit(main())

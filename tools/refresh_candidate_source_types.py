#!/usr/bin/env python3
"""Separates, explizites Migrations-/Refresh-Werkzeug fuer research_screening_record.
candidate_source_type (siehe ADR-0058, Phase 4B-1B-2, Abschnitt 4.5).

Verfeinert den bei der Initialisierung (ADR-0057, tools/initialize_screening_records.py) je
Datenbank gesetzten, einzelnen neutralen candidate_source_type (z. B. 'peer_reviewed_publication'
fuer PubMed) anhand der bereits versionierten PubMed-publication_types-Metadaten im jeweiligen
Candidate Manifest -- rein technisch, deterministisch, NIEMALS eine wissenschaftliche Entscheidung.
Bewusst ein EIGENSTAENDIGES Werkzeug, nicht Teil von initialize_screening_records.py: dieses
veraendert bestehende Screening Records nie still (siehe dessen Docstring), waehrend dieses
Werkzeug genau das -- kontrolliert, mit Dry-Run als Standard -- tut.

    python tools/refresh_candidate_source_types.py --protocol-id research-protocol-retatrutide-v1
        Dry-Run (Standard): zeigt fuer jeden betroffenen Screening Record den Vorschlag, ohne eine
        Datei zu aendern.

    python tools/refresh_candidate_source_types.py --protocol-id <id> --apply
        Wendet ausschliesslich die als 'proposed' eingestuften Aenderungen an (siehe unten) --
        aktualisiert NUR candidate_source_type und updated_at, keine anderen Felder,
        insbesondere KEINEN decision_history-Eintrag (candidate_source_type ist kein Teil von
        decision_history[], siehe research_screening_record.schema.json) und KEINE
        wissenschaftliche Entscheidung.

Ein Kandidat wird in genau eine der folgenden Kategorien eingeordnet (Konfliktbericht):

- 'proposed': aktueller Wert entspricht noch dem generischen Datenbank-Default aus
  tools/_researchlib.py::CANDIDATE_SOURCE_TYPE_BY_DATABASE, UND die Ableitung aus
  publication_types (tools/_researchlib.py::derive_source_type_from_pubmed_publication_types)
  liefert einen abweichenden, praeziseren Wert -- sicher automatisierbar.
- 'already_matches': Ableitung stimmt bereits mit dem aktuellen Wert ueberein -- nichts zu tun.
- 'conflict': aktueller Wert weicht bereits vom generischen Datenbank-Default ab (jemand/etwas hat
  ihn bereits gezielt gesetzt) UND die Ableitung schlaegt einen ANDEREN Wert vor -- wird NIE
  automatisch ueberschrieben, erscheint nur im Bericht fuer manuelle Pruefung.
- 'skipped_human_reviewed': der Bearbeitungszustand (_researchlib.derive_workflow_state) ist nicht
  mehr 'system_initialized' -- ein Mensch hat den Datensatz bereits uebernommen, dieses Werkzeug
  fasst menschlich bearbeitete Datensaetze grundsaetzlich nicht an.
- 'skipped_no_candidate_reference' / 'skipped_non_pubmed' / 'skipped_metadata_not_fetched' /
  'skipped_no_derivation': technische Gruende, warum keine Ableitung moeglich ist.

Keine automatische wissenschaftliche Entscheidung, keine Migration der 197 bestehenden Retatrutide-
Records in irgendeinem PR, der dieses Werkzeug nur hinzufuegt (ein tatsaechlicher --apply-Lauf ist
eine separate, hier nicht implizit mitgenommene redaktionelle Entscheidung, siehe PR-Bericht)."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _datalib import load_yaml_file  # noqa: E402
from _researchlib import (  # noqa: E402
    CANDIDATE_SOURCE_TYPE_BY_DATABASE,
    RESEARCH_DIR,
    WORKFLOW_STATE_SYSTEM_INITIALIZED,
    derive_source_type_from_pubmed_publication_types,
    derive_workflow_state,
    iter_research_files,
)


def _today() -> str:
    return date.today().isoformat()


def _dump_yaml(data: dict, path: Path) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        yaml.safe_dump(data, handle, sort_keys=False, default_flow_style=False, allow_unicode=True, width=100)


@dataclass
class Outcome:
    proposed: list[tuple[str, str, str]] = field(default_factory=list)  # (id, current, derived)
    already_matches: list[str] = field(default_factory=list)
    conflicts: list[tuple[str, str, str]] = field(default_factory=list)  # (id, current, derived)
    skipped_human_reviewed: list[str] = field(default_factory=list)
    skipped_no_candidate_reference: list[str] = field(default_factory=list)
    skipped_non_pubmed: list[str] = field(default_factory=list)
    skipped_metadata_not_fetched: list[str] = field(default_factory=list)
    skipped_no_derivation: list[str] = field(default_factory=list)
    applied: list[str] = field(default_factory=list)


def _load_candidate_manifests(protocol_id: str) -> dict[str, dict]:
    manifests = {}
    for path in iter_research_files(RESEARCH_DIR, "candidate_manifest"):
        data = load_yaml_file(path)
        if data.get("protocol_id") == protocol_id:
            manifests[data["id"]] = data
    return manifests


def refresh(protocol_id: str, apply: bool) -> Outcome:
    outcome = Outcome()
    manifests = _load_candidate_manifests(protocol_id)

    screening_paths = sorted(
        (p for p in iter_research_files(RESEARCH_DIR, "screening_record")), key=lambda p: p.name
    )
    for path in screening_paths:
        data = load_yaml_file(path)
        if data.get("protocol_id") != protocol_id:
            continue
        record_id = data["id"]

        candidate_manifest_id = data.get("candidate_manifest_id")
        candidate_id = data.get("candidate_id")
        if not candidate_manifest_id or not candidate_id:
            outcome.skipped_no_candidate_reference.append(record_id)
            continue

        manifest = manifests.get(candidate_manifest_id)
        if manifest is None:
            outcome.skipped_no_candidate_reference.append(record_id)
            continue

        database = manifest.get("database")
        if database != "pubmed":
            outcome.skipped_non_pubmed.append(record_id)
            continue

        candidate = next(
            (c for c in manifest.get("candidates") or [] if c.get("candidate_id") == candidate_id), None,
        )
        if candidate is None or candidate.get("metadata_status") != "fetched":
            outcome.skipped_metadata_not_fetched.append(record_id)
            continue

        if derive_workflow_state(data) != WORKFLOW_STATE_SYSTEM_INITIALIZED:
            outcome.skipped_human_reviewed.append(record_id)
            continue

        publication_types = (candidate.get("metadata") or {}).get("publication_types") or []
        derived = derive_source_type_from_pubmed_publication_types(publication_types)
        if derived is None:
            outcome.skipped_no_derivation.append(record_id)
            continue

        current = data.get("candidate_source_type")
        if derived == current:
            outcome.already_matches.append(record_id)
            continue

        database_default = CANDIDATE_SOURCE_TYPE_BY_DATABASE.get(database)
        if current != database_default:
            outcome.conflicts.append((record_id, current, derived))
            continue

        outcome.proposed.append((record_id, current, derived))
        if apply:
            data["candidate_source_type"] = derived
            data["updated_at"] = _today()
            _dump_yaml(data, path)
            outcome.applied.append(record_id)

    return outcome


def _print_report(outcome: Outcome, apply: bool) -> None:
    print(f"Mode: {'APPLY' if apply else 'DRY-RUN (pass --apply to write changes)'}")
    print()
    print(f"proposed: {len(outcome.proposed)}")
    for record_id, current, derived in sorted(outcome.proposed):
        marker = "applied" if record_id in outcome.applied else "not applied (dry-run)"
        print(f"  {record_id}: '{current}' -> '{derived}' ({marker})")
    print(f"already_matches: {len(outcome.already_matches)}")
    print(f"conflicts (never auto-applied, needs manual review): {len(outcome.conflicts)}")
    for record_id, current, derived in sorted(outcome.conflicts):
        print(f"  {record_id}: current '{current}' already differs from the database default, "
              f"but derivation suggests '{derived}'")
    print(f"skipped_human_reviewed: {len(outcome.skipped_human_reviewed)}")
    print(f"skipped_no_candidate_reference: {len(outcome.skipped_no_candidate_reference)}")
    print(f"skipped_non_pubmed: {len(outcome.skipped_non_pubmed)}")
    print(f"skipped_metadata_not_fetched: {len(outcome.skipped_metadata_not_fetched)}")
    print(f"skipped_no_derivation: {len(outcome.skipped_no_derivation)}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--protocol-id", required=True, help="z. B. research-protocol-retatrutide-v1")
    parser.add_argument(
        "--apply", action="store_true",
        help="Schreibt die als 'proposed' eingestuften Aenderungen tatsaechlich (Standard: Dry-Run).",
    )
    args = parser.parse_args(argv)

    outcome = refresh(args.protocol_id, args.apply)
    _print_report(outcome, args.apply)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Validiert die Recherche-/Provenienzebene von Peptide Atlas (research/**).

Laeuft GETRENNT vom kanonischen Datenvalidator (tools/validate_data.py) -- research/**
ist Provenienz- und Arbeitsebene, kein kanonisches Wissen (siehe ADR-0033 im Decision Log)
und fliesst nicht in build/catalog.json oder build/graph.json ein. Dieser Validator prueft
aber Querverweise auf die kanonische Datenebene, wo Research-Datensaetze `canonical_source_id`
oder `canonical_study_id` gesetzt haben.

Prueft:

- Schemaebene: gueltiges YAML (ausschliesslich yaml.safe_load), JSON-Schema-Konformitaet,
  Pflichtfelder, Enums, echte Kalenderdaten (aktivierter FormatChecker), schema_version,
  Dateiname == id.
- Referenzebene: protocol_id, search_run_ids, duplicate_of, canonical_source_id (gegen
  data/sources/**), canonical_study_id (gegen data/entities/studies/**).
- Workflowebene: Ausschluss braucht Grund, Duplikat braucht Ziel (beides zusaetzlich
  schema-seitig erzwungen), keine Selbstreferenz/Zyklen bei duplicate_of, Extraktion nur
  fuer eingeschlossene Screening-Datensaetze, approved/verified brauchen Review/Verifikation
  (schema-seitig erzwungen).
- Dateiebene: keine unerwuenschten Binaerdateien in versionierten research/-Verzeichnissen
  (research/raw/** wird uebersprungen), research/examples/** bildet einen eigenen, in sich
  geschlossenen Namensraum (wie data/examples/).

Exitcode 0 bei Erfolg (nur WARNINGs erlaubt), Exitcode 1 bei mindestens einem ERROR. Keine
Netzwerkzugriffe.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _datalib import (  # noqa: E402
    DATA_DIR,
    DataFileError,
    Report,
    build_schema_registry,
    iter_entity_files,
    iter_source_files,
    load_yaml_file,
    relative,
    validate_against_schema,
)
from _researchlib import (  # noqa: E402
    RESEARCH_DIR,
    RESEARCH_KIND_TO_SCHEMA_ID,
    iter_research_files,
    load_all_research_vocabularies,
)

UNWANTED_BINARY_SUFFIXES = {
    ".exe", ".dll", ".so", ".bin", ".zip", ".7z", ".tar", ".gz",
    ".png", ".jpg", ".jpeg", ".gif", ".pdf", ".doc", ".docx", ".xls", ".xlsx",
    ".ris", ".bib", ".csv",
}

RESEARCH_KINDS = ("protocol", "search_run", "screening_record", "extraction_record")


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


def load_canonical_reference_sets(data_root: Path) -> tuple[set[str], set[str]]:
    """Laedt nur die IDs aus data/sources/** und data/entities/studies/**, fuer
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

    return source_ids, study_ids


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

    for obj in screening.values():
        file_rel = relative(obj.path)
        data = obj.data

        for search_run_id in data.get("search_run_ids") or []:
            if search_run_id not in search_runs:
                report.error(file_rel, "$.search_run_ids", f"references missing search run: {search_run_id}")

        duplicate_of = data.get("duplicate_of")
        if duplicate_of:
            if duplicate_of == obj.id:
                report.error(file_rel, "$.duplicate_of", "screening record cannot mark itself as duplicate_of")
            elif duplicate_of not in screening:
                report.error(file_rel, "$.duplicate_of", f"references missing screening record: {duplicate_of}")

        canonical_source_id = data.get("canonical_source_id")
        if canonical_source_id and canonical_source_id not in source_ids:
            report.error(
                file_rel, "$.canonical_source_id",
                f"references a canonical source that does not exist under data/sources/**: {canonical_source_id}",
            )

    # Zyklenerkennung bei duplicate_of (unabhaengig von der Selbstreferenzpruefung oben).
    for obj_id, obj in screening.items():
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
            path_seen.add(current)
            current = screening[current].data.get("duplicate_of")
            steps += 1

    for obj in extractions.values():
        file_rel = relative(obj.path)
        data = obj.data

        screening_id = data.get("screening_record_id")
        screening_obj = screening.get(screening_id)
        if screening_id and screening_obj is None:
            report.error(file_rel, "$.screening_record_id", f"references missing screening record: {screening_id}")
        elif screening_obj is not None and screening_obj.data.get("decision") != "include":
            report.error(
                file_rel, "$.screening_record_id",
                f"extraction record created for screening record '{screening_id}' whose decision is "
                f"'{screening_obj.data.get('decision')}', not 'include' -- extraction is only allowed for "
                "included candidates",
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


def check_no_unwanted_binaries(report: Report, root: Path) -> None:
    if not root.exists():
        return
    for path in root.rglob("*"):
        rel_parts = path.relative_to(root).parts
        if rel_parts and rel_parts[0] == "raw":
            continue  # research/raw/** ist expliziter, nicht validierter lokaler Arbeitsbereich
        if path.is_file() and path.suffix.lower() in UNWANTED_BINARY_SUFFIXES:
            report.error(relative(path), "", "unexpected binary file inside a versioned research/ directory")


def run_validation(
    verbose: bool, research_root: Path = RESEARCH_DIR, data_root: Path = DATA_DIR
) -> Report:
    report = Report()
    registry, schemas = build_schema_registry()
    vocabularies = load_all_research_vocabularies()

    check_no_unwanted_binaries(report, research_root)

    source_ids, study_ids = load_canonical_reference_sets(data_root)

    objects = load_research_dataset(research_root, report, registry, schemas, vocabularies)
    check_research_references(report, objects, source_ids, study_ids)

    examples_root = research_root / "examples"
    example_objects = load_research_dataset(examples_root, report, registry, schemas, vocabularies)
    check_research_references(report, example_objects, source_ids, study_ids)

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

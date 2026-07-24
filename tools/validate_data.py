#!/usr/bin/env python3
"""Validiert die strukturierten wissenschaftlichen Daten von Peptide Atlas.

Prueft (siehe docs/project/Phase_3_Scientific_Data_Architecture.md, Abschnitt
Validierung, fuer die vollstaendige Regel-Uebersicht):

- Schemaebene: gueltiges YAML, gueltiges JSON Schema, Pflichtfelder, Enums,
  Datumsformate, oneOf-Regeln, schema_version.
- Dateiebene: Dateiname == id, globale ID-Eindeutigkeit, keine leeren
  Platzhalterdateien ausserhalb data/examples/, keine unsicheren YAML-Tags,
  keine unerwuenschten Binaerdateien.
- Referenzebene: referenzierte Entitaeten/Studien/Quellen/Claims existieren,
  Praedikate und Objekttypen sind im Vokabular bekannt.
- Evidenzebene: Quellenpflicht fuer aktive medizinisch relevante Claims,
  Haendlerangabe/persoenliche Erfahrung nicht als alleiniger aktiver
  Wirksamkeitsnachweis, zurueckgezogene Quellen, certainty_rationale.
- Reviewebene: Statuswerte gueltig, `active` benoetigt Reviewdatum und
  mindestens einen Reviewer.
- Artikelintegration: Frontmatter von docs/**/*.md (ausser docs/project/**)
  referenziert existierende entity_id/claim_ids; `evidenzstufe` erzeugt eine
  Deprecation-Warnung, keinen Fehler.

Exitcode 0 bei Erfolg (nur WARNINGs erlaubt), Exitcode 1 bei mindestens einem
ERROR. Keine Netzwerkzugriffe.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import jsonschema
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _datalib import (  # noqa: E402
    DATA_DIR,
    DOCS_DIR,
    ENTITY_TYPE_TO_SCHEMA_ID,
    DataFileError,
    build_schema_registry,
    iter_claim_files,
    iter_entity_files,
    iter_example_entity_files,
    iter_source_files,
    load_all_vocabularies,
    load_yaml_file,
    normalize_doi,
    normalize_isbn,
    normalize_pmcid,
    normalize_pmid,
    normalize_url,
    relative,
)

# Rein navigatorische Seiten ohne redaktionellen Artikel-Workflow (siehe Quality
# Standards: Pflichtfelder gelten "fuer jeden Content-Artikel", nicht fuer die
# Startseite oder die automatisch befuellte Tag-Uebersichtsseite).
NON_ARTICLE_PAGES = {"index.md", "tags.md"}

UNWANTED_BINARY_SUFFIXES = {
    ".exe", ".dll", ".so", ".bin", ".zip", ".7z", ".tar", ".gz",
    ".png", ".jpg", ".jpeg", ".gif", ".pdf", ".doc", ".docx", ".xls", ".xlsx",
}

# Claimtypen, die eine wissenschaftlich substanzielle, medizinisch relevante Aussage
# treffen. Diese duerfen im Status 'active' niemals ohne Quelle sein (source_requirement:
# exempt ist fuer sie ausgeschlossen, siehe EXEMPTABLE_CLAIM_TYPES) und duerfen als
# alleinige Evidenzkategorie nicht merchant_claim/personal_experience tragen.
MEDICALLY_RELEVANT_CLAIM_TYPES = {
    "mechanism",
    "receptor_activity",
    "pathway_activity",
    "pharmacokinetics",
    "efficacy",
    "safety",
    "adverse_event",
    "regulatory",
    "study_result",
    "association",
    "comparison",
}

# Einzige Claimtypen, fuer die source_requirement: exempt ueberhaupt zulaessig ist --
# rein administrative/identifizierende Aussagen ohne eigene medizinische Substanz.
EXEMPTABLE_CLAIM_TYPES = {"identity", "classification"}

WEAK_EVIDENCE_CATEGORIES = {"merchant_claim", "personal_experience"}
WEAK_SOURCE_TYPES = {"merchant_page", "personal_report"}
EVIDENCE_CATEGORY_BY_SOLE_SOURCE_TYPE = {
    "merchant_page": "merchant_claim",
    "personal_report": "personal_experience",
}


@dataclass
class Issue:
    level: str  # "ERROR" | "WARNING"
    file: str
    path: str
    message: str

    def format(self) -> str:
        location = f"{self.file}\n  {self.path}: " if self.path else f"{self.file}\n  "
        return f"{self.level} {location}{self.message}"


class Report:
    def __init__(self) -> None:
        self.issues: list[Issue] = []

    def error(self, file: str, path: str, message: str) -> None:
        self.issues.append(Issue("ERROR", file, path, message))

    def warning(self, file: str, path: str, message: str) -> None:
        self.issues.append(Issue("WARNING", file, path, message))

    @property
    def error_count(self) -> int:
        return sum(1 for issue in self.issues if issue.level == "ERROR")

    @property
    def warning_count(self) -> int:
        return sum(1 for issue in self.issues if issue.level == "WARNING")


@dataclass
class LoadedObject:
    id: str
    kind: str  # "entity" | "source" | "claim"
    entity_type: str | None
    path: Path
    data: dict


def jsonschema_error_path(error: jsonschema.exceptions.ValidationError) -> str:
    parts = [str(p) for p in error.absolute_path]
    return "$" + "".join(f"[{p}]" if isinstance(p, int) else f".{p}" for p in parts) if parts else "$"


_FORMAT_CHECKER = jsonschema.FormatChecker()


def validate_against_schema(report: Report, file_rel: str, data: Any, schema_id: str, registry, schemas) -> None:
    schema = schemas[schema_id]
    validator_cls = jsonschema.validators.validator_for(schema)
    validator = validator_cls(schema, registry=registry, format_checker=_FORMAT_CHECKER)
    for error in sorted(validator.iter_errors(data), key=lambda e: list(e.absolute_path)):
        report.error(file_rel, jsonschema_error_path(error), error.message)


def load_dataset(root: Path, report: Report, registry, schemas, vocabularies, entity_iterator=iter_entity_files) -> tuple[
    dict[str, LoadedObject], dict[str, LoadedObject], dict[str, LoadedObject]
]:
    """Laedt und schema-validiert ein Datenset (production oder examples)."""
    entities: dict[str, LoadedObject] = {}
    sources: dict[str, LoadedObject] = {}
    claims: dict[str, LoadedObject] = {}
    seen_ids: dict[str, str] = {}

    def register(obj: LoadedObject, file_rel: str) -> None:
        if obj.id in seen_ids:
            report.error(file_rel, "$.id", f"duplicate id '{obj.id}', already used in {seen_ids[obj.id]}")
        else:
            seen_ids[obj.id] = file_rel

    for path, entity_type in entity_iterator(root):
        file_rel = relative(path)
        try:
            data = load_yaml_file(path)
        except DataFileError as exc:
            report.error(file_rel, "", str(exc))
            continue
        if not data:
            if "examples" not in path.parts:
                report.error(file_rel, "", "empty placeholder file is not allowed outside data/examples/")
            continue
        if not isinstance(data, dict):
            report.error(file_rel, "", "top-level YAML content must be a mapping")
            continue

        stem = path.stem
        obj_id = data.get("id")
        if obj_id != stem:
            report.error(file_rel, "$.id", f"id '{obj_id}' does not match filename '{stem}'")

        declared_type = data.get("entity_type")
        if declared_type is not None and declared_type != entity_type:
            report.error(
                file_rel, "$.entity_type",
                f"entity_type '{declared_type}' does not match folder-implied type '{entity_type}'",
            )
            schema_id = ENTITY_TYPE_TO_SCHEMA_ID.get(entity_type)
        else:
            schema_id = ENTITY_TYPE_TO_SCHEMA_ID[entity_type]

        validate_against_schema(report, file_rel, data, schema_id, registry, schemas)

        vocab = vocabularies["entity_types"]
        if entity_type not in vocab.values:
            report.error(file_rel, "$.entity_type", f"entity_type '{entity_type}' is unknown to entity_types.yaml")

        if entity_type == "substance":
            for cls in data.get("substance_classes") or []:
                if cls not in vocabularies["substance_classes"].values:
                    report.error(file_rel, "$.substance_classes", f"unknown substance class '{cls}'")

        obj = LoadedObject(id=obj_id or stem, kind="entity", entity_type=entity_type, path=path, data=data)
        register(obj, file_rel)
        entities[obj.id] = obj

    # Normalisierte-Identifikator -> Source-ID, fuer Duplikaterkennung ueber alle Quellen
    # dieses Datensets hinweg (siehe normalize_* in _datalib.py).
    seen_doi: dict[str, str] = {}
    seen_pmid: dict[str, str] = {}
    seen_pmcid: dict[str, str] = {}
    seen_isbn: dict[str, str] = {}
    seen_url: dict[str, str] = {}

    for path in iter_source_files(root):
        file_rel = relative(path)
        try:
            data = load_yaml_file(path)
        except DataFileError as exc:
            report.error(file_rel, "", str(exc))
            continue
        if not data:
            if "examples" not in path.parts:
                report.error(file_rel, "", "empty placeholder file is not allowed outside data/examples/")
            continue
        if not isinstance(data, dict):
            report.error(file_rel, "", "top-level YAML content must be a mapping")
            continue

        stem = path.stem
        obj_id = data.get("id")
        if obj_id != stem:
            report.error(file_rel, "$.id", f"id '{obj_id}' does not match filename '{stem}'")
        source_key = obj_id or stem

        validate_against_schema(report, file_rel, data, "source.schema.json", registry, schemas)

        if data.get("source_type") not in vocabularies["source_types"].values:
            report.error(file_rel, "$.source_type", f"unknown source_type '{data.get('source_type')}'")

        identifiers = data.get("identifiers") or {}

        def check_duplicate_identifier(
            raw_value, normalizer, seen: dict[str, str], field_path: str, label: str
        ) -> None:
            if not raw_value:
                return
            try:
                normalized = normalizer(raw_value)
            except ValueError:
                return
            existing = seen.get(normalized)
            if existing is not None and existing != source_key:
                report.error(
                    file_rel, field_path,
                    f"duplicate {label} (normalized '{normalized}') already used by source '{existing}'",
                )
            else:
                seen[normalized] = source_key

        check_duplicate_identifier(identifiers.get("doi"), normalize_doi, seen_doi, "$.identifiers.doi", "DOI")
        check_duplicate_identifier(identifiers.get("pmid"), normalize_pmid, seen_pmid, "$.identifiers.pmid", "PMID")
        check_duplicate_identifier(identifiers.get("pmcid"), normalize_pmcid, seen_pmcid, "$.identifiers.pmcid", "PMCID")
        check_duplicate_identifier(identifiers.get("isbn"), normalize_isbn, seen_isbn, "$.identifiers.isbn", "ISBN")

        url = data.get("url")
        if url:
            normalized_url = normalize_url(url)
            existing_url = seen_url.get(normalized_url)
            if existing_url is not None and existing_url != source_key:
                report.warning(
                    file_rel, "$.url",
                    f"canonical URL (normalized '{normalized_url}') also used by source '{existing_url}' "
                    "-- verify these are not the same source under two IDs",
                )
            else:
                seen_url[normalized_url] = source_key

        obj = LoadedObject(id=obj_id or stem, kind="source", entity_type=None, path=path, data=data)
        register(obj, file_rel)
        sources[obj.id] = obj

    for path in iter_claim_files(root):
        file_rel = relative(path)
        try:
            data = load_yaml_file(path)
        except DataFileError as exc:
            report.error(file_rel, "", str(exc))
            continue
        if not data:
            if "examples" not in path.parts:
                report.error(file_rel, "", "empty placeholder file is not allowed outside data/examples/")
            continue
        if not isinstance(data, dict):
            report.error(file_rel, "", "top-level YAML content must be a mapping")
            continue

        stem = path.stem
        obj_id = data.get("id")
        if obj_id != stem:
            report.error(file_rel, "$.id", f"id '{obj_id}' does not match filename '{stem}'")

        validate_against_schema(report, file_rel, data, "claim.schema.json", registry, schemas)

        predicate = data.get("predicate")
        if predicate is not None and predicate not in vocabularies["predicates"].values:
            report.error(file_rel, "$.predicate", f"predicate '{predicate}' is not defined in data/vocabularies/predicates.yaml")

        obj = LoadedObject(id=obj_id or stem, kind="claim", entity_type=None, path=path, data=data)
        register(obj, file_rel)
        claims[obj.id] = obj

    return entities, sources, claims


def check_references(
    report: Report,
    entities: dict[str, LoadedObject],
    sources: dict[str, LoadedObject],
    claims: dict[str, LoadedObject],
) -> None:
    for claim in claims.values():
        file_rel = relative(claim.path)
        data = claim.data
        subject_id = data.get("subject_id")
        if subject_id and subject_id not in entities:
            report.error(file_rel, "$.subject_id", f"references missing entity: {subject_id}")

        obj = data.get("object") or {}
        if "entity_id" in obj:
            target = obj["entity_id"]
            if target not in entities:
                report.error(file_rel, "$.object.entity_id", f"references missing entity: {target}")

        for i, link in enumerate(data.get("evidence") or []):
            source_id = link.get("source_id")
            if source_id and source_id not in sources:
                report.error(file_rel, f"$.evidence[{i}].source_id", f"references missing source: {source_id}")
            study_id = link.get("study_id")
            if study_id:
                study = entities.get(study_id)
                if study is None:
                    report.error(file_rel, f"$.evidence[{i}].study_id", f"references missing study: {study_id}")
                elif study.entity_type != "study":
                    report.error(file_rel, f"$.evidence[{i}].study_id", f"'{study_id}' is not a study entity")

    for entity in entities.values():
        if entity.entity_type != "study":
            continue
        file_rel = relative(entity.path)
        data = entity.data
        for source_id in data.get("source_ids") or []:
            if source_id not in sources:
                report.error(file_rel, "$.source_ids", f"references missing source: {source_id}")
        for sponsor_id in data.get("sponsor_ids") or []:
            if sponsor_id not in entities:
                report.error(file_rel, "$.sponsor_ids", f"references missing entity: {sponsor_id}")


def check_evidence_rules(
    report: Report,
    entities: dict[str, LoadedObject],
    sources: dict[str, LoadedObject],
    claims: dict[str, LoadedObject],
) -> None:
    for claim in claims.values():
        file_rel = relative(claim.path)
        data = claim.data
        status = data.get("status")
        claim_type = data.get("claim_type")
        evidence = data.get("evidence") or []
        evidence_category = data.get("evidence_category")
        certainty = data.get("certainty")
        source_requirement = data.get("source_requirement", "required")

        resolved_sources = [sources[link["source_id"]].data for link in evidence if link.get("source_id") in sources]
        resolved_source_types = {s.get("source_type") for s in resolved_sources}

        # --- 1. Quellen-Ausnahmen absichern -------------------------------------------------
        if source_requirement == "exempt":
            if claim_type in MEDICALLY_RELEVANT_CLAIM_TYPES:
                report.error(
                    file_rel, "$.source_requirement",
                    f"claim_type '{claim_type}' is medically relevant and can never use "
                    "source_requirement: exempt -- a source is always required",
                )
            elif claim_type not in EXEMPTABLE_CLAIM_TYPES:
                report.error(
                    file_rel, "$.source_requirement",
                    f"source_requirement: exempt is only allowed for claim_type in "
                    f"{sorted(EXEMPTABLE_CLAIM_TYPES)}, got '{claim_type}'",
                )

        if status == "active" and claim_type in MEDICALLY_RELEVANT_CLAIM_TYPES:
            if not evidence and source_requirement != "exempt":
                report.error(
                    file_rel, "$.evidence",
                    f"active claim of medically relevant type '{claim_type}' has no source "
                    "(set source_requirement: exempt with source_exemption_reason for administrative exceptions)",
                )

        # --- 3. Evidenzkategorie und Quellentyp konsistent validieren ------------------------
        if resolved_source_types and resolved_source_types == {"merchant_page"} and evidence_category != "merchant_claim":
            report.error(
                file_rel, "$.evidence_category",
                "claim relies exclusively on merchant_page sources but is not classified as "
                "evidence_category: merchant_claim",
            )
        if resolved_source_types and resolved_source_types == {"personal_report"} and evidence_category != "personal_experience":
            report.error(
                file_rel, "$.evidence_category",
                "claim relies exclusively on personal_report sources but is not classified as "
                "evidence_category: personal_experience",
            )

        if status == "active" and claim_type in MEDICALLY_RELEVANT_CLAIM_TYPES:
            if evidence_category == "merchant_claim":
                report.error(
                    file_rel, "$.evidence_category",
                    f"merchant_claim must not back an active, medically relevant claim_type "
                    f"('{claim_type}') -- model attributed merchant statements separately "
                    "(claim_type: other, predicate: claimed_by) instead of as a scientific claim",
                )
            if evidence_category == "personal_experience":
                report.error(
                    file_rel, "$.evidence_category",
                    f"personal_experience must not back an active, medically relevant claim_type "
                    f"('{claim_type}') -- model attributed personal reports separately "
                    "(claim_type: other, predicate: reported_by) instead of as a scientific claim",
                )
            if resolved_sources and all(s.get("source_type") in WEAK_SOURCE_TYPES for s in resolved_sources):
                report.error(
                    file_rel, "$.evidence",
                    "active, medically relevant claim relies exclusively on merchant_page/personal_report "
                    "source types, regardless of the assigned evidence_category or certainty",
                )

        # --- 10. Zusaetzliche Evidenzintegritaet ---------------------------------------------
        if status == "active" and evidence:
            directions = {link.get("direction") for link in evidence}
            if not (directions & {"supports", "mixed"}):
                report.error(
                    file_rel, "$.evidence",
                    "active claim's evidence contains no link with direction 'supports' or 'mixed' "
                    "(only contradicts/context_only) -- nothing actually backs this claim",
                )

        if status == "active" and resolved_sources:
            retraction_statuses = [s.get("retraction_status") for s in resolved_sources]
            if all(rs == "retracted" for rs in retraction_statuses):
                report.error(
                    file_rel, "$.evidence",
                    "active claim relies exclusively on retracted source(s)",
                )
            elif any(rs == "retracted" for rs in retraction_statuses):
                report.warning(
                    file_rel, "$.evidence",
                    "active claim uses at least one retracted source alongside other, non-retracted "
                    "sources -- verify the retracted source does not undermine the claim",
                )
            elif any(rs in {"expression_of_concern", "corrected"} for rs in retraction_statuses):
                report.warning(
                    file_rel, "$.evidence",
                    "claim references a source with retraction_status expression_of_concern/corrected",
                )

        if certainty == "high":
            weak_by_category = evidence_category in WEAK_EVIDENCE_CATEGORIES
            weak_by_source = bool(resolved_sources) and all(
                s.get("source_type") in WEAK_SOURCE_TYPES for s in resolved_sources
            )
            if weak_by_category or weak_by_source:
                report.error(
                    file_rel, "$.certainty",
                    "certainty 'high' is not allowed when the only evidence is a merchant page or personal report",
                )

        if status == "active":
            review = data.get("review") or {}
            if not review.get("last_reviewed_at"):
                report.error(file_rel, "$.review.last_reviewed_at", "status 'active' requires review.last_reviewed_at")
            if not review.get("reviewers"):
                report.error(file_rel, "$.review.reviewers", "status 'active' requires at least one reviewer")

        review = data.get("review") or {}
        last_reviewed_at = review.get("last_reviewed_at")
        updated_at = data.get("updated_at")
        if last_reviewed_at and updated_at and last_reviewed_at < updated_at:
            report.warning(
                file_rel, "$.review.last_reviewed_at",
                "claim was updated after its last review date -- confirm the review status is still valid "
                "(Phase 3 uses this simple date heuristic, not a full git-diff analysis; see known limitations)",
            )

    for entity in entities.values():
        file_rel = relative(entity.path)
        data = entity.data
        if data.get("status") == "active":
            review = data.get("review") or {}
            if not review.get("last_reviewed_at"):
                report.error(file_rel, "$.review.last_reviewed_at", "status 'active' requires review.last_reviewed_at")
            if not review.get("reviewers"):
                report.error(file_rel, "$.review.reviewers", "status 'active' requires at least one reviewer")

    # --- 6. Reviewmetadaten fuer Quellen -----------------------------------------------------
    for source in sources.values():
        file_rel = relative(source.path)
        data = source.data
        if data.get("status") == "active":
            review = data.get("review") or {}
            if not review.get("last_reviewed_at"):
                report.error(file_rel, "$.review.last_reviewed_at", "status 'active' requires review.last_reviewed_at")
            if not review.get("reviewers"):
                report.error(file_rel, "$.review.reviewers", "status 'active' requires at least one reviewer")


def check_no_unwanted_binaries(report: Report, root: Path) -> None:
    if not root.exists():
        return
    for path in root.rglob("*"):
        if path.is_file() and path.suffix.lower() in UNWANTED_BINARY_SUFFIXES:
            report.error(relative(path), "", "unexpected binary file inside data/ directory")


FRONTMATTER_DELIM = "---"


def parse_frontmatter(path: Path) -> dict | None:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != FRONTMATTER_DELIM:
        return None
    for i in range(1, len(lines)):
        if lines[i].strip() == FRONTMATTER_DELIM:
            block = "\n".join(lines[1:i])
            try:
                data = yaml.safe_load(block)
            except yaml.YAMLError as exc:
                raise DataFileError(f"invalid frontmatter YAML: {exc}") from exc
            return data if isinstance(data, dict) else {}
    return None


def check_articles(
    report: Report,
    entities: dict[str, LoadedObject],
    claims: dict[str, LoadedObject],
    registry,
    schemas,
    docs_root: Path = DOCS_DIR,
) -> None:
    if not docs_root.exists():
        return
    for path in sorted(docs_root.rglob("*.md")):
        rel_parts = path.relative_to(docs_root).parts
        if rel_parts and rel_parts[0] == "project":
            continue  # Architektur-/Projektdokumente benoetigen kein Frontmatter-Schema
        if len(rel_parts) == 1 and rel_parts[0] in NON_ARTICLE_PAGES:
            continue  # Startseite / automatische Tag-Uebersicht sind keine Content-Artikel
        file_rel = relative(path)
        try:
            frontmatter = parse_frontmatter(path)
        except DataFileError as exc:
            report.error(file_rel, "", str(exc))
            continue
        if frontmatter is None:
            report.error(
                file_rel, "",
                "content article is missing YAML frontmatter (expected a '---' delimited block with at "
                "least title/description/tags/status)",
            )
            continue

        validate_against_schema(report, file_rel, frontmatter, "article_frontmatter.schema.json", registry, schemas)

        if "evidenzstufe" in frontmatter:
            report.warning(
                file_rel, "$.evidenzstufe",
                "'evidenzstufe' is a deprecated legacy field. New scientific object pages should evaluate "
                "evidence per claim via entity_id/claim_ids instead of a single article-level grade "
                "(see docs/00_grundlagen/evidenzsystem.md).",
            )

        entity_id = frontmatter.get("entity_id")
        if entity_id and entity_id not in entities:
            report.error(file_rel, "$.entity_id", f"references missing entity: {entity_id}")

        claim_ids = frontmatter.get("claim_ids") or []
        for claim_id in claim_ids:
            claim = claims.get(claim_id)
            if claim is None:
                report.error(file_rel, "$.claim_ids", f"references missing claim: {claim_id}")
                continue
            claim_data = claim.data
            connected = claim_data.get("subject_id") == entity_id or (
                (claim_data.get("object") or {}).get("entity_id") == entity_id
            )
            if entity_id and not connected:
                report.warning(
                    file_rel, "$.claim_ids",
                    f"claim '{claim_id}' does not appear thematically connected to entity_id '{entity_id}' "
                    "(neither subject_id nor object.entity_id match)",
                )
            if claim_data.get("status") == "withdrawn" and frontmatter.get("status") == "Aktiv":
                report.warning(
                    file_rel, "$.claim_ids",
                    f"active article references withdrawn claim '{claim_id}' -- ensure this is clearly marked "
                    "in the article text (Phase 3 does not analyze Markdown body content)",
                )


def run_validation(verbose: bool, data_root: Path = DATA_DIR, docs_root: Path = DOCS_DIR) -> Report:
    report = Report()
    registry, schemas = build_schema_registry()
    vocabularies = load_all_vocabularies()

    check_no_unwanted_binaries(report, data_root)

    entities, sources, claims = load_dataset(data_root, report, registry, schemas, vocabularies)
    check_references(report, entities, sources, claims)
    check_evidence_rules(report, entities, sources, claims)

    examples_root = data_root / "examples"
    ex_entities, ex_sources, ex_claims = load_dataset_examples(examples_root, report, registry, schemas, vocabularies)
    check_references(report, ex_entities, ex_sources, ex_claims)
    check_evidence_rules(report, ex_entities, ex_sources, ex_claims)

    check_articles(report, entities, claims, registry, schemas, docs_root=docs_root)

    if verbose:
        print(f"Loaded: {len(entities)} entities, {len(sources)} sources, {len(claims)} claims (production)")
        print(
            f"Loaded: {len(ex_entities)} entities, {len(ex_sources)} sources, {len(ex_claims)} claims (examples)"
        )
    return report


def load_dataset_examples(root: Path, report: Report, registry, schemas, vocabularies):
    """Beispieldaten bilden ihren eigenen, in sich geschlossenen Namensraum."""
    return load_dataset(root, report, registry, schemas, vocabularies, entity_iterator=iter_example_entity_files)


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

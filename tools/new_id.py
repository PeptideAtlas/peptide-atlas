#!/usr/bin/env python3
"""Erzeugt stabile, eindeutige IDs fuer Entitaeten, Quellen und Claims.

Verwendet ausschliesslich die Python-Standardbibliothek `uuid` -- keine
zusaetzliche Bibliothek fuer ULIDs oder aehnliches (siehe Abschnitt 12.2 der
Phase-3-Spezifikation).

Beispiele:
    python tools/new_id.py entity substance "Example Peptide"
    python tools/new_id.py claim
    python tools/new_id.py source --pmid 12345678
    python tools/new_id.py source --nct NCT00000000
    python tools/new_id.py source --doi 10.1000/example.doi
    python tools/new_id.py source
"""

from __future__ import annotations

import argparse
import re
import sys
import unicodedata
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _datalib import ENTITY_FOLDER_TO_TYPE  # noqa: E402

ENTITY_TYPE_TO_PREFIX = {
    "substance": "substance",
    "receptor": "receptor",
    "pathway": "pathway",
    "condition": "condition",
    "adverse_event": "adverse-event",
    "organization": "organization",
    "study": "study",
}

_TRANSLITERATION = str.maketrans(
    {"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss", "Ä": "Ae", "Ö": "Oe", "Ü": "Ue"}
)


def slugify(text: str) -> str:
    """Wandelt einen beliebigen Namen in einen ASCII-lowercase-kebab-case-Slug um."""
    text = text.translate(_TRANSLITERATION)
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    if not text:
        raise ValueError("slug is empty after normalization")
    return text


def new_entity_id(entity_type: str, name: str) -> str:
    if entity_type not in ENTITY_TYPE_TO_PREFIX:
        valid = ", ".join(sorted(ENTITY_TYPE_TO_PREFIX))
        raise ValueError(f"unknown entity_type '{entity_type}', expected one of: {valid}")
    prefix = ENTITY_TYPE_TO_PREFIX[entity_type]
    return f"{prefix}-{slugify(name)}"


def new_claim_id() -> str:
    return f"claim-{uuid.uuid4()}"


def normalize_doi(doi: str) -> str:
    doi = doi.strip()
    doi = re.sub(r"^https?://(dx\.)?doi\.org/", "", doi, flags=re.IGNORECASE)
    doi = doi.lower()
    doi = re.sub(r"[^a-z0-9]+", "-", doi)
    doi = re.sub(r"-+", "-", doi).strip("-")
    return doi


def new_source_id(*, pmid: str | None = None, nct: str | None = None, doi: str | None = None) -> str:
    if pmid:
        digits = re.sub(r"\D", "", pmid)
        if not digits:
            raise ValueError("pmid must contain digits")
        return f"source-pmid-{digits}"
    if nct:
        identifier = nct.strip().lower()
        if not identifier.startswith("nct"):
            identifier = f"nct{identifier}"
        return f"source-nct-{identifier}"
    if doi:
        return f"source-doi-{normalize_doi(doi)}"
    return f"source-{uuid.uuid4()}"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    subparsers = parser.add_subparsers(dest="command", required=True)

    entity_parser = subparsers.add_parser("entity", help="Neue Entitaets-ID erzeugen")
    entity_parser.add_argument("entity_type", choices=sorted(ENTITY_FOLDER_TO_TYPE.values()))
    entity_parser.add_argument("name", help="canonical_name, aus dem der Slug gebildet wird")

    subparsers.add_parser("claim", help="Neue Claim-ID (UUID4) erzeugen")

    source_parser = subparsers.add_parser("source", help="Neue Quellen-ID erzeugen")
    group = source_parser.add_mutually_exclusive_group()
    group.add_argument("--pmid", help="PubMed-ID")
    group.add_argument("--nct", help="ClinicalTrials.gov NCT-Nummer")
    group.add_argument("--doi", help="DOI")

    subparsers.add_parser("slug", help="Nur einen Slug aus einem Namen erzeugen").add_argument("name")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "entity":
        print(new_entity_id(args.entity_type, args.name))
    elif args.command == "claim":
        print(new_claim_id())
    elif args.command == "source":
        print(new_source_id(pmid=args.pmid, nct=args.nct, doi=args.doi))
    elif args.command == "slug":
        print(slugify(args.name))
    else:  # pragma: no cover - argparse erzwingt gueltige Subcommands
        parser.error(f"unknown command {args.command!r}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Generiert build/catalog.json aus den validierten Daten unter data/.

Der Katalog ist ein reines Build-Artefakt (siehe .gitignore) und dient als
Grundlage fuer eine kuenftige read-only API. Er enthaelt keine zirkulaeren
Einbettungen: Objekte referenzieren einander ausschliesslich ueber IDs.

Dieses Skript validiert die Daten NICHT selbst -- fuehre vorher
`python tools/validate_data.py` aus. Es geht von syntaktisch ladbarem YAML
aus und bricht mit einer klaren Fehlermeldung ab, falls das nicht der Fall ist.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _datalib import (  # noqa: E402
    BUILD_DIR,
    DATA_DIR,
    DataFileError,
    SCHEMA_VERSION,
    iter_claim_files,
    iter_entity_files,
    iter_source_files,
    load_yaml_file,
    relative,
)


def load_records(root: Path) -> tuple[list[dict], list[dict], list[dict]]:
    entities: list[dict] = []
    for path, entity_type in iter_entity_files(root):
        try:
            data = load_yaml_file(path)
        except DataFileError as exc:
            raise SystemExit(f"ERROR {relative(path)}: {exc}")
        if not data:
            continue
        entities.append(data)

    sources: list[dict] = []
    for path in iter_source_files(root):
        try:
            data = load_yaml_file(path)
        except DataFileError as exc:
            raise SystemExit(f"ERROR {relative(path)}: {exc}")
        if not data:
            continue
        sources.append(data)

    claims: list[dict] = []
    for path in iter_claim_files(root):
        try:
            data = load_yaml_file(path)
        except DataFileError as exc:
            raise SystemExit(f"ERROR {relative(path)}: {exc}")
        if not data:
            continue
        claims.append(data)

    return entities, sources, claims


ENTITY_TYPE_PLURAL = {
    "substance": "substances",
    "receptor": "receptors",
    "pathway": "pathways",
    "condition": "conditions",
    "adverse_event": "adverse_events",
    "organization": "organizations",
    "study": "studies",
}


def build_catalog(root: Path, generated_at: str) -> dict:
    entities, sources, claims = load_records(root)

    entities_sorted = sorted(entities, key=lambda e: e["id"])
    sources_sorted = sorted(sources, key=lambda s: s["id"])
    claims_sorted = sorted(claims, key=lambda c: c["id"])

    counts: dict[str, int] = {}
    for entity in entities_sorted:
        entity_type = entity.get("entity_type", "unknown")
        key = ENTITY_TYPE_PLURAL.get(entity_type, f"{entity_type}s")
        counts[key] = counts.get(key, 0) + 1
    counts["sources"] = len(sources_sorted)
    counts["claims"] = len(claims_sorted)

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": generated_at,
        "counts": dict(sorted(counts.items())),
        "entities": entities_sorted,
        "studies": [e for e in entities_sorted if e.get("entity_type") == "study"],
        "sources": sources_sorted,
        "claims": claims_sorted,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out", type=Path, default=BUILD_DIR / "catalog.json", help="Zielpfad (Standard: build/catalog.json)"
    )
    parser.add_argument(
        "--generated-at",
        default=None,
        help="ISO-8601-Zeitstempel fuer generated_at. Standard: aktuelle UTC-Zeit.",
    )
    args = parser.parse_args(argv)

    generated_at = args.generated_at
    if generated_at is None:
        from datetime import datetime, timezone

        generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    catalog = build_catalog(DATA_DIR, generated_at)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as handle:
        json.dump(catalog, handle, ensure_ascii=False, indent=2, sort_keys=False)
        handle.write("\n")

    print(f"wrote {args.out} ({sum(catalog['counts'].values())} objects total)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

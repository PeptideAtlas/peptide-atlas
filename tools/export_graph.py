#!/usr/bin/env python3
"""Generiert build/graph.json (Nodes + Edges) aus den validierten Daten unter data/.

Edges werden ausschliesslich aus Claims abgeleitet, deren `object` ein
`entity_id` referenziert -- sie sind kein zweites, redaktionell gepflegtes
Datenmodell (siehe schemas/relationship.schema.json und Decision Log).

Dieses Skript validiert die Daten NICHT selbst -- fuehre vorher
`python tools/validate_data.py` aus. Keine Graphdatenbank, keine externe
Infrastruktur: das Ergebnis ist eine einzelne deterministische JSON-Datei.
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
    load_yaml_file,
    relative,
)


def load_entities(root: Path) -> list[dict]:
    entities = []
    for path, _entity_type in iter_entity_files(root):
        try:
            data = load_yaml_file(path)
        except DataFileError as exc:
            raise SystemExit(f"ERROR {relative(path)}: {exc}")
        if data:
            entities.append(data)
    return entities


def load_claims(root: Path) -> list[dict]:
    claims = []
    for path in iter_claim_files(root):
        try:
            data = load_yaml_file(path)
        except DataFileError as exc:
            raise SystemExit(f"ERROR {relative(path)}: {exc}")
        if data:
            claims.append(data)
    return claims


def build_nodes(entities: list[dict]) -> list[dict]:
    nodes = [
        {
            "id": entity["id"],
            "entity_type": entity.get("entity_type"),
            "canonical_name": entity.get("canonical_name"),
            "labels": entity.get("labels", {}),
            "status": entity.get("status"),
        }
        for entity in entities
    ]
    return sorted(nodes, key=lambda n: n["id"])


def build_edges(claims: list[dict]) -> list[dict]:
    edges = []
    for claim in claims:
        obj = claim.get("object") or {}
        target = obj.get("entity_id")
        if not target:
            continue
        edges.append(
            {
                "claim_id": claim["id"],
                "from": claim.get("subject_id"),
                "to": target,
                "predicate": claim.get("predicate"),
                "evidence_category": claim.get("evidence_category"),
                "certainty": claim.get("certainty"),
                "status": claim.get("status"),
                "source_ids": sorted(
                    {link["source_id"] for link in claim.get("evidence") or [] if link.get("source_id")}
                ),
            }
        )
    return sorted(edges, key=lambda e: (e["from"] or "", e["to"] or "", e["claim_id"]))


def build_graph(root: Path, generated_at: str) -> dict:
    entities = load_entities(root)
    claims = load_claims(root)
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": generated_at,
        "nodes": build_nodes(entities),
        "edges": build_edges(claims),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out", type=Path, default=BUILD_DIR / "graph.json", help="Zielpfad (Standard: build/graph.json)"
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

    graph = build_graph(DATA_DIR, generated_at)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as handle:
        json.dump(graph, handle, ensure_ascii=False, indent=2, sort_keys=False)
        handle.write("\n")

    print(f"wrote {args.out} ({len(graph['nodes'])} nodes, {len(graph['edges'])} edges)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

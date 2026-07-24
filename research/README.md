# research/ — Rechercheverlauf, Kandidaten, Screening, Extraktion und Audit Trail

Dieser Ordner ist die **Provenienz- und Arbeitsebene** von Peptide Atlas — nicht die kanonische
Wissensdatenbank. Er beantwortet die Frage „wie wurde etwas gefunden, geprüft und bewertet?", während
[`data/`](../data/README.md) die Frage „was ist geprüftes, veröffentlichtes Wissen?" beantwortet.

```text
research/** = Rechercheverlauf, Kandidaten, Screening, Extraktion und Audit Trail
data/**     = geprüfte und kanonisch veröffentlichte Wissensobjekte
```

**Ein Forschungsdatensatz unter `research/**` gilt nicht automatisch als wissenschaftliche Erkenntnis.**
Eine Information wird erst dann kanonisches Wissen, wenn sie nach manueller Prüfung ausdrücklich als Entität,
Quelle, Studie oder Claim unter `data/**` angelegt wurde (siehe ADR-0033 im
[Decision Log](../docs/project/Decision_Log.md)). `research/**` fließt deshalb **nicht** in
`build/catalog.json` oder `build/graph.json` ein.

Der vollständige, verbindliche Prozess steht in:

- [Scientific Research Protocol](../docs/project/Scientific_Research_Protocol.md) — das allgemeine, für jeden
  künftigen Wirkstoff geltende Standardverfahren.
- [Evidence Curation Workflow](../docs/project/Evidence_Curation_Workflow.md) — der konkrete
  Zustandsübergang vom Suchtreffer bis zum aktiven kanonischen Claim.

## Struktur

```text
research/
├── protocols/       Ein Research-Protokoll (research-protocol-<slug>-v<N>.yaml) pro Wirkstoff/Fragestellung
├── search_runs/     Protokollierte, tatsächlich ausgeführte Suchläufe (search-run-<uuid4>.yaml)
├── screening/       Ein-/Ausschlussentscheidungen pro Kandidat (screening-record-<uuid4>.yaml)
├── extractions/     Beobachtungen und vorläufige Kandidatenclaims (extraction-record-<uuid4>.yaml)
├── vocabularies/    kontrollierte Vokabulare (Datenbanken, Statuswerte, Ausschlussgründe, ...)
├── examples/        ausschließlich fiktive Platzhalterdaten, eigener Namensraum (wie data/examples/)
└── raw/             lokaler, NICHT versionierter Arbeitsbereich fuer Exporte/Volltexte (siehe raw/README.md)
```

## Objektarten und ihre IDs

| Objektart | Ordner | ID-Muster | Schema |
|---|---|---|---|
| Research-Protokoll | `research/protocols/` | `research-protocol-<slug>-v<N>` | `schemas/research_protocol.schema.json` |
| Suchlauf | `research/search_runs/` | `search-run-<uuid4>` | `schemas/research_search_run.schema.json` |
| Screening-Datensatz | `research/screening/` | `screening-record-<uuid4>` | `schemas/research_screening_record.schema.json` |
| Extraktionsdatensatz | `research/extractions/` | `extraction-record-<uuid4>` | `schemas/research_extraction_record.schema.json` |

Wie bei `data/**` muss der Dateiname exakt der `id` entsprechen (ohne `.yaml`).

## Validierung

```bash
python tools/validate_research.py --verbose
```

Läuft **getrennt** vom bestehenden `tools/validate_data.py`, prüft aber Querverweise auf die kanonische
Datenebene (`canonical_source_id` muss unter `data/sources/**`, `canonical_study_id` unter
`data/entities/studies/**` existieren, sofern gesetzt). Beide Validatoren laufen in CI
(siehe `.github/workflows/ci.yml`).

## Kurzfassung des Workflows

1. Ein **Protokoll** (`protocols/`) legt Forschungsfragen, geplante Suchbegriffe, Datenbanken sowie Ein-/
   Ausschluss-, Dedup-, Screening-, Extraktions- und Claim-Promotion-Regeln fest, bevor gesucht wird.
2. Ein **Suchlauf** (`search_runs/`) protokolliert exakt, was wann in welcher Datenbank gesucht wurde.
3. Jeder Treffer wird als **Screening-Datensatz** (`screening/`) erfasst und durchläuft Deduplizierung,
   Titel-/Abstract- und Volltext-Screening bis zu einer Entscheidung (`include`/`exclude`/`duplicate`/...).
4. Eingeschlossene Kandidaten werden in einem **Extraktionsdatensatz** (`extractions/`) mit kurzen Paraphrasen
   und präzisen Fundstellen erfasst — inklusive vorläufiger, ausdrücklich ungeprüfter Kandidatenclaims.
5. Erst nach zweiter Prüfung (`extraction_status: verified`) und wissenschaftlichem Review werden Informationen
   **manuell** als Quelle, Studie oder Claim unter `data/**` angelegt — dieser Schritt ist in Phase 4A bewusst
   **nicht automatisiert**.

## `research/examples/`

Wie `data/examples/`: ausschließlich offensichtlich fiktive Platzhalterdaten, ein eigener, in sich
geschlossener Namensraum, der nicht in echte Validierungs-Querverweise oder Exporte eingeht.

## Sicherheit und Urheberrecht

- Keine Zugangsdaten, Tokens oder API-Schlüssel.
- Keine personenbezogenen Patientendaten.
- Keine vollständigen urheberrechtlich geschützten Artikeltexte — nur kurze Paraphrasen mit Fundstelle
  (technisch durch eine Zeichenlängengrenze in den Schemas abgesichert, siehe
  [Scientific Research Protocol](../docs/project/Scientific_Research_Protocol.md), Abschnitt „Urheberrecht und
  Volltextspeicherung").
- Keine PDF-Sammlung im Repository.

---
title: Roadmap
description: Ausbaustand und geplante nächste Schritte für Peptide Atlas.
tags:
  - Projekt
status: Aktiv
---

# Roadmap

## Version 0.1 (abgeschlossen)

- [x] Projektstruktur und MkDocs-Material-Setup
- [x] Navigation, lokale Suche, Tags, hell/dunkles Design
- [x] Evidenzsystem und Redaktionsstandard definiert
- [x] Artikelvorlage angelegt
- [x] Erste Grundlagenartikel: „Was sind Peptide?", „Rezeptoren"
- [x] GitHub-Actions-Workflow für GitHub-Pages-Deployment vorbereitet

## Version 0.2 (abgeschlossen)

- [x] Vollständige Architektur-Dokumentation unter `docs/project/`
- [x] Universelles Datenmodell entworfen (Denkmodell, siehe [Data Model](project/Data_Model.md))
- [x] Knowledge-Graph-Denkmodell dokumentiert
- [x] Workflow, Naming, Versionierung dokumentiert

## Version 0.3 — Scientific Data Architecture (aktuell, Phase 3)

- [x] JSON Schemas für Entitäten, Studien, Quellen, Claims und Beziehungen (`schemas/`)
- [x] YAML-Datenebene mit kontrollierten Vokabularen (`data/`)
- [x] Claim-basiertes Evidenzmodell (Evidenzkategorie getrennt von Sicherheit, siehe
      [Evidenzsystem](00_grundlagen/evidenzsystem.md))
- [x] Validator (`tools/validate_data.py`) mit Schema-, Datei-, Referenz-, Evidenz- und Reviewprüfungen
- [x] Katalog- und Graphexport (`tools/build_catalog.py`, `tools/export_graph.py`)
- [x] Testsuite (pytest, gültige/ungültige Fixtures)
- [x] CI-Integration (`ci.yml`, erweitertes `deploy.yml`)
- [ ] Erste Wirkstoffartikel im Bereich [Wirkstoffe](01_wirkstoffe/index.md) — bewusst nicht Teil von Phase 3,
      siehe [Phase 3 Dokumentation](project/Phase_3_Scientific_Data_Architecture.md)

## Geplant (Phase 4+)

- [ ] Retatrutid als erstes vollständiges wissenschaftliches Pilotobjekt (erste reale `substance`-, `source`-
      und `claim`-Dateien nach dem in Phase 3 geschaffenen Schema)
- [ ] Ausbau [Biologie](02_biologie/index.md): weitere Rezeptorklassen und Signalwege
- [ ] Aufbau [Indikationen](03_indikationen/index.md) mit klarer Trennung Zulassung/Forschung (als Claims, siehe
      [Data Model](project/Data_Model.md))
- [ ] Erste Studienzusammenfassungen im Bereich [Studien](04_studien/index.md)
- [ ] Vergleichstabellen im Bereich [Vergleiche](05_vergleiche/index.md), abgeleitet aus `COMPARED_TO`-Claims
- [ ] Strukturformeln und Diagramme im Bereich [Medien](06_medien/index.md)
- [ ] Ausbau [Glossar](07_glossar/index.md)
- [ ] Redaktionelle Prüfung bestehender Entwurfsartikel (Status „Entwurf" → „Aktiv")
- [ ] Kontrollierte Migration bestehender `evidenzstufe`-Angaben auf claim-basierte Evidenz (siehe
      [Phase 3 Dokumentation](project/Phase_3_Scientific_Data_Architecture.md))

## Nicht geplant

- Keine Dosierungsrechner oder individualisierte Empfehlungen.
- Keine Nutzerkonten oder Community-Funktionen in dieser Phase.
- Kein vollautomatischer Artikelgenerator, keine automatisierte Literaturrecherche (siehe
  [Phase 3 Dokumentation](project/Phase_3_Scientific_Data_Architecture.md), Abschnitt „Grenzen der Phase").

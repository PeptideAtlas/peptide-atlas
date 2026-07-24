---
title: Release Strategy
description: Technische Release-Meilensteine für Peptide Atlas, unabhängig vom medizinischen Content-Fortschritt.
tags:
  - Architektur
  - Projekt
---

# Release Strategy

Diese Strategie beschreibt **ausschließlich technische und strukturelle** Meilensteine. Der inhaltliche Fortschritt (welche Wirkstoffe, Rezeptoren, Studien dokumentiert sind) wird separat über die inhaltliche [Roadmap](../roadmap.md) der Redaktion getrackt und **nicht** hier vorweggenommen.

## Meilensteine

### v0.1 — Grundgerüst (abgeschlossen)

- MkDocs Material Setup, Navigation, Suche, Tags, hell/dunkles Design
- GitHub Pages Deployment über GitHub Actions
- Redaktionelle Basisdokumente: Evidenzsystem, Redaktionsstandard, Artikelvorlage
- Erste Grundlagenartikel als Platzhalter/Entwurf

### v0.2 — Projektarchitektur (diese Phase)

- Vollständige Architektur-Dokumentation unter `docs/project/`
- Universelles Datenmodell entworfen (noch nicht implementiert)
- Knowledge-Graph-Denkmodell dokumentiert
- Empfehlungen zu Workflow, Naming, Versionierung dokumentiert (Umsetzung folgt in v0.3+)

### v0.3 — Struktur- und Prozess-Tooling

- Frontmatter-/Schema-Validator als CI-Schritt
- Branch-Protection auf `main` aktiviert (siehe [Workflow](Workflow.md))
- `CHANGELOG.md` eingeführt (siehe [Versioning](Versioning.md), aktuell fehlend)
- Erste strukturierte Datendateien (`data/`) nach dem [Data Model](Data_Model.md) angelegt — als Schema-Gerüst, nicht zwingend mit realen Inhalten

### v0.5 — Redaktioneller Regelbetrieb

- Erste real geprüfte, freigegebene Fachartikel (Status `Aktiv`) durch die wissenschaftliche Redaktion
- Reviewprozess gemäß [Editorial Policy](Editorial_Policy.md) im Alltagsbetrieb erprobt
- `LICENSE`-Datei ergänzt (aktuell fehlend, siehe technischer Übergabebericht)

### v1.0 — Produktionsreife Wissensbasis

- Grundabdeckung aller acht Content-Bereiche mit redaktionell freigegebenen Inhalten
- Stabile Informationsarchitektur (Navigation, Verlinkung) ohne grundlegende Strukturbrüche
- Öffentlich als „produktionsreif" kommunizierbar

### v2.0 — Strukturierte Plattform

- Knowledge Graph als eigenständiges, exportierbares Artefakt (siehe [Knowledge Graph](Knowledge_Graph.md))
- Perspektivisch read-only API (siehe [Architecture](Architecture.md))
- Erweiterte Suche, sobald der bestehende client-seitige Ansatz an Grenzen stößt

## Grundsatz

Jede Version erhöht **technische Reife**, nicht zwangsläufig Content-Menge. Ein Release kann „leer" an neuen Fachartikeln sein und trotzdem ein sinnvoller Versionssprung, wenn er z. B. Validierung, Sicherheit oder Struktur verbessert.

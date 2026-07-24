---
title: Naming Conventions
description: Einheitliche Benennungsregeln für Ordner, Dateien, IDs, JSON, Markdown und YAML in Peptide Atlas.
tags:
  - Architektur
  - Projekt
---

# Naming Conventions

## Ordner

- Content-Bereiche unter `docs/` behalten die bestehende Konvention: zweistelliges Zahlenpräfix + `lowercase_snake_case`, z. B. `00_grundlagen`, `02_biologie` (siehe bestehende Struktur in `README.md` im Repository-Root).
- Neue, nicht-inhaltliche Top-Level-Bereiche unter `docs/` (z. B. `docs/project/`) verwenden `lowercase`, ohne Zahlenpräfix, da sie keine fortlaufende Content-Kategorie sind.

## Content-Dateien (`docs/**`, außer `docs/project/`)

- `lowercase_snake_case.md`, deutsch, wie bisher etabliert (`was_sind_peptide.md`, `redaktionsstandard.md`).

## Architektur-/Projektdokumente (`docs/project/`)

- **Ausnahme von der obigen Regel**: Diese Dokumente verwenden `PascalCase_With_Underscores.md` (z. B. `Data_Model.md`), wie in Phase 2 explizit vorgegeben.
- Dies ist eine **bewusste Sonderkonvention** für diesen Bereich, kein Widerspruch, der sofort aufgelöst werden muss. Sie ist im [Decision Log](Decision_Log.md) als Entscheidung dokumentiert. Empfehlung für die Zukunft: langfristig auf eine einzige Konvention vereinigen, sobald ein größerer Umbau ohnehin ansteht — nicht isoliert nur deswegen.

## Objekt-IDs (künftiges Datenmodell)

- Format: `<typ>-<kebab-case-slug>`, ausschließlich ASCII, lowercase.
- Umlaute/Sonderzeichen werden transliteriert (ä → ae, ö → oe, ü → ue, ß → ss).
- IDs sind stabil: einmal vergeben, nie geändert oder wiederverwendet — auch nicht nach Löschung/Rückzug eines Objekts (siehe [Data Model](Data_Model.md)).
- Beispiele (rein illustrativ, keine echten Objekte): `drug-beispielsubstanz`, `receptor-beispielrezeptor-typ-1`.

## JSON

- Schlüssel: `snake_case`, **englisch** — für Kompatibilität mit gängigem Tooling, unabhängig von der deutschen Content-Sprache.
- Beispiel: `source_type`, `relation_type`, `last_reviewed` (siehe [Data Model](Data_Model.md)).
- Versionsfeld pro Datendatei nach [Versioning](Versioning.md).

## YAML-Frontmatter (Markdown-Artikel)

- Schlüssel: `snake_case`, **deutsch**, wo der [Redaktionsstandard](../00_grundlagen/redaktionsstandard.md) es vorgibt: `title`, `description`, `tags`, `status`, `evidenzstufe`, `quellen_typ`.
- Diese bewusste Abweichung (deutsche Frontmatter-Schlüssel vs. englische JSON-Schlüssel) ist im [Decision Log](Decision_Log.md) begründet: Frontmatter wird von der deutschsprachigen Redaktion direkt bearbeitet, JSON von technischem Tooling.

## Tags

- Singular, großgeschrieben, deutsch — wie bestehende Praxis (`Grundlagen`, `Biologie`, `Rezeptoren`).

## Git-Branches

- Siehe [Workflow](Workflow.md) für Präfixe (`content/`, `feature/`, `fix/`, `arch/`, `release/`).
- Nach dem Präfix: `lowercase-kebab-case`, kurz und beschreibend.

## Commit-Messages

- Kurze Betreffzeile im Präsens, optionaler Body mit Begründung (etablierte Praxis seit dem ersten Commit).
- Keine reinen „update"/„fix"-Betreffzeilen ohne Kontext.

## Git-Tags (Releases)

- Format: `vMAJOR.MINOR.PATCH` (siehe [Versioning](Versioning.md)), z. B. `v0.2.0`.

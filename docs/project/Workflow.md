---
title: Workflow
description: Empfohlener Git-Workflow für Peptide Atlas — Branches, Pull Requests, Reviews, Releases.
tags:
  - Architektur
  - Projekt
---

# Workflow

Dieses Dokument konkretisiert die im technischen Übergabebericht ausgesprochene Empfehlung: **Branch + Pull Request pro Änderung**, kein direkter Push auf `main`.

## Grundprinzip

`main` ist **immer deploybar**. Jede Änderung — Content, Konfiguration, Architektur-Dokumentation, Code — entsteht auf einem eigenen Branch und wird über einen Pull Request nach `main` gemergt.

## Branch-Typen

| Präfix | Verwendung | Beispiel |
|---|---|---|
| `content/` | Neuer oder geänderter Fachartikel | `content/wirkstoff-beispielpeptid` |
| `feature/` | Neue technische Funktionalität | `feature/frontmatter-validator` |
| `fix/` | Fehlerbehebung (Technik oder Redaktion) | `fix/tote-links-glossar` |
| `arch/` | Architektur-/Projektdokumentation | `arch/data-model-review` |
| `release/` | Vorbereitung eines Releases | `release/v0.3` |

Details zur Benennung siehe [Naming Conventions](Naming_Conventions.md).

## Pull-Request-Pflicht

- Kein direkter Commit auf `main`.
- Jeder Pull Request beschreibt **was** geändert wurde und **warum**.
- Pull Requests mit medizinischem Content verlinken die betroffenen Quellen und die Ziel-Statusstufe (siehe [Quality Standards](Quality_Standards.md)).

## Review-Pflicht

| PR-Typ | Erforderlicher Review |
|---|---|
| Technik/Infrastruktur (Code, `mkdocs.yml`, CI) | 1 technischer Review |
| Architektur-/Projektdokumentation (`docs/project/`) | 1 technischer Review |
| Medizinischer Content (`docs/00_grundlagen/` bis `docs/07_glossar/`) | Reviewkette gemäß [Editorial Policy](Editorial_Policy.md) |

## Merge-Strategie

**Squash-Merge** wird empfohlen: eine saubere, nachvollziehbare Historie auf `main`, während die Detail-Historie im Pull Request selbst erhalten bleibt.

## CI-Gate

Vor jedem Merge muss `mkdocs build --strict` erfolgreich durchlaufen (bereits als Teil von `.github/workflows/deploy.yml` etabliert). Empfohlene künftige Ergänzungen (siehe [Future Roadmap](Future_Roadmap.md)):

- Frontmatter-/Schema-Validator (Pflichtfelder gemäß [Quality Standards](Quality_Standards.md))
- Externer Link-Checker (ergänzend zum internen Linkcheck von `--strict`)

## Releases

Releases werden über Git-Tags (`vX.Y.Z`) markiert, siehe [Versioning](Versioning.md) und [Release Strategy](Release_Strategy.md). Ein `release/`-Branch dient nur der letzten Abstimmung vor dem Tag, nicht der laufenden Entwicklung.

## Branch-Schutz (empfohlen, aktuell nicht aktiv)

Zum jetzigen Zeitpunkt ist `main` **nicht** über GitHub Branch-Protection-Regeln geschützt (siehe technischer Übergabebericht). Empfehlung für die nahe Zukunft:

- Pflicht-Review vor Merge
- Pflicht-Status-Check „Deploy MkDocs to GitHub Pages" muss grün sein
- Kein Force-Push auf `main`

Diese Aktivierung liegt in der Verantwortung der Repository-Administration und wird hier nur empfohlen, nicht automatisch umgesetzt (siehe [Decision Log](Decision_Log.md)).

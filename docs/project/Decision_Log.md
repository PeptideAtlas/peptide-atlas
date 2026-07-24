---
title: Decision Log
description: Protokoll getroffener und vorgeschlagener Architekturentscheidungen für Peptide Atlas.
tags:
  - Architektur
  - Projekt
---

# Decision Log

Kurze, strukturierte Architecture Decision Records (ADRs): Kontext, Entscheidung, Konsequenz. Neue Entscheidungen werden **angehängt**, bestehende Einträge werden nicht rückwirkend verändert — bei Revision wird ein neuer Eintrag ergänzt, der auf den alten verweist.

| ID | Titel | Status | Kurzfassung |
|---|---|---|---|
| ADR-0001 | MkDocs Material statt individuellem Framework | Entschieden (v0.1) | Ausgereiftes, wartungsarmes Static-Site-Framework mit nativer Suche/Tags/Theming — passend zu einer reinen Content-Plattform ohne Backend-Bedarf. |
| ADR-0002 | GitHub Actions Deployment statt `gh-pages`-Branch | Entschieden (v0.1) | Modernere offizielle Methode (`upload-pages-artifact`/`deploy-pages`), kein separater Branch, kein zusätzliches Push-Token nötig. |
| ADR-0003 | Deutschsprachiger Content, englische Fachbegriffe erlaubt | Entschieden (v0.1) | Zielgruppe ist primär deutschsprachig; etablierte englische Fachtermini (GPCR, Research Peptide …) werden nicht künstlich eingedeutscht. |
| ADR-0004 | Evidenzsystem A–E als verbindliches Bewertungsschema | Entschieden (v0.1) | Einheitliche, einfache Klassifikation der Belegstärke, siehe [Evidenzsystem](../00_grundlagen/evidenzsystem.md). |
| ADR-0005 | Architektur-Dokumente in `docs/project/` mit eigener Namenskonvention | Entschieden (v0.2) | `PascalCase_With_Underscores.md` als bewusste Ausnahme zur sonstigen `lowercase_snake_case`-Konvention der Content-Dateien — explizit vorgegebenes Format für diese Dokumentkategorie, siehe [Naming Conventions](Naming_Conventions.md). Empfehlung: langfristig vereinheitlichen, aber nicht isoliert deswegen migrieren. |
| ADR-0006 | Mermaid-Diagramme aktiviert | Entschieden (v0.2) | `pymdownx.superfences` um `custom_fences` für `mermaid` ergänzt, um Architektur- und Graph-Diagramme direkt in Markdown darstellen zu können — keine externe Abhängigkeit, da in MkDocs Material bereits gebündelt. |
| ADR-0007 | Markdown+Frontmatter bleibt vorerst alleinige Source of Truth | Entschieden (v0.2) | Strukturierte Daten (`data/*.json`) und Knowledge Graph werden **abgeleitet**, nicht umgekehrt. Verhindert doppelte Pflege und Synchronisationsprobleme, solange kein konkreter Anwendungsfall eine andere Quelle erfordert. Siehe [Architecture](Architecture.md), [Knowledge Graph](Knowledge_Graph.md). |
| ADR-0008 | Evidenz wird an Beziehungen (Edges), nicht an Objekten (Nodes) verankert | Entschieden (v0.2) | Ein Objekt wie ein Wirkstoff hat keine einzelne Evidenzstufe — jede einzelne Aussage/Beziehung über ihn hat ihre eigene. Siehe [Data Model](Data_Model.md). |
| ADR-0009 | Neuer Status `Zurückgezogen` vorgeschlagen | Vorgeschlagen, nicht umgesetzt (v0.2) | Ergänzung zum bestehenden Status-Schema (`Entwurf`/`In Prüfung`/`Aktiv`) im [Redaktionsstandard](../00_grundlagen/redaktionsstandard.md), für veraltete/widerrufene, aber aus Transparenzgründen weiter sichtbare Artikel. Muss vor Einführung mit der Redaktion abgestimmt werden. |
| ADR-0010 | Branch-Protection auf `main` empfohlen | Vorgeschlagen, nicht umgesetzt | Repository ist öffentlich, `main` deployt automatisch — Pflicht-Review und Pflicht-CI-Check werden empfohlen. Umsetzung liegt bei der Repository-Administration, siehe [Workflow](Workflow.md). |
| ADR-0011 | `data/catalog.json` perspektivisch in typ-spezifische Dateien aufteilen | Vorgeschlagen, nicht umgesetzt | Statt eines einzelnen Katalogs künftig z. B. `data/drugs.json`, `data/receptors.json` gemäß [Data Model](Data_Model.md) — erst sinnvoll, sobald reale Einträge entstehen. |
| ADR-0012 | `CHANGELOG.md` einführen | Vorgeschlagen, nicht umgesetzt | Aktuell fehlt eine zusammenfassende Änderungsdokumentation auf Repository-Ebene, siehe [Versioning](Versioning.md). Empfohlen ab v0.3. |
| ADR-0013 | `LICENSE`-Datei ergänzen | Vorgeschlagen, nicht umgesetzt | Repository ist öffentlich, aber unlizenziert (bestätigt über GitHub-API, 404 auf `/license`). Rechtlich zu klären, bevor Dritte substanziell beitragen oder Inhalte nachnutzen. |
| ADR-0014 | Frontmatter-/Schema-Validator als CI-Schritt | Vorgeschlagen, nicht umgesetzt | Automatisierte Prüfung der Pflichtfelder aus [Quality Standards](Quality_Standards.md) — technisch sinnvoll, aber erst mit wachsender Artikelzahl priorisiert. |

## Format für neue Einträge

```markdown
### ADR-00XX: <Titel>
- **Status:** Entschieden | Vorgeschlagen | Verworfen
- **Datum:** YYYY-MM-DD
- **Kontext:** Was war die Ausgangslage/das Problem?
- **Entscheidung:** Was wurde entschieden?
- **Konsequenzen:** Was folgt daraus, welche Alternativen wurden verworfen und warum?
```

---
title: Glossary for Developers
description: Technisches Glossar für Entwickler:innen, die an Peptide Atlas mitarbeiten.
tags:
  - Architektur
  - Projekt
  - Glossar
---

# Glossary for Developers

Ein technisches Begriffsglossar — zur Abgrenzung vom fachlich-medizinischen [Glossar](../07_glossar/index.md) im Content-Bereich.

| Begriff | Bedeutung im Kontext von Peptide Atlas |
|---|---|
| **Frontmatter** | Der YAML-Block am Anfang einer Markdown-Datei (zwischen `---`), der strukturierte Metadaten trägt (`title`, `status`, `evidenzstufe` …). |
| **Node** | Ein einzelnes Objekt im [Knowledge Graph](Knowledge_Graph.md), entspricht einem Objekttyp aus dem [Data Model](Data_Model.md). |
| **Edge** | Eine gerichtete, typisierte Beziehung zwischen zwei Nodes im [Knowledge Graph](Knowledge_Graph.md), mit eigenen Quellen und Evidenzstufe. |
| **Knowledge Graph** | Die graphbasierte Repräsentation aller Objekte und ihrer Beziehungen — siehe [Knowledge Graph](Knowledge_Graph.md). |
| **SemVer** | *Semantic Versioning* — Versionsschema `MAJOR.MINOR.PATCH`, siehe [Versioning](Versioning.md). |
| **Static Site Generator (SSG)** | Werkzeug, das aus Markdown-Quelldateien eine fertige, statische HTML-Website erzeugt — hier: MkDocs Material. |
| **CI/CD** | *Continuous Integration / Continuous Deployment* — hier umgesetzt über GitHub Actions (`.github/workflows/deploy.yml`). |
| **Build-Artefakt** | Das Ergebnis eines Build-Vorgangs — hier: der Ordner `site/`, erzeugt durch `mkdocs build`. |
| **Branch Protection** | GitHub-Funktion, die Regeln für einen Branch erzwingt (z. B. Pflicht-Review vor Merge). Für `main` empfohlen, siehe [Workflow](Workflow.md). |
| **ADR (Architecture Decision Record)** | Kurzes, strukturiertes Protokoll einer Architekturentscheidung (Kontext, Entscheidung, Konsequenz) — hier geführt im [Decision Log](Decision_Log.md). |
| **Slug** | URL-/ID-tauglicher Kurzname, meist `lowercase-kebab-case`, siehe [Naming Conventions](Naming_Conventions.md). |
| **Source of Truth** | Die Stelle, an der eine Information *verbindlich* gepflegt wird. Für Peptide Atlas aktuell: die Markdown-Dateien in `docs/` (siehe [Architecture](Architecture.md)). |
| **Schema** | Die formale Struktur- und Feldbeschreibung eines Datentyps — siehe [Data Model](Data_Model.md). |
| **Static-First** | Architekturprinzip: so lange wie möglich ohne eigenen Server auskommen, siehe [Architecture](Architecture.md). |
| **Evidenzstufe** | Redaktionelle Kennzeichnung der Belegstärke einer Aussage (A–E), siehe [Evidenzsystem](../00_grundlagen/evidenzsystem.md) — kein rein technischer, aber für das Datenmodell zentraler Begriff. |
| **Relation** | Im [Data Model](Data_Model.md) verwendetes Synonym für Edge/Beziehung zwischen zwei Objekten. |
| **`--strict`-Build** | `mkdocs build --strict` — bricht bei Konfigurations- oder internen Link-Warnungen ab, dient als CI-Qualitätsgate. |

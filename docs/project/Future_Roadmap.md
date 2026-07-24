---
title: Future Roadmap
description: Technischer Ausblick auf 3–5 Jahre für Peptide Atlas.
tags:
  - Architektur
  - Projekt
---

# Future Roadmap

Ein technischer 3–5-Jahres-Ausblick, bewusst getrennt vom inhaltlichen Fortschritt (siehe [Release Strategy](Release_Strategy.md) für die Abgrenzung zur inhaltlichen [Roadmap](../roadmap.md)). Einige Punkte sind bewusst als **offene Fragen** markiert, nicht als feste Entscheidung.

## Jahr 1 — Fundament festigen

- Frontmatter-/Schema-Validator in CI (siehe [Quality Standards](Quality_Standards.md), [Decision Log](Decision_Log.md) ADR-0014)
- Branch-Protection auf `main` (siehe [Workflow](Workflow.md), ADR-0010)
- `CHANGELOG.md` und `LICENSE` ergänzen (ADR-0012, ADR-0013)
- Redaktioneller Regelbetrieb etabliert (siehe [Release Strategy](Release_Strategy.md) v0.5)

## Jahr 2 — Strukturierte Daten

- Erste typ-spezifische Datendateien nach dem [Data Model](Data_Model.md) (z. B. `data/drugs.json`, `data/receptors.json`)
- Automatisierte Referenzintegritätsprüfung (existiert jede in einer Relation referenzierte ID auch als Objekt?)
- Erweiterte Suche, falls die client-seitige Suche bei wachsendem Content spürbar an Grenzen stößt (z. B. Pagefind oder ein gehosteter Suchindex)

## Jahr 3 — Knowledge Graph als eigenständiges Artefakt

- Export des [Knowledge Graph](Knowledge_Graph.md) in ein Standardformat (JSON-LD oder GraphML)
- Read-only API auf Basis der strukturierten Daten (siehe [Architecture](Architecture.md)) — zunächst statisch generiert, nur bei konkretem Bedarf als echter Dienst
- Automatisierte Beziehungsvorschläge (mit verpflichtendem redaktionellen Review, siehe [Knowledge Graph](Knowledge_Graph.md), Abschnitt „Automatisch entstehende Beziehungen")

## Jahr 4 — Interaktive Nutzung

- Interaktive Visualisierung von Signalwegen und Rezeptor-Liganden-Netzwerken auf Basis des Graphs
- Studienbrowser: filterbare Übersicht über `Study`-Objekte (Studientyp, Phase, Registrierungsstatus)
- Vergleichssystem: UI-Ebene über `COMPARED_TO`/`SIMILAR_TO`-Beziehungen für den Content-Bereich [Vergleiche](../05_vergleiche/index.md)

## Jahr 5 — Reichweite

- Mehrsprachigkeit (z. B. `mkdocs-static-i18n` oder dedizierte Übersetzungspipeline) — Vorbereitung dazu bereits in `mkdocs.yml` (`theme.language: de`) angelegt, siehe [Architecture](Architecture.md)
- Evaluierung einer mobil optimierten Variante bzw. PWA — **offene Frage**, ob das eigenständige App-Entwicklung erfordert oder über responsive Web-Optimierung ausreichend abgedeckt ist
- KI-gestützte Redaktionsassistenz als festes Werkzeug (Vorschläge, niemals autonome Veröffentlichung, siehe [Contribution Guide](Contribution_Guide.md))

## Offene, bewusst ungeklärte Fragen

- Wird jemals eine echte Datenbank/ein echtes Backend benötigt, oder reicht „Static-First" (siehe [Architecture](Architecture.md)) dauerhaft aus? Abhängig davon, ob künftige Features (z. B. Nutzerinteraktion) das zwingend erfordern.
- Ab welcher Content-Menge lohnt sich ein Wechsel der Suchlösung? Kein fester Schwellenwert, sondern anhand konkret beobachteter Einschränkungen zu entscheiden.
- Soll der Knowledge Graph irgendwann öffentlich per API abfragbar sein, oder nur als Download-Artefakt (JSON-LD/GraphML) angeboten werden? Sicherheits- und Missbrauchsaspekte sind vor einer Entscheidung zu prüfen.

Diese Roadmap ist eine **Leitplanke**, kein verbindlicher Fahrplan. Jede Stufe wird erst konkretisiert, wenn die vorherige abgeschlossen ist (siehe [Release Strategy](Release_Strategy.md)).

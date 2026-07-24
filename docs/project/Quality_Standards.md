---
title: Quality Standards
description: Pflichtfelder, Pflichtquellen und Veröffentlichungskriterien für Inhalte in Peptide Atlas.
tags:
  - Architektur
  - Projekt
  - Redaktion
---

# Quality Standards

Konkrete, prüfbare Mindeststandards, die ein Artikel erfüllen muss, um einen bestimmten Status zu erreichen. Ergänzt den [Redaktionsstandard](../00_grundlagen/redaktionsstandard.md) und die [Editorial Policy](Editorial_Policy.md) um überprüfbare Kriterien.

## Pflichtfelder (Frontmatter)

Für jeden Content-Artikel (nicht: Architektur-/Projektdokumente):

| Feld | Pflicht | Bemerkung |
|---|---|---|
| `title` | ja | |
| `description` | ja | Ein-Satz-Zusammenfassung |
| `tags` | ja | mind. 1 Tag |
| `status` | ja | `Entwurf` \| `In Prüfung` \| `Aktiv` |
| `evidenzstufe` | ja, sobald medizinisch relevante Aussagen enthalten sind | `A`–`E` oder `Nicht zutreffend` |
| `quellen_typ` | empfohlen | gemäß Artikelvorlage unter `templates/artikelvorlage.md` im Repository |
| `last_reviewed` | empfohlen ab Status `In Prüfung` | siehe [Editorial Policy](Editorial_Policy.md) |

## Pflichtquellen

- Jede medizinisch relevante Aussage benötigt mindestens eine Quelle (siehe [Redaktionsstandard](../00_grundlagen/redaktionsstandard.md)).
- Bevorzugt werden Primärquellen: registrierte klinische Studien, peer-reviewte Publikationen, offizielle Zulassungsdokumente.
- Sekundärquellen (Reviews, Leitlinien) sind zulässig, ersetzen aber keine Primärquelle bei zentralen Aussagen.
- Händlerangaben sind als Quelle zulässig, **nur** wenn explizit als solche gekennzeichnet (`source_type: Händlerangabe`, siehe [Data Model](Data_Model.md)) und nie als alleiniger Beleg für eine Wirksamkeitsaussage.

## Reviewprozess (Checkliste vor Merge)

Ein Pull Request mit Content-Änderungen wird erst gemerged, wenn:

- [ ] Alle Pflichtfelder gesetzt sind
- [ ] Jede medizinisch relevante Aussage eine Quelle **und** eine Evidenzstufe hat
- [ ] Zulassung, klinische Forschung, präklinische Forschung und Händlerangaben klar getrennt sind
- [ ] Keine Dosierungsanleitung, kein Selbstbehandlungsprotokoll enthalten ist
- [ ] Keine Werbeaussage oder kein Heilsversprechen enthalten ist
- [ ] Unsichere/experimentelle Angaben sichtbar gekennzeichnet sind
- [ ] Interne Links funktionieren (`mkdocs build --strict` ist grün)
- [ ] Bei Status-Übergang `In Prüfung` → `Aktiv`: zweiter unabhängiger fachlicher Review erfolgt ist (siehe [Editorial Policy](Editorial_Policy.md))

## Statuslogik

| Status | Voraussetzung, um in diesem Status zu **bleiben** | Voraussetzung für **nächsten** Status |
|---|---|---|
| `Entwurf` | Grundgerüst (Frontmatter, Struktur) vorhanden, Inhalte/Quellen dürfen unvollständig sein | Inhalte und Quellen vollständig, Checkliste oben erfüllbar |
| `In Prüfung` | Inhalte vollständig, mind. 1 fachlicher Review ausstehend oder erfolgt | Zweiter unabhängiger fachlicher Review bestätigt Inhalt |
| `Aktiv` | Vollständig geprüft und freigegeben, `last_reviewed` gepflegt | — (Änderungen an Kernaussagen setzen zurück auf `In Prüfung`) |
| `Zurückgezogen` | Inhalt ist veraltet/widerrufen, bleibt aus Transparenzgründen sichtbar, aber klar gekennzeichnet | — |

`Zurückgezogen` ist ein in dieser Phase neu vorgeschlagener Status (siehe [Data Model](Data_Model.md), [Decision Log](Decision_Log.md)) — bisher nicht Teil des bestehenden Redaktionsstandards und dort zu ergänzen, sobald der erste Anwendungsfall auftritt.

## Wann ein Artikel NICHT veröffentlicht werden darf

- Fehlende Quelle für eine medizinisch relevante Aussage
- Vermischung der vier Ebenen (Zulassung/klinisch/präklinisch/Händler)
- Enthält Dosierungsangaben oder Handlungsanleitungen
- Enthält Werbesprache oder Heilsversprechen
- `evidenzstufe` fehlt, obwohl medizinisch relevante Aussagen enthalten sind

## Automatisierung (Ausblick, nicht in dieser Phase umgesetzt)

Ein CI-Schritt könnte künftig automatisiert prüfen: Pflichtfelder vorhanden, `evidenzstufe` aus gültiger Werteliste, keine toten internen Links (über `--strict` hinaus auch externe Links). Diese Automatisierung ist als offener Punkt in [Future Roadmap](Future_Roadmap.md) und [Decision Log](Decision_Log.md) vermerkt, aber bewusst noch nicht implementiert.

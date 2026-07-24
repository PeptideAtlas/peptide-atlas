---
title: Editorial Policy
description: Redaktionelle Grundsätze für Peptide Atlas — Quellenpflicht, Neutralität, Interessenkonflikte, Review- und Korrekturprozess.
tags:
  - Architektur
  - Projekt
  - Redaktion
---

# Editorial Policy

Dieses Dokument ergänzt den bestehenden [Redaktionsstandard](../00_grundlagen/redaktionsstandard.md) und das [Evidenzsystem](../00_grundlagen/evidenzsystem.md) um die organisatorischen Prozesse dahinter. Inhaltliche Regeln (Quellenpflicht, Trennung der Ebenen, verbotene Inhalte) sind dort verbindlich definiert — hier geht es um **wer** sie **wie** durchsetzt.

## Quellenpflicht (Verweis)

Verbindlich gemäß [Redaktionsstandard](../00_grundlagen/redaktionsstandard.md): keine medizinisch relevante Aussage ohne nachvollziehbare Quelle, keine Vermischung von Zulassung, klinischer Forschung, präklinischer Forschung und Händlerangaben.

## Neutralität

- Aussagen werden so formuliert, dass ihre tatsächliche Evidenzstärke nicht sprachlich auf- oder abgewertet wird (siehe [Evidenzsystem](../00_grundlagen/evidenzsystem.md), Grundregel 4).
- Unsicherheit und widersprüchliche Datenlage werden sichtbar dargestellt, nicht geglättet.
- Kein Artikel bevorzugt einen einzelnen Anbieter, Hersteller oder Händler gegenüber einem anderen.

## Interessenkonflikte

- Beitragende (menschlich oder KI-gestützt) mit einer wirtschaftlichen Verbindung zu einem im Artikel behandelten Unternehmen (z. B. Hersteller, Vertrieb) legen diese Verbindung im Pull Request offen.
- Bezahlte Platzierung, gesponserte Inhalte oder bevorzugte Darstellung gegen Entgelt sind ausgeschlossen.
- Handelsnamen werden ausschließlich nach der bestehenden Regel geführt: nur wenn die genaue Zusammensetzung dokumentiert und belegt ist (siehe [Redaktionsstandard](../00_grundlagen/redaktionsstandard.md)).

## Reviewprozess

| Änderungstyp | Mindest-Review |
|---|---|
| Neuer Entwurfsartikel (Status `Entwurf`) | 1 technischer Review (Struktur, Frontmatter, Build) |
| Übergang `Entwurf` → `In Prüfung` | 1 fachlicher Review durch die wissenschaftliche Redaktion |
| Übergang `In Prüfung` → `Aktiv` | 1 zusätzlicher, unabhängiger fachlicher Review (Vier-Augen-Prinzip) |
| Änderung an einem `Aktiv`-Artikel mit Auswirkung auf Evidenzstufe oder Kernaussage | wie Neuveröffentlichung — erneut 2 fachliche Reviews |
| Rein redaktionelle/technische Korrektur (Tippfehler, Linkfix) ohne inhaltliche Auswirkung | 1 Review genügt |

Details zu den Statuswerten selbst siehe [Quality Standards](Quality_Standards.md).

## Korrekturprozess

1. Fehler oder veraltete Inhalte werden als GitHub Issue gemeldet (siehe Kontakt-Hinweis im [Haftungshinweis](../haftungshinweis.md)) oder direkt per Pull Request korrigiert.
2. Jede Korrektur an einem `Aktiv`-Artikel durchläuft denselben Reviewprozess wie eine inhaltliche Änderung (siehe Tabelle oben).
3. Korrekturen werden nicht überschrieben, sondern versioniert — die vorherige Aussage bleibt über die Git-Historie nachvollziehbar.

## Versionshistorie

- **Technische Versionshistorie**: vollständig über Git (Commits, Pull-Request-Historie).
- **Redaktionelle Versionshistorie**: empfohlene Frontmatter-Felder `last_reviewed` (Datum der letzten Prüfung) und `reviewed_by` (Rolle/Kürzel, kein Klarname) — siehe [Data Model](Data_Model.md). Aktuell in den bestehenden Artikeln noch nicht durchgängig gepflegt (siehe [Decision Log](Decision_Log.md), offener Punkt).
- Ein zusammenfassendes Änderungsprotokoll auf Plattformebene wird über [Release Strategy](Release_Strategy.md) und [Versioning](Versioning.md) geführt.

## Datenschutz bei Reviewer-Angaben

Um Reviewer:innen nicht unnötig öffentlich zu exponieren, werden im Frontmatter Rollen oder Kürzel statt Klarnamen empfohlen. Die vollständige Nachvollziehbarkeit bleibt über die Git-Commit-Historie (mit den dort ohnehin sichtbaren Autor:innen) gewährleistet.

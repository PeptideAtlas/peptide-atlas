---
title: Versioning
description: Versionierungsmodell für Plattform, Artikel und Datenschema in Peptide Atlas.
tags:
  - Architektur
  - Projekt
---

# Versioning

Peptide Atlas versioniert auf drei unabhängigen Ebenen, die absichtlich **nicht** synchron laufen müssen.

## 1. Plattform-Versionierung

- [Semantic Versioning](https://semver.org/) (`MAJOR.MINOR.PATCH`), markiert über Git-Tags `vX.Y.Z`.
- **MAJOR**: grundlegender Strukturbruch (z. B. Wechsel der Informationsarchitektur, inkompatible Datenmodell-Änderung).
- **MINOR**: neue technische Fähigkeit ohne Strukturbruch (z. B. neues Tooling, neue Content-Sektion).
- **PATCH**: Fehlerbehebungen, redaktionelle Korrekturen ohne strukturelle Auswirkung.
- Meilensteine siehe [Release Strategy](Release_Strategy.md).
- **Offener Punkt:** Es existiert aktuell kein `CHANGELOG.md` im Repository. Empfehlung: ab v0.3 einführen (siehe [Decision Log](Decision_Log.md)).

## 2. Artikel-Versionierung

- Primäre Quelle: Git-Historie der jeweiligen Markdown-Datei.
- Ergänzend empfohlen (siehe [Data Model](Data_Model.md), [Editorial Policy](Editorial_Policy.md)): Frontmatter-Felder `last_reviewed` (Datum) und `reviewed_by` (Rolle/Kürzel).
- Artikel selbst tragen **keine** eigene SemVer-Nummer — ihr Reifegrad wird über `status` (`Entwurf`/`In Prüfung`/`Aktiv`/`Zurückgezogen`) ausgedrückt, nicht über eine Versionsnummer (siehe [Quality Standards](Quality_Standards.md)).

## 3. Daten-/Schema-Versionierung

- Das Datenmodell selbst (siehe [Data Model](Data_Model.md)) entwickelt sich unabhängig von der Plattformversion und trägt eine eigene SemVer-Nummer.
- Bestehendes Beispiel: `data/catalog.json` enthält bereits ein `version`-Feld (`"0.1.0"`), unabhängig von der Plattformversion `v0.1`.
- Empfehlung: jede strukturelle Änderung am Datenmodell (neues Pflichtfeld, geänderter Beziehungstyp) erhöht die Schema-Version und wird im [Decision Log](Decision_Log.md) als Entscheidung festgehalten.

## Warum getrennt?

Eine Änderung an der Redaktionsrichtlinie (Plattform-Ebene) erfordert keine neue Datenschema-Version. Umgekehrt kann ein neues Pflichtfeld im Datenmodell eingeführt werden, ohne dass sich an der Navigation oder Optik der Plattform etwas ändert. Die Trennung verhindert, dass unabhängige Änderungen künstlich an eine gemeinsame Versionsnummer gekoppelt werden.

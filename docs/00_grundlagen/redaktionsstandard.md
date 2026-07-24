---
title: Redaktionsstandard
description: Verbindliche redaktionelle Regeln für alle Inhalte in Peptide Atlas.
tags:
  - Grundlagen
  - Methodik
status: Aktiv
---

# Redaktionsstandard

Diese Regeln gelten verbindlich für alle Inhalte in Peptide Atlas.

## Quellenpflicht

- Jede medizinisch relevante Aussage muss eine nachvollziehbare Quelle haben (Studie, Leitlinie, Zulassungsdokument).
- Quellen werden am Ende jedes Artikels im Abschnitt „Quellen" aufgeführt und, wo möglich, im Fließtext direkt referenziert.
- Die Evidenzstärke jeder Aussage folgt dem [Evidenzsystem](evidenzsystem.md). Seit Phase 3 gilt das
  claim-basierte Modell (Evidenzkategorie getrennt von Sicherheit) für neue wissenschaftliche Objektseiten; das
  bisherige `evidenzstufe`-Feld (A–E) ist Legacy und wird für bestehende Artikel weiter toleriert, aber nicht
  mehr neu vergeben.
- Neue Objektseiten verweisen im Frontmatter über `entity_id` und `claim_ids` auf die strukturierten Daten unter
  `data/` (siehe `data/README.md` im Repository sowie
  [Phase 3 Dokumentation](../project/Phase_3_Scientific_Data_Architecture.md)) — der Claim, nicht der Artikel,
  trägt die Quelle und die Evidenzbewertung.

## Trennung der Ebenen

Folgende vier Ebenen werden in jedem Artikel klar getrennt dargestellt und nie vermischt:

1. **Zulassung** — behördlich zugelassene Indikationen und Anwendungen.
2. **Klinische Forschung** — Studien am Menschen außerhalb zugelassener Indikationen.
3. **Präklinische Forschung** — Tier- und Zellstudien.
4. **Händlerangaben** — Aussagen von Anbietern/Herstellern, die nicht mit wissenschaftlicher Evidenz gleichzusetzen sind und explizit als solche gekennzeichnet werden.

## Was nicht ergänzt wird

- Keine Dosierungsanleitungen oder Selbstbehandlungsprotokolle.
- Keine medizinischen Empfehlungen oder individuellen Therapieratschläge.
- Keine Werbeaussagen oder Heilsversprechen.
- Handelsnamen von Produktmischungen (z. B. „GLOW", „KLOW") werden nur geführt, wenn die genaue Zusammensetzung dokumentiert und belegt ist.
- Der Begriff „Research Peptide" wird nicht als Qualitäts- oder Reinheitsmerkmal dargestellt.

## Umgang mit Unsicherheit

Unsichere, vorläufige oder widersprüchliche Angaben werden sichtbar als **unklar** oder **experimentell** gekennzeichnet, z. B. mit einem Admonition-Block:

```markdown
!!! warning "Experimentell / unklare Datenlage"
    Diese Aussage beruht auf vorläufigen Daten und ist nicht als gesichert zu betrachten.
```

## Artikelaufbau

Jeder Artikel verwendet:

- YAML-Frontmatter mit mindestens `title`, `description`, `tags`, `status` (siehe Artikelvorlage unter `templates/artikelvorlage.md` im Repository)
- Klare Überschriftenstruktur (H1 einmalig als Titel, danach H2/H3)
- Einen abschließenden Abschnitt „Quellen"

## Status-Kennzeichnung

| Status | Bedeutung |
|---|---|
| Entwurf | Grundgerüst vorhanden, Inhalte/Quellen unvollständig |
| In Prüfung | Inhalte vollständig, redaktionelle Prüfung ausstehend |
| Aktiv | Geprüft und freigegeben |

---
title: Vision
description: Langfristige Vision der Plattform Peptide Atlas.
tags:
  - Architektur
  - Projekt
---

# Vision

## Die langfristige Vision

Peptide Atlas soll zu einer der weltweit hochwertigsten, evidenzbasierten Wissensplattformen für Peptide, peptidbasierte Arzneimittel, Rezeptoren, Signalwege, Studien, Erkrankungen, Pharmakologie und Biomedizin werden.

Nicht als loses Nachschlagewerk, sondern als **strukturierte, überprüfbare und langfristig wartbare Wissensbasis**, die sowohl von Menschen gelesen als auch von Maschinen ausgewertet werden kann.

## Was wir bauen

Eine **professionelle Knowledge Base** mit folgenden Eigenschaften:

- **Kuratiert statt offen** — Inhalte durchlaufen einen definierten Redaktionsprozess (siehe [Editorial Policy](Editorial_Policy.md)), keine anonyme Freitextbearbeitung.
- **Belegpflichtig statt frei** — jede medizinisch relevante Aussage ist mit Quelle und Evidenzstufe versehen (siehe [Evidenzsystem](../00_grundlagen/evidenzsystem.md)).
- **Strukturiert statt nur Fließtext** — Inhalte sind zusätzlich zur lesbaren Markdown-Form als strukturierte Daten und perspektivisch als Graph modelliert (siehe [Data Model](Data_Model.md), [Knowledge Graph](Knowledge_Graph.md)).
- **Neutral statt kommerziell** — keine Werbeaussagen, keine Heilsversprechen, keine bevorzugte Darstellung einzelner Anbieter.
- **Nachvollziehbar statt anonym** — Versionshistorie, Review-Verantwortung und Änderungsgründe sind jederzeit rekonstruierbar.

## Was wir NICHT bauen

- **Nicht Wikipedia** — kein offenes Wiki-Modell mit anonymer Sofort-Bearbeitung und Konsensfindung durch Mehrheitsmeinung. Stattdessen: definierte redaktionelle Verantwortung und ein festes Evidenzsystem statt „neutraler Standpunkt" durch Diskussion.
- **Nicht ein Blog** — keine chronologischen Meinungsartikel, keine Autorenperspektive, keine Spekulation. Jeder Artikel ist ein lebendes, versioniertes Referenzdokument, kein Zeitpunkt-Beitrag.
- **Nicht eine Verkaufsplattform** — keine Produktplatzierung, keine Handelsnamen als Qualitätsmerkmal, keine Vermischung von Händlerangaben mit wissenschaftlicher Evidenz (siehe [Redaktionsstandard](../00_grundlagen/redaktionsstandard.md)).

## Abgrenzung im Detail

| Dimension | Wikipedia | Kommerzielle Seiten | Peptide Atlas |
|---|---|---|---|
| Bearbeitung | Offen, anonym | Redaktionell, oft werblich motiviert | Redaktionell, fachlich verantwortet |
| Evidenzkennzeichnung | Uneinheitlich | Meist keine | Verbindliches A–E-System |
| Struktur | Freier Fließtext | Freier Fließtext, SEO-optimiert | Fließtext + strukturiertes Datenmodell + Graph |
| Trennung Zulassung/Forschung/Marketing | Selten explizit | Meist vermischt | Strikt getrennt (Pflicht) |
| Ziel | Allgemeinwissen | Verkauf/Traffic | Fachlich verlässliche Referenz |
| Maschinenlesbarkeit | Gering (Wikidata separat) | Gering | Von Anfang an mitgedacht |

## Werte

1. **Wissenschaftlichkeit vor Vollständigkeit** — lieber ein kurzer, korrekt belegter Artikel als ein langer, unbelegter.
2. **Transparenz** — jede Aussage ist auf ihre Quelle und Evidenzstufe zurückführbar.
3. **Sorgfalt vor Geschwindigkeit** — kein Artikel wird veröffentlicht, nur um Lücken zu füllen.
4. **Sicherheit** — keine Inhalte, die als Handlungsanleitung missverstanden werden können.
5. **Offenheit der Plattform, Verantwortung bei den Inhalten** — die technische Infrastruktur ist offen (öffentliches Repository), die inhaltliche Freigabe bleibt redaktionell kontrolliert.

## Zeithorizont

Diese Vision ist auf **5+ Jahre** angelegt. Der [Future Roadmap](Future_Roadmap.md) beschreibt, welche technischen Ausbaustufen dorthin führen; die [Release Strategy](Release_Strategy.md) beschreibt die konkreten Versionsschritte.

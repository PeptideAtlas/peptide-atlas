---
title: Phase 3 – Scientific Data Architecture
description: Konkrete, getestete technische Umsetzung der wissenschaftlichen Datenarchitektur von Peptide Atlas.
tags:
  - Architektur
  - Projekt
  - Datenmodell
---

# Phase 3 – Scientific Data Architecture

Phase 2 ([Data Model](Data_Model.md), [Knowledge Graph](Knowledge_Graph.md)) hat die langfristige Architektur als
Leitplanke beschrieben, aber bewusst nicht implementiert (siehe ADR-0007). Phase 3 macht daraus eine konkrete,
getestete und erweiterbare technische Grundlage: JSON Schemas, eine YAML-Datenebene, ein Claim-basiertes
Evidenzmodell, einen Validator, einen Katalog- und Graphexport sowie CI-Integration.

!!! warning "Kein medizinischer Content in dieser Phase"
    Diese Phase enthaelt ausschliesslich technische Platzhalterdaten (`Placeholder Substance`, `Placeholder
    Receptor`, ...). Keine reale Substanz, kein reales Studienergebnis, keine reale Wirksamkeits- oder
    Sicherheitsaussage ist Teil dieser Implementierung. Siehe Abschnitt „Nicht-Ziele" und [Future
    Roadmap](Future_Roadmap.md)/[Roadmap](../roadmap.md) fuer Phase 4.

## Ziel von Phase 3

Peptide Atlas soll langfristig mindestens 5.000 Wirkstoff-/Fachartikel, 100.000 Quellen, mehrere Sprachen,
automatisierte Vergleichstabellen, PDF-Generierung, eine read-only API, einen Knowledge Graph, wissenschaftliche
Diagramme, KI-gestuetzte redaktionelle Prozesse, mobile Anwendungen und langfristige Versions-/Quellenhistorien
tragen koennen. Ziel dieser Phase ist nicht, moeglichst schnell erste Wirkstoffartikel zu veroeffentlichen,
sondern eine belastbare Datenarchitektur zu schaffen, die diese Groessenordnungen unterstuetzen kann, ohne
grundlegend neu gebaut werden zu muessen.

## Data-First Hybridmodell

Ab Phase 3 gilt ein **data-first Hybridmodell** (siehe ADR-0015):

- **Strukturierte YAML-Daten unter `data/`** sind die fachliche Quelle der Wahrheit fuer: stabile Objektidentitaeten,
  kanonische Namen, Synonyme, Objekttypen, Studien, Quellen, wissenschaftliche Claims, Beziehungen,
  Evidenzkategorien, Evidenzqualitaet, Reviewstatus, regulatorische Metadaten und maschinenlesbare
  Klassifikationen.
- **Markdown unter `docs/`** bleibt die verstaendliche redaktionelle Darstellung: Erklaerungen, Einordnungen,
  didaktische Uebergaenge, Zusammenfassungen, Kontext, Diskussion von Unsicherheiten und offenen
  Forschungsfragen. Markdown verweist auf strukturierte Objekte und Claims (`entity_id`, `claim_ids` im
  Frontmatter), kopiert deren Fakten aber nicht.
- **Kein vollstaendiger automatischer Textgenerator.** Phase 3 generiert keine vollstaendigen Artikel aus Daten.
  Sie schafft aber die Grundlage, damit spaeter Metadatenboxen, Quellenlisten, Evidenzuebersichten,
  Studienlisten, Vergleichstabellen, Knowledge-Graph-Verbindungen, API-Ausgaben und PDFs automatisiert erzeugt
  werden koennen.
- **Keine doppelte Faktenpflege.** Ein wissenschaftlicher Claim existiert genau einmal als kanonischer Datensatz.
  Artikel verweisen darauf, duplizieren ihn aber nicht.

Dies ist eine praezisierende Fortschreibung von ADR-0007 (Markdown+Frontmatter als Source of Truth), nicht deren
Aufhebung: Redaktionelle Prosa bleibt in Markdown, maschinenlesbare Fakten wandern in die neue Datenebene.

## Entitaet, Studie, Quelle und Claim

| Objektart | Ordner | Beispiel-ID | Was es ist |
|---|---|---|---|
| **Entitaet** | `data/entities/<typ>/` | `substance-placeholder` | Ein stabiles Objekt: Substanz, Rezeptor, Signalweg, Erkrankung, Nebenwirkung, Organisation oder Studie. Traegt keine eigene Evidenzstufe. |
| **Studie** | `data/entities/studies/` | `study-placeholder` | Eine eigenstaendige Studie (Design, Registrierung). Kein Synonym fuer Publikation: eine Studie kann mehrere Publikationen, vorlaeufige und aktualisierte Ergebnisse oder auch keine Publikation besitzen. |
| **Quelle** | `data/sources/` | `source-placeholder` | Eine deduplizierte Quelle (Publikation, Registrierungseintrag, Behoerdendokument, Haendlerseite ...). Wird von Studien und Claims referenziert. |
| **Claim** | `data/claims/` | `claim-<uuid4>` | Eine einzeln pruefbare wissenschaftliche Aussage mit genau einer primaeren Evidenzkategorie und einer separat bewerteten Sicherheit. Das zentrale Objekt dieser Architektur. |

Ein Objekt wie eine Substanz hat **keine** einzelne Evidenzstufe (ADR-0008 bleibt gueltig) — jede Aussage
*ueber* die Substanz ist ein eigener Claim mit eigener Evidenz. Ein Artikel kann gleichzeitig gut gesicherte
molekulare Eigenschaften, hochwertige Humanstudien, fruehe klinische Ergebnisse, Tierstudien und theoretische
Hypothesen enthalten — deshalb darf ein vollstaendiger Artikel nicht pauschal nur eine Evidenzstufe erhalten
(siehe Abschnitt „Neues Evidenzmodell").

### Substanz statt getrennter Peptide-/Drug-Objekte

Das Phase-2-Datenmodell (siehe [Data Model](Data_Model.md)) unterschied `Peptide` und `Drug` als getrennte
Objekttypen. Das kann dazu fuehren, dass dasselbe Molekuel doppelt angelegt wird (`peptide-example` und
`drug-example` fuer dieselbe Substanz). Phase 3 fuehrt stattdessen ein allgemeines Objekt `substance` ein, das
ueber `substance_classes` naeher klassifiziert wird (`peptide`, `protein`, `small_molecule`, `hormone`,
`antibody`, `conjugate`, `approved_drug`, `investigational_drug`, `endogenous_substance`,
`synthetic_analogue`). Eine Substanz kann mehrere Klassen gleichzeitig tragen. Ein konkretes Markenprodukt oder
zugelassenes Fertigarzneimittel wird **spaeter** als eigenes Objekt `medicinal_product` modelliert (in Phase 3
noch nicht implementiert) — die molekulare Substanz und das vermarktete Produkt werden nicht vermischt. Siehe
ADR-0015.

### Erkrankung (`condition`) statt Indikationsobjekt

Eine Erkrankung oder ein biologischer Zustand ist ein Objekt (`condition`). Eine Indikation — „Substanz X ist
fuer Erkrankung Y zugelassen" oder „wird fuer Erkrankung Y untersucht" — ist dagegen eine kontextabhaengige
Aussage und wird als **Claim** (`claim_type: regulatory` bzw. `association`, Praedikate `approved_for` /
`not_approved_for` / `studied_for`) modelliert, nicht als eigenes Indikationsobjekt pro Substanz-Erkrankung-Paar.
Das vermeidet ein redundantes Indikationsobjekt fuer jede Kombination und haelt die Aussage an der Stelle, an
der ihre Evidenz und Sicherheit ohnehin bewertet werden. Siehe ADR-0022.

### Reduzierter Objekttyp-Katalog gegenueber Phase 2

[Data Model](Data_Model.md) skizzierte deutlich mehr Objekttypen (`Protein`, `Gene`, `Publication`, `Author`,
`Institution`, `Journal`, `Country`, `Company`, `Target`, `Mechanism`, `Side Effect`, `Indication`, `Organ`,
`Tissue`, `Biomarker` ...) als Leitplanke fuer einen 5-Jahres-Horizont. Phase 3 implementiert bewusst nur sieben
Entitaetstypen (`substance`, `receptor`, `pathway`, `condition`, `adverse_event`, `organization`, `study`) plus
`source` und `claim` — die einfachste belastbare Loesung fuer den aktuellen Bedarf (siehe Abschnitt
„Arbeitsweise": konservative, wartbare Entscheidungen statt Overengineering). Konsolidierung im Detail:

- `Institution`, `Company`, `Regulatory Agency`, `Sponsor` → vereinheitlicht in `organization` mit
  `organization_type`.
- `Publication`, `Journal`, `Author` → als einfache Felder (`journal`, `authors[]`) auf `source` statt eigener
  Entitaeten, da fuer den aktuellen Anwendungsfall (Quelle referenzieren, nicht Autoren-Netzwerke analysieren)
  ausreichend.
- `Target`, `Mechanism` → Praedikate am Claim (`binds_to`, `agonist_of`, `inhibits`, ...) statt eigener
  Entitaeten, konsistent mit Data Models eigener Beobachtung, dass ein Wirktyp Eigenschaft einer Relation ist.
- `Gene` → optionales Feld `gene_symbol` auf `receptor`, kein eigenes Objekt, solange keine genzentrierten
  Inhalte geplant sind.
- `Side Effect` → `adverse_event` (Begriff an das international gebraeuchlichere Vokabular angeglichen).
- `Indication` → Claim statt Objekt (siehe oben).
- `Protein`, `Hormone` → als `substance_classes`-Wert auf `substance` abgebildet statt eigener Entitaetstypen.
- `Organ`, `Tissue`, `Biomarker`, `Country`, `Author` als eigenstaendige IDs → bewusst zurueckgestellt (YAGNI),
  bis ein konkreter redaktioneller Bedarf entsteht. Siehe [Future Roadmap](Future_Roadmap.md).

Neue Entitaetstypen koennen spaeter ergaenzt werden, ohne bestehende Schemas inkompatibel zu aendern (neuer
Ordner unter `data/entities/`, neuer Wert in `entity_types.yaml`, neues `<typ>.schema.json`).

## Neues Evidenzmodell

Das bisherige A–E-Modell (siehe [Evidenzsystem](../00_grundlagen/evidenzsystem.md)) vermischte Art der Evidenz,
Studiendesign, Qualitaet, Sicherheit der Aussage sowie Marketing-/Erfahrungsangaben in einer einzigen Skala.
Phase 3 trennt diese Dimensionen:

1. **Evidenzkategorie** (`evidence_category`, genau eine primaere Kategorie pro Claim): `established_knowledge`,
   `clinical_evidence`, `limited_evidence`, `preclinical_evidence`, `theoretical_hypothesis`, `merchant_claim`,
   `personal_experience`. Vollstaendige Definitionen: [Evidenzsystem](../00_grundlagen/evidenzsystem.md) und
   `data/vocabularies/evidence_categories.yaml`.
2. **Sicherheit/Vertrauenswuerdigkeit** (`certainty`, redaktionell vergeben, nie automatisch aus dem
   Studiendesign errechnet): `high`, `moderate`, `low`, `very_low`, `not_assessed`, mit Pflichtfeld
   `certainty_rationale` ausser bei `not_assessed`.
3. **Studiendesign** (`study_design`, kontrolliertes Vokabular): `randomized_controlled_trial` bis `other`, siehe
   `data/vocabularies/study_designs.yaml`.
4. **Unterstuetzende/widersprechende Evidenz** (`evidence[]` je Claim): jede Verknuepfung traegt `source_id`,
   optional `study_id` und `locator` (Seite/Tabelle/Abbildung/Abschnitt), sowie eine `direction` (`supports`,
   `contradicts`, `mixed`, `context_only`).

Wichtige Leitplanken, vom Validator durchgesetzt (siehe unten): `merchant_claim` und `personal_experience` duerfen
niemals alleiniger aktiver Wirksamkeitsnachweis sein; `certainty: high` ist ausgeschlossen, wenn die einzige
Evidenz eine Haendlerseite oder ein persoenlicher Bericht ist; eine praeklinische Studie bleibt praeklinische
Evidenz, auch wenn sie methodisch gut ist — sie wird nicht zu klinischer Wirksamkeit umformuliert.

### `evidenzstufe` ist Legacy

Das Frontmatter-Feld `evidenzstufe` (A–E) wird als **veraltet** gekennzeichnet (siehe ADR-0018). Es wird fuer
bestehende Legacy-Artikel vorruebergehend toleriert; der Validator gibt dafuer eine klare
Deprecation-**Warnung** aus, keinen Build-Abbruch. Neue wissenschaftliche Objektseiten sollen es nicht als
alleinige Evidenzbewertung verwenden, sondern per `entity_id`/`claim_ids` auf claim-basierte Evidenz verweisen.
Eine vollstaendige Entfernung ist fruehestens fuer Phase 4 vorgesehen.

## Dateistruktur

```
schemas/            JSON Schema (Draft 2020-12) je Objektart, common.schema.json fuer gemeinsame Definitionen
data/
├── entities/        substances/ receptors/ pathways/ conditions/ adverse_events/ organizations/ studies/
├── sources/         eine YAML-Datei je Quelle
├── claims/          eine YAML-Datei je Claim (Dateiname == UUID-basierte id)
├── vocabularies/     kontrollierte Vokabulare (predicates, evidence_categories, certainty_levels, ...)
└── examples/         offensichtlich fiktive Platzhalterdaten, eigener Namensraum, nicht im Katalog enthalten
tools/               new_id.py, validate_data.py, build_catalog.py, export_graph.py
tests/               fixtures/{valid,invalid} + pytest-Tests
build/               generiert, nicht committed (siehe .gitignore)
```

## Validierung

`python tools/validate_data.py [--verbose]` prueft (Exitcode 0 bei Erfolg, 1 bei mindestens einem Fehler,
Warnungen blockieren den Build nicht):

- **Schemaebene**: gueltiges YAML (ausschliesslich `yaml.safe_load`), JSON-Schema-Konformitaet, Pflichtfelder,
  Enums, Datumsformate, `oneOf` fuer Claim-Objektvarianten, `schema_version`.
- **Dateiebene**: Dateiname == `id`, globale ID-Eindeutigkeit ueber alle Objektarten hinweg, keine leeren
  Platzhalterdateien ausserhalb `data/examples/`, keine unerwuenschten Binaerdateien unter `data/`.
- **Referenzebene**: `subject_id`, `object.entity_id`, `evidence[].source_id`, `evidence[].study_id`,
  `study.source_ids`, `study.sponsor_ids` muessen auf existierende Objekte zeigen; `predicate` muss in
  `data/vocabularies/predicates.yaml` stehen.
- **Evidenzebene**: aktive medizinisch relevante Claims (Mechanismus, Wirksamkeit, Sicherheit, Nebenwirkung,
  Pharmakokinetik, Rezeptor-/Signalwegaktivitaet, regulatorischer Status, Studienergebnis, krankheitsbezogene
  Assoziation) benoetigen mindestens eine Quelle, ausser bei explizitem `source_requirement: exempt` mit
  Begruendung; `merchant_claim`/`personal_experience` nicht als alleinige aktive Evidenzkategorie;
  zurueckgezogene Quellen als alleinige aktive Evidenz sind ein Fehler, `expression_of_concern`/`corrected` eine
  Warnung; `certainty: high` ist mit ausschliesslich Haendler-/Erfahrungsevidenz unzulaessig.
- **Reviewebene**: `status: active` erfordert `review.last_reviewed_at` und mindestens einen Reviewer (fuer
  Entitaeten und Claims). Eine einfache Datums-Heuristik warnt, wenn `updated_at` nach `review.last_reviewed_at`
  liegt (siehe „Grenzen der Phase").
- **Artikelintegration**: Frontmatter unter `docs/**` (ausser `docs/project/**` sowie der Startseite und der
  automatischen Tag-Uebersicht) wird gegen `article_frontmatter.schema.json` geprueft; referenzierte
  `entity_id`/`claim_ids` muessen existieren; `evidenzstufe` erzeugt die oben beschriebene Warnung.

Fehler werden dateibezogen und lesbar ausgegeben (`ERROR <Datei>` / `<Pfad>: <Meldung>`), nicht als roher
Python-Traceback.

## Katalog- und Graphexport

`python tools/build_catalog.py` erzeugt `build/catalog.json`: alle Entitaeten, Studien, Quellen und Claims nach
`id` sortiert, mit Objektzaehlung je Typ, `schema_version` und `generated_at`. `python tools/export_graph.py`
erzeugt `build/graph.json`: Nodes aus Entitaeten, Edges ausschliesslich aus Claims mit `object.entity_id`
abgeleitet (siehe `schemas/relationship.schema.json`). Beide Exporte sind deterministisch (gleiche Eingabedaten
→ gleiche Struktur und Reihenfolge, abgesehen vom Zeitstempel) und enthalten keine zirkulaeren Einbettungen —
referenziert wird ausschliesslich per ID. Beide Artefakte liegen unter `build/` und werden nicht committed;
sie sind die Grundlage fuer eine kuenftige read-only API (siehe [Architecture](Architecture.md)).

## Artikelintegration

Wissenschaftliche Markdown-Artikel koennen im Frontmatter `entity_id` (das behandelte kanonische Objekt) und
`claim_ids` (die Claims, auf die sich der Artikel stuetzt) angeben. Architekturdokumente unter `docs/project/**`
sowie rein navigatorische Seiten (Startseite, automatische Tag-Uebersicht) benoetigen kein `entity_id`.
Allgemeine Grundlagenartikel, die mehrere Entitaeten behandeln, koennen ohne einzelnes `entity_id` bleiben.
Phase 3 implementiert bewusst **keine** Markdown-AST-Analyse — Referenzpruefungen beschraenken sich auf das
Frontmatter.

## Grenzen der Phase

- Keine echten medizinischen Inhalte, kein Retatrutid-Datensatz, keine automatisierte Literaturrecherche
  (PubMed/ClinicalTrials.gov/FDA/EMA), keine automatische Evidenzbewertung durch KI, keine vollstaendige
  Artikelerzeugung, keine PDF-Generierung, kein dynamisches Backend, keine Graphdatenbank, kein Suchserver.
- Die Pruefung „ein substantiell geaenderter Claim sollte nicht unbemerkt mit altem Reviewstatus weiterlaufen"
  ist **nicht** als vollstaendige Git-Diff-Analyse implementiert. Stattdessen vergleicht der Validator
  `updated_at` mit `review.last_reviewed_at` und gibt eine Warnung aus, wenn Ersteres neuer ist. Das erkennt
  nicht jede inhaltliche Aenderung (z. B. eine Korrektur an `evidence[]` ohne Aktualisierung von `updated_at`
  wuerde nicht erkannt) — eine zuverlaessigere Loesung (z. B. inhaltsbasierter Hash statt Datum) ist fuer eine
  spaetere Phase vorgemerkt, siehe [Future Roadmap](Future_Roadmap.md).
- „Thematisch verbunden" zwischen Artikel und referenziertem Claim wird nur naeherungsweise geprueft
  (`subject_id` oder `object.entity_id` muss `entity_id` entsprechen); eine abweichende, aber warnungsfrei
  bleibende Verbindung ist moeglich und erfordert redaktionelle Aufmerksamkeit.
- `medicinal_product` (konkretes Markenprodukt/Fertigarzneimittel) ist beschrieben, aber nicht implementiert.

## Migrationshinweise

- Bestehende Artikel mit `evidenzstufe` bleiben gueltig und funktionsfaehig; der Validator warnt, bricht aber
  nicht ab. Eine kontrollierte Migration auf claim-basierte Evidenz erfolgt schrittweise, sobald reale
  Wirkstoffartikel entstehen (Phase 4+).
  Es wird empfohlen, migrationswillige Artikel zunaechst mit `entity_id` zu versehen, dann Claims fuer die
  einzelnen Aussagen anzulegen und erst danach `evidenzstufe` zu entfernen.
- Der Artikelstatus in Markdown-Frontmatter (`Entwurf`/`In Pruefung`/`Aktiv`/`Zurueckgezogen`) bleibt bewusst
  deutschsprachig (siehe ADR-0019) und wird **nicht** auf die englischen Werte der Datenebene umgestellt.
- `data/catalog.json` (leeres Phase-1-Geruest) wurde entfernt; der neue, generierte Katalog liegt unter
  `build/catalog.json` (siehe ADR-0020, setzt ADR-0011 um).

## Naechste Schritte fuer Phase 4

Phase 4 ist **nicht** Teil dieser Implementierung. Vorbereitet ist:

- Ein vollstaendiges Schema- und Validierungsgeruest, das das erste reale Pilotobjekt (voraussichtlich
  Retatrutid, siehe [Roadmap](../roadmap.md)) direkt aufnehmen kann: eine `substance`-Datei, zugehoerige
  `source`- und `claim`-Dateien, ein oder mehrere `study`-Eintraege. Das Geruest ist dann vollstaendig nutzbar,
  sobald die wissenschaftliche Redaktion reale Inhalte liefert, die den Qualitaets- und Evidenzregeln aus dieser
  Phase genuegen. Bei Bedarf koennen weitere Entitaetstypen (`medicinal_product`, `gene`, `biomarker`, ...) nach
  demselben Muster ergaenzt werden.
- Ein Reviewprozess-Fahrplan: `status: active` erfordert bereits jetzt Reviewdatum und Reviewer, konsistent mit
  [Editorial Policy](Editorial_Policy.md).

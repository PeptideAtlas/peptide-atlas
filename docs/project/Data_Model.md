---
title: Data Model
description: Universelles Objekt- und Beziehungsmodell für Peptide Atlas.
tags:
  - Architektur
  - Projekt
  - Datenmodell
---

# Data Model

Dieses Dokument entwirft ein **universelles, technologieunabhängiges Datenmodell** für Peptide Atlas. Es ist bewusst **keine** konkrete Datenbankspezifikation (kein SQL-Schema, keine Neo4j-Cypher-Definition) — es beschreibt Objekttypen, Pflichtfelder und Beziehungen so, dass sie später gleichermaßen als YAML-Frontmatter, als JSON-Dateien in `data/`, in einer relationalen Datenbank oder in einem Graphsystem umgesetzt werden können.

**Wichtig:** Dieses Dokument definiert nur die **Struktur**. Es enthält keine echten Wirkstoff-, Studien- oder Krankheitsdaten. Alle Beispiele sind rein illustrativ und mit Platzhaltern gekennzeichnet.

!!! info "Konkrete Umsetzung seit Phase 3"
    Dieses Dokument bleibt die konzeptionelle Leitplanke. Die konkrete, implementierte und getestete Umsetzung
    (JSON Schemas, YAML-Dateien, Validator) steht in [Phase 3 Dokumentation](Phase_3_Scientific_Data_Architecture.md).
    Zwei Konkretisierungen weichen bewusst von der ursprünglichen Tabelle unten ab (siehe ADR-0015, ADR-0022,
    ADR-0023 im [Decision Log](Decision_Log.md)): `Peptide`/`Drug` wurden zu einem einzigen Objekt `substance`
    vereinheitlicht, und `Indication` wird als Claim statt als eigenes Objekt modelliert. Der Objekttyp-Katalog
    wurde für Phase 3 auf sieben Entitätstypen reduziert (siehe Phase 3 Dokumentation für die vollständige
    Begründung je Typ).

!!! info "Provenienzebene seit Phase 4A"
    Seit Phase 4A gibt es zusätzlich `research/**` — eine separate Recherche- und Provenienzebene (siehe
    ADR-0033 im [Decision Log](Decision_Log.md)), die Rechercheverlauf, Kandidaten, Screening- und
    Extraktionsdaten hält. `research/**` ist **kein** kanonisches Wissen und fließt nicht in dieses Datenmodell
    ein — erst nach manueller Prüfung wird eine Information als Entität, Quelle, Studie oder Claim unter
    `data/**` angelegt. Seit Phase 4B-1B-0 gehört dazu zusätzlich `research_candidate_manifest`
    (`research/candidates/**`) — eine protokoll-/datenbankgebundene, rein technisch-bibliographische
    Normalisierung der Discovery-Grundmenge zwischen Search Result Manifest und Screening Record (siehe
    ADR-0056). Seit Phase 4B-1B-1 erzeugt `tools/initialize_screening_records.py` daraus automatisch je
    Kandidat genau einen `research_screening_record` im rein administrativen Initialzustand
    (`decision: pending`, `screened_by: system-screening-initializer`) — weiterhin keine wissenschaftliche
    Bewertung, nur die technische Bereitstellung des Datensatzes (siehe ADR-0057). Ein begleitendes, rein
    technisches Kontrollartefakt `research/screening_status/initialization_manifest.yaml` ist **kein**
    eigener Objekttyp dieses Datenmodells — es dokumentiert nur den Initialisierungsfortschritt je
    Protokoll. Seit Phase 4B-1B-3 gehört zusätzlich die optionale Objektart `research_reviewer`
    (`research/reviewers/**`, ADR-0059) dazu — versieht ein bereits verwendetes `research_actor_id`-Kürzel
    nachträglich mit einem strukturellen Akteurstyp (`human`/`ai_assistant`/`automation`/`service`); ebenso
    **kein** kanonisches Wissensobjekt, sondern Teil derselben Provenienzebene wie die übrigen
    `research/**`-Objektarten. Details: [Scientific Research Protocol](Scientific_Research_Protocol.md),
    [Evidence Curation Workflow](Evidence_Curation_Workflow.md).

## Leitprinzipien

1. **Ein Objekt, eine ID, eine Quelle der Wahrheit.** Jedes Objekt existiert genau einmal und wird von überall darauf verlinkt, nie dupliziert.
2. **Aussagen leben in Beziehungen, nicht nur in Objekten.** Ob eine Aussage stimmt „Substanz X wirkt auf Rezeptor Y", ist eine **Relation** mit eigener Quelle und Evidenzstufe — nicht nur ein Freitextsatz im Objekt.
3. **Evidenz ist eine Eigenschaft der Aussage, nicht (nur) des Objekts.** Ein Wirkstoff-Objekt selbst hat keine einzelne Evidenzstufe; jede einzelne Beziehung/Aussage über ihn hat ihre eigene (siehe [Evidenzsystem](../00_grundlagen/evidenzsystem.md)).
4. **Alles ist optional erweiterbar, nichts wird rückwirkend inkompatibel.** Neue Felder werden ergänzt, bestehende nicht ohne Migrationspfad umbenannt (siehe [Versioning](Versioning.md)).

## Basis-Schema (gilt für jeden Objekttyp)

Jedes Objekt — unabhängig vom Typ — besitzt mindestens folgende Felder:

| Feld | Typ | Pflicht | Beschreibung |
|---|---|---|---|
| `id` | string | ja | Stabiler, eindeutiger Bezeichner. Format: `<typ>-<kebab-case-slug>` (siehe [Naming Conventions](Naming_Conventions.md)). Wird nie wiederverwendet, auch nicht nach Löschung. |
| `type` | enum | ja | Einer der in diesem Dokument definierten Objekttypen. |
| `title` | string | ja | Kanonischer Name/Titel des Objekts. |
| `synonyms` | string[] | nein | Alternative Namen, Abkürzungen, frühere Bezeichnungen. |
| `description` | string | ja | Kurze, neutrale Beschreibung (wird von der wissenschaftlichen Redaktion geliefert). |
| `status` | enum | ja | `Entwurf` \| `In Prüfung` \| `Aktiv` \| `Zurückgezogen` (siehe [Quality Standards](Quality_Standards.md)). |
| `sources` | Source[] | ja, sobald Aussagen enthalten sind | Siehe Abschnitt „Quellenmodell". |
| `relations` | Relation[] | nein | Siehe [Knowledge Graph](Knowledge_Graph.md). |
| `last_reviewed` | date | nein (empfohlen) | Datum der letzten redaktionellen Prüfung. |
| `reviewed_by` | string | nein (empfohlen) | Kürzel/Rolle der prüfenden Person (kein Klarname, siehe Datenschutz-Erwägungen in [Editorial Policy](Editorial_Policy.md)). |
| `language` | string | nein | ISO-639-1-Code, Vorbereitung für Mehrsprachigkeit. Default: `de`. |

## Quellenmodell (`Source`)

| Feld | Typ | Beschreibung |
|---|---|---|
| `id` | string | Eindeutige Quellen-ID. |
| `citation` | string | Vollständige Zitation. |
| `url_or_doi` | string | Link oder DOI, falls vorhanden. |
| `source_type` | enum | `Zulassung` \| `Klinische Forschung` \| `Präklinische Forschung` \| `Händlerangabe` \| `Leitlinie` \| `Sonstige` (Trennung gemäß [Redaktionsstandard](../00_grundlagen/redaktionsstandard.md)). |
| `evidenzstufe` | enum | `A`–`E` (siehe [Evidenzsystem](../00_grundlagen/evidenzsystem.md)), falls auf eine konkrete Aussage anwendbar. |

## Objekttypen

Für jeden Typ werden hier nur **strukturelle**, typ-spezifische Zusatzfelder zum Basis-Schema aufgeführt — keine Inhalte.

| Typ | ID-Präfix | Typ-spezifische Zusatzfelder (Beispiele) | Entspricht Content-Bereich |
|---|---|---|---|
| **Peptide** | `peptide-` | Sequenzlänge, Strukturtyp (linear/zyklisch), Ursprungsorganismus | [Wirkstoffe](../01_wirkstoffe/index.md) |
| **Drug** (Arzneimittel) | `drug-` | INN-Name, ATC-Code, Zulassungsstatus je Land/Agentur | [Wirkstoffe](../01_wirkstoffe/index.md) |
| **Protein** | `protein-` | UniProt-ID (falls verfügbar), Funktion (strukturell, katalytisch, Signal) | [Biologie](../02_biologie/index.md) |
| **Hormone** | `hormone-` | Ursprungsdrüse, Zielorgane | [Biologie](../02_biologie/index.md) |
| **Receptor** | `receptor-` | Rezeptorfamilie (GPCR, RTK, Zytokinrezeptor, nukleär …), kodierendes Gen | [Rezeptoren](../02_biologie/rezeptoren.md) |
| **Gene** | `gene-` | Gensymbol, Genlocus | [Biologie](../02_biologie/index.md) |
| **Disease** (Erkrankung) | `disease-` | ICD-10/11-Code, Kategorie | [Indikationen](../03_indikationen/index.md) |
| **Study** (Studie) | `study-` | Studientyp (RCT, Kohorte, Fallserie, tierexperimentell, in vitro), Phase, Registrierungs-ID (z. B. NCT-Nummer), Stichprobengröße | [Studien](../04_studien/index.md) |
| **Publication** | `publication-` | DOI, Publikationstyp (Peer-Review, Preprint, Konferenzabstract), Jahr | [Studien](../04_studien/index.md) |
| **Author** | `author-` | ORCID (falls vorhanden) | Metadaten zu Publikationen |
| **Institution** | `institution-` | Institutionstyp (Universität, Klinik, Unternehmen) | Metadaten |
| **Journal** | `journal-` | ISSN | Metadaten zu Publikationen |
| **Country** | `country-` | ISO-3166-Code | Regulatorischer Kontext |
| **Company** | `company-` | Rolle (Hersteller, Sponsor, Vertrieb) — Kennzeichnungspflicht als Händlerangabe bleibt bestehen | [Wirkstoffe](../01_wirkstoffe/index.md) |
| **Guideline** (Leitlinie) | `guideline-` | Herausgebende Institution, Jahr, Geltungsbereich | [Studien](../04_studien/index.md) |
| **Regulatory Agency** | `agency-` | Land/Region, Zuständigkeitsbereich | [Wirkstoffe](../01_wirkstoffe/index.md) |
| **Target** | `target-` | Zielklasse (Rezeptor, Enzym, Ionenkanal) — Abgrenzung zu `Receptor`: `Target` ist die allgemeinere Kategorie, `Receptor` ein spezifischer Fall | [Biologie](../02_biologie/index.md) |
| **Mechanism** | `mechanism-` | Wirktyp (Agonist, Antagonist, Inhibitor, Modulator …) | [Biologie](../02_biologie/index.md) |
| **Side Effect** (Nebenwirkung) | `side-effect-` | Schweregradklasse, Häufigkeitskategorie (falls aus Quelle ableitbar) | [Wirkstoffe](../01_wirkstoffe/index.md) |
| **Indication** (Indikation) | `indication-` | Zulassungsumfang je Agentur/Land | [Indikationen](../03_indikationen/index.md) |
| **Biological Pathway** (Signalweg) | `pathway-` | Kategorie (Signalweg, Stoffwechselweg) | [Biologie](../02_biologie/index.md) |
| **Organ** | `organ-` | Organsystem | [Biologie](../02_biologie/index.md) |
| **Tissue** (Gewebe) | `tissue-` | Übergeordnetes Organ | [Biologie](../02_biologie/index.md) |
| **Biomarker** | `biomarker-` | Messmatrix (Blut, Gewebe …), assoziierte Erkrankung/Signalweg | [Studien](../04_studien/index.md) |

Alle Objekttypen teilen sich das Basis-Schema; die Tabelle listet nur **zusätzliche**, typ-spezifische Felder als Designvorschlag. Konkrete Pflicht-/Optional-Kennzeichnung je Feld erfolgt beim Schema-Rollout (siehe [Release Strategy](Release_Strategy.md), v0.3).

## Beziehungstypen (Auszug)

Beziehungstypen werden ausführlich in [Knowledge Graph](Knowledge_Graph.md) behandelt. Zur Einordnung hier die wichtigsten, mit Bezug zu den Objekttypen:

| Relation | Von → Nach | Entspricht Content-Bereich |
|---|---|---|
| `BINDS_TO` | Peptide/Drug → Receptor/Target | Rezeptoren |
| `ENCODED_BY` | Protein/Receptor → Gene | Biologie |
| `TREATS` | Drug → Indication/Disease | Indikationen |
| `STUDIED_IN` | Drug/Peptide → Study | Studien |
| `PUBLISHED_IN` | Study → Publication → Journal | Studien |
| `MANUFACTURED_BY` | Drug → Company | Wirkstoffe (mit Kennzeichnungspflicht) |
| `APPROVED_BY` | Drug/Indication → Regulatory Agency | Wirkstoffe/Indikationen |
| `PART_OF_PATHWAY` | Receptor/Protein → Biological Pathway | Biologie |
| `CAUSES_SIDE_EFFECT` | Drug → Side Effect | Wirkstoffe |
| `HAS_BIOMARKER` | Disease/Pathway → Biomarker | Studien |
| `COMPARED_TO` | Drug ↔ Drug, Peptide ↔ Peptide | Vergleiche |
| `SIMILAR_TO` | Peptide ↔ Peptide (struktureller Analog) | Vergleiche |

## Verhältnis zum generierten `build/catalog.json`

Das ursprüngliche, leere `data/catalog.json` (Phase 1) wurde entfernt (siehe ADR-0020 im [Decision Log](Decision_Log.md)).
An seine Stelle tritt ein generiertes `build/catalog.json`: typ-spezifische YAML-Dateien unter `data/entities/<typ>/`
sind die redaktionelle Source of Truth, der Katalog wird daraus bei jedem Build deterministisch erzeugt und
nicht committed. Details: [Phase 3 Dokumentation](Phase_3_Scientific_Data_Architecture.md).

## Nicht Teil dieses Dokuments

- Konkrete Datenbankwahl (SQL vs. Graphdatenbank) — bewusst offen gelassen, siehe [Architecture](Architecture.md).
- Reale Objektinstanzen oder medizinische Inhalte — werden ausschließlich von der wissenschaftlichen Redaktion geliefert.
- Validierungsregeln/JSON-Schema-Implementierung — siehe [Quality Standards](Quality_Standards.md) für die fachliche Anforderung, Umsetzung folgt in einer späteren Phase.

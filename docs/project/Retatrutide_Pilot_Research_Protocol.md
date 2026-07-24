---
title: Retatrutide Pilot Research Protocol
description: Menschenlesbare Begleitung zum maschinenlesbaren Rechercheprotokoll für das Retatrutid-Pilotvorhaben.
tags:
  - Architektur
  - Projekt
  - Redaktion
---

# Retatrutide Pilot Research Protocol

Dieses Dokument begleitet die maschinenlesbare Datei
[`research/protocols/research-protocol-retatrutide-v1.yaml`](https://github.com/PeptideAtlas/peptide-atlas/blob/main/research/protocols/research-protocol-retatrutide-v1.yaml)
(Schema: `schemas/research_protocol.schema.json`) und erklärt sie in Fließtext. Es ist das erste konkrete
Anwendungsbeispiel des [Scientific Research Protocol](Scientific_Research_Protocol.md) und bereitet Retatrutid
als erstes vollständiges Pilotobjekt für Peptide Atlas vor.

!!! danger "Ausdrücklich KEINE realen Inhalte in diesem Auftrag"
    Dieses Protokoll plant **wie** recherchiert werden soll. Es enthält **keine** realen Studienergebnisse,
    Wirksamkeitszahlen, Nebenwirkungsraten, Halbwertszeiten, Rezeptorpotenzen oder Zulassungsbehauptungen, und
    es verweist auf keine realen PMID-, DOI- oder NCT-Datensätze. Es existieren dazu (noch) keine
    `data/entities/substances/**`-, `data/sources/**`-, `data/entities/studies/**`- oder `data/claims/**`-Dateien
    und kein Retatrutid-Artikel. Diese entstehen frühestens in Phase 4B, nach wissenschaftlichem Review dieses
    Protokolls (siehe [Roadmap](../roadmap.md)).

## Warum Retatrutid als Pilot?

Retatrutid dient als erstes vollständiges Pilotobjekt, weil es alle acht in
[Data Model](Data_Model.md)/[Phase 3 Dokumentation](Phase_3_Scientific_Data_Architecture.md) vorgesehenen
Forschungsbereiche berührt — Identität, Geschichte, Mechanismus, Pharmakokinetik, klinische Forschung,
Sicherheit, präklinische Forschung und regulatorischer Status — und damit ein realistischer, vollständiger Test
für das gesamte Recherche- und Kuratierungsprotokoll ist.

## Untersuchungsgegenstand

Der Arbeitsname ist **Retatrutid** (`subject.working_name`). Der kanonische Name, dokumentierte
Entwicklungsbezeichnungen (z. B. Codebezeichnungen der Entwicklungsphase) und Schreibvarianten gelten
ausdrücklich als **noch zu verifizieren** — sie werden erst nach Bestätigung durch eine belastbare Quelle in
einen kanonischen `identity`-Claim überführt (siehe [Scientific Research Protocol](Scientific_Research_Protocol.md#4-definition-des-untersuchungsgegenstands)).

## Acht getrennte Forschungsbereiche

Das Protokoll definiert für jeden Bereich mindestens eine explizite Forschungsfrage
(`research_questions[].topic`):

| Bereich | Forschungsfrage (verkürzt) |
|---|---|
| Identität und Nomenklatur | Kanonischer Name, Entwicklungsbezeichnungen, Schreibvarianten; chemische/biologische Klassifikation. |
| Geschichte und Entwicklung | Sponsor/Entwickler, zeitliche Abfolge der Forschungsphasen. |
| Wirkmechanismus | Beteiligte Rezeptoren (GIP, GLP-1, Glucagon), Aktivitätsform, nachgelagerte Signalwege; Abgrenzung gesicherte Erkenntnis vs. theoretische Interpretation. |
| Pharmakokinetik | Absorption, Tmax, Verteilung, Metabolismus, Eliminationshalbwertszeit, Dosisproportionalität, populationsbezogene Unterschiede — nur mit Primärquelle. |
| Klinische Forschung | Getrennt nach Phase, Population, Design, Intervention, Vergleichsgruppe, Dauer, Endpunkten, Analysepopulation, Ergebnis, Registerstatus. |
| Sicherheit | Unerwünschte Ereignisse, schwerwiegende Ereignisse, Therapieabbrüche, dosisbezogene Verträglichkeit, Sicherheitssignale, fehlende Langzeitdaten; Unterschied Beobachtung vs. nachgewiesene Kausalität. |
| Präklinische Forschung | In-vitro-/Tiermodell, Spezies, Dosis, Endpunkt, Übertragbarkeit, methodische Grenzen. |
| Regulatorischer Status | Ausschließlich FDA/EMA/andere zuständige Behörden als maßgebliche Grundlage; ClinicalTrials.gov/Herstellerangaben werden nicht mit einer Zulassung verwechselt. |

Für unbekannte oder unzureichend untersuchte Aspekte gilt verbindlich die Formulierung: *„Derzeit gibt es keine
ausreichenden wissenschaftlichen Daten."* — statt eine Lücke stillschweigend zu übergehen oder mit einer
schwächeren Quelle zu füllen.

## Geplante Suchstrategie (noch nicht ausgeführt)

Die folgenden Suchkonzepte sind im Protokoll (`planned_search_concepts[]`) hinterlegt — sie beschreiben, **was**
gesucht werden soll, nicht die exakte, datenbankspezifische Syntax (diese entsteht erst in einem konkreten
`search_run`-Datensatz, siehe [Scientific Research Protocol](Scientific_Research_Protocol.md#7-suchprotokollierung)):

```text
retatrutide
Entwicklungsbezeichnungen/Aliasnamen (zunächst als zu verifizieren markiert)
triple agonist
GIP receptor
GLP-1 receptor
glucagon receptor
obesity
overweight
type 2 diabetes
pharmacokinetics
safety
adverse events
randomized trial
phase 1 / phase 2 / phase 3
```

Geplante Quellen (`planned_information_sources[]`), mit Rolle:

| Datenbank | Rolle |
|---|---|
| PubMed/MEDLINE | primär |
| ClinicalTrials.gov | primär (Register, keine Zulassung) |
| FDA | primär (US-Zulassungsstatus) |
| EMA | primär (EU-Zulassungsstatus) |
| WHO ICTRP | primär (internationale Register) |
| Crossref | ergänzend |
| Cochrane Library | ergänzend, nur zur Orientierung/Primärquellen-Identifikation |
| Google Scholar | nur Discovery, ergänzende Zitationssuche |
| Herstellerregister | nur Discovery, ausschließlich für attribuierte Entwicklungsinformationen |

**Keine dieser Suchen wurde im Rahmen dieses Auftrags tatsächlich ausgeführt.**

## Ein- und Ausschlusskriterien (Zusammenfassung)

Grundsätzlich eingeschlossen werden Primärstudien mit direktem Bezug zu Retatrutid, offizielle
Studienregistereinträge, offizielle regulatorische Dokumente, peer-reviewte pharmakologische Untersuchungen,
relevante präklinische Primärstudien sowie Korrekturen/Errata/Retraction Notices zu bereits eingeschlossenen
Quellen. Systematische Reviews dienen nur zur Orientierung und zur Identifikation weiterer Primärquellen.

**Gesondert behandelt** (nicht automatisch wie eine peer-reviewte Primärstudie gewichtet): Hersteller-
Pressemitteilungen, Konferenzabstracts, Preprints, narrative Reviews, Sekundäranalysen, Post-hoc-Analysen,
Subgruppenanalysen sowie nicht vollständig verfügbare Quellen (siehe
[Scientific Research Protocol](Scientific_Research_Protocol.md#19-umgang-mit-preprints)).

**Nicht als Wirksamkeitsnachweis verwendet**: Händlerseiten, Social-Media- und Forenbeiträge, persönliche
Erfahrungsberichte, Werbeseiten, nicht nachvollziehbare Zusammenfassungen, KI-generierte Texte ohne
Primärquellenprüfung, Suchmaschinen-Snippets, ungeprüfte Presseartikel.

## Studien- und Publikationsmodell

Wie im [Scientific Research Protocol](Scientific_Research_Protocol.md#13-trennung-von-studie-und-publikation)
festgelegt, wird auch für Retatrutid strikt zwischen Studie und Publikation getrennt: Ein Registereintrag bei
ClinicalTrials.gov und ein späterer Fachartikel zur selben Studie werden als zwei Quellen, aber **eine** Studie
modelliert. Mehrere Publikationen (Zwischenergebnis, Endergebnis, Sicherheits-Update) derselben Studie werden
nicht als unabhängige Evidenz doppelt gezählt.

## Freigabestatus

Dieses Protokoll hat den Status `draft` (`research/protocols/research-protocol-retatrutide-v1.yaml`,
`status: draft`) — es wurde noch nicht durch einen dokumentierten Review freigegeben (`status: approved` würde
mindestens ein Reviewdatum, mindestens einen Reviewer und eine dokumentierte Freigabeentscheidung erfordern,
siehe [Scientific Research Protocol](Scientific_Research_Protocol.md)). Die eigentliche Recherche (Phase 4B)
beginnt erst nach diesem Review.

## Nächste Schritte (Phase 4B, nicht Teil dieses Auftrags)

1. Wissenschaftlicher Review und Freigabe dieses Protokolls (`status: approved`).
2. Ausführung der ersten `search_run`-Datensätze je geplanter Datenbank.
3. Screening der Treffer nach dem [Evidence Curation Workflow](Evidence_Curation_Workflow.md).
4. Extraktion, Verifikation und — nach Review — Promotion in `data/entities/substances/`,
   `data/sources/`, `data/entities/studies/` und `data/claims/`.

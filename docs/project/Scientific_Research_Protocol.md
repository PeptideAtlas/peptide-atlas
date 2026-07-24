---
title: Scientific Research Protocol
description: Verbindliches Standardverfahren für die wissenschaftliche Recherche zu jedem künftigen Wirkstoff in Peptide Atlas.
tags:
  - Architektur
  - Projekt
  - Redaktion
---

# Scientific Research Protocol

Dieses Dokument beschreibt das **verbindliche Standardverfahren**, nach dem jede künftige wissenschaftliche
Recherche in Peptide Atlas ablaufen soll — unabhängig davon, welcher Wirkstoff untersucht wird. Es ist die
menschenlesbare Ergänzung zu den maschinenlesbaren Schemas unter `schemas/research_*.schema.json` und zum
Validator `tools/validate_research.py`. Das konkrete erste Anwendungsbeispiel ist das
[Retatrutide Pilot Research Protocol](Retatrutide_Pilot_Research_Protocol.md); der Zustandsübergang vom
Suchtreffer zum aktiven Claim steht im [Evidence Curation Workflow](Evidence_Curation_Workflow.md).

!!! warning "Phase 4A: Protokoll, keine Inhalte"
    Dieses Dokument beschreibt einen **Prozess**. Es enthält selbst keine medizinischen Aussagen. Reale Quellen,
    Studien oder Claims entstehen erst, wenn dieser Prozess tatsächlich durchlaufen und die Ergebnisse
    wissenschaftlich geprüft wurden (Phase 4B, nach Review dieses Protokolls).

## 1. Zweck und Geltungsbereich

Peptide Atlas trennt seit Phase 3 strukturierte, maschinenlesbare Daten (`data/**`) von redaktioneller
Markdown-Darstellung (`docs/**`). Phase 4A ergänzt eine dritte Ebene: die **Recherche- und Provenienzebene**
(`research/**`, siehe [Data Model](Data_Model.md)). Dieses Protokoll regelt, wie Informationen von einem ersten
Suchtreffer bis zu einem geprüften, aktiven kanonischen Claim gelangen — reproduzierbar, auditierbar und ohne
dass ein automatischer Schritt jemals unbemerkt zu veröffentlichtem medizinischen Wissen wird. Es gilt für
**jeden** künftigen Wirkstoff, nicht nur für das Retatrutid-Pilotvorhaben.

## 2. Rollen und Verantwortlichkeiten

| Rolle | Verantwortung |
|---|---|
| Rechercheur:in | Führt Suchläufe aus, screent Kandidaten, extrahiert Beobachtungen. |
| Zweitprüfer:in | Bestätigt oder widerspricht Screening- und Extraktionsentscheidungen unabhängig (siehe Abschnitt 27). |
| Wissenschaftliche Redaktion | Entscheidet über die Promotion von Kandidatenclaims in die kanonische Datenebene (siehe Abschnitt 29) und über den Claim-Status. |
| Automatisierung/KI | Unterstützt bei Suche, Strukturierung und Kandidatenmarkierung — trifft **keine** endgültigen wissenschaftlichen Entscheidungen (siehe Abschnitt 13 im ursprünglichen Auftrag und [Evidence Curation Workflow](Evidence_Curation_Workflow.md)). |

Alle Rollen werden über stabile Kürzel dokumentiert (Felder wie `screened_by`, `extracted_by`, `verified_by`),
nicht über Klarnamen (siehe [Editorial Policy](Editorial_Policy.md)).

## 3. Formulierung der Forschungsfragen

Jedes Rechercheprotokoll (`research_questions[]`) formuliert Forschungsfragen **getrennt nach Themenbereich**
(`topic`): `identity`, `history`, `mechanism`, `pharmacokinetics`, `clinical`, `safety`, `preclinical`,
`regulatory`, `other`. Eine gute Forschungsfrage ist konkret genug, um zu entscheiden, ob eine gefundene Quelle
sie beantwortet („Welcher chemischen Klassifikation ist die Substanz zuzuordnen?"), nicht so vage, dass jede
Quelle irgendwie passt.

## 4. Definition des Untersuchungsgegenstands

Der Untersuchungsgegenstand (`subject.working_name`) ist zu Beginn ein **Arbeitsname**, kein bestätigter
kanonischer Name. Der kanonische Name, Entwicklungsbezeichnungen und Schreibvarianten (siehe
[Substanzschema](Phase_3_Scientific_Data_Architecture.md)) müssen durch eine belastbare Quelle bestätigt werden,
bevor sie in einen kanonischen `identity`-Claim einfließen (siehe Abschnitt 28).

## 5. Suchquellen und Quellenhierarchie

Nicht jede Datenbank hat denselben Stellenwert. `planned_information_sources[].role` unterscheidet:

- **`primary`** — geeignet als eigenständiger Beleg (PubMed/MEDLINE, ClinicalTrials.gov, FDA, EMA, WHO ICTRP).
- **`supplementary`** — ergänzend, ersetzt aber keine Primärquelle (Crossref, Cochrane Library).
- **`discovery_only`** — nur zum *Finden* von Kandidaten geeignet, niemals eigenständiger Wirksamkeitsnachweis
  (Google Scholar, Herstellerregister — siehe `data/vocabularies/source_types.yaml` zur Abgrenzung
  Händler-/Herstellerangabe von wissenschaftlicher Evidenz). Diese Zuordnung ist nicht nur redaktionelle
  Konvention: `schemas/research_protocol.schema.json` lehnt `database: google_scholar`/
  `manufacturer_registry` mit `role: primary`/`supplementary` strukturell ab (siehe ADR-0036 im
  [Decision Log](Decision_Log.md)).

Ein `search_run.database` muss außerdem tatsächlich unter `planned_information_sources[]` des referenzierten
Protokolls stehen — eine neue, im Protokoll noch nicht geplante Datenbank zu durchsuchen, ist ein
Validierungsfehler. Eine neue Datenbank erfordert eine neue Protokollversion (Abschnitt 31), die diese
Datenbank plant, **bevor** ein Suchlauf dagegen ausgeführt wird — keine stille Erweiterung nach Freigabe
(siehe ADR-0041 im [Decision Log](Decision_Log.md)).

## 6. Suchstrategie

Eine Suchstrategie kombiniert Konzepte (z. B. Substanzname, Zielrezeptor, Indikation, Studiendesign) mit
datenbankspezifischer Syntax. `planned_search_concepts[]` im Protokoll hält die **Konzepte** fest, bevor die
Recherche beginnt — die exakte, datenbankspezifische Syntax wird erst im jeweiligen Suchlauf (`search_run`)
dokumentiert (Abschnitt 7), da sie sich zwischen PubMed, ClinicalTrials.gov usw. unterscheidet.

## 7. Suchprotokollierung

Jeder tatsächlich ausgeführte Suchlauf wird als eigener `search_run`-Datensatz erfasst (Schema:
`schemas/research_search_run.schema.json`): exakter Suchstring (`exact_query`), Datenbank **und** Oberfläche
getrennt (`database`/`interface`), Zeitpunkt mit Uhrzeit (`executed_at`), Trefferzahl (`result_count`, muss
$\geq 0$ sein). Ein Suchlauf darf nur gegen ein Protokoll ausgeführt werden, dessen Status zum Zeitpunkt der
Validierung `approved` oder `superseded` ist — gegen ein noch nicht freigegebenes (`draft`) Protokoll wird kein
Suchlauf angelegt (`tools/validate_research.py`, siehe ADR-0036 im [Decision Log](Decision_Log.md)).

Ein Suchlauf wird **nie nachträglich verändert** — eine Korrektur oder Wiederholung erhält eine neue ID. Das
macht jede Recherche reproduzierbar: Jeder kann exakt nachvollziehen, was wann gesucht wurde. `status`
(`research/vocabularies/search_run_statuses.yaml`: `executed`/`superseded`/`withdrawn`) ist ein eigenständiges
Vokabular, bewusst getrennt von `editorial_status` — ein Suchlauf hat keinen Entwurfszustand, er wird erst als
Datei angelegt, nachdem er tatsächlich ausgeführt wurde (siehe ADR-0038). `tools/check_research_immutability.py`
prüft in CI zusätzlich, dass eine bereits gegenüber dem Zielbranch committete `search_run`-Datei nur in
`status`/`updated_at`/`review`/`notes` verändert wird — mit der dokumentierten Grenze, dass dieser Check nur
greift, wenn der Basis-Ref auflösbar ist, und keine serverseitige Branch Protection ersetzt (Abschnitt 34).

## 8. Deduplizierung

**Deduplizierung** bedeutet: erkennen, dass zwei gefundene Datensätze dieselbe zugrunde liegende Publikation
oder denselben Registereintrag beschreiben. Die `deduplication_policy` eines Protokolls legt die Priorität
stabiler externer Kennungen fest (`identifier_priority`, z. B. `[nct_id, doi, pmid, pmcid]`). Wird ein Duplikat
erkannt, wird der redundante Kandidat als `decision: duplicate` mit `duplicate_of`-Verweis auf den
„Hauptdatensatz" markiert (siehe [Evidence Curation Workflow](Evidence_Curation_Workflow.md)). Siehe auch
Abschnitt 16 zur Vermeidung von Doppelzählungen bei mehreren Publikationen derselben Studie.

Diese Regel ist nicht nur redaktionell, sondern wird von `tools/validate_research.py` tatsächlich durchgesetzt:
DOI/PMID/PMCID/NCT-ID/ISBN werden je Kandidat normalisiert (`tools/_researchlib.py`, wiederverwendet aus
`tools/_datalib.py` bzw. neu ergänzt für NCT-IDs — `NCT01234567`, `nct01234567` und `NCT 01234567` gelten als
identisch). Teilen sich zwei Screening-Datensätze **innerhalb desselben Protokolls** mindestens einen
normalisierten Identifikator und sind beide nicht als `duplicate` markiert, ist das ein Validierungsfehler.
Identifikator-Kollisionen **über verschiedene Protokolle hinweg** sind ausdrücklich erlaubt, da dieselbe
Publikation legitim in mehreren unabhängigen Recherche-Vorhaben auftauchen kann. Eine übereinstimmende
normalisierte URL löst nur eine Warnung aus, keinen Fehler — Redirects und Spiegelseiten können legitim
unterschiedliche, aber inhaltlich identische URLs erzeugen (analog zur Quellen-Deduplizierung, ADR-0026). Siehe
ADR-0039 im [Decision Log](Decision_Log.md).

`duplicate_of` muss innerhalb **desselben Protokolls** bleiben: Der Validator prüft nicht nur den unmittelbaren
Verweis, sondern die **gesamte Kette** verketteter Duplikate (A verweist auf B, B verweist auf den eigentlichen
Hauptdatensatz C) gegen die `protocol_id` des Ausgangsdatensatzes — zusätzlich zur bestehenden Zyklenerkennung
(kein Datensatz darf sich selbst oder über einen Kreis referenzieren). Ein als `duplicate` markierter Kandidat
zählt strukturell nie zu den „aktiven" Kandidaten (siehe oben) und ist damit auch nie extraktionsfähig
(Abschnitt 9b).

## 9b. Terminale Extraktionsfähigkeit

`decision_stage: final` ist die **einzige** extraktionsfähige Stufe — `decision_stage: full_text` dokumentiert
lediglich die Volltextbewertung, entscheidet aber noch nicht abschließend über eine Extraktion. Ein
`extraction_record` darf nur auf einen Screening-Datensatz verweisen, der **alle** folgenden Bedingungen
gleichzeitig erfüllt (`tools/validate_research.py`, siehe ADR-0042 im [Decision Log](Decision_Log.md)):

1. `decision: include`
2. `decision_stage: final`
3. `full_text_status: obtained`
4. Ist `final` in `screening_policy.dual_reviewer_stages` des Protokolls aufgeführt, liegt eine
   `second_review` vor.
5. Es gibt keinen ungelösten Widerspruch zwischen Erst- und Zweitentscheidung (siehe Abschnitt 10a) — entweder
   stimmen `second_review.reviewer_decision` und `decision` überein, oder eine gültige Adjudikation liegt vor.

Fehlt eine dieser Bedingungen, ist die Extraktion ein Validierungsfehler, unabhängig davon, ob der
zugrundeliegende Widerspruch zusätzlich schon auf Screening-Ebene beanstandet wird.

## 9a. Vollständige Screening-Historie

Ein `screening_record` speichert nicht nur den aktuellen Zustand, sondern die vollständige Abfolge aller
Entscheidungen in `decision_history[]`: je Eintrag Stufe, Entscheidung, Grund, verantwortliche Person, Zeitpunkt,
Volltextstatus und ggf. Zweitprüfung. Ein neuer Zustand wird redaktionell als neuer Eintrag **angehängt**, nie
durch Überschreiben eines früheren Eintrags ersetzt — so bleibt nachvollziehbar, dass ein Kandidat z. B. im
Titel-/Abstract-Screening zunächst `include` war, bevor er im Volltext-Screening doch ausgeschlossen wurde. Die
bestehenden Top-Level-Felder (`decision`, `decision_stage`, `decision_reason`, `full_text_status`,
`screened_by`, `screened_at`, `second_review`) bleiben aus Gründen der einfachen Abfragbarkeit erhalten, sind
aber eine vom Validator geprüfte **Projektion** des letzten `decision_history`-Eintrags — beide Darstellungen
dürfen nie auseinanderlaufen (siehe ADR-0037 im [Decision Log](Decision_Log.md)).

**Jeder** Eintrag in `decision_history[]` — nicht nur der letzte — wird gegen dieselben fachlichen Invarianten
geprüft wie der aktuelle Zustand: Stufe im Protokoll vorgesehen, Dual-Reviewer-Pflicht, Reviewer-/
Adjudikator-Unabhängigkeit, konsistente Zweitentscheidung, Konfliktlösung, Volltextvollständigkeit sowie eine
plausible Datumsreihenfolge (`decided_at <= second_review.reviewed_at <= adjudication.resolved_at`) und
nicht rückwärts laufende Stufen/Zeitpunkte über die Historie hinweg (ADR-0042).

**Grenze der Unveränderlichkeit:** `decision_history[]` ist ein **manuell editierbares Array innerhalb derselben
Datei**, kein separates, dateisystemseitig geschütztes Event-Log. „Append-only" ist eine redaktionelle
Konvention, die der Validator strukturell prüft (lückenlose Reihenfolge, keine Rückwärtsbewegung, konsistente
Projektion), aber nicht technisch erzwingen kann, dass ein früherer Eintrag nie nachträglich verändert statt
ergänzt wurde — anders als `research/search_runs/**`, das zusätzlich durch
`tools/check_research_immutability.py` in CI abgesichert ist (Abschnitt 7), gibt es für `decision_history[]`
keinen entsprechenden Git-Diff-Schutz.

## 9. Titel-/Abstract-Screening

Die erste inhaltliche Sichtungsstufe (`decision_stage: title_abstract`): anhand von Titel und Kurzfassung wird
entschieden, ob ein Kandidat prinzipiell zu den Forschungsfragen passt. Bereits hier kann ausgeschlossen werden
(z. B. `wrong_substance`), aber auch erst ein Volltext angefordert werden (`decision: awaiting_full_text`).

## 10. Volltext-Screening

Die zweite Stufe (`decision_stage: full_text`): erst nach Lektüre des vollständigen Textes wird final über
Einschluss oder Ausschluss entschieden. Ist diese Stufe (oder `final`) in `screening_policy.dual_reviewer_stages`
des Protokolls aufgeführt, ist eine zweite, unabhängige Prüfung (`second_review`, siehe Abschnitt 27) für eine
finale `include`/`exclude`-Entscheidung **verpflichtend** und wird vom Validator erzwungen — `second_review.
reviewed_by` muss sich zudem von `screened_by` unterscheiden (Reviewer-Unabhängigkeit). Ein finaler Einschluss
auf dieser oder der `final`-Stufe erfordert außerdem `full_text_status: obtained`; ohne vorliegenden Volltext
bleibt die Entscheidung `awaiting_full_text`, `uncertain` oder — mit kontrolliertem Grund — `exclude`.

## 10a. Eigenständige Zweitentscheidung und Widerspruchsauflösung durch Adjudikation

Eine Zweitprüfung dokumentiert eine **eigenständige, explizite Entscheidung** — `second_review.
reviewer_decision` ist schema-seitig Pflicht (nicht `null`), sobald `second_review` überhaupt gesetzt ist. Das
bisherige rein boolesche `decision_confirmed` bleibt als Feld erhalten, ist aber keine frei editierbare Angabe
mehr, sondern eine vom Validator geprüfte **Projektion** von `reviewer_decision == Erstentscheidung`: stimmen
`decision_confirmed` und dieser Vergleich nicht überein, ist das ein Validierungsfehler (ADR-0042).

Stimmen Erst- und Zweitentscheidung überein (`reviewer_decision == decision`), ist keine Adjudikation nötig.
Stimmen sie **nicht** überein, darf der Kandidat nicht unverändert als final eingeschlossen oder ausgeschlossen
weitergeführt werden. Zwei Wege sind zulässig: (1) die Entscheidung bleibt `decision: uncertain`, bis der
Widerspruch geklärt ist, oder (2) eine **dritte, von beiden vorherigen Personen unabhängige** Person löst den
Widerspruch über `second_review.adjudication` auf (`resolved_by`, `resolved_at`, `final_decision`,
`rationale`). `adjudication.resolved_by` darf weder dem Erstprüfer noch `second_review.reviewed_by`
entsprechen, und `adjudication.final_decision` muss mit der `decision` des jeweiligen Eintrags übereinstimmen
— beides wird vom Validator geprüft (`tools/validate_research.py`, siehe ADR-0039/ADR-0042 im
[Decision Log](Decision_Log.md)). Ein Datensatz mit ungelöstem Widerspruch (Entscheidungen weichen ab, keine
Adjudikation, `decision` ≠ `uncertain`) ist ein Validierungsfehler — und, sofern es sich um den terminalen
Eintrag handelt, zusätzlich nie extraktionsfähig (Abschnitt 9b).

## 11. Ein- und Ausschlusskriterien

`eligibility.inclusion_criteria`/`exclusion_criteria` im Protokoll legen die grundsätzlichen Kriterien fest;
die konkrete Entscheidung pro Kandidat wird im `screening_record` als `decision` + `decision_reason`
dokumentiert. `decision_reason` ist ein **kontrolliertes Vokabular**
(`research/vocabularies/exclusion_reasons.yaml`), kein Freitext — das macht Ausschlussentscheidungen über viele
Kandidaten hinweg auswertbar und vergleichbar. Eine Händlerseite oder ein Marketinginhalt darf niemals allein
als Beleg für eine wissenschaftliche Wirksamkeits-, Sicherheits- oder Mechanismusaussage eingeschlossen werden
(siehe [Evidenzsystem](../00_grundlagen/evidenzsystem.md)) — sie kann höchstens für eine ausdrücklich
attribuierte Händlerangabe berücksichtigt werden (Prädikat `claimed_by`, siehe
[Phase 3 Dokumentation](Phase_3_Scientific_Data_Architecture.md)).

## 12. Datenextraktion

**Extraktion** bedeutet: relevante Informationen aus einer eingeschlossenen Quelle strukturiert erfassen — als
kurze Paraphrase mit präziser Fundstelle (Seite/Tabelle/Abbildung/Abschnitt), nicht als langer wörtlicher
Textabschnitt (siehe Abschnitt 32). Ein `extraction_record` (Schema:
`schemas/research_extraction_record.schema.json`) trennt Beobachtungen nach Bereich (bibliografisch, Studie,
Population, Intervention, Vergleichsgruppe, Endpunkt, Sicherheit, Pharmakokinetik, Mechanismus, Limitationen) —
siehe Abschnitt 17 für die Zuordnung zur Evidenzkategorie.

## 13. Trennung von Studie und Publikation

Eine **Studie** (`data/entities/studies/**`) ist die durchgeführte Untersuchung selbst — ihr Design, ihre
Population, ihr Ablauf. Eine **Publikation** (eine `data/sources/**`-Quelle vom Typ
`peer_reviewed_publication`) ist ein Text, der über eine Studie berichtet. Eine Studie kann mehrere
Publikationen haben (Zwischenergebnisse, Endergebnisse, Sicherheits-Update); eine Publikation ist nicht
automatisch eine eigene Studie. Diese Trennung existiert bereits im kanonischen Datenmodell (siehe
[Data Model](Data_Model.md)) und wird durch die Recherche-Ebene konsequent fortgeführt: ein
`extraction_record` kann sowohl `canonical_source_id` (die Publikation) als auch `canonical_study_id` (die
Studie) referenzieren.

## 14. Verknüpfung von Registereintrag und Publikation

Ein Registereintrag (z. B. bei ClinicalTrials.gov) und ein Fachartikel über dieselbe Studie sind zwei
**verschiedene Quellen**, die dieselbe **eine Studie** beschreiben. Bei der Deduplizierung (Abschnitt 8) wird
die `nct_id` als starker Identifikator genutzt, um Registereintrag und Publikation demselben Studienobjekt
zuzuordnen, statt sie versehentlich als zwei unabhängige Studien zu behandeln.

## 15. Umgang mit mehreren Publikationen derselben Studie

Zwischenergebnisse, Endergebnisse, Subgruppenanalysen und Sicherheits-Updates derselben Studie werden als
**eigenständige Quellen** angelegt, aber alle über `study.source_ids`/`claim.evidence[].study_id` mit **derselben
Studie** verknüpft (siehe [Data Model](Data_Model.md)). So bleibt nachvollziehbar, dass es sich um eine Studie
mit mehreren Publikationszeitpunkten handelt, nicht um mehrere unabhängige Studien.

## 16. Vermeidung von Doppelzählungen

Ohne sorgfältige Verknüpfung (Abschnitte 13–15) könnte ein und derselbe Studienbefund mehrfach als „unabhängige"
Evidenz gezählt werden, wenn er in mehreren Publikationen auftaucht — das würde die Beleglage künstlich
verstärken. Deshalb: **ein Studienbefund, eine Studie**, unabhängig davon, wie viele Publikationen darüber
berichten. Follow-up-, Subgruppen- und Sicherheitsanalysen werden immer mit der Ursprungsstudie verknüpft, nie
als eigenständige, unabhängige Evidenz gezählt.

## 17. Evidenzkategorie versus Studiendesign

**Studiendesign** (`study_design`, z. B. `randomized_controlled_trial`, `animal_study`) beschreibt, *wie* eine
Studie aufgebaut ist. **Evidenzkategorie** (`evidence_category`, siehe
[Evidenzsystem](../00_grundlagen/evidenzsystem.md)) beschreibt, *welche Art* von Beleg eine Aussage stützt. Ein
Studiendesign legt die Evidenzkategorie nahe, bestimmt sie aber nicht automatisch: Eine methodisch gute
Tierstudie (`study_design: animal_study`) bleibt `preclinical_evidence`, unabhängig von ihrer Qualität — sie
wird nie zu `clinical_evidence` umformuliert, nur weil sie sauber durchgeführt wurde.

## 18. Bewertung der Sicherheit eines Claims

„Sicherheit" hat hier zwei Bedeutungen, die nicht verwechselt werden dürfen: **Certainty** (`certainty` am
Claim, siehe [Evidenzsystem](../00_grundlagen/evidenzsystem.md)) ist, wie sehr die Redaktion einer Aussage
vertraut — getrennt von der Evidenzkategorie und redaktionell mit `certainty_rationale` begründet, nie
automatisch aus dem Studiendesign berechnet. **Arzneimittelsicherheit** (Abschnitt 25 im Sinne unerwünschter
Ereignisse) ist ein inhaltliches Thema, das selbst wieder Claims mit eigener Evidenzkategorie und eigenem
Certainty-Wert erzeugt.

## 19. Umgang mit Preprints

Ein Preprint ist eine Publikation, die noch **kein** Peer-Review durchlaufen hat (`source_type: preprint`,
`peer_review_status: not_peer_reviewed`). Preprints werden gesondert behandelt (Abschnitt 11, „Gesondert
behandeln") — sie dürfen als Kandidat eingeschlossen und extrahiert werden, aber nicht automatisch wie eine
peer-reviewte Primärstudie gewichtet werden. Wird ein Preprint später als reguläre Publikation akzeptiert,
entsteht dafür ein eigener Quellendatensatz, der über `study_id` mit derselben Studie verbunden bleibt
(Abschnitt 15).

## 20. Umgang mit Konferenzabstracts

Ein Konferenzabstract (`source_type: conference_abstract`) enthält typischerweise nur vorläufige, unvollständige
Ergebnisse. Er wird als `limited_evidence` behandelt (siehe [Evidenzsystem](../00_grundlagen/evidenzsystem.md)),
nicht automatisch aufgewertet, auch wenn eine spätere Vollpublikation folgt — diese wird dann als eigene Quelle
erfasst und mit der Studie verknüpft (Abschnitt 15).

## 21. Umgang mit regulatorischen Dokumenten

Nur offizielle Dokumente zuständiger Behörden (FDA, EMA oder vergleichbare) gelten als maßgebliche Grundlage für
eine regulatorische Aussage (`claim_type: regulatory`). Ein ClinicalTrials.gov-Eintrag ist ein
**Studienregister**, keine Zulassungsentscheidung — beides wird nie verwechselt oder vermischt (siehe
[Redaktionsstandard](../00_grundlagen/redaktionsstandard.md), „Trennung der Ebenen").

## 22. Umgang mit Herstellerinformationen

Herstellerdokumente (`source_type: manufacturer_document`) und Herstellerregister sind zulässige Quellen für
**attribuierte** Entwicklungsinformationen (z. B. „Hersteller X gibt Entwicklungsphase Y an", modelliert über
das Prädikat `claimed_by`, siehe [Phase 3 Dokumentation](Phase_3_Scientific_Data_Architecture.md)) — niemals
aber als eigenständiger wissenschaftlicher Wirksamkeits- oder Sicherheitsnachweis.

## 23. Umgang mit Händlerseiten

Eine Händlerseite (`source_type: merchant_page`) darf als Kandidat erfasst werden, wird aber nur für eine
ausdrücklich als Händlerangabe gekennzeichnete Aussage eingeschlossen (`evidence_category: merchant_claim`,
Prädikat `claimed_by`). Sie darf niemals der alleinige Beleg für eine aktive, medizinisch relevante
Wirksamkeits-, Sicherheits- oder Mechanismusaussage sein — das wird sowohl im Screening (Abschnitt 11) als auch
später vom Datenvalidator (`tools/validate_data.py`) durchgesetzt.

## 24. Umgang mit persönlichen Erfahrungen

Ein Einzelbericht oder Erfahrungsbericht (`source_type: personal_report`) wird analog zur Händlerseite
behandelt: zulässig als ausdrücklich attribuierte Beobachtung (`evidence_category: personal_experience`,
Prädikat `reported_by`), niemals als allgemeiner Wirksamkeitsnachweis.

## 25. Retractions, Corrections und Expressions of Concern

Jede Quelle trägt einen `retraction_status` (siehe [Data Model](Data_Model.md)): `not_retracted`, `retracted`,
`expression_of_concern`, `corrected` oder `unknown`. Wird eine bereits eingeschlossene Quelle später
zurückgezogen, muss dieser Status aktualisiert werden — ein aktiver Claim, der ausschließlich auf einer
zurückgezogenen Quelle beruht, ist ein Fehler; eine zurückgezogene Quelle neben weiteren gültigen Quellen löst
eine Warnung aus (siehe `tools/validate_data.py`). Korrekturen und Retraction Notices zu bereits eingeschlossenen
Quellen werden selbst als (verknüpfte) Kandidaten erfasst, nicht stillschweigend ignoriert.

## 26. Interessenkonflikte und Finanzierung

Bei der Extraktion wird dokumentiert, wenn eine Quelle offengelegte Interessenkonflikte oder eine
Industriefinanzierung nennt (als Beobachtung, z. B. unter `study_observations`). Das fließt in die
redaktionelle `certainty`-Bewertung ein (Abschnitt 18), ersetzt aber nicht die inhaltliche Prüfung — ein
finanzierter Claim ist nicht automatisch falsch, muss aber transparent eingeordnet werden.

## 27. Extraktionskontrolle durch zweite Prüfung

`extraction_status: verified` bedeutet in Peptide Atlas **immer**: eine **zweite Person** (`verified_by`) hat
zu einem **getrennt dokumentierten Zeitpunkt** (`verified_at`) die Extraktion bestätigt — nicht dieselbe
Person, die extrahiert hat (`extracted_by`). Diskrepanzen zwischen Erst- und Zweitprüfung werden in
`discrepancies[]` festgehalten, nicht stillschweigend geglättet.

## 27a. Unbedingte Verifikationsunabhängigkeit; `self_checked` für Ein-Personen-Durchläufe

`verified_by != extracted_by` wird von `tools/validate_research.py` **unbedingt** erzwungen, sobald
`extraction_status: verified` gesetzt ist — es gibt **keine** protokollabhängige Ausnahme mehr (frühere
Fassung dieses Abschnitts, abgelöst durch ADR-0040 im [Decision Log](Decision_Log.md)). Für einen rein
technischen Ein-Personen-Durchlauf ohne unabhängige Zweitprüfung (z. B. Strukturtest, Platzhalterdaten) steht
stattdessen `extraction_status: self_checked` zur Verfügung — ehrlich benannt, ohne den Anschein einer
unabhängigen Prüfung zu erwecken. Eine `self_checked`-Extraktion ist **strukturell nie promotion-fähig**: ein
`promotion_record` darf sich nur auf eine Extraktion mit `extraction_status: verified` beziehen (Abschnitt 29).

## 28. Erstellung atomarer Claims

Ein **atomarer Claim** ist eine einzeln prüfbare Aussage (siehe
[Phase 3 Dokumentation](Phase_3_Scientific_Data_Architecture.md)) — „Substanz X bindet an Rezeptor Y" ist ein
Claim, nicht „Substanz X: Übersicht über Wirkung und Sicherheit". Bei der Extraktion werden
**Kandidatenclaims** (`candidate_claims[]`) formuliert: vorläufig, ausdrücklich ungeprüft
(`is_provisional: true`), mit präziser Fundstelle. Sie tragen bewusst **kein** Status-Feld — ein Kandidatenclaim
kann strukturell nicht als „aktiv" markiert werden (siehe [Evidence Curation Workflow](Evidence_Curation_Workflow.md)).

## 29. Promotion in die kanonische Datenebene

**Promotion** bedeutet: aus einem verifizierten Extraktionsdatensatz wird — nach wissenschaftlichem Review —
manuell eine kanonische Datei unter `data/sources/**`, `data/entities/studies/**` oder `data/claims/**`
angelegt. Dieser Schritt ist in Phase 4A **bewusst nicht automatisiert**: kein Werkzeug erzeugt selbstständig
eine `data/claims/*.yaml`-Datei aus einem `candidate_claims`-Eintrag. Voraussetzung für die Promotion eines
medizinisch relevanten Claims ist ein zweiter Review oder eine dokumentierte unabhängige Kontrollprüfung (siehe
Abschnitt 13 des ursprünglichen Auftrags sowie [Evidence Curation Workflow](Evidence_Curation_Workflow.md)).

Diese Kette ist seit ADR-0037 maschinenlesbar: ein `promotion_record` (Schema:
`schemas/research_promotion_record.schema.json`, `research/promotions/`) verweist auf `extraction_record_id`
(muss `extraction_status: verified` sein) und `candidate_working_id` (muss im referenzierten Extraktionsdatensatz
vorkommen) und trägt `promotion_status`. Nur die Zustände `approved_for_creation` und `promoted` erfordern
dokumentierte Reviewer und eine `decision_rationale` — und dürfen, wie jede Aktivierung eines kanonischen Claims,
**nie** automatisiert durch Automatisierung/KI gesetzt werden (ADR-0035). `promoted` erfordert eine gesetzte
`canonical_claim_id`, die tatsächlich unter `data/claims/**` existiert; `rejected` darf keine tragen. Pro
Kandidat ist höchstens ein aktiver (nicht `rejected`/`withdrawn`) `promotion_record` gleichzeitig zulässig.
Ein `promotion_record` darf sich zudem nur auf eine Extraktion mit `extraction_status: verified` beziehen —
`self_checked` (Abschnitt 27a) ist strukturell nie promotion-fähig.

Setzt das referenzierte Protokoll `claim_promotion_policy.requires_second_review: true`, erzwingt der Validator
zusätzlich, dass `promotion_status: approved_for_creation`/`promoted` mindestens **zwei unterschiedliche,
nicht-leere** Einträge in `review.reviewers` tragen (ADR-0041). **Ausdrückliche Grenze dieser Prüfung:** Sie
stellt technisch nur sicher, dass zwei unterschiedliche *Kürzel* eingetragen sind — sie kann nicht
maschinenlesbar verifizieren, dass es sich dabei tatsächlich um zwei unterschiedliche *menschliche* Personen
handelt (im Unterschied zu Automatisierung/KI), da Phase 4A **keine** maschinenlesbare Akteur-Registry
(human/automation/ai_assistant/service) einführt. Diese Garantie bleibt organisatorisch — durch
Reviewprozess und Repository-Zugriffskontrolle — abgesichert, nicht durch das Schema (siehe Abschnitt 34).

## 30. Aktualisierungen und Rechercheanläufe

Ein neuer Rechercheanlauf (z. B. jährliche Aktualisierung) verwendet dasselbe Protokoll (ggf. eine neue Version,
Abschnitt 31) und erzeugt neue `search_run`-Datensätze. Bereits kanonisch veröffentlichte Claims werden bei
neuen, widersprechenden Erkenntnissen nicht stillschweigend überschrieben, sondern durchlaufen erneut den
Reviewprozess (siehe [Editorial Policy](Editorial_Policy.md), Statuslogik in
[Quality Standards](Quality_Standards.md)).

## 31. Protokolländerungen

Eine inhaltliche Änderung am Protokoll (neue Suchbegriffe, angepasste Kriterien) wird als **neue Version**
angelegt (`research-protocol-<slug>-v2.yaml` usw., siehe `amendment_policy`), nicht als stille Überschreibung
der bestehenden Datei — damit bleibt nachvollziehbar, unter welcher Protokollversion ein bestimmter Suchlauf
oder Screening-Entscheid getroffen wurde.

## 32. Urheberrecht und Volltextspeicherung

Datenbankanbieter und Verlage untersagen meist die Weiterverbreitung von Volltexten oder vollständigen
Exporten. Peptide Atlas speichert deshalb **nur kurze Paraphrasen mit präziser Fundstelle**
(`schemas/common.schema.json#/$defs/short_paraphrase`, technisch auf 600 Zeichen je Sprache begrenzt), keine
längeren wörtlichen Textübernahmen. Volltexte oder Exporte, die lokal benötigt werden, gehören ausschließlich
nach `research/raw/` — ein per `.gitignore` nicht versionierter, rein lokaler Arbeitsbereich (siehe
`research/raw/README.md`).

## 33. Auditierbarkeit und Reproduzierbarkeit

Jeder Schritt ist einer Person/Rolle und einem Zeitpunkt zugeordnet (`screened_by`/`screened_at`,
`extracted_by`/`extracted_at`, `verified_by`/`verified_at`). Jeder Suchlauf ist durch den exakten Suchstring
reproduzierbar. `screened_at` muss zeitlich nach `executed_at` **jedes einzelnen** in `search_run_ids[]`
referenzierten Suchlaufs liegen, nicht nur nach dem frühesten — ein Screening kann nicht vor Abschluss aller
Suchläufe stattgefunden haben, die es angeblich auswertet. Jede Ausschlussentscheidung trägt einen kontrollierten Grund. Jeder Kandidatenclaim trägt eine
präzise Fundstelle. In der Summe lässt sich für jeden künftigen kanonischen Claim lückenlos zurückverfolgen: aus
welchem Suchlauf er stammt, wer ihn wann geprüft hat, und welche konkrete Textstelle ihn stützt — auch bei
100.000 Quellen, weil jeder Schritt strukturiert (nicht als Fließtext) und maschinell validierbar
(`tools/validate_research.py`) gespeichert wird.

## 34. Bekannte Grenzen

Diese Liste unterscheidet ausdrücklich, **wie** eine Regel abgesichert ist — eine Behauptung wie „strukturell
nicht automatisierbar" oder „lückenlos validiert" ist nur zulässig, wenn die Implementierung sie tatsächlich
maschinenlesbar sicherstellt:

- **Schema-seitig erzwungen** (JSON-Schema-Validierung, z. B. Pflichtfelder, Enums, `additionalProperties:
  false`): `google_scholar`/`manufacturer_registry` nur `discovery_only`, `candidate_claims[]` ohne
  Status-Feld, `second_review.reviewer_decision` nicht `null`, `promoted`/`rejected`-Bedingungen an
  `canonical_claim_id`.
- **Validator-seitig erzwungen** (`tools/validate_research.py`, blockiert Pull Requests via CI, aber nicht
  außerhalb eines CI-Laufs, z. B. bei einem direkten Push ohne PR): Protokoll-/Referenzkonsistenz,
  Identifier-Deduplizierung, Screening-Workflow inkl. jedes `decision_history`-Eintrags, terminale
  Extraktionsfähigkeit, Verifikationsunabhängigkeit, Claim-Promotion-Kette inkl.
  `requires_second_review`-Reviewerzahl.
- **CI-seitig geprüft, mit dokumentierter Lücke**: `tools/check_research_immutability.py` (ADR-0038/ADR-0042)
  vergleicht nur den Nettounterschied zum Merge-Base mit einem einzelnen Basis-Ref und wird übersprungen, wenn
  dieser nicht auflösbar ist (z. B. ein lokaler Push ohne Pull-Request-Kontext) — er erkennt keine Manipulation,
  die bereits vor diesem Vergleichszeitpunkt auf dem Zielbranch selbst stattgefunden hat, und ersetzt keine
  serverseitige Branch Protection (ADR-0010, weiterhin nicht umgesetzt). Für `decision_history[]` (Abschnitt 9a)
  gibt es **keinen** entsprechenden Git-Diff-Schutz — nur die strukturelle Konsistenzprüfung bei der
  Validierung.
- **Redaktionell vorgeschrieben, nicht technisch erzwungen**: Append-only-Pflege von `decision_history[]`
  innerhalb derselben Datei (Abschnitt 9a); die Erkennung „derselbe Studie, mehrere Publikationen"
  (Abschnitte 13–16) mit Unterstützung durch `identifier_priority`, aber ohne automatische
  Studienzusammenführung; inhaltliche Richtigkeit von Beobachtungen, Paraphrasen und Kandidatenclaims.
- **Organisatorisch kontrolliert, nicht technisch überprüfbar**: Ob ein Reviewer-, Adjudikator- oder
  Promotion-Reviewer-**Kürzel** tatsächlich eine andere *menschliche* Person bezeichnet (statt z. B. zweier
  unterschiedlicher Automatisierungsläufe), lässt sich mit den in Phase 4A verwendeten freien String-Feldern
  **nicht** maschinenlesbar verifizieren — Phase 4A führt bewusst **keine** Actor-Registry
  (human/automation/ai_assistant/service) ein (siehe Abschnitt 29, ADR-0041 „Alternativen"). Diese Garantie
  bleibt organisatorisch, durch Reviewprozess und Repository-Zugriffskontrolle abgesichert. Jede Dokumentation,
  die eine stärkere (technisch erzwungene) Garantie behauptet, ist als Fehler zu melden.
- **Derzeit nicht technisch überprüfbar / bewusst nicht implementiert**: keine automatisierte Literaturrecherche,
  keine automatische Quellenabfrage über externe APIs — jeder Suchlauf wird manuell ausgeführt und
  protokolliert; kein PDF-Download oder Volltextarchivierung im Repository; die Identifier-Deduplizierung
  (Abschnitt 8) erkennt nur **exakte** Kollisionen normalisierter DOI/PMID/PMCID/NCT-ID/ISBN, keine
  fuzzy-übereinstimmenden Titel, keine Duplikate ohne gemeinsamen stabilen Identifikator und keine semantische
  Ähnlichkeit.
- Phase 4A implementiert das **Protokoll und die Werkzeuge**, nicht die eigentliche Recherche. Es gibt noch
  keine echten `search_run`-, `screening_record`-, `extraction_record`- oder `promotion_record`-Datensätze zu
  Retatrutid.
- Ein `promotion_record` (Abschnitt 29) macht die Kette bis zum kanonischen Claim maschinenlesbar
  nachvollziehbar, ersetzt aber nicht die inhaltliche wissenschaftliche Prüfung, ob der kanonische Claim den
  Kandidatenclaim tatsächlich korrekt wiedergibt — diese Prüfung bleibt Aufgabe der wissenschaftlichen
  Redaktion beim Review von `promotion_status: approved_for_creation`.

---
title: "Phase 4B-1B-2 – Deduplication & Workflow Architecture (Proposed)"
description: Architektur-Entwurf für ein Workflow-State-Modell, eine vollständige Deduplizierungsarchitektur und ein erweitertes Publikationstyp-Datenmodell. Reine Spezifikation, keine Implementierung.
tags:
  - Architektur
  - Projekt
  - Datenmodell
---

# Phase 4B-1B-2 – Deduplication & Workflow Architecture (Proposed)

!!! warning "Status: Vorgeschlagen, nicht entschieden"
    Dieses Dokument ist ein **Architektur-Entwurf** (siehe ADR-0058 im [Decision Log](Decision_Log.md),
    Status „Vorgeschlagen"). Es enthält **keine Implementierung**: keine Schema-Änderungen, keine
    Validator-Änderungen, keine veränderten oder neuen Screening Records. Alle Codeblöcke in diesem
    Dokument sind Entwürfe zur Diskussion, keine bereits angewendeten Artefakte. Nichts hier schaltet
    eine wissenschaftliche Entscheidung frei oder trifft eine.

## 0. Anlass und Ausgangslage

Phase 4B-1B-1 (PR [#6](https://github.com/PeptideAtlas/peptide-atlas/pull/6), gemerged, ADR-0057) hat bei
der Initialisierung der 197 realen Retatrutide-Screening-Records eine reale Datenkollision aufgedeckt: drei
PubMed-PMIDs (`37888925`, `37888926`, `37888927`) teilen sich dieselbe DOI `10.1056/NEJMc2310645` — ein
NEJM-Correspondence-Letter (evtl. doppelt indexiert) plus dessen separat indexierte Reply. Die damalige
Lösung (`check_deduplication`-Herabstufung zu einer Warnung, solange ein beteiligter Datensatz noch nicht
von einem Menschen übernommen wurde) war eine **explizite, aber bewusst provisorische** Nutzerentscheidung,
um die Initialisierung nicht zu blockieren — mit der ausdrücklichen Ankündigung im PR-#6-Bericht, dass diese
Regel selbst noch keinen eigenständigen CSO-Review durchlaufen hatte.

Dieses Dokument beantwortet die daraus folgende CSO-Rückfrage mit einem vollständigen Architektur-Entwurf,
statt die Ad-hoc-Lösung aus ADR-0057 stillschweigend als Dauerzustand zu belassen. Drei strukturelle
Probleme der aktuellen Lösung werden dabei behoben:

1. **`screened_by`-basierte Validatorlogik ist eine Zweckentfremdung.** ADR-0057 nutzt
   `screened_by == system-screening-initializer` als Stellvertreter für „wurde dieser Datensatz schon von
   einem Menschen bearbeitet?" — eine Akteursidentität wird als Workflow-Zustand missbraucht, an **zwei**
   unabhängigen Stellen im Code (`check_screening_system_actor_invariants`,
   `check_deduplication`) redundant neu hergeleitet.
2. **`decision: duplicate` ist strukturell überladen.** Der bestehende Deduplizierungsmechanismus
   (Abschnitt 8 im [Scientific Research Protocol](Scientific_Research_Protocol.md)) kennt nur eine einzige
   Beziehung zwischen zwei Kandidaten: „identisch, einer ist redundant". Das ist korrekt für eine
   doppelt indexierte PMID, aber **fachlich falsch** für einen Letter+Reply-Fall — eine Reply ist kein
   redundantes Duplikat des Letters, sie hat eigenen Inhalt und muss unabhängig screenbar/extrahierbar
   bleiben. Der aktuelle Validator kann diesen Unterschied nicht ausdrücken.
3. **`candidate_source_type` ist zu grobkörnig**, um Publikationstypen wie Letter/Reply/Editorial/
   Corrigendum überhaupt zu erkennen — genau das hätte die Kollision von vornherein einordnen können,
   ohne eine wissenschaftliche Bewertung zu erfordern (siehe Abschnitt 4).

## 1. Workflow-State-Modell statt `screened_by`-basierter Validatorlogik

### 1.1 Problem

`tools/validate_research.py::check_screening_system_actor_invariants` und `check_deduplication`
(ADR-0057-Anpassung) leiten beide unabhängig voneinander denselben Sachverhalt her — „ist der aktuelle
effektive Bearbeiter noch der technische Systemakteur?" — durch einen String-Vergleich gegen
`SYSTEM_SCREENING_INITIALIZER_ACTOR`. Das hat drei konkrete Schwächen:

- **Duplizierte Herleitung.** Zwei Funktionen implementieren dieselbe Bedingung unabhängig voneinander.
  Ändert sich die Semantik (z. B. weil ein zweiter technischer Akteur für eine andere Automatisierung
  eingeführt wird), müssen beide Stellen synchron aktualisiert werden — ein klassisches Risiko für
  stillschweigendes Auseinanderlaufen.
- **Konzeptionelle Vermischung.** `screened_by` beantwortet „wer hat zuletzt entschieden?" (Akteursfrage).
  Die eigentlich benötigte Frage ist „in welchem Bearbeitungszustand befindet sich dieser Datensatz?"
  (Workflow-Frage). Beide Fragen sind orthogonal, werden aber aktuell aus demselben Feld beantwortet.
- **Nicht erweiterbar.** Ein binärer Zustand (System vs. Mensch) reicht für ADR-0057 gerade so aus, trägt
  aber keine der in Abschnitt 2 benötigten Zwischenzustände (z. B. „menschlich referenziert, aber
  Kollision noch nicht klassifiziert").

### 1.2 Entwurf: `workflow_state`

Neues, **optionales** (additiv, kein Schema-Versionsbump nötig) Feld auf `research_screening_record`:

```yaml
workflow_state: system_initialized  # kontrolliertes Vokabular, siehe unten
```

Kontrolliertes Vokabular (neu, `research/vocabularies/screening_workflow_states.yaml`):

| Wert | Bedeutung | Ableitungsregel (Validator-Projektion) |
|---|---|---|
| `system_initialized` | Noch nie von einem Menschen bearbeitet. | `len(decision_history) == 1` UND `decision_history[0].decided_by == system-screening-initializer`. |
| `under_human_review` | Mindestens ein Mensch hat den Datensatz übernommen, aber die Screening-Entscheidung ist noch nicht terminal abgeschlossen. | Mindestens ein `decision_history`-Eintrag mit `decided_by != system-screening-initializer`, UND NICHT die `finalized`-Bedingung. |
| `finalized` | Die Screening-Entscheidung ist terminal und widerspruchsfrei abgeschlossen. | `decision_stage == final` UND `decision ∈ {include, exclude}` UND kein ungelöster Erst-/Zweitprüfungs-Widerspruch (dieselbe Bedingung wie die bestehende terminale Extraktionsfähigkeit, Abschnitt 9b im Scientific Research Protocol, MINUS die `full_text_status: obtained`-Anforderung — `finalized` beschreibt den Abschluss der **Entscheidung**, nicht die Extraktionsbereitschaft). |

**Wichtig — dies ist wie `decision`/`decision_stage` selbst eine vom Validator geprüfte Projektion**
(`check_screening_workflow_state_projection`, neu), kein frei editierbares Feld und **keine zweite
Wahrheitsquelle**: `decision_history[]` bleibt die einzige tatsächliche Datengrundlage. `workflow_state`
ist eine denormalisierte, direkt abfragbare Sicht darauf — exakt dasselbe Muster, das bereits für
`decision`/`decision_stage`/`screened_by` als Projektion von `decision_history[-1]` etabliert ist
(ADR-0037). Kein neuer Präzedenzfall, sondern eine konsequente Anwendung des bestehenden Musters auf ein
bisher nur implizit vorhandenes Konzept.

### 1.3 Auswirkung auf bestehende Prüfungen

- `check_screening_system_actor_invariants`: die zweite Invariante (canonical_source_id/candidate_title
  nur solange der Systemakteur aktueller Bearbeiter ist) wird auf `workflow_state == system_initialized`
  umgestellt statt auf `screened_by == SYSTEM_SCREENING_INITIALIZER_ACTOR`. Die erste Invariante (jeder
  `decision_history`-Eintrag mit `decided_by == system-screening-initializer` bleibt strukturell neutral)
  bleibt unverändert — das ist korrekt an die Akteursidentität gebunden, nicht an den Workflow-Zustand.
- `check_deduplication`: `dedup_phase_pending` wird zu
  `any(o.data.get("workflow_state") == "system_initialized" for o in active)` — inhaltlich identisch zum
  heutigen Verhalten, aber aus einer einzigen, zentral geprüften Quelle statt einem wiederholten
  String-Vergleich.

### 1.4 Offene Frage: lohnt sich ein vierter Zustand?

Ein zusätzlicher Zwischenzustand `flagged_for_dedup_review` (automatisch gesetzt, sobald ein Datensatz
Teil einer noch ungelösten Identifikator-Kollision ist, siehe Abschnitt 2) würde ein direkt abfragbares
Arbeits-Worklist für menschliche Reviewer ermöglichen, ohne den Validator erneut laufen lassen zu müssen.
**Das ist bewusst nicht Teil dieses Entwurfs** — es wäre ein von Validierungsergebnissen abgeleiteter,
selbst wieder zu pflegender Zustand (wer setzt ihn zurück, wenn die Kollision aufgelöst wird?) und damit
ein potenzieller neuer Ort für Drift. Empfehlung: erst einführen, wenn ein konkretes Tooling-Bedürfnis
(z. B. ein Dedup-Dashboard) das rechtfertigt.

## 2. Vollständige Deduplizierungsarchitektur

### 2.1 Zwei fundamental verschiedene Beziehungen, eine falsch überladene

Der aktuelle `check_deduplication` behandelt **jede** Identifikator-Kollision gleich: „einer der beiden
muss `duplicate` sein". Das ist nur für eine der beiden real vorkommenden Beziehungsarten korrekt.

| | **Bibliographische Dublette** | **Studienverknüpfte, aber eigenständige Publikation** |
|---|---|---|
| **Definition** | Zwei Kandidaten beschreiben **exakt denselben Text** — typischerweise ein Datenbank-Indexierungsartefakt (z. B. doppelt vergebene PMID für dieselbe Einreichung). | Zwei Kandidaten sind **unterschiedliche Texte**, die sich auf dieselbe Studie/denselben wissenschaftlichen Vorgang beziehen (Registereintrag + Publikation, Zwischen-/Endergebnis, Letter + Reply, Preprint + publizierte Fassung). |
| **Inhalt** | Identisch (oder trivial redundant). | Unterschiedlich — jede Publikation kann eigene, nicht in der anderen enthaltene Fakten tragen. |
| **Screening-Konsequenz** | Nur EINE Version wird unabhängig gescreent/extrahiert; die andere ist `decision: duplicate`. | **Beide** bleiben unabhängig screenbar/extrahierbar — aber ihre spätere Evidenz darf beim Claim-Aufbau nicht doppelt gezählt werden (Abschnitt 16 im Scientific Research Protocol). |
| **Bestehendes Feld** | `duplicate_of` (bereits vorhanden, bleibt unverändert). | **Fehlt aktuell vollständig** — genau die Lücke, die die DOI-Kollision aus Phase 4B-1B-1 aufgedeckt hat. |
| **Beispiel aus echten Daten** | Falls PMID 37888925 und 37888926 tatsächlich dieselbe Einreichung doppelt indexieren (noch nicht bestätigt). | PMID 37888927 (Reply) zum Letter — unabhängig vom Duplikat-Verdacht der beiden anderen PMIDs. Ebenso: jede PubMed-Publikation zu einer Studie, die auch einen ClinicalTrials.gov-Registereintrag hat (siehe Abschnitt 5). |

**Kernregel dieses Entwurfs:** `decision: duplicate`/`duplicate_of` bleibt ausschließlich für
bibliographische Dubletten reserviert. Für die zweite Kategorie wird ein neues, separates Feld
eingeführt (`related_records[]`, siehe 2.2) — es wird **niemals** durch `duplicate_of` ersetzt oder
imitiert, selbst wenn beide Kandidaten denselben Identifikator teilen.

### 2.2 Entwurf: `related_records[]`

Neues, optionales Feld auf `research_screening_record`:

```yaml
related_records:
  - screening_record_id: screening-record-3d3643ee-cdd8-4fee-9869-b963aece7a34
    relationship_type: letter_and_reply
    rationale: >
      Teilt DOI 10.1056/NEJMc2310645 mit PMID 37888925/37888926, aber eigener Titel
      ("... Reply.") und eigener PMID -- eigenständiger Text, keine Dublette.
    identified_by: reviewer-1
    identified_at: '2026-08-03'
```

Schema-Entwurf:

```json
"related_records": {
  "type": "array",
  "default": [],
  "items": {
    "type": "object",
    "properties": {
      "screening_record_id": {
        "type": "string",
        "pattern": "^screening-record-[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}$"
      },
      "relationship_type": { "$ref": "common.schema.json#/$defs/screening_relationship_type" },
      "rationale": { "type": "string", "minLength": 1 },
      "identified_by": { "$ref": "common.schema.json#/$defs/research_actor_id" },
      "identified_at": { "$ref": "common.schema.json#/$defs/date" }
    },
    "additionalProperties": false,
    "required": ["screening_record_id", "relationship_type", "rationale", "identified_by", "identified_at"]
  }
}
```

Neues kontrolliertes Vokabular `research/vocabularies/screening_relationship_types.yaml`
(`$defs/screening_relationship_type` in `common.schema.json`) — siehe Abschnitt 6 für die vollständige
Werteliste und Begründung je Wert.

**`rationale` ist Pflichtfeld mit Freitext, keine automatisch generierte Zeichenkette** — das erzwingt,
dass ein Mensch die Beziehung tatsächlich begründet, statt sie nur aus einem Dropdown zu wählen. Analog
zu `decision_reason`/`primary_decision_reason` (kontrolliertes Vokabular) UND `adjudication.rationale`
(Freitext) im bestehenden Schema — hier bewusst Freitext, weil die Beziehungsarten in Abschnitt 6 zu
grobkörnig sind, um jede reale Konstellation ohne Begründung eindeutig zu machen.

### 2.3 Validator-Konsequenzen (Entwurf)

**`check_screening_related_records`** (neu):
- Referenzielle Prüfung wie bei `duplicate_of`: Ziel existiert als `screening_record`, gleiches
  `protocol_id`, kein Selbstverweis.
- **Symmetrie-Pflicht:** verweist A auf B mit einem `relationship_type`, muss B eine passende
  Gegenreferenz auf A tragen (v1: identischer `relationship_type` in beide Richtungen — siehe
  offene Frage 2.4 zur Richtungsabhängigkeit einzelner Typen).
- `identified_by` darf nicht `system-screening-initializer` sein — diese Klassifikation ist per
  Definition eine inhaltliche Einordnung, die dem technischen Akteur nicht zusteht (dieselbe Grenze wie
  ADR-0057 für `decision`).

**`check_deduplication`** (angepasst): eine Identifikator-Kollision zwischen zwei Datensätzen, die
sich bereits über eine **symmetrische** `related_records`-Beziehung referenzieren, ist **weder Fehler
noch Warnung** — sie gilt als explizit klassifiziert und aufgelöst. Eine Kollision ohne
`related_records`-Eintrag bleibt wie bisher: Warnung, solange mindestens ein beteiligter Datensatz noch
`workflow_state: system_initialized` ist; Fehler, sobald alle beteiligten Datensätze `workflow_state !=
system_initialized` sind.

Damit ergibt sich pro Kollisionsgruppe genau einer von drei zulässigen End-Zuständen:
1. Alle bis auf einen Datensatz sind `decision: duplicate` mit `duplicate_of` auf den verbleibenden
   Hauptdatensatz (bibliographische Dublette).
2. Jedes Paar der Gruppe trägt eine symmetrische `related_records`-Klassifikation (eigenständige, aber
   verwandte Publikationen).
3. Eine Kombination aus beidem (z. B. zwei echte Dubletten, von denen eine zusätzlich mit einem dritten,
   inhaltlich verwandten, aber eigenständigen Datensatz verknüpft ist).

Ein Zustand, in dem die Kollision weder durch (1) noch (2) erklärt ist, bleibt ein Validierungsfehler,
sobald kein beteiligter Datensatz mehr `system_initialized` ist — identisch zur heutigen Sicherheitsgrenze
aus ADR-0057, nur jetzt mit einem echten Auflösungsweg für den Fall, der in Phase 4B-1B-1 nicht abbildbar
war.

### 2.4 Offene Frage: Richtungsabhängigkeit

Einige Beziehungstypen sind inhaltlich **nicht symmetrisch** — „A ist die Reply zu Letter B" trägt mehr
Information als „A und B sind ein Letter/Reply-Paar". Zwei Optionen zur Diskussion:
- **Option A (dieser Entwurf, v1):** ein einziger, ungerichteter `relationship_type`-Wert
  (`letter_and_reply`), keine Richtung. Einfacher, aber verliert die Information, welcher Datensatz der
  ursprüngliche Letter und welcher die Reply ist (die steht ohnehin schon in `candidate_title`/
  `metadata`, ist also nicht verloren, nur nicht strukturiert an der Beziehung selbst).
- **Option B:** gerichtete Typen (`replies_to`/`is_replied_to_by`,
  `corrects`/`is_corrected_by`, `interim_result_of`/`has_interim_result`, ...) — präziser, verdoppelt
  aber die Vokabulargröße und erschwert die Symmetrieprüfung (Gegenrichtung muss den passenden
  inversen Typ tragen, nicht denselben).

**Empfehlung:** mit Option A (ungerichtet) beginnen — deckt den aktuellen Fall vollständig ab und ist
einfacher zu validieren; auf Option B nur wechseln, falls ein konkreter künftiger Anwendungsfall die
Richtung tatsächlich braucht (z. B. ein automatisierter Report „alle Retraction Notices ohne
zurückgezogene Ursprungspublikation").

## 3. Trennung zwischen bibliographischer und wissenschaftlicher Dublette — Entscheidungsleitfaden

Dieser Abschnitt konkretisiert Abschnitt 2.1 als praktischen Leitfaden für den menschlichen Reviewer, der
eine Identifikator-Kollision auflöst (Titel/Abstract-Screening-Vorstufe an Stufe `deduplication`):

1. **Sind Titel, Autoren und Publikationsdatum identisch (oder trivial variiert, z. B. Interpunktion)?**
   Ja → wahrscheinlich bibliographische Dublette → `decision: duplicate` prüfen.
2. **Trägt einer der Kandidaten einen erkennbar anderen strukturellen Publikationstyp** (siehe Abschnitt
   4 — z. B. einer ist `letter_or_comment`, der andere `reply_or_response`)? Ja → **niemals** `duplicate`,
   sondern `related_records` mit passendem `relationship_type`.
3. **Beziehen sich beide auf dieselbe Studie (gleicher NCT-Bezug, gleiche Sponsor-/Interventionsangaben),
   aber mit erkennbar unterschiedlichem Berichtszeitpunkt** (Zwischenergebnis vs. Endergebnis) oder
   unterschiedlicher Quelle (Registereintrag vs. Fachartikel)? Ja → `related_records` mit
   `interim_and_final_results` bzw. `registry_entry_and_publication`.
4. **Bleibt nach 1–3 Unsicherheit** (z. B. wirklich zwei identische PMIDs für dieselbe Einreichung, ohne
   erkennbaren inhaltlichen Unterschied)? Diese Unsicherheit selbst ist keine Lizenz, automatisch zu
   raten — der Reviewer dokumentiert seine Einschätzung mitsamt Begründung in `decision_reason`/
   `rationale`; bleibt echte Unsicherheit bestehen, ist `decision: uncertain` (Stufe `deduplication`
   unterstützt das bereits, siehe `ALLOWED_DECISIONS_BY_STAGE`) der korrekte, ehrliche Zwischenzustand —
   **kein** erzwungenes `duplicate` oder `related_records` nur um die Warnung verschwinden zu lassen.

**Wichtig:** dieser Leitfaden ersetzt keine menschliche Prüfung — er strukturiert sie. Kein Teil davon
wird für `system-screening-initializer` automatisiert (siehe ADR-0057, unverändert).

## 4. Erweiterung des Source-Type-Datenmodells für wissenschaftliche Publikationstypen

### 4.1 Problem

`common.schema.json#/$defs/source_type` (aktuell: `peer_reviewed_publication`, `preprint`,
`conference_abstract`, `trial_registry`, `regulatory_document`, `guideline`, `systematic_review`,
`reference_database`, `manufacturer_document`, `merchant_page`, `personal_report`, `other`) kann Letter,
Reply, Editorial, Corrigendum, Erratum, Retraction Notice und Expression-of-Concern-Notice nicht
unterscheiden — alle würden aktuell als `peer_reviewed_publication` oder `other` erfasst. Das ist der
Grund, warum `tools/initialize_screening_records.py` (ADR-0057) für alle drei kollidierenden PubMed-
Kandidaten identisch `peer_reviewed_publication` vergeben hat, obwohl PubMed selbst bereits strukturierte
Information trägt, die den Unterschied zeigt (siehe 4.3).

### 4.2 Entwurf: neue `source_type`-Werte (additiv)

| Neuer Wert | Bedeutung | Bezug zu bestehenden Abschnitten |
|---|---|---|
| `letter_or_comment` | Redaktioneller Leserbrief/Kommentar zu einer anderen Publikation. | — |
| `reply_or_response` | Autorenantwort auf einen Letter/Comment. | — |
| `editorial` | Redaktioneller Meinungsbeitrag, keine Primärforschung. | — |
| `case_report` | Klinischer Einzelfallbericht. | Bereits im Evidenzsystem als eigene Kategorie mit begrenztem Gewicht behandelt, aber schema-seitig bisher nicht als `source_type` unterscheidbar. |
| `corrigendum_or_erratum` | Die formale Korrekturmitteilung selbst (eigenes Dokument, eigene PMID/DOI) — **nicht** dasselbe wie `retraction_status: corrected` auf der ursprünglichen Quelle (Abschnitt 25 im Scientific Research Protocol). | Ergänzt Abschnitt 25. |
| `retraction_notice` | Die formale Rückzugsmitteilung selbst. | Ergänzt Abschnitt 25 (`retraction_status: retracted` bleibt auf der zurückgezogenen Quelle; die Mitteilung ist ein eigenes Dokument). |
| `expression_of_concern_notice` | Die formale „Expression of Concern"-Mitteilung selbst. | Ergänzt Abschnitt 25. |

Additiv, kein Schema-Versionsbump nötig (bestehende Werte/Daten bleiben unverändert gültig — dieselbe
Konvention wie bei jeder bisherigen additiven Schema-Erweiterung in diesem Projekt, z. B. ADR-0056).
Betrifft sowohl `schemas/common.schema.json#/$defs/source_type` (kanonische Quellen, `data/sources/**`)
als auch indirekt `research_screening_record.candidate_source_type` (Recherche-Ebene, verwendet
denselben `$ref`).

### 4.3 Entwurf: technische (nicht wissenschaftliche) Ableitung für PubMed-Kandidaten

PubMed führt für jede Publikation ein strukturiertes, von der NLM selbst vergebenes Feld
`publication_types` (bereits Teil von `candidates[].metadata.publication_types` seit ADR-0056). Dieses
Feld enthält bereits *heute*, unverändert in den echten Retatrutide-Candidate-Manifests, Werte wie
`Comment`, `Letter`, `Published Erratum`, `Retraction of Publication`, `Editorial`, `Case Reports`,
`Systematic Review` — von der NLM redaktionell vergeben, keine Ableitung durch dieses Projekt.

**Diese Zuordnung ist eine technische Übernahme fremder Strukturmetadaten, keine wissenschaftliche
Einordnung** — derselbe Grundsatz, der in ADR-0057 bereits `candidate_source_type` (ein Wert je
Datenbank) rechtfertigt, hier nur feinkörniger angewendet, weil das Quellenfeld selbst feinkörniger ist:

```python
# Entwurf, NICHT implementiert -- Prioritaetsreihenfolge, erster Treffer gewinnt
PUBMED_PUBLICATION_TYPE_TO_SOURCE_TYPE = [
    ("Retraction of Publication", "retraction_notice"),
    ("Published Erratum", "corrigendum_or_erratum"),
    ("Expression of Concern", "expression_of_concern_notice"),
    ("Comment", "letter_or_comment"),
    ("Letter", "letter_or_comment"),
    ("Editorial", "editorial"),
    ("Case Reports", "case_report"),
    ("Systematic Review", "systematic_review"),
    # kein Treffer -> peer_reviewed_publication (unveraendertes Verhalten aus ADR-0057)
]
```

**Ausdrücklich NICHT vorgeschlagen:** eine Ableitung für `reply_or_response` — PubMed markiert eine Reply
üblicherweise ebenfalls nur als `Comment`, nicht strukturell von einem ursprünglichen Letter
unterscheidbar. Die `letter_or_comment`-vs-`reply_or_response`-Unterscheidung (und ob zwei so
klassifizierte Kandidaten ein zusammengehöriges Paar sind) bleibt der `related_records`-Klassifikation
durch einen Menschen vorbehalten (Abschnitt 2), **nicht** dem automatischen Initialisierer.

**ClinicalTrials.gov bleibt unverändert** bei einem einzigen Wert (`trial_registry`) — CT.gov-Metadaten
enthalten kein vergleichbares Feld, das eine analoge Verfeinerung technisch (nicht wissenschaftlich)
rechtfertigen würde.

### 4.4 Auswirkung auf die drei realen Kollisions-Records

Würde diese Ableitung rückwirkend angewendet (nicht Teil dieses Architektur-PRs — reine Illustration),
hätte sie vermutlich mindestens PMID 37888927 ("... Reply.") korrekt von den beiden anderen
unterschieden, sofern dessen `publication_types` `Comment` enthält (noch nicht gegen die echten
NCBI-ESummary-Rohdaten verifiziert — das wäre ein technischer Prüfschritt für die Umsetzung, keine
wissenschaftliche Frage). Das hätte die Kollision nicht vollständig aufgelöst (`related_records` bliebe
weiterhin erforderlich, um die drei Datensätze explizit zu verknüpfen), aber dem menschlichen Reviewer
sofort einen strukturellen Hinweis gegeben, statt drei identisch aussehende
`peer_reviewed_publication`-Einträge vorzufinden.

## 5. Beziehungen zwischen PMID, DOI, PMCID und NCT-ID

### 5.1 Was jeder Identifikator tatsächlich verspricht

| Identifikator | Vergeben von | Referenziert | Kardinalität zu „einem Dokument" |
|---|---|---|---|
| **PMID** | NLM/PubMed | Eine indexierte Zitation. | Soll 1:1 sein, ist es in der Praxis fast immer — seltene Doppel-Indexierung ist ein bekanntes, aber nicht garantiert erkennbares PubMed-Artefakt (vermutlicher Fall: PMID 37888925/37888926). |
| **DOI** | Verlag/Crossref | Ein vom Verlag definiertes „Werk". | **Nicht zuverlässig 1:1.** Verlage vergeben gelegentlich dieselbe DOI für redaktionell zusammengehörige, aber inhaltlich getrennte Texte (typischer Fall: ein Correspondence-Letter + seine Reply unter gemeinsamer Online-Veröffentlichung — vermuteter Fall für `10.1056/NEJMc2310645`). |
| **PMCID** | NLM/PubMed Central | Eine frei verfügbare Volltextkopie. | Meist 1:1 mit einer PMID, wenn ein Volltext in PMC vorliegt; nicht jede PMID hat eine PMCID. |
| **NCT-ID** | ClinicalTrials.gov | Eine **Studienregistrierung**, keine Publikation. | 1:1 mit einer Studie (Registrierungsobjekt), aber **1:n mit Publikationen** — eine Studie sammelt über ihre Laufzeit typischerweise mehrere Publikationen (Zwischenergebnis, Endergebnis, Sicherheits-Update, Subgruppenanalysen), die alle auf dieselbe NCT-ID zurückgehen können, ohne dass sie sich gegenseitig als Dubletten betrachten. |

**Zentrale Erkenntnis dieses Entwurfs:** *Identifikator-Übereinstimmung ist ein Signal für eine mögliche
Beziehung — niemals ein Beweis für eine bestimmte Beziehungsart.* Das Vorgängersystem (Phase 4A,
`check_deduplication`) hat implizit angenommen, dass Identifikator-Gleichheit ⇔ dasselbe Dokument gilt —
korrekt für PMID/PMCID/ISBN/NCT-ID in der weit überwiegenden Mehrheit der Fälle, aber **nachweislich
falsch** für DOI bei Correspondence-Paaren. Dieser Entwurf korrigiert das nicht durch eine neue Regel „DOI
zählt nicht mehr" (das würde echte DOI-Dubletten übersehen), sondern durch die Trennung in Abschnitt 2:
jede Kollision — unabhängig vom auslösenden Feld — braucht eine menschliche Klassifikation, welche der
beiden Beziehungsarten tatsächlich vorliegt.

### 5.2 Die bereits bestehende kanonische Trennung als Zielbild

Diese Architektur ist **kein neues Konzept**, sondern die konsequente Fortführung einer bereits im
kanonischen Datenmodell etablierten Trennung (Abschnitte 13–16 im
[Scientific Research Protocol](Scientific_Research_Protocol.md), [Data Model](Data_Model.md)):

- `study.schema.json` trägt `registration.identifier` (die NCT-ID) und `source_ids[]` — **eine** Studie
  kann **mehrere** Quellen referenzieren.
- `source.schema.json` trägt `identifiers.{doi,pmid,pmcid,isbn}` (bewusst **ohne** `nct_id` — eine
  Quelle ist eine Publikation, keine Studienregistrierung) und **keine** direkte Rückreferenz auf die
  Studie; die Verknüpfung läuft ausschließlich über `study.source_ids[]`.
- Genau diese Trennung fehlt aktuell auf der Recherche-Ebene (`research/screening/**`): ein
  `screening_record` hat `candidate_identifiers` als flache, unverknüpfte Liste (`doi`, `pmid`, `pmcid`,
  `nct_id`, `isbn`, `url`) ohne jede Beziehung zwischen den Feldern.

`related_records[]` (Abschnitt 2) ist die **Vorstufe** dieser kanonischen Verknüpfung auf der
Recherche-Ebene — eine frühzeitig dokumentierte Beobachtung („dieser PubMed-Kandidat und dieser
ClinicalTrials.gov-Kandidat gehören wahrscheinlich zur selben Studie"), die bei der späteren, weiterhin
manuellen Anlage der kanonischen `study`/`source`-Objekte (Phase 4A: „dieser Schritt ist bewusst nicht
automatisiert") als Ausgangspunkt dient — **ohne** selbst schon eine kanonische Aussage zu sein, exakt
wie ein Candidate Manifest keine Screening-Entscheidung ist (ADR-0056) und ein Screening Record keine
kanonische Quelle ist (Abschnitt 12 im Scientific Research Protocol).

## 6. Modellierung von Letter, Reply, Editorial, Corrigendum und Mehrfachpublikationen

Vollständige, für dieses Dokument vorgeschlagene Werteliste für
`research/vocabularies/screening_relationship_types.yaml` /
`common.schema.json#/$defs/screening_relationship_type`:

| Wert | Bedeutung | Typischer Auslöser |
|---|---|---|
| `letter_and_reply` | Ein Letter/Comment und die dazugehörige Reply/Response. | Gemeinsame DOI, unterschiedliche PMID, einer der Titel endet auf „Reply"/"Response" (menschlich bestätigt, nicht automatisch erkannt). |
| `interim_and_final_results` | Zwischen- und Endergebnis derselben Studie. | Gemeinsamer Studienbezug (Sponsor/Intervention/Registrierung erkennbar identisch), unterschiedlicher Berichtszeitraum. |
| `subgroup_or_secondary_analysis` | Eine Subgruppen- oder Sekundäranalyse derselben Studie. | Wie oben, erkennbar eingeschränkte Population/Fragestellung. |
| `safety_update` | Ein späteres, sicherheitsfokussiertes Update derselben Studie. | Wie oben, Titel/Fokus erkennbar sicherheitsbezogen. |
| `preprint_and_published_version` | Ein Preprint und seine später formal publizierte Fassung. | `source_type: preprint`-Kandidat und ein späterer, inhaltlich übereinstimmender `peer_reviewed_publication`-Kandidat (Abschnitt 19 im Scientific Research Protocol). |
| `registry_entry_and_publication` | Ein ClinicalTrials.gov-Registereintrag und ein Fachartikel über dieselbe Studie. | `nct_id`-Kandidat und `pmid`-Kandidat mit erkennbar übereinstimmender Intervention/Sponsor/Studiendesign (Abschnitt 14 im Scientific Research Protocol). |
| `correction_or_erratum` | Eine Korrekturmitteilung (`source_type: corrigendum_or_erratum`) zu einem bereits erfassten Kandidaten. | Siehe Abschnitt 4, Abschnitt 25 im Scientific Research Protocol. |
| `expression_of_concern` | Eine Expression-of-Concern-Mitteilung zu einem bereits erfassten Kandidaten. | Siehe Abschnitt 4, Abschnitt 25. |
| `retraction_notice` | Eine Rückzugsmitteilung zu einem bereits erfassten Kandidaten. | Siehe Abschnitt 4, Abschnitt 25. |
| `editorial_comment` | Ein Editorial, das einen anderen Kandidaten redaktionell kommentiert (schwächere Beziehung als `letter_and_reply` — i. d. R. selbst kein direkter Evidenzbeitrag). | `source_type: editorial`. |
| `other` | Jede andere, im Freitext begründete Beziehung, die keiner der obigen Kategorien entspricht. | — |

**Bewusst nicht in dieser Liste:** eine Kategorie für „ist eine bibliographische Dublette" — das bleibt
strukturell `decision: duplicate`/`duplicate_of` (Abschnitt 2.1), nicht `related_records`. Eine
Vermischung beider Mechanismen in einem Feld würde exakt das Problem reproduzieren, das dieser Entwurf
beheben soll.

## 7. Zusammenfassung der Schema-Änderungen (Entwurf, nicht angewendet)

| Datei | Änderung | Additiv? |
|---|---|---|
| `schemas/research_screening_record.schema.json` | Neu: `workflow_state` (optional), `related_records[]` (optional, `default: []`) | Ja |
| `schemas/common.schema.json` | Neu: `$defs/screening_workflow_state`, `$defs/screening_relationship_type`; erweitert: `$defs/source_type` um 7 neue Werte (Abschnitt 4.2) | Ja |
| `research/vocabularies/screening_workflow_states.yaml` | Neu | — |
| `research/vocabularies/screening_relationship_types.yaml` | Neu | — |
| `tools/validate_research.py` | Neu: `check_screening_workflow_state_projection`, `check_screening_related_records`; angepasst: `check_screening_system_actor_invariants` (workflow_state statt screened_by), `check_deduplication` (workflow_state statt screened_by; `related_records`-Ausnahme) | — |
| `tools/initialize_screening_records.py` | Optional (separater Folge-Vorschlag, nicht Teil dieses PRs): feinere `candidate_source_type`-Ableitung aus `publication_types` (Abschnitt 4.3) | — |

**Kein Schema-Versionsbump** für `research_screening_record`/`common` nötig — alle Änderungen sind
additiv-optional, bestehende 197 reale Records sowie alle `research/examples/**`-Fixtures bleiben
unverändert gültig (keine Migration erforderlich, `workflow_state`/`related_records` können nachträglich
für bestehende Records berechnet bzw. leer gelassen werden).

## 8. Nicht-Ziele dieses Entwurfs

- **Keine rückwirkende Änderung** der 197 bestehenden Screening Records — dieser PR enthält ausschließlich
  Dokumentation.
- **Keine automatische Auflösung** der drei realen Kollisions-Records (PMID 37888925/37888926/37888927) —
  das bleibt explizit eine Aufgabe für einen menschlichen Reviewer in einer künftigen Phase, mit diesem
  Entwurf als Werkzeug, nicht als Abkürzung.
- **Keine Ableitung von `relationship_type` durch Automatisierung** — anders als `candidate_source_type`
  (Abschnitt 4.3, technische Metadatenübernahme) ist die Entscheidung, DASS zwei Kandidaten verwandt sind
  und WELCHE Beziehungsart vorliegt, immer eine menschliche Einordnung.
- **Keine Erweiterung von `duplicate_of`-Semantik** — bibliographische Dubletten funktionieren nach
  diesem Entwurf exakt wie heute.

## 9. Offene Fragen für den CSO

1. Ist die 3-Zustands-Workflow-Modellierung (`system_initialized`/`under_human_review`/`finalized`,
   Abschnitt 1.2) ausreichend, oder wird der zusätzliche `flagged_for_dedup_review`-Zustand (Abschnitt
   1.4) bereits jetzt benötigt?
2. Ungerichtete (`related_records`, Option A) oder gerichtete Beziehungstypen (Option B, Abschnitt 2.4)?
3. Ist die vorgeschlagene `source_type`-Erweiterung (Abschnitt 4.2, 7 neue Werte) vollständig, oder fehlen
   weitere Publikationstypen (z. B. `meta_analysis` getrennt von `systematic_review`)?
4. Soll die technische `publication_types`-Ableitung (Abschnitt 4.3) als eigenständiger, kleinerer
   Folge-PR vor der vollständigen `related_records`-Implementierung umgesetzt werden (schnellerer
   Nutzen, geringeres Risiko), oder gemeinsam?
5. Reicht die vorgeschlagene Symmetrie-Pflicht für `related_records` (Abschnitt 2.3), oder soll zusätzlich
   geprüft werden, dass alle Mitglieder einer Identifikator-Kollisionsgruppe **paarweise** klassifiziert
   sind (nicht nur teilweise)?
6. Freigabe, diesen Entwurf als Grundlage für die konkrete Implementierung in einer eigenständigen
   Phase-4B-1B-2-PR zu verwenden.

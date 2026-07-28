---
title: "Phase 4B-1B-2 – Deduplication & Workflow Architecture (Proposed, v2)"
description: Architektur-Entwurf (Revision 2 nach CSO-Review Runde 1) für ein berechnetes Workflow-State-Modell, eine vollständige Deduplizierungsarchitektur mit gerichteten, candidate-basierten Beziehungen und ein erweitertes Publikationstyp-Datenmodell. Reine Spezifikation, keine Implementierung.
tags:
  - Architektur
  - Projekt
  - Datenmodell
---

# Phase 4B-1B-2 – Deduplication & Workflow Architecture (Proposed, v2)

!!! warning "Status: Vorgeschlagen, nicht entschieden"
    Dieses Dokument ist ein **Architektur-Entwurf** (siehe ADR-0058 im [Decision Log](Decision_Log.md),
    Status „Vorgeschlagen"). Es enthält **keine Implementierung**: keine Schema-Änderungen, keine
    Validator-Änderungen, keine veränderten oder neuen Screening Records. Alle Codeblöcke in diesem
    Dokument sind Entwürfe zur Diskussion, keine bereits angewendeten Artefakte. Nichts hier schaltet
    eine wissenschaftliche Entscheidung frei oder trifft eine.

## Änderungsprotokoll gegenüber Version 1

Die CSO-Review-Runde 1 (2026-07-27) hat die Grundarchitektur freigegeben und sechs konkrete Änderungen
vor einem Merge verlangt. Diese Fassung (v2) setzt alle sechs um:

| # | Forderung | Umgesetzt in |
|---|---|---|
| 1 | `workflow_state` nicht als persistentes Schemafeld, sondern reine Projektion | Abschnitt 1 (vollständig neu) |
| 2 | Stabilere Referenz für `related_records` statt `screening_record_id` prüfen | Abschnitt 2.2 (candidate-basiert) |
| 3 | Source-Type-Vokabular um 12 genannte Kandidaten prüfen/erweitern | Abschnitt 4.2/4.3 (neu) |
| 4 | `relationship_type` auf gerichtete Beziehungen umstellen | Abschnitt 2.4/6 (neu) |
| 5 | Identifier-Grundsatz verschärfen, explizit auf DOI/PMID/PMCID/NCT/ISBN | Abschnitt 5.1 (erweitert) |
| 6 | Vollständige Kollisionsgruppen statt nur paarweiser Symmetrie | Abschnitt 2.5 (neu) |

## 0. Anlass und Ausgangslage

Phase 4B-1B-1 (PR [#6](https://github.com/PeptideAtlas/peptide-atlas/pull/6), gemerged, ADR-0057) hat bei
der Initialisierung der 197 realen Retatrutide-Screening-Records eine reale Datenkollision aufgedeckt: drei
PubMed-PMIDs (`37888925`, `37888926`, `37888927`) teilen sich dieselbe DOI `10.1056/NEJMc2310645` — ein
NEJM-Correspondence-Letter (evtl. doppelt indexiert) plus dessen separat indexierte Reply. Die damalige
Lösung (`check_deduplication`-Herabstufung zu einer Warnung, solange ein beteiligter Datensatz noch nicht
von einem Menschen übernommen wurde) war eine **explizite, aber bewusst provisorische** Nutzerentscheidung,
um die Initialisierung nicht zu blockieren.

Version 1 dieses Dokuments beantwortete die daraus folgende CSO-Rückfrage mit einem ersten Architektur-
Entwurf. Diese Version 2 setzt die sechs Änderungen aus der ersten CSO-Review-Runde um (siehe
Änderungsprotokoll oben). Die drei ursprünglich identifizierten strukturellen Probleme bleiben die
Grundlage:

1. **`screened_by`-basierte Validatorlogik ist eine Zweckentfremdung** — ADR-0057 nutzt
   `screened_by == system-screening-initializer` als Stellvertreter für einen Workflow-Zustand, redundant
   an zwei Stellen im Code hergeleitet.
2. **`decision: duplicate` ist strukturell überladen** — kennt nur „identisch, einer redundant", nicht
   „eigenständig, aber verwandt" (Letter+Reply).
3. **`candidate_source_type` ist zu grobkörnig**, um Letter/Reply/Editorial/Corrigendum zu erkennen,
   obwohl PubMed dafür bereits strukturierte Metadaten liefert.

## 1. Workflow-Zustand als reine, nicht gespeicherte Projektion

### 1.1 Problem (unverändert aus v1)

`tools/validate_research.py::check_screening_system_actor_invariants` und `check_deduplication`
(ADR-0057-Anpassung) leiten beide unabhängig voneinander denselben Sachverhalt her — „ist der aktuelle
effektive Bearbeiter noch der technische Systemakteur?" — durch einen String-Vergleich gegen
`SYSTEM_SCREENING_INITIALIZER_ACTOR`: duplizierte Herleitung, konzeptionelle Vermischung von
Akteursidentität und Workflow-Zustand, nicht erweiterbar.

### 1.2 Revision (v2): kein Schemafeld, ausschließlich ein berechneter Helfer

**CSO-Vorgabe:** `workflow_state` wird **nicht** als Feld in `research_screening_record` eingeführt.
Stattdessen: eine reine Python-Hilfsfunktion in `tools/_researchlib.py`, die bei Bedarf aus bereits
vorhandenen, validierten Daten berechnet — **niemals in eine YAML-Datei geschrieben**:

```python
# Entwurf, NICHT implementiert
def derive_workflow_state(screening_data: dict) -> str:
    """Berechnet den Bearbeitungszustand ausschliesslich aus decision_history (massgeblich) sowie
    den bereits validierten Top-Level-Projektionen decision/decision_stage (guenstige Abkuerzung fuer
    die 'finalized'-Bedingung -- decision/decision_stage sind selbst bereits eine vom Validator
    geprueft Projektion von decision_history[-1], also keine zweite Wahrheitsquelle, siehe ADR-0037).
    Kein Speicherort, kein Cache -- wird bei jedem Bedarf neu berechnet."""
    history = screening_data.get("decision_history") or []
    if len(history) == 1 and history[0].get("decided_by") == SYSTEM_SCREENING_INITIALIZER_ACTOR:
        return "system_initialized"
    if (
        screening_data.get("decision_stage") == "final"
        and screening_data.get("decision") in ("include", "exclude")
        and not _has_unresolved_review_conflict(screening_data)  # bereits vorhandene Hilfsfunktion
    ):
        return "finalized"
    return "under_human_review"
```

**Konsequenzen dieser Umstellung gegenüber v1:**

- **Kein neues Schemafeld**, kein neuer Eintrag in `additionalProperties`/`required` von
  `research_screening_record.schema.json`.
- **Keine neue kontrollierte Vokabular-Datei** (`research/vocabularies/screening_workflow_states.yaml`
  entfällt ersatzlos) — es gibt nichts Gespeichertes, das gegen ein Vokabular zu validieren wäre. Die drei
  konzeptuellen Zustandsnamen (`system_initialized`/`under_human_review`/`finalized`) leben ausschließlich
  als Rückgabewerte dieser einen Funktion, an einer einzigen Stelle im Code definiert.
- **`check_screening_workflow_state_projection` entfällt ersatzlos** (war in v1 vorgeschlagen) — es gibt
  nichts mehr, dessen Konsistenz mit einer gespeicherten Kopie geprüft werden müsste. Das eliminiert einen
  ganzen Validator sowie das ihm zugrunde liegende Risiko einer künftig auseinanderlaufenden zweiten
  Wahrheitsquelle vollständig, nicht nur in der Theorie.
- **Keine Migration** — folgt zwingend daraus, dass nichts gespeichert wird: es gibt für die 197
  bestehenden Records nichts nachzutragen oder zu berechnen und abzulegen.
- `check_screening_system_actor_invariants` und `check_deduplication` rufen beide
  `_researchlib.derive_workflow_state(data)` direkt auf, statt (wie in v1 vorgeschlagen) ein gespeichertes
  Feld zu vergleichen — die Vereinheitlichung der Herleitung an einer Stelle (Ziel von Abschnitt 1.1) wird
  dadurch **stärker** erreicht als in v1, nicht schwächer: v1 hätte zwei Prüfungen gegen ein drittes,
  gespeichertes Feld verglichen (drei Stellen); v2 hat zwei Aufrufer einer einzigen Funktion (zwei
  Stellen, keine gespeicherte Kopie).

### 1.3 Alle Zustände, Übergänge, Zuständigkeiten (unverändert in der Semantik, jetzt rein rechnerisch)

| Wert | Bedeutung | Berechnung |
|---|---|---|
| `system_initialized` | Noch nie von einem Menschen bearbeitet. | `len(decision_history) == 1` UND `decision_history[0].decided_by == system-screening-initializer`. |
| `under_human_review` | Mindestens ein Mensch hat übernommen, Entscheidung noch nicht terminal. | Weder `system_initialized` noch `finalized`. |
| `finalized` | Terminal, widerspruchsfrei abgeschlossen. | `decision_stage == final` UND `decision ∈ {include, exclude}` UND kein ungelöster Erst-/Zweitprüfungs-Widerspruch. |

**Erlaubte Übergänge** (aus der Berechnungsregel abgeleitet, gegen `check_decision_history`s
Stufen-Monotonie verifiziert — diese verbietet nur Rückwärtslauf der Stufe, kein Überspringen):
`system_initialized → under_human_review`, `system_initialized → finalized` (in einem Schritt möglich,
sofern der erste menschliche Eintrag bereits terminal ist), `under_human_review → finalized`,
`under_human_review → under_human_review`, `finalized → finalized`.

**Verbotene/unmögliche Übergänge:** jeder Rückschritt (`finalized`/`under_human_review` →
`system_initialized` ist unmöglich, da `len(decision_history) == 1` nach einem zweiten Eintrag nie wieder
gilt; `finalized` → `under_human_review` ist durch die Stufen-Monotonie sowie die Append-only-Konvention
faktisch ausgeschlossen); jeder Übergang, ausgelöst durch einen Eintrag mit
`decided_by == system-screening-initializer` nach der Initialerzeugung (durch die unveränderte erste
ADR-0057-Invariante strukturell verboten — ein solcher Eintrag kann nie `under_human_review`/`finalized`
erfüllen).

**Wer darf Übergänge auslösen:** ausschließlich menschliche Akteure, durch Anhängen eines neuen,
gültigen `decision_history`-Eintrags — wie zuvor, jetzt aber ohne dass irgendjemand (Mensch oder
Werkzeug) je ein `workflow_state`-Feld direkt schreibt, weil es keines gibt.

**Wer prüft was:** `check_screening_system_actor_invariants` ruft `derive_workflow_state()` auf, um die
zweite Invariante (canonical_source_id/candidate_title) auf `system_initialized`-Datensätze zu
beschränken. `check_deduplication` ruft dieselbe Funktion auf, um die Warnung-statt-Fehler-Herabstufung
zu entscheiden (siehe Abschnitt 2.5).

### 1.4 Offene Frage: vierter Zustand bleibt offen, jetzt ebenfalls nicht-persistent zu denken

Ein zusätzlicher Zwischenzustand `flagged_for_dedup_review` (Abschnitt 1.4 in v1) wäre unter demselben
Prinzip weiterhin **nicht** als gespeichertes Feld zu denken, sondern — falls überhaupt eingeführt —
ebenfalls als reine Berechnung (z. B. „ist dieser Datensatz Teil einer aktuell ungelösten
Kollisionsgruppe", direkt aus `check_deduplication`s eigener Kollisionslogik ableitbar, siehe
Abschnitt 2.5). Empfehlung unverändert: erst einführen, wenn ein konkretes Tooling-Bedürfnis das
rechtfertigt.

## 2. Vollständige Deduplizierungsarchitektur

### 2.1 Zwei fundamental verschiedene Beziehungen, eine falsch überladene (unverändert aus v1)

| | **Bibliographische Dublette** | **Studienverknüpfte, aber eigenständige Publikation** |
|---|---|---|
| **Definition** | Zwei Kandidaten beschreiben **exakt denselben Text**. | Zwei Kandidaten sind **unterschiedliche Texte** zur selben Studie/demselben Vorgang. |
| **Screening-Konsequenz** | Nur EINE Version bleibt aktiv; die andere ist `decision: duplicate`. | **Beide** bleiben unabhängig screenbar/extrahierbar. |
| **Bestehendes Feld** | `duplicate_of` (unverändert). | `related_records[]` (dieser Entwurf). |

**Kernregel unverändert:** `decision: duplicate`/`duplicate_of` bleibt ausschließlich für bibliographische
Dubletten reserviert.

### 2.2 Revision (v2): `related_records[]` referenziert Kandidaten, nicht Screening Records

**CSO-Vorgabe:** prüfen, ob eine langfristig stabilere Referenz als `screening_record_id` möglich ist.

**Ergebnis der Prüfung — ja, und zwar aus zwei unabhängigen Gründen:**

1. **Nachweisbar stärkere Stabilitätsgarantie.** `candidate_id` (zusammen mit `candidate_manifest_id`)
   ist seit ADR-0056 **technisch erzwungen unveränderlich**:
   `tools/check_research_immutability.py::CANDIDATE_ENTRY_IMMUTABLE_FIELDS = frozenset({"candidate_id",
   "primary_identifier", "discovered_in_search_run_ids"})` — jede Änderung dieser Felder nach dem Merge
   wird von der CI blockiert. Für `research_screening_record.id` (das Feld, das `screening_record_id` in
   v1 referenziert hätte) existiert **keine vergleichbare, technisch geprüfte Garantie** — im Gegenteil
   dokumentiert `research/screening/README.md` ausdrücklich, dass sogar `decision_history[]` innerhalb
   derselben Datei nur redaktionell, nicht technisch vor Änderung geschützt ist. `candidate_id` ist damit
   objektiv die stärker abgesicherte Identität im gesamten Recherche-Datenmodell.
2. **Semantisch korrekter.** Eine `related_records`-Beziehung ist eine Aussage über zwei **Dokumente**
   (Letter und Reply sind zwei Publikationen), nicht über ihre jeweiligen Screening-Workflow-Wrapper. Der
   Kandidat (`candidate_id`) repräsentiert die Discovery-Identität des Dokuments (ADR-0056); der Screening
   Record ist die redaktionelle Bearbeitungshülle darum. Eine künftige Umstrukturierung der
   Screening-Infrastruktur (z. B. eine Zusammenlegung mehrerer Screening-Record-Dateien) würde
   candidate-basierte Beziehungen unberührt lassen, `screening_record_id`-basierte Beziehungen dagegen
   nicht.

**Revidiertes Feld:**

```yaml
related_records:
  - related_candidate_manifest_id: candidate-manifest-73f50257-b982-47cc-a1df-0f8f5fd31353
    related_candidate_id: research-candidate-7c900398-fab9-4366-aa4f-22e64aa756da
    relationship_type: has_reply   # gerichtet, siehe Abschnitt 2.4
    rationale: >
      Antwort (Reply) auf diesen Letter -- teilt DOI 10.1056/NEJMc2310645, aber eigener
      Titel und eigene PMID, kein redundanter Text.
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
      "related_candidate_manifest_id": {
        "type": "string",
        "pattern": "^candidate-manifest-[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}$"
      },
      "related_candidate_id": {
        "type": "string",
        "pattern": "^research-candidate-[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}$"
      },
      "relationship_type": { "$ref": "common.schema.json#/$defs/screening_relationship_type" },
      "rationale": { "type": "string", "minLength": 1 },
      "identified_by": { "$ref": "common.schema.json#/$defs/research_actor_id" },
      "identified_at": { "$ref": "common.schema.json#/$defs/date" }
    },
    "additionalProperties": false,
    "required": [
      "related_candidate_manifest_id", "related_candidate_id", "relationship_type",
      "rationale", "identified_by", "identified_at"
    ]
  }
}
```

**Warum beide Felder (`related_candidate_manifest_id` UND `related_candidate_id`), obwohl `candidate_id`
allein bereits projektweit eindeutig ist** (ADR-0056: „projektweite Eindeutigkeit von candidate_id"):
Konsistenz mit dem bereits bestehenden Muster auf `research_screening_record` selbst
(`candidate_manifest_id`/`candidate_id` werden dort ebenfalls immer als Paar geführt, nie `candidate_id`
allein) — kein neues, abweichendes Referenzmuster im selben Schema, plus ein direkter
Nachschlage-Pfad ohne projektweite Suche.

**Bewusste Einschränkung:** `related_records` ist dadurch nur für Screening Records nutzbar, deren
zugrunde liegender Kandidat über eine aufgelöste Kandidatenreferenz verfügt — also für alle Protokolle,
die (wie Retatrutide) bereits mindestens ein Candidate Manifest haben, für die die Referenz laut
ADR-0056/CSO-Nachtrag ohnehin verpflichtend ist. Für migrationskompatible ältere Protokolle ohne jedes
Candidate Manifest bleibt `related_records` schlicht ungenutzt — akzeptierte, dokumentierte Grenze, keine
funktionale Lücke für den tatsächlich betroffenen Fall (Retatrutide).

### 2.3 Referenzielle Prüfung (Entwurf, revidiert)

**`check_screening_related_records`** (neu) — referenziert jetzt gegen Candidate Manifests statt gegen
Screening Records:
- Ziel existiert als `candidate` innerhalb eines `research_candidate_manifest` mit
  `related_candidate_manifest_id`, gleiches `protocol_id` wie der referenzierende Screening Record.
- Kein Selbstverweis (Ziel-Kandidat ≠ eigener `candidate_id`/`candidate_manifest_id`).
- `identified_by` darf nicht `system-screening-initializer` sein.
- **Vorteil der candidate-basierten Referenz:** die Zielprüfung ist unabhängig davon möglich, ob für den
  Ziel-Kandidaten bereits ein Screening Record existiert — eine Beziehung kann dokumentiert werden, sobald
  beide Kandidaten im Candidate Manifest bekannt sind, unabhängig von der Reihenfolge, in der ihre
  Screening Records angelegt werden.

### 2.4 Revision (v2): gerichtete Beziehungstypen

**CSO-Vorgabe:** von ungerichteten (`letter_and_reply`) auf gerichtete Typen umstellen, analog
`reply_to`/`has_reply`, `corrects`/`corrected_by`, `retracts`/`retracted_by`, `updates`/`updated_by`.

**Umgesetzt als kleines, wiederverwendbares Set gerichteter Primitive** statt eines bespoken Paars je
Einzelkonzept (letzteres hätte die in v1 unter „Option B" befürchtete Vokabular-Verdopplung auf 22 Werte
bedeutet). Stattdessen: semantisch verwandte v1-Konzepte (Zwischen-/Endergebnis, Subgruppenanalyse,
Sicherheits-Update) werden unter dem generischen, von der CSO selbst vorgeschlagenen Paar
`updates`/`updated_by` zusammengefasst — die spezifische Nuance (welche Art von Update) bleibt im
ohnehin verpflichtenden Freitext `rationale` erhalten (dieselbe Begründung, die v1 bereits für die
Pflicht-Freitextigkeit von `rationale` gab: die Typen sind grobkörniger als jede reale Konstellation).

Vollständige Tabelle in Abschnitt 6. Kern-Validatorlogik:

```python
# Entwurf, NICHT implementiert
RELATIONSHIP_TYPE_INVERSE = {
    "replies_to": "has_reply", "has_reply": "replies_to",
    "updates": "updated_by", "updated_by": "updates",
    "is_preprint_of": "has_published_version", "has_published_version": "is_preprint_of",
    "reports_on_registered_study": "has_publication", "has_publication": "reports_on_registered_study",
    "corrects": "corrected_by", "corrected_by": "corrects",
    "retracts": "retracted_by", "retracted_by": "retracts",
    "raises_concern_about": "has_expression_of_concern",
    "has_expression_of_concern": "raises_concern_about",
    "comments_on": "has_editorial_comment", "has_editorial_comment": "comments_on",
    "other_related_to": "other_related_to",  # einzige Ausnahme: bewusst selbstinvers
}
```

`check_screening_related_records` prüft: verweist Kandidat A (via seinem Screening Record) auf Kandidat B
mit Typ `T`, muss — sobald ein Screening Record für B existiert — dieser einen Eintrag tragen, der auf A
mit Typ `RELATIONSHIP_TYPE_INVERSE[T]` verweist. Ein Eintrag, dessen Gegenrichtung stattdessen wieder `T`
selbst trägt (statt der Inversen), ist ein Fehler — das verhindert z. B. den widersprüchlichen Zustand
„A korrigiert B **und** B korrigiert A". Existiert für B noch kein Screening Record, ist das (noch) kein
Fehler, sondern eine Warnung „Gegenrichtung noch nicht dokumentiert, sobald der Ziel-Datensatz angelegt
wird" — siehe Abschnitt 2.3, letzter Punkt.

### 2.5 Revision (v2): vollständige Kollisionsgruppen statt nur paarweiser Symmetrie

**CSO-Vorgabe:** Kollisionsgruppen mit mehr als zwei Mitgliedern (wie die realen drei DOI-Records) sollen
vollständig, nicht nur paarweise geprüft werden.

**Entwurf: Zusammenhangskomponenten-Prüfung (Graph-Konnektivität) statt vollständiger paarweiser
Klassifikation.** Eine vollständige paarweise Anforderung (jedes Paar der Gruppe muss direkt klassifiziert
sein) würde bei einer Gruppe der Größe n bereits `n·(n-1)/2` Einzelklassifikationen verlangen — bei den
drei realen Records wären das 3 Paare, real oft mehr, und bei größeren Correspondence-Ketten (Letter →
Reply → zweite Reply → ...) wüchse das quadratisch. Stattdessen: für jede Identifikator-Kollisionsgruppe
`G = {r1, ..., rn}` (Datensätze mit gemeinsamem normalisiertem Identifikator, wie bisher von
`check_deduplication` ermittelt) wird ein ungerichteter Graph gebildet — Knoten: die Datensätze in `G`;
Kanten: `duplicate_of`-Beziehungen sowie `related_records`-Beziehungen zwischen zwei Mitgliedern von `G`
(Richtung wird für die reine Konnektivitätsprüfung ignoriert, sie ist bereits durch Abschnitt 2.4
gesondert geprüft). **Die Kollisionsgruppe gilt als vollständig erklärt, wenn dieser Graph aus genau einer
Zusammenhangskomponente besteht** — jedes Mitglied muss von jedem anderen Mitglied aus über mindestens
einen (nicht notwendig direkten) Pfad erklärender Beziehungen erreichbar sein.

**Beispiel mit den drei realen Datensätzen:** wird `37888926` als `decision: duplicate` mit
`duplicate_of: 37888925` markiert (Kante 925↔926), und trägt `37888927` eine `replies_to`-Beziehung zu
`37888925` **oder** zu `37888926` (Kante 926↔927 oder 925↔927), ist die gesamte Dreiergruppe bereits eine
einzige Zusammenhangskomponente — **ohne** dass zusätzlich eine direkte Beziehung zwischen `37888925` und
`37888927` dokumentiert werden müsste (sie ist transitiv über `37888926` erklärt). Das vermeidet
redundante Doppel-Dokumentation derselben Information.

**Implementierung:** Union-Find (Disjoint-Set-Union) über die Mitglieder jeder Kollisionsgruppe — nahezu
lineare Laufzeit (`O(n·α(n))`), keine quadratische Explosion, skaliert auf beliebig große Korpora (heute
197 Datensätze, potenziell tausende in künftigen Phasen).

```python
# Entwurf, NICHT implementiert -- Kernidee, kein vollstaendiger Code
def collision_group_is_resolved(group: list[ResearchObject]) -> bool:
    parent = {obj.id: obj.id for obj in group}
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    def union(a, b):
        parent[find(a)] = find(b)

    ids_in_group = {obj.id for obj in group}
    for obj in group:
        if obj.data.get("duplicate_of") in ids_in_group:
            union(obj.id, obj.data["duplicate_of"])
        for rel in obj.data.get("related_records") or []:
            target_id = _resolve_candidate_to_screening_record_id(rel)  # falls vorhanden
            if target_id in ids_in_group:
                union(obj.id, target_id)

    roots = {find(obj.id) for obj in group}
    return len(roots) == 1
```

**Angepasste `check_deduplication`-Regel:** eine Kollisionsgruppe, deren Graph **eine einzige**
Zusammenhangskomponente bildet, löst weder Fehler noch Warnung aus. Eine Gruppe mit **mehr als einer**
Komponente (d. h. mindestens ein Mitglied ist über keinen Pfad mit mindestens einem anderen Mitglied
verbunden) bleibt Warnung, solange mindestens ein Mitglied `system_initialized` ist (Abschnitt 1), und
wird zum Fehler, sobald kein Mitglied mehr `system_initialized` ist — die Fehlermeldung benennt die
getrennten Komponenten explizit (z. B. „37888927 ist nicht mit {37888925, 37888926} verbunden"), damit der
Reviewer sofort sieht, welche Verbindung fehlt.

**Alternative, strengere Option (nicht empfohlen, aber dokumentiert):** vollständige paarweise
Klassifikation aller `n·(n-1)/2` Paare — höhere Sicherheit gegen implizite/versehentliche
Transitivitätsannahmen, aber quadratischer Dokumentationsaufwand ohne zusätzlichen Erkenntnisgewinn in den
bisher beobachteten Fällen. Empfehlung bleibt die Zusammenhangskomponenten-Prüfung.

## 3. Trennung zwischen bibliographischer und wissenschaftlicher Dublette — Entscheidungsleitfaden

(unverändert aus v1, Beziehungstyp-Namen an Abschnitt 6 angepasst)

1. **Sind Titel, Autoren und Publikationsdatum identisch (oder trivial variiert)?** Ja → wahrscheinlich
   bibliographische Dublette → `decision: duplicate` prüfen.
2. **Trägt einer der Kandidaten einen erkennbar anderen strukturellen Publikationstyp** (Abschnitt 4)? Ja
   → **niemals** `duplicate`, sondern `related_records` mit passendem, gerichtetem `relationship_type`
   (z. B. `replies_to` vom Reply-Kandidaten aus).
3. **Beziehen sich beide auf dieselbe Studie, aber mit unterschiedlichem Berichtszeitpunkt oder
   unterschiedlicher Quelle?** Ja → `related_records` mit `updates`/`updated_by` bzw.
   `reports_on_registered_study`/`has_publication`.
4. **Bleibt Unsicherheit?** Kein erzwungenes `duplicate`/`related_records` — `decision: uncertain`
   (Stufe `deduplication`) ist der korrekte, ehrliche Zwischenzustand.

**Wichtig:** dieser Leitfaden ersetzt keine menschliche Prüfung — er strukturiert sie. Kein Teil davon
wird für `system-screening-initializer` automatisiert.

## 4. Erweiterung des Source-Type-Datenmodells für wissenschaftliche Publikationstypen

### 4.1 Problem (unverändert aus v1)

`common.schema.json#/$defs/source_type` kann Letter, Reply, Editorial, Corrigendum, Erratum, Retraction
Notice und Expression-of-Concern-Notice nicht unterscheiden.

### 4.2 Ursprünglich vorgeschlagene sieben Werte (aus v1, unverändert)

| Wert | Bedeutung | Automatisierbar |
|---|---|---|
| `letter_or_comment` | Redaktioneller Leserbrief/Kommentar. | Ja — `Comment`/`Letter` |
| `reply_or_response` | Autorenantwort auf einen Letter/Comment. | Nein — siehe 4.4 |
| `editorial` | Redaktioneller Meinungsbeitrag. | Ja — `Editorial` |
| `case_report` | Klinischer Einzelfallbericht. | Ja — `Case Reports` |
| `corrigendum_or_erratum` | Formale Korrekturmitteilung. | Ja — `Published Erratum` |
| `retraction_notice` | Formale Rückzugsmitteilung. | Ja — `Retraction of Publication` |
| `expression_of_concern_notice` | Formale EoC-Mitteilung. | Ja — `Expression of Concern` |

### 4.3 Revision (v2): zwölf zusätzlich geprüfte Kandidaten

**CSO-Vorgabe:** mindestens folgende zwölf Werte prüfen. Vollständige Prüfung je Wert:

| Wert | Definition | Ableitbar? | Begründung |
|---|---|---|---|
| `meta_analysis` | Quantitative statistische Zusammenführung der Ergebnisse mehrerer Einzelstudien zu einer gepoolten Effektschätzung. | **Ja** — PubMed führt `Meta-Analysis` als eigenen, von `Systematic Review` strukturell getrennten Publication-Type-Wert. | Beide Methodiken sind fachlich unterscheidbar (eine systematische Übersicht muss keine quantitative Metaanalyse enthalten und umgekehrt); da `systematic_review` bereits im Vokabular existiert, schließt ein eigener Wert eine Lücke. **Offene Unterfrage:** Prioritätsreihenfolge, falls ein Artikel beide Tags trägt (Vorschlag Abschnitt 4.5: `Meta-Analysis` vor `Systematic Review`) — CSO-Bestätigung ausstehend. |
| `narrative_review` | Nicht-systematische, erzählende Literaturübersicht ohne vordefinierte, reproduzierbare Suchmethodik. | **Eingeschränkt** — kein eigenes PubMed-Tag; Ableitung nur als Ausschlussregel möglich: `publication_types` enthält `Review`, aber weder `Systematic Review` noch `Meta-Analysis`. | Rein mechanische Ausschlussregel (keine inhaltliche Bewertung), aber schwächer abgesichert als eine direkte Tag-Übernahme — vor Umsetzung stichprobenartig gegen echte PubMed-Daten zu verifizieren, nicht als sicheres Faktum zu behandeln. |
| `scoping_review` | Strukturierte Kartierung eines Forschungsfeldes (Umfang, Art, Lücken) ohne notwendige methodische Strenge einer systematischen Übersicht. | **Nein** — kein bekannter eigener PubMed-Publication-Type; Erkennung würde Titel-/Freitextanalyse erfordern (vom Projekt bewusst vermieden, keine Freitexterkennung). | Ausschließlich menschlich vergeben. |
| `umbrella_review` | Übersicht, die mehrere bereits vorhandene systematische Übersichten/Metaanalysen selbst zusammenfasst. | **Nein** — kein eigener PubMed-Publication-Type. | Ausschließlich menschlich vergeben. |
| `living_systematic_review` | Systematische Übersicht, die kontinuierlich mit neuer Evidenz aktualisiert statt einmalig veröffentlicht wird. | **Nein als eigener Typ** — PubMed unterscheidet das strukturell nicht von `Systematic Review`. | Vorschlag: technisch weiter als `systematic_review` klassifizieren; der „living"-Charakter (falls überhaupt benötigt) gehört in ein separates, hier nicht vorgeschlagenes Feld statt in `source_type`. **Offene Frage:** wird dieser Wert überhaupt eigenständig benötigt? |
| `practice_guideline` | Formale, evidenzbasierte klinische Praxisleitlinie einer Fachgesellschaft/Behörde. | **Ja** — PubMed führt `Practice Guideline` als offiziellen Publication-Type. | Direkte technische Übernahme. **Offene Unterfrage:** das Vokabular enthält bereits `guideline` — Verhältnis zu `practice_guideline` (Ersatz, Ergänzung, Präzisierung?) muss der CSO klären, siehe Abschnitt 4.5. |
| `consensus_statement` | Formale Konsenserklärung einer Expertengruppe, oft nach strukturiertem Konsensverfahren. | **Unsicher** — PubMed führte historisch `Consensus Development Conference`/`Consensus Development Conference, NIH`; ob ein generisches, zuverlässig unterscheidbares „Consensus Statement"-Tag heute durchgängig existiert, ist mir nicht mit Sicherheit bekannt. | **Nicht als Faktum behauptet** — vor Umsetzung gegen die aktuelle offizielle NLM-Publication-Type-Liste zu verifizieren (technischer Prüfschritt). Bis dahin: menschlich. |
| `technical_report` | Technischer Bericht (Behörden-/Institutsbericht), keine klassische Zeitschriftenpublikation. | **Unsicher** — `Technical Report` existiert als älterer PubMed-Publication-Type für bestimmte NLM-katalogisierte Inhalte; heutige Abdeckung für die in diesem Projekt genutzten Datenbanken nicht verifiziert. | Bis Verifikation: menschlich. |
| `consensus_statement`/`technical_report` gemeinsame Einschränkung | — | — | Beide Werte werden hier bewusst mit unsicherem Status gemeldet, statt fälschlich als sicher automatisierbar dargestellt zu werden — entspricht der projektweiten Regel, keine unverifizierten Fakten zu behaupten. |
| `white_paper` | Positionsbeziehendes Diskussionspapier einer Organisation, meist außerhalb des Peer-Review-Prozesses. | **Nein** — kein PubMed-Publication-Type; White Papers sind i. d. R. ohnehin keine PubMed-indexierten Quellen (Grauliteratur). | Ausschließlich menschlich, primär relevant für eine künftige, hier nicht im Scope befindliche dritte Datenbank/Quelle außerhalb PubMed/ClinicalTrials.gov. |
| `dataset` | Eigenständiger, zitierfähiger Forschungsdatensatz, keine Publikation im engeren Sinn. | **Unsicher** — neuere PubMed-Einträge können `Dataset` als Publication Type führen (Data-Descriptor-Einträge); Zuverlässigkeit über die genutzte NCBI-ESummary-Schnittstelle nicht verifiziert. | Bis Verifikation: menschlich. |
| `software` | Zitierfähige Forschungssoftware/ein Code-Repository. | **Nein** — kein PubMed-Publication-Type; Software-Zitationen laufen typischerweise über andere Register (Zenodo, GitHub-DOIs), nicht über PubMed. | Ausschließlich menschlich, aktuell außerhalb des Datenbank-Scopes dieses Projekts. |
| `protocol_paper` | Publikation, die ausschließlich das geplante Studienprotokoll (Design, Methodik) vor Ergebnisvorliegen beschreibt. | **Nein (nicht zuverlässig)** — vereinzelt `Clinical Trial Protocol` als älterer, inkonsistent genutzter Tag; zuverlässigste Erkennung wäre über Titelmuster („study protocol"), was das Projekt bewusst vermeidet. | Ausschließlich menschlich vergeben. |

**Zusammenfassung Automatisierbarkeit der 12 geprüften Werte:** 2 sicher automatisierbar (`meta_analysis`,
`practice_guideline`), 1 eingeschränkt/mit Vorbehalt automatisierbar (`narrative_review`), 3 mit
unsicherem, vor Umsetzung zu verifizierendem Status (`consensus_statement`, `technical_report`,
`dataset`), 6 ausschließlich menschlich (`scoping_review`, `umbrella_review`,
`living_systematic_review`, `white_paper`, `software`, `protocol_paper`).

### 4.4 `reply_or_response` — unverändert nicht automatisierbar (aus v1)

PubMed markiert eine Reply üblicherweise ebenfalls nur als `Comment`, nicht strukturell vom
ursprünglichen Letter unterscheidbar. Bleibt ausschließlich menschlicher `related_records`-Klassifikation
vorbehalten (jetzt: `replies_to`/`has_reply`, siehe Abschnitt 6).

### 4.5 Revidierte technische Ableitungsreihenfolge (Entwurf, NICHT implementiert)

```python
PUBMED_PUBLICATION_TYPE_TO_SOURCE_TYPE = [
    ("Retraction of Publication", "retraction_notice"),
    ("Published Erratum", "corrigendum_or_erratum"),
    ("Expression of Concern", "expression_of_concern_notice"),
    ("Comment", "letter_or_comment"),
    ("Letter", "letter_or_comment"),
    ("Practice Guideline", "practice_guideline"),          # neu, offene Unterfrage zu "guideline"
    ("Meta-Analysis", "meta_analysis"),                     # neu, Prioritaet vor Systematic Review
    ("Systematic Review", "systematic_review"),
    ("Editorial", "editorial"),
    ("Case Reports", "case_report"),
    ("Review", "narrative_review"),                         # neu, nur als Ausschlussregel (s.o.)
    # kein Treffer -> peer_reviewed_publication
]
```

`consensus_statement`, `technical_report`, `dataset` bewusst **nicht** in dieser Liste, bis ihre
Ableitbarkeit technisch verifiziert ist (siehe 4.3).

## 5. Beziehungen zwischen PMID, DOI, PMCID, NCT-ID und ISBN

### 5.1 Verschärfter Grundsatz (CSO-Vorgabe)

> **Kein bibliographischer Identifier beweist allein eine wissenschaftliche Beziehung.**

Dieser Grundsatz gilt ausdrücklich und ausnahmslos für **DOI, PMID, PMCID, NCT-ID und ISBN** — jeder
dieser fünf Identifikatoren liefert höchstens ein *Signal* für eine mögliche Beziehung zwischen zwei
Kandidaten, nie einen Beweis für deren genaue Art (bibliographische Dublette vs. eigenständige, verwandte
Publikation). Die Klassifikation der tatsächlichen Beziehung bleibt in jedem Fall menschlich (Abschnitt 3).

### 5.2 Kardinalitätstabelle (erweitert um ISBN)

| Identifikator | Vergeben von | Referenziert | Kardinalität zu „einem Dokument" |
|---|---|---|---|
| **PMID** | NLM/PubMed | Eine indexierte Zitation. | Soll 1:1 sein, ist es in der Praxis fast immer — seltene Doppel-Indexierung ist ein bekanntes, aber nicht garantiert erkennbares Artefakt. |
| **DOI** | Verlag/Crossref | Ein vom Verlag definiertes „Werk". | **Nicht zuverlässig 1:1** — gemeinsame DOI für redaktionell zusammengehörige, aber inhaltlich getrennte Texte (Correspondence-Paare) kommt vor. |
| **PMCID** | NLM/PubMed Central | Eine frei verfügbare Volltextkopie. | Meist 1:1 mit einer PMID, wenn Volltext in PMC vorliegt. |
| **NCT-ID** | ClinicalTrials.gov | Eine **Studienregistrierung**, keine Publikation. | 1:1 mit einer Studie, aber **1:n mit Publikationen**. |
| **ISBN** | Internationale ISBN-Agentur/Verlag | Eine bestimmte Ausgabe/Auflage/Format eines Buches. | **Nicht zuverlässig 1:1 mit „einem Werk"** — verschiedene Auflagen und Formate (Hardcover/Softcover/E-Book) desselben inhaltlichen Werks erhalten jeweils **eigene** ISBNs; umgekehrt ist eine einzelne ISBN eindeutig genau einer Ausgabe zugeordnet. Strukturell derselbe Unzuverlässigkeitstyp wie DOI: Identität auf Werksebene ⇏ Identität auf Identifikatorebene. |

### 5.3 Was aus jedem Identifikator NICHT geschlossen werden darf

| Identifikator | Unzulässige Schlussfolgerung |
|---|---|
| **PMID** | Aus zwei unterschiedlichen PMIDs automatisch „zwei unabhängige, unverwandte Dokumente" zu schließen, ohne übrige Identifikatoren/Metadaten zu prüfen. |
| **DOI** | Gleiche DOI automatisch als Beweis für „identisches Dokument" zu werten (der Fehler, der die reale Kollision verursachte) — ebenso unzulässig: DOI-Gleichheit pauschal zu ignorieren. |
| **PMCID** | Aus dem Fehlen einer PMCID zu schließen, ein Dokument sei kein Volltext-zugänglicher Artikel — reines technisches Hosting-Merkmal. |
| **NCT-ID** | Eine NCT-ID als Ersatz-Identität für „Studie = Publikation X" zu behandeln — Studie und Publikation bleiben strukturell getrennte Objekte (Abschnitt 13 im Scientific Research Protocol). |
| **ISBN** | Unterschiedliche ISBNs automatisch als „unterschiedliche Werke" zu werten (verschiedene Auflagen/Formate desselben Werks) — ebenso unzulässig: gleiche ISBN mit „exakt derselbe Bezug in jedem Kontext" gleichzusetzen, ohne die Ausgabe/Auflage zu prüfen. |

### 5.4 Die bereits bestehende kanonische Trennung als Zielbild (unverändert aus v1)

`study.schema.json` trägt `registration.identifier` (NCT-ID) und `source_ids[]`; `source.schema.json`
trägt `identifiers.{doi,pmid,pmcid,isbn}` (bewusst ohne `nct_id`) ohne Rückreferenz auf die Studie.
`related_records[]` (Abschnitt 2) ist die Vorstufe dieser kanonischen Verknüpfung auf der Recherche-Ebene
— keine kanonische Aussage, analog zu Candidate Manifest (ADR-0056).

## 6. Beziehungstaxonomie (gerichtet, Revision v2)

**CSO-Vorgabe:** von ungerichteten auf gerichtete Beziehungstypen umstellen.

| Konzept | Gerichtetes Paar (A → B / B → A) | Beschreibung | Beispiel |
|---|---|---|---|
| Letter + Reply | `replies_to` / `has_reply` | A antwortet auf B. | PMID 37888927 `replies_to` PMID 37888925/26; diese(r) `has_reply` 37888927. |
| Zwischen-/Endergebnis, Subgruppenanalyse, Sicherheits-Update | `updates` / `updated_by` | A aktualisiert/erweitert B mit neuen oder anderen Daten zu derselben Studie (spezifische Art der Aktualisierung in `rationale`). | Illustrativ: eine Sicherheits-Update-Publikation `updates` die ursprüngliche Wirksamkeitspublikation. |
| Preprint + publizierte Fassung | `is_preprint_of` / `has_published_version` | A ist die Preprint-Fassung von B. | Illustrativ: ein `source_type: preprint`-Kandidat `is_preprint_of` die spätere Zeitschriftenversion. |
| Registereintrag + Publikation | `reports_on_registered_study` / `has_publication` | A (Publikation) berichtet über die in B (Registereintrag) registrierte Studie. | Ein PubMed-Kandidat `reports_on_registered_study` einen CT.gov-Kandidaten. |
| Korrektur/Erratum | `corrects` / `corrected_by` | A korrigiert B. | Ein `corrigendum_or_erratum`-Kandidat `corrects` die Originalpublikation. |
| Retraction | `retracts` / `retracted_by` | A zieht B zurück. | Ein `retraction_notice`-Kandidat `retracts` die zurückgezogene Publikation. |
| Expression of Concern | `raises_concern_about` / `has_expression_of_concern` | A äußert Bedenken zu B. | Ein `expression_of_concern_notice`-Kandidat `raises_concern_about` die betroffene Publikation. |
| Editorial-Kommentar | `comments_on` / `has_editorial_comment` | A kommentiert redaktionell B. | Ein `editorial`-Kandidat `comments_on` die besprochene Publikation. |
| Alles Übrige | `other_related_to` / `other_related_to` | Einzige bewusst **symmetrische** Ausnahme — jede andere, freitextbegründete Beziehung. | — |

**Begründung der Konsolidierung:** statt eines bespoken gerichteten Paares je der ursprünglich elf
Einzelkonzepte aus v1 (was 22 Werte ergäbe) werden inhaltlich verwandte Konzepte (Zwischen-/Endergebnis,
Subgruppenanalyse, Sicherheits-Update) unter dem generischen, von der CSO selbst als Beispiel genannten
Paar `updates`/`updated_by` gebündelt — 9 Konzeptpaare, 17 Werte insgesamt (16 gerichtete + 1
selbstinverser Ausnahmewert). Die dadurch verlorene Feinunterscheidung wird durch das ohnehin
verpflichtende Freitextfeld `rationale` aufgefangen.

**`check_screening_related_records`-Symmetrieprüfung:** siehe Kernlogik in Abschnitt 2.4 — Gegenrichtung
muss exakt den in `RELATIONSHIP_TYPE_INVERSE` hinterlegten inversen Typ tragen, nicht denselben Typ
(außer bei `other_related_to`).

## 7. Zusammenfassung der Schema-Änderungen (Entwurf, nicht angewendet, Revision v2)

| Datei | Änderung | Additiv? |
|---|---|---|
| `schemas/research_screening_record.schema.json` | Neu: `related_records[]` (optional, `default: []`, referenziert Kandidaten). **Kein** `workflow_state`-Feld (v2-Änderung — entfällt gegenüber v1). | Ja |
| `schemas/common.schema.json` | Neu: `$defs/screening_relationship_type` (17 gerichtete/symmetrische Werte, Abschnitt 6); erweitert: `$defs/source_type` um bis zu 19 neue Werte (7 aus v1 + bis zu 12 aus Abschnitt 4.3, abhängig von CSO-Entscheidung zu den unsicheren/offenen Werten). **Kein** `$defs/screening_workflow_state` (v2-Änderung — entfällt). | Ja |
| `research/vocabularies/screening_relationship_types.yaml` | Neu, inkl. hinterlegter inverser Typ je Eintrag. | — |
| `research/vocabularies/screening_workflow_states.yaml` | **Entfällt ersatzlos** (v2-Änderung). | — |
| `tools/_researchlib.py` | Neu: `derive_workflow_state()` (reine Funktion, kein Speicherort), `RELATIONSHIP_TYPE_INVERSE`, `collision_group_is_resolved()` (Union-Find). | — |
| `tools/validate_research.py` | Neu: `check_screening_related_records` (candidate-basiert, gerichtete Symmetrie), `check_screening_collision_group_connectivity` (ersetzt die reine Paarprüfung aus v1). Angepasst: `check_screening_system_actor_invariants`/`check_deduplication` rufen `derive_workflow_state()` statt einen gespeicherten Wert zu vergleichen. **Entfällt:** `check_screening_workflow_state_projection` (v2-Änderung, nicht mehr nötig). | — |
| `tools/initialize_screening_records.py` | Optional, separater Folge-Vorschlag: feinere `candidate_source_type`-Ableitung aus `publication_types` inkl. der in Abschnitt 4.5 gelisteten neuen Werte. | — |

**Kein Schema-Versionsbump nötig** — alle Änderungen additiv-optional, keine Migration der 197
bestehenden Records (für `related_records` gilt zusätzlich: nichts nachzutragen, leeres Array ist der
gültige Ausgangszustand; für den entfallenen `workflow_state` gilt es ohnehin nicht mehr, da kein Feld
existiert).

## 8. Nicht-Ziele dieses Entwurfs (unverändert aus v1)

- Keine rückwirkende Änderung der 197 bestehenden Screening Records.
- Keine automatische Auflösung der drei realen Kollisions-Records.
- Keine Ableitung von `relationship_type` durch Automatisierung.
- Keine Erweiterung von `duplicate_of`-Semantik.

## 9. Offene Fragen für den CSO (Revision v2 — bereinigt um die in Runde 1 beantworteten Fragen)

Aus v1 **beantwortet und entfallen:** Richtungsabhängigkeit (jetzt gerichtet, Abschnitt 6),
Vollständigkeit der Kollisionsprüfung (jetzt Zusammenhangskomponenten, Abschnitt 2.5), 4-Zustands- vs.
3-Zustands-Frage bleibt technisch offen, aber die Grundsatzfrage „gespeichert oder berechnet" ist geklärt
(berechnet, Abschnitt 1).

**Weiterhin offen bzw. neu durch Runde 1 hinzugekommen:**

1. Wird der zusätzliche, weiterhin nicht-persistente Zustand „Teil einer ungelösten Kollisionsgruppe"
   (Abschnitt 1.4) bereits jetzt benötigt, oder erst bei konkretem Tooling-Bedarf?
2. Priorität, falls ein PubMed-Artikel sowohl `Meta-Analysis` als auch `Systematic Review` trägt —
   Vorschlag `meta_analysis` vor `systematic_review` (Abschnitt 4.5), CSO-Bestätigung ausstehend.
3. Verhältnis von `practice_guideline` (neu) zum bereits bestehenden `guideline` — Ersatz, Ergänzung oder
   Präzisierung?
4. Wird `living_systematic_review` als eigenständiger Wert tatsächlich benötigt, oder reicht
   `systematic_review` weiterhin aus (Abschnitt 4.3)?
5. Technische Verifikation vor Umsetzung nötig für `consensus_statement`, `technical_report`, `dataset`
   (aktueller NLM-Publication-Type-Katalog) — soll das vor oder im Rahmen der Implementierungs-PR
   erfolgen?
6. Soll die technische `publication_types`-Ableitung als eigenständiger, kleinerer Folge-PR vor der
   vollständigen `related_records`-Implementierung umgesetzt werden, oder gemeinsam?
7. Ist die Zusammenhangskomponenten-Prüfung (Abschnitt 2.5) ausreichend streng, oder wird doch die
   strengere, vollständige paarweise Klassifikation gewünscht?
8. Freigabe, diesen Entwurf (v2) als Grundlage für die konkrete Implementierung in einer eigenständigen
   Phase-4B-1B-2-PR zu verwenden.

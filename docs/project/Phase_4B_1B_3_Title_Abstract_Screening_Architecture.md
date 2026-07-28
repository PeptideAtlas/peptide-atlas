---
title: "Phase 4B-1B-3 – Title & Abstract Screening Architecture (Proposed)"
description: Architektur-Entwurf für ein vollständiges Reviewer-Modell (Mensch + KI + Zweitreview), Konfliktauflösung, Wiederaufnahme ausgeschlossener Studien und Skalierung auf zehntausende Screening Records. Reine Spezifikation, keine Implementierung.
tags:
  - Architektur
  - Projekt
  - Datenmodell
---

# Phase 4B-1B-3 – Title & Abstract Screening Architecture (Proposed)

!!! warning "Status: Vorgeschlagen, nicht entschieden"
    Dieses Dokument ist ein **Architektur-Entwurf** (siehe ADR-0059 im [Decision Log](Decision_Log.md),
    Status „Vorgeschlagen"). Es enthält **keine Implementierung**: keine Schema-Änderungen, keine
    Validator-Änderungen, keine veränderten oder neuen Screening Records, keine echten Include-/
    Exclude-Entscheidungen. Alle Codeblöcke in diesem Dokument sind Entwürfe zur Diskussion, keine
    bereits angewendeten Artefakte.

## 0. Anlass, Geltungsbereich und Lesehinweis

Phase 4B-1B-1 (ADR-0057, gemerged) hat 197 reale Screening Records im administrativen Ausgangszustand
angelegt (`decision: pending`, Stufe `deduplication`). Phase 4B-1B-2 (ADR-0058, gemerged) hat die
Deduplizierungsarchitektur vervollständigt. Der nächste inhaltliche Schritt im bereits etablierten
Workflow (Abschnitt 8/9 im [Scientific Research Protocol](Scientific_Research_Protocol.md)) ist das
**Titel-/Abstract-Screening** selbst — die erste inhaltliche Sichtungsstufe, an der ein Kandidat anhand
von Titel und Kurzfassung ein- oder ausgeschlossen wird.

**Wichtiger Befund vorab:** ein großer Teil der angefragten Themen ist **bereits vollständig oder
größtenteils implementiert** — dieses Dokument unterscheidet deshalb durchgängig zwischen (a) bereits
bestehenden Mechanismen, die hier nur dokumentiert/auf diese Phase angewendet werden, und (b) echten
Lücken mit einem neuen Architekturvorschlag. Diese Unterscheidung ist keine Formsache: sie verhindert,
dass bereits sorgfältig geprüfte, mehrfach CSO-gehärtete Mechanik (Phase 4A, PR #2, 5+ Review-Runden)
unnötig verdoppelt oder ersetzt wird.

| Angefragtes Thema | Status | Abschnitt |
|---|---|---|
| Reviewer-Modell (Mensch + KI + Zweitreview) | **Teilweise vorhanden, echte Lücke: Akteurstyp** | 1 |
| Include-/Exclude-Entscheidungen | **Bereits vollständig vorhanden** | 2 |
| Kontrollierte Exclude-Gründe | **Bereits vollständig vorhanden** | 3 |
| Konfliktauflösung zwischen Reviewern | **Bereits vollständig vorhanden, eine neue Ergänzung** | 4 |
| Dokumentation jeder Entscheidung | **Bereits vollständig vorhanden, eine neue Ergänzung** | 5 |
| Wiederaufnahme ausgeschlossener Studien | **Echte Lücke** | 6 |
| Versionierung von Screening-Entscheidungen | **Bereits vollständig vorhanden (identisch mit Abschnitt 5)** | 7 |
| Trennung technische Validierung / wissenschaftliche Bewertung | **Bereits etabliertes Prinzip, hier verallgemeinert** | 8 |
| Mehrere Wirkstoffe gleichzeitig | **Bereits durchgängig protokollskaliert** | 9 |
| Skalierung auf zehntausende Records | **Teilweise geprüft, zwei Empfehlungen** | 10 |

## 1. Reviewer-Modell (Mensch + KI + Zweitreview)

### 1.1 Was bereits existiert

- **Erst-/Zweitprüfung strukturell getrennt** (ADR-0043): `primary_decision`/`decided_by`/`decided_at`
  vs. `second_review.reviewer_decision`/`reviewed_by`/`reviewed_at`, jeweils eigener Grund/Duplikatverweis
  (ADR-0047).
- **Reviewer-Unabhängigkeit erzwungen:** `second_review.reviewed_by` muss von `decided_by` abweichen;
  `adjudication.resolved_by` darf weder dem Erst- noch dem Zweitprüfer entsprechen.
- **`dual_reviewer_stages`** im Protokoll legt fest, an welchen Stufen ein Zweitreview verpflichtend ist
  (aktuell für Retatrutide: `[full_text, final]` — **`title_abstract` ist nicht enthalten**, siehe
  `research/protocols/research-protocol-retatrutide-v1.yaml`).
- **`research_actor_id`** (`^[a-z0-9][a-z0-9._-]*$`) ist bereits durchgängiges Muster für jedes
  Akteursfeld.
- **Ein KI-Akteur ist bereits reales Präjudiz im Projekt:** `cso-chatgpt` — „der KI-basierte Chief
  Scientific Officer des Projekts, keine menschliche Person" (Decision Log, Phase-4B-0-Eintrag) — trägt
  bereits reale Freigabeverantwortung (Protokollfreigabe).

### 1.2 Die echte Lücke: kein struktureller Akteurstyp

`research_actor_id` ist ein **rein syntaktisches** Kürzel — nichts im Schema unterscheidet einen
menschlichen Reviewer, einen KI-gestützten Reviewer (wie `cso-chatgpt`) und einen rein technischen
Akteur (wie `system-screening-initializer`, ADR-0057) voneinander. Diese Lücke ist **bereits bekannt und
bewusst vertagt**: ADR-0041 diskutierte genau diese Frage für `promotion_record.review.reviewers` und
verwarf eine Actor-Registry **nicht aus Prinzip**, sondern wegen des Umfangs zu jenem Zeitpunkt:

> „*Actor-Registry einführen (`id`, `actor_type: human|automation|ai_assistant|service`, ...) —
> inhaltlich die langfristig sauberere Lösung für Auditierbarkeit ... aber verworfen für diesen Commit
> ... verfrüht, solange noch keine realen Reviewer-Daten existieren. **Bleibt für eine spätere Phase
> vorgemerkt.***" (ADR-0041, Alternative 1)

Phase 4B-1B-3 — echtes Titel-/Abstract-Screening mit realen menschlichen und KI-gestützten Reviewern in
nennenswertem Umfang — ist genau diese vorgemerkte spätere Phase.

### 1.3 Entwurf: leichtgewichtige Actor-Registry (Option A, empfohlen)

**Bewusst NICHT** die 2026 in ADR-0041 befürchtete große Migration: `research_actor_id`-Felder bleiben
überall **unverändert einfache Strings** (kein bestehendes Schema ändert Typ oder Struktur). Die
Registry ist rein additiv — eine neue, unabhängige Objektart, die vorhandene Kürzel nachträglich mit
Typinformation versieht, ohne dass eine einzige bestehende Datei geändert werden müsste.

Neue Objektart `research_reviewer` (Schema-Entwurf, NICHT implementiert):

```json
{
  "$id": "research_reviewer.schema.json",
  "type": "object",
  "properties": {
    "schema_version": { "$ref": "common.schema.json#/$defs/schema_version" },
    "id": { "$ref": "common.schema.json#/$defs/research_actor_id" },
    "actor_type": {
      "type": "string",
      "enum": ["human", "ai_assistant", "automation", "service"]
    },
    "display_name": { "type": ["string", "null"] },
    "description": { "type": ["string", "null"] },
    "active": { "type": "boolean" },
    "created_at": { "$ref": "common.schema.json#/$defs/date" },
    "updated_at": { "$ref": "common.schema.json#/$defs/date" }
  },
  "additionalProperties": false,
  "required": ["schema_version", "id", "actor_type", "display_name", "description", "active", "created_at", "updated_at"]
}
```

Ordner `research/reviewers/`, ID-Muster identisch zu `research_actor_id` selbst (das Kürzel, das bereits
überall verwendet wird, wird direkt zur Datei-ID — keine Indirektionsebene).

**Wiederverwendung der bereits 2026 vorgeschlagenen Taxonomie** (`human`/`ai_assistant`/`automation`/
`service`) statt einer neuen Erfindung — Kontinuität zu ADR-0041. `system-screening-initializer` wäre
`automation`; `cso-chatgpt` wäre `ai_assistant`; ein menschlicher Reviewer wäre `human`.

**Bewusst milde referenzielle Kopplung:** die Registrierung ist **verpflichtend nur für Akteure, die als
`ai_assistant` oder `automation` auftreten** — die Behauptung „diese Entscheidung war KI-gestützt" ist
eine überprüfbare technische Tatsache und sollte auch überprüfbar sein. Für `human`-Akteure bleibt die
Registrierung **optional** — dieselbe organisatorische Grenze, die ADR-0041 bereits für menschliche
Identität akzeptiert hat (Kürzel beweisen keine bestimmte Person), wird hier bewusst **nicht**
verschärft, um keine neue, technisch nicht einlösbare Garantie vorzutäuschen.

### 1.4 Entwurf: leichtgewichtige Alternative (Option B)

Falls selbst diese kleine Registry als verfrüht gilt: reine **Namenskonvention** statt neuer Objektart —
KI-/Automatisierungsakteure MÜSSEN mit einem reservierten Präfix beginnen (`ai-*` bzw. bereits etabliert
`system-*`, siehe `system-screening-initializer`), validator-seitig als Regex-Prüfung erzwungen, aber
ohne strukturierte Metadaten (kein `display_name`, keine Nachvollziehbarkeit, welches KI-Modell/welche
Version). Schwächer, aber ohne neue Objektart. **Empfehlung bleibt Option A** — der Zusatzaufwand ist
gering (eine neue, kleine, optionale Objektart), der Erkenntnisgewinn deutlich höher.

### 1.5 Entwurf: verpflichtendes Zweitreview für nicht-menschliche Erstentscheidungen

Unabhängig von Option A/B, die zentrale neue Regel: **jede Erstentscheidung eines nicht-menschlichen
Akteurs (`ai_assistant`/`automation`) erfordert ein Zweitreview — unabhängig davon, ob
`dual_reviewer_stages` diese Stufe sonst verlangt.** Das erweitert den bestehenden
`dual_reviewer_stages`-Mechanismus um eine zweite, unabhängige Auslösebedingung, statt einen neuen
Mechanismus zu erfinden:

```python
# Entwurf, NICHT implementiert -- Erweiterung von _check_decision_snapshot
dual_review_required = (
    stage in protocol_dual_reviewer_stages
    or decided_by_actor_type in ("ai_assistant", "automation")  # neu
)
```

**Begründung:** erlaubt KI-gestütztes Erst-Screening im großen Maßstab (Abschnitt 10) — eine
Kernvoraussetzung, um zehntausende Kandidaten überhaupt zeitnah zu sichten — ohne dass eine
KI-Entscheidung je unbeaufsichtigt terminal wird. Der menschliche Reviewer prüft/bestätigt/widerspricht,
statt jeden Titel von Grund auf neu zu lesen.

### 1.6 Entwurf: Adjudikation bleibt ausschließlich menschlich

**Vorschlag (hart, nicht protokollkonfigurierbar):** `second_review.adjudication.resolved_by` muss
(sofern die Registry existiert, Option A) einen Akteur mit `actor_type: human` referenzieren. Ein
Widerspruch zwischen zwei Entscheidungen ist der Moment mit der größten fachlichen Tragweite im gesamten
Screening-Workflow — hier bleibt die Letztentscheidung ausdrücklich beim Menschen, unabhängig davon, wie
weit KI-Unterstützung an früheren Stellen reicht. Dies **erweitert**, ersetzt aber nicht, die bereits
bestehende Adjudikator-Unabhängigkeitsregel.

### 1.7 Offene Frage: Protokoll-Opt-out

Soll `screening_policy` ein Feld erhalten, das KI-gestütztes Erst-Screening pro Protokoll ausdrücklich
erlaubt/verbietet (`ai_screening_enabled: bool`, Default `false` — explizites Opt-in statt stillschweigend
erlaubt), oder ist die in 1.5 vorgeschlagene automatische Zweitreview-Pflicht als alleinige Absicherung
ausreichend? Siehe Abschnitt 11.

## 2. Include-/Exclude-Entscheidungen — bereits vollständig vorhanden

Keine neue Architektur nötig. Vollständig durch das bestehende Schema abgedeckt:

- `screening_decision`-Vokabular: `pending`/`include`/`exclude`/`duplicate`/`awaiting_full_text`/
  `uncertain`.
- `ALLOWED_DECISIONS_BY_STAGE["title_abstract"] = {"include", "exclude", "awaiting_full_text",
  "uncertain"}` — kein `pending`/`duplicate` an dieser Stufe (fachlich korrekt: Dedup ist bereits
  abgeschlossen, ein neuer Duplikatfund gehört nicht mehr hierher).
- `decision_reason` Pflicht (nicht `null`) genau dann, wenn `decision: exclude` — schema-seitig
  erzwungen, sowohl Top-Level als auch je `decision_history`-Eintrag.
- `full_text_status`: an `title_abstract` noch nicht `obtained` erforderlich (das gehört erst zu
  `full_text`/`final`, Abschnitt 9b im Scientific Research Protocol).

**Einzige Ergänzung durch dieses Dokument:** die in Abschnitt 1.5 vorgeschlagene zusätzliche
Zweitreview-Pflicht für nicht-menschliche Erstentscheidungen — inhaltlich keine Änderung an der
Include-/Exclude-Semantik selbst.

## 3. Kontrollierte Exclude-Gründe — bereits vollständig vorhanden

`research/vocabularies/exclusion_reasons.yaml` (13 Werte: `wrong_substance`, `wrong_population`,
`wrong_intervention`, `wrong_outcome`, `wrong_study_type`, `not_primary_source`, `duplicate_record`,
`insufficient_information`, `unavailable_full_text`, `not_scientific`, `marketing_content`,
`superseded_record`, `other`) deckt die für Titel-/Abstract-Screening typischen Ausschlussgründe bereits
vollständig ab, inkl. `other` als Auffangkategorie.

**Geprüfte, nicht empfohlene Ergänzung:** ein möglicher Wert `language_not_supported` (Abstract in einer
vom Reviewer-Team nicht abgedeckten Sprache) wurde erwogen, aber **nicht** in diesen Entwurf
aufgenommen — `other` deckt diesen seltenen Fall bereits ab, ein eigener Wert wäre vermutlich
Overengineering für einen Randfall. Als offene Frage an den CSO festgehalten (Abschnitt 11), keine
Festlegung.

## 4. Konfliktauflösung zwischen Reviewern — bereits vollständig vorhanden, eine Ergänzung

### 4.1 Was bereits existiert (ADR-0043/ADR-0046/ADR-0052/ADR-0053)

- Stimmen Erst- und Zweitentscheidung überein: keine Adjudikation nötig, eine dennoch vorhandene wäre
  selbst ein Fehler.
- Stimmen sie nicht überein: entweder bleibt die effektive Entscheidung `uncertain` (Erstentscheidung
  bleibt erhalten, geht nicht verloren), oder eine **dritte, unabhängige** Person löst über
  `adjudication` auf (`resolved_by`/`resolved_at`/`final_decision`/`rationale`).
- `adjudication.final_decision` ist strikt auf `include`/`exclude` beschränkt.
- `decision_confirmed` ist eine geprüfte Projektion von `reviewer_decision == primary_decision` — nicht
  frei editierbar, nicht gegen die effektive Entscheidung verglichen (ADR-0043).
- Abweichende `duplicate`-Zielverweise trotz gleicher `duplicate`-Entscheidung sind ein eigenständiger
  Konflikt (ADR-0052/ADR-0053) — bereits am Deduplizierungsschritt behandelt, nicht Teil dieser Phase.

### 4.2 Neu in diesem Entwurf

Die Adjudikator-muss-Mensch-sein-Regel (Abschnitt 1.6) ist die einzige inhaltliche Ergänzung zur
Konfliktauflösung. Alles andere wird unverändert auf `title_abstract` angewendet, nicht neu erfunden.

## 5. Dokumentation jeder Entscheidung — bereits vollständig vorhanden, eine Ergänzung

### 5.1 Was bereits existiert

`decision_history[]` ist bereits der vollständige, append-only dokumentierte Audit Trail: jeder Eintrag
trägt Stufe, alle drei Entscheidungsebenen (Erst-/Zweit-/effektiv), Gründe, verantwortliche Akteure,
Zeitpunkte, Volltextstatus. **Jeder** Eintrag (nicht nur der letzte) wird gegen dieselben Invarianten
geprüft (ADR-0042). Die Top-Level-Felder sind eine geprüfte Projektion des letzten Eintrags (ADR-0037).

### 5.2 Echte Lücke: `decision_history[]` ist nicht technisch vor rückwirkender Änderung geschützt

`research/screening/README.md` dokumentiert das bereits ehrlich: „Append-only ist redaktionelle
Konvention, ... nicht technisch erzwungen" — anders als `research/search_runs/**`, das durch
`tools/check_research_immutability.py` in CI geschützt ist (Abschnitt 7 im Scientific Research
Protocol). Bei rein technischer Initialisierung (Phase 4B-1B-1) war dieses Risiko gering (nur
`pending`-Einträge). Bei realem Titel-/Abstract-Screening mit potenziell folgenreichen
Include-/Exclude-Entscheidungen ist eine stillschweigend nachträglich veränderte Historie ein
ernsteres Risiko.

**Entwurf:** viertes `ImmutableTarget` in `tools/check_research_immutability.py` für
`research/screening/**`: jeder bereits committete `decision_history[]`-Eintrag muss byte-identisch
erhalten bleiben; **nur Anhängen neuer Einträge am Ende ist zulässig**. Alle übrigen Felder
(`candidate_title`, `related_records[]`, Top-Level-Projektionsfelder) bleiben wie in Phase 4B-1B-1/-2
bereits festgelegt kontrolliert veränderlich — dieser Vorschlag ändert an deren Mutability-Regeln
nichts, er schützt ausschließlich die historischen `decision_history`-Einträge selbst.

## 6. Wiederaufnahme bereits ausgeschlossener Studien — echte Lücke

### 6.1 Was bereits mechanisch funktioniert

`check_decision_history`s Stufen-/Datumsprüfung verbietet nur **Rückwärtslauf** (`stage_index <
prev_stage_index` bzw. `decided_at < prev_decided_at`) — ein **neuer** Eintrag an derselben oder einer
späteren Stufe, der eine frühere Entscheidung umkehrt, ist bereits heute mechanisch zulässig (verifiziert
gegen `tools/validate_research.py::check_decision_history`, Zeilen zur Stufen-/Datumsmonotonie). Das
Grundgerüst für eine „Wiederaufnahme" existiert also bereits — es fehlt die **semantische Schicht**:
warum wurde reaktiviert, durch wen, mit welcher Begründung, unterscheidbar von einer normalen
Weiterbewegung durch die Stufenfolge.

### 6.2 Entwurf: `revision_context` auf `decision_history`-Einträgen

Neues, optionales Feld je `decision_history`-Eintrag, **Pflicht genau dann**, wenn dieser Eintrag eine
vorherige Entscheidung **umkehrt** statt sie nur um eine neue Stufe zu ergänzen (formale Bedingung:
`stage_index <= prev_stage_index` UND `primary_decision != <vorherige effektive Entscheidung an
derselben oder einer frueheren Stufe>`):

```json
"revision_context": {
  "type": ["object", "null"],
  "properties": {
    "reason": {
      "type": "string",
      "enum": [
        "protocol_amendment", "new_evidence", "reviewer_error_correction",
        "periodic_reevaluation", "other"
      ]
    },
    "reference": {
      "type": "string",
      "minLength": 1,
      "description": "z. B. neue Protokollversion (research-protocol-<slug>-v2), Zitat/Fundstelle neuer Evidenz, oder Freitext-Begruendung bei 'other'."
    },
    "triggered_by": { "$ref": "common.schema.json#/$defs/research_actor_id" }
  },
  "additionalProperties": false,
  "required": ["reason", "reference", "triggered_by"]
}
```

Neues kontrolliertes Vokabular `research/vocabularies/screening_revision_reasons.yaml` mit den fünf
Werten oben.

**Verknüpfung zu Protokolländerungen (Abschnitt 31 im Scientific Research Protocol):** eine inhaltliche
Protokolländerung entsteht bereits heute als neue Version (`research-protocol-<slug>-v2.yaml`), ändert
aber nichts an bereits bestehenden Screening Records, deren `protocol_id` weiterhin auf `v1` verweist.
`revision_context.reason: protocol_amendment` mit `reference: research-protocol-<slug>-v2` macht diese
Verbindung erstmals explizit maschinenlesbar — ohne die bereits etablierte Versionierungsregel selbst zu
ändern.

**Vorschlag (an Abschnitt 1.6 angelehnt):** `triggered_by` einer Wiederaufnahme muss ein `human`-Akteur
sein (sofern die Registry existiert) — eine Wiederaufnahme ist eine redaktionelle Grundsatzentscheidung,
nicht Teil des routinemäßigen KI-gestützten Ersttriagierens aus Abschnitt 1.5.

## 7. Versionierung von Screening-Entscheidungen — identisch mit Abschnitt 5

**Es gibt keinen separaten Versionierungsmechanismus zu entwerfen** — `decision_history[]` (Abschnitt 5)
IST die Versionierung: jeder neue Zustand ist eine neue, angehängte Version, nichts wird überschrieben.
Der einzige neue Baustein ist derselbe wie in Abschnitt 5.2 (technischer Schreibschutz für bereits
committete Einträge) plus `revision_context` (Abschnitt 6.2) als semantische Kennzeichnung *rückwärts
gerichteter* Versionsänderungen. Dieser Abschnitt existiert nur, um die Frage explizit zu beantworten,
statt sie unbeantwortet zu lassen: **die Versionierung ist bereits gelöst, nicht neu zu bauen.**

## 8. Trennung zwischen technischer Validierung und wissenschaftlicher Bewertung

### 8.1 Bereits etabliertes Prinzip (ADR-0057), hier verallgemeinert

Phase 4B-1B-1 etablierte für `system-screening-initializer`: der Validator prüft **Struktur**
(Pflichtfelder, Vokabular-Zugehörigkeit, Konsistenz zwischen Feldern), **niemals inhaltliche Richtigkeit**
einer wissenschaftlichen Entscheidung. Dieses Dokument verallgemeinert das explizit auf **jede** neue
Regel, die hier vorgeschlagen wird:

| Regel | Technisch geprüft (Validator) | Wissenschaftlich (nie vom Validator geprüft) |
|---|---|---|
| Zweitreview-Pflicht bei KI-Erstentscheidung (1.5) | Ist `second_review` vorhanden, wenn `decided_by`-Akteurstyp nicht `human` ist? | Ist die Erstentscheidung inhaltlich richtig? |
| Adjudikator muss Mensch sein (1.6) | Ist `resolved_by`-Akteurstyp `human`? | Ist die Adjudikationsentscheidung inhaltlich richtig? |
| Exclude-Grund (Abschnitt 3) | Ist der Wert im kontrollierten Vokabular? | Ist dieser Grund für **diesen konkreten** Kandidaten tatsächlich zutreffend? |
| Wiederaufnahme (6.2) | Ist `revision_context` vorhanden und vollständig, wenn eine Entscheidung umgekehrt wird? | Rechtfertigt die angegebene `reference` inhaltlich die Wiederaufnahme? |
| Historienschutz (5.2) | Ist ein bereits committeter Eintrag unverändert? | — (rein strukturell, keine wissenschaftliche Dimension) |

**Konsequenz für eine künftige KI-Unterstützung im großen Maßstab (Abschnitt 10):** der Validator bleibt
in jedem Fall blind gegenüber der inhaltlichen Qualität einer KI- oder menschlichen Entscheidung. Skalierung
löst ein Kapazitätsproblem (wie viele Kandidaten können in welcher Zeit gesichtet werden), nicht ein
Qualitätsproblem — Qualität bleibt ausschließlich Aufgabe der Reviewer selbst und des in Abschnitt 4
bereits bestehenden Konfliktauflösungsmechanismus.

## 9. Vorbereitung auf mehrere Wirkstoffe gleichzeitig

### 9.1 Bereits durchgängig protokollskaliert

Eine Prüfung der bestehenden Architektur zeigt: **es gibt keine versteckte Single-Substanz-Annahme.**

- Jedes Research-Objekt trägt `protocol_id` — ein neuer Wirkstoff ist einfach ein neues Protokoll
  (`research-protocol-<neuer-slug>-v1`), keine Struktur muss geändert werden.
- `check_deduplication` gruppiert bereits **je Protokoll** (`by_protocol`) — Identifikator-Kollisionen
  über verschiedene Protokolle hinweg sind ausdrücklich erlaubt (dieselbe Publikation kann legitim in
  mehreren unabhängigen Recherche-Vorhaben auftauchen, Abschnitt 8 im Scientific Research Protocol).
- Das Kontrollartefakt `research/screening_status/initialization_manifest.yaml` (ADR-0057) ist bereits
  als Liste **je `protocol_id`** modelliert („höchstens ein Eintrag je `protocol_id`") — mehrere
  Wirkstoffe parallel wurden dort bereits mitgedacht, nicht erst mit diesem Dokument.
- `research_actor_id`-Kürzel sind **projektweit**, nicht protokollgebunden — ein Reviewer kann an
  mehreren Wirkstoffen gleichzeitig arbeiten, ohne Sonderbehandlung.

### 9.2 Was dieses Dokument zusätzlich sicherstellt

Jede in diesem Dokument neu vorgeschlagene Regel (Reviewer-Modell, Wiederaufnahme, Historienschutz) ist
**pro Konstruktion protokollunabhängig formuliert** — keine davon nennt Retatrutide oder einen anderen
Wirkstoff. Die vorgeschlagene Actor-Registry (1.3) ist explizit **projektweit**, nicht protokollgebunden,
da Reviewer typischerweise wirkstoffübergreifend arbeiten.

**Offene, nicht in diesem Dokument gelöste Frage:** Reviewer-**Kapazitäts-**/Zuweisungsplanung über
mehrere gleichzeitig laufende Wirkstoff-Screenings hinweg ist eine Tooling-/Prozessfrage, keine
Datenarchitekturfrage — bewusst außerhalb des Geltungsbereichs dieses Dokuments (siehe Abschnitt 12).

## 10. Skalierung auf zehntausende Screening Records

### 10.1 Dateilayout

Aktuell: ein flaches Verzeichnis `research/screening/*.yaml`, ein Kandidat je Datei (197 Dateien heute).
Bei 10.000–50.000 Dateien bleibt ein flaches Verzeichnis technisch funktionsfähig (Git und moderne
Dateisysteme handhaben Verzeichnisse dieser Größenordnung ohne strukturelle Probleme; `protocol_id` als
Feld liefert bereits die logische Gruppierung, unabhängig von der physischen Verzeichnisstruktur) —
**keine Änderung empfohlen, um keine verfrühte Komplexität einzuführen.** Eine Sharding-Strategie (z. B.
Unterverzeichnisse je Protokoll oder je erstem Hex-Zeichen der UUID) bleibt als spätere Option
festgehalten, **nur** falls reale Performance-Probleme auftreten — nicht vorab implementiert.

### 10.2 Validator-Laufzeit

`load_research_dataset` lädt und schema-validiert **alle** Dateien bei jedem Lauf, projektweit über alle
Protokolle. Bei linearem Wachstum auf zehntausende Records wird das der dominante CI-Laufzeitfaktor
(aktuell: 197 Records, `validate-and-test`-Job Gesamtlaufzeit ~35-45s inkl. `pytest`/Katalog/Graph/
`mkdocs`). **Empfehlung:** kein vorzeitiges Caching/Incremental-Validation einführen (Komplexität,
Fehleranfälligkeit) — stattdessen einen konkreten Beobachtungsschwellenwert festlegen (Vorschlag: falls
der `validate-and-test`-Job wiederholt über ~5 Minuten läuft, wird eine inkrementelle Validierung
[nur geänderte Dateien je PR-Diff plus vollständiger Lauf auf `main`] zur eigenständigen Prüfung fällig)
— eine bewusste, dokumentierte Nicht-Entscheidung statt stillschweigender Ignoranz.

### 10.3 Bereits skalierende Mechanismen

Die in Phase 4B-1B-2 eingeführte Zusammenhangskomponenten-Prüfung für Kollisionsgruppen (Union-Find,
`O(n·α(n))`) sowie die je-Protokoll-Gruppierung in `check_deduplication` sind bereits für diese
Größenordnung ausgelegt — keine weitere Optimierung in diesem Dokument nötig.

### 10.4 Was Skalierung für das Reviewer-Modell bedeutet

Die in Abschnitt 1.5 vorgeschlagene KI-Erstscreening-Regel ist der zentrale Skalierungshebel dieses
Dokuments: sie erlaubt, dass ein KI-Akteur den überwiegenden Teil eines großen Korpus in vertretbarer
Zeit sichtet, während jede einzelne Entscheidung strukturell an ein menschliches Zweitreview gebunden
bleibt (Abschnitt 8.1: Kapazität, nicht Qualität, wird gelöst).

### 10.5 Nicht in diesem Dokument behandelt (explizit außerhalb des Geltungsbereichs)

Reviewer-Oberfläche/UI, Aufgabenverteilung/Warteschlangen, Benachrichtigungen, Fortschritts-Dashboards —
alles Tooling-/Prozessfragen, keine Datenarchitektur. Siehe Abschnitt 12.

## 11. Zusammenfassung der Schema-Änderungen (Entwurf, nicht angewendet)

| Datei | Änderung | Additiv? |
|---|---|---|
| `schemas/research_reviewer.schema.json` | Neu (Option A, Abschnitt 1.3) — eigenständige, optionale Objektart. | Ja, neue Objektart |
| `schemas/research_screening_record.schema.json` | Neu: `decision_history[].revision_context` (optional, Pflicht nur bei Umkehrung, Abschnitt 6.2). | Ja |
| `research/vocabularies/screening_revision_reasons.yaml` | Neu, 5 Werte (Abschnitt 6.2). | — |
| `tools/check_research_immutability.py` | Neu: viertes `ImmutableTarget` für `research/screening/**`, schützt ausschließlich bereits committete `decision_history[]`-Einträge (Abschnitt 5.2). | — |
| `tools/validate_research.py` | Angepasst: `_check_decision_snapshot` (Dual-Review-Pflicht bei nicht-menschlicher Erstentscheidung, Adjudikator-muss-Mensch-Regel, `revision_context`-Vollständigkeitsprüfung bei Umkehrungen). Neu (falls Option A): `check_research_reviewers` (Registry-Konsistenz, Pflichtregistrierung für `ai_assistant`/`automation`). | — |
| `research/protocols/*.schema.json` (`research_protocol.schema.json`) | Offene Frage (1.7): optionales `screening_policy.ai_screening_enabled`. | Ja, falls umgesetzt |

**Kein Schema-Versionsbump nötig** — alle Änderungen additiv-optional. Keine Migration der 197
bestehenden Records erforderlich (`revision_context` ist nur für künftige, tatsächlich umkehrende
Einträge relevant; die Registry ist für bestehende Akteure nachträglich befüllbar, ohne dass ein
bestehender Screening Record geändert werden müsste).

## 12. Nicht-Ziele dieses Entwurfs

- Keine echten Include-/Exclude-Entscheidungen für die 197 bestehenden Records.
- Keine Auflösung der drei realen DOI-kollidierenden Records (bleibt Phase-4B-1B-2-Folgearbeit).
- Keine Reviewer-Oberfläche, kein UI, keine Aufgabenverteilung/Warteschlangen (Abschnitt 10.5).
- Keine automatische Ableitung von Include-/Exclude-Entscheidungen durch die Validierungsschicht selbst
  — der Validator bleibt strukturell, nie inhaltlich (Abschnitt 8).
- Keine Änderung an der bereits bestehenden `dual_reviewer_stages`-Grundmechanik — nur eine zusätzliche,
  unabhängige Auslösebedingung (Abschnitt 1.5).

## 13. Offene Fragen für den CSO

1. Actor-Registry: Option A (leichtgewichtige neue Objektart `research_reviewer`, empfohlen) oder
   Option B (reine Namenskonvention, Abschnitt 1.4)?
2. Ist die verpflichtende Registrierung für `ai_assistant`/`automation`-Akteure (Abschnitt 1.3)
   ausreichend, oder soll sie auch für `human` gelten?
3. Ist die automatische Zweitreview-Pflicht bei nicht-menschlicher Erstentscheidung (Abschnitt 1.5) die
   richtige Absicherung, oder wird zusätzlich ein protokollweites Opt-in-Feld
   `ai_screening_enabled` benötigt (Abschnitt 1.7)?
4. Ist die harte Adjudikator-muss-Mensch-Regel (Abschnitt 1.6) korrekt, oder soll sie
   protokollkonfigurierbar bleiben?
5. Ist die vorgeschlagene `revision_context.reason`-Werteliste (Abschnitt 6.2, 5 Werte) vollständig?
6. Muss `revision_context.triggered_by` zwingend ein `human`-Akteur sein (Abschnitt 6.2), oder reicht
   die allgemeine Zweitreview-Pflicht aus Abschnitt 1.5 auch hier?
7. Soll `language_not_supported` doch als eigener Exclude-Grund ergänzt werden (Abschnitt 3), oder bleibt
   `other` ausreichend?
8. Ist der vorgeschlagene Beobachtungsschwellenwert für Validator-Laufzeit (Abschnitt 10.2, ~5 Minuten)
   sinnvoll, oder soll von Anfang an eine inkrementelle Validierungsstrategie entworfen werden?
9. Freigabe, diesen Entwurf als Grundlage für die konkrete Implementierung in einer eigenständigen
   Phase-4B-1B-3-PR zu verwenden.

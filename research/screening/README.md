# research/screening/

Ein Screening-Datensatz (`screening-record-<uuid4>.yaml`) repräsentiert **einen gefundenen Kandidaten** —
nicht automatisch eine kanonische Quelle. Er dokumentiert die Ein-/Ausschlussentscheidung und deren Begründung.

- Schema: [`schemas/research_screening_record.schema.json`](../../schemas/research_screening_record.schema.json)

## Technische Initialisierung (ADR-0057, Phase 4B-1B-1)

`tools/initialize_screening_records.py` erzeugt für jeden Discovery-Kandidaten eines
`research_candidate_manifest` (siehe [`research/candidates/README.md`](../candidates/README.md)) genau einen
Screening-Datensatz im rein administrativen, noch nicht wissenschaftlich gescreenten Initialzustand:

```yaml
decision: pending
decision_stage: deduplication
decision_reason: null
duplicate_of: null
full_text_status: not_yet_obtained
screened_by: system-screening-initializer
second_review: null
```

**`pending` bedeutet ausschließlich „noch nicht wissenschaftlich gescreent" — nicht „wahrscheinlich
relevant" und nicht „wahrscheinlich irrelevant".** `system-screening-initializer` dokumentiert nur die
technische Initialisierung; es ist kein wissenschaftlicher Reviewer und hat keine Relevanzentscheidung
getroffen.

Zwei bewusste Abweichungen vom Vokabular, das man naiv erwarten würde (siehe ADR-0057 im
[Decision Log](../../docs/project/Decision_Log.md) für die vollständige Begründung):

- **`decision_stage: deduplication`, nicht `title_abstract`:** `tools/_researchlib.py::
  ALLOWED_DECISIONS_BY_STAGE` erlaubt `pending` ausschließlich an Stufe `deduplication` — der
  Ausgangszustand vor jeder inhaltlichen Sichtung. `title_abstract` verlangt bereits eine inhaltliche
  Entscheidung (`include`/`exclude`/`awaiting_full_text`/`uncertain`).
- **`full_text_status: not_yet_obtained`, nicht `not_requested`:** letzterer Wert existiert nicht im
  kontrollierten Vokabular (`research/vocabularies/full_text_statuses.yaml`); `not_yet_obtained`
  ("Noch nicht beschafft") ist die inhaltlich passende, tatsächlich vorhandene Entsprechung.

**Validator-seitig erzwungene Invarianten** (`tools/validate_research.py`):

- `check_screening_system_actor_invariants`: JEDER `decision_history`-Eintrag mit
  `decided_by: system-screening-initializer` muss `primary_decision: pending`,
  `stage: deduplication`, `full_text_status: not_yet_obtained`, keinen Duplikatverweis und keine
  Zweitprüfung tragen — der technische Akteur kann strukturell NIE `include`/`exclude`/`duplicate`
  dokumentieren. Solange der aktuelle effektive Bearbeiter (`screened_by`) noch dieser Akteur ist,
  muss `canonical_source_id` `null` bleiben und `candidate_title` (bei aufgelöster Kandidatenreferenz)
  exakt der aus den Candidate-Manifest-Metadaten abgeleitete Titel sein.
- `check_screening_candidate_uniqueness`: höchstens ein Screening-Datensatz je
  (`candidate_manifest_id`, `candidate_id`)-Paar.
- `check_screening_candidate_references` (seit ADR-0057 erweitert): `search_run_ids` muss bei
  aufgelöster Kandidatenreferenz **exakt** (nicht nur teilweise) den
  `discovered_in_search_run_ids` des referenzierten Kandidaten entsprechen.
- `check_deduplication` (ADR-0057-Anpassung): eine Identifikator-Kollision, an der noch mindestens ein
  nie menschlich übernommener, system-initialisierter Datensatz beteiligt ist, ist nur eine
  **Warnung** („potenzielles Duplikat, menschliche Prüfung steht aus") — kein Fehler. Sobald ein
  Mensch **jeden** beteiligten Datensatz übernommen hat (`screened_by` ≠ `system-screening-initializer`
  für alle Mitglieder der Kollisionsgruppe), gilt die Deduplizierungsphase für diese Gruppe als
  abgeschlossen und eine weiterhin ungelöste Kollision wird wieder zum Fehler.
- `check_screening_initialization_completeness`: „jeder Candidate eines Protokolls braucht einen
  Screening-Datensatz" greift **ausschließlich** für Protokolle, die im rein technischen
  Kontrollartefakt `research/screening_status/initialization_manifest.yaml` ausdrücklich als
  `status: complete` markiert sind — ein teilweise durchgelaufener Import macht die CI dadurch nicht
  zwischenzeitlich rot.
- `canonical_source_id` bleibt `null`, bis nach manueller Prüfung tatsächlich eine Datei unter
  `data/sources/**` angelegt wurde.
- `decision: exclude` benötigt `decision_reason` aus dem kontrollierten Vokabular
  (`research/vocabularies/exclusion_reasons.yaml`).
- `decision: duplicate` benötigt `duplicate_of` (Verweis auf einen anderen Screening-Datensatz
  **desselben Protokolls** — `tools/validate_research.py` prüft das für die gesamte Kette, nicht nur den
  unmittelbaren Verweis).
- **`decision_stage: final` ist die einzige extraktionsfähige Stufe** (Validator-seitig erzwungen):
  `decision: include`, `full_text_status: obtained`, keine erforderliche, aber fehlende Zweitprüfung, und
  kein ungelöster Widerspruch zwischen Erst- und Zweitentscheidung. `full_text` dokumentiert nur die
  Volltextbewertung, entscheidet aber noch nicht abschließend (siehe
  [Scientific Research Protocol](../../docs/project/Scientific_Research_Protocol.md), Abschnitt 9b).
- Jeder `decision_history[]`-Eintrag trennt strukturell **`primary_decision`** (Erstentscheidung, bleibt bei
  einem ungelösten Widerspruch immer erhalten) von **`decision`** (effektive/aktuelle Entscheidung, ggf. nach
  Adjudikation) — siehe [Scientific Research Protocol](../../docs/project/Scientific_Research_Protocol.md),
  Abschnitt 9c. `second_review.reviewer_decision` ist schema-seitig Pflicht (nicht `null`), sobald
  `second_review` gesetzt ist. `decision_confirmed` wird Validator-seitig als Projektion von
  `reviewer_decision == primary_decision` geprüft (**nicht** gegen die effektive `decision`), nicht frei
  editierbar akzeptiert. Eine Adjudikation ist nur zulässig, wenn Erst- und Zweitentscheidung tatsächlich
  abweichen, und ihr `final_decision` ist auf `include`/`exclude` beschränkt.
- Eine zentrale Stage-/Decision-Matrix (`tools/_researchlib.py::ALLOWED_DECISIONS_BY_STAGE`) begrenzt, welche
  Entscheidungen an welcher Stufe zulässig sind (z. B. kein `pending`/`duplicate` an Stufe `final`) — geprüft
  gegen **alle drei** Entscheidungsebenen: `primary_decision`, `second_review.reviewer_decision` und die
  effektive `decision` jedes Eintrags.
- Jede der drei Entscheidungsebenen speichert ihren eigenen Grund/Duplikatverweis unabhängig und verlustfrei:
  `primary_decision_reason`/`primary_duplicate_of`, `second_review.reviewer_decision_reason`/
  `reviewer_duplicate_of`, sowie `decision_reason`/`duplicate_of` für die effektive Entscheidung — dieselbe
  bedingte Regel (Pflicht bei `exclude`/`duplicate`, sonst `null`) gilt unabhängig je Ebene.
- **`deduplication` unterstützt strukturell keine Adjudikation**: `second_review` darf an dieser Stufe zwar
  vorhanden sein, aber `second_review.adjudication` ist dort immer ein Validierungsfehler. Ein Dedup-Widerspruch
  bleibt immer `decision: uncertain` und wird durch einen neuen Screening-Eintrag aufgelöst, nicht durch
  Adjudikation. `screening_policy.dual_reviewer_stages` (im Protokoll) kann `deduplication` bereits schema-seitig
  nicht enthalten und muss außerdem eine Teilmenge von `screening_policy.stages` sein.
- **Historische Duplikatverweise referenziell geprüft:** `primary_duplicate_of`,
  `second_review.reviewer_duplicate_of` und `decision_history[].duplicate_of` müssen (wenn nicht `null`) auf
  einen tatsächlich existierenden Screening-Datensatz **desselben Protokolls** verweisen und dürfen nicht auf
  den eigenen Datensatz zeigen — jeweils am exakten Feldpfad geprüft. Anders als bei der effektiven
  Top-Level-`duplicate_of` läuft hier **keine** Ketten-/Zyklenverfolgung: jedes historische Feld ist die
  Momentaufnahme einer einzelnen Entscheidung, kein fortlaufend gepflegter Verweis.
- **Unterschiedliche Duplikatziele sind ein Konflikt, auch bei gleicher Entscheidung:** Wählen Erst- und
  Zweitprüfung beide `decision: duplicate`, aber mit unterschiedlichem `primary_duplicate_of`/
  `second_review.reviewer_duplicate_of`, ist `decision_confirmed: true` ein Validierungsfehler — beide sind
  sich einig, dass es sich um ein Duplikat handelt, aber nicht, wessen Duplikat. Die effektive `decision`
  bleibt `uncertain`, `duplicate_of` bleibt `null`, bis ein neuer `decision_history`-Eintrag den Widerspruch
  auflöst (siehe ADR-0052 im [Decision Log](../../docs/project/Decision_Log.md)).
- **Effektives Duplikatziel deterministisch gebunden:** Ohne Zweitprüfung muss die effektive `duplicate_of`
  exakt `primary_duplicate_of` entsprechen. Bei bestätigtem Duplikatkonsens (`decision_confirmed: true` bei
  `duplicate`) müssen Erst-, Zweit- und effektives Duplikatziel **identisch** sein — ein davon abweichender
  dritter Hauptdatensatz in `duplicate_of` ist ein Validierungsfehler, selbst wenn dieser dritte Datensatz
  selbst ein gültiger, existierender, protokollinterner Screening-Datensatz ist (siehe ADR-0053 im
  [Decision Log](../../docs/project/Decision_Log.md)).
- `decision_history[]` wird als **gesamtes** Array geprüft (jeder Eintrag, nicht nur der aktuelle Zustand,
  inkl. Datumsreihenfolge gegen jeden referenzierten Suchlauf). **Seit ADR-0059 (Phase 4B-1B-3) ist Append-only
  nicht mehr nur redaktionelle Konvention, sondern technisch erzwungen:** `tools/check_research_immutability.py`
  vergleicht jeden bereits committeten `decision_history[]`-Eintrag byte-identisch gegen den Merge-Base — nur
  Anhängen neuer Einträge am Ende ist zulässig, ein bereits committeter Eintrag darf weder geändert noch entfernt
  noch umsortiert werden. Alle übrigen Felder (`candidate_title`, Top-Level-Projektionsfelder, `related_records`)
  bleiben davon unberührt weiterhin frei kontrolliert veränderlich.
- **Zweitreview-Pflicht bei nicht-menschlicher Erstentscheidung (ADR-0059):** jede primäre `include`/
  `exclude`-Entscheidung eines Akteurs, der in [`research/reviewers/**`](../reviewers/README.md) mit
  `actor_type: ai_assistant` oder `automation` registriert ist, erfordert `second_review` — unabhängig davon,
  ob `screening_policy.dual_reviewer_stages` diese Stufe sonst verlangt. Ein unregistriertes Kürzel löst diese
  Pflicht nicht aus (dieselbe Grenze wie die für `human` optionale Registrierung).
- **Adjudikation bleibt ausschließlich menschlich (ADR-0059):** `second_review.adjudication.resolved_by` darf,
  sofern registriert, keinen Akteur mit `actor_type` ≠ `human` referenzieren — hart, nicht
  protokollkonfigurierbar. Erweitert die bereits bestehende Adjudikator-Unabhängigkeitsregel (Drittperson,
  ungleich Erst-/Zweitprüfer), ersetzt sie nicht.
- **`decision_history[].revision_context` (ADR-0059):** echtes optionales Feld (kein required-aber-nullable
  Key wie `decision_reason`) — Pflicht genau dann, wenn ein Eintrag die effektive Entscheidung des unmittelbar
  vorangegangenen Eintrags an **derselben Stufe** umkehrt (die bestehende Monotonie-Prüfung verbietet echten
  Rückwärtslauf bereits strukturell, sodass sich „an derselben oder einer früheren Stufe" aus der ursprünglichen
  Spezifikation auf genau diesen Fall reduziert). Ein Übergang von `pending`/`uncertain` zu einer konkreten
  Entscheidung ist **keine** Umkehrung, sondern die erste tatsächliche Entscheidung (z. B. der bereits
  bestehende Zielkonflikt-Mechanismus aus ADR-0052/ADR-0053). `reason` folgt dem kontrollierten Vokabular
  `research/vocabularies/screening_revision_reasons.yaml` (8 Werte); `triggered_by` muss, sofern registriert,
  ein `human`-Akteur sein.
- Die zeitliche Provenienzkette wird objektübergreifend geprüft: die terminale Screening-Entscheidung (bzw.
  deren Zweitprüfung/Adjudikation) muss vor der Extraktion liegen, die Extraktion vor ihrer Verifikation
  (siehe `research/extractions/README.md`). Zusätzlich muss `created_at <= Ereignisdatum <= updated_at`
  objektintern für jeden `decision_history[].decided_at`, `second_review.reviewed_at` und
  `second_review.adjudication.resolved_at` gelten.
- Alle Akteursfelder (`screened_by`, `decided_by`, `second_review.reviewed_by`,
  `second_review.adjudication.resolved_by`, seit ADR-0059 auch `decision_history[].revision_context.
  triggered_by`) folgen der `research_actor_id`-Syntax (`^[a-z0-9][a-z0-9._-]*$`, keine Leerzeichen, keine
  Großschreibung) und können optional in [`research/reviewers/**`](../reviewers/README.md) einen
  strukturellen Akteurstyp tragen.
- Siehe [Evidence Curation Workflow](../../docs/project/Evidence_Curation_Workflow.md) für den vollständigen
  Zustandsübergang.

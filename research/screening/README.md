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
  dokumentieren. Solange der Bearbeitungszustand (seit ADR-0058, Phase 4B-1B-2: `tools/_researchlib.py::
  derive_workflow_state()`, siehe unten) noch `system_initialized` ist, muss `canonical_source_id`
  `null` bleiben und `candidate_title` (bei aufgelöster Kandidatenreferenz) exakt der aus den
  Candidate-Manifest-Metadaten abgeleitete Titel sein.
- `check_screening_candidate_uniqueness`: höchstens ein Screening-Datensatz je
  (`candidate_manifest_id`, `candidate_id`)-Paar.
- `check_screening_candidate_references` (seit ADR-0057 erweitert): `search_run_ids` muss bei
  aufgelöster Kandidatenreferenz **exakt** (nicht nur teilweise) den
  `discovered_in_search_run_ids` des referenzierten Kandidaten entsprechen.
- `check_deduplication` (seit ADR-0058, Phase 4B-1B-2 — ersetzt die vormals rein paarweise
  ADR-0057-Logik): eine Identifikator-Kollisionsgruppe gilt erst dann als vollständig erklärt, wenn
  sie — über Kanten aus `duplicate_of` (bibliographische Dubletten) UND `related_records`
  (eigenständige, aber inhaltlich verwandte Publikationen, siehe unten) — eine EINZIGE
  Zusammenhangskomponente bildet (Union-Find über die gesamte Gruppe, nicht nur die aktuell
  „aktiven" Mitglieder). Das erkennt transitive Erklärung korrekt: eine Dreiergruppe braucht nur 2
  Kanten (statt aller 3 Paare), um vollständig verbunden zu sein — z. B. A `duplicate_of` B, C
  `replies_to` B, ohne dass A↔C zusätzlich direkt dokumentiert werden müsste. Eine nicht
  vollständig verbundene Gruppe ist nur eine **Warnung** („potenzielles Duplikat, menschliche
  Prüfung steht aus") — kein Fehler —, solange mindestens ein Mitglied der Gruppe
  Bearbeitungszustand `system_initialized` hat (siehe unten). Sobald kein Mitglied mehr
  `system_initialized` ist, wird eine weiterhin ungelöste Kollision zum Fehler.
- **`related_records[]` (ADR-0058, Phase 4B-1B-2):** optionales, additives Feld — strukturell
  getrennt von `duplicate_of`, das ausschließlich für bibliographische Dubletten (derselbe Text)
  reserviert bleibt. Dokumentiert eigenständige, aber inhaltlich verwandte Kandidaten (z. B.
  Letter+Reply, Preprint+publizierte Fassung, Korrektur+Originalpublikation). Referenziert
  Kandidaten (`related_candidate_manifest_id`/`related_candidate_id`), NICHT Screening Records —
  `candidate_id` ist seit ADR-0056 technisch erzwungen unveränderlich, `research_screening_record.id`
  hat keine vergleichbare Garantie. `relationship_type` folgt einem gerichteten, 17-wertigen
  kontrollierten Vokabular (`research/vocabularies/screening_relationship_types.yaml`: 9
  Konzeptpaare, z. B. `replies_to`/`has_reply`, `corrects`/`corrected_by`, plus `other_related_to`
  als einzige bewusst symmetrische Ausnahme). Jeder Eintrag trägt eine Pflicht-Freitext-`rationale`
  sowie `relationship_metadata` (`identified_by`/`identified_at`/`evidence_source[]` — 10-wertiges
  Vokabular `research/vocabularies/screening_relationship_evidence_sources.yaml`). `confidence`
  (Konzept dokumentiert in ADR-0058) ist bewusst **nicht** implementiert, solange keine Skala final
  freigegeben ist. **`relationship_metadata` beschreibt ausschließlich die Evidenz DAFÜR, dass die
  Beziehung besteht — niemals die wissenschaftliche Evidenz der beteiligten Studie(n) selbst; fließt
  nie in Evidenzstufe/`evidence_category` ein.**
  `check_screening_related_records` prüft: Ziel-Kandidat existiert als `candidates[]`-Eintrag im
  selben Protokoll, kein Selbstverweis, `relationship_metadata.identified_by` ist nie
  `system-screening-initializer` (eine Beziehungsklassifikation ist eine inhaltliche, keine
  technische Entscheidung). Gerichtete Symmetrie: existiert bereits ein Screening Record für den
  Ziel-Kandidaten, muss dessen eigenes `related_records[]` den passenden INVERSEN
  `relationship_type` zurückverweisen (fehlende Gegenrichtung: Warnung, wird erneut geprüft sobald
  der Ziel-Datensatz angelegt wird; falscher, nicht-inverser Typ: Fehler).
- **Bearbeitungszustand als reine Projektion (ADR-0058, Phase 4B-1B-2):**
  `tools/_researchlib.py::derive_workflow_state()` berechnet `system_initialized`/
  `under_human_review`/`finalized` AUSSCHLIESSLICH aus `decision_history` — **kein Schemafeld, kein
  Cache, keine zweite Wahrheitsquelle.** Ersetzt die vormals redundante, an zwei Stellen
  duplizierte `screened_by`-Stringvergleichslogik. `system_initialized`: genau ein Eintrag,
  verantwortet von `system-screening-initializer`. `finalized`: Stufe `final`, `decision`
  `include`/`exclude`, kein ungelöster Erst-/Zweitprüfungs-Widerspruch. `under_human_review`: alles
  dazwischen.
- **Erweitertes `candidate_source_type`-Vokabular (ADR-0058, Phase 4B-1B-2):** eigenständiges
  `research_candidate_source_type` (`schemas/common.schema.json`, `research/vocabularies/
  research_candidate_source_types.yaml`) statt einer Erweiterung des mit `data/**` geteilten
  `source_type` — 12 Basiswerte identisch mit `data/vocabularies/source_types.yaml`, plus 18
  zusätzliche wissenschaftliche Publikationstyp-Werte (Letter/Reply/Editorial/Case Report/
  Corrigendum/Retraction/Expression of Concern/Meta-Analysis/Narrative Review/Scoping Review/
  Umbrella Review/Practice Guideline/Consensus Statement/Technical Report/White Paper/Dataset/
  Software/Protocol Paper). `tools/refresh_candidate_source_types.py` (separates, explizites
  Dry-Run-Werkzeug, siehe dessen Docstring) verfeinert den bei der Initialisierung gesetzten
  generischen Wert anhand bereits versionierter PubMed-`publication_types`-Metadaten — rein
  technisch, nie eine wissenschaftliche Entscheidung, rührt einen Datensatz nur an, solange dessen
  Bearbeitungszustand noch `system_initialized` ist. `reply_or_response` wird NIE automatisiert
  vergeben (PubMed unterscheidet Letter/Reply strukturell nicht) — ausschließlich menschliche
  `related_records`-Klassifikation.
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
- **Zweitreview-Pflicht bei nicht-menschlicher Erstentscheidung (ADR-0059, verschärft in
  CSO-Review Runde 2):** jede **nicht-administrative primäre wissenschaftliche Entscheidung**
  eines Akteurs, der in [`research/reviewers/**`](../reviewers/README.md) mit
  `actor_type: ai_assistant` oder `automation` registriert ist, erfordert `second_review` —
  unabhängig davon, ob `screening_policy.dual_reviewer_stages` diese Stufe sonst verlangt, UND
  unabhängig von der konkreten Entscheidung (`include`/`exclude`/`awaiting_full_text`/`uncertain`/
  `duplicate`, jeweils soweit die Stage-/Decision-Matrix diese Entscheidung an der jeweiligen Stufe
  überhaupt zulässt) — **nicht mehr nur `include`/`exclude`**. Die einzige Ausnahme ist der rein
  administrative `pending`-Initialisierungseintrag (strukturell nur an Stufe `deduplication`
  möglich, ausschließlich vom technischen Akteur `system-screening-initializer` erzeugt) — das ist
  keine „Erstentscheidung" in diesem Sinne. Ein unregistriertes Kürzel löst diese Pflicht nicht aus
  (dieselbe Grenze wie die für `human` optionale Registrierung).
- **Adjudikation muss ein registrierter Mensch sein (ADR-0059, verschärft in CSO-Review Runde 2):**
  `second_review.adjudication.resolved_by` muss auf ein Kürzel verweisen, das in
  [`research/reviewers/**`](../reviewers/README.md) mit `actor_type: human` registriert ist — hart,
  nicht protokollkonfigurierbar. Anders als bei normalen Erst-/Zweitprüfern reicht hier ein
  **unregistriertes** Kürzel NICHT mehr als implizite Mensch-Annahme; ein unregistriertes oder ein
  registriertes `ai_assistant`/`automation`/`service`-Kürzel ist beides ungültig. Erweitert die
  bereits bestehende Adjudikator-Unabhängigkeitsregel (Drittperson, ungleich Erst-/Zweitprüfer),
  ersetzt sie nicht.
- **`decision_history[].revision_context` (ADR-0059):** echtes optionales Feld (kein required-aber-nullable
  Key wie `decision_reason`) — Pflicht genau dann, wenn ein Eintrag die effektive Entscheidung des unmittelbar
  vorangegangenen Eintrags an **derselben Stufe** umkehrt (die bestehende Monotonie-Prüfung verbietet echten
  Rückwärtslauf bereits strukturell, sodass sich „an derselben oder einer früheren Stufe" aus der ursprünglichen
  Spezifikation auf genau diesen Fall reduziert). Ein Übergang von `pending`/`uncertain` zu einer konkreten
  Entscheidung ist **keine** Umkehrung, sondern die erste tatsächliche Entscheidung (z. B. der bereits
  bestehende Zielkonflikt-Mechanismus aus ADR-0052/ADR-0053). `reason` folgt dem kontrollierten Vokabular
  `research/vocabularies/screening_revision_reasons.yaml` (8 Werte); `triggered_by` muss (verschärft in
  CSO-Review Runde 2) genau wie `adjudication.resolved_by` oben ein **registrierter** `human`-Akteur sein —
  ein unregistriertes Kürzel ist hier ebenfalls ungültig, nicht mehr implizit menschlich.
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

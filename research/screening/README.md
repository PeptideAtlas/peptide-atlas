# research/screening/

Ein Screening-Datensatz (`screening-record-<uuid4>.yaml`) repräsentiert **einen gefundenen Kandidaten** —
nicht automatisch eine kanonische Quelle. Er dokumentiert die Ein-/Ausschlussentscheidung und deren Begründung.

- Schema: [`schemas/research_screening_record.schema.json`](../../schemas/research_screening_record.schema.json)
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
  inkl. Datumsreihenfolge gegen jeden referenzierten Suchlauf) — ist aber ein manuell editierbares Feld
  innerhalb derselben Datei, **kein** unveränderliches, separates Event-Log (append-only ist redaktionelle
  Konvention, nicht technisch erzwungen).
- Die zeitliche Provenienzkette wird objektübergreifend geprüft: die terminale Screening-Entscheidung (bzw.
  deren Zweitprüfung/Adjudikation) muss vor der Extraktion liegen, die Extraktion vor ihrer Verifikation
  (siehe `research/extractions/README.md`). Zusätzlich muss `created_at <= Ereignisdatum <= updated_at`
  objektintern für jeden `decision_history[].decided_at`, `second_review.reviewed_at` und
  `second_review.adjudication.resolved_at` gelten.
- Alle Akteursfelder (`screened_by`, `decided_by`, `second_review.reviewed_by`,
  `second_review.adjudication.resolved_by`) folgen der `research_actor_id`-Syntax
  (`^[a-z0-9][a-z0-9._-]*$`, keine Leerzeichen, keine Großschreibung).
- Siehe [Evidence Curation Workflow](../../docs/project/Evidence_Curation_Workflow.md) für den vollständigen
  Zustandsübergang.

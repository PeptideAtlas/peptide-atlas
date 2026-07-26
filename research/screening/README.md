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
  gegen `primary_decision` **und** `decision` jedes Eintrags.
- `decision_history[]` wird als **gesamtes** Array geprüft (jeder Eintrag, nicht nur der aktuelle Zustand,
  inkl. Datumsreihenfolge gegen jeden referenzierten Suchlauf) — ist aber ein manuell editierbares Feld
  innerhalb derselben Datei, **kein** unveränderliches, separates Event-Log (append-only ist redaktionelle
  Konvention, nicht technisch erzwungen).
- Die zeitliche Provenienzkette wird objektübergreifend geprüft: die terminale Screening-Entscheidung (bzw.
  deren Zweitprüfung/Adjudikation) muss vor der Extraktion liegen, die Extraktion vor ihrer Verifikation
  (siehe `research/extractions/README.md`).
- Siehe [Evidence Curation Workflow](../../docs/project/Evidence_Curation_Workflow.md) für den vollständigen
  Zustandsübergang.

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
- `second_review.reviewer_decision` ist schema-seitig Pflicht (nicht `null`), sobald `second_review` gesetzt
  ist — eine Zweitprüfung ohne dokumentierte eigene Entscheidung ist strukturell nicht mehr möglich.
  `decision_confirmed` wird Validator-seitig als Projektion von `reviewer_decision == Erstentscheidung`
  geprüft, nicht frei editierbar akzeptiert.
- `decision_history[]` wird als **gesamtes** Array geprüft (jeder Eintrag, nicht nur der aktuelle Zustand) —
  ist aber ein manuell editierbares Feld innerhalb derselben Datei, **kein** unveränderliches, separates
  Event-Log (append-only ist redaktionelle Konvention, nicht technisch erzwungen).
- Siehe [Evidence Curation Workflow](../../docs/project/Evidence_Curation_Workflow.md) für den vollständigen
  Zustandsübergang.

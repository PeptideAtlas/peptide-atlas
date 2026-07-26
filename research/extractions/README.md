# research/extractions/

Ein Extraktionsdatensatz (`extraction-record-<uuid4>.yaml`) enthält **Beobachtungen und Arbeitsnotizen** aus
einer eingeschlossenen Quelle — kurze Paraphrasen mit präziser Fundstelle (Seite/Tabelle/Abbildung/Abschnitt),
keine langen wörtlichen Textübernahmen.

- Schema: [`schemas/research_extraction_record.schema.json`](../../schemas/research_extraction_record.schema.json)
- `extraction_status: verified` bedeutet **immer** durch eine andere Person geprüft: `verified_by` muss sich
  von `extracted_by` unterscheiden, unbedingt und ohne protokollabhängige Ausnahme (`tools/validate_research.py`,
  siehe ADR-0040 im [Decision Log](../../docs/project/Decision_Log.md)).
- `extraction_status: self_checked` ist der ehrliche Zustand für einen rein technischen
  Ein-Personen-Durchlauf ohne unabhängige Zweitprüfung — strukturell **nie** promotion-fähig (ein
  `promotion_record` darf sich nur auf eine `verified`-Extraktion beziehen).
- `candidate_claims[]` sind **ausdrücklich vorläufig** (`is_provisional: true`) und tragen niemals ein
  Status-Feld wie ein kanonischer Claim — sie erzeugen nie automatisch einen aktiven Claim unter `data/claims/**`.
- `canonical_source_id`/`canonical_study_id` dürfen erst gesetzt werden, wenn die entsprechenden Objekte unter
  `data/**` tatsächlich existieren.
- `extracted_by`/`verified_by` folgen der `research_actor_id`-Syntax (`^[a-z0-9][a-z0-9._-]*$`, keine
  Leerzeichen, keine Großschreibung; `verified_by` darf weiterhin `null` sein, solange keine Verifikation
  stattgefunden hat).
- `created_at <= extracted_at <= updated_at` und, wo gesetzt, `verified_at <= updated_at` gelten objektintern
  (ADR-0048 im [Decision Log](../../docs/project/Decision_Log.md)); zusätzlich darf `extracted_at` nicht vor
  Abschluss der terminalen Screening-Entscheidung liegen (objektübergreifende Kette, ADR-0044).
- Siehe [Evidence Curation Workflow](../../docs/project/Evidence_Curation_Workflow.md) für den Weg von der
  Beobachtung zum geprüften, aktiven kanonischen Claim.

# research/extractions/

Ein Extraktionsdatensatz (`extraction-record-<uuid4>.yaml`) enthält **Beobachtungen und Arbeitsnotizen** aus
einer eingeschlossenen Quelle — kurze Paraphrasen mit präziser Fundstelle (Seite/Tabelle/Abbildung/Abschnitt),
keine langen wörtlichen Textübernahmen.

- Schema: [`schemas/research_extraction_record.schema.json`](../../schemas/research_extraction_record.schema.json)
- `extraction_status: verified` erfordert eine zweite, getrennt dokumentierte Prüfung (`verified_by`/`verified_at`).
- `candidate_claims[]` sind **ausdrücklich vorläufig** (`is_provisional: true`) und tragen niemals ein
  Status-Feld wie ein kanonischer Claim — sie erzeugen nie automatisch einen aktiven Claim unter `data/claims/**`.
- `canonical_source_id`/`canonical_study_id` dürfen erst gesetzt werden, wenn die entsprechenden Objekte unter
  `data/**` tatsächlich existieren.
- Siehe [Evidence Curation Workflow](../../docs/project/Evidence_Curation_Workflow.md) für den Weg von der
  Beobachtung zum geprüften, aktiven kanonischen Claim.

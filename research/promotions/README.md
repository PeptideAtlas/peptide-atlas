# research/promotions/

Ein Promotion-Datensatz (`promotion-record-<uuid4>.yaml`) macht die Kette von einem verifizierten
Kandidatenclaim zu einem später manuell angelegten kanonischen Claim unter `data/claims/**`
**maschinenlesbar** nachvollziehbar:

```text
search_run → screening_record → extraction_record → promotion_record → kanonischer Claim
```

- Schema: [`schemas/research_promotion_record.schema.json`](../../schemas/research_promotion_record.schema.json)
- `extraction_record_id` muss auf einen `extraction_record` mit `extraction_status: verified` verweisen.
- `candidate_working_id` muss einem `candidate_claims[].working_id` in diesem Extraktionsdatensatz entsprechen.
- `promotion_status: approved_for_creation`/`promoted` erfordern dokumentierte Reviewer und eine
  nicht-leere `decision_rationale` — und dürfen **nie** automatisiert durch Automatisierung/KI gesetzt
  werden (siehe [Evidence Curation Workflow](../../docs/project/Evidence_Curation_Workflow.md), ADR-0035,
  ADR-0037 im [Decision Log](../../docs/project/Decision_Log.md)).
- `review.reviewers` ist **schema-seitig** auf Eindeutigkeit (`uniqueItems`) und Nicht-Leerheit (mindestens ein
  Nicht-Leerzeichen-Zeichen je Eintrag) geprüft — eigenständig definiert in diesem Schema, nicht über das
  gemeinsame `common.schema.json#/$defs/review_block` (das andere Objektarten unverändert weiterverwenden,
  siehe ADR-0045 im [Decision Log](../../docs/project/Decision_Log.md)). Setzt das referenzierte Protokoll
  `claim_promotion_policy.requires_second_review: true`, prüft der Validator zusätzlich die **Mindestanzahl**
  (mindestens zwei Kürzel, ADR-0041). **Grenze:** Schema und Validator prüfen nur die Kürzel selbst
  (Eindeutigkeit, keine Leerstrings, Mindestanzahl) — sie können nicht maschinell verifizieren, dass es sich
  dabei tatsächlich um zwei unterschiedliche *menschliche* Personen handelt. Diese Garantie bleibt in Phase 4A
  organisatorisch, durch Reviewprozess und Repository-Zugriffskontrolle abgesichert, nicht durch das
  Schema (siehe Abschnitt „Bekannte Grenzen" im
  [Scientific Research Protocol](../../docs/project/Scientific_Research_Protocol.md)).
- `self_checked` (unabhängig ungeprüfte Ein-Personen-Extraktion, siehe `research/extractions/README.md`)
  ist strukturell nie promotion-fähig — nur `extraction_status: verified` erfüllt Zeile 12 oben.
- `promotion_status: promoted` erfordert eine gesetzte `canonical_claim_id`, die unter `data/claims/**`
  tatsächlich existiert. `promotion_status: rejected` darf keine `canonical_claim_id` tragen.
- Ein Kandidatenclaim darf nicht unbemerkt mehrfach zu verschiedenen aktiven Promotionen führen (vom
  Validator geprüft, siehe `tools/validate_research.py`).
- Zeitliche Reihenfolge (ADR-0044): `extraction.verified_at <= created_at <= updated_at`; bei
  `approved_for_creation`/`promoted`/`rejected` zusätzlich `verified_at <= review.last_reviewed_at <=
  updated_at`.
- Dieser Datensatz selbst ist **kein** kanonisches Wissensobjekt und fließt nicht in `build/catalog.json`
  oder `build/graph.json` ein (siehe ADR-0033).

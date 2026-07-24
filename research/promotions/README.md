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
- Setzt das referenzierte Protokoll `claim_promotion_policy.requires_second_review: true`, prüft der
  Validator zusätzlich, dass `review.reviewers` mindestens **zwei unterschiedliche, nicht-leere**
  Kürzel enthält (ADR-0041). **Grenze:** Diese Prüfung stellt nur sicher, dass zwei unterschiedliche
  Kürzel eingetragen sind — sie kann nicht maschinell verifizieren, dass es sich dabei tatsächlich um
  zwei unterschiedliche *menschliche* Personen handelt. Diese Garantie bleibt in Phase 4A
  organisatorisch, durch Reviewprozess und Repository-Zugriffskontrolle abgesichert, nicht durch das
  Schema (siehe Abschnitt „Bekannte Grenzen" im
  [Scientific Research Protocol](../../docs/project/Scientific_Research_Protocol.md)).
- `self_checked` (unabhängig ungeprüfte Ein-Personen-Extraktion, siehe `research/extractions/README.md`)
  ist strukturell nie promotion-fähig — nur `extraction_status: verified` erfüllt Zeile 12 oben.
- `promotion_status: promoted` erfordert eine gesetzte `canonical_claim_id`, die unter `data/claims/**`
  tatsächlich existiert. `promotion_status: rejected` darf keine `canonical_claim_id` tragen.
- Ein Kandidatenclaim darf nicht unbemerkt mehrfach zu verschiedenen aktiven Promotionen führen (vom
  Validator geprüft, siehe `tools/validate_research.py`).
- Dieser Datensatz selbst ist **kein** kanonisches Wissensobjekt und fließt nicht in `build/catalog.json`
  oder `build/graph.json` ein (siehe ADR-0033).

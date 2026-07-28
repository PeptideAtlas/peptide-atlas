# research/reviewers/

Ein Reviewer-Eintrag (`<research-actor-id>.yaml`) versieht ein bereits an anderer Stelle
verwendetes `research_actor_id`-Kürzel (z. B. `screened_by`, `decided_by`,
`second_review.reviewed_by`, `second_review.adjudication.resolved_by`,
`decision_history[].revision_context.triggered_by`) nachträglich mit einem strukturellen
Akteurstyp. Siehe ADR-0059 im [Decision Log](../../docs/project/Decision_Log.md) (Phase 4B-1B-3)
für die vollständige Begründung.

- Schema: [`schemas/research_reviewer.schema.json`](../../schemas/research_reviewer.schema.json)
- Die `id` dieses Objekts **ist** das Kürzel selbst — keine Indirektionsebene, keine separate
  technische ID. Der Dateiname muss exakt der `id` entsprechen (z. B. `cso-chatgpt.yaml`).

## Keine neue Migration

`research_actor_id`-Felder bleiben überall **unverändert einfache Strings** — kein bestehendes
Schema ändert Typ oder Struktur. Diese Registry ist rein additiv: ein bereits verwendetes Kürzel
wird nachträglich beschrieben, ohne dass eine einzige bestehende Datei geändert werden müsste.

## `actor_type`

Vier Werte: `human` | `ai_assistant` | `automation` | `service`. Zwei weitere Werte
(`external_expert`, `editorial_board`) sind vom CSO **langfristig reserviert**, aber ausdrücklich
**noch nicht** Teil dieses Enums (ADR-0059, Phase 4B-1B-3 Review) — eine spätere, eigenständige
Erweiterung fügt sie additiv hinzu.

## Registrierungspflicht

**Verpflichtend** für Akteure, die als `ai_assistant`, `automation` oder `service` auftreten —
`tools/validate_research.py::check_research_reviewers` erzwingt das für die beiden bereits
bekannten, real existierenden nicht-menschlichen Akteure:

| Kürzel | `actor_type` | Beleg |
|---|---|---|
| `system-screening-initializer` | `automation` | ADR-0057 — rein technischer Initialisierungsakteur, trifft nie eine wissenschaftliche Entscheidung |
| `cso-chatgpt` | `ai_assistant` | Decision Log, Phase-4B-0-Eintrag — "der KI-basierte Chief Scientific Officer des Projekts, keine menschliche Person" |

Für `human`-Akteure bleibt die Registrierung **optional** — dieselbe organisatorische Grenze, die
ADR-0041 bereits für menschliche Identität akzeptiert hat (ein Kürzel beweist keine bestimmte
Person).

**Bewusst nicht registriert:** `claude-code-operator` (`research_search_run.executed_by`, 4
Vorkommen in den Phase-4B-1A-Suchläufen) ist ein real existierendes, drittes Kürzel — sein
`actor_type` ist jedoch nirgends im Projekt dokumentiert oder festgelegt. Diese Bestandsaufnahme
erfindet ihn **nicht**; kein Reviewer-Eintrag dafür angelegt. `executed_by` liegt ohnehin
außerhalb des Geltungsbereichs der neuen Regeln in diesem Dokument, die sich auf
Screening-Entscheidungsakteure (`decided_by`/`reviewed_by`/`resolved_by`/`triggered_by`)
beschränken.

## Strukturelle Konsequenzen einer Registrierung

Sobald ein Kürzel mit `actor_type: ai_assistant` oder `automation` registriert ist, erzwingt der
Validator zusätzlich:

- **Zweitreview-Pflicht:** jede Erstentscheidung (`primary_decision` `include`/`exclude`) dieses
  Akteurs erfordert `second_review` — unabhängig von `screening_policy.dual_reviewer_stages`
  (siehe [research/screening/README.md](../screening/README.md)).
- **Adjudikation bleibt ausschließlich menschlich:** `second_review.adjudication.resolved_by` darf
  nicht auf einen registrierten Akteur mit `actor_type` ≠ `human` verweisen.
- **`revision_context.triggered_by` bleibt ausschließlich menschlich:** dieselbe Regel wie bei der
  Adjudikation.

Ein **unregistriertes** Kürzel wird für diese drei Regeln wie ein menschlicher Akteur behandelt
(dieselbe Grenze wie die optionale `human`-Registrierung) — die Behauptung "diese Entscheidung war
KI-gestützt/automatisiert" wird erst durch eine tatsächliche Registrierung überprüfbar, nicht
automatisch unterstellt.

## Lebenszyklus

Kein Löschmechanismus. Ein nicht mehr eingesetzter Akteur wird `active: false` gesetzt statt
entfernt, damit bereits von ihm verantwortete `decision_history`-Einträge nachvollziehbar
referenzierbar bleiben.

## Zukunftsperspektive

Diese Objektart ist bewusst **nicht** auf Titel-/Abstract-Screening beschränkt konzipiert —
projektweit, protokoll- und stufenunabhängig. Perspektivisch auch für Promotion Review, Evidence
Review, Editorial Review und Quality Audit wiederverwendbar, ohne dass sich diese Objektart selbst
ändern müsste (ADR-0059, Abschnitt 1.8). Reine Zukunftsperspektive — keine Implementierung dieser
weiteren Anwendungsfälle in dieser Phase.

# research/ — Rechercheverlauf, Kandidaten, Screening, Extraktion und Audit Trail

Dieser Ordner ist die **Provenienz- und Arbeitsebene** von Peptide Atlas — nicht die kanonische
Wissensdatenbank. Er beantwortet die Frage „wie wurde etwas gefunden, geprüft und bewertet?", während
[`data/`](../data/README.md) die Frage „was ist geprüftes, veröffentlichtes Wissen?" beantwortet.

```text
research/** = Rechercheverlauf, Kandidaten, Screening, Extraktion und Audit Trail
data/**     = geprüfte und kanonisch veröffentlichte Wissensobjekte
```

**Ein Forschungsdatensatz unter `research/**` gilt nicht automatisch als wissenschaftliche Erkenntnis.**
Eine Information wird erst dann kanonisches Wissen, wenn sie nach manueller Prüfung ausdrücklich als Entität,
Quelle, Studie oder Claim unter `data/**` angelegt wurde (siehe ADR-0033 im
[Decision Log](../docs/project/Decision_Log.md)). `research/**` fließt deshalb **nicht** in
`build/catalog.json` oder `build/graph.json` ein.

Der vollständige, verbindliche Prozess steht in:

- [Scientific Research Protocol](../docs/project/Scientific_Research_Protocol.md) — das allgemeine, für jeden
  künftigen Wirkstoff geltende Standardverfahren.
- [Evidence Curation Workflow](../docs/project/Evidence_Curation_Workflow.md) — der konkrete
  Zustandsübergang vom Suchtreffer bis zum aktiven kanonischen Claim.

## Struktur

```text
research/
├── protocols/       Ein Research-Protokoll (research-protocol-<slug>-v<N>.yaml) pro Wirkstoff/Fragestellung
├── search_runs/     Protokollierte, tatsächlich ausgeführte Suchläufe (search-run-<uuid4>.yaml)
├── search_results/  Versionierte Identifikator-Manifeste je Suchlauf (search-result-manifest-<uuid4>.yaml)
├── candidates/      Technische Discovery-Kandidaten je Protokoll+Datenbank (candidate-manifest-<uuid4>.yaml)
├── screening/       Ein-/Ausschlussentscheidungen pro Kandidat (screening-record-<uuid4>.yaml)
├── screening_status/ Rein technisches Kontrollartefakt: Initialisierungsfortschritt je Protokoll (ADR-0057)
├── extractions/     Beobachtungen und vorläufige Kandidatenclaims (extraction-record-<uuid4>.yaml)
├── promotions/      Verknüpfung Kandidatenclaim → kanonischer Claim (promotion-record-<uuid4>.yaml)
├── reviewers/       Struktureller Akteurstyp fuer research_actor_id-Kuerzel (<research-actor-id>.yaml, ADR-0059)
├── vocabularies/    kontrollierte Vokabulare (Datenbanken, Statuswerte, Ausschlussgründe, ...)
├── examples/        ausschließlich fiktive Platzhalterdaten, eigener Namensraum (wie data/examples/)
└── raw/             lokaler, NICHT versionierter Arbeitsbereich fuer Exporte/Volltexte (siehe raw/README.md)
```

## Objektarten und ihre IDs

| Objektart | Ordner | ID-Muster | Schema |
|---|---|---|---|
| Research-Protokoll | `research/protocols/` | `research-protocol-<slug>-v<N>` | `schemas/research_protocol.schema.json` |
| Suchlauf | `research/search_runs/` | `search-run-<uuid4>` | `schemas/research_search_run.schema.json` |
| Search Result Manifest | `research/search_results/` | `search-result-manifest-<uuid4>` | `schemas/research_search_result_manifest.schema.json` |
| Candidate Manifest | `research/candidates/` | `candidate-manifest-<uuid4>` | `schemas/research_candidate_manifest.schema.json` |
| Screening-Datensatz | `research/screening/` | `screening-record-<uuid4>` | `schemas/research_screening_record.schema.json` |
| Extraktionsdatensatz | `research/extractions/` | `extraction-record-<uuid4>` | `schemas/research_extraction_record.schema.json` |
| Promotion-Datensatz | `research/promotions/` | `promotion-record-<uuid4>` | `schemas/research_promotion_record.schema.json` |
| Reviewer | `research/reviewers/` | `<research-actor-id>` (kein Praefix — die ID IST das Kürzel selbst) | `schemas/research_reviewer.schema.json` |

Siehe [`research/reviewers/README.md`](reviewers/README.md) für Details zum strukturellen Akteurstyp
(`human`/`ai_assistant`/`automation`/`service`, ADR-0059, Phase 4B-1B-3) und
[`research/candidates/README.md`](candidates/README.md) für Details zum Candidate Manifest (ADR-0056):
die technische, protokoll-/datenbankgebundene Brücke zwischen Search Result Manifest und Screening Record.

`research/screening_status/initialization_manifest.yaml` (ADR-0057) ist **kein** Research-Objekt aus obiger
Tabelle — kein eigener `RESEARCH_KINDS`-Eintrag, keine wissenschaftliche Aussage. Es ist ein rein technisches
Kontrollartefakt (Schema `schemas/research_screening_initialization_manifest.schema.json`), das je Protokoll
dokumentiert, ob `tools/initialize_screening_records.py` für alle zum Zeitpunkt des letzten Laufs bekannten
Candidate-Manifest-Einträge ohne Fehler/Konflikte durchgelaufen ist (`status: complete`). Siehe
[`research/screening/README.md`](screening/README.md) für Details zur Initialisierung.

Wie bei `data/**` muss der Dateiname exakt der `id` entsprechen (ohne `.yaml`).

## Validierung

```bash
python tools/validate_research.py --verbose
python tools/check_research_immutability.py
python tools/initialize_screening_records.py --protocol-id <research-protocol-id>
```

`initialize_screening_records.py` (ADR-0057) erzeugt für jeden Discovery-Kandidaten eines Protokolls genau
einen rein administrativen `research_screening_record` (`decision: pending`, `decision_stage: deduplication`,
`screened_by: system-screening-initializer`) — deterministisch, idempotent, ohne Netzwerkzugriffe und ohne
jemals eine wissenschaftliche Entscheidung zu treffen. Siehe
[`research/screening/README.md`](screening/README.md) für den vollständigen Initialzustand und die
Validator-seitig erzwungenen Invarianten.

`validate_research.py` läuft **getrennt** vom bestehenden `tools/validate_data.py`, prüft aber Querverweise auf
die kanonische Datenebene (`canonical_source_id` muss unter `data/sources/**`, `canonical_study_id` unter
`data/entities/studies/**`, `canonical_claim_id` unter `data/claims/**` existieren, sofern gesetzt) sowie
Protokollkonsistenz (Version/ID, Freigabestatus, ein Suchlauf darf nur eine unter
`planned_information_sources[]` freigegebene Datenbank verwenden, protokollübergreifende Referenzen inkl. der
gesamten `duplicate_of`-Kette, `dual_reviewer_stages` als Teilmenge von `stages`), echte Identifier-
Deduplizierung (ADR-0057: eine Kollision, an der noch mindestens ein nie menschlich übernommener,
system-initialisierter Screening Record beteiligt ist, ist nur eine WARNUNG — „potenzielles Duplikat,
menschliche Prüfung steht aus" — kein ERROR; sobald ein Mensch **jeden** beteiligten Datensatz übernommen
hat, wird eine weiterhin ungelöste Kollision zum ERROR), den vollständigen Screening-Workflow (JEDER `decision_history`-Eintrag wird geprüft, nicht nur
der aktuelle Zustand: Stage-/Decision-Matrix gegen alle drei Entscheidungsebenen — `primary_decision`,
`second_review.reviewer_decision`, effektive `decision` —, strukturell getrennte, verlustfreie Drei-Ebenen-
Provenienz inkl. eigenständiger Gründe/Duplikatverweise je Ebene, Dual-Reviewer-Pflicht (nicht für
`deduplication`, das strukturell keine Adjudikation unterstützt), wechselseitig konsistente
Zweitentscheidung/Adjudikation, Volltextregeln, terminale Extraktionsfähigkeit), die zeitliche Provenienzkette
sowohl objektübergreifend (Screening → Extraktion → Verifikation → Promotion) als auch objektintern (jedes von
einem Objekt selbst dokumentierte Ereignisdatum liegt innerhalb von dessen eigenem
`[created_at, updated_at]`) und die Claim-Promotion-Kette (inkl. `claim_promotion_policy.
requires_second_review`, symmetrisch für `approved_for_creation`/`promoted`/`rejected`).
Seit ADR-0059 (Phase 4B-1B-3) zusätzlich: `research/reviewers/**`-Registry-Konsistenz und
Pflichtregistrierung der bereits bekannten nicht-menschlichen Akteure (`system-screening-initializer` als
`automation`, `cso-chatgpt` als `ai_assistant` — nur wenn ein Datensatz sie tatsächlich verwendet), Zweitreview-
Pflicht für jede primäre `include`/`exclude`-Entscheidung eines registrierten `ai_assistant`/`automation`-
Akteurs (unabhängig von `dual_reviewer_stages`), Adjudikation und `decision_history[].revision_context.
triggered_by` ausschließlich durch registrierte `human`-Akteure (ein unregistriertes Kürzel gilt als
menschlich), sowie `revision_context` genau dann verpflichtend, wenn ein Eintrag die effektive Entscheidung
des unmittelbar vorangegangenen Eintrags an derselben Stufe umkehrt.

`check_research_immutability.py` prüft zusätzlich, dass bereits committete `search_run`-Dateien nicht
rückwirkend verändert werden (nur `status`/`updated_at`/`review`/`notes` dürfen sich ändern), dass
`candidates`-Discovery-Identität unveränderlich bleibt (ADR-0056), und seit ADR-0059 (Phase 4B-1B-3), dass
bereits committete `decision_history[]`-Einträge eines Screening Records byte-identisch erhalten bleiben —
nur Anhängen neuer Einträge ist zulässig, alle übrigen Screening-Felder bleiben frei kontrolliert
veränderlich. Alle drei Validatoren laufen in CI (siehe `.github/workflows/ci.yml`).

**Was validiert wird, im Klartext:** JSON-Schema-Konformität und die oben genannten Cross-Referenz-/
Workflow-Regeln sind **Validator-seitig erzwungen** (Pull Requests mit Verstößen werden von der CI blockiert).
Die Unveränderlichkeit von Suchläufen ist **CI-seitig geprüft**, aber nur soweit der Git-Vergleichs-Ref
auflösbar ist (siehe `tools/check_research_immutability.py`, keine Branch-Protection-Garantie). Alle
Research-Akteursfelder folgen einer restriktiven `research_actor_id`-Kürzel-Syntax (schema-seitig erzwungen),
die stabile, unterscheidbare Kürzel sicherstellt — aber ob ein Reviewer-Kürzel tatsächlich eine andere
*menschliche* Person bezeichnet, bleibt weiterhin organisatorisch/durch Repository-Zugriffskontrolle
abgesichert (siehe „Bekannte Grenzen" im
[Scientific Research Protocol](../docs/project/Scientific_Research_Protocol.md), Abschnitt 34). Seit ADR-0059
(Phase 4B-1B-3) technisch überprüfbar ist dagegen die schwächere, aber eigenständig nützliche Aussage
„dieses Kürzel ist als KI-gestützt/automatisiert/technischer Dienst **registriert**" — siehe
[`research/reviewers/README.md`](reviewers/README.md). Ein **unregistriertes** Kürzel wird für die daran
anknüpfenden Regeln (verpflichtendes Zweitreview bei KI-/Automatisierungs-Erstentscheidung, Adjudikation und
`revision_context.triggered_by` ausschließlich menschlich) wie ein menschlicher Akteur behandelt — dieselbe
Grenze wie die für `human` optionale Registrierung.

## Kurzfassung des Workflows

1. Ein **Protokoll** (`protocols/`) legt Forschungsfragen, geplante Suchbegriffe, Datenbanken sowie Ein-/
   Ausschluss-, Dedup-, Screening-, Extraktions- und Claim-Promotion-Regeln fest, bevor gesucht wird.
2. Ein **Suchlauf** (`search_runs/`) protokolliert exakt, was wann in welcher Datenbank gesucht wurde; sein
   versioniertes **Search Result Manifest** (`search_results/`) haelt die tatsaechlich erhaltene
   Identifikatormenge fest (siehe ADR-0055).
2a. Ein **Candidate Manifest** (`candidates/`, siehe ADR-0056) buendelt die Search Result Manifests
    desselben Protokolls/derselben Datenbank zu einer normalisierten, technischen Discovery-Grundmenge mit
    vollstaendiger Suchlauf-Herkunft je Kandidat — noch KEINE Screening-Entscheidung.
2b. `tools/initialize_screening_records.py` (ADR-0057) erzeugt für jeden Candidate-Manifest-Eintrag
    genau einen **Screening-Datensatz** im rein administrativen Initialzustand (`decision: pending`,
    `decision_stage: deduplication`, `screened_by: system-screening-initializer`) — noch keine
    wissenschaftliche Bewertung, nur die technische Bereitstellung des Datensatzes für den nächsten Schritt.
3. Jeder Treffer durchläuft Deduplizierung, Titel-/Abstract- und Volltext-Screening bis zu einer
   **terminalen** Entscheidung (`decision_stage: final`, `include`/`exclude`/`duplicate`/...) — `full_text`
   dokumentiert nur die Volltextbewertung, ist aber selbst noch nicht extraktionsfähig.
4. Eingeschlossene, terminal bestätigte Kandidaten werden in einem **Extraktionsdatensatz** (`extractions/`)
   mit kurzen Paraphrasen und präzisen Fundstellen erfasst — inklusive vorläufiger, ausdrücklich ungeprüfter
   Kandidatenclaims.
5. Ein **Promotion-Datensatz** (`promotions/`) macht optional den Fortschritt eines einzelnen Kandidatenclaims
   in Richtung eines kanonischen Claims maschinenlesbar nachvollziehbar (`promotion_status: proposed` → … →
   `promoted`).
6. Erst nach unabhängiger Zweitprüfung (`extraction_status: verified` — per Definition durch eine andere
   Person als `extracted_by`, `self_checked` ist nie promotion-fähig) und wissenschaftlichem Review werden
   Informationen **manuell** als Quelle, Studie oder Claim unter `data/**` angelegt — dieser Schritt ist in
   Phase 4A bewusst **nicht automatisiert**.

## `research/examples/`

Wie `data/examples/`: ausschließlich offensichtlich fiktive Platzhalterdaten, ein eigener, in sich
geschlossener Namensraum, der nicht in echte Validierungs-Querverweise oder Exporte eingeht.

## Sicherheit und Urheberrecht

- Keine Zugangsdaten, Tokens oder API-Schlüssel.
- Keine personenbezogenen Patientendaten.
- Keine vollständigen urheberrechtlich geschützten Artikeltexte — nur kurze Paraphrasen mit Fundstelle
  (technisch durch eine Zeichenlängengrenze in den Schemas abgesichert, siehe
  [Scientific Research Protocol](../docs/project/Scientific_Research_Protocol.md), Abschnitt „Urheberrecht und
  Volltextspeicherung").
- Keine PDF-Sammlung im Repository.

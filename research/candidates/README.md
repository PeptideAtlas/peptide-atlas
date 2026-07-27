# research/candidates/

Ein Candidate Manifest (`candidate-manifest-<uuid4>.yaml`) ist eine **protokoll- und
datenbankgebundene, technisch-bibliographische Normalisierung** der Vereinigungsmenge stabiler
Identifikatoren (PMID *oder* NCT-ID, nie gemischt) aus einem oder mehreren
[`research_search_result_manifest`](../search_results/README.md)-Datensätzen. Siehe ADR-0056 im
[Decision Log](../../docs/project/Decision_Log.md) für die vollständige Begründung.

- Schema: [`schemas/research_candidate_manifest.schema.json`](../../schemas/research_candidate_manifest.schema.json)
- Erzeugt/aktualisiert durch [`tools/build_research_candidates.py`](../../tools/build_research_candidates.py).

## Begriffstrennung

| Objektart | Bedeutet |
|---|---|
| Search Result Manifest | Die unveränderte Trefferliste **eines einzelnen** Suchlaufs. |
| **Candidate Manifest** | Die normalisierte, **protokollgebundene** Discovery-Menge mit vollständiger technischer Herkunft über mehrere Suchläufe/Manifeste hinweg. |
| Screening Record | Die **wissenschaftliche** Ein-/Ausschlussentscheidung zu einem Kandidaten. |
| Source Object | Eine später freigegebene kanonische Quelle unter `data/**`. |
| Study Object | Eine wissenschaftliche Studie, die mehrere Publikationen/Registereinträge verbinden kann. |

## Ein Candidate Manifest bedeutet NICHT

Relevant · eingeschlossen · wissenschaftlich geprüft · peer-reviewed · Originalstudie · Humanstudie ·
sicher · wirksam · kanonische Quelle. Es ist ein **Discovery-Snapshot**, keine Entscheidung.

## Objektgranularität

Ein Manifest pro **Protokoll × Datenbank** (nicht eine Datei je Kandidat) — z. B. ein
PubMed-Candidate-Manifest mit allen entdeckten PMIDs und ein ClinicalTrials.gov-Candidate-Manifest
mit allen entdeckten NCT-IDs für dasselbe Protokoll. Jeder Kandidat innerhalb des Manifests trägt
eine stabile interne `candidate_id` (`research-candidate-<uuid4>`), die bei erneutem Lauf von
`tools/build_research_candidates.py` für denselben `primary_identifier` erhalten bleibt.

## Herkunft (`discovered_in_search_run_ids`)

Ein Identifikator kann in mehreren Suchläufen desselben Protokolls auftauchen (z. B. zwei
Alias-Suchen nach demselben Wirkstoff unter Entwicklungsname und Wirkstoffname). Die Herkunft wird
**vollständig** dokumentiert — nie auf einen einzigen "primären" Suchlauf reduziert. Der Validator
(`tools/validate_research.py::check_candidate_manifests`) prüft dies bijektiv: jeder Identifikator
aus einem referenzierten Search Result Manifest kommt genau einmal im Candidate Manifest vor, und
seine `discovered_in_search_run_ids` entsprechen exakt den Suchläufen, die ihn tatsächlich enthielten
— nicht mehr, nicht weniger.

## Metadaten

Nur sparsame, strukturierte technische/bibliographische Felder — siehe
`schemas/research_candidate_manifest.schema.json#/$defs/pubmed_metadata` bzw.
`#/$defs/clinicaltrials_gov_metadata`. **Kein** Abstracttext, keine vollständigen
Freitextbeschreibungen, keine Ergebnisdaten. `metadata_status` (kontrolliertes Vokabular
[`candidate_metadata_statuses.yaml`](../vocabularies/candidate_metadata_statuses.yaml)) ist ein rein
technischer Abrufzustand: `not_fetched` → `fetched`/`partial`/`not_found`/`fetch_error`. Jeder
Abrufversuch trägt eine nachvollziehbare `metadata_provenance` (Interface, Zeitpunkt, technische
Anfragereferenz) — niemals geheime Tokens oder vollständige API-URLs mit sensiblen Parametern.

## Unveränderlichkeit

Nach dem Merge unveränderlich (siehe `tools/check_research_immutability.py`): `id`, `protocol_id`,
`database`, `identifier_namespace`, `source_search_run_ids`, `source_result_manifest_ids`,
`candidate_count`, sowie je Kandidat `candidate_id`/`primary_identifier`/
`discovered_in_search_run_ids`. Kontrolliert **aktualisierbar** bleiben je Kandidat `metadata`/
`metadata_status`/`metadata_fetch_note`/`metadata_provenance` sowie das Manifest-eigene
`updated_at` (Metadaten-Refresh ändert nie, welche Kandidaten entdeckt wurden oder woher).

## Erzeugung

```bash
python tools/build_research_candidates.py --from-manifests --protocol-id research-protocol-retatrutide-v1
python tools/build_research_candidates.py --refresh-metadata --protocol-id research-protocol-retatrutide-v1
```

`--from-manifests` läuft offline und ist deterministisch: unveränderte Eingaben erzeugen denselben
fachlichen Output (bestehende `candidate_id`-Werte und bereits abgerufene Metadaten bleiben
erhalten). `--refresh-metadata` ruft fehlende Metadaten über die offiziellen APIs ab (NCBI ESummary
für PubMed, ClinicalTrials.gov API v2) — lädt niemals Volltexte oder PDFs, und ein Netzwerkfehler
entfernt nie die Discovery-Identität eines Kandidaten (er setzt nur `metadata_status: fetch_error`
mit einer knappen technischen Begründung).

## Verhältnis zum Screening Record

Ein `screening_record` kann über `candidate_manifest_id`/`candidate_id` auf genau den
Discovery-Kandidaten zurückverweisen, aus dem er hervorgegangen ist (siehe
`schemas/research_screening_record.schema.json`). Die Pflicht dazu ist **datengetrieben**
(`tools/validate_research.py::check_screening_candidate_references`): existiert mindestens ein
Candidate Manifest mit derselben `protocol_id`, müssen neue, reale Screening Records dieses
Protokolls die Referenz setzen; existiert (noch) keins für ein Protokoll, bleibt die Referenz dort
optional (Migrationskompatibilität für ältere Protokolle). `research/examples/**` bleibt davon immer
ausgenommen. Liegt eine Referenz vor, muss der zum Namespace passende externe Identifikator
(`candidate_identifiers.pmid` bzw. `.nct_id`) gesetzt sein und mit dem Kandidaten übereinstimmen —
ein fehlender und ein abweichender Identifikator sind zwei getrennte Validierungsfehler. Diese
Verknüpfung ist ansonsten rein referenziell und löst **niemals** automatisch eine
Include-/Exclude-Entscheidung aus.

`tools/initialize_screening_records.py` (ADR-0057, siehe [`research/screening/README.md`](../screening/README.md))
erzeugt diese Screening Records automatisch — genau einen rein administrativen, noch nicht
wissenschaftlich gescreenten Datensatz je Kandidat eines Candidate Manifest, deterministisch und
idempotent, ohne jemals eine Include-/Exclude-Entscheidung zu treffen.

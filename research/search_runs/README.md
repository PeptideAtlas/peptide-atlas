# research/search_runs/

Ein Suchlauf (`search-run-<uuid4>.yaml`) protokolliert **einen konkret ausgeführten** Suchvorgang in einer
Datenbank: die exakte Suchsyntax, wann und von wem er ausgeführt wurde, sowie die Trefferzahl. Ein Suchlauf ist
selbst **keine wissenschaftliche Quelle** — er ist der nachvollziehbare Nachweis, *wie* Kandidaten gefunden
wurden.

- Schema: [`schemas/research_search_run.schema.json`](../../schemas/research_search_run.schema.json)
- Jeder Suchlauf verweist über `protocol_id` auf das Protokoll, unter dem er ausgeführt wurde.
- Ein wiederholter oder korrigierter Suchlauf bekommt eine **neue** ID — bestehende Suchläufe werden nicht
  überschrieben (siehe [Scientific Research Protocol](../../docs/project/Scientific_Research_Protocol.md)).
- Rohexporte gehören nicht hierher, sondern (falls überhaupt lokal benötigt) nach `research/raw/` — hier wird
  nur die Metadaten-Beschreibung des Suchlaufs versioniert.

## `filters` vs. `request_parameters`

Zwei getrennte, beide offen gehaltene (`additionalProperties: true`) Objektfelder mit unterschiedlichem Zweck
(siehe ADR-0055 im [Decision Log](../../docs/project/Decision_Log.md)):

- `filters`: **inhaltliche/wissenschaftliche** Suchentscheidungen (Sprache, Publikationstyp, Spezies, ...).
- `request_parameters`: rein **technische** API-/Interface-Parameter, die zusätzlich zu `interface` und
  `exact_query` für eine Reproduktion nötig sind — z. B. bei NCBI E-utilities ESearch
  `{db, retmode, retmax, retstart}`, bei der ClinicalTrials.gov API v2
  `{query_parameter, countTotal, pageSize, format}`. **Niemals** API-Schlüssel, Tokens oder andere Geheimnisse
  eintragen — nur öffentlich unbedenkliche technische Parameter.

`pagination` (optional) dokumentiert bei einem paginierenden Interface, dass tatsächlich **alle** Seiten
abgerufen wurden (`pages_retrieved`, `completion_confirmed: true` — kein weiterer `nextPageToken` mehr vorhanden).
Entfällt, wenn das Ergebnis vollständig in einer einzigen Seite lag oder das Interface nicht paginiert.

## `result_capture`: Verknüpfung mit dem Search Result Manifest

Jeder ausgeführte Suchlauf muss `result_capture` setzen (siehe ADR-0055 und
[`research/search_results/README.md`](../search_results/README.md)):

- `status: complete` — das vollständige, tatsächlich erhaltene Identifikator-Set ist als
  `research_search_result_manifest` unter `research/search_results/` versioniert. `manifest_id` verweist auf
  dieses Manifest, `rationale` bleibt `null`.
- `status: unavailable` — aus einem echten, dokumentierten Grund (z. B. keine stabile/reproduzierbare
  Gesamttrefferzahl, gesperrte automatisierte Anfrage, Interface liefert keine Identifikatorliste) wurde bewusst
  **kein** Manifest erzeugt. `manifest_id` bleibt `null`, `rationale` ist Pflicht und muss einen echten Grund
  nennen — kein Platzhalter für "wurde vergessen".

Die reine Trefferzahl (`result_count`) reicht für historische Reproduzierbarkeit **nicht** aus: Datenbanken
verändern sich über Zeit (neue Publikationen, zurückgezogene Einträge, geänderte Indexierung), sodass eine
identische Query zu einem späteren Zeitpunkt ein anderes Ergebnis liefern kann. `result_capture` stellt sicher,
dass entweder das tatsächlich erhaltene Identifikator-Set selbst versioniert ist, oder dass dokumentiert ist,
warum das nicht möglich war.

## API-Profile: Mindestvalidierung für die derzeit verwendeten Interfaces (R2, ADR-0055-Härtung)

`tools/validate_research.py::check_search_run_interface_profiles` erzwingt für die beiden aktuell tatsächlich
genutzten API-Profile vollständige `request_parameters` (und ggf. `pagination`). Die Erkennung erfolgt
ausschließlich über `database` **und** einen textuellen Hinweis in `interface` — ein anderer Suchlauf gegen
dieselbe Datenbank, aber mit einem anderen Interface (z. B. eine manuelle Websuche statt der API), wird bewusst
**nicht** diesen Regeln unterworfen.

**NCBI E-utilities ESearch** (`interface` enthält sowohl „E-utilities" als auch „ESearch", `database: pubmed`):

```yaml
request_parameters:
  db: pubmed
  retmode: json
  retmax: <positive Ganzzahl>
  retstart: <nicht negative Ganzzahl>
```

Zusätzlich: ist `result_capture.status: complete` und liegt **keine** `pagination` vor, muss `retmax >=
result_count` gelten — sonst könnte die Antwort strukturell gar nicht das vollständige Ergebnis enthalten haben.

**ClinicalTrials.gov API v2** (`interface` enthält „ClinicalTrials.gov API v2", `database: clinicaltrials_gov`):

```yaml
request_parameters:
  query_parameter: query.term
  countTotal: true
  pageSize: <positive Ganzzahl>
  format: json
  fields: NCTId
```

Zusätzlich ist bei `result_capture.status: complete` `pagination` **verpflichtend**, und es muss gelten:
`pagination.completion_confirmed: true` sowie `pagination.pages_retrieved × request_parameters.pageSize >=
result_count`. `completion_confirmed: true` bedeutet konkret: die letzte abgerufene Seite enthielt **keinen**
weiteren `nextPageToken` (oder äquivalenten Fortsetzungsmarker) mehr — es wurde also nicht nur "genug" Seiten für
die Trefferzahl abgerufen, sondern die API selbst hat bestätigt, dass keine weitere Seite folgt. Diese
Regeln beweisen nicht allein die tatsächliche API-Antwort, verhindern aber strukturell unmögliche
Vollständigkeitsangaben.

## Zeitliche Provenienz und Exportreferenz gegenüber dem Manifest

Für jeden Suchlauf mit `result_capture.status: complete` gilt zusätzlich (siehe
[`research/search_results/README.md`](../search_results/README.md)):

- Das Datum von `executed_at` muss `<=` dem `created_at` seines Manifests sein — ein Manifest kann nicht vor dem
  Suchereignis entstanden sein, dessen Momentaufnahme es ist.
- `export_reference` (auf diesem Suchlauf) muss **exakt** `manifest.source_export_reference` entsprechen — ein
  Suchlauf darf nicht auf einen anderen lokalen Ursprung verweisen als das Manifest, das er als sein eigenes
  ausgibt. Das schließt `export_reference: null` bei einem sonst vollständigen Suchlauf aus, da das zugehörige
  Manifest `source_export_reference` als Pflichtfeld immer setzt.

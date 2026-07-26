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

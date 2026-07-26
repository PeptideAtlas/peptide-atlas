# research/search_results/

Ein Search Result Manifest (`search-result-manifest-<uuid4>.yaml`) ist eine **versionierte, maschinenlesbare
Momentaufnahme** der stabilen Identifikatoren (PMID, NCT-ID, ...), die ein
[`research_search_run`](../search_runs/README.md) tatsächlich zum Ausführungszeitpunkt erhalten hat. Siehe
ADR-0055 im [Decision Log](../../docs/project/Decision_Log.md) für die vollständige Begründung.

- Schema: [`schemas/research_search_result_manifest.schema.json`](../../schemas/research_search_result_manifest.schema.json)
- Jedes Manifest verweist über `search_run_id` auf genau **einen** Suchlauf, und dieser Suchlauf verweist über
  `result_capture.manifest_id` zurück auf genau dieses Manifest (gegenseitige Verknüpfung, siehe
  `tools/validate_research.py::check_search_result_manifests`).
- Ein Suchlauf hat **höchstens ein** aktives, vollständiges Manifest.

## Warum getrennt vom Suchlauf?

Der Suchlauf (`research_search_run`) ist das **ausgeführte Suchereignis**: Query, Zeitpunkt, Trefferzahl. Das
Manifest ist die **tatsächlich erhaltene Identifikatormenge** selbst. Diese Trennung ist notwendig, weil:

- die reine Trefferzahl für historische Reproduzierbarkeit nicht ausreicht — Datenbanken verändern sich über
  Zeit (neue Publikationen, zurückgezogene Einträge, geänderte Indexierung), sodass ein späteres erneutes
  Ausführen derselben Query ein anderes Ergebnis liefern kann;
- stabile Identifikatoren (PMID, NCT-ID) selbst **keine** geschützten Volltexte, Abstracts oder Titel sind und
  deshalb versioniert werden dürfen — anders als der vollständige API-Export, der unter `research/raw/`
  (gitignored) bleibt.

## Enthält NICHT

Ausschließlich stabile Identifikatoren. Kein Abstract, kein Titel, kein Volltext, keine sonstigen
urheberrechtlich geschützten Inhalte, kein vollständiger API-Export.

## Hash-Regel

`sha256` ist verbindlich definiert als SHA-256 über:

```python
("\n".join(identifiers) + "\n").encode("utf-8")
```

`identifiers` muss dabei bereits in der im Manifest gespeicherten, kanonisch sortierten Reihenfolge vorliegen
(numerisch aufsteigend für `pmid`, lexikografisch aufsteigend für `nct_id`) — der Hash wird über exakt diese
Reihenfolge gebildet, nicht über eine neu sortierte Kopie. Ein leeres Result Set (`identifiers: []`, `count: 0`)
hasht über `b'\n'` (leerer `join` plus der eine abschließende Zeilenumbruch), nicht über den leeren String.
Referenzimplementierung: `tools/_researchlib.py::compute_manifest_sha256`.

## Unveränderlichkeit

Ein Search Result Manifest ist **vollständig** unveränderlich nach dem Merge (siehe
`tools/check_research_immutability.py`) — anders als ein Suchlauf gibt es hier **kein** redaktionelles
`status`/`review`-Feld, das nachträglich ändern dürfte: das Manifest ist die reine Tatsachenfeststellung "diese
Identifikatoren wurden zu diesem Zeitpunkt erhalten", kein Workflow-Dokument. Eine Korrektur oder Wiederholung
erhält ein **neues** Manifest mit neuer ID (und damit auch einen neuen Suchlauf, siehe oben) statt einer
nachträglichen Bearbeitung.

## Zeitliche Provenienz gegenüber dem Suchlauf (R2, ADR-0055-Härtung)

Ein Manifest ist die Momentaufnahme **eines bereits ausgeführten** Suchlaufs und kann diesem daher zeitlich nicht
vorausgehen: `search_run.executed_at` (Datum, Uhrzeit ignoriert) muss `<=` `manifest.created_at` sein, und
`manifest.created_at <= manifest.updated_at` gilt weiterhin wie für jedes Objekt (siehe
`tools/validate_research.py::check_search_result_manifests`). Ein Manifest mit einem `created_at` vor dem
`executed_at`-Datum seines eigenen Suchlaufs ist ein Fehler (`$.created_at`).

## Exportreferenz muss mit dem Suchlauf übereinstimmen

Bei `result_capture.status: complete` muss `manifest.source_export_reference` **exakt** dem
`export_reference`-Wert seines Suchlaufs entsprechen (siehe `research/search_runs/README.md`). Ein Suchlauf mit
`export_reference: null`, aber einem vollständigen Manifest, ist ebenso ein Fehler wie eine abweichende
Referenz — beide Fälle würden bedeuten, dass Suchlauf und Manifest scheinbar aus unterschiedlichen lokalen
Quellen stammen, obwohl sie dasselbe Ergebnis beschreiben sollen (`$.source_export_reference`).

## Nicht jeder Suchlauf hat ein Manifest

`result_capture.status: unavailable` (auf dem Suchlauf, nicht auf einem Manifest) dokumentiert den Fall, dass
aus einem echten Grund kein Manifest erzeugt werden konnte (z. B. keine stabile Gesamttrefferzahl, gesperrte
automatisierte Anfrage). Das ist keine Ausnahme von diesem Ordner — es bedeutet lediglich, dass für diesen
Suchlauf **keine** Datei hier angelegt wird.

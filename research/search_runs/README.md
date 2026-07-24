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
